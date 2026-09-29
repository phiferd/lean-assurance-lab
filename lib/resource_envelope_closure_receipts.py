"""Portable custody and disposition check for closure supervisor fixtures."""

from hashlib import sha256
import json
from pathlib import Path


EXPECTED = {
    "normal.with.dots": (0, False, False, b"supervised-ok\n", b""),
    "nonzero": (7, False, False, b"", b"refusal\n"),
    "memory": (-9, False, True, b"", b""),
    "timeout": (-9, True, False, b"", b""),
}


def _unique(pairs):
    row = {}
    for key, value in pairs:
        if key in row:
            raise ValueError(f"duplicate closure receipt key: {key}")
        row[key] = value
    return row


def validate(root: Path, output_dir: Path) -> dict:
    """Check four expected cases and bind all twelve exact receipt/raw files."""
    root = root.resolve()
    directory = output_dir if output_dir.is_absolute() else root / output_dir
    directory = directory.resolve()
    if not directory.is_relative_to(root):
        raise ValueError("closure receipt directory escapes repository")
    receipts = directory / "supervisor-receipts"
    expected_names = {f"{name}.{suffix}" for name in EXPECTED
                      for suffix in ("receipt.json", "stdout", "stderr")}
    actual_names = {path.name for path in receipts.iterdir()}
    if actual_names != expected_names:
        raise ValueError("closure supervisor file inventory differs")
    files = []
    for name, (exit_code, timed_out, memory_exceeded, stdout, stderr) in EXPECTED.items():
        path = receipts / f"{name}.receipt.json"
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"unsafe closure receipt: {path}")
        row = json.loads(path.read_bytes(), object_pairs_hook=_unique)
        if (type(row) is not dict or type(row.get("cwd")) is not str
                or not Path(row["cwd"]).is_absolute()
                or type(row.get("argv")) is not list or not row["argv"]
                or not all(type(arg) is str for arg in row["argv"])
                or type(row.get("exit_code")) is not int
                or row.get("exit_code") != exit_code
                or row.get("timed_out") is not timed_out
                or row.get("memory_exceeded") is not memory_exceeded
                or row.get("cleanup_complete") is not True
                or row.get("memory_monitor_error") is not None
                or type(row.get("memory_monitor_samples")) is not int
                or row["memory_monitor_samples"] <= 0
                or type(row.get("maximum_observed_rss_bytes")) is not int
                or row["maximum_observed_rss_bytes"] <= 0):
            raise ValueError(f"closure supervisor disposition differs: {name}")
        for stream, expected in (("stdout", stdout), ("stderr", stderr)):
            raw_path = receipts / f"{name}.{stream}"
            relative = raw_path.relative_to(root).as_posix()
            if raw_path.is_symlink() or not raw_path.is_file():
                raise ValueError(f"unsafe closure raw stream: {raw_path}")
            raw = raw_path.read_bytes()
            if (row.get(f"raw_{stream}_path") != relative
                    or row.get(f"{stream}_bytes") != len(raw)
                    or row.get(f"{stream}_sha256") != sha256(raw).hexdigest()
                    or raw != expected):
                raise ValueError(f"closure raw stream differs: {name}.{stream}")
            files.append({"path": relative, "bytes": len(raw),
                          "sha256": sha256(raw).hexdigest()})
        data = path.read_bytes()
        files.append({"path": path.relative_to(root).as_posix(),
                      "bytes": len(data), "sha256": sha256(data).hexdigest()})
    return {"schema_version": 1, "status": "PASS", "cases": len(EXPECTED),
            "files": sorted(files, key=lambda row: row["path"])}
