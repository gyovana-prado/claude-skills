---
name: semanario-conector
description: "Gera, revisa e aprova o semanário (planejamento quinzenal) de qualquer turma cadastrada usando o conector Semanário (MCP), que lê o catálogo CPB e o progresso da professora direto do banco. Não precisa de PDF, DOCX nem do projeto local. Use quando mencionar: semanário, quinzenário, plano quinzenal, planejamento da quinzena, onde parei, aprovar semanário."
---

# Semanário pelo conector

Toda a lógica (catálogo dos livros, grade da turma, "onde parei", motor que distribui as aulas, Excel no modelo da escola) roda no servidor. Esta skill só conduz a conversa com a professora e chama as tools do conector **Semanário**.

**Antes de tudo:** confira se as tools do conector estão disponíveis (`listar_turmas`, `gerar_quinzena` etc.). Se não estiverem, diga à professora que o conector Semanário não está conectado nesta conversa e pare. Não tente montar o semanário por conta própria.

## Tools

| Tool | Para quê |
|---|---|
| `listar_turmas` | Turmas (id, professora, série) e quinzenas de cada uma (id, período, status) |
| `ver_onde_parei` / `definir_onde_parei` | Última aula dada por matéria / registrar o que a professora disse |
| `listar_capitulos` | Achar o capítulo quando ela fala "capítulo 3 de Matemática" |
| `definir_feriados` | Feriados e recessos permanentes no calendário da turma |
| `gerar_quinzena` | Gera o rascunho a partir do catálogo, da grade e do "onde parei" |
| `ver_quinzena` | Plano completo, dia a dia |
| `trocar_aula` | Muda o texto de uma aula (objeto, desenvolvimento, avaliação, recursos) |
| `listar_versoes` / `restaurar_versao` | Toda mudança vira versão; dá para voltar |
| `exportar_quinzena` | Excel no modelo oficial da escola (devolve link) |
| `aprovar_quinzena` | Aprova e grava o novo "onde parei" |
| `marcar_enviada` | Registra que foi para a coordenação |
| `ver_historico` | Log de tudo que aconteceu na turma |

Em clientes com tela (claude.ai, ChatGPT), `abrir_semanario`, `gerar_quinzena` e `ver_quinzena` também abrem a UI ao lado do chat. Sem tela, o resultado vem em JSON e a conversa segue igual.

## Ciclo da quinzena

### 1. Turma

Chame `listar_turmas`. Se só uma turma combina com quem está falando (pelo nome da professora), use essa. Senão, pergunte qual. Hoje existem `turma:angela_3a_2026` (Angela, 3º Ano A) e `turma:adriana_5b_2026` (Adriana, 5º Ano B), mas confie no que a tool devolver.

### 2. Onde parei

Chame `ver_onde_parei` e leia para a professora, por matéria: capítulo, última aula dada e a fonte. Pergunte se está certo.

**Tudo que ela disser sobre progresso vira registro, antes de gerar**, com a frase literal dela:

- "Fiquei na aula 5 do capítulo 3 de Matemática" → `definir_onde_parei(materia="Matemática", capitulo="3", ultima_aula=5, frase="fiquei na aula 5 do capítulo 3 de matemática")`
- "Começa Ciências do capítulo 4" → `capitulo="4", ultima_aula=0`
- Na dúvida sobre qual capítulo, `listar_capitulos` com a matéria.

O registro mais recente sempre prevalece, inclusive sobre a quinzena aprovada. Essa é a regra do produto: não pule o registro mesmo que pareça redundante.

Se ela quiser começar de outro ponto **só nesta quinzena**, sem mudar o "onde parei", use o parâmetro `comecar` do `gerar_quinzena` em vez de `definir_onde_parei`.

### 3. Feriados

Pergunte se há feriado ou recesso no período.

- Feriado do calendário escolar (vale para o ano): `definir_feriados(feriados=["2026-11-20=Consciência Negra", "2026-12-21=Recesso:recesso"])`.
- Algo só desta quinzena: passe em `feriados` do `gerar_quinzena`.

O motor ocupa o slot com FERIADO/RECESSO e não avança a aula.

### 4. Gerar

Datas em AAAA-MM-DD, segunda da primeira semana até sexta da segunda. Se ela disser só "a próxima quinzena", calcule a partir da última quinzena em `listar_turmas`.

`gerar_quinzena(turma_id, inicio, fim)`. Leia os `avisos` do resultado e repasse os relevantes (matéria sem registro começando do capítulo 1, capítulo que acabou etc.).

Se já existe quinzena desse período em rascunho, ela é regerada e a anterior fica como versão. Se estiver aprovada ou enviada, a tool recusa: só use `sobrescrever=true` se a professora pedir explicitamente.

### 5. Revisar com a professora

Mostre, por matéria, de onde até onde a quinzena vai (capítulo e aulas) e, se ela quiser, o detalhe por dia (`ver_quinzena`). Ajustes:

- Mudar texto de uma aula → `trocar_aula(quinzena_id, dia="18/11", numero=2, frase=<o que ela disse>, desenvolvimento=...)`. `dia` é a data como aparece no plano; `numero` é a posição da aula no dia.
- Mudar onde uma matéria começa → `definir_onde_parei` e gere de novo.
- Errou alguma coisa → `listar_versoes` e `restaurar_versao`.

**Regras de conteúdo:**

- **3º ano (formato percurso):** o Desenvolvimento é transcrição literal do percurso CPB. Não parafraseie nem "melhore". Se ela pedir para mudar, aplique exatamente o que ela pediu.
- **5º ano (formato plano de aula):** o Desenvolvimento sai do catálogo com os parágrafos inteiros do plano. Condense cada aula em 1 a 3 frases (cerca de 150 a 300 caracteres), separadas por " • ", mantendo literais as páginas (`p. 46`), nomes de boxes (`"Trocando Ideias"`) e seções. Mostre os condensados por matéria para ela validar **antes** de gravar e só então aplique com `trocar_aula` (na `frase`, registre que foi a condensação aprovada por ela).
- Objeto do conhecimento nunca é só "Capítulo X".
- Aulas especiais (Ed. Física, Arte, Bilíngue, Cultura Maker, Cultura Geral) não têm conteúdo do catálogo. Não invente.

### 6. Excel

`exportar_quinzena` e entregue o link. É o modelo oficial da escola: não monte planilha por conta própria.

### 7. Aprovar

Só quando ela disser que está ok: `aprovar_quinzena(quinzena_id, frase=<o que ela disse>)`. Isso grava a última aula planejada de cada matéria como o novo "onde parei". Confirme para ela onde cada matéria vai começar na próxima quinzena.

### 8. Enviada

Se ela mandar para a coordenação: `marcar_enviada(quinzena_id, para=[...])`. A tool só registra; o envio é por fora (e-mail etc.).

## Erros

- Tool devolveu erro com mensagem: leia a mensagem, corrija o argumento (data, capítulo, número da aula) e tente de novo uma vez. Se persistir, explique para a professora em linguagem simples.
- Conector fora do ar (erro de conexão, 502): avise que o servidor do Semanário não respondeu e peça para tentar mais tarde. Não gere o semanário de cabeça.
