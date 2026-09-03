# Shared packages

This directory is reserved for code that is both proven reusable and safely distributable across independently installable Yandex service plugins.

Duplication across at least two plugins plus a stable shared interface is necessary, but not sufficient, for runtime-code promotion. A shared package also needs an explicit installability/distribution contract: every independently installed plugin must receive the dependency through a supported versioned dependency mechanism or a reproducible build/vendor step that does not rely on the monorepo root being present at runtime.

Do not centralize service-specific API behavior prematurely, and do not create hidden repo-root runtime dependencies merely to satisfy DRY. Candidates such as auth, HTTP/retry, cache, schemas, safety helpers, and CLI utilities are promoted here only when both the interface and distribution boundary are stable.

The current service-local `_http.py` adapters intentionally remain inside their owning plugins until such a shared distribution mechanism exists.
