Below is a complete, runnable Minecraft-like 3D sandbox game in a single HTML file. It uses Three.js, procedural terrain, voxel placement/removal, pointer lock, WASD movement, jump/fly modes, and an instanced rendering approach for better performance.

Save this as `index.html` and open it in a modern desktop browser (Chrome/Edge/Firefox recommended). A local server is not strictly required, but if you have issues with pointer lock or CDN imports, run it with a simple local server.

```html
<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>マイクラ風3D箱庭</title>
<style>
  html, body {
    margin: 0;
    height: 100%;
    overflow: hidden;
    background: #111;
    color: #fff;
    font-family: system-ui, sans-serif;
    user-select: none;
  }

  #c {
    display: block;
    width: 100%;
    height: 100%;
  }

  #overlay {
    position: fixed;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(0,0,0,0.45);
    cursor: pointer;
    z-index: 10;
  }

  #panel {
    max-width: 560px;
    padding: 24px 28px;
    border-radius: 16px;
    background: rgba(20, 24, 34, 0.88);
    border: 1px solid rgba(255,255,255,0.18);
    box-shadow: 0 10px 40px rgba(0,0,0,0.45);
    line-height: 1.65;
  }

  #panel h1 {
    margin: 0 0 12px;
    font-size: 24px;
  }

  #panel p {
    margin: 8px 0;
    opacity: 0.95;
  }

  #panel .hint {
    margin-top: 14px;
    padding: 10px 12px;
    border-radius: 10px;
    background: rgba(255,255,255,0.08);
  }

  #crosshair {
    position: fixed;
    left: 50%;
    top: 50%;
    width: 18px;
    height: 18px;
    margin-left: -9px;
    margin-top: -9px;
    pointer-events: none;
    z-index: 5;
    opacity: 0.85;
  }

  #crosshair:before,
  #crosshair:after {
    content: "";
    position: absolute;
    background: #fff;
    box-shadow: 0 0 0 1px rgba(0,0,0,0.55);
  }

  #crosshair:before {
    left: 8px;
    top: 0;
    width: 2px;
    height: 18px;
  }

  #crosshair:after {
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
    gap: 8px;
    padding: 8px;
    border-radius: 12px;
    background: rgba(0,0,0,0.35);
    z-index: 6;
  }

  .slot {
    width: 44px;
    height: 44px;
    border-radius: 8px;
    border: 2px solid rgba(255,255,255,0.25);
    position: relative;
    overflow: hidden;
    cursor: pointer;
  }

  .slot.active {
    border-color: #fff;
    box-shadow: 0 0 0 2px rgba(255,255,255,0.22);
    transform: translateY(-2px);
  }

  .slot .key {
    position: absolute;
    right: 3px;
    top: 2px;
    font-size: 10px;
    color: rgba(255,255,255,0.8);
    text-shadow: 0 1px 2px #000;
  }

  #status {
    position: fixed;
    left: 12px;
    bottom: 12px;
    padding: 8px 10px;
    border-radius: 10px;
    background: rgba(0,0,0,0.35);
    z-index: 6;
    font-size: 12px;
    line-height: 1.4;
  }
</style>
</head>
<body>

<div id="overlay">
  <div id="panel">
    <h1>マイクラ風3D箱庭</h1>
    <p>クリックまたはタップでゲームを開始します。</p>
    <p class="hint">
      操作:<br>
      WASD: 移動 / Space: ジャンプ or 上昇 / Shift: 下降<br>
      F: フライト切替 / Ctrl: スプリント / R: スポーン地点へ戻る<br>
      左クリック: ブロック破壊 / 右クリック: ブロック設置<br>
      1-7またはホイール: 設置するブロックを選択<br>
      Esc: マウスキャプチャ解除
    </p>
  </div>
</div>

<div id="crosshair"></div>
<div id="hotbar"></div>
<div id="status"></div>

<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js"
  }
}
</script>

<script type="module">
import * as THREE from "three";

// ------------------------------------------------------------
// Config
// ------------------------------------------------------------
const WORLD_SIZE = 44;          // XZ world size
const WORLD_HEIGHT = 32;        // max block height
const BLOCK_CAP_PER_TYPE = 30000;

const PLAYER_HALF_WIDTH = 0.30;
const PLAYER_HEIGHT = 1.72;
const EYE_HEIGHT = 1.62;

const GRAVITY = 27;
const JUMP_SPEED = 8.6;
const WALK_SPEED = 4.6;
const SPRINT_SPEED = 7.8;
const FLY_SPEED = 14;
const FLY_SPRINT_SPEED = 28;

// ------------------------------------------------------------
// Renderer / scene / camera
// ------------------------------------------------------------
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.domElement.id = "c";
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color("#7ec8ff");
scene.fog = new THREE.Fog("#7ec8ff", 55, 145);

const camera = new THREE.PerspectiveCamera(
  70,
  window.innerWidth / window.innerHeight,
  0.1,
  500
);

const hemiLight = new THREE.HemisphereLight("#dff6ff", "#4f623a", 0.95);
scene.add(hemiLight);

const sun = new THREE.DirectionalLight("#ffffff", 1.0);
sun.position.set(35, 55, 20);
scene.add(sun);

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// ------------------------------------------------------------
// Block definitions
// ------------------------------------------------------------
const BLOCKS = {
  grass:   { label: "草",   color: "#65b945" },
  dirt:    { label: "土",   color: "#8b6b43" },
  stone:   { label: "石",   color: "#8f8f8f" },
  sand:    { label: "砂",   color: "#dccb8a" },
  planks:  { label: "木板", color: "#b6884d" },
  log:     { label: "原木", color: "#7a5233" },
  leaves:  { label: "葉",   color: "#3a822d" },
  bedrock: { label: "基盤", color: "#333333" },
};

const HOTBAR_TYPES = [
  "grass",
  "dirt",
  "stone",
  "sand",
  "planks",
  "log",
  "leaves",
];

let selectedIndex = 0;
let selectedType = HOTBAR_TYPES[selectedIndex];

// ------------------------------------------------------------
// Procedural textures
// ------------------------------------------------------------
function canvasTexture(draw, { transparent = false, alphaTest = 0 } = {}) {
  const canvas = document.createElement("canvas");
  canvas.width = 16;
  canvas.height = 16;
  const ctx = canvas.getContext("2d");

  ctx.clearRect(0, 0, 16, 16);
  draw(ctx);

  const tex = new THREE.CanvasTexture(canvas);
  tex.magFilter = THREE.NearestFilter;
  tex.minFilter = THREE.NearestFilter;
  tex.generateMipmaps = false;
  tex.colorSpace = THREE.SRGBColorSpace;

  const mat = new THREE.MeshLambertMaterial({
    map: tex,
    transparent,
    alphaTest,
  });

  if (transparent) {
    mat.side = THREE.DoubleSide;
  }

  return mat;
}

function hexToRgb(hex) {
  const n = parseInt(hex.slice(1), 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}

function fillNoise(ctx, x0, y0, w, h, hex, amount = 0.12) {
  const [r, g, b] = hexToRgb(hex);
  for (let y = y0; y < y0 + h; y++) {
    for (let x = x0; x < x0 + w; x++) {
      const f = 1 + (Math.random() * 2 - 1) * amount;
      const rr = Math.max(0, Math.min(255, Math.round(r * f)));
      const gg = Math.max(0, Math.min(255, Math.round(g * f)));
      const bb = Math.max(0, Math.min(255, Math.round(b * f)));
      ctx.fillStyle = `rgb(${rr},${gg},${bb})`;
      ctx.fillRect(x, y, 1, 1);
    }
  }
}

function specks(ctx, count, colors) {
  for (let i = 0; i < count; i++) {
    const x = Math.floor(Math.random() * 16);
    const y = Math.floor(Math.random() * 16);
    ctx.fillStyle = colors[Math.floor(Math.random() * colors.length)];
    ctx.fillRect(x, y, 1, 1);
  }
}

const MATERIALS = {
  grass: canvasTexture((ctx) => {
    fillNoise(ctx, 0, 0, 16, 16, "#62b846", 0.12);
    specks(ctx, 28, ["#58a83e", "#71c94f", "#4f9836"]);
  }),

  dirt: canvasTexture((ctx) => {
    fillNoise(ctx, 0, 0, 16, 16, "#8b6b43", 0.15);
    specks(ctx, 24, ["#7b5c38", "#9a7750", "#6b4f2f"]);
  }),

  stone: canvasTexture((ctx) => {
    fillNoise(ctx, 0, 0, 16, 16, "#909090", 0.14);
    specks(ctx, 36, ["#828282", "#a2a2a2", "#757575"]);
  }),

  sand: canvasTexture((ctx) => {
    fillNoise(ctx, 0, 0, 16, 16, "#dccb8a", 0.10);
    specks(ctx, 20, ["#d0bf80", "#e6d696", "#c7b67a"]);
  }),

  planks: canvasTexture((ctx) => {
    fillNoise(ctx, 0, 0, 16, 16, "#b6884d", 0.10);
    ctx.fillStyle = "rgba(60, 35, 15, 0.35)";
    for (let y = 0; y < 16; y += 4) ctx.fillRect(0, y, 16, 1);
    ctx.fillRect(3, 0, 1, 4);
    ctx.fillRect(11, 4, 1, 4);
    ctx.fillRect(6, 8, 1, 4);
    ctx.fillRect(13, 12, 1, 4);
  }),

  log: canvasTexture((ctx) => {
    fillNoise(ctx, 0, 0, 16, 16, "#7a5233", 0.12);
    ctx.fillStyle = "rgba(40, 22, 10, 0.35)";
    for (let x = 1; x < 16; x += 4) {
      for (let y = 0; y < 16; y++) {
        if (Math.random() < 0.72) ctx.fillRect(x, y, 1, 1);
      }
    }
  }),

  leaves: canvasTexture((ctx) => {
    ctx.clearRect(0, 0, 16, 16);
    for (let y = 0; y < 16; y++) {
      for (let x = 0; x < 16; x++) {
        if (Math.random() < 0.12) continue;
        const f = 1 + (Math.random() * 2 - 1) * 0.18;
        const r = Math.max(0, Math.min(255, Math.round(56 * f)));
        const g = Math.max(0, Math.min(255, Math.round(128 * f)));
        const b = Math.max(0, Math.min(255, Math.round(44 * f)));
        ctx.fillStyle = `rgb(${r},${g},${b})`;
        ctx.fillRect(x, y, 1, 1);
      }
    }
  }, { transparent: true, alphaTest: 0.25 }),

  bedrock: canvasTexture((ctx) => {
    fillNoise(ctx, 0, 0, 16, 16, "#383838", 0.22);
    specks(ctx, 32, ["#2a2a2a", "#4a4a4a", "#1f1f1f"]);
  }),
};

// ------------------------------------------------------------
// Instanced voxel world
// ------------------------------------------------------------
const blockGeo = new THREE.BoxGeometry(1, 1, 1);
const blocks = new Map(); // "x,y,z" -> { x, y, z, type, instanceId }
const instanced = {};
const instanceToKey = {};

for (const type of Object.keys(BLOCKS)) {
  const mesh = new THREE.InstancedMesh(blockGeo, MATERIALS[type], BLOCK_CAP_PER_TYPE);
  mesh.count = 0;
  mesh.frustumCulled = false;
  mesh.userData.blockType = type;

  // Large bounding sphere prevents stale bounds issues after edits.
  mesh.boundingSphere = new THREE.Sphere(
    new THREE.Vector3(WORLD_SIZE / 2, WORLD_HEIGHT / 2, WORLD_SIZE / 2),
    1000
  );

  scene.add(mesh);
  instanced[type] = mesh;
  instanceToKey[type] = new Array(BLOCK_CAP_PER_TYPE);
}

const dummy = new THREE.Object3D();
const tmpMatrix = new THREE.Matrix4();

function key(x, y, z) {
  return `${x},${y},${z}`;
}

function inWorld(x, y, z) {
  return x >= 0 && z >= 0 && y >= 0 && x < WORLD_SIZE && z < WORLD_SIZE && y < WORLD_HEIGHT;
}

function addBlock(x, y, z, type) {
  if (!inWorld(x, y, z)) return false;

  const k = key(x, y, z);
  if (blocks.has(k)) return false;

  const mesh = instanced[type];
  if (!mesh || mesh.count >= BLOCK_CAP_PER_TYPE) {
    console.warn(`Block capacity full: ${type}`);
    return false;
  }

  const instanceId = mesh.count;

  dummy.position.set(x + 0.5, y + 0.5, z + 0.5);
  dummy.rotation.set(0, 0, 0);
  dummy.scale.set(1, 1, 1);
  dummy.updateMatrix();

  mesh.setMatrixAt(instanceId, dummy.matrix);
  mesh.count++;
  mesh.instanceMatrix.needsUpdate = true;

  const data = { x, y, z, type, instanceId };
  blocks.set(k, data);
  instanceToKey[type][instanceId] = k;

  return true;
}

function removeBlock(x, y, z) {
  const data = blocks.get(key(x, y, z));
  if (!data) return false;
  if (data.type === "bedrock") return false;

  const type = data.type;
  const mesh = instanced[type];
  const instanceId = data.instanceId;
  const lastId = mesh.count - 1;

  if (instanceId !== lastId) {
    const lastKey = instanceToKey[type][lastId];
    const lastData = blocks.get(lastKey);

    mesh.getMatrixAt(lastId, tmpMatrix);
    mesh.setMatrixAt(instanceId, tmpMatrix);

    if (lastData) {
      lastData.instanceId = instanceId;
      blocks.set(lastKey, lastData);
    }

    instanceToKey[type][instanceId] = lastKey;
  }

  instanceToKey[type][lastId] = undefined;
  mesh.count--;
  mesh.instanceMatrix.needsUpdate = true;

  blocks.delete(key(x, y, z));
  return true;
}

// ------------------------------------------------------------
// Terrain generation
// ------------------------------------------------------------
const heightMap = new Uint8Array(WORLD_SIZE * WORLD_SIZE);

function hash2(x, z) {
  const s = Math.sin(x * 127.1 + z * 311.7) * 43758.5453123;
  return s - Math.floor(s);
}

function smoothNoise2(x, z) {
  const ix = Math.floor(x);
  const iz = Math.floor(z);
  const fx = x - ix;
  const fz = z - iz;

  const sx = fx * fx * (3 - 2 * fx);
  const sz = fz * fz * (3 - 2 * fz);

  const n00 = hash2(ix, iz);
  const n10 = hash2(ix + 1, iz);
  const n01 = hash2(ix, iz + 1);
  const n11 = hash2(ix + 1, iz + 1);

  const lx0 = n00 + (n10 - n00) * sx;
  const lx1 = n01 + (n11 - n01) * sx;
  return lx0 + (lx1 - lx0) * sz;
}

function fbm2(x, z) {
  return (
    0.62 * smoothNoise2(x * 0.085, z * 0.085) +
    0.26 * smoothNoise2(x * 0.20, z * 0.20) +
    0.12 * smoothNoise2(x * 0.42, z * 0.42)
  );
}

function generateWorld() {
  // Terrain
  for (let x = 0; x < WORLD_SIZE; x++) {
    for (let z = 0; z < WORLD_SIZE; z++) {
      const n = fbm2(x, z);
      const h = Math.max(1, Math.min(WORLD_HEIGHT - 10, Math.floor(6 + n * 10)));
      heightMap[x * WORLD_SIZE + z] = h;

      for (let y = 0; y <= h; y++) {
        let type = "stone";

        if (y === 0) type = "bedrock";
        else if (y < h - 2) type = "stone";
        else if (y < h) type = "dirt";
        else {
          // surface
          type = h <= 4 ? "sand" : "grass";
        }

        addBlock(x, y, z, type);
      }
    }
  }

  // Trees
  for (let x = 4; x < WORLD_SIZE - 4; x++) {
    for (let z = 4; z < WORLD_SIZE - 4; z++) {
      const h = heightMap[x * WORLD_SIZE + z];
      const surface = blocks.get(key(x, h, z));
      if (!surface || surface.type !== "grass") continue;

      if (hash2(x * 7.13 + 11, z * 13.77 + 3) > 0.030) continue;

      const trunkHeight = 4;
      const topY = h + trunkHeight;

      // trunk
      for (let y = h + 1; y <= topY; y++) {
        addBlock(x, y, z, "log");
      }

      // leaves
      for (let dx = -2; dx <= 2; dx++) {
        for (let dy = -2; dy <= 1; dy++) {
          for (let dz = -2; dz <= 2; dz++) {
            const manhattan = Math.abs(dx) + Math.abs(dy) + Math.abs(dz);
            if (manhattan > 3) continue;

            const lx = x + dx;
            const ly = topY + dy;
            const lz = z + dz;

            addBlock(lx, ly, lz, "leaves");
          }
        }
      }
    }
  }
}

generateWorld();

// ------------------------------------------------------------
// Player
// ------------------------------------------------------------
const player = {
  pos: new THREE.Vector3(),
  vel: new THREE.Vector3(),
  onGround: false,
  fly: false,
};

function respawn() {
  const cx = Math.floor(WORLD_SIZE / 2);
  const cz = Math.floor(WORLD_SIZE / 2);
  const h = heightMap[cx * WORLD_SIZE + cz] ?? 8;

  player.pos.set(cx + 0.5, h + 1.02, cz + 0.5);
  player.vel.set(0, 0, 0);
  player.onGround = true;

  yaw = Math.PI * 0.15;
  pitch = -0.18;
}

respawn();

// ------------------------------------------------------------
// Controls
// ------------------------------------------------------------
let yaw = Math.PI * 0.15;
let pitch = -0.18;

const keys = new Set();

const overlay = document.getElementById("overlay");
const hotbarEl = document.getElementById("hotbar");
const statusEl = document.getElementById("status");

function startGame() {
  renderer.domElement.requestPointerLock();
}

overlay.addEventListener("click", startGame);
renderer.domElement.addEventListener("click", () => {
  if (document.pointerLockElement !== renderer.domElement) startGame();
});

document.addEventListener("pointerlockchange", () => {
  const locked = document.pointerLockElement === renderer.domElement;
  overlay.style.display = locked ? "none" : "flex";
});

document.addEventListener("mousemove", (e) => {
  if (document.pointerLockElement !== renderer.domElement) return;

  const sensitivity = 0.0022;
  yaw -= e.movementX * sensitivity;
  pitch -= e.movementY * sensitivity;

  const maxPitch = Math.PI / 2 - 0.02;
  pitch = Math.max(-maxPitch, Math.min(maxPitch, pitch));
});

document.addEventListener("contextmenu", (e) => {
  e.preventDefault();
});

document.addEventListener("mousedown", (e) => {
  if (document.pointerLockElement !== renderer.domElement) return;

  if (e.button === 0) {
    breakBlock();
  } else if (e.button === 2) {
    placeBlock();
  }
});

document.addEventListener("wheel", (e) => {
  if (document.pointerLockElement !== renderer.domElement) return;

  if (e.deltaY > 0) {
    selectedIndex = (selectedIndex + 1) % HOTBAR_TYPES.length;
  } else {
    selectedIndex = (selectedIndex - 1 + HOTBAR_TYPES.length) % HOTBAR_TYPES.length;
  }
  selectedType = HOTBAR_TYPES[selectedIndex];
  updateHotbar();
}, { passive: true });

document.addEventListener("keydown", (e) => {
  keys.add(e.code);

  if (e.code === "KeyF") {
    player.fly = !player.fly;
    player.vel.set(0, 0, 0);
  }

  if (e.code === "KeyR") {
    respawn();
  }

  if (e.code.startsWith("Digit")) {
    const idx = Number(e.code.slice(5)) - 1;
    if (idx >= 0 && idx < HOTBAR_TYPES.length) {
      selectedIndex = idx;
      selectedType = HOTBAR_TYPES[idx];
      updateHotbar();
    }
  }

  if (e.code === "Space" || e.code.startsWith("Arrow")) {
    e.preventDefault();
  }
});

document.addEventListener("keyup", (e) => {
  keys.delete(e.code);
});

// ------------------------------------------------------------
// Hotbar UI
// ------------------------------------------------------------
function buildHotbar() {
  hotbarEl.innerHTML = "";

  HOTBAR_TYPES.forEach((type, i) => {
    const div = document.createElement("div");
    div.className = "slot";
    div.style.background = BLOCKS[type].color;
    div.title = BLOCKS[type].label;

    const keyTag = document.createElement("div");
    keyTag.className = "key";
    keyTag.textContent = String(i + 1);
    div.appendChild(keyTag);

    div.addEventListener("click", () => {
      selectedIndex = i;
      selectedType = type;
      updateHotbar();
    });

    hotbarEl.appendChild(div);
  });

  updateHotbar();
}

function updateHotbar() {
  [...hotbarEl.children].forEach((el, i) => {
    el.classList.toggle("active", i === selectedIndex);
  });

  statusEl.innerHTML = `
    ブロック: <strong>${BLOCKS[selectedType].label}</strong><br>
    モード: ${player.fly ? "フライト" : "通常"}
  `;
}

buildHotbar();

// ------------------------------------------------------------
// Target selection
// ------------------------------------------------------------
const raycaster = new THREE.Raycaster();
raycaster.far = 8;
const center = new THREE.Vector2(0, 0);

const highlightGeo = new THREE.BoxGeometry(1.005, 1.005, 1.005);
const highlight = new THREE.LineSegments(
  new THREE.EdgesGeometry(highlightGeo),
  new THREE.LineBasicMaterial({ color: 0x111111, transparent: true, opacity: 0.9 })
);
highlight.visible = false;
highlight.renderOrder = 999;
scene.add(highlight);

const ghost = new THREE.LineSegments(
  new THREE.EdgesGeometry(highlightGeo),
  new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.55 })
);
ghost.visible = false;
ghost.renderOrder = 998;
scene.add(ghost);

let target = null;
let pickAccumulator = 0;

function pickBlock() {
  raycaster.setFromCamera(center, camera);

  const intersects = raycaster.intersectObjects(Object.values(instanced), false);

  for (const inter of intersects) {
    const type = inter.object.userData.blockType;
    const instanceId = inter.instanceId;

    if (!type || instanceId === undefined) continue;

    const k = instanceToKey[type]?.[instanceId];
    if (!k) continue;

    const data = blocks.get(k);
    if (!data || data.instanceId !== instanceId) continue;

    const n = inter.face ? inter.face.normal.clone() : new THREE.Vector3(0, 1, 0);
    n.set(Math.round(n.x), Math.round(n.y), Math.round(n.z));

    if (n.lengthSq() === 0) n.set(0, 1, 0);

    return {
      x: data.x,
      y: data.y,
      z: data.z,
      type: data.type,
      normal: n,
      point: inter.point,
    };
  }

  return null;
}

function updateTarget() {
  target = pickBlock();

  if (target) {
    highlight.visible = true;
    highlight.position.set(target.x + 0.5, target.y + 0.5, target.z + 0.5);

    const px = target.x + target.normal.x;
    const py = target.y + target.normal.y;
    const pz = target.z + target.normal.z;

    if (
      inWorld(px, py, pz) &&
      !blocks.has(key(px, py, pz)) &&
      !wouldBlockOverlapPlayer(px, py, pz)
    ) {
      ghost.visible = true;
      ghost.position.set(px + 0.5, py + 0.5, pz + 0.5);
    } else {
      ghost.visible = false;
    }
  } else {
    highlight.visible = false;
    ghost.visible = false;
  }
}

function breakBlock() {
  const t = target || pickBlock();
  if (!t) return;

  removeBlock(t.x, t.y, t.z);
  updateTarget();
  updateStatusMode();
}

function placeBlock() {
  const t = target || pickBlock();
  if (!t) return;

  const px = t.x + t.normal.x;
  const py = t.y + t.normal.y;
  const pz = t.z + t.normal.z;

  if (!inWorld(px, py, pz)) return;
  if (blocks.has(key(px, py, pz))) return;
  if (wouldBlockOverlapPlayer(px, py, pz)) return;

  addBlock(px, py, pz, selectedType);
  updateTarget();
}

function wouldBlockOverlapPlayer(bx, by, bz) {
  const cx = bx + 0.5;
  const cy = by + 0.5;
  const cz = bz + 0.5;

  const feet = player.pos.y;
  const head = feet + PLAYER_HEIGHT;

  const overlapX = Math.abs(player.pos.x - cx) < 0.5 + PLAYER_HALF_WIDTH;
  const overlapZ = Math.abs(player.pos.z - cz) < 0.5 + PLAYER_HALF_WIDTH;
  const overlapY = feet < by + 1 && head > by;

  return overlapX && overlapY && overlapZ;
}

function updateStatusMode() {
  statusEl.innerHTML = `
    ブロック: <strong>${BLOCKS[selectedType].label}</strong><br>
    モード: ${player.fly ? "フライト" : "通常"}
  `;
}

// ------------------------------------------------------------
// Collision
// ------------------------------------------------------------
function isSolid(x, y, z) {
  return blocks.has(key(x, y, z));
}

function collidesFeet(px, py, pz) {
  const eps = 0.0015;

  const minX = px - PLAYER_HALF_WIDTH;
  const maxX = px + PLAYER_HALF_WIDTH;
  const minY = py + eps;
  const maxY = py + PLAYER_HEIGHT - eps;
  const minZ = pz - PLAYER_HALF_WIDTH;
  const maxZ = pz + PLAYER_HALF_WIDTH;

  const x0 = Math.floor(minX + eps);
  const x1 = Math.floor(maxX - eps);
  const y0 = Math.floor(minY + eps);
  const y1 = Math.floor(maxY - eps);
  const z0 = Math.floor(minZ + eps);
  const z1 = Math.floor(maxZ - eps);

  for (let x = x0; x <= x1; x++) {
    for (let y = y0; y <= y1; y++) {
      for (let z = z0; z <= z1; z++) {
        if (isSolid(x, y, z)) return true;
      }
    }
  }

  return false;
}

function moveAxis(axis, amount) {
  if (amount === 0) return false;

  const steps = Math.max(1, Math.ceil(Math.abs(amount) / 0.12));
  const step = amount / steps;
  const old = player.pos[axis];

  for (let i = 1; i <= steps; i++) {
    player.pos[axis] += step;
    if (collidesFeet(player.pos.x, player.pos.y, player.pos.z)) {
      player.pos[axis] = old;
      return true;
    }
  }

  return false;
}

// ------------------------------------------------------------
// Player update
// ------------------------------------------------------------
const forward = new THREE.Vector3();
const right = new THREE.Vector3();

function updatePlayer(dt) {
  const input = document.pointerLockElement === renderer.domElement;

  forward.set(-Math.sin(yaw), 0, -Math.cos(yaw));
  right.set(Math.cos(yaw), 0, -Math.sin(yaw));

  let mx = 0;
  let mz = 0;

  if (input) {
    if (keys.has("KeyW")) { mx += forward.x; mz += forward.z; }
    if (keys.has("KeyS")) { mx -= forward.x; mz -= forward.z; }
    if (keys.has("KeyD")) { mx += right.x;   mz += right.z;   }
    if (keys.has("KeyA")) { mx -= right.x;   mz -= right.z;   }
  }

  const len = Math.hypot(mx, mz);
  if (len > 0) {
    mx /= len;
    mz /= len;
  }

  const sprint = input && (keys.has("ControlLeft") || keys.has("ControlRight"));

  if (player.fly) {
    const speed = sprint ? FLY_SPRINT_SPEED : FLY_SPEED;

    let vy = 0;
    if (input && keys.has("Space")) vy += 1;
    if (input && (keys.has("ShiftLeft") || keys.has("ShiftRight"))) vy -= 1;

    const hCollisionX = moveAxis("x", mx * speed * dt);
    const hCollisionZ = moveAxis("z", mz * speed * dt);
    const hCollisionY = moveAxis("y", vy * speed * dt);

    if (hCollisionX) player.vel.x = 0;
    if (hCollisionZ) player.vel.z = 0;
    if (hCollisionY) player.vel.y = 0;

    player.vel.set(mx * speed, vy * speed, mz * speed);
    player.onGround = false;
  } else {
    const speed = sprint ? SPRINT_SPEED : WALK_SPEED;

    const targetVX = mx * speed;
    const targetVZ = mz * speed;

    const damp = 1 - Math.exp(-12 * dt);
    player.vel.x += (targetVX - player.vel.x) * damp;
    player.vel.z += (targetVZ - player.vel.z) * damp;

    if (input && keys.has("Space") && player.onGround) {
      player.vel.y = JUMP_SPEED;
      player.onGround = false;
    }

    player.vel.y -= GRAVITY * dt;
    player.vel.y = Math.max(player.vel.y, -28);

    const collisionX = moveAxis("x", player.vel.x * dt);
    const collisionZ = moveAxis("z", player.vel.z * dt);
    const collisionY = moveAxis("y", player.vel.y * dt);

    if (collisionX) player.vel.x = 0;
    if (collisionZ) player.vel.z = 0;

    if (collisionY) {
      if (player.vel.y < 0) player.onGround = true;
      player.vel.y = 0;
    } else {
      player.onGround = false;
    }
  }

  // Prevent falling forever out of the world.
  if (
    player.pos.y < -25 ||
    player.pos.x < -20 ||
    player.pos.z < -20 ||
    player.pos.x > WORLD_SIZE + 20 ||
    player.pos.z > WORLD_SIZE + 20
  ) {
    respawn();
  }

  camera.position.set(player.pos.x, player.pos.y + EYE_HEIGHT, player.pos.z);
  camera.quaternion.setFromEuler(new THREE.Euler(pitch, yaw, 0, "YXZ"));
}

// ------------------------------------------------------------
// Main loop
// ------------------------------------------------------------
const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);

  const dt = Math.min(clock.getDelta(), 0.033);

  updatePlayer(dt);

  pickAccumulator += dt;
  if (pickAccumulator > 0.05) {
    pickAccumulator = 0;
    updateTarget();
    updateStatusMode();
  }

  renderer.render(scene, camera);
}

updateStatusMode();
animate();
</script>

</body>
</html>
```

Notes:

- The world is a small procedural voxel island/hills sandbox.
- Bedrock at the bottom is unbreakable.
- Leaves use transparent pixel-style holes.
- Movement uses a simple voxel AABB collision system.
- Fly mode is useful for quickly building and inspecting the terrain.
- If you want a much larger world later, the next natural improvement is chunking and dynamic mesh generation around the player.