# Yandex AI Plugin Standard

[Русский](PLUGIN_STANDARD.md) · [**English**](PLUGIN_STANDARD.en.md)

This document defines the repository-wide contract for production plugins under `plugins/`.

## 1. Required structure

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

A plugin is the installation/versioning boundary. A `SKILL.md` is a discoverable workflow/knowledge unit.

## 2. Production requirements

Every plugin MUST provide a router and focused task skills; keep volatile API facts in references; test bundled executable code; include offline eval expectations; default to read-first; preview consequential writes; require explicit approval; keep secrets out of content; expose a capability matrix; use independent SemVer; avoid universal business thresholds and runtime-specific home paths; preserve source-specific semantics; and keep cross-service plugins transport-free.

The documentation contract additionally requires RU-primary `README.md`/`CHANGELOG.md` and English `README.en.md`/`CHANGELOG.en.md` with reciprocal language links. RU/EN changelog release markers must match. Key repository docs follow the same `.en.md` convention. A documentation-only repository release does not bump plugin SemVer.

## 3. Safety contract

```text
read → analyze → preview → explicit approval → write → verify
```

A recommendation is not permission. Draft creation is distinct from activation/publication.

## 4. Execution abstraction

Preferred order: compatible connected MCP/app → bundled helper → user-provided export/file. Reasoning and safety semantics remain backend-independent.

Cross-service plugins may prepare delegated previews but own no service transport or credentials. In the `.agents` marketplace they use `policy.authentication: ON_USE` because the marketplace schema requires an authentication policy from the supported `ON_INSTALL` / `ON_USE` values. For transport-free orchestration this is **schema-compatible deferred-auth metadata**, not a claim that the plugin owns credentials: repository validation separately rejects `.env.example` and service transport inside `yandex-seo` / `yandex-marketing`.

## 5. Skill conventions

```yaml
---
name: yandex-service-task
description: Use when ...
---
```

Descriptions start with `Use when`; references contain long/volatile API facts.

## 6. API freshness

Official Yandex documentation is canonical. Platform facts in freshness-controlled references carry a verification marker. Ordinary PR/push validation makes the 90-day age rule a hard error only for a changed freshness-controlled reference; malformed/missing/future verification markers remain errors. A separate scheduled strict check evaluates the complete controlled set and creates or updates an issue when references become stale. This preserves re-verification pressure without making unrelated PRs fail because time passed.

## 7. Capability matrix

Each plugin README contains at least:

| Capability | Read | Write | MCP/App | Bundled API | File fallback |
|---|---:|---:|---:|---:|---:|
| Example capability | yes | approval | optional | yes | yes |

Consequential writes use `approval`; cross-service writes are delegated previews/approval in the owning plugin.

## 8. Versioning

Plugins version independently with SemVer. Structural/documentation repository changes do not automatically change plugin versions. Service tags may use `yandex-direct-v1.1.0`; repository milestones may use `opus-*` or `docs-*`.

## 9. Tests and evals

Executable helpers have unit tests. `evals/scenarios.json` includes machine-verifiable `expect` fields: `must_route_to`, `must_refuse`, `must_mention`, `must_not_claim`; allowed write values are `false`, `preview-first`, and `approval-required`.

Important: the current repository validator checks **eval fixture structure and consistency**, but it does not execute scenarios against a model. The `expect` contract makes scenarios formal and suitable for a future eval runner; green CI does not mean a model has automatically passed those scenarios.

## 10. Contract matrix: traceability, not semantic proof

`docs/CONTRACT_MATRIX.json` is a traceability index for high-risk contracts. It links `SKILL.md` → helper → regression-test file → reference/freshness metadata.

Validation checks matrix structure, unique IDs, supported statuses, referenced path existence, presence of a declared regression-test file for `implemented` contracts, and selected reference freshness metadata. It **does not inspect the semantic content of the test code** and therefore cannot prove that a listed test assertion actually enforces the stated invariant. A green matrix gate proves traceability metadata is consistent; it does not replace semantic test review or external API verification.

## 11. Shared code rule

Do not promote code into `packages/` merely because it looks similar. Shared packages require repeated responsibility and a stable interface.

## 12. CI contract

Validation covers both marketplace formats, manifest families, SemVer consistency, capability matrices, evals, secrets/paths, the cross-service no-transport boundary, bilingual documentation pairs, and changelog release-marker parity. Path-aware CI models producer → consumer dependencies. Freshness age is scoped to changed controlled references on PR/push; the scheduled workflow performs the strict whole-repository freshness check.
