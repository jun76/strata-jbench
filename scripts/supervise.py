"""The run's supervisor: everything a run does after `scripts/bench.py start`, in one process detached from the terminal
and from the agent's session (AGENTS.md 1.1).

    python3 -I scripts/supervise.py <run dir>       # started by scripts/bench.py start, never by hand

It reads the settings the run started with (<run dir>/bench.json, written by bench.py start; scripts/config.py) and:
  1. with "fetch", starts scripts/overnight.py when models are missing (downloads, the NVFP4-QAD conversion), and waits
     until what the run needs is on disk (scripts/acquire.py check; without "fetch" bench.py start has checked it)
  2. Strata's run configs for the models fetched (scripts/install_configs.py; it changes Strata's saved settings)
  3. preflight (scripts/preflight.py, with one real launch unless "smoke" is false)
  4. scripts/stats_watch.py beside the run (unless "stats" is false)
  5. scripts/bench_runner.py Tier by Tier, in the order of "tiers", for the models and cases chosen; the case lists and
     the charts after each Tier (preview/); then scripts/verify_run.py
While it runs it checks the run every "watch_interval_s" (scripts/healthcheck.py: run-status/STATUS.md, ALERTS.log,
notifications). A runner that exits with an error is started again up to "crash_restarts" times, and one that has
written nothing for longer than any step needs is stopped and started again up to "stuck_restarts" times (finished
cases are skipped either way); past that the Tier is left FAILED and the next Tier runs.

Its records are the run's queue.log (one line per stage, and the runner's output) and queue.pid; supervisor.json names
the process groups of its children, so that bench.py stop reaches them even if this process is gone. A run that ends,
is stopped or fails says so in the last line of queue.log ("queue finished", "queue stopped", ...).
"""
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import config  # noqa: E402
import envs  # noqa: E402

PY = [sys.executable, '-I']
RUN_DIR = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else None
CHILDREN = {}            # name: Popen, each in a process group of its own
STATE = {}


def stamp():
    return datetime.now().astimezone().isoformat(timespec='seconds')


def log(msg):
    with (RUN_DIR / 'queue.log').open('a') as f:
        f.write(f'{stamp()} {msg}\n')


def save_state():
    (RUN_DIR / 'supervisor.json').write_text(json.dumps(
        {'pid': os.getpid(), 'started_at': STATE.get('started_at'),
         'children': {k: p.pid for k, p in CHILDREN.items() if p.poll() is None}}, indent=2) + '\n')


def spawn(name, cmd, out=None):
    """A child in its own process group (so that a stuck runner can be stopped with everything it started)."""
    f = open(out or RUN_DIR / 'queue.log', 'a')
    p = subprocess.Popen(cmd, cwd=ROOT, stdout=f, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True)
    f.close()
    CHILDREN[name] = p
    save_state()
    return p


def stop_child(name, grace=60):
    p = CHILDREN.pop(name, None)
    if p and p.poll() is None:
        try:
            os.killpg(p.pid, signal.SIGTERM)
            p.wait(grace)
        except subprocess.TimeoutExpired:
            os.killpg(p.pid, signal.SIGKILL)
            p.wait()
        except ProcessLookupError:
            pass
    save_state()


def run(cmd):
    """A short step, its output into queue.log; its exit code."""
    with (RUN_DIR / 'queue.log').open('a') as f:
        return subprocess.run(cmd, cwd=ROOT, stdout=f, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL).returncode


def health():
    """One look (scripts/healthcheck.py writes STATUS.md and notifies); the bench part's state."""
    subprocess.run(PY + ['scripts/healthcheck.py', '--quiet', '--run-id', RUN_DIR.name, '--env', STATE['env']],
                   cwd=ROOT, capture_output=True)
    try:
        st = json.loads((ROOT / 'run-status/status.json').read_text())
        return next((p['state'] for p in st['parts'] if p['phase'] == 'bench'), None)
    except (OSError, ValueError, KeyError):
        return None


def notify(text):
    if STATE['cfg']['notify']:
        subprocess.run(['notify-send', 'strata-jbench', text], capture_output=True)


def on_term(signum, frame):
    for name in list(CHILDREN):
        stop_child(name, grace=30)
    subprocess.run(['strata', 'launch', '--stop'], capture_output=True, cwd='/tmp')
    log('queue stopped')
    health()
    sys.exit(143)


def overnight_alive():
    p = CHILDREN.get('acquire')
    if p and p.poll() is None:
        return True
    try:
        os.kill(int(json.loads((ROOT / 'downloads/overnight-state.json').read_text())['pid']), 0)
        return True
    except (OSError, ValueError, KeyError):
        return False


def wait_on_disk(cfg):
    """Step 1: until acquire.py check passes; False when something is missing and nothing is fetching it."""
    if cfg['fetch'] and not (ROOT / 'downloads/READY').exists() and not overnight_alive():
        if run(PY + ['scripts/acquire.py', 'check']) != 0:
            log('fetching the models (scripts/overnight.py, downloads/overnight.log)')
            spawn('acquire', [str(ROOT / '.venv-hf/bin/python'), '-u', 'scripts/overnight.py'],
                  out=ROOT / 'downloads/overnight.out')
    last = 0
    said = False
    # nothing is fetched while the run measures (AGENTS.md 1.8): with the run's own models here, the downloads of other
    # models of env.json are waited for too
    while subprocess.run(PY + ['scripts/acquire.py', 'check'], cwd=ROOT, capture_output=True).returncode != 0 or overnight_alive():
        if not overnight_alive():
            log('something the run needs is missing and nothing is fetching it; stopping (run-status/acquire.json)')
            return False
        if not said and subprocess.run(PY + ['scripts/acquire.py', 'check'], cwd=ROOT, capture_output=True).returncode == 0:
            log('waiting until the downloads end (nothing is fetched during a measurement)')
            said = True
        if time.time() - last > cfg['watch_interval_s']:
            health()
            last = time.time()
        time.sleep(60)
    CHILDREN.pop('acquire', None)
    save_state()
    return True


def run_tier(step, cfg, models, ids):
    """Step 5 for one Tier, with the restarts the settings allow; the runner's last exit code."""
    cmd = PY[:1] + ['scripts/bench_runner.py', '--run-id', RUN_DIR.name, '--steps', step]
    if models:
        cmd += ['--models', ','.join(m.replace(' ', ':', 1) for m in models)]
    if ids:
        cmd += ['--ids', ','.join(ids)]
    crashes = stucks = 0
    while True:
        p = spawn('runner', cmd)
        last = time.time()
        stuck = False
        while p.poll() is None:
            time.sleep(15)
            if time.time() - last >= cfg['watch_interval_s']:
                last = time.time()
                if health() == 'STUCK':
                    stuck = True
                    break
        if stuck:
            stop_child('runner')
            subprocess.run(['strata', 'launch', '--stop'], capture_output=True, cwd='/tmp')
            stucks += 1
            if stucks > cfg['stuck_restarts']:
                log(f'steps {step}: the runner was stuck {stucks} time(s); giving up on this Tier')
                return 124
            log(f'steps {step}: the runner wrote nothing for too long; stopped, starting again ({stucks}/{cfg["stuck_restarts"]})')
            continue
        CHILDREN.pop('runner', None)
        rc = p.returncode
        if rc == 0:
            return 0
        crashes += 1
        if crashes > cfg['crash_restarts']:
            return rc
        log(f'steps {step}: the runner ended with {rc}; starting again ({crashes}/{cfg["crash_restarts"]})')


def main():
    if not RUN_DIR or not (RUN_DIR / 'bench.json').exists():
        raise SystemExit('started by scripts/bench.py start (it needs the run folder with its bench.json)')
    cfg = config.load(RUN_DIR / 'bench.json', need_run_id=True)
    STATE.update(cfg=cfg, env=RUN_DIR.parent.name, started_at=stamp())
    # every script below reads the run's own settings, not bench.json as it may be edited meanwhile
    os.environ.update(BENCH_CONFIG=str(RUN_DIR / 'bench.json'), BENCH_DIVISION=RUN_DIR.parent.parent.name,
                      BENCH_ENV=STATE['env'], RUN_ID=RUN_DIR.name, BENCH_LAUNCH_TIMEOUT=str(cfg['launch_timeout_s']))
    signal.signal(signal.SIGTERM, on_term)
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    (RUN_DIR / 'queue.pid').write_text(f'{os.getpid()}\n')
    save_state()
    log(f'queue start (pid {os.getpid()}), waiting until what the run needs is on disk')
    run(PY + ['scripts/build_cases.py'])
    if not wait_on_disk(cfg):
        health()
        notify('the run did not start: something it needs is missing')
        return 1
    plan = [json.loads(x) for x in (envs.plan_dir(STATE['env']) / 'cases.jsonl').read_text().splitlines() if x.strip()]
    rows = config.select(plan, cfg)
    tiers = list(dict.fromkeys(r['step'] for r in rows))
    log('run configs')
    if run(PY + ['scripts/install_configs.py', '--env', STATE['env']]) != 0:
        log('run configs failed; not starting')
        health()
        return 1
    log('preflight')
    if run(PY + ['scripts/preflight.py', '--phase', 'bench', '--steps', ','.join(tiers)] + ([] if cfg['smoke'] else ['--no-smoke'])) != 0:
        log('preflight failed; not starting (see run-status/preflight.json)')
        health()
        notify('the run did not start: preflight failed')
        return 1
    if cfg['stats']:
        spawn('stats', PY + ['scripts/stats_watch.py', '--run-id', RUN_DIR.name, '--env', STATE['env']])
    # healthcheck.py reads these lines ("steps <s>" and "steps <s>: runner exit <rc>") and, after the queue, checks that
    # every chosen case of the steps run has a result
    failed = []
    for step in tiers:
        log(f'steps {step}')
        rc = run_tier(step, cfg, cfg['models'], cfg['cases'])
        log(f'steps {step}: runner exit {rc}')
        if rc != 0:
            failed.append(step)
        run(PY + ['scripts/build_cases.py'])
        run(PY + ['scripts/build_results.py'])
        health()
    rc = run(PY + ['scripts/verify_run.py', STATE['env'], RUN_DIR.name])
    log(f'steps verify: runner exit {rc}')
    if rc != 0:
        failed.append('verify')
    stop_child('stats', grace=30)
    log(f'queue finished with runner errors in steps {" ".join(failed)}' if failed else 'queue finished')
    state = health()
    notify(f'{RUN_DIR.name}: {state}')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
