"""Apply Oct 21 2026 freshness rechecks to data.csv (official pages only) and log real value changes to ops/freshness/changes.csv.
last_checked is set to 2026-10-21 only for tools listed here (verified today from the vendor's own pricing page)."""
import csv,io
D="2026-10-21"; O="[official, Oct 21]"
U={
"Gumloop":dict(starting_paid_price=f"$37/mo Pro {O}",_src="gumloop.com/pricing (Pro from $37/mo, 14-day free trial)"),
"Suno":dict(starting_paid_price=f"$8/mo Pro billed yearly, $10 monthly {O}",_src="suno.com/pricing (Free 50 credits/day; Pro $8/mo yearly, saves $24/yr)"),
"Runway":dict(starting_paid_price=f"$12/mo Standard billed annually, $15 monthly {O}",_src="runwayml.com/pricing (Free 125 one-time credits)"),
"Descript":dict(starting_paid_price=f"$16/mo Hobbyist annual, $24 monthly {O}",_src="descript.com/pricing"),
"Jasper":dict(starting_paid_price=f"$59/mo Pro annual, $69 monthly {O}",_src="jasper.ai/pricing"),
"Copy.ai":dict(starting_paid_price=f"$24/mo billed yearly, $29 monthly {O}",_src="copy.ai/prices (free plan not shown; 'Try for free' only, free_tier stays unverified)"),
"Scenario":dict(starting_paid_price=f"$15/mo Starter (monthly; annual saves 33%) {O}",_src="scenario.com/pricing (50 free daily credits)"),
"Rosebud AI":dict(free_tier="Yes (8,000 credits; refill weekly in eligible regions)",starting_paid_price=f"$15/mo Indie Dev {O}",_src="rosebud.ai/pricing FAQ: Free plan 8,000 credits, weekly refill in eligible regions"),
"AIVA":dict(starting_paid_price=f"€11/mo Standard billed annually, + VAT {O}",_src="aiva.ai/pricing"),
"Windsurf (now Devin Desktop)":dict(starting_paid_price=f"$20/mo Pro {O}",_src="devin.ai/pricing (Free $0; Pro $20; Max $200)"),
"ngram":dict(starting_paid_price=f"$23.20/mo Basic billed annually, $29 monthly {O}",_src="ngram.com/pricing"),
"Cartesia":dict(starting_paid_price=f"$5/mo Pro {O}",_src="cartesia.ai/pricing (Free 20K credits/mo)"),
"Synthesia":dict(starting_paid_price=f"$18/mo Starter billed yearly, $29 monthly {O}",_src="synthesia.io/pricing (Basic $0: 10 min video/mo, watermark)"),
"Claude":dict(starting_paid_price=f"$17/mo Pro annual, $20 monthly {O}",_src="claude.com/pricing"),
"Claude Code":dict(starting_paid_price=f"$17/mo annual, $20 monthly via Claude Pro {O}",_src="claude.com/pricing (Claude Code included in Pro)"),
"Gemini (Deep Research)":dict(starting_paid_price=f"$4.99/mo Google AI Plus; $19.99/mo AI Pro {O}",_src="gemini.google/subscriptions"),
}
REMOVE={}
NEW=[
["AI coding assistant","Alt","Beacon","Open-source memory shared across Claude Code, Cursor, Codex and 20+ agent harnesses, so one agent's fixes carry over to the next","Yes (open source, MIT; Beacon Cloud free plan)",f"Free OSS; Beacon Cloud Pro $20/mo billed annually {O}","https://beacon.sh","unverified",D],
["Generate music and SFX","Alt","Mirelo","Video-to-sound: adds synced SFX, foley and ambience to a clip while keeping the dialogue (SFX 2.0)","Yes (5,000 credits/mo, about 8 min of SFX 2.0)",f"€20/mo Creator (about 40 min of SFX 2.0) {O}","https://mirelo.ai","unverified",D],
]
REL=[
["2026-10-20","Perplexity Computer runs fully local on Mac (Pro, Max and Enterprise; Apple silicon with 36GB+ unified memory; Qwen 3.6 or PPLX Pro local models)","https://www.perplexity.ai/hub/blog/perplexity-computer-now-runs-fully-local-on-mac"],
["2026-10-20","Gemini adds a small-business hub: brand-style visuals with Nano Banana 2.1, finance insights from messy spreadsheets, connectors to Business Profile, Ads, Shopify, Canva, Xero and more","https://blog.google/innovation-and-ai/products/gemini-app/new-tools-small-business-owners/"],
["2026-10-20","Beacon (Asymptote Labs): open-source memory and telemetry layer that carries lessons across Claude Code, Cursor, Codex and 20+ agent harnesses","https://asymptotelabs.ai/blog/asymptote-labs-raises-5-5m-seed-round"],
["2026-10-20","Vercel WebSocket support in Functions is generally available (same limits and pricing as other Function invocations)","https://vercel.com/changelog/websocket-support-is-now-generally-available"],
["2026-10-20","Amazon Polly Generative engine upgraded: more natural speech, 14 new voices, Hindi and Finnish","https://aws.amazon.com/about-aws/whats-new/2026/10/polly-generative/"],
["2026-10-21","GemDB Code: free VS Code extension for an ACID object database where the code is the schema (no migration scripts)","https://www.businesswire.com/news/home/20261021228398/en/GemDB-Makes-Code-the-Schema-Eliminating-Database-Migration-Bottlenecks-to-Accelerate-AI-Driven-Development"],
]
txt=open("data.csv").read(); tpart,rpart=txt.split("\n\n",1)
rows=list(csv.reader(io.StringIO(tpart))); hdr=rows[0]; body=rows[1:]
ix={h:i for i,h in enumerate(hdr)}
log=[]; seen=set(); out=[]
for r in body:
    t=r[ix["tool"]]
    if t in REMOVE: log.append([D,t,"removed",r[ix["starting_paid_price"]],"(removed from directory)",REMOVE[t]]); continue
    if t in U:
        seen.add(t); u=U[t]; src=u.get("_src","official page")
        for f,v in u.items():
            if f.startswith("_"): continue
            old=r[ix[f]]
            strip=lambda s: s.split(" [")[0].strip()
            if strip(old)!=strip(v) and f in ("free_tier","starting_paid_price"): log.append([D,t,f,old,v,src])
            r[ix[f]]=v
        if r[ix["last_checked"]]!=D: log.append([D,t,"last_checked",r[ix["last_checked"]],D,src])
        r[ix["last_checked"]]=D
    out.append(r)
missing=set(U)-seen; assert not missing, missing
have_tools={r[ix["tool"]] for r in out}
for n in NEW:
    if n[2] in have_tools: continue
    out.append(n); log.append([D,n[2],"added","",n[5],{"Beacon":"beacon.sh/pricing + github.com/Asymptote-Labs/agent-beacon (MIT)","Mirelo":"mirelo.ai/pricing (Free 0 EUR 5,000 credits; Creator 20 EUR)"}[n[2]]])
rr=list(csv.reader(io.StringIO(rpart.strip())))
have={(x[0],x[1]) for x in rr}
for x in REL:
    if (x[0],x[1]) not in have: rr.append(x)
s=io.StringIO(); w=csv.writer(s,lineterminator="\n"); w.writerow(hdr); w.writerows(out); s.write("\n"); w.writerows(rr)
open("data.csv","w").write(s.getvalue())
with open("ops/freshness/changes.csv","a",newline="") as f: csv.writer(f,lineterminator="\n").writerows(log)
print(len(U),"verified;",len(log),"log rows")
for l in log:
    if l[2]!="last_checked": print(" ",l[1],l[2],"|",l[3],"->",l[4])
