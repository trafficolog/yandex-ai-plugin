# Archive and PRO exports

Verified: 2026-09-02

## Indexing archive

- `POST .../indexing/archive/` starts formation and returns `task_id`.
- `GET .../indexing/archive/{task-id}` returns state and a `download_url` when `DONE`.

## Search-query export / PRO

Before starting an export, check known context from:

- `GET .../pro/limits`
- `GET .../pro/serp/dates`
- optionally `GET .../pro/regions`

Start: `POST .../pro/serp/queries/download/` with dates, host-relative paths beginning with `/`, regions and tariff choice. Full URLs are not valid export paths. The public boolean tariff choice is serialized as API strings `"true"` / `"false"` for `use_pro_tariff`.

Status: `GET .../pro/serp/queries/download/{task-id}`. Documented lifecycle values are `IN_PROGRESS`, `SUCCESS` and `FAILED`. `SUCCESS` is ready only when an absolute HTTPS `url` is present; a missing URL stays explicit rather than being treated as downloadable. Preserve failure error fields.

The successful download URL has a 24-hour lifetime. Assert expiry only when completion age is known and greater than 24 hours; unknown age remains unknown.

Exports can consume quota. Prefer initialization-response quota information when available; otherwise use explicitly known remaining quota. Missing usage/remaining data means `QUOTA_USAGE_UNKNOWN`, not zero use or free capacity.

The plugin does not autonomously poll or schedule task checks. A workflow may perform an explicit later status request, but must not invent undocumented retry intervals.

Download large results to files, not the model context.
