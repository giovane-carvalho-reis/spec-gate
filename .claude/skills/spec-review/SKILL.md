---
name: spec-review
description: Revisa um projeto antes da aprovacao: roda o validador e depois os subagentes de coerencia e rastreabilidade. Use antes de aprovar etapa ou fechar o PSP.
---

# Revisão antes de aprovar

Rode **antes** de pedir aprovação de etapa ou de fechar o PSP. Dois passos, nesta ordem.

## 1. Estrutura (grátis, local)

```bash
python3 validate.py projects/<slug>
```

Os 11 gates: referência quebrada, regra órfã, critério ausente, `proposed`, `stale`,
documento ou diagrama faltando. Conserte tudo antes do passo 2 — não gaste subagente com
o que um script pega.

## 2. Sentido (subagentes)

O validador checa estrutura; ele não sabe se o documento **faz sentido**. Isso vai para
contexto frio:

```
Agent(subagent_type="spec-coherence",    prompt="Revise a coerencia de projects/<slug>")
Agent(subagent_type="spec-traceability", prompt="Audite a cobertura de projects/<slug>")
```

Pode rodar os dois em paralelo, na mesma mensagem — são independentes.

Cada achado vira pergunta em `questions.md` ou mudança proposta ao usuário. **Nenhum é
corrigido por você sem confirmação.**

## Ao fechar

Relate o resultado real do validador. Exit 0 ou não terminou — e não desligue gate para
ele passar.

## Invariantes (valem em toda skill deste repo)

- Escreva `status: proposed`. **Nunca** `approved` — só o humano promove.
- Faltou informação? Vai para `questions.md`, não para o artefato. Sem suposição.
- Contradição encontrada é reportada, não resolvida.
- Preencha `satisfies` / `verified_by` / `source` na criação.
- Não reescreva artefato `approved`: proponha, e marque dependente como `stale`.
- Ao terminar: `python3 validate.py projects/<slug>` e relate o resultado real.
