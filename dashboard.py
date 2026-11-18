#!/usr/bin/env python3
"""Painel local, somente leitura, para ler e criticar as especificacoes.

Uso:  python3 dashboard.py [porta]        # padrao 8099
      python3 dashboard.py --selftest     # renderiza sem abrir porta

Rotas:
  /                      progresso, cobertura e pendencias
  /doc?p=&f=             um arquivo, com sumario, ligacoes e vizinhos
  /read?p=&g=            todos os artefatos de um grupo em sequencia (critica)

Le as pastas a cada request — sem build, sem cache, sem estado. Nunca
escreve: o arquivo segue sendo a fonte de verdade (ADR-001) e o processo
segue conduzido pelo agente (ADR-002, emendado pelo ADR-009).
"""
import html
import re
import sys
import urllib.parse as up
from collections import Counter, defaultdict
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import yaml

import render
import validate as V

ROOT = Path(__file__).parent
PROJECTS = ROOT / "projects"
MERMAID = "https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.esm.min.mjs"

GROUPS = [
    ("requisitos", ("FR", "NFR")),
    ("regras", ("BR",)),
    ("decisoes", ("ADR",)),
    ("testes", ("TC",)),
    ("casos e fluxos", ("UC", "PR")),
]
GATE_WHY = {
    "G1": "requisito sem critério de aceitação", "G2": "regra de negócio órfã",
    "G3": "referência a ID inexistente", "G4": "etapa obrigatória não aprovada",
    "G5": "pergunta bloqueante em aberto", "G6": "artefato obsoleto (stale)",
    "G7": "artefato não revisado (proposed)", "G8": "frontmatter inválido ou id errado",
    "G9": "etapa aprovada sem conteúdo", "G10": "diagrama obrigatório ausente",
    "G11": "requisito sem `verification`",
}

CSS = """
:root{--bg:#fbfbfa;--fg:#1a1a18;--mut:#6f6f69;--line:#e4e4e0;--card:#fff;--soft:#f4f4f1;
--ok:#2f7d32;--warn:#b26a00;--off:#9a9a94;--bad:#b3261e;--link:#1a5fb4;--sel:#eceae4}
@media(prefers-color-scheme:dark){:root{--bg:#141413;--fg:#ededeb;--mut:#9b9b95;
--line:#2d2d2b;--card:#1c1c1a;--soft:#222220;--ok:#6cc070;--warn:#e0a44a;--off:#6b6b66;
--bad:#e2756b;--link:#7eb3f0;--sel:#2a2a27}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
font:15px/1.65 ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
a{color:var(--link);text-decoration:none}a:hover{text-decoration:underline}
.wrap{display:grid;grid-template-columns:252px minmax(0,1fr);gap:0;min-height:100vh}
nav{border-right:1px solid var(--line);padding:22px 18px 60px;position:sticky;top:0;
height:100vh;overflow-y:auto;background:var(--card)}
nav .brand{font-size:15px;font-weight:650;margin-bottom:2px;display:block;color:var(--fg)}
nav .tag{font-size:11.5px;color:var(--mut)}
nav .mini{display:flex;height:5px;border-radius:3px;overflow:hidden;background:var(--line);
margin:12px 0 6px}
nav .mini i{display:block}.mini .a{background:var(--ok)}.mini .r{background:var(--warn)}
nav .pct{font-size:11.5px;color:var(--mut);margin:0 0 18px}
nav h4{font-size:10.5px;text-transform:uppercase;letter-spacing:.07em;color:var(--mut);
margin:20px 0 7px;font-weight:600}
nav ul{list-style:none;padding:0;margin:0}
nav li a{display:flex;gap:7px;align-items:baseline;padding:3.5px 8px;border-radius:5px;
font-size:13px;color:var(--fg);margin:0 -8px}
nav li a:hover{background:var(--soft);text-decoration:none}
nav li a.on{background:var(--sel);font-weight:600}
nav .id{font:11.5px ui-monospace,Menlo,monospace;color:var(--mut);flex:0 0 52px}
nav .nm{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.dot{width:7px;height:7px;border-radius:50%;flex:0 0 7px;align-self:center}
.dot.approved{background:var(--ok)}.dot.review,.dot.proposed{background:var(--warn)}
.dot.pending{background:var(--off)}.dot.stale{background:var(--bad)}
main{padding:30px 34px 80px;max-width:860px}
h1{font-size:22px;margin:0 0 4px}
.sub{color:var(--mut);font-size:13px;margin:0 0 24px}
h2.sec{font-size:13px;margin:34px 0 12px;color:var(--mut);font-weight:600;
text-transform:uppercase;letter-spacing:.05em}
table{width:100%;border-collapse:collapse;font-size:13.5px}
td,th{text-align:left;padding:7px 12px 7px 0;border-bottom:1px solid var(--line);
vertical-align:top}
th{color:var(--mut);font-weight:500;font-size:12.5px}
tr:last-child td{border-bottom:0}
code{font:12.5px ui-monospace,SFMono-Regular,Menlo,monospace;background:var(--soft);
padding:1px 5px;border-radius:3px}
td code,th code,nav code{background:none;padding:0}
.st{font-size:11.5px;padding:2px 8px;border-radius:4px;border:1px solid;white-space:nowrap}
.st.approved{color:var(--ok);border-color:var(--ok)}
.st.review,.st.proposed{color:var(--warn);border-color:var(--warn)}
.st.pending{color:var(--off);border-color:var(--line)}
.st.stale{color:var(--bad);border-color:var(--bad)}
.gate{color:var(--bad);font-weight:600;font-variant-numeric:tabular-nums}
.green{color:var(--ok);font-weight:600}
.empty{color:var(--mut);font-size:13.5px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px}
.kv{background:var(--soft);border-radius:8px;padding:11px 13px}
.kv b{display:block;font-size:20px;font-weight:600}
.kv span{font-size:11.5px;color:var(--mut)}

/* leitura */
article{font-size:16px;line-height:1.72;max-width:72ch}
article h1{font-size:23px;margin:0 0 14px;line-height:1.3}
article h2{font-size:18px;margin:34px 0 10px;padding-top:4px;border-top:1px solid var(--line)}
article h3{font-size:15.5px;margin:24px 0 6px}
article p{margin:0 0 14px}
article ul,article ol{margin:0 0 14px;padding-left:22px}
article li{margin:4px 0}
article table{margin:16px 0;font-size:14px}
article input[type=checkbox]{margin-right:7px}
article blockquote{border-left:3px solid var(--line);margin:16px 0;padding:2px 0 2px 16px;
color:var(--mut)}
article hr{border:0;border-top:1px solid var(--line);margin:30px 0}
pre.code{background:var(--soft);padding:14px 16px;border-radius:7px;overflow-x:auto;
font:12.5px/1.55 ui-monospace,Menlo,monospace}
pre.mermaid{background:var(--soft);padding:18px;border-radius:7px;text-align:center;
overflow-x:auto;margin:18px 0}
.chips{display:flex;flex-wrap:wrap;gap:7px;align-items:center;margin:0 0 6px}
.meta{background:var(--soft);border-radius:8px;padding:13px 16px;margin:0 0 24px;
font-size:13.5px}
.meta div{margin:3px 0}.meta b{color:var(--mut);font-weight:500;margin-right:6px}
.toc{border-left:2px solid var(--line);padding:2px 0 2px 14px;margin:0 0 26px;
font-size:13.5px}
.toc a{display:block;padding:2px 0;color:var(--mut)}
.toc a:hover{color:var(--link)}
.nxt{display:flex;justify-content:space-between;gap:16px;margin-top:40px;
border-top:1px solid var(--line);padding-top:16px;font-size:13.5px}
.sep{margin:52px 0 0;border-top:2px solid var(--line);padding-top:30px}
footer{color:var(--mut);font-size:12.5px;margin-top:40px}
@media(max-width:820px){.wrap{grid-template-columns:1fr}
nav{position:static;height:auto;border-right:0;border-bottom:1px solid var(--line)}
main{padding:24px 18px 60px}}
"""


def esc(x):
    return html.escape(str(x))


def slugify(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-") or "s"


def frontmatter(path):
    txt = path.read_text()
    m = re.match(r"\A---\n(.*?)\n---\n", txt, re.S)
    if not m:
        return {}, txt
    try:
        return yaml.safe_load(m.group(1)) or {}, txt[m.end():]
    except yaml.YAMLError:
        return {}, txt


def load(slug):
    d = PROJECTS / slug
    meta = yaml.safe_load((d / "project.yaml").read_text()) or {}
    track = meta.get("track")
    arts, order = {}, []
    for sub in V.ARTIFACT_DIRS:
        for f in sorted((d / sub).glob("*.md")):
            fm, body = frontmatter(f)
            aid = fm.get("id", f.stem)
            arts[aid] = {"id": aid, "file": f"{sub}/{f.name}", "meta": fm, "body": body}
            order.append(aid)
    back = defaultdict(list)
    for aid, a in arts.items():
        for field in ("satisfies", "verified_by", "depends_on"):
            for t in a["meta"].get(field) or []:
                back[t].append(aid)
    fails = defaultdict(list)
    for line in V.validate(d):
        gate = line.split("]")[0].lstrip("[")
        rest = line.split("] ", 1)[1]
        key = rest.split(":")[0] if "/" in rest.split(":")[0] else "projeto"
        fails[key].append((gate, rest))
    return {"dir": d, "slug": slug, "name": meta.get("name", slug), "track": track,
            "stages": [(s, (meta.get("stages") or {}).get(s, "pending"))
                       for s in V.TRACK_STAGES.get(track, [])],
            "arts": arts, "order": sorted(order), "back": back, "fails": fails,
            "n_fails": sum(len(v) for v in fails.values())}


def docs_of(p):
    out = [(V.STAGE_DOCS[s], s) for s, _ in p["stages"] if s in V.STAGE_DOCS
           and (p["dir"] / V.STAGE_DOCS[s]).exists()]
    if (p["dir"] / "questions.md").exists():
        out.append(("questions.md", "perguntas"))
    return out


def sidebar(p, here=""):
    done = sum(1 for _, v in p["stages"] if v == "approved")
    rev = sum(1 for _, v in p["stages"] if v == "review")
    tot = len(p["stages"]) or 1
    s = [f'<a class="brand" href="/">{esc(p["name"])}</a>'
         f'<span class="tag">trilha {esc(p["track"])} · {p["n_fails"]} pendência(s)</span>'
         f'<div class="mini"><i class="a" style="width:{done / tot:.1%}"></i>'
         f'<i class="r" style="width:{rev / tot:.1%}"></i></div>'
         f'<p class="pct">{done}/{tot} etapas aprovadas</p>']

    s.append("<h4>Etapas</h4><ul>")
    for st, state in p["stages"]:
        doc = V.STAGE_DOCS.get(st)
        href = (f'/doc?p={p["slug"]}&f={up.quote(doc)}' if doc
                and (p["dir"] / doc).exists() else "/")
        on = " on" if doc and here == doc else ""
        s.append(f'<li><a class="x{on}" href="{href}">'
                 f'<span class="dot {esc(state)}"></span>'
                 f'<span class="nm">{esc(st)}</span></a></li>')
    s.append("</ul>")

    for label, prefixes in GROUPS:
        ids = [a for a in p["order"] if a.split("-")[0] in prefixes]
        if not ids:
            continue
        g = slugify(label)
        s.append(f'<h4><a href="/read?p={p["slug"]}&g={g}">{esc(label)} ↗</a></h4><ul>')
        for aid in ids:
            a = p["arts"][aid]
            on = " on" if here == a["file"] else ""
            s.append(f'<li><a class="x{on}" href="/doc?p={p["slug"]}'
                     f'&f={up.quote(a["file"])}">'
                     f'<span class="dot {esc(a["meta"].get("status", ""))}"></span>'
                     f'<span class="id">{esc(aid)}</span>'
                     f'<span class="nm">{esc(a["meta"].get("title", ""))}</span></a></li>')
        s.append("</ul>")

    extra = [(f, lbl) for f, lbl in docs_of(p) if f == "questions.md"]
    if extra:
        s.append("<h4>Outros</h4><ul>")
        for f, lbl in extra:
            on = " on" if here == f else ""
            s.append(f'<li><a class="x{on}" href="/doc?p={p["slug"]}&f={up.quote(f)}">'
                     f'<span class="nm">{esc(f)}</span></a></li>')
        s.append("</ul>")
    return "<nav>" + "".join(s) + "</nav>"


def shell(title, p, body, here="", mermaid=False):
    script = (f'<script type="module">import m from "{MERMAID}";'
              'm.initialize({startOnLoad:true,securityLevel:"strict",'
              'theme:matchMedia("(prefers-color-scheme:dark)").matches?"dark":"default"});'
              "</script>") if mermaid else ""
    return (f'<!doctype html><html lang="pt-BR"><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f"<title>{esc(title)}</title><style>{CSS}</style>"
            f'<div class="wrap">{sidebar(p, here)}<main>{body}</main></div>{script}</html>')


def links_block(p, aid):
    a = p["arts"][aid]
    m = a["meta"]
    rows = []

    def ln(ids):
        out = []
        for i in ids:
            if i in p["arts"]:
                out.append(f'<a href="/doc?p={p["slug"]}'
                           f'&f={up.quote(p["arts"][i]["file"])}"><code>{esc(i)}</code></a>')
            else:
                out.append(f'<code class="gate">{esc(i)}</code>')
        return ", ".join(out)

    for label, key in (("satisfaz", "satisfies"), ("verificado por", "verified_by"),
                       ("depende de", "depends_on")):
        if m.get(key):
            rows.append(f"<div><b>{label}</b>{ln(m[key])}</div>")
    if p["back"].get(aid):
        rows.append(f'<div><b>citado por</b>{ln(sorted(p["back"][aid]))}</div>')
    if m.get("source"):
        rows.append(f'<div><b>origem</b><code>{esc(m["source"])}</code></div>')
    bad = p["fails"].get(a["file"])
    if bad:
        txt = "; ".join(f'{g} — {GATE_WHY.get(g, "")}' for g, _ in bad)
        rows.append(f'<div><b>bloqueios</b><span class="gate">{esc(txt)}</span></div>')
    return f'<div class="meta">{"".join(rows)}</div>' if rows else ""


def toc(body):
    heads = re.findall(r"^##\s+(.+)$", body, re.M)
    if len(heads) < 3:
        return ""
    items = "".join(f'<a href="#{slugify(h)}">{esc(h)}</a>' for h in heads)
    return f'<div class="toc">{items}</div>'


def anchored(body_html):
    return re.sub(r"<h2>(.*?)</h2>",
                  lambda m: f'<h2 id="{slugify(re.sub("<[^>]+>", "", m.group(1)))}">'
                            f"{m.group(1)}</h2>", body_html)


def chips(meta):
    out = []
    if meta.get("status"):
        out.append(f'<span class="st {esc(meta["status"])}">{esc(meta["status"])}</span>')
    for k in ("verification", "priority", "type"):
        if meta.get(k):
            out.append(f'<span class="st pending">{esc(k)}: {esc(meta[k])}</span>')
    return f'<div class="chips">{"".join(out)}</div>' if out else ""


def neighbours(p, aid):
    pref = aid.split("-")[0]
    sib = [x for x in p["order"] if x.split("-")[0] == pref]
    i = sib.index(aid)
    prev = sib[i - 1] if i > 0 else None
    nxt = sib[i + 1] if i < len(sib) - 1 else None

    def lk(x, arrow):
        if not x:
            return "<span></span>"
        t = p["arts"][x]["meta"].get("title", "")
        return (f'<a href="/doc?p={p["slug"]}&f={up.quote(p["arts"][x]["file"])}">'
                f"{arrow} {esc(x)} · {esc(t)}</a>")
    return f'<div class="nxt">{lk(prev, "←")}{lk(nxt, "→")}</div>'


def document(slug, rel):
    p = load(slug)
    base = p["dir"].resolve()
    f = (base / rel).resolve()
    if not str(f).startswith(str(base) + "/") or not f.is_file() or f.suffix != ".md":
        return None
    meta, body = frontmatter(f)
    aid = meta.get("id")
    head = (chips(meta) + (links_block(p, aid) if aid in p["arts"] else ""))
    nav = neighbours(p, aid) if aid in p["arts"] else ""
    title = meta.get("title") or rel
    return shell(f"{title} · {slug}", p,
                 f"{head}{toc(body)}<article>{anchored(render.to_html(body))}</article>{nav}",
                 here=rel, mermaid=True)


def read_group(slug, g):
    p = load(slug)
    match = next((pre for lbl, pre in GROUPS if slugify(lbl) == g), None)
    if not match:
        return None
    ids = [a for a in p["order"] if a.split("-")[0] in match]
    parts = []
    for n, aid in enumerate(ids):
        a = p["arts"][aid]
        cls = "sep" if n else ""
        parts.append(f'<section class="{cls}">{chips(a["meta"])}'
                     f'{links_block(p, aid)}'
                     f'<article>{anchored(render.to_html(a["body"]))}</article></section>')
    label = next(lbl for lbl, pre in GROUPS if pre == match)
    body = (f"<h1>{esc(label)}</h1>"
            f'<p class="sub">{len(ids)} artefatos em sequência, para leitura corrida '
            f"e crítica. Cada bloco mostra estado e ligações antes do texto.</p>"
            + ("".join(parts) or '<p class="empty">Nenhum.</p>'))
    return shell(f"{label} · {slug}", p, body, mermaid=True)


def coverage(p):
    sat = defaultdict(list)
    for aid, a in p["arts"].items():
        for t in a["meta"].get("satisfies") or []:
            sat[t].append(aid)
    rows = []
    for aid in p["order"]:
        pref = aid.split("-")[0]
        if pref not in ("BR", "FR", "NFR"):
            continue
        by = sat.get(aid, [])
        tests = [x for x in by if x.startswith("TC-")]
        reqs = [x for x in by if x.startswith(("FR-", "NFR-"))]
        if pref == "BR":
            ok, got, need = bool(reqs), reqs, "requisito"
        else:
            ver = p["arts"][aid]["meta"].get("verification")
            ok = bool(tests) or ver == "observacao"
            got = tests or ([ver] if ver else [])
            need = "teste"
        mark = '<span class="green">✓</span>' if ok else '<span class="gate">—</span>'
        rows.append(f'<tr><td><a href="/doc?p={p["slug"]}'
                    f'&f={up.quote(p["arts"][aid]["file"])}"><code>{esc(aid)}</code></a>'
                    f"</td><td>{mark}</td><td><code>{esc(', '.join(got))}</code></td>"
                    f"<td>{need}</td></tr>")
    return ('<h2 class="sec">Cobertura</h2><table><thead><tr><th>artefato</th>'
            "<th>coberto</th><th>por</th><th>precisa de</th></tr></thead>"
            f"<tbody>{''.join(rows)}</tbody></table>")


def pendencies(p):
    if not p["n_fails"]:
        return ('<h2 class="sec">Pendências</h2><p class="green">Os 11 gates passam. '
                f'Pronto para <code>./deliver.sh {esc(p["slug"])}</code>.</p>')
    by_gate = Counter(g for v in p["fails"].values() for g, _ in v)
    summary = "".join(
        f'<div class="kv"><b class="gate">{n}</b>'
        f'<span>{esc(g)} — {esc(GATE_WHY.get(g, ""))}</span></div>'
        for g, n in sorted(by_gate.items(), key=lambda kv: int(kv[0][1:])))
    rows = []
    for key in sorted(p["fails"], key=lambda k: (k == "projeto", k)):
        label = (f'<a href="/doc?p={p["slug"]}&f={up.quote(key)}">'
                 f"<code>{esc(key)}</code></a>" if key != "projeto" else "<i>projeto</i>")
        gates = " ".join(f'<span class="gate">{esc(g)}</span>'
                         for g, _ in p["fails"][key])
        why = "; ".join(t.split(": ", 1)[-1] for _, t in p["fails"][key])
        rows.append(f"<tr><td>{label}</td><td>{gates}</td><td>{esc(why)}</td></tr>")
    return (f'<h2 class="sec">Pendências ({p["n_fails"]})</h2>'
            f'<div class="grid">{summary}</div><div style="height:18px"></div>'
            f"<table><thead><tr><th>arquivo</th><th>gate</th><th>o quê</th></tr></thead>"
            f"<tbody>{''.join(rows)}</tbody></table>")


def overview(slug):
    p = load(slug)
    counts = Counter(a["meta"].get("status", "?") for a in p["arts"].values())
    tiles = "".join(f'<div class="kv"><b>{n}</b><span>{esc(k)}</span></div>'
                    for k, n in [("artefatos", len(p["arts"]))] + sorted(counts.items()))
    def stage_content(s):
        doc = V.STAGE_DOCS.get(s)
        if doc and (p["dir"] / doc).exists():
            return (f'<a href="/doc?p={p["slug"]}&f={up.quote(doc)}">'
                    f"{esc(doc)}</a>")
        folder = V.STAGE_ARTIFACTS.get(s)
        return f"<code>{esc(folder)}/</code>" if folder else ""

    stage_rows = "".join(
        f'<tr><td><span class="dot {esc(v)}"></span> <code>{esc(s)}</code></td>'
        f'<td><span class="st {esc(v)}">{esc(v)}</span></td>'
        f"<td>{stage_content(s)}</td></tr>"
        for s, v in p["stages"])
    reading = " · ".join(f'<a href="/read?p={p["slug"]}&g={slugify(l)}">{esc(l)}</a>'
                         for l, pre in GROUPS if any(
                             a.split("-")[0] in pre for a in p["order"]))
    body = f"""<h1>{esc(p["name"])}</h1>
<p class="sub">Somente leitura. Para mudar algo, edite o arquivo e recarregue.<br>
Leitura corrida: {reading}</p>
<div class="grid">{tiles}</div>
<h2 class="sec">Etapas</h2>
<table><thead><tr><th>etapa</th><th>estado</th><th>conteúdo</th></tr></thead>
<tbody>{stage_rows}</tbody></table>
{coverage(p)}
{pendencies(p)}
<footer>Lê <code>projects/{esc(p["slug"])}/</code> a cada request. Sem estado, sem cache.
</footer>"""
    return shell(p["name"], p, body)


def first_slug():
    if not PROJECTS.is_dir():
        return None
    for d in sorted(PROJECTS.iterdir()):
        if (d / "project.yaml").is_file():
            return d.name
    return None


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        u = up.urlparse(self.path)
        q = up.parse_qs(u.query)
        slug = q.get("p", [None])[0] or first_slug()
        out = None
        if slug:
            if u.path in ("/", "/index.html"):
                out = overview(slug)
            elif u.path == "/doc":
                out = document(slug, q.get("f", [""])[0])
            elif u.path == "/read":
                out = read_group(slug, q.get("g", [""])[0])
        if out is None:
            self.send_error(404)
            return
        data = out.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *a):
        pass


def selftest():
    render.demo()
    slug = first_slug()
    assert slug, "nenhum projeto"
    ov = overview(slug)
    for w in ("<nav>", "Cobertura", "Pendências", "FR-001", "/read?p="):
        assert w in ov, f"overview sem {w!r}"
    print(f"  ok  overview: {len(ov)} bytes, com navegacao lateral")

    d = document(slug, "requirements/FR-001.md")
    for w in ("citado por", "satisfaz", 'class="nxt"', "Critérios de aceitação"):
        assert w in d, f"documento sem {w!r}"
    print("  ok  documento: ligacoes, vizinhos e corpo renderizado")

    a = document(slug, "architecture.md")
    assert 'class="toc"' in a and "mermaid" in a
    print("  ok  documento longo: sumario e diagrama")

    r = read_group(slug, "requisitos")
    assert r.count("<article>") >= 10, "leitura corrida deveria trazer todos"
    print("  ok  leitura corrida: todos os requisitos em sequencia")

    for bad in ("../../etc/passwd", "../README.md", "nao-existe.md"):
        assert document(slug, bad) is None, f"{bad} deveria ser recusado"
    assert read_group(slug, "inventado") is None
    print("  ok  travessia de path e grupo invalido recusados")
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    port = int(next((a for a in argv[1:] if a.isdigit()), 8099))
    srv = HTTPServer(("127.0.0.1", port), Handler)   # local apenas: sem auth
    print(f"spec-gate → http://localhost:{port}   (ctrl+c para parar)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nparado")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
