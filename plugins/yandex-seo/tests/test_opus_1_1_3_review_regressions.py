import unittest

from scripts import seo_internal_linking, seo_topical_architecture
from scripts.seo_bundle import add_evidence, new_bundle


COVERAGE = {
    "wordstat": "COMPLETE",
    "search": "COMPLETE",
    "webmaster": "COMPLETE",
    "metrika": "MISSING",
    "site_inventory": "COMPLETE",
}

VALID_CONTEXT = {
    "site": "example.com",
    "analysis_period": {"from": "2026-08-01", "to": "2026-08-31"},
    "search_region_id": 213,
    "search_type": "SEARCH_TYPE_RU",
}


def valid_cluster(cluster_id="c1", **overrides):
    cluster = {
        "cluster_id": cluster_id,
        "queries": ["seo audit", "site audit"],
        "min_shared_urls": 2,
        "bridge_risk": False,
        "limitations": [],
    }
    cluster.update(overrides)
    return cluster


def existing_nodes():
    return [
        {
            "page_id": "p1",
            "url": "/legacy/",
            "canonical_parent_id": None,
            "cluster_ids": ["c1"],
            "evidence": ["WEBMASTER_EXISTING_URL"],
            "confidence": "HIGH",
        },
        {
            "page_id": "p2",
            "url": "/target/",
            "canonical_parent_id": None,
            "cluster_ids": ["c1"],
            "evidence": ["WEBMASTER_EXISTING_URL"],
            "confidence": "HIGH",
        },
    ]


class Opus113ReviewRegressionTests(unittest.TestCase):
    def test_legacy_existing_root_without_page_role_remains_orphan_exempt(self):
        architecture = {
            "schema": "seo-topical-architecture/v1",
            "structural_tree": {
                "nodes": [
                    {"page_id": "root", "canonical_parent_id": None},
                    {"page_id": "child", "canonical_parent_id": "root"},
                ],
                "edges": [{"parent_page_id": "root", "child_page_id": "child"}],
            },
            "semantic_graph": {"nodes": [{"page_id": "root"}, {"page_id": "child"}], "edges": []},
        }
        audit = seo_internal_linking.audit_link_inventory(
            architecture=architecture,
            existing_links=[],
        )
        orphan_pages = {
            finding["page_id"]
            for finding in audit["findings"]
            if finding["type"] == "ORPHAN_PAGE"
        }
        self.assertNotIn("root", orphan_pages)
        self.assertIn("child", orphan_pages)

    def test_parentless_explicit_non_root_role_is_not_legacy_root_exempt(self):
        for page_role in ("HUB", "SUPPORT", "UTILITY", "OTHER"):
            with self.subTest(page_role=page_role):
                architecture = {
                    "schema": "seo-topical-architecture/v1",
                    "structural_tree": {
                        "nodes": [
                            {
                                "page_id": "node",
                                "canonical_parent_id": None,
                                "page_role": page_role,
                            }
                        ],
                        "edges": [],
                    },
                    "semantic_graph": {"nodes": [{"page_id": "node"}], "edges": []},
                }
                audit = seo_internal_linking.audit_link_inventory(
                    architecture=architecture,
                    existing_links=[],
                )
                orphan_pages = {
                    finding["page_id"]
                    for finding in audit["findings"]
                    if finding["type"] == "ORPHAN_PAGE"
                }
                self.assertIn("node", orphan_pages)

    def test_every_empirical_boundary_decision_requires_search_owned_provenance(self):
        boundary_decisions = (
            "CREATE",
            "MERGE",
            "SPLIT",
            "REDIRECT",
            "SECTION_ONLY",
            "BRIDGE",
            "NO_PAGE",
        )
        for decision in boundary_decisions:
            with self.subTest(decision=decision):
                candidate = {
                    "page_id": "p1",
                    "decision": decision,
                    "cluster_ids": ["c1"],
                    "reason_codes": ["WORDSTAT_ASSOCIATION"],
                    "evidence": ["wordstat association"],
                    "confidence": "HIGH",
                    "claim_class": "DERIVED",
                }
                if decision in {"MERGE", "REDIRECT"}:
                    candidate["target_page_id"] = "p2"
                    candidate["reason_codes"].append("WEBMASTER_EXISTING_URL")
                with self.assertRaises(ValueError):
                    seo_topical_architecture.build_topical_architecture(
                        mode="EXISTING_SITE",
                        coverage=COVERAGE,
                        clusters=[valid_cluster()],
                        page_decisions=[candidate],
                        structural_nodes=existing_nodes(),
                        semantic_edges=[],
                    )

    def test_methodology_rejects_metric_and_value_independently(self):
        invalid_records = (
            {
                "kind": "METHODOLOGY",
                "source": "semantic-cocoon-methodology",
                "metric": "internal_link_score",
                "claim": "qualitative heuristic",
            },
            {
                "kind": "METHODOLOGY",
                "source": "semantic-cocoon-methodology",
                "value": 1,
                "claim": "qualitative heuristic",
            },
        )
        for record in invalid_records:
            with self.subTest(record=record):
                bundle = new_bundle(VALID_CONTEXT, {})
                with self.assertRaises(ValueError):
                    add_evidence(bundle, record)

    def test_search_cluster_ingress_rejects_each_malformed_constraint(self):
        malformed_sets = [
            [valid_cluster(cluster_id=" ")],
            [valid_cluster("dup"), valid_cluster("dup", queries=["different query"])],
            [valid_cluster(queries=[])],
            [valid_cluster(queries="seo audit")],
            [valid_cluster(min_shared_urls=0)],
            [valid_cluster(min_shared_urls=True)],
            [valid_cluster(bridge_risk="false")],
            [valid_cluster(limitations="SEARCH_SNAPSHOT_PARTIAL")],
        ]
        for clusters in malformed_sets:
            with self.subTest(clusters=clusters):
                with self.assertRaises(ValueError):
                    seo_topical_architecture.build_topical_architecture(
                        mode="GREENFIELD",
                        coverage=COVERAGE,
                        clusters=clusters,
                        page_decisions=[],
                        structural_nodes=[],
                        semantic_edges=[],
                    )

    def test_attach_audit_appends_without_discarding_existing_audits(self):
        architecture = seo_topical_architecture.build_topical_architecture(
            mode="GREENFIELD",
            coverage=COVERAGE,
            clusters=[],
            page_decisions=[],
            structural_nodes=[],
            semantic_edges=[],
        )
        architecture = seo_topical_architecture.attach_audit(
            architecture,
            {"kind": "INTERNAL_LINK_AUDIT", "findings": []},
        )
        architecture = seo_topical_architecture.attach_audit(
            architecture,
            {"kind": "CONSISTENCY_AUDIT", "findings": [{"type": "EXAMPLE"}]},
        )
        self.assertEqual(
            architecture["audits"],
            [
                {"kind": "INTERNAL_LINK_AUDIT", "findings": []},
                {"kind": "CONSISTENCY_AUDIT", "findings": [{"type": "EXAMPLE"}]},
            ],
        )


if __name__ == "__main__":
    unittest.main()
