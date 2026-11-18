---
name: get-4geeks-mentorship
description: "When Jack asks for available 4Geeks mentors, their services, or mentorship schedules, retrieve academy mentors and booking links while accurately distinguishing booking links from confirmed open slots."
---

1. Read `TOKEN_4GEEKS` from the process environment; if the Gateway execution environment lacks it, load the existing `~/.openclaw/.env` into the execution shell with `set -a; . "$HOME/.openclaw/.env"; set +a`, without printing or copying the value. Keep the file-backed environment variable distinct from the protected-secret store.
2. Run `python3 scripts/get_mentors.py` from this skill directory. It authenticates `GET /v1/admissions/user/me`, derives academy IDs from the user's cohort records, and queries all pages of `GET /v1/mentorship/academy/mentor` and `/v1/mentorship/academy/service` with the matching `Academy` header.
3. Summarize the returned mentors by name, status, bio/rating/price/timezone when present, provided service names and status, and booking link if available. Treat the API's returned mentor statuses as-is (ACTIVE, UNLISTED, etc.); do not call UNLISTED public/advertised availability.
4. A mentor's `booking_url` is a scheduler link, not evidence of open appointment slots. The verified listing response has no schedule/timeslot inventory. Explicitly say exact schedule availability is not provided by these listing endpoints; offer the booking link as the next step when present, but do not claim a time is open or fetch a private calendar without a separately authorized source.
5. Report authentication/access, network, malformed response, or missing academy information as unavailable without exposing credentials or raw response bodies. An empty successful list means no mentors/services were returned for the user's associated academies.

Verification: run `python3 scripts/test_get_mentors.py`, validate this skill, then run `python3 scripts/get_mentors.py` with `TOKEN_4GEEKS` available. Verify mentor/service counts and fields from the live response; mocked output is not live proof. Do not emit mentor email addresses or other unneeded personal identifiers.
