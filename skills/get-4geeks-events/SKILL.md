---
name: get-4geeks-events
description: "When Jack asks for upcoming 4Geeks events, retrieve active events with timestamps and accurately reported availability."
---

1. Read `TOKEN_4GEEKS` from the process environment; if the Gateway execution environment lacks it, load the existing `~/.openclaw/.env` into the execution shell with `set -a; . "$HOME/.openclaw/.env"; set +a`, without printing or copying the value. Keep the file-backed environment variable distinct from the protected-secret store.
2. Run `python3 scripts/get_events.py` from this skill directory. The helper makes an authenticated request to `GET https://breathecode.herokuapp.com/v1/events/all?upcoming=true` with a finite timeout.
3. Report each returned event's title, ISO-8601 start/end timestamps (preserving their UTC `Z` or converting only with an explicit timezone label), status, and capacity when provided. Do not present `capacity` as remaining seats: the API response has no registration count or available-seat field, so availability must be reported as “not provided by this endpoint.” Do not invent registration links or infer open seats from capacity/status.
4. Report unauthorized, network, or malformed responses as unavailable; an empty successful response means no upcoming events were returned by this endpoint.

Verification: run `python3 scripts/test_get_events.py`, validate the skill, then run `python3 scripts/get_events.py` with `TOKEN_4GEEKS` available. Verify actual event titles/count and required fields; mocked output is not live proof.
