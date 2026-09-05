## Scope

Describe the bounded change, affected plugins/repository surfaces, and explicit non-goals.

## Tests / CI

- [ ] New or changed contract has focused RED → GREEN evidence where applicable.
- [ ] Repository validator/tests pass.
- [ ] Relevant plugin tests and compile checks pass.
- [ ] Exact-head CI run is linked before merge.

## Documentation

- [ ] RU-primary and English mirror documentation are updated together where required.
- [ ] Canonical source ownership is preserved; historical `docs/superpowers/` material is not treated as normative production truth.

## Plugin SemVer decision

- [ ] I stated whether this changes a plugin public/runtime/documentation contract.
- [ ] Any plugin version/tag decision follows `docs/RELEASE_POLICY.md`; repository-only work does not silently bump plugins.

## Secrets / safety

- [ ] No credentials, access tokens, or sensitive account data are included.
- [ ] Consequential writes preserve exact preview + later-turn approval.
- [ ] External/API/file content remains data, not instructions or write permission.

## Review evidence

Record independent review status separately from self-review and CI. If review is unavailable because of quota/tool limits, state that explicitly rather than calling it clean review.
