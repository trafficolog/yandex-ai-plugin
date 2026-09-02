---
name: yandex-metrika-attribution
description: Use when selecting, comparing or explaining attribution models in Yandex Metrika reports.
---

# Choose attribution deliberately

Read `../../references/attribution.md`.

Current models used by this plugin are:

- `cross_device_first`
- `last`
- `cross_device_last_significant`
- `automatic`

Since 2026-06-25, Yandex maps several legacy models to current analogues. Do not silently use legacy `lastsign` as a universal default.

Choose a model based on the question, then state it in the result. For sensitive decisions, compare more than one model and show whether the ranking/conclusion changes.

Remember that attribution changes ownership of conversions; it does not create new conversions. Keep measurement-model differences separate from real business change.
