from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DocumentationGuardTests(unittest.TestCase):
    """String/structure guards for shipped documentation, not behavioral proof."""

    def test_repository_foundation_docs_exist(self):
        for path in [
            "docs/CONTRACT_MATRIX.json",
            "docs/PLUGIN_STANDARD.md",
            "docs/SERVICE_MATRIX.md",
            "docs/ROADMAP.md",
            "packages/README.md",
            "workflows/README.md",
        ]:
            self.assertTrue((ROOT / path).is_file(), path)

    def test_plugin_standard_documents_safety_lifecycle(self):
        standard = (ROOT / "docs/PLUGIN_STANDARD.md").read_text(encoding="utf-8")
        self.assertIn("read → analyze → preview → explicit approval → write → verify", standard)

    def test_roadmap_documents_shipped_phases(self):
        content = (ROOT / "docs/ROADMAP.md").read_text(encoding="utf-8")
        self.assertIn("### Phase 4 — Yandex Wordstat", content)
        self.assertIn("### Phase 5 — Yandex Search", content)
        self.assertIn("### Phase 6A — Yandex SEO", content)
        self.assertIn("### Phase 6B — Yandex Marketing", content)
        self.assertIn("### Phase 7 — Topical Architecture", content)
        self.assertIn("Wordstat `1.1.0`", content)
        self.assertIn("SEO `1.1.0`", content)
        self.assertIn("Search `1.0.2`", content)

    def test_roadmap_documents_marketing_implementation_boundary(self):
        content = (ROOT / "docs/ROADMAP.md").read_text(encoding="utf-8")
        marker = "### Phase 6B — Yandex Marketing"
        self.assertIn(marker, content)
        phase = content.split(marker, 1)[1].split("# Стратегия развития после 1.0.8", 1)[0]
        self.assertIn("Изначально выпущен как plugin `1.0.0`", phase)
        self.assertIn("не содержит Yandex API clients", phase)

    def test_release_history_documents_prior_releases(self):
        self.assertTrue((ROOT / "CHANGELOG.md").is_file())
        self.assertTrue((ROOT / "docs/REVIEW_FIRST_RELEASE.md").is_file())
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        review = (ROOT / "docs/REVIEW_FIRST_RELEASE.md").read_text(encoding="utf-8")
        self.assertIn("## [PHASE 7 1.0.1] — 2026-09-03", changelog)
        self.assertIn("## [PHASE 7 1.0.0] — 2026-09-02", changelog)
        self.assertIn("## [OPUS 1.1.1] — 2026-09-02", changelog)
        self.assertIn("## [OPUS 1.1.0] — 2026-09-02", changelog)
        self.assertIn("## [1.0.0] — 2026-09-02", changelog)
        self.assertIn("First Release Independent Review Guide", review)

    def test_future_services_remain_documented_as_frozen_backlog(self):
        roadmap = (ROOT / "docs/ROADMAP.md").read_text(encoding="utf-8")
        matrix = (ROOT / "docs/SERVICE_MATRIX.md").read_text(encoding="utf-8")
        self.assertIn("## Frozen expansion backlog", roadmap)
        self.assertIn("заморожены для реализации", roadmap)
        self.assertNotIn("## Phase 7 — Operations, AI, mobile", roadmap)
        for service in ["Yandex Tracker", "Yandex 360", "Yandex Maps", "AppMetrica", "YandexGPT", "SpeechKit"]:
            self.assertIn(service, roadmap)
        self.assertIn("| Yandex Tracker | 2 | backlog |", matrix)
        self.assertIn("| SpeechKit | 3 | backlog |", matrix)


if __name__ == "__main__":
    unittest.main()
