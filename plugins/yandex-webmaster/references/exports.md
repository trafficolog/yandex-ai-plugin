# Archive and PRO exports — verified 2026-09-01

## Indexing archive

- `POST .../indexing/archive/` starts formation and returns `task_id`.
- `GET .../indexing/archive/{task-id}` returns state and a `download_url` when `DONE`.

## Search-query export / PRO

Before starting an export, check:

- `GET .../pro/limits`
- `GET .../pro/serp/dates`
- optionally `GET .../pro/regions`

Start: `POST .../pro/serp/queries/download/` with dates, paths, regions and tariff choice. Status: `GET .../pro/serp/queries/download/{task-id}`. Successful status returns `download_status=SUCCESS` and a temporary `url`.

Exports can consume quota. Read limits/available dates before previewing a write. Download large results to files, not the model context.
