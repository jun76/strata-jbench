#!/usr/bin/env python3
"""Make what the acquisition phase (scripts/overnight.py) runs with, on a fresh clone or after a Strata update.

Every step is skipped when its result is already there, so it can run before every start (scripts/start_pipeline.sh
runs it while downloads/READY is missing). It writes only inside the repository (Git-ignored) and installs pinned
packages from PyPI and the PyTorch index; nothing in Strata's own folders is changed.

  1. .venv-hf      the downloader's Python: Strata's bundled Python + scripts/requirements-acquire.txt
  2. downloads/manifest.json   every file to fetch, pinned by Strata's setup.py (scripts/download_models.py prepare)
  3. .venv-qad     the NVFP4-QAD converter's Python: Strata's requirements.txt + requirements-nvfp4-local.txt
                   (torch, transformers, safetensors; the CPU build of torch on Linux, as Strata's setup installs it)
  4. work/qad-root the Strata source's tools beside the install's llama.cpp: tools/nvfp4_convert.py imports llama.cpp
                   from <its own root>/third_party/llama.cpp, which neither the source checkout nor the app has
                   (setup writes it to ~/.local/share/strata/install/third_party), so the tools are copied (not
                   linked: they find their root through their resolved path) into a root whose third_party is a link.
Steps 3 and 4 are skipped once NVFP4-QAD is prepared.

The source is a checkout of Strata's source (default ~/Strata); the downloads are pinned by its setup.py, and the
commit is kept in downloads/manifest.json.

    python3 -I scripts/setup_acquire.py [--source ~/Strata]
    python3 -I scripts/setup_acquire.py --rebuild      make the venvs and work/qad-root again
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import overnight  # noqa: E402  (the paths the acquisition runs with)

STRATA = Path.home() / '.local/share/strata'
INSTALL_THIRD_PARTY = STRATA / 'install/third_party'
TORCH_CPU_INDEX = 'https://download.pytorch.org/whl/cpu'


def say(msg):
    print(f'setup_acquire: {msg}', flush=True)


def bundled_python():
    """The Python that ships with the active Strata Control (the one setup.py runs with); else this Python."""
    try:
        active = json.loads((STRATA / 'components/control/active.json').read_text())['folder']
        exe = STRATA / 'components/control' / active / 'python/bin/python3.12'
        if exe.is_file():
            return exe
    except (OSError, ValueError, KeyError):
        pass
    return Path(sys.executable)


def venv_ok(venv, probe):
    py = venv / 'bin/python'
    return py.is_file() and subprocess.run([str(py), '-c', probe], capture_output=True).returncode == 0


def make_venv(venv, requirements, probe, rebuild, extra=()):
    if not rebuild and venv_ok(venv, probe):
        return
    if venv.exists():
        shutil.rmtree(venv)
    base = bundled_python()
    say(f'{venv.name}: creating with {base}')
    subprocess.run([str(base), '-m', 'venv', str(venv)], check=True)
    args = [str(venv / 'bin/python'), '-m', 'pip', 'install', '--disable-pip-version-check', '-q', *extra]
    for r in requirements:
        args += ['-r', str(r)]
    subprocess.run(args, check=True)
    if not venv_ok(venv, probe):
        sys.exit(f'setup_acquire: {venv.name} was made but `{probe}` still fails')


def check_source(source):
    need = ['setup.py', 'tools/nvfp4_local_pack.py', 'requirements.txt', 'requirements-nvfp4-local.txt']
    missing = [n for n in need if not (source / n).exists()]
    if missing:
        sys.exit(f'setup_acquire: {source} is not a Strata source checkout (missing {", ".join(missing)}); '
                 'clone Strata\'s source there, or pass --source')


def make_qad_root(source, rebuild):
    root = overnight.QAD_ROOT
    llama = INSTALL_THIRD_PARTY / 'llama.cpp'
    if not (llama / 'convert_hf_to_gguf.py').is_file():
        sys.exit(f'setup_acquire: {llama} is missing; it is written by Strata\'s setup the first time a model is '
                 'installed (install any model with Strata once, then run this again)')
    if root.exists() and not rebuild and (root / 'tools/nvfp4_local_pack.py').is_file():
        return
    if root.exists():
        shutil.rmtree(root)
    say(f'{root}: tools from {source}, third_party -> {INSTALL_THIRD_PARTY}')
    root.mkdir(parents=True)
    for entry in source.iterdir():
        if entry.name in ('tools', 'third_party', '.git', '__pycache__'):
            continue
        (root / entry.name).symlink_to(entry)
    shutil.copytree(source / 'tools', root / 'tools', ignore=shutil.ignore_patterns('__pycache__'))
    (root / 'third_party').symlink_to(INSTALL_THIRD_PARTY)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--source', type=Path, default=Path.home() / 'Strata', help="Strata's source checkout")
    ap.add_argument('--rebuild', action='store_true', help='make the venvs and work/qad-root again')
    a = ap.parse_args()
    source = a.source.expanduser().resolve()
    check_source(source)

    make_venv(overnight.DL_PYTHON.parents[1], [ROOT / 'scripts/requirements-acquire.txt'],
              'import huggingface_hub', a.rebuild)
    if not (overnight.STATE_DIR / 'manifest.json').exists():
        say('downloads/manifest.json: writing the pinned file list')
        subprocess.run([str(overnight.DL_PYTHON), 'scripts/download_models.py', 'prepare', '--source', str(source)],
                       cwd=ROOT, check=True)
    if (overnight.STATE_DIR / 'manifest.json').exists() and overnight.qad_prepared():
        say('NVFP4-QAD is prepared; no converter needed')
        return 0
    make_venv(overnight.QAD_PYTHON.parents[1],
              [source / 'requirements.txt', source / 'requirements-nvfp4-local.txt'],
              'import torch, transformers, safetensors, numpy', a.rebuild,
              extra=['--extra-index-url', TORCH_CPU_INDEX])
    make_qad_root(source, a.rebuild)
    say('ready')
    return 0


if __name__ == '__main__':
    sys.exit(main())
