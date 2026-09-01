---
name: yandex-metrika
description: Use when the request concerns Yandex Metrika broadly or spans multiple Metrika capabilities and needs routing.
---

# Yandex Metrika router

Read `../../references/api-2026.md` and `../../references/safety.md` when API behavior or writes matter.

## Route the task

- measurement/setup quality → `yandex-metrika-audit`
- traffic, source, page, UTM, device or period reports → `yandex-metrika-reporting`
- goals, CR or funnel reasoning → `yandex-metrika-conversions`
- orders/revenue/products → `yandex-metrika-ecommerce`
- attribution-model choice → `yandex-metrika-attribution`
- goal configuration changes → `yandex-metrika-goals`
- raw visit/hit export → `yandex-metrika-logs`
- offline/call/expense/CRM import → `yandex-metrika-imports`
- raw endpoint/payload debugging → `yandex-metrika-api`

## Establish context

Before analysis, resolve the counter, exact date range, business outcome/goal and attribution model when they materially affect the result. If the user named a domain but not a counter, use available account data to resolve it rather than guessing.

Prefer reads first. Creation, import, deletion and other writes follow `read → analyze → preview → explicit approval → write → verify`.

## Execution order

Use a compatible connected Metrika app/MCP when available. Otherwise use bundled helpers. If live access is unavailable, work from user exports/files and provide reproducible queries/change plans.
