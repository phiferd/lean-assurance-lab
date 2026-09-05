import importlib.machinery
import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader(
    "proof_review", str(ROOT / "scripts/build-proof-parameter-contract-review")
)
spec = importlib.util.spec_from_loader(loader.name, loader)
module = importlib.util.module_from_spec(spec)
loader.exec_module(module)


class ProofParameterContractReviewTests(unittest.TestCase):
    def test_review_preserves_unresolved_authority_and_shared_scope(self):
        review = __import__("json").loads(module.build()[module.OUTPUT])
        self.assertEqual(review["authority"]["status"], "UNRESOLVED_FOR_UNIVERSAL_CONFORMANCE")
        self.assertEqual(review["arena_recommendation"]["candidate"], "either")
        paths = review["pair_structure"]["shared_expression_reachability"]
        self.assertEqual(paths["constructor_type"][-1], 11)
        self.assertEqual(paths["recursor_type"][-1], 11)
        self.assertEqual(paths["recursor_rule_rhs"][-1], 11)

    def test_drafts_disclose_shared_recursors_and_no_unsoundness(self):
        outputs = module.build()
        for name in ("kiota-proof-parameter.md", "arena-proof-parameter.md"):
            draft = outputs[module.DRAFT_ROOT + "/" + name]
            self.assertIn("shared", draft)
            self.assertNotIn("original complete recursor is retained", draft.lower())
        self.assertIn("does not allege unsoundness", outputs[module.DRAFT_ROOT + "/kiota-proof-parameter.md"])


if __name__ == "__main__":
    unittest.main()
