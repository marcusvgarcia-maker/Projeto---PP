#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASE="$RAIZ/build/10_kmeans_base"
MPI="$RAIZ/build/10_kmeans_mpi"
CSV="$RAIZ/resultados/resultados_mpi.csv"

for exe in "$BASE" "$MPI"; do
    if [[ ! -x "$exe" ]]; then
        echo "ERRO: executavel ausente: $exe" >&2
        echo "Execute: make baseline mpi" >&2
        exit 1
    fi
done

extrair() {
    local saida="$1"

    if [[ "$saida" =~ checksum=([0-9]+\.[0-9]+)[[:space:]]+tempo=([0-9]+\.[0-9]+) ]]; then
        checksum="${BASH_REMATCH[1]}"
        tempo="${BASH_REMATCH[2]}"
    else
        echo "ERRO: saida invalida: $saida" >&2
        exit 1
    fi
}

mkdir -p "$RAIZ/resultados"

echo "versao,N,K,IT,processos,repeticao,checksum,tempo_s" > "$CSV"

for N in 100000 1000000 5000000; do
    echo "========== N=$N =========="

    # Aquecimento sequencial
    saida=$("$BASE" "$N" 8 20)
    extrair "$saida"
    esperado="$checksum"

    # Aquecimento MPI
    for P in 1 2 4; do
        timeout 180s mpirun --oversubscribe -np "$P" \
            "$MPI" "$N" 8 20 </dev/null >/dev/null
    done

    # Repeticoes medidas
    for R in 1 2 3 4 5; do
        echo "Repeticao $R"

        saida=$("$BASE" "$N" 8 20)
        extrair "$saida"

        if [[ "$checksum" != "$esperado" ]]; then
            echo "ERRO: checksum sequencial divergente" >&2
            exit 1
        fi

        echo "sequencial,$N,8,20,1,$R,$checksum,$tempo" >> "$CSV"
        echo "  Sequencial: $tempo s"

        for P in 1 2 4; do
            saida=$(timeout 180s mpirun --oversubscribe -np "$P" \
                "$MPI" "$N" 8 20 </dev/null)

            extrair "$saida"

            if [[ "$checksum" != "$esperado" ]]; then
                echo "ERRO: checksum MPI divergente, N=$N P=$P" >&2
                exit 1
            fi

            echo "mpi,$N,8,20,$P,$R,$checksum,$tempo" >> "$CSV"
            echo "  MPI $P processo(s): $tempo s"
        done
    done
done

echo
echo "Medicoes concluidas: $CSV"
