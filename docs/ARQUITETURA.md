# Arquitetura — K-means de Lloyd

As três implementações de produção preservam o resultado do baseline
sequencial fornecido. O novo perfilador é um auxiliar de medição separado.
Os resultados e limites estão em [RESULTADOS_FINAIS_DOCKER.md](RESULTADOS_FINAIS_DOCKER.md).

## Interface e matemática

Argumentos N, K e IT; padrões 1000000, 8 e 20. Domínio coerente:
N>=K>=1 e IT>=0. O MPI valida explicitamente os parâmetros; o baseline
assume entrada válida.

- Pontos 2D gerados pelo LCG original, estado uint64_t com semente 2024ULL.
- Coordenadas inteiras entre 0 e 999, armazenadas em double.
- Primeiros K pontos como centroides iniciais.
- Distância euclidiana ao quadrado, sem raiz.
- Atualização do melhor apenas com d<best; empate favorece o menor índice.
- Exatamente IT iterações; não há parada antecipada por convergência.
- Cluster vazio preserva o centroide anterior.
- Checksum soma cx[j]+cy[j], impresso com quatro casas.

Cada iteração atribui os pontos, acumula somas/contagens e atualiza as médias.
A iteração seguinte depende dos novos centroides.
Complexidade sequencial: O(IT×(NK+N+K)); memória O(N+K).

## OpenMP

O laço de atribuição usa parallel for schedule(static).
Cada ponto percorre os mesmos K centroides e escreve um rótulo próprio.
O custo por ponto é regular, justificando a escolha estática.

O recálculo usa somas e contagens privadas por thread. Após as barreiras,
uma combinação serial por cluster reúne os acumuladores e atualiza os centroides.
A redução é manual: não há cláusula reduction, critical ou atomic por ponto.
O custo adicional de memória é O(TK), e a combinação custa O(TK) por iteração.
As regiões paralelas e suas barreiras respeitam a dependência entre fases.

São duas regiões paralelas por iteração, quarenta para IT=20.
Possíveis custos de sincronização, memória e false sharing exigem medição
específica para serem identificados como causas, não apenas hipótese.

## MPI

O rank 0 gera exatamente a entrada do baseline e escolhe os primeiros K pontos.
Duas Bcast compartilham os centroides; duas Scatterv distribuem X/Y por
blocos contíguos. As quantidades diferem por no máximo um ponto.
Ranks sem pontos usam contagem zero e continuam participando das coletivas.

Em cada iteração, cada rank atribui seus pontos e acumula coordenadas e
contagens locais. Uma Allreduce reúne as 2K somas em double; outra reúne
as K contagens em long. Todos recebem os totais e atualizam os centroides.
Clusters vazios continuam com o valor anterior.

Há duas Allreduce por iteração. O tempo de comunicação interna faz parte
do laço medido. Ao final, Reduce com MPI_MAX agrega os tempos locais;
o rank 0 imprime o resultado. --centroides acrescenta as coordenadas com
17 dígitos significativos, mantendo a saída normal sem essa opção.

O rank 0 mantém também os vetores globais: a implementação não elimina
o armazenamento O(N) nesse rank. O ensaio usa processos em uma única máquina
e não demonstra escalabilidade entre máquinas de um cluster.

## Cronometragem

O baseline cronometra somente as iterações. OpenMP usa o mesmo recorte.
MPI mede as iterações, incluindo as reduções; geração, MPI_Init e Bcast/Scatterv
iniciais ficam fora. O máximo das durações locais é o tempo MPI reportado.
O coletor registra também a duração externa de cada subprocesso, separadamente.

## Perfilador adicional e Amdahl

perfilamento/10_kmeans_amdahl.cpp é uma cópia adicional instrumentada;
sequencial/10_kmeans.cpp permanece inalterado.
O auxiliar mede atribuição e acumulação de pontos separadamente. A razão
dessas médias pela média total produz uma estimativa ideal do trabalho
potencialmente paralelo. Inicialização, atualização, desalocação, controle
e instrumentação pertencem ao restante.

O perfilador foi conferido por centroides para os três N da campanha.
A instrumentação pode alterar os tempos, principalmente nos trechos pequenos.
A estimativa não mede a fração serial efetiva do paralelo e não incorpora
seus custos extras. A comparação com Amdahl está discutida no relatório final.

## Fontes e construção

O Makefile compila as três versões, o perfilador histórico, os validadores
sequencial/OpenMP e, pelo alvo amdahl, o novo perfilador: sete executáveis.
Os validadores históricos são cópias instrumentadas para imprimir centroides;
os arquivos de produção atuais não foram modificados nesta finalização.

O coletor recompila os programas usados, valida o perfilador, verifica
checksums, captura logs e hashes, registra ambiente e gera arquivos exclusivos.
O analisador confere configurações/repetições e calcula estatísticas,
previsões ideais e gráficos. Falhas impedem marcar uma coleta como concluída.
