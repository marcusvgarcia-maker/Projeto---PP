/* Baseline 10 — Agrupamento por k-medias (k-means, algoritmo de Lloyd)
 * IESB 2026/2 — CCO085 — Prof. Rodrigo Goncalves Pinto
 * Aspecto interessante: fases paralelas alternadas — atribuicao (paralela) 
 * (para cada ponto, descobrir qual centróide está mais próximo e atribuir o ponto a esse cluster)
 * e recalculo dos centroides (reducao) — com sincronizacao global a cada passo.
 * Compilar: g++ -O2 -o 10_kmeans 10_kmeans.cpp
 * Executar: ./10_kmeans 1000000 8 20   (pontos; clusters; iteracoes)
 */
#include <cstdio> // fornece funções de entrada e saída, como printf, scanf, etc.
#include <cstdlib> // fornece funções de entrada e saída, como printf, scanf, etc.
#include <vector> // usado para o comando vector (vetores dinamicos)
#include <cstdint> // fornece tipos de inteiros com tamanho fixo, como uint64_t
#include <cmath> // fornece funções matemáticas como sqrt, pow, sin, cos, etc.
#include <ctime> // fornece funções para manipulação de tempo, como clock_gettime
using namespace std; // permite usar nomes de funções e classes da biblioteca padrão sem precisar do prefixo std::

// Função para obter o tempo atual em segundos com precisão de nanosegundos
static double agora() { // criando uma função que retorna um double, e que fica disponível apenas dentro deste arquivo (static)
    // timespec é um tipo de estrutura que contém informações sobre um instante de tempo.
    timespec t; clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec + t.tv_nsec * 1e-9; 
    // tv_sec -> segundos, tv_nsec -> nanosegundos (tv_nsec * 1e-9 converte nanosegundos para segundos)
}

// Função principal do programa
int main(int argc, char** argv) {
    // argc = quantidade de argumentos passados na linha de comando
    // argv = vetor de strings contendo os argumentos passados na linha de comando
    int N = (argc > 1) ? atoi(argv[1]) : 1000000; // quantidade de pontos (que vão ser agrupados)
    // atoi = ASCII to integer (converte string para inteiro)
    int K = (argc > 2) ? atoi(argv[2]) : 8; // quantidade de clusters (centroides para formar os grupos)
    int IT = (argc > 3) ? atoi(argv[3]) : 20; // quantidade de iteracoes
    // ? = if, : = else

    // "Crie uma sequência chamada px contendo N valores, e outra sequência chamada py contendo N valores, ambos do tipo double."
    vector<double> px(N), py(N); 
    // uint64_t define um tipo inteiro sem sinal com exatamente 64 bits
    uint64_t s = 2024ULL; 
    for (int i = 0; i < N; i++) { // percorrer os pontos
        s = s*6364136223846793005ULL + 1; px[i] = (double)((s >> 40) % 1000);
        s = s*6364136223846793005ULL + 1; py[i] = (double)((s >> 40) % 1000);
    }
    vector<double> cx(K), cy(K);
    // "Crie uma sequência chamada cx contendo K valores, e outra sequência chamada cy contendo K valores, ambos do tipo double."
    for (int j = 0; j < K; j++) { cx[j] = px[j]; cy[j] = py[j]; }  // centroides iniciais \ percorrer os clusters

    vector<int> rotulo(N, 0);

    double t0 = agora();
    for (int it = 0; it < IT; it++) {
        // fase 1 — atribuicao
        for (int i = 0; i < N; i++) {
            double best = 1e18; int bj = 0;
            for (int j = 0; j < K; j++) {
                double dx = px[i]-cx[j], dy = py[i]-cy[j];
                double d = dx*dx + dy*dy;
                if (d < best) { best = d; bj = j; }
            }
            rotulo[i] = bj;
        }
        // fase 2 — recalculo dos centroides (reducao)
        vector<double> sx(K, 0), sy(K, 0); vector<long> cnt(K, 0);
        for (int i = 0; i < N; i++) { int j = rotulo[i]; sx[j]+=px[i]; sy[j]+=py[i]; cnt[j]++; }
        for (int j = 0; j < K; j++) if (cnt[j]) { cx[j]=sx[j]/cnt[j]; cy[j]=sy[j]/cnt[j]; }
    }
    double t1 = agora();

    double soma = 0;
    for (int j = 0; j < K; j++) soma += cx[j] + cy[j];
    printf("N=%d K=%d it=%d  checksum=%.4f  tempo=%.6f s\n", N, K, IT, soma, t1 - t0);
    return 0;
}
