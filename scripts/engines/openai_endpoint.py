"""Attach only: an OpenAI-compatible endpoint the user started (bench.json "engine_url").

For a derived engine that has no adapter yet. jbench starts and stops nothing, so one run measures the one model that
is loaded, at the context it was started with, and nothing about the launch is checked: the engine's name, version and
how it was started are what the user says in bench.json "engine_note", kept as said. The results carry
"managed": false and are marked "attach only" wherever they are shown.

A row's family and model are what the user says is loaded (bench.json "models" names exactly one).
"""
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engines import Engine  # noqa: E402


class Adapter(Engine):
    def __init__(self, info, **ctx):
        super().__init__(info, **ctx)
        self.url = (ctx.get('engine_url') or '').rstrip('/')
        if self.url:
            u = urlparse(self.url if '//' in self.url else 'http://' + self.url)
            self.host, self.port = u.hostname or self.host, u.port or 80
        self.note = ctx.get('engine_note') or ''
        if self.track == 'exact' and not ctx.get('dry'):
            # nothing can be confirmed about an engine jbench did not start
            self.track = 'custom'

    def models(self):
        with urllib.request.urlopen(f'http://{self.host}:{self.port}/v1/models', timeout=10) as r:
            return [m['id'] for m in json.loads(r.read()).get('data', [])]

    def probe(self):
        if not self.url:
            return {'ok': False, 'reason': 'bench.json "engine_url" is not set (e.g. "http://127.0.0.1:8080")'}
        try:
            found = self.models()
        except (OSError, ValueError, urllib.error.URLError) as e:
            return {'ok': False, 'where': self.url, 'reason': f'{self.url}/v1/models does not answer: {e}'}
        return {'ok': bool(found), 'where': self.url, 'version': None, 'served_models': found, 'declared': self.note,
                'provision': 'user', 'reason': '' if found else 'the endpoint lists no model'}

    def start(self, row, session_dir):
        p = self.probe()
        info = {'backend': self.id, 'argv': [], 'rc': 0 if p['ok'] else 1, 'launch_s': 0.0, 'attached': self.url,
                'declared': self.note}
        (session_dir / 'launch.txt').write_text(f'attached to {self.url} (not started by jbench)\n\n{self.note}\n\n'
                                                + json.dumps(p, ensure_ascii=False, indent=2) + '\n')
        if not p['ok']:
            info['error'] = p['reason']
            return info
        self.api_model = p['served_models'][0]
        info['api_model'] = self.api_model
        return info
