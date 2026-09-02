# Yandex Webmaster

Workflow-first Yandex Webmaster plugin for SEO audits, search queries, indexing, recrawl, sitemaps, links, feeds, exports and API work.

Version: `1.0.2`.

Consequential actions follow `read → analyze → preview → explicit approval → write → verify`.

## Capability matrix

| Capability | Read | Write | MCP/App | Bundled API | File fallback |
|---|---:|---:|---:|---:|---:|
| Host, diagnostics, queries, indexing, links | yes | no | optional | yes | yes |
| URL recrawl | yes | approval | optional | yes | preview |
| Sitemap operations / priority recrawl | yes | approval | optional | yes | preview |
| Feed management | yes | approval | optional | yes | preview |
| PRO / archive exports | yes | no | optional | yes | yes |
| Site management | yes | approval | optional | yes | preview |

## PRO export contract

- request paths are host-relative, non-empty and begin with `/`; full URLs are rejected;
- `use_pro_tariff` is serialized as API strings `"true"` / `"false"`;
- lifecycle is explicit: `IN_PROGRESS`, `SUCCESS`, `FAILED` with deterministic pending/ready/failed/missing/expired states;
- successful downloads require an absolute HTTPS URL;
- the documented URL lifetime is 24 hours, but expiry is claimed only when completion age is known and greater than 24 hours;
- quota planning distinguishes known remaining quota from unknown usage;
- helpers do not autonomously poll, schedule, or invent status-check intervals.
