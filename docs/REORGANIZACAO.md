# Reorganização local concluída e plano de integração ao GitHub

> **Projeto:** Programação Paralela (CCO085), IESB, 2026/2 — Problema 10, K-means (Lloyd)  
> **Referência:** 09/11/2026  
> **Estado:** reorganização **local concluída e verificada**; publicação na `main` do GitHub **ainda pendente**.  
> **Repositório:** <https://github.com/marcusvgarcia-maker/Projeto---PP>

## 1. Objetivo deste documento

Registrar como os arquivos foram organizados e orientar uma integração futura ao GitHub **sem repetir a reorganização** ou sobrescrever trabalho validado. Este arquivo substitui instruções antigas de recuperação manual de arquivos das branches.

**Regra central para pessoas e IAs:** trate a pasta local reorganizada `projeto_pp/` como fonte de trabalho atual para código, scripts e resultados já testados. Antes de qualquer publicação, verifique seu conteúdo e o estado real do Git. Não presuma que os arquivos já estejam na branch `main`.

## 2. Diagnóstico histórico do GitHub

Na inspeção realizada em 09/11/2026 foram encontradas estas branches:

| Branch | Conteúdo observado na inspeção |
|---|---|
| `main` | `10_kmeans.cpp` original e README genérico |
| `baseline_perfilamento` | baseline, perfilamento, script de medição, CSV e binários |
| `openmp` | código OpenMP, medições, gráficos, scripts e arquivos de validação |

A comparação entre `main` e cada branch de desenvolvimento retornou **“No common ancestor”**. Portanto, **não realizar `git merge` automático nem `git merge --allow-unrelated-histories` sem uma análise específica**. As branches antigas devem ser preservadas pelo menos até a entrega/avaliação.

Os scripts e códigos das branches históricas são **versões anteriores**: não devem ser copiados sobre os arquivos locais reorganizados. Alguns executáveis foram versionados nessas branches; o `.gitignore` atual impede novos arquivos correspondentes de serem adicionados acidentalmente, mas não apaga binários já rastreados em históricos anteriores.

## 3. Organização local já concluída

A pasta local de trabalho é `projeto_pp/`. A listagem e os testes fornecidos durante a reorganização confirmaram:

```text
projeto_pp/
├── .gitignore
├── AGENTS.md
├── AUTORES.md
├── Makefile
├── README.md
├── sequencial/10_kmeans.cpp
├── perfilamento/10_kmeans.cpp
├── openmp/10_kmeans.cpp
├── mpi/                         # vazia, implementação pendente
├── scripts/
│   ├── medir_baseline.sh
│   ├── medir_openmp.sh
│   ├── gerar_graficos_openmp.py
│   └── validar_openmp.sh
├── resultados/
│   ├── baseline.csv
│   ├── resultados_openmp.csv
│   ├── resumo_openmp.csv
│   ├── validacao_openmp.csv
│   └── graficos/                # nove PNG históricos
├── validacao/
│   ├── sequencial.cpp
│   ├── openmp.cpp
│   ├── referencia.txt
│   ├── omp_1.txt
│   ├── omp_2.txt
│   └── omp_4.txt
└── docs/
    ├── ARQUITETURA.md
    ├── ESTADO_ATUAL.md
    ├── EXPERIMENTOS.md
    ├── PROXIMOS_PASSOS.md
    └── REORGANIZACAO.md
```

**Observações:**

- A pasta `build/` é gerada por `make` e ignorada no Git; não é código-fonte.
- A pasta de teste `resultados/graficos_teste/` foi retirada da organização principal; a execução histórica do teste continua documentada.
- Versões anteriores dos documentos foram retiradas da pasta do projeto e preservadas em backup externo, conforme relatado durante a reorganização.
- O Git não rastreia diretórios vazios. `mpi/` só aparecerá no repositório quando contiver um arquivo rastreado (por exemplo, o código MPI futuro ou um `.gitkeep` deliberado).
- As saídas `validacao/*.txt` são evidências auxiliares da última comparação salva; o registro completo dos nove casos está em `resultados/validacao_openmp.csv`, gerado por script.

## 4. Evidências dos testes locais

- `make` compilou baseline, OpenMP, perfilamento e dois programas de validação sem erro.
- Baseline e OpenMP executaram para `N=1.000.000`, `K=8`, `IT=20` com `checksum=8109.0037`.
- `bash scripts/validar_openmp.sh` aprovou **9/9 comparações de centroides finais**: `N` = 100.000, 1.000.000, 5.000.000, com 1, 2 e 4 threads; `K=8`, `IT=20`.
- O gerador de gráficos foi executado na estrutura nova e produziu nove PNG e um CSV de resumo em uma pasta temporária de teste.
- As **60 medições** OpenMP e as **15 medições** iniciais do baseline estão preservadas nos CSVs históricos.
- **MPI não foi implementado, validado nem medido** na estrutura atual.

> Não interpretar checksum coincidente isoladamente como prova geral de igualdade. A comparação dos centroides finais foi verificada apenas nas nove configurações acima; outros parâmetros ainda exigem testes.

## 5. O que NÃO deve ser repetido

- Não recuperar `medir_baseline.sh`, `medir_openmp.sh`, `gerar_graficos_openmp.py` ou os fontes de branches antigas por `git show ... > arquivo`: isso **sobrescreveria as versões adaptadas**.
- Não mover novamente os arquivos entre pastas: a estrutura local já foi consolidada.
- Não substituir `README.md`, `AGENTS.md`, `AUTORES.md` ou `docs/` por modelos anteriores.
- Não enviar executáveis de `build/`, caches ou gráficos temporários para o repositório.
- Não declarar o MPI concluído ou a publicação remota efetuada sem evidência.
- Não apagar nem forçar a atualização das branches históricas.

## 6. Plano seguro para publicar posteriormente (AINDA NÃO EXECUTADO)

Este é um **roteiro futuro**, não um comando para executar agora. Antes, preservar uma cópia de segurança da pasta local e verificar seu conteúdo.

1. **Inspecionar o Git local:** na pasta `projeto_pp`, executar `git rev-parse --is-inside-work-tree` e `git status`. Isso revela se a pasta já é um repositório. Não executar `git init` automaticamente e não trocar de branch com modificações não salvas.
2. **Preferir integração por um clone limpo:** se a pasta reorganizada não possuir um vínculo Git confiável, criar **outra pasta** para a publicação, clonando a `main` existente. Não copiar a pasta `.git` antiga para dentro da reorganizada.
3. **Criar uma branch nova a partir da `main`:** por exemplo `organizacao/kmeans`. Não mesclar diretamente `baseline_perfilamento` ou `openmp`.
4. **Copiar seletivamente pelo Explorador de Arquivos** da pasta local `projeto_pp/` para a nova pasta clonada: fontes, scripts, CSVs, nove gráficos, `Makefile`, `.gitignore`, `README.md`, `AGENTS.md`, `AUTORES.md` e `docs/`. **Não copiar** `build/`, backups ou `.git`.
5. **Preservar o baseline fornecido pelo professor:** verificar que `sequencial/10_kmeans.cpp` corresponde à lógica do original; recomenda-se manter também o `10_kmeans.cpp` existente na raiz da `main` durante a primeira integração, eliminando qualquer ambiguidade apenas após revisão.
6. **Compilar e testar do zero no clone:** executar `make`, testar baseline e OpenMP e rodar `bash scripts/validar_openmp.sh`. Checar que os comandos documentados no README funcionam. Corrigir divergências antes de publicar.
7. **Inspecionar antes do commit:** revisar `git status`, `git diff`, `git diff --cached` e `git ls-files` para evitar binários e arquivos indevidos. Adicionar somente os arquivos pretendidos.
8. **Criar commits descritivos**, enviar a nova branch ao GitHub e abrir Pull Request para `main`. Solicitar revisão do grupo. Manter as branches históricas e evitar `push --force`.
9. **Após a integração efetiva**, atualizar `README.md`, `AGENTS.md`, `docs/ESTADO_ATUAL.md` e `docs/PROXIMOS_PASSOS.md` para registrar a branch, o commit ou PR e a data reais, removendo advertências que só se aplicavam à etapa local.

### Exemplo de comandos, APENAS quando a publicação for autorizada e a pasta de destino estiver livre

```bash
# Executar a partir de um diretório PAI; escolher um nome de destino novo.
git clone --branch main https://github.com/marcusvgarcia-maker/Projeto---PP.git projeto_pp_publicacao
cd projeto_pp_publicacao
git switch -c organizacao/kmeans

# Neste ponto, copiar os arquivos da pasta LOCAL reorganizada pelo Explorador,
# sem copiar .git, build ou backups. Revisar tudo antes do commit.
git status
git diff
```

Não executar `git add`, `git commit`, `git push` ou criar a Pull Request antes de revisar o resultado final com o grupo.

## 7. Próximas tarefas técnicas

Após publicar a reorganização, continuar a implementação **MPI** em `mpi/`, validar os resultados contra o sequencial, realizar medições, gerar gráficos, comparar escalabilidade e discutir a Lei de Amdahl. O prazo do Marco 2 indicado pelo professor é **12/11/2026**.

Consulte `docs/PROXIMOS_PASSOS.md` para a lista operacional e `docs/ESTADO_ATUAL.md` para o estado confirmado. Depois de qualquer mudança, atualize esses documentos e registre o que foi testado e o que permanece pendente.
