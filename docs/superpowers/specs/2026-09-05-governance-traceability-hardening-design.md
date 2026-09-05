# Governance & Traceability Hardening — design

Date: 2026-09-05
Target repository release: `1.0.7`
Base: `main` at `88d2f45e63308a476cbe456402bf17dc847436cb`
Scope class: architectural governance/metadata change

## 1. Goal

Close the remaining governance and traceability gaps identified by the independent AI audit without reopening already-hardened plugin runtime, write-safety, transport, or release-engine behavior.

The release must make high-risk contract traceability more precise, preserve auditable review evidence in-repository, establish an explicit security-reporting policy, and stop treating implementation specs under `docs/superpowers/` as normative production requirements.

This is a repository-only patch release. Production plugin SemVer remains unchanged.

## 2. Non-goals

The PR MUST NOT:

- change plugin runtime helpers, API behavior, transport ownership, credentials, or write execution semantics;
- bump any plugin version or publish any plugin tag;
- add a model eval runner or claim semantic eval execution;
- add new service plugins;
- mutate, retarget, delete, or recreate historical immutable releases/tags;
- redesign the declarative publisher shipped in repository `1.0.6` except for advancing its release declaration to `1.0.7`;
- turn `docs/superpowers/` into a second normative documentation hierarchy.

## 3. CONTRACT_MATRIX schema v2

### 3.1. Motivation

`docs/CONTRACT_MATRIX.json` v1 links high-risk contracts to regression-test files. File existence is useful traceability metadata, but it does not prove that a named regression test still exists. The next inexpensive hardening step is function-level test traceability.

### 3.2. Schema

`docs/CONTRACT_MATRIX.json` advances from `version: 1` to `version: 2`.

The v1 `tests` string-list is replaced by `test_refs`, a list of exact Python test selectors. Under schema v2, the legacy `tests` key is forbidden on contract entries; validation fails if it is present, even when `test_refs` is also present. This prevents mixed v1/v2 metadata from becoming silently authoritative.

Allowed selector forms are:

```text
path/to/test_file.py::test_function
path/to/test_file.py::TestClass::test_method
```

Example:

```json
{
  "id": "direct.preview-bound-write",
  "plugin": "yandex-direct",
  "status": "implemented",
  "skills": ["plugins/yandex-direct/skills/yandex-direct-api/SKILL.md"],
  "helpers": ["plugins/yandex-direct/scripts/yd_api.py"],
  "test_refs": [
    "plugins/yandex-direct/tests/test_approval.py::ApprovalContractTests::test_require_approval_rejects_without_leaking_expected_digest"
  ],
  "references": ["plugins/yandex-direct/references/safety.md"],
  "freshness_controlled_references": []
}
```

`implemented` and `infrastructure` contracts require at least one valid `test_ref`. `deferred` contracts may have none.

All existing matrix entries are migrated to v2. A contract may point to multiple exact test functions when several assertions jointly cover the traceability claim.

### 3.3. AST validation

`scripts/contract_controls.py` validates each `test_ref` without importing or executing test code.

For every selector it MUST verify:

1. the repository-relative path is safe, exists, and ends in `.py`;
2. the file is UTF-8 and parses with `ast.parse`;
3. the selector has exactly one of the two supported shapes;
4. the referenced top-level function or class method exists exactly once;
5. the terminal symbol begins with `test_`;
6. the referenced test is not statically skipped.

Static skip detection covers unconditional decorators and literal skip conditions that can be proven from syntax:

- `@unittest.skip(...)` or a decorator call whose terminal attribute/name is exactly `skip`;
- `@unittest.skipIf(True, ...)` or terminal name `skipIf` with literal boolean `True` as its first argument;
- `@unittest.skipUnless(False, ...)` or terminal name `skipUnless` with literal boolean `False` as its first argument;
- `@pytest.mark.skip(...)` (also covered by terminal name `skip`);
- the same skip decorators applied to the containing class.

Dynamic skip conditions, runtime `self.skipTest(...)`, conditional imports, and semantic correctness of assertions remain outside validator scope. The standard MUST continue to state that traceability is not semantic proof.

Malformed selectors, missing/duplicate symbols, parse failures, escaping paths, or statically skipped targets fail validation closed.

## 4. Normative requirements table

`docs/PLUGIN_STANDARD.md` and `docs/PLUGIN_STANDARD.en.md` replace the current compressed production-requirements paragraph with an explicit requirements table.

Each normative row has four fields:

| Field | Meaning |
|---|---|
| `REQ-ID` | stable repository requirement identifier |
| Requirement | concise normative rule |
| Enforcement | validator / CI / review / policy, including combinations |
| Canonical document | the authoritative repository document or executable contract |

For this migration, the RU and EN tables use exactly this stable ID set:

```text
REQ-SKILL-ROUTING
REQ-REFERENCE-VOLATILITY
REQ-HELPER-TESTS
REQ-EVAL-CONTRACT
REQ-READ-FIRST
REQ-WRITE-PREVIEW
REQ-EXPLICIT-APPROVAL
REQ-NO-SECRETS
REQ-CAPABILITY-MATRIX
REQ-PLUGIN-SEMVER
REQ-NO-UNIVERSAL-THRESHOLDS
REQ-RUNTIME-PATH-PORTABILITY
REQ-SOURCE-SEMANTICS
REQ-CROSS-SERVICE-TRANSPORT
REQ-BILINGUAL-DOCS
REQ-CHANGELOG-PARITY
REQ-DOCS-RELEASE-NO-PLUGIN-BUMP
```

These IDs map the requirements already present in the current standard; they do not introduce new plugin runtime behavior. Future releases may append new IDs deliberately, but MUST preserve the meaning of existing IDs rather than silently repurposing them.

RU and EN documents MUST carry the same `REQ-ID` set. Tests enforce identifier parity, uniqueness, and non-empty Requirement / Enforcement / Canonical document cells. Enforcement text must distinguish mechanical validator/CI coverage from review-only or policy-only obligations.

The purpose is to distinguish statements that are mechanically enforced from statements that require semantic review.

## 5. Review artifacts

Create a bilingual review-artifact area:

```text
docs/reviews/README.md
docs/reviews/README.en.md
docs/reviews/2026-09-05-opus-codex-governance.md
docs/reviews/2026-09-05-opus-codex-governance.en.md
```

The README pair defines the artifact convention: date/scope, reviewer type, reviewed commit or release when known, findings, disposition, evidence, limitations, and explicit distinction between AI review, human authorization, and CI.

The dated artifact records factual review history relevant to the current repository state, including:

- Opus 5 audit findings that motivated contract/governance hardening;
- which findings are already closed in current `main`, which are addressed by PR C, and which remain intentionally deferred/out of scope;
- Codex findings from the release-infrastructure PR and their RED→GREEN closure evidence;
- exact reviewed/candidate/main SHAs and CI run IDs when they are available from repository history;
- the explicit Codex code-review quota limitation that prevented a final exact-head re-review of PR #56;
- a statement that AI review is advisory/independent semantic input, not a substitute for human merge/release authorization.

The artifact MUST NOT claim a clean review when the reviewer was unavailable, and MUST NOT present CI success as semantic review.

Root RU/EN README documentation navigation links to the review index and latest dated artifact.

## 6. Security policy

Add:

```text
SECURITY.md
SECURITY.en.md
```

`SECURITY.md` is RU-primary and links reciprocally to the English mirror.

The policy defines:

- supported scope as the current default-branch/release line and current plugin versions, unless a historical version is explicitly declared supported;
- security-sensitive categories relevant to this repository: secret exposure, approval/write-safety bypass, prompt-injection/data-as-instructions boundary violations, cross-service transport/credential ownership violations, release/tag immutability failures, and dependency/supply-chain concerns;
- private reporting preference via GitHub's repository security reporting UI when available;
- fallback to a private contact method exposed by the repository owner/profile when the GitHub private-reporting UI is unavailable;
- if no private reporting route is available, a public issue may request a private contact channel but MUST NOT contain vulnerability details or sensitive material;
- a warning not to post exploit details, credentials, tokens, customer/account data, or other sensitive material in a public issue;
- no invented SLA, bounty, email address, or guaranteed response time.

RU/EN policy meaning must remain aligned.

## 7. `docs/superpowers/` status

Approved design/spec/plan files under `docs/superpowers/` remain valuable historical implementation records, but are not canonical production requirements.

Canonical normative sources are root governance documents, `docs/PLUGIN_STANDARD*`, `docs/RELEASE_POLICY*`, executable validators/tests, plugin SKILL/reference contracts, and machine-owned registries/matrices.

Changes required:

- `REVIEW_FIRST_RELEASE` RU/EN describes `docs/superpowers/` as historical implementation context, not an authoritative production contract;
- any root test that reads prose from a `docs/superpowers/` spec solely to enforce a production requirement is migrated to the canonical document or executable contract;
- no new production invariant may be enforced only by prose in `docs/superpowers/`.

This does not delete historical specs/plans and does not prohibit tests that merely verify links/files that are intentionally part of documentation navigation.

## 8. Validator and tests

The implementation follows strict RED → GREEN cycles.

Minimum regression coverage:

1. matrix v2 rejects a legacy `tests` key, including mixed `tests` + `test_refs` entries;
2. valid top-level function selector passes;
3. valid `unittest.TestCase` method selector passes;
4. missing function/class/method fails;
5. malformed selector fails;
6. repository-escaping test path fails;
7. non-Python selector path fails;
8. invalid Python syntax / non-UTF8 test source fails closed;
9. unconditional function-level skip fails;
10. class-level skip fails;
11. literal `skipIf(True)` and `skipUnless(False)` fail;
12. non-literal/dynamic skip conditions are not falsely treated as statically skipped;
13. all production matrix entries resolve to existing non-statically-skipped exact tests;
14. RU/EN `REQ-ID` sets match the fixed migration set, are unique, and every row has requirement, enforcement, and canonical source;
15. review artifacts and SECURITY RU/EN pairs exist with reciprocal links;
16. canonical governance docs no longer rely on `docs/superpowers/` prose as the sole enforcement source.

`python scripts/validate_repo.py` and `python -m unittest discover -s tests -v` remain the repository verification commands. Existing plugin jobs must stay green despite no plugin runtime changes.

## 9. Release `1.0.7`

PR C is repository-only.

Advance the declarative release set to repository `1.0.7`:

- `.github/releases/release.json` repository version/tag/title → `1.0.7`;
- add `.github/releases/1.0.7.md`;
- update RU/EN root README release markers;
- add matching RU/EN changelog `1.0.7` entries;
- keep `plugins: []` in the release declaration;
- do not change any plugin manifest or plugin changelog version.

Publication uses the single `publish-current-release.yml` engine from repository `1.0.6`.

Required completion evidence:

1. exact-head branch CI green;
2. independent review or explicitly documented reviewer/tool limitation;
3. squash merge with exact-head guard;
4. `main` ref equals merge SHA;
5. post-merge CI green on exact merge SHA;
6. generic publisher succeeds on that SHA;
7. release `1.0.7` is `immutable=true` and tag `1.0.7` points exactly to the merge SHA;
8. historical `1.0.6` remains immutable and still points to `88d2f45e63308a476cbe456402bf17dc847436cb`;
9. production plugin SemVer remains Direct `2.0.1`, Metrika `2.0.0`, Webmaster `2.0.0`, Wordstat `1.1.2`, Search `1.0.2`, SEO `1.1.2`, Marketing `1.1.0`.

## 10. Acceptance criteria

PR C is complete only when all of the following are true:

- contract traceability is function-level and AST-validated for matrix v2;
- statically skipped test targets cannot satisfy implemented/infrastructure traceability;
- PLUGIN_STANDARD makes enforcement ownership explicit through the fixed stable requirement IDs;
- repository contains bilingual, factual review evidence with reviewer limitations recorded honestly;
- repository contains a bilingual security policy without invented reporting coordinates or SLAs;
- `docs/superpowers/` is clearly historical/non-normative for production contracts;
- no plugin runtime file or plugin SemVer changes;
- repository `1.0.7` is published immutably by the generic declarative publisher with exact-SHA evidence.
