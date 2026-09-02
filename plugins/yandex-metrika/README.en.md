# Yandex Metrika

[Русский](README.md) · [**English**](README.en.md)

Version `1.0.2`. Service plugin for Yandex Metrika reporting, conversions, ecommerce, attribution, goals, Logs API, imports and low-level Management API workflows.

## Capability matrix

| Capability | Read | Write | MCP/App | Bundled API | File fallback |
|---|---:|---:|---:|---:|---:|
| Reporting / attribution / quality | yes | no | optional | yes | yes |
| Goals management | yes | approval | optional | yes | preview |
| Logs API lifecycle | yes | preview-first | optional | yes | yes |
| Offline conversions / calls / expenses import | preview | approval | optional | yes | yes |
| Raw Management API operations | yes | approval | optional | yes | preview |

## Key contracts

- omitted attribution remains explicit omission provenance rather than an invented default;
- sampling, sample share, data lag and quality fields are part of the result contract;
- Logs lifecycle is explicit: evaluate → create → status → download → clean;
- imports guard against duplicate native Yandex Direct expenses;
- the 1.0.2 expense guard rejects exact aliases and tokenized labels (`Yandex Direct RU`, `direct_ads`, `Яндекс Директ агентство`) and independently inspects CSV `UTMSource`/`UTMMedium` content;
- an arbitrary substring such as `MyDirect` is not treated as proven Direct provenance by label alone;
- goal mutations are preview-first;
- cross-service consumers preserve quality limitations.

## Skills

`yandex-metrika`, `-audit`, `-reporting`, `-conversions`, `-ecommerce`, `-attribution`, `-goals`, `-logs`, `-imports`, `-api`.

## Credentials and verification

Use `YANDEX_METRIKA_TOKEN` locally or connected-app credentials; never commit real tokens.

```bash
python -m unittest discover -s tests -v
```
