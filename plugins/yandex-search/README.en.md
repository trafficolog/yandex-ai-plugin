# Yandex Search

[Русский](README.md) · [**English**](README.en.md)

Version `1.0.2`. SEO-first service plugin for classic web SERP retrieval, snapshots, rankings, competitor presence, URL-overlap clustering and sync/deferred Search API v2 workflows.

> `DOCS 1.0.0` changes documentation only.

## Capability matrix

| Capability | Read | Write | MCP/App | Bundled API | File fallback |
|---|---:|---:|---:|---:|---:|
| Interactive web SERP retrieval | yes | no | optional | yes | yes |
| Deferred / batch search | yes | no | optional | yes | yes |
| SERP snapshot normalization | yes | no | optional | yes | yes |
| Absolute rank / snapshot comparison | yes | no | optional | yes | yes |
| Competitor presence analysis | yes | no | optional | yes | yes |
| URL-overlap clustering / bridge-risk analysis | yes | no | optional | yes | yes |
| Raw Search API request construction | preview | no | optional | yes | yes |

## 250-result depth contract

`requested_per_page = groups_on_page * docs_in_group`; `window_start = page * requested_per_page`; `window_end = window_start + requested_per_page`.

A window ending at 250 is valid. `start >= 250` or `end > 250` is rejected; helpers do not rely on undocumented partial truncation. Snapshots retain `max_supported_results`, `window_start`, `window_end`, `reaches_result_ceiling`; rank >250 is invalid.

SERP presence is not market share. URL identity stays conservative: tracking params can be separated while functional params keep pages distinct.

```bash
python -m unittest discover -s tests -v
```
