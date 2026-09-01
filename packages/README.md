# Shared packages

This directory is reserved for code proven reusable across at least two Yandex service plugins.

Do not centralize service-specific API behavior prematurely. Candidates such as auth, HTTP/retry, cache, schemas, safety helpers, and CLI utilities are promoted here only after duplication demonstrates a stable shared interface.
