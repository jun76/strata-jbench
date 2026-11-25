"""Build the configurator: one HTML page to choose what a run measures and get its recipe.

    python3 -I scripts/build_configurator.py              # preview/configurator.html (this PC's environments too)
    python3 -I scripts/build_configurator.py --published  # configurator/index.html (the committed page, GitHub Pages)

The page is the skill's template (.claude/skills/strata-jbench/assets/configurator.template.html) with the catalog
and, per environment, the plan's cases with their estimates written into it; nothing in the template names a model, an
engine or a task. In the browser the reader picks an environment, an engine, models and tasks, sees which metrics
that covers and how long it takes, and copies the recipe (scripts/recipe.py) to hand to the agent.
"""
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import case_plan  # noqa: E402
import catalog  # noqa: E402
import engines  # noqa: E402
import envs  # noqa: E402
from i18n import tr  # noqa: E402

TEMPLATE = ROOT / '.claude/skills/strata-jbench/assets/configurator.template.html'
PROMPT_CHARS = 1500


def prompt_of(fixture):
    """What a fixture sends, for the reader: the prompt's text (the start of it when it is long)."""
    try:
        f = json.loads((ROOT / 'prompts' / f'{fixture}.json').read_text())
    except (OSError, ValueError):
        return None
    if f.get('kind') == 'records':
        fmt = f.get('record_format', 'record{:06d}: ...')
        text = (f'{fmt.format(1)}\n{fmt.format(2)}\n…  ({f.get("records")} records)\n\n{f.get("question", "")}')
    elif f.get('kind') == 'long':
        qs = f.get('questions') or {}
        text = (f'[{f.get("lines")} lines of {f.get("corpus")}: ten works of Aozora Bunko and Project Gutenberg, Japanese and '
                f'English in turns, with three made-up facts placed at 10% / 50% / 90%]\n\n'
                + '\n\n'.join(f'{k}: {v.get("question", v) if isinstance(v, dict) else v}' for k, v in qs.items()))
    else:
        text = f.get('prompt') or f.get('question') or ''
        if not text and isinstance(f.get('messages'), list):
            text = '\n\n'.join(str(m.get('content', '')) for m in f['messages'])
    text = str(text)
    return {'text': text[:PROMPT_CHARS], 'cut': len(text) > PROMPT_CHARS, 'tokens': f.get('input_tokens')}


def rows_of(cfg, division, published_only):
    """Every case of an environment in one division, every model of the catalog (the reader chooses), compact."""
    os.environ['BENCH_DIVISION'] = division
    plan = case_plan.build({**cfg, 'models': None})
    case_plan.attach_results(plan, cfg['id'], published_only)
    hs = catalog.headlines()
    serves = {}
    for h in hs:
        for group in catalog.headline_rows(h, plan).values():
            for r in group:
                serves.setdefault(r['id'], []).append(h['id'])
    endpoint = engines.entry('endpoint')
    out = []
    for r in plan:
        if r['step'] == '2':
            a = case_plan.ASSUME_ENV
            launch = a['standard_runs'] * (case_plan.launch_seconds(r) + a['standard_run_overhead_s'])
            key = f'2/{r["family"]}/{r["model"]}'
        else:
            launch = r['restarts'] * case_plan.launch_seconds(r)
            key = f'{r["step"]}/{r["session"]}'
        out.append({'d': division, 'e': r['engine'], 'f': r['family'], 'm': r['model'], 't': r['task'], 's': r['step'],
                    'k': key, 'est': r['est_s'], 'l': round(launch), 'rq': r['requests'], 'fx': r['fixture'],
                    'h': serves.get(r['id'], []), 'sc': r['size_class'], 'done': r['status'] == 'done',
                    'a': int(r['step'] in endpoint['steps'] and not r['launch_opts'] and r['context'] == 131072
                             and r['restarts'] == 1 and r['engine'] == engines.DEFAULT)})
    return out


def collect(published_only):
    was = os.environ.get('BENCH_DIVISION')
    divisions = []
    for d in envs.division_ids():
        cfg = envs.load_division(d)
        divisions.append({'id': d, 'status': cfg.get('status'), 'harness': cfg.get('harness'), 'label': cfg['label'],
                          'summary': cfg['summary'], 'pin': {k: (cfg.get('pin') or {}).get(k) for k in ('name', 'version')}})
    local = None
    if not published_only:
        try:
            local = envs.detect()[0]
        except (SystemExit, Exception):   # noqa: BLE001  (no nvidia-smi, say: the page still builds)
            local = None
    found = []
    for env_id in envs.page_ids(published_only, 'plain'):
        os.environ['BENCH_DIVISION'] = 'plain'      # the environment's own record is its plain runs' (rows_of sets others)
        cfg = envs.load(env_id, published_only)
        rows = []
        for d in divisions:
            if d['status'] == 'active':
                rows += rows_of(cfg, d['id'], published_only)
        found.append({'id': env_id, 'label': envs.label(cfg), 'hardware': cfg.get('hardware') or {},
                      'drafters': cfg.get('drafters'), 'local': env_id == local, 'ref': envs.ref(cfg), 'rows': rows})
    if was is None:
        os.environ.pop('BENCH_DIVISION', None)
    else:
        os.environ['BENCH_DIVISION'] = was
    fixtures = sorted({r['fx'] for e in found for r in e['rows']})
    repo, pages = envs.github()
    return {'generated': datetime.now().astimezone().strftime('%Y-%m-%d %H:%M %Z'), 'preview': not published_only,
            'repo': repo, 'pages': pages,
            'engines': engines.entries(), 'bases': catalog.load(), 'tasks': catalog.tasks(), 'presets': catalog.presets(),
            'metrics': catalog.metrics(), 'headlines': catalog.headlines(), 'divisions': divisions, 'envs': found,
            'prompts': {fx: p for fx in fixtures if (p := prompt_of(fx))},
            'i18n_roles': {role: {lang: tr(role, lang) for lang in ('ja', 'en', 'zh')} for _, _, _, role in catalog.builds()}}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--published', action='store_true', help='published/ only, written to configurator/index.html')
    a = ap.parse_args()
    data = collect(a.published)
    html = TEMPLATE.read_text()
    mark = '/*JBENCH_DATA*/null'
    if mark not in html:
        raise SystemExit(f'{TEMPLATE.relative_to(ROOT)} has no {mark} to fill in')
    blob = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    out = ROOT / 'configurator/index.html' if a.published else envs.PREVIEW / 'configurator.html'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html.replace(mark, blob))
    print(f'{out.relative_to(ROOT)}: {len(data["envs"])} environment(s), {sum(len(e["rows"]) for e in data["envs"])} cases, '
          f'{len(data["tasks"])} tasks, {len(data["engines"])} engines, {out.stat().st_size / 1e6:.1f} MB')


if __name__ == '__main__':
    main()
