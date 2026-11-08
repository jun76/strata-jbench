以下、単一の `index.html` として保存すれば、ブラウザでそのまま遊べるマイクラ風3D箱庭ゲームです。

必要：最近のブラウザ（Chrome / Edge / Firefox / Safari）。Three.js を CDN から読み込みます。

```html
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>マイクラ風 3D箱庭ゲーム</title>
<style>
  html, body {
    margin: 0;
    height: 100%;
    overflow: hidden;
    background: #87ceeb;
    font-family: system-ui, -apple-system, "Segoe UI", "Hiragino Sans", "Noto Sans JP", sans-serif;
    user-select: none;
  }

  #game {
    display: block;
    width: 100%;
    height: 100%;
    outline: none;
  }

  #ui {
    position: absolute;
    inset: 0;
    pointer-events: none;
    color: #fff;
    text-shadow: 1px 1px 0 rgba(0,0,0,.8);
  }

  #topbar {
    position: absolute;
    top: 10px;
    left: 10px;
    line-height: 1.5;
    font-size: 13px;
    background: rgba(0,0,0,.32);
    padding: 8px 10px;
    border-radius: 8px;
    max-width: 480px;
  }

  #topbar b {
    font-size: 16px;
  }

  #status {
    margin-top: 6px;
    opacity: .9;
  }

  #hint {
    margin-top: 6px;
    opacity: .85;
  }

  #crosshair {
    position: absolute;
    left: 50%;
    top: 50%;
    width: 24px;
    height: 24px;
    transform: translate(-50%, -50%);
    mix-blend-mode: difference;
  }

  #crosshair::before,
  #crosshair::after {
    content: "";
    position: absolute;
    background: rgba(255,255,255,.9);
  }

  #crosshair::before {
    left: 11px;
    top: 3px;
    width: 2px;
    height: 18px;
  }

  #crosshair::after {
    left: 3px;
    top: 11px;
    width: 18px;
    height: 2px;
  }

  #hotbar {
    position: absolute;
    left: 50%;
    bottom: 22px;
    transform: translateX(-50%);
    display: flex;
    gap: 7px;
    background: rgba(0,0,0,.30);
    padding: 7px;
    border-radius: 10px;
  }

  .slot {
    position: relative;
    width: 52px;
    height: 52px;
    border: 3px solid rgba(0,0,0,.35);
    border-radius: 6px;
    background: #777;
    box-shadow: inset 0 0 0 2px rgba(255,255,255,.25);
  }

  .slot.sel {
    border-color: #fff;
    box-shadow:
      inset 0 0 0 2px rgba(255,255,255,.45),
      0 0 0 3px rgba(0,0,0,.25),
      0 0 14px rgba(255,255,255,.35);
    transform: translateY(-3px);
  }

  .slot .num {
    position: absolute;
    left: 4px;
    bottom: 3px;
    font-size: 13px;
    color: #fff;
    text-shadow:
      0 1px 1px #000,
      0 -1px 1px #000,
      1px 0 1px #000,
      -1px 0 1px #000;
  }

  .slot .label {
    position: absolute;
    right: 4px;
    bottom: 3px;
    font-size: 11px;
    opacity: .95;
  }

  #lockHint {
    position: absolute;
    left: 50%;
    top: 58%;
    transform: translate(-50%, 0);
    font-size: 16px;
    background: rgba(0,0,0,.55);
    padding: 10px 14px;
    border-radius: 8px;
    pointer-events: none;
  }
</style>
</head>
<body>
<canvas id="game"></canvas>

<div id="ui">
  <div id="topbar">
    <b>マイクラ風 3D箱庭ゲーム</b><br>
    WASD:移動 / Space:ジャンプ / Shift:ゆっくり移動<br>
    左クリック:壊す / 右クリック:置く / 1〜6:ブロック選択<br>
    <div id="status"></div>
    <div id="hint">クリックしてマウス操作を有効にします。</div>
  </div>

  <div id="crosshair"></div>
  <div id="hotbar"></div>
  <div id="lockHint">画面をクリックして開始</div>
</div>

<script type="module">
import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js";

// ----------------------------
// 基本セット
// ----------------------------
const canvas = document.getElementById("game");

const renderer = new THREE.WebGLRenderer({
  canvas,
  antialias: true,
  powerPreference: "high-performance"
});
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 28, 170);

const camera = new THREE.PerspectiveCamera(75, innerWidth / innerHeight, 0.1, 500);
camera.rotation.order = "YXZ";

// ----------------------------
// ブロック定義
// ----------------------------
const AIR = 0;
const GRASS = 1;
const DIRT = 2;
const STONE = 3;
const WOOD = 4;
const LEAF = 5;
const SAND = 6;
const BEDROCK = 7;

const BLOCKS = {
  [GRASS]: {
    name: "草",
    hotbar: true,
    colors: {
      top: 0x74ab55,
      side: 0x856038,
      bottom: 0x6d4b2f
    }
  },
  [DIRT]: {
    name: "土",
    hotbar: true,
    colors: {
      top: 0x856038,
      side: 0x77522f,
      bottom: 0x664223
    }
  },
  [STONE]: {
    name: "石",
    hotbar: true,
    colors: {
      top: 0x9a9a9a,
      side: 0x888888,
      bottom: 0x757575
    }
  },
  [WOOD]: {
    name: "木",
    hotbar: true,
    colors: {
      top: 0xa88665,
      side: 0x6b4a2f,
      bottom: 0x6b4a2f
    }
  },
  [LEAF]: {
    name: "葉",
    hotbar: true,
    colors: {
      top: 0x407c45,
      side: 0x366a3c,
      bottom: 0x2d5a33
    }
  },
  [SAND]: {
    name: "砂",
    hotbar: true,
    colors: {
      top: 0xe6d58f,
      side: 0xdcc882,
      bottom: 0xc8b772
    }
  },
  [BEDROCK]: {
    name: "岩盤",
    hotbar: false,
    colors: {
      top: 0x555555,
      side: 0x444444,
      bottom: 0x333333
    }
  }
};

const HOTBAR = [GRASS, DIRT, STONE, WOOD, LEAF, SAND];

// ----------------------------
// ワールド
// ----------------------------
const WORLD_SIZE = 64;
const WORLD_HEIGHT = 36;

const blocks = new Map(); // "x,y,z" -> blockType

let dirty = true;

function key(x, y, z) {
  return `${x},${y},${z}`;
}

function getBlock(x, y, z) {
  return blocks.get(key(x, y, z)) ?? AIR;
}

function isSolid(x, y, z) {
  return blocks.has(key(x, y, z));
}

function setBlock(x, y, z, type) {
  blocks.set(key(x, y, z), type);
  dirty = true;
}

function removeBlock(x, y, z) {
  const k = key(x, y, z);
  const id = blocks.get(k);
  if (id === undefined || id === BEDROCK) return false;
  blocks.delete(k);
  dirty = true;
  return true;
}

// ----------------------------
// 地形生成
// ----------------------------
const heightMap = new Int8Array(WORLD_SIZE * WORLD_SIZE);

function seededRandom(seed) {
  let s = seed >>> 0;
  return function () {
    s = (s * 1664525 + 1013904223) >>> 0;
    return s / 4294967296;
  };
}

function generateWorld() {
  blocks.clear();
  heightMap.fill(0);

  const rand = seededRandom(987654321);

  for (let x = 0; x < WORLD_SIZE; x++) {
    for (let z = 0; z < WORLD_SIZE; z++) {
      // 軽量なノイズっぽい起伏
      let h = 10
        + 4 * Math.sin(x * 0.11)
        + 3 * Math.cos(z * 0.13)
        + 2 * Math.sin((x + z) * 0.07)
        + 1.5 * Math.cos((x - z) * 0.05);

      h = Math.max(4, Math.min(20, Math.round(h)));
      heightMap[x * WORLD_SIZE + z] = h;

      for (let y = 0; y <= h; y++) {
        let type;

        if (y === 0) {
          type = BEDROCK;
        } else if (h <= 7) {
          type = y === h ? SAND : DIRT;
        } else {
          if (y === h) type = GRASS;
          else if (y >= h - 2) type = DIRT;
          else type = STONE;
        }

        blocks.set(key(x, y, z), type);
      }
    }
  }

  // 木を植える
  for (let x = 2; x < WORLD_SIZE - 2; x++) {
    for (let z = 2; z < WORLD_SIZE - 2; z++) {
      const h = heightMap[x * WORLD_SIZE + z];
      if (h < 9 || h > 18) continue;
      if (rand() > 0.035) continue;

      const base = h + 1;
      const trunkHeight = 5 + Math.floor(rand() * 3);
      const top = base + trunkHeight - 1;

      // 幹
      for (let ty = 0; ty < trunkHeight; ty++) {
        const y = base + ty;
        if (y < WORLD_HEIGHT) {
          blocks.set(key(x, y, z), WOOD);
        }
      }

      // 葉
      for (let dy = -2; dy <= 1; dy++) {
        const y = top + dy;
        if (y < 0 || y >= WORLD_HEIGHT) continue;

        let r;
        let r2;

        if (dy <= -1) {
          r = 2;
          r2 = 4;
        } else if (dy === 0) {
          r = 1;
          r2 = 1;
        } else {
          r = 0;
          r2 = 0;
        }

        for (let dx = -r; dx <= r; dx++) {
          for (let dz = -r; dz <= r; dz++) {
            if (dx * dx + dz * dz > r2) continue;
            if (dy <= 0 && dx === 0 && dz === 0) continue;

            const tx = x + dx;
            const tz = z + dz;

            if (tx < 0 || tx >= WORLD_SIZE || tz < 0 || tz >= WORLD_SIZE) continue;

            const k = key(tx, y, tz);
            if (!blocks.has(k)) {
              blocks.set(k, LEAF);
            }
          }
        }
      }
    }
  }
}

// ----------------------------
// メッシュ生成
// ----------------------------
const FACES = [
  // +X
  {
    kind: "side",
    shade: 0.92,
    corners: [[1,0,0], [1,0,1], [1,1,1], [1,1,0]]
  },
  // -X
  {
    kind: "side",
    shade: 0.80,
    corners: [[0,0,1], [0,0,0], [0,1,0], [0,1,1]]
  },
  // +Y
  {
    kind: "top",
    shade: 1.00,
    corners: [[0,1,0], [0,1,1], [1,1,1], [1,1,0]]
  },
  // -Y
  {
    kind: "bottom",
    shade: 0.62,
    corners: [[0,0,0], [1,0,0], [1,0,1], [0,0,1]]
  },
  // +Z
  {
    kind: "side",
    shade: 0.88,
    corners: [[1,0,1], [0,0,1], [0,1,1], [1,1,1]]
  },
  // -Z
  {
    kind: "side",
    shade: 0.74,
    corners: [[0,0,0], [1,0,0], [1,1,0], [0,1,0]]
  }
];

const FACE_DIRS = [
  [1, 0, 0],
  [-1, 0, 0],
  [0, 1, 0],
  [0, -1, 0],
  [0, 0, 1],
  [0, 0, -1]
];

const worldMaterial = new THREE.MeshBasicMaterial({
  vertexColors: true,
  side: THREE.DoubleSide,
  fog: true
});

const worldGeometry = new THREE.BufferGeometry();
const worldMesh = new THREE.Mesh(worldGeometry, worldMaterial);
worldMesh.frustumCulled = false;
scene.add(worldMesh);

const tmpColor = new THREE.Color();

function rebuildWorldMesh() {
  const positions = [];
  const colors = [];
  const indices = [];

  let vertexCount = 0;

  for (const [k, type] of blocks) {
    const block = BLOCKS[type];
    if (!block) continue;

    const parts = k.split(",");
    const x = +parts[0];
    const y = +parts[1];
    const z = +parts[2];

    for (let f = 0; f < 6; f++) {
      const d = FACE_DIRS[f];
      const nx = x + d[0];
      const ny = y + d[1];
      const nz = z + d[2];

      // 隣にブロックがない面だけ作る
      if (!blocks.has(key(nx, ny, nz))) {
        const face = FACES[f];
        const hex = block.colors[face.kind];
        tmpColor.setHex(hex).multiplyScalar(face.shade);

        for (const p of face.corners) {
          positions.push(x + p[0], y + p[1], z + p[2]);
          colors.push(tmpColor.r, tmpColor.g, tmpColor.b);
        }

        indices.push(
          vertexCount, vertexCount + 1, vertexCount + 2,
          vertexCount, vertexCount + 2, vertexCount + 3
        );

        vertexCount += 4;
      }
    }
  }

  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
  geo.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));
  geo.setIndex(indices);
  geo.computeBoundingSphere();

  worldMesh.geometry.dispose();
  worldMesh.geometry = geo;

  dirty = false;
}

// ----------------------------
// ハイライト
// ----------------------------
const highlightBox = new THREE.LineSegments(
  new THREE.EdgesGeometry(new THREE.BoxGeometry(1.004, 1.004, 1.004)),
  new THREE.LineBasicMaterial({
    color: 0x000000,
    transparent: true,
    opacity: 0.55
  })
);
highlightBox.visible = false;
highlightBox.renderOrder = 1;
scene.add(highlightBox);

// ----------------------------
// 雲・太陽
// ----------------------------
const cloudMaterial = new THREE.MeshBasicMaterial({
  color: 0xffffff,
  transparent: true,
  opacity: 0.72,
  fog: true,
  side: THREE.DoubleSide
});

const clouds = new THREE.Group();
scene.add(clouds);

{
  const cloudRand = seededRandom(20240901);
  for (let i = 0; i < 22; i++) {
    const w = 12 + cloudRand() * 32;
    const d = 8 + cloudRand() * 24;
    const h = 1.5 + cloudRand() * 2.5;

    const cloud = new THREE.Mesh(
      new THREE.BoxGeometry(w, h, d),
      cloudMaterial
    );

    cloud.position.set(
      (cloudRand() - 0.5) * 360,
      70 + cloudRand() * 30,
      (cloudRand() - 0.5) * 360
    );

    cloud.scale.y = 0.55;
    clouds.add(cloud);
  }
}

const sun = new THREE.Mesh(
  new THREE.SphereGeometry(10, 24, 16),
  new THREE.MeshBasicMaterial({
    color: 0xffe066,
    fog: false
  })
);
sun.position.set(120, 180, 90);
scene.add(sun);

// ----------------------------
// プレイヤー
// ----------------------------
const player = {
  x: 0,
  y: 0,
  z: 0,
  vx: 0,
  vy: 0,
  vz: 0,
  yaw: 0,
  pitch: 0,
  onGround: false
};

const EYE_HEIGHT = 1.62;
const PLAYER_HALF = 0.3;
const PLAYER_HEIGHT = 1.8;
const GRAVITY = 28;
const JUMP_SPEED = 9.0;
const WALK_SPEED = 4.6;
const SNEAK_SPEED = 2.2;

function spawnPlayer() {
  const cx = Math.floor(WORLD_SIZE / 2);
  const cz = Math.floor(WORLD_SIZE / 2);
  player.x = cx + 0.5;
  player.z = cz + 0.5;
  player.y = heightMap[cx * WORLD_SIZE + cz] + 1.1;
  player.vx = player.vy = player.vz = 0;
  player.yaw = 0;
  player.pitch = 0;
}

// ----------------------------
// 当たり判定
// ----------------------------
function intersectsPlayer(x, y, z) {
  const minX = player.x - PLAYER_HALF;
  const maxX = player.x + PLAYER_HALF;
  const minY = player.y;
  const maxY = player.y + PLAYER_HEIGHT;
  const minZ = player.z - PLAYER_HALF;
  const maxZ = player.z + PLAYER_HALF;

  const bx0 = x;
  const bx1 = x + 1;
  const by0 = y;
  const by1 = y + 1;
  const bz0 = z;
  const bz1 = z + 1;

  return (
    maxX > bx0 &&
    minX < bx1 &&
    maxY > by0 &&
    minY < by1 &&
    maxZ > bz0 &&
    minZ < bz1
  );
}

function collides(px, py, pz) {
  const minX = px - PLAYER_HALF;
  const maxX = px + PLAYER_HALF;
  const minY = py;
  const maxY = py + PLAYER_HEIGHT;
  const minZ = pz - PLAYER_HALF;
  const maxZ = pz + PLAYER_HALF;

  const eps = 0.001;

  const x0 = Math.floor(minX + eps);
  const x1 = Math.floor(maxX - eps);
  const y0 = Math.floor(minY + eps);
  const y1 = Math.floor(maxY - eps);
  const z0 = Math.floor(minZ + eps);
  const z1 = Math.floor(maxZ - eps);

  for (let x = x0; x <= x1; x++) {
    for (let y = y0; y <= y1; y++) {
      for (let z = z0; z <= z1; z++) {
        if (blocks.has(key(x, y, z))) return true;
      }
    }
  }

  return false;
}

function blockOverlapsPlayer(x, y, z) {
  return intersectsPlayer(x, y, z);
}

// ----------------------------
// レイキャスト（ボクセル用DDA）
// ----------------------------
const raycastDir = new THREE.Vector3();

function raycastBlock(origin, direction, maxDistance = 7) {
  const dir = direction;

  if (
    Math.abs(dir.x) + Math.abs(dir.y) + Math.abs(dir.z) < 1e-8
  ) {
    return null;
  }

  let x = Math.floor(origin.x);
  let y = Math.floor(origin.y);
  let z = Math.floor(origin.z);

  const stepX = dir.x > 0 ? 1 : dir.x < 0 ? -1 : 0;
  const stepY = dir.y > 0 ? 1 : dir.y < 0 ? -1 : 0;
  const stepZ = dir.z > 0 ? 1 : dir.z < 0 ? -1 : 0;

  const tDeltaX = stepX !== 0 ? Math.abs(1 / dir.x) : Infinity;
  const tDeltaY = stepY !== 0 ? Math.abs(1 / dir.y) : Infinity;
  const tDeltaZ = stepZ !== 0 ? Math.abs(1 / dir.z) : Infinity;

  let tMaxX = stepX > 0
    ? (x + 1 - origin.x) / dir.x
    : stepX < 0
    ? (origin.x - x) / -dir.x
    : Infinity;

  let tMaxY = stepY > 0
    ? (y + 1 - origin.y) / dir.y
    : stepY < 0
    ? (origin.y - y) / -dir.y
    : Infinity;

  let tMaxZ = stepZ > 0
    ? (z + 1 - origin.z) / dir.z
    : stepZ < 0
    ? (origin.z - z) / -dir.z
    : Infinity;

  let t = 0;

  // 最初のセルが固体なら、一旦外に出ることは考えない。
  // プレイヤー位置は物理で固体内に入らないようになっている。
  while (t <= maxDistance) {
    if (tMaxX < tMaxY && tMaxX < tMaxZ) {
      t = tMaxX;
      x += stepX;
      tMaxX += tDeltaX;

      if (blocks.has(key(x, y, z))) {
        return {
          x, y, z,
          nx: -stepX,
          ny: 0,
          nz: 0,
          distance: t
        };
      }
    } else if (tMaxY < tMaxX && tMaxY < tMaxZ) {
      t = tMaxY;
      y += stepY;
      tMaxY += tDeltaY;

      if (blocks.has(key(x, y, z))) {
        return {
          x, y, z,
          nx: 0,
          ny: -stepY,
          nz: 0,
          distance: t
        };
      }
    } else {
      t = tMaxZ;
      z += stepZ;
      tMaxZ += tDeltaZ;

      if (blocks.has(key(x, y, z))) {
        return {
          x, y, z,
          nx: 0,
          ny: 0,
          nz: -stepZ,
          distance: t
        };
      }
    }
  }

  return null;
}

// ----------------------------
// 入力
// ----------------------------
const keys = new Set();

const statusEl = document.getElementById("status");
const hintEl = document.getElementById("hint");
const lockHintEl = document.getElementById("lockHint");
const hotbarEl = document.getElementById("hotbar");

let selectedType = HOTBAR[0];

function updateSelectedUI() {
  for (const slot of hotbarEl.children) {
    const id = +slot.dataset.id;
    slot.classList.toggle("sel", id === selectedType);
  }
}

function createHotbar() {
  hotbarEl.innerHTML = "";

  HOTBAR.forEach((id, idx) => {
    const b = BLOCKS[id];
    const slot = document.createElement("div");
    slot.className = "slot";
    slot.dataset.id = id;

    const top = "#" + b.colors.top.toString(16).padStart(6, "0");
    const side = "#" + b.colors.side.toString(16).padStart(6, "0");

    slot.style.background = `linear-gradient(180deg,
      ${top} 0%, ${top} 38%, ${side} 38%, ${side} 100%)`;

    slot.innerHTML = `
      <span class="num">${idx + 1}</span>
      <span class="label">${b.name}</span>
    `;

    hotbarEl.appendChild(slot);
  });

  updateSelectedUI();
}

createHotbar();

window.addEventListener("keydown", (e) => {
  if (e.code === "Space") e.preventDefault();

  keys.add(e.code);

  if (e.code === "Digit1") selectSlot(0);
  if (e.code === "Digit2") selectSlot(1);
  if (e.code === "Digit3") selectSlot(2);
  if (e.code === "Digit4") selectSlot(3);
  if (e.code === "Digit5") selectSlot(4);
  if (e.code === "Digit6") selectSlot(5);

  if (e.code === "Escape") {
    hintEl.textContent = "ESCでロック解除。画面をクリックして再開始。";
  }
});

window.addEventListener("keyup", (e) => {
  keys.delete(e.code);
});

function selectSlot(index) {
  if (index < 0 || index >= HOTBAR.length) return;
  selectedType = HOTBAR[index];
  updateSelectedUI();
}

// ----------------------------
// ポインターロック
// ----------------------------
let locked = false;

document.addEventListener("pointerlockchange", () => {
  locked = document.pointerLockElement === canvas;

  if (locked) {
    hintEl.textContent = "マウスで視点移動 / クリックで編集";
    lockHintEl.style.display = "none";
  } else {
    hintEl.textContent = "クリックしてマウス操作を有効にします。";
    lockHintEl.style.display = "block";
  }
});

canvas.addEventListener("click", () => {
  if (!locked) {
    canvas.requestPointerLock();
  }
});

window.addEventListener("mousemove", (e) => {
  if (!locked) return;

  const sens = 0.0022;
  player.yaw -= e.movementX * sens;
  player.pitch -= e.movementY * sens;

  player.pitch = Math.max(-1.5, Math.min(1.5, player.pitch));
});

// ----------------------------
// ブロック編集
// ----------------------------
let currentTarget = null;

function updateTarget() {
  camera.getWorldDirection(raycastDir);
  currentTarget = raycastBlock(camera.position, raycastDir, 7);

  if (currentTarget) {
    highlightBox.visible = true;
    highlightBox.position.set(
      currentTarget.x + 0.5,
      currentTarget.y + 0.5,
      currentTarget.z + 0.5
    );
  } else {
    highlightBox.visible = false;
  }
}

function tryBreak() {
  if (!currentTarget) return;
  removeBlock(currentTarget.x, currentTarget.y, currentTarget.z);
  updateTarget();
}

function tryPlace() {
  if (!currentTarget) return;

  const x = currentTarget.x + currentTarget.nx;
  const y = currentTarget.y + currentTarget.ny;
  const z = currentTarget.z + currentTarget.nz;

  if (y < 0 || y > WORLD_HEIGHT + 32) return;
  if (blocks.has(key(x, y, z))) return;
  if (blockOverlapsPlayer(x, y, z)) return;

  setBlock(x, y, z, selectedType);
  updateTarget();
}

window.addEventListener("mousedown", (e) => {
  if (!locked) return;

  if (e.button === 0) {
    tryBreak();
  } else if (e.button === 2) {
    tryPlace();
  }
});

window.addEventListener("contextmenu", (e) => {
  e.preventDefault();
});

// ----------------------------
// プレイヤー更新
// ----------------------------
const tmpVec = new THREE.Vector3();

function updatePlayer(dt) {
  // 地面判定
  player.onGround = collides(player.x, player.y - 0.06, player.z);

  // 入力方向
  let ix = 0;
  let iz = 0;

  if (keys.has("KeyW")) {
    ix -= Math.sin(player.yaw);
    iz -= Math.cos(player.yaw);
  }
  if (keys.has("KeyS")) {
    ix += Math.sin(player.yaw);
    iz += Math.cos(player.yaw);
  }
  if (keys.has("KeyA")) {
    ix -= Math.cos(player.yaw);
    iz += Math.sin(player.yaw);
  }
  if (keys.has("KeyD")) {
    ix += Math.cos(player.yaw);
    iz -= Math.sin(player.yaw);
  }

  const len = Math.hypot(ix, iz);
  if (len > 0) {
    ix /= len;
    iz /= len;
  }

  const speed = keys.has("ShiftLeft") || keys.has("ShiftRight") ? SNEAK_SPEED : WALK_SPEED;
  const desiredVx = ix * speed;
  const desiredVz = iz * speed;

  const control = player.onGround ? 22 : 6.5;
  const blend = Math.min(1, control * dt);

  player.vx += (desiredVx - player.vx) * blend;
  player.vz += (desiredVz - player.vz) * blend;

  // ジャンプ
  if (keys.has("Space") && player.onGround) {
    player.vy = JUMP_SPEED;
    keys.delete("Space");
  }

  // 重力
  player.vy -= GRAVITY * dt;

  if (player.vy < -80) player.vy = -80;

  // X移動
  const dx = player.vx * dt;
  player.x += dx;
  if (collides(player.x, player.y, player.z)) {
    player.x -= dx;
    player.vx = 0;
  }

  // Z移動
  const dz = player.vz * dt;
  player.z += dz;
  if (collides(player.x, player.y, player.z)) {
    player.z -= dz;
    player.vz = 0;
  }

  // Y移動
  const dy = player.vy * dt;
  const oldY = player.y;
  player.y += dy;
  if (collides(player.x, player.y, player.z)) {
    player.y = oldY;

    if (player.vy < 0) {
      player.onGround = true;
    }

    player.vy = 0;
  }

  // 落としたら復帰
  if (player.y < -25) {
    spawnPlayer();
  }

  // カメラ反映
  camera.position.set(player.x, player.y + EYE_HEIGHT, player.z);
  camera.rotation.set(player.pitch, player.yaw, 0, "YXZ");
}

// ----------------------------
// ステータス表示
// ----------------------------
function updateStatus() {
  const selectedName = BLOCKS[selectedType].name;
  statusEl.textContent =
    `位置: ${player.x.toFixed(1)}, ${player.y.toFixed(1)}, ${player.z.toFixed(1)} / ` +
    `ブロック: ${blocks.size} / 選択: ${selectedName}`;
}

// ----------------------------
// 雲更新
// ----------------------------
function updateClouds(dt) {
  for (const cloud of clouds.children) {
    cloud.position.x += dt * 3.5;
    if (cloud.position.x > 220) cloud.position.x = -220;
  }
}

// ----------------------------
// リサイズ
// ----------------------------
window.addEventListener("resize", () => {
  renderer.setSize(innerWidth, innerHeight);
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
});

// ----------------------------
// 開始
// ----------------------------
generateWorld();
spawnPlayer();
rebuildWorldMesh();

let prevTime = performance.now();

function animate() {
  requestAnimationFrame(animate);

  const now = performance.now();
  const dt = Math.min(0.05, (now - prevTime) / 1000);
  prevTime = now;

  updatePlayer(dt);
  updateTarget();
  updateClouds(dt);

  if (dirty) {
    rebuildWorldMesh();
  }

  updateStatus();
  renderer.render(scene, camera);
}

animate();
</script>
</body>
</html>
```