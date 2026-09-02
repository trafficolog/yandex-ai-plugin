# Yandex Webmaster

[**Русский**](README.md) · [English](README.en.md)

Версия `1.0.3`. Service plugin для technical/search visibility: hosts, diagnostics, search queries, indexing, recrawl, sitemaps, links, feeds, archive/PRO exports и raw API workflows.

## Capability matrix

| Capability | Read | Write | MCP/App | Bundled API | File fallback |
|---|---:|---:|---:|---:|---:|
| Host, diagnostics, queries, indexing, links | yes | no | optional | yes | yes |
| URL recrawl | yes | approval | optional | yes | preview |
| Sitemap operations / priority recrawl | yes | approval | optional | yes | preview |
| Feed management | yes | approval | optional | yes | preview |
| PRO / archive exports | yes | no | optional | yes | yes |
| Site management | yes | approval | optional | yes | preview |

## Ключевые semantics

- crawl, index и search presence — разные состояния;
- top-N/popular queries не являются полной query universe;
- recrawl/sitemap submission не гарантируют indexing/ranking;
- feed batch add использует `{"feeds": [...]}`;
- indexing archive status contract 1.0.3 закрепляет официальное поле `state` со значениями `IN_PROGRESS`, `DONE`, `FAILED`; `download_url` используется только при `DONE` и проходит HTTPS guard;
- generic `status` не используется как недокументированный fallback;
- destructive/quota-consuming operations требуют exact preview + approval.

## PRO export

- request paths host-relative, non-empty и начинаются с `/`;
- `use_pro_tariff` сериализуется как `"true"` / `"false"`;
- lifecycle: `IN_PROGRESS`, `SUCCESS`, `FAILED` → deterministic states;
- success download требует absolute HTTPS URL;
- expiry утверждается только при доказанном возрасте >24h;
- quota planning различает known remaining quota и unknown usage;
- helpers не выполняют autonomous polling/scheduling.

```bash
python -m unittest discover -s tests -v
```
