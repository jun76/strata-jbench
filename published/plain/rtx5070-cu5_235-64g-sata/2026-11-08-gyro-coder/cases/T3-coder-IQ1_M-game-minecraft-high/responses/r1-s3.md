はい，単 HTML の「マイクラ風 3D box-sandbox」を作って。  
この is single HTML file, so just save as `index.html` and open in browser.

**Controls:**
- Mouse click: pointer lock
- Left mouse: remove targeted block
- Right mouse: place selected block
- Scroll wheel / keys 1-6: change block
- WASD: move
- Space: jump
- Mouse move: camera

```html
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, height=device-width" />
<title>Voxel Sandbox - Minecraft-like 3D</title>
<style>
  html,body { margin:0; height:100%; overflow:hidden; }
  canvas { position:fixed; inset:0; width:100%; height:100%; }
  .ui {
    position:fixed;
    left:12px; top:12px;
    color:white;
    font-family:monospace;
    font-size:13px;
    text-shadow:0 1px 2px black;
    pointer-events:none;
    line-height:1.35;
    max-width:calc(100vw-24px);
  }
</style>
</head>
<body>
<div class="ui" id="ui"></div>
<canvas id="game"></canvas>

<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.165.0/build/three.module.js"
  }
}
</script>

<script type="module">
import * as THREE from 'three';

/* =========================
   UI / DOM
========================= */
const canvas = document.getElementById('game');
const ui = document.getElementById('ui');

let selected = 0;
let selectedName = '';
let fps = 0;

function updateUI() {
  selectedName = TYPES[selected].name;
  ui.textContent =
`Voxel Sandbox
Click: start mouse lock
WASD: move
Space: jump
Mouse: look
Left click: remove block
Right click: place block
Scroll / 1-6: select block

Selected: ${selectedName}
FPS: ${Math.round(fps)}
Block count: ${blockCount()}`;
}

function blockCount() {
  let c = 0;
  for (const arr of coords) c += arr.length;
  return c;
}

/* =========================
   Renderer / Scene
========================= */
const renderer = new THREE.WebGLRenderer({ canvas, antialias:true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);

const scene = new THREE.Scene();
scene.background = new THREE.Color('#87ceeb');
scene.fog = new THREE.Fog('#87ceeb', 24, 110);

const camera = new THREE.PerspectiveCamera(78, window.innerWidth / window.innerHeight, 0.1, 250);
camera.rotation.order = 'YXZ';

const hemi = new THREE.HemisphereLight('#ffffff', '#30353a', 0.95);
scene.add(hemi);

const sun = new THREE.DirectionalLight('#fff3d8', 0.65);
sun.position.set(12, 25, 8);
scene.add(sun);

function onResize() {
  renderer.setSize(window.innerWidth, window.innerHeight);
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
}
window.addEventListener('resize', onResize);

/* =========================
   Block types / textures
========================= */
const TYPES = [
  { name:'grass', fill:'#5fae52', dot:'#74c264' },
  { name:'dirt',  fill:'#7d5438', dot:'#916545' },
  { name:'stone', fill:'#8a9098', dot:'#aab2ba' },
  { name:'wood',  fill:'#8c613c', dot:'#6a472b' },
  { name:'leaf',  fill:'#3e7d3b', dot:'#599c4a' },
  { name:'sand',  fill:'#c9b17b', dot:'#d7c48c' },
];

function makeTexture(base, dot, extra = '') {
  const c = document.createElement('canvas');
  c.width = 32; c.height = 32;
  const ctx = c.getContext('2d');

  ctx.fillStyle = base;
  ctx.fillRect(0, 0, 32, 32);

  // noisy voxel look
  for (let y = 0; y < 32; y++) {
    for (let x = 0; x < 32; x++) {
      const r = Math.random();
      if (r < 0.04) ctx.fillStyle = '#ffffff';
      else if (r < 0.18) ctx.fillStyle = dot;
      else continue;

      ctx.fillRect(x, y, 1, 1);
    }
  }

  if (extra === 'wood') {
    ctx.strokeStyle = 'rgba(0,0,0,0.18)';
    ctx.lineWidth = 1;
    for (let i = 4; i < 32; i += 8) {
      ctx.beginPath();
      ctx.moveTo(i, 0);
      ctx.lineTo(i, 32);
      ctx.stroke();
    }
  }

  const t = new THREE.CanvasTexture(c);
  t.magFilter = THREE.NearestFilter;
  t.minFilter = THREE.NearestFilter;
  return t;
}

const materials = TYPES.map((t, i) => {
  const tex = makeTexture(t.fill, t.dot, t.name === 'wood' ? 'wood' : '');
  return new THREE.MeshLambertMaterial({ map: tex });
});

/* =========================
   InstancedMesh world
========================= */
const SIZE = 24;           // horizontal map size
const MAX_Y = 48;          // max vertical block index
const MAX_INSTANCES = SIZE * SIZE * MAX_Y;

const blockGeo = new THREE.BoxGeometry(1, 1, 1);

const meshes = [];
const coords = TYPES.map(() => []);

for (let i = 0; i < materials.length; i++) {
  const m = new THREE.InstancedMesh(blockGeo, materials[i], MAX_INSTANCES);
  m.userData.type = i;
  m.frustumCulled = false;
  m.count = 0;
  meshes[i] = m;
}

/*
  block coordinates:
  integer x,y,z.
  A block at x=5 occupies x=5.0 .. 6.0,
  so its visual center is 5.5.
*/
const blockType = new Map();  // key -> type index
const blockIndex = new Map(); // key -> index in coords[type]

function keyFor(x, y, z) {
  return `${x},${y},${z}`;
}

function keyFrom(c) {
  return `${c[0]},${c[1]},${c[2]}`;
}

const dummy = new THREE.Object3D();
dummy.scale.set(1, 1, 1);

function addBlock(x, y, z, type) {
  if (x < 0 || x >= SIZE) return false;
  if (z < 0 || z >= SIZE) return false;
  if (y < 0 || y >= MAX_Y) return false;

  const k = keyFor(x, y, z);
  if (blockType.has(k)) return false;

  const arr = coords[type];
  if (arr.length >= MAX_INSTANCES) return false;

  const idx = arr.length;
  arr.push([x, y, z]);

  blockType.set(k, type);
  blockIndex.set(k, idx);

  dummy.position.set(x + 0.5, y + 0.5, z + 0.5);
  dummy.updateMatrix();
  meshes[type].setMatrixAt(idx, dummy.matrix);

  meshes[type].count = arr.length;
  meshes[type].instanceMatrix.needsUpdate = true;

  return true;
}

function removeBlock(x, y, z) {
  const k = keyFor(x, y, z);
  if (!blockType.has(k)) return false;

  const type = blockType.get(k);
  const arr = coords[type];
  const idx = blockIndex.get(k);
  const lastIdx = arr.length - 1;

  if (idx !== lastIdx) {
    const last = arr[lastIdx];
    const lastKey = keyFrom(last);

    arr[idx] = last;
    blockIndex.set(lastKey, idx);

    dummy.position.set(last[0] + 0.5, last[1] + 0.5, last[2] + 0.5);
    dummy.updateMatrix();
    meshes[type].setMatrixAt(idx, dummy.matrix);
  }

  arr.pop();

  blockType.delete(k);
  blockIndex.delete(k);

  meshes[type].count = arr.length;
  meshes[type].instanceMatrix.needsUpdate = true;

  return true;
}

function hasBlock(x, y, z) {
  return blockType.has(keyFor(x, y, z));
}

/* =========================
   Terrain generation
========================= */
function hash2(x, z) {
  const n = Math.sin(x * 127.13 + z * 311.7) * 43758.5453;
  return n - Math.floor(n);
}

function noise2(x, z) {
  return (
    hash2(x, z) * 0.5 +
    hash2(x + 3.1, z - 1.7) * 0.3 +
    hash2(x - 5.2, z + 2.8) * 0.2
  );
}

function heightAt(x, z) {
  const n = noise2(x, z);
  const h = 3 + Math.floor(n * 10);
  return Math.max(2, Math.min(12, h));
}

function terrain(x, z) {
  const h = heightAt(x, z);

  for (let y = 0; y < h; y++) {
    let type = 0;

    if (y === h - 1) type = 0;          // grass top
    else if (y >= h - 3) type = 1;      // dirt
    else type = 2;                      // stone

    addBlock(x, y, z, type);
  }
}

for (let x = 0; x < SIZE; x++) {
  for (let z = 0; z < SIZE; z++) {
    terrain(x, z);
  }
}

// simple trees
for (let x = 2; x < SIZE - 2; x++) {
  for (let z = 2; z < SIZE - 2; z++) {
    const seed = hash2(x * 9.1 + 3.7, z * 14.3 + 11.2);
    if (seed < 0.92) continue;

    const h = heightAt(x, z);
    if (h < 4) continue;

    const trunkH = 3 + Math.floor(seed * 2.5);

    // trunk
    for (let y = h; y < h + trunkH; y++) {
      addBlock(x, y, z, 3); // wood
    }

    // leaves
    const leafY = h + trunkH;
    addBlock(x, leafY, z, 4);

    for (let dx = -1; dx <= 1; dx++) {
      for (let dz = -1; dz <= 1; dz++) {
        if (dx === 0 && dz === 0) continue;
        addBlock(x + dx, leafY, z + dz, 4);
      }
    }

    for (let dx = -1; dx <= 1; dx++) {
      for (let dz = -1; dz <= 1; dz++) {
        if (Math.abs(dx) === 1 && Math.abs(dz) === 1) continue;
        addBlock(x + dx, leafY - 1, z + dz, 4);
      }
    }
  }
}

/* =========================
   Interaction highlight
========================= */
const outline = new THREE.LineSegments(
  new THREE.EdgesGeometry(new THREE.BoxGeometry(1.001, 1.001, 1.001)),
  new THREE.LineBasicMaterial({ color: '#ffffff' })
);
outline.visible = false;
scene.add(outline);

const preview = new THREE.Mesh(
  new THREE.BoxGeometry(0.98, 0.98, 0.98),
  new THREE.MeshBasicMaterial({
    color: '#ffffff',
    transparent: true,
    opacity: 0.28
  })
);
preview.visible = false;
scene.add(preview);

/* =========================
   Pointer lock / input
========================= */
let pointerLocked = false;
let yaw = 0;
let pitch = 0;

document.addEventListener('pointerlockchange', () => {
  pointerLocked = true;
  updateUI();
});

document.addEventListener('pointerlockerror', () => {
  pointerLocked = false;
});

canvas.addEventListener('click', () => {
  canvas.requestPointerLock();
});

canvas.addEventListener('contextmenu', e => {
  e.preventDefault();
});

document.addEventListener('mousemove', e => {
  if (!pointerLocked) return;
  const sens = 0.0025;
  yaw -= e.movementX * sens;
  pitch -= e.movementY * sens;
  pitch = Math.max(-1.55, Math.min(1.55, pitch));
  camera.rotation.set(pitch, yaw, 0);
}, { passive:true });

const keys = new Set();

document.addEventListener('keydown', e => {
  keys.add(e.key.toLowerCase());

  if (e.key >= '1' && e.key <= '6') {
    selected = Number(e.key) - 1;
    updateUI();
  }
});

document.addEventListener('keyup', e => {
  keys.delete(e.key.toLowerCase());
});

document.addEventListener('wheel', e => {
  const dir = e.deltaY > 0 ? 1 : -1;
  selected = (selected + dir + TYPES.length) % TYPES.length;
  updateUI();
}, { passive:true });

function doClick(button) {
  if (!pointerLocked) return;

  const ray = new THREE.Raycaster();
  ray.setFromCamera(new THREE.Vector2(0, 0), camera);
  ray.far = 9;

  const hits = ray.intersectObjects(meshes, false);
  if (!hits.length) return;

  const hit = hits[0];
  const type = hit.object.userData.type;
  const id = hit.instanceId;
  if (id == null) return;

  const coord = coords[type][id];
  if (!coord) return;

  const bx = coord[0];
  const by = coord[1];
  const bz = coord[2];

  // show outline
  outline.position.set(bx + 0.5, by + 0.5, bz + 0.5);
  outline.visible = true;

  if (button === 0) {
    // remove block
    removeBlock(bx, by, bz);
  } else if (button === 2) {
    // place block adjacent to face normal
    const center = new THREE.Vector3(bx + 0.5, by + 0.5, bz + 0.5);
    const point = hit.point;

    let n;
    if (hit.face) n = hit.face.normal.clone();
    else n = new THREE.Vector3().subVectors(point, center);

    if (n.lengthSq() < 1e-10) n.set(0, 1, 0);

    n.normalize();

    // snap to 6 directions
    const ax = Math.abs(n.x);
    const ay = Math.abs(n.y);
    const az = Math.abs(n.z);

    if (ax >= ay && ax >= az) n.set(Math.sign(n.x), 0, 0);
    else if (ay >= az) n.set(0, Math.sign(n.y), 0);
    else n.set(0, 0, Math.sign(n.z));

    // ensure normal points outward from block center
    const delta = new THREE.Vector3().subVectors(point, center);
    if (delta.lengthSq() > 1e-8 && n.dot(delta) < 0) n.negate();

    const nx = bx + Math.round(n.x);
    const ny = by + Math.round(n.y);
    const nz = bz + Math.round(n.z);

    // preview block
    preview.position.set(nx + 0.5, ny + 0.5, nz + 0.5);
    preview.visible = true;

    // prevent placing inside player
    const px = player.x, py = player.y, pz = player.z;
    const overlap =
      px + PLAYER_R > nx && px - PLAYER_R < nx + 1 &&
      py + PLAYER_H > ny && py < ny + 1 &&
      pz + PLAYER_R > nz && pz - PLAYER_R < nz + 1;

    if (!overlap) {
      addBlock(nx, ny, nz, selected);
    }
  }
}

canvas.addEventListener('mousedown', e => {
  doClick(e.button);
});

/* =========================
   Player physics
========================= */
const PLAYER_R = 0.34;
const PLAYER_H = 1.65;

const player = { x: SIZE / 2, y: 30, z: SIZE / 2, vy: 0 };

const gravity = 22;
const jumpPower = 7.4;
const moveSpeed = 4.4;
const airControl = 0.72;
const groundControl = 1.0;

let grounded = true;

function collide(px, py, pz) {
  const eps = 0.001;
  const minX = px - PLAYER_R + eps;
  const maxX = px + PLAYER_R - eps;
  const minY = py + eps;
  const maxY = py + PLAYER_H - eps;
  const minZ = pz - PLAYER_R + eps;
  const maxZ = pz + PLAYER_R - eps;

  const x0 = Math.floor(minX);
  const x1 = Math.floor(maxX);
  const y0 = Math.floor(minY);
  const y1 = Math.floor(maxY);
  const z0 = Math.floor(minZ);
  const z1 = Math.floor(maxZ);

  for (let x = x0; x <= x1; x++) {
    for (let y = y0; y <= y1; y++) {
      for (let z = z0; z <= z1; z++) {
        if (hasBlock(x, y, z)) return true;
      }
    }
  }
  return false;
}

function tryX(delta) {
  const old = player.x;
  player.x += delta;
  if (collide(player.x, player.y, player.z)) {
    player.x = old;
    return true;
  }
  return false;
}

function tryZ(delta) {
  const old = player.z;
  player.z += delta;
  if (collide(player.x, player.y, player.z)) {
    player.z = old;
    return true;
  }
  return false;
}

function tryY(delta) {
  const old = player.y;
  player.y += delta;
  if (collide(player.x, player.y, player.z)) {
    player.y = old;
    if (delta < 0) grounded = true;
    return true;
  }
  return false;
}

function movePlayer(dt) {
  const forward = new THREE.Vector3(-Math.sin(yaw), 0, -Math.cos(yaw));
  const right = new THREE.Vector3(Math.cos(yaw), 0, -Math.sin(yaw));

  let inputX = 0;
  let inputZ = 0;

  if (keys.has('a')) inputX -= 1;
  if (keys.has('d')) inputX += 1;
  if (keys.has('z')) inputZ += 1; // for French/AZERTY users
  if (keys.has('w')) inputZ += 1;
  if (keys.has('s')) inputZ -= 1;

  const dir = new THREE.Vector3();
  dir.addScaledVector(right, inputX);
  dir.addScaledVector(forward, inputZ);

  if (dir.lengthSq() > 0) dir.normalize();

  const control = grounded ? groundControl : airControl;
  const moveX = dir.x * moveSpeed * control * dt;
  const moveZ = dir.z * moveSpeed * control * dt;

  tryX(moveX);
  tryZ(moveZ);

  // gravity
  player.vy -= gravity * dt;
  player.vy = Math.max(-50, player.vy);

  // jump
  if (keys.has(' ') && grounded) {
    player.vy = jumpPower;
    grounded = false;
  }

  if (tryY(player.vy)) {
    if (player.vy < 0) {
      grounded = true;
    }
    player.vy = 0;
  }

  // respawn if somehow under world
  if (player.y < -20) {
    player.x = SIZE / 2;
    player.y = 30;
    player.z = SIZE / 2;
    player.vy = 0;
    grounded = false;
  }
}

/* =========================
   Main loop
========================= */
function updateCameraToPlayer() {
  camera.position.set(player.x, player.y + PLAYER_H * 0.45, player.z);
}

updateCameraToPlayer();

let last = performance.now();

function loop() {
  const now = performance.now();
  let dt = (now - last) / 1000;
  last = now;
  dt = Math.min(dt, 0.05);

  fps = 1 / Math.max(0.0001, dt);

  movePlayer(dt);
  updateCameraToPlayer();

  // clear highlights when not clicking
  outline.visible = false;
  preview.visible = false;

  renderer.render(scene, camera);
  updateUI();

  requestAnimationFrame(loop);
}

/* start loop */
requestAnimationFrame(loop);
</script>
</body>
</html>
```