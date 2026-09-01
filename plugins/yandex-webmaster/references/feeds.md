# Feeds — verified 2026-09-01

Feed management applies to HTTPS sites. Relevant resources include:

- `GET .../feeds/list`
- `POST .../feeds/add/start` — asynchronous add, returns `requestId`.
- `GET .../feeds/add/info?requestId=...` — async status.
- `POST .../feeds/batch/add` — up to 50 feeds.
- `DELETE .../feeds/batch/remove` — remove feeds.

Feed add/delete changes Webmaster configuration. Validate target host and feed URLs, preview the exact payload, require approval, then verify resulting status. Deleting feeds is destructive.
