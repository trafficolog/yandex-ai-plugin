---
name: yandex-metrika-conversions
description: Use when analyzing Yandex Metrika goals, conversion rate, funnels, goal reach or conversion changes.
---

# Analyze conversions

Read `../../references/reporting.md` and `../../references/audit-framework.md`.

## Workflow

1. Read the configured goals.
2. Identify which goals represent business outcomes versus micro/technical events.
3. State whether the metric basis is visits, users, reaches or ecommerce transactions.
4. Compare explicit periods with the same goal definitions and attribution context.
5. Drill down by source/device/landing or another relevant dimension only after confirming enough data.

Do not combine unrelated goals into one CPA/CR without explaining the aggregation. If a goal was renamed/reconfigured during the period, flag comparability risk.

For writes such as creating or changing a goal, hand off to `yandex-metrika-goals`.
