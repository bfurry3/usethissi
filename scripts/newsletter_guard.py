#!/usr/bin/env python3
"""Pre-send guard for UseThisSI beehiiv issues.

Usage:
  python3 scripts/newsletter_guard.py newsletter/YYYY-MM-DD-beehiiv-paste.md
  python3 scripts/newsletter_guard.py --rendered page.html   # web/email version after beehiiv renders it
  python3 scripts/newsletter_guard.py --send-time [ISO-now]  # prints the 7:15 AM America/Phoenix slot to schedule

Exit 0 = PASS (ok to schedule). Exit 1 = FAIL: do NOT publish; alert Baz/AA with the printed reasons.
"""
import re, sys, html
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo

AZ = ZoneInfo("America/Phoenix")
SEND_AT = time(7, 15)
GRACE_MIN = 30  # a run that can't schedule by 7:45 AM goes to tomorrow 7:15 (next weekday)

PLUS_PATTERN = re.compile(r",\s*plus\s+", re.I)
REQUIRED_SECTIONS = ["The big one"]
BIG_ONE_FIELDS = ["The catch", "How to try it"]


def parse_paste(text):
    subj = re.search(r"^Subject:\s*(.*)$", text, re.M)
    pre = re.search(r"^Preheader:\s*(.*)$", text, re.M)
    body = text.split("\n---\n", 1)[1] if "\n---\n" in text else ""
    return (subj.group(1).strip() if subj else ""), (pre.group(1).strip() if pre else ""), body


def check_subject(subject, errors):
    if not subject:
        errors.append("missing Subject")
        return
    if PLUS_PATTERN.search(subject):
        errors.append("subject uses retired 'X, plus Y' pattern: lead with the hook instead")
    if len(subject) > 70:
        errors.append(f"subject too long ({len(subject)} > 70 chars)")


def check_markdown_body(body, errors):
    stripped = body.strip()
    if len(re.sub(r"\s+", "", stripped)) < 200:
        errors.append("body is empty or nearly empty")
        return
    for s in REQUIRED_SECTIONS:
        if not re.search(rf"^#+\s*{re.escape(s)}\b", body, re.M | re.I):
            errors.append(f"missing '{s}' section")
    big = re.split(r"^##\s+The big one.*$", body, flags=re.M | re.I)
    if len(big) > 1:
        sec = re.split(r"^##\s", big[1], flags=re.M)[0]
        for f in BIG_ONE_FIELDS:
            if f.lower() not in sec.lower():
                errors.append(f"'The big one' is missing '{f}'")
        if not re.search(r"\((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2}\)", sec):
            errors.append("'The big one' headline has no dated fact-check like '(Oct 22)'")
    # bare URLs: any http(s) not inside markdown link target ](...)
    no_links = re.sub(r"\]\((https?://[^)\s]+)\)", "]()", body)
    bare = re.findall(r"https?://\S+", no_links)
    if bare:
        errors.append(f"bare visible URL(s) in body: {bare[:3]} (wrap them as [text](url))")
    for line in body.splitlines():
        if re.match(r"^\s*<[a-z]", line):
            errors.append("raw HTML in paste body (beehiiv default editor only)")
            break


def visible_text(h):
    h = re.sub(r"(?is)<(script|style|head)[^>]*>.*?</\1>", " ", h)
    h = re.sub(r"(?s)<[^>]+>", " ", h)
    return html.unescape(h)


def check_rendered(h, errors):
    t = visible_text(h)
    if len(re.sub(r"\s+", "", t)) < 200:
        errors.append("rendered issue is empty")
        return
    if "the big one" not in t.lower():
        errors.append("rendered issue has no 'The big one'")
    if re.search(r"(^|\s)#{1,6}\s", t):
        errors.append("visible raw markdown heading '##' in rendered issue")
    if re.search(r"\*\*|__\S|\[[^\]]+\]\(", t):
        errors.append("visible raw markdown (** or [text](url)) in rendered issue")
    if re.search(r"https?://", t):
        errors.append("visible bare 'https://' text in rendered issue")


def guard_paste(text):
    errors = []
    subject, pre, body = parse_paste(text)
    check_subject(subject, errors)
    if not pre:
        errors.append("missing preview text (Preheader)")
    elif len(pre) < 40:
        errors.append("preview text too short (<40 chars)")
    check_markdown_body(body, errors)
    return errors


def next_send_slot(now=None):
    """7:15 AM AZ today if we're before 7:15+grace, else the next weekday 7:15."""
    now = (now or datetime.now(AZ)).astimezone(AZ)
    slot = datetime.combine(now.date(), SEND_AT, AZ)
    if now.weekday() < 5 and now <= slot + timedelta(minutes=GRACE_MIN):
        return max(slot, now)  # inside window: schedule 7:15 (or now if 7:15-7:45)
    d = now.date() + timedelta(days=1)
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return datetime.combine(d, SEND_AT, AZ)


def main(argv):
    if argv and argv[0] == "--send-time":
        now = datetime.fromisoformat(argv[1]) if len(argv) > 1 else None
        print(next_send_slot(now).isoformat())
        return 0
    if not argv:
        print(__doc__)
        return 2
    if argv[0] == "--rendered":
        errors = []
        check_rendered(open(argv[1], encoding="utf-8").read(), errors)
    else:
        errors = guard_paste(open(argv[0], encoding="utf-8").read())
    if errors:
        print("GUARD FAIL: do NOT publish. Alert Baz/AA instead:")
        for e in errors:
            print(" -", e)
        return 1
    print("GUARD PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
