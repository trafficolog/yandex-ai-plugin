# Reporting API — verified 2026-09-01

Current report families used by the helper:

- table: `https://api-metrika.yandex.net/stat/v1/data`
- by time: `/stat/v1/data/bytime`
- comparison: `/stat/v1/data/comparison`
- drilldown: `/stat/v1/data/drilldown`
- comparison drilldown: `/stat/v1/data/comparison/drilldown`

Always preserve the requested counter, date range, filters, metrics, dimensions and accuracy. When the response contains sampling/quality metadata, expose it with the analysis: `sampled`, `sample_share`, `sample_size`, `sample_space`, `data_lag`, `contains_sensitive_data`, `total_rows_rounded`.

Do not describe sampled or disclosure-limited values as exact without qualification.

Official docs:
- https://yandex.ru/dev/metrika/ru/stat/
- https://yandex.ru/dev/metrika/ru/stat/openapi/data
- https://yandex.ru/dev/metrika/ru/stat/openapi/bytime
- https://yandex.ru/dev/metrika/ru/stat/openapi/drilldown
- https://yandex.ru/dev/metrika/ru/stat/openapi/comparison_drilldown
