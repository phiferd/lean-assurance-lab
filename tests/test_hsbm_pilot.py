"""Administrative selection regressions; no Nanoda execution or source triage."""
from importlib.machinery import SourceFileLoader
from pathlib import Path
from types import ModuleType
from unittest.mock import patch
import json
import random
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load_tool():
    module = ModuleType("hsbm_pilot_selection_test")
    SourceFileLoader(module.__name__, str(ROOT / "scripts/hsbm-pilot")).exec_module(module)
    return module


class SyntheticHistory:
    """Strict git boundary: reject changed population or descendant commands."""

    tip = "f" * 40

    def __init__(self, module, patches):
        self.module = module
        self.patches = patches
        self.calls = []
        self.exclusions = {prefix: prefix.ljust(40, "0") for prefix in module.EXCLUDED}
        self.descendants = [f"{i:040x}" for i in range(100, 115)]

    def __call__(self, repo, *args):
        self.calls.append(args)
        if args == ("merge-base", "--is-ancestor", self.module.LOWER, self.tip):
            return b""
        if args == ("rev-list", "--no-merges", f"{self.module.LOWER}..{self.tip}"):
            # Deliberately unsorted, representing all reachable branches.
            return "\n".join(reversed(list(self.patches))).encode()
        if args[:2] == ("rev-parse", self.tip):
            return self.tip.encode()
        if args == ("rev-parse", f"{self.tip}^{{tree}}"):
            return ("e" * 40).encode()
        if args[0] == "rev-parse" and args[1] in self.exclusions:
            return self.exclusions[args[1]].encode()
        if args[0] == "rev-parse" and args[1].endswith("^"):
            return ("d" * 40).encode()
        if args[:3] == ("diff", "--no-ext-diff", "--no-renames"):
            return self.patches[args[-1]].encode()
        if args[:3] == ("diff", "--numstat", "--no-renames"):
            return b"2\t1\tsrc/synthetic.rs\n"
        if args[:3] == ("show", "-s", "--format=%s"):
            return b"synthetic fixture"
        if args[:4] == ("rev-list", "--ancestry-path", "--topo-order", "--reverse"):
            assert args[4].endswith(".." + self.tip)
            assert args[4].split("..")[0] in self.patches
            return "\n".join(self.descendants).encode()
        raise AssertionError(f"Unexpected git request: {args!r}")


class HsbmPilotSelectionTests(unittest.TestCase):
    def generate(self, patches):
        module = load_tool()
        history = SyntheticHistory(module, patches)
        with patch.object(module, "git", history):
            value = module.generate(Path("synthetic-history"), history.tip)
        return value, history

    def test_population_exclusions_diversity_and_seeded_controls(self):
        ids = [f"{i:040x}" for i in range(1, 10)]
        patches = dict(zip(ids, [
            "+default parse cache",  # rank 3; first family
            "+default parse",        # rank 2; second family
            "+default cache",        # rank 2; third family
            "+default",              # skip repeated family
            "+spawn",                # available fourth family
            "+unrelated", "+unrelated", "+unrelated", "+unrelated",
        ]))
        excluded = "9c3a447".ljust(40, "0")
        patches[excluded] = "+default parse cache spawn assert test"
        value, history = self.generate(patches)
        self.assertEqual([r["commit"] for r in value["population"]], sorted(patches))
        self.assertTrue(next(r for r in value["population"] if r["commit"] == excluded)["excluded"])
        signal = [r for r in value["selected"] if r["arm"] == "SIGNAL"]
        self.assertEqual([r["commit"] for r in signal], [ids[0], ids[1], ids[2], ids[4]])
        self.assertEqual(len({r["family"] for r in signal}), 4)
        remaining = sorted(set(ids) - {r["commit"] for r in signal})
        controls = [r["commit"] for r in value["selected"] if r["arm"] == "CONTROL"]
        self.assertEqual(controls, random.Random(20260909).sample(remaining, 2))
        self.assertNotIn(excluded, [r["commit"] for r in value["selected"]])
        self.assertEqual(value["shortfall"], 0)
        for selected in value["selected"]:
            self.assertEqual(selected["descendants"], history.descendants[:10])

    def test_diff_context_and_headers_do_not_create_signals(self):
        commit = "1" * 40
        value, _ = self.generate({commit: "--- default/parse/cache\n+++ spawn/assert/test\n default parse cache spawn assert test\n+unrelated\n-test\n"})
        row = value["population"][0]
        self.assertEqual(row["score"], 1)
        self.assertEqual([name for name, hits in row["signals"].items() if hits], ["test_wiring"])
        self.assertEqual(row["changed_lines"], 3)

    def test_small_population_keeps_shortfall_and_never_duplicates(self):
        ids = [f"{i:040x}" for i in range(1, 4)]
        value, _ = self.generate({commit: "+unrelated" for commit in ids})
        self.assertEqual(value["shortfall"], 3)
        self.assertEqual([r["commit"] for r in value["selected"]], ids)
        self.assertTrue(all(r["family"] is None for r in value["selected"]))

    def test_frozen_selection_cannot_be_overwritten_and_check_rejects_drift(self):
        module = load_tool()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "selection.json"
            output.write_text('{"frozen": true}\n')
            argv = ["hsbm-pilot", "--repo", directory, "--tip", "fixed", "--output", str(output)]
            with patch.object(module, "generate", return_value={"changed": True}), patch("sys.argv", argv):
                with self.assertRaisesRegex(SystemExit, "Refusing to overwrite"):
                    module.main()
            self.assertEqual(json.loads(output.read_text()), {"frozen": True})
            with patch.object(module, "generate", return_value={"changed": True}), patch("sys.argv", argv + ["--check"]):
                with self.assertRaisesRegex(SystemExit, "population/selection mismatch"):
                    module.main()


if __name__ == "__main__":
    unittest.main()
