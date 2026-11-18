#!/usr/bin/env python3
"""Empacota o PSP de um projeto em zip.

Uso:  python3 package.py <slug> [-o saida.zip] [--rascunho]
      python3 package.py --selftest

O PSP e o pacote que passou os 11 gates (FR-009). Por padrao o empacotamento
e recusado com gate vermelho — `--rascunho` gera assim mesmo, marcado como
tal no nome do arquivo e no manifesto, para inspecao. Rascunho nao e entrega.

Marcar a tag do instantaneo e trabalho do `deliver.sh` (ADR-007): este script
produz o arquivo, aquele registra qual versao foi entregue.
"""
import argparse
import io
import subprocess
import sys
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import yaml

import validate as V

ROOT = Path(__file__).parent
PROJECTS = ROOT / "projects"

COMO_LER = """
# Como ler este pacote
# 1. brief.md — o problema. Comece aqui.
# 2. plan.md — as fatias, na ordem. Cada fatia e executavel sozinha.
# 3. requirements/FR-*.md — criterios de aceitacao sao o contrato.
# 4. rules/BR-*.md — regra de negocio e categorica, nao sugestao.
# 5. domain-model.md — glossario e linguagem proibida: use estes termos.
# 6. decisions/ADR-*.md — o que ja foi decidido. Nao reabrir sem motivo novo.
#
# Frontmatter: satisfies / verified_by / depends_on ligam os artefatos por id.
# Artefato com status != approved nao foi revisado por humano.
""".strip()


def git_commit():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                              capture_output=True, text=True, timeout=5,
                              check=True).stdout.strip()
    except (subprocess.SubprocessError, OSError):
        return "desconhecido"


def inspect(slug):
    """Le o projeto sem depender do painel: so o que o manifesto precisa."""
    d = PROJECTS / slug
    if not (d / "project.yaml").is_file():
        raise FileNotFoundError(f"projects/{slug}/project.yaml nao existe")
    meta = yaml.safe_load((d / "project.yaml").read_text()) or {}
    ids = [f.stem for sub in V.ARTIFACT_DIRS for f in (d / sub).glob("*.md")]
    return {
        "dir": d, "slug": slug, "name": meta.get("name", slug),
        "track": meta.get("track"),
        "stages": [(s, (meta.get("stages") or {}).get(s, "pending"))
                   for s in V.TRACK_STAGES.get(meta.get("track"), [])],
        "counts": Counter(i.split("-")[0] for i in ids),
        "n_artifacts": len(ids),
        "fails": V.validate(d),
    }


def manifest(p, rascunho=False):
    fails = p["fails"]
    status = ("RASCUNHO — %d pendencia(s), NAO e uma entrega valida" % len(fails)
              if fails else "verdes — PSP valido")
    lines = [
        "# MANIFEST — Project Specification Package",
        f"slug: {p['slug']}",
        f"name: {p['name']}",
        f"track: {p['track']}",
        f"commit: {git_commit()}",
        f"generated_at: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        f"gates: {status}",
        f"artifacts_total: {p['n_artifacts']}",
        "artifacts:",
        *[f"  {k}: {n}" for k, n in sorted(p["counts"].items())],
        "stages:",
        *[f"  {s}: {v}" for s, v in p["stages"]],
    ]
    if fails:
        lines += ["pendencias:", *[f"  - {f}" for f in sorted(fails)]]
    return "\n".join(lines) + "\n\n" + COMO_LER + "\n"


def build(p, rascunho=False):
    buf = io.BytesIO()
    base = p["dir"]
    top = f"{p['slug']}-rascunho" if rascunho else p["slug"]
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(base.rglob("*")):
            if f.is_file():
                z.writestr(f"{top}/{f.relative_to(base).as_posix()}", f.read_bytes())
        z.writestr(f"{top}/MANIFEST.txt", manifest(p, rascunho))
    return buf.getvalue()


def selftest():
    slug = next((d.name for d in sorted(PROJECTS.iterdir())
                 if (d / "project.yaml").is_file()), None)
    assert slug, "nenhum projeto"
    p = inspect(slug)

    mf = manifest(p)
    for w in ("slug:", "track:", "commit:", "Como ler este pacote", "brief.md"):
        assert w in mf, f"manifesto sem {w!r}"
    if p["fails"]:
        assert "RASCUNHO" in mf and "pendencias:" in mf
    print(f"  ok  manifesto de {slug}: {len(mf.splitlines())} linhas")

    data = build(p, rascunho=bool(p["fails"]))
    names = zipfile.ZipFile(io.BytesIO(data)).namelist()
    top = f"{slug}-rascunho" if p["fails"] else slug
    assert f"{top}/MANIFEST.txt" in names and f"{top}/brief.md" in names
    assert len(names) > 30, f"zip magro: {len(names)}"
    assert all(n.startswith(top + "/") for n in names), "zip sem pasta raiz unica"
    print(f"  ok  zip: {len(names)} arquivos, {len(data) // 1024} KB, raiz {top}/")

    try:
        inspect("nao-existe")
    except FileNotFoundError:
        print("  ok  projeto inexistente recusado")
    else:
        raise AssertionError("deveria ter recusado")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("slug", nargs="?", help="projeto em projects/")
    ap.add_argument("-o", "--out", help="arquivo de saida (padrao <slug>-psp.zip)")
    ap.add_argument("--rascunho", action="store_true",
                    help="empacota mesmo com gate vermelho, marcado como rascunho")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.slug:
        ap.error("informe o slug do projeto")

    try:
        p = inspect(a.slug)
    except FileNotFoundError as e:
        print(f"erro: {e}")
        return 2

    if p["fails"] and not a.rascunho:
        print(f"BLOQUEADO — {len(p['fails'])} pendencia(s) em projects/{a.slug}.\n")
        for f in sorted(p["fails"])[:10]:
            print(" ", f)
        if len(p["fails"]) > 10:
            print(f"  ... e mais {len(p['fails']) - 10}")
        print("\nO PSP e o pacote que passou os 11 gates (FR-009).")
        print("Para inspecionar assim mesmo: --rascunho")
        return 1

    suffix = "-rascunho" if p["fails"] else "-psp"
    out = Path(a.out) if a.out else ROOT / f"{a.slug}{suffix}.zip"
    data = build(p, rascunho=bool(p["fails"]))
    out.write_bytes(data)
    n = len(zipfile.ZipFile(io.BytesIO(data)).namelist())
    print(f"{out}  ({n} arquivos, {len(data) // 1024} KB)")
    if p["fails"]:
        print(f"RASCUNHO: {len(p['fails'])} pendencia(s). Nao e uma entrega valida.")
    else:
        print(f"PSP valido. Marque o instantaneo: ./deliver.sh {a.slug}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
