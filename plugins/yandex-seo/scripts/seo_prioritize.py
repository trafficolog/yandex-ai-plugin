from __future__ import annotations

DEFAULT_ORDER = [
    'TECHNICAL_BLOCKER',
    'CONTENT_GAP',
    'CANNIBALIZATION_CANDIDATE',
    'CTR_OPPORTUNITY',
    'LANDING_OR_INTENT_MISMATCH',
    'DISCOVERY_CANDIDATE',
]


def prioritize(findings: list[dict], priority_order: list[str] | None = None) -> list[dict]:
    order = priority_order or DEFAULT_ORDER
    index = {name: i for i, name in enumerate(order)}
    confidence = {'HIGH':0,'MEDIUM':1,'LOW':2}
    basis = 'user-provided-order' if priority_order else 'categorical-evidence-order'
    out = [dict(item) for item in findings]
    out.sort(key=lambda x: (index.get(x.get('type'), len(index)), confidence.get(x.get('confidence'), 3), str(x.get('type',''))))
    for item in out:
        item['priority_basis'] = basis
    return out


def delegate_action(finding: dict) -> dict | None:
    if finding.get('type') == 'TECHNICAL_BLOCKER' and finding.get('issue') in {'NOT_INDEXED','RECRAWL_RECOMMENDED'} and finding.get('url_key'):
        return {
            'service':'yandex-webmaster',
            'skill':'yandex-webmaster-recrawl',
            'target':finding['url_key'],
            'reason':'SEO finding recommends recrawl; execution remains in Webmaster plugin.',
            'requires_approval':True,
        }
    if finding.get('type') == 'SITEMAP_ACTION' and finding.get('target'):
        return {
            'service':'yandex-webmaster',
            'skill':'yandex-webmaster-sitemaps',
            'target':finding['target'],
            'reason':'SEO finding recommends sitemap action; execution remains in Webmaster plugin.',
            'requires_approval':True,
        }
    return None
