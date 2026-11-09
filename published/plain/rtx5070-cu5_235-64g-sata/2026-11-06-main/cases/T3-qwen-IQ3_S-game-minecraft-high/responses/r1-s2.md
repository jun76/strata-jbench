以下、**単一 HTML ファイル**で動く、ブラウザ版「Minecraft風 3D ボクセル箱庭ゲーム」です。  
ファイルに保存してブラウザで開くだけで遊べます。

**保存方法**  
例: `minecraft-like-sandbox.html` として保存 → ブラウザで開く

---

```html
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>マイクラ風 3D 箱庭ゲーム</title>

<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
  }
}
</script>

<style>
  html, body {
    margin: 0;
    height: 100%;
    overflow: hidden;
    background: #77c;
    font-family: system-ui, -apple-system, "Hiragino Kaku Gothic ProN", "Meiryo", sans-serif;
    color: #fff;
  }

  canvas { display: block; }

  #overlay {
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.55);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10;
  }

  .panel {
    background: rgba(20,24,28,0.82);
    border: 2px solid rgba(255,255,255,0.18);
    border-radius: 14px;
    padding: 22px 26px;
    max-width: 760px;
    box-shadow: 0 12px 40px rgba(0,0,0,0.45);
  }

  .panel h1 {
    margin: 0 0 10px;
    font-size: 24px;
    letter-spacing: 1px;
  }

  .panel p {
    margin: 8px 0;
    line-height: 1.6;
  }

  .start-btn {
    margin-top: 16px;
    padding: 12px 18px;
    border: 0;
    border-radius: 10px;
    background: #38b25a;
    color: white;
    font-size: 16px;
    cursor: pointer;
    box-shadow: 0 4px 0 #1f7e39;
  }

  .start-btn:hover { background: #3ecf67; }

  #hud {
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 5;
  }

  #crosshair {
    position: fixed;
    left: 50%;
    top: 50%;
    width: 18px;
    height: 18px;
    transform: translate(-50%, -50%);
  }

  #crosshair::before, #crosshair::after {
    content: "";
    position: absolute;
    background: rgba(255,255,255,0.85);
    box-shadow: 0 0 2px rgba(0,0,0,0.55);
  }

  #crosshair::before {
    left: 8px;
    top: 0;
    width: 2px;
    height: 18px;
  }

  #crosshair::after {
    left: 0;
    top: 8px;
    width: 18px;
    height: 2px;
  }

  #hotbar {
    position: fixed;
    left: 50%;
    bottom: 18px;
    transform: translateX(-50%);
    display: flex;
    gap: 6px;
    padding: 8px;
    background: rgba(0,0,0,0.35);
    border-radius: 10px;
  }

  .slot {
    width: 54px;
    height: 54px;
    border-radius: 8px;
    border: 2px solid rgba(255,255,255,0.22);
    background: rgba(0,0,0,0.35);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 700;
    text-shadow: 0 1px 2px black;
  }

  .slot .color {
    width: 30px;
    height: 30px;
    border-radius: 5px;
    margin-bottom: 3px;
    border: 1px solid rgba(0,0,0,0.25);
  }

  .slot.active {
    border-color: #fff;
    outline: 2px solid rgba(255,255,255,0.75);
  }

  #info {
    position: fixed;
    left: 12px;
    top: 12px;
    padding: 10px 12px;
    background: rgba(0,0,0,0.35);
    border-radius: 10px;
    font-size: 12px;
    line-height: 1.5;
  }

  #mode {
    position: fixed;
    right: 12px;
    top: 12px;
    padding: 10px 12px;
    background: rgba(0,0,0,0.35);
    border-radius: 10px;
    font-size: 13px;
  }

  #toast {
    position: fixed;
    left: 50%;
    top: 60px;
    transform: translateX(-50%);
    padding: 8px 14px;
    border-radius: 999px;
    background: rgba(0,0,0,0.42);
    font-size: 13px;
    opacity: 0;
    transition: opacity 0.18s ease;
  }
</style>
</head>
<body>

<div id="overlay">
  <div class="panel">
    <h1>🟩 マインクラフト風 3D 箱庭ゲーム</h1>
    <p>
      Three.js を使った、ブラウザで動くボクセルワールドです。<br>
      画面クリックでマウスロックすると操作できます。
    </p>

    <p>
      <b>操作</b><br>
      WASD：移動<br>
      Space：ジャンプ / フライト時に上昇<br>
      Shift：地面に落ちる / フライト時に下降<br>
      F：フライモード切り替え<br>
      R：プレイヤーを初期位置へ戻す<br>
      1〜8 または マウスホイール：ブロック切り替え<br>
      左クリック：ブロックを置く<br>
      右クリック：ブロックを壊す<br>
      Esc：マウスロック解除
    </p>

    <button id="start" class="start-btn">ゲーム開始</button>
  </div>
</div>

<div id="hud">
  <div id="crosshair"></div>
  <div id="info">
    <b>マイクラ風ボクセル</b><br>
    WASD 移動 / Space ジャンプ<br>
    F フライ / R 復帰<br>
    左クリック置く / 右クリック壊す
  </div>
  <div id="mode">通常</div>
  <div id="hotbar"></div>
  <div id="toast"></div>
</div>

<script type="module">
import * as THREE from "three";
import { PointerLockControls } from "three/addons/controls/PointerLockControls.js";

/* ------------------------------------------------------------------
   基本設定
------------------------------------------------------------------ */
const BLOCK = {
  AIR: 0,
  GRASS: 1,
  DIRT: 2,
  STONE: 3,
  WOOD: 4,
  LEAVES: 5,
  SAND: 6,
  GLASS: 7,
  BRICK: 8
};

const PLACEABLE = [
  BLOCK.GRASS,
  BLOCK.DIRT,
  BLOCK.STONE,
  BLOCK.WOOD,
  BLOCK.LEAVES,
  BLOCK.SAND,
  BLOCK.GLASS,
  BLOCK.BRICK
];

const BLOCK_NAMES = {
  [BLOCK.GRASS]: "草",
  [BLOCK.DIRT]: "土",
  [BLOCK.STONE]: "石",
  [BLOCK.WOOD]: "木",
  [BLOCK.LEAVES]: "葉",
  [BLOCK.SAND]: "砂",
  [BLOCK.GLASS]: "ガラス",
  [BLOCK.BRICK]: "レンガ"
};

const BLOCK_COLORS = {
  [BLOCK.GRASS]: "#5e9b3b",
  [BLOCK.DIRT]: "#7a5230",
  [BLOCK.STONE]: "#8f8f8f",
  [BLOCK.WOOD]: "#6b4f2a",
  [BLOCK.LEAVES]: "#356f22",
  [BLOCK.SAND]: "#d9d09a",
  [BLOCK.GLASS]: "#a8d8ff",
  [BLOCK.BRICK]: "#a63f3f"
};

/* ワールドサイズ */
const X_SIZE = 48;
const Y_SIZE = 64;
const Z_SIZE = 48;

const world = new Uint8Array(X_SIZE * Y_SIZE * Z_SIZE);

function idx(x, y, z) {
  return x + X_SIZE * (z + Z_SIZE * y);
}

function inBounds(x, y, z) {
  return (
    x >= 0 && x < X_SIZE &&
    y >= 0 && y < Y_SIZE &&
    z >= 0 && z < Z_SIZE
  );
}

function getBlock(x, y, z) {
  if (!inBounds(x, y, z)) return BLOCK.AIR;
  return world[idx(x, y, z)];
}

function setBlock(x, y, z, type) {
  if (!inBounds(x, y, z)) return;
  world[idx(x, y, z)] = type;
}

function isSolid(x, y, z) {
  return getBlock(x, y, z) !== BLOCK.AIR;
}

/* ------------------------------------------------------------------
   テクスチャ作成
------------------------------------------------------------------ */
function randInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function clamp(v, min, max) {
  return Math.max(min, Math.min(max, v));
}

function hsl(h, s, l) {
  h = ((h % 360) + 360) % 360;
  s = clamp(s, 0, 100);
  l = clamp(l, 0, 100);
  return `hsl(${h}, ${s}%, ${l}%)`;
}

function makeCanvasTexture(draw) {
  const size = 16;
  const canvas = document.createElement("canvas");
  canvas.width = size;
  canvas.height = size;

  const ctx = canvas.getContext("2d");
  draw(ctx, size);

  const tex = new THREE.CanvasTexture(canvas);
  tex.magFilter = THREE.NearestFilter;
  tex.minFilter = THREE.NearestFilter;
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.generateMipmaps = false;
  return tex;
}

function fillNoise(ctx, size, h, s, l, vh = 6, vs = 5, vl = 8) {
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      ctx.fillStyle = hsl(
        h + randInt(-vh, vh),
        s + randInt(-vs, vs),
        l + randInt(-vl, vl)
      );
      ctx.fillRect(x, y, 1, 1);
    }
  }
}

const texGrassTop = makeCanvasTexture((ctx, size) => {
  fillNoise(ctx, size, 95, 55, 38, 7, 6, 8);
});

const texDirt = makeCanvasTexture((ctx, size) => {
  fillNoise(ctx, size, 28, 40, 32, 6, 6, 8);
});

const texGrassSide = makeCanvasTexture((ctx, size) => {
  fillNoise(ctx, size, 28, 40, 32, 6, 6, 8);

  for (let y = 0; y < 5; y++) {
    for (let x = 0; x < size; x++) {
      ctx.fillStyle = hsl(
        95 + randInt(-8, 8),
        52 + randInt(-8, 8),
        38 + randInt(-9, 9)
      );
      ctx.fillRect(x, y, 1, 1);
    }
  }

  for (let x = 0; x < size; x++) {
    if (Math.random() < 0.35) {
      ctx.fillStyle = hsl(95 + randInt(-10, 10), 52, 36);
      ctx.fillRect(x, 5, 1, randInt(1, 3));
    }
  }
});

const texStone = makeCanvasTexture((ctx, size) => {
  fillNoise(ctx, size, 0, 0, 54, 4, 2, 10);

  for (let i = 0; i < 14; i++) {
    const x = randInt(1, size - 1);
    const y = randInt(1, size - 1);
    const l = randInt(40, 60);
    ctx.fillStyle = hsl(0, 0, l);
    ctx.fillRect(x, y, randInt(2, 5), randInt(1, 2));
  }
});

const texSand = makeCanvasTexture((ctx, size) => {
  fillNoise(ctx, size, 48, 55, 72, 5, 8, 7);
});

const texWoodSide = makeCanvasTexture((ctx, size) => {
  fillNoise(ctx, size, 28, 42, 30, 5, 5, 6);

  for (let x = 0; x < size; x++) {
    if (Math.random() < 0.22) {
      ctx.fillStyle = hsl(28, 42, 22);
      for (let y = 0; y < size; y++) {
        if (Math.random() < 0.78) ctx.fillRect(x, y, 1, 1);
      }
    }
  }
});

const texWoodTop = makeCanvasTexture((ctx, size) => {
  fillNoise(ctx, size, 30, 38, 42, 5, 5, 6);

  ctx.strokeStyle = hsl(30, 38, 30);
  ctx.lineWidth = 1;
  ctx.strokeRect(2, 2, 12, 12);
  ctx.strokeRect(4, 4, 8, 8);
  ctx.strokeRect(6, 6, 4, 4);
});

const texLeaves = makeCanvasTexture((ctx, size) => {
  fillNoise(ctx, size, 115, 46, 30, 8, 8, 8);

  for (let i = 0; i < 22; i++) {
    ctx.fillStyle = hsl(115 + randInt(-12, 12), 50, randInt(24, 42));
    ctx.fillRect(randInt(0, 15), randInt(0, 15), randInt(1, 3), randInt(1, 3));
  }
});

const texGlass = makeCanvasTexture((ctx, size) => {
  fillNoise(ctx, size, 205, 45, 74, 5, 5, 5);

  ctx.strokeStyle = "rgba(255,255,255,0.75)";
  ctx.lineWidth = 1;
  ctx.strokeRect(0.5, 0.5, 15, 15);

  ctx.strokeStyle = "rgba(255,255,255,0.55)";
  ctx.beginPath();
  ctx.moveTo(3, 12);
  ctx.lineTo(11, 4);
  ctx.stroke();
});

const texBrick = makeCanvasTexture((ctx, size) => {
  fillNoise(ctx, size, 0, 45, 36, 5, 5, 6);

  ctx.fillStyle = "rgba(35,35,35,0.65)";
  for (let y = 2; y < size; y += 5) {
    ctx.fillRect(0, y, size, 1);
  }

  for (let row = 0; row < 4; row++) {
    const offset = (row % 2 === 0) ? 2 : 6;
    for (let x = offset; x < size; x += 8) {
      ctx.fillRect(x, row * 5, 1, 5);
    }
  }
});

const matDirt = new THREE.MeshLambertMaterial({ map: texDirt });
const matStone = new THREE.MeshLambertMaterial({ map: texStone });
const matSand = new THREE.MeshLambertMaterial({ map: texSand });
const matWoodSide = new THREE.MeshLambertMaterial({ map: texWoodSide });
const matWoodTop = new THREE.MeshLambertMaterial({ map: texWoodTop });
const matLeaves = new THREE.MeshLambertMaterial({ map: texLeaves });

const matGlass = new THREE.MeshLambertMaterial({
  map: texGlass,
  transparent: true,
  opacity: 0.72,
  depthWrite: true
});

const matBrick = new THREE.MeshLambertMaterial({ map: texBrick });

const blockMaterials = new Array(9);
blockMaterials[BLOCK.GRASS] = [
  new THREE.MeshLambertMaterial({ map: texGrassSide }),
  new THREE.MeshLambertMaterial({ map: texGrassSide }),
  new THREE.MeshLambertMaterial({ map: texGrassTop }),
  matDirt,
  new THREE.MeshLambertMaterial({ map: texGrassSide }),
  new THREE.MeshLambertMaterial({ map: texGrassSide })
];
blockMaterials[BLOCK.DIRT] = matDirt;
blockMaterials[BLOCK.STONE] = matStone;
blockMaterials[BLOCK.WOOD] = matWoodSide;
blockMaterials[BLOCK.LEAVES] = matLeaves;
blockMaterials[BLOCK.SAND] = matSand;
blockMaterials[BLOCK.GLASS] = matGlass;
blockMaterials[BLOCK.BRICK] = matBrick;

/* ------------------------------------------------------------------
   Three.js
------------------------------------------------------------------ */
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 26, 92);

const camera = new THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 0.1, 220);
camera.position.set(X_SIZE / 2, 20, Z_SIZE / 2);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.setClearColor(0x87ceeb);
document.body.appendChild(renderer.domElement);

const hemi = new THREE.HemisphereLight(0xcfe8ff, 0x3b2b1d, 0.85);
scene.add(hemi);

const dir = new THREE.DirectionalLight(0xffffff, 1.05);
dir.position.set(30, 50, 20);
scene.add(dir);

const blockGeo = new THREE.BoxGeometry(1, 1, 1);
const renderRoot = new THREE.Group();
scene.add(renderRoot);

const controls = new PointerLockControls(camera, renderer.domElement);

/* ------------------------------------------------------------------
   ワールド生成
------------------------------------------------------------------ */
function hash2(x, z) {
  let n = Math.sin(x * 127.1 + z * 311.7) * 43758.5453;
  return n - Math.floor(n);
}

function lerp(a, b, t) {
  return a + (b - a) * t;
}

function smoothstep(t) {
  return t * t * (3 - 2 * t);
}

function valueNoise(x, z) {
  const xi = Math.floor(x);
  const zi = Math.floor(z);
  const xf = x - xi;
  const zf = z - zi;

  const u = smoothstep(xf);
  const v = smoothstep(zf);

  const a = hash2(xi, zi);
  const b = hash2(xi + 1, zi);
  const c = hash2(xi, zi + 1);
  const d = hash2(xi + 1, zi + 1);

  return lerp(lerp(a, b, u), lerp(c, d, u), v);
}

function fbm(x, z) {
  let value = 0;
  let amp = 1;
  let freq = 1;
  let norm = 0;

  for (let i = 0; i < 4; i++) {
    value += valueNoise(x * freq, z * freq) * amp;
    norm += amp;
    amp *= 0.5;
    freq *= 2;
  }

  return value / norm;
}

function heightAt(x, z) {
  let h =
    4 +
    5.0 * fbm(x / 18, z / 18) +
    3.0 * fbm(x / 6 + 13.2, z / 6 + 17.8) +
    1.2 * Math.sin(x * 0.18) * Math.cos(z * 0.14);

  h = Math.floor(h);
  h = clamp(h, 2, 24);
  return h;
}

function generateWorld() {
  world.fill(0);

  for (let x = 0; x < X_SIZE; x++) {
    for (let z = 0; z < Z_SIZE; z++) {
      const h = heightAt(x, z);

      for (let y = 0; y < h; y++) {
        let type = BLOCK.STONE;

        if (y >= h - 1) {
          if (h <= 4) type = BLOCK.SAND;
          else if (h >= 12) type = BLOCK.STONE;
          else type = BLOCK.GRASS;
        } else if (y >= h - 4) {
          type = BLOCK.DIRT;
        }

        setBlock(x, y, z, type);
      }
    }
  }

  const spawnX = Math.floor(X_SIZE / 2);
  const spawnZ = Math.floor(Z_SIZE / 2);

  for (let x = 2; x < X_SIZE - 2; x++) {
    for (let z = 2; z < Z_SIZE - 2; z++) {
      if (Math.abs(x - spawnX) <= 3 && Math.abs(z - spawnZ) <= 3) continue;

      const h = heightAt(x, z);
      if (getBlock(x, h - 1, z) !== BLOCK.GRASS) continue;
      if (Math.random() > 0.018) continue;

      const trunkH = 3 + randInt(0, 2);
      const topY = h - 1 + trunkH;

      for (let y = h; y <= topY; y++) {
        setBlock(x, y, z, BLOCK.WOOD);
      }

      for (let ly = topY - 1; ly <= topY + 1; ly++) {
        for (let dx = -2; dx <= 2; dx++) {
          for (let dz = -2; dz <= 2; dz++) {
            const absX = Math.abs(dx);
            const absZ = Math.abs(dz);

            if (ly === topY + 1 && absX + absZ > 1) continue;
            if (ly === topY && absX + absZ > 3) continue;
            if (ly === topY - 1 && absX === 2 && absZ === 2) continue;

            const bx = x + dx;
            const bz = z + dz;

            if (getBlock(bx, ly, bz) !== BLOCK.AIR) continue;

            setBlock(bx, ly, bz, BLOCK.LEAVES);
          }
        }
      }
    }
  }
}

function rebuildWorld() {
  renderRoot.clear();

  const counts = new Uint32Array(9);

  for (let y = 0; y < Y_SIZE; y++) {
    for (let z = 0; z < Z_SIZE; z++) {
      for (let x = 0; x < X_SIZE; x++) {
        const t = world[idx(x, y, z)];
        if (t !== BLOCK.AIR) counts[t]++;
      }
    }
  }

  const meshList = [];

  for (let t = 1; t < blockMaterials.length; t++) {
    if (counts[t] === 0) continue;

    const mesh = new THREE.InstancedMesh(blockGeo, blockMaterials[t], counts[t]);
    mesh.frustumCulled = false;
    meshList[t] = mesh;
  }

  const cursor = new Uint32Array(9);
  const dummy = new THREE.Object3D();

  for (let y = 0; y < Y_SIZE; y++) {
    for (let z = 0; z < Z_SIZE; z++) {
      for (let x = 0; x < X_SIZE; x++) {
        const t = world[idx(x, y, z)];
        if (t === BLOCK.AIR) continue;

        dummy.position.set(x + 0.5, y + 0.5, z + 0.5);
        dummy.updateMatrix();

        meshList[t].setMatrixAt(cursor[t], dummy.matrix);
        cursor[t]++;
      }
    }
  }

  for (let t = 1; t < blockMaterials.length; t++) {
    if (meshList[t]) {
      meshList[t].instanceMatrix.needsUpdate = true;
      renderRoot.add(meshList[t]);
    }
  }
}

/* ------------------------------------------------------------------
   プレイヤー
------------------------------------------------------------------ */
const EYE_HEIGHT = 1.62;
const PLAYER_HALF_WIDTH = 0.28;
const PLAYER_HEIGHT = 1.8;
const GRAVITY = 30;
const JUMP_SPEED = 10;
const WALK_SPEED = 6.6;
const FLY_SPEED = 20;

const playerPos = new THREE.Vector3(X_SIZE / 2, 30, Z_SIZE / 2);
let velocityY = 0;
let onGround = false;
let flying = false;

function resetPlayer() {
  const sx = Math.floor(X_SIZE / 2);
  const sz = Math.floor(Z_SIZE / 2);

  let topY = 0;
  for (let y = Y_SIZE - 1; y >= 0; y--) {
    if (isSolid(sx, y, sz)) {
      topY = y;
      break;
    }
  }

  playerPos.set(sx + 0.5, topY + 1.01, sz + 0.5);
  velocityY = 0;
  flying = false;
  onGround = false;
  updateModeText();
}

function collides(px, py, pz) {
  const minX = px - PLAYER_HALF_WIDTH;
  const maxX = px + PLAYER_HALF_WIDTH;
  const minY = py;
  const maxY = py + PLAYER_HEIGHT;
  const minZ = pz - PLAYER_HALF_WIDTH;
  const maxZ = pz + PLAYER_HALF_WIDTH;

  const startX = Math.floor(minX);
  const endX = Math.floor(maxX);
  const startY = Math.floor(minY);
  const endY = Math.floor(maxY);
  const startZ = Math.floor(minZ);
  const endZ = Math.floor(maxZ);

  for (let x = startX; x <= endX; x++) {
    for (let y = startY; y <= endY; y++) {
      for (let z = startZ; z <= endZ; z++) {
        if (isSolid(x, y, z)) {
          const overlapX = minX < x + 1 && maxX > x;
          const overlapY = minY < y + 1 && maxY > y;
          const overlapZ = minZ < z + 1 && maxZ > z;

          if (overlapX && overlapY && overlapZ) return true;
        }
      }
    }
  }

  return false;
}

/* ------------------------------------------------------------------
   ブロックの当たり判定
------------------------------------------------------------------ */
function raycastVoxel(maxDistance = 7.0) {
  const ox = camera.position.x;
  const oy = camera.position.y;
  const oz = camera.position.z;

  const dirV = new THREE.Vector3();
  camera.getWorldDirection(dirV);
  dirV.normalize();

  let ix = Math.floor(ox);
  let iy = Math.floor(oy);
  let iz = Math.floor(oz);

  const stepX = dirV.x > 0 ? 1 : dirV.x < 0 ? -1 : 0;
  const stepY = dirV.y > 0 ? 1 : dirV.y < 0 ? -1 : 0;
  const stepZ = dirV.z > 0 ? 1 : dirV.z < 0 ? -1 : 0;

  const tDeltaX = stepX !== 0 ? 1 / Math.abs(dirV.x) : Infinity;
  const tDeltaY = stepY !== 0 ? 1 / Math.abs(dirV.y) : Infinity;
  const tDeltaZ = stepZ !== 0 ? 1 / Math.abs(dirV.z) : Infinity;

  let tMaxX = stepX === 0
    ? Infinity
    : (stepX > 0 ? (ix + 1 - ox) : (ox - ix)) / Math.abs(dirV.x);

  let tMaxY = stepY === 0
    ? Infinity
    : (stepY > 0 ? (iy + 1 - oy) : (oy - iy)) / Math.abs(dirV.y);

  let tMaxZ = stepZ === 0
    ? Infinity
    : (stepZ > 0 ? (iz + 1 - oz) : (oz - iz)) / Math.abs(dirV.z);

  let prevX = ix;
  let prevY = iy;
  let prevZ = iz;
  let t = 0;

  while (t <= maxDistance) {
    if (isSolid(ix, iy, iz)) {
      return {
        x: ix,
        y: iy,
        z: iz,
        nx: prevX - ix,
        ny: prevY - iy,
        nz: prevZ - iz
      };
    }

    prevX = ix;
    prevY = iy;
    prevZ = iz;

    if (tMaxX < tMaxY && tMaxX < tMaxZ) {
      t = tMaxX;
      ix += stepX;
      tMaxX += tDeltaX;
    } else if (tMaxY < tMaxZ) {
      t = tMaxY;
      iy += stepY;
      tMaxY += tDeltaY;
    } else {
      t = tMaxZ;
      iz += stepZ;
      tMaxZ += tDeltaZ;
    }
  }

  return null;
}

function overlapsPlayer(bx, by, bz) {
  const minX = bx;
  const maxX = bx + 1;
  const minY = by;
  const maxY = by + 1;
  const minZ = bz;
  const maxZ = bz + 1;

  const pMinX = playerPos.x - PLAYER_HALF_WIDTH;
  const pMaxX = playerPos.x + PLAYER_HALF_WIDTH;
  const pMinY = playerPos.y;
  const pMaxY = playerPos.y + PLAYER_HEIGHT;
  const pMinZ = playerPos.z - PLAYER_HALF_WIDTH;
  const pMaxZ = playerPos.z + PLAYER_HALF_WIDTH;

  return (
    minX < pMaxX && maxX > pMinX &&
    minY < pMaxY && maxY > pMinY &&
    minZ < pMaxZ && maxZ > pMinZ
  );
}

let selected = 0;

function placeBlock() {
  const hit = raycastVoxel(8.0);
  if (!hit) return;

  const type = PLACEABLE[selected];
  const bx = hit.x + hit.nx;
  const by = hit.y + hit.ny;
  const bz = hit.z + hit.nz;

  if (hit.nx === 0 && hit.ny === 0 && hit.nz === 0) return;
  if (!inBounds(bx, by, bz)) return;
  if (getBlock(bx, by, bz) !== BLOCK.AIR) return;

  if (overlapsPlayer(bx, by, bz)) return;

  setBlock(bx, by, bz, type);
  rebuildWorld();
}

function breakBlock() {
  const hit = raycastVoxel(8.0);
  if (!hit) return;

  if (hit.y <= 0) {
    showToast("一番下のブロックは壊せません");
    return;
  }

  setBlock(hit.x, hit.y, hit.z, BLOCK.AIR);
  rebuildWorld();
}

/* ------------------------------------------------------------------
   UI
------------------------------------------------------------------ */
const hotbar = document.getElementById("hotbar");
const modeText = document.getElementById("mode");
const toast = document.getElementById("toast");

for (let i = 0; i < PLACEABLE.length; i++) {
  const slot = document.createElement("div");
  slot.className = "slot" + (i === selected ? " active" : "");

  const color = document.createElement("div");
  color.className = "color";
  color.style.background = BLOCK_COLORS[PLACEABLE[i]];

  const label = document.createElement("div");
  label.textContent = BLOCK_NAMES[PLACEABLE[i]];

  const num = document.createElement("div");
  num.textContent = String(i + 1);
  num.style.marginTop = "2px";
  num.style.fontSize = "10px";
  num.style.opacity = "0.75";

  slot.appendChild(color);
  slot.appendChild(label);
  slot.appendChild(num);

  hotbar.appendChild(slot);
}

function selectSlot(i) {
  selected = ((i % PLACEABLE.length) + PLACEABLE.length) % PLACEABLE.length;

  const slots = hotbar.children;
  for (let k = 0; k < slots.length; k++) {
    slots[k].classList.toggle("active", k === selected);
  }
}

function showToast(text) {
  toast.textContent = text;
  toast.style.opacity = "1";
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => {
    toast.style.opacity = "0";
  }, 1200);
}

function updateModeText() {
  modeText.textContent = flying ? "フライ" : "通常";
}

function updateHotbar() {
  selectSlot(selected);
}

/* ------------------------------------------------------------------
   入力
------------------------------------------------------------------ */
const keys = {};

window.addEventListener("keydown", (e) => {
  keys[e.code] = true;

  if (e.code === "KeyF") {
    flying = !flying;
    velocityY = 0;
    updateModeText();
    showToast(flying ? "フライモード: ON" : "フライモード: OFF");
  }

  if (e.code === "KeyR") {
    resetPlayer();
    showToast("プレイヤーを復帰しました");
  }

  if (e.code.startsWith("Digit")) {
    const n = Number(e.code.slice(5));
    if (n >= 1 && n <= PLACEABLE.length) {
      selectSlot(n - 1);
    }
  }
});

window.addEventListener("keyup", (e) => {
  keys[e.code] = false;
});

window.addEventListener("wheel", (e) => {
  if (!controls.isLocked) return;

  if (e.deltaY > 0) selectSlot(selected + 1);
  if (e.deltaY < 0) selectSlot(selected - 1);
}, { passive: true });

renderer.domElement.addEventListener("contextmenu", (e) => e.preventDefault());

window.addEventListener("mousedown", (e) => {
  if (!controls.isLocked) return;

  if (e.button === 0) placeBlock();
  else if (e.button === 2) breakBlock();
});

const overlay = document.getElementById("overlay");
const startBtn = document.getElementById("start");

startBtn.addEventListener("click", () => {
  controls.lock();
});

controls.addEventListener("lock", () => {
  overlay.style.display = "none";
});

controls.addEventListener("unlock", () => {
  overlay.style.display = "flex";
});

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

/* ------------------------------------------------------------------
   ゲームループ
------------------------------------------------------------------ */
generateWorld();
rebuildWorld();
resetPlayer();

const clock = new THREE.Clock();
const tmpForward = new THREE.Vector3();
const tmpRight = new THREE.Vector3();
const worldUp = new THREE.Vector3(0, 1, 0);

function tryStepMoveX(newX) {
  if (!collides(newX, playerPos.y, playerPos.z)) {
    playerPos.x = newX;
    return;
  }

  for (let step = 0.06; step <= 0.62; step += 0.06) {
    const testY = playerPos.y + step;
    if (!collides(newX, testY, playerPos.z) && collides(newX, testY - 0.05, playerPos.z)) {
      playerPos.y = testY;
      playerPos.x = newX;
      return;
    }
  }
}

function tryStepMoveZ(newZ) {
  if (!collides(playerPos.x, playerPos.y, newZ)) {
    playerPos.z = newZ;
    return;
  }

  for (let step = 0.06; step <= 0.62; step += 0.06) {
    const testY = playerPos.y + step;
    if (!collides(playerPos.x, testY, newZ) && collides(playerPos.x, testY - 0.05, newZ)) {
      playerPos.y = testY;
      playerPos.z = newZ;
      return;
    }
  }
}

function updatePlayer(dt) {
  camera.getWorldDirection(tmpForward);
  tmpForward.y = 0;

  if (tmpForward.lengthSq() < 1e-6) {
    tmpForward.set(0, 0, -1);
  } else {
    tmpForward.normalize();
  }

  tmpRight.crossVectors(tmpForward, worldUp).normalize();

  const wish = new THREE.Vector3();

  if (keys["KeyW"]) wish.add(tmpForward);
  if (keys["KeyS"]) wish.sub(tmpForward);
  if (keys["KeyD"]) wish.add(tmpRight);
  if (keys["KeyA"]) wish.sub(tmpRight);

  if (wish.lengthSq() > 0) wish.normalize();

  if (flying) {
    const moveSpeed = keys["ControlLeft"] || keys["ControlRight"] ? FLY_SPEED * 0.45 : FLY_SPEED;

    const dx = wish.x * moveSpeed * dt;
    const dz = wish.z * moveSpeed * dt;

    if (Math.abs(dx) > 1e-6) {
      const newX = playerPos.x + dx;
      if (!collides(newX, playerPos.y, playerPos.z)) playerPos.x = newX;
    }

    if (Math.abs(dz) > 1e-6) {
      const newZ = playerPos.z + dz;
      if (!collides(playerPos.x, playerPos.y, newZ)) playerPos.z = newZ;
    }

    let vy = 0;
    if (keys["Space"]) vy += moveSpeed;
    if (keys["ShiftLeft"] || keys["ShiftRight"]) vy -= moveSpeed;

    const newY = playerPos.y + vy * dt;

    if (!collides(playerPos.x, newY, playerPos.z)) {
      playerPos.y = newY;
      velocityY = 0;
      onGround = false;
    } else {
      velocityY = 0;
    }

  } else {
    const moveSpeed = keys["ControlLeft"] || keys["ControlRight"] ? WALK_SPEED * 0.42 : WALK_SPEED;

    const dx = wish.x * moveSpeed * dt;
    const dz = wish.z * moveSpeed * dt;

    if (Math.abs(dx) > 1e-6) tryStepMoveX(playerPos.x + dx);
    if (Math.abs(dz) > 1e-6) tryStepMoveZ(playerPos.z + dz);

    onGround =
      collides(playerPos.x, playerPos.y - 0.06, playerPos.z) ||
      collides(playerPos.x, playerPos.y - 0.001, playerPos.z);

    velocityY -= GRAVITY * dt;

    if (onGround && keys["Space"]) {
      velocityY = JUMP_SPEED;
    }

    const dy = velocityY * dt;
    const newY = playerPos.y + dy;

    if (!collides(playerPos.x, newY, playerPos.z)) {
      playerPos.y = newY;
      if (dy < 0) onGround = false;
    } else {
      if (dy < 0) {
        velocityY = 0;
        onGround = true;
      } else {
        velocityY = -1;
      }
    }
  }

  if (playerPos.y < -25) resetPlayer();

  camera.position.set(playerPos.x, playerPos.y + EYE_HEIGHT, playerPos.z);
}

function animate() {
  requestAnimationFrame(animate);

  const dt = Math.min(clock.getDelta(), 0.05);

  if (controls.isLocked) {
    updatePlayer(dt);
  }

  renderer.render(scene, camera);
}

animate();
</script>
</body>
</html>
```

---

### 遊び方のメモ
- **左クリック**で視線上のブロックの隣にブロックを設置
- **右クリック**でブロックを破壊
- **1〜8** または **ホイール**でブロック種切り替え
- **F**でフライモード
- **R**で初期位置復帰
- ブロックを置く位置が自分の体と重なる場合は置けません

### 拡張案
- クラフト・インベントリ追加
- 水中とスウォム
- チャンク分割で巨大マップ化
- セーブ／ロード
- マルチプレイ

必要なら「水中追加」「セーブ追加」「巨大地形生成」などもそのまま拡張できます。