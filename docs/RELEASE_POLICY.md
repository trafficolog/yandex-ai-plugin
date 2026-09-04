# Политика релизов

[**Русский**](RELEASE_POLICY.md) · [English](RELEASE_POLICY.en.md)

Документ определяет будущий release process. Он не переписывает исторические tags/releases и не отменяет independent SemVer у plugins.

## 1. Две независимые линии версий

**repository SemVer** — единственная текущая шкала версии marketplace/repository. Новые repository releases используют обычный SemVer `X.Y.Z`.

**plugin SemVer** — независимая версия каждого устанавливаемого plugin. Изменение документации или orchestration repository не должно автоматически повышать версии всех plugins.

## 2. Repository SemVer

Repository release описывает согласованный набор repository-level изменений: документацию, validator/CI contracts, marketplace metadata или другую общую инфраструктуру. Changelog новой работы начинается с repository SemVer, а не с имени модели или фазы.

Patch release используется для совместимых исправлений/документации, minor — для совместимых существенных возможностей repository contract, major — для breaking repository-level contract.

## 3. Plugin SemVer

Plugin меняет версию только когда изменяется его собственный public/runtime/documentation contract в объёме, требующем release. Service tags сохраняют форму `yandex-<service>-vX.Y.Z`.

Repository-only release не создаёт новые plugin tags, если plugin artifacts и contract version не изменились.

## 4. Исторические codenames

`OPUS`, `PHASE`, `DOCS`, `FABLE` — исторические codenames/milestones. Они могут упоминаться как контекст в старых changelog entries и immutable releases, но не образуют конкурирующую будущую шкалу repository version.

Исторические tags/releases не retarget, не delete и не переписываются ради унификации naming.

## 5. Release gates

### AI audit

`AI audit` — advisory input: источник гипотез, edge cases и review questions. Сам по себе аудит модели не доказывает дефект и не разрешает release.

### CI

`CI` — mechanical evidence: validator, tests, compilation и release-contract checks. Green CI подтверждает прохождение этих проверок, но не заменяет semantic review и актуальность внешнего API.

### Independent review

`independent review` — отдельный gate, когда доступен: reviewer проверяет scope, semantics, safety и отсутствие regressions независимо от автора исправления. Если внешний review недоступен из-за quota/tool limitation, это фиксируется явно, а не представляется как clean review.

### Human authorization

`human` decision — разрешение на merge/release. AI audit, CI или reviewer не должны самостоятельно подменять владельца repository в решении о публикации.

### Publication

После human authorization PR merge выполняется с проверкой exact head. Затем post-merge CI должен пройти на точном `main` SHA. Publisher публикует только заранее объявленный release set и проверяет exact tag SHA, immutable release state и idempotent recovery semantics.

## 6. Batching hardening fixes

Небольшие совместимые hardening findings следует по возможности объединять в один patch release вместо серии релизов в течение нескольких часов. Отдельный срочный patch оправдан, если откладывание увеличивает security/safety или correctness risk.

Audit source или codename можно указать в release notes как provenance изменения, но repository version остаётся SemVer.

## 7. Immutable history

Уже опубликованный release считается историческим record. Его tag не переносится на другой commit. Исправление опубликованной версии выпускается новой версией.

Publisher должен fail-closed при conflicting tag/release state, неожиданном target SHA или невозможности доказать remote tag absence.

## 8. Ответственность

- contributor/agent — предлагает изменение и evidence;
- tests/CI — механически проверяют заявленные contracts;
- independent reviewer — ищет semantic/safety gaps;
- human maintainer — принимает решение о merge/release;
- publisher — детерминированно публикует уже разрешённый exact-main artifact.

Связанные документы: [`CONTRIBUTING.md`](../CONTRIBUTING.md), [`REVIEW_FIRST_RELEASE.md`](REVIEW_FIRST_RELEASE.md), [`PLUGIN_STANDARD.md`](PLUGIN_STANDARD.md).
