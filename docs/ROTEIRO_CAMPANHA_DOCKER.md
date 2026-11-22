# Campanha conjunta no Docker e estimativa de Amdahl

Este documento descreve o protocolo utilizado na campanha experimental de K-means executada em 11/11/2026 e orienta a reprodução de novas campanhas independentes.

A campanha original foi executada no commit `66e2e16`, com 105 medições fortes, 30 fracas e 15 de perfilamento. Seus resultados foram conferidos e estão preservados no repositório.

A análise final está disponível em [RESULTADOS_FINAIS_DOCKER.md](RESULTADOS_FINAIS_DOCKER.md).

## 1. Registro do ambiente da campanha original

As informações abaixo representam o ambiente utilizado na preparação e execução da campanha de 11/11/2026. Não devem ser interpretadas como uma descrição do ambiente atual do aluno.

- Branch utilizada: `entrega/finalizacao`.
- Commit de referência inicial: `852af1d`.
- Dockerfile, docker-compose.yml e regras de exclusão registrados nesse commit.
- MPI integrado à `main` pelo PR #19, commit de merge `d9fb659`.
- Docker: quatro CPUs visíveis no ambiente.
- Imagem: Ubuntu 24.04.5 LTS.
- CPU informada: Intel Core i5-5300U, dois núcleos físicos e quatro processadores lógicos.
- Memória visível no Linux: 8.069.680 kB, aproximadamente 7,70 GiB.
- G++ 13.3.0.
- Open MPI 4.1.6.
- Matplotlib 3.6.3.
- Seis executáveis compilados na preparação original da campanha.
- OpenMP: 9/9 comparações individuais de centroides aprovadas.
- MPI: 33/33 comparações aprovadas, com maior erro absoluto de 0,0.

A memória informada pelo Linux representa a memória visível naquele ambiente. Não identifica necessariamente a RAM física instalada no Windows nem substitui um eventual limite de memória do contêiner.

Posteriormente, o alvo `amdahl` foi incorporado ao Makefile principal, fazendo com que o `make` padrão passasse a gerar sete executáveis.

## 2. Componentes utilizados na campanha

Os principais arquivos utilizados foram:

- `scripts/medir_campanha_docker.py`: coleta conjunta das medições e geração de metadados.
- `scripts/analisar_campanha_docker.py`: cálculo das estatísticas, geração de gráficos e estimativa de Amdahl.
- `perfilamento/10_kmeans_amdahl.cpp`: cópia instrumentada adicional do programa sequencial.

O baseline original e as implementações OpenMP e MPI foram preservados.

Os arquivos históricos de resultados não foram sobrescritos.

## 3. Reprodução de uma nova campanha

A campanha descrita neste documento já foi executada. Os procedimentos desta seção destinam-se à realização de novas campanhas independentes.

Para novas alterações no projeto, utilizar a `main` atualizada como ponto de partida, seguindo as orientações de organização e revisão por Pull Request descritas no `README.md` e no `AGENTS.md`.

Antes de iniciar uma nova coleta:

1. Verificar o estado do repositório e dos arquivos utilizados.
2. Preparar o ambiente Docker.
3. Confirmar a disponibilidade dos compiladores, bibliotecas e ferramentas necessárias.
4. Conectar o computador à energia.
5. Encerrar trabalhos concorrentes que possam afetar as medições.
6. Registrar as condições de execução que possam influenciar os resultados.

Com a pasta de trabalho do contêiner em `/lab`, executar:

```bash
python3 scripts/medir_campanha_docker.py --observacoes "descreva as condicoes reais"
```

O parâmetro `--observacoes` permite registrar as condições reais da nova coleta.

O script recompila os programas utilizados com `-O2 -std=c++17`.

- OpenMP utiliza `-fopenmp` pelo Makefile.
- MPI utiliza o compilador configurado no Makefile.
- O perfilador adicional é compilado separadamente pelo coletor.
- Matplotlib é necessário para a análise automática e geração dos gráficos.

O novo perfilador não substitui o perfilador histórico.

## 4. Protocolo experimental

### 4.1. Escalabilidade forte

Configurações utilizadas:

- N: 100.000, 1.000.000 e 5.000.000 pontos.
- K: 8 clusters.
- IT: 20 iterações.
- Versões: sequencial, OpenMP e MPI.
- Workers: 1, 2 e 4 para OpenMP e MPI.
- Repetições: cinco rodadas medidas por configuração.
- Aquecimento: uma execução descartada por configuração.

A ordem das variantes foi embaralhada em cada rodada, utilizando uma semente registrada nos metadados.

O total foi de 105 medições:

- 21 configurações.
- Cinco repetições por configuração.

### 4.2. Escalabilidade fraca

Configurações utilizadas:

- N = 1.000.000 × número de workers.
- K = 8.
- IT = 20.
- Versões: OpenMP e MPI.
- Workers: 1, 2 e 4.
- Repetições: cinco por configuração.

Cada modelo utiliza sua própria referência com um worker.

O total foi de 30 medições.

### 4.3. Perfilamento e Amdahl

Foram realizadas 15 medições de perfilamento, distribuídas em três tamanhos de entrada e cinco repetições por tamanho.

Houve aquecimentos e verificação prévia dos centroides do perfilador em relação ao sequencial.

O perfilamento separa duas fases:

- Atribuição: associação de cada ponto ao centroide mais próximo.
- Acumulação: soma das coordenadas e contagem de pontos de cada cluster.

As duas fases são potencialmente paralelizáveis.

### 4.4. Configurações de execução

- Tempos principais: somente as iterações reportadas pelo programa.
- Duração externa: registrada separadamente para cada subprocesso.
- OpenMP: `OMP_DYNAMIC=FALSE` e `OMP_PROC_BIND=FALSE`.
- `GOMP_CPU_AFFINITY` removida dos subprocessos.
- MPI: `--oversubscribe --bind-to none`.
- Processos MPI executados na mesma máquina.

As escolhas de configuração ficam registradas nos metadados.

A campanha representa execução em uma única máquina. Portanto, não comprova desempenho em um cluster distribuído.

## 5. Saídas e preservação dos dados

Cada nova execução cria uma pasta exclusiva, com data, dentro de `resultados/`.

O padrão de organização é:

`resultados/campanha_docker_DATA/`

Se o destino informado já existir, o script recusa sobrescrevê-lo.

Os arquivos principais são:

| Arquivo | Conteúdo |
|---|---|
| `forte.csv` | Medições de escalabilidade forte |
| `fraca.csv` | Medições de escalabilidade fraca |
| `perfilamento.csv` | Resultados do perfilamento |
| `metadados.json` | Configurações e informações do ambiente |

As demais pastas são:

- `logs/`: comandos executados e respectivas saídas.
- `fontes/`: cópias dos fontes efetivamente utilizados.
- `analise/`: resumos CSV, gráficos e `RESUMO.md`.

Ao final, um ZIP com sufixo `_para_enviar.zip` é criado ao lado da pasta da campanha.

Checksums inconsistentes, comandos com erro, timeouts ou amostras incompletas impedem a conclusão automática. Os dados parciais permanecem identificados como tais.

Os resultados históricos devem ser preservados. Nenhuma nova campanha deve sobrescrever os dados anteriores.

## 6. Hipótese de Amdahl

A estimativa de Amdahl utiliza os tempos médios obtidos pelo perfilador sequencial instrumentado.

Para cada tamanho de entrada:

```text
f = (tempo médio de atribuição + tempo médio de acumulação) / tempo médio total perfilado

S(P) = 1 / ((1-f) + f/P)

S(infinito) = 1/(1-f)
```

Em que:

- `f` representa a fração estimada do tempo do perfilador correspondente às duas fases potencialmente paralelizáveis.
- `P` representa o número de workers.
- `S(P)` representa o speedup ideal estimado para P workers.
- `S(infinito)` representa o limite formal do modelo quando o número de workers tende ao infinito.

A parcela restante inclui inicialização dos acumuladores, atualização dos centroides, desalocação, controle e instrumentação.

Essa estimativa é um modelo ideal do código sequencial instrumentado e está sujeita ao custo do próprio perfilamento.

O modelo não mede diretamente a fração serial efetiva do OpenMP ou MPI. Também não incorpora automaticamente o custo das reduções, criação de threads, contenção de memória ou efeitos de SMT.

As diferenças entre o modelo ideal e os resultados medidos precisam ser discutidas.

O percentual histórico de 87,38% correspondia somente à atribuição em outra execução. Não deve ser utilizado automaticamente como fração paralelizável total.

## 7. Fechamento da campanha original

A campanha experimental foi executada em 11/11/2026. Seus resultados foram recebidos, conferidos e documentados.

Os dados, scripts, fontes utilizados, metadados, logs e gráficos estão preservados em:

`resultados/campanha_docker_20261111_181418/`

A discussão dos resultados, incluindo speedup, eficiência, escalabilidade fraca, variabilidade e modelo de Amdahl, está disponível em [RESULTADOS_FINAIS_DOCKER.md](RESULTADOS_FINAIS_DOCKER.md).

### Histórico de integração

A finalização do projeto foi desenvolvida na branch `entrega/finalizacao` e integrada à `main` pelo PR #20.

- Pull Request: https://github.com/marcusvgarcia-maker/Projeto---PP/pull/20
- Estado: integrado (merged).
- Commit de integração: `35d1005`.
- Commit da campanha experimental: `66e2e16`.

O código e a documentação referentes ao fechamento da entrega fazem parte da `main` desde a integração do PR #20.

### Resultados e limitações

As comparações de desempenho devem considerar:

- O ambiente de execução.
- A configuração e a quantidade de workers.
- A variabilidade das medições.
- O recorte temporal utilizado.
- As limitações de hardware e de memória.

Os resultados desta campanha representam as condições registradas em 11/11/2026. Novas medições devem ser tratadas como campanhas independentes, preservando integralmente os dados anteriores.
