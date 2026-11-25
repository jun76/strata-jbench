"""Sync-Strata (github.com/hiruhiru2005/sync-strata), driven by its launcher: `sync.sh up --api-only --json`.

A fork of Strata with its own quantizations (Sync-XS / S / M), its own launcher and its own settings folder. The
launcher resolves a config (written under SYNC_HOME, one per run: the user's own Sync-Strata settings are neither read
nor changed) and starts the fork's engine; this adapter checks that config against what was asked.

Where it is: bench.json "engine_path", else tools/provision.json, else tools/engines/sync-strata/<pinned version>/
(the folder holding SyncStrata/app/launcher/sync.sh). The models folder: tools/provision.json "models_dir", else the
install's own sync-data/settings.json.

Tracks: exact = tail skip R10 (no expert skipped; checked in the resolved config and in the worker's environment);
default = the launcher's own pick (R4 or R7 by the PC), recorded per session.
"""
import json
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import provision  # noqa: E402
from engines import TOOLS, Engine  # noqa: E402

KV = 'k8v4'


def read(path):
    return json.loads(Path(path).read_text())


class Adapter(Engine):
    def __init__(self, info, **ctx):
        super().__init__(info, **ctx)
        known = provision.engine(self.id)
        root = ctx.get('engine_path') or known.get('path') or TOOLS / self.id / info['pin']['version']
        self.root = Path(root).expanduser()
        self._models_dir = known.get('models_dir')

    # --- where things are
    @property
    def app(self):
        for cand in (self.root / 'SyncStrata/app', self.root / 'app', self.root):
            if (cand / 'launcher/sync.sh').is_file():
                return cand
        return self.root / 'SyncStrata/app'

    @property
    def cli(self):
        return self.app / 'launcher/sync.sh'

    def models_dir(self):
        if self._models_dir:
            return Path(self._models_dir).expanduser().resolve()
        for cand in (self.root / 'sync-data/settings.json', self.app.parent.parent / 'sync-data/settings.json'):
            if cand.is_file():
                return Path(read(cand)['models_dir']).resolve()
        raise OSError(f'no models folder known for {self.id}: tools/provision.json "models_dir" or {self.root}/sync-data/settings.json')

    def models_catalog(self):
        return read(self.app / 'chat/models/models.dist.json')

    def installation(self):
        for cand in (self.app.parent / 'state/state.json', self.root / 'SyncStrata/state/state.json'):
            if cand.is_file():
                return read(cand)
        return {}

    def home(self):
        """SYNC_HOME of this run (the supervisor's children share its run folder)."""
        owner = os.environ.get('BENCH_ENGINE_HOME')
        return (Path(owner) if owner else Path(self.run_dir)) / 'sync-home'

    def child_env(self):
        return {**{k: v for k, v in os.environ.items() if not k.startswith(('SYNC_', 'STRATA_'))},
                'SYNC_HOME': str(self.home())}

    # --- fetching it for jbench alone (scripts/acquire.py fetch engine:sync-strata; never without the user's yes)
    def fetch_plan(self, models_dir):
        a = self.info['pin']['archive']
        root = TOOLS / self.id / self.info['pin']['version']
        return {'what': f'{self.info["label"]} {self.info["pin"]["version"]} ({a["name"]})', 'url': a['url'],
                'bytes': a['bytes'], 'sha256': a['sha256'], 'into': str(root),
                'then': ' '.join(x.format(root=root, models_dir=models_dir) for x in self.info['pin']['setup'])}

    def fetch(self, models_dir, say=print):
        """Download the pinned release, check its SHA-256, unpack it and run its own installer into tools/engines/
        (no shortcuts, its own settings folder, no model download). Returns the provision record."""
        import hashlib
        import urllib.request
        import zipfile
        pin, a = self.info['pin'], self.info['pin']['archive']
        root = TOOLS / self.id / pin['version']
        dist = root / 'dist'
        dist.mkdir(parents=True, exist_ok=True)
        zpath = root / a['name']
        if not zpath.exists() or zpath.stat().st_size != a['bytes']:
            say(f'downloading {a["url"]} ({a["bytes"] / 1e9:.2f} GB)')
            urllib.request.urlretrieve(a['url'], zpath)
        h = hashlib.sha256()
        with zpath.open('rb') as f:
            while chunk := f.read(1 << 24):
                h.update(chunk)
        if h.hexdigest() != a['sha256']:
            raise SystemExit(f'{zpath}: SHA-256 {h.hexdigest()} is not the pinned {a["sha256"]}; nothing was run')
        say('SHA-256 matches the pin; unpacking')
        with zipfile.ZipFile(zpath) as z:
            for m in z.infolist():
                out = z.extract(m, dist)
                mode = m.external_attr >> 16
                if mode:
                    os.chmod(out, mode & 0o777)
        setup = next(iter(sorted(dist.rglob('setup.sh'), key=lambda q: len(q.parts))), None)
        if not setup:
            raise SystemExit(f'no setup.sh in {a["name"]}')
        args = [x.format(root=root, models_dir=models_dir) for x in pin['setup']]
        say('running ' + shlex.join(args) + f' (in {setup.parent})')
        r = subprocess.run(['bash'] + args, cwd=setup.parent, env=self.child_env_for(root / 'sync-home'))
        if r.returncode:
            raise SystemExit(f'the installer exited {r.returncode}')
        self.root = root
        return provision.put('engines', self.id, path=str(root), models_dir=str(models_dir), version=pin['version'],
                             source=a['url'], sha256=a['sha256'], by='jbench')

    @staticmethod
    def child_env_for(home):
        return {**{k: v for k, v in os.environ.items() if not k.startswith(('SYNC_', 'STRATA_'))}, 'SYNC_HOME': str(home)}

    # --- before a run
    def probe(self):
        if not self.cli.is_file():
            return {'ok': False, 'where': str(self.root), 'reason': f'{self.cli} is missing (the engine is not fetched: '
                    f'python3 -I scripts/acquire.py check)'}
        state = self.installation()
        comp = state.get('components', {})
        return {'ok': True, 'version': state.get('release') or self.info['pin']['version'], 'where': str(self.root),
                'engine_build': comp.get('engine', {}).get('version'), 'components': comp,
                'provision': provision.engine(self.id).get('by', 'user')}

    def needs(self, models):
        out = []
        p = self.probe()
        if not p['ok']:
            pin = self.info['pin']
            return [{'item': f'engine:{self.id}', 'what': f'{self.info["label"]} {pin["version"]}', 'state': 'missing',
                     'detail': p['reason'], 'fix': f'fetch it into tools/engines/{self.id}/{pin["version"]}/ '
                     f'({pin["release"]}) or name where it is: bench.json "engine_path"'}]
        try:
            catalog, root = self.models_catalog(), self.models_dir()
        except (OSError, ValueError, KeyError) as e:
            return [{'item': 'sync-model', 'what': 'Sync-Strata models folder', 'state': 'unknown', 'detail': str(e), 'fix': ''}]
        for _, model in models:
            entry = next((e for e in catalog['models'] if e['id'] == model.lower()), None)
            if not entry:
                out.append({'item': 'sync-model', 'what': model, 'state': 'unknown',
                            'detail': 'not in this Sync-Strata\'s models.dist.json', 'fix': ''})
                continue
            missing = []
            for part in [entry, *[s for s in catalog['shared'] if not s.get('optional')]]:
                for f in part['files']:
                    path = root / part['local_dir'] / f['path']
                    if not path.is_file() or path.stat().st_size != f['bytes']:
                        missing.append(str(path.relative_to(root)))
            out.append({'item': 'sync-model', 'what': f'sync {model}', 'state': 'missing' if missing else 'ok',
                        'detail': ', '.join(missing[:6]) + (f' (+{len(missing) - 6})' if len(missing) > 6 else ''),
                        'fix': f'the pack and the shared files into {root} (hf download, the revisions of models.dist.json)'})
        return out

    def preflight(self, models):
        out = super().preflight(models)
        if not out[0][1]:
            return out
        out.append((f'{self.id}: port {self.port} is free', self.port_free(), ''))
        busy = self.gpu_compute_busy()
        out.append((f'{self.id}: no other process holds 1 GB or more on GPU {self.gpu}', not busy, busy))
        for item in self.needs(models):
            out.append((f'{self.id}: {item["what"]} on disk', item['state'] == 'ok', item['detail']))
        return out

    # --- a session
    def setup_home(self):
        home = self.home()
        home.mkdir(mode=0o700, parents=True, exist_ok=True)
        settings = {'models_dir': str(self.models_dir()), 'api_port': self.port, 'api_host': self.host,
                    'ram_squeeze': 'off', 'expert_learning': 'off'}
        (home / 'settings.json').write_text(json.dumps(settings) + '\n')

    def launch_args(self, row):
        args = [str(self.cli), 'up', '--api-only', '--json', '--port', str(self.port), '--model', row['model'].lower(),
                '--context', str(row['context']), '--kv', KV, '--ram-squeeze', 'off']
        if self.track == 'exact':
            args += ['--tail-skip', '10']
        return args + shlex.split(row.get('launch_opts') or '')

    def config_errors(self, config, model, context):
        args = config['args']
        flags = {a: v for a, v in zip(args, args[1:]) if a.startswith('--')}
        expected = next(e for e in self.models_catalog()['models'] if e['id'] == model.lower())
        checks = {
            'context': flags.get('--max-context') == str(context),
            'KV format': flags.get('--kv') == KV,
            'GPU': config.get('gpu') == self.gpu,
            'model pack': Path(flags.get('--pack', '')).name == Path(expected['local_dir']).name,
            'MTP configured': '--mtp' in flags,
        }
        if self.track == 'exact':
            checks['tail skip is off'] = config['env'].get('STRATA_ROUTE_TAIL_SKIP') == '0'
        return [name for name, ok in checks.items() if not ok]

    def worker_pid(self, server_pid):
        for children in Path(f'/proc/{server_pid}/task').glob('*/children'):
            try:
                pids = children.read_text().split()
            except OSError:
                continue
            for pid in map(int, pids):
                try:
                    exe = Path(os.readlink(f'/proc/{pid}/exe'))
                except OSError:
                    continue
                if exe.name == 'strata' and exe.is_relative_to(self.app):
                    return pid
        return 0

    def start(self, row, session_dir):
        args = self.launch_args(row)
        info = {'backend': self.id, 'argv': args, 'rc': 1, 'track': self.track}
        t0 = time.monotonic()
        stdout = stderr = ''
        try:
            if not self.port_free() or self.gpu_compute_busy():
                raise ValueError('benchmark port in use, or another process holds 1 GB or more of the GPU')
            self.setup_home()
            proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=self.child_env())
            try:
                stdout, stderr = proc.communicate(timeout=self.ctx.get('launch_timeout', 3 * 3600))
            except subprocess.TimeoutExpired:
                proc.kill()
                stdout, stderr = proc.communicate()
                info['rc'] = None
                raise ValueError('launch timed out') from None
            info['rc'] = proc.returncode
            if proc.returncode:
                raise ValueError(f'the launcher exited {proc.returncode}: {stderr[-450:]}')
            result = json.loads(stdout)
            if not result['ok'] or result['pick']['model'] != row['model'].lower():
                raise ValueError('the launcher did not start the requested model')
            info['tail_skip'] = f'R{result["pick"]["r"]}'
            if self.track == 'exact' and result['pick']['r'] != 10:
                raise ValueError(f'track exact asks for tail skip R10, the launcher picked R{result["pick"]["r"]}')
            owned = read(self.home() / 'run/procs.json')['engine']
            if owned['port'] != self.port or result['settings']['api_port'] != self.port:
                raise ValueError('the launcher moved away from the benchmark port')
            started = read(self.home() / 'run/cfg/started.json')
            cfg = read(started['config'])
            (session_dir / 'sync-config.json').write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + '\n')
            info.update(engine_log=started['log'], engine_log_offset=started['log_offset'], server_pid=owned['pid'],
                        api_model=cfg['model_name'], gpu=self.gpu, requested_context=row['context'],
                        requested_model=row['model'])
            self.api_model = cfg['model_name']
        except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as e:
            info['error'] = str(e)
        (session_dir / 'launch.txt').write_text(shlex.join(args) + '\n\n' + stderr + stdout)
        info['launch_s'] = round(time.monotonic() - t0, 1)
        if 'error' in info:
            self.stop()
        return info

    def verify(self, row, info, session_dir):
        try:
            cfg = read(session_dir / 'sync-config.json')
            missing = self.config_errors(cfg, row['model'], row['context'])
            if missing:
                info['setting_missing'] = missing
                raise ValueError('settings not applied: ' + ', '.join(missing))
            text = Path(info['engine_log']).read_bytes()[info['engine_log_offset']:].decode(errors='replace')
            if 'draft layer loaded' not in text:
                info['mtp_missing'] = True
                raise ValueError('the MTP draft layer was not loaded')
            pid = self.worker_pid(info['server_pid'])
            if not pid:
                raise ValueError('no engine process under the launcher\'s recorded server PID')
            info['engine_pid'] = pid
            if self.track == 'exact' and b'STRATA_ROUTE_TAIL_SKIP=0' not in Path(f'/proc/{pid}/environ').read_bytes().split(b'\0'):
                info['setting_missing'] = ['tail skip is off']
                raise ValueError('the engine process did not receive STRATA_ROUTE_TAIL_SKIP=0')
            info['settings_verified'] = True
        except (OSError, ValueError, KeyError) as e:
            info['error'] = str(e)
            return False
        return True

    def pid(self):
        try:
            return self.worker_pid(read(self.home() / 'run/procs.json')['engine']['pid']) or None
        except (OSError, ValueError, KeyError):
            return None

    def collect_log(self, info, session_dir):
        if info.get('engine_log'):
            (session_dir / 'engine.log').write_bytes(Path(info['engine_log']).read_bytes()[info['engine_log_offset']:])

    def stop(self, session_dir=None):
        if not (self.home() / 'run/procs.json').exists():
            return
        # The packaged down command only stops the server PID before the API socket opens. Stop the recorded tree during
        # startup as well, with the launcher's own PID and start-time checks.
        code = 'import sync_home as h; h.stop_tree("engine"); raise SystemExit(int(h.alive("engine")))'
        r = subprocess.run([str(self.app / 'python/bin/python3'), '-s', '-c', code], cwd=self.cli.parent,
                           env=self.child_env(), capture_output=True, text=True, timeout=180)
        if session_dir:
            (session_dir / 'stop.txt').write_text(r.stdout + r.stderr)
        if r.returncode:
            raise RuntimeError(f'{self.id}: the engine could not be stopped: {r.stderr[-300:]}')

    # --- the run's record
    def describe(self, rows):
        doc = self.probe()
        try:
            catalog = self.models_catalog()
            roster = {r['model'].lower() for r in rows}
            doc['models'] = [p for p in catalog['models'] if p['id'] in roster]
            doc['shared'] = catalog['shared']
        except (OSError, ValueError, KeyError):
            pass
        return doc
