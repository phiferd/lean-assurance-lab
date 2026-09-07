"""Process-group supervisor with a parent-loss pipe and durable raw receipts.

The forked supervisor survives controller death, observes pipe EOF, and cleans
up its child group. The OS, Python runtime and reviewed local source are trusted.
This is execution accounting, not a sandbox against hostile source programs.
"""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import select
import signal
import subprocess
import time


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for data in iter(lambda: stream.read(1048576), b''):
            h.update(data)
    return h.hexdigest()


def sync_dir(path):
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + '.tmp')
    if temporary.is_symlink() or path.is_symlink():
        raise ValueError('symlink accounting file')
    with temporary.open('w') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    os.replace(temporary, path)
    sync_dir(path.parent)


def cleanup(proc):
    # Always address the group, even when the leader already exited.
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(proc.pid, sig)
        except ProcessLookupError:
            pass
        if sig == signal.SIGTERM:
            try:
                proc.wait(timeout=.05)
            except subprocess.TimeoutExpired:
                pass
    proc.wait(timeout=.5)


def _supervise(read_fd, request, directory):
    started, begin, proc = request['started_at'], request['monotonic_started'], None
    status, error, rc, cancel = 'FAILED', None, None, []
    def cancelled(signum, _frame):
        cancel.append(signum)
    signal.signal(signal.SIGTERM, cancelled)
    signal.signal(signal.SIGINT, cancelled)
    # A supervisor must not inherit a controller's alarm handler/timer.
    signal.signal(signal.SIGALRM, cancelled)
    signal.setitimer(signal.ITIMER_REAL, max(.001, request['deadline_monotonic'] - time.monotonic()))
    stdout, stderr = directory / 'stdout', directory / 'stderr'
    try:
        with stdout.open('xb') as so, stderr.open('xb') as se:
            proc = subprocess.Popen(request['argv'], cwd=request['cwd'], env=request['env'],
                                    stdin=subprocess.DEVNULL, stdout=so, stderr=se, start_new_session=True)
            atomic(directory / 'process.json', {'pid': proc.pid, 'supervisor_pid': os.getpid(),
                                                'request_sha256': request['request_sha256'], 'started_at': now()})
            deadline = request['deadline_monotonic'] - .2
            while True:
                if cancel:
                    status, error = ('TIMED_OUT', 'supervisor deadline') if signal.SIGALRM in cancel else ('INTERRUPTED', 'supervisor cancelled')
                    break
                ready, _, _ = select.select([read_fd], [], [], .01)
                if ready and os.read(read_fd, 1) == b'':
                    status, error = 'INTERRUPTED', 'controller pipe closed'
                    break
                rc = proc.poll()
                if rc is not None:
                    status = 'COMPLETE' if rc == 0 else 'FAILED'
                    break
                if time.monotonic() >= deadline:
                    status, error = 'TIMED_OUT', 'process deadline'
                    break
    except BaseException as exc:
        status, error = 'FAILED', type(exc).__name__ + ': ' + str(exc)
    finally:
        # Further cancellation must not interrupt cleanup or evidence writing.
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.setitimer(signal.ITIMER_REAL, 0)
        cleanup_completed = True
        try:
            if proc is not None:
                cleanup(proc); rc = proc.returncode
        except BaseException as exc:
            cleanup_completed = False
            status, error = 'INTERRUPTED', 'cleanup failed: ' + str(exc)
        elapsed = time.monotonic() - begin
        deadline_exceeded = time.monotonic() > request['deadline_monotonic']
        if deadline_exceeded:
            status, error = 'TIMED_OUT', 'elapsed including cleanup exceeded reservation'
        receipt = {'status': status, 'returncode': rc, 'charged_seconds': elapsed,
                   'started_at': started, 'ended_at': now(), 'monotonic_started': begin,
                   'monotonic_ended': time.monotonic(), 'request_sha256': request['request_sha256'],
                   'stdout_sha256': sha(stdout) if stdout.is_file() else None,
                   'stderr_sha256': sha(stderr) if stderr.is_file() else None,
                   'cleanup_completed': cleanup_completed, 'deadline_exceeded': deadline_exceeded}
        if error:
            receipt['error'] = error
        atomic(directory / 'supervisor.json', receipt)


def run_process(argv, cwd, env, directory, seconds, *, deadline_monotonic=None):
    """The caller must durably reserve before calling. Fork is also charged.

    Raw outputs and a supervisor receipt survive controller SIGTERM/SIGKILL.
    No general command override is exposed by the protocol's production CLI.
    """
    if not isinstance(seconds, (int, float)) or not 0 < seconds <= 300:
        raise ValueError('invalid process reservation')
    directory = Path(directory)
    begin = time.monotonic()
    deadline = min(begin + seconds, deadline_monotonic) if deadline_monotonic is not None else begin + seconds
    if deadline <= begin:
        raise ValueError('reservation expired before supervisor launch')
    request = {'argv': list(argv), 'cwd': str(cwd), 'env': dict(env), 'seconds': seconds,
               'monotonic_started': begin, 'started_at': now(), 'deadline_monotonic': deadline}
    request['request_sha256'] = hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()
    atomic(directory / 'request.json', request)
    read_fd, write_fd = os.pipe()
    os.set_inheritable(write_fd, False)
    cancelled = []
    def interrupt(signum, _frame):
        cancelled.append(signum)
    old = {sig: signal.signal(sig, interrupt) for sig in (signal.SIGTERM, signal.SIGINT)}
    pid, closed = None, False
    try:
        pid = os.fork()
        if pid == 0:
            os.close(write_fd)
            try:
                os.setsid()
                _supervise(read_fd, request, directory)
                os._exit(0)
            except BaseException:
                os._exit(1)
        os.close(read_fd)
        deadline = request['deadline_monotonic'] + 1
        while True:
            if cancelled and not closed:
                os.close(write_fd); closed = True
            done, _ = os.waitpid(pid, os.WNOHANG)
            if done:
                break
            if time.monotonic() > deadline:
                # Bound failure recovery; a child PID receipt comes from this
                # exact just-created supervisor on the trusted local filesystem.
                marker = directory / 'process.json'
                if marker.exists():
                    child = json.loads(marker.read_text())
                    if child['request_sha256'] == request['request_sha256']:
                        try: os.killpg(child['pid'], signal.SIGKILL)
                        except ProcessLookupError: pass
                try: os.kill(pid, signal.SIGKILL)
                except ProcessLookupError: pass
                os.waitpid(pid, 0)
                raise ValueError('supervisor failed to finish within cleanup bound')
            time.sleep(.01)
        receipt = json.loads((directory / 'supervisor.json').read_text())
        if receipt['request_sha256'] != request['request_sha256']:
            raise ValueError('wrong supervisor receipt')
        return receipt
    finally:
        if not closed:
            os.close(write_fd)
        if pid is None:
            os.close(read_fd)
        for sig, handler in old.items():
            signal.signal(sig, handler)
