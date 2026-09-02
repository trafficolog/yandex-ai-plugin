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
4. show a preview without exposing full customer data;
5. obtain explicit approval;
6. upload;
7. poll the corresponding upload status before treating the data as available.

Never manually import Yandex Direct expenses: Direct transfers cost data automatically and duplicate import makes reports incorrect.

Plugin 1.0.0 executable helper supports CSV upload for offline conversions, calls and expenses. Visitor parameters and CRM imports remain supported at the reasoning/reference layer until dedicated executors are added in a later version.

Use `../../scripts/ym_import.py` for validated previews/uploads when local execution is available.
