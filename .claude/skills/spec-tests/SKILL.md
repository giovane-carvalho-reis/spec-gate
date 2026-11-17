---
name: spec-tests
description: Define a estrategia de teste por nivel e escreve os casos de teste (TC). Use na etapa tests.
---

# Teste

Escreve `test-strategy.md` e `tests/TC-*.md`.

Templates: `templates/test-strategy.md`, `templates/test-case.md`.

A estratégia define **o que se testa e onde**; o `TC-*` é o caso individual.

Obrigatório ter `TC-*`:
- Toda `BR-*` — regra sem teste é regra que some no refactor.
- Todo cálculo de dinheiro, prazo ou permissão.
- Todo caminho de falha de integração externa.
- Toda query com filtro semântico, contra banco real e não mock.

Preencha "o que deliberadamente não se testa", com o porquê. Lista explícita evita
cobertura escrita por culpa.

`satisfies` do `TC-*` aponta o que ele verifica; o alvo ganha o ID em `verified_by`. O
gate G3 bloqueia referência quebrada nas duas pontas.

## Invariantes (valem em toda skill deste repo)

- Escreva `status: proposed`. **Nunca** `approved` — só o humano promove.
- Faltou informação? Vai para `questions.md`, não para o artefato. Sem suposição.
- Contradição encontrada é reportada, não resolvida.
- Preencha `satisfies` / `verified_by` / `source` na criação.
- Não reescreva artefato `approved`: proponha, e marque dependente como `stale`.
- Ao terminar: `python3 validate.py projects/<slug>` e relate o resultado real.
