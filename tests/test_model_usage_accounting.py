"""Aggregate-only model usage extraction regressions."""
from pathlib import Path
import json
import tempfile
import unittest

from lib.model_usage_accounting import UsageError, extract


ROOT_TURN = "root-turn"


def row(kind, payload, timestamp="2026-09-29T12:00:00Z"):
    return json.dumps({"timestamp": timestamp, "type": kind, "payload": payload})


def usage(input_tokens=10, cached=6, output=3, reasoning=2, cache_write=1):
    return {"input_tokens": input_tokens, "cached_input_tokens": cached,
            "cache_write_input_tokens": cache_write, "output_tokens": output,
            "reasoning_output_tokens": reasoning, "total_tokens": input_tokens + output}


class ModelUsageAccountingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, name, rows):
        path = self.root / name
        path.write_text("\n".join(rows) + "\n")
        return path

    def session(self, response_id="response-1", root_turn=ROOT_TURN, counters=None):
        return [
            row("session_meta", {"id": "thread-1", "cwd": self.root.as_posix()}),
            row("turn_context", {"turn_id": "turn-1", "model": "gpt-test"}),
            row("response_item", {"private": "must never appear"}),
            row("token_usage_record", {"response_id": response_id,
                "root_turn_id": root_turn, "turn_id": "turn-1",
                "usage": counters or usage()}),
        ]

    def test_unique_responses_aggregate_cached_uncached_and_never_copy_content(self):
        first = self.write("one.jsonl", self.session())
        second_rows = self.session(response_id="response-2", counters=usage(8, 2, 4, 1, 0))
        second_rows[0] = row("session_meta", {"id": "thread-2", "cwd": self.root.as_posix()})
        second = self.write("two.jsonl", second_rows)
        result = extract([first, second], root_turn_id=ROOT_TURN,
                         project_root=self.root, observed_at="2026-09-29T12:01:00Z")
        self.assertEqual(result["responses"], 2)
        self.assertEqual(result["totals"]["input_tokens"], 18)
        self.assertEqual(result["totals"]["cached_input_tokens"], 8)
        self.assertEqual(result["totals"]["uncached_input_tokens"], 10)
        self.assertEqual(result["totals"]["output_tokens"], 7)
        self.assertEqual(result["by_model"][0]["responses"], 2)
        self.assertNotIn("private", json.dumps(result))

    def test_identical_response_observation_is_deduplicated(self):
        rows = self.session()
        first = self.write("one.jsonl", rows)
        second = self.write("two.jsonl", rows)
        result = extract([first, second], root_turn_id=ROOT_TURN, project_root=self.root)
        self.assertEqual(result["responses"], 1)
        self.assertEqual(result["duplicate_observations_deduplicated"], 1)

    def test_conflicting_duplicate_and_invalid_usage_fail_closed(self):
        first = self.write("one.jsonl", self.session())
        second = self.write("two.jsonl", self.session(counters=usage(11, 6, 3, 2, 1)))
        with self.assertRaisesRegex(UsageError, "conflicting duplicate"):
            extract([first, second], root_turn_id=ROOT_TURN, project_root=self.root)
        bad = self.write("bad.jsonl", self.session(counters=usage(3, 4, 1, 1, 0)))
        with self.assertRaisesRegex(UsageError, "cached input exceeds"):
            extract([bad], root_turn_id=ROOT_TURN, project_root=self.root)

    def test_missing_match_and_wrong_project_fail(self):
        source = self.write("one.jsonl", self.session(root_turn="other"))
        with self.assertRaisesRegex(UsageError, "no response"):
            extract([source], root_turn_id=ROOT_TURN, project_root=self.root)
        with self.assertRaisesRegex(UsageError, "outside the selected project"):
            extract([source], root_turn_id="other", project_root=self.root / "different")


if __name__ == "__main__":
    unittest.main()
