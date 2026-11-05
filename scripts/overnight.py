"""Unattended acquisition: finish the downloads, prepare NVFP4-QAD, then fetch Q8_0.

Runs detached. Each phase is skipped when its result is already on disk, so the
script can be started again at any point. Progress goes to downloads/overnight.log
and downloads/overnight-state.json; downloads/READY appears when every model is here.

  1. download everything except Q8_0, restarting the downloader when it stalls
  2. tools/nvfp4_local_pack.py prepare on NVIDIA's FP4-Local checkpoint (as setup runs it)
  3. delete the checkpoint's *.safetensors once every prepare step is marked done
  4. download Q8_0 (same watchdog)
"Everything" is downloads/manifest.json: the environment's models (env.json "models"); steps 2-4 are skipped when it
does not list NVFP4-QAD or Q8_0.
"""
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_DIR = ROOT / 'downloads'
LOG = STATE_DIR / 'overnight.log'
# The prepare tool expects llama.cpp at <root>/third_party, which neither Strata's source nor the app has, so it runs
# from a copy of the source's tools beside a link to the install's llama.cpp (work/qad-root). scripts/setup_acquire.py
# makes it and both venvs.
QAD_ROOT = ROOT / 'work/qad-root'
GGUF_PY = Path.home() / '.local/share/strata/install/third_party/llama.cpp/gguf-py'
QAD_PYTHON = ROOT / '.venv-qad/bin/python'
DL_PYTHON = ROOT / '.venv-hf/bin/python'
STALL_S = 8 * 60          # no growth on disk and no change of file for this long: restart the downloader
MAX_RESTARTS = 30


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def log(msg):
    with LOG.open('a') as f:
        f.write(f'{now()} {msg}\n')


def set_state(**kw):
    path = STATE_DIR / 'overnight-state.json'
    state = json.loads(path.read_text()) if path.exists() else {}
    state.update(kw, updated_at=now())
    path.write_text(json.dumps(state, indent=2) + '\n')


def manifest():
    return json.loads((STATE_DIR / 'manifest.json').read_text())


def models_root():
    return Path(manifest()['models_root'])


def model_complete(family, model):
    """Every file of the model is on disk with its .done mark (the downloader's verified state)."""
    root = models_root()
    files = [f for f in manifest()['files'] if f['family'] == family and f['model'] == model]
    return bool(files) and all((root / f['path']).is_file() and (root / (f['path'] + '.done')).is_file()
                               for f in files)


def stop(proc):
    for sig, wait in [(signal.SIGINT, 60), (signal.SIGTERM, 30), (signal.SIGKILL, 10)]:
        if proc.poll() is not None:
            return
        proc.send_signal(sig)
        try:
            proc.wait(wait)
        except subprocess.TimeoutExpired:
            continue


def download(extra_args, done_check, label):
    """Run the downloader until done_check() holds, restarting it when it stalls or exits early."""
    restarts = 0
    while not done_check():
        if restarts > MAX_RESTARTS:
            log(f'{label}: giving up after {restarts} restarts')
            set_state(phase=label, error='too many restarts')
            return False
        out = (STATE_DIR / 'download.log').open('a')
        proc = subprocess.Popen([str(DL_PYTHON), '-u', 'scripts/download_models.py', 'run', *extra_args],
                                cwd=ROOT, stdout=out, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
        (STATE_DIR / 'pid').write_text(f'{proc.pid}\n')
        log(f'{label}: downloader started pid {proc.pid} args {extra_args}')
        set_state(phase=label, downloader_pid=proc.pid, restarts=restarts)
        last_used, last_current, last_change = -1, None, time.time()
        while proc.poll() is None:
            time.sleep(30)
            used = shutil.disk_usage(models_root()).used
            try:
                current = json.loads((STATE_DIR / 'status.json').read_text()).get('current')
            except (OSError, ValueError):
                current = last_current
            if abs(used - last_used) > 50_000_000 or current != last_current:
                last_used, last_current, last_change = used, current, time.time()
            elif time.time() - last_change > STALL_S:
                log(f'{label}: no progress for {STALL_S}s on {current}; restarting')
                stop(proc)
                break
        out.close()
        if proc.poll() is None:
            stop(proc)
        restarts += 1
        try:
            st = json.loads((STATE_DIR / 'status.json').read_text())
            log(f'{label}: downloader ended rc={proc.returncode} state={st.get("state")}')
            if st.get('state') == 'paused_low_disk':
                log(f'{label}: paused for low disk; stopping here')
                set_state(phase=label, error='paused_low_disk')
                return False
        except (OSError, ValueError):
            pass
        time.sleep(10)
    log(f'{label}: complete')
    return True


def qad_paths():
    root = models_root()
    ck = root / 'nvidia--Qwen3.8-Flash-Next-FP4-Local'
    return ck, ck / 'prepared'


def qad_prepared():
    _, out = qad_paths()
    return all((out / m).is_file() for m in ('ple-nvfp4.gguf.done', 'dense.gguf.done', 'pack.done', 'draft.done'))


def prepare_qad():
    if qad_prepared():
        log('qad: already prepared')
        return True
    ck, out = qad_paths()
    if not model_complete('nvfp4', 'NVFP4-QAD'):
        log('qad: checkpoint incomplete; not preparing')
        return False
    free = shutil.disk_usage(ck).free
    if free < 115e9:
        log(f'qad: only {free / 1e9:.0f} GB free, need ~110 GB; not preparing')
        set_state(phase='qad', error='low disk')
        return False
    env = dict(os.environ, STRATA_GGUF_PY=str(GGUF_PY))
    log(f'qad: prepare {ck} -> {out}')
    set_state(phase='qad')
    t0 = time.time()
    with (STATE_DIR / 'qad-prepare.log').open('a') as f:
        rc = subprocess.call([str(QAD_PYTHON), str(QAD_ROOT / 'tools/nvfp4_local_pack.py'), 'prepare',
                              '--model', str(ck), '--out', str(out)],
                             cwd=QAD_ROOT, env=env, stdout=f, stderr=subprocess.STDOUT)
    log(f'qad: prepare rc={rc} in {time.time() - t0:.0f}s, prepared={qad_prepared()}')
    return rc == 0 and qad_prepared()


def drop_qad_checkpoint():
    """setup: once prepared, the checkpoint's tensors are no longer read and can be deleted (re-fetchable by SHA)."""
    if not qad_prepared():
        return
    ck, _ = qad_paths()
    freed = 0
    for p in sorted(ck.glob('*.safetensors')):
        freed += p.stat().st_size
        p.unlink()
        mark = p.with_name(p.name + '.done')
        if mark.exists():
            mark.unlink()
    if freed:
        log(f'qad: deleted checkpoint tensors, {freed / 1e9:.1f} GB freed (SHA-256 kept in downloads/manifest.json)')


def main():
    log(f'start pid {os.getpid()}')
    set_state(pid=os.getpid(), started_at=now(), phase='start', error=None)
    # downloads/manifest.json lists the environment's models (scripts/setup_acquire.py); Q8_0 and NVFP4-QAD may not be there
    listed = list(dict.fromkeys((f['family'], f['model']) for f in manifest()['files']))
    others = [c for c in listed if c != ('unsloth', 'Q8_0')]
    has_q8, has_qad = ('unsloth', 'Q8_0') in listed, ('nvfp4', 'NVFP4-QAD') in listed

    def others_done():
        return all(model_complete(fam, m) or (m == 'NVFP4-QAD' and qad_prepared()) for fam, m in others)

    if not download(['--exclude', 'unsloth:Q8_0'] if has_q8 else [], others_done, 'download'):
        return 1
    if has_qad:
        if not qad_prepared() and not prepare_qad():
            set_state(phase='qad', error='prepare failed')
            return 1
        drop_qad_checkpoint()
    if has_q8:
        # The QAD checkpoint is gone on purpose by now; keep the downloader from fetching it again.
        if not download(['--exclude', 'nvfp4:NVFP4-QAD'] if has_qad else [], lambda: model_complete('unsloth', 'Q8_0'),
                        'download-q8'):
            return 1
    (STATE_DIR / 'READY').write_text(now() + '\n')
    set_state(phase='done')
    log('all models ready')
    return 0


if __name__ == '__main__':
    sys.exit(main())
