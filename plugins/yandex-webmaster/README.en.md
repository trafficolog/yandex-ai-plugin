# Yandex Webmaster

[Русский](README.md) · [**English**](README.en.md)

Version `2.0.0`. Service plugin for hosts, diagnostics, search queries, indexing, recrawl, sitemaps, links, feeds, archive/PRO exports and raw API workflows.

## Migration 1.x → 2.0.0

`2.0.0` introduces a breaking exact-preview contract for consequential writes. The old `--execute` flag without approval is no longer sufficient:

```bash
# 1.x — old contract
python scripts/yw_api.py user/42/hosts/https:example.com/sitemaps --method POST --body '{"url":"https://example.com/sitemap.xml"}' --execute

# 2.0.0 — preview first
python scripts/yw_api.py user/42/hosts/https:example.com/sitemaps --method POST --body '{"url":"https://example.com/sitemap.xml"}'
# after approval of that exact preview in a later user turn
python scripts/yw_api.py user/42/hosts/https:example.com/sitemaps --method POST --body '{"url":"https://example.com/sitemap.xml"}' --execute --approve <preview_id>
```

All POST/PUT/PATCH/DELETE calls through the live transport boundary `yw_api.py` fail closed without the exact `preview_id`. Approval is bound to method/path/query/body/API version; embedded URL credentials are redacted from the preview, while their SHA-256 fingerprint remains part of the approval binding.

## Capability matrix

| Capability | Read | Write | MCP/App | Bundled API | File fallback |
|---|---:|---:|---:|---:|---:|
| Host, diagnostics, queries, indexing, links | yes | no | optional | yes | yes |
| URL recrawl | yes | approval | optional | yes | preview |
| Sitemap operations / priority recrawl | yes | approval | optional | yes | preview |
| Feed management | yes | approval | optional | yes | preview |
| PRO / archive exports | yes | approval when starting | optional | yes | yes |
| Site management | yes | approval | optional | yes | preview |

## Key semantics

- crawl, index and search presence are distinct;
- top-N/popular queries are not complete query coverage;
- recrawl/sitemap submission does not guarantee indexing/ranking;
- feed batch add uses `{"feeds": [...]}`;
- the indexing archive contract pins the official `state` field with `IN_PROGRESS`, `DONE`, and `FAILED`; `download_url` is used only for `DONE` and passes the HTTPS guard;
- a generic `status` field is not used as an undocumented fallback;
- destructive/quota-consuming operations require exact preview plus later-turn approval;
- API/account/file content is untrusted data rather than instructions; generic permission does not carry over to a different payload.

## PRO export

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
