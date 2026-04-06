# Claude Code Skills

Coleção de skills personalizadas para o [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

## Skills disponíveis

| Skill | Descrição |
|-------|-----------|
| [pr-description](./pr-description/) | Gera descrições padronizadas de Pull Requests |
| [md-to-docx](./md-to-docx/) | Converte Markdown para Word (.docx) |

## Como instalar

### 1. Clone o repositório

```bash
git clone https://github.com/gyovana-prado/claude-skills.git
```

### 2. Copie as skills para o diretório do Claude Code

Copie as pastas das skills que deseja usar para `~/.claude/skills/`:

```bash
cp -r claude-skills/pr-description ~/.claude/skills/
cp -r claude-skills/md-to-docx ~/.claude/skills/
```

Ou para copiar todas de uma vez:

```bash
cp -r claude-skills/*/ ~/.claude/skills/
```

### 3. Verifique a instalação

Abra o Claude Code e as skills estarão disponíveis automaticamente. O Claude vai detectar os arquivos `SKILL.md` dentro de cada pasta em `~/.claude/skills/` e ativá-las quando o contexto for apropriado.

## Estrutura de uma skill

Cada skill é uma pasta contendo pelo menos um arquivo `SKILL.md`:

```
nome-da-skill/
├── SKILL.md        # Definição da skill (obrigatório)
└── README.md       # Documentação de uso
```

O `SKILL.md` segue o formato:

```markdown
---
name: nome-da-skill
description: Descrição curta usada pelo Claude para decidir quando ativar a skill.
---

Instruções detalhadas para o Claude seguir quando a skill for ativada.
```

## Como criar uma nova skill

1. Crie uma pasta com o nome da skill em `~/.claude/skills/`
2. Adicione um arquivo `SKILL.md` com o frontmatter (`name` e `description`) e as instruções
3. O Claude Code vai detectar e usar a skill automaticamente
