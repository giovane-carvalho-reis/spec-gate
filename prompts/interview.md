# Prompt — Entrevista para fechar lacunas

Objetivo: converter `questions.md` em respostas, e as respostas em artefatos.

## Condução

- Uma pergunta por vez, ou um grupo pequeno de perguntas relacionadas. Nunca despeje 15.
- Comece pelas `blocking: true`.
- Ofereça opções quando houver um default razoável: "A, B ou C? Eu iria de B porque X."
  É mais fácil escolher do que inventar.
- Aceite "não sei". Registre como `answer: indefinido` e proponha a decisão mais reversível,
  como `ADR-*` com status Proposta.
- O usuário pode não ser técnico. Pergunte sobre o negócio, nunca sobre schema, endpoint,
  padrão de projeto ou framework.

## Ao receber a resposta

1. Escreva a resposta no campo `answer` da pergunta, e tire o `blocking`.
2. Gere o artefato correspondente a partir do template, com `status: proposed`.
3. Preencha `satisfies`, `verified_by` e `source` — rastreabilidade na criação, não depois.
4. Diga ao usuário o que foi criado e que ele precisa aprovar (`status: approved`).

## Proibido

- Marcar `approved` por conta própria. Aprovação é humana.
- Inventar critério de aceitação que o usuário não confirmou.
- Reescrever ou apagar artefato já `approved`. Proponha a mudança e marque o dependente
  como `stale`.
