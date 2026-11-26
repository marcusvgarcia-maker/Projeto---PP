# Demonstração ao vivo e arguição cruzada

Planejamento para aproximadamente nove minutos de demonstração e nove de
arguição, conforme o enunciado.

- **Data da apresentação:** 26/11/2026, das 8h às 11h.
- **Referência principal dos resultados:** campanha Docker oficial em
  [resultados/campanha_docker_20261111_181418](../resultados/campanha_docker_20261111_181418/)
  e análise completa em [RESULTADOS_FINAIS_DOCKER.md](RESULTADOS_FINAIS_DOCKER.md).

## 1. Preparação do ambiente

Ter o repositório aberto em um terminal na raiz do projeto.

- **Em Linux nativo (laboratório ou WSL2):** conferir `g++ --version`, `mpirun --version` e `nproc`.
- **No Docker:** subir o contêiner oficial a partir da raiz do repositório:

```bash
docker compose build pp-lab
docker compose run --rm pp-lab
```

Compilar todos os alvos do zero (7 executáveis em `build/`):

```bash
make clean && make
```

> O hardware e o compilador do laboratório podem diferir da máquina da campanha oficial; a execução ao vivo comprova corretude e aceleração no ambiente atual, enquanto a evidência estatística (média, mediana, desvio-padrão e Amdahl) vem da campanha com repetições.

## 2. Sequência da demonstração ao vivo

1. Apresentar o problema (K-means / algoritmo de Lloyd), a referência sequencial (`sequencial/10_kmeans.cpp`) e a divisão de frentes (`AUTORES.md`).
2. Executar o baseline sequencial e destacar o checksum de referência.
3. Explicar a versão OpenMP (`openmp/10_kmeans.cpp` — `schedule(static)`, barreira implícita entre Fase 1 e Fase 2, acumuladores privados por thread) e executar com 1, 2 e 4 threads.
4. Explicar a versão MPI (`mpi/10_kmeans.cpp` — `MPI_Bcast`, `MPI_Scatterv`, `MPI_Allreduce`) e executar com 1, 2 e 4 processos.
5. (Opcional, se solicitado) Rodar os validadores de corretude comparando centroides/checksums.
6. Abrir os gráficos medidos e discutir speedup, eficiência, escalabilidade fraca, Amdahl e limites.

## 3. Comandos prontos para a demonstração ao vivo

Entrada principal (`N=5.000.000`, `K=8`, `IT=20` — **checksum esperado: `8099.9055`**):

### Baseline sequencial

```bash
./build/10_kmeans_base 5000000 8 20
```

### OpenMP (variando número de threads)

```bash
OMP_NUM_THREADS=1 OMP_DYNAMIC=FALSE OMP_PROC_BIND=FALSE ./build/10_kmeans_omp 5000000 8 20
OMP_NUM_THREADS=2 OMP_DYNAMIC=FALSE OMP_PROC_BIND=FALSE ./build/10_kmeans_omp 5000000 8 20
OMP_NUM_THREADS=4 OMP_DYNAMIC=FALSE OMP_PROC_BIND=FALSE ./build/10_kmeans_omp 5000000 8 20
```

### MPI (variando número de processos)

```bash
mpirun --oversubscribe --bind-to none -np 1 ./build/10_kmeans_mpi 5000000 8 20
mpirun --oversubscribe --bind-to none -np 2 ./build/10_kmeans_mpi 5000000 8 20
mpirun --oversubscribe --bind-to none -np 4 ./build/10_kmeans_mpi 5000000 8 20
```

> Para uma execução ainda mais rápida durante perguntas, usar a entrada padrão `1000000 8 20` (**checksum esperado: `8109.0037`**). Ajustar a quantidade máxima de workers conforme o `nproc` da máquina usada.

### Validação automatizada de corretude (opcional)

Os validadores confirmam igualdade de centroides/checksums entre sequencial, OpenMP e MPI (para preservar os CSVs versionados antes de rodar novamente, faça backup ou restaure com `git checkout -- resultados/validacao_*.csv` ao final):

```bash
./scripts/validar_openmp.sh
./scripts/validar_mpi.sh
python3 scripts/validar_centroides_mpi.py
```

## 4. Gráficos e números de referência da campanha oficial

Números médios da campanha oficial para `N=5.000.000`, `K=8`, `IT=20` (somente tempo das iterações):

- **Sequencial:** `1,957904 s` (`1,000×`)
- **OpenMP (4 threads):** `1,503139 s` — speedup **`1,303×`**, eficiência **`32,6%`**
- **MPI (4 processos):** `1,187470 s` — speedup **`1,649×`**, eficiência **`41,2%`**

Principais gráficos em `resultados/campanha_docker_20261111_181418/analise/`:

- [Speedup forte + curva de Amdahl (N=5M)](../resultados/campanha_docker_20261111_181418/analise/speedup_forte_N5000000.png)
- [Eficiência forte (N=5M)](../resultados/campanha_docker_20261111_181418/analise/eficiencia_forte_N5000000.png)
- [Tempo forte (N=5M)](../resultados/campanha_docker_20261111_181418/analise/tempo_forte_N5000000.png)
- [Tempo de escalabilidade fraca](../resultados/campanha_docker_20261111_181418/analise/tempo_fraca.png)
- [Eficiência de escalabilidade fraca](../resultados/campanha_docker_20261111_181418/analise/eficiencia_fraca.png)

Comandos rápidos para abrir os gráficos pelo terminal:

```bash
# Linux com interface gráfica
xdg-open resultados/campanha_docker_20261111_181418/analise/speedup_forte_N5000000.png
xdg-open resultados/campanha_docker_20261111_181418/analise/eficiencia_forte_N5000000.png
xdg-open resultados/campanha_docker_20261111_181418/analise/tempo_fraca.png

# Windows / WSL
explorer.exe resultados\\campanha_docker_20261111_181418\\analise\\speedup_forte_N5000000.png
```

## 5. Pontos que todos devem saber explicar na arguição

- O que significam `N`, `K` e `IT`; por que há iterações fixas e distância euclidiana ao quadrado (sem `sqrt`).
- Por que a atribuição é independente por ponto e cada iteração depende dos centroides da iteração anterior.
- Como acumuladores privados por thread (`sx_local[tid]`, `sy_local[tid]`, `cnt_local[tid]`) e as barreiras implícitas evitam condições de corrida no OpenMP sem `atomic`/`critical`.
- Por que `schedule(static)` é adequado ao custo regular por ponto.
- Por que o MPI precisa reunir somas/contagens globais; diferença entre `MPI_Reduce` e `MPI_Allreduce`.
- Como `MPI_Scatterv` trata `N` não divisível por `P` e ranks sem pontos.
- Como preservar centroides de clusters vazios (`if (cnt)`).
- Por que o checksum com 4 casas decimais é triagem e a comparação individual de centroides (17 dígitos) é evidência mais forte.
- Como calcular speedup e eficiência em escalabilidade forte e fraca.
- Por que `f` no perfilador inclui atribuição e acumulação, e por que o limite ideal de Amdahl difere do speedup medido.
- Por que quatro processadores lógicos (SMT em 2 núcleos físicos) não equivalem a quatro núcleos físicos independentes.
- Por que MPI teve menor tempo iterativo, mas maior duração externa que OpenMP em `N=5.000.000`.
- Por que a eficiência fraca MPI-2 de `111,92%` não demonstra ganho superlinear estável (efeito da alta dispersão na referência MPI-1; razão das medianas é `88,4%`).

A defesa é individual, sobre uma frente de outro integrante. Conforme o
enunciado, ocorre sem apoio de colegas ou IA, com consulta ao próprio repositório.
O uso de IA no desenvolvimento é permitido; o grupo precisa compreender
e defender efetivamente o código e os resultados apresentados.
