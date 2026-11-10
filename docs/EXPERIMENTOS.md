# Experimentos e evidências — Projeto PP / K-means

> **Data de referência:** 09/11/2026 (America/Sao_Paulo)  
> **Disciplina:** Programação Paralela (CCO085), IESB, 2026/2 · Problema 10  
> **Estado:** experimentos sequencial e OpenMP realizados; MPI **não implementado nem medido**.  
> **Escopo:** documentação da pasta **local** `projeto_pp/`; não presumir publicação na branch `main` do GitHub.

## 1. Objetivo e critérios de análise

Comparar o desempenho da implementação **sequencial de referência** do algoritmo de Lloyd para K-means com as versões paralelas requeridas pelo professor: **OpenMP** e, futuramente, **MPI**. Registrar tempo, *speedup*, eficiência, escalabilidade forte e fraca, relação com a Lei de Amdahl, evidências de corretude e limitações experimentais.

**Fonte da verdade:** os arquivos CSV originais e o código efetivamente compilado. Resultados reproduzidos neste documento descrevem execuções já realizadas, **não** garantem comportamento idêntico em outras máquinas. Não inventar dados MPI ou medições de escalabilidade fraca.

## 2. Ambiente experimental conhecido

| Elemento | Informação confirmada |
|---|---|
| Sistema e editor | Windows 11, VS Code, Ubuntu via WSL2 |
| Shell usado na execução | Bash no Ubuntu/WSL2; projeto em `/mnt/c/Users/Thinkpad/Documents/Programas (criacao)/ProgParal/projeto_pp/` após reorganização |
| Compilador Linux | `g++ (Ubuntu 15.2.0-16ubuntu1) 15.2.0` |
| Paralelismo disponível | `nproc` retornou **4 unidades de processamento disponíveis** (não comprova 4 núcleos físicos) |
| Flags de compilação atuais | `-O2 -std=c++17`; OpenMP: adicional `-fopenmp` |
| Controle de threads | `OMP_NUM_THREADS` em {1, 2, 4}, `OMP_DYNAMIC=FALSE` |
| MPI | OpenMPI instalado; `mpirun --oversubscribe -np 4 /bin/echo MPI_OK` funcionou; sem `--oversubscribe` houve erro de alocação de slots; **nenhum benchmark MPI realizado** |

**Dados a completar antes da versão final:** modelo exato da CPU, RAM, número de núcleos físicos, versão exata do Ubuntu (`lsb_release -a`), modo de energia/carga concorrente, disponibilidade no laboratório. O uso de WSL2 e arquivos em `/mnt/c` deve ser informado ao interpretar os tempos. Não atribuir causalidade às oscilações sem investigação específica.

## 3. Programa, entradas e tempo medido

O baseline implementa K-means (Lloyd) em 2D com geração determinística de pontos (semente `2024ULL`), `K` centroides iniciais selecionados dos primeiros pontos e **IT iterações fixas** (sem parada antecipada). Cada iteração faz (i) atribuição ao centroide mais próximo por distância euclidiana ao quadrado e (ii) acumulação de coordenadas/contagens e atualização dos centroides. Clusters vazios conservam o centroide anterior.

Para os experimentos realizados:

- `N = 100000`, `1000000` e `5000000`; `K=8`; `IT=20`.
- As entradas são iguais para sequencial e OpenMP: não há entradas aleatórias diferentes entre as versões.
- O tempo de saída `tempo=... s` do baseline e do OpenMP compreende **o laço de IT iterações**; exclui geração dos pontos, escolha inicial dos centroides e cálculo final do checksum. No OpenMP, estruturas auxiliares alocadas antes de `t0` também não entram nessa medida.
- O checksum tem **quatro casas decimais**, útil como triagem, mas insuficiente como prova individual de cada coordenada; para isso existe validação instrumentada.
- Os dados foram obtidos antes da reorganização local; após a reorganização, compilação e funcionamento foram testados, **sem repetir o experimento completo**.

## 4. Metodologia de medição

### 4.1 Baseline inicial (15 execuções medidas)

Script original (agora adaptado): `scripts/medir_baseline.sh`. Para cada N, uma execução de aquecimento **descartada**, seguida de **cinco execuções medidas**, sempre com K=8 e IT=20. O registro original está em `resultados/baseline.csv` e deve ser preservado. A versão reorganizada do script grava por padrão em `resultados/baseline_reteste.csv`, evitando sobrescrita.

### 4.2 Comparação sequencial × OpenMP (60 execuções medidas)

Script: `scripts/medir_openmp.sh`. Para cada N, uma execução de aquecimento do sequencial e uma de cada configuração OpenMP (1, 2 e 4 threads); depois, cinco rodadas contendo **sequencial seguido de OpenMP com 1, 2 e 4 threads**. São 3 entradas × 5 repetições × 4 variantes = **60 linhas de medição**.

O experimento original está em `resultados/resultados_openmp.csv`; a versão adaptada do script grava novos testes em `resultados/resultados_openmp_reteste.csv`. **Não substituir os CSV originais sem conservar a proveniência**. O script verifica o checksum informado nas saídas; a comparação de centroides completos é realizada separadamente.

### 4.3 Métricas utilizadas

Para cada N, usar o **tempo médio sequencial medido dentro das mesmas 60 execuções**, e não a média do ensaio inicial de baseline:

\[
S(P) = \frac{\overline{T}_{\text{sequencial}}}{\overline{T}_{\text{OpenMP},P}},\qquad
E(P)=\frac{S(P)}{P}\times 100\%.
\]

`P` = número de threads. A **mediana** e o **desvio-padrão amostral** também são registrados, pois as amostras exibiram dispersão acentuada. Um speedup acima de 1 é uma aceleração observada nas médias; não prova ganho consistente sem avaliação de variabilidade. Um valor de eficiência maior que 100% em uma comparação com **uma thread** é um indicador de ruído/condições de execução distintas, não evidência de escalabilidade superlinear.

## 5. Perfilamento do sequencial (evidência preliminar)

Uma execução do código instrumentado `perfilamento/10_kmeans.cpp` para `N=1.000.000`, `K=8`, `IT=20`:

| Trecho | Tempo (s) | Fração do tempo |
|---|---:|---:|
| Atribuição | 0,304297 | **87,38%** |
| Recálculo dos centroides | 0,043902 | **12,61%** |
| Total do laço | 0,348253 | 100% |

A diferença residual é compatível com overhead dos instrumentos e arredondamentos. Trata-se de **uma medição**, não de um perfil agregado. A fase de atribuição foi o maior *hotspot* observado.

**Cuidado com a Lei de Amdahl:** 87,38% é o **peso temporal da fase de atribuição**, não uma estimativa demonstrada da fração paralelizável total, porque a fase de recálculo também foi paralelizada. A fração sequencial remanescente deve ser estimada e justificada; a análise teórica e a comparação final com Amdahl estão **pendentes**.

## 6. Baseline inicial: estatísticas das 15 medições

| N | Média (s) | Mediana (s) | Desvio-padrão amostral (s) |
|---:|---:|---:|---:|
| 100.000 | 0,039958 | 0,040211 | 0,001319 |
| 1.000.000 | 0,402359 | 0,384654 | 0,047630 |
| 5.000.000 | 2,192117 | 2,117201 | 0,272486 |

Esses números provêm do primeiro ensaio de baseline, **não** do baseline intercalado nos testes OpenMP. Não os misturar no mesmo cálculo de speedup.

## 7. OpenMP: estatísticas e comparação (60 medições)

Todas as linhas abaixo têm `K=8`, `IT=20` e **5 repetições por configuração**. O speedup usa o sequencial **da mesma campanha**.

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

**Resultado observado:** no maior N e com quatro threads, a média OpenMP foi `1,805006 s`, contra `2,243186 s` da versão sequencial: speedup aproximado de **1,243×** e eficiência **31,1%**. Isso não garante aceleração estável em todas as rodadas.

**Instabilidade relevante:** para `N=1.000.000`, OpenMP com 2 threads variou de **0,396783 s a 0,974336 s**; para `N=100.000`, OpenMP 4 variou de **0,048745 s a 0,190246 s**. Possíveis hipóteses: escalonamento, execução concorrente, ambiente WSL ou overhead; **nenhuma foi isolada experimentalmente**. São necessários retestes controlados e registro do hardware/carga.

## 8. Gráficos e procedimento de reprodução

Os nove gráficos originais estão em `resultados/graficos/`: três de tempo, três de speedup e três de eficiência, um de cada tipo para cada N. O CSV de resumo fica em `resultados/resumo_openmp.csv`. O código gerador é `scripts/gerar_graficos_openmp.py`.

Após a reorganização, a geração foi testada com sucesso, **sem sobrescrever os originais**:

```bash
python3 scripts/gerar_graficos_openmp.py \
  resultados/resultados_openmp.csv \
  resultados/graficos_teste
find resultados/graficos_teste -maxdepth 1 -type f | wc -l
# Saída observada: 10 (9 PNG + resumo_openmp.csv)
```

A execução reimprimiu as doze linhas de resumo e conservou os resultados anteriores. Ao reproduzir, prefira uma pasta distinta ou um nome versionado; rodar sem indicar o destino pode sobrescrever arquivos de gráficos existentes.

## 9. Verificação de corretude OpenMP

**Script:** `scripts/validar_openmp.sh` (usa `build/validacao_seq` e `build/validacao_omp`, gerados por `make validacao`). Compara as coordenadas de **cada um dos K=8 centroides** finais, impressas com `%.17g`, não apenas a soma do checksum.

**Casos:** N = 100.000, 1.000.000 e 5.000.000; K=8; IT=20; OpenMP com 1, 2 e 4 threads → **9 comparações**.

**Execução confirmada após a reorganização:**

```bash
make validacao
bash scripts/validar_openmp.sh
cat resultados/validacao_openmp.csv
```

Resultado relatado: **9/9 aprovados**, arquivos textuais dos centroides iguais ao baseline em todas as nove configurações; evidência gravada em `resultados/validacao_openmp.csv`.

| N | Checksum de referência | OpenMP 1 | OpenMP 2 | OpenMP 4 |
|---:|---:|:---:|:---:|:---:|
| 100.000 | 8090.3550 | aprovado | aprovado | aprovado |
| 1.000.000 | 8109.0037 | aprovado | aprovado | aprovado |
| 5.000.000 | 8099.9055 | aprovado | aprovado | aprovado |

A igualdade individual foi demonstrada **somente** para essas entradas e configurações. Os `validacao/omp_*.txt` e `validacao/referencia.txt` herdados da fase anterior representam uma última execução gravada, **não** nove registros permanentes separados; o CSV automatizado é o registro consolidado. Quando possível, ampliar a validação para outros valores de K e IT e registrar casos de borda válidos.

## 10. Situação real dos scripts após a reorganização

| Arquivo | Estado observado |
|---|---|
| `Makefile` | Compilou com sucesso baseline, OpenMP, perfilamento e dois validadores; versão MPI preparada como alvo, mas **sem fonte** |
| `scripts/medir_baseline.sh` | Caminhos corrigidos; `bash -n` passou; **não reexecutado integralmente** |
| `scripts/medir_openmp.sh` | Caminhos corrigidos; `bash -n` e teste de executáveis passaram; **não reexecutado integralmente** |
| `scripts/gerar_graficos_openmp.py` | Adaptado e **executado com sucesso**, gerando 9 PNG + CSV em pasta de teste |
| `scripts/validar_openmp.sh` | **Executado com sucesso**; 9/9 comparações aprovadas e CSV gerado |

Apenas passar em `bash -n` não prova que o script de medição completo executa corretamente. Os testes históricos permanecem válidos como registros, e os scripts atuais estão preparados para uma reprodução posterior.

## 11. Próximos experimentos obrigatórios

- **MPI:** implementar `mpi/10_kmeans.cpp`, validar resultados com diferentes processos e criar medições em CSV com repetição, checksum e comparações individuais dos centroides.
- **Comparabilidade:** identificar precisamente se o tempo MPI inclui `Scatterv`, `Bcast` ou outras etapas que o sequencial exclui; apresentar fases separadas ou justificar os limites da comparação.
- **Escalabilidade forte:** aprofundar a análise para N fixo variando número de threads/processos. OpenMP já possui curvas preliminares; MPI ainda não.
- **Escalabilidade fraca:** definir protocolo em que a carga por trabalhador permaneça aproximadamente constante e executar os testes. **Ainda não realizada.**
- **Lei de Amdahl:** estimar a fração sequencial/paralelizável com premissas explícitas, fazer previsão teórica e discutir a diferença para os resultados medidos. **Ainda não concluída.**
- **Qualidade das medições:** reduzir variação, registrar condições de execução e, se possível, repetir no ambiente Linux do laboratório.
- **Relatório/entrega:** integrar gráficos e conclusões à documentação, confirmar exigências do professor e manter `AUTORES.md` preenchido. O documento da disciplina exige PDF de até 6 páginas no **Marco 1**; para o **Marco 2**, exige principalmente repositório com código, CSV, gráficos e documentação, sem declarar um PDF final separado como obrigatório.

## 12. Regra para futuros colaboradores e IAs

Antes de atualizar qualquer número:

1. Abrir o CSV original e identificar a campanha experimental a que pertence.
2. Confirmar N, K, IT, variante, threads/processos, aquecimento e repetições.
3. Verificar o comando de compilação e o escopo temporal medido no código.
4. Calcular o speedup contra **o baseline sequencial da mesma campanha**.
5. Não confundir checksum com verificação individual dos centroides; anotar ambos quando disponíveis.
6. Preservar dados originais e publicar novos ensaios em CSVs separados.
7. Registrar a origem e as limitações dos dados; atualizar `docs/ESTADO_ATUAL.md` e `docs/PROXIMOS_PASSOS.md` quando uma etapa terminar.

**Relações com outros documentos:** `README.md` (execução); `AGENTS.md` (regras para IA); `docs/ARQUITETURA.md` (algoritmo e decisões); `docs/ESTADO_ATUAL.md` (situação executada); `docs/PROXIMOS_PASSOS.md` (fila de trabalho e handoff).
