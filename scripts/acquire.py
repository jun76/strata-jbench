#!/usr/bin/env python3
"""What a run needs on disk (models, the DFlash2 drafter, the NVFP4-QAD conversion, the harness), whether each is here,
and fetching the missing ones only after asking (AGENTS.md 2.0a).

    python3 -I scripts/acquire.py check [--env <id>]            # changes nothing; also writes run-status/acquire.json
    python3 -I scripts/acquire.py fetch <item>... [--yes]       # items as check names them: models, dflash2, harness:<division>
    python3 -I scripts/acquire.py fetch --all [--yes]

The division, the environment and the cases are bench.json's, as for the run (scripts/config.py; $BENCH_DIVISION
and $BENCH_ENV override them): what is needed is what the cases chosen use, from the environment's plan
(plan/<division>/<env>/cases.jsonl, scripts/build_cases.py).
Where each thing is looked for:
  models     Strata's models folder (downloads/manifest.json, pinned by Strata's setup.py: scripts/setup_acquire.py)
  dflash2    strata drafting plan, per model of the DFlash2 cases (the drafter Strata fetches with strata drafting fetch)
  harness    tools/harness/<division>/<version>/, then the harness's default place, at the pinned version only
             (divisions/<division>/division.json "pin"; scripts/harnesses.py)

fetch asks before each item (its size and source), unless --yes (for a fetch agreed beforehand, AGENTS.md 2.2):
  models     scripts/overnight.py (hf downloads, the NVFP4-QAD conversion) detached from the terminal, as the run's
             supervisor starts it with "fetch"; it runs for hours, so it is started and not waited for
  dflash2    strata drafting fetch
  harness    the pinned version into tools/harness/<division>/<version>/, never the user's global packages: npm
             --prefix, a venv for a pip pin (Hermes Agent at its tagged commit), or the Strata app's AppImage checked
             against its SHA-256 and extracted (scripts/harnesses.py install)
Nothing is fetched while a benchmark queue is running (AGENTS.md 1.8).
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
import config  # noqa: E402
import envs  # noqa: E402
import harnesses  # noqa: E402
import install_configs  # noqa: E402
import overnight  # noqa: E402


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def gb(n):
    return f'{n / 1e9:.1f} GB'


def queue_running():
    """The benchmark queue of the run started last, if its recorded PID is alive."""
    try:
        cur = json.loads((ROOT / 'run-status/current-run.json').read_text())
        pid = int((ROOT / cur['run_dir'] / 'queue.pid').read_text())
        os.kill(pid, 0)
        return f'{cur["run_dir"]} (pid {pid})'
    except (OSError, ValueError, KeyError):
        return None


def overnight_running():
    try:
        os.kill(int(json.loads((ROOT / 'downloads/overnight-state.json').read_text())['pid']), 0)
        return True
    except (OSError, ValueError, KeyError):
        return False


def needed(env_id, div):
    """The models and the drafter the cases bench.json chooses from the environment's plan for this division use."""
    plan = envs.plan_dir(env_id, div) / 'cases.jsonl'
    if not plan.exists():
        raise SystemExit(f'{plan.relative_to(ROOT)} is missing: python3 -I scripts/build_cases.py (with BENCH_DIVISION={div})')
    rows = config.select([json.loads(x) for x in plan.read_text().splitlines() if x.strip()], config.load())
    models = list(dict.fromkeys((r['family'], r['model']) for r in rows))
    return models, list(dict.fromkeys((r['family'], r['model']) for r in rows if '--drafting dflash2' in r['launch_opts']))


def model_items(models):
    m = overnight.manifest()
    root = overnight.models_root()
    items = []
    for fam, model in models:
        files = [f for f in m['files'] if (f.get('family'), f['model']) == (fam, model)]
        if not files:
            items.append({'item': 'models', 'what': f'{fam} {model}', 'state': 'not in downloads/manifest.json',
                          'fix': 'python3 -I scripts/setup_acquire.py (env.json "models")', 'bytes': None})
            continue
        if model == 'NVFP4-QAD' and overnight.qad_prepared():
            items.append({'item': 'models', 'what': f'{fam} {model}', 'state': 'ok', 'detail': 'converted'})
            continue
        left = [f for f in files if not ((root / f['path']).is_file() and (root / (f['path'] + '.done')).is_file())]
        if not left:
            items.append({'item': 'models', 'what': f'{fam} {model}', 'state': 'ok'})
            continue
        items.append({'item': 'models', 'what': f'{fam} {model}', 'state': 'missing', 'bytes': sum(f['bytes'] for f in left),
                      'source': 'huggingface.co (pinned by Strata setup.py)', 'fix': 'python3 -I scripts/acquire.py fetch models'})
    return items


def drafting_args(fam, model):
    """strata drafting plan / fetch for one model: its run config where there is one, since the drafter depends on the
    model (since 0.2.12 some take Strata's tuned pack, 0.34 GB, beside the stock one), else the family."""
    conf = install_configs.config_path(fam, model)
    return ['--config', str(conf)] if conf.exists() else ['--family', fam]


def dflash2_item(models):
    missing, gb_, source = [], 0.0, None
    for fam, model in models:
        r = subprocess.run(['strata', 'drafting', 'plan', *drafting_args(fam, model), '--mode', 'dflash2', '--output', 'json'],
                           capture_output=True, text=True, timeout=120, cwd='/tmp')
        try:
            j = json.loads(r.stdout[r.stdout.index('{'):])
        except ValueError:
            return {'item': 'dflash2', 'what': 'DFlash2 drafter', 'state': 'unknown', 'detail': (r.stdout + r.stderr)[-200:]}
        if not j.get('ready'):
            missing.append((fam, model))
            gb_ = max(gb_, j.get('gb') or 0)          # the models that lack one lack the same file
            source = source or j.get('repo')
    return {'item': 'dflash2', 'what': 'DFlash2 drafter', 'state': 'missing' if missing else 'ok',
            'detail': ', '.join(f'{f} {m}' for f, m in missing) or None, 'models': missing,
            'bytes': int(gb_ * 1e9), 'source': source, 'fix': 'python3 -I scripts/acquire.py fetch dflash2'}


def harness_item(div):
    pin = harnesses.load_pin(div)
    f = harnesses.find(div)
    it = {'item': f'harness:{div}', 'what': f'{div} {pin.get("version") or "(version not pinned yet)"}', 'state': 'ok' if f['ok'] else 'missing',
          'detail': f'{f.get("where")}: {f.get("bin")}' if f['ok'] else f['reason'],
          'bytes': int(pin['size_mb'] * 1e6) if pin.get('size_mb') else None,
          'source': harnesses.install_note(div) or pin.get('source')}
    if not f['ok']:
        it['fix'] = ('python3 -I scripts/acquire.py fetch ' + it['item'] if harnesses.install_note(div)
                     else f'install by hand: {pin.get("note") or pin.get("source")}')
    return it


def tool_items(div):
    out = []
    if envs.load_division(div).get('harness'):
        out.append({'item': 'system', 'what': 'bubblewrap (bwrap)', 'state': 'ok' if shutil.which('bwrap') else 'missing',
                    'fix': 'the system package bubblewrap (root: the user installs it)'})
        if harnesses.load_pin(div).get('how') == 'npm':
            out.append({'item': 'system', 'what': 'node and npm', 'state': 'ok' if shutil.which('npm') else 'missing',
                        'fix': 'Node.js 22 or newer on PATH'})
    return out


def check(env_id, div):
    models, dflash = needed(env_id, div)
    items = model_items(models)
    if dflash:
        items.append(dflash2_item(dflash))
    if envs.load_division(div).get('harness'):
        items.append(harness_item(div))
    items += tool_items(div)
    free = shutil.disk_usage(overnight.models_root()).free
    out = {'at': now(), 'env': env_id, 'division': div, 'ok': all(i['state'] == 'ok' for i in items),
           'free_bytes': free, 'items': items}
    (ROOT / 'run-status').mkdir(exist_ok=True)
    (ROOT / 'run-status/acquire.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
    return out


def show(out):
    print(f'division {out["division"]}, environment {out["env"]}: '
          + ('everything is here' if out['ok'] else 'something is missing'))
    for i in out['items']:
        size = f' ({gb(i["bytes"])})' if i.get('bytes') and i["state"] != "ok" else ''
        line = f'  [{"ok" if i["state"] == "ok" else "--"}] {i["what"]}: {i["state"]}{size}'
        if i['state'] != 'ok':
            line += f' — {i.get("detail") + "; " if i.get("detail") else ""}{i.get("fix", "")}'
        print(line)
    left = sum(i.get('bytes') or 0 for i in out['items'] if i['state'] == 'missing')
    if left:
        print(f'  to download: {gb(left)}; free on the models disk: {gb(out["free_bytes"])}'
              + (' (NOT ENOUGH)' if left + 10e9 > out['free_bytes'] else ''))


def ask(question, yes):
    if yes:
        return True
    if not sys.stdin.isatty():
        print(f'{question} [not asked: no terminal; run it again with --yes once agreed]')
        return False
    return input(f'{question} [y/N] ').strip().lower() in ('y', 'yes')


def fetch(out, wanted, yes, skip_models=False):
    busy = queue_running()
    if busy:
        raise SystemExit(f'a benchmark queue is running ({busy}): nothing is fetched during a measurement (AGENTS.md 1.8)')
    missing = [i for i in out['items'] if i['state'] == 'missing']
    todo = {i['item'] for i in missing} if 'all' in wanted else set(wanted)
    if skip_models:
        todo.discard('models')
    unknown = todo - {i['item'] for i in out['items']}
    if unknown:
        raise SystemExit(f'not an item of this run: {", ".join(sorted(unknown))} (python3 -I scripts/acquire.py check)')
    rc = 0
    if 'models' in todo and any(i['item'] == 'models' for i in missing):
        size = sum(i['bytes'] or 0 for i in missing if i['item'] == 'models')
        names = ', '.join(i['what'] for i in missing if i['item'] == 'models')
        if ask(f'download {names} ({gb(size)} from huggingface.co) with scripts/overnight.py?', yes):
            if overnight_running():
                print('scripts/overnight.py is already running (downloads/overnight.log)')
            else:
                (ROOT / 'downloads/READY').unlink(missing_ok=True)
                with (ROOT / 'downloads/overnight.out').open('a') as f:
                    subprocess.Popen([str(ROOT / '.venv-hf/bin/python'), '-u', 'scripts/overnight.py'], cwd=ROOT,
                                     env={**os.environ, 'BENCH_ENV': out['env']}, stdout=f, stderr=subprocess.STDOUT,
                                     stdin=subprocess.DEVNULL, start_new_session=True)
                print('started scripts/overnight.py (downloads/overnight.log); it runs for hours, so it is not waited for')
    if 'dflash2' in todo and any(i['item'] == 'dflash2' for i in missing):
        it = next(i for i in missing if i['item'] == 'dflash2')
        if ask(f'fetch the DFlash2 drafter ({gb(it["bytes"] or 0)} from {it["source"]}) with strata drafting fetch?', yes):
            for fam, model in it['models']:
                if dflash2_item([(fam, model)])['state'] == 'missing':   # one fetch may have brought another model's too
                    rc |= subprocess.run(['strata', 'drafting', 'fetch', *drafting_args(fam, model), '--mode', 'dflash2'],
                                         cwd='/tmp').returncode
    for it in missing:
        if not it['item'].startswith('harness:') or it['item'] not in todo:
            continue
        div = it['item'].split(':', 1)[1]
        if not harnesses.install_note(div):
            print(f'{it["what"]}: installed by hand ({it.get("fix")})')
            continue
        size = f', about {gb(it["bytes"])}' if it.get('bytes') else ''
        where = (harnesses.TOOLS / div / str(harnesses.load_pin(div).get('version'))).relative_to(ROOT)
        if ask(f'install {it["source"]} into {where}/{size}?', yes):
            rc |= harnesses.install(div)
    return rc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['check', 'fetch'], nargs='?', default='check')
    ap.add_argument('items', nargs='*', help='fetch: models, dflash2, harness:<division> (as check names them)')
    ap.add_argument('--all', action='store_true', help='fetch: every missing item')
    ap.add_argument('--yes', action='store_true', help='fetch: do not ask (agreed beforehand)')
    ap.add_argument('--skip-models', action='store_true',
                    help='fetch: leave the models out (the run\'s supervisor starts scripts/overnight.py itself)')
    ap.add_argument('--env', default='', help='the environment (default: the one this hardware matches)')
    a = ap.parse_args()
    env_id = envs.current(a.env)
    div = envs.division()
    out = check(env_id, div)
    show(out)
    if a.cmd == 'check':
        return 0 if out['ok'] else 1
    if not a.items and not a.all:
        raise SystemExit('fetch what? models, dflash2, harness:<division>, or --all')
    rc = fetch(out, ['all'] if a.all else a.items, a.yes, a.skip_models)
    after = check(env_id, div)
    show(after)
    # still missing after the fetch, other than the models (their unit runs for hours): the run cannot start
    left = [i['what'] for i in after['items'] if i['state'] != 'ok' and i['item'] != 'models']
    if left:
        print('still missing: ' + ', '.join(left))
    return rc or (1 if left else 0)


if __name__ == '__main__':
    sys.exit(main())
