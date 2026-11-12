# Fluxo com o catálogo (SurrealDB) — padrão desde out/2026

O percurso de todos os livros do 3º e 5º ano já está extraído no banco (projeto `~/dev/semanario`). A professora **não envia PDF nem DOCX**: a skill lê o catálogo, a grade da turma e o "onde parei", gera a quinzena e grava tudo o que acontece no banco.

## Como chamar a CLI

Sempre com este prefixo (abreviado como `$SEM` abaixo):

```bash
SEM="uv run --project $HOME/dev/semanario --env-file $HOME/dev/semanario/.env semanario-extrator"
```

## Turmas cadastradas

| Professora | Turma | id |
|---|---|---|
| Angela | 3º Ano A | `turma:angela_3a_2026` |
| Adriana | 5º Ano B | `turma:adriana_5b_2026` |

`$SEM turma listar` mostra todas; `$SEM turma mostrar <turma>` traz grade, livros e feriados.

## Ciclo da quinzena

1. **Onde parei**: `$SEM onde-parei <turma>`. Mostra a última aula dada por matéria e a fonte. Ler para a professora e perguntar se está certo.
   - Sem registro ainda (primeira vez): perguntar capítulo e aula de cada matéria, achar o id com `$SEM capitulos <turma> --materia MAT` e gravar com `registrar --tipo ajuste_manual`.
2. **Registrar o que ela disser**, sempre, antes de gerar. Qualquer fala sobre progresso vira registro com a frase literal:
   ```bash
   $SEM registrar <turma> --tipo dito_ao_agente --materia MAT --capitulo capitulo:10136 --aula 5 --frase "fiquei na aula 5 de matemática"
   ```
   `--aula` é a **última aula dada** (0 = capítulo não começou). O registro mais recente prevalece sobre a aprovação da quinzena: essa é a regra de produto, não pular.
3. **Feriados e recessos**: perguntar e gravar no calendário da turma (ficam para as próximas quinzenas):
   ```bash
   $SEM turma feriados <turma> -f 2026-06-04="Corpus Christi" -f 2026-07-13="Recesso:recesso"
   ```
4. **Gerar**: datas em ISO, de segunda a sexta da segunda semana.
   ```bash
   $SEM quinzena <turma> --inicio 2026-05-04 --fim 2026-05-15 --saida /tmp/plano.json
   ```
   Mostra de onde até onde cada matéria vai e os avisos. O plano fica salvo como **rascunho** no banco e em `/tmp/plano.json` (com campos internos `_ref`, que devem ser preservados).
5. **Revisar com a professora**: mostrar, por matéria, as aulas que entraram. Se ela pedir ajuste, editar `/tmp/plano.json` (texto de células, trocar aulas de lugar). Regras de edição:
   - Desenvolvimento continua literal do catálogo; não parafrasear (exceto 5º ano, ver a skill da Adriana).
   - Mover uma aula = mover o objeto inteiro da aula, com o `_ref`.
   - Aula que não vai acontecer: esvaziar `desenvolvimento` e remover o `_ref`.
6. **Excel**: `$SEM excel /tmp/plano.json --saida <arquivo.xlsx>` (ou `--append-to <existente.xlsx>` para nova aba).
7. **Aprovar** quando ela disser que está ok:
   ```bash
   $SEM aprovar quinzena:<turma>_<inicio> --plano /tmp/plano.json --arquivo <arquivo.xlsx>
   ```
   Isso grava a última aula planejada de cada matéria como novo "onde parei".
8. **Enviada**: se ela mandar para a coordenação, `$SEM enviada quinzena:<id> --para coordenacao@...`.

`$SEM historico <turma>` mostra o log de tudo (o que ela disse, aprovações, envios).

## O que o motor já faz sozinho

- 1 aula do percurso = 1 slot da grade; encadeia para o próximo capítulo quando o atual acaba.
- Feriado/recesso ocupa o slot com "FERIADO"/"RECESSO" sem avançar.
- Objeto do conhecimento: tópico vigente do capítulo, seção "Para ler" (LP) ou texto do plano (5º ano).
- Competências: habilidades do capítulo vindas do portal + RAI; marca CPB/BNCC/Referencial.
- Avaliação pela composição do dia; especiais só com o componente (Ed. Física com a professora da grade).
- Tarefa de casa do dia a partir do percurso.

## Quando cair no fluxo antigo (PDF/DOCX)

Só se a CLI falhar (banco fora, `.env` ausente) ou o capítulo estiver marcado para revisão e sem aulas. Avisar a professora e seguir os passos manuais da skill.

## Conta da professora

Cada professora conecta a própria conta do portal (modelo 1 + 2): ela cola o `portal-token` dela no `.env` como `CPB_TOKEN` e roda `$SEM conectar --escola "..."`. Isso cria `professora:<id do portal>` e a relação `acessa` com os livros que a conta dela enxerga. Para a Adriana, que ainda está como pendente: `$SEM conectar --assumir professora:pendente_adriana`.
