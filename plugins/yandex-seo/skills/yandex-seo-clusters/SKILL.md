---
name: yandex-seo-clusters
description: Use when enriching Search SERP-overlap clusters with demand, Webmaster visibility and Metrika performance evidence.
---
# SEO cluster enrichment

Treat Yandex Search as the owner of clustering. Preserve its explicit top-K, `min_shared_urls`, pairwise overlap/Jaccard and `bridge_risk`; do not re-cluster by fuzzy text similarity. Join normalized query evidence from Wordstat, Webmaster and Metrika around the Search cluster identifier. If `bridge_risk` is true, disclose it when summarizing cluster intent or prioritizing pages. Never imply all cluster members are equally similar when the Search evidence says otherwise.

When the user needs page boundaries, structural hierarchy, semantic-cocoon design or internal links, pass the enriched Search-owned clusters to `yandex-seo-topical-architecture`. Do not create a second clustering algorithm in SEO.
