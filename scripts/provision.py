"""What jbench uses on this PC and where it came from: tools/provision.json (not in Git; docs/001 3.5).

A run measures engines, harnesses and models at fixed versions. Wherever possible they are fetched for jbench alone,
into tools/ (or, for models, a folder the user names on a larger disk), and what is used is written here: what, which
version, its SHA-256, where it is, where it came from, and whether jbench fetched it ("by": "jbench") or the user
pointed at something already on the PC ("by": "user"). A run copies this file into its folder at each start, and it is
published with the run.

    python3 -I scripts/provision.py                      # what is recorded
    python3 -I scripts/provision.py set-engine sync-strata --path DIR [--models-dir DIR] [--by user|jbench] ...
"""
import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / 'tools' / 'provision.json'


def load():
    try:
        return json.loads(PATH.read_text())
    except FileNotFoundError:
        return {}
    except ValueError as e:
        raise SystemExit(f'tools/provision.json is not valid JSON: {e}')


def save(doc):
    PATH.parent.mkdir(parents=True, exist_ok=True)
    PATH.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + '\n')


def engine(engine_id):
    return load().get('engines', {}).get(engine_id, {})


def models(group):
    return load().get('models', {}).get(group, {})


def put(kind, name, **fields):
    doc = load()
    entry = doc.setdefault(kind, {}).setdefault(name, {})
    entry.update({k: v for k, v in fields.items() if v is not None})
    entry['recorded_at'] = datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds')
    save(doc)
    return entry


def copy_to(run_dir):
    """The run's own copy (home written as ~, as everything published is)."""
    if PATH.exists():
        (Path(run_dir) / 'provision.json').write_text(PATH.read_text().replace(str(Path.home()), '~'))
    return PATH.exists()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd')
    for cmd, kind in (('set-engine', 'engines'), ('set-models', 'models'), ('set-harness', 'harnesses')):
        p = sub.add_parser(cmd)
        p.set_defaults(kind=kind)
        p.add_argument('name')
        p.add_argument('--path', required=True, help='where it is')
        p.add_argument('--models-dir', help='an engine\'s models folder, when it is not inside the engine\'s own')
        p.add_argument('--version')
        p.add_argument('--source', help='the URL or repository it came from')
        p.add_argument('--sha256', help='of the downloaded archive, or of the file')
        p.add_argument('--by', choices=['jbench', 'user'], default='jbench',
                       help='jbench fetched it for itself, or the user named something already on the PC')
        p.add_argument('--note')
    a = ap.parse_args()
    if not a.cmd:
        print(json.dumps(load(), ensure_ascii=False, indent=1) if PATH.exists() else 'tools/provision.json: nothing recorded')
        return
    if not Path(a.path).expanduser().exists():
        raise SystemExit(f'{a.path} does not exist')
    e = put(a.kind, a.name, path=str(Path(a.path).expanduser()), models_dir=a.models_dir, version=a.version,
            source=a.source, sha256=a.sha256, by=a.by, note=a.note)
    print(json.dumps({a.name: e}, ensure_ascii=False, indent=1))
    free = shutil.disk_usage(Path(a.path).expanduser()).free
    print(f'{free / 1e9:.0f} GB free on its disk')


if __name__ == '__main__':
    main()
