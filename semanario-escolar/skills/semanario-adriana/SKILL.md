---
name: semanario-adriana
description: "Gera o semanário em Excel para a Professora Adriana (5º Ano B) a partir do catálogo de planos de aula no banco (sem DOCX) e registra o progresso dela. Use quando mencionar: semanário Adriana, quinzenário 5º ano, plano quinzenal 5º B."
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
---

# Gerador de Semanário Escolar — Professora Adriana (5º Ano B)

Gera a planilha Excel do semanário (planejamento quinzenal) para a Professora **Adriana dos Santos Negretti** do 5º Ano B, parseando os DOCX de Plano de Aula da CPB.

## Contexto rápido

- Matérias core (responsabilidade da Adriana): LP, Matemática, Ciências, História, Geografia, Ensino Religioso
- Matérias especiais (outros professores): Ed. Física, Arte, Bilíngue, Cultura Maker, Cultura Geral
- **Input fundamental**: a Adriana recebe **um DOCX por capítulo**, em formato narrativo (não tabela). As habilidades BNCC já vêm dentro do docx.
- **Diferença chave vs Angela**: o desenvolvimento precisa ser **CONDENSADO** (parágrafos longos → 1-3 frases por aula)

## Modo padrão: catálogo no banco (sem PDF)

**Desde out/2026 a skill não pede mais PDF/DOCX.** O percurso de todos os capítulos está no SurrealDB e o que a professora faz fica registrado lá. Seguir:

```
Read ${CLAUDE_PLUGIN_ROOT}/shared/catalogo-db.md
```

Turma: `turma:adriana_5b_2026`. Ciclo resumido:

1. `onde-parei` → confirmar com a professora; o que ela disser vira `registrar --tipo dito_ao_agente` com a frase literal (prevalece sempre).
2. Perguntar feriados/recessos do período → `turma feriados`.
3. `quinzena --inicio --fim --saida /tmp/plano.json` → revisar com ela, editar o JSON se pedir.
4. `excel` → `aprovar --plano /tmp/plano.json` → `enviada` se mandar para a coordenação.

**5º ano: condensar depois de gerar.** No 5º ano o campo Desenvolvimento sai do catálogo com todos os parágrafos do plano de aula (introdução, desenvolvimento, conclusão). Depois de gerar, condensar cada um em `/tmp/plano.json` seguindo o Passo 4 (1-3 frases, literais preservados), mostrar para a Adriana validar e só então gerar o Excel. A grade dela está como INFERIDA: confirmar no primeiro uso (Passo 1) e, se mudar, reimportar com `turma importar`.

Os Passos abaixo (coletar PDF/DOCX, parsear, mapear na grade) são o **fluxo de reserva**: usar só se a CLI falhar ou o capítulo não tiver aulas no catálogo. As regras de conteúdo (transcrição literal, objeto do conhecimento, competências, avaliação, checklist final) continuam valendo para revisar o plano gerado.

## Passo 0: Carregar referências (fluxo de reserva)

Antes de qualquer coisa, ler os arquivos de suporte:

```
Read ${CLAUDE_PLUGIN_ROOT}/skills/semanario-adriana/references/grade_horaria_5anoB.json
Read ${CLAUDE_PLUGIN_ROOT}/skills/semanario-adriana/references/parsing-guide-docx.md
```

## Passo 1: Confirmar grade horária (PRIMEIRA VEZ)

Verificar `status_confirmacao` em `grade_horaria_5anoB.json`. Se for **"INFERIDA"**, perguntar à Adriana:

> "Antes de gerar, preciso confirmar sua grade horária do 5º Ano B. A que tenho registrada é:
> - SEG: LP / Bilíngue / Mat / Ciências / Ed.Física
> - TER: Bilíngue / Bilíngue / Arte / LP / Mat
> - QUA: LP / Ciências / Ens.Rel / Geografia / História
> - QUI: LP / História / Mat / Bilíngue / Cult.Maker
> - SEX: Bilíngue / Cult.Geral / Mat / LP / Ens.Rel
>
> Está correta? Algum ajuste?"

Aplicar os ajustes e mudar `status_confirmacao` para `"CONFIRMADA"`.

## Passo 2: Coletar inputs — PERGUNTAR TUDO ANTES DE COMEÇAR

### 2.1 Dados obrigatórios

- **Data de início da quinzena** (ex: 02/06/2026)
- **Feriados, recessos ou eventos especiais no período?** (ex: "Reunião de Pais quarta dia 03/06; feriado 06/06")
- **Arquivo .xlsx existente** para adicionar nova aba? Ou criar arquivo novo?

### 2.2 Para CADA matéria core — perguntar individualmente

> "Para cada matéria, me diga:
> 1. Em qual capítulo você está? (ex: LP no Cap. 6, Mat no Cap. 5)
> 2. Me envie o **DOCX do plano de aula** do capítulo
> 3. Quais aulas do capítulo entram nesta quinzena? (ex: aulas 1 a 6 do cap. 6)"

Se a quinzena atravessa capítulos:

> "A quinzena tem 10 slots de LP mas o cap. 6 só tem 8 aulas. Quer:
> a) Começar o cap. 7 (preciso do DOCX dele)
> b) Preencher os 2 slots restantes com revisão / atividade extra
> c) Outra opção"

Registrar claramente o que foi recebido:

```
✅ LP: docx do cap. 6 recebido — usar aulas 1-8 + revisão nos 2 slots restantes
✅ Mat: docx do cap. 5 recebido — usar aulas 3-6 (4 slots)
❌ Ciências: Nenhum input — campos ficarão vazios
❌ História: Nenhum input — campos ficarão vazios
```

### 2.3 Inputs opcionais

- **Materiais solicitados**: itens que os alunos devem trazer
- **Observações específicas**: avisos ou ênfases da Adriana para a quinzena

## Passo 3: Parsear cada DOCX

Para cada matéria que teve docx fornecido, rodar:

```bash
uv run python ${CLAUDE_PLUGIN_ROOT}/skills/semanario-adriana/scripts/parse_plano_aula.py <docx_path> <output.json>
```

O parser extrai:
- Cabeçalho (capítulo, texto, páginas, duração)
- Objetos de conhecimento
- Habilidades BNCC por categoria
- Objetivos de aprendizagem
- Materiais, princípios, interdisciplinaridade
- Cada aula (introducao / desenvolvimento / conclusao / tarefa_casa)

## Passo 4: Condensar o Desenvolvimento — ETAPA CRÍTICA

Ler o guia completo:

```
Read ${CLAUDE_PLUGIN_ROOT}/skills/semanario-adriana/references/parsing-guide-docx.md
```

Para CADA aula do percurso a ser usada:

1. Ler os blocos `introducao`, `desenvolvimento`, `conclusao` do JSON parseado
2. Identificar a sequência de **verbos-ação** principais
3. Produzir um Desenvolvimento condensado de 1-3 frases (~150-300 chars), separadas por " • "
4. **Manter literais**: páginas (`p. 46`), nomes de boxes (`"Trocando Ideias"`), nomes de seções
5. Cortar exemplos longos, links e detalhes que não cabem no Excel

### Validação humana ANTES de gerar o Excel

Mostrar para o usuário:

```
LP - Cap. 6 — Desenvolvimentos condensados:

AULA 1: Apresentar texto do Matteo e debater propostas. • Diálogo prévio (p. 46) • Leitura de "Governar" com estratégias de antecipação e inferência • Boxe "Trocando Ideias"
AULA 2: Releitura de "Governar". • Atividades 2-7 (p. 47-48): elementos da narrativa (tempo, espaço, narrador, clímax, desfecho)
...

OK? Quer ajustar algum?
```

Aplicar os ajustes antes de prosseguir.

## Passo 5: Objeto do Conhecimento — regra de prioridade

Para cada aula:

1. **Aula menciona um tópico específico** (ex: "Aula 4 — Concordância verbal" no texto da aula) → usar como Objeto
2. **Lista de Objetos do cabeçalho** → distribuir conforme o foco da aula:
   - Aula 1-2: "Estratégias e procedimentos de leitura"
   - Aula 3: "Dialogia e relação entre textos"
   - Aula 4-5: "Forma de composição dos textos (concordância verbal)"
   - Aula 6: "Pontuação (discurso direto)"
   - Aula 7: "Conhecimento das diversas grafias do alfabeto (acentuação)"
   - Aula 8: "Construção da textualidade (elementos estruturais da narrativa)"
3. **Nada disponível** → sugestão entre colchetes: `[Sugestão: ...]`

**NUNCA** usar apenas "Capítulo X" como objeto do conhecimento.

## Passo 6: Competências — hierarquia de busca

### 6.1 Prioridade de fontes

1. **Habilidades BNCC do cabeçalho do docx** → primeira escolha (mais específicas ao capítulo)
2. **Banco RAI 5º ano** (`competencias_rai_5ano.json`) → fallback se algo faltar
3. **Banco por capítulo** (`competencias.json`) → reuso de quinzenas anteriores

### 6.2 Associação competência → aula (N:N)

Igual à skill da Angela: uma aula pode mobilizar múltiplas competências (Leitura + Oralidade, por exemplo). Listar todas as competências relevantes, separadas por quebra de linha.

**Exemplo:**

```
(EF35LP22) Perceber diálogos em textos narrativos, observando o efeito de sentido de verbos de enunciação...
(EF15LP13) Identificar finalidades da interação oral em diferentes contextos...
```

### 6.3 Buscar no banco RAI quando faltar

```bash
uv run python ${CLAUDE_PLUGIN_ROOT}/skills/semanario-adriana/scripts/manage_competencias.py rai --materia lp
uv run python ${CLAUDE_PLUGIN_ROOT}/skills/semanario-adriana/scripts/manage_competencias.py rai --materia mat --categoria Geometria
```

## Passo 7: Mapear na grade horária

Ler `grade_horaria_5anoB.json` e distribuir aulas:

- LP: 10 slots na quinzena (SEG 1ª, TER 4ª, QUA 1ª, QUI 1ª, SEX 4ª × 2 semanas)
- Mat: 8 slots (SEG 3ª, TER 5ª, QUI 3ª, SEX 3ª × 2 semanas)
- Ciências: 4 slots (SEG 4ª, QUA 2ª × 2 semanas)
- História: 4 slots (QUA 5ª, QUI 2ª × 2 semanas)
- Geografia: 2 slots (QUA 4ª × 2 semanas)
- Ensino Religioso: 4 slots (QUA 3ª, SEX 5ª × 2 semanas)

**Regra**: 1 aula do plano = 1 slot.

### Feriados, recessos e eventos

Para cada dia de feriado/recesso/evento:
- Preencher componente curricular normalmente
- Desenvolvimento = "FERIADO" ou "RECESSO" ou "REUNIÃO DE PAIS E MESTRES" etc.
- Demais campos vazios
- Aulas NÃO avançam (slot perdido)

## Passo 8: Avaliação — composição do dia

Pelo quinzenário real, a Adriana usa avaliações curtas e padronizadas:
- "Participação, envolvimento nas atividades e questionamentos do debate."
- "Correção coletiva e participação nos questionamentos."
- "Envolvimento nas atividades."
- Em aulas com produção: descrição específica do que avaliar (ex: "Avaliar a capacidade de identificar elementos da narrativa.")

Sem percurso → campo Avaliação **VAZIO**.

## Passo 9: Datas

1. Partir da data de início
2. Domingo → avançar para segunda
3. Seq: seg-sex semana 1, seg-sex semana 2. Formato DD/MM
4. Marcar feriados/recessos conforme usuário informou

## Passo 10: Aulas especiais

Matérias especiais (Bilíngue, Arte, Cult. Maker, Cult. Geral, Ed. Física) — preencher apenas:
- Componente Curricular (com a abreviação)
- Objeto do Conhecimento = horário da aula (ex: "7H50 - 8H50") ou nome do professor

Demais campos vazios.

## Passo 11: Gerar JSON e Excel

### Abreviações

LING. PORT. | MATEMÁTICA | CIÊNCIAS | HISTÓRIA | GEOGRAFIA | ENSINO REL. | ED. FÍSICA | ARTE | BILÍNGUE | CULT. MAKER | CULT. GERAL

### Schema JSON

```json
{
  "professora": "ADRIANA DOS SANTOS NEGRETTI",
  "turma": "5º ANO - B",
  "quinzena": "02 a 13 de junho",
  "materiais": "",
  "semanas": [
    {
      "dias": [
        {
          "dia_semana": "SEGUNDA-FEIRA",
          "data": "02/06",
          "aulas": [
            {
              "numero": "1ª",
              "componente": "LING. PORT.",
              "objeto_conhecimento": "Estratégias e procedimentos de leitura",
              "competencias": "(EF35LP22) Perceber diálogos em textos narrativos...\n(EF15LP13) Identificar finalidades da interação oral...",
              "desenvolvimento": "Apresentar texto do Matteo e debater propostas. • Leitura de \"Governar\" com estratégias de antecipação e inferência (p. 46) • Boxe \"Trocando Ideias\"",
              "recursos": "Livro p. 46",
              "avaliacao": "Participação, envolvimento nas atividades e questionamentos do debate.",
              "cpb": "",
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
uv run --with openpyxl python ${CLAUDE_PLUGIN_ROOT}/shared/generate_semanario.py <input.json> <output.xlsx>
```

**Append:**
```bash
uv run --with openpyxl python ${CLAUDE_PLUGIN_ROOT}/shared/generate_semanario.py <input.json> --append-to <existing.xlsx> <output.xlsx>
```

### Abas

- Mesmo mês: "02-13 Jun" / Meses diferentes: "30Mai-10Jun" / Duplicata: "(2)"

Perguntar: "Tem o arquivo anterior para adicionar aba, ou cria novo?"

## Passo 12: Checklist final — NUNCA PULAR

- [ ] Grade horária do 5º B foi CONFIRMADA pela Adriana?
- [ ] Cada matéria no capítulo correto? (perguntar antes de gerar)
- [ ] Desenvolvimentos foram CONDENSADOS (não copiados literalmente dos parágrafos do docx)?
- [ ] Páginas literais preservadas (`(p. 46)`, etc.)?
- [ ] Nomes de boxes mantidos entre aspas?
- [ ] Versão condensada foi VALIDADA pelo usuário antes de gerar Excel?
- [ ] Nenhum "Objeto do Conhecimento" é apenas "Capítulo X"?
- [ ] Competências de input real (docx ou banco RAI)?
- [ ] Feriados/recessos/eventos marcados?
- [ ] Datas sequenciais e corretas?
- [ ] Aulas especiais só com placeholder (horário)?
- [ ] CPB/BNCC/Referencial corretos? (BNCC=EF..., CPB=numérico)
