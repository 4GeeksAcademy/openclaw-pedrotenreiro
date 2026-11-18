"""Offline tests for progress aggregation and safe error handling."""

import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

import get_progress


class FakeResponse:
    status = 200
    def __init__(self, rows, count=None):
        self.payload = json.dumps({"results": rows, "count": len(rows) if count is None else count}).encode()
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self, _limit): return self.payload


class ProgressTests(unittest.TestCase):
    def test_aggregates_pending_submitted_and_graded(self):
        rows = [
            {"task_status": "PENDING"},
            {"task_status": "DONE", "revision_status": "PENDING"},
            {"task_status": "DONE", "revision_status": "APPROVED"},
            {"task_status": "DONE", "revision_status": "REJECTED"},
        ]
        with patch.object(get_progress, "urlopen", return_value=FakeResponse(rows)):
            self.assertEqual(get_progress.get_progress("test"), {
                "assigned": 4, "pending": 1, "submitted": 1, "graded": 2,
                "unknown": 0, "completion_percent": 75,
            })

    def test_paginates_all_assignments(self):
        with patch.object(get_progress, "fetch_page", side_effect=[
            ([{"task_status": "PENDING"}], 2),
            ([{"task_status": "DONE", "revision_status": "APPROVED"}], 2),
        ]) as mocked:
            result = get_progress.get_progress("test")
        self.assertEqual(result["assigned"], 2)
        self.assertEqual(mocked.call_args_list[1].args[1], 1)

    def test_incomplete_pagination_is_unavailable(self):
        with patch.object(get_progress, "fetch_page", side_effect=[
            ([{"task_status": "PENDING"}], 2),
            ([], 2),
        ]):
            with self.assertRaisesRegex(get_progress.ProgressLookupError, "pagination ended"):
                get_progress.get_progress("test")

    def test_missing_token_stops_before_request(self):
        with patch.dict("os.environ", {}, clear=True):
            with patch.object(get_progress, "urlopen") as mocked:
                with self.assertRaisesRegex(get_progress.ProgressLookupError, "TOKEN_4GEEKS is unavailable"):
                    get_progress.get_progress()
        mocked.assert_not_called()

    def test_unauthorized_response_body_is_not_reported(self):
        error = HTTPError(get_progress.URL, 401, "unauthorized", {}, io.BytesIO(b"secret body"))
        with patch.object(get_progress, "urlopen", side_effect=error):
            with self.assertRaises(get_progress.ProgressLookupError) as caught:
                get_progress.get_progress("test")
        self.assertNotIn("secret", str(caught.exception))


if __name__ == "__main__": unittest.main()
