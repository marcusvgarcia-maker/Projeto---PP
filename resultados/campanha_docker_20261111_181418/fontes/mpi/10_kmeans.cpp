/* K-means de Lloyd — versao MPI do baseline do projeto CCO085.
 * Uso: mpirun --oversubscribe -np 4 ./build/10_kmeans_mpi 1000000 8 20
 * Tempo: apenas iteracoes de Lloyd, incluindo reducoes MPI.
 * O processo 0 gera pontos com o mesmo LCG e a mesma ordem do baseline.
 */
#include <mpi.h>
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <vector>
#include <algorithm>
#include <string>
using namespace std;

int main(int argc, char** argv) {
    MPI_Init(&argc, &argv);

    int rank = 0, processos = 1;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &processos);

    const int N = (argc > 1) ? atoi(argv[1]) : 1000000;
    const int K = (argc > 2) ? atoi(argv[2]) : 8;
    const int IT = (argc > 3) ? atoi(argv[3]) : 20;

    // O baseline supoe que existam K pontos para centroides iniciais.
    if (N < 1 || K < 1 || K > N || IT < 0) {
        if (rank == 0) {
            fprintf(stderr, "Parametros invalidos: requer N >= K >= 1 e IT >= 0.\n");
        }
        MPI_Abort(MPI_COMM_WORLD, 1);
        return 1;
    }

    // Distribuicao contigua, inclusive quando N nao e divisivel por processos.
    vector<int> quantidades(processos), deslocamentos(processos);
    for (int p = 0; p < processos; ++p) {
        quantidades[p] = N / processos + (p < N % processos ? 1 : 0);
        deslocamentos[p] = (p == 0) ? 0 : deslocamentos[p - 1] + quantidades[p - 1];
    }
    const int n_local = quantidades[rank];

    vector<double> px, py;
    vector<double> cx(K), cy(K);
    if (rank == 0) {
        px.resize(N);
        py.resize(N);
        uint64_t s = 2024ULL;
        for (int i = 0; i < N; ++i) {
            s = s * 6364136223846793005ULL + 1;
            px[i] = (double)((s >> 40) % 1000);
            s = s * 6364136223846793005ULL + 1;
            py[i] = (double)((s >> 40) % 1000);
        }
        for (int j = 0; j < K; ++j) {
            cx[j] = px[j];
            cy[j] = py[j];
        }
    }

    // Cada rank passa a ter os mesmos centroides iniciais.
    MPI_Bcast(cx.data(), K, MPI_DOUBLE, 0, MPI_COMM_WORLD);
    MPI_Bcast(cy.data(), K, MPI_DOUBLE, 0, MPI_COMM_WORLD);

    // Separar coordenadas evita alterar a ordem de geracao do baseline.
    // Reservar pelo menos uma posicao permite passar data() com n_local == 0.
    vector<double> px_local(max(1, n_local)), py_local(max(1, n_local));
    MPI_Scatterv(rank == 0 ? px.data() : nullptr,
                 quantidades.data(), deslocamentos.data(), MPI_DOUBLE,
                 px_local.data(), n_local, MPI_DOUBLE, 0, MPI_COMM_WORLD);
    MPI_Scatterv(rank == 0 ? py.data() : nullptr,
                 quantidades.data(), deslocamentos.data(), MPI_DOUBLE,
                 py_local.data(), n_local, MPI_DOUBLE, 0, MPI_COMM_WORLD);

    vector<int> rotulo(n_local);
    vector<double> somas_locais(2 * K, 0.0), somas_globais(2 * K, 0.0);
    vector<long> contagens_locais(K, 0), contagens_globais(K, 0);

    // Medir somente iteracoes, com comunicacao, como no baseline.
    MPI_Barrier(MPI_COMM_WORLD);
    const double t0 = MPI_Wtime();
    for (int it = 0; it < IT; ++it) {
        // Fase 1 — atribuicao de cada ponto local ao centroide mais proximo.
        for (int i = 0; i < n_local; ++i) {
            double melhor = 1e18;
            int indice = 0;
            for (int j = 0; j < K; ++j) {
                const double dx = px_local[i] - cx[j];
                const double dy = py_local[i] - cy[j];
                const double d = dx * dx + dy * dy;
                if (d < melhor) {
                    melhor = d;
                    indice = j;
                }
            }
            rotulo[i] = indice;
        }

        // Fase 2 — somas e contagens privadas de cada processo.
        fill(somas_locais.begin(), somas_locais.end(), 0.0);
        fill(contagens_locais.begin(), contagens_locais.end(), 0L);
        for (int i = 0; i < n_local; ++i) {
            const int j = rotulo[i];
            somas_locais[j] += px_local[i];
            somas_locais[K + j] += py_local[i];
            ++contagens_locais[j];
        }

        // Reducoes coletivas: todos os processos recebem os totais globais.
        MPI_Allreduce(somas_locais.data(), somas_globais.data(), 2 * K,
                      MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
        MPI_Allreduce(contagens_locais.data(), contagens_globais.data(), K,
                      MPI_LONG, MPI_SUM, MPI_COMM_WORLD);

        // Clusters vazios mantem o centroide anterior, como no baseline.
        for (int j = 0; j < K; ++j) {
            if (contagens_globais[j] != 0) {
                cx[j] = somas_globais[j] / contagens_globais[j];
                cy[j] = somas_globais[K + j] / contagens_globais[j];
            }
        }
    }
    const double tempo_local = MPI_Wtime() - t0;
    double tempo_maximo = 0.0;
    MPI_Reduce(&tempo_local, &tempo_maximo, 1, MPI_DOUBLE, MPI_MAX, 0,
               MPI_COMM_WORLD);

    if (rank == 0) {
        if (argc > 4 && std::string(argv[4]) == "--centroides") {
            for (int j = 0; j < K; ++j)
                printf("CENTROIDE %d %.17g %.17g\n", j, cx[j], cy[j]);
        }
        double soma = 0.0;
        for (int j = 0; j < K; ++j) soma += cx[j] + cy[j];
        printf("N=%d K=%d it=%d  checksum=%.4f  tempo=%.6f s\n",
               N, K, IT, soma, tempo_maximo);
    }

    MPI_Finalize();
    return 0;
}
