# Authentication

Cloud Wordstat follows Yandex Search API authentication.

- Service-account API key: `Authorization: Api-Key <key>`.
- IAM token: `Authorization: Bearer <IAM token>`.
- Required role baseline: `search-api.webSearch.user`.
- API keys should have `yc.search-api.execute` scope where applicable.

Bundled helper variables:

- `YANDEX_WORDSTAT_API_KEY`
- `YANDEX_WORDSTAT_IAM_TOKEN`
- `YANDEX_WORDSTAT_FOLDER_ID`

API key and IAM token are mutually exclusive. `folderId` is optional for service-account credentials but can be required for other IAM flows; never assume a fixed 20-character length.
