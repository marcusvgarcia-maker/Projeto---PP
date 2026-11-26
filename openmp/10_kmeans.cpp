/* K-means de Lloyd — versao paralela com OpenMP (memoria compartilhada)
 * IESB 2026/2 — CCO085 — Prof. Rodrigo Goncalves Pinto
 * Aspecto interessante: fases paralelas alternadas — atribuicao (paralela)
 * e recalculo dos centroides (reducao com acumuladores privados por thread) —
 * com barreira implicita entre fases a cada iteracao.
 *
 * Compilar: g++ -O2 -std=c++17 -fopenmp -o build/10_kmeans_omp openmp/10_kmeans.cpp
 * Executar: OMP_NUM_THREADS=4 OMP_DYNAMIC=FALSE OMP_PROC_BIND=FALSE ./build/10_kmeans_omp 1000000 8 20
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
    // Acumuladores privados por thread, alocados uma unica vez fora do laco principal.
    // Cada thread escreve apenas na propria linha [tid], eliminando condicoes de corrida
    // na fase de reducao sem necessidade de #pragma omp atomic ou critical por ponto.
    const int T = omp_get_max_threads();

    vector<vector<double>> sx_local(T, vector<double>(K, 0));
    vector<vector<double>> sy_local(T, vector<double>(K, 0));
    vector<vector<long>> cnt_local(T, vector<long>(K, 0));

    double t0 = agora();
    for (int it = 0; it < IT; it++) {
        // Fase 1 — atribuicao paralela dos pontos aos centroides atuais.
        // schedule(static) divide blocos contiguos igualmente entre as threads, pois
        // cada ponto executa o mesmo trabalho (K comparacoes de distancia ao quadrado)
        // e escreve exclusivamente em rotulo[i]. Ha uma barreira implicita ao final
        // do #pragma omp parallel for, garantindo todos os rotulos prontos antes da Fase 2.
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
        // Fase 2 — recalculo paralelo dos centroides (reducao manual em duas etapas)

        // Zerar os acumuladores privados de cada thread antes da acumulacao
        for (int t = 0; t < T; t++) {
            fill(sx_local[t].begin(), sx_local[t].end(), 0.0);
            fill(sy_local[t].begin(), sy_local[t].end(), 0.0);
            fill(cnt_local[t].begin(), cnt_local[t].end(), 0);
        }

        // Acumulacao paralela sem condicoes de corrida: cada thread atualiza apenas
        // seus proprios vetores (indice tid). A barreira implicita no fim da regiao
        // paralela assegura que todas as somas parciais estejam concluidas antes da combinacao.
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

        // Reducao deterministica das somas parciais por cluster: custo O(T * K)
        for (int j = 0; j < K; j++) {
            double sx = 0.0;
            double sy = 0.0;
            long cnt = 0;

            for (int t = 0; t < T; t++) {
                sx += sx_local[t][j];
                sy += sy_local[t][j];
                cnt += cnt_local[t][j];
            }

            // Atualizar o centroide apenas se o cluster nao estiver vazio (invariante do baseline)
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
