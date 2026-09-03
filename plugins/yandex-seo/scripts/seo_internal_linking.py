from __future__ import annotations

from copy import deepcopy
from typing import Any

from .seo_topical_architecture import (
    CLAIM_CLASSES,
    CONFIDENCE_LEVELS,
    REASON_CODES,
    SEARCH_REASON_CODES,
    SEMANTIC_RELATIONS,
    SCHEMA as ARCHITECTURE_SCHEMA,
)


NON_EMPIRICAL_REASON_CODES = {"METHODOLOGY_HEURISTIC", "SEMANTIC_HYPOTHESIS"}
EMPIRICAL_CLAIM_CLASSES = {"OBSERVED", "DERIVED"}


def _require_architecture(architecture: dict[str, Any]) -> tuple[list[dict[str, Any]], set[str]]:
    if not isinstance(architecture, dict) or architecture.get("schema") != ARCHITECTURE_SCHEMA:
        raise ValueError(f"architecture must use schema {ARCHITECTURE_SCHEMA}")
    tree = architecture.get("structural_tree")
    if not isinstance(tree, dict) or not isinstance(tree.get("nodes"), list):
        raise ValueError("architecture.structural_tree.nodes is required")
    nodes = tree["nodes"]
    page_ids: set[str] = set()
    for node in nodes:
        page_id = node.get("page_id")
        if not isinstance(page_id, str) or not page_id:
            raise ValueError("every structural node requires page_id")
        if page_id in page_ids:
            raise ValueError(f"duplicate page_id in architecture: {page_id}")
        page_ids.add(page_id)
    return nodes, page_ids


def _normalize_candidate_link(
    raw: dict[str, Any],
    page_ids: set[str],
    *,
    search_missing: bool = False,
) -> dict[str, Any]:
    source = raw.get("from_page_id")
    target = raw.get("to_page_id")
    if source not in page_ids or target not in page_ids:
        raise ValueError("candidate link references unknown page")
    if source == target:
        raise ValueError("candidate link source and target must differ")
    relation = raw.get("relation")
    if relation not in SEMANTIC_RELATIONS:
        raise ValueError(f"relation must be one of {sorted(SEMANTIC_RELATIONS)}")
    user_need = raw.get("user_need")
    if not isinstance(user_need, str) or not user_need.strip():
        raise ValueError("candidate link requires a non-empty user_need")
    reason_codes = raw.get("reason_codes")
    if (
        not isinstance(reason_codes, list)
        or not reason_codes
        or any(not isinstance(code, str) or not code.strip() for code in reason_codes)
    ):
        raise ValueError("candidate link requires at least one non-empty reason_code")
    normalized_reason_codes = [code.strip() for code in reason_codes]
    unknown_reason_codes = sorted(set(normalized_reason_codes) - REASON_CODES)
    if unknown_reason_codes:
        raise ValueError(f"unknown reason codes: {unknown_reason_codes}")
    if search_missing and set(normalized_reason_codes) & SEARCH_REASON_CODES:
        raise ValueError("Search-owned link reasons require Search coverage")
    confidence = raw.get("confidence")
    if confidence not in CONFIDENCE_LEVELS:
        raise ValueError(f"confidence must be one of {sorted(CONFIDENCE_LEVELS)}")
    claim_class = raw.get("claim_class")
    if claim_class not in CLAIM_CLASSES:
        raise ValueError(f"claim_class must be one of {sorted(CLAIM_CLASSES)}")
    if (
        set(normalized_reason_codes).issubset(NON_EMPIRICAL_REASON_CODES)
        and claim_class in EMPIRICAL_CLAIM_CLASSES
    ):
        raise ValueError("methodology/hypothesis-only link reasons cannot use an empirical claim_class")
    if raw.get("exact_match_required") is True:
        raise ValueError("forced exact-match anchor requirements are not supported")
    evidence = raw.get("evidence", [])
    if not isinstance(evidence, list):
        raise ValueError("candidate link evidence must be a list")

    item = {
        "from_page_id": source,
        "to_page_id": target,
        "relation": relation,
        "user_need": user_need.strip(),
        "reason_codes": normalized_reason_codes,
        "evidence": deepcopy(evidence),
        "confidence": confidence,
        "claim_class": claim_class,
        "status": "PREVIEW",
    }
    if raw.get("anchor_concept") is not None:
        anchor = raw["anchor_concept"]
        if not isinstance(anchor, str) or not anchor.strip():
            raise ValueError("anchor_concept must be a non-empty string when supplied")
        item["anchor_concept"] = anchor.strip()
    if raw.get("placement") is not None:
        placement = raw["placement"]
        if not isinstance(placement, str) or not placement.strip():
            raise ValueError("placement must be a non-empty string when supplied")
        item["placement"] = placement.strip()
    return item


def build_link_plan(
    *,
    architecture: dict[str, Any],
    candidate_links: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Validate candidate internal links and return preview-only records."""

    _, page_ids = _require_architecture(architecture)
    if not isinstance(candidate_links, list):
        raise ValueError("candidate_links must be a list")
    coverage = architecture.get("coverage")
    search_missing = isinstance(coverage, dict) and coverage.get("search") == "MISSING"
    return [
        _normalize_candidate_link(raw, page_ids, search_missing=search_missing)
        for raw in candidate_links
    ]


def audit_link_inventory(
    *,
    architecture: dict[str, Any],
    existing_links: list[dict[str, Any]],
) -> dict[str, Any]:
    """Compare supplied link inventory with structural and semantic contracts.

    Directed semantic cycles are intentionally allowed. A cycle is reported only
    by a higher-level UX/navigation analysis if it causes a concrete problem.
    """

    nodes, page_ids = _require_architecture(architecture)
    if not isinstance(existing_links, list):
        raise ValueError("existing_links must be a list")

    findings: list[dict[str, Any]] = []
    valid_links: set[tuple[str, str]] = set()
    connected_pages: set[str] = set()

    for index, raw in enumerate(existing_links):
        source = raw.get("from_page_id")
        target = raw.get("to_page_id")
        if source not in page_ids or target not in page_ids:
            findings.append(
                {
                    "type": "UNKNOWN_LINK_ENDPOINT",
                    "link_index": index,
                    "from_page_id": source,
                    "to_page_id": target,
                }
            )
            continue
        valid_links.add((source, target))
        connected_pages.update((source, target))

    structural_links = {
        (node["canonical_parent_id"], node["page_id"])
        for node in nodes
        if node.get("canonical_parent_id") is not None
    }
    semantic_graph = architecture.get("semantic_graph", {})
    semantic_links = {
        (edge.get("from_page_id"), edge.get("to_page_id"))
        for edge in semantic_graph.get("edges", [])
        if edge.get("from_page_id") in page_ids and edge.get("to_page_id") in page_ids
    }
    justified_links = structural_links | semantic_links

    for source, target in sorted(valid_links):
        if (source, target) not in justified_links:
            findings.append(
                {
                    "type": "UNJUSTIFIED_LINK",
                    "from_page_id": source,
                    "to_page_id": target,
                }
            )

    for node in nodes:
        page_id = node["page_id"]
        if page_id not in connected_pages and node.get("canonical_parent_id") is not None:
            findings.append({"type": "ORPHAN_PAGE", "page_id": page_id})

        parent = node.get("canonical_parent_id")
        if parent is not None and (parent, page_id) not in valid_links:
            findings.append(
                {
                    "type": "STRUCTURAL_PARENT_LINK_MISSING",
                    "parent_page_id": parent,
                    "child_page_id": page_id,
                }
            )

    for edge in semantic_graph.get("edges", []):
        source = edge.get("from_page_id")
        target = edge.get("to_page_id")
        if source in page_ids and target in page_ids and (source, target) not in valid_links:
            findings.append(
                {
                    "type": "MISSING_JUSTIFIED_LINK",
                    "from_page_id": source,
                    "to_page_id": target,
                    "relation": edge.get("relation"),
                    "claim_class": edge.get("claim_class"),
                    "confidence": edge.get("confidence"),
                }
            )

    return {
        "schema": "seo-internal-link-audit/v1",
        "known_pages": sorted(page_ids),
        "observed_link_count": len(valid_links),
        "findings": findings,
    }
