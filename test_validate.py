#!/usr/bin/env python3
"""Autoteste do validador. Uso: python3 test_validate.py"""
import tempfile
import time
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
verification: teste
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
            (d / name).parent.mkdir(parents=True, exist_ok=True)
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
        check("TC-002 projeto valido passa", validate(build(tmp)), set())

    with tempfile.TemporaryDirectory() as tmp:
        d = build(tmp, fr=FR.replace("- [ ] Dado x, quando y, entao z",
                                     "- [ ] Dado <contexto>, quando <acao>, entao <r>"))
        check("TC-002 G1 criterio placeholder nao conta", validate(d), {"G1"})

    with tempfile.TemporaryDirectory() as tmp:
        d = build(tmp, fr=FR.replace("satisfies: [BR-001]", "satisfies: []"))
        check("TC-007 G2 regra orfa", validate(d), {"G2"})

    with tempfile.TemporaryDirectory() as tmp:
        d = build(tmp, fr=FR.replace("[BR-001]", "[BR-999]"))
        check("TC-007 G3 referencia inexistente + G2", validate(d), {"G3", "G2"})

    with tempfile.TemporaryDirectory() as tmp:
        d = build(tmp, project=BASE_PROJECT.replace("plan: approved", "plan: review"))
        check("TC-004 G4 etapa nao aprovada", validate(d), {"G4"})

    with tempfile.TemporaryDirectory() as tmp:
        d = build(tmp, questions="- id: Q-001\n  question: e isso?\n  blocking: true")
        check("TC-002 G5 pergunta bloqueante", validate(d), {"G5"})

    with tempfile.TemporaryDirectory() as tmp:
        d = build(tmp, questions="- id: Q-001\n  question: e isso?\n  blocking: false")
        check("TC-002 G5 pergunta nao bloqueante passa", validate(d), set())

    with tempfile.TemporaryDirectory() as tmp:
        d = build(tmp, br=BR.replace("status: approved", "status: stale"))
        check("TC-005 G6 stale", validate(d), {"G6"})

    with tempfile.TemporaryDirectory() as tmp:
        d = build(tmp, br=BR.replace("status: approved", "status: proposed"))
        check("TC-004 G7 proposed", validate(d), {"G7"})

    with tempfile.TemporaryDirectory() as tmp:
        d = build(tmp, br=BR.replace("id: BR-001", "id: BR-002"))
        check("TC-007 G8 id != nome do arquivo (+G2/G3)", validate(d), {"G8", "G2", "G3"})

    with tempfile.TemporaryDirectory() as tmp:
        d = build(tmp, br="sem frontmatter nenhum")
        check("TC-007 G8 sem frontmatter (+G3)", validate(d), {"G8", "G3"})

    with tempfile.TemporaryDirectory() as tmp:
        d = build(tmp, br=BR.replace("type: rule", "type: banana"))
        check("TC-007 G8 type invalido", validate(d), {"G8"})

    with tempfile.TemporaryDirectory() as tmp:
        d = build(tmp, docs={"plan.md": None})
        check("TC-004 G9 documento de etapa ausente", validate(d), {"G9"})

    with tempfile.TemporaryDirectory() as tmp:
        d = build(tmp, docs={"plan.md": "# Plano\n\n<fatia a definir>\n"})
        check("TC-004 G9 placeholder do template", validate(d), {"G9"})

    with tempfile.TemporaryDirectory() as tmp:
        d = build(tmp, docs={"plan.md": "# Plano\n\nrode `validate.py projects/<slug>`\n"})
        check("TC-004 G9 placeholder em code span nao conta", validate(d), set())

    with tempfile.TemporaryDirectory() as tmp:
        # tag HTML em rotulo mermaid nao e placeholder (falso positivo real)
        d = build(tmp, docs={"architecture.md":
                             "# Arq\n\n```mermaid\nflowchart TD\n"
                             "    U[Autor<br/><i>aprova</i>] --> S[Sistema]\n```\n"})
        check("TC-004 G9 tag HTML em mermaid nao e placeholder", validate(d), set())

    with tempfile.TemporaryDirectory() as tmp:
        d = build(tmp, fr=None)
        check("TC-004 G9 pasta de requisitos vazia (+G2)", validate(d), {"G9", "G2"})

    with tempfile.TemporaryDirectory() as tmp:
        d = build(tmp, docs={"architecture.md": "# Arq\n\nso prosa, sem diagrama.\n"})
        check("TC-002 G10 diagrama de contexto ausente", validate(d), {"G10"})

    with tempfile.TemporaryDirectory() as tmp:
        d = build(tmp, docs={"domain-model.md": "# Dom\n\n```mermaid\nflowchart TD\n  A\n```\n"})
        check("TC-002 G10 diagrama do tipo errado", validate(d), {"G10"})

    with tempfile.TemporaryDirectory() as tmp:
        d = build(tmp, br=None)
        check("TC-004 G9 pasta de regras vazia (+G3)", validate(d), {"G9", "G3"})

    with tempfile.TemporaryDirectory() as tmp:
        d = build(tmp, fr=FR.replace("verification: teste\n", ""))
        check("TC-002 G11 FR sem verification", validate(d), {"G11"})

    with tempfile.TemporaryDirectory() as tmp:
        d = build(tmp, fr=FR.replace("verification: teste", "verification: chute"))
        check("TC-002 G8 verification fora do enum", validate(d), {"G8"})

    with tempfile.TemporaryDirectory() as tmp:
        d = build(tmp, project=BASE_PROJECT.replace("plan: approved", "plan: in_progress"))
        check("TC-004 G8 in_progress nao existe mais", validate(d), {"G8", "G4"})

    with tempfile.TemporaryDirectory() as tmp:
        d = build(tmp, docs={"processes/PR-001.md":
                             "---\nid: PR-001\ntype: process\ntitle: Fluxo\n"
                             "status: approved\n---\nso prosa\n"})
        check("TC-002 G10 PR sem flowchart", validate(d), {"G10"})
    # TC-008 — NFR-002: 100 artefatos em menos de 2s.
    with tempfile.TemporaryDirectory() as tmp:
        d = build(tmp)
        for i in range(2, 51):
            (d / f"requirements/FR-{i:03d}.md").write_text(
                FR.replace("FR-001", f"FR-{i:03d}"))
            (d / f"rules/BR-{i:03d}.md").write_text(
                BR.replace("BR-001", f"BR-{i:03d}"))
            # cada regra referenciada, para isolar o tempo de G2/G3
            f = d / f"requirements/FR-{i:03d}.md"
            f.write_text(f.read_text().replace("satisfies: [BR-001]",
                                               f"satisfies: [BR-{i:03d}]"))
        n = len(list(d.rglob("*.md")))
        t0 = time.perf_counter()
        fails = validate(d)
        dt = time.perf_counter() - t0
        assert not fails, f"projeto sintetico deveria passar: {fails[:3]}"
        assert dt < 2.0, f"{n} artefatos em {dt:.2f}s — NFR-002 exige < 2s"
        print(f"  ok  TC-008 NFR-002: {n} artefatos em {dt:.2f}s (< 2s)")

    print("\ntodos os gates verificados")


if __name__ == "__main__":
    main()
