---
name: yandex-direct-reporting
description: Use when producing Yandex Direct performance reports, period comparisons, campaign or keyword statistics, search-query reports, conversion analysis, or KPI summaries.
---

# Report on Yandex Direct

Read `../../references/reporting.md` and `../../references/api-2026.md`.

## Before fetching

State the exact date range, comparison range, account currency, VAT treatment, conversion goals, and attribution model when those affect the answer.

Use Reports v501. If a report is queued (201) or still generating (202), resend the same request after `retryIn`; do not regenerate `ReportName` or mutate fields while polling.

## Interpretation

Calculate only metrics supported by available data. If revenue is missing, do not infer ROAS/DRR. If goals are ambiguous, show conversion metrics by goal or label the ambiguity.

For keyword/query decisions include spend, clicks, conversions, and criterion type. Separate autotargeting when useful. For placement decisions include `AdNetworkType` or equivalent supported grouping.

## Helper

When local Python is available, `../../scripts/yd_report.py` provides v501 presets and correct offline polling behavior. Inspect and customize fields/filters rather than assuming a preset is sufficient for every question.
