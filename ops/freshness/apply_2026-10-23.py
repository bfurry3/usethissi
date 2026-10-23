"""Apply Oct 23 2026 freshness rechecks to data.csv (official pages only) and log real value changes to ops/freshness/changes.csv.
last_checked is set to 2026-10-23 only for tools listed here (verified today from the vendor's own page or official docs).
Corrections that are not price moves are logged with field 'correction' so the homepage price-change list ignores them.
Not verified today (need a browser check): Make (pricing page 403 to scripts; FAQ confirms Free 1,000 credits only), PixelLab (prices render in JS), Krea (annual Basic shows $5 vs stored $5.25; JS-bound)."""
import csv,io
D="2026-10-23"; O="[official, Oct 23]"
U={
"Google Antigravity":dict(starting_paid_price=f"Org plans from $30/seat/mo (eligible Gemini Enterprise); Pro via Google AI plans {O}",_src="antigravity.google/pricing (Individuals $0/month; Standard/Plus from $30 USD per seat per month for eligible Gemini Enterprise customers; pay-as-you-go $0 seat fee)",_corr=True),
"Cursor":dict(starting_paid_price=f"$8/mo Plus (Grok models only); $30/mo Premium {O}",_src="cursor.com/pricing (Free $0; Plus $8/month, only Grok models; Premium $30/month; Teams $30/user/month)"),
"ElevenLabs":dict(starting_paid_price=f"$6/mo Starter ($1 first month until Nov 1) {O}",_src="elevenlabs.io/pricing (Free 10k credits; Starter $6, 'Until Nov 1 First month 83% off $1'; Creator $22)"),
"ElevenLabs Music and SFX":dict(starting_paid_price=f"$6/mo Starter, music commercial use ($1 first month until Nov 1) {O}",_src="elevenlabs.io/pricing (Free includes Music and Sound Effects; Starter $6 adds music commercial use; first month $1 until Nov 1)"),
"Amp":dict(starting_paid_price=f"$20/mo Individual {O}",_src="ampcode.com/pricing (Hobby Free; Individual $20/mo; Enterprise custom)"),
"Browserbase":dict(starting_paid_price=f"$20/mo Developer {O}",_src="browserbase.com/pricing (Free $0: 3 concurrent browsers, 1 browser hour; Developer $20/mo; Startup $99/mo)"),
"Mastra":dict(starting_paid_price=f"Free OSS; hosted Platform Starter $0 then usage; Teams $250/mo {O}",_src="mastra.ai/pricing (Starter $0/month, 100K events; Teams $250/month)"),
"Exa":dict(free_tier="Yes ($10 credits/mo plus $10 onboarding bonus)",starting_paid_price=f"Pay-as-you-go from $4/1k searches {O}",_src="exa.ai/pricing (Starter Free $10 credits every month plus a $10 onboarding bonus; Search from $4/1k requests)",_corr=True),
"HeyGen":dict(starting_paid_price=f"$29/mo Creator ($24/mo annual) {O}",_src="heygen.com/pricing (Free $0, 3 videos a month; Creator $29/month or $24/month annually)"),
"Pika":dict(starting_paid_price=f"$10/mo Starter ($8 annual) {O}",_src="pika.art/pricing (Starter $10/mo billed monthly; annual -20% $8)"),
"Snyk Evo":dict(starting_paid_price=f"Enterprise / talk to sales (Team plan $25/mo is non-Evo) {O}",_src="snyk.io/plans (Free $0; Team starting at $25/month; Enterprise credit-based platform)"),
"LangGraph":dict(starting_paid_price=f"Free OSS; LangSmith Plus $39/seat/mo for hosting {O}",_src="langchain.com/pricing (Developer $0/seat, 5k traces; Plus $39/seat per month with Deployment)",_corr=True),
"Cline":dict(starting_paid_price=f"Free / pay model providers {O}",_src="cline.bot/pricing (Cline is free for individual developers; pay only for AI inference; bring your own API keys)"),
"Fish Audio":dict(starting_paid_price=f"$10/M UTF-8 bytes Drama 3 API promo thru Nov 12 (list $50); app Plus $11/mo annual {O}",_src="docs.fish.audio pricing-and-rate-limits (drama-3 $50/M UTF-8 bytes; $10 launch promo until Nov 12, 2026 09:00 PT) + fish.audio/plan (Free 8,000 credits; Plus $11/mo annual, $15 monthly)",_corr=True),
"Google AI Studio":dict(starting_paid_price=f"Free tier; Argon API $2/$10 per 1M tokens thru Nov 30, then $4/$20 {O}",_src="ai.google.dev/gemini-api/docs/pricing (Gemini 4 Argon not on Free tier; input $2.00 thru Nov 30, $4.00 from Dec 1; output $10.00 then $20.00)"),
"Lovable":dict(free_tier="Yes (5 build credits/day, up to 30/mo on Free)",starting_paid_price=f"$25/mo Pro ($21/mo billed annually) {O}",_src="docs.lovable.dev subscription-plans (Pro 100 credits $25 monthly, $250/yr = $21/month) + plans-and-credits (Free: 5 daily build credits, up to 30 per calendar month)",_corr=True),
}
NEW=[
["Voice and TTS","Alt","Mistral Voxtral 3","Speech-to-text, text-to-speech and a voice agent API from one vendor, with EU or US endpoints or self-hosting","Yes (Mistral Free plan includes Studio access)",f"$13 per 1M chars TTS (Voxtral Mini TTS 3); voice agents from $0.04/min (preview) {O}","https://mistral.ai/news/voxtral-3/","None found",D],
]
NEWSRC={"Mistral Voxtral 3":"mistral.ai/news/voxtral-3 (Mini TTS 3 $13/1M chars; Mini Transcribe 3 $0.0035/min batch; voice agent API $0.04/min; public preview) + mistral.ai/pricing (Free plan)"}
REL=[
["2026-10-20","Mistral Voxtral 3 (public preview): speech-to-text, text-to-speech and a voice agent API; TTS $13 per 1M chars, transcription from $0.0035/min, voice agents from $0.04/min","https://mistral.ai/news/voxtral-3/"],
["2026-10-22","OpenAI Decisions API is generally available: bounded yes/no and multiple-choice decisions on GPT-6 Luna, up to 400 questions per request, $0.10 per 1M input tokens and no output-token charges","https://openai.com/index/decisions-api/"],
["2026-10-22","1Password for Agents: AI agents sign in to sites without ever seeing your passwords, and you approve each use on your own device","https://www.businesswire.com/news/home/20261022810032/en/1Password-for-Agents-Launches-as-the-Trust-Layer-for-Personal-AI-Agents"],
["2026-10-22","Pictory 3: an AI video agent that turns a brief, doc, URL, slide deck or audio into a script, scenes and a preview video","https://pictory.ai/blog/introducing-pictory-3"],
["2026-10-23","Claude models on Google Cloud, run by Anthropic, are generally available: same prices, Google Cloud billing and IAM, and day-one Claude Platform features","https://cloud.google.com/blog/products/ai-machine-learning/expanding-claude-availability-on-google-cloud"],
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
