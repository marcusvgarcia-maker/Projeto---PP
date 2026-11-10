
#!/usr/bin/env bash
set -euo pipefail

export LC_ALL=C

# Descobrir automaticamente a raiz do projeto
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Caminhos dos arquivos
BASE="$RAIZ/build/10_kmeans_base"
CSV="$RAIZ/resultados/baseline_reteste.csv"

# Verificar se o executavel existe
if [[ ! -x "$BASE" ]]; then
    echo "Erro: baseline nao encontrado." >&2
    echo "Execute 'make baseline' na raiz do projeto." >&2
    exit 1
fi

# Cabecalho do CSV
echo "N,K,IT,repeticao,checksum,tempo_s" > "$CSV"

for N in 100000 1000000 5000000; do
    echo "Testando N=$N"

    # Aquecimento descartado
    "$BASE" "$N" 8 20 > /dev/null

    # Cinco execucoes medidas
    for r in 1 2 3 4 5; do
        saida=$("$BASE" "$N" 8 20)

        if [[ $saida =~ checksum=([0-9.]+)[[:space:]]+tempo=([0-9.]+) ]]; then
            checksum="${BASH_REMATCH[1]}"
            tempo="${BASH_REMATCH[2]}"
        else
            echo "Erro ao interpretar: $saida" >&2
            exit 1
        fi

        echo "$N,8,20,$r,$checksum,$tempo" >> "$CSV"
        echo "  Repeticao $r: $tempo s"
    done
done

echo "Medicoes concluidas: $CSV"
