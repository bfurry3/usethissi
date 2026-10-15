#!/usr/bin/env python3
"""Render a UseThisSI brief (written in TEMPLATE.md format) to email-safe HTML.
Usage: python3 render.py brief.md [out.html]"""
import html, re, sys, pathlib

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

def render(md):
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
    tpl = TEMPLATE.read_text()
    return (tpl.replace("{{TITLE}}", html.escape(meta.get("subject", title)))
               .replace("{{PREHEADER}}", html.escape(meta.get("preheader", "")))
               .replace("{{HEADER_LINE}}", html.escape(title))
               .replace("{{SECTIONS}}", "\n".join(blocks)))

if __name__ == "__main__":
    src = pathlib.Path(sys.argv[1])
    dst = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_suffix(".html")
    dst.write_text(render(src.read_text()))
    print(dst)
