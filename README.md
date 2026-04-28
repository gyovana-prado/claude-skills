# Claude Skills

Marketplace de skills e plugins para [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

## Plugins disponíveis

| Plugin | Descrição |
|--------|-----------|
| [md-to-docx](./md-to-docx/) | Converte arquivos Markdown para Word (.docx) |
| [open-pr](./open-pr/) | Abre PRs end-to-end: auditoria de segurança, formatação, commit e criação no GitHub |
| [semanario-escolar](./semanario-escolar/) | Gera semanário escolar em Excel com banco RAI de competências |

## Como instalar

### Instalar o marketplace completo

```bash
claude marketplace add https://github.com/gyovana-prado/claude-skills
```

Depois instale os plugins que quiser:

```bash
claude plugin install md-to-docx
claude plugin install open-pr
claude plugin install semanario-escolar
```

### Instalar um plugin diretamente

```bash
claude plugin install https://github.com/gyovana-prado/claude-skills/tree/main/open-pr
```

### Instalar localmente (desenvolvimento)

```bash
git clone https://github.com/gyovana-prado/claude-skills.git
claude plugin install ./claude-skills/open-pr
```

## Estrutura do repositório

```
claude-skills/
  .claude-plugin/
    marketplace.json          # Manifesto do marketplace
  md-to-docx/
    .claude-plugin/
      plugin.json
    skills/
      md-to-docx/
        SKILL.md
  open-pr/
    .claude-plugin/
      plugin.json
    skills/
      open-pr/
        SKILL.md
        security-patterns.md
  semanario-escolar/
    .claude-plugin/
      plugin.json
    skills/
      semanario/
        SKILL.md
```

## Contribuindo

Cada plugin é um diretório independente com seu próprio `plugin.json`. Para adicionar um novo plugin:

1. Crie a estrutura de diretórios seguindo o padrão acima
2. Adicione o plugin ao `.claude-plugin/marketplace.json`
3. Abra um PR
