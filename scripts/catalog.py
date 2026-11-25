"""The catalog: what jbench can measure, as data (catalog/README.md).

catalog/models/<base>.json is one base model (Qwen3.8-Flash-Next, Hy4-Flash, ...) with what holds for every build of
it (tokenizer, trained length, whether it thinks, its drafter) and its builds (family, model, size, role). The plan
builder and the runner read these properties instead of naming families: a new base model or build is a JSON edit.

`python3 -I scripts/catalog.py` lists the catalog and reports what is wrong in it.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = ROOT / 'catalog' / 'models'

BASE_KEYS = {'base', 'order', 'label', 'tokenizer', 'trained_context', 'max_context', 'thinking', 'lineup', 'drafter',
             'builds'}
BUILD_KEYS = {'family', 'model', 'size_gb', 'role', 'derivative', 'display'}


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
    bad = problems(found)
    for line in bad:
        print('NG ' + line)
    raise SystemExit(1 if bad else 0)


if __name__ == '__main__':
    main()
