#!/usr/bin/env python3
"""Explain the retained E0 selector's zero-candidate failure without selecting alternatives."""

import importlib.machinery
import importlib.util
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
loader = importlib.machinery.SourceFileLoader("generate_mutations", str(ROOT / "scripts/generate-mutations"))
spec = importlib.util.spec_from_loader(loader.name, loader)
module = importlib.util.module_from_spec(spec)
loader.exec_module(module)

model = json.loads(module.MODEL.read_text(encoding="utf-8"))
operators = {
    operator: family["id"]
    for family in model["operator_families"]
    for operator in family["operators"]
}
existing_specs = [
    json.loads(path.read_text(encoding="utf-8"))
    for path in sorted(module.MUTATIONS.glob("*.json"))
]
existing_sites = {
    (row.get("source_file"), str(row.get("source_span", "")), row.get("original"), row.get("mutation_operator"))
    for row in existing_specs
}
manual_locations = {
    (row.get("source_file"), str(row.get("source_span")))
    for row in module.read_jsonl(module.REGISTRY)
    if not row.get("id", "").startswith("nanoda-gen-") and row.get("source_file")
}

counts = Counter()
examples = {}
total = 0
for source in sorted((module.CHECKER_ROOT / "src").rglob("*.rs")):
    source_file = str(source.relative_to(module.CHECKER_ROOT))
    for candidate in module.parse_candidates(source):
        total += 1
        span = module.source_span(candidate)
        subsystem = module.infer_subsystem(source_file, candidate.get("function"), candidate["subsystem"])
        site = (source_file, span, candidate["original"], candidate["operator"])
        if (source_file, span) in manual_locations:
            reason = "DUPLICATE_MANUAL_LOCATION"
        elif site in existing_sites:
            reason = "DUPLICATE_GENERATED_SITE"
        elif source_file in module.NON_SEMANTIC_FILES:
            reason = "NON_SEMANTIC_FILE"
        elif candidate["operator"] not in operators:
            reason = "UNSUPPORTED_OPERATOR"
        elif subsystem == "unknown" or not module.is_modeled_function(source_file, candidate.get("function")):
            reason = "NOT_MODELED_SEMANTIC_FUNCTION"
        else:
            reason = "ELIGIBLE"
        counts[reason] += 1
        examples.setdefault(reason, {
            "source_file": source_file,
            "source_span": span,
            "function": candidate.get("function"),
            "operator": candidate["operator"],
            "subsystem": subsystem,
        })

print(json.dumps({
    "schema_version": 1,
    "purpose": "diagnose the retained failed selector attempt; not a replacement sample",
    "total_parser_candidates": total,
    "classification_counts": dict(sorted(counts.items())),
    "first_example_by_classification": dict(sorted(examples.items())),
}, indent=2, sort_keys=True))
