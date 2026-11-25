"""Engines: what the runner measures, behind one small interface.

catalog/engines/<id>.json names an engine (Strata itself, a derived engine, or just an OpenAI-compatible URL) and the
adapter that drives it; an adapter is one module here with a class `Adapter(Engine)`. The runner knows no engine by
name: it asks the adapter to start a model, to say what it could not confirm, to hand over its log, to stop, and to
record what was measured (versions, files). bench.json "engine" picks one (default strata), "track" how it is set:

  exact    every approximation that changes the output is off (the engine's entry says which: Sync-Strata's tail skip)
  default  the engine as it comes
  custom   anything else (attach only: whatever the user started)

Three kinds of adapters:
  strata_cli       managed: `strata launch`, the choices checked against the engine's own command line
  sync_cli         managed: Sync-Strata's `sync up --api-only`, checked against its resolved config
  openai_endpoint  attach only: a URL the user started; nothing about the launch can be checked
"""
import importlib
import json
import socket
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / 'catalog' / 'engines'
TOOLS = ROOT / 'tools' / 'engines'          # engines jbench fetched for itself (not in Git; docs/001 3.5)
DEFAULT = 'strata'
TRACKS = ('exact', 'default', 'custom')
KEYS = {'id', 'order', 'label', 'source', 'adapter', 'managed', 'steps', 'max_context', 'tracks', 'approximations',
        'pin', 'about'}


def entries():
    out = []
    for path in sorted(CATALOG.glob('*.json')):
        try:
            out.append(json.loads(path.read_text()))
        except ValueError as e:
            raise SystemExit(f'catalog/engines/{path.name} is not valid JSON: {e}')
    return sorted(out, key=lambda e: (e.get('order', 0), e.get('id', '')))


def ids():
    return [e['id'] for e in entries()]


def entry(engine_id):
    for e in entries():
        if e['id'] == engine_id:
            return e
    raise SystemExit(f'no engine {engine_id!r} in catalog/engines/ (there: {", ".join(ids())})')


def problems():
    out = []
    for e in entries():
        name = e.get('id', '?')
        for k in sorted({'id', 'label', 'adapter', 'managed', 'steps', 'tracks', 'about'} - set(e)):
            out.append(f'engine {name}: no "{k}"')
        for k in sorted(set(e) - KEYS):
            out.append(f'engine {name}: unknown key "{k}"')
        if not (Path(__file__).parent / f'{e.get("adapter")}.py').exists():
            out.append(f'engine {name}: no adapter scripts/engines/{e.get("adapter")}.py')
        for t in e.get('tracks', {}):
            if t not in TRACKS:
                out.append(f'engine {name}: track {t!r} is not one of {", ".join(TRACKS)}')
    return out


def of_run(run_dir):
    """(engine id, track) a run measured: its engine.json; a run from before engines were recorded is Strata, exact."""
    try:
        e = json.loads((Path(run_dir) / 'engine.json').read_text())
        return e.get('id', DEFAULT), e.get('track', 'exact')
    except (OSError, ValueError):
        return DEFAULT, 'exact'


def now():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds')


class Engine:
    """What an adapter is. ctx: host, port, gpu (card index), launch_timeout (s), run_dir, p_cores, track, and the
    settings an adapter reads from bench.json (engine_url, engine_note, engine_path)."""
    api_model = 'strata'    # the "model" the requests name (an engine with one model loaded takes any)

    def __init__(self, info, **ctx):
        self.info = info
        self.id = info['id']
        self.ctx = ctx
        self.host, self.port, self.gpu = ctx.get('host', '127.0.0.1'), ctx.get('port', 18600), ctx.get('gpu', 0)
        self.track = ctx.get('track') or 'exact'
        if self.track not in info['tracks']:
            raise SystemExit(f'engine {self.id} has no track {self.track!r} (it has: {", ".join(info["tracks"])})')
        self.run_dir = ctx.get('run_dir')

    # --- what a run needs before it starts
    def probe(self):
        """{'ok': bool, 'version': ..., 'where': ..., 'reason': ...}: is the engine here, and which one."""
        raise NotImplementedError

    def needs(self, models):
        """What is missing for these (family, model) pairs: acquire.py items ({'item', 'what', 'state', 'detail', 'fix'})."""
        return []

    def preflight(self, models):
        """[(what was checked, ok, detail)], without starting anything heavy."""
        p = self.probe()
        return [(f'engine {self.id}: {p.get("version") or "?"} at {p.get("where") or "?"}', p['ok'], p.get('reason', ''))]

    # --- a session: one model started once
    def start(self, row, session_dir):
        """Start the row's model with its context and launch options; block until it answers. Returns the session's
        record: argv, rc, and 'error' when it did not start."""
        raise NotImplementedError

    def verify(self, row, info, session_dir):
        """After the engine answered: what was asked for and cannot be confirmed. Sets info['error'] (and the keys the
        runner names failures by: mtp_missing, setting_missing) and returns False to give the session up."""
        return True

    def after_launch(self, row, info, session_dir):
        """Whatever the launch leaves to keep (Strata: the presets a tune launch saved). Returns a log line or None."""
        return None

    def pid(self):
        """The process whose RSS and disk reads the telemetry follows, or None."""
        return None

    def collect_log(self, info, session_dir):
        """Write this start's part of the engine's log to session_dir/engine.log."""

    def stop(self, session_dir=None):
        """Stop what this adapter started, nothing else."""

    # --- the run's record
    def record(self, run_dir, rows):
        """Write engine.json (and whatever says which files were measured) into the run. Returns a line for the log."""
        doc = {'id': self.id, 'label': self.info['label'], 'adapter': self.info['adapter'], 'managed': self.info['managed'],
               'track': self.track, 'track_settings': self.info['tracks'].get(self.track, {}),
               'source': self.info.get('source'), 'pin': self.info.get('pin'), **self.describe(rows), 'recorded_at': now()}
        text = json.dumps(doc, ensure_ascii=False, indent=2).replace(str(Path.home()), '~')
        (Path(run_dir) / 'engine.json').write_text(text + '\n')
        return f'engine.json: {self.id} {doc.get("version") or ""} track {self.track}'.replace('  ', ' ')

    def describe(self, rows):
        return self.probe()

    # --- helpers
    def port_free(self):
        with socket.socket() as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind((self.host, self.port))
            except OSError:
                return False
        return True

    def gpu_compute_busy(self):
        """The compute processes on the card that hold 1 GB of VRAM or more, as "pid name MiB" lines ('' when none). A
        desktop's own (the compositor, a browser's GPU process) are listed as compute processes too and hold far
        less; an inference engine left running holds more."""
        r = subprocess.run(['nvidia-smi', '-i', str(self.gpu), '--query-compute-apps=pid,process_name,used_memory',
                            '--format=csv,noheader,nounits'], capture_output=True, text=True)
        busy = []
        for line in r.stdout.splitlines():
            parts = [x.strip() for x in line.split(',')]
            if len(parts) >= 3 and parts[-1].isdigit() and int(parts[-1]) >= 1000:
                busy.append(f'{parts[0]} {parts[1].split()[0]} {parts[-1]} MiB')
        return '; '.join(busy)


def get(engine_id=None, **ctx):
    info = entry(engine_id or DEFAULT)
    mod = importlib.import_module(f'engines.{info["adapter"]}')
    return mod.Adapter(info, **ctx)
