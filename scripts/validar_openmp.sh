
#!/usr/bin/env bash
set -euo pipefail

export LC_ALL=C
export OMP_DYNAMIC=FALSE

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

SEQ="$RAIZ/build/validacao_seq"
OMP="$RAIZ/build/validacao_omp"

CSV="$RAIZ/resultados/validacao_openmp.csv"

# Verificar os executaveis
for exe in "$SEQ" "$OMP"; do
    if [[ ! -x "$exe" ]]; then
        echo "Erro: executavel ausente: $exe" >&2
        echo "Execute 'make validacao'." >&2
        exit 1
    fi
done

# Arquivos temporarios removidos automaticamente
TEMP="$(mktemp -d)"
trap 'rm -rf "$TEMP"' EXIT

K=8
IT=20

echo "N,K,IT,threads,resultado" > "$CSV"

total=0

for N in 100000 1000000 5000000; do
    echo "========== N=$N =========="

    # Executar o baseline instrumentado
    "$SEQ" "$N" "$K" "$IT" > "$TEMP/saida_seq.txt"

    grep '^CENTROIDE ' "$TEMP/saida_seq.txt" \
        > "$TEMP/referencia.txt"

    # Verificar quantidade de centroides
    if [[ $(wc -l < "$TEMP/referencia.txt") -ne "$K" ]]; then
        echo "ERRO: baseline nao produziu $K centroides."
        exit 1
    fi

    for T in 1 2 4; do
        # Executar OpenMP instrumentado
        OMP_NUM_THREADS="$T" "$OMP" "$N" "$K" "$IT" \
            > "$TEMP/saida_omp.txt"

        grep '^CENTROIDE ' "$TEMP/saida_omp.txt" \
            > "$TEMP/omp.txt"

        if [[ $(wc -l < "$TEMP/omp.txt") -ne "$K" ]]; then
            echo "ERRO: quantidade incorreta de centroides."
            exit 1
        fi

        # Comparar todas as coordenadas dos centroides
        if cmp -s "$TEMP/referencia.txt" "$TEMP/omp.txt"; then
            echo "Threads $T: CENTROIDES IDENTICOS"
            echo "$N,$K,$IT,$T,APROVADO" >> "$CSV"
            total=$((total + 1))
        else
            echo "Threads $T: DIVERGENCIA ENCONTRADA"
            echo "$N,$K,$IT,$T,FALHOU" >> "$CSV"
            diff -u "$TEMP/referencia.txt" "$TEMP/omp.txt" || true
            exit 1
        fi
    done
done

echo
echo "Validacao concluida: $total de 9 testes aprovados."
echo "Relatorio: $CSV"
