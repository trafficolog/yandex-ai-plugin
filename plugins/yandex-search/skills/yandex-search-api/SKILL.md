---
name: yandex-search-api
description: Use when building or inspecting low-level Yandex Search API v2 web-search requests and responses.
---
# Search API

Current classic Web Search endpoints: `/v2/web/search` and `/v2/web/searchAsync`. REST fields are CamelCase. Auth may use API-Key or IAM token; redact credentials from previews. Current service-account role is `search-api.webSearch.user`, API-key scope `yc.search-api.execute`. Image/generative/infocontext APIs are outside the shipped classic-web-search scope.

The documented result-depth ceiling is 250 results per query. The bundled request helper validates the **entire** configured result window: `requested_per_page = groupsOnPage * docsInGroup`, `window_start = page * requested_per_page`, `window_end = window_start + requested_per_page` (exclusive). `window_end == 250` is valid; `window_start >= 250` or `window_end > 250` is rejected. Do not assume the service will provide a safe partial final page beyond the documented ceiling.
