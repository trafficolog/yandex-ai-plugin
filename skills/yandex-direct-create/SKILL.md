---
name: yandex-direct-create
description: Use when creating a new Yandex Direct campaign, building campaign structure from a brief, preparing semantics and ads, or taking a new campaign to draft/preflight state.
---

# Create Yandex Direct Campaign

Read `../../references/create-workflow.md`, `../../references/api-2026.md`, and `../../references/safety.md`.

## Required inputs

Resolve from the user or available project material: business objective, landing page, geo, budget boundary, target action, conversion goal/value if known, brand restrictions, product/service scope, and whether Yandex Metrika is installed.

Do not block the whole workflow for a missing optional detail. Record gaps explicitly and continue with the parts that can be prepared safely. However, do not configure a conversion strategy around a goal that is unknown or untrustworthy.

## Workflow

1. Produce a compact campaign brief and list missing evidence.
2. Build semantic hypotheses and query-intent clusters. Use live Wordstat/account data when available; otherwise mark frequency/CPC as unknown.
3. Design EPK structure and placement intent. Avoid campaign splits that have no operational reason.
4. Build campaign/group negatives and cross-routing where query intent overlaps.
5. Draft ads/assets and landing mappings. Verify current limits before upload.
6. Define measurement goals before bidding strategy.
7. Choose strategy from objective, data availability, and current Yandex support—not folklore thresholds.
8. Produce preflight: campaign/group count, URLs, geo, placements, budget, goal IDs, strategy, negatives, tracking, assets, unresolved gaps.
9. Generate API/MCP payload previews.
10. Require explicit approval before writes. Creating entities does not authorize activation.

## Output artifacts

Prefer a working folder with `brief.md`, `semantics.csv`, `structure.md`, `negatives.md`, `ads.csv`, `measurement.md`, `strategy.md`, `preflight.md`, and `change-log.md` when the environment supports files.

## Stop conditions

Stop before write operations when the requested topic is prohibited by platform policy, critical measurement is invalid, the user cannot identify the intended account/client, or the payload would spend money immediately without a distinct activation gate.
