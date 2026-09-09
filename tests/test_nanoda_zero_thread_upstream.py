import unittest
from pathlib import Path

from lib.nanoda_zero_thread_upstream import next_link, validate_issue_url, validate_protocol

ROOT = Path(__file__).resolve().parents[1]


class ProtocolTests(unittest.TestCase):
    def test_bound_protocol(self):
        self.assertEqual(validate_protocol(ROOT), {
            "status": "PASS", "request_cap": 6,
            "conditional_pagination_slots": 2, "external_writes": 0})

    def test_link_parser_accepts_only_explicit_next(self):
        link = '<https://api.github.com/x?page=1>; rel="prev", <https://api.github.com/x?page=3>; rel="next"'
        self.assertEqual(next_link(link), "https://api.github.com/x?page=3")
        self.assertIsNone(next_link('<https://api.github.com/x?page=1>; rel="prev"'))

    def test_pagination_cannot_change_repository_or_query(self):
        exact = "https://api.github.com/repos/ammkrn/nanoda_lib/issues?state=all&per_page=100&sort=updated&direction=desc&page=2"
        self.assertEqual(validate_issue_url(exact, 2), exact)
        for bad in (exact.replace("ammkrn", "other"), exact.replace("page=2", "page=3"),
                    exact + "&labels=bug"):
            with self.assertRaises(ValueError):
                validate_issue_url(bad, 2)


if __name__ == "__main__":
    unittest.main()
