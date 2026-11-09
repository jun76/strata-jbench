Save this as a `.html` file (for example `harbor.html`) and open it in Chrome. It uses Three.js from a CDN, so the browser needs internet access.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Voxel Harbor — A Sailing Ship Calling At Harbor</title>
<style>
  html, body {
    margin: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
    background: #9fd3ff;
    font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
    touch-action: none;
  }
  canvas { display: block; }
  #ui {
    position: fixed;
    top: 14px;
    left: 14px;
    color: white;
    background: rgba(0, 0, 0, 0.28);
    padding: 10px 14px;
    border-radius: 10px;
    font-size: 14px;
    line-height: 1.35;
    pointer-events: none;
    text-shadow: 0 1px 4px rgba(0,0,0,0.35);
    user-select: none;
  }
  #ui b {
    display: block;
    font-size: 16px;
    margin-bottom: 4px;
  }
</style>
</head>
<body>
<div id="ui">
  <b>Sailing Ship Calling At Harbor</b>
  Drag to orbit &bull; Scroll to zoom &bull; Double-click resets view
</div>

<script type="module">
import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js";

// Renderer
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Scene
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x8fc8f0);
scene.fog = new THREE.Fog(0xbfdfff, 110, 420);

// Camera
const camera = new THREE.PerspectiveCamera(
  48,
  window.innerWidth / window.innerHeight,
  0.1,
  800
);

// Lights
scene.add(new THREE.HemisphereLight(0xc6eaff, 0x365464, 1.0));

const sun = new THREE.DirectionalLight(0xfffbdd, 1.05);
sun.position.set(100, 160, -80);
scene.add(sun);

const fill = new THREE.DirectionalLight(0x95cfff, 0.32);
fill.position.set(-90, 60, 90);
scene.add(fill);

// Palette
const C = {
  water: 0x2f7e99,
  grass: 0x5a8b40,
  grassDark: 0x446b32,
  flower: 0xd9f0a2,
  dock: 0x91683e,
  dockDark: 0x664628,
  wood: 0x8c6238,
  woodDark: 0x55371f,
  stone: 0x8a8d91,
  stoneDark: 0x5f6266,
  brick: 0xa95545,
  brickDark: 0x7d3e33,
  roof: 0x6b4636,
  roofLight: 0xa2624b,
  hullDark: 0x432e21,
  hullLight: 0x714934,
  deck: 0xc4a074,
  mast: 0x64523c,
  sail: 0xf4ead8,
  sailShade: 0xd9c9ab,
  rope: 0x3c2c20,
  glow: 0xffdf6e,
  lamp: 0xfff3b2,
  window: 0x9fd7e6,
  crateRed: 0xa84136,
  crateBlue: 0x396ea5,
  crateGreen: 0x4f8b3a,
  white: 0xf4f4f2,
  red: 0xc0392b,
  gold: 0xf5c43c,
  black: 0x1f1f1f,
  foam: 0xeafff8
};

// Shared geometry and materials
const unit = new THREE.BoxGeometry(1, 1, 1);
const lambertMap = new Map();
const basicMap = new Map();

function lambertMaterial(color) {
  let m = lambertMap.get(color);
  if (!m) {
    m = new THREE.MeshLambertMaterial({ color });
    lambertMap.set(color, m);
  }
  return m;
}

function basicMaterial(color) {
  let m = basicMap.get(color);
  if (!m) {
    m = new THREE.MeshBasicMaterial({ color });
    basicMap.set(color, m);
  }
  return m;
}

// Add voxel using y as bottom face.
// x, z are center; sx = size along x, sz = size along z, sy = height.
function addVoxel(group, x, yBottom, z, color, sx = 1, sz = 1, sy = 1, basic = false) {
  const mesh = new THREE.Mesh(unit, basic ? basicMaterial(color) : lambertMaterial(color));
  mesh.position.set(x, yBottom + sy / 2, z);
  mesh.scale.set(sx, sy, sz);
  group.add(mesh);
  return mesh;
}

// Add voxel using y as center face.
function addRotVoxel(
  group,
  x,
  yCenter,
  z,
  color,
  sx = 1,
  sz = 1,
  sy = 1,
  basic = false,
  rx = 0,
  ry = 0,
  rz = 0
) {
  const mesh = new THREE.Mesh(unit, basic ? basicMaterial(color) : lambertMaterial(color));
  mesh.position.set(x, yCenter, z);
  mesh.scale.set(sx, sy, sz);
  mesh.rotation.set(rx, ry, rz);
  group.add(mesh);
  return mesh;
}

// Visible sun
const sunMesh = new THREE.Mesh(
  unit,
  new THREE.MeshBasicMaterial({ color: 0xfff3b0, fog: false })
);
sunMesh.position.set(180, 185, -140);
sunMesh.scale.set(20, 20, 20);
scene.add(sunMesh);

// Animated water surface
function createWater() {
  const geo = new THREE.PlaneGeometry(420, 330, 72, 56);
  geo.rotateX(-Math.PI / 2);

  const base = Float32Array.from(geo.attributes.position.array);

  const mat = new THREE.MeshStandardMaterial({
    color: C.water,
    roughness: 0.72,
    metalness: 0.04,
    flatShading: true,
    transparent: true,
    opacity: 0.9
  });

  const mesh = new THREE.Mesh(geo, mat);
  mesh.position.set(10, -0.1, -128);
  scene.add(mesh);

  geo.computeVertexNormals();

  return { geo, base, mesh };
}
const waterObj = createWater();

// Land and dock
addVoxel(scene, 0, -2, 70, C.grass, 230, 190, 2); // land behind dock, top y=0
addVoxel(scene, 0, -2, 5, C.dock, 110, 10, 2);    // wooden quay, top y=0
addVoxel(scene, 0, -1, -0.5, C.stoneDark, 110, 1, 1); // stone curb

// Grass tufts / flowers
for (let i = 0; i < 260; i++) {
  const x = -115 + ((i * 17) % 230);
  const z = 18 + ((i * 31) % 175);
  if (Math.abs(x) < 48 && z < 38) continue; // avoid dock/building area
  if (i % 11 === 0) {
    addVoxel(scene, x, 0, z, C.flower, 0.7, 0.7, 0.45);
  } else if (i % 3 === 0) {
    addVoxel(scene, x, 0, z, C.grassDark, 0.6, 0.6, 0.55);
  } else {
    addVoxel(scene, x, 0, z, C.grass, 0.6, 0.6, 0.4);
  }
}

// Breakwater
addVoxel(scene, 82, -1, -38, C.stone, 140, 6, 2);
for (let x = 28; x < 150; x += 11) {
  const z = -38 + Math.sin(x * 0.33) * 0.6;
  addVoxel(scene, x, 0, z, x % 22 === 0 ? C.stoneDark : C.stone, 6, 5, 1);
  addVoxel(scene, x + 2, 1, z, C.stone, 3, 3, 1);
}

// Lighthouse
let beaconMat = null;
function addLighthouse(x, z) {
  addVoxel(scene, x, 1, z, C.stoneDark, 10, 10, 3);
  addVoxel(scene, x, 4, z, C.stoneDark, 8, 8, 1);

  for (let i = 0; i < 18; i++) {
    const color = (i % 5 === 0 || i % 5 === 1) ? C.white : C.red;
    addVoxel(scene, x, 5 + i, z, color, 7, 7, 1);
  }

  addVoxel(scene, x, 23, z, C.black, 9, 9, 1);

  beaconMat = new THREE.MeshBasicMaterial({
    color: 0xfff7bd,
    transparent: true,
    opacity: 0.85,
    fog: false
  });

  const beacon = new THREE.Mesh(unit, beaconMat);
  beacon.position.set(x, 25.2, z);
  beacon.scale.set(5.5, 3.2, 5.5);
  scene.add(beacon);

  addVoxel(scene, x, 26, z, C.stoneDark, 5, 5, 1);
  addVoxel(scene, x, 27, z, C.gold, 1.5, 1.5, 1);

  const lamp = new THREE.PointLight(0xffe6a8, 7, 220, 1.7);
  lamp.position.set(x, 25.5, z);
  scene.add(lamp);
}
addLighthouse(118, -38);

// Harbor buildings
function warehouse(x, z, w, d, h, wall, roof) {
  const hx = w / 2;
  const hz = d / 2;

  addVoxel(scene, x - hx + 0.5, 0, z, wall, 1, d, h);
  addVoxel(scene, x + hx - 0.5, 0, z, wall, 1, d, h);
  addVoxel(scene, x, 0, z - hz + 0.5, wall, w - 2, 1, h);
  addVoxel(scene, x, 0, z + hz - 0.5, wall, w - 2, 1, h);

  let rw = w;
  for (let i = 0; i < 3; i++) {
    addVoxel(scene, x, h + i, z, i % 2 ? C.roofLight : roof, rw, d + 2 - i * 2, 1);
    rw -= 2;
  }

  for (let wx = 0; wx < w - 4; wx += 4) {
    addVoxel(scene, x - hx + 2 + wx, 3, z - hz - 0.5, C.window, 1.6, 1, 1.8, true);
  }

  addVoxel(scene, x, 0, z - hz - 0.5, C.woodDark, 2.6, 1, 3.5);
}

warehouse(-42, 30, 18, 16, 9, C.brick, C.roof);
warehouse(-16, 37, 22, 18, 8, C.brickDark, C.roofLight);
warehouse(18, 32, 18, 16, 9, C.brick, C.roof);
warehouse(50, 24, 14, 10, 7, C.stone, C.roof);
warehouse(-72, 48, 16, 14, 7, C.brickDark, C.roof);
warehouse(76, 52, 18, 16, 8, C.brick, C.roof);

// Dock clutter
function addCrate(x, z, color) {
  const s = 2.2;
  addVoxel(scene, x, 0, z, color, s, s, s);
  addVoxel(scene, x, 1.1, z, C.wood, s + 0.4, s + 0.4, 0.3);
  addVoxel(scene, x, s, z, C.wood, s * 0.9, s * 0.9, 0.3);
}

const crateData = [
  [-48, 3, C.crateRed],
  [-45, 8, C.crateBlue],
  [-33, 2, C.crateGreen],
  [-28, 9, C.crateRed],
  [-19, 4, C.crateBlue],
  [-13, 8, C.crateGreen],
  [7, 3, C.crateRed],
  [13, 9, C.crateBlue],
  [24, 2, C.crateGreen],
  [35, 6, C.crateRed],
  [46, 8, C.crateBlue]
];
crateData.forEach(([x, z, c]) => addCrate(x, z, c));

function addBarrel(x, z) {
  addVoxel(scene, x, 0, z, C.wood, 1.3, 1.3, 2.6);
  addVoxel(scene, x, 0.8, z, C.black, 1.5, 1.5, 0.25);
  addVoxel(scene, x, 1.8, z, C.black, 1.4, 1.4, 0.25);
}

const barrelData = [
  [-52, 5],
  [-40, 3],
  [-20, 6],
  [16, 4],
  [38, 7],
  [49, 3]
];
barrelData.forEach(([x, z]) => addBarrel(x, z));

function addBollard(x, z) {
  addVoxel(scene, x, 0, z, C.stoneDark, 1, 1, 2);
  addVoxel(scene, x, 2, z, C.stone, 1.8, 1.8, 0.5);
}
[-50, -35, -20, -5, 10, 25, 40, 50].forEach(x => addBollard(x, 0.7));

function addLamp(x, z) {
  addVoxel(scene, x, 0, z, C.black, 1, 1, 7);
  addVoxel(scene, x, 7, z, C.lamp, 1.5, 1.5, 1, true);
}
[-46, -16, 16, 44].forEach(x => addLamp(x, 6));

// Small rowboats
function addBoat(x, z, ry) {
  const g = new THREE.Group();
  g.position.set(x, 0, z);
  g.rotation.y = ry;
  scene.add(g);

  addVoxel(g, 0, -0.85, 0, C.woodDark, 7, 2.2, 1.1);
  addVoxel(g, 0, 0.25, 0, C.wood, 6, 1.6, 0.55);
  addVoxel(g, 0, 0.8, 0, C.deck, 3, 1.1, 0.2);
}
addBoat(-48, -11, 0.2);
addBoat(-18, -17, -0.5);
addBoat(42, -16, 0.8);

// Gangway from dock to ship
for (let i = 0; i < 8; i++) {
  addVoxel(scene, 0, i * 0.45, -i * 0.85, C.wood, 2, 0.8, 0.4);
}
addVoxel(scene, 0, 3.45, -7.3, C.deck, 2, 1.2, 0.5);

// =====================================================================
// The sailing ship
// =====================================================================

const ship = new THREE.Group();
ship.position.set(0, 0, -14);
ship.rotation.y = -0.08;
scene.add(ship);

function hullHalf(x) {
  if (x < -22) return 0;
  if (x < -20) return 1;
  if (x < -17) return 2;
  if (x < -13) return 3;
  if (x < -10) return 4;
  if (x <= 15) return 6;
  if (x <= 19) return 5;
  if (x <= 22) return 4;
  return 3;
}

// Hull sides, deck, railings
for (let x = -22; x <= 22; x += 2) {
  const w = hullHalf(x);
  if (w <= 0) continue;

  for (const side of [-1, 1]) {
    addVoxel(ship, x, -4, side * w, C.hullDark, 2, 1, 3);
    addVoxel(ship, x, -1, side * w, C.hullLight, 2, 1, 4);

    if (w >= 3 && x % 4 === 0) {
      addVoxel(ship, x, -0.5, side * (w - 0.5), C.black, 0.8, 0.8, 0.8);
    }
  }

  const deckWidth = Math.max(1, 2 * w - 1);
  addVoxel(ship, x, 3, 0, C.deck, 2, deckWidth, 1);
  addVoxel(ship, x, 4, w, C.wood, 2, 1, 0.4);
  addVoxel(ship, x, 4, -w, C.wood, 2, 1, 0.4);
}

// Bow and stern end caps
function addHullEnd(xEnd, wEnd) {
  addVoxel(ship, xEnd, -4, 0, C.hullDark, 1, 2 * wEnd + 1, 3);
  addVoxel(ship, xEnd, -1, 0, C.hullLight, 1, 2 * wEnd + 1, 4);
  addVoxel(ship, xEnd, 4, 0, C.wood, 1, 2 * wEnd + 1, 0.4);
}
addHullEnd(-23, 2);
addHullEnd(23, 4);

// Bowsprit
addRotVoxel(ship, -29, 4, 0, C.mast, 10, 0.8, 0.8, false, 0, 0, -0.25);
addVoxel(ship, -26, 2, 0, C.gold, 1, 1, 1, true);

// Stern castle
addVoxel(ship, 18, 4, 0, C.deck, 12, 12, 1);
addVoxel(ship, 18, 5, 0, C.hullLight, 10, 10, 3);
addVoxel(ship, 18, 8, 0, C.gold, 10.4, 10.4, 0.4);
for (let i = -1; i <= 1; i++) {
  addVoxel(ship, 18 + i * 3, 6.5, 5.5, C.window, 1.5, 1, 1.5, true);
  addVoxel(ship, 18 + i * 3, 6.5, -5.5, C.window, 1.5, 1, 1.5, true);
}

// Forecastle deckhouse
addVoxel(ship, -14, 4, 0, C.wood, 6, 6, 2);
addVoxel(ship, -14, 6, 0, C.deck, 7, 7, 0.5);

// Masts
function addMast(x, h) {
  addVoxel(ship, x, 4, 0, C.mast, 1, 1, h);
  addVoxel(ship, x, 4 + h, 0, C.mast, 0.6, 0.6, 1);
}
addMast(-8, 20);  // fore
addMast(2, 24);   // main
addMast(14, 16);  // mizzen

// Square sails and yards
function addSail(mastX, yBottom, height, width, sailColor = C.sail) {
  addVoxel(ship, mastX, yBottom, 0, sailColor, 0.6, width, height);
  addRotVoxel(ship, mastX, yBottom + height + 0.5, 0, C.mast, 1, width + 3, 1);
}

addSail(-8, 5, 7, 11, C.sail);
addSail(-8, 13, 5, 9, C.sailShade);
addSail(-8, 19, 3, 7, C.sail);

addSail(2, 5, 9, 13, C.sail);
addSail(2, 15, 7, 11, C.sailShade);
addSail(2, 23, 3, 9, C.sail);

addSail(14, 5, 6, 10, C.sail);
addSail(14, 12, 4, 8, C.sailShade);

// Flags
addRotVoxel(ship, -7.2, 25.0, 0, C.red, 1.8, 0.1, 1.2, true);
addRotVoxel(ship, 2.8, 29.0, 0, C.red, 1.8, 0.1, 1.2, true);
addRotVoxel(ship, 14.8, 19.0, 0, C.gold, 1.8, 0.1, 1.2, true);

// Rigging
const rigPoints = [];
function rigLine(a, b) {
  rigPoints.push(a[0], a[1], a[2], b[0], b[1], b[2]);
}
function shrouds(mastX, topY, width) {
  for (const side of [-1, 1]) {
    rigLine([mastX, topY, 0], [mastX, 4, side * width * 0.82]);
  }
}
shrouds(-8, 24, 6);
shrouds(2, 28, 6);
shrouds(14, 18, 6);

rigLine([-8, 24, 0], [-23, 4, 0]);
rigLine([-8, 24, 0], [-34, 4.5, 0]);
rigLine([2, 28, 0], [-10, 4, 0]);
rigLine([2, 28, 0], [23, 4, 0]);
rigLine([14, 18, 0], [23, 4, 0]);

const rigGeo = new THREE.BufferGeometry();
rigGeo.setAttribute("position", new THREE.Float32BufferAttribute(rigPoints, 3));
const rigMat = new THREE.LineBasicMaterial({
  color: C.rope,
  transparent: true,
  opacity: 0.58
});
ship.add(new THREE.LineSegments(rigGeo, rigMat));

// Foam around hull
const foamMat = new THREE.MeshBasicMaterial({
  color: C.foam,
  transparent: true,
  opacity: 0.34
});

function addFoam(x, z, sx, sz) {
  const m = new THREE.Mesh(unit, foamMat);
  m.position.set(x, 0.06, z);
  m.scale.set(sx, 0.09, sz);
  ship.add(m);
}

for (let x = -22; x <= 22; x += 4) {
  const w = Math.max(1, hullHalf(x));
  addFoam(x, w + 0.8, 3, 1.3);
  addFoam(x, -(w + 0.8), 3, 1.3);
}
addFoam(-23, 0, 2.2, 6);
addFoam(23, 0, 2.2, 7);

// Clouds
const clouds = [];
function addCloud(x, y, z, s) {
  const g = new THREE.Group();
  g.position.set(x, y, z);
  scene.add(g);

  const pieces = [
    [0, 0, 0, 3],
    [2.2, 0.8, 0.4, 2.2],
    [-2.2, 0.3, -0.5, 2.3],
    [0.3, 1.8, 0.2, 2.0]
  ];

  pieces.forEach(([ox, oy, oz, ps]) => {
    const size = ps * s;
    addVoxel(g, ox * s, oy * s, oz * s, C.white, size, size, size);
  });

  return g;
}
clouds.push(
  addCloud(-110, 52, -55, 1.1),
  addCloud(60, 56, -120, 1.5),
  addCloud(160, 46, 30, 1.2),
  addCloud(-30, 68, 150, 1.3)
);

// Seagulls
const gulls = [];
function addGull(x, y, z) {
  const g = new THREE.Group();
  g.position.set(x, y, z);
  scene.add(g);
  addVoxel(g, 0, 0, 0, C.white, 2, 1, 0.45);
  addRotVoxel(g, 0, 0.2, 0, C.white, 0.4, 3.4, 0.5);
  return g;
}
gulls.push(addGull(0, 34, -10), addGull(20, 39, 15), addGull(-25, 44, -5));

// =====================================================================
// Mouse controls
// =====================================================================

const target = new THREE.Vector3(0, 6, -12);
let radius = 98;
let phi = 1.05;
let theta = Math.PI * 0.62;
let isDragging = false;
let lastX = 0;
let lastY = 0;
let autoRotate = true;
let lastInteraction = performance.now();

function updateCamera() {
  camera.position.setFromSphericalCoords(radius, phi, theta).add(target);
  camera.lookAt(target);
}
updateCamera();

renderer.domElement.addEventListener("pointerdown", (e) => {
  isDragging = true;
  lastX = e.clientX;
  lastY = e.clientY;
  renderer.domElement.setPointerCapture(e.pointerId);
  e.preventDefault();
  autoRotate = false;
  lastInteraction = performance.now();
});

window.addEventListener("pointerup", () => {
  isDragging = false;
  lastInteraction = performance.now();
});

window.addEventListener("pointermove", (e) => {
  if (!isDragging) return;
  const dx = e.clientX - lastX;
  const dy = e.clientY - lastY;
  lastX = e.clientX;
  lastY = e.clientY;

  theta -= dx * 0.004;
  phi += dy * 0.004;
  phi = THREE.MathUtils.clamp(phi, 0.25, Math.PI / 2 - 0.02);

  lastInteraction = performance.now();
});

renderer.domElement.addEventListener(
  "wheel",
  (e) => {
    e.preventDefault();
    radius *= 1 + e.deltaY * 0.001;
    radius = THREE.MathUtils.clamp(radius, 30, 260);
    autoRotate = false;
    lastInteraction = performance.now();
  },
  { passive: false }
);

renderer.domElement.addEventListener("contextmenu", (e) => e.preventDefault());

window.addEventListener("dblclick", () => {
  radius = 98;
  phi = 1.05;
  theta = Math.PI * 0.62;
  target.set(0, 6, -12);
  autoRotate = true;
  lastInteraction = performance.now();
});

window.addEventListener("resize", () => {
  renderer.setSize(window.innerWidth, window.innerHeight);
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
});

// =====================================================================
// Animation loop
// =====================================================================

let last = performance.now();
let elapsed = 0;
let frame = 0;

function animate() {
  requestAnimationFrame(animate);

  const now = performance.now();
  let dt = (now - last) / 1000;
  last = now;
  dt = Math.min(dt, 0.05);
  elapsed += dt;
  frame++;

  const t = elapsed;

  // Water waves
  const pos = waterObj.geo.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    const ix = i * 3;
    const x = waterObj.base[ix];
    const zLocal = waterObj.base[ix + 2];
    const worldZ = waterObj.mesh.position.z + zLocal;
    const shore = THREE.MathUtils.clamp(-worldZ / 22, 0, 1);
    const wave = Math.sin(x * 0.11 + t * 1.2) + Math.sin(zLocal * 0.14 + t * 1.7);
    pos.setY(i, shore * wave * 0.22);
  }
  pos.needsUpdate = true;
  if ((frame % 8) === 0) {
    waterObj.geo.computeVertexNormals();
  }

  // Ship motion
  ship.position.y = Math.sin(t * 0.9) * 0.16;
  ship.rotation.z = Math.sin(t * 0.65) * 0.018;
  ship.rotation.x = Math.sin(t * 0.52) * 0.01;

  // Lighthouse beacon
  if (beaconMat) {
    beaconMat.opacity = 0.62 + 0.38 * (0.5 + 0.5 * Math.sin(t * 1.8));
  }

  // Clouds
  clouds.forEach((cloud, i) => {
    cloud.position.x += dt * (2.0 + i * 1.5);
    if (cloud.position.x > 270) cloud.position.x = -270;
  });

  // Gulls
  gulls.forEach((gull, i) => {
    const p = t * 0.45 + i * 2.3;
    gull.position.x = Math.sin(p) * 70 + (i - 1) * 18;
    gull.position.z = -45 + Math.cos(p * 0.72) * 65;
    gull.position.y = 36 + Math.sin(p * 1.9) * 2.8;
    gull.rotation.z = Math.sin(p * 2.7) * 0.18;
  });

  // Gentle auto-orbit after inactivity
  if (!isDragging && now - lastInteraction > 4000) {
    autoRotate = true;
  }
  if (autoRotate) {
    theta += dt * 0.045;
  }

  updateCamera();
  renderer.render(scene, camera);
}

animate();
</script>
</body>
</html>
```