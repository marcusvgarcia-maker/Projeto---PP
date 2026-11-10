# AGENTS.md — Contexto de continuidade para IAs e agentes de programação

> **Projeto:** Programação Paralela (CCO085), IESB, semestre 2026/2 — Problema 10, K-means (algoritmo de Lloyd).  
> **Estado registrado:** 09/11/2026, com base em execuções e saídas fornecidas no desenvolvimento local.  
> **Atenção:** este documento descreve principalmente a pasta **local reorganizada** `projeto_pp/`. **Não pressuponha que essa estrutura já esteja publicada na branch `main` do GitHub.** Verifique antes de agir.

## 1. Missão e regras obrigatórias

O grupo deve partir do **código sequencial fornecido pelo professor**, implementar versões em **OpenMP** (memória compartilhada) e **MPI** (memória distribuída), comprovar a corretude, medir tempo, speedup, eficiência e escalabilidade forte/fraca, e confrontar resultados com a Lei de Amdahl. A entrega inclui código das três versões, Makefile, scripts que produzam CSV, gráficos, README, `AUTORES.md` e histórico de commits distribuído entre os integrantes. A apresentação inclui demonstração ao vivo e arguição cruzada.

**Invariantes do baseline (não modificar):**

- Entradas de linha de comando `N`, `K`, `IT`, com padrões `1000000`, `8`, `20`.
- Geração determinística de pontos bidimensionais pelo gerador original com semente `2024ULL`.
- Inicialização dos centroides pelos primeiros `K` pontos.
- Distância euclidiana **ao quadrado**, sem raiz quadrada.
- Para empates, vence o primeiro centroide encontrado (`if (d < best)`).
- Número **fixo** de iterações `IT`, sem critério de convergência.
- Clusters vazios preservam seus centroides anteriores.
- A saída mantém `checksum` e tempo; o checksum de quatro casas decimais é **insuficiente, isoladamente, para comprovar a igualdade dos centroides**.
- A região cronometrada do baseline compreende o laço principal, **não** a geração dos pontos; explicitar possíveis diferenças de medição de outras versões.

Preserve `sequencial/10_kmeans.cpp` como referência. Não introduza mudanças na matemática, no gerador, na entrada ou na semântica numérica sem aprovação e uma análise explícita de corretude.

## 2. Ordem de leitura antes de trabalhar

1. Este arquivo (`AGENTS.md`) e `README.md`.
2. `docs/ESTADO_ATUAL.md`, `docs/PROXIMOS_PASSOS.md`, `docs/ARQUITETURA.md` e `docs/EXPERIMENTOS.md`.
3. Os **códigos reais**, o Makefile, os scripts e os arquivos CSV; prevalecem sobre descrições desatualizadas.
4. `docs/REORGANIZACAO.md` antes de mudanças no Git/GitHub.
5. Documento oficial do professor, quando disponível: `Projeto_Academico_PP_20262(1).pdf` (nome do arquivo fornecido na conversa; verificar se existe no workspace). Não presumir que foi copiado para o repositório.

**Aviso de documentação:** vários arquivos em `docs/` foram criados quando o trabalho ainda estava separado em branches. **Os caminhos e estados podem estar desatualizados**. Atualize esses documentos a partir da estrutura e das evidências atuais; não replique informações antigas sem verificar.

## 3. Estrutura local preparada

```text
projeto_pp/
├── README.md                 # nova versão preparada; confirmar se foi instalada
├── AGENTS.md                 # este arquivo, após substituição
├── AUTORES.md                # confirmar preenchimento dos nomes e funções reais
├── .gitignore
├── Makefile
├── sequencial/10_kmeans.cpp
├── perfilamento/10_kmeans.cpp
├── openmp/10_kmeans.cpp
├── mpi/                      # vazio; MPI ainda NÃO implementado
├── validacao/
│   ├── sequencial.cpp
│   ├── openmp.cpp
│   └── *.txt                  # registros antigos, não cobrem necessariamente os 9 cenários
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
│   └── graficos/             # 9 PNG originais
└── docs/
    ├── ESTADO_ATUAL.md
    ├── ARQUITETURA.md
    ├── EXPERIMENTOS.md
    ├── PROXIMOS_PASSOS.md
    └── REORGANIZACAO.md
```

`build/` é gerado por `make` e não deve ser enviado ao Git. Pode haver `resultados/graficos_teste/` (9 PNG + um CSV, gerados em teste de reprodutibilidade); isso não substitui os gráficos históricos.

## 4. Estado confirmado e evidências

| Frente | Estado | Evidência / ressalva |
|---|---|---|
| Baseline | **Compila e executa** | `make` gerou `build/10_kmeans_base`; entrada 1.000.000/8/20 produziu checksum `8109.0037` |
| Perfilamento | **Executado, análise preliminar** | Em medição N=1.000.000, K=8, IT=20: atribuição `0.304297 s` (`87.38%`); recálculo `0.043902 s` (`12.61%`) |
| Medições baseline | **Realizadas** | 3 tamanhos, 1 aquecimento descartado e 5 medidas por tamanho; `resultados/baseline.csv` |
| OpenMP | **Implementado** | `openmp/10_kmeans.cpp`, compilado via `make` |
| Validação OpenMP | **9/9 aprovados** | `bash scripts/validar_openmp.sh`; gerou `resultados/validacao_openmp.csv` |
| Experimentos OpenMP | **Realizados** | `resultados/resultados_openmp.csv`: 60 medições (baseline intercalado + OpenMP 1/2/4 threads; 3 tamanhos × 5 repetições) |
| Gráficos OpenMP | **Gerados e regenerados** | Nove PNG históricos em `resultados/graficos/`; teste de script gerou 9 PNG + 1 CSV em `resultados/graficos_teste/` |
| MPI | **Não implementado** | Diretório `mpi/` vazio; proposta de código em conversa não significa código salvo ou testado |
| Lei de Amdahl / escalabilidade / relatório final | **Pendentes ou parciais** | Estimativa justificada, comparação completa e testes forte/fraco ainda necessitam conclusão |
| Publicação da reorganização | **Não confirmada** | GitHub e pasta local precisam ser sincronizados com revisão |

**Como funciona o OpenMP atual:** a fase de atribuição usa `#pragma omp parallel for schedule(static)`. O recálculo usa somas e contagens privadas por thread, depois combinação serial por cluster, evitando múltiplas threads escreverem simultaneamente no mesmo acumulador. Há barreira ao fim da região `parallel`. Não afirmar que `critical`, `atomic` ou `reduction` do OpenMP foram usadas literalmente: a redução é **manual**, por acumuladores locais. Considerar false sharing e overhead como hipóteses de investigação, não causas comprovadas.

**Corretude verificada:** entradas `N=100000`, `1000000`, `5000000`, sempre `K=8` e `IT=20`, com 1, 2 e 4 threads. Em cada caso, as oito linhas de coordenadas finais (`%.17g`) coincidiram com o baseline. Checksum de referência por N: `8090.3550`, `8109.0037`, `8099.9055`. Ainda faltam casos adicionais (outros valores de K/IT e clusters vazios).

**Desempenho:** no experimento de 60 medições, para `N=5000000`, 4 threads, média sequencial `2.2431864 s` e média OpenMP `1.8050062 s`: speedup **~1.243×** e eficiência **~31.1%**. A variabilidade foi elevada; **não declarar ganho estável nem atribuir causalidade sem testes controlados**. A referência correta para speedup é o baseline sequencial, não OpenMP com uma thread.

## 5. Ambiente e comandos confirmados

- Windows 11 + VS Code + Ubuntu em WSL2, terminal Linux dentro do VS Code.
- G++ Ubuntu 15.2.0; OpenMP via `-fopenmp`; `nproc` indicou 4 unidades de processamento disponíveis.
- OpenMPI foi instalado e um teste funcional `mpirun --oversubscribe -np 4 /bin/echo MPI_OK` produziu 4 linhas. Isso **não valida** ainda uma implementação K-means MPI. Investigar problema de slots sem `--oversubscribe` antes de métricas confiáveis.
- Pasta local: `C:\Users\Thinkpad\Documents\Programas (criacao)\ProgParal\projeto_pp` (no WSL: `/mnt/c/Users/Thinkpad/Documents/Programas (criacao)/ProgParal/projeto_pp`). Use caminhos relativos nos scripts; não fixe esse caminho pessoal no código.

Na raiz do projeto:

```bash
make
./build/10_kmeans_base 1000000 8 20
OMP_NUM_THREADS=4 OMP_DYNAMIC=FALSE ./build/10_kmeans_omp 1000000 8 20
make validacao
bash scripts/validar_openmp.sh
python3 scripts/gerar_graficos_openmp.py resultados/resultados_openmp.csv resultados/graficos_teste
```

O alvo padrão `make` compilou: `10_kmeans_base`, `10_kmeans_omp`, `10_kmeans_perfil`, `validacao_seq` e `validacao_omp`. O alvo `make mpi` está **preparado mas não funciona até existir `mpi/10_kmeans.cpp`**.

Os scripts `scripts/medir_baseline.sh` e `scripts/medir_openmp.sh` foram ajustados para usar `build/` e passaram em `bash -n`, mas **a execução completa dos scripts reorganizados ainda não foi demonstrada**. Para preservar os dados originais, seus destinos são `resultados/baseline_reteste.csv` e `resultados/resultados_openmp_reteste.csv`.

## 6. Regras de trabalho para futuras IAs

1. **Verificar antes de alterar:** `pwd`, `ls`, `git status`, branch, arquivos e scripts presentes; não assumir que o layout do GitHub é igual ao local.
2. **Trabalhar em incrementos pequenos**, com objetivo, arquivos afetados, comando de teste e resultado esperado. Respeitar quando o usuário pedir uma etapa por vez.
3. **Não sobrescrever dados históricos:** CSVs de medidas, gráficos, fontes originais e relatórios devem permanecer rastreáveis. Saídas de reteste devem usar outro nome/diretório e indicar ambiente e data.
4. **Não inventar conclusões:** distinguir *planejado*, *implementado*, *compilado*, *testado* e *validado*. Saída de `bash -n` prova sintaxe, não correção de comportamento.
5. **Validação > checksum:** comparar centroides individualmente; acrescentar entradas e testes com K/IT diferentes quando pertinente. Documentar diferenças numéricas justificadas se um futuro MPI mudar a ordem das somas.
6. **Medição justa:** manter `-O2`, conjunto de entradas, aquecimento/repetições, configurações do sistema e a referência sequencial. Informar se MPI inclui distribuição inicial dos pontos e se o benchmark parte de um processador distinto.
7. **Git com segurança:** evitar sobrescrever mudanças não commitadas; não fazer `push --force`; preservar branches históricas e confirmar integração com a equipe.
8. **Atualizar documentação após cada tarefa:** pelo menos `docs/ESTADO_ATUAL.md` e `docs/PROXIMOS_PASSOS.md`, e `docs/EXPERIMENTOS.md` quando houver medições novas. `README.md` deve descrever caminhos e comandos reais.
9. **Não preencher `AUTORES.md` com nomes ou papéis presumidos**: solicitar/confirmar os três integrantes e a divisão formal.
10. **Não registrar senhas, tokens ou dados pessoais sensíveis** nos arquivos versionados.

## 7. Próximos passos (ordem recomendada)

1. Confirmar substituição do `README.md` local e instalar este `AGENTS.md`; revisar caminhos desatualizados nos documentos de `docs/`.
2. Revisar o `.gitignore`, garantir que `build/` e temporários estejam ignorados, sem ignorar CSVs/gráficos que são evidência de entrega.
3. Conferir e registrar evidências da validação OpenMP; ampliar testes se necessário.
4. Implementar MPI a partir do **baseline**, começando por decomposição dos pontos, comunicação coletiva e validação; não alegar conclusão antes de compilar e executar.
5. Medir MPI com protocolos comparáveis, completar análise de speedup/eficiência, escalabilidade forte/fraca, Amdahl e discussão de overhead.
6. Consolidar a pasta local no GitHub com revisão cuidadosa: `main`, `baseline_perfilamento` e `openmp` não devem ser fundidas automaticamente. Em uma verificação de 09/11/2026, `main` não tinha ancestral comum com as branches de desenvolvimento; usar integração seletiva e branch nova.
7. Preparar `AUTORES.md`, documentação final, Makefile que compile as três versões, demonstração ao vivo e arguição cruzada.

**Prazos do documento do professor:** Marco 2 em **12/11/2026**; apresentações em **19 e 26/11/2026**. Priorizar o funcionamento e a corretude da versão MPI, a entrega reproduzível e a comunicação clara das limitações.

## 8. Protocolo de passagem de trabalho (*handoff*)

Ao interromper ou concluir uma sessão, adicionar um registro datado em `docs/PROXIMOS_PASSOS.md` ou documento de handoff contendo:

```markdown
### Handoff — AAAA-MM-DD HH:MM (fuso)
- Branch e commit atual: (se houver)
- Tarefa em andamento:
- Arquivos modificados:
- Mudanças efetuadas:
- Comandos realmente executados:
- Resultados observados / arquivos de evidência:
- Testes ainda não executados:
- Erros ou bloqueadores:
- Próxima ação exata:
- Restrições / cuidados:
```

Nunca escrever "feito" com base apenas em um plano, um arquivo rascunhado ou uma instrução fornecida ao usuário. Registrar a diferença entre o que a IA preparou e o que foi efetivamente executado na máquina do usuário.
