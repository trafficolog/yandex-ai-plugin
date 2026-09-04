# Yandex Direct

[**Русский**](README.md) · [English](README.en.md)

Версия `2.0.0`. Service plugin для Яндекс Директа: кампании, Reports API, аудит, ключевые слова/минус-фразы, бюджеты, оптимизация и low-level API workflows.

## Модель выполнения

Предпочтение: compatible connected MCP/app → bundled Python helper → export/file fallback. Consequential изменения всегда проходят `read → analyze → preview → explicit approval → write → verify`.

### Migration 1.x → 2.0.0

`2.0.0` вводит breaking write-safety contract. Старый вызов с одним `--execute` больше не является достаточным разрешением:

```bash
# 1.x — старый контракт
python scripts/yd_api.py campaigns update --params-file update.json --execute

# 2.0.0 — сначала preview
export YANDEX_DIRECT_TOKEN='...'
python scripts/yd_api.py campaigns update --params-file update.json
# затем, только после approval exact preview в следующем пользовательском turn
python scripts/yd_api.py campaigns update --params-file update.json --execute --approve <preview_id>
```

`preview_id` привязан к service, method, `Client-Login`, OAuth auth principal, environment и body. Изменение token, payload или environment требует нового preview/approval. OAuth token передаётся только через `YANDEX_DIRECT_TOKEN`; argv-параметра `--token` в 2.0.0 нет.

## Production и sandbox

По умолчанию helper использует production endpoint `https://api.direct.yandex.com/json/v501/{service}`. Для официального sandbox используйте отдельный флаг:

```bash
python scripts/yd_api.py campaigns get --params '{}' --sandbox
```

Sandbox использует `https://api-sandbox.direct.yandex.com/json/v5/{service}`. Production и sandbox являются разными approval-bound environments: preview из production не авторизует sandbox write и наоборот.

## Transport metadata и ошибки

Live-вызов возвращает исходный JSON Yandex Direct под `result`, а безопасные transport headers — отдельно под `transport`. Поддерживаются `RequestId` → `request_id`, `Units` → `units`, `Units-Used-Login` → `units_used_login`; остальные headers по умолчанию не копируются.

Ожидаемые CLI-ошибки (`validation`, `input`, `network`, `http`, `api`) выводятся как JSON в stderr с exit code `2`, без обычного traceback. HTTP error body ограничен 4096 bytes и декодируется с replacement semantics.

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

- production API использует v501, sandbox — отдельно документированный `/json/v5/` contract;
- service name проходит строгий allowlist до URL construction;
- queued Reports 201/202 повторяют тот же payload/report name и учитывают `retryIn`;
- report artifacts сохраняют goal/attribution/VAT provenance и не выдумывают currency;
- autotargeting и keyword criteria различаются;
- unknown/mutating methods safe-by-default: preview перед execute;
- consequential writes требуют exact `preview_id` approval;
- нет universal CPA/CPC/CTR/ROAS kill rules;
- создание campaign не означает activation.

## Helpers

```bash
export YANDEX_DIRECT_TOKEN='...'
python scripts/yd_api.py campaigns get --params '{"SelectionCriteria":{},"FieldNames":["Id","Name","Status"]}'
python scripts/yd_api.py campaigns update --params-file update.json # preview
python scripts/yd_api.py campaigns update --params-file update.json --execute --approve <preview_id>
python scripts/yd_api.py campaigns get --params '{}' --sandbox
python scripts/yd_report.py campaign 2026-08-01 2026-08-31 --output report.tsv
```

## Проверка

```bash
python -m unittest discover -s tests -v
python -m compileall -q scripts
```

Источники и upstream attribution: `THIRD_PARTY_NOTICES.md`, `references/sources.md`, `references/api-2026.md`.
