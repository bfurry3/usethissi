"""Apply Oct 20 2026 freshness rechecks to data.csv (official pages only) and log real value changes to ops/freshness/changes.csv.
last_checked is set to 2026-10-20 only for tools listed here (verified today)."""
import csv,io
D="2026-10-20"; O="[official, Oct 20]"
U={
"Manus":dict(free_tier="Yes (300 credits/day; Manus 2.0 Lite in Agent Mode)",starting_paid_price="$20/mo Pro (4,000 credits; 17% off billed annually) [official help center, Oct 20]",_src="help.manus.im membership pricing article"),
"Muse Code (Meta)":dict(free_tier="No (subscription or pay-as-you-go API)",starting_paid_price=f"$5/mo Everyday Usage; $15 High, $50 Power (adds Muse Wonder Full) {O}",url="https://dev.meta.ai/products/muse-code",_src="dev.meta.ai/products/muse-code"),
"Gemini agent (Google Cloud)":dict(reason="Enterprise work agent inside Gemini Enterprise (early access), launched Oct 8, 2026",free_tier="Trial only (30-day Gemini Enterprise Plus trial; agent features in early access)",starting_paid_price=f"Not published separately; Gemini Enterprise via contact sales {O}",url="https://cloud.google.com/gemini-enterprise",_src="cloud.google.com/gemini-enterprise"),
"CopilotKit CLiF":dict(free_tier="No (Self-Learning is Enterprise early access; CopilotKit Developer plan is free)",starting_paid_price=f"Enterprise custom pricing (Self-Learning early access); not in Pro $39/mo {O}",_src="copilotkit.ai/pricing"),
"Magic Patterns (MagicOS)":dict(free_tier="Yes (limited)",starting_paid_price="$20/seat/mo Starter [official site FAQ, Oct 20]",_src="magicpatterns.com pricing FAQ"),
"Aider":dict(reason="Terminal pair-programmer with repo map and git auto-commits; BYOK (last tagged release Aug 2025)",starting_paid_price=f"Free / pay model providers {O}",_src="aider.chat + GitHub releases"),
"Builder Agent-Native":dict(free_tier="Yes (open source, MIT; Builder.io Free plan 60 agent credits/mo)",starting_paid_price=f"Free OSS (MIT); Builder.io hosted Pro $24/user/mo {O}",_src="builder.io/pricing + GitHub"),
"Bolt.new":dict(starting_paid_price=f"$25/mo Pro ($18/mo billed annually) {O}",_src="bolt.new/pricing"),
"v0 by Vercel":dict(starting_paid_price=f"$30/user/mo Plus {O}",_src="v0.app/pricing"),
"Replit":dict(starting_paid_price=f"$20/mo Core ($18 annual) {O}",_src="replit.com/pricing"),
"Hostinger AI Builder":dict(starting_paid_price=f"$2.49/mo Premium (48-mo term; renews $10.99/mo) {O}",_src="hostinger.com/ai-website-builder"),
"GitHub Copilot":dict(starting_paid_price=f"$10/mo Pro {O}",_src="github.com/features/copilot/plans"),
"Tabnine":dict(starting_paid_price="Contact sales (now part of Tricentis) [official redirect, Oct 20]",_src="tabnine.com/pricing redirects to tricentis.com/contact-us"),
"n8n":dict(free_tier="Yes (self-host Community Edition); Cloud free trial",starting_paid_price=f"€20/mo Starter, billed annually {O}",_src="n8n.io/pricing"),
"Lindy":dict(starting_paid_price=f"$29.99/user/mo Team (3,000 credits) {O}",_src="lindy.ai/pricing"),
"CrewAI":dict(starting_paid_price=f"Free cloud Basic; Enterprise custom {O}",_src="crewai.com/pricing"),
"Zapier":dict(starting_paid_price=f"$19.99/mo Professional (starting price) {O}",_src="zapier.com/pricing"),
"Muse Spark Open (Meta)":dict(free_tier="Yes (weights; Muse Model License, limited commercial terms)",starting_paid_price=f"Free weights; hosted via Baseten/Fireworks/Groq/Together/etc {O}",_src="research.meta.ai/blog/muse-spark-open"),
"TwelveLabs Jockey":dict(starting_paid_price=f"$29/mo Plus {O}",_src="twelvelabs.io/pricing"),
"Chainguard Workspaces":dict(reason="Hardened microVM sandboxes for agents + optional Checks CI gating (beta)",free_tier="Yes (beta: 500 free hours/month)",starting_paid_price=f"Compute-based (beta) {O}",_src="chainguard.dev Workspaces launch post FAQ"),
"Autonomous Harness":dict(starting_paid_price=f"Free OSS (MIT); optional Harness device $149 {O}",_src="GitHub README + autonomous.ai/harness-device"),
"AWS Aidlc":dict(starting_paid_price="Free OSS [official repo, Oct 20]",_src="github.com/awslabs/aidlc-workflows (MIT-0)"),
}
REMOVE={"Relevance AI":"pricing page now lists only Enterprise / talk to sales (no self-serve plan), so it no longer fits a solo-builder pick"}
NEW=[["AI coding assistant","Alt","MiniMax Code","Desktop coding agent on MiniMax M3.1 Flash (1M context); the same plan key also works in Claude Code, Cursor and OpenCode","No (M Plan subscription or pay-as-you-go API)",f"$22/mo M Plan Go; API $0.15/$0.60 per 1M tokens {O}","https://agent.minimax.io","unverified",D]]
REL=[
["2026-10-15","Kling 4.0 launches: native 30-second video, up to 15 reference assets and 10 keyframes, MCP and CLI access (API coming soon)","https://ir.kuaishou.com/news-releases/news-release-details/kling-ai-officially-launches-next-generation-kling-40-raising/"],
["2026-10-15","ElevenLabs Instant Soundtracks: auto-scored music plus timed sound effects for uploaded videos (ElevenCreative, ElevenMusic, API)","https://elevenlabs.io/blog/introducing-instant-soundtracks"],
["2026-10-19","MiniMax M3.1 Flash GA: 1M-context agent and coding model at $0.15/$0.60 per 1M tokens (weights later)","https://www.minimax.io/blog/minimax-m31f"],
["2026-10-19","Notion Agents rebuilt: own computer and browser, Auto model router, connect your ChatGPT plan, new AI credit system","https://www.notion.com/releases/2026-10-19"],
["2026-10-19","GitHub Copilot retires GPT-5.5, GPT-5.4, GPT-5 mini, Gemini 3.7 Flash and Grok 4.5 (suggested: GPT-6.1 Sol, GPT-6 Luna, Gemini 3.8 Flash, Grok 4.7)","https://github.blog/changelog/2026-10-19-github-copilot-models-deprecated-on-october-19-2026/"],
["2026-10-20","Mintlify Autopilot beta: always-on agent that opens doc-update PRs when code changes (250 credits per PR)","https://www.mintlify.com/blog/autopilot"],
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
for n in NEW: out.append(n); log.append([D,n[2],"added","",n[5],"agent.minimax.io + platform.minimax.io M Plan docs"])
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
