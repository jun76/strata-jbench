"""The recording proxy between an agent harness and the engine (the harness divisions: divisions/README.md).

The harness is pointed at http://127.0.0.1:<PROXY_PORT>/v1 instead of the engine. Every request is forwarded to the engine
as it came, except for the fields the case pins (sampling, thinking, seed, output cap): what a harness leaves out Strata
fills in from the shared Chat settings or the model card, so without this the conditions would differ per harness. The
harness's own values are kept in the record ("sent") beside what was forwarded ("pinned").

Per request one JSON line in the file given to begin(): when it started and ended, the client-side times (first byte,
first token, first answer token), the message and tool counts, the engine's usage and timings, finish_reason and the
tool calls the model made. The streamed answer goes back to the harness byte for byte.

    p = Proxy(); p.start()
    p.begin(path, pins)   ... run the harness ...   records = p.end()
    p.stop()
"""
import http.client
import json
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = '127.0.0.1'
PROXY_PORT = 18601
ENGINE_PORT = 18600
# hop-by-hop headers (RFC 9110 7.6.1) and the ones the proxy sets itself
SKIP_HEADERS = {'connection', 'keep-alive', 'transfer-encoding', 'te', 'trailer', 'upgrade', 'proxy-connection', 'host',
                'content-length', 'accept-encoding'}


def now():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds')


def pin_body(body, pins):
    """The request as forwarded: the case's values over the harness's. pins: flat fields (temperature, seed, max_tokens,
    ...) plus chat_template_kwargs, merged into the harness's own. A harness that asks with max_completion_tokens gets
    max_tokens instead (the one Strata reads first), so that the cap is the case's either way."""
    out = dict(body)
    for k, v in pins.items():
        if k == 'chat_template_kwargs':
            # a harness may name the effort here too (dsh does): the pinned top-level reasoning_effort is the one, as in plain
            own = {x: y for x, y in (out.get(k) or {}).items() if not (x == 'reasoning_effort' and 'reasoning_effort' in pins)}
            out[k] = {**own, **v}
        else:
            out[k] = v
    if 'max_tokens' in pins:
        out.pop('max_completion_tokens', None)
    if out.get('stream'):
        out['stream_options'] = {**(out.get('stream_options') or {}), 'include_usage': True}
    return out


def shape(body):
    """What the harness sent, without the conversation itself (that stays in raw/): sizes and the fields that steer it."""
    msgs = body.get('messages') or []
    sys_chars = sum(len(m.get('content') if isinstance(m.get('content'), str) else json.dumps(m.get('content') or ''))
                    for m in msgs if m.get('role') in ('system', 'developer'))
    return {'messages': len(msgs), 'roles': [m.get('role') for m in msgs], 'tools': len(body.get('tools') or []),
            'system_chars': sys_chars, 'chars': len(json.dumps(msgs, ensure_ascii=False)),
            **{k: body.get(k) for k in ('model', 'stream', 'temperature', 'top_p', 'top_k', 'min_p', 'presence_penalty',
                                        'repetition_penalty', 'seed', 'max_tokens', 'max_completion_tokens',
                                        'reasoning_effort', 'reasoning_budget_tokens', 'chat_template_kwargs',
                                        'tool_choice', 'parallel_tool_calls') if k in body}}


class Proxy:
    def __init__(self, port=PROXY_PORT, upstream=(HOST, ENGINE_PORT), timeout=7200):
        self.port, self.upstream, self.timeout = port, upstream, timeout
        self.lock = threading.Lock()
        self.path = None           # the JSONL of the case being run (begin / end)
        self.pins = {}
        self.records = []
        self.raw_dir = None        # bodies and streams, kept out of Git (raw/)
        self.n = 0
        proxy = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = 'HTTP/1.1'

            def log_message(self, *a):
                pass

            def do_GET(self):
                proxy.forward(self, None)

            def do_POST(self):
                n = int(self.headers.get('Content-Length') or 0)
                proxy.forward(self, self.rfile.read(n) if n else b'')

        self.server = ThreadingHTTPServer((HOST, port), Handler)
        self.server.daemon_threads = True
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def start(self):
        self.thread.start()
        return self

    def stop(self):
        self.server.shutdown()
        self.server.server_close()

    def begin(self, path, pins, raw_dir=None):
        with self.lock:
            self.path, self.pins, self.records, self.raw_dir, self.n = path, dict(pins), [], raw_dir, 0
            path.parent.mkdir(parents=True, exist_ok=True)
            if raw_dir:
                raw_dir.mkdir(parents=True, exist_ok=True)

    def end(self):
        with self.lock:
            out, self.path, self.pins = self.records, None, {}
            return out

    def write(self, rec):
        with self.lock:
            self.records.append(rec)
            if self.path:
                with self.path.open('a') as f:
                    f.write(json.dumps(rec, ensure_ascii=False) + '\n')

    def forward(self, h, data):
        with self.lock:
            self.n += 1
            n, pins, raw_dir = self.n, dict(self.pins), self.raw_dir
        rec = {'n': n, 'method': h.command, 'path': h.path, 'started_at': now()}
        t0 = time.monotonic()
        body = None
        if data and h.path.rstrip('/').endswith('/chat/completions'):
            try:
                body = json.loads(data)
            except ValueError:
                body = None
        if body is not None:
            rec['sent'] = shape(body)
            fwd = pin_body(body, pins)
            rec['pinned'] = {k: fwd.get(k) for k in pins} | ({'stream_options': fwd['stream_options']} if fwd.get('stream') else {})
            data = json.dumps(fwd).encode()
            if raw_dir:
                (raw_dir / f'req-{n:03d}.json').write_text(json.dumps(body, ensure_ascii=False))
        headers = {k: v for k, v in h.headers.items() if k.lower() not in SKIP_HEADERS}
        conn = http.client.HTTPConnection(*self.upstream, timeout=self.timeout)
        try:
            conn.request(h.command, h.path, body=data, headers=headers)
            resp = conn.getresponse()
        except OSError as e:
            conn.close()
            rec['error'] = f'upstream: {e}'
            self.write(rec)
            msg = json.dumps({'error': {'message': f'jbench proxy: engine not reachable ({e})'}}).encode()
            h.send_response(502)
            h.send_header('Content-Type', 'application/json')
            h.send_header('Content-Length', str(len(msg)))
            h.end_headers()
            h.wfile.write(msg)
            return
        rec['status'] = resp.status
        h.send_response(resp.status)
        for k, v in resp.getheaders():
            if k.lower() not in SKIP_HEADERS:
                h.send_header(k, v)
        stream = 'text/event-stream' in (resp.getheader('Content-Type') or '')
        raw = (raw_dir / f'resp-{n:03d}.sse').open('wb') if raw_dir and body is not None else None
        try:
            if stream:
                h.send_header('Transfer-Encoding', 'chunked')
                h.end_headers()
                self.relay_sse(resp, h, rec, t0, raw)
                h.wfile.write(b'0\r\n\r\n')
            else:
                payload = resp.read()
                h.send_header('Content-Length', str(len(payload)))
                h.end_headers()
                h.wfile.write(payload)
                if raw:
                    raw.write(payload)
                if body is not None:
                    try:
                        j = json.loads(payload)
                        rec.update(usage=j.get('usage'), timings=j.get('timings'))
                        ch = (j.get('choices') or [{}])[0]
                        rec['finish_reason'] = ch.get('finish_reason')
                        rec['tool_calls'] = [(c.get('function') or {}).get('name') for c in (ch.get('message') or {}).get('tool_calls') or []]
                    except ValueError:
                        pass
        except (BrokenPipeError, ConnectionResetError) as e:
            rec['error'] = f'client went away: {e}'      # the harness gave up (its own timeout, or it was stopped)
        finally:
            conn.close()
            if raw:
                raw.close()
        rec['total_ms'] = round((time.monotonic() - t0) * 1000, 1)
        rec['ended_at'] = now()
        if body is not None or rec.get('error'):
            self.write(rec)

    @staticmethod
    def relay_sse(resp, h, rec, t0, raw):
        first = answer = None
        tools, finish, content_chars, reasoning_chars = {}, None, 0, 0
        for line in resp:
            if raw:
                raw.write(line)
            h.wfile.write(f'{len(line):x}\r\n'.encode() + line + b'\r\n')
            h.wfile.flush()
            s = line.strip()
            if not s.startswith(b'data:'):
                continue
            d = s[5:].strip()
            if d == b'[DONE]':
                continue
            try:
                chunk = json.loads(d)
            except ValueError:
                continue
            if chunk.get('usage'):
                rec['usage'] = chunk['usage']
            if chunk.get('timings'):
                rec['timings'] = chunk['timings']
            for ch in chunk.get('choices') or []:
                delta = ch.get('delta') or {}
                r = delta.get('reasoning_content') or delta.get('reasoning')
                c = delta.get('content')
                for tc in delta.get('tool_calls') or []:
                    i = tc.get('index', 0)
                    name = (tc.get('function') or {}).get('name')
                    if name:
                        tools[i] = name
                    tools.setdefault(i, None)
                if (r or c or delta.get('tool_calls')) and first is None:
                    first = time.monotonic()
                if c:
                    content_chars += len(c)
                    if answer is None:
                        answer = time.monotonic()
                if r:
                    reasoning_chars += len(r)
                if ch.get('finish_reason'):
                    finish = ch['finish_reason']
        rec['ttft_ms'] = round((first - t0) * 1000, 1) if first else None
        rec['first_answer_ms'] = round((answer - t0) * 1000, 1) if answer else None
        rec['finish_reason'] = finish
        rec['tool_calls'] = [tools[i] for i in sorted(tools)]
        rec['content_chars'], rec['reasoning_chars'] = content_chars, reasoning_chars
