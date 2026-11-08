マイクラ風の「3D箱庭ブロックゲーム」をブラウザで遊べる単一 HTML ファイルとして作りました。  
`index.html` に保存して Chrome/Edge/Firefox で開くとそのまま動きます。

**できること**

- WASD で移動 / スペースでジャンプ
- マウスで視点操作（クリックでポインターロック）
- 数字 `1〜7` でブロック選択
- 左クリックでブロック破壊
- 右クリックでブロック設置
- 簡易地形生成・木生成・ガラス設置

```html
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>マイクラ風 3D 箱庭ゲーム</title>
<style>
  html, body {
    margin: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
    background: #2b2b35;
    font-family: system-ui, -apple-system, "Segoe UI", "Hiragino Sans", "Yu Gothic UI", sans-serif;
    color: #fff;
  }

  canvas {
    display: block;
  }

  #ui {
    position: fixed;
    left: 16px;
    top: 16px;
    z-index: 10;
    pointer-events: none;
    user-select: none;
  }

  #title {
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 0.04em;
    margin-bottom: 8px;
    text-shadow: 0 2px 8px rgba(0,0,0,.45);
  }

  #info {
    font-size: 13px;
    line-height: 1.55;
    background: rgba(10,10,15,.55);
    padding: 10px 12px;
    border-radius: 12px;
    max-width: 420px;
    box-shadow: 0 4px 18px rgba(0,0,0,.35);
  }

  #hotbar {
    display: flex;
    gap: 8px;
    margin-top: 12px;
  }

  .slot {
    width: 42px;
    height: 42px;
    border-radius: 10px;
    background: rgba(30,30,40,.75);
    border: 2px solid rgba(255,255,255,.18);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    color: #cfd6ff;
    box-shadow: 0 3px 10px rgba(0,0,0,.25);
  }

  .slot.selected {
    border-color: #ffffff;
    box-shadow: 0 0 0 3px rgba(140,210,255,.35), 0 4px 14px rgba(0,0,0,.35);
  }

  .swatch {
    width: 22px;
    height: 22px;
    border-radius: 6px;
  }

  #crosshair {
    position: fixed;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    width: 20px;
    height: 20px;
    z-index: 9;
    pointer-events: none;
  }

  #crosshair::before, #crosshair::after {
    content: "";
    position: absolute;
    background: rgba(255,255,255,.8);
    box-shadow: 0 0 6px rgba(0,0,0,.45);
  }

  #crosshair::before {
    left: 9px;
    top: 0;
    width: 2px;
    height: 20px;
  }

  #crosshair::after {
    left: 0;
    top: 9px;
    width: 20px;
    height: 2px;
  }

  .key {
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    background: rgba(255,255,255,.12);
    border-radius: 6px;
    padding: 2px 6px;
    margin-right: 4px;
  }
</style>
</head>
<body>

<div id="ui">
  <div id="title">マイクラ風 3D 箱庭ブロックゲーム</div>

  <div id="info">
    <div><span class="key">W</span> 前 / <span class="key">S</span> 後</div>
    <div><span class="key">A</span> 左 / <span class="key">D</span> 右</div>
    <div><span class="key">Space</span> ジャンプ / <span class="key">F</span> 飛行切替</div>
    <div><span class="key">1〜7</span> ブロック選択</div>
    <div>左クリック：ブロック破壊</div>
    <div>右クリック：ブロック設置</div>
    <div>クリックでマウス捕捉。解除は Esc。</div>
  </div>

  <div id="hotbar"></div>
</div>

<div id="crosshair"></div>

<script type="module">
import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js";

/*
  ------------------------------------------------
  基本設定
  ------------------------------------------------
*/
const W = 32;
const H = 24;
const D = 32;
const MAX_INSTANCES = W * H * D;

const AIR = 0;
const GRASS = 1;
const DIRT = 2;
const STONE = 3;
const WOOD = 4;
const LEAVES = 5;
const SAND = 6;
const GLASS = 7;

const TYPE_NAMES = ["", "Grass", "Dirt", "Stone", "Wood", "Leaves", "Sand", "Glass"];

const typeConfigs = [
  null,
  { top: 0x59a84f, side: 0x7b5e3e, bottom: 0x7b5e3e },
  { top: 0x7b5e3e, side: 0x7b5e3e, bottom: 0x7b5e3e },
  { top: 0x828993, side: 0x767d86, bottom: 0x767d86 },
  { top: 0x8a6a3e, side: 0x8a6a3e, bottom: 0x8a6a3e },
  { top: 0x4e8039, side: 0x4e8039, bottom: 0x4e8039 },
  { top: 0xd3bd84, side: 0xd3bd84, bottom: 0xd3bd84 },
  { top: 0x96c3ff, side: 0x96c3ff, bottom: 0x96c3ff, transparent: true, opacity: 0.35 }
];

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 24, 80);

const camera = new THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 0.1, 200);
camera.rotation.order = "YXZ";

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setAnimationLoop(animate);
document.body.appendChild(renderer.domElement);

/*
  ------------------------------------------------
  光源
  ------------------------------------------------
*/
const hemi = new THREE.HemisphereLight(0xbdd7ff, 0x556044, 0.85);
scene.add(hemi);

const dirLight = new THREE.DirectionalLight(0xffffff, 0.85);
dirLight.position.set(10, 18, 7);
scene.add(dirLight);

/*
  ------------------------------------------------
  ボクセルデータ
  ------------------------------------------------
*/
const data = new Uint8Array(W * H * D);

function idx(x, y, z) {
  return x + y * W + z * W * H;
}

function getBlock(x, y, z) {
  if (x < 0 || x >= W || y < 0 || y >= H || z < 0 || z >= D) return AIR;
  return data[idx(x, y, z)];
}

function setBlockRaw(x, y, z, type) {
  if (x < 0 || x >= W || y < 0 || y >= H || z < 0 || z >= D) return;
  data[idx(x, y, z)] = type;
}

function setBlock(x, y, z, type) {
  setBlockRaw(x, y, z, type);
  rebuildInstances();
}

function isSolid(block) {
  return block !== AIR;
}

/*
  ------------------------------------------------
  地形生成
  ------------------------------------------------
*/
function hash2(x, y) {
  let h = ((x | 0) * 73856093) ^ ((y | 0) * 19349157);
  h = Math.abs(h);
  return (h & 255) / 255.0;
}

function noise2(x, y) {
  const x0 = Math.floor(x);
  const y0 = Math.floor(y);
  const x1 = x0 + 1;
  const y1 = y0 + 1;

  const fx = x - x0;
  const fy = y - y0;

  const u = fx * fx * (3 - 2 * fx);
  const v = fy * fy * (3 - 2 * fy);

  const a = hash2(x0, y0);
  const b = hash2(x1, y0);
  const c = hash2(x0, y1);
  const d = hash2(x1, y1);

  const ab = a * (1 - u) + b * u;
  const cd = c * (1 - u) + d * u;

  return ab * (1 - v) + cd * v;
}

function heightAt(x, z) {
  const n = noise2(x * 0.07, z * 0.07);
  const h = Math.floor(8 + n * 8);
  return Math.max(2, Math.min(H - 8, h));
}

function mulberry32(seed) {
  return function () {
    seed |= 0;
    seed = seed + 0x6D2B79F5 | 0;
    let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}

const rand = mulberry32(13337);

function generateWorld() {
  for (let z = 0; z < D; z++) {
    for (let x = 0; x < W; x++) {
      const h = heightAt(x, z);

      for (let y = 0; y < H; y++) {
        let block = AIR;

        if (y <= h) {
          if (y === h) {
            block = h <= 5 ? SAND : GRASS;
          } else if (y >= h - 3) {
            block = DIRT;
          } else {
            block = STONE;
          }
        }

        data[idx(x, y, z)] = block;
      }
    }
  }

  for (let z = 0; z < D; z++) {
    for (let x = 0; x < W; x++) {
      const h = heightAt(x, z);
      const surface = getBlock(x, h, z);

      if (surface === GRASS && rand() < 0.035) {
        for (let dy = 1; dy <= 4; dy++) {
          setBlockRaw(x, h + dy, z, WOOD);
        }

        for (let dx = -2; dx <= 2; dx++) {
          for (let dz = -2; dz <= 2; dz++) {
            const d = dx * dx + dz * dz;
            if (d === 0 || d > 4) continue;

            const yTop = h + 5;
            const yTop2 = h + 6;

            if (getBlock(x + dx, yTop, z + dz) === AIR) {
              setBlockRaw(x + dx, yTop, z + dz, LEAVES);
            }

            if (d <= 1 && getBlock(x + dx, yTop2, z + dz) === AIR) {
              setBlockRaw(x + dx, yTop2, z + dz, LEAVES);
            }
          }
        }
      }
    }
  }
}

/*
  ------------------------------------------------
  ブロックメッシュ生成
  ------------------------------------------------
*/
function makeGeometry(config) {
  const g = new THREE.BoxGeometry(1, 1, 1);
  const pos = g.attributes.position;
  const normal = g.attributes.normal;
  const colorAttr = new Float32Array(pos.count * 3);

  const top = new THREE.Color(config.top);
  const side = new THREE.Color(config.side);
  const bottom = new THREE.Color(config.bottom);

  for (let i = 0; i < pos.count; i++) {
    const nx = normal.getX(i);
    const ny = normal.getY(i);
    const nz = normal.getZ(i);

    let c;
    if (ny > 0.5) c = top;
    else if (ny < -0.5) c = bottom;
    else c = side;

    colorAttr[i * 3 + 0] = c.r;
    colorAttr[i * 3 + 1] = c.g;
    colorAttr[i * 3 + 2] = c.b;
  }

  g.setAttribute("color", new THREE.BufferAttribute(colorAttr, 3));
  return g;
}

function makeMaterial(config) {
  return new THREE.MeshLambertMaterial({
    vertexColors: true,
    transparent: !!config.transparent,
    opacity: config.opacity ?? 1
  });
}

const typeGeometries = [null];
const typeMaterials = [null];
const typeMeshes = [null];

for (let t = 1; t <= 7; t++) {
  typeGeometries[t] = makeGeometry(typeConfigs[t]);
  typeMaterials[t] = makeMaterial(typeConfigs[t]);

  const mesh = new THREE.InstancedMesh(typeGeometries[t], typeMaterials[t], MAX_INSTANCES);
  mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
  mesh.frustumCulled = false;
  mesh.count = 0;
  scene.add(mesh);
  typeMeshes[t] = mesh;
}

function rebuildInstances() {
  const counts = new Array(8).fill(0);
  const matrix = new THREE.Matrix4();

  for (let z = 0; z < D; z++) {
    for (let y = 0; y < H; y++) {
      for (let x = 0; x < W; x++) {
        const block = data[idx(x, y, z)];
        if (block === AIR) continue;

        const mesh = typeMeshes[block];
        if (!mesh) continue;

        const count = counts[block];
        if (count >= MAX_INSTANCES) continue;

        matrix.makeTranslation(x + 0.5, y + 0.5, z + 0.5);
        mesh.setMatrixAt(count, matrix);
        counts[block]++;
      }
    }
  }

  for (let t = 1; t <= 7; t++) {
    const mesh = typeMeshes[t];
    if (!mesh) continue;

    mesh.count = counts[t];
    mesh.instanceMatrix.needsUpdate = true;
  }
}

generateWorld();
rebuildInstances();

/*
  ------------------------------------------------
  プレイヤー
  ------------------------------------------------
*/
const PLAYER_HEIGHT = 1.7;
const EYE_HEIGHT = 1.62;
const PLAYER_RADIUS = 0.30;

const player = {
  x: W / 2 + 0.5,
  y: heightAt(Math.floor(W / 2), Math.floor(D / 2)) + 1,
  z: D / 2 + 0.5
};

const vel = new THREE.Vector3(0, 0, 0);
const keys = new Set();

let yaw = 0;
let pitch = 0;
let selected = GRASS;
let flight = false;
let grounded = true;

const tempForward = new THREE.Vector3();
const tempRight = new THREE.Vector3();
const tempMove = new THREE.Vector3();
const tempDir = new THREE.Vector3();

function collides(px, py, pz) {
  const minX = px - PLAYER_RADIUS;
  const maxX = px + PLAYER_RADIUS;
  const minY = py;
  const maxY = py + PLAYER_HEIGHT;
  const minZ = pz - PLAYER_RADIUS;
  const maxZ = pz + PLAYER_RADIUS;

  const startX = Math.floor(minX);
  const endX = Math.floor(maxX);
  const startY = Math.floor(minY);
  const endY = Math.floor(maxY);
  const startZ = Math.floor(minZ);
  const endZ = Math.floor(maxZ);

  for (let bx = startX; bx <= endX; bx++) {
    for (let by = startY; by <= endY; by++) {
      for (let bz = startZ; bz <= endZ; bz++) {
        const block = getBlock(bx, by, bz);
        if (!isSolid(block)) continue;

        if (
          maxX > bx &&
          minX < bx + 1 &&
          maxY > by &&
          minY < by + 1 &&
          maxZ > bz &&
          minZ < bz + 1
        ) {
          return true;
        }
      }
    }
  }

  return false;
}

function canPlaceBlockAt(bx, by, bz) {
  if (!collides(player.x, player.y, player.z)) {
    const minX = bx;
    const maxX = bx + 1;
    const minY = by;
    const maxY = by + 1;
    const minZ = bz;
    const maxZ = bz + 1;

    if (
      player.x + PLAYER_RADIUS > minX &&
      player.x - PLAYER_RADIUS < maxX &&
      player.y + PLAYER_HEIGHT > minY &&
      player.y < maxY &&
      player.z + PLAYER_RADIUS > minZ &&
      player.z - PLAYER_RADIUS < maxZ
    ) {
      return false;
    }
  }

  return true;
}

function moveAxis(axis, amount) {
  if (amount === 0) return;

  const old = player[axis];
  player[axis] += amount;

  if (collides(player.x, player.y, player.z)) {
    player[axis] = old;

    if (axis === "y") {
      vel.y = 0;
      if (amount < 0) grounded = true;
    } else {
      vel[axis] = 0;
    }
  } else {
    if (axis === "y" && amount < 0) {
      grounded = false;
    }
  }
}

function updatePlayer(dt) {
  camera.getWorldDirection(tempDir);

  tempForward.set(tempDir.x, 0, tempDir.z);
  if (tempForward.lengthSq() > 0.0001) tempForward.normalize();

  tempRight.set(-tempDir.z, 0, tempDir.x);
  if (tempRight.lengthSq() > 0.0001) tempRight.normalize();

  tempMove.set(0, 0, 0);

  if (keys.has("KeyW")) tempMove.add(tempForward);
  if (keys.has("KeyS")) tempMove.sub(tempForward);
  if (keys.has("KeyD")) tempMove.add(tempRight);
  if (keys.has("KeyA")) tempMove.sub(tempRight);

  const speed = flight ? 9 : 5.5;

  if (flight) {
    if (keys.has("Space")) tempMove.y += 1;
    if (keys.has("ShiftLeft") || keys.has("ShiftRight")) tempMove.y -= 1;

    if (tempMove.lengthSq() > 0.0001) tempMove.normalize();

    vel.x = tempMove.x * speed;
    vel.y = tempMove.y * speed;
    vel.z = tempMove.z * speed;

    grounded = false;
  } else {
    const gravity = 22;
    vel.y -= gravity * dt;

    if (grounded && keys.has("Space")) {
      vel.y = 8.2;
    }

    const horizontal = tempMove.lengthSq() > 0.0001 ? tempMove : new THREE.Vector3(0, 0, 0);
    if (horizontal.lengthSq() > 0.0001) horizontal.normalize();

    vel.x = horizontal.x * speed;
    vel.z = horizontal.z * speed;

    if (tempMove.lengthSq() <= 0.0001) {
      // 空入力でも重力だけ適用
    }
  }

  moveAxis("x", vel.x * dt);
  moveAxis("y", vel.y * dt);
  moveAxis("z", vel.z * dt);

  camera.position.set(player.x, player.y + EYE_HEIGHT, player.z);
}

/*
  ------------------------------------------------
  視点・ポインターロック
  ------------------------------------------------
*/
document.addEventListener("pointerlockchange", () => {
  const locked = document.pointerLockElement === renderer.domElement;
  renderer.domElement.style.outline = locked ? "0 solid #000" : "0 solid #000";
});

renderer.domElement.addEventListener("mousedown", (e) => {
  if (document.pointerLockElement !== renderer.domElement) {
    renderer.domElement.requestPointerLock();
    return;
  }

  if (e.button === 0) {
    const hit = raycast(64);
    if (hit) {
      setBlock(hit.x, hit.y, hit.z, AIR);
    }
  } else if (e.button === 2) {
    const hit = raycast(64);
    if (hit) {
      const nx = hit.x + hit.nx;
      const ny = hit.y + hit.ny;
      const nz = hit.z + hit.nz;

      if (getBlock(nx, ny, nz) === AIR && canPlaceBlockAt(nx, ny, nz)) {
        setBlock(nx, ny, nz, selected);
      }
    }
  }
});

renderer.domElement.addEventListener("contextmenu", e => e.preventDefault());

document.addEventListener("mousemove", (e) => {
  if (document.pointerLockElement !== renderer.domElement) return;

  const sens = 0.0022;
  yaw -= e.movementX * sens;
  pitch -= e.movementY * sens;
  pitch = Math.max(-1.45, Math.min(1.45, pitch));

  camera.rotation.set(pitch, yaw, 0, "YXZ");
});

document.addEventListener("keydown", (e) => {
  keys.add(e.code);

  if (e.code === "Space") e.preventDefault();

  if (e.code === "KeyF") {
    flight = !flight;
    grounded = false;
    vel.set(0, 0, 0);
  }

  if (e.key >= "1" && e.key <= "7") {
    selected = Number(e.key);
    updateHotbar();
  }
});

document.addEventListener("keyup", e => {
  keys.delete(e.code);
});

/*
  ------------------------------------------------
  レイキャスト（ボクセル DDA）
  ------------------------------------------------
*/
function raycast(maxDist = 64) {
  camera.getWorldDirection(tempDir);
  const dir = tempDir.clone().normalize();

  const ox = camera.position.x;
  const oy = camera.position.y;
  const oz = camera.position.z;

  let cx = Math.floor(ox);
  let cy = Math.floor(oy);
  let cz = Math.floor(oz);

  if (getBlock(cx, cy, cz) !== AIR) {
    return { x: cx, y: cy, z: cz, nx: -dir.x, ny: -dir.y, nz: -dir.z };
  }

  const stepX = dir.x > 0 ? 1 : dir.x < 0 ? -1 : 0;
  const stepY = dir.y > 0 ? 1 : dir.y < 0 ? -1 : 0;
  const stepZ = dir.z > 0 ? 1 : dir.z < 0 ? -1 : 0;

  const dtX = Math.abs(dir.x) > 0.0001 ? 1 / Math.abs(dir.x) : Infinity;
  const dtY = Math.abs(dir.y) > 0.0001 ? 1 / Math.abs(dir.y) : Infinity;
  const dtZ = Math.abs(dir.z) > 0.0001 ? 1 / Math.abs(dir.z) : Infinity;

  let tMaxX = dtX * ((stepX > 0 ? cx + 1 - ox : ox - cx) / Math.max(Math.abs(dir.x), 0.0001));
  let tMaxY = dtY * ((stepY > 0 ? cy + 1 - oy : oy - cy) / Math.max(Math.abs(dir.y), 0.0001));
  let tMaxZ = dtZ * ((stepZ > 0 ? cz + 1 - oz : oz - cz) / Math.max(Math.abs(dir.z), 0.0001));

  let nx = 0;
  let ny = 0;
  let nz = 0;

  for (let i = 0; i < 500; i++) {
    const minT = Math.min(tMaxX, tMaxY, tMaxZ);
    if (minT > maxDist) break;

    if (minT === tMaxX) {
      cx += stepX;
      nx = -stepX;
      tMaxX += dtX;
    } else if (minT === tMaxY) {
      cy += stepY;
      ny = -stepY;
      tMaxY += dtY;
    } else {
      cz += stepZ;
      nz = -stepZ;
      tMaxZ += dtZ;
    }

    if (cx < 0 || cx >= W || cy < 0 || cy >= H || cz < 0 || cz >= D) continue;

    const block = getBlock(cx, cy, cz);
    if (block !== AIR) {
      return { x: cx, y: cy, z: cz, nx, ny, nz };
    }
  }

  return null;
}

/*
  ------------------------------------------------
  選択ブロックハイライト
  ------------------------------------------------
*/
const highlight = new THREE.LineSegments(
  new THREE.EdgesGeometry(new THREE.BoxGeometry(1, 1, 1)),
  new THREE.LineBasicMaterial({ color: 0xffffff })
);
highlight.visible = false;
scene.add(highlight);

function updateHighlight() {
  const hit = raycast(64);

  if (!hit) {
    highlight.visible = false;
    return;
  }

  highlight.visible = true;
  highlight.position.set(hit.x + 0.5, hit.y + 0.5, hit.z + 0.5);
}

/*
  ------------------------------------------------
  ホットバー
  ------------------------------------------------
*/
const hotbar = document.getElementById("hotbar");

function hexToCss(hex) {
  return "#" + hex.toString(16).padStart(6, "0");
}

function updateHotbar() {
  hotbar.innerHTML = "";

  for (let t = 1; t <= 7; t++) {
    const slot = document.createElement("div");
    slot.className = "slot" + (selected === t ? " selected" : "");
    slot.textContent = t;

    const swatch = document.createElement("div");
    swatch.className = "swatch";
    swatch.style.background = hexToCss(typeConfigs[t].top);
    slot.appendChild(swatch);

    hotbar.appendChild(slot);
  }
}

updateHotbar();

/*
  ------------------------------------------------
  アニメーション
  ------------------------------------------------
*/
const clock = new THREE.Clock();

function animate() {
  const dt = Math.min(0.05, clock.getDelta());

  updatePlayer(dt);
  updateHighlight();

  renderer.render(scene, camera);
}

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
</script>
</body>
</html>
```

補足：これは「箱庭」として使うのに適した単一のブラウザゲームです。ブロック設置・破壊、第一人称視点、地形生成、ホットバーまで含めています。さらに「セーブ／ロード、クラフト、水、夜/昼、ブロック音、チャンク生成」も拡張できます。