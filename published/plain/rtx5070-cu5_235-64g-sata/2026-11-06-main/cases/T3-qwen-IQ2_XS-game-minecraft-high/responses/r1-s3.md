保存してブラウザで開けばそのまま遊べる「単一HTMLファイル版」のマイクラ風3D箱庭ゲームです。  
voxel(ブロック)ワールドで、**左クリックでブロック破壊／右クリックでブロック設置**ができます。

## Controls
- WASD: 移動
- Space: ジャンプ
- Shift: 走る
- マウス: 視点操作（画面クリックでマウスロック）
- 左クリック: ブロック破壊
- 右クリック: ブロック設置
- `1〜9`: インベントリ選択
- `Esc`: pointer lock解除（マウス選択に戻ります）

---

```html
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>Minecraft風 3D 箱庭</title>
<style>
  body {
    margin: 0;
    overflow: hidden;
    background: #0e1115;
    font-family: monospace;
  }
  canvas { display: block; }

  #hud {
    position: fixed;
    inset: 0;
    pointer-events: none;
  }
  #reticle {
    position: absolute;
    top: 50%;
    left: 50%;
    width: 6px;
    height: 6px;
    background: #111;
    border: 1px solid #fff;
    transform: translate(-50%, -50%);
  }
  #info {
    position: absolute;
    top: 12px;
    left: 12px;
    background: rgba(0, 0, 0, 0.60);
    color: #e8e8e8;
    padding: 10px 12px;
    border-radius: 8px;
    font-size: 13px;
    line-height: 1.45;
    max-width: 360px;
  }
  #inventory {
    position: absolute;
    bottom: 12px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: 6px;
    pointer-events: auto;
  }
  .slot {
    width: 38px;
    height: 38px;
    border: 2px solid #444;
    border-radius: 6px;
    background: #222;
    cursor: pointer;
    box-shadow: 0 2px 4px rgba(0,0,0,.35);
  }
  .slot.active {
    border-color: #fff;
    outline: 2px solid #fff;
  }
  #tip {
    position: absolute;
    bottom: 64px;
    left: 50%;
    transform: translateX(-50%);
    color: #fff;
    background: rgba(0,0,0,.55);
    padding: 6px 10px;
    border-radius: 8px;
    font-size: 13px;
  }
</style>
</head>
<body>
<div id="hud">
  <div id="reticle"></div>
  <div id="info">
    <strong>Minecraft風 3D 箱庭</strong><br>
    画面クリックでマウスロック。<br>
    WASD移動 / Spaceジャンプ / Shift走る。<br>
    左クリックで破壊、右クリックで設置。<br>
    1〜9でインベントリ切替。
  </div>
  <div id="tip"></div>
  <div id="inventory"></div>
</div>

<script type="module">
import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js";

// -------------------------
// 定数
// -------------------------
const AIR = 0;
const GRASS = 1;
const DIRT = 2;
const STONE = 3;
const SAND = 4;
const WOOD = 5;
const LEAVES = 6;
const PLANK = 7;
const GLASS = 8;
const COBBLE = 9;
const BRICK = 10;

const W = 40;
const H = 24;
const D = 40;

const PLAYER_HEIGHT = 1.8;
const PLAYER_RADIUS = 0.34;
const EYE_HEIGHT = 1.65;
const GRAVITY = 22;
const JUMP_SPEED = 6.3;
const WALK_SPEED = 4.3;
const RUN_SPEED = 6.5;

const COLORS = [
  null,
  new THREE.Color(0x65a547), // grass
  new THREE.Color(0x8b6641), // dirt
  new THREE.Color(0x707274), // stone
  new THREE.Color(0xd9bd76), // sand
  new THREE.Color(0x714b2b), // wood
  new THREE.Color(0x3b7d3f), // leaves
  new THREE.Color(0x8d7246), // plank
  new THREE.Color(0x79c7e6), // glass
  new THREE.Color(0x56585c), // cobble
  new THREE.Color(0xa34949), // brick
];

const BLOCK_NAMES = [
  "Air",
  "Grass",
  "Dirt",
  "Stone",
  "Sand",
  "Wood",
  "Leaves",
  "Plank",
  "Glass",
  "Cobble",
  "Brick"
];

// -------------------------
// Three.js setup
// -------------------------
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x86c5e6);
scene.fog = new THREE.Fog(0x86c5e6, 35, 90);

const camera = new THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 0.1, 200);
camera.rotation.order = "YXZ";

const hemi = new THREE.HemisphereLight(0xa6e2ff, 0x463a30, 0.9);
scene.add(hemi);

const sun = new THREE.DirectionalLight(0xffffff, 0.75);
sun.position.set(35, 70, 20);
scene.add(sun);

const geom = new THREE.BufferGeometry();
const mesh = new THREE.Mesh(geom, new THREE.MeshLambertMaterial({
  vertexColors: true,
  side: THREE.DoubleSide
}));
scene.add(mesh);

const outline = new THREE.LineSegments(
  new THREE.EdgesGeometry(new THREE.BoxGeometry(1, 1, 1)),
  new THREE.LineBasicMaterial({ color: 0x000000 })
);
scene.add(outline);

// -------------------------
// World data
// -------------------------
const world = new Uint8Array(W * H * D);

function idx(x, y, z) {
  return ((x * D + z) * H + y);
}

function inWorld(x, y, z) {
  return x >= 0 && y >= 0 && z >= 0 && x < W && y < H && z < D;
}

function getBlock(x, y, z) {
  if (!inWorld(x, y, z)) return AIR;
  return world[idx(x, y, z)];
}

function setBlock(x, y, z, t) {
  if (!inWorld(x, y, z)) return;
  world[idx(x, y, z)] = t;
  dirty = true;
}

function isSolid(x, y, z) {
  return getBlock(x, y, z) !== AIR;
}

// -------------------------
// Simple noise
// -------------------------
function hash(x, z, seed = 0) {
  let n = (x * 73856093) ^ (z * 19349163) ^ (seed * 83492791);
  n = Math.imul(n, 0x9e3779b9);
  n ^= n >>> 13;
  n = Math.imul(n, 0x85ebca6b);
  n ^= n >>> 16;
  return n & 255;
}

function valueNoise(x, z) {
  const xi = Math.floor(x);
  const zi = Math.floor(z);
  const fx = x - xi;
  const fz = z - zi;

  const a = hash(xi, zi);
  const b = hash(xi + 1, zi);
  const c = hash(xi, zi + 1);
  const d = hash(xi + 1, zi + 1);

  const u = fx * fx * (3 - 2 * fx);
  const v = fz * fz * (3 - 2 * fz);

  const top = a * (1 - u) + b * u;
  const bottom = c * (1 - u) + d * u;
  return top * (1 - v) + bottom * v;
}

// -------------------------
// World generation
// -------------------------
function heightAt(x, z) {
  const n = valueNoise(x * 0.12, z * 0.12);
  let h = 8 + n * 5 + Math.sin(x * 0.08) * 2 + Math.cos(z * 0.09) * 2;
  h = Math.max(2, Math.min(H - 3, Math.round(h)));
  return h;
}

function addTree(x, z, baseY) {
  const trunk = 4 + (hash(x, z, 77) % 2);
  const top = baseY + trunk;

  for (let y = baseY; y < top; y++) {
    setBlock(x, y, z, WOOD);
  }

  for (let y = top - 1; y <= top + 1; y++) {
    for (let x0 = x - 2; x0 <= x + 2; x0++) {
      for (let z0 = z - 2; z0 <= z + 2; z0++) {
        if (x0 === x && z0 === z && y === top - 1) continue;

        const dx = x0 - x;
        const dz = z0 - z;
        const dist = Math.max(Math.abs(dx), Math.abs(dz));
        if (dist <= 1 || (dist === 2 && Math.abs(dx) <= 1 && Math.abs(dz) <= 1)) {
          if (getBlock(x0, y, z0) === AIR) {
            setBlock(x0, y, z0, LEAVES);
          }
        }
      }
    }
  }
}

function generateWorld() {
  for (let x = 0; x < W; x++) {
    for (let z = 0; z < D; z++) {
      const h = heightAt(x, z);

      for (let y = 0; y <= h; y++) {
        let b = STONE;

        if (y === h) {
          b = h < 5 ? SAND : GRASS;
        } else if (y >= h - 2) {
          b = h < 5 ? SAND : DIRT;
        }

        setBlock(x, y, z, b);
      }

      if (h >= 7 && hash(x, z, 13) < 40) {
        addTree(x, z, h + 1);
      }
    }
  }
}

// -------------------------
// Mesh rebuild
// -------------------------
let dirty = true;

const FACES = [
  { n: [1, 0, 0], v: [[1, 0, 0], [1, 1, 0], [1, 1, 1], [1, 0, 1]] },
  { n: [0, 1, 0], v: [[0, 1, 1], [1, 1, 1], [1, 1, 0], [0, 1, 0]] },
  { n: [0, 0, 1], v: [[1, 0, 1], [0, 0, 1], [0, 1, 1], [1, 1, 1]] },
  { n: [-1, 0, 0], v: [[0, 0, 1], [0, 1, 1], [0, 1, 0], [0, 0, 0]] },
  { n: [0, -1, 0], v: [[0, 0, 0], [1, 0, 0], [1, 0, 1], [0, 0, 1]] },
  { n: [0, 0, -1], v: [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]] }
];

function rebuildMesh() {
  const positions = [];
  const colors = [];
  const normals = [];
  const indices = [];

  for (let x = 0; x < W; x++) {
    for (let z = 0; z < D; z++) {
      for (let y = 0; y < H; y++) {
        const t = getBlock(x, y, z);
        if (t === AIR) continue;

        const c = COLORS[t];
        if (!c) continue;

        const neighbors = [
          [getBlock(x + 1, y, z), 0],
          [getBlock(x, y + 1, z), 1],
          [getBlock(x, y, z + 1), 2],
          [getBlock(x - 1, y, z), 3],
          [getBlock(x, y - 1, z), 4],
          [getBlock(x, y, z - 1), 5]
        ];

        for (const [n, faceIndex] of neighbors) {
          if (n !== AIR) continue;

          const face = FACES[faceIndex];
          const base = positions.length / 3;

          for (const v of face.v) {
            positions.push(x + v[0], y + v[1], z + v[2]);
            colors.push(c.r, c.g, c.b);
            normals.push(face.n[0], face.n[1], face.n[2]);
          }

          indices.push(
            base, base + 1, base + 2,
            base, base + 2, base + 3
          );
        }
      }
    }
  }

  geom.setIndex(indices);
  geom.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
  geom.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));
  geom.setAttribute("normal", new THREE.Float32BufferAttribute(normals, 3));
  geom.computeBoundingSphere();
  geom.computeBoundingBox();

  dirty = false;
}

// -------------------------
// Player
// -------------------------
const player = {
  x: W / 2,
  y: heightAt(W / 2, D / 2),
  z: D / 2,
  vy: 0,
  yaw: 0,
  pitch: 0,
  onGround: true
};

player.y = heightAt(player.x, player.z);

function isBoxColliding(px, py, pz) {
  const minX = Math.floor(px - PLAYER_RADIUS);
  const maxX = Math.floor(px + PLAYER_RADIUS);
  const minY = Math.floor(py);
  const maxY = Math.floor(py + PLAYER_HEIGHT);
  const minZ = Math.floor(pz - PLAYER_RADIUS);
  const maxZ = Math.floor(pz + PLAYER_RADIUS);

  for (let x = minX; x <= maxX; x++) {
    for (let z = minZ; z <= maxZ; z++) {
      for (let y = minY; y <= maxY; y++) {
        if (isSolid(x, y, z)) return true;
      }
    }
  }
  return false;
}

function isGrounded(px, py, pz) {
  const minX = Math.floor(px - PLAYER_RADIUS);
  const maxX = Math.floor(px + PLAYER_RADIUS);
  const minZ = Math.floor(pz - PLAYER_RADIUS);
  const maxZ = Math.floor(pz + PLAYER_RADIUS);

  const y = Math.floor(py) - 1;

  for (let x = minX; x <= maxX; x++) {
    for (let z = minZ; z <= maxZ; z++) {
      if (isSolid(x, y, z)) return true;
    }
  }
  return false;
}

function overlapsPlayer(cx, cy, cz) {
  const minX = player.x - PLAYER_RADIUS;
  const maxX = player.x + PLAYER_RADIUS;
  const minY = player.y;
  const maxY = player.y + PLAYER_HEIGHT;
  const minZ = player.z - PLAYER_RADIUS;
  const maxZ = player.z + PLAYER_RADIUS;

  return (
    cx + 1 > minX &&
    cx < maxX &&
    cy + 1 > minY &&
    cy < maxY &&
    cz + 1 > minZ &&
    cz < maxZ
  );
}

function moveHorizontal(dx, dz, dt) {
  const vx = dx * dt;
  const vz = dz * dt;

  const nx = player.x + vx;
  if (!isBoxColliding(nx, player.y, player.z)) {
    player.x = nx;
  }

  const nz = player.z + vz;
  if (!isBoxColliding(player.x, player.y, nz)) {
    player.z = nz;
  }
}

function moveVertical(dt) {
  if (!player.onGround) {
    player.vy -= GRAVITY * dt;
  }

  const ny = player.y + player.vy * dt;

  if (player.vy < 0) {
    if (isBoxColliding(player.x, ny, player.z)) {
      const startY = Math.floor(ny);
      const endY = Math.floor(ny + PLAYER_HEIGHT);
      const minX = Math.floor(player.x - PLAYER_RADIUS);
      const maxX = Math.floor(player.x + PLAYER_RADIUS);
      const minZ = Math.floor(player.z - PLAYER_RADIUS);
      const maxZ = Math.floor(player.z + PLAYER_RADIUS);

      let landed = false;

      for (let y = startY; y <= endY && !landed; y++) {
        for (let x = minX; x <= maxX; x++) {
          for (let z = minZ; z <= maxZ; z++) {
            if (isSolid(x, y, z)) {
              player.y = y + 1;
              player.vy = 0;
              player.onGround = true;
              landed = true;
              break;
            }
          }
          if (landed) break;
        }
        if (landed) break;
      }

      if (!landed) player.y = ny;
    } else {
      player.y = ny;
    }
  } else if (player.vy > 0) {
    if (isBoxColliding(player.x, ny, player.z)) {
      const startY = Math.floor(ny);
      const endY = Math.floor(ny + PLAYER_HEIGHT);
      const minX = Math.floor(player.x - PLAYER_RADIUS);
      const maxX = Math.floor(player.x + PLAYER_RADIUS);
      const minZ = Math.floor(player.z - PLAYER_RADIUS);
      const maxZ = Math.floor(player.z + PLAYER_RADIUS);

      let hit = false;

      for (let y = endY; y >= startY && !hit; y--) {
        for (let x = minX; x <= maxX; x++) {
          for (let z = minZ; z <= maxZ; z++) {
            if (isSolid(x, y, z)) {
              player.y = y - PLAYER_HEIGHT;
              player.vy = 0;
              player.onGround = false;
              hit = true;
              break;
            }
          }
          if (hit) break;
        }
        if (hit) break;
      }

      if (!hit) player.y = ny;
    } else {
      player.y = ny;
    }
  } else {
    player.y = ny;
  }

  if (player.vy < 0 && isGrounded(player.x, player.y, player.z)) {
    player.vy = 0;
    player.onGround = true;
    player.y = Math.floor(player.y);
  }

  if (player.vy >= 0) {
    player.onGround = isGrounded(player.x, player.y, player.z);
  }

  if (player.y < 0) {
    player.y = 0;
    player.vy = 0;
    player.onGround = true;
  }

  if (player.y > H) {
    player.y = H;
    player.vy = 0;
    player.onGround = false;
  }
}

// -------------------------
// Input
// -------------------------
const keys = {};
let selectedBlock = GRASS;

window.addEventListener("keydown", (e) => {
  keys[e.code] = true;

  const digit = Number(e.key);
  if (digit >= 1 && digit <= 9) {
    selectedBlock = digit;
    updateInventory();
  }

  if (e.code === "Space") {
    e.preventDefault();
  }
});

window.addEventListener("keyup", (e) => {
  keys[e.code] = false;
});

window.addEventListener("mousemove", (e) => {
  if (document.pointerLockElement !== renderer.domElement) return;

  player.yaw += e.movementX * 0.0025;
  player.pitch -= e.movementY * 0.0025;

  player.pitch = Math.max(-1.5, Math.min(1.5, player.pitch));
});

renderer.domElement.addEventListener("click", () => {
  renderer.domElement.requestPointerLock();
});

window.addEventListener("contextmenu", (e) => {
  e.preventDefault();
});

document.addEventListener("mousedown", (e) => {
  if (document.pointerLockElement !== renderer.domElement) return;

  const target = raycastCamera(6);

  if (!target) return;

  if (e.button === 0) {
    setBlock(target.x, target.y, target.z, AIR);
  } else if (e.button === 2) {
    const px = target.x + target.nx;
    const py = target.y + target.ny;
    const pz = target.z + target.nz;

    if (inWorld(px, py, pz) && getBlock(px, py, pz) === AIR && !overlapsPlayer(px, py, pz)) {
      setBlock(px, py, pz, selectedBlock);
    }
  }
});

// -------------------------
// Raycasting for block selection
// -------------------------
const dirVec = new THREE.Vector3();

function raycastCamera(maxDist) {
  camera.getWorldDirection(dirVec);

  const ox = camera.position.x;
  const oy = camera.position.y;
  const oz = camera.position.z;

  const dx = dirVec.x;
  const dy = dirVec.y;
  const dz = dirVec.z;

  let cx = Math.floor(ox);
  let cy = Math.floor(oy);
  let cz = Math.floor(oz);

  const stepX = dx > 0 ? 1 : -1;
  const stepY = dy > 0 ? 1 : -1;
  const stepZ = dz > 0 ? 1 : -1;

  const tDeltaX = dx === 0 ? Infinity : 1 / Math.abs(dx);
  const tDeltaY = dy === 0 ? Infinity : 1 / Math.abs(dy);
  const tDeltaZ = dz === 0 ? Infinity : 1 / Math.abs(dz);

  const tMaxX = dx === 0 ? Infinity : ((stepX > 0 ? cx + 1 - ox : ox - cx) / Math.abs(dx));
  const tMaxY = dy === 0 ? Infinity : ((stepY > 0 ? cy + 1 - oy : oy - cy) / Math.abs(dy));
  const tMaxZ = dz === 0 ? Infinity : ((stepZ > 0 ? cz + 1 - oz : oz - cz) / Math.abs(dz));

  const initialAxis =
    tMaxX < tMaxY && tMaxX < tMaxZ ? 0 :
    tMaxY < tMaxZ ? 1 : 2;

  let lastAxis = initialAxis;
  let dist = 0;

  while (dist <= maxDist) {
    if (isSolid(cx, cy, cz)) {
      const nx = lastAxis === 0 ? -stepX : 0;
      const ny = lastAxis === 1 ? -stepY : 0;
      const nz = lastAxis === 2 ? -stepZ : 0;

      return { x: cx, y: cy, z: cz, nx, ny, nz, dist };
    }

    if (tMaxX < tMaxY && tMaxX < tMaxZ) {
      cx += stepX;
      dist = tMaxX;
      tMaxX += tDeltaX;
      lastAxis = 0;
    } else if (tMaxY < tMaxZ) {
      cy += stepY;
      dist = tMaxY;
      tMaxY += tDeltaY;
      lastAxis = 1;
    } else {
      cz += stepZ;
      dist = tMaxZ;
      tMaxZ += tDeltaZ;
      lastAxis = 2;
    }
  }

  return null;
}

// -------------------------
// Inventory UI
// -------------------------
const inv = document.getElementById("inventory");
const tip = document.getElementById("tip");

const inventoryBlocks = [
  GRASS,
  DIRT,
  STONE,
  SAND,
  WOOD,
  LEAVES,
  PLANK,
  GLASS,
  BRICK
];

function updateInventory() {
  inv.innerHTML = "";

  inventoryBlocks.forEach((blockId, i) => {
    const slot = document.createElement("div");
    slot.className = "slot" + (selectedBlock === blockId ? " active" : "");
    slot.style.background = "#" + COLORS[blockId].getHexString();
    slot.title = BLOCK_NAMES[blockId];

    slot.addEventListener("click", () => {
      selectedBlock = blockId;
      updateInventory();
    });

    inv.appendChild(slot);
  });

  tip.textContent = `Selected: ${BLOCK_NAMES[selectedBlock]}`;
}

updateInventory();

// -------------------------
// Main loop
// -------------------------
generateWorld();
rebuildMesh();

let lastTime = performance.now();
let raf = requestAnimationFrame;

function update() {
  const now = performance.now();
  const dt = Math.min((now - lastTime) / 1000, 0.05);
  lastTime = now;

  camera.rotation.set(player.pitch, player.yaw, 0, "YXZ");
  camera.position.set(player.x, player.y + EYE_HEIGHT, player.z);

  const forward = new THREE.Vector3();
  camera.getWorldDirection(forward);
  forward.y = 0;
  forward.normalize();

  const right = new THREE.Vector3();
  right.crossVectors(forward, new THREE.Vector3(0, 1, 0)).normalize();

  let mx = 0;
  let mz = 0;

  if (keys.KeyW) {
    mx += forward.x;
    mz += forward.z;
  }
  if (keys.KeyS) {
    mx -= forward.x;
    mz -= forward.z;
  }
  if (keys.KeyA) {
    mx -= right.x;
    mz -= right.z;
  }
  if (keys.KeyD) {
    mx += right.x;
    mz += right.z;
  }

  const len = Math.hypot(mx, mz);
  if (len > 0.0001) {
    mx /= len;
    mz /= len;
  }

  const speed = (keys.ShiftLeft || keys.ShiftRight) ? RUN_SPEED : WALK_SPEED;

  if (player.onGround && keys.Space) {
    player.vy = JUMP_SPEED;
    player.onGround = false;
  }

  moveHorizontal(mx * speed, mz * speed, dt);
  moveVertical(dt);

  const target = raycastCamera(6);

  if (target) {
    outline.position.set(target.x + 0.5, target.y + 0.5, target.z + 0.5);
    outline.visible = true;
  } else {
    outline.visible = false;
  }

  if (dirty) {
    rebuildMesh();
  }

  renderer.render(scene, camera);
  raf(update);
}

window.addEventListener("resize", () => {
  renderer.setSize(window.innerWidth, window.innerHeight);
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
});

raf(update);
</script>
</body>
</html>
```

## 補足
- ブロックは `1〜9` で切り替え：Grass / Dirt / Stone / Sand / Wood / Leaves / Plank / Glass / Brick。
- 破壊したブロックや設置したブロックはすぐ反映されます。
- 木も自動生成されます。
- 完全にMinecraftそのものではなく、自作voxelゲーム風です。