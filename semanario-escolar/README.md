# Semanário Escolar — Plugin

Gera automaticamente semanários escolares (planejamento quinzenal) em Excel para duas professoras do Ensino Fundamental I de uma escola adventista, cada uma com fluxo adaptado ao formato de material que recebem.

## Skills disponíveis

### `semanario` — Professora Angela (3º Ano A)

Fluxo otimizado para **PDF de percurso pedagógico tabular** + **PDF de competências separado** (portal CPB Educacional). O percurso é uma tabela com colunas "Aula 1, Aula 2…" com bullets curtos.

Gatilhos: "semanário Angela", "quinzenário 3º ano", "plano quinzenal 3º A".

### `semanario-adriana` — Professora Adriana (5º Ano B)

Fluxo otimizado para **DOCX de plano de aula narrativo**, um arquivo por capítulo. As habilidades BNCC já vêm no cabeçalho do docx. Cada aula é descrita em parágrafos longos (Introdução / Desenvolvimento / Conclusão / Tarefa de casa) que precisam ser **condensados** para o formato compacto do Excel.

Gatilhos: "semanário Adriana", "quinzenário 5º ano", "plano quinzenal 5º B".

## Estrutura do plugin

```
semanario-escolar/
├── .claude-plugin/plugin.json
├── shared/
│   └── generate_semanario.py        # Gerador do Excel (compartilhado pelas duas skills)
├── skills/
│   ├── semanario/                   # Angela (3º A)
│   │   ├── SKILL.md
│   │   ├── references/
│   │   │   ├── grade_horaria.json
│   │   │   ├── parsing-guide.md
│   │   │   ├── competencias.json
│   │   │   └── competencias_rai_3ano.json   (194 competências)
│   │   └── scripts/manage_competencias.py
│   └── semanario-adriana/           # Adriana (5º B)
│       ├── SKILL.md
│       ├── references/
│       │   ├── grade_horaria_5anoB.json
│       │   ├── parsing-guide-docx.md
│       │   ├── competencias.json
│       │   └── competencias_rai_5ano.json   (147 competências)
│       └── scripts/
│           ├── parse_plano_aula.py          # Parser DOCX → JSON
│           └── manage_competencias.py
└── agent-smith-index.json
```

## Como usar

Diga algo como:
- (Angela) "gerar semanário da Angela para 02 a 13 de junho"
- (Adriana) "gerar semanário da Adriana — quinzena começa 02/06"

A skill correspondente vai perguntar pelos materiais necessários (PDFs para Angela, DOCX para Adriana) e gerar a planilha.

## Requisitos

- Python 3 com `openpyxl` instalado (para gerar Excel)
- `pypdf` (para o extrator inicial do RAI — uso único)
- Materiais da quinzena: PDFs (Angela) ou DOCX (Adriana) fornecidos pelas professoras

## Bancos RAI

- **3º ano**: 194 competências organizadas por matéria, com 3 níveis (categoria → objeto de conhecimento → competência).
- **5º ano**: 147 competências organizadas por matéria, com 2 níveis (categoria → competência). Extraído do RAI 2024 (`shared/_extract_rai_5ano.py`).
