# SERP snapshots

XML is canonical for structured analytics. HTML is a raw artifact only: it may include ads, quick answers and other elements and is not parsed as a stable schema. Fields in Yandex responses are optional. Normalize URLs conservatively: case/default ports/fragments/query ordering only; never delete arbitrary query parameters automatically.

Reproducible structured snapshots preserve the request/config fingerprint plus `max_supported_results`, `window_start`, `window_end`, `reaches_result_ceiling`, absolute `rank`, and `position_on_page`. The supported depth ceiling is 250. Reject windows that start at or cross past that ceiling rather than silently recording a partial/unsupported observation.

SERP presence is presence in the observed result set, not market share. A snapshot that reaches the 250-result ceiling still must not be described as exhaustive market coverage.
