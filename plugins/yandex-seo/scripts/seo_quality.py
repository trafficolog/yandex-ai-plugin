from __future__ import annotations


def capability_mode(coverage: dict) -> str:
    have = {key for key, value in coverage.items() if value}
    if {"wordstat", "search", "webmaster", "metrika"} <= have:
        return "FULL"
    if have == {"wordstat", "search"}:
        return "DISCOVERY"
    if have == {"search", "webmaster"}:
        return "VISIBILITY"
    if have == {"webmaster", "metrika"}:
        return "PERFORMANCE"
    return "PARTIAL"


def propagate_limitations(source_records: list[dict]) -> list[dict]:
    limitations: list[dict] = []
    for record in source_records:
        source = record.get("source")
        if source == "yandex-metrika":
            if "quality" not in record or not isinstance(record.get("quality"), dict):
                limitations.append({"kind": "QUALITY_METADATA_MISSING", "source": source})
            else:
                quality = record["quality"]
                if quality.get("sampled"):
                    limitations.append({
                        "kind": "METRIKA_SAMPLING",
                        "source": source,
                        "sample_share": quality.get("sample_share"),
                    })
                if quality.get("data_lag") not in (None, 0):
                    limitations.append({
                        "kind": "METRIKA_DATA_LAG",
                        "source": source,
                        "data_lag": quality.get("data_lag"),
                    })
        if source == "yandex-webmaster":
            coverage = record.get("coverage") or {}
            if coverage.get("top_n"):
                limitations.append({"kind": "WEBMASTER_TOP_N", "source": source, "top_n": coverage["top_n"]})
        if source == "yandex-search":
            cluster = record.get("cluster") or {}
            if cluster.get("bridge_risk"):
                limitations.append({
                    "kind": "SEARCH_BRIDGE_RISK",
                    "source": source,
                    "cluster_id": cluster.get("cluster_id"),
                })
        for limitation in record.get("limitations") or []:
            limitations.append({"kind": "SOURCE_LIMITATION", "source": source, "detail": limitation})

    unique: list[dict] = []
    seen: set[str] = set()
    for item in limitations:
        key = repr(sorted(item.items()))
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique
