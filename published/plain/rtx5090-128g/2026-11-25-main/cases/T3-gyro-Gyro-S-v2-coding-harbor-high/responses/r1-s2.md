Here is a complete single-file voxel harbor scene. It uses Three.js from a CDN, so it needs internet access on first load. Paste it into an HTML file and open it in Chrome.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Voxel Harbor — Sailing Ship Calling at Harbor</title>
<style>
  body { margin: 0; overflow: hidden; background: #10202a; }
  canvas { display: block; }
  #info {
    position: absolute;
    top: 12px;
    left: 12px;
    color: #dff3f7;
    font: 12px/1.3 monospace;
    text-shadow: 0 1px 2px #000;
    pointer-events: none;
  }
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
<div id="info">drag: orbit · scroll: zoom · right drag: pan</div>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* ------------------------------------------------------------------ */
/* Renderer / scene / camera                                           */
/* ------------------------------------------------------------------ */
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();

/* Sky gradient */
const skyCanvas = document.createElement('canvas');
skyCanvas.width = 32;
skyCanvas.height = 256;
const skyCtx = skyCanvas.getContext('2d');
const grad = skyCtx.createLinearGradient(0, 0, 0, skyCanvas.height);
grad.addColorStop(0.00, '#4b82a4');
grad.addColorStop(0.35, '#8bb5c6');
grad.addColorStop(0.70, '#c6dde6');
grad.addColorStop(1.00, '#e6f2f7');
skyCtx.fillStyle = grad;
skyCtx.fillRect(0, 0, skyCanvas.width, skyCanvas.height);

const skyTex = new THREE.CanvasTexture(skyCanvas);
skyTex.colorSpace = THREE.SRGBColorSpace;
scene.background = skyTex;
scene.fog = new THREE.Fog(0xd7e6e9, 25, 130);

const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 400);
camera.position.set(24, 18, 28);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(2, 4, 3);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.minDistance = 8;
controls.maxDistance = 80;
controls.maxPolarAngle = 1.45;
controls.update();

/* ------------------------------------------------------------------ */
/* Lights                                                              */
/* ------------------------------------------------------------------ */
const hemi = new THREE.HemisphereLight(0x9cc7de, 0x524a3e, 0.55);
scene.add(hemi);

const sun = new THREE.DirectionalLight(0xffe3bd, 1.35);
sun.position.set(-28, 32, 22);
sun.castShadow = true;
sun.shadow.mapSize.set(1024, 1024);
sun.shadow.camera.near = 1;
sun.shadow.camera.far = 120;
sun.shadow.camera.left = -35;
sun.shadow.camera.right = 35;
sun.shadow.camera.top = 35;
sun.shadow.camera.bottom = -35;
sun.shadow.bias = -0.001;
scene.add(sun);

scene.add(new THREE.AmbientLight(0xffffff, 0.12));

/* ------------------------------------------------------------------ */
/* Voxel helpers                                                       */
/* ------------------------------------------------------------------ */
function mulberry32(a) {
  return function () {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 0x1b6d9f5a);
    t = (t + Math.imul(t ^ (t >>> 7), 0x4b2b34b9)) | 0;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
const rng = mulberry32(0x5612524776);

const boxGeo = new THREE.BoxGeometry(1, 1, 1);
const voxelMat = new THREE.MeshStandardMaterial({
  roughness: 0.93,
  metalness: 0.02
});

const matrices = [];
const colors = [];
const dummy = new THREE.Object3D();

function addCube(x, y, z, sx = 1, sy = 1, sz = 1, color = 0xffffff) {
  dummy.position.set(x, y, z);
  dummy.scale.set(sx, sy, sz);
  dummy.updateMatrix();
  matrices.push(dummy.matrix.clone());
  colors.push(new THREE.Color(color));
}

function addRod(x1, y1, z1, x2, y2, z2, color = 0x7f5f42, thickness = 0.24, step = 0.35) {
  const dx = x2 - x1;
  const dy = y2 - y1;
  const dz = z2 - z1;
  const len = Math.hypot(dx, dy, dz);
  if (len <= 0) return;

  const steps = Math.max(1, Math.ceil(len / step));
  for (let i = 0; i <= steps; i++) {
    const s = i / steps;
    addCube(x1 + dx * s, y1 + dy * s, z1 + dz * s, thickness, thickness, thickness, color);
  }
}

/* ------------------------------------------------------------------ */
/* Water                                                               */
/* ------------------------------------------------------------------ */
const waterGeo = new THREE.PlaneGeometry(220, 220, 70, 70);
const waterMat = new THREE.MeshStandardMaterial({
  color: 0x236a82,
  roughness: 0.42,
  metalness: 0.05,
  flatShading: true
});
const water = new THREE.Mesh(waterGeo, waterMat);
water.rotation.x = -Math.PI / 2;
water.receiveShadow = true;
scene.add(water);

function updateWater(t) {
  const p = waterGeo.attributes.position;
  for (let i = 0; i < p.count; i++) {
    const x = p.getX(i);
    const y = p.getY(i);

    const h =
      0.08 * Math.sin(x * 0.12 + t * 0.65) +
      0.07 * Math.cos(-y * 0.12 + t * 0.9) +
      0.05 * Math.sin((x * 0.06 + y * 0.08) + t * 0.5);

    p.setZ(i, h);
  }
  p.needsUpdate = true;
}

/* ------------------------------------------------------------------ */
/* Harbor quay                                                         */
/* ------------------------------------------------------------------ */
const deckColors = [0x9f958a, 0x8f8476, 0x979b8e, 0xc1ad97, 0x8b7f74];
const wallColors = [0x4c555a, 0x3d454a, 0x566164];

function pick(arr) {
  return arr[Math.floor(rng() * arr.length)];
}

for (let x = 6; x <= 30; x++) {
  for (let z = -16; z <= 16; z++) {
    // Quay deck surface
    addCube(x, 1, z, 1, 1, 1, pick(deckColors));

    // Stone wall beneath the deck
    addCube(x, 0, z, 1, 1, 1, pick(wallColors));
  }
}

/* Foam along the dock edge */
for (let z = -16; z <= 16; z++) {
  addCube(5.35, 0.25, z, 0.8, 0.25, 0.9, 0xe9f6f9);
}

/* Bollards */
const bollardZ = [-6, -2, 2, 6, 10];
for (const z of bollardZ) {
  addCube(7, 1.85, z, 0.55, 0.7, 0.55, 0x3e312a);
  addCube(7, 2.25, z, 0.35, 0.22, 0.35, 0x5c4b3b);
}

/* Crates and barrels */
function addCrate(x, z) {
  const base = pick([0x9d6f3b, 0x8f6232, 0xa87844]);
  for (let dx = 0; dx < 2; dx++) {
    for (let dz = 0; dz < 2; dz++) {
      const c = rng() < 0.5 ? base : (rng() < 0.5 ? 0x7b522b : 0xa2764a);
      addCube(x + dx, 2, z + dz, 1, 1, 1, c);
    }
  }
}

function addBarrel(x, z) {
  addCube(x, 2.05, z, 0.85, 0.95, 0.85, pick([0x8f6338, 0x7a522f, 0x9c7142]));
  addCube(x, 2.45, z, 0.72, 0.12, 0.72, 0x5b3d26);
}

for (let i = 0; i < 18; i++) {
  const x = 8 + Math.floor(rng() * 20);
  const z = -15 + Math.floor(rng() * 29);

  // Avoid warehouse footprint
  if (x >= 16 && x <= 30 && z >= -14 && z <= -2) continue;

  if (rng() < 0.7) addCrate(x, z);
  else addBarrel(x, z);
}

/* ------------------------------------------------------------------ */
/* Warehouse                                                           */
/* ------------------------------------------------------------------ */
const warehouseXMin = 18;
const warehouseXMax = 29;
const warehouseZMin = -14;
const warehouseZMax = -2;

for (let x = warehouseXMin; x <= warehouseXMax; x++) {
  for (let z = warehouseZMin; z <= warehouseZMax; z++) {
    for (let y = 2; y <= 6; y++) {
      const onWall = x === warehouseXMin || x === warehouseXMax || z === warehouseZMin || z === warehouseZMax;
      if (!onWall) continue;

      let color = pick([0x936f54, 0x82624c, 0xa4785a]);

      const isDoor = z === warehouseZMax && (y === 2 || y === 3) && x === 24;
      if (isDoor) color = 0x2f241b;

      if (y >= 3 && y <= 5 && !isDoor && ((x * 7 + z * 5 + y * 3) % 9 === 0)) {
        color = 0xf1e5cf;
      }

      addCube(x, y, z, 1, 1, 1, color);
    }
  }
}

/* Door panel protruding from the dock side */
addCube(24, 2.5, -2.6, 0.8, 1.4, 0.25, 0x26211b);

/* Roof */
for (let x = warehouseXMin - 1; x <= warehouseXMax + 1; x++) {
  for (let z = warehouseZMin - 1; z <= warehouseZMax + 1; z++) {
    addCube(x, 7, z, 1, 1, 1, pick([0x5a4332, 0x6f4f38, 0x4c3c2f]));
  }
}

/* Chimney */
addCube(28, 7.55, -11, 0.9, 1.8, 0.9, 0x735343);

/* ------------------------------------------------------------------ */
/* Lighthouse pier                                                     */
/* ------------------------------------------------------------------ */
for (let x = 31; x <= 35; x++) {
  for (let z = 11; z <= 16; z++) {
    addCube(x, 1, z, 1, 1, 1, pick(deckColors));
    addCube(x, 0, z, 1, 1, 1, pick(wallColors));
  }
}

/* Lighthouse tower */
for (let y = 2; y <= 11; y++) {
  const hw = y <= 4 ? 2 : 1;
  const band = Math.floor((y - 2) / 2) % 2;
  const color = band === 0 ? 0xf7f7f7 : 0xd2463b;

  for (let dx = -hw; dx <= hw; dx++) {
    for (let dz = -hw; dz <= hw; dz++) {
      addCube(33 + dx, y, 13 + dz, 1, 1, 1, color);
    }
  }
}

/* Roof cap */
addCube(33, 13.0, 13, 3.0, 0.7, 3.0, 0xc34536);

/* ------------------------------------------------------------------ */
/* Ship                                                                */
/* ------------------------------------------------------------------ */
const shipCenterZ = 2;
const shipZMin = -10;
const shipZMax = 14;
const shipHalfLen = 12;

function shipWidth(z) {
  const t = (z - shipCenterZ) / shipHalfLen;
  return Math.max(0.35, 4.2 * (1 - 0.82 * t * t));
}

const hullWaterline = 0x3b2920;
const hullBrownA = 0x5f4331;
const hullBrownB = 0x70523b;
const hullStripe = 0xeadfca;
const deckBrownA = 0x9b734a;
const deckBrownB = 0x8a623d;
const mastColor = 0x4d382d;
const ropeColor = 0xc89e71;
const sailColor = 0xf2ece1;

/* Hull body */
for (let z = shipZMin; z <= shipZMax; z++) {
  const hw = shipWidth(z);
  const isEnd = z === shipZMin || z === shipZMax;

  for (let y = 0; y <= 4; y++) {
    const verticalScale = 1 - (y / 6) * 0.35;
    const half = Math.max(0, hw * verticalScale);
    const maxI = Math.floor(half + 0.05);

    for (let x = -maxI; x <= maxI; x++) {
      if (y === 4) {
        // Deck row fills the top
        const c = ((x + z) % 2 === 0 ? deckBrownA : deckBrownB);
        addCube(x, y, z, 1, 1, 1, c);
        continue;
      }

      const include = y === 0 || x === maxI || x === -maxI || isEnd;
      if (!include) continue;

      let color;
      if (y === 0) {
        color = hullWaterline;
      } else if (y === 2) {
        color = x === maxI || x === -maxI ? hullStripe : hullBrownB;
      } else {
        color = rng() < 0.35 ? hullBrownA : hullBrownB;
      }

      addCube(x, y, z, 1, 1, 1, color);
    }
  }
}

/* Deck rail */
for (let z = -8; z <= 13; z++) {
  const half = shipWidth(z) * (1 - (4 / 6) * 0.35);
  const maxI = Math.floor(half + 0.05);

  if (maxI >= 0) {
    addCube(maxI + 0.25, 5, z, 0.16, 0.35, 0.16, 0x553f34);
    if (maxI > 0) {
      addCube(-maxI - 0.25, 5, z, 0.16, 0.35, 0.16, 0x553f34);
    }
  }
}

/* Stern cabin */
addCube(0, 5.2, 12.2, 5, 2.5, 5.5, 0x5d3e2c);
addCube(0, 6.65, 12.2, 5.4, 0.35, 6.0, 0x2f2820);
addCube(2.6, 5.5, 12, 0.25, 0.7, 0.25, 0xe8ddcf);
addCube(-2.6, 5.5, 12, 0.25, 0.7, 0.25, 0xe8ddcf);
addCube(2.6, 5.5, 13, 0.25, 0.7, 0.25, 0xe8ddcf);

/* Cargo crates on deck */
function addCargo(x, z) {
  addCube(x, 5, z, 0.7, 0.8, 0.7, 0x8f6a3b);
  addCube(x, 5.05, z, 0.62, 0.1, 0.62, 0x5e4326);
}
addCargo(1.2, -3);
addCargo(-1.2, -1);
addCargo(2, -2);
addCargo(-1.5, 4);

/* Bowsprit */
addRod(0, 4.2, -9.5, 0, 5.0, -12.6, mastColor, 0.22, 0.32);
addCube(0, 5.0, -12.6, 0.3, 0.3, 0.3, mastColor);

/* Masts */
const foreZ = -4;
const mainZ = 2;
const mizzenZ = 8;
const foreTop = 13.5;
const mainTop = 15.0;
const mizzenTop = 11.5;

addRod(0, 4.2, foreZ, 0, foreTop, foreZ, mastColor, 0.27, 0.32);
addRod(0, 4.2, mainZ, 0, mainTop, mainZ, mastColor, 0.29, 0.32);
addRod(0, 4.2, mizzenZ, 0, mizzenTop, mizzenZ, mastColor, 0.24, 0.32);

addCube(0, foreTop + 0.1, foreZ, 0.35, 0.3, 0.35, mastColor);
addCube(0, mainTop + 0.1, mainZ, 0.38, 0.32, 0.38, mastColor);
addCube(0, mizzenTop + 0.1, mizzenZ, 0.3, 0.28, 0.3, mastColor);

/* Small pennant */
addRod(0, mainTop + 0.15, mainZ, 1.0, mainTop + 0.65, mainZ, 0x304a63, 0.12, 0.25);
addCube(1.0, mainTop + 0.65, mainZ, 0.25, 0.25, 0.25, 0x304a63);

/* Furled sails along yards */
function addFurledSail(y, z, width) {
  const n = Math.max(2, Math.round((width * 2) / 0.45));

  for (let i = 0; i <= n; i++) {
    const x = -width + 2 * width * (i / n);
    const sag = Math.sin((x / width + 0.5) * Math.PI) * 0.35;
    const c = rng() < 0.12 ? 0xe4dbc7 : sailColor;
    addCube(x, y - 0.28 - sag, z, 0.35, 0.28, 0.35, c);
  }
}

function addYard(z, y, width) {
  addRod(-width, y, z, width, y, z, mastColor, 0.22, 0.3);
  addCube(width, y, z, 0.35, 0.3, 0.35, mastColor);
  addCube(-width, y, z, 0.35, 0.3, 0.35, mastColor);
  addFurledSail(y, z, width);
}

addYard(foreZ, 10, 5);
addYard(foreZ, 6.8, 3.5);
addYard(mainZ, 12, 5.8);
addYard(mainZ, 8.4, 4.2);
addYard(mizzenZ, 9, 4);
addYard(mizzenZ, 6, 2.5);

/* Rigging stays */
addRod(0, foreTop, foreZ, 0, 5.0, -12.6, ropeColor, 0.12, 0.35);
addRod(0, mainTop, mainZ, 0, 5.0, -12.6, ropeColor, 0.12, 0.35);
addRod(0, mainTop, mainZ, 0, 6.6, 12.2, ropeColor, 0.12, 0.35);
addRod(0, mizzenTop, mizzenZ, 0, 6.6, 12.2, ropeColor, 0.12, 0.35);

/* Side shrouds */
addRod(0, foreTop, foreZ, 3.1, 4.6, foreZ, ropeColor, 0.11, 0.35);
addRod(0, foreTop, foreZ, -3.1, 4.6, foreZ, ropeColor, 0.11, 0.35);
addRod(0, mainTop, mainZ, 3.5, 4.6, mainZ, ropeColor, 0.11, 0.35);
addRod(0, mainTop, mainZ, -3.5, 4.6, mainZ, ropeColor, 0.11, 0.35);
addRod(0, mizzenTop, mizzenZ, 3.0, 4.6, mizzenZ, ropeColor, 0.11, 0.35);
addRod(0, mizzenTop, mizzenZ, -3.0, 4.6, mizzenZ, ropeColor, 0.11, 0.35);

/* Mooring ropes to dock bollards */
for (const z of [-6, -2, 2, 6, 10]) {
  const half = shipWidth(z) * (1 - (4 / 6) * 0.35);
  const maxI = Math.floor(half + 0.05);
  const startX = Math.max(1, maxI + 0.6);

  addRod(startX, 4.7, z, 7, 2.2, z, ropeColor, 0.14, 0.3);
}

/* ------------------------------------------------------------------ */
/* Build instanced voxel mesh                                          */
/* ------------------------------------------------------------------ */
const voxelMesh = new THREE.InstancedMesh(boxGeo, voxelMat, matrices.length);

for (let i = 0; i < matrices.length; i++) {
  voxelMesh.setMatrixAt(i, matrices[i]);
  voxelMesh.setColorAt(i, colors[i]);
}

voxelMesh.instanceMatrix.needsUpdate = true;
if (voxelMesh.instanceColor) voxelMesh.instanceColor.needsUpdate = true;
voxelMesh.castShadow = true;
voxelMesh.receiveShadow = true;
scene.add(voxelMesh);

/* ------------------------------------------------------------------ */
/* Lighthouse lamp                                                     */
/* ------------------------------------------------------------------ */
const lampMat = new THREE.MeshBasicMaterial({ color: 0xffe080 });
const lamp = new THREE.Mesh(new THREE.BoxGeometry(1.3, 0.9, 1.3), lampMat);
lamp.position.set(33, 12.2, 13);
lamp.castShadow = false;
scene.add(lamp);

const lampLight = new THREE.PointLight(0xffd796, 1.2, 35);
lampLight.position.copy(lamp.position);
scene.add(lampLight);

/* ------------------------------------------------------------------ */
/* Resize / animation                                                  */
/* ------------------------------------------------------------------ */
function onResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}
window.addEventListener('resize', onResize);

const clock = new THREE.Clock();
let firstShadowRender = true;

function animate() {
  requestAnimationFrame(animate);

  const t = clock.getElapsedTime();
  updateWater(t);

  const pulse = 0.5 + 0.5 * Math.sin(t * 2.7);
  lampLight.intensity = 0.5 + pulse * 1.1;
  lampMat.color.setRGB(1.0, 0.92 + pulse * 0.08, 0.62 + pulse * 0.2);

  controls.update();
  renderer.render(scene, camera);

  if (firstShadowRender) {
    sun.shadow.autoUpdate = false;
    firstShadowRender = false;
  }
}

animate();
</script>
</body>
</html>
```