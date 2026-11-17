---
name: spec-domain
description: Modela o dominio: glossario, entidades, relacoes e invariantes, com classDiagram mermaid. Use na etapa domain.
---

# Domínio

Escreve `domain-model.md`. Template: `templates/domain-model.md`.

Ordem: **glossário primeiro**, diagrama depois. O diagrama só fica estável quando os
termos estão.

- Glossário usa a palavra que o **usuário** usa, não a do banco. Um termo, um significado,
  em todo o PSP. A coluna "não confundir com" é onde o ambíguo morre.
- Diagrama obrigatório: `classDiagram` mermaid (gate G10).
- Invariantes: regra que a estrutura garante **sempre**, independente de fluxo. Cite a
  `BR-*` correspondente.
- "Linguagem proibida": termo herdado ou ambíguo que não deve aparecer no código. Essa
  tabela é o que faz o agente de implementação nomear as coisas certo.

Entidade que nenhum requisito usa é entidade especulativa. Aponte.

## Invariantes (valem em toda skill deste repo)

- Escreva `status: proposed`. **Nunca** `approved` — só o humano promove.
- Faltou informação? Vai para `questions.md`, não para o artefato. Sem suposição.
- Contradição encontrada é reportada, não resolvida.
- Preencha `satisfies` / `verified_by` / `source` na criação.
- Não reescreva artefato `approved`: proponha, e marque dependente como `stale`.
- Ao terminar: `python3 validate.py projects/<slug>` e relate o resultado real.
