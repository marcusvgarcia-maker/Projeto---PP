/* Perfilamento adicional do baseline de Lloyd para a estimativa de Amdahl.
 * Nao substitui nem modifica sequencial/10_kmeans.cpp.
 * Mantem gerador, inicializacao, desempate, iteracoes e clusters vazios.
 * Tempo principal: iteracoes, excluindo a geracao e a impressao.
 * Partes potencialmente paralelas: atribuicao e acumulacao dos pontos.
 * O restante inclui inicializacao, atualizacao, desalocacao e instrumentacao.
 */
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <ctime>
#include <string>
#include <vector>
using namespace std;

static double agora() {
    timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec + t.tv_nsec * 1e-9;
}

int main(int argc, char** argv) {
    const int N = argc > 1 ? atoi(argv[1]) : 1000000;
    const int K = argc > 2 ? atoi(argv[2]) : 8;
    const int IT = argc > 3 ? atoi(argv[3]) : 20;
    if (N < 1 || K < 1 || K > N || IT < 0) {
        fprintf(stderr, "Requer N >= K >= 1 e IT >= 0.\n");
        return 1;
    }
    vector<double> px(N), py(N);
    uint64_t s = 2024ULL;
    for (int i = 0; i < N; ++i) {
        s = s * 6364136223846793005ULL + 1;
        px[i] = (double)((s >> 40) % 1000);
        s = s * 6364136223846793005ULL + 1;
        py[i] = (double)((s >> 40) % 1000);
    }
    vector<double> cx(K), cy(K);
    for (int j = 0; j < K; ++j) { cx[j] = px[j]; cy[j] = py[j]; }
    vector<int> rotulo(N, 0);
    double atribuicao = 0.0, acumulacao = 0.0;
    const double t0 = agora();
    for (int it = 0; it < IT; ++it) {
        const double a0 = agora();
        for (int i = 0; i < N; ++i) {
            double best = 1e18;
            int bj = 0;
            for (int j = 0; j < K; ++j) {
                double dx = px[i] - cx[j], dy = py[i] - cy[j];
                double d = dx * dx + dy * dy;
                if (d < best) { best = d; bj = j; }
            }
            rotulo[i] = bj;
        }
        atribuicao += agora() - a0;
        vector<double> sx(K, 0), sy(K, 0);
        vector<long> cnt(K, 0);
        const double c0 = agora();
        for (int i = 0; i < N; ++i) {
            int j = rotulo[i];
            sx[j] += px[i]; sy[j] += py[i]; cnt[j]++;
        }
        acumulacao += agora() - c0;
        for (int j = 0; j < K; ++j)
            if (cnt[j]) { cx[j] = sx[j] / cnt[j]; cy[j] = sy[j] / cnt[j]; }
    }
    const double total = agora() - t0;
    if (argc > 4 && string(argv[4]) == "--centroides")
        for (int j = 0; j < K; ++j)
            printf("CENTROIDE %d %.17g %.17g\n", j, cx[j], cy[j]);
    double soma = 0.0;
    for (int j = 0; j < K; ++j) soma += cx[j] + cy[j];
    printf("N=%d K=%d it=%d  checksum=%.4f  tempo=%.6f s\n",
           N, K, IT, soma, total);
    printf("PERFIL atribuicao_s=%.12g acumulacao_s=%.12g total_s=%.12g\n",
           atribuicao, acumulacao, total);
    return 0;
}
