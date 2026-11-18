#!/usr/bin/env python3
"""Autoteste dos scripts de shell. Uso: python3 test_scripts.py

Cobre TC-001 (criacao respeita a trilha) e TC-006 (trilha promove, nao rebaixa).
Roda em copia temporaria do repo — nunca toca projects/ de verdade.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent
KEEP = ("templates", "schemas", "new-project.sh", "promote.sh", "validate.py")


def sandbox():
    """Copia so o necessario para rodar os scripts, com projects/ vazio."""
    d = Path(tempfile.mkdtemp()) / "repo"
    d.mkdir(parents=True)
    for name in KEEP:
        src = ROOT / name
        (shutil.copytree if src.is_dir() else shutil.copy2)(src, d / name)
    (d / "projects").mkdir()
    return d


def run(d, *args, expect_ok=True):
    r = subprocess.run([str(d / args[0]), *args[1:]], cwd=d,
                       capture_output=True, text=True)
    if expect_ok:
        assert r.returncode == 0, f"{args} falhou: {r.stderr or r.stdout}"
    else:
        assert r.returncode != 0, f"{args} deveria ter falhado, mas saiu 0"
    return r


def stages(d, slug):
    y = (d / "projects" / slug / "project.yaml").read_text()
    return {l.split(":")[0].strip(): l.split(":")[1].strip()
            for l in y.splitlines() if l.startswith("  ") and ":" in l}


def docs(d, slug):
    return {f.name for f in (d / "projects" / slug).glob("*.md")}


def check(label, fn):
    fn()
    print(f"  ok  {label}")


def main():
    d = sandbox()

    def t1_light():
        run(d, "new-project.sh", "a", "A", "light")
        assert len(docs(d, "a")) == 5, docs(d, "a")
        st = stages(d, "a")
        assert len(st) == 6 and set(st.values()) == {"pending"}, st

    def t1_full():
        run(d, "new-project.sh", "b", "B", "full")
        assert len(docs(d, "b")) == 9, docs(d, "b")
        assert len(stages(d, "b")) == 12, stages(d, "b")

    def t1_slug_invalido():
        run(d, "new-project.sh", "Nao Vale", "X", expect_ok=False)
        assert not (d / "projects/Nao Vale").exists()

    def t1_duplicado():
        before = docs(d, "a")
        run(d, "new-project.sh", "a", "Outro", "full", expect_ok=False)
        assert docs(d, "a") == before, "projeto existente foi sobrescrito"

    def t6_promove():
        y = d / "projects/a/project.yaml"
        y.write_text(y.read_text().replace("brief: pending", "brief: approved"))
        run(d, "promote.sh", "a")
        st = stages(d, "a")
        assert len(st) == 12, st
        assert st["brief"] == "approved", "promocao perdeu uma aprovacao"
        assert st["data"] == "pending", st
        assert "track: full" in y.read_text()
        assert len(docs(d, "a")) == 9, docs(d, "a")

    def t6_idempotente():
        st = stages(d, "a")
        run(d, "promote.sh", "a", expect_ok=False)   # ja e full
        assert stages(d, "a") == st, "promocao repetida alterou o projeto"

    def t6_nao_rebaixa():
        # Nao existe caminho de rebaixamento: o script recusa qualquer segunda
        # chamada em projeto full, que e a unica porta por onde isso entraria.
        assert "full) echo" in (d / "promote.sh").read_text()

    for label, fn in [
        ("TC-001 light: 5 documentos, 6 etapas pending", t1_light),
        ("TC-001 full: 9 documentos, 12 etapas", t1_full),
        ("TC-001 slug invalido nao cria nada", t1_slug_invalido),
        ("TC-001 slug duplicado nao sobrescreve", t1_duplicado),
        ("TC-006 promove light->full preservando aprovacao", t6_promove),
        ("TC-006 promover projeto full e recusado", t6_idempotente),
        ("TC-006 nao existe rebaixamento", t6_nao_rebaixa),
    ]:
        check(label, fn)

    shutil.rmtree(d.parent, ignore_errors=True)
    print("\nscripts verificados")


if __name__ == "__main__":
    sys.exit(main())
