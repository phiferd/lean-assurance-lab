#!/usr/bin/env python3
"""Run the one approved public image pull with daemon-side liveness evidence."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import threading
import time


DOCKER = "/usr/local/bin/docker"
PS = "/bin/ps"
NETTOP = "/usr/bin/nettop"
LSOF = "/usr/sbin/lsof"
RAW = Path.home() / "Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw"
LOGS = [
    Path.home() / "Library/Containers/com.docker.docker/Data/log/vm/dockerd.log",
    Path.home() / "Library/Containers/com.docker.docker/Data/log/vm/containerd.log",
    Path.home() / "Library/Containers/com.docker.docker/Data/log/host/com.docker.vpnkit.stderr.log",
]


def process_rows(pgid: int) -> list[dict[str, object]]:
    raw = subprocess.check_output(
        [PS, "-A", "-o", "pid=", "-o", "ppid=", "-o", "pgid=", "-o", "rss=",
         "-o", "time=", "-o", "state=", "-o", "command="], text=True,
    )
    rows = []
    for line in raw.splitlines():
        fields = line.split(None, 6)
        if len(fields) == 7 and fields[2].isdecimal() and int(fields[2]) == pgid:
            rows.append({"pid": int(fields[0]), "ppid": int(fields[1]), "pgid": int(fields[2]),
                         "rss_bytes": int(fields[3]) * 1024, "cpu_time": fields[4],
                         "state": fields[5], "command": fields[6]})
    return rows


def cpu_seconds(value: str) -> float:
    days = 0
    if "-" in value:
        day_text, value = value.split("-", 1)
        days = int(day_text)
    fields = [int(field) for field in value.split(":")]
    if len(fields) == 2:
        hours, minutes, seconds = 0, fields[0], fields[1]
    else:
        hours, minutes, seconds = fields
    return days * 86400 + hours * 3600 + minutes * 60 + seconds


def vpnkit_pid() -> int | None:
    raw = subprocess.check_output([PS, "-A", "-o", "pid=", "-o", "command="], text=True)
    for line in raw.splitlines():
        fields = line.strip().split(None, 1)
        if len(fields) == 2 and "com.docker.vpnkit" in fields[1]:
            return int(fields[0])
    return None


def network(pid: int | None) -> dict[str, object]:
    if pid is None:
        return {"pid": None, "bytes_in": None, "bytes_out": None, "error": "vpnkit not found"}
    done = subprocess.run(
        [NETTOP, "-P", "-L", "1", "-J", "bytes_in,bytes_out", "-p", str(pid)],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5,
    )
    for line in done.stdout.splitlines():
        fields = [field for field in line.split(",") if field]
        if fields and fields[0].endswith("." + str(pid)) and len(fields) >= 3:
            return {"pid": pid, "bytes_in": int(fields[1]), "bytes_out": int(fields[2]),
                    "error": None}
    return {"pid": pid, "bytes_in": None, "bytes_out": None,
            "error": (done.stderr or "no nettop process row")[:400]}


def file_state(path: Path) -> dict[str, object]:
    try:
        stat = path.stat()
        return {"path": str(path), "size": stat.st_size, "blocks": stat.st_blocks,
                "mtime_ns": stat.st_mtime_ns}
    except OSError as error:
        return {"path": str(path), "error": f"{type(error).__name__}: {error}"}


def image_present(env: dict[str, str]) -> bool:
    return subprocess.run([DOCKER, "image", "inspect", "ubuntu:24.04"], env=env,
                          stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL).returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--docker-config", type=Path, required=True)
    parser.add_argument("--no-progress-seconds", type=float, default=240)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        parser.error("output already exists")
    config = args.docker_config.resolve()
    if (config / "config.json").read_text(encoding="utf-8") != "{}\n":
        parser.error("Docker config must be the exact empty public config")

    env = dict(os.environ, DOCKER_CONFIG=str(config))
    argv = [DOCKER, "pull", "--platform", "linux/amd64", "ubuntu:24.04"]
    started = time.monotonic()
    process = subprocess.Popen(argv, env=env, stdin=subprocess.DEVNULL,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               start_new_session=True)
    raw = {"stdout": bytearray(), "stderr": bytearray()}

    def drain(name: str, pipe: object) -> None:
        while True:
            chunk = pipe.read(65536)
            if not chunk:
                break
            raw[name].extend(chunk)

    threads = [threading.Thread(target=drain, args=("stdout", process.stdout), daemon=True),
               threading.Thread(target=drain, args=("stderr", process.stderr), daemon=True)]
    for thread in threads:
        thread.start()

    vp = vpnkit_pid()
    samples: list[dict[str, object]] = []
    last_primary = 0
    baseline_network = network(vp)
    previous_network = baseline_network
    previous_raw = file_state(RAW)
    previous_logs = [file_state(path) for path in LOGS]
    last_progress = started
    stop_reason = None
    maximum_rss = 0
    previous_cpu: dict[int, float] = {}

    while process.poll() is None:
        now = time.monotonic()
        rows = process_rows(process.pid)
        for row in rows:
            pid = int(row["pid"])
            total = cpu_seconds(str(row["cpu_time"]))
            row["cpu_seconds"] = total
            row["cpu_delta_seconds"] = total - previous_cpu.get(pid, total)
            previous_cpu[pid] = total
        rss = sum(int(row["rss_bytes"]) for row in rows)
        maximum_rss = max(maximum_rss, rss)
        net = network(vp)
        raw_state = file_state(RAW)
        logs = [file_state(path) for path in LOGS]
        output_bytes = len(raw["stdout"]) + len(raw["stderr"])
        output_changed = output_bytes > last_primary
        net_changed = all(isinstance(net.get(key), int) and isinstance(previous_network.get(key), int)
                          and int(net[key]) > int(previous_network[key])
                          for key in ("bytes_in", "bytes_out"))
        disk_changed = (isinstance(raw_state.get("blocks"), int)
                        and isinstance(previous_raw.get("blocks"), int)
                        and int(raw_state["blocks"]) > int(previous_raw["blocks"]))
        log_changed = any(current.get("size") != previous.get("size")
                          or current.get("mtime_ns") != previous.get("mtime_ns")
                          for current, previous in zip(logs, previous_logs))
        present = image_present(env)
        if output_changed or present or (net_changed and (disk_changed or log_changed)):
            last_progress = now
        sample = {"elapsed_seconds": now - started, "processes": rows,
                  "group_rss_bytes": rss, "stdout_bytes": len(raw["stdout"]),
                  "stderr_bytes": len(raw["stderr"]), "network": net,
                  "docker_raw": raw_state, "logs": logs, "image_present": present,
                  "progress": {"output": output_changed, "network_both_directions": net_changed,
                               "disk_blocks": disk_changed, "logs": log_changed}}
        samples.append(sample)
        if present:
            last_progress = now
        if rss > 4 * 1024**3:
            stop_reason = "OBSERVED_PULL_PROCESS_MEMORY_LIMIT"
        elif now - last_progress >= args.no_progress_seconds:
            stop_reason = "NO_CORROBORATED_PULL_PROGRESS"
        if stop_reason:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
            break
        last_primary = output_bytes
        previous_network, previous_raw, previous_logs = net, raw_state, logs
        time.sleep(5)

    returncode = process.wait()
    for thread in threads:
        thread.join(timeout=5)
    output.mkdir(parents=True, exist_ok=False)
    (output / "stdout.log").write_bytes(raw["stdout"])
    (output / "stderr.log").write_bytes(raw["stderr"])
    receipt = {"schema_version": 1, "argv": argv, "docker_config": str(config),
               "elapsed_seconds": time.monotonic() - started, "exit_code": returncode,
               "stop_reason": stop_reason, "no_progress_seconds": args.no_progress_seconds,
               "maximum_pull_group_rss_bytes": maximum_rss, "vpnkit_pid": vp,
               "baseline_network": baseline_network, "samples": samples,
               "final_image_present": image_present(env),
               "stdout_bytes": len(raw["stdout"]), "stderr_bytes": len(raw["stderr"])}
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return 0 if returncode == 0 and receipt["final_image_present"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
