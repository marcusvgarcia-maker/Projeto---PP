#!/usr/bin/env python3
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAIZ = Path(__file__).resolve().parent.parent

ARQ_OPENMP = RAIZ / "resultados/resumo_openmp.csv"
ARQ_MPI = RAIZ / "resultados/resumo_mpi.csv"

CSV_SAIDA = RAIZ / "resultados/comparacao_openmp_mpi.csv"
DIR_GRAFICOS = RAIZ / "resultados/graficos_comparacao"
DIR_GRAFICOS.mkdir(parents=True, exist_ok=True)

def carregar_openmp():
    registros = []
    with ARQ_OPENMP.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["versao"] != "openmp":
                continue
            registros.append({
                "modelo": "openmp",
                "N": int(r["N"]),
                "workers": int(r["threads"]),
                "media_s": float(r["media_s"]),
                "mediana_s": float(r["mediana_s"]),
                "desvio_s": float(r["desvio_s"]),
                "speedup": float(r["speedup"]),
                "eficiencia_pct": float(r["eficiencia_pct"]),
                "checksum": r["checksum"],
            })
    return registros

def carregar_mpi():
    registros = []
    with ARQ_MPI.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["versao"] != "mpi":
                continue
            registros.append({
                "modelo": "mpi",
                "N": int(r["N"]),
                "workers": int(r["processos"]),
                "media_s": float(r["media_s"]),
                "mediana_s": float(r["mediana_s"]),
                "desvio_s": float(r["desvio_s"]),
                "speedup": float(r["speedup"]),
                "eficiencia_pct": float(r["eficiencia_pct"]),
                "checksum": r["checksum"],
            })
    return registros

registros = carregar_openmp() + carregar_mpi()

# salvar CSV consolidado
with CSV_SAIDA.open("w", newline="", encoding="utf-8") as f:
    campos = [
        "modelo", "N", "workers",
        "media_s", "mediana_s", "desvio_s",
        "speedup", "eficiencia_pct", "checksum"
    ]
    w = csv.DictWriter(f, fieldnames=campos, lineterminator="\n")
    w.writeheader()
    w.writerows(registros)

for n in (100000, 1000000, 5000000):
    dados_n = [r for r in registros if r["N"] == n]

    openmp = sorted(
        [r for r in dados_n if r["modelo"] == "openmp"],
        key=lambda r: r["workers"]
    )
    mpi = sorted(
        [r for r in dados_n if r["modelo"] == "mpi"],
        key=lambda r: r["workers"]
    )

    if len(openmp) != 3 or len(mpi) != 3:
        raise ValueError(f"Quantidade inesperada de configuracoes para N={n}")

    workers = [r["workers"] for r in openmp]

    metricas = [
        ("tempo", "Tempo medio (s)", "media_s"),
        ("speedup", "Speedup (vezes)", "speedup"),
        ("eficiencia", "Eficiencia (%)", "eficiencia_pct"),
    ]

    for nome, ylabel, campo in metricas:
        fig, ax = plt.subplots(figsize=(7.5, 4.6))

        ax.plot(
            workers,
            [r[campo] for r in openmp],
            marker="o",
            linewidth=2,
            label="OpenMP"
        )

        ax.plot(
            workers,
            [r[campo] for r in mpi],
            marker="o",
            linewidth=2,
            label="MPI"
        )

        if nome == "speedup":
            ax.plot(
                workers,
                workers,
                linestyle="--",
                label="Ideal"
            )
        elif nome == "eficiencia":
            ax.axhline(
                100,
                linestyle="--",
                label="Ideal"
            )

        ax.set_title(
            f"Comparacao {nome} | N={n:,}, K=8, IT=20".replace(",", ".")
        )
        ax.set_xlabel("Workers (threads ou processos)")
        ax.set_ylabel(ylabel)
        ax.set_xticks(workers)
        ax.set_ylim(bottom=0)
        ax.grid(alpha=0.25)
        ax.legend()
        fig.tight_layout()

        fig.savefig(DIR_GRAFICOS / f"{nome}_comparacao_N{n}.png", dpi=170)
        plt.close(fig)

print(f"CSV consolidado salvo em: {CSV_SAIDA}")
print(f"9 graficos de comparacao salvos em: {DIR_GRAFICOS}")

print("\nResumo comparativo:")
for n in (100000, 1000000, 5000000):
    print(f"\n========== N={n} ==========")
    for workers in (1, 2, 4):
        o = next(r for r in registros if r["modelo"] == "openmp" and r["N"] == n and r["workers"] == workers)
        m = next(r for r in registros if r["modelo"] == "mpi" and r["N"] == n and r["workers"] == workers)

        melhor_tempo = "OpenMP" if o["media_s"] < m["media_s"] else "MPI"
        melhor_speedup = "OpenMP" if o["speedup"] > m["speedup"] else "MPI"

        print(
            f"workers={workers}: "
            f"tempo -> OpenMP={o['media_s']:.6f}s | MPI={m['media_s']:.6f}s | melhor={melhor_tempo}; "
            f"speedup -> OpenMP={o['speedup']:.3f}x | MPI={m['speedup']:.3f}x | melhor={melhor_speedup}"
        )
