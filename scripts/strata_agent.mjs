// One chat turn through the Strata desktop app's own agent (the strata division: scripts/harnesses.py Strata).
//
// It loads the app's agent bridge from the extracted app (host/server/agent/agent-bridge.mjs, as the app's host does) with
// one local model, the recording proxy, and runs one turn the way a chat in the app runs it: the app's profile and plug-ins
// for the pinned DeepSeek Harness the app ships, mode Bypass (no approval cards: the sandbox around this process confines
// it), thinking High. Every frame the bridge sends to the chat goes to stdout as one JSON line, then {"type": "final"}.
//
//   <app>/node/node scripts/strata_agent.mjs --app <app root> --base-url http://127.0.0.1:18601/v1 --task <file> --data <dir>
//
// The working folder is the current directory.
import { readFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';

const arg = name => { const i = process.argv.indexOf(`--${name}`); return i > 0 ? process.argv[i + 1] : null; };
const app = arg('app'), baseUrl = arg('base-url'), task = arg('task'), data = arg('data');
if (!app || !baseUrl || !task || !data) { console.error('needs --app, --base-url, --task and --data'); process.exit(2); }
mkdirSync(data, { recursive: true });
const out = obj => process.stdout.write(JSON.stringify(obj) + '\n');

const { createAgentBridge } = await import(pathToFileURL(join(app, 'host/server/agent/agent-bridge.mjs')).href);
const agent = createAgentBridge({
  dataDir: data,
  bundledDir: join(app, 'harness'),
  nodePath: process.execPath,
  // one local model, reached through the proxy (the app's own forwarding endpoint, proxyBase, is not running here)
  localInstances: () => [{ id: 'jbench', label: 'jbench', baseUrl, modelId: 'strata', context: 131072, key: 'strata-local', vision: false, slots: 1 }],
  connections: () => [],
  defaultLocalId: () => 'jbench',
  log: line => console.error(line),
});
let text = '', code = 0;
try {
  const r = await agent.runTurn({
    chatId: 'jbench', message: readFileSync(task, 'utf8'), workspacePath: process.cwd(), mode: 'bypass', thinking: 'high',
    onFrame: f => { if (f.type === 'delta' && f.text) text += f.text; out(f); },
  });
  if (r && r.error) code = 1;
} catch (e) {
  console.error(`turn failed: ${e && e.stack || e}`);
  code = 1;
} finally {
  out({ type: 'final', text });
  try { await agent.close(); } catch { /* ending anyway */ }
}
process.exit(code);
