"""Oct 23 2026 browser rechecks (Q9 + Q13): Gamma, Make, Krea, PixelLab, official pages only.
Real price moves are logged by field; last_checked moves are logged as usual. Also refreshes data/plans.csv."""
import csv,io
D="2026-10-23"; O="[official, Oct 23]"
U={
"Gamma":dict(starting_paid_price=f"$9/seat/mo Plus billed annually, $12 monthly {O}",url="https://gamma.app/pricing",_src="gamma.app/pricing (Plus $12/mo monthly or $9/mo annual; Pro $18 annual; Ultra $90 annual; Free 400 credits at signup, up to 10 slides per prompt)"),
"Make":dict(starting_paid_price=f"$12/mo Core billed annually, $16 monthly (10,000 credits) {O}",url="https://www.make.com/pricing",_src="make.com/pricing at 10k credits (Core $16 monthly/$12 annual; Pro $28/$21; Teams $51/$38; Free 1,000 credits/mo)"),
"Krea":dict(starting_paid_price=f"$5.25/mo Basic billed annually, $9 monthly; Pro $21 annual, $35 monthly {O}",url="https://www.krea.ai/pricing",_src="krea.ai/pricing (Basic $9 monthly/$5.25 yearly; Pro $35/$21; Max $105/$63; Free 100 units/day)"),
"PixelLab":dict(free_tier="Yes (40 fast generations, then 5 slower generations/day)",starting_paid_price=f"$12/mo Tier 1 Pixel Apprentice ($99/yr) {O}",url="https://www.pixellab.ai/",_src="pixellab.ai (Tier 1 $12/mo or $99/yr; Tier 2 $24/mo or $220/yr; Tier 3 $50/mo; Free 40 fast generations then 5 slower/day)"),
}
txt=open("data.csv").read(); tpart,rpart=txt.split("\n\n",1)
rows=list(csv.reader(io.StringIO(tpart))); hdr=rows[0]; ix={h:i for i,h in enumerate(hdr)}
log=[]; strip=lambda s: s.split(" [")[0].strip()
for r in rows[1:]:
    t=r[ix["tool"]]
    if t in U:
        u=U[t]; src=u["_src"]
        for f,v in u.items():
            if f.startswith("_"): continue
            if strip(r[ix[f]])!=strip(v): log.append([D,t,f,r[ix[f]],v,src])
            r[ix[f]]=v
        if r[ix["last_checked"]]!=D: log.append([D,t,"last_checked",r[ix["last_checked"]],D,src])
        r[ix["last_checked"]]=D
s=io.StringIO(); w=csv.writer(s,lineterminator="\n"); w.writerows(rows); s.write("\n"+rpart)
open("data.csv","w").write(s.getvalue())
with open("ops/freshness/changes.csv","a",newline="") as f: csv.writer(f,lineterminator="\n").writerows(log)
# plans.csv
P={"Krea":[("Free",0,0,"100 compute units/day"),("Basic",5.25,9,"Entry plan"),("Pro",21,35,"Commercial license (save 40% with annual)"),("Max",63,105,"More compute units")],
"Gamma":[("Free",0,0,"400 credits at signup; up to 10 slides per prompt; Gamma badge on exports"),("Plus",9,12,"Per seat; 1,000 credits/mo; removes Gamma branding"),("Pro",18,"","Per seat; 4,000 credits/mo; custom domains; API"),("Ultra",90,"","Per seat; 20,000 credits/mo")],
"Make":[("Free",0,0,"1,000 credits/mo"),("Core",12,16,"10,000 credits/mo; unlimited active scenarios"),("Pro",21,28,"10,000 credits/mo; priority execution"),("Teams",38,51,"10,000 credits/mo; teams and roles")],
"PixelLab":[("Free trial",0,0,"40 fast generations, then 5 slower generations/day"),("Tier 1: Pixel Apprentice",8.25,12,"2,000 generations/mo; $99/yr"),("Tier 2: Pixel Artisan",18.33,24,"5,000 generations/mo; priority queue; $220/yr"),("Tier 3: Pixel Architect","",50,"10,000 generations/mo; highest priority")]}
SRC={"Krea":"https://www.krea.ai/pricing","Gamma":"https://gamma.app/pricing","Make":"https://www.make.com/pricing","PixelLab":"https://www.pixellab.ai/"}
pr=list(csv.reader(open("data/plans.csv"))); ph=pr[0]; old={}
keep=[]
for r in pr[1:]:
    if r[0] in P: old.setdefault(r[0],[]).append(r)
    else: keep.append(r)
# preserve Krea Business row (not in this check) but restamp? keep original date.
extra=[r for r in old.get("Krea",[]) if r[1]=="Business"]
newrows=[]
order=[]
for r in pr[1:]:
    if r[0] in P and r[0] not in order: order.append(r[0])
out=[ph]; done=set()
for r in pr[1:]:
    t=r[0]
    if t in P:
        if t in done: continue
        done.add(t)
        for n,a,m,inc in P[t]: out.append([t,n,("%g"%a) if a!="" else "",("%g"%m) if m!="" else "","USD",inc,SRC[t],D])
        if t=="Krea": out+=extra
    else: out.append(r)
csv.writer(open("data/plans.csv","w",newline=""),lineterminator="\n").writerows(out)
for l in log: print(l[1],l[2],"|",l[3],"->",l[4])
