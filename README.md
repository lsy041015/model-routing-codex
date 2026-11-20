# model-routing-codex

Subagent routing rules for the OpenAI Codex CLI: send each subagent task to the right GPT model and reasoning effort, based on what the task is and how hard it is. Codex counterpart of [lsy041015/model-routing](https://github.com/lsy041015/model-routing) (Claude Code).

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
| Easy 1-2 file changes | main session | your main model |

Read-only roles (`scout`, `reader`, `extractor`, `reviewer-lite`, `reviewer`) run with `sandbox_mode = "read-only"`.

## Why these models

From Artificial Analysis (Intelligence Index v4.3.2, 2026-11-19); raw numbers in `routing/gpt_rows.json`.

| Variant | Intelligence | Terminal-Bench | Hallucination (lower is better) | Cost / task | Time / task |
|---|---|---|---|---|---|
| gpt-6.1-terra low | 29.4 | 0.152 | 0.416 | $0.07 | 78 s |
| gpt-6.1-terra high | 42.4 | 0.419 | 0.370 | $0.26 | 267 s |
| gpt-6.2-sol medium | 52.7 | 0.561 | 0.611 | $0.41 | 198 s |
| gpt-6.2-sol high | 54.9 | 0.586 | 0.600 | $0.56 | 280 s |
| gpt-6.2-sol xhigh | 55.7 | 0.561 | 0.562 | $0.65 | 323 s |
| gpt-6.2-astra high | 60.1 | 0.601 | 0.581 | $2.07 | 366 s |
| gpt-6.2-astra xhigh | 61.6 | 0.641 | 0.577 | $2.52 | 449 s |

- terra high has the lowest hallucination rate of all variants: used for text extraction only.
- sol medium has the best tool-workflow value (AutomationBench 0.70): used for mail/chat/drive extraction.
- Hard and up start on sol xhigh, about a quarter of astra's cost; astra is kept as the escalation after sol xhigh fails twice on the same task (two fix rounds still missing the criteria).
- astra max equals astra xhigh on Terminal-Bench (0.641) for +59% cost and +85% time; `ultra` has no AA data. Use `max`/`ultra` only when the user names them.
- Dominated on every axis, never routed to: `gpt-6.1-sol`, `gpt-6-sol`, `gpt-6-astra`, all `gpt-5.6-*`, `gpt-6-luna` high and up.

AA benchmarks are a proxy, not Codex's real workload; cost is API price, not subscription quota.

## Install

Needs a Codex CLI with the `multi_agent` feature (tested on codex-cli 0.167.0).

```bash
git clone https://github.com/lsy041015/model-routing-codex
cd model-routing-codex
mkdir -p ~/.codex/agents
cp agents/*.toml ~/.codex/agents/
cat config.agents.toml >> ~/.codex/config.toml
cat AGENTS.routing.md >> ~/.codex/AGENTS.md
```

If your `config.toml` already has an `[agents]` table, merge by hand instead of appending. Then ask Codex to spawn a role, for example "spawn one subagent with agent_type=scout to find X", and check the subagent's model in `~/.codex/sessions/**/rollout-*.jsonl`.

## Files

- `AGENTS.routing.md`: routing table, difficulty signals, delegation checklist and escalation order, appended to `~/.codex/AGENTS.md`.
- `agents/*.toml`: one config layer per role (model, effort, sandbox, instructions).
- `config.agents.toml`: `[agents]` registrations and `max_threads = 3`.
- `routing/gpt_rows.json`, `routing/refresh.py`: AA metrics and the script that refreshes them (`python3 -I routing/refresh.py routing/gpt_rows.json`).

## License

MIT
