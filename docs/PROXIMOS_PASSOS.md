# Próximos passos e transferência de contexto — Projeto PP / K-means

> **Atualizacao confirmada em 11/11/2026:** MPI integrado a main pelo PR #19 (merge d9fb659). O aluno criou a branch local entrega/finalizacao e o commit 852af1d com o ambiente Docker; sua publicacao ainda nao foi demonstrada. No conteiner, seis executaveis compilaram, OpenMP passou em 9/9 comparacoes e MPI em 33/33, com erro maximo 0,0. A campanha conjunta e o novo perfilador foram preparados, mas ainda precisam ser executados na maquina do aluno. Consulte [o roteiro atual](ROTEIRO_CAMPANHA_DOCKER.md). Os registros datados anteriores descrevem as respectivas etapas historicas.


> **Data de referência:** 10/11/2026 (horário de Brasília).  
> **Projeto:** IESB · Ciência da Computação · CCO085 · 2026/2 · Problema 10 — K-means (algoritmo de Lloyd).  
> **Repositório:** https://github.com/marcusvgarcia-maker/Projeto---PP  
> **Clone de trabalho:** `~/projeto_pp_integracao` (Ubuntu no WSL2).  
> **Branch local:** `desenvolvimento/mpi`, criada a partir de `organizacao/kmeans` (base `22d9583`).  
> **Importante:** estados e resultados abaixo foram confirmados por saídas de terminal compartilhadas durante a colaboração; não significam que as alterações já estejam publicadas no GitHub.

## 1. Regras para retomar o trabalho

1. Trabalhar no clone Ubuntu com `cd ~/projeto_pp_integracao`; a pasta antiga em `/mnt/c/.../projeto_pp` pertence a **outro contexto Git** e não deve ser usada para commits deste projeto.
2. Antes de qualquer operação Git, executar `git status --short --branch`, conferir o remoto e verificar se houve mudanças desde esta documentação.
3. Preservar `sequencial/10_kmeans.cpp`, a lógica do professor e as evidências originais. Não sobrescrever CSVs ou gráficos históricos com novos ensaios.
4. Distinguir o que foi **executado e validado**, o que foi **documentado localmente** e o que ainda está **pendente de revisão, commit ou publicação**.
5. Seguir `README.md`, `AGENTS.md`, `docs/ESTADO_ATUAL.md`, `docs/ARQUITETURA.md` e `docs/EXPERIMENTOS.md`, dando prioridade ao código e aos CSVs reais se houver divergências.

## 2. Estado técnico confirmado em 10/11/2026

| Frente | Estado | Evidência principal |
|---|---|---|
| Baseline sequencial | Implementado e compilado | `sequencial/10_kmeans.cpp`; `make` |
| Perfilamento | Realizado (preliminar) | Atribuição: 87,38%; recálculo: 12,61% em uma medição |
| OpenMP | Implementado e compilado | `openmp/10_kmeans.cpp` |
| Corretude OpenMP | **9/9 aprovações** | `scripts/validar_openmp.sh`, `resultados/validacao_openmp.csv` |
| Desempenho OpenMP | 60 medições e 9 gráficos | `resultados/resultados_openmp.csv`, `resultados/resumo_openmp.csv`, `resultados/graficos/` |
| MPI | **Implementado e compilado** | `mpi/10_kmeans.cpp`, `build/10_kmeans_mpi` |
| Corretude MPI por checksum | **33/33 casos aprovados** | Nove casos padrão no `resultados/validacao_mpi.csv`; 24 adicionais observados no terminal |
| Corretude MPI por centroides | **33/33 casos aprovados**, erro absoluto máximo impresso 0,0 | `scripts/validar_centroides_mpi.py`, `resultados/validacao_centroides_mpi.csv` |
| Escalabilidade forte MPI | **60 medições** | `resultados/resultados_mpi.csv`, `resultados/resumo_mpi.csv`, 9 gráficos em `resultados/graficos_mpi/` |
| Comparação OpenMP × MPI | **Preliminar** | `resultados/comparacao_openmp_mpi.csv`, 9 gráficos em `resultados/graficos_comparacao/` |
| Escalabilidade fraca MPI | **15 medições** (1, 2, 4 processos; 1 milhão de pontos/processo) | `resultados/escalabilidade_fraca_mpi.csv`, `resultados/resumo_escalabilidade_fraca_mpi.csv`, gráfico em `resultados/graficos_mpi/` |
| Makefile | **Atualizado e compilado com sucesso** | `make clean && make` criou 6 executáveis, incluindo MPI |
| Documentação | **Em atualização local** | README, AGENTS, ESTADO_ATUAL, EXPERIMENTOS e ARQUITETURA foram substituídos e verificados; este arquivo é o último dessa sequência |
| Publicação da fase MPI | **Pendente** | Arquivos MPI e resultados ainda não rastreados por Git no último `git status`; sem commit/push/PR MPI confirmados |

**Implementação MPI atual:** processo 0 gera os mesmos pontos do baseline e inicializa os centroides; `MPI_Bcast` compartilha centroides iniciais; `MPI_Scatterv` distribui blocos contíguos de pontos, inclusive quando `N` não é divisível por `P`. Em cada iteração, cada processo atribui seus pontos e calcula somas/contagens locais; `MPI_Allreduce` produz os totais globais e os centroides são atualizados em todos os processos. `MPI_Reduce` com `MPI_MAX` agrega o maior tempo das iterações. A geração, os broadcasts e os scatter iniciais ficam **fora** da medição reportada como `tempo`.

**Regras de corretude:** distância euclidiana ao quadrado; primeiro centroide em empates (`<`); número fixo de iterações; centroides de clusters vazios preservados; gerador e semente originais. O parâmetro opcional `--centroides` na implementação MPI imprime os centroides finais com `%.17g` para validação. A aprovação se limita aos cenários executados.

## 3. Resultados que não devem ser confundidos

### 3.1 Escalabilidade forte — MPI

Para `K=8`, `IT=20`, 5 repetições por configuração e três valores de `N`:

| N | Baseline da campanha MPI (s) | MPI 1 (s) | MPI 2 (s) | MPI 4 (s) |
|---:|---:|---:|---:|---:|
| 100.000 | 0,103463 | 0,092206 | 0,104039 | 0,310480 |
| 1.000.000 | 0,691980 | 0,669102 | 0,367687 | 0,431920 |
| 5.000.000 | 2,341218 | 2,316310 | 2,050126 | 1,469368 |

Para `N=5.000.000`, quatro processos obtiveram *speedup* de aproximadamente **1,593×** e eficiência de **39,8%** em relação ao sequencial **da campanha MPI**. Para `N=100.000`, quatro processos foram mais lentos que o sequencial.

### 3.2 Escalabilidade fraca — MPI

Com um milhão de pontos por processo (`N=P×1.000.000`, `K=8`, `IT=20`):

| Processos | Tempo médio (s) | Desvio-padrão (s) | Eficiência fraca |
|---:|---:|---:|---:|
| 1 | 0,670650 | 0,243925 | 100,0% |
| 2 | 0,814082 | 0,120106 | 82,4% |
| 4 | 1,661666 | 0,191052 | 40,4% |

Os resultados indicam perda de eficiência **nessas medições**, mas a dispersão é relevante; não atribuir causalidade exclusiva às coletivas MPI ou ao WSL2 sem instrumentos adicionais.

### 3.3 Comparação entre OpenMP e MPI

A campanha OpenMP histórica e a campanha MPI recente foram coletadas em momentos diferentes e apresentam médias sequenciais distintas (por exemplo, `N=100.000`: 0,050713 s na campanha OpenMP versus 0,103463 s na campanha MPI). Assim, as curvas de *speedup* de cada uma usam **referências diferentes**. A comparação direta de desempenho é **exploratória**, não uma demonstração controlada de superioridade de uma tecnologia.

O protocolo atual mede **somente as iterações**, excluindo distribuição inicial MPI. Uma eventual análise do custo total fim a fim exigirá instrumentação separada e alinhamento do escopo com as demais versões.

## 4. Pendências prioritárias para o Marco 2

A entrega está indicada para **12/11/2026**; priorizar reprodutibilidade, integridade e integração do repositório antes de experimentos opcionais.

- [x] Implementar, compilar e validar a versão MPI nos cenários testados.
- [x] Coletar resultados de escalabilidade forte MPI, calcular métricas e gerar nove gráficos.
- [x] Coletar resultados de escalabilidade fraca MPI, calcular métricas e gerar um gráfico.
- [x] Produzir comparação **preliminar** OpenMP × MPI e gráficos.
- [x] Incluir `mpi` no alvo padrão do `Makefile` e confirmar `make clean && make`.
- [x] Atualizar e verificar `README.md`, `AGENTS.md`, `docs/ESTADO_ATUAL.md`, `docs/EXPERIMENTOS.md` e `docs/ARQUITETURA.md` localmente.
- [ ] Instalar e verificar **este** `docs/PROXIMOS_PASSOS.md` no clone.
- [ ] Revisar todos os scripts novos (erros, dependências, permissões, caminhos, não sobrescrita de dados) e confirmar o conteúdo real de `mpi/`.
- [ ] Conferir `AUTORES.md` e a distribuição formal de trabalho/commits entre os três integrantes; não inferir autoria a partir do usuário que executou os testes.
- [ ] Rodar uma revisão final de compilação, validações e consistência dos CSVs e gráficos em um clone limpo ou ambiente equivalente.
- [ ] Revisar a análise de Lei de Amdahl, separando hipótese teórica, fração observada de atribuição e *speedup* medido; **não tratar como concluída**.
- [ ] Publicar a branch `desenvolvimento/mpi` e abrir um Pull Request contra `main`. Os três commits locais estão concluídos, e o PR #18 já foi mesclado.
- [ ] Abrir PR MPI com base apropriada após confirmar como a reorganização será integrada; solicitar revisão da equipe.
- [ ] Se viável, repetir a comparação OpenMP × MPI na **mesma campanha** sob condições mais controladas e registrar hardware/afinidade/carga concorrente. Não bloquear a preservação dos resultados existentes.
- [ ] Se exigido ou houver tempo, realizar escalabilidade fraca OpenMP; **ainda não comprovada**.
- [ ] Testar no Linux do laboratório, preparar demonstração e apresentação; seminários previstos para 19 ou 26/11/2026.

## 5. Sequência imediata recomendada

**Etapa A — Fechar a documentação local:** copiar este arquivo para `docs/PROXIMOS_PASSOS.md`; executar `head`, `grep`, `git diff --check` e `git diff --stat`. Ajustar referências que ainda digam que MPI não existe.

**Etapa B — Auditoria antes do commit:** na branch `desenvolvimento/mpi`, listar arquivos modificados e não rastreados; revisar diffs; verificar se fontes, scripts, CSVs e PNGs necessários estão presentes. **Atenção:** `git diff --check` sozinho não avalia arquivos ainda não rastreados; depois de `git add`, usar também `git diff --cached --check`.

**Etapa C — Teste final reproduzível:** `make clean && make`, `bash scripts/validar_openmp.sh`, `python3 scripts/validar_centroides_mpi.py`; conferir quantidades dos registros (`61` linhas de forte, `16` linhas de fraca, `13` no resumo forte, `4` no resumo fraco) e existência dos gráficos. Evitar repetir ensaios longos sem necessidade; preservá-los como campanhas identificáveis.

**Etapa D — Git e revisão:** os três commits MPI foram concluídos. O PR #18 já foi mesclado à `main`, e o commit `22d9583` é ancestral de `origin/main`. Resta publicar `desenvolvimento/mpi`, abrir o PR MPI contra `main` e solicitar revisão. Não utilizar `push --force`.

**Etapa E — Preparação da entrega:** conferir dependências (G++, OpenMPI, Python 3, matplotlib), instruções de execução, dados, gráficos, responsabilidades e roteiro de demonstração.

## 6. Comandos de referência

```bash
cd ~/projeto_pp_integracao

git status --short --branch
make clean && make

# Validação de centroides
bash scripts/validar_openmp.sh
python3 scripts/validar_centroides_mpi.py

# Execução MPI: exemplo
mpirun --oversubscribe -np 4 ./build/10_kmeans_mpi 1000000 8 20

# Análises de resultados já coletados
python3 scripts/analisar_mpi.py
python3 scripts/analisar_escalabilidade_fraca_mpi.py
python3 scripts/comparar_openmp_mpi.py

# Verificações de contagens
wc -l resultados/resultados_mpi.csv resultados/resumo_mpi.csv \
  resultados/escalabilidade_fraca_mpi.csv resultados/resumo_escalabilidade_fraca_mpi.csv

git diff --check
```

`--oversubscribe` foi utilizado para possibilitar execução no ambiente observado; isso não assegura execução ideal para benchmark. O argumento do script de validação MPI por centroides e seu relatório são explicados em `docs/EXPERIMENTOS.md`.

## 7. GitHub e integração segura

- O PR [#18](https://github.com/marcusvgarcia-maker/Projeto---PP/pull/18) contém a reorganização em `organizacao/kmeans` para `main`; **último estado conhecido:** aberto para revisão, ainda não integrado. Verificar novamente antes de ações Git.
- A branch local `desenvolvimento/mpi` contém a implementação e documentação novas, mas **não há commit/push/PR MPI confirmado** nesta etapa.
- As branches históricas `baseline_perfilamento` e `openmp` têm histórias independentes de `main`; preservá-las e evitar merges automáticos sem plano específico.
- O trabalho MPI deve ser revisado com os integrantes responsáveis antes de integração final e atribuição de autoria.

## 8. Registro de passagem de tarefa (*handoff*)

Ao terminar cada sessão, registrar: data, branch, arquivos alterados, comandos realmente executados, evidências, pendências, próximo comando e bloqueios. Não substituir resultados confirmados por previsões.

### Handoff — 2026-11-10 (fase MPI, documentação quase concluída)

- **Branch:** `desenvolvimento/mpi` no clone `~/projeto_pp_integracao`.
- **Compilação confirmada:** `make clean && make` criou `10_kmeans_base`, `10_kmeans_omp`, `10_kmeans_perfil`, `validacao_seq`, `validacao_omp` e `10_kmeans_mpi`.
- **Validação confirmada:** OpenMP 9/9; MPI 33/33 por checksum (nove casos no CSV padrão e 24 adicionais relatados); MPI 33/33 por centroides, maior erro impresso 0,0.
- **Experimentos confirmados:** forte MPI 60 medidas + nove gráficos; fraca MPI 15 medidas + um gráfico; comparação preliminar OpenMP × MPI + nove gráficos.
- **Arquivos rastreados modificados no último `git diff --stat` compartilhado:** `AGENTS.md`, `Makefile`, `README.md`, `docs/ARQUITETURA.md`, `docs/ESTADO_ATUAL.md`, `docs/EXPERIMENTOS.md`; `git diff --check` sem saída. Fontes e scripts MPI e novos CSVs/gráficos ainda apareciam como **não rastreados** no `git status` anterior.
- **Documentação restante:** copiar e confirmar este `docs/PROXIMOS_PASSOS.md`.
- **Confirmado:** PR #18 integrado à `main` e três commits MPI criados localmente. **Pendente:** publicação e PR MPI, análise final de Amdahl, comparação controlada de desempenho e teste no laboratório.
- **Próxima ação:** instalar o documento, verificar `git diff --check` e `git diff --stat`, fazer auditoria de conteúdo e então preparar commits sem perder os novos arquivos.


## Handoff — 11/11/2026, America/Sao_Paulo

- Estado informado pelo usuario: branch entrega/finalizacao, commit 852af1d, arvore limpa.
- PR #19 integrado a main, merge d9fb659. Dockerfiles ainda nao aparecem na main consultada.
- Confirmado no Docker do aluno: seis compilacoes; OpenMP 9/9 e MPI 33/33 centroides, erro maximo 0,0; Matplotlib 3.6.3.
- Preparado nesta etapa: coletor conjunto, analisador, perfilador sequencial adicional e roteiro.
- O baseline, OpenMP, MPI e CSVs historicos permanecem inalterados.
- Teste tecnico do pacote em outro executor: coleta real sequencial/OpenMP, analise automatica e comparacao individual do novo perfilador com o baseline. Isso nao constitui a campanha do aluno.
- Nao executado pelo assistente: nova campanha completa no Docker do aluno, incluindo MPI.
- Proxima acao: copiar o pacote para o repositorio, revisar e registrar as mudancas reais; dentro do conteiner executar python3 scripts/medir_campanha_docker.py e enviar o ZIP gerado.
- Amdahl: instrumentacao e formulas preparadas; valores finais e discussao permanecem pendentes ate a coleta.
- Preservar as campanhas antigas, registrar condicoes de energia/carga e revisar o relatorio gerado antes da entrega.
