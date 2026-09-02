# Indexing and search inclusion — verified 2026-09-01

Do not conflate crawl, indexing and presence in search.

- `GET .../indexing/history` returns indexing history and HTTP-status indicators.
- `GET .../search-urls/in-search/history` tracks pages in search.
- `GET .../search-urls/events/history` tracks appearances/removals from search.
- `POST .../indexing/archive/` starts asynchronous archive creation.
- `GET .../indexing/archive/{task-id}` returns `IN_PROGRESS`, `DONE` or `FAILED`; `download_url` appears when ready.

A recrawl request does not guarantee indexing or ranking. A page excluded from search may require diagnostics/technical evidence before recommending another recrawl.
