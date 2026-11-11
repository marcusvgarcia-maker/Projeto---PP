# AGENTS.md — Contexto de continuidade para IAs e agentes de programação

> **Atualizacao operacional de 11/11/2026:** o PR #19 foi integrado a main em d9fb659. O usuario trabalha na branch local entrega/finalizacao, commit 852af1d, com Dockerfile e Compose registrados e arvore limpa no ultimo retorno. Docker validado: G++ 13.3.0, Open MPI 4.1.6, Ubuntu 24.04.5 LTS; OpenMP 9/9 e MPI 33/33 centroides aprovados. O pacote da campanha conjunta foi preparado para execucao pelo usuario. Esses resultados de desempenho ainda nao foram coletados. Priorize este registro e docs/ROTEIRO_CAMPANHA_DOCKER.md sobre os estados Git antigos abaixo.


> **Projeto:** Programação Paralela (CCO085), IESB, semestre 2026/2 — Problema 10, K-means (algoritmo de Lloyd).
>
> **Estado confirmado:** 10/11/2026, a partir das saídas de terminal fornecidas pelo usuário.
>
> **Atenção ao Git:** o desenvolvimento MPI está na branch **local** `desenvolvimento/mpi`, no clone Ubuntu `~/projeto_pp_integracao`. Ela deriva de `organizacao/kmeans` (commit-base `22d9583`). O Pull Request [#18](https://github.com/marcusvgarcia-maker/Projeto---PP/pull/18) publica a reorganização para `main`; está aberto, pronto para revisão, com solicitações para `joaovictorc1` e `Jpezildo` no último estado confirmado. **A branch MPI ainda não foi publicada nem mesclada.** Verifique os estados novamente antes de operações Git.

## 1. Missão e invariantes do baseline

O grupo deve manter o sequencial fornecido pelo professor, produzir as versões OpenMP e MPI, validar a corretude e estudar tempo, speedup, eficiência, escalabilidade forte/fraca e Lei de Amdahl. A entrega envolve fontes, Makefile, scripts reprodutíveis, CSVs, gráficos, README, `AUTORES.md`, histórico de contribuições e demonstração/arguição cruzada.

**Não alterar as regras matemáticas do baseline `sequencial/10_kmeans.cpp`:**

- Argumentos `N`, `K`, `IT`; padrões `1000000`, `8`, `20`.
- Pontos 2D gerados em sequência pelo LCG original, semente `2024ULL`.
- Centroides iniciais iguais aos primeiros `K` pontos.
- Distância euclidiana ao quadrado, sem raiz; empate favorece o primeiro índice (`d < best`).
- Exatamente `IT` iterações; clusters vazios conservam o centroide anterior.
- A saída normal informa `checksum` com quatro casas e `tempo` em segundos. Um checksum igual não comprova, isoladamente, a igualdade de todos os centroides.
- O cronômetro sequencial envolve as iterações, não a geração dos pontos.

Manter o baseline como referência imutável; quaisquer alterações exigem justificativa e nova validação.

## 2. Onde trabalhar e o que ler primeiro

**Clone Git correto:** `/home/thinkpad/projeto_pp_integracao` (`~/projeto_pp_integracao`).

**Cópia original no Windows:** `/mnt/c/Users/Thinkpad/Documents/Programas (criacao)/ProgParal/projeto_pp`. Ela não possui `.git` próprio e herda um repositório superior ligado a `joaovictorc1/Programacao-Paralela`. **Não fazer commits nem pushes nessa pasta acreditando estar no repositório `marcusvgarcia-maker/Projeto---PP`.**

Antes de agir:

```bash
cd ~/projeto_pp_integracao
pwd
git status -sb
git remote -v
```

Ordem de leitura: `AGENTS.md`, `README.md`, `docs/ESTADO_ATUAL.md`, `docs/PROXIMOS_PASSOS.md`, `docs/ARQUITETURA.md`, `docs/EXPERIMENTOS.md` e fontes/scripts/CSVs. Consultar `docs/REORGANIZACAO.md` antes de qualquer operação Git. O documento oficial do professor é `Projeto_Academico_PP_20262(1).pdf`, disponibilizado na conversa; não presumir que está no repositório.

**Nota:** os documentos de `docs/` anteriores à fase MPI podem conter frases desatualizadas (como “MPI não implementado”). Considerar o código, os resultados gerados e as últimas execuções como evidência; atualizar os documentos com cuidado.

## 3. Organização dos arquivos

```text
projeto_pp_integracao/
├── .gitattributes, .gitignore, Makefile
├── README.md, AGENTS.md, AUTORES.md
├── sequencial/10_kmeans.cpp
├── perfilamento/10_kmeans.cpp
├── openmp/10_kmeans.cpp
├── mpi/10_kmeans.cpp
├── validacao/sequencial.cpp, validacao/openmp.cpp, validacao/*.txt
├── scripts/
│   ├── medir_baseline.sh, medir_openmp.sh, validar_openmp.sh
│   ├── gerar_graficos_openmp.py
│   ├── validar_mpi.sh, validar_centroides_mpi.py
│   ├── medir_mpi.sh, analisar_mpi.py, gerar_graficos_mpi.py
│   ├── comparar_openmp_mpi.py
│   └── medir_escalabilidade_fraca_mpi.sh, analisar_escalabilidade_fraca_mpi.py
├── resultados/
│   ├── baseline.csv, resultados_openmp.csv, resumo_openmp.csv, validacao_openmp.csv
│   ├── resultados_mpi.csv, resumo_mpi.csv
│   ├── validacao_mpi.csv, validacao_centroides_mpi.csv
│   ├── escalabilidade_fraca_mpi.csv, resumo_escalabilidade_fraca_mpi.csv
│   ├── comparacao_openmp_mpi.csv
│   ├── graficos/                 # 9 PNG OpenMP históricos
│   ├── graficos_mpi/             # 9 PNG forte + 1 PNG fraca
│   └── graficos_comparacao/      # 9 PNG comparativos
├── docs/
│   ├── ARQUITETURA.md, ESTADO_ATUAL.md, EXPERIMENTOS.md
│   ├── PROXIMOS_PASSOS.md, REORGANIZACAO.md
│   └── ...
└── build/                        # gerado por make; ignorado pelo Git
```

Os arquivos MPI e dados novos estavam **não rastreados** no último `git status`; a árvore acima descreve o conteúdo local, **não** uma publicação remota. A pasta `build/` não deve ser versionada. Preservar os CSVs/PNGs originais; retestes devem usar arquivos distintos.

## 4. Estado confirmado e evidências

| Frente | Evidência registrada | Estado |
|---|---|---|
| Sequencial | `make` compila `build/10_kmeans_base`; checksums conhecidos para N=100 mil, 1 milhão e 5 milhões | Funcional |
| Perfilamento | Para N=1 milhão/K=8/IT=20, atribuição `0.304297 s` (87,38%) e recálculo `0.043902 s` (12,61%), em uma execução | Preliminar |
| OpenMP | `openmp/10_kmeans.cpp`, 9/9 comparações de centroides aprovadas em 1/2/4 threads | Implementado e validado nos casos ensaiados |
| Forte OpenMP | `resultados/resultados_openmp.csv`: 60 medições; `resumo_openmp.csv`; 9 PNG em `graficos/` | Registrada |
| MPI | `mpi/10_kmeans.cpp` compilado com `mpic++`; `make clean && make` gerou os seis executáveis esperados | Implementado e compilado |
| Checksum MPI | `scripts/validar_mpi.sh` passou em 9/9 casos padrão; houve ainda 9 casos de N não divisível e 15 casos variados, totalizando 33/33 testes de checksum | Aprovado nos casos ensaiados |
| Centroides MPI | `scripts/validar_centroides_mpi.py`, `resultados/validacao_centroides_mpi.csv`: **33/33** aprovações para P=1/2/4, vários N/K/IT; maior erro absoluto observado **0.0** (coordenadas impressas com 17 dígitos significativos) | Aprovado nos casos ensaiados |
| Forte MPI | `resultados/resultados_mpi.csv` (60 medições), `resumo_mpi.csv` (12 configurações), `graficos_mpi/` (9 gráficos fortes) | Registrada |
| Comparação OpenMP × MPI | `comparacao_openmp_mpi.csv` (18 linhas de dados) e `graficos_comparacao/` (9 PNG) | **Preliminar**; campanhas e baselines distintos |
| Fraca MPI | `escalabilidade_fraca_mpi.csv` (15 medições), `resumo_escalabilidade_fraca_mpi.csv` e `graficos_mpi/escalabilidade_fraca_mpi.png` | Registrada |
| Amdahl / relatório final | Há perfilamento inicial; falta confrontar previsão e dados, complementar descrição do ambiente e preparar entrega final | **Pendente** |
| GitHub | PR #18 mesclado à `main` em 10/11/2026; três commits MPI na branch local `desenvolvimento/mpi` | **Publicação e PR MPI pendentes** |

**Números úteis:** checksums `8090.3550` (N=100 mil), `8109.0037` (N=1 milhão) e `8099.9055` (N=5 milhões), para K=8/IT=20. O OpenMP alcançou speedup médio de aproximadamente `1,243x` com 4 threads e N=5 milhões na campanha histórica. O MPI teve, para esse N, tempo sequencial médio `2.341218 s` e MPI-4 médio `1.469368 s`, speedup `1,593x` e eficiência `39,8%` dentro de **sua própria campanha**.

**Escalabilidade fraca MPI:** com `N_por_processo=1.000.000`, `K=8`, `IT=20`, cinco repetições: P=1 média `0.670650 s` (100%), P=2 `0.814082 s` (82,4%), P=4 `1.661666 s` (40,4%). Desvios-padrão respectivos `0.243925`, `0.120106` e `0.191052 s`; variabilidade considerável.

**Cuidado metodológico:** OpenMP e MPI foram medidos em **campanhas distintas**, com diferentes tempos do sequencial. Não comparar os speedups como se partilhassem a mesma referência experimental nem atribuir as diferenças à tecnologia sem um benchmark conjunto controlado. O MPI mede somente as iterações (incluindo coletivas); exclui geração, `MPI_Bcast` inicial e `MPI_Scatterv` inicial. O tempo reportado é o máximo dos tempos locais, via `MPI_Reduce` com `MPI_MAX`. `--oversubscribe` foi usado nos testes, devendo ser declarado. Ainda não houve comprovação de funcionamento no laboratório.

## 5. Arquitetura técnica

**OpenMP:** atribuição com `#pragma omp parallel for schedule(static)`; somas e contagens por thread, combinadas posteriormente em um laço serial por cluster. A redução é manual, sem `critical` ou `atomic` no trecho utilizado.

**MPI:** rank 0 gera a mesma entrada LCG do sequencial; `MPI_Bcast` difunde centroides iniciais; duas chamadas de `MPI_Scatterv` distribuem coordenadas X e Y por blocos contíguos; cada processo atribui os pontos e calcula somas/contagens; dois `MPI_Allreduce` agregam coordenadas e contagens; todos atualizam centroides; rank 0 imprime a saída. Suporta N não divisível por P e P maior que N nos casos válidos testados. Opção adicional `--centroides` imprime coordenadas com `%.17g` sem alterar a saída padrão.

Compilação `-O2 -std=c++17`, com `-fopenmp` para OpenMP e `mpic++` para MPI. `make` padrão compila **seis** executáveis: `10_kmeans_base`, `10_kmeans_omp`, `10_kmeans_perfil`, `validacao_seq`, `validacao_omp`, `10_kmeans_mpi`.

## 6. Comandos úteis (na raiz do clone Ubuntu)

```bash
make clean && make
bash scripts/validar_openmp.sh
bash scripts/validar_mpi.sh
python3 scripts/validar_centroides_mpi.py

./build/10_kmeans_base 1000000 8 20
OMP_NUM_THREADS=4 OMP_DYNAMIC=FALSE ./build/10_kmeans_omp 1000000 8 20
mpirun --oversubscribe -np 4 ./build/10_kmeans_mpi 1000000 8 20
mpirun --oversubscribe -np 4 ./build/10_kmeans_mpi 19 3 5 --centroides

# Geração/análise a partir dos dados já existentes (não refaz benchmark):
python3 scripts/analisar_mpi.py
python3 scripts/gerar_graficos_mpi.py
python3 scripts/comparar_openmp_mpi.py
python3 scripts/analisar_escalabilidade_fraca_mpi.py
```

Para **repetir** medições (custosas e sujeitas a variação): `bash scripts/medir_mpi.sh` e `bash scripts/medir_escalabilidade_fraca_mpi.sh`. Atenção: esses scripts escrevem em `resultados/resultados_mpi.csv` e `resultados/escalabilidade_fraca_mpi.csv`, **sobrescrevendo as campanhas existentes**; antes de reproduzir, salve uma cópia ou altere o destino com um nome de reteste. As rotinas `medir_baseline.sh` e `medir_openmp.sh` escrevem em arquivos `_reteste.csv`; não foram reexecutadas integralmente após a reorganização.

## 7. Regras para futuras IAs e colaboradores

1. **Verificar repositório, branch e arquivos antes de alterar.** Evitar inadvertidamente o repositório-pai da pasta no Windows.
2. **Trabalhar incrementalmente.** Uma alteração por vez, comandos reproduzíveis, saída observada e próximo passo; distinguir intenção, implementação, compilação, teste e publicação.
3. **Preservar dados originais e autoria.** Nunca substituir CSVs/PNGs históricos silenciosamente; não inventar commits nem atribuir implementação a pessoas sem confirmação. `AUTORES.md` já está preenchido com as responsabilidades confirmadas.
4. **Conferir corretude além do checksum.** Usar as coordenadas de cada centroide e tolerância apropriada; igualdade observada em 33 casos não garante correção universal.
5. **Interpretar desempenho com cautela.** Registrar ambiente, flags, repetição/aquecimento, escopo cronometrado, mediana/desvio e campanha sequencial correspondente. Variabilidade e sobrecarga MPI são hipóteses a medir, não fatos causalmente demonstrados.
6. **Segurança Git:** não executar `push --force`, merges sem revisão ou publicação direta na `main`. Preservar as branches históricas e confirmar a ancestralidade antes de abrir o PR MPI contra `main`.
7. **Manter documentação consistente:** ao concluir tarefas, atualizar `README.md`, `docs/ESTADO_ATUAL.md`, `docs/PROXIMOS_PASSOS.md`, `docs/EXPERIMENTOS.md` e, quando necessário, `docs/ARQUITETURA.md`.
8. **Não armazenar segredos** (PAT, tokens, senhas) no repositório, documentação ou saídas de testes.

## 8. Próximas ações prioritárias

1. Atualizar `AGENTS.md` e os documentos `docs/` com os resultados MPI efetivamente medidos, sem reescrever retrospectivamente os dados OpenMP.
2. Completar a análise da Lei de Amdahl, explicitando hipóteses; detalhar custos de comunicação/geração não cronometrados.
3. Fazer, se possível, uma **campanha conjunta controlada** sequencial/OpenMP/MPI, registrando hardware, carga, variabilidade e condições para comparação justa; testar no laboratório.
4. Auditar scripts, CSVs, PNGs e fontes; executar `make clean && make`, validações e `git diff --check`; então preparar um commit na branch `desenvolvimento/mpi`.
5. O PR #18 foi mesclado à `main` em 10/11/2026. O commit `22d9583`, base da branch MPI, já pertence ao histórico de `origin/main`. Publicar `desenvolvimento/mpi` e criar um PR contra `main`. A implementação MPI ainda não está integrada.
6. Confirmar exigências finais do professor, reprodutibilidade, autoria real dos commits, demonstração e arguição cruzada. Prazo indicado para o Marco 2: **12/11/2026**; apresentações **19 ou 26/11/2026**.

## 9. Protocolo de handoff

Ao interromper/retomar o projeto, registrar em `docs/PROXIMOS_PASSOS.md`:

```markdown
### Handoff — AAAA-MM-DD HH:MM (fuso)
- Branch, commit e status local:
- PRs abertos e revisões pendentes:
- Objetivo atual:
- Arquivos modificados/criados:
- Comandos realmente executados e saídas:
- Métricas e evidências CSV/PNG:
- Testes faltantes, limitações e bloqueios:
- Próxima ação exata:
```

Nunca declarar uma tarefa como concluída apenas porque a IA escreveu instruções: exigir confirmação de execução ou artefato verificável.
