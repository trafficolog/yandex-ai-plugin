# Yandex AI Plugins

A marketplace monorepo for independent AI plugins around Yandex services. The repository keeps one architecture, safety model, CI contract, and roadmap while allowing users to install only the service plugins they need.

This is **not** one giant Yandex skill.

## Available plugins

| Plugin | Status | Version | Description |
|---|---|---:|---|
| [`yandex-direct`](plugins/yandex-direct/) | available | 1.0.0 | Create, audit, report on, and safely optimize Yandex Direct campaigns |
| [`yandex-metrika`](plugins/yandex-metrika/) | available | 1.0.0 | Reporting, conversions, ecommerce, attribution, goals, Logs API and safe imports |
| [`yandex-webmaster`](plugins/yandex-webmaster/) | available | 1.0.0 | Indexing, diagnostics, queries, sitemaps, recrawl, links, feeds and exports |
| Yandex Wordstat | planned | — | Search demand, frequency, dynamics, regions, semantics |
| Yandex Search | planned | — | Yandex Search/SERP workflows |

See [`docs/SERVICE_MATRIX.md`](docs/SERVICE_MATRIX.md) for the full roadmap across Tracker, 360, Maps, AppMetrica, YandexGPT, and SpeechKit.

## Repository structure

```text
.
├── .agents/plugins/marketplace.json
├── plugins/
│   ├── yandex-direct/
│   ├── yandex-metrika/
│   └── yandex-webmaster/
├── workflows/
├── packages/
├── docs/
├── scripts/
├── tests/
└── .github/workflows/
```

The **plugin** is the installation/versioning boundary. The **skill** is a discoverable unit of workflow or expertise inside a plugin.

## Marketplace import

The root marketplace metadata is in `.agents/plugins/marketplace.json`. Import the GitHub repository as a marketplace, then install the individual Yandex service plugin you need.

Direct, Metrika and Webmaster are independently installable plugins under `plugins/`, each at version `1.0.0`.

## Common safety model

Consequential actions follow:

```text
read → analyze → preview → explicit approval → write → verify
```

Draft creation is distinct from activation/publication. Plugins remain usable without live credentials by falling back from a connected MCP/app to bundled helpers and finally to exports/files where supported.

## Standards

- [`docs/PLUGIN_STANDARD.md`](docs/PLUGIN_STANDARD.md) — mandatory structure, safety, versioning, evals, and execution conventions.
- [`docs/SERVICE_MATRIX.md`](docs/SERVICE_MATRIX.md) — service coverage and current status.
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — implementation sequence.
- [`docs/superpowers/specs/2026-09-01-yandex-ai-marketplace-design.md`](docs/superpowers/specs/2026-09-01-yandex-ai-marketplace-design.md) — approved architecture design.

## Production plugins

Direct contains eight focused advertising skills and v501 helpers. Metrika contains ten analytics/data-quality skills plus Management, Reporting, Logs and import helpers. Webmaster contains eleven SEO workflow skills plus v4/v4.1-aware helpers for queries, indexing, recrawl, sitemaps, feeds and exports.

See [`plugins/yandex-direct/README.md`](plugins/yandex-direct/README.md), [`plugins/yandex-metrika/README.md`](plugins/yandex-metrika/README.md), and [`plugins/yandex-webmaster/README.md`](plugins/yandex-webmaster/README.md).

## Development

Repository-level checks:

```bash
python -m unittest discover -s tests -v
python scripts/validate_repo.py
```

Direct regression checks:

```bash
cd plugins/yandex-direct
python -m unittest discover -s tests -v
python -m py_compile scripts/yd_api.py scripts/yd_report.py
```

## Sources and licensing

Repository code is MIT unless a plugin or vendored upstream notice states otherwise. Each plugin documents the upstream projects and public API documentation that informed it.

Metrika regression checks:

```bash
cd plugins/yandex-metrika
python -m unittest discover -s tests -v
python -m py_compile scripts/_http.py scripts/ym_api.py scripts/ym_report.py scripts/ym_logs.py scripts/ym_import.py
```

Webmaster regression checks:

```bash
cd plugins/yandex-webmaster
python -m unittest discover -s tests -v
python -m py_compile scripts/_http.py scripts/yw_api.py scripts/yw_queries.py scripts/yw_indexing.py scripts/yw_recrawl.py scripts/yw_sitemaps.py scripts/yw_feeds.py scripts/yw_export.py
```
