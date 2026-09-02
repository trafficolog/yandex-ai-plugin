# Стандарт Yandex AI Plugin

[**Русский**](PLUGIN_STANDARD.md) · [English](PLUGIN_STANDARD.en.md)

Этот документ задаёт repository-wide contract для production plugins под `plugins/`.

## 1. Обязательная структура

```text
plugins/yandex-<service>/
├── .codex-plugin/plugin.json
├── .claude-plugin/plugin.json
├── skills/
├── references/
├── scripts/
├── tests/
├── evals/
├── README.md
├── README.en.md
├── CHANGELOG.md
├── CHANGELOG.en.md
└── THIRD_PARTY_NOTICES.md
```

Plugin — граница установки и versioning. `SKILL.md` — discoverable unit знаний/workflow.

## 2. Production requirements

Каждый plugin MUST: иметь router и task-specific skills; хранить volatile API facts в references; тестировать bundled code; иметь offline eval expectations; быть read-first; preview/dry-run consequential writes; требовать explicit approval; не хранить secrets; иметь capability matrix; использовать independent SemVer; не кодировать universal business thresholds; не использовать runtime-specific home paths; сохранять source-specific semantics; а cross-service plugins — оставаться transport-free.

Дополнительно documentation contract требует RU-primary `README.md`/`CHANGELOG.md` и English `README.en.md`/`CHANGELOG.en.md` с reciprocal language links. Release markers RU/EN changelog должны совпадать. Repository key docs используют такой же `.en.md` convention. Documentation-only repository release не повышает SemVer плагина.

## 3. Safety contract

```text
read → analyze → preview → explicit approval → write → verify
```

Recommendation не является permission. Draft creation отделено от activation/publication.

## 4. Execution abstraction

Preferred order: compatible connected MCP/app → bundled helper → user-provided export/file. Reasoning и safety semantics не должны зависеть от backend.

Cross-service plugins могут создавать delegated previews, но не владеют transport или service credentials.

## 5. Skill conventions

```yaml
---
name: yandex-service-task
description: Use when ...
---
```

Описание начинается с `Use when`. References содержат длинные/изменчивые API facts.

## 6. API freshness

Official Yandex documentation — canonical source. Platform facts в freshness-controlled references содержат verification marker и проходят deterministic 90-day gate.

## 7. Capability matrix

Каждый plugin README должен содержать минимум:

| Capability | Read | Write | MCP/App | Bundled API | File fallback |
|---|---:|---:|---:|---:|---:|
| Example capability | yes | approval | optional | yes | yes |

Для consequential writes используйте `approval`; cross-service writes описываются как delegated preview/approval in owning plugin.

## 8. Versioning

Plugins version independently with SemVer. Structural/documentation repository changes не обязаны менять plugin version.

Recommended service tags: `yandex-direct-v1.1.0`, `yandex-metrika-v1.0.0`. Repository milestones могут иметь собственные tags (`opus-*`, `docs-*`).

## 9. Tests and evals

Executable helpers имеют unit tests. `evals/scenarios.json` содержит machine-verifiable `expect`: `must_route_to`, `must_refuse`, `must_mention`, `must_not_claim`; allowed write values: `false`, `preview-first`, `approval-required`.

## 10. Shared code rule

Не выносить код в `packages/` только из-за сходства. Shared package появляется, когда одинаковая responsibility реализована минимум в двух plugins и interface стабилен.

## 11. CI contract

Validator проверяет оба marketplace format, manifest families, SemVer consistency, capability matrices, evals, secrets/paths, cross-service no-transport boundary, bilingual documentation pairs и changelog release-marker parity. Path-aware CI моделирует producer → consumer dependencies.