# Independent review artifacts

[Русский](README.md) · [**English**](README.en.md)

This directory stores auditable review artifacts for repository/plugin releases. They do not replace CI, human authorization, or canonical production contracts.

## Artifact convention

Each dated review should record, when available:

- date and scope;
- reviewer type: human / external AI / automated reviewer;
- reviewed commit, PR, or release;
- findings without silently rewriting them after the fact;
- disposition of each finding: closed / addressed in current PR / deferred / out of scope;
- exact evidence such as commit SHA, CI run ID, review thread, or immutable release;
- reviewer/tool limitations, including quota limits that affected coverage;
- explicit role separation: AI review is semantic/advisory input, CI is mechanical evidence, and the human maintainer owns merge/release authorization.

Reviewer absence or a quota/tool limitation **is not a clean review**.

## Artifacts

- [`2026-09-05 — Fable 5.1 Round 2 closure`](2026-09-05-fable-round2-closure.en.md) — cross-check of the earlier normative audit after out-of-order remediation and disposition of remaining findings in repository `1.0.8`.
- [`2026-09-05 — Opus/Codex governance review`](2026-09-05-opus-codex-governance.en.md) — governance/validator audit gaps plus follow-up review of release-infrastructure PR #56.

Canonical production requirements live in [`PLUGIN_STANDARD.en.md`](../PLUGIN_STANDARD.en.md), [`RELEASE_POLICY.en.md`](../RELEASE_POLICY.en.md), executable validators/tests, plugin `SKILL.md`/references, and machine-owned registries/matrices. Files under `docs/superpowers/` are historical implementation context.