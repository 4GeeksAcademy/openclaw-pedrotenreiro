"""Offline tests for the authentication verifier. No network calls or credentials."""

import io
import json
import unittest
from unittest.mock import patch

import verify_auth


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


class VerifyAuthTests(unittest.TestCase):
    @patch.object(verify_auth, "urlopen", return_value=FakeResponse(200, json.dumps({"id": 1}).encode()))
    def test_accepted_token_sends_expected_header_and_reports_no_profile_data(self, mocked):
        result = verify_auth.verify("test-token-not-a-real-secret")
        self.assertEqual(result, ("AUTHENTICATED: the API accepted the token for the current-user request", 0))
        request = mocked.call_args.args[0]
        timeout = mocked.call_args.kwargs["timeout"]
        self.assertEqual(request.full_url, verify_auth.URL)
        self.assertEqual(request.get_method(), "GET")
        self.assertEqual(request.get_header("Authorization"), "Token test-token-not-a-real-secret")
        self.assertEqual(timeout, verify_auth.TIMEOUT_SECONDS)
        self.assertNotIn("test-token", result[0])
        self.assertNotIn('"id"', result[0])

    @patch.object(verify_auth, "urlopen", side_effect=verify_auth.HTTPError(verify_auth.URL, 401, "unauthorized", {}, io.BytesIO(b"sensitive body")))
    def test_rejected_token_does_not_echo_response_body(self, _mocked):
        result = verify_auth.verify("test-token-not-a-real-secret")
        self.assertEqual(result, ("NOT AUTHENTICATED: the API rejected the token (HTTP 401)", 1))
        self.assertNotIn("sensitive", result[0])

    def test_reads_configured_token_name_from_environment_without_printing_it(self):
        with patch.dict("os.environ", {"TOKEN_4GEEKS": "private-test-value"}, clear=True):
            with patch.object(verify_auth, "urlopen", return_value=FakeResponse(200, b'{"ok":true}')) as mocked:
                result = verify_auth.verify()
        self.assertEqual(result[1], 0)
        self.assertEqual(mocked.call_args.args[0].get_header("Authorization"), "Token private-test-value")
        self.assertNotIn("private-test-value", result[0])

    def test_missing_token_does_not_make_request(self):
        with patch.dict("os.environ", {}, clear=True):
            with patch.object(verify_auth, "urlopen") as mocked:
                result = verify_auth.verify()
        mocked.assert_not_called()
        self.assertEqual(result[1], 2)


if __name__ == "__main__":
    unittest.main()
