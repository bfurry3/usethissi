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
sys.exit(0 if all(r) else 1)
