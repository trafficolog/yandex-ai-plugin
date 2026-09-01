# Data imports — verified 2026-09-01

Initial executable helper coverage:

- offline conversions: `POST /management/v1/counter/{counterId}/offline_conversions/upload`
- calls: `POST /management/v1/counter/{counterId}/offline_conversions/upload_calls`
- expenses: `POST /management/v1/counter/{counterId}/expense/upload`

All three use multipart CSV uploads. Validate UTF-8, headers, row count, target counter and query parameters before upload. Processing is asynchronous for some imports; after upload, use the corresponding status endpoint before assuming the data is available in reports.

## Critical Direct-cost guard

Do not manually upload Yandex Direct expenses. Direct transfers its cost data to Metrika automatically; a manual upload can duplicate those expenses and make reports incorrect.

Official docs:
- https://yandex.ru/dev/metrika/ru/management/openapi/offline_conversions/upload_1
- https://yandex.ru/dev/metrika/ru/management/openapi/call/uploadCalls
- https://yandex.ru/dev/metrika/ru/management/openapi/expense/uploadMultipart

Other Data Import API capabilities, including visitor parameters and CRM clients/orders, are documented for agent reasoning but are outside the executable helper scope of plugin 1.0.0.
