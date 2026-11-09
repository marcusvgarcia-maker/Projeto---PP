/* Baseline 10 — Agrupamento por k-medias (k-means, algoritmo de Lloyd)
 * IESB 2026/2 — CCO085 — Prof. Rodrigo Goncalves Pinto
 * Aspecto interessante: fases paralelas alternadas — atribuicao (paralela)
 * e recalculo dos centroides (reducao) — com sincronizacao global a cada passo.
 *
 * Compilar: g++ -O2 -o 10_kmeans 10_kmeans.cpp
 * Executar: ./10_kmeans 1000000 8 20   (pontos; clusters; iteracoes)
 */
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <cstdint>
#include <cmath>
#include <ctime>
#include <omp.h>
#include <algorithm>
using namespace std;

static double agora() {
    timespec t; clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec + t.tv_nsec * 1e-9;
}

int main(int argc, char** argv) {
    int N = (argc > 1) ? atoi(argv[1]) : 1000000;
    int K = (argc > 2) ? atoi(argv[2]) : 8;
    int IT = (argc > 3) ? atoi(argv[3]) : 20;

    vector<double> px(N), py(N);
    uint64_t s = 2024ULL;
    for (int i = 0; i < N; i++) {
        s = s*6364136223846793005ULL + 1; px[i] = (double)((s >> 40) % 1000);
        s = s*6364136223846793005ULL + 1; py[i] = (double)((s >> 40) % 1000);
    }
    vector<double> cx(K), cy(K);
    for (int j = 0; j < K; j++) { cx[j] = px[j]; cy[j] = py[j]; }  // centroides iniciais

    vector<int> rotulo(N, 0);
    // Acumuladores privados para cada thread
    const int T = omp_get_max_threads();

    vector<vector<double>> sx_local(T, vector<double>(K, 0));
    vector<vector<double>> sy_local(T, vector<double>(K, 0));
    vector<vector<long>> cnt_local(T, vector<long>(K, 0));

    double t0 = agora();
    for (int it = 0; it < IT; it++) {
        // fase 1 — atribuicao
        #pragma omp parallel for schedule(static)
        for (int i = 0; i < N; i++) {
            double best = 1e18; int bj = 0;
            for (int j = 0; j < K; j++) {
                double dx = px[i]-cx[j], dy = py[i]-cy[j];
                double d = dx*dx + dy*dy;
                if (d < best) { best = d; bj = j; }
            }
            rotulo[i] = bj;
        }        
        // fase 2 — recalculo paralelo dos centroides

        // Zerar os acumuladores locais
        for (int t = 0; t < T; t++) {
            fill(sx_local[t].begin(), sx_local[t].end(), 0.0);
            fill(sy_local[t].begin(), sy_local[t].end(), 0.0);
            fill(cnt_local[t].begin(), cnt_local[t].end(), 0);
        }

        // Acumulacao paralela sem condicoes de corrida
        #pragma omp parallel
        {
            int tid = omp_get_thread_num();

            #pragma omp for schedule(static)
            for (int i = 0; i < N; i++) {
                int j = rotulo[i];

                sx_local[tid][j] += px[i];
                sy_local[tid][j] += py[i];
                cnt_local[tid][j]++;
            }
        }

        // Reducao dos resultados parciais
        for (int j = 0; j < K; j++) {
            double sx = 0.0;
            double sy = 0.0;
            long cnt = 0;

            for (int t = 0; t < T; t++) {
                sx += sx_local[t][j];
                sy += sy_local[t][j];
                cnt += cnt_local[t][j];
            }

            // Atualizar o centroide se o cluster nao estiver vazio
            if (cnt) {
                cx[j] = sx / cnt;
                cy[j] = sy / cnt;
            }
        }

    }
    double t1 = agora();

    double soma = 0;
    for (int j = 0; j < K; j++) soma += cx[j] + cy[j];
    printf("N=%d K=%d it=%d  checksum=%.4f  tempo=%.6f s\n", N, K, IT, soma, t1 - t0);
    return 0;
}
