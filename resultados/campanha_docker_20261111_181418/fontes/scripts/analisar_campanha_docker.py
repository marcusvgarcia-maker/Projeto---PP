#!/usr/bin/env python3
"""Analisa somente os arquivos da campanha conjunta indicada no argumento."""
import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean, median, stdev

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def ler_csv(arquivo):
    with arquivo.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def escrever_csv(arquivo, linhas):
    if not linhas:
        return
    with arquivo.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(linhas)


def agrupar(linhas, esperados, meta, perfil=False):
    grupos = defaultdict(dict)
    reps = meta["argumentos"]["repeticoes"]
    for r in linhas:
        n, k, it, rep = [int(r[x]) for x in ("N", "K", "IT", "repeticao")]
        if (k, it) != (meta["argumentos"]["k"], meta["argumentos"]["it"]):
            raise ValueError("K/IT divergente nos registros.")
        if r["checksum"] != meta["checksums"].get(str(n)):
            raise ValueError(f"Checksum divergente para N={n}.")
        chave = (n,) if perfil else (n, r["versao"], int(r["workers"]))
        if chave not in esperados or rep in grupos[chave]:
            raise ValueError(f"Configuracao inesperada ou repeticao duplicada: {chave}.")
        campos = ["total_s", "atribuicao_s", "acumulacao_s"] if perfil else ["tempo_s"]
        if any(not math.isfinite(float(r[x])) or float(r[x]) < 0 for x in campos):
            raise ValueError("Tempo negativo ou nao finito.")
        if float(r["total_s" if perfil else "tempo_s"]) <= 0:
            raise ValueError("Tempo total deve ser positivo.")
        if perfil and (float(r["atribuicao_s"]) + float(r["acumulacao_s"]) >
                       float(r["total_s"]) * (1 + 1e-9)):
            raise ValueError("As fases excedem o total do perfilamento.")
        grupos[chave][rep] = r
    if set(grupos) != set(esperados):
        raise ValueError("Faltam configuracoes na campanha.")
    for chave, amostras in grupos.items():
        if set(amostras) != set(range(1, reps + 1)):
            raise ValueError(f"Repeticoes incompletas em {chave}.")
    return {chave: list(amostras.values()) for chave, amostras in grupos.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("campanha", type=Path)
    parser.add_argument("--saida", type=Path, help="Pasta NOVA; padrao: CAMPANHA/analise.")
    args = parser.parse_args()
    pasta = args.campanha.resolve()
    meta = json.loads((pasta / "metadados.json").read_text())
    if meta["estado"] not in ("coleta_concluida", "concluida"):
        raise ValueError("A coleta nao foi concluida; nao gerar conclusoes sobre dados parciais.")
    fortes = agrupar(
        ler_csv(pasta / "forte.csv"),
        {tuple(x) for x in meta["configuracoes_fortes"]}, meta)
    fracas = agrupar(
        ler_csv(pasta / "fraca.csv"),
        {tuple(x) for x in meta["configuracoes_fracas"]}, meta)
    perfis = agrupar(
        ler_csv(pasta / "perfilamento.csv"),
        {(n,) for n in meta["argumentos"]["tamanhos"]}, meta, perfil=True)
    destino = args.saida or pasta / "analise"
    destino.mkdir(parents=True, exist_ok=False)
    resumo_perfil = []
    for (n,), linhas in sorted(perfis.items()):
        a = mean(float(r["atribuicao_s"]) for r in linhas)
        c = mean(float(r["acumulacao_s"]) for r in linhas)
        total = mean(float(r["total_s"]) for r in linhas)
        f = min(1.0, (a + c) / total)
        resumo_perfil.append(dict(
            N=n, repeticoes=len(linhas), atribuicao_media_s=a,
            acumulacao_media_s=c, total_medio_s=total,
            total_desvio_s=stdev(float(r["total_s"]) for r in linhas),
            outras_media_s=max(0.0, total - a - c),
            fracao_paralelizavel_estimada=f, fracao_restante=1-f,
            speedup_limite_ideal=1/(1-f) if f < 1 else math.inf))
    por_n = {r["N"]: r for r in resumo_perfil}
    resumo_forte, amdahl = [], []
    for (n, modelo, workers), linhas in sorted(fortes.items()):
        tempos = [float(r["tempo_s"]) for r in linhas]
        referencia = mean(float(r["tempo_s"]) for r in fortes[(n, "sequencial", 1)])
        tm = mean(tempos)
        speedup = referencia / tm
        resumo_forte.append(dict(
            N=n, versao=modelo, workers=workers, repeticoes=len(tempos),
            media_s=tm, mediana_s=median(tempos), desvio_s=stdev(tempos),
            speedup=speedup, eficiencia_pct=100*speedup/workers))
        if modelo != "sequencial":
            f = por_n[n]["fracao_paralelizavel_estimada"]
            previsto = 1 / ((1-f) + f/workers)
            amdahl.append(dict(
                N=n, versao=modelo, workers=workers,
                fracao_paralelizavel_estimada=f, speedup_ideal_amdahl=previsto,
                speedup_medido=speedup, diferenca_ideal_medido=previsto-speedup))
    resumo_fraca = []
    for (n, modelo, workers), linhas in sorted(fracas.items()):
        tempos = [float(r["tempo_s"]) for r in linhas]
        referencia = mean(float(r["tempo_s"])
                          for r in fracas[(meta["argumentos"]["n_fraca"], modelo, 1)])
        tm = mean(tempos)
        resumo_fraca.append(dict(
            N=n, versao=modelo, workers=workers, repeticoes=len(tempos),
            media_s=tm, mediana_s=median(tempos), desvio_s=stdev(tempos),
            eficiencia_fraca_pct=100*referencia/tm))
    for nome, linhas in [
            ("resumo_forte.csv", resumo_forte), ("resumo_fraca.csv", resumo_fraca),
            ("resumo_perfilamento.csv", resumo_perfil), ("amdahl.csv", amdahl)]:
        escrever_csv(destino / nome, linhas)
    modelos = [m for m in meta["argumentos"]["modelos"] if m != "sequencial"]
    for n in meta["argumentos"]["tamanhos"]:
        base = next(r["media_s"] for r in resumo_forte
                    if r["N"] == n and r["versao"] == "sequencial")
        xs = meta["argumentos"]["workers"]
        for nome, campo, ylabel in [
                ("tempo", "media_s", "Tempo das iteracoes (s)"),
                ("speedup", "speedup", "Speedup"),
                ("eficiencia", "eficiencia_pct", "Eficiencia (%)")]:
            fig, ax = plt.subplots(figsize=(7.5, 4.7))
            for modelo in modelos:
                dados = sorted((r for r in resumo_forte
                                if r["N"] == n and r["versao"] == modelo),
                               key=lambda r: r["workers"])
                if nome == "tempo":
                    ax.errorbar(
                        [r["workers"] for r in dados], [r[campo] for r in dados],
                        yerr=[r["desvio_s"] for r in dados], marker="o",
                        capsize=4, label=modelo)
                else:
                    ax.plot([r["workers"] for r in dados],
                            [r[campo] for r in dados], marker="o", label=modelo)
            if nome == "tempo":
                ax.axhline(base, linestyle="--", label="Sequencial da mesma campanha")
            elif nome == "speedup":
                f = por_n[n]["fracao_paralelizavel_estimada"]
                ax.plot(xs, xs, linestyle=":", label="Ideal linear")
                ax.plot(xs, [1/((1-f)+f/p) for p in xs], linestyle="--",
                        label="Amdahl: estimativa pelo perfil")
            else:
                ax.axhline(100, linestyle="--", label="Ideal")
            ax.set(title=f"K-means: {nome} forte | N={n:,}",
                   xlabel="Workers (threads ou processos)", ylabel=ylabel)
            ax.set_xticks(xs)
            ax.set_ylim(bottom=0)
            ax.grid(alpha=.25)
            ax.legend()
            fig.tight_layout()
            fig.savefig(destino / f"{nome}_forte_N{n}.png", dpi=160)
            plt.close(fig)
    if resumo_fraca:
        for nome, campo, ylabel in [
                ("tempo", "media_s", "Tempo das iteracoes (s)"),
                ("eficiencia", "eficiencia_fraca_pct", "Eficiencia fraca (%)")]:
            fig, ax = plt.subplots(figsize=(7.5, 4.7))
            for modelo in modelos:
                dados = sorted((r for r in resumo_fraca if r["versao"] == modelo),
                               key=lambda r: r["workers"])
                ax.errorbar([r["workers"] for r in dados], [r[campo] for r in dados],
                            yerr=[r["desvio_s"] for r in dados] if nome == "tempo" else None,
                            marker="o", capsize=4, label=modelo)
            if nome == "eficiencia":
                ax.axhline(100, linestyle="--", label="Ideal")
            ax.set(title="K-means: escalabilidade fraca",
                   xlabel="Workers (N cresce proporcionalmente)", ylabel=ylabel)
            ax.set_xticks(meta["argumentos"]["workers"])
            ax.set_ylim(bottom=0)
            ax.grid(alpha=.25)
            ax.legend()
            fig.tight_layout()
            fig.savefig(destino / f"{nome}_fraca.png", dpi=160)
            plt.close(fig)
    texto = [
        "# Resultados da campanha Docker", "",
        f"Inicio da coleta: {meta['inicio']}",
        f"Commit informado pelas referencias Git: {meta['git'].get('commit')}", "",
        "## Escopo", "",
        "Tempos usados nos calculos: iteracoes de Lloyd reportadas pelos programas.",
        "Geracao, distribuicao inicial MPI e lancamento ficam fora desse cronometro.",
        "A duracao externa dos processos tambem foi registrada, mas nao entra no speedup.",
        "As reducoes MPI de cada iteracao entram no tempo medido.", "",
        "## Escalabilidade forte", "",
        "| N | Versao | Workers | Media (s) | Desvio (s) | Speedup | Eficiencia (%) |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    for r in resumo_forte:
        texto.append(f"| {r['N']} | {r['versao']} | {r['workers']} | "
                     f"{r['media_s']:.6f} | {r['desvio_s']:.6f} | "
                     f"{r['speedup']:.3f} | {r['eficiencia_pct']:.1f} |")
    texto += [
        "", "## Estimativa de Amdahl", "",
        "f = (media da atribuicao + media da acumulacao) / media do total perfilado.",
        "S(P) = 1 / ((1-f) + f/P); limite ideal = 1/(1-f).", "",
        "| N | f estimado | Fracao restante | Limite ideal |",
        "|---:|---:|---:|---:|",
    ]
    for r in resumo_perfil:
        texto.append(f"| {r['N']} | {r['fracao_paralelizavel_estimada']:.8f} | "
                     f"{r['fracao_restante']:.8f} | {r['speedup_limite_ideal']:.2f} |")
    texto += [
        "", "A estimativa usa uma copia sequencial instrumentada e validada por centroides.",
        "Inicializacao de acumuladores, atualizacao, desalocacao e instrumentacao ficam no restante.",
        "Esse e um modelo ideal do trabalho potencialmente paralelo; nao e uma fracao efetiva",
        "medida das implementacoes OpenMP/MPI nem uma promessa de aceleracao real.",
        "A instrumentacao pode alterar os custos observados, sobretudo os trechos pequenos.",
        "O modelo nao incorpora criacao de threads/processos, coletivas, banda de memoria ou SMT.",
        "Diferencas para a previsao precisam ser discutidas com base nos dados, sem atribuir",
        "causalidade exclusiva a qualquer desses fatores.", "",
    ]
    if resumo_fraca:
        texto += [
            "## Escalabilidade fraca", "",
            "E_fraca(P) = T(1,N0)/T(P,P*N0)*100, usando a referencia de cada modelo.", "",
            "| N | Versao | Workers | Media (s) | Desvio (s) | Eficiencia fraca (%) |",
            "|---:|---|---:|---:|---:|---:|",
        ]
        for r in resumo_fraca:
            texto.append(f"| {r['N']} | {r['versao']} | {r['workers']} | "
                         f"{r['media_s']:.6f} | {r['desvio_s']:.6f} | "
                         f"{r['eficiencia_fraca_pct']:.1f} |")
    texto += [
        "", "## Limites da interpretacao", "",
        "Medias, medianas e desvios descrevem as repeticoes desta sessao.",
        "Os graficos nao demonstram diferencas estatisticamente significativas.",
        "Registre carga concorrente e energia da maquina junto aos metadados automaticos.",
        "Na maquina informada pelo grupo ha 2 nucleos e 4 processadores logicos;",
        "quatro workers nao equivalem a quatro nucleos fisicos.",
        "As validacoes 9/9 OpenMP e 33/33 MPI foram executadas separadamente pelo grupo.",
        "Esta campanha confere checksums em todas as execucoes e valida o novo perfilador",
        "contra todos os centroides do sequencial para cada tamanho perfilado.", "",
    ]
    (destino / "RESUMO.md").write_text("\n".join(texto), encoding="utf-8")
    print(f"ANALISE CONCLUIDA: {destino}")
    print(f"Forte: {sum(map(len, fortes.values()))} registros; "
          f"fraca: {sum(map(len, fracas.values()))}; "
          f"perfilamento: {sum(map(len, perfis.values()))}.")
    for r in resumo_forte:
        if r["versao"] != "sequencial":
            print(f"N={r['N']} {r['versao']} workers={r['workers']}: "
                  f"S={r['speedup']:.3f} E={r['eficiencia_pct']:.1f}%")


if __name__ == "__main__":
    main()
