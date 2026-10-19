#!/usr/bin/env python3
"""Build UseThisSI static site from data.csv into dist/."""
import csv, json, os, re, shutil, html
CFG=json.load(open("config.json")); SITE=CFG["base_url"].rstrip("/"); import datetime as _dt,zoneinfo as _z; CHECKED=_dt.datetime.now(_z.ZoneInfo("America/Phoenix")).strftime("%Y-%m-%d"); REPO=CFG["repo"]; NAME="UseThisSI"
E=html.escape
def slug(s): return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
rows=list(csv.reader(open("data.csv")))
tools,rels=[],[];mode=0
for r in rows[1:]:
    if not r: mode=1; continue
    if r[0]=="release_date": continue
    (rels if mode else tools).append(r)
rels.sort(key=lambda r:r[0])
TODAY=_dt.date.fromisoformat(CHECKED)
plans={}
for p in csv.DictReader(open("data/plans.csv")): plans.setdefault(p["tool"],[]).append(p)
changes=list(csv.DictReader(open("ops/freshness/changes.csv"))) if os.path.exists("ops/freshness/changes.csv") else []
UMAMI=CFG.get("umami_website_id","").strip()
STATIC_LASTMOD=CFG.get("static_lastmod",{})
LASTMOD={}
uses={}
for t in tools:
    d=dict(zip(["use","role","tool","reason","free","price","url","aff","checked"],t)); d.setdefault("checked",""); d["checked"]=d["checked"].strip(); d["slug"]=slug(d["tool"])
    uses.setdefault(d["use"],[]).append(d)
DATA_DATE=max(d["checked"] for L in uses.values() for d in L if d["checked"])
def fresh(d): return bool(d["checked"]) and (TODAY-_dt.date.fromisoformat(d["checked"])).days<=30
def bad_price(p): return (not p) or bool(re.search(r"unverified|contact sales|talk to sales|3rd-party",p,re.I))
def vprice(d): return fresh(d) and not bad_price(d["price"])
def free_ok(d): return fresh(d) and d["free"].lower().startswith("yes")
def cprice(p): return re.sub(r"\s*\[[^\]]*\]","",p).strip()
def fl(f):
    m=re.match(r"yes\s*\((.*)\)\s*$",f,re.I) or re.match(r"yes\s*\((.*?)\)(.*)$",f,re.I)
    return "".join(m.groups()).strip() if m else ("a free plan" if f.strip().lower()=="yes" else f)
def nice(c): return _dt.date.fromisoformat(c).strftime("%b %-d, %Y") if c else ""
def mon(c): return _dt.date.fromisoformat(c).strftime("%b %Y")
def checked_html(d):
    c=d.get("checked","")
    return f'<time datetime="{E(c)}">{E(c)}</time>' if c else "no recorded check yet"
def has_aff(d): return d["aff"].lower().startswith("yes")
def link(d,text=None):
    a=f' data-aff="{{{{AFF:{d["slug"]}}}}}" rel="sponsored noopener"' if has_aff(d) else ' rel="noopener"'
    return f'<a href="{E(d["url"])}"{a} data-umami-event="outbound" data-umami-event-tool="{d["slug"]}">{E(text or d["url"])}</a>'
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
CSS+=r"""
.kit{display:grid;grid-template-columns:1fr auto;gap:1rem 1.5rem;align-items:center;margin:2rem 0;padding:1.3rem 1.5rem;border-radius:16px;border:1px solid #8b5cf666;background:linear-gradient(135deg,#8b5cf61f,#22d3ee14)}.kit h2,.kit h3{margin:.1rem 0 .4rem;font-size:1.3rem}.kit p{margin:.2rem 0;color:var(--mut)}.kit ul{margin:.4rem 0 0;padding-left:1.1rem;color:var(--mut);font-size:.92rem}.kit .eyebrow{color:var(--c);font-weight:600;font-size:.8rem;text-transform:uppercase;letter-spacing:.06em}
.kitbar{display:flex;flex-wrap:wrap;gap:.6rem 1rem;align-items:center;justify-content:space-between;margin:1.8rem 0;padding:.7rem 1rem;border-radius:12px;border:1px solid var(--line);background:#22d3ee10;font-size:.95rem}.kitbar b{color:var(--txt)}.kitbar span{color:var(--mut)}.kitbar a.btn{padding:.5rem 1rem;font-size:.9rem}
.crumbs{font-size:.85rem;color:var(--mut);margin:1.2rem 0 0}.crumbs a{color:var(--mut)}.how{font-size:.85rem;color:var(--mut);border-top:1px solid var(--line);padding-top:.8rem;margin-top:2rem}
.chg{list-style:none;padding:0}.chg li{padding:.45rem 0;border-bottom:1px solid var(--line)}.chg time{color:var(--c);font-family:"Space Grotesk";font-size:.85rem;margin-right:.5rem}
@media (max-width:640px){.kit{grid-template-columns:1fr}}"""
CSS+=r"""
.quizbar{display:flex;flex-wrap:wrap;gap:.6rem 1rem;align-items:center;justify-content:space-between;margin:1.8rem 0;padding:.9rem 1.1rem;border-radius:14px;border:1px solid #8b5cf666;background:linear-gradient(135deg,#8b5cf622,#22d3ee12)}.quizbar b{color:var(--txt)}.quizbar span{color:var(--mut)}.quizbar a.btn{padding:.55rem 1.1rem;font-size:.92rem}
.qhero{padding:2.2rem 0 .4rem;text-align:center}.qhero h1{font-size:clamp(2rem,7vw,3.2rem);margin:.5rem 0}.qhero .lead{color:var(--mut);font-size:1.08rem;max-width:520px;margin:.4rem auto 0}
.qpill{display:inline-flex;gap:.5rem;align-items:center;font-size:.8rem;font-weight:600;color:#6ee7b7;border:1px solid #065f4699;background:#064e3b44;border-radius:999px;padding:.3rem .8rem;margin:0}
.quiz{--qf:#34d399;--qp:#a78bfa;--qs:#fb7185;max-width:640px;margin:1.2rem auto 2rem;scroll-margin-top:84px}
.qtop{display:flex;align-items:center;gap:.8rem;margin:.4rem 0 1.4rem}.qprog{flex:1;height:8px;border-radius:99px;background:#ffffff14;overflow:hidden}.qprog span{display:block;height:100%;border-radius:99px;background:var(--g);transition:width .35s cubic-bezier(.2,.8,.2,1)}
.qstepn{font:600 .85rem "Space Grotesk",Inter,sans-serif;color:var(--mut);min-width:2.2rem;text-align:right}
.qicon{font:inherit;font-size:1.1rem;width:40px;height:40px;border-radius:12px;border:1px solid var(--line);background:var(--bg2);color:var(--txt);cursor:pointer;flex:none}.qicon[hidden]{display:block!important;visibility:hidden}
.qstep{animation:qin .32s cubic-bezier(.2,.8,.2,1)}@keyframes qin{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
.quiz h2{font-size:clamp(1.6rem,5.5vw,2.1rem);margin:0 0 1.1rem}.quiz h2:focus{outline:none}
.qopts{display:grid;gap:.65rem;grid-template-columns:1fr 1fr}
.qopt{display:flex;align-items:center;gap:.8rem;font:500 1.05rem/1.3 Inter,system-ui,sans-serif;text-align:left;color:var(--txt);background:linear-gradient(180deg,#171a35,#11132a);border:1px solid var(--line);border-radius:16px;padding:1rem 1.1rem;min-height:64px;cursor:pointer;transition:border-color .15s,transform .15s,background .15s}
.qopt:hover{border-color:var(--v);transform:translateY(-2px)}.qopt:active{transform:scale(.98)}.qe{font-size:1.4rem;line-height:1;flex:none}
.qlink{font:inherit;background:none;border:0;color:var(--mut);text-decoration:underline;text-underline-offset:3px;cursor:pointer;padding:.9rem 0 0;font-size:.92rem}
.qres{animation:qin .35s cubic-bezier(.2,.8,.2,1)}.qmeta{margin:0;color:var(--c);font-weight:600;font-size:.85rem;text-transform:uppercase;letter-spacing:.06em}
.qres h2{margin:.2rem 0 1rem}
.qcard{position:relative;background:linear-gradient(180deg,#171a35,#10122a);border:1px solid var(--line);border-radius:20px;padding:1.15rem 1.2rem;margin:0 0 .8rem;box-shadow:0 10px 30px #0006}
.qcard:before{content:"";position:absolute;inset:0 0 auto 0;height:3px;border-radius:20px 20px 0 0;background:var(--qc,var(--c))}
.q-free{--qc:var(--qf)}.q-paid{--qc:var(--qp)}.q-skip{--qc:var(--qs)}
.qlabel{margin:0;font-size:.72rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--qc)}
.qcard h3{margin:.25rem 0 .3rem;font-size:1.45rem}.qcard h3 a{color:var(--txt)}.qwhy{margin:0 0 .6rem;color:#c9cce6;font-size:1rem}
.qcatch{margin:-.2rem 0 .6rem;font-size:.85rem;color:#fcd34d}.qc-soft{color:var(--mut)}
.qchips{display:flex;flex-wrap:wrap;gap:.4rem}.qchip{font-size:.78rem;font-weight:600;padding:.25rem .6rem;border-radius:999px;background:#ffffff0d;border:1px solid var(--line);color:#d7d9f0}.qc-free{color:#6ee7b7;border-color:#065f46;background:#064e3b55}.qc-date{color:var(--mut);font-weight:500}
.qgate{display:block;margin:0 0 .8rem;padding:1.25rem 1.2rem 1rem;border-radius:20px;border:1px solid #8b5cf699;background:radial-gradient(500px 200px at 100% 0,#22d3ee22,transparent),linear-gradient(135deg,#2a1d5e,#141634);box-shadow:0 0 0 1px #8b5cf622,0 16px 40px #8b5cf633;text-align:center}
.qgate h3{margin:.2rem 0 .8rem;font-size:1.3rem;line-height:1.2}.qlockline{margin:0;font-size:.8rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:#c4b5fd}
.qframe{min-height:52px;border-radius:12px;overflow:hidden;background:#0b0b14;height:52px}.qframe.qready{height:auto}
.qtrust{margin:.6rem 0 0;font-size:.85rem;color:var(--mut)}.qalt{display:none;margin:.4rem 0 0;font-size:.85rem}.qalt.qshow{display:block}
.qnothanks{font:inherit;font-size:.82rem;background:none;border:0;color:#8b90b3;text-decoration:underline;text-underline-offset:3px;cursor:pointer;padding:.7rem .5rem .1rem}
.qanchor{display:flex;align-items:center;justify-content:center;gap:.55rem;margin:-.35rem 0 .6rem;font-size:.95rem;color:#cbd5e1}.qanchor s{color:#94a3b8;text-decoration-color:#f87171;text-decoration-thickness:2px}.qfreeb{background:#10b981;color:#04261b;border-radius:999px;padding:.12rem .6rem;font-size:.85rem;letter-spacing:.03em}.qanote{margin:.15rem 0 0;font-size:.72rem;color:#8b93a7}
.qsuccess{font-size:1.05rem;font-weight:600;color:#6ee7b7;margin:.2rem 0}.qgate.qdone{border-color:#065f46;background:linear-gradient(135deg,#064e3b88,#141634)}
.qlocked .qcard{min-height:112px}.qlocked .qcard h3,.qlocked .qcard p.qbar{filter:blur(6px);user-select:none}.qbar{height:.8rem;border-radius:6px;background:#ffffff1a;margin:.5rem 0;width:70%}.qbar.s{width:45%}
.qlock{position:absolute;top:1rem;right:1.1rem;font-size:1.1rem;opacity:.85}
.qin{animation:qin .4s cubic-bezier(.2,.8,.2,1)}
.qactions{display:flex;gap:.6rem;justify-content:center;flex-wrap:wrap;margin:1.2rem 0 .4rem}.qbtn2{font:inherit;font-size:.9rem;color:var(--txt);background:var(--bg2);border:1px solid var(--line);border-radius:12px;padding:.6rem 1rem;cursor:pointer;min-height:44px}.qbtn2:hover{border-color:var(--v)}
.qfine{text-align:center;color:var(--mut);font-size:.82rem;margin:.4rem 0}
.qsticky{position:fixed;left:.75rem;right:.75rem;bottom:.75rem;z-index:60;display:none;align-items:center;justify-content:space-between;gap:.8rem;padding:.6rem .6rem .6rem 1rem;border-radius:16px;background:#1b1640f2;border:1px solid #8b5cf699;backdrop-filter:blur(10px);box-shadow:0 10px 30px #000a;font-size:.92rem;font-weight:600}
.qsticky button{font:600 .92rem Inter,sans-serif;border:0;border-radius:12px;padding:.6rem 1rem;background:var(--g);color:#0a0b14;cursor:pointer;min-height:44px}
.qseo{max-width:760px;margin:3rem auto 0;border-top:1px solid var(--line);padding-top:1rem;color:var(--mut)}.qseo summary{cursor:pointer;font-weight:600;color:var(--txt);padding:.4rem 0}.qseo h2{font-size:1.2rem}
.qpicks td:first-child{white-space:nowrap}[hidden]{display:none!important}
body:has(#quiz) .crumbs,body:has(#quiz) #newsletter{display:none}.qframe{max-width:440px;margin:0 auto}
@media (max-width:640px){.qopts{grid-template-columns:1fr}.qopt{min-height:58px}.qhero{padding:1.4rem 0 0}.qsticky:not([hidden]){display:flex}body:has(#quiz) nav{flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none}body:has(#quiz) nav .logo{width:auto;flex:none}body:has(#quiz) nav a{flex:none}}
@media (prefers-reduced-motion:reduce){.qstep,.qres,.qin{animation:none}}"""
def quizbar(job_slug=None,job=None):
    href="/quiz/"+("#j="+job_slug if job_slug else "")
    t=f"Not sure which one fits <i>you</i>? Answer 3 questions and get the free pick, the paid pick worth it, and one to skip{' for this job' if job else ''}."
    return f'<div class="quizbar" role="note"><span><b>30-second quiz:</b> {t}</span><a class="btn" href="{href}" data-umami-event="quiz-cta">Find your AI stack</a></div>'
def kit_offer(variant="default",tool=None):
    head={"default":"Get the free 5-Minute AI Stack Kit","free":"Want the whole $0 Stack?","pricing":f"Get alerted when {tool} changes price" if tool else "Get price-change alerts","job":"Get the full stack for every job"}[variant]
    lead={"default":"Every job, our top pick, the real price and free-tier limits, checked weekly. Free.","free":"The free kit has the best free option for all 10 jobs, with the exact limits, plus 4 starter stacks under $50/mo.","pricing":"Subscribers hear first when a tool in our kit changes its price or free tier. You also get the free 5-Minute AI Stack Kit.","job":"The free kit covers all 10 jobs with prices, free tiers, starter stacks and a Skip List."}[variant]
    return f'<aside class="kit" aria-label="Free AI Stack Kit"><div><p class="eyebrow">Free download for subscribers</p><h2>{E(head)}</h2><p>{E(lead)}</p><ul><li>Best tool per job, with price and last-checked date</li><li>The $0 Stack and 4 starter stacks under $50/mo</li><li>Skip List, first-hour tips, and a 24-hour wrong-price fix</li></ul></div><a class="btn" href="#newsletter" data-umami-event="kit-cta" data-umami-event-variant="{variant}">Get the free kit</a></aside>'
KITBAR='<div class="kitbar" role="note"><span><b>Free:</b> the 5-Minute AI Stack Kit. Every job, real prices, checked weekly.</span><a class="btn" href="#newsletter" data-umami-event="kit-bar">Send me the kit</a></div>'
def crumbs(items):
    h=" / ".join(f'<a href="{u}">{E(n)}</a>' if u else E(n) for n,u in items)
    ld={"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":i+1,"name":n,**({"item":SITE+u} if u else {})} for i,(n,u) in enumerate(items)]}
    return f'<nav class="crumbs" aria-label="Breadcrumb">{h}</nav>',ld
HOW='<p class="how">How we check: every price and free tier on this page comes from the vendor\'s own pricing page, with the date we checked it. If we can\'t verify something, we say so. Found a wrong price? Email <a href="mailto:info@usethissi.com">info@usethissi.com</a> and we fix it within 24 hours.</p>'
def page(path,title,desc,body,ld=None,lastmod=None,noindex=False):
    canon=SITE+"/"+path.replace("index.html","")
    if isinstance(ld,list): ld={"@context":"https://schema.org","@graph":ld}
    ldj=f'<script type="application/ld+json">{json.dumps(ld)}</script>' if ld else ""
    LASTMOD[path]=(lastmod or STATIC_LASTMOD.get(path) or DATA_DATE, noindex)
    rob='<meta name="robots" content="noindex,follow">' if noindex else ""
    um=f'<script defer src="https://cloud.umami.is/script.js" data-website-id="{E(UMAMI)}"></script>' if UMAMI else ""
    pages[path]=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="impact-site-verification" value="1c1f3cbc-5bfd-4425-80ce-c30b259ba149"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}"><link rel="canonical" href="{canon}">{rob}
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{canon}"><meta property="og:type" content="website">
<meta name="theme-color" content="#0a0b14"><link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" type="image/png" sizes="192x192" href="/icon-192.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@500;700&display=swap"><link rel="stylesheet" href="/style.css">{ldj}
<script>window.va=window.va||function(){{(window.vaq=window.vaq||[]).push(arguments)}};</script><script defer src="/_vercel/insights/script.js"></script>{um}</head><body>
<a class="skip" href="#main">Skip to content</a><header><nav aria-label="Main"><a class="logo" href="/">⚡ {NAME}</a><a href="/use-cases/">Use cases</a><a href="/tools/">Tools</a><a href="/free/">Free tools</a><a href="/new/">New this week</a><a href="/about/">About</a><a href="/quiz/" class="pick" data-umami-event="quiz-nav">Find your stack</a><a href="#newsletter" class="pick" data-umami-event="kit-nav">Free kit</a></nav></header>
<main id="main" class="wrap">{body}</main>
<section id="newsletter"><h2>Get the free 5-Minute AI Stack Kit</h2><p>Subscribe and we'll email you the kit: the best AI tool for each job with real prices and free-tier limits, the $0 Stack, 4 starter stacks under $50/mo, and a Skip List. Plus a 5-minute weekday brief on what launched, what changed, and what to try today. Free, one-click unsubscribe.</p><script async src="https://subscribe-forms.beehiiv.com/v3/loader.js" data-beehiiv-form="767b56cc-d716-4bab-a162-0baf03c34b2c"></script><p><small>Form not loading? <a href="https://usethissi.beehiiv.com/subscribe" rel="noopener">Subscribe on beehiiv</a>.</small></p></section>
<footer>Some links are affiliate links. <a href="/about/#affiliates">Disclosure</a>. Directory data last checked {DATA_DATE}; each tool shows its own last-checked date. Contact: <a href="mailto:info@usethissi.com">info@usethissi.com</a></footer><script type="text/javascript" async src="https://subscribe-forms.beehiiv.com/attribution.js"></script></body></html>'''
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
tm={}
for L in uses.values():
    for d in L: tm.setdefault(d["slug"],[]).append(d)
def tool_checked(s): return max((x["checked"] for x in tm[s] if x["checked"]),default="")
# ---- gates for programmatic pages
def has_pricing_page(d): return vprice(d) and len([p for p in plans.get(d["tool"],[]) if p["per_month_annual"] or p["per_month_monthly"]])>=2
PRICING={s:ds[0] for s,ds in tm.items() if has_pricing_page(ds[0])}
FREEJOBS={}
for u,L in uses.items():
    F=[d for d in L if free_ok(d)]
    if len(F)>=3: FREEJOBS[u]=F
def catch(f):
    x=f.lower()
    if re.search(r"non-commercial|no commercial|personal",x): return "Not for commercial use on the free tier"
    if re.search(r"trial|one-time",x): return "Runs out: a one-time allowance or trial, not a monthly reset"
    if re.search(r"self-host|open source|byok|weights|apache|mit",x): return "You host it yourself or pay your own model costs"
    if "watermark" in x: return "Output carries a watermark"
    if re.search(r"/day|daily|/week|weekly|/mo|month",x): return "Usage caps reset on a schedule; heavy use needs a paid plan"
    return "Limits not published in detail; check the vendor's page"
def num(x):
    try: return float(x)
    except: return None
def money(v,cur="USD"):
    sym="€" if cur=="EUR" else "$"
    return f"{sym}{v:,.2f}".replace(".00","")
def plink(d): return ' · <a href="/tools/%s/pricing/">pricing</a>'%d["slug"] if d["slug"] in PRICING else ""
TOPB=' <span class="badge b-top">Top pick</span>'
# use case pages
ucl=[]
for u,L in uses.items():
    s=slug(u); t=top(L); alts=[d for d in L if d is not t]; ucl.append((u,s,t))
    lm=max((d["checked"] for d in L if d["checked"]),default=DATA_DATE)
    rowsh="".join(f'<tr><td>{E(d["role"])}</td><td><a href="/tools/{d["slug"]}/">{E(d["tool"])}</a>{plink(d)}</td><td>{E(d["reason"])}</td><td>{E(d["free"])}</td><td>{E(d["price"])}</td><td>{checked_html(d)}</td></tr>' for d in L)
    cb,cld=crumbs([("Home","/"),("Use cases","/use-cases/"),(u,None)])
    freelink=f'<p>Only want free options? See <a href="/free/{s}/">free AI tools to {E(u[0].lower()+u[1:])}</a>, with the limits spelled out.</p>' if u in FREEJOBS else ""
    body=f'''{cb}<article><p class="pick">{ICON.get(u,"✨")} Use case</p><h1>Best AI tools to {E(u[0].lower()+u[1:])}</h1>
<p class="tldr"><strong>Short answer:</strong> Use <a href="/tools/{t["slug"]}/">{E(t["tool"])}</a>. {E(t["reason"])}. Free tier: {E(t["free"])}. Paid from {E(t["price"])}. Alternatives: {", ".join(E(a["tool"]) for a in alts[:2])}.</p>
<h2>Top pick: {E(t["tool"])}</h2><p>{E(t["reason"])}. Official site: {link(t)}</p>{KITBAR}
<h2>All options</h2><ul class="grid">{"".join(tcard(d) for d in L)}</ul>{quizbar(s,u)}<h2>Compare</h2><div class="tablewrap"><table><thead><tr><th>Role</th><th>Tool</th><th>Why</th><th>Free tier</th><th>Paid from</th><th>Last checked</th></tr></thead><tbody>{rowsh}</tbody></table></div>
{kit_offer("job")}{freelink}
<p><small>Last checked is per tool (see the table). Page updated <time datetime="{lm}">{lm}</time>. Prices change, so confirm on the vendor's site.</small></p>{HOW}</article>'''
    ld=[{"@type":"CollectionPage","name":f"Best AI tools to {u}","url":f"{SITE}/use-cases/{s}/","dateModified":lm,"mainEntity":{"@type":"ItemList","name":f"AI tools to {u}","itemListElement":[{"@type":"ListItem","position":i+1,"url":f"{SITE}/tools/{d['slug']}/","name":d["tool"]} for i,d in enumerate(L)]}},cld]
    ld[0]["mainEntity"]["@type"]="ItemList"
    page(f"use-cases/{s}/index.html",f"Best AI tools to {u} (checked {mon(lm)}) | {NAME}",f"Top pick: {t['tool']}. {t['reason']}. Compare {len(L)} tools with prices and free tiers, each with its own last-checked date.",body,ld,lastmod=lm)
page("use-cases/index.html",f"AI tools by use case | {NAME}","Pick the right AI tool for the job: one top pick per use case, plus alternatives.",
 "<h1>Use cases</h1>"+quizbar()+"<ul class=\"grid\">"+"".join(f'<li><a class="card" href="/use-cases/{s}/"><span class="ico" aria-hidden="true">{ICON.get(u,"✨")}</span><h3>{E(u)}</h3><p>Top pick: <span class="pick">{E(t["tool"])}</span></p></a></li>' for u,s,t in ucl)+"</ul>"+kit_offer(),
 {"@context":"https://schema.org","@type":"ItemList","itemListElement":[{"@type":"ListItem","position":i+1,"url":f"{SITE}/use-cases/{s}/","name":u} for i,(u,s,t) in enumerate(ucl)]})
# ---- schema helpers
def offers_for(d):
    if not vprice(d): return None
    p=cprice(d["price"])
    m=re.search(r'([$€])\s?([\d,]+(?:\.\d+)?)',p)
    if m: return {"@type":"Offer","price":m.group(2).replace(",",""),"priceCurrency":"EUR" if m.group(1)=="€" else "USD","description":f"Starting paid price: {p}","url":d["url"]}
    if re.search(r'\bfree\b',p,re.I): return {"@type":"Offer","price":"0","priceCurrency":"USD","description":p,"url":d["url"]}
    return None
def sw(d,extra_offers=None):
    o={"@type":"SoftwareApplication","name":d["tool"],"url":d["url"],"applicationCategory":"BusinessApplication","operatingSystem":"Web","description":d["reason"]}
    of=extra_offers or offers_for(d)
    if of: o["offers"]=of
    return o
# tool pages (merge duplicates)
for s,ds in tm.items():
    d=ds[0]; lc=tool_checked(s); stale=not fresh(d)
    ucs="".join(f'<li><a href="/use-cases/{slug(x["use"])}/">{E(x["use"])}</a> ({E(x["role"])})</li>' for x in ds)
    cb,cld=crumbs([("Home","/"),("Tools","/tools/"),(d["tool"],None)])
    pl=f'<p><a class="btn ghost" style="margin-left:0" href="/tools/{s}/pricing/">See every {E(d["tool"])} plan and what you\'ll really pay →</a></p>' if s in PRICING else ""
    sib=[x for x in uses[d["use"]] if x["slug"]!=s and vprice(x)][:3]
    sibh=("<h2>Alternatives worth checking</h2><ul>"+"".join(f'<li><a href="/tools/{x["slug"]}/">{E(x["tool"])}</a>: {E(x["reason"])}. From {E(cprice(x["price"]))} (checked {nice(x["checked"])}).</li>' for x in sib)+"</ul>") if sib else ""
    stalenote='<p class="tldr"><strong>Heads up:</strong> we haven\'t been able to verify this tool\'s current pricing in the last 30 days. Treat the details below as unconfirmed.</p>' if stale else ""
    body=f'''{cb}<article><h1>{E(d["tool"])}</h1><div>{badges(d)}</div><p class="tldr">{E(d["reason"])}.</p>{stalenote}
<dl><dt>Free tier</dt><dd>{E(d["free"])}</dd><dt>Paid from</dt><dd>{E(d["price"])}</dd><dt>Official site</dt><dd>{link(d)}</dd><dt>Affiliate program</dt><dd>{E(d["aff"])}</dd><dt>Last checked</dt><dd>{checked_html(d)}</dd></dl>{pl}
{kit_offer("pricing",d["tool"]) if not stale else kit_offer()}
<h2>Listed for</h2><ul>{ucs}</ul>{sibh}<p><small>Last checked: {checked_html(d)}</small></p>{HOW}</article>'''
    ld=[sw(d),{"@type":"WebPage","name":d["tool"],"url":f"{SITE}/tools/{s}/",**({"dateModified":lc} if lc else {})},cld]
    title=f"{d['tool']}: free tier, price and alternatives | {NAME}" if s in PRICING else f"{d['tool']} pricing, free tier and alternatives | {NAME}"
    page(f"tools/{s}/index.html",title,f"{d['tool']}: {d['reason']}. Free tier: {d['free']}. From {cprice(d['price'])}.",body,ld,lastmod=lc or None,noindex=stale)
# ---- [tool] pricing pages (gated)
for s,d in PRICING.items():
    P=plans[d["tool"]]; lc=max(p["checked"] for p in P); cur=P[0]["currency"]
    rowsp="".join(f'<tr><td><b>{E(p["plan"])}</b></td><td>{money(num(p["per_month_annual"]),cur)+"/mo" if num(p["per_month_annual"]) is not None else "n/a"}</td><td>{money(num(p["per_month_monthly"]),cur)+"/mo" if num(p["per_month_monthly"]) is not None else "n/a"}</td><td>{E(p["includes"])}</td></tr>' for p in P)
    yr=[]
    for p in P:
        a,m=num(p["per_month_annual"]),num(p["per_month_monthly"])
        if (a or 0)==0 and (m or 0)==0: continue
        if a and m: yr.append(f'<li><b>{E(p["plan"])}</b>: {money(a*12,cur)} a year billed annually vs {money(m*12,cur)} paying monthly. Annual saves {money(m*12-a*12,cur)} ({round((1-a/m)*100)}%).</li>')
        elif a: yr.append(f'<li><b>{E(p["plan"])}</b>: {money(a*12,cur)} a year (price shown is per month, billed annually).</li>')
        elif m: yr.append(f'<li><b>{E(p["plan"])}</b>: {money(m*12,cur)} a year if you stay 12 months.</li>')
    free=[p for p in P if (num(p["per_month_annual"]) or 0)==0 and (num(p["per_month_monthly"]) or 0)==0 and (p["per_month_annual"] or p["per_month_monthly"])]
    hist=[c for c in changes if c["tool"]==d["tool"] and c["field"] in("starting_paid_price","free_tier")]
    histh="<ul class=\"chg\">"+"".join(f'<li><time datetime="{c["date"]}">{nice(c["date"])}</time>{"Starting price" if c["field"]=="starting_paid_price" else "Free tier"}: we had "{E(cprice(c["old"]) or "not listed")}"; verified on the official page as "{E(cprice(c["new"]))}"</li>' for c in hist)+"</ul>" if hist else f"<p>No correction to the starting price or free tier in our checks so far (latest check {nice(lc)}). When it changes, it'll show up here and in the brief.</p>"
    alts=[x for x in uses[d["use"]] if x["slug"]!=s and vprice(x)]
    alth="".join(f'<tr><td><a href="/tools/{x["slug"]}/{"pricing/" if x["slug"] in PRICING else ""}">{E(x["tool"])}</a></td><td>{E(x["free"])}</td><td>{E(cprice(x["price"]))}</td><td>{checked_html(x)}</td></tr>' for x in alts)
    cb,cld=crumbs([("Home","/"),("Tools","/tools/"),(d["tool"],f"/tools/{s}/"),("Pricing",None)])
    cheapest=min([v for p in P for v in (num(p["per_month_annual"]),num(p["per_month_monthly"])) if v],default=None)
    body=f'''{cb}<article><p class="pick">Pricing · checked {nice(lc)}</p><h1>{E(d["tool"])} pricing</h1>
<p class="tldr"><strong>Short answer:</strong> {E(d["tool"])} {"has a free plan, and paid plans" if free else "paid plans"} start at {money(cheapest,cur) if cheapest else E(cprice(d["price"]))} a month{" (billed annually)" if cheapest and any(num(p["per_month_annual"])==cheapest for p in P) else ""}. Free tier: {E(fl(d["free"]))}. We checked every plan below on the official pricing page on {nice(lc)}.</p>
<h2>Every plan</h2><div class="tablewrap"><table><thead><tr><th>Plan</th><th>Billed annually</th><th>Billed monthly</th><th>What you get</th></tr></thead><tbody>{rowsp}</tbody></table></div>
<p><small>"n/a" means that billing option isn't listed. Prices exclude tax. Source: <a href="{E(P[0]["source_url"])}" rel="noopener">official pricing page</a>.</small></p>
{kit_offer("pricing",d["tool"])}
<h2>What you'll actually pay in a year</h2><ul>{"".join(yr)}</ul>
<h2>Price check log</h2>{histh}
<h2>Cheaper or free alternatives for {E(d["use"][0].lower()+d["use"][1:])}</h2><div class="tablewrap"><table><thead><tr><th>Tool</th><th>Free tier</th><th>Paid from</th><th>Last checked</th></tr></thead><tbody>{alth}</tbody></table></div>
<p>Full comparison: <a href="/use-cases/{slug(d["use"])}/">best AI tools to {E(d["use"][0].lower()+d["use"][1:])}</a>. Back to the <a href="/tools/{s}/">{E(d["tool"])} overview</a>.</p>{HOW}</article>'''
    offs=[{"@type":"Offer","name":p["plan"],"price":str(num(p["per_month_monthly"]) if num(p["per_month_monthly"]) is not None else num(p["per_month_annual"])).replace(".0","") ,"priceCurrency":cur,"url":p["source_url"]} for p in P if (num(p["per_month_monthly"]) is not None or num(p["per_month_annual"]) is not None)]
    for o in offs:
        if o["price"].endswith(".") : o["price"]=o["price"][:-1]
    ld=[sw(d,offs),{"@type":"WebPage","name":f"{d['tool']} pricing","url":f"{SITE}/tools/{s}/pricing/","dateModified":lc},cld]
    page(f"tools/{s}/pricing/index.html",f"{d['tool']} pricing (checked {mon(lc)}): every plan, free tier, real cost | {NAME}",f"{d['tool']} pricing checked {nice(lc)}: {len(P)} plans, free tier ({d['free']}), annual vs monthly cost, price changes and cheaper alternatives.",body,ld,lastmod=lc)
# ---- free AI tools for [job] (gated)
for u,F in FREEJOBS.items():
    s=slug(u); lc=max(d["checked"] for d in F); best=F[0] if F[0]["role"]=="Top pick" else F[0]
    rowsf="".join(f'<tr><td><a href="/tools/{d["slug"]}/">{E(d["tool"])}</a>{TOPB if d["role"]=="Top pick" else ""}</td><td>{E(d["free"])}</td><td>{E(catch(d["free"]))}</td><td>{E(cprice(d["price"])) if vprice(d) else "Not verified"}</td><td>{checked_html(d)}</td></tr>' for d in F)
    paid=[d for d in uses[u] if vprice(d) and re.search(r"\$\d",cprice(d["price"]))]
    cb,cld=crumbs([("Home","/"),("Free AI tools","/free/"),(u,None)])
    nonc=[d["tool"] for d in F if catch(d["free"]).startswith("Not for commercial")]
    warn=(" Watch out: "+", ".join(E(x) for x in nonc)+" "+("doesn't" if len(nonc)==1 else "don't")+" allow commercial use on the free tier.") if nonc else ""
    pv=lambda d: float(re.search(r"\$([\d.]+)",cprice(d["price"])).group(1))
    cheap="; ".join('<a href="/tools/%s/">%s</a> from %s'%(d["slug"],E(d["tool"]),E(cprice(d["price"]))) for d in sorted(paid,key=pv)[:3])
    body=f'''{cb}<article><p class="pick">{ICON.get(u,"✨")} Free options · limits checked {nice(lc)}</p><h1>Free AI tools to {E(u[0].lower()+u[1:])}</h1>
<p class="tldr"><strong>Short answer:</strong> start with <a href="/tools/{best["slug"]}/">{E(best["tool"])}</a> on its free plan{(" ("+E(fl(best["free"]))+")") if fl(best["free"])!="a free plan" else ""}. We found {len(F)} tools for this job with a free tier we verified in the last 30 days.{warn}</p>
{quizbar(s,u)}<h2>Every free option, with the catch</h2><div class="tablewrap"><table><thead><tr><th>Tool</th><th>Free tier, as listed</th><th>The catch</th><th>Paid from</th><th>Last checked</th></tr></thead><tbody>{rowsf}</tbody></table></div>
{kit_offer("free")}
<h2>When it's worth paying</h2><p>Upgrade when you hit the free limits every week, or when you need commercial rights. The cheapest verified paid plans for this job right now: {cheap}.</p>
<p>See the full comparison, paid tools included: <a href="/use-cases/{s}/">best AI tools to {E(u[0].lower()+u[1:])}</a>.</p>{HOW}</article>'''
    ld=[{"@type":"CollectionPage","name":f"Free AI tools to {u}","url":f"{SITE}/free/{s}/","dateModified":lc,"mainEntity":{"@type":"ItemList","itemListElement":[{"@type":"ListItem","position":i+1,"url":f"{SITE}/tools/{d['slug']}/","name":d["tool"]} for i,d in enumerate(F)]}},cld]
    page(f"free/{s}/index.html",f"Free AI tools to {u} (limits checked {mon(lc)}) | {NAME}",f"{len(F)} free AI tools to {u[0].lower()+u[1:]}, with the exact free-tier limits and the catch for each. Checked {nice(lc)}.",body,ld,lastmod=lc)
if FREEJOBS:
    lcf=max(max(d["checked"] for d in F) for F in FREEJOBS.values())
    page("free/index.html",f"Free AI tools by job, limits checked | {NAME}","Free AI tools for every builder job, with the real free-tier limits and the catch, checked in the last 30 days.",
     "<h1>Free AI tools by job</h1><p>Only tools whose free tier we verified on the vendor's site in the last 30 days.</p>"+quizbar()+"<ul class=\"grid\">"+"".join(f'<li><a class="card" href="/free/{slug(u)}/"><span class="ico" aria-hidden="true">{ICON.get(u,"✨")}</span><h3>{E(u)}</h3><p>{len(F)} free options. Start with <span class="pick">{E(F[0]["tool"])}</span>.</p></a></li>' for u,F in FREEJOBS.items())+"</ul>"+kit_offer("free"),
     {"@context":"https://schema.org","@type":"ItemList","itemListElement":[{"@type":"ListItem","position":i+1,"url":f"{SITE}/free/{slug(u)}/","name":f"Free AI tools to {u}"} for i,u in enumerate(FREEJOBS)]},lastmod=lcf)
# ---- /quiz/: "Find your AI stack in 30 seconds" (data from quiz.py, computed from data.csv at build time)
import quiz as _quiz
QUIZ=_quiz.build(uses,fresh,bad_price,cprice,fl,nice,slug)
QUIZ_ELIG=QUIZ.pop("_eligible")
QUIZ["defaultSkill"]=_quiz.DEFAULT_SKILL; QUIZ["icons"]={slug(u):ICON.get(u,"") for u in uses}; QUIZ["freeJobs"]=[slug(u) for u in FREEJOBS]
BEEHIIV_FORM="767b56cc-d716-4bab-a162-0baf03c34b2c"; QUIZ_FORM="6601f72f-cbe4-41fa-8313-787075c593f7"; BEEHIIV_PUB="d420e641-998f-43f4-a9ec-f398fd8e23c6"
QUIZ_JS=open("src/quiz.js").read()
def _qcell(t,extra=""):
    return f'<a href="/tools/{t["slug"]}/">{E(t["tool"])}</a><br><small>{E(extra or t["price"])}</small>' if t else "None"
_qrows="".join(f'<tr><td><a href="/use-cases/{j["slug"]}/">{E(j["name"])}</a></td><td>{_qcell(r["free"],"Free: "+r["free"]["freeShort"] if r["free"] else "")}</td><td>{_qcell(r["paid"])}</td><td>{_qcell(r["skip"],r["skip_note"])}</td></tr>' for j in QUIZ["jobs"] for r in [_quiz.result(QUIZ,"founder",j["slug"],"20","mid")])
QUIZ_LM=max(t["checked"] for t in QUIZ["tools"])
_qn=len(QUIZ["tools"])
_qdata=json.dumps(QUIZ,separators=(",",":")).replace("</","<\\/")
cb,cld=crumbs([("Home","/"),("Find your AI stack",None)])
qbody=f"""{cb}<section class="qhero" id="qhero"><p class="qpill">Free &middot; 30 seconds &middot; No paid placements.</p><h1>You don't need 40 AI tools. <span class="grad">You need 3.</span></h1><p class="lead">Answer 3 questions. Get the free pick, the paid pick worth it, and one to skip, prices checked this week.</p></section>
<div id="quiz" class="quiz" data-form="{QUIZ_FORM}" data-pub="{BEEHIIV_PUB}">
<div id="qask" aria-live="polite"><noscript><p>The quiz needs JavaScript. The same picks are in "Quick picks by job" below.</p></noscript><p class="qmeta">Loading&hellip;</p></div>
<section id="qres" class="qres" hidden aria-labelledby="qrtitle"><p class="qmeta" id="qmeta"></p><h2 id="qrtitle" tabindex="-1">Your AI stack</h2>
<div id="qfree"></div>
<div id="qfull" hidden></div>
<aside id="qgate" class="kit qgate" aria-labelledby="qgh"><div id="qgatebody"><p class="qlockline" id="qlockline">&#128274; 2 more picks</p><h3 id="qgh">Unlock 2 more picks + the AI Stack Kit</h3><div class="qanchor" id="qanchor" hidden><span>Testing these yourself: <s id="qanchorv"></s></span><b class="qfreeb">Free</b></div><div id="qform"></div><p class="qtrust">Free. Weekday 5-min brief. Unsubscribe anytime.</p><p class="qanote" id="qanote" hidden></p><p class="qalt" id="qalt">Form not loading? <a id="qfallback" href="https://usethissi.beehiiv.com/subscribe?utm_source=quiz&amp;utm_medium=website&amp;utm_campaign=quiz" rel="noopener">Subscribe on beehiiv</a></p><button type="button" class="qnothanks" id="qnothanks" data-skip-gate="1">No thanks, just show me</button></div><div id="qsuccess" hidden><p class="qsuccess">&#10003; You're in. Your full stack is unlocked.</p><p class="qtrust">The AI Stack Kit is on its way to your inbox.</p></div></aside>
<div id="qlocked" class="qlocked" aria-hidden="true"><div class="qcard q-paid"><span class="qlock">&#128274;</span><p class="qlabel">Paid pick</p><h3>Locked pick</h3><p class="qbar"></p><p class="qbar s"></p></div><div class="qcard q-skip"><span class="qlock">&#128274;</span><p class="qlabel">Skip</p><h3>Locked pick</h3><p class="qbar"></p><p class="qbar s"></p></div></div>
<div class="qactions"><button type="button" class="qbtn2" data-copy="1">Copy link</button><button type="button" class="qbtn2" data-restart="1">Start over</button></div>
<p class="qfine">Rules, not sponsors. Only tools checked in the last 30 days. <a id="qall" href="/use-cases/">All options &rarr;</a></p></section>
</div>
<div id="qsticky" class="qsticky" hidden role="region" aria-label="Unlock your stack"><span>&#128274; 2 picks locked</span><button type="button">Unlock free</button></div>
<details class="qseo"><summary>How the quiz picks, and quick picks by job</summary>
<h2>Quick picks by job</h2><p>What a solo builder on $20/mo or less gets. Your answers can change the picks.</p><div class="tablewrap"><table class="qpicks"><thead><tr><th>Job</th><th>Free pick</th><th>Paid pick ($20/mo or less)</th><th>Skip</th></tr></thead><tbody>{_qrows}</tbody></table></div>
<h2>How the quiz picks</h2><ul><li>Only tools checked in the last 30 days with a verified price and free tier ({_qn} listings right now).</li><li><b>Free pick:</b> the best free tier for your job that keeps working.</li><li><b>Paid pick:</b> our highest-ranked tool whose cheapest monthly plan fits your budget.</li><li><b>Skip:</b> the clearest reason in our data not to start there.</li><li>Affiliate deals never affect a pick. Nobody can pay for a spot.</li></ul>{HOW}</details>
<script type="application/json" id="qdata">{_qdata}</script><script>{QUIZ_JS}</script>"""
qld=[{"@type":"WebApplication","name":"Find your AI stack in 30 seconds","url":f"{SITE}/quiz/","applicationCategory":"BusinessApplication","operatingSystem":"Web","browserRequirements":"Requires JavaScript","isAccessibleForFree":True,"offers":{"@type":"Offer","price":"0","priceCurrency":"USD"},"description":"Answer 3 questions about your job, main task and budget. Get a free pick, a paid pick that fits your budget, and one tool to skip, with prices checked in the last 30 days.","dateModified":QUIZ_LM,"publisher":{"@type":"Organization","name":NAME,"url":SITE}},
 {"@type":"WebPage","name":"Find your AI stack in 30 seconds","url":f"{SITE}/quiz/","dateModified":QUIZ_LM},cld]
page("quiz/index.html",f"Find your AI stack in 30 seconds: free quiz | {NAME}","You don't need 40 AI tools. You need 3. Answer 3 questions and get the free pick, the paid pick worth it, and one to skip, with prices checked this week. No paid placements.",qbody,qld,lastmod=QUIZ_LM)
srt=sorted(tm.items())
page("tools/index.html",f"All AI tools | {NAME}",f"Directory of {len(tm)} AI tools for builders, each with its free tier, starting price and last-checked date.",
 "<h1>All tools</h1>"+KITBAR+"<ul class=\"grid\">"+"".join(tcard(ds[0]) for s,ds in srt)+"</ul>"+kit_offer(),
 {"@context":"https://schema.org","@type":"ItemList","itemListElement":[{"@type":"ListItem","position":i+1,"url":f"{SITE}/tools/{s}/","name":ds[0]["tool"]} for i,(s,ds) in enumerate(srt)]})
page("new/index.html",f"New AI tool releases this week | {NAME}","The AI releases from the last two weeks that matter for builders.",
 "<h1>New <span class=\"grad\">this week</span></h1><p>Releases from the last 7 days that matter if you build things. Every item links to its source.</p>"+KITBAR+"<ol class=\"feed\" reversed>"+"".join(f'<li><time datetime="{E(a[:10])}">{E(a)}</time><p>{E(b)}</p><a href="{E(c)}" rel="noopener">Read the source →</a></li>' for a,b,c in reversed(rels))+"</ol>",lastmod=max(r[0][:10] for r in rels))
page("submit/index.html",f"Submit your AI tool | {NAME}","Submit an AI tool for review in the UseThisSI directory.",
 f'<h1>Submit your tool</h1><p>Every tool gets the same review, whether or not it pays. Featured placement will come later and will always be labeled.</p><p><a href="https://github.com/{REPO}/issues/new?template=submit-tool.yml">Submit your tool on GitHub</a> (needs a free GitHub account). We review submissions every week.</p>'+KITBAR)
page("about/index.html",f"About and affiliate disclosure | {NAME}","How UseThisSI picks tools, and how affiliate links work.",
 '<h1>About UseThisSI</h1><p>UseThisSI picks one AI tool per job for builders, vibe coders, agent tinkerers and game devs. Agents re-check pricing regularly, and every page shows when it was last checked.</p>'+KITBAR+'<h2 id="how">How we check</h2><p>Prices and free tiers come from each vendor\'s own pricing page, recorded with the date we checked. Tools we can\'t verify within 30 days are flagged and kept out of search until we can. Found a wrong price? We fix it within 24 hours.</p><h2 id="affiliates">Affiliate disclosure</h2><p>Some outbound links are affiliate links (marked rel="sponsored"). If you buy through one, we may earn a commission at no extra cost to you. Affiliate status never decides our top picks.</p><h2 id="contact">Contact</h2><p>Questions, corrections or sponsorships: <a href="mailto:info@usethissi.com">info@usethissi.com</a></p>')
tops="".join(f'<li><a class="card" href="/use-cases/{s}/"><span class="ico" aria-hidden="true">{ICON.get(u,"✨")}</span><h3>{E(u)}</h3><p>Use <span class="pick">{E(t["tool"])}</span>. {E(t["reason"])}.</p></a></li>' for u,s,t in ucl)
feed="".join(f'<li><time datetime="{E(a[:10])}">{E(a)}</time><p>{E(b)}</p></li>' for a,b,c in list(reversed(rels))[:3])
pc=[c for c in changes if c["field"]=="starting_paid_price"][-6:]
chg="".join(f'<li><time datetime="{c["date"]}">{nice(c["date"])}</time><a href="/tools/{slug(c["tool"])}/{"pricing/" if slug(c["tool"]) in PRICING else ""}">{E(c["tool"])}</a>: now {E(cprice(c["new"]))}</li>' for c in reversed(pc))
chgsec=f'<section><h2>Recently verified prices</h2><ul class="chg">{chg}</ul></section>' if chg else ""
page("index.html",f"{NAME}: the right AI tool for every job","One top pick per job for builders, vibe coders and game devs. Prices checked weekly, plus new releases.",
 f'<section class="hero"><p class="pick">For builders, vibe coders, agent tinkerers and game devs</p><h1>Stop guessing.<br><span class="grad">Use this AI</span> for that job.</h1><p class="lead">{NAME} picks the best AI tool for each job, with two alternatives and current pricing, plus a 5-minute weekday brief on what just launched.</p><a class="btn" href="/quiz/" data-umami-event="quiz-hero">Find your AI stack in 30 seconds</a><a class="btn ghost" href="#newsletter" data-umami-event="kit-hero">Get the free AI Stack Kit</a><p class="qsmall" style="margin-top:.8rem">You don&#39;t need 40 AI tools. You need 3. Free quiz, no paid placements.</p><div class="stats"><div><b>{len(tm)}</b>tools</div><div><b>{len(ucl)}</b>use cases</div><div><b>{DATA_DATE}</b>last price check</div></div></section><section><h2>Top picks by job</h2><ul class="grid">{tops}</ul></section>{kit_offer()}{chgsec}<section><h2>New this week</h2><ol class="feed">{feed}</ol><a href="/new/">See all releases →</a></section>',
 {"@context":"https://schema.org","@type":"WebSite","name":NAME,"url":SITE})
page("404.html",f"Not found | {NAME}","Page not found.",'<h1>Not found</h1><p><a href="/">Go home</a></p>')
shutil.rmtree("dist",ignore_errors=True)
for p,c in pages.items():
    os.makedirs(os.path.dirname("dist/"+p) or "dist",exist_ok=True); open("dist/"+p,"w").write(c)
open("dist/style.css","w").write(CSS)
if os.path.isdir("static"): shutil.copytree("static","dist",dirs_exist_ok=True)
sm=[(SITE+"/"+p.replace("index.html",""),LASTMOD[p][0]) for p in pages if p!="404.html" and not LASTMOD[p][1]]
open("dist/sitemap.xml","w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+"".join(f"<url><loc>{u}</loc><lastmod>{m}</lastmod></url>\n" for u,m in sm)+"</urlset>\n")
open("dist/robots.txt","w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
recent="\n".join(f"- {a}: {b} ({c})" for a,b,c in list(reversed(rels))[:8])
llms=f"""# {NAME}

> One top AI tool pick per job for builders, vibe coders, AI agent tinkerers and indie game devs. Directory data last checked {DATA_DATE}; each tool page shows its own last-checked date.

## Use cases
"""+"".join(f"- [{u}]({SITE}/use-cases/{s}/): top pick {t['tool']}. {t['reason']}.\n" for u,s,t in ucl)+"""
## Free AI tools by job
"""+"".join(f"- [Free AI tools to {u}]({SITE}/free/{slug(u)}/): {len(F)} verified free tiers.\n" for u,F in FREEJOBS.items())+"""
## Find your AI stack (quiz)
- [Find your AI stack in 30 seconds]("""+SITE+"""/quiz/): answer 3 questions (role, main job, budget), get a free pick, a paid pick that fits the budget, and one to skip.

## Pricing pages (every plan, checked)
"""+"".join(f"- [{d['tool']} pricing]({SITE}/tools/{s}/pricing/)\n" for s,d in PRICING.items())+f"""
## Recent releases
{recent}

## FAQ
- Q: How do you pick a top tool? A: One Top pick per use case based on fit for builders, plus honest free-tier and starting paid price with a per-tool last-checked date.
- Q: Are affiliate links labeled? A: Yes. Affiliate outbound links use rel=sponsored and are disclosed on /about/#affiliates.
- Q: Where is pricing verified? A: On each tool page under Last checked. Prices come from vendor pages; unverified fields stay labeled.
- Q: How do I get the weekday brief and the free AI Stack Kit? A: Subscribe at {SITE}/#newsletter or https://usethissi.beehiiv.com/subscribe.

## Pages
- [All tools]({SITE}/tools/)
- [New this week]({SITE}/new/)
- [About and affiliate disclosure]({SITE}/about/)
- [Contact](mailto:info@usethissi.com)
"""
open("dist/llms.txt","w").write(llms)
INDEXNOW_KEY="fcd27737423484d8886b49b06518a52a"
open(f"dist/{INDEXNOW_KEY}.txt","w").write(INDEXNOW_KEY)
print(f"Built {len(pages)} HTML pages ({len(PRICING)} pricing, {len(FREEJOBS)} free-by-job, {sum(1 for p in LASTMOD.values() if p[1])} noindex); sitemap {len(sm)} URLs")
