---
id: PR-001
type: process
title: Nome do fluxo
status: proposed
satisfies: []
verified_by: []
source: brief.md#4-funcionalidades-imaginadas
---

# PR-001 — Nome do fluxo

**Ator:** · **Gatilho:** · **Resultado:**

## Fluxo

<!-- Gate G10: flowchart mermaid obrigatorio neste artefato. -->

```mermaid
flowchart TD
    A[Inicio] --> B{Decisao}
    B -- sim --> C[Acao]
    B -- nao --> D[Alternativa]
    C --> E[Fim]
```

| Passo | Regra aplicada | Requisito |
|---|---|---|
| B | BR-001 | FR-001 |

## Exceções
O que acontece quando falha, quem é avisado, o que acontece com o dado pela metade.

## Sequência

Só se este fluxo for **crítico**: integração externa, ordem que importa, estado
intermediário, ou falha parcial possível. Sequência de CRUD é desperdício — sem resposta
para "por que este fluxo é crítico", apague esta seção.

```mermaid
sequenceDiagram
    autonumber
    actor U as Usuario
    participant S as Sistema
    participant E as Servico externo

    U->>S: acao
    S->>E: chamada
    alt sucesso
        E-->>S: resultado
        S-->>U: confirmacao
    else falha ou timeout
        E--xS: erro
        S-->>U: mensagem + estado preservado
    end
```

| Passo | Pode falhar? | Consequência | Tratamento |
|---|:-:|---|---|
| 2 | sim | | |

Todo caminho de falha do diagrama precisa de linha na tabela. Sequência que só mostra o
caminho feliz não serve para implementar.
