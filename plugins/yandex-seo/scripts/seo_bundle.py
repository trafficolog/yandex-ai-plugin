from __future__ import annotations

ALLOWED_KINDS = {'OBSERVED','DERIVED','HYPOTHESIS'}


def new_bundle(context: dict, coverage: dict) -> dict:
    return {
        'version': 1,
        'context': dict(context),
        'coverage': dict(coverage),
        'queries': [],
        'pages': [],
        'clusters': [],
        'sources': {},
        'evidence': [],
        'findings': [],
        'limitations': [],
    }


def add_evidence(bundle: dict, evidence: dict) -> dict:
    if evidence.get('kind') not in ALLOWED_KINDS:
        raise ValueError('evidence kind must be OBSERVED, DERIVED, or HYPOTHESIS')
    if evidence.get('metric') == 'demand':
        raise ValueError('ambiguous demand metric is forbidden; use source-specific metric name')
    if not evidence.get('source'):
        raise ValueError('evidence source is required')
    bundle.setdefault('evidence', []).append(dict(evidence))
    return bundle
