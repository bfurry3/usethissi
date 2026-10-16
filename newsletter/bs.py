import csv,re,html
E=html.escape
slug=lambda s:re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
rows=[r for r in csv.DictReader(open('../data.csv')) if r['role'] in('Top pick','Alt')]
alts=["Bolt.new","v0 by Vercel","Claude Code","GitHub Copilot","Zapier","CrewAI","Midjourney","Ideogram","ElevenLabs Music and SFX","Descript","HeyGen","ChatGPT","Gamma","NotebookLM","Cartesia"]
tips={"Lovable":"Write a one-paragraph spec (pages, users, data) before your first prompt, and connect GitHub early so you own the code.",
"Cursor":"Add a project rules file describing your stack and conventions; it keeps every agent edit on-style.",
"n8n":"Start from a community template, then swap in your credentials. Self-host with Docker if you want unlimited runs.",
"Make":"Build the scenario with 'Run once' and sample data first, then turn on scheduling. Watch your operations count.",
"Scenario":"Train a custom model on 10-20 of your own reference images so every asset stays in one consistent style.",
"Suno":"Put genre, tempo and mood in the style box and keep lyrics separate. Free tier is non-commercial, so upgrade before you ship.",
"Runway":"Lock a strong still image first, then animate it; image-to-video gives far more control than text alone.",
"Claude":"Create a Project with your style guide and examples attached so every draft starts with your context.",
"Perplexity":"Use Spaces to save sources and instructions per topic, and always click through to verify key citations.",
"ElevenLabs":"Clone your voice from a clean 1-2 minute recording in a quiet room; audio quality matters more than length.",
"Bolt.new":"Ask for the scaffold first, then iterate one feature per prompt to save tokens and avoid regressions.",
"v0 by Vercel":"Paste a screenshot of a UI you like as a reference, then deploy straight to Vercel when it looks right.",
"Claude Code":"Run /init in your repo to generate a CLAUDE.md, then keep it updated with build and test commands.",
"GitHub Copilot":"Turn on Copilot in your editor and use chat with #file references so answers use the right context.",
"Zapier":"Begin with a two-step Zap, test each step with real data, then add filters to avoid wasting tasks.",
"CrewAI":"Define each agent's role, goal and tools narrowly; small focused crews beat one do-everything agent.",
"Midjourney":"Use --sref with an image you like to keep a consistent style across a whole asset set.",
"Ideogram":"Reach for it when you need readable text inside images: logos, posters and thumbnails.",
"ElevenLabs Music and SFX":"Describe sounds concretely (material, distance, length), e.g. 'short wooden door creak, close mic'.",
"Descript":"Edit video by editing the transcript, then run Studio Sound to clean up audio in one click.",
"HeyGen":"Record a 2-minute avatar video with steady lighting and eye contact for the most natural results.",
"ChatGPT":"Set Custom Instructions with who you are and how you like answers, so you stop repeating context.",
"Gamma":"Paste an outline or doc and let Gamma build the deck, then apply your brand theme once.",
"NotebookLM":"Upload your own PDFs and docs as sources; answers stay grounded and cite where they came from.",
"Cartesia":"Test the low-latency API in the playground first if you are building a real-time voice agent."}
top=[r for r in rows if r['role']=='Top pick']; by={r['tool']:r for r in rows}
picks=top+[by[a] for a in alts]
def price(p): return 'Check vendor site' if (not p or 'unverified' in p.lower()) else re.sub(r'\s*\[[^\]]*\]','',p)
def free(f): return 'Check vendor site' if 'unverified' in f.lower() else f
def card(i,r):
  s=slug(r['tool']); top_=r['role']=='Top pick'
  return f'''<div class="card"><div class="ch"><span class="n">{i:02d}</span><div><h3>{E(r['tool'])}{' <span class="tp">TOP PICK</span>' if top_ else ''}</h3><div class="uc">{E(r['use_case'])}</div></div></div>
<p><b>Best for:</b> {E(r['reason'])}</p>
<div class="meta"><div><span>Price</span>{E(price(r['starting_paid_price']))}</div><div><span>Free tier</span>{E(free(r['free_tier']))}</div></div>
<p class="tip"><b>Setup tip:</b> {E(tips[r['tool']])}</p>
<a href="https://usethissi.vercel.app/tools/{s}/">usethissi.vercel.app/tools/{s}/</a></div>'''
def chunk(l,n): return [l[i:i+n] for i in range(0,len(l),n)]
sec=[("The Top Picks","Our #1 tool for each job",top,1),("The Bench","Strong alternatives worth knowing",picks[10:],11)]
pages=""
for t,sub,L,st in sec:
  for j,c in enumerate(chunk(L,3)):
    pages+=f'<section class="pg"><div class="bar"></div><div class="sh"><h2>{t}</h2><span>{sub}</span></div>'+"".join(card(st+j*3+k,r) for k,r in enumerate(c))+'<div class="ft">The UseThisSI Builder Stack · usethissi.vercel.app</div></section>'
idx="".join(f'<tr><td>{i+1:02d}</td><td>{E(r["tool"])}</td><td>{E(r["use_case"])}</td><td>{E(price(r["starting_paid_price"]))}</td></tr>' for i,r in enumerate(picks))
H=f'''<html><head><meta charset="utf-8"><style>
@page{{size:Letter;margin:0}}*{{box-sizing:border-box}}body{{margin:0;font-family:Inter,"Helvetica Neue",Arial,sans-serif;color:#1a1a2e}}
.pg{{width:8.5in;height:11in;padding:.6in .7in;position:relative;page-break-after:always;overflow:hidden;background:#fafaff}}
.cover{{background:#0B0B14;color:#fff;display:flex;flex-direction:column;justify-content:center;padding:1in}}
.cover:before{{content:"";position:absolute;width:7in;height:7in;right:-2.5in;top:-2in;background:radial-gradient(circle,#7C3AED66,transparent 65%)}}
.cover:after{{content:"";position:absolute;width:6in;height:6in;left:-2in;bottom:-2in;background:radial-gradient(circle,#22D3EE44,transparent 65%)}}
.logo{{font-size:40pt;font-weight:900;background:linear-gradient(90deg,#7C3AED,#22D3EE);-webkit-background-clip:text;color:transparent}}
.cover h1{{font-size:50pt;line-height:1.02;margin:.3in 0 .15in;font-weight:900}}.cover h1 em{{font-style:normal;background:linear-gradient(90deg,#a78bfa,#22D3EE);-webkit-background-clip:text;color:transparent}}
.cyan{{width:2in;height:6px;background:#22D3EE;box-shadow:0 0 18px #22D3EE;border-radius:3px;margin:.2in 0}}
.cover p{{font-size:15pt;color:#c7c7e0;max-width:5.5in}}.cover .url{{color:#22D3EE;position:absolute;bottom:.8in;font-size:12pt}}
.bar{{position:absolute;top:0;left:0;right:0;height:10px;background:linear-gradient(90deg,#7C3AED,#22D3EE)}}
h2{{margin:0;font-size:22pt;color:#0B0B14}}.sh{{display:flex;align-items:baseline;gap:12px;border-bottom:2px solid #e4e0f7;padding-bottom:8px;margin-bottom:16px}}.sh span{{color:#7C3AED;font-weight:600}}
.card{{background:#fff;border:1px solid #e6e3f3;border-left:5px solid #7C3AED;border-radius:10px;padding:14px 18px;margin-bottom:14px;font-size:10.5pt;line-height:1.45}}
.ch{{display:flex;gap:14px;align-items:center}}.n{{font-weight:900;font-size:20pt;background:linear-gradient(135deg,#7C3AED,#22D3EE);-webkit-background-clip:text;color:transparent}}
h3{{margin:0;font-size:15pt}}.uc{{color:#6b6b85;font-size:9.5pt}}.tp{{font-size:7.5pt;background:#0B0B14;color:#22D3EE;padding:2px 7px;border-radius:9px;vertical-align:middle}}
.card p{{margin:8px 0}}.meta{{display:flex;gap:10px}}.meta div{{flex:1;background:#f3f0ff;border-radius:6px;padding:6px 10px}}.meta span{{display:block;font-size:7.5pt;text-transform:uppercase;color:#7C3AED;font-weight:700;letter-spacing:.05em}}
.tip{{background:#ecfeff;border-radius:6px;padding:6px 10px}}.card a{{color:#0e7490;font-size:9pt;text-decoration:none}}
.ft{{position:absolute;bottom:.35in;left:.7in;right:.7in;font-size:8pt;color:#9a9ab0;border-top:1px solid #e4e0f7;padding-top:6px}}
.intro p,.intro li{{font-size:10.5pt;line-height:1.45}}table{{width:100%;border-collapse:collapse;font-size:9pt}}td{{padding:2px 6px;font-size:8.5pt;border-bottom:1px solid #eee}}td:first-child{{color:#7C3AED;font-weight:700}}
</style></head><body>
<section class="pg cover"><div class="logo">UseThisSI</div><h1>The UseThisSI<br><em>Builder Stack</em></h1><div class="cyan"></div><p>The 25 AI tools we'd actually use to build, ship and grow, sorted by the job and checked for price.</p><p style="font-size:11pt;color:#8b8ba8">October 2026 edition · Exclusive for UseThisSI referrers</p><div class="url">usethissi.vercel.app</div></section>
<section class="pg intro"><div class="bar"></div><div class="sh"><h2>Why this stack</h2><span>Read this first</span></div>
<p>There's a new "AI tool of the day" every hour. Most of them don't matter. This guide is the short list: the tools we'd reach for if we had to build something real this week.</p>
<ul><li><b>Top picks first.</b> Our #1 choice for each of 10 jobs, from vibe-coding an app to voice and research.</li><li><b>Then the bench.</b> 15 strong alternatives for when the top pick doesn't fit your budget or workflow.</li><li><b>Honest prices.</b> Prices are taken from our directory. Where we couldn't verify a price, we say "check vendor site" rather than guess. Prices change, so confirm before you buy.</li><li><b>A setup tip for each tool</b> to get you to a useful result in your first session.</li></ul>
<p>Every tool links to its full page on UseThisSI with alternatives and updates. Get the free weekday brief at <b>usethissi.beehiiv.com</b>.</p>
<h3 style="margin-top:18px">The 25 at a glance</h3><table>{idx}</table><div class="ft">The UseThisSI Builder Stack · usethissi.vercel.app</div></section>
{pages}
<section class="pg cover" style="justify-content:center"><div class="logo" style="font-size:30pt">Build something this week.</div><div class="cyan"></div><p>Know a tool that belongs here? Reply to any UseThisSI brief and tell us. Thanks for sharing UseThisSI. At 10 referrals you get a shout-out in the brief.</p><div class="url">usethissi.vercel.app · usethissi.beehiiv.com · @UseThisSI</div></section>
</body></html>'''
open('builder-stack.html','w').write(H)
