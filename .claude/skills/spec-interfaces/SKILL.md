---
name: spec-interfaces
description: Escreve contratos de API, fluxos de processo e diagramas de sequencia de fluxo critico. Use nas etapas interfaces e processes.
---

# Interfaces e fluxos

Escreve `interfaces.md`, `processes.md` e `sequence.md`.

Templates: `templates/interfaces.md`, `templates/processes.md`, `templates/sequence.md`.

## Interfaces
Formato tabular — OpenAPI completo é entrega de implementação, não de especificação.
**Todo erro que o usuário pode causar precisa estar na tabela de erros.** Erro não
especificado vira mensagem inventada no código.

Em integração externa, a coluna que importa é "e se cair?". Integração sem comportamento
de falha definido é incidente agendado.

## Processos
Um `flowchart` por fluxo, com tabela ligando passo → regra → requisito. Exceções em texto:
o que acontece quando falha, quem é avisado, o que acontece com dado pela metade.

## Sequência
**Só para fluxo crítico:** integração externa, ordem que importa, estado intermediário,
falha parcial possível. Sequência de CRUD é desperdício — se não houver resposta para "por
que este fluxo é crítico", apague o diagrama.

Todo caminho de falha do diagrama precisa de linha na tabela de falhas. Sequência que só
mostra o caminho feliz não serve para implementar.

## Invariantes (valem em toda skill deste repo)

- Escreva `status: proposed`. **Nunca** `approved` — só o humano promove.
- Faltou informação? Vai para `questions.md`, não para o artefato. Sem suposição.
- Contradição encontrada é reportada, não resolvida.
- Preencha `satisfies` / `verified_by` / `source` na criação.
- Não reescreva artefato `approved`: proponha, e marque dependente como `stale`.
- Ao terminar: `python3 validate.py projects/<slug>` e relate o resultado real.
