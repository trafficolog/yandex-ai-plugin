---
name: yandex-seo
description: Use when the user asks for a cross-service Yandex SEO analysis spanning demand, SERP, Webmaster visibility, Metrika performance, topical architecture, semantic cocoons, or internal linking.
---
# Yandex SEO router

Detect source coverage first: Wordstat, Search, Webmaster and Metrika may be complete or partial. Select Discovery, Visibility, Performance, Full SEO, Topical Architecture, or Internal Linking; otherwise explicitly report PARTIAL coverage.

Route semantic-cocoon / page-architecture work to `yandex-seo-topical-architecture`. Route link-graph design or audit to `yandex-seo-internal-linking`. Treat `yandex-search-clustering` as the owner of real SERP-overlap clustering and `yandex-wordstat-topic-map` as candidate demand/topic discovery.

Build findings and architecture only from preserved evidence. Label claims as `OBSERVED`, `DERIVED`, `HYPOTHESIS` or `METHODOLOGY`; methodology must never be presented as a verified ranking mechanism. Never fail globally just because one source is absent; state unavailable analyses and limitations such as `SERP_VALIDATION_MISSING`.

This skill is read-only and transport-free. Route any consequential action back to the owning service/CMS/deployment workflow.
