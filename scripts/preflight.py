"""Check, in minutes, everything a long unattended run will need, before starting it.

  python3 scripts/preflight.py [--phase acquire|bench|all] [--steps 0,1,2,3,4a,4b,4c,4d,5] [--env <id>]

The bench checks are for the environment this hardware matches (scripts/envs.py; --env or $BENCH_ENV must match it).

Each check runs the real step in a cheap form (imports the converter, asks strata launch for a plan, sends one request),
so a failure that would surface hours into the run surfaces now. Exit code 0 only when every check passes.
Writes run-status/preflight.json.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import case_plan  # noqa: E402
import config  # noqa: E402
import engines  # noqa: E402
import envs  # noqa: E402
import overnight  # noqa: E402  (paths and model completeness of the acquisition phase)
import own_build  # noqa: E402

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
    has_qad = any(f['model'] == 'NVFP4-QAD' for f in m['files'])
    qad_extra = 0 if overnight.qad_prepared() or not has_qad else 115e9
    # per disk: a model folder may link to another one (Hy4-Flash's on rtx5090-128g); the QAD prepare is on the models disk
    disks = overnight.missing_by_disk([f for f in m['files'] if f['sha256'] not in have
                                       and not (f['model'] == 'NVFP4-QAD' and overnight.qad_prepared())])
    root_dev = os.stat(root).st_dev
    disks.setdefault(root.resolve(), (0, shutil.disk_usage(root).free))
    short = [f'{d}: free {fr / 1e9:.0f} GB, need {(b + (qad_extra if os.stat(d).st_dev == root_dev else 0)) / 1e9:.0f} GB + 10'
             for d, (b, fr) in disks.items() if fr <= b + (qad_extra if os.stat(d).st_dev == root_dev else 0) + 10e9]
    check('disk: free space covers the remaining downloads + QAD prepare + 10 GB (the downloader stops below that)',
          not short, '; '.join(short) or f'{left / 1e9:.0f} GB to fetch')
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
    settings = config.load()
    engine_id = settings.get('engine') or engines.DEFAULT
    rows = [json.loads(l) for l in (envs.plan_dir(env_id) / 'cases.jsonl').read_text().splitlines()]
    rows = [r for r in config.select(rows, {**settings, 'tiers': None, 'cases': None}) if r['step'] in steps]
    check(f'engine {engine_id}: the plan has cases for it in the selected steps', rows,
          'none: its builds are not among env.json "models", or the engine does not take these steps')
    # Tier 2 sends standard-v1's own frozen bundle through strata bench run, not prompts/
    missing = sorted({r['fixture'] for r in rows
                      if r['step'] != '2' and not (ROOT / 'prompts' / f'{r["fixture"]}.json').exists()})
    check('fixtures: every case of the selected steps has its prompt file', not missing, ', '.join(missing))
    models = list(dict.fromkeys((r['family'], r['model']) for r in rows))
    card = str(envs.gpu_index(cfg))              # the environment's card: the runner launches on it alone (--gpu)
    if engine_id == engines.DEFAULT:
        bad = []
        for fam, model in models:
            why = own_build.state(fam, model) if own_build.own(fam, model) else \
                own_build.pinned_state(fam, model) if own_build.pinned(fam, model) else None
            if why:        # a build with files of jbench's own (catalog "own"), or one file the catalog pins ("pinned")
                bad.append(f'{fam}:{model} {why}')
                continue
            sfam, smodel = own_build.target(fam, model)
            # a build with files of its own: every context of its cases (a launch at another context than the run config's
            # runs Strata's setup, which is where the known model's file would be fetched)
            ctxs = sorted({r['context'] for r in rows if (r['family'], r['model']) == (fam, model)}) \
                if own_build.own(fam, model) else [131072]
            for ctx in ctxs:
                rc, out = run(['strata', 'launch', '--plan', '--family', sfam, '--model', smodel, '--context', str(ctx),
                               '--vision', 'off', '--parallel', '1', '--tune', 'skip', '--port', '18600', '--drafting', 'mtp',
                               '--gpu', card, '--output', 'json', *own_build.launch_extra(fam, model)], timeout=180, cwd='/tmp',
                              env=own_build.env(fam, model))
                try:
                    plan = json.loads(out[out.index('{'):])['plan']
                    if plan['download']['gb']:
                        bad.append(f'{fam}:{model} at {ctx} would download {plan["download"]["gb"]} GB')
                except (ValueError, KeyError) as e:
                    bad.append(f'{fam}:{model} plan at {ctx} failed ({e}): {out[-200:]}')
        check(f'strata launch --plan: {len(models)} models need no download', not bad, '; '.join(bad))
        # "mtp": false in a model's installed config (left by an earlier --mtp off / --drafting off that ran setup) keeps
        # the draft layer off at every launch, --mtp on included; only setup's own --mtp on writes --mtp <data>/mtp/rt back
        install = Path.home() / '.local/share/strata/install'
        off = []
        for fam, model in models:
            if fam in case_plan.OWN_DRAFTER:   # its own drafter (DFly2, DFlash 2: catalog "drafter"), no MTP layer
                continue
            conf = own_build.config_path(fam, model)
            try:
                if json.loads(conf.read_text()).get('mtp') is False:
                    off.append(f'{fam}:{model} ({conf.name})')
            except (OSError, ValueError):
                pass
        check('installed configs: no model has the MTP draft layer switched off ("mtp": false)', not off,
              '; '.join(off) + ' - run Control setup.py --yes --no-start --family F --model M --mtp on (AGENTS.md 5)')
        # a saved tuning active for a model's choices is put over every start of it (strata presets effective)
        tuned = [f'{fam}:{model} {t}' for fam, model in models
                 if (t := engines.get(engines.DEFAULT, gpu=int(card), dry=True).saved_tuning(own_build.config_path(fam, model)))]
        check('saved tunings: no preset of Strata\'s tuner changes a measuring launch', not tuned,
              '; '.join(tuned) + ' - strata presets off <run config> switches it off (Strata\'s saved settings: ask first)')
        # The DFlash2 cases: the drafter must be on disk before, not fetched in the middle of a measurement.
        dflash = sorted({(r['family'], r['model']) for r in rows if '--drafting dflash2' in r['launch_opts']})
        if dflash:
            fam, model = dflash[0]
            sfam, smodel = own_build.target(fam, model)
            rc, out = run(['strata', 'launch', '--plan', '--family', sfam, '--model', smodel, '--context', '128k', '--vision', 'off',
                           '--parallel', '1', '--tune', 'skip', '--port', '18600', '--drafting', 'dflash2', '--gpu', card,
                           '--output', 'json', *own_build.launch_extra(fam, model)],
                          timeout=180, cwd='/tmp', env=own_build.env(fam, model))
            try:
                gb = json.loads(out[out.index('{'):])['plan']['download']['gb']
            except (ValueError, KeyError):
                gb = None
            check('DFlash2 drafter is on disk (strata drafting fetch)', gb == 0, f'plan download {gb} GB')
    else:
        # another engine: what its adapter can check without starting it (it is here, its models are on disk, ...)
        eng = engines.get(engine_id, gpu=int(card), track=settings.get('track'), dry=True,
                          run_dir=Path(os.environ.get('BENCH_ENGINE_HOME') or ROOT / 'run-status'),
                          **{k: settings.get(k) for k in ('engine_url', 'engine_path', 'engine_note')})
        for what, ok, detail in eng.preflight(models):
            check(what, ok, detail)
    want = cfg.get('gpu_power_limit_w')
    if want:
        rc, out = run(['nvidia-smi', '-i', card, '--query-gpu=power.limit', '--format=csv,noheader,nounits'])
        limit = float(out.split()[0]) if rc == 0 and out.strip() else None
        check(f'GPU power limit is {want:g} W (env.json; gpu-power-limit.service)', limit is not None and abs(limit - want) < 1,
              f'{limit} W')
    want = cfg.get('cpu_power_limit_w')
    if want:
        import machine_info
        have = machine_info.cpu_power_limits() or {}
        check(f'CPU power limits are PL1 {want["pl1"]} W / PL2 {want["pl2"]} W (env.json; BIOS or intel-rapl)',
              all(have.get(k) is not None and abs(have[k] - want[k]) < 1 for k in ('pl1', 'pl2')),
              f'PL1 {have.get("pl1")} W / PL2 {have.get("pl2")} W')
    rc, out = run(['nvidia-smi', '-i', card, '--query-gpu=memory.used', '--format=csv,noheader,nounits'])
    used = int(out.split()[0]) if rc == 0 and out.strip() else None
    check(f'GPU {card}: no other engine holds VRAM (< 4 GB used)', used is not None and used < 4000, f'{used} MiB')
    if engine_id != 'endpoint':
        rc, out = run(['pgrep', '-af', 'strata --serve'])
        check('no other Strata engine is running', rc != 0, out)
    chrome = shutil.which('google-chrome') or shutil.which('chromium')
    check('headless Chrome for game screenshots', chrome, 'not found')
    # the packs a first launch builds (about 1.5 GB a model; a canonical Q2_0 pack on an AVX-512 CPU about 40 GB) plus the
    # same 10 GB headroom as the downloader (results are well under 1 GB a run without raw/)
    packs = Path.home() / '.local/share/strata/Strata-data/packs'
    new = [m for _, m in models if not (packs / m.lower()).exists() and not any(packs.glob(f'*-{m.lower()}'))] \
        if engine_id == engines.DEFAULT else []
    q2 = any(m == 'Q2_0' for m in new) and 'avx512f' in Path('/proc/cpuinfo').read_text()
    need = 10e9 + 2e9 * len(new) + (40e9 if q2 else 0)
    free = shutil.disk_usage(ROOT).free
    check(f'disk: {need / 1e9:.0f} GB free (packs of {len(new)} models not launched yet + 10 GB)', free > need,
          f'{free / 1e9:.0f} GB')


def harness_checks(div):
    """A harness division: what scripts/acquire.py checks (the pinned harness, bubblewrap), then the harness once against
    the mock engine through the proxy (no GPU): its configuration, the sandbox and the reading of its output."""
    import harnesses
    found = harnesses.find(div)
    check(f'harness {div}: the pinned version is installed (python3 -I scripts/acquire.py check)', found['ok'], found['reason'])
    check('bubblewrap (bwrap) for the harness sandbox', shutil.which('bwrap'), 'not found')
    if found['ok'] and shutil.which('bwrap'):
        import tempfile
        with tempfile.TemporaryDirectory(prefix='jbench-harness-') as tmp:
            try:
                ok, detail = harnesses.selfcheck(div, tmp)
            except SystemExit as e:
                ok, detail = False, str(e)
        check(f'harness {div}: one task against the mock engine through the proxy, in the sandbox', ok, detail)


def smoke(env_id):
    """One real session on the engine the settings name: start its smallest model in the plan, three short requests,
    stop. The runner fails the case when what it asked of the engine cannot be confirmed (Strata: the MTP draft layer
    loaded, the launch choices reached the engine), so this checks that too. It is plain's Tier 1 case whatever the
    division (the engine side is the same)."""
    settings = config.load()
    engine_id = settings.get('engine') or engines.DEFAULT
    rows = [json.loads(l) for l in (envs.plan_dir(env_id, 'plain') / 'cases.jsonl').read_text().splitlines()]
    rows = config.select(rows, {**settings, 'tiers': None, 'cases': None})
    sizes = {(f, m): gb for f, m, gb, _ in overnight_models()}
    cand = [r for r in rows if r['step'] == '1' and r['fixture'] == 'decode-prose-en' and r['config'] == 'baseline'
            and r['temperature'] == 0.7]
    if not cand:
        check(f'smoke: a Tier 1 case of engine {engine_id} to try', False, 'the plan has none')
        return
    case = min(cand, key=lambda r: sizes.get((r['family'], r['model']), 1e9))
    run_dir = envs.run_dir(env_id, 'test-preflight', 'plain')
    rc, out = run([sys.executable, 'scripts/bench_runner.py', '--run-id', 'test-preflight', '--steps', '1', '--env', env_id,
                   '--ids', case['id'], '--engine', engine_id], timeout=1800, cwd=ROOT,
                  env={**os.environ, 'BENCH_DIVISION': 'plain', 'BENCH_ENGINE_HOME': str(run_dir)})
    s = run_dir / 'cases' / case['id'] / 'summary.json'
    ok = s.exists() and json.loads(s.read_text()).get('status') == 'done'
    check(f'smoke: engine {engine_id}: launch (settings confirmed) + 3 requests + stop on {case["family"]} {case["model"]}',
          ok, out[-400:])
    shutil.rmtree(run_dir, ignore_errors=True)


def overnight_models():
    return case_plan.MODELS


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--phase', choices=['acquire', 'bench', 'all'], default='all')
    ap.add_argument('--steps', default='', help='default: 0,1,2,3,4a,4b,4c,4d,5, or G in a harness division')
    ap.add_argument('--no-smoke', action='store_true', help='skip the one real launch (when a run is using the GPU)')
    ap.add_argument('--env', default='', help='the environment (default: the one this hardware matches)')
    a = ap.parse_args()
    env_id = None
    if a.phase in ('acquire', 'all'):
        if (config.load().get('engine') or engines.DEFAULT) == engines.DEFAULT:
            acquire_checks()
        else:
            import acquire     # another engine: what its adapter says the run needs (scripts/acquire.py check)
            found = acquire.check(envs.current(a.env), envs.division())
            check('everything the run needs is on disk (python3 -I scripts/acquire.py check)', found['ok'],
                  ', '.join(i['what'] for i in found['items'] if i['state'] != 'ok'))
    if a.phase in ('bench', 'all'):
        env_id = env_check(a.env)
        if env_id:
            harness = envs.load_division(envs.division()).get('harness')
            bench_checks((a.steps or ('G' if harness else '0,1,2,3,4a,4b,4c,4d,5')).split(','), env_id)
            if envs.load_division(envs.division()).get('harness'):
                harness_checks(envs.division())
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
