# Yandex Search

SEO-first Yandex Search API v2 plugin for classic web SERP retrieval and analysis. Version `1.0.2` keeps XML as the canonical structured format; large batches are cost-planned and can use resumable deferred execution.

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

## Result-depth contract

The documented maximum supported result depth is 250 results per query. Request and snapshot helpers validate the complete configured window:

`requested_per_page = groups_on_page * docs_in_group`, `window_start = page * requested_per_page`, `window_end = window_start + requested_per_page`.

A window ending exactly at 250 is accepted. Windows starting at 250 or crossing past 250 are rejected instead of relying on undocumented server truncation. Structured snapshots retain `max_supported_results`, `window_start`, `window_end` and `reaches_result_ceiling`; impossible observed ranks above 250 are rejected.

Absolute rank and conservative tracking-URL identity semantics from 1.0.1 remain unchanged.
