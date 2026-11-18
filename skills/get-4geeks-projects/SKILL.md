---
name: get-4geeks-projects
description: "When Jack asks for his assigned 4Geeks projects or their status, retrieve paginated project tasks and report pending, submitted, or graded state."
---

1. Read `TOKEN_4GEEKS` from the process environment; if the Gateway-hosted execution environment lacks it, load the existing `~/.openclaw/.env` into the execution shell with `set -a; . "$HOME/.openclaw/.env"; set +a` without printing the value or copying it to another file. Do not confuse the owner-controlled file-backed environment variable with the protected-secret store, and never request or expose the token for this lookup.
2. Run `python3 scripts/get_projects.py` from this skill directory. The helper calls `GET https://breathecode.herokuapp.com/v1/assignment/user/me/task` using `task_type=PROJECT`, pagination, a finite timeout, and `Authorization: Token <token>`. It emits project titles and normalized statuses only; it must not include submission URLs, response bodies, or other student profile data.
3. Map `task_status=PENDING` to `pending`; map `task_status=DONE` with `revision_status=PENDING` or absent to `submitted`; map `task_status=DONE` with `revision_status=APPROVED` or `REJECTED` (or task status APPROVED/REJECTED) to `graded`. Preserve `unknown` for unrecognized combinations instead of guessing.
4. Report an API rejection as unauthorized without echoing the response body, and network/format errors as unavailable. Do not claim a complete list unless pagination finishes; the helper fails safely if its pagination cap is reached.

Verification: run `python3 scripts/test_get_projects.py`, validate this skill's frontmatter/resources, then run `python3 scripts/get_projects.py` in the environment with `TOKEN_4GEEKS` available. Report the real returned count/statuses as the test; never treat mocked tests as evidence of live account data.
