"""Prospective resource closure around unchanged historical closure controls."""

from hashlib import sha256
from pathlib import Path
import sys

from lib import closure_controls as controls
from lib.resource_envelope_closure_receipts import validate as validate_receipts


def _binding(root: Path, path: Path) -> dict:
    raw = path.read_bytes()
    return {"path": path.relative_to(root).as_posix(), "bytes": len(raw),
            "sha256": sha256(raw).hexdigest()}


def finish(root: Path, scope_file: str, output_dir: Path) -> int:
    """Require old ordered gate, four fixture receipts, then final freshness."""
    root = root.resolve()
    output_dir = output_dir if output_dir.is_absolute() else root / output_dir
    if (output_dir.is_symlink() or not output_dir.resolve().is_relative_to(root)
            or output_dir.resolve().is_relative_to(root / "results/research")):
        raise ValueError("resource closure output must be safe and outside results/research")
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=False)
    terminal = {"schema_version": 1, "item_id": "RESOURCE-ENVELOPE-PILOT-1",
                "status": "FAILED", "scope_file": scope_file, "completed_steps": []}
    try:
        controls_dir = output_dir / "controls"
        code = controls.finish(root, scope_file, controls_dir)
        terminal["controls_returncode"] = code
        terminal["controls_result"] = _binding(root, controls_dir / "result.json")
        if code:
            raise ValueError("unchanged ordered closure controls failed")
        for key, name in (("controls_input_inventory", "input-inventory.json"),
                          ("controls_suite_log", "full-suite.log"),
                          ("controls_validation", "validation.json")):
            terminal[key] = _binding(root, controls_dir / name)
        terminal["completed_steps"].append("unchanged-ordered-closure-controls")
        custody = validate_receipts(root, controls_dir)
        receipt_path = output_dir / "supervisor-receipts-validation.json"
        controls.write_new(receipt_path, custody)
        terminal["supervisor_receipts_validation"] = _binding(root, receipt_path)
        terminal["completed_steps"].append("four-closure-supervisor-receipts")
        freshness_log = output_dir / "final-freshness.log"
        code = controls._run_logged(
            root, ["scripts/artifact-status", "--require-current"], freshness_log)
        terminal["final_freshness_returncode"] = code
        terminal["final_freshness_log"] = _binding(root, freshness_log)
        if code:
            raise ValueError("post-receipt current artifact status failed")
        terminal["completed_steps"].append("post-receipt-current-artifact-status")
        terminal["status"] = "COMPLETE"
        return 0
    except (OSError, ValueError) as error:
        terminal["error"] = str(error)
        print(str(error), file=sys.stderr)
        return 1
    finally:
        controls.write_new(output_dir / "result.json", terminal)
