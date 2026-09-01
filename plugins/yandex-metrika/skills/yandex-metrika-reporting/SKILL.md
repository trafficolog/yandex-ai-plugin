---
name: yandex-metrika-reporting
description: Use when building or interpreting Yandex Metrika traffic, source, page, UTM, device, geography, time-series or comparison reports.
---

# Report with Yandex Metrika

Read `../../references/reporting.md` and `../../references/attribution.md`.

## Before fetching

State the counter, exact date range, comparison range, metrics, dimensions, filters, attribution model and accuracy when they affect interpretation.

Use table/bytime/comparison/drilldown endpoints intentionally rather than forcing every question into one table.

## Data quality

Always inspect and surface material response metadata: `sampled`, `sample_share`, `sample_size`, `sample_space`, `data_lag`, `contains_sensitive_data`, `total_rows_rounded`.

If sampling or disclosure limits are material, qualify the conclusion and avoid false precision.

## Interpretation

Decompose changes before assigning causes: source/channel → campaign/referrer → device → landing/page → conversion/revenue as supported by the data. Do not infer revenue, ROAS or ecommerce outcomes if those metrics are absent.

When local Python is available, `../../scripts/ym_report.py` builds current report requests and returns the API payload plus a separate `quality` object.
