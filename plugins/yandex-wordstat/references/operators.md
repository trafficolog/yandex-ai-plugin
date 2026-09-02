# Wordstat operators

Operators include `-`, `!`, `+`, quotes, `[]`, `()`, and `|`.

Top/Regions workflows can use the full operator language. Cloud v2 REST Dynamics currently exposes `PERIOD_MONTHLY` and `PERIOD_WEEKLY`; for those granularities only `+` is guaranteed by the current Search API operator documentation. Do not silently strip unsupported operators from a requested expression.

Preserve the exact operator expression next to every frequency result so numbers are not separated from the query semantics that produced them.
