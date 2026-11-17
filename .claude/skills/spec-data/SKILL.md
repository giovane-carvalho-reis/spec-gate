---
name: spec-data
description: Modela o banco de dados com erDiagram mermaid, tabelas, indices justificados e invariantes. Use na etapa data.
---

# Modelo de dados

Escreve `data-model.md`. Template: `templates/data-model.md`.

- Diagrama `erDiagram` mermaid obrigatório (gate G10). Mermaid é o formato único deste
  repo — renderiza no GitHub, sem ferramenta externa.
- Cada tabela liga à entidade de `domain-model.md`. Tabela que não corresponde a nada do
  domínio precisa de justificativa.
- **Todo índice precisa da consulta que o justifica.** Índice sem consulta por trás é
  custo de escrita sem retorno — e é o excesso mais comum nesta etapa.
- Deleção: cascata, restrição ou lógica. Diga qual, e o que acontece com o filho.
- A seção "invariantes garantidas pelo banco" separa o que a estrutura garante do que
  depende de código. Regra que só o código garante é regra que alguém vai furar.

Dado já existente que precise migrar entra nas decisões de modelagem, não fica implícito.

## Invariantes (valem em toda skill deste repo)

- Escreva `status: proposed`. **Nunca** `approved` — só o humano promove.
- Faltou informação? Vai para `questions.md`, não para o artefato. Sem suposição.
- Contradição encontrada é reportada, não resolvida.
- Preencha `satisfies` / `verified_by` / `source` na criação.
- Não reescreva artefato `approved`: proponha, e marque dependente como `stale`.
- Ao terminar: `python3 validate.py projects/<slug>` e relate o resultado real.
