"""Offline tests for the safe upcoming-event lookup."""

import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

import get_events


class FakeResponse:
    status = 200
    def __init__(self, data): self.payload = json.dumps(data).encode()
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self, _limit): return self.payload


class EventTests(unittest.TestCase):
    def test_returns_times_and_does_not_infer_availability(self):
        rows = [
            {"title": "Later", "starting_at": "2026-12-01T10:00:00Z", "ending_at": "2026-12-01T11:00:00Z", "status": "ACTIVE", "capacity": 100},
            {"title": "Sooner", "starting_at": "2026-11-20T10:00:00Z", "ending_at": "2026-11-20T11:00:00Z", "status": "ACTIVE", "capacity": 150, "remaining_seats": 99},
        ]
        with patch.object(get_events, "urlopen", return_value=FakeResponse(rows)) as mocked:
            result = get_events.get_events("test-token")
        self.assertEqual([e["title"] for e in result["events"]], ["Sooner", "Later"])
        self.assertEqual(result["events"][0]["availability"], "not provided by this endpoint")
        self.assertNotIn("remaining_seats", result["events"][0])
        req = mocked.call_args.args[0]
        self.assertIn("upcoming=true", req.full_url)
        self.assertEqual(req.get_header("Authorization"), "Token test-token")

    def test_empty_list_is_successful_empty_result(self):
        with patch.object(get_events, "urlopen", return_value=FakeResponse([])):
            self.assertEqual(get_events.get_events("test"), {"events": [], "total": 0})

    def test_missing_token_makes_no_request(self):
        with patch.dict("os.environ", {}, clear=True):
            with patch.object(get_events, "urlopen") as mocked:
                with self.assertRaisesRegex(get_events.EventLookupError, "TOKEN_4GEEKS is unavailable"):
                    get_events.get_events()
        mocked.assert_not_called()

    def test_unauthorized_error_does_not_echo_body(self):
        error = HTTPError(get_events.URL, 401, "unauthorized", {}, io.BytesIO(b"private body"))
        with patch.object(get_events, "urlopen", side_effect=error):
            with self.assertRaises(get_events.EventLookupError) as caught:
                get_events.get_events("test")
        self.assertEqual(str(caught.exception), "API rejected the token (HTTP 401)")
        self.assertNotIn("private", str(caught.exception))


if __name__ == "__main__": unittest.main()
