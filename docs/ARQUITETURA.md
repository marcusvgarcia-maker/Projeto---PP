# Arquitetura técnica — Projeto de Programação Paralela (K-means)

> **Disciplina:** Programação Paralela (CCO085), IESB — 2026/2  
> **Problema:** nº 10 — Agrupamento por k-médias (K-means), algoritmo de Lloyd  
> **Estado documentado:** 10/11/2026 — sequencial, OpenMP e MPI implementados e compilados; validações e experimentos registrados.  
> **Referência operacional:** clone Ubuntu/WSL2 `~/projeto_pp_integracao`, branch local `desenvolvimento/mpi`. A reorganização foi integrada à `main` pelo PR #18 em 10/11/2026. A implementação MPI ainda não foi publicada ou mesclada.

## 1. Objetivo e invariantes do algoritmo

Manter o comportamento do código sequencial fornecido pelo professor (`sequencial/10_kmeans.cpp`) e desenvolver implementações paralelas em OpenMP (memória compartilhada) e MPI (processos com espaços de endereçamento separados). Alterações na decomposição do trabalho não devem mudar as regras matemáticas do problema.

| Elemento | Regra preservada |
|---|---|
| Argumentos | `N` pontos, `K` clusters, `IT` iterações; padrões `1000000`, `8`, `20` |
| Geração | Pontos 2D determinísticos em `double`: estado `uint64_t s=2024ULL`; a cada coordenada, `s=s*6364136223846793005ULL+1`; valor `(s >> 40) % 1000` |
| Inicialização | Os primeiros `K` pontos são os centroides iniciais |
| Distância | Euclidiana ao quadrado: `(px[i]-cx[j])²+(py[i]-cy[j])²` |
| Empates | Vence o centroide de menor índice; troca do melhor somente quando `d < best` |
| Quantidade de ciclos | Exatamente `IT` iterações, sem parada antecipada |
| Recálculo | Média das coordenadas de todos os pontos atribuídos ao cluster |
| Cluster vazio | Preservar o centroide da iteração anterior |
| Saída | `N`, `K`, `it`, `checksum=%.4f` e `tempo=%.6f s`; o checksum soma `cx[j]+cy[j]` |
| Cronometragem | Somente o laço iterativo (o trabalho de preparação fica fora da medida reportada) |

O baseline assume valores coerentes de entrada. O MPI acrescenta validação explícita de `N >= 1`, `K >= 1`, `K <= N` e `IT >= 0`, abortando a execução distribuída se forem inválidos; esse tratamento de erros é uma diferença de interface, não do cálculo para entradas válidas.

## 2. Etapas, dependências e complexidade

Em cada iteração de Lloyd:

1. **Atribuição:** cada ponto recebe o índice do centroide mais próximo. São `K` comparações por ponto; os rótulos são independentes para pontos diferentes.
2. **Acumulação:** cada ponto contribui para duas somas de coordenadas e uma contagem do seu cluster; somas compartilhadas exigem redução segura.
3. **Atualização:** cada centroide não vazio é substituído pela média global dos pontos atribuídos a ele.
4. **Dependência entre iterações:** a iteração seguinte precisa dos centroides atualizados; não é correto sobrepor iterações arbitrariamente.

```text
               Centroides atuais
                       |
           +-----------+-----------+
           |                       |
       Ponto 0                 Demais pontos
           |                       |
           +----> Atribuições <----+
                       |
                 Acumulações
                       |
            Redução/combinação
                       |
              Novos centroides
                       |
                Próxima iteração
```

- Geração inicial sequencial: `O(N)`, fora do cronômetro.
- Trabalho por iteração sequencial: `O(NK + N + K)`; em `IT` iterações: `O(IT·(NK + N + K))`.
- Memória do baseline: `O(N+K)`.
- No OpenMP, o recálculo usa acumuladores privados, com custo de memória adicional `O(TK)` para `T` threads.
- No MPI, a computação local é aproximadamente `O(IT·(N/P·K + N/P + K))` para `P` processos, **mais** o custo das coletivas, que depende da implementação MPI, hardware, tamanho das mensagens e sincronização. A distribuição não é necessariamente uniforme quando `N % P != 0`.

## 3. Organização dos fontes e artefatos

```text
projeto_pp_integracao/
├── Makefile
├── README.md
├── AGENTS.md
├── AUTORES.md
├── sequencial/10_kmeans.cpp
├── perfilamento/10_kmeans.cpp
├── openmp/10_kmeans.cpp
├── mpi/10_kmeans.cpp
├── validacao/{sequencial.cpp,openmp.cpp}
├── scripts/
│   ├── medir_baseline.sh, medir_openmp.sh, validar_openmp.sh
│   ├── gerar_graficos_openmp.py
│   ├── validar_mpi.sh, validar_centroides_mpi.py
│   ├── medir_mpi.sh, analisar_mpi.py, gerar_graficos_mpi.py
│   ├── comparar_openmp_mpi.py
│   ├── medir_escalabilidade_fraca_mpi.sh
│   └── analisar_escalabilidade_fraca_mpi.py
├── resultados/
│   ├── baseline.csv, resultados_openmp.csv, resumo_openmp.csv
│   ├── resultados_mpi.csv, resumo_mpi.csv
│   ├── validacao_openmp.csv, validacao_mpi.csv
│   ├── validacao_centroides_mpi.csv
│   ├── comparacao_openmp_mpi.csv
│   ├── escalabilidade_fraca_mpi.csv
│   ├── resumo_escalabilidade_fraca_mpi.csv
│   ├── graficos/                # gráficos OpenMP históricos
│   ├── graficos_mpi/            # 9 gráficos fortes + 1 de escala fraca
│   └── graficos_comparacao/     # 9 gráficos comparativos
└── docs/{ARQUITETURA.md,ESTADO_ATUAL.md,EXPERIMENTOS.md,PROXIMOS_PASSOS.md,REORGANIZACAO.md}
```

`build/` contém executáveis locais e é ignorado pelo Git. Esta árvore resume os arquivos relevantes, não todos os arquivos do repositório. Novos arquivos MPI e resultados ainda estavam **não rastreados** pelo Git na última auditoria, embora existam no clone local.

## 4. Baseline e perfilamento

**Baseline:** `sequencial/10_kmeans.cpp`, preservado como referência de corretude.  
**Perfilamento:** `perfilamento/10_kmeans.cpp`, que cronometra separadamente as fases do laço.

Uma execução de perfilamento com `N=1000000`, `K=8`, `IT=20` encontrou:

| Etapa | Tempo (s) | Participação |
|---|---:|---:|
| Atribuição | 0,304297 | 87,38% |
| Recálculo | 0,043902 | 12,61% |
| Total instrumentado | 0,348253 | aproximadamente 100% |

A atribuição foi o principal *hotspot* **nessa execução**. O percentual de 87,38% não equivale automaticamente à fração paralelizável para a Lei de Amdahl, pois partes do recálculo também foram paralelizadas, e as versões paralelas introduzem comunicação/sincronização.

## 5. OpenMP — implementação em memória compartilhada

**Fonte:** `openmp/10_kmeans.cpp`. **Compilação:** `g++ -O2 -std=c++17 -fopenmp`.

### 5.1 Atribuição

Usa `#pragma omp parallel for schedule(static)` para dividir as posições de `rotulo` entre as threads. Cada iteração lê `px`, `py`, `cx`, `cy` e escreve apenas o seu rótulo; portanto não há conflito de escrita entre threads na fase de atribuição. O escalonamento estático é compatível com o número fixo de comparações (`K`) por ponto.

### 5.2 Acumulação e atualização

Cada thread acumula em seus próprios vetores `sx_local`, `sy_local` e `cnt_local`, indexados pelo identificador da thread. Após o encerramento da região paralela, os valores são combinados **manualmente e sequencialmente** por cluster, e os centroides são atualizados.

```cpp
#pragma omp parallel
{
    int tid = omp_get_thread_num();
    #pragma omp for schedule(static)
    for (int i = 0; i < N; ++i) {
        int j = rotulo[i];
        sx_local[tid][j] += px[i];
        sy_local[tid][j] += py[i];
        cnt_local[tid][j]++;
    }
}
// Combinação manual dos acumuladores e atualização dos centroides.
```

Não afirmar que a implementação usa cláusula `reduction(...)`, `atomic` ou `critical` para a acumulação: a redução é manual. A estratégia evita disputas de atualização por ponto, mas tem custo de criação/sincronização de regiões paralelas e combinação `O(TK)` por iteração. *False sharing* e contenção de memória são hipóteses, não causas diagnosticadas.

### 5.3 Evidência de corretude e desempenho OpenMP

- **9/9 validações aprovadas:** `N` em {100000,1000000,5000000}, `K=8`, `IT=20`, threads em {1,2,4}; comparação dos centroides finais impressos com `%.17g` usando os programas de `validacao/`.
- **60 medições de desempenho**, cinco por configuração, mais nove gráficos, preservadas em `resultados/resultados_openmp.csv`, `resultados/resumo_openmp.csv` e `resultados/graficos/`.
- Para `N=5000000` e 4 threads: tempo médio OpenMP `1,805006 s` contra sequencial `2,243186 s`, speedup aproximado de `1,243×`, eficiência `31,1%`, **nessa campanha**.

## 6. MPI — implementação em memória distribuída

**Fonte:** `mpi/10_kmeans.cpp`. **Compilação:** `mpic++ -O2 -std=c++17`, via `make mpi` ou `make` (alvo padrão agora inclui MPI). **Estado:** compilação bem-sucedida, execução funcional e testes automatizados de corretude concluídos nos cenários relatados.

### 6.1 Inicialização e distribuição de dados

1. `MPI_Init` inicializa o ambiente; cada processo consulta `rank` (`MPI_Comm_rank`) e número total `P` (`MPI_Comm_size`).
2. O **rank 0** gera os mesmos `N` pontos determinísticos do baseline e seleciona os primeiros `K` como centroides iniciais.
3. Cada processo calcula as contagens de pontos e os deslocamentos dos `P` blocos **contíguos**, com:

   ```cpp
   quantidade[p] = N / P + (p < N % P ? 1 : 0);
   deslocamento[p] = (p == 0 ? 0 : deslocamento[p-1] + quantidade[p-1]);
   ```

4. `MPI_Bcast` compartilha os vetores iniciais `cx` e `cy` a partir do rank 0.
5. Dois `MPI_Scatterv` distribuem os vetores de coordenadas `px` e `py`, respeitando blocos desiguais quando `N` não é divisível por `P`.
6. Cada processo mantém somente seus pontos locais para os cálculos seguintes. O rank 0 mantém adicionalmente os vetores globais usados na distribuição.

Há suporte funcional testado para `P > N`, quando alguns processos ficam sem pontos locais. As contagens e deslocamentos do `MPI_Scatterv` são representados por `int`, consistentes com a interface de `N` do programa; não declarar suporte a entradas maiores que os limites desses tipos.

### 6.2 Iteração local e comunicação coletiva

Em cada iteração, cada processo:

1. Percorre os `n_local` pontos e determina os rótulos com o mesmo critério de distância e desempate do baseline.
2. Zera os vetores de somas `2*K` e contagens `K` e acumula contribuições somente de seus próprios pontos.
3. Executa **dois `MPI_Allreduce`**: um com `MPI_DOUBLE`/`MPI_SUM` para somas de `x` e `y`; outro com `MPI_LONG`/`MPI_SUM` para contagens por cluster.
4. Atualiza localmente todos os centroides não vazios com as somas e contagens **globais**. Como `Allreduce` disponibiliza os mesmos agregados em todos os processos, todos começam a próxima iteração com os centroides atualizados, sem um `MPI_Bcast` adicional a cada ciclo.

```text
                      MPI_Bcast (cx, cy)
                             |
                   MPI_Scatterv (px, py)
                             |
           +-----------------+-----------------+
           |                 |                 |
         Rank 0           Rank 1            Rank P-1
        pontos locais    pontos locais      pontos locais
           |                 |                 |
       atribuição        atribuição         atribuição
       e somas           e somas            e somas
           +-----------------+-----------------+
                             |
                MPI_Allreduce (somas)
                MPI_Allreduce (contagens)
                             |
             atualiza centroides em cada rank
                             |
                próxima iteração (IT vezes)
```

**Por que `Allreduce`?** A fase de atribuição é independente por ponto, mas os centroides requerem as contribuições de **todos** os processos. A coletiva combina os acumuladores e disponibiliza o resultado em cada processo. Seu custo é pago a cada iteração; portanto, há potencial perda de eficiência para problemas pequenos ou aumento de processos, sem atribuir causalidade exclusiva a esse fator com os dados atuais.

### 6.3 Medição de tempo e saída

A implementação executa `MPI_Barrier` e inicia `MPI_Wtime` **depois** da geração dos dados, da difusão inicial dos centroides e da distribuição `Scatterv`. Ao fim de `IT` ciclos, mede a duração local e usa `MPI_Reduce(..., MPI_MAX, root=0)` para reportar o **maior tempo entre os processos**. Somente o rank 0 imprime a linha com checksum e tempo.

A saída opcional com quarto argumento `--centroides` faz o rank 0 imprimir `CENTROIDE j x y` com `%.17g` para cada cluster; isso é usado para validação individual. A opção não faz parte dos três argumentos originais do baseline.

**Limite da comparação temporal:** os tempos sequencial, OpenMP e MPI representam a fase iterativa, não o custo total da aplicação. Preparação, alocação inicial e distribuição MPI inicial estão fora da região cronometrada. Já as coletivas `Allreduce` de cada ciclo estão dentro dela. Não inferir desempenho fim a fim ou custo completo de comunicação usando apenas o campo `tempo`.

### 6.4 Corretude MPI comprovada nos cenários ensaiados

- `scripts/validar_mpi.sh` registrou **9/9** comparações de checksum para três tamanhos padrão e `P=1,2,4`, em `resultados/validacao_mpi.csv`.
- Outros testes apresentados no terminal cobriram **9 configurações de distribuição desigual** e **15 testes de casos variados**, totalizando **33/33 verificações de checksum** no conjunto executado.
- `scripts/validar_centroides_mpi.py` verificou **33/33 configurações** (11 triplas `N,K,IT` vezes `P=1,2,4`) comparando **todos os centroides finais** contra `build/validacao_seq`, com `rel_tol=1e-12` e `abs_tol=1e-10`. O maior erro absoluto reportado foi `0.0` nas coordenadas impressas em 17 dígitos significativos. O CSV está em `resultados/validacao_centroides_mpi.csv`.
- Foram incluídos `IT=0`, `K=1`, valores pequenos e não divisíveis de `N`, e um caso com `P>N`.

As validações sustentam equivalência **nessas entradas**, não uma prova universal. A equivalência exata observada nos valores impressos não deve ser generalizada para qualquer outro conjunto de dados de ponto flutuante.

### 6.5 Desempenho MPI registrado

**Escalabilidade forte:** `N` constante em {100000,1000000,5000000}, `K=8`, `IT=20`, `P=1,2,4`; cinco repetições por configuração, com sequencial intercalado, totalizando **60 medições** (`resultados/resultados_mpi.csv`). Estatísticas em `resultados/resumo_mpi.csv`; **9 gráficos** em `resultados/graficos_mpi/` (tempo, speedup, eficiência por N).

| N | Sequencial médio (s) | MPI 1 (s) | MPI 2 (s) | MPI 4 (s) |
|---:|---:|---:|---:|---:|
| 100.000 | 0,103463 | 0,092206 | 0,104039 | 0,310480 |
| 1.000.000 | 0,691980 | 0,669102 | 0,367687 | 0,431920 |
| 5.000.000 | 2,341218 | 2,316310 | 2,050126 | 1,469368 |

Para `N=5000000, P=4`, o speedup médio MPI foi **1,593×**, com eficiência **39,8%**, em comparação ao sequencial da **mesma campanha**.

**Escalabilidade fraca:** carga de `1.000.000` pontos por processo, com `P=1,2,4`, respectivamente `N=1.000.000`, `2.000.000` e `4.000.000`, cinco repetições por configuração (**15 medições**). Dados em `resultados/escalabilidade_fraca_mpi.csv`, resumo em `resultados/resumo_escalabilidade_fraca_mpi.csv` e gráfico `resultados/graficos_mpi/escalabilidade_fraca_mpi.png`.

| Processos | Tempo médio (s) | Desvio-padrão (s) | Eficiência fraca |
|---:|---:|---:|---:|
| 1 | 0,670650 | 0,243925 | 100,0% |
| 2 | 0,814082 | 0,120106 | 82,4% |
| 4 | 1,661666 | 0,191052 | 40,4% |

A eficiência fraca é `T(1,N0)/T(P,P·N0) × 100%`. Os dados indicam perda de eficiência com 4 processos e dispersão relevante entre repetições. O tempo reportado continua excluindo a distribuição inicial de dados.

## 7. Comparação OpenMP × MPI e limitações metodológicas

`resultados/comparacao_openmp_mpi.csv` contém **18 configurações paralelas** (9 OpenMP e 9 MPI); `resultados/graficos_comparacao/` contém nove figuras com comparação de tempo, speedup e eficiência por tamanho de entrada.

**Ressalva essencial:** as campanhas OpenMP e MPI ocorreram em sessões diferentes, com baselines médios diferentes (por exemplo, para `N=100000`: **0,050713 s** no ensaio OpenMP e **0,103463 s** no ensaio MPI). Assim, comparar diretamente os speedups de campanhas diferentes pode induzir a conclusões erradas. Comparações de tempo médio entre as versões também são **preliminares**, pois a carga do sistema e as condições da sessão podem variar. É recomendado realizar uma campanha conjunta, intercalada e controlada, antes de declarar superioridade geral.

O ambiente confirmado é Windows 11 + Ubuntu/WSL2, `g++` 15.2.0, OpenMPI, `nproc=4`. Os testes MPI usaram `mpirun --oversubscribe`; **isso não demonstra, por si só, que houve oversubscription real**, mas torna importante registrar a alocação efetiva dos processos, os limites de CPU e o ambiente do laboratório. Não atribuir as oscilações apenas a MPI, comunicação ou WSL2 sem medição específica.

Também continuam pendentes: campanha equivalente de escalabilidade fraca OpenMP, identificação mais completa do hardware e discussão quantitativa da Lei de Amdahl. Os dados e a metodologia detalhada estão em `docs/EXPERIMENTOS.md`.

## 8. Compilação, execução e validação

Na raiz do clone Ubuntu:

```bash
make clean && make
# Executáveis gerados: base, omp, perfil, validacao_seq, validacao_omp, mpi

./build/10_kmeans_base 1000000 8 20
OMP_NUM_THREADS=4 OMP_DYNAMIC=FALSE ./build/10_kmeans_omp 1000000 8 20
mpirun --oversubscribe -np 4 ./build/10_kmeans_mpi 1000000 8 20

bash scripts/validar_openmp.sh
bash scripts/validar_mpi.sh
python3 scripts/validar_centroides_mpi.py

python3 scripts/analisar_mpi.py
python3 scripts/gerar_graficos_mpi.py
python3 scripts/comparar_openmp_mpi.py
python3 scripts/analisar_escalabilidade_fraca_mpi.py
```

As rotinas `medir_mpi.sh` e `medir_escalabilidade_fraca_mpi.sh` **refazem as medições** e escrevem nos CSVs indicados; preservar os resultados históricos antes de reexecutá-las. Os scripts OpenMP de reteste usam nomes de saída próprios.

## 9. Continuidade, responsabilidades e Git

- `README.md`: visão geral, comandos para executar e evidências principais.
- `AGENTS.md`: instruções de continuidade e cautelas para assistentes de programação.
- `docs/ESTADO_ATUAL.md`: status com evidências de terminal.
- `docs/EXPERIMENTOS.md`: protocolo, resultados numéricos e limitações.
- `docs/PROXIMOS_PASSOS.md`: tarefas restantes e preparação de entrega.
- `docs/REORGANIZACAO.md`: histórico da reestruturação e integração das branches.
- `AUTORES.md`: divisão de responsabilidades do grupo.

A reorganização foi publicada na branch `organizacao/kmeans`, com PR [#18](https://github.com/marcusvgarcia-maker/Projeto---PP/pull/18) para `main`. O trabalho MPI permanece na branch local `desenvolvimento/mpi`, derivada de `organizacao/kmeans`. **Antes de criar commit, publicar ou mesclar**, verificar o estado real do repositório, do PR e dos revisores; não sobrescrever mudanças não commitadas nem mesclar histórias antigas sem revisão.

**Estado final deste documento (10/11/2026):** sequencial, OpenMP e MPI compilados e validados nas configurações descritas; medições e gráficos MPI criados. Pendem análise final de Amdahl, revisão metodológica/experimental, atualização dos próximos passos e integração Git após revisão.
