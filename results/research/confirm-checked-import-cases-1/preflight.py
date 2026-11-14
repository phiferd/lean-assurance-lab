"""Exercise exact-image identity and host supervision without scientific inputs."""

import json
from pathlib import Path

from confirmation_common import (
    HERE, IMAGE, PINNED, assert_container_absent, container_prefix,
    docker, require_supervision, write_attempt,
)


def main() -> None:
    root = HERE / "preflight-r2"
    attempts = root / "attempts"
    attempts.mkdir(parents=True, exist_ok=False)

    verify_name = "lal-cic-preflight-identity"
    verify = write_attempt(
        attempts,
        "01-image-identity",
        container_prefix(verify_name) + [IMAGE, "sha256sum", *PINNED],
        60,
    )
    require_supervision(verify.receipt)
    assert verify.receipt["exit_code"] == 0 and verify.stderr == b""
    observed = dict(line.split(maxsplit=1)[::-1] for line in verify.stdout.decode().splitlines())
    assert observed == PINNED, (observed, PINNED)
    assert_container_absent(attempts, "02-identity-absent", verify_name)

    success_name = "lal-cic-preflight-success"
    success = write_attempt(
        attempts,
        "03-success-control",
        container_prefix(success_name) + [IMAGE, "/bin/true"],
        30,
    )
    require_supervision(success.receipt)
    assert success.receipt["exit_code"] == 0
    assert_container_absent(attempts, "04-success-absent", success_name)

    timeout_name = "lal-cic-preflight-timeout"
    timeout = write_attempt(
        attempts,
        "05-intentional-timeout",
        container_prefix(timeout_name, auto_remove=False) + [IMAGE, "/bin/sleep", "60"],
        2,
    )
    require_supervision(timeout.receipt, allow_stop="OBSERVED_TIME_LIMIT")
    cleanup = write_attempt(attempts, "06-timeout-cleanup", [docker(), "rm", "-f", timeout_name], 30)
    require_supervision(cleanup.receipt)
    assert cleanup.receipt["exit_code"] == 0
    assert_container_absent(attempts, "07-timeout-absent", timeout_name)

    result = {
        "schema_version": 1,
        "item_id": "CONFIRM-CHECKED-IMPORT-CASES-1",
        "evidence_class": "E1",
        "image": IMAGE,
        "identity_hashes": PINNED,
        "fresh_identity_container_removed": True,
        "success_control": "PASS",
        "intentional_timeout_observed": timeout.receipt["stop_reason"],
        "timeout_container_forcibly_removed": True,
        "post_cleanup_absence_verified": True,
        "scientific_inputs_observed": False,
        "verdict": "PASS",
    }
    (root / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print("PASS: exact image identity, ordinary completion, intentional timeout and forced cleanup")


if __name__ == "__main__":
    main()
