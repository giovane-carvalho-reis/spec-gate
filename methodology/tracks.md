# Trilhas

A trilha é escolhida na criação do projeto e define quais etapas são obrigatórias.
Pode ser promovida de `light` para `full`. Nunca rebaixada — perderia artefato aprovado.

| Etapa | Chave | `light` | `full` |
|---|---|:-:|:-:|
| Briefing e problema | `brief` | ● | ● |
| Produto e escopo do MVP | `product` | | ● |
| Requisitos funcionais e NFR | `requirements` | ● | ● |
| Regras de negócio | `rules` | ● | ● |
| Casos de uso | `use-cases` | | ● |
| Fluxos e processos (`PR-*`) | `processes` | | ● |
| Modelo de domínio | `domain` | ● | ● |
| Arquitetura e decisões | `architecture` | ● | ● |
| Modelo de dados | `data` | | ● |
| Contratos de interface | `interfaces` | | ● |
| Estratégia de teste | `tests` | | ● |
| Plano de implementação | `plan` | ● | ● |

● = obrigatória para aprovar o PSP.

Uma etapa não obrigatória pode ser preenchida de todo modo. Se preenchida, é validada
igual — artefato que existe tem que ser coerente, independente da trilha.

## Estados de etapa

`pending` → `review` → `approved`

`review` significa "terminei, falta você ler".

Só `approved` passa o gate. Aprovação é humana e explícita: editar `project.yaml`.
