#!/usr/bin/env python3
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAIZ = Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "resultados/resumo_mpi.csv"
SAIDA = RAIZ / "resultados/graficos_mpi"
SAIDA.mkdir(parents=True, exist_ok=True)

with ENTRADA.open(newline="", encoding="utf-8") as f:
    registros = list(csv.DictReader(f))

for n in (100000, 1000000, 5000000):
    linhas = [r for r in registros if int(r["N"]) == n]

    base = next(
        float(r["media_s"])
        for r in linhas if r["versao"] == "sequencial"
    )

    mpi = sorted(
        (r for r in linhas if r["versao"] == "mpi"),
        key=lambda r: int(r["processos"])
    )

    if len(mpi) != 3:
        raise ValueError(f"Quantidade incorreta de configuracoes para N={n}")

    processos = [int(r["processos"]) for r in mpi]
    tempos = [float(r["media_s"]) for r in mpi]
    desvios = [float(r["desvio_s"]) for r in mpi]
    speedups = [float(r["speedup"]) for r in mpi]
    eficiencias = [float(r["eficiencia_pct"]) for r in mpi]

    graficos = (
        ("tempo", "Tempo medio (s)", tempos),
        ("speedup", "Speedup (vezes)", speedups),
        ("eficiencia", "Eficiencia (%)", eficiencias),
    )

    for nome, ylabel, valores in graficos:
        fig, ax = plt.subplots(figsize=(7.5, 4.6))

        if nome == "tempo":
            ax.errorbar(
                processos, valores, yerr=desvios,
                marker="o", capsize=4, label="MPI"
            )
            ax.axhline(
                base, linestyle="--",
                label="Baseline sequencial"
            )
        else:
            ax.plot(
                processos, valores,
                marker="o", linewidth=2, label="MPI"
            )

            if nome == "speedup":
                ax.plot(
                    processos, processos,
                    linestyle="--", label="Ideal"
                )
            else:
                ax.axhline(
                    100, linestyle="--",
                    label="Ideal"
                )

        ax.set_title(
            f"K-means: {nome} | N={n:,}, K=8, IT=20"
            .replace(",", ".")
        )
        ax.set_xlabel("Processos MPI")
        ax.set_ylabel(ylabel)
        ax.set_xticks(processos)
        ax.set_ylim(bottom=0)
        ax.grid(alpha=0.25)
        ax.legend()
        fig.tight_layout()

        fig.savefig(
            SAIDA / f"{nome}_N{n}.png",
            dpi=170
        )
        plt.close(fig)

print(f"9 graficos MPI gerados em: {SAIDA}")
