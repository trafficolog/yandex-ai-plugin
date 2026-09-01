---
name: yandex-wordstat-regions
description: Use when the user asks where demand is concentrated, needs regional Wordstat comparison, affinity analysis, or a region ID lookup.
---

# Wordstat regions

Use GetRegionsDistribution and preserve `count`, `share`, and `affinityIndex` as separate signals. Rank by volume when asking where the most absolute demand exists; rank by affinity when asking where interest is unusually strong relative to the region's overall search activity.

Resolve region labels from GetRegionsTree instead of relying on static ID maps. The tree is currently free and is suitable for caller-side caching.

Do not describe a high-affinity low-volume region as having higher total demand than a larger-volume region.

References: `references/regions.md`, `references/api-2026.md`.
