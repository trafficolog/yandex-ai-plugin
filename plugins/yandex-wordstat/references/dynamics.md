# Dynamics

Cloud REST endpoint: `/v2/wordstat/dynamics`.

Payload fields use camelCase: `fromDate`, `toDate`; supported bundled periods are `PERIOD_MONTHLY` and `PERIOD_WEEKLY`.

Validate date order and operator compatibility before sending a paid request. Normalize `count` to integer and `share` to float. Dynamics is historical and must not be described as a trailing-30-day-only dataset.
