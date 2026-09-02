---
name: yandex-search-batch
description: Use when planning or executing many Yandex web queries with quota, cost, sync versus deferred mode, and resumable operation handling.
---
# Batch search

1. Validate and dedupe queries.
2. Produce a **cost preview** for sync and deferred modes using dated prices.
3. Recommend sync for small interactive work and `/v2/web/searchAsync` for larger batches when appropriate.
4. Never auto-spend based only on available quota.
5. Deferred flow is submit → persist operation IDs → status → collect; do not poll forever. Results have a documented 12-hour retention window.
