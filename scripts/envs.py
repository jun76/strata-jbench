#!/usr/bin/env python3
"""Test environments: one per hardware set-up the benchmark runs on (a GPU and an amount of RAM on this PC, or another PC).

Each environment is a folder envs/<id>/ with env.json (see envs/README.md), written on the PC that measures it and kept
out of Git (its models and power limits are the measurer's choices); scripts/publish.py keeps a copy with every published
run (published/<division>/<id>/<run id>/env.json), and the pages read that copy. The results are also split by division
(divisions/<division>/division.json: how the models are driven, "plain" = the engine's API with no agent harness):
the plan of an environment is plan/<division>/<id>/, its results results/<division>/<id>/<run id>/ and its case list
cases/<division>/<id>/. Which environment a run belongs to is never typed by hand
in the middle of a measurement: it is the environment whose "match" fits the hardware found now (GPU name and RAM),
and the runner and preflight refuse to measure under an environment that does not match.

    python3 -I scripts/envs.py detect              # the id of the environment this hardware is (exit 1 if none)
    python3 -I scripts/envs.py list                # every environment, and which one matches now
    python3 -I scripts/envs.py new <id> [--gpu N]  # write envs/<id>/env.json from the hardware found now (card N, default 0)
    python3 -I scripts/envs.py run-dir <run id>    # results/<division>/<env>/<run id> for the detected environment
    python3 -I scripts/envs.py divisions           # every division and whether it is measured yet

The division is $BENCH_DIVISION, else bench.json "division" ("plain" by default: scripts/config.py); only a division whose division.json says "status": "active" can be
measured (the others are planned: their harness is not set up, or its adapter in scripts/harnesses.py has not been run yet).
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import config  # noqa: E402
ENVS = ROOT / 'envs'
DIVISIONS = ROOT / 'divisions'
RAM_TOLERANCE = 0.03      # MemTotal moves a little between kernels and firmware settings, not by a whole module


def ids():
    """The environments of this PC (envs/<id>/env.json): the ones it can measure."""
    return sorted(p.parent.name for p in ENVS.glob('*/env.json'))


def published_env(env_id, div=None):
    """The env.json kept with the environment's newest published run (as of UNTIL), or None."""
    for run in reversed(run_dirs(env_id, published_only=True, div=div)):
        if (run / 'env.json').exists():
            return run / 'env.json'
    return None


def page_ids(published_only=False, div=None):
    """The environments the pages show: those with a published run (their env.json kept with it) and, unless
    published_only, this PC's envs/ too."""
    found = {p.parent.parent.name for p in (PUBLISHED / division(div)).glob('*/*/env.json')}
    found = {e for e in found if published_env(e, div)}
    return sorted(found if published_only else found | set(ids()))


def load(env_id, published_only=False):
    """An environment's env.json: this PC's envs/<id>/env.json, else (and always with published_only, for the
    committed pages) the copy kept with its newest published run."""
    path = None if published_only else ENVS / env_id / 'env.json'
    if not path or not path.exists():
        path = published_env(env_id) or path
    if not path or not path.exists():
        raise SystemExit(f'no environment {env_id!r}: envs/{env_id}/env.json is missing (scripts/envs.py new {env_id})')
    cfg = json.loads(path.read_text())
    cfg['id'] = env_id
    cfg.setdefault('drafters', ['mtp'])
    cfg.setdefault('models', None)            # None: every model of the plan
    cfg.setdefault('gpu_power_limit_w', None) # None: the card's default, not checked
    cfg.setdefault('cpu_power_limit_w', None) # {'pl1': W, 'pl2': W}; None: the board's setting, not checked
    cfg.setdefault('assume', {})
    return cfg


def hardware():
    """The GPU and RAM found now (scripts/machine_info.py)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import machine_info
    return machine_info.collect()['env']


def gpu_index(cfg):
    """The card the environment measures on: env.json "gpu_index" (nvidia-smi's -i number; 0 when not set). On a PC with
    two cards each card is an environment of its own, and the runner launches on that card alone (--gpu)."""
    return int((cfg or {}).get('gpu_index') or 0)


def smi_card(env_id=None):
    """nvidia-smi's arguments for the environment's card: ['-i', N]."""
    try:
        return ['-i', str(gpu_index(load(env_id or current())))]
    except SystemExit:
        return ['-i', '0']


def matches(cfg, hw):
    m = cfg.get('match') or {}
    names = hw.get('gpus') or [hw.get('gpu')]
    i = gpu_index(cfg)
    if m.get('gpu') and (i >= len(names) or m['gpu'] != names[i]):
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
    """The environment to use: --env / $BENCH_ENV / bench.json "env" if given (it must match the hardware), else the
    detected one."""
    want = explicit or os.environ.get('BENCH_ENV') or config.get('env') or None
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
    """The division to use: --division / $BENCH_DIVISION if given, else bench.json "division" (default plain).
    measuring=True: it must be active."""
    div_id = explicit or os.environ.get('BENCH_DIVISION') or config.get('division') or 'plain'
    cfg = load_division(div_id)
    if measuring and cfg.get('status') != 'active':
        raise SystemExit(f'division {div_id!r} is {cfg.get("status")!r}, not measured yet (divisions/{div_id}/division.json)')
    return div_id


def plan_dir(env_id, div=None):
    return ROOT / 'plan' / division(div) / env_id


# Runs are measured into results/ (ignored by Git). A run that is final is moved to published/ (tracked) by
# scripts/publish.py. What is built from published/ alone is committed: the case lists (cases/, Markdown and CSV, read
# on GitHub) and, per published run, the charts as they were when it was published (snapshots/<division>/<env>/<run id>/,
# served by GitHub Pages). A build that also reads results/ writes to preview/ (ignored), so a running benchmark never
# touches a tracked file.
WORK = ROOT / 'results'
PUBLISHED = ROOT / 'published'
PREVIEW = ROOT / 'preview'
SNAPSHOTS = ROOT / 'snapshots'
# A snapshot's builds see only the published runs that finished by then (set by scripts/build_results.py --snapshot).
UNTIL = None


def finished(run):
    """When the run's queue last finished (ISO time from queue.log), or '' if it never did."""
    q = run / 'queue.log'
    ends = re.findall(r'^(\d{4}-\d\d-\d\dT\S+) queue finished', q.read_text(errors='replace'), re.M) if q.exists() else []
    return ends[-1] if ends else ''


def finished_ts(run):
    from datetime import datetime
    end = finished(run)
    return datetime.fromisoformat(end).timestamp() if end else 0


def snapshot_dir(env_id, run_id, div=None):
    """Where the charts as of a published run are kept (snapshots/<division>/<env>/<run id>/index.html)."""
    return SNAPSHOTS / division(div) / env_id / run_id


def tag(env_id, run_id, div=None):
    """The Git tag on the commit that published a run: the case lists as they were then."""
    return f'run/{division(div)}/{env_id}/{run_id}'


def github():
    """(repository URL, GitHub Pages URL) from the origin remote, or (None, None) when it is not on GitHub."""
    try:
        url = subprocess.run(['git', 'remote', 'get-url', 'origin'], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    except OSError:
        return None, None
    m = re.match(r'^(?:https://github\.com/|git@github\.com:)([^/]+)/(.+?)(?:\.git)?$', url)
    if not m:
        return None, None
    owner, repo = m.groups()
    return f'https://github.com/{owner}/{repo}', f'https://{owner.lower()}.github.io/{repo}'


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
    results/, test- runs left out. A run id in both is read from published/. With UNTIL set, only published runs that
    finished by then."""
    found = {}
    for root in ([WORK] if not published_only else []) + [PUBLISHED]:
        for d in (root / division(div) / env_id).glob('*/'):
            if d.is_dir() and not d.name.startswith('test-'):
                if UNTIL is not None and (root != PUBLISHED or not finished(d) or finished_ts(d) > UNTIL):
                    continue
                found[d.name] = d
    return [found[k] for k in sorted(found)]


def label(cfg):
    return cfg.get('label') or cfg['id']


def cpu_slug(name):
    """'Intel(R) Core(TM) Ultra 5 235' -> 'cu5_235', 'Intel(R) Core(TM) i7-14700' -> 'i7_14700',
    'AMD Ryzen 9 7950X 16-Core Processor' -> 'r9_7950x'. Joined with '_' so that '-' only separates the id's parts."""
    n = re.sub(r'\((R|TM)\)|\b(Intel|AMD|Processor|CPU)\b|\d+-Core', '', name or '').strip()
    m = re.match(r'Core Ultra (\d+) (\w+)', n)
    if m:
        return f'cu{m.group(1)}_{m.group(2)}'.lower()
    m = re.match(r'Core (i\d)-(\w+)', n)
    if m:
        return f'{m.group(1)}_{m.group(2)}'.lower()
    m = re.match(r'Ryzen (\d+)(?: PRO)? (\w+)', n)
    if m:
        return f'r{m.group(1)}_{m.group(2)}'.lower()
    return re.sub(r'[^a-z0-9]+', '_', n.lower()).strip('_') or 'cpu'


DISK_SLUG = {'NVMe': 'nvme', 'SATA SSD': 'sata', 'SATA HDD': 'hdd', 'SAS SSD': 'sas', 'SAS HDD': 'hdd', 'USB': 'usb'}


def slug(hw):
    """A suggested id, <GPU>-<CPU>-<RAM>-<model disk>: rtx5070-cu5_235-64g-sata. The id is the folder name in every path
    and URL (published/, snapshots/, the run tags), so it names what moves the results: the card, the CPU, the RAM and
    the bus of the disk the models are read from."""
    gpu = re.sub(r'^(NVIDIA )?(GeForce )?', '', hw.get('gpu') or 'gpu').lower().replace(' ', '')
    ram = -(-hw['ram_gib'] // 16) * 16 if hw.get('ram_gib') else 0
    disk = DISK_SLUG.get(hw.get('models_drive_bus') or '', 'disk')
    return f'{gpu}-{cpu_slug(hw.get("cpu"))}-{ram:.0f}g-{disk}'


def label_of(hw, ram):
    """'GeForce RTX 5070 · Core Ultra 5 235 · 64 GB RAM · SATA SSD'"""
    cpu = re.sub(r'\((R|TM)\)|\b(Intel|AMD|Processor)\b|\d+-Core', '', hw.get('cpu') or '?').split()
    return ' · '.join([re.sub(r'^NVIDIA ', '', hw.get('gpu') or '?'), ' '.join(cpu), f'{ram:.0f} GB RAM',
                       hw.get('models_drive_bus') or '?'])


# The reference model of an environment (Tier 0, Tier 4d, the representatives of Tiers 4b, 4c and 5, the harness
# divisions' "ref", the pages' "reference"): env.json "ref" ("family model"), else the model Strata itself recommends for
# that much RAM + VRAM. Strata's memory tiers are read from its source checkout's setup.py (MEMORY_TIERS, the floors in GB
# of RAM + VRAM less TIER_SYSTEM_RESERVE_GB); below the lowest tier its older rule picks Gyro-S.
STRATA_SOURCE = Path(os.environ.get('STRATA_SOURCE') or Path.home() / 'Strata')
REF_BELOW_TIERS = 'gyro Gyro-S'


def strata_tiers(source=None):
    """Strata's ((floor, family, model), ...) and its system reserve, from setup.py (parsed, not imported)."""
    import ast
    vals = {}
    for node in ast.parse(((source or STRATA_SOURCE) / 'setup.py').read_text()).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) \
                and node.targets[0].id in ('MEMORY_TIERS', 'TIER_SYSTEM_RESERVE_GB'):
            vals[node.targets[0].id] = ast.literal_eval(node.value)
    return vals['MEMORY_TIERS'], vals['TIER_SYSTEM_RESERVE_GB']


def ref_for(ram_gib, vram_gib):
    """"family model" Strata recommends for this RAM + VRAM, or None without its source checkout."""
    try:
        tiers, reserve = strata_tiers()
    except (OSError, KeyError, SyntaxError, ValueError):
        return None
    for floor, fam, model in tiers:
        if (ram_gib or 0) + (vram_gib or 0) - reserve >= floor:
            return f'{fam} {model}'
    return REF_BELOW_TIERS


def ref(cfg):
    """The environment's reference model as "family model": env.json "ref", else Strata's pick for its hardware. Whether
    the environment measures it is the plan's business (scripts/build_cases.py use_env)."""
    hw = cfg.get('hardware') or {}
    return cfg.get('ref') or ref_for(hw.get('ram_gib'), hw.get('gpu_vram_gib'))


def dflash2_here(card=0, model='qwen IQ3_S'):
    """Whether Auto drafting picks DFlash2 for a Qwen3.8 model on this card (strata launch --plan --gpu card)."""
    fam, name = model.split()
    try:
        out = subprocess.run(['strata', 'launch', '--plan', '--family', fam, '--model', name, '--context', '128k',
                              '--vision', 'off', '--parallel', '1', '--tune', 'skip', '--port', '18600', '--gpu', str(card),
                              '--output', 'json'],
                             capture_output=True, text=True, timeout=180, cwd='/tmp').stdout
        plan = json.loads(out[out.index('{'):])['plan']
        return 'dflash2' in json.dumps(plan.get('drafting', '')).lower()
    except (OSError, ValueError, KeyError, subprocess.SubprocessError):
        return False


def new(env_id, card=0):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import machine_info
    hw = machine_info.collect(gpu_index=card)['env']
    path = ENVS / env_id / 'env.json'
    if path.exists():
        raise SystemExit(f'{path} already exists')
    ram = -(-hw['ram_gib'] // 16) * 16
    vram = round((hw.get('gpu_vram_mib') or 0) / 1024, 1)
    pick = ref_for(hw.get('ram_gib'), vram)
    cfg = {
        'label': label_of(hw, ram),
        'match': {'gpu': hw.get('gpu'), 'ram_gib': hw.get('ram_gib')},
        'gpu_index': card,
        'hardware': {'gpu_vram_gib': vram, 'ram_gib': hw.get('ram_gib')},
        'gpu_power_limit_w': None,
        'cpu_power_limit_w': None,
        'drafters': ['mtp', 'dflash2'] if dflash2_here(card, pick or 'qwen IQ3_S') else ['mtp'],
        'ref': pick,
        'models': None,
        'memory': None,
        'assume': {},
        'notes': '',
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + '\n')
    print(f'wrote {path.relative_to(ROOT)}; fill in "memory" (sudo dmidecode -t memory), and "gpu_power_limit_w" / "cpu_power_limit_w" if you '
          'set them')


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
        card = int(sys.argv[sys.argv.index('--gpu') + 1]) if '--gpu' in sys.argv else 0
        rest = [x for i, x in enumerate(sys.argv[2:], 2) if x != '--gpu' and sys.argv[i - 1] != '--gpu']
        new(rest[0] if rest else slug(hardware()), card)
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
