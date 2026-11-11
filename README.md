# Projeto de Programação Paralela — K-means

IESB · Ciência da Computação · CCO085 · 2026/2 · Problema 10.

Implementações sequencial, OpenMP e MPI do algoritmo de Lloyd, preservando
o baseline fornecido pelo professor. A campanha final foi executada no Docker
em 11/11/2026, commit 66e2e16, com 150 medições conferidas.

## Resultados principais

Para N=5.000.000, K=8 e IT=20, usando quatro workers:

| Versão | Tempo médio das iterações | Speedup | Eficiência |
|---|---:|---:|---:|
| Sequencial | 1,957904 s | 1,000× | — |
| OpenMP | 1,503139 s | 1,303× | 32,6% |
| MPI | 1,187470 s | 1,649× | 41,2% |

Os valores descrevem as iterações desta campanha, não o tempo completo da
aplicação nem uma superioridade geral entre tecnologias. A duração externa
e a variabilidade também foram analisadas.

- [Resultados finais e discussão de Amdahl](docs/RESULTADOS_FINAIS_DOCKER.md).
- [Protocolo experimental](docs/EXPERIMENTOS.md).
- [Arquitetura](docs/ARQUITETURA.md).
- [Demonstração e arguição](docs/ROTEIRO_DEMONSTRACAO.md).

## Executar com Docker

Requisitos no host: Docker Desktop com mecanismo WSL2 e integração com Ubuntu,
ou Docker Engine/Compose em Linux. Execute na raiz do repositório:

~~~bash
docker compose build pp-lab
docker compose run --rm pp-lab
~~~

O Compose monta a pasta do projeto em /lab. Dentro do contêiner:

~~~bash
make
./build/10_kmeans_base 1000000 8 20
OMP_NUM_THREADS=4 OMP_DYNAMIC=FALSE OMP_PROC_BIND=FALSE ./build/10_kmeans_omp 1000000 8 20
mpirun --oversubscribe --bind-to none -np 4 ./build/10_kmeans_mpi 1000000 8 20
~~~

Checksum de referência dessa entrada: 8109.0037. O checksum é triagem;
as validações abaixo comparam os centroides individualmente.
Use exit para sair; repita docker compose run --rm pp-lab para voltar.
Os arquivos da pasta montada permanecem no host.

## Compilação nativa

No Linux do laboratório: G++ com OpenMP, Make, Open MPI com cabeçalhos
de desenvolvimento; Python 3 e Matplotlib para a análise.

~~~bash
make
~~~

O alvo padrão gera sete executáveis em build/: baseline, OpenMP, MPI,
perfilamento histórico, dois validadores e o perfilador adicional de Amdahl.
Alvos individuais: baseline, openmp, mpi, perfilamento, validacao e amdahl.
make clean remove somente build/. O coletor da campanha também recompila
os programas que utiliza.

## Interface e invariantes

Os programas recebem N K IT, com padrões 1000000 8 20. Use N>=K>=1 e IT>=0.
As coordenadas são geradas pelo LCG original com semente 2024ULL.
Os primeiros K pontos inicializam os centroides; a distância é euclidiana
ao quadrado; empates favorecem o primeiro índice; são feitas exatamente IT
iterações; clusters vazios preservam o centroide anterior.
O baseline permanece em sequencial/10_kmeans.cpp, inalterado.
O MPI aceita --centroides após N K IT para imprimir coordenadas com 17 dígitos.

## Corretude

O grupo confirmou no Docker 9/9 comparações OpenMP e 33/33 MPI, com erro
máximo MPI de 0,0. Os relatórios usados estão preservados em
[validacoes_preexistentes](resultados/campanha_docker_20261111_181418/validacoes_preexistentes/).
Esses resultados se referem aos casos executados.

Para repetir os validadores, preserve primeiro os CSVs anteriores:

~~~bash
pasta_backup="resultados/backup_validacao_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$pasta_backup"
cp resultados/validacao_openmp.csv resultados/validacao_centroides_mpi.csv "$pasta_backup/"
bash scripts/validar_openmp.sh
python3 scripts/validar_centroides_mpi.py
~~~

O backup fica dentro da pasta montada e permanece no host. Os validadores
antigos têm destinos fixos; conserve seus relatórios antes de repetir testes.

## Campanha final e reprodução

A pasta versionada de referência é
[resultados/campanha_docker_20261111_181418](resultados/campanha_docker_20261111_181418/).
Há 105 medições fortes, 30 fracas e 15 de perfilamento, com cinco repetições
e um aquecimento descartado por configuração. A coleta compara as três
versões na mesma sessão; a escalabilidade fraca cobre OpenMP e MPI.

Para uma nova campanha, com notebook na energia e condições de carga registradas:

~~~bash
python3 scripts/medir_campanha_docker.py --observacoes "descreva as condicoes reais"
~~~

O script cria uma pasta exclusiva, confere checksums, valida o novo
perfilador por centroides, registra metadados, gera gráficos e um ZIP.
Campanhas antigas permanecem preservadas. O
[roteiro completo](docs/ROTEIRO_CAMPANHA_DOCKER.md) documenta parâmetros e saídas.

As campanhas históricas com G++ 15.2.0 continuam em resultados/ e são
separadas da campanha Docker com G++ 13.3.0. Seus baselines não devem ser
misturados no cálculo de speedup.

## Organização e entrega

Fontes em sequencial/, openmp/, mpi/, perfilamento/ e validacao/.
Scripts em scripts/; documentação em docs/; dados e gráficos em resultados/.
[AUTORES.md](AUTORES.md) declara as frentes técnicas do trio.

O PR #19 integrou MPI à main em d9fb659. A campanha final está identificada
pelo commit local 66e2e16 em entrega/finalizacao. Na última consulta,
essa branch ainda não estava publicada. Falta registrar este fechamento,
publicar/revisar a branch e submeter o link ao professor.
Marco 2: 12/11/2026. Seminário em 19 ou 26/11, conforme a escala.
