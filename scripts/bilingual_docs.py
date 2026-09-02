from __future__ import annotations

from pathlib import Path
import re

KEY_DOC_NAMES = (
    "SERVICE_MATRIX",
    "ROADMAP",
    "PLUGIN_STANDARD",
    "REVIEW_FIRST_RELEASE",
)

_RELEASE_MARKER = re.compile(
    r"^##\s+(?:\[)?((?:DOCS|OPUS)\s+\d+\.\d+\.\d+|\d+\.\d+\.\d+)(?:\])?(?:\s|—|$)",
    re.MULTILINE,
)


def release_markers(text: str) -> list[str]:
    return _RELEASE_MARKER.findall(text)


def _read(path: Path, errors: list[str]) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(f"bilingual documentation missing: {path}")
    except UnicodeDecodeError:
        errors.append(f"bilingual documentation is not UTF-8: {path}")
    return None


def _validate_pair(
    ru_path: Path,
    en_path: Path,
    errors: list[str],
    *,
    compare_release_markers: bool = False,
) -> None:
    ru = _read(ru_path, errors)
    en = _read(en_path, errors)
    if ru is None or en is None:
        return

    if en_path.name not in ru:
        errors.append(
            f"bilingual documentation language switch missing English link: {ru_path} -> {en_path.name}"
        )
    if ru_path.name not in en:
        errors.append(
            f"bilingual documentation language switch missing Russian link: {en_path} -> {ru_path.name}"
        )

    if compare_release_markers:
        ru_markers = release_markers(ru)
        en_markers = release_markers(en)
        if ru_markers != en_markers:
            errors.append(
                f"bilingual changelog release markers differ: {ru_path}={ru_markers} vs {en_path}={en_markers}"
            )


def validate_bilingual_docs(root: Path, plugin_dirs: set[str]) -> list[str]:
    root = root.resolve()
    errors: list[str] = []

    _validate_pair(root / "README.md", root / "README.en.md", errors)
    _validate_pair(
        root / "CHANGELOG.md",
        root / "CHANGELOG.en.md",
        errors,
        compare_release_markers=True,
    )

    for name in KEY_DOC_NAMES:
        _validate_pair(
            root / "docs" / f"{name}.md",
            root / "docs" / f"{name}.en.md",
            errors,
        )

    for plugin_dir in sorted(plugin_dirs):
        plugin = root / "plugins" / plugin_dir
        _validate_pair(plugin / "README.md", plugin / "README.en.md", errors)
        _validate_pair(
            plugin / "CHANGELOG.md",
            plugin / "CHANGELOG.en.md",
            errors,
            compare_release_markers=True,
        )

    return errors
