---
name: yandex-wordstat-dynamics
description: Use when the user needs Wordstat seasonality, monthly or weekly history, period comparisons, or changes in query frequency over time.
---

# Wordstat dynamics

Bundled Cloud v2 uses `PERIOD_MONTHLY` or `PERIOD_WEEKLY` with REST fields `fromDate` and `toDate`.

Before the paid request, validate dates, filters and operator compatibility. For Cloud monthly/weekly Dynamics, only `+` is guaranteed; do not silently remove `!`, quotes, `[]`, `()`, `|`, or negative-word operators.

Normalize count/share values, show the time window, and distinguish long-term history from GetTop's trailing-30-day window.

Route growth classification to `yandex-wordstat-trends` when the user asks whether a topic is trending.

References: `references/dynamics.md`, `references/operators.md`.
