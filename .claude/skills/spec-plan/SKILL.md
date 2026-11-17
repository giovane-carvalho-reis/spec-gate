---
name: spec-plan
description: Monta o plano de implementacao fatiado em entregas demonstraveis de ponta a ponta. Use na etapa plan, por ultimo.
---

# Plano de implementação

Escreve `plan.md`. Template: `templates/plan.md`.

Para fatiar, delegue ao subagente **`spec-estimator`** — ele lê todos os requisitos em
contexto próprio e devolve só a proposta de fatias:

```
Agent(subagent_type="spec-estimator", prompt="Proponha o fatiamento de projects/<slug>")
```

Ao escrever o plano:
- **Fatia = algo demonstrável de ponta a ponta.** Não "o banco", não "a camada de
  serviço" — isso é camada, e camada não demonstra nada.
- Toda fatia lista os requisitos que cobre. Todo requisito `must` cabe em alguma fatia, ou
  o plano está incompleto.
- Primeira fatia é a que mais **reduz incerteza**, não a mais fácil.
- O destino é um agente de implementação: cada fatia precisa ser executável sem ler o PSP
  inteiro.

## Invariantes (valem em toda skill deste repo)

- Escreva `status: proposed`. **Nunca** `approved` — só o humano promove.
- Faltou informação? Vai para `questions.md`, não para o artefato. Sem suposição.
- Contradição encontrada é reportada, não resolvida.
- Preencha `satisfies` / `verified_by` / `source` na criação.
- Não reescreva artefato `approved`: proponha, e marque dependente como `stale`.
- Ao terminar: `python3 validate.py projects/<slug>` e relate o resultado real.
