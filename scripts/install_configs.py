#!/usr/bin/env python3
"""Write Strata's run config (install/strata-<tag>.json) for every model of the environment whose files are on disk.

`strata launch --plan` counts a model without a run config as a download, so preflight stops on it even though every file
is here (the downloads come from scripts/download_models.py, not from Strata's setup). For each such model, and for one whose
config was written for another card, this runs Strata's setup in install-only mode (`strata install ... --no-start`, the
setup.py `strata launch` runs itself), with the choices the runner launches with: --gpu <the environment's card>,
--vision no, --mtp on (setup keeps the MTP draft layer; AGENTS.md 5), --context 131072. Setup checks the files (by their
finish marks) and writes the config and the start script; it downloads nothing that is already on disk where it looks.
It is never left to fetch a model: a family Strata reads from its own models folder alone (envs.STRATA_FOLDER_ONLY) is
installed only when its files are there, and a setup that starts downloading a model file anyway is stopped and fails
(the 2026-11-22 Hy4-Flash run fetched SQ-64 and Engram twice, jbench's copy being in another folder).

It changes Strata's saved settings (the run configs), so it runs only with the user's agreement (AGENTS.md 3);
The run's supervisor (scripts/supervise.py) runs it once the run's models are on disk, before preflight.

    python3 -I scripts/install_configs.py [--env <id>] [--dry-run]
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import case_plan  # noqa: E402
import envs  # noqa: E402
import overnight  # noqa: E402
import own_build  # noqa: E402

INSTALL = Path.home() / '.local/share/strata/install'
HELPER_FAMILIES = ('qwen', 'swift', 'coder', 'unsloth', 'gyro')   # the families setup takes --mtp for (Strata's modelstate)


def config_path(fam, model):
    return own_build.config_path(fam, model)   # Strata's install folder, or jbench's for a build with files of its own


def plan_download_gb(fam, model, card):
    sfam, smodel = own_build.target(fam, model)
    out = subprocess.run(['strata', 'launch', '--plan', '--family', sfam, '--model', smodel, '--context', '128k',
                          '--vision', 'off', '--parallel', '1', '--tune', 'skip', '--port', '18600', '--drafting', 'mtp',
                          '--gpu', str(card), '--output', 'json', *own_build.launch_extra(fam, model)],
                         capture_output=True, text=True, timeout=180, cwd='/tmp').stdout
    try:
        return json.loads(out[out.index('{'):])['plan']['download']['gb']
    except (ValueError, KeyError):
        return None


def needs_install(fam, model, card):
    """Why the model needs setup run for it, or None."""
    try:
        cfg = json.loads(config_path(fam, model).read_text())
    except (OSError, ValueError):
        return 'no run config'
    if cfg.get('gpu') != card or cfg.get('gpus'):
        return f'run config for card {cfg.get("gpus") or cfg.get("gpu")}, not {card}'
    if fam in HELPER_FAMILIES and cfg.get('mtp') is False:
        return 'run config has the MTP draft layer off'
    mine = own_build.pinned_file(fam, model)
    if mine and str(mine) not in cfg.get('args', []):   # Strata keeps an older file of the build where it has one
        return f'run config does not name {mine.name}'
    gb = plan_download_gb(fam, model, card)
    if gb:
        return f'launch --plan would download {gb} GB'
    return None


PROGRESS = re.compile(r'\d+\.\d+ / (\d+\.\d+) GB \(\d+%\)')   # setup's download progress ("0.02 / 62.03 GB (0%)")
MODEL_FILE_GB = 0.1   # a download this large is a model file; a smaller one (a chat template, a tokenizer) is let through


def outside_strata_folder(fam, model):
    """Files of the model that are not in the folder Strata reads the family from (only for envs.STRATA_FOLDER_ONLY)."""
    if fam not in envs.STRATA_FOLDER_ONLY:
        return []
    root, want = overnight.models_root(), (envs.strata_models_dir() / fam).resolve()
    return [f['path'] for f in overnight.manifest()['files'] if f['family'] == fam and f['model'] == model
            and (root / f['path']).resolve().parent != want]


def run_install(args):
    """Run setup; stop it (rc -1) as soon as it shows a model download. Returns (rc, output)."""
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd='/tmp')
    out = b''
    while chunk := p.stdout.read1(65536):
        out += chunk
        if any(float(m.group(1)) >= MODEL_FILE_GB for m in PROGRESS.finditer(out[-4096:].decode(errors='replace'))):
            p.terminate()
            try:
                p.wait(30)
            except subprocess.TimeoutExpired:
                p.kill()
            text = out.decode(errors='replace').replace('\r', '\n')
            return -1, text + '\nstopped: setup started downloading a model file that jbench has on disk'
    return p.wait(), out.decode(errors='replace').replace('\r', '\n')


def install_args(fam, model, card):
    sfam, smodel = own_build.target(fam, model)
    args = ['strata', 'install', '--family', sfam, '--model', smodel, '--yes', '--no-start', '--context', '131072',
            '--vision', 'no', '--gpu', str(card)]
    if own_build.custom(fam, model):   # as strata launch passes one of its custom builds to setup
        args += ['--gguf-dir', str(own_build.pinned_file(fam, model)), '--custom-label', model]
    if fam in HELPER_FAMILIES:
        args += ['--mtp', 'on']
    if fam in ('qwen', 'coder'):
        args += ['--experimental-speed-projection', 'off']   # as strata launch passes it
    return args


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--env', default='', help='the environment (default: the one this hardware matches)')
    ap.add_argument('--dry-run', action='store_true', help='say what would be installed, change nothing')
    a = ap.parse_args()
    env_id = envs.current(a.env)
    cfg = envs.load(env_id)
    card = envs.gpu_index(cfg)
    case_plan.use_env(cfg)
    failed = []
    for fam, model, *_ in case_plan.env_models():
        if own_build.own(fam, model):   # its run config is jbench's own (scripts/own_build.py prepare), not setup's
            print(f'{fam} {model}: {own_build.state(fam, model) or "run config ok (jbench\'s own)"}', flush=True)
            continue
        if own_build.pinned(fam, model):   # one file the catalog pins: not in the downloads' manifest
            missing = own_build.pinned_state(fam, model)
            if missing:
                print(f'{fam} {model}: {missing}; skipped', flush=True)
                continue
        elif not overnight.model_complete(fam, model):
            print(f'{fam} {model}: files not all on disk yet; skipped', flush=True)
            continue
        why = needs_install(fam, model, card)
        if not why:
            print(f'{fam} {model}: run config ok', flush=True)
            continue
        args = install_args(fam, model, card)
        away = [] if own_build.pinned(fam, model) else outside_strata_folder(fam, model)
        if away:
            failed.append(f'{fam} {model}')
            print(f'{fam} {model}: {why}, but not installed: Strata reads {fam} only from '
                  f'{envs.strata_models_dir() / fam} and would fetch {", ".join(away)} again', flush=True)
            continue
        print(f'{fam} {model}: {why}; {" ".join(args)}', flush=True)
        if a.dry_run:
            continue
        rc, out = run_install(args)
        tail = '\n'.join(l for l in out.strip().splitlines() if not PROGRESS.search(l))
        tail = '\n'.join(tail.splitlines()[-6:])
        left = needs_install(fam, model, card) if rc == 0 else None
        if rc != 0 or left:
            failed.append(f'{fam} {model}')
            print(f'{fam} {model}: FAILED (rc {rc}{", " + left if left else ""})\n{tail}', flush=True)
        else:
            print(f'{fam} {model}: installed', flush=True)
    if failed:
        print(f'install_configs: failed for {", ".join(failed)}', flush=True)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
