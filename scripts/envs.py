#!/usr/bin/env python3
"""Test environments: one per hardware set-up the benchmark runs on (a GPU and an amount of RAM on this PC, or another PC).

Each environment is a folder envs/<id>/ with env.json (see envs/README.md). The results are also split by division
(divisions/<division>/division.json: how the models are driven, "plain" = the engine's API with no agent harness):
the plan of an environment is plan/<division>/<id>/, its results results/<division>/<id>/<run id>/ and its case list
cases/<division>/<id>.html. Which environment a run belongs to is never typed by hand
in the middle of a measurement: it is the environment whose "match" fits the hardware found now (GPU name and RAM),
and the runner and preflight refuse to measure under an environment that does not match.

    python3 -I scripts/envs.py detect              # the id of the environment this hardware is (exit 1 if none)
    python3 -I scripts/envs.py list                # every environment, and which one matches now
    python3 -I scripts/envs.py new <id>            # write envs/<id>/env.json from the hardware found now
    python3 -I scripts/envs.py run-dir <run id>    # results/<division>/<env>/<run id> for the detected environment
    python3 -I scripts/envs.py divisions           # every division and whether it is measured yet

The division is $BENCH_DIVISION, "plain" when unset; only a division whose division.json says "status": "active" can be
measured (the others are planned: the runner does not drive a harness yet).
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENVS = ROOT / 'envs'
DIVISIONS = ROOT / 'divisions'
RAM_TOLERANCE = 0.03      # MemTotal moves a little between kernels and firmware settings, not by a whole module


def ids():
    return sorted(p.parent.name for p in ENVS.glob('*/env.json'))


def load(env_id):
    path = ENVS / env_id / 'env.json'
    if not path.exists():
        raise SystemExit(f'no environment {env_id!r}: {path} is missing (scripts/envs.py new {env_id})')
    cfg = json.loads(path.read_text())
    cfg['id'] = env_id
    cfg.setdefault('drafters', ['mtp'])
    cfg.setdefault('models', None)            # None: every model of the plan
    cfg.setdefault('gpu_power_limit_w', None) # None: the card's default, not checked
    cfg.setdefault('assume', {})
    return cfg


def hardware():
    """The GPU and RAM found now (scripts/machine_info.py)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import machine_info
    return machine_info.collect()['env']


def matches(cfg, hw):
    m = cfg.get('match') or {}
    if m.get('gpu') and m['gpu'] != hw.get('gpu'):
        return False
    if m.get('ram_gib') and hw.get('ram_gib'):
        if abs(hw['ram_gib'] - m['ram_gib']) > m['ram_gib'] * RAM_TOLERANCE:
            return False
    return bool(m)


def detect(hw=None):
    hw = hw or hardware()
    found = [i for i in ids() if matches(load(i), hw)]
    return found[0] if len(found) == 1 else None, found, hw


def current(explicit=None):
    """The environment to use: --env / $BENCH_ENV if given (it must match the hardware), else the detected one."""
    want = explicit or os.environ.get('BENCH_ENV') or None
    env_id, found, hw = detect()
    if want:
        if want not in found:
            raise SystemExit(f'environment {want!r} does not match this hardware ({hw.get("gpu")}, {hw.get("ram_gib")} GiB RAM); '
                             f'matching: {", ".join(found) or "none"}')
        return want
    if not env_id:
        raise SystemExit(f'no single environment matches this hardware ({hw.get("gpu")}, {hw.get("ram_gib")} GiB RAM); '
                         f'matching: {", ".join(found) or "none"}. Add one: python3 -I scripts/envs.py new <id>')
    return env_id


def division_ids():
    return sorted(p.parent.name for p in DIVISIONS.glob('*/division.json'))


def load_division(div_id):
    path = DIVISIONS / div_id / 'division.json'
    if not path.exists():
        raise SystemExit(f'no division {div_id!r}: {path} is missing (divisions/README.md)')
    cfg = json.loads(path.read_text())
    cfg['id'] = div_id
    return cfg


def division(explicit=None, measuring=False):
    """The division to use: --division / $BENCH_DIVISION if given, else "plain". measuring=True: it must be active."""
    div_id = explicit or os.environ.get('BENCH_DIVISION') or 'plain'
    cfg = load_division(div_id)
    if measuring and cfg.get('status') != 'active':
        raise SystemExit(f'division {div_id!r} is {cfg.get("status")!r}, not measured yet (divisions/{div_id}/division.json)')
    return div_id


def plan_dir(env_id, div=None):
    return ROOT / 'plan' / division(div) / env_id


# Runs are measured into results/ (ignored by Git). A run that is final is moved to published/ (tracked) by
# scripts/publish.py. The pages built from published/ alone are the ones committed (CASES.html, cases/, RESULTS.html);
# a build that also reads results/ writes its pages to preview/ (ignored), so a running benchmark never touches a tracked file.
WORK = ROOT / 'results'
PUBLISHED = ROOT / 'published'
PREVIEW = ROOT / 'preview'


def results_dir(env_id, div=None):
    return WORK / division(div) / env_id


def run_dir(env_id, run_id, div=None):
    """Where the runner writes a run (results/<division>/<env>/<run id>)."""
    return results_dir(env_id, div) / run_id


def published_dir(env_id, run_id, div=None):
    """Where a final run lives (published/<division>/<env>/<run id>)."""
    return PUBLISHED / division(div) / env_id / run_id


def run_dirs(env_id, published_only=False, div=None):
    """Every run of the environment the pages may show, sorted by run id: published/ and (unless published_only)
    results/, test- runs left out. A run id in both is read from published/."""
    found = {}
    for root in ([WORK] if not published_only else []) + [PUBLISHED]:
        for d in (root / division(div) / env_id).glob('*/'):
            if d.is_dir() and not d.name.startswith('test-'):
                found[d.name] = d
    return [found[k] for k in sorted(found)]


def label(cfg):
    return cfg.get('label') or cfg['id']


def slug(hw):
    """A suggested id: rtx5090-128g."""
    gpu = re.sub(r'^(NVIDIA )?(GeForce )?', '', hw.get('gpu') or 'gpu').lower().replace(' ', '')
    ram = -(-hw['ram_gib'] // 16) * 16 if hw.get('ram_gib') else 0
    return f'{gpu}-{ram:.0f}g'


def dflash2_here():
    """Whether Auto drafting picks DFlash2 for a Qwen3.8 model on this card (strata launch --plan)."""
    try:
        out = subprocess.run(['strata', 'launch', '--plan', '--family', 'qwen', '--model', 'IQ3_S', '--context', '128k',
                              '--vision', 'off', '--parallel', '1', '--tune', 'skip', '--port', '18600', '--output', 'json'],
                             capture_output=True, text=True, timeout=180, cwd='/tmp').stdout
        plan = json.loads(out[out.index('{'):])['plan']
        return 'dflash2' in json.dumps(plan.get('drafting', '')).lower()
    except (OSError, ValueError, KeyError, subprocess.SubprocessError):
        return False


def new(env_id):
    hw = hardware()
    path = ENVS / env_id / 'env.json'
    if path.exists():
        raise SystemExit(f'{path} already exists')
    ram = -(-hw['ram_gib'] // 16) * 16
    cfg = {
        'label': f'{re.sub(r"^NVIDIA ", "", hw.get("gpu") or "?")} · {ram:.0f} GB RAM',
        'match': {'gpu': hw.get('gpu'), 'ram_gib': hw.get('ram_gib')},
        'hardware': {'gpu_vram_gib': round((hw.get('gpu_vram_mib') or 0) / 1024, 1), 'ram_gib': hw.get('ram_gib')},
        'gpu_power_limit_w': None,
        'drafters': ['mtp', 'dflash2'] if dflash2_here() else ['mtp'],
        'models': None,
        'memory': None,
        'assume': {},
        'notes': '',
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + '\n')
    print(f'wrote {path.relative_to(ROOT)}; fill in "memory" (sudo dmidecode -t memory) and "gpu_power_limit_w" if you set one')


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'list'
    if cmd == 'detect':
        env_id, found, hw = detect()
        if not env_id:
            print(f'none ({hw.get("gpu")}, {hw.get("ram_gib")} GiB RAM; matching: {", ".join(found) or "none"})', file=sys.stderr)
            raise SystemExit(1)
        print(env_id)
    elif cmd == 'list':
        env_id, _, hw = detect()
        print(f'this hardware: {hw.get("gpu")}, {hw.get("ram_gib")} GiB RAM')
        for i in ids():
            print(f'{"*" if i == env_id else " "} {i:20} {label(load(i))}')
        if not ids():
            print(f'  (none yet: python3 -I scripts/envs.py new {slug(hw)})')
    elif cmd == 'new':
        new(sys.argv[2] if len(sys.argv) > 2 else slug(hardware()))
    elif cmd == 'run-dir':
        print(run_dir(current(), sys.argv[2], division(measuring=True)).relative_to(ROOT))
    elif cmd == 'divisions':
        for i in division_ids():
            d = load_division(i)
            print(f'{i:10} {d.get("status", "?"):8} {d.get("label", {}).get("ja", i)}')
    else:
        raise SystemExit(__doc__)


if __name__ == '__main__':
    main()
