# Estado atual do projeto — Programação Paralela / K-means

> **Data de referência:** 09/11/2026 (horário de Brasília).  
> **Disciplina:** CCO085 — Programação Paralela, IESB, 2026/2.  
> **Problema:** nº 10, agrupamento por k-médias (*K-means*, algoritmo de Lloyd).  
> **Pasta de trabalho local:** `projeto_pp/` — Windows 11, VS Code e Ubuntu pelo WSL2.  
> **Repositório remoto:** https://github.com/marcusvgarcia-maker/Projeto---PP  
> **Regra de leitura:** este documento registra **resultados relatados e confirmados por saídas de terminal nesta colaboração**. Não significa que tudo já tenha sido publicado na branch `main` do GitHub. Confirme o estado real dos arquivos e do Git antes de modificá-los.

## 1. Objetivo, condições e entrega

O grupo deve manter a implementação sequencial fornecida pelo professor como referência de comportamento e desenvolver as versões paralelas **OpenMP** e **MPI**, validando os resultados e avaliando tempo, *speedup*, eficiência, escalabilidade forte e fraca, com discussão da Lei de Amdahl e dos custos reais da paralelização.

A entrega do **Marco 2 está prevista para 12/11/2026**. O documento do professor exige um repositório Git com as três implementações em diretórios separados, um `Makefile`, um script gerador de CSV, gráficos, um `README.md` e um `AUTORES.md`, além da análise experimental. As apresentações estão previstas para 19 e 26/11/2026. **Não há exigência explícita de um PDF final separado para o Marco 2**; o Marco 1 exigia um PDF com até seis páginas. A documentação técnica adicional é útil, mas não substitui os artefatos obrigatórios.

### Restrições do baseline

- Entrada: `N`, `K`, `IT` (padrões de 1.000.000, 8 e 20).
- Pontos bidimensionais gerados deterministicamente, com semente `2024ULL` e o gerador original.
- Centroides iniciais: primeiros `K` pontos.
- Atribuição pelo quadrado da distância euclidiana; desempate pelo primeiro centroide (`d < best`).
- Exatamente `IT` iterações, sem parada antecipada por convergência.
- Se um cluster fica vazio, seu centroide não é atualizado.
- O cronômetro do baseline cobre as **iterações**, excluindo a geração inicial dos pontos.
- **Não modificar a lógica do código sequencial de referência.** O checksum de quatro casas decimais não é prova suficiente de corretude; comparar também os centroides.

## 2. Resumo de status

| Área | Estado em 09/11/2026 | Evidência e ressalvas |
|---|---|---|
| Baseline sequencial | **Concluído no escopo testado** | Compila com `make`, executa e produz `checksum=8109.0037` para `N=1000000 K=8 IT=20` |
| Perfilamento | **Realizado; interpretação preliminar** | Uma medição mostrou atribuição 87,38% e recálculo 12,61%; repetir/aperfeiçoar se houver tempo |
| Medições do baseline | **Realizadas** | 15 medições originais: três N × cinco repetições; CSV preservado |
| OpenMP | **Implementado e compilado** | Atribuição paralela e recálculo com acumuladores privados por thread |
| Validação OpenMP | **Aprovada (9/9)** | `scripts/validar_openmp.sh` executado após reorganização; `resultados/validacao_openmp.csv` registrado |
| Medições OpenMP | **Realizadas** | 60 medições originais, com 1, 2 e 4 threads e baseline intercalado |
| Gráficos OpenMP | **Gerados e regeneração testada** | Nove PNGs originais preservados; teste produziu 9 PNGs + resumo CSV em `resultados/graficos_teste/` |
| Scripts de medição reorganizados | **Sintaxe verificada; execução completa pendente** | `bash -n` passou para os dois scripts; não afirmar que os retestes foram executados |
| `Makefile` | **Criado e testado** | `make` compilou cinco executáveis; baseline e OpenMP executados com sucesso |
| Documentação para IA | **Em atualização** | `AGENTS.md` atualizado e verificado; README revisado foi preparado, mas a substituição ainda não foi explicitamente confirmada nesta conversa |
| `AUTORES.md` | **Pendente de conferência/preenchimento** | Confirmar integrantes e papéis técnicos reais |
| MPI | **Não implementado na pasta local confirmada** | Diretório `mpi/` estava vazio na última árvore apresentada; código sugerido em conversa não equivale a implementação salva/testada |
| Escalabilidade forte/fraca e Amdahl | **Pendentes de conclusão formal** | Não confundir perfilamento com estimativa completa da fração paralelizável |
| Publicação da nova organização | **Não confirmada** | Nenhuma integração ao GitHub foi comprovada após a reorganização local |

## 3. Estrutura local de referência

A estrutura abaixo resulta da listagem do Explorador/terminal apresentada pelo desenvolvedor **mais alterações cuja execução foi confirmada posteriormente**. Alguns nomes de documentos devem ser conferidos no disco antes de assumir que foram substituídos.

```text
projeto_pp/
├── .gitignore
├── AGENTS.md                 # atualizado e confirmado por head/grep
├── README.md                 # versão nova preparada; confirmar substituição
├── AUTORES.md                # confirmar renomeação e preenchimento
├── Makefile                  # criado e testado
├── sequencial/
│   └── 10_kmeans.cpp
├── perfilamento/
│   └── 10_kmeans.cpp
├── openmp/
│   └── 10_kmeans.cpp
├── mpi/                      # ainda vazio
├── validacao/
│   ├── sequencial.cpp
│   ├── openmp.cpp
│   └── *.txt                 # saídas antigas, podem ter sido sobrescritas
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
│   ├── graficos/             # nove PNG originais
├── build/                    # executáveis gerados por make; não versionar
└── docs/
    ├── ARQUITETURA.md
    ├── ESTADO_ATUAL.md        # este documento, após substituição
    ├── EXPERIMENTOS.md
    ├── PROXIMOS_PASSOS.md
    └── REORGANIZACAO.md
```

**Organização local confirmada em 09/11/2026:** os arquivos `README_PROPOSTO.md` e `AUTORES_MODELO.md` foram substituídos por `README.md` e `AUTORES.md`, respectivamente. O documento de autores contém os nomes, matrículas e responsabilidades dos três integrantes.

A auditoria local confirmou a presença dos 14 arquivos essenciais verificados. Os documentos antigos foram retirados da estrutura principal, e os gráficos de teste foram separados dos resultados oficiais.

A organização local está concluída, mas ainda não foi integrada à branch `main` do GitHub. A implementação MPI também permanece pendente.

## 4. Ambiente e compilação confirmados

- Host Windows 11 com VS Code, terminal Ubuntu via WSL2.
- `g++ (Ubuntu 15.2.0-16ubuntu1) 15.2.0` e OpenMPI instalados.
- `nproc` retornou `4`.
- `mpirun --oversubscribe -np 4 /bin/echo MPI_OK` produziu quatro linhas `MPI_OK`.
- `mpirun` **sem** `--oversubscribe` apresentou erro de alocação de slots; houve também falhas ao localizar arquivos de ajuda PRRTE/PMIx. Investigar antes dos experimentos de desempenho MPI. Não tratar `--oversubscribe` como configuração ideal de benchmark.
- O código está em `/mnt/c/.../projeto_pp` (sistema de arquivos do Windows acessado pelo WSL), o que deve ser registrado nas condições experimentais.

`make` produziu, sem erros, estes cinco arquivos:

```text
build/10_kmeans_base
build/10_kmeans_omp
build/10_kmeans_perfil
build/validacao_seq
build/validacao_omp
```

O alvo `mpi` foi preparado no Makefile, mas **não integra o alvo padrão `all` enquanto o fonte MPI não existir**.

Testes feitos após a reorganização, para `N=1000000 K=8 IT=20`:

| Executável | Configuração | Tempo observado | Checksum |
|---|---|---:|---:|
| Sequencial | execução 1 | 0,390819 s | 8109.0037 |
| Sequencial | execução 2 | 0,372863 s | 8109.0037 |
| OpenMP | 1 thread | 0,598412 s | 8109.0037 |
| OpenMP | 2 threads | 0,399357 s | 8109.0037 |
| OpenMP | 4 threads | 0,408286 s | 8109.0037 |

Essas execuções são **testes funcionais isolados**, não novos resultados estatísticos finais.

## 5. Perfilamento, medições e interpretação

### Perfilamento original

Entrada `N=1000000 K=8 IT=20`:

| Fase | Tempo | Parcela observada |
|---|---:|---:|
| Atribuição | 0,304297 s | 87,38% |
| Recálculo | 0,043902 s | 12,61% |
| Tempo total reportado | 0,348253 s | 100% (aprox.) |

A atribuição foi o maior *hotspot* **nessa execução**. As duas fases podem ser paralelizadas, mas o recálculo exige redução/sincronização; iterações consecutivas são dependentes porque os novos centroides alimentam a próxima atribuição. A proporção do hotspot **não deve ser automaticamente tratada como a fração paralelizável exata para Amdahl**.

### Experimentos OpenMP originais

Protocolo: N = 100.000, 1.000.000 e 5.000.000; K = 8; IT = 20; um aquecimento descartado por configuração e cinco execuções medidas; sequencial intercalado com OpenMP 1, 2 e 4 threads.

| N | Sequencial médio | OMP 1 médio | OMP 2 médio | OMP 4 médio |
|---:|---:|---:|---:|---:|
| 100.000 | 0,050713 s | 0,051308 s | 0,075015 s | 0,101940 s |
| 1.000.000 | 0,527968 s | 0,464654 s | 0,638230 s | 0,539434 s |
| 5.000.000 | 2,243186 s | 2,297215 s | 2,107286 s | 1,805006 s |

Para N = 5.000.000 e quatro threads, *speedup* com base na média sequencial foi aproximadamente **1,243×**, com eficiência **31,1%**. O ganho é observado nessa amostra; outras configurações foram instáveis e há variações expressivas entre repetições. Não alegar que uma causa específica do ruído foi demonstrada.

Arquivos de evidência: `resultados/resultados_openmp.csv` (60 linhas de dados), `resultados/resumo_openmp.csv` e nove PNGs em `resultados/graficos/`. O gerador adaptado `scripts/gerar_graficos_openmp.py` foi executado na nova estrutura e produziu 10 arquivos em `resultados/graficos_teste/` (9 PNG + `resumo_openmp.csv`), preservando os originais.

### Scripts de medição

- `scripts/medir_baseline.sh`: alterado para localizar `build/10_kmeans_base` e produzir `resultados/baseline_reteste.csv`. **`bash -n`: aprovado; reteste completo não executado.**
- `scripts/medir_openmp.sh`: alterado para localizar executáveis em `build/` e produzir `resultados/resultados_openmp_reteste.csv`. **`bash -n`: aprovado; reteste completo não executado.**
- `scripts/gerar_graficos_openmp.py`: adaptado para CSV padrão em `resultados/resultados_openmp.csv` e saída opcional; **execução de teste aprovada**.

Os arquivos originais (`baseline.csv`, `resultados_openmp.csv` e nove PNG) não devem ser sobrescritos sem cópia e justificativa.

## 6. Implementação e validação OpenMP

A implementação atual realiza:

1. Atribuição com `#pragma omp parallel for schedule(static)`; cada thread escreve o rótulo dos pontos que processa.
2. Recálculo em acumuladores privados por thread (`sx_local`, `sy_local`, `cnt_local`) para evitar condições de corrida.
3. Combinação sequencial das somas e contagens e atualização dos centroides antes da próxima iteração.

Após a reorganização, foi criado e **executado** `scripts/validar_openmp.sh`. Ele usa os executáveis instrumentados `build/validacao_seq` e `build/validacao_omp`, compara as coordenadas finais dos centroides impressas com 17 algarismos significativos e grava `resultados/validacao_openmp.csv`.

**Resultado confirmado: 9/9 testes aprovados** — para cada N = 100.000, 1.000.000 e 5.000.000, com 1, 2 e 4 threads; sempre K = 8 e IT = 20.

Esta evidência cobre **as configurações testadas**, não uma prova universal para todas as entradas. Os `.txt` legados da pasta `validacao/` não devem ser apresentados como registro separado de todos os nove testes, pois foram sobrescritos nos procedimentos manuais anteriores.

## 7. GitHub: situação e cautelas

O repositório remoto foi consultado antes da reorganização local. Foram identificadas as branches `main`, `baseline_perfilamento` e `openmp`. A `main` ainda tinha o baseline e um README genérico, enquanto códigos, dados e gráficos de desenvolvimento estavam nas outras branches. Comparações de `main` com as branches de desenvolvimento retornaram ausência de ancestral comum; portanto, **evitar merge automático entre essas histórias**.

Uma tentativa de criar branch pelo conector GitHub foi recusada com `403 Resource not accessible by integration`. **Não foi realizada publicação pelo assistente.** O trabalho de organização e os testes acima foram executados **localmente** pelo desenvolvedor. Antes de publicar, verificar `git status`, branch atual, arquivos ignorados, regras de `.gitignore` e mudanças não confirmadas; preparar integração seletiva em branch nova e revisão cuidadosa.

## 8. Prioridades restantes (ordem sugerida)

1. **Conferir os arquivos locais e documentação**: nome do `README.md`, preenchimento de `AUTORES.md`, atualizações de `docs/`, `.gitignore` e scripts.
2. **MPI obrigatório**: implementar `mpi/10_kmeans.cpp`, compilar e validar com 1, 2, 4 processos; tratar distribuição, comunicação coletiva, decomposição e sincronização. Registrar diferenças entre tempo MPI e tempo sequencial.
3. **Experimentos MPI**: medir, gerar CSV, tempo, *speedup*, eficiência; investigar problema de slots no WSL sem mascarar medições com oversubscription.
4. **Análise completa**: escalabilidade forte e fraca para ambas as tecnologias, estimativa justificada de Amdahl, discussão de overhead, sincronização e variabilidade.
5. **Entrega reproduzível**: incluir MPI em `make all`, validar scripts em ambiente limpo, confirmar gráficos, preencher `AUTORES.md`, organizar commits e revisar README.
6. **Publicação e apresentação**: incorporar organização ao GitHub sem perder as branches anteriores, testar em Linux do laboratório e preparar demonstração ao vivo e arguição cruzada.

## 9. Comandos atuais para retomada

Na raiz `projeto_pp/`, usando terminal Ubuntu:

```bash
make
./build/10_kmeans_base 1000000 8 20
OMP_NUM_THREADS=4 OMP_DYNAMIC=FALSE ./build/10_kmeans_omp 1000000 8 20
bash scripts/validar_openmp.sh
python3 scripts/gerar_graficos_openmp.py resultados/resultados_openmp.csv resultados/graficos_teste
```

Para inspecionar os testes de corretude:

```bash
cat resultados/validacao_openmp.csv
```

Para inspecionar a situação do Git, sem alterá-la:

```bash
git status --short --branch
git branch -avv
```

## 10. Handoff — encerramento da etapa de validação/documentação

- **Estado comprovado:** Makefile compilou cinco alvos; baseline e OpenMP executaram; nove comparações automáticas de centroides passaram; gerador de gráficos adaptado produziu 10 arquivos de teste; `AGENTS.md` atualizado e verificado.
- **Atualização de documentação em andamento:** este arquivo (`docs/ESTADO_ATUAL.md`) foi preparado como substituto. A substituição deve ser confirmada no ambiente local. Revisar posteriormente `docs/ARQUITETURA.md`, `docs/EXPERIMENTOS.md`, `docs/PROXIMOS_PASSOS.md`.
- **Não confirmado:** substituição final do README, cadastro real dos autores, execução completa dos scripts de medição adaptados, sincronização com GitHub.
- **Tarefa imediata:** copiar este arquivo para `docs/ESTADO_ATUAL.md` e conferir seu cabeçalho; em seguida, atualizar `docs/PROXIMOS_PASSOS.md` e demais documentos sem inventar tarefas concluídas.
- **Próxima frente técnica principal:** MPI, ainda não salvo/testado na pasta local confirmada.
