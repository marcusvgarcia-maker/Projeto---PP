# Estado atual — projeto K-means

Referência: 22/11/2026.

## Histórico de integração

O projeto foi desenvolvido e consolidado por etapas:

- PR #19: integração da implementação MPI à branch `main`, commit `d9fb659`.
- PR #20: integração da finalização documental e experimental à branch `main`.
- Commit de integração do PR #20: `35d1005`.
- Commit da campanha experimental: `66e2e16`.

O PR #20 está integrado (merged).

O PR #21 está aberto para revisão e atualização da documentação. Suas alterações ainda não fazem parte da branch `main`.

A branch `main` representa a versão consolidada do projeto até o PR #20.

## Estado das atividades

| Item | Evidência | Estado |
|---|---|---|
| Baseline sequencial | Fonte original preservado em `sequencial/10_kmeans.cpp` | Implementado |
| OpenMP | Implementação e validações individuais | Aprovado nos casos testados |
| MPI | Implementação integrada pelo PR #19 | Aprovado nos casos testados |
| Campanha Docker oficial | Ubuntu 24.04.5, G++ 13.3.0, Open MPI 4.1.6 e Matplotlib 3.6.3 | Executada |
| Compilação do núcleo | Executáveis compilados no Docker | Confirmada |
| Perfilador adicional | Compilado pelo coletor e validado por comparação de centroides | Confirmado |
| Validação OpenMP da campanha | 9/9 comparações individuais | Aprovada nos casos testados |
| Validação MPI da campanha | 33/33 comparações, erro máximo 0,0 | Aprovada nos casos testados |
| Escalabilidade forte | 105 medições, 21 configurações | Conferida |
| Escalabilidade fraca | 30 medições, 6 configurações | Conferida |
| Perfilamento / Amdahl | 15 medições de perfilamento e 18 previsões | Calculado e discutido |
| Dados e logs | 150 medições com checksums conferidos e 190 subprocessos com retorno zero | Conferidos |
| Gráficos | Onze arquivos PNG na pasta de análise | Gerados |
| Documentação do fechamento | Integrada pelo PR #20; atualização de consistência em andamento no PR #21 | Em revisão |
| Testes adicionais no laboratório | Execução com checksum 8109.0037 e oito centroides apresentados | Execução realizada |
| Envio do link ao professor | Depende de confirmação do grupo | A confirmar |
| Apresentação / seminário | Programada para 26/11/2026, das 8h às 11h | Preparação pendente |

## Resultados principais

A campanha oficial foi executada em 11/11/2026, utilizando N=5.000.000, K=8 e IT=20.

Resultados com quatro workers:

| Versão | Tempo médio das iterações | Speedup | Eficiência |
|---|---:|---:|---:|
| Sequencial | 1,957904 s | 1,000× | — |
| OpenMP | 1,503139 s | 1,303× | 32,6% |
| MPI | 1,187470 s | 1,649× | 41,2% |

Esses valores consideram somente o tempo das iterações.

Considerando a duração externa dos processos, OpenMP-4 apresentou média de 1,602381 s, enquanto MPI-4 apresentou média de 1,877881 s.

Portanto, a comparação depende do recorte temporal utilizado. MPI-4 obteve menor tempo iterativo nesse experimento, mas OpenMP-4 apresentou menor duração externa.

O [relatório final](RESULTADOS_FINAIS_DOCKER.md) apresenta os recortes temporais, a dispersão, a escalabilidade fraca, o modelo de Amdahl e as limitações das conclusões.

## Testes adicionais realizados no laboratório

Além da campanha oficial, foram realizados testes adicionais no ambiente Docker do laboratório.

Ambiente informado:

- Docker 29.3.1.
- Docker Compose 5.1.1.
- CPU Intel Core i5-9500 @ 3.00 GHz.
- Memória visível no Linux: 8.073.716 kB.

Em uma das execuções adicionais, foram apresentados oito centroides, com checksum `8109.0037` e tempo informado de aproximadamente 0,19 segundo.

Essa execução confirma que o programa foi executado no ambiente testado, mas não substitui uma campanha experimental completa.

A validação completa OpenMP 9/9 não foi confirmada nesse ambiente. Portanto, não se deve atribuir a esses testes adicionais a mesma cobertura das validações documentadas na campanha oficial.

Os resultados desses testes não devem ser misturados aos dados da campanha de 11/11/2026.

## Cuidados e limitações

Não misturar baselines de campanhas diferentes, não substituir dados históricos e não apresentar o limite formal de Amdahl como previsão de desempenho do hardware.

As observações manuais de energia e carga não foram registradas na campanha oficial.

Uma nova coleta poderia reduzir incertezas, mas os resultados recebidos foram preservados integralmente.

O alvo `amdahl` foi acrescentado ao Makefile para incluir o auxiliar no processo de compilação padrão. Os fontes de produção e o perfilador utilizado na campanha permaneceram idênticos.

O histórico integrado está disponível no GitHub. O arquivo `AUTORES.md` declara as frentes designadas, mas não comprova individualmente a autoria de cada arquivo.

O grupo deve registrar sua participação efetiva e preparar todos os integrantes para a arguição individual.

## Pendências e próximas ações

- Concluir a revisão documental do PR #21.
- Confirmar a integração do PR #21 à branch `main`.
- Confirmar se o link do repositório foi efetivamente enviado ao professor.
- Preparar a apresentação e a arguição de 26/11/2026.
- Registrar eventuais observações ou correções solicitadas pelo professor.

O prazo do Marco 2 foi prorrogado pelo professor para o dia da apresentação do grupo, em 26/11/2026.
