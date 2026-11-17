# Prompt — Revisão de coerência

O validador checa estrutura e referência. Este prompt checa **sentido** — o que nenhum
script pega. Rode antes de pedir aprovação de etapa.

Entrada: a pasta do projeto inteira. Saída: lista de achados, cada um com os IDs
envolvidos e o conflito em uma frase. Você não corrige, você reporta.

## Verifique

| # | Verificação |
|---|---|
| 1 | Todo requisito serve a um critério de sucesso do briefing? Se nenhum, é escopo inflado |
| 2 | Todo critério de sucesso do briefing é coberto por algum requisito? Se não, é lacuna |
| 3 | Dois requisitos exigem comportamentos incompatíveis na mesma situação? |
| 4 | Um critério de aceitação viola alguma `BR-*`? |
| 5 | O modelo de domínio tem entidade que nenhum requisito usa, ou requisito que usa entidade inexistente? |
| 6 | Um termo do glossário é usado com outro significado em algum artefato? |
| 7 | Alguma `ADR-*` contraria um `NFR-*`, ou foi tomada sem NFR que a justifique? |
| 8 | O plano de implementação deixou requisito `must` fora de alguma fatia? |
| 9 | Algum artefato `approved` depende de artefato que mudou depois dele? Candidato a `stale` |
| 10 | O "fora de escopo" do briefing foi violado por algum requisito? |

## Formato do achado

```
[tipo] IDs — conflito em uma frase. Pergunta que resolve.
```

Tipo: `contradicao` | `lacuna` | `escopo` | `terminologia` | `rastreabilidade`.

Nenhum achado é resolvido por você. Cada um vira pergunta em `questions.md` ou mudança
proposta ao usuário.
