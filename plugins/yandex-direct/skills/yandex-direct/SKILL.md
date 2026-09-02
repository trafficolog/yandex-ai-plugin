---
name: yandex-direct
description: Use when a user asks broadly about Yandex Direct, Директ, ЕПК, РСЯ, search ads, campaign management, or is unclear which Yandex Direct workflow is needed.
---

# Yandex Direct Router

Use this skill to route the request to the smallest relevant Yandex Direct skill. Do not load every reference by default.

## Route

- New campaign, brief → draft: read `../yandex-direct-create/SKILL.md`.
- Audit of an account or export: read `../yandex-direct-audit/SKILL.md`.
- Statistics, KPI table, period comparison: read `../yandex-direct-reporting/SKILL.md`.
- Optimization of existing campaigns: read `../yandex-direct-optimize/SKILL.md`.
- Keywords, search queries, negatives, autotargeting: read `../yandex-direct-keywords/SKILL.md`.
- Budget pace, forecast, allocation: read `../yandex-direct-budget/SKILL.md`.
- Raw API calls, payloads, troubleshooting: read `../yandex-direct-api/SKILL.md`.

For any live account mutation, also read `../../references/safety.md`.

## Defaults

- Treat EPK / Unified Performance Campaign as the default model for new performance work unless current evidence says otherwise.
- Use official Yandex docs for fields/limits that can change.
- Never invent Wordstat frequency, CPC, conversions, business targets, or moderation requirements.
- Keep creation and activation as separate decisions.
