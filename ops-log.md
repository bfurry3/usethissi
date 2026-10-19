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
- Newsletter #1 rewritten and published to beehiiv at 7:10 AM PT: https://usethissi.beehiiv.com/p/gemini-4-argon-is-live-plus-a-cv-agent-that-plugs-into-cursor — emailed + web to 1 subscriber (Pro trial Day 1/14).
- X search for UseThisSI / @UseThisSI / usethissi: 0 posts (account may not exist yet).
- No blockers requiring Baz unless beehiiv login or paywall appears.
- @UseThisSI handle does not exist on X yet (API not found); no mentions to act on.

## 2026-10-15 ~00:15 MST: Indexing setup
- Verified live: /sitemap.xml (200, 71 URLs) and /robots.txt (Allow: /, Sitemap: line). Pages have canonical tags, no noindex.
- IndexNow: key fcd27737423484d8886b49b06518a52a, build.py emits dist/<key>.txt (live, 200). Commit 8f8d2c4.
- Submitted all 71 sitemap URLs to api.indexnow.org -> HTTP 202 (accepted, key validation pending). Re-ping after deploys: `python3 indexnow.py`.
- Google Search Console skipped (needs owner login); Google discovers via robots.txt Sitemap line.

## 2026-10-15 ~7:00 AM PT: weekday daily ops (scheduled)

- Releases added (source-confirmed via WebFetch): Builder.io Agent-Native beta (Oct 14), Google Deep Review public launch (Oct 14), Attio Agentic Revenue architecture (Oct 14), Snyk Evo Agentic AppSec (Oct 15), BAND for Developers (Oct 15).
- Tools added (13): Amp, Cline, Aider, Builder Agent-Native, BAND, LangGraph, Mastra, Browserbase, Snyk Evo, Google Deep Review, Exa, HeyGen, Pika. Directory now **68 tools** / 10 use cases / 16 release rows (was 55 / 10 / 11).
- Price spot-check (Oct 15):
  - **Cursor:** still Free / Plus $8 (Grok-only) / Premium $30 / Super $100 / Ultra $200 on cursor.com/pricing (matches CSV; same conflict with older docs still noted).
  - **ElevenLabs Starter:** $1 first month until Oct 18 (normally $6) still live on elevenlabs.io/pricing.
- Rebuilt (`python3 build.py`), tests pass, link check clean. Pushed directory update: commit **336eaa5**.
- Live verified ~7:15 AM PT: homepage shows **68 tools**; /new/ lists all 5 new releases; all 13 new /tools/*/ pages return 200.
- IndexNow re-ping after deploy: `python3 indexnow.py` -> HTTP 200, 84 URLs.
- Newsletter #2 drafted: newsletter/2026-10-15.md (Subject: Agent-Native is open source, plus Google's free doc reviewer). Published to beehiiv 7:19 AM PT (email + web, all free subscribers, 1 recipient): https://usethissi.beehiiv.com/p/agent-native-is-open-source-plus-google-s-free-doc-reviewer
- Skipped this run (per task): beehiiv browser publish, X posting.
- X (@UseThisSI): daily post https://x.com/UseThisSI/status/2110737518102540346 (Agent-Native + Brief #2 link). Followed 10 builders (karpathy, simonw, levelsio, mckaywrigley, rauchg, amasad, Lovable, AndrewYNg, hwchase17, llama_index). Replied to 3 posts (simonw, hwchase17, cursor_ai); one cursor_ai reply with an unverifiable price claim was deleted and replaced.
- Mentions/notifications: no mentions or feedback. X notified the account got a blue checkmark (verified); unclear whether a paid X plan was turned on, so flag to Baz in the weekly report.
- Next: hit 75+ tools (68 now), keep daily posts, start building subscriber count.

## 2026-10-16 ~7:00 AM PT: weekday daily ops (scheduled)

- Releases added (source-confirmed): Meta Muse Spark Open (Oct 15), GitHub Agentic autofix GA (Oct 15), TwelveLabs Jockey GA (Oct 15), Chainguard Workspaces (Oct 14), Chainguard Checks (Oct 14).
- Tools added (5): Muse Spark Open (Meta), TwelveLabs Jockey, Chainguard Workspaces, Autonomous Harness, AWS Aidlc. Directory now **73 tools** / 10 use cases / 21 release rows (was 68 / 10 / 16).
- Price re-verify (Oct 16, official pages via WebFetch):
  - **Verified + last_checked set:** Bolt.new ($25 Pro), v0 ($30/user Plus; free 7 msg/day), Replit ($20 Core / $18 annual), Hostinger AI Builder ($2.99/mo 48-mo), Claude Code ($17 annual / $20 monthly via Pro), GitHub Copilot ($10 Pro; Free 2k completions), n8n (€20 Starter annual), Lindy (**$49.99/user/mo**, was $29.99), Zapier ($19.99 Pro annual), CrewAI (Free Basic / Enterprise custom; $99 gone), Tabnine (Contact sales — now Tricentis), ElevenLabs Starter ($1 first month until Oct 18).
  - **Not set (blocked/empty/client-rendered):** Windsurf/Devin pricing 404; Make (no $ in HTML); Manus (empty); Relevance AI (Enterprise-only HTML).
- SEO ship: `llms.txt` Recent releases + FAQ; regression in `test.py`.
- Rebuild + tests green. Newsletter #3 drafted (not published by executor).
- Experiment: Brief #3 subject A vs B — pending open/click.
- X: parent handles posts; notes 34 followers / @ishaan_gpt reply on Brief #2.
- Brief #3 published beehiiv 7:09 AM PT: https://usethissi.beehiiv.com/p/muse-spark-open-is-free-to-run-plus-github-agentic-autofix (email+web, 2 recipients / 0 outside).
- X (@UseThisSI): main https://x.com/UseThisSI/status/2111097288147788267; replies to ishaan_gpt, cursor_ai, vercel, simonw. Duplicate main deleted. No new mentions beyond ishaan_gpt; 2 new followers overnight.


## 2026-10-19 ~7:15 AM AZ: weekday daily ops (executor)

- Releases added (source-confirmed): Reflection Beam (Oct 16, reflection.ai + HF), Appwrite MCP Events (Oct 19).
- Tools: added Reflection Beam (AI coding assistant Alt). Directory now **74 tools** / 10 use cases / 23 release rows (was 73 / 10 / 21).
- Price/product recheck (Oct 19, official pages via WebFetch; last_checked set only when verified):
  - **Verified:** ElevenLabs ($6 Starter; $1 promo ended), Cursor ($8 Plus / $30 Premium), Exa ($10 free credits; Instant from $4/1k), HeyGen ($29 Creator), Pika ($10/$8 Starter), Browserbase ($20 Developer), LangGraph (MIT OSS), Mastra (Platform Starter $0 / Teams $250), Cline (free BYOK), Google Deep Review (2 free/wk), Google AI Studio / Argon ($2/$10 thru Nov 30 then $4/$20), Amp ($20 Individual), Roboflow Agent (product page), Snyk Evo (Evo needs Enterprise; Team $25 is non-Evo), BAND (no self-serve price), Fish Audio (homepage; /pricing 404).
  - **Not updated (JS-empty / no price):** Magic Patterns pricing page empty; CopilotKit CLiF left at Oct 14.
  - **Still never checked:** Relevance AI, Muse Code (Meta), Manus, Gemini agent (Google Cloud).
- Freshness after: **70/74 within 7d**, 4 never checked, 0 older.
- SEO ship: FAQPage JSON-LD on every use-case page + regression in test.py.
- Newsletter Brief #4 drafted and rendered green: newsletter/2026-10-19.md (do not publish; parent handles beehiiv).
- Experiment: Brief #4 subject A vs B row in ops/experiments.csv.
- Rebuild + tests + link check green. Push + optional IndexNow after commit.
- Skipped (parent): beehiiv publish, X posts / pain-point replies.

## 2026-10-19 ~7:00 AM AZ: weekday daily ops (scheduled)

- Directory: +1 Reflection Beam; 17 tools rechecked; +2 releases (Beam, Appwrite MCP Events). Tools **74**. Freshness **70/74** within 7d.
- Brief #4 published beehiiv (web fixed after empty HTML-snippet body): https://usethissi.beehiiv.com/p/reflection-beam-open-weights-plus-appwrite-mcp-events
- SEO: FAQPage JSON-LD on use-case pages. Commits c886bbd / a2e17c0.
- X main https://x.com/UseThisSI/status/2112187812644614525 + 1 builder reply + 5 pain-point replies. Followers 36.
- Experiment: Brief #4 subject A/B + pain-point reply tracking started.

## 2026-10-19 weekly review
- Week-of-Oct-12 scorecard logged (ops/weekly.csv). This week top priority: free launch listings into /quiz/ (ops/launch-listings.md). Vercel Web Analytics is live. beehiiv drops to Free ~Oct 27 (paste markdown, no custom HTML). Make/ElevenLabs pick reasons no longer cite affiliate terms.
