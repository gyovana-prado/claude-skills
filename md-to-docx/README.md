# MD to DOCX

Skill para o Claude Code que converte arquivos Markdown (`.md`) para Word (`.docx`) usando **pandoc**.

## O que faz

Converte um ou mais arquivos `.md` para `.docx`, com suporte a templates de estilo, tabela de conteúdo e syntax highlighting.

## Quando é ativada

- Quando você pede para converter um arquivo Markdown para Word/DOCX
- Quando você pede para gerar um documento Word a partir de Markdown

## Dependências

- **pandoc** instalado no sistema (`/usr/bin/pandoc` ou disponível no PATH)

## Uso

### Conversão básica

```
Converta o arquivo relatorio.md para docx
```

### Com template de estilo

```
Converta relatorio.md para docx usando o template estilo.docx
```

### Conversão em lote

```
Converta todos os arquivos .md desta pasta para docx
```

## Opções suportadas

| Opção | Descrição |
|-------|-----------|
| `--reference-doc=template.docx` | Aplica estilos de um template Word |
| `--toc` | Adiciona tabela de conteúdo |
| `--toc-depth=N` | Profundidade dos headings no TOC (padrão: 3) |
| `--highlight-style=tango` | Syntax highlighting para blocos de código |

## Observações

- Preserva headings, negrito, itálico, listas, tabelas, blocos de código e links
- Imagens com caminhos relativos precisam ser resolvíveis a partir do diretório de trabalho
