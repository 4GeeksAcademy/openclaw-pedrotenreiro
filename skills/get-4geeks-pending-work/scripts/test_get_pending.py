"""Offline tests for the safe 4Geeks pending-work helper."""

import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

import get_pending


class FakeResponse:
    def __init__(self, status, body):
        self.status = status
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, _limit):
        return self.body


def page(results, count=None):
    return json.dumps({"count": len(results) if count is None else count, "results": results}).encode()


class PendingTests(unittest.TestCase):
    def test_filters_pending_and_rejected_tasks(self):
        rows = [
            {"title": "To do", "task_type": "EXERCISE", "task_status": "PENDING"},
            {"title": "Revise", "task_type": "PROJECT", "task_status": "DONE", "revision_status": "REJECTED", "github_url": "private"},
            {"title": "Approved", "task_type": "LESSON", "task_status": "DONE", "revision_status": "APPROVED"},
        ]
        with patch.object(get_pending, "urlopen", return_value=FakeResponse(200, page(rows))) as mocked:
            result = get_pending.get_pending("test-token")
        self.assertEqual(result, {"pending": [
            {"title": "To do", "type": "exercise", "status": "pending"},
            {"title": "Revise", "type": "project", "status": "needs revision"},
        ], "total": 2})
        self.assertEqual(mocked.call_args.args[0].get_header("Authorization"), "Token test-token")
        self.assertNotIn("private", json.dumps(result))

    def test_paginates_through_all_tasks(self):
        with patch.object(get_pending, "fetch_page", side_effect=[
            ([{"title": "A", "task_status": "PENDING"}], 2),
            ([{"title": "B", "task_status": "DONE"}], 2),
        ]) as mocked:
            result = get_pending.get_pending("test-token")
        self.assertEqual(result["total"], 1)
        self.assertEqual(mocked.call_args_list[1].args[1], 1)

    def test_missing_token_stops_before_request(self):
        with patch.dict("os.environ", {}, clear=True):
            with patch.object(get_pending, "urlopen") as mocked:
                with self.assertRaisesRegex(get_pending.PendingLookupError, "TOKEN_4GEEKS is unavailable"):
                    get_pending.get_pending()
        mocked.assert_not_called()

    def test_unauthorized_error_does_not_echo_body(self):
        error = HTTPError(get_pending.URL, 401, "unauthorized", {}, io.BytesIO(b"sensitive"))
        with patch.object(get_pending, "urlopen", side_effect=error):
            with self.assertRaises(get_pending.PendingLookupError) as caught:
                get_pending.get_pending("test-token")
        self.assertEqual(str(caught.exception), "API rejected the token (HTTP 401)")
        self.assertNotIn("sensitive", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
