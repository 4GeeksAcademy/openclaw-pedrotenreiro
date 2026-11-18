"""Offline tests for the safe 4Geeks project list helper."""

import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

import get_projects


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


def body(results, count=None):
    return json.dumps({"count": len(results) if count is None else count, "results": results}).encode()


class ProjectTests(unittest.TestCase):
    def test_maps_pending_submitted_and_graded_without_private_fields(self):
        results = [
            {"title": "Pending project", "task_status": "PENDING", "revision_status": "PENDING", "github_url": "private"},
            {"title": "Submitted project", "task_status": "DONE", "revision_status": "PENDING", "github_url": "private"},
            {"title": "Graded project", "task_status": "DONE", "revision_status": "APPROVED", "github_url": "private"},
        ]
        with patch.object(get_projects, "urlopen", return_value=FakeResponse(200, body(results))) as mocked:
            result = get_projects.get_projects("test-token")
        self.assertEqual(result, {"projects": [
            {"title": "Pending project", "status": "pending"},
            {"title": "Submitted project", "status": "submitted"},
            {"title": "Graded project", "status": "graded"},
        ], "total": 3})
        request = mocked.call_args.args[0]
        self.assertIn("task_type=PROJECT", request.full_url)
        self.assertEqual(request.get_header("Authorization"), "Token test-token")
        self.assertNotIn("private", json.dumps(result))

    def test_paginates_until_count_is_reached(self):
        first = [{"title": "Project A", "task_status": "PENDING"}]
        second = [{"title": "Project B", "task_status": "PENDING"}]
        with patch.object(get_projects, "fetch_page", side_effect=[(first, 2), (second, 2)]) as mocked:
            result = get_projects.get_projects("test-token")
        self.assertEqual(result["total"], 2)
        self.assertEqual(mocked.call_args_list[1].args[1], 1)

    def test_missing_token_stops_without_request(self):
        with patch.dict("os.environ", {}, clear=True):
            with patch.object(get_projects, "urlopen") as mocked:
                with self.assertRaisesRegex(get_projects.ProjectLookupError, "TOKEN_4GEEKS is unavailable"):
                    get_projects.get_projects()
        mocked.assert_not_called()

    def test_rejected_token_does_not_include_response_body(self):
        error = HTTPError(get_projects.BASE_URL, 401, "unauthorized", {}, io.BytesIO(b"sensitive response"))
        with patch.object(get_projects, "urlopen", side_effect=error):
            with self.assertRaises(get_projects.ProjectLookupError) as caught:
                get_projects.get_projects("test-token")
        self.assertEqual(str(caught.exception), "API rejected the token (HTTP 401)")
        self.assertNotIn("sensitive", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
