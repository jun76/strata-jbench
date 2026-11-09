以下は、**単一 HTML に保存してブラウザで開くだけで動くマイクラ風 3D 箱庭ゲーム**です。  
WASD で移動、マウスで視点、左クリックで破壊、右クリックで設置できます。

```html
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Voxel Sandbox</title>
<style>
  html, body {
    margin: 0;
    height: 100%;
    overflow: hidden;
    background: #87ceeb;
    font-family: system-ui, -apple-system, "Hiragino Sans", "Noto Sans JP", sans-serif;
    user-select: none;
  }

  canvas {
    display: block;
  }

  #overlay {
    position: absolute;
    inset: 0;
    background: rgba(0,0,0,0.62);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    z-index: 50;
  }

  #panel {
    background: rgba(20,20,20,0.95);
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 14px;
    padding: 24px 28px;
    max-width: 520px;
    text-align: center;
  }

  #panel h1 {
    margin: 0 0 10px;
    font-size: 28px;
  }

  #panel p {
    margin: 8px 0;
    color: #ddd;
    line-height: 1.55;
  }

  #play {
    margin-top: 16px;
    padding: 12px 28px;
    border: none;
    border-radius: 10px;
    background: #25d366;
    color: #fff;
    font-size: 17px;
    font-weight: 700;
    cursor: pointer;
  }

  #play:hover {
    filter: brightness(1.08);
  }

  #hud {
    position: absolute;
    inset: 0;
    pointer-events: none;
    color: #fff;
    text-shadow: 0 0 4px rgba(0,0,0,0.6);
  }

  #crosshair {
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    width: 22px;
    height: 22px;
  }

  #crosshair::before,
  #crosshair::after {
    content: "";
    position: absolute;
    background: rgba(255,255,255,0.85);
  }

  #crosshair::before {
    left: 10px;
    top: 0;
    width: 2px;
    height: 22px;
  }

  #crosshair::after {
    left: 0;
    top: 10px;
    width: 22px;
    height: 2px;
  }

  #info,
  #status {
    position: absolute;
    top: 12px;
    left: 12px;
    background: rgba(0,0,0,0.38);
    border-radius: 10px;
    padding: 9px 12px;
    font-size: 13px;
    line-height: 1.45;
    white-space: pre-line;
  }

  #status {
    left: auto;
    right: 12px;
  }

  #hotbar {
    position: absolute;
    bottom: 18px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: 8px;
    background: rgba(0,0,0,0.30);
    border-radius: 12px;
    padding: 8px;
  }

  .slot {
    width: 44px;
    height: 44px;
    border-radius: 8px;
    border: 2px solid rgba(255,255,255,0.22);
    background: rgba(40,40,40,0.85);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    font-size: 11px;
    color: #fff;
  }

  .slot.sel {
    border-color: #fff;
    outline: 1px solid rgba(255,255,255,0.8);
    transform: translateY(-3px);
  }

  .sw {
    width: 24px;
    height: 24px;
    border-radius: 5px;
    border: 1px solid rgba(0,0,0,0.25);
  }

  #blockName {
    display: inline-block;
    min-width: 42px;
  }
</style>
</head>
<body>
<div id="overlay">
  <div id="panel">
    <h1>Voxel Sandbox</h1>
    <p>マイクラ風 3D 箱庭ゲーム</p>
    <p>
      W / A / S / D : 移動<br>
      Space : ジャンプ<br>
      マウス : 視点<br>
      左クリック : 破壊<br>
      右クリック : 設置<br>
      1〜8 / ホイール : ブロック選択
    </p>
    <button id="play">開始して操作する</button>
  </div>
</div>

<div id="hud">
  <div id="crosshair"></div>

  <div id="info">
    WASD 移動
Space ジャンプ
左クリック 破壊
右クリック 設置
    </div>

  <div id="status">FPS: 0</div>

  <div id="hotbar"></div>
</div>

<script type="module">
import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js";

// ----------------------------------------------------------------
// 定数
// ----------------------------------------------------------------
const SIZE = 64;
const HEIGHT = 24;
const MAX_BLOCKS = 200000;

const HALF_WIDTH = 0.3;
const HALF_HEIGHT = 0.9;
const EYE_Y = 0.7;

const REACH = 7.0;
const GRAVITY = -24.0;
const JUMP = 8.5;
const SPEED = 5.8;

const BLOCK = {
  AIR: 0,
  GRASS: 1,
  DIRT: 2,
  STONE: 3,
  WOOD: 4,
  LEAVES: 5,
  SAND: 6,
  BRICK: 7,
  GLASS: 8
};

const BLOCK_ORDER = [
  BLOCK.GRASS,
  BLOCK.DIRT,
  BLOCK.STONE,
  BLOCK.WOOD,
  BLOCK.LEAVES,
  BLOCK.SAND,
  BLOCK.BRICK,
  BLOCK.GLASS
];

const BLOCK_DEF = {
  [BLOCK.GRASS]:  { name: "草",    hex: 0x5da646, css: "#5da646" },
  [BLOCK.DIRT]:   { name: "土",    hex: 0x8b5a2b, css: "#8b5a2b" },
  [BLOCK.STONE]:  { name: "石",    hex: 0x8a8a8a, css: "#8a8a8a" },
  [BLOCK.WOOD]:   { name: "木",    hex: 0x9c6a3a, css: "#9c6a3a" },
  [BLOCK.LEAVES]: { name: "葉",    hex: 0x2f6f31, css: "#2f6f31" },
  [BLOCK.SAND]:   { name: "砂",    hex: 0xd6c08c, css: "#d6c08c" },
  [BLOCK.BRICK]:  { name: "レンガ", hex: 0xb0503f, css: "#b0503f" },
  [BLOCK.GLASS]:  { name: "ガラス", hex: 0x9ed7ff, css: "#9ed7ff" }
};

// ----------------------------------------------------------------
// Three.js 基礎
// ----------------------------------------------------------------
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 35, 180);

const camera = new THREE.PerspectiveCamera(
  75,
  window.innerWidth / window.innerHeight,
  0.1,
  500
);
camera.rotation.order = "YXZ";

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
document.body.appendChild(renderer.domElement);

const canvas = renderer.domElement;

const sun = new THREE.DirectionalLight(0xffffff, 1.05);
sun.position.set(50, 100, 40);
scene.add(sun);

const sky = new THREE.HemisphereLight(0xaedcff, 0x7d7465, 0.85);
scene.add(sky);

// ----------------------------------------------------------------
// ワールドデータ
// ----------------------------------------------------------------
const world = new Uint8Array(SIZE * SIZE * HEIGHT);
const blockIds = new Int32Array(world.length).fill(-1);
const heightMap = new Uint8Array(SIZE * SIZE);

function idx(x, y, z) {
  return x + SIZE * (z + SIZE * y);
}

function inBounds(x, y, z) {
  return x >= 0 && x < SIZE && y >= 0 && y < HEIGHT && z >= 0 && z < SIZE;
}

function getBlock(x, y, z) {
  if (!inBounds(x, y, z)) return 0;
  return world[idx(x, y, z)];
}

function setVoxel(x, y, z, type) {
  if (!inBounds(x, y, z)) return;
  world[idx(x, y, z)] = type;
}

// ----------------------------------------------------------------
// 軽量な procedural noise
// ----------------------------------------------------------------
function hash(x, z) {
  let n = (x * 1297463 + z * 1297467) | 0;
  n ^= n << 13;
  n ^= n >>> 7;
  n ^= n << 17;
  n ^= n >>> 10;
  return (n >>> 0) / 4294967295;
}

function smooth(t) {
  return t * t * (3 - 2 * t);
}

function valueNoise(x, z) {
  const x0 = Math.floor(x);
  const z0 = Math.floor(z);
  const x1 = x0 + 1;
  const z1 = z0 + 1;

  const fx = x - x0;
  const fz = z - z0;
  const ux = smooth(fx);
  const uz = smooth(fz);

  const v00 = hash(x0, z0);
  const v10 = hash(x1, z0);
  const v01 = hash(x0, z1);
  const v11 = hash(x1, z1);

  const a = v00 + (v10 - v00) * ux;
  const b = v01 + (v11 - v01) * ux;
  return a + (b - a) * uz;
}

function fbm(x, z) {
  return (
    valueNoise(x, z) * 0.55 +
    valueNoise(x * 2 + 11, z * 2 + 7) * 0.30 +
    valueNoise(x * 4 + 31, z * 4 + 13) * 0.15
  );
}

// ----------------------------------------------------------------
// ワールド生成
// ----------------------------------------------------------------
function generateWorld() {
  const center = SIZE >> 1;

  // 地形
  for (let x = 0; x < SIZE; x++) {
    for (let z = 0; z < SIZE; z++) {
      let h = Math.floor(
        4 +
        fbm(x * 0.07, z * 0.07) * 7 +
        fbm(x * 0.022, z * 0.022) * 5
      );
      h = Math.max(1, Math.min(HEIGHT - 6, h));

      const top = h <= 3 ? BLOCK.SAND : BLOCK.GRASS;

      for (let y = 0; y <= h; y++) {
        let type;
        if (y === h) {
          type = top;
        } else if (y > h - 3) {
          type = BLOCK.DIRT;
        } else {
          type = BLOCK.STONE;
        }
        setVoxel(x, y, z, type);
      }

      heightMap[x + SIZE * z] = h;
    }
  }

  // 木
  for (let x = 2; x < SIZE - 2; x++) {
    for (let z = 2; z < SIZE - 2; z++) {
      if (Math.abs(x - center) < 2 && Math.abs(z - center) < 2) continue;

      const h = heightMap[x + SIZE * z];
      if (h < 4 || h > 14) continue;
      if (getBlock(x, h, z) !== BLOCK.GRASS) continue;
      if (hash(x + 12345, z + 54321) >= 0.028) continue;

      const trunk = 4 + Math.floor(hash(x + 999, z + 888) * 3);
      const top = h + trunk;

      for (let y = h + 1; y <= top; y++) {
        if (y < HEIGHT) setVoxel(x, y, z, BLOCK.WOOD);
      }

      for (let ly = top - 2; ly <= top + 1; ly++) {
        const r = ly <= top - 1 ? 2 : 1;
        for (let dx = -r; dx <= r; dx++) {
          for (let dz = -r; dz <= r; dz++) {
            if (Math.abs(dx) + Math.abs(dz) > r + 1) continue;
            if (dx === 0 && dz === 0 && ly === top) continue;

            const px = x + dx;
            const pz = z + dz;
            if (getBlock(px, ly, pz) === BLOCK.AIR) {
              setVoxel(px, ly, pz, BLOCK.LEAVES);
            }
          }
        }
      }
    }
  }
}

// ----------------------------------------------------------------
// InstancedMesh で描画
// ----------------------------------------------------------------
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshLambertMaterial({
  color: 0xffffff,
  vertexColors: true
});

const mesh = new THREE.InstancedMesh(geometry, material, MAX_BLOCKS);
mesh.frustumCulled = false;
scene.add(mesh);

const tempMatrix = new THREE.Matrix4();
const tempQuat = new THREE.Quaternion();
const tempScale = new THREE.Vector3(1, 1, 1);
const tempVec = new THREE.Vector3();
const tempColor = new THREE.Color();

let usedInstances = 0;

function setInstance(id, x, y, z, type, on) {
  if (on) {
    tempVec.set(x + 0.5, y + 0.5, z + 0.5);
    tempMatrix.compose(tempVec, tempQuat, tempScale);
    mesh.setMatrixAt(id, tempMatrix);

    const def = BLOCK_DEF[type];
    tempColor.setHex(def ? def.hex : 0xffffff);
    mesh.setColorAt(id, tempColor);
  } else {
    tempMatrix.makeScale(0, 0, 0);
    mesh.setMatrixAt(id, tempMatrix);
    tempColor.setHex(0x000000);
    mesh.setColorAt(id, tempColor);
  }
}

function invalidateInstances() {
  mesh.instanceMatrix.needsUpdate = true;
  if (mesh.instanceColor) {
    mesh.instanceColor.needsUpdate = true;
  }
}

function buildInstances() {
  usedInstances = 0;

  for (let y = 0; y < HEIGHT; y++) {
    for (let x = 0; x < SIZE; x++) {
      for (let z = 0; z < SIZE; z++) {
        const i = idx(x, y, z);
        const t = world[i];
        if (t !== BLOCK.AIR && usedInstances < MAX_BLOCKS) {
          blockIds[i] = usedInstances;
          setInstance(usedInstances, x, y, z, t, true);
          usedInstances++;
        }
      }
    }
  }

  mesh.count = usedInstances;
  invalidateInstances();
}

// ----------------------------------------------------------------
// 衝突判定
// ----------------------------------------------------------------
function collides(px, py, pz) {
  const eps = 0.001;

  const minX = Math.floor(px - HALF_WIDTH + eps);
  const maxX = Math.floor(px + HALF_WIDTH - eps);
  const minY = Math.floor(py - HALF_HEIGHT + eps);
  const maxY = Math.floor(py + HALF_HEIGHT - eps);
  const minZ = Math.floor(pz - HALF_WIDTH + eps);
  const maxZ = Math.floor(pz + HALF_WIDTH - eps);

  for (let x = minX; x <= maxX; x++) {
    for (let y = minY; y <= maxY; y++) {
      for (let z = minZ; z <= maxZ; z++) {
        if (getBlock(x, y, z) !== BLOCK.AIR) {
          return true;
        }
      }
    }
  }

  return false;
}

const player = new THREE.Vector3();
const velocity = new THREE.Vector3();

function intersectsPlayer(bx, by, bz) {
  const eps = 0.001;
  return (
    player.x + HALF_WIDTH > bx + eps &&
    player.x - HALF_WIDTH < bx + 1 - eps &&
    player.y + HALF_HEIGHT > by + eps &&
    player.y - HALF_HEIGHT < by + 1 - eps &&
    player.z + HALF_WIDTH > bz + eps &&
    player.z - HALF_WIDTH < bz + 1 - eps
  );
}

// ----------------------------------------------------------------
// レイキャスト
// ----------------------------------------------------------------
function raycast(
  ox, oy, oz,
  dx, dy, dz,
  maxDist
) {
  if (dx === 0 && dy === 0 && dz === 0) return null;

  let x = Math.floor(ox);
  let y = Math.floor(oy);
  let z = Math.floor(oz);

  const stepX = dx > 0 ? 1 : -1;
  const stepY = dy > 0 ? 1 : -1;
  const stepZ = dz > 0 ? 1 : -1;

  let tMaxX = dx !== 0
    ? (stepX > 0 ? (x + 1 - ox) / dx : (ox - x) / dx)
    : Infinity;

  let tMaxY = dy !== 0
    ? (stepY > 0 ? (y + 1 - oy) / dy : (oy - y) / dy)
    : Infinity;

  let tMaxZ = dz !== 0
    ? (stepZ > 0 ? (z + 1 - oz) / dz : (oz - z) / dz)
    : Infinity;

  const tDeltaX = dx !== 0 ? 1 / Math.abs(dx) : Infinity;
  const tDeltaY = dy !== 0 ? 1 / Math.abs(dy) : Infinity;
  const tDeltaZ = dz !== 0 ? 1 / Math.abs(dz) : Infinity;

  let nx = 0;
  let ny = 0;
  let nz = 0;

  let t = 0;

  if (getBlock(x, y, z) !== BLOCK.AIR) {
    return {
      x,
      y,
      z,
      nx: dx > 0 ? -1 : dx < 0 ? 1 : 0,
      ny: dy > 0 ? -1 : dy < 0 ? 1 : 0,
      nz: dz > 0 ? -1 : dz < 0 ? 1 : 0
    };
  }

  for (let i = 0; i < 64; i++) {
    if (tMaxX < tMaxY && tMaxX < tMaxZ) {
      x += stepX;
      t = tMaxX;
      tMaxX += tDeltaX;
      nx = -stepX;
      ny = 0;
      nz = 0;
    } else if (tMaxY < tMaxZ) {
      y += stepY;
      t = tMaxY;
      tMaxY += tDeltaY;
      nx = 0;
      ny = -stepY;
      nz = 0;
    } else {
      z += stepZ;
      t = tMaxZ;
      tMaxZ += tDeltaZ;
      nx = 0;
      ny = 0;
      nz = -stepZ;
    }

    if (t > maxDist) break;
    if (getBlock(x, y, z) !== BLOCK.AIR) {
      return { x, y, z, nx, ny, nz };
    }
  }

  return null;
}

// ----------------------------------------------------------------
// 選択ターゲット表示
// ----------------------------------------------------------------
const targetBox = new THREE.LineSegments(
  new THREE.EdgesGeometry(new THREE.BoxGeometry(1, 1, 1)),
  new THREE.LineBasicMaterial({ color: 0xffff00, transparent: true, opacity: 0.9 })
);
targetBox.visible = false;
scene.add(targetBox);

let target = null;
const rayDir = new THREE.Vector3();

function updateTarget() {
  camera.getWorldDirection(rayDir);

  target = raycast(
    camera.position.x,
    camera.position.y,
    camera.position.z,
    rayDir.x,
    rayDir.y,
    rayDir.z,
    REACH
  );

  if (target) {
    targetBox.visible = true;
    targetBox.position.set(
      target.x + 0.5,
      target.y + 0.5,
      target.z + 0.5
    );
  } else {
    targetBox.visible = false;
  }
}

// ----------------------------------------------------------------
// 設置 / 破壊
// ----------------------------------------------------------------
let selectedIndex = 0;

function addBlock(x, y, z, type) {
  if (!inBounds(x, y, z)) return;
  if (getBlock(x, y, z) !== BLOCK.AIR) return;
  if (intersectsPlayer(x, y, z)) return;
  if (usedInstances >= MAX_BLOCKS) return;

  const i = idx(x, y, z);
  const id = usedInstances++;

  blockIds[i] = id;
  world[i] = type;

  setInstance(id, x, y, z, type, true);
  mesh.count = usedInstances;
  invalidateInstances();
}

function removeBlock(x, y, z) {
  if (!inBounds(x, y, z)) return;
  const i = idx(x, y, z);
  if (world[i] === BLOCK.AIR) return;

  const id = blockIds[i];
  if (id >= 0) {
    setInstance(id, x, y, z, 0, false);
    blockIds[i] = -1;
  }

  world[i] = BLOCK.AIR;
  invalidateInstances();
}

function tryPlace() {
  if (!target) return;

  const tx = target.x + target.nx;
  const ty = target.y + target.ny;
  const tz = target.z + target.nz;

  if (target.nx === 0 && target.ny === 0 && target.nz === 0) return;

  addBlock(tx, ty, tz, BLOCK_ORDER[selectedIndex]);
}

function tryRemove() {
  if (!target) return;
  removeBlock(target.x, target.y, target.z);
}

// ----------------------------------------------------------------
// プレイヤー初期化
// ----------------------------------------------------------------
let yaw = 0;
let pitch = 0;
let onGround = false;

function getHighestY(x, z) {
  for (let y = HEIGHT - 1; y >= 0; y--) {
    if (getBlock(x, y, z) !== BLOCK.AIR) return y;
  }
  return -1;
}

function clamp(v, a, b) {
  return Math.max(a, Math.min(b, v));
}

function resetPlayer() {
  const sx = SIZE >> 1;
  const sz = SIZE >> 1;

  let y = getHighestY(sx, sz) + 1;
  player.set(sx + 0.5, y + HALF_HEIGHT, sz + 0.5);

  let guard = 0;
  while (collides(player.x, player.y, player.z) && guard < 80) {
    player.y += 0.5;
    guard++;
  }

  velocity.set(0, 0, 0);
  yaw = 0;
  pitch = 0;
  onGround = true;
}

function moveAxis(axis, amount) {
  if (amount === 0) return;

  const before = player[axis];
  player[axis] += amount;

  if (collides(player.x, player.y, player.z)) {
    player[axis] = before;

    if (axis === 1) {
      velocity.y = 0;
      if (amount < 0) onGround = true;
    }
  }
}

// ----------------------------------------------------------------
// 入力
// ----------------------------------------------------------------
const keys = Object.create(null);

const overlay = document.getElementById("overlay");
const playButton = document.getElementById("play");

function startGame() {
  overlay.style.display = "none";
  canvas.requestPointerLock();
}

playButton.addEventListener("click", startGame);

canvas.addEventListener("click", () => {
  if (document.pointerLockElement !== canvas) {
    startGame();
  }
});

document.addEventListener("pointerlockchange", () => {
  if (!document.pointerLockElement) {
    overlay.style.display = "flex";
  }
});

document.addEventListener("keydown", e => {
  keys[e.code] = true;

  if (e.code === "Space") {
    e.preventDefault();
  }

  if (/^Digit\d$/.test(e.code)) {
    const n = Number(e.code.slice(5)) - 1;
    if (n >= 0 && n < BLOCK_ORDER.length) {
      selectedIndex = n;
      updateHotbar();
    }
  }
});

document.addEventListener("keyup", e => {
  keys[e.code] = false;
});

document.addEventListener("mousemove", e => {
  if (document.pointerLockElement !== canvas) return;

  yaw -= e.movementX * 0.0022;
  pitch -= e.movementY * 0.0022;
  pitch = clamp(pitch, -1.45, 1.45);
});

canvas.addEventListener("contextmenu", e => e.preventDefault());

canvas.addEventListener("mousedown", e => {
  if (document.pointerLockElement !== canvas) return;
  e.preventDefault();

  if (e.button === 0) {
    tryRemove();
  } else if (e.button === 2) {
    tryPlace();
  }
});

window.addEventListener("wheel", e => {
  if (document.pointerLockElement !== canvas) return;
  e.preventDefault();

  const dir = e.deltaY > 0 ? 1 : -1;
  selectedIndex = (selectedIndex + dir + BLOCK_ORDER.length) % BLOCK_ORDER.length;
  updateHotbar();
}, { passive: false });

// ----------------------------------------------------------------
// UI
// ----------------------------------------------------------------
const hotbarEl = document.getElementById("hotbar");
const statusEl = document.getElementById("status");

function buildHotbar() {
  hotbarEl.innerHTML = "";

  BLOCK_ORDER.forEach((type, i) => {
    const def = BLOCK_DEF[type];
    const slot = document.createElement("div");
    slot.className = "slot";
    slot.innerHTML = `
      <div class="sw" style="background:${def.css}"></div>
      <div>${type}</div>
    `;
    hotbarEl.appendChild(slot);
  });
}

function updateHotbar() {
  const slots = hotbarEl.children;
  for (let i = 0; i < slots.length; i++) {
    slots[i].classList.toggle("sel", i === selectedIndex);
  }
}

// ----------------------------------------------------------------
// FPS 表示
// ----------------------------------------------------------------
let frames = 0;
let lastFpsTime = performance.now();
let fps = 0;

function updateStatus() {
  frames++;
  const now = performance.now();

  if (now - lastFpsTime >= 500) {
    fps = Math.round(frames * 1000 / (now - lastFpsTime));
    frames = 0;
    lastFpsTime = now;

    const type = BLOCK_ORDER[selectedIndex];
    const def = BLOCK_DEF[type];

    statusEl.textContent =
`FPS: ${fps}
XYZ: ${player.x.toFixed(1)}, ${player.y.toFixed(1)}, ${player.z.toFixed(1)}
Block: ${def.name}
Used: ${usedInstances}`;
  }
}

// ----------------------------------------------------------------
// 更新
// ----------------------------------------------------------------
const clock = new THREE.Clock();

function update(dt) {
  if (document.pointerLockElement === canvas) {
    const forward = (keys["KeyW"] ? 1 : 0) - (keys["KeyS"] ? 1 : 0);
    const right = (keys["KeyD"] ? 1 : 0) - (keys["KeyA"] ? 1 : 0);
    const jump = keys["Space"];

    const sinY = Math.sin(yaw);
    const cosY = Math.cos(yaw);

    const desiredX = (-sinY * forward + cosY * right) * SPEED;
    const desiredZ = (-cosY * forward - sinY * right) * SPEED;

    const accel = 18;
    velocity.x += (desiredX - velocity.x) * Math.min(1, accel * dt);
    velocity.z += (desiredZ - velocity.z) * Math.min(1, accel * dt);

    if (jump && onGround) {
      velocity.y = JUMP;
      onGround = false;
    }

    velocity.y += GRAVITY * dt;
    velocity.y = Math.max(velocity.y, -40);

    onGround = false;

    moveAxis(0, velocity.x * dt);
    moveAxis(2, velocity.z * dt);
    moveAxis(1, velocity.y * dt);

    player.x = clamp(player.x, HALF_WIDTH, SIZE - HALF_WIDTH);
    player.z = clamp(player.z, HALF_WIDTH, SIZE - HALF_WIDTH);

    if (player.y < -15) {
      resetPlayer();
    }
  }

  camera.position.copy(player);
  camera.position.y += EYE_Y;
  camera.rotation.set(pitch, yaw, 0);
}

// ----------------------------------------------------------------
// リサイズ
// ----------------------------------------------------------------
window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// ----------------------------------------------------------------
// 初期化 & ループ
// ----------------------------------------------------------------
generateWorld();
buildInstances();
resetPlayer();
buildHotbar();
updateHotbar();

function animate() {
  requestAnimationFrame(animate);

  const dt = Math.min(clock.getDelta(), 0.05);

  update(dt);
  updateTarget();

  renderer.render(scene, camera);
  updateStatus();
}

animate();
</script>
</body>
</html>
```