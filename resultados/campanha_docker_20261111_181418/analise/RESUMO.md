# Resultados da campanha Docker

Inicio da coleta: 2026-11-11T18:14:18.780992-03:00
Commit informado pelas referencias Git: 66e2e16ab971cdadb98d683c3ce316ef79889af6

## Escopo

Tempos usados nos calculos: iteracoes de Lloyd reportadas pelos programas.
Geracao, distribuicao inicial MPI e lancamento ficam fora desse cronometro.
A duracao externa dos processos tambem foi registrada, mas nao entra no speedup.
As reducoes MPI de cada iteracao entram no tempo medido.

## Escalabilidade forte

| N | Versao | Workers | Media (s) | Desvio (s) | Speedup | Eficiencia (%) |
|---:|---|---:|---:|---:|---:|---:|
| 100000 | mpi | 1 | 0.042376 | 0.005659 | 0.853 | 85.3 |
| 100000 | mpi | 2 | 0.035476 | 0.020581 | 1.018 | 50.9 |
| 100000 | mpi | 4 | 0.083889 | 0.089532 | 0.431 | 10.8 |
| 100000 | openmp | 1 | 0.046986 | 0.010830 | 0.769 | 76.9 |
| 100000 | openmp | 2 | 0.044028 | 0.007287 | 0.821 | 41.0 |
| 100000 | openmp | 4 | 0.104329 | 0.074248 | 0.346 | 8.7 |
| 100000 | sequencial | 1 | 0.036132 | 0.004044 | 1.000 | 100.0 |
| 1000000 | mpi | 1 | 0.394803 | 0.036564 | 0.934 | 93.4 |
| 1000000 | mpi | 2 | 0.294183 | 0.060663 | 1.254 | 62.7 |
| 1000000 | mpi | 4 | 0.250326 | 0.081642 | 1.473 | 36.8 |
| 1000000 | openmp | 1 | 0.380309 | 0.029050 | 0.970 | 97.0 |
| 1000000 | openmp | 2 | 0.329321 | 0.005730 | 1.120 | 56.0 |
| 1000000 | openmp | 4 | 0.358279 | 0.041297 | 1.029 | 25.7 |
| 1000000 | sequencial | 1 | 0.368838 | 0.019859 | 1.000 | 100.0 |
| 5000000 | mpi | 1 | 2.094306 | 0.249041 | 0.935 | 93.5 |
| 5000000 | mpi | 2 | 1.325666 | 0.087547 | 1.477 | 73.8 |
| 5000000 | mpi | 4 | 1.187470 | 0.076018 | 1.649 | 41.2 |
| 5000000 | openmp | 1 | 1.979156 | 0.110273 | 0.989 | 98.9 |
| 5000000 | openmp | 2 | 1.631648 | 0.078971 | 1.200 | 60.0 |
| 5000000 | openmp | 4 | 1.503139 | 0.052985 | 1.303 | 32.6 |
| 5000000 | sequencial | 1 | 1.957904 | 0.080485 | 1.000 | 100.0 |

## Estimativa de Amdahl

f = (media da atribuicao + media da acumulacao) / media do total perfilado.
S(P) = 1 / ((1-f) + f/P); limite ideal = 1/(1-f).

| N | f estimado | Fracao restante | Limite ideal |
|---:|---:|---:|---:|
| 100000 | 0.99855426 | 0.00144574 | 691.69 |
| 1000000 | 0.99978049 | 0.00021951 | 4555.70 |
| 5000000 | 0.99995750 | 0.00004250 | 23527.17 |

A estimativa usa uma copia sequencial instrumentada e validada por centroides.
Inicializacao de acumuladores, atualizacao, desalocacao e instrumentacao ficam no restante.
Esse e um modelo ideal do trabalho potencialmente paralelo; nao e uma fracao efetiva
medida das implementacoes OpenMP/MPI nem uma promessa de aceleracao real.
A instrumentacao pode alterar os custos observados, sobretudo os trechos pequenos.
O modelo nao incorpora criacao de threads/processos, coletivas, banda de memoria ou SMT.
Diferencas para a previsao precisam ser discutidas com base nos dados, sem atribuir
causalidade exclusiva a qualquer desses fatores.

## Escalabilidade fraca

E_fraca(P) = T(1,N0)/T(P,P*N0)*100, usando a referencia de cada modelo.

| N | Versao | Workers | Media (s) | Desvio (s) | Eficiencia fraca (%) |
|---:|---|---:|---:|---:|---:|
| 1000000 | mpi | 1 | 0.705012 | 0.356813 | 100.0 |
| 1000000 | openmp | 1 | 0.427227 | 0.084937 | 100.0 |
| 2000000 | mpi | 2 | 0.629901 | 0.143847 | 111.9 |
| 2000000 | openmp | 2 | 0.707291 | 0.059715 | 60.4 |
| 4000000 | mpi | 4 | 1.462157 | 0.741375 | 48.2 |
| 4000000 | openmp | 4 | 1.379823 | 0.178997 | 31.0 |

## Limites da interpretacao

Medias, medianas e desvios descrevem as repeticoes desta sessao.
Os graficos nao demonstram diferencas estatisticamente significativas.
Registre carga concorrente e energia da maquina junto aos metadados automaticos.
Na maquina informada pelo grupo ha 2 nucleos e 4 processadores logicos;
quatro workers nao equivalem a quatro nucleos fisicos.
As validacoes 9/9 OpenMP e 33/33 MPI foram executadas separadamente pelo grupo.
Esta campanha confere checksums em todas as execucoes e valida o novo perfilador
contra todos os centroides do sequencial para cada tamanho perfilado.
