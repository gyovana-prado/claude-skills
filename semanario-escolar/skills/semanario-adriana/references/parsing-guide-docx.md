# Guia de Parsing dos Planos de Aula (Formato Adriana)

Esta professora recebe um **DOCX por capítulo** de cada matéria, em formato narrativo. Muito diferente do formato tabular do percurso pedagógico (Angela).

---

## Estrutura do DOCX

### 1. Cabeçalho (parte fixa do topo)

```
Ano: 5º
Bimestre: 2º
Plano de aula: 1
Capítulo 6: Ser cidadão é...
Texto: Governar
Páginas: 46 a 54
Orientações didáticas: p. 9 e 10
Duração / carga horária: 8 horas-aulas
```

### 2. Blocos de contexto (após cabeçalho)

- **Objetos de conhecimento** — lista de tópicos a trabalhar (vão para a coluna "Objeto do Conhecimento" do Excel)
- **Habilidades BNCC** — organizadas por categoria:
  - LP: Leitura/escuta, Escrita, Análise linguística/semiótica, Oralidade
  - Mat: Números, Álgebra, Geometria, Grandezas e medidas, Probabilidade e estatística
  - Demais matérias: Unidades temáticas
- **Objetivos de aprendizagem** — lista (não vai para o Excel, mas pode informar Avaliação)
- **Princípios e valores** — contextual
- **Interdisciplinaridade** — conexões com outras matérias
- **Materiais, tecnologias, recursos** — vão para "Solicitação de Materiais" ou complementam "Recursos"

### 3. AULAS (parte principal)

Cada aula tem a estrutura:

```
AULA N
1.Introdução
[parágrafos descrevendo a abertura da aula]
2.Desenvolvimento
[parágrafos descrevendo o miolo da aula]
3.Conclusão
[parágrafos descrevendo o fechamento]
4.Tarefa de casa (opcional)
[parágrafo opcional]
```

### 4. Final do documento

- Verificação da aprendizagem
- Autoavaliação
- Referências
- Para aprofundamento do professor

---

## Como usar o parser

```bash
uv run python ${CLAUDE_PLUGIN_ROOT}/skills/semanario-adriana/scripts/parse_plano_aula.py <docx> <output.json>
```

Saída JSON:

```json
{
  "cabecalho": {"ano": "5º", "bimestre": "2º", "capitulo": "6: Ser cidadão é...", "texto": "Governar", "paginas": "46 a 54", "duracao": "8 horas-aulas"},
  "objetos_conhecimento": ["Forma de composição dos textos...", "Pontuação (discurso direto)", ...],
  "habilidades_bncc": {
    "Leitura/escuta": [{"codigo": "EF35LP22", "descricao": "Perceber diálogos..."}],
    "Escrita": [...],
    "Análise linguística/ semiótica": [...],
    "Oralidade": [...]
  },
  "objetivos_aprendizagem": [...],
  "principios_valores": [...],
  "interdisciplinaridade": [...],
  "materiais_recursos": [...],
  "aulas": [
    {
      "numero": "1",
      "introducao": ["..."],
      "desenvolvimento": ["..."],
      "conclusao": ["..."],
      "tarefa_casa": []
    },
    ...
  ]
}
```

---

## Regra de CONDENSAÇÃO do Desenvolvimento

**O ponto mais crítico desta skill.**

O texto do docx é **narrativo e longo** (parágrafos com 3-10 linhas). O quinzenário Excel real tem o campo "Desenvolvimento" com **1-3 frases curtas** (~150-300 caracteres).

### Estratégia

1. Ler os 3 blocos da aula (Introdução / Desenvolvimento / Conclusão)
2. Identificar a sequência de **verbos-ação** principais (Apresentar, Realizar, Discutir, Propor, Ler, Analisar, Escrever, Retomar, Solicitar...)
3. Cada momento da aula vira **um bullet curto** (5-15 palavras)
4. Concatenar com " • " ou quebra de linha

### Exemplo real

**Input (AULA 1 do cap. 6 LP — texto bruto do docx):**

> 1. Introdução: Compartilhe com os alunos o seguinte texto do Matteo, de 8 anos, cujas propostas de governo foram amplamente divulgadas… Peça que os alunos opinarem… Antes da leitura do texto "Governar", proponha um diálogo partindo da pergunta prévia: "Como você age quando é o líder de um grupo?" (p. 46).
> 2. Desenvolvimento: Proponha a leitura do texto "Governar" (p. 46), considerando estratégias: Antecipação (antes da leitura)… Inferência (durante a leitura)… Seleção (depois da leitura)… Verificação…
> 3. Conclusão: Partindo das perguntas do boxe "Trocando Ideias" (p. 46), solicite que os alunos pensem na resposta, organizem o pensamento, expressem o ponto de vista justificando.

**Output condensado:**

> Apresentar texto do Matteo e debater suas propostas. • Diálogo prévio: "Como você age como líder?" (p. 46). • Leitura do texto "Governar" com estratégias de antecipação, inferência, seleção e verificação. • Boxe "Trocando Ideias" — discussão em roda (p. 46).

### Regras

- **Manter páginas literais**: sempre que o docx cita "(p. X)" ou "p. X a Y", preservar no condensado
- **Manter nomes de boxes/seções entre aspas**: "Trocando Ideias", "Por dentro do texto", "Click: frases" etc.
- **Verbo de comando no infinitivo ou imperativo simples**: "Apresentar", "Ler", "Discutir" (não "Você deve apresentar")
- **Cortar exemplos longos**: se o docx lista 5 exemplos, o condensado fica com a categoria geral (ex: docx lista "letoca, cafave, fujovalo…" → condensado: "Exercício com palavras inventadas para identificar sílaba tônica")
- **Preservar links críticos só se forem o ponto central da aula** (vídeo, jogo). Senão omitir.

### Validação humana

Após gerar a versão condensada, **mostrar ao usuário antes de partir para o Excel**:

```
AULA 1 (LP) — Desenvolvimento condensado:
  Apresentar texto do Matteo e debater suas propostas. • Diálogo prévio: "Como você age como líder?" (p. 46) • Leitura do texto "Governar"...

OK? (sim / ajustar)
```

---

## Mapeamento docx → campos do Excel

| Campo do Excel | Fonte no docx |
|---|---|
| Objeto do Conhecimento | Item correspondente da lista `objetos_conhecimento` ou tópico declarado na aula |
| Evidências de Competências | Códigos + descrição de `habilidades_bncc` (associação N:N por categoria) |
| Desenvolvimento | **Condensado** de introducao + desenvolvimento + conclusao da aula |
| Recursos | "Apostila p. X a Y" do cabeçalho `paginas` (refinar conforme a aula cita páginas específicas) |
| Avaliação | Inferir do `objetivos_aprendizagem` + composição do dia (igual à Angela) |
| Tarefa de Casa | Conteúdo de `tarefa_casa` (raramente preenchido) |
| CPB / BNCC / Referencial | "X" quando há código correspondente nas competências |

---

## Distribuição capítulo → quinzena

Um capítulo tem 8 aulas tipicamente. Uma quinzena tem 10 slots de LP, 8 de Matemática, 4 de Ciências, etc.

**Antes de mapear, perguntar à Adriana**:

> "Esta quinzena: aulas 1-8 do cap. 6 cabem nos 10 slots de LP. Sobram 2 slots — quer começar o cap. 7 (preciso do docx) ou prefere preencher com revisão / atividade extra?"

Para outras matérias que só têm 4-8 slots na quinzena, **perguntar quais aulas do capítulo entram**:

> "Matemática: você está no cap. 5 do livro de Mat. Quais aulas desse capítulo quer trabalhar nesta quinzena (4 slots disponíveis)?"
