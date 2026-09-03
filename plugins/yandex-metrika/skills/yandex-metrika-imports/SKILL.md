---
name: yandex-metrika-imports
description: Use when preparing or executing Yandex Metrika offline conversion, call, expense, visitor-parameter or CRM data imports.
---

# Import data safely

Read `../../references/imports.md` and `../../references/safety.md`.

## Required sequence

1. identify target counter and import family;
2. inspect the source file/schema locally;
3. validate encoding, columns, row count, dates/identifiers and provider context;
4. for expense CSVs, establish source provenance from UTM or `TrafficSource` / `TrafficSourceDetail` evidence before upload;
5. show a preview without exposing full customer data;
6. obtain explicit approval;
7. upload;
8. poll the corresponding upload status before treating the data as available.

Never manually import Yandex Direct expenses: Direct transfers cost data automatically and duplicate import makes reports incorrect.

For expense imports, a human `provider` label is not sufficient provenance. The helper blocks proven Direct rows (`DIRECT_DUPLICATION_RISK`) and also fails closed when source evidence cannot rule Direct out (`DIRECT_SOURCE_UNVERIFIED`). `--allow-direct-risk` is an explicit reviewed override, not a default bypass.

The executable helper supports CSV upload for offline conversions, calls and expenses. Visitor parameters and CRM imports remain supported at the reasoning/reference layer until dedicated executors are added in a later version.

Use `../../scripts/ym_import.py` for validated previews/uploads when local execution is available.
