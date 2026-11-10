# Arquitetura técnica — Projeto de Programação Paralela (K-means)

> **Disciplina:** Programação Paralela (CCO085), IESB — 2026/2  
> **Problema:** nº 10 — Agrupamento por k-médias, algoritmo de Lloyd  
> **Referência do estado:** 09/11/2026  
> **Escopo deste arquivo:** arquitetura **implementada** do sequencial e OpenMP; arquitetura **planejada** do MPI.  
> **Fonte da verdade operacional:** código e resultados locais em `projeto_pp/`. A publicação dessa reorganização na `main` do GitHub ainda não foi confirmada.

## 1. Objetivo e restrições

Partir do código sequencial fornecido pelo professor, desenvolver versões paralelas com OpenMP e MPI sem modificar as regras do algoritmo e avaliar corretude e desempenho. O projeto também exige medições e análise de *speedup*, eficiência, escalabilidade e comparação com a Lei de Amdahl.

**Preservar o código em `sequencial/10_kmeans.cpp` como baseline original.** Versões derivadas podem mudar a organização dos cálculos para paralelizar, mas devem manter as entradas, a inicialização, a regra de atribuição, o recálculo e o resultado exigido. Qualquer mudança de ordem das operações de ponto flutuante precisa de validação explícita.

### Regras e invariantes do baseline

| Item | Comportamento de referência |
|---|---|
| Argumentos | `N` (pontos), `K` (clusters), `IT` (iterações); padrões: `1000000`, `8`, `20` |
| Dados | `N` pontos bidimensionais em `px[i]` e `py[i]`, gerados deterministicamente |
| Gerador | `uint64_t s = 2024ULL`; atualização `s = s*6364136223846793005ULL + 1` duas vezes por ponto; coordenada `(s >> 40) % 1000`, convertida para `double` |
| Centroides iniciais | Primeiros `K` pontos (`cx[j] = px[j]`, `cy[j] = py[j]`) |
| Distância | Quadrado da distância euclidiana: `(px[i]-cx[j])² + (py[i]-cy[j])²` |
| Desempate | O primeiro centroide com menor distância vence; atualizar apenas com `d < best`, não `<=` |
| Iterações | Exatamente `IT` ciclos; não há interrupção por convergência |
| Recálculo | Média aritmética por coordenada dos pontos de cada cluster |
| Cluster vazio | Centroide permanece inalterado quando `cnt[j] == 0` |
| Resultado impresso | `N`, `K`, `it`, `checksum=%.4f`, `tempo=%.6f s`; checksum é a soma de `cx[j] + cy[j]` |
| Região temporizada | Começa antes do laço de iterações e termina depois dele; geração e inicialização ficam fora |

O programa original assume entradas coerentes (por exemplo, `N >= K > 0`); não introduzir uma nova semântica de entrada sem registrar e justificar a decisão.

## 2. Ciclo do algoritmo e dependências

Para cada iteração `it`:

1. **Atribuição:** para cada ponto `i`, comparar a distância aos `K` centroides correntes e escrever seu rótulo `rotulo[i]`.
2. **Acumulação:** para cada ponto `i`, somar suas coordenadas e uma unidade na contagem do cluster de `rotulo[i]`.
3. **Atualização:** para cada cluster não vazio, dividir as somas por sua contagem para obter `cx[j]` e `cy[j]`.
4. **Sincronização lógica:** a atribuição da iteração seguinte só pode começar quando os novos centroides estiverem prontos.

```text
centroides de iteração it
           |
           v
   atribuir N pontos     <- independente por ponto
           |
           v
 acumular por cluster    <- compartilhamento / redução necessária
           |
           v
 atualizar K centroides  <- depende da acumulação completa
           |
           v
 próxima iteração        <- depende dos centroides atualizados
```

A atribuição é naturalmente paralela por ponto, porque cada operação lê os mesmos centroides e escreve somente `rotulo[i]`. O recálculo tem dependência de acumulação: diversos pontos podem atualizar o mesmo cluster. Não é seguro usar uma soma compartilhada sem mecanismos de proteção ou redução.

### Complexidade

- Geração inicial: `O(N)` (fora do cronômetro do baseline).
- Por iteração: atribuição `O(NK)`; acumulação `O(N)`; atualização `O(K)`.
- Região iterativa: `O(IT × (NK + N + K))`, habitualmente `O(IT × N × K)` para `N >= K > 0`.
- Memória sequencial: `O(N + K)` (coordenadas, rótulos, centroides e acumuladores).

## 3. Estrutura de arquivos local

```text
projeto_pp/
├── README.md
├── AGENTS.md
├── AUTORES.md                    # confirmar dados reais dos integrantes
├── Makefile
├── .gitignore
├── sequencial/10_kmeans.cpp     # fonte original de referência
├── perfilamento/10_kmeans.cpp   # cópia instrumentada para medir fases
├── openmp/10_kmeans.cpp         # OpenMP efetivamente implementado
├── mpi/                         # VAZIO em 09/11/2026: ainda não implementado
├── validacao/
│   ├── sequencial.cpp            # baseline instrumentado: imprime centroides
│   └── openmp.cpp                # OpenMP instrumentado: imprime centroides
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
│   └── graficos/                # 9 PNG originais
├── build/                       # gerado por make; não versionar
└── docs/
    ├── ARQUITETURA.md
    ├── ESTADO_ATUAL.md
    ├── EXPERIMENTOS.md
    ├── PROXIMOS_PASSOS.md
    └── REORGANIZACAO.md
```

**Nota:** um `resultados/graficos_teste/` pode existir após testar a reprodução dos gráficos. Backups com sufixo `_ANTERIOR` podem existir durante a transição, mas não devem ser confundidos com a versão canônica.

## 4. Baseline e perfilamento — implementados

**Fonte:** `sequencial/10_kmeans.cpp`. É o código de referência e deve permanecer inalterado.

**Instrumentação:** `perfilamento/10_kmeans.cpp` adiciona chamadas ao relógio para separar a atribuição e o recálculo. Como há temporizadores adicionais, os tempos do perfilamento não são necessariamente iguais aos do executável original sem instrumentação.

Um teste com `N=1.000.000`, `K=8` e `IT=20` registrou:

| Etapa | Tempo | Participação |
|---|---:|---:|
| Atribuição | 0,304297 s | 87,38% |
| Recálculo | 0,043902 s | 12,61% |
| Total instrumentado | 0,348253 s | 100% |

A atribuição foi o maior *hotspot* nessa execução. **Esses 87,38% não são automaticamente a fração paralelizável exata para a Lei de Amdahl**, porque o recálculo também foi parcialmente paralelizado e há sobrecarga de paralelização, memória e sincronização. A estimativa de Amdahl ainda requer justificativa e confronto com os resultados.

## 5. OpenMP — implementado e validado nos cenários registrados

**Fonte:** `openmp/10_kmeans.cpp`. **Compilação:** `g++ -O2 -std=c++17 -fopenmp`, automatizada por `make openmp`.

### 5.1 Atribuição paralela

```cpp
#pragma omp parallel for schedule(static)
for (int i = 0; i < N; i++) {
    double best = 1e18;
    int bj = 0;
    for (int j = 0; j < K; j++) {
        double dx = px[i] - cx[j], dy = py[i] - cy[j];
        double d = dx*dx + dy*dy;
        if (d < best) { best = d; bj = j; }
    }
    rotulo[i] = bj;
}
```

- `schedule(static)` foi escolhido porque o número de comparações por ponto é igual (`K`); o custo efetivo pode variar com o ambiente, mas a carga algorítmica é bem distribuída.
- `px`, `py`, `cx` e `cy` são lidos durante essa fase; cada thread escreve somente posições distintas de `rotulo`.
- `best` e `bj` são locais à iteração do laço.
- Ao fim do `parallel for`, a sincronização garante que os rótulos estejam prontos para o recálculo.

### 5.2 Recálculo paralelo com acumuladores por thread

A versão sequencial atualizava `sx[j]`, `sy[j]` e `cnt[j]` para cada ponto. Uma adaptação ingênua com um único conjunto de vetores compartilhados criaria condição de corrida.

A implementação existente usa:

1. `T = omp_get_max_threads()` e três conjuntos de acumuladores indexados por thread (`sx_local`, `sy_local`, `cnt_local`), cada um com `K` posições.
2. Zera os acumuladores privados por thread no início de cada iteração.
3. Executa uma região `#pragma omp parallel` com `#pragma omp for schedule(static)`; cada thread atualiza **somente seus vetores locais**.
4. Após terminar a região paralela, combina os parciais **sequencialmente** para cada cluster e atualiza os centroides não vazios.

```cpp
#pragma omp parallel
{
    int tid = omp_get_thread_num();
    #pragma omp for schedule(static)
    for (int i = 0; i < N; i++) {
        int j = rotulo[i];
        sx_local[tid][j] += px[i];
        sy_local[tid][j] += py[i];
        cnt_local[tid][j]++;
    }
}
// Após a região paralela: redução MANUAL das linhas locais por cluster.
```

**Decisão técnica:** evitar `critical` ou `atomic` em cada atualização de ponto reduz a contenção; aqui **não** se usou literalmente a cláusula `reduction(...)` do OpenMP — a combinação é **manual**, com vetores locais. O encerramento da região `parallel` sincroniza as threads antes da combinação.

**Custos/limitações:** memória adicional `O(TK)`; zerar acumuladores e combiná-los custa `O(TK)` por iteração; as regiões paralelas e barreiras geram overhead. Possível *false sharing* entre pequenos vetores e limitações da largura de banda de memória são hipóteses a testar, **não causas comprovadas**. Não há comparação medida entre `static`, `dynamic` e `guided` ou entre redução manual/`atomic`/`critical`.

### 5.3 Corretude registrada

Foi criado um código de validação separado (`validacao/sequencial.cpp` e `validacao/openmp.cpp`) que imprime cada coordenada final com `%.17g`. O script `scripts/validar_openmp.sh` compara os arquivos de centroides byte a byte usando `cmp`.

- `N = 100.000`, `1.000.000` e `5.000.000`.
- `K = 8`, `IT = 20` em todos os testes.
- OpenMP com 1, 2 e 4 threads.
- **9/9 comparações aprovadas**, registradas em `resultados/validacao_openmp.csv`.
- Checksums por entrada: `8090.3550`, `8109.0037` e `8099.9055`, respectivamente.

Essa evidência confirma igualdade **dos centroides finais impressos** para os cenários testados. O checksum isolado não é prova suficiente e a bateria atual não cobre outros valores de `K`, `IT` ou casos-limite. No conjunto testado, as coordenadas de entrada são números inteiros pequenos representados como `double`; as somas permanecem na faixa de representação exata, favorecendo a igualdade mesmo com outra ordem de acumulação.

### 5.4 Desempenho registrado

Protocolo do experimento OpenMP original: três entradas, uma execução descartada de aquecimento por configuração, cinco repetições por configuração, baseline sequencial intercalado com OpenMP usando 1/2/4 threads. Dados brutos em `resultados/resultados_openmp.csv` (60 linhas de dados); gráficos em `resultados/graficos/` (9 PNG) e estatísticas em `resultados/resumo_openmp.csv`.

| N | Sequencial médio | OpenMP 1 | OpenMP 2 | OpenMP 4 |
|---:|---:|---:|---:|---:|
| 100.000 | 0,050713 s | 0,051308 s | 0,075015 s | 0,101940 s |
| 1.000.000 | 0,527968 s | 0,464654 s | 0,638230 s | 0,539434 s |
| 5.000.000 | 2,243186 s | 2,297215 s | 2,107286 s | 1,805006 s |

Para `N=5.000.000` e 4 threads, o *speedup* com base nas médias foi aproximadamente `1,243×` e a eficiência foi `31,1%`. **Há variação expressiva entre as repetições**; não concluir que esse ganho será mantido em todo ambiente. O *speedup* do projeto deve usar como referência o **executável sequencial**, nunca simplesmente a versão OpenMP com 1 thread. Mais detalhes: `docs/EXPERIMENTOS.md`.

## 6. MPI — ARQUITETURA PLANEJADA, NÃO IMPLEMENTADA

**Estado:** a pasta `mpi/` estava vazia na última árvore local informada. Foi discutida uma estratégia MPI na conversa, mas **não há código MPI comprovadamente criado, compilado, testado ou validado**. Não marcar esta frente como concluída.

Proposta de decomposição por blocos de pontos:

1. Processo 0 gera **exatamente os dados originais**, inicializa os mesmos centroides e prepara contagens/deslocamentos por processo.
2. Distribuir blocos contíguos de `px` e `py` com `MPI_Scatterv` (inclusive quando `N` não for divisível pelo número de processos).
3. Compartilhar centroides iniciais com `MPI_Bcast`.
4. Em cada iteração, cada processo atribui os pontos de seu bloco e acumula somas e contagens por cluster em memória local.
5. Combinar somas e contagens com coletivas como `MPI_Allreduce`; cada processo atualiza os centroides antes da próxima iteração.
6. Medir o tempo do processo mais lento (por exemplo, com `MPI_Reduce` + `MPI_MAX`), declarar o escopo medido e validar cada centroide contra o baseline.

**Questões ainda abertas:** sincronização necessária, custos das coletivas, correspondência numérica das somas, balanceamento quando há mais processos que pontos, limite de slots no WSL, tratamento de casos-limite e metodologia justa de comparação de tempo. O baseline cronometra somente iterações; qualquer tempo MPI que também inclua distribuição inicial precisa ser identificado ou analisado em uma métrica separada. Evitar inferir speedup diretamente de medições com `--oversubscribe` sem explicitar essa restrição.

## 7. Reproduzir as versões existentes

Ambiente observado: Windows 11 + VS Code + Ubuntu WSL2; `g++` Ubuntu 15.2.0; 4 unidades de processamento visíveis em `nproc`. Executar na **raiz** de `projeto_pp/`:

```bash
make
./build/10_kmeans_base 1000000 8 20
OMP_NUM_THREADS=4 OMP_DYNAMIC=FALSE ./build/10_kmeans_omp 1000000 8 20
make validacao
bash scripts/validar_openmp.sh
python3 scripts/gerar_graficos_openmp.py \
    resultados/resultados_openmp.csv resultados/graficos_teste
```

O Makefile atual compila 5 executáveis: `10_kmeans_base`, `10_kmeans_omp`, `10_kmeans_perfil`, `validacao_seq`, `validacao_omp`, todos sob `build/`. A regra `make mpi` está prevista, mas depende de `mpi/10_kmeans.cpp` ainda inexistente. Os scripts de medição foram adaptados para a estrutura com `build/` e passaram na verificação `bash -n`, mas **não houve nova execução integral após a reorganização**.

## 8. Continuidade e documentação cruzada

- **`README.md`:** instruções gerais para colaboradores e execução do zero.
- **`AGENTS.md`:** regras obrigatórias para futuras IAs/agentes.
- **`docs/ESTADO_ATUAL.md`:** evidência recente do que está pronto e do que ainda é pendência.
- **`docs/EXPERIMENTOS.md`:** metodologia e interpretação dos dados; deve ser revisado para a estrutura reorganizada.
- **`docs/PROXIMOS_PASSOS.md`:** fila priorizada, checklist e handoff entre sessões.
- **`docs/REORGANIZACAO.md`:** diferenças entre organização local e branches antigas do GitHub.

Ao concluir uma etapa: (a) informar arquivos alterados; (b) registrar comando e resultado do teste; (c) atualizar `docs/ESTADO_ATUAL.md` e `docs/PROXIMOS_PASSOS.md`; (d) preservar dados originais; (e) não marcar tarefas sem evidência.

**Próximo trabalho:** revisar `docs/EXPERIMENTOS.md`, conferir `README.md` e o `AUTORES.md`, e depois implementar MPI. Os requisitos oficiais do professor devem prevalecer sobre qualquer sugestão técnica deste documento.
