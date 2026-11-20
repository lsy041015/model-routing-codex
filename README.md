<p align="center">
  <img src="assets/model-routing-codex-banner.png" alt="model-routing-codex — Codex CLI subagents routed to the right GPT model" width="560">
</p>

# model-routing-codex

The Codex CLI version of [model-routing](https://github.com/lsy041015/model-routing): each subagent task goes to the GPT model and reasoning effort that fits it, instead of everything running on the same one.

| Task | Role | Model / effort |
|---|---|---|
| Find files, symbols, call sites, config, log lines | `scout` | gpt-6.1-terra / low |
| Facts or summary from files, logs, pasted docs, a known URL | `reader` | gpt-6.1-terra / high |
| Facts found via mail, chat, drive or many web pages | `extractor` | gpt-6.2-sol / medium |
| Scoped bug fix or feature (2-5 files, tests) | `implementer` | gpt-6.2-sol / high |
| Standard code review | `reviewer-lite` | gpt-6.2-sol / high |
| Hard debugging, concurrency, cross-module, UI, no tests; architecture, major refactor or migration; security, data loss, production or hardware control, release review | `implementer-hard` | gpt-6.2-sol / xhigh |
| Hard, architecture or critical review or audit | `reviewer` | gpt-6.2-sol / xhigh |
| Hard task after sol xhigh failed twice | `astra-hard` | gpt-6.2-astra / high |
| Architecture or critical task after sol xhigh failed twice | `architect` | gpt-6.2-astra / xhigh |
| Easy 1-2 file changes, planning, integration, final checks | main session | gpt-6.2-sol / medium |

Read-only roles (`scout`, `reader`, `extractor`, `reviewer-lite`, `reviewer`) run in a read-only sandbox.

Why these: terra high has the lowest hallucination rate, so it only does text extraction. Hard work starts on sol xhigh at about a quarter of astra's cost, and astra is the fallback. The main session stays on sol medium because it re-sends the whole conversation every turn; high costs about 39 % more per task for a small gain. Numbers are from Artificial Analysis (2026-11-19) and live in `routing/gpt_rows.json` (refresh with `python3 -I routing/refresh.py routing/gpt_rows.json`). They're a proxy for real Codex work, and cost means API price, not subscription quota.

## Setup

Needs a Codex CLI with the `multi_agent` feature (I tested on codex-cli 0.167.0).

```bash
git clone https://github.com/lsy041015/model-routing-codex
cd model-routing-codex
# main session: set model = "gpt-6.2-sol" and model_reasoning_effort = "medium" at the top of ~/.codex/config.toml
mkdir -p ~/.codex/agents
cp agents/*.toml ~/.codex/agents/
cat config.agents.toml >> ~/.codex/config.toml
cat AGENTS.routing.md >> ~/.codex/AGENTS.md
```

If your `config.toml` already has an `[agents]` table, merge it by hand instead. To check it works, ask Codex to "spawn one subagent with agent_type=scout to find X" and look at the subagent's model in `~/.codex/sessions/**/rollout-*.jsonl`.

MIT licensed.
