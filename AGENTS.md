# AGENTS.md — como conduzir uma especificação neste repo

Este arquivo é a interface do produto. Não há aplicação: você, agente, é quem executa o
processo. Leia `docs/alignment.md` antes de agir — é o escopo que vale.

## O ciclo

```
/spec-brief → /spec-critique → /spec-interview → /spec-requirements → /spec-rules
  → /spec-domain → /spec-architecture → [/spec-data /spec-interfaces /spec-tests]
  → /spec-plan → /spec-review → validate.py → PSP
```

Iterativo. Uma decisão de arquitetura pode reabrir requisito; uma regra descoberta na
modelagem pode mudar caso de uso. Voltar não é retrabalho, é o processo.

As etapas entre colchetes só existem na trilha `full`.

## Skills e subagentes — e por que a divisão economiza crédito

**Skill** carrega instrução no contexto atual, custo marginal quase zero. É o certo para
**gerar**: o briefing já está em contexto, a skill só diz como escrever.

**Subagente** paga contexto frio. Só compensa quando **lê muito e devolve pouco** — e
então compensa duas vezes, porque o varrimento não entope a janela principal.

Portanto: **skill para gerar, subagente para revisar.** Delegar a geração de um requisito
a um subagente é desperdício — paga contexto frio para produzir o que a skill faz de graça.

| Skill | Etapa |
|---|---|
| `spec-brief` | briefing inicial |
| `spec-critique` | crítica do briefing (delega a `spec-critic`) |
| `spec-interview` | fecha as lacunas com o usuário |
| `spec-requirements` | `FR-*` e `NFR-*` |
| `spec-rules` | `BR-*` |
| `spec-domain` | glossário, entidades, `classDiagram` |
| `spec-architecture` | C4 níveis 1-2 e `ADR-*` |
| `spec-data` | `erDiagram`, tabelas, índices |
| `spec-interfaces` | contratos, fluxos, sequência |
| `spec-tests` | estratégia e `TC-*` |
| `spec-plan` | fatiamento (delega a `spec-estimator`) |
| `spec-review` | validador + agentes de revisão |

| Subagente | Lê | Devolve |
|---|---|---|
| `spec-critic` | o briefing | lacuna, ambiguidade, contradição |
| `spec-coherence` | a pasta inteira | incoerência de sentido entre artefatos |
| `spec-traceability` | todas as cadeias | cobertura errada, faltando ou inflada |
| `spec-estimator` | requisitos e arquitetura | proposta de fatias e ordem |

`spec-coherence` e `spec-traceability` são independentes: dispare na mesma mensagem para
rodarem em paralelo.

**Ordem que não se inverte:** `validate.py` antes de qualquer subagente. Os 11 gates são
grátis e locais — não gaste contexto frio com o que um script pega.

## Regras invioláveis

1. **Nada de `approved` por sua conta.** Você escreve `status: proposed`. Só o humano
   promove. Essa é a única garantia do processo — não a contorne nem "por eficiência".
2. **Lacuna gera pergunta, não valor.** Se a informação não está no briefing nem veio do
   usuário, ela vai para `questions.md`. Nunca para o artefato.
3. **Contradição é reportada, não resolvida.** Você não escolhe qual das duas versões vale.
4. **Rastreabilidade na criação.** Preencha `satisfies`, `verified_by` e `source` ao criar
   o artefato. Depois ninguém preenche.
5. **Não reescreva artefato `approved`.** Proponha a mudança, e marque como `stale` todo
   artefato que dependia dele. O validador vai bloquear até o humano revisar.
6. **Nunca gere código de aplicação aqui.** Este repo produz especificação. A
   implementação é outro projeto, e recebe o PSP.

## Dois tipos de arquivo

- **Artefato** — ID estável, frontmatter, rastreável: `FR`, `NFR`, `BR`, `UC`, `ADR`, `TC`,
  `PR`. Mora em pasta por tipo.
- **Documento de etapa** — narrativo, um por etapa, sem ID: briefing, produto, domínio,
  arquitetura, dados, interfaces, estratégia de teste, plano.

A escolha é uma pergunta só: **outro arquivo precisa citar isto por ID?** Ver ADR-008 na
spec do próprio repo.

## Ao criar artefato

- Template em `templates/`, um por tipo. Copie e preencha; não invente estrutura.
- Requisito funcional declara `verification: gate | teste | observacao` (G11). `observacao`
  significa que nenhum gate ou teste alcança — só humano confirma.
- Nome do arquivo = o `id`. `FR-003` vive em `requirements/FR-003.md`. O validador checa.
- Numere sequencialmente dentro do tipo, sem reaproveitar número de artefato removido.
- Prefixos: `FR` requisito, `NFR` atributo de qualidade, `BR` regra, `UC` caso de uso,
  `ADR` decisão, `TC` caso de teste, `PR` processo.

## Ao falar com o usuário

Ele pode não ser técnico. Pergunte sobre o negócio — quem faz o quê, o que não pode
acontecer, o que acontece quando dá errado. Nunca sobre schema, endpoint, padrão de
projeto ou framework. Traduzir negócio em técnica é seu trabalho, não dele.

Uma pergunta por vez. Ofereça um default quando houver um razoável: escolher é mais fácil
que inventar.

## Diagramas

Mermaid é o formato único — renderiza no GitHub, sem ferramenta externa.

| Diagrama | Onde | Obrigatório |
|---|---|---|
| C4 nível 1, contexto | `architecture.md` | sim (G10) |
| C4 nível 2, contêiner | `architecture.md` | recomendado |
| C4 nível 3, componente | — | **fora de propósito**: envelhece em semanas, o código conta melhor |
| `flowchart` de fluxo | `processes/PR-*.md` | sim, em cada `PR-*` (G10) |
| `sequenceDiagram` | dentro do `PR-*` que ele detalha | só fluxo crítico |
| `classDiagram` do domínio | `domain-model.md` | sim (G10) |
| `erDiagram` do banco | `data-model.md` | sim na trilha `full` (G10) |

Sequência só onde há integração externa, ordem que importa, estado intermediário ou falha
parcial. Sequência de CRUD é desperdício. E todo caminho de falha do diagrama precisa de
linha na tabela de falhas — diagrama só com caminho feliz não serve para implementar.

**Diagrama é o documento; texto é a legenda.** Prosa só onde ela carrega o *porquê*, que
nenhum diagrama expressa.

## Antes de dizer que terminou

```bash
python3 validate.py projects/<slug>
```

Mexeu no validador, nos schemas ou nos scripts? Rode os dois autotestes também:

```bash
python3 test_validate.py && python3 test_scripts.py
```

Exit 0 ou não terminou. Não relate "pronto" com o validador vermelho, e não desligue um
gate para ele passar — o gate existe porque aquela falha já custou retrabalho.

## O que este repo deliberadamente não tem

Sem banco, sem servidor, sem interface web, sem orquestração multiagente, sem CI. Arquivo
e git bastam para um usuário. Se você sentir falta de algum deles, leia a §9 de
`docs/alignment.md` antes de propor: a ausência é decisão tomada, não lacuna.
