---
name: yandex-wordstat-operators
description: Use when Wordstat query operators affect the requested frequency or when the user asks how -, !, +, quotes, [], (), or | change interpretation.
---

# Wordstat operators

Wordstat operator language includes `-`, `!`, `+`, quotes, `[]`, `()`, and `|`.

Top and Regions workflows can use the operator language. For the bundled Cloud v2 monthly/weekly Dynamics surface, only `+` is guaranteed; reject incompatible expressions rather than silently rewriting them.

Always return the exact expression beside its number. Do not compare different operator expressions as though they measured the same population.

References: `references/operators.md`.
