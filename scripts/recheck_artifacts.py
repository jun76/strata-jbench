#!/usr/bin/env python3
"""Capture the coding cases' pages of a run again, with the runner's current screenshot step (bench_runner.screenshot:
the page's errors, whether it froze, whether anything was drawn), without asking the models again.

  python3 -I scripts/recheck_artifacts.py results/plain/rtx5090-128g/<RUN_ID> [--ids <case id>,...]

Rewrites each seed's screenshot.png, console.txt and the manifest's "screenshot", the same record in requests.jsonl,
and the counts in summary.json ("drawn", "hung"). Run it while no measurement is running (Chrome uses the CPU).
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bench_runner  # noqa: E402


def recheck(case_dir):
    shots = {}
    for d in sorted(case_dir.glob('artifact/seed-*')):
        mf = d / 'manifest.json'
        if not mf.exists():
            continue
        m = json.loads(mf.read_text())
        entry = m.get('entry')
        if not entry or not (d / 'files' / entry).exists():
            continue
        m['screenshot'] = bench_runner.screenshot(d / 'files', entry, d)
        mf.write_text(json.dumps(m, ensure_ascii=False, indent=2) + '\n')
        shots[int(d.name.split('-')[1])] = m['screenshot']
        s = m['screenshot']
        print(f"  {d.name}: {'drawn' if s.get('drawn') else 'hung' if s.get('hung') else 'empty' if s.get('ok') else s.get('error')}"
              f", {len(s.get('console_errors') or [])} errors")
    if not shots:
        return
    req = case_dir / 'requests.jsonl'
    lines = []
    for line in req.read_text().splitlines():
        r = json.loads(line)
        if r.get('artifact') and r.get('seed') in shots:
            r['artifact']['screenshot'] = shots[r['seed']]
        lines.append(json.dumps(r, ensure_ascii=False))
    req.write_text('\n'.join(lines) + '\n')
    sf = case_dir / 'summary.json'
    if sf.exists():
        s = json.loads(sf.read_text())
        arts = [json.loads(line).get('artifact') for line in lines]
        arts = [a for a in arts if a]
        s['drawn'] = f"{sum(1 for a in arts if (a.get('screenshot') or {}).get('drawn'))}/{len(arts)}"
        s['hung'] = sum(1 for a in arts if (a.get('screenshot') or {}).get('hung'))
        sf.write_text(json.dumps(s, ensure_ascii=False, indent=2) + '\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('run_dir', type=Path)
    ap.add_argument('--ids', default='')
    a = ap.parse_args()
    ids = {i for i in a.ids.split(',') if i}
    for case_dir in sorted((a.run_dir / 'cases').iterdir()):
        if (ids and case_dir.name not in ids) or not (case_dir / 'artifact').exists():
            continue
        print(case_dir.name)
        recheck(case_dir)


if __name__ == '__main__':
    main()
