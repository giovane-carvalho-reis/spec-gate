# Contratos de interface

> Formato tabular. OpenAPI completo é entrega de implementação, não de especificação.

## Endpoints

| Método | Rota | Faz | Requisito | Auth |
|---|---|---|---|---|
| POST | `/recurso` | | FR-001 | sim |

### `POST /recurso`

**Entrada**
| Campo | Tipo | Obrigatório | Validação |
|---|---|:-:|---|

**Saída `201`**
```json
{ "id": "uuid" }
```

**Erros**
| Código | Quando | Corpo |
|---|---|---|
| 400 | | |
| 409 | | |

Todo erro que o usuário pode causar precisa estar aqui. Erro não especificado vira
mensagem inventada na implementação.

## Integrações externas

| Sistema | Protocolo | Quem chama quem | Autenticação | Timeout | E se cair? |
|---|---|---|---|---|---|

A última coluna é a que importa. Integração sem comportamento de falha definido é
incidente agendado.

## Eventos
Se houver mensageria: nome, produtor, consumidor, payload, garantia de entrega,
idempotência.
