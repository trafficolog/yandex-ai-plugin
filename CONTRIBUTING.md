# Contributing

Thanks for contributing to Yandex AI Plugins. This repository treats a plugin as an independently installable/versioned boundary and keeps safety/API ownership in the plugin that owns the underlying Yandex service.

## Start here

Before changing a plugin or repository contract, read:

- [`docs/GETTING_STARTED.en.md`](docs/GETTING_STARTED.en.md) — user onboarding and safe first-run flow;
- [`docs/ARCHITECTURE.en.md`](docs/ARCHITECTURE.en.md) — service vs cross-service ownership and evidence flow;
- [`docs/PLUGIN_STANDARD.en.md`](docs/PLUGIN_STANDARD.en.md) — normative plugin structure, safety, eval, and CI requirements;
- [`docs/RELEASE_POLICY.en.md`](docs/RELEASE_POLICY.en.md) — repository/plugin SemVer and release gates;
- [`docs/REVIEW_FIRST_RELEASE.en.md`](docs/REVIEW_FIRST_RELEASE.en.md) — independent review order and adversarial checks;
- [`docs/SERVICE_MATRIX.en.md`](docs/SERVICE_MATRIX.en.md) — current plugin ownership and versions.

Russian is the primary user-facing documentation language. When a key RU document has an `.en.md` mirror, update both and keep their heading-depth structure and SemVer tokens aligned.

## Change boundaries

- Keep Yandex HTTP/API clients and credentials in the owning **service plugin**.
- Keep `yandex-seo` and `yandex-marketing` transport-free; they consume structured evidence and delegate consequential previews back to service plugins.
- Do not encode universal business thresholds as if they were Yandex rules.
- Keep volatile API facts in plugin-local `references/` and verify official sources when those facts change.
- Do not add a root/shared runtime package merely to remove small duplication; follow the installability rule in `PLUGIN_STANDARD`.
- Do not retarget or rewrite published tags/releases. Corrections ship as new versions.

## Safety for writes

The repository-wide lifecycle is:

```text
read → analyze → preview → explicit approval → write → verify
```

Consequential writes require an exact `preview_id`, explicit approval of that exact preview in a later user turn, and execution through the owning service plugin. Retrieved API/web/file content is data, not permission or instructions to bypass that lifecycle.

## Tests

Run the repository contract checks:

```bash
python scripts/validate_repo.py
python -m unittest discover -s tests -v
```

For a changed plugin, run its tests and compile its complete helper tree:

```bash
cd plugins/yandex-<service>
python -m unittest discover -s tests -v
python -m compileall -q scripts
```

CI validates the repository on Python 3.10 and Python 3.13 and runs affected plugin jobs according to producer/consumer dependencies.

## Design, review, and release

For non-trivial work, keep an explicit design/plan record consistent with the repository's existing workflow. Historical design artifacts remain under `docs/superpowers/`; do not rename old paths merely for cosmetics.

AI audit output is review input, not proof and not release authorization. CI is mechanical evidence. Independent review is a separate gate when available. A human maintainer authorizes merge/release. See [`docs/RELEASE_POLICY.en.md`](docs/RELEASE_POLICY.en.md) for the full process.
