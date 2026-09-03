# Yandex Metrika

[Русский](README.md) · [**English**](README.en.md)

Version `1.0.3`. Service plugin for Yandex Metrika reporting, conversions, ecommerce, attribution, goals, Logs API, imports and low-level Management API workflows.

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
- the `1.0.3` expense guard classifies CSV provenance as `DIRECT`, `NON_DIRECT`, or `UNVERIFIED` from UTM and `TrafficSource` / `TrafficSourceDetail` evidence;
- official `TrafficSourceDetail=yandex_direct_star` is blocked as `DIRECT_DUPLICATION_RISK` even when `UTMSource` / `UTMMedium` are absent;
- generic advertising provenance without enough source detail is blocked as `DIRECT_SOURCE_UNVERIFIED` until explicit review/override;
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
