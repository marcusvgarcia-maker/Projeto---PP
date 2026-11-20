
# Estado atual — fechamento do Marco 2

Referência: 20/11/2026.

O fechamento documental e experimental do projeto foi desenvolvido
na branch entrega/finalizacao e integrado à main pelo PR #20.

- PR anterior: #19, integração da implementação MPI.
- PR de finalização: #20.
- Estado do PR #20: integrado (merged).
- Commit de integração na main: 35d1005.
- Commit da campanha experimental: 66e2e16.

## Estado das atividades

| Item | Evidência | Estado |
|---|---|---|
| Baseline sequencial | Fonte original preservado | Implementado |
| OpenMP | Implementação e validações individuais | Aprovado nos casos testados |
| MPI | Implementação integrada pelo PR #19 | Aprovado nos casos testados |
| Docker | Ubuntu 24.04.5, G++ 13.3.0, MPI 4.1.6 e Matplotlib 3.6.3 | Executado |
| Compilação do núcleo | Executáveis compilados no Docker | Confirmada |
| Perfilador adicional | Compilado pelo coletor e validado por centroides | Confirmado |
| Validação OpenMP | 9/9 comparações individuais | Aprovado nos casos testados |
| Validação MPI | 33/33 comparações, erro máximo 0,0 | Aprovado nos casos testados |
| Escalabilidade forte | 105 medições, 21 configurações | Conferida |
| Escalabilidade fraca | 30 medições, 6 configurações | Conferida |
| Perfilamento / Amdahl | 15 medições e 18 previsões | Calculado e discutido |
| Dados e logs | 150 checksums consistentes e 190 subprocessos com retorno zero | Conferidos |
| Gráficos | Onze PNGs na pasta de análise | Gerados |
| Documentação final | README, protocolo, arquitetura, resultados e demonstração | Integrada |
| Publicação da finalização | PR #20 integrado à main | Concluída |
| Envio do link ao professor | Depende de confirmação do grupo | A confirmar |
| Apresentação / seminário | Depende da escala e confirmação do grupo | A confirmar |

## Resultado principal

Para N=5 milhões, quatro workers:

- OpenMP: speedup de 1,303× e eficiência de 32,6%.
- MPI: speedup de 1,649× e eficiência de 41,2%.

Esses valores consideram o tempo das iterações.

Considerando a duração externa, OpenMP-4 apresentou média menor
que MPI-4 nesse experimento.

O relatório final apresenta os recortes temporais, a dispersão,
a escalabilidade fraca, o modelo de Amdahl e as limitações
das conclusões.

Consulte [RESULTADOS_FINAIS_DOCKER.md](RESULTADOS_FINAIS_DOCKER.md).

## Cuidados e limitações

Não misturar baselines de campanhas diferentes, não substituir
dados históricos e não apresentar o limite formal de Amdahl
como previsão de desempenho do hardware.

As observações manuais de energia e carga não foram registradas.

Uma nova coleta poderia reduzir incertezas, mas a campanha recebida
foi preservada integralmente.

O alvo amdahl foi acrescentado ao Makefile para incluir o auxiliar
no make padrão. Os fontes de produção e o perfilador utilizado
na campanha permaneceram idênticos.

O histórico integrado está disponível no GitHub. O arquivo AUTORES.md
declara as frentes designadas, mas não comprova individualmente
a autoria de cada arquivo.

O grupo deve registrar sua participação efetiva e preparar
todos os integrantes para a arguição.
