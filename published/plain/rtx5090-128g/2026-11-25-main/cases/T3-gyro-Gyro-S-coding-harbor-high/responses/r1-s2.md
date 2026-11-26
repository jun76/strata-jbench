```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Voxel Harbor: A Sailing Ship Calling at Harbor</title>
<style>
  html, body {
    margin: 0;
    height: 100%;
    overflow: hidden;
    background: #000;
  }
  canvas {
    display: block;
  }
  #hint {
    position: fixed;
    left: 12px;
    bottom: 12px;
    color: #e7f4f5;
    font: 12px/1.3 system-ui, sans-serif;
    pointer-events: none;
    opacity: 0.85;
  }
</style>
</head>
<body>
<div id="hint">Drag to orbit • Scroll to zoom</div>

<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
  }
}
</script>

<script type="module">
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

/* Deterministic small random generator for voxel color variation */
let seed = 987654321;
function rnd() {
  seed = (seed * 1664525 + 1013904223) >>> 0;
  return seed / 4294967296;
}
function pick(arr) {
  return arr[Math.floor(rnd() * arr.length)];
}

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xb9e0e6);
scene.fog = new THREE.Fog(0xb9e0e6, 42, 140);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 300);
camera.position.set(-28, 22, 26);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(4, 2, 0);
controls.enableDamping = true;
controls.minDistance = 12;
controls.maxDistance = 90;
controls.maxPolarAngle = Math.PI / 2.05;

const hemi = new THREE.HemisphereLight(0xe6d4b9, 0x4d6473, 0.65);
scene.add(hemi);

const sun = new THREE.DirectionalLight(0xffd299, 1.25);
sun.position.set(35, 50, -22);
sun.castShadow = true;
sun.shadow.mapSize.set(1024, 1024);
sun.shadow.camera.near = 10;
sun.shadow.camera.far = 130;
sun.shadow.camera.left = -38;
sun.shadow.camera.right = 38;
sun.shadow.camera.top = 38;
sun.shadow.camera.bottom = -38;
scene.add(sun);

/* Static voxel builder */
const boxGeo = new THREE.BoxGeometry(1, 1, 1);
const staticMat = new THREE.MeshLambertMaterial();
const staticMatrices = [];
const staticColors = [];

function addBlock(x, y, z, color, sx = 1, sy = 1, sz = 1) {
  const matrix = new THREE.Matrix4().compose(
    new THREE.Vector3(x, y, z),
    new THREE.Quaternion(),
    new THREE.Vector3(sx, sy, sz)
  );
  staticMatrices.push(matrix);
  staticColors.push(color);
}

function finalizeStatic() {
  if (staticMatrices.length === 0) return null;

  const mesh = new THREE.InstancedMesh(boxGeo, staticMat, staticMatrices.length);
  mesh.castShadow = true;
  mesh.receiveShadow = true;

  const tmpColor = new THREE.Color();
  for (let i = 0; i < staticMatrices.length; i++) {
    mesh.setMatrixAt(i, staticMatrices[i]);
    tmpColor.setHex(staticColors[i]);
    mesh.setColorAt(i, tmpColor);
  }
  mesh.instanceMatrix.needsUpdate = true;
  if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;

  scene.add(mesh);
  return mesh;
}

/* Harbor stone, quay, and land */
const stoneColors = [0x9b9085, 0x8b7f72, 0xa89d8b];
const dockWoodColors = [0x7c5a40, 0x8b6848];
const landColors = [0x779c5c, 0x876f55, 0x9a8b6a];

for (let x = 10; x <= 13; x++) {
  for (let z = -14; z <= 14; z++) {
    addBlock(x, 1, z, pick(stoneColors));
  }
}

for (let x = 12; x <= 13; x++) {
  for (let z = -14; z <= 14; z++) {
    addBlock(x, 1.3, z, pick(dockWoodColors), 1, 0.4, 1);
  }
}

for (let x = 14; x <= 24; x++) {
  for (let z = -16; z <= 16; z++) {
    addBlock(x, 1, z, pick(landColors));
  }
}

/* Dock bollards */
const bollardColor = 0x3f4751;
for (let z = -12; z <= 12; z += 4) {
  addBlock(12.5, 1.9, z, bollardColor, 0.35, 0.8, 0.35);
}

/* Cargo on dock */
const crateColors = [0xa8814f, 0x8f5a3a, 0x6b7a3b, 0x72563a];
function addCargo(x, baseY, z, s, color = pick(crateColors)) {
  addBlock(x, baseY + s / 2, z, color, s, s, s);
}

addCargo(12, 1.5, -9, 0.7);
addCargo(12, 1.5, -6, 0.5);
addCargo(13, 1.5, -7, 0.55);
addCargo(12, 1.5, 4, 0.7);
addCargo(13, 1.5, 7, 0.5);
addCargo(12, 1.5, 8, 0.45);

/* Building helper */
function addBoxLayer(cx, cz, y, halfX, halfZ, color, frontWindows = null) {
  for (let xi = -halfX; xi <= halfX; xi++) {
    for (let zi = -halfZ; zi <= halfZ; zi++) {
      let c = color;
      if (frontWindows && xi === -halfX && y === 3 && frontWindows.includes(zi)) {
        c = 0x2b4153;
      }
      addBlock(cx + xi, y, cz + zi, c);
    }
  }
}

function voxelBuilding(cx, cz, widthX, depthZ, height, wallColors, roofColor, frontWindows = null) {
  const halfX = Math.floor(widthX / 2);
  const halfZ = Math.floor(depthZ / 2);

  for (let y = 2; y < 2 + height; y++) {
    addBoxLayer(cx, cz, y, halfX, halfZ, pick(wallColors), frontWindows);
  }

  const roofY = 2 + height;
  for (let r = 0; r < 2; r++) {
    addBoxLayer(cx, cz, roofY + r, Math.max(0, halfX - r), Math.max(0, halfZ - r), roofColor);
  }
}

voxelBuilding(
  18, -2,
  7, 11,
  3,
  [0xd0a67c, 0xb98d62, 0xcaa072],
  0x6d4433,
  [-4, -2, 0, 2, 4]
);

voxelBuilding(
  22, 7,
  5, 7,
  2,
  [0xc5a175, 0xb28b5c],
  0x5e5550,
  [-2, 0, 2]
);

voxelBuilding(
  16, 13,
  5, 5,
  2,
  [0xd7b487, 0xb99166],
  0x6d4433,
  [-1, 1]
);

/* Lighthouse */
function buildLighthouse(cx, cz) {
  for (let y = 2; y <= 7; y++) {
    const half = y < 4 ? 2 : 1;
    const band = Math.floor((y - 2) / 2) % 2 === 0 ? 0xf4efe5 : 0xc0483f;
    addBoxLayer(cx, cz, y, half, half, band);
  }

  addBlock(cx, 8, cz, 0x353b43, 1, 0.8, 1);
}

buildLighthouse(22, -12);

const lampMat = new THREE.MeshBasicMaterial({ color: 0xfff29a });
const lamp = new THREE.Mesh(boxGeo, lampMat);
lamp.position.set(22, 8.6, -12);
lamp.scale.set(0.8, 0.55, 0.8);
scene.add(lamp);

const lampLight = new THREE.PointLight(0xfff29a, 1.2, 26);
lampLight.position.set(22, 8.2, -12);
scene.add(lampLight);

/* Sailing ship */
const hullDarkColors = [0x4f3826, 0x5d4330];
const hullBrownColors = [0x6a4f38, 0x775a42];
const deckWoodColors = [0x8f6f51, 0x836049];
const sailColors = [0xf2e6c9, 0xf8efd8];
const poleColors = [0x70523d, 0x806046];

const shipXMin = -12;
const shipXMax = 6;
const shipLen = shipXMax - shipXMin + 1;

for (let x = shipXMin; x <= shipXMax; x++) {
  const t = (x - shipXMin) / (shipLen - 1);
  const shape = Math.sin(t * Math.PI);
  const halfZ = Math.max(1, Math.round(1 + 2.4 * shape));
  const lowHalf = Math.max(1, halfZ - 1);

  for (let z = -lowHalf; z <= lowHalf; z++) {
    addBlock(x, 1.5, z, pick(hullDarkColors), 1, 1, 1);
  }

  for (let z = -halfZ; z <= halfZ; z++) {
    addBlock(x, 2.5, z, pick(hullBrownColors), 1, 1, 1);
  }

  for (let z = -halfZ; z <= halfZ; z++) {
    addBlock(x, 3.0, z, pick(deckWoodColors), 1, 0.4, 1);
  }
}

/* Stern cabin */
const cabinColor = 0x8e5a40;
const cabinRoofColor = 0x7c3a2e;

for (let xi = -2; xi <= 2; xi++) {
  for (let zi = -1; zi <= 1; zi++) {
    addBlock(-9 + xi, 3.6, zi, cabinColor);
    addBlock(-9 + xi, 4.6, zi, cabinColor);
  }
}

addBlock(-9, 5.6, 0, cabinRoofColor, 3, 1, 3);

/* Bowsprit */
for (let x = 6; x <= 8; x++) {
  addBlock(x, 2.8, 0, pick(poleColors), 0.3, 0.5, 0.3);
}

/* Main mast */
for (let y = 4; y <= 8; y++) {
  addBlock(-3, y, 0, pick(poleColors), 0.6, 1, 0.6);
}

/* Main yard */
for (let z = -3; z <= 3; z++) {
  addBlock(-3, 7, z, pick(poleColors), 0.5, 0.5, 1);
}

/* Main sail */
for (let z = -3; z <= 3; z++) {
  addBlock(-3, 5.8, z, pick(sailColors), 0.6, 2.2, 1);
}

/* Secondary mast */
for (let y = 4; y <= 7; y++) {
  addBlock(3, y, 0, pick(poleColors), 0.55, 1, 0.55);
}

/* Secondary yard */
for (let z = -2; z <= 2; z++) {
  addBlock(3, 6, z, pick(poleColors), 0.45, 0.45, 1);
}

/* Secondary sail */
for (let z = -2; z <= 2; z++) {
  addBlock(3, 4.8, z, pick(sailColors), 0.55, 1.6, 1);
}

/* Flag */
addBlock(-2.6, 8.6, 0, 0xb54339, 0.55, 0.55, 0.6);

/* Ship cargo */
addCargo(-5, 3.2, -1, 0.7);
addCargo(-5, 3.2, 1, 0.5);
addCargo(0, 3.2, -1, 0.8);
addCargo(0, 3.2, 1, 0.6);
addCargo(3, 3.2, 0, 0.7);

/* Water surface as animated voxel blocks */
const waterGeo = new THREE.BoxGeometry(1, 1, 1);
const waterMat = new THREE.MeshLambertMaterial();
const waterDeepColors = [0x2a6b88, 0x3a7f9f, 0x4b8f9f];
const waterNearColors = [0x5da5bf, 0x6cc0ce, 0x4895a8];

let waterCount = 0;
for (let x = -22; x <= 9; x++) {
  for (let z = -14; z <= 14; z++) {
    waterCount++;
  }
}

const waterMesh = new THREE.InstancedMesh(waterGeo, waterMat, waterCount);
waterMesh.receiveShadow = true;
waterMesh.castShadow = false;
scene.add(waterMesh);

const waterBase = [];
let wi = 0;
const dummy = new THREE.Object3D();
const tmpWaterColor = new THREE.Color();

for (let x = -22; x <= 9; x++) {
  for (let z = -14; z <= 14; z++) {
    const color = x > 5 ? pick(waterNearColors) : pick(waterDeepColors);
    tmpWaterColor.setHex(color);
    waterMesh.setColorAt(wi, tmpWaterColor);

    waterBase.push({
      x,
      z,
      phase: rnd() * 4.0,
      sx: 0.96,
      sy: 0.92,
      sz: 0.96
    });

    dummy.position.set(x, 0.35, z);
    dummy.scale.set(0.96, 0.92, 0.96);
    dummy.updateMatrix();
    waterMesh.setMatrixAt(wi, dummy.matrix);
    wi++;
  }
}

if (waterMesh.instanceColor) {
  waterMesh.instanceColor.needsUpdate = true;
}
waterMesh.instanceMatrix.needsUpdate = true;

function updateWater(t) {
  for (let i = 0; i < waterCount; i++) {
    const b = waterBase[i];
    const y = 0.35 + Math.sin(t * 1.8 + b.x * 0.38 + b.z * 0.27 + b.phase) * 0.12 + Math.sin(t * 3.2 + b.z * 0.2 + b.phase) * 0.04;

    dummy.position.set(b.x, y, b.z);
    dummy.scale.set(b.sx, b.sy, b.sz);
    dummy.updateMatrix();
    waterMesh.setMatrixAt(i, dummy.matrix);
  }
  waterMesh.instanceMatrix.needsUpdate = true;
}

/* Seagulls */
const birds = [];
const birdMat = new THREE.MeshLambertMaterial({ color: 0xf6f7fa });

for (let i = 0; i < 4; i++) {
  const group = new THREE.Group();

  const body = new THREE.Mesh(boxGeo, birdMat);
  body.scale.set(0.7, 0.3, 0.45);
  group.add(body);

  const wing1 = new THREE.Mesh(boxGeo, birdMat);
  wing1.scale.set(0.8, 0.12, 1.3);
  wing1.position.set(0, 0.18, -0.45);
  group.add(wing1);

  const wing2 = new THREE.Mesh(boxGeo, birdMat);
  wing2.scale.set(0.8, 0.12, 1.3);
  wing2.position.set(0, 0.18, 0.45);
  group.add(wing2);

  birds.push({
    group,
    wing1,
    wing2,
    phase: i * 1.7,
    radius: 7 + i * 2,
    height: 11 + i * 1.5,
    speed: 0.35 + i * 0.12
  });

  scene.add(group);
}

/* Finalize all static voxel blocks */
finalizeStatic();

/* Resize */
window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

/* Render loop */
renderer.setAnimationLoop((time) => {
  const t = time * 0.001;

  updateWater(t);

  lampLight.intensity = 0.75 + 0.45 * Math.sin(t * 2.2);
  lamp.scale.set(0.8 + Math.sin(t * 4) * 0.04, 0.55, 0.8);

  for (const bird of birds) {
    const a = t * bird.speed + bird.phase;
    bird.group.position.set(
      4 + Math.cos(a) * bird.radius,
      bird.height + Math.sin(t * 2 + bird.phase) * 0.5,
      Math.sin(a) * bird.radius
    );
    bird.group.rotation.y = -a + Math.PI / 2;

    const flap = Math.sin(t * 8 + bird.phase) * 0.55;
    bird.wing1.rotation.x = flap;
    bird.wing2.rotation.x = -flap;
  }

  controls.update();
  renderer.render(scene, camera);
});
</script>
</body>
</html>
```