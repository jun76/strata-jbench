"""Lifecycle and local model catalog for the plain-sync benchmark."""
import json
import os
import socket
import subprocess
from pathlib import Path

DIVISION = 'plain-sync'
PORT = 18600
INSTALL = Path.home() / 'sync-strata/.sync-local'
APP = INSTALL / 'SyncStrata/app'
CLI = APP / 'launcher/sync.sh'
MODELS = [
    ('sync', 'Sync-XS', 24.12, 'Sync-Strata'),
    ('sync', 'Sync-S', 28.14, 'Sync-Strata'),
    ('sync', 'Sync-M', 34.59, 'Sync-Strata'),
]


def enabled(division):
    return division == DIVISION


def read(path):
    return json.loads(path.read_text())


def installation():
    return read(INSTALL / 'SyncStrata/state/state.json')


def models_dir():
    return Path(read(INSTALL / 'sync-data/settings.json')['models_dir']).resolve()


def models(models_to_check):
    catalog = read(APP / 'chat/models/models.dist.json')
    root = models_dir()
    out = []
    for family, model in models_to_check:
        entry = next(e for e in catalog['models'] if e['id'] == model.lower())
        files = []
        for part in [entry, *catalog['shared']]:
            folder = root / part['local_dir']
            for item in part['files']:
                path = folder / item['path']
                if not path.is_file() or path.stat().st_size != item['bytes']:
                    files.append(str(path.relative_to(root)))
        out.append({'item': 'sync-model', 'what': model, 'state': 'missing' if files else 'ok',
                    'detail': ', '.join(files), 'fix': 'install the selected pack and shared files in Sync-Strata'})
    return out


def setup(home):
    home.mkdir(mode=0o700, parents=True, exist_ok=True)
    settings = {'models_dir': str(models_dir()), 'api_port': PORT, 'api_host': '127.0.0.1',
                'ram_squeeze': 'off', 'expert_learning': 'off'}
    (home / 'settings.json').write_text(json.dumps(settings) + '\n')


def child_env(home):
    return {**{k: v for k, v in os.environ.items() if not k.startswith(('SYNC_', 'STRATA_'))},
            'SYNC_HOME': str(home)}


def launch_args(model, context):
    return [str(CLI), 'up', '--api-only', '--json', '--port', str(PORT), '--model', model.lower(),
            '--context', str(context), '--kv', 'k8v4', '--tail-skip', '10', '--ram-squeeze', 'off']


def port_free():
    with socket.socket() as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(('127.0.0.1', PORT))
        except OSError:
            return False
        return True


def config_errors(config, model, context, gpu):
    args = config['args']
    flags = {arg: value for arg, value in zip(args, args[1:]) if arg.startswith('--')}
    expected = next(e for e in read(APP / 'chat/models/models.dist.json')['models'] if e['id'] == model.lower())
    checks = {
        'tail skip is off': config['env'].get('STRATA_ROUTE_TAIL_SKIP') == '0',
        'context': flags.get('--max-context') == str(context),
        'KV format': flags.get('--kv') == 'k8v4',
        'GPU': config.get('gpu') == gpu,
        'model pack': Path(flags.get('--pack', '')).name == Path(expected['local_dir']).name,
        'MTP configured': '--mtp' in flags,
    }
    return [name for name, ok in checks.items() if not ok]


def home_for(run_dir):
    owner = os.environ.get('BENCH_SYNC_OWNER')
    return (Path(owner) if owner else run_dir) / 'sync-home'


def stop(run_dir):
    home = home_for(run_dir)
    if not (home / 'run/procs.json').exists():
        return None
    # The packaged down command only stops the server PID before the API socket opens.
    # Stop the recorded tree during startup as well, using Sync's PID and start-time checks.
    code = 'import sync_home as h; h.stop_tree("engine"); raise SystemExit(int(h.alive("engine")))'
    return subprocess.run([str(APP / 'python/bin/python3'), '-s', '-c', code], cwd=CLI.parent,
                          env=child_env(home), capture_output=True, text=True, timeout=180)


def record(run_dir, roster):
    state = installation()
    catalog = read(APP / 'chat/models/models.dist.json')
    document = {'release': state['release'], 'components': state['components'],
                'models': [part for part in catalog['models'] if part['id'] in roster], 'shared': catalog['shared']}
    (run_dir / 'sync-models.json').write_text(json.dumps(document, ensure_ascii=False, indent=2) + '\n')


def compute_busy(gpu):
    result = subprocess.run(['nvidia-smi', '-i', str(gpu), '--query-compute-apps=pid',
                             '--format=csv,noheader,nounits'], capture_output=True, text=True, check=True)
    return bool(result.stdout.strip())


def worker_pid(server_pid):
    tasks = Path(f'/proc/{server_pid}/task')
    for children in tasks.glob('*/children'):
        try:
            pids = children.read_text().split()
        except FileNotFoundError:
            continue
        for pid in map(int, pids):
            try:
                executable = Path(os.readlink(f'/proc/{pid}/exe'))
            except FileNotFoundError:
                continue
            if executable.name == 'strata' and executable.is_relative_to(APP):
                return pid
    return 0
