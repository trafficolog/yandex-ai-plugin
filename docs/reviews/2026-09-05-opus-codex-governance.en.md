# 2026-09-05 — Opus/Codex governance review

[Русский](2026-09-05-opus-codex-governance.md) · [**English**](2026-09-05-opus-codex-governance.en.md)

## Scope and roles

This artifact combines two independent review lines that materially shaped current repository governance:

1. **Opus 5 audit** — external AI audit of repository contracts, validator coverage, release/documentation consistency, and traceability. It is advisory semantic review, not merge permission.
2. **Codex review of PR #56** — automated independent review of the declarative release publisher. Findings were closed through separate RED→GREEN cycles.

**CI** in this artifact is mechanical evidence. The **human maintainer** separately owns merge/release authorization. Neither AI review nor green CI silently replaces human authorization.

## Opus 5 findings and disposition

The audit identified a gap between declared repository guarantees and mechanical enforcement. Findings included bypassable cross-service transport detection, incomplete secret scanning, weak `SKILL.md` validation, drift-prone version/release-marker surfaces, formal bilingual validation, and limited contract traceability.

Maintenance releases completed before repository `1.0.6` addressed the runtime/validator parts of that list: cross-service transport ownership, secret patterns, skill contracts, version/documentation consistency, bilingual checks, and one repository release-governance line. PR C does not reopen those areas and does not modify plugin runtime.

The remaining governance gap addressed by PR C / repository `1.0.7` is narrower:

- `CONTRACT_MATRIX` v1 named a regression-test **file**, not an exact test function/method;
- production requirements were compressed prose without stable requirement IDs or explicit enforcement ownership;
- review evidence had no repository-owned dated artifact;
- the repository had no `SECURITY` policy;
- `docs/superpowers/` needed an explicit boundary as historical implementation context rather than canonical production requirements.

PR C adds exact selectors plus Python AST validation for function-level traceability. This strengthens metadata integrity but is still not presented as semantic proof of test assertions.

## Codex review of PR #56

The first Codex review was performed on reviewed head:

`130050f11b2612a01ca6909215dbf30952a89d45`

It reported three actionable findings:

- **P1:** TSV record injection through tab/newline characters in release-manifest scalars;
- **P1:** rollback could attempt destructive cleanup when the immutability probe had not proven mutable state;
- **P2:** generic release-manifest validation did not derive README/CHANGELOG release surfaces from `repository.version`.

All three findings received regression tests and RED→GREEN closure. Candidate head after fixes:

`23a14d9b9e51825b96286bf6f9a8d4244d035ebe`

Exact-head CI:

- `33953946792` — 10/10 jobs success.

PR #56 was then squash-merged. Main/merge SHA:

`88d2f45e63308a476cbe456402bf17dc847436cb`

Post-merge mechanical evidence:

- CI `33954164035` — 10/10 jobs success;
- generic publisher `33954198278` — success;
- Repository `1.0.6` was published immutable at the exact merge SHA.

## Reviewer limitation

After the three Codex findings were addressed, an exact-head re-review was requested for `23a14d9b9e51825b96286bf6f9a8d4244d035ebe`. Codex reported that the **code-review quota** limit had been reached.

Therefore the final head of PR #56 **does not have a claimed clean Codex re-review**. The limitation was documented in the PR; the reviewed-head → candidate-head delta was separately checked and contained only the fixes/regressions for the reported P1/P2 findings. This is a documented reviewer/tool limitation, not a positive review result.

## What this artifact proves — and what it does not

It proves traceability of review history: what was reviewed, which findings were recorded, which exact SHAs and CI runs are associated with closure, and where a reviewer was unavailable.

It does not prove:

- that an AI reviewer exhaustively covered the repository;
- that CI is semantic review;
- that current external Yandex API behavior is automatically verified;
- that the presence of an exact test selector guarantees assertion semantics.

Canonical requirements remain in `PLUGIN_STANDARD`, `RELEASE_POLICY`, executable validators/tests, plugin contracts, and machine-owned registries/matrices.