Here's a self-contained 3D voxel scene — a sailing ship calling at a harbor (pier, docks, lighthouse, seagulls, drifting clouds, animated voxel waves). Paste it into a `.html` file and open it in Chrome.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Voxel Harbor — A Sailing Ship Calling</title>
<style>
  html, body { margin: 0; height: 100%; overflow: hidden; }
  body {
    font-family: Georgia, serif;
    background: linear-gradient(180deg, #5fb4e6 0%, #8fd0ee 38%, #c7e6f2 68%, #e8f4f6 100%);
  }
  #app { position: fixed; inset: 0; }
  canvas { display: block; }
  #hud {
    position: fixed; top: 16px; left: 16px;
    background: rgba(255,255,255,0.72);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255,255,255,0.8);
    border-radius: 12px;
    padding: 12px 16px;
    color: #23445e;
    box-shadow: 0 6px 24px rgba(30,60,90,0.18);
    pointer-events: none;
    max-width: 340px;
  }
  #hud h1 { margin: 0 0 6px; font-size: 19px; letter-spacing: 0.4px; }
  #hud p { margin: 0; font-size: 12px; line-height: 1.5; opacity: 0.85; }
  #hud .tag { color: #4a7a9a; }
</style>
</head>
<body>
<div id="app"></div>
<div id="hud">
  <h1>⚓ Voxel Harbor</h1>
  <p>A sailing ship calling at a harbor — built entirely from voxel cubes.</p>
  <p class="tag">Drag to orbit · Scroll to zoom · Right-drag to pan</p>
</div>

<script type="importmap">
{
  "imports": {
    "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
    "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
  }
}
</script>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// ---------- deterministic random ----------
let _seed = 987654321;
function srand() { _seed = (_seed * 1664525 + 1013904223) >>> 0; return _seed / 4294967296; }

// ---------- renderer / scene / camera ----------
const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xd8ecf2, 70, 190);

const camera = new THREE.PerspectiveCamera(42, window.innerWidth / window.innerHeight, 0.1, 500);
camera.position.set(30, 24, 40);

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setClearColor(0x000000, 0);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
document.getElementById('app').appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(4, 4, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.minDistance = 12;
controls.maxDistance = 120;
controls.maxPolarAngle = Math.PI * 0.49;

// ---------- lights ----------
scene.add(new THREE.HemisphereLight(0xd9ecff, 0x2e4a5e, 0.85));

const sunLight = new THREE.DirectionalLight(0xfff1d6, 1.7);
sunLight.position.set(-40, 48, 30);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
sunLight.shadow.camera.left = -60; sunLight.shadow.camera.right = 60;
sunLight.shadow.camera.top = 60;  sunLight.shadow.camera.bottom = -60;
sunLight.shadow.camera.near = 10; sunLight.shadow.camera.far = 160;
sunLight.shadow.bias = -0.0004;
sunLight.shadow.normalBias = 0.02;
scene.add(sunLight);

const rim = new THREE.DirectionalLight(0xbfdcff, 0.45);
rim.position.set(45, 18, -35);
scene.add(rim);

// ---------- voxel helpers ----------
function makeInstancedMesh(cells, { castShadow = true, receiveShadow = true } = {}) {
  const geo = new THREE.BoxGeometry(1, 1, 1);
  const mat = new THREE.MeshLambertMaterial({ color: 0xffffff });
  const mesh = new THREE.InstancedMesh(geo, mat, cells.length);
  const dummy = new THREE.Object3D();
  const col = new THREE.Color();
  for (let i = 0; i < cells.length; i++) {
    const c = cells[i];
    dummy.position.set(c.x, c.y, c.z);
    dummy.updateMatrix();
    mesh.setMatrixAt(i, dummy.matrix);
    col.set(c.color);
    if (c.jitter) col.multiplyScalar(1 + (srand() - 0.5) * c.jitter);
    mesh.setColorAt(i, col);
  }
  mesh.instanceMatrix.needsUpdate = true;
  if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
  mesh.castShadow = castShadow;
  mesh.receiveShadow = receiveShadow;
  mesh.frustumCulled = false;
  return mesh;
}

// ---------- water ----------
const waterCells = [];
for (let x = -44; x <= 44; x++) {
  for (let z = -26; z <= 26; z++) {
    if (x >= -38 && x <= -10 && z >= -16 && z <= 16) continue;   // island
    if (x >= 24 && x <= 28 && z >= -22 && z <= -18) continue;   // lighthouse islet
    if ((x === -9 || x === -5 || x === -1) && (z === -2 || z === 2)) continue; // pier posts
    const foam = (x === -9 && z >= -15 && z <= 15) || (x === -39 && z >= -15 && z <= 15)
               || (z === -17 && x >= -37 && x <= -11) || (z === 17 && x >= -37 && x <= -11);
    const color = foam ? 0xd9eef4 : (srand() < 0.12 ? 0x49a3c6 : 0x2f7fa8);
    waterCells.push({ x, y: 0, z, color, foam });
  }
}
const waterMesh = makeInstancedMesh(waterCells, { castShadow: false, receiveShadow: true });
scene.add(waterMesh);

// ---------- island ----------
const islandCells = [];
for (let x = -38; x <= -10; x++) {
  for (let z = -16; z <= 16; z++) {
    islandCells.push({ x, y: 0, z, color: 0x7d5a38, jitter: 0.15 });
    islandCells.push({ x, y: 1, z, color: 0x8a6238, jitter: 0.12 });
    const beach = (x === -11 || x === -10);
    let top = 0xe3c98e, jitter = 0.12;
    if (!beach && x <= -12 && srand() < 0.34) { top = 0x5fa63f; jitter = 0.25; }
    islandCells.push({ x, y: 2, z, color: top, jitter });
    if (!beach && x <= -12 && srand() < 0.07) {
      const fc = [0xff7b9c, 0xffd75e, 0xffffff, 0xc77bff][Math.floor(srand() * 4)];
      islandCells.push({ x, y: 3, z, color: fc, jitter: 0.1 });
    }
  }
}
// trees
function tree(tx, tz) {
  islandCells.push({ x: tx, y: 3, z: tz, color: 0x6e4a2c, jitter: 0.1 });
  for (let dx = -1; dx <= 1; dx++) for (let dz = -1; dz <= 1; dz++)
    islandCells.push({ x: tx + dx, y: 4, z: tz + dz, color: 0x4e8f3a, jitter: 0.2 });
  islandCells.push({ x: tx, y: 5, z: tz, color: 0x5fa63f });
}
tree(-33, 12); tree(-14, 10);
// warehouse
for (let x = -34; x <= -30; x++) for (let z = -8; z <= -4; z++) for (let y = 3; y <= 4; y++) {
  let color = 0xb98a63;
  if (x === -30 && y === 3 && z === -6) color = 0x3a2a1c;   // door
  if (x === -34 && y === 4 && z === -6) color = 0x3a2a1c;   // window
  islandCells.push({ x, y, z, color, jitter: 0.15 });
}
for (let x = -35; x <= -29; x++) for (let z = -9; z <= -3; z++)
  islandCells.push({ x, y: 5, z, color: 0x5d3d22, jitter: 0.1 });
// crates & barrels
for (let x = -13; x <= -12; x++) for (let y = 3; y <= 4; y++) for (let z = -6; z <= -5; z++)
  islandCells.push({ x, y, z, color: 0xa9773f, jitter: 0.2 });
islandCells.push({ x: -11, y: 3, z: -6, color: 0xa9773f, jitter: 0.2 });
for (const bx of [-11, -12]) for (let y = 3; y <= 4; y++)
  islandCells.push({ x: bx, y, z: 4, color: 0x7a4a2b, jitter: 0.12 });
scene.add(makeInstancedMesh(islandCells));

// ---------- pier ----------
const pierCells = [];
for (let x = -9; x <= 2; x++) for (let z = -2; z <= 2; z++)
  pierCells.push({ x, y: 2, z, color: 0x9a6b3f, jitter: 0.18 });
for (const px of [-9, -5, -1]) for (const pz of [-2, 2]) for (let py = 0; py <= 1; py++)
  pierCells.push({ x: px, y: py, z: pz, color: 0x5d3d22, jitter: 0.1 });
scene.add(makeInstancedMesh(pierCells));

// ---------- ship ----------
const shipCells = [];
const hullRows = [
  { z: -6, cells: [-1, 0, 1] },
  { z: -5, cells: [-2, -1, 0, 1] },
  { z: -4, cells: [-2, -1, 0, 1] },
  { z: -3, cells: [-2, -1, 0, 1, 2] },
  { z: -2, cells: [-2, -1, 0, 1, 2] },
  { z: -1, cells: [-2, -1, 0, 1, 2] },
  { z: 0,  cells: [-2, -1, 0, 1, 2] },
  { z: 1,  cells: [-2, -1, 0, 1] },
  { z: 2,  cells: [-2, -1, 0, 1] },
  { z: 3,  cells: [-1, 0, 1] },
  { z: 4,  cells: [-1, 0] },
  { z: 5,  cells: [0] }
];
for (const row of hullRows) {
  for (const dx of row.cells) shipCells.push({ x: dx, y: 1, z: row.z, color: 0x6e3f22, jitter: 0.16 });
  const first = row.cells[0], last = row.cells[row.cells.length - 1];
  for (const dx of row.cells) {
    if (dx === first || dx === last) shipCells.push({ x: dx, y: 2, z: row.z, color: 0xf2e3c0, jitter: 0.06 });
    else shipCells.push({ x: dx, y: 2, z: row.z, color: 0xc89a5e, jitter: 0.12 });
  }
}
// cabin
for (let x = -2; x <= 0; x++) for (let z = -5; z <= -3; z++) for (let y = 3; y <= 4; y++) {
  let color = 0xf2e3c0;
  if (x === -2 && y === 3 && z === -4) color = 0x3a2a1c;  // door (pier side)
  if (x === -2 && y === 4 && z === -3) color = 0x3a2a1c;  // window
  if (x === 0  && y === 4 && z === -4) color = 0x3a2a1c;  // window
  shipCells.push({ x, y, z, color, jitter: 0.08 });
}
for (let x = -2; x <= 0; x++) for (let z = -5; z <= -3; z++)
  shipCells.push({ x, y: 5, z, color: 0x7a4a2b, jitter: 0.1 });
// masts + flags
for (let y = 3; y <= 10; y++) shipCells.push({ x: 0, y, z: 0, color: 0x5d3d22, jitter: 0.1 });
for (let y = 3; y <= 8; y++) shipCells.push({ x: 0, y, z: 2, color: 0x5d3d22, jitter: 0.1 });
shipCells.push({ x: 0, y: 11, z: 0, color: 0xd43a2f });
shipCells.push({ x: 0, y: 9, z: 2, color: 0xd43a2f });
// sails (skip mast column)
const mainSail = [[4,3],[5,3],[6,2],[7,1],[8,1]];
const foreSail = [[4,2],[5,2],[6,1],[7,1]];
for (const [y, hw] of mainSail) {
  const color = y <= 5 ? 0xeadfbe : 0xf6efdc;
  for (let x = -hw; x <= hw; x++) { if (x === 0) continue; shipCells.push({ x, y, z: 0, color, jitter: 0.05 }); }
}
for (const [y, hw] of foreSail) {
  const color = y <= 5 ? 0xeadfbe : 0xf6efdc;
  for (let x = -hw; x <= hw; x++) { if (x === 0) continue; shipCells.push({ x, y, z: 2, color, jitter: 0.05 }); }
}
const shipGroup = new THREE.Group();
shipGroup.add(makeInstancedMesh(shipCells));
shipGroup.position.set(6, 0, 0);
scene.add(shipGroup);

// ---------- floating group (rowboat + buoys) ----------
const floatCells = [];
const boatRows = [
  { z: -2, cells: [0] }, { z: -1, cells: [-1, 0, 1] }, { z: 0, cells: [-1, 0, 1] },
  { z: 1, cells: [-1, 0, 1] }, { z: 2, cells: [0] }
];
for (const row of boatRows) {
  for (const dx of row.cells) floatCells.push({ x: dx, y: 1, z: row.z, color: 0x7a4a2b, jitter: 0.15 });
  for (const dx of row.cells) if (row.z === -2 || row.z === 2)
    floatCells.push({ x: dx, y: 2, z: row.z, color: 0xf2e3c0 });
}
// buoys at world (16, 12) and (22, -12) -> local coords relative to group at (3,0,8)
floatCells.push({ x: 13, y: 1, z: 4, color: 0xd43a2f, jitter: 0.1 });
floatCells.push({ x: 13, y: 2, z: 4, color: 0xf4f1e8 });
floatCells.push({ x: 19, y: 1, z: -20, color: 0xd43a2f, jitter: 0.1 });
floatCells.push({ x: 19, y: 2, z: -20, color: 0xf4f1e8 });
const floatGroup = new THREE.Group();
floatGroup.add(makeInstancedMesh(floatCells));
floatGroup.position.set(3, 0, 8);
scene.add(floatGroup);

// ---------- lighthouse islet ----------
const lhCells = [];
for (let x = 23; x <= 29; x++) for (let z = -23; z <= -17; z++) {
  const tower = x >= 25 && x <= 26 && z >= -21 && z <= -20;
  if (tower) continue;
  if (srand() < 0.55) lhCells.push({ x, y: 0, z, color: 0x8d939b, jitter: 0.22 });
  if (srand() < 0.35) lhCells.push({ x, y: 1, z, color: 0x7d838b, jitter: 0.22 });
}
for (let x = 25; x <= 26; x++) for (let z = -21; z <= -20; z++) {
  lhCells.push({ x, y: 2, z, color: 0xd43a2f, jitter: 0.08 });
  lhCells.push({ x, y: 3, z, color: 0xd43a2f, jitter: 0.08 });
  lhCells.push({ x, y: 4, z, color: 0xf4f1e8, jitter: 0.08 });
  lhCells.push({ x, y: 5, z, color: 0xf4f1e8, jitter: 0.08 });
  lhCells.push({ x, y: 6, z, color: 0xd43a2f, jitter: 0.08 });
  lhCells.push({ x, y: 7, z, color: 0xd43a2f, jitter: 0.08 });
  lhCells.push({ x, y: 8, z, color: 0x3a2a1c, jitter: 0.08 });
}
scene.add(makeInstancedMesh(lhCells));
const lightMesh = new THREE.Mesh(new THREE.BoxGeometry(1.1, 1.1, 1.1), new THREE.MeshBasicMaterial({ color: 0xffe27a }));
lightMesh.position.set(25.5, 9.3, -20.5);
scene.add(lightMesh);
const glowMesh = new THREE.Mesh(new THREE.BoxGeometry(2.3, 2.3, 2.3), new THREE.MeshBasicMaterial({ color: 0xffdf7a, transparent: true, opacity: 0.28 }));
glowMesh.position.set(25.5, 9.3, -20.5);
scene.add(glowMesh);

// ---------- voxel sun ----------
const sunCells = [];
for (let x = -32; x <= -28; x++) for (let z = -38; z <= -34; z++)
  sunCells.push({ x, y: 24, z, color: 0xffd75e, jitter: 0.05 });
for (let x = -31; x <= -29; x++) for (let z = -37; z <= -35; z++)
  sunCells.push({ x, y: 25, z, color: 0xffdf7a, jitter: 0.05 });
scene.add(makeInstancedMesh(sunCells, { castShadow: false, receiveShadow: false }));

// ---------- clouds ----------
const clouds = [];
function makeCloud(x, y, z) {
  const group = new THREE.Group();
  const mat = new THREE.MeshLambertMaterial({ color: 0xffffff });
  const cells = [];
  for (let dx = -2; dx <= 2; dx++) for (let dz = -1; dz <= 1; dz++)
    if (srand() < 0.75) cells.push([dx, 0, dz]);
  cells.push([0, 1, 0], [1, 1, 0]);
  for (const [dx, dy, dz] of cells) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), mat);
    m.position.set(dx, dy, dz);
    group.add(m);
  }
  group.scale.setScalar(1.6);
  group.position.set(x, y, z);
  scene.add(group);
  clouds.push({ group, speed: 0.5 + srand() * 0.7 });
}
makeCloud(-24, 23, -18); makeCloud(14, 26, -24); makeCloud(32, 24, 6); makeCloud(-6, 27, 18);

// ---------- seagulls ----------
const gulls = [];
function makeGull(phase) {
  const group = new THREE.Group();
  const mat = new THREE.MeshLambertMaterial({ color: 0xf6f6f2 });
  const dark = new THREE.MeshLambertMaterial({ color: 0x3a2a1c });
  const body = new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.5, 1.3), mat);
  body.castShadow = true;
  group.add(body);
  const head = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.5, 0.5), mat);
  head.position.set(0, 0.15, 0.75);
  group.add(head);
  const beak = new THREE.Mesh(new THREE.BoxGeometry(0.25, 0.25, 0.4), new THREE.MeshLambertMaterial({ color: 0xe88f4a }));
  beak.position.set(0, 0.15, 1.05);
  group.add(beak);
  const wingGeo = new THREE.BoxGeometry(1.5, 0.18, 0.7);
  const tipGeo = new THREE.BoxGeometry(0.4, 0.2, 0.7);
  const leftWing = new THREE.Group(); leftWing.position.set(-0.3, 0, 0);
  const lw = new THREE.Mesh(wingGeo, mat); lw.position.set(-0.75, 0, 0); leftWing.add(lw);
  const lt = new THREE.Mesh(tipGeo, dark); lt.position.set(-1.45, 0, 0); leftWing.add(lt);
  const rightWing = new THREE.Group(); rightWing.position.set(0.3, 0, 0);
  const rw = new THREE.Mesh(wingGeo, mat); rw.position.set(0.75, 0, 0); rightWing.add(rw);
  const rt = new THREE.Mesh(tipGeo, dark); rt.position.set(1.45, 0, 0); rightWing.add(rt);
  group.add(leftWing, rightWing);
  scene.add(group);
  gulls.push({ group, leftWing, rightWing, phase });
}
makeGull(0); makeGull(2.1); makeGull(4.2);

// ---------- animation ----------
const waterDummy = new THREE.Object3D();
const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);
  const dt = clock.getDelta();
  const t = clock.elapsedTime;

  for (let i = 0; i < waterCells.length; i++) {
    const c = waterCells[i];
    const amp = c.foam ? 0.55 : 1;
    waterDummy.position.set(
      c.x,
      amp * (0.16 * Math.sin(c.x * 0.42 + t * 1.6) * Math.cos(c.z * 0.38 + t * 1.25)
           + 0.05 * Math.sin((c.x + c.z) * 0.8 + t * 2.1)),
      c.z
    );
    waterDummy.updateMatrix();
    waterMesh.setMatrixAt(i, waterDummy.matrix);
  }
  waterMesh.instanceMatrix.needsUpdate = true;

  shipGroup.position.y = 0.28 * Math.sin(t * 1.25 + 1.2);
  shipGroup.rotation.z = 0.035 * Math.sin(t * 1.05 + 0.5);
  shipGroup.rotation.x = 0.02 * Math.sin(t * 0.85 + 2);

  floatGroup.position.y = 0.24 * Math.sin(t * 1.35 + 2.5);
  floatGroup.rotation.z = 0.03 * Math.sin(t * 1.15 + 1);
  floatGroup.rotation.x = 0.02 * Math.sin(t * 1.05);

  for (const c of clouds) {
    c.group.position.x += c.speed * dt;
    if (c.group.position.x > 55) c.group.position.x = -55;
  }

  for (const g of gulls) {
    const tt = t * 0.28 + g.phase;
    const r = 11;
    const x = 2 + Math.cos(tt) * r;
    const z = 2 + Math.sin(tt) * r * 0.75;
    const y = 12.5 + Math.sin(t * 1.7 + g.phase) * 1.6;
    g.group.position.set(x, y, z);
    const vx = -Math.sin(tt) * r, vz = Math.cos(tt) * r * 0.75;
    g.group.rotation.y = Math.atan2(vx, vz);
    const flap = Math.sin(t * 9 + g.phase) * 0.55;
    g.leftWing.rotation.z = -flap;
    g.rightWing.rotation.z = flap;
  }

  lightMesh.scale.setScalar(1 + 0.18 * Math.sin(t * 2.6));
  glowMesh.scale.setScalar(1 + 0.35 * Math.sin(t * 2.6));

  controls.update();
  renderer.render(scene, camera);
}
animate();

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
</script>
</body>
</html>
```

**How it works**
- Everything (water, island, pier, ship, lighthouse, sun) is built from `InstancedMesh` voxel cubes, so it renders in one draw call per region and is fast.
- The scene is animated immediately: voxel waves ripple, the ship and rowboat/buoys bob and roll, seagulls flap and circle the harbor, clouds drift, and the lighthouse light pulses.
- Orbit with the mouse (drag = orbit, scroll = zoom, right-drag = pan); the scene renders instantly on open.

**Notes**
- It needs an internet connection the first time to fetch Three.js from a CDN (unpkg). For a fully offline file, I can swap in a local `three.min.js` — just drop the script tag into the folder.
- If you want a specific change (e.g., a second sailing ship, a crane, more seagulls, a dusk palette), the voxel-builder structure makes it easy to tweak.