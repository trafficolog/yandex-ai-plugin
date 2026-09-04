import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from scripts import validate_repo


@unittest.skipUnless(os.name == "posix", "byte-oriented filenames require POSIX")
class RepositoryDotenvNonUtf8FilenameTests(unittest.TestCase):
    def test_non_utf8_tracked_filename_does_not_disable_staged_dotenv_scan(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / ".env.production"
            target.write_text(
                "YANDEX_DIRECT_TOKEN=y0_AgAAAAJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJ\n",
                encoding="utf-8",
            )
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)

            invalid_name = os.fsencode(root) + b"/unrelated-\xff.txt"
            fd = os.open(invalid_name, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
            try:
                os.write(fd, b"unrelated\n")
            finally:
                os.close(fd)

            subprocess.run(["git", "add", "--all"], cwd=root, check=True)
            target.write_text("YANDEX_DIRECT_TOKEN=\n", encoding="utf-8")

            errors: list[str] = []
            validate_repo._validate_repository_dotenv(root, errors)

            self.assertIn(
                f"credential-like secret found in repository dotenv file: {target}",
                errors,
            )


if __name__ == "__main__":
    unittest.main()
