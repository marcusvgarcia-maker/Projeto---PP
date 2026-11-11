# Próximos passos — publicação e apresentação

## Etapas técnicas concluídas

- Docker preparado e registrado pelo aluno no commit 852af1d.
- Campanha executada no commit 66e2e16.
- OpenMP 9/9 e MPI 33/33 aprovados nos validadores individuais anteriores.
- 105 medições fortes, 30 fracas e 15 de perfilamento conferidas.
- Cálculos, logs, hashes e gráficos da campanha revisados.
- Relatório com Amdahl, variabilidade, recortes de tempo e limitações preparado.

## Entrega do Marco 2 — 12/11/2026

1. Aplicar o patch de fechamento na branch entrega/finalizacao, revisar o diff
   e executar make amdahl para conferir o alvo auxiliar acrescentado.
2. Registrar a documentação e a pasta completa da campanha em um commit.
3. Publicar a branch com git push -u origin entrega/finalizacao.
4. Abrir/revisar o PR contra main; conferir os arquivos e a participação real do grupo.
5. Integrar a versão final e enviar o link pelo canal solicitado pelo professor.

Não criar commits fictícios ou alterar autoria para simular participação.
As contribuições registradas devem corresponder ao trabalho efetivo.

## Seminário — 19 ou 26/11/2026, conforme a escala

Usar [ROTEIRO_DEMONSTRACAO.md](ROTEIRO_DEMONSTRACAO.md).
Testar em Linux do laboratório quando possível. Ensaiar baseline, OpenMP,
MPI, gráfico de speedup e questões de outra frente. A defesa individual
deve ocorrer sem apoio de colegas ou IA, conforme o enunciado.

## Handoff — 11/11/2026, America/Sao_Paulo

- Estado de entrada: branch entrega/finalizacao, commit da campanha 66e2e16ab971cdadb98d683c3ce316ef79889af6.
- Dados recebidos: campanha_docker_20261111_181418_para_enviar.zip.
- Integridade: ZIP íntegro, caminhos seguros e dez hashes SHA-256 conferidos.
- Auditoria: 150 registros confrontados com logs; 190 subprocessos sem erro/timeout.
- Estatísticas: 21 configurações fortes, 6 fracas, 3 perfis e 18 previsões conferidos.
- Evidências: resultados/campanha_docker_20261111_181418/ e docs/RESULTADOS_FINAIS_DOCKER.md.
- Preparado: documentação final, roteiro de demonstração e alvo Makefile amdahl.
- Não realizado pelo assistente: executar na máquina física do aluno, publicar
  a branch local, integrar o PR, enviar o link ao professor ou testar no laboratório.
- Próxima ação exata: aplicar o patch, conferir make amdahl e registrar os arquivos.
- Limites: energia/carga manuais não registradas; fraca e entradas pequenas com
  alta dispersão; nenhuma atribuição causal isolada a false sharing/comunicação.
