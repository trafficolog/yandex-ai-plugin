# Trend classification

The bundled classifier is a research heuristic, not a universal business rule.

Default labels:

- `LOW_VOLUME_NOISE` — latest absolute volume below configured floor.
- `STABLE` — growth below configured growing threshold.
- `GROWING` — material growth above baseline median.
- `EXPLOSIVE` — growth above the explicit explosive threshold.
- `SEASONAL` — a current spike resembles the same-month prior-year spike and both exceed local baselines.

Always disclose absolute floor and percentage thresholds used. Percentage growth alone is not enough: 2 -> 20 is not treated like 2,000 -> 20,000.
