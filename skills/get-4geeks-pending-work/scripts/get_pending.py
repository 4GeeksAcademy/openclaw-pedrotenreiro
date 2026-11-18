#!/usr/bin/env python3
"""List the authenticated student's 4Geeks tasks that still need completion."""

import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

URL = "https://breathecode.herokuapp.com/v1/assignment/user/me/task"
TIMEOUT_SECONDS = 20
PAGE_SIZE = 100
MAX_PAGES = 100


class PendingLookupError(Exception):
    """Safe-to-report API lookup error; never includes the response body."""


def fetch_page(token, offset):
    query = urlencode({"limit": PAGE_SIZE, "offset": offset})
    request = Request(
        f"{URL}?{query}",
        headers={"Authorization": f"Token {token}", "Accept": "application/json"},
        method="GET",
    )
    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            if response.status != 200:
                raise PendingLookupError(f"API returned HTTP {response.status}")
            payload = response.read(2 * 1024 * 1024)
    except HTTPError as exc:
        if exc.code in (401, 403):
            raise PendingLookupError(f"API rejected the token (HTTP {exc.code})") from None
        raise PendingLookupError(f"API returned HTTP {exc.code}") from None
    except (URLError, TimeoutError, OSError):
        raise PendingLookupError("could not reach or read the 4Geeks API") from None

    try:
        data = json.loads(payload)
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise PendingLookupError("API response was not valid JSON") from None
    if not isinstance(data, dict) or not isinstance(data.get("results"), list):
        raise PendingLookupError("API response had an unexpected shape")
    count = data.get("count")
    if count is not None and (not isinstance(count, int) or count < 0):
        raise PendingLookupError("API response had an invalid result count")
    return data["results"], count


def get_pending(token=None):
    token = token if token is not None else os.environ.get("TOKEN_4GEEKS", "")
    if not token:
        raise PendingLookupError("TOKEN_4GEEKS is unavailable")

    pending = []
    offset = 0
    expected_count = None
    for _ in range(MAX_PAGES):
        results, count = fetch_page(token, offset)
        if expected_count is None:
            expected_count = count
        if not results:
            break
        for item in results:
            if not isinstance(item, dict):
                raise PendingLookupError("API response contained an invalid task record")
            task_status = str(item.get("task_status") or "").upper()
            revision_status = str(item.get("revision_status") or "").upper()
            if task_status in ("PENDING", "REJECTED") or revision_status == "REJECTED":
                pending.append({
                    "title": str(item.get("title") or "Untitled task"),
                    "type": str(item.get("task_type") or "unknown").lower(),
                    "status": "needs revision" if task_status == "REJECTED" or revision_status == "REJECTED" else "pending",
                })
        offset += len(results)
        if expected_count is not None:
            if offset >= expected_count:
                break
        elif len(results) < PAGE_SIZE:
            break
    else:
        raise PendingLookupError("task list exceeded the safe pagination limit")

    return {"pending": pending, "total": len(pending)}


if __name__ == "__main__":
    try:
        print(json.dumps(get_pending(), ensure_ascii=False))
    except PendingLookupError as exc:
        print(f"UNAVAILABLE: {exc}")
        sys.exit(1)
