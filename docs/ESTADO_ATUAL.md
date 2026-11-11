# Estado atual do projeto — Programação Paralela / K-means

> **Data de referência:** 10/11/2026 (horário de Brasília).  
> **Disciplina:** CCO085 — Programação Paralela, IESB, 2026/2.  
> **Problema:** nº 10 — agrupamento por k-médias (K-means, algoritmo de Lloyd).  
> **Repositório:** https://github.com/marcusvgarcia-maker/Projeto---PP  
> **Clone de integração utilizado:** `~/projeto_pp_integracao`, no Ubuntu/WSL2.  
> **Critério:** este documento registra resultados confirmados por saídas de terminal; não pressupõe que mudanças locais tenham sido publicadas no GitHub.

## 1. Objetivo, invariantes e entrega

Manter o algoritmo sequencial fornecido pelo professor, desenvolver versões paralelas em OpenMP e MPI, verificar a equivalência dos resultados e estudar tempo, *speedup*, eficiência, escalabilidade forte/fraca, overhead e Lei de Amdahl.

**Marco 2:** data indicada de entrega em **12/11/2026**. Seminários previstos para **19 ou 26/11/2026**, de acordo com a escala do grupo. Entre os artefatos exigidos estão código sequencial/OpenMP/MPI separado, Makefile, scripts para CSV, gráficos, README e AUTORES. O documento do professor não estabeleceu, nas informações disponíveis, um novo PDF separado como requisito do Marco 2.

Invariantes do baseline, que não deve ser alterado: entrada `N K IT` (padrões `1000000 8 20`); pontos 2D gerados deterministicamente com semente `2024ULL`; primeiros `K` pontos como centroides iniciais; distância euclidiana ao quadrado; empate resolvido em favor do primeiro centroide; exatamente `IT` iterações; clusters vazios preservam o centroide; cronômetro apenas do laço iterativo. O checksum com quatro casas decimais é útil para triagem, mas **não substitui a validação de centroides individuais**.

## 2. Quadro de situação confirmado

| Área | Situação em 10/11/2026 | Evidência |
|---|---|---|
| Sequencial | Compilado e preservado | `sequencial/10_kmeans.cpp`; `make` |
| Perfilamento | Executado, com interpretação preliminar | Atribuição 87,38%, recálculo 12,61% em uma medição |
| OpenMP | Implementado e compilado | `openmp/10_kmeans.cpp`; `build/10_kmeans_omp` |
| Corretude OpenMP | **9/9 aprovados** | `scripts/validar_openmp.sh`; `resultados/validacao_openmp.csv` |
| Experimentos OpenMP | **60 medições** e 9 gráficos originais | `resultados/resultados_openmp.csv`; `resultados/graficos/` |
| MPI | **Implementado e compilado** | `mpi/10_kmeans.cpp`; `build/10_kmeans_mpi` |
| Corretude MPI por checksum | **33/33 comparações aprovadas** nos cenários executados | 9 casos padrão em `resultados/validacao_mpi.csv` e 24 testes adicionais relatados no terminal |
| Corretude MPI por centroide | **33/33 casos aprovados** | `scripts/validar_centroides_mpi.py`; `resultados/validacao_centroides_mpi.csv` |
| Escalabilidade forte MPI | **60 medições**, 9 gráficos | `resultados/resultados_mpi.csv`; `resultados/resumo_mpi.csv`; `resultados/graficos_mpi/` |
| Comparação OpenMP × MPI | Preliminar: **18 configurações e 9 gráficos** | `resultados/comparacao_openmp_mpi.csv`; `resultados/graficos_comparacao/` |
| Escalabilidade fraca MPI | **15 medições**, resumo e gráfico | `resultados/escalabilidade_fraca_mpi.csv`; `resultados/resumo_escalabilidade_fraca_mpi.csv` |
| Makefile | **Seis executáveis compilados via `make clean && make`** | Sequencial, perfilamento, OpenMP, MPI e dois validadores |
| Documentação | README e AGENTS atualizados localmente; documentos de `docs/` ainda em revisão | `git diff --stat` e cabeçalhos conferidos |
| Publicação MPI | **Pendente** | Branch local `desenvolvimento/mpi`; novos arquivos ainda não rastreados no último `git status` |
| Amdahl, controle experimental e preparação final | **Pendentes** | Não há avaliação teórica/empírica final consolidada |

A marcação **aprovado** significa apenas que o conjunto de casos efetivamente executado passou; não constitui prova universal do algoritmo.

## 3. Estrutura relevante do clone de integração

```text
projeto_pp_integracao/
├── README.md
├── AGENTS.md
├── AUTORES.md
├── Makefile
├── sequencial/10_kmeans.cpp
├── perfilamento/10_kmeans.cpp
├── openmp/10_kmeans.cpp
├── mpi/10_kmeans.cpp
├── validacao/{sequencial.cpp,openmp.cpp}
├── scripts/
│   ├── validar_openmp.sh
│   ├── validar_mpi.sh
│   ├── validar_centroides_mpi.py
│   ├── medir_baseline.sh
│   ├── medir_openmp.sh
│   ├── medir_mpi.sh
│   ├── analisar_mpi.py
│   ├── gerar_graficos_openmp.py
│   ├── gerar_graficos_mpi.py
│   ├── comparar_openmp_mpi.py
│   ├── medir_escalabilidade_fraca_mpi.sh
│   └── analisar_escalabilidade_fraca_mpi.py
├── resultados/
│   ├── baseline.csv
│   ├── resultados_openmp.csv, resumo_openmp.csv, validacao_openmp.csv
│   ├── resultados_mpi.csv, resumo_mpi.csv, validacao_mpi.csv
│   ├── validacao_centroides_mpi.csv
│   ├── comparacao_openmp_mpi.csv
│   ├── escalabilidade_fraca_mpi.csv, resumo_escalabilidade_fraca_mpi.csv
│   ├── graficos/                 # OpenMP original
│   ├── graficos_mpi/             # 9 de forte + 1 de fraca
│   └── graficos_comparacao/      # 9 de comparação
├── docs/
│   ├── ARQUITETURA.md
│   ├── ESTADO_ATUAL.md
│   ├── EXPERIMENTOS.md
│   ├── PROXIMOS_PASSOS.md
│   └── REORGANIZACAO.md
└── build/                        # compilado; ignorado pelo Git
```

Esta árvore é um resumo funcional, não um inventário exaustivo. Os novos scripts/artefatos MPI, no último `git status`, constavam como **não rastreados**; sua presença local foi confirmada, mas ainda não um commit.

## 4. Ambiente e compilação

- Windows 11, VS Code e Ubuntu via **WSL2**, com repositório de integração sob `/home/thinkpad/projeto_pp_integracao` (sistema de arquivos Linux, diferente da antiga pasta em `/mnt/c`).
- `g++` Ubuntu 15.2.0, C++17, `-O2`, OpenMP com `-fopenmp`; `mpic++` / OpenMPI no MPI. `nproc` retornou quatro unidades de processamento disponíveis — não necessariamente quatro núcleos físicos.
- Execução MPI com `mpirun --oversubscribe -np P`; o uso desse parâmetro **não comprova** que houve oversubscription física, mas precisa constar na metodologia. Houve anteriormente aviso de arquivos de ajuda PRRTE/PMIx no `mpirun --version`, sem impedir os testes práticos.
- Em 10/11, `make clean && make` gerou sem erros:

```text
build/10_kmeans_base
build/10_kmeans_omp
build/10_kmeans_perfil
build/validacao_seq
build/validacao_omp
build/10_kmeans_mpi
```

O alvo padrão `all` do `Makefile` passou a incluir `mpi` nesta fase.

## 5. Implementações e corretude

### OpenMP

Atribuição paralela com `#pragma omp parallel for schedule(static)`; acumulação em estruturas privadas por thread; redução manual de somas e contagens; atualização dos centros antes da iteração seguinte. Os testes para N = 100.000, 1.000.000 e 5.000.000, K = 8 e IT = 20, em 1/2/4 threads, passaram **9/9 comparações de centroides** com o baseline.

### MPI

O processo 0 gera os pontos e inicializa os centroides. A distribuição usa `MPI_Scatterv` com blocos contíguos, inclusive para divisões não exatas; os centroides iniciais são transmitidos por `MPI_Bcast`. Cada processo executa atribuição e acumulação locais. A cada iteração, `MPI_Allreduce` combina coordenadas e contagens para atualizar os centroides em todos os processos. A duração reportada é o **máximo** dos tempos locais, reduzidos com `MPI_Reduce` e `MPI_MAX`.

**Escopo do cronômetro MPI:** inicia após a distribuição inicial dos pontos e uma barreira; cobre as iterações, inclusive reduções coletivas, e exclui geração dos dados, `MPI_Scatterv`, transmissões iniciais e inicialização do ambiente MPI. Trata-se de tempo da região iterativa, **não** do programa completo.

- **33/33 verificações de checksum:** 9 testes padrão (três N × 1/2/4 processos); 9 testes com N não divisível por P; e 15 testes com N/K/IT variados, incluindo IT=0 e cenário com P maior que N. O CSV `validacao_mpi.csv` cobre os **9 casos padrão**; os demais foram exibidos no terminal.
- **33/33 verificações de centroides:** script Python compara todos os centroides da versão MPI com `build/validacao_seq` em 11 cenários × P = 1, 2, 4, tolerâncias `rel_tol=1e-12` e `abs_tol=1e-10`. **Maior erro absoluto relatado: 0.0** para coordenadas impressas em `%.17g`.
- Checksums da bateria principal: N=100.000 → `8090.3550`; N=1.000.000 → `8109.0037`; N=5.000.000 → `8099.9055`.

## 6. Experimentos realizados e resultados

### 6.1 Perfilamento sequencial (uma medição)

Para N = 1.000.000, K = 8 e IT = 20, a atribuição consumiu `0,304297 s` (**87,38%**) e o recálculo `0,043902 s` (**12,61%**) de `0,348253 s` totais reportados. Essas porcentagens descrevem *hotspots observados*, **não** a fração serial exata para a Lei de Amdahl.

### 6.2 Escalabilidade forte

Protocolo por campanha: N = 100.000, 1.000.000, 5.000.000; K = 8; IT = 20; uma execução descartada de aquecimento por configuração; cinco medições por configuração. Em ambas as campanhas, cada rodada mediu também o baseline sequencial. **OpenMP e MPI foram coletados em campanhas diferentes.**

| N | Seq. da campanha OMP (s) | OpenMP 1 (s) | OpenMP 2 (s) | OpenMP 4 (s) |
|---:|---:|---:|---:|---:|
| 100.000 | 0,050713 | 0,051308 | 0,075015 | 0,101940 |
| 1.000.000 | 0,527968 | 0,464654 | 0,638230 | 0,539434 |
| 5.000.000 | 2,243186 | 2,297215 | 2,107286 | 1,805006 |

| N | Seq. da campanha MPI (s) | MPI 1 (s) | MPI 2 (s) | MPI 4 (s) |
|---:|---:|---:|---:|---:|
| 100.000 | 0,103463 | 0,092206 | 0,104039 | 0,310480 |
| 1.000.000 | 0,691980 | 0,669102 | 0,367687 | 0,431920 |
| 5.000.000 | 2,341218 | 2,316310 | 2,050126 | 1,469368 |

- OpenMP N=5.000.000/4 threads: *speedup* **1,243×** e eficiência **31,1%** relativamente ao sequencial **da campanha OpenMP**.
- MPI N=1.000.000/2 processos: *speedup* **1,882×**, eficiência **94,1%** relativamente ao sequencial **da campanha MPI**.
- MPI N=5.000.000/4 processos: *speedup* **1,593×**, eficiência **39,8%**, também com sua própria referência sequencial.
- A comparação exploratória dos **tempos absolutos** indica OpenMP menor em N=100.000 para 1/2/4 trabalhadores; MPI menor em N=1.000.000 e 5.000.000 com 2/4. A comparação **não está controlada entre campanhas** e não sustenta afirmação causal ou ranking definitivo.
- **Não comparar diretamente speedups ou eficiências calculados com baselines sequenciais diferentes.** Os gráficos comparativos existem como visualização preliminar, e devem ser acompanhados desta ressalva.

Arquivos: `resultados/resultados_openmp.csv`, `resultados/resumo_openmp.csv`, `resultados/resultados_mpi.csv`, `resultados/resumo_mpi.csv`, `resultados/comparacao_openmp_mpi.csv`, além de 9 PNG OpenMP originais, 9 PNG MPI fortes e 9 comparativos.

### 6.3 Escalabilidade fraca MPI

Carga nominal fixa em **1.000.000 de pontos por processo**: P=1 → N=1.000.000; P=2 → N=2.000.000; P=4 → N=4.000.000. Um aquecimento e cinco medições por configuração, validadas por checksum contra execução sequencial equivalente.

| Processos | N total | Tempo médio (s) | Desvio-padrão amostral (s) | Eficiência fraca |
|---:|---:|---:|---:|---:|
| 1 | 1.000.000 | 0,670650 | 0,243925 | 100,0% |
| 2 | 2.000.000 | 0,814082 | 0,120106 | 82,4% |
| 4 | 4.000.000 | 1,661666 | 0,191052 | 40,4% |

Eficiência fraca calculada como `100 × T(P=1,N=1.000.000) / T(P,N=P×1.000.000)` usando **médias da mesma campanha**. O aumento de P não manteve o tempo constante: com P=4, a média ficou ~2,48× a de P=1. Houve variabilidade considerável; hipóteses como contenção, sincronização e ruído do WSL2 **não foram isoladas experimentalmente**.

Arquivos: `resultados/escalabilidade_fraca_mpi.csv` (15 medições), `resultados/resumo_escalabilidade_fraca_mpi.csv`, `resultados/graficos_mpi/escalabilidade_fraca_mpi.png`. **Escalabilidade fraca OpenMP não foi medida nesta fase.**

## 7. Metodologia e limitações importantes

1. O tempo das versões sequencial, OpenMP e MPI cobre o laço iterativo, não o custo total de geração/distribuição, inicialização MPI ou lançamento de processos. O overhead de comunicação **dentro** das iterações MPI é contabilizado.
2. A amostragem tem apenas cinco repetições por cenário e apresentou **dispersão expressiva**; médias não descrevem necessariamente um ganho estável.
3. As campanhas OpenMP e MPI têm baselines de referência diferentes (por exemplo, N=100.000: `0,050713 s` versus `0,103463 s`), portanto speedup e eficiência das duas campanhas **não são diretamente comparáveis**. Fazer reteste intercalado e sob condições equivalentes, se possível.
4. WSL2, disponibilidade de CPU e configuração do OpenMPI devem constar do relatório; verificar versão do Ubuntu, CPU, memória e carga concorrente antes de apresentar conclusões fortes.
5. A escalabilidade fraca fixa o número de pontos por processo, mas as reduções coletivas e a distribuição geral do problema ainda podem afetar a duração medida.
6. A análise de Amdahl ainda necessita explicitar premissas sobre a fração sequencial; não identificar automaticamente os 87,38% de tempo de atribuição como fração paralelizável total.

## 8. Estado do Git e publicação

- Repositório remoto: `marcusvgarcia-maker/Projeto---PP`.
- `organizacao/kmeans` contém a reorganização, registrada no commit `22d9583`. O **PR #18 foi mesclado à `main` em 10/11/2026**, com commit de merge `1d1a7fe`. A ancestralidade foi confirmada por `git merge-base --is-ancestor`.
- Branch local **`desenvolvimento/mpi`**, criada a partir de `organizacao/kmeans`. O último `git status --short --branch` confirmou esta branch e exibiu `Makefile`, `README.md` e `AGENTS.md` modificados, além de diretórios/arquivos MPI, relatórios e gráficos **não rastreados**. Nenhum commit MPI foi relatado ainda.
- **Não executar Git no diretório antigo do Windows**, associado a outro repositório remoto. Usar `cd ~/projeto_pp_integracao`.
- Evitar `push --force` e integração automática de branches históricas sem ancestral comum. A sequência planejada é terminar a documentação, revisar e commitar MPI em sua branch, e publicar/abrir PR respeitando a dependência de revisão da organização.

## 9. Pendências prioritárias

1. Atualizar **este documento**, `docs/EXPERIMENTOS.md`, `docs/ARQUITETURA.md` e `docs/PROXIMOS_PASSOS.md` de acordo com os arquivos reais; manter README/AGENTS consistentes.
2. Verificar executabilidade e sintaxe dos novos scripts; revisar `git diff --check` **depois de adicionar os arquivos ao índice**, pois comandos `git diff` comuns não verificam arquivos não rastreados.
3. Realizar, se possível, uma **campanha comparativa intercalada e controlada** entre sequencial, OpenMP e MPI; decidir se a escalabilidade fraca OpenMP é necessária para a entrega.
4. Preparar uma análise teórica justificada da **Lei de Amdahl** e discutir diferenças para medidas empíricas, comunicação e sincronização.
5. Revisar `AUTORES.md`, requisitos do professor, máquina de teste e material para demonstração/arguição cruzada.
6. Preparar **commit na branch `desenvolvimento/mpi`**, publicar e abrir PR após coordenar a integração/revisão da reorganização. Não mesclar ou publicar mudanças de terceiros sem alinhamento com o grupo.

## 10. Comandos para retomar

Na raiz do clone Ubuntu:

```bash
cd ~/projeto_pp_integracao
make clean && make
bash scripts/validar_openmp.sh
bash scripts/validar_mpi.sh
python3 scripts/validar_centroides_mpi.py
python3 scripts/analisar_mpi.py
python3 scripts/gerar_graficos_mpi.py
python3 scripts/comparar_openmp_mpi.py
python3 scripts/analisar_escalabilidade_fraca_mpi.py
git status --short --branch
```

**Cuidado:** alguns scripts de validação e análise reescrevem seus CSVs/gráficos de destino ao executar. Preserve os artefatos históricos antes de qualquer reteste. Para repetir medições, executar os scripts `medir_*.sh` conscientemente e usar novos nomes de saída se precisar manter campanhas anteriores.

## 11. Handoff

**Confirmado até 10/11/2026:** seis compilações; MPI implementado; corretude OpenMP 9/9 e MPI centroides 33/33; MPI forte (60 medições), fraca (15 medições), gráficos e comparação preliminar; README e AGENTS locais atualizados. **Pendente:** documentação restante, revisão do código/scripts, Amdahl, controle de comparabilidade, commit/PR MPI e testes de entrega. Este documento foi instalado localmente e sua presença foi confirmada em 10/11/2026.
