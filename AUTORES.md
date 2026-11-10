# Autores e responsabilidades — Projeto de Programação Paralela

**Instituição:** Centro Universitário IESB  
**Curso:** Ciência da Computação  
**Disciplina:** Programação Paralela (CCO085) — 2026/2  
**Projeto:** Problema 10 — Agrupamento por k-médias (K-means, algoritmo de Lloyd)

## Integrantes e responsabilidades técnicas

| Integrante | Matrícula | Frente técnica |
|---|---|---|
| Marcus Vinícius Braz Garcia | 2412130155 | Baseline e perfilamento |
| João Victor Souza Cruz | 2412130066 | OpenMP (memória compartilhada) |
| João Pedro Alves dos Santos Reis | 2412130154 | MPI (memória distribuída) |

## Escopo das responsabilidades

- **Baseline e perfilamento:** compreender o código sequencial, analisar a complexidade, medir os tempos e identificar os hotspots, estabelecer o protocolo experimental e estimar os limites de speedup pela Lei de Amdahl.
- **OpenMP:** desenvolver e validar a versão em memória compartilhada, tratar condições de corrida e analisar o desempenho por número de threads.
- **MPI:** desenvolver e validar a versão em memória distribuída, justificar a decomposição de dados, usar operações coletivas e analisar o custo de comunicação e o desempenho por número de processos.

As atribuições acima indicam as **responsabilidades técnicas designadas**, não uma declaração de autoria individual de cada arquivo ou commit. As contribuições efetivas devem ser identificadas pelo histórico do repositório.

**Responsabilidade compartilhada:** todos os integrantes devem compreender as três frentes para a demonstração e a arguição cruzada previstas pelo professor.
