#!/usr/bin/env python3
"""Valida um projeto do PSP. Exit 0 = pronto para implementacao.

Uso: python3 validate.py projects/<slug> [--quiet]

Gates em methodology/gates.md. Cada falha cita o gate que a origina.
"""
import json
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).parent
ARTIFACT_DIRS = ("requirements", "rules", "use-cases", "decisions", "tests", "processes")
TRACK_STAGES = {
    "light": ["brief", "requirements", "rules", "domain", "architecture", "plan"],
    "full": ["brief", "product", "requirements", "rules", "use-cases", "processes",
             "domain", "architecture", "data", "interfaces", "tests", "plan"],
}
# Etapa -> documento que a materializa. Etapa sem entrada aqui vive em pasta de artefato.
STAGE_DOCS = {
    "brief": "brief.md",
    "product": "product.md",
    "processes": "processes.md",
    "domain": "domain-model.md",
    "architecture": "architecture.md",
    "data": "data-model.md",
    "interfaces": "interfaces.md",
    "tests": "test-strategy.md",
    "plan": "plan.md",
}
# Etapa -> pasta que precisa de ao menos um artefato.
STAGE_ARTIFACTS = {"requirements": "requirements", "use-cases": "use-cases"}
# Diagrama obrigatorio: etapa -> (documento, tipo mermaid, rotulo).
REQUIRED_DIAGRAMS = {
    "architecture": ("architecture.md", "flowchart", "C4 nivel 1 (contexto)"),
    "data": ("data-model.md", "erDiagram", "ER do banco"),
    "domain": ("domain-model.md", "classDiagram", "modelo de dominio"),
}
PLACEHOLDER = re.compile(r"<[a-z][^>\n]{2,}>|CHANGE[- ]ME|\bTBD\b|\bTODO\b")
REF_FIELDS = ("satisfies", "verified_by", "depends_on")
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n(.*)\Z", re.S)


def split_frontmatter(text):
    m = FRONTMATTER.match(text)
    if not m:
        return None, text
    return yaml.safe_load(m.group(1)) or {}, m.group(2)


def acceptance_criteria(body):
    """Itens de lista sob a secao de critérios de aceitação, ignorando placeholder."""
    m = re.search(r"^##\s*Crit[eé]rios de aceita[cç][aã]o\s*$(.*?)(?=^##\s|\Z)",
                  body, re.S | re.M | re.I)
    if not m:
        return []
    items = re.findall(r"^\s*[-*]\s*(?:\[[ xX]\]\s*)?(.+)$", m.group(1), re.M)
    return [i.strip() for i in items if "<" not in i and i.strip()]


def load_questions(path):
    if not path.exists():
        return []
    blocks = re.findall(r"```yaml\n(.*?)```", path.read_text(), re.S)
    if not blocks:
        return []
    data = yaml.safe_load(blocks[-1])
    return data if isinstance(data, list) else []


def validate(project_dir):
    project_dir = Path(project_dir)
    fails = []
    add = lambda gate, msg: fails.append(f"[{gate}] {msg}")

    schema_art = Draft202012Validator(
        json.loads((ROOT / "schemas/artifact.schema.json").read_text()))
    schema_proj = Draft202012Validator(
        json.loads((ROOT / "schemas/project.schema.json").read_text()))

    # project.yaml
    pfile = project_dir / "project.yaml"
    if not pfile.exists():
        return [f"[G8] {pfile} nao existe"]
    project = yaml.safe_load(pfile.read_text()) or {}
    for e in schema_proj.iter_errors(project):
        add("G8", f"project.yaml: {'/'.join(map(str, e.path)) or '(raiz)'}: {e.message}")
    track = project.get("track")
    if track not in TRACK_STAGES:
        return fails + [f"[G8] track invalida: {track!r}"]

    # artefatos
    artifacts = {}   # id -> (relpath, meta, body)
    for d in ARTIFACT_DIRS:
        for f in sorted((project_dir / d).glob("*.md")):
            rel = f.relative_to(project_dir)
            meta, body = split_frontmatter(f.read_text())
            if meta is None:
                add("G8", f"{rel}: sem frontmatter")
                continue
            for e in schema_art.iter_errors(meta):
                field = "/".join(map(str, e.path)) or "(raiz)"
                add("G8", f"{rel}: {field}: {e.message}")
            aid = meta.get("id")
            if aid and aid != f.stem:
                add("G8", f"{rel}: id {aid!r} != nome do arquivo {f.stem!r}")
            if aid in artifacts:
                add("G8", f"{rel}: id {aid} duplicado (ja em {artifacts[aid][0]})")
            elif aid:
                artifacts[aid] = (rel, meta, body)

    for aid, (rel, meta, body) in artifacts.items():
        status = meta.get("status")
        if status == "proposed":
            add("G7", f"{rel}: status proposed — falta revisao humana")
        elif status == "stale":
            add("G6", f"{rel}: status stale — dependencia mudou e nao foi propagada")
        if aid.startswith("FR-") and not acceptance_criteria(body):
            add("G1", f"{rel}: sem critério de aceitação preenchido")
        for field in REF_FIELDS:
            for ref in meta.get(field) or []:
                if ref not in artifacts:
                    add("G3", f"{rel}: {field} aponta para {ref}, que nao existe")

    satisfied = {r for _, m, _ in artifacts.values() for r in (m.get("satisfies") or [])}
    for aid, (rel, _, _) in artifacts.items():
        if aid.startswith("BR-") and aid not in satisfied:
            add("G2", f"{rel}: regra orfa — nenhum requisito a referencia em satisfies")

    stages = project.get("stages") or {}
    for stage in TRACK_STAGES[track]:
        if stages.get(stage) != "approved":
            add("G4", f"etapa obrigatoria '{stage}' esta '{stages.get(stage, 'ausente')}'"
                      f" (trilha {track})")
            continue
        # Etapa aprovada precisa ter o documento, com conteudo proprio.
        doc = STAGE_DOCS.get(stage)
        if doc:
            f = project_dir / doc
            if not f.exists():
                add("G9", f"etapa '{stage}' aprovada mas {doc} nao existe")
            else:
                text = f.read_text()
                if PLACEHOLDER.search(text):
                    add("G9", f"{doc}: etapa '{stage}' aprovada com placeholder do template"
                              f" ainda no texto")
        folder = STAGE_ARTIFACTS.get(stage)
        if folder and not any((project_dir / folder).glob("*.md")):
            add("G9", f"etapa '{stage}' aprovada mas {folder}/ esta vazia")
        diag = REQUIRED_DIAGRAMS.get(stage)
        if diag:
            dfile, kind, label = diag
            f = project_dir / dfile
            if f.exists() and not re.search(rf"```mermaid\s*\n\s*{kind}", f.read_text()):
                add("G10", f"{dfile}: falta diagrama mermaid '{kind}' — {label}")

    for q in load_questions(project_dir / "questions.md"):
        if isinstance(q, dict) and q.get("blocking"):
            add("G5", f"pergunta bloqueante {q.get('id', '?')}: {q.get('question', '')}")

    return fails


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("-")]
    quiet = "--quiet" in argv
    if len(args) != 1:
        print(__doc__)
        return 2
    target = Path(args[0])
    if not target.is_dir():
        print(f"erro: {target} nao e um diretorio")
        return 2
    fails = validate(target)
    if not fails:
        if not quiet:
            print(f"OK — {target} passa todos os gates. A pasta e o PSP.")
        return 0
    print(f"BLOQUEADO — {len(fails)} pendencia(s) em {target}:\n")
    for f in sorted(fails):
        print(" ", f)
    print("\nDetalhe de cada gate: methodology/gates.md")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
