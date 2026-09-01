# Safety contract

All consequential actions use:

`read → analyze → preview → explicit approval → write → verify`

## Read

Diagnostics, summary, SQI, indexing/search history, queries, links, sitemap/feed status, quota/limits.

## Low-risk but state-changing

Verification start and ordinary URL recrawl. Still require explicit approval.

## Consequential / quota-consuming

Add host, add sitemap, add feed, priority sitemap recrawl, archive/PRO export initiation.

## Destructive

Delete host, user-added sitemap or feed. Approval must identify the exact target. A generic request to “clean up” is not deletion authorization.

Never expose OAuth tokens. Never claim that recrawl guarantees indexing/ranking or that adding a sitemap guarantees discovery/inclusion.
