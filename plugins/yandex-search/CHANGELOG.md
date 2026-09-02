# Changelog

## 1.0.2 — 2026-09-02

- Added strict enforcement of the documented 250-result search-depth ceiling using complete request-window validation.
- Added snapshot depth metadata (`max_supported_results`, result window boundaries, and ceiling reach state) and rejected impossible observed ranks above 250.
- Preserved absolute-rank and conservative tracking-URL identity behavior from 1.0.1.

## 1.0.1 — 2026-09-02

- Made SERP ranks absolute across paginated result pages while preserving position-on-page metadata.
- Added strict `fix_typo_mode` validation.
- Added adversarial bridge-risk eval expectations and the required capability matrix.

## 1.0.0 — 2026-09-01
- Initial Yandex Search plugin release.