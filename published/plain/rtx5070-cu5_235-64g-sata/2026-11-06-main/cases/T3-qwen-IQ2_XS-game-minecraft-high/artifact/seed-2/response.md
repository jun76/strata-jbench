以下、そのまま開くだけで遊べる「マイクラ風3D箱庭ゲーム」です。

- **WASD**：移動
- **Space**：ジャンプ
- **左クリック**：ブロック破壊
- **右クリック**：ブロック設置
- **1〜5**：ブロック種切り替え
- **Shift**：走る
- **Esc**：マウス解除
- **画面クリック**：視点操作開始

単一HTMLファイルとして保存してブラウザで開けば動作する想定です。Three.jsをCDNから読み込みます。

```html
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Minecraft-like 3D Garden</title>
<style>
  html, body {
    margin: 0;
    height: 100%;
    overflow: hidden;
    background: #111;
    font-family: system-ui, sans-serif;
    color: #fff;
  }

  #app {
    position: relative;
    width: 100%;
    height: 100%;
  }

  canvas {
    display: block;
    width: 100%;
    height: 100%;
    cursor: crosshair;
  }

  #ui {
    position: absolute;
    top: 12px;
    left: 12px;
    padding: 12px 14px;
    border-radius: 12px;
    background: rgba(0, 0, 0, 0.55);
    border: 1px solid rgba(255, 255, 255, 0.15);
    font-size: 13px;
    line-height: 1.5;
    max-width: 360px;
  }

  #crosshair {
    position: absolute;
    left: 50%;
    top: 50%;
    width: 18px;
    height: 18px;
    transform: translate(-50%, -50%);
    pointer-events: none;
  }

  #crosshair::before,
  #crosshair::after {
    content: "";
    position: absolute;
    background: #fff;
    opacity: 0.85;
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
    position: absolute;
    bottom: 14px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: 8px;
    pointer-events: none;
  }

  .slot {
    width: 54px;
    height: 54px;
    border-radius: 8px;
    background: rgba(0, 0, 0, 0.55);
    border: 2px solid rgba(255, 255, 255, 0.25);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    text-align: center;
  }

  .slot.active {
    border-color: #fff;
    background: rgba(255, 255, 255, 0.18);
  }

  .swatch {
    width: 22px;
    height: 22px;
    border-radius: 4px;
    margin-bottom: 4px;
    box-shadow: 0 0 0 1px rgba(255,255,255,0.25) inset;
  }

  .slot-label {
    font-size: 11px;
    opacity: 0.9;
  }
</style>
</head>
<body>
<div id="app">
  <div id="ui">
    <strong>Minecraft-like 3D Garden</strong><br>
    WASD: move, Space: jump<br>
    Left click: break, Right click: place<br>
    1-5: select block, Shift: run<br>
    Click screen to lock mouse. Esc to release.
  </div>

  <div id="crosshair"></div>

  <div id="hotbar"></div>
</div>

<script type="module">
import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js";

const app = document.getElementById("app");

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
app.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x70b7ff);
scene.fog = new THREE.Fog(0x70b7ff, 24, 80);

const camera = new THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 0.1, 200);
camera.rotation.order = "YXZ";

const worldSize = 64;
const maxHeight = 44;

// -----------------------------
// Block settings
// -----------------------------
const BLOCK_NAMES = [
  null,
  "Grass",
  "Dirt",
  "Stone",
  "Wood",
  "Leaves"
];

const blockMaterials = [
  null,
  new THREE.MeshLambertMaterial({ color: 0x55a44a }), // grass
  new THREE.MeshLambertMaterial({ color: 0x8a6a47 }), // dirt
  new THREE.MeshLambertMaterial({ color: 0x8f8f8f }), // stone
  new THREE.MeshLambertMaterial({ color: 0x7c532c }), // wood
  new THREE.MeshLambertMaterial({ color: 0x2f7c2d })  // leaves
];

const blockGeometry = new THREE.BoxGeometry(1, 1, 1);

// Instanced meshes: one mesh per block type
const instancedMeshes = new Array(BLOCK_NAMES.length).fill(null);
const typeKeys = new Array(BLOCK_NAMES.length).fill(null).map(() => []);

// key pack helpers. Use offsets so negative values can also fit.
const OFF = 200;
const SX = 1000000;
const SY = 1000;

function pack(x, y, z) {
  return (x + OFF) * SX + (y + OFF) * SY + (z + OFF);
}

function unpack(key) {
  const x = Math.floor(key / SX) - OFF;
  const rem = key % SX;
  const y = Math.floor(rem / SY) - OFF;
  const z = (rem % SY) - OFF;
  return { x, y, z };
}

// Map voxelKey -> { id, index }
const blocks = new Map();

const dummy = new THREE.Object3D();

function ensureMesh(type, needed = 1) {
  const current = instancedMeshes[type];
  const count = typeKeys[type].length;

  if (!current || current.instanceMatrix.count < Math.max(count, needed)) {
    const cap = Math.max(count, 10000);
    current = new THREE.InstancedMesh(blockGeometry, blockMaterials[type], cap);
    current.userData.type = type;
    instancedMeshes[type] = current;
    scene.add(current);
  }

  return current;
}

function setMatrixAt(type, index, key) {
  const mesh = instancedMeshes[type];
  const p = unpack(key);
  dummy.position.set(p.x + 0.5, p.y + 0.5, p.z + 0.5);
  dummy.rotation.set(0, 0, 0);
  dummy.updateMatrix();
  mesh.setMatrixAt(index, dummy.matrix);
}

function rebuildType(type) {
  const mesh = ensureMesh(type, typeKeys[type].length);
  mesh.count = typeKeys[type].length;

  for (let i = 0; i < typeKeys[type].length; i++) {
    setMatrixAt(type, i, typeKeys[type][i]);
  }

  mesh.instanceMatrix.needsUpdate = true;
}

function addBlock(x, y, z, type) {
  if (type <= 0) return false;

  const key = pack(x, y, z);
  if (blocks.has(key)) return false;

  const arr = typeKeys[type];
  const mesh = ensureMesh(type, arr.length + 1);

  const idx = arr.length;
  arr.push(key);
  blocks.set(key, { type, idx });

  setMatrixAt(type, idx, key);
  mesh.count = arr.length;
  mesh.instanceMatrix.needsUpdate = true;

  return true;
}

function removeBlock(key) {
  const entry = blocks.get(key);
  if (!entry) return false;

  const type = entry.type;
  const idx = entry.idx;
  const arr = typeKeys[type];
  const mesh = instancedMeshes[type];

  const lastKey = arr[arr.length - 1];
  const lastEntry = blocks.get(lastKey);

  arr[idx] = lastKey;
  lastEntry.idx = idx;

  arr.pop();
  blocks.delete(key);

  if (arr.length >= idx) {
    setMatrixAt(type, idx, arr[idx]);
  }

  mesh.count = arr.length;
  mesh.instanceMatrix.needsUpdate = true;

  return true;
}

function getBlock(x, y, z) {
  return blocks.has(pack(x, y, z));
}

// -----------------------------
// Terrain generation
// -----------------------------
function heightAt(x, z) {
  const h =
    14 +
    Math.floor(
      4 * Math.sin(x * 0.12) * Math.cos(z * 0.14) +
      3 * Math.sin(x * 0.035 + z * 0.05) +
      2 * Math.cos(x * 0.025 - z * 0.018)
    );

  return Math.max(1, Math.min(maxHeight, h));
}

function seedRandom(x, z) {
  const t = Math.sin(x * 127.1 + z * 311.7) * 43758.5453;
  return t - Math.floor(t);
}

function generateWorld() {
  for (let x = 0; x < worldSize; x++) {
    for (let z = 0; z < worldSize; z++) {
      const h = heightAt(x, z);

      for (let y = 0; y <= h; y++) {
        let type = 3; // stone

        if (y === h) {
          type = 1; // grass
        } else if (y >= h - 1) {
          type = 2; // dirt
        }

        addBlock(x, y, z, type);
      }
    }
  }

  // Simple trees
  for (let x = 4; x < worldSize - 4; x++) {
    for (let z = 4; z < worldSize - 4; z++) {
      const r = seedRandom(x, z);
      if (r < 0.015) {
        const h = heightAt(x, z);
        if (h < 2) continue;

        const trunkHeight = 4 + Math.floor(seedRandom(x + 7, z + 13) * 3);

        for (let y = h + 1; y <= h + trunkHeight; y++) {
          addBlock(x, y, z, 4);
        }

        const top = h + trunkHeight;

        for (let lx = -2; lx <= 2; lx++) {
          for (let ly = 0; ly <= 1; ly++) {
            for (let lz = -2; lz <= 2; lz++) {
              if (Math.abs(lx) + Math.abs(lz) >= 4) continue;

              const tx = x + lx;
              const ty = top - ly;
              const tz = z + lz;

              addBlock(tx, ty, tz, 5);
            }
          }
        }
      }
    }
  }

  for (let i = 1; i < blockMaterials.length; i++) {
    rebuildType(i);
  }
}

generateWorld();

// -----------------------------
// Player
// -----------------------------
const player = {
  pos: new THREE.Vector3(worldSize / 2, heightAt(worldSize / 2, worldSize / 2) + 1, worldSize / 2),
  vel: new THREE.Vector3(),
  yaw: 0,
  pitch: 0,
  onGround: false
};

const EYE_HEIGHT = 1.62;
const PLAYER_HEIGHT = 1.8;
const RADIUS = 0.35;
const EPS = 1e-5;

function collides(pos) {
  const minX = pos.x - RADIUS + EPS;
  const maxX = pos.x + RADIUS - EPS;
  const minY = pos.y + EPS;
  const maxY = pos.y + PLAYER_HEIGHT - EPS;
  const minZ = pos.z - RADIUS + EPS;
  const maxZ = pos.z + RADIUS - EPS;

  const x0 = Math.floor(minX);
  const x1 = Math.floor(maxX);
  const y0 = Math.floor(minY);
  const y1 = Math.floor(maxY);
  const z0 = Math.floor(minZ);
  const z1 = Math.floor(maxZ);

  for (let x = x0; x <= x1; x++) {
    for (let y = y0; y <= y1; y++) {
      for (let z = z0; z <= z1; z++) {
        if (blocks.has(pack(x, y, z))) {
          return true;
        }
      }
    }
  }

  return false;
}

function snapHorizontal(pos, axis, sign) {
  if (sign > 0) {
    const cell = Math.floor(pos[axis] + RADIUS - EPS);
    pos[axis] = cell - RADIUS - EPS;
  } else {
    const cell = Math.floor(pos[axis] - RADIUS + EPS);
    pos[axis] = cell + 1 + RADIUS + EPS;
  }
}

function snapVertical(pos, sign) {
  if (sign < 0) {
    const cell = Math.floor(pos.y + EPS);
    pos.y = cell + 1 + EPS;
  } else {
    const cell = Math.floor(pos.y + PLAYER_HEIGHT - EPS);
    pos.y = cell - PLAYER_HEIGHT - EPS;
  }
}

function moveAxis(axis, amount) {
  const step = 0.05;
  let remaining = Math.abs(amount);
  const sign = Math.sign(amount);
  if (sign === 0) return false;

  while (remaining > 0) {
    const s = Math.min(step, remaining);
    const test = player.pos.clone();
    test[axis] += sign * s;

    if (collides(test)) {
      if (axis === "y") {
        snapVertical(test, sign);

        if (sign < 0) {
          player.onGround = true;
        }

        player.pos[axis] = test[axis];
      } else {
        snapHorizontal(test, axis, sign);
        player.pos[axis] = test[axis];
      }

      player.vel[axis] = 0;
      return true;
    }

    player.pos[axis] += sign * s;
    remaining -= s;
  }

  return false;
}

function blockIntersectsPlayer(x, y, z) {
  const minX = x;
  const maxX = x + 1;
  const minY = y;
  const maxY = y + 1;
  const minZ = z;
  const maxZ = z + 1;

  const pMinX = player.pos.x - RADIUS;
  const pMaxX = player.pos.x + RADIUS;
  const pMinY = player.pos.y;
  const pMaxY = player.pos.y + PLAYER_HEIGHT;
  const pMinZ = player.pos.z - RADIUS;
  const pMaxZ = player.pos.z + RADIUS;

  return (
    pMaxX > minX &&
    pMinX < maxX &&
    pMaxY > minY &&
    pMinY < maxY &&
    pMaxZ > minZ &&
    pMinZ < maxZ
  );
}

function canPlaceBlock(x, y, z) {
  if (blockIntersectsPlayer(x, y, z)) return false;
  return true;
}

// -----------------------------
// Input
// -----------------------------
const keys = new Set();
let pointerLocked = false;

let selectedBlock = 1;

window.addEventListener("keydown", e => {
  keys.add(e.code);

  if (e.code === "Space") e.preventDefault();

  const num = Number(e.key);
  if (num >= 1 && num <= 5) {
    selectedBlock = num;
    updateHotbar();
  }
});

window.addEventListener("keyup", e => {
  keys.delete(e.code);
});

canvas.addEventListener("click", () => {
  canvas.requestPointerLock();
});

document.addEventListener("pointerlockchange", () => {
  pointerLocked = document.pointerLockElement === canvas;
});

document.addEventListener("mousemove", e => {
  if (!pointerLocked) return;

  const sens = 0.0025;

  player.yaw -= e.movementX * sens;
  player.pitch -= e.movementY * sens;

  player.pitch = Math.max(-Math.PI / 2 + 0.01, Math.min(Math.PI / 2 - 0.01, player.pitch));
});

document.addEventListener("contextmenu", e => e.preventDefault());

canvas.addEventListener("mousedown", e => {
  if (!pointerLocked) {
    canvas.requestPointerLock();
    return;
  }

  if (e.button === 0) {
    breakBlock();
  } else if (e.button === 2) {
    placeBlock();
  }
});

const raycaster = new THREE.Raycaster();
raycaster.far = 8;

const targetList = [];

function getTargetList() {
  targetList.length = 0;

  for (let i = 0; i < instancedMeshes.length; i++) {
    const mesh = instancedMeshes[i];
    if (mesh && mesh.count > 0) {
      targetList.push(mesh);
    }
  }

  return targetList;
}

function getRayInfo() {
  const origin = camera.position.clone();
  const dir = camera.getWorldDirection(new THREE.Vector3());

  raycaster.set(origin, dir);

  const hits = raycaster.intersectObjects(getTargetList(), false);
  if (!hits.length) return null;

  const hit = hits[0];

  if (typeof hit.instanceId !== "number") return null;

  const type = hit.object.userData.type;
  const key = typeKeys[type][hit.instanceId];
  const blockPos = unpack(key);

  return {
    hit,
    type,
    key,
    blockPos,
    faceNormal: hit.face ? hit.face.normal.clone() : null
  };
}

function getNormal(info) {
  const blockCenter = new THREE.Vector3(
    info.blockPos.x + 0.5,
    info.blockPos.y + 0.5,
    info.blockPos.z + 0.5
  );

  if (info.faceNormal) {
    const n = info.faceNormal.clone();
    n.transformDirection(info.hit.object.matrixWorld);
    return n;
  }

  const v = info.hit.point.clone().sub(blockCenter);
  const absX = Math.abs(v.x);
  const absY = Math.abs(v.y);
  const absZ = Math.abs(v.z);

  if (absX > absY && absX > absZ) {
    return new THREE.Vector3(Math.sign(v.x), 0, 0);
  }

  if (absY > absX && absY > absZ) {
    return new THREE.Vector3(0, Math.sign(v.y), 0);
  }

  return new THREE.Vector3(0, 0, Math.sign(v.z));
}

function breakBlock() {
  const info = getRayInfo();
  if (!info) return;

  removeBlock(info.key);
}

function placeBlock() {
  const info = getRayInfo();
  if (!info) return;

  const n = getNormal(info);

  const tx = info.blockPos.x + Math.round(n.x);
  const ty = info.blockPos.y + Math.round(n.y);
  const tz = info.blockPos.z + Math.round(n.z);

  if (!canPlaceBlock(tx, ty, tz)) return;
  if (blocks.has(pack(tx, ty, tz))) return;

  addBlock(tx, ty, tz, selectedBlock);
}

// -----------------------------
// Hotbar UI
// -----------------------------
const hotbar = document.getElementById("hotbar");

function buildHotbar() {
  hotbar.innerHTML = "";

  for (let i = 1; i <= 5; i++) {
    const slot = document.createElement("div");
    slot.className = "slot";

    const swatch = document.createElement("div");
    swatch.className = "swatch";

    const color = blockMaterials[i].color.getHexString();
    swatch.style.background = "#" + color;

    const label = document.createElement("div");
    label.className = "slot-label";
    label.textContent = i + " " + BLOCK_NAMES[i];

    slot.appendChild(swatch);
    slot.appendChild(label);

    hotbar.appendChild(slot);
  }

  updateHotbar();
}

function updateHotbar() {
  const slots = hotbar.querySelectorAll(".slot");
  slots.forEach((slot, i) => {
    slot.classList.toggle("active", (i + 1) === selectedBlock);
  });
}

buildHotbar();

// -----------------------------
// Lighting
// -----------------------------
const ambient = new THREE.AmbientLight(0xffffff, 0.35);
scene.add(ambient);

const sun = new THREE.DirectionalLight(0xffffff, 1.0);
sun.position.set(40, 70, 25);
scene.add(sun);

const hemi = new THREE.HemisphereLight(0x77c1ff, 0x445533, 0.5);
scene.add(hemi);

// -----------------------------
// Main loop
// -----------------------------
const clock = new THREE.Clock();

function updatePhysics(dt) {
  dt = Math.min(dt, 0.05);

  const speed = keys.has("ShiftLeft") || keys.has("ShiftRight") ? 8.5 : 4.8;

  const forward = camera.getWorldDirection(new THREE.Vector3());
  forward.y = 0;
  forward.normalize();

  const right = new THREE.Vector3(-forward.z, 0, forward.x);

  let move = new THREE.Vector3();

  if (pointerLocked) {
    if (keys.has("KeyW")) move.add(forward);
    if (keys.has("KeyS")) move.sub(forward);
    if (keys.has("KeyD")) move.add(right);
    if (keys.has("KeyA")) move.sub(right);
  }

  if (move.lengthSq() > 0) {
    move.normalize();
    move.multiplyScalar(speed);
  }

  player.vel.x = move.x;
  player.vel.z = move.z;

  if (pointerLocked && keys.has("Space") && player.onGround) {
    player.vel.y = 7.6;
    player.onGround = false;
  }

  player.vel.y -= 18 * dt;

  // Move horizontal
  const movedX = moveAxis("x", player.vel.x * dt);
  const movedZ = moveAxis("z", player.vel.z * dt);

  // Move vertical
  const movedY = moveAxis("y", player.vel.y * dt);

  // Ground check for small vertical movements
  if (!movedY && player.vel.y <= 0) {
    const groundCheck = player.pos.clone();
    groundCheck.y -= 0.01;

    if (collides(groundCheck)) {
      player.onGround = true;
      player.vel.y = 0;
    }
  }

  if (movedY) {
    player.onGround = false;
  }

  camera.position.set(
    player.pos.x,
    player.pos.y + EYE_HEIGHT,
    player.pos.z
  );

  camera.rotation.set(player.pitch, player.yaw, 0, "YXZ");
}

function render() {
  const dt = clock.getDelta();
  updatePhysics(dt);
  renderer.render(scene, camera);
  requestAnimationFrame(render);
}

render();

window.addEventListener("resize", () => {
  renderer.setSize(window.innerWidth, window.innerHeight);
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
});
</script>
</body>
</html>
```

もし「完全にローカルで動く版」が必要なら、Three.jsのCDN読み込みを止め、自前で簡易3Dエンジンを書いた軽量版も作れます。