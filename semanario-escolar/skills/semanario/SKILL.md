---
name: semanario
description: "Gera o semanário escolar em Excel para a Professora Angela do 3º Ano A. Use quando mencionar: semanário, quinzenário, plano de aulas, plano quinzenal, planejamento semanal, gerar semanário, preencher semanário."
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Agent
  - Glob
  - Grep
---

# Gerador de Semanário Escolar - 3º Ano A

Gera a planilha Excel do semanário (planejamento quinzenal) para a Professora Angela do 3º Ano A, parseando os PDFs/textos do portal CPB Educacional.

## Contexto rápido

A Professora Angela leciona as matérias "core": Língua Portuguesa, Matemática, Ciências, História, Geografia e Ensino Religioso. As matérias especiais (Ed. Física, Arte, Bilíngue, Cultura Maker, Cultura Geral) são de outros professores.

## Passo 0: Carregar referências

Antes de qualquer coisa, ler os arquivos de suporte:

```
Read ${CLAUDE_PLUGIN_ROOT}/skills/semanario/references/grade_horaria.json
Read ${CLAUDE_PLUGIN_ROOT}/skills/semanario/references/parsing-guide.md
```

## Passo 1: Coletar inputs — PERGUNTAR TUDO ANTES DE COMEÇAR

Antes de gerar qualquer conteúdo, fazer TODAS estas perguntas ao usuário:

### 1.1 Dados obrigatórios

- **Data de início da quinzena** (ex: 13/04/2025)
- **Feriados ou recessos no período?** (ex: "20/04 recesso, 21/04 feriado Tiradentes")
- **Arquivo .xlsx existente** para adicionar nova aba? Ou criar arquivo novo?

### 1.2 Para CADA matéria core — perguntar individualmente

Cada matéria pode estar em um capítulo e aula DIFERENTES. Perguntar:

> "Para cada matéria, me diga:
> 1. Em qual capítulo e aula vocês estão? (ex: LP no Cap. 4 aula 6 / Matemática no Cap. 5 aula 1)
> 2. Me envie o PDF ou texto do percurso pedagógico dessa matéria
> 3. Me envie o PDF ou texto de competências (se tiver — se não tiver, verifico no banco)"

Registrar claramente o que foi recebido:
```
✅ LP: Percurso Cap. 4 (aulas 1-8) + Competências Cap. 4
✅ História: Percurso Cap. 4 (aulas 1-5) + Competências via banco
❌ Matemática: Nenhum input — campos ficarão vazios
❌ Ciências: Nenhum input — campos ficarão vazios
❌ Geografia: Nenhum input — campos ficarão vazios
❌ Ensino Religioso: Nenhum input — campos ficarão vazios
```

### 1.3 Inputs opcionais

- **Prints ou texto do livro virtual**: se o usuário enviar capturas de tela ou texto copiado da apostila digital, usar para enriquecer o "Objeto do Conhecimento" e "Atividades práticas"
- **Materiais solicitados**: itens que os alunos devem trazer

## Passo 2: Parsear o Percurso Pedagógico

Para cada matéria que teve percurso fornecido, seguir o guia detalhado:

```
Read ${CLAUDE_PLUGIN_ROOT}/skills/semanario/references/parsing-guide.md
```

### REGRA ABSOLUTA: TRANSCRIÇÃO LITERAL

O campo "Desenvolvimento" deve ser uma **cópia exata** dos bullet points do percurso pedagógico, separados por " • ". Copiar EXATAMENTE como está no PDF — nomes de boxes, números de atividades, referências de páginas.

**CERTO** (texto literal do percurso):
> `Boxe - Vamos começar? • Boxe - Trocando ideias • Tópico 1: O nome do bairro diz muito sobre ele (p. 153 a 155)`

**ERRADO** (texto inventado/parafraseado):
> `Introdução ao capítulo com discussão sobre bairros e atividades de leitura.`

Se o desenvolvimento real não estiver disponível → campo fica **VAZIO**.

### Parsing de cada coluna "Aula N"

De cada coluna do percurso extrair:

1. **paginas**: texto no topo da coluna (ex: "p. 153 a 155")
2. **atividades**: lista EXATA das atividades, na ordem do PDF
3. **tarefa_casa**: se mencionada (ex: "Tarefa de casa: Boxe - Investigue – p. 155")

### Montagem dos campos

| Campo | Como preencher | Fonte |
|-------|---------------|-------|
| Desenvolvimento | Concatenar atividades com " • " | Coluna do percurso — LITERAL |
| Recursos | "Apostila p. X a Y" usando páginas do TOPO da coluna | Coluna do percurso |
| Competências | Código + descrição BNCC/CPB | PDF de competências ou banco |
| Avaliação | Baseada na composição do dia | Ver Passo 6 |

### Quebra de página no PDF — CUIDADO

Quando a tabela do percurso quebra entre páginas do PDF:
- O conteúdo da próxima página é **continuação**, NÃO uma nova entrada
- Identificar pela sequência numérica: se pág. 1 tem Aulas 1-8 e pág. 2 tem Aulas 9-16 = mesmo capítulo
- Juntar tudo antes de distribuir na grade

## Passo 3: Objeto do Conhecimento — regra de prioridade

Ordem de prioridade:

1. **Percurso traz o tópico** → usar o tópico literal
   - Ex: "Tópico 1: O nome do bairro diz muito sobre ele" → usar como está

2. **Livro virtual fornecido** → usar título/tópico do livro
   - Ex: print mostra "Subtração e fatos fundamentais" → usar como está

3. **Nenhum disponível** → sugestão clara entre colchetes
   - Ex: `[Sugestão: Classificação de animais vertebrados — verificar apostila p. 72]`

**NUNCA** usar apenas "Capítulo X" como objeto do conhecimento.

## Passo 4: Competências — hierarquia de busca

### 4.1 Prioridade de fontes

1. **PDF de competências fornecido pelo usuário** → usa diretamente (mais específico ao capítulo)
2. **Banco por capítulo** (competencias.json) → competências já salvas de quinzenas anteriores
3. **Banco RAI master** (competencias_rai_3ano.json) → 194 competências do 3º ano completo

### 4.2 Comandos

**Verificar banco por capítulo:**
```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/semanario/scripts/manage_competencias.py list
```

**Buscar no banco RAI por matéria:**
```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/semanario/scripts/manage_competencias.py rai --materia lp
```

**Buscar no RAI por categoria:**
```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/semanario/scripts/manage_competencias.py rai --materia lp --categoria Oralidade
```

**Buscar no RAI por termo:**
```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/semanario/scripts/manage_competencias.py rai --materia mat --busca "multiplicação"
```

**Buscar competência por código:**
```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/semanario/scripts/manage_competencias.py rai --materia lp --codigo EF03LP01
```

**Aliases de matéria:** lp, mat, cie, geo, his, er (ou nomes completos)

### 4.3 Fluxo de decisão

1. Se o usuário mandou PDF de competências do capítulo → usar essas
2. Se não, verificar banco por capítulo (`list` / `get`)
3. Se não encontrou, buscar no banco RAI (`rai --materia X --categoria Y`)
4. Se o usuário fornecer novas competências, perguntar se quer salvar no banco por capítulo

### 4.4 Associação competência → aula (relação N:N)

**REGRA FUNDAMENTAL:** Uma aula pode ter MÚLTIPLAS competências e uma competência pode aparecer em MÚLTIPLAS aulas. A relação é N:N, não 1:1.

**Por que isso acontece:** Uma aula de Língua Portuguesa que trabalha interpretação de texto mas inclui uma atividade oral (ex: "Trocando ideias") mobiliza competências de Leitura E de Oralidade ao mesmo tempo. Uma aula de Matemática que usa gráficos pode mobilizar Números E Probabilidade e estatística.

**Como associar:**

1. Ler o conteúdo/desenvolvimento da aula e identificar TODAS as práticas/habilidades envolvidas
2. Para cada prática identificada, buscar a(s) competência(s) correspondente(s) no banco RAI
3. Listar todas na célula de competências, separadas por quebra de linha

**Guia por matéria:**

- **Língua Portuguesa:** analisar quais práticas de linguagem a aula mobiliza:
  - Leitura de texto → competências de Leitura
  - Discussão oral, roda de conversa, boxe "Trocando ideias" → + competências de Oralidade
  - Exercício de gramática, ortografia → + competências de Análise linguística
  - Produção escrita (redação, reescrita) → + competências de Produção de textos
  - **Uma mesma aula frequentemente mobiliza 2-3 práticas**
- **Matemática:** unidade temática (Números, Álgebra, Geometria, Grandezas e medidas, Probabilidade e estatística). Uma aula de problemas pode envolver Números + Álgebra.
- **Ciências:** unidade temática (Matéria e energia, Vida e evolução, Terra e Universo)
- **Geografia/História/Ensino Religioso:** associar pelo(s) objeto(s) de conhecimento mais próximo(s)

**Formato na célula:** listar os códigos com descrição, um por linha. Exemplo:
```
(EF15LP02) Estabelecer expectativas em relação ao texto...
(EF15LP09) Expressar-se em situações de intercâmbio oral...
```

## Passo 5: Mapear na grade horária

Ler `${CLAUDE_PLUGIN_ROOT}/skills/semanario/references/grade_horaria.json`.

**Regra: 1 aula do percurso = 1 slot de 45 minutos.**

### Contagem por quinzena

- Língua Portuguesa: 5/semana → 10 na quinzena
- Matemática: 3/semana → 6 na quinzena
- Ciências, História, Geografia, Ensino Religioso: 2/semana → 4 na quinzena

### Distribuição

Sequencial: Aula 1 → primeiro slot, Aula 2 → segundo slot, etc.
Consultar `distribuicao_semanal_por_materia` no JSON.

- Mais aulas que slots → distribuir as que cabem, avisar usuário
- Menos aulas que slots → preencher o que tem, restante vazio

### Feriados e recessos

Para cada dia de feriado/recesso:
- Preencher componente curricular normalmente
- Desenvolvimento = "FERIADO" ou "RECESSO"
- Demais campos vazios
- Aulas NÃO avançam (slot perdido)

## Passo 6: Avaliação — composição do dia

Consultar `composicao_diaria` na grade horária.

**4 core (Seg, Qui):** rápida → "Registro na apostila." / "Participação oral."
**2 core (Ter):** elaborada → "Produção textual avaliada." / "Apresentação oral com roteiro."
**3 core (Qua, Sex):** padrão. Sexta 5ª aula (LP): preferir "Registro na apostila."

Sem percurso → campo Avaliação **VAZIO**.

## Passo 7: Datas

1. Partir da data de início
2. Domingo → avançar para segunda
3. Seq: seg-sex semana 1, seg-sex semana 2. Formato DD/MM
4. Marcar feriados/recessos conforme usuário informou

## Passo 8: Aulas especiais

- ED. FÍSICA → "Professora Bárbara" no objeto do conhecimento
- ARTE, BILÍNGUE, CULT. MAKER, CULT. GERAL → apenas componente, sem conteúdo

## Passo 9: Gerar JSON e Excel

### Abreviações

LING. PORT. | MATEMÁTICA | CIÊNCIAS | HISTÓRIA | GEOGRAFIA | ENSINO REL. | ED. FÍSICA | ARTE | BILÍNGUE | CULT. MAKER | CULT. GERAL

### Schema JSON

```json
{
  "professora": "ANGELA DOS SANTOS PRADO",
  "turma": "3º ANO - A",
  "quinzena": "13 à 24 de abril",
  "materiais": "",
  "semanas": [
    {
      "dias": [
        {
          "dia_semana": "SEGUNDA-FEIRA",
          "data": "14/04",
          "aulas": [
            {
              "numero": "1ª",
              "componente": "LING. PORT.",
              "objeto_conhecimento": "Tópico real da aula",
              "competencias": "(12) (EF35LP20) Texto completo...",
              "desenvolvimento": "Boxe - Vamos começar? • Leitura de imagem (p. 7) • Conversa a partir das perguntas",
              "recursos": "Apostila p. 7 a 9",
              "avaliacao": "Participação oral e registro na apostila.",
              "cpb": "X",
              "bncc": "X",
              "referencial": "X",
              "outros": ""
            }
          ],
          "tarefa_casa": ""
        }
      ]
    }
  ]
}
```

### Comandos

**Novo:**
```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/semanario/scripts/generate_semanario.py <input.json> <output.xlsx>
```

**Append:**
```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/semanario/scripts/generate_semanario.py <input.json> --append-to <existing.xlsx> <output.xlsx>
```

### Abas

- Mesmo mês: "13-24 Abr" / Meses diferentes: "28Abr-09Mai" / Duplicata: "(2)"

Perguntar: "Tem o arquivo anterior para adicionar aba, ou cria novo?"

## Passo 10: Checklist final — NUNCA PULAR

- [ ] Todo "Desenvolvimento" é transcrição LITERAL do percurso?
- [ ] Páginas em "Recursos" vieram do TOPO da coluna do percurso (NÃO do cabeçalho do PDF de competências)?
- [ ] Nenhum "Objeto do Conhecimento" é apenas "Capítulo X"?
- [ ] Campos sem dados estão realmente VAZIOS?
- [ ] Feriados/recessos marcados?
- [ ] Cada matéria no capítulo/aula correto? (podem ser diferentes!)
- [ ] Competências de input real (PDF, texto ou banco)?
- [ ] Datas sequenciais e corretas?
- [ ] Aulas especiais só com placeholder?
- [ ] CPB/BNCC/Referencial corretos? (BNCC=EF..., CPB=numérico)
