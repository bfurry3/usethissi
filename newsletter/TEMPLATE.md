<!--
UseThisSI daily brief template. Copy to newsletter/YYYY-MM-DD.md, fill in, then:
  python3 newsletter/render.py newsletter/YYYY-MM-DD.md   -> newsletter/YYYY-MM-DD.html
Paste the HTML into a beehiiv "Custom HTML" block (Subject/Preheader go in beehiiv's own fields).

WRITING RULES
- Short sentences. One idea per sentence. No paragraph over 3 lines.
- Every item starts with a bold lead-in (**Name:** or **What happened:**).
- No walls of text: bullets over prose.
- Every claim has a source link. If you can't source it, cut it.
- Never invent numbers, prices, dates or quotes. Prices only from the vendor page.
- Write for builders: say what to DO with it ("Try it:").
- No em dashes or smart quotes: use commas, periods, colons or plain hyphens. (render.py also converts them and outputs pure-ASCII HTML.)
- Subject: no hype. Describe big models accurately ("open weights", "runs via API", "runs on Apple silicon"). Never "free to run", "game-changer", "insane" etc.
- Preheader: ONE proper English sentence, 25-140 chars, capital first letter, ends with a period. Subject-verb-object, e.g. "Meta released open weights for its coding model, and GitHub autofix is now GA."
- Dedupe: each tool/company appears in ONE section only (Today in 30 seconds is the only exception, as a summary).
  Price changes go ONLY in Price watch. Tool of the day must be a different tool than The big one.
- The big one must include **The catch:** with one skeptical point (license limits, hardware cost, or hosted vs local tradeoff).
- SUBJECT: lead with the hook (what the builder gets), vary shape day to day (question, number, "now you can..."). The "X, plus Y" pattern is retired; the guard rejects ", plus ".
- EDITORIAL: every story must be something a builder can use (API, model, dev tool, price). Drop or reframe consumer/small-business items (e.g. Oct 21 "Gemini small-business hub"). Keep The catch, dated fact-checks "(Oct 22)" and How to try it.
- LINKS: never paste a bare URL; always [text](url). Footer: "[78 tools across 10 jobs, prices re-checked weekly](https://www.usethissi.com)".
- PRE-SEND GUARD: python3 scripts/newsletter_guard.py newsletter/DATE-beehiiv-paste.md must PASS before scheduling; after beehiiv preview, save the web version HTML and run --rendered. Schedule at python3 scripts/newsletter_guard.py --send-time (7:15 AM AZ; missed window -> next weekday 7:15, never send late).
- render.py runs these checks and exits non-zero on failure. Fix the brief; never use --force to ship.
- Keep section headings exactly as below; the renderer keys on them. Drop a section only if there is truly nothing (Price watch / tip can be skipped).
-->
# Brief #N | Mon D, YYYY | 5-min read

Subject: Hook first: the one builder payoff of the lead story, 6-9 words (no "X, plus Y"; vary the shape daily)
Preheader: One complete sentence that tells the reader what is inside today.

## Today in 30 seconds
- **Lead item:** one line.
- **Item two:** one line.
- **Item three:** one line.

## The big one
### Headline of the lead story
**What happened:** 1-2 sentences.
**Why it matters for builders:** 1-2 sentences.
**The catch:** one skeptical point (license limits, hardware cost, or hosted vs local).
**How to try it:** one concrete step, with a [link](https://example.com).
[Read the source](https://example.com)

## Quick hits
- **Name (date):** one-line takeaway. [Source](https://example.com)
- **Name (date):** one-line takeaway. [Source](https://example.com)
- **Name (date):** one-line takeaway. [Source](https://example.com)

## Tool of the day
### Tool name (not the same tool as The big one)
**Use it for:** the job it does.
**Price:** from the vendor page only.
**Why we like it:** one sentence.
[Try it on UseThisSI](https://www.usethissi.com/tools/SLUG/)

## Price watch
- **Tool:** what changed / deadline. [Source](https://example.com)

## One tip to try
**Tip title:** 1-3 sentences or a short prompt in `code`.

<!-- Footer (directory link, reply ask, affiliate disclosure) is added automatically by render.py. -->
