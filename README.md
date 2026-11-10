# Projeto de Programação Paralela — K-means (algoritmo de Lloyd)

**IESB · Ciência da Computação · CCO085 · 2026/2**  
**Problema 10:** agrupamento por k-médias.  
**Estado local atualizado:** 09/11/2026, após reorganização e validação OpenMP.

> **Atenção:** este README descreve a pasta **local reorganizada** `projeto_pp/`. Sua publicação na branch `main` do GitHub ainda não foi confirmada. Não confunda a estrutura local abaixo com a estrutura das branches antigas.

## Objetivo

Partir da implementação sequencial fornecida pelo professor, manter seu comportamento e desenvolver versões paralelas em **OpenMP** (memória compartilhada) e **MPI** (memória distribuída). Medir corretude e desempenho por meio de tempo de execução, *speedup*, eficiência, escalabilidade forte e fraca e comparação com a Lei de Amdahl.

**Regras fundamentais:** não modificar a lógica ou as entradas da versão sequencial de referência. O programa usa `N` pontos bidimensionais, `K` clusters e `IT` iterações fixas. A entrada é gerada de maneira determinística (semente `2024ULL`); os primeiros `K` pontos são os centroides iniciais; a atribuição utiliza distância euclidiana ao quadrado; em caso de empate, o primeiro centroide vence; e um cluster vazio mantém seu centroide anterior.

## Situação atual

| Componente | Situação | Evidência |
|---|---|---|
| Baseline sequencial | Compila e executa | `sequencial/10_kmeans.cpp` e `resultados/baseline.csv` |
| Perfilamento | Executado | `perfilamento/10_kmeans.cpp`; atribuição 87,38% e recálculo 12,61% em uma medição |
| OpenMP | Implementado e compilado | `openmp/10_kmeans.cpp` |
| Corretude OpenMP | **9/9 comparações aprovadas** | `resultados/validacao_openmp.csv`, gerado por `scripts/validar_openmp.sh` |
| Análise OpenMP | 60 medições e nove gráficos | `resultados/resultados_openmp.csv`, `resultados/resumo_openmp.csv` e `resultados/graficos/` |
| MPI | **Ainda não implementado** | `mpi/` reservado; código e testes pendentes |
| Publicação da estrutura reorganizada no GitHub | **Pendente** | Arquivos organizados e testados localmente; ainda não publicados/mesclados |

**Não tratar implementação MPI, testes de escalabilidade ou análise final de Amdahl como concluídos.** Para continuidade, consultar `AGENTS.md`, `docs/ESTADO_ATUAL.md` e `docs/PROXIMOS_PASSOS.md`; parte desses documentos foi redigida antes desta reorganização e será atualizada em seguida.

## Estrutura de diretórios

```text
projeto_pp/
├── README.md
├── AGENTS.md
├── AUTORES.md                 # preencher com integrantes/responsabilidades reais
├── .gitignore
├── Makefile
├── sequencial/10_kmeans.cpp
├── perfilamento/10_kmeans.cpp
├── openmp/10_kmeans.cpp
├── mpi/                       # ainda vazio
├── validacao/
│   ├── sequencial.cpp
│   ├── openmp.cpp
│   └── ...                    # registros de comparações anteriores
├── scripts/
│   ├── medir_baseline.sh
│   ├── medir_openmp.sh
│   ├── gerar_graficos_openmp.py
│   └── validar_openmp.sh
├── resultados/
│   ├── baseline.csv
│   ├── resultados_openmp.csv
│   ├── resumo_openmp.csv
│   ├── validacao_openmp.csv
│   └── graficos/             # nove gráficos originais
└── docs/
    ├── ARQUITETURA.md
    ├── ESTADO_ATUAL.md
    ├── EXPERIMENTOS.md
    ├── PROXIMOS_PASSOS.md
    └── REORGANIZACAO.md
```

O diretório `build/` é **gerado automaticamente** pela compilação e não deve ser versionado. Pastas de teste, como `resultados/graficos_teste/`, também podem ser removidas após conferência.

## Ambiente

Desenvolvimento em **Windows 11 + VS Code + Ubuntu no WSL2**, usando `g++` 15.2.0 (Ubuntu), `make` e OpenMP; `nproc` retornou quatro unidades de processamento disponíveis. OpenMPI foi instalado e testado com `mpirun --oversubscribe`, mas as medições MPI ainda não foram realizadas. O ambiente de referência do professor é Linux com `g++` e OpenMPI.

## Compilação

Execute os comandos **na raiz de `projeto_pp/`**, em um terminal Ubuntu/WSL:

```bash
make
```

O alvo padrão compila o sequencial, OpenMP, perfilamento e dois validadores:

```text
build/10_kmeans_base
build/10_kmeans_omp
build/10_kmeans_perfil
build/validacao_seq
build/validacao_omp
```

Também estão disponíveis `make baseline`, `make openmp`, `make perfilamento`, `make validacao` e `make clean`. **Não execute `make mpi` ainda**: a regra existe, mas `mpi/10_kmeans.cpp` ainda precisa ser implementado.

## Execução rápida

Formato da linha de comando:

```text
./programa [N] [K] [IT]
```

Padrões do código original: `N=1000000`, `K=8`, `IT=20`.

```bash
./build/10_kmeans_base 1000000 8 20
OMP_NUM_THREADS=1 OMP_DYNAMIC=FALSE ./build/10_kmeans_omp 1000000 8 20
OMP_NUM_THREADS=2 OMP_DYNAMIC=FALSE ./build/10_kmeans_omp 1000000 8 20
OMP_NUM_THREADS=4 OMP_DYNAMIC=FALSE ./build/10_kmeans_omp 1000000 8 20
```

Para essa entrada, o checksum de referência é **`8109.0037`**. O tempo varia conforme máquina e carga. Comparar apenas o checksum **não prova igualdade dos centroides**; usar a validação abaixo.

## Validação automática de corretude OpenMP

```bash
make validacao
bash scripts/validar_openmp.sh
cat resultados/validacao_openmp.csv
```

A rotina executa `N=100000`, `1000000` e `5000000`, sempre com `K=8` e `IT=20`, em 1, 2 e 4 threads. Compara as coordenadas de cada centroide final, impressas com 17 algarismos significativos, usando a versão sequencial como referência. **Resultado confirmado: 9 de 9 comparações aprovadas.** Essas verificações não dispensam testes adicionais com outros valores de `K` e `IT`.

## Experimentos e gráficos

Protocolo original: uma execução de aquecimento descartada, seguida de **cinco medições**, com `N=100000`, `1000000` e `5000000`, `K=8` e `IT=20`. A versão OpenMP usa 1, 2 e 4 threads.

Para repetir, quando necessário:

```bash
bash scripts/medir_baseline.sh  # gera resultados/baseline_reteste.csv
bash scripts/medir_openmp.sh    # gera resultados/resultados_openmp_reteste.csv
```

**Atenção:** os scripts de medição foram adaptados e passaram por verificação de sintaxe, mas ainda não tiveram o ciclo completo reexecutado após a mudança de pastas. Os nomes `_reteste.csv` preservam os CSVs originais.

O gerador de gráficos **foi efetivamente testado** na nova organização:

```bash
python3 scripts/gerar_graficos_openmp.py \
    resultados/resultados_openmp.csv \
    resultados/graficos_teste
```

Isso gera nove arquivos PNG e um `resumo_openmp.csv`, sem sobrescrever as figuras originais. Se faltar a biblioteca, instalar `python3-matplotlib` no Ubuntu.

Tempos médios da coleta OpenMP anterior (em segundos):

| N | Sequencial | OpenMP 1 | OpenMP 2 | OpenMP 4 |
|---:|---:|---:|---:|---:|
| 100.000 | 0,050713 | 0,051308 | 0,075015 | 0,101940 |
| 1.000.000 | 0,527968 | 0,464654 | 0,638230 | 0,539434 |
| 5.000.000 | 2,243186 | 2,297215 | 2,107286 | 1,805006 |

Para `N=5.000.000`, o *speedup* médio com quatro threads foi **1,243×**, com eficiência de **31,1%**, usando a média sequencial como denominador. A variabilidade foi alta em algumas configurações; não interpretar esses números como garantia de ganho estável ou explicar sua causa sem novos controles experimentais.

## Documentação e continuidade para uma IA

1. Ler **`AGENTS.md`** e este README.
2. Conferir **`docs/ESTADO_ATUAL.md`**, **`docs/ARQUITETURA.md`**, **`docs/EXPERIMENTOS.md`** e **`docs/PROXIMOS_PASSOS.md`**.
3. Inspecionar os fontes e os CSVs locais; documentos anteriores à reorganização podem citar caminhos antigos.
4. Antes de mudar o código, compilar (`make`) e executar os nove testes (`bash scripts/validar_openmp.sh`).
5. Atualizar o estado e os próximos passos ao concluir ou interromper uma tarefa. Não afirmar conclusão sem artefato e teste.

## Pendências prioritárias

- Atualizar os documentos de `docs/` e o `AGENTS.md` para refletir esta estrutura local.
- Preencher `AUTORES.md` com os três integrantes e respectivas frentes técnicas.
- Implementar, compilar, validar e medir a versão **MPI**.
- Comparar sequencial, OpenMP e MPI, justificar os resultados pela Lei de Amdahl e analisar escalabilidade forte e fraca.
- Criar evidências reprodutíveis das validações MPI e revisar a metodologia de tempo/overhead de comunicação.
- Testar o projeto no ambiente do laboratório, preparar demonstração e arguição cruzada.
- Integrar os arquivos ao GitHub com segurança, preservando as branches históricas e o código original.

**Marco 2:** entrega indicada para 12/11/2026. **Seminário:** 19 ou 26/11/2026, conforme a escala do grupo. O professor exige repositório com código sequencial, OpenMP e MPI em diretórios separados, Makefile, scripts que produzam CSV, gráficos, README e `AUTORES.md`.
