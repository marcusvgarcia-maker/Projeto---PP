# Demonstração e arguição cruzada

Planejamento para aproximadamente nove minutos de demonstração e nove de
arguição, conforme o enunciado. Data do grupo: 19 ou 26/11, conforme a escala.
O teste no laboratório deve ser feito quando houver acesso; não foi confirmado.

## Preparação

Ter o link da versão final, o repositório disponível e um terminal na raiz.
Em Linux nativo do laboratório, conferir g++, mpirun e nproc; executar make.
No Docker, abrir o serviço pp-lab e trabalhar em /lab. O compilador do
laboratório pode diferir do usado na campanha; não prometer tempos idênticos.

## Sequência ao vivo

1. Apresentar o problema, a referência sequencial e a divisão formal das frentes.
2. Mostrar o baseline executando e o checksum de referência.
3. Mostrar OpenMP, suas regiões e a redução manual; executar e comparar resultado.
4. Mostrar MPI, Scatterv e Allreduce; executar com vários processos.
5. Abrir o gráfico medido e explicar speedup, eficiência, Amdahl e limites.

Comandos sugeridos, com entrada grande que demonstrou aceleração:

~~~bash
./build/10_kmeans_base 5000000 8 20
OMP_NUM_THREADS=4 OMP_DYNAMIC=FALSE OMP_PROC_BIND=FALSE ./build/10_kmeans_omp 5000000 8 20
mpirun --oversubscribe --bind-to none -np 4 ./build/10_kmeans_mpi 5000000 8 20
~~~

Checksum esperado: 8099.9055. Uma execução ao vivo comprova funcionamento
e pode ilustrar desempenho; a evidência estatística é a campanha com repetições.
Escolher a quantidade de workers de acordo com os recursos da máquina usada.

Gráfico: [speedup forte, N=5 milhões](../resultados/campanha_docker_20261111_181418/analise/speedup_forte_N5000000.png).
O baseline médio da campanha é 1,957904 s; OpenMP-4 1,503139 s
(1,303×); MPI-4 1,187470 s (1,649×), medindo as iterações.

## Pontos que todos devem saber explicar

- O que significam N, K e IT; por que há iterações fixas e distância ao quadrado.
- Por que a atribuição é independente por ponto e iterações dependem dos centroides anteriores.
- Como acumuladores privados e barreiras evitam corridas no OpenMP.
- Por que schedule(static) é adequado ao custo regular por ponto.
- Por que MPI precisa reunir somas/contagens globais; diferença entre Reduce e Allreduce.
- Como Scatterv trata N não divisível e ranks sem pontos.
- Como preservar centroides de clusters vazios.
- Por que checksum é triagem e comparação individual é evidência mais detalhada.
- Como calcular speedup e eficiência, forte e fraca.
- Por que f inclui atribuição e acumulação, e por que o limite ideal é diferente do observado.
- Por que quatro processadores lógicos não são quatro núcleos físicos.
- Por que MPI teve menor tempo iterativo, mas maior duração externa que OpenMP no maior N.
- Por que a eficiência fraca MPI-2 de 111,92% não demonstra ganho superlinear estável.

A defesa é individual, sobre uma frente de outro integrante. Conforme o
enunciado, é sem apoio de colegas ou IA, com consulta ao próprio repositório.
O uso de IA no desenvolvimento é permitido; o grupo precisa compreender
e defender efetivamente o código e os resultados apresentados.
