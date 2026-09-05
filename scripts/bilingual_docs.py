from __future__ import annotations

import json
from pathlib import Path
import re

try:
    from .version_contracts import validate_plugin_version_mentions
except ImportError:
    from version_contracts import validate_plugin_version_mentions

KEY_DOC_NAMES = (
    "SERVICE_MATRIX",
    "ROADMAP",
    "PLUGIN_STANDARD",
    "REVIEW_FIRST_RELEASE",
    "GETTING_STARTED",
    "ARCHITECTURE",
    "GLOSSARY",
    "RELEASE_POLICY",
)
ROOT_POLICY_NAMES = (
    "SECURITY",
    "CODE_OF_CONDUCT",
)

_RELEASE_MARKER = re.compile(
    r"^##\s+(?:\[)?((?:(?:[A-Z][A-Z0-9]*(?:\s+[A-Z0-9]+)*)\s+)?\d+\.\d+\.\d+)(?:\])?(?:\s|—|$)",
    re.MULTILINE,
)
_HEADING_PATTERN = re.compile(r"^(#{2,6})\s+", re.MULTILINE)
_SEMVER_PATTERN = re.compile(r"(?<![0-9.])\d+\.\d+\.\d+(?![0-9.])")


def release_markers(text: str) -> list[str]:
    return _RELEASE_MARKER.findall(text)


def _heading_structure(text: str) -> list[int]:
    return [len(marker) for marker in _HEADING_PATTERN.findall(text)]


def _semver_tokens(text: str) -> set[str]:
    return set(_SEMVER_PATTERN.findall(text))


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

    ru_structure = _heading_structure(ru)
    en_structure = _heading_structure(en)
    if ru_structure != en_structure:
        errors.append(
            f"bilingual documentation heading structure differs: {ru_path}={ru_structure} vs {en_path}={en_structure}"
        )

    ru_semvers = _semver_tokens(ru)
    en_semvers = _semver_tokens(en)
    if ru_semvers != en_semvers:
        errors.append(
            f"bilingual documentation SemVer tokens differ: {ru_path}={sorted(ru_semvers)} vs {en_path}={sorted(en_semvers)}"
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

    for name in ROOT_POLICY_NAMES:
        _validate_pair(root / f"{name}.md", root / f"{name}.en.md", errors)

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
        manifest_path = plugin / ".codex-plugin" / "plugin.json"
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        version = manifest.get("version") if isinstance(manifest, dict) else None
        if isinstance(version, str):
            validate_plugin_version_mentions(root, plugin, version, errors)

    return errors
