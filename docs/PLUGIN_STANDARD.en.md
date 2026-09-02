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

Preferred order: compatible connected MCP/app → bundled helper → user-provided export/file. Reasoning and safety semantics remain backend-independent. Cross-service plugins may prepare delegated previews but own no service transport or credentials.

## 5. Skill conventions

```yaml
---
name: yandex-service-task
description: Use when ...
---
```

Descriptions start with `Use when`; references contain long/volatile API facts.

## 6. API freshness

Official Yandex documentation is canonical. Platform facts in freshness-controlled references carry a verification marker and pass the deterministic 90-day gate.

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

## 10. Shared code rule

Do not promote code into `packages/` merely because it looks similar. Shared packages require repeated responsibility and a stable interface.

## 11. CI contract

Validation covers both marketplace formats, manifest families, SemVer consistency, capability matrices, evals, secrets/paths, the cross-service no-transport boundary, bilingual documentation pairs, and changelog release-marker parity. Path-aware CI models producer → consumer dependencies.