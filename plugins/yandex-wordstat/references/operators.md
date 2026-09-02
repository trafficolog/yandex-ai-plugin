# Wordstat operators

Operators include `-`, `!`, `+`, quotes, `[]`, `()`, and `|`.

Top/Regions workflows can use the Wordstat operator language. The bundled plugin keeps a conservative compatibility guard for Cloud v2 `PERIOD_MONTHLY` and `PERIOD_WEEKLY`: expressions using operators beyond `+` are rejected because this repository does not guarantee that combination. This is a repository compatibility policy, **not** a documented Yandex API prohibition. `PERIOD_DAILY` remains available for the supported non-`+` Wordstat operator path.

Do not silently strip or rewrite operators from a requested expression. Preserve the exact operator expression next to every frequency result so numbers are not separated from the query semantics that produced them.
