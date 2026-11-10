#!/usr/bin/env python3
import csv
import math
from pathlib import Path
from statistics import mean, median, stdev

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAIZ = Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "resultados/escalabilidade_fraca_mpi.csv"
SAIDA = RAIZ / "resultados/resumo_escalabilidade_fraca_mpi.csv"
GRAFICO = RAIZ / "resultados/graficos_mpi/escalabilidade_fraca_mpi.png"

medicoes = {1: {}, 2: {}, 4: {}}
checksums = {}

with ENTRADA.open(newline="", encoding="utf-8-sig") as arquivo:
    for r in csv.DictReader(arquivo):
        p = int(r["processos"])
        n = int(r["N"])
        repeticao = int(r["repeticao"])
        tempo = float(r["tempo_s"])

        if p not in medicoes:
            raise ValueError(f"Processos invalidos: {p}")

        if (n != p * 1000000
                or int(r["N_por_processo"]) != 1000000
                or int(r["K"]) != 8
                or int(r["IT"]) != 20):
            raise ValueError(f"Configuracao inesperada: {r}")

        if not math.isfinite(tempo) or tempo <= 0:
            raise ValueError(f"Tempo invalido: {r}")

        if repeticao in medicoes[p]:
            raise ValueError(f"Repeticao duplicada: P={p}, R={repeticao}")

        if p in checksums and checksums[p] != r["checksum"]:
            raise ValueError(f"Checksum inconsistente: P={p}")

        checksums[p] = r["checksum"]
        medicoes[p][repeticao] = tempo

for p, repeticoes in medicoes.items():
    if set(repeticoes) != set(range(1, 6)):
        raise ValueError(f"Repeticoes incompletas: P={p}")

referencia = mean(medicoes[1].values())
resumo = []

for p in (1, 2, 4):
    tempos = list(medicoes[p].values())
    media = mean(tempos)

    resumo.append({
        "processos": p,
        "N": p * 1000000,
        "N_por_processo": 1000000,
        "K": 8,
        "IT": 20,
        "repeticoes": len(tempos),
        "media_s": media,
        "mediana_s": median(tempos),
        "desvio_s": stdev(tempos),
        "eficiencia_fraca_pct": 100 * referencia / media,
        "checksum": checksums[p],
    })

with SAIDA.open("w", newline="", encoding="utf-8") as arquivo:
    writer = csv.DictWriter(arquivo, fieldnames=list(resumo[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(resumo)

processos = [r["processos"] for r in resumo]
medias = [r["media_s"] for r in resumo]
desvios = [r["desvio_s"] for r in resumo]

fig, ax = plt.subplots(figsize=(7.5, 4.6))
ax.errorbar(
    processos, medias, yerr=desvios,
    marker="o", capsize=5, linewidth=2,
    label="MPI (media +/- desvio-padrao)"
)
ax.axhline(
    referencia, linestyle="--",
    label="Ideal: tempo constante"
)

ax.set_title("K-means MPI - Escalabilidade fraca")
ax.set_xlabel("Processos MPI")
ax.set_ylabel("Tempo medio das iteracoes (s)")
ax.set_xticks(processos)
ax.set_ylim(bottom=0)
ax.grid(alpha=0.25)
ax.legend()
fig.tight_layout()

GRAFICO.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(GRAFICO, dpi=170)
plt.close(fig)

print("VALIDACAO: 15/15 registros consistentes")
for r in resumo:
    print(
        f'P={r["processos"]}: '
        f'media={r["media_s"]:.6f}s '
        f'eficiencia_fraca={r["eficiencia_fraca_pct"]:.1f}% '
        f'desvio={r["desvio_s"]:.6f}s'
    )

print(f"Resumo: {SAIDA}")
print(f"Grafico: {GRAFICO}")
