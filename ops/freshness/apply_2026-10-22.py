"""Apply Oct 22 2026 freshness rechecks to data.csv (official pages only) and log real value changes to ops/freshness/changes.csv.
last_checked is set to 2026-10-22 only for tools listed here (verified today from the vendor's own page or official help center).
Corrections that are not price moves are logged with field 'correction' so the homepage price-change list ignores them."""
import csv,io
D="2026-10-22"; O="[official, Oct 22]"
U={
"Midjourney":dict(starting_paid_price=f"$10/mo Basic ($8/mo billed annually) {O}",_src="docs.midjourney.com Comparing Midjourney Plans (Basic $10 monthly, $96/yr)"),
"Ideogram":dict(starting_paid_price=f"$15/mo Plus billed annually, $20 monthly {O}",_src="ideogram.ai/pricing (Plus $15/mo, $180/yr; free accounts get weekly credits)"),
"Leonardo.Ai":dict(starting_paid_price=f"$12/mo Essential, ex. tax {O}",_src="leonardo.ai/pricing (Free 150 fast tokens/day; Essential $12/month ex. tax)"),
"Udio":dict(free_tier="Yes (10 credits/day, 100/mo)",starting_paid_price=f"$8/mo Standard billed annually, $10 monthly {O}",_src="udio.com/pricing (Free 10 credits/day, 100/mo; Standard $10, $8/mo annual)"),
"NotebookLM":dict(starting_paid_price=f"$4.99/mo via Google AI Plus {O}",_src="notebooklm.google/plans (Free up to 50 sources; AI Plus 100) + gemini.google/subscriptions ($4.99/month)"),
"Murf AI":dict(free_tier="Yes ($10 free API credit, no card)",starting_paid_price=f"API from $0.01 per 1,000 chars (Falcon); Studio TTS $0.03 {O}",_src="murf.ai/pricing (Free trial $10 for API calls; Falcon $0.01/1000 chars; Studio TTS $0.03/1000 chars)",_corr=True),
"CapCut":dict(starting_paid_price=f"$19.99/mo Pro (US, monthly; yearly up to 30% off) {O}",_src="capcut.com/pricing (Pro USD 19.99/month)"),
"Speechify":dict(starting_paid_price=f"$29/mo Premium billed monthly {O}",_src="speechify.com/pricing (Free up to 1.5x; Premium $29/Month billed monthly)"),
"Perplexity":dict(starting_paid_price=f"$17/mo Pro billed annually {O}",_src="perplexity.ai/pro + perplexity.ai/hub/pricing (Pro $17/mo billed annually; Free $0)"),
"ChatGPT":dict(starting_paid_price=f"$20/mo Plus (monthly only) {O}",_src="help.openai.com What is ChatGPT Plus ($20/month billed monthly, no annual) + chatgpt.com/pricing (Free GPT-6)"),
"Gamma":dict(starting_paid_price=f"$9/seat/mo Plus billed annually {O}",_src="gamma.app/pricing ($9/seat/mo, $108/seat/yr) + help.gamma.app (Free 400 credits at signup, no refresh)"),
"Kling AI":dict(free_tier="Yes (Basic $0: credits monthly by logging in)",starting_paid_price=f"$10/mo Standard ($6.99 first month) {O}",url="https://kling.ai",_src="klingai.com/membership/membership-plan (Basic $0 free forever, credits by logging in; Standard $79.2/yr, list $120); klingai.com 301 -> kling.ai",_corr=True),
}
NEW=[
["AI coding assistant","Alt","Recursive Flint","Free open-weights coding model that runs on your own laptop, so your code stays private and there are no API fees","Yes (Apache 2.0 open weights on Hugging Face)",f"Free (open weights; runs on your own hardware) {O}","https://recursive.com/updates/introducing-recursive-flint","None found",D],
]
NEWSRC={"Recursive Flint":"recursive.com/updates/introducing-recursive-flint + huggingface.co/RecursiveSI/flint (Apache 2.0)"}
REL=[
["2026-10-21","Recursive Flint: free open-weights coding model (40B total, 2.5B active) built to run locally; 125+ tokens/sec on an M4 Pro MacBook Pro, Apache 2.0","https://recursive.com/updates/introducing-recursive-flint"],
["2026-10-21","HeyGen Video (heygen-video-1): 5 to 15 second clips with picture and sound from one prompt, via the HeyGen API (paid API keys) and Creative Studio","https://www.heygen.com/blog/introducing-heygen-video"],
["2026-10-21","Stripe Treasury for agents: let ChatGPT or Claude check balances, pay invoices, move funds and convert currencies, with human approval controls","https://stripe.com/newsroom/news/treasury-for-agents"],
["2026-10-21","OpenAI models and Codex are coming to Google Cloud Model Garden (GA planned in the coming weeks), and soon to Google Antigravity","https://openai.com/index/openai-models-google-cloud"],
]
txt=open("data.csv").read(); tpart,rpart=txt.split("\n\n",1)
rows=list(csv.reader(io.StringIO(tpart))); hdr=rows[0]; body=rows[1:]
ix={h:i for i,h in enumerate(hdr)}
log=[]; seen=set(); out=[]
strip=lambda s: s.split(" [")[0].strip()
for r in body:
    t=r[ix["tool"]]
    if t in U:
        seen.add(t); u=U[t]; src=u.get("_src","official page"); corr=u.get("_corr")
        for f,v in u.items():
            if f.startswith("_"): continue
            old=r[ix[f]]
            if strip(old)!=strip(v): log.append([D,t,"correction" if corr else f,old,v,src])
            r[ix[f]]=v
        if r[ix["last_checked"]]!=D: log.append([D,t,"last_checked",r[ix["last_checked"]],D,src])
        r[ix["last_checked"]]=D
    out.append(r)
missing=set(U)-seen; assert not missing, missing
have_tools={r[ix["tool"]] for r in out}
for n in NEW:
    if n[2] in have_tools: continue
    out.append(n); log.append([D,n[2],"added","",n[5],NEWSRC[n[2]]])
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
