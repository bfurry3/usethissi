# UseThisSI ops log

## 2026-10-14: first ops run
- The base URL is now set in one place, config.json `base_url`, as https://usethissi.vercel.app. Canonical URLs, Open Graph tags, the sitemap, robots.txt and llms.txt all use it.
- Releases: 6 from Oct 7–13, each source confirmed with WebFetch. Removed the older items (Suno Speech Oct 2, Mistral Large 4 Oct 6, Roboflow Agent).
- Tools: added 6 (Google Antigravity, Muse Code, Gemini agent, ngram, Speechify, Google AI Studio). The directory now has 51 rows across 10 use cases.
- Prices confirmed on official pages (WebFetch, Oct 14):
  - **Cursor:** changed. The pricing page now shows Free / Plus $8 (Grok-only) / Premium $30 / Super $100 / Ultra $200, while cursor.com/docs still says Pro $20. Re-check next run.
  - **Others:** n8n €20/mo (annual), Runway $12 (annual) / $15 monthly, ElevenLabs $6 (promo $1 until Oct 18), Suno Premier $24 (annual).
  - **Not confirmed on the official page:** Lovable (page shows no price), Make (prices not rendered), and Perplexity (fetch timed out). Their prices stay from the earlier third-party sources.
- Newsletter: a free Tally or Google Form needs an account, so neither was used. The site uses a GitHub issue form instead (.github/ISSUE_TEMPLATE/newsletter-signup.yml), which is public, so this is a stopgap.
- The Submit page now links to the GitHub issue form submit-tool.yml.
- Newsletter draft #1: newsletter/2026-10-14.md (not sent).
- X search for "usethissi" found 0 posts.

## Next priorities
1. Set up a real newsletter provider (beehiiv or Buttondown, free tier). Needs Baz to sign up.
2. Apply to affiliate programs (Make, n8n, ElevenLabs, Lovable, Runway). Needs Baz.
3. Resolve the conflicting Cursor prices. Fetch Lovable, Make and Perplexity prices in a browser.
4. Submit the sitemap to Google Search Console.
5. Fill in the remaining "unverified" fields.

## 2026-10-14: newsletter moved to beehiiv
- The newsletter now runs on beehiiv at usethissi.beehiiv.com. The embed form 767b56cc-… is on every page's signup block, with a fallback link to https://usethissi.beehiiv.com/subscribe and attribution.js before </body>.
- Removed the GitHub newsletter-signup issue template and the public-issue warning.

## 2026-10-14 ~7:00 AM PT: weekday daily ops (scheduled)

- Releases added (source-confirmed): Fish Audio Drama 3 (Oct 13), MagicOS (Oct 13), CopilotKit CLiF (Oct 13), Roboflow Agent (Oct 14), Chainguard Harness (Oct 14).
- Tools added: Roboflow Agent, CopilotKit CLiF, Fish Audio, Magic Patterns (MagicOS). Directory now 55 tools / 10 use cases / 11 release rows.
- Price spot-check: Cursor pricing page still Free / Plus $8 (Grok-only) / Premium $30 / Super $100 / Ultra $200 (matches CSV). Lovable pricing still client-rendered (no $ amounts in HTML). Make and Perplexity official pricing pages returned 403 to automated fetch.
- Rebuilt, tests pass, link check clean. Pushed to main for Vercel deploy.
- Newsletter #1 rewritten for freshest Oct 13–14 items in newsletter/2026-10-14.md; publishing to beehiiv this run.
- X search for UseThisSI / @UseThisSI / usethissi: 0 posts (account may not exist yet).
- No blockers requiring Baz unless beehiiv login or paywall appears.

