#!/usr/bin/env python3
"""Check every internal href/src in dist/ resolves to a file."""
import os,re,sys
bad=[]
for root,_,fs in os.walk("dist"):
    for f in fs:
        if not f.endswith(".html"): continue
        p=os.path.join(root,f)
        for h in re.findall(r'(?:href|src)="(/[^"#?]*)',open(p).read()):
            t="dist"+h+("index.html" if h.endswith("/") else "")
            if not os.path.exists(t): bad.append((p,h))
for b in bad: print("BROKEN",*b)
print(f"{len(bad)} broken internal links"); sys.exit(1 if bad else 0)
