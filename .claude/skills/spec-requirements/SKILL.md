---
name: spec-requirements
description: Escreve requisitos funcionais (FR) com criterios de aceitacao e nao funcionais (NFR) com metrica. Use na etapa requirements.
---

# Requisitos

Escreve `requirements/FR-*.md` e `requirements/NFR-*.md`.

Templates: `templates/requirement.md`, `templates/nfr.md`.

## Funcional (`FR-*`)
- Uma capacidade do ponto de vista de quem usa. Não uma tela, não uma tabela, não um
  endpoint.
- **Critério de aceitação é obrigatório** (gate G1) e precisa ser verificável por
  observação: `Dado <contexto>, quando <ação>, então <resultado>`. Inclua pelo menos um de
  exceção — requisito só com caminho feliz volta como bug.
- `satisfies` aponta as `BR-*` que o requisito atende. Regra sem requisito é bloqueio (G2).
- Preencha "Fora deste requisito": o que alguém assumiria estar incluído e não está.

## Não funcional (`NFR-*`)
- **Sem número não é NFR, é desejo.** Grandeza, valor-alvo, condição de medição e
  instrumento.
- Preencha a consequência de não atender — é ela que justifica o custo.
- NFR sem consequência concreta é candidato a ser cortado. Diga isso ao usuário.

Numere sequencialmente, sem reaproveitar número de artefato removido.

## Invariantes (valem em toda skill deste repo)

- Escreva `status: proposed`. **Nunca** `approved` — só o humano promove.
- Faltou informação? Vai para `questions.md`, não para o artefato. Sem suposição.
- Contradição encontrada é reportada, não resolvida.
- Preencha `satisfies` / `verified_by` / `source` na criação.
- Não reescreva artefato `approved`: proponha, e marque dependente como `stale`.
- Ao terminar: `python3 validate.py projects/<slug>` e relate o resultado real.
