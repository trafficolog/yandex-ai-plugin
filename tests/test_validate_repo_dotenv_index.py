from pathlib import Path
import subprocess
import tempfile
import unittest

from scripts import validate_repo


class RepositoryDotenvIndexTests(unittest.TestCase):
    def test_staged_dotenv_secret_is_scanned_when_worktree_copy_is_scrubbed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / ".env.production"
            target.write_text(
                "YANDEX_DIRECT_TOKEN=y0_AgAAAAIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII\n",
                encoding="utf-8",
            )
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "add", ".env.production"], cwd=root, check=True)
            target.write_text("YANDEX_DIRECT_TOKEN=\n", encoding="utf-8")

            errors: list[str] = []
            validate_repo._validate_repository_dotenv(root, errors)

            self.assertIn(
                f"credential-like secret found in repository dotenv file: {target}",
                errors,
            )


if __name__ == "__main__":
    unittest.main()
