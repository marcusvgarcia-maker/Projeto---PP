# AGENTS.md — continuidade do projeto K-means

## Estado confirmado em 11/11/2026

Projeto CCO085, IESB 2026/2, problema 10. O PR #19 integrou MPI à main,
merge d9fb659. O usuário trabalha em ~/projeto_pp_integracao, branch local
entrega/finalizacao. O commit medido é 66e2e16ab971cdadb98d683c3ce316ef79889af6.
O fechamento documental está preparado para aplicação e publicação.
A última consulta GitHub não mostrou a branch entrega/finalizacao; confirmar
o estado atual antes de qualquer escrita remota.

Fonte principal: docs/RESULTADOS_FINAIS_DOCKER.md, docs/ESTADO_ATUAL.md,
docs/EXPERIMENTOS.md e a campanha resultados/campanha_docker_20261111_181418/.
Não confundir as campanhas históricas com a coleta Docker final.

## Invariantes obrigatórios

Preservar sequencial/10_kmeans.cpp como referência imutável.
Argumentos N/K/IT, padrões 1000000/8/20; LCG uint64_t original, semente 2024ULL;
centroides iniciais nos primeiros K pontos; distância ao quadrado; desempate
por d<best; exatamente IT iterações; cluster vazio conserva o centroide.
Não alterar matemática, gerador ou entradas sem autorização e nova análise.
Checksum com quatro casas não comprova individualmente todos os centroides.

## Evidências confirmadas

- Docker: Ubuntu 24.04.5, G++ 13.3.0, MPI 4.1.6, Matplotlib 3.6.3.
- CPU informada: i5-5300U, dois núcleos e quatro processadores lógicos.
- Memória visível no Linux: aproximadamente 7,70 GiB; não inferir RAM física do Windows.
- OpenMP 9/9 e MPI 33/33 centroides aprovados antes da campanha; erro MPI máximo 0,0.
- Campanha concluída: 105 registros fortes, 30 fracos e 15 de perfilamento.
- 150 checksums consistentes, 190 subprocessos com retorno zero e sem timeout.
- Hashes dos dez fontes/configurações arquivados conferidos.
- Maior N, quatro workers: OpenMP 1,303×; MPI 1,649×,
  somente para o tempo iterativo. A duração externa favoreceu OpenMP-4 nesse caso.
- Amdahl calculado como modelo ideal; não apresentar f como fração serial
  efetiva medida do paralelo nem S(infinito) como previsão para o notebook.
- Observações manuais de energia/carga ficaram vazias.

## Onde trabalhar e verificar

O clone usado pelo aluno é ~/projeto_pp_integracao, no Ubuntu/WSL2.
O diretório antigo no Windows estava associado a outro repositório superior;
não presumir seu remote. Verificar pwd, git status -sb, branch e git remote -v.
O assistente de revisão não controla automaticamente o computador do aluno.
Distinguir comandos preparados de comandos realmente executados por ele.

## Construção e execução

make compila as três versões, perfilador histórico, dois validadores e
o novo auxiliar de Amdahl, totalizando sete executáveis após este fechamento.
O coletor compila separadamente os programas usados e não altera os fontes.
Docker: docker compose run --rm pp-lab, pasta de trabalho /lab.
O laço principal, não a geração/distribuição inicial, é o recorte temporal
usado nos speedups principais. Allreduce por iteração entra no tempo MPI.

## Regras de trabalho

1. Ler README, estado, resultados e protocolo antes de modificar.
2. Preservar autoria real, fontes originais, CSVs brutos, logs e metadados.
3. Novos ensaios usam novas pastas; nunca reescrever silenciosamente históricos.
4. Repetir validações relevantes se mudar matemática, sincronização ou fontes.
5. Interpretar resultados com dispersão, SMT, recorte temporal e hardware.
   Não atribuir causalidade sem evidência isolada.
6. Não fazer push --force, publicação direta na main ou merges sem revisão.
7. Não inventar autoria/commits; AUTORES lista responsabilidades designadas.
8. Não registrar tokens, senhas ou outros segredos no repositório/logs.
9. Atualizar documentação e handoff ao encerrar uma tarefa.

## Pendências

Aplicar/registrar o fechamento, publicar a branch e revisar/integrar o PR;
enviar o link ao professor até 12/11/2026. Preparar demonstração e arguição
cruzada em 19 ou 26/11. O teste no laboratório não foi confirmado.
A ausência de um PDF final separado não é falha: o enunciado exige PDF
de até seis páginas no Marco 1 e repositório/análise documentada no Marco 2.
