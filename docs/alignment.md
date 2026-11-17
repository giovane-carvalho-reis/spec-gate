# spec-gate — Entendimento fechado

> Escopo que vale. Refina a visão original (`vision.md`), que descreve uma plataforma web
> deliberadamente descartada — ver §9. Em conflito, este arquivo vence.
>
> Revisão 2 — 2026-11-17. Mudanças desde a revisão 1 em §10.

## 1. O que o produto é

Repositório de metodologia para especificação de software, anterior à implementação.
Recebe um briefing cru, conduz refinamento assistido por agente de IA, produz um conjunto
coerente de artefatos e entrega um **Project Specification Package (PSP)** consumido por um
projeto separado de execução.

O valor não é volume de documento. É **coerência cruzada e rastreável** entre problema,
escopo, requisitos, regras de negócio, domínio, arquitetura, dados, contratos e testes —
verificada por gate automático antes de a implementação começar.

## 2. Decisões fechadas

| # | Decisão | Valor | Origem |
|---:|---|---|---|
| 1 | Forma do produto | Repositório de metodologia + validador. Sem app, sem servidor | revisto — §9 |
| 2 | Consumidor do PSP | Agente de IA (Claude Code / OpenCode) | usuário |
| 3 | Profundidade | Trilhas por porte: `light` (6 etapas) / `full` (12) | usuário |
| 4 | Primeiro caso real | Um projeto novo do usuário | usuário |
| 5 | Persistência | Nenhum banco. Arquivo em disco, versionado por git | nada no MVP exige banco |
| 6 | Interface | O agente de IA sobre os arquivos, conduzido por `AGENTS.md` | uso individual |
| 7 | Acesso a LLM | Nenhum no código. O agente que lê o repo *é* o LLM | sem app, nada a orquestrar |
| 8 | Autenticação | Inexistente. Uso individual, arquivo local | usuário |
| 9 | Formato de diagrama | Mermaid, único. Renderiza no GitHub, sem ferramenta externa | usuário |
| 10 | Entrada | Markdown. O "formulário guiado" é o agente perguntando | escopo mínimo |
| 11 | Repositório | Um só: metodologia, templates, prompts, skills, agentes, projetos | nada a separar |
| 12 | Cobertura de diagrama | C4 níveis 1-2, ER, sequência só de fluxo crítico | usuário — §6 |
| 13 | Divisão de trabalho da IA | Skill gera, subagente revisa | usuário — §7 |
| 14 | Nome | `spec-gate`. Antes: `lazy-mvp-project-generator` | §12 |

## 3. Fonte de verdade dos artefatos

**O arquivo é a fonte de verdade. Não há banco de dados.**

Uma única representação, que é ao mesmo tempo fonte de verdade e entrega. Não existe
sincronização, não existe projeção, não existe exportação — o PSP é a própria pasta do
projeto, commitada.

```text
projects/<slug>/
├── project.yaml           # trilha, estado das etapas, aprovações
├── brief.md
├── questions.md           # lacunas abertas, bloqueantes marcadas
├── requirements/FR-001.md
├── rules/BR-001.md
├── decisions/ADR-001.md
├── tests/TC-001.md
├── domain-model.md
├── architecture.md
└── plan.md
```

Cada artefato é um Markdown com frontmatter validado por `schemas/artifact.schema.json`:

```yaml
---
id: FR-003
type: requirement
status: proposed | approved | stale
satisfies: [BR-001]
verified_by: [TC-007]
source: brief.md#secao-4
---
```

- ID estável = nome do arquivo (gate G8 verifica).
- Relação = campo do frontmatter (gate G3 resolve).
- Histórico e versão = git.
- Rastreabilidade e gate = `validate.py`, com exit code.

## 4. Trilhas

| Trilha | Etapas obrigatórias |
|---|---|
| `light` | brief, requirements, rules, domain, architecture, plan |
| `full` | as 12 da §7 da visão: + product, use-cases, processes, data, interfaces, tests |

Escolhida na criação. Promovível de `light` para `full`; nunca rebaixada — perderia
artefato aprovado.

## 5. Os 10 gates

`validate.py` bloqueia o PSP enquanto existir:

| Gate | Bloqueio |
|---|---|
| G1 | Requisito funcional sem critério de aceitação |
| G2 | Regra de negócio órfã (nenhum requisito a referencia) |
| G3 | Referência a ID inexistente |
| G4 | Etapa obrigatória da trilha não `approved` |
| G5 | Pergunta aberta `blocking: true` |
| G6 | Artefato `stale` |
| G7 | Artefato `proposed` (sugestão de IA não revisada) |
| G8 | Frontmatter inválido, ou `id` ≠ nome do arquivo |
| G9 | Etapa aprovada sem documento, com pasta vazia, ou com placeholder do template |
| G10 | Diagrama obrigatório ausente ou do tipo errado |

Detalhe em `methodology/gates.md`. Autoteste em `test_validate.py`, 17 casos.

## 6. Diagramas

Definido na revisão 2. **Diagrama é o documento; texto é a legenda** — prosa só onde
carrega o *porquê*, que nenhum diagrama expressa.

| Diagrama | Onde | Obrigatório |
|---|---|---|
| C4 nível 1 (contexto) | `architecture.md` | sim (G10) |
| C4 nível 2 (contêiner) | `architecture.md` | recomendado |
| C4 nível 3 (componente) | — | **fora de propósito** |
| `classDiagram` do domínio | `domain-model.md` | sim (G10) |
| `erDiagram` do banco | `data-model.md` | sim na `full` (G10) |
| `flowchart` de processo | `processes.md` | um por fluxo relevante |
| `sequenceDiagram` | `sequence.md` | só fluxo crítico |

Nível 3 fica fora porque diagrama de componente mantido à mão diverge do código em
semanas — e diagrama em que alguém confia e está errado é pior que diagrama ausente.

Sequência só onde há integração externa, ordem que importa, estado intermediário ou falha
parcial possível. Sequência de CRUD é desperdício, e o template exige a tabela de falhas:
diagrama com só o caminho feliz não serve para implementar.

## 7. Skills e subagentes

Definido na revisão 2. A divisão existe para economizar crédito:

- **Skill** carrega instrução no contexto atual. Custo marginal quase zero. Certo para
  **gerar** — o briefing já está em contexto, a skill só diz como escrever.
- **Subagente** paga contexto frio. Só compensa quando **lê muito e devolve pouco**, e
  então compensa duas vezes: o varrimento não entope a janela principal.

**Skill gera, subagente revisa.** 12 skills em `.claude/skills/`, uma por etapa.
4 subagentes em `.claude/agents/`: `spec-critic`, `spec-coherence`, `spec-traceability`,
`spec-estimator`.

Ordem que não se inverte: `validate.py` antes de qualquer subagente. Os 10 gates são
locais e grátis — não se gasta contexto frio com o que um script pega.

## 8. Regras invioláveis para o agente

1. Toda saída de IA entra como `proposed`. Só o humano promove a `approved`.
2. Lacuna gera pergunta em `questions.md`, nunca valor suposto no artefato.
3. Contradição é reportada, nunca resolvida pelo agente.
4. Rastreabilidade preenchida na criação do artefato, não depois.
5. Artefato `approved` não é reescrito: propõe-se a mudança e marca-se o dependente
   como `stale`.
6. Nenhum código de aplicação é gerado neste repo. Isso é o projeto de implementação.

## 9. Por que não é uma plataforma web

A visão original (`vision.md`, §15) descreve uma plataforma com 11 módulos. Duas
restrições confirmadas a derrubaram: nenhum banco de dados (§3) e uso individual (§2,
decisão 8). Sem banco e sem segundo usuário, não resta o que um servidor faria.

| Módulo da visão | Como fica |
|---|---|
| Project Management | pasta por projeto |
| Document / Requirements Management | Markdown com frontmatter |
| Task Management (Kanban) | campo `status` em `project.yaml` |
| Specification Engine | templates + JSON Schema |
| AI Orchestrator | skills e subagentes versionados |
| Diagram Engine | bloco Mermaid dentro do próprio documento |
| Decision Management | `decisions/ADR-*.md` |
| Traceability / Review Engine | `validate.py` + `spec-coherence` + `spec-traceability` |
| Export Engine | git |

Volta à mesa quando houver uma segunda pessoa usando, ou volume que torne busca em arquivo
insuportável. Nenhuma das duas é hoje.

## 10. Mudanças desde a revisão 1

| O que | Antes | Agora |
|---|---|---|
| Diagramas | não definido | decisão 12, §6 |
| Skills e subagentes | não previsto | decisão 13, §7 |
| Gates | 8 | 10 (G9 e G10) |
| Templates | 12 | 18 — a trilha `full` exigia 5 etapas sem template |
| Verbosidade | não tratada | diagrama e tabela primeiro, prosa só para o *porquê* |

## 11. Pontos ainda abertos

1. Qual é o projeto novo da decisão 4 — define o primeiro uso real.
2. `spec-traceability` sobrepõe parte do `validate.py`. Escopado para cobertura semântica;
   se na prática só repetir o script, é o primeiro dos quatro subagentes a cortar.
3. Propagação de `stale` é manual hoje. Automatizar só depois de doer.

## 12. Nome

`spec-gate`, desde 2026-11-17. Antes: `lazy-mvp-project-generator`.

O nome antigo vinha da visão original, de uma plataforma que geraria projetos. Errava
duas vezes: "generator" promete gerar, e a ferramenta não gera nada — ela especifica e
barra; "mvp" descreve o escopo do produto especificado, não o que a ferramenta faz.

`spec-gate` nomeia o diferencial real: coerência verificada por gate antes de implementar.

Descartados:
- `spec-kit` — colide com um projeto conhecido do GitHub.
- `lazy-spec` — mantinha o prefixo da família, mas fica perto de `project-specs`, que
  guarda a verdade sobre projetos que **já existem**. Confusão garantida em seis meses.
- `preflight` — boa metáfora, mas não se explica sozinho numa lista de pastas.
- `spec-first` — nomeia a postura, não a ferramenta, e não sugere o gate.
