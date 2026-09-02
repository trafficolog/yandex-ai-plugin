# Cross-service safety

Verified design baseline: 2026-09-01.

`yandex-seo` is read/analyze/recommend/preview only. It may generate a delegated action descriptor naming the owning service plugin, skill, target, reason and `requires_approval`, but it never executes a live change. The owning plugin must perform its own preview and approval flow.
