"""The benchmark's settings: bench.json at the repository's root (not in Git; AGENTS.md 2.2).

bench.json holds only what differs from the defaults below; every key it may hold is in PARAMS, with its default and
what it does (`python3 -I scripts/bench.py config` lists them with the values in force). The supervisor keeps the
settings a run started with in the run's folder (bench.json, the defaults filled in), published with the run.

What makes results comparable is not a setting: the cases themselves (seeds, temperatures, contexts, prompts) are the
plan, in scripts/build_cases.py; the hardware and the measurer's choices per environment (its models, the reference
model, power limits) are its env.json (envs/README.md).
"""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / 'bench.json'

# key: (default, type, description)
PARAMS = {
    'run_id': (None, str,
               'The run: results/<division>/<env>/<run_id>/. A new name starts a run, an existing one resumes it '
               '(finished cases are skipped). A name starting with test- is for checks: never in the lists or charts, '
               'never published. When the same case is in two runs, the pages show the run whose name sorts last.'),
    'division': ('plain', str,
                 'How the models are driven (divisions/README.md): plain (the engine API directly) or a harness '
                 'division (dsh, strata, opencode, hermes, pi). Only a division whose status is active can be measured.'),
    'env': (None, str,
            'The environment (envs/<env>/env.json). null: the one this hardware matches; a name must match it too.'),
    'tiers': (None, list,
              'The Tiers to run, in this order, e.g. ["1", "3"]. null: every Tier of the division (plain 0 1 2 3 4a '
              '4b 4c 4d 5, a harness division G). Tier 0 checks the instruments: worth running once per environment.'),
    'models': (None, list,
               'Only these models of the plan, e.g. ["qwen IQ3_S"]. null: every model of the plan (env.json "models"). '
               'Leaving a model out of the environment for good is env.json\'s "models" instead.'),
    'cases': (None, list,
              'Only these case ids (the case lists, plan/<division>/<env>/cases.csv), e.g. to measure one case again. '
              'null: every case of the Tiers and models chosen.'),
    'fetch': (False, bool,
              'true: fetch what the run needs and is missing (models from Hugging Face, the DFlash2 drafter, the '
              'pinned harness; scripts/acquire.py). false: report it and start nothing. Only with the user\'s agreement.'),
    'smoke': (True, bool,
              'Preflight launches the reference model once for real before the run (a GPU check). false: skip it, '
              'for a run resumed right after one that passed.'),
    'stats': (True, bool,
              'Machine snapshots during the run (scripts/stats_watch.py: processes, CPU, memory, temperatures, GPU; '
              'stats/thermal.csv every 5 s).'),
    'watch_interval_s': (300, int,
                         'How often the supervisor checks the run (scripts/healthcheck.py: run-status/STATUS.md, '
                         'run-status/ALERTS.log, a desktop notification on a new problem).'),
    'crash_restarts': (1, int,
                       'How many times the supervisor starts a Tier\'s runner again after it exits with an error '
                       '(finished cases are skipped). Past that the Tier is left FAILED and the next one runs.'),
    'stuck_restarts': (1, int,
                       'How many times the supervisor stops and starts again a runner that has written nothing for '
                       'longer than any step needs (75 min; 3 h 20 min during a launch). Past that the Tier is left '
                       'FAILED and the next one runs.'),
    'launch_timeout_s': (3 * 3600, int,
                         'How long the runner waits for one engine launch (with tuning) before failing its cases.'),
    'notify': (True, bool, 'Desktop notifications (notify-send) on a problem and when the run ends.'),
}


def defaults():
    return {k: v[0] for k, v in PARAMS.items()}


def here():
    """The settings file in force: the run's own copy for the scripts its supervisor runs ($BENCH_CONFIG), else bench.json."""
    return Path(os.environ.get('BENCH_CONFIG') or PATH)


def read(path=None):
    """bench.json as written (only the keys it sets), {} without one."""
    path = path or here()
    try:
        return json.loads(Path(path).read_text())
    except FileNotFoundError:
        return {}
    except ValueError as e:
        raise SystemExit(f'{Path(path).name} is not valid JSON: {e}')


def problems(own):
    out = []
    for k, v in own.items():
        if k not in PARAMS:
            out.append(f'unknown key {k!r} (python3 -I scripts/bench.py config lists them)')
            continue
        typ = PARAMS[k][1]
        if v is None:
            continue
        if typ is int and (isinstance(v, bool) or not isinstance(v, int)) or typ is not int and not isinstance(v, typ):
            out.append(f'{k}: {v!r} is not a {typ.__name__}')
        elif typ is list and not all(isinstance(x, str) for x in v):
            out.append(f'{k}: every item is a string ({v!r})')
    return out


def load(path=None, need_run_id=False):
    path = path or here()
    own = read(path)
    bad = problems(own)
    if bad:
        raise SystemExit(f'{Path(path).name}: ' + '; '.join(bad))
    cfg = {**defaults(), **own}
    if need_run_id and not cfg['run_id']:
        raise SystemExit(f'set "run_id" in {Path(path).name} (python3 -I scripts/bench.py config)')
    return cfg


def get(key):
    """One setting in force, for the scripts that fall back on bench.json (scripts/envs.py: the division, the env)."""
    return load().get(key)


def select(rows, cfg):
    """The plan's rows the settings choose, in the order of "tiers"."""
    tiers = cfg.get('tiers')
    models = set(cfg.get('models') or [])
    cases = set(cfg.get('cases') or [])
    out = [r for r in rows if (not tiers or r['step'] in tiers) and (not models or f'{r["family"]} {r["model"]}' in models)
           and (not cases or r['id'] in cases)]
    if tiers:
        out.sort(key=lambda r: tiers.index(r['step']))
    return out


def table(cfg=None):
    """Every parameter: name, value in force, default, whether bench.json sets it, what it does."""
    own = read()
    cfg = cfg or load()
    return [{'key': k, 'value': cfg[k], 'default': d, 'set': k in own, 'about': about}
            for k, (d, _, about) in PARAMS.items()]
