"""Run benchmark cases from plan/<division>/<env>/cases.jsonl against Strata and write the evidence under results/<division>/<env>/<run-id>/.

  python3 scripts/bench_runner.py --run-id 2026-11-03-night --steps 0,1 [--models qwen:IQ3_S,...] [--dry-run] [--env <id>]

The environment (envs/<id>/env.json) is the one this hardware matches (scripts/envs.py); --env or $BENCH_ENV names it,
and a run under an environment the hardware does not match is refused (a dry run may name any). The division
($BENCH_DIVISION, else bench.json "division", default plain: divisions/README.md) must be one that is measured. In plain the runner calls the engine's
API itself. In a harness division (division.json "harness") it hands each case's prompt to the harness in one shot
(scripts/harnesses.py), inside a sandbox and a fresh work folder, with the recording proxy (scripts/agent_proxy.py)
between the harness and the engine; the proxy puts the case's sampling, thinking, seed and cap into every request.

One engine start per session (strata launch on a dedicated port), a warm-up request, then the session's cases in a
seeded shuffled order. Every request is streamed; the engine's timings and usage are kept as they arrive. A case that
already has a summary.json with status done in this run is skipped, so the same command resumes after a stop.

Per case: results/<division>/<env>/<run-id>/cases/<case id>/
  summary.json      medians and the counts build_cases.py shows
  requests.jsonl    one line per request (timings, usage, client times, check result)
  responses/        the final answer text per request
  artifact/seed-N/  coding cases: the files taken from the answer (or the harness's work folder), manifest.json, screenshot.png,
                    console.txt (the page's errors)
  harness/seed-N/   harness divisions: the harness's output (events.jsonl, stderr.txt) and proxy.jsonl (one line per request)
  raw/              the SSE stream and thinking text; in a harness division also each seed's work folder, the harness's
                    folder and the requests as the harness sent them (kept out of Git)
Per session: results/<division>/<env>/<run-id>/sessions/<session>/ (launch output, /settings, /config, /props, telemetry.csv).
"""
import argparse
import hashlib
import http.client
import json
import os
import random
import re
import shlex
import shutil
import socket
import statistics
import subprocess
import sys
import tempfile
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import agent_proxy  # noqa: E402
import catalog  # noqa: E402
import config  # noqa: E402
import engines  # noqa: E402
from engines import strata_cli  # noqa: E402
import provision  # noqa: E402
import envs  # noqa: E402
import harnesses  # noqa: E402
import machine_info  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PROMPTS = ROOT / 'prompts'
PORT = 18600
HOST = '127.0.0.1'
SAMPLING = {'top_p': 0.95, 'top_k': 20, 'min_p': 0.0, 'presence_penalty': 0.0, 'repetition_penalty': 1.0}
AUTHOR_SAMPLING = {'top_p': 0.95, 'top_k': 20, 'min_p': 0.05, 'presence_penalty': 0.0, 'repetition_penalty': 1.0}
UNEXPECTED_CACHE = 64            # cached prompt tokens above this on a fresh-prompt case: the run is flagged
# a launch includes tuning: --tune thorough on a model at the RAM boundary took over an hour. A launch that still has
# not answered is a launch failure (its cases are failed, the next session starts). BENCH_LAUNCH_TIMEOUT: for tests.
LAUNCH_TIMEOUT = int(os.environ.get('BENCH_LAUNCH_TIMEOUT') or 3 * 3600)
P_CORES = None                   # filled from lscpu: the logical CPUs of the performance cores
GPU = 0                          # the environment's card (env.json "gpu_index"): launches use it alone, telemetry reads it


def now():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds')


def log(run_dir, msg):
    line = f'{now()} {msg}'
    print(line, flush=True)
    with (run_dir / 'runner.log').open('a') as f:
        f.write(line + '\n')


CODING_THINKING = 65536
HARNESS_THINKING = 32768


def thinking_budget(cap, fixture_name=''):
    """Strata's answer_room value for this cap, sent explicitly. The coding cases leave the page more room: the harness
    divisions' Minecraft (game-) 32K, with the cap at the whole window (the engine shortens it on every request to what
    the context has left), since a harness case is meant to finish and only the time limit stops it; plain's coding task (coding-) 64K, with the cap at the whole 128K window: every model thinks all of its
    budget on it (at 16K and 32K the pages had more errors the less they thought), and the page has the other 63K."""
    if fixture_name.startswith('coding-'):
        return min(CODING_THINKING, cap)
    if fixture_name.startswith('game-'):
        return min(HARNESS_THINKING, cap)
    return cap - min(max(512, cap // 4), cap // 2)


# ------------------------------------------------------------------ prompts

def fixture(name):
    return json.loads((PROMPTS / f'{name}.json').read_text())


_DOCS = {}


def long_document(name):
    """A long fixture's document: the first `lines` lines of its corpus with the facts placed after their lines."""
    if name not in _DOCS:
        fx = fixture(name)
        lines = (PROMPTS / fx['corpus']).read_text(encoding='utf-8').split('\n')[:fx['lines']]
        for f in sorted(fx['facts'], key=lambda f: -f['after_line']):
            lines.insert(f['after_line'] + 1, f['text'])
        _DOCS[name] = '\n'.join(lines)
    return _DOCS[name]


def long_question(row):
    """The question a long case asks of its document (its id ends in the question: …-q-d10, …-q-multi)."""
    return fixture(row['fixture'])['questions']['q-' + row['id'].rsplit('-q-', 1)[1]]


def records_body(fx):
    lines = [fx['record_format'].format(i + 1) for i in range(fx['records'])]
    return '\n'.join(lines) + '\n' + fx['question']


def user_text(row, nonce, doc_nonce=None):
    fx = fixture(row['fixture'])
    marker = f'[case {row["id"]} / {nonce}]'
    if fx['kind'] == 'long':
        # the document first, under a marker its questions share (doc_nonce: one per start and seed), then this case's
        # marker and question: the first question of a seed reads the whole document, the others reuse it (prefix cache)
        doc = f'[document {row["fixture"]} / {doc_nonce or nonce}]\n' + long_document(row['fixture'])
        return doc + '\n\n' + marker + '\n' + long_question(row)['question']
    body = records_body(fx) if fx['kind'] == 'records' else fx['prompt']
    return marker + '\n' + body


def request_body(row, seed, nonce, doc_nonce=None):
    effort = row['effort']
    cap = int(row['output_cap'])
    body = {
        'model': ENGINE.api_model if ENGINE else 'strata', 'stream': True, 'stream_options': {'include_usage': True},
        'messages': [{'role': 'user', 'content': user_text(row, nonce, doc_nonce)}],
        'max_tokens': cap, 'temperature': row['temperature'], 'seed': seed,
        **(AUTHOR_SAMPLING if row['config'] == 'author-protocol' else SAMPLING),
    }
    if effort == 'none':
        body['reasoning_effort'] = 'none'
        body['chat_template_kwargs'] = {'enable_thinking': False}
    else:
        body['reasoning_effort'] = 'xhigh'
        body['chat_template_kwargs'] = {'enable_thinking': True}
        body['reasoning_budget_tokens'] = thinking_budget(cap, row['fixture'])
    return body


# ------------------------------------------------------------------ HTTP

def engine_address():
    return (ENGINE.host, ENGINE.port) if ENGINE else (HOST, PORT)


def get_json(path, timeout=10):
    conn = http.client.HTTPConnection(*engine_address(), timeout=timeout)
    try:
        conn.request('GET', path)
        r = conn.getresponse()
        return r.status, json.loads(r.read() or b'null')
    except (OSError, ValueError) as e:
        return None, {'error': str(e)}
    finally:
        conn.close()


def stream_chat(body, timeout, raw_path):
    """POST a streaming chat completion; returns client-side times, the text and the engine's last usage/timings."""
    out = {'error': None, 'finish_reason': None, 'usage': None, 'timings': None}
    content, reasoning = [], []
    t_first = t_answer = None
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    conn = http.client.HTTPConnection(*engine_address(), timeout=timeout)
    t0 = time.monotonic()
    out['started_at'] = now()
    try:
        conn.request('POST', '/v1/chat/completions', body=json.dumps(body).encode(),
                     headers={'Content-Type': 'application/json', 'Accept': 'text/event-stream'})
        resp = conn.getresponse()
        if resp.status != 200:
            out['error'] = f'HTTP {resp.status}: {resp.read()[:500].decode(errors="replace")}'
            return out, '', ''
        with raw_path.open('wb') as raw:
            deadline = t0 + timeout
            for line in resp:
                raw.write(line)
                if time.monotonic() > deadline:
                    out['error'] = 'timeout'
                    break
                line = line.strip()
                if not line.startswith(b'data:'):
                    continue
                data = line[5:].strip()
                if data == b'[DONE]':
                    break
                try:
                    chunk = json.loads(data)
                except ValueError:
                    continue
                if chunk.get('error'):
                    # an error sent inside the stream (HTTP 200): the engine ended while it read or wrote ("the GPU reported
                    # a fatal error and the engine ended", 2026-11-28). Without this the request had no error and no numbers,
                    # and its case was "done" with nothing measured.
                    e = chunk['error']
                    out['error'] = 'stream error: ' + str(e.get('message') if isinstance(e, dict) else e)[:500]
                if chunk.get('usage'):
                    out['usage'] = chunk['usage']
                if chunk.get('timings'):
                    out['timings'] = chunk['timings']
                for choice in chunk.get('choices') or []:
                    delta = choice.get('delta') or {}
                    r = delta.get('reasoning_content') or delta.get('reasoning')
                    c = delta.get('content')
                    if r:
                        reasoning.append(r)
                    if c:
                        content.append(c)
                        if t_answer is None:
                            t_answer = time.monotonic()
                    if (r or c) and t_first is None:
                        t_first = time.monotonic()
                    if choice.get('finish_reason'):
                        out['finish_reason'] = choice['finish_reason']
    except (OSError, http.client.HTTPException) as e:
        out['error'] = f'{type(e).__name__}: {e}'
    finally:
        conn.close()
    t_end = time.monotonic()
    out['ended_at'] = now()
    out['ttft_ms'] = round((t_first - t0) * 1000, 1) if t_first else None
    out['first_answer_ms'] = round((t_answer - t0) * 1000, 1) if t_answer else None
    out['total_ms'] = round((t_end - t0) * 1000, 1)
    return out, ''.join(content), ''.join(reasoning)


# ------------------------------------------------------------------ telemetry

class Telemetry:
    """nvidia-smi once a second, plus the engine's RSS and bytes read from disk."""

    def __init__(self, path):
        self.path = path
        self.samples = []
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self.loop, daemon=True)

    def engine_pid(self):
        return ENGINE.pid() if ENGINE else None

    def loop(self):
        pid = self.engine_pid()
        with self.path.open('a') as f:
            f.write('t,gpu_mem_mib,power_w,temp_c,sm_mhz,util_pct,rss_mib,read_mib,avail_mib\n')
            while not self.stop.wait(1.0):
                q = subprocess.run(['nvidia-smi', '-i', str(GPU), '--query-gpu=memory.used,power.draw,temperature.gpu,clocks.sm,'
                                    'utilization.gpu', '--format=csv,noheader,nounits'],
                                   capture_output=True, text=True).stdout.strip().split(', ')
                rss = read = None
                try:
                    if pid:
                        rss = int(re.search(r'VmRSS:\s+(\d+)', Path(f'/proc/{pid}/status').read_text()).group(1)) // 1024
                        read = int(re.search(r'read_bytes: (\d+)', Path(f'/proc/{pid}/io').read_text()).group(1)) >> 20
                except (OSError, AttributeError):
                    pid = self.engine_pid()
                avail = int(re.search(r'MemAvailable:\s+(\d+)', Path('/proc/meminfo').read_text()).group(1)) // 1024
                s = [time.time(), *[float(x) if x.replace('.', '', 1).isdigit() else None for x in q[:5]], rss, read, avail]
                self.samples.append(s)
                f.write(','.join('' if v is None else str(v) for v in s) + '\n')
                f.flush()

    def window(self, t0, t1):
        rows = [s for s in self.samples if t0 - 1 <= s[0] <= t1 + 1]
        if not rows:
            return {}

        def peak(i):
            vals = [r[i] for r in rows if r[i] is not None]
            return max(vals) if vals else None
        reads = [r[7] for r in rows if r[7] is not None]
        return {'gpu_mem_peak_mib': peak(1), 'power_peak_w': peak(2), 'temp_peak_c': peak(3),
                'rss_peak_mib': peak(6), 'disk_read_mib': (reads[-1] - reads[0]) if len(reads) > 1 else None,
                'mem_avail_min_mib': min((r[8] for r in rows if r[8] is not None), default=None)}


# ------------------------------------------------------------------ checks and artifacts

def check_task(expected, content, work):
    kind = expected['kind']
    if kind == 'final_number':
        nums = re.findall(r'(?:答え|Answer)\s*[:：]\s*\**\s*([-\d,]+)', content)
        got, form = (nums[-1].replace(',', ''), 'answer line') if nums else (None, None)
        if got is None and expected.get('loose'):
            # long-input questions ask whether the fact was found: a last line that is only the number also counts
            last = [ln for ln in content.strip().splitlines() if ln.strip()][-1:] or ['']
            m = re.fullmatch(r'\s*[*「"]*\s*([-\d,]+)\s*[*」"]*\s*[。.]?\s*', last[0])
            got, form = (m.group(1).replace(',', ''), 'bare number') if m else (None, None)
        return {'ok': got is not None and got.lstrip('-').isdigit() and int(got) == expected['value'], 'got': got, 'form': form}
    if kind == 'final_text':
        hits = re.findall(rf'{expected["prefix"]}\s*[:：]\s*\**\s*([^\s*。.\n]+)', content)
        got = hits[-1].strip() if hits else None
        return {'ok': got is not None and got.strip('「」"\'*') == expected['value'], 'got': got}
    if kind == 'python_tests':
        blocks = re.findall(r'```(?:python|py)?\s*\n(.*?)```', content, re.S)
        if not blocks:
            return {'ok': False, 'got': 'no code block'}
        d = Path(tempfile.mkdtemp(prefix='bench-code-', dir=work))
        (d / 'solution.py').write_text(blocks[-1])
        (d / 'test_run.py').write_text(expected['tests'])
        try:
            r = subprocess.run([sys.executable, '-s', '-E', 'test_run.py'], cwd=d, capture_output=True, text=True,
                               timeout=20, env={'PATH': '/usr/bin:/bin', 'HOME': str(d)})
            return {'ok': r.returncode == 0 and 'PASS' in r.stdout, 'got': (r.stdout + r.stderr)[-400:]}
        except subprocess.TimeoutExpired:
            return {'ok': False, 'got': 'timeout'}
        finally:
            shutil.rmtree(d, ignore_errors=True)
    return {'ok': None, 'got': None}


FILE_RE = r'([a-z0-9_][\w./-]*\.(?:html|js|mjs|css|json|md|py|txt|sh))'
# A name counts only where answers put file names: in backticks or bold, in a heading, or alone before a colon.
NAME_HINT = re.compile(rf'`{FILE_RE}`|\*\*{FILE_RE}\*\*|^#+.*?{FILE_RE}|^\s*{FILE_RE}\s*[:：]?\s*$', re.I)
COMMENT_NAME = re.compile(rf'^\s*(?://|#|<!--|/\*)\s*(?:file(?:name)?\s*[:：]\s*)?{FILE_RE}', re.I)
SNIPPET_LINES = 15     # an unnamed block shorter than this is an excerpt (a tweak to show), not a file
DEFAULT_NAME = {'html': 'index.html', 'javascript': 'main.js', 'js': 'main.js', 'css': 'style.css',
                'python': 'main.py', 'py': 'main.py', 'json': 'data.json', 'bash': 'run.sh', 'sh': 'run.sh',
                'markdown': 'README.md', 'md': 'README.md'}


def extract_artifact(content, dest):
    """The answer's code blocks as files. A file name named on the line before a block (or in its first comment) wins."""
    dest.mkdir(parents=True, exist_ok=True)
    (dest / 'response.md').write_text(content)
    files_dir = dest / 'files'
    files, taken = [], set()
    # closed blocks, then a last block the output cap cut off (no closing fence)
    blocks = [(m.group(1), m.group(2), m.start(), False)
              for m in re.finditer(r'```([\w+-]*)[^\n]*\n(.*?)```', content, re.S)]
    tail = re.search(r'```([\w+-]*)[^\n]*\n((?:(?!```).)*)\Z', content, re.S)
    if tail and content.count('```') % 2 == 1:
        blocks.append((tail.group(1), tail.group(2), tail.start(), True))
    for lang, code, start, truncated in blocks:
        lang = lang.lower()
        before = content[:start].rstrip().splitlines()[-1:] or ['']
        first = code.splitlines()[0] if code.strip() else ''
        found = [g for m in NAME_HINT.finditer(before[0]) for g in m.groups() if g]
        cm = COMMENT_NAME.match(first)
        hint = found[-1] if found else cm.group(1) if cm else None
        how = 'named' if hint else 'default'
        name = Path(hint).name if hint else DEFAULT_NAME.get(lang, f'block.{lang or "txt"}')
        if not hint and (lang in ('bash', 'sh', 'shell', 'console', 'text', '')
                         or len(code.splitlines()) < SNIPPET_LINES):
            how, name = 'snippet', f'snippet-{len(files) + 1}.{lang or "txt"}'
        base, i = name, 2
        while name in taken:
            stem, dot, ext = base.rpartition('.')
            name = f'{stem}-{i}.{ext}' if dot else f'{base}-{i}'
            i += 1
        taken.add(name)
        (files_dir / name).parent.mkdir(parents=True, exist_ok=True)
        (files_dir / name).write_text(code)
        files.append({'name': name, 'lang': lang, 'how': how, 'bytes': len(code.encode()), 'truncated': truncated})
    names = {f['name'] for f in files}
    html = next((n for n in ['index.html'] + sorted(names) if n.endswith('.html') and n in names), None)
    server_hint = re.search(r'(npm (?:run|start|install)|npx |vite|python3? -m http\.server|localhost:\d+|http-server)',
                            content)
    kind = ('static-html' if html and not server_hint else 'needs-server' if html or server_hint
            else 'other' if files else 'no-code')
    manifest = {'source': 'answer', 'files': files, 'entry': html, 'kind': kind, 'truncated': any(f['truncated'] for f in files), 'readme': any(n.lower().startswith('readme') for n in names),
                'server_hint': server_hint.group(1) if server_hint else None}
    if html:
        manifest.update(single_file(files_dir / html, sum(n.endswith('.html') for n in names)))
        manifest['screenshot'] = screenshot(files_dir, html, dest)
    (dest / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    return manifest


LOCAL_REF = re.compile(r'(?:src|href)\s*=\s*["\']([^"\'#][^"\']*)["\']', re.I)


def single_file(entry, html_files):
    """Whether the page is one self-contained HTML file: the files it loads by a relative path (scripts, styles, images;
    CDN URLs, data: and anchors do not count)."""
    try:
        text = entry.read_text(errors='replace')
    except OSError:
        return {'single_file': None}
    local = sorted({u for u in LOCAL_REF.findall(text) if not re.match(r'(?:[a-z][\w+.-]*:|//)', u, re.I)})
    return {'single_file': not local, 'local_refs': local[:20], 'html_files': html_files}


SERVER_HINT = r'(npm (?:run|start|install)|npx |vite|python3? -m http\.server|localhost:\d+|http-server)'


def workspace_artifact(work, final, dest):
    """A harness's result: the HTML it wrote into the work folder (harnesses.pick_html) with the folder's files, or,
    when it wrote none, the code blocks of its last answer (extract_artifact)."""
    entry = harnesses.pick_html(work)
    if not entry:
        return extract_artifact(final or '', dest)
    dest.mkdir(parents=True, exist_ok=True)
    (dest / 'response.md').write_text(final or '')
    files_dir = dest / 'files'
    listed = harnesses.copy_work(work, files_dir)
    rel = str(entry.relative_to(work))
    hint = re.search(SERVER_HINT, final or '')
    m = {'source': 'workspace', 'files': listed, 'entry': rel, 'kind': 'needs-server' if hint else 'static-html',
         'truncated': not re.search(r'</html\s*>', entry.read_text(errors='replace'), re.I),
         'readme': any(Path(f['name']).name.lower().startswith('readme') for f in listed),
         'server_hint': hint.group(1) if hint else None,
         **single_file(entry, sum(f['name'].lower().endswith(('.html', '.htm')) for f in listed))}
    m['screenshot'] = screenshot(files_dir, rel, dest)
    (dest / 'manifest.json').write_text(json.dumps(m, ensure_ascii=False, indent=2) + '\n')
    return m


def free_port():
    s = socket.socket()
    s.bind((HOST, 0))
    port = s.getsockname()[1]
    s.close()
    return port


PAGE_WAIT_MS = 10000   # how long a page runs, in real time, before it is captured


def screenshot(files_dir, entry, dest):
    """Serve the files over a local static server and capture the page with headless Chrome (network on, for CDNs;
    software GL, since the engine holds the GPU's memory): scripts/page_shot.mjs lets it run PAGE_WAIT_MS in real time
    and records its errors and whether it froze; page_look says whether anything was drawn. A page found empty or
    frozen is opened once more in a fresh browser and the second capture is kept: a slow CDN or a GL context that
    failed to start once left a page empty that drew every time after. A page stalled on the network (a CDN script that
    does not answer, page_shot.mjs "stalled") is opened again after STALL_RETRY_S, up to STALL_ATTEMPTS times in all:
    the CDN was not answering for minutes on 2026-11-22, and a page that drew at once afterwards was judged frozen."""
    shot = capture(files_dir, entry, dest)
    attempts = 1
    if shot.get('drawn') is False or shot.get('hung'):
        shot, attempts = capture(files_dir, entry, dest), 2
    while shot.get('stalled') and attempts < STALL_ATTEMPTS:
        time.sleep(STALL_RETRY_S)
        shot, attempts = capture(files_dir, entry, dest), attempts + 1
    return shot | ({'attempts': attempts} if attempts > 1 else {})


STALL_ATTEMPTS = 4     # captures of a page stalled on the network, in all
STALL_RETRY_S = 60     # wait between them


def capture(files_dir, entry, dest):
    """One capture: screenshot.png, console.txt and what page_shot.mjs and page_look found."""
    chrome = shutil.which('google-chrome') or shutil.which('chromium')
    node = shutil.which('node')
    if not chrome or not node:
        return {'ok': False, 'error': 'no chrome' if not chrome else 'no node'}
    port = free_port()
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(port), '--bind', HOST, '--directory', str(files_dir)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    png = dest / 'screenshot.png'
    png.unlink(missing_ok=True)
    try:
        time.sleep(1)
        r = subprocess.run([node, str(ROOT / 'scripts' / 'page_shot.mjs'), f'http://{HOST}:{port}/{entry}', str(png),
                            '--wait', str(PAGE_WAIT_MS), '--size', '1280x800'],
                           capture_output=True, text=True, timeout=PAGE_WAIT_MS / 1000 + 90,
                           env={**os.environ, 'CHROME': chrome})
        shot = json.loads(r.stdout.strip().splitlines()[-1])
    except (subprocess.TimeoutExpired, ValueError, IndexError) as e:
        shot = {'ok': False, 'error': 'timeout' if isinstance(e, subprocess.TimeoutExpired) else 'no result',
                'console_errors': []}
    finally:
        srv.terminate()
    (dest / 'console.txt').write_text('\n'.join(shot.get('console_errors') or []) + '\n')
    shot['ok'] = png.exists()
    if shot['ok']:
        shot.update(page_look(png))
    return shot


def page_look(png):
    """Whether the capture shows a drawn scene or an empty page: an empty one is nearly one colour, or has almost no
    edges (a plain or gradient background, a title or a loading text on it). Two numbers on the image scaled to
    320x200, grey: the share of its commonest shade, and the share of pixels that differ by more than 16 from the next
    one to the right or below. Pillow is optional: without it nothing is judged."""
    try:
        from PIL import Image
    except ImportError:
        return {}
    im = Image.open(png).convert('L').resize((320, 200))
    w, h = im.size
    px = im.load()
    edges = sum(1 for y in range(h - 1) for x in range(w - 1)
                if abs(px[x, y] - px[x + 1, y]) > 16 or abs(px[x, y] - px[x, y + 1]) > 16)
    top = max(im.histogram()) / (w * h)
    edge_share = edges / ((w - 1) * (h - 1))
    return {'drawn': top < BLANK_TOP_SHARE and edge_share >= BLANK_EDGE_SHARE,
            'top_share': round(top, 3), 'edge_share': round(edge_share, 4)}


BLANK_TOP_SHARE = 0.9    # one shade over 90% of the image: empty
BLANK_EDGE_SHARE = 0.03  # edges on under 3% of it: empty


# ------------------------------------------------------------------ summary

def median(vals):
    vals = [v for v in vals if v is not None]
    return round(statistics.median(vals), 2) if vals else None


def summarize(row, records):
    ok = [r for r in records if not r.get('error')]
    t = [r.get('timings') or {} for r in ok]
    prefill = [x.get('prompt_per_second') for x in t if (x.get('prompt_n') or 0) > 0]
    draft = sum(x.get('draft_n') or 0 for x in t)
    accepted = sum(x.get('draft_n_accepted') or 0 for x in t)
    checks = [r['check']['ok'] for r in ok if r.get('check') and r['check'].get('ok') is not None]
    flags = sorted({f for r in records for f in r.get('flags', [])})
    status = ('done' if records and len(ok) == len(records) and len(records) >= row['reps']
              else 'partial' if ok else 'failed')
    s = {
        'status': status, 'case': row['id'], 'n': len(ok), 'planned': row['reps'], 'flags': flags,
        'prefill_tps': median(prefill), 'decode_tps': median([x.get('predicted_per_second') for x in t]),
        'ttft_ms': median([r.get('ttft_ms') for r in ok]), 'first_answer_ms': median([r.get('first_answer_ms') for r in ok]),
        'total_ms': median([r.get('total_ms') for r in ok]),
        'completion_tokens': median([(r.get('usage') or {}).get('completion_tokens') for r in ok]),
        'reasoning_chars': median([r.get('reasoning_chars') for r in ok]),
        'accept_rate': round(accepted / draft, 3) if draft else None,
        'capped': sum(1 for r in ok if r.get('finish_reason') == 'length'),
        'correct': f'{sum(checks)}/{len(checks)}' if checks else None,
        'per_request': [{k: r.get(k) for k in ('seed', 'restart', 'ttft_ms', 'total_ms', 'finish_reason', 'error')}
                        | {'prefill_tps': (r.get('timings') or {}).get('prompt_per_second'),
                           'decode_tps': (r.get('timings') or {}).get('predicted_per_second')} for r in records],
    }
    for key in ('gpu_mem_peak_mib', 'rss_peak_mib', 'disk_read_mib', 'power_peak_w'):
        s[key] = max((r['telemetry'].get(key) for r in ok if r.get('telemetry') and r['telemetry'].get(key) is not None),
                     default=None)
    if any(r.get('harness') for r in records):
        # a harness division: per run the harness's requests, tools and preamble (medians), and the result's form
        for key in ('requests', 'requests_without_tools', 'tool_calls_n', 'steps', 'preamble_tokens', 'tools_offered',
                    'cached_share', 'engine_share', 'harness_start_ms'):
            s[key] = median([r.get(key) for r in ok])
        s['capped'] = sum(1 for r in ok if r.get('capped_requests'))
        s['harness'] = next(r['harness'] for r in records if r.get('harness'))
        s['harness_version'] = next((r.get('harness_version') for r in records if r.get('harness')), None)
        s['per_request'] = [p | {k: r.get(k) for k in ('requests', 'tool_calls_n')} for p, r in zip(s['per_request'], records)]
    arts = [r['artifact'] for r in ok if r.get('artifact')]
    if arts:
        s['single_file'] = f'{sum(1 for a in arts if a.get("single_file"))}/{len(arts)}'
        shots = [a.get('screenshot') or {} for a in arts]
        s['drawn'] = f'{sum(1 for x in shots if x.get("drawn"))}/{len(arts)}'
        s['hung'] = sum(1 for x in shots if x.get('hung'))
        s['stalled'] = sum(1 for x in shots if x.get('stalled'))
        s['from_workspace'] = sum(1 for a in arts if a.get('source') == 'workspace')
    return s


# ------------------------------------------------------------------ sessions

def cpu_list(text):
    """'0-5,8' -> {0, 1, 2, 3, 4, 5, 8}"""
    out = set()
    for part in text.strip().split(','):
        if part:
            lo, _, hi = part.partition('-')
            out.update(range(int(lo), int(hi or lo) + 1))
    return out


def lscpu_pcores():
    """One logical CPU per performance core, leaving the first core to the engine's host thread, which the engine puts
    on CPU 0. A hybrid Intel lists its performance cores' CPUs in the cpu_core PMU; without that list (an older kernel),
    the performance cores are the ones with two hardware threads, which misses a hybrid CPU without Hyper-Threading
    (Core Ultra 200S: the list is empty there)."""
    out = subprocess.run(['lscpu', '-e=CPU,CORE'], capture_output=True, text=True).stdout.split('\n')[1:]
    cores = {}
    for line in out:
        if line.strip():
            cpu, core = line.split()[:2]
            cores.setdefault(core, []).append(int(cpu))
    try:
        pcpus = cpu_list(Path('/sys/bus/event_source/devices/cpu_core/cpus').read_text())
    except (OSError, ValueError):
        pcpus = None
    if pcpus:
        firsts = sorted(min(cpus) for cpus in cores.values() if set(cpus) & pcpus)
    else:
        firsts = sorted(min(cpus) for cpus in cores.values() if len(cpus) > 1)
    return ','.join(str(c) for c in firsts if c != 0)


ENGINE = None     # the run's engine adapter (scripts/engines/; bench.json "engine"), set in main


def gpu_used_mib():
    out = subprocess.run(['nvidia-smi', '-i', str(GPU), '--query-gpu=memory.used', '--format=csv,noheader,nounits'],
                         capture_output=True, text=True).stdout.strip()
    return int(out.split()[0]) if out else None


def start_session(row, session_dir, run_dir):
    """One engine start for this row's model, context and launch options, through the run's engine adapter: start, the
    engine's own account of itself (/settings, /config, /props, where it has them), then what the adapter can confirm
    of what was asked. Returns (telemetry, record), telemetry None when the session cannot be used."""
    session_dir.mkdir(parents=True, exist_ok=True)

    def save(info):
        (session_dir / 'session.json').write_text(json.dumps(info, ensure_ascii=False, indent=2) + '\n')

    ENGINE.stop()
    used = gpu_used_mib()
    if used and used > 4000:
        log(run_dir, f'GPU already holds {used} MiB before launch; another engine may be running')
        (session_dir / 'gpu-busy.txt').write_text(f'{used}\n')
    started = now()
    info = ENGINE.start(row, session_dir)
    info.update(engine=ENGINE.id, track=ENGINE.track, started_at=started)
    if info.get('error'):
        save(info)
        if info.get('rc') is None:
            ENGINE.stop(session_dir)
        return None, info
    for name, path in [('settings', '/settings'), ('config', '/config'), ('props', '/props')]:
        status, data = get_json(path)
        if name == 'props' and isinstance(data, dict):
            info['chat_template_sha256'] = hashlib.sha256((data.pop('chat_template', None) or '').encode()).hexdigest()
        (session_dir / f'{name}.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    st = json.loads((session_dir / 'settings.json').read_text())
    info['shared_settings_empty'] = isinstance(st, dict) and not st.get('defaults')
    if not ENGINE.verify(row, info, session_dir):
        ENGINE.collect_log(info, session_dir)
        save(info)
        ENGINE.stop(session_dir)
        return None, info
    tel = Telemetry(session_dir / 'telemetry.csv')
    tel.thread.start()
    save(info)
    return tel, info


def end_session(tel, info, session_dir):
    if tel:
        tel.stop.set()
        tel.thread.join(5)
    ENGINE.collect_log(info, session_dir)
    ENGINE.stop(session_dir)
    info['ended_at'] = now()
    (session_dir / 'session.json').write_text(json.dumps(info, ensure_ascii=False, indent=2) + '\n')


def warmup(session_dir):
    body = {'model': ENGINE.api_model if ENGINE else 'strata', 'stream': True, 'stream_options': {'include_usage': True}, 'max_tokens': 128,
            'temperature': 0.7, 'seed': 1, 'reasoning_effort': 'none', 'chat_template_kwargs': {'enable_thinking': False},
            'messages': [{'role': 'user', 'content': f'[warmup {time.time_ns()}]\nExplain briefly what a hash table is.'}],
            **SAMPLING}
    out, content, _ = stream_chat(body, 600, session_dir / 'warmup.sse')
    (session_dir / 'warmup.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
    return not out['error']


def run_case(row, case_dir, tel, restart, concurrency_fn=None, seeds=None, doc_nonce=None):
    """Every seed of one case in this session (or the seeds given). Returns the request records."""
    records = []
    seeds = seeds or [1, 2, 3][:min(row['reps'], 3)]
    is_long = row['fixture'].startswith('long-')
    for seed in seeds:
        nonce = f'r{restart}-s{seed}-{time.time_ns() % 10**10:010d}'
        body = request_body(row, seed, nonce, doc_nonce)
        t0 = time.time()
        if row['concurrency'] > 1:
            results = [None] * row['concurrency']

            def one(i):
                b = dict(body, messages=[{'role': 'user', 'content': user_text(row, f'{nonce}-c{i}')}])
                results[i] = stream_chat(b, row['timeout_s'], case_dir / 'raw' / f'r{restart}-s{seed}-c{i}.sse')
            threads = [threading.Thread(target=one, args=(i,)) for i in range(row['concurrency'])]
            [th.start() for th in threads]
            [th.join() for th in threads]
            out, content, reasoning = results[0]
            out['concurrent'] = [{k: r[0].get(k) for k in ('ttft_ms', 'total_ms', 'error', 'timings', 'usage')}
                                 for r in results]
            wall = time.time() - t0
            total_tokens = sum(((r[0].get('usage') or {}).get('completion_tokens') or 0) for r in results)
            out['aggregate_tps'] = round(total_tokens / wall, 2) if wall else None
        else:
            out, content, reasoning = stream_chat(body, row['timeout_s'], case_dir / 'raw' / f'r{restart}-s{seed}.sse')
        rec = {'case': row['id'], 'seed': seed, 'restart': restart, 'nonce': nonce, **out,
               'reasoning_chars': len(reasoning), 'content_chars': len(content), 'flags': []}
        if tel:
            rec['telemetry'] = tel.window(t0, time.time())
        cached = ((out.get('usage') or {}).get('prompt_tokens_details') or {}).get('cached_tokens') or 0
        if cached > UNEXPECTED_CACHE and not is_long:
            rec['flags'].append('unexpected_cache')
        resp_dir = case_dir / 'responses'
        resp_dir.mkdir(parents=True, exist_ok=True)
        (resp_dir / f'r{restart}-s{seed}.md').write_text(content)
        if reasoning:
            (case_dir / 'raw' / f'r{restart}-s{seed}.thinking.md').write_text(reasoning)
        fx = fixture(row['fixture'])
        expected = long_question(row)['expected'] if fx['kind'] == 'long' else fx.get('expected')
        if expected and not out['error']:
            rec['check'] = check_task(expected, content, case_dir)
        if row.get('artifact') and not out['error']:
            rec['artifact'] = extract_artifact(content, case_dir / 'artifact' / f'seed-{seed}')
        records.append(rec)
    return records


# ------------------------------------------------------------------ harness divisions

def pins_of(row, seed):
    """What the proxy puts into every request of a harness case: plain's request body for the same case, without the
    conversation (sampling, seed, max_tokens, reasoning_effort, chat_template_kwargs, reasoning_budget_tokens)."""
    body = request_body(row, seed, 'pin')
    return {k: v for k, v in body.items() if k not in ('model', 'stream', 'stream_options', 'messages')}


def iso_ts(text):
    try:
        return datetime.fromisoformat(text).timestamp()
    except (TypeError, ValueError):
        return None


def aggregate(reqs):
    """The engine's numbers over every request of one harness run: tokens and times summed, so the rates are per token
    over all the turns (a turn that only calls a tool weighs what it generated)."""
    t = [r.get('timings') or {} for r in reqs]
    u = [r.get('usage') or {} for r in reqs]
    s = lambda xs, k: sum(x.get(k) or 0 for x in xs)  # noqa: E731
    pn, pms, dn, dms = s(t, 'prompt_n'), s(t, 'prompt_ms'), s(t, 'predicted_n'), s(t, 'predicted_ms')
    timings = {'prompt_n': pn, 'prompt_ms': round(pms, 1), 'prompt_per_second': round(pn / pms * 1000, 2) if pms else None,
               'predicted_n': dn, 'predicted_ms': round(dms, 1),
               'predicted_per_second': round(dn / dms * 1000, 2) if dms else None,
               'draft_n': s(t, 'draft_n'), 'draft_n_accepted': s(t, 'draft_n_accepted')}
    cached = sum(((x.get('prompt_tokens_details') or {}).get('cached_tokens') or 0) for x in u)
    usage = {'prompt_tokens': s(u, 'prompt_tokens'), 'completion_tokens': s(u, 'completion_tokens'),
             'prompt_tokens_details': {'cached_tokens': cached}}
    return timings, usage


def run_harness_case(row, case_dir, tel, restart, h, proxy):
    """Every seed of one case through the harness: a fresh work folder and harness folder (raw/<r>-<s>/), the prompt
    handed over in one shot inside the sandbox, the proxy's record of every request, then the result from the work
    folder. Returns the request records (one per seed, built from that seed's requests)."""
    records = []
    prompt = fixture(row['fixture'])['prompt']
    for seed in [1, 2, 3][:min(row['reps'], 3)]:
        tag = f'r{restart}-s{seed}'
        raw = case_dir / 'raw' / tag
        work, home = raw / 'work', raw / 'home'
        for d in (work, home):
            shutil.rmtree(d, ignore_errors=True)
            d.mkdir(parents=True)
        out_dir = case_dir / 'harness' / f'seed-{seed}'
        shutil.rmtree(out_dir, ignore_errors=True)
        out_dir.mkdir(parents=True)
        (home / 'task.txt').write_text(prompt)    # inside the sandbox's binds, for a harness that reads it from a file
        env = h.prepare(home, f'http://{HOST}:{agent_proxy.PROXY_PORT}/v1')
        argv = harnesses.sandboxed(h.argv(home / 'task.txt'), work, home, env, h.binds())
        (out_dir / 'command.txt').write_text(shlex.join(argv).replace(str(ROOT), '<jbench>') + '\n')
        for f in h.config_files(home):
            shutil.copyfile(f, out_dir / ('config-' + f.name))
        proxy.begin(out_dir / 'proxy.jsonl', pins_of(row, seed), raw / 'requests')
        started_at, t0, timed_out = now(), time.time(), False
        p = subprocess.Popen(argv, stdin=subprocess.PIPE if h.stdin else subprocess.DEVNULL, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, text=True, start_new_session=True, cwd=work)
        try:
            stdout, stderr = p.communicate(input=prompt if h.stdin else None, timeout=row['timeout_s'])
        except subprocess.TimeoutExpired:
            timed_out = True
            strata_cli.kill_session(p.pid)
            stdout, stderr = p.communicate()
        wall = time.time() - t0
        reqs = [r for r in proxy.end() if 'sent' in r]
        (out_dir / 'events.jsonl').write_text(stdout)
        (out_dir / 'stderr.txt').write_text(stderr)
        parsed = h.parse(stdout)
        timings, usage = aggregate(reqs)
        first = reqs[0] if reqs else {}
        off = (iso_ts(first.get('started_at')) or t0) - t0
        names = [n for r in reqs for n in r.get('tool_calls') or [] if n]
        error = ('timeout' if timed_out else f'harness exit {p.returncode}' if p.returncode else
                 'the harness sent no request' if not reqs else
                 next((f'engine: {r.get("error") or r.get("status")}' for r in reqs if r.get('error') or r.get('status') != 200), None))
        rec = {'case': row['id'], 'seed': seed, 'restart': restart, 'harness': h.div, 'harness_version': h.found['version'],
               'started_at': started_at, 'ended_at': now(), 'exit_code': p.returncode, 'error': error,
               'total_ms': round(wall * 1000, 1),
               'ttft_ms': round((off * 1000) + first['ttft_ms'], 1) if first.get('ttft_ms') is not None else None,
               'first_answer_ms': next((round((iso_ts(r['started_at']) - t0) * 1000 + r['first_answer_ms'], 1)
                                        for r in reqs if r.get('first_answer_ms') is not None), None),
               'harness_start_ms': round(off * 1000, 1) if reqs else None,
               'finish_reason': reqs[-1].get('finish_reason') if reqs else None,
               'timings': timings, 'usage': usage,
               'requests': len(reqs), 'requests_without_tools': sum(1 for r in reqs if not r['sent'].get('tools')),
               'tool_calls': {n: names.count(n) for n in sorted(set(names))}, 'tool_calls_n': len(names),
               'steps': parsed.get('steps'),
               'preamble_tokens': (first.get('usage') or {}).get('prompt_tokens'),
               'tools_offered': first.get('sent', {}).get('tools'), 'system_chars': first.get('sent', {}).get('system_chars'),
               'cached_share': round(usage['prompt_tokens_details']['cached_tokens'] / usage['prompt_tokens'], 3)
               if usage['prompt_tokens'] else None,
               'engine_share': round(sum(r.get('total_ms') or 0 for r in reqs) / 1000 / wall, 3) if wall else None,
               'capped_requests': sum(1 for r in reqs if r.get('finish_reason') == 'length'),
               'harness_sent': {k: v for k, v in first.get('sent', {}).items()
                                if k not in ('messages', 'roles', 'tools', 'system_chars', 'chars')},
               'reasoning_chars': sum(r.get('reasoning_chars') or 0 for r in reqs),
               'content_chars': sum(r.get('content_chars') or 0 for r in reqs), 'flags': []}
        if tel:
            rec['telemetry'] = tel.window(t0, time.time())
        resp_dir = case_dir / 'responses'
        resp_dir.mkdir(parents=True, exist_ok=True)
        (resp_dir / f'{tag}.md').write_text(parsed.get('final') or '')
        if row.get('artifact'):
            rec['artifact'] = workspace_artifact(work, parsed.get('final'), case_dir / 'artifact' / f'seed-{seed}')
        records.append(rec)
    return records


def set_aside(case_dir):
    """A case measured again (its last attempt was not done) starts from no records: the earlier attempt's
    requests.jsonl is kept beside it as requests-attempt-N.jsonl and no longer counts in the summary. Otherwise a
    failed launch's record stays among the new requests and the case reads 'partial' although every request passed."""
    f = case_dir / 'requests.jsonl'
    if not f.exists():
        return
    n = 1
    while (case_dir / f'requests-attempt-{n}.jsonl').exists():
        n += 1
    f.rename(case_dir / f'requests-attempt-{n}.jsonl')


def write_case(case_dir, row, records):
    case_dir.mkdir(parents=True, exist_ok=True)
    with (case_dir / 'requests.jsonl').open('a') as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    all_records = [json.loads(l) for l in (case_dir / 'requests.jsonl').read_text().splitlines() if l.strip()]
    s = summarize(row, all_records)
    (case_dir / 'summary.json').write_text(json.dumps(s, ensure_ascii=False, indent=2) + '\n')
    return s


def run_long(rows, run_dir, tel, restart, name):
    """Long cases: per fixture and seed, its questions one after another (q-d10 first) under one document marker, so
    that the first reads the document and the rest reuse it from the prefix cache (the plan's Tier 4b). Each case's
    records are written once all its seeds are done."""
    qorder = ['q-d10', 'q-d50', 'q-d90', 'q-multi']
    by_fx = {}
    for r in sorted(rows, key=lambda r: qorder.index('q-' + r['id'].rsplit('-q-', 1)[1])):
        by_fx.setdefault(r['fixture'], []).append(r)
    for fx_name, group in by_fx.items():
        records = {r['id']: [] for r in group}
        for seed in [1, 2, 3][:min(group[0]['reps'], 3)]:
            doc_nonce = f'r{restart}-s{seed}-{time.time_ns() % 10**10:010d}'
            for r in group:
                records[r['id']] += run_case(r, run_dir / 'cases' / r['id'], tel, restart, seeds=[seed], doc_nonce=doc_nonce)
        for r in group:
            s = write_case(run_dir / 'cases' / r['id'], r, records[r['id']])
            log(run_dir, f'  {r["id"]}: {s["status"]} prefill={s["prefill_tps"]} decode={s["decode_tps"]} '
                         f'ttft={s["ttft_ms"]} correct={s["correct"]} flags={s["flags"]}')


def case_done(case_dir):
    try:
        return json.loads((case_dir / 'summary.json').read_text()).get('status') == 'done'
    except (OSError, ValueError):
        return False


def mark_skipped(case_dir, row, reason):
    case_dir.mkdir(parents=True, exist_ok=True)
    (case_dir / 'summary.json').write_text(json.dumps({'status': 'skipped', 'case': row['id'], 'reason': reason},
                                                      ensure_ascii=False, indent=2) + '\n')


# ------------------------------------------------------------------ standard-v1 (Tier 2)

STD_MAP = {'performance-short': 'std-short', 'performance-prompt-4k': 'std-prompt-4k',
           'performance-prompt-16k': 'std-prompt-16k'}


def run_standard(rows, run_dir, dry):
    """strata bench run --suite standard-v1, three times, each on a freshly started engine."""
    first = rows[0]
    key = f'{first["family"]}-{first["model"]}'
    out_root = run_dir / 'standard' / key
    for k in range(1, 4):
        out = out_root / f'run-{k}'
        if (out / 'done').exists():
            continue
        if dry:
            log(run_dir, f'[dry] standard-v1 {key} run {k}')
            continue
        session_dir = run_dir / 'sessions' / f'S2-{key}-run{k}'
        tel, info = start_session(dict(first, launch_opts='', context=131072), session_dir, run_dir)
        if not tel:
            log(run_dir, f'standard-v1 {key}: launch failed')
            for row in rows:
                mark_skipped(run_dir / 'cases' / row['id'], row, 'launch failed: ' + info.get('error', '')[:200])
            return
        out.parent.mkdir(parents=True, exist_ok=True)
        r = subprocess.run(['strata', 'bench', 'run', '--url', f'http://{HOST}:{PORT}', '--suite', 'standard-v1',
                            '--out', str(out), '--json', '--background', 'none (dedicated benchmark session)'],
                           capture_output=True, text=True, timeout=4 * 3600)
        (session_dir / 'bench-run.txt').write_text(r.stdout + r.stderr)
        end_session(tel, info, session_dir)
        if out.exists():
            (out / 'done').write_text(now() + '\n')
        log(run_dir, f'standard-v1 {key} run {k}: rc={r.returncode}')
    if dry:
        return
    # one summary per case id from the three results.json files
    per_case = {}
    for res in sorted(out_root.glob('run-*/**/results.json')):
        data = json.loads(res.read_text())
        for req in data.get('requests', []):
            rid = req.get('id', '')
            base = re.sub(r'-r\d+$', '', rid)
            case = STD_MAP.get(base) or (f'std-sanity-{rid.split("-", 1)[1]}' if rid.startswith('sanity-') else None)
            if case:
                per_case.setdefault(case, []).append(req)
    for row in rows:
        suffix = row['id'].split(f'{row["model"]}-', 1)[1]
        reqs = per_case.get(suffix, [])
        case_dir = run_dir / 'cases' / row['id']
        case_dir.mkdir(parents=True, exist_ok=True)
        with (case_dir / 'requests.jsonl').open('w') as f:
            for q in reqs:
                f.write(json.dumps(q, ensure_ascii=False) + '\n')

        def pick(group, name, scale=1):
            return median([(q.get(group) or {}).get(name) * scale for q in reqs
                           if (q.get(group) or {}).get(name) is not None])
        passed = [(q.get('evaluation') or {}).get('passed') for q in reqs
                  if (q.get('evaluation') or {}).get('passed') is not None]
        s = {'status': 'done' if reqs else 'failed', 'case': row['id'], 'n': len(reqs), 'planned': row['reps'],
             'prefill_tps': pick('metrics', 'prompt_tps'), 'decode_tps': pick('metrics', 'decode_tps'),
             'ttft_ms': pick('timings', 'ttft_s', 1000), 'first_answer_ms': pick('timings', 'first_answer_s', 1000),
             'total_ms': pick('timings', 'total_s', 1000), 'completion_tokens': pick('tokens', 'output_tokens'),
             'capped': sum(1 for q in reqs if q.get('finish_reason') == 'length'),
             'correct': f'{sum(1 for p in passed if p)}/{len(passed)}' if passed else None,
             'source': [str(p.relative_to(run_dir)) for p in sorted(out_root.glob('run-*/**/results.json'))]}
        (case_dir / 'summary.json').write_text(json.dumps(s, ensure_ascii=False, indent=2) + '\n')


# ------------------------------------------------------------------ main

def main():
    global P_CORES, GPU, ENGINE
    ap = argparse.ArgumentParser()
    ap.add_argument('--run-id', required=True)
    ap.add_argument('--steps', default='0,1')
    ap.add_argument('--models', default='', help='family:model,... (default: all)')
    ap.add_argument('--ids', default='', help='only these case ids (comma separated)')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--env', default='', help='the environment (default: the one this hardware matches)')
    ap.add_argument('--engine', default='', help='the engine (catalog/engines/; default: bench.json "engine", else strata)')
    ap.add_argument('--track', default='', help='exact, default or custom (default: bench.json "track", else exact)')
    a = ap.parse_args()
    P_CORES = lscpu_pcores()
    env_id = a.env if a.dry_run and a.env else envs.current(a.env)
    cfg = envs.load(env_id)
    GPU = envs.gpu_index(cfg)
    div = envs.division(measuring=True)
    harness = envs.load_division(div).get('harness')
    h = proxy = None
    if harness:
        if not shutil.which('bwrap'):
            raise SystemExit('a harness division runs the harness inside bubblewrap (bwrap), which is not installed')
        try:
            h = harnesses.adapter(div)
        except SystemExit:
            if not a.dry_run:
                raise
    run_dir = envs.run_dir(env_id, a.run_id, div)
    run_dir.mkdir(parents=True, exist_ok=True)
    steps = a.steps.split(',')
    models = {tuple(m.split(':')) for m in a.models.split(',') if m}
    ids = set(filter(None, a.ids.split(',')))
    rows = [json.loads(l) for l in (envs.plan_dir(env_id) / 'cases.jsonl').read_text().splitlines()]
    settings = config.load()
    engine_id = a.engine or settings.get('engine') or engines.DEFAULT
    mine = config.of_engine(engine_id)
    rows = [r for r in rows if r['step'] in steps and (not models or (r['family'], r['model']) in models)
            and (not ids or r['id'] in ids) and mine(r)]
    if os.environ.get('BENCH_CONFIG'):
        # under the supervisor: the run's own settings narrow the cases further (a preset, tasks); by hand, the
        # arguments alone choose
        picked = catalog.chosen_ids(rows, settings.get('tasks'), settings.get('preset'))
        if picked is not None:
            rows = [r for r in rows if r['id'] in picked]
    ENGINE = engines.get(engine_id, host=HOST, port=PORT, gpu=GPU, launch_timeout=LAUNCH_TIMEOUT, run_dir=run_dir,
                         p_cores=P_CORES, track=a.track or settings.get('track'), dry=a.dry_run,
                         **{k: settings.get(k) for k in ('engine_url', 'engine_note', 'engine_path')})
    if not (run_dir / 'machine.json').exists():
        machine = {**machine_info.collect(P_CORES, cfg.get('memory'), GPU), 'env_id': env_id, 'created_at': now()}
        if ENGINE.id != engines.DEFAULT and not a.dry_run:   # the "Test system" box names the engine measured
            machine['env']['strata'] = f'{ENGINE.info["label"]} {ENGINE.probe().get("version") or ""}'.strip()
        (run_dir / 'machine.json').write_text(json.dumps(machine, indent=2, ensure_ascii=False) + '\n')
    # the env.json this start measured with (envs/ is outside Git): published with the run, and the pages read it
    if (envs.ENVS / env_id / 'env.json').exists():
        shutil.copyfile(envs.ENVS / env_id / 'env.json', run_dir / 'env.json')
    log(run_dir, f'start env={env_id} division={div} engine={ENGINE.id} track={ENGINE.track} steps={steps} cases={len(rows)} dry={a.dry_run}')
    # what this start measured: the engine, its version and track (engine.json; Strata: models.json too), and where the
    # engine, the harness and the models on this PC came from (provision.json)
    log(run_dir, ENGINE.record(run_dir, rows) if not a.dry_run else f'[dry] engine {ENGINE.id} track {ENGINE.track}')
    provision.copy_to(run_dir)
    if harness:
        # the harness this start drove (published with the run, beside models.json)
        hinfo = {'division': div, 'harness': harness, 'pin': harnesses.load_pin(div),
                'found': h.found if h else harnesses.find(div), 'adapter_tested': bool(h and h.tested), 'recorded_at': now()}
        (run_dir / 'harness.json').write_text(json.dumps(hinfo, ensure_ascii=False, indent=2).replace(str(Path.home()), '~') + '\n')
        log(run_dir, f'harness: {harness} {hinfo["found"].get("version")} ({hinfo["found"].get("where") or hinfo["found"].get("reason")})')
        if h and not a.dry_run:
            proxy = agent_proxy.Proxy(upstream=engine_address()).start()

    for step in steps:
        step_rows = [r for r in rows if r['step'] == step]
        if step == '2':
            by_model = {}
            for r in step_rows:
                by_model.setdefault((r['family'], r['model']), []).append(r)
            for group in by_model.values():
                if all(case_done(run_dir / 'cases' / r['id']) for r in group):
                    continue
                run_standard(group, run_dir, a.dry_run)
            continue
        sessions = {}
        for r in step_rows:
            sessions.setdefault(r['session'] + ('' if step != '0' else ''), []).append(r)
        for name, srows in sessions.items():
            todo = []
            for r in srows:
                case_dir = run_dir / 'cases' / r['id']
                if case_done(case_dir):
                    continue
                if not (PROMPTS / f'{r["fixture"]}.json').exists():
                    if not a.dry_run:
                        mark_skipped(case_dir, r, f'fixture {r["fixture"]} not built yet')
                    continue
                todo.append(r)
            if not todo:
                continue
            restarts = max(r['restarts'] for r in todo)
            log(run_dir, f'session {name}: {len(todo)} cases x {restarts} start(s)')
            if a.dry_run:
                continue
            for r in todo:
                set_aside(run_dir / 'cases' / r['id'])
            for restart in range(1, restarts + 1):
                session_dir = run_dir / 'sessions' / f'{name}-T{step}' / f'start-{restart}'
                tel, info = start_session(todo[0], session_dir, run_dir)
                if not tel:
                    log(run_dir, f'session {name}: launch failed: {info.get("error", "")[-300:]}')
                    error = 'launch timed out' if info.get('rc') is None else \
                        'MTP not loaded' if info.get('mtp_missing') else \
                        'setting not applied' if info.get('setting_missing') else 'launch failed'
                    for r in todo:
                        write_case(run_dir / 'cases' / r['id'], r,
                                   [{'case': r['id'], 'restart': restart, 'error': error, 'flags': []}])
                    break
                log(run_dir, f'session {name}: launched in {info["launch_s"]}s')
                kept = ENGINE.after_launch(todo[0], info, session_dir)
                if kept:
                    log(run_dir, f'session {name}: {kept}')
                if not warmup(session_dir):
                    log(run_dir, f'session {name}: warm-up failed')
                order = list(todo)
                random.Random(f'{a.run_id}-{name}-{restart}').shuffle(order)
                long_cases = [r for r in order if r['fixture'].startswith('long-')]
                if long_cases:
                    run_long(long_cases, run_dir, tel, restart, name)
                    order = [r for r in order if not r['fixture'].startswith('long-')]
                for r in order:
                    case_dir = run_dir / 'cases' / r['id']
                    records = (run_harness_case(r, case_dir, tel, restart, h, proxy) if h
                               else run_case(r, case_dir, tel, restart))
                    s = write_case(case_dir, r, records)
                    log(run_dir, f'  {r["id"]}: {s["status"]} prefill={s["prefill_tps"]} decode={s["decode_tps"]} '
                                 f'ttft={s["ttft_ms"]} correct={s["correct"]} flags={s["flags"]}')
                    if s['status'] == 'failed' and get_json('/props')[0] is None:
                        log(run_dir, f'session {name}: engine not answering; ending session')
                        break
                end_session(tel, info, session_dir)
    if proxy:
        proxy.stop()
    log(run_dir, 'finished')


if __name__ == '__main__':
    main()
