---
name: yandex-wordstat-api
description: Use when the user needs raw Yandex Cloud Wordstat v2 requests, authentication troubleshooting, payload construction, quota planning, or API-cost estimation.
---

# Wordstat API

Bundled methods: GetTop, GetDynamics, GetRegionsDistribution, GetRegionsTree on Yandex Cloud Wordstat v2.

Auth accepts exactly one of API-Key or IAM token. Redact credentials in every preview. `folderId` is optional in some service-account flows and must not be forced to 20 characters; when supplied, current REST schema allows up to 50.

Current documented quota: **100** Wordstat requests/hour and 10/second. Default research safety budget: **90** requests/hour. Produce a **cost preview** for large plans using dated rates and label it as an estimate rather than a billing guarantee.

The legacy `api.wordstat.yandex.net/v1` surface is reference-only in plugin 1.0.0.

References: `references/api-2026.md`, `references/auth.md`, `references/quota-pricing.md`.
