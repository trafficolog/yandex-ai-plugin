---
name: yandex-wordstat-operators
description: Use when Wordstat query operators affect the requested frequency or when the user asks how -, !, +, quotes, [], (), or | change interpretation.
---

# Wordstat operators

Wordstat operator language includes `-`, `!`, `+`, quotes, `[]`, `()`, and `|`.

Top and Regions workflows can use the Wordstat operator language. For bundled Cloud v2 monthly/weekly Dynamics, the plugin applies a conservative repository-level compatibility guard and rejects expressions using operators beyond `+`. Do not present that guard as a documented Yandex prohibition. Use `PERIOD_DAILY` when the requested supported Wordstat expression needs non-`+` operators.

Always return the exact expression beside its number. Do not compare different operator expressions as though they measured the same population.

References: `references/operators.md`.
