
# Próximos passos — entrega e apresentação

## Etapas técnicas concluídas

- [x] Preparar e registrar o ambiente Docker.
- [x] Executar a campanha experimental.
- [x] Validar os resultados e os dados coletados.
- [x] Conferir os logs, hashes e gráficos.
- [x] Preparar a documentação técnica e experimental.
- [x] Registrar os commits de finalização.
- [x] Publicar a branch entrega/finalizacao.
- [x] Abrir e revisar o Pull Request #20.
- [x] Integrar o Pull Request #20 à main.
- [ ] Integrar o Pull Request da documentação após a revisão.
- [ ] Enviar o link da entrega pelo canal solicitado pelo professor.

## Histórico da integração

A finalização foi desenvolvida na branch entrega/finalizacao.

O PR #20 foi integrado à main.

- Pull Request: https://github.com/marcusvgarcia-maker/Projeto---PP/pull/20
- Branch de origem: entrega/finalizacao.
- Commit de integração: 35d1005.
- Commit da campanha: 66e2e16.

A versão integrada contém os fontes, scripts, documentação,
resultados e evidências experimentais do fechamento do projeto.

## Entrega acadêmica

- [ ] Confirmar o envio do link do repositório ao professor.
- [ ] Registrar eventual confirmação de recebimento.
- [ ] Registrar eventuais correções solicitadas pelo professor.

O envio do link deve ser marcado como concluído somente após
sua realização efetiva.

## Apresentação e seminário

Consultar [ROTEIRO_DEMONSTRACAO.md](ROTEIRO_DEMONSTRACAO.md).

- [x] Data da apresentação: confirmada, caso seja realmente 26/11/2026.
- [ ] Confirmar a realização de testes no laboratório, caso aplicável.
- [ ] Ensaiar a execução do baseline sequencial.
- [ ] Ensaiar a execução OpenMP.
- [ ] Ensaiar a execução MPI.
- [ ] Preparar a explicação dos gráficos de speedup e eficiência.
- [ ] Revisar o modelo de Amdahl e suas limitações.
- [ ] Preparar todos os integrantes para a arguição individual.
- [x] Horário da apresentação: 8h ás 11h.

## Registro de auditoria — 11/11/2026

- Estado de entrada: branch entrega/finalizacao.
- Commit da campanha: 66e2e16ab971cdadb98d683c3ce316ef79889af6.
- Dados recebidos: campanha_docker_20261111_181418_para_enviar.zip.
- Integridade: ZIP íntegro, caminhos seguros e dez hashes SHA-256 conferidos.
- Auditoria: 150 registros confrontados com logs.
- Execuções: 190 subprocessos com retorno zero.
- Estatísticas: 21 configurações fortes, 6 fracas e 3 perfis.
- Evidências: resultados/campanha_docker_20261111_181418/.
- Relatório: docs/RESULTADOS_FINAIS_DOCKER.md.
- Publicação: branch entrega/finalizacao publicada.
- Integração: PR #20 integrado à main, commit 35d1005.

## Limitações registradas

- Observações manuais de energia e carga não foram registradas.
- Experimentos de escalabilidade fraca e entradas pequenas apresentam
  maior dispersão.
- Não foi estabelecida atribuição causal isolada para false sharing
  ou custos de comunicação.

Novas alterações no projeto devem partir da main atualizada,
preferencialmente em uma nova branch, com revisão por Pull Request.
