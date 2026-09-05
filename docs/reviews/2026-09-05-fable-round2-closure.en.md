# Fable 5.1 Round 2 Closure

[Русский](2026-09-05-fable-round2-closure.md) · [**English**](2026-09-05-fable-round2-closure.en.md)

Date: 2026-09-05  
Scope: cross-check of the Fable 5.1 Round 2 normative audit after later audit rounds were remediated out of order.  
PR: #58 (`pre-merge` when this artifact was created).

This document records finding disposition. It does not replace the GitHub PR/release record: the exact final branch SHA, exact-head CI, squash-merge SHA, post-merge CI, publisher run, and immutable release metadata exist only after those events and therefore belong in PR/release evidence rather than being invented here in advance.

## Statuses

- **closed** — the Round 2 residual is fixed by the `1.0.8` remediation;
- **closed as explicit backlog** — the current system remains truthfully limited while the missing capability now has explicit ROADMAP acceptance criteria without a false implementation claim;
- **previously closed** — the finding was already closed by later remediation before the `1.0.8` cross-check.

## Finding matrix

| Round 2 finding | Disposition | Evidence class | Current state |
|---|---|---|---|
| Version drift across manifests/README/SERVICE_MATRIX | previously closed | mechanical + CI | `scripts/version_contracts.py` checks canonical version mentions, bilingual contracts, and the service matrix. |
| SemVer validation promises more than it checks | previously closed | mechanical + documentation | Version mention validation now covers plugin/root README, changelog, and SERVICE_MATRIX surfaces. |
| Wordstat product/auth naming ambiguity | closed | mechanical doc regression + semantic documentation review | Current docs use `Wordstat API within Yandex Search API v2`; runtime authentication does not change. |
| `_http.py` drift without controls | previously closed | mechanical behavioral tests | Repository-level HTTP contract tests cover redaction, bounded error reads, and explicit timeout across service-local adapters. |
| `PLUGIN_STANDARD` lacks requirement IDs | previously closed | mechanical | `1.0.7` introduced stable requirement IDs and enforcement ownership. |
| Incomplete `SKILL.md` content contract | closed | mechanical + semantic/review | `REQ-SKILL-CONTENT` documents real bounds/safety markers plus review-level ownership/delegation/limitations semantics. |
| Independent review lacks artifacts | previously closed | governance + semantic evidence | `docs/reviews/` stores dated review artifacts and explicitly distinguishes AI review, CI, and quota limitations. |
| File-level traceability | previously closed | mechanical | `CONTRACT_MATRIX` v2 uses exact test selectors and AST/static-skip validation. |
| Evals exist but model semantic runner does not | closed as explicit backlog | policy + future semantic evidence | ROADMAP defines model eval runner/judge acceptance including backend-equivalence; `1.0.8` does not claim model execution. |
| Per-plugin release tags | previously closed | release evidence | Canonical `yandex-<service>-vX.Y.Z` tags exist and the declarative publisher supports explicit plugin release declarations. |
| `docs/superpowers/` as normative source | closed | mechanical regression + semantic governance | Production plugin READMEs no longer depend on `docs/superpowers/`; historical specs remain non-normative context. |
| Copy-pasted ON_USE explanation | closed | mechanical documentation ownership | The full explanation is owned by `ARCHITECTURE`; other docs use a concise link/summary. |
| ROADMAP initial/current ambiguity | closed | mechanical doc regression + semantic review | Historical phases are marked as initial shipments; current versions are owned by SERVICE_MATRIX/manifests. |
| RU-primary language drift | closed | focused mechanical regression + review policy | Known English prose sentences are removed from RU ROADMAP and policy distinguishes technical identifiers/terms from ordinary prose. |
| Community governance baseline | closed | mechanical existence/bilingual checks + policy | CONTRIBUTING/SECURITY are complemented by CODE_OF_CONDUCT and GitHub issue/PR templates without invented contact coordinates or SLAs. |
| Wordstat “nine skills” vs capability rows | closed | documentation clarification | ROADMAP says nine **initial workflow skills**; capability rows are not interpreted as skill count. |
| YandexGPT/SpeechKit naming ambiguity | previously closed | documentation | Root README explicitly states that the marketplace targets Yandex services and is not a plugin set for YandexGPT. |
| Backend-independent safety requirement lacks an eval case | closed as explicit backlog | policy + future semantic evidence | The model-eval backlog requires a paired MCP/app vs bundled-helper/file case preserving the same exact-preview + later-turn approval gate. |

## Evidence boundary

**Mechanical evidence** in this remediation means repository tests, validator, and CI that verify specific static/structural contracts. **Semantic evidence** means review of documentation meaning, ownership, and safety semantics; green CI is not semantic proof.

Before merge, this artifact intentionally contains no future final identifiers. Final exact-head and publication facts must be verified in PR #58 and immutable release `1.0.8` after they actually exist.
