from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ProductStrategyRoadmapTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_roadmap_prioritizes_methodology_over_api_catalog_expansion(self):
        ru = self.read("docs/ROADMAP.md")
        en = self.read("docs/ROADMAP.en.md")

        for token in (
            "Методология, safety и orchestration",
            "транспорт остаётся заменяемым",
            "задачи пользователя, а не каталог API Яндекса",
        ):
            self.assertIn(token, ru)

        for token in (
            "methodology, safety, and orchestration",
            "transport remains replaceable",
            "user problems rather than the Yandex API catalog",
        ):
            self.assertIn(token, en)

    def test_roadmap_orders_four_depth_first_product_bets(self):
        for filename in ("docs/ROADMAP.md", "docs/ROADMAP.en.md"):
            text = self.read(filename)
            with self.subTest(filename=filename):
                p0 = text.index("P0")
                p1 = text.index("P1")
                p2 = text.index("P2")
                p3 = text.index("P3")
                self.assertLess(p0, p1)
                self.assertLess(p1, p2)
                self.assertLess(p2, p3)
                for token in (
                    "preview_id",
                    "decisions.jsonl",
                    "USER_STATED",
                    "self-contained HTML",
                    "Mermaid/DOT",
                    "eval runner",
                ):
                    self.assertIn(token, text)

    def test_project_memory_is_domain_memory_not_runtime_memory(self):
        for filename in ("docs/ROADMAP.md", "docs/ROADMAP.en.md"):
            text = self.read(filename)
            with self.subTest(filename=filename):
                for token in (
                    ".yandex-ai/project.yaml",
                    ".yandex-ai/decisions.jsonl",
                    ".yandex-ai/baselines/",
                    ".yandex-ai/hypotheses.md",
                    "USER_STATED",
                ):
                    self.assertIn(token, text)
                self.assertIn("secrets", text.lower())

    def test_desktop_ui_and_service_expansion_are_explicitly_deprioritized(self):
        ru = self.read("docs/ROADMAP.md")
        en = self.read("docs/ROADMAP.en.md")

        for token in ("Electron", "Frozen expansion backlog", "Tracker", "Yandex 360", "Maps", "AppMetrica", "YandexGPT", "SpeechKit"):
            self.assertIn(token, ru)
            self.assertIn(token, en)

        self.assertIn("90-днев", ru)
        self.assertIn("90-day", en)
        self.assertIn("low-maintenance", ru)
        self.assertIn("low-maintenance", en)


if __name__ == "__main__":
    unittest.main()
