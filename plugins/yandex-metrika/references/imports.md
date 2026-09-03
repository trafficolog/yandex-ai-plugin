# Data imports — verified 2026-09-03

Initial executable helper coverage:

- offline conversions: `POST /management/v1/counter/{counterId}/offline_conversions/upload`
- calls: `POST /management/v1/counter/{counterId}/offline_conversions/upload_calls`
- expenses: `POST /management/v1/counter/{counterId}/expense/upload`

All three use multipart CSV uploads. Validate UTF-8, headers, row count, target counter and query parameters before upload. Processing is asynchronous for some imports; after upload, use the corresponding status endpoint before assuming the data is available in reports.

## Critical Direct-cost guard

Do not manually upload Yandex Direct expenses. Direct transfers its cost data to Metrika automatically; a manual upload can duplicate those expenses and make reports incorrect.

The expense CSV format can identify acquisition provenance through either UTM fields or Metrika traffic-source fields. The official expense schema accepts `UTMSource` or `TrafficSource`; `TrafficSourceDetail` is the source-detail discriminator. For advertising traffic, Yandex Direct is represented by `TrafficSource=ad` with `TrafficSourceDetail=yandex_direct_star`.

The bundled expense helper applies complementary risk layers:

1. **Source-label guard.** Exact aliases and explicit tokenized Direct labels are rejected, including forms such as `Yandex Direct RU`, `direct_ads` and `Яндекс Директ агентство`. Arbitrary concatenations such as `MyDirect` are not treated as proven Direct provenance solely because they contain the substring `direct`.
2. **CSV provenance classification.** Rows are classified as `DIRECT`, `NON_DIRECT` or `UNVERIFIED` from `UTMSource`/`UTMMedium` and `TrafficSource`/`TrafficSourceDetail`. Direct-like UTM combinations and the official `yandex_direct_star` detail raise `DIRECT_DUPLICATION_RISK`.
3. **Insufficient-evidence guard.** Generic advertising rows such as `TrafficSource=ad` without a source detail, or otherwise incomplete source evidence, raise `DIRECT_SOURCE_UNVERIFIED`. They require the same explicit `--allow-direct-risk` override after provenance review rather than silently passing the Direct duplication guard.

Explicit non-Direct evidence remains allowed. For example, `TrafficSource=ad` plus another documented provider detail such as `google_adwords` does not become Direct merely because it is advertising traffic.

The content layer is deliberately stronger than human provider-label naming. An explicit `--allow-direct-risk` override is available only after review and remains visible in preview warnings.

Official docs:
- https://yandex.ru/dev/metrika/ru/management/openapi/offline_conversions/upload_1
- https://yandex.ru/dev/metrika/ru/management/openapi/call/uploadCalls
- https://yandex.ru/dev/metrika/ru/management/openapi/expense/uploadMultipart
- https://yandex.ru/dev/metrika/ru/management/openapi/expense/traffic-source

Other Data Import API capabilities, including visitor parameters and CRM clients/orders, are documented for agent reasoning but are outside the executable helper scope of the initial plugin surface.
