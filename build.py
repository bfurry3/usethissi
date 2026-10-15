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
CSS=r""":root{--bg:#0a0b14;--bg2:#121427;--card:#151830;--line:#262a4a;--txt:#e8eaf6;--mut:#a3a8c9;--v:#a78bfa;--c:#22d3ee;--g:linear-gradient(135deg,#8b5cf6,#22d3ee)}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:radial-gradient(1200px 600px at 80% -10%,#2a1b5a55,transparent),radial-gradient(900px 500px at -10% 10%,#0e4a5a44,transparent),var(--bg);color:var(--txt);font:16px/1.6 Inter,system-ui,sans-serif}
a{color:var(--c);text-decoration:none}a:hover{text-decoration:underline}a:focus-visible,button:focus-visible{outline:2px solid var(--c);outline-offset:2px}
h1,h2,h3{font-family:"Space Grotesk",Inter,sans-serif;line-height:1.15;letter-spacing:-.02em}h1{font-size:clamp(2rem,5vw,3.4rem);margin:.2em 0}
.wrap{max-width:1100px;margin:auto;padding:0 1.25rem}
.skip{position:absolute;left:-999px}.skip:focus{left:1rem;top:1rem;background:#000;padding:.5rem;z-index:99}
header{position:sticky;top:0;z-index:50;background:#0a0b14cc;backdrop-filter:blur(12px);border-bottom:1px solid var(--line)}
nav{display:flex;flex-wrap:wrap;gap:.25rem 1.2rem;align-items:center;padding:.8rem 1.25rem;max-width:1100px;margin:auto}nav a{color:var(--mut);font-weight:500;font-size:.95rem}nav a:hover{color:var(--txt);text-decoration:none}
nav .logo{font-family:"Space Grotesk";font-weight:700;font-size:1.25rem;background:var(--g);-webkit-background-clip:text;background-clip:text;color:transparent;margin-right:auto}
.grad{background:var(--g);-webkit-background-clip:text;background-clip:text;color:transparent}
.hero{padding:4.5rem 0 3rem;text-align:center}.hero p.lead{color:var(--mut);font-size:1.2rem;max-width:640px;margin:1rem auto 1.8rem}
.btn{display:inline-block;padding:.8rem 1.4rem;border-radius:12px;font-weight:600;background:var(--g);color:#0a0b14;box-shadow:0 0 24px #8b5cf655;transition:transform .15s,box-shadow .15s}.btn:hover{transform:translateY(-2px);box-shadow:0 0 36px #22d3ee66;text-decoration:none}
.btn.ghost{background:transparent;color:var(--txt);border:1px solid var(--line);box-shadow:none;margin-left:.6rem}
.stats{display:flex;justify-content:center;gap:2rem;margin-top:2rem;color:var(--mut);flex-wrap:wrap}.stats b{display:block;font-size:1.6rem;color:var(--txt);font-family:"Space Grotesk"}
.grid{display:grid;gap:1rem;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));padding:0;list-style:none}
.card{display:block;background:linear-gradient(180deg,var(--card),var(--bg2));border:1px solid var(--line);border-radius:16px;padding:1.2rem;color:var(--txt);transition:transform .15s,border-color .15s,box-shadow .15s}
a.card:hover,.card:hover{transform:translateY(-3px);border-color:var(--v);box-shadow:0 8px 30px #8b5cf633;text-decoration:none}
.card .ico{font-size:1.8rem}.card h3{margin:.4rem 0 .3rem;font-size:1.15rem}.card p{margin:.2rem 0;color:var(--mut);font-size:.92rem}
.pick{color:var(--c);font-weight:600}
.badge{display:inline-block;font-size:.75rem;font-weight:600;padding:.15rem .55rem;border-radius:999px;margin:.15rem .25rem .15rem 0;border:1px solid}
.b-free{color:#6ee7b7;border-color:#065f46;background:#064e3b55}.b-paid{color:#c4b5fd;border-color:#5b21b6;background:#4c1d9555}.b-top{color:#0a0b14;background:var(--g);border:0}.b-aff{color:#fcd34d;border-color:#78350f;background:#78350f44}
.tldr{background:#22d3ee12;border:1px solid #22d3ee44;border-left:4px solid var(--c);border-radius:12px;padding:1rem 1.2rem}
.tablewrap{overflow-x:auto;border:1px solid var(--line);border-radius:12px}table{border-collapse:collapse;width:100%;min-width:620px}td,th{padding:.7rem .8rem;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}th{background:var(--bg2);color:var(--mut);font-size:.85rem;text-transform:uppercase;letter-spacing:.04em}tr:hover td{background:#ffffff06}
dl{display:grid;grid-template-columns:max-content 1fr;gap:.5rem 1.2rem;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:1.2rem}dt{color:var(--mut)}dd{margin:0;word-break:break-word}
.feed{list-style:none;padding:0;border-left:2px solid var(--line);margin-left:.5rem}.feed li{position:relative;padding:0 0 1.4rem 1.4rem}.feed li:before{content:"";position:absolute;left:-7px;top:.45rem;width:12px;height:12px;border-radius:50%;background:var(--g);box-shadow:0 0 12px var(--c)}.feed time{font-family:"Space Grotesk";color:var(--c);font-size:.85rem;font-weight:600}.feed p{margin:.2rem 0}
main{padding-bottom:2rem}section{margin:2.5rem 0}
#newsletter{margin:3rem auto;max-width:1100px;padding:2rem 1.25rem;text-align:center;background:linear-gradient(135deg,#8b5cf622,#22d3ee18);border:1px solid var(--line);border-radius:20px}#newsletter p{color:var(--mut)}#newsletter iframe{max-width:100%;border-radius:12px}
footer{border-top:1px solid var(--line);color:var(--mut);font-size:.88rem;padding:1.5rem 1.25rem;text-align:center}
@media (max-width:640px){nav{gap:.2rem .9rem}nav .logo{width:100%}.hero{padding:2.5rem 0 1.5rem}.btn.ghost{margin:.6rem 0 0}dl{grid-template-columns:1fr}}
@media (prefers-reduced-motion:reduce){*{transition:none!important;scroll-behavior:auto!important}}"""
def page(path,title,desc,body,ld=None):
    canon=SITE+"/"+path.replace("index.html","")
    ldj=f'<script type="application/ld+json">{json.dumps(ld)}</script>' if ld else ""
    pages[path]=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}"><link rel="canonical" href="{canon}">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{canon}"><meta property="og:type" content="website">
<meta name="theme-color" content="#0a0b14"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@500;700&display=swap"><link rel="stylesheet" href="/style.css">{ldj}</head><body>
<a class="skip" href="#main">Skip to content</a><header><nav aria-label="Main"><a class="logo" href="/">⚡ {NAME}</a><a href="/use-cases/">Use cases</a><a href="/tools/">Tools</a><a href="/new/">New this week</a><a href="/submit/">Submit a tool</a><a href="/about/">About</a></nav></header>
<main id="main" class="wrap">{body}</main>
<section id="newsletter"><h2>Get the 5-minute builder brief</h2><p>A 5-minute weekday brief: what launched, what changed, and what to try today.</p><script async src="https://subscribe-forms.beehiiv.com/v3/loader.js" data-beehiiv-form="767b56cc-d716-4bab-a162-0baf03c34b2c"></script><p><small>Form not loading? <a href="https://usethissi.beehiiv.com/subscribe" rel="noopener">Subscribe on beehiiv</a>.</small></p></section>
<footer>Some links are affiliate links. <a href="/about/#affiliates">Disclosure</a>. Data last checked {CHECKED}.</footer><script type="text/javascript" async src="https://subscribe-forms.beehiiv.com/attribution.js"></script></body></html>'''
ICON={"Vibe-code an app or landing page":"🧱","AI coding assistant":"⌨️","Set up or run AI agents":"🤖","Automate workflows":"⚙️","Make game art and sprites":"🎮","Generate music and SFX":"🎵","Edit and generate video":"🎬","Write content":"✍️","Research":"🔎","Voice and TTS":"🎙️"}
def badges(d):
    b=[]
    if d["role"]=="Top pick": b.append('<span class="badge b-top">Top pick</span>')
    f=d["free"].lower()
    if f.startswith("yes"): b.append('<span class="badge b-free">Free tier</span>')
    elif f.startswith("no"): b.append('<span class="badge b-paid">Paid only</span>')
    p=d["price"].split(" [")[0].split(";")[0]
    if p and "unverified" not in p.lower(): b.append(f'<span class="badge b-paid">{E(p[:40])}</span>')
    return "".join(b)
def tcard(d): return f'<li><a class="card" href="/tools/{d["slug"]}/"><h3>{E(d["tool"])}</h3><p>{E(d["reason"])}</p><div>{badges(d)}</div></a></li>'
def top(L): return next(d for d in L if d["role"]=="Top pick")
# use case pages
ucl=[]
for u,L in uses.items():
    s=slug(u); t=top(L); alts=[d for d in L if d is not t]; ucl.append((u,s,t))
    rowsh="".join(f'<tr><td>{E(d["role"])}</td><td><a href="/tools/{d["slug"]}/">{E(d["tool"])}</a></td><td>{E(d["reason"])}</td><td>{E(d["free"])}</td><td>{E(d["price"])}</td></tr>' for d in L)
    body=f'''<article><p class="pick">{ICON.get(u,"✨")} Use case</p><h1>Best AI tools to {E(u[0].lower()+u[1:])}</h1>
<p class="tldr"><strong>Short answer:</strong> Use <a href="/tools/{t["slug"]}/">{E(t["tool"])}</a>. {E(t["reason"])}. Free tier: {E(t["free"])}. Paid from {E(t["price"])}. Alternatives: {", ".join(E(a["tool"]) for a in alts[:2])}.</p>
<h2>Top pick: {E(t["tool"])}</h2><p>{E(t["reason"])}. Official site: {link(t)}</p>
<h2>All options</h2><ul class="grid">{"".join(tcard(d) for d in L)}</ul><h2>Compare</h2><div class="tablewrap"><table><thead><tr><th>Role</th><th>Tool</th><th>Why</th><th>Free tier</th><th>Paid from</th></tr></thead><tbody>{rowsh}</tbody></table></div>
<p><small>Last checked: <time datetime="{CHECKED}">{CHECKED}</time>. Prices change, so confirm on the vendor's site.</small></p></article>'''
    ld={"@context":"https://schema.org","@type":"ItemList","name":f"AI tools to {u}","itemListElement":[{"@type":"ListItem","position":i+1,"url":f"{SITE}/tools/{d['slug']}/","name":d["tool"]} for i,d in enumerate(L)]}
    page(f"use-cases/{s}/index.html",f"Best AI tools to {u} (2026) | {NAME}",f"Top pick: {t['tool']}. {t['reason']}. Compare {len(L)} tools with pricing, checked {CHECKED}.",body,ld)
page("use-cases/index.html",f"AI tools by use case | {NAME}","Pick the right AI tool for the job: one top pick per use case, plus alternatives.",
 "<h1>Use cases</h1><ul class=\"grid\">"+"".join(f'<li><a class="card" href="/use-cases/{s}/"><span class="ico" aria-hidden="true">{ICON.get(u,"✨")}</span><h3>{E(u)}</h3><p>Top pick: <span class="pick">{E(t["tool"])}</span></p></a></li>' for u,s,t in ucl)+"</ul>",
 {"@context":"https://schema.org","@type":"ItemList","itemListElement":[{"@type":"ListItem","position":i+1,"url":f"{SITE}/use-cases/{s}/","name":u} for i,(u,s,t) in enumerate(ucl)]})
# tool pages (merge duplicates)
tm={}
for L in uses.values():
    for d in L: tm.setdefault(d["slug"],[]).append(d)
for s,ds in tm.items():
    d=ds[0]
    ucs="".join(f'<li><a href="/use-cases/{slug(x["use"])}/">{E(x["use"])}</a> ({E(x["role"])})</li>' for x in ds)
    body=f'''<article><h1>{E(d["tool"])}</h1><div>{badges(d)}</div><p class="tldr">{E(d["reason"])}.</p>
<dl><dt>Free tier</dt><dd>{E(d["free"])}</dd><dt>Paid from</dt><dd>{E(d["price"])}</dd><dt>Official site</dt><dd>{link(d)}</dd><dt>Affiliate program</dt><dd>{E(d["aff"])}</dd></dl>
<h2>Listed for</h2><ul>{ucs}</ul><p><small>Last checked: <time datetime="{CHECKED}">{CHECKED}</time></small></p></article>'''
    ld={"@context":"https://schema.org","@type":"SoftwareApplication","name":d["tool"],"url":d["url"],"applicationCategory":"BusinessApplication","operatingSystem":"Web","description":d["reason"]}
    m=re.search(r'\$([\d.]+)',d["price"])
    if m: ld["offers"]={"@type":"Offer","price":m.group(1),"priceCurrency":"USD"}
    page(f"tools/{s}/index.html",f"{d['tool']} pricing, free tier and alternatives | {NAME}",f"{d['tool']}: {d['reason']}. Free tier: {d['free']}. From {d['price']}.",body,ld)
page("tools/index.html",f"All AI tools | {NAME}",f"Directory of {len(tm)} AI tools for builders, vibe coders and game devs.",
 "<h1>All tools</h1><ul class=\"grid\">"+"".join(tcard(ds[0]) for s,ds in sorted(tm.items()))+"</ul>")
page("new/index.html",f"New AI tool releases this week | {NAME}","The AI releases from the last two weeks that matter for builders.",
 "<h1>New <span class=\"grad\">this week</span></h1><p>Releases from the last 7 days that matter if you build things. Every item links to its source.</p><ol class=\"feed\" reversed>"+"".join(f'<li><time datetime="{E(a[:10])}">{E(a)}</time><p>{E(b)}</p><a href="{E(c)}" rel="noopener">Read the source →</a></li>' for a,b,c in reversed(rels))+"</ol>")
page("submit/index.html",f"Submit your AI tool | {NAME}","Submit an AI tool for review in the UseThisSI directory.",
 f'<h1>Submit your tool</h1><p>Every tool gets the same review, whether or not it pays. Featured placement will come later and will always be labeled.</p><p><a href="https://github.com/{REPO}/issues/new?template=submit-tool.yml">Submit your tool on GitHub</a> (needs a free GitHub account). We review submissions every week.</p>')
page("about/index.html",f"About and affiliate disclosure | {NAME}","How UseThisSI picks tools, and how affiliate links work.",
 '<h1>About UseThisSI</h1><p>UseThisSI picks one AI tool per job for builders, vibe coders, agent tinkerers and game devs. Agents re-check pricing regularly, and every page shows when it was last checked.</p><h2 id="affiliates">Affiliate disclosure</h2><p>Some outbound links are affiliate links (marked rel="sponsored"). If you buy through one, we may earn a commission at no extra cost to you. Affiliate status never decides our top picks.</p>')
tops="".join(f'<li><a class="card" href="/use-cases/{s}/"><span class="ico" aria-hidden="true">{ICON.get(u,"✨")}</span><h3>{E(u)}</h3><p>Use <span class="pick">{E(t["tool"])}</span>. {E(t["reason"])}.</p></a></li>' for u,s,t in ucl)
feed="".join(f'<li><time datetime="{E(a[:10])}">{E(a)}</time><p>{E(b)}</p></li>' for a,b,c in list(reversed(rels))[:3])
page("index.html",f"{NAME}: the right AI tool for every job","One top pick per job for builders, vibe coders and game devs. Prices checked weekly, plus new releases.",
 f'<section class="hero"><p class="pick">For builders, vibe coders, agent tinkerers and game devs</p><h1>Stop guessing.<br><span class="grad">Use this AI</span> for that job.</h1><p class="lead">{NAME} picks the best AI tool for each job, with two alternatives and current pricing, plus a 5-minute weekday brief on what just launched.</p><a class="btn" href="#newsletter">Get the weekday brief</a><a class="btn ghost" href="/use-cases/">Browse use cases</a><div class="stats"><div><b>{len(tm)}</b>tools</div><div><b>{len(ucl)}</b>use cases</div><div><b>{CHECKED}</b>last checked</div></div></section><section><h2>Top picks by job</h2><ul class="grid">{tops}</ul></section><section><h2>New this week</h2><ol class="feed">{feed}</ol><a href="/new/">See all releases →</a></section>',
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
INDEXNOW_KEY="fcd27737423484d8886b49b06518a52a"
open(f"dist/{INDEXNOW_KEY}.txt","w").write(INDEXNOW_KEY)
print(f"Built {len(pages)} HTML pages")
