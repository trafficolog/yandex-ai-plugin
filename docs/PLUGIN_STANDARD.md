# Yandex AI Plugin Standard

This document defines the repository-wide contract for every production plugin under `plugins/`.

## 1. Required structure

Each production service plugin must be independently understandable, testable, and versioned.

```text
plugins/yandex-<service>/
├── .codex-plugin/plugin.json
├── .claude-plugin/plugin.json
├── skills/
├── references/
├── scripts/
├── tests/
├── evals/
├── CHANGELOG.md
├── README.md
└── THIRD_PARTY_NOTICES.md
```

The plugin directory is the installation/versioning boundary. A `SKILL.md` is a discoverable unit of agent knowledge or workflow, not the whole product.

## 2. Mandatory requirements

Every production plugin MUST:

1. Provide a router skill for general requests to that Yandex service.
2. Split materially different tasks into task-specific skills instead of one monolithic `SKILL.md`.
3. Include a current API reference with a visible verification date.
4. Include a safety/write policy appropriate to the service.
5. Document sources, upstream projects, attribution, and licenses.
6. Test all bundled executable code.
7. Include offline agent-behavior eval scenarios with machine-verifiable expectations.
8. Default to read-first behavior.
9. Preview/dry-run consequential writes when technically possible.
10. Require explicit user approval for destructive, financial, publishing, permission-changing, or otherwise irreversible actions.
11. Keep secrets only in environment/app credentials; never commit them or include them in skill/reference/example text.
12. Document API version(s), endpoints, authentication model, and known compatibility constraints.
13. Include a capability matrix for read/write and supported execution backends.
14. Fall back gracefully when live access is unavailable.
15. Maintain an independent changelog and semantic version.
16. Avoid presenting universal business-performance thresholds as facts without evidence and context.
17. Avoid runtime-specific absolute filesystem paths such as `~/.claude/`, `~/.codex/`, and `~/.openclaw/` anywhere in the plugin contract.
18. Keep agent output compact by default and save large datasets to files/artifacts when the runtime allows it.
19. Keep `.agents`, Claude marketplace, Codex manifest, Claude plugin manifest, plugin changelog and release-facing version documentation consistent.
20. Keep cross-service orchestration transport-free: service API clients and credentials remain in the owning service plugins.

## 3. Safety contract

The common behavior for consequential operations is:

```text
read → analyze → preview → explicit approval → write → verify
```

Draft creation is distinct from activation/publication. A user asking for analysis, optimization ideas, or a payload does not implicitly authorize a live change.

### Risk classes

- **Read:** reports, lists, diagnostics, metadata. No extra approval beyond the user's request.
- **Draft/preview:** payloads, campaign drafts, proposed goals, proposed sitemap changes. No live publication.
- **Consequential write:** budget changes, campaign activation, deletes, permissions, outbound communication, publishing. Explicit approval required immediately before execution.
- **Bulk consequential write:** apply the same rules with tighter preview scope, count of affected objects, and rollback/verification notes.

## 4. Execution abstraction

Skills describe capabilities rather than hard-coding one tool implementation.

Preferred runtime fallback order:

1. compatible connected MCP/app;
2. bundled API helper when local execution is available;
3. user-provided export/file with a reproducible change plan.

A plugin may support more than one backend, but its reasoning and safety rules must remain backend-independent.

Cross-service plugins may prepare delegated previews, but they do not own service transport. Their `write` eval posture should therefore remain `false`; delegated preview expectations belong in the `expect` block.

## 5. Skill conventions

Every `SKILL.md` must have YAML frontmatter with:

```yaml
---
name: yandex-service-task
description: Use when ...
---
```

Folded/block descriptions are allowed when they resolve to text beginning with `Use when`. References hold volatile API facts and long tables. Skills should not embed secrets, absolute runtime paths, or stale copied API documentation.

## 6. API freshness

A reference containing platform facts must state when it was last verified. Before adding or changing live-write behavior, verify mutable facts against official Yandex documentation.

Official documentation is canonical. Third-party repositories are donors for workflow ideas, coverage, tests, and adapters, not the API source of truth.

## 7. Capability matrix

Each plugin README must state at minimum:

| Capability | Read | Write | MCP/App | Bundled API | File fallback |
|---|---:|---:|---:|---:|---:|
| Example capability | yes | approval | optional | yes | yes |

Use `approval`, not a bare `yes`, for consequential writes. Cross-service plugins should label writes as delegated previews/approval in the owning plugin rather than implying local mutation capability.

## 8. Versioning

Plugins version independently with SemVer. Repository-wide releases are not required.

Recommended tags:

```text
yandex-direct-v1.1.0
yandex-metrika-v1.0.0
```

A structural monorepo change does not automatically increment every plugin version. Version bumps are based on that plugin's user-facing contract. When several plugins are changed by one remediation release, synchronized versions are acceptable but remain independent plugin SemVer declarations.

## 9. Tests and evals

A plugin with executable helpers must have unit tests. Evals are offline fixtures that encode routing and critical safety expectations without live credentials. A scenario that only contains prompt/skill metadata is not considered a verifiable safety fixture.

Required `evals/scenarios.json` shape:

```json
{
  "version": 1,
  "scenarios": [
    {
      "prompt": "...",
      "skill": "yandex-service-task",
      "write": false,
      "expect": {
        "must_route_to": "yandex-service-task",
        "must_refuse": false,
        "must_mention": ["quality limitation"],
        "must_not_claim": ["unsupported causal claim"]
      }
    }
  ]
}
```

Contract:

- `must_route_to` is required and must equal the scenario `skill`;
- `must_refuse` is a boolean describing whether the requested operation/inference itself must be declined;
- `must_mention` is a list of required safety/limitation concepts for a future eval runner;
- `must_not_claim` is a list of forbidden claims;
- `write` describes the owning plugin's execution posture, not whether a prompt merely asks for a delegated preview.

Allowed `write` values are `false`, `preview-first`, and `approval-required`.

## 10. Shared code rule

Do not create a shared package merely because code looks similar. Promote code to `packages/` only after the same responsibility is implemented by at least two service plugins **and a stable shared interface is evident**. Service-specific auth/transport behavior or intentionally different URL identity policies are reasons to keep helpers separate.

## 11. CI contract

Repository validation must check:

- both root marketplace manifests and both plugin manifest families;
- local source paths, skill directories and skill frontmatter;
- SemVer consistency across discovery manifests, plugin changelog and release-facing version documentation;
- capability matrices;
- eval syntax plus the expectation contract from §9;
- forbidden runtime-specific paths across plugin text files;
- credential-like committed literals;
- the invariant that cross-service plugin scripts contain no service transport/client layer.

Path-aware CI must also model producer → consumer dependencies. Changes to a service plugin must trigger affected cross-service regressions, not only that service's own tests. Changes to the CI workflow, repository validator, plugin standard, shared root tests and approved specs are treated as shared changes that exercise the complete plugin matrix.
