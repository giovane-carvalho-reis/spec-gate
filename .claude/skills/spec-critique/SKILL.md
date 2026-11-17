---
name: spec-critique
description: Analisa criticamente o briefing e registra lacunas, ambiguidades e contradicoes em questions.md. Use depois de preencher o brief e antes de escrever requisitos.
---

# Crítica do briefing

Delegue ao subagente **`spec-critic`** — ele lê o briefing inteiro em contexto próprio e
devolve só a lista de achados, sem entupir o seu.

```
Agent(subagent_type="spec-critic", prompt="Analise projects/<slug>/brief.md")
```

Ao receber os achados: grave cada um em `questions.md` no formato YAML do template, com
`blocking: true` apenas onde implementar sem a resposta significaria adivinhar algo de
efeito estrutural.

Depois conduza a entrevista com `spec-interview`.

## Invariantes (valem em toda skill deste repo)

- Escreva `status: proposed`. **Nunca** `approved` — só o humano promove.
- Faltou informação? Vai para `questions.md`, não para o artefato. Sem suposição.
- Contradição encontrada é reportada, não resolvida.
- Preencha `satisfies` / `verified_by` / `source` na criação.
- Não reescreva artefato `approved`: proponha, e marque dependente como `stale`.
- Ao terminar: `python3 validate.py projects/<slug>` e relate o resultado real.
