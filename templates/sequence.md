# Diagramas de sequência

> Só para **fluxo crítico**: onde há integração externa, ordem que importa, estado
> intermediário, ou falha parcial possível. Sequência de CRUD é desperdício.

## SQ-001 — <o que esta sequencia mostra>

**Por que este fluxo é crítico:** uma linha. Se não houver resposta, apague o diagrama.

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
