# Yandex Direct

[Русский](README.md) · [**English**](README.en.md)

Version `1.0.1`. Service plugin for Yandex Direct campaigns, Reports API, audits, keywords/negatives, budgets, optimization and low-level API v501 workflows.

> `DOCS 1.0.0` adds bilingual documentation; the plugin version is unchanged.

## Execution model

Preference: compatible connected MCP/app → bundled Python helper → export/file fallback. Consequential changes follow `read → analyze → preview → explicit approval → write → verify`.

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

- v501 and an EPK-first model for new performance workflows;
- queued 201/202 Reports repeat the same payload/report name and honor `retryIn`;
- report artifacts preserve goal/attribution/VAT provenance and do not invent currency;
- autotargeting and keyword criteria stay distinct;
- unknown/mutating methods are safe-by-default and preview before execute;
- no universal CPA/CPC/CTR/ROAS kill rules;
- campaign creation is distinct from activation.

## Helpers

```bash
export YANDEX_DIRECT_TOKEN='...'
python scripts/yd_api.py campaigns get --params '{"SelectionCriteria":{},"FieldNames":["Id","Name","Status"]}'
python scripts/yd_api.py campaigns update --params-file update.json
python scripts/yd_report.py campaign 2026-08-01 2026-08-31 --output report.tsv
```

## Verification

```bash
python -m unittest discover -s tests -v
python -m py_compile scripts/yd_api.py scripts/yd_report.py
```

Sources and upstream attribution: `THIRD_PARTY_NOTICES.md`, `references/sources.md`.