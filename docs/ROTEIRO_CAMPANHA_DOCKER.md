# Campanha conjunta no Docker e estimativa de Amdahl

Campanha executada pelo grupo em 11/11/2026, commit 66e2e16.
Foram recebidos e conferidos 105 registros fortes, 30 fracos e 15 de perfilamento.
A analise final esta em RESULTADOS_FINAIS_DOCKER.md. Este documento preserva o
protocolo e permite novas campanhas independentes.

## Estado de entrada confirmado pelo aluno

- Branch local: entrega/finalizacao, commit 852af1d; arvore de trabalho limpa.
- Dockerfile, docker-compose.yml e regras de exclusao registrados nesse commit.
- MPI ja integrado a main pelo PR 19; commit de merge d9fb659.
- Docker: 4 CPUs visiveis; imagem Ubuntu 24.04.5 LTS.
- CPU informada: Intel Core i5-5300U, 2 nucleos e 4 processadores logicos.
- Memoria total informada pelo Linux: 8069680 kB, cerca de 7,70 GiB.
  Esse valor descreve o ambiente Linux; nao identifica a RAM fisica do Windows
  nem substitui um eventual limite de memoria do conteiner.
- G++ 13.3.0, Open MPI 4.1.6, Matplotlib 3.6.3.
- Seis executaveis compilados no conteiner.
- OpenMP: 9/9 comparacoes de centroides aprovadas.
- MPI: 33/33 comparacoes aprovadas, maior erro absoluto 0,0.

## Arquivos novos

- scripts/medir_campanha_docker.py: coleta conjunta e metadados.
- scripts/analisar_campanha_docker.py: estatisticas, graficos e modelo de Amdahl.
- perfilamento/10_kmeans_amdahl.cpp: copia instrumentada adicional do sequencial.

O baseline e as implementacoes OpenMP/MPI permanecem inalterados.
Os arquivos historicos de resultados nao sao sobrescritos.

## Execucao

Copie os arquivos para a raiz do projeto, respeitando as subpastas do pacote.
Registre as mudancas reais na branch de finalizacao antes da campanha.
Dentro do conteiner, com a pasta de trabalho em /lab:

~~~bash
python3 scripts/medir_campanha_docker.py
~~~

O script recompila os programas utilizados com -O2 -std=c++17.
OpenMP recebe -fopenmp pelo Makefile. O MPI usa o compilador do Makefile.
O novo perfilador e compilado separadamente pelo coletor; nao substitui o
perfilador historico. Matplotlib e necessario para a analise automatica.

Antes da coleta, conecte o computador a energia e encerre trabalhos concorrentes
que possam afetar as medicoes. Registre qualquer condicao que nao possa controlar.

## Protocolo padrao

- Forte: N=100000,1000000,5000000; K=8; IT=20.
- Um sequencial e OpenMP/MPI com 1, 2 e 4 workers na mesma campanha.
- Cinco rodadas medidas e um aquecimento descartado por configuracao.
- Ordem das variantes embaralhada em cada rodada, com semente registrada.
- Total forte: 105 registros medidos.
- Fraca: N=1000000*workers, K=8, IT=20, para OpenMP e MPI.
  Sao 30 registros medidos, com referencia propria de cada modelo em worker 1.
- Perfilamento: 15 registros medidos, mais aquecimentos e verificacao previa
  dos centroides do perfilador para os tres tamanhos.
- Tempos principais: apenas as iteracoes reportadas pelo programa.
- A duracao externa de cada subprocesso e registrada separadamente.
- OMP_DYNAMIC=FALSE, OMP_PROC_BIND=FALSE; GOMP_CPU_AFFINITY removida dos subprocessos.
- MPI: --oversubscribe --bind-to none. Essas escolhas ficam nos metadados.
  O experimento usa processos na mesma maquina; nao comprova desempenho em cluster.

## Saidas

Cada execucao cria uma pasta NOVA com data em resultados/campanha_docker_DATA.
Se um destino informado ja existir, o script recusa sobrescreve-lo.

Os arquivos principais sao forte.csv, fraca.csv, perfilamento.csv e metadados.json.
A pasta logs guarda comandos e saidas; fontes guarda os fontes efetivamente usados.
analise contem resumos CSV, graficos e RESUMO.md. Ao final, um ZIP com sufixo
_para_enviar.zip e criado ao lado da pasta da campanha.

Checksums inconsistentes, comandos com erro, timeout e amostras incompletas
impedem a conclusao automatica. Dados parciais permanecem identificados como tais.

## Hipotese de Amdahl

Para cada N:

~~~text
f = (tempo medio de atribuicao + tempo medio de acumulacao) / tempo total medio
S(P) = 1 / ((1-f) + f/P)
S(infinito) = 1/(1-f)
~~~

Os dois lacos sobre pontos sao potencialmente paralelos. A parcela restante
inclui inicializacao dos acumuladores, atualizacao dos centroides, desalocacao,
controle e instrumentacao. A estimativa e um modelo ideal do codigo sequencial
instrumentado, sujeito ao custo do proprio perfilamento.

O modelo nao mede a fracao serial efetiva do OpenMP ou do MPI. Nao incorpora
automaticamente o custo das reducoes, criacao de threads, contencao de memoria
ou efeitos de SMT. As diferencas entre modelo e medicoes exigem discussao.
O percentual historico de 87,38% era somente atribuicao e nao deve ser usado
automaticamente como toda a fracao paralelizavel.

## Fechamento da entrega

A campanha experimental foi executada em 11/11/2026 e seus
resultados foram recebidos, conferidos e documentados.

Os dados, scripts, fontes utilizados, metadados, logs e gráficos
estão preservados em:

resultados/campanha_docker_20261111_181418/

A discussão dos resultados, incluindo speedup, eficiência,
escalabilidade fraca, variabilidade e modelo de Amdahl,
está disponível em:

docs/RESULTADOS_FINAIS_DOCKER.md

### Histórico de publicação

A finalização do projeto foi desenvolvida na branch
entrega/finalizacao e integrada à main pelo PR #20.

- Pull Request: https://github.com/marcusvgarcia-maker/Projeto---PP/pull/20
- Estado: integrado (merged).
- Commit de integração: 35d1005.
- Commit da campanha experimental: 66e2e16.

O código e a documentação referentes ao fechamento da entrega
já fazem parte da main.

### Preservação dos experimentos

Os resultados históricos devem ser preservados.

Novas campanhas devem utilizar diretórios exclusivos,
sem sobrescrever os dados anteriores.

As comparações de desempenho devem considerar o ambiente,
a configuração dos workers, a variabilidade das medições
e o recorte temporal utilizado.

O prazo informado para o Marco 2 foi no dia da apresentação 26/11/2026.
Eventuais novas solicitações do professor devem ser registradas
e tratadas em alterações posteriores.

O prazo de entrega do Marco 2 foi prorrogado pelo professor para o dia da apresentação do grupo, em 26/11/2026.

A apresentação será no dia 26/11.

