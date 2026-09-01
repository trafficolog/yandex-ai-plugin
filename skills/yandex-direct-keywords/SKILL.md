---
name: yandex-direct-keywords
description: Use when working with Yandex Direct keywords, search queries, negative phrases, cross-negatives, shared negative sets, keyword bids, or autotargeting.
---

# Keywords, Queries, Negatives, Autotargeting

Read `../../references/api-2026.md` and `../../references/safety.md` before mutations.

## Query analysis

Use search-query reports to classify intent: relevant/converting, relevant/uncertain, irrelevant, competitor/brand, informational, navigational, and ambiguous. Do not add a negative phrase just because it has no conversion in a small sample.

## Negatives

Use the narrowest correct level: campaign, group, shared set, or keyword-level negative. Cross-negative only when two routes compete for the same intent and one route should own it. Keep a proposed additions/removals diff before writing.

`NegativeKeywordSharedSets` supports v501 CRUD and is suitable for reusable governance sets. Verify current limits before bulk changes.

## Autotargeting

Treat `---autotargeting` as a special criterion, not a normal keyword. Use `CriterionType=AUTOTARGETING` in reporting where supported. Do not assume keyword-level bid behavior applies identically to autotargeting; verify current API capability for the campaign/placement.

## Writes

Suspend/resume/add/update/delete and shared-set changes require a preview with IDs and explicit approval.
