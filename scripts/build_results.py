#!/usr/bin/env python3
"""The results as charts, per test environment and compared between them (and summary.csv, one row per measured case
and environment).

With --snapshot <env>/<run id> it is the page as of that published run: it reads only the published runs that finished
by then (every environment) and writes snapshots/<division>/<env>/<run id>/index.html and summary.csv, which GitHub
Pages serves; scripts/publish.py writes one per run, and they are never rewritten. Its links into the repository (the
case lists, models.json, the divisions) go to GitHub at the tag of that publish (envs.tag). Without, it also reads
results/ (runs still being measured, ignored by Git) and writes preview/RESULTS.html and preview/summary.csv
(another division than plain: preview/RESULTS-<division>.html and summary-<division>.csv).

For every environment (envs/<id>/env.json) it reads that environment's case plan (scripts/build_cases.py) and every
results/<division>/<env>/<run-id>/cases/<case id>/summary.json, with the same rule as the case pages: test- run ids are left out,
and for a case measured in several runs of the environment the run id that sorts last wins (--run-id keeps one run). Adds, per case, the engine's launch time (sessions/*/start-*/session.json) and
the machine's heat and power while it ran (stats/thermal.csv from scripts/stats_watch.py, matched by the runner.log
times), and per run the conditions (machine.json: GPU power limit, CPU, Strata).

    python3 -I scripts/build_results.py
    python3 -I scripts/build_results.py --snapshot rtx5090-128g/2026-11-04-long
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
from build_cases import display_model as dm  # noqa: E402
import envs  # noqa: E402
import i18n  # noqa: E402
import machine_info  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CASE_LINE = re.compile(r'^(\S+) {3}(\S+): \w+ prefill=')
SESSION_LINE = re.compile(r'^(\S+) session (\S+): ')
KEEP = ['status', 'n', 'planned', 'prefill_tps', 'decode_tps', 'ttft_ms', 'first_answer_ms', 'total_ms',
        'completion_tokens', 'reasoning_chars', 'accept_rate', 'capped', 'correct', 'gpu_mem_peak_mib', 'rss_peak_mib',
        'disk_read_mib', 'power_peak_w', 'flags', 'single_file', 'from_workspace', 'drawn', 'hung',
        # harness divisions (scripts/bench_runner.py run_harness_case)
        'harness', 'harness_version', 'requests', 'requests_without_tools', 'tool_calls_n', 'steps', 'preamble_tokens',
        'tools_offered', 'cached_share', 'engine_share', 'harness_start_ms']
CSV_COLS = ['division', 'env', 'id', 'run_id', 'step', 'family', 'model', 'context_label', 'fixture', 'input_tokens', 'temperature',
            'effort', 'config', 'concurrency', 'status', 'n', 'prefill_tps', 'decode_tps', 'ttft_ms', 'first_answer_ms',
            'total_ms', 'completion_tokens', 'accept_rate', 'capped', 'correct', 'launch_s', 'power_peak_w',
            'rss_peak_mib', 'gpu_mem_peak_mib', 'cpu_core_throttle_pct', 'cpu_pkg_c_max', 'gpu_power_w', 'single_file', 'drawn',
            'harness', 'harness_version', 'requests', 'tool_calls_n', 'preamble_tokens', 'cached_share', 'engine_share',
            'harness_start_ms']


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


# One case shown under each section of the page, so a reader sees what a Tier sends and gets back and where its record
# is: the first of these the environment has (the reference model, done), else the section's first done case.
SAMPLE = {
    'speed': ('1', ['T1-{ref}-decode-prose-ja-t0.7']),
    'long': ('1', ['T1-{ref}-prefill-32k']),
    'std': ('2', ['T2-{ref}-std-prompt-4k']),
    'think': ('3', ['T3-{ref}-math-1-high']),
    'ctx': ('4a', ['T4a-{ref}-ctxcost-1M']),
    'doc': ('4b', ['T4b-{ref}-long-32K-q-d10']),
    'yarn': ('4d', ['T4d-{ref}-yarn-300K-ctx384K-yarn1.5-q-d10']),
    'opts': ('5', ['T5-{ref}-kv-q4_0-decode-prose-ja']),
    # the coding results: the reference model's coding case in whatever Tier has one (plain 3, a harness division G)
    'games': (None, ['T3-{ref}-coding-harbor-high', 'TG-{ref}-game-minecraft-high'], ('coding-', 'game-')),
}
SAMPLE_CHARS = 700          # how much of a prompt or an answer the page shows (head and tail of a longer one)
REQUEST_KEYS = ['max_tokens', 'temperature', 'seed', 'top_p', 'top_k', 'min_p', 'presence_penalty', 'repetition_penalty',
                'reasoning_effort', 'chat_template_kwargs', 'reasoning_budget_tokens']


def clip(text):
    """A long text as its head and tail, with how much was left out between them."""
    if text is None or len(text) <= SAMPLE_CHARS:
        return text, 0
    head, tail = SAMPLE_CHARS * 2 // 3, SAMPLE_CHARS // 3
    return text[:head] + '\n…\n' + text[-tail:], len(text) - head - tail


def sample(row, run, path, base):
    """What the page shows of one case: its conditions, the first request (as sent, rebuilt from the fixture with the
    nonce recorded) and its answer, the measured numbers and links to its record. base: the way to the repository."""
    import bench_runner
    case = path.parent
    rel = str(case.relative_to(ROOT))
    reqs = [json.loads(x) for x in (case / 'requests.jsonl').read_text().splitlines() if x.strip()] \
        if (case / 'requests.jsonl').exists() else []
    first = reqs[0] if reqs else {}
    out = {'id': row['id'], 'step': row['step'], 'model': f'{row["family"]} {dm(row["family"], row["model"])}', 'run_id': run.name,
           'context': row['context_label'], 'launch_opts': row['launch_opts'], 'config': row['config'],
           'fixture': row['fixture'], 'effort': row['effort'], 'temperature': row['temperature'],
           'output_cap': row['output_cap'], 'reps': row['reps'],
           'folder': (base + rel + '/').replace('/blob/', '/tree/', 1), 'requests': base + rel + '/requests.jsonl'}
    if row['step'] == '2':     # strata bench run: Strata's own frozen prompts, recorded as its results
        out['bench'] = {k: first.get(k) for k in ('case_id', 'phase', 'max_output_tokens', 'status', 'finish_reason', 'tokens', 'timings', 'metrics')}
        return out
    if first.get('nonce'):
        body = bench_runner.request_body(row, first.get('seed', 1), first['nonce'])
        out['input'], out['input_left_out'] = clip(body['messages'][0]['content'])
        out['request'] = {k: body[k] for k in REQUEST_KEYS if k in body}
    resp = case / 'responses' / 'r1-s1.md'
    if resp.exists():
        out['output'], out['output_left_out'] = clip(resp.read_text(errors='replace'))
        out['response'] = base + str(resp.relative_to(ROOT))
    shot = next(iter(sorted(case.glob('artifact/seed-1/screenshot.png'))), None)
    if shot:
        out['screenshot'] = base + str(shot.relative_to(ROOT))
    out['measured'] = {k: first.get(k) for k in ('ttft_ms', 'first_answer_ms', 'total_ms', 'finish_reason', 'reasoning_chars', 'content_chars')}
    out['measured'].update({'prompt_tokens': (first.get('usage') or {}).get('prompt_tokens'),
                            'completion_tokens': (first.get('usage') or {}).get('completion_tokens'),
                            'decode_tps': (first.get('timings') or {}).get('predicted_per_second'),
                            'prefill_tps': (first.get('timings') or {}).get('prompt_per_second'),
                            'check': first.get('check')})
    return out


def samples(rows, found, base, ref_model):
    ref = '-'.join(ref_model or ('', ''))
    by_id = {r['id']: r for r in rows}
    out = {}
    for sec, (step, want, *fixtures) in SAMPLE.items():
        ids = [w.format(ref=ref) for w in want] + [r['id'] for r in rows if step in (None, r['step'])
                                                    and (not fixtures or r['fixture'].startswith(fixtures[0]))]
        cid = next((i for i in ids if i in found and i in by_id and load(found[i][1]).get('status') == 'done'), None)
        if cid:
            out[sec] = sample(by_id[cid], *found[cid], base)
    return out


def artifacts(case, rel, per_request=None):
    """A game case's results per seed, for the gallery: the screenshot and the page itself (opened in a sandboxed frame),
    as paths relative to the page (GitHub Pages serves them; a blob link would not run them), and the manifest's form."""
    out = []
    for d in sorted(case.glob('artifact/seed-*')):
        m = load(d / 'manifest.json')
        entry = m.get('entry')
        page = d / 'files' / entry if entry else None
        shot = d / 'screenshot.png'
        look = m.get('screenshot') or {}
        seed = d.name.split('-', 1)[1]
        run = next((x for x in per_request or [] if str(x.get('seed')) == seed), {})
        out.append({'seed': seed, 'source': m.get('source', 'answer'), 'kind': m.get('kind'),
                    'total_ms': run.get('total_ms'), 'error': run.get('error'), 'requests': run.get('requests'),
                    'tool_calls_n': run.get('tool_calls_n'),
                    'single_file': m.get('single_file'), 'truncated': m.get('truncated'),
                    'console_errors': len(look.get('console_errors') or []),
                    # what the capture shows (bench_runner.screenshot): drawn / empty / hung; None where it was not judged
                    'look': 'hung' if look.get('hung') else None if 'drawn' not in look else 'drawn' if look['drawn'] else 'empty',
                    'files': len(m.get('files') or []),
                    'screenshot': rel + str(shot.relative_to(ROOT)) if shot.exists() else None,
                    'page': rel + str(page.relative_to(ROOT)) if page and page.exists() else None,
                    'folder': rel + str(d.relative_to(ROOT)) + '/'})
    return out


def collect_env(cfg, run_id, published_only, rel=''):
    env_id = cfg['id']
    plan = build_cases.build(cfg)
    found = summaries(env_id, run_id, published_only)
    rows = plan + build_cases.measured_rows(cfg, plan, set(found))   # models no longer measured keep their results
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
        c['model_id'], c['model'] = r['model'], dm(r['family'], r['model'])   # the page shows the set's version
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
        if r['fixture'].startswith(('coding-', 'game-')):
            c['artifacts'] = artifacts(path.parent, rel, s.get('per_request'))
        cases.append(c)
    # Every model in every environment and chart: which ones an environment measures is the measurer's choice (a disk
    # too small for some), not a property of the environment, so a model it has no value for reads "not measured".
    models = [{'key': f'{f} {dm(f, m)}', 'family': f, 'model': dm(f, m), 'gb': gb, 'role': role,
               'derivative': (f, m) in build_cases.DERIVATIVE, 'ref': (f, m) == build_cases.REF}
              for f, m, gb, role in build_cases.MODELS]
    planned = {}
    for r in plan:
        planned.setdefault(r['step'], set()).add(f'{r["family"]} {dm(r["family"], r["model"])}')
    env = {'id': env_id, 'label': envs.label(cfg), 'runs': [machine(d) for d in runs], 'models': models,
           'planned_cases': {k: sum(1 for r in plan if r['step'] == k) for k in planned},
           'planned_per_model': {k: {m: sum(1 for r in plan if r['step'] == k and f'{r["family"]} {dm(r["family"], r["model"])}' == m) for m in v}
                                 for k, v in planned.items()},
           'dflash2_models': sorted({f'{r["family"]} {dm(r["family"], r["model"])}' for r in rows if r['config'] == 'drafter=DFlash2'}),
           'noise_pct': {k: restart_noise(found, k) for k in ('decode', 'prefill')}}
    env['ref'] = ' '.join(build_cases.REF) if build_cases.REF else None   # this environment's (build_cases.use_env)
    env['_rows'], env['_found'] = rows, found
    return env, cases


def collect(run_id, published_only=False, rel=''):
    here = envs.detect()[0]
    out = {'generated': datetime.now().astimezone().strftime('%Y-%m-%d %H:%M %Z'), 'envs': [], 'cases': [], 'here': here,
           'tr': i18n.TR}
    out['division'] = envs.division()
    out['harness'] = envs.load_division(out['division']).get('harness')
    for env_id in envs.page_ids(published_only):
        env, cases = collect_env(envs.load(env_id, published_only), run_id, published_only, rel)
        out['envs'].append(env)
        out['cases'] += [{'division': out['division'], **c} for c in cases]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run-id', default='', help='only this run (default: the newest result of every case)')
    ap.add_argument('--snapshot', metavar='ENV/RUN_ID',
                    help='the charts as of a published run: the published runs that finished by then, written to '
                         'snapshots/<division>/<env>/<run id>/ (default: results/ and published/, to preview/)')
    a = ap.parse_args()
    snap = None
    if a.snapshot:
        env_id, run = a.snapshot.split('/', 1)
        pub = envs.published_dir(env_id, run)
        if not envs.finished(pub):
            raise SystemExit(f'{pub.relative_to(ROOT)}: not published, or its queue never finished')
        envs.UNTIL = envs.finished_ts(pub)
        snap = {'env': env_id, 'run_id': run, 'division': envs.division(),
                'finished': envs.finished(pub)[:16].replace('T', ' ')}
    if snap:
        out = envs.snapshot_dir(snap['env'], snap['run_id'])
        page_path, csv_path = out / 'index.html', out / 'summary.csv'
    else:
        # one preview per division: plain's is RESULTS.html, another's RESULTS-<division>.html
        tail = '' if envs.division() == 'plain' else '-' + envs.division()
        page_path, csv_path = envs.PREVIEW / f'RESULTS{tail}.html', envs.PREVIEW / f'summary{tail}.csv'
    data = collect(a.run_id, bool(snap), os.path.relpath(ROOT, page_path.parent) + '/')
    if snap:
        # Links into the repository go to GitHub at the tag the publish leaves, so they show the files as they were then
        repo = envs.github()[0]
        if not repo:
            raise SystemExit('the origin remote is not a GitHub repository: the snapshot cannot link to its files')
        base = f'{repo}/blob/{envs.tag(snap["env"], snap["run_id"])}/'
        data['here'] = None
    else:
        base = os.path.relpath(ROOT, page_path.parent) + '/'
    data['snapshot'] = snap
    for e in data['envs']:
        e['samples'] = samples(e.pop('_rows'), e.pop('_found'), base, tuple(e['ref'].split()) if e.get('ref') else None)
    data['csv'] = os.path.relpath(csv_path, page_path.parent)
    for e in data['envs']:   # each run's models.json (which version of each model), linked from the page
        for r in e['runs']:
            if r.get('models_json'):
                r['models_json'] = base + r['models_json']
    cases_link = base + 'cases/README.md' if snap else os.path.relpath(envs.PREVIEW / 'cases/README.md', page_path.parent)
    data['published'] = bool(snap)
    page = Path(__file__).with_name('results_template.html').read_text()
    blob = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
    page = page.replace('{{data}}', blob).replace('{{generated}}', html.escape(data['generated']))
    boxes = ''.join(f'<div class="envwrap" data-env="{html.escape(e["id"])}">'
                    f'{machine_info.env_box(ROOT, envs.load(e["id"], bool(snap)), bool(snap), how=False)}</div>' for e in data['envs'])
    page = page.replace('{{env}}', boxes).replace('{{how}}', machine_info.how_html()).replace('{{csv}}', html.escape(data['csv']))
    page = page.replace('{{cases}}', html.escape(cases_link))
    page = page.replace('{{division}}', i18n.division_html(envs.load_division(data['division']), base))
    page = page.replace('{{i18n_head}}', i18n.HEAD).replace('{{i18n_script}}', i18n.SCRIPT).replace('{{lang_switch}}', i18n.SWITCH)
    page_path.parent.mkdir(parents=True, exist_ok=True)
    page_path.write_text(page)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open('w', newline='') as f:
        w = csv.writer(f)
        w.writerow(CSV_COLS)
        for c in data['cases']:
            w.writerow(['' if c.get(k) is None else c.get('model_id', c[k]) if k == 'model' else c.get(k) for k in CSV_COLS])
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
