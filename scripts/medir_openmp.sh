
#!/usr/bin/env bash
set -euo pipefail

export LC_ALL=C
export OMP_DYNAMIC=FALSE

# Identificar automaticamente a raiz do projeto
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Caminhos dos executaveis e resultados
BASE="$RAIZ/build/10_kmeans_base"
OMP="$RAIZ/build/10_kmeans_omp"
CSV="$RAIZ/resultados/resultados_openmp_reteste.csv"

# Verificar os executaveis
for exe in "$BASE" "$OMP"; do
    if [[ ! -x "$exe" ]]; then
        echo "Erro: executavel nao encontrado: $exe" >&2
        echo "Execute 'make' na raiz do projeto." >&2
        exit 1
    fi
done

# Extrair checksum e tempo da saida do programa
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

# Preparar arquivo CSV
mkdir -p "$RAIZ/resultados"

echo "versao,N,K,IT,threads,repeticao,checksum,tempo_s" > "$CSV"

# Configuracoes experimentais
for N in 100000 1000000 5000000; do
    echo "========== N=$N =========="

    # Aquecimento do baseline e checksum esperado
    extrair "$("$BASE" "$N" 8 20)"
    esperado="$checksum"

    # Aquecimento das versoes OpenMP
    for T in 1 2 4; do
        OMP_NUM_THREADS="$T" "$OMP" "$N" 8 20 > /dev/null
    done

    # Cinco repeticoes medidas
    for R in 1 2 3 4 5; do
        echo "Repeticao $R"

        # Execucao sequencial
        extrair "$("$BASE" "$N" 8 20)"

        if [[ "$checksum" != "$esperado" ]]; then
            echo "Erro: checksum divergente no baseline." >&2
            exit 1
        fi

        echo "sequencial,$N,8,20,1,$R,$checksum,$tempo" >> "$CSV"

        # Execucoes OpenMP
        for T in 1 2 4; do
            extrair "$(OMP_NUM_THREADS="$T" "$OMP" "$N" 8 20)"

            if [[ "$checksum" != "$esperado" ]]; then
                echo "Erro: checksum divergente! N=$N T=$T" >&2
                exit 1
            fi

            echo "openmp,$N,8,20,$T,$R,$checksum,$tempo" >> "$CSV"

            echo "  Threads=$T Tempo=$tempo s"
        done
    done
done

echo "Medicoes concluidas: $CSV"
