以下、ブラウザで開くだけで遊べる「マイクラ風3D箱庭ゲーム」です。  
保存してそのまま開くと、WASD視点、左クリックで破壊、右クリックで設置ができます。

```html
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>マイクラ風3D箱庭</title>
<style>
html,body{margin:0;height:100%;overflow:hidden;background:#111;font-family:system-ui,sans-serif;color:#fff}
canvas{display:block;width:100%;height:100%;cursor:crosshair}
#overlay{
position:fixed;left:12px;top:12px;background:rgba(0,0,0,.45);padding:12px 16px;border-radius:8px;
max-width:380px;line-height:1.45;font-size:14px;z-index:10
}
#target{position:fixed;right:12px;top:12px;background:rgba(0,0,0,.45);padding:8px 12px;border-radius:8px;font-size:14px}
#fps{position:fixed;right:12px;top:50px;background:rgba(0,0,0,.45);padding:8px 12px;border-radius:8px;font-size:14px}
#hotbar{
position:fixed;left:50%;bottom:18px;transform:translateX(-50%);display:flex;gap:8px;background:rgba(0,0,0,.45);padding:8px;border-radius:10px
}
.slot{width:44px;height:44px;border:2px solid #555;border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:12px}
.slot.on{border-color:#fff;background:rgba(255,255,255,.12)}
</style>
</head>
<body>
<div id="overlay">
クリックで視点をロック。<br>
WASD:移動<br>
Space:ジャンプ<br>
左クリック:ブロックを破壊<br>
右クリック:ブロックを設置<br>
数字キー1〜6:ブロック選択<br>
G:飛行モード切替<br>
R:リスポーン
</div>
<div id="target">Target: -</div>
<div id="fps">FPS: -</div>
<div id="hotbar"></div>
<canvas id="game"></canvas>

<script type="module">
import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js";

const W = 64, D = 64, H = 32;
const SIZE = W * D * H;

const BLOCKS = [
  { id:0, name:"Air", color:0x222222 },
  { id:1, name:"Grass", color:0x4e9344 },
  { id:2, name:"Dirt", color:0x6d4f35 },
  { id:3, name:"Stone", color:0x8c8c8c },
  { id:4, name:"Sand", color:0xd5bd6d },
  { id:5, name:"Wood", color:0x6f4d38 },
  { id:6, name:"Leaves", color:0x357844 },
];

const colors = BLOCKS.map(b => new THREE.Color(b.color));
const inventory = [1,2,3,4,5,6];

const grid = new Uint8Array(SIZE);
const blockToSlot = new Int32Array(SIZE).fill(-1);
const slotToBlock = new Int32Array(SIZE).fill(-1);
let visibleCount = 0;

function encode(x,z,y) {
  return (x * D + z) * H + y;
}

function decode(idx) {
  const x = Math.floor(idx / (D * H));
  const rem = idx % (D * H);
  const z = Math.floor(rem / H);
  const y = rem % H;
  return [x,z,y];
}

function getB(x,z,y) {
  if (x < 0 || z < 0 || y < 0 || x >= W || z >= D || y >= H) return 0;
  return grid[encode(x,z,y)];
}

function isSolidAt(x,z,y) {
  return getB(x,z,y) > 0;
}

function hash(x,z) {
  let v = (x * 73856093) ^ (z * 19349189);
  v ^= v << 13;
  v ^= v >>> 7;
  v ^= v << 17;
  return ((v >>> 16) % 10000) / 10000;
}

function terrainHeight(x,z) {
  const v =
    8 +
    Math.floor(
      Math.sin(x * 0.17 + 0.3) * 4 +
      Math.sin(z * 0.19 + 0.2) * 4 +
      Math.sin((x + z) * 0.06) * 3 +
      Math.sin((x - z) * 0.12) * 3
    );
  return Math.max(1, Math.min(H - 4, v));
}

function setBlockDirect(x,z,y,id) {
  if (x < 0 || z < 0 || y < 0 || x >= W || z >= D || y >= H) return;
  grid[encode(x,z,y)] = id;
}

// 世界生成
for (let x = 0; x < W; x++) {
  for (let z = 0; z < D; z++) {
    const h = terrainHeight(x,z);
    for (let y = 0; y <= h; y++) {
      let id = 0;
      if (y < h - 3) id = 3;
      else if (y < h) id = 2;
      else id = 1;
      grid[encode(x,z,y)] = id;
    }
  }
}

// 木
for (let x = 1; x < W - 1; x++) {
  for (let z = 1; z < D - 1; z++) {
    const h = terrainHeight(x,z);
    if (grid[encode(x,z,h)] !== 1) continue;
    if (hash(x,z) > 0.045) continue;

    const trunkH = 3 + Math.floor(hash(x + 1, z + 2) * 3);
    for (let y = h; y <= h + trunkH && y < H; y++) {
      grid[encode(x,z,y)] = 5;
    }

    for (let dx = -2; dx <= 2; dx++) {
      for (let dz = -2; dz <= 2; dz++) {
        for (let dy = h + trunkH - 1; dy <= h + trunkH + 1; dy++) {
          const xx = x + dx, zz = z + dz, yy = dy;
          if (xx < 0 || zz < 0 || yy < 0 || xx >= W || zz >= D || yy >= H) continue;
          if (Math.abs(dx) == 0 && Math.abs(dz) == 0 && yy < h + trunkH) continue;
          grid[encode(xx,zz,yy)] = 6;
        }
      }
    }
  }
}

// レンダラ
const canvas = document.getElementById("game");
const renderer = new THREE.WebGLRenderer({ canvas, antialias:true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x79c3ec);
scene.fog = new THREE.Fog(0x79c3ec, 60, 200);

const camera = new THREE.PerspectiveCamera(75, innerWidth / innerHeight, 0.1, 300);

const material = new THREE.MeshLambertMaterial();
const mesh = new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1), material, SIZE);
mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
mesh.instanceColor = new THREE.InstancedBufferAttribute(new Float32Array(SIZE * 3), 3);
mesh.instanceColor.setUsage(THREE.DynamicDrawUsage);
scene.add(mesh);

const hemi = new THREE.HemisphereLight(0xffffff, 0x444444, 0.85);
scene.add(hemi);

const dirLight = new THREE.DirectionalLight(0xffffff, 1.15);
dirLight.position.set(40, 80, 20);
scene.add(dirLight);

const highlight = new THREE.LineSegments(
  new THREE.EdgesGeometry(new THREE.BoxGeometry(1.01,1.01,1.01)),
  new THREE.LineBasicMaterial({ color: 0xffffff })
);
highlight.visible = false;
scene.add(highlight);

const dummy = new THREE.Matrix4();

function setSlotFromBlock(slot, blockIdx) {
  const [x,z,y] = decode(blockIdx);
  dummy.identity();
  dummy.setPosition(x + 0.5, y + 0.5, z + 0.5);
  mesh.setMatrixAt(slot, dummy);
  mesh.setColorAt(slot, colors[grid[blockIdx]]);
}

function hasAirNeighbor(idx) {
  const [x,z,y] = decode(idx);
  const dirs = [
    [1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]
  ];
  for (const [dx,dy,dz] of dirs) {
    if (getB(x+dx, z+dz, y+dy) === 0) return true;
  }
  return false;
}

function addVisible(idx) {
  if (grid[idx] === 0) return;
  if (blockToSlot[idx] !== -1) return;

  const slot = visibleCount;
  blockToSlot[idx] = slot;
  slotToBlock[slot] = idx;
  setSlotFromBlock(slot, idx);
  visibleCount++;
}

function removeVisible(idx) {
  const slot = blockToSlot[idx];
  if (slot === -1) return;

  const last = visibleCount - 1;
  if (slot !== last) {
    const lastIdx = slotToBlock[last];
    slotToBlock[slot] = lastIdx;
    blockToSlot[lastIdx] = slot;
    setSlotFromBlock(slot, lastIdx);
  }

  blockToSlot[idx] = -1;
  visibleCount--;
}

function setVisibility(idx, show) {
  const [x,z,y] = decode(idx);
  if (!isSolidAt(x,z,y)) {
    removeVisible(idx);
    return;
  }
  if (show) addVisible(idx);
  else removeVisible(idx);
}

function refreshVisibilityAround(idx) {
  setVisibility(idx, hasAirNeighbor(idx));
  const [x,z,y] = decode(idx);
  const dirs = [
    [1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]
  ];
  for (const [dx,dy,dz] of dirs) {
    const nx = x + dx, nz = z + dz, ny = y + dy;
    if (nx < 0 || nz < 0 || ny < 0 || nx >= W || nz >= D || ny >= H) continue;
    setVisibility(encode(nx,nz,ny), hasAirNeighbor(encode(nx,nz,ny)));
  }
}

// 初期可见面
for (let idx = 0; idx < SIZE; idx++) {
  if (grid[idx] > 0 && hasAirNeighbor(idx)) {
    addVisible(idx);
  }
}

mesh.instanceColor.needsUpdate = true;
mesh.instanceMatrix.needsUpdate = true;

// プレイヤー
const PW = 0.4;
const PH = 1.8;
const EYE = 1.6;
const EPS = 0.001;

const pos = new THREE.Vector3(W/2, 0, D/2);
pos.y = terrainHeight(Math.floor(pos.x), Math.floor(pos.z)) + 1.0;

let vy = 0;
let grounded = true;
let fly = false;

function collides(px,py,pz) {
  const minx = Math.floor(px - PW + EPS);
  const maxx = Math.floor(px + PW - EPS);
  const minz = Math.floor(pz - PW + EPS);
  const maxz = Math.floor(pz + PW - EPS);
  const miny = Math.floor(py + EPS);
  const maxy = Math.floor(py + PH - EPS);

  for (let x = minx; x <= maxx; x++) {
    for (let z = minz; z <= maxz; z++) {
      for (let y = miny; y <= maxy; y++) {
        if (isSolidAt(x,z,y)) return true;
      }
    }
  }
  return false;
}

function respawn() {
  pos.x = W/2;
  pos.z = D/2;
  pos.y = terrainHeight(Math.floor(pos.x), Math.floor(pos.z)) + 1.0;
  vy = 0;
  grounded = collides(pos.x, pos.y - 0.01, pos.z);
}

// 視点数値
let pitch = 0;
let yaw = 0;
let pointerLocked = false;

const keys = {};

document.addEventListener("keydown", e => {
  const k = e.key.toLowerCase();
  keys[k] = true;

  if (["w","a","s","d","space"].includes(k)) e.preventDefault();

  if (k === "g") fly = !fly;
  if (k === "r") respawn();

  if (/^[1-6]$/.test(k)) {
    selected = parseInt(k, 10) - 1;
    updateHotbar();
  }
});

document.addEventListener("keyup", e => {
  const k = e.key.toLowerCase();
  keys[k] = false;
});

document.addEventListener("mousemove", e => {
  if (!pointerLocked) return;

  yaw -= e.movementX * 0.0025;
  pitch -= e.movementY * 0.0025;

  pitch = Math.max(-1.5, Math.min(1.5, pitch));
  yaw = ((yaw + Math.PI * 2) % (Math.PI * 2));
});

canvas.addEventListener("click", () => {
  if (!pointerLocked) canvas.requestPointerLock();
});

canvas.addEventListener("contextmenu", e => e.preventDefault());

document.addEventListener("pointerlockchange", () => {
  pointerLocked = document.pointerLockElement === canvas;
  document.getElementById("overlay").style.display = pointerLocked ? "block" : "block";
});

let selected = 0;
const hotbar = document.getElementById("hotbar");

function updateHotbar() {
  hotbar.innerHTML = "";
  for (let i = 0; i < inventory.length; i++) {
    const block = BLOCKS[inventory[i]];
    const div = document.createElement("div");
    div.className = "slot" + (i === selected ? " on" : "");
    div.style.background = "#" + block.color.toString(16).padStart(6, "0");
    div.textContent = i + 1;
    hotbar.appendChild(div);
  }
}
updateHotbar();

function raycast(origin, dir, maxDist) {
  const ix = Math.floor(origin.x);
  const iy = Math.floor(origin.y);
  const iz = Math.floor(origin.z);

  if (isSolidAt(ix, iz, iy)) {
    return { idx: encode(ix, iz, iy), normal: null };
  }

  const dx = dir.x, dy = dir.y, dz = dir.z;

  const stepX = dx === 0 ? 0 : (dx > 0 ? 1 : -1);
  const stepY = dy === 0 ? 0 : (dy > 0 ? 1 : -1);
  const stepZ = dz === 0 ? 0 : (dz > 0 ? 1 : -1);

  const tMaxX = dx === 0 ? Infinity : Math.abs((stepX > 0 ? ix + 1 - origin.x : origin.x - ix) / dx);
  const tMaxY = dy === 0 ? Infinity : Math.abs((stepY > 0 ? iy + 1 - origin.y : origin.y - iy) / dy);
  const tMaxZ = dz === 0 ? Infinity : Math.abs((stepZ > 0 ? iz + 1 - origin.z : origin.z - iz) / dz);

  const tDeltaX = dx === 0 ? Infinity : 1 / Math.abs(dx);
  const tDeltaY = dy === 0 ? Infinity : 1 / Math.abs(dy);
  const tDeltaZ = dz === 0 ? Infinity : 1 / Math.abs(dz);

  let lastAxis = -1;

  for (let i = 0; i < 2000; i++) {
    if (isSolidAt(ix, iz, iy)) {
      const normal = [0,0,0];
      if (lastAxis === 0) normal[0] = -stepX;
      else if (lastAxis === 1) normal[1] = -stepY;
      else if (lastAxis === 2) normal[2] = -stepZ;
      return { idx: encode(ix, iz, iy), normal };
    }

    const t = Math.min(tMaxX, tMaxY, tMaxZ);
    if (t > maxDist) break;

    if (tMaxX < tMaxY && tMaxX < tMaxZ) {
      tMaxX += tDeltaX;
      ix += stepX;
      lastAxis = 0;
    } else if (tMaxY < tMaxZ) {
      tMaxY += tDeltaY;
      iy += stepY;
      lastAxis = 1;
    } else {
      tMaxZ += tDeltaZ;
      iz += stepZ;
      lastAxis = 2;
    }

    if (ix < 0 || iz < 0 || iy < 0 || ix >= W || iz >= D || iy >= H) break;
  }

  return null;
}

function setBlockAt(x,z,y,id) {
  if (x < 0 || z < 0 || y < 0 || x >= W || z >= D || y >= H) return;
  const idx = encode(x,z,y);
  if (grid[idx] === id) return;

  grid[idx] = id;
  refreshVisibilityAround(idx);

  mesh.instanceMatrix.needsUpdate = true;
  mesh.instanceColor.needsUpdate = true;
}

function playerOverlapsBlock(x,y,z) {
  return (
    pos.x - PW < x + 1 - EPS &&
    pos.x + PW > x + EPS &&
    pos.y < y + 1 - EPS &&
    pos.y + PH > y + EPS &&
    pos.z - PW < z + 1 - EPS &&
    pos.z + PW > z + EPS
  );
}

function mine() {
  const origin = camera.position.clone();
  const dir = new THREE.Vector3();
  camera.getWorldDirection(dir);

  const hit = raycast(origin, dir, 8);
  if (!hit) return;

  const [x,z,y] = decode(hit.idx);
  setBlockAt(x,z,y,0);
}

function place() {
  const origin = camera.position.clone();
  const dir = new THREE.Vector3();
  camera.getWorldDirection(dir);

  const hit = raycast(origin, dir, 8);
  if (!hit || !hit.normal) return;

  const [x,z,y] = decode(hit.idx);
  const nx = x + hit.normal[0];
  const nz = z + hit.normal[2];
  const ny = y + hit.normal[1];

  if (getB(nx,nz,ny) !== 0) return;
  if (playerOverlapsBlock(nx,ny,nz)) return;

  setBlockAt(nx,nz,ny,inventory[selected]);
}

canvas.addEventListener("mousedown", e => {
  if (!pointerLocked) return;
  if (e.button === 0) mine();
  if (e.button === 2) place();
});

// HUD
const targetText = document.getElementById("target");
const fpsText = document.getElementById("fps");

let frame = 0;
let lastFpsTime = performance.now();

function updateHUD(hit) {
  if (hit) {
    const [x,z,y] = decode(hit.idx);
    targetText.textContent = `Target: ${BLOCKS[grid[hit.idx]].name} @ ${x},${y},${z}`;

    highlight.position.set(x + 0.5, y + 0.5, z + 0.5);
    highlight.visible = true;
  } else {
    targetText.textContent = "Target: なし";
    highlight.visible = false;
  }
}

// メインループ
const cameraQuat = new THREE.Quaternion();

function update(dt) {
  cameraQuat.setFromEuler(new THREE.Euler(pitch, yaw, 0, "YXZ"));
  camera.quaternion.copy(cameraQuat);

  const forward = new THREE.Vector3(0,0,-1).applyQuaternion(cameraQuat);
  forward.y = 0;
  forward.normalize();

  const right = new THREE.Vector3(1,0,0).applyQuaternion(cameraQuat);
  right.y = 0;
  right.normalize();

  const speed = fly ? 12 : 5;
  const move = new THREE.Vector3();

  if (keys["w"]) move.add(forward);
  if (keys["s"]) move.sub(forward);
  if (keys["d"]) move.add(right);
  if (keys["a"]) move.sub(right);

  if (move.lengthSq() > 0) move.normalize().multiplyScalar(speed);

  const vx = move.x * dt;
  const vz = move.z * dt;

  // 横方向
  const nx = pos.x + vx;
  const nz = pos.z + vz;

  if (collides(nx, pos.y, nz)) {
    if (!collides(nx, pos.y, pos.z)) pos.x = nx;
    else if (!collides(pos.x, pos.y, nz)) pos.z = nz;
  } else {
    pos.x = nx;
    pos.z = nz;
  }

  // 縦方向
  if (!fly) {
    vy -= 22 * dt;

    if (keys["space"] && grounded) {
      vy = 8;
      grounded = false;
    }

    const ny = pos.y + vy * dt;

    if (collides(pos.x, ny, pos.z)) {
      if (vy < 0) {
        pos.y = pos.y;
        vy = 0;
        grounded = collides(pos.x, pos.y - 0.01, pos.z);
      } else {
        vy = 0;
      }
    } else {
      pos.y = ny;
      grounded = collides(pos.x, pos.y - 0.01, pos.z);
    }
  } else {
    if (keys["space"]) pos.y += 8 * dt;
    if (keys["shift"]) pos.y -= 8 * dt;
    vy = 0;
    grounded = true;
  }

  camera.position.set(pos.x, pos.y + EYE, pos.z);
}

let lastTime = performance.now();

function animate() {
  requestAnimationFrame(animate);

  const now = performance.now();
  const dt = Math.min((now - lastTime) / 1000, 0.05);
  lastTime = now;

  update(dt);

  const dir = new THREE.Vector3();
  camera.getWorldDirection(dir);

  const hit = raycast(camera.position, dir, 8);
  updateHUD(hit);

  renderer.render(scene, camera);

  frame++;
  if (frame % 20 === 0) {
    const fps = Math.round((frame * 1000) / (now - lastFpsTime));
    fpsText.textContent = `FPS: ${fps}`;
    lastFpsTime = now;
    frame = 0;
  }
}

window.addEventListener("resize", () => {
  renderer.setSize(innerWidth, innerHeight);
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
});

grounded = collides(pos.x, pos.y - 0.01, pos.z);
animate();
</script>
</body>
</html>
```