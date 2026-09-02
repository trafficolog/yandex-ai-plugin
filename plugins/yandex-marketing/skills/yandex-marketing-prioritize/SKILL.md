---
name: yandex-marketing-prioritize
description: Use when ordering cross-service marketing findings and preparing safe delegated action previews.
---
# Marketing prioritization

Default prioritization is categorical and evidence-based. The default group order contains only finding types actually implemented by local deterministic `find_*` producers. `IMPLEMENTED_FINDING_TYPES` is the authoritative local set; future/unsupported classes are represented by `DEFERRED_FINDING_TYPES` and are not presented as shipped local findings.

Unknown or deferred external findings sort after implemented findings and receive `UNKNOWN_OR_DEFERRED_TYPE` metadata. Do not invent an opaque Marketing Score.

If the user supplies priorities or weights, disclose them. Delegated actions are preview-only and only exist for explicitly supported implemented/approved external types. Route budgets to `yandex-direct-budget`, supported query changes to `yandex-direct-keywords`, and explicitly recommended goal changes to `yandex-metrika-goals`. There is no executable `NEW_CAMPAIGN_CANDIDATE` route in 1.1.0. Consequential actions require explicit approval in the owning plugin.
