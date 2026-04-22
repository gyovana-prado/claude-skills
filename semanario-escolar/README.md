# Semanário Escolar - Plugin

Gera automaticamente o semanário escolar (planejamento quinzenal) em Excel para a Professora Angela do 3º Ano A de uma escola adventista.

## O que faz

- Parseia PDFs de percurso pedagógico e competências do portal CPB Educacional
- Gera a planilha Excel no formato exato que a Angela usa
- Inclui banco de dados RAI com 194 competências do 3º ano pré-extraídas
- Suporta feriados, professor substituto e múltiplas competências por aula

## Como usar

Diga algo como:
- "gerar semanário da quinzena 13 a 24 de abril"
- "preencher semanário"
- "plano de aulas da próxima quinzena"

O Claude vai pedir os PDFs do percurso pedagógico e gerar a planilha.

## Componentes

### Skill: semanario
A skill principal que guia todo o fluxo de geração do semanário.

### Banco RAI (194 competências)
Banco completo de competências do 3º ano extraído do RAI 2024, organizado por matéria:
- Língua Portuguesa: 80 competências
- Matemática: 38 competências
- Ciências: 15 competências
- Geografia: 13 competências
- História: 17 competências
- Ensino Religioso: 31 competências

### Scripts
- `generate_semanario.py` — Gera o Excel usando openpyxl
- `manage_competencias.py` — Gerencia bancos de competências (por capítulo e RAI)

## Requisitos

- Python 3 com `openpyxl` instalado
- PDFs do percurso pedagógico (fornecidos pela professora)
