#!/usr/bin/env python3
import csv
import math
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SEQ = RAIZ / "build/validacao_seq"
MPI = RAIZ / "build/10_kmeans_mpi"
CSV = RAIZ / "resultados/validacao_centroides_mpi.csv"

CASOS = [
    (100000, 8, 20),
    (1000000, 8, 20),
    (5000000, 8, 20),
    (17, 8, 20),
    (100003, 8, 20),
    (1000003, 8, 20),
    (3, 2, 3),
    (17, 1, 1),
    (19, 3, 5),
    (101, 8, 0),
    (100003, 12, 25),
]

PROCESSOS = (1, 2, 4)
TOL_ABS = 1e-10
TOL_REL = 1e-12


def executar(comando):
    resultado = subprocess.run(
        comando,
        capture_output=True,
        text=True,
        stdin=subprocess.DEVNULL,
        timeout=180,
        check=True,
    )
    return resultado.stdout


def extrair_centroides(saida, k):
    centroides = {}

    for linha in saida.splitlines():
        if not linha.startswith("CENTROIDE "):
            continue

        partes = linha.split()
        if len(partes) != 4:
            raise ValueError("Linha de centroide invalida")

        indice = int(partes[1])
        x, y = float(partes[2]), float(partes[3])

        if indice in centroides or not (0 <= indice < k):
            raise ValueError("Indice de centroide invalido ou duplicado")

        if not (math.isfinite(x) and math.isfinite(y)):
            raise ValueError("Coordenada nao finita")

        centroides[indice] = (x, y)

    if set(centroides) != set(range(k)):
        raise ValueError(f"Esperados {k} centroides, recebidos {len(centroides)}")

    return centroides


def comparar(referencia, obtidos):
    erro_maximo = 0.0
    aprovado = True

    for indice in referencia:
        for esperado, obtido in zip(referencia[indice], obtidos[indice]):
            erro = abs(esperado - obtido)
            erro_maximo = max(erro_maximo, erro)

            if not math.isclose(
                esperado, obtido,
                rel_tol=TOL_REL,
                abs_tol=TOL_ABS,
            ):
                aprovado = False

    return aprovado, erro_maximo


def main():
    for executavel in (SEQ, MPI):
        if not executavel.is_file():
            sys.exit(f"Executavel ausente: {executavel}")

    CSV.parent.mkdir(parents=True, exist_ok=True)
    aprovados = 0
    total = 0

    with CSV.open("w", newline="", encoding="utf-8") as arquivo:
        writer = csv.writer(arquivo, lineterminator="\n")
        writer.writerow([
            "N", "K", "IT", "processos",
            "resultado", "erro_maximo_absoluto", "detalhes"
        ])

        for n, k, it in CASOS:
            print(f"========== N={n} K={k} IT={it} ==========")

            try:
                referencia = extrair_centroides(
                    executar([str(SEQ), str(n), str(k), str(it)]),
                    k,
                )
            except Exception as erro:
                sys.exit(f"Falha no sequencial: {erro}")

            for p in PROCESSOS:
                total += 1
                erro_maximo = ""
                detalhes = ""

                try:
                    saida = executar([
                        "mpirun", "--oversubscribe", "-np", str(p),
                        str(MPI), str(n), str(k), str(it),
                        "--centroides",
                    ])

                    obtidos = extrair_centroides(saida, k)
                    passou, erro_maximo = comparar(referencia, obtidos)

                    resultado = "APROVADO" if passou else "REPROVADO"

                    if passou:
                        aprovados += 1

                except Exception as erro:
                    resultado = "ERRO"
                    detalhes = str(erro)

                writer.writerow([
                    n, k, it, p, resultado, erro_maximo, detalhes
                ])

                print(
                    f"MPI {p} processo(s): {resultado} "
                    f"| erro maximo: {erro_maximo}"
                )

    print()
    print(f"RESULTADO FINAL: {aprovados}/{total} testes aprovados")
    print(f"Relatorio: {CSV}")

    return 0 if aprovados == total else 1


if __name__ == "__main__":
    sys.exit(main())
