# Plano de implementação

> Destino: um agente de implementação. Cada fatia é executável sem ler o PSP inteiro.
>
> Este projeto é parcialmente construído. A coluna **estado** diz o que já existe — o
> plano é honesto sobre isso em vez de replanejar o que está feito.

## Ordem de construção

| # | Fatia | Entrega observável | Requisitos | Depende de | Estado |
|---:|---|---|---|---|---|
| 1 | Contrato do artefato | Schema do frontmatter e do `project.yaml`; template de cada tipo | FR-005 | — | feito |
| 2 | Gates e validador | `validate.py` com os 10 gates e exit code; autoteste em 17 casos | FR-002, FR-006, FR-007, NFR-001, NFR-002 | 1 | feito |
| 3 | Criação de projeto | `new-project.sh` criando a estrutura conforme a trilha | FR-001 | 1 | feito |
| 4 | Instrução do processo | `AGENTS.md` com as regras invioláveis e o ciclo | FR-005, NFR-004 | 2, 3 | feito |
| 5 | Skills por etapa | 12 skills; cada etapa gera seu artefato a partir do template | FR-003, FR-004, FR-005 | 4 | feito |
| 6 | Subagentes de revisão | 4 papéis em contexto isolado, devolvendo achados | FR-003, FR-008, NFR-001 | 5 | feito |
| 7 | **Primeiro projeto real** | Um projeto do autor atravessa as 12 skills e sai com os 10 gates verdes | FR-009, NFR-004 | 5, 6 | **pendente** |
| 8 | Promoção de trilha | `light` → `full` preservando aprovação | FR-010 | 3 | pendente |

## Primeira fatia pendente — a 7

O que construir: nada. O que **fazer**: atravessar o processo com um briefing real, de
ponta a ponta, até o exit code 0.

Por que esta antes da 8: as fatias 1 a 6 não estão provadas, só testadas. O autoteste
verifica que o validador detecta o que ele sabe detectar; não verifica que os templates
perguntam o que importa, que as skills geram artefato útil, nem que o PSP resultante basta
para implementar. Template genérico parece bom até o primeiro uso real — é o caso concreto
que revela qual campo sobra e qual falta.

Promover trilha (fatia 8) antes disso seria construir sobre forma não validada: se o uso
real mudar os templates, a promoção muda junto.

## Incerteza que a fatia 7 resolve

| Pergunta | Sinal de que a resposta é "não" |
|---|---|
| Os templates perguntam o que importa? | O autor preenche tudo e o agente de implementação ainda pergunta algo óbvio |
| O custo é menor que reexplicar contexto a cada sessão? | Especificar leva mais crédito do que a implementação economiza |
| Os gates bloqueiam o que importa? | Gate verde com especificação visivelmente incompleta, ou gate vermelho em algo irrelevante |
| O PSP cabe no contexto do agente? | O agente pede o PSP inteiro para executar uma fatia (viola NFR-004) |

## Pronto para implementar quando

- `python3 validate.py projects/<slug>` sai 0.
- Toda fatia tem requisito associado.
- Nenhum requisito `must` sobrou fora de fatia.

## Fora deste plano

Propagação automática de `stale` (Q-002): fica manual até o esquecimento causar um PSP
aprovado incoerente. Automatizar exige grafo de dependência — custo que o sintoma ainda
não justificou.
