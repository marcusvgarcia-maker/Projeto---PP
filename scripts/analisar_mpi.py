#!/usr/bin/env python3
import csv
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean, median, stdev

RAIZ = Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "resultados/resultados_mpi.csv"
SAIDA = RAIZ / "resultados/resumo_mpi.csv"

TAMANHOS = (100000, 1000000, 5000000)
PROCESSOS = (1, 2, 4)
CHECKSUMS = {
    100000: "8090.3550",
    1000000: "8109.0037",
    5000000: "8099.9055",
}

amostras = defaultdict(dict)

with ENTRADA.open(newline="", encoding="utf-8-sig") as f:
    for linha in csv.DictReader(f):
        n = int(linha["N"])
        k = int(linha["K"])
        it = int(linha["IT"])
        versao = linha["versao"]
        p = int(linha["processos"])
        repeticao = int(linha["repeticao"])
        tempo = float(linha["tempo_s"])

        if n not in TAMANHOS or k != 8 or it != 20:
            raise ValueError(f"Configuracao inesperada: {linha}")

        if versao == "sequencial":
            if p != 1:
                raise ValueError("Baseline com processos != 1")
        elif versao == "mpi":
            if p not in PROCESSOS:
                raise ValueError(f"Processos inesperados: {p}")
        else:
            raise ValueError(f"Versao inesperada: {versao}")

        if linha["checksum"] != CHECKSUMS[n]:
            raise ValueError(f"Checksum divergente: {linha}")

        if not math.isfinite(tempo) or tempo < 0:
            raise ValueError(f"Tempo invalido: {linha}")

        chave = (n, versao, p)

        if repeticao in amostras[chave]:
            raise ValueError(f"Repeticao duplicada: {linha}")

        amostras[chave][repeticao] = tempo

linhas = []

for n in TAMANHOS:
    configuracoes = [("sequencial", 1)]
    configuracoes += [("mpi", p) for p in PROCESSOS]

    for versao, p in configuracoes:
        chave = (n, versao, p)
        repeticoes = amostras.get(chave, {})

        if set(repeticoes) != set(range(1, 6)):
            raise ValueError(
                f"Repeticoes incompletas em {chave}: "
                f"{sorted(repeticoes)}"
            )

    referencia = mean(amostras[(n, "sequencial", 1)].values())

    for versao, p in configuracoes:
        tempos = list(amostras[(n, versao, p)].values())
        media = mean(tempos)
        speedup = referencia / media
        eficiencia = 100 * speedup / p

        linhas.append({
            "N": n,
            "K": 8,
            "IT": 20,
            "versao": versao,
            "processos": p,
            "repeticoes": len(tempos),
            "media_s": media,
            "mediana_s": median(tempos),
            "desvio_s": stdev(tempos),
            "speedup": speedup,
            "eficiencia_pct": eficiencia,
            "checksum": CHECKSUMS[n],
        })

SAIDA.parent.mkdir(parents=True, exist_ok=True)

with SAIDA.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(linhas[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(linhas)

print("VALIDACAO: 60/60 registros consistentes")

for n in TAMANHOS:
    print(f"\n========== N={n} ==========")
    for r in linhas:
        if r["N"] == n:
            print(
                f'{r["versao"]:10} P={r["processos"]} '
                f'media={r["media_s"]:.6f}s '
                f'speedup={r["speedup"]:.3f}x '
                f'eficiencia={r["eficiencia_pct"]:.1f}%'
            )

print(f"\nResumo salvo em: {SAIDA}")
