#!/usr/bin/env python3
"""Check a run's records against each other (the plan's Tier 0 checks, for every run), into <run dir>/verify.json.

    python3 -I scripts/verify_run.py <env> <run id> [--published]

1. The client's timing of the stream (SSE) against the engine's own timings, request by request: the first character
   cannot come before the engine has read the prompt (ttft_ms >= timings.prompt_ms), and what the client adds on top of
   the engine (ttft_ms - prompt_ms, total_ms - prompt_ms - predicted_ms) stays small: a request is listed when it is over
   LATE_MS and also over LATE_SHARE of the client's time (the runner's own delays show on short prompts, while a long
   prompt's text that the server tokenizes for the first time adds a second or two outside the engine's timings). Only for one request at a time with
   thinking off: with thinking on, the engine's prompt_ms also counts the text it adds when the thinking budget closes the
   thinking (after the first character), and with several requests at once a request also waits for the others in the
   batch. Those two are counted apart, not checked, and so are the runs of a harness division (a record there is one
   harness run of many requests; the proxy keeps each request's own times in harness/seed-N/proxy.jsonl).
2. Every session's launch choices are on the engine's command line (scripts/bench_runner.py not_applied); the runner
   already refuses a launch that fails this, so here it covers runs measured before that check.
3. The presets the tuner saved in Strata's preset store during the run (tune-presets.json of each tune session): these
   are active for their choices, the desktop app's included, so the run lists them.

scripts/overnight_bench.sh runs it after the last Tier; it is published with the run.
"""
import argparse
import importlib.util
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import envs  # noqa: E402

LATE_MS = 500        # client time beyond the engine's, per request, past which a request is listed ...
LATE_SHARE = 0.05    # ... when it is also this share of the client's own time (the server's tokenizing of a long text
                     # it has not seen yet lies outside the engine's timings but is a small part of that wait)
EARLY_MS = -5        # the client seeing the first character this much before the engine finished the prompt


def runner():
    spec = importlib.util.spec_from_file_location('bench_runner', Path(__file__).with_name('bench_runner.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def timing(run_dir):
    first, rest, odd = [], [], []
    skipped = {'thinking': 0, 'concurrent': 0, 'harness': 0}
    for f in sorted(run_dir.glob('cases/*/requests.jsonl')):
        for line in f.read_text().splitlines():
            r = json.loads(line)
            t = r.get('timings') or {}
            if r.get('error') or r.get('ttft_ms') is None or t.get('prompt_ms') is None:
                continue
            if r.get('harness'):
                skipped['harness'] += 1
                continue
            if r.get('reasoning_chars'):
                skipped['thinking'] += 1
                continue
            if '-parallel-' in r['case']:
                skipped['concurrent'] += 1
                continue
            a = r['ttft_ms'] - t['prompt_ms']
            b = r['total_ms'] - t['prompt_ms'] - (t.get('predicted_ms') or 0)
            first.append(a)
            rest.append(b)
            late = lambda extra, of: extra > LATE_MS and extra > LATE_SHARE * of  # noqa: E731
            if a < EARLY_MS or late(a, r['ttft_ms']) or late(b, r['total_ms']):
                odd.append({'case': r['case'], 'seed': r.get('seed'), 'restart': r.get('restart'),
                            'ttft_minus_prompt_ms': round(a, 1), 'total_minus_engine_ms': round(b, 1)})
    q = lambda v, p: round(statistics.quantiles(v, n=100)[p - 1], 1) if len(v) > 1 else None  # noqa: E731
    return {'requests': len(first), 'not_checked': skipped,
            'ttft_minus_prompt_ms': {'median': q(first, 50), 'p99': q(first, 99), 'min': round(min(first), 1) if first else None},
            'total_minus_engine_ms': {'median': q(rest, 50), 'p99': q(rest, 99)},
            'outside': odd[:50], 'outside_count': len(odd),
            'ok': not odd}


def settings(run_dir):
    br = runner()
    missing = []
    for s in sorted(run_dir.glob('sessions/*/start-*/session.json')) + sorted(run_dir.glob('sessions/S2-*/session.json')):
        info = json.loads(s.read_text())
        log = s.with_name('engine.log')
        if not info.get('argv') or info.get('rc') != 0 or not log.exists():
            continue
        m = br.not_applied(info['argv'], log.read_text(errors='replace'))
        if m:
            missing.append({'session': str(s.parent.relative_to(run_dir)), 'missing': m})
    return {'missing': missing, 'ok': not missing}


def tune_presets(run_dir):
    out = []
    for f in sorted(run_dir.glob('sessions/*/start-*/tune-presets.json')):
        for p in json.loads(f.read_text()):
            out.append({'session': str(f.parent.relative_to(run_dir)), 'name': p.get('name'), 'id': p.get('id'),
                        'active': p.get('active'), 'settings': (p.get('settings') or {}).get('args')})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('env')
    ap.add_argument('run_id')
    ap.add_argument('--published', action='store_true', help='the run in published/ (default: results/)')
    a = ap.parse_args()
    run_dir = envs.published_dir(a.env, a.run_id) if a.published else envs.run_dir(a.env, a.run_id)
    doc = {'run_id': a.run_id, 'env': a.env, 'timing': timing(run_dir), 'settings': settings(run_dir),
           'tune_presets': tune_presets(run_dir)}
    doc['ok'] = doc['timing']['ok'] and doc['settings']['ok']
    (run_dir / 'verify.json').write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n')
    t = doc['timing']
    print(f'{a.run_id}: {t["requests"]} requests (not checked: {t["not_checked"]}), client - engine at the first character: median {t["ttft_minus_prompt_ms"]["median"]} ms, '
          f'p99 {t["ttft_minus_prompt_ms"]["p99"]} ms, min {t["ttft_minus_prompt_ms"]["min"]} ms; at the end: median '
          f'{t["total_minus_engine_ms"]["median"]} ms, p99 {t["total_minus_engine_ms"]["p99"]} ms; {t["outside_count"]} outside')
    print(f'  settings not on the engine command line: {len(doc["settings"]["missing"])} session(s); '
          f'tuner presets saved: {[p["name"] for p in doc["tune_presets"]]}')
    return 0 if doc['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
