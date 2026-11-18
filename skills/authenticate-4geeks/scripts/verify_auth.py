#!/usr/bin/env python3
"""Safely verify a 4Geeks student token without printing it or user data."""

import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


URL = "https://breathecode.herokuapp.com/v1/admissions/user/me"
TIMEOUT_SECONDS = 15


def verify(token=None):
    token = token if token is not None else os.environ.get("TOKEN_4GEEKS", "")
    if not token:
        return "UNVERIFIED: protected student token is unavailable", 2

    request = Request(URL, headers={"Authorization": f"Token {token}", "Accept": "application/json"}, method="GET")
    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            status = response.status
            payload = response.read(1024 * 1024)
    except HTTPError as exc:
        if exc.code in (401, 403):
            return "NOT AUTHENTICATED: the API rejected the token (HTTP %d)" % exc.code, 1
        return "INCONCLUSIVE: the API returned HTTP %d" % exc.code, 3
    except (URLError, TimeoutError, OSError):
        return "INCONCLUSIVE: could not reach or read the 4Geeks API", 3

    if status != 200:
        return "INCONCLUSIVE: the API returned HTTP %d" % status, 3
    try:
        user = json.loads(payload)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return "INCONCLUSIVE: the API response was not valid JSON", 3
    if not isinstance(user, dict):
        return "INCONCLUSIVE: the API response did not contain a user object", 3
    return "AUTHENTICATED: the API accepted the token for the current-user request", 0


if __name__ == "__main__":
    message, code = verify()
    print(message)
    sys.exit(code)
