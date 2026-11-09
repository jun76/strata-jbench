マイクラ風 3D 箱庭ゲームを 1 個の HTML ファイルで作成します。以下を `.html` として保存し、ブラウザで開けばそのまま起動します。

```html
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>マイクラ風 3D 箱庭ゲーム</title>
<style>
  body { margin: 0; overflow: hidden; }
  #hud {
    position: fixed;
    top: 10px;
    left: 10px;
    color: #fff;
    font-family: monospace;
    background: rgba(0,0,0,0.55);
    padding: 10px;
    border-radius: 8px;
    z-index: 10;
  }
  #hud small { opacity: 0.8; }
  canvas { display: block; }
</style>
</head>
<body>

<div id="hud">
  <div>マイクラ風 3D 箱庭ゲーム</div>
  <small>
    画面左クリック: 視点ロック<br>
    WASD: 移動<br>
    Space:  jump<br>
    Shift:  sprint<br>
    mouse:  look<br>
    Q: block remove<br>
    E: block place<br>
    Left click: remove<br>
    Right click: place
  </small>
</div>

<script src="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js"></script>
<script>
/* =========================
   World size
   ========================= */
const W = 64;
const H = 32;
const D = 64;

const BLOCK_AIR = 0;
const BLOCK_GRASS = 1;
const BLOCK_DIRT = 2;
const BLOCK_STONE = 3;
const BLOCK_SAND = 4;
const BLOCK_WOOD = 5;
const BLOCK_LEAVES = 6;

const world = new Uint8Array(W * H * D);

function index(x, y, z) {
  return x + W * (y + H * z);
}

function inBounds(x, y, z) {
  return x >= 0 && x < W && y >= 0 && y < H && z >= 0 && z < D;
}

function getBlock(x, y, z) {
  if (!inBounds(x, y, z)) return 0;
  return world[index(x, y, z)];
}

function setBlockRaw(x, y, z, type) {
  if (!inBounds(x, y, z)) return;
  world[index(x, y, z)] = type;
}

/* =========================
   Terrain generation
   ========================= */
function noise(x, z) {
  return (
    Math.sin(x * 0.23) +
    Math.cos(z * 0.21) +
    Math.sin((x + z) * 0.11) +
    Math.sin((x - z) * 0.14)
  );
}

const topY = new Int16Array(W * D);

for (let x = 0; x < W; x++) {
  for (let z = 0; z < D; z++) {
    const n = noise(x, z);
    let h = Math.floor(10 + n * 2.5);
    h = Math.max(3, Math.min(H - 3, h));

    for (let y = 0; y <= h; y++) {
      let type;

      if (y === h) {
        type = h <= 4 ? BLOCK_SAND : BLOCK_GRASS;
      } else if (y >= h - 3) {
        type = BLOCK_DIRT;
      } else {
        type = BLOCK_STONE;
      }

      setBlockRaw(x, y, z, type);
    }

    topY[x * D + z] = h;
  }
}

/* =========================
   Trees
   ========================= */
for (let x = 1; x < W - 1; x++) {
  for (let z = 1; z < D - 1; z++) {
    const h = topY[x * D + z];

    if (getBlock(x, h, z) !== BLOCK_GRASS) continue;
    if (h + 5 >= H) continue;

    if (Math.random() < 0.018) {
      // Trunk
      for (let y = h + 1; y <= h + 4; y++) {
        setBlockRaw(x, y, z, BLOCK_WOOD);
      }

      // Leaves
      for (let ly = h + 4; ly <= h + 5; ly++) {
        const radius = ly === h + 5 ? 1 : 2;

        for (let dx = -radius; dx <= radius; dx++) {
          for (let dz = -radius; dz <= radius; dz++) {
            if (dx === 0 && dz === 0) continue;
            if (inBounds(x + dx, ly, z + dz) && getBlock(x + dx, ly, z + dz) === BLOCK_AIR) {
              setBlockRaw(x + dx, ly, z + dz, BLOCK_LEAVES);
            }
          }
        }
      }

      // A small leaf cap above the trunk
      setBlockRaw(x, h + 6, z, BLOCK_LEAVES);
    }
  }
}

/* =========================
   Three.js scene
   ========================= */
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setClearColor(0x87ceeb);
document.body.appendChild(renderer.domElement);

const canvas = renderer.domElement;
const scene = new THREE.Scene();

const camera = new THREE.PerspectiveCamera(
  70,
  window.innerWidth / window.innerHeight,
  0.1,
  200
);

const light = new THREE.DirectionalLight(0xffffff, 1.1);
light.position.set(40, 100, 40);
scene.add(light);

scene.add(new THREE.AmbientLight(0xffffff, 0.35));

const boxGeometry = new THREE.BoxGeometry(1, 1, 1);

const materials = {
  [BLOCK_GRASS]: new THREE.MeshLambertMaterial({ color: 0x79c17a }),
  [BLOCK_DIRT]: new THREE.MeshLambertMaterial({ color: 0x8c5a3d }),
  [BLOCK_STONE]: new THREE.MeshLambertMaterial({ color: 0x7d8286 }),
  [BLOCK_SAND]: new THREE.MeshLambertMaterial({ color: 0xd8c79b }),
  [BLOCK_WOOD]: new THREE.MeshLambertMaterial({ color: 0x7b5a3a }),
  [BLOCK_LEAVES]: new THREE.MeshLambertMaterial({ color: 0x5c9b63 })
};

let instancedMeshes = [];

function rebuildMeshes() {
  for (const mesh of instancedMeshes) {
    scene.remove(mesh);
  }

  instancedMeshes = [];

  for (let type = 1; type <= BLOCK_LEAVES; type++) {
    let count = 0;

    for (let y = 0; y < H; y++) {
      for (let z = 0; z < D; z++) {
        for (let x = 0; x < W; x++) {
          if (world[index(x, y, z)] === type) count++;
        }
      }
    }

    if (count === 0) continue;

    const mesh = new THREE.InstancedMesh(boxGeometry, materials[type], count);
    const matrix = new THREE.Matrix4();

    let n = 0;

    for (let y = 0; y < H; y++) {
      for (let z = 0; z < D; z++) {
        for (let x = 0; x < W; x++) {
          if (world[index(x, y, z)] === type) {
            matrix.makeTranslation(x + 0.5, y + 0.5, z + 0.5);
            mesh.setMatrixAt(n++, matrix);
          }
        }
      }
    }

    mesh.instanceMatrix.needsUpdate = true;
    scene.add(mesh);
    instancedMeshes.push(mesh);
  }
}

rebuildMeshes();

/* =========================
   Player
   ========================= */
const playerHalfWidth = 0.35;
const playerHalfHeight = 0.9;

function findSpawnY(x, z) {
  for (let y = H - 1; y >= 0; y--) {
    if (getBlock(x, y, z) !== BLOCK_AIR) return y;
  }
  return 0;
}

const spawnX = W / 2;
const spawnZ = D / 2;
const spawnTop = findSpawnY(spawnX, spawnZ);

let pos = new THREE.Vector3(
  spawnX + 0.5,
  spawnTop + 1.9,
  spawnZ + 0.5
);

let vel = new THREE.Vector3(0, 0, 0);
let yaw = 0;
let pitch = 0;
let grounded = false;

const keys = {};

document.addEventListener("keydown", (e) => {
  keys[e.code] = true;

  if (e.code === "Space") e.preventDefault();

  if (e.code === "KeyQ") {
    removeBlockAtView();
  }

  if (e.code === "KeyE") {
    placeBlockAtView();
  }
});

document.addEventListener("keyup", (e) => {
  keys[e.code] = false;
});

canvas.addEventListener("click", () => {
  if (document.pointerLockElement !== canvas) {
    canvas.requestPointerLock();
  }
});

window.addEventListener("contextmenu", (e) => {
  e.preventDefault();
});

canvas.addEventListener("mousedown", (e) => {
  if (document.pointerLockElement === canvas) {
    if (e.button === 0) {
      removeBlockAtView();
    } else if (e.button === 2) {
      placeBlockAtView();
    }
  }
});

document.addEventListener("mousemove", (e) => {
  if (document.pointerLockElement === canvas) {
    yaw += e.movementX * 0.0025;
    pitch -= e.movementY * 0.0025;

    pitch = Math.max(-Math.PI / 2 + 0.05, Math.min(Math.PI / 2 - 0.05, pitch));
  }
});

/* =========================
   Collision
   ========================= */
function collides(px, py, pz) {
  const eps = 0.001;

  const minX = Math.floor(px - playerHalfWidth + eps);
  const maxX = Math.floor(px + playerHalfWidth - eps);
  const minY = Math.floor(py - playerHalfHeight + eps);
  const maxY = Math.floor(py + playerHalfHeight - eps);
  const minZ = Math.floor(pz - playerHalfWidth + eps);
  const maxZ = Math.floor(pz + playerHalfWidth - eps);

  for (let x = Math.max(0, minX); x <= Math.min(W - 1, maxX); x++) {
    for (let y = Math.max(0, minY); y <= Math.min(H - 1, maxY); y++) {
      for (let z = Math.max(0, minZ); z <= Math.min(D - 1, maxZ); z++) {
        if (getBlock(x, y, z) !== BLOCK_AIR) {
          return true;
        }
      }
    }
  }

  return false;
}

function blockTouchesPlayer(x, y, z) {
  const eps = 0.01;

  const minX = pos.x - playerHalfWidth;
  const maxX = pos.x + playerHalfWidth;
  const minY = pos.y - playerHalfHeight;
  const maxY = pos.y + playerHalfHeight;
  const minZ = pos.z - playerHalfWidth;
  const maxZ = pos.z + playerHalfWidth;

  return (
    x < maxX - eps &&
    x + 1 > minX + eps &&
    y < maxY - eps &&
    y + 1 > minY + eps &&
    z < maxZ - eps &&
    z + 1 > minZ + eps
  );
}

/* =========================
   View direction
   ========================= */
function getViewForward() {
  return new THREE.Vector3(
    -Math.sin(yaw) * Math.cos(pitch),
    Math.sin(pitch),
    -Math.cos(yaw) * Math.cos(pitch)
  ).normalize();
}

/* =========================
   Voxel raycast
   ========================= */
function raycastVoxel(origin, direction, maxDist = 6) {
  const ox = origin.x;
  const oy = origin.y;
  const oz = origin.z;

  const eps = 1e-6;

  let x = Math.floor(ox + (direction.x > 0 ? eps : direction.x < 0 ? -eps : 0));
  let y = Math.floor(oy + (direction.y > 0 ? eps : direction.y < 0 ? -eps : 0));
  let z = Math.floor(oz + (direction.z > 0 ? eps : direction.z < 0 ? -eps : 0));

  let nx = 0;
  let ny = 0;
  let nz = 0;

  const stepX = direction.x > 0 ? 1 : direction.x < 0 ? -1 : 0;
  const stepY = direction.y > 0 ? 1 : direction.y < 0 ? -1 : 0;
  const stepZ = direction.z > 0 ? 1 : direction.z < 0 ? -1 : 0;

  let tMaxX = direction.x === 0
    ? Infinity
    : (stepX > 0 ? (x + 1 - ox) / direction.x : (x - ox) / direction.x);

  let tMaxY = direction.y === 0
    ? Infinity
    : (stepY > 0 ? (y + 1 - oy) / direction.y : (y - oy) / direction.y);

  let tMaxZ = direction.z === 0
    ? Infinity
    : (stepZ > 0 ? (z + 1 - oz) / direction.z : (z - oz) / direction.z);

  if (!inBounds(x, y, z)) return null;

  if (getBlock(x, y, z) !== BLOCK_AIR) {
    return { x, y, z, nx, ny, nz };
  }

  while (true) {
    let advanced = false;

    if (tMaxX < tMaxY && tMaxX < tMaxZ) {
      if (tMaxX > maxDist) break;

      x += stepX;
      nx = -stepX;
      ny = 0;
      nz = 0;

      if (stepX !== 0) tMaxX += Math.abs(1 / direction.x);
      advanced = true;
    } else if (tMaxY < tMaxZ) {
      if (tMaxY > maxDist) break;

      y += stepY;
      nx = 0;
      ny = -stepY;
      nz = 0;

      if (stepY !== 0) tMaxY += Math.abs(1 / direction.y);
      advanced = true;
    } else {
      if (tMaxZ > maxDist) break;

      z += stepZ;
      nx = 0;
      ny = 0;
      nz = -stepZ;

      if (stepZ !== 0) tMaxZ += Math.abs(1 / direction.z);
      advanced = true;
    }

    if (!advanced) break;

    if (!inBounds(x, y, z)) break;

    if (getBlock(x, y, z) !== BLOCK_AIR) {
      return { x, y, z, nx, ny, nz };
    }
  }

  return null;
}

/* =========================
   Block interaction
   ========================= */
function removeBlockAtView() {
  const origin = camera.position.clone();
  const direction = getViewForward();

  const hit = raycastVoxel(origin, direction, 6);

  if (hit) {
    setBlockRaw(hit.x, hit.y, hit.z, BLOCK_AIR);
    rebuildMeshes();
  }
}

function placeBlockAtView() {
  const origin = camera.position.clone();
  const direction = getViewForward();

  const hit = raycastVoxel(origin, direction, 6);

  if (!hit) return;

  if (hit.nx === 0 && hit.ny === 0 && hit.nz === 0) return;

  const bx = hit.x + hit.nx;
  const by = hit.y + hit.ny;
  const bz = hit.z + hit.nz;

  if (!inBounds(bx, by, bz)) return;
  if (getBlock(bx, by, bz) !== BLOCK_AIR) return;
  if (blockTouchesPlayer(bx, by, bz)) return;

  setBlockRaw(bx, by, bz, BLOCK_STONE);
  rebuildMeshes();
}

/* =========================
   Update loop
   ========================= */
const clock = new THREE.Clock();

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

function update() {
  const dt = Math.min(clock.getDelta(), 0.05);

  const forwardX = -Math.sin(yaw);
  const forwardZ = -Math.cos(yaw);

  const rightX = Math.cos(yaw);
  const rightZ = -Math.sin(yaw);

  let moveX = 0;
  let moveZ = 0;

  if (keys["KeyW"]) {
    moveX += forwardX;
    moveZ += forwardZ;
  }

  if (keys["KeyS"]) {
    moveX -= forwardX;
    moveZ -= forwardZ;
  }

  if (keys["KeyD"]) {
    moveX += rightX;
    moveZ += rightZ;
  }

  if (keys["KeyA"]) {
    moveX -= rightX;
    moveZ -= rightZ;
  }

  const moveLen = Math.hypot(moveX, moveZ);
  if (moveLen > 0) {
    moveX /= moveLen;
    moveZ /= moveLen;
  }

  const speed = keys["ShiftLeft"] || keys["ShiftRight"] ? 7.5 : 4.5;

  vel.x = moveX * speed;
  vel.z = moveZ * speed;

  vel.y -= 18 * dt;

  if ((keys["Space"] || keys["Spacebar"]) && grounded) {
    vel.y = 7.2;
    grounded = false;
  }

  const nextX = pos.x + vel.x * dt;
  if (!collides(nextX, pos.y, pos.z)) {
    pos.x = nextX;
  } else {
    vel.x = 0;
  }

  const nextZ = pos.z + vel.z * dt;
  if (!collides(pos.x, pos.y, nextZ)) {
    pos.z = nextZ;
  } else {
    vel.z = 0;
  }

  const nextY = pos.y + vel.y * dt;
  if (!collides(pos.x, nextY, pos.z)) {
    pos.y = nextY;
    grounded = false;
  } else {
    if (vel.y < 0) {
      grounded = true;
    }
    vel.y = 0;
  }

  const eyeOffset = 0.65;
  camera.position.set(pos.x, pos.y + eyeOffset, pos.z);

  const forward = getViewForward();
  camera.lookAt(
    camera.position.x + forward.x,
    camera.position.y + forward.y,
    camera.position.z + forward.z
  );

  renderer.render(scene, camera);
  requestAnimationFrame(update);
}

update();
</script>
</body>
</html>
```

操作:

- 左クリックで視点をロック
- `WASD` 移動
- `Space` 飛ぶ
- `Shift` 走る
- 左クリック: ブロック破壊
- 右クリック: 石ブロック放置
- `Q`: 破壊
- `E`: 放置

このコードには地形生成、木、碰撞、重力、視点操作、voxel raycast、ブロック放置/破壊が入っています。