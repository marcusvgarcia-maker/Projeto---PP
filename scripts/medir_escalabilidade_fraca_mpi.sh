#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASE="$RAIZ/build/10_kmeans_base"
MPI="$RAIZ/build/10_kmeans_mpi"
CSV="$RAIZ/resultados/escalabilidade_fraca_mpi.csv"

N_BASE=1000000
K=8
IT=20

for exe in "$BASE" "$MPI"; do
    if [[ ! -x "$exe" ]]; then
        echo "ERRO: executavel ausente: $exe" >&2
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

echo "processos,N,N_por_processo,K,IT,repeticao,checksum,tempo_s" > "$CSV"

for P in 1 2 4; do
    N=$((N_BASE * P))

    echo "========== P=$P N=$N =========="

    # Referencia sequencial para verificar corretude
    extrair "$("$BASE" "$N" "$K" "$IT")"
    esperado="$checksum"

    # Aquecimento MPI descartado
    timeout 180s mpirun --oversubscribe -np "$P" \
        "$MPI" "$N" "$K" "$IT" </dev/null >/dev/null

    for R in 1 2 3 4 5; do
        saida=$(timeout 180s mpirun --oversubscribe -np "$P" \
            "$MPI" "$N" "$K" "$IT" </dev/null)

        extrair "$saida"

        if [[ "$checksum" != "$esperado" ]]; then
            echo "ERRO: checksum divergente em P=$P N=$N" >&2
            exit 1
        fi

        echo "$P,$N,$N_BASE,$K,$IT,$R,$checksum,$tempo" >> "$CSV"
        echo "Repeticao $R: $tempo s"
    done
done

echo
echo "Medicoes concluidas: $CSV"
