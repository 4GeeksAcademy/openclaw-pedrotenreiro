#!/usr/bin/env python3
"""Summarize authenticated student's assigned 4Geeks task progress."""

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


class ProgressLookupError(Exception):
    """Safe-to-report API lookup error."""


def fetch_page(token, offset):
    query = urlencode({"limit": PAGE_SIZE, "offset": offset})
    request = Request(f"{URL}?{query}", headers={
        "Authorization": f"Token {token}", "Accept": "application/json"
    }, method="GET")
    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            if response.status != 200:
                raise ProgressLookupError(f"API returned HTTP {response.status}")
            payload = response.read(2 * 1024 * 1024)
    except HTTPError as exc:
        if exc.code in (401, 403):
            raise ProgressLookupError(f"API rejected the token (HTTP {exc.code})") from None
        raise ProgressLookupError(f"API returned HTTP {exc.code}") from None
    except (URLError, TimeoutError, OSError):
        raise ProgressLookupError("could not reach or read the 4Geeks API") from None
    try:
        data = json.loads(payload)
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise ProgressLookupError("API response was not valid JSON") from None
    if not isinstance(data, dict) or not isinstance(data.get("results"), list):
        raise ProgressLookupError("API response had an unexpected shape")
    count = data.get("count")
    if count is not None and (not isinstance(count, int) or count < 0):
        raise ProgressLookupError("API response had an invalid result count")
    return data["results"], count


def get_progress(token=None):
    token = token if token is not None else os.environ.get("TOKEN_4GEEKS", "")
    if not token:
        raise ProgressLookupError("TOKEN_4GEEKS is unavailable")
    counts = {"assigned": 0, "pending": 0, "submitted": 0, "graded": 0, "unknown": 0}
    offset = 0
    expected_count = None
    for _ in range(MAX_PAGES):
        rows, count = fetch_page(token, offset)
        if expected_count is None:
            expected_count = count
        if not rows:
            break
        for task in rows:
            if not isinstance(task, dict):
                raise ProgressLookupError("API response contained an invalid task record")
            counts["assigned"] += 1
            task_status = str(task.get("task_status") or "").upper()
            revision_status = str(task.get("revision_status") or "").upper()
            if task_status == "PENDING":
                counts["pending"] += 1
            elif task_status in ("APPROVED", "REJECTED") or revision_status in ("APPROVED", "REJECTED"):
                counts["graded"] += 1
            elif task_status == "DONE" and revision_status in ("", "PENDING"):
                counts["submitted"] += 1
            else:
                counts["unknown"] += 1
        offset += len(rows)
        if expected_count is not None:
            if offset >= expected_count:
                break
        elif len(rows) < PAGE_SIZE:
            break
    else:
        raise ProgressLookupError("task list exceeded the safe pagination limit")
    if expected_count is not None and counts["assigned"] != expected_count:
        raise ProgressLookupError("API task pagination ended before all assigned tasks were retrieved")
    counts["completion_percent"] = round(100 * (counts["submitted"] + counts["graded"]) / counts["assigned"]) if counts["assigned"] else 0
    return counts


if __name__ == "__main__":
    try:
        print(json.dumps(get_progress(), ensure_ascii=False))
    except ProgressLookupError as exc:
        print(f"UNAVAILABLE: {exc}")
        sys.exit(1)
