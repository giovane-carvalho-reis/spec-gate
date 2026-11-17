# Estratégia de teste

> Define **o que se testa e onde**. Caso de teste individual é `tests/TC-*.md`.

## Alvo por nível

| Nível | Testa o quê | Não testa |
|---|---|---|
| Unidade | regra de negócio pura, cálculo, validação | infraestrutura |
| Integração | query real, contrato com externo, migração | regra já coberta na unidade |
| Aceitação | critério de aceitação de `FR-*`, ponta a ponta | caminho de exceção raro |

## O que exige teste obrigatório
- Toda `BR-*` tem ao menos um `TC-*`.
- Todo cálculo de dinheiro, prazo ou permissão.
- Todo caminho de falha de integração externa.
- Toda query com filtro semântico — testada contra banco real, não mock.

## O que deliberadamente não se testa
E por quê. Lista explícita evita cobertura por culpa.

## Dados de teste
De onde vêm. Como se produz o caso de borda. O que não pode ser dado real de produção.

## Rastreabilidade
| Requisito / Regra | Casos de teste |
|---|---|
| FR-001 | TC-001, TC-002 |

Linha sem caso de teste é lacuna, não detalhe.
