---
name: yandex-wordstat-trends
description: Use when the user wants rising topics, trend detection, breakout keyword research, or help separating growth from seasonality and tiny-volume noise.
---

# Wordstat trends

Classify a normalized Dynamics series with explicit thresholds and report them. Supported research labels:

- `LOW_VOLUME_NOISE`
- `STABLE`
- `GROWING`
- `EXPLOSIVE`
- `SEASONAL`

Use a recent value against a local baseline median, enforce an absolute-volume floor, and check a same-month prior-year spike when data exists. Percentage growth alone is insufficient.

Thresholds are research parameters, not universal business rules. Never call 2 -> 20 equivalent to 2,000 -> 20,000 simply because both are large percentages.

References: `references/trends.md`, `references/dynamics.md`.
