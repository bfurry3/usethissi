#!/usr/bin/env python3
"""Build UseThisSI static site from data.csv into dist/."""
import csv, json, os, re, shutil, html
CFG=json.load(open("config.json")); SITE=CFG["base_url"].rstrip("/"); CHECKED=CFG["checked"]; REPO=CFG["repo"]; NAME="UseThisSI"
E=html.escape
def slug(s): return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
rows=list(csv.reader(open("data.csv")))
tools,rels=[],[];mode=0
for r in rows[1:]:
    if not r: mode=1; continue
    if r[0]=="release_date": continue
    (rels if mode else tools).append(r)
uses={}
for t in tools:
    d=dict(zip(["use","role","tool","reason","free","price","url","aff"],t)); d["slug"]=slug(d["tool"])
    uses.setdefault(d["use"],[]).append(d)
def has_aff(d): return d["aff"].lower().startswith("yes")
def link(d):
    a=f' data-aff="{{{{AFF:{d["slug"]}}}}}" rel="sponsored noopener"' if has_aff(d) else ' rel="noopener"'
    return f'<a href="{E(d["url"])}"{a}>{E(d["url"])}</a>'
pages={}
CSS="body{font-family:system-ui,sans-serif;max-width:860px;margin:auto;padding:1rem;line-height:1.5}nav a{margin-right:1rem}table{border-collapse:collapse;width:100%}td,th{border:1px solid #ddd;padding:.4rem;text-align:left}.tldr{background:#f4f7ff;padding:.8rem;border-left:4px solid #36f}footer{margin-top:3rem;font-size:.85rem;color:#555}"
def page(path,title,desc,body,ld=None):
    canon=SITE+"/"+path.replace("index.html","")
    ldj=f'<script type="application/ld+json">{json.dumps(ld)}</script>' if ld else ""
    pages[path]=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}"><link rel="canonical" href="{canon}">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{canon}"><meta property="og:type" content="website">
<link rel="stylesheet" href="/style.css">{ldj}</head><body>
<header><nav><a href="/">{NAME}</a><a href="/use-cases/">Use cases</a><a href="/tools/">Tools</a><a href="/new/">New this week</a><a href="/submit/">Submit a tool</a><a href="/about/">About</a></nav></header>
<main>{body}</main>
<section id="newsletter"><h2>Get the 5-minute builder brief</h2><p>Free weekly email: what launched, what changed, and what to try.</p><script async src="https://subscribe-forms.beehiiv.com/v3/loader.js" data-beehiiv-form="767b56cc-d716-4bab-a162-0baf03c34b2c"></script><p><small>Form not loading? <a href="https://usethissi.beehiiv.com/subscribe" rel="noopener">Subscribe on beehiiv</a>.</small></p></section>
<footer>Some links are affiliate links. <a href="/about/#affiliates">Disclosure</a>. Data last checked {CHECKED}.</footer><script type="text/javascript" async src="https://subscribe-forms.beehiiv.com/attribution.js"></script></body></html>'''
def top(L): return next(d for d in L if d["role"]=="Top pick")
# use case pages
ucl=[]
for u,L in uses.items():
    s=slug(u); t=top(L); alts=[d for d in L if d is not t]; ucl.append((u,s,t))
    rowsh="".join(f'<tr><td>{E(d["role"])}</td><td><a href="/tools/{d["slug"]}/">{E(d["tool"])}</a></td><td>{E(d["reason"])}</td><td>{E(d["free"])}</td><td>{E(d["price"])}</td></tr>' for d in L)
    body=f'''<article><h1>Best AI tools to {E(u[0].lower()+u[1:])}</h1>
<p class="tldr"><strong>Short answer:</strong> Use <a href="/tools/{t["slug"]}/">{E(t["tool"])}</a>. {E(t["reason"])}. Free tier: {E(t["free"])}. Paid from {E(t["price"])}. Alternatives: {", ".join(E(a["tool"]) for a in alts[:2])}.</p>
<h2>Top pick: {E(t["tool"])}</h2><p>{E(t["reason"])}. Official site: {link(t)}</p>
<h2>Compare</h2><table><thead><tr><th>Role</th><th>Tool</th><th>Why</th><th>Free tier</th><th>Paid from</th></tr></thead><tbody>{rowsh}</tbody></table>
<p><small>Last checked: <time datetime="{CHECKED}">{CHECKED}</time>. Prices change, so confirm on the vendor's site.</small></p></article>'''
    ld={"@context":"https://schema.org","@type":"ItemList","name":f"AI tools to {u}","itemListElement":[{"@type":"ListItem","position":i+1,"url":f"{SITE}/tools/{d['slug']}/","name":d["tool"]} for i,d in enumerate(L)]}
    page(f"use-cases/{s}/index.html",f"Best AI tools to {u} (2026) | {NAME}",f"Top pick: {t['tool']}. {t['reason']}. Compare {len(L)} tools with pricing, checked {CHECKED}.",body,ld)
page("use-cases/index.html",f"AI tools by use case | {NAME}","Pick the right AI tool for the job: one top pick per use case, plus alternatives.",
 "<h1>Use cases</h1><ul>"+"".join(f'<li><a href="/use-cases/{s}/">{E(u)}</a>, top pick: {E(t["tool"])}</li>' for u,s,t in ucl)+"</ul>",
 {"@context":"https://schema.org","@type":"ItemList","itemListElement":[{"@type":"ListItem","position":i+1,"url":f"{SITE}/use-cases/{s}/","name":u} for i,(u,s,t) in enumerate(ucl)]})
# tool pages (merge duplicates)
tm={}
for L in uses.values():
    for d in L: tm.setdefault(d["slug"],[]).append(d)
for s,ds in tm.items():
    d=ds[0]
    ucs="".join(f'<li><a href="/use-cases/{slug(x["use"])}/">{E(x["use"])}</a> ({E(x["role"])})</li>' for x in ds)
    body=f'''<article><h1>{E(d["tool"])}</h1><p class="tldr">{E(d["reason"])}.</p>
<dl><dt>Free tier</dt><dd>{E(d["free"])}</dd><dt>Paid from</dt><dd>{E(d["price"])}</dd><dt>Official site</dt><dd>{link(d)}</dd><dt>Affiliate program</dt><dd>{E(d["aff"])}</dd></dl>
<h2>Listed for</h2><ul>{ucs}</ul><p><small>Last checked: <time datetime="{CHECKED}">{CHECKED}</time></small></p></article>'''
    ld={"@context":"https://schema.org","@type":"SoftwareApplication","name":d["tool"],"url":d["url"],"applicationCategory":"BusinessApplication","operatingSystem":"Web","description":d["reason"]}
    m=re.search(r'\$([\d.]+)',d["price"])
    if m: ld["offers"]={"@type":"Offer","price":m.group(1),"priceCurrency":"USD"}
    page(f"tools/{s}/index.html",f"{d['tool']} pricing, free tier and alternatives | {NAME}",f"{d['tool']}: {d['reason']}. Free tier: {d['free']}. From {d['price']}.",body,ld)
page("tools/index.html",f"All AI tools | {NAME}",f"Directory of {len(tm)} AI tools for builders, vibe coders and game devs.",
 "<h1>All tools</h1><ul>"+"".join(f'<li><a href="/tools/{s}/">{E(ds[0]["tool"])}</a></li>' for s,ds in sorted(tm.items()))+"</ul>")
page("new/index.html",f"New AI tool releases this week | {NAME}","The AI releases from the last two weeks that matter for builders.",
 "<h1>New this week</h1><ul>"+"".join(f'<li><time>{E(a)}</time>: {E(b)} (<a href="{E(c)}" rel="noopener">source</a>)</li>' for a,b,c in rels)+"</ul>")
page("submit/index.html",f"Submit your AI tool | {NAME}","Submit an AI tool for review in the UseThisSI directory.",
 f'<h1>Submit your tool</h1><p>Every tool gets the same review, whether or not it pays. Featured placement will come later and will always be labeled.</p><p><a href="https://github.com/{REPO}/issues/new?template=submit-tool.yml">Submit your tool on GitHub</a> (needs a free GitHub account). We review submissions every week.</p>')
page("about/index.html",f"About and affiliate disclosure | {NAME}","How UseThisSI picks tools, and how affiliate links work.",
 '<h1>About UseThisSI</h1><p>UseThisSI picks one AI tool per job for builders, vibe coders, agent tinkerers and game devs. Agents re-check pricing regularly, and every page shows when it was last checked.</p><h2 id="affiliates">Affiliate disclosure</h2><p>Some outbound links are affiliate links (marked rel="sponsored"). If you buy through one, we may earn a commission at no extra cost to you. Affiliate status never decides our top picks.</p>')
tops="".join(f'<li><a href="/use-cases/{s}/">{E(u)}</a>: <strong>{E(t["tool"])}</strong></li>' for u,s,t in ucl)
page("index.html",f"{NAME}: the right AI tool for every job","One top pick per job for builders, vibe coders and game devs. Prices checked weekly, plus new releases.",
 f'<h1>Use this AI for that job.</h1><p class="tldr">{NAME} picks the best AI tool for each job, with two alternatives and current pricing. {len(tm)} tools, {len(ucl)} use cases, last checked {CHECKED}.</p><h2>Top picks</h2><ul>{tops}</ul><p><a href="/new/">See what launched this week</a></p>',
 {"@context":"https://schema.org","@type":"WebSite","name":NAME,"url":SITE})
page("404.html",f"Not found | {NAME}","Page not found.",'<h1>Not found</h1><p><a href="/">Go home</a></p>')
shutil.rmtree("dist",ignore_errors=True)
for p,c in pages.items():
    os.makedirs(os.path.dirname("dist/"+p) or "dist",exist_ok=True); open("dist/"+p,"w").write(c)
open("dist/style.css","w").write(CSS)
urls=[SITE+"/"+p.replace("index.html","") for p in pages if p!="404.html"]
open("dist/sitemap.xml","w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+"".join(f"<url><loc>{u}</loc><lastmod>{CHECKED}</lastmod></url>\n" for u in urls)+"</urlset>\n")
open("dist/robots.txt","w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
llms=f"# {NAME}\n\n> One top AI tool pick per job for builders, vibe coders, AI agent tinkerers and indie game devs. Pricing last checked {CHECKED}.\n\n## Use cases\n"+"".join(f"- [{u}]({SITE}/use-cases/{s}/): top pick {t['tool']}. {t['reason']}.\n" for u,s,t in ucl)+f"\n## Pages\n- [All tools]({SITE}/tools/)\n- [New this week]({SITE}/new/)\n- [About and affiliate disclosure]({SITE}/about/)\n"
open("dist/llms.txt","w").write(llms)
print(f"Built {len(pages)} HTML pages")
