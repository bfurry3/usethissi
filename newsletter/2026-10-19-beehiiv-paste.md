Five minutes, only what matters if you build things.



## Today in 30 seconds
- **Reflection Beam:** 501B MoE open weights (23B active), Apache 2.0, 1M context, built for coding and agents.
- **Appwrite MCP Events:** Agents can subscribe to project events over MCP without polling.
- **ElevenLabs Starter:** The $1 first-month promo ended; Starter is back at $6/mo.

## The big one
### Reflection Beam open weights (Oct 16)
**What happened:** Reflection released Beam, a sparse MoE model with 501B total parameters and about 23B active, under Apache 2.0 on Hugging Face. It targets coding, reasoning, and long-horizon agent work with a 1M-token context.
**Why it matters for builders:** You get frontier-scale open weights you can self-host, fine-tune, or hit via partners (Ollama Cloud `beam:cloud`, Fireworks, Together, OpenRouter, Reflection's own API beta, and more). Day-zero support in transformers, vLLM, and SGLang, plus an open Mirror CLI harness.
**The catch:** Weights are free, but self-hosting still needs serious GPUs. The practical NVFP4 path is roughly four B200-class cards; smaller machines should use a hosted endpoint instead.
**How to try it:** Run `ollama run beam:cloud`, or pull weights from the [Hugging Face Beam collection](https://huggingface.co/blog/reflection-beam) and point Mirror / OpenCode / Claude Code at a partner endpoint.
[Read the source](https://reflection.ai/blog/beam-is-available)

## Quick hits
- **Appwrite MCP Events (Oct 19):** Agents on the Appwrite MCP server can subscribe to six launch events (new users, failed functions, finished deployments, new rows, uploaded files) via stream or signed webhooks. No more polling. [Source](https://appwrite.io/changelog/entry/2026-10-19)
- **Claude Code idle compaction:** Long terminal chats (200K+ tokens) idle about 54 minutes get compacted before the one-hour prompt cache expires. Toggle it in `/config`, or set `"idleCompaction": false`. [Source](https://code.claude.com/docs/en/changelog)
- **Ollama Cloud Beam:** `beam:cloud` is live with a 1M context window, so you can test Beam without racking GPUs. [Source](https://ollama.com/library/beam)

## Tool of the day
### Browserbase
**Use it for:** Cloud browsers and Stagehand so agents can click through real websites at scale.
**Price:** Free plan to start; Developer from $20/mo (100 browser hours, then $0.12/hr).
**Why we like it:** Clear concurrency and browser-hour limits, plus a Model Gateway so you are not babysitting headless Chrome yourself.
[Try it on UseThisSI](https://www.usethissi.com/tools/browserbase/)

## Price watch
- **ElevenLabs Starter:** $1 first-month promo ended after Oct 18. Starter is $6/mo (about $5/mo annual). Creator still shows $22 first month (50% off), then $11/mo. [Source](https://elevenlabs.io/pricing)
- **Gemini 4 Argon API:** Still $2/$10 per 1M tokens through Nov 30, then $4/$20 starting Dec 1. [Source](https://ai.google.dev/gemini-api/docs/pricing)
- **Krea Basic:** Confirmed $5.25/mo annual / $9 monthly (Pro $21 / $35). [Source](https://www.krea.ai)

## One tip to try
**Leave a long Claude Code session overnight:** If a 200K+ token terminal chat will sit idle near the one-hour cache window, let idle compaction run (or turn it off in `/config` if you need the full history intact). That avoids paying to reprocess the whole thread on your next message.

74 tools across 10 jobs, prices re-checked weekly: https://www.usethissi.com
