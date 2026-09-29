"""Planning-only E0 handoff. No assurance generation, replay or receipts."""
import json
from pathlib import Path
import runpy
import subprocess

from lib import exploration as e

PLANNING = {'config/research-queue.json', 'docs/RESEARCH_STATUS.md',
            'docs/research/DISCOVERY_AND_CONFORMANCE_PLAN.md',
            'results/research/project-review.json', 'docs/PROJECT_REVIEW.md'}


def git(root, *args):
    return subprocess.check_output(['git', *args], cwd=root)


def changed_paths(root, base, *, worktree=False):
    args = ['diff', '--name-only', '--no-renames', base]
    if not worktree:
        args.append('HEAD')
    paths = set(git(root, *args, '--').decode().splitlines())
    if worktree:
        paths.update(git(root, 'ls-files', '--others', '--exclude-standard').decode().splitlines())
    return paths


def qualifies(root, base, paths):
    """An E0 completion plus planning changes; unknown/shared changes fail closed."""
    if not paths or e.LEDGER not in paths:
        return False
    if any(not (p == e.LEDGER or p.startswith('explorations/runs/') or p in PLANNING
                or p.startswith('results/research/queue-reviews/') and p.endswith('.json')
                or p.startswith('docs/research/') and p.endswith('.md')) for p in paths):
        return False
    previous = git(root, 'show', f'{base}:{e.LEDGER}')
    raw = e.local_file(root, e.LEDGER).read_bytes()
    if not raw.startswith(previous):
        return False
    rows = [e.read_json(line) for line in raw.splitlines()]
    starts = {r['id']: r for r in rows if r['event'] == 'start'}
    finishes = [e.read_json(line) for line in raw[len(previous):].splitlines()
                if e.read_json(line)['event'] == 'finish']
    old_queue = e.read_json(git(root, 'show', f'{base}:config/research-queue.json'))
    campaign = old_queue['selected_item']
    item = next(i for i in old_queue['items'] if i['id'] == campaign)
    if not any(starts[r['id']]['data']['campaign'] == campaign for r in finishes):
        return False
    base_files = set(git(root, 'ls-tree', '-r', '--name-only', base).decode().splitlines())
    if not any(p in base_files and p.endswith('.md') and b'\nEvidence class: E0\n' in
               git(root, 'show', f'{base}:{p}') for p in item['evidence_refs']):
        return False
    for path in paths:
        if path == e.LEDGER or path.startswith('explorations/runs/') or path in PLANNING:
            continue
        if path not in base_files and (
                path.startswith('results/research/queue-reviews/') and path.endswith('.json')
                or path.startswith('docs/research/') and path.endswith('.md')):
            continue
        return False
    return True


def planning_view(root, *, write=False):
    # Reuse the existing pure builder/render functions. Its CLI also replays a
    # historical publication gate; E0 planning neither changes nor reattests it.
    module = runpy.run_path(str(root / 'scripts/build-project-review'))
    review = module['build']()
    outputs = {module['OUTPUT']: json.dumps(review, indent=2, sort_keys=True) + '\n',
               module['REPORT']: module['render'](review)}
    for path, value in outputs.items():
        target = root / path
        if write:
            target.write_text(value)
        elif target.read_text() != value:
            raise ValueError('planning view is stale; run exploration-handoff --write')


def handoff(root, base, *, write=False):
    paths = changed_paths(root, base, worktree=True)
    if not qualifies(root, base, paths):
        raise ValueError('not an E0-only handoff; shared/assurance changes require their full checks')
    raw = e.local_file(root, e.LEDGER).read_bytes()
    e.committed_prefix(root, raw, base)
    states = e.validate(root, raw)
    from lib.research_queue_v4 import load_queue
    queue = load_queue(root)
    review = e.read_json(e.local_file(root, queue['strategic_review']['path']).read_bytes())
    if review['phase'] != 'CLOSURE' or any(i['status'] == 'ACTIVE' for i in queue['items']):
        raise ValueError('handoff must close the campaign and leave its successor unstarted')
    stopped = review['stopped_item']
    old_queue = e.read_json(git(root, 'show', f'{base}:config/research-queue.json'))
    if stopped != old_queue['selected_item']:
        raise ValueError('handoff must close the campaign selected at the review base')
    trials = [s for s in states.values() if s['start']['data']['campaign'] == stopped]
    if not trials or any('finish' not in s for s in trials):
        raise ValueError('handoff requires all campaign trials to be closed')
    planning_view(root, write=write)
    git(root, 'diff', '--check', base)
    return dict(e.summary(states), handoff='PASS', selected_item=queue['selected_item'],
                assurance_refreshed=False)
