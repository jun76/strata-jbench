#!/usr/bin/env python3
"""RESULTS.html: the results as charts, per test environment and compared between them (and summary.csv, one row per
measured case and environment).

With --published it reads published/ only and writes RESULTS.html and published/summary.csv (the committed pages);
without, it also reads results/ (runs still being measured, ignored by Git) and writes preview/RESULTS.html and
preview/summary.csv.

For every environment (envs/<id>/env.json) it reads that environment's case plan (scripts/build_cases.py) and every
results/<division>/<env>/<run-id>/cases/<case id>/summary.json, with the same rule as the case pages: test- run ids are left out,
and for a case measured in several runs of the environment the run id that sorts last wins (--run-id keeps one run). Adds, per case, the engine's launch time (sessions/*/start-*/session.json) and
the machine's heat and power while it ran (stats/thermal.csv from scripts/stats_watch.py, matched by the runner.log
times), and per run the conditions (machine.json: GPU power limit, CPU, Strata).

    python3 -I scripts/build_results.py
    python3 -I scripts/build_results.py --published
    python3 -I scripts/build_results.py --run-id 2026-11-03-main
"""
import os
import argparse
import csv
import html
import json
import re
import statistics
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_cases  # noqa: E402
import envs  # noqa: E402
import i18n  # noqa: E402
import machine_info  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CASE_LINE = re.compile(r'^(\S+) {3}(\S+): \w+ prefill=')
SESSION_LINE = re.compile(r'^(\S+) session (\S+): ')
KEEP = ['status', 'n', 'planned', 'prefill_tps', 'decode_tps', 'ttft_ms', 'first_answer_ms', 'total_ms',
        'completion_tokens', 'reasoning_chars', 'accept_rate', 'capped', 'correct', 'gpu_mem_peak_mib', 'rss_peak_mib',
        'disk_read_mib', 'power_peak_w', 'flags']
CSV_COLS = ['division', 'env', 'id', 'run_id', 'step', 'family', 'model', 'context_label', 'fixture', 'input_tokens', 'temperature',
            'effort', 'config', 'concurrency', 'status', 'n', 'prefill_tps', 'decode_tps', 'ttft_ms', 'first_answer_ms',
            'total_ms', 'completion_tokens', 'accept_rate', 'capped', 'correct', 'launch_s', 'power_peak_w',
            'rss_peak_mib', 'gpu_mem_peak_mib', 'cpu_core_throttle_pct', 'cpu_pkg_c_max', 'gpu_power_w']


def load(path):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return {}


def ts(text):
    try:
        return datetime.fromisoformat(text).timestamp()
    except ValueError:
        return None


def summaries(env_id, run_id, published_only):
    """case id -> (run folder, summary.json) of the newest run that has it."""
    by_id = {}
    for d in envs.run_dirs(env_id, published_only):
        if run_id and d.name != run_id:
            continue
        for p in sorted(d.glob('cases/*/summary.json')):
            by_id[p.parent.name] = (d, p)
    return by_id


def launches(run):
    """(session dir name) -> the launches of that session: launch_s, ok, error. run: the run's folder."""
    out = {}
    for p in sorted((run / 'sessions').glob('*/start-*/session.json')):
        s = load(p)
        out.setdefault(p.parents[1].name, []).append(
            {'launch_s': s.get('launch_s'), 'ok': s.get('rc') == 0 and not s.get('error'), 'error': (s.get('error') or '')[-200:]})
    return out


def case_windows(run):
    """case id -> (start, end) epoch seconds: from the runner line before it to its own line (the last time it ran)."""
    out, prev = {}, None
    for line in (run / 'runner.log').read_text(errors='replace').splitlines() if (run / 'runner.log').exists() else []:
        t = ts(line.split(' ', 1)[0])
        m = CASE_LINE.match(line)
        if m and prev and t:
            out[m.group(2)] = (prev, t)
        if t:
            prev = t
    return out


def thermal_rows(run):
    path = run / 'stats' / 'thermal.csv'
    if not path.exists():
        return []
    rows = []
    with path.open() as f:
        for r in csv.DictReader(f):
            try:
                r['t'] = float(r['t'])
            except (TypeError, ValueError):
                continue
            rows.append(r)
    return rows


def num(rows, key, how):
    vals = []
    for r in rows:
        try:
            vals.append(float(r[key]))
        except (KeyError, TypeError, ValueError):
            pass
    if not vals:
        return None
    return round(statistics.median(vals) if how == 'median' else max(vals), 1)


def machine(run):
    m = load(run / 'machine.json')
    smi = m.get('nvidia_smi', '')
    limit = re.search(r'Current Power Limit\s+:\s+([\d.]+) W', smi)
    gpu = re.search(r'Product Name\s+:\s+(.+)', smi)
    cpu = re.search(r'^(?:Model name|モデル名):\s+(.+)$', m.get('lscpu', ''), re.M)   # lscpu follows the locale
    strata = re.sub(r';\s*python .*\)', ')', m.get('strata') or '')                 # without the install path
    return {'run_id': run.name, 'power_limit_w': float(limit.group(1)) if limit else None,
            'gpu': gpu.group(1).strip() if gpu else None, 'cpu': cpu.group(1).strip() if cpu else None,
            'strata': strata, 'created_at': m.get('created_at'),
            'models_json': str((run / 'models.json').relative_to(ROOT)) if (run / 'models.json').exists() else None}


def spread(per_request, key):
    vals = [r.get(key) for r in per_request or [] if r.get(key) is not None and not r.get('error')]
    return [round(min(vals), 2), round(max(vals), 2)] if vals else None


def restart_noise(found, kind):
    """How much a Tier 0 case moves between engine starts (the same launch, 3 starts): the range of the per-start medians
    over their median, the median of that over the Tier 0 cases of one kind ('decode' or 'prefill'). Tier 5 calls a change
    smaller than twice this no effect (docs: the plan's Tier 5)."""
    key = 'decode_tps' if kind == 'decode' else 'prefill_tps'
    out = []
    for cid, (_, path) in found.items():
        if not cid.startswith('T0-') or '-author-' in cid or f'-{kind}-' not in cid:
            continue
        by = {}
        for r in load(path).get('per_request') or []:
            if r.get(key) is not None and not r.get('error'):
                by.setdefault(r.get('restart'), []).append(r[key])
        meds = [statistics.median(v) for v in by.values()]
        if len(meds) >= 2 and statistics.median(meds) > 0:
            out.append((max(meds) - min(meds)) / statistics.median(meds))
    return round(100 * statistics.median(out), 2) if out else None


def collect_env(cfg, run_id, published_only):
    env_id = cfg['id']
    rows = build_cases.build(cfg)
    found = summaries(env_id, run_id, published_only)
    runs = sorted({run for run, _ in found.values()}, key=lambda d: d.name)
    per_run = {}
    for d in runs:
        per_run[d] = {'launches': launches(d), 'windows': case_windows(d), 'thermal': thermal_rows(d)}
    cases = []
    for r in rows:
        if r['id'] not in found:
            continue
        run, path = found[r['id']]
        s = load(path)
        info = per_run[run]
        c = {k: r[k] for k in ('id', 'step', 'family', 'model', 'context', 'context_label', 'fixture', 'content',
                               'input_tokens', 'output_cap', 'effort', 'temperature', 'config', 'launch_opts',
                               'concurrency', 'session')}
        c.update({k: s.get(k) for k in KEEP})
        c['env'] = env_id
        c['run_id'] = run.name
        c['decode_range'] = spread(s.get('per_request'), 'decode_tps')
        c['prefill_range'] = spread(s.get('per_request'), 'prefill_tps')
        c['ttft_range'] = spread(s.get('per_request'), 'ttft_ms')
        starts = info['launches'].get(f'{r["session"]}-T{r["step"]}', [])
        ok = [x['launch_s'] for x in starts if x['ok'] and x['launch_s'] is not None]
        c['launch_s'] = round(statistics.median(ok), 1) if ok else None
        c['launch_failed'] = bool(starts) and not ok
        w = info['windows'].get(r['id'])
        th = [x for x in info['thermal'] if w and w[0] < x['t'] <= w[1]]
        c['cpu_core_throttle_pct'] = num(th, 'cpu_core_throttle_pct', 'median')
        c['cpu_pkg_throttle_pct'] = num(th, 'cpu_pkg_throttle_pct', 'median')
        c['cpu_pkg_c_max'] = num(th, 'cpu_pkg_c', 'max')
        c['gpu_c_max'] = num(th, 'gpu_c', 'max')
        c['gpu_power_w'] = num(th, 'gpu_power_avg_w', 'median')
        cases.append(c)
    models = [{'key': f'{f} {m}', 'family': f, 'model': m, 'gb': gb, 'role': role,
               'derivative': (f, m) in build_cases.DERIVATIVE, 'ref': (f, m) == build_cases.REF}
              for f, m, gb, role in build_cases.env_models()]
    planned = {}
    for r in rows:
        planned.setdefault(r['step'], set()).add(f'{r["family"]} {r["model"]}')
    env = {'id': env_id, 'label': envs.label(cfg), 'runs': [machine(d) for d in runs], 'models': models,
           'planned_models': {k: sorted(v) for k, v in planned.items()},
           'planned_cases': {k: sum(1 for r in rows if r['step'] == k) for k in planned},
           'planned_per_model': {k: {m: sum(1 for r in rows if r['step'] == k and f'{r["family"]} {r["model"]}' == m) for m in v}
                                 for k, v in planned.items()},
           'dflash2_models': sorted({f'{r["family"]} {r["model"]}' for r in rows if r['config'] == 'drafter=DFlash2'}),
           'noise_pct': {k: restart_noise(found, k) for k in ('decode', 'prefill')}}
    return env, cases


def collect(run_id, published_only=False):
    here = envs.detect()[0]
    out = {'generated': datetime.now().astimezone().strftime('%Y-%m-%d %H:%M %Z'), 'envs': [], 'cases': [], 'here': here,
           'tr': i18n.TR}
    out['division'] = envs.division()
    for env_id in envs.ids():
        env, cases = collect_env(envs.load(env_id), run_id, published_only)
        out['envs'].append(env)
        out['cases'] += [{'division': out['division'], **c} for c in cases]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run-id', default='', help='only this run (default: the newest result of every case)')
    ap.add_argument('--published', action='store_true',
                    help='only the runs in published/, written to RESULTS.html (default: also results/, to preview/)')
    a = ap.parse_args()
    data = collect(a.run_id, a.published)
    page_path = ROOT / 'RESULTS.html' if a.published else envs.PREVIEW / 'RESULTS.html'
    csv_path = envs.PUBLISHED / 'summary.csv' if a.published else envs.PREVIEW / 'summary.csv'
    data['csv'] = os.path.relpath(csv_path, page_path.parent)
    for e in data['envs']:   # each run's models.json (which version of each model), linked from the page
        for r in e['runs']:
            if r.get('models_json'):
                r['models_json'] = os.path.relpath(ROOT / r['models_json'], page_path.parent)
    data['published'] = a.published
    page = Path(__file__).with_name('results_template.html').read_text()
    blob = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
    page = page.replace('{{data}}', blob).replace('{{generated}}', html.escape(data['generated']))
    boxes = ''.join(f'<div class="envwrap" data-env="{html.escape(e["id"])}">'
                    f'{machine_info.env_box(ROOT, envs.load(e["id"]), a.published, how=False)}</div>' for e in data['envs'])
    page = page.replace('{{env}}', boxes).replace('{{how}}', machine_info.how_html()).replace('{{csv}}', html.escape(data['csv']))
    up = os.path.relpath(ROOT, page_path.parent) + '/' if page_path.parent != ROOT else ''
    page = page.replace('{{division}}', i18n.division_html(envs.load_division(data['division']), up))
    page = page.replace('{{i18n_head}}', i18n.HEAD).replace('{{i18n_script}}', i18n.SCRIPT).replace('{{lang_switch}}', i18n.SWITCH)
    page_path.parent.mkdir(parents=True, exist_ok=True)
    page_path.write_text(page)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open('w', newline='') as f:
        w = csv.writer(f)
        w.writerow(CSV_COLS)
        for c in data['cases']:
            w.writerow(['' if c.get(k) is None else c.get(k) for k in CSV_COLS])
    missing = i18n.untranslated([x for e in data['envs'] for m in e['models'] for x in (m['role'],)]
                                + [c['config'] for c in data['cases']])
    if missing:
        print(f'RESULTS.html: {len(missing)} string(s) without a translation in scripts/i18n.py TR (shown in Japanese):')
        for x in missing:
            print('  ' + x)
    for e in data['envs']:
        n = sum(c['env'] == e['id'] for c in data['cases'])
        print(f'{page_path.relative_to(ROOT)}: {e["id"]}: {n} cases from {", ".join(r["run_id"] for r in e["runs"]) or "no run"}')


if __name__ == '__main__':
    main()
