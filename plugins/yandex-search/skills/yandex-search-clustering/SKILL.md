---
name: yandex-search-clustering
description: Use when clustering search queries by real overlap of ranking URLs in Yandex SERPs.
---
# SERP-overlap clustering

Requirements: XML snapshots, `GROUP_MODE_FLAT`, `docsInGroup=1`, explicit `top_k`, and explicit `min_shared_urls`. Never invent a universal threshold. Report pairwise shared URLs and Jaccard. For each connected component show representative query, weakest pair and `bridge_risk` when transitive A↔B↔C chaining hides weak direct overlap.
