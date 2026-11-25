"""The recipe: what a run measures, as one text that can be pasted, kept and compared.

    jbench-recipe/1
    engine: strata (track exact)
    driver: plain
    preset: standard
    tasks: long-read
    models: qwen IQ3_S, inkling-2-mini SQ-15
    id: r1-3f9a2c7e

The configurator page writes it (preview/configurator.html), the user pastes it to the agent or into
`python3 -I scripts/bench.py recipe --apply`, the run keeps it (recipe.txt) and the result pages show it.

The id is a hash of what makes results comparable and nothing else: the engine and its track, the driver (the
division), and the tasks chosen with their versions. The models are not in it (what is measured is not the ruler), nor
are the run's name and the watch settings. Two runs with the same id asked the same things of the same kind of engine.
Case by case the ruler is finer still: every case carries the hash of its own conditions (case_plan.condition), and
only cases with the same hash are put side by side across environments.

Lines: "engine: <id> (track <t>)" or "engine: <id>"; "driver: <division>"; "preset: <id>" and / or
"tasks: a, b" (a task may be narrowed as in the preset: "speed-decode[headline]"); "models: all" or a list;
"id:" is checked when present. Unknown lines are an error, so that a typo does not silently change a run.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catalog  # noqa: E402
import engines  # noqa: E402

HEAD = 'jbench-recipe/1'


def task_specs(cfg):
    """The tasks a configuration chooses, as the preset and "tasks" say: [{'task', 'headline_only'?, 'only'?}], in the
    catalog's order, one entry per task (the widest wins: a task named whole beside its headline-only form is whole)."""
    wanted = []
    if cfg.get('preset'):
        found = [p for p in catalog.presets() if p['id'] == cfg['preset']]
        if not found:
            raise SystemExit(f'no preset {cfg["preset"]!r} (catalog/tasks.json)')
        wanted += found[0]['tasks']
    wanted += [{'task': t} for t in cfg.get('tasks') or []]
    by = {}
    for w in wanted:
        old = by.get(w['task'])
        if old is None or (old.get('headline_only') or old.get('only')) and not (w.get('headline_only') or w.get('only')):
            by[w['task']] = w
    order = [t['id'] for t in catalog.tasks()]
    return [by[t] for t in order if t in by]


def recipe_id(cfg):
    versions = {t['id']: t.get('version', 1) for t in catalog.tasks()}
    specs = task_specs(cfg)
    what = {'v': 1, 'engine': cfg.get('engine') or engines.DEFAULT, 'track': cfg.get('track') or 'exact',
            'driver': cfg.get('division') or 'plain',
            'tasks': [{**s, 'version': versions.get(s['task'], 1)} for s in specs] or {'tiers': cfg.get('tiers')}}
    return 'r1-' + hashlib.sha256(json.dumps(what, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:8]


def text(cfg):
    """The recipe of a configuration (bench.json with the defaults filled in)."""
    engine, track = cfg.get('engine') or engines.DEFAULT, cfg.get('track') or 'exact'
    lines = [HEAD, f'engine: {engine} (track {track})', f'driver: {cfg.get("division") or "plain"}']
    if cfg.get('preset'):
        lines.append(f'preset: {cfg["preset"]}')
    if cfg.get('tasks'):
        lines.append('tasks: ' + ', '.join(cfg['tasks']))
    if not cfg.get('preset') and not cfg.get('tasks'):
        lines.append('tiers: ' + (', '.join(cfg['tiers']) if cfg.get('tiers') else 'all'))
    lines.append('models: ' + (', '.join(cfg['models']) if cfg.get('models') else 'all'))
    lines.append(f'id: {recipe_id(cfg)}')
    return '\n'.join(lines) + '\n'


def parse(src):
    """A pasted recipe -> the bench.json keys it sets. Raises SystemExit with what is wrong."""
    lines = [ln.strip() for ln in src.strip().splitlines() if ln.strip() and not ln.strip().startswith('#')]
    lines = [ln.strip('`').strip() for ln in lines if ln.strip('`').strip()]      # pasted inside a code fence
    if not lines or lines[0] != HEAD:
        raise SystemExit(f'a recipe starts with the line "{HEAD}"')
    out, given = {'preset': None, 'tasks': None, 'tiers': None, 'models': None}, None
    for ln in lines[1:]:
        if ':' not in ln:
            raise SystemExit(f'recipe: not "key: value": {ln!r}')
        key, val = (x.strip() for x in ln.split(':', 1))
        items = [x.strip() for x in val.split(',') if x.strip()]
        if key == 'engine':
            m = re.fullmatch(r'(\S+)(?:\s*\(track\s+(\w+)\))?', val)
            if not m:
                raise SystemExit(f'recipe: engine: "<id>" or "<id> (track exact|default|custom)", not {val!r}')
            out['engine'], out['track'] = m.group(1), m.group(2) or 'exact'
            e = engines.entry(out['engine'])
            if out['track'] not in e['tracks']:
                raise SystemExit(f'recipe: engine {out["engine"]} has no track {out["track"]!r}')
        elif key == 'driver':
            out['division'] = val
        elif key == 'preset':
            if val not in [p['id'] for p in catalog.presets()]:
                raise SystemExit(f'recipe: no preset {val!r} (catalog/tasks.json)')
            out['preset'] = val
        elif key == 'tasks':
            known = {t['id'] for t in catalog.tasks()}
            bad = [t for t in items if t not in known]
            if bad:
                raise SystemExit(f'recipe: no task {", ".join(bad)} (python3 -I scripts/catalog.py lists them)')
            out['tasks'] = items
        elif key == 'tiers':
            out['tiers'] = None if val == 'all' else items
        elif key == 'models':
            if val != 'all':
                known = {f'{f} {m}' for f, m, *_ in catalog.builds()}
                bad = [m for m in items if m not in known]
                if bad:
                    raise SystemExit(f'recipe: not in the catalog: {", ".join(bad)} (catalog/models/)')
                out['models'] = items
        elif key == 'id':
            given = val
        else:
            raise SystemExit(f'recipe: unknown line {key!r}')
    if 'engine' not in out:
        raise SystemExit('recipe: no "engine:" line')
    out.setdefault('division', 'plain')
    want = recipe_id(out)
    if given and given != want:
        raise SystemExit(f'recipe: its id is {given} but its lines give {want}: the text was changed after it was made, '
                         'or it was made with another version of the tasks (catalog/tasks.json)')
    return out


def main():
    import config
    print(text(config.load()), end='')


if __name__ == '__main__':
    main()
