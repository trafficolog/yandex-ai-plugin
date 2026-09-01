---
name: yandex-search-rankings
description: Use when comparing positions between two Yandex SERP snapshots for the same search configuration.
---
# Ranking comparison

Require matching `config_fingerprint` before calculating movement. A change #4 → #2 is `+2`; track new and dropped URLs separately. If region/search type/grouping/freshness/device-related settings differ, stop and report the comparison as invalid.
