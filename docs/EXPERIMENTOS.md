# Experimentos — protocolo e evidências

Atualização de fechamento em 11/11/2026. A referência final é a campanha
[Docker campanha_docker_20261111_181418](../resultados/campanha_docker_20261111_181418/), executada no commit
66e2e16ab971cdadb98d683c3ce316ef79889af6. A análise completa está em
[RESULTADOS_FINAIS_DOCKER.md](RESULTADOS_FINAIS_DOCKER.md).

## Ambiente e controle

Ubuntu 24.04.5 LTS no Docker/WSL2; G++ 13.3.0, -O2 -std=c++17;
OpenMP acrescenta -fopenmp; Open MPI 4.1.6. Intel Core i5-5300U,
dois núcleos e quatro processadores lógicos informados pelo aluno.
Memória visível no Linux: 8069680 kB; afinidade 0–3, sem limite adicional
de quota CPU/memória nos campos cgroup registrados.
OMP_DYNAMIC=FALSE e OMP_PROC_BIND=FALSE; GOMP_CPU_AFFINITY foi removida
dos subprocessos. MPI usa --oversubscribe --bind-to none.
O manual da série Open MPI 4.1 documenta essas opções:
https://www.open-mpi.org/doc/v4.1/man1/mpirun.1.php

Observações manuais de energia/carga ficaram vazias; não preencher
retrospectivamente com suposições. Os metadados automáticos estão no JSON da campanha.

## Protocolo

| Fase | Configuração | Repetições medidas | Registros |
|---|---|---:|---:|
| Forte | N=100000,1000000,5000000; sequencial + OpenMP/MPI com 1/2/4 workers; K=8/IT=20 | 5 | 105 |
| Fraca | N=1000000×P; OpenMP/MPI com P=1/2/4; K=8/IT=20 | 5 | 30 |
| Perfilamento adicional | Três N da fase forte, sequencial instrumentado | 5 | 15 |

Um aquecimento por configuração foi descartado. As variantes foram
embaralhadas em cada rodada com semente 20261111, registrada separadamente
da semente original 2024 do gerador de pontos. O coletor recompila os
programas utilizados antes da coleta e valida o perfilador por centroides.

Há 190 logs: 150 execuções medidas, 30 aquecimentos, oito execuções de
referência/validação do perfilador e dois subprocessos de compilação.
Todos retornaram zero e não houve timeout. Os 150 checksums conferem.
As validações individuais anteriores no mesmo Docker aprovaram 9/9
OpenMP e 33/33 MPI; seus arquivos foram copiados, sem alegar nova execução
dessas baterias dentro do coletor.

## Métricas

O tempo principal é o laço iterativo reportado pelo programa. Exclui geração
e preparação, incluindo no MPI as coletivas por iteração, mas não a distribuição
inicial. O tempo externo dos subprocessos é uma métrica complementar separada.

S(P)=média sequencial da mesma fase/N ÷ média paralela.
E(P)=100×S(P)/P. Na fraca, E_fraca(P)=100×T_modelo(1,N0)/T_modelo(P,P×N0).
São calculados média, mediana e desvio-padrão amostral; nenhuma amostra foi
descartada depois da coleta. Barras de erro indicam desvio, não intervalo de confiança.

## Amdahl

O fonte adicional perfilamento/10_kmeans_amdahl.cpp preserva a matemática
e separa os tempos de atribuição e acumulação. Estima-se
f=(média_atribuição+média_acumulação)/média_total_perfilado.
S_ideal(P)=1/((1-f)+f/P). A parcela restante inclui inicialização,
atualização, desalocação, controle e instrumentação.

Os f estimados foram 0,99855426; 0,99978049 e 0,99995750, respectivamente.
O modelo ideal fica próximo do linear para 2/4 workers. O enorme limite
formal em P infinito resulta de um resíduo muito pequeno e sensível ao
perfilamento; não é previsão para o equipamento real.

## Resultados e limites

No maior N, OpenMP-4: 1,503139 s, 1,303×,
32,6%. MPI-4: 1,187470 s,
1,649×, 41,2%.
Os tempos externos mudam a comparação: no mesmo caso, OpenMP-4 teve
menor duração externa que MPI-4.

Na fraca, P=4: OpenMP 30,96%, MPI 48,22%. A eficiência média MPI-2 de
111,92% é sensível à referência variável; a razão das medianas é 88,4%.
Cinco repetições, SMT, WSL2, observações manuais ausentes e variação elevada
limitam a generalização. Não foram isolados custos de coletivas ou false sharing.
Os números e a discussão detalhada estão no relatório final vinculado acima.

## Reprodutibilidade e preservação

O coletor cria uma pasta nova e recusa destinos existentes. O analisador
também usa uma pasta nova. Dados brutos, logs e metadados originais são preservados.
O Makefile usado na coleta está arquivado em fontes/; a revisão final apenas
adiciona ao Makefile principal um alvo para o perfilador auxiliar, já compilado
separadamente pelo coletor. Os três programas de produção permanecem idênticos.

As campanhas históricas permanecem separadas: baseline.csv,
resultados_openmp.csv, resultados_mpi.csv e escalabilidade_fraca_mpi.csv,
com seus resumos/gráficos originais. Não substituir esses arquivos nem
combinar seus baselines com os desta campanha.

## Fontes de evidência

- CSVs brutos, resumos, metadados, logs e fontes arquivados na pasta da campanha.
- [Arquitetura das implementações](ARQUITETURA.md).
- [Protocolo executável](ROTEIRO_CAMPANHA_DOCKER.md).
- Enunciado da disciplina, seções 3, 5.2, 5.3, 7 e 8, disponibilizado pelo professor.
