"""Apply Oct 18 2026 freshness rechecks to data.csv. Each entry: tool -> dict of new field values. Only fields verified on official pages today."""
import csv,io,json
D="2026-10-18"; O=f"[official, Oct 18]"
U={
"Windsurf (Devin Desktop)":None,  # handled by key below
}
U={
"Windsurf (now Devin Desktop)":dict(free_tier="Yes (Free plan)",starting_paid_price=f"$20/mo Pro {O}"),
"Make":dict(free_tier="Yes (1,000 credits/mo)",starting_paid_price=f"$9/mo Core billed annually (10,000 credits) {O}"),
"Gumloop":dict(free_tier="No free plan shown (14-day trial)",starting_paid_price=f"$37/mo Pro {O}"),
"Scenario":dict(free_tier="Yes (50 credits/day; personal use only)",starting_paid_price=f"$15/mo Starter (monthly; annual saves 33%) {O}"),
"PixelLab":dict(free_tier="Yes (free trial: 40 fast generations)",starting_paid_price=f"$12/mo Tier 1 Pixel Apprentice {O}"),
"Midjourney":dict(free_tier="No",starting_paid_price=f"$10/mo Basic ($8/mo billed annually) {O}"),
"Leonardo.Ai":dict(free_tier="Yes (150 fast tokens/day)",starting_paid_price=f"$12/mo Essential, ex. tax {O}"),
"Ideogram":dict(free_tier="Yes (weekly free credits)",starting_paid_price=f"$15/mo Plus billed annually, $20 monthly {O}"),
"Krea":dict(free_tier="Yes (100 units/day)",starting_paid_price=f"$21/mo Pro billed annually, $35 monthly {O}"),
"Rosebud AI":dict(free_tier="Yes (8,000 credits/week)",starting_paid_price=f"$15/mo {O}"),
"Suno":dict(free_tier="Yes (50 credits/day, no commercial use)",starting_paid_price=f"$8/mo Pro billed yearly, $10 monthly {O}"),
"ElevenLabs Music and SFX":dict(free_tier="Yes (10k credits/mo, includes music and SFX)",starting_paid_price=f"$6/mo Starter (music commercial use) {O}"),
"Udio":dict(free_tier="Yes (10 credits/day)",starting_paid_price=f"$8/mo Standard billed annually, $10 monthly {O}"),
"AIVA":dict(free_tier="Yes (non-commercial, credit AIVA, 3 downloads/mo)",starting_paid_price=f"€11/mo Standard billed annually, + VAT {O}"),
"Runway":dict(free_tier="Yes (125 one-time credits)",starting_paid_price=f"$12/mo Standard billed annually, $15 monthly {O}"),
"Descript":dict(free_tier="Yes (1 media hour/mo, 720p)",starting_paid_price=f"$16/mo Hobbyist annual, $24 monthly {O}"),
"CapCut":dict(free_tier="Yes",starting_paid_price=f"$19.99/mo (US, monthly; yearly up to 30% off) {O}"),
"Kling AI":dict(starting_paid_price=f"$10/mo Standard ($6.99 first month) {O}"),
"Synthesia":dict(free_tier="Yes (10 min video/mo, watermarked)",starting_paid_price=f"$18/mo Starter billed yearly, $29 monthly {O}"),
"Claude":dict(free_tier="Yes",starting_paid_price=f"$17/mo Pro annual, $20 monthly {O}"),
"Claude Code":dict(starting_paid_price=f"$17/mo annual, $20 monthly via Claude Pro {O}"),
"ChatGPT":dict(free_tier="Yes (GPT-6)",starting_paid_price=f"$20/mo Plus (monthly only) {O}"),
"Jasper":dict(free_tier="No (7-day trial)",starting_paid_price=f"$59/mo Pro annual, $69 monthly {O}"),
"Copy.ai":dict(starting_paid_price=f"$24/mo billed yearly, $29 monthly {O}"),
"Gamma":dict(free_tier="Yes (400 one-time credits)",starting_paid_price=f"$9/seat/mo Plus billed annually {O}"),
"Perplexity":dict(free_tier="Yes",starting_paid_price=f"$17/mo Pro billed annually {O}"),
"Gemini (Deep Research)":dict(free_tier="Yes",starting_paid_price=f"$4.99/mo Google AI Plus; $19.99/mo AI Pro {O}"),
"NotebookLM":dict(reason="Grounded in your own sources (now also branded Gemini Notebook)",free_tier="Yes (up to 50 sources per notebook)",starting_paid_price=f"$4.99/mo via Google AI Plus {O}"),
"Cartesia":dict(free_tier="Yes (20K credits/mo)",starting_paid_price=f"$5/mo Pro {O}"),
"Murf AI":dict(free_tier="Yes (free credits)",starting_paid_price=f"API from $0.03 per 1,000 chars (Studio TTS) {O}"),
"Google Antigravity":dict(free_tier="Yes (Individual plan, $0)",starting_paid_price=f"Org plans from $30/seat/mo; Pro via Google AI plans {O}"),
"ngram":dict(starting_paid_price=f"$23.20/mo Basic billed annually, $29 monthly {O}"),
"Speechify":dict(free_tier="Yes (up to 1.5x speed)",starting_paid_price=f"$29/mo Premium billed monthly {O}"),
"Google AI Studio":dict(starting_paid_price=f"Free tier; Argon API $2/$10 per 1M tokens thru Nov 30, then $4/$20 {O}"),
"ElevenLabs":dict(starting_paid_price=f"$6/mo Starter ($1 first month promo ends Oct 18) {O}"),
}
rows=list(csv.reader(open("data.csv")))
hdr=rows[0]; idx={h:i for i,h in enumerate(hdr)}
log=[];seen=set()
for r in rows[1:]:
    if not r or r[0]=="release_date": 
        if not r: break
        continue
    t=r[idx["tool"]]
    if t in U:
        seen.add(t)
        for k,v in U[t].items():
            old=r[idx[k]]
            if old!=v: log.append(dict(tool=t,field=k,old=old,new=v))
            r[idx[k]]=v
        oldc=r[idx["last_checked"]] if len(r)>idx["last_checked"] else ""
        while len(r)<=idx["last_checked"]: r.append("")
        r[idx["last_checked"]]=D
        log.append(dict(tool=t,field="last_checked",old=oldc,new=D))
missing=set(U)-seen
assert not missing, missing
buf=io.StringIO(); w=csv.writer(buf,lineterminator="\r\n"); w.writerows(rows)
open("data.csv","w").write(buf.getvalue())
with open("ops/freshness/changes.csv","a",newline="") as f:
    cw=csv.DictWriter(f,fieldnames=["date","tool","field","old","new","source"])
    if f.tell()==0: cw.writeheader()
    for e in log: cw.writerow(dict(date=D,source="official pricing page",**e))
print(len(seen),"tools updated;",sum(1 for e in log if e['field']!='last_checked'),"field changes")
