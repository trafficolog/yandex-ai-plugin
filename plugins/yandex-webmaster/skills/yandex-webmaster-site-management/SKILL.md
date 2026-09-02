---
name: yandex-webmaster-site-management
description: Use when listing, adding, verifying or deleting sites in Yandex Webmaster.
---

# Site management

Read `../../references/api-2026.md` and `../../references/safety.md`. Use `scripts/yw_api.py` for generic host/verification endpoints.

Workflow: resolve `user_id` → list/resolve host → read host/verification state → prepare action. Verification uses `GET .../verification` for the UIN/state and `POST .../verification?verification_type=DNS|HTML_FILE|META_TAG` to start checking.

Add/delete host are writes. Deletion is destructive: require approval naming the **exact target** host and DELETE operation. “Clean up unused sites” is not sufficient authorization. Verify the host list after execution.
