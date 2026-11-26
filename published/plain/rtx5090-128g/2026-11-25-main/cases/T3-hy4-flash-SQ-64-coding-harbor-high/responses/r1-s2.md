Paste this into a single `index.html` file and open it in Chrome:

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Voxel Harbor — Sailing Ship</title>
<style>
  html, body {
    height: 100%;
    margin: 0;
    overflow: hidden;
    background: #9ed3ef;
  }
  canvas { display: block; }
  #hud {
    position: fixed;
    left: 16px;
    top: 16px;
    padding: 12px 16px;
    background: rgba(7, 25, 40, 0.75);
    color: white;
    border-radius: 10px;
    font: 14px/1.45 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    pointer-events: none;
    user-select: none;
  }
  #hud strong { font-size: 18px; }
</style>

<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
  }
}
</script>
</head>
<body>
<div id="hud">
  <strong>Voxel Harbor</strong><br />
  Drag: orbit &nbsp;·&nbsp; Scroll: zoom &nbsp;·&nbsp; Right-drag: pan
</div>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x9ed3ef);
scene.fog = new THREE.Fog(0x9ed3ef, 90, 220);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 500);
camera.position.set(42, 28, 50);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.target.set(0, 5, 4);
controls.minDistance = 15;
controls.maxDistance = 130;
controls.maxPolarAngle = Math.PI * 0.49;
controls.update();

// Lighting
scene.add(new THREE.AmbientLight(0xffffff, 0.45));
scene.add(new THREE.HemisphereLight(0xbfe9ff, 0x6a5038, 0.65));

const sun = new THREE.DirectionalLight(0xfff0d5, 1.7);
sun.position.set(35, 55, 35);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -80;
sun.shadow.camera.right = 80;
sun.shadow.camera.top = 80;
sun.shadow.camera.bottom = -80;
sun.shadow.camera.near = 1;
sun.shadow.camera.far = 180;
scene.add(sun);
scene.add(sun.target);

// Shared voxel geometry
const cubeGeo = new THREE.BoxGeometry(1, 1, 1);

class VoxelBatch {
  constructor(parent, color, roughness = 0.85, metalness = 0) {
    this.parent = parent;
    this.items = [];
    this.material = new THREE.MeshStandardMaterial({ color, roughness, metalness });
  }

  add(x, y, z, sx = 1, sy = 1, sz = 1) {
    const matrix = new THREE.Matrix4().compose(
      new THREE.Vector3(x, y, z),
      new THREE.Quaternion(),
      new THREE.Vector3(sx, sy, sz)
    );
    this.items.push(matrix);
  }

  flush() {
    const mesh = new THREE.InstancedMesh(cubeGeo, this.material, this.items.length);
    for (let i = 0; i < this.items.length; i++) mesh.setMatrixAt(i, this.items[i]);
    mesh.instanceMatrix.needsUpdate = true;
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    this.parent.add(mesh);
    return mesh;
  }
}

// Water
const water = new THREE.Mesh(
  new THREE.PlaneGeometry(180, 140),
  new THREE.MeshStandardMaterial({ color: 0x2f9fbd, roughness: 0.35 })
);
water.rotation.x = -Math.PI / 2;
water.position.y = 0;
water.receiveShadow = true;
scene.add(water);

const waveLight = new VoxelBatch(scene, 0x9ee7ef, 0.5);
const waveDark = new VoxelBatch(scene, 0x207fa5, 0.5);

for (let x = -84; x <= 84; x += 5) {
  for (let z = -60; z <= 60; z += 8) {
    if (z > 14 && Math.abs(x) < 55) continue;
    const v = Math.sin(x * 0.23 + z * 0.37);
    if (v > 0.55) waveLight.add(x, 0.07, z, 2.4, 0.08, 0.7);
    else if (v < -0.65) waveDark.add(x, 0.05, z, 1.8, 0.06, 0.5);
  }
}
waveLight.flush().castShadow = false;
waveDark.flush().castShadow = false;

// Land / quay
const land = new THREE.Mesh(
  new THREE.BoxGeometry(110, 3, 34),
  new THREE.MeshStandardMaterial({ color: 0xbfae83, roughness: 1 })
);
land.position.set(0, 1.5, 32);
land.castShadow = true;
land.receiveShadow = true;
scene.add(land);

// Clouds
const cloud = new VoxelBatch(scene, 0xffffff, 0.9);
function cloudCluster(cx, cy, cz) {
  cloud.add(cx, cy, cz, 6, 2, 3);
  cloud.add(cx + 3, cy + 1, cz, 5, 2, 3);
  cloud.add(cx - 3, cy + 0.5, cz, 4, 2, 3);
}
cloudCluster(-34, 34, -38);
cloudCluster(24, 38, -48);
cloudCluster(48, 33, 12);
cloud.flush().castShadow = false;

// Ship group — animated gently
const ship = new THREE.Group();
scene.add(ship);

const hullDark = new VoxelBatch(ship, 0x3b2b24, 0.92);
const hullPlank = new VoxelBatch(ship, 0x8b5a2b, 0.9);
const hullTop = new VoxelBatch(ship, 0xb06a35, 0.85);
const stripe = new VoxelBatch(ship, 0xd94f3d, 0.75);
const deck = new VoxelBatch(ship, 0xc08a4a, 0.95);
const rail = new VoxelBatch(ship, 0x5a3424, 0.9);
const cabin = new VoxelBatch(ship, 0xd2a05a, 0.9);
const cabinRoof = new VoxelBatch(ship, 0x8d3d2e, 0.85);
const glow = new VoxelBatch(ship, 0xffd47a, 0.6);
const mast = new VoxelBatch(ship, 0x7a4b2b, 0.9);
const yard = new VoxelBatch(ship, 0x4a3020, 0.9);
const sail = new VoxelBatch(ship, 0xf2f0df, 0.9);
const sailShade = new VoxelBatch(ship, 0xdcd9c5, 0.9);
const flag = new VoxelBatch(ship, 0xd43b34, 0.8);
const gold = new VoxelBatch(ship, 0xe4b84c, 0.5, 0.25);

// Hull: tapered bow/stern, dark bottom, plank sides, deck
for (let x = -14; x <= 14; x++) {
  const ax = Math.abs(x);
  const half = ax <= 9 ? 5 : ax <= 12 ? 4 : ax === 13 ? 3 : 2;
  const low = Math.max(1, half - 1);

  for (let z = -low; z <= low; z++) {
    hullDark.add(x, 0.55, z, 1, 1, 1);
  }

  for (let z = -half + 1; z <= half - 1; z++) {
    deck.add(x, 2.55, z, 1, 0.35, 1);
  }

  hullPlank.add(x, 1.5, -half, 1, 1, 1);
  hullPlank.add(x, 1.5, half, 1, 1, 1);
  hullTop.add(x, 2.5, -half, 1, 1, 1);
  hullTop.add(x, 2.5, half, 1, 1, 1);

  stripe.add(x, 1.55, -half - 0.52, 1, 0.28, 0.12);
  stripe.add(x, 1.55, half + 0.52, 1, 0.28, 0.12);

  rail.add(x, 3.25, -half, 0.9, 0.35, 0.55);
  rail.add(x, 3.25, half, 0.9, 0.35, 0.55);
}

// Bow and stern caps
for (let z = -2; z <= 2; z++) {
  hullTop.add(-14, 2.5, z, 1, 1, 1);
  hullTop.add(14, 2.5, z, 1, 1, 1);
}
gold.add(15, 2.35, 0, 1, 0.7, 1);
gold.add(16, 2.65, 0, 1, 0.9, 0.7);

// Stern cabin
for (let x = -13; x <= -10; x++) {
  for (let z = -3; z <= 3; z++) {
    cabin.add(x, 3.75, z, 1, 1, 1);
    cabinRoof.add(x, 4.45, z, 1, 0.35, 1);
  }
}
for (let x = -12; x <= -11; x++) {
  glow.add(x, 3.9, 3.52, 0.75, 0.55, 0.12);
  glow.add(x, 3.9, -3.52, 0.75, 0.55, 0.12);
}

// Masts and square sails
function addMast(mx, topY, tiers) {
  for (let y = 4; y <= topY; y++) {
    mast.add(mx, y, 0, 0.6, 1, 0.6);
  }
  mast.add(mx, topY + 0.35, 0, 1.25, 0.25, 1.25);

  for (const tier of tiers) {
    const { bottom, top, half } = tier;
    for (let y = bottom; y <= top; y++) {
      for (let z = -half; z <= half; z++) {
        if ((y + z) % 6 === 0) sailShade.add(mx, y, z, 0.18, 0.86, 0.92);
        else sail.add(mx, y, z, 0.18, 0.86, 0.92);
      }
    }
    yard.add(mx, bottom - 0.4, 0, 0.35, 0.25, half * 2 + 2.2);
    yard.add(mx, top + 0.4, 0, 0.35, 0.25, half * 2 + 2.2);
  }
}

addMast(-1, 17, [
  { bottom: 8, top: 11, half: 3 },
  { bottom: 12, top: 15, half: 2 }
]);

addMast(8, 14, [
  { bottom: 7, top: 9, half: 2 },
  { bottom: 10, top: 12, half: 2 }
]);

flag.add(-2, 17.4, 0, 0.9, 0.45, 0.12);
flag.add(-3, 17.4, 0, 0.9, 0.45, 0.12);
flag.add(-4, 17.3, 0, 0.9, 0.4, 0.1);

// Rigging
const ropePoints = [];
function rope(a, b) {
  ropePoints.push(a[0], a[1], a[2], b[0], b[1], b[2]);
}
rope([-1, 17, 0], [14, 3, 0]);
rope([-1, 17, 0], [-14, 3, 0]);
rope([-1, 17, 0], [-1, 3, 4]);
rope([-1, 17, 0], [-1, 3, -4]);
rope([8, 14, 0], [14, 3, 0]);
rope([8, 14, 0], [-14, 3, 0]);
rope([8, 14, 0], [8, 3, 3]);
rope([8, 14, 0], [8, 3, -3]);

const ropeGeometry = new THREE.BufferGeometry();
ropeGeometry.setAttribute('position', new THREE.Float32BufferAttribute(ropePoints, 3));
const ropeLines = new THREE.LineSegments(
  ropeGeometry,
  new THREE.LineBasicMaterial({ color: 0x604832, transparent: true, opacity: 0.85 })
);
ship.add(ropeLines);

const shipBatches = [
  hullDark, hullPlank, hullTop, stripe, deck, rail,
  cabin, cabinRoof, glow, mast, yard, sail, sailShade, flag, gold
];
shipBatches.forEach(b => b.flush());

// Dock
const dockWood = new VoxelBatch(scene, 0xa87543, 0.92);
const dockEdge = new VoxelBatch(scene, 0x6e4427, 0.9);
const support = new VoxelBatch(scene, 0x5a3a25, 0.95);
const metalDock = new VoxelBatch(scene, 0x3f474b, 0.55, 0.4);
const gangway = new VoxelBatch(scene, 0xc08a4a, 0.9);

for (let x = -18; x <= 18; x++) {
  for (let z = 8; z <= 12; z++) {
    dockWood.add(x, 3.0, z, 1, 0.35, 1);
  }
  dockEdge.add(x, 3.15, 7.55, 1, 0.25, 0.35);
  dockEdge.add(x, 3.15, 12.45, 1, 0.25, 0.35);
}

for (let x = -18; x <= 18; x += 3) {
  support.add(x, 1.4, 8.4, 0.65, 2.8, 0.65);
  support.add(x, 1.4, 12.4, 0.65, 2.8, 0.65);
}

// Gangway from ship to dock
for (let z = 5.5; z <= 7.5; z += 0.5) {
  gangway.add(6, 3.08, z, 3.0, 0.22, 0.45);
}
for (const x of [4.5, 7.5]) {
  for (const z of [5.5, 7.5]) {
    dockEdge.add(x, 3.6, z, 0.25, 1.2, 0.25);
  }
}
dockEdge.add(4.5, 4.2, 6.5, 0.25, 0.25, 2.5);
dockEdge.add(7.5, 4.2, 6.5, 0.25, 0.25, 2.5);

// Bollards
for (const x of [-14, -5, 10, 16]) {
  metalDock.add(x, 3.55, 8, 0.5, 0.7, 0.5);
  metalDock.add(x, 3.75, 8, 0.8, 0.2, 0.8);
}

// Crates and barrels
const crate = new VoxelBatch(scene, 0xc58b4b, 0.92);
const crateDark = new VoxelBatch(scene, 0x74462b, 0.9);
const barrel = new VoxelBatch(scene, 0x9d6b39, 0.9);
const barrelBand = new VoxelBatch(scene, 0x3f474b, 0.6, 0.3);

function addCrate(x, z, y) {
  crate.add(x, y, z, 1.4, 1.4, 1.4);
  crateDark.add(x, y + 0.72, z, 1.45, 0.12, 1.45);
  crateDark.add(x, y - 0.72, z, 1.45, 0.12, 1.45);
}
addCrate(-15, 11, 3.9);
addCrate(-15, 11, 5.3);
addCrate(-12, 12, 3.9);
addCrate(9, 11, 3.9);
addCrate(12, 10, 3.9);
addCrate(12, 10, 5.3);

function addBarrel(x, z) {
  barrel.add(x, 3.7, z, 1.0, 1.1, 1.0);
  barrelBand.add(x, 3.7, z, 1.08, 0.14, 1.08);
}
addBarrel(-8, 11);
addBarrel(-7, 12);
addBarrel(14, 12);

// Mooring ropes
const tiePoints = [];
function tie(a, b) {
  tiePoints.push(a[0], a[1], a[2], b[0], b[1], b[2]);
}
tie([6, 3.25, 5], [6, 3.7, 8]);
tie([10, 3.25, 5], [10, 3.7, 8]);
tie([-5, 3.25, 5], [-5, 3.7, 8]);

const tieGeometry = new THREE.BufferGeometry();
tieGeometry.setAttribute('position', new THREE.Float32BufferAttribute(tiePoints, 3));
scene.add(new THREE.LineSegments(tieGeometry, new THREE.LineBasicMaterial({ color: 0x6b5a42 })));

const dockBatches = [dockWood, dockEdge, support, metalDock, gangway, crate, crateDark, barrel, barrelBand];
dockBatches.forEach(b => b.flush());

// Warehouse on the quay
const warehouseStone = new VoxelBatch(scene, 0x9a8b72, 0.95);
const warehouse = new VoxelBatch(scene, 0xb86b4a, 0.95);
const warehouseRoof = new VoxelBatch(scene, 0x7a3c34, 0.9);
const door = new VoxelBatch(scene, 0x5c3b2c, 0.9);
const windowGlow = new VoxelBatch(scene, 0xffd36b, 0.55);

for (let x = -24; x <= -8; x++) {
  for (let z = 18; z <= 24; z++) {
    warehouseStone.add(x, 3.25, z, 1, 0.5, 1);
    warehouseRoof.add(x, 9.7, z, 1, 0.4, 1);
  }
}

for (let y = 4; y <= 9; y++) {
  for (let x = -24; x <= -8; x++) {
    warehouse.add(x, y, 18, 1, 1, 1);
    warehouse.add(x, y, 24, 1, 1, 1);
  }
  for (let z = 19; z <= 23; z++) {
    warehouse.add(-24, y, z, 1, 1, 1);
    warehouse.add(-8, y, z, 1, 1, 1);
  }
}

door.add(-16, 4.25, 24.55, 2.5, 1.5, 0.12);
for (const x of [-21, -18, -12, -10]) {
  windowGlow.add(x, 7, 24.55, 1.1, 0.9, 0.12);
}

[warehouseStone, warehouse, warehouseRoof, door, windowGlow].forEach(b => b.flush());

// Harbor crane
const craneWood = new VoxelBatch(scene, 0x5b4028, 0.9);
const craneMetal = new VoxelBatch(scene, 0x40494d, 0.55, 0.35);
for (let y = 4; y <= 11; y++) craneWood.add(22, y, 12, 0.8, 1, 0.8);
craneMetal.add(21.5, 11.2, 12, 9, 0.35, 0.55);
craneMetal.add(25, 9.4, 12, 0.18, 2.8, 0.18);
craneMetal.add(25, 7.9, 12, 0.55, 0.55, 0.55);
craneWood.add(19, 5.5, 12, 0.25, 3.8, 0.25);
craneWood.add(25, 5.5, 12, 0.25, 3.8, 0.25);
[craneWood, craneMetal].forEach(b => b.flush());

// Lighthouse
const lighthouseWhite = new VoxelBatch(scene, 0xf3f1e8, 0.8);
const lighthouseRed = new VoxelBatch(scene, 0xd94f3d, 0.8);
const lamp = new VoxelBatch(scene, 0xffd36b, 0.35);
const lampRoof = new VoxelBatch(scene, 0x444444, 0.7);
lighthouseWhite.add(32, 3.25, 28, 2.8, 0.5, 2.8);
for (let y = 4; y <= 14; y++) {
  const b = Math.floor((y - 4) / 2) % 2 === 0 ? lighthouseWhite : lighthouseRed;
  b.add(32, y, 28, 2.2, 1, 2.2);
}
lamp.add(32, 15.1, 28, 2.4, 0.8, 2.4);
lampRoof.add(32, 15.8, 28, 2.8, 0.5, 2.8);
[lighthouseWhite, lighthouseRed, lamp, lampRoof].forEach(b => b.flush());

// Buoys
const buoyRed = new VoxelBatch(scene, 0xd94f3d, 0.7);
const buoyWhite = new VoxelBatch(scene, 0xf3f1e8, 0.7);
buoyRed.add(-26, 0.35, -12, 1, 0.7, 1);
buoyWhite.add(-26, 0.78, -12, 0.8, 0.2, 0.8);
buoyRed.add(24, 0.35, -18, 1, 0.7, 1);
buoyWhite.add(24, 0.78, -18, 0.8, 0.2, 0.8);
[buoyRed, buoyWhite].forEach(b => {
  const mesh = b.flush();
  mesh.castShadow = false;
});

// Animation
const clock = new THREE.Clock();

function animate() {
  const t = clock.getElapsedTime();
  ship.position.y = Math.sin(t * 0.8) * 0.14;
  ship.rotation.z = Math.sin(t * 0.55) * 0.008;
  ship.rotation.x = Math.cos(t * 0.65) * 0.005;

  controls.update();
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
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