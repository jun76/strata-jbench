#!/usr/bin/env python3
"""Write Strata's run config (install/strata-<tag>.json) for every model of the environment whose files are on disk.

`strata launch --plan` counts a model without a run config as a download, so preflight stops on it even though every file
is here (the downloads come from scripts/download_models.py, not from Strata's setup). For each such model, and for one whose
config was written for another card, this runs Strata's setup in install-only mode (`strata install ... --no-start`, the
setup.py `strata launch` runs itself), with the choices the runner launches with: --gpu <the environment's card>,
--vision no, --mtp on (setup keeps the MTP draft layer; AGENTS.md 5), --context 131072. Setup checks the files (by their
finish marks) and writes the config and the start script; it downloads nothing that is already on disk.

It changes Strata's saved settings (the run configs), so it runs only with the user's agreement (AGENTS.md 3);
scripts/overnight_bench.sh runs it after downloads/READY, before preflight.

    python3 -I scripts/install_configs.py [--env <id>] [--dry-run]
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_cases  # noqa: E402
import envs  # noqa: E402
import overnight  # noqa: E402

INSTALL = Path.home() / '.local/share/strata/install'
HELPER_FAMILIES = ('qwen', 'swift', 'coder', 'unsloth', 'gyro')   # the families setup takes --mtp for (Strata's modelstate)


def config_path(fam, model):
    return INSTALL / f'strata-{model.lower() if fam == "qwen" else f"{fam}-{model.lower()}"}.json'


def plan_download_gb(fam, model, card):
    out = subprocess.run(['strata', 'launch', '--plan', '--family', fam, '--model', model, '--context', '128k',
                          '--vision', 'off', '--parallel', '1', '--tune', 'skip', '--port', '18600', '--drafting', 'mtp',
                          '--gpu', str(card), '--output', 'json'], capture_output=True, text=True, timeout=180,
                         cwd='/tmp').stdout
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
    gb = plan_download_gb(fam, model, card)
    if gb:
        return f'launch --plan would download {gb} GB'
    return None


def install_args(fam, model, card):
    args = ['strata', 'install', '--family', fam, '--model', model, '--yes', '--no-start', '--context', '131072',
            '--vision', 'no', '--gpu', str(card)]
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
    build_cases.use_env(cfg)
    failed = []
    for fam, model, *_ in build_cases.env_models():
        if not overnight.model_complete(fam, model):
            print(f'{fam} {model}: files not all on disk yet; skipped', flush=True)
            continue
        why = needs_install(fam, model, card)
        if not why:
            print(f'{fam} {model}: run config ok', flush=True)
            continue
        args = install_args(fam, model, card)
        print(f'{fam} {model}: {why}; {" ".join(args)}', flush=True)
        if a.dry_run:
            continue
        r = subprocess.run(args, capture_output=True, text=True, cwd='/tmp', timeout=7200)
        tail = '\n'.join((r.stdout + r.stderr).strip().splitlines()[-6:])
        left = needs_install(fam, model, card) if r.returncode == 0 else None
        if r.returncode != 0 or left:
            failed.append(f'{fam} {model}')
            print(f'{fam} {model}: FAILED (rc {r.returncode}{", " + left if left else ""})\n{tail}', flush=True)
        else:
            print(f'{fam} {model}: installed', flush=True)
    if failed:
        print(f'install_configs: failed for {", ".join(failed)}', flush=True)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
