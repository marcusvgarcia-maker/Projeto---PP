# Experimentos e evidências — Projeto PP / K-means

> **Atualizacao confirmada em 11/11/2026:** MPI integrado a main pelo PR #19 (merge d9fb659). O aluno criou a branch local entrega/finalizacao e o commit 852af1d com o ambiente Docker; sua publicacao ainda nao foi demonstrada. No conteiner, seis executaveis compilaram, OpenMP passou em 9/9 comparacoes e MPI em 33/33, com erro maximo 0,0. A campanha conjunta e o novo perfilador foram preparados, mas ainda precisam ser executados na maquina do aluno. Consulte [o roteiro atual](ROTEIRO_CAMPANHA_DOCKER.md). Os registros datados anteriores descrevem as respectivas etapas historicas.


> **Data de referência:** 10/11/2026 (America/Sao_Paulo)  
> **Disciplina:** Programação Paralela (CCO085), IESB, 2026/2 · Problema 10  
> **Estado:** implementações sequencial, OpenMP e MPI compiladas; validação MPI, escalabilidade forte e fraca e comparação preliminar registradas.  
> **Repositório:** https://github.com/marcusvgarcia-maker/Projeto---PP  
> **Contexto Git:** a reorganização foi integrada à `main` pelo PR #18 em 10/11/2026. Os arquivos MPI estão na branch local `desenvolvimento/mpi`, com três commits concluídos, ainda sem publicação ou integração.

## 1. Objetivo e critérios de análise

Comparar a implementação sequencial de referência do algoritmo de Lloyd para K-means com as versões **OpenMP** (memória compartilhada) e **MPI** (processos com comunicação explícita). Avaliar corretude, tempo das iterações, *speedup*, eficiência, escalabilidade forte e fraca, custo de paralelização e aderência qualitativa à Lei de Amdahl.

**Fonte de evidência:** códigos, scripts e CSVs do projeto, junto às saídas de terminal confirmadas em 10/11/2026. Os dados não garantem o mesmo desempenho em outros equipamentos. Distinguir resultados **observados** de hipóteses sobre suas causas. Preservar os arquivos históricos em qualquer reteste.

## 2. Ambiente experimental e limitações

| Elemento | Informação observada |
|---|---|
| Plataforma | Windows 11, VS Code, Ubuntu no WSL2 |
| Diretório do clone de integração | `~/projeto_pp_integracao` (sistema de arquivos do Ubuntu) |
| Compilador C++ | `g++` 15.2.0 (Ubuntu), com `-O2 -std=c++17` |
| OpenMP | Compilação com `-fopenmp`; 1, 2 e 4 threads; `OMP_DYNAMIC=FALSE` nos scripts |
| MPI | Open MPI via `mpic++`; execução com `mpirun --oversubscribe -np P`; 1, 2 e 4 processos |
| Capacidade informada | `nproc` retornou 4 processadores lógicos disponíveis; não comprova 4 núcleos físicos |
| Repetições | Cinco medições após aquecimento descartado por configuração |
| Métricas | Tempo médio, mediana, desvio-padrão amostral, *speedup* e eficiência |

O uso de `--oversubscribe` é **uma opção de lançamento**, não uma evidência de que houve efetivamente mais processos que CPUs disponíveis. As condições concretas de alocação de recursos devem ser verificadas se a comparação for refeita. Houve avisos de arquivos de ajuda PMIx/PRRTE em uma verificação de versão do MPI, mas execuções funcionais com `mpirun` foram realizadas.

**Ainda não registrados de forma completa:** modelo da CPU, número de núcleos físicos, memória RAM, versão exata do Ubuntu, afinidade dos processos/threads, política de energia e carga concorrente. A dispersão dos tempos foi relevante. Não atribuir a variação exclusivamente ao WSL2, à comunicação MPI ou ao escalonamento sem testes que isolem esses fatores.

## 3. Programa, invariantes e escopo de tempo

O problema é o K-means (Lloyd) em duas dimensões. O gerador determinístico original usa semente `2024ULL`; os primeiros `K` pontos inicializam os centroides. Cada uma das `IT` iterações atribui cada ponto ao centroide de menor distância euclidiana ao quadrado, com desempate pelo primeiro índice, acumula as coordenadas e contagens e atualiza centroides não vazios. Clusters vazios preservam o centroide anterior. A versão sequencial de referência não deve ser alterada.

**Entradas principais:** `N = 100000`, `1000000` e `5000000`; `K=8`; `IT=20`. Os programas mantêm esses dados determinísticos. No benchmark de escalabilidade fraca, `N = P × 1000000`, mantendo `K=8` e `IT=20`.

**Tempo efetivamente reportado:**

- **Sequencial:** apenas o laço das iterações, excluindo geração dos dados e checksum final.
- **OpenMP:** laço principal com suas regiões paralelas; estruturas auxiliares preparadas antes do cronômetro não entram no tempo.
- **MPI:** o cronômetro (`MPI_Wtime`) começa após gerar e distribuir os pontos (`MPI_Scatterv`) e compartilhar os centroides iniciais (`MPI_Bcast`); cobre atribuições, acumulações locais, duas reduções `MPI_Allreduce` por iteração e atualização dos centroides. O tempo final é o **máximo entre os processos**, obtido por `MPI_Reduce` com `MPI_MAX`. Inicialização, distribuição inicial e encerramento MPI não estão incluídos na métrica.

Assim, a comparação avalia predominantemente **o custo das iterações** e não o tempo de execução de ponta a ponta. As coletivas dentro do laço MPI estão incluídas; a distribuição inicial não. Não generalizar estes resultados para aplicações que precisem distribuir os dados a cada execução.

O `checksum` de quatro casas decimais é útil como triagem, mas **não substitui** a comparação das coordenadas individuais de cada centroide.

## 4. Protocolo de medição e métricas

### 4.1 Baseline inicial

`scripts/medir_baseline.sh`: três tamanhos × cinco repetições, após aquecimento, totalizando 15 medições. Dados históricos: `resultados/baseline.csv`. O script reorganizado direciona novos ensaios a `resultados/baseline_reteste.csv`; sua execução integral após a reorganização não foi confirmada nesta etapa.

### 4.2 Escalabilidade forte OpenMP

Dados históricos: `resultados/resultados_openmp.csv`. Três valores de `N` × cinco rodadas × quatro variantes (sequencial, OpenMP com 1, 2 ou 4 threads) = **60 medições**. O baseline foi medido dentro da própria campanha. `scripts/medir_openmp.sh` foi adaptado para gerar `resultados/resultados_openmp_reteste.csv` em um futuro reteste; não confundir com os dados históricos.

### 4.3 Escalabilidade forte MPI

`scripts/medir_mpi.sh`: três valores de `N` × cinco rodadas × quatro variantes (sequencial, MPI com 1, 2 ou 4 processos) = **60 medições**. Para cada N houve aquecimento sequencial e MPI descartados; cada rodada mediu o baseline e as três configurações MPI. Checksums foram comparados ao sequencial, e as medições foram registradas em `resultados/resultados_mpi.csv`. O script `scripts/analisar_mpi.py` validou **60/60 registros** e gerou `resultados/resumo_mpi.csv` (12 configurações + cabeçalho).

### 4.4 Comparação OpenMP × MPI

`scripts/comparar_openmp_mpi.py` consolidou os CSVs de resumo em `resultados/comparacao_openmp_mpi.csv` (18 configurações + cabeçalho) e gerou nove gráficos em `resultados/graficos_comparacao/`.

**Ressalva fundamental:** OpenMP e MPI foram medidos em **campanhas diferentes**, com seus respectivos baselines e condições não estritamente controladas. Portanto, a comparação de *speedup* e eficiência entre as campanhas **não é diretamente controlada**. Os tempos absolutos também são indicativos, e diferenças pequenas exigem reteste conjunto com ordem de execução alternada e registro de variabilidade.

### 4.5 Escalabilidade fraca MPI

`scripts/medir_escalabilidade_fraca_mpi.sh`: com `N/P = 1000000` pontos por processo, foram medidos `P=1,2,4`, logo `N=1000000,2000000,4000000`; cinco repetições por configuração após aquecimento, totalizando **15 medições**. Os checksums de cada tamanho foram comparados ao baseline sequencial correspondente. Dados em `resultados/escalabilidade_fraca_mpi.csv` (15 registros + cabeçalho). `scripts/analisar_escalabilidade_fraca_mpi.py` validou **15/15 registros**, gerou `resultados/resumo_escalabilidade_fraca_mpi.csv` e o gráfico correspondente.

### 4.6 Fórmulas

Para a escalabilidade **forte**, em cada campanha e para cada tamanho fixo de entrada:

\[
S(P)=\frac{\overline{T}_{seq}}{\overline{T}_{par}(P)},\qquad
E(P)=\frac{S(P)}{P}\times 100\%.
\]

A referência é **o sequencial da mesma campanha**, e não o executável paralelo com apenas um worker. As estatísticas foram calculadas sobre **cinco tempos**, usando desvio-padrão amostral. Eficiências ligeiramente superiores a 100% com um processo/thread não comprovam escalabilidade superlinear.

Para a escalabilidade **fraca**, com carga `N_0` por processo:

\[
E_{fraca}(P)=\frac{\overline{T}(1,N_0)}{\overline{T}(P,P\,N_0)}\times100\%.
\]

A eficiência ideal é 100% (tempo constante). Trata-se da métrica observada para o **tempo cronometrado das iterações**, com as ressalvas já indicadas.

## 5. Perfilamento sequencial e Lei de Amdahl

Uma medição instrumentada de `perfilamento/10_kmeans.cpp`, com `N=1000000`, `K=8`, `IT=20`, apresentou:

| Trecho | Tempo | Fração observada |
|---|---:|---:|
| Atribuição | 0,304297 s | 87,38% |
| Recálculo dos centroides | 0,043902 s | 12,61% |
| Total reportado do laço | 0,348253 s | 100% (aprox.) |

A atribuição foi o *hotspot* dessa execução. **Não tratar 87,38% como a fração paralelizável total**: o recálculo também tem componentes paralelizáveis e inclui sincronização/redução. Há dependência entre iterações, porque novos centroides alimentam a iteração seguinte. A previsão teórica e o confronto formal com a Lei de Amdahl **continuam pendentes**; não foi estimada experimentalmente uma fração sequencial estável.

## 6. Baseline inicial — 15 medições históricas

| N | Média (s) | Mediana (s) | Desvio-padrão amostral (s) |
|---:|---:|---:|---:|
| 100.000 | 0,039958 | 0,040211 | 0,001319 |
| 1.000.000 | 0,402359 | 0,384654 | 0,047630 |
| 5.000.000 | 2,192117 | 2,117201 | 0,272486 |

Esses dados são de uma campanha **separada** e não servem como denominador dos *speedups* OpenMP ou MPI apresentados abaixo.

## 7. OpenMP — resultados de escalabilidade forte

`K=8`, `IT=20`, cinco medidas por configuração; referência: baseline **da campanha OpenMP**.

| N | Versão | Média (s) | Mediana (s) | Desvio (s) | Speedup | Eficiência |
|---:|---|---:|---:|---:|---:|---:|
| 100.000 | Sequencial | 0,050713 | 0,046150 | 0,010242 | 1,000× | — |
| 100.000 | OpenMP 1 | 0,051308 | 0,039665 | 0,018677 | 0,988× | 98,8% |
| 100.000 | OpenMP 2 | 0,075015 | 0,085522 | 0,024506 | 0,676× | 33,8% |
| 100.000 | OpenMP 4 | 0,101940 | 0,060673 | 0,066067 | 0,497× | 12,4% |
| 1.000.000 | Sequencial | 0,527968 | 0,429901 | 0,250242 | 1,000× | — |
| 1.000.000 | OpenMP 1 | 0,464654 | 0,503341 | 0,078418 | 1,136× | 113,6% |
| 1.000.000 | OpenMP 2 | 0,638230 | 0,464040 | 0,295674 | 0,827× | 41,4% |
| 1.000.000 | OpenMP 4 | 0,539434 | 0,437513 | 0,215055 | 0,979× | 24,5% |
| 5.000.000 | Sequencial | 2,243186 | 2,283460 | 0,200970 | 1,000× | — |
| 5.000.000 | OpenMP 1 | 2,297215 | 2,494970 | 0,445382 | 0,976× | 97,6% |
| 5.000.000 | OpenMP 2 | 2,107286 | 2,057153 | 0,342129 | 1,064× | 53,2% |
| 5.000.000 | OpenMP 4 | 1,805006 | 1,621190 | 0,426521 | **1,243×** | **31,1%** |

Os números são **observações históricas**, não garantias de aceleração reproduzível. Para N=1.000.000 e duas threads, os tempos OpenMP variaram de 0,396783 a 0,974336 s; para N=100.000 e quatro threads, de 0,048745 a 0,190246 s. O motivo da variação não foi isolado.

## 8. MPI — resultados de escalabilidade forte

`K=8`, `IT=20`, cinco medidas por configuração; referência: baseline **da campanha MPI**. Dados e métricas: `resultados/resultados_mpi.csv` e `resultados/resumo_mpi.csv`.

| N | Versão | Média (s) | Speedup | Eficiência |
|---:|---|---:|---:|---:|
| 100.000 | Sequencial | 0,103463 | 1,000× | — |
| 100.000 | MPI 1 | 0,092206 | 1,122× | 112,2% |
| 100.000 | MPI 2 | 0,104039 | 0,994× | 49,7% |
| 100.000 | MPI 4 | 0,310480 | 0,333× | 8,3% |
| 1.000.000 | Sequencial | 0,691980 | 1,000× | — |
| 1.000.000 | MPI 1 | 0,669102 | 1,034× | 103,4% |
| 1.000.000 | MPI 2 | 0,367687 | **1,882×** | 94,1% |
| 1.000.000 | MPI 4 | 0,431920 | 1,602× | 40,1% |
| 5.000.000 | Sequencial | 2,341218 | 1,000× | — |
| 5.000.000 | MPI 1 | 2,316310 | 1,011× | 101,1% |
| 5.000.000 | MPI 2 | 2,050126 | 1,142× | 57,1% |
| 5.000.000 | MPI 4 | 1,469368 | **1,593×** | 39,8% |

**Interpretação restrita aos dados:** para 100 mil pontos, quatro processos foram mais lentos que um. Para um milhão, a menor média MPI foi com dois processos; para cinco milhões, com quatro processos. São compatíveis com possíveis efeitos de overhead, sincronização e variação do ambiente, **não com a comprovação isolada de qualquer causa**. Medianas e desvios completos constam no `resumo_mpi.csv`; não foram transcritos aqui por não constarem nas saídas compartilhadas.

## 9. Comparação exploratória OpenMP × MPI

Tempos médios absolutos, em segundos, extraídos das duas campanhas distintas:

| N | Workers | OpenMP (s) | MPI (s) | Menor média observada |
|---:|---:|---:|---:|---|
| 100.000 | 1 | 0,051308 | 0,092206 | OpenMP |
| 100.000 | 2 | 0,075015 | 0,104039 | OpenMP |
| 100.000 | 4 | 0,101940 | 0,310480 | OpenMP |
| 1.000.000 | 1 | 0,464654 | 0,669102 | OpenMP |
| 1.000.000 | 2 | 0,638230 | 0,367687 | MPI |
| 1.000.000 | 4 | 0,539434 | 0,431920 | MPI |
| 5.000.000 | 1 | 2,297215 | 2,316310 | OpenMP |
| 5.000.000 | 2 | 2,107286 | 2,050126 | MPI |
| 5.000.000 | 4 | 1,805006 | 1,469368 | MPI |

Para cinco milhões de pontos e quatro workers, a média MPI foi cerca de **18,6% menor** que a OpenMP registrada. Isso **não estabelece superioridade geral do MPI**, pois há dispersão e sessões diferentes de medição.

**Atenção à normalização:** com N=100.000, o sequencial da campanha OpenMP teve média `0,050713 s`, enquanto na campanha MPI teve média `0,103463 s`. Portanto, o gráfico que compara *speedups* calculados separadamente **não é uma comparação experimental controlada de aceleração relativa**. Interpretar as curvas como históricos próprios de cada campanha; um protocolo único com baseline comum é necessário para comparação conclusiva.

Os nove gráficos de comparação existentes são descritivos da coleta, não uma prova de diferença estatisticamente significativa.

## 10. MPI — escalabilidade fraca

Protocolo: `P={1,2,4}`, `N=P×1000000`, `K=8`, `IT=20`; cinco medições por configuração, carga nominal de **1 milhão de pontos por processo**.

| P | N total | Média (s) | Desvio amostral (s) | Eficiência fraca |
|---:|---:|---:|---:|---:|
| 1 | 1.000.000 | 0,670650 | 0,243925 | 100,0% |
| 2 | 2.000.000 | 0,814082 | 0,120106 | 82,4% |
| 4 | 4.000.000 | 1,661666 | 0,191052 | 40,4% |

A média com quatro processos foi aproximadamente **2,48 vezes** a média com um processo, apesar da carga por processo constante. Houve perda observada de eficiência fraca; a variabilidade elevada limita conclusões causais. O experimento não inclui o tempo de distribuição inicial dos dados.

Arquivos: `resultados/escalabilidade_fraca_mpi.csv`, `resultados/resumo_escalabilidade_fraca_mpi.csv` e `resultados/graficos_mpi/escalabilidade_fraca_mpi.png`.

## 11. Corretude validada

### 11.1 OpenMP

`scripts/validar_openmp.sh` usa `build/validacao_seq` e `build/validacao_omp` para comparar cada centroide final impresso com 17 dígitos significativos. Três entradas (`N=100000,1000000,5000000`), `K=8`, `IT=20` e 1, 2 ou 4 threads: **9/9 comparações aprovadas**. Evidência: `resultados/validacao_openmp.csv`.

### 11.2 MPI

1. **Checksum:** `scripts/validar_mpi.sh` passou em 9/9 cenários padrão (três N × P=1/2/4), com registro em `resultados/validacao_mpi.csv`; outros 9 cenários com N não divisível por P e 15 cenários variados foram testados no terminal. **Total relatado: 33/33 checksums aprovados.**
2. **Centroides individuais:** `scripts/validar_centroides_mpi.py` comparou todos os centroides em 11 entradas × P=1,2,4, usando `math.isclose(rel_tol=1e-12,abs_tol=1e-10)`. **33/33 casos aprovados**, com maior diferença absoluta reportada de **0,0** para as coordenadas exibidas em `%.17g`. Evidência: `resultados/validacao_centroides_mpi.csv`.

Os 11 cenários incluem N grandes e pequenos, N não divisível pelo número de processos, variações de K/IT, `IT=0` e P maior que N. A aprovação se refere **aos casos executados**. Não é prova formal de correção para toda entrada possível.

## 12. Artefatos, reprodução e situação dos scripts

| Artefato | Finalidade / resultado confirmado |
|---|---|
| `Makefile` | `make clean && make` compilou **seis executáveis**, incluindo `build/10_kmeans_mpi` |
| `scripts/validar_openmp.sh` | OpenMP: 9/9 testes aprovados |
| `scripts/validar_mpi.sh` | MPI: 9/9 checksums padrão; `resultados/validacao_mpi.csv` |
| `scripts/validar_centroides_mpi.py` | MPI: 33/33 comparações de centroides |
| `scripts/medir_mpi.sh` | 60 medições; `resultados/resultados_mpi.csv` |
| `scripts/analisar_mpi.py` | Validação 60/60; `resultados/resumo_mpi.csv` |
| `scripts/gerar_graficos_mpi.py` | Nove PNGs de tempo, speedup e eficiência em `resultados/graficos_mpi/` |
| `scripts/comparar_openmp_mpi.py` | 18 configurações consolidadas; CSV e nove PNGs em `resultados/graficos_comparacao/` |
| `scripts/medir_escalabilidade_fraca_mpi.sh` | 15 medições; `resultados/escalabilidade_fraca_mpi.csv` |
| `scripts/analisar_escalabilidade_fraca_mpi.py` | Validação 15/15; resumo e gráfico adicional em `resultados/graficos_mpi/` |
| `scripts/medir_baseline.sh`, `scripts/medir_openmp.sh` | Adaptados para retestes sem sobrescrever CSVs históricos; execução integral da versão reorganizada não confirmada |
| `scripts/gerar_graficos_openmp.py` | Regeneração OpenMP testada anteriormente; 9 PNGs + CSV de resumo em diretório de teste |

Comandos principais, a partir da raiz do clone no Ubuntu:

```bash
make clean && make
bash scripts/validar_openmp.sh
bash scripts/validar_mpi.sh
python3 scripts/validar_centroides_mpi.py
bash scripts/medir_mpi.sh
python3 scripts/analisar_mpi.py
python3 scripts/gerar_graficos_mpi.py
python3 scripts/comparar_openmp_mpi.py
bash scripts/medir_escalabilidade_fraca_mpi.sh
python3 scripts/analisar_escalabilidade_fraca_mpi.py
```

**Cuidado:** scripts de medição sobrescrevem **seus próprios CSVs de saída** se forem reexecutados. Antes de uma nova campanha, duplicar os dados originais ou adaptar os destinos com identificação de data/ambiente. A execução das medições consome recursos; não é necessária apenas para verificar a documentação.

## 13. Limitações e próximos trabalhos

- **Comparabilidade:** realizar uma campanha conjunta sequencial/OpenMP/MPI, com baseline na mesma sessão, alternando a ordem das versões e acompanhando dispersão; idealmente no Linux do laboratório e com registro do hardware.
- **Precisão experimental:** ampliar repetições se necessário; incluir comparações estatísticas e registro de afinidade/carga para avaliar a estabilidade dos ganhos.
- **Escalabilidade fraca OpenMP:** não foi apresentada campanha equivalente; não declarar concluída. A análise forte OpenMP e MPI e a fraca MPI já foram registradas.
- **Lei de Amdahl:** estimar e justificar a fração paralelizável efetiva, construir previsões e confrontar com os resultados, incluindo sincronização e coletivas; permanece pendente.
- **Medição de ponta a ponta:** opcionalmente medir inicialização, `Bcast`, `Scatterv`, iterações e finalização separadamente para avaliar overhead real da execução MPI completa.
- **Entrega:** conferir integridade de scripts, gráficos, `README.md`, `AUTORES.md` e branches/PRs. A entrega do Marco 2 está indicada para **12/11/2026**; apresentação para **19 ou 26/11/2026**, conforme a escala do grupo. O PDF de até seis páginas foi exigido no Marco 1; não afirmar obrigação de PDF final separado no Marco 2 sem conferir o enunciado.

## 14. Instruções para revisão e continuidade

Ao avaliar um novo resultado, identificar a campanha e os arquivos de origem; conferir N/K/IT e quantidade de workers; distinguir cálculo sobre média de cálculo sobre mediana; utilizar o baseline da mesma campanha; registrar o escopo de tempo cronometrado; preservar a proveniência dos CSVs; não inferir causalidade apenas de diferenças entre tempos. Atualizar `docs/ESTADO_ATUAL.md`, `docs/PROXIMOS_PASSOS.md`, `README.md` e `AGENTS.md` quando houver mudanças de status.

**Documentos relacionados:** `README.md` (execução), `AGENTS.md` (regras para IAs), `docs/ARQUITETURA.md` (método e paralelização), `docs/ESTADO_ATUAL.md` (estado efetivo), `docs/PROXIMOS_PASSOS.md` (fila de trabalho), `docs/REORGANIZACAO.md` (histórico de integração Git).


## Campanha conjunta Docker — preparada em 11/11/2026

O protocolo e as hipoteses estao em ROTEIRO_CAMPANHA_DOCKER.md.
A coleta padrao produz 105 registros fortes, 30 fracos e 15 de perfilamento,
com aquecimentos separados, ordenacao embaralhada e arquivos exclusivos.
Os tempos iterativos e a duracao externa sao registrados separadamente.
O modelo de Amdahl usa atribuicao e acumulacao da copia instrumentada;
a parcela restante inclui atualizacao, alocacao/desalocacao e instrumentacao.
E uma estimativa ideal, nao uma fracao serial efetiva medida do paralelo.
O coletor MPI explicita --oversubscribe --bind-to none, e o OpenMP
OMP_DYNAMIC=FALSE e OMP_PROC_BIND=FALSE. A configuracao difere das campanhas
historicas e precisa ser identificada separadamente. As opcoes de afinidade
estao descritas no manual oficial da serie Open MPI 4.1:
https://www.open-mpi.org/doc/v4.1/man1/mpirun.1.php

Nenhum numero dessa nova campanha foi produzido ainda na maquina do aluno.
A discussao final, os graficos finais e a comparacao com a previsao aguardam
a execucao real do protocolo.
