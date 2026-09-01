# Webmaster audit framework

Use evidence-first statuses: `PASS`, `ISSUE`, `REVIEW`, `N/A`.

Recommended order:

1. resolve user and host;
2. verification state and data availability;
3. summary and diagnostics with Yandex severity/state;
4. SQI/history where useful;
5. crawl/indexing history;
6. pages in search and search events;
7. sitemap state/coverage;
8. internal broken and external links where relevant;
9. search-query trends with exact period/filter context;
10. prioritize findings by business/SEO impact, confidence, reversibility and quota/write cost.

Do not invent universal thresholds for CTR, position, SQI, number of indexed pages or diagnostic severity. Use site history, business context and Yandex-provided semantics.
