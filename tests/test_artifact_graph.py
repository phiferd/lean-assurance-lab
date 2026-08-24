from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))

from artifact_graph import evaluate_graph, load_graph, require_current, sha256_file


def graph_for(root: Path) -> dict:
    source = root / "source"
    result = root / "result"
    source.write_text("source", encoding="utf-8")
    result.write_text("result", encoding="utf-8")
    source_digest = sha256_file(source)
    result_digest = sha256_file(result)
    return {
        "schema_version": 1,
        "generated_at": "2026-08-23T00:00:00+00:00",
        "provenance": {
            "repository_revision": "a",
            "arena_revision": "b",
            "validator_source_sha256": source_digest,
            "lean_versions": {},
            "mutation_specs_sha256": "c",
            "corpus_inventory_sha256": "d",
            "scripts_sha256": "e",
            "configurations_sha256": "f",
        },
        "nodes": [
            {
                "id": "input",
                "artifact_type": "validator",
                "lifecycle": "current",
                "required_for_current_claims": True,
                "locator": {"kind": "file", "path": "source"},
                "dependencies": [],
                "expected_sha256": source_digest,
            },
            {
                "id": "report",
                "artifact_type": "report",
                "lifecycle": "current",
                "required_for_current_claims": True,
                "locator": {"kind": "file", "path": "result"},
                "dependencies": [{"id": "input", "expected_sha256": source_digest}],
                "expected_sha256": result_digest,
            },
        ],
    }


class ArtifactGraphTests(unittest.TestCase):
    def test_current_graph_passes_gate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            graph = graph_for(root)
            require_current(graph, root)
            self.assertEqual(evaluate_graph(graph, root)["report"]["state"], "CURRENT")

    def test_changed_dependency_marks_report_stale(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            graph = graph_for(root)
            (root / "source").write_text("changed", encoding="utf-8")
            statuses = evaluate_graph(graph, root)
            self.assertEqual(statuses["input"]["state"], "STALE")
            self.assertEqual(statuses["report"]["state"], "STALE")
            with self.assertRaises(RuntimeError):
                require_current(graph, root, ["report"], dependencies_only=True)

    def test_missing_dependency_marks_report_missing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            graph = graph_for(root)
            (root / "source").unlink()
            statuses = evaluate_graph(graph, root)
            self.assertEqual(statuses["input"]["state"], "MISSING")
            self.assertEqual(statuses["report"]["state"], "MISSING")

    def test_bad_pinned_dependency_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            graph = graph_for(Path(directory))
            graph["nodes"][1]["dependencies"][0]["expected_sha256"] = "0" * 64
            with self.assertRaises(ValueError):
                evaluate_graph(graph, Path(directory))

    def test_project_graph_invalidation_contracts(self) -> None:
        path = ROOT / "results" / "artifacts" / "graph.json"
        if not path.exists():
            self.skipTest("project artifact graph has not been attested")
        graph = load_graph(path)
        cases = {
            "validator:nanoda": {"coverage:local-payload", "run:mutation-batch-semantic-0001", "report:milestone3-assurance"},
            "corpus:arena-materialized": {"coverage:local-payload", "run:mutation-batch-semantic-0001", "report:milestone3-assurance"},
            "mutation-model:nanoda": {"mutation-spec:catalog", "run:mutation-batch-semantic-0001", "report:mutation-summary"},
            "input:expected-semantics-0003": {"classification:regression-0003", "run:augmented-0003", "report:milestone1-assurance"},
        }
        for changed, expected in cases.items():
            override = hashlib.sha256(f"changed:{changed}".encode()).hexdigest()
            statuses = evaluate_graph(graph, ROOT, {changed: override})
            stale = {node_id for node_id, status in statuses.items() if status["effective_state"] != "CURRENT"}
            self.assertTrue(expected <= stale, (changed, expected - stale))


if __name__ == "__main__":
    unittest.main()
