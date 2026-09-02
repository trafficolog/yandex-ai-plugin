# Search queries — verified 2026-09-01

Relevant resources:

- `GET .../search-queries/popular`
- `GET .../search-queries/all/history`
- `GET .../search-queries/{query-id}/history`
- `POST .../query-analytics/list`

Popular-query output is a top-N view, not proof of complete query coverage. Preserve period, device type, sort/order, offset and limit in analysis. Query Analytics supports richer text/statistic filters, regions, devices and search-location parameters.

When reporting a drop, distinguish changes in impressions, clicks, CTR and average position; do not infer causality from correlation alone. Compare equivalent filters and periods.
