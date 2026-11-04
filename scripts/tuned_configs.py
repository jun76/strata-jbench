#!/usr/bin/env python3
"""What Strata's tuner chose in the Tier 5 tune cases, as configs/tuned/<family>-<model>.json (tracked).

    python3 -I scripts/tuned_configs.py

Read from published/ alone: each tune session's tune-presets.json (the presets the tuner saved during that launch, kept
by scripts/bench_runner.py). A session published before the runner kept them is filled in once from Strata's own preset
list, matched by the time the preset was made (within the session), and its tune-presets.json written beside it.
When several runs tuned the same model, the run whose name sorts last wins, as on the pages.
"""
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import envs  # noqa: E402
import publish  # noqa: E402  (scrub: ~ and <host>)

ROOT = envs.ROOT
OUT = ROOT / 'configs' / 'tuned'


def strata_presets():
    r = subprocess.run(['strata', 'presets', 'list', '--output', 'json'], capture_output=True, text=True, timeout=120)
    try:
        return json.loads(r.stdout).get('presets', [])
    except ValueError:
        return []


def backfill(session_dir, presets):
    """tune-presets.json for a session published before the runner kept it: the presets made while it ran."""
    info = json.loads((session_dir / 'session.json').read_text())
    t0 = datetime.fromisoformat(info['started_at']).timestamp() - info.get('launch_s', 0) - 5
    t1 = datetime.fromisoformat(info.get('ended_at') or info['started_at']).timestamp() + 5
    made = [p for p in presets if t0 <= datetime.fromisoformat(p['created']).timestamp() <= t1]
    out = session_dir / 'tune-presets.json'
    out.write_text(json.dumps(made, ensure_ascii=False, indent=2) + '\n')
    publish.scrub(out)
    return made


def main():
    presets = None
    found = {}
    for start in sorted((envs.PUBLISHED / 'plain').glob('*/*/sessions/S-*-tune-*-T5/start-1')):   # the launches of the plain division
        run, name = start.parents[2].name, start.parent.name
        mode = 'thorough' if '-tune-thorough-' in name else 'quick'
        info = json.loads((start / 'session.json').read_text())
        argv = info.get('argv') or []
        fam, model = argv[argv.index('--family') + 1], argv[argv.index('--model') + 1]
        f = start / 'tune-presets.json'
        if f.exists():
            made = json.loads(f.read_text())
        else:
            presets = strata_presets() if presets is None else presets
            made = backfill(start, presets)
        # the tuner's own one-line verdict ("Tuning result: …"), also when it kept the standard settings and saved nothing
        said = re.search(r'Tuning result: (.*)', (start / 'launch.txt').read_text(errors='replace'))
        base = {'run_id': run, 'env': start.parents[3].name, 'session': f'{name}/start-1', 'mode': mode,
                'result': said.group(1).strip() if said else None}
        if not made:
            found[(fam, model, mode)] = {**base, 'preset': None, 'settings': None}
            continue
        p = made[-1]
        found[(fam, model, mode)] = {
            **base,
            'preset': {k: p.get(k) for k in ('name', 'id', 'created', 'active')},
            'settings': p.get('settings'), 'tuner': p.get('tuner'), 'gain_pct': p.get('gain_pct'),
            'baseline_decode_tok_s': p.get('baseline_decode_tok_s', (p.get('baseline') or {}).get('decode_tok_s')),
            'decode_tok_s': p.get('decode_tok_s'), 'choices': p.get('choices'),
        }
    OUT.mkdir(parents=True, exist_ok=True)
    models = sorted({(f, m) for f, m, _ in found})
    for fam, model in models:
        doc = {'family': fam, 'model': model,
               'note': 'What Strata\'s tuner chose in the Tier 5 tune cases (strata launch --tune quick / thorough --retune).',
               **{mode: found[(fam, model, mode)] for mode in ('quick', 'thorough') if (fam, model, mode) in found}}
        path = OUT / f'{fam}-{model}.json'
        path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n')
        publish.scrub(path)
    print(f'configs/tuned/: {len(models)} model(s), {len(found)} tune result(s)')


if __name__ == '__main__':
    main()
