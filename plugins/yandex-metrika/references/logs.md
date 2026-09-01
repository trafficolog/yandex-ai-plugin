# Logs API — verified 2026-09-01

Use the documented lifecycle:

1. `GET .../logrequests/evaluate` when feasibility/quota is uncertain.
2. `POST .../logrequests` to create the request.
3. `GET .../logrequest/{requestId}` until status is `processed`.
4. Download every part from `.../part/{partNumber}/download`.
5. After successful download, `POST .../clean` to free prepared-log space.

A single request must cover no more than one year. The create endpoint accepts `date1`, `date2`, comma-separated `fields`, `source=hits|visits`, and optional attribution as query parameters. Logs API does not support request-level filtering.

Create and clean mutate server-side state; preview/approval is required. Raw parts should be saved to files rather than printed into the agent context.

Official docs:
- https://yandex.ru/dev/metrika/ru/logs/practice/quick-start
- https://yandex.ru/dev/metrika/ru/logs/openapi/evaluate
- https://yandex.ru/dev/metrika/ru/logs/openapi/createLogRequest
