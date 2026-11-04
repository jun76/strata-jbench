できます。  
以下は **ブラウザだけで動く Minecraft風3Dボクセル箱庭ゲーム**です。  
ファイル1つで完結するように作っています。

## 使い方

1. PCのブラウザ向けです。
2. 下記コードを `index.html` として保存します。
3. そのHTMLをブラウザで開きます。
4. 画面をクリックするとマウスで視点操作できます。

## 操作

- `W A S D` : 移動
- `Space` : ジャンプ
- `Shift` : ダッシュ
- `左クリック` : ブロック破壊
- `右クリック` : ブロック設置
- `1〜6` : 置くブロックの種類選択
- `Esc` : ポインターロック解除

## 特徴

- 簡易地形生成
- 木生成
- ブロック破壊/設置
- 当たり判定
- 重力
- 簡易ホットバー

---

```html
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>マイクラ風3D箱庭ゲーム</title>
<style>
  html, body {
    margin: 0;
    overflow: hidden;
    background: #000;
    font-family: sans-serif;
  }

  canvas {
    display: block;
  }

  #hud {
    position: fixed;
    top: 12px;
    left: 12px;
    color: white;
    text-shadow: 1px 1px 2px black;
    pointer-events: none;
    font-size: 14px;
    line-height: 1.5;
  }

  #crosshair {
    position: fixed;
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
    background: white;
    box-shadow: 0 0 2px black;
  }

  #crosshair::before {
    width: 2px;
    height: 18px;
    left: 8px;
    top: 0;
  }

  #crosshair::after {
    width: 18px;
    height: 2px;
    left: 0;
    top: 8px;
  }

  #hotbar {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: 6px;
    pointer-events: none;
  }

  .slot {
    width: 48px;
    height: 48px;
    border: 3px solid rgba(255,255,255,0.35);
    border-radius: 6px;
    box-shadow: inset 0 0 10px rgba(0,0,0,0.45);
  }

  .slot.selected {
    border-color: #ffe066;
    box-shadow:
      inset 0 0 10px rgba(0,0,0,0.45),
      0 0 12px #ffe066;
  }
</style>

<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js"
  }
}
</script>
</head>
<body>

<div id="hud">
  W A S D : 移動<br />
  Space : ジャンプ<br />
  Shift : ダッシュ<br />
  左クリック : 破壊<br />
  右クリック : 設置<br />
  1〜6 : ブロック選択<br />
  画面クリックで視点操作開始
</div>

<div id="crosshair"></div>
<div id="hotbar"></div>

<script type="module">
import * as THREE from "three";

// -----------------------------
// 定数
// -----------------------------
const SIZE = 48;
const HEIGHT = 32;
const MAX_INSTANCES = SIZE * SIZE * HEIGHT;

const PLAYER_HALF_WIDTH = 0.3;
const PLAYER_HEIGHT = 1.8;
const EYE_HEIGHT = 1.62;

const GRAVITY = -24;
const JUMP = 8.2;
const SPEED = 4.5;
const SPRINT_SPEED = 8.0;
const REACH = 6;

const BLOCK = {
  GRASS: 1,
  DIRT: 2,
  STONE: 3,
  SAND: 4,
  WOOD: 5,
  LEAVES: 6
};

// -----------------------------
// ワールドデータ
// -----------------------------
const world = new Uint8Array(SIZE * SIZE * HEIGHT);
const heightMap = new Uint8Array(SIZE * SIZE);

function idx(x, y, z) {
  return (y * SIZE + z) * SIZE + x;
}

function inBounds(x, y, z) {
  return x >= 0 && x < SIZE && y >= 0 && y < HEIGHT && z >= 0 && z < SIZE;
}

function getBlock(x, y, z) {
  if (!inBounds(x, y, z)) return 0;
  return world[idx(x, y, z)];
}

function setBlock(x, y, z, type) {
  if (!inBounds(x, y, z)) return false;
  world[idx(x, y, z)] = type;
  return true;
}

function isSolidForCollision(x, y, z) {
  if (y < 0) return true;

  if (!inBounds(x, y, z)) {
    if (y >= HEIGHT) return false;
    // 外周は透明な壁にする
    return x < 0 || x >= SIZE || z < 0 || z >= SIZE;
  }

  return world[idx(x, y, z)] !== 0;
}

// -----------------------------
// ノイズ系
// -----------------------------
function hash2(x, z) {
  let h = Math.imul(x, 374761393) ^ Math.imul(z, 668265263);
  h = (h ^ (h >>> 13)) >>> 0;
  h = Math.imul(h, 1274126177) >>> 0;
  h = (h ^ (h >>> 16)) >>> 0;
  return (h & 0xffffff) / 0xffffff;
}

function lerp(a, b, t) {
  return a + (b - a) * t;
}

function smooth(t) {
  return t * t * (3 - 2 * t);
}

function noise2(x, z) {
  const xi = Math.floor(x);
  const zi = Math.floor(z);
  const xf = x - xi;
  const zf = z - zi;

  const u = smooth(xf);
  const v = smooth(zf);

  const a = hash2(xi, zi);
  const b = hash2(xi + 1, zi);
  const c = hash2(xi, zi + 1);
  const d = hash2(xi + 1, zi + 1);

  return lerp(lerp(a, b, u), lerp(c, d, u), v);
}

function clamp(v, min, max) {
  return Math.max(min, Math.min(max, v));
}

// -----------------------------
// 地形生成
// -----------------------------
function generateWorld() {
  world.fill(0);
  heightMap.fill(0);

  for (let z = 0; z < SIZE; z++) {
    for (let x = 0; x < SIZE; x++) {
      let h =
        6 +
        Math.floor(
          7 * noise2(x * 0.07, z * 0.07) +
          5 * noise2(x * 0.18, z * 0.18) +
          2 * noise2(x * 0.40, z * 0.40)
        );

      h = clamp(h, 3, HEIGHT - 10);
      heightMap[z * SIZE + x] = h;

      for (let y = 0; y <= h; y++) {
        let type;

        if (y === h) {
          type = h <= 5 ? BLOCK.SAND : BLOCK.GRASS;
        } else if (y >= h - 2) {
          type = BLOCK.DIRT;
        } else {
          type = BLOCK.STONE;
        }

        world[idx(x, y, z)] = type;
      }
    }
  }

  // 木
  for (let z = 2; z < SIZE - 2; z++) {
    for (let x = 2; x < SIZE - 2; x++) {
      const r = hash2(x + 17, z + 29);
      const h = heightMap[z * SIZE + x];

      if (r < 0.006 && h > 6 && h < HEIGHT - 8) {
        placeTree(x, z, h);
      }
    }
  }
}

function placeTree(x, z, h) {
  const trunkHeight = 3 + Math.floor(hash2(x + 91, z + 73) * 3);
  const topY = h + trunkHeight;

  for (let y = h + 1; y <= topY; y++) {
    setBlock(x, y, z, BLOCK.WOOD);
  }

  for (let ly = topY - 1; ly <= topY + 1; ly++) {
    for (let lx = x - 2; lx <= x + 2; lx++) {
      for (let lz = z - 2; lz <= z + 2; lz++) {
        if (lx === x && lz === z && ly <= topY) continue;

        const d = Math.abs(lx - x) + Math.abs(ly - topY) + Math.abs(lz - z);
        if (d <= 4 && getBlock(lx, ly, lz) === 0) {
          setBlock(lx, ly, lz, BLOCK.LEAVES);
        }
      }
    }
  }
}

// -----------------------------
// テクスチャ生成
// -----------------------------
function createTexture(type) {
  const canvas = document.createElement("canvas");
  canvas.width = 16;
  canvas.height = 16;

  const ctx = canvas.getContext("2d");
  const image = ctx.createImageData(16, 16);

  for (let y = 0; y < 16; y++) {
    for (let x = 0; x < 16; x++) {
      const rnd = Math.random();

      let r, g, b;

      if (type === BLOCK.GRASS) {
        r = 70 + rnd * 25;
        g = 140 + rnd * 35;
        b = 60 + rnd * 25;
      } else if (type === BLOCK.DIRT) {
        r = 100 + rnd * 40;
        g = 70 + rnd * 20;
        b = 45 + rnd * 20;
      } else if (type === BLOCK.STONE) {
        const s = 100 + rnd * 60;
        r = s;
        g = s;
        b = s;
      } else if (type === BLOCK.SAND) {
        r = 200 + rnd * 40;
        g = 190 + rnd * 40;
        b = 130 + rnd * 30;
      } else if (type === BLOCK.WOOD) {
        const dark = x % 4 === 0 || x % 7 === 0;
        if (dark) {
          r = 70 + rnd * 20;
          g = 50 + rnd * 15;
          b = 30 + rnd * 10;
        } else {
          r = 130 + rnd * 20;
          g = 95 + rnd * 15;
          b = 60 + rnd * 10;
        }
      } else if (type === BLOCK.LEAVES) {
        r = 35 + rnd * 35;
        g = 110 + rnd * 50;
        b = 40 + rnd * 30;
      }

      const i = (y * 16 + x) * 4;
      image.data[i] = r;
      image.data[i + 1] = g;
      image.data[i + 2] = b;
      image.data[i + 3] = 255;
    }
  }

  ctx.putImageData(image, 0, 0);

  const texture = new THREE.CanvasTexture(canvas);
  texture.magFilter = THREE.NearestFilter;
  texture.minFilter = THREE.NearestFilter;
  texture.generateMipmaps = false;
  return texture;
}

// -----------------------------
// Three.js 初期化
// -----------------------------
const scene = new THREE.Scene();

const camera = new THREE.PerspectiveCamera(
  75,
  window.innerWidth / window.innerHeight,
  0.1,
  500
);
camera.rotation.order = "YXZ";

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const skyColor = 0x87ceeb;
scene.background = new THREE.Color(skyColor);
scene.fog = new THREE.Fog(skyColor, 45, 110);

scene.add(new THREE.AmbientLight(0xffffff, 0.65));

const sun = new THREE.DirectionalLight(0xffffff, 0.7);
sun.position.set(40, 60, 20);
scene.add(sun);

const boxGeometry = new THREE.BoxGeometry(1, 1, 1);
const meshes = [];

for (let type = 1; type <= 6; type++) {
  const material = new THREE.MeshLambertMaterial({
    map: createTexture(type)
  });

  meshes[type] = new THREE.InstancedMesh(
    boxGeometry,
    material,
    MAX_INSTANCES
  );

  meshes[type].frustumCulled = false;
  scene.add(meshes[type]);
}

// -----------------------------
// メッシュ再構築
// -----------------------------
function isFullyHidden(x, y, z) {
  return (
    getBlock(x - 1, y, z) !== 0 &&
    getBlock(x + 1, y, z) !== 0 &&
    getBlock(x, y + 1, z) !== 0 &&
    getBlock(x, y - 1, z) !== 0 &&
    getBlock(x, y, z - 1) !== 0 &&
    getBlock(x, y, z + 1) !== 0
  );
}

const dummy = new THREE.Object3D();

function rebuild() {
  const counts = new Int32Array(7);

  for (let y = 0; y < HEIGHT; y++) {
    for (let z = 0; z < SIZE; z++) {
      for (let x = 0; x < SIZE; x++) {
        const type = world[idx(x, y, z)];
        if (!type) continue;

        if (isFullyHidden(x, y, z)) continue;

        if (counts[type] >= MAX_INSTANCES) continue;

        dummy.position.set(x + 0.5, y + 0.5, z + 0.5);
        dummy.updateMatrix();

        meshes[type].setMatrixAt(counts[type], dummy.matrix);
        counts[type]++;
      }
    }
  }

  for (let type = 1; type <= 6; type++) {
    meshes[type].count = counts[type];
    meshes[type].instanceMatrix.needsUpdate = true;
  }
}

// -----------------------------
// レイキャスト
// -----------------------------
function raycast(origin, dir, maxDist) {
  let x = Math.floor(origin.x);
  let y = Math.floor(origin.y);
  let z = Math.floor(origin.z);

  const stepX = Math.sign(dir.x);
  const stepY = Math.sign(dir.y);
  const stepZ = Math.sign(dir.z);

  const tDeltaX = dir.x !== 0 ? Math.abs(1 / dir.x) : Infinity;
  const tDeltaY = dir.y !== 0 ? Math.abs(1 / dir.y) : Infinity;
  const tDeltaZ = dir.z !== 0 ? Math.abs(1 / dir.z) : Infinity;

  let tMaxX = Infinity;
  let tMaxY = Infinity;
  let tMaxZ = Infinity;

  if (dir.x > 0) {
    tMaxX = (Math.floor(origin.x) + 1 - origin.x) / dir.x;
  } else if (dir.x < 0) {
    tMaxX = (Math.floor(origin.x) - origin.x) / dir.x;
  }

  if (dir.y > 0) {
    tMaxY = (Math.floor(origin.y) + 1 - origin.y) / dir.y;
  } else if (dir.y < 0) {
    tMaxY = (Math.floor(origin.y) - origin.y) / dir.y;
  }

  if (dir.z > 0) {
    tMaxZ = (Math.floor(origin.z) + 1 - origin.z) / dir.z;
  } else if (dir.z < 0) {
    tMaxZ = (Math.floor(origin.z) - origin.z) / dir.z;
  }

  const normal = new THREE.Vector3(0, 1, 0);

  for (let i = 0; i < 200; i++) {
    if (isRaySolid(x, y, z)) {
      return {
        x,
        y,
        z,
        normal: normal.clone()
      };
    }

    if (tMaxX > maxDist && tMaxY > maxDist && tMaxZ > maxDist) break;

    if (tMaxX < tMaxY && tMaxX < tMaxZ) {
      if (tMaxX > maxDist) break;
      x += stepX;
      tMaxX += tDeltaX;
      normal.set(-stepX, 0, 0);
    } else if (tMaxY < tMaxZ) {
      if (tMaxY > maxDist) break;
      y += stepY;
      tMaxY += tDeltaY;
      normal.set(0, -stepY, 0);
    } else {
      if (tMaxZ > maxDist) break;
      z += stepZ;
      tMaxZ += tDeltaZ;
      normal.set(0, 0, -stepZ);
    }
  }

  return null;
}

function isRaySolid(x, y, z) {
  return inBounds(x, y, z) && world[idx(x, y, z)] !== 0;
}

// -----------------------------
// プレイヤー
// -----------------------------
const player = {
  x: SIZE / 2 + 0.5,
  y: 20,
  z: SIZE / 2 + 0.5
};

const velocity = new THREE.Vector3(0, 0, 0);
let onGround = false;

function collides(px, py, pz) {
  const minX = Math.floor(px - PLAYER_HALF_WIDTH + 1e-6);
  const maxX = Math.floor(px + PLAYER_HALF_WIDTH - 1e-6);
  const minY = Math.floor(py + 1e-6);
  const maxY = Math.floor(py + PLAYER_HEIGHT - 1e-6);
  const minZ = Math.floor(pz - PLAYER_HALF_WIDTH + 1e-6);
  const maxZ = Math.floor(pz + PLAYER_HALF_WIDTH - 1e-6);

  for (let ix = minX; ix <= maxX; ix++) {
    for (let iy = minY; iy <= maxY; iy++) {
      for (let iz = minZ; iz <= maxZ; iz++) {
        if (isSolidForCollision(ix, iy, iz)) {
          return true;
        }
      }
    }
  }

  return false;
}

function blockIntersectsPlayer(x, y, z) {
  return (
    x < player.x + PLAYER_HALF_WIDTH &&
    x + 1 > player.x - PLAYER_HALF_WIDTH &&
    y < player.y + PLAYER_HEIGHT &&
    y + 1 > player.y &&
    z < player.z + PLAYER_HALF_WIDTH &&
    z + 1 > player.z - PLAYER_HALF_WIDTH
  );
}

function respawnPlayer() {
  const cx = Math.floor(SIZE / 2);
  const cz = Math.floor(SIZE / 2);

  let top = 0;
  for (let y = HEIGHT - 1; y >= 0; y--) {
    if (getBlock(cx, y, cz) !== 0) {
      top = y;
      break;
    }
  }

  player.x = cx + 0.5;
  player.y = top + 1;
  player.z = cz + 0.5;

  velocity.set(0, 0, 0);
  onGround = false;

  yaw = 0;
  pitch = 0;
}

// -----------------------------
// ブロック破壊/設置
// -----------------------------
let selected = BLOCK.GRASS;
const rayDir = new THREE.Vector3();

function breakBlock() {
  camera.getWorldDirection(rayDir);
  const hit = raycast(camera.position, rayDir, REACH);
  if (!hit) return;

  if (!inBounds(hit.x, hit.y, hit.z)) return;

  world[idx(hit.x, hit.y, hit.z)] = 0;
  rebuild();
}

function placeBlock() {
  camera.getWorldDirection(rayDir);
  const hit = raycast(camera.position, rayDir, REACH);
  if (!hit) return;

  const nx = hit.x + hit.normal.x;
  const ny = hit.y + hit.normal.y;
  const nz = hit.z + hit.normal.z;

  if (!inBounds(nx, ny, nz)) return;
  if (world[idx(nx, ny, nz)] !== 0) return;
  if (blockIntersectsPlayer(nx, ny, nz)) return;

  world[idx(nx, ny, nz)] = selected;
  rebuild();
}

// -----------------------------
// UI
// -----------------------------
const blockData = {
  [BLOCK.GRASS]: { name: "草ブロック", css: "#5aa547" },
  [BLOCK.DIRT]: { name: "土ブロック", css: "#795642" },
  [BLOCK.STONE]: { name: "石ブロック", css: "#8e8e8e" },
  [BLOCK.SAND]: { name: "砂ブロック", css: "#d8c17a" },
  [BLOCK.WOOD]: { name: "木材", css: "#7b5233" },
  [BLOCK.LEAVES]: { name: "葉", css: "#3f8f3e" }
};

const hotbar = document.getElementById("hotbar");
const slots = {};

for (let type = 1; type <= 6; type++) {
  const div = document.createElement("div");
  div.className = "slot";
  div.style.background = blockData[type].css;
  div.title = blockData[type].name;
  hotbar.appendChild(div);
  slots[type] = div;
}

function updateHotbar() {
  for (let type = 1; type <= 6; type++) {
    slots[type].classList.toggle("selected", type === selected);
  }
}

// -----------------------------
// 入力
// -----------------------------
const keys = {};
let isLocked = false;
let yaw = 0;
let pitch = 0;

renderer.domElement.addEventListener("pointerdown", (e) => {
  if (!isLocked) {
    renderer.domElement.requestPointerLock();
    return;
  }

  if (e.button === 0) {
    breakBlock();
  } else if (e.button === 2) {
    placeBlock();
  }
});

window.addEventListener("contextmenu", (e) => e.preventDefault());

document.addEventListener("pointerlockchange", () => {
  isLocked = document.pointerLockElement === renderer.domElement;
});

window.addEventListener("mousemove", (e) => {
  if (!isLocked) return;

  const sensitivity = 0.0022;
  yaw -= e.movementX * sensitivity;
  pitch -= e.movementY * sensitivity;

  const limit = Math.PI / 2 - 0.01;
  pitch = clamp(pitch, -limit, limit);
});

window.addEventListener("keydown", (e) => {
  keys[e.code] = true;

  if (e.code === "Digit1") selected = BLOCK.GRASS;
  if (e.code === "Digit2") selected = BLOCK.DIRT;
  if (e.code === "Digit3") selected = BLOCK.STONE;
  if (e.code === "Digit4") selected = BLOCK.SAND;
  if (e.code === "Digit5") selected = BLOCK.WOOD;
  if (e.code === "Digit6") selected = BLOCK.LEAVES;

  updateHotbar();

  if (e.code === "Space") e.preventDefault();
});

window.addEventListener("keyup", (e) => {
  keys[e.code] = false;
});

// -----------------------------
// 更新
// -----------------------------
function update(dt) {
  if (isLocked) {
    camera.rotation.y = yaw;
    camera.rotation.x = pitch;
    camera.rotation.z = 0;
  }

  let mx = 0;
  let mz = 0;

  if (keys["KeyW"]) {
    mx -= Math.sin(yaw);
    mz -= Math.cos(yaw);
  }

  if (keys["KeyS"]) {
    mx += Math.sin(yaw);
    mz += Math.cos(yaw);
  }

  if (keys["KeyA"]) {
    mx -= Math.cos(yaw);
    mz += Math.sin(yaw);
  }

  if (keys["KeyD"]) {
    mx += Math.cos(yaw);
    mz -= Math.sin(yaw);
  }

  const len = Math.hypot(mx, mz);
  if (len > 1) {
    mx /= len;
    mz /= len;
  }

  const speed = keys["ShiftLeft"] || keys["ShiftRight"] ? SPRINT_SPEED : SPEED;

  velocity.x = mx * speed;
  velocity.z = mz * speed;

  velocity.y += GRAVITY * dt;

  if (keys["Space"] && onGround) {
    velocity.y = JUMP;
    onGround = false;
  }

  // X方向
  player.x += velocity.x * dt;
  if (collides(player.x, player.y, player.z)) {
    player.x -= velocity.x * dt;
    velocity.x = 0;
  }

  // Z方向
  player.z += velocity.z * dt;
  if (collides(player.x, player.y, player.z)) {
    player.z -= velocity.z * dt;
    velocity.z = 0;
  }

  // Y方向
  const vy = velocity.y;
  player.y += vy * dt;

  if (collides(player.x, player.y, player.z)) {
    player.y -= vy * dt;
    velocity.y = 0;

    if (vy < 0) {
      onGround = true;
    }
  } else {
    if (vy < 0) {
      onGround = false;
    }
  }

  if (player.y < -30 || player.y > HEIGHT + 50) {
    respawnPlayer();
  }

  camera.position.set(player.x, player.y + EYE_HEIGHT, player.z);
}

// -----------------------------
// ゲーム開始
// -----------------------------
generateWorld();
rebuild();
respawnPlayer();
updateHotbar();

let last = performance.now();

function animate() {
  requestAnimationFrame(animate);

  const now = performance.now();
  let dt = (now - last) / 1000;
  last = now;
  dt = Math.min(dt, 0.05);

  update(dt);
  renderer.render(scene, camera);
}

animate();

// -----------------------------
// リサイズ
// -----------------------------
window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
</script>

</body>
</html>
```

次は、  
**水ブロック**、**洞窟**、**アイテム取得**、**インベントリ**、**ブロックのテクスチャをさらに凝る**、**スマホ対応**  
みたいな拡張もできます。