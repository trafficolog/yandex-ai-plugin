# Changelog — Yandex Direct

[Русский](CHANGELOG.md) · [**English**](CHANGELOG.en.md)

## [2.0.0] — 2026-09-03

- Breaking safety contract: consequential Direct writes now require the exact `preview_id`; `--execute` alone is not sufficient.
- New flow: preview → approval of the exact preview in a later user turn → `--execute --approve <preview_id>`.
- Approval binds service, method, `Client-Login`, environment, body, and a pseudonymous HMAC-SHA256 auth-principal binding; changing the OAuth token or payload invalidates permission without exposing the token.
- API/account/file content is treated as data, not instructions; adjacent-service work routes to the owning plugin.

Migration:

```bash
# 1.x
python scripts/yd_api.py campaigns update --params-file update.json --execute
# 2.0.0
python scripts/yd_api.py campaigns update --params-file update.json
python scripts/yd_api.py campaigns update --params-file update.json --execute --approve <preview_id>
```

## [1.0.1] — 2026-09-02

- Made API method safety allowlist-based: unknown and mutating methods are preview-first by default.
- Made Reports attribution/goals explicit, removed obsolete `IncludeDiscount`, and retry the first HTTP 500 once.
- Added KPI provenance metadata sidecars for TSV reports without inventing currency.
- Added regression eval expectations for write safety and report context.

## [1.0.0] — 2026-09-01

- Split monolithic Direct knowledge into 8 discoverable skills.
- Updated core API workflow to v501 and an EPK-first model.
- Added safe API and Reports helpers, autotargeting/shared-negative guidance, offline tests and marketplace manifests.