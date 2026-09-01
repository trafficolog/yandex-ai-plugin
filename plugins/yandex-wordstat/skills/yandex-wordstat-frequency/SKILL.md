---
name: yandex-wordstat-frequency
description: Use when the user asks for Wordstat frequency of one or a few expressions or wants to compare broad versus operator-constrained demand.
---

# Wordstat frequency

Preserve the exact input expression. Use GetTop `totalCount` for the specific expression/filter combination; do not replace it with a sum of returned rows.

When comparing forms such as a broad phrase, quoted phrase, `!` word form or `[]` order, explain that each expression answers a different question. Keep region/device filters identical when comparing values.

If live execution is unavailable, do not fabricate a frequency number.

References: `references/operators.md`, `references/semantics.md`.
