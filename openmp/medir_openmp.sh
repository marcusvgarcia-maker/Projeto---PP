
#!/usr/bin/env bash
set -euo pipefail

export LC_ALL=C
export OMP_DYNAMIC=FALSE

BASE="../10_kmeans_base"
OMP="./10_kmeans_omp"
CSV="resultados_openmp.csv"

# Verificar os executaveis
for exe in "$BASE" "$OMP"; do
    if [[ ! -x "$exe" ]]; then
        echo "Executavel nao encontrado: $exe" >&2
        exit 1
    fi
done

# Extrair checksum e tempo da saida
extrair() {
    local saida="$1"

    if [[ $saida =~ checksum=([0-9.]+)[[:space:]]+tempo=([0-9.]+) ]]; then
        checksum="${BASH_REMATCH[1]}"
        tempo="${BASH_REMATCH[2]}"
    else
        echo "Erro ao interpretar: $saida" >&2
        exit 1
    fi
}

echo "versao,N,K,IT,threads,repeticao,checksum,tempo_s" > "$CSV"

for N in 100000 1000000 5000000; do
    echo "========== N=$N =========="

    # Aquecimento do baseline e referencia de checksum
    extrair "$("$BASE" "$N" 8 20)"
    esperado="$checksum"

    # Aquecimento das configuracoes OpenMP
    for T in 1 2 4; do
        OMP_NUM_THREADS="$T" "$OMP" "$N" 8 20 > /dev/null
    done

    for R in 1 2 3 4 5; do
        echo "Repeticao $R"

        # Versao sequencial
        extrair "$("$BASE" "$N" 8 20)"
        [[ "$checksum" == "$esperado" ]] || {
            echo "Checksum divergente no baseline" >&2
            exit 1
        }
        echo "sequencial,$N,8,20,1,$R,$checksum,$tempo" >> "$CSV"

        # Versao OpenMP
        for T in 1 2 4; do
            extrair "$(OMP_NUM_THREADS="$T" "$OMP" "$N" 8 20)"

            if [[ "$checksum" != "$esperado" ]]; then
                echo "ERRO: checksum divergente! N=$N T=$T" >&2
                exit 1
            fi

            echo "openmp,$N,8,20,$T,$R,$checksum,$tempo" >> "$CSV"
            echo "  Threads=$T Tempo=$tempo s"
        done
    done
done

echo "Concluido: $CSV"
