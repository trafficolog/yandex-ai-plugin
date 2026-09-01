# Safety and data-quality contract

Wordstat is read-only with respect to campaign/site state, but calls consume quota and may incur cost.

- Redact API keys and IAM tokens from previews/logs.
- Preview request count and estimated cost before a large batch.
- Default safety budget: 90 of the currently documented 100 requests/hour.
- Do not invent live values when credentials/backend are unavailable.
- Do not sum overlapping phrase counts into fake total demand.
- Preserve query expression, region/device filters, period and collection timestamp with results.
- Prefer file artifacts for large semantic sets.
