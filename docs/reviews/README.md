# Артефакты независимого review

[**Русский**](README.md) · [English](README.en.md)

Эта директория хранит проверяемые review-артефакты для repository/plugin releases. Они не заменяют CI, human authorization или canonical production contracts.

## Формат артефакта

Каждый датированный review должен по возможности фиксировать:

- дату и scope;
- тип reviewer: human / external AI / automated reviewer;
- reviewed commit, PR или release, если они известны;
- findings без переписывания их постфактум;
- disposition каждого finding: closed / addressed in current PR / deferred / out of scope;
- exact evidence: commit SHA, CI run ID, review thread или immutable release;
- ограничения reviewer/tool, включая quota, если они повлияли на полноту проверки;
- явное разделение ролей: AI review — semantic/advisory input, CI — mechanical evidence, human maintainer — merge/release authorization.

Отсутствие reviewer или quota/tool limitation **не считается clean review**.

## Артефакты

- [`2026-09-05 — Opus/Codex governance review`](2026-09-05-opus-codex-governance.md) — аудит governance/validator gaps и follow-up review release infrastructure PR #56.

Canonical production requirements находятся в [`PLUGIN_STANDARD.md`](../PLUGIN_STANDARD.md), [`RELEASE_POLICY.md`](../RELEASE_POLICY.md), executable validators/tests, plugin `SKILL.md`/references и machine-owned registries/matrices. Файлы `docs/superpowers/` — исторический implementation context.