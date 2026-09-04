from pathlib import Path
import subprocess
import tempfile
import unittest

from scripts import validate_repo


class RepositoryDotenvSymlinkTargetTests(unittest.TestCase):
    def test_tracked_repository_dotenv_symlink_is_rejected_even_with_benign_tracked_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "config/credentials"
            target.parent.mkdir(parents=True)
            target.write_text(
                "YANDEX_DIRECT_TOKEN=y0_AgAAAAHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH\n",
                encoding="utf-8",
            )
            link = root / ".env"
            link.symlink_to("config/credentials")
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "add", ".env", "config/credentials"], cwd=root, check=True)

            errors: list[str] = []
            validate_repo._validate_repository_dotenv(root, errors)

            self.assertIn(
                f"repository dotenv symlink is not allowed: {link}",
                errors,
            )


if __name__ == "__main__":
    unittest.main()
