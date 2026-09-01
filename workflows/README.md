# Cross-service workflows

This directory will contain workflows that orchestrate multiple stable Yandex service plugins.

A workflow composes service capabilities; it must not duplicate low-level API clients or copy volatile API reference material from component plugins.

Planned examples: `yandex-marketing`, `yandex-seo`, `yandex-ecommerce`, and `yandex-mobile-growth`.
