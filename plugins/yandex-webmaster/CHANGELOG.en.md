# Changelog — Yandex Webmaster

[Русский](CHANGELOG.md) · [**English**](CHANGELOG.en.md)

## [2.0.0] — 2026-09-03

- Breaking safety contract: consequential POST/PUT/PATCH/DELETE calls no longer execute based on `--execute` alone; after a separate later-turn user approval, the exact preview requires `--execute --approve <preview_id>`.
- The live write boundary `yw_api.py` binds approval to method/path/query/body/API version and fails closed on missing or mismatched approval.
- Embedded URL basic-auth credentials are redacted from previews; their SHA-256 fingerprint remains part of the approval binding, so changed credentials invalidate the old approval.
- API/account/file content is untrusted data rather than instructions; generic permission does not carry over to a new payload.

Migration:

```bash
# 1.x
python scripts/yw_api.py user/42/hosts/https:example.com/sitemaps --method POST --body '{"url":"https://example.com/sitemap.xml"}' --execute
# 2.0.0
python scripts/yw_api.py user/42/hosts/https:example.com/sitemaps --method POST --body '{"url":"https://example.com/sitemap.xml"}'
python scripts/yw_api.py user/42/hosts/https:example.com/sitemaps --method POST --body '{"url":"https://example.com/sitemap.xml"}' --execute --approve <preview_id>
```

## [1.0.3] — 2026-09-02

- Re-verified the official indexing archive status contract: the response uses `state` with `IN_PROGRESS`, `DONE`, and `FAILED`, and `download_url` belongs to a completed `DONE` state.
- Regression tests pin `state` and intentionally do not accept an undocumented `status` fallback.
- Added the archive lifecycle as a separate high-risk contract in the repository traceability matrix.

## [1.0.2] — 2026-09-02

- Corrected PRO export `use_pro_tariff` serialization and host-relative path validation.
- Added deterministic lifecycle normalization, missing/expired states and 24-hour age handling without autonomous polling.
- Quota planning distinguishes known remaining quota from unknown usage.

## [1.0.1] — 2026-09-02

- Corrected feed batch body to `{"feeds": [...]}`.
- Strengthened credential redaction and HTTPS-only artifact downloads.
- Added verifiable eval expectations for destructive/quota-consuming workflows.

## [1.0.0] — 2026-09-01

- Initial Yandex Webmaster plugin.
