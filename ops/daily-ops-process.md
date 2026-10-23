# usethissi-weekday-daily-ops: newsletter send process (effective Oct 26, 2026)

Source: Baz's Oct 19-23 review. Every weekday run MUST follow this. A guard FAIL is a hard stop.

1. Write `newsletter/YYYY-MM-DD-beehiiv-paste.md` from `newsletter/TEMPLATE.md`.
   - Subject: hook first, varied shape, no "X, plus Y" (guard rejects ", plus ").
   - Preheader (preview text) on every issue, one full sentence (Oct 23's style).
   - Builders only: drop/reframe non-builder stories (e.g. Oct 21 Gemini small-business hub).
   - Keep "The catch", dated fact-checks "(Oct 22)", "How to try it".
   - No bare URLs: always `[text](url)`.
2. `python3 scripts/newsletter_guard.py newsletter/YYYY-MM-DD-beehiiv-paste.md`
   - FAIL -> do NOT publish. Fix and re-run; if it can't be fixed in-run, alert Baz (chat) with the printed reasons and leave the post as a draft.
3. Paste into beehiiv (default editor, no HTML blocks). Open the web preview, save its HTML, run
   `python3 scripts/newsletter_guard.py --rendered preview.html` (catches leaked "##", "**", visible https://, empty body).
4. Send-time lock: `python3 scripts/newsletter_guard.py --send-time` prints the slot.
   - Before 7:45 AM AZ on a weekday -> schedule 7:15 AM AZ today (or now if 7:15-7:45).
   - Later -> schedule next weekday 7:15 AM AZ. Never "Send now" late (Oct 20 went out 4:42 PM).
   - Use beehiiv "Schedule", not "Publish now".
5. Log subject, preview, guard result, and scheduled time in ops-log.md.

Sender branding (beehiiv Settings > Publication / Emails): sender name "UseThisSI", Reply-To info@usethissi.com, logo static/brand/usethissi-logo-512.png. See ops/beehiiv-branding.md.
