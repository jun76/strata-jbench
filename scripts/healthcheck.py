"""One look at the unattended pipeline: is each running phase alive and making progress?

  python3 scripts/healthcheck.py --run-id <run id> [--env <id>] [--quiet]

Run by the run's supervisor every "watch_interval_s" (scripts/supervise.py, bench.json; 5 min by default) and by
`scripts/bench.py status`, independent of any agent's session. Writes run-status/status.json and run-status/STATUS.md; when the overall state turns FAILED or STUCK it
appends to run-status/ALERTS.log and shows a desktop notification, once per new problem.

States: RUNNING (alive and progressing), WAITING (queue waiting until what the run needs is on disk), DONE, STOPPED
(stopped with scripts/bench.py stop), FAILED (a phase ended without its result), STUCK (alive but nothing has changed
for longer than the phase ever needs).
A finished queue is DONE only when no runner exited with an error and every planned case of the steps it ran has a
result; otherwise FAILED. A runner error while the queue goes on with the next Tier is notified at once.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import config  # noqa: E402
import envs  # noqa: E402
DL = ROOT / 'downloads'
OUT = ROOT / 'run-status'
STALE = {'download': 45 * 60, 'download-q8': 45 * 60, 'qad': 45 * 60, 'bench': 75 * 60, 'launch': 3 * 3600 + 20 * 60}


def alive(pid):
    try:
        os.kill(int(pid), 0)
        return True
    except (OSError, TypeError, ValueError):
        return False


def age(path):
    try:
        return time.time() - Path(path).stat().st_mtime
    except OSError:
        return None


def load(path):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return {}


def acquire_state():
    st = load(DL / 'overnight-state.json')
    if (DL / 'READY').exists():
        return {'phase': 'acquire', 'state': 'DONE', 'detail': 'all models on disk'}
    if not st:
        return {'phase': 'acquire', 'state': 'NOT_STARTED', 'detail': ''}
    phase = st.get('phase', '?')
    if not alive(st.get('pid')) and phase == 'done' and not st.get('error'):
        # it finished; READY went away later because env.json lists models it has not fetched (scripts/setup_acquire.py).
        # Nothing fetches them until someone chooses to (AGENTS.md 2.0a); a run that does not need them goes ahead
        return {'phase': 'acquire', 'state': 'NOT_STARTED',
                'detail': 'not every model of env.json is on disk (python3 -I scripts/acquire.py check)'}
    if not alive(st.get('pid')):
        return {'phase': f'acquire/{phase}', 'state': 'FAILED',
                'detail': f'scripts/overnight.py ended without READY (error: {st.get("error")}); see downloads/overnight.log'}
    # status.json is written per file, and the hf CLI writes download.log only as a file starts and ends (a 50 GB shard
    # takes 10-30 min); scripts/overnight.py restarts a downloader silent for 20 min, which writes download.log again
    files = [DL / 'qad-prepare.log'] if phase == 'qad' else [DL / 'status.json', DL / 'download.log']
    ages = [(age(f), f) for f in files if age(f) is not None]
    a, progress = min(ages, key=lambda t: t[0]) if ages else (None, files[0])
    if a is not None and a > STALE.get(phase, 1800):
        return {'phase': f'acquire/{phase}', 'state': 'STUCK', 'detail': f'{progress.name} unchanged for {a / 60:.0f} min'}
    status = load(DL / 'status.json')
    return {'phase': f'acquire/{phase}', 'state': 'RUNNING',
            'detail': f'current: {status.get("current")}' if phase.startswith('download') else 'preparing NVFP4-QAD'}


def queue_errors(lines):
    """Runner exits other than 0 ("steps <s>: runner exit <rc>", scripts/supervise.py) and Python tracebacks
    in the queue log (a queue started before the exit codes were logged shows only the traceback)."""
    exits = [ln for ln in lines if ': runner exit ' in ln]
    errors = [ln[26:].strip() for ln in exits if not ln.rstrip().endswith(' exit 0')]
    tracebacks = sum(ln.startswith('Traceback (most recent call last)') for ln in lines)
    # a runner started again by the supervisor after a crash leaves its traceback above an exit 0
    if tracebacks and not exits:
        errors.append(f'{tracebacks} traceback(s) in queue.log')
    return errors


def missing_cases(run_dir, env_id, lines):
    """Planned cases of the steps this queue ran, among the models and cases its settings chose (the run's bench.json),
    that have no summary.json: {step: count}."""
    steps = {ln[26:].split('steps ', 1)[1].strip() for ln in lines if ln[26:].startswith('steps ') and ':' not in ln[26:]}
    if (run_dir / 'bench.json').exists():
        cfg = config.load(run_dir / 'bench.json')
    else:   # a run started before bench.json: $MODELS, as run-status/current-run.json kept it
        current = load(OUT / 'current-run.json')
        chosen = current.get('models', '') if current.get('run_dir') == str(run_dir.relative_to(ROOT)) else ''
        cfg = {'models': [m.replace(':', ' ', 1) for m in chosen.split(',') if m]}
    missing = {}
    plan = envs.plan_dir(env_id) / 'cases.jsonl'
    rows = [json.loads(ln) for ln in plan.read_text().splitlines() if ln.strip()] if plan.exists() else []
    for row in config.select(rows, {**cfg, 'tiers': None}):
        if row.get('step') in steps and not (run_dir / 'cases' / row['id'] / 'summary.json').exists():
            missing[row['step']] = missing.get(row['step'], 0) + 1
    return missing


def bench_state(run_dir, env_id):
    queue_log = run_dir / 'queue.log'
    pid_file = run_dir / 'queue.pid'
    if not queue_log.exists():
        return {'phase': 'bench', 'state': 'NOT_STARTED', 'detail': ''}
    lines = queue_log.read_text(errors='replace').strip().splitlines()
    starts = [i for i, ln in enumerate(lines) if ' queue start ' in ln]
    lines = lines[starts[-1]:] if starts else lines       # this queue only, not an earlier start of the same run id
    last = lines[-1:] or ['']
    pid = pid_file.read_text().strip() if pid_file.exists() else None
    summaries = [load(p) for p in run_dir.glob('cases/*/summary.json')]
    counts = {}
    for s in summaries:
        counts[s.get('status', '?')] = counts.get(s.get('status', '?'), 0) + 1
    errors = queue_errors(lines)
    if 'queue finished' in last[0]:
        # finished is not done: every planned case of the steps run must have a result (done, failed or skipped)
        missing = missing_cases(run_dir, env_id, lines)
        if errors or missing:
            gaps = ', '.join(f'steps {s}: {n}' for s, n in missing.items())
            return {'phase': 'bench', 'state': 'FAILED',
                    'detail': '; '.join(filter(None, ['; '.join(errors), f'cases without a result ({gaps})' if gaps else '',
                                                      f'cases {counts}']))}
        return {'phase': 'bench', 'state': 'DONE', 'detail': f'cases {counts}'}
    if 'queue stopped' in last[0]:
        return {'phase': 'bench', 'state': 'STOPPED', 'detail': f'stopped at {last[0][:25]} (scripts/bench.py start resumes it); cases {counts}'}
    if not alive(pid):
        return {'phase': 'bench', 'state': 'FAILED', 'detail': f'queue ended: {last[0]}; cases {counts}'}
    if any(w in last[0] for w in ('waiting for downloads/READY', 'waiting until what the run needs is on disk',
                                  'waiting until the downloads end')):
        return {'phase': 'bench', 'state': 'WAITING', 'detail': 'queue waits until what the run needs is on disk (run-status/acquire.json)'}
    fresh = [age(run_dir / 'runner.log')] + [age(p) for p in run_dir.glob('sessions/*/*/telemetry.csv')]
    fresh = min((a for a in fresh if a is not None), default=None)
    # a launch (with tuning) writes nothing until it is ready or the runner gives up on it (LAUNCH_TIMEOUT in
    # scripts/bench_runner.py, 3 h); only past that is a silent launch stuck
    runner = (run_dir / 'runner.log').read_text(errors='replace').strip().splitlines()[-1:] if (run_dir / 'runner.log').exists() else []
    limit = STALE['launch'] if runner and runner[0].endswith('start(s)') else STALE['bench']
    if fresh is not None and fresh > limit:
        return {'phase': 'bench', 'state': 'STUCK', 'detail': f'no runner log or telemetry for {fresh / 60:.0f} min'}
    failed = counts.get('failed', 0)
    # a Tier whose runner died: the queue goes on with the next Tier, so say so now (and notify) instead of after the queue
    warn = '; '.join(filter(None, ['; '.join(errors), f'{failed} failed cases' if failed else '']))
    return {'phase': 'bench', 'state': 'RUNNING', 'detail': f'{last[0][26:]}; cases {counts}',
            'warn': warn or None, 'alert': '; '.join(errors) or None}


def stats_line(run_dir, bench):
    """The last machine snapshot (scripts/stats_watch.py); a warning on a running bench when they have stopped."""
    last = load(run_dir / 'stats' / 'last.json')
    a = age(run_dir / 'stats' / 'last.json')
    if bench['state'] == 'RUNNING' and (a is None or a > 900):
        stale = 'no snapshot yet' if a is None else f'no snapshot for {a / 60:.0f} min'
        bench['warn'] = '; '.join(filter(None, [bench.get('warn'), f'stats: {stale} (scripts/stats_watch.py)']))
    return f'統計スナップショット: {last.get("t", "なし")} {last.get("event", "")}'


def notify(text, desktop=True):
    with (OUT / 'ALERTS.log').open('a') as f:
        f.write(f'{datetime.now().astimezone().isoformat(timespec="seconds")} {text}\n')
    if desktop:
        subprocess.run(['notify-send', '--urgency=critical', 'strata-jbench', text], capture_output=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run-id', default=os.environ.get('RUN_ID'), required=not os.environ.get('RUN_ID'))
    ap.add_argument('--env', default=os.environ.get('BENCH_ENV', ''), help='default: the one this hardware matches')
    ap.add_argument('--quiet', action='store_true')
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    env_id = a.env or envs.current()
    # the division: the supervisor sets BENCH_DIVISION; by hand, the one of the run started last when it is this run
    current = load(OUT / 'current-run.json')
    if not os.environ.get('BENCH_DIVISION') and current.get('run_id') == a.run_id and current.get('division'):
        os.environ['BENCH_DIVISION'] = current['division']
    run_dir = envs.run_dir(env_id, a.run_id)
    parts = [acquire_state(), bench_state(run_dir, env_id)]
    bad = [p for p in parts if p['state'] in ('FAILED', 'STUCK')]
    overall = bad[0]['state'] if bad else 'STOPPED' if parts[1]['state'] == 'STOPPED' \
        else 'DONE' if all(p['state'] in ('DONE', 'NOT_STARTED') for p in parts) else 'RUNNING'
    gpu = subprocess.run(['nvidia-smi', *envs.smi_card(env_id), '--query-gpu=memory.used,temperature.gpu', '--format=csv,noheader'],
                         capture_output=True, text=True).stdout.strip()
    disk = os.statvfs(ROOT)
    status = {'at': datetime.now().astimezone().isoformat(timespec='seconds'), 'overall': overall, 'env': env_id,
              'run_id': a.run_id, 'run_dir': str(run_dir.relative_to(ROOT)), 'parts': parts,
              'gpu': gpu, 'disk_free_gb': round(disk.f_bavail * disk.f_frsize / 1e9)}
    stats = stats_line(run_dir, parts[1])
    status['stats'] = stats
    prev = load(OUT / 'status.json')
    (OUT / 'status.json').write_text(json.dumps(status, ensure_ascii=False, indent=2) + '\n')
    lines = [f'# 実行状況 {status["at"]}', '', f'全体: **{overall}**（環境 {env_id}、RUN_ID {a.run_id}、`{status["run_dir"]}`）', '', '| 段階 | 状態 | 内容 |', '| --- | --- | --- |']
    lines += [f'| {p["phase"]} | {p["state"]} | {p["detail"]}{" ⚠ " + p["warn"] if p.get("warn") else ""} |'
              for p in parts]
    lines += ['', f'GPU: {gpu} / 空きディスク: {status["disk_free_gb"]} GB', stats]
    (OUT / 'STATUS.md').write_text('\n'.join(lines) + '\n')
    desktop = config.load(run_dir / 'bench.json')['notify'] if (run_dir / 'bench.json').exists() else True
    problem = '; '.join(f'{p["phase"]} {p["state"]}: {p["detail"]}' for p in bad)
    old = '; '.join(f'{p["phase"]} {p["state"]}: {p["detail"]}' for p in prev.get('parts', [])
                    if p['state'] in ('FAILED', 'STUCK'))
    if problem and problem.split(':')[0] != old.split(':')[0]:
        notify(problem, desktop)
    alerts = [f'{p["phase"]} {p["state"]}: {p["alert"]}' for p in parts if p.get('alert')]
    old_alerts = [f'{p["phase"]} {p["state"]}: {p["alert"]}' for p in prev.get('parts', []) if p.get('alert')]
    if alerts and alerts != old_alerts:
        notify('; '.join(alerts), desktop)
    if not a.quiet:
        print((OUT / 'STATUS.md').read_text())
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
