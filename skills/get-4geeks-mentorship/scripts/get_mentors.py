#!/usr/bin/env python3
"""List academy mentorship providers and booking links; API has no slot inventory."""

import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE = "https://breathecode.herokuapp.com/v1"
TIMEOUT_SECONDS = 25
PAGE_SIZE = 100


class MentorshipLookupError(Exception):
    """Safe-to-report failure without response content or credentials."""


def _get_json(url, token, academy_id=None):
    headers = {"Authorization": f"Token {token}", "Accept": "application/json"}
    if academy_id is not None:
        headers["Academy"] = str(academy_id)
    request = Request(url, headers=headers, method="GET")
    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            if response.status != 200:
                raise MentorshipLookupError(f"API returned HTTP {response.status}")
            payload = response.read(4 * 1024 * 1024)
    except HTTPError as exc:
        if exc.code in (401, 403):
            raise MentorshipLookupError(f"API rejected the token or academy access (HTTP {exc.code})") from None
        raise MentorshipLookupError(f"API returned HTTP {exc.code}") from None
    except (URLError, TimeoutError, OSError):
        raise MentorshipLookupError("could not reach or read the 4Geeks API") from None
    try:
        return json.loads(payload)
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise MentorshipLookupError("API response was not valid JSON") from None


def _all_pages(path, token, academy_id=None):
    items, offset = [], 0
    while True:
        query = urlencode({"limit": PAGE_SIZE, "offset": offset})
        url = f"{BASE}/{path}?{query}"
        data = _get_json(url, token, academy_id)
        if isinstance(data, list):
            batch, has_next = data, len(data) == PAGE_SIZE
        elif isinstance(data, dict) and isinstance(data.get("results"), list):
            batch, has_next = data["results"], bool(data.get("next"))
        else:
            raise MentorshipLookupError("API response had an unexpected pagination shape")
        if any(not isinstance(item, dict) for item in batch):
            raise MentorshipLookupError("API response contained an invalid record")
        items.extend(batch)
        if not has_next:
            return items
        if not batch:
            raise MentorshipLookupError("API pagination did not advance")
        offset += len(batch)


def _academy_ids(user):
    ids = set()
    for enrollment in user.get("cohorts", []) if isinstance(user, dict) else []:
        if not isinstance(enrollment, dict):
            continue
        cohort = enrollment.get("cohort") or {}
        academy = cohort.get("academy") or {} if isinstance(cohort, dict) else {}
        academy_id = academy.get("id") if isinstance(academy, dict) else None
        if academy_id is not None:
            ids.add(academy_id)
    return sorted(ids, key=str)


def get_mentors(token=None):
    token = token if token is not None else os.environ.get("TOKEN_4GEEKS", "")
    if not token:
        raise MentorshipLookupError("TOKEN_4GEEKS is unavailable")

    user = _get_json(f"{BASE}/admissions/user/me", token)
    academy_ids = _academy_ids(user)
    if not academy_ids:
        raise MentorshipLookupError("could not find an academy ID in the current user's cohort records")

    mentors, services = [], []
    for academy_id in academy_ids:
        mentors.extend(_all_pages("mentorship/academy/mentor", token, academy_id))
        services.extend(_all_pages("mentorship/academy/service", token, academy_id))

    service_fields = ("id", "slug", "name", "status", "duration", "language")
    mentor_fields = ("id", "slug", "status", "one_line_bio", "rating", "price_per_hour", "booking_url", "timezone")
    mentor_results = []
    seen = set()
    for mentor in mentors:
        identity = (str(mentor.get("id")), str(mentor.get("slug")))
        if identity in seen:
            continue
        seen.add(identity)
        user_info = mentor.get("user") or {}
        service_list = mentor.get("services") or []
        if not isinstance(user_info, dict) or not isinstance(service_list, list):
            raise MentorshipLookupError("API response contained a mentor with an unexpected shape")
        mentor_results.append({
            "name": " ".join(part for part in (user_info.get("first_name"), user_info.get("last_name")) if part),
            **{field: mentor.get(field) for field in mentor_fields},
            "services": [{field: service.get(field) for field in service_fields if field in service}
                         for service in service_list if isinstance(service, dict)],
            "schedule_availability": "not provided by this API; booking_url may link to Calendly",
        })

    service_results = []
    service_seen = set()
    for service in services:
        identity = str(service.get("id", service.get("slug", "")))
        if identity in service_seen:
            continue
        service_seen.add(identity)
        service_results.append({field: service.get(field) for field in service_fields if field in service})

    return {
        "academies_checked": len(academy_ids),
        "mentors": mentor_results,
        "services": service_results,
        "schedule_availability": "specific open timeslots are not exposed by the mentorship listing API",
        "total_mentors": len(mentor_results),
        "total_services": len(service_results),
    }


if __name__ == "__main__":
    try:
        print(json.dumps(get_mentors(), ensure_ascii=False))
    except MentorshipLookupError as exc:
        print(f"UNAVAILABLE: {exc}")
        sys.exit(1)
