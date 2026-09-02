#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import re
import sys
from typing import Any

FORBIDDEN_SKILL_PATHS = ("~/.openclaw/", "~/.claude/", "~/.codex/")
ALLOWED_EVAL_WRITE = {False, "preview-first", "approval-required"}


def _load_json(path: Path, errors: list[str]) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing required JSON file: {path}")
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        errors.append(f"invalid JSON in {path}: {exc}")
    return None


def _frontmatter(text: str) -> dict[str, str] | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    result: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip()
    return result


def _validate_skill(skill_path: Path, errors: list[str]) -> None:
    text = skill_path.read_text(encoding="utf-8")
    fm = _frontmatter(text)
    if fm is None:
        errors.append(f"skill frontmatter missing or malformed: {skill_path}")
        return
    if not fm.get("name"):
        errors.append(f"skill frontmatter missing name: {skill_path}")
    description = fm.get("description", "")
    if not description.startswith("Use when"):
        errors.append(f"skill description must start with 'Use when': {skill_path}")
    for forbidden in FORBIDDEN_SKILL_PATHS:
        if forbidden in text:
            errors.append(
                f"runtime-specific absolute path '{forbidden}' found in skill: {skill_path}"
            )


def _validate_evals(plugin_path: Path, errors: list[str]) -> None:
    path = plugin_path / "evals/scenarios.json"
    data = _load_json(path, errors)
    if not isinstance(data, dict):
        return
    scenarios = data.get("scenarios")
    if data.get("version") != 1 or not isinstance(scenarios, list) or not scenarios:
        errors.append(f"invalid evals/scenarios.json structure: {path}")
        return
    for index, scenario in enumerate(scenarios):
        if not isinstance(scenario, dict):
            errors.append(f"invalid eval scenario #{index}: {path}")
            continue
        if not isinstance(scenario.get("prompt"), str) or not scenario["prompt"].strip():
            errors.append(f"eval scenario #{index} missing prompt: {path}")
        if not isinstance(scenario.get("skill"), str) or not scenario["skill"].strip():
            errors.append(f"eval scenario #{index} missing skill: {path}")
        if scenario.get("write") not in ALLOWED_EVAL_WRITE:
            errors.append(f"eval scenario #{index} has invalid write mode: {path}")


def _validate_plugin(plugin_path: Path, errors: list[str]) -> None:
    manifest_path = plugin_path / ".codex-plugin/plugin.json"
    manifest = _load_json(manifest_path, errors)
    if not isinstance(manifest, dict):
        return

    version = manifest.get("version")
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        errors.append(f"plugin manifest has invalid SemVer version: {manifest_path}")

    skills_value = manifest.get("skills")
    if not isinstance(skills_value, str):
        errors.append(f"plugin manifest missing skills path: {manifest_path}")
        return
    skills_path = plugin_path / skills_value
    if not skills_path.is_dir():
        errors.append(f"plugin skills target does not exist: {skills_path}")
        return

    skill_files = sorted(skills_path.glob("*/SKILL.md"))
    if not skill_files:
        errors.append(f"plugin has no discoverable SKILL.md files: {skills_path}")
    for skill_path in skill_files:
        _validate_skill(skill_path, errors)

    _validate_evals(plugin_path, errors)


def validate_repository(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    marketplace_path = root / ".agents/plugins/marketplace.json"
    marketplace = _load_json(marketplace_path, errors)
    if not isinstance(marketplace, dict):
        return errors

    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        errors.append(f"marketplace has no plugins: {marketplace_path}")
        return errors

    for item in plugins:
        if not isinstance(item, dict):
            errors.append(f"marketplace plugin entry is not an object: {marketplace_path}")
            continue
        source = item.get("source")
        if not isinstance(source, dict) or source.get("source") != "local":
            errors.append(f"marketplace plugin must use local source object: {item.get('name')}")
            continue
        raw_path = source.get("path")
        if not isinstance(raw_path, str) or not raw_path:
            errors.append(f"marketplace plugin source path missing: {item.get('name')}")
            continue
        plugin_path = (root / raw_path).resolve()
        try:
            plugin_path.relative_to(root)
        except ValueError:
            errors.append(f"marketplace source escapes repository root: {raw_path}")
            continue
        if not plugin_path.is_dir():
            errors.append(f"marketplace source path does not exist: {raw_path}")
            continue
        _validate_plugin(plugin_path, errors)

    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors = validate_repository(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Repository validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
