以下、単一の HTML ファイルだけで動く **マイクラ風 3D 箱庭ゲーム** です。

## 遊び方
- クリックでマウス操作開始（Escで解除）
- `WASD`: 移動
- `マウス左`: ブロック破壊
- `マウス右`: ブロック設置
- `1〜9`: ブロック選択
- `マウスホイール`: ブロック切り替え
- `Space`: ジャンプ
- `F`: 飛行切替
- `Shift`: 飛行中に降下 / 着地時に忍び足
- `Ctrl + S`: ワールドをブラウザに保存（自動読み込み）
- `Ctrl + R`: 再読み込みで保存データから復元
- スタート画面の「新しいワールド」で初期化

そのまま `minecraft.html` などに保存してブラウザで開けば遊べます。

```html
<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>マイクラ風 3D 箱庭</title>
<style>
  html, body {
    margin: 0;
    padding: 0;
    overflow: hidden;
    background: #000;
    font-family: "Segoe UI", "Hiragino Kaku Gothic ProN", "Noto Sans JP", sans-serif;
    color: #fff;
    -webkit-user-select: none;
    user-select: none;
    touch-action: none;
  }

  canvas {
    display: block;
    width: 100vw;
    height: 100vh;
    cursor: crosshair;
  }

  #overlay {
    position: fixed;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(180deg, rgba(12,24,40,.82), rgba(5,10,16,.88));
    z-index: 20;
    backdrop-filter: blur(5px);
  }

  #panel {
    width: min(920px, calc(100vw - 24px));
    max-height: calc(100vh - 24px);
    overflow: auto;
    background: rgba(15, 24, 34, .92);
    border: 2px solid rgba(255,255,255,.12);
    border-radius: 18px;
    padding: 22px 26px;
    box-shadow: 0 18px 80px rgba(0,0,0,.45);
  }

  #panel h1 {
    margin: 0 0 8px;
    font-size: clamp(26px, 4vw, 42px);
    letter-spacing: .04em;
  }

  #panel p {
    color: #c8d4e2;
    line-height: 1.7;
  }

  .buttons {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 18px;
  }

  button {
    appearance: none;
    border: 0;
    border-radius: 12px;
    padding: 12px 18px;
    font-size: 16px;
    font-weight: 800;
    color: #05101a;
    background: linear-gradient(180deg, #7ee081, #44b45f);
    cursor: pointer;
    box-shadow: 0 4px 0 rgba(0,0,0,.25);
  }

  button.secondary {
    background: linear-gradient(180deg, #85b3ff, #4d77ff);
    color: white;
  }

  button.danger {
    background: linear-gradient(180deg, #ff9b9b, #e05656);
    color: white;
  }

  #ui {
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 10;
  }

  #crosshair {
    position: fixed;
    left: 50%;
    top: 50%;
    width: 22px;
    height: 22px;
    transform: translate(-50%, -50%);
    opacity: .92;
  }

  #crosshair:before,
  #crosshair:after {
    content: "";
    position: absolute;
    left: 50%;
    top: 50%;
    background: #fff;
    box-shadow: 0 0 3px rgba(0,0,0,.85);
    transform: translate(-50%, -50%);
  }

  #crosshair:before {
    width: 2px;
    height: 18px;
  }

  #crosshair:after {
    width: 18px;
    height: 2px;
  }

  #hotbar {
    position: fixed;
    bottom: 16px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: 6px;
    padding: 8px;
    border-radius: 14px;
    background: rgba(10,14,20,.46);
    border: 1px solid rgba(255,255,255,.12);
  }

  .slot {
    width: 46px;
    height: 46px;
    border-radius: 9px;
    border: 2px solid rgba(255,255,255,.28);
    background: rgba(0,0,0,.28);
    display: grid;
    place-items: center;
    font-size: 11px;
    font-weight: 800;
    text-shadow: 0 1px 2px #000;
    color: #fff;
    position: relative;
  }

  .slot.selected {
    border-color: #fff;
    box-shadow: 0 0 0 3px rgba(255,255,255,.22), inset 0 0 18px rgba(255,255,255,.16);
    transform: translateY(-4px);
  }

  .slot .num {
    position: absolute;
    top: 2px;
    left: 4px;
    font-size: 9px;
    opacity: .72;
  }

  .blockIcon {
    width: 28px;
    height: 28px;
    border-radius: 5px;
    box-shadow: inset 0 0 0 1px rgba(0,0,0,.25), 0 2px 5px rgba(0,0,0,.35);
  }

  #info {
    position: fixed;
    top: 12px;
    left: 12px;
    font-size: 13px;
    line-height: 1.45;
    color: rgba(255,255,255,.88);
    text-shadow: 0 1px 3px #000;
    background: rgba(0,0,0,.22);
    padding: 10px 12px;
    border-radius: 12px;
    max-width: 44vw;
  }

  #savedToast {
    position: fixed;
    right: 16px;
    bottom: 82px;
    padding: 10px 14px;
    border-radius: 12px;
    background: rgba(20, 110, 58, .88);
    color: #fff;
    font-weight: 800;
    opacity: 0;
    transform: translateY(8px);
    transition: .22s ease;
    z-index: 30;
    pointer-events: none;
  }

  #savedToast.show {
    opacity: 1;
    transform: translateY(0);
  }
</style>
</head>
<body>
<div id="ui">
  <div id="crosshair"></div>
  <div id="hotbar"></div>
  <div id="info"></div>
</div>

<div id="savedToast">保存しました</div>

<div id="overlay">
  <div id="panel">
    <h1>🧱 マイクラ風 3D 箱庭</h1>
    <p>
      WebGL / Three.js で作った、ブラウザで動く小さなボクセルワールドです。<br>
      クリックすると一人称視点で操作できます。<br><br>
      <b>操作</b><br>
      クリック: ゲーム開始 / 左クリック破壊 / 右クリック設置<br>
      WASD: 移動 / Space: ジャンプ / Shift: 忍び足・飛行で降下<br>
      1〜9: ブロック選択 / ホイール: 切り替え<br>
      F: 飛行切り替え / Esc: 視点解除<br>
      Ctrl+S: 保存 / Ctrl+R: 再読み込みで復元
    </p>
    <div class="buttons">
      <button id="startBtn">ゲーム開始</button>
      <button id="resetBtn" class="danger">新しいワールド</button>
    </div>
  </div>
</div>

<script type="module">
import * as THREE from "https://unpkg.com/three@0.160.0/build/three.module.js";

/* =========================
   設定
========================= */
const TILE = 64;
const ATLAS_COLS = 8;
const ATLAS_ROWS = 8;

const WORLD_X = 64;
const WORLD_Y = 64;
const WORLD_Z = 64;
const CHUNK = 16;

const PLAYER_HEIGHT = 1.8;
const PLAYER_HALF_WIDTH = 0.32;
const EYE_HEIGHT = 1.62;

const GRAVITY = 22;
const JUMP_SPEED = 8.2;
const WALK_SPEED = 4.6;
const SNEAK_SPEED = 1.8;
const SPRINT_SPEED = 7.4;
const FLY_SPEED = 10.5;

const SAVE_KEY = "minecraft_like_voxel_world_v1";
const WATER_LEVEL = 9;

/* ブロックID */
const AIR = 0;
const GRASS = 1;
const DIRT = 2;
const STONE = 3;
const SAND = 4;
const LOG = 5;
const LEAVES = 6;
const PLANKS = 7;
const GLASS = 8;
const BRICK = 9;
const WATER = 10;
const COBBLE = 11;
const BEDROCK = 12;

const BLOCKS = {
  [GRASS]:  { name: "草",     tiles: { top: 0, side: 1, bottom: 2 } },
  [DIRT]:   { name: "土",     tiles: 2 },
  [STONE]:  { name: "石",     tiles: 3 },
  [SAND]:   { name: "砂",     tiles: 4 },
  [LOG]:    { name: "原木",   tiles: { top: 5, side: 6, bottom: 5 } },
  [LEAVES]: { name: "葉",     tiles: 7 },
  [PLANKS]: { name: "板",     tiles: 8 },
  [GLASS]:  { name: "ガラス", tiles: 9, transparent: true },
  [BRICK]:  { name: "レンガ", tiles: 10 },
  [WATER]:  { name: "水",     tiles: 11, transparent: true },
  [COBBLE]: { name: "丸石",   tiles: 12 },
  [BEDROCK]:{ name: "基盤",   tiles: 13, unbreakable: true }
};

const HOTBAR = [GRASS, DIRT, STONE, COBBLE, SAND, LOG, PLANKS, GLASS, WATER];

/* =========================
   Three.js 初期化
========================= */
const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x75b7ff);
scene.fog = new THREE.Fog(0x75b7ff, 42, 130);

const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.05, 500);
camera.rotation.order = "YXZ";

const hemi = new THREE.HemisphereLight(0xbddfff, 0x775d3c, 0.75);
scene.add(hemi);

const sun = new THREE.DirectionalLight(0xfff2d5, 1.05);
sun.position.set(45, 90, 25);
scene.add(sun);

const ambient = new THREE.AmbientLight(0xffffff, 0.18);
scene.add(ambient);

/* 雲 */
const cloudTexture = createCloudTexture();
const cloudGeo = new THREE.PlaneGeometry(260, 260);
const cloudMat = new THREE.MeshBasicMaterial({
  map: cloudTexture,
  transparent: true,
  opacity: 0.58,
  depthWrite: false,
  side: THREE.DoubleSide
});
const clouds = new THREE.Mesh(cloudGeo, cloudMat);
clouds.rotation.x = -Math.PI / 2;
clouds.position.set(WORLD_X / 2, 52, WORLD_Z / 2);
scene.add(clouds);

/* =========================
   テクスチャ生成
========================= */
const atlasTexture = createAtlasTexture();

function createAtlasTexture() {
  const c = document.createElement("canvas");
  c.width = TILE * ATLAS_COLS;
  c.height = TILE * ATLAS_ROWS;
  const ctx = c.getContext("2d");

  for (let i = 0; i < 16; i++) {
    drawTile(ctx, i, tilePixel);
  }

  const tex = new THREE.CanvasTexture(c);
  tex.magFilter = THREE.NearestFilter;
  tex.minFilter = THREE.NearestFilter;
  tex.generateMipmaps = false;
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

function drawTile(ctx, tileIndex, pixelFn) {
  const tx = (tileIndex % ATLAS_COLS) * TILE;
  const ty = Math.floor(tileIndex / ATLAS_COLS) * TILE;
  const img = ctx.createImageData(TILE, TILE);

  for (let y = 0; y < TILE; y++) {
    for (let x = 0; x < TILE; x++) {
      const idx = (y * TILE + x) * 4;
      const px = pixelFn(tileIndex, x, y);
      img.data[idx] = px[0];
      img.data[idx + 1] = px[1];
      img.data[idx + 2] = px[2];
      img.data[idx + 3] = px[3] === undefined ? 255 : px[3];
    }
  }

  ctx.putImageData(img, tx, ty);
}

function tilePixel(tile, x, y) {
  const n = hash01(x, y, tile);
  const m = hash01(x * 0.5 + 17, y * 0.5 + 31, tile + 99);

  if (tile === 0) {
    // 草上面
    const g = 135 + n * 55;
    return [
      55 + n * 28,
      Math.min(235, g),
      45 + m * 22
    ];
  }

  if (tile === 1) {
    // 草横面
    if (y < 10) {
      return [58 + n * 24, 150 + n * 60, 50 + m * 22];
    }
    if (y < 17 && hash01(x, y, 111) < 0.45) {
      return [65 + n * 22, 142 + n * 48, 52 + m * 20];
    }
    return dirtPixels(x, y, 2);
  }

  if (tile === 2) {
    return dirtPixels(x, y, tile);
  }

  if (tile === 3) {
    // 石
    const base = 130 + n * 25;
    const crack = hash01(Math.floor(x / 2), Math.floor(y / 2), 303);
    const c = crack < 0.14 ? -45 : 0;
    return [base + c, base + c, base + 4 + c];
  }

  if (tile === 4) {
    // 砂
    const base = 215 + n * 22;
    return [base, base - 18, base - 85 + m * 22];
  }

  if (tile === 5) {
    // 原木上面：年輪
    const dx = x - TILE / 2;
    const dy = y - TILE / 2;
    const r = Math.sqrt(dx * dx + dy * dy);
    const ring = Math.floor(r / 7) % 2;
    const base = ring ? 162 : 190;
    const noise = n * 18;
    return [base - 32 + noise, base - 72 + noise, base - 118 + noise];
  }

  if (tile === 6) {
    // 原木横面：樹皮
    const stripe = Math.sin(x * 0.75) * 0.5 + 0.5;
    const base = 108 + stripe * 30 + n * 18;
    return [base, base - 32, base - 78];
  }

  if (tile === 7) {
    // 葉
    const dark = hash01(Math.floor(x / 3), Math.floor(y / 3), 707);
    const base = 70 + dark * 82 + n * 24;
    return [
      Math.max(20, base - 22),
      Math.min(235, base),
      Math.max(18, base - 50)
    ];
  }

  if (tile === 8) {
    // 板
    const plankY = Math.floor(y / 16) % 2;
    const seam = (x + plankY * 8) % 32 < 1 || y % 16 < 1;
    if (seam) return [105 + n * 12, 74 + n * 10, 42 + n * 8];
    const base = 165 + n * 26;
    return [base + 8, base - 22, base - 78];
  }

  if (tile === 9) {
    // ガラス
    const border = x < 3 || y < 3 || x >= TILE - 3 || y >= TILE - 3;
    if (border) return [220, 246, 255, 190];
    if (Math.abs(x - y) < 3) return [255, 255, 255, 90];
    return [160, 225, 255, 40];
  }

  if (tile === 10) {
    // レンガ
    const row = Math.floor(y / 12);
    const offset = row % 2 ? 8 : 0;
    const seamX = ((x + offset) % 16) < 2;
    const seamY = (y % 12) < 2;
    if (seamX || seamY) return [222, 210, 202];
    return [150 + n * 28, 52 + n * 18, 42 + m * 14];
  }

  if (tile === 11) {
    // 水
    const wave = Math.sin((x + y * 0.6) * 0.35) * 18;
    return [
      45 + n * 18 + wave * 0.2,
      120 + n * 28 + wave,
      210 + n * 30 + wave * 0.4,
      230
    ];
  }

  if (tile === 12) {
    // 丸石
    const cell = hash01(Math.floor(x / 5), Math.floor(y / 5), 1212);
    const base = 112 + cell * 46 + n * 14;
    return [base, base, base + 3];
  }

  if (tile === 13) {
    // 基盤
    const base = 52 + hash01(Math.floor(x / 4), Math.floor(y / 4), 1313) * 60;
    return [base, base, base + 8];
  }

  // 予備タイル
  return [0, 255, 0];
}

function dirtPixels(x, y, tile) {
  const noise = hash01(Math.floor(x / 2), Math.floor(y / 2), tile * 17);
  const base = 128 + noise * 28;
  return [base, base - 34, base - 76];
}

function hash01(x, y, seed = 0) {
  let n = Math.sin((x + 0.5) * 12.9898 + (y + 0.5) * 78.233 + seed * 37.719) * 43758.5453;
  return n - Math.floor(n);
}

function createCloudTexture() {
  const size = 256;
  const c = document.createElement("canvas");
  c.width = c.height = size;
  const ctx = c.getContext("2d");
  const img = ctx.createImageData(size, size);

  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      let v = 0;
      let amp = 1;
      let freq = 0.025;
      for (let o = 0; o < 4; o++) {
        v += noise2(x * freq, y * freq) * amp;
        amp *= 0.5;
        freq *= 2;
      }
      v = (v + 1) * 0.5;
      const a = Math.max(0, Math.min(1, (v - 0.48) * 3.5));
      const i = (y * size + x) * 4;
      img.data[i] = 255;
      img.data[i + 1] = 255;
      img.data[i + 2] = 255;
      img.data[i + 3] = a * 220;
    }
  }

  ctx.putImageData(img, 0, 0);
  const tex = new THREE.CanvasTexture(c);
  tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
  tex.repeat.set(2, 2);
  return tex;
}

/* =========================
   ワールドデータ
========================= */
const blockData = new Uint8Array(WORLD_X * WORLD_Y * WORLD_Z);

function blockIndex(x, y, z) {
  return (y * WORLD_Z + z) * WORLD_X + x;
}

function getBlock(x, y, z) {
  if (x < 0 || x >= WORLD_X) return STONE;
  if (z < 0 || z >= WORLD_Z) return STONE;
  if (y < 0) return STONE;
  if (y >= WORLD_Y) return AIR;
  return blockData[blockIndex(x, y, z)];
}

function setBlock(x, y, z, t) {
  if (x < 0 || x >= WORLD_X || y < 0 || y >= WORLD_Y || z < 0 || z >= WORLD_Z) return false;
  const i = blockIndex(x, y, z);
  const old = blockData[i];
  if (old === t) return false;
  blockData[i] = t;
  markChunkDirtyAt(x, z);
  return true;
}

function isTransparentType(type) {
  return !!BLOCKS[type] && !!BLOCKS[type].transparent;
}

function isOpaqueType(type) {
  return type !== AIR && !isTransparentType(type);
}

/* =========================
   チャンクレンダリング
========================= */
const chunksX = WORLD_X / CHUNK;
const chunksZ = WORLD_Z / CHUNK;
const chunks = [];

const solidMaterial = new THREE.MeshLambertMaterial({
  map: atlasTexture,
  vertexColors: true
});

const transparentMaterial = new THREE.MeshLambertMaterial({
  map: atlasTexture,
  vertexColors: true,
  transparent: true,
  depthWrite: false,
  side: THREE.DoubleSide
});

const FACES = [
  {
    // -X 西
    dir: [-1, 0, 0],
    brightness: 0.72,
    corners: [[0,1,0], [0,0,0], [0,1,1], [0,0,1]],
    uvs: [[0,1], [0,0], [1,1], [1,0]]
  },
  {
    // +X 東
    dir: [1, 0, 0],
    brightness: 0.86,
    corners: [[1,1,1], [1,0,1], [1,1,0], [1,0,0]],
    uvs: [[1,1], [1,0], [0,1], [0,0]]
  },
  {
    // -Y 下
    dir: [0, -1, 0],
    brightness: 0.42,
    corners: [[1,0,1], [0,0,1], [1,0,0], [0,0,0]],
    uvs: [[1,0], [0,0], [1,1], [0,1]]
  },
  {
    // +Y 上
    dir: [0, 1, 0],
    brightness: 1.0,
    corners: [[0,1,1], [1,1,1], [0,1,0], [1,1,0]],
    uvs: [[0,1], [1,1], [0,0], [1,0]]
  },
  {
    // -Z 北
    dir: [0, 0, -1],
    brightness: 0.78,
    corners: [[1,1,0], [0,1,0], [1,0,0], [0,0,0]],
    uvs: [[1,1], [0,1], [1,0], [0,0]]
  },
  {
    // +Z 南
    dir: [0, 0, 1],
    brightness: 0.82,
    corners: [[0,1,1], [1,1,1], [0,0,1], [1,0,1]],
    uvs: [[0,1], [1,1], [0,0], [1,0]]
  }
];

function initChunks() {
  for (let cz = 0; cz < chunksZ; cz++) {
    for (let cx = 0; cx < chunksX; cx++) {
      const solid = new THREE.Mesh(new THREE.BufferGeometry(), solidMaterial);
      solid.frustumCulled = true;

      const trans = new THREE.Mesh(new THREE.BufferGeometry(), transparentMaterial);
      trans.frustumCulled = true;

      scene.add(solid);
      scene.add(trans);

      chunks.push({
        cx,
        cz,
        solid,
        trans,
        dirty: true
      });
    }
  }
}

function chunkAt(cx, cz) {
  if (cx < 0 || cx >= chunksX || cz < 0 || cz >= chunksZ) return null;
  return chunks[cz * chunksX + cx];
}

function markChunkDirtyAt(x, z) {
  const cx = Math.floor(x / CHUNK);
  const cz = Math.floor(z / CHUNK);

  chunkAt(cx, cz)?.dirty = true;

  const lx = x % CHUNK;
  const lz = z % CHUNK;

  if (lx === 0) chunkAt(cx - 1, cz)?.dirty = true;
  if (lx === CHUNK - 1) chunkAt(cx + 1, cz)?.dirty = true;
  if (lz === 0) chunkAt(cx, cz - 1)?.dirty = true;
  if (lz === CHUNK - 1) chunkAt(cx, cz + 1)?.dirty = true;
}

function markAllDirty() {
  for (const c of chunks) c.dirty = true;
}

function rebuildDirtyChunks(limit = 3) {
  let count = 0;
  for (const chunk of chunks) {
    if (!chunk.dirty) continue;
    rebuildChunk(chunk);
    chunk.dirty = false;
    count++;
    if (count >= limit) break;
  }
}

function rebuildChunk(chunk) {
  const x0 = chunk.cx * CHUNK;
  const z0 = chunk.cz * CHUNK;

  const solid = makeGeometryArrays();
  const trans = makeGeometryArrays();

  for (let y = 0; y < WORLD_Y; y++) {
    for (let z = z0; z < z0 + CHUNK; z++) {
      for (let x = x0; x < x0 + CHUNK; x++) {
        const type = getBlock(x, y, z);
        if (type === AIR) continue;

        const def = BLOCKS[type];
        if (!def) continue;

        const target = isTransparentType(type) ? trans : solid;

        for (let faceIndex = 0; faceIndex < 6; faceIndex++) {
          const face = FACES[faceIndex];
          const nx = x + face.dir[0];
          const ny = y + face.dir[1];
          const nz = z + face.dir[2];

          let neighbor;
          if (nx < 0 || nx >= WORLD_X || nz < 0 || nz >= WORLD_Z || ny < 0) {
            neighbor = STONE; // 外側は壁扱いにして穴を見せない
          } else if (ny >= WORLD_Y) {
            neighbor = AIR;
          } else {
            neighbor = blockData[blockIndex(nx, ny, nz)];
          }

          if (isTransparentType(type)) {
            if (isOpaqueType(neighbor)) continue;
            if (neighbor === type) continue;
          } else {
            if (isOpaqueType(neighbor)) continue;
          }

          const tile = getTileForBlock(type, faceIndex);
          addFace(target, x, y, z, faceIndex, tile, face.brightness);
        }
      }
    }
  }

  applyGeometry(chunk.solid, solid);
  applyGeometry(chunk.trans, trans);
}

function makeGeometryArrays() {
  return {
    positions: [],
    normals: [],
    colors: [],
    uvs: [],
    indices: []
  };
}

function addFace(arrs, x, y, z, faceIndex, tile, brightness) {
  const face = FACES[faceIndex];
  const start = arrs.positions.length / 3;

  for (let i = 0; i < 4; i++) {
    const c = face.corners[i];
    const uv = face.uvs[i];

    arrs.positions.push(x + c[0], y + c[1], z + c[2]);

    arrs.normals.push(face.dir[0], face.dir[1], face.dir[2]);

    const b = brightness * (0.92 + hash01(x + c[0] * 0.1, z + c[2] * 0.1, y) * 0.08);
    arrs.colors.push(b, b, b);

    const col = tile % ATLAS_COLS;
    const row = Math.floor(tile / ATLAS_COLS);

    const pad = 0.5 / TILE;
    const uu = uv[0] === 1 ? 1 - pad : pad;
    const vv = uv[1] === 1 ? 1 - pad : pad;

    const u = (col + uu) / ATLAS_COLS;
    const v = 1 - (row + vv) / ATLAS_ROWS;

    arrs.uvs.push(u, v);
  }

  arrs.indices.push(
    start, start + 1, start + 2,
    start + 2, start + 1, start + 3
  );
}

function applyGeometry(mesh, arrs) {
  const old = mesh.geometry;
  old.dispose();

  if (arrs.positions.length === 0) {
    mesh.geometry = new THREE.BufferGeometry();
    mesh.visible = false;
    return;
  }

  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.Float32BufferAttribute(arrs.positions, 3));
  geo.setAttribute("normal", new THREE.Float32BufferAttribute(arrs.normals, 3));
  geo.setAttribute("color", new THREE.Float32BufferAttribute(arrs.colors, 3));
  geo.setAttribute("uv", new THREE.Float32BufferAttribute(arrs.uvs, 2));
  geo.setIndex(arrs.indices);
  geo.computeBoundingSphere();

  mesh.geometry = geo;
  mesh.visible = true;
}

function getTileForBlock(type, faceIndex) {
  const def = BLOCKS[type];
  if (typeof def.tiles === "number") return def.tiles;
  if (faceIndex === 3) return def.tiles.top;
  if (faceIndex === 2) return def.tiles.bottom;
  return def.tiles.side;
}

/* =========================
   テレイン生成
========================= */
let currentSeed = Math.floor(Math.random() * 1e9);

function seededNoise2D(x, z, seed = currentSeed) {
  const x0 = Math.floor(x);
  const z0 = Math.floor(z);
  const xf = x - x0;
  const zf = z - z0;

  const v00 = valueNoise(x0, z0, seed);
  const v10 = valueNoise(x0 + 1, z0, seed);
  const v01 = valueNoise(x0, z0 + 1, seed);
  const v11 = valueNoise(x0 + 1, z0 + 1, seed);

  const u = fade(xf);
  const v = fade(zf);

  return lerp(
    lerp(v00, v10, u),
    lerp(v01, v11, u),
    v
  );
}

function valueNoise(x, z, seed) {
  let n = x * 374761393 + z * 668265263 + seed * 1013904223;
  n = (n ^ (n >> 13)) * 1274126177;
  n = n ^ (n >> 16);
  return (n >>> 0) / 4294967295;
}

function fade(t) {
  return t * t * t * (t * (t * 6 - 15) + 10);
}

function lerp(a, b, t) {
  return a + (b - a) * t;
}

function fbm2(x, z, octaves = 4, seed = currentSeed) {
  let total = 0;
  let amp = 1;
  let freq = 1;
  let max = 0;

  for (let i = 0; i < octaves; i++) {
    total += seededNoise2D(x * freq, z * freq, seed + i * 917) * amp;
    max += amp;
    amp *= 0.5;
    freq *= 2;
  }

  return total / max;
}

function generateWorld(seed = currentSeed) {
  currentSeed = seed;
  blockData.fill(AIR);

  for (let x = 0; x < WORLD_X; x++) {
    for (let z = 0; z < WORLD_Z; z++) {
      const n1 = fbm2(x * 0.035, z * 0.035, 5, seed + 1);
      const n2 = fbm2(x * 0.011 + 100, z * 0.011 + 100, 3, seed + 2);
      const ridge = Math.abs(seededNoise2D(x * 0.022, z * 0.022, seed + 3) * 2 - 1);

      let h = Math.floor(
        5 +
        n1 * 16 +
        n2 * 11 +
        Math.pow(ridge, 3.0) * 13
      );

      h = Math.max(2, Math.min(WORLD_Y - 12, h));

      const surfaceNearWater = h <= WATER_LEVEL + 1;

      for (let y = 0; y <= h; y++) {
        let type = STONE;

        if (y === 0) type = BEDROCK;
        else if (y >= h - 2) type = DIRT;

        if (y === h) {
          type = surfaceNearWater ? SAND : GRASS;
        }

        // 浅い洞窟風を少しだけ
        if (y > 1 && y < h - 3) {
          const cave = fbm2((x + 300) * 0.07, (z + 200 + y * 1.4) * 0.07, 3, seed + 42);
          if (cave > 0.72) continue;
        }

        blockData[blockIndex(x, y, z)] = type;
      }

      // 水
      for (let y = h + 1; y <= WATER_LEVEL; y++) {
        blockData[blockIndex(x, y, z)] = WATER;
      }
    }
  }

  placeTrees(seed);

  for (const c of chunks) c.dirty = true;
}

function placeTrees(seed) {
  const rng = mulberry32(seed ^ 0x9e3779b9);

  for (let i = 0; i < 70; i++) {
    const x = Math.floor(rng() * WORLD_X);
    const z = Math.floor(rng() * WORLD_Z);

    if (x < 2 || z < 2 || x > WORLD_X - 3 || z > WORLD_Z - 3) continue;

    let surface = -1;
    for (let y = WORLD_Y - 1; y >= 0; y--) {
      const t = getBlock(x, y, z);
      if (t !== AIR && t !== WATER) {
        surface = y;
        break;
      }
    }

    if (surface < 0 || surface <= WATER_LEVEL) continue;
    if (getBlock(x, surface, z) !== GRASS) continue;

    if (rng() < 0.62) continue;

    const trunkH = 4 + Math.floor(rng() * 3);
    const topY = surface + trunkH;

    for (let y = 1; y <= trunkH; y++) {
      setBlock(x, surface + y, z, LOG);
    }

    // 葉
    const leafStartY = surface + trunkH - 3;
    for (let ly = leafStartY; ly <= surface + trunkH + 2; ly++) {
      const radius = ly <= surface + trunkH ? 2 : (ly === surface + trunkH + 1 ? 1 : 0);

      for (let lx = -radius; lx <= radius; lx++) {
        for (let lz = -radius; lz <= radius; lz++) {
          if (Math.abs(lx) === radius && Math.abs(lz) === radius) {
            if (rng() < 0.6) continue;
          }

          const wx = x + lx;
          const wz = z + lz;
          if (wx < 0 || wx >= WORLD_X || wz < 0 || wz >= WORLD_Z || ly < 0 || ly >= WORLD_Y) continue;

          const old = getBlock(wx, ly, wz);
          if (old === AIR) setBlock(wx, ly, wz, LEAVES);
        }
      }
    }
  }

  // 葉で埋まった原木の上を軽く整える
  markAllDirty();
}

function mulberry32(a) {
  return function() {
    a |= 0;
    a = a + 0x6D2B79F5 | 0;
    let t = Math.imul(a ^ a >>> 15, 1 | a);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}

/* =========================
   プレイヤー
========================= */
const player = {
  x: WORLD_X / 2 + 0.5,
  y: 30,
  z: WORLD_Z / 2 + 0.5,
  vx: 0,
  vy: 0,
  vz: 0,
  grounded: false,
  fly: false,
  yaw: 0,
  pitch: 0
};

function findSpawn() {
  const x = Math.floor(WORLD_X / 2);
  const z = Math.floor(WORLD_Z / 2);

  for (let y = WORLD_Y - 1; y >= 0; y--) {
    const t = getBlock(x, y, z);
    if (t !== AIR && t !== WATER) {
      return { x: x + 0.5, y: y + 1.25, z: z + 0.5 };
    }
  }

  return { x: WORLD_X / 2 + 0.5, y: 30, z: WORLD_Z / 2 + 0.5 };
}

function setSpawn() {
  const s = findSpawn();
  player.x = s.x;
  player.y = s.y;
  player.z = s.z;
  player.vx = player.vy = player.vz = 0;
  player.yaw = 0;
  player.pitch = 0;
}

function collidesAABB(px, py, pz) {
  const minX = Math.floor(px - PLAYER_HALF_WIDTH);
  const maxX = Math.floor(px + PLAYER_HALF_WIDTH);
  const minY = Math.floor(py + 0.001);
  const maxY = Math.floor(py + PLAYER_HEIGHT - 0.001);
  const minZ = Math.floor(pz - PLAYER_HALF_WIDTH);
  const maxZ = Math.floor(pz + PLAYER_HALF_WIDTH);

  for (let y = minY; y <= maxY; y++) {
    for (let x = minX; x <= maxX; x++) {
      for (let z = minZ; z <= maxZ; z++) {
        if (x < 0 || x >= WORLD_X || z < 0 || z >= WORLD_Z || y < 0) return true;
        if (y >= WORLD_Y) continue;

        const t = blockData[blockIndex(x, y, z)];
        if (t !== AIR && t !== WATER) return true;
      }
    }
  }

  return false;
}

function intersectsPlayerBlock(bx, by, bz) {
  return (
    player.x + PLAYER_HALF_WIDTH > bx &&
    player.x - PLAYER_HALF_WIDTH < bx + 1 &&
    player.y + PLAYER_HEIGHT > by &&
    player.y < by + 1 &&
    player.z + PLAYER_HALF_WIDTH > bz &&
    player.z - PLAYER_HALF_WIDTH < bz + 1
  );
}

function moveAxis(axis, amount) {
  if (amount === 0) return false;

  if (axis === "x") player.x += amount;
  if (axis === "y") player.y += amount;
  if (axis === "z") player.z += amount;

  if (collidesAABB(player.x, player.y, player.z)) {
    if (axis === "x") player.x -= amount;
    if (axis === "y") player.y -= amount;
    if (axis === "z") player.z -= amount;

    if (axis === "y") {
      if (amount < 0) player.grounded = true;
      player.vy = 0;
    }

    return true;
  }

  if (axis === "y") {
    player.grounded = false;
  }

  return false;
}

function updatePlayer(dt) {
  if (!pointerLocked) return;

  const forwardInput =
    (keys["KeyW"] ? 1 : 0) -
    (keys["KeyS"] ? 1 : 0);

  const strafeInput =
    (keys["KeyD"] ? 1 : 0) -
    (keys["KeyA"] ? 1 : 0);

  const upInput =
    (keys["Space"] ? 1 : 0) -
    (keys["ShiftLeft"] || keys["ShiftRight"] ? 1 : 0);

  const forward = new THREE.Vector3(-Math.sin(player.yaw), 0, -Math.cos(player.yaw));
  const right = new THREE.Vector3(Math.cos(player.yaw), 0, -Math.sin(player.yaw));

  const wish = new THREE.Vector3();
  wish.addScaledVector(forward, forwardInput);
  wish.addScaledVector(right, strafeInput);

  if (wish.lengthSq() > 0) wish.normalize();

  let speed = WALK_SPEED;
  if (player.fly) speed = FLY_SPEED;
  else if (keys["ControlLeft"] || keys["ControlRight"]) speed = SPRINT_SPEED;
  else if (keys["ShiftLeft"] || keys["ShiftRight"]) speed = SNEAK_SPEED;

  player.vx = wish.x * speed;
  player.vz = wish.z * speed;

  if (player.fly) {
    player.vy = upInput * speed * 0.85;
    player.grounded = false;
  } else {
    player.vy -= GRAVITY * dt;
    player.vy = Math.max(player.vy, -34);

    if (upInput > 0 && player.grounded) {
      player.vy = JUMP_SPEED;
      player.grounded = false;
    }
  }

  // 念のため複数サブステップで移動
  const steps = Math.max(1, Math.ceil(Math.max(Math.abs(player.vx), Math.abs(player.vy), Math.abs(player.vz)) * dt / 0.12));
  const step = dt / steps;

  for (let i = 0; i < steps; i++) {
    moveAxis("x", player.vx * step);
    moveAxis("z", player.vz * step);
    moveAxis("y", player.vy * step);
  }

  // 落下復帰
  if (player.y < -30) {
    setSpawn();
  }

  player.x = THREE.MathUtils.clamp(player.x, 0.7, WORLD_X - 0.7);
  player.z = THREE.MathUtils.clamp(player.z, 0.7, WORLD_Z - 0.7);

  camera.position.set(player.x, player.y + EYE_HEIGHT, player.z);
  camera.rotation.set(player.pitch, player.yaw, 0, "YXZ");
}

/* =========================
   レイキャスト
========================= */
function getCameraDirection() {
  return new THREE.Vector3(0, 0, -1).applyEuler(new THREE.Euler(player.pitch, player.yaw, 0, "YXZ")).normalize();
}

function raycastVoxel(maxDistance = 6) {
  const origin = new THREE.Vector3(player.x, player.y + EYE_HEIGHT, player.z);
  const dir = getCameraDirection();

  let x = Math.floor(origin.x);
  let y = Math.floor(origin.y);
  let z = Math.floor(origin.z);

  const stepX = dir.x > 0 ? 1 : dir.x < 0 ? -1 : 0;
  const stepY = dir.y > 0 ? 1 : dir.y < 0 ? -1 : 0;
  const stepZ = dir.z > 0 ? 1 : dir.z < 0 ? -1 : 0;

  const tDeltaX = stepX !== 0 ? Math.abs(1 / dir.x) : Infinity;
  const tDeltaY = stepY !== 0 ? Math.abs(1 / dir.y) : Infinity;
  const tDeltaZ = stepZ !== 0 ? Math.abs(1 / dir.z) : Infinity;

  let tMaxX = stepX > 0 ? (x + 1 - origin.x) / dir.x : stepX < 0 ? (x - origin.x) / dir.x : Infinity;
  let tMaxY = stepY > 0 ? (y + 1 - origin.y) / dir.y : stepY < 0 ? (y - origin.y) / dir.y : Infinity;
  let tMaxZ = stepZ > 0 ? (z + 1 - origin.z) / dir.z : stepZ < 0 ? (z - origin.z) / dir.z : Infinity;

  let face = new THREE.Vector3(0, 1, 0);

  for (let i = 0; i < 120; i++) {
    if (x >= 0 && x < WORLD_X && y >= 0 && y < WORLD_Y && z >= 0 && z < WORLD_Z) {
      const t = blockData[blockIndex(x, y, z)];
      if (t !== AIR && t !== WATER) {
        return { x, y, z, face, block: t };
      }
    }

    if (tMaxX < tMaxY && tMaxX < tMaxZ) {
      if (tMaxX > maxDistance) break;
      x += stepX;
      tMaxX += tDeltaX;
      face.set(-stepX, 0, 0);
    } else if (tMaxY < tMaxZ) {
      if (tMaxY > maxDistance) break;
      y += stepY;
      tMaxY += tDeltaY;
      face.set(0, -stepY, 0);
    } else {
      if (tMaxZ > maxDistance) break;
      z += stepZ;
      tMaxZ += tDeltaZ;
      face.set(0, 0, -stepZ);
    }

    if (
      (x < 0 || x >= WORLD_X) &&
      (z < 0 || z >= WORLD_Z) &&
      (y < 0 || y >= WORLD_Y)
    ) {
      break;
    }
  }

  return null;
}

/* =========================
   破壊 / 設置
========================= */
let selectedHotbar = 0;

function breakBlock() {
  const hit = raycastVoxel(6);
  if (!hit) return;

  if (BLOCKS[hit.block]?.unbreakable) return;

  setBlock(hit.x, hit.y, hit.z, AIR);

  // 水や葉の一部が残るとき、上の葉を連鎖除去（軽く）
  if (hit.block === LOG) {
    for (let y = hit.y + 1; y < WORLD_Y; y++) {
      const t = getBlock(hit.x, y, hit.z);
      if (t === LEAVES) setBlock(hit.x, y, hit.z, AIR);
      else if (t !== AIR) break;
    }
  }

  markChunkDirtyAt(hit.x, hit.z);
}

function placeBlock() {
  const hit = raycastVoxel(6);
  if (!hit) return;

  const nx = hit.x + hit.face.x;
  const ny = hit.y + hit.face.y;
  const nz = hit.z + hit.face.z;

  if (nx < 0 || nx >= WORLD_X || ny < 0 || ny >= WORLD_Y || nz < 0 || nz >= WORLD_Z) return;

  const target = blockData[blockIndex(nx, ny, nz)];
  const selected = HOTBAR[selectedHotbar];

  if (target !== AIR && target !== WATER) return;

  if (selected !== WATER && intersectsPlayerBlock(nx, ny, nz)) return;

  setBlock(nx, ny, nz, selected);
  markChunkDirtyAt(nx, nz);
}

/* =========================
   UI
========================= */
const overlay = document.getElementById("overlay");
const hotbarEl = document.getElementById("hotbar");
const infoEl = document.getElementById("info");
const toast = document.getElementById("savedToast");

function createHotbar() {
  hotbarEl.innerHTML = "";

  HOTBAR.forEach((type, i) => {
    const slot = document.createElement("div");
    slot.className = "slot";
    slot.dataset.i = i;

    const num = document.createElement("span");
    num.className = "num";
    num.textContent = i + 1;
    slot.appendChild(num);

    const icon = document.createElement("div");
    icon.className = "blockIcon";
    icon.style.background = blockPreviewColor(type);
    slot.appendChild(icon);

    hotbarEl.appendChild(slot);
  });

  updateHotbarUI();
}

function updateHotbarUI() {
  [...hotbarEl.children].forEach((el, i) => {
    el.classList.toggle("selected", i === selectedHotbar);
  });

  const type = HOTBAR[selectedHotbar];
  infoEl.textContent =
    `選択: ${BLOCKS[type]?.name || "なし"} (${selectedHotbar + 1})\n` +
    `位置: ${player.x.toFixed(1)}, ${player.y.toFixed(1)}, ${player.z.toFixed(1)}\n` +
    `飛行: ${player.fly ? "ON" : "OFF"}`;
}

function blockPreviewColor(type) {
  const map = {
    [GRASS]: "linear-gradient(180deg,#58b05a 0%,#58b05a 35%,#8d6544 35%,#6d4a31 100%)",
    [DIRT]: "#7e573a",
    [STONE]: "#868688",
    [SAND]: "#dbcc8e",
    [LOG]: "linear-gradient(90deg,#6d4c2c,#8b6338,#6d4c2c)",
    [LEAVES]: "#377a38",
    [PLANKS]: "linear-gradient(180deg,#b88a52,#8d683c)",
    [GLASS]: "linear-gradient(135deg,rgba(180,230,255,.65),rgba(255,255,255,.35))",
    [BRICK]: "#933331",
    [WATER]: "linear-gradient(180deg,rgba(70,150,230,.95),rgba(35,100,190,.95))",
    [COBBLE]: "linear-gradient(45deg,#6d6d6d,#8f8f8f,#5b5b5b)",
    [BEDROCK]: "#303033"
  };

  return map[type] || "#888";
}

function showToast(text) {
  toast.textContent = text;
  toast.classList.add("show");
  clearTimeout(showToast._t);
  showToast._t = setTimeout(() => toast.classList.remove("show"), 1100);
}

/* =========================
   入力
========================= */
const keys = Object.create(null);
let pointerLocked = false;

document.addEventListener("keydown", (e) => {
  keys[e.code] = true;

  if (e.ctrlKey && e.code === "KeyS") {
    e.preventDefault();
    saveWorld();
    showToast("保存しました");
    return;
  }

  if (!pointerLocked) return;

  if (e.code === "KeyF") {
    player.fly = !player.fly;
    player.vy = 0;
    updateHotbarUI();
  }

  if (e.code.startsWith("Digit")) {
    const n = Number(e.code.slice(5));
    if (n >= 1 && n <= HOTBAR.length) {
      selectedHotbar = n - 1;
      updateHotbarUI();
    }
  }
});

document.addEventListener("keyup", (e) => {
  keys[e.code] = false;
});

renderer.domElement.addEventListener("contextmenu", e => e.preventDefault());

renderer.domElement.addEventListener("mousedown", (e) => {
  if (!pointerLocked) return;

  if (e.button === 0) breakBlock();
  if (e.button === 2) placeBlock();
});

renderer.domElement.addEventListener("wheel", (e) => {
  if (!pointerLocked) return;
  selectedHotbar = (selectedHotbar + (e.deltaY > 0 ? 1 : -1) + HOTBAR.length) % HOTBAR.length;
  updateHotbarUI();
}, { passive: true });

document.addEventListener("mousemove", (e) => {
  if (!pointerLocked) return;

  player.yaw -= e.movementX * 0.0022;
  player.pitch -= e.movementY * 0.0022;

  const maxPitch = Math.PI / 2 - 0.01;
  player.pitch = THREE.MathUtils.clamp(player.pitch, -maxPitch, maxPitch);
});

document.addEventListener("pointerlockchange", () => {
  pointerLocked = document.pointerLockElement === renderer.domElement;
  overlay.style.display = pointerLocked ? "none" : "flex";
});

document.getElementById("startBtn").addEventListener("click", () => {
  renderer.domElement.requestPointerLock();
});

document.getElementById("resetBtn").addEventListener("click", () => {
  localStorage.removeItem(SAVE_KEY);
  currentSeed = Math.floor(Math.random() * 1e9);
  generateWorld(currentSeed);
  setSpawn();
  updateHotbarUI();
  showToast("新しいワールドを作成");
});

/* =========================
   保存 / 読み込み
========================= */
function saveWorld() {
  try {
    const payload = {
      seed: currentSeed,
      player: {
        x: player.x,
        y: player.y,
        z: player.z,
        yaw: player.yaw,
        pitch: player.pitch
      },
      data: bytesToBase64(blockData)
    };
    localStorage.setItem(SAVE_KEY, JSON.stringify(payload));
    return true;
  } catch (err) {
    console.warn("保存に失敗しました", err);
    return false;
  }
}

function loadWorld() {
  try {
    const raw = localStorage.getItem(SAVE_KEY);
    if (!raw) return false;

    const obj = JSON.parse(raw);
    if (!obj?.data) return false;

    currentSeed = obj.seed ?? currentSeed;
    const loaded = base64ToBytes(obj.data);
    if (loaded.length !== blockData.length) return false;

    blockData.set(loaded);

    if (obj.player) {
      player.x = obj.player.x;
      player.y = obj.player.y;
      player.z = obj.player.z;
      player.yaw = obj.player.yaw || 0;
      player.pitch = obj.player.pitch || 0;
    }

    markAllDirty();
    return true;
  } catch (err) {
    console.warn("読み込みに失敗しました", err);
    return false;
  }
}

function bytesToBase64(u8) {
  let binary = "";
  const chunk = 8192;
  for (let i = 0; i < u8.length; i += chunk) {
    binary += String.fromCharCode(...u8.subarray(i, i + chunk));
  }
  return btoa(binary);
}

function base64ToBytes(b64) {
  const binary = atob(b64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
  return bytes;
}

/* =========================
   2Dノイズ（雲用）
========================= */
function noise2(x, y) {
  const xi = Math.floor(x);
  const yi = Math.floor(y);
  const xf = x - xi;
  const yf = y - yi;

  const a = valueNoise(xi, yi, 777);
  const b = valueNoise(xi + 1, yi, 777);
  const c = valueNoise(xi, yi + 1, 777);
  const d = valueNoise(xi + 1, yi + 1, 777);

  const u = fade(xf);
  const v = fade(yf);

  return lerp(lerp(a, b, u), lerp(c, d, u), v) * 2 - 1;
}

/* =========================
   メインループ
========================= */
initChunks();

if (!loadWorld()) {
  generateWorld(currentSeed);
  setSpawn();
}

createHotbar();

const clock = new THREE.Clock();
let acc = 0;
const FIXED_STEP = 1 / 120;

function animate() {
  requestAnimationFrame(animate);

  const dt = Math.min(clock.getDelta(), 0.08);

  acc += dt;
  let loops = 0;
  while (acc >= FIXED_STEP && loops < 8) {
    updatePlayer(FIXED_STEP);
    acc -= FIXED_STEP;
    loops++;
  }

  camera.position.set(player.x, player.y + EYE_HEIGHT, player.z);
  camera.rotation.set(player.pitch, player.yaw, 0, "YXZ");

  clouds.position.x = WORLD_X / 2 + Math.sin(performance.now() * 0.00003) * 12;
  clouds.position.z = WORLD_Z / 2 + Math.cos(performance.now() * 0.000024) * 12;
  cloudTexture.offset.x += dt * 0.004;

  rebuildDirtyChunks(2);

  if (!pointerLocked && acc > 0.25) {
    // 未操作時も軽くUI更新
    updateHotbarUI();
    acc = Math.min(acc, FIXED_STEP * 2);
  }

  renderer.render(scene, camera);
}

animate();

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
```