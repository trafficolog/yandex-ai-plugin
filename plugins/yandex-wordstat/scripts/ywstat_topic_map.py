from __future__ import annotations

from copy import deepcopy
from typing import Any, Iterable


SCHEMA = "wordstat-topic-map/v1"
CONFIDENCE_LEVELS = {"LOW", "MEDIUM", "HIGH"}
TOPIC_RELATIONS = {"RELATED", "NARROWER", "BROADER", "COMPLEMENTARY"}
ASSOCIATION_CAP_LIMITATION = "WORDSTAT_ASSOCIATIONS_CAPPED"


def _normalize_text(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("query text must be a non-empty string")
    return " ".join(value.split()).casefold()


def _unique(values: Iterable[Any]) -> list[Any]:
    result: list[Any] = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def _validate_confidence(value: str) -> str:
    if value not in CONFIDENCE_LEVELS:
        raise ValueError(f"confidence must be one of {sorted(CONFIDENCE_LEVELS)}")
    return value


def build_topic_map(
    *,
    seeds: list[dict[str, Any]],
    phrase_records: list[dict[str, Any]],
    candidate_topics: list[dict[str, Any]],
    candidate_relations: list[dict[str, Any]] | None = None,
    scope: dict[str, Any] | None = None,
    limitations: list[str] | None = None,
) -> dict[str, Any]:
    """Build a deterministic, candidate-only Wordstat topic-map artifact.

    The helper validates and normalizes evidence supplied by the caller. It does
    not infer SEO page boundaries or perform fuzzy/LLM clustering.
    """

    if not isinstance(seeds, list) or not seeds:
        raise ValueError("seeds must be a non-empty list")
    if not isinstance(phrase_records, list):
        raise ValueError("phrase_records must be a list")
    if not isinstance(candidate_topics, list):
        raise ValueError("candidate_topics must be a list")

    normalized_queries: dict[str, dict[str, Any]] = {}
    query_aliases: dict[str, str] = {}
    query_id_keys: dict[str, str] = {}

    for record in phrase_records:
        query_id = record.get("query_id")
        text = record.get("text")
        source_seed = record.get("source_seed")
        relation = record.get("relation")
        if not isinstance(query_id, str) or not query_id:
            raise ValueError("every phrase record requires query_id")
        if not isinstance(source_seed, str) or not source_seed:
            raise ValueError("every phrase record requires source_seed")
        if not isinstance(relation, str) or not relation:
            raise ValueError("every phrase record requires relation")

        key = _normalize_text(text)
        previous_key = query_id_keys.get(query_id)
        if previous_key is not None and previous_key != key:
            raise ValueError(f"query_id {query_id!r} resolves to multiple normalized queries")
        query_id_keys[query_id] = key

        if key not in normalized_queries:
            normalized_queries[key] = {
                "query_id": query_id,
                "query_ids": [query_id],
                "text": " ".join(text.split()),
                "source_seeds": [],
                "relations": [],
                "demand_observations": [],
                "regions": [],
                "dynamics": None,
            }
        query = normalized_queries[key]
        query["query_ids"] = _unique([*query["query_ids"], query_id])
        query_aliases[query_id] = query["query_id"]
        query["source_seeds"] = _unique([*query["source_seeds"], source_seed])
        query["relations"] = _unique([*query["relations"], relation])
        if record.get("demand") is not None:
            query["demand_observations"].append(deepcopy(record["demand"]))
        if record.get("regions"):
            query["regions"] = _unique([*query["regions"], *deepcopy(record["regions"])])
        if record.get("dynamics") is not None:
            if query["dynamics"] is None:
                query["dynamics"] = []
            query["dynamics"].append(deepcopy(record["dynamics"]))

    topic_ids: set[str] = set()
    normalized_topics: list[dict[str, Any]] = []
    for topic in candidate_topics:
        topic_id = topic.get("topic_id")
        label = topic.get("label")
        if not isinstance(topic_id, str) or not topic_id:
            raise ValueError("candidate topic requires topic_id")
        if topic_id in topic_ids:
            raise ValueError(f"duplicate topic_id: {topic_id}")
        if not isinstance(label, str) or not label.strip():
            raise ValueError("candidate topic requires label")

        resolved_query_ids: list[str] = []
        for query_id in topic.get("query_ids", []):
            if query_id not in query_aliases:
                raise ValueError(f"unknown query_id in candidate topic: {query_id}")
            canonical_id = query_aliases[query_id]
            if canonical_id not in resolved_query_ids:
                resolved_query_ids.append(canonical_id)

        confidence = _validate_confidence(topic.get("confidence"))
        normalized_topics.append(
            {
                "topic_id": topic_id,
                "label": label.strip(),
                "query_ids": resolved_query_ids,
                "candidate_intents": deepcopy(topic.get("candidate_intents", [])),
                "reasons": deepcopy(topic.get("reasons", [])),
                "confidence": confidence,
                "status": "CANDIDATE",
            }
        )
        topic_ids.add(topic_id)

    normalized_relations: list[dict[str, Any]] = []
    for relation in candidate_relations or []:
        source = relation.get("from_topic_id")
        target = relation.get("to_topic_id")
        relation_type = relation.get("relation")
        if source not in topic_ids or target not in topic_ids:
            raise ValueError("candidate relation references unknown topic")
        if relation_type not in TOPIC_RELATIONS:
            raise ValueError(f"candidate relation must be one of {sorted(TOPIC_RELATIONS)}")
        normalized_relations.append(
            {
                "from_topic_id": source,
                "to_topic_id": target,
                "relation": relation_type,
                "evidence": deepcopy(relation.get("evidence", [])),
                "status": "HYPOTHESIS",
            }
        )

    output_limitations = _unique(limitations or [])
    if any(bool(seed.get("coverage", {}).get("associations_truncated")) for seed in seeds):
        output_limitations = _unique([*output_limitations, ASSOCIATION_CAP_LIMITATION])

    return {
        "schema": SCHEMA,
        "scope": deepcopy(scope or {}),
        "seeds": deepcopy(seeds),
        "queries": list(normalized_queries.values()),
        "candidate_topics": normalized_topics,
        "candidate_relations": normalized_relations,
        "limitations": output_limitations,
    }
