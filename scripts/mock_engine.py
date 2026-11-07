"""A stand-in for the engine's /v1/chat/completions, to check a harness's wiring without a model (scripts/preflight.py,
and by hand). No GPU, nothing measured.

The first request that offers a tool able to write a file gets a call to it (index.html with a small page); the request
after a tool result, or one with no such tool, gets a short answer with the page in a code block. Usage and timings are
sent in the last chunk the way Strata sends them.

    python3 -I scripts/mock_engine.py [--port 18600]
"""
import argparse
import json
import re
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PAGE = '<!doctype html>\n<html><head><meta charset="utf-8"><title>mock</title></head>\n<body><canvas id="c"></canvas><p>mock block world</p></body></html>\n'


def write_tool(tools):
    """(tool name, arguments) for a tool that writes a file, else None: its parameters name a path and a content."""
    for t in tools or []:
        f = t.get('function') or {}
        props = ((f.get('parameters') or {}).get('properties') or {})
        path = next((k for k in props if re.search(r'path|file', k, re.I)), None)
        body = next((k for k in props if re.search(r'content|text|data', k, re.I)), None)
        if path and body and re.search(r'write|create|save', f.get('name', ''), re.I):
            return f['name'], {path: 'index.html', body: PAGE}
    return None


def chunk(delta=None, finish=None, extra=None):
    c = {'id': 'mock', 'object': 'chat.completion.chunk', 'created': int(time.time()), 'model': 'mock',
         'choices': [{'index': 0, 'delta': delta or {}, 'finish_reason': finish}]}
    return b'data: ' + json.dumps({**c, **(extra or {})}).encode() + b'\n\n'


class Handler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    calls = []

    def log_message(self, *a):
        pass

    def send_json(self, obj, status=200):
        b = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path.rstrip('/').endswith('/models'):
            return self.send_json({'object': 'list', 'data': [{'id': 'strata', 'object': 'model'}]})
        self.send_json({'ok': True})

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers.get('Content-Length') or 0)) or b'{}')
        Handler.calls.append(body)
        msgs = body.get('messages') or []
        tool = None if any(m.get('role') == 'tool' for m in msgs) else write_tool(body.get('tools'))
        prompt_n = len(json.dumps(msgs)) // 4
        usage = {'prompt_tokens': prompt_n, 'completion_tokens': 40, 'total_tokens': prompt_n + 40,
                 'prompt_tokens_details': {'cached_tokens': 0}}
        timings = {'prompt_n': prompt_n, 'prompt_ms': 10.0, 'prompt_per_second': prompt_n * 100.0,
                   'predicted_n': 40, 'predicted_ms': 200.0, 'predicted_per_second': 200.0}
        if not body.get('stream'):
            msg = ({'role': 'assistant', 'content': None, 'tool_calls': [{'id': 'call_1', 'type': 'function', 'function': {
                'name': tool[0], 'arguments': json.dumps(tool[1])}}]} if tool else
                   {'role': 'assistant', 'content': 'Done.\n\n```html\n' + PAGE + '```\n'})
            return self.send_json({'id': 'mock', 'object': 'chat.completion', 'model': 'mock', 'usage': usage, 'timings': timings,
                                   'choices': [{'index': 0, 'message': msg, 'finish_reason': 'tool_calls' if tool else 'stop'}]})
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.send_header('Transfer-Encoding', 'chunked')
        self.end_headers()
        parts = [chunk({'role': 'assistant', 'reasoning_content': 'Thinking about it.'})]
        if tool:
            parts += [chunk({'tool_calls': [{'index': 0, 'id': 'call_1', 'type': 'function',
                                             'function': {'name': tool[0], 'arguments': ''}}]}),
                      chunk({'tool_calls': [{'index': 0, 'function': {'arguments': json.dumps(tool[1])}}]}),
                      chunk(finish='tool_calls')]
        else:
            parts += [chunk({'content': 'Done. The page is in index.html.\n\n```html\n' + PAGE + '```\n'}), chunk(finish='stop')]
        parts += [b'data: ' + json.dumps({'id': 'mock', 'object': 'chat.completion.chunk', 'choices': [], 'usage': usage,
                                          'timings': timings}).encode() + b'\n\n', b'data: [DONE]\n\n']
        for p in parts:
            self.wfile.write(f'{len(p):x}\r\n'.encode() + p + b'\r\n')
            self.wfile.flush()
            time.sleep(0.01)
        self.wfile.write(b'0\r\n\r\n')


def serve(port):
    srv = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, default=18600)
    srv = serve(ap.parse_args().port)
    print('mock engine on', srv.server_address, flush=True)
    threading.Event().wait()
