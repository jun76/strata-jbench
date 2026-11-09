できます。以下は、**ブラウザだけで動くマイクラ風の3D箱庭ゲーム（ボクセル建造・破壊・視点移動・日周期つき）**の単一HTMLファイルです。  
保存名例：`minecraft-style-sandbox.html` としてブラウザで開くと起動します。

特徴

- WASD移動 / Spaceジャンプ / Shift着地・飛行下降 / Gで飛行切替
- マウス視点（ポインターロック）
- 左クリック：ブロック破壊 / 右クリック：設置 / 中クリック：選択ブロックに反映
- ホットバー 1〜9 でブロック切り替え
- 木、草、土、石、砂、ガラス、レンガなど
- 自動地形・木生成、距離霧、昼夜サイクル

※Three.jsをCDNから読み込むため、初回はネット接続が必要です。  
※ブラウザによって右クリックメニューが出ますが、ゲーム中はそのイベントを抑制しています。

```html
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>マイクラ風3D箱庭</title>
<style>
  html,body{margin:0;height:100%;overflow:hidden;background:#000;font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#fff}
  #game{width:100%;height:100%;display:block;cursor:crosshair}
  #ui{position:fixed;inset:0;pointer-events:none}
  #crosshair{position:absolute;left:50%;top:50%;width:18px;height:18px;transform:translate(-50%,-50%);opacity:.8}
  #crosshair::before,#crosshair::after{content:"";position:absolute;background:#fff;box-shadow:0 0 2px #000}
  #crosshair::before{left:8px;top:0;width:2px;height:18px}
  #crosshair::after{left:0;top:8px;width:18px;height:2px}
  #hotbar{position:absolute;left:50%;bottom:18px;transform:translateX(-50%);display:flex;gap:6px;padding:8px;border-radius:12px;background:rgba(0,0,0,.35);backdrop-filter:blur(4px);pointer-events:auto}
  .slot{width:44px;height:44px;border-radius:9px;background:rgba(255,255,255,.08);border:2px solid rgba(255,255,255,.25);display:grid;place-items:center;font-size:12px;text-align:center;position:relative}
  .slot.sel{border-color:#fff;background:rgba(255,255,255,.18);transform:translateY(-4px)}
  .slot .idx{position:absolute;top:2px;left:5px;opacity:.65;font-size:10px}
  #info{position:absolute;top:12px;left:12px;line-height:1.55;background:rgba(0,0,0,.35);padding:10px 12px;border-radius:10px;font-size:13px;backdrop-filter:blur(4px)}
  #start{position:absolute;inset:0;display:grid;place-items:center;background:rgba(0,0,0,.55);pointer-events:auto}
  #start .panel{background:rgba(20,25,35,.92);padding:28px 34px;border-radius:16px;border:1px solid rgba(255,255,255,.15);box-shadow:0 20px 60px rgba(0,0,0,.5);max-width:640px;text-align:center}
  #start h1{margin:0 0 10px;font-size:28px}
  #start p{margin:.35rem 0;font-size:14px;line-height:1.75;opacity:.92}
  #start button{margin-top:18px;padding:12px 24px;border:none;border-radius:10px;background:#4a90d9;color:#fff;font-size:16px;cursor:pointer}
  #start button:hover{background:#3a7dc4}
  #loading{position:absolute;inset:0;display:grid;place-items:center;background:rgba(15,20,30,.95);z-index:20;font-size:18px}
</style>
</head>
<body>
<canvas id="game"></canvas>
<div id="ui">
  <div id="crosshair"></div>
  <div id="info">
    WASD: 移動 / Space: ジャンプ / Shift: 飛行時は下降<br>
    左クリック: 破壊 / 右クリック: 設置 / 中クリック: 選択<br>
    1-9: ブロック / G: 飛行 ON-OFF / F3相当情報表示<br>
    <span id="coords"></span>
  </div>
  <div id="hotbar"></div>
</div>
<div id="start">
  <div class="panel">
    <h1>マイクラ風3D箱庭</h1>
    <p>クリックでゲーム開始。画面をクリックするとマウス視点が固定されます。</p>
    <p>左クリックでブロックを壊し、右クリックで設置できます。<br>1〜9でホットバー、Gで飛行モードも試せます。</p>
    <button id="play">クリックして開始</button>
  </div>
</div>
<div id="loading">読み込み中…</div>

<script type="module">
import * as THREE from "https://unpkg.com/three@0.160.0/build/three.module.js";

// =========================================================
// 基本定数
// =========================================================
const CHUNK_SIZE = 16;
const HEIGHT = 64;
const WORLD_CHUNKS = 8;
const WORLD_SIZE = CHUNK_SIZE * WORLD_CHUNKS;

const AIR = 0;
const GRASS = 1;
const DIRT = 2;
const STONE = 3;
const SAND = 4;
const WOOD = 5;
const LEAVES = 6;
const PLANKS = 7;
const GLASS = 8;
const BRICK = 9;
const BEDROCK = 10;

const PLAYER_RADIUS = 0.3;
const PLAYER_HEIGHT = 1.8;
const PLAYER_EYE = 1.62;
const GRAVITY = 28;
const JUMP_V = 8.8;
const WALK_SPEED = 5.2;
const SPRINT_SPEED = 8.0;
const FLY_SPEED = 10.0;
const RAY_DISTANCE = 6.0;

const BLOCKS = [];
BLOCKS[AIR] = {name:"Air", solid:false, transparent:true, top:"#000000", side:"#000000", bottom:"#000000"};
BLOCKS[GRASS] = {name:"Grass", solid:true, transparent:false, top:"#6ab04c", side:"#7f5e3c", bottom:"#7f5e3c"};
BLOCKS[DIRT] = {name:"Dirt", solid:true, transparent:false, top:"#7f5e3c", side:"#7f5e3c", bottom:"#7f5e3c"};
BLOCKS[STONE] = {name:"Stone", solid:true, transparent:false, top:"#8a8a8a", side:"#8a8a8a", bottom:"#8a8a8a"};
BLOCKS[SAND] = {name:"Sand", solid:true, transparent:false, top:"#e2d2a1", side:"#e2d2a1", bottom:"#e2d2a1"};
BLOCKS[WOOD] = {name:"Wood", solid:true, transparent:false, top:"#b07e4e", side:"#6e4b25", bottom:"#b07e4e"};
BLOCKS[LEAVES] = {name:"Leaves", solid:true, transparent:false, top:"#3f8f4f", side:"#3f8f4f", bottom:"#3f8f4f"};
BLOCKS[PLANKS] = {name:"Planks", solid:true, transparent:false, top:"#c8a05a", side:"#c8a05a", bottom:"#c8a05a"};
BLOCKS[GLASS] = {name:"Glass", solid:true, transparent:true, top:"#aaddff", side:"#aaddff", bottom:"#aaddff"};
BLOCKS[BRICK] = {name:"Brick", solid:true, transparent:false, top:"#a45b4b", side:"#9c5348", bottom:"#7f3e38"};
BLOCKS[BEDROCK] = {name:"Bedrock", solid:true, transparent:false, top:"#1d1d1d", side:"#1d1d1d", bottom:"#1d1d1d"};

const HOTBAR = [GRASS, DIRT, STONE, SAND, WOOD, PLANKS, LEAVES, BRICK, GLASS];
let selectedHotbar = 0;

// =========================================================
// 雑音・地形
// =========================================================
const SEED = (Math.random() * 2147483647) | 0;

function hash2(x, z) {
  let h = Math.imul(x | 0, 374761393);
  h ^= Math.imul(z | 0, 668265263);
  h ^= Math.imul(SEED | 0, 1274126177);
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  h ^= h >>> 15;
  return (h >>> 0) / 4294967295;
}

function hash2i(x, z) {
  let h = Math.imul(x | 0, 374761393);
  h ^= Math.imul(z | 0, 668265263);
  h ^= Math.imul(SEED | 0, 1274126177);
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  h ^= h >>> 15;
  return (h ^ (h >>> 16)) >>> 0;
}

function smooth(t) { return t * t * (3 - 2 * t); }
function lerp(a,b,t){ return a + (b-a)*t; }

function noise2D(x, z) {
  const X = Math.floor(x), Z = Math.floor(z);
  const xf = smooth(x - X), zf = smooth(z - Z);
  const a = hash2(X, Z);
  const b = hash2(X+1, Z);
  const c = hash2(X, Z+1);
  const d = hash2(X+1, Z+1);
  return lerp(lerp(a,b,xf), lerp(c,d,xf), zf);
}

function fbm(x, z) {
  let sum = 0, amp = 1, freq = 0.018, max = 0;
  for (let i=0; i<5; i++) {
    sum += noise2D(x*freq, z*freq) * amp;
    max += amp;
    amp *= 0.52;
    freq *= 2.05;
  }
  return sum / max;
}

function terrainHeight(x, z) {
  let h = 22;
  h += fbm(x + 1000, z + 1000) * 22;
  const mountains = Math.pow(Math.max(0, fbm(x*0.9 + 500, z*0.9 - 400) - 0.45) * 2.6, 2.0);
  h += mountains * 14;
  h += (noise2D(x*0.11 + 333, z*0.11 - 121) - 0.5) * 6;
  h = Math.floor(Math.max(4, Math.min(HEIGHT - 8, h)));
  return h;
}

// =========================================================
// Three.js
// =========================================================
const canvas = document.getElementById("game");
let renderer;
try {
  renderer = new THREE.WebGLRenderer({canvas, antialias:false, powerPreference:"high-performance"});
} catch(e) {
  document.getElementById("loading").textContent = "WebGLを初期化できませんでした。";
  throw e;
}
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.8));
renderer.setSize(window.innerWidth, window.innerHeight);

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0x87ceeb, 35, 135);

const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.05, 700);
camera.rotation.order = "YXZ";

const opaqueMaterial = new THREE.MeshBasicMaterial({ vertexColors:true, fog:true });
const transparentMaterial = new THREE.MeshBasicMaterial({
  vertexColors:true, fog:true, transparent:true, opacity:0.72, depthWrite:false, side:THREE.DoubleSide
});

const highlightBox = new THREE.LineSegments(
  new THREE.EdgesGeometry(new THREE.BoxGeometry(1.001, 1.001, 1.001)),
  new THREE.LineBasicMaterial({ color:0x000000, opacity:0.75, transparent:true })
);
highlightBox.visible = false;
scene.add(highlightBox);

// =========================================================
// ワールドデータ
// =========================================================
const chunks = new Map();
const dirtyChunks = new Set();

function chunkKey(cx, cz) { return cx + "|" + cz; }
function inWorld(cx, cz) { return cx >= 0 && cz >= 0 && cx < WORLD_CHUNKS && cz < WORLD_CHUNKS; }
function worldInBounds(wx, wy, wz) { return wx >= 0 && wz >= 0 && wx < WORLD_SIZE && wz < WORLD_SIZE && wy >= 0 && wy < HEIGHT; }

function idx(lx, ly, lz) { return lx + CHUNK_SIZE * (lz + CHUNK_SIZE * ly); }

function generateChunk(cx, cz) {
  const key = chunkKey(cx, cz);
  if (chunks.has(key)) return chunks.get(key);
  const data = new Uint8Array(CHUNK_SIZE * CHUNK_SIZE * HEIGHT);
  const ox = cx * CHUNK_SIZE;
  const oz = cz * CHUNK_SIZE;

  for (let lz=0; lz<CHUNK_SIZE; lz++) {
    for (let lx=0; lx<CHUNK_SIZE; lx++) {
      const wx = ox + lx;
      const wz = oz + lz;
      const h = terrainHeight(wx, wz);

      for (let y=0; y<HEIGHT; y++) {
        let id = AIR;
        if (y === 0) id = BEDROCK;
        else if (y < h - 3) id = STONE;
        else if (y < h) id = DIRT;
        else if (y === h) {
          if (h <= 20) id = SAND;
          else id = GRASS;
        }

        // 簡易洞窟：地下に少し穴
        if (y > 2 && y < h - 2) {
          const caveNoise = noise2D(wx*0.18 + y*0.25 + 1200, wz*0.18 - y*0.18 + 777);
          if (caveNoise > 0.69) id = AIR;
        }

        data[idx(lx,y,lz)] = id;
      }
    }
  }

  const chunk = { data, group:null };
  chunks.set(key, chunk);
  return chunk;
}

function getChunk(cx, cz) {
  if (!inWorld(cx, cz)) return null;
  const key = chunkKey(cx, cz);
  let c = chunks.get(key);
  if (!c) c = generateChunk(cx, cz);
  return c;
}

function getBlock(wx, wy, wz) {
  if (wy < 0) return BEDROCK;
  if (wy >= HEIGHT) return AIR;
  if (wx < 0 || wz < 0 || wx >= WORLD_SIZE || wz >= WORLD_SIZE) return AIR;
  const cx = Math.floor(wx / CHUNK_SIZE);
  const cz = Math.floor(wz / CHUNK_SIZE);
  const c = getChunk(cx, cz);
  if (!c) return AIR;
  const lx = wx - cx * CHUNK_SIZE;
  const lz = wz - cz * CHUNK_SIZE;
  return c.data[idx(lx, wy, lz)];
}

function setBlockData(wx, wy, wz, id, markDirty = true) {
  if (!worldInBounds(wx, wy, wz)) return false;
  const cx = Math.floor(wx / CHUNK_SIZE);
  const cz = Math.floor(wz / CHUNK_SIZE);
  const c = getChunk(cx, cz);
  if (!c) return false;
  const lx = wx - cx * CHUNK_SIZE;
  const lz = wz - cz * CHUNK_SIZE;
  c.data[idx(lx, wy, lz)] = id;

  if (markDirty) {
    markChunkDirty(cx, cz);
    if (lx === 0) markChunkDirty(cx - 1, cz);
    if (lx === CHUNK_SIZE - 1) markChunkDirty(cx + 1, cz);
    if (lz === 0) markChunkDirty(cx, cz - 1);
    if (lz === CHUNK_SIZE - 1) markChunkDirty(cx, cz + 1);
  }
  return true;
}

function markChunkDirty(cx, cz) {
  if (!inWorld(cx, cz)) return;
  const key = chunkKey(cx, cz);
  const c = chunks.get(key);
  if (c) {
    dirtyChunks.add(key);
  }
}

function isSolid(id) {
  const b = BLOCKS[id];
  return !!b && b.solid;
}

function isOpaque(id) {
  const b = BLOCKS[id];
  return id !== AIR && !!b && !b.transparent;
}

// =========================================================
// メッシュ生成
// =========================================================
const FACES = [
  { dir:[ 1, 0, 0], shade:0.76,
    corners:[[1,0,0],[1,0,1],[1,1,1],[1,1,0]] },
  { dir:[-1, 0, 0], shade:0.72,
    corners:[[0,0,0],[0,0,1],[0,1,1],[0,1,0]] },
  { dir:[ 0, 1, 0], shade:1.00,
    corners:[[0,1,0],[1,1,0],[1,1,1],[0,1,1]] },
  { dir:[ 0,-1, 0], shade:0.45,
    corners:[[0,0,0],[0,0,1],[1,0,1],[1,0,0]] },
  { dir:[ 0, 0, 1], shade:0.86,
    corners:[[0,0,1],[1,0,1],[1,1,1],[0,1,1]] },
  { dir:[ 0, 0,-1], shade:0.68,
    corners:[[0,0,0],[1,0,0],[1,1,0],[0,1,0]] }
];

function colorToRgb(hex) {
  const n = parseInt(hex.replace("#",""), 16);
  return [((n>>16)&255)/255, ((n>>8)&255)/255, (n&255)/255];
}

function shouldDraw(currentId, neighborId) {
  if (currentId === neighborId) return false;
  const curB = BLOCKS[currentId];
  const nbB = BLOCKS[neighborId];
  if (!curB) return false;
  if (curB.transparent) {
    if (neighborId === AIR) return true;
    if (nbB && nbB.transparent) return true;
    return false;
  } else {
    return !(neighborId !== AIR && nbB && !nbB.transparent);
  }
}

function buildChunk(cx, cz) {
  const key = chunkKey(cx, cz);
  const chunk = chunks.get(key);
  if (!chunk) return;

  const opaquePos = [];
  const opaqueCol = [];
  const transPos = [];
  const transCol = [];

  const ox = cx * CHUNK_SIZE;
  const oz = cz * CHUNK_SIZE;

  for (let y=0; y<HEIGHT; y++) {
    for (let z=0; z<CHUNK_SIZE; z++) {
      for (let x=0; x<CHUNK_SIZE; x++) {
        const id = chunk.data[idx(x,y,z)];
        if (id === AIR) continue;
        const block = BLOCKS[id];
        if (!block) continue;

        const top = colorToRgb(block.top);
        const side = colorToRgb(block.side);
        const bottom = colorToRgb(block.bottom);

        const positions = block.transparent ? transPos : opaquePos;
        const colors = block.transparent ? transCol : opaqueCol;

        for (let f=0; f<FACES.length; f++) {
          const face = FACES[f];
          const nx = ox + x + face.dir[0];
          const ny = y + face.dir[1];
          const nz = oz + z + face.dir[2];
          const nb = getBlock(nx, ny, nz);
          if (!shouldDraw(id, nb)) continue;

          let base;
          if (face.dir[1] === 1) base = top;
          else if (face.dir[1] === -1) base = bottom;
          else base = side;

          const shade = face.shade;
          const r = Math.min(1, base[0] * shade);
          const g = Math.min(1, base[1] * shade);
          const b = Math.min(1, base[2] * shade);

          // slight per-vertex variation to make faces less flat
          const variation = ((hash2i(ox+x, oz+z+y*17+f) & 15) - 7) * 0.012;
          const vr = Math.max(0, Math.min(1, r + variation));
          const vg = Math.max(0, Math.min(1, g + variation));
          const vb = Math.max(0, Math.min(1, b + variation));

          const faceBase = positions.length / 3;

          for (let v=0; v<4; v++) {
            const c = face.corners[v];
            positions.push(ox + x + c[0], y + c[1], oz + z + c[2]);
            colors.push(vr, vg, vb);
          }

          // two triangles: 0,1,2 / 0,2,3
          // use non-indexed geometry for simplicity
          const p = faceBase;
          const pushTri = (a,b,c) => {
            // duplicate vertices for simple non-indexed
            const pa = p + a, pb = p + b, pc = p + c;
            const ax = positions[pa*3], ay = positions[pa*3+1], az = positions[pa*3+2];
            const bx = positions[pb*3], by = positions[pb*3+1], bz = positions[pb*3+2];
            const cx = positions[pc*3], cy = positions[pc*3+1], cz2 = positions[pc*3+2];

            const ar = colors[pa*3], ag = colors[pa*3+1], ab = colors[pa*3+2];
            const br = colors[pb*3], bg = colors[pb*3+1], bb = colors[pb*3+2];
            const cr = colors[pc*3], cg = colors[pc*3+1], cb = colors[pc*3+2];

            positions.push(ax,ay,az, bx,by,bz, cx,cy,cz2);
            colors.push(ar,ag,ab, br,bg,bb, cr,cg,cb);
          };

          // remove original 4 vertices? We'll instead not push original and build directly
        }
      }
    }
  }

  // 上のコードは非インデックス化に失敗しているため、やり直すための簡易関数
  // ここから本来のメッシュ再構築を行う
  chunk.meshOpaque?.geometry?.dispose();
  chunk.meshOpaque?.material?.dispose();
  chunk.meshTransparent?.geometry?.dispose();
  chunk.meshTransparent?.material?.dispose();
  chunk.group?.remove();

  chunk.opaquePos = opaquePos;
  chunk.opaqueCol = opaqueCol;
  chunk.transPos = transPos;
  chunk.transCol = transCol;

  const group = new THREE.Group();
  group.position.set(0,0,0);

  const oGeom = createGeometryFromQuads(opaquePos, opaqueCol);
  if (oGeom.attributes.position.count > 0) {
    chunk.meshOpaque = new THREE.Mesh(oGeom, opaqueMaterial.clone());
    chunk.meshOpaque.frustumCulled = false;
    group.add(chunk.meshOpaque);
  } else {
    oGeom.dispose();
    chunk.meshOpaque = null;
  }

  const tGeom = createGeometryFromQuads(transPos, transCol);
  if (tGeom.attributes.position.count > 0) {
    chunk.meshTransparent = new THREE.Mesh(tGeom, transparentMaterial.clone());
    chunk.meshTransparent.frustumCulled = false;
    group.add(chunk.meshTransparent);
  } else {
    tGeom.dispose();
    chunk.meshTransparent = null;
  }

  if (group.children.length) {
    chunk.group = group;
    scene.add(group);
  } else {
    chunk.group = null;
  }

  dirtyChunks.delete(key);
}

// 4頂点クッド配列を三角形に変換する関数（posは4個ずつ、colも同数）
function createGeometryFromQuads(pos4, col4) {
  const triPos = [];
  const triCol = [];

  for (let i=0; i<pos4.length; i += 12) {
    const p0 = i, p1 = i+3, p2 = i+6, p3 = i+9;

    const v0 = [pos4[p0], pos4[p0+1], pos4[p0+2]];
    const v1 = [pos4[p1], pos4[p1+1], pos4[p1+2]];
    const v2 = [pos4[p2], pos4[p2+1], pos4[p2+2]];
    const v3 = [pos4[p3], pos4[p3+1], pos4[p3+2]];

    const c0 = [col4[p0], col4[p0+1], col4[p0+2]];
    const c1 = [col4[p1], col4[p1+1], col4[p1+2]];
    const c2 = [col4[p2], col4[p2+1], col4[p2+2]];
    const c3 = [col4[p3], col4[p3+1], col4[p3+2]];

    triPos.push(...v0, ...v1, ...v2);
    triCol.push(...c0, ...c1, ...c2);
    triPos.push(...v0, ...v2, ...v3);
    triCol.push(...c0, ...c2, ...c3);
  }

  const g = new THREE.BufferGeometry();
  if (triPos.length) {
    g.setAttribute("position", new THREE.Float32BufferAttribute(triPos, 3));
    g.setAttribute("color", new THREE.Float32BufferAttribute(triCol, 3));
    g.computeVertexNormals();
  }
  return g;
}

// buildChunk内の簡易addFaceを修正するため、別のルートで再定義する
function buildChunkProper(cx, cz) {
  const key = chunkKey(cx, cz);
  const chunk = chunks.get(key);
  if (!chunk) return;

  const opaquePos = [];
  const opaqueCol = [];
  const transPos = [];
  const transCol = [];

  const ox = cx * CHUNK_SIZE;
  const oz = cz * CHUNK_SIZE;

  for (let y=0; y<HEIGHT; y++) {
    for (let z=0; z<CHUNK_SIZE; z++) {
      for (let x=0; x<CHUNK_SIZE; x++) {
        const id = chunk.data[idx(x,y,z)];
        if (id === AIR) continue;
        const block = BLOCKS[id];
        if (!block) continue;

        const top = colorToRgb(block.top);
        const side = colorToRgb(block.side);
        const bottom = colorToRgb(block.bottom);

        for (let f=0; f<FACES.length; f++) {
          const face = FACES[f];
          const nx = ox + x + face.dir[0];
          const ny = y + face.dir[1];
          const nz = oz + z + face.dir[2];
          const nb = getBlock(nx, ny, nz);
          if (!shouldDraw(id, nb)) continue;

          let base;
          if (face.dir[1] === 1) base = top;
          else if (face.dir[1] === -1) base = bottom;
          else base = side;

          const shade = face.shade;
          const variation = ((hash2i(ox+x, oz+z+y*17+f) & 15) - 7) * 0.012;

          const posArr = block.transparent ? transPos : opaquePos;
          const colArr = block.transparent ? transCol : opaqueCol;

          const v0 = [face.corners[0][0], face.corners[0][1], face.corners[0][2]];
          const v1 = [face.corners[1][0], face.corners[1][1], face.corners[1][2]];
          const v2 = [face.corners[2][0], face.corners[2][1], face.corners[2][2]];
          const v3 = [face.corners[3][0], face.corners[3][1], face.corners[3][2]];

          function pushVertex(v, i) {
            const px = ox + x + v[0];
            const py = y + v[1];
            const pz = oz + z + v[2];
            const r = Math.max(0, Math.min(1, base[0]*shade + variation));
            const g = Math.max(0, Math.min(1, base[1]*shade + variation));
            const b = Math.max(0, Math.min(1, base[2]*shade + variation));
            posArr.push(px, py, pz);
            colArr.push(r, g, b);
          }

          pushVertex(v0, 0);
          pushVertex(v1, 1);
          pushVertex(v2, 2);
          pushVertex(v3, 3);
        }
      }
    }
  }

  chunk.meshOpaque?.geometry?.dispose();
  chunk.meshTransparent?.geometry?.dispose();
  chunk.meshOpaque?.material?.dispose();
  chunk.meshTransparent?.material?.dispose();
  if (chunk.group) {
    chunk.group.traverse(o => { if(o.geometry) o.geometry.dispose(); });
    scene.remove(chunk.group);
  }

  const group = new THREE.Group();

  const oGeom = createGeometryFromQuads(opaquePos, opaqueCol);
  if (oGeom.attributes.position?.count > 0) {
    const mat = opaqueMaterial.clone();
    mat.color.setScalar(dayFactor);
    const mesh = new THREE.Mesh(oGeom, mat);
    mesh.frustumCulled = false;
    chunk.meshOpaque = mesh;
    group.add(mesh);
  } else {
    oGeom.dispose();
    chunk.meshOpaque = null;
  }

  const tGeom = createGeometryFromQuads(transPos, transCol);
  if (tGeom.attributes.position?.count > 0) {
    const mat = transparentMaterial.clone();
    mat.color.setScalar(dayFactor);
    const mesh = new THREE.Mesh(tGeom, mat);
    mesh.frustumCulled = false;
    chunk.meshTransparent = mesh;
    group.add(mesh);
  } else {
    tGeom.dispose();
    chunk.meshTransparent = null;
  }

  chunk.group = group;
  scene.add(group);
  dirtyChunks.delete(key);
}

// buildChunkは使わずbuildChunkProperを使う
const buildChunkFinal = buildChunkProper;

// =========================================================
// 木生成
// =========================================================
function generateTrees() {
  for (let x=0; x<WORLD_SIZE; x++) {
    for (let z=0; z<WORLD_SIZE; z++) {
      if (getBlock(x, 0, z) !== BEDROCK) continue;
      const h = terrainHeight(x, z);
      if (getBlock(x, h, z) !== GRASS) continue;

      const rand = hash2i(x * 7 + 13, z * 7 + 29);
      if ((rand & 0x3ff) > 22) continue; // 約2.2%
      if (h < 21 || h > 48) continue;

      const trunkH = 4 + ((rand >> 12) & 1) * 2;
      if (h + trunkH + 2 >= HEIGHT) continue;

      // 幹
      for (let y=h+1; y<=h+trunkH; y++) {
        setBlockData(x, y, z, WOOD, false);
      }

      // 葉
      const topY = h + trunkH;
      for (let dy=-2; dy<=2; dy++) {
        for (let dx=-2; dx<=2; dx++) {
          for (let dz=-2; dz<=2; dz++) {
            const wx = x + dx;
            const wy = topY + dy;
            const wz = z + dz;
            const dist2 = dx*dx + dz*dz + dy*dy*1.5;
            if (dist2 <= 7.5) {
              if (!worldInBounds(wx, wy, wz)) continue;
              if (getBlock(wx, wy, wz) === AIR) {
                setBlockData(wx, wy, wz, LEAVES, false);
              }
            }
          }
        }
      }
    }
  }

  // 木生成後に全チャンク再メッシュ
  for (let cx=0; cx<WORLD_CHUNKS; cx++) {
    for (let cz=0; cz<WORLD_CHUNKS; cz++) {
      markChunkDirty(cx, cz);
    }
  }
}

// =========================================================
// プレイヤー
// =========================================================
const player = {
  pos: new THREE.Vector3(WORLD_SIZE / 2, 40, WORLD_SIZE / 2),
  vel: new THREE.Vector3(),
  yaw: 0,
  pitch: 0,
  onGround: false,
  flying: false,
  selected: HOTBAR[0]
};

function isPlayerColliding(px = player.pos.x, py = player.pos.y, pz = player.pos.z) {
  const EPS = 0.0015;
  const minX = Math.floor(px - PLAYER_RADIUS + EPS);
  const maxX = Math.floor(px + PLAYER_RADIUS - EPS);
  const minY = Math.floor(py + EPS);
  const maxY = Math.floor(py + PLAYER_HEIGHT - EPS);
  const minZ = Math.floor(pz - PLAYER_RADIUS + EPS);
  const maxZ = Math.floor(pz + PLAYER_RADIUS - EPS);

  for (let y=minY; y<=maxY; y++) {
    for (let z=minZ; z<=maxZ; z++) {
      for (let x=minX; x<=maxX; x++) {
        if (isSolid(getBlock(x, y, z))) return true;
      }
    }
  }
  return false;
}

function isOnGround() {
  const y = Math.floor(player.pos.y - 0.01);
  const minX = Math.floor(player.pos.x - PLAYER_RADIUS + 0.001);
  const maxX = Math.floor(player.pos.x + PLAYER_RADIUS - 0.001);
  const minZ = Math.floor(player.pos.z - PLAYER_RADIUS + 0.001);
  const maxZ = Math.floor(player.pos.z + PLAYER_RADIUS - 0.001);
  for (let z=minZ; z<=maxZ; z++) {
    for (let x=minX; x<=maxX; x++) {
      if (isSolid(getBlock(x, y, z))) return true;
    }
  }
  return false;
}

function moveAxis(axis, amount) {
  if (amount === 0) return false;
  const old = player.pos[axis];
  const target = old + amount;

  const collidesAt = val => {
    const p = { x:player.pos.x, y:player.pos.y, z:player.pos.z };
    p[axis] = val;
    return isPlayerColliding(p.x, p.y, p.z);
  };

  if (!collidesAt(target)) {
    player.pos[axis] = target;
    return false;
  }

  let low = 0;
  let high = 1;
  for (let i=0; i<14; i++) {
    const mid = (low + high) / 2;
    if (!collidesAt(old + amount * mid)) low = mid;
    else high = mid;
  }

  player.pos[axis] = old + amount * low;

  // 接触位置から微小に離す
  if (axis === "y") {
    if (amount > 0) player.pos.y -= 0.002;
    else player.pos.y += 0.002;
  } else if (axis === "x") {
    if (amount > 0) player.pos.x -= 0.002;
    else player.pos.x += 0.002;
  } else {
    if (amount > 0) player.pos.z -= 0.002;
    else player.pos.z += 0.002;
  }

  if (isPlayerColliding()) {
    player.pos[axis] = old;
    return true;
  }
  return false;
}

function findSpawn() {
  const cx = WORLD_SIZE >> 1;
  const cz = WORLD_SIZE >> 1;
  for (let r=0; r<80; r++) {
    const x = cx + Math.floor(Math.cos(r*1.7) * r);
    const z = cz + Math.floor(Math.sin(r*1.7) * r);
    if (x < 0 || z < 0 || x >= WORLD_SIZE || z >= WORLD_SIZE) continue;
    const h = terrainHeight(x, z);
    for (let y=HEIGHT-1; y>1; y--) {
      if (isSolid(getBlock(x, y, z))) {
        player.pos.set(x + 0.5, y + 1.01, z + 0.5);
        return;
      }
    }
  }
  player.pos.set(WORLD_SIZE/2, 50, WORLD_SIZE/2);
}

// =========================================================
// レイキャスト
// =========================================================
function raycastVoxel(origin, direction, maxDistance = RAY_DISTANCE) {
  let x = Math.floor(origin.x);
  let y = Math.floor(origin.y);
  let z = Math.floor(origin.z);

  const dir = direction.clone().normalize();
  const stepX = dir.x > 0 ? 1 : dir.x < 0 ? -1 : 0;
  const stepY = dir.y > 0 ? 1 : dir.y < 0 ? -1 : 0;
  const stepZ = dir.z > 0 ? 1 : dir.z < 0 ? -1 : 0;

  const tDeltaX = stepX !== 0 ? Math.abs(1 / dir.x) : Infinity;
  const tDeltaY = stepY !== 0 ? Math.abs(1 / dir.y) : Infinity;
  const tDeltaZ = stepZ !== 0 ? Math.abs(1 / dir.z) : Infinity;

  let tMaxX = stepX > 0 ? (x + 1 - origin.x) / dir.x : stepX < 0 ? (x - origin.x) / dir.x : Infinity;
  let tMaxY = stepY > 0 ? (y + 1 - origin.y) / dir.y : stepY < 0 ? (y - origin.y) / dir.y : Infinity;
  let tMaxZ = stepZ > 0 ? (z + 1 - origin.z) / dir.z : stepZ < 0 ? (z - origin.z) / dir.z : Infinity;

  let normal = null;

  // スタート地点が固体なら最初の面は不確定なので、少しだけ進む
  if (isSolid(getBlock(x, y, z))) {
    x += stepX || 0;
    y += stepY || 0;
    z += stepZ || 0;
  }

  for (let i=0; i<120; i++) {
    if (x < 0 || y < 0 || z < 0 || x >= WORLD_SIZE || z >= WORLD_SIZE || y >= HEIGHT) return null;

    const id = getBlock(x, y, z);
    if (isSolid(id)) {
      return {
        x, y, z,
        id,
        normal: normal || [-Math.sign(dir.x || 0), -Math.sign(dir.y || 0), -Math.sign(dir.z || 0)]
      };
    }

    if (tMaxX < tMaxY && tMaxX < tMaxZ) {
      x += stepX;
      if (x * stepX > WORLD_SIZE) break;
      tMaxX += tDeltaX;
      if (tMaxX > maxDistance) break;
      normal = stepX > 0 ? [-1, 0, 0] : stepX < 0 ? [1, 0, 0] : [0, 0, 0];
    } else if (tMaxY < tMaxZ) {
      y += stepY;
      tMaxY += tDeltaY;
      if (tMaxY > maxDistance) break;
      normal = stepY > 0 ? [0, -1, 0] : stepY < 0 ? [0, 1, 0] : [0, 0, 0];
    } else {
      z += stepZ;
      tMaxZ += tDeltaZ;
      if (tMaxZ > maxDistance) break;
      normal = stepZ > 0 ? [0, 0, -1] : stepZ < 0 ? [0, 0, 1] : [0, 0, 0];
    }
  }

  return null;
}

// =========================================================
// 入力
// =========================================================
const keys = new Set();
let locked = false;
let leftDown = false;
let rightDown = false;
let lastAction = 0;

document.addEventListener("keydown", e => {
  if (e.code === "Space") e.preventDefault();
  keys.add(e.code);

  if (!locked) return;

  if (e.code === "KeyG") {
    player.flying = !player.flying;
    if (!player.flying) player.vel.y = 0;
  }

  const num = parseInt(e.key, 10);
  if (num >= 1 && num <= 9) {
    selectedHotbar = num - 1;
    updateHotbar();
  }

  if (e.code === "KeyF3") {
    e.preventDefault();
  }
});

document.addEventListener("keyup", e => keys.delete(e.code));
window.addEventListener("blur", () => keys.clear());

canvas.addEventListener("mousedown", e => {
  if (!locked) return;
  if (e.button === 0) leftDown = true;
  if (e.button === 2) rightDown = true;
  if (e.button === 1) {
    const hit = getTarget();
    if (hit) {
      const idx = HOTBAR.indexOf(hit.id);
      if (idx >= 0) selectedHotbar = idx;
      else HOTBAR[7] = hit.id; // 未登録ブロックは念のため
      updateHotbar();
    }
    e.preventDefault();
  }
});

document.addEventListener("mouseup", e => {
  if (e.button === 0) leftDown = false;
  if (e.button === 2) rightDown = false;
});

document.addEventListener("contextmenu", e => e.preventDefault());

canvas.addEventListener("wheel", e => {
  if (!locked) return;
  e.preventDefault();
  selectedHotbar = (selectedHotbar + (e.deltaY > 0 ? 1 : -1) + HOTBAR.length) % HOTBAR.length;
  updateHotbar();
}, { passive:false });

document.addEventListener("mousemove", e => {
  if (!locked) return;
  player.yaw -= e.movementX * 0.0023;
  player.pitch -= e.movementY * 0.0023;
  player.pitch = Math.max(-Math.PI / 2 + 0.01, Math.min(Math.PI / 2 - 0.01, player.pitch));
});

document.addEventListener("pointerlockchange", () => {
  locked = document.pointerLockElement === canvas;
});

canvas.addEventListener("click", () => {
  if (!locked && loaded) canvas.requestPointerLock();
});

document.getElementById("play").addEventListener("click", () => {
  document.getElementById("start").style.display = "none";
  canvas.requestPointerLock();
});

// =========================================================
// UI
// =========================================================
function updateHotbar() {
  const hotbar = document.getElementById("hotbar");
  hotbar.innerHTML = "";
  HOTBAR.forEach((id, i) => {
    const div = document.createElement("div");
    div.className = "slot" + (i === selectedHotbar ? " sel" : "");
    div.innerHTML = `<span class="idx">${i+1}</span><div style="color:${BLOCKS[id].top}">${BLOCKS[id].name}</div>`;
    hotbar.appendChild(div);
  });
}

updateHotbar();

// =========================================================
// 初期ロード
// =========================================================
let loaded = false;
let dayFactor = 1;

async function initialLoad() {
  const loading = document.getElementById("loading");

  // 全チャンクデータ生成
  for (let cx=0; cx<WORLD_CHUNKS; cx++) {
    for (let cz=0; cz<WORLD_CHUNKS; cz++) {
      generateChunk(cx, cz);
    }
    loading.textContent = "地形生成中… " + Math.round((cx+1)/WORLD_CHUNKS*50) + "%";
    await frame();
  }

  loading.textContent = "木生成中…";
  await frame();
  generateTrees();

  loading.textContent = "メッシュ生成中…";
  let done = 0;
  let total = WORLD_CHUNKS * WORLD_CHUNKS;

  for (let cx=0; cx<WORLD_CHUNKS; cx++) {
    for (let cz=0; cz<WORLD_CHUNKS; cz++) {
      buildChunkFinal(cx, cz);
      done++;
      if (done % 4 === 0) {
        loading.textContent = "メッシュ生成中… " + Math.round(done/total*100) + "%";
        await frame();
      }
    }
  }

  findSpawn();

  // シーンが暗くないか確認
  opaqueMaterial.color.setScalar(dayFactor);
  transparentMaterial.color.setScalar(dayFactor);

  loading.style.display = "none";
  loaded = true;
}

function frame() {
  return new Promise(r => requestAnimationFrame(r));
}

// =========================================================
// アクション
// =========================================================
function getTarget() {
  const dir = new THREE.Vector3();
  camera.getWorldDirection(dir);
  return raycastVoxel(camera.position.clone(), dir, RAY_DISTANCE);
}

function canPlace(x, y, z) {
  if (!worldInBounds(x, y, z)) return false;
  if (isSolid(getBlock(x, y, z))) return false;
  if (!isSolid(player.selected)) return false;

  // プレイヤーを塞がない
  const EPS = 0.001;
  const minX = Math.floor(x);
  const maxX = Math.floor(x + 1 - EPS);
  const minY = Math.floor(y);
  const maxY = Math.floor(y + 1 - EPS);
  const minZ = Math.floor(z);
  const maxZ = Math.floor(z + 1 - EPS);

  const px = player.pos.x, py = player.pos.y, pz = player.pos.z;
  const rx = Math.floor(px - PLAYER_RADIUS + EPS);
  const cx = Math.floor(px + PLAYER_RADIUS - EPS);
  const ry = Math.floor(py + EPS);
  const cy = Math.floor(py + PLAYER_HEIGHT - EPS);
  const rz = Math.floor(pz - PLAYER_RADIUS + EPS);
  const cz = Math.floor(pz + PLAYER_RADIUS - EPS);

  return !(rx <= maxX && cx >= minX && ry <= maxY && cy >= minY && rz <= maxZ && cz >= minZ);
}

function handleActions(now) {
  const hit = getTarget();

  if (hit) {
    highlightBox.position.set(hit.x + 0.5, hit.y + 0.5, hit.z + 0.5);
    highlightBox.visible = true;
  } else {
    highlightBox.visible = false;
  }

  if (!locked || !hit) return;

  const actionGap = 150;
  if (leftDown && now - lastAction > actionGap) {
    if (hit.id !== BEDROCK) {
      setBlockData(hit.x, hit.y, hit.z, AIR, true);
      lastAction = now;
    }
  }

  if (rightDown && now - lastAction > actionGap) {
    const nx = hit.x + hit.normal[0];
    const ny = hit.y + hit.normal[1];
    const nz = hit.z + hit.normal[2];
    if (canPlace(nx, ny, nz)) {
      setBlockData(nx, ny, nz, player.selected, true);
      lastAction = now;
    }
  }
}

// =========================================================
// 更新
// =========================================================
let lastTime = performance.now();

function update(dt) {
  const moveDir = new THREE.Vector3();

  if (keys.has("KeyW")) moveDir.z -= 1;
  if (keys.has("KeyS")) moveDir.z += 1;
  if (keys.has("KeyA")) moveDir.x -= 1;
  if (keys.has("KeyD")) moveDir.x += 1;

  moveDir.applyAxisAngle(new THREE.Vector3(0,1,0), player.yaw);

  const speed = player.flying
    ? FLY_SPEED
    : (keys.has("ShiftLeft") || keys.has("ShiftRight") ? SPRINT_SPEED : WALK_SPEED);

  const dx = moveDir.x * speed * dt;
  const dz = moveDir.z * speed * dt;

  if (!player.flying) {
    player.vel.y -= GRAVITY * dt;
    if (keys.has("Space") && isOnGround()) {
      player.vel.y = JUMP_V;
    }
    if (player.vel.y < -40) player.vel.y = -40;

    const dy = player.vel.y * dt;
    const hitY = moveAxis("y", dy);
    if (hitY) {
      player.vel.y = 0;
    }

    moveAxis("x", dx);
    moveAxis("z", dz);

    player.onGround = isOnGround();
  } else {
    let dy = 0;
    if (keys.has("Space")) dy += 1;
    if (keys.has("ShiftLeft") || keys.has("ShiftRight")) dy -= 1;
    moveAxis("y", dy * FLY_SPEED * dt);
    moveAxis("x", dx);
    moveAxis("z", dz);
    player.vel.y = 0;
  }

  camera.position.set(player.pos.x, player.pos.y + PLAYER_EYE, player.pos.z);
  camera.rotation.y = player.yaw;
  camera.rotation.x = player.pitch;

  // 汚れたチャンクを少量ずつ再生成
  let rebuilt = 0;
  const maxRebuildPerFrame = 3;
  for (const key of dirtyChunks) {
    if (rebuilt >= maxRebuildPerFrame) break;
    const [cx, cz] = key.split("|").map(Number);
    buildChunkFinal(cx, cz);
    rebuilt++;
  }

  // 昼夜
  dayFactor = 0.34 + 0.66 * Math.max(0, Math.sin(performance.now() * 0.00012));
  const sky = new THREE.Color().lerpColors(
    new THREE.Color(0x0e1726),
    new THREE.Color(0x87ceeb),
    Math.max(0, dayFactor - 0.18) / 0.82
  );
  scene.fog.color.copy(sky);
  scene.background = sky;

  scene.traverse(o => {
    if (o.isMesh && o.material && o.material.color) {
      // 各チャンクマテリアルの色だけ更新
      if (o.material.vertexColors) {
        o.material.color.setScalar(dayFactor);
      }
    }
  });

  document.getElementById("coords").textContent =
    `XYZ: ${player.pos.x.toFixed(1)}, ${player.pos.y.toFixed(1)}, ${player.pos.z.toFixed(1)} | ${player.flying ? "FLY" : "WALK"}`;
}

function render() {
  renderer.render(scene, camera);
}

function animate(now) {
  const raw = (now - lastTime) / 1000;
  lastTime = now;
  const dt = Math.min(raw, 0.05);

  if (loaded) {
    update(dt);
    handleActions(now);
    render();
  }

  requestAnimationFrame(animate);
}

// =========================================================
// リサイズ
// =========================================================
window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// =========================================================
// 起動
// =========================================================
camera.position.set(player.pos.x, player.pos.y + PLAYER_EYE, player.pos.z);
requestAnimationFrame(animate);
initialLoad();
</script>
</body>
</html>
```