# 2026-09-05 — Opus/Codex governance review

[**Русский**](2026-09-05-opus-codex-governance.md) · [English](2026-09-05-opus-codex-governance.en.md)

## Scope и роли

Этот артефакт объединяет две независимые линии review, повлиявшие на текущий repository governance:

1. **Opus 5 audit** — внешний AI-аудит repository contracts, validator coverage, release/docs consistency и traceability. Это advisory semantic review, а не merge permission.
2. **Codex review PR #56** — automated independent review declarative release publisher. Его findings закрывались отдельными RED→GREEN циклами.

**CI** в этом артефакте означает mechanical evidence. **Human maintainer** отдельно принимает решение о merge/release. Ни AI review, ни зелёный CI не подменяют human authorization.

## Opus 5: findings и disposition

Аудит выявил разрыв между заявленными repository guarantees и механическим enforcement. Среди проверенных им проблем были: обходимость cross-service transport detection, неполный secret scanning, слабая проверка `SKILL.md`, drift version surfaces/release markers, формальная bilingual validation и ограниченная contract traceability.

Предыдущие maintenance releases до repository `1.0.6` закрыли runtime/validator части этого списка: cross-service transport ownership, secret patterns, skill contracts, version/documentation consistency, bilingual checks и единый repository release governance. PR C не открывает их заново и не меняет plugin runtime.

Оставшийся governance gap, адресуемый PR C / repository `1.0.7`:

- `CONTRACT_MATRIX` v1 указывал regression-test **файл**, но не exact test function/method;
- production requirements были плотным prose-блоком без стабильных requirement IDs и явного enforcement ownership;
- review evidence не имело repository-owned датированного артефакта;
- отсутствовал repository `SECURITY` policy;
- `docs/superpowers/` требовалось явно отделить как historical implementation context от canonical production requirements.

Function-level traceability в PR C использует exact selectors и Python AST. Это усиливает metadata integrity, но всё равно не объявляется semantic proof assertions.

## Codex review PR #56

Первый Codex review был выполнен на reviewed head:

`130050f11b2612a01ca6909215dbf30952a89d45`

Он нашёл три actionable finding:

- **P1:** TSV record injection через tab/newline в release manifest scalars;
- **P1:** rollback мог пытаться destructive cleanup, когда immutability probe не доказал mutable state;
- **P2:** generic release manifest validation не выводила README/CHANGELOG version surfaces из `repository.version`.

Все три finding получили regression tests и RED→GREEN closure. Candidate head после исправлений:

`23a14d9b9e51825b96286bf6f9a8d4244d035ebe`

Exact-head CI:

- `33953946792` — 10/10 jobs success.

Затем PR #56 был squash-merged. Main/merge SHA:

`88d2f45e63308a476cbe456402bf17dc847436cb`

Post-merge mechanical evidence:

- CI `33954164035` — 10/10 jobs success;
- generic publisher `33954198278` — success;
- Repository `1.0.6` опубликован immutable на exact merge SHA.

## Reviewer limitation

После закрытия трёх Codex findings был запрошен новый exact-head re-review на `23a14d9b9e51825b96286bf6f9a8d4244d035ebe`. Codex сообщил о достигнутом **code-review quota** limit.

Поэтому финальный head PR #56 **не имеет заявленного clean Codex re-review**. Ограничение было зафиксировано в PR; reviewed-head → candidate-head delta отдельно проверялся и состоял только из fixes/regressions по найденным P1/P2. Это documented reviewer/tool limitation, а не положительный review result.

## Что этот артефакт доказывает и чего не доказывает

Доказывает traceability review history: кто/что проверялось, какие findings были зафиксированы, какие exact SHAs и CI runs связаны с closure, где reviewer был недоступен.

Не доказывает:

- что AI reviewer исчерпывающе проверил весь repository;
- что CI является semantic review;
- что current external Yandex API behavior автоматически подтверждён;
- что наличие exact test selector означает корректную семантику assertions.

Canonical требования остаются в `PLUGIN_STANDARD`, `RELEASE_POLICY`, executable validators/tests, plugin contracts и machine-owned registries/matrices.