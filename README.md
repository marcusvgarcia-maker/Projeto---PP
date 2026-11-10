# Projeto de Programação Paralela — K-means (algoritmo de Lloyd)

**IESB · Ciência da Computação · CCO085 · 2026/2**  
**Problema 10:** agrupamento por k-médias.  
**Estado documentado:** 10/11/2026 — baseline, OpenMP e MPI implementados; experimentos iniciais concluídos.

> **Situação do Git:** o Pull Request [#18](https://github.com/marcusvgarcia-maker/Projeto---PP/pull/18) foi mesclado à `main` em 10/11/2026. Os três commits MPI estão na branch local `desenvolvimento/mpi`, ainda não publicada. O próximo passo é abrir um PR MPI separado contra `main`.

## Objetivo e preservação do baseline

Partir da implementação sequencial fornecida pelo professor, implementar versões paralelas em **OpenMP** (memória compartilhada) e **MPI** (memória distribuída), verificar a corretude e analisar tempo, *speedup*, eficiência e escalabilidades forte e fraca. A comparação com a Lei de Amdahl ainda precisa ser consolidada.

**Invariantes preservados:** `N` pontos bidimensionais, `K` clusters e `IT` iterações fixas; gerador determinístico com semente `2024ULL`; primeiros `K` pontos como centroides iniciais; distância euclidiana ao quadrado; primeiro centroide em empates; clusters vazios mantêm o centroide anterior. Não alterar `sequencial/10_kmeans.cpp` sem justificativa e validação.

## Situação comprovada

| Frente | Estado | Evidência |
|---|---|---|
| Sequencial | Implementado e compilado | `sequencial/10_kmeans.cpp`; `resultados/baseline.csv` |
| Perfilamento | Executado | `perfilamento/10_kmeans.cpp`; atribuição 87,38% e recálculo 12,61% em uma execução |
| OpenMP | Implementado, compilado e validado | `openmp/10_kmeans.cpp`; **9/9** comparações individuais aprovadas em `resultados/validacao_openmp.csv` |
| Experimentos OpenMP | Realizados | 60 medições, resumo e nove gráficos em `resultados/graficos/` |
| MPI | Implementado e compilado | `mpi/10_kmeans.cpp`; comunicação com `MPI_Bcast`, `MPI_Scatterv`, `MPI_Allreduce` e `MPI_Reduce` |
| Corretude MPI | **33/33 cenários aprovados** | Checksums comparados; centroides comparados individualmente em `resultados/validacao_centroides_mpi.csv`, maior erro observado **0,0** |
| Escalabilidade forte MPI | Campanha inicial realizada | 60 medições em `resultados/resultados_mpi.csv`, 9 gráficos em `resultados/graficos_mpi/` |
| Escalabilidade fraca MPI | Campanha inicial realizada | 15 medições, resumo e gráfico em `resultados/graficos_mpi/escalabilidade_fraca_mpi.png` |
| Comparação OpenMP × MPI | **Preliminar** | `resultados/comparacao_openmp_mpi.csv` e nove gráficos em `resultados/graficos_comparacao/` |
| Lei de Amdahl, retestes controlados e entrega | **Pendentes** | Consultar `docs/PROXIMOS_PASSOS.md` após sua atualização |

A igualdade de centroides foi verificada **para os casos testados**, não para todas as entradas possíveis. O número 33 se refere a combinações de `N`, `K`, `IT` e quantidades de processos, não a 33 conjuntos independentes de pontos aleatórios.

## Estrutura do repositório

```text
projeto_pp_integracao/
├── .gitattributes
├── .gitignore
├── AGENTS.md
├── AUTORES.md
├── Makefile
├── README.md
├── sequencial/10_kmeans.cpp
├── perfilamento/10_kmeans.cpp
├── openmp/10_kmeans.cpp
├── mpi/10_kmeans.cpp
├── validacao/                # programas e evidências de validação OpenMP
├── scripts/
│   ├── medir_baseline.sh
│   ├── medir_openmp.sh
│   ├── gerar_graficos_openmp.py
│   ├── validar_openmp.sh
│   ├── validar_mpi.sh
│   ├── validar_centroides_mpi.py
│   ├── medir_mpi.sh
│   ├── analisar_mpi.py
│   ├── gerar_graficos_mpi.py
│   ├── comparar_openmp_mpi.py
│   ├── medir_escalabilidade_fraca_mpi.sh
│   └── analisar_escalabilidade_fraca_mpi.py
├── resultados/
│   ├── baseline.csv
│   ├── resultados_openmp.csv
│   ├── resumo_openmp.csv
│   ├── validacao_openmp.csv
│   ├── resultados_mpi.csv
│   ├── resumo_mpi.csv
│   ├── validacao_mpi.csv
│   ├── validacao_centroides_mpi.csv
│   ├── escalabilidade_fraca_mpi.csv
│   ├── resumo_escalabilidade_fraca_mpi.csv
│   ├── comparacao_openmp_mpi.csv
│   ├── graficos/             # 9 PNG OpenMP
│   ├── graficos_mpi/         # 9 PNG de escalabilidade forte + 1 fraca
│   └── graficos_comparacao/  # 9 PNG comparativos
└── docs/                     # arquitetura, estado, experimentos e próximos passos
```

`build/` é gerado por `make` e está no `.gitignore`. Os CSVs e PNGs das campanhas são evidências do projeto e devem ser preservados. A pasta `mpi/` foi implementada na branch `desenvolvimento/mpi`; não suponha que já esteja disponível na `main`.

## Ambiente e compilação

Desenvolvimento no **Windows 11 / Ubuntu WSL2**, com `g++` Ubuntu 15.2.0, OpenMP e Open MPI (`mpic++`). Os testes utilizaram até quatro processos MPI, com `mpirun --oversubscribe`. `nproc` indicou quatro unidades de processamento disponíveis; isso não comprova quatro núcleos físicos. O clone de integração está em `~/projeto_pp_integracao`.

Na raiz do clone:

```bash
make clean && make
```

O alvo padrão produz:

```text
build/10_kmeans_base
build/10_kmeans_omp
build/10_kmeans_perfil
build/validacao_seq
build/validacao_omp
build/10_kmeans_mpi
```

Alvos individuais: `make baseline`, `make openmp`, `make perfilamento`, `make validacao`, `make mpi` e `make clean`.

## Execução e corretude

Os programas recebem `N K IT` (padrões: `1000000 8 20`). Exemplos:

```bash
./build/10_kmeans_base 1000000 8 20
OMP_NUM_THREADS=4 OMP_DYNAMIC=FALSE ./build/10_kmeans_omp 1000000 8 20
mpirun --oversubscribe -np 4 ./build/10_kmeans_mpi 1000000 8 20
mpirun --oversubscribe -np 4 ./build/10_kmeans_mpi 19 3 5 --centroides
```

Com `--centroides`, apenas o rank 0 imprime as coordenadas finais com 17 dígitos significativos, além do checksum e do tempo. Sem a opção, o MPI mantém o formato resumido do baseline.

```bash
make validacao mpi
bash scripts/validar_openmp.sh
bash scripts/validar_mpi.sh
python3 scripts/validar_centroides_mpi.py
```

O OpenMP passou em **9/9** cenários (três tamanhos e 1, 2 e 4 threads). O MPI passou em **33/33** comparações individuais contra o sequencial instrumentado, com 1, 2 e 4 processos, incluindo `N` não divisível pelos processos, processos sem pontos, valores variados de `K` e `IT=0`. O erro máximo absoluto impresso foi zero. O arquivo `validacao_mpi.csv` registra a bateria inicial de nove comparações por checksum; os outros cenários foram testados separadamente e consolidados no CSV da validação de centroides.

## Metodologia dos experimentos

As campanhas de escalabilidade forte usam `N` em **100.000, 1.000.000 e 5.000.000**, `K=8`, `IT=20`; uma execução de aquecimento por configuração e cinco medições. O OpenMP utiliza 1, 2 e 4 **threads**; o MPI utiliza 1, 2 e 4 **processos**. Cada campanha reúne 60 medições, incluindo o sequencial intercalado.

Os tempos impressos medem **apenas as iterações de Lloyd**; no MPI incluem as reduções coletivas de cada iteração, mas **excluem** geração dos dados, `MPI_Bcast` e `MPI_Scatterv` iniciais. Os valores não descrevem o tempo total de ponta a ponta do programa.

Os scripts de medições MPI e os analisadores utilizados foram:

```bash
bash scripts/medir_mpi.sh
python3 scripts/analisar_mpi.py
python3 scripts/gerar_graficos_mpi.py
python3 scripts/comparar_openmp_mpi.py
```

Reexecutar `medir_mpi.sh` sobrescreve `resultados/resultados_mpi.csv`. Antes de novos experimentos, copie o CSV para preservar a campanha original. Os scripts históricos de medição OpenMP e baseline gravam arquivos `_reteste.csv` para preservar seus resultados anteriores.

### Escalabilidade forte MPI — médias iniciais

| N | Sequencial | MPI 1 | MPI 2 | MPI 4 |
|---:|---:|---:|---:|---:|
| 100.000 | 0,103463 s | 0,092206 s | 0,104039 s | 0,310480 s |
| 1.000.000 | 0,691980 s | 0,669102 s | 0,367687 s | 0,431920 s |
| 5.000.000 | 2,341218 s | 2,316310 s | 2,050126 s | 1,469368 s |

Com `N=5.000.000`, o MPI de quatro processos teve **speedup de 1,593×** e **eficiência de 39,8%**, calculados contra o sequencial **da campanha MPI**.

### Escalabilidade fraca MPI

Mantiveram-se **1.000.000 de pontos por processo**, com `K=8` e `IT=20`:

| Processos | N total | Tempo médio | Desvio-padrão | Eficiência fraca |
|---:|---:|---:|---:|---:|
| 1 | 1.000.000 | 0,670650 s | 0,243925 s | 100,0% |
| 2 | 2.000.000 | 0,814082 s | 0,120106 s | 82,4% |
| 4 | 4.000.000 | 1,661666 s | 0,191052 s | 40,4% |

A eficiência foi calculada por `100 × tempo_médio(P=1) / tempo_médio(P)`. O resultado mostra aumento do tempo com mais processos, mas **não identifica isoladamente sua causa**. Para reproduzir e analisar:

```bash
bash scripts/medir_escalabilidade_fraca_mpi.sh
python3 scripts/analisar_escalabilidade_fraca_mpi.py
```

### Comparação entre OpenMP e MPI — limitação importante

Os experimentos OpenMP e MPI foram coletados **em campanhas diferentes**, com condições e tempos sequenciais de referência distintos. Por exemplo, com `N=100.000`, a média sequencial da campanha OpenMP foi `0,050713 s`, enquanto na campanha MPI foi `0,103463 s`.

Portanto, a comparação direta de *speedups* ou eficiências entre os dois CSVs **não é controlada**. Os gráficos de `resultados/graficos_comparacao/` são **exploratórios**. Em `N=5.000.000` e quatro trabalhadores, o tempo médio MPI foi `1,469368 s`, contra `1,805006 s` no OpenMP, mas essa diferença não comprova superioridade geral sem retestes sob condições equivalentes.

A variabilidade foi considerável, especialmente nas medições com WSL2. Interpretar resultados usando média, mediana, desvio-padrão, hardware, carga concorrente, frequência de CPU e limite de slots. Evitar atribuir automaticamente as diferenças ao overhead de MPI, OpenMP ou sistema operacional.

## Documentação e continuidade

Consultar `AGENTS.md`, `docs/ESTADO_ATUAL.md`, `docs/ARQUITETURA.md`, `docs/EXPERIMENTOS.md`, `docs/PROXIMOS_PASSOS.md` e `docs/REORGANIZACAO.md`. **Alguns documentos ainda serão atualizados** para refletir o avanço do MPI; quando divergirem, priorizar os fontes, scripts, CSVs e verificações realizadas. Confirmar sempre `pwd`, `git status -sb` e o `remote` antes de qualquer operação Git.

## Pendências antes da entrega

- Atualizar `AGENTS.md` e os documentos de `docs/` com a implementação e os experimentos MPI, distinguindo evidências concluídas de hipóteses.
- Analisar a Lei de Amdahl com premissas explícitas e confrontar previsão com as medições.
- Realizar, se possível, medições controladas conjuntas de sequencial, OpenMP e MPI; registrar hardware e contexto experimental.
- Verificar a reprodutibilidade da compilação e dos testes em um clone limpo e, se possível, no laboratório.
- Revisar a autoria e as contribuições reais com os integrantes; preparar a demonstração e a arguição cruzada.
- Os três commits MPI foram criados em `desenvolvimento/mpi`. Resta publicar a branch e abrir um Pull Request separado para `main`, preservando as branches históricas.

**Marco 2:** entrega indicada para 12/11/2026. **Apresentação:** 19 ou 26/11/2026, conforme a escala do grupo. Manter os três fontes, Makefile, scripts, CSVs, gráficos, README e `AUTORES.md` disponíveis no repositório exigido pelo professor.
