#!/usr/bin/env python3
"""Painel local, somente leitura, do progresso dos projetos.

Uso:  python3 dashboard.py [porta]        # padrao 8099
      python3 dashboard.py --selftest     # renderiza sem abrir porta

Le as pastas a cada request — nao ha build, nao ha cache, nao ha estado.
Nunca escreve: o arquivo continua sendo a fonte de verdade (ADR-001), e o
processo continua conduzido pelo agente (ADR-002, emendado pelo ADR-009).
"""
import html
import sys
from collections import Counter
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import yaml

import validate as V

ROOT = Path(__file__).parent
PROJECTS = ROOT / "projects"
STATE_ORDER = {"approved": 0, "review": 1, "pending": 2}

CSS = """
:root{--bg:#fbfbfa;--fg:#1a1a18;--mut:#6b6b66;--line:#e3e3df;--card:#fff;
--ok:#2f7d32;--warn:#b26a00;--off:#9a9a94;--bad:#b3261e}
@media(prefers-color-scheme:dark){:root{--bg:#141413;--fg:#eeeeec;--mut:#9a9a94;
--line:#2c2c2a;--card:#1c1c1a;--ok:#6cc070;--warn:#e0a44a;--off:#6b6b66;--bad:#e2756b}}
*{box-sizing:border-box}
body{margin:0;padding:32px 16px;background:var(--bg);color:var(--fg);
font:15px/1.55 ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
main{max-width:860px;margin:0 auto}
h1{font-size:20px;margin:0 0 4px}
.sub{color:var(--mut);font-size:13px;margin-bottom:28px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;
padding:20px;margin-bottom:16px}
.head{display:flex;flex-wrap:wrap;gap:8px;align-items:baseline;justify-content:space-between}
h2{font-size:17px;margin:0}
.track{font-size:12px;color:var(--mut);border:1px solid var(--line);
border-radius:20px;padding:2px 10px}
.bar{display:flex;height:7px;border-radius:4px;overflow:hidden;background:var(--line);
margin:14px 0 6px}
.bar i{display:block}
.bar .a{background:var(--ok)}.bar .r{background:var(--warn)}
.pct{font-size:13px;color:var(--mut);margin-bottom:14px}
ul.stages{list-style:none;padding:0;margin:0 0 16px;display:flex;flex-wrap:wrap;gap:6px}
ul.stages li{font-size:12.5px;padding:3px 9px;border-radius:5px;border:1px solid var(--line)}
li.approved{color:var(--ok);border-color:var(--ok)}
li.review{color:var(--warn);border-color:var(--warn)}
li.pending{color:var(--off)}
table{width:100%;border-collapse:collapse;font-size:13.5px}
td,th{text-align:left;padding:5px 10px 5px 0;border-bottom:1px solid var(--line)}
th{color:var(--mut);font-weight:500}
tr:last-child td{border-bottom:0}
.gate{font-variant-numeric:tabular-nums;color:var(--bad);font-weight:600}
.green{color:var(--ok);font-weight:600}
code{font:12.5px ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--mut)}
footer{color:var(--mut);font-size:12.5px;margin-top:28px;text-align:center}
"""

GATE_WHY = {
    "G1": "requisito sem critério de aceitação",
    "G2": "regra de negócio órfã",
    "G3": "referência a ID inexistente",
    "G4": "etapa obrigatória não aprovada",
    "G5": "pergunta bloqueante em aberto",
    "G6": "artefato obsoleto (stale)",
    "G7": "artefato não revisado (proposed)",
    "G8": "frontmatter inválido ou id errado",
    "G9": "etapa aprovada sem conteúdo",
    "G10": "diagrama obrigatório ausente",
    "G11": "requisito sem `verification`",
}


def esc(x):
    return html.escape(str(x))


def read_projects():
    if not PROJECTS.is_dir():
        return []
    out = []
    for d in sorted(p for p in PROJECTS.iterdir() if (p / "project.yaml").is_file()):
        try:
            meta = yaml.safe_load((d / "project.yaml").read_text()) or {}
        except yaml.YAMLError as e:
            out.append({"slug": d.name, "error": f"project.yaml ilegivel: {e}"})
            continue
        track = meta.get("track")
        required = V.TRACK_STAGES.get(track, [])
        stages = meta.get("stages") or {}
        gates = Counter(f.split("]")[0].lstrip("[") for f in V.validate(d))
        artifacts = Counter()
        for sub in V.ARTIFACT_DIRS:
            for f in (d / sub).glob("*.md"):
                artifacts[f.stem.split("-")[0]] += 1
        out.append({
            "slug": d.name, "name": meta.get("name", d.name), "track": track,
            "stages": [(s, stages.get(s, "pending")) for s in required],
            "gates": gates, "artifacts": artifacts, "error": None,
        })
    return out


def render_project(p):
    if p["error"]:
        return f'<div class="card"><h2>{esc(p["slug"])}</h2>' \
               f'<p class="gate">{esc(p["error"])}</p></div>'

    st = p["stages"]
    done = sum(1 for _, v in st if v == "approved")
    rev = sum(1 for _, v in st if v == "review")
    total = len(st) or 1
    bar = (f'<i class="a" style="width:{done / total:.1%}"></i>'
           f'<i class="r" style="width:{rev / total:.1%}"></i>')

    stages = "".join(
        f'<li class="{esc(v)}">{esc(s)}</li>' for s, v in
        sorted(st, key=lambda kv: (STATE_ORDER.get(kv[1], 9), kv[0])))

    arts = "".join(
        f"<tr><td><code>{esc(k)}-*</code></td><td>{n}</td></tr>"
        for k, n in sorted(p["artifacts"].items())) or \
        '<tr><td colspan="2"><code>nenhum artefato ainda</code></td></tr>'

    if p["gates"]:
        rows = "".join(
            f'<tr><td class="gate">{esc(g)}</td>'
            f'<td>{esc(GATE_WHY.get(g, ""))}</td><td>{n}</td></tr>'
            for g, n in sorted(p["gates"].items(), key=lambda kv: int(kv[0][1:])))
        gates = (f"<table><tr><th>gate</th><th>bloqueio</th><th>n</th></tr>"
                 f"{rows}</table>")
    else:
        gates = '<p class="green">Os 11 gates passam. Pronto para <code>./deliver.sh ' \
                f'{esc(p["slug"])}</code>.</p>'

    return f"""<div class="card">
<div class="head"><h2>{esc(p["name"])}</h2>
<span class="track">trilha {esc(p["track"])}</span></div>
<div class="bar">{bar}</div>
<p class="pct">{done} de {total} etapas aprovadas · {rev} em revisão</p>
<ul class="stages">{stages}</ul>
<table><tr><th>artefatos</th><th></th></tr>{arts}</table>
<div style="height:14px"></div>
{gates}
</div>"""


def render():
    projects = read_projects()
    body = "".join(render_project(p) for p in projects) or \
        '<div class="card"><p>Nenhum projeto ainda. ' \
        '<code>./new-project.sh &lt;slug&gt; "&lt;Nome&gt;" light</code></p></div>'
    return f"""<!doctype html><html lang="pt-BR"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>spec-gate</title><style>{CSS}</style>
<main><h1>spec-gate</h1>
<p class="sub">Progresso das especificações. Somente leitura — para mudar algo, edite o
arquivo. Recarregue para atualizar.</p>
{body}
<footer>Lê <code>projects/</code> a cada request. Nenhum estado, nenhum cache.</footer>
</main></html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ("/", "/index.html"):
            self.send_error(404)
            return
        page = render().encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(page)))
        self.end_headers()
        self.wfile.write(page)

    def log_message(self, *a):
        pass   # silencio: o painel e para olhar, nao para logar


def selftest():
    page = render()
    for expect in ("<!doctype html>", "spec-gate", "trilha"):
        assert expect in page, f"faltou {expect!r} na pagina"
    assert "<script" not in page, "painel deve ser estatico, sem script"
    projects = read_projects()
    assert projects, "nenhum projeto lido — esperado ao menos spec-gate"
    p = next(x for x in projects if x["slug"] == "spec-gate")
    assert p["gates"], "spec-gate deveria ter gates vermelhos neste momento"
    assert any(v == "approved" for _, v in p["stages"]), "domain deveria estar aprovada"
    print(f"  ok  painel renderiza {len(projects)} projeto(s), {len(page)} bytes")
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    port = int(next((a for a in argv[1:] if a.isdigit()), 8099))
    # localhost apenas: o painel expoe a especificacao inteira, sem auth.
    srv = HTTPServer(("127.0.0.1", port), Handler)
    print(f"spec-gate → http://localhost:{port}   (ctrl+c para parar)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nparado")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
