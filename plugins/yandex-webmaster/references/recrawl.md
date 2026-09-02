# Ordinary URL recrawl — verified 2026-09-01

Resources:

- `GET .../recrawl/quota` — `daily_quota`, `quota_remainder`.
- `GET .../recrawl/queue` — queue/tasks.
- `GET .../recrawl/queue/{task-id}` — task state.
- `POST .../recrawl/queue` body `{ "url": "..." }` — submit URL.

Workflow: read quota → inspect existing queue/state → validate URL belongs to selected host → preview → explicit approval → submit → verify.

`409 URL_ALREADY_ADDED` means the URL is already queued. Treat it as an idempotent already-queued state, not a reason to retry repeatedly.
