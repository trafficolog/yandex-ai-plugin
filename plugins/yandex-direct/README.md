# Yandex Direct

[**Русский**](README.md) · [English](README.en.md)

Версия `1.0.1`. Service plugin для Яндекс Директа: кампании, Reports API, аудит, ключевые слова/минус-фразы, бюджеты, оптимизация и low-level API v501 workflows.

> `DOCS 1.0.0` добавляет двуязычную документацию; версия плагина не изменена.

## Модель выполнения

Предпочтение: compatible connected MCP/app → bundled Python helper → export/file fallback. Consequential изменения всегда проходят `read → analyze → preview → explicit approval → write → verify`.

## Capability matrix

| Capability | Read | Write | MCP/App | Bundled API | File fallback |
|---|---:|---:|---:|---:|---:|
| Campaign discovery / state | yes | — | optional | yes | yes |
| Campaign draft / update payloads | yes | approval | optional | yes | yes |
| Audit | yes | — | optional | yes | yes |
| Reports / KPI analysis | yes | — | optional | yes | yes |
| Keywords / negatives | yes | approval | optional | yes | yes |
| Budget analysis / changes | yes | approval | optional | yes | yes |
| Optimization recommendations / writes | yes | approval | optional | yes | yes |

## Skills

`yandex-direct` router; `yandex-direct-create`; `yandex-direct-audit`; `yandex-direct-reporting`; `yandex-direct-optimize`; `yandex-direct-keywords`; `yandex-direct-budget`; `yandex-direct-api`.

## Ключевые correctness rules

- v501 и ЕПК-first mental model для новых performance workflows;
- queued Reports 201/202 повторяют тот же payload/report name и учитывают `retryIn`;
- report artifacts сохраняют goal/attribution/VAT provenance и не выдумывают currency;
- autotargeting и keyword criteria различаются;
- unknown/mutating methods safe-by-default: preview перед execute;
- нет universal CPA/CPC/CTR/ROAS kill rules;
- создание campaign не означает activation.

## Helpers

```bash
export YANDEX_DIRECT_TOKEN='...'
python scripts/yd_api.py campaigns get --params '{"SelectionCriteria":{},"FieldNames":["Id","Name","Status"]}'
python scripts/yd_api.py campaigns update --params-file update.json          # preview
python scripts/yd_api.py campaigns update --params-file update.json --execute # только после approval
python scripts/yd_report.py campaign 2026-08-01 2026-08-31 --output report.tsv
```

## Проверка

```bash
python -m unittest discover -s tests -v
python -m py_compile scripts/yd_api.py scripts/yd_report.py
```

Источники и upstream attribution: `THIRD_PARTY_NOTICES.md`, `references/sources.md`.