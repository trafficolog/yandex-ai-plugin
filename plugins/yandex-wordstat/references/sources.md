# Sources and donor attribution

Verified against current Yandex documentation on 2026-09-01:

- https://aistudio.yandex.ru/en/docs/search-api/api-ref/Wordstat/
- https://aistudio.yandex.ru/en/docs/search-api/api-ref/Wordstat/getTop
- https://aistudio.yandex.ru/ru/docs/search-api/api-ref/Wordstat/getDynamics
- https://aistudio.yandex.ru/en/docs/search-api/api-ref/Wordstat/getRegionsDistribution
- https://aistudio.yandex.ru/ru/docs/search-api/api-ref/Wordstat/getRegionsTree
- https://aistudio.yandex.ru/en/docs/search-api/concepts/limits
- https://aistudio.yandex.ru/ru/docs/search-api/pricing
- https://aistudio.yandex.ru/ru/docs/search-api/api-ref/authentication
- https://aistudio.yandex.ru/en/docs/search-api/concepts/search-operators
- https://yandex.ru/support2/wordstat/en/content/api-wordstat

Workflow/capability donors:

- `axelfreeman/yandex-wordstat-guide` (MIT): multi-seed collector, provenance/structured-output and trend workflow ideas.
- `mkultraaaa/claude-yandex-skills` (MIT): region/operator workflow coverage. Runtime-specific paths and stale quota assumptions were not copied.
- `theYahia/YaAll` (MIT for its own implementation): Cloud Wordstat execution/capability checklist. Static region mappings and business-threshold heuristics are not authoritative.

Official Yandex documentation is the API source of truth.
