# Yandex Direct Suite — plugin из skills

Актуализированный на **1 сентября 2026 года** skill-only plugin для работы с Яндекс Директом: создание новой ЕПК, аудит, отчётность, оптимизация, семантика/минус-фразы, бюджет и низкоуровневые API v501 операции.

Проект сделан как новая модульная реализация на базе идей двух open-source проектов:

- `Silverov/yandex-direct-skill` — аудит, отчёты, бюджет, оптимизация;
- `ai-hub-open/yandex-direct-manager` 0.12.1 — современный workflow создания кампании и подход с артефактами/гейтами.

Актуальные API-факты дополнительно сверены с официальной документацией Яндекс Директа.

## Почему это plugin, а не один SKILL.md

Исходные проекты загружают большой универсальный skill. Здесь задачи разделены, чтобы агент подтягивал только нужную методику:

| Skill | Для чего |
|---|---|
| `yandex-direct` | router для общих запросов |
| `yandex-direct-create` | новая кампания / ЕПК до preflight и draft |
| `yandex-direct-audit` | аудит аккаунта и кампаний |
| `yandex-direct-reporting` | Reports API, KPI, сравнение периодов |
| `yandex-direct-optimize` | оптимизация существующих кампаний |
| `yandex-direct-keywords` | ключи, запросы, минусы, автотаргетинг |
| `yandex-direct-budget` | pace, forecast, распределение бюджета |
| `yandex-direct-api` | raw API v501, payloads, debugging |

Общие меняющиеся факты вынесены в `references/`, поэтому их можно обновлять без разрастания каждого skill.

## Что обновлено относительно февральского yandex-direct-skill

- новый default endpoint — `https://api.direct.yandex.com/json/v501/` для ЕПК и актуальных workflow;
- ЕПК / Unified Performance Campaign рассматривается как default-модель для новых performance-кампаний;
- Reports polling исправлен: при 201/202 повторяется **тот же запрос**, учитывается `retryIn`;
- текущие поля criteria-report используют `Criterion`, `CriterionId`, `CriterionType`;
- автотаргетинг (`---autotargeting`) рассматривается отдельно от обычных ключей;
- поддерживается логика `NegativeKeywordSharedSets` v501;
- из аудита убраны устаревающие универсальные требования: обязательное разделение Search/РСЯ, «2 объявления на группу», фиксированный CTR, жёсткий `3× CPA kill rule`;
- write-операции отделены от рекомендаций: read → preview → explicit approval → write;
- создание кампании не означает её активацию.

## OpenAI Plugin / marketplace

Этот каталог является отдельным plugin внутри monorepo `trafficolog/yandex-ai-plugin`:

```text
plugins/yandex-direct/
├── .codex-plugin/plugin.json
├── .claude-plugin/plugin.json
├── skills/*/SKILL.md
├── references/
├── scripts/
├── tests/
└── evals/
```

Marketplace принадлежит корню репозитория: `../../.agents/plugins/marketplace.json`. Он публикует Direct как независимый устанавливаемый plugin и позже будет перечислять другие сервисы Яндекса.

Это **skill-only plugin**: он не подключает Yandex Direct как ChatGPT app автоматически. Для прямых live API-вызовов используйте среду, которая может запускать bundled scripts (например Codex/local agent) или совместимый Yandex Direct MCP/app. При отсутствии live-доступа skills работают с выгрузками и формируют воспроизводимый plan/preview изменений.

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

`approval` означает explicit approval непосредственно перед consequential live-write.

## Live API helper

Переменные окружения:

```bash
export YANDEX_DIRECT_TOKEN='...'
export YANDEX_DIRECT_CLIENT_LOGIN='...'   # optional for agency client
```

Read:

```bash
python scripts/yd_api.py campaigns get \
  --params '{"SelectionCriteria":{},"FieldNames":["Id","Name","Status","State","Type"]}'
```

Write по умолчанию — только preview:

```bash
python scripts/yd_api.py campaigns update --params-file update.json
```

После проверки payload:

```bash
python scripts/yd_api.py campaigns update --params-file update.json --execute
```

## Reports helper

```bash
python scripts/yd_report.py campaign 2026-08-01 2026-08-31 --output report.tsv
python scripts/yd_report.py search_query 2026-08-01 2026-08-31 --output queries.tsv
```

Helper использует v501, `returnMoneyInMicros: false`, сохраняет один `ReportName` на весь polling и ждёт `retryIn` для offline-report.

## Тесты

```bash
python -m unittest discover -s tests -v
```

Тесты не обращаются к сети и не читают реальные токены.

## Структура

```text
plugins/yandex-direct/
├── .codex-plugin/plugin.json
├── .claude-plugin/plugin.json
├── .env.example
├── skills/
│   ├── yandex-direct/
│   ├── yandex-direct-api/
│   ├── yandex-direct-audit/
│   ├── yandex-direct-budget/
│   ├── yandex-direct-create/
│   ├── yandex-direct-keywords/
│   ├── yandex-direct-optimize/
│   └── yandex-direct-reporting/
├── references/
├── scripts/
├── tests/
└── evals/
```

## Лицензия и источники

Новая реализация распространяется по MIT. Происхождение идей и upstream-проекты перечислены в `THIRD_PARTY_NOTICES.md` и `references/sources.md`.
