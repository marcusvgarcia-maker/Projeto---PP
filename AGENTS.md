# AGENTS.md — continuidade do projeto K-means

## Estado confirmado em 22/11/2026

Projeto CCO085, IESB 2026/2, problema 10.

O PR #19 integrou a implementação MPI à branch `main`, no commit `d9fb659`.

A finalização documental e experimental foi desenvolvida na branch `entrega/finalizacao` e integrada à `main` pelo PR #20.

- Branch de origem: `entrega/finalizacao`.
- PR de integração: https://github.com/marcusvgarcia-maker/Projeto---PP/pull/20
- Estado do PR: integrado (merged).
- Commit de integração na `main`: `35d1005`.
- Commit da campanha experimental: `66e2e16`.

O PR #21 está aberto para revisão e atualização da documentação. Não considerar suas alterações integradas à `main` até que a integração seja confirmada no GitHub.

A branch `main` contém a versão consolidada até o PR #20.

Fonte principal: `docs/RESULTADOS_FINAIS_DOCKER.md`, `docs/ESTADO_ATUAL.md`, `docs/EXPERIMENTOS.md` e a campanha `resultados/campanha_docker_20261111_181418/`.

Não confundir as campanhas históricas com a coleta Docker final nem com os testes adicionais realizados no laboratório.

## Invariantes obrigatórios

Preservar `sequencial/10_kmeans.cpp` como referência imutável.

Argumentos N/K/IT, padrões 1000000/8/20; LCG `uint64_t` original, semente `2024ULL`; centroides iniciais nos primeiros K pontos; distância euclidiana ao quadrado; desempate por `d < best`; exatamente IT iterações; cluster vazio conserva o centroide anterior.

Não alterar matemática, gerador ou entradas sem autorização e nova análise.

Checksum com quatro casas decimais não comprova individualmente todos os centroides.

## Evidências confirmadas

### Campanha experimental de 11/11/2026

- Docker: Ubuntu 24.04.5, G++ 13.3.0, Open MPI 4.1.6 e Matplotlib 3.6.3.
- CPU informada na campanha: Intel Core i5-5300U, dois núcleos e quatro processadores lógicos.
- Memória visível no Linux: aproximadamente 7,70 GiB; não inferir a RAM física do Windows.
- OpenMP: 9/9 comparações individuais aprovadas.
- MPI: 33/33 comparações individuais aprovadas, erro máximo 0,0.
- Campanha concluída: 105 medições fortes, 30 fracas e 15 de perfilamento.
- 150 checksums consistentes e 190 subprocessos com retorno zero e sem timeout.
- Hashes dos dez fontes/configurações arquivados conferidos.
- Maior N, quatro workers: OpenMP 1,303×; MPI 1,649×, considerando somente o tempo iterativo.
- A duração externa favoreceu OpenMP-4 nesse mesmo caso.
- Amdahl calculado como modelo ideal. Não apresentar f como fração serial efetiva medida do paralelo nem S(infinito) como previsão para o notebook.
- Observações manuais de energia/carga ficaram vazias.

### Testes adicionais no laboratório

Em novembro de 2026, foram realizados testes adicionais no ambiente Docker do laboratório.

- Docker informado: versão 29.3.1.
- Docker Compose informado: versão 5.1.1.
- CPU informada: Intel Core i5-9500 @ 3.00 GHz.
- Memória visível informada pelo Linux: 8.073.716 kB.
- Execução com entrada de referência: checksum `8109.0037`.
- Em uma execução, foram exibidos oito centroides e tempo aproximado de 0,19 segundo.

Esses testes adicionais não devem ser confundidos com a campanha experimental de 11/11.

A execução no laboratório foi realizada, mas não há confirmação de que a validação completa OpenMP 9/9 tenha sido concluída nesse ambiente. Não declarar essa validação como aprovada no laboratório sem o relatório correspondente.

## Onde trabalhar e verificar

O clone usado pelo aluno é `~/projeto_pp_integracao`, no Ubuntu/WSL2.

Na última verificação, o ambiente local informava Ubuntu 26.04.1 LTS e WSL2.

O diretório antigo no Windows estava associado a outro repositório superior; não presumir seu remote.

Antes de qualquer operação Git, verificar:

```bash
pwd
git status -sb
git branch --show-current
git remote -v
```

O assistente de revisão não controla automaticamente o computador do aluno. Distinguir comandos preparados de comandos realmente executados por ele.

## Construção e execução

`make` compila as três versões, o perfilador histórico, dois validadores e o novo auxiliar de Amdahl, totalizando sete executáveis após este fechamento.

O coletor compila separadamente os programas utilizados e não altera os fontes.

Docker: `docker compose run --rm pp-lab`, pasta de trabalho `/lab`.

O laço principal, e não a geração/distribuição inicial, é o recorte temporal usado nos speedups principais. As operações Allreduce por iteração entram no tempo MPI.

## Regras de trabalho

1. Ler README, estado, resultados e protocolo antes de modificar.
2. Preservar autoria real, fontes originais, CSVs brutos, logs e metadados.
3. Novos ensaios devem utilizar pastas exclusivas; nunca reescrever silenciosamente os históricos.
4. Repetir validações relevantes se houver mudanças na matemática, sincronização ou fontes.
5. Interpretar resultados considerando dispersão, SMT, recorte temporal e hardware. Não atribuir causalidade sem evidência isolada.
6. Não fazer `push --force`, publicação direta na `main` ou merges sem revisão.
7. Não inventar autoria ou commits; `AUTORES.md` lista responsabilidades designadas.
8. Não registrar tokens, senhas ou outros segredos no repositório/logs.
9. Atualizar a documentação e o handoff ao encerrar uma tarefa.

## Pendências

- Concluir a revisão documental do PR #21 e confirmar sua integração à `main`.
- Confirmar se o link do repositório foi efetivamente enviado ao professor.
- Preparar a apresentação e a arguição previstas para 26/11/2026.
- Registrar eventuais observações ou correções solicitadas pelo professor.
- Não declarar a validação completa OpenMP 9/9 no laboratório sem evidência correspondente.
- Caso sejam realizadas novas alterações depois da integração, criar uma nova branch a partir da `main` atualizada e submeter as mudanças por Pull Request.

O PR #20 já foi integrado. Portanto, não considerar a publicação da branch `entrega/finalizacao` ou a integração do PR #20 como pendências.

A ausência de um PDF final separado não é necessariamente uma falha: o enunciado exige PDF de até seis páginas no Marco 1 e repositório/análise documentada no Marco 2.
