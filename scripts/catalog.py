"""The catalog: what jbench can measure, as data (catalog/README.md).

catalog/models/<base>.json is one base model (Qwen3.8-Flash-Next, Hy4-Flash, ...) with what holds for every build of
it (tokenizer, trained length, whether it thinks, its drafter) and its builds (family, model, size, role). The plan
builder and the runner read these properties instead of naming families: a new base model or build is a JSON edit.

catalog/tasks.json names what a run can do (the tasks: what each asks, what it sends, which metrics it gives) and
the presets that bundle them; catalog/metrics.json defines every metric in one line and the headline numbers (one
fixed condition each). A task is tied to the plan's cases by "match" (the step and the fixture's prefix).

`python3 -I scripts/catalog.py` lists the catalog and reports what is wrong in it, the plans on this PC included
(every case belongs to exactly one task).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = ROOT / 'catalog' / 'models'
TASKS = ROOT / 'catalog' / 'tasks.json'
METRICS = ROOT / 'catalog' / 'metrics.json'
LANGS = ('ja', 'en', 'zh')

BASE_KEYS = {'base', 'order', 'label', 'tokenizer', 'trained_context', 'max_context', 'thinking', 'lineup', 'drafter',
             'builds'}
BUILD_KEYS = {'family', 'model', 'size_gb', 'role', 'derivative', 'display', 'engines', 'own'}


def bases():
    """Every base model, in the order of "order" (the order of the pages and the lists)."""
    out = []
    for path in sorted(MODELS_DIR.glob('*.json')):
        try:
            out.append(json.loads(path.read_text()))
        except ValueError as e:
            raise SystemExit(f'catalog/models/{path.name} is not valid JSON: {e}')
    return sorted(out, key=lambda b: (b.get('order', 0), b.get('base', '')))


def problems(found=None):
    out, seen, fams = [], set(), {}
    for b in found if found is not None else bases():
        name = b.get('base', '?')
        for k in sorted(BASE_KEYS - set(b)):
            out.append(f'{name}: no "{k}"')
        for k in sorted(set(b) - BASE_KEYS):
            out.append(f'{name}: unknown key "{k}"')
        if b.get('lineup') not in ('main', 'other'):
            out.append(f'{name}: "lineup" is "main" or "other"')
        d = b.get('drafter') or {}
        if not ('pin' in d) ^ ('builtin' in d):
            out.append(f'{name}: "drafter" has either "pin" (the runner pins it at launch) or "builtin" (the build\'s own)')
        for e in b.get('builds', []):
            key = (e.get('family'), e.get('model'))
            for k in ('family', 'model', 'size_gb', 'role'):
                if k not in e:
                    out.append(f'{name}: a build without "{k}": {e}')
            for k in sorted(set(e) - BUILD_KEYS):
                out.append(f'{name} {key}: unknown key "{k}"')
            if key in seen:
                out.append(f'{name}: {key[0]} {key[1]} is listed twice')
            seen.add(key)
            if fams.setdefault(key[0], name) != name:   # a family's properties are its base model's
                out.append(f'family {key[0]} is in two base models: {fams[key[0]]} and {name}')
    return out


def load():
    found = bases()
    bad = problems(found)
    if bad:
        raise SystemExit('catalog/models: ' + '; '.join(bad))
    return found


def builds(found=None):
    """(family, model, size GB, role) of every build, in catalog order."""
    return [(e['family'], e['model'], e['size_gb'], e['role']) for b in found or load() for e in b['builds']]


def by_family(found=None):
    """family -> its base model's entry."""
    return {e['family']: b for b in found or load() for e in b['builds']}


def tasks():
    return json.loads(TASKS.read_text())['tasks']


def presets():
    return json.loads(TASKS.read_text())['presets']


def metrics():
    return json.loads(METRICS.read_text())['metrics']


def headlines():
    return json.loads(METRICS.read_text())['headlines']


def matches(task, row):
    m = task['match']
    return row['step'] in m['step'] and ('fixture_prefix' not in m or row['fixture'].startswith(tuple(m['fixture_prefix'])))


def task_of(row, found=None):
    """The task a plan row (a case) belongs to: its id, or None."""
    hit = [t['id'] for t in found or tasks() if matches(t, row)]
    return hit[0] if len(hit) == 1 else None


def selects(only, row):
    """A preset's "only" (key -> allowed values) against a row."""
    return all(row.get(k) in v for k, v in (only or {}).items())


def headline_rows(headline, rows, found=None):
    """The cases a headline number is read from, per model: {(family, model): [rows]}. "where" fixes the condition;
    "prefer" lists alternatives in order where models differ in what they have (the drafter the engine picks by
    itself, thinking on where the model thinks): per model, the first alternative that has a case wins."""
    ts = found or tasks()
    per = {}
    for r in rows:
        if task_of(r, ts) == headline['task'] and all(r.get(k) == v for k, v in headline['where'].items()):
            per.setdefault((r['family'], r['model']), []).append(r)
    out = {}
    for key, mine in per.items():
        for alt in headline.get('prefer') or [{}]:
            hit = [r for r in mine if all(r.get(k) == v for k, v in alt.items())]
            if hit:
                out[key] = hit
                break
    return out


def chosen_ids(rows, task_ids=None, preset_id=None):
    """The case ids the tasks or the preset pick out of rows (bench.json "tasks" / "preset"). None when neither is
    given (no narrowing)."""
    if not task_ids and not preset_id:
        return None
    ts = tasks()
    hs = {h['id']: h for h in headlines()}
    by_task = {t['id']: t for t in ts}
    wanted = [{'task': t} for t in task_ids or []]
    if preset_id:
        found = [p for p in presets() if p['id'] == preset_id]
        if not found:
            raise SystemExit(f'no preset {preset_id!r} in catalog/tasks.json (there: {", ".join(p["id"] for p in presets())})')
        wanted += found[0]['tasks']
    ids = set()
    for w in wanted:
        if w['task'] not in by_task:
            raise SystemExit(f'no task {w["task"]!r} in catalog/tasks.json (there: {", ".join(by_task)})')
        mine = [r for r in rows if task_of(r, ts) == w['task']]
        if w.get('headline_only'):
            h = hs[by_task[w['task']]['headline']]
            mine = [r for group in headline_rows(h, mine, ts).values() for r in group]
        ids |= {r['id'] for r in mine if selects(w.get('only'), r)}
    return ids


def task_problems():
    out = []
    ts, ms, hs = tasks(), {m['id'] for m in metrics()}, {h['id']: h for h in headlines()}
    ids = [t['id'] for t in ts]
    for t in ts:
        for k in ('label', 'question', 'sends'):
            if set(t.get(k, {})) != set(LANGS):
                out.append(f'task {t["id"]}: "{k}" needs {", ".join(LANGS)}')
        for m in t.get('metrics', []):
            if m not in ms:
                out.append(f'task {t["id"]}: metric {m!r} is not in metrics.json')
        if t.get('headline') and t['headline'] not in hs:
            out.append(f'task {t["id"]}: headline {t["headline"]!r} is not in metrics.json')
    for h in hs.values():
        if h['task'] not in ids:
            out.append(f'headline {h["id"]}: no task {h["task"]!r}')
        for m in (h['metric'], h.get('also')):
            if m and m not in ms:
                out.append(f'headline {h["id"]}: metric {m!r} is not in metrics.json')
    for p in presets():
        for x in p['tasks']:
            if x['task'] not in ids:
                out.append(f'preset {p["id"]}: no task {x["task"]!r}')
    return out


def plan_problems():
    """Every case of the plans on this PC (plan/<division>/<env>/cases.jsonl) belongs to exactly one task, and every
    headline's condition picks exactly one case per model that has the task."""
    out, ts, hs = [], tasks(), headlines()
    for path in sorted((ROOT / 'plan').glob('*/*/cases.jsonl')):
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        where = f'{path.parent.parent.name}/{path.parent.name}'
        stray = [r['id'] for r in rows if len([t for t in ts if matches(t, r)]) != 1]
        if stray:
            out.append(f'plan {where}: {len(stray)} case(s) in no task or in two, e.g. {stray[0]}')
        for h in hs:
            mine = [r for r in rows if task_of(r, ts) == h['task']]
            per = headline_rows(h, rows, ts)
            none = {(r['family'], r['model']) for r in mine} - set(per)
            many = {k for k, v in per.items() if len(v) != 1} if h['id'] in ('JB-decode', 'JB-ttft-32k', 'JB-page') else set()
            if many or none:   # one case per model for these; the others combine several
                out.append(f'plan {where}: headline {h["id"]} picks {len(many)} model(s) with several cases and '
                           f'{len(none)} with none ({sorted(none)[:3]})')
    return out


def main():
    found = bases()
    for b in found:
        d = b.get('drafter', {})
        print(f'{b.get("base")}: {len(b.get("builds", []))} builds, tokenizer {b.get("tokenizer")}, trained '
              f'{b.get("trained_context")}, thinking {"yes" if b.get("thinking") else "no"}, drafter '
              f'{d.get("pin") or d.get("builtin")}{" (built in)" if "builtin" in d else ""}')
        for e in b.get('builds', []):
            print(f'  {e.get("family")} {e.get("model")}  {e.get("size_gb")} GB'
                  + ('  derivative' if e.get('derivative') else ''))
    for t in tasks():
        print(f'task {t["id"]}: {t["label"]["en"]} ({", ".join(t["metrics"])})' + (f' -> {t["headline"]}' if t.get('headline') else ''))
    for p in presets():
        print(f'preset {p["id"]}: {", ".join(x["task"] + ("*" if x.get("only") else "") for x in p["tasks"])}')
    import engines
    for e in engines.entries():
        print(f'engine {e["id"]}: {e["label"]} ({e["adapter"]}, {"managed" if e["managed"] else "attach only"}, tracks {", ".join(e["tracks"])})')
    known = set(engines.ids())
    stray = [f'{b["base"]} {x["family"]} {x["model"]}: no engine {g!r} in catalog/engines/' for b in found for x in b.get('builds', []) for g in x.get('engines', []) if g not in known]
    bad = problems(found) + stray + engines.problems() + task_problems() + plan_problems()
    for line in bad:
        print('NG ' + line)
    raise SystemExit(1 if bad else 0)


if __name__ == '__main__':
    main()
