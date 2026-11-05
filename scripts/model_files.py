#!/usr/bin/env python3
"""Which version of each model a run measured: results/<division>/<env>/<run-id>/models.json.

A model keeps its name when its publisher uploads a new version, so the name alone does not say what was measured.
Every file the benchmark fetches is pinned by Strata's setup.py to a Hugging Face commit and a SHA-256
(downloads/manifest.json); the downloader verified each one and left its SHA-256 in a `.done` mark beside the file.
models.json keeps, per model, the repository, the commit and every file with its size and SHA-256, and whether the
file on disk still carries that SHA-256 when the run starts ("verified"). It is published with the run.

scripts/bench_runner.py writes it at the start of a run. If a resumed run finds other files than the first start did,
the earlier record is kept in "earlier" and the new one becomes the record.

    python3 -I scripts/model_files.py <run dir> ... [--note "..."]    # write it for a run recorded before it existed
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'downloads/manifest.json'
HF = re.compile(r'^https://huggingface\.co/(?P<repo>[^/]+/[^/]+)/resolve/(?P<rev>[0-9a-f]{40})/(?P<name>.+)$')
# NVFP4-QAD: NVIDIA's checkpoint is converted on the measuring PC and its tensors deleted afterwards (scripts/overnight.py)
PREPARED = ('ple-nvfp4.gguf.done', 'dense.gguf.done', 'pack.done', 'draft.done')


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def on_disk(root, f):
    """verified: the downloader's mark carries the pinned SHA-256; differs: another one; missing: no file or no mark."""
    path, mark = root / f['path'], root / (f['path'] + '.done')
    if not path.is_file() or not mark.is_file():
        return 'missing'
    got = mark.read_text().split()
    return 'verified' if got[-1:] == [f['sha256']] else 'differs'


def snapshot():
    """Every model of the manifest: its repository, commit and files, as they are on disk now."""
    m = json.loads(MANIFEST.read_text())
    root = Path(m['models_root'])
    models = {}
    for f in m['files']:
        hit = HF.match(f['url'])
        if not hit:
            raise SystemExit(f'model_files: not a pinned Hugging Face URL: {f["url"]}')
        entry = models.setdefault((f['family'], f['model']), {'family': f['family'], 'model': f['model'], 'sources': {}})
        src = entry['sources'].setdefault((hit['repo'], hit['rev']), {
            'repo': hit['repo'], 'revision': hit['rev'],
            'url': f'https://huggingface.co/{hit["repo"]}/tree/{hit["rev"]}', 'files': []})
        src['files'].append({'name': hit['name'], 'bytes': f['bytes'], 'sha256': f['sha256'], 'on_disk': on_disk(root, f)})
    out = []
    for entry in models.values():
        entry['sources'] = list(entry['sources'].values())
        files = [x for s in entry['sources'] for x in s['files']]
        if entry['model'] == 'NVFP4-QAD':
            prepared = root / 'nvidia--Qwen3.8-Flash-Next-FP4-Local/prepared'
            done = all((prepared / p).is_file() for p in PREPARED)
            entry['converted_on_this_machine'] = done
            if done:   # the checkpoint's tensors are gone on purpose; what was converted is the pinned checkpoint
                for x in files:
                    if x['on_disk'] == 'missing' and x['name'].endswith('.safetensors'):
                        x['on_disk'] = 'converted, then deleted'
        states = {x['on_disk'] for x in files}
        entry['state'] = 'verified' if states <= {'verified', 'converted, then deleted'} else \
            'differs' if 'differs' in states else 'missing'
        out.append(entry)
    return {'strata_source_commit': m.get('source_commit'), 'strata_setup_sha256': m.get('source_setup_sha256'),
            'models': out}


def same(a, b):
    def key(r):
        return [(e['family'], e['model'], e['state'],
                 [(s['repo'], s['revision'], [(x['name'], x['sha256'], x['on_disk']) for x in s['files']])
                  for s in e['sources']]) for e in r['models']]
    return key(a) == key(b)


def record(run_dir, note=None):
    """Write <run dir>/models.json; returns its state in a word for the runner's log."""
    if not MANIFEST.exists():
        return 'no downloads/manifest.json: models.json not written'
    path = Path(run_dir) / 'models.json'
    new = {'recorded_at': now(), **snapshot()}
    if note:
        new['note'] = note
    old = json.loads(path.read_text()) if path.exists() else None
    if old and same(old, new):
        return 'unchanged'
    if old:
        new['earlier'] = old.pop('earlier', []) + [old]
    path.write_text(json.dumps(new, indent=2, ensure_ascii=False) + '\n')
    bad = [f'{e["family"]} {e["model"]}: {e["state"]}' for e in new['models'] if e['state'] != 'verified']
    return ('changed since the last start; ' if old else '') + ('; '.join(bad) if bad else 'every model verified')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('run_dirs', nargs='+', type=Path)
    ap.add_argument('--note', help='kept in models.json, e.g. that it was written after the run')
    a = ap.parse_args()
    for d in a.run_dirs:
        print(f'{d}: {record(d, a.note)}')


if __name__ == '__main__':
    sys.exit(main())
