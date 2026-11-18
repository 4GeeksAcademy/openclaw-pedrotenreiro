#!/usr/bin/env python3
"""Retrieve upcoming 4Geeks events without inventing seat availability."""

import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

URL = "https://breathecode.herokuapp.com/v1/events/all"
TIMEOUT_SECONDS = 20


class EventLookupError(Exception):
    """Safe-to-report failure without response content or credentials."""


def get_events(token=None):
    token = token if token is not None else os.environ.get("TOKEN_4GEEKS", "")
    if not token:
        raise EventLookupError("TOKEN_4GEEKS is unavailable")
    query = urlencode({"upcoming": "true", "limit": 100})
    request = Request(f"{URL}?{query}", headers={
        "Authorization": f"Token {token}", "Accept": "application/json"
    }, method="GET")
    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            if response.status != 200:
                raise EventLookupError(f"API returned HTTP {response.status}")
            payload = response.read(2 * 1024 * 1024)
    except HTTPError as exc:
        if exc.code in (401, 403):
            raise EventLookupError(f"API rejected the token (HTTP {exc.code})") from None
        raise EventLookupError(f"API returned HTTP {exc.code}") from None
    except (URLError, TimeoutError, OSError):
        raise EventLookupError("could not reach or read the 4Geeks API") from None
    try:
        data = json.loads(payload)
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise EventLookupError("API response was not valid JSON") from None
    if not isinstance(data, list):
        raise EventLookupError("API response had an unexpected shape")

    events = []
    for item in data:
        if not isinstance(item, dict) or not item.get("title") or not item.get("starting_at"):
            raise EventLookupError("API response contained an event without required fields")
        events.append({
            "title": str(item["title"]),
            "starting_at": item["starting_at"],
            "ending_at": item.get("ending_at"),
            "status": str(item.get("status") or "unknown"),
            "capacity": item.get("capacity"),
            "availability": "not provided by this endpoint",
        })
    events.sort(key=lambda event: event["starting_at"])
    return {"events": events, "total": len(events)}


if __name__ == "__main__":
    try:
        print(json.dumps(get_events(), ensure_ascii=False))
    except EventLookupError as exc:
        print(f"UNAVAILABLE: {exc}")
        sys.exit(1)
