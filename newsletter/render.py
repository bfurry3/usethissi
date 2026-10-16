#!/usr/bin/env python3
"""Render a UseThisSI brief (written in TEMPLATE.md format) to email-safe HTML.
Usage: python3 render.py brief.md [out.html]"""
import html, re, sys, pathlib

MOJIBAKE = ("â€", "Ã©", "Ã¨", "Â ", "Â·", "ï»¿", "\ufffd")
SECTION_ORDER = ["Today in 30 seconds", "The big one", "Quick hits", "Tool of the day", "Price watch", "One tip to try"]
HYPE = ["free to run", "game-changer", "game changer", "revolutionary", "insane", "mind-blowing", "killer", "destroys"]
SKEPTIC = re.compile(r"\*\*(The catch|Watch out|Caveat):\*\*", re.I)


TEMPLATE = pathlib.Path(__file__).with_name("email.html")
DARK, PURPLE, CYAN, TEXT, MUTED = "#0B0B14", "#7C3AED", "#22D3EE", "#1F2937", "#6B7280"
SECTIONS = {  # heading -> (emoji-free label color, card bg)
    "Today in 30 seconds": "#F5F3FF", "The big one": "#FFFFFF", "Quick hits": "#FFFFFF",
    "Tool of the day": "#ECFEFF", "Price watch": "#FFFFFF", "One tip to try": "#F5F3FF",
}

def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: f'<a href="{m[2]}" style="color:{PURPLE};text-decoration:underline;font-weight:600;">{m[1]}</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", rf'<strong style="color:{DARK};">\1</strong>', s)
    s = re.sub(r"(?<!\*)\*(?!\*)(.+?)\*", r"<em>\1</em>", s)
    s = re.sub(r"`(.+?)`", r'<code style="background:#F3F4F6;padding:1px 5px;border-radius:4px;font-family:Menlo,Consolas,monospace;font-size:14px;">\1</code>', s)
    return s

P = f'margin:0 0 12px 0;font-size:16px;line-height:1.6;color:{TEXT};'

def body_html(lines):
    out, items = [], []
    def flush():
        if items:
            out.append('<table role="presentation" width="100%" cellpadding="0" cellspacing="0">' + "".join(
                f'<tr><td width="18" valign="top" style="padding:0 0 12px 0;color:{CYAN};font-size:16px;line-height:1.6;font-weight:700;">&#9656;</td>'
                f'<td valign="top" style="{P}padding:0 0 12px 0;">{inline(i)}</td></tr>' for i in items) + "</table>")
            items.clear()
    for ln in lines:
        ln = ln.rstrip()
        if not ln: flush(); continue
        if ln.startswith(("- ", "* ")) or re.match(r"\d+\. ", ln):
            items.append(re.sub(r"^(- |\* |\d+\. )", "", ln)); continue
        flush()
        if ln.startswith("### "):
            out.append(f'<h3 style="margin:0 0 12px 0;font-size:21px;line-height:1.3;color:{DARK};font-weight:800;">{inline(ln[4:])}</h3>')
        else:
            m = re.fullmatch(r"\[([^\]]+)\]\(([^)]+)\)", ln)
            if m:  # standalone link -> button
                out.append(f'<table role="presentation" cellpadding="0" cellspacing="0" style="margin:4px 0 4px 0;"><tr><td style="background:{PURPLE};border-radius:6px;">'
                           f'<a href="{m[2]}" style="display:inline-block;padding:10px 18px;color:#FFFFFF;font-weight:700;font-size:15px;text-decoration:none;">{html.escape(m[1])} &rarr;</a></td></tr></table>')
            else:
                out.append(f'<p style="{P}">{inline(ln)}</p>')
    flush()
    return "\n".join(out)

def safe_punct(s):
    """Replace em/en dashes and smart quotes with plain ASCII punctuation."""
    s = re.sub(r"\s*\u2014\s*", ", ", s).replace("\u2013", "-")
    return s.replace("\u2018", "'").replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"').replace("\u2026", "...")

def parse(md):
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    meta, sections, cur = {}, {}, None
    for ln in md.splitlines():
        if ln.startswith("## "): cur = ln[3:].strip(); sections[cur] = []
        elif cur is None:
            m = re.match(r"(Subject|Preheader):\s*(.*)", ln)
            if m: meta[m[1].lower()] = m[2].strip()
        else: sections[cur].append(ln)
    return meta, sections

def names(lines):
    """Bold lead-in names and ### headings (tool/company names) in a section."""
    out = set()
    for ln in lines:
        if ln.startswith("### "): out.add(re.split(r"[:(,|]| is | goes | ships | launches ", ln[4:])[0].strip().lower())
        for m in re.finditer(r"\*\*([^*:]+?)(?:\s*\([^)]*\))?:\*\*", ln):
            n = m[1].strip().lower()
            if n not in {"what happened", "why it matters for builders", "how to try it", "use it for", "price", "why we like it", "the catch", "watch out", "caveat", "lead item", "item two", "item three", "tip title"}: out.add(n)
    return out

def check(md, out_html=None):
    """Return (errors, warnings). Errors block rendering."""
    errs, warns = [], []
    meta, secs = parse(md)
    for t, label in ((md, "source"), (out_html or "", "output")):
        for bad in MOJIBAKE:
            if bad in t: errs.append(f"mojibake {bad!r} in {label}")
    if out_html and any(ord(c) > 127 for c in out_html): errs.append("output HTML is not pure ASCII")
    pre = meta.get("preheader", "")
    if not re.fullmatch(r"[A-Z0-9].{24,140}[.!?]", pre or ""): errs.append("preheader must be one full sentence, 25-140 chars, capitalized, ending in . ! or ?")
    subj = (meta.get("subject", "")).lower()
    for h in HYPE:
        if h in subj or h in pre.lower(): errs.append(f"hype phrase {h!r} in subject/preheader")
    big = secs.get("The big one")
    if big is not None and not any(SKEPTIC.search(l) for l in big):
        errs.append("The big one needs a skeptical point: add **The catch:** (license, hardware cost, or hosted vs local)")
    # dedupe: content sections only (Today in 30 seconds is a summary of them)
    items = []  # (section, name)
    for sec in SECTION_ORDER[1:]:
        for n in names(secs.get(sec, [])): items.append((sec, n))
    brand = lambda n: n.split()[0] if n.split() else n
    for i, (sa, a) in enumerate(items):
        for sb, b in items[i + 1:]:
            if brand(a) == brand(b) or a in b or b in a:
                errs.append(f"duplicate tool/company: {a!r} ({sa}) and {b!r} ({sb}); each may appear in one section only")
    for ln in secs.get("Quick hits", []) + secs.get("Tool of the day", []) + secs.get("The big one", []):
        if re.search(r"(price (cut|drop|increase|change|hike)|now \$\d|was \$\d|plan (removed|is gone))", ln, re.I):
            warns.append(f"possible price change outside Price watch: {ln[:70]}")
    return errs, warns

def render(md):
    md = safe_punct(md)
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    meta, title, sections, cur = {}, "", [], None
    for ln in md.splitlines():
        if ln.startswith("# "): title = ln[2:].strip()
        elif ln.startswith("## "):
            cur = [ln[3:].strip(), []]; sections.append(cur)
        elif cur is None:
            m = re.match(r"(Subject|Preheader):\s*(.*)", ln)
            if m: meta[m[1].lower()] = m[2].strip()
        else: cur[1].append(ln)
    blocks = []
    for name, lines in sections:
        bg = SECTIONS.get(name, "#FFFFFF")
        blocks.append(
            f'<tr><td style="padding:0 24px 20px 24px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" '
            f'style="background:{bg};border:1px solid #E5E7EB;border-radius:10px;"><tr><td style="padding:20px 22px 10px 22px;">'
            f'<p style="margin:0 0 12px 0;font-size:12px;letter-spacing:1.5px;text-transform:uppercase;font-weight:800;color:{PURPLE};">'
            f'<span style="color:{CYAN};">&#9632;</span>&nbsp; {html.escape(name)}</p>{body_html(lines)}</td></tr></table></td></tr>')
    tpl = TEMPLATE.read_text(encoding="utf-8")
    return (tpl.replace("{{TITLE}}", html.escape(meta.get("subject", title)))
               .replace("{{PREHEADER}}", html.escape(meta.get("preheader", "")))
               .replace("{{HEADER_LINE}}", html.escape(title))
               .replace("{{SECTIONS}}", "\n".join(blocks))).encode("ascii", "xmlcharrefreplace").decode("ascii")

def selftest():
    good = ("Subject: Muse Spark Open ships open weights, plus GitHub autofix\nPreheader: Meta released open weights for a big coding model today.\n"
            "## The big one\n### Muse Spark Open\n**What happened:** Meta \u2014 released \u201cweights\u201d.\n**The catch:** needs 8 GPUs.\n"
            "## Tool of the day\n### Lindy\n**Use it for:** x\n## Price watch\n- **Tabnine:** contact sales.\n")
    out = render(good); e, _ = check(good, out)
    assert not e, e
    assert "\u00e2\u20ac" not in out and out.isascii() and "<meta charset=\"utf-8\">" in out
    bad = good.replace("ships open weights", "is free to run").replace("Meta released open weights for a big coding model today.", "lowercase no period").replace("**The catch:** needs 8 GPUs.\n", "") + "- **Lindy:** now $49.99.\n" + "x \u00e2\u20ac\u201d y\n"
    e, _ = check(bad, render(bad)); msg = " | ".join(e)
    for k in ("mojibake", "preheader", "hype", "skeptical", "duplicate tool/company: 'lindy'"): assert k in msg, (k, msg)
    print("selftest ok")

if __name__ == "__main__":
    if sys.argv[1:] == ["--test"]: selftest(); sys.exit(0)
    src = pathlib.Path(sys.argv[1])
    dst = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_suffix(".html")
    md = src.read_text(encoding="utf-8")
    out = render(md)
    errs, warns = check(md, out)
    for w in warns: print("WARN:", w, file=sys.stderr)
    if errs:
        for x in errs: print("ERROR:", x, file=sys.stderr)
        if "--force" not in sys.argv: sys.exit(1)
    dst.write_text(out, encoding="utf-8")
    print(dst)
