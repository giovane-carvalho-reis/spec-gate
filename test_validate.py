#!/usr/bin/env python3
"""Autoteste do validador. Uso: python3 test_validate.py"""
import tempfile
from pathlib import Path

from validate import validate

BASE_PROJECT = """\
slug: t
name: Teste
track: light
created: 2026-01-01
stages:
  brief: approved
  requirements: approved
  rules: approved
  domain: approved
  architecture: approved
  plan: approved
"""

FR = """\
---
id: FR-001
type: requirement
title: Fazer a coisa
status: approved
satisfies: [BR-001]
---
## Critérios de aceitação
- [ ] Dado x, quando y, entao z
"""

BR = """\
---
id: BR-001
type: rule
title: A regra
status: approved
---
Enunciado.
"""


DOCS = {
    "brief.md": "# Briefing\n\nO problema e concreto.\n",
    "domain-model.md": "# Dominio\n\n```mermaid\nclassDiagram\n    class Pedido\n```\n",
    "architecture.md": "# Arq\n\n```mermaid\nflowchart TD\n    U --> S\n```\n",
    "plan.md": "# Plano\n\n| 1 | fatia | entrega | FR-001 | - |\n",
}


def build(tmp, fr=FR, br=BR, project=BASE_PROJECT, questions=None, docs=None):
    d = Path(tmp)
    for sub in ("requirements", "rules", "use-cases", "decisions", "tests", "processes"):
        (d / sub).mkdir(parents=True, exist_ok=True)
    for name, text in {**DOCS, **(docs or {})}.items():
        if text is not None:
            (d / name).write_text(text)
    (d / "project.yaml").write_text(project)
    if fr:
        (d / "requirements/FR-001.md").write_text(fr)
    if br:
        (d / "rules/BR-001.md").write_text(br)
    if questions:
        (d / "questions.md").write_text("```yaml\n" + questions + "\n```")
    return d


def gates(fails):
    return {f.split("]")[0].lstrip("[") for f in fails}


def check(label, fails, expected):
    got = gates(fails)
    assert got == expected, f"{label}: esperava {expected}, veio {got} — {fails}"
    print(f"  ok  {label}")


def main():
    with tempfile.TemporaryDirectory() as tmp:
        check("projeto valido passa", validate(build(tmp)), set())

    with tempfile.TemporaryDirectory() as tmp:
        d = build(tmp, fr=FR.replace("- [ ] Dado x, quando y, entao z",
                                     "- [ ] Dado <contexto>, quando <acao>, entao <r>"))
        check("G1 criterio placeholder nao conta", validate(d), {"G1"})

    with tempfile.TemporaryDirectory() as tmp:
        d = build(tmp, fr=FR.replace("satisfies: [BR-001]", "satisfies: []"))
        check("G2 regra orfa", validate(d), {"G2"})

    with tempfile.TemporaryDirectory() as tmp:
        d = build(tmp, fr=FR.replace("[BR-001]", "[BR-999]"))
        check("G3 referencia inexistente + G2", validate(d), {"G3", "G2"})

    with tempfile.TemporaryDirectory() as tmp:
        d = build(tmp, project=BASE_PROJECT.replace("plan: approved", "plan: review"))
        check("G4 etapa nao aprovada", validate(d), {"G4"})

    with tempfile.TemporaryDirectory() as tmp:
        d = build(tmp, questions="- id: Q-001\n  question: e isso?\n  blocking: true")
        check("G5 pergunta bloqueante", validate(d), {"G5"})

    with tempfile.TemporaryDirectory() as tmp:
        d = build(tmp, questions="- id: Q-001\n  question: e isso?\n  blocking: false")
        check("G5 pergunta nao bloqueante passa", validate(d), set())

    with tempfile.TemporaryDirectory() as tmp:
        d = build(tmp, br=BR.replace("status: approved", "status: stale"))
        check("G6 stale", validate(d), {"G6"})

    with tempfile.TemporaryDirectory() as tmp:
        d = build(tmp, br=BR.replace("status: approved", "status: proposed"))
        check("G7 proposed", validate(d), {"G7"})

    with tempfile.TemporaryDirectory() as tmp:
        d = build(tmp, br=BR.replace("id: BR-001", "id: BR-002"))
        check("G8 id != nome do arquivo (+G2/G3)", validate(d), {"G8", "G2", "G3"})

    with tempfile.TemporaryDirectory() as tmp:
        d = build(tmp, br="sem frontmatter nenhum")
        check("G8 sem frontmatter (+G3)", validate(d), {"G8", "G3"})

    with tempfile.TemporaryDirectory() as tmp:
        d = build(tmp, br=BR.replace("type: rule", "type: banana"))
        check("G8 type invalido", validate(d), {"G8"})

    with tempfile.TemporaryDirectory() as tmp:
        d = build(tmp, docs={"plan.md": None})
        check("G9 documento de etapa aprovada ausente", validate(d), {"G9"})

    with tempfile.TemporaryDirectory() as tmp:
        d = build(tmp, docs={"plan.md": "# Plano\n\n<fatia a definir>\n"})
        check("G9 placeholder do template", validate(d), {"G9"})

    with tempfile.TemporaryDirectory() as tmp:
        d = build(tmp, docs={"plan.md": "# Plano\n\nrode `validate.py projects/<slug>`\n"})
        check("G9 placeholder em code span nao conta", validate(d), set())

    with tempfile.TemporaryDirectory() as tmp:
        # tag HTML em rotulo mermaid nao e placeholder (falso positivo real)
        d = build(tmp, docs={"architecture.md":
                             "# Arq\n\n```mermaid\nflowchart TD\n"
                             "    U[Autor<br/><i>aprova</i>] --> S[Sistema]\n```\n"})
        check("G9 tag HTML em mermaid nao e placeholder", validate(d), set())

    with tempfile.TemporaryDirectory() as tmp:
        d = build(tmp, fr=None)
        check("G9 pasta de requisitos vazia (+G2)", validate(d), {"G9", "G2"})

    with tempfile.TemporaryDirectory() as tmp:
        d = build(tmp, docs={"architecture.md": "# Arq\n\nso prosa, sem diagrama.\n"})
        check("G10 diagrama de contexto ausente", validate(d), {"G10"})

    with tempfile.TemporaryDirectory() as tmp:
        d = build(tmp, docs={"domain-model.md": "# Dom\n\n```mermaid\nflowchart TD\n  A\n```\n"})
        check("G10 diagrama do tipo errado", validate(d), {"G10"})

    print("\ntodos os gates verificados")


if __name__ == "__main__":
    main()
