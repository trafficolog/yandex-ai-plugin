# Attribution — verified 2026-09-01

Current documented attribution models relevant to Metrika report parameterization:

- `cross_device_first`
- `last`
- `cross_device_last_significant`
- `automatic`

Since 2026-06-25, Yandex maps several legacy attribution requests to current analogues. Do not silently hard-code legacy `lastsign` behavior.

Choose the model for the analytical question and state it in the result. A model change can materially change source/campaign conclusions.

If the caller does not provide an attribution model, the bundled Reporting helper must preserve that omission rather than inventing `last` or another model. Result metadata records `attribution_model: null` with `attribution_provenance: omitted`; an explicitly supplied model is recorded with provenance `explicit`.

Official reference: https://yandex.ru/dev/metrika/ru/stat/param
