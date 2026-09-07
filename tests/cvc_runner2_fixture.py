"""Inert fixture entrypoint. Every invocation has its own <5s alarm."""
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

signal.signal(signal.SIGALRM, lambda *_: os._exit(124))
signal.setitimer(signal.ITIMER_REAL, 2 if sys.argv[1] != 'controller' else 3.5)
mode = sys.argv[1]
if mode == 'ok':
    print('inert stdout', flush=True)
    print('inert stderr', file=sys.stderr, flush=True)
elif mode == 'sleep':
    print(os.getpid(), flush=True)
    time.sleep(20)
elif mode == 'cancel':
    print(os.getpid(), flush=True)
    os.kill(os.getppid(), signal.SIGTERM)
    time.sleep(20)
elif mode == 'descendant':
    child = subprocess.Popen([sys.executable, __file__, 'sleep'], stdout=subprocess.DEVNULL)
    print(str(os.getpid()) + ' ' + str(child.pid), flush=True)
    time.sleep(20)
elif mode == 'kill-controller':
    print(os.getpid(), flush=True)
    os.kill(int(sys.argv[2]), signal.SIGKILL)
    time.sleep(20)
elif mode == 'controller':
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from lib.cvc_process import run_process
    dest = Path(sys.argv[2]); dest.mkdir()
    run_process([sys.executable, __file__, 'kill-controller', str(os.getpid())], dest,
                {'PATH': '/usr/bin:/bin'}, dest, 2.5)
else:
    raise SystemExit('unknown fixture')
