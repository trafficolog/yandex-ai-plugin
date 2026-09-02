# Deferred search lifecycle

`POST /v2/web/searchAsync` returns an Operation ID. Treat submit, status and collect as separate resumable steps; persist operation ID and submission time. Current documented minimum processing time is 5 minutes and result retention is 12 hours. Never implement an endless polling loop in an agent workflow.
