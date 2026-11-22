# Próximos passos — entrega e apresentação

Referência: 22/11/2026.

O prazo do Marco 2 foi prorrogado pelo professor para o dia da apresentação do grupo, em 26/11/2026.

## Etapas técnicas concluídas

- [x] Preparar e registrar o ambiente Docker.
- [x] Executar a campanha experimental de 11/11/2026.
- [x] Validar os resultados e os dados coletados.
- [x] Conferir os logs, hashes, CSVs e gráficos.
- [x] Preparar a documentação técnica e experimental.
- [x] Registrar os commits de finalização.
- [x] Publicar a branch `entrega/finalizacao`.
- [x] Abrir e integrar o Pull Request #20 à `main`.
- [x] Realizar testes adicionais de execução no Docker do laboratório.

### Testes adicionais no laboratório

Em novembro de 2026, foram realizados testes adicionais no ambiente Docker do laboratório.

- Docker 29.3.1.
- Docker Compose 5.1.1.
- CPU Intel Core i5-9500 @ 3.00 GHz.
- Memória visível no Linux: 8.073.716 kB.
- Execução com checksum `8109.0037`.
- Oito centroides apresentados em uma das execuções.
- Tempo aproximado de 0,19 segundo nessa execução.

A execução foi realizada, mas a validação completa OpenMP 9/9 não foi confirmada nesse ambiente. Não atribuir aos testes adicionais a cobertura da campanha experimental oficial.

## Histórico da integração

A finalização documental e experimental foi desenvolvida na branch `entrega/finalizacao`.

O PR #20 integrou essa finalização à branch `main`.

- Pull Request: https://github.com/marcusvgarcia-maker/Projeto---PP/pull/20
- Branch de origem: `entrega/finalizacao`.
- Branch de destino: `main`.
- Commit de integração: `35d1005`.
- Commit da campanha: `66e2e16`.

A versão integrada contém os fontes, scripts, documentação, resultados e evidências experimentais do fechamento do projeto.

O PR #21 foi aberto para atualizar e revisar a documentação restante. Sua integração ainda depende da conclusão da revisão documental e da confirmação do destino correto (`main`).

## Entrega acadêmica

- [ ] Confirmar o envio do link do repositório ao professor.
- [ ] Registrar eventual confirmação de recebimento.
- [ ] Registrar eventuais correções solicitadas pelo professor.

O envio do link deve ser marcado como concluído somente após sua realização efetiva.

## Apresentação e seminário

Consultar [ROTEIRO_DEMONSTRACAO.md](ROTEIRO_DEMONSTRACAO.md).

### Informações da apresentação

- Data: 26/11/2026.
- Horário: das 8h às 11h.
- Prazo do Marco 2: dia da apresentação, conforme prorrogação concedida pelo professor.

### Preparação

- [ ] Ensaiar a execução do baseline sequencial.
- [ ] Ensaiar a execução OpenMP.
- [ ] Ensaiar a execução MPI.
- [ ] Preparar a explicação dos gráficos de speedup e eficiência.
- [ ] Revisar o modelo de Amdahl e suas limitações.
- [ ] Preparar todos os integrantes para a arguição individual.
- [ ] Conferir o ambiente e os comandos que serão utilizados na apresentação.

## Registro de auditoria — campanha de 11/11/2026

- Estado de entrada: branch `entrega/finalizacao`.
- Commit da campanha: `66e2e16ab971cdadb98d683c3ce316ef79889af6`.
- Dados recebidos: `campanha_docker_20261111_181418_para_enviar.zip`.
- Integridade: ZIP íntegro, caminhos seguros e dez hashes SHA-256 conferidos.
- Auditoria: 150 registros confrontados com logs.
- Execuções: 190 subprocessos com retorno zero.
- Estatísticas: 21 configurações fortes, 6 fracas e 3 perfis.
- Evidências: `resultados/campanha_docker_20261111_181418/`.
- Relatório: `docs/RESULTADOS_FINAIS_DOCKER.md`.
- Publicação: branch `entrega/finalizacao` publicada.
- Integração: PR #20 integrado à `main`, commit `35d1005`.

## Limitações registradas

- Observações manuais de energia e carga não foram registradas na campanha oficial.
- Experimentos de escalabilidade fraca e entradas pequenas apresentam maior dispersão.
- Não foi estabelecida atribuição causal isolada para false sharing ou custos de comunicação.
- Os resultados da campanha representam o ambiente e as condições de execução registrados, não uma garantia de desempenho em outros equipamentos.

Novas alterações no projeto devem partir da `main` atualizada, preferencialmente em uma nova branch, com revisão por Pull Request.
