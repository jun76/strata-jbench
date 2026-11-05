"""Check, in minutes, everything a long unattended run will need, before starting it.

  python3 scripts/preflight.py [--phase acquire|bench|all] [--steps 0,1,2,3,4a,4b,4c,4d,5] [--env <id>]

The bench checks are for the environment this hardware matches (scripts/envs.py; --env or $BENCH_ENV must match it).

Each check runs the real step in a cheap form (imports the converter, asks strata launch for a plan, sends one request),
so a failure that would surface hours into the run surfaces now. Exit code 0 only when every check passes.
Writes run-status/preflight.json.
"""
import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import envs  # noqa: E402
import overnight  # noqa: E402  (paths and model completeness of the acquisition phase)

results = []


def check(name, ok, detail=''):
    results.append({'check': name, 'ok': bool(ok), 'detail': str(detail)[:500]})
    print(f'[{"ok" if ok else "NG"}] {name}' + (f': {detail}' if detail and not ok else ''), flush=True)
    return ok


def run(args, timeout=120, **kw):
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=timeout, **kw)
        return r.returncode, r.stdout + r.stderr
    except (OSError, subprocess.TimeoutExpired) as e:
        return -1, str(e)


def acquire_checks():
    m = overnight.manifest()
    root = overnight.models_root()
    # a file listed under two models (a shard shared by quantizations) is stored once: the downloader hard-links it, also
    # to a copy already on disk
    have = {f['sha256'] for f in m['files'] if (root / f['path']).is_file() and (root / (f['path'] + '.done')).is_file()}
    left = sum({f['sha256']: f['bytes'] for f in m['files'] if f['sha256'] not in have
                and not (f['model'] == 'NVFP4-QAD' and overnight.qad_prepared())}.values())
    free = shutil.disk_usage(root).free
    has_qad = any(f['model'] == 'NVFP4-QAD' for f in m['files'])
    qad_extra = 0 if overnight.qad_prepared() or not has_qad else 115e9
    check('disk: free space covers the remaining downloads + QAD prepare + 10 GB (the downloader stops below that)',
          free > left + qad_extra + 10e9, f'free {free / 1e9:.0f} GB, need {(left + qad_extra) / 1e9:.0f} GB + 10')
    rc, out = run([str(overnight.DL_PYTHON), '-c', 'import sys; print(sys.version)'])
    check('downloader python runs (python3 -I scripts/setup_acquire.py)', rc == 0, out)
    if has_qad and not overnight.qad_prepared():
        # the step that failed on 2026-11-03: import the converter exactly as prepare does
        rc, out = run([str(overnight.QAD_PYTHON), '-c',
                       'import sys; sys.path[:0] = ["tools"]; import nvfp4_convert, nvfp4_local_pack; print("ok")'],
                      cwd=overnight.QAD_ROOT)
        check('QAD prepare: converter imports (torch, transformers, gguf, llama.cpp conversion; '
              'python3 -I scripts/setup_acquire.py)', rc == 0, out[-400:])


def env_check(explicit):
    """The environment this hardware is; None (and an NG) when no single one matches."""
    try:
        env_id = envs.current(explicit)
    except SystemExit as e:
        check('environment: this hardware matches one envs/<id>/env.json', False, e)
        return None
    check(f'environment: this hardware is {env_id}', True)
    plan = envs.plan_dir(env_id) / 'cases.jsonl'
    fresh = plan.exists() and plan.stat().st_mtime >= (envs.ENVS / env_id / 'env.json').stat().st_mtime
    check(f'plan: {plan.relative_to(ROOT)} exists and is newer than env.json (python3 -I scripts/build_cases.py)', fresh)
    return env_id if fresh else None


def bench_checks(steps, env_id):
    cfg = envs.load(env_id)
    rows = [json.loads(l) for l in (envs.plan_dir(env_id) / 'cases.jsonl').read_text().splitlines()]
    rows = [r for r in rows if r['step'] in steps]
    # Tier 2 sends standard-v1's own frozen bundle through strata bench run, not prompts/
    missing = sorted({r['fixture'] for r in rows
                      if r['step'] != '2' and not (ROOT / 'prompts' / f'{r["fixture"]}.json').exists()})
    check('fixtures: every case of the selected steps has its prompt file', not missing, ', '.join(missing))
    models = list(dict.fromkeys((r['family'], r['model']) for r in rows))
    card = str(envs.gpu_index(cfg))              # the environment's card: the runner launches on it alone (--gpu)
    bad = []
    for fam, model in models:
        rc, out = run(['strata', 'launch', '--plan', '--family', fam, '--model', model, '--context', '128k',
                       '--vision', 'off', '--parallel', '1', '--tune', 'skip', '--port', '18600', '--drafting', 'mtp',
                       '--gpu', card, '--output', 'json'], timeout=180, cwd='/tmp')
        try:
            plan = json.loads(out[out.index('{'):])['plan']
            if plan['download']['gb']:
                bad.append(f'{fam}:{model} would download {plan["download"]["gb"]} GB')
        except (ValueError, KeyError) as e:
            bad.append(f'{fam}:{model} plan failed ({e}): {out[-200:]}')
    check(f'strata launch --plan: {len(models)} models need no download', not bad, '; '.join(bad))
    # "mtp": false in a model's installed config (left by an earlier --mtp off / --drafting off that ran setup) keeps
    # the draft layer off at every launch, --mtp on included; only setup's own --mtp on writes --mtp <data>/mtp/rt back
    install = Path.home() / '.local/share/strata/install'
    off = []
    for fam, model in models:
        conf = install / f'strata-{model.lower() if fam == "qwen" else f"{fam}-{model.lower()}"}.json'
        try:
            if json.loads(conf.read_text()).get('mtp') is False:
                off.append(f'{fam}:{model} ({conf.name})')
        except (OSError, ValueError):
            pass
    check('installed configs: no model has the MTP draft layer switched off ("mtp": false)', not off,
          '; '.join(off) + ' - run Control setup.py --yes --no-start --family F --model M --mtp on (AGENTS.md 5)')
    # The DFlash2 cases: the drafter must be on disk before, not fetched in the middle of a measurement.
    dflash = sorted({(r['family'], r['model']) for r in rows if '--drafting dflash2' in r['launch_opts']})
    if dflash:
        fam, model = dflash[0]
        rc, out = run(['strata', 'launch', '--plan', '--family', fam, '--model', model, '--context', '128k', '--vision', 'off',
                       '--parallel', '1', '--tune', 'skip', '--port', '18600', '--drafting', 'dflash2', '--gpu', card,
                       '--output', 'json'],
                      timeout=180, cwd='/tmp')
        try:
            gb = json.loads(out[out.index('{'):])['plan']['download']['gb']
        except (ValueError, KeyError):
            gb = None
        check('DFlash2 drafter is on disk (strata drafting fetch)', gb == 0, f'plan download {gb} GB')
    want = cfg.get('gpu_power_limit_w')
    if want:
        rc, out = run(['nvidia-smi', '-i', card, '--query-gpu=power.limit', '--format=csv,noheader,nounits'])
        limit = float(out.split()[0]) if rc == 0 and out.strip() else None
        check(f'GPU power limit is {want:g} W (env.json; gpu-power-limit.service)', limit is not None and abs(limit - want) < 1,
              f'{limit} W')
    rc, out = run(['nvidia-smi', '-i', card, '--query-gpu=memory.used', '--format=csv,noheader,nounits'])
    used = int(out.split()[0]) if rc == 0 and out.strip() else None
    check(f'GPU {card}: no other engine holds VRAM (< 4 GB used)', used is not None and used < 4000, f'{used} MiB')
    rc, out = run(['pgrep', '-af', 'strata --serve'])
    check('no other Strata engine is running', rc != 0, out)
    chrome = shutil.which('google-chrome') or shutil.which('chromium')
    check('headless Chrome for game screenshots', chrome, 'not found')
    free = shutil.disk_usage(ROOT).free
    check('disk: 50 GB free for packs built at first launch and results', free > 50e9, f'{free / 1e9:.0f} GB')


def smoke(env_id):
    """One real session: launch the environment's smallest model, three short requests, stop. The runner fails the
    case when the MTP draft layer it asked for did not load, so this also checks the drafter pinning."""
    rows = [json.loads(l) for l in (envs.plan_dir(env_id) / 'cases.jsonl').read_text().splitlines()]
    sizes = {(f, m): gb for f, m, gb, _ in overnight_models()}
    case = min((r for r in rows if r['step'] == '1' and r['fixture'] == 'decode-prose-en' and r['config'] == 'baseline'
                and r['temperature'] == 0.7), key=lambda r: sizes.get((r['family'], r['model']), 1e9))
    rc, out = run([sys.executable, 'scripts/bench_runner.py', '--run-id', 'test-preflight', '--steps', '1', '--env', env_id,
                   '--ids', case['id']], timeout=1800, cwd=ROOT)
    run_dir = envs.run_dir(env_id, 'test-preflight')
    s = run_dir / 'cases' / case['id'] / 'summary.json'
    ok = s.exists() and json.loads(s.read_text()).get('status') == 'done'
    check(f'smoke: launch (MTP loaded) + 3 requests + stop on {case["family"]} {case["model"]}', ok, out[-400:])
    shutil.rmtree(run_dir, ignore_errors=True)


def overnight_models():
    import build_cases
    return build_cases.MODELS


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--phase', choices=['acquire', 'bench', 'all'], default='all')
    ap.add_argument('--steps', default='0,1,2,3,4a,4b,4c,4d,5')
    ap.add_argument('--no-smoke', action='store_true', help='skip the one real launch (when a run is using the GPU)')
    ap.add_argument('--env', default='', help='the environment (default: the one this hardware matches)')
    a = ap.parse_args()
    env_id = None
    if a.phase in ('acquire', 'all'):
        acquire_checks()
    if a.phase in ('bench', 'all'):
        env_id = env_check(a.env)
        if env_id:
            bench_checks(a.steps.split(','), env_id)
            if not a.no_smoke and all(r['ok'] for r in results):
                smoke(env_id)
    out = ROOT / 'run-status'
    out.mkdir(exist_ok=True)
    ok = all(r['ok'] for r in results)
    (out / 'preflight.json').write_text(json.dumps({
        'ok': ok, 'at': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'phase': a.phase, 'env': env_id,
        'checks': results}, ensure_ascii=False, indent=2) + '\n')
    print('PREFLIGHT', 'PASSED' if ok else 'FAILED')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
