"""One whole-module retry; tested supervisor plus scoped coarse progress observer."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from local_supervisor import run_direct
RUN = Path(__file__).resolve().parent

def cpu_seconds(text):
    days, clock = text.split('-', 1) if '-' in text else ('0', text)
    total = 0.0
    for field in clock.split(':'):
        total = total * 60 + float(field)
    return int(days) * 86400 + total

def stalled(window):
    if len(window) < 2 or window[-1]['elapsed'] - window[0]['elapsed'] < 600:
        return False
    return (window[-1]['cpu_seconds'] - window[0]['cpu_seconds'] < 1
        and max(x['rss_bytes'] for x in window) - min(x['rss_bytes'] for x in window)
            < max(1024**2, window[0]['rss_bytes'] * .01)
        and all(x['state'].startswith('S') or x['state'].startswith('T') for x in window))

def self_test():
    assert cpu_seconds('01:02.50') == 62.5
    assert cpu_seconds('1-02:03:04.5') == 93784.5
    quiet = [dict(elapsed=t, cpu_seconds=2, rss_bytes=10000000, state='S') for t in (0, 600)]
    assert stalled(quiet)
    assert not stalled([quiet[0], {**quiet[1], 'cpu_seconds': 100}])
    assert not stalled([quiet[0], {**quiet[1], 'rss_bytes': 20000000}])
    assert not stalled([quiet[0], {**quiet[1], 'state': 'R'}])
    assert not stalled([quiet[0], {**quiet[1], 'elapsed': 599}])
    print('PASS: CPU parser, combined stall detector and healthy silent computation controls')

def save(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')

def main():
    identity = json.loads((RUN / 'preflight.json').read_text())
    cwd = Path(identity['payload'])
    binary = Path(identity['runtime_bin']) / 'nanoda_bin'
    assert hashlib.sha256(binary.read_bytes()).hexdigest() == identity['binaries']['nanoda_bin']
    assert hashlib.sha256((cwd / 'export.txt').read_bytes()).hexdigest() == identity['export_sha256']
    assert hashlib.sha256((cwd / 'config.json').read_bytes()).hexdigest() == identity['config_sha256']
    out = RUN / 'attempt-0002'
    out.mkdir(exist_ok=False)
    argv = [str(binary), str(cwd / 'config.json')]
    overrides = {'PATH': str(binary.parent) + ':' + os.environ['PATH']}
    save(out / 'command.json', {'argv': argv, 'cwd': str(cwd), 'environment_overrides': overrides,
        'wall_clock_deadline': 'disabled: explicit None; run-local optional-timeout patch',
        'memory_ceiling_bytes': 16 * 1024**3, 'sample_interval_seconds': 5,
        'max_trace_gap_seconds': 20, 'watchdog_interval_seconds': 5,
        'pressure_interval_seconds': 30, 'stall_window_seconds': 600,
        'stall_stop': '600s less than1s CPU, less than1percent/1MiB RSS change, all sampled states sleeping/stopped; no stdout criterion', 'pressure_stop': '<10% system memory free sustained60s', 'disk_stop': '<20GiB free'})
    done = threading.Event()
    watch = {'stop_reason': None, 'signal_events': [], 'errors': [], 'samples': 0}
    started = time.monotonic()
    window = []

    def stop(pid, reason):
        if done.is_set():
            return
        watch['stop_reason'] = reason
        try:
            if os.getpgid(pid) == pid:
                os.killpg(pid, signal.SIGKILL)
                watch['signal_events'].append({'pid': pid, 'reason': reason, 'elapsed': time.monotonic() - started})
        except ProcessLookupError:
            watch['signal_events'].append({'pid': pid, 'reason': reason, 'already_exited': True})
        except OSError as e:
            watch['errors'].append(str(e))

    def observe():
        pressure_at = -30
        low_pressure_since = None
        free_percent = None
        errors = 0
        last_status_at = -60
        with (out / 'progress.jsonl').open('w') as log:
            last_pid = None
            while not done.is_set():
                targets = []
                try:
                    raw = subprocess.check_output(['/bin/ps', '-axo', 'pid=,ppid=,pgid=,state=,time=,rss=,comm='], timeout=3, text=True)
                    targets = []
                    for line in raw.splitlines():
                        f = line.split(None, 6)
                        if len(f) == 7 and int(f[1]) == os.getpid() and int(f[0]) == int(f[2]) and Path(f[6]).name == 'nanoda_bin':
                            targets.append(f)
                    if targets:
                        assert len(targets) == 1
                        f = targets[0]
                        last_pid = int(f[0])
                        elapsed = time.monotonic() - started
                        if elapsed - pressure_at >= 30:
                            pressure = subprocess.check_output(['/usr/bin/memory_pressure', '-Q'], timeout=3, text=True)
                            free_percent = int(re.search(r'free percentage:\s*(\d+)%', pressure)[1])
                            pressure_at = elapsed
                            low_pressure_since = (elapsed if low_pressure_since is None else low_pressure_since) if free_percent < 10 else None
                        sample = {'elapsed': elapsed, 'pid': int(f[0]), 'state': f[3], 'cpu_seconds': cpu_seconds(f[4]),
                            'rss_bytes': int(f[5]) * 1024,
                            'disk_free_bytes': shutil.disk_usage(cwd).free, 'system_memory_free_percent': free_percent}
                        log.write(json.dumps(sample) + '\n'); log.flush()
                        watch['samples'] += 1
                        window.append(sample)
                        while len(window) > 1 and elapsed - window[1]['elapsed'] >= 600:
                            window.pop(0)
                        if sample['disk_free_bytes'] < 20 * 1024**3:
                            stop(sample['pid'], 'LOW_DISK_SPACE')
                        elif low_pressure_since is not None and elapsed - low_pressure_since >= 60:
                            stop(sample['pid'], 'SUSTAINED_HOST_MEMORY_PRESSURE')
                        elif stalled(window):
                            stop(sample['pid'], 'COMBINED_NO_PROGRESS_600S')
                        if elapsed - last_status_at >= 60:
                            print('progress', json.dumps(sample), flush=True)
                            last_status_at = elapsed
                        errors = 0
                        if watch['stop_reason']:
                            return
                except Exception as e:
                    watch['errors'].append(type(e).__name__ + ': ' + str(e))
                    errors += 1
                    if errors >= 3 and last_pid is not None:
                        stop(last_pid, 'PROGRESS_MONITOR_FAULT')
                        return
                done.wait(5)

    observer = threading.Thread(target=observe, daemon=True)
    observer.start()
    try:
        result = run_direct(argv=argv, cwd=cwd, env={**os.environ, **overrides}, stdin_bytes=None,
            timeout_seconds=None, memory_ceiling_bytes=16*1024**3,
            sample_interval_seconds=5, max_trace_gap_seconds=20, cleanup_seconds=10,
            ps_timeout_seconds=3, output_cap_bytes=10_000_000)
    finally:
        done.set()
        observer.join(timeout=10)
    (out / 'stdout').write_bytes(result.stdout)
    (out / 'stderr').write_bytes(result.stderr)
    save(out / 'receipt.json', result.receipt)
    save(out / 'watchdog.json', watch)
    if observer.is_alive():
        raise RuntimeError('Progress observer failed to finish')
    print('completed exit', result.receipt['exit_code'], 'elapsed', result.receipt['elapsed_seconds'],
        'cpu', result.receipt['child_user_cpu_seconds'], 'peak', result.receipt['child_peak_rss_bytes'], flush=True)
    print(result.stdout.decode(errors='replace'), result.stderr.decode(errors='replace'), flush=True)
    r = result.receipt
    safe = (r['cleanup_complete'] and r['reap_complete'] and not r['monitor_errors'] and not r['pipe_errors']
        and not r['accounting_error'] and not r['stop_reason'] and not r['trace_gap_fault']
        and not watch['stop_reason'] and not watch['errors'])
    save(RUN / 'observation.json', {'evidence_class': 'E0', 'whole_module': 'Foo plus all imports',
        'exit_code': r['exit_code'], 'measurement_complete': safe, 'export_sha256': identity['export_sha256'],
        'config_sha256': identity['config_sha256'], 'scope': 'one retained full clean export, same bundled checker; no fallback or composite-action claim'})
    if not safe:
        raise RuntimeError('Pause on resource/control fault; all raw evidence retained')

if __name__ == '__main__':
    if sys.argv[1:] == ['--self-test']:
        self_test()
    else:
        main()
