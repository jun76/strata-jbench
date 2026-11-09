// Open a page in headless Chrome over the DevTools protocol, let it run for a fixed real time, and capture it.
//   node scripts/page_shot.mjs <url> <out.png> [--wait ms] [--size WxH] [--gpu]
// Prints one JSON line: {ok, hung, hung_at, error, console_errors, load_ms}. Real time rather than Chrome's virtual time: a page
// that keeps a request open or works hard on the main thread never let --virtual-time-budget expire, and the
// command-line --screenshot then never fired. A page whose main thread does not answer within HUNG_MS after the wait
// is reported as hung (the same page freezes a visitor's tab), with where its script was busy (hung_at). console_errors holds uncaught exceptions, console.error
// calls and the browser's own errors (failed requests, WebGL), each "kind: text (source:line)".
import { spawn } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync, writeFileSync, existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const HUNG_MS = 20000;
const args = process.argv.slice(2);
const opt = (name, dflt) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : dflt; };
const [url, out] = args;
const wait = Number(opt('--wait', 10000));
const [width, height] = opt('--size', '1280x800').split('x').map(Number);
const gl = args.includes('--gpu') ? [] : ['--disable-gpu', '--use-gl=swiftshader', '--enable-unsafe-swiftshader'];
const chrome = process.env.CHROME || 'google-chrome';
const sleep = ms => new Promise(r => setTimeout(r, ms));
const result = { ok: false, hung: false, hung_at: null, error: null, console_errors: [], load_ms: null };
const profile = mkdtempSync(join(tmpdir(), 'bench-chrome-'));
const proc = spawn(chrome, ['--headless=new', ...gl, '--remote-debugging-port=0', `--user-data-dir=${profile}`,
  `--window-size=${width},${height}`, '--no-first-run', '--no-default-browser-check', 'about:blank'],
  { stdio: 'ignore', detached: true });

function finish() {
  try { process.kill(-proc.pid, 'SIGKILL'); } catch {}
  setTimeout(() => { rmSync(profile, { recursive: true, force: true }); console.log(JSON.stringify(result)); process.exit(0); }, 300);
}

async function main() {
  let port;
  for (let i = 0; i < 100 && !port; i++) {
    await sleep(100);
    const f = join(profile, 'DevToolsActivePort');
    if (existsSync(f)) port = readFileSync(f, 'utf8').split('\n')[0];
  }
  if (!port) throw new Error('chrome did not start');
  const targets = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  const page = targets.find(t => t.type === 'page');
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  let id = 0;
  const pending = new Map();
  const send = (method, params = {}, timeout = 30000) => new Promise((res, rej) => {
    const n = ++id;
    const t = setTimeout(() => { pending.delete(n); rej(new Error(`timeout: ${method}`)); }, timeout);
    pending.set(n, m => { clearTimeout(t); m.error ? rej(new Error(m.error.message)) : res(m.result); });
    ws.send(JSON.stringify({ id: n, method, params }));
  });
  const where = (u, l) => (u ? ` (${u.replace(/^https?:\/\/127\.0\.0\.1:\d+\//, '')}:${l ?? ''})` : '');
  const t0 = Date.now();
  ws.onmessage = ev => {
    const m = JSON.parse(ev.data);
    if (m.id) return pending.get(m.id)?.(m);
    const p = m.params || {};
    if (m.method === 'Runtime.exceptionThrown') {
      const d = p.exceptionDetails;
      result.console_errors.push(`uncaught: ${d.exception?.description?.split('\n')[0] || d.text}${where(d.url, d.lineNumber + 1)}`);
    } else if (m.method === 'Runtime.consoleAPICalled' && p.type === 'error') {
      const f = p.stackTrace?.callFrames?.[0];
      result.console_errors.push(`console.error: ${p.args.map(a => a.value ?? a.description ?? '').join(' ')}${where(f?.url, f && f.lineNumber + 1)}`);
    } else if (m.method === 'Log.entryAdded' && p.entry.level === 'error') {
      if (!/\/favicon\.ico$/.test(p.entry.url || ''))   // the browser's own request, not the page's
        result.console_errors.push(`${p.entry.source}: ${p.entry.text}${where(p.entry.url, p.entry.lineNumber)}`);
    } else if (m.method === 'Debugger.paused') {
      const f = p.callFrames?.[0];
      result.hung_at = f ? `${f.functionName || '(anonymous)'}${where(f.url, f.location.lineNumber + 1)}` : null;
      send('Debugger.resume').catch(() => {});
    } else if (m.method === 'Page.loadEventFired' && result.load_ms === null) {
      result.load_ms = Date.now() - t0;
    }
  };
  await send('Runtime.enable');
  await send('Log.enable');
  await send('Page.enable');
  await send('Debugger.enable');
  await send('Page.navigate', { url });
  await sleep(wait);
  try {
    await send('Runtime.evaluate', { expression: '1' }, HUNG_MS);
    const shot = await send('Page.captureScreenshot', { format: 'png' }, HUNG_MS);
    writeFileSync(out, Buffer.from(shot.data, 'base64'));
    result.ok = true;
  } catch (e) {
    result.hung = true;
    result.error = `page did not answer within ${HUNG_MS / 1000} s after ${wait / 1000} s`;
    await send('Debugger.pause', {}, 5000).catch(() => {});   // where its script is busy, from Debugger.paused
    await sleep(1000);
  }
  result.console_errors = result.console_errors.slice(0, 50);
}

main().catch(e => { result.error = String(e.message || e); }).finally(finish);
