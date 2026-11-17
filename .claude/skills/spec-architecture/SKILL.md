---
name: spec-architecture
description: Define a arquitetura em C4 nivel 1 e 2 e registra as decisoes como ADR. Use na etapa architecture.
---

# Arquitetura

Escreve `architecture.md` e as `decisions/ADR-*.md`.

Templates: `templates/architecture.md`, `templates/decision.md`.

- **C4 níveis 1 e 2 apenas.** Contexto (quem fala com o sistema) e contêiner (unidade
  executável + tecnologia). Nível 3 está fora de propósito: envelhece em semanas e o
  código conta melhor.
- Diagrama de contexto obrigatório (gate G10).
- A tabela "atributos de qualidade que moldaram a estrutura" é o coração: cada escolha
  estrutural ligada ao `NFR-*` que a forçou. **Se nenhuma linha preenche, a arquitetura
  foi escolhida por hábito** — diga isso ao usuário.
- Preencha "o que foi deixado de fora": cache, fila, réplica, microsserviço. Ausência
  documentada impede que alguém adicione por reflexo.

Toda decisão com alternativa real vira `ADR-*`. ADR precisa da coluna "por que não" de
cada alternativa, e da seção de custos — ADR que só lista ganho é propaganda.

## Invariantes (valem em toda skill deste repo)

- Escreva `status: proposed`. **Nunca** `approved` — só o humano promove.
- Faltou informação? Vai para `questions.md`, não para o artefato. Sem suposição.
- Contradição encontrada é reportada, não resolvida.
- Preencha `satisfies` / `verified_by` / `source` na criação.
- Não reescreva artefato `approved`: proponha, e marque dependente como `stale`.
- Ao terminar: `python3 validate.py projects/<slug>` e relate o resultado real.
