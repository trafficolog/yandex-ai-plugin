# Yandex AI Plugin Marketplace — Architecture Design

**Date:** 2026-09-01  
**Repository:** `trafficolog/yandex-ai-plugin`  
**Status:** Approved architecture; implementation pending

## 1. Purpose

Turn the repository from a single Yandex Direct plugin into a unified Yandex AI marketplace monorepo that keeps all Yandex integrations in one place while preserving independent installation, versioning, testing, and evolution of each service plugin.

The repository is a **marketplace/composition layer**, not one giant Yandex skill.

## 2. Core architectural decision

Use one monorepo with multiple independent plugins:

```text
trafficolog/yandex-ai-plugin/
├── .agents/plugins/marketplace.json
├── plugins/
│   ├── yandex-direct/
│   ├── yandex-metrika/
│   ├── yandex-webmaster/
│   ├── yandex-wordstat/
│   ├── yandex-search/
│   ├── yandex-appmetrica/
│   ├── yandex-maps/
│   ├── yandex-tracker/
│   ├── yandex-360/
│   ├── yandexgpt/
│   └── yandex-speechkit/
├── workflows/
├── packages/
├── docs/
├── scripts/
└── .github/workflows/
```

Each directory under `plugins/` is an independently installable plugin with its own manifest, version, skills, references, tests, and optional execution adapters.

The root repository owns marketplace metadata, shared standards, CI, shared packages, cross-service workflows, and documentation.

## 3. Plugin boundary

A plugin is the unit of installation and versioning.

A skill is the unit of agent knowledge/workflow.

Example:

```text
plugins/yandex-direct/
├── .codex-plugin/plugin.json
├── .claude-plugin/plugin.json
├── skills/
│   ├── yandex-direct/
│   ├── yandex-direct-create/
│   ├── yandex-direct-audit/
│   ├── yandex-direct-reporting/
│   ├── yandex-direct-optimize/
│   ├── yandex-direct-keywords/
│   ├── yandex-direct-budget/
│   └── yandex-direct-api/
├── references/
├── scripts/
├── tests/
├── evals/
├── CHANGELOG.md
└── README.md
```

No service plugin should grow into a single monolithic `SKILL.md` when several distinct tasks can be discovered independently.

## 4. Initial service tiers

### Tier 1 — Marketing and SEO

Build first because the services are tightly connected and already have useful upstream work to study:

1. `yandex-direct` — existing reference implementation.
2. `yandex-metrika` — reporting, conversions, ecommerce, attribution, logs, goals.
3. `yandex-webmaster` — indexing, diagnostics, search queries, sitemaps, recrawl, links.
4. `yandex-wordstat` — demand analysis, frequency, dynamics, regions, semantics.
5. `yandex-search` — Yandex SERP/Search API workflows.

### Tier 2 — Operations

- `yandex-tracker`
- `yandex-360`
- `yandex-maps`

### Tier 3 — AI and mobile

- `yandex-appmetrica`
- `yandexgpt`
- `yandex-speechkit`

## 5. Cross-service workflows

Cross-service workflows live outside individual service plugins because they orchestrate multiple products.

Planned examples:

```text
workflows/
├── yandex-marketing/
├── yandex-seo/
├── yandex-ecommerce/
└── yandex-mobile-growth/
```

Examples:

- `yandex-seo`: Wordstat → Search → Webmaster → Metrika.
- `yandex-marketing`: Direct → Metrika → Wordstat.
- `yandex-ecommerce`: Direct + Metrika ecommerce + product/feed data.

A workflow must not duplicate the low-level API reference of its component plugins.

## 6. Execution architecture

Separate reasoning/workflow from execution.

```text
User
  ↓
Plugin skills
  ↓
Execution adapter
  ├── MCP/app when available
  ├── bundled API helper when available
  └── export/file fallback
  ↓
Yandex API
```

Skills should describe required **capabilities**, not hard-code one runtime-specific MCP tool name.

Preferred execution order:

1. Use a compatible connected Yandex app/MCP when available.
2. Otherwise use bundled local API helpers if the runtime can execute them.
3. Otherwise work from user-provided exports/files and provide a reproducible change plan.

This keeps plugins usable across ChatGPT/Codex, Claude Code, Cursor, and other Agent Skills-compatible environments.

## 7. Relationship to upstream projects

### `mkultraaaa/claude-yandex-skills`

Use as a workflow/UX donor for:

- Metrika;
- Webmaster;
- Wordstat;
- Search API;
- cache-first patterns;
- context-window hygiene;
- compact CLI output;
- split `SKILL.md` / `references` / `scripts` structure.

Do not copy assumptions blindly. Re-verify API versions, limits, fields, auth, and policies against current official Yandex documentation before implementation.

### `theYahia/YaAll`

Use as:

- capability/coverage reference;
- optional MCP execution backend;
- donor for AppMetrica, Tracker, 360, Maps, YandexGPT, SpeechKit, Webmaster and Metrika tooling;
- source of tested patterns such as string-safe large IDs, sandbox support, and broad tool coverage.

Do not treat YaAll as the canonical API specification. Official Yandex API documentation remains the source of truth. Each imported idea must be checked for API-version drift before use.

## 8. Shared packages

Shared code should exist only where duplication is proven across two or more plugins.

Candidate packages:

```text
packages/
├── yandex-auth/
├── yandex-http/
├── cache/
├── safety/
├── schemas/
└── cli/
```

Do not prematurely centralize service-specific API behavior.

## 9. Mandatory plugin standard

Every production plugin MUST have:

1. Router skill.
2. Task-specific skills where responsibilities differ materially.
3. Current API reference with a verification date.
4. Safety/write policy.
5. Source and attribution document.
6. Tests for bundled executable code.
7. Eval scenarios for agent behavior.
8. Read-first behavior.
9. Preview/dry-run before consequential writes when technically possible.
10. Explicit user approval for destructive, financial, publishing, or irreversible actions.
11. Secrets only via environment/app credentials; never in skill text or committed files.
12. Documented API version and authentication model.
13. Capability matrix: read/write, MCP/API/file fallback.
14. Graceful fallback when live access is unavailable.
15. Independent changelog and semantic version.
16. No universal business-performance thresholds presented as facts without evidence/source.
17. No runtime-specific absolute filesystem paths in skills.
18. Compact outputs by default; full datasets saved as artifacts/files when possible.

The implementation will formalize these rules in `docs/PLUGIN_STANDARD.md`.

## 10. Safety model

All plugins use one behavioral contract:

```text
read → analyze → preview → explicit approval → write → verify
```

Higher-risk actions require stronger confirmation:

- advertising activation or budget changes;
- deleting analytics counters/goals;
- deleting Webmaster resources;
- changing Tracker permissions;
- sending mail/push notifications;
- publishing or changing externally visible resources.

Creation of a draft is distinct from activation/publication.

## 11. Versioning

Plugins version independently inside the monorepo.

Example:

```text
yandex-direct      1.1.0
yandex-metrika     1.0.0
yandex-webmaster   0.9.0
```

Release tags should be service-scoped:

```text
yandex-direct-v1.1.0
yandex-metrika-v1.0.0
```

Root marketplace metadata references the current plugin versions but does not force a shared monorepo version.

## 12. CI strategy

Root CI should be path-aware.

For every changed plugin:

- validate manifests;
- validate Agent Skills frontmatter;
- run plugin unit tests;
- run static syntax/type checks;
- run offline eval fixtures where available;
- check forbidden committed secrets;
- verify referenced files exist.

Additionally, scheduled freshness jobs should compare critical Yandex API documentation assumptions and open an issue when a verified fact may have changed.

## 13. Migration of the existing Direct plugin

Current root Direct implementation will move without functional redesign to:

```text
plugins/yandex-direct/
```

During migration:

- preserve the existing Direct plugin version `1.0.0`;
- preserve tests and behavior;
- update internal relative paths;
- update root marketplace to reference `plugins/yandex-direct`;
- move Direct-specific `.env.example`, scripts, references, tests, changelog, manifests and notices under the plugin;
- keep repository-level `LICENSE`, root `README.md`, marketplace metadata and architecture docs at root;
- add a root roadmap for future services.

Functional Direct improvements occur only after the structural migration passes all existing tests.

## 14. Implementation order

### Phase 1 — Marketplace foundation

- migrate Direct into `plugins/yandex-direct/`;
- create root marketplace metadata;
- add `docs/PLUGIN_STANDARD.md`;
- add path-aware CI and manifest validation;
- add roadmap/service matrix;
- verify Direct still passes all existing tests.

### Phase 2 — Metrika

Build Metrika to the Direct standard using current Yandex docs, `claude-yandex-skills` as workflow donor, and YaAll as capability/MCP reference.

### Phase 3 — Webmaster

Same process.

### Phase 4 — Wordstat + Search

Implement separately because demand statistics and web SERP/search are different domains despite overlapping Yandex Search infrastructure.

### Phase 5 — Cross-service workflows

Add `yandex-marketing` and `yandex-seo` only after their component plugins are stable.

### Phase 6 — Operations / AI / mobile

Tracker, 360, Maps, AppMetrica, YandexGPT, SpeechKit.

## 15. Success criteria

The architecture is successful when:

- one GitHub marketplace exposes multiple Yandex plugins;
- users can install only the service plugins they need;
- Direct remains independently usable after migration;
- all plugins follow the same safety, metadata, testing, and documentation conventions;
- live execution is backend-agnostic;
- API-version drift is detectable by tests/freshness checks;
- cross-service workflows reuse service plugins rather than reimplementing them.
