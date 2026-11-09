Here is a complete single-file HTML scene. Save it as `index.html` and open it in Chrome. It uses Three.js from a CDN, so you need internet access.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Voxel Harbor — Sailing Ship Calling In</title>
<style>
  html, body {
    margin: 0;
    height: 100%;
    overflow: hidden;
    background: #102436;
  }

  #ui {
    position: fixed;
    top: 12px;
    left: 12px;
    z-index: 10;
    color: #12243a;
    font-family: system-ui, Segoe UI, Arial, sans-serif;
    pointer-events: none;
  }

  #ui h1 {
    margin: 0 0 6px;
    font-size: 16px;
  }

  #ui p {
    margin: 2px 0;
    font-size: 13px;
  }

  #controls {
    position: fixed;
    bottom: 12px;
    left: 12px;
    z-index: 10;
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    pointer-events: auto;
  }

  button {
    background: rgba(255, 255, 255, 0.85);
    border: 1px solid #779;
    border-radius: 6px;
    padding: 7px 10px;
    font-size: 13px;
    cursor: pointer;
  }

  button:hover {
    background: #fff;
  }
</style>
</head>
<body>

<div id="ui">
  <h1>Voxel Harbor — Sailing Ship Calling In</h1>
  <p>Left-drag: orbit · right-drag: pan · mouse wheel: zoom</p>
</div>

<div id="controls">
  <button id="reset">Reset</button>
  <button id="rotate">Auto-rotate: off</button>
  <button id="night">Night: off</button>
  <button id="zoomIn">Zoom in</button>
  <button id="zoomOut">Zoom out</button>
  <button id="full">Fullscreen</button>
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
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x7ec8e3);
scene.fog = new THREE.Fog(0x7ec8e3, 95, 250);

const camera = new THREE.PerspectiveCamera(
  48,
  window.innerWidth / window.innerHeight,
  0.1,
  500
);
camera.position.set(30, 24, 35);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.target.set(0, 4, 0);
controls.minDistance = 8;
controls.maxDistance = 140;
controls.maxPolarAngle = Math.PI * 0.49;

const boxes = [];
const waterBoxes = [];
const waterAnim = [];
const birds = [];
const pointLights = [];

function addBox(x, y, z, sx, sy, sz, color, opts = {}) {
  const b = {
    x,
    y,
    z,
    sx,
    sy,
    sz,
    color: new THREE.Color(color),
    opts
  };
  boxes.push(b);
  return boxes.length - 1;
}

function addWaterBox(x, y, z, sx, sy, sz, color, opts = {}) {
  const b = {
    x,
    y,
    z,
    sx,
    sy,
    sz,
    color: new THREE.Color(color),
    opts
  };
  waterBoxes.push(b);
  const idx = waterBoxes.length - 1;
  waterAnim.push({ idx, x, z, baseY: y, sx, sy, sz });
  return idx;
}

function addLine(x1, y1, z1, x2, y2, z2, color, size = 0.18) {
  const dx = x2 - x1;
  const dy = y2 - y1;
  const dz = z2 - z1;
  const steps = Math.max(
    1,
    Math.ceil(Math.max(Math.abs(dx), Math.abs(dy), Math.abs(dz)))
  );

  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    addBox(
      x1 + dx * t,
      y1 + dy * t,
      z1 + dz * t,
      size,
      size,
      size,
      color,
      { cast: false }
    );
  }
}

function addBuilding(xMin, xMax, zMin, zMax, h, wall, roof, hasDoor) {
  for (let y = 1.5; y <= h; y += 1) {
    for (let x = xMin; x <= xMax; x++) {
      for (let z = zMin; z <= zMax; z++) {
        if (x === xMin || x === xMax || z === zMin || z === zMax) {
          addBox(x, y, z, 1, 1, 1, wall);
        }
      }
    }
  }

  addBox(
    (xMin + xMax) / 2,
    h + 1,
    (zMin + zMax) / 2,
    xMax - xMin + 2,
    1,
    zMax - zMin + 2,
    roof
  );

  if (hasDoor) {
    addBox((xMin + xMax) / 2, 1.5, zMax, 0.8, 1.2, 0.12, 0x332014);
    addBox((xMin + xMax) / 2, 2.4, zMax, 0.45, 0.45, 0.12, 0x3a3028);
  }

  for (let x = xMin + 1; x <= xMax - 1; x++) {
    addBox(x, 2.5, zMin, 0.55, 0.55, 0.12, 0x3a3028);
    addBox(x, 2.5, zMax, 0.55, 0.55, 0.12, 0x3a3028);
  }
}

function addTree(x, z) {
  for (let y = 1.5; y <= 3.5; y += 1) {
    addBox(x, y, z, 1, 1, 1, 0x593d25);
  }

  for (let dx = -2; dx <= 2; dx++) {
    for (let dz = -2; dz <= 2; dz++) {
      if (Math.abs(dx) + Math.abs(dz) <= 2) {
        addBox(x + dx, 4.5, z + dz, 1, 1, 1, 0x38743f);
      }
    }
  }

  for (let dx = -2; dx <= 2; dx++) {
    for (let dz = -2; dz <= 2; dz++) {
      if (Math.abs(dx) + Math.abs(dz) <= 1.5) {
        addBox(x + dx, 5.5, z + dz, 1, 1, 1, 0x468450);
      }
    }
  }

  for (let dx = -1; dx <= 1; dx++) {
    for (let dz = -1; dz <= 1; dz++) {
      if (Math.abs(dx) + Math.abs(dz) <= 1) {
        addBox(x + dx, 6.5, z + dz, 1, 1, 1, 0x53965b);
      }
    }
  }

  addBox(x, 7.5, z, 1, 1, 1, 0x5f9f67);
}

function addBarrel(x, y, z) {
  addBox(x, y, z, 0.8, 1, 0.8, 0x9b6c43);
  addBox(x, y + 0.6, z, 0.9, 0.12, 0.9, 0x4c3322);
  addBox(x, y - 0.6, z, 0.9, 0.12, 0.9, 0x4c3322);
  addBox(x + 0.4, y, z, 0.12, 0.7, 0.7, 0x4c3322);
  addBox(x - 0.4, y, z, 0.12, 0.7, 0.7, 0x4c3322);
}

function addCrate(x, y, z, s) {
  addBox(x, y, z, s, s, s, 0x9b6c43);
  addBox(x, y + s / 2, z, s, s, 0.12, 0x5c3c24);
  addBox(x, y - s / 2, z, s, s, 0.12, 0x5c3c24);
  addBox(x, y, z + s / 2, s, 0.12, s, 0x5c3c24);
  addBox(x, y, z - s / 2, s, 0.12, s, 0x5c3c24);
  addBox(x, y, z, s, 0.12, 0.12, 0x5c3c24);
}

function addStall(x, z) {
  addBox(x, 1.5, z, 1, 1, 1, 0x856144);
  addBox(x, 2.5, z, 1.8, 1, 2.2, 0xf3ecd6);
  addBox(x, 3.5, z, 1.8, 0.35, 2.2, 0xc44b4b);
  addBox(x, 1.8, z, 1, 0.35, 2.2, 0xd27b39);
}

function addLamp(x, z) {
  addBox(x, 2.1, z, 0.2, 1.4, 0.2, 0x3d2e25);
  addBox(x, 3.2, z, 0.75, 0.75, 0.75, 0xffd47a);

  const light = new THREE.PointLight(0xffb565, 1.8, 8, 2);
  light.position.set(x, 3.2, z);
  light.visible = false;
  scene.add(light);
  pointLights.push(light);
}

function waterColor(x, z) {
  const n =
    Math.sin(x * 0.22 + z * 0.17) * 0.5 +
    Math.sin(x * 0.09 - z * 0.13) * 0.5 +
    Math.sin((x + z) * 0.25) * 0.3;

  const t = Math.max(0, Math.min(1, 0.55 + n * 0.25));

  const c = new THREE.Color(0x2d82b8).lerp(new THREE.Color(0x1f5c89), t);

  if (x >= 9 && z > -6 && z < 6) {
    c.lerp(new THREE.Color(0x79b9e5), 0.25);
  }

  return c;
}

/* Water */
for (let x = -34; x <= 14; x++) {
  for (let z = -34; z <= 34; z++) {
    addWaterBox(x, -0.5, z, 1, 1, 1, waterColor(x, z), { receive: true });
  }
}

/* Land */
for (let x = 15; x <= 35; x++) {
  for (let z = -34; z <= 34; z++) {
    const top =
      x <= 16
        ? 0xe6c58c
        : x <= 20
        ? 0x9ec36d
        : 0x6db36a;

    addBox(x, 0.5, z, 1, 1, 1, top);
    addBox(x, -0.5, z, 1, 1, 1, 0x6b6455);
  }
}

/* Seawall */
for (let z = -34; z <= 34; z++) {
  addBox(14, 1.0, z, 1, 2, 1, 0x848c96);
  addBox(14, 2.1, z, 1, 0.2, 1, 0x656e78);
}

/* Shore road */
for (let z = -30; z <= 30; z++) {
  addBox(16, 0.5, z, 1, 1, 1, 0x918e93);
  addBox(18, 0.5, z, 1, 1, 1, 0x88909c);
}

for (let x = 16; x <= 18; x++) {
  addBox(x, 0.5, 0, 1, 1, 1, 0x918e93);
}

/* Pier */
for (let x = -12; x <= 15; x++) {
  for (let z = -1; z <= 1; z++) {
    addBox(x, 1.0, z, 1, 1, 1, 0xb88055);
    addBox(x, 1.5, z, 1, 0.2, 1, 0x986d45);
  }
}

for (let x = -12; x <= 15; x += 3) {
  for (let z = -1; z <= 1; z++) {
    addBox(x, -0.5, z, 0.8, 1, 0.8, 0x4b3222);
    addBox(x, 0.5, z, 0.8, 1, 0.8, 0x4b3222);
  }
}

/* Pier railings */
for (let x = -12; x <= 15; x++) {
  addBox(x, 1.6, 1.6, 1, 0.55, 0.2, 0x7b5942);
  addBox(x, 1.6, -1.6, 1, 0.55, 0.2, 0x7b5942);
}

/* Bollards */
for (let x = -10; x <= 14; x += 4) {
  addBox(x, 1.4, 1.6, 0.8, 0.8, 0.8, 0x3d2e25);
}

/* Lamps on pier */
for (let x = -10; x <= 14; x += 4) {
  addLamp(x, 1.6);
}

addLamp(18, 0);
addLamp(22, 2);
addLamp(26, 14);
addLamp(30, 20);

/* Cargo */
addBarrel(-8, 1.8, 1.6);
addBarrel(-4, 1.8, 1.6);
addBarrel(6, 1.8, 1.6);
addBarrel(12, 1.8, 1.6);
addBarrel(20, 1.8, -3.5);

addCrate(-10, 1.9, 1.6, 1.0);
addCrate(-6, 1.9, 1.6, 1.0);
addCrate(2, 1.9, 1.6, 1.0);
addCrate(10, 1.9, 1.6, 1.0);
addCrate(24, 1.9, -12, 1.0);

/* Dock sign */
addBox(15, 2.0, 0, 0.12, 3, 0.12, 0x7b5942);
addBox(16.5, 3.0, 0, 2.2, 1, 0.12, 0xf3ecd6);
addBox(16.5, 3.5, 0, 1, 0.5, 0.12, 0xc44b4b);

/* Small rowboat */
addBox(-1, 0.45, 2, 3, 0.75, 1, 0x846134);
addBox(-1, 1.45, 2, 1, 0.7, 1, 0x5b3a23);
addBox(-1, 2.45, 2, 0.2, 2, 0.2, 0x4d321d);
addBox(-1, 2.45, 2, 0.15, 1.5, 1.0, 0xf6f4ea);

/* Warehouses and buildings */
addBuilding(22, 30, -14, -6, 3.5, 0xa96f4c, 0x8b3b3b, true);
addBuilding(18, 24, -8, -4, 2.5, 0xb57a55, 0x2e7d32, false);
addBuilding(28, 32, 12, 16, 2.5, 0xc9a46b, 0x3b7b3b, true);

/* Market stalls */
for (let x = 18; x <= 20; x++) {
  addStall(x, -2.8);
}

/* Lighthouse */
const LH = 30;
const LHZ = 20;

for (let y = 1.5; y <= 3.5; y += 1) {
  for (let dx = -1; dx <= 1; dx++) {
    for (let dz = -1; dz <= 1; dz++) {
      addBox(LH + dx, y, LHZ + dz, 1, 1, 1, 0x8b8b8b);
    }
  }
}

for (let y = 4.5, band = 0; y <= 11.0; y += 1, band++) {
  addBox(
    LH,
    y,
    LHZ,
    1,
    1,
    1,
    band % 2 === 0 ? 0xd85555 : 0xf7f7f7
  );
}

for (let dx = -1; dx <= 1; dx++) {
  for (let dz = -1; dz <= 1; dz++) {
    addBox(LH + dx, 11.5, LHZ + dz, 1, 1, 1, 0xf5e7a8);
  }
}

addBox(LH, 12.5, LHZ, 1, 1, 1, 0x222222);

const beamGroup = new THREE.Group();
const beamMesh = new THREE.Mesh(
  new THREE.BoxGeometry(80, 3, 3),
  new THREE.MeshBasicMaterial({
    color: 0xf7f4a0,
    transparent: true,
    opacity: 0.24,
    fog: false,
    depthWrite: false
  })
);

beamMesh.position.set(40, 0, 0);
beamGroup.position.set(LH, 12.5, LHZ);
beamGroup.add(beamMesh);
scene.add(beamGroup);

const beamLight = new THREE.PointLight(0xf7f4a0, 4, 90, 2);
beamLight.position.set(LH, 12.5, LHZ);
beamLight.visible = false;
scene.add(beamLight);
pointLights.push(beamLight);

/* Trees */
addTree(31, -25);
addTree(33, -15);
addTree(31, -2);
addTree(33, 4);
addTree(29, 18);
addTree(34, 26);
addTree(21, 26);
addTree(24, -22);

/* Fence */
for (let z = -30; z <= 30; z += 4) {
  addBox(17, 1.5, z, 1, 1, 1, 0x7b5942);
  addBox(17, 2.5, z, 1, 1, 1, 0x7b5942);
  addBox(17, 2.25, z, 1, 0.25, 1, 0x7b5942);
}

/* Breakwater */
for (let x = -5; x <= 5; x++) {
  for (let z = -32; z <= -26; z++) {
    addBox(x, 0.5, z, 1, 1, 1, 0x78808a);
    addBox(x, 1.5, z, 1, 1, 1, 0x87909a);
  }
}

/* Ship */
function shipHullLayer(y, color) {
  for (let x = -16; x <= 4; x++) {
    let zMin = 4;
    let zMax = 8;

    if (x === -16) {
      zMin = 6;
      zMax = 6;
    } else if (x === -15) {
      zMin = 5;
      zMax = 7;
    } else if (x === -14) {
      zMin = 4;
      zMax = 8;
    } else if (x === 4) {
      zMin = 6;
      zMax = 6;
    } else if (x === 3) {
      zMin = 5;
      zMax = 7;
    } else if (x === 2) {
      zMin = 4;
      zMax = 8;
    }

    for (let z = zMin; z <= zMax; z++) {
      addBox(x, y, z, 1, 1, 1, color);
    }
  }
}

shipHullLayer(-0.4, 0x3b2b1c);
shipHullLayer(0.3, 0x5b3a23);
shipHullLayer(1.2, 0x82532d);

/* Deck */
for (let x = -16; x <= 4; x++) {
  for (let z = 4; z <= 8; z++) {
    addBox(x, 1.7, z, 1, 0.25, 1, 0x9c723f);
  }
}

/* Deck rails */
for (let x = -16; x <= 4; x++) {
  addBox(x, 2.0, 4, 1, 0.45, 0.2, 0x7b5942);
  addBox(x, 2.0, 8, 1, 0.45, 0.2, 0x7b5942);
}

/* Gunwale stripe */
for (let x = -14; x <= 2; x++) {
  addBox(x, 1.2, 4, 1, 0.25, 0.2, 0xf1d5ac);
  addBox(x, 1.2, 8, 1, 0.25, 0.2, 0xf1d5ac);
}

/* Gun ports */
for (let x = -11; x <= -5; x += 3) {
  addBox(x, 1.0, 4, 0.6, 0.6, 0.15, 0x252525);
  addBox(x, 1.0, 8, 0.6, 0.6, 0.15, 0x252525);
}

/* Bow and stern */
addBox(-16, 1.3, 6, 0.7, 0.7, 0.7, 0xe0b66b);
addBox(-17, 1.3, 6, 0.7, 0.7, 0.7, 0x644a34);
addBox(4, 1.3, 6, 0.7, 1.2, 0.7, 0x3b2b1c);

/* Cabin */
for (let x = 0; x <= 3; x++) {
  for (let z = 5; z <= 7; z++) {
    addBox(x, 2.3, z, 1, 1, 1, 0x73523a);
  }
}

addBox(1.5, 2.8, 6, 4, 0.3, 4, 0x6b573f);
addBox(1, 2.5, 7, 0.55, 0.55, 0.15, 0x252525);
addBox(2, 2.5, 7, 0.55, 0.55, 0.15, 0x252525);
addBox(1.5, 1.9, 7, 1, 1, 0.15, 0x3b2f1c);

/* Cargo and lifeboat */
addBox(-11, 2.1, 6, 3, 0.7, 1, 0xb47746);
addBox(-6, 2.1, 6, 1, 1, 1, 0x9b6c43);
addBox(-5, 2.6, 6, 0.8, 0.7, 0.8, 0x9b6c43);
addBox(1, 2.5, 7, 0.7, 0.7, 0.7, 0x4c3322);

/* Masts */
function addMast(x, topY) {
  for (let y = 1.9; y <= topY; y += 1) {
    addBox(x, y, 6, 0.7, 1, 0.7, 0x4d321d);
  }

  addBox(x, topY, 6, 5, 0.5, 0.5, 0x4d321d);
}

addMast(-14, 12);
addMast(-8, 14);
addMast(-2, 10);

/* Sails */
function addSquareSail(x, yStart, yEnd, width, depth, color) {
  for (let y = yStart; y <= yEnd; y += 1) {
    addBox(x, y, 6, width, 1, depth, color);
  }
  addBox(x, yStart, 6, width, 0.2, depth, 0xf0d8b0);
}

addSquareSail(-14, 3, 8, 5, 3, 0xf7f5e8);
addSquareSail(-8, 4, 11, 7, 3, 0xf7f5e8);
addSquareSail(-2, 3, 7, 5, 3, 0xf7f5e8);

/* Bowsprit */
addBox(-17, 5, 6, 3, 0.6, 0.6, 0x4d321d);
addBox(-20, 4, 6, 0.4, 2, 0.4, 0x4d321d);

/* Jib */
for (let x = -17; x <= -14; x++) {
  addBox(x, 4, 6, 0.18, 1.5, 0.25, 0xf7f5e8);
}

/* Flags */
addBox(-14, 13.1, 6, 2, 1, 0.25, 0xd14c4c);
addBox(-8, 15.2, 6, 2.5, 1.2, 0.25, 0xd14c4c);
addBox(-2, 11.2, 6, 1.5, 1, 0.25, 0xd14c4c);
addBox(5, 3, 6, 1.2, 1.2, 0.25, 0xd14c4c);

/* Rigging */
addLine(-14, 13, 6, -20, 4, 6, 0x333333, 0.15);
addLine(-14, 13, 6, -10, 2, 6, 0x333333, 0.15);
addLine(-14, 13, 6, -18, 2, 6, 0x333333, 0.15);

addLine(-8, 15, 6, -12, 2, 6, 0x333333, 0.15);
addLine(-8, 15, 6, -4, 2, 6, 0x333333, 0.15);

addLine(-2, 11, 6, -6, 2, 6, 0x333333, 0.15);
addLine(-2, 11, 6, 2, 2, 6, 0x333333, 0.15);

/* Mooring ropes */
addLine(-14, 1.9, 4, -10, 1.4, 1.6, 0x755d44, 0.18);
addLine(-6, 1.9, 4, -4, 1.4, 1.6, 0x755d44, 0.18);
addLine(2, 1.9, 4, 4, 1.4, 1.6, 0x755d44, 0.18);
addLine(4, 1.9, 4, 6, 1.4, 1.6, 0x755d44, 0.18);

/* Birds */
function addBird(cx, cy, cz, r) {
  const idx = addBox(cx, cy, cz, 1.0, 0.45, 1.4, 0xffffff, { cast: false });

  birds.push({
    idx,
    cx,
    cy,
    cz,
    r,
    sx: 1.0,
    sy: 0.45,
    sz: 1.4,
    phase: Math.random() * 6.283
  });
}

addBird(-20, 10, 0, 15);
addBird(10, 14, 20, 18);
addBird(5, 12, -20, 16);
addBird(-10, 16, 10, 14);
addBird(20, 15, -10, 18);
addBird(-25, 13, -20, 16);
addBird(30, 18, 20, 20);
addBird(0, 20, 30, 22);

/* Sun and moon */
const sunMesh = new THREE.Mesh(
  new THREE.BoxGeometry(8, 8, 8),
  new THREE.MeshBasicMaterial({ color: 0xffd26b, fog: false })
);

sunMesh.position.set(60, 70, 40);
scene.add(sunMesh);

const moon = new THREE.Group();

const moonBox = new THREE.Mesh(
  new THREE.BoxGeometry(6, 6, 6),
  new THREE.MeshBasicMaterial({ color: 0xffffff, fog: false })
);

moonBox.castShadow = false;
moon.add(moonBox);
moon.position.set(65, 80, -35);
scene.add(moon);
moon.visible = false;

/* Lights */
const hemi = new THREE.HemisphereLight(0x7ec8e3, 0x9bc4d8, 0.85);
scene.add(hemi);

const sun = new THREE.DirectionalLight(0xffe5b0, 1.25);
sun.position.set(45, 70, 35);
sun.castShadow = true;

sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -85;
sun.shadow.camera.right = 85;
sun.shadow.camera.top = 85;
sun.shadow.camera.bottom = -85;
sun.shadow.camera.near = 1;
sun.shadow.camera.far = 260;

sun.target.position.set(0, 4, 0);
scene.add(sun);
scene.add(sun.target);

const moonLight = new THREE.PointLight(0x8899cc, 0, 300, 2);
moonLight.position.set(65, 80, -35);
scene.add(moonLight);

/* Instanced meshes */
function makeMesh(list, material, cast, receive) {
  if (list.length === 0) return null;

  const mesh = new THREE.InstancedMesh(
    new THREE.BoxGeometry(1, 1, 1),
    material,
    list.length
  );

  const dummy = new THREE.Object3D();

  for (let i = 0; i < list.length; i++) {
    const b = list[i];

    dummy.position.set(b.x, b.y, b.z);
    dummy.scale.set(b.sx, b.sy, b.sz);
    dummy.updateMatrix();

    mesh.setMatrixAt(i, dummy.matrix);
    mesh.setColorAt(i, b.color);
  }

  mesh.instanceMatrix.needsUpdate = true;

  if (mesh.instanceColor) {
    mesh.instanceColor.needsUpdate = true;
  }

  mesh.castShadow = cast;
  mesh.receiveShadow = receive;

  scene.add(mesh);

  return mesh;
}

const solidMaterial = new THREE.MeshStandardMaterial({
  color: 0xffffff,
  roughness: 0.85,
  metalness: 0.05,
  flatShading: true
});

const waterMaterial = new THREE.MeshStandardMaterial({
  color: 0xffffff,
  roughness: 0.45,
  metalness: 0.15,
  transparent: true,
  opacity: 0.9,
  flatShading: true
});

const solidMesh = makeMesh(boxes, solidMaterial, true, true);
const waterMesh = makeMesh(waterBoxes, waterMaterial, false, true);

/* UI */
let isNight = false;
let isRotating = false;

function applyNight() {
  const bg = new THREE.Color(isNight ? 0x122033 : 0x7ec8e3);
  scene.background = bg;
  scene.fog.color.copy(bg);

  hemi.intensity = isNight ? 0.28 : 0.85;
  hemi.color.set(isNight ? 0x224466 : 0x7ec8e3);
  hemi.groundColor.set(isNight ? 0x222831 : 0x9bc4d8);

  sun.intensity = isNight ? 0.18 : 1.25;
  sun.color.set(isNight ? 0x8899cc : 0xffe5b0);

  moonLight.intensity = isNight ? 0.35 : 0;

  sunMesh.visible = !isNight;
  moon.visible = isNight;

  for (const pl of pointLights) {
    pl.visible = isNight;
  }

  beamGroup.visible = isNight;

  document.getElementById("night").textContent =
    "Night: " + (isNight ? "on" : "off");
}

function zoom(factor) {
  const v = camera.position.clone().sub(controls.target);
  const len = Math.max(8, Math.min(140, v.length() * factor));
  v.setLength(len);
  camera.position.copy(controls.target).add(v);
}

document.getElementById("reset").onclick = () => {
  camera.position.set(30, 24, 35);
  controls.target.set(0, 4, 0);
  controls.update();
};

document.getElementById("rotate").onclick = () => {
  isRotating = !isRotating;
  controls.autoRotate = isRotating;
  controls.autoRotateSpeed = 1.2;

  document.getElementById("rotate").textContent =
    "Auto-rotate: " + (isRotating ? "on" : "off");
};

document.getElementById("night").onclick = () => {
  isNight = !isNight;
  applyNight();
};

document.getElementById("zoomIn").onclick = () => zoom(0.8);
document.getElementById("zoomOut").onclick = () => zoom(1.25);

document.getElementById("full").onclick = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen();
  } else {
    document.exitFullscreen();
  }
};

applyNight();

/* Animation */
const clock = new THREE.Clock();
const dummy = new THREE.Object3D();

function animate() {
  requestAnimationFrame(animate);

  const t = clock.getElapsedTime();
  controls.update();

  for (const w of waterAnim) {
    const y =
      w.baseY +
      Math.sin(t * 1.8 + w.x * 0.22 + w.z * 0.15) * 0.18;

    dummy.position.set(w.x, y, w.z);
    dummy.scale.set(w.sx, w.sy, w.sz);
    dummy.updateMatrix();
    waterMesh.setMatrixAt(w.idx, dummy.matrix);
  }

  if (waterMesh) {
    waterMesh.instanceMatrix.needsUpdate = true;
  }

  for (const b of birds) {
    dummy.position.set(
      b.cx + Math.cos(t * 0.25 + b.phase) * b.r,
      b.cy + Math.sin(t * 1.5 + b.phase) * 1.2,
      b.cz + Math.sin(t * 0.25 + b.phase) * b.r
    );

    dummy.scale.set(b.sx, b.sy, b.sz);
    dummy.updateMatrix();

    if (solidMesh) {
      solidMesh.setMatrixAt(b.idx, dummy.matrix);
    }
  }

  if (solidMesh) {
    solidMesh.instanceMatrix.needsUpdate = true;
  }

  beamGroup.rotation.y = t * 0.5;

  renderer.render(scene, camera);
}

animate();

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
</script>

</body>
</html>
```