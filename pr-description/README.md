# PR Description

Skill para o Claude Code que gera descrições padronizadas de Pull Requests analisando o diff entre a branch atual e a branch `main`.

## O que faz

- Analisa o diff (`git diff main...HEAD`) para entender as mudanças
- Busca o card do Linear associado à branch (via MCP)
- Gera uma descrição com três seções: **Why**, **What** e **Validation**
- Abre o PR no GitHub automaticamente

## Quando é ativada

- Quando você pede para abrir um pull request
- Quando você pede uma descrição de PR
- Quando você diz algo como "crie uma descrição de PR para mim"

## Dependências

- **Linear MCP** configurado no Claude Code (para buscar cards do Linear)
- **GitHub CLI** (`gh`) autenticado

## Formato da descrição

Toda descrição de PR gerada inclui:

1. **Why** — Motivação para a mudança
2. **What** — O que foi alterado e o impacto no projeto
3. **Validation** — Testes adicionados ou processo de validação manual

## Fluxo de execução

1. Verifica que você não está na branch `main`
2. Analisa o diff com `main`
3. Extrai o identificador do ticket da branch (ex: `feature/SUP-123-add-auth` → `SUP-123`)
4. Busca o card no Linear e valida alinhamento com as mudanças
5. Pergunta se deseja commitar mudanças pendentes
6. Abre o PR no GitHub
