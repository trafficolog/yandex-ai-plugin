from __future__ import annotations

import ast
from datetime import date
from pathlib import Path
import re
from typing import Any

MAX_REFERENCE_AGE_DAYS = 90
CONTRACT_STATUSES = {"implemented", "deferred", "infrastructure"}
VERIFIED_PATTERN = re.compile(
    r"(?:\bVerified:\s*|\bverified\s+|\bverified_at:\s*)(\d{4}-\d{2}-\d{2})",
    re.IGNORECASE,
)


def parse_verified_date(text: str) -> date:
    match = VERIFIED_PATTERN.search(text)
    if not match:
        raise ValueError("verification marker missing")
    try:
        return date.fromisoformat(match.group(1))
    except ValueError as exc:
        raise ValueError("verification marker has invalid date") from exc


def validate_reference_freshness(text: str, *, today: date | None = None, enforce_age: bool = True) -> list[str]:
    observed_today = today or date.today()
    try:
        verified = parse_verified_date(text)
    except ValueError as exc:
        return [str(exc)]
    if verified > observed_today:
        return [f"verification date is in the future: {verified.isoformat()}"]
    age = (observed_today - verified).days
    if enforce_age and age > MAX_REFERENCE_AGE_DAYS:
        return [f"reference verification is stale: {verified.isoformat()} is {age} days old (max {MAX_REFERENCE_AGE_DAYS})"]
    return []


def _normalize_repo_path(raw: str) -> str:
    return raw.replace("\\", "/").removeprefix("./")


def _string_list(contract: dict[str, Any], field: str, contract_id: str, errors: list[str]) -> list[str]:
    value = contract.get(field, [])
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        errors.append(f"contract {contract_id} field {field} must be a string list")
        return []
    return value


def _safe_repo_path(root: Path, raw: str, contract_id: str, field: str, errors: list[str]) -> Path | None:
    path = (root / raw).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError:
        errors.append(f"contract {contract_id} {field} path escapes repository root: {raw}")
        return None
    if not path.is_file():
        errors.append(f"contract {contract_id} {field} path does not exist: {raw}")
        return None
    return path


def _parse_test_ref(raw: str) -> tuple[str, str | None, str]:
    parts = raw.split("::")
    if len(parts) == 2 and all(parts):
        path, function = parts
        return path, None, function
    if len(parts) == 3 and all(parts):
        path, class_name, method = parts
        return path, class_name, method
    raise ValueError("test_ref must use path.py::test_function or path.py::TestClass::test_method")


def _decorator_terminal_name(node: ast.expr) -> str | None:
    target = node.func if isinstance(node, ast.Call) else node
    if isinstance(target, ast.Name):
        return target.id
    if isinstance(target, ast.Attribute):
        return target.attr
    return None


def _is_literal_bool(node: ast.expr, expected: bool) -> bool:
    return isinstance(node, ast.Constant) and node.value is expected


def _is_statically_skipped(decorators: list[ast.expr]) -> bool:
    for decorator in decorators:
        name = _decorator_terminal_name(decorator)
        if name == "skip":
            return True
        if not isinstance(decorator, ast.Call) or not decorator.args:
            continue
        if name == "skipIf" and _is_literal_bool(decorator.args[0], True):
            return True
        if name == "skipUnless" and _is_literal_bool(decorator.args[0], False):
            return True
    return False


def _functions_named(nodes: list[ast.stmt], name: str) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    return [
        node
        for node in nodes
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name
    ]


def _validate_test_ref(root: Path, raw: str, contract_id: str, errors: list[str]) -> None:
    try:
        raw_path, class_name, test_name = _parse_test_ref(raw)
    except ValueError as exc:
        errors.append(f"contract {contract_id} invalid test_ref {raw!r}: {exc}")
        return

    if not raw_path.endswith(".py"):
        errors.append(f"contract {contract_id} test_ref path must be a Python file: {raw_path}")
        return
    path = _safe_repo_path(root, raw_path, contract_id, "test_refs", errors)
    if path is None:
        return
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"contract {contract_id} test_ref is unreadable or non-UTF8: {raw_path}: {exc}")
        return
    try:
        tree = ast.parse(source, filename=raw_path)
    except SyntaxError as exc:
        errors.append(f"contract {contract_id} test_ref Python syntax is invalid: {raw_path}: {exc.msg}")
        return

    if not test_name.startswith("test_"):
        errors.append(f"contract {contract_id} test_ref terminal symbol must start with test_: {raw}")
        return

    if class_name is None:
        matches = _functions_named(tree.body, test_name)
        if len(matches) != 1:
            errors.append(
                f"contract {contract_id} test_ref must resolve exactly one top-level function; "
                f"found {len(matches)}: {raw}"
            )
            return
        if _is_statically_skipped(matches[0].decorator_list):
            errors.append(f"contract {contract_id} test_ref target is statically skipped: {raw}")
        return

    classes = [node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == class_name]
    if len(classes) != 1:
        errors.append(
            f"contract {contract_id} test_ref must resolve exactly one class; found {len(classes)}: {raw}"
        )
        return
    class_node = classes[0]
    methods = _functions_named(class_node.body, test_name)
    if len(methods) != 1:
        errors.append(
            f"contract {contract_id} test_ref must resolve exactly one class method; "
            f"found {len(methods)}: {raw}"
        )
        return
    if _is_statically_skipped(class_node.decorator_list) or _is_statically_skipped(methods[0].decorator_list):
        errors.append(f"contract {contract_id} test_ref target is statically skipped: {raw}")


def validate_contract_matrix(root: Path, matrix: Any, *, known_plugins: set[str], today: date | None = None, changed_paths: set[str] | None = None, strict_freshness: bool = False) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    normalized_changed = {_normalize_repo_path(path) for path in (changed_paths or set())}
    if not isinstance(matrix, dict) or matrix.get("version") != 2:
        return ["contract matrix version must be 2"]
    contracts = matrix.get("contracts")
    if not isinstance(contracts, list) or not contracts:
        return ["contract matrix contracts must be a non-empty list"]

    seen_ids: set[str] = set()
    for index, contract in enumerate(contracts):
        if not isinstance(contract, dict):
            errors.append(f"contract matrix entry #{index} must be an object")
            continue
        contract_id = contract.get("id")
        if not isinstance(contract_id, str) or not contract_id:
            errors.append(f"contract matrix entry #{index} missing id")
            contract_id = f"#{index}"
        elif contract_id in seen_ids:
            errors.append(f"duplicate contract id: {contract_id}")
        else:
            seen_ids.add(contract_id)

        status = contract.get("status")
        if status not in CONTRACT_STATUSES:
            errors.append(f"contract {contract_id} has invalid status: {status}")
        plugin = contract.get("plugin")
        if plugin not in known_plugins and plugin != "repository":
            errors.append(f"contract {contract_id} references unknown plugin: {plugin}")

        if "tests" in contract:
            errors.append(f"contract {contract_id} uses forbidden legacy tests field; use test_refs")

        skills = _string_list(contract, "skills", contract_id, errors)
        helpers = _string_list(contract, "helpers", contract_id, errors)
        test_refs = _string_list(contract, "test_refs", contract_id, errors)
        references = _string_list(contract, "references", contract_id, errors)
        freshness_refs = _string_list(contract, "freshness_controlled_references", contract_id, errors)

        if status in {"implemented", "infrastructure"} and not test_refs:
            errors.append(f"{status} contract {contract_id} requires at least one regression test_ref")
        if status == "implemented" and plugin != "repository" and (not skills or not helpers):
            errors.append(f"implemented contract {contract_id} requires SKILL.md and helper traceability")

        resolved: dict[str, Path] = {}
        for field, values in (("skills", skills), ("helpers", helpers), ("references", references)):
            for raw in values:
                path = _safe_repo_path(root, raw, contract_id, field, errors)
                if path is not None:
                    resolved[raw] = path
                if field == "skills" and not raw.endswith("/SKILL.md"):
                    errors.append(f"contract {contract_id} skill path must point to a real SKILL.md: {raw}")

        for raw in test_refs:
            _validate_test_ref(root, raw, contract_id, errors)

        reference_set = set(references)
        for raw in freshness_refs:
            if raw not in reference_set:
                errors.append(f"contract {contract_id} freshness-controlled reference must also appear in references: {raw}")
                continue
            path = resolved.get(raw)
            if path is None:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                errors.append(f"contract {contract_id} reference is not UTF-8: {raw}")
                continue
            enforce_age = strict_freshness or _normalize_repo_path(raw) in normalized_changed
            for error in validate_reference_freshness(text, today=today, enforce_age=enforce_age):
                errors.append(f"contract {contract_id} reference verification error for {raw}: {error}")
    return errors
