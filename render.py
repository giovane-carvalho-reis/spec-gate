#!/usr/bin/env python3
"""Markdown -> HTML minimo, sem dependencia. So o que os templates usam.

Cobre: titulo, paragrafo, lista, tabela, bloco de codigo (mermaid marcado
como tal), citacao, regua, enfase, codigo inline e link. Nao e um parser
CommonMark — e o subconjunto que este repo escreve, e falha de forma visivel
(o texto cru aparece) em vez de silenciosa.
"""
import html
import re

_INLINE = (
    (re.compile(r"`([^`]+)`"), r"<code>\1</code>"),
    (re.compile(r"\*\*([^*]+)\*\*"), r"<strong>\1</strong>"),
    (re.compile(r"(?<![*\w])\*([^*\n]+)\*(?!\w)"), r"<em>\1</em>"),
    (re.compile(r"~~([^~]+)~~"), r"<del>\1</del>"),
    (re.compile(r"\[([^\]]+)\]\(([^)]+)\)"), r'<a href="\2">\1</a>'),
)


def inline(t):
    t = html.escape(t)
    for pat, sub in _INLINE:
        t = pat.sub(sub, t)
    return t


def _row(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def to_html(md):
    out, lines, i = [], md.split("\n"), 0
    while i < len(lines):
        ln = lines[i]

        if ln.startswith("```"):
            lang = ln[3:].strip()
            i += 1
            buf = []
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(lines[i]); i += 1
            i += 1
            body = html.escape("\n".join(buf))
            if lang == "mermaid":
                out.append(f'<pre class="mermaid">{body}</pre>')
            else:
                out.append(f'<pre class="code"><code>{body}</code></pre>')
            continue

        if re.match(r"^\s*\|.*\|\s*$", ln) and i + 1 < len(lines) \
                and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            head = _row(ln); i += 2
            rows = []
            while i < len(lines) and re.match(r"^\s*\|.*\|\s*$", lines[i]):
                rows.append(_row(lines[i])); i += 1
            th = "".join(f"<th>{inline(c)}</th>" for c in head)
            tb = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>"
                         for r in rows)
            out.append(f"<table><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table>")
            continue

        m = re.match(r"^(#{1,6})\s+(.*)$", ln)
        if m:
            lvl = len(m.group(1))
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>")
            i += 1
            continue

        if re.match(r"^\s*[-*]\s+", ln) or re.match(r"^\s*\d+\.\s+", ln):
            ordered = bool(re.match(r"^\s*\d+\.\s+", ln))
            items = []
            while i < len(lines) and (re.match(r"^\s*[-*]\s+", lines[i])
                                      or re.match(r"^\s*\d+\.\s+", lines[i])):
                txt = re.sub(r"^\s*(?:[-*]|\d+\.)\s+", "", lines[i])
                box = ""
                mb = re.match(r"^\[([ xX])\]\s*(.*)$", txt)
                if mb:
                    checked = " checked" if mb.group(1).lower() == "x" else ""
                    box = f'<input type="checkbox" disabled{checked}> '
                    txt = mb.group(2)
                items.append(f"<li>{box}{inline(txt)}</li>")
                i += 1
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>{''.join(items)}</{tag}>")
            continue

        if ln.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].startswith(">"):
                buf.append(lines[i].lstrip(">").strip()); i += 1
            out.append(f"<blockquote>{inline(' '.join(buf))}</blockquote>")
            continue

        if re.match(r"^\s*(---|___|\*\*\*)\s*$", ln):
            out.append("<hr>"); i += 1
            continue

        if not ln.strip():
            i += 1
            continue

        buf = []
        while i < len(lines) and lines[i].strip() \
                and not lines[i].startswith(("#", ">", "```", "|")) \
                and not re.match(r"^\s*(?:[-*]|\d+\.)\s+", lines[i]):
            buf.append(lines[i]); i += 1
        out.append(f"<p>{inline(' '.join(buf))}</p>")

    return "\n".join(out)


def demo():
    h = to_html("# T\n\npara **forte**\n\n| a | b |\n|---|---|\n| 1 | 2 |\n\n"
                "- [ ] todo\n- [x] feito\n\n```mermaid\nflowchart TD\n  A\n```\n")
    assert "<h1>T</h1>" in h
    assert "<strong>forte</strong>" in h
    assert "<th>a</th>" in h and "<td>1</td>" in h
    assert 'class="mermaid"' in h
    assert "checkbox" in h and "checked" in h
    assert "<script" not in h
    print("  ok  render: titulo, tabela, lista, checkbox, mermaid")


if __name__ == "__main__":
    demo()
