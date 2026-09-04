from __future__ import annotations

from pathlib import Path
import re


def _read(path: Path, errors: list[str]) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(f"version mention file missing: {path}")
    except UnicodeDecodeError:
        errors.append(f"version mention file is not UTF-8: {path}")
    return None


def _service_label(plugin_dir: str) -> str:
    suffix = plugin_dir.removeprefix("yandex-")
    label = "SEO" if suffix == "seo" else suffix.replace("-", " ").title()
    return f"Yandex {label}"


def _table_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def validate_plugin_version_mentions(
    root: Path,
    plugin_path: Path,
    version: str,
    errors: list[str],
) -> None:
    plugin_dir = plugin_path.name
    escaped_version = re.escape(version)

    for filename in ("README.md", "README.en.md"):
        path = plugin_path / filename
        text = _read(path, errors)
        if text is None:
            continue
        if re.search(
            rf"(?m)^(?:Версия|Version)\s+`?{escaped_version}`?(?:[.\s]|$)",
            text,
        ) is None:
            errors.append(f"version mention {version} missing or stale in {path}")

    for filename in ("CHANGELOG.md", "CHANGELOG.en.md"):
        path = plugin_path / filename
        text = _read(path, errors)
        if text is None:
            continue
        if re.search(
            rf"^##\s+(?:\[)?{escaped_version}(?:\])?(?:\s|—|$)",
            text,
            re.MULTILINE,
        ) is None:
            errors.append(f"version mention {version} missing or stale in {path}")

    plugin_marker = f"plugins/{plugin_dir}/"
    for filename in ("README.md", "README.en.md"):
        path = root / filename
        text = _read(path, errors)
        if text is None:
            continue
        matching_rows = [line for line in text.splitlines() if plugin_marker in line]
        row_ok = False
        for line in matching_rows:
            cells = _table_cells(line)
            if len(cells) >= 2 and cells[1] == version:
                row_ok = True
                break
        if not row_ok:
            errors.append(f"version mention {version} missing or stale in {path} table for {plugin_dir}")

        if "## Версии" in text or "## Versions" in text:
            version_line = re.compile(
                rf"(?m)^\s*{re.escape(plugin_dir)}\s+{escaped_version}\s*$"
            )
            if version_line.search(text) is None:
                errors.append(
                    f"version mention {version} missing or stale in {path} versions block for {plugin_dir}"
                )

    service_label = _service_label(plugin_dir)
    for filename in ("SERVICE_MATRIX.md", "SERVICE_MATRIX.en.md"):
        path = root / "docs" / filename
        text = _read(path, errors)
        if text is None:
            continue
        # Minimal synthetic repository fixtures predate the service table. Once the
        # canonical table exists, every marketplace plugin row is strict.
        if "| Service plugin |" not in text:
            continue
        matching = [
            _table_cells(line)
            for line in text.splitlines()
            if _table_cells(line) and _table_cells(line)[0] == service_label
        ]
        if len(matching) != 1 or len(matching[0]) < 4 or matching[0][3] != version:
            errors.append(
                f"version mention {version} missing or stale in {path} row for {service_label}"
            )
