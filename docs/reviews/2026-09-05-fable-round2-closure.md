# Закрытие Fable 5.1 Round 2

[**Русский**](2026-09-05-fable-round2-closure.md) · [English](2026-09-05-fable-round2-closure.en.md)

Дата: 2026-09-05  
Scope: cross-check нормативного аудита Fable 5.1 Round 2 после out-of-order remediation последующих раундов.  
PR: #58 (`pre-merge` на момент создания этого артефакта).

Этот документ фиксирует disposition находок. Он не подменяет GitHub PR/release record: exact final branch SHA, exact-head CI, squash-merge SHA, post-merge CI, publisher run и immutable release metadata появляются только после соответствующих событий и поэтому хранятся в PR/release evidence, а не выдумываются здесь заранее.

## Статусы

- **closed** — остаток Round 2 исправлен в remediation `1.0.8`;
- **closed as explicit backlog** — текущая система честно ограничена, а отсутствующая capability получила явные acceptance criteria в ROADMAP без ложного заявления реализации;
- **previously closed** — пункт был закрыт более поздним remediation ещё до cross-check `1.0.8`.

## Матрица находок

| Round 2 finding | Disposition | Evidence class | Текущее состояние |
|---|---|---|---|
| Version drift между manifests/README/SERVICE_MATRIX | previously closed | mechanical + CI | `scripts/version_contracts.py` проверяет canonical version mentions, bilingual contracts и service matrix. |
| SemVer validation обещает больше, чем проверяет | previously closed | mechanical + documentation | Version mention validator теперь охватывает plugin/root README, changelog и SERVICE_MATRIX. |
| Wordstat product/auth naming ambiguity | closed | mechanical doc regression + semantic documentation review | Current docs используют `Wordstat API в составе Yandex Search API v2`; runtime auth не меняется. |
| `_http.py` drift без контроля | previously closed | mechanical behavioral tests | Repository-level HTTP contract tests проверяют redaction, bounded error reads и explicit timeout для service-local adapters. |
| `PLUGIN_STANDARD` без requirement IDs | previously closed | mechanical | `1.0.7` ввёл стабильные requirement IDs и enforcement ownership. |
| Неполный `SKILL.md` content contract | closed | mechanical + semantic/review | `REQ-SKILL-CONTENT` документирует реальные bounds/safety markers и review-level ownership/delegation/limitations semantics. |
| Independent review без артефактов | previously closed | governance + semantic evidence | `docs/reviews/` содержит датированные review artifacts и явно различает AI review, CI и quota limitations. |
| File-level traceability | previously closed | mechanical | `CONTRACT_MATRIX` v2 использует exact test selectors и AST/static-skip validation. |
| Evals объявлены, но model semantic runner отсутствует | closed as explicit backlog | policy + future semantic evidence | ROADMAP фиксирует model eval runner/judge acceptance, включая backend-equivalence; `1.0.8` не заявляет model execution. |
| Per-plugin release tags | previously closed | release evidence | Canonical `yandex-<service>-vX.Y.Z` tags существуют, declarative publisher поддерживает explicit plugin release declarations. |
| `docs/superpowers/` как normative source | closed | mechanical regression + semantic governance | Production plugin README больше не зависит от `docs/superpowers/`; historical specs остаются non-normative context. |
| Copy-paste ON_USE explanation | closed | mechanical documentation ownership | Полное объяснение принадлежит `ARCHITECTURE`; остальные docs используют краткую ссылку/summary. |
| ROADMAP initial/current ambiguity | closed | mechanical doc regression + semantic review | Historical phases маркируются как initial shipment; current versions принадлежат SERVICE_MATRIX/manifests. |
| RU-primary language drift | closed | focused mechanical regression + review policy | Известные EN prose sentences удалены из RU ROADMAP; policy явно различает technical identifiers/terms и обычный prose. |
| Community governance baseline | closed | mechanical existence/bilingual checks + policy | CONTRIBUTING/SECURITY дополнены CODE_OF_CONDUCT и GitHub issue/PR templates без выдуманных контактов/SLA. |
| Wordstat “nine skills” vs capability rows | closed | documentation clarification | ROADMAP говорит о девяти **initial workflow skills**; capability rows не трактуются как количество skills. |
| YandexGPT/SpeechKit naming ambiguity | previously closed | documentation | Root README прямо объясняет, что marketplace предназначен для Yandex services и не является набором plugins для YandexGPT. |
| Backend-independent safety requirement без eval case | closed as explicit backlog | policy + future semantic evidence | Model-eval backlog требует paired MCP/app vs bundled-helper/file case с одинаковым exact-preview + later-turn approval gate. |

## Evidence boundary

**Mechanical evidence** в этом remediation означает repository tests, validator и CI, которые проверяют конкретные статические/структурные contracts. **Semantic evidence** означает review смысла документации, ownership и safety semantics; зелёный CI не считается semantic proof.

До merge этот artifact намеренно не содержит будущие final identifiers. Финальные exact-head и publication facts должны проверяться в PR #58 и immutable release `1.0.8` после их фактического появления.
