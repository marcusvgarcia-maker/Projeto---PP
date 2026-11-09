
#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C

echo "N,K,IT,repeticao,checksum,tempo_s" > baseline.csv

for N in 100000 1000000 5000000; do
    echo "Testando N=$N"

    # Aquecimento (descartado)
    ./10_kmeans_base "$N" 8 20 > /dev/null

    # Cinco execuções medidas
    for r in 1 2 3 4 5; do
        saida=$(./10_kmeans_base "$N" 8 20)

        if [[ $saida =~ checksum=([0-9.]+)[[:space:]]+tempo=([0-9.]+) ]]; then
            checksum="${BASH_REMATCH[1]}"
            tempo="${BASH_REMATCH[2]}"
        else
            echo "Erro ao interpretar: $saida" >&2
            exit 1
        fi

        echo "$N,8,20,$r,$checksum,$tempo" >> baseline.csv
        echo "  Repetição $r: $tempo s"
    done
done

echo "Medições concluídas: baseline.csv"
