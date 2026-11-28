Here's a single self-contained HTML file — paste it into a file (e.g. `harbor.html`) and open it in Chrome. It renders immediately, with orbit/zoom/pan via the mouse. Three.js loads from a CDN, so the page needs internet (otherwise the "Loading…" note stays visible).

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>A Sailing Ship Calling at a Harbor</title>
<style>
  body {
    margin: 0; overflow: hidden;
    background: linear-gradient(180deg, #5fa8d8 0%, #9cc8e4 45%, #e8f4fa 100%);
    font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
  }
  canvas { display: block; }
  .panel {
    position: absolute; top: 14px; left: 14px; z-index: 10;
    padding: 12px 16px; max-width: 340px;
    background: rgba(20, 30, 44, 0.55); color: #fff;
    border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.2);
    backdrop-filter: blur(6px);
  }
  .panel h1 { font-size: 16px; margin: 0 0 6px 0; letter-spacing: 0.4px; }
  .panel p { font-size: 12px; margin: 0 0 10px 0; opacity: 0.85; line-height: 1.45; }
  .buttons { display: flex; gap: 8px; }
  button {
    cursor: pointer; border: 1px solid rgba(255,255,255,0.35);
    background: rgba(255,255,255,0.12); color: #fff;
    padding: 6px 10px; border-radius: 8px; font-size: 12px;
  }
  button:hover { background: rgba(255,255,255,0.22); }
  .hint {
    position: absolute; bottom: 12px; left: 14px; z-index: 10;
    color: #fff; font-size: 11px; background: rgba(20,30,44,0.4);
    padding: 6px 10px; border-radius: 8px; backdrop-filter: blur(4px);
  }
  .loading {
    position: absolute; bottom: 12px; right: 14px; z-index: 10;
    color: #fff; font-size: 11px; background: rgba(20,30,44,0.4);
    padding: 6px 10px; border-radius: 8px;
  }
</style>
</head>
<body>
<div class="panel">
  <h1>A Sailing Ship Calling at a Harbor</h1>
  <p>Voxel scene — drag to orbit, scroll to zoom, right-drag to pan.</p>
  <div class="buttons">
    <button id="reset" type="button">Reset view</button>
    <button id="rotate" type="button">Auto-rotate: off</button>
  </div>
</div>
<div class="hint">Mouse: drag = orbit · wheel = zoom · right-drag = pan</div>
<div class="loading" id="loading">Loading scene… (needs internet for the Three.js CDN)</div>

<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
  }
}
</script>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const loadingEl = document.getElementById('loading');

// ---------- renderer / scene / camera ----------
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xd8e9f2, 70, 150);

const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 300);
camera.position.set(26, 22, 36);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 3, -2);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.minDistance = 8;
controls.maxDistance = 90;
controls.maxPolarAngle = Math.PI * 0.49;
controls.autoRotateSpeed = 0.6;

// ---------- lights ----------
scene.add(new THREE.HemisphereLight(0xcfe8f5, 0x5b6b7a, 0.7));
const sunLight = new THREE.DirectionalLight(0xfff2d8, 1.1);
sunLight.position.set(30, 40, 18);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
sunLight.shadow.camera.left = -40; sunLight.shadow.camera.right = 40;
sunLight.shadow.camera.top = 40;  sunLight.shadow.camera.bottom = -40;
sunLight.shadow.camera.near = 1;  sunLight.shadow.camera.far = 120;
sunLight.shadow.bias = -0.0004;
scene.add(sunLight);
const fillLight = new THREE.DirectionalLight(0xbfd3e8, 0.3);
fillLight.position.set(-25, 15, -20);
scene.add(fillLight);

// ---------- helpers ----------
const boxGeo = new THREE.BoxGeometry(1, 1, 1);
const matCache = new Map();
const glowCache = new Map();
function mat(color) {
  if (!matCache.has(color)) matCache.set(color, new THREE.MeshLambertMaterial({ color }));
  return matCache.get(color);
}
function glowMat(color) {
  if (!glowCache.has(color)) glowCache.set(color, new THREE.MeshBasicMaterial({ color }));
  return glowCache.get(color);
}
function voxel(parent, x, y, z, color, size = 1, castShadow = true) {
  const mesh = new THREE.Mesh(boxGeo, mat(color));
  mesh.position.set(x, y, z);
  mesh.scale.setScalar(size);
  mesh.castShadow = castShadow;
  mesh.receiveShadow = true;
  parent.add(mesh);
  return mesh;
}
function rand(x, y, z) {
  return Math.abs(Math.sin(x * 12.9898 + y * 78.233 + z * 37.719) * 43758.5453) % 1;
}
const dummy = new THREE.Object3D();
function buildInstanced(tiles, { size = 1, castShadow = true, receiveShadow = true } = {}) {
  const mesh = new THREE.InstancedMesh(
    boxGeo, new THREE.MeshLambertMaterial({ color: 0xffffff }), tiles.length
  );
  mesh.castShadow = castShadow;
  mesh.receiveShadow = receiveShadow;
  for (let i = 0; i < tiles.length; i++) {
    const t = tiles[i];
    dummy.position.set(t.x, t.y ?? 0, t.z);
    dummy.rotation.set(0, 0, 0);
    dummy.scale.setScalar(size);
    dummy.updateMatrix();
    mesh.setMatrixAt(i, dummy.matrix);
    mesh.setColorAt(i, new THREE.Color(t.color));
  }
  mesh.instanceMatrix.needsUpdate = true;
  mesh.instanceColor.needsUpdate = true;
  return mesh;
}

// ---------- static harbor (instanced voxels) ----------
const staticTiles = [];
function addStatic(x, y, z, color) { staticTiles.push({ x, y, z, color }); }

// pier
for (let x = -16; x <= 16; x++) {
  for (let z = -14; z <= -6; z++) {
    for (let y = 1; y <= 2; y++) {
      const edge = (z === -6) || (x === -16 || x === 16);
      const color = edge ? 0x5f636a : (rand(x, y, z) > 0.5 ? 0x8b8f95 : 0x7a7e84);
      addStatic(x, y, z, color);
    }
  }
}
for (const [px, pz] of [[-16, -6], [16, -6], [-16, -14], [16, -14]]) {
  addStatic(px, 3, pz, 0x5a3a24);
}

// warehouse
for (let x = -13; x <= -8; x++) {
  for (let z = -13; z <= -9; z++) {
    for (let y = 3; y <= 5; y++) {
      if (z === -9 && y <= 4 && (x === -10 || x === -9)) continue; // door cells
      if (z === -9 && y === 4 && (x === -12 || x === -8)) continue; // window cells
      addStatic(x, y, z, rand(x, y, z) > 0.5 ? 0xc8a06b : 0xb89466);
    }
  }
}
for (const x of [-10, -9]) for (const y of [3, 4]) addStatic(x, y, -9, 0x4a2f1a);
addStatic(-12, 4, -9, 0x2e2a26);
addStatic(-8, 4, -9, 0x2e2a26);
for (let x = -13; x <= -8; x++) {
  for (let z = -12; z <= -10; z++) addStatic(x, 6, z, 0x7a4b2e);
  for (let z = -11; z <= -10; z++) addStatic(x, 7, z, 0x5f3a22);
}
addStatic(-12, 7, -12, 0x5f3a22); // chimney

// lighthouse (rock + striped tower + spire)
for (let x = -20; x <= -18; x++) {
  for (let z = -11; z <= -9; z++) {
    for (let y = 1; y <= 2; y++) addStatic(x, y, z, rand(x, y, z) > 0.5 ? 0x6f6b63 : 0x7a7268);
  }
}
for (let y = 3; y <= 8; y++) addStatic(-19, y, -10, y <= 4 ? 0xc4453c : y <= 6 ? 0xf2efe6 : 0xc4453c);
addStatic(-19, 9, -10, 0x3a3d44);
addStatic(-19, 11, -10, 0xc4453c);

// crane
addStatic(13, 3, -8, 0x3a3d44);
for (let y = 4; y <= 7; y++) addStatic(13, y, -8, 0xb3542c);
for (let z = -7; z <= -4; z++) addStatic(13, 7, z, 0x5a3a24);
addStatic(13, 6, -4, 0x3a3d44); // hook
addStatic(13, 5, -4, 0xb08d57); // hanging crate

// crates, barrels, lamppost
addStatic(-6, 3, -8, 0xb08d57);
addStatic(-6, 4, -8, 0x9a7747);
addStatic(-4, 3, -7, 0xb08d57);
addStatic(6, 3, -8, 0x7a4b2e);
addStatic(7, 3, -8, 0x7a4b2e);
addStatic(0, 3, -7, 0x4a3a2a);
addStatic(0, 4, -7, 0x4a3a2a);
addStatic(0, 5, -7, 0x4a3a2a);

const staticMesh = buildInstanced(staticTiles, { size: 1, castShadow: true, receiveShadow: true });
scene.add(staticMesh);

// ---------- water (instanced, animated) ----------
const waterTiles = [];
const waterPalette = [0x3a6fa8, 0x4a7fb5, 0x2e5d8a, 0x5a8fc2];
function waterColor(x, z) {
  const r = Math.abs(Math.sin(x * 12.9898 + z * 78.233) * 43758.5453) % 1;
  return waterPalette[Math.floor(r * waterPalette.length) % waterPalette.length];
}
for (let x = -22; x <= 22; x++) {
  for (let z = -16; z <= 14; z++) {
    if (x >= -16 && x <= 16 && z >= -14 && z <= -6) continue; // under the pier
    waterTiles.push({ x, z, color: waterColor(x, z) });
  }
}
const waterMesh = buildInstanced(waterTiles, { size: 1.02, castShadow: false, receiveShadow: true });
scene.add(waterMesh);

// ---------- the sailing ship ----------
const shipGroup = new THREE.Group();
const portholes = new Set();
for (const px of [-4, -1, 2]) { portholes.add(`${px},2,2`); portholes.add(`${px},2,-2`); }
function sv(x, y, z, color) { voxel(shipGroup, x, y, z, color); }

for (let x = -5; x <= 5; x++) for (let z = -1; z <= 1; z++) sv(x, 0, z, 0x4a2f1a);
for (let x = -6; x <= 6; x++) {
  for (let z = -2; z <= 2; z++) {
    sv(x, 1, z, 0x4a2f1a);
    sv(x, 2, z, portholes.has(`${x},2,${z}`) ? 0x2e2a26 : 0x4a2f1a);
  }
}
for (let z = -1; z <= 1; z++) {
  sv(7, 0, z, 0x4a2f1a); sv(7, 1, z, 0x4a2f1a);
  sv(-7, 0, z, 0x4a2f1a); sv(-7, 1, z, 0x4a2f1a);
}
sv(8, 0, 0, 0x4a2f1a); sv(8, 1, 0, 0x4a2f1a);
sv(-8, 0, 0, 0x4a2f1a); sv(-8, 1, 0, 0x4a2f1a);
for (let x = -6; x <= 6; x++) for (let z = -2; z <= 2; z++) sv(x, 3, z, 0xc99e5f);
for (let x = -3; x <= 1; x++) for (let z = -1; z <= 1; z++) sv(x, 4, z, 0xb08d57);
for (let x = -4; x <= 2; x++) for (let z = -2; z <= 2; z++) sv(x, 5, z, 0x7a4b2e);
for (const y of [4, 5, 6, 7, 9, 10]) sv(3, y, 0, 0x5a3a24); // mast (skip yard row)
for (let z = -4; z <= 4; z++) sv(3, 8, z, 0x5a3a24);       // yard
const sailGroup = new THREE.Group();
sailGroup.position.set(2, 7, 0);
shipGroup.add(sailGroup);
for (const [y, zmin, zmax] of [[4, -3, 3], [5, -2, 2], [6, -2, 2], [7, -1, 1]]) {
  for (let z = zmin; z <= zmax; z++) {
    voxel(sailGroup, 0, y - 7, z, rand(z, y, 0) > 0.5 ? 0xf4ead8 : 0xe8dcc6);
  }
}
const flagGroup = new THREE.Group();
flagGroup.position.set(3, 11, 0);
shipGroup.add(flagGroup);
for (const dx of [-1, -2, -3]) voxel(flagGroup, dx, 0, 0, 0xc4453c);
shipGroup.position.set(6, 0.45, 3);
shipGroup.rotation.y = -0.15;
scene.add(shipGroup);

// ---------- moored rowboat ----------
const boatGroup = new THREE.Group();
for (let x = -2; x <= 2; x++) {
  for (let z = -1; z <= 1; z++) {
    voxel(boatGroup, x, 0, z, 0x4a2f1a);
    voxel(boatGroup, x, 1, z, 0xc99e5f);
  }
}
for (let x = -1; x <= 1; x++) for (let z = -1; z <= 1; z++) voxel(boatGroup, x, 2, z, 0xb08d57);
boatGroup.position.set(-9, 0.45, 0);
scene.add(boatGroup);

// ---------- buoys ----------
const buoy1 = new THREE.Group();
voxel(buoy1, 0, 0, 0, 0xc4453c); voxel(buoy1, 0, 1, 0, 0xf2efe6);
buoy1.position.set(-4, 0.1, 5); scene.add(buoy1);
const buoy2 = new THREE.Group();
voxel(buoy2, 0, 0, 0, 0xc4453c); voxel(buoy2, 0, 1, 0, 0xf2efe6);
buoy2.position.set(12, 0.1, 7); scene.add(buoy2);

// ---------- glows / beam / sun ----------
const lantern = new THREE.Mesh(boxGeo, glowMat(0xffd84d));
lantern.position.set(-19, 10, -10); lantern.scale.setScalar(1.05);
scene.add(lantern);
const lamp = new THREE.Mesh(boxGeo, glowMat(0xffd84d));
lamp.position.set(0, 6, -7); scene.add(lamp);

const beamGroup = new THREE.Group();
beamGroup.position.set(-19, 10, -10);
const beam = new THREE.Mesh(
  new THREE.BoxGeometry(14, 0.8, 1.6),
  new THREE.MeshBasicMaterial({ color: 0xffd84d, transparent: true, opacity: 0.15, depthWrite: false })
);
beam.position.set(7, 0, 0);
beamGroup.add(beam); scene.add(beamGroup);

const sunGroup = new THREE.Group();
for (let dx = 0; dx < 2; dx++) for (let dy = 0; dy < 2; dy++) for (let dz = 0; dz < 2; dz++) {
  const m = new THREE.Mesh(boxGeo, glowMat(0xffd84d));
  m.position.set(dx, dy, dz); sunGroup.add(m);
}
sunGroup.position.set(18, 14.5, -22);
scene.add(sunGroup);

// ---------- clouds ----------
const clouds = [];
function makeCloud(x, y, z, speed) {
  const g = new THREE.Group();
  const white = mat(0xf5f7fa);
  for (const [dx, dy, dz] of [[0,0,0],[1,0,0],[2,0,0],[0,1,0],[1,1,0],[2,1,0]]) {
    const m = new THREE.Mesh(boxGeo, white);
    m.position.set(dx, dy, dz); g.add(m);
  }
  g.position.set(x, y, z);
  g.userData.speed = speed;
  scene.add(g); clouds.push(g);
}
makeCloud(-10, 13, -12, 0.5);
makeCloud(10, 14, -6, 0.4);
makeCloud(2, 13.5, 6, 0.35);

// ---------- gulls ----------
const gulls = [];
function makeGull(a, radius, height, speed) {
  const group = new THREE.Group();
  const body = new THREE.Mesh(boxGeo, mat(0x3a3d44));
  group.add(body);
  const wingL = new THREE.Group();
  const wl = new THREE.Mesh(boxGeo, mat(0x3a3d44)); wl.position.set(-1, 0, 0); wingL.add(wl);
  const wingR = new THREE.Group();
  const wr = new THREE.Mesh(boxGeo, mat(0x3a3d44)); wr.position.set(1, 0, 0); wingR.add(wr);
  group.add(wingL, wingR); scene.add(group);
  gulls.push({ group, wingL, wingR, a, radius, height, speed });
}
makeGull(0.5, 9, 11.5, 0.45);
makeGull(2.5, 12, 13, 0.3);

// ---------- UI ----------
document.getElementById('reset').addEventListener('click', () => {
  camera.position.set(26, 22, 36);
  controls.target.set(0, 3, -2);
  controls.update();
});
document.getElementById('rotate').addEventListener('click', (e) => {
  controls.autoRotate = !controls.autoRotate;
  e.target.textContent = `Auto-rotate: ${controls.autoRotate ? 'on' : 'off'}`;
});
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// ---------- animation ----------
const clock = new THREE.Clock();
let t = 0;
let firstFrame = true;
function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  t += dt;

  for (let i = 0; i < waterTiles.length; i++) {
    const w = waterTiles[i];
    const y = Math.sin(w.x * 0.35 + w.z * 0.5 + t * 1.4) * 0.12;
    dummy.position.set(w.x, y, w.z);
    dummy.rotation.set(0, 0, 0);
    dummy.scale.setScalar(1.02);
    dummy.updateMatrix();
    waterMesh.setMatrixAt(i, dummy.matrix);
  }
  waterMesh.instanceMatrix.needsUpdate = true;

  shipGroup.position.y = 0.45 + Math.sin(t * 1.1) * 0.18;
  shipGroup.rotation.z = Math.sin(t * 0.9) * 0.035;
  shipGroup.rotation.x = Math.sin(t * 0.7) * 0.02;
  sailGroup.rotation.y = Math.sin(t * 0.9) * 0.08;
  flagGroup.rotation.y = Math.sin(t * 4) * 0.3;

  boatGroup.position.y = 0.45 + Math.sin(t * 1.1 + 1.5) * 0.18;
  boatGroup.rotation.z = Math.sin(t * 0.9 + 1.5) * 0.035;

  buoy1.position.y = 0.1 + Math.sin(t * 1.4 + 1) * 0.1;
  buoy2.position.y = 0.1 + Math.sin(t * 1.4 + 2.3) * 0.1;

  for (const c of clouds) {
    c.position.x += c.userData.speed * dt;
    if (c.position.x > 34) c.position.x = -34;
  }

  beamGroup.rotation.y = t * 0.45;

  for (const g of gulls) {
    g.a += g.speed * dt;
    g.group.position.set(
      Math.cos(g.a) * g.radius,
      g.height + Math.sin(t * 0.8 + g.a) * 0.7,
      Math.sin(g.a) * g.radius
    );
    g.group.rotation.y = -g.a;
    const flap = Math.sin(t * 9 + g.a * 2) * 0.55;
    g.wingL.rotation.z = -flap;
    g.wingR.rotation.z = flap;
  }

  sunGroup.scale.setScalar(1 + Math.sin(t * 1.5) * 0.05);

  controls.update();
  renderer.render(scene, camera);

  if (firstFrame) { loadingEl.style.display = 'none'; firstFrame = false; }
}
animate();
</script>
</body>
</html>
```

Highlights:

- **Scene**: a voxel sailing ship (hull, portholes, cabin, mast, yard, cream sail, red flag) bobbing in the water near a stone pier with a warehouse, striped lighthouse with rotating beam, orange crane with a hanging crate, crates/barrels, a lamppost, a moored rowboat, floating buoys, drifting clouds, two gliding gulls, a voxel sun, and gently rippling water — all animated.
- **Mouse control**: left-drag to orbit, scroll to zoom, right-drag to pan (with a Reset view button and optional auto-rotate).
- **Performance**: water and static harbor are rendered as `InstancedMesh` (few draw calls); the ship is individual voxels with cached materials — runs immediately in Chrome.

If you want, I can also add a clickable "moo" button that nudges the ship toward the dock, or a night-time palette variant.