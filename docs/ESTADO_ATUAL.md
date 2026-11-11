# Estado atual — fechamento do Marco 2

Referência: 11/11/2026, após recebimento da campanha Docker do aluno.
Commit medido: 66e2e16ab971cdadb98d683c3ce316ef79889af6, branch entrega/finalizacao.
Este documento está preparado para aplicação; não comprova publicação no GitHub.

| Item | Evidência | Estado |
|---|---|---|
| Baseline, OpenMP e MPI | Fontes preservados; MPI integrado à main pelo PR #19 | Implementados |
| Docker | Ubuntu 24.04.5, G++ 13.3.0, MPI 4.1.6, Matplotlib 3.6.3 | Executado pelo aluno |
| Compilação do núcleo | Seis executáveis compilados no Docker antes da campanha | Confirmada |
| Perfilador adicional | Compilado pelo coletor e validado por centroides em três N | Confirmado |
| OpenMP | 9/9 validações individuais anteriores no Docker | Aprovado nos casos testados |
| MPI | 33/33 validações anteriores, erro máximo 0,0 | Aprovado nos casos testados |
| Forte | 105 medições, 21 configurações | Conferida |
| Fraca OpenMP e MPI | 30 medições, 6 configurações | Conferida |
| Perfilamento / Amdahl | 15 medições, 3 f estimados e 18 previsões | Calculado e discutido |
| Dados e logs | 150 checksums consistentes; 190 subprocessos com retorno zero | Conferidos |
| Gráficos | Onze PNGs na pasta de análise | Gerados |
| Documentação final | README, protocolo, arquitetura, resultados e demonstração | Preparada neste patch |
| Publicação da finalização | Branch não aparece na última consulta ao GitHub | Pendente |
| Entrega do link | Canal e envio pelo aluno | Pendente |
| Laboratório / seminário | Nenhuma execução no laboratório relatada | Preparação pendente |

## Resultado principal

Para N=5 milhões, quatro workers: OpenMP 1,303×,
eficiência 32,6%; MPI 1,649×,
eficiência 41,2%, medindo as iterações.
Considerando a duração externa, OpenMP-4 teve média menor que MPI-4.
O [relatório final](RESULTADOS_FINAIS_DOCKER.md) apresenta esses recortes,
dispersão, fraca, Amdahl e limites de inferência.

## Cuidados restantes

Não misturar baselines de campanhas diferentes, não substituir dados históricos
e não apresentar o enorme limite formal de Amdahl como previsão de hardware.
Observações manuais de energia/carga não foram registradas. Uma nova coleta
poderia reduzir incerteza, mas a campanha recebida foi mantida integralmente.

O alvo amdahl foi acrescentado ao Makefile final para incluir o auxiliar
no make padrão; os fontes de produção e o perfilador usado na campanha
permanecem idênticos. O Makefile exato da coleta está arquivado em fontes/.

O histórico integrado consultado está concentrado no perfil do proprietário.
AUTORES declara as frentes designadas, não comprova a autoria individual de
cada arquivo. O grupo deve registrar sua participação efetiva e preparar
todos os integrantes para a arguição cruzada.
