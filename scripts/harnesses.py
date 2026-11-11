"""The agent harnesses the harness divisions drive (divisions/<division>/division.json "harness" and "pin").

Per harness: where its pinned version is (find), how to install that version into jbench's own folder (install:
npm --prefix, a venv for a pip pin, or the Strata app's AppImage checked against its SHA-256 and extracted),
its configuration in a folder of its own pointed at the recording proxy (prepare: never the user's ~/.dsh, ~/.pi,
~/.config/opencode or ~/.hermes), the one-shot command (argv) and how to read its output (parse). The command runs
inside bubblewrap (sandboxed): the whole file system read-only except the case's work folder and the harness's own
folder, so the tools the model calls (shell, file writes) need no approval and cannot write elsewhere.

Where a harness is looked for, in this order (only the pinned version is used):
  1. tools/harness/<division>/<version>/   installed by jbench (scripts/acquire.py fetch; Git-ignored)
  2. the harness's own default place       on PATH (npm's global prefix, ~/.local/bin), if its version is the pinned one

`tested` says whether the adapter has been run against a server (the mock engine counts): an untested adapter's division
stays "planned" in its division.json.
"""
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / 'tools' / 'harness'
WINDOW = 131072                 # the engine's context (plain's baseline, 128K)
OUTPUT = 32768                  # the output the harness plans for (its compaction reserve); the proxy pins the case's cap
MODEL = 'strata'                # the model id the harnesses send (the engine serves one model whatever the name)


def load_pin(div):
    return json.loads((ROOT / 'divisions' / div / 'division.json').read_text()).get('pin') or {}


def npm_version(bin_path, package):
    """The version of the npm package that owns this executable (its package.json up the resolved path), else None."""
    p = Path(os.path.realpath(bin_path))
    for d in [p.parent, *p.parents]:
        f = d / 'package.json'
        if f.is_file():
            try:
                j = json.loads(f.read_text())
            except ValueError:
                continue
            if j.get('name') == package:
                return j.get('version')
    return None


def cmd_version(bin_path):
    try:
        r = subprocess.run([str(bin_path), '--version'], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return (r.stdout + r.stderr).strip()


MARK = 'jbench-pin.json'        # written into tools/harness/<division>/<version>/ when jbench installed it there


def marked(root, pin):
    """The pin a jbench install recorded, if it is this pin (same source)."""
    try:
        m = json.loads((root / MARK).read_text())
    except (OSError, ValueError):
        return False
    return m.get('source') == pin.get('source') and m.get('version') == pin.get('version')


def venv_home(root):
    """The Python folder a venv was made from (pyvenv.cfg "home")."""
    try:
        return next(l.split('=', 1)[1].strip() for l in (root / 'pyvenv.cfg').read_text().splitlines() if l.startswith('home'))
    except (OSError, StopIteration):
        return 'unknown'


def find(div):
    """{'ok', 'bin', 'version', 'where', 'reason'} for the division's pinned harness."""
    pin = load_pin(div)
    how, ver, name = pin.get('how'), pin.get('version'), pin.get('bin')
    root = TOOLS / div / str(ver)
    if how == 'appimage':
        # the Strata desktop app, extracted: its bundled harness and the host code that writes the app's profile
        harness = root / 'squashfs-root' / (pin.get('harness_dir') or '')
        if marked(root, pin) and (harness / 'lib/bin.js').exists():
            return {'ok': True, 'bin': str(harness / 'lib/bin.js'), 'version': ver, 'where': 'jbench', 'reason': ''}
        return {'ok': False, 'bin': None, 'version': None, 'where': None,
                'reason': f'not installed (pinned {pin.get("name")} {ver}, extracted into {root.relative_to(ROOT)}/)'}
    mine = root / ('node_modules/.bin' if how == 'npm' else 'bin') / name
    if how == 'pip' and mine.exists() and not (root / 'bin/python').exists():
        # the venv's Python is gone: Strata's bundled one goes with its Control folder, which an update removes
        return {'ok': False, 'bin': None, 'version': None, 'where': None,
                'reason': f'the venv in {root.relative_to(ROOT)}/ lost its Python ({venv_home(root)}); installing again rebuilds it'}
    if mine.exists():
        if how == 'npm' and npm_version(mine, pin['package']) == ver or how == 'pip' and marked(root, pin):
            return {'ok': True, 'bin': str(mine), 'version': ver, 'where': 'jbench', 'reason': ''}
    other = shutil.which(name)
    if other:
        if how == 'npm':
            have = npm_version(other, pin['package'])
            ok = have == ver
        else:   # a version line has to name the pinned release (Hermes: "v0.21.5"; the tag 2026.9.24 is the same)
            out = cmd_version(other) or ''
            have = out.splitlines()[0][:80] if out else None
            ok = any(v and v in out for v in (ver, pin.get('version_text')))
        if ok:
            return {'ok': True, 'bin': other, 'version': ver, 'where': 'default', 'reason': ''}
        return {'ok': False, 'bin': other, 'version': have, 'where': 'default',
                'reason': f'{other} is {have}, not the pinned {ver} (left as it is; install {ver} into {root.relative_to(ROOT)}/)'}
    return {'ok': False, 'bin': None, 'version': None, 'where': None, 'reason': f'not installed (pinned {ver})'}


def install_note(div):
    """What installing the pin fetches, in a line (for the question asked before it), or None when jbench cannot."""
    pin = load_pin(div)
    how = pin.get('how')
    if how == 'npm':
        return f'npm {pin["package"]}@{pin["version"]} from npmjs.com'
    if how == 'pip':
        return f'{pin["source"]} (a git checkout) and its pinned Python dependencies from PyPI, into a venv'
    if how == 'appimage':
        return f'{pin["url"]} (checked against its SHA-256), extracted'
    return None


def python_for(spec):
    """A Python for a pip pin's requires-python ("3.11-3.13"): python3.13 .. 3.11 on PATH, else Strata's bundled one."""
    lo, hi = (int(x.split('.')[1]) for x in spec.split('-'))
    for minor in range(hi, lo - 1, -1):
        if shutil.which(f'python3.{minor}'):
            return shutil.which(f'python3.{minor}')
    control = Path.home() / '.local/share/strata/components/control'
    try:
        folder = json.loads((control / 'active.json').read_text())['folder']
    except (OSError, ValueError, KeyError):
        return None
    for minor in range(hi, lo - 1, -1):
        exe = control / folder / 'python/bin' / f'python3.{minor}'
        if exe.exists():
            return str(exe)
    return None


def install(div, say=print):
    """Install the division's pin into tools/harness/<division>/<version>/ (never the user's global packages).
    Returns 0 when it is there afterwards."""
    pin = load_pin(div)
    how, root = pin.get('how'), TOOLS / div / str(pin.get('version'))
    root.mkdir(parents=True, exist_ok=True)
    run = lambda argv, **kw: subprocess.run(argv, **kw).returncode  # noqa: E731
    if how == 'npm':
        rc = run([shutil.which('npm') or 'npm', 'install', '--no-fund', '--no-audit', '--prefix', str(root),
                  f'{pin["package"]}@{pin["version"]}'])
    elif how == 'pip':
        py = python_for(pin['python'])
        if not py:
            say(f'no Python {pin["python"]} found (nor Strata\'s bundled one)')
            return 1
        # a checkout at the pinned commit installed in place (Hermes builds no wheel: "use an editable install")
        repo, commit = pin['source'].removeprefix('git+').rsplit('@', 1)
        src = root / 'src'
        # a fresh venv each time: one made from a Python that is gone (or another minor version) cannot be reused
        shutil.rmtree(root, ignore_errors=True)
        root.mkdir(parents=True)
        rc = (run(['git', 'clone', '--quiet', '--filter=blob:none', repo, str(src)])
              or run(['git', '-C', str(src), 'checkout', '--quiet', commit])
              or run([py, '-m', 'venv', str(root)])
              or run([str(root / 'bin/pip'), 'install', '--no-input', '--disable-pip-version-check', '-e', str(src)]))
    elif how == 'appimage':
        import hashlib
        import urllib.request
        image = root / Path(pin['url']).name
        say(f'downloading {pin["url"]}')
        urllib.request.urlretrieve(pin['url'], image)
        h = hashlib.sha256()
        with image.open('rb') as f:
            for block in iter(lambda: f.read(1 << 20), b''):
                h.update(block)
        if h.hexdigest() != pin['sha256']:
            say(f'{image.name}: SHA-256 {h.hexdigest()} is not the pinned {pin["sha256"]}; removed')
            image.unlink()
            return 1
        image.chmod(0o755)
        shutil.rmtree(root / 'squashfs-root', ignore_errors=True)
        rc = run([str(image), '--appimage-extract'], cwd=root, stdout=subprocess.DEVNULL)
        if rc == 0:
            image.unlink()      # the extracted tree is what runs; the pin keeps the image's SHA-256
    else:
        say(f'{div}: installed by hand ({pin.get("note") or pin.get("source")})')
        return 1
    if rc == 0 and how in ('pip', 'appimage'):
        (root / MARK).write_text(json.dumps({'source': pin.get('source'), 'version': pin.get('version'),
                                             'sha256': pin.get('sha256')}, indent=2) + '\n')
    return 0 if rc == 0 and find(div)['ok'] else 1


def sandboxed(argv, work, home, env, binds=()):
    """argv inside bubblewrap: / read-only, a private /tmp, the work folder, the harness folder and binds (the harness's
    shared cache) writable. The network is shared (the harness reaches the proxy on 127.0.0.1)."""
    out = ['bwrap', '--ro-bind', '/', '/', '--dev', '/dev', '--proc', '/proc', '--tmpfs', '/tmp',
           '--bind', str(work), str(work), '--bind', str(home), str(home), '--chdir', str(work), '--die-with-parent']
    for b in binds:
        Path(b).mkdir(parents=True, exist_ok=True)
        out += ['--bind', str(b), str(b)]
    for k, v in env.items():
        out += ['--setenv', k, v]
    return out + list(argv)


# ------------------------------------------------------------------ the adapters

class Harness:
    """One harness: prepare() writes its configuration under home and returns the environment, argv() the one-shot
    command, parse() reads its stdout into {'final', 'tool_calls', 'steps', 'events'}."""
    tested = False
    stdin = False               # the prompt goes on stdin (else argv() names it)

    def __init__(self, div, found):
        self.div, self.found = div, found
        # what a harness fetches for itself on its first start (opencode: its provider package from npm) is kept per
        # version in one cache, so that it is fetched once (by preflight's self-check) and not inside a measured run
        self.cache = TOOLS / div / str(found.get('version')) / 'cache'

    def binds(self):
        return [self.cache]

    def env(self, home):
        return {'HOME': str(home), 'XDG_CONFIG_HOME': str(home / '.config'), 'XDG_DATA_HOME': str(home / '.local/share'),
                'XDG_CACHE_HOME': str(self.cache / 'xdg'), 'npm_config_cache': str(self.cache / 'npm'),
                'XDG_STATE_HOME': str(home / '.local/state'), 'TMPDIR': '/tmp', 'NO_COLOR': '1'}

    def parse(self, stdout):
        return {'final': stdout.strip(), 'tool_calls': [], 'steps': None, 'events': 0}

    def config_files(self, home):
        return []


class Dsh(Harness):
    """DeepSeek Harness, `dsh --profile headless --json -` (the task on stdin; one JSON event per line). Its own home
    (DSH_HOME) gets a home-level patch: the proxy as an OpenAI-compatible provider (thinking through the chat template,
    as the Strata app configures it), the session title request and the telemetry export off; compaction as dsh ships it. Approvals:
    DSH_PERMISSION_MODE danger-full-access (approval never), inside the sandbox."""
    tested = True
    stdin = True

    def prepare(self, home, base_url):
        (home / 'sessions').mkdir(parents=True, exist_ok=True)
        patch = [
            {'id': 'llm-pi-ai', 'config': {'providers': {'jbench': {
                'name': 'Strata (jbench proxy)', 'api': 'openai-completions', 'baseURL': base_url,
                'headers': {'Authorization': 'Bearer strata-local'}, 'streamIdleTimeoutMs': 3600000,
                'compat': {'supportsStore': False, 'thinkingFormat': 'chat-template', 'chatTemplateKwargs': {
                    'enable_thinking': {'$var': 'thinking.enabled'},
                    'reasoning_effort': {'$var': 'thinking.effort', 'omitWhenOff': True}}},
                'models': [{'id': MODEL, 'name': 'Strata (jbench)', 'contextWindow': WINDOW, 'maxTokens': OUTPUT,
                            'input': ['text'], 'reasoning': True,
                            'reasoningEfforts': {'off': None, 'low': 'low', 'medium': 'medium', 'high': 'high', 'max': 'high'}}]}}}},
            {'id': 'agent-default-model', 'config': {'provider': 'jbench', 'model': MODEL, 'reasoningEffort': 'high'}},
            {'id': 'session-title-llm', 'disabled': True},
            {'id': 'session-telemetry-otel', 'disabled': True},
        ]
        # YAML is a superset of JSON: the patch is written as JSON lines in a YAML list
        (home / 'cordis.patch.yml').write_text(''.join(f'- {json.dumps(p, ensure_ascii=False)}\n' for p in patch))
        return {**self.env(home), 'DSH_HOME': str(home), 'DSH_PERMISSION_MODE': 'danger-full-access',
                'DSH_TELEMETRY_DISABLED': '1', 'DSH_TELEMETRY_MODE': 'OFF'}

    def config_files(self, home):
        return [home / 'cordis.patch.yml']

    def argv(self, prompt_file):
        return [self.found['bin'], '--profile', 'headless', '--json', '-']

    def parse(self, stdout):
        final, tools, steps, n = None, [], 0, 0
        for line in stdout.splitlines():
            try:
                e = json.loads(line)
            except ValueError:
                continue
            n += 1
            if e.get('type') == 'final':
                final = e.get('text')
            elif e.get('type') == 'tool_call':
                tools.append(e.get('tool'))
            elif e.get('type') == 'status' and e.get('phase') == 'step_start':
                steps += 1
        return {'final': final, 'tool_calls': tools, 'steps': steps, 'events': n}


class Pi(Harness):
    """pi, `pi --mode json --no-session --offline <task>` (JSONL events). Its agent folder (PI_CODING_AGENT_DIR) gets
    models.json and settings.json as `strata connect pi` writes them, with the window and output limit of this bench;
    compaction as pi ships it. pi has no approvals."""
    tested = True

    def prepare(self, home, base_url):
        home.mkdir(parents=True, exist_ok=True)
        (home / 'models.json').write_text(json.dumps({'providers': {'jbench': {
            'baseUrl': base_url, 'api': 'openai-completions', 'apiKey': 'strata-local',
            'compat': {'supportsDeveloperRole': False, 'supportsReasoningEffort': False},
            'models': [{'id': MODEL, 'name': 'Strata (jbench)', 'reasoning': True, 'input': ['text'], 'contextWindow': WINDOW,
                        'maxTokens': OUTPUT, 'cost': {'input': 0, 'output': 0, 'cacheRead': 0, 'cacheWrite': 0}}]}}}, indent=2))
        (home / 'settings.json').write_text(json.dumps({'defaultProvider': 'jbench', 'defaultModel': MODEL,
                                                        'defaultThinkingLevel': 'high',
                                                        'enableInstallTelemetry': False, 'cacheWarming': 'off'}, indent=2))
        return {**self.env(home), 'PI_CODING_AGENT_DIR': str(home), 'PI_SKIP_VERSION_CHECK': '1', 'PI_TELEMETRY': '0',
                'PI_OFFLINE': '1'}

    def config_files(self, home):
        return [home / 'models.json', home / 'settings.json']

    def argv(self, prompt_file):
        return [self.found['bin'], '--mode', 'json', '--no-session', '--offline', '--thinking', 'high',
                Path(prompt_file).read_text()]

    def parse(self, stdout):
        final, tools, steps, n = None, [], 0, 0
        for line in stdout.splitlines():
            try:
                e = json.loads(line)
            except ValueError:
                continue
            n += 1
            t = e.get('type')
            if t == 'tool_execution_start':
                tools.append(e.get('toolName'))
            elif t == 'turn_start':
                steps += 1
            elif t == 'message_end':
                m = e.get('message') or {}
                if m.get('role') == 'assistant':
                    parts = m.get('content') if isinstance(m.get('content'), list) else [{'type': 'text', 'text': m.get('content') or ''}]
                    text = ''.join(p.get('text', '') for p in parts if p.get('type') == 'text')
                    if text:
                        final = text
        return {'final': final, 'tool_calls': tools, 'steps': steps, 'events': n}


class OpenCode(Harness):
    """opencode, `opencode run --format json --auto --pure --title jbench <task>` with stdin closed (it waits for typing
    otherwise): --auto approves the tools (inside the sandbox), --pure leaves external plug-ins out and --title names the
    session, which saves the title request it would send first. Its config (XDG_CONFIG_HOME/opencode/opencode.json) is
    `strata connect opencode`'s with this bench's limits, compaction as opencode ships it, sharing and updates off; the environment turns
    off the model catalog fetch, LSP downloads and the configs and skills it would read from elsewhere."""
    tested = True

    def prepare(self, home, base_url):
        cfg = home / '.config' / 'opencode'
        cfg.mkdir(parents=True, exist_ok=True)
        (cfg / 'opencode.json').write_text(json.dumps({
            '$schema': 'https://opencode.ai/config.json', 'model': f'jbench/{MODEL}', 'small_model': f'jbench/{MODEL}',
            'autoupdate': False, 'share': 'disabled',
            'provider': {'jbench': {'npm': '@ai-sdk/openai-compatible', 'name': 'Strata (jbench proxy)',
                                    'options': {'baseURL': base_url, 'apiKey': 'strata-local'},
                                    'models': {MODEL: {'name': 'Strata (jbench)', 'tool_call': True, 'reasoning': True,
                                                       'limit': {'context': WINDOW, 'input': WINDOW - OUTPUT, 'output': OUTPUT}}}}}},
            indent=2))
        return {**self.env(home), 'OPENCODE_DISABLE_AUTOUPDATE': '1', 'OPENCODE_DISABLE_SHARE': '1',
                'OPENCODE_DISABLE_MODELS_FETCH': '1', 'OPENCODE_DISABLE_LSP_DOWNLOAD': '1',
                'OPENCODE_DISABLE_CLAUDE_CODE': '1', 'OPENCODE_DISABLE_PROJECT_CONFIG': '1',
                'OPENCODE_DISABLE_EXTERNAL_SKILLS': '1', 'OPENCODE_DISABLE_DEFAULT_PLUGINS': '1'}

    def config_files(self, home):
        return [home / '.config/opencode/opencode.json']

    def argv(self, prompt_file):
        return [self.found['bin'], 'run', '--format', 'json', '--auto', '--pure', '--title', 'jbench',
                Path(prompt_file).read_text()]

    def parse(self, stdout):
        texts, tools, n = [], [], 0
        for line in stdout.splitlines():
            try:
                e = json.loads(line)
            except ValueError:
                continue
            n += 1
            part = e.get('part') or e
            if part.get('type') == 'text' and part.get('text'):
                texts.append(part['text'])
            elif part.get('type') in ('tool', 'tool_use'):
                tools.append(part.get('tool') or part.get('name'))
        return {'final': texts[-1] if texts else stdout.strip() or None, 'tool_calls': tools, 'steps': None, 'events': n}


class Hermes(Harness):
    """Hermes Agent, `hermes chat --oneshot --yolo --format stream-json --query-file <task file>`. Its home (HERMES_HOME)
    gets config.yaml as `strata connect hermes` writes it (compression on, its summariser on the same model), with title
    generation off."""
    tested = True

    def prepare(self, home, base_url):
        home.mkdir(parents=True, exist_ok=True)
        (home / 'config.yaml').write_text(
            f'model:\n  default: {MODEL}\n  provider: lmstudio\n  base_url: {base_url}\n  context_length: {WINDOW}\n'
            'compression:\n  enabled: true\nauxiliary:\n  title_generation:\n    enabled: false\n'
            '  compression:\n    context_length: 65536\n')
        return {**self.env(home), 'HERMES_HOME': str(home), 'OPENAI_API_KEY': 'strata-local'}

    def config_files(self, home):
        return [home / 'config.yaml']

    def argv(self, prompt_file):
        return [self.found['bin'], 'chat', '--oneshot', '--yolo', '--ignore-rules', '--format', 'stream-json',
                '--query-file', str(prompt_file)]

    def parse(self, stdout):
        final, tools, n = None, [], 0
        for line in stdout.splitlines():
            try:
                e = json.loads(line)
            except ValueError:
                continue
            n += 1
            if e.get('type') == 'result':
                final = e.get('text')
            elif e.get('type') == 'tool_use':
                tools.append(e.get('name'))
        return {'final': final, 'tool_calls': tools, 'steps': None, 'events': n}


class Strata(Harness):
    """The Strata desktop app's own agent: scripts/strata_agent.mjs loads the extracted app's agent bridge (the code a chat
    in the app runs) with the proxy as its one local model and runs one turn, mode Bypass, thinking High, on the app's
    bundled node. The bridge writes the app's profile for the DeepSeek Harness the app pins and starts it itself; its
    data folder is the harness folder. The frames it sends to the chat are read back (deltas, tool cards, done)."""
    tested = True

    def app(self):
        return Path(self.found['bin']).parents[2]          # <app>/harness/lib/bin.js -> <app>

    def prepare(self, home, base_url):
        home.mkdir(parents=True, exist_ok=True)
        self.base_url = base_url
        return self.env(home)

    def argv(self, prompt_file):
        return [str(self.app() / 'node/node'), str(ROOT / 'scripts/strata_agent.mjs'), '--app', str(self.app()),
                '--base-url', self.base_url, '--task', str(prompt_file), '--data', str(Path(prompt_file).parent / 'app-data')]

    def parse(self, stdout):
        final, tools, n = None, {}, 0
        for line in stdout.splitlines():
            try:
                e = json.loads(line)
            except ValueError:
                continue
            n += 1
            if e.get('type') == 'final':
                final = e.get('text') or None
            elif e.get('type') == 'agent-tool':     # a tool card, sent again as it changes (running, done)
                card = e.get('tool') or {}
                tools[card.get('id') or len(tools)] = card.get('name')
        return {'final': final, 'tool_calls': list(tools.values()), 'steps': None, 'events': n}


ADAPTERS = {'dsh': Dsh, 'pi': Pi, 'opencode': OpenCode, 'hermes': Hermes, 'strata': Strata}


def adapter(div):
    """The division's harness, or SystemExit with what is missing."""
    found = find(div)
    if div not in ADAPTERS:
        raise SystemExit(f'harness {div!r}: no adapter yet ({found.get("reason") or "scripts/harnesses.py"})')
    if not found['ok']:
        raise SystemExit(f'harness {div!r}: {found["reason"]} (python3 -I scripts/acquire.py check)')
    return ADAPTERS[div](div, found)


# ------------------------------------------------------------------ the result in the work folder

SKIP_DIRS = {'node_modules', '.git', '__pycache__', '.venv', 'venv', '.cache'}
COPY_LIMIT = 30 * 2**20         # what is copied of the work folder into artifact/ (a model that runs npm install, say)


def work_files(work):
    out = []
    for p in sorted(work.rglob('*')):
        if p.is_file() and not any(part in SKIP_DIRS for part in p.relative_to(work).parts):
            out.append(p)
    return out


def pick_html(work):
    """The HTML the harness wrote: the only one, else index.html (the shallowest), else the last written. None if none."""
    html = [p for p in work_files(work) if p.suffix.lower() in ('.html', '.htm')]
    if not html:
        return None
    if len(html) == 1:
        return html[0]
    index = sorted((p for p in html if p.name.lower() == 'index.html'), key=lambda p: len(p.parts))
    return index[0] if index else max(html, key=lambda p: p.stat().st_mtime)


def copy_work(work, files_dir):
    """The work folder's files (up to COPY_LIMIT, skipping dependency folders) into files_dir; returns their list."""
    listed, total = [], 0
    for p in work_files(work):
        rel = p.relative_to(work)
        size = p.stat().st_size
        if total + size > COPY_LIMIT:
            listed.append({'name': str(rel), 'bytes': size, 'copied': False})
            continue
        total += size
        (files_dir / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, files_dir / rel)
        listed.append({'name': str(rel), 'bytes': size, 'copied': True})
    return listed


def selfcheck(div, tmp, timeout=300):
    """The division's harness against the mock engine (scripts/mock_engine.py) through the proxy, on ports of their own:
    one short task in a sandboxed work folder under tmp. No GPU and no model. Returns (ok, detail)."""
    import agent_proxy
    import mock_engine
    h = adapter(div)
    work, home = Path(tmp) / 'work', Path(tmp) / 'home'
    for d in (work, home):
        shutil.rmtree(d, ignore_errors=True)
        d.mkdir(parents=True)
    engine = mock_engine.serve(18690)
    proxy = agent_proxy.Proxy(port=18691, upstream=('127.0.0.1', 18690)).start()
    try:
        prompt = 'Write a small web page into index.html.'
        (home / 'task.txt').write_text(prompt)   # inside the sandbox's binds (its /tmp is a private one)
        env = h.prepare(home, 'http://127.0.0.1:18691/v1')
        proxy.begin(Path(tmp) / 'proxy.jsonl', {'seed': 1, 'max_tokens': 256})
        try:
            r = subprocess.run(sandboxed(h.argv(home / 'task.txt'), work, home, env, h.binds()), cwd=work, text=True,
                               input=prompt if h.stdin else None, stdin=None if h.stdin else subprocess.DEVNULL,
                               capture_output=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return False, f'{div}: no end within {timeout} s'
        reqs = [x for x in proxy.end() if 'sent' in x]
        side = sum(1 for x in reqs if not x['sent'].get('tools'))
        wrote = (work / 'index.html').exists()
        final = h.parse(r.stdout).get('final')
        ok = r.returncode == 0 and bool(reqs) and (wrote or bool(final))
        return ok, (f'{div} {h.found["version"]}: exit {r.returncode}, {len(reqs)} request(s), '
                    f'{"wrote index.html" if wrote else "no file"}, answer {"yes" if final else "no"}'
                    + (f', {side} without tools (side requests?)' if side else '')
                    + ('' if ok else f'; stderr: {r.stderr[-300:]}'))
    finally:
        proxy.stop()
        engine.shutdown()
        engine.server_close()
