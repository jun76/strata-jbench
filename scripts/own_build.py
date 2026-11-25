"""Builds jbench keeps the files of itself: a model file Strata's setup does not list (catalog/models/, "own").

Strata starts a model from its run config (install/strata-<tag>.json). A build with "own" in the catalog is another
file of a model Strata knows (Gyro-S v2: the same name, size and tensor types as Gyro-S, other expert weights), so
Strata is told to start the model it knows ("as") with STRATA_INSTALL_DIR pointing at a folder of jbench's own
(tools/strata-install/<install>/, not in Git) whose run config names jbench's file and a pack built from it. Strata's
saved run configs and the files of the model it knows are never touched, and both can be measured side by side.

    "own": {"as": ["gyro", "Gyro-S"], "install": "gyro-s-v2", "repo": "...", "revision": "...", "file": "...", "sha256": "..."}

    python3 -I scripts/own_build.py                          # every such build and its state on this PC
    python3 -I scripts/own_build.py prepare gyro Gyro-S-v2   # the pack and the run config (the file is fetched first:
                                                             # hf download, then provision.py set-models <install>)

prepare needs the run config Strata wrote for the model it knows ("as": installed on this PC) and writes nothing
outside the folder of the file and tools/strata-install/. After each launch the runner checks that the engine's
command line names jbench's file: a launch that ran Strata's setup would write the known model's paths back.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import catalog  # noqa: E402
import provision  # noqa: E402

INSTALLS = ROOT / 'tools' / 'strata-install'
STRATA_INSTALL = Path.home() / '.local/share/strata/install'
CONTROL = Path.home() / '.local/share/strata/components/control'


def own(fam, model):
    """The build's "own" record, or None for a build Strata's setup lists."""
    for base in catalog.load():
        for e in base['builds']:
            if (e['family'], e['model']) == (fam, model):
                return e.get('own')
    return None


def builds():
    return [(f, m) for f, m, *_ in catalog.builds() if own(f, m)]


def target(fam, model):
    """(family, model) as Strata knows it."""
    o = own(fam, model)
    return tuple(o['as']) if o else (fam, model)


def tag(fam, model):
    fam, model = target(fam, model)
    return model.lower() if fam == 'qwen' else f'{fam}-{model.lower()}'


def install_dir(fam, model):
    o = own(fam, model)
    return INSTALLS / o['install'] if o else STRATA_INSTALL


def config_path(fam, model):
    return install_dir(fam, model) / f'strata-{tag(fam, model)}.json'


def env(fam, model):
    """The environment a strata command about this build runs in (None: as it is)."""
    return dict(os.environ, STRATA_INSTALL_DIR=str(install_dir(fam, model))) if own(fam, model) else None


def model_file(fam, model):
    o = own(fam, model)
    where = provision.models(o['install']).get('path')
    return Path(where) / o['file'] if where else None


def data_dir(fam, model):
    """The folder Strata takes for the build's data folder: it reads the drafter from <pack>/../../dflash2, so the
    pack is kept as Strata keeps its own (<data>/packs/<tag>) and dflash2 there is a link to Strata's."""
    f = model_file(fam, model)
    return f.parent.parent / (f.parent.name + '-data') if f else None


def pack_dir(fam, model):
    d = data_dir(fam, model)
    return d / 'packs' / tag(fam, model) if d else None


def state(fam, model):
    """None when the build can be launched, else what is missing."""
    f = model_file(fam, model)
    if not f:
        o = own(fam, model)
        return (f'no folder recorded for it: hf download {o["repo"]} {o["file"]} --revision {o["revision"]} --local-dir DIR, '
                f'then python3 -I scripts/provision.py set-models {o["install"]} --path DIR')
    if not f.is_file():
        return f'{f} is missing'
    conf = config_path(fam, model)
    if not conf.is_file() or not (pack_dir(fam, model) / 'native_experts.txt').is_file():
        return f'not prepared: python3 -I scripts/own_build.py prepare {fam} {model}'
    if str(f) not in conf.read_text():
        return f'{conf} does not name {f}: python3 -I scripts/own_build.py prepare {fam} {model}'
    return None


def control():
    """Strata's active Control folder (its Python and tools/iq_pack.py)."""
    return CONTROL / json.loads((CONTROL / 'active.json').read_text())['folder']


def prepare(fam, model):
    o = own(fam, model)
    if not o:
        raise SystemExit(f'{fam} {model} is not a build with "own" in the catalog')
    f = model_file(fam, model)
    if not f or not f.is_file():
        raise SystemExit(state(fam, model))
    known = STRATA_INSTALL / f'strata-{tag(fam, model)}.json'
    if not known.is_file():
        raise SystemExit(f'{known} is missing: Strata has to have {" ".join(o["as"])} installed (its run config is the pattern)')
    cfg = json.loads(known.read_text())
    args = cfg['args']
    old_file, old_pack = args[args.index('--native') + 1], args[args.index('--pack') + 1]
    pack, ctl = pack_dir(fam, model), control()
    pack.parent.mkdir(parents=True, exist_ok=True)
    shared = Path(old_pack).parent.parent / 'dflash2'      # the DFlash2 drafter is the model's, not the build's
    link = data_dir(fam, model) / 'dflash2'
    if shared.is_dir() and not link.exists():
        link.symlink_to(shared)
    if not (pack / 'native_experts.txt').is_file():
        pack_args = ['--compat-bf16'] if '--compat-bf16' in (o.get('pack_args') or ['--compat-bf16']) else []
        r = subprocess.run([str(ctl / 'python/bin/python3.12'), str(ctl / 'tools/iq_pack.py'), '--gguf', str(f), '--out', str(pack),
                            *pack_args], cwd='/tmp')
        if r.returncode:
            raise SystemExit(f'iq_pack.py exited {r.returncode}')

    def sub(x):
        if isinstance(x, str):
            x = x.replace(old_file, str(f)).replace(old_pack, str(pack))
            for part in Path(x).parts:      # a run config written by an older Control names that Control's folder
                if x.startswith(str(CONTROL)) and part != ctl.name and (CONTROL / part).parent == CONTROL and part[0].isdigit():
                    x = x.replace(f'/control/{part}', f'/control/{ctl.name}')
            return x
        if isinstance(x, list):
            return [sub(i) for i in x]
        if isinstance(x, dict):
            return {k: sub(v) for k, v in x.items()}
        return x
    cfg = sub(cfg)
    conf = config_path(fam, model)
    conf.parent.mkdir(parents=True, exist_ok=True)
    cfg['log'] = str(conf.with_suffix('.log'))
    conf.write_text(json.dumps(cfg, indent=1) + '\n')
    provision.put('models', o['install'], pack=str(pack), install=str(conf.parent), prepared_with=f'Control {ctl.name} tools/iq_pack.py')
    print(f'{fam} {model}: {conf.relative_to(ROOT)} (file {f}, pack {pack})')


def main():
    if sys.argv[1:2] == ['prepare'] and len(sys.argv) == 4:
        return prepare(sys.argv[2], sys.argv[3])
    for fam, model in builds():
        o = own(fam, model)
        print(f'{fam} {model}: started as {" ".join(o["as"])} from tools/strata-install/{o["install"]}/: {state(fam, model) or "ok"}')


if __name__ == '__main__':
    main()
