---
name: spec-brief
description: Preenche o briefing inicial (brief.md) de um projeto a partir da ideia do usuario. Use ao comecar um projeto novo ou quando o briefing estiver vazio ou raso.
---

# Briefing

Transforma uma ideia solta em `projects/<slug>/brief.md`.

Template: `templates/brief.md`. Preencha as 9 seções a partir do que o usuário disse.

Regras:
- Seção 1 descreve **dor**, não solução. Se o usuário já veio com solução, pergunte qual
  problema ela resolve e escreva a resposta ali.
- Seção 9 (fora de escopo) é a mais valiosa e a que o usuário sempre esquece. Pergunte
  explicitamente: "o que você *não* quer que isso faça?"
- Seção 8 precisa de número, ou de um critério observável. "Ser fácil de usar" não é.
- O que ele não souber vira pergunta em `questions.md`, não texto inventado.

Terminou o brief? Chame `spec-critique` em seguida — nunca pule para requisitos direto.

## Invariantes (valem em toda skill deste repo)

- Escreva `status: proposed`. **Nunca** `approved` — só o humano promove.
- Faltou informação? Vai para `questions.md`, não para o artefato. Sem suposição.
- Contradição encontrada é reportada, não resolvida.
- Preencha `satisfies` / `verified_by` / `source` na criação.
- Não reescreva artefato `approved`: proponha, e marque dependente como `stale`.
- Ao terminar: `python3 validate.py projects/<slug>` e relate o resultado real.
