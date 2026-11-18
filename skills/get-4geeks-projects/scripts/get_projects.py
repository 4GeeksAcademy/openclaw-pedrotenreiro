#!/usr/bin/env python3
"""List the authenticated student's assigned 4Geeks projects and safe statuses."""

import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE_URL = "https://breathecode.herokuapp.com/v1/assignment/user/me/task"
TIMEOUT_SECONDS = 20
PAGE_SIZE = 100
MAX_PAGES = 100


class ProjectLookupError(Exception):
    """A safe-to-report lookup failure with no response body or credentials."""


def display_status(task_status, revision_status):
    task_status = str(task_status or "").upper()
    revision_status = str(revision_status or "").upper()
    if task_status == "PENDING":
        return "pending"
    if task_status in ("APPROVED", "REJECTED"):
        return "graded"
    if task_status == "DONE":
        if revision_status in ("APPROVED", "REJECTED"):
            return "graded"
        if revision_status in ("", "PENDING"):
            return "submitted"
    return "unknown"


def fetch_page(token, offset):
    query = urlencode({"task_type": "PROJECT", "limit": PAGE_SIZE, "offset": offset})
    request = Request(
        f"{BASE_URL}?{query}",
        headers={"Authorization": f"Token {token}", "Accept": "application/json"},
        method="GET",
    )
    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            if response.status != 200:
                raise ProjectLookupError(f"API returned HTTP {response.status}")
            payload = response.read(2 * 1024 * 1024)
    except HTTPError as exc:
        if exc.code in (401, 403):
            raise ProjectLookupError(f"API rejected the token (HTTP {exc.code})") from None
        raise ProjectLookupError(f"API returned HTTP {exc.code}") from None
    except (URLError, TimeoutError, OSError):
        raise ProjectLookupError("could not reach or read the 4Geeks API") from None

    try:
        data = json.loads(payload)
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise ProjectLookupError("API response was not valid JSON") from None
    if not isinstance(data, dict) or not isinstance(data.get("results"), list):
        raise ProjectLookupError("API response had an unexpected shape")
    count = data.get("count")
    if count is not None and (not isinstance(count, int) or count < 0):
        raise ProjectLookupError("API response had an invalid result count")
    return data["results"], count


def get_projects(token=None):
    token = token if token is not None else os.environ.get("TOKEN_4GEEKS", "")
    if not token:
        raise ProjectLookupError("TOKEN_4GEEKS is unavailable")

    projects = []
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
                raise ProjectLookupError("API response contained an invalid project record")
            projects.append({
                "title": str(item.get("title") or "Untitled project"),
                "status": display_status(item.get("task_status"), item.get("revision_status")),
            })
        offset += len(results)
        if expected_count is not None:
            if offset >= expected_count:
                break
        elif len(results) < PAGE_SIZE:
            break
    else:
        raise ProjectLookupError("project list exceeded the safe pagination limit")

    return {"projects": projects, "total": len(projects)}


if __name__ == "__main__":
    try:
        print(json.dumps(get_projects(), ensure_ascii=False))
    except ProjectLookupError as exc:
        print(f"UNAVAILABLE: {exc}")
        sys.exit(1)
