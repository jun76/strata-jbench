```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Voxel Scene: Sailing Ship Calling at a Harbor</title>
<style>
  html, body {
    margin: 0;
    height: 100%;
    overflow: hidden;
    background: #bfe4f7;
  }
  canvas { display: block; }
  #info {
    position: fixed;
    left: 12px;
    bottom: 12px;
    font-family: monospace;
    font-size: 12px;
    color: #113346;
    background: rgba(255, 255, 255, 0.55);
    padding: 6px 10px;
    border-radius: 8px;
    pointer-events: none;
  }
</style>

<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.161.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.161.0/examples/jsm/"
  }
}
</script>
</head>

<body>
<div id="info">drag: orbit • scroll: zoom • right-drag: pan</div>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const scene = new THREE.Scene();
const SKY = 0xbfe4f7;
scene.background = new THREE.Color(SKY);
scene.fog = new THREE.Fog(SKY, 85, 230);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const camera = new THREE.PerspectiveCamera(
  45,
  window.innerWidth / window.innerHeight,
  0.1,
  600
);
camera.position.set(34, 22, 36);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(-1, 7, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.minDistance = 12;
controls.maxDistance = 170;
controls.maxPolarAngle = Math.PI * 0.49;

const hemi = new THREE.HemisphereLight(0x9fd8ff, 0x486075, 0.85);
scene.add(hemi);

const sun = new THREE.DirectionalLight(0xffd7a8, 1.35);
sun.position.set(45, 55, 25);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -85;
sun.shadow.camera.right = 85;
sun.shadow.camera.top = 85;
sun.shadow.camera.bottom = -85;
sun.shadow.camera.near = 10;
sun.shadow.camera.far = 250;
sun.shadow.bias = -0.0008;
scene.add(sun);

const fillLight = new THREE.DirectionalLight(0x6f99c0, 0.25);
fillLight.position.set(-30, 20, -20);
scene.add(fillLight);

const tmpPos = new THREE.Vector3();
const tmpScale = new THREE.Vector3(1, 1, 1);
const tmpQuat = new THREE.Quaternion();
const tmpMatrix = new THREE.Matrix4();
const tmpColor = new THREE.Color();

function noise3(x, y, z) {
  const n = Math.sin(x * 0.17 + y * 0.29 + z * 0.37) * 43758.545312;
  return n - Math.floor(n);
}

class VoxelBuilder {
  constructor(max = 12000, castShadow = false, receiveShadow = false) {
    this.max = max;
    this.count = 0;
    this.mesh = new THREE.InstancedMesh(
      new THREE.BoxGeometry(1, 1, 1),
      new THREE.MeshLambertMaterial(),
      max
    );
    this.mesh.castShadow = castShadow;
    this.mesh.receiveShadow = receiveShadow;
    this.mesh.frustumCulled = false;
  }

  add(x, y, z, color) {
    if (this.count >= this.max) return false;

    tmpPos.set(x, y, z);
    tmpScale.set(1, 1, 1);
    tmpMatrix.compose(tmpPos, tmpQuat, tmpScale);

    this.mesh.setMatrixAt(this.count, tmpMatrix);
    this.mesh.setColorAt(this.count, color);
    this.count++;
    return true;
  }

  addHex(x, y, z, hex, jitter = 0) {
    tmpColor.set(hex);
    if (jitter > 0) {
      const f = 0.90 + 0.14 * noise3(x, y, z);
      tmpColor.multiplyScalar(f);
    }
    return this.add(x, y, z, tmpColor);
  }

  fill(xStart, yStart, zStart, w, h, d, hex, jitter = 0) {
    if (w <= 0 || h <= 0 || d <= 0) return;
    for (let x = 0; x < w; x++) {
      for (let y = 0; y < h; y++) {
        for (let z = 0; z < d; z++) {
          this.addHex(xStart + x, yStart + y, zStart + z, hex, jitter);
        }
      }
    }
  }

  fillCenteredXY(cx, cyStart, cz, sx, sy, sz, hex, jitter = 0) {
    this.fill(
      cx - Math.floor(sx / 2),
      cyStart,
      cz - Math.floor(sz / 2),
      sx,
      sy,
      sz,
      hex,
      jitter
    );
  }

  finish(parent = scene) {
    this.mesh.count = this.count;
    this.mesh.instanceMatrix.needsUpdate = true;
    if (this.mesh.instanceColor) this.mesh.instanceColor.needsUpdate = true;
    parent.add(this.mesh);
  }
}

const waterBuilder = new VoxelBuilder(20000, false, true);
const cityBuilder = new VoxelBuilder(35000, true, true);
const shipBuilder = new VoxelBuilder(16000, true, true);

const shipGroup = new THREE.Group();
scene.add(shipGroup);

const LAND_X = 17;
const LAND_W = 22;
const LAND_Z_MIN = -26;
const LAND_Z_LEN = 53;

function hullHalfWidth(x) {
  if (x < -7 || x > 8) return -1;
  if (x === -7) return 1;
  if (x === -6) return 2;
  if (x === -5) return 3;
  if (x >= -4 && x <= 3) return 4;
  if (x === 4) return 3;
  if (x === 5) return 2;
  if (x === 6) return 1;
  if (x === 7) return 1;
  if (x === 8) return 0;
}

function isLand(x, z) {
  return x >= LAND_X && z >= LAND_Z_MIN && z <= LAND_Z_MIN + LAND_Z_LEN - 1;
}

function isShipWaterSkip(x, z) {
  if (x < -7 || x > 8) return false;
  const h = hullHalfWidth(x);
  if (h < 0) return false;
  return Math.abs(z) <= h;
}

function isFoamAdjacent(x, z) {
  if (x >= -7 && x <= 8) {
    const h = hullHalfWidth(x);
    if (h >= 0 && Math.abs(z) === h + 1) return true;
  }
  if (x === -8 && z === 0) return true;
  if (x === 9 && z === 0) return true;
  return false;
}

/* Sea */
for (let x = -48; x <= 48; x++) {
  for (let z = -48; z <= 48; z++) {
    if (isLand(x, z) || isShipWaterSkip(x, z)) continue;

    const wave =
      Math.sin(x * 0.42 + z * 0.23) * 0.09 +
      Math.sin(x * 0.17 - z * 0.38) * 0.07;
    const y = -0.5 + wave;

    let hex;
    const shoreFoam =
      x === LAND_X - 1 &&
      z >= LAND_Z_MIN &&
      z < LAND_Z_MIN + LAND_Z_LEN &&
      noise3(x, -1, z) > 0.55;

    if (isFoamAdjacent(x, z) && noise3(x, -1, z) > 0.42) hex = 0xe7fbf6;
    else if (shoreFoam) hex = 0xe7fbf6;
    else if (wave > 0.08) hex = 0x74c1d3;
    else if (wave < -0.08) hex = 0x176185;
    else hex = 0x3394b8;

    waterBuilder.addHex(x, y, z, hex, 0.06);
  }
}

/* Ship hull */
const woodDark = 0x523322;
const woodMid = 0x8b5634;
const woodStripe = 0xe6c772;
const deckColor = 0xb88250;
const railColor = 0x593722;
const mastColor = 0x432718;
const sailColor = 0xf5f1e4;

for (let x = -7; x <= 8; x++) {
  const h = hullHalfWidth(x);
  if (h < 0) continue;

  // Bottom fill
  for (let y = -3; y <= -2; y++) {
    for (let z = -h; z <= h; z++) {
      shipBuilder.addHex(x, y, z, woodDark, 0.07);
    }
  }

  // Side shell and bow/stern caps
  for (let y = -1; y <= 1; y++) {
    const col = y === -1 ? woodStripe : woodMid;

    if (h === 0) {
      shipBuilder.addHex(x, y, 0, col);
    } else {
      shipBuilder.addHex(x, y, -h, col);
      shipBuilder.addHex(x, y, h, col);
    }

    if (x === -7 || x === 7) {
      if (h === 0) {
        shipBuilder.addHex(x, y, 0, col);
      } else {
        for (let z = -h + 1; z <= h - 1; z++) {
          shipBuilder.addHex(x, y, z, col);
        }
      }
    }
  }

  // Deck
  for (let z = -h; z <= h; z++) {
    shipBuilder.addHex(x, 2, z, deckColor, 0.08);
  }

  // Rail
  if (h > 0) {
    shipBuilder.addHex(x, 3, -h, railColor);
    shipBuilder.addHex(x, 3, h, railColor);

    if (x === -7 || x === 7) {
      for (let z = -h + 1; z <= h - 1; z++) {
        shipBuilder.addHex(x, 3, z, railColor);
      }
    }
  } else if (x === 8) {
    shipBuilder.addHex(x, 3, 0, railColor);
  }
}

/* Stern cabin */
shipBuilder.fill(-6, 3, -3, 3, 3, 7, 0xf0e1c7, 0.03);
shipBuilder.fill(-5, 6, -2, 2, 1, 5, 0xa6493d, 0.04);
shipBuilder.fill(-4, 7, -1, 1, 1, 3, 0xa6493d, 0.03);

for (let x = -6; x <= -4; x++) {
  shipBuilder.addHex(x, 4, 4, 0x2d4450);
  shipBuilder.addHex(x, 4, -4, 0x2d4450);
}
shipBuilder.addHex(-3, 4, 0, 0x2d4450);

/* Masts */
function mast(x, height) {
  for (let y = 3; y <= height; y++) {
    shipBuilder.addHex(x, y, 0, mastColor, 0.05);
  }
}
mast(0, 16);   // main
mast(4, 14);   // fore
mast(-3, 12);  // mizzen

/* Yards */
function yard(x, y, half) {
  for (let z = -half; z <= half; z++) {
    if (z === 0) continue; // leave room for mast
    shipBuilder.addHex(x, y, z, 0x45271a, 0.05);
  }
}

yard(0, 7, 7);
yard(0, 10, 5);
yard(0, 13, 3);

yard(4, 7, 5);
yard(4, 10, 3);

yard(-3, 7, 4);
yard(-3, 10, 3);

/* Square sails */
function sail(x, y0, y1, half) {
  for (let y = y0; y <= y1; y++) {
    for (let z = -half; z <= half; z++) {
      if (z === 0) continue; // leave mast visible
      shipBuilder.addHex(x, y, z, sailColor, 0.06);
    }
  }
}

// Main
sail(0, 4, 6, 7);
sail(0, 8, 9, 5);
sail(0, 11, 12, 3);

// Fore
sail(4, 4, 6, 5);
sail(4, 8, 9, 3);
sail(4, 11, 12, 2);

// Mizzen
sail(-3, 4, 6, 4);
sail(-3, 8, 9, 3);

/* Bowsprit */
for (let i = 1; i <= 7; i++) {
  const x = 8 + i;
  const y = i <= 4 ? 3 : 2;
  shipBuilder.addHex(x, y, 0, 0x45271a, 0.05);
}

/* Jib sail */
for (let x = 5; x <= 14; x++) {
  const t = (x - 5) / 9;
  const yTop = 14 + (3 - 14) * t;
  const yBottom = 6 + (2 - 6) * t;
  const y0 = Math.ceil(yBottom);
  const y1 = Math.floor(yTop);

  for (let y = y0; y <= y1; y++) {
    shipBuilder.addHex(x, y, 0, 0xf6f2e3, 0.05);
  }
}

/* Deck cargo */
shipBuilder.fill(1, 3, 1, 2, 1, 2, 0x8b5e3c, 0.04);
shipBuilder.fill(1, 4, 1, 2, 1, 2, 0x6b4324, 0.03);

shipBuilder.fill(2, 3, -3, 2, 1, 2, 0xc59863, 0.04);
shipBuilder.fill(2, 4, -3, 2, 1, 2, 0x8d6536, 0.03);

/* Flags */
shipBuilder.addHex(0, 17, 0, 0xd94d38);
shipBuilder.addHex(1, 17, 0, 0xd94d38);
shipBuilder.addHex(2, 17, 0, 0xd94d38);
shipBuilder.addHex(4, 15, 0, 0xd94d38);
shipBuilder.addHex(-3, 13, 0, 0xd94d38);

/* Harbor land */
cityBuilder.fill(LAND_X, -1, LAND_Z_MIN, LAND_W, 1, LAND_Z_LEN, 0x6f6a5f, 0.05);
cityBuilder.fill(LAND_X, 0, LAND_Z_MIN, 1, 1, LAND_Z_LEN, 0xd8c58c, 0.04);
cityBuilder.fill(LAND_X + 1, 0, LAND_Z_MIN, 6, 1, LAND_Z_LEN, 0xa6a094, 0.04);
cityBuilder.fill(LAND_X + 7, 0, LAND_Z_MIN, LAND_W - 7, 1, LAND_Z_LEN, 0x6f9d5b, 0.05);

// Bollards along quay edge
for (let z = -24; z <= 24; z += 6) {
  cityBuilder.fill(17, 1, z, 1, 2, 1, 0x2b2b30, 0.04);
}

/* Helper for quay boxes */
function addQuayBox(cx, cz, baseHex, topHex) {
  cityBuilder.fill(cx - 1, 1, cz - 1, 2, 1, 2, baseHex, 0.06);
  cityBuilder.fill(cx - 1, 2, cz - 1, 2, 1, 2, topHex, 0.04);
}

/* Buildings */
function addBuilding(cx, cz, w, d, h, wallHex, roofHex) {
  cityBuilder.fill(
    cx - Math.floor(w / 2),
    1,
    cz - Math.floor(d / 2),
    w,
    h,
    d,
    wallHex,
    0.05
  );

  cityBuilder.fill(
    cx - Math.floor(w / 2) - 1,
    h + 1,
    cz - Math.floor(d / 2) - 1,
    w + 2,
    1,
    d + 2,
    roofHex,
    0.05
  );

  cityBuilder.fill(
    cx - Math.floor(w / 2),
    h + 2,
    cz - Math.floor(d / 2),
    w,
    1,
    d,
    roofHex,
    0.05
  );
}

// Warehouse near shore
addBuilding(25, 8, 6, 6, 4, 0xd5c5a4, 0xa14b3c);

// Windows for first warehouse
for (let x = 23; x <= 25; x++) {
  cityBuilder.addHex(x, 3, 11, 0xf0d17a);
}
cityBuilder.addHex(21, 2, 8, 0x355266);
cityBuilder.addHex(28, 2, 8, 0x355266);

// Second warehouse
addBuilding(28, -12, 7, 5, 5, 0x9bb3c9, 0x56758a);
for (let x = 26; x <= 30; x += 2) {
  cityBuilder.addHex(x, 3, -9, 0x70b5d6);
}
cityBuilder.addHex(24, 2, -12, 0x426b7d);

/* Lighthouse */
cityBuilder.fillCenteredXY(32, 1, -24, 5, 1, 5, 0xb2a998, 0.04);

for (let y = 2; y <= 12; y++) {
  const stripeWhite = Math.floor((y - 2) / 2) % 2 === 0;
  const hex = stripeWhite ? 0xf1efe6 : 0xc74b3a;
  cityBuilder.fillCenteredXY(32, y, -24, 3, 1, 3, hex, 0.02);
}

cityBuilder.fillCenteredXY(32, 13, -24, 5, 1, 5, 0xa8a396, 0.03);
cityBuilder.fillCenteredXY(32, 14, -24, 3, 4, 3, 0xf2e08d, 0.04);
cityBuilder.fillCenteredXY(32, 18, -24, 5, 1, 5, 0x8e3a30, 0.03);
cityBuilder.fillCenteredXY(32, 19, -24, 3, 1, 3, 0x5f251f, 0);

const harborLight = new THREE.PointLight(0xffee88, 0.75, 35);
harborLight.position.set(32, 15.5, -24);
harborLight.castShadow = false;
scene.add(harborLight);

/* Crane */
cityBuilder.fill(22, 1, -20, 1, 6, 1, 0x45454d, 0.04);
cityBuilder.fill(22, 7, -20, 6, 1, 1, 0x8a6a4a, 0.05);
cityBuilder.fill(27, 3, -20, 1, 4, 1, 0x2b2b33, 0);
addQuayBox(27, -20, 0xa27347, 0x5e3921);

/* Cargo on quay */
addQuayBox(19, 0, 0xa87749, 0x674125);
addQuayBox(20, -4, 0xc2a067, 0x7c5631);
addQuayBox(20, 16, 0xa87749, 0x674125);
addQuayBox(21, -2, 0xb86e45, 0x71422b);
addQuayBox(21, 20, 0xc2a067, 0x7c5631);
addQuayBox(24, -18, 0xa87749, 0x674125);
addQuayBox(31, 18, 0xc2a067, 0x7c5631);

/* Small boats near ship */
function addBoat(cx, cz) {
  cityBuilder.fill(cx - 1, 1, cz - 1, 3, 1, 2, 0xb87b4a, 0.06);
  cityBuilder.fill(cx - 1, 2, cz - 1, 3, 1, 2, 0x8d5d35, 0.04);
}

addBoat(12, 6);
addBoat(11, -8);

/* Palm trees / harbor vegetation */
function addPalm(x, z) {
  cityBuilder.fill(x, 1, z, 1, 6, 1, 0x8f5e3a, 0.04);
  cityBuilder.fill(x - 1, 7, z, 3, 1, 1, 0x55a047, 0.05);
  cityBuilder.fill(x, 7, z - 1, 1, 1, 3, 0x61b354, 0.05);
  cityBuilder.fill(x - 2, 8, z - 2, 3, 1, 3, 0x4e9741, 0.05);
}

addPalm(34, 20);
addPalm(30, 24);
addPalm(37, 16);

/* Finish meshes */
waterBuilder.finish(scene);
shipBuilder.finish(shipGroup);
cityBuilder.finish(scene);

/* Rigging lines attached to ship group */
const linePts = [];
function line(x1, y1, z1, x2, y2, z2) {
  linePts.push(new THREE.Vector3(x1, y1, z1), new THREE.Vector3(x2, y2, z2));
}

// Main mast shrouds
line(0, 16, 0, -3, 2, 4);
line(0, 16, 0, 3, 2, 4);
line(0, 16, 0, -3, 2, -4);
line(0, 16, 0, 3, 2, -4);

// Foremast shrouds
line(4, 14, 0, 1, 2, 3);
line(4, 14, 0, 7, 2, 3);
line(4, 14, 0, 1, 2, -3);
line(4, 14, 0, 7, 2, -3);

// Mizzen shrouds
line(-3, 12, 0, -6, 2, 2);
line(-3, 12, 0, -6, 2, -2);

// Stays
line(0, 16, 0, 8, 2, 0);
line(4, 14, 0, 8, 2, 0);
line(4, 14, 0, 15, 2, 0);
line(15, 2, 0, 8, 2, 0);
line(0, 16, 0, -7, 2, 0);

const rigMaterial = new THREE.LineBasicMaterial({
  color: 0xffffff,
  transparent: true,
  opacity: 0.55
});
const rigLines = new THREE.LineSegments(
  new THREE.BufferGeometry().setFromPoints(linePts),
  rigMaterial
);
shipGroup.add(rigLines);

/* Resize */
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

/* Gentle ship motion */
function animate(time) {
  requestAnimationFrame(animate);

  const t = time * 0.001;
  shipGroup.position.y = Math.sin(t * 0.65) * 0.04;
  shipGroup.rotation.z = Math.sin(t * 0.33) * 0.002;

  controls.update();
  renderer.render(scene, camera);
}

requestAnimationFrame(animate);
</script>
</body>
</html>
```