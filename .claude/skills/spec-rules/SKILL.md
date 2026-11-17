---
name: spec-rules
description: Escreve as regras de negocio (BR) com enunciado categorico, excecoes e dono. Use na etapa rules.
---

# Regras de negócio

Escreve `rules/BR-*.md`. Template: `templates/rule.md`.

- Enunciado **categórico**. Sem "deveria", sem "normalmente", sem "em geral".
- Condição de aplicação: quando vale e quando **não** vale. A segunda metade é a que
  ninguém escreve e todo mundo descobre em produção.
- Exceções: em que caso a regra é violada de propósito, e quem autoriza.
- Origem: lei, contrato, política, decisão do dono do produto — e **quem pode mudar**.
  Regra sem dono é regra que ninguém defende na primeira pressa.

Toda `BR-*` precisa ser referenciada por alguma `FR-*` em `satisfies`, ou o gate G2
bloqueia. Se não há requisito que a atenda, a pergunta certa é: a regra é real, ou falta
requisito?

## Invariantes (valem em toda skill deste repo)

- Escreva `status: proposed`. **Nunca** `approved` — só o humano promove.
- Faltou informação? Vai para `questions.md`, não para o artefato. Sem suposição.
- Contradição encontrada é reportada, não resolvida.
- Preencha `satisfies` / `verified_by` / `source` na criação.
- Não reescreva artefato `approved`: proponha, e marque dependente como `stale`.
- Ao terminar: `python3 validate.py projects/<slug>` e relate o resultado real.
