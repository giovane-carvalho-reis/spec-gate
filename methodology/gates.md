# Gates

O validador (`validate.py`) bloqueia o PSP enquanto qualquer condição abaixo existir.
Cada uma corresponde a uma falha concreta que já custou retrabalho em projeto real.

| Gate | Condição de bloqueio | Por quê |
|---|---|---|
| `G1` | Requisito sem critério de aceitação | Sem critério, "pronto" é opinião |
| `G2` | Regra de negócio não referenciada por nenhum requisito | Regra órfã não é implementada |
| `G3` | Referência a ID inexistente | Rastreabilidade quebrada é pior que ausente |
| `G4` | Etapa obrigatória da trilha não `approved` | Trilha incompleta |
| `G5` | Pergunta aberta marcada `blocking: true` | Lacuna conhecida vira suposição na implementação |
| `G6` | Artefato com `status: stale` | Mudança a montante não propagada |
| `G7` | Artefato com `status: proposed` | Sugestão de IA não revisada por humano |
| `G8` | Frontmatter inválido, ou `id` diferente do nome do arquivo | Contrato quebrado |
| `G9` | Etapa aprovada sem seu Documento de etapa, com pasta de Artefatos vazia, ou com placeholder do template | Etapa aprovada sem conteúdo |
| `G10` | Diagrama obrigatório ausente ou do tipo errado | Diagrama é o documento; sem ele não há o que ler |
| `G11` | Requisito funcional sem `verification` declarado | `verified_by` vazio seria ambíguo: não testado ainda, ou não testável? |

`G1` e `G11` só se aplicam a requisito funcional (`FR-*`). NFR usa métrica no corpo, não critério
em lista.

## Definition of Ready (por artefato)

- Tem `id`, `title`, `status: approved`. Requisito funcional tem `verification`.
- Está rastreado: requisito aponta a regra que satisfaz; teste aponta o que verifica.
- Não contém `TODO`, `TBD` nem `?` como valor de campo.

## Definition of Done (do PSP)

`python3 validate.py projects/<slug>` sai com código 0.
