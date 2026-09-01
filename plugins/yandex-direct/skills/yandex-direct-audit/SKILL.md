---
name: yandex-direct-audit
description: Use when auditing a Yandex Direct account, campaign export, PPC setup, tracking quality, search-query waste, bidding configuration, or account hygiene.
---

# Audit Yandex Direct

Read `../../references/audit-framework.md`, `../../references/reporting.md`, and `../../references/api-2026.md`.

## Audit method

Collect evidence first. Separate configuration evidence from performance evidence. Mark checks PASS, ISSUE, REVIEW, or N/A; do not penalize N/A.

Audit these domains: measurement, economics, query quality, structure/EPK placements, ads/assets, strategy, device/audience/placement segmentation, and recent change risk.

## Important corrections to older audit templates

- Do not require separate Search and Network campaigns universally; EPK can combine placements. Judge separation by control/measurement need.
- Do not require “2 ads per group” or “keyword in title” as universal pass/fail rules.
- Do not treat a fixed CTR/CPC/CPA benchmark as proof of quality without industry/account context.
- Do not auto-pause on a fixed 2×/3× CPA heuristic without sample size and conversion-delay analysis.
- Treat autotargeting as a first-class criterion and report it separately where possible.
- Verify current moderation, asset, and strategy rules before calling them violations.

## Deliverable

Return: executive summary, evidence table, high-impact issues, quick fixes, experiments, items requiring more data, and optionally a transparent score with published weights.
