# Yandex Metrika

[**Русский**](README.md) · [English](README.en.md)

Версия `1.0.1`. Service plugin для аналитики Яндекс Метрики: reporting, conversions, ecommerce, attribution, goals, Logs API, imports и low-level Management API.

> `DOCS 1.0.0` меняет только документацию.

## Capability matrix

| Capability | Read | Write | MCP/App | Bundled API | File fallback |
|---|---:|---:|---:|---:|---:|
| Reporting / attribution / quality | yes | no | optional | yes | yes |
| Goals management | yes | approval | optional | yes | preview |
| Logs API lifecycle | yes | preview-first | optional | yes | yes |
| Offline conversions / calls / expenses import | preview | approval | optional | yes | yes |
| Raw Management API operations | yes | approval | optional | yes | preview |

## Ключевые контракты

- omitted attribution сохраняется как omitted provenance, а не заменяется выдуманным default;
- sampling, sample share, data lag и другие quality fields являются частью результата;
- Logs lifecycle explicit: evaluate → create → status → download → clean;
- imports защищены от duplicate-risk для native Yandex Direct expenses;
- goal mutations preview-first;
- cross-service consumers должны сохранять quality limitations.

## Skills

`yandex-metrika`, `-audit`, `-reporting`, `-conversions`, `-ecommerce`, `-attribution`, `-goals`, `-logs`, `-imports`, `-api`.

## Credentials и проверка

Используйте `YANDEX_METRIKA_TOKEN` локально или credentials connected app; реальные токены не коммитятся.

```bash
python -m unittest discover -s tests -v
```
