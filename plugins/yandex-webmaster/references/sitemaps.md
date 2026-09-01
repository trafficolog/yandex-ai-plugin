# Sitemaps — verified 2026-09-01

Distinguish discovered sitemaps, user-added sitemaps and sitemap indexes. Sources can include robots.txt, Webmaster and parent sitemap/index relationships.

Standard resources remain under `/v4/`:

- `GET .../sitemaps`
- `GET/POST .../user-added-sitemaps`
- delete a specific user-added sitemap by ID using the documented user-added sitemap resource.

Priority recrawl is a v4.1 feature:

- `GET /v4.1/.../sitemaps/recrawl`
- `POST /v4.1/.../sitemaps/{sitemap-id}/recrawl`

Priority recrawl is limited to no more than 10 requests per month. Preserve `monthly_limit_requests`, `requests_count`, `nearest_allowed_day`, `pending` and `allowed` when returned. Do not submit when the API says a new request is not allowed.
