# Verificacao tecnica do pacote da campanha

Verificacao executada pelo assistente em 11/11/2026, em outro executor Linux.
Nao representa a campanha de desempenho no Docker do aluno.

- Sintaxe Python aprovada para os dois scripts.
- Perfilador adicional compilado com -O2 -std=c++17 -Wall -Wextra -Wpedantic.
- Perfilador: 9/9 comparacoes individuais de centroides contra validacao_seq,
  incluindo N=1/K=1/IT=0; IT=0 com K=8; K=12; N=3156/K=3156 com duplicatas
  e clusters vazios; N=1.000.000 e N=5.000.000.
- Teste real do coletor: sequencial/OpenMP, N=10003 e 30011, workers 1/2,
  K=8/IT=3, duas repeticoes e um aquecimento. Gerou 12 registros fortes,
  4 fracos, 4 de perfilamento, resumos, 8 graficos e ZIP.
- Parser rejeitou 5 saidas invalidas e 3 conjuntos invalidos de centroides.
- Analise rejeitou 4 conjuntos com amostras incompletas, duplicadas ou invalidas.
- Timeout de subprocesso verificado.
- Repetir um destino existente foi recusado e seu CSV permaneceu identico.
- Fontes sequencial, OpenMP, MPI, perfilador historico e CSVs originais
  permaneceram byte a byte identicos.
- O caminho MPI da nova campanha nao foi executado neste executor. O MPI
  existente foi validado no Docker pelo aluno (33/33) antes desta etapa.
- A execucao completa, os numeros finais de Amdahl e a discussao critica
  permanecem pendentes ate a campanha no Docker do aluno.


## Evidência posterior — campanha completa do aluno

Em 11/11/2026 foi recebido o ZIP da campanha no commit 66e2e16.
O caminho MPI foi executado com sucesso pelo aluno no Docker: 190 subprocessos
da campanha retornaram zero e não houve timeout. Foram conferidos os 150
registros medidos, seus logs e hashes. Esta evidência complementa, sem alterar
retrospectivamente, os testes técnicos de preparação descritos acima.
