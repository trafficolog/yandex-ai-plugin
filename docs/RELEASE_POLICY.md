# Политика релизов

[**Русский**](RELEASE_POLICY.md) · [English](RELEASE_POLICY.en.md)

Документ определяет текущий release process. Он не переписывает исторические tags/releases и не отменяет independent SemVer у plugins.

## 1. Две независимые линии версий

**repository SemVer** — единственная текущая шкала версии marketplace/repository. Новые repository releases используют обычный SemVer `X.Y.Z`.

**plugin SemVer** — независимая версия каждого устанавливаемого plugin. Изменение документации или orchestration repository не должно автоматически повышать версии всех plugins.

## 2. Repository SemVer и release set

Repository release описывает согласованный release set: repository-level изменения и, при необходимости, явно перечисленные plugin releases. Changelog новой работы начинается с repository SemVer, а не с имени модели или фазы.

Patch release используется для совместимых исправлений/документации, minor — для совместимых существенных возможностей repository contract, major — для breaking repository-level contract.

**Каждый новый release set получает новый repository SemVer и новый repository tag.** Уже immutable repository release нельзя повторно использовать, чтобы позже добавить к нему plugin release. Это сохраняет однозначную связь release set → exact commit.

## 3. Plugin SemVer

Plugin меняет версию только когда изменяется его собственный public/runtime/documentation contract в объёме, требующем release. Service tags сохраняют форму `yandex-<service>-vX.Y.Z`.

Repository-only release не создаёт новые plugin tags, если plugin artifacts и contract version не изменились. В declarative manifest значение `plugins: []` явно означает repository-only release и запрещает создание нового plugin tag этим release set.

## 4. Declarative release manifest

Human-approved release intent хранится в [`.github/releases/release.json`](../.github/releases/release.json). Manifest объявляет repository version/tag/title/notes и опциональный список plugin releases. Он не вычисляется автоматически из changed files: отсутствие plugin entry означает отсутствие разрешения на его публикацию.

Единственный automatic publisher в current default branch — [`.github/workflows/publish-current-release.yml`](../.github/workflows/publish-current-release.yml). Workflow владеет общей механикой публикации, а manifest — составом конкретного release set. Следующий release меняет manifest/notes/version surfaces, а не добавляет новый publisher workflow.

Publisher и CI используют repository-owned manifest validator `scripts/release_manifest.py`, чтобы schema, SemVer, notes paths, plugin versions и canonical plugin tags интерпретировались одинаково.

## 5. Исторические codenames и publisher source

`OPUS`, `PHASE`, `DOCS`, `FABLE` — исторические codenames/milestones. Они могут упоминаться как контекст в старых changelog entries и immutable releases, но не образуют конкурирующую будущую шкалу repository version.

Исторические tags/releases не retarget, не delete и не переписываются ради унификации naming.

После того как historical release стал immutable, соответствующий **historical publisher** YAML удаляется из активного workflow set текущего default branch. Его исходный код не теряется: точная версия остаётся доступна через **Git history** и immutable release tag/commit. Копировать такие workflows в executable `archive/` внутри current tip не требуется.

## 6. Release gates

### AI audit

`AI audit` — advisory input: источник гипотез, edge cases и review questions. Сам по себе аудит модели не доказывает дефект и не разрешает release.

### CI

`CI` — mechanical evidence: validator, tests, compilation и release-contract checks. Green CI подтверждает прохождение этих проверок, но не заменяет semantic review и актуальность внешнего API.

### Independent review

`independent review` — отдельный gate, когда доступен: reviewer проверяет scope, semantics, safety и отсутствие regressions независимо от автора исправления. Если внешний review недоступен из-за quota/tool limitation, это фиксируется явно, а не представляется как clean review.

### Human authorization

`human` decision — разрешение на merge/release. AI audit, CI или reviewer не должны самостоятельно подменять владельца repository в решении о публикации.

### Publication

После human authorization PR merge выполняется с проверкой exact head. Затем post-merge CI должен пройти на точном `main` SHA. `publish-current-release.yml` читает только объявленный release set, проверяет exact tag SHA, immutable release state и idempotent recovery semantics и не добавляет release items по собственной инициативе.

## 7. Publisher safety contract

Для initial publication publisher требует, чтобы successful CI SHA оставался текущим `main`; stale initial run завершается verified no-op. Recovery уже существующего draft/immutable state разрешён только для одного common target, который остаётся ancestor live `main`.

Remote tag absence проверяется fail-closed: transport/auth/probe error не считается отсутствием tag. Standalone tag, published-but-mutable release, conflicting targets и неоднозначный recovery state являются hard failure.

Rollback вооружается только на mutable publication window. Перед destructive cleanup publisher повторно проверяет `isImmutable`; сразу после подтверждения immutability rollback отключается до любых последующих tag/target probes. Immutable release не удаляется rollback-механизмом.

## 8. Batching hardening fixes

Небольшие совместимые hardening findings следует по возможности объединять в один patch release вместо серии релизов в течение нескольких часов. Отдельный срочный patch оправдан, если откладывание увеличивает security/safety или correctness risk.

Audit source или codename можно указать в release notes как provenance изменения, но repository version остаётся SemVer.

## 9. Immutable history

Уже опубликованный release считается историческим immutable record. Его tag не переносится на другой commit. Исправление опубликованной версии выпускается новой версией.

Publisher должен fail-closed при conflicting tag/release state, неожиданном target SHA или невозможности доказать remote tag absence. Никакой normal release flow не изменяет предыдущий immutable release ради синхронизации с новым `main`.

## 10. Ответственность

- contributor/agent — предлагает изменение и evidence;
- human-approved `.github/releases/release.json` — определяет конкретный release set;
- tests/CI — механически проверяют заявленные contracts;
- independent reviewer — ищет semantic/safety gaps;
- human maintainer — принимает решение о merge/release;
- `publish-current-release.yml` — детерминированно reconciles уже разрешённый exact-main release set.

Связанные документы: [`CONTRIBUTING.md`](../CONTRIBUTING.md), [`REVIEW_FIRST_RELEASE.md`](REVIEW_FIRST_RELEASE.md), [`PLUGIN_STANDARD.md`](PLUGIN_STANDARD.md).
