---
name: spec-interview
description: Conduz a entrevista com o usuario para fechar as lacunas abertas em questions.md e gerar os artefatos correspondentes.
---

# Entrevista

Converte `questions.md` em respostas, e respostas em artefatos.

Processo em `prompts/interview.md`. O essencial:

- Uma pergunta por vez, ou um grupinho relacionado. Nunca despeje a lista inteira.
- Comece pelas `blocking: true`.
- Ofereça um default quando houver um razoável: "A, B ou C? Eu iria de B porque X."
  Escolher é mais fácil que inventar.
- O usuário pode não ser técnico. Pergunte sobre negócio — quem faz o quê, o que não pode
  acontecer, o que acontece quando dá errado. Nunca sobre schema, endpoint ou framework.
- "Não sei" é resposta válida: registre `answer: indefinido` e proponha um `ADR-*` com a
  opção mais reversível.

Cada resposta fechada preenche o campo `answer` e tira o `blocking`.

## Invariantes (valem em toda skill deste repo)

- Escreva `status: proposed`. **Nunca** `approved` — só o humano promove.
- Faltou informação? Vai para `questions.md`, não para o artefato. Sem suposição.
- Contradição encontrada é reportada, não resolvida.
- Preencha `satisfies` / `verified_by` / `source` na criação.
- Não reescreva artefato `approved`: proponha, e marque dependente como `stale`.
- Ao terminar: `python3 validate.py projects/<slug>` e relate o resultado real.
