from __future__ import annotations

import unicodedata
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode


def normalize_query(text: str) -> str:
    text = unicodedata.normalize('NFKC', text)
    return ' '.join(text.casefold().split())


def normalize_url(url: str) -> str:
    parts = urlsplit(url)
    scheme = parts.scheme.lower()
    host = (parts.hostname or '').lower()
    port = parts.port
    if port and not ((scheme == 'https' and port == 443) or (scheme == 'http' and port == 80)):
        netloc = f'{host}:{port}'
    else:
        netloc = host
    path = parts.path or '/'
    query = urlencode(sorted(parse_qsl(parts.query, keep_blank_values=True)), doseq=True)
    return urlunsplit((scheme, netloc, path, query, ''))


def classify_period_alignment(items: list[dict]) -> str:
    if not items:
        return 'EXACT'
    periods = []
    has_rolling = False
    for item in items:
        if item.get('window'):
            has_rolling = True
            continue
        period = item.get('period')
        if period and period.get('from') and period.get('to'):
            periods.append((period['from'], period['to']))
    if periods and len(set(periods)) > 1:
        return 'MISMATCHED'
    if has_rolling and periods:
        return 'APPROXIMATE'
    if has_rolling and len(items) > 1:
        return 'APPROXIMATE'
    return 'EXACT'
