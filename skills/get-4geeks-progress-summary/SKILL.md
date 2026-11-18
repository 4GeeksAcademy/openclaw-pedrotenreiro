---
name: get-4geeks-progress-summary
description: "When Jack asks how far along he is in the 4Geeks course, aggregate assigned tasks into an evidence-based progress summary."
---

1. Read `TOKEN_4GEEKS` from the process environment; if absent there, load the existing `~/.openclaw/.env` into the execution shell using `set -a; . "$HOME/.openclaw/.env"; set +a`, without printing or copying the token. The file-backed environment setting and protected-secret store are distinct; do not request or expose the token.
2. Run `python3 scripts/get_progress.py` from this skill directory. The helper fetches the authenticated, paginated `GET https://breathecode.herokuapp.com/v1/assignment/user/me/task` results with finite timeouts and verifies the API's reported total is fully retrieved.
3. Summarize assigned count and status totals: PENDING is pending; DONE with no revision or PENDING revision is submitted; APPROVED/REJECTED task or revision is graded. Explain that the reported completion percentage counts submitted plus graded tasks divided by all assigned tasks; it is a task-status snapshot, not an official course completion percentage.
4. Report API/authentication/pagination errors as unavailable, not as zero progress. Do not infer requirements, due dates, or course completion from task counts alone.

Verification: run `python3 scripts/test_get_progress.py`, validate the skill, and execute `python3 scripts/get_progress.py` with `TOKEN_4GEEKS` available. Report the real totals and explicitly qualify the metric; mocked results are not live proof.
