from __future__ import annotations

import importlib.machinery
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit-mutation-surface"
loader = importlib.machinery.SourceFileLoader("mutation_surface_audit", str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
module = importlib.util.module_from_spec(spec)
loader.exec_module(module)

GENERATOR = ROOT / "scripts" / "generate-mutations"
generator_loader = importlib.machinery.SourceFileLoader("generate_mutations", str(GENERATOR))
generator_spec = importlib.util.spec_from_loader(generator_loader.name, generator_loader)
generator = importlib.util.module_from_spec(generator_spec)
generator_loader.exec_module(generator)

SCHEDULER = ROOT / "scripts" / "schedule-mutant"
scheduler_loader = importlib.machinery.SourceFileLoader("schedule_mutant", str(SCHEDULER))
scheduler_spec = importlib.util.spec_from_loader(scheduler_loader.name, scheduler_loader)
scheduler = importlib.util.module_from_spec(scheduler_spec)
scheduler_loader.exec_module(scheduler)

CLASSIFIER = ROOT / "scripts" / "classify-nat-extension-survivors"
classifier_loader = importlib.machinery.SourceFileLoader("nat_survivors", str(CLASSIFIER))
classifier_spec = importlib.util.spec_from_loader(classifier_loader.name, classifier_loader)
classifier = importlib.util.module_from_spec(classifier_spec)
classifier_loader.exec_module(classifier)

QUOT_CLASSIFIER = ROOT / "scripts" / "classify-quot-ind-survivor"
quot_loader = importlib.machinery.SourceFileLoader("quot_survivor", str(QUOT_CLASSIFIER))
quot_spec = importlib.util.spec_from_loader(quot_loader.name, quot_loader)
quot_classifier = importlib.util.module_from_spec(quot_spec)
quot_loader.exec_module(quot_classifier)

CTOR_CLASSIFIER = ROOT / "scripts" / "classify-constructor-owner-survivor"
ctor_loader = importlib.machinery.SourceFileLoader("ctor_survivor", str(CTOR_CLASSIFIER))
ctor_spec = importlib.util.spec_from_loader(ctor_loader.name, ctor_loader)
ctor_classifier = importlib.util.module_from_spec(ctor_spec)
ctor_loader.exec_module(ctor_classifier)

REPORT = ROOT / "scripts" / "report"
report_loader = importlib.machinery.SourceFileLoader("mutation_report", str(REPORT))
report_spec = importlib.util.spec_from_loader(report_loader.name, report_loader)
mutation_report = importlib.util.module_from_spec(report_spec)
report_loader.exec_module(mutation_report)


class MutationSurfaceAuditTests(unittest.TestCase):
    def test_reference_aligned_mutants_are_excluded_from_scores(self) -> None:
        self.assertIn("REFERENCE_ALIGNED", mutation_report.EXCLUDED_CLASSIFICATIONS)

    def test_quot_ind_classification_requires_explicit_probe(self) -> None:
        spec = {
            "function": "reduce_quot",
            "mutation_operator": "REL_EQ_TO_NE",
            "original": "c_name == cache.quot_ind",
        }
        comparison = {"status": "SURVIVED", "all_covering_tests_exhausted": True}
        quot_source = (
            "Quot.ind : x; @Quot A r → Prop; "
            "Quot : Π {A : Sort u}; Quot.mk : Π {A : Sort u}; "
            "Quot.lift : Π {A : Sort u}"
        )
        tc_source = (
            "if self.proof_irrel_eq(x_n, y_n) {} fn proof_irrel_eq() {} "
            "let inferred_type = tc.infer(*val, crate::tc::InferFlag::Check); "
            "let arg_type = self.infer(arg, flag); "
            "self.assert_def_eq(binder_type, arg_type);"
        )
        accepted = {
            "different": False,
            "baseline": {"normalized_outcome": "ACCEPT"},
            "mutant": {"normalized_outcome": "ACCEPT"},
        }

        passed = quot_classifier.classify(
            spec, comparison, quot_source, tc_source, accepted
        )
        failed = quot_classifier.classify(
            spec, comparison, quot_source, tc_source, {**accepted, "different": True}
        )

        self.assertEqual(passed["registry_classification"], "EQUIVALENT")
        self.assertEqual(failed["status"], "FAIL")

    def test_constructor_owner_classification_requires_all_invariants(self) -> None:
        spec = {
            "function": "check_declar",
            "mutation_operator": "SKIP_VALIDATION",
            "original": "assert!(self.declars.get(&ctor_data.inductive_name).is_some());",
        }
        comparison = {"status": "SURVIVED", "all_covering_tests_exhausted": True}
        parser_source = (
            "for IndInfo { self.declars.insert(name, inductive); } "
            "for Constructor { self.declars.insert(name, ctor); }"
        )
        inductive_source = (
            "inductive_name: inductive.name; env_ext.insert(ctor.name, d); "
            "assert!(old_ctor.aux_data_ck(&new_ctor));"
        )
        env_source = "self.inductive_name == other.inductive_name"
        search = {"status": "NO_WITNESS_FOUND", "attempts": 300}
        attempts = [
            {
                "different": False,
                "transformation": "record-1:induct:increment:inductive.ctors.0.induct",
                "baseline_outcome": "REJECT",
                "mutant_outcome": "REJECT",
            }
            for _ in range(300)
        ]

        passed = ctor_classifier.classify(
            spec, comparison, parser_source, inductive_source, env_source, search, attempts
        )
        failed = ctor_classifier.classify(
            spec, comparison, parser_source, inductive_source.replace(
                "inductive_name: inductive.name", "inductive_name: serialized"
            ), env_source, search, attempts
        )

        self.assertEqual(passed["registry_classification"], "EQUIVALENT")
        self.assertEqual(failed["status"], "FAIL")

    def test_nat_extension_classification_fails_closed(self) -> None:
        spec = {
            "mutation_operator": "SKIP_VALIDATION",
            "original": "assert!(self.ctx.export_file.config.nat_extension);",
            "function": "infer",
        }
        comparison = {
            "status": "SURVIVED",
            "reason": "ALL_COVERING_TESTS_MATCH",
            "all_covering_tests_exhausted": True,
        }
        parser_source = (
            "if !self.config.nat_extension { "
            "Nat lit extension disallowed by checker execution config }"
        )
        util_source = (
            "pub fn mk_nat_lit() { if !self.export_file.config.nat_extension { return None } "
            "Some(self.alloc_expr(Expr::NatLit { })) }"
        )

        passed = classifier.classify(
            {"nat_extension": True}, parser_source, util_source,
            [{"spec": spec, "comparison": comparison}],
        )
        failed = classifier.classify(
            {"nat_extension": False}, parser_source, util_source,
            [{"spec": spec, "comparison": comparison}],
        )

        self.assertEqual(passed["registry_classification"], "EQUIVALENT")
        self.assertEqual(failed["status"], "FAIL")

    def test_diversity_selection_spreads_subsystems_then_functions(self) -> None:
        def candidate(name: str, subsystem: str, function: str, family: str, seconds: int) -> dict:
            return {
                "id": name, "subsystem": subsystem, "function": function, "family": family,
                "estimated_seconds": seconds, "source_file": "src/a.rs", "line_start": seconds,
                "column_start": 0, "operator": name,
            }

        eligible = [
            candidate("a1", "a", "f1", "one", 1),
            candidate("a2", "a", "f1", "two", 2),
            candidate("a3", "a", "f2", "one", 3),
            candidate("b1", "b", "g1", "one", 4),
        ]

        selected = generator.select_semantic_diversity(eligible, 3)

        self.assertEqual({row["subsystem"] for row in selected[:2]}, {"a", "b"})
        self.assertEqual({row["function"] for row in selected}, {"f1", "f2", "g1"})

    def test_instantiation_and_abstraction_are_modeled_as_substitution(self) -> None:
        for function in ("inst_aux", "abstr_aux", "abstr_aux_levels"):
            self.assertEqual(
                generator.infer_subsystem("src/expr.rs", function, "unknown"),
                "substitution-lifting",
            )
            self.assertTrue(generator.is_modeled_function("src/expr.rs", function))

    def test_debug_only_strong_reduce_is_not_in_modeled_surface(self) -> None:
        self.assertFalse(generator.is_modeled_function("src/tc.rs", "strong_reduce"))

    def test_scheduler_falls_back_to_full_baseline_without_coverage_inputs(self) -> None:
        baseline = {
            "slow": {"wall_time": 2.0, "outcome": "ACCEPT"},
            "fast": {"wall_time": 1.0, "outcome": "REJECT"},
        }

        covered, tests, policy = scheduler.select_tests(
            ["src/tc.rs:130"], {}, baseline
        )

        self.assertEqual(covered, [])
        self.assertEqual(tests, ["fast", "slow"])
        self.assertEqual(policy, "FULL_BASELINE_FALLBACK")

    def test_scheduler_keeps_coverage_guided_selection_when_available(self) -> None:
        baseline = {
            "covered": {"wall_time": 2.0, "outcome": "ACCEPT"},
            "other": {"wall_time": 1.0, "outcome": "REJECT"},
        }

        covered, tests, policy = scheduler.select_tests(
            ["src/tc.rs:10"], {"src/tc.rs:10": ["covered"]}, baseline
        )

        self.assertEqual(covered, ["src/tc.rs:10"])
        self.assertEqual(tests, ["covered"])
        self.assertEqual(policy, "LINE_COVERAGE")

    def test_distinguishes_selection_and_operator_surface_gaps(self) -> None:
        batch = {
            "checker": "nanoda",
            "batch_id": "example",
            "mutants": [{"id": "selected"}],
            "attempts": [
                {
                    "id": "selected", "source_file": "src/a.rs", "function": "f",
                    "subsystem": "a", "family": "one",
                    "attempt_status": "COMPILING_SEMANTIC_MUTANT",
                    "attempt_reason": "ISOLATED_RELEASE_BUILD_PASSED",
                },
                {
                    "id": "limited", "source_file": "src/b.rs", "function": "g",
                    "subsystem": "b", "family": "one",
                    "attempt_status": "UNSUPPORTED_MUTATION_SITE",
                    "attempt_reason": "OUTSIDE_BOUNDED_BATCH_LIMIT",
                },
                {
                    "id": "uncovered", "source_file": "src/a.rs", "function": "h",
                    "subsystem": "a", "family": "one",
                    "attempt_status": "UNSUPPORTED_MUTATION_SITE",
                    "attempt_reason": "UNCOVERED_SOURCE_LOCATION",
                },
                {
                    "id": "rejected", "source_file": "src/c.rs", "function": "i",
                    "subsystem": "unknown", "family": "one",
                    "attempt_status": "REJECTED_NON_SEMANTIC",
                    "attempt_reason": "NOT_IN_A_MODELED_SEMANTIC_FUNCTION",
                },
            ],
        }
        catalog = {
            "operator_families": [{"id": "one"}],
            "subsystems": [{"id": "a"}, {"id": "b"}, {"id": "c"}],
        }

        report = module.audit(batch, catalog)

        self.assertEqual(report["totals"]["eligible_candidate_count"], 3)
        self.assertEqual(report["totals"]["operator_surface_candidate_count"], 3)
        self.assertEqual(report["totals"]["covered_eligible_candidate_count"], 2)
        self.assertEqual(report["findings"]["subsystems_missing_due_to_selection"], ["b"])
        self.assertEqual(report["findings"]["subsystems_missing_from_operator_surface"], ["c"])
        self.assertEqual(report["findings"]["uncovered_eligible_candidate_count"], 1)

    def test_repository_report_matches_active_batch(self) -> None:
        import json

        batch = json.loads(
            (ROOT / "results/mutation-batches/nanoda-semantic-0001.json").read_text()
        )
        catalog = json.loads((ROOT / "mutation-model/catalog.json").read_text())

        report = module.audit(batch, catalog)

        self.assertEqual(report["totals"]["discovered_candidate_count"], 480)
        self.assertEqual(report["totals"]["eligible_candidate_count"], 127)
        self.assertEqual(report["totals"]["selected_function_count"], 7)
        self.assertIn("quotients", report["findings"]["subsystems_missing_due_to_selection"])
        self.assertEqual(
            report["findings"]["subsystems_missing_from_operator_surface"],
            ["substitution-lifting", "bound-variables"],
        )


if __name__ == "__main__":
    unittest.main()
