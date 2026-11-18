#!/usr/bin/env python3
import unittest
from unittest.mock import patch

from get_mentors import MentorshipLookupError, _all_pages, get_mentors


class MentorshipTests(unittest.TestCase):
    @patch("get_mentors._all_pages")
    @patch("get_mentors._get_json")
    def test_lists_mentors_services_and_disclaims_live_slots(self, get_json, all_pages):
        get_json.return_value = {"cohorts": [
            {"cohort": {"academy": {"id": 6}}},
            {"cohort": {"academy": {"id": 6}}},
        ]}
        all_pages.side_effect = [
            [{"id": 2, "slug": "mentor-a", "status": "ACTIVE", "booking_url": "https://cal.example",
              "user": {"first_name": "A", "last_name": "B"},
              "services": [{"slug": "career", "name": "Career", "status": "ACTIVE"}]}],
            [{"id": 5, "slug": "career", "name": "Career", "status": "ACTIVE"}],
        ]
        result = get_mentors("t")
        self.assertEqual(result["academies_checked"], 1)
        self.assertEqual(result["total_mentors"], 1)
        self.assertEqual(result["mentors"][0]["name"], "A B")
        self.assertIn("not provided", result["mentors"][0]["schedule_availability"])
        self.assertIn("not exposed", result["schedule_availability"])
        self.assertEqual(all_pages.call_count, 2)

    @patch("get_mentors._all_pages")
    @patch("get_mentors._get_json")
    def test_collects_multiple_academies_and_deduplicates(self, get_json, all_pages):
        get_json.return_value = {"cohorts": [
            {"cohort": {"academy": {"id": 6}}},
            {"cohort": {"academy": {"id": 9}}},
        ]}
        all_pages.side_effect = [
            [{"id": 1, "slug": "x", "user": {}, "services": []}], [],
            [{"id": 1, "slug": "x", "user": {}, "services": []}], [],
        ]
        result = get_mentors("t")
        self.assertEqual(result["academies_checked"], 2)
        self.assertEqual(result["total_mentors"], 1)
        self.assertEqual(all_pages.call_count, 4)

    @patch("get_mentors._get_json")
    def test_paginates_all_results(self, get_json):
        get_json.side_effect = [
            {"results": [{"id": 1}], "next": "https://api.invalid/?limit=100&offset=100"},
            {"results": [{"id": 2}], "next": None},
        ]
        result = _all_pages("mentorship/academy/mentor", "t", 6)
        self.assertEqual([item["id"] for item in result], [1, 2])
        self.assertEqual(get_json.call_count, 2)
        self.assertIn("offset=1", get_json.call_args_list[1].args[0])

    @patch("get_mentors._get_json")
    def test_missing_academy_is_safe_error(self, get_json):
        get_json.return_value = {"cohorts": []}
        with self.assertRaisesRegex(MentorshipLookupError, "academy ID"):
            get_mentors("t")

    def test_missing_token_is_safe_error(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaisesRegex(MentorshipLookupError, "TOKEN_4GEEKS"):
                get_mentors()


if __name__ == "__main__":
    unittest.main()
