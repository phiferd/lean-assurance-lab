import copy
import hashlib
import importlib.machinery
import importlib.util
import json
import unittest
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate-declaration-validation-catalog"


def load_module(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


module = load_module("declaration_catalog_validator", SCRIPT)
model_module = load_module(
    "declaration_characterization_model_validator",
    ROOT / "scripts" / "validate-declaration-validation-characterization-model",
)


class DeclarationValidationCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = module.load_json(module.CATALOG_PATH)
        cls.catalog_schema = module.load_json(module.CATALOG_SCHEMA_PATH)
        cls.entry_schema = module.load_json(module.ENTRY_SCHEMA_PATH)
        cls.authority = module.load_json(module.AUTHORITY_PATH)
        cls.authority_schema = module.load_json(module.AUTHORITY_SCHEMA_PATH)
        cls.decisions = module.load_json(module.DECISIONS_PATH)
        cls.decisions_schema = module.load_json(module.DECISIONS_SCHEMA_PATH)
        cls.target = module.load_json(module.TARGET_PATH)
        cls.model = module.load_json(module.MODEL_PATH)
        cls.identities_document = module.load_json(module.IDENTITY_PATH)
        cls.identities = {
            row["id"]: row for row in cls.identities_document["identities"]
        }
        cls.source_lock = module.load_json(module.SOURCE_LOCK_PATH)
        cls.evidence_lock = module.load_json(module.M7_EVIDENCE_LOCK_PATH)
        cls.current_evidence_lock = module.load_json(
            ROOT / cls.catalog["artifact_bindings"]["evidence_lock"]["path"]
        )
        cls.evidence_lock_schema = module.load_json(module.EVIDENCE_LOCK_SCHEMA_PATH)
        cls.approved_authority_sources = module.load_json(
            module.APPROVED_AUTHORITY_SOURCES_PATH
        )
        cls.approved_authority_sources_schema = module.load_json(
            module.APPROVED_AUTHORITY_SOURCES_SCHEMA_PATH
        )
        cls.current_approved_authority_sources_path = (
            ROOT / cls.catalog["artifact_bindings"]["approved_authority_sources"]["path"]
        )
        cls.current_approved_authority_sources = module.load_json(
            cls.current_approved_authority_sources_path
        )
        cls.current_approved_authority_sources_schema = module.load_json(
            module.registry_schema_path(cls.current_approved_authority_sources_path)
        )
        cls.prior_decisions = module.load_json(module.PRIOR_DECISIONS_PATH)
        cls.m7_catalog = copy.deepcopy(cls.catalog)
        cls.m7_catalog["status"] = "MILESTONE_7_INFRASTRUCTURE_ONLY"
        cls.m7_catalog["entries"] = []
        cls.m7_catalog["site_dispositions"] = []
        cls.m7_catalog["existing_evidence_dispositions"] = []
        cls.m7_catalog["identity_dispositions"] = []
        cls.m7_catalog["artifact_bindings"]["evidence_lock"] = {
            "path": str(module.M7_EVIDENCE_LOCK_PATH.relative_to(ROOT)),
            "sha256": module.sha256_file(module.M7_EVIDENCE_LOCK_PATH),
        }
        cls.m7_catalog["artifact_bindings"]["approved_authority_sources"] = {
            "path": str(module.APPROVED_AUTHORITY_SOURCES_PATH.relative_to(ROOT)),
            "sha256": module.sha256_file(module.APPROVED_AUTHORITY_SOURCES_PATH),
        }
        cls.m7_catalog["artifact_bindings"]["approved_authority_sources_schema"] = {
            "path": str(module.APPROVED_AUTHORITY_SOURCES_SCHEMA_PATH.relative_to(ROOT)),
            "sha256": module.sha256_file(module.APPROVED_AUTHORITY_SOURCES_SCHEMA_PATH),
        }
        cls.m7_catalog["completion_boundary"] = {
            "canonical_data_authoritative": True,
            "generated_report_required": True,
            "inventory_populated": False,
            "authority_assignments_created": False,
            "next_milestone": "MILESTONE_8_BUILD_FIRST_CHARACTERIZATION_INVENTORY",
        }

    def approved_authority_sources_fixture(self):
        result = copy.deepcopy(self.approved_authority_sources)
        source_path = "docs/research/DECLARATION_VALIDATION_CONTRACT_SLICE_PLAN.md"
        result["normative_documentation"] = [
            {
                "id": "APPROVED.NORMDOC.FIXTURE.SPECIFICATION",
                "document_kind": "SPECIFICATION",
                "version_or_edition": "in-memory test fixture",
                "stable_url_or_doi": "https://leanassurancelab.invalid/test-fixture",
                "authenticated_content_sha256": module.sha256_file(ROOT / source_path),
                "approval_decision": "DEC.AUTHORITY_SOURCE.FIXTURE",
            }
        ]
        return result

    def successor_evidence_lock(self):
        result = copy.deepcopy(self.evidence_lock)
        result["lock_id"] = "ordinary-declaration-validation.evidence-lock.test-m8.v1"
        result["sequence"] = 2
        result["status"] = "MILESTONE_8_EVIDENCE_SELECTION"
        result["predecessor"] = {
            "kind": "EVIDENCE_LOCK",
            "path": str(module.M7_EVIDENCE_LOCK_PATH.relative_to(ROOT)),
            "sha256": module.sha256_file(module.M7_EVIDENCE_LOCK_PATH),
        }
        source_path = "docs/research/DECLARATION_VALIDATION_CONTRACT_SLICE_PLAN.md"
        result["normative_documentation"] = [
            {
                "id": "NORMDOC.FIXTURE.SPECIFICATION",
                "approved_source_id": "APPROVED.NORMDOC.FIXTURE.SPECIFICATION",
                "document_kind": "SPECIFICATION",
                "version_or_edition": "in-memory test fixture",
                "stable_url_or_doi": "https://leanassurancelab.invalid/test-fixture",
                "retrieved_path": source_path,
                "retrieved_content_sha256": module.sha256_file(ROOT / source_path),
                "section_anchor_or_page": "fixture-section",
                "claim_supported": "Schema and validator regression fixture only.",
            }
        ]
        return result

    def errors(
        self,
        catalog=None,
        authority=None,
        decisions=None,
        evidence_lock=None,
        approved_authority_sources=None,
        enforce_milestone_boundary=False,
        allow_test_approved_sources=True,
    ):
        catalog_value = copy.deepcopy(self.catalog if catalog is None else catalog)
        if evidence_lock is None:
            if catalog is None:
                evidence_lock = self.current_evidence_lock
            elif catalog_value["status"] == "MILESTONE_7_INFRASTRUCTURE_ONLY":
                evidence_lock = self.evidence_lock
            else:
                evidence_lock = self.successor_evidence_lock()
        if approved_authority_sources is None:
            if catalog is None:
                approved_authority_sources = self.current_approved_authority_sources
            elif catalog_value["status"] == "MILESTONE_7_INFRASTRUCTURE_ONLY":
                approved_authority_sources = self.approved_authority_sources
            else:
                approved_authority_sources = self.approved_authority_sources_fixture()
        approved_schema = (
            self.current_approved_authority_sources_schema
            if catalog is None
            else self.approved_authority_sources_schema
        )
        catalog_value["artifact_bindings"]["evidence_lock"]["sha256"] = (
            module.document_sha256(evidence_lock)
        )
        catalog_value["artifact_bindings"]["approved_authority_sources"]["sha256"] = (
            module.document_sha256(approved_authority_sources)
        )
        return module.validate_artifacts(
            catalog_value,
            self.catalog_schema,
            self.entry_schema,
            self.authority if authority is None else authority,
            self.authority_schema,
            self.decisions if decisions is None else decisions,
            self.decisions_schema,
            self.target,
            self.model,
            self.identities_document,
            self.source_lock,
            evidence_lock,
            self.evidence_lock_schema,
            approved_authority_sources,
            approved_schema,
            self.prior_decisions,
            check_generated=False,
            enforce_milestone_boundary=enforce_milestone_boundary,
            allow_test_approved_sources=allow_test_approved_sources,
        )

    def populated_catalog(self, *entries):
        catalog = copy.deepcopy(self.m7_catalog)
        catalog["status"] = "MILESTONE_8_CHARACTERIZATION_INVENTORY"
        catalog["completion_boundary"] = {
            "canonical_data_authoritative": True,
            "generated_report_required": True,
            "inventory_populated": True,
            "authority_assignments_created": True,
            "next_milestone": "MILESTONE_9_ADVERSARIAL_REVIEW",
        }
        catalog["entries"] = list(entries)
        return catalog

    def normative_wrapper(self, stable_id="DECL.THEOREM.TYPE_PROP"):
        identity = self.identities[stable_id]
        entry = model_module.normative_fixture()
        entry["id"] = stable_id
        entry["name"] = "In-memory catalog validation fixture"
        entry["authority"]["basis"]["qualification_rule"] = (
            "AUTH.NORMATIVE.ESTABLISHED.V1"
        )
        entry["statement"]["target_premise"]["statement"] = identity[
            "semantic_statement"
        ]
        entry["statement"]["applicability"][0]["statement"] = identity[
            "applicability"
        ]
        entry["evidence"][0]["source_lock"] = {
            "registry": "DECLARATION_VALIDATION_SOURCE_LOCK",
            "lock_id": "NORMDOC.FIXTURE.SPECIFICATION",
        }
        entry["evidence"][0]["exact_locator"] = {
            "kind": "DOCUMENT_SECTION",
            "value": "fixture-section",
        }
        return {
            "characterization": entry,
            "identity_denotation": module.canonical_identity_denotation(identity),
            "identity_statement_sha256": identity["statement_sha256"],
            "semantic_denotation_sha256": hashlib.sha256(
                json.dumps(
                    module.canonical_identity_denotation(identity),
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
            ).hexdigest(),
            "decision_ids": list(identity["decision_ids"]),
            "observer_vector": [
                {
                    "profile_pointer": pointer,
                    "outcome": "NOT_INSPECTED",
                    "attribution": "In-memory test fixture; no observer claim.",
                    "evidence_refs": [],
                }
                for pointer in self.catalog["observer_order"]
            ],
            "source_mappings": [],
            "arena_disposition": {
                "disposition": "NOT_INSPECTED",
                "evidence_refs": [],
                "notes": "In-memory fixture; Arena linkage not inspected.",
            },
        }

    def empirical_wrapper(self, stable_id="SCENARIO.AXIOM.SAFETY_FLAG"):
        identity = self.identities[stable_id]
        entry = model_module.empirical_fixture(self.model)
        entry["id"] = stable_id
        entry["name"] = "In-memory empirical catalog validation fixture"
        entry["authority"]["basis"]["qualification_rule"] = (
            "AUTH.EMPIRICAL.ESTABLISHED.V1"
        )
        entry["statement"]["subject_scope"] = identity["applicability"]
        entry["statement"]["precondition"][0]["statement"] = identity[
            "applicability"
        ]
        entry["statement"]["stimulus"]["statement"] = identity["semantic_statement"]
        entry["statement"]["observation_points"][0]["statement"] = (
            module.empirical_observation_statement(identity)
        )
        entry["statement"]["profile_specific_effects"][0]["outcome"] = "REJECT"
        witness = next(
            item
            for item in self.source_lock["generated_witnesses"]
            if item["id"] == "WITNESS.AXIOM_UNSAFE_FLAG_CONTROL"
        )
        control = next(item for item in entry["evidence"] if item["role"] == "CONTROL")
        control["source_lock"] = {
            "registry": "DECLARATION_VALIDATION_SOURCE_LOCK",
            "lock_id": witness["id"],
        }
        control["exact_locator"] = {
            "kind": "ARTIFACT_SHA256",
            "value": witness["artifact_sha256"],
        }
        observation = next(
            item for item in entry["evidence"] if item["role"] == "IMPLEMENTATION_OBSERVATION"
        )
        observation["source_lock"] = {
            "registry": "DECLARATION_VALIDATION_SOURCE_LOCK",
            "lock_id": "LOCAL.AXIOM_FLAG_RESULTS",
        }
        observation["exact_locator"] = {
            "kind": "JSON_POINTER",
            "value": "results/cross-validation/axiom-unsafe-flag/results.json#/validators/2/result/normalized_outcome",
            "secondary": [
                "observer_profile=/observer_profiles/lean4lean",
                "outcome=REJECT",
            ],
        }
        observations = []
        for pointer in self.catalog["observer_order"]:
            concrete = pointer == "/observer_profiles/lean4lean"
            observations.append(
                {
                    "profile_pointer": pointer,
                    "outcome": "REJECT" if concrete else "NOT_INSPECTED",
                    "attribution": "In-memory fixture observation." if concrete else "Not inspected in fixture.",
                    "evidence_refs": ["EVID.FIXTURE.OBSERVATION"] if concrete else [],
                }
            )
        return {
            "characterization": entry,
            "identity_denotation": module.canonical_identity_denotation(identity),
            "identity_statement_sha256": identity["statement_sha256"],
            "semantic_denotation_sha256": hashlib.sha256(
                json.dumps(
                    module.canonical_identity_denotation(identity),
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
            ).hexdigest(),
            "decision_ids": list(identity["decision_ids"]),
            "observer_vector": observations,
            "source_mappings": [],
            "arena_disposition": {
                "disposition": "NOT_INSPECTED",
                "evidence_refs": [],
                "notes": "In-memory fixture; Arena linkage not inspected.",
            },
        }

    def test_schemas_are_valid_and_frozen_artifacts_pass(self):
        for schema in (
            self.catalog_schema,
            self.entry_schema,
            self.authority_schema,
            self.decisions_schema,
            self.evidence_lock_schema,
            self.approved_authority_sources_schema,
        ):
            jsonschema.Draft202012Validator.check_schema(schema)
        self.assertEqual(self.errors(enforce_milestone_boundary=True), [])

    def test_gate_5_catalog_successor_is_authoritative_and_complete(self):
        self.assertEqual(self.catalog["status"], "PUBLICATION_STUDY_SENTINEL_VALIDATED")
        self.assertEqual(len(self.catalog["entries"]), 27)
        self.assertEqual(len(self.catalog["identity_dispositions"]), 30)
        self.assertEqual(len(self.catalog["site_dispositions"]), 149)
        self.assertEqual(len(self.catalog["existing_evidence_dispositions"]), 41)
        self.assertTrue(
            self.catalog["completion_boundary"]["canonical_data_authoritative"]
        )
        self.assertTrue(self.catalog["completion_boundary"]["inventory_populated"])
        self.assertEqual(
            self.catalog["completion_boundary"]["next_milestone"],
            "PUBLICATION_STUDY_GATE_6_COMPLETE_ADJUDICATION",
        )
        authority_counts = {}
        for row in self.catalog["entries"]:
            status = row["characterization"]["authority"]["status"]
            authority_counts[status] = authority_counts.get(status, 0) + 1
        self.assertEqual(authority_counts, {"ESTABLISHED": 1, "PROVISIONAL": 26})

    def current_evidence_chain(self):
        errors, chain = module.validate_evidence_lock_chain(
            self.current_evidence_lock,
            self.evidence_lock_schema,
            self.source_lock,
            check_git_tracking=False,
        )
        self.assertEqual(errors, [])
        return chain

    def evidence_disposition_errors(self, rows):
        return module.validate_existing_evidence_dispositions(
            rows,
            source_lock=self.source_lock,
            evidence_locks=self.current_evidence_chain(),
            entries=self.catalog["entries"],
        )

    def test_existing_evidence_closure_rejects_silent_omission(self):
        rows = copy.deepcopy(self.catalog["existing_evidence_dispositions"])
        rows.pop()
        self.assertTrue(
            any(
                "existing-evidence closure omits" in item
                for item in self.evidence_disposition_errors(rows)
            )
        )

    def test_existing_evidence_cannot_be_linked_to_wrong_identity(self):
        rows = copy.deepcopy(self.catalog["existing_evidence_dispositions"])
        row = next(
            item
            for item in rows
            if item["source_lock_id"] == "WITNESS.SELF_REFERENCE"
            and item["stable_identity_id"] == "SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY"
        )
        row["stable_identity_id"] = "SCENARIO.AXIOM.ADMISSION_POLICY"
        self.assertTrue(
            any(
                "not frozen as relevant to this identity" in item
                for item in self.evidence_disposition_errors(rows)
            )
        )

    def test_explicit_multi_identity_witness_is_dispositioned_for_both(self):
        rows = [
            item
            for item in self.catalog["existing_evidence_dispositions"]
            if item["source_lock_id"] == "WITNESS.SELF_REFERENCE"
        ]
        self.assertEqual(
            {item["stable_identity_id"] for item in rows},
            {
                "DECL.ENV.CURRENT_DECL_NOT_VISIBLE",
                "SCENARIO.REPLAY.CURRENT_DECL_VISIBILITY",
            },
        )
        self.assertEqual(self.evidence_disposition_errors(self.catalog["existing_evidence_dispositions"]), [])

    def test_reviewed_pilot_entries_remain_exact_historical_inputs(self):
        catalog = copy.deepcopy(self.catalog)
        pilot_entry = next(
            row
            for row in catalog["entries"]
            if row["characterization"]["id"] == "DECL.THEOREM.TYPE_PROP"
        )
        pilot_entry["characterization"]["name"] = "Mutated reviewed entry"
        self.assertTrue(
            any(
                "changes immutable reviewed-pilot bytes" in item
                for item in module.validate_reviewed_pilot_reuse(catalog)
            )
        )

    def test_six_authority_rules_cover_both_kinds_and_all_statuses(self):
        errors, rules = module.validate_rule_set(self.authority)
        self.assertEqual(errors, [])
        self.assertEqual(len(rules), 6)

    def test_report_is_deterministic_synchronized_and_content_bound(self):
        renderer = module.load_module("catalog_report_test", module.REPORT_RENDERER_PATH)
        first = renderer.render(self.catalog, self.source_lock, self.current_evidence_lock)
        self.assertEqual(
            first, renderer.render(self.catalog, self.source_lock, self.current_evidence_lock)
        )
        self.assertEqual(first, module.REPORT_PATH.read_text(encoding="utf-8"))
        self.assertIn(module.sha256_file(module.CATALOG_PATH), first)

    def test_report_contains_all_required_generated_views(self):
        report = module.REPORT_PATH.read_text(encoding="utf-8")
        for heading in (
            "Counts by Kind",
            "Counts by Layer",
            "Counts by Authority Status",
            "Counts by Lifecycle Status",
            "Checker Observation Summary",
            "Unresolved Items",
            "Source Mappings",
            "Normative Candidate Obligations",
            "Empirical Contract Scenarios",
        ):
            self.assertIn(heading, report)

    def test_historical_m7_attestation_replaces_mutable_freeze_rendering(self):
        self.assertEqual(module.validate_historical_m7_attestation(), [])

    def test_reviewed_m8_pilot_attestation_is_required_by_completion_validation(self):
        self.assertEqual(module.validate_historical_m8_pilot(), [])

    def test_corrected_milestone_8_historical_attestation_is_required(self):
        self.assertEqual(module.validate_historical_m8_attestation(), [])

    def test_milestone_8_completion_derives_evidence_observer_and_arena_counts(self):
        freeze = module.load_json(module.M8_FREEZE_PATH)
        summary = freeze["inventory_summary"]
        self.assertEqual(summary["existing_evidence_dispositions"], 41)
        self.assertEqual(summary["existing_evidence_linked"], 24)
        self.assertEqual(summary["existing_evidence_explicit_negative"], 17)
        self.assertEqual(summary["un_dispositioned_existing_evidence"], 0)
        self.assertEqual(summary["observer_outcomes_by_profile"]["official_importer"]["ACCEPT"], 1)
        self.assertEqual(summary["observer_outcomes_by_profile"]["official_importer"]["REJECT"], 7)
        self.assertEqual(summary["observer_outcomes_by_profile"]["nanoda"]["NOT_INSPECTED"], 27)
        self.assertEqual(summary["arena_dispositions"]["LINKED"], 1)

    def test_milestone_8_freeze_is_acyclic_and_binds_its_historical_catalog(self):
        freeze = module.load_json(module.M8_FREEZE_PATH)
        attestation = module.load_json(
            ROOT / "results" / "research" / "declaration-validation-milestone-8-historical.json"
        )
        self.assertEqual(module.dependency_cycle_errors(freeze["dependency_edges"]), [])
        self.assertEqual(
            freeze["artifacts"]["catalog"]["sha256"],
            attestation["artifacts"]["catalog"]["sha256"],
        )

    def test_valid_normative_fixture_satisfies_established_rule(self):
        catalog = self.populated_catalog(self.normative_wrapper())
        self.assertEqual(self.errors(catalog), [])

    def test_valid_empirical_fixture_satisfies_established_rule(self):
        catalog = self.populated_catalog(self.empirical_wrapper())
        self.assertEqual(self.errors(catalog), [])

    def test_duplicate_stable_id_fails(self):
        entry = self.normative_wrapper()
        catalog = self.populated_catalog(entry, copy.deepcopy(entry))
        self.assertTrue(any("duplicate catalog stable ID" in item for item in self.errors(catalog)))

    def test_unregistered_stable_id_fails(self):
        entry = self.normative_wrapper()
        entry["characterization"]["id"] = "DECL.UNKNOWN.FIXTURE"
        catalog = self.populated_catalog(entry)
        self.assertTrue(any("absent from the frozen identity registry" in item for item in self.errors(catalog)))

    def test_identity_statement_hash_drift_fails(self):
        entry = self.normative_wrapper()
        entry["identity_statement_sha256"] = "0" * 64
        catalog = self.populated_catalog(entry)
        self.assertTrue(any("identity statement hash is stale" in item for item in self.errors(catalog)))

    def test_unknown_decision_id_fails(self):
        entry = self.normative_wrapper()
        entry["decision_ids"] = ["DEC.UNKNOWN.001"]
        catalog = self.populated_catalog(entry)
        self.assertTrue(any("unknown decision ID" in item for item in self.errors(catalog)))

    def test_missing_lifecycle_target_fails(self):
        entry = self.normative_wrapper()
        entry["characterization"]["lifecycle"] = {
            "status": "SUPERSEDED",
            "reason": "In-memory target validation fixture.",
            "target_ids": ["DECL.VALUE.WELL_FORMED"],
        }
        catalog = self.populated_catalog(entry)
        self.assertTrue(any("lifecycle target is not a catalog entry" in item for item in self.errors(catalog)))

    def test_lifecycle_target_cycle_fails(self):
        first = self.normative_wrapper("DECL.THEOREM.TYPE_PROP")
        second = self.normative_wrapper("DECL.VALUE.WELL_FORMED")
        first["characterization"]["lifecycle"] = {
            "status": "SUPERSEDED",
            "reason": "Cycle fixture.",
            "target_ids": ["DECL.VALUE.WELL_FORMED"],
        }
        second["characterization"]["lifecycle"] = {
            "status": "SUPERSEDED",
            "reason": "Cycle fixture.",
            "target_ids": ["DECL.THEOREM.TYPE_PROP"],
        }
        catalog = self.populated_catalog(first, second)
        self.assertTrue(any("lifecycle target cycle" in item for item in self.errors(catalog)))

    def test_incomplete_observer_vector_fails(self):
        entry = self.normative_wrapper()
        entry["observer_vector"].pop()
        catalog = self.populated_catalog(entry)
        self.assertTrue(any("observer_vector" in item for item in self.errors(catalog)))

    def test_concrete_observer_outcome_requires_evidence(self):
        entry = self.normative_wrapper()
        entry["observer_vector"][0]["outcome"] = "REJECT"
        catalog = self.populated_catalog(entry)
        self.assertTrue(any("concrete observer outcome lacks evidence" in item for item in self.errors(catalog)))

    def test_unknown_source_mapping_fails(self):
        entry = self.normative_wrapper()
        entry["source_mappings"] = [
            {
                "implementation": "LOGICAL_TARGET",
                "source_file_id": "SRC.UNKNOWN.FILE",
                "symbol_or_range": "fixture",
                "role": "ENFORCEMENT",
                "evidence_refs": ["EVID.FIXTURE.NORMATIVE"],
            }
        ]
        catalog = self.populated_catalog(entry)
        self.assertTrue(any("unknown mapped source file" in item for item in self.errors(catalog)))

    def test_unresolved_evidence_reference_fails(self):
        entry = self.normative_wrapper()
        entry["observer_vector"][0]["outcome"] = "REJECT"
        entry["observer_vector"][0]["evidence_refs"] = ["EVID.UNKNOWN.REFERENCE"]
        catalog = self.populated_catalog(entry)
        self.assertTrue(any("unresolved evidence refs" in item for item in self.errors(catalog)))

    def test_unknown_source_lock_reference_fails(self):
        entry = self.normative_wrapper()
        entry["characterization"]["evidence"][0]["source_lock"] = {
            "registry": "DECLARATION_VALIDATION_SOURCE_LOCK",
            "lock_id": "LOCAL.DOES_NOT_EXIST",
        }
        catalog = self.populated_catalog(entry)
        self.assertTrue(any("unknown source-lock id" in item for item in self.errors(catalog)))

    def test_invalid_claim_pointer_fails(self):
        entry = self.normative_wrapper()
        entry["characterization"]["evidence"][0]["claim_supported"][
            "entry_json_pointer"
        ] = "/does/not/exist"
        catalog = self.populated_catalog(entry)
        self.assertTrue(any("claim JSON Pointer does not resolve" in item for item in self.errors(catalog)))

    def test_tracked_evidence_descendant_json_pointer_resolves(self):
        evidence = copy.deepcopy(self.normative_wrapper()["characterization"]["evidence"][0])
        evidence["role"] = "DISCOVERY"
        evidence["source_type"] = "LAB_EXPERIMENT"
        evidence["source_lock"] = {
            "registry": "DECLARATION_VALIDATION_SOURCE_LOCK",
            "lock_id": "LOCAL.CORE_DECL_MATRIX",
        }
        evidence["exact_locator"] = {
            "kind": "JSON_POINTER",
            "value": "results/investigations/nanoda-core-declaration-contract-matrix.json#/cases/0",
        }
        self.assertEqual(
            module.evidence_source_errors(
                evidence,
                self.target,
                self.source_lock,
                [self.evidence_lock],
                self.approved_authority_sources,
            ), []
        )

    def test_unknown_case_id_fails_source_lock_resolution(self):
        evidence = copy.deepcopy(self.normative_wrapper()["characterization"]["evidence"][0])
        evidence["role"] = "DISCOVERY"
        evidence["source_type"] = "LAB_EXPERIMENT"
        evidence["source_lock"] = {
            "registry": "DECLARATION_VALIDATION_SOURCE_LOCK",
            "lock_id": "LOCAL.CORE_DECL_MATRIX",
        }
        evidence["exact_locator"] = {
            "kind": "CASE_ID",
            "value": "case-that-does-not-exist",
        }
        self.assertTrue(
            any(
                "case ID does not resolve" in item
                for item in module.evidence_source_errors(
                    evidence,
                    self.target,
                    self.source_lock,
                    [self.evidence_lock],
                    self.approved_authority_sources,
                )
            )
        )

    def test_implementation_observation_cannot_establish_normativity(self):
        entry = self.normative_wrapper()
        evidence = entry["characterization"]["evidence"][0]
        evidence["role"] = "IMPLEMENTATION_OBSERVATION"
        evidence["source_type"] = "IMPLEMENTATION_SOURCE"
        evidence["lineage"] = {
            "group": "FIXTURE_IMPLEMENTATION",
            "relationship_to_target": "DISTINCT_CODEBASE",
            "independence_scope": "DISTINCT_LINEAGE_ONLY",
            "basis": "In-memory fixture only.",
        }
        catalog = self.populated_catalog(entry)
        self.assertTrue(any("lacks NORMATIVE_SUPPORT" in item for item in self.errors(catalog)))

    def test_unresolved_authority_requires_durable_blocker(self):
        entry = self.normative_wrapper()
        authority = entry["characterization"]["authority"]
        authority["status"] = "UNRESOLVED"
        authority["basis"]["qualification_rule"] = "AUTH.NORMATIVE.UNRESOLVED.V1"
        authority["basis"]["unmet_requirements"] = ["Fixture missing authority resolution."]
        catalog = self.populated_catalog(entry)
        self.assertTrue(any("lacks a blocking unknown or contradiction" in item for item in self.errors(catalog)))

    def test_established_empirical_authority_requires_concrete_observation(self):
        entry = self.empirical_wrapper()
        for observation in entry["observer_vector"]:
            observation["outcome"] = "NOT_INSPECTED"
            observation["evidence_refs"] = []
        entry["characterization"]["statement"]["profile_specific_effects"][0][
            "outcome"
        ] = "NOT_INSPECTED"
        catalog = self.populated_catalog(entry)
        self.assertTrue(any("has no concrete observer outcome" in item for item in self.errors(catalog)))

    def test_dynamic_report_is_derived_from_catalog_entry(self):
        entry = self.normative_wrapper()
        catalog = self.populated_catalog(entry)
        renderer = module.load_module("catalog_dynamic_report_test", module.REPORT_RENDERER_PATH)
        report = renderer.render(catalog, self.source_lock, self.successor_evidence_lock())
        self.assertIn("DECL.THEOREM.TYPE_PROP", report)
        self.assertIn("| NORMATIVE_CANDIDATE_OBLIGATION | 1 |", report)

    def test_semantic_target_profile_cannot_establish_normativity(self):
        entry = self.normative_wrapper()
        evidence = entry["characterization"]["evidence"][0]
        evidence["source_lock"] = {
            "registry": "SEMANTIC_TARGET_PROFILE",
            "lock_id": self.target["profile_id"],
        }
        evidence["exact_locator"] = {
            "kind": "DOCUMENT_SECTION",
            "value": "/logical_target/modeled_judgment",
        }
        errors = self.errors(self.populated_catalog(entry))
        self.assertTrue(
            any("semantic-target profile cannot serve as normative support" in item for item in errors)
        )

    def test_source_type_must_match_locked_record_kind(self):
        entry = self.normative_wrapper()
        evidence = entry["characterization"]["evidence"][0]
        evidence["source_lock"] = {
            "registry": "DECLARATION_VALIDATION_SOURCE_LOCK",
            "lock_id": "SRC.NANODA.TC",
        }
        evidence["exact_locator"] = {"kind": "SOURCE_SYMBOL", "value": "check_declar"}
        errors = self.errors(self.populated_catalog(entry))
        self.assertTrue(any("incompatible with locked record kind source_file" in item for item in errors))

    def test_unqualified_other_evidence_cannot_establish_empirical_authority(self):
        entry = self.empirical_wrapper()
        evidence = next(
            item
            for item in entry["characterization"]["evidence"]
            if item["role"] == "IMPLEMENTATION_OBSERVATION"
        )
        evidence["source_type"] = "OTHER"
        errors = self.errors(self.populated_catalog(entry))
        self.assertTrue(
            any("role/source-type combination is not qualified" in item for item in errors)
        )
        self.assertTrue(any("OTHER/LLM-like evidence" in item for item in errors))

    def test_established_normative_support_rejects_unresolved_assumptions(self):
        entry = self.normative_wrapper()
        entry["characterization"]["evidence"][0]["assumptions"] = [
            {
                "id": "ASSUMPTION.FIXTURE.UNRESOLVED",
                "statement": "A required target relationship remains unresolved.",
                "status": "UNRESOLVED",
            }
        ]
        errors = self.errors(self.populated_catalog(entry))
        self.assertTrue(any("unresolved assumptions" in item for item in errors))

    def test_established_normative_support_rejects_active_assumptions(self):
        entry = self.normative_wrapper()
        entry["characterization"]["evidence"][0]["assumptions"] = [
            {
                "id": "ASSUMPTION.FIXTURE.ACTIVE",
                "statement": "The formal model-to-target relationship is assumed.",
                "status": "ACTIVE",
            }
        ]
        errors = self.errors(self.populated_catalog(entry))
        self.assertTrue(any("has active assumptions" in item for item in errors))

    def test_active_statement_contradiction_blocks_established_authority(self):
        entry = self.normative_wrapper()
        contradiction = copy.deepcopy(entry["characterization"]["evidence"][0])
        contradiction.update(
            {
                "id": "EVID.FIXTURE.CONTRADICTION",
                "role": "CONTRADICTION",
                "claim_supported": {
                    "entry_json_pointer": "/statement/target_premise",
                    "predicate_id": "CLAIM.FIXTURE.CONTRADICTION",
                    "proposition": "The fixture contradicts the target premise.",
                },
            }
        )
        entry["characterization"]["evidence"].append(contradiction)
        errors = self.errors(self.populated_catalog(entry))
        self.assertTrue(any("active statement contradiction" in item for item in errors))

    def test_checker_disagreement_does_not_block_independently_qualified_normative_authority(self):
        entry = self.normative_wrapper()
        observation = copy.deepcopy(entry["characterization"]["evidence"][0])
        observation.update(
            {
                "id": "EVID.FIXTURE.CHECKER_DIFFERENCE",
                "role": "IMPLEMENTATION_OBSERVATION",
                "source_type": "CHECKER_RESULT",
                "source_lock": {
                    "registry": "DECLARATION_VALIDATION_SOURCE_LOCK",
                    "lock_id": "LOCAL.NONPROP_RESULTS",
                },
                "exact_locator": {
                    "kind": "JSON_POINTER",
                    "value": "results/cross-validation/m6-nonprop-theorem/results.json#/validators/2/result/normalized_outcome",
                },
                "claim_supported": {
                    "entry_json_pointer": "/statement",
                    "predicate_id": "CLAIM.FIXTURE.CHECKER_DIFFERENCE",
                    "proposition": "A checker result differs from another implementation outcome.",
                },
                "assumptions": [],
                "lineage": {
                    "group": "FIXTURE_DISTINCT_CHECKER",
                    "relationship_to_target": "DISTINCT_CODEBASE",
                    "independence_scope": "DISTINCT_LINEAGE_ONLY",
                    "basis": "Synthetic checker disagreement fixture.",
                },
            }
        )
        entry["characterization"]["evidence"].append(observation)
        errors = self.errors(self.populated_catalog(entry))
        self.assertEqual(errors, [])

    def test_soundness_claims_are_blocked_until_separately_qualified(self):
        entry = self.normative_wrapper()
        entry["characterization"]["soundness_relevance"] = {
            "status": "DIRECT_LOGICAL_SOUNDNESS_RELEVANCE_ESTABLISHED",
            "basis_evidence_refs": ["EVID.FIXTURE.NORMATIVE"],
            "statement": "Unsupported direct soundness claim.",
        }
        errors = self.errors(self.populated_catalog(entry))
        self.assertTrue(any("must remain NOT_ASSESSED" in item for item in errors))

    def test_locally_forged_normative_document_cannot_establish_authority(self):
        entry = self.normative_wrapper()
        evidence = entry["characterization"]["evidence"][0]
        evidence["source_lock"]["lock_id"] = "NORMDOC.FORGED.TEST"
        evidence["exact_locator"]["value"] = "invented-section"
        evidence_lock = self.successor_evidence_lock()
        invented_path = "tests/fixtures/declaration-validation/invented-specification.md"
        self.assertTrue(module.is_tracked(invented_path))
        evidence_lock["normative_documentation"] = [
            {
                "id": "NORMDOC.FORGED.TEST",
                "approved_source_id": "APPROVED.NORMDOC.FORGED.TEST",
                "document_kind": "SPECIFICATION",
                "version_or_edition": "plausible invented edition",
                "stable_url_or_doi": "https://lean-lang.org/forged-specification",
                "retrieved_path": invented_path,
                "retrieved_content_sha256": module.sha256_file(ROOT / invented_path),
                "section_anchor_or_page": "invented-section",
                "claim_supported": "Lean requires arbitrary predicate X.",
            }
        ]
        errors = self.errors(
            self.populated_catalog(entry), evidence_lock=evidence_lock
        )
        self.assertTrue(
            any("absent from the frozen approved authority-source registry" in item for item in errors)
        )

    def test_catalog_adjudication_cannot_extend_frozen_approved_source_registry(self):
        approved_sources = self.approved_authority_sources_fixture()
        errors = self.errors(
            self.populated_catalog(self.normative_wrapper()),
            approved_authority_sources=approved_sources,
            allow_test_approved_sources=False,
        )
        self.assertTrue(
            any("cannot extend the frozen pre-M8 approved" in item for item in errors)
        )

    def test_successor_registry_cannot_self_approve_a_source(self):
        root_path = module.APPROVED_AUTHORITY_SOURCES_PATH
        successor = {
            "schema_version": 1,
            "registry_id": "ordinary-declaration-validation.approved-authority-sources.test.v2",
            "sequence": 2,
            "recorded_at": "2026-08-31T08:00:00-04:00",
            "status": "FROZEN_VERSIONED_APPROVED_AUTHORITY_SOURCES",
            "predecessor": {
                "path": "config/declaration-validation-approved-authority-sources.json",
                "sha256": module.sha256_file(root_path),
                "registry_id": "ordinary-declaration-validation.approved-authority-sources.m7.v1",
                "sequence": 1,
            },
            "approval_decision_bindings": [],
            "normative_documentation": [
                {
                    "id": "APPROVED.NORMDOC.TEST.V2",
                    "document_kind": "SPECIFICATION",
                    "version_or_edition": "test",
                    "stable_url_or_doi": "https://example.invalid/test",
                    "authenticated_content_sha256": "0" * 64,
                    "approval_decision": "DEC.AUTHORITY_SOURCE.TEST.V2",
                }
            ],
            "mechanized_results": [],
            "change_control": {
                "catalog_adjudication_may_extend_registry": False,
                "extension_requires": "SEPARATE_EXPLICIT_AUTHORITY_SOURCE_DECISION_BEFORE_CATALOG_ADJUDICATION",
                "new_version_required": True,
            },
            "nonclaims": [
                "Synthetic test fixture only.",
                "The registry is not a catalog adjudication.",
                "No source is actually approved by this test.",
            ],
        }
        errors = module.validate_approved_authority_source_registry(
            successor,
            module.load_json(module.APPROVED_AUTHORITY_SOURCES_SUCCESSOR_SCHEMA_PATH),
            ROOT / "config/declaration-validation-approved-authority-sources/test-v2.json",
            check_generated=False,
        )
        self.assertTrue(any("lacks a separate predecessor-bound approval decision" in item for item in errors))

    def test_locally_forged_authoritative_document_cannot_establish_authority(self):
        entry = self.normative_wrapper()
        evidence = entry["characterization"]["evidence"][0]
        evidence["source_type"] = "AUTHORITATIVE_DOCUMENTATION"
        evidence["source_lock"]["lock_id"] = "NORMDOC.FORGED.AUTHORITATIVE"
        evidence["exact_locator"]["value"] = "invented-section"
        evidence_lock = self.successor_evidence_lock()
        invented_path = "tests/fixtures/declaration-validation/invented-specification.md"
        evidence_lock["normative_documentation"] = [
            {
                "id": "NORMDOC.FORGED.AUTHORITATIVE",
                "approved_source_id": "APPROVED.NORMDOC.FORGED.AUTHORITATIVE",
                "document_kind": "AUTHORITATIVE_DOCUMENTATION",
                "version_or_edition": "plausible invented edition",
                "stable_url_or_doi": "https://lean-lang.org/forged-documentation",
                "retrieved_path": invented_path,
                "retrieved_content_sha256": module.sha256_file(ROOT / invented_path),
                "section_anchor_or_page": "invented-section",
                "claim_supported": "Lean requires arbitrary predicate X.",
            }
        ]
        errors = self.errors(
            self.populated_catalog(entry), evidence_lock=evidence_lock
        )
        self.assertTrue(
            any("absent from the frozen approved authority-source registry" in item for item in errors)
        )

    def test_locally_forged_formal_mechanization_cannot_establish_authority(self):
        entry = self.normative_wrapper()
        evidence = entry["characterization"]["evidence"][0]
        evidence["source_type"] = "FORMAL_MECHANIZATION"
        evidence["source_lock"]["lock_id"] = "MECH.FORGED.TEST"
        evidence["exact_locator"] = {
            "kind": "THEOREM_OR_DEFINITION",
            "value": "forged_theorem",
        }
        evidence["lineage"] = {
            "group": "FORGED_LOCAL",
            "relationship_to_target": "NON_IMPLEMENTATION_SOURCE",
            "independence_scope": "NOT_APPLICABLE",
            "basis": "Self-asserted fixture lineage.",
        }
        evidence["mechanized_result"] = {
            "theorem_or_definition": "forged_theorem",
            "relevant_assumptions_or_axioms": [],
            "relationship_to_modeled_judgment": "Self-asserted mapping.",
            "check_command": "true",
            "unchecked_command_reason": None,
        }
        evidence_lock = self.successor_evidence_lock()
        evidence_lock["normative_documentation"] = []
        invented_path = "tests/fixtures/declaration-validation/invented-specification.md"
        digest = module.sha256_file(ROOT / invented_path)
        evidence_lock["mechanized_results"] = [
            {
                "id": "MECH.FORGED.TEST",
                "approved_source_id": "APPROVED.MECH.FORGED.TEST",
                "repository_url": "https://github.com/leanprover/lean4",
                "revision": "0" * 40,
                "module": "Forged",
                "theorem_or_definition": "forged_theorem",
                "path": "Forged.lean",
                "blob_sha256": digest,
                "retrieved_path": invented_path,
                "retrieved_content_sha256": digest,
                "assumptions_or_axioms": [],
                "verification_command": "true",
                "target_judgment_mapping": "Self-asserted mapping.",
            }
        ]
        errors = self.errors(
            self.populated_catalog(entry), evidence_lock=evidence_lock
        )
        self.assertTrue(
            any("absent from the frozen approved authority-source registry" in item for item in errors)
        )

    def test_checker_outcome_cannot_be_forged_by_secondary_metadata(self):
        entry = self.empirical_wrapper()
        evidence = next(
            item
            for item in entry["characterization"]["evidence"]
            if item["role"] == "IMPLEMENTATION_OBSERVATION"
        )
        evidence["source_lock"]["lock_id"] = "LOCAL.SELF_REFERENCE_RESULTS"
        evidence["exact_locator"] = {
            "kind": "JSON_POINTER",
            "value": "results/cross-validation/nanoda-gen-8317efea2c7d-self-reference/results.json#/validators/1/result/normalized_outcome",
            "secondary": [
                "observer_profile=/observer_profiles/kiota",
                "outcome=REJECT",
            ],
        }
        extracted = module.checker_observation_from_evidence(
            evidence, self.source_lock, [self.evidence_lock]
        )
        self.assertEqual(extracted["checker"], "kiota")
        self.assertEqual(extracted["outcome"], "ACCEPT")
        for observation in entry["observer_vector"]:
            concrete = observation["profile_pointer"] == "/observer_profiles/kiota"
            observation["outcome"] = "REJECT" if concrete else "NOT_INSPECTED"
            observation["evidence_refs"] = [evidence["id"]] if concrete else []
        entry["characterization"]["statement"]["profile_specific_effects"] = [
            {
                "observer_profile_pointer": "/observer_profiles/kiota",
                "outcome": "REJECT",
                "attribution": "Forged opposite of the content-bound ACCEPT result.",
            }
        ]
        errors = self.errors(self.populated_catalog(entry))
        self.assertTrue(any("profile/outcome-bound checker evidence" in item for item in errors))

    def test_checker_outcome_cannot_be_forged_through_case_id_locator(self):
        entry = self.empirical_wrapper()
        evidence = next(
            item
            for item in entry["characterization"]["evidence"]
            if item["role"] == "IMPLEMENTATION_OBSERVATION"
        )
        evidence["source_lock"]["lock_id"] = "LOCAL.SELF_REFERENCE_RESULTS"
        evidence["exact_locator"] = {
            "kind": "CASE_ID",
            "value": "nanoda-gen-8317efea2c7d-self-reference",
            "secondary": [
                "observer_profile=/observer_profiles/kiota",
                "outcome=REJECT",
            ],
        }
        for observation in entry["observer_vector"]:
            concrete = observation["profile_pointer"] == "/observer_profiles/kiota"
            observation["outcome"] = "REJECT" if concrete else "NOT_INSPECTED"
            observation["evidence_refs"] = [evidence["id"]] if concrete else []
        entry["characterization"]["statement"]["profile_specific_effects"] = [
            {
                "observer_profile_pointer": "/observer_profiles/kiota",
                "outcome": "REJECT",
                "attribution": "Free-form case locator cannot establish an outcome.",
            }
        ]
        errors = self.errors(self.populated_catalog(entry))
        self.assertTrue(any("profile/outcome-bound checker evidence" in item for item in errors))

    def test_stable_identity_rejects_applicability_or_premise_drift(self):
        entry = self.normative_wrapper()
        entry["characterization"]["statement"]["applicability"].append(
            {"id": "PRED.FORGED.NAME_FOO", "statement": "The theorem name is Foo."}
        )
        errors = self.errors(self.populated_catalog(entry))
        self.assertTrue(any("applicability narrows or widens" in item for item in errors))

        entry = self.normative_wrapper()
        entry["characterization"]["statement"]["premises"].append(
            {"id": "PRED.FORGED.UNRELATED", "statement": "Unrelated predicate P holds."}
        )
        errors = self.errors(self.populated_catalog(entry))
        self.assertTrue(any("additional normative premises" in item for item in errors))

    def test_stable_identity_rejects_modeled_judgment_drift(self):
        entry = self.normative_wrapper()
        entry["characterization"]["statement"]["judgment"][
            "target_profile_pointer"
        ] = "/logical_target/target_id"
        errors = self.errors(self.populated_catalog(entry))
        self.assertTrue(any("modeled-judgment identity changes" in item for item in errors))

    def test_empirical_stable_identity_rejects_precondition_or_observation_drift(self):
        entry = self.empirical_wrapper()
        entry["characterization"]["statement"]["precondition"].append(
            {
                "id": "PRED.FORGED.EMPIRICAL_SCOPE",
                "statement": "Only when unrelated condition P holds.",
            }
        )
        errors = self.errors(self.populated_catalog(entry))
        self.assertTrue(any("empirical precondition changes" in item for item in errors))

        entry = self.empirical_wrapper()
        entry["characterization"]["statement"]["observation_points"].append(
            {
                "id": "PRED.FORGED.OBSERVATION",
                "layer": "IMPLEMENTATION_POLICY",
                "statement": "Observe an unrelated implementation property.",
            }
        )
        errors = self.errors(self.populated_catalog(entry))
        self.assertTrue(any("empirical observation point changes" in item for item in errors))

    def test_editorial_and_observational_fields_are_not_identity_defining(self):
        entry = self.normative_wrapper()
        entry["characterization"]["name"] = "Editorially revised fixture name"
        entry["characterization"]["statement"]["judgment"]["statement"] = (
            "Editorial explanation of the same pinned judgment."
        )
        entry["characterization"]["statement"]["expected_effect"][
            "authority_scope"
        ] = "Editorial explanation of the same authority scope."
        self.assertEqual(self.errors(self.populated_catalog(entry)), [])

        empirical = self.empirical_wrapper()
        empirical["characterization"]["statement"]["profile_specific_effects"][0][
            "attribution"
        ] = "Editorially revised attribution of the same extracted outcome."
        self.assertEqual(self.errors(self.populated_catalog(empirical)), [])

    def test_stable_identity_binds_structured_semantics(self):
        entry = self.normative_wrapper()
        entry["characterization"]["statement"]["target_premise"]["statement"] = (
            "A theorem declaration type need not be proposition-valued."
        )
        errors = self.errors(self.populated_catalog(entry))
        self.assertTrue(any("target premise changes the stable semantic identity" in item for item in errors))

        entry = self.normative_wrapper()
        entry["characterization"]["statement"]["expected_effect"][
            "violation_expectation"
        ] = "ACCEPT"
        errors = self.errors(self.populated_catalog(entry))
        self.assertTrue(any("violation semantics change" in item for item in errors))

        empirical = self.empirical_wrapper()
        empirical["characterization"]["statement"]["stimulus"]["statement"] = (
            "Characterize an unrelated scenario."
        )
        errors = self.errors(self.populated_catalog(empirical))
        self.assertTrue(any("empirical stimulus changes the stable semantic identity" in item for item in errors))

    def test_secondary_observer_metadata_is_not_factual_authority(self):
        entry = self.empirical_wrapper()
        observation = next(
            item
            for item in entry["characterization"]["evidence"]
            if item["role"] == "IMPLEMENTATION_OBSERVATION"
        )
        observation["exact_locator"]["secondary"] = [
            "observer_profile=/observer_profiles/official_importer",
            "outcome=ACCEPT",
        ]
        errors = self.errors(self.populated_catalog(entry))
        self.assertEqual(errors, [])

    def test_source_mapping_must_match_implementation_repository_and_evidence(self):
        entry = self.normative_wrapper()
        implementation = copy.deepcopy(entry["characterization"]["evidence"][0])
        implementation.update(
            {
                "id": "EVID.FIXTURE.KIOTA_MAPPING",
                "role": "IMPLEMENTATION_OBSERVATION",
                "source_type": "IMPLEMENTATION_SOURCE",
                "source_lock": {
                    "registry": "DECLARATION_VALIDATION_SOURCE_LOCK",
                    "lock_id": "SRC.NANODA.TC",
                },
                "exact_locator": {"kind": "SOURCE_SYMBOL", "value": "nonexistent::symbol"},
                "lineage": {
                    "group": "NANODA",
                    "relationship_to_target": "DISTINCT_CODEBASE",
                    "independence_scope": "DISTINCT_LINEAGE_ONLY",
                    "basis": "In-memory mismatch fixture.",
                },
            }
        )
        entry["characterization"]["evidence"].append(implementation)
        entry["source_mappings"] = [
            {
                "implementation": "KIOTA",
                "source_file_id": "SRC.NANODA.TC",
                "symbol_or_range": "nonexistent::symbol",
                "role": "ENFORCEMENT",
                "evidence_refs": ["EVID.FIXTURE.KIOTA_MAPPING"],
            }
        ]
        errors = self.errors(self.populated_catalog(entry))
        self.assertTrue(any("does not belong to KIOTA" in item for item in errors))
        self.assertTrue(any("not bound by the source-lock locator" in item for item in errors))

    def test_full_m8_site_closure_rejects_an_omitted_frozen_site(self):
        entry = self.normative_wrapper()
        errors = module.validate_site_dispositions(
            [],
            stable_ids={"DECL.THEOREM.TYPE_PROP"},
            identities=self.identities,
            discovery_closure=module.load_json(module.CLOSURE_PATH),
            entries=[entry],
        )
        self.assertTrue(any("site-disposition closure omits frozen M4 site pairs" in item for item in errors))

    def test_milestone_8_requires_complete_identity_dispositions(self):
        catalog = self.populated_catalog(self.normative_wrapper())
        errors = self.errors(catalog, enforce_milestone_boundary=True)
        self.assertTrue(any("do not exactly cover the frozen discovery surface" in item for item in errors))
        self.assertTrue(any("do not exactly match identities" in item for item in errors))

    def test_reserved_out_of_scope_identity_cannot_be_active_entry(self):
        entry = self.empirical_wrapper("SCENARIO.LITERAL.AVAILABILITY_POLICY")
        errors = self.errors(self.populated_catalog(entry))
        self.assertTrue(any("reserved/deferred identity cannot be admitted" in item for item in errors))

    def test_json_pointer_resolution_is_strict_rfc6901(self):
        self.assertEqual(module.resolve_pointer({"": 7}, "/"), 7)
        with self.assertRaises(KeyError):
            module.resolve_pointer({"a": [10, 20]}, "/a/-1")
        with self.assertRaises(KeyError):
            module.resolve_pointer({"a": 1}, "/~2")

    def test_evidence_lock_successor_chain_binds_immutable_m7_root(self):
        successor = self.successor_evidence_lock()
        errors, chain = module.validate_evidence_lock_chain(
            successor,
            self.evidence_lock_schema,
            self.source_lock,
            check_git_tracking=False,
        )
        self.assertEqual(errors, [])
        self.assertEqual([item["sequence"] for item in chain], [1, 2])
        successor["predecessor"]["sha256"] = "0" * 64
        errors, _ = module.validate_evidence_lock_chain(
            successor,
            self.evidence_lock_schema,
            self.source_lock,
            check_git_tracking=False,
        )
        self.assertTrue(any("predecessor hash is stale" in item for item in errors))

    def test_report_is_status_aware_and_exposes_provisional_gap(self):
        entry = self.normative_wrapper()
        authority = entry["characterization"]["authority"]
        authority["status"] = "PROVISIONAL"
        authority["basis"]["qualification_rule"] = "AUTH.NORMATIVE.PROVISIONAL.V1"
        authority["basis"]["unmet_requirements"] = ["Independent normative source missing."]
        catalog = self.populated_catalog(entry)
        renderer = module.load_module("catalog_status_report_test", module.REPORT_RENDERER_PATH)
        report = renderer.render(catalog, self.source_lock, self.successor_evidence_lock())
        self.assertNotIn("Milestone 7 catalog is intentionally empty", report)
        self.assertIn("Independent normative source missing.", report)

    def test_decision_requires_content_bound_before_snapshot(self):
        entry = self.normative_wrapper()
        entry["decision_ids"].append("DEC.CATALOG.999")
        catalog = self.populated_catalog(entry)
        evidence_lock = self.successor_evidence_lock()
        approved_sources = self.approved_authority_sources_fixture()
        catalog["artifact_bindings"]["evidence_lock"]["sha256"] = module.document_sha256(
            evidence_lock
        )
        catalog["artifact_bindings"]["approved_authority_sources"]["sha256"] = (
            module.document_sha256(approved_sources)
        )
        statement_bytes = json.dumps(
            entry["characterization"]["statement"],
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
        statement_hash = hashlib.sha256(statement_bytes).hexdigest()
        decisions = copy.deepcopy(self.decisions)
        decisions["records"] = [
            {
                "id": "DEC.CATALOG.999",
                "decision_type": "OTHER",
                "decision": "Invalid fixture lacking a durable before snapshot.",
                "inputs": ["DECL.THEOREM.TYPE_PROP"],
                "result": ["DECL.THEOREM.TYPE_PROP"],
                "reason": "Exercise the snapshot gate.",
                "evidence": [
                    {
                        "entry_id": "DECL.THEOREM.TYPE_PROP",
                        "evidence_id": "EVID.FIXTURE.NORMATIVE",
                    }
                ],
                "catalog_snapshot_before": {
                    "path": "results/research/declaration-validation-catalog-snapshots/missing.json",
                    "sha256": "0" * 64,
                },
                "catalog_hash_before": "0" * 64,
                "catalog_hash_after": module.document_sha256(catalog),
                "statement_hashes_before": {
                    "DECL.THEOREM.TYPE_PROP": statement_hash
                },
                "statement_hashes_after": {
                    "DECL.THEOREM.TYPE_PROP": statement_hash
                },
            }
        ]
        errors = self.errors(
            catalog,
            decisions=decisions,
            evidence_lock=evidence_lock,
            approved_authority_sources=approved_sources,
        )
        self.assertTrue(any("before snapshot is missing" in item for item in errors))
        self.assertFalse(any("catalog_hash_after is not the supplied catalog" in item for item in errors))

    def test_historical_m7_attestation_rejects_missing_completion_artifact(self):
        historical = module.load_module(
            "catalog_history_test", module.HISTORICAL_VALIDATOR_PATH
        )
        attestation = historical.load_json(historical.M7_ATTESTATION_PATH)
        del attestation["artifacts"]["completion_record"]
        errors = historical.validate_m7_attestation(attestation)
        self.assertTrue(any("artifact set is not exact" in item for item in errors))


if __name__ == "__main__":
    unittest.main()
