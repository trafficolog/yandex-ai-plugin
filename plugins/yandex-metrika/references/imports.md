# Data imports — verified 2026-09-01

Initial executable helper coverage:

- offline conversions: `POST /management/v1/counter/{counterId}/offline_conversions/upload`
- calls: `POST /management/v1/counter/{counterId}/offline_conversions/upload_calls`
- expenses: `POST /management/v1/counter/{counterId}/expense/upload`

All three use multipart CSV uploads. Validate UTF-8, headers, row count, target counter and query parameters before upload. Processing is asynchronous for some imports; after upload, use the corresponding status endpoint before assuming the data is available in reports.

## Critical Direct-cost guard

Do not manually upload Yandex Direct expenses. Direct transfers its cost data to Metrika automatically; a manual upload can duplicate those expenses and make reports incorrect.

The bundled expense helper applies two independent risk layers:

1. **Source-label guard.** Exact aliases and explicit tokenized Direct labels are rejected, including forms such as `Yandex Direct RU`, `direct_ads` and `Яндекс Директ агентство`. Arbitrary concatenations such as `MyDirect` are not treated as proven Direct provenance solely because they contain the substring `direct`.
2. **CSV-content guard.** When `UTMSource` / `UTMMedium` columns are present, Direct-like source/medium combinations such as `yandex,cpc` raise `DIRECT_DUPLICATION_RISK` independently of the human source label.

The second layer is deliberately stronger than label naming. An explicit `--allow-direct-risk` override is available only after review and remains visible in preview warnings.

Official docs:
- https://yandex.ru/dev/metrika/ru/management/openapi/offline_conversions/upload_1
- https://yandex.ru/dev/metrika/ru/management/openapi/call/uploadCalls
- https://yandex.ru/dev/metrika/ru/management/openapi/expense/uploadMultipart

Other Data Import API capabilities, including visitor parameters and CRM clients/orders, are documented for agent reasoning but are outside the executable helper scope of the initial plugin surface.
