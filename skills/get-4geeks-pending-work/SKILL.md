---
name: get-4geeks-pending-work
description: "When Jack asks what 4Geeks work remains, retrieve all assigned tasks and list pending or revision-required items."
---

1. Read `TOKEN_4GEEKS` from the process environment; if the Gateway-hosted execution environment lacks it, load the existing `~/.openclaw/.env` into the execution shell using `set -a; . "$HOME/.openclaw/.env"; set +a` without printing or copying the value. The `.env` setting and protected-secret store are different mechanisms; do not request or expose the token.
2. Run `python3 scripts/get_pending.py` from this skill directory. The helper queries the authenticated `GET https://breathecode.herokuapp.com/v1/assignment/user/me/task` endpoint and paginates the full assigned-task list with finite timeouts.
3. Report tasks with `task_status=PENDING` as pending and tasks with `task_status=REJECTED` or `revision_status=REJECTED` as needing revision. Show each task title and type, but omit submission URLs, raw response bodies, and unrelated profile data; do not infer due dates or requirements not provided by the API response.
4. Report an empty result as “no pending tasks found” only after pagination completes. Report unauthorized, network, malformed data, or pagination-cap errors as unavailable without claiming there is no remaining work.

Verification: run `python3 scripts/test_get_pending.py`, validate the skill, and run `python3 scripts/get_pending.py` with `TOKEN_4GEEKS` available. The live test must confirm all pages were processed; mocked tests do not prove live account results.
