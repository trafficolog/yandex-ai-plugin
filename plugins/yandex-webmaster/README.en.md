# Yandex Webmaster

[Русский](README.md) · [**English**](README.en.md)

Version `1.0.2`. Service plugin for hosts, diagnostics, search queries, indexing, recrawl, sitemaps, links, feeds, archive/PRO exports and raw API workflows.

> `DOCS 1.0.0` changes documentation only.

## Capability matrix

| Capability | Read | Write | MCP/App | Bundled API | File fallback |
|---|---:|---:|---:|---:|---:|
| Host, diagnostics, queries, indexing, links | yes | no | optional | yes | yes |
| URL recrawl | yes | approval | optional | yes | preview |
| Sitemap operations / priority recrawl | yes | approval | optional | yes | preview |
| Feed management | yes | approval | optional | yes | preview |
| PRO / archive exports | yes | no | optional | yes | yes |
| Site management | yes | approval | optional | yes | preview |

## Key semantics

- crawl, index and search presence are distinct;
- top-N/popular queries are not complete query coverage;
- recrawl/sitemap submission does not guarantee indexing/ranking;
- feed batch add uses `{"feeds": [...]}`;
- destructive/quota-consuming operations require exact preview + approval.

## PRO export 1.0.2

- request paths are non-empty host-relative paths beginning with `/`;
- `use_pro_tariff` serializes as `"true"` / `"false"`;
- lifecycle `IN_PROGRESS`, `SUCCESS`, `FAILED` maps to deterministic states;
- success downloads require an absolute HTTPS URL;
- expiry is asserted only with proven age >24h;
- quota planning distinguishes known remaining quota from unknown usage;
- helpers do not autonomously poll or schedule.

```bash
python -m unittest discover -s tests -v
```
