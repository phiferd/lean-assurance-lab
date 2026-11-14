"""Compare the separately executed initial and replay E1 phases."""

import json

from confirmation_common import HERE, IMAGE, load_manifest


def main() -> None:
    manifest = load_manifest()
    initial = json.loads((HERE / "initial/result.json").read_text())
    replay = json.loads((HERE / "replay/result.json").read_text())
    assert initial["status"] == replay["status"] == "COMPLETE_EXPECTED"
    assert initial["attributable_cells"] == replay["attributable_cells"] == 20
    first = {cell["id"]: cell for cell in initial["cells"]}
    second = {cell["id"]: cell for cell in replay["cells"]}
    assert set(first) == set(second) == {cell["id"] for cell in manifest["cases"]}
    matched = []
    for ident in sorted(first):
        left, right = first[ident], second[ident]
        for field in ("family", "checker", "input_sha256", "expected", "outcome", "declaration", "attribution", "exit_code"):
            assert left[field] == right[field], (ident, field, left[field], right[field])
        matched.append({
            "id": ident,
            "input_sha256": left["input_sha256"],
            "outcome": left["outcome"],
            "attribution": left["attribution"],
            "initial_raw_attempt": "initial/" + left["raw_attempt"],
            "replay_raw_attempt": "replay/" + right["raw_attempt"],
        })
    result = {
        "schema_version": 1,
        "item_id": manifest["item_id"],
        "evidence_class": "E1",
        "status": "SUCCESS",
        "image": IMAGE,
        "cases": 10,
        "profiles": 2,
        "initial_cells": 20,
        "replay_cells": 20,
        "attributable_cells": 40,
        "accepted_control_cells": 20,
        "rejected_negative_cells": 20,
        "reproduced_cells": len(matched),
        "cells": matched,
        "integration_recommendation": "Proceed only through the separately gated CHECKED-IMPORT-REGRESSION-PACK-1 E2 item.",
        "nonclaim": "This finite known-case reproduction does not prove either checker correct, estimate defect prevalence, or test current tips.",
    }
    (HERE / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print("PASS: all 20 bounded cell identities and attributable outcomes reproduced")


if __name__ == "__main__":
    main()
