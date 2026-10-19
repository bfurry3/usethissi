"""'Find your AI stack in 30 seconds' quiz: recommendation data, computed at build time from data.csv.

Every pick comes from a tool that was checked in the last 30 days and has a verified free-tier field
and a verified starting price. Nothing here invents a price: the cards show the data.csv text verbatim
(minus our [source] notes) and the per-tool last-checked date. Affiliate status is never read.
Python 3.9 compatible.
"""
import re

ROLES = [
    ("founder", "Founder or solo operator", True, ["vibe-code-an-app-or-landing-page", "automate-workflows", "write-content", "research", "set-up-or-run-ai-agents"]),
    ("dev", "Developer", False, ["ai-coding-assistant", "set-up-or-run-ai-agents", "vibe-code-an-app-or-landing-page", "automate-workflows", "research"]),
    ("marketer", "Marketer or content creator", True, ["write-content", "edit-and-generate-video", "research", "automate-workflows", "voice-and-tts"]),
    ("freelancer", "Freelancer or agency", True, ["write-content", "automate-workflows", "edit-and-generate-video", "research", "vibe-code-an-app-or-landing-page"]),
    ("gamedev", "Indie game dev", True, ["make-game-art-and-sprites", "generate-music-and-sfx", "ai-coding-assistant", "voice-and-tts", "edit-and-generate-video"]),
    ("explore", "Student or just exploring", False, ["research", "write-content", "vibe-code-an-app-or-landing-page", "ai-coding-assistant"]),
]
BUDGETS = [("0", "$0, free only", 0.0), ("20", "$20/mo or less", 20.0), ("50", "$50/mo or less", 50.0), ("any", "Whatever works", None)]
SKILLS = [("new", "New to AI tools"), ("mid", "I use them most weeks"), ("tech", "I code or can self-host")]
DEFAULT_SKILL = "mid"


def kind(free):
    """Classify a free tier from its listed text. Order matters (n8n: self-host is the ongoing free tier)."""
    x = free.lower()
    if re.search(r"non-commercial|no commercial|personal use", x):
        return "noncommercial"
    if re.search(r"self-host|open source|byok|weights|apache|mit\b|mit-0", x):
        return "selfhost"
    if re.search(r"trial|one-time|\d+\s*days\b", x):
        return "trial"
    if "watermark" in x:
        return "watermark"
    return "ok"


PAID_NOTES = ["", "Same tool, paid plan. Upgrade once you hit the free limits every week.", "Fits your budget: from {price}/mo."]
SKIP_NOTES = ["", "No free plan, and your budget is $0.", "Starts at {price}/mo, over your budget.",
              "The free allowance runs out instead of resetting, so it won't stay free.",
              "Free tier isn't for commercial use, so it won't cover client or business work.",
              "Free tier means running it yourself or paying your own model costs. Not a beginner's first tool.",
              "Costs more than {paidtool} ({price} vs {paidprice}/mo) for the same job.",
              "Paid only, and your picks already cover this job.",
              "Overlaps with your picks. Add it later only if they fall short."]

CATCH = {
    "noncommercial": "Free tier isn't for commercial use.",
    "selfhost": "Free means you run it yourself or pay your own model costs.",
    "trial": "Free allowance runs out (one-time credits or a trial), it doesn't reset.",
    "watermark": "Free output carries a watermark.",
    "ok": "",
}


def monthly(price):
    """Lowest listed per-month subscription price, as (value, currency), or None. Usage-based prices are ignored."""
    best = None
    for sym, v in re.findall(r"([$\u20ac])\s?([\d,]+(?:\.\d+)?)(?:/(?:user|seat))?/mo\b", price):
        val = float(v.replace(",", ""))
        cur = "EUR" if sym == "\u20ac" else "USD"
        if best is None or val < best[0]:
            best = (val, cur)
    return best


def build(uses, fresh, bad_price, cprice, fl, nice, slug):
    jobs = list(uses.keys())
    jslug = {u: slug(u) for u in jobs}
    tools, tindex = [], {}
    elig = {}
    for u in jobs:
        L = []
        for i, d in enumerate(uses[u]):
            if not fresh(d) or bad_price(d["price"]) or d["free"].strip().lower().startswith("unverified") or not d["free"].strip():
                continue
            key = d["slug"] + "|" + jslug[u]
            m = monthly(cprice(d["price"]))
            t = {
                "id": len(tools), "slug": d["slug"], "tool": d["tool"], "job": jslug[u], "reason": d["reason"].strip().rstrip("."),
                "free": d["free"].strip(), "freeShort": d["free"].strip(), "hasFree": d["free"].strip().lower().startswith("yes"),
                "price": cprice(d["price"]), "checked": d["checked"], "checkedNice": nice(d["checked"]),
                "top": d["role"] == "Top pick", "order": i, "kind": kind(d["free"]),
                "mo": m[0] if m else None, "cur": m[1] if m else None,
            }
            tindex[key] = t["id"]
            tools.append(t)
            L.append(t)
        elig[jslug[u]] = L
    # combos[role][job][budget][skill] = [free, paid, skip, paid_note, skip_note, free_upgrade_fits]
    combos = [[[[pick(elig[jslug[u]], commercial, cap, bk, sk) for sk, _ in SKILLS] for bk, _, cap in BUDGETS] for u in jobs] for _, _, commercial, _ in ROLES]
    out_tools = [{k: t[k] for k in ("slug", "tool", "reason", "freeShort", "price", "checked", "checkedNice", "kind", "mo", "cur")} for t in tools]
    return {
        "tools": out_tools,
        "jobs": [{"slug": jslug[u], "name": u} for u in jobs],
        "roles": [{"k": rk, "name": n, "jobs": jl} for rk, n, _, jl in ROLES],
        "budgets": [{"k": bk, "name": n} for bk, n, _ in BUDGETS],
        "skills": [{"k": sk, "name": n} for sk, n in SKILLS],
        "catch": CATCH, "paidNotes": PAID_NOTES, "skipNotes": SKIP_NOTES,
        "combos": combos,
        "_eligible": elig,
    }


def fmt(v, cur):
    s = ("\u20ac" if cur == "EUR" else "$") + ("%.2f" % v)
    return s[:-3] if s.endswith(".00") else s


def free_score(t, commercial, skill):
    s = float(t["order"]) / 100.0
    if t["top"]:
        s -= 1.5
    k = t["kind"]
    if k == "trial":
        s += 3
    elif k == "noncommercial" and commercial:
        s += 2
    elif k == "selfhost":
        s += {"new": 4, "mid": 1, "tech": 0}[skill]
    elif k == "watermark":
        s += 1
    return s


def affordable(t, cap, bk):
    if t["mo"] is None:
        return False
    if bk == "any":
        return True
    if cap is None or cap <= 0 or t["cur"] != "USD":
        return False
    return t["mo"] <= cap + 1e-9


def pick(L, commercial, cap, bk, skill):
    """Return [free_id, paid_id, skip_id, paid_note_code, skip_note_code]; ids are None (-1 in JSON) when there is no honest pick."""
    frees = sorted([t for t in L if t["hasFree"]], key=lambda t: free_score(t, commercial, skill))
    free = frees[0] if frees else None
    paid, pnote = None, 0
    if bk != "0":
        cands = [t for t in L if affordable(t, cap, bk)]
        if skill == "new":
            cands = [t for t in cands if t["kind"] != "selfhost"] or cands
        # Prefer a different tool than the free pick (the promise is 3 tools), editorial order otherwise.
        cands.sort(key=lambda t: (1 if (free is not None and t["slug"] == free["slug"]) else 0, 0 if t["top"] else 1, t["order"]))
        if cands:
            paid = cands[0]
            pnote = 1 if (free is not None and paid["slug"] == free["slug"]) else 2
    used = set(x["slug"] for x in (free, paid) if x is not None)
    best, bs, bnote = None, -1.0, 0
    for t in L:
        if t["slug"] in used:
            continue
        sc, note = 0.0, 0
        over = t["mo"] is not None and t["cur"] == "USD" and bk not in ("0", "any") and t["mo"] > (cap or 0)
        weakfree = (not t["hasFree"]) or t["kind"] == "trial"
        if bk == "0" and not t["hasFree"]:
            sc, note = 4.0, 1
        elif over and weakfree:
            sc, note = 3.0 + t["mo"] / 1000.0, 2
        elif t["hasFree"] and t["kind"] == "trial" and bk == "0":
            sc, note = 2.5, 3
        elif t["hasFree"] and t["kind"] == "noncommercial" and commercial:
            sc, note = 2.2, 4
        elif t["kind"] == "selfhost" and skill == "new":
            sc, note = 2.0, 5
        elif weakfree and paid is not None and t["mo"] is not None and paid["mo"] is not None and t["cur"] == paid["cur"] and t["mo"] > paid["mo"]:
            sc, note = 1.0 + t["mo"] / 1000.0, 6
        elif not t["hasFree"]:
            sc, note = 1.5, 7
        elif t["kind"] == "trial":
            sc, note = 0.9, 3
        else:
            sc, note = 0.5 + t["order"] / 1000.0, 8
        if sc > bs:
            best, bs, bnote = t, sc, note
    if best is not None and not bnote:
        best = None
    av, ad = anchor(paid, best)
    return [free["id"] if free else -1, paid["id"] if paid else -1, best["id"] if best else -1, pnote, bnote,
            1 if (free is not None and paid is not None and free["slug"] != paid["slug"] and affordable(free, cap, bk)) else 0,
            av, ad]


def anchor(paid, skip):
    """Real monthly cost of trying the locked tools yourself, from data.csv verified prices only.
    paid pick's cheapest monthly plan + skip tool's cheapest monthly plan; paid only if skip has no
    verified USD monthly price; (-1, "") if the paid pick has none. Returns (value, oldest checked date, formatted)."""
    if paid is None or paid["mo"] is None or paid["cur"] != "USD":
        return -1, ""
    if skip is not None and skip["mo"] is not None and skip["cur"] == "USD":
        return round(paid["mo"] + skip["mo"], 2), min((paid, skip), key=lambda t: t["checked"])["checkedNice"]
    return round(paid["mo"], 2), paid["checkedNice"]


def note_text(code, notes, t, paid):
    """Render a note code the same way the page's JS does."""
    if not code or t is None:
        return ""
    txt = notes[code].replace("{price}", fmt(t["mo"], t["cur"]) if t.get("mo") is not None else "")
    if paid is not None:
        txt = txt.replace("{paidtool}", paid["tool"]).replace("{paidprice}", fmt(paid["mo"], paid["cur"]) if paid.get("mo") is not None else "")
    return txt


def result(Q, role, job, budget, skill=DEFAULT_SKILL):
    """Look up one quiz result by keys, e.g. result(Q, "dev", "ai-coding-assistant", "20", "tech")."""
    ri = [r["k"] for r in Q["roles"]].index(role)
    ji = [j["slug"] for j in Q["jobs"]].index(job)
    bi = [b["k"] for b in Q["budgets"]].index(budget)
    si = [k["k"] for k in Q["skills"]].index(skill)
    f, p, s, pn, sn, up = Q["combos"][ri][ji][bi][si][:6]
    T = Q["tools"]
    ft, pt, st = (T[f] if f >= 0 else None), (T[p] if p >= 0 else None), (T[s] if s >= 0 else None)
    return {"free": ft, "paid": pt, "skip": st,
            "paid_note": note_text(pn, PAID_NOTES, pt, pt), "skip_note": note_text(sn, SKIP_NOTES, st, pt),
            "upgrade": ("Happy with %s? Its paid plan starts at %s/mo." % (ft["tool"], fmt(ft["mo"], ft["cur"]))) if up else ""}
