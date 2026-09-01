---
name: yandex-metrika-audit
description: Use when auditing a Yandex Metrika counter, measurement setup, analytics quality, conversion tracking or data reliability.
---

# Audit Yandex Metrika

Read `../../references/audit-framework.md`, `../../references/reporting.md`, and `../../references/attribution.md`.

## Method

Build an evidence table using `PASS / ISSUE / REVIEW / N/A`. Never mark a check failed just because data is unavailable.

Audit these layers when relevant:

1. counter/site identity, timezone and access context;
2. configured goals versus actual business conversions;
3. ecommerce presence and transaction consistency;
4. UTM/source hygiene and Direct linkage;
5. sampling, sample share, data lag and sensitive-data limitations;
6. attribution model versus the decision being made;
7. suspicious data gaps/discontinuities.

## Output

For each issue state: evidence, likely impact, confidence, and smallest reversible next action. Separate measurement defects from business-performance observations.

Do not use universal bounce-rate, session-duration, CR or ecommerce benchmarks as facts without a user-specific baseline/source.
