# Regions

Regional distribution returns region ID, count, share, and `affinityIndex`.

- `count` answers absolute query volume for the expression in that region.
- `share` is the expression's share of all Yandex queries in the region.
- `affinityIndex` compares the regional share with the country-wide share.

High affinity does not mean highest absolute demand. Present volume and affinity as different signals.

Resolve names through GetRegionsTree rather than hard-coded region maps. The tree should be cacheable by the runtime/caller because it changes slowly and is currently not billed.
