---
name: yandex-webmaster-sitemaps
description: Use when listing, adding, deleting or requesting priority recrawl for sitemaps.
---

# Sitemaps

Read `../../references/sitemaps.md`, `../../references/endpoint-map.md` and `../../references/safety.md`. Use `scripts/yw_sitemaps.py`.

Standard sitemap resources stay on v4. Priority Sitemap recrawl is v4.1. Check priority limit/state before proposing POST. The documented monthly limit is **10** requests; preserve `requests_count`, `nearest_allowed_day`, `pending` and `allowed`.

Add/delete are configuration changes; delete is destructive and requires exact target approval. Adding or recrawling a sitemap does not guarantee search inclusion.
