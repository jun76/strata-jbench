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

A build with "pinned" is one file the catalog itself pins (repo, revision, file, bytes, sha256), for a model whose
engine reads one file and needs no pack (Inkling-2-Mini). Three kinds, by what else the record says:

    "pinned": {...}                      a build Strata lists under the same name (GSQ-RCO-IQ3_S): the file is in
                                         Strata's own folder for the family, with its finish mark
    "pinned": {"as": "SQ-20", ...}       a build Strata lists under another name (SQ-20-v2: Strata 0.2.23 calls the new
                                         file SQ-20 as it called the old one); launched and installed under Strata's name
    "pinned": {"custom": {"base": "GSQ-RCO-IQ3_S", "group": "<provision models group>"}, ...}
                                         a file Strata does not list, run as one of Strata's custom builds (0.2.23 on):
                                         every launch names it (--model-path FILE --custom-label <model>) with the
                                         settings of "base"; Strata writes a run config of its own for it
                                         (strata-<family>-custom-<slug>.json) and never copies the file

For all three the runner checks that the engine was started on the pinned file.
"""
import json
import os
import re
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


def pinned(fam, model):
    """The build's "pinned" record (one file the catalog pins), or None."""
    for base in catalog.load():
        for e in base['builds']:
            if (e['family'], e['model']) == (fam, model):
                return e.get('pinned')
    return None


def custom(fam, model):
    """The "custom" part of a pinned build Strata does not list ({"base", "group"}), or None."""
    return (pinned(fam, model) or {}).get('custom')


def slug(text):
    """Strata's slug of a custom build's name (strata_control/custom_models.py)."""
    return re.sub(r'-{2,}', '-', re.sub(r'[^a-z0-9]+', '-', str(text).lower())).strip('-')[:40] or 'build'


def target(fam, model):
    """(family, model) as Strata knows it."""
    o = own(fam, model)
    if o:
        return tuple(o['as'])
    p = pinned(fam, model) or {}
    return fam, p.get('as') or (p.get('custom') or {}).get('base') or model


def tag(fam, model):
    if custom(fam, model):
        return f'{fam}-custom-{slug(model)}'
    fam, model = target(fam, model)
    return model.lower() if fam == 'qwen' else f'{fam}-{model.lower()}'


def pinned_file(fam, model):
    """Where a pinned build's file is: Strata's own folder for the family, or for a custom build the folder recorded
    for its group (tools/provision.json). None when no folder is recorded."""
    p = pinned(fam, model)
    if not p:
        return None
    if p.get('custom'):
        where = provision.models(p['custom']['group']).get('path')
        return Path(where) / p['file'] if where else None
    import envs
    return envs.strata_models_dir() / fam / p['file']


def pinned_state(fam, model):
    """None when a pinned build's file is on disk as pinned, else what is missing. The SHA-256 is checked when the
    file is fetched (its finish mark, <file>.done, holds it); here the size and the mark."""
    p, f = pinned(fam, model), pinned_file(fam, model)
    fetch = f'hf download {p["repo"]} {p["file"]} --revision {p["revision"]} --local-dir DIR'
    if not f:
        return f'no folder recorded for it: {fetch}, then python3 -I scripts/provision.py set-models {p["custom"]["group"]} --path DIR'
    if not f.is_file():
        return f'{f} is missing ({fetch}; check its SHA-256 {p["sha256"]} and write "sha256 <hash>" into {f.name}.done)'
    if f.stat().st_size != p['bytes']:
        return f'{f} has {f.stat().st_size} bytes, the pin {p["bytes"]}'
    mark = f.with_name(f.name + '.done')
    if not mark.is_file() or mark.read_text().split()[-1:] != [p['sha256']]:
        return f'{mark} does not say sha256 {p["sha256"]} (sha256sum {f})'
    return None


def expected_file(fam, model):
    """The file the engine has to be started on, for a build with files of jbench's own or a pinned one; else None."""
    return model_file(fam, model) if own(fam, model) else pinned_file(fam, model)


def install_dir(fam, model):
    o = own(fam, model)
    return INSTALLS / o['install'] if o else STRATA_INSTALL


def config_path(fam, model):
    return install_dir(fam, model) / f'strata-{tag(fam, model)}.json'


def env(fam, model):
    """The environment a strata command about this build runs in (None: as it is)."""
    return dict(os.environ, STRATA_INSTALL_DIR=str(install_dir(fam, model))) if own(fam, model) else None


def launch_extra(fam, model):
    """What a strata launch of this build adds: --model-path, the file to use where it is, and --data-dir, the build's
    data folder (its pack and the link to the drafter). A launch that runs Strata's setup (any context but the one the
    run config was written for) otherwise takes the known model's file: on 2026-11-26 it fetched Gyro-S (58.5 GB) into
    the build's data folder and started that. With --model-path alone the pack is built again in a folder Strata
    derives from the file's path, where no drafter is."""
    if custom(fam, model):   # one of Strata's custom builds: the file where it is, under the build's name
        f = pinned_file(fam, model)
        return ['--model-path', str(f), '--custom-label', model] if f else []
    f = model_file(fam, model) if own(fam, model) else None
    return ['--model-path', str(f), '--data-dir', str(data_dir(fam, model))] if f else []


STRATA_SETTINGS = Path.home() / '.config/strata/settings.json'


def saved_data_dir():
    """Strata's saved data folder ("data_dir" in ~/.config/strata/settings.json), or None when it has none."""
    try:
        return json.loads(STRATA_SETTINGS.read_text()).get('data_dir')
    except (OSError, ValueError):
        return None


def restore_data_dir(before):
    """Put Strata's saved data folder back to what it was before a launch with --data-dir: strata launch saves the
    folder it is given as the default for the next start and for the app (it passes setup --set-default-data-dir
    whenever --data-dir is there), so after a Gyro-S v2 launch Strata's own downloads went to the build's data folder
    and Hy4-Flash and Inkling-2-Mini were looked for there (2026-11-27). Only "data_dir" is written, and only when
    the launch changed it. Returns the folder the launch had saved, or None when nothing was changed."""
    try:
        doc = json.loads(STRATA_SETTINGS.read_text())
    except (OSError, ValueError):
        return None
    now = doc.get('data_dir')
    if now == before:
        return None
    if before is None:
        doc.pop('data_dir', None)
    else:
        doc['data_dir'] = before
    tmp = STRATA_SETTINGS.with_name(STRATA_SETTINGS.name + '.jbench-tmp')
    tmp.write_text(json.dumps(doc, indent=1))
    tmp.replace(STRATA_SETTINGS)
    return now


def before_launch(fam, model):
    """A launch that runs Strata's setup rewrites the run config it starts from. With --model-path and --data-dir it
    writes this build's paths again; should the config name another file all the same, it is written again here."""
    if own(fam, model) and state(fam, model) and not state_files(fam, model):
        prepare(fam, model, quiet=True)


def state_files(fam, model):
    """What is missing of the build's files (the model file, the pack), or None."""
    f = model_file(fam, model)
    if not f or not f.is_file():
        return state(fam, model)
    return None if (pack_dir(fam, model) / 'native_experts.txt').is_file() else 'no pack'


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


def prepare(fam, model, quiet=False):
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
    # the drafters are the model's, not the build's: links to Strata's, or a launch that runs setup with --data-dir
    # fetches them again (the MTP draft layer, 5.2 GB, at the 1M launch of test-gyro-v2-ctx2)
    shared = [Path(old_pack).parent.parent / 'dflash2']
    if '--mtp' in args:
        shared.append(Path(args[args.index('--mtp') + 1]).parent)
    for src in shared:
        link = data_dir(fam, model) / src.name
        if src.is_dir() and not link.exists():
            link.symlink_to(src)
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
    if not quiet:
        print(f'{fam} {model}: {conf.relative_to(ROOT)} (file {f}, pack {pack})')


def main():
    if sys.argv[1:2] == ['prepare'] and len(sys.argv) == 4:
        return prepare(sys.argv[2], sys.argv[3])
    for fam, model in builds():
        o = own(fam, model)
        print(f'{fam} {model}: started as {" ".join(o["as"])} from tools/strata-install/{o["install"]}/: {state(fam, model) or "ok"}')
    for fam, model, *_ in catalog.builds():
        if pinned(fam, model):
            how = 'a custom build' if custom(fam, model) else 'Strata\'s ' + target(fam, model)[1]
            print(f'{fam} {model}: pinned file, started as {how}: {pinned_state(fam, model) or "ok"} ({pinned_file(fam, model)})')


if __name__ == '__main__':
    main()
