# UseThisSI: a growth and revenue plan that lasts (Hormozi offer + Google at scale)
Researched and written Oct 17-18, 2026 (America/Phoenix, MST). Research and plan only: nothing here has been built, shipped, bought, or sent.

**Rules for this doc.** Every outside number has a source URL. Anything marked **[EST]** is my own estimate or a planning assumption, not a sourced fact. Our internal numbers (73 tools, 36 checked within 7 days, 0 real subscribers, 36 X followers) come from `data.csv`, `metrics.csv`, and the ops log as of Oct 17. Hormozi's books are paraphrased with short quotes only.

Companion doc: `research/2026-10-18-ai-monetization-on-x.md` (who makes money in this niche, and how).

---

## 0. The one-paragraph answer for Baz

You're right: subscribers come first and money comes after. Hormozi's own rule is "give away the secrets, sell the implementation." So the plan is to (1) give away the most useful thing we have, a price-checked "which AI tool for which job" kit, in exchange for an email; (2) make Google our long-term, faceless growth engine by turning our tool data into honest, always-current pages (pricing, comparisons, alternatives, free options) that each push readers into that kit; and (3) turn money on one rung at a time as the list grows: labeled affiliate links now, featured listings around 1K subscribers, sponsors from about 2.5K-10K, and a paid "do it for me" stack setup later. Durability comes from the one thing big competitors can't easily copy without hurting their own ad money: **current, dated, honest prices and verdicts.** Freshness is both our Google ranking edge and our trust edge.

---

## Part A. Hormozi applied to UseThisSI

### A1. The frameworks we're using (paraphrased, with sources)

**Value Equation ($100M Offers).** Value = (Dream Outcome × Perceived Likelihood of Achievement) ÷ (Time Delay × Effort & Sacrifice). Push the top two up and the bottom two toward zero. Hormozi argues the bottom half (speed and ease) is where the real advantage is, because anyone can make big promises. One line that matters for a free newsletter competing with free content: "fast beats free."
- Hormozi's own talk transcript: https://hormozi.blog/this-one-equation-will-make-you-rich/
- Chapter summaries: https://www.devendavis.com/book-summaries/100m-offers ; https://www.jamesgibbins.com/100m-offers/ ; https://sobrief.com/books/100m-offers

**Grand Slam Offer.** Build the offer by (1) naming the dream outcome, (2) listing every obstacle the customer hits on the way, in the order they'd hit it, (3) turning each obstacle into a solution, (4) packaging the solutions as named bonuses (an offer split into parts and stacked feels more valuable than the same thing as one lump), then (5) enhancing with scarcity (limited units), urgency (limited time), guarantees (reverse risk), and a name. Hormozi insists scarcity and urgency be real and enforced.
- https://alexhormozi.wiki/frameworks/grand-slam-offer-anatomy ; chapter notes: https://github.com/Jason2Brownlee/AuthoritySite/blob/main/resources/100m_offers.md
- **MAGIC naming:** Magnetic reason, Avatar, Goal, Interval, Container word (e.g., "kit", "blueprint", "system"). Use 3 to 5 of them. Same sources.

**$100M Leads.**
- **Core Four:** warm outreach (1-to-1, people who know you), posting content (1-to-many, warm), cold outreach (1-to-1, strangers), paid ads (1-to-many, strangers). https://manassaloi.com/booksummaries/2025/07/27/million-leads-hormozi.html ; https://businessbookclub.substack.com/p/free-book-summary-100m-leads-by-alex
- **Lead magnets:** a complete solution to a narrow problem that reveals the next problem your paid offer solves (his "salty pretzel" analogy: free pretzels make you thirsty, the bar sells drinks). Make it good enough to charge for. "Give away the secrets, sell the implementation." Same sources, plus his own audiobook episode: https://podscripts.co/podcasts/the-game-with-alex-hormozi/part-2-engage-your-leads-100m-leads-book
- **Rule of 100:** 100 primary actions a day for 100 days (e.g., 100 minutes of content a day). https://manassaloi.com/booksummaries/2025/07/27/million-leads-hormozi.html
- **More, better, new:** do more of what works before trying new channels. https://bestbookbits.com/100m-leads-how-to-get-strangers-to-want-to-buy-your-stuff-by-alex-hormozi-book-summary/
- **Lead getters:** people who run the Core Four for you: customer referrals, employees, agencies, affiliates. https://hormozigame.com/card/lead-getters/ ; his episode on affiliates: https://podscripts.co/podcasts/the-game-with-alex-hormozi/part-10-affiliates-and-partners-100m-leads-book
- Acquisition.com gives away its offer and lead-gen courses free: https://www.acquisition.com/training

### A2. The Grand Slam free offer

**The dream outcome (for a busy builder):** "I know exactly which AI tool to use for this job, what it really costs today, and I'm using it within the hour, without wasting a weekend on trials or getting surprised by a bill."

**Name (MAGIC):** **The Builder's 5-Minute AI Stack Kit**
- Subtitle: *Pick the right AI tool for any job in 5 minutes. Real prices, checked every week. Free.*
- Magnet: free + price-checked. Avatar: builders. Goal: right tool for the job. Interval: 5 minutes. Container: kit.
- Edition label for honest urgency: "October 2026 edition" (a new edition each month).

**Obstacles → solutions → value stack.** Each bonus answers one real obstacle, in the order a builder hits them. All are built from data we already have; nothing new to buy.

| # | Obstacle (in order) | Stack item (what they get) | Built from |
|---|---|---|---|
| Core | "There are thousands of AI tools; I don't know which one to use." | **The AI Stack by Job sheet**: one page per job (10 jobs today), with our Top Pick, the bench, starting price, free-tier limits, and the date we last checked each one. Delivered as a Google Sheet + PDF. | `data.csv` (73 tools, 10 use cases) |
| B1 | "I don't want to pay yet." | **The $0 Stack**: how to do each job on free tiers only, with the real limits spelled out (51 of 73 listed tools show a free tier). | `free_tier` column |
| B2 | "I have a budget and a role, not a job list." | **4 starter stacks under $50/mo**: Solo Founder, Marketer, Developer, Creator. Each has a monthly total. | price column |
| B3 | "I'll pick one and then it changes price on me." | **Price-change alerts** in the weekday brief: when a listed tool's price or free tier changes, subscribers hear first. | daily freshness checks |
| B4 | "Even with the right tool, setup eats my afternoon." | **First-hour quickstarts**: one setup tip per Top Pick so you get a result in the first session. | tips already written in `newsletter/bs.py` |
| B5 | "I've wasted money on hyped tools before." | **The Skip List**: tools we'd skip right now, and why (unverified pricing, sales-only, rebranded, beta-only). | `unverified` flags in `data.csv` |
| Ongoing | "I can't keep up." | **The 5-minute weekday brief**: what launched, what changed, what to try today. | existing brief |

**Guarantee (adapted for a free offer; it reverses the real risk, which is wasted time and wrong info):**
- "Found a wrong price in the kit? Reply and we'll fix it within 24 hours and thank you in the brief." This is our charter's "fix fast" value made public.
- "Every brief reads in 5 minutes or less. One-click unsubscribe, any time."

**Scarcity and urgency (honest only):**
- Urgency: monthly editions. Subscribers get each new edition automatically; the public site keeps only the current kit's teaser. This is Hormozi's "rolling seasonal urgency", and it's real because prices genuinely change.
- No fake countdowns, no fake "only 100 spots."

**Value Equation score vs. the alternative (googling "best AI tool for X" and reading sponsored listicles):**

| Driver | Typical listicle or big directory | Our kit |
|---|---|---|
| Dream outcome | "Here are 50 tools" | "Here's the one to use for this job, and what it costs today" |
| Perceived likelihood | Unclear what's paid placement; prices often stale | Dated prices, labeled affiliate links, a public correction promise |
| Time delay | An evening of reading and trials | 5 minutes to a pick; quickstart gets a result in the first session |
| Effort & sacrifice | Compare tabs yourself, risk surprise bills | Free-tier limits and monthly totals already worked out |

**Where it's delivered:** beehiiv's welcome email (available on the Free plan) links to the kit. The Free plan doesn't include multi-step automations or the referral program; those need Lite (see A4). Source on Free vs. Lite features: https://www.beehiiv.com/blog/email-marketing-pricing ; https://facelessfuel.com/beehiiv-pricing/ (third-party, checked Oct 8, 2026).

**Existing asset to repurpose:** `newsletter/builder-stack.pdf` (the 25-tool "Builder Stack") is already designed. It needs (a) the old `usethissi.vercel.app` URLs swapped for `www.usethissi.com`, (b) refreshed prices, and (c) the "At 10 referrals you get a shout-out" line removed or made trackable. That line promises a referral reward we can't track on beehiiv Free, which conflicts with "honest".

### A3. The value ladder: free → money (with trigger points)

The principle from the companion doc and Hormozi: monetize in order of trust. Each rung turns on only at its trigger. Prices for featured listings and sponsors are benchmarked to competitors; ours are **[EST]** starting points.

| Rung | What | Price | Turns on when | Values guardrail | Benchmark source |
|---|---|---|---|---|---|
| 0 | **5-Minute AI Stack Kit + weekday brief** | Free | Now | n/a | Hormozi lead-magnet principle |
| 1 | **Labeled affiliate links** on tools we already recommend | Commission. Examples already in `data.csv`: Lovable up to $100 one-time per first subscriber (Impact); Bolt.new 15% of payments, capped $50 per referral (Cello). 14 of 73 listed tools show a program. | **Now, at 0 subscribers.** Blocked only on Baz's payout details. | Only tools we'd pick anyway; ranking never changes because of a commission; "affiliate" label on every link | Matt Wolfe's early income was mostly affiliates (companion doc, row 5) |
| 2 | **Low-ticket product: "AI Stack Kit Pro"** (role-specific stacks, setup checklists, prompt packs, a quarterly price-history file) | $19-29 one-time **[EST]** | ~300-500 subscribers **and** 10+ reader replies asking for more depth **[EST]** | Free kit stays genuinely complete; Pro is depth, not the missing half | beehiiv says digital products carry a 0% platform fee and are on every plan: https://www.beehiiv.com/blog/beehiiv-pricing-2026. Note: a paid *subscription* "bombed" at Superhuman (companion doc), so this is a one-time product, not a paywall. |
| 3 | **Featured tool slot** on the directory + in the brief, clearly labeled | $49-99/week **[EST]**; max 1-2 slots a week (real scarcity) | ~1,000 subscribers or ~5,000 monthly site visitors **[EST]** | Only tools we'd recommend; never changes the Top Pick | TAAFT $49 basic / $437 max; Futurepedia $497 enhanced (companion doc rows 3-4) |
| 4 | **Newsletter sponsors** (one main slot) | ~$250/issue at ~10K readers, raised when it sells out | beehiiv Ad Network from ~1-2.5K subs (needs Lite); direct sponsors from ~10K | Labeled "Sponsor"; only products we'd use | Superhuman opened at 10K readers, ~$250/ad, sold out in 24h **[OLD, 2024]**: https://inboxcollective.com/the-rise-of-the-100k-newsletter-operator/ ; beehiiv Lite lists "Ad monetization, avg. $39/mo": https://www.beehiiv.com/pricing |
| 5 | **Paid recommendations (earning side)** | beehiiv pays per verified sub you send to another newsletter (beehiiv keeps 20%) | ~2,500 subs, on Lite | Only newsletters we'd read | https://www.beehiiv.com/blog/guide-to-free-and-paid-recommendations-in-beehiiv |
| 6 | **"Implementation": AI Stack Audit / Done-for-you Stack Setup** (async, written, faceless: reader fills a form; we deliver a stack, setup steps, and a monthly cost plan) | Audit $149; setup $500-1,500 **[EST]** | Pilot at ~1,000 subs with 5 beta clients at a discount; scale at 2,500+ **[EST]** | Conditional guarantee: "if your stack doesn't save you an hour a week in 30 days, full refund" **[EST, needs Baz]** | Hormozi "sell the implementation"; Sergiu sold done-for-you directory submissions after a free list, $10K in 4 months **[OLD, self-reported]** (companion doc row 9) |

**What "lasting" means here:** rungs 1, 3 and 4 compound with traffic and list size; rung 6 has the highest margin but doesn't need a face because delivery is written. Nothing on the ladder needs paid ads.

**Illustrative revenue math (all [EST] assumptions, to be replaced by real data once analytics are on):** if Google sends 5,000 visitors a month and 10% click out to a tool, that's 500 outbound clicks. If 2% of those sign up for a paid plan at an average affiliate payout of $30, that's about $300/month from affiliates alone. One featured slot at $49/week adds ~$200/month. None of these rates are sourced; they're placeholders to show how the levers multiply.

### A4. Core Four, lead getters, and the beehiiv referral program, without a face

| Core Four channel | What it means for us | Faceless? | Who does it |
|---|---|---|---|
| **Warm outreach** (1-to-1, warm) | (a) Reply to every mention/reply on @UseThisSI within the day. (b) Optional: Baz sends one personal note to builder friends with the kit link (I draft; he decides). No DMs from @UseThisSI (standing rule). | Yes for (a); (b) is Baz's choice | Al / Baz |
| **Content** (1-to-many, warm) | Daily X post (one tool, real price, last-checked date), useful replies on big builder accounts, weekly 10-15s Short, the weekday brief, and **SEO pages (Part B)**. Every piece ends with one soft CTA to the kit. | Yes | Al |
| **Cold outreach** (1-to-1, cold) | (a) Email small AI and builder newsletters to set up free beehiiv recommendation swaps. (b) Email tool makers: "your pricing page and ours, here's your listing; tell us if anything changed." That earns corrections, links, and future featured-slot leads. (c) Free directory submissions: Product Hunt, Indie Hackers, BetaList. | Yes (brand voice) | Al drafts; **each outbound email type needs Baz's OK before first send** (standing rule: never send unasked) |
| **Paid ads** (1-to-many, cold) | Off. Charter: no paid ads until affiliate income covers them. First paid channel later: beehiiv paid recommendations at a CPA (about $2-3 per sub per the companion doc), funded only from affiliate revenue. | Yes | Later, Baz approval |

**Rule of 100, adapted for an AI operator (daily quota, [EST]):** ~100 primary actions a day across 1 X post, 10-20 genuinely useful replies, 1-2 SEO pages built or upgraded, 10+ tool rechecks, 1 brief (weekdays), and outreach drafts. Stay within X's automation rules: no bulk or repetitive replies.

**Lead getters (people who get leads for us):**
- **Customer referrals = the beehiiv referral program.** Readers earn rewards at milestones (e.g., 1 referral: the "Skip List" deep dive; 3: Kit Pro free; 10: a shout-out in the brief). **It needs a paid plan:** "Plan: All Paid Plans", with Lite allowing 3 milestones (https://www.beehiiv.com/support/article/13090888705943, updated Oct 4, 2026). Lite is $49/mo billed yearly or $59 month-to-month at 1,000 subscribers (https://www.beehiiv.com/blog/email-marketing-pricing, checked Oct 13, 2026). **That's over our $50/month cap, so it needs Baz.** Recommendation: turn it on once we hit ~250-500 subscribers or once affiliate income covers it, whichever comes first.
- **Affiliates of our own:** once Kit Pro exists, offer other small newsletters 30-50% **[EST]** to promote it.
- **Employees/agencies:** our "employees" are the AI routines (daily ops, weekend X, weekly Short).
- **Free now:** the beehiiv recommendation network works on the Free plan (https://www.beehiiv.com/pricing).

---

## Part B. Scaling on Google (programmatic SEO from `data.csv`)

### B1. Where we stand today (from the repo)
- 90 HTML pages built: home, about, new, submit, 73 tool pages (`/tools/<slug>/`), 10 use-case pages (`/use-cases/<slug>/`), and index pages. `sitemap.xml` and `robots.txt` exist; IndexNow key is live.
- Schema in use: `ItemList` on use-case pages, `SoftwareApplication` on tool pages, `WebSite` on home.
- Gaps found:
  1. `sitemap.xml` uses one site-wide date for every URL's `<lastmod>`. Google says it uses `lastmod` only "if it's consistently and verifiably accurate" and it should reflect the last significant change to that page (https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap). Fix: per-page `lastmod` = that tool's `last_checked`.
  2. Our `SoftwareApplication` markup lacks `offers.price` and a rating/review. Google lists both as **required** for the software-app rich result (https://developers.google.com/search/docs/appearance/structured-data/software-app). We should add `offers` (real prices) and **only add a review if we adopt an honest, documented scoring rubric.** Never invent ratings.
  3. Only 36 of 73 tools have a `last_checked` date, and 22 have no free-tier info. Freshness gaps are our biggest content-quality risk.
  4. Search Console isn't connected, so we can't see indexing or queries.
  5. **IndexNow doesn't reach Google.** It notifies Bing, Yandex, Seznam, Naver and Yep (https://www.indexnow.org/faq). For Google, the levers are the sitemap, Search Console, and internal links.

### B2. The rules we design around (Google's own docs)
- **Scaled content abuse:** "when many pages are generated for the primary purpose of manipulating search rankings and not helping users… no matter how it's created." Examples include using AI to generate many pages without adding value, and "creating many pages where the content makes little or no sense to a reader but contains search keywords." https://developers.google.com/search/docs/essentials/spam-policies
- **Doorway abuse:** "creating substantially similar pages that are closer to search results than a clearly defined, browseable hierarchy." Same page.
- **Thin affiliation:** affiliate pages that copy merchant descriptions without added value. Google explicitly names "additional information about price… navigation of products or categories, and product comparisons" as what *good* affiliate pages offer. Same page. **That's our exact format.**
- **AI content:** fine if it adds value, but must be fact-checked, including titles and structured data; consider telling readers how content was made. https://developers.google.com/search/docs/fundamentals/using-gen-ai-content
- **Paid links:** affiliate and sponsor links must carry `rel="sponsored"` (or `nofollow`). Same spam-policies page.
- **FAQ rich results are gone for everyone** as of May 7, 2026. FAQ markup is harmless but earns nothing visible in Google (https://www.searchenginejournal.com/google-drops-faq-rich-results-from-search/574429/). We keep on-page FAQs for readers and skip relying on FAQ schema.

### B3. Page types, templates, and quality gates

Each page type publishes **only** when its quality gate passes, generated by `build.py`. Pages that fail the gate either don't get built or get `noindex` until the data is filled in.

| Page type | URL | Title template | Unique value on the page | Quality gate (must pass to publish) |
|---|---|---|---|---|
| **Best AI tool for [job]** (upgrade existing use-case pages) | `/use-cases/<job>/` | "Best AI tool for [job] (checked [Mon YYYY])" | Our Top Pick + why, the bench, comparison table (price, free-tier limits, best for, skip if), "what changed this month" | ≥3 tools with verified price and checked ≤30 days |
| **[Tool] pricing (updated [date])** | `/tools/<tool>/pricing/` | "[Tool] pricing (checked [date]): plans, free tier, real cost" | Every plan tier, free-tier limits, **price-change history** (our moat), "what you'll actually pay" for 2-3 usage profiles, link to official page | Verified price **and** checked ≤30 days **and** ≥2 tiers recorded. Otherwise the pricing info stays a section on the main tool page, not a separate URL (avoids near-duplicates). |
| **[Tool] vs [Tool]** | `/compare/<a>-vs-<b>/` | "[A] vs [B] ([Mon YYYY]): price, free tier, which to pick" | Side-by-side table, "pick A if… / pick B if…", our verdict, price difference per month | Same use case; both verified and fresh; written verdict present; **only pairs with real search demand** (Top Pick vs each Alt, plus well-known pairs). Never all combinations. |
| **[Tool] alternatives** | `/tools/<tool>/alternatives/` | "[N] [Tool] alternatives (cheaper, free, or better for X)" | Ranked alternatives in the same job with *why switch*: cheaper, free tier, specific feature | Tool is well known enough to be searched, and ≥3 verified alternatives |
| **Free AI tools for [job]** | `/free/<job>/` | "Free AI tools for [job] (limits checked [date])" | Only tools with a real free tier, with exact limits and the catch (e.g., non-commercial) | ≥3 tools with a verified free tier in that job |
| **AI tools under $20 for [role]** | `/stacks/<role>-under-20/` | "AI tools under $20/mo for [solo founders / marketers / developers / creators / game devs]" | A role stack (cross-job) with a monthly total and free fallbacks | ≥5 tools ≤$20 with verified prices across ≥3 jobs |

**Data we need to add to make pages non-thin (not in `data.csv` yet):** `best_for`, `skip_if`, `verdict` (1-2 sentences, written from the official page plus hands-on checks), `free_tier_limits` (normalized), `plans` (tier name + price), `price_history` (date, old → new), and `checked_by_method` (official page / signup / docs). Every new page gets a short "How we check" line (Google's AI-content guidance recommends telling readers how content was made).

### B4. Internal linking
- Hub and spoke: Home → use-case hubs → tool pages → pricing / alternatives / vs pages. Every spoke links back to its hub and to 2-3 siblings (e.g., "Cursor vs Copilot", "Cursor alternatives").
- Breadcrumbs on every page (plus `BreadcrumbList` schema).
- "Recently changed prices" module on home and hubs that links straight to updated pricing pages. This spreads freshness signals and gives Google a reason to recrawl.
- The weekday brief archive links to the pages it mentions (and vice versa), so news pages feed the evergreen pages.

### B5. Schema
- `ItemList` on hubs, free and stacks pages (already partly in place).
- `SoftwareApplication` on tool and pricing pages with `offers` (price, priceCurrency, plus `priceValidUntil` only if the vendor states it). Add `review` only with an honest, published rubric.
- `dateModified` / `datePublished` on every page (via `WebPage` or `Article`), equal to the real `last_checked`. Matching visible "Last checked" text.
- `BreadcrumbList` everywhere.
- `FAQPage`: optional, for readers and other engines; no Google rich result (see B2).
- Validate with the Rich Results Test before shipping (Google's step 3 in the software-app doc).

### B6. Sitemaps, IndexNow, and recrawl
- Split sitemaps by type (`sitemap-tools.xml`, `sitemap-compare.xml`, …) under a sitemap index, so Search Console shows indexing per page type (Google supports sitemap indexes and multiple sitemaps; same build-sitemap doc).
- Per-URL `lastmod` = real change date only. Don't bump dates on pages that didn't change.
- IndexNow ping (existing key) on every changed URL, for Bing and partners.
- Search Console: submit the sitemap index and use URL Inspection on new hubs. **Needs Baz's Google login once** (see C3).

### B7. Freshness as the moat
- Google weighs `lastmod` only if it's accurate, and we intend to be the site whose dates are always true.
- Readers searching "[tool] pricing" mostly want *today's* price. A visible "checked [date]" plus a change log beats a 2024 listicle.
- Operating rule: every published tool rechecked at least every 30 days (charter); pricing pages for affiliate tools and Top Picks at least every 7 days. A page that goes over 45 days without a check is automatically flagged "may be out of date" in the UI **[EST threshold]**.

### B8. How many quality pages can we make from today's data?

Counted from `data.csv` on Oct 17 (73 tools across 10 jobs). "Verified price" = price field not marked unverified/contact sales (57 tools); 27 tools have both a verified price and a last-checked date.

| Page type | Raw combinations | Publish after quality gate **today** | Ceiling after the 30-day freshness sprint **[EST]** |
|---|---|---|---|
| Best for [job] (existing hubs, upgraded) | 10 | 10 | 10 |
| [Tool] pricing (separate pages) | 73 | ~27 (verified + dated) | ~50-57 |
| [Tool] vs [Tool] (same job, both verified) | 157 | ~20 (Top Pick vs Alt, demand-checked) | ~40-50 |
| [Tool] alternatives | 51 eligible | ~15 (well-known tools only) | ~25-30 |
| Free AI tools for [job] | 9 jobs with ≥3 free tools | 9 | 9-10 |
| Under $20 for [role] | 5-6 roles | 5 | 6 |
| **Total new or upgraded** | ~300 | **~85** | **~140-160** |

Plus the 73 existing tool pages (those with unverified data get improved first; any we can't verify get `noindex` until we can). **Anything beyond ~160 needs more real data** (more tools, or hands-on testing notes). Generating the remaining ~150 raw combinations would be exactly the "substantially similar pages" Google calls doorway and scaled-content abuse.

### B9. Realistic timeline: indexing to traffic, for a new domain

Facts:
- Google: "it may take several days after publishing a page for Google to find and crawl it" (https://developers.google.com/search/docs/appearance/structured-data/software-app). Submitting a sitemap "is merely a hint" (build-sitemap doc).
- Ahrefs, 2025 study: only 1.74% of newly published pages reach the top 10 within a year (6.11% in a cleaner sample of English, non-empty pages). Of pages that did rank, 40.82% got there within a month. Higher-volume keywords take longer. 72.9% of top-10 pages are over 3 years old; the average #1 page is 5 years old. If a page isn't top 10 after ~6 months, update it. https://ahrefs.com/blog/how-long-does-it-take-to-rank-in-google-and-how-old-are-top-ranking-pages/

Our estimate **[EST]** for usethissi.com (registered mid-October 2026, no backlinks yet):

| Window | What to expect |
|---|---|
| Weeks 1-4 after Search Console + sitemap | Hubs and a portion of tool pages indexed; first impressions on long-tail queries ("[small tool] pricing", "[tool] free tier limits") |
| Months 2-3 | First steady clicks from low-competition pricing, alternatives and vs pages: tens to low hundreds a month |
| Months 4-6 | Pages that earned links and kept fresh dates climb; hundreds to low thousands of clicks a month if we keep quality high and earn some links |
| 6-12 months | Competitive "best AI tool for X" terms become possible. Older sites dominate these. |

Faster paths in the meantime: Bing via IndexNow, X, newsletter swaps, and directory listings, which also earn the first backlinks.

### B10. Turning each page into subscribers
- **Inline offer** right after the comparison table: "Get the full 5-Minute AI Stack Kit: every job, every price, checked weekly. Free." Using the existing beehiiv embed.
- **Content upgrade per page type:** pricing pages offer "Get alerted when [Tool] changes price" (subscribe with that tool tagged); vs pages offer "Get our full [job] stack"; free pages offer "The $0 Stack".
- **Scroll CTA** at ~60% depth (a slim, dismissible bar, no full-screen popup). An exit prompt on desktop only, once per visitor, so it doesn't feel spammy. Measure whether it helps.
- **Sticky footer link** on mobile: "Free AI Stack Kit".
- **Attribution:** keep beehiiv's attribution script (already on site) so we can see which page types produce subscribers.
- **Measurement constraint:** Vercel Web Analytics is free on Hobby (50K events/month) but **custom events (outbound and CTA clicks) are Pro-only** (https://vercel.com/docs/analytics/custom-events ; https://vercel.com/docs/analytics/limits-and-pricing). Free alternative for click tracking: Umami Cloud's free Hobby plan (100K events/month, custom events included; https://umami.is/pricing). That's $0 and within budget.

---

## Part C. 30/60/90-day roadmap (Oct 19, 2026 → Jan 16, 2027)

Targets are goals, not forecasts. **[EST]** throughout. Spend stays at $0 unless Baz approves an item.

### Days 1-30 (Oct 19 → Nov 17): offer + foundation
| Week | Milestones | Target by end of week |
|---|---|---|
| W1 Oct 19-25 | Refresh and rename the Builder Stack PDF into the 5-Minute AI Stack Kit (new domain, fresh prices, remove the untrackable referral promise). Wire beehiiv welcome email to deliver it. Kit CTA on every page. Pinned X thread. Per-page sitemap `lastmod`. Turn on Vercel Web Analytics + Umami. Freshness sprint starts (tools without dates first). | 25 real subs (charter goal); 50 of 73 tools checked ≤30d |
| W2 Oct 26-Nov 1 | Add data columns (best_for, skip_if, verdict, plans, price_history). Upgrade 10 hubs. Search Console live (Baz). Submit to Product Hunt / Indie Hackers / BetaList (free). | 40 subs; 73/73 checked ≤30d; sitemap submitted |
| W3 Nov 2-8 | Ship first ~25 pricing pages (verified + fresh only) and 9 "free tools for [job]" pages. 3 newsletter-swap emails drafted for Baz's OK. | 60 subs; ~45 pages indexed |
| W4 Nov 9-15 | Ship first ~10 vs pages and 5 role stacks. First monthly kit edition (Nov). | 100 subs; ~60 indexed; first search impressions |

### Days 31-60 (Nov 17 → Dec 16): scale pages + first dollar
| Week | Milestones | Target |
|---|---|---|
| W5 | Alternatives pages (~15). Affiliate links live on approved programs (if Baz has sent payout info). | First affiliate click |
| W6 | Second batch of vs pages (demand-checked). Outreach to tool makers about their listings (after Baz approves the template). | 150 subs |
| W7 | Prune or `noindex` pages with zero impressions after 4 weeks and thin data. Strengthen winners. | ~100 indexed |
| W8 | Decide on beehiiv Lite (referral program) based on list size and affiliate income. Ask Baz. | 300 subs; **first affiliate dollar** (if payout info by W2) |

### Days 61-90 (Dec 16 → Jan 16): compound + next rungs
| Week | Milestones | Target |
|---|---|---|
| W9-10 | Price-change alert content upgrades per tool. "Year in AI tool prices" roundup (a linkable asset for backlinks). | 450 subs |
| W11 | Kit Pro ($19-29) spec and outline, for Baz's go/no-go once there's ~300-500 subs and reader demand. | ~140 indexed |
| W12-13 | "Advertise / Featured tool" waitlist page (no sales until ~1K subs). Q1 plan. | 750 subs; 300-1,000 search clicks/month; affiliate revenue covering at least one tool cost |

**Metrics to track (all already in or added to `metrics.csv`):** real subscribers, signups by page type, indexed pages (Search Console), search impressions and clicks, outbound and affiliate clicks, affiliate revenue, tools checked ≤7d / ≤30d, price changes caught.

### C3. Autonomous vs. needs Baz

| I do it (routine, inside the charter) | Needs Baz |
|---|---|
| Kit build and refresh, site pages, schema, sitemaps, IndexNow, internal links | **Affiliate payout details** (PayPal or bank). This is the single blocker on the first dollar. |
| Freshness rechecks, price-change logging | **Search Console verification:** a one-time Google login. I can add the DNS TXT record on Vercel myself; adding the property needs his Google account. I'll bundle it into one weekly-scorecard line, no separate pings. |
| Daily X, weekly Short, the brief, replies | **First send of each new outbound email type** (newsletter swaps, tool-maker notes) |
| Umami (free) + Vercel Web Analytics (free) setup | **beehiiv Lite** ($49/mo yearly or $59 monthly, over the $50/month cap) for the referral program and automations |
| Free directory submissions where no paid account is needed | Any paid listing over $25 (e.g., TAAFT $49 basic) |
| Drafting Kit Pro, featured-listing terms, audit offer | **Launching any paid product or service, guarantees, and featured-listing sales** (new revenue lines = reputation and partnership risk under the charter) |

### C4. Budget check
- Planned spend in 90 days: **$0** (domain already paid; Vercel Hobby, beehiiv Free, Umami Hobby, and directory listings are all free).
- Optional items needing approval: beehiiv Lite ($49-59/mo), TAAFT basic listing ($49 one-time). Both exceed a limit and stay off unless Baz says yes.

---

## Top 5 actions for the next 7 days (Oct 19-25)
1. **Ship the 5-Minute AI Stack Kit** (refresh `builder-stack.pdf` + a Sheet version; new domain; fresh prices; drop the untrackable referral line). Deliver it in the beehiiv welcome email, add the kit CTA to every page, and pin an X thread about it.
2. **Freshness sprint:** date-check the 37 tools with no `last_checked`, fill free-tier gaps, and get to 73/73 checked within 30 days. Fix per-page sitemap `lastmod` and add real `offers` to `SoftwareApplication`.
3. **Turn on measurement:** Vercel Web Analytics (free) + Umami free for outbound and CTA clicks, so the scoreboard shows signups by page.
4. **Ask Baz for two things in one message:** affiliate payout details and a one-time Search Console login. Those are the only blockers to the first dollar and to Google data.
5. **Build the data columns and templates** for pricing, free-for-[job] and vs pages, with quality gates in `build.py`. Then publish the first batch only for tools that pass (target ~25 pricing + 9 free pages in Week 2-3).
