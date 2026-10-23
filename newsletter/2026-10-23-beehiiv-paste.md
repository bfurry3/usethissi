Subject: OpenAI ships a Decisions API, plus Mistral Voxtral 3
Preheader: OpenAI launched an API for fast yes-or-no and multiple-choice calls, Mistral shipped Voxtral 3, and Claude is now GA on Google Cloud.

(Paste everything below this line into the beehiiv default editor. Subject and Preheader go in beehiiv's own fields. No HTML blocks.)

---

Five minutes, only what matters if you build things.

## Today in 30 seconds
- **OpenAI Decisions API:** A new API for bounded choices, priced on input tokens only.
- **Mistral Voxtral 3:** Speech-to-text, text-to-speech and a voice agent API in public preview.
- **Claude on Google Cloud:** Anthropic-run Claude models are now generally available with Google Cloud billing.

## The big one
### OpenAI Decisions API: cheap, fast yes-or-no calls (Oct 22)
**What happened:** OpenAI made the Decisions API generally available. It answers bounded questions, like yes or no or pick one of these options, on GPT-6 Luna, and one request can hold up to 400 questions.
**Why it matters for builders:** Most agent and app logic is small judgment calls: is this email a lead, is this ticket urgent, does this row match. OpenAI says it is up to 10x faster than asking Luna the same thing through the Responses API, at $0.10 per 1M input tokens, $0.01 cached, and no output-token charge.
**The catch:** It only returns bounded answers, so it cannot write text or explain itself in prose. You still pay for every input token, so long context on every question adds up, and you should spot-check its calls before you let them trigger real actions.
**How to try it:** Take one filter you run today with a full chat prompt, rewrite it as a single yes-or-no question, and run 50 real examples through both to compare speed, cost and accuracy.
[Read the source](https://openai.com/index/decisions-api/)

## Quick hits
- **Claude on Google Cloud (Oct 23):** Claude models run by Anthropic are now generally available on Google Cloud at the same prices, with Google Cloud billing and IAM and day-one Claude Platform features such as skills and code execution. [Source](https://cloud.google.com/blog/products/ai-machine-learning/expanding-claude-availability-on-google-cloud)
- **1Password for Agents (Oct 22):** AI agents can sign in to sites without ever seeing your passwords. 1Password fills the login, and you approve each request on your own device. [Source](https://1password.com/press/2026/october/1password-for-agents-trust-layer-personal-ai-agents)
- **Pictory 3 (Oct 22):** Pictory's new AI video agent turns a brief, doc, URL, slide deck or audio file into a script, scenes and a preview video. New users start in Pictory 3 as it rolls out. [Source](https://pictory.ai/blog/introducing-pictory-3)

## Tool of the day
### Mistral Voxtral 3
**Use it for:** Transcription, text-to-speech and voice agents from one vendor, with EU, US or global endpoints, or self-hosting.
**Price:** Voxtral Mini TTS 3 is $13 per 1M characters. Batch transcription starts at $0.0035 per minute, and the voice agent API starts at $0.04 per minute. It is a public preview, so prices and limits can change.
**Why we like it:** One bill covers listening, speaking and the agent loop, and the EU endpoint helps if your users need their data kept in Europe.
[Try it on UseThisSI](https://www.usethissi.com/tools/mistral-voxtral-3/)

## Price watch
- **ElevenLabs:** The $1 first month on Starter is back until Nov 1, then $6/mo. Creator shows $11 for the first month, then $22/mo. [Source](https://elevenlabs.io/pricing)
- **Fish Audio:** The Drama 3 API launch price is $10 per 1M UTF-8 bytes until Nov 12, then $50. We had said characters, now fixed. The app's Plus plan is $11/mo billed annually or $15 monthly. [Source](https://docs.fish.audio/developer-guide/models-pricing/pricing-and-rate-limits)
- **Lovable:** The free plan gives 5 build credits a day but caps them at 30 a month. Pro is still $25/mo, or $21/mo billed annually. [Source](https://docs.lovable.dev/introduction/subscription-plans)
- **No other moves:** We rechecked 16 tools on their own pages today, including Cursor, Google Antigravity, HeyGen, Pika and Browserbase. None changed. [Full list](https://www.usethissi.com/tools/)

## One tip to try
**Turn fuzzy checks into yes-or-no questions:** Before you build an agent step, write the decision it makes as one line, like `Is this message asking for a price quote? Answer yes or no.` Short, bounded questions are cheaper, faster and easier to test than open-ended prompts on any model.

78 tools across 10 jobs, prices re-checked weekly: https://www.usethissi.com
