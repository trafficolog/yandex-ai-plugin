#!/usr/bin/env python3
from pathlib import Path

try:
    from .validate_repo import validate_repository
except ImportError:
    from validate_repo import validate_repository


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors = validate_repository(root, strict_reference_freshness=True)
    freshness_errors = [error for error in errors if "reference verification error" in error]
    if freshness_errors:
        for error in freshness_errors:
            print(error)
        return 1
    print("All freshness-controlled references are current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
