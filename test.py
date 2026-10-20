#!/usr/bin/env python3
"""Basic tests: build succeeds, required pages and files exist, titles unique, JSON-LD valid, no broken links."""
import subprocess,os,re,json,sys
def ok(c,m): print(("PASS " if c else "FAIL ")+m); return c
r=[ok(subprocess.run([sys.executable,"build.py"]).returncode==0,"build runs")]
for f in ["index.html","new/index.html","submit/index.html","about/index.html","use-cases/index.html","tools/index.html","sitemap.xml","robots.txt","llms.txt"]:
    r.append(ok(os.path.exists("dist/"+f),f"exists {f}"))
htmls=[os.path.join(a,f) for a,_,fs in os.walk("dist") for f in fs if f.endswith(".html")]
titles=[re.search(r"<title>(.*?)</title>",open(p).read()).group(1) for p in htmls]
r.append(ok(len(titles)==len(set(titles)),f"{len(htmls)} pages, titles unique"))
r.append(ok(all('name="description"' in open(p).read() for p in htmls),"all pages have a meta description"))
lds=[json.loads(m) for p in htmls for m in re.findall(r'application/ld\+json">(.*?)</script>',open(p).read())]
def _types(l):
    out=set()
    for n in (l.get("@graph") or [l]):
        out.add(n["@type"]); me=n.get("mainEntity")
        if isinstance(me,dict): out.add(me["@type"])
    return out
types=set().union(*[_types(l) for l in lds])
sw=[n for l in lds for n in (l.get("@graph") or [l]) if n["@type"]=="SoftwareApplication"]
r.append(ok(all("aggregateRating" not in n and "review" not in n for n in sw),"no ratings/reviews in SoftwareApplication (none invented)"))
r.append(ok(sum("offers" in n for n in sw)>=40,f"{sum('offers' in n for n in sw)} SoftwareApplication nodes carry real offers"))
r.append(ok({"ItemList","SoftwareApplication"}<=types,f"JSON-LD parses, types {sorted(types)}"))
uc=[p for p in htmls if "/use-cases/" in p and p.count("/")==3]
r.append(ok(all('class="tldr"' in open(p).read() and "Last checked" in open(p).read() for p in uc),f"{len(uc)} use-case pages have a summary and a last-checked date"))
r.append(ok(uc and all('"FAQPage"' in open(p).read() and '"Question"' in open(p).read() for p in uc),f"{len(uc)} use-case pages carry FAQPage schema"))
tp=[p for p in htmls if "/tools/" in p and p.count("/")==3]
r.append(ok(all("<dt>Last checked</dt>" in open(p).read() for p in tp),f"{len(tp)} tool pages show a per-tool last-checked date"))
r.append(ok("{{AFF:" in "".join(open(p).read() for p in htmls),"affiliate placeholders present"))
llms=open("dist/llms.txt").read()
r.append(ok("## Recent releases" in llms and "## FAQ" in llms and "rel=sponsored" in llms,"llms.txt has releases FAQ and affiliate note"))
r.append(ok(subprocess.run([sys.executable,"check_links.py"]).returncode==0,"no broken internal links"))
base=__import__("json").load(open("config.json"))["base_url"]
all_txt="".join(open(p).read() for p in htmls)+open("dist/sitemap.xml").read()+open("dist/llms.txt").read()+open("dist/robots.txt").read()
r.append(ok("usethissi.vercel.app" not in all_txt and base in open("dist/robots.txt").read(),"all absolute URLs use base_url"))
sm=open("dist/sitemap.xml").read()
r.append(ok(len(set(re.findall(r"<lastmod>(.*?)</lastmod>",sm)))>1,"sitemap lastmod varies per page"))
r.append(ok(os.path.exists("dist/kit/builder-stack.pdf"),"kit PDF hosted at /kit/builder-stack.pdf"))
r.append(ok(all('id="newsletter"' in open(p).read() and 'class="kit' in open(p).read() for p in htmls if not p.endswith("404.html")),"every page has a kit CTA and signup"))
noidx=[p for p in htmls if 'content="noindex' in open(p).read()]
r.append(ok(all(("https://www.usethissi.com/"+p[5:].replace("index.html","")) not in sm for p in noidx),f"{len(noidx)} noindex pages excluded from sitemap"))

# ---- /quiz/ (Find your AI stack)
import csv,datetime as _dt
qp="dist/quiz/index.html"; qh=open(qp).read() if os.path.exists(qp) else ""
r.append(ok(bool(qh),"quiz page builds at /quiz/"))
r.append(ok("You don't need 40 AI tools." in qh.replace("&#x27;","'") and "No paid placements." in qh and "Answer 3 questions. Get the free pick, the paid pick worth it, and one to skip, prices checked this week." in qh,"quiz headline, sub-line and no-paid-placements note"))
r.append(ok("<title>Find your AI stack in 30 seconds" in qh and 'name="description"' in qh and '"WebApplication"' in qh and '"BreadcrumbList"' in qh,"quiz has SEO title, description and WebApplication schema"))
r.append(ok("<loc>https://www.usethissi.com/quiz/</loc>" in sm,"quiz is in the sitemap"))
IMPACT='<meta name="impact-site-verification" value="1c1f3cbc-5bfd-4425-80ce-c30b259ba149">'
r.append(ok(all(IMPACT in open(p).read() for p in htmls),f"impact-site-verification meta on all {len(htmls)} pages"))
txt=[os.path.join(a,f) for a,_,fs in os.walk("dist") for f in fs if f.endswith((".html",".xml",".txt",".css",".js"))]
r.append(ok(not any("vercel.app" in open(p,errors="ignore").read() for p in txt),"no vercel.app links anywhere in dist"))
r.append(ok(all('href="/quiz/"' in open(p).read() for p in htmls),"nav links to /quiz/ on every page"))
home=open("dist/index.html").read()
r.append(ok('href="/quiz/" data-umami-event="quiz-hero"' in home,"homepage hero CTA to the quiz"))
ucf=[p for p in htmls if re.search(r"dist/(use-cases|free)/[^/]+/index.html$",p)]
r.append(ok(ucf and all('class="quizbar"' in open(p).read() and 'href="/quiz/#j=' in open(p).read() for p in ucf),f"{len(ucf)} use-case and free pages carry a quiz CTA"))
m=re.search(r'<script type="application/json" id="qdata">(.*?)</script>',qh,re.S)
Q=json.loads(m.group(1).replace("<\\/","</")) if m else None
r.append(ok(Q is not None and qh.count('data-form="6601f72f-cbe4-41fa-8313-787075c593f7"')==1 and "subscribe-forms.beehiiv.com" in qh and "utm_source=quiz" in qh and "utm_campaign=quiz" in qh,"quiz embeds data, the quiz beehiiv form id and quiz UTM tagging"))
QFORM="6601f72f-cbe4-41fa-8313-787075c593f7"; SFORM="767b56cc-d716-4bab-a162-0baf03c34b2c"
_qp=[p for p in htmls if re.search(r"dist/quiz/index.html$",p)]
_other=[p for p in htmls if p not in _qp]
r.append(ok(len(_qp)==1 and QFORM in qh and not any(QFORM in open(p).read() for p in _other) and all(SFORM in open(p).read() for p in _other if 'id="newsletter"' in open(p).read()),f"quiz gate uses form {QFORM[:8]}; {len(_other)} other pages don't reference it and keep the site form"))
r.append(ok(os.path.isfile("dist/favicon.ico") and open("dist/favicon.ico","rb").read(4)==b"\x00\x00\x01\x00" and all('href="/favicon.ico"' in open(p).read() for p in htmls),"favicon.ico built and linked on every page"))
if Q:
    today=_dt.datetime.now(__import__("zoneinfo").ZoneInfo("America/Phoenix")).date()
    rows=[x for x in csv.reader(open("data.csv"))][1:]
    rows=rows[:rows.index([])] if [] in rows else rows
    def _slug(x): return re.sub(r'[^a-z0-9]+','-',x.lower()).strip('-')
    by={(_slug(x[2]),_slug(x[0])):x for x in rows}
    jobs=[j["slug"] for j in Q["jobs"]]
    bad=[]
    for i,t in enumerate(Q["tools"]):
        pass
    used=set()
    caps={"0":0,"20":20,"50":50,"any":None}
    viol=[]
    for ri,R in enumerate(Q["combos"]):
        for ji,J in enumerate(R):
            for bi,B in enumerate(J):
                for si,c in enumerate(B):
                    f,pd,sk=c[0],c[1],c[2]
                    ids=[x for x in (f,pd,sk) if x>=0]; used.update((x,jobs[ji]) for x in ids)
                    if f<0: viol.append(("no free pick",ri,ji,bi,si))
                    if sk>=0 and sk in (f,pd): viol.append(("skip repeats a pick",ri,ji,bi,si))
                    bk=Q["budgets"][bi]["k"]
                    if bk=="0" and pd>=0: viol.append(("paid pick on $0",ri,ji,bi,si))
                    if pd>=0 and caps[bk] is not None:
                        t=Q["tools"][pd]
                        if t["mo"] is None or t["cur"]!="USD" or t["mo"]>caps[bk]: viol.append(("paid pick over budget",t["tool"],bk))
    for i,job in used:
        t=Q["tools"][i]; row=by.get((t["slug"],job))
        if not row: bad.append((t["tool"],job,"not in data.csv for this job")); continue
        ch=row[8].strip()
        if not ch or (today-_dt.date.fromisoformat(ch)).days>30: bad.append((t["tool"],"stale or no check date"))
        if t["checked"]!=ch: bad.append((t["tool"],"checked date mismatch"))
        if re.search(r"unverified|contact sales|talk to sales|3rd-party",row[5],re.I) or not row[5].strip(): bad.append((t["tool"],"unverified price"))
        if row[4].strip().lower().startswith("unverified") or not row[4].strip(): bad.append((t["tool"],"unverified free tier"))
        if t["price"]!=re.sub(r"\s*\[[^\]]*\]","",row[5]).strip(): bad.append((t["tool"],"price text differs from data.csv"))
        for n in re.findall(r"[$\u20ac]\s?([\d,]+(?:\.\d+)?)",t["price"]):
            if n not in row[5]: bad.append((t["tool"],"price number not in data.csv",n))
    for b in (bad+viol)[:10]: print("  ",b)
    r.append(ok(not bad,f"quiz recommendations ({len(used)} tool/job pairs used) all come from tools checked <=30 days ago with verified price and free tier, prices verbatim from data.csv"))
    r.append(ok(not viol,f"{sum(len(B) for R in Q['combos'] for J in R for B in J)} quiz results: free pick always set, paid pick within budget, skip never repeats a pick"))
    r.append(ok(all(os.path.exists(f"dist/tools/{t['slug']}/index.html") for t in Q["tools"]) and all(os.path.exists(f"dist/use-cases/{j}/index.html") for j in jobs),"every quiz card links to a real tool page and use-case page"))
    stale=[x for x in rows if not x[8].strip() or (today-_dt.date.fromisoformat(x[8].strip())).days>30]
    r.append(ok(not any((_slug(x[2]),_slug(x[0])) in {(Q["tools"][i]["slug"],j) for i,j in used} for x in stale),f"none of the {len(stale)} stale/undated listings appear in quiz results"))

# ---- quiz price anchor (honest: derived only from data.csv verified monthly prices)
if Q is not None:
    import quiz as _qz
    _abad=[];_an=0;_ex=[]
    for R in Q["combos"]:
        for J in R:
            for B in J:
                for c in B:
                    p=Q["tools"][c[1]] if c[1]>=0 else None; k=Q["tools"][c[2]] if c[2]>=0 else None
                    pm=_qz.monthly(p["price"]) if p else None; km=_qz.monthly(k["price"]) if k else None
                    if not pm or pm[1]!="USD": exp=-1
                    elif km and km[1]=="USD": exp=round(pm[0]+km[0],2)
                    else: exp=round(pm[0],2)
                    if abs(c[6]-exp)>1e-9 or ((c[6]>=0)!=bool(c[7])): _abad.append(c)
                    _an+=c[6]>=0
    r.append(ok(not _abad and _an>0,f"{_an} quiz price anchors all equal paid+skip cheapest monthly price from data.csv; none shown when the paid price is missing ({len(_abad)} mismatches)"))
r.append(ok('id="qanchor"' in qh and "Testing these yourself:" in qh and "Unlock 2 more picks + the AI Stack Kit" in qh and not re.search(r"normally \$",qh,re.I),"quiz gate has the anchor line, short headline and no invented 'normally $' price"))
# ---- quiz soft gate
r.append(ok('id="qres"' in qh and re.search(r'<section id="qres"[^>]*\bhidden\b',qh) is not None and re.search(r'<div id="qfull" hidden>\s*</div>',qh) is not None,"quiz results start hidden; paid/skip cards are not in the page until unlock"))
gi,li,fi=qh.find('id="qgate"'),qh.find('id="qlocked"'),qh.find('id="qfree"')
r.append(ok(0<fi<gi<li,"email capture sits right after the free pick and before the locked paid/skip cards"))
r.append(ok("Unlock 2 more picks + the AI Stack Kit" in qh and "Free. Weekday 5-min brief. Unsubscribe anytime." in qh,"gate headline and trust line"))
r.append(ok('id="qnothanks"' in qh and "No thanks, just show me" in qh and "/quiz/skip/" in qh,"no-thanks link exists and is tracked as /quiz/skip/"))
r.append(ok(all(x in qh for x in ('"/quiz/start/"','"/quiz/done/"','"/quiz/signup/"','"layout", "slim"','"utm_source", "quiz"','"utm_campaign", "quiz-" + job','data-pub="d420e641-998f-43f4-a9ec-f398fd8e23c6"')),"quiz tracks start/done/signup and loads the beehiiv slim form tagged utm_source=quiz, utm_campaign=quiz-<job>"))
r.append(ok(IMPACT in qh and "vercel.app" not in qh,"quiz page keeps the Impact meta and has no vercel.app links"))
r.append(ok('<details class="qseo">' in qh and "Quick picks by job" in qh,"no-JS SEO section kept, collapsed"))
# ---- regressions added 2026-10-20 (live audit)
import html as _h
_today=_dt.datetime.now(__import__("zoneinfo").ZoneInfo("America/Phoenix")).date()
nw=open("dist/new/index.html").read()
_wk=re.search(r'<ol class="feed" id="week">(.*?)</ol>',nw,re.S)
_wd=re.findall(r'<time datetime="(\d{4}-\d\d-\d\d)"',_wk.group(1)) if _wk else []
r.append(ok(_wk is not None and all((_today-_dt.date.fromisoformat(x)).days<=6 for x in _wd) and ("Earlier releases" in nw)==bool(re.search(r'id="earlier"',nw)),f"/new/ 'last 7 days' list only holds releases from the last 7 days ({len(_wd)} items); older ones sit under Earlier releases"))
_bad=[p for p in htmls if re.search(r"AI tools to (AI coding assistant|research|voice and TTS|aI )|tools? to aI |AI tool for (Set up|Vibe-code|AI coding assistant)",open(p).read())]
r.append(ok(not _bad,f"use-case/free titles read naturally (no 'AI tools to AI coding assistant' / 'aI'); offenders: {_bad[:3]}"))
_prices=[re.sub(r"\s*\[[^\]]*\]","",x[5]).split(" [")[0].split(";")[0].strip() for x in rows] if Q else []
_bt=[_h.unescape(t) for p in htmls for t in re.findall(r'<span class="badge b-paid">([^<]*)</span>',open(p).read()) if t!="Paid only"]
_cut=[t for t in set(_bt) if not any(pp.startswith(t.rstrip("…")) and (len(pp)==len(t.rstrip("…")) or not pp[len(t.rstrip("…"))].isalnum()) for pp in _prices)]
r.append(ok(_bt and not _cut,f"{len(set(_bt))} price badges are cut at word boundaries, never mid-number (bad: {_cut[:3]})"))
r.append(ok(re.search(r"## Recent price changes \(last 14 days",llms) is not None and re.search(r"top pick [^\n]*Paid from [^\n]*\(checked 20\d\d-\d\d-\d\d\)",llms) is not None,"llms.txt lists recent price changes and each top pick's price with its check date"))
_vj=json.load(open("vercel.json"))
_dslugs={os.path.basename(os.path.dirname(p)) for p in htmls if "/tools/" in p and p.count("/")==3}
r.append(ok(all(x["destination"].startswith("/") and os.path.exists("dist"+x["destination"]+"index.html") for x in _vj.get("redirects",[])) and "relevance-ai" not in _dslugs,"removed tools redirect to a live page (relevance-ai -> agents use case)"))

sys.exit(0 if all(r) else 1)
