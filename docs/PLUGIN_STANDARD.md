# Yandex AI Plugin Standard

This document defines the repository-wide contract for every production plugin under `plugins/`.

## 1. Required structure

Each production service plugin must be independently understandable, testable, and versioned.

```text
plugins/yandex-<service>/
├── .codex-plugin/plugin.json
├── .claude-plugin/plugin.json        # when Claude portability is provided
├── skills/
├── references/
├── scripts/                          # optional execution fallback
├── tests/
├── evals/
├── CHANGELOG.md
├── README.md
└── THIRD_PARTY_NOTICES.md            # when upstream work is used
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
7. Include offline agent-behavior eval scenarios.
8. Default to read-first behavior.
9. Preview/dry-run consequential writes when technically possible.
10. Require explicit user approval for destructive, financial, publishing, permission-changing, or otherwise irreversible actions.
11. Keep secrets only in environment/app credentials; never commit them or include them in skill text.
12. Document API version(s), endpoints, authentication model, and known compatibility constraints.
13. Include a capability matrix for read/write and supported execution backends.
14. Fall back gracefully when live access is unavailable.
15. Maintain an independent changelog and semantic version.
16. Avoid presenting universal business-performance thresholds as facts without evidence and context.
17. Avoid runtime-specific absolute filesystem paths such as `~/.claude/` and `~/.openclaw/` in skills.
18. Keep agent output compact by default and save large datasets to files/artifacts when the runtime allows it.

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

## 5. Skill conventions

Every `SKILL.md` must have YAML frontmatter with:

```yaml
---
name: yandex-service-task
description: Use when ...
---
```

Descriptions state triggering conditions. References hold volatile API facts and long tables. Skills should not embed secrets, absolute runtime paths, or stale copied API documentation.

## 6. API freshness

A reference containing platform facts must state when it was last verified. Before adding or changing live-write behavior, verify mutable facts against official Yandex documentation.

Official documentation is canonical. Third-party repositories are donors for workflow ideas, coverage, tests, and adapters, not the API source of truth.

## 7. Capability matrix

Each plugin README should state at minimum:

| Capability | Read | Write | MCP/App | Bundled API | File fallback |
|---|---:|---:|---:|---:|---:|
| Example capability | yes | approval | optional | yes | yes |

Use `approval`, not a bare `yes`, for consequential writes.

## 8. Versioning

Plugins version independently with SemVer. Repository-wide releases are not required.

Recommended tags:

```text
yandex-direct-v1.1.0
yandex-metrika-v1.0.0
```

A structural monorepo change does not automatically increment every plugin version. Version bumps are based on that plugin's user-facing contract.

## 9. Tests and evals

A plugin with executable helpers must have unit tests. Evals are offline fixtures that verify routing and critical safety expectations without live credentials.

Recommended `evals/scenarios.json` shape:

```json
{
  "version": 1,
  "scenarios": [
    {"prompt": "...", "skill": "yandex-service-task", "write": false}
  ]
}
```

Allowed `write` values are `false`, `preview-first`, and `approval-required`.

## 10. Shared code rule

Do not create a shared package for code used by only one plugin. Promote code to `packages/` only after the same responsibility is implemented by at least two service plugins and a stable interface is evident.

## 11. CI contract

Repository validation must check marketplace paths, plugin manifests, skill frontmatter, eval syntax, referenced directories, and forbidden absolute runtime paths. Each changed plugin runs its own tests and static checks.
