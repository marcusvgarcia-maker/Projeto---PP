#!/usr/bin/env python3
"""Uso: python3 gerar_graficos_openmp.py resultados_openmp.csv"""
import csv
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean, median, stdev

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

RAIZ = Path(__file__).resolve().parent.parent

arquivo = (
    Path(sys.argv[1])
    if len(sys.argv) > 1
    else RAIZ / "resultados" / "resultados_openmp.csv"
)
if not arquivo.exists():
    sys.exit(f'Arquivo nao encontrado: {arquivo}')

amostras = defaultdict(list)
checksums = defaultdict(set)
with arquivo.open(encoding='utf-8-sig', newline='') as f:
    for linha in csv.DictReader(f):
        n, k, it, threads = [int(linha[c]) for c in ('N', 'K', 'IT', 'threads')]
        versao = linha['versao']
        chave = (n, k, it, versao, threads)
        amostras[chave].append(float(linha['tempo_s']))
        checksums[(n, k, it)].add(linha['checksum'])

saida = (
    Path(sys.argv[2])
    if len(sys.argv) > 2
    else RAIZ / "resultados" / "graficos"
)

saida.mkdir(parents=True, exist_ok=True)
resumo = []
for n, k, it in sorted(checksums):
    if len(checksums[(n, k, it)]) != 1:
        sys.exit(f'ATENCAO: checksum divergente para N={n}, K={k}, IT={it}')
    tbase = mean(amostras[(n, k, it, 'sequencial', 1)])
    for (nn, kk, ii, versao, threads), tempos in sorted(amostras.items()):
        if (nn, kk, ii) != (n, k, it):
            continue
        tm = mean(tempos)
        speedup = tbase / tm
        resumo.append(dict(N=n, K=k, IT=it, versao=versao, threads=threads,
                           repeticoes=len(tempos), media_s=tm, mediana_s=median(tempos),
                           desvio_s=stdev(tempos) if len(tempos) > 1 else 0,
                           speedup=speedup, eficiencia_pct=100*speedup/threads,
                           checksum=next(iter(checksums[(n, k, it)]))))

campos = list(resumo[0])
with (saida / 'resumo_openmp.csv').open('w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=campos)
    writer.writeheader()
    writer.writerows(resumo)

for n, k, it in sorted(checksums):
    linhas = [r for r in resumo if (r['N'], r['K'], r['IT']) == (n, k, it)]
    base = next(r['media_s'] for r in linhas if r['versao'] == 'sequencial')
    omp = sorted((r for r in linhas if r['versao'] == 'openmp'), key=lambda r: r['threads'])
    xs = [r['threads'] for r in omp]
    graficos = [
        ('tempo', 'Tempo medio (s)', [r['media_s'] for r in omp]),
        ('speedup', 'Speedup (vezes)', [r['speedup'] for r in omp]),
        ('eficiencia', 'Eficiencia (%)', [r['eficiencia_pct'] for r in omp]),
    ]
    for nome, ylabel, ys in graficos:
        fig, ax = plt.subplots(figsize=(7.5, 4.6))
        ax.plot(xs, ys, marker='o', linewidth=2, label='OpenMP')
        if nome == 'tempo':
            ax.axhline(base, linestyle='--', color='gray', label='Baseline sequencial')
        elif nome == 'speedup':
            ax.plot(xs, xs, linestyle='--', color='gray', label='Ideal')
        else:
            ax.axhline(100, linestyle='--', color='gray', label='Ideal')
        ax.set_title(f'K-means: {nome} | N={n:,}, K={k}, IT={it}'.replace(',', '.'))
        ax.set_xlabel('Threads')
        ax.set_ylabel(ylabel)
        ax.set_xticks(xs)
        ax.set_ylim(bottom=0)
        ax.grid(alpha=.25)
        ax.legend()
        fig.tight_layout()
        fig.savefig(saida / f'{nome}_N{n}.png', dpi=170)
        plt.close(fig)

print(f'Resumo e 9 graficos salvos em: {saida}')
for r in resumo:
    print(f"N={r['N']:<8} {r['versao']:<10} t={r['threads']} "
          f"media={r['media_s']:.6f}s speedup={r['speedup']:.3f}x "
          f"eficiencia={r['eficiencia_pct']:.1f}%")
