#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import re
import sys
from typing import Any

FORBIDDEN_RUNTIME_PATHS = ("~/.openclaw/", "~/.claude/", "~/.codex/")
ALLOWED_EVAL_WRITE = {False, "preview-first", "approval-required"}
TEXT_SUFFIXES = {".md", ".py", ".json", ".yml", ".yaml", ".txt", ".toml"}
CAPABILITY_HEADER = "| Capability | Read | Write | MCP/App | Bundled API | File fallback |"
CROSS_SERVICE_PLUGINS = {"yandex-seo", "yandex-marketing"}
SUPPORTED_AUTHENTICATION_POLICIES = {"ON_INSTALL", "ON_USE"}
SECRET_PATTERNS = (
    re.compile(r"Authorization\s*:\s*(?:Bearer|OAuth)\s+[A-Za-z0-9._-]{16,}", re.IGNORECASE),
    re.compile(r"Api-Key\s+[A-Za-z0-9._-]{16,}", re.IGNORECASE),
    re.compile(r"\bAQVN[A-Za-z0-9_-]{8,}\b"),
)
TRANSPORT_PATTERNS = (
    re.compile(r"\bimport\s+urllib\.request\b"),
    re.compile(r"\bfrom\s+urllib\s+import\s+request\b"),
    re.compile(r"\bimport\s+(?:requests|httpx|aiohttp)\b"),
    re.compile(r"\bfrom\s+(?:requests|httpx|aiohttp)\b"),
    re.compile(r"https://(?:api(?:-[a-z]+)?\.yandex\.(?:com|net)|searchapi\.api\.cloud\.yandex\.net)"),
)


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
    lines = text[4:end].splitlines()
    result: dict[str, str] = {}
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip() or line.lstrip().startswith("#"):
            index += 1
            continue
        if line[:1].isspace() or ":" not in line:
            index += 1
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value in {">", "|"}:
            folded: list[str] = []
            index += 1
            while index < len(lines):
                continuation = lines[index]
                if continuation and not continuation[:1].isspace():
                    break
                if continuation.strip():
                    folded.append(continuation.strip())
                index += 1
            result[key] = " ".join(folded) if value == ">" else "\n".join(folded)
            continue
        result[key] = value.strip('"\'')
        index += 1
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
        prompt = scenario.get("prompt")
        skill = scenario.get("skill")
        if not isinstance(prompt, str) or not prompt.strip():
            errors.append(f"eval scenario #{index} missing prompt: {path}")
        if not isinstance(skill, str) or not skill.strip():
            errors.append(f"eval scenario #{index} missing skill: {path}")
        if scenario.get("write") not in ALLOWED_EVAL_WRITE:
            errors.append(f"eval scenario #{index} has invalid write mode: {path}")

        expect = scenario.get("expect")
        if not isinstance(expect, dict):
            errors.append(f"eval scenario #{index} missing expect object: {path}")
            continue
        route = expect.get("must_route_to")
        if not isinstance(route, str) or not route.strip():
            errors.append(f"eval scenario #{index} expect.must_route_to is required: {path}")
        elif isinstance(skill, str) and route != skill:
            errors.append(f"eval scenario #{index} expect.must_route_to must match skill: {path}")
        if not isinstance(expect.get("must_refuse"), bool):
            errors.append(f"eval scenario #{index} expect.must_refuse must be boolean: {path}")
        for field in ("must_mention", "must_not_claim"):
            values = expect.get(field)
            if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
                errors.append(f"eval scenario #{index} expect.{field} must be a string list: {path}")


def _iter_plugin_text_files(plugin_path: Path):
    for path in plugin_path.rglob("*"):
        if not path.is_file():
            continue
        if path.name == ".env.example" or path.suffix.lower() in TEXT_SUFFIXES:
            yield path


def _validate_plugin_text(plugin_path: Path, errors: list[str]) -> None:
    for path in _iter_plugin_text_files(plugin_path):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for forbidden in FORBIDDEN_RUNTIME_PATHS:
            if forbidden in text:
                errors.append(f"runtime-specific absolute path '{forbidden}' found in plugin file: {path}")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"credential-like secret found in plugin file: {path}")
                break


def _validate_cross_service_transport(plugin_path: Path, errors: list[str]) -> None:
    if plugin_path.name not in CROSS_SERVICE_PLUGINS:
        return
    scripts = plugin_path / "scripts"
    if not scripts.is_dir():
        return
    for path in scripts.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if any(pattern.search(text) for pattern in TRANSPORT_PATTERNS):
            errors.append(f"cross-service transport/API client found in {path}")


def _manifest_version(path: Path, errors: list[str]) -> tuple[dict[str, Any] | None, str | None]:
    manifest = _load_json(path, errors)
    if not isinstance(manifest, dict):
        return None, None
    version = manifest.get("version")
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        errors.append(f"plugin manifest has invalid SemVer version: {path}")
        return manifest, None
    return manifest, version


def _validate_plugin(
    root: Path,
    plugin_path: Path,
    agent_entry: dict[str, Any],
    claude_entry: dict[str, Any] | None,
    errors: list[str],
) -> None:
    codex_path = plugin_path / ".codex-plugin/plugin.json"
    claude_path = plugin_path / ".claude-plugin/plugin.json"
    codex, codex_version = _manifest_version(codex_path, errors)
    claude, claude_version = _manifest_version(claude_path, errors)
    if not isinstance(codex, dict):
        return

    agent_version = agent_entry.get("version")
    if not isinstance(agent_version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", agent_version):
        errors.append(f"agent marketplace plugin version missing or invalid: {agent_entry.get('name')}")
    versions = {
        "agent marketplace": agent_version,
        "codex manifest": codex_version,
        "claude manifest": claude_version,
        "claude marketplace": claude_entry.get("version") if isinstance(claude_entry, dict) else None,
    }
    present_versions = {value for value in versions.values() if isinstance(value, str)}
    if len(present_versions) > 1:
        errors.append(f"version mismatch for {agent_entry.get('name')}: {versions}")

    plugin_name = agent_entry.get("name")
    policy = agent_entry.get("policy")
    authentication = policy.get("authentication") if isinstance(policy, dict) else None
    if authentication not in SUPPORTED_AUTHENTICATION_POLICIES:
        errors.append(f"unsupported or missing authentication policy for {plugin_name}: {authentication}")
    if plugin_name in CROSS_SERVICE_PLUGINS:
        if authentication != "ON_USE":
            errors.append(f"cross-service authentication policy must be ON_USE for {plugin_name}")
        if (plugin_path / ".env.example").exists():
            errors.append(f"cross-service plugin must not define .env.example: {plugin_name}")

    if codex.get("name") != plugin_name:
        errors.append(f"codex manifest name mismatch for {plugin_name}: {codex_path}")
    if isinstance(claude, dict) and claude.get("name") != plugin_name:
        errors.append(f"claude manifest name mismatch for {plugin_name}: {claude_path}")
    if not isinstance(claude_entry, dict):
        errors.append(f"plugin missing from .claude-plugin/marketplace.json: {plugin_name}")
    else:
        expected_source = f"./plugins/{plugin_path.name}"
        if claude_entry.get("source") != expected_source:
            errors.append(f"claude marketplace source mismatch for {plugin_name}")

    skills_value = codex.get("skills")
    if not isinstance(skills_value, str):
        errors.append(f"plugin manifest missing skills path: {codex_path}")
        return
    if isinstance(claude, dict) and claude.get("skills") != skills_value:
        errors.append(f"skills path mismatch between plugin manifests: {plugin_path}")
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
    _validate_plugin_text(plugin_path, errors)
    _validate_cross_service_transport(plugin_path, errors)

    readme_path = plugin_path / "README.md"
    try:
        plugin_readme = readme_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(f"missing plugin README: {readme_path}")
        plugin_readme = ""
    if CAPABILITY_HEADER not in plugin_readme:
        errors.append(f"plugin README missing capability matrix: {readme_path}")

    if isinstance(codex_version, str):
        changelog_path = plugin_path / "CHANGELOG.md"
        try:
            changelog = changelog_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            errors.append(f"missing plugin CHANGELOG: {changelog_path}")
            changelog = ""
        if not re.search(rf"^##\s+(?:\[)?{re.escape(codex_version)}(?:\])?(?:\s|$)", changelog, re.MULTILINE):
            errors.append(f"CHANGELOG version {codex_version} missing for {plugin_name}: {changelog_path}")

        root_readme_path = root / "README.md"
        try:
            root_readme = root_readme_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            errors.append(f"missing root README: {root_readme_path}")
            root_readme = ""
        plugin_marker = f"plugins/{plugin_path.name}/"
        matching_rows = [line for line in root_readme.splitlines() if plugin_marker in line]
        if not any(re.search(rf"\|\s*{re.escape(codex_version)}\s*\|", line) for line in matching_rows):
            errors.append(f"root README version {codex_version} missing for {plugin_name}")


def validate_repository(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    agent_marketplace_path = root / ".agents/plugins/marketplace.json"
    claude_marketplace_path = root / ".claude-plugin/marketplace.json"
    agent_marketplace = _load_json(agent_marketplace_path, errors)
    claude_marketplace = _load_json(claude_marketplace_path, errors)
    if not isinstance(agent_marketplace, dict) or not isinstance(claude_marketplace, dict):
        return errors

    plugins = agent_marketplace.get("plugins")
    claude_plugins = claude_marketplace.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        errors.append(f"marketplace has no plugins: {agent_marketplace_path}")
        return errors
    if not isinstance(claude_plugins, list):
        errors.append(f"marketplace has no plugins: {claude_marketplace_path}")
        claude_plugins = []
    claude_by_name = {
        item.get("name"): item
        for item in claude_plugins
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    }

    for item in plugins:
        if not isinstance(item, dict):
            errors.append(f"marketplace plugin entry is not an object: {agent_marketplace_path}")
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
        _validate_plugin(root, plugin_path, item, claude_by_name.get(item.get("name")), errors)

    agent_names = {item.get("name") for item in plugins if isinstance(item, dict)}
    extra_claude = set(claude_by_name) - agent_names
    for name in sorted(extra_claude):
        errors.append(f"claude marketplace contains plugin absent from agent marketplace: {name}")

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
