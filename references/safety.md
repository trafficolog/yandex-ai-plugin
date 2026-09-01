# Safety contract for Yandex Direct changes

Use these rules for every mutation of a live advertising account.

1. **Read first.** Fetch the exact object and relevant recent metrics before proposing a change.
2. **Preview second.** Show object IDs, current value, proposed value, scope, and expected effect. Generate a dry-run payload when possible.
3. **Explicit approval before writes.** Creating, updating, deleting, suspending, resuming, changing bids/strategies/budgets, or attaching/removing negative sets requires a clear user instruction to apply the previewed change.
4. **Activation is separate.** Creating a campaign does not imply starting impressions. New campaign workflows end in draft/stopped state whenever the API or connected tool permits it.
5. **No invented targets.** Do not invent target CPA, ROAS/DRR, monthly budget, conversion goal, attribution model, margin, or conversion value.
6. **No universal kill threshold.** Rules like “CPA > 3× target = pause” may be presented as heuristics only when sample size, conversion delay, attribution, and business targets make them meaningful.
7. **Preserve rollback data.** For updates, record previous values and IDs in the result log.
8. **Never expose secrets.** Redact OAuth/API tokens in previews, errors, logs, and artifacts.
9. **High-impact bulk edits require tighter scope.** For more than 20 entities, summarize the batch and require approval of the entity set or an attached change file.
10. **Policy and legal claims require fresh verification.** Moderation rules, labeling, regulated-topic requirements, and platform limits can change.
