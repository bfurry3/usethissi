#!/usr/bin/env python3
"""Build The Builder's 5-Minute AI Stack Kit (HTML + PDF) from data.csv only.
Run from repo root: python3 newsletter/kit.py  -> newsletter/builder-stack.{html,pdf} and static/kit/builder-stack.pdf"""
import csv,re,html,datetime as dt,subprocess,shutil,os,sys
E=html.escape
slug=lambda s:re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
TODAY=dt.date(2026,10,18) if len(sys.argv)<2 else dt.date.fromisoformat(sys.argv[1])
EDITION=TODAY.strftime("%B %Y")
SITE="https://www.usethissi.com"; SUB=SITE+"/#newsletter"
rows=[r for r in csv.DictReader(open('data.csv')) if r.get('role') in('Top pick','Alt')]
for r in rows: r['last_checked']=(r.get('last_checked') or '').strip()
def fresh(r): return bool(r['last_checked']) and (TODAY-dt.date.fromisoformat(r['last_checked'])).days<=30
def bad_price(p): return (not p) or bool(re.search(r'unverified|contact sales|talk to sales|3rd-party',p,re.I))
def price(r):
    p=re.sub(r'\s*\[[^\]]*\]','',r['starting_paid_price']).strip()
    p=re.sub(r'\s*\(\$1 first month[^)]*\)','',p)
    return p
def verified_price(r): return fresh(r) and not bad_price(r['starting_paid_price'])
def free_ok(r): return fresh(r) and r['free_tier'].lower().startswith('yes')
def free_txt(r):
    f=r['free_tier']
    return 'Not verified' if 'unverified' in f.lower() else f
def d(r):
    c=r['last_checked']; return dt.date.fromisoformat(c).strftime('%b %-d, %Y') if c else 'not checked'
TIPS={"Lovable":"Write a one-paragraph spec (pages, users, data) before your first prompt, and connect GitHub early so you own the code.",
"Cursor":"Add a project rules file describing your stack and conventions; it keeps every agent edit on-style.",
"n8n":"Start from a community template, then swap in your credentials. Self-host with Docker if you want unlimited runs.",
"Make":"Build the scenario with 'Run once' and sample data first, then turn on scheduling. Watch your credit count.",
"Scenario":"Train a custom model on 10-20 of your own reference images so every asset stays in one consistent style.",
"Suno":"Put genre, tempo and mood in the style box and keep lyrics separate. Free tier is non-commercial, so upgrade before you ship.",
"Runway":"Lock a strong still image first, then animate it; image-to-video gives far more control than text alone.",
"Claude":"Create a Project with your style guide and examples attached so every draft starts with your context.",
"Perplexity":"Use Spaces to save sources and instructions per topic, and always click through to verify key citations.",
"ElevenLabs":"Clone your voice from a clean 1-2 minute recording in a quiet room; audio quality matters more than length."}
uses={}
for r in rows: uses.setdefault(r['use_case'],[]).append(r)
jobs=[]
for u,L in uses.items():
    t=next(r for r in L if r['role']=='Top pick')
    bench=[r for r in L if r is not t and verified_price(r)][:2]
    jobs.append((u,t,bench))
by={r['tool']:r for r in rows}
# ---- starter stacks: (tool, monthly $ we count, label). Each $ must literally appear in that tool's verified price.
STACKS=[("Solo Founder","Ship a product and run the busywork",[("Lovable",25,"build the app"),("Claude",20,"write, plan and code help (Pro, monthly)"),("Make",0,"automations on the Free plan"),("Perplexity",0,"research on the Free plan")]),
("Marketer","Write, design and publish every week",[("Claude",20,"long-form drafts (Pro, monthly)"),("Gamma",9,"decks and one-pagers (Plus, billed annually)"),("Descript",16,"edit video by text (Hobbyist, billed annually)"),("CapCut",0,"short-form edits on the Free plan")]),
("Developer","Code faster with agents you control",[("Claude Code",20,"terminal agent via Claude Pro (monthly)"),("GitHub Copilot",10,"in-editor completions (Pro)"),("n8n",0,"self-hosted workflows"),("Aider",0,"open-source pair programmer, bring your own key")]),
("Creator","Video, voice and music for content",[("Runway",15,"generative video (Standard, monthly)"),("ElevenLabs",6,"voiceover (Starter)"),("Suno",10,"music with commercial rights (Pro, monthly)"),("CapCut",0,"final cut on the Free plan")])]
for name,_,items in STACKS:
    for tool,cost,_ in items:
        r=by[tool]; assert fresh(r),tool
        if cost: assert verified_price(r) and f"${cost}" in price(r), (tool,price(r))
        else: assert free_ok(r) or 'free' in price(r).lower(), tool
    assert sum(c for _,c,_ in items)<50, name
# ---- $0 stack: best verified free option per job
zero=[]
for u,t,_ in jobs:
    L=uses[u]; pick=t if free_ok(t) else next((r for r in L if free_ok(r)),None)
    if pick: zero.append((u,pick,t))
# ---- skip list
def why(r):
    p=r['starting_paid_price'].lower()
    if 'contact sales' in p or 'talk to sales' in p: return "Sales-only pricing; no self-serve plan we can verify."
    if re.search(r'beta|early access|waitlist|preview|demo',p+r['free_tier'].lower()+r['reason'].lower()): return "Beta or early access; pricing isn't final yet."
    if not r['last_checked']: return "We couldn't confirm a current price on the official site."
    if 'unverified' in p: return "No public price we could verify."
    return ""
skip=[(r,why(r)) for r in rows if why(r) and not free_ok(r)]
skip=[s for s in skip if s[0]['role']!='Top pick'][:12]
n_checked=sum(fresh(r) for r in rows); n_free=sum(free_ok(r) for r in rows)
dates=sorted(r['last_checked'] for r in rows if fresh(r)); span=f"{dt.date.fromisoformat(dates[0]).strftime('%b %-d')} to {dt.date.fromisoformat(dates[-1]).strftime('%b %-d, %Y')}"
FT=f'<div class="ft"><span>The Builder\'s 5-Minute AI Stack Kit · {EDITION} edition</span><span>www.usethissi.com</span></div>'
def pg(title,sub,body,cls=""): return f'<section class="pg {cls}"><div class="bar"></div><div class="sh"><h2>{title}</h2><span>{sub}</span></div>{body}{FT}</section>'
def jobcard(i,u,t,bench):
    b="".join(f'<tr><td>{E(r["tool"])}</td><td>{E(r["reason"])}</td><td>{E(price(r))}</td><td>{d(r)}</td></tr>' for r in bench)
    tp=price(t) if verified_price(t) else "Check vendor site"
    return f'''<div class="card"><div class="ch"><span class="n">{i:02d}</span><div><div class="uc">{E(u)}</div><h3>{E(t["tool"])} <span class="tp">TOP PICK</span></h3></div></div>
<p>{E(t["reason"])}.</p><div class="meta"><div><span>Starts at</span>{E(tp)}</div><div><span>Free tier</span>{E(free_txt(t))}</div><div class="sm"><span>Checked</span>{d(t)}</div></div>
{f'<table class="bench"><tr><th>The bench</th><th>Why</th><th>Starts at</th><th>Checked</th></tr>{b}</table>' if b else ''}
<a href="{SITE}/use-cases/{slug(u)}/">www.usethissi.com/use-cases/{slug(u)}/</a></div>'''
CH=[];i=0
for n in [3,3,2,2]:
    CH.append(list(range(i,min(i+n,len(jobs))))); i+=n
picks_pages="".join(pg("Best tool for each job",f"Jobs {c[0]+1}-{c[-1]+1} of {len(jobs)}","".join(jobcard(j+1,*jobs[j]) for j in c)) for c in CH if c)
zero_rows="".join(f'<tr><td><b>{E(u)}</b></td><td>{E(p["tool"])}{"" if p is t else f"<br><small>(top pick {E(t["tool"])} is paid)</small>"}</td><td>{E(free_txt(p))}</td><td>{d(p)}</td></tr>' for u,p,t in zero)
zero_pg=pg("The $0 Stack","Every job on free tiers only",f'<p class="lead">You can do all {len(zero)} jobs without paying anything. These are the best free options we could verify, with the real limits. Free tiers are for trying and light use; check the limits before you build a business on one.</p><table class="t"><tr><th>Job</th><th>Use this free</th><th>Free tier, as listed</th><th>Checked</th></tr>{zero_rows}</table><p class="note">{n_free} of {len(rows)} tools in our directory have a free tier we verified in the last 30 days.</p>')
def stackcard(name,goal,items):
    tot=sum(c for _,c,_ in items)
    li="".join(f'<tr><td><b>{E(t)}</b><br><small>{E(l)}</small></td><td class="r">{"$"+str(c) if c else "Free"}</td><td class="r"><small>{d(by[t])}</small></td></tr>' for t,c,l in items)
    return f'<div class="stack"><div class="sth"><h3>{E(name)}</h3><div class="tot">${tot}<small>/mo</small></div></div><p class="goal">{E(goal)}</p><table class="st">{li}</table></div>'
stack_pg=pg("4 starter stacks under $50/mo","Pick your role, not a tool",'<p class="lead">Each stack covers a whole role for under $50 a month. Totals use the plan and billing shown next to each price, so check whether a plan is billed monthly or annually before you buy.</p><div class="stacks">'+"".join(stackcard(*s) for s in STACKS)+'</div>')
qs="".join(f'<div class="q"><b>{E(t["tool"])}</b> <span class="uc">· {E(u)}</span><p>{E(TIPS[t["tool"]])}</p></div>' for u,t,_ in jobs if t["tool"] in TIPS)
quick_pg=pg("First-hour quickstarts","Get a real result in your first session",f'<p class="lead">One setup tip per top pick. Do this first and you\'ll get something useful before the free trial runs out.</p><div class="qs">{qs}</div>')
skip_rows="".join(f'<tr><td><b>{E(r["tool"])}</b><br><small>{E(r["use_case"])}</small></td><td>{E(w)}</td><td>{E(next(x for x in uses[r["use_case"]] if x["role"]=="Top pick")["tool"])}</td></tr>' for r,w in skip)
skip_pg=pg("The Skip List","Tools we'd skip right now, and why",f'<p class="lead">These aren\'t bad tools. They\'re ones we can\'t recommend to a busy builder today, mostly because we couldn\'t confirm what they cost. When that changes, they come off the list and you\'ll hear about it in the brief.</p><table class="t"><tr><th>Skip for now</th><th>Why</th><th>Use instead</th></tr>{skip_rows}</table>')
H=f'''<!doctype html><html><head><meta charset="utf-8"><title>The Builder's 5-Minute AI Stack Kit ({EDITION})</title><style>
@page{{size:Letter;margin:0}}*{{box-sizing:border-box}}body{{margin:0;font-family:Inter,"Helvetica Neue",Arial,sans-serif;color:#1a1a2e;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.pg{{width:8.5in;height:11in;padding:.55in .65in .7in;position:relative;page-break-after:always;overflow:hidden;background:#fafaff}}
.cover{{background:#0B0B14;color:#fff;display:flex;flex-direction:column;justify-content:center;padding:.9in}}
.cover:before{{content:"";position:absolute;width:7in;height:7in;right:-2.5in;top:-2in;background:radial-gradient(circle,#7C3AED66,transparent 65%)}}
.cover:after{{content:"";position:absolute;width:6in;height:6in;left:-2in;bottom:-2in;background:radial-gradient(circle,#22D3EE44,transparent 65%)}}
.cover>*{{position:relative;z-index:1}}.logo{{font-size:26pt;font-weight:900;background:linear-gradient(90deg,#a78bfa,#22D3EE);-webkit-background-clip:text;color:transparent}}
.cover h1{{font-size:46pt;line-height:1.02;margin:.25in 0 .12in;font-weight:900}}.cover h1 em{{font-style:normal;background:linear-gradient(90deg,#a78bfa,#22D3EE);-webkit-background-clip:text;color:transparent}}
.cyan{{width:2in;height:6px;background:#22D3EE;box-shadow:0 0 18px #22D3EE;border-radius:3px;margin:.2in 0}}
.cover p{{font-size:15pt;color:#c7c7e0;max-width:5.8in;margin:.06in 0}}.cover .ed{{font-size:11pt;color:#8b8ba8}}.cover .url{{color:#22D3EE;position:absolute;bottom:.7in;font-size:12pt}}
.inside{{display:grid;grid-template-columns:1fr 1fr;gap:8px 18px;margin-top:.3in;max-width:6.2in}}.inside div{{font-size:10.5pt;color:#e8e8f5;border-left:3px solid #7C3AED;padding:2px 10px}}
.bar{{position:absolute;top:0;left:0;right:0;height:10px;background:linear-gradient(90deg,#7C3AED,#22D3EE)}}
h2{{margin:0;font-size:21pt;color:#0B0B14}}.sh{{display:flex;align-items:baseline;gap:12px;border-bottom:2px solid #e4e0f7;padding-bottom:7px;margin-bottom:12px}}.sh span{{color:#7C3AED;font-weight:600;font-size:10.5pt}}
.lead{{font-size:10.5pt;line-height:1.5;margin:0 0 12px;color:#33334d}}.note{{font-size:9pt;color:#6b6b85}}
.card{{background:#fff;border:1px solid #e6e3f3;border-left:5px solid #7C3AED;border-radius:10px;padding:10px 14px;margin-bottom:10px;font-size:9.6pt;line-height:1.4}}
.ch{{display:flex;gap:12px;align-items:center}}.n{{font-weight:900;font-size:19pt;background:linear-gradient(135deg,#7C3AED,#22D3EE);-webkit-background-clip:text;color:transparent}}
h3{{margin:0;font-size:13.5pt}}.uc{{color:#6b6b85;font-size:8.5pt;text-transform:uppercase;letter-spacing:.04em;font-weight:600}}.tp{{font-size:7pt;background:#0B0B14;color:#22D3EE;padding:2px 7px;border-radius:9px;vertical-align:middle;letter-spacing:.05em}}
.card p{{margin:5px 0}}.meta{{display:flex;gap:8px}}.meta div{{flex:2;background:#f3f0ff;border-radius:6px;padding:5px 9px}}.meta div.sm{{flex:1}}.meta span{{display:block;font-size:7pt;text-transform:uppercase;color:#7C3AED;font-weight:700;letter-spacing:.05em}}
.card a{{color:#0e7490;font-size:8.5pt;text-decoration:none}}
table{{border-collapse:collapse;width:100%}}.bench{{margin:6px 0 4px;font-size:8.4pt}}.bench th{{text-align:left;font-size:7pt;text-transform:uppercase;color:#7C3AED;letter-spacing:.05em;padding:2px 6px}}.bench td{{padding:3px 6px;border-top:1px solid #eee;vertical-align:top}}.bench td:first-child{{font-weight:700;white-space:nowrap}}
.t{{font-size:9pt;background:#fff;border:1px solid #e6e3f3;border-radius:10px}}.t th{{text-align:left;background:#0B0B14;color:#22D3EE;font-size:7.5pt;text-transform:uppercase;letter-spacing:.05em;padding:7px 8px}}.t td{{padding:6px 8px;border-top:1px solid #eee;vertical-align:top;line-height:1.35}}.t small{{color:#6b6b85}}
.stacks{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}.stack{{background:#fff;border:1px solid #e6e3f3;border-top:5px solid #22D3EE;border-radius:10px;padding:10px 12px}}.sth{{display:flex;justify-content:space-between;align-items:baseline}}.tot{{font-weight:900;font-size:20pt;color:#7C3AED}}.tot small{{font-size:9pt;color:#6b6b85}}.goal{{margin:2px 0 6px;color:#6b6b85;font-size:9pt}}
.st{{font-size:9pt}}.st td{{padding:5px 2px;border-top:1px solid #eee;vertical-align:top}}.st small{{color:#6b6b85}}.r{{text-align:right;white-space:nowrap}}
.qs{{display:grid;grid-template-columns:1fr 1fr;gap:10px}}.q{{background:#ecfeff;border-radius:8px;padding:9px 12px;font-size:9.5pt;line-height:1.4}}.q p{{margin:4px 0 0}}.q .uc{{text-transform:none;letter-spacing:0}}
.box{{background:#0B0B14;color:#fff;border-radius:12px;padding:14px 18px;margin:12px 0}}.box h3{{color:#22D3EE;margin-bottom:6px}}.box p{{margin:4px 0;font-size:10pt;color:#d6d6ea;line-height:1.45}}
ol.steps{{padding-left:18px;font-size:10.5pt;line-height:1.5}}ol.steps li{{margin-bottom:6px}}ul.rules{{font-size:10pt;line-height:1.5;padding-left:18px}}
.ft{{position:absolute;bottom:.3in;left:.65in;right:.65in;font-size:7.8pt;color:#9a9ab0;border-top:1px solid #e4e0f7;padding-top:6px;display:flex;justify-content:space-between}}
.end{{background:#0B0B14;color:#fff}}.end h2{{color:#fff}}.end .sh{{border-color:#26264a}}.end p,.end li{{color:#d6d6ea;font-size:10.5pt;line-height:1.5}}.end a{{color:#22D3EE}}.end .ft{{border-color:#26264a}}
.btn{{display:inline-block;background:linear-gradient(90deg,#7C3AED,#22D3EE);color:#0B0B14;font-weight:800;padding:10px 18px;border-radius:10px;text-decoration:none;margin-top:8px}}
</style></head><body>
<section class="pg cover"><div class="logo">UseThisSI</div><h1>The Builder's<br><em>5-Minute AI Stack Kit</em></h1><div class="cyan"></div>
<p>Pick the right AI tool for any job in 5 minutes. Real prices, checked every week. Free.</p>
<p class="ed">{EDITION} edition · {len(jobs)} jobs · {len(rows)} tools · prices checked {span}</p>
<div class="inside"><div>Best tool for each job, with price and free tier</div><div>The $0 Stack: every job on free tiers</div><div>4 starter stacks under $50/mo</div><div>First-hour quickstarts</div><div>The Skip List</div><div>Our 24-hour wrong-price guarantee</div></div>
<div class="url">www.usethissi.com</div></section>
{pg("Start here","How to use this kit in 5 minutes",f"""<ol class="steps"><li><b>Find your job</b> on the next pages (building an app, writing, research, video, voice and more). Use the <b>Top Pick</b> unless you have a reason not to.</li><li><b>Check the free tier</b> and the date we last checked the price. If you'd rather not pay yet, jump to <b>The $0 Stack</b>.</li><li><b>Got a budget and a role, not a job list?</b> Grab one of the <b>4 starter stacks</b>, each under $50 a month.</li><li><b>Do the first-hour quickstart</b> for your pick so you get a real result in your first session.</li></ol>
<h3>How we pick and check</h3><ul class="rules"><li>One Top Pick per job, chosen for fit for busy builders, not for who pays us.</li><li>Every price comes from the vendor's own pricing page, with the date we checked it. If we couldn't verify a price, we say so instead of guessing.</li><li>{n_checked} of {len(rows)} tools were checked in the last 30 days. Prices change, so confirm on the vendor's site before you buy.</li><li>Some links on our site are affiliate links. They're always labeled and never change our picks.</li></ul>
<div class="box"><h3>Our guarantee: wrong price, fixed in 24 hours</h3><p>Found a price or free tier in this kit that's wrong? Reply to any UseThisSI email or write to info@usethissi.com. We'll fix it on the site within 24 hours and thank you in the brief.</p><p>Every weekday brief reads in 5 minutes or less. One-click unsubscribe, any time.</p></div>""")}
{picks_pages}{zero_pg}{stack_pg}{quick_pg}{skip_pg}
<section class="pg end"><div class="bar"></div><div class="sh"><h2>Stay current in 5 minutes a day</h2></div>
<p>Prices and free tiers change every week. This kit is the {EDITION} edition, and subscribers get each new edition automatically.</p>
<ul><li><b>The weekday brief:</b> what launched, what changed, and what's worth trying today. Five minutes, Monday to Friday.</li><li><b>Price-change alerts:</b> when a tool in this kit changes its price or free tier, you hear it in the brief first.</li><li><b>Full directory:</b> every job, every tool, with alternatives and last-checked dates at <a href="{SITE}/">www.usethissi.com</a>.</li></ul>
<p>Know a tool that belongs here, or spot a wrong price? Reply to any brief or email <a href="mailto:info@usethissi.com">info@usethissi.com</a>. We fix wrong prices within 24 hours.</p>
<a class="btn" href="{SUB}">Share the free kit: www.usethissi.com</a>
<div class="ft"><span>The Builder's 5-Minute AI Stack Kit · {EDITION} edition</span><span>www.usethissi.com · @UseThisSI</span></div></section>
</body></html>'''
assert 'vercel.app' not in H and '10 referrals' not in H
open('newsletter/builder-stack.html','w').write(H)
subprocess.run(["google-chrome","--headless=new","--no-sandbox","--disable-gpu","--no-pdf-header-footer","--print-to-pdf=newsletter/builder-stack.pdf","file://"+os.path.abspath("newsletter/builder-stack.html")],check=True,capture_output=True,timeout=120)
os.makedirs("static/kit",exist_ok=True); shutil.copy("newsletter/builder-stack.pdf","static/kit/builder-stack.pdf")
print("kit built:",len(jobs),"jobs,",len(zero),"zero-stack rows,",len(skip),"skips,",n_checked,"fresh tools")
