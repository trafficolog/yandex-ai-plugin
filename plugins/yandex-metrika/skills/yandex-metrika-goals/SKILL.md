---
name: yandex-metrika-goals
description: Use when reading, creating, updating or deleting Yandex Metrika goals.
---

# Manage goals safely

Read `../../references/safety.md` and `../../references/api-2026.md`.

## Before changing a goal

Read the counter and current goals. Identify the business event, existing duplicates, goal type/conditions and whether historic reporting depends on the current definition.

Prepare an exact before/after preview. Creation and update require explicit approval before execution. Deletion is destructive: require confirmation that clearly identifies the counter and goal.

After a write, read the goal back and verify the expected state. Do not infer that a newly created goal has historical data.

Use `../../scripts/ym_api.py` for raw Management API operations when local execution is available; write methods are preview-only unless `--execute` is supplied.
