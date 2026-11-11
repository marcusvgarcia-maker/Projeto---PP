#!/usr/bin/env bash
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SEQ="$RAIZ/build/10_kmeans_base"
MPI="$RAIZ/build/10_kmeans_mpi"
CSV="$RAIZ/resultados/validacao_mpi.csv"

K=8
IT=20
aprovados=0
total=0

if [[ ! -x "$SEQ" || ! -x "$MPI" ]]; then
    echo "ERRO: executaveis ausentes. Execute: make baseline mpi"
    exit 1
fi

mkdir -p "$RAIZ/resultados"
echo "N,K,IT,processos,checksum_seq,checksum_mpi,status" > "$CSV"

for N in 100000 1000000 5000000; do
    echo "========== N=$N =========="

    saida_seq=$("$SEQ" "$N" "$K" "$IT")

    if [[ "$saida_seq" =~ checksum=([0-9]+\.[0-9]+) ]]; then
        checksum_seq="${BASH_REMATCH[1]}"
    else
        echo "ERRO: checksum sequencial nao encontrado"
        exit 1
    fi

    for P in 1 2 4; do
        total=$((total + 1))
        checksum_mpi="ERRO"
        status="REPROVADO"

        if saida_mpi=$(mpirun --oversubscribe -np "$P" \
            "$MPI" "$N" "$K" "$IT"); then

            if [[ "$saida_mpi" =~ checksum=([0-9]+\.[0-9]+) ]]; then
                checksum_mpi="${BASH_REMATCH[1]}"

                if [[ "$checksum_seq" == "$checksum_mpi" ]]; then
                    status="APROVADO"
                    aprovados=$((aprovados + 1))
                fi
            fi
        fi

        echo "$P processo(s): $status"

        echo "$N,$K,$IT,$P,$checksum_seq,$checksum_mpi,$status" \
            >> "$CSV"
    done
done

echo
echo "Validacao concluida: $aprovados de $total testes aprovados."
echo "Relatorio: $CSV"

if [[ "$aprovados" -ne "$total" ]]; then
    exit 1
fi
