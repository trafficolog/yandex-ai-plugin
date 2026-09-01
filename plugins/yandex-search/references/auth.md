# Authentication

Use either `Authorization: Api-Key <key>` or `Authorization: Bearer <IAM token>`. Do not log secrets. API keys for the current Search API use scope `yc.search-api.execute`; the service account needs `search-api.webSearch.user`. `folderId` is required by the bundled request builder.
