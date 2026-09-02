from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

FORBIDDEN_AGGREGATE_LABELS = {
    "total demand",
    "market size",
    "unique searches",
    "суммарный спрос",
    "размер рынка",
    "уникальные запросы",
}


def assert_no_fake_total_demand(label: str) -> None:
    normalized = " ".join(label.lower().split())
    if any(term in normalized for term in FORBIDDEN_AGGREGATE_LABELS):
        raise ValueError(
            "Overlapping Wordstat phrase counts must not be labeled as total demand, market size, or unique searches"
        )


def merge_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for row in records:
        phrase = str(row.get("phrase", "")).strip()
        if not phrase:
            continue
        count = int(row.get("count", 0))
        relation = row.get("relation")
        sources = row.get("sources") or []
        expression = row.get("operator_expression")
        item = merged.setdefault(
            phrase,
            {
                "phrase": phrase,
                "count": count,
                "relations": set(),
                "sources": set(),
                "operator_expressions": set(),
            },
        )
        item["count"] = max(item["count"], count)
        if relation:
            item["relations"].add(str(relation))
        item["sources"].update(str(source) for source in sources if str(source).strip())
        if expression:
            item["operator_expressions"].add(str(expression))

    result: list[dict[str, Any]] = []
    for item in merged.values():
        result.append(
            {
                "phrase": item["phrase"],
                "count": item["count"],
                "relations": sorted(item["relations"]),
                "sources": sorted(item["sources"]),
                "operator_expressions": sorted(item["operator_expressions"]),
            }
        )
    return sorted(result, key=lambda item: (-item["count"], item["phrase"]))


def build_dataset(
    seed_results: list[dict[str, Any]],
    *,
    backend: str = "yandex-cloud-wordstat-v2",
) -> dict[str, Any]:
    all_records: list[dict[str, Any]] = []
    total_counts: dict[str, int] = {}
    for seed_result in seed_results:
        seed = str(seed_result.get("seed", "")).strip()
        if not seed:
            raise ValueError("Each seed result must include seed")
        total_counts[seed] = int(seed_result.get("total_count", 0))
        all_records.extend(seed_result.get("records") or [])
    phrases = merge_records(all_records)
    return {
        "total_counts": total_counts,
        "phrases": phrases,
        "meta": {
            "backend": backend,
            "window": "trailing-30-days-for-top",
            "unique_phrases": len(phrases),
            "seed_count": len(seed_results),
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "overlapping_counts": True,
        },
    }
