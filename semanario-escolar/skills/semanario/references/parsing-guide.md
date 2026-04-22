# Guia de Parsing dos PDFs do Portal CPB

Este guia detalha como extrair dados dos dois tipos de PDF fornecidos pelo portal CPB Educacional.

---

## PDF 1: "Distribuição do Percurso Pedagógico"

É uma **TABELA** com colunas "Aula 1", "Aula 2", ..., "Aula N".

### Estrutura do documento

**Cabeçalho do PDF contém:**
- Matéria, ano, bimestre, capítulo
- Nome do texto/tema (ex: "Para ler 1 - O violino")
- Previsão de aulas (ex: "Previsão: 8 aulas")
- Competências específicas (texto descritivo, NÃO são os códigos BNCC)

**Cada coluna "Aula N" contém:**
- **Topo**: referência de páginas (ex: "p. 7 a 9", "p. 10 e 11") ← ISSO VAI PARA O CAMPO RECURSOS
- **Corpo**: lista de atividades sugeridas ← ISSO VAI PARA O CAMPO DESENVOLVIMENTO

### Como extrair de cada coluna

```
Aula 1                    ← Número da aula no percurso
(p. 7 a 9)                ← RECURSOS: "Apostila p. 7 a 9"
                          
Vamos começar?            ← DESENVOLVIMENTO item 1
                          
• Leitura de imagem (p.7) ← DESENVOLVIMENTO item 2
                          
• Conversa a partir       ← DESENVOLVIMENTO item 3
  das perguntas           
                          
• Boxe - Trocando ideias  ← DESENVOLVIMENTO item 4
```

**Resultado no campo Desenvolvimento:**
`Vamos começar? • Leitura de imagem (p. 7) • Conversa a partir das perguntas • Boxe - Trocando ideias`

### REGRA DE OURO: transcrição literal

- Copiar EXATAMENTE como está no PDF
- Manter nomes de boxes em itálico/negrito como texto: "Boxe - Trocando ideias", "Boxe - Investigue"
- Manter números de atividades: "Atividades 1 a 4", "Atividade 12"
- Manter referências de página: "(p. 7)", "p. 155"
- Manter nomes de seções: "Seção - O que aprendi", "Click: frases"
- Manter tarefas de casa: "Tarefa de casa: coleta de informações e imagens"

### Exemplos reais de parsing correto

**Input (coluna "Aula 1" do percurso de LP Cap. 4):**
```
(p. 7 a 9)
Ponto de partida
• Vídeo "Primavera", de Vivaldi.
• Pergunta prévia
• Leitura do conto em imagens (p. 8 e 9)
• Boxe - Trocando ideias
```

**Output correto:**
- Desenvolvimento: `Ponto de partida • Vídeo "Primavera", de Vivaldi. • Pergunta prévia • Leitura do conto em imagens (p. 8 e 9) • Boxe - Trocando ideias`
- Recursos: `Apostila p. 7 a 9`

**Output ERRADO (inventado):**
- Desenvolvimento: `Introdução ao Capítulo 4. Roda de conversa sobre como nos expressamos oralmente. Planejamento de tempo de fala.`
- Recursos: `Apostila Capítulo 4, p. 8`

### Input (coluna "Aula 2" do percurso de LP Cap. 4):**
```
(p. 10)
Por dentro do texto
instrumentos musicais.
• Atividades 1 a 4.
• Tarefa de casa: trazer materiais que podem se tornar
```

**Output correto:**
- Desenvolvimento: `Por dentro do texto instrumentos musicais. • Atividades 1 a 4.`
- Recursos: `Apostila p. 10`
- Tarefa de casa: `Trazer materiais que podem se tornar [instrumentos musicais]`

---

## Quebra de página — como lidar

### O problema

Quando a tabela do percurso é grande demais para caber numa página do PDF, ela quebra. A parte inferior da página 1 é cortada e continua no topo da página 2.

### Como identificar

1. A página 2 começa com continuação de conteúdo sem cabeçalho novo
2. OU: a página 2 tem um cabeçalho como "Para ler 2 - Carta - Projeto Tupiabá" indicando continuação do mesmo capítulo
3. A numeração de aulas continua (Aula 9, 10, 11...)

### Como tratar

- **Mesmo "Para ler"**: se a pág. 1 termina no meio da Aula 4 e a pág. 2 continua com itens da Aula 4 → JUNTAR os itens
- **"Para ler" diferente**: "Para ler 1" (aulas 1-8) e "Para ler 2" (aulas 9-16) são sequências do MESMO capítulo → tratar como aulas 1-16 contínuas
- **NUNCA** tratar o conteúdo da pág. 2 como uma aula separada se ele é continuação

### Sinais de continuação

- Texto começa com letra minúscula ou sem bullet
- Falta cabeçalho "Aula N" no topo
- Numeração de atividades continua de onde parou (ex: pág. 1 termina com "Atividade 7", pág. 2 começa com "Atividade 8")

---

## PDF 2: "Evidências de Competências"

Lista competências BNCC/CPB organizadas por categoria.

### Estrutura típica

```
Atitudes e Habilidades

Oralidade
(12) (EF35LP20) Expor trabalhos ou pesquisas escolares...
(06) (EF15LP12) Atribuir significado a aspectos não linguísticos...

Leitura
(EF15LP02) Estabelecer expectativas em relação ao texto...
(19) (EF03LP12) Ler e compreender, com autonomia, cartas pessoais...

Análise linguística
(EF02LP07) Escrever palavras, frases, textos curtos...

Produção de textos
(47) (EF35LP09) Organizar o texto em unidades de sentido...
```

### Formato de cada competência

`(código CPB) (código BNCC) Descrição`

- O código CPB é numérico: (12), (06), (47)
- O código BNCC começa com EF: (EF35LP20), (EF15LP12)
- Nem toda competência tem ambos os códigos
- Se tem código BNCC → marcar "X" na coluna BNCC
- Se tem código CPB → marcar "X" na coluna CPB
- Se tem qualquer código referencial → marcar "X" na coluna REFERENCIAL

### ATENÇÃO: quebra de texto nas competências

Competências longas podem quebrar em múltiplas linhas no PDF. Exemplo:

```
(19) (EF03LP12) Ler e compreender, com autonomia, cartas pessoais e diários com expressão de sentimentos e opiniões,
dentre outros gêneros do campo da vida cotidiana, de acordo com as convenções do gênero carta e considerando a situação
comunicativa e o tema/assunto do texto.
```

Isso é UMA competência, não três. Juntar as linhas até encontrar o próximo código `(XX)` ou `(EFXXXXX)`.

---

## Campos do semanário e fonte de cada um

| Campo | O que colocar | Fonte | Se não disponível |
|-------|--------------|-------|-------------------|
| Componente Curricular | Abreviação da matéria | Grade horária fixa | Sempre disponível |
| Objeto do Conhecimento | Tópico/tema da aula | Percurso → Livro virtual → Sugestão | `[Sugestão: ...]` |
| Evidências de Competências | Código + descrição | PDF competências ou banco | VAZIO |
| Desenvolvimento | Atividades EXATAS | PDF percurso — LITERAL | VAZIO |
| Recursos | Páginas da apostila | Topo da coluna do percurso | VAZIO |
| Avaliação | Tipo de registro | Lógica por composição do dia | VAZIO |
| CPB / BNCC / Referencial | "X" quando aplicável | Códigos das competências | Sem marcação |
