# Yandex Metrika Plugin

Workflow-first plugin for Yandex Metrika API as part of the Yandex AI marketplace. Version 1.0.0 covers audit, reporting, conversions, ecommerce, attribution, goals, Logs API, imports and low-level API workflows.

Execution preference: connected Metrika app/MCP when available, bundled Python helpers when executable, otherwise user-provided exports/files. Consequential changes follow `read → analyze → preview → explicit approval → write → verify`.

## Skills

- `yandex-metrika` — router
- `yandex-metrika-audit` — measurement/data-quality audit
- `yandex-metrika-reporting` — traffic and period reports
- `yandex-metrika-conversions` — goals and conversion analysis
- `yandex-metrika-ecommerce` — orders/revenue/products
- `yandex-metrika-attribution` — attribution model selection
- `yandex-metrika-goals` — goal management
- `yandex-metrika-logs` — Logs API lifecycle
- `yandex-metrika-imports` — offline/import workflows
- `yandex-metrika-api` — low-level API operations

## Credentials

Set `YANDEX_METRIKA_TOKEN` locally or use credentials supplied by a connected app. Never commit tokens.
