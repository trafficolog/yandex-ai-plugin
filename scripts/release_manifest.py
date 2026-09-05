#!/usr/bin/env python3
"""Validate and normalize the declarative release manifest."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys
from typing import Any


DEFAULT_MANIFEST = Path(".github/releases/release.json")
RELEASES_DIR = Path(".github/releases")
SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)
TSV_CONTROL_CHARS = ("\t", "\r", "\n")


@dataclass(frozen=True)
class ReleaseItem:
    kind: str
    name: str
    version: str
    tag: str
    title: str
    notes_file: str


def _manifest_file(root: Path, manifest_path: Path | None) -> Path:
    selected = manifest_path or DEFAULT_MANIFEST
    if selected.is_absolute():
        return selected
    return root / selected


def load_release_manifest(root: Path, manifest_path: Path | None = None) -> dict[str, Any]:
    """Load the manifest as a JSON object.

    Validation is intentionally separate so callers can receive a complete
    list of contract errors instead of an exception for the first one.
    """

    root = Path(root).resolve()
    path = _manifest_file(root, manifest_path)
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("release manifest root must be a JSON object")
    return data


def _read_json_object(path: Path, label: str, errors: list[str]) -> dict[str, Any] | None:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except FileNotFoundError:
        errors.append(f"{label} does not exist: {path}")
        return None
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        errors.append(f"{label} is unreadable or invalid JSON: {path}: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{label} must contain a JSON object: {path}")
        return None
    return value


def _required_string(obj: dict[str, Any], key: str, label: str, errors: list[str]) -> str | None:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label}.{key} must be a non-empty string")
        return None
    if any(control in value for control in TSV_CONTROL_CHARS):
        errors.append(f"{label}.{key} must not contain a TSV control character")
        return None
    return value.strip()


def _validate_notes_file(root: Path, notes_file: str | None, label: str, errors: list[str]) -> None:
    if notes_file is None:
        return
    relative = Path(notes_file)
    releases_root = (root / RELEASES_DIR).resolve()
    if relative.is_absolute():
        errors.append(f"{label}.notes_file must stay under .github/releases and be repository-relative")
        return
    resolved = (root / relative).resolve()
    try:
        resolved.relative_to(releases_root)
    except ValueError:
        errors.append(f"{label}.notes_file must stay under .github/releases")
        return
    if resolved.suffix.lower() != ".md":
        errors.append(f"{label}.notes_file must be a Markdown file under .github/releases")
    if not resolved.is_file():
        errors.append(f"{label} notes file does not exist: {notes_file}")


def _validate_repository_release_surfaces(root: Path, version: str | None, errors: list[str]) -> None:
    if version is None:
        return
    required_markers = {
        "README.md": f"release-{version}",
        "README.en.md": f"release-{version}",
        "CHANGELOG.md": f"## [{version}]",
        "CHANGELOG.en.md": f"## [{version}]",
    }
    for filename, marker in required_markers.items():
        path = root / filename
        try:
            text = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            errors.append(f"{filename} does not exist for declared repository release {version}")
            continue
        except (OSError, UnicodeError) as exc:
            errors.append(f"{filename} is unreadable for declared repository release {version}: {exc}")
            continue
        if marker not in text:
            errors.append(
                f"{filename} must contain declared repository release {version} marker {marker!r}"
            )


def validate_release_manifest(root: Path, manifest_path: Path | None = None) -> list[str]:
    """Return release-manifest contract errors; an empty list means valid."""

    root = Path(root).resolve()
    path = _manifest_file(root, manifest_path)
    errors: list[str] = []

    try:
        data = load_release_manifest(root, manifest_path)
    except FileNotFoundError:
        return [f"release manifest does not exist: {path}"]
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        return [f"release manifest is invalid: {path}: {exc}"]

    if data.get("schema_version") != 1:
        errors.append("release manifest schema_version must equal 1")

    repository = data.get("repository")
    if not isinstance(repository, dict):
        errors.append("release manifest repository must be an object")
        repository = {}

    plugins = data.get("plugins")
    if not isinstance(plugins, list):
        errors.append("release manifest plugins must be a list")
        plugins = []

    repository_version = _required_string(repository, "version", "repository", errors)
    repository_tag = _required_string(repository, "tag", "repository", errors)
    _required_string(repository, "title", "repository", errors)
    repository_notes = _required_string(repository, "notes_file", "repository", errors)

    if repository_version is not None and SEMVER_RE.fullmatch(repository_version) is None:
        errors.append(f"repository version must be strict SemVer: {repository_version}")
    if repository_version is not None and repository_tag is not None and repository_tag != repository_version:
        errors.append(
            f"repository tag must equal version: tag={repository_tag!r} version={repository_version!r}"
        )
    _validate_notes_file(root, repository_notes, "repository", errors)
    _validate_repository_release_surfaces(root, repository_version, errors)

    seen_plugins: set[str] = set()
    seen_tags: set[str] = set()
    if repository_tag is not None:
        seen_tags.add(repository_tag)

    for index, raw in enumerate(plugins):
        label = f"plugins[{index}]"
        if not isinstance(raw, dict):
            errors.append(f"{label} must be an object")
            continue

        plugin = _required_string(raw, "plugin", label, errors)
        version = _required_string(raw, "version", label, errors)
        tag = _required_string(raw, "tag", label, errors)
        _required_string(raw, "title", label, errors)
        notes_file = _required_string(raw, "notes_file", label, errors)
        _validate_notes_file(root, notes_file, label, errors)

        if plugin is not None:
            if plugin in seen_plugins:
                errors.append(f"duplicate plugin in release manifest: {plugin}")
            seen_plugins.add(plugin)

        if tag is not None:
            if tag in seen_tags:
                errors.append(f"duplicate release tag in release manifest: {tag}")
            seen_tags.add(tag)

        if version is not None and SEMVER_RE.fullmatch(version) is None:
            errors.append(f"{label}.version must be strict SemVer: {version}")

        if plugin is not None and version is not None and tag is not None:
            expected_tag = f"{plugin}-v{version}"
            if tag != expected_tag:
                errors.append(
                    f"{label}.tag must equal canonical plugin tag {expected_tag!r}; got {tag!r}"
                )

        if plugin is None:
            continue
        plugin_root = root / "plugins" / plugin
        if not plugin_root.is_dir():
            errors.append(f"declared plugin does not exist: {plugin}")
            continue

        if version is None:
            continue
        for manifest_rel in (Path(".codex-plugin/plugin.json"), Path(".claude-plugin/plugin.json")):
            manifest = _read_json_object(
                plugin_root / manifest_rel,
                f"{plugin} {manifest_rel.as_posix()}",
                errors,
            )
            if manifest is None:
                continue
            actual = manifest.get("version")
            if actual != version:
                errors.append(
                    f"{plugin} {manifest_rel.as_posix()} version {actual!r}, expected declared {version!r}"
                )

    return errors


def release_items(root: Path, manifest_path: Path | None = None) -> list[ReleaseItem]:
    """Return normalized release items after validating the declaration."""

    root = Path(root).resolve()
    errors = validate_release_manifest(root, manifest_path)
    if errors:
        raise ValueError("; ".join(errors))
    data = load_release_manifest(root, manifest_path)
    repository = data["repository"]
    items = [
        ReleaseItem(
            kind="repository",
            name="repository",
            version=repository["version"],
            tag=repository["tag"],
            title=repository["title"],
            notes_file=repository["notes_file"],
        )
    ]
    for plugin in data["plugins"]:
        items.append(
            ReleaseItem(
                kind="plugin",
                name=plugin["plugin"],
                version=plugin["version"],
                tag=plugin["tag"],
                title=plugin["title"],
                notes_file=plugin["notes_file"],
            )
        )
    return items


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--manifest", default=None, help="Manifest path relative to root")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate", help="Validate the release declaration")
    items_parser = subparsers.add_parser("items", help="Print normalized release items")
    items_parser.add_argument("--format", choices=("tsv",), default="tsv")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    root = Path(args.root)
    manifest_path = Path(args.manifest) if args.manifest else None

    if args.command == "validate":
        errors = validate_release_manifest(root, manifest_path)
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            return 1
        return 0

    try:
        items = release_items(root, manifest_path)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    for item in items:
        print(
            "\t".join(
                (
                    item.kind,
                    item.name,
                    item.version,
                    item.tag,
                    item.title,
                    item.notes_file,
                )
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
