# spec-gate

Especificação de software antes da implementação. Transforma um briefing cru num conjunto
de artefatos coerentes e rastreáveis — o **Project Specification Package (PSP)** — pronto
para ser entregue a um agente de implementação.

O nome é o diferencial: `validate.py` é um **gate**. Ele não gera nada — ele barra a
entrega enquanto a especificação for incoerente, com exit code e sem custar crédito de IA.

Não há aplicação, servidor nem banco de dados. Os artefatos são arquivos Markdown com
frontmatter, versionados por git. A interface é um agente de IA conduzido por
[`AGENTS.md`](AGENTS.md). A garantia de coerência é [`validate.py`](validate.py).

## Uso

```bash
./new-project.sh minha-ideia "Minha Ideia" light   # cria projects/minha-ideia/
./promote.sh minha-ideia                           # light -> full, se o projeto crescer
```

Depois, no Claude Code, uma skill por etapa:

```
/spec-brief minha-ideia        → /spec-critique → /spec-interview
/spec-requirements → /spec-rules → /spec-domain → /spec-architecture → /spec-plan
/spec-review                   → roda os 10 gates + revisão por subagente
```

```bash
python3 validate.py projects/minha-ideia   # exit != 0 enquanto houver bloqueio
python3 package.py minha-ideia             # empacota o PSP em zip
./deliver.sh minha-ideia                   # marca a tag do instantaneo
```

`package.py` recusa com gate vermelho — o PSP é o pacote que passou os 11 gates.
`--rascunho` empacota assim mesmo, marcado no nome e no manifesto, para inspeção.
O zip traz um `MANIFEST.txt` com trilha, commit, contagem de artefatos, estado das
etapas e a ordem de leitura para quem vai implementar.

Painel de progresso, somente leitura:

```bash
python3 dashboard.py              # http://localhost:8099
```

| Rota | Para quê |
|---|---|
| `/` | progresso, cobertura e pendências |
| `/doc?p=&f=` | um arquivo, com sumário, ligações e vizinhos |
| `/read?p=&g=` | todos os artefatos de um grupo em sequência, para crítica |

Autoteste do repositório:

```bash
python3 test_validate.py    # os 11 gates, 26 casos
python3 test_scripts.py     # criacao e promocao de projeto, 7 casos
python3 dashboard.py --selftest   # painel: rotas, ligacoes, travessia de path
python3 render.py                 # markdown -> html
python3 package.py --selftest     # manifesto e zip
```

Quando o validador passa, `deliver.sh` marca a tag: o **PSP** é esse instantâneo imutável,
não a pasta viva, que continua mudando depois da entrega (ADR-007). A Implementação recebe
`git archive psp/<slug>/v1`.

## Estrutura

| Pasta | Conteúdo |
|---|---|
| `methodology/` | trilhas e gates — o processo |
| `templates/` | um arquivo por tipo de artefato |
| `prompts/` | crítica, entrevista e revisão de coerência |
| `schemas/` | contrato do frontmatter e do `project.yaml` |
| `projects/` | os projetos especificados, um por pasta |
| `.claude/skills/` | 12 skills, uma por etapa — geração |
| `.claude/agents/` | 4 subagentes — revisão em contexto frio |
| `validate.py` | os 11 gates. Exit code, zero chamada de LLM |
| `new-project.sh` · `promote.sh` · `deliver.sh` | criar, promover trilha, marcar o PSP |
| `package.py` | empacota o PSP em zip, com manifesto |
| `dashboard.py` · `render.py` | painel local de leitura, somente leitura (ADR-009) |
| `docs/` | visão longa e o entendimento fechado que define este escopo |

Leia [`docs/alignment.md`](docs/alignment.md) antes de [`docs/vision.md`](docs/vision.md):
a visão é o documento original e mais amplo; o alignment é o escopo que vale.

## Requisitos

Python 3.11+. `pip install -r requirements.txt` (duas dependências: `pyyaml`, `jsonschema`).

> Chamou-se `lazy-mvp-project-generator` até 2026-11-17. O nome antigo prometia gerar
> projeto; a ferramenta especifica e bloqueia. Ver §12 de `docs/alignment.md`.
