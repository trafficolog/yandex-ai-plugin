# Yandex Direct

[Русский](README.md) · [**English**](README.en.md)

Version `2.0.0`. Service plugin for Yandex Direct campaigns, Reports API, audits, keywords/negatives, budgets, optimization and low-level API workflows.

## Execution model

Preference: compatible connected MCP/app → bundled Python helper → export/file fallback. Consequential changes follow `read → analyze → preview → explicit approval → write → verify`.

### Migration 1.x → 2.0.0

`2.0.0` introduces a breaking write-safety contract. The old `--execute`-only invocation is no longer sufficient authorization:

```bash
# 1.x — old contract
python scripts/yd_api.py campaigns update --params-file update.json --execute

# 2.0.0 — preview first
export YANDEX_DIRECT_TOKEN='...'
python scripts/yd_api.py campaigns update --params-file update.json
# then, only after the exact preview is approved in a later user turn
python scripts/yd_api.py campaigns update --params-file update.json --execute --approve <preview_id>
```

The `preview_id` binds service, method, `Client-Login`, OAuth auth principal, environment, and body. Changing the token, payload, or environment requires a fresh preview/approval. OAuth is supplied only through `YANDEX_DIRECT_TOKEN`; the 2.0.0 CLI has no `--token` argument.

## Production and sandbox

The helper uses production `https://api.direct.yandex.com/json/v501/{service}` by default. Use the explicit flag for the official sandbox:

```bash
python scripts/yd_api.py campaigns get --params '{}' --sandbox
```

Sandbox uses `https://api-sandbox.direct.yandex.com/json/v5/{service}`. Production and sandbox are distinct approval-bound environments: a production preview cannot authorize a sandbox write and vice versa.

## Transport metadata and errors

A live call keeps the exact Yandex Direct JSON payload under `result` and exposes selected safe transport headers separately under `transport`: `RequestId` → `request_id`, `Units` → `units`, and `Units-Used-Login` → `units_used_login`. Other response headers are not copied by default.

Expected CLI failures (`validation`, `input`, `network`, `http`, `api`) are emitted as JSON to stderr with exit code `2`, without a normal traceback. HTTP error bodies are capped at 4096 bytes and decoded with replacement semantics.

## Capability matrix

| Capability | Read | Write | MCP/App | Bundled API | File fallback |
|---|---:|---:|---:|---:|---:|
| Campaign discovery / state | yes | — | optional | yes | yes |
| Campaign draft / update payloads | yes | approval | optional | yes | yes |
| Audit | yes | — | optional | yes | yes |
| Reports / KPI analysis | yes | — | optional | yes | yes |
| Keywords / negatives | yes | approval | optional | yes | yes |
| Budget analysis / changes | yes | approval | optional | yes | yes |
| Optimization recommendations / writes | yes | approval | optional | yes | yes |

## Skills

`yandex-direct` router; `yandex-direct-create`; `yandex-direct-audit`; `yandex-direct-reporting`; `yandex-direct-optimize`; `yandex-direct-keywords`; `yandex-direct-budget`; `yandex-direct-api`.

## Key correctness rules

- production API uses v501; sandbox uses the separately documented `/json/v5/` contract;
- service names are checked against a strict allowlist before URL construction;
- queued 201/202 Reports repeat the same payload/report name and honor `retryIn`;
- report artifacts preserve goal/attribution/VAT provenance and do not invent currency;
- autotargeting and keyword criteria stay distinct;
- unknown/mutating methods are safe-by-default and preview before execute;
- consequential writes require exact `preview_id` approval;
- no universal CPA/CPC/CTR/ROAS kill rules;
- campaign creation is distinct from activation.

## Helpers

```bash
export YANDEX_DIRECT_TOKEN='...'
python scripts/yd_api.py campaigns get --params '{"SelectionCriteria":{},"FieldNames":["Id","Name","Status"]}'
python scripts/yd_api.py campaigns update --params-file update.json # preview
python scripts/yd_api.py campaigns update --params-file update.json --execute --approve <preview_id>
python scripts/yd_api.py campaigns get --params '{}' --sandbox
python scripts/yd_report.py campaign 2026-08-01 2026-08-31 --output report.tsv
```

## Verification

```bash
python -m unittest discover -s tests -v
python -m compileall -q scripts
```

Sources and upstream attribution: `THIRD_PARTY_NOTICES.md`, `references/sources.md`, `references/api-2026.md`.
