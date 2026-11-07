#!/usr/bin/env python3
"""The benchmark's one entry point (AGENTS.md 2): settings, plan, start, status, stop.

    python3 -I scripts/bench.py config [--json]     every setting of bench.json: name, value in force, default, what it does
    python3 -I scripts/bench.py plan                the cases the settings choose: per Tier the cases, requests and hours
    python3 -I scripts/bench.py start               check, then start the run's supervisor detached (scripts/supervise.py)
    python3 -I scripts/bench.py status [--json]     how the run started last is going (run-status/STATUS.md)
    python3 -I scripts/bench.py stop                stop it (the supervisor, the runner, the engine it launched)

The settings are bench.json at the repository's root (not in Git; scripts/config.py has every key, its default and
what it does). start refuses with no "run_id", with no environment matching this hardware, with a division that is not
active, with nothing chosen, while another run's supervisor is alive, or while something the cases chosen need is not
on disk (unless "fetch": AGENTS.md 2.0a). Starting the same run_id again resumes it (finished cases are skipped).

The supervisor runs on its own, with no systemd unit and no terminal: it survives the terminal and the agent's session
being closed, and checks itself (healthcheck every "watch_interval_s", runner restarts). It does not survive a reboot or,
while linger is off, the user's last logout (AGENTS.md 2.2); `start` again resumes.
"""
import argparse
import json
import os
import signal
import subprocess
import sys
import textwrap
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import config  # noqa: E402
import envs  # noqa: E402

PY = [sys.executable, '-I']
STATUS = ROOT / 'run-status'
CURRENT = STATUS / 'current-run.json'


def load(path):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return {}


def alive(pid):
    try:
        os.kill(int(pid), 0)
        return True
    except (OSError, TypeError, ValueError):
        return False


def supervisor_pid(run_dir):
    pid = (Path(run_dir) / 'queue.pid').read_text().strip() if (Path(run_dir) / 'queue.pid').exists() else None
    return int(pid) if alive(pid) else None


def cmd_config(a):
    rows = config.table()
    if a.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return 0
    print(f'{config.PATH.relative_to(ROOT)}: {"sets " + ", ".join(r["key"] for r in rows if r["set"]) if config.PATH.exists() and any(r["set"] for r in rows) else "nothing set (every value is its default)"}')
    for r in rows:
        mark = '*' if r['set'] else ' '
        val = json.dumps(r['value'], ensure_ascii=False)
        dflt = '' if not r['set'] else f'   (default {json.dumps(r["default"], ensure_ascii=False)})'
        print(f'\n{mark} {r["key"]} = {val}{dflt}')
        print(textwrap.fill(r['about'], 110, initial_indent='    ', subsequent_indent='    '))
    return 0


def chosen(cfg, env_id):
    """Build the plan and return (the plan's rows, the rows the settings choose, warnings)."""
    r = subprocess.run(PY + ['scripts/build_cases.py', '--env', env_id], cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(r.stdout + r.stderr)
    warn = [ln for ln in r.stderr.splitlines() if ln.strip()]
    plan = [json.loads(x) for x in (envs.plan_dir(env_id) / 'cases.jsonl').read_text().splitlines() if x.strip()]
    rows = config.select(plan, cfg)
    steps = {p['step'] for p in plan}
    models = {f'{p["family"]} {p["model"]}' for p in plan}
    ids = {p['id'] for p in plan}
    for key, have in (('tiers', steps), ('models', models), ('cases', ids)):
        gone = [x for x in cfg.get(key) or [] if x not in have]
        if gone:
            warn.append(f'bench.json {key}: not in this plan: {", ".join(gone)}')
    if envs.division() == 'plain' and any(r['step'] != '0' for r in rows) and not any(r['step'] == '0' for r in rows):
        measured = [d for root in (envs.WORK, envs.PUBLISHED) for d in (root / 'plain' / env_id).glob('*/cases/T0-*/summary.json')
                    if not d.parts[-4].startswith('test-')]
        if not measured:
            warn.append('Tier 0 (the instruments checked: launches, the author\'s values, the game\'s layout) has never been '
                        'measured in this environment; worth running once ("tiers": ["0", ...])')
    return plan, rows, warn


def estimate(env_id, rows):
    """Hours per Tier for these rows, as scripts/build_cases.py estimates the plan (requests and engine launches)."""
    import contextlib
    import io
    import build_cases
    with contextlib.redirect_stderr(io.StringIO()):
        build_cases.use_env(envs.load(env_id))
    return build_cases.estimate(rows)


def cmd_plan(a):
    cfg = config.load()
    env_id = envs.current()
    div = envs.division()
    plan, rows, warn = chosen(cfg, env_id)
    run = cfg['run_id']
    done = set()
    if run:
        rd = envs.run_dir(env_id, run, div)
        done = {r['id'] for r in rows if (rd / 'cases' / r['id'] / 'summary.json').exists()}
    print(f'division {div}, environment {env_id}, run {run or "(run_id not set)"}')
    print(f'chosen: {len(rows)} of {len(plan)} cases' + (f' ({len(done)} already measured in {run}: skipped)' if done else ''))
    todo = [r for r in rows if r['id'] not in done]
    est = estimate(env_id, todo)
    print(f'{"Tier":>5} {"cases":>6} {"models":>6} {"requests":>8} {"est h":>6}')
    for step, e in est.items():
        sel = [r for r in todo if r['step'] == step]
        print(f'{step:>5} {len(sel):>6} {len({(r["family"], r["model"]) for r in sel}):>6} '
              f'{sum(r.get("requests") or 0 for r in sel):>8} {e["total_h"]:>6.1f}')
    print(f'{"all":>5} {len(todo):>6} {len({(r["family"], r["model"]) for r in todo}):>6} '
          f'{sum(r.get("requests") or 0 for r in todo):>8} {sum(e["total_h"] for e in est.values()):>6.1f}'
          '   (hours: requests and engine launches, as the case lists estimate them)')
    for w in warn:
        print(f'note: {w}')
    return 0 if rows else 1


def cmd_start(a):
    cfg = config.load(need_run_id=True)
    env_id = envs.current()
    div = envs.division(measuring=True)
    run_dir = envs.run_dir(env_id, cfg['run_id'], div)
    print(f'division: {div}, environment: {env_id}, run: {run_dir.relative_to(ROOT)}')
    if supervisor_pid(run_dir):
        print(f'already running (pid {supervisor_pid(run_dir)})')
        return cmd_status(a)
    cur = load(CURRENT)
    if cur.get('run_dir') and supervisor_pid(ROOT / cur['run_dir']):
        raise SystemExit(f'another run is running: {cur["run_dir"]} (scripts/bench.py stop first)')
    fetch = ['--no-fetch'] if not cfg['fetch'] else []
    if subprocess.run(PY + ['scripts/setup_acquire.py'] + fetch, cwd=ROOT).returncode != 0:
        return 1
    plan, rows, warn = chosen(cfg, env_id)
    for w in warn:
        print(f'note: {w}')
    if not rows:
        raise SystemExit('nothing chosen: no case of the plan matches bench.json "tiers", "models" and "cases" (scripts/bench.py plan)')
    if subprocess.run(PY + ['scripts/acquire.py', 'check'], cwd=ROOT).returncode != 0:
        if not cfg['fetch']:
            print('not started: something the run needs is missing (above). Choose what to do with it (AGENTS.md 2.0a);')
            print('to let jbench fetch it, set "fetch": true in bench.json')
            return 1
        if subprocess.run(PY + ['scripts/acquire.py', 'fetch', '--all', '--yes', '--skip-models'], cwd=ROOT).returncode != 0:
            return 1
    run_dir.mkdir(parents=True, exist_ok=True)
    # the settings this start runs with, the defaults filled in (published with the run, like env.json)
    resolved = {**cfg, 'env': env_id, 'division': div}
    (run_dir / 'bench.json').write_text(json.dumps(resolved, ensure_ascii=False, indent=2) + '\n')
    with (run_dir / 'bench-starts.jsonl').open('a') as f:
        f.write(json.dumps({'at': datetime.now().astimezone().isoformat(timespec='seconds'), **resolved}, ensure_ascii=False) + '\n')
    STATUS.mkdir(exist_ok=True)
    CURRENT.write_text(json.dumps({'division': div, 'env': env_id, 'run_id': cfg['run_id'],
                                   'run_dir': str(run_dir.relative_to(ROOT)), 'tiers': cfg['tiers'], 'models': cfg['models'],
                                   'cases': cfg['cases'], 'started_at': datetime.now().astimezone().isoformat(timespec='seconds')},
                                  ensure_ascii=False) + '\n')
    with (run_dir / 'supervise.err').open('a') as err:
        subprocess.Popen(PY + ['scripts/supervise.py', str(run_dir)], cwd=ROOT, stdin=subprocess.DEVNULL,
                         stdout=err, stderr=subprocess.STDOUT, start_new_session=True,
                         env={k: v for k, v in os.environ.items() if k not in ('BENCH_CONFIG',)})
    time.sleep(3)
    return cmd_status(a)


def current_run(a):
    cur = load(CURRENT)
    if not cur.get('run_dir'):
        raise SystemExit('no run started yet (run-status/current-run.json)')
    return cur


def cmd_status(a):
    cur = current_run(a)
    env = {**os.environ, 'BENCH_DIVISION': cur['division'], 'BENCH_CONFIG': str(ROOT / cur['run_dir'] / 'bench.json')}
    r = subprocess.run(PY + ['scripts/healthcheck.py', '--run-id', cur['run_id'], '--env', cur['env'],
                             *(['--quiet'] if getattr(a, 'json', False) else [])], cwd=ROOT, env=env)
    if getattr(a, 'json', False):
        st = load(STATUS / 'status.json')
        st['supervisor_pid'] = supervisor_pid(ROOT / cur['run_dir'])
        print(json.dumps(st, ensure_ascii=False, indent=2))
    return r.returncode


def cmd_stop(a):
    cur = current_run(a)
    run_dir = ROOT / cur['run_dir']
    pid = supervisor_pid(run_dir)
    if pid:
        os.kill(pid, signal.SIGTERM)       # it stops its children and the engine, and logs "queue stopped"
        for _ in range(120):
            if not alive(pid):
                break
            time.sleep(1)
    # children left behind by a supervisor that died or would not stop
    for name, cpid in (load(run_dir / 'supervisor.json').get('children') or {}).items():
        if alive(cpid):
            try:
                os.killpg(int(cpid), signal.SIGTERM)
                print(f'stopped {name} (pid {cpid})')
            except OSError:
                pass
    if pid and alive(pid):
        os.kill(pid, signal.SIGKILL)
    subprocess.run(['strata', 'launch', '--stop'], capture_output=True, cwd='/tmp')
    q = run_dir / 'queue.log'
    last = q.read_text(errors='replace').strip().splitlines()[-1:] if q.exists() else []
    if last and not any(w in last[0] for w in ('queue stopped', 'queue finished')):
        with q.open('a') as f:
            f.write(f'{datetime.now().astimezone().isoformat(timespec="seconds")} queue stopped\n')
    print('stopped')
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    for name in ('config', 'status'):
        sub.add_parser(name).add_argument('--json', action='store_true')
    for name in ('plan', 'start', 'stop'):
        sub.add_parser(name)
    a = ap.parse_args()
    return {'config': cmd_config, 'plan': cmd_plan, 'start': cmd_start, 'status': cmd_status, 'stop': cmd_stop}[a.cmd](a)


if __name__ == '__main__':
    sys.exit(main())
