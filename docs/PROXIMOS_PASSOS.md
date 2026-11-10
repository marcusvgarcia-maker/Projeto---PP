# Próximos passos e transferência de contexto — Projeto PP / K-means

> **Atualizado em:** 09/11/2026 (horário de Brasília)  
> **Projeto:** IESB · Ciência da Computação · CCO085 · 2026/2 · Problema 10 — K-means (algoritmo de Lloyd)  
> **Repositório remoto:** https://github.com/marcusvgarcia-maker/Projeto---PP  
> **Pasta local atual:** `projeto_pp/` (Windows 11, VS Code, Ubuntu via WSL2)  
> **Natureza:** plano de continuidade e *handoff*. Não confundir ações propostas com ações já realizadas.

## 1. Leia isto antes de começar

1. Leia `README.md`, `AGENTS.md` e `docs/ESTADO_ATUAL.md` para entender o funcionamento, as restrições e os testes já realizados.
2. Confira os arquivos presentes, a branch atual, `git status` e as alterações locais antes de editar ou reorganizar. **A estrutura local atualizada ainda não foi confirmada como publicada na `main` do GitHub.**
3. Não altere a lógica matemática do baseline original `sequencial/10_kmeans.cpp`: geração determinística, inicialização, distâncias, desempate, quantidade fixa de iterações e tratamento de clusters vazios.
4. Preserve os resultados históricos e os códigos-fonte. Faça retestes em arquivos separados, com data e método documentados.
5. Para trabalho com IA: informe sempre **o que está comprovado**, **o que foi apenas preparado** e **qual o próximo comando de verificação**. Não presuma que comandos de conversas anteriores foram executados.

## 2. Estado confirmado até aqui

| Frente | Situação | Evidência |
|---|---|---|
| Baseline | Compilado e executado | `make`; `./build/10_kmeans_base 1000000 8 20` apresentou `checksum=8109.0037` |
| Perfilamento | Uma medição realizada | Em `N=1000000, K=8, IT=20`: atribuição 87,38%; recálculo 12,61% (resultado preliminar) |
| Medições sequenciais | Realizadas | 3 tamanhos × 5 repetições: `resultados/baseline.csv` |
| OpenMP | Implementado, compilado e executado | Atribuição paralela `schedule(static)` e recálculo com acumuladores privados e redução manual |
| Medições OpenMP | Realizadas | 60 medidas em `resultados/resultados_openmp.csv`; gráficos de tempo, speedup e eficiência |
| Correção OpenMP | **9/9 validações aprovadas** | `bash scripts/validar_openmp.sh` e `resultados/validacao_openmp.csv` |
| Gerador de gráficos | Testado na nova estrutura | 9 PNGs + 1 CSV regenerados em `resultados/graficos_teste/` |
| `Makefile` | Funcional para sequencial, perfilamento, OpenMP e validadores | `make` compilou 5 executáveis, sem erro |
| Scripts `medir_baseline.sh` e `medir_openmp.sh` | Caminhos corrigidos e sintaxe aprovada | `bash -n` passou; **execução completa dos scripts reorganizados ainda não foi testada** |
| `AGENTS.md` | Atualizado e verificado | `head` e `grep` confirmaram cabeçalho e referência aos 9/9 testes |
| `docs/ESTADO_ATUAL.md` | **Atualizado e verificado** | `head` e `grep` confirmaram cabeçalho e registro de 9/9 testes |
| `README.md` | Versão atualizada preparada anteriormente | **A substituição local ainda não foi demonstrada nesta conversa por comando**; conferir arquivo real |
| MPI | **Não iniciado/confirmado no ambiente local** | Pasta `mpi/` estava vazia na última árvore; código sugerido em conversa não significa implementado |
| Integração com GitHub | Pendente | Há branches históricas `main`, `baseline_perfilamento` e `openmp`; estrutura local nova não confirmada na `main` |

### Resultados numéricos que devem permanecer rastreáveis

- **Perfilamento:** `N=1000000`, `K=8`, `IT=20`: tempo total `0,348253 s`; atribuição `0,304297 s` (87,38%); recálculo `0,043902 s` (12,61%). Medição única; não converter automaticamente 87,38% na fração paralelizável exata para Amdahl.
- **Médias do experimento OpenMP original** (sequencial / 1 / 2 / 4 threads, segundos):
  - N=100000: `0,050713 / 0,051308 / 0,075015 / 0,101940`.
  - N=1000000: `0,527968 / 0,464654 / 0,638230 / 0,539434`.
  - N=5000000: `2,243186 / 2,297215 / 2,107286 / 1,805006`.
- **Caso de maior entrada:** speedup médio de OpenMP com 4 threads em relação ao baseline sequencial ≈ **1,243×**; eficiência ≈ **31,1%**. Os tempos apresentaram variabilidade importante, de causa ainda não determinada.
- **Validação de centroides:** N = 100000, 1000000, 5000000; K=8; IT=20; 1, 2 e 4 threads. Todas as coordenadas finais coincidiram com as do baseline nos testes executados. Outros valores de K e IT não foram validados nesse protocolo.

## 3. Próxima tarefa imediata — concluir a documentação local

**Situação de entrada:** `AGENTS.md` e `docs/ESTADO_ATUAL.md` foram atualizados e verificados. Agora falta revisar os demais documentos com base na estrutura reorganizada e no que foi realmente testado.

### 3.1 Atualizar este arquivo `docs/PROXIMOS_PASSOS.md`

- [ ] Substituir a versão antiga por este arquivo, preservando backup se desejado.
- [ ] Conferir o cabeçalho com `head -n 5 docs/PROXIMOS_PASSOS.md`.
- [ ] Conferir o status MPI com `grep -n 'MPI' docs/PROXIMOS_PASSOS.md | head`.
- [ ] Marcar o item como concluído no `docs/ESTADO_ATUAL.md`, após confirmação.

### 3.2 Revisar os demais documentos

- [ ] **`README.md`:** confirmar que a versão atualizada está instalada e que todos os caminhos/comandos se referem à estrutura `projeto_pp/`, com executáveis em `build/`.
- [ ] **`docs/ARQUITETURA.md`:** registrar algoritmo, entradas, gerador, atribuição, recálculo, sincronização, versões, riscos numéricos e decisões OpenMP. Descrever MPI como *planejado*, não *implementado*.
- [ ] **`docs/EXPERIMENTOS.md`:** apontar para `resultados/baseline.csv`, `resultados/resultados_openmp.csv`, `resultados/resumo_openmp.csv`, os 9 PNGs e `resultados/validacao_openmp.csv`; explicar protocolo, média/mediana/desvio, variabilidade e limitações.
- [ ] **`AUTORES.md`:** substituir o modelo pelas três pessoas e responsabilidades reais, confirmadas pelo grupo. Não inventar nomes ou funções.
- [x] **Configurar `.gitignore`:** concluído em 09/11/2026. O arquivo ignora `build/`, executáveis, caches e arquivos temporários, preservando os CSVs e PNGs experimentais. A pasta `resultados/graficos_teste/` também está configurada para ser ignorada.
- [x] **Organizar documentos antigos e backups:** concluído em 09/11/2026. As versões anteriores dos documentos foram retiradas da estrutura principal e preservadas em backup externo. Os arquivos `README.md`, `AGENTS.md`, `AUTORES.md` e os documentos atuais de `docs/` são as referências oficiais.

**Critério de conclusão:** uma pessoa sem acesso à conversa consegue localizar o código, compilar, executar, validar, regenerar gráficos e identificar com precisão o que falta, seguindo os documentos do repositório.

## 4. Próxima frente obrigatória — implementação MPI

**Marco 2:** entrega prevista para **12/11/2026**. Priorizar uma versão MPI funcional e correta, além de medições e documentação essenciais.

### 4.1 Desenvolvimento

- [ ] Verificar compilador, execução e topologia disponível: `mpic++ --version`, `nproc`, testes MPI mínimos. A execução `mpirun -np 4 ...` sem `--oversubscribe` falhou anteriormente por problema de slots; o teste `mpirun --oversubscribe -np 4 /bin/echo MPI_OK` funcionou. **Investigar antes de benchmarks**.
- [ ] Criar `mpi/10_kmeans.cpp` **a partir das mesmas regras matemáticas do baseline**.
- [ ] Justificar a divisão de pontos entre processos e a inicialização dos centroides.
- [ ] Distribuir dados e coordenar o cálculo global mediante coletivas (como `MPI_Bcast`, `MPI_Scatterv` e `MPI_Allreduce`, se apropriadas).
- [ ] Impor a dependência entre fases: atribuição → redução/atualização → próxima iteração.
- [ ] Compilar com `make mpi`; atualizar `all` do Makefile **depois** que o fonte MPI estiver pronto e compilável.
- [ ] Testar com 1, 2 e 4 processos; verificar primeiro checksum e depois **todas as coordenadas dos centroides**. Considerar diferenças da ordem de soma de ponto flutuante; documentar critério e tolerância, sem ocultar divergências.

### 4.2 Experimentos e análise

- [ ] Criar `scripts/medir_mpi.sh`, registrando tempos e checksums em `resultados/resultados_mpi.csv`, com aquecimento e repetição.
- [ ] Evitar usar `--oversubscribe` para concluir sobre speedup sem reconhecer seu efeito. Registrar número de CPUs, versão de MPI, afinidade/slots e condições do WSL.
- [ ] Definir claramente os trechos cronometrados: o baseline mede **somente as iterações**; uma versão MPI pode medir distribuição inicial + iterações. **Alinhar o escopo da comparação ou declarar explicitamente a diferença.**
- [ ] Calcular tempo médio, speedup relativo ao baseline sequencial e eficiência por processo.
- [ ] Gerar gráficos para MPI e comparar com OpenMP e baseline.
- [ ] Analisar escalabilidade **forte** (mesmo N, variar processos) e **fraca** (aumentar N proporcionalmente aos processos), com ressalvas sobre limites do ambiente.
- [ ] Estimar e justificar a fração paralelizável e comparar os resultados com a Lei de Amdahl. Discutir comunicação, sincronização, balanceamento, banda de memória e outros fatores apenas quando relevantes e sustentados pelos dados.

## 5. Entrega e apresentação

- [ ] As três versões em diretórios separados, com fonte compilável, usando `make` no ambiente Linux da disciplina.
- [ ] `Makefile` compilando sequencial, OpenMP e MPI (inclusive `all`).
- [ ] Scripts para gerar CSVs; dados brutos e gráficos versionados conforme exigência do professor.
- [ ] `README.md` com dependências, compilação e demonstração do zero.
- [ ] `AUTORES.md` com responsabilidades técnicas formais dos três integrantes.
- [ ] Histórico de commits distribuído e legível; evitar entrega em commit único ou concentrada num integrante.
- [ ] Repositório disponível ao professor e testado no laboratório Linux (g++, OpenMPI).
- [ ] Preparar demonstração ao vivo (baseline, OpenMP, MPI e gráfico de speedup) e treino de arguição cruzada.

O professor prevê seminários em **19/11 e 26/11/2026**. A orientação oficial não requer explicitamente um PDF final separado no Marco 2; exige análise experimental e documentação no repositório. Verificar eventual comunicação complementar do professor antes da entrega.

## 6. Integração segura com GitHub — somente depois de conferir o local

- [ ] Conferir `git status`, branch e remotos no diretório correto.
- [ ] Preservar `main`, `baseline_perfilamento` e `openmp` históricas. A consulta feita em 09/11 encontrou ausência de ancestral comum entre `main` e as duas branches de desenvolvimento; **não fazer `git merge` automático às cegas**.
- [ ] Criar branch nova a partir da `main` e integrar seletivamente os arquivos reorganizados. Não publicar executáveis de `build/` nem arquivos de teste desnecessários.
- [ ] Revisar o diff, rodar `make`, `bash scripts/validar_openmp.sh` e geração de gráficos antes de abrir Pull Request.
- [ ] Publicar e revisar PR; depois registrar o commit de integração e atualizar `docs/ESTADO_ATUAL.md`.

## 7. Comandos de referência (na raiz de `projeto_pp/`)

```bash
# Compilar o que já está implementado
make

# Execução de referência
./build/10_kmeans_base 1000000 8 20
OMP_NUM_THREADS=4 OMP_DYNAMIC=FALSE ./build/10_kmeans_omp 1000000 8 20

# Validar centroides finais (9 combinações)
make validacao
bash scripts/validar_openmp.sh
cat resultados/validacao_openmp.csv

# Reproduzir os nove gráficos sem sobrescrever os originais
python3 scripts/gerar_graficos_openmp.py \
  resultados/resultados_openmp.csv resultados/graficos_teste

# Checar a sintaxe dos scripts de medição sem executar tudo
bash -n scripts/medir_baseline.sh
bash -n scripts/medir_openmp.sh
```

**Não há comando MPI pronto para executar até o fonte `mpi/10_kmeans.cpp` ser criado e compilado.**

## 8. Registro de passagem de tarefa (*handoff*)

Ao encerrar uma sessão de trabalho, adicionar um registro abaixo, mantendo os anteriores. Cada registro deve distinguir execução verificada de intenção.

```markdown
### Handoff — AAAA-MM-DD HH:MM (America/Sao_Paulo)
- Branch e commit: (se houver)
- Tarefa trabalhada:
- Arquivos efetivamente modificados:
- Comandos executados e resultados:
- Evidências geradas (caminhos):
- Testes não executados:
- Pendências ou bloqueadores:
- Próxima ação exata:
```

### Handoff — 2026-11-09 (documentação, pendente de instalação local)

- **Última ação comprovada:** `docs/ESTADO_ATUAL.md` foi substituído e `head -n 5` / `grep` localizaram o cabeçalho esperado e o texto **"9/9 testes aprovados"** na linha 170.
- **Novo artefato preparado:** esta revisão de `docs/PROXIMOS_PASSOS.md`. **A cópia para a pasta local ainda precisa ser confirmada.**
- **Próxima ação exata:** substituir `docs/PROXIMOS_PASSOS.md`, rodar as duas verificações simples indicadas na seção 3.1 e informar as saídas. Depois revisar `docs/ARQUITETURA.md` e `docs/EXPERIMENTOS.md`.
- **Estado MPI:** ainda não há fonte MPI salvo/testado no diretório local confirmado; não registrar a etapa como concluída.
