Save the following as something like `voxel-harbor.html` and open it in Chrome.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>Voxel Harbor — Sailing Ship Calling at Harbor</title>
<meta name="viewport" content="width=device-width,initial-scale=1" />
<style>
  html, body {
    margin: 0;
    height: 100%;
    overflow: hidden;
    background: #8ecff5;
  }
  canvas { display: block; }
  #ui {
    position: fixed;
    left: 12px;
    bottom: 12px;
    color: #103344;
    font-family: system-ui, Arial, sans-serif;
    font-size: 13px;
    opacity: 0.85;
    pointer-events: none;
    text-shadow: 0 1px 3px rgba(255,255,255,.55);
  }
</style>

<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.160.1/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.1/examples/jsm/"
  }
}
</script>
</head>
<body>
<div id="ui">Voxel Harbor — drag to orbit, scroll to zoom, right-drag to pan</div>

<script type="module">
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

/* Renderer */
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
document.body.appendChild(renderer.domElement);

/* Scene */
const scene = new THREE.Scene();
scene.background = new THREE.Color("#9fd9ff");
scene.fog = new THREE.Fog("#9fd9ff", 90, 235);

/* Camera */
const camera = new THREE.PerspectiveCamera(48, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(48, 34, 58);

/* Mouse controls */
const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 6, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.minDistance = 18;
controls.maxDistance = 170;
controls.maxPolarAngle = Math.PI * 0.49;
controls.autoRotate = true;
controls.autoRotateSpeed = 0.45;

renderer.domElement.addEventListener("pointerdown", () => {
  controls.autoRotate = false;
}, { once: true });

/* Lights */
const hemi = new THREE.HemisphereLight(0xdfefff, 0x35553a, 1.0);
scene.add(hemi);

const sun = new THREE.DirectionalLight(0xfff1c7, 3.0);
sun.position.set(65, 95, 25);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -90;
sun.shadow.camera.right = 90;
sun.shadow.camera.top = 90;
sun.shadow.camera.bottom = -90;
sun.shadow.camera.near = 1;
sun.shadow.camera.far = 260;
sun.shadow.bias = -0.0004;
scene.add(sun);

const fill = new THREE.DirectionalLight(0x8fbfff, 0.4);
fill.position.set(-60, 45, -45);
scene.add(fill);

/* Voxel geometry: bottom of each box is at y */
const boxGeo = new THREE.BoxGeometry(1, 1, 1);
boxGeo.translate(0, 0.5, 0);

/* Static voxel builder */
const staticMat = new THREE.MeshStandardMaterial({
  color: 0xffffff,
  roughness: 0.86,
  metalness: 0.0,
  flatShading: true
});

const MAX_STATIC = 200000;
const staticMesh = new THREE.InstancedMesh(boxGeo, staticMat, MAX_STATIC);
staticMesh.frustumCulled = false;
staticMesh.castShadow = true;
staticMesh.receiveShadow = true;
staticMesh.count = 0;
scene.add(staticMesh);
let staticCount = 0;

/* Glow voxel builder */
const glowMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
const MAX_GLOW = 20000;
const glowMesh = new THREE.InstancedMesh(boxGeo, glowMat, MAX_GLOW);
glowMesh.frustumCulled = false;
glowMesh.count = 0;
scene.add(glowMesh);
let glowCount = 0;

const dummy = new THREE.Object3D();
const tmpColor = new THREE.Color();

function color(hex, jitter = true) {
  tmpColor.set(hex);
  if (jitter) {
    const v = 0.92 + Math.random() * 0.16;
    tmpColor.multiplyScalar(v);
    tmpColor.r = Math.min(1, tmpColor.r);
    tmpColor.g = Math.min(1, tmpColor.g);
    tmpColor.b = Math.min(1, tmpColor.b);
  }
  return tmpColor;
}

function addBlock(x, y, z, w = 1, h = 1, d = 1, col = "#888", jitter = true) {
  if (staticCount >= MAX_STATIC) return;

  dummy.position.set(x, y, z);
  dummy.scale.set(w, h, d);
  dummy.rotation.set(0, 0, 0);
  dummy.updateMatrix();

  staticMesh.setMatrixAt(staticCount, dummy.matrix);
  staticMesh.setColorAt(staticCount, color(col, jitter));
  staticCount++;
}

function addGlow(x, y, z, w = 1, h = 1, d = 1, col = "#fff") {
  if (glowCount >= MAX_GLOW) return;

  dummy.position.set(x, y, z);
  dummy.scale.set(w, h, d);
  dummy.rotation.set(0, 0, 0);
  dummy.updateMatrix();

  glowMesh.setMatrixAt(glowCount, dummy.matrix);
  glowMesh.setColorAt(glowCount, color(col, false));
  glowCount++;
}

function fillRect(x0, x1, y0, y1, z0, z1, col, jitter = true) {
  if (x0 > x1 || y0 > y1 || z0 > z1) return;
  for (let x = x0; x <= x1; x++) {
    for (let y = y0; y <= y1; y++) {
      for (let z = z0; z <= z1; z++) {
        addBlock(x, y, z, 1, 1, 1, col, jitter);
      }
    }
  }
}

function slab(x0, x1, y, z0, z1, col, h = 1, jitter = true) {
  for (let x = x0; x <= x1; x++) {
    for (let z = z0; z <= z1; z++) {
      addBlock(x, y, z, 1, h, 1, col, jitter);
    }
  }
}

function addCylinder(cx, cz, bottomY, height, radius, col, jitter = true) {
  const rr = (radius + 0.45) * (radius + 0.45);
  for (let dy = 0; dy < height; dy++) {
    const c = typeof col === "function" ? col(dy) : col;
    for (let dz = -radius; dz <= radius; dz++) {
      for (let dx = -radius; dx <= radius; dx++) {
        if (dx * dx + dz * dz <= rr) {
          addBlock(cx + dx, bottomY + dy, cz + dz, 1, 1, 1, c, jitter);
        }
      }
    }
  }
}

function addVoxelLine(x1, y1, z1, x2, y2, z2, col, size = 0.28, step = 0.5) {
  const dx = x2 - x1;
  const dy = y2 - y1;
  const dz = z2 - z1;
  const len = Math.sqrt(dx * dx + dy * dy + dz * dz);
  const steps = Math.max(1, Math.round(len / step));

  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    addBlock(
      x1 + dx * t,
      y1 + dy * t - size * 0.5,
      z1 + dz * t,
      size, size, size,
      col,
      false
    );
  }
}

function addCargoAt(x, y, z, s = 1, col = "#8d5a34") {
  addBlock(x, y, z, s, s, s, col);
}

function addTree(cx, cz) {
  addBlock(cx, 2, cz, 1, 3, 1, "#5d4129");
  fillRect(cx - 2, cx + 2, 5, 6, cz - 2, cz + 2, "#2e7c35");
  fillRect(cx - 1, cx + 1, 7, 7, cz - 1, cz + 1, "#3fa044");
  addBlock(cx - 1, 8, cz, 1, 1, 1, "#3fa044");
}

function addHouse(cx, cz, wall = "#e3c99b", roof = "#6c3b36") {
  fillRect(cx - 2, cx + 2, 2, 4, cz - 2, cz + 2, wall);
  slab(cx - 2, cx + 2, 5, cz - 2, cz + 2, roof, 1, true);
  slab(cx - 1, cx + 1, 6, cz - 1, cz + 1, roof, 1, true);

  addBlock(cx - 3, 2, cz, 1, 2, 1, "#433022", false);
  addGlow(cx - 3, 4, cz - 1, 1, 1, 1, "#ffe08a");
  addGlow(cx - 3, 4, cz + 1, 1, 1, 1, "#ffe08a");
  addBlock(cx + 1, 5, cz, 1, 3, 1, "#5c4a46");
}

/* Animated water */
const waterMat = new THREE.MeshStandardMaterial({
  color: 0xffffff,
  flatShading: true,
  roughness: 0.32,
  metalness: 0.05,
  transparent: true,
  opacity: 0.88
});

const MAX_WATER = 12000;
const waterMesh = new THREE.InstancedMesh(boxGeo, waterMat, MAX_WATER);
waterMesh.frustumCulled = false;
waterMesh.receiveShadow = true;
waterMesh.count = 0;
scene.add(waterMesh);

let waterCount = 0;
const waterCells = [];

function isDry(x, z) {
  if (x >= 8 && x <= 28 && z >= -14 && z <= 20) return true;   // dock
  if (x >= 29 && z >= -20 && z <= 20) return true;             // land
  if (x >= 26 && x <= 42 && z >= 22 && z <= 26) return true;   // breakwater
  return false;
}

function waterColor(x, z) {
  if (x > 18 || z > 18) return "#2fb6c0";
  if (x > 8 || z > 8) return "#1f8fae";
  return "#166d96";
}

for (let x = -48; x <= 48; x++) {
  for (let z = -48; z <= 48; z++) {
    if (isDry(x, z)) continue;
    if (waterCount >= MAX_WATER) break;

    dummy.position.set(x, 0, z);
    dummy.scale.set(1, 1, 1);
    dummy.rotation.set(0, 0, 0);
    dummy.updateMatrix();

    waterMesh.setMatrixAt(waterCount, dummy.matrix);
    waterMesh.setColorAt(waterCount, color(waterColor(x, z), true));

    waterCells.push({ x, z, baseY: 0 });
    waterCount++;
  }
}

waterMesh.count = waterCount;
if (waterMesh.instanceMatrix) waterMesh.instanceMatrix.needsUpdate = true;
if (waterMesh.instanceColor) waterMesh.instanceColor.needsUpdate = true;

/* ======================= */
/* Build harbor and harbor */
/* ======================= */

/* Dock */
slab(8, 28, 1, -14, 20, "#c19a6b", 1, true);
slab(8, 9, 1, -14, 20, "#8d6c46", 1, true);

for (let z = -12; z <= 20; z += 5) {
  addBlock(8, -1, z, 1, 3, 1, "#503622");
  addBlock(18, -1, z, 1, 3, 1, "#503622");
  addBlock(28, -1, z, 1, 3, 1, "#503622");
}

for (let z = -10; z <= 18; z += 5) {
  addBlock(8, 2, z, 1, 1, 1, "#332b26", true);
}

/* Land */
slab(29, 30, 1, -20, 20, "#d4bf8b", 1, true); // sand edge
slab(31, 46, 1, -20, 20, "#4d8d3e", 1, true); // grass

/* Trees */
addTree(35, -18);
addTree(43, -18);
addTree(34, -2);
addTree(45, 16);

/* Cargo */
addCargoAt(11, 2, 8, 1.9, "#8b5b35");
addCargoAt(13.4, 2, 7, 1.4, "#a46f41");
addCargoAt(11, 2, 11, 1.2, "#946038");
addCargoAt(18, 2, -10, 1.7, "#8a5a32");
addCargoAt(20, 2, -11, 1.2, "#a0703f");

/* Barrels */
addCylinder(15, 7, 2, 2, 1, "#7b5432");
addCylinder(17, 9, 2, 2, 1, "#734d30");
addCylinder(13, 15, 2, 2, 1, "#7d5532");
addCylinder(21, -4, 2, 2, 1, "#734d30");

/* Crane */
function addCrane(x, z) {
  fillRect(x - 1, x + 1, 2, 3, z - 1, z + 1, "#5b422c");

  for (let y = 4; y <= 9; y++) {
    addBlock(x, y, z, 1, 1, 1, "#6a4a2f", false);
  }

  addBlock(x, 10, z, 1, 1, 1, "#4a321f", false);

  addVoxelLine(x, 10, z, x + 7, 8, z - 8, "#4b321e", 0.45, 0.7);
  addVoxelLine(x, 10, z, x - 4, 9, z + 2, "#4b321e", 0.35, 0.6);

  const hx = x + 7;
  const hz = z - 8;

  addVoxelLine(hx, 8, hz, hx, 3, hz, "#2d2d2d", 0.18, 0.5);
  addCargoAt(hx, 2, hz, 1.6, "#8f5c36");
}

addCrane(14, 16);

/* Warehouse */
fillRect(32, 42, 2, 6, 2, 14, "#9d4c3c", true);

for (let i = 0; i < 5; i++) {
  slab(32 + i, 42 - i, 7 + i, 2 + i, 14 - i, "#4b3a34", 1, true);
}

addBlock(31, 2, 8, 1, 2, 1, "#3d2a1c", false);

for (let z = 3; z <= 13; z += 2) {
  if (z === 8) continue;
  addGlow(31, 4, z, 1, 1, 1, "#ffe58f");
}

/* Small houses */
addHouse(36, -12, "#dcc1a0", "#6e3b33");
addHouse(42, -6, "#e0cfb0", "#5b3e2f");
addHouse(44, -16, "#d9b78d", "#7b4a39");

/* Breakwater */
fillRect(26, 42, 0, 1, 22, 26, "#77746f", true);

/* Lighthouse */
function lighthouseColor(dy) {
  return (dy % 4) < 2 ? "#f2f2f2" : "#e4575a";
}

addCylinder(38, 24, 2, 14, 2, lighthouseColor);

/* Gallery */
slab(35, 41, 16, 21, 27, "#2e2a2b", 1, true);

/* Light room */
for (let x = 36; x <= 40; x++) {
  for (let y = 17; y <= 18; y++) {
    for (let z = 22; z <= 26; z++) {
      const dx = x - 38;
      const dz = z - 24;
      if (dx * dx + dz * dz <= 4) {
        addGlow(x, y, z, 1, 1, 1, "#fff3a6");
      }
    }
  }
}

/* Roof and spire */
addCylinder(38, 24, 19, 2, 2, "#2a2526");
addBlock(38, 21, 24, 1, 3, 1, "#2a2526");

const lighthouseLight = new THREE.PointLight(0xffe28a, 140, 120, 2);
lighthouseLight.position.set(38, 18, 24);
scene.add(lighthouseLight);

/* Clouds (non-shadow glow blocks) */
for (let i = 0; i < 22; i++) {
  const x = -80 + Math.random() * 160;
  const z = -80 + Math.random() * 160;
  const y = 40 + Math.random() * 12;
  addGlow(
    x,
    y,
    z,
    10 + Math.random() * 12,
    2,
    8 + Math.random() * 8,
    "#e8f2ff"
  );
}

/* ================= */
/* Build sailing ship */
/* ================= */
function buildShip() {
  const cx = -2;
  const z0 = -12;
  const z1 = 11;

  for (let z = z0; z <= z1; z++) {
    let half;

    if (z === -12 || z === 11) {
      half = 0;
    } else if (z === -11 || z === 10) {
      half = 1;
    } else {
      half = 2;
    }

    const x0 = cx - half;
    const x1 = cx + half;

    for (let x = x0; x <= x1; x++) {
      addBlock(x, 0, z, 1, 1, 1, "#24130b");
      addBlock(x, 1, z, 1, 1, 1, "#3f2315");
      addBlock(x, 2, z, 1, 1, 1, "#7d3727");
    }

    if (z > z0) {
      const dHalf = Math.max(0, half - 1);
      for (let x = cx - dHalf; x <= cx + dHalf; x++) {
        addBlock(x, 3, z, 1, 1, 1, "#b88156");
      }

      if (half >= 1) {
        addBlock(x0, 3, z, 1, 1, 1, "#956042");
        if (x1 !== x0) addBlock(x1, 3, z, 1, 1, 1, "#956042");
      }
    }
  }

  /* Stern cabin */
  fillRect(-4, -1, 4, 5, -11, -8, "#7a4a28");
  slab(-4, -1, 6, -11, -8, "#432615", 1, true);
  slab(-3, -2, 7, -10, -9, "#432615", 1, true);

  addGlow(-5, 5, -10, 1, 1, 1, "#ffe58f");
  addGlow(0, 5, -10, 1, 1, 1, "#ffe58f");

  const sailColor = "#f5f0e1";

  function addSailRow(z, x0, x1, y0, y1, col = sailColor) {
    for (let x = x0; x <= x1; x++) {
      for (let y = y0; y <= y1; y++) {
        addBlock(x, y, z, 1, 1, 1, col, false);
      }
    }
  }

  function addMast(z, lowerY, lowerH, lowerW, upperY, upperH, upperW, flagColor) {
    const topY = upperY + upperH + 2;

    for (let y = 4; y <= topY; y++) {
      addBlock(cx, y, z, 1, 1, 1, "#654227", false);
    }

    const lx0 = cx - Math.floor(lowerW / 2);
    const lx1 = cx + Math.floor(lowerW / 2);

    for (let x = lx0; x <= lx1; x++) {
      addBlock(x, lowerY + lowerH, z, 1, 1, 1, "#563622", false);
    }

    addSailRow(z, lx0, lx1, lowerY, lowerY + lowerH - 1, "#f2ecdd");

    const ux0 = cx - Math.floor(upperW / 2);
    const ux1 = cx + Math.floor(upperW / 2);

    for (let x = ux0; x <= ux1; x++) {
      addBlock(x, upperY + upperH, z, 1, 1, 1, "#563622", false);
    }

    addSailRow(z, ux0, ux1, upperY, upperY + upperH - 1, "#f7f4e8");

    addBlock(cx, topY + 1, z, 1, 1, 1, "#4d3220", false);
    addBlock(cx + 1, topY + 1, z, 1, 1, 1, flagColor, false);
    addBlock(cx + 2, topY + 1, z, 1, 1, 1, flagColor, false);
    addBlock(cx + 2, topY, z, 1, 1, 1, flagColor, false);
  }

  addMast(7, 10, 5, 9, 16, 4, 7, "#265c9d");
  addMast(0, 9, 6, 11, 16, 5, 9, "#c23b38");
  addMast(-7, 11, 4, 7, 16, 3, 5, "#f0c93a");

  /* Bowsprit */
  for (let z = 12; z <= 15; z++) {
    addBlock(cx, 4, z, 1, 1, 1, "#654227", false);
  }

  addBlock(cx, 5, 15, 1, 1, 1, "#654227", false);

  /* Simple rigging / jib lines */
  addVoxelLine(cx, 5, 15, cx, 12, 7, "#3f2a1b", 0.2, 0.7);
  addVoxelLine(cx, 4, 12, cx, 10, 7, "#3f2a1b", 0.2, 0.7);

  /* Small side anchor suggestion */
  addBlock(cx - 3, 3, 9, 1, 1, 1, "#3c3c3c", false);
}

buildShip();

/* Mooring lines from ship to dock */
addVoxelLine(-2, 5, 10, 8, 3, 8, "#4a3524", 0.26, 0.55);
addVoxelLine(-2, 5, 10, 8, 3, 14, "#4a3524", 0.26, 0.55);
addVoxelLine(-4, 5, -3, 8, 3, -3, "#4a3524", 0.26, 0.55);

/* Harbor buoys */
function addBuoy(x, z, col) {
  addCylinder(x, z, 0, 1, 1, col);
  addBlock(x, 1, z, 1, 1, 1, col, false);
  addVoxelLine(x, 2, z, x, 5, z, "#2f2f2f", 0.18, 0.45);
  addBlock(x + 1, 5, z, 1, 1, 1, col, false);
}

addBuoy(-8, 22, "#d94848");
addBuoy(-14, 18, "#2f8d4c");

/* Finalize instanced meshes */
staticMesh.count = staticCount;
glowMesh.count = glowCount;

staticMesh.instanceMatrix.needsUpdate = true;
if (staticMesh.instanceColor) staticMesh.instanceColor.needsUpdate = true;

glowMesh.instanceMatrix.needsUpdate = true;
if (glowMesh.instanceColor) glowMesh.instanceColor.needsUpdate = true;

/* Animation */
const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);

  const t = clock.getElapsedTime();
  controls.update();

  /* Water wave animation */
  for (let i = 0; i < waterCells.length; i++) {
    const c = waterCells[i];

    const y =
      Math.sin(c.x * 0.17 + t * 0.9) * 0.14 +
      Math.sin(c.z * 0.13 - t * 0.7) * 0.12;

    dummy.position.set(c.x, c.baseY + y, c.z);
    dummy.scale.set(1, 1, 1);
    dummy.rotation.set(0, 0, 0);
    dummy.updateMatrix();

    waterMesh.setMatrixAt(i, dummy.matrix);
  }

  waterMesh.instanceMatrix.needsUpdate = true;

  /* Lighthouse pulse */
  lighthouseLight.intensity = 120 + Math.sin(t * 2.2) * 45;

  renderer.render(scene, camera);
}

animate();

/* Resize */
window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
</script>
</body>
</html>
```