from __future__ import annotations

from copy import deepcopy
from typing import Any


SCHEMA = "seo-topical-architecture/v1"
MODES = {"GREENFIELD", "EXISTING_SITE"}
COVERAGE_STATES = {"COMPLETE", "PARTIAL", "MISSING"}
COVERAGE_KEYS = {"wordstat", "search", "webmaster", "metrika", "site_inventory"}
PAGE_ROLES = {
    "ROOT",
    "HUB",
    "SUPPORT",
    "DETAIL",
    "COMPARISON",
    "TRANSACTIONAL",
    "DEFINITION",
    "EVIDENCE",
    "BRIDGE",
    "UTILITY",
    "OTHER",
}
ROOT_PAGE_ROLES = {"ROOT", "BRIDGE"}
STRUCTURAL_NODE_FIELDS = {
    "page_id",
    "url",
    "proposed_url",
    "title",
    "page_role",
    "canonical_parent_id",
    "breadcrumbs",
    "cluster_ids",
    "evidence",
    "confidence",
}
PAGE_DECISIONS = {
    "PRESERVE",
    "CREATE",
    "EXPAND",
    "MERGE",
    "SPLIT",
    "REDIRECT",
    "SECTION_ONLY",
    "BRIDGE",
    "NO_PAGE",
    "MANUAL_REVIEW",
}
PAGE_DECISION_OPTIONAL_FIELDS = {
    "reason_codes",
    "target_page_id",
    "target_url",
    "notes",
    "methodology_source",
    "limitations",
}
SEARCH_REQUIRED_BOUNDARY_DECISIONS = {
    "CREATE",
    "MERGE",
    "SPLIT",
    "REDIRECT",
    "SECTION_ONLY",
    "BRIDGE",
    "NO_PAGE",
}
CLAIM_CLASSES = {"OBSERVED", "DERIVED", "HYPOTHESIS", "METHODOLOGY"}
CONFIDENCE_LEVELS = {"LOW", "MEDIUM", "HIGH"}
SEMANTIC_RELATIONS = {
    "PARENT_CONTEXT",
    "CHILD_DETAIL",
    "SIBLING",
    "SUPPORT",
    "DEFINITION",
    "COMPARISON",
    "ALTERNATIVE",
    "EVIDENCE",
    "USE_CASE",
    "NEXT_STEP",
    "TRANSACTIONAL_PATH",
    "BRIDGE",
    "COMPLIANCE",
}
REASON_CODES = {
    "SERP_OVERLAP",
    "SERP_BRIDGE_RISK",
    "WORDSTAT_NESTED_RELATION",
    "WORDSTAT_ASSOCIATION",
    "WORDSTAT_DEMAND_CONTEXT",
    "WORDSTAT_REGION_CONTEXT",
    "WORDSTAT_SEASONAL_CONTEXT",
    "WEBMASTER_QUERY_VISIBILITY",
    "WEBMASTER_EXISTING_URL",
    "METRIKA_LANDING_TRAFFIC",
    "METRIKA_CONVERSION_CONTEXT",
    "EXISTING_INTERNAL_LINK",
    "EXISTING_BREADCRUMB",
    "USER_BUSINESS_CONSTRAINT",
    "MANUAL_ENTITY_RELATION",
    "SEMANTIC_HYPOTHESIS",
    "METHODOLOGY_HEURISTIC",
}
SEARCH_REASON_CODES = {"SERP_OVERLAP", "SERP_BRIDGE_RISK"}
NON_EMPIRICAL_REASON_CODES = {"METHODOLOGY_HEURISTIC", "SEMANTIC_HYPOTHESIS"}
EMPIRICAL_CLAIM_CLASSES = {"OBSERVED", "DERIVED"}
SERP_VALIDATION_MISSING = "SERP_VALIDATION_MISSING"


def _unique(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def _require_nonempty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def _validate_confidence(value: Any) -> str:
    if value not in CONFIDENCE_LEVELS:
        raise ValueError(f"confidence must be one of {sorted(CONFIDENCE_LEVELS)}")
    return value


def _validate_claim_class(value: Any) -> str:
    if value not in CLAIM_CLASSES:
        raise ValueError(f"claim_class must be one of {sorted(CLAIM_CLASSES)}")
    return value


def _normalize_reason_codes(value: Any, field: str = "reason_codes") -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{field} must be a list")
    normalized: list[str] = []
    for raw_code in value:
        code = _require_nonempty_string(raw_code, f"{field}[]")
        if code not in REASON_CODES:
            raise ValueError(f"unknown reason code: {code}")
        if code not in normalized:
            normalized.append(code)
    return normalized


def _validate_coverage(coverage: dict[str, Any]) -> dict[str, str]:
    if not isinstance(coverage, dict):
        raise ValueError("coverage must be an object")
    missing_keys = COVERAGE_KEYS - set(coverage)
    if missing_keys:
        raise ValueError(f"coverage is missing keys: {sorted(missing_keys)}")
    normalized: dict[str, str] = {}
    for key in sorted(COVERAGE_KEYS):
        value = coverage[key]
        if value not in COVERAGE_STATES:
            raise ValueError(f"coverage.{key} must be one of {sorted(COVERAGE_STATES)}")
        normalized[key] = value
    return normalized


def _validate_structural_nodes(structural_nodes: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    if not isinstance(structural_nodes, list):
        raise ValueError("structural_nodes must be a list")

    by_id: dict[str, dict[str, Any]] = {}
    seen_locations: dict[str, str] = {}
    normalized: list[dict[str, Any]] = []
    breadcrumbs_supplied: set[str] = set()

    for raw in structural_nodes:
        page_id = _require_nonempty_string(raw.get("page_id"), "page_id")
        if page_id in by_id:
            raise ValueError(f"duplicate page_id: {page_id}")

        node = {
            key: deepcopy(raw[key])
            for key in STRUCTURAL_NODE_FIELDS
            if key in raw
        }
        node["page_id"] = page_id
        node["confidence"] = _validate_confidence(raw.get("confidence"))
        node.setdefault("canonical_parent_id", None)
        if "breadcrumbs" in raw:
            breadcrumbs_supplied.add(page_id)
        node.setdefault("breadcrumbs", [])
        node.setdefault("cluster_ids", [])
        node.setdefault("evidence", [])

        if node.get("page_role") is not None:
            page_role = _require_nonempty_string(node.get("page_role"), "page_role")
            if page_role not in PAGE_ROLES:
                raise ValueError(f"page_role must be one of {sorted(PAGE_ROLES)}")
            node["page_role"] = page_role

        for field in ("url", "proposed_url"):
            location = node.get(field)
            if location is None:
                continue
            location = _require_nonempty_string(location, field)
            node[field] = location
            if location in seen_locations:
                raise ValueError(
                    f"duplicate page location {location!r} for {page_id} and {seen_locations[location]}"
                )
            seen_locations[location] = page_id

        by_id[page_id] = node
        normalized.append(node)

    for node in normalized:
        parent = node.get("canonical_parent_id")
        if parent is None:
            if node.get("proposed_url") is not None and node.get("page_role") not in ROOT_PAGE_ROLES:
                raise ValueError("parentless proposed page requires page_role ROOT or BRIDGE")
            continue
        parent = _require_nonempty_string(parent, "canonical_parent_id")
        node["canonical_parent_id"] = parent
        if parent not in by_id:
            raise ValueError(f"unknown canonical parent {parent!r} for {node['page_id']}")
        if parent == node["page_id"]:
            raise ValueError("a page cannot be its own canonical parent")

    state: dict[str, int] = {}

    def visit(page_id: str) -> None:
        marker = state.get(page_id, 0)
        if marker == 1:
            raise ValueError("structural tree contains a cycle")
        if marker == 2:
            return
        state[page_id] = 1
        parent = by_id[page_id].get("canonical_parent_id")
        if parent is not None:
            visit(parent)
        state[page_id] = 2

    for page_id in by_id:
        visit(page_id)

    for page_id in breadcrumbs_supplied:
        breadcrumbs = by_id[page_id].get("breadcrumbs")
        if not isinstance(breadcrumbs, list):
            raise ValueError("breadcrumbs must be a list when supplied")
        normalized_breadcrumbs: list[str] = []
        for breadcrumb_id in breadcrumbs:
            normalized_id = _require_nonempty_string(breadcrumb_id, "breadcrumbs[]")
            if normalized_id not in by_id:
                raise ValueError(f"unknown breadcrumb page: {normalized_id}")
            normalized_breadcrumbs.append(normalized_id)

        ancestors: list[str] = []
        parent = by_id[page_id].get("canonical_parent_id")
        while parent is not None:
            ancestors.append(parent)
            parent = by_id[parent].get("canonical_parent_id")
        expected = list(reversed(ancestors))
        if normalized_breadcrumbs != expected:
            raise ValueError("breadcrumbs must match canonical parent chain")
        by_id[page_id]["breadcrumbs"] = normalized_breadcrumbs

    return normalized, by_id


def _normalize_page_decisions(
    page_decisions: list[dict[str, Any]],
    page_index: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    if not isinstance(page_decisions, list):
        raise ValueError("page_decisions must be a list")
    known_pages = set(page_index)
    location_owners: dict[str, str] = {}
    for known_page_id, node in page_index.items():
        for location in (node.get("url"), node.get("proposed_url")):
            if location is not None:
                location_owners[location] = known_page_id
    decided_pages: set[str] = set()
    result: list[dict[str, Any]] = []
    for raw in page_decisions:
        page_id = _require_nonempty_string(raw.get("page_id"), "page_decision.page_id")
        if page_id not in known_pages:
            raise ValueError(f"page decision references unknown page: {page_id}")
        if page_id in decided_pages:
            raise ValueError(f"duplicate page decision for page: {page_id}")
        decided_pages.add(page_id)
        decision = raw.get("decision")
        if decision not in PAGE_DECISIONS:
            raise ValueError(f"decision must be one of {sorted(PAGE_DECISIONS)}")
        claim_class = _validate_claim_class(raw.get("claim_class"))
        evidence = raw.get("evidence", [])
        if not isinstance(evidence, list):
            raise ValueError("page_decision.evidence must be a list")
        evidence = deepcopy(evidence)
        reason_codes: list[str] = []

        item = {
            "page_id": page_id,
            "decision": decision,
            "cluster_ids": deepcopy(raw.get("cluster_ids", [])),
            "evidence": evidence,
            "confidence": _validate_confidence(raw.get("confidence")),
            "claim_class": claim_class,
            "status": "PREVIEW",
        }

        if "reason_codes" in raw:
            reason_codes = _normalize_reason_codes(
                raw.get("reason_codes"), "page_decision.reason_codes"
            )
            if (
                reason_codes
                and set(reason_codes).issubset(NON_EMPIRICAL_REASON_CODES)
                and claim_class in EMPIRICAL_CLAIM_CLASSES
            ):
                raise ValueError(
                    "methodology/hypothesis-only page decision reasons cannot use an empirical claim_class"
                )
            item["reason_codes"] = reason_codes

        if claim_class in EMPIRICAL_CLAIM_CLASSES and not reason_codes and not evidence:
            raise ValueError("empirical page decisions require reason_codes or evidence provenance")

        if "target_page_id" in raw:
            target_page_id = _require_nonempty_string(
                raw.get("target_page_id"), "page_decision.target_page_id"
            )
            if target_page_id not in known_pages:
                raise ValueError(f"page decision references unknown target page: {target_page_id}")
            if decision in {"MERGE", "REDIRECT"} and target_page_id == page_id:
                raise ValueError(f"{decision} target_page_id must differ from page_id")
            item["target_page_id"] = target_page_id

        if "target_url" in raw:
            target_url = _require_nonempty_string(
                raw.get("target_url"), "page_decision.target_url"
            )
            source_node = page_index[page_id]
            source_locations = {
                location
                for location in (source_node.get("url"), source_node.get("proposed_url"))
                if location is not None
            }
            if decision in {"MERGE", "REDIRECT"} and target_url in source_locations:
                raise ValueError(f"{decision} target_url must differ from the source page location")
            if "target_page_id" in item:
                target_url_owner = location_owners.get(target_url)
                if target_url_owner is not None and target_url_owner != item["target_page_id"]:
                    raise ValueError(
                        "target_page_id and target_url must resolve to the same known page"
                    )
            item["target_url"] = target_url

        for field in PAGE_DECISION_OPTIONAL_FIELDS - {"reason_codes", "target_page_id", "target_url"}:
            if field in raw:
                item[field] = deepcopy(raw[field])
        result.append(item)

    destructive_targets: dict[str, str] = {}
    for item in result:
        if item["decision"] not in {"MERGE", "REDIRECT"}:
            continue
        target_page_id = item.get("target_page_id")
        if target_page_id is None and item.get("target_url") is not None:
            target_page_id = location_owners.get(item["target_url"])
        if target_page_id is not None:
            destructive_targets[item["page_id"]] = target_page_id

    destructive_state: dict[str, int] = {}

    def visit_destructive(page_id: str) -> None:
        marker = destructive_state.get(page_id, 0)
        if marker == 1:
            raise ValueError("destructive page decisions contain a target cycle")
        if marker == 2:
            return
        destructive_state[page_id] = 1
        target_page_id = destructive_targets.get(page_id)
        if target_page_id in destructive_targets:
            visit_destructive(target_page_id)
        destructive_state[page_id] = 2

    for page_id in destructive_targets:
        visit_destructive(page_id)

    return result


def _normalize_semantic_edges(
    semantic_edges: list[dict[str, Any]],
    known_pages: set[str],
) -> list[dict[str, Any]]:
    if not isinstance(semantic_edges, list):
        raise ValueError("semantic_edges must be a list")
    result: list[dict[str, Any]] = []
    for raw in semantic_edges:
        source = _require_nonempty_string(raw.get("from_page_id"), "from_page_id")
        target = _require_nonempty_string(raw.get("to_page_id"), "to_page_id")
        if source not in known_pages or target not in known_pages:
            raise ValueError("semantic edge references unknown page")
        if source == target:
            raise ValueError("semantic edge source and target must differ")
        relation = raw.get("relation")
        if relation not in SEMANTIC_RELATIONS:
            raise ValueError(f"semantic relation must be one of {sorted(SEMANTIC_RELATIONS)}")
        item = deepcopy(raw)
        item["from_page_id"] = source
        item["to_page_id"] = target
        item["relation"] = relation
        item["user_need"] = _require_nonempty_string(raw.get("user_need"), "user_need")
        item["confidence"] = _validate_confidence(raw.get("confidence"))
        item["claim_class"] = _validate_claim_class(raw.get("claim_class"))
        reason_codes = _normalize_reason_codes(raw.get("reason_codes"))
        if not reason_codes:
            raise ValueError("semantic edge requires at least one reason code")
        item["reason_codes"] = reason_codes
        item.setdefault("evidence", [])
        if (
            set(item["reason_codes"]).issubset(NON_EMPIRICAL_REASON_CODES)
            and item["claim_class"] in EMPIRICAL_CLAIM_CLASSES
        ):
            raise ValueError("methodology/hypothesis-only semantic reasons cannot use an empirical claim_class")
        result.append(item)
    return result


def _normalize_fact_sets(
    fact_sets: list[dict[str, Any]] | None,
    known_pages: set[str],
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for raw in fact_sets or []:
        fact_set_id = _require_nonempty_string(raw.get("fact_set_id"), "fact_set_id")
        if fact_set_id in seen_ids:
            raise ValueError(f"duplicate fact_set_id: {fact_set_id}")
        canonical_page_id = _require_nonempty_string(raw.get("canonical_page_id"), "canonical_page_id")
        if canonical_page_id not in known_pages:
            raise ValueError("fact set canonical owner references unknown page")
        consumers = list(raw.get("consumers", []))
        if any(page_id not in known_pages for page_id in consumers):
            raise ValueError("fact set consumer references unknown page")
        item = deepcopy(raw)
        item["fact_set_id"] = fact_set_id
        item["canonical_page_id"] = canonical_page_id
        item["consumers"] = consumers
        item.setdefault("dimensions", [])
        item.setdefault("verification_required", True)
        result.append(item)
        seen_ids.add(fact_set_id)
    return result


def build_topical_architecture(
    *,
    mode: str,
    coverage: dict[str, Any],
    clusters: list[dict[str, Any]],
    page_decisions: list[dict[str, Any]],
    structural_nodes: list[dict[str, Any]],
    semantic_edges: list[dict[str, Any]],
    fact_sets: list[dict[str, Any]] | None = None,
    limitations: list[str] | None = None,
) -> dict[str, Any]:
    """Validate and assemble an evidence-first topical architecture artifact.

    The helper never chooses page boundaries or clustering thresholds. Those
    decisions are supplied by the orchestration layer and checked here.
    """

    if mode not in MODES:
        raise ValueError(f"mode must be one of {sorted(MODES)}")
    if not isinstance(clusters, list):
        raise ValueError("clusters must be a list")

    normalized_coverage = _validate_coverage(coverage)
    nodes, node_index = _validate_structural_nodes(structural_nodes)
    known_pages = set(node_index)
    decisions = _normalize_page_decisions(page_decisions, node_index)
    edges = _normalize_semantic_edges(semantic_edges, known_pages)
    mutable_fact_sets = _normalize_fact_sets(fact_sets, known_pages)

    output_limitations = _unique(list(limitations or []))
    if normalized_coverage["search"] == "MISSING":
        output_limitations = _unique([*output_limitations, SERP_VALIDATION_MISSING])
        if clusters:
            raise ValueError("Search clusters cannot be supplied when Search coverage is missing")
        for decision in decisions:
            if set(decision.get("reason_codes", [])) & SEARCH_REASON_CODES:
                raise ValueError(
                    "Search-owned page decision provenance cannot be supplied when Search coverage is missing"
                )
            if (
                decision["decision"] in SEARCH_REQUIRED_BOUNDARY_DECISIONS
                and decision["claim_class"] != "HYPOTHESIS"
            ):
                raise ValueError(
                    "boundary-changing page decisions must remain HYPOTHESIS when Search evidence is missing"
                )
        for edge in edges:
            if set(edge.get("reason_codes", [])) & SEARCH_REASON_CODES:
                raise ValueError(
                    "Search-owned semantic provenance cannot be supplied when Search coverage is missing"
                )

    structural_edges = [
        {"parent_page_id": node["canonical_parent_id"], "child_page_id": node["page_id"]}
        for node in nodes
        if node.get("canonical_parent_id") is not None
    ]

    return {
        "schema": SCHEMA,
        "mode": mode,
        "coverage": normalized_coverage,
        "clusters": deepcopy(clusters),
        "page_decisions": decisions,
        "structural_tree": {"nodes": nodes, "edges": structural_edges},
        "semantic_graph": {
            "nodes": [{"page_id": page_id} for page_id in node_index],
            "edges": edges,
        },
        "link_plan": [],
        "consistency": {
            "mutable_fact_sets": mutable_fact_sets,
            "navigation_conflicts": [],
            "parity_checks": [],
        },
        "audits": [],
        "limitations": output_limitations,
    }
