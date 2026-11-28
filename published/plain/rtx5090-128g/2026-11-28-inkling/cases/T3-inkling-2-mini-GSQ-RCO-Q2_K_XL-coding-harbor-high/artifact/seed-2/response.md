Here's a complete, self-contained voxel harbor scene (Three.js). Paste it into a single `.html` file and open it in Chrome — it renders immediately and is fully orbitable with the mouse.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Voxel Harbor — Sailing Ship</title>
<style>
  html, body { margin: 0; height: 100%; overflow: hidden; background: #7ec8e3;
    font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; }
  #app { position: fixed; inset: 0; }
  .hud { position: fixed; z-index: 10; color: #ffffff;
    background: rgba(12, 24, 34, 0.55); padding: 10px 14px; border-radius: 10px;
    backdrop-filter: blur(6px); box-shadow: 0 2px 12px rgba(0,0,0,.2); }
  .hud.title { top: 14px; left: 14px; }
  .hud.title h1 { margin: 0; font-size: 18px; font-weight: 700; letter-spacing: .4px; }
  .hud.title p { margin: 4px 0 0; font-size: 12px; opacity: .85; }
  .hud.hint { bottom: 14px; left: 14px; font-size: 12px; opacity: .92; line-height: 1.5; }
  .hud.controls { top: 14px; right: 14px; display: flex; gap: 8px; background: transparent; box-shadow: none; padding: 0; }
  .hud.controls button { background: rgba(12, 24, 34, 0.55); border: 1px solid rgba(255,255,255,.25);
    color: #fff; padding: 8px 12px; border-radius: 8px; cursor: pointer; font-size: 12px; backdrop-filter: blur(6px); }
  .hud.controls button:hover { background: rgba(40, 60, 80, 0.7); }
</style>
<script type="importmap">
{ "imports": {
    "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
    "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
} }
</script>
</head>
<body>
<div id="app"></div>
<div class="hud title"><h1>Voxel Harbor</h1><p>A sailing ship calling at the quay</p></div>
<div class="hud hint">Drag to orbit &middot; Scroll to zoom &middot; Right-drag to pan<br/>three.js loads from CDN &mdash; needs internet</div>
<div class="hud controls">
  <button id="resetBtn" type="button">Reset view</button>
  <button id="pauseBtn" type="button">Pause</button>
</div>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

// ---------- setup ----------
const app = document.getElementById('app');
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
app.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x7ec8e3);
scene.fog = new THREE.Fog(0x7ec8e3, 55, 130);

const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 400);
const START_POS = new THREE.Vector3(20, 13, 24);
const START_TARGET = new THREE.Vector3(1.5, 2.2, -0.5);
camera.position.copy(START_POS);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.copy(START_TARGET);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.minDistance = 8;
controls.maxDistance = 65;
controls.maxPolarAngle = Math.PI * 0.495;

// lights
scene.add(new THREE.HemisphereLight(0xcfe9ff, 0x40573f, 0.9));
const sunLight = new THREE.DirectionalLight(0xfff0d0, 1.8);
sunLight.position.set(18, 26, 14);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
sunLight.shadow.camera.left = -26; sunLight.shadow.camera.right = 26;
sunLight.shadow.camera.top = 26; sunLight.shadow.camera.bottom = -26;
sunLight.shadow.camera.near = 2; sunLight.shadow.camera.far = 80;
sunLight.shadow.bias = -0.0004;
sunLight.shadow.camera.updateProjectionMatrix();
scene.add(sunLight);

// ---------- voxel helpers ----------
const lambertCache = new Map();
function lambert(color) {
  if (!lambertCache.has(color)) lambertCache.set(color, new THREE.MeshLambertMaterial({ color }));
  return lambertCache.get(color);
}

class VoxelBuilder {
  constructor() { this.buckets = new Map(); }
  add(x, y, z, w, h, d, color) {
    const g = new THREE.BoxGeometry(w, h, d);
    g.translate(x, y, z);
    if (!this.buckets.has(color)) this.buckets.set(color, []);
    this.buckets.get(color).push(g);
  }
  build(opts = {}) {
    const cast = opts.cast !== false, receive = opts.receive !== false;
    const group = new THREE.Group();
    for (const [color, geos] of this.buckets) {
      const merged = mergeGeometries(geos, false);
      const mesh = new THREE.Mesh(merged, lambert(color));
      mesh.castShadow = cast; mesh.receiveShadow = receive;
      group.add(mesh);
      geos.forEach(g => g.dispose());
    }
    this.buckets.clear();
    return group;
  }
}

function rope(a, b, color, width) {
  const dir = new THREE.Vector3().subVectors(b, a);
  const len = dir.length();
  const m = new THREE.Mesh(new THREE.BoxGeometry(width, len, width), lambert(color));
  m.position.copy(a).addScaledVector(dir, 0.5);
  m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir.normalize());
  m.castShadow = true;
  return m;
}

// ---------- water ----------
const waterTiles = [];
const waterGroup = new THREE.Group();
const waterGeo = new THREE.BoxGeometry(1, 1, 1);
const waterMatA = new THREE.MeshLambertMaterial({ color: 0x2f6f9e });
const waterMatB = new THREE.MeshLambertMaterial({ color: 0x3a7fb5 });
const W_COLS = 30, D_ROWS = 16;
for (let i = 0; i < W_COLS; i++) {
  for (let j = 0; j < D_ROWS; j++) {
    const mesh = new THREE.Mesh(waterGeo, (i + j) % 2 ? waterMatA : waterMatB);
    const x = i - (W_COLS - 1) / 2;   // -14.5 .. 14.5
    const z = j - 7.5;                // -7.5 .. 7.5
    mesh.scale.set(0.94, 1, 0.94);
    mesh.position.set(x, -0.5, z);
    mesh.receiveShadow = true;
    waterGroup.add(mesh);
    waterTiles.push({ mesh, phase: i * 0.55 + j * 0.38 });
  }
}
scene.add(waterGroup);

// ---------- quay (back strip) ----------
const quay = new VoxelBuilder();
const quayColor = 0x8f9aa6, quayEdge = 0x75808d;
for (let i = 0; i < 32; i++) {
  const x = i - 15.5;
  for (let r = 0; r < 4; r++) {
    const z = -12 + r + 0.5;
    quay.add(x, 0.7, z, 1, 1.4, 1, r === 3 ? quayEdge : quayColor);
  }
}
scene.add(quay.build());

// lighthouse
const lighthouse = new VoxelBuilder();
lighthouse.add(-9, 1.85, -10, 2.4, 0.9, 2.4, 0x6f7885);
const stripe = [0xf2efe6, 0xc94f3d];
for (let k = 0; k < 5; k++) lighthouse.add(-9, 2.3 + k * 1.0, -10, 1.5, 1.0, 1.5, stripe[k % 2]);
lighthouse.add(-9, 6.95, -10, 1.9, 0.5, 1.9, 0x3a3f4a);
scene.add(lighthouse.build());

const lighthouseLight = new THREE.Mesh(new THREE.BoxGeometry(0.62, 0.5, 0.62),
  new THREE.MeshLambertMaterial({ color: 0xffd166, emissive: 0xffd166, emissiveIntensity: 2.0 }));
lighthouseLight.position.set(-9, 7.45, -10);
scene.add(lighthouseLight);
const lightGlow = new THREE.PointLight(0xffd166, 30, 14, 2);
lightGlow.position.set(-9, 7.5, -10);
scene.add(lightGlow);

// house
const house = new VoxelBuilder();
house.add(7.5, 2.5, -10.2, 3.2, 2.2, 2.6, 0xf0e6cf);
house.add(7.5, 3.95, -10.2, 3.6, 0.7, 3.0, 0x8a3b2e);
house.add(6.9, 4.35, -10.5, 0.5, 0.8, 0.5, 0x6f6f6f);
scene.add(house.build());

// crates & barrels
const cargo = new VoxelBuilder();
cargo.add(2.6, 1.85, -9.6, 0.9, 0.9, 0.9, 0xc9a35f);
cargo.add(2.6, 2.7, -9.6, 0.8, 0.8, 0.8, 0xb98d4e);
cargo.add(4.5, 1.825, -9.2, 0.75, 0.85, 0.75, 0x7a4a2c);
cargo.add(5.4, 1.825, -9.2, 0.75, 0.85, 0.75, 0x8a5a33);
scene.add(cargo.build());

// quay lanterns
const lanternPosts = new VoxelBuilder();
for (const x of [-4.5, 1.5]) lanternPosts.add(x, 2.15, -8.6, 0.22, 1.5, 0.22, 0x3a2c1c);
scene.add(lanternPosts.build());
const lanternLights = [];
for (const x of [-4.5, 1.5]) {
  const lm = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.34, 0.42),
    new THREE.MeshLambertMaterial({ color: 0xffd166, emissive: 0xffd166, emissiveIntensity: 1.4 }));
  lm.position.set(x, 3.05, -8.6);
  scene.add(lm);
  lanternLights.push(lm);
}

// ---------- dock ----------
const dock = new VoxelBuilder();
const plankColors = [0x8a5a33, 0x7d4f2b, 0x94633a];
for (let x = -2; x <= 2; x++) {
  for (let z = -7; z <= 4; z++) {
    const c = plankColors[(Math.abs(x) + Math.abs(z)) % 3];
    dock.add(x, 1.05, z, 1, 0.35, 0.92, c);
  }
}
for (const px of [-2.3, 2.3]) {
  for (const pz of [-7.5, 3.5]) dock.add(px, -0.2, pz, 0.4, 2.5, 0.4, 0x4a2c1a);
}
dock.add(2.0, 1.5, 2.5, 0.45, 0.5, 0.45, 0x2e2a26);
dock.add(2.0, 1.5, -2.5, 0.45, 0.5, 0.45, 0x2e2a26);
scene.add(dock.build());

// ---------- ship ----------
const shipPos = new THREE.Vector3(5.6, 1.2, 0.5);
const shipGroup = new THREE.Group();
const ship = new VoxelBuilder();

const widths = [3, 4, 4, 5, 5, 5, 5, 5, 4, 3, 2, 1];
const hullColor = 0x6b3f2a, red = 0xc94f3d, wood = 0x8a5a33,
      darkWood = 0x4a2c1a, mast = 0x3d2a1a;

for (let i = 0; i < widths.length; i++) {
  const w = widths[i];
  const z = i - 5.5;
  const h = (i === 0) ? 3 : (i === widths.length - 1) ? 1 : 2;
  for (let k = 0; k < w; k++) {
    const x = k - (w - 1) / 2;
    for (let y = 0; y < h; y++) ship.add(x, y - 2, z, 1, 1, 1, hullColor);
    ship.add(x, 0.05, z, 1, 0.3, 1, wood);      // deck
    ship.add(x, -0.5, z, 1, 0.3, 1, red);       // red stripe
  }
}
ship.add(0, 0.7, -5.5, 3, 1.0, 1.4, darkWood);   // stern castle
ship.add(0, 6.45, -1.6, 0.5, 0.5, 0.5, mast);     // main cap
ship.add(0, 5.4, 2.3, 0.5, 0.5, 0.5, mast);       // fore cap

// masts
function mastColumn(z, top) {
  for (let y = 0.2; y < top; y += 1) ship.add(0, y + 0.5, z, 0.45, 1.0, 0.45, mast);
}
mastColumn(2.3, 5.4);   // fore
mastColumn(-1.6, 6.4);  // main

// yards
ship.add(0, 5.6, -1.6, 4.6, 0.18, 0.18, mast);
ship.add(0, 4.75, 2.3, 3.6, 0.18, 0.18, mast);

// sails
const sailColors = [0xf2e3c0, 0xead9b4];
[[1.25, 4], [2.25, 5], [3.25, 5], [4.25, 4], [5.15, 3]].forEach(([y, w], idx) =>
  ship.add(0, y, -1.6, w, 0.95, 0.2, sailColors[idx % 2]));
[[1.25, 3], [2.25, 4], [3.25, 4], [4.25, 3]].forEach(([y, w], idx) =>
  ship.add(0, y, 2.3, w, 0.95, 0.2, sailColors[(idx + 1) % 2]));

// jib (staircase triangle)
[[4.7, 2.9, 1.6], [3.8, 3.8, 1.4], [2.9, 4.7, 1.2], [2.0, 5.6, 1.0], [1.2, 6.4, 0.85]]
  .forEach(([y, z, w]) => ship.add(0, y, z, w, 0.55, 0.9, 0xf2e3c0));

const shipMeshes = ship.build();
shipGroup.add(shipMeshes);

// rigging & bowsprit
shipGroup.add(rope(new THREE.Vector3(0, 6.4, -1.6), new THREE.Vector3(0, 1.2, -5.9), 0x2a2118, 0.07));
shipGroup.add(rope(new THREE.Vector3(0, 6.4, -1.6), new THREE.Vector3(0, 5.4, 2.3), 0x2a2118, 0.07));
shipGroup.add(rope(new THREE.Vector3(0, 5.4, 2.3), new THREE.Vector3(0, 1.15, 7.2), 0x2a2118, 0.07));
shipGroup.add(rope(new THREE.Vector3(0, 0.6, 5.4), new THREE.Vector3(0, 1.15, 7.3), 0x3d2a1a, 0.2));

// cleats + mooring ropes
const cleatGeo = new THREE.BoxGeometry(0.3, 0.25, 0.3);
for (const zc of [2.6, -2.6]) {
  const cleat = new THREE.Mesh(cleatGeo, lambert(0x2e2a26));
  cleat.position.set(-2.3, 0.35, zc);
  cleat.castShadow = true;
  shipGroup.add(cleat);
}
shipGroup.add(rope(new THREE.Vector3(2.0 - 5.6, 1.5 - 1.2, 2.5 - 0.5),
                   new THREE.Vector3(-2.3, 0.35, 2.6), 0x2a2118, 0.07));
shipGroup.add(rope(new THREE.Vector3(2.0 - 5.6, 1.5 - 1.2, -2.5 - 0.5),
                   new THREE.Vector3(-2.3, 0.35, -2.6), 0x2a2118, 0.07));

// flag
const flagGroup = new THREE.Group();
flagGroup.position.set(0, 6.75, -1.6);
const flagGeo = new THREE.BoxGeometry(1.3, 0.7, 0.12);
flagGeo.translate(0.65, 0, 0);
const flag = new THREE.Mesh(flagGeo, lambert(0xd43d2a));
flag.castShadow = true;
flagGroup.add(flag);
shipGroup.add(flagGroup);

// bow lantern
const bowLamp = new THREE.Mesh(new THREE.BoxGeometry(0.36, 0.36, 0.36),
  new THREE.MeshLambertMaterial({ color: 0xffb347, emissive: 0xffb347, emissiveIntensity: 1.6 }));
bowLamp.position.set(0, -0.95, 5.5);
shipGroup.add(bowLamp);

shipGroup.position.copy(shipPos);
scene.add(shipGroup);

// ---------- buoys ----------
const buoys = [];
function makeBuoy(x, z, c1, c2) {
  const g = new THREE.Group();
  const b1 = new THREE.Mesh(new THREE.BoxGeometry(0.55, 0.4, 0.55), lambert(c1));
  const b2 = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.35, 0.4), lambert(c2));
  b2.position.y = 0.35;
  g.add(b1, b2);
  g.traverse(o => { if (o.isMesh) o.castShadow = true; });
  g.position.set(x, 0.2, z);
  scene.add(g);
  buoys.push({ g, phase: Math.random() * 6.28 });
}
makeBuoy(-6.5, 4.5, 0xd43d2a, 0xf5f5f5);
makeBuoy(9.5, 5.2, 0xf5f5f5, 0x2a2118);

// ---------- seagulls ----------
const gulls = [];
function makeGull(phase, radius, height, speed) {
  const g = new THREE.Group();
  const body = new THREE.Mesh(new THREE.BoxGeometry(0.32, 0.28, 0.62), lambert(0x3a3a46));
  body.castShadow = true;
  const rightGeo = new THREE.BoxGeometry(0.75, 0.08, 0.36); rightGeo.translate(0.375, 0, 0);
  const right = new THREE.Mesh(rightGeo, lambert(0x9aa2ad)); right.position.set(0.15, 0, 0);
  const leftGeo = new THREE.BoxGeometry(0.75, 0.08, 0.36); leftGeo.translate(-0.375, 0, 0);
  const left = new THREE.Mesh(leftGeo, lambert(0x9aa2ad)); left.position.set(-0.15, 0, 0);
  right.castShadow = left.castShadow = true;
  g.add(body, right, left);
  scene.add(g);
  gulls.push({ g, right, left, phase, radius, height, speed });
}
makeGull(0, 8, 9.5, 0.5);
makeGull(2.1, 9.5, 8.6, 0.42);
makeGull(4.2, 7.5, 10.3, 0.55);

// ---------- clouds & sun ----------
const clouds = [];
function makeCloud(x, y, z, speed) {
  const b = new VoxelBuilder();
  b.add(0, 0, 0, 2.6, 1.1, 1.4, 0xffffff);
  b.add(-1.4, 0.35, 0.2, 1.4, 0.9, 1.1, 0xeef3f8);
  b.add(1.4, 0.3, -0.2, 1.5, 0.9, 1.2, 0xf4f8fb);
  b.add(0.3, 0.9, 0.3, 1.7, 0.8, 1.0, 0xffffff);
  const g = b.build({ cast: true, receive: false });
  g.position.set(x, y, z);
  scene.add(g);
  clouds.push({ g, speed });
}
makeCloud(-12, 13.5, -6, 0.5);
makeCloud(2, 15.0, -11, 0.35);
makeCloud(11, 12.5, 3, 0.6);
makeCloud(-3, 14.0, 7, 0.45);

const sun = new VoxelBuilder();
sun.add(0, 0, 0, 2.6, 2.6, 2.6, 0xffd94d);
const sunMesh = sun.build({ cast: false, receive: false });
sunMesh.position.set(-16, 17, -16);
scene.add(sunMesh);

// ---------- animation ----------
const clock = new THREE.Clock();
let elapsed = 0;
let paused = false;

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  if (!paused) elapsed += dt;
  const t = elapsed;

  for (const w of waterTiles)
    w.mesh.position.y = -0.5 + Math.sin(t * 1.6 + w.phase) * 0.14;

  shipGroup.position.y = 1.2 + Math.sin(t * 0.85) * 0.12;
  shipGroup.rotation.z = Math.sin(t * 0.6) * 0.03;
  shipGroup.rotation.x = Math.sin(t * 0.5 + 1.3) * 0.025;

  flagGroup.rotation.y = Math.sin(t * 2.4) * 0.35;
  flag.scale.x = 1 + 0.12 * Math.sin(t * 6);

  bowLamp.material.emissiveIntensity = 1.6 + Math.sin(t * 2.5) * 1.0;
  lighthouseLight.material.emissiveIntensity = 2.0 + Math.sin(t * 2.5 + 1) * 1.4;
  lightGlow.intensity = 30 + Math.sin(t * 2.5 + 1) * 18;
  for (const lm of lanternLights) lm.material.emissiveIntensity = 1.4 + Math.sin(t * 2 + 2) * 0.5;

  for (const b of buoys) {
    b.g.position.y = 0.2 + Math.sin(t * 1.5 + b.phase) * 0.14;
    b.g.rotation.z = Math.sin(t * 1.2 + b.phase) * 0.08;
  }

  for (const gl of gulls) {
    const a = t * gl.speed + gl.phase;
    gl.g.position.set(Math.cos(a) * gl.radius, gl.height + Math.sin(t * 0.5 + gl.phase) * 0.7,
                      Math.sin(a) * gl.radius + 1);
    gl.g.rotation.y = Math.atan2(-Math.sin(a), Math.cos(a));
    const flap = 0.35 + Math.sin(t * 9 + gl.phase) * 0.55;
    gl.right.rotation.z = flap;
    gl.left.rotation.z = -flap;
  }

  if (!paused) {
    for (const c of clouds) {
      c.g.position.x += c.speed * dt;
      if (c.g.position.x > 28) c.g.position.x = -28;
    }
  }

  controls.update();
  renderer.render(scene, camera);
}
animate();

// ---------- UI ----------
const pauseBtn = document.getElementById('pauseBtn');
pauseBtn.addEventListener('click', () => {
  paused = !paused;
  pauseBtn.textContent = paused ? 'Resume' : 'Pause';
});
document.getElementById('resetBtn').addEventListener('click', () => {
  camera.position.copy(START_POS);
  controls.target.copy(START_TARGET);
});

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
</script>
</body>
</html>
```

**What you get**
- Voxel scene: animated checkerboard water (bobbing cubes), a two-mast sailing ship (tapered hull, red stripe, deck, stern castle, sails, jib, bowsprit, rigging, waving flag, glowing bow lantern, mooring ropes to the dock), a wooden dock with posts/bollards, a stone quay with a striped lighthouse (pulsing light), a voxel house, crates, barrels, lanterns, bobbing buoys, drifting clouds, a voxel sun, and three flapping seagulls circling the ship.
- Mouse controls: drag to orbit, scroll to zoom, right-drag to pan (with damping). Buttons: Reset view and Pause/Resume.

**Notes**
- It needs internet to load three.js from the CDN. If you want it fully offline, download `three.module.js` and the `examples/jsm/` folder (`OrbitControls.js`, `BufferGeometryUtils.js`) next to the HTML file and update the importmap — I can do that if you'd like.
- To change the mood, tweak the water colors/speeds, fog color, or the `sunLight` intensity. If you want the ship sailing (instead of moored), I can make it glide past the dock on a loop — just ask.