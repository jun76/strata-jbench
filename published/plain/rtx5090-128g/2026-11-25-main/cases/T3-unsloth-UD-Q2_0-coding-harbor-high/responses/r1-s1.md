Here is a complete single-file HTML page. Paste it into a `.html` file and open it in Chrome.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Sailing Ship Calling at a Harbor — Voxel 3D Scene</title>
<style>
  html, body {
    margin: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
    background: #0b1a24;
    font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
  }

  canvas {
    display: block;
  }

  #info {
    position: fixed;
    left: 14px;
    top: 14px;
    color: #1d2b33;
    background: rgba(255, 255, 255, 0.82);
    padding: 12px 16px;
    border-radius: 12px;
    backdrop-filter: blur(6px);
    box-shadow: 0 4px 18px rgba(0, 0, 0, 0.18);
    user-select: none;
    pointer-events: none;
    max-width: 300px;
    line-height: 1.35;
  }

  #info b {
    font-size: 15px;
    display: block;
    margin-bottom: 4px;
  }

  #info span {
    font-size: 12px;
    opacity: 0.8;
  }

  #fallback {
    position: fixed;
    right: 14px;
    bottom: 14px;
    color: #fff;
    background: rgba(0, 0, 0, 0.72);
    padding: 10px 14px;
    border-radius: 10px;
    font-size: 12px;
    z-index: 10;
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

<div id="info">
  <b>Sailing Ship Calling at a Harbor</b>
  <span>Drag to orbit • Scroll/pinch to zoom • Right-drag to pan</span>
</div>

<div id="fallback">Loading Three.js… If this stays, check WebGL or network.</div>

<script type="module">
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

const fallback = document.getElementById("fallback");
if (fallback) fallback.style.display = "none";

/* ----------------------------------------------------------
   Renderer, scene, camera, controls
---------------------------------------------------------- */
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.08;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();

const horizon = new THREE.Color("#d7eff8");
scene.fog = new THREE.Fog(horizon, 65, 240);

/* Gradient sky background */
const skyCanvas = document.createElement("canvas");
skyCanvas.width = 2;
skyCanvas.height = 512;
const skyCtx = skyCanvas.getContext("2d");
const skyGradient = skyCtx.createLinearGradient(0, 0, 0, 512);
skyGradient.addColorStop(0.00, "#49a8f2");
skyGradient.addColorStop(0.45, "#a8dcf8");
skyGradient.addColorStop(1.00, "#d7eff8");
skyCtx.fillStyle = skyGradient;
skyCtx.fillRect(0, 0, 2, 512);

const skyTexture = new THREE.CanvasTexture(skyCanvas);
skyTexture.colorSpace = THREE.SRGBColorSpace;
scene.background = skyTexture;

const camera = new THREE.PerspectiveCamera(58, window.innerWidth / window.innerHeight, 0.1, 600);
camera.position.set(36, 26, 46);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(4, 5, 6);
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.minDistance = 18;
controls.maxDistance = 180;
controls.maxPolarAngle = Math.PI / 2 - 0.04;
controls.autoRotate = true;
controls.autoRotateSpeed = 0.35;

controls.addEventListener("start", () => {
  controls.autoRotate = false;
});

/* ----------------------------------------------------------
   Lights
---------------------------------------------------------- */
const hemi = new THREE.HemisphereLight(0xbfdfff, 0x50778a, 0.85);
scene.add(hemi);

const sun = new THREE.DirectionalLight(0xffefc0, 1.7);
sun.position.set(55, 70, 28);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.near = 1;
sun.shadow.camera.far = 280;
sun.shadow.camera.left = -95;
sun.shadow.camera.right = 95;
sun.shadow.camera.top = 95;
sun.shadow.camera.bottom = -95;
sun.shadow.bias = -0.002;
sun.target.position.set(0, 2, 0);
scene.add(sun.target);

/* ----------------------------------------------------------
   Voxel builder
---------------------------------------------------------- */
class VoxelBuilder {
  constructor(parent, max = 200000) {
    this.parent = parent;
    this.max = max;
    this.count = 0;
    this.positions = [];
    this.colors = [];
    this.geometry = new THREE.BoxGeometry(1, 1, 1);
    this.material = new THREE.MeshLambertMaterial({ color: 0xffffff });
  }

  add(x, y, z, color) {
    if (this.count >= this.max) return;
    this.positions.push(x, y, z);
    this.colors.push(color);
    this.count++;
  }

  build() {
    if (this.count === 0) return null;

    const mesh = new THREE.InstancedMesh(this.geometry, this.material, this.count);
    const dummy = new THREE.Object3D();
    const col = new THREE.Color();

    for (let i = 0; i < this.count; i++) {
      const o = i * 3;
      dummy.position.set(this.positions[o], this.positions[o + 1], this.positions[o + 2]);
      dummy.updateMatrix();
      mesh.setMatrixAt(i, dummy.matrix);

      col.set(this.colors[i]);
      mesh.setColorAt(i, col);
    }

    mesh.castShadow = true;
    mesh.receiveShadow = true;
    mesh.instanceMatrix.needsUpdate = true;
    if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
    mesh.computeBoundingSphere();

    this.parent.add(mesh);
    return mesh;
  }
}

const P = {
  grass: 0x77a55c,
  grassDark: 0x628d4f,
  sand: 0xe7cf9b,
  sandDark: 0xd1b986,
  dirt: 0x826242,
  dirtDark: 0x694d34,
  rock: 0x95887b,
  rockDark: 0x716457,
  rockLight: 0xb4a492,
  wood: 0x8b5a31,
  woodDark: 0x57351f,
  woodMid: 0xa67446,
  deck: 0xb28c5d,
  deckDark: 0x906f49,
  stone: 0xb8a180,
  lighthouseRed: 0xc54f4f,
  dark: 0x3b3029
};

let seed = 937;
function rnd() {
  seed = (seed * 1664525 + 1013904223) >>> 0;
  return seed / 4294967296;
}

function addBox(b, x1, x2, y1, y2, z1, z2, color) {
  if (x1 > x2) { const t = x1; x1 = x2; x2 = t; }
  if (y1 > y2) { const t = y1; y1 = y2; y2 = t; }
  if (z1 > z2) { const t = z1; z1 = z2; z2 = t; }

  for (let x = x1; x <= x2; x++) {
    for (let y = y1; y <= y2; y++) {
      for (let z = z1; z <= z2; z++) {
        b.add(x, y, z, color);
      }
    }
  }
}

function addLineVox(b, x1, y1, z1, x2, y2, z2, color, thickness = 1) {
  const dx = x2 - x1;
  const dy = y2 - y1;
  const dz = z2 - z1;
  const steps = Math.max(1, Math.max(Math.abs(dx), Math.max(Math.abs(dy), Math.abs(dz))));

  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    const x = Math.round(x1 + dx * t);
    const y = Math.round(y1 + dy * t);
    const z = Math.round(z1 + dz * t);

    if (thickness <= 1) {
      b.add(x, y, z, color);
    } else {
      for (let ox = 0; ox < thickness; ox++) {
        for (let oz = 0; oz < thickness; oz++) {
          b.add(x + ox, y, z + oz, color);
        }
      }
    }
  }
}

/* ----------------------------------------------------------
   Water
---------------------------------------------------------- */
const waterLevel = 0.28;

const waterMat = new THREE.MeshPhongMaterial({
  color: 0x296c8c,
  specular: 0x8fe1f4,
  shininess: 45,
  transparent: true,
  opacity: 0.82,
  depthWrite: false
});

const water = new THREE.Mesh(new THREE.PlaneGeometry(600, 600), waterMat);
water.geometry.rotateX(-Math.PI / 2);
water.position.y = waterLevel;
water.renderOrder = 0;
scene.add(water);

const grid = new THREE.GridHelper(600, 160, 0x9adff2, 0x286d8a);
grid.position.y = waterLevel + 0.005;
grid.renderOrder = 1;
const gridMaterials = Array.isArray(grid.material) ? grid.material : [grid.material];
for (const mat of gridMaterials) {
  mat.transparent = true;
  mat.opacity = 0.22;
  mat.depthWrite = false;
}
scene.add(grid);

/* ----------------------------------------------------------
   Harbor static voxels
---------------------------------------------------------- */
const harbor = new VoxelBuilder(scene, 250000);

/* Land / grass */
for (let x = -60; x <= 16; x++) {
  for (let z = -60; z <= -8; z++) {
    const n = Math.abs(x * 7 + z * 11);
    harbor.add(x, 1, z, n % 11 === 0 ? P.grassDark : P.grass);
    harbor.add(x, 0, z, n % 5 === 0 ? P.dirtDark : P.dirt);
  }
}

/* Shore sand strip */
for (let x = -24; x <= 14; x++) {
  harbor.add(x, 0, -9, Math.abs(x) % 3 === 0 ? P.sandDark : P.sand);
}

/* Wooden dock */
for (let x = -20; x <= 14; x++) {
  for (let z = -7; z <= -3; z++) {
    const n = Math.abs(x + z);
    harbor.add(x, 1, z, n % 7 === 0 ? P.woodDark : P.woodMid);
  }
}

/* Dock supports */
for (let x = -18; x <= 12; x += 3) {
  for (let z = -6; z <= -4; z += 2) {
    for (let y = 0; y >= -1; y--) {
      harbor.add(x, y, z, P.woodDark);
    }
  }
}

/* Bollards */
for (let x = -18; x <= 14; x += 3) {
  harbor.add(x, 2, -3, P.woodDark);
}

/* Cargo crates and barrels */
const crateColors = [0xd7c18f, 0x9c6b3f, 0x7f8c95, 0xa5c39a];
for (let x = -16; x <= 10; x += 4) {
  if (rnd() < 0.68) {
    const z = -5 + (rnd() < 0.5 ? 0 : -1);
    const c = crateColors[Math.floor(rnd() * crateColors.length)];
    harbor.add(x, 2, z, c);
    harbor.add(x, 3, z, c === crateColors[0] ? 0xbba778 : 0x774d30);
  }
}

for (let x = -14; x <= 12; x += 6) {
  if (rnd() < 0.45) {
    harbor.add(x, 2, -6, 0x8a5f2f);
    harbor.add(x, 3, -6, 0x644220);
  }
}

/* Cranes */
function addCrane(x, z) {
  addBox(harbor, x, x, 2, 7, z, z, P.woodDark);
  addLineVox(harbor, x, 7, z, x + 6, 5, z, P.woodDark);
  addLineVox(harbor, x, 7, z, x - 2, 5, z, P.woodDark);
  addLineVox(harbor, x + 6, 5, z, x + 6, 2, z, 0xa99065);
  addBox(harbor, x + 5, x + 7, 2, 3, z, z, 0x8b5a31);
}
addCrane(0, -4);
addCrane(-12, -5);

/* Town houses */
const houseWalls = [
  0xe8cfa0, 0xc98686, 0x86a7c9,
  0x9fbf9b, 0xe8b87a, 0xa6c3d8,
  0xd7a6c4, 0xf0d8a8
];
const houseRoofs = [
  0x8c3a3a, 0x3a4f8c,
  0x5e6e55, 0x7a4e2c,
  0x614141, 0x475a6a
];

function addHouse(x, z, w, d, h, wall, roof) {
  const half = Math.floor(w / 2);
  const zHalf = Math.floor(d / 2);
  const x1 = x - half;
  const x2 = x + half;
  const z1 = z - zHalf;
  const z2 = z + zHalf;

  for (let xx = x1; xx <= x2; xx++) {
    for (let yy = 2; yy <= 2 + h; yy++) {
      for (let zz = z1; zz <= z2; zz++) {
        const n = Math.abs(xx + yy + zz);
        harbor.add(xx, yy, zz, n % 17 === 0 ? P.dirt : wall);
      }
    }
  }

  const roofH = Math.max(1, Math.ceil(Math.max(w, d) / 2));
  const ry = 3 + h;
  for (let s = 0; s < roofH; s++) {
    const sx1 = x1 + s;
    const sx2 = x2 - s;
    const sz1 = z1 + s;
    const sz2 = z2 - s;
    if (sx1 > sx2 || sz1 > sz2) break;
    addBox(harbor, sx1, sx2, ry + s, ry + s, sz1, sz2, roof);
  }

  /* Small windows/doors protruding a bit from the wall */
  for (let wx = x1 + 1; wx <= x2 - 1; wx += 2) {
    harbor.add(wx, 4, z1 - 1, 0x23303c);
    harbor.add(wx, 4, z2 + 1, 0x23303c);
  }
  harbor.add(x, 2, z1 - 1, 0x3b2517);
  harbor.add(x, 2, z2 + 1, 0x3b2517);
}

function addWarehouse(x, z) {
  addBox(harbor, x - 3, x + 3, 2, 4, z - 1, z + 1, 0x9b7f5e);
  addBox(harbor, x - 2, x + 2, 5, 5, z - 1, z + 1, 0x77583f);
  addBox(harbor, x, x, 2, 3, z - 2, z - 2, 0x3b2517);
}

function addChurch(x, z) {
  addBox(harbor, x - 3, x + 3, 2, 5, z - 3, z + 3, 0xf3ead7);

  for (let s = 0; s < 4; s++) {
    addBox(harbor,
      x - 3 + s, x + 3 - s,
      6 + s, 6 + s,
      z - 3 + s, z + 3 - s,
      s % 2 ? 0x465c73 : 0x3e5166
    );
  }

  addBox(harbor, x - 1, x + 1, 2, 9, z + 4, z + 5, 0xf5efe1);
  addBox(harbor, x, x, 10, 13, z + 4, z + 5, 0x344251);
  harbor.add(x, 8, z + 6, 0xffffff);
}

function buildTown() {
  for (let x = -28; x <= 10; x += 8) {
    for (let z = -40; z <= -15; z += 7) {
      if (Math.abs(x + 8) < 14 && Math.abs(z + 26) < 14) continue;
      if (rnd() < 0.18) continue;

      const w = rnd() < 0.5 ? 3 : 5;
      const d = rnd() < 0.5 ? 3 : 5;
      const h = 2 + Math.floor(rnd() * 3);
      const wall = houseWalls[Math.floor(rnd() * houseWalls.length)];
      const roof = houseRoofs[Math.floor(rnd() * houseRoofs.length)];

      addHouse(x, z, w, d, h, wall, roof);
    }
  }
}
buildTown();

addWarehouse(-16, -10);
addWarehouse(-6, -10);
addWarehouse(6, -10);
addChurch(-8, -26);

/* Breakwaters */
function rockColor(x, z) {
  const n = Math.abs(x + z) % 3;
  if (n === 0) return P.rockDark;
  if (n === 1) return P.rock;
  return P.rockLight;
}

function buildBreakwater(x1, z1, x2, z2) {
  const steps = Math.max(1, Math.max(Math.abs(x2 - x1), Math.abs(z2 - z1)));

  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    const x = Math.round(x1 + (x2 - x1) * t);
    const z = Math.round(z1 + (z2 - z1) * t);

    for (let ox = -1; ox <= 1; ox++) {
      for (let oz = -1; oz <= 1; oz++) {
        const bx = x + ox;
        const bz = z + oz;
        const height = ((Math.abs(bx * 7 + bz * 5) & 1) ? 1 : 2);
        addBox(harbor, bx, bx, -1, height, bz, bz, rockColor(bx, bz));
      }
    }
  }
}

buildBreakwater(-20, -8, -12, 12);
buildBreakwater(18, -8, 14, 4);

/* Lighthouse */
function buildLighthouse(x, z) {
  addBox(harbor, x - 2, x + 2, 1, 2, z - 2, z + 2, P.stone);

  for (let y = 3; y <= 13; y++) {
    const half = y < 11 ? 2 : 1;
    const band = Math.floor((y - 3) / 3) % 2 ? P.lighthouseRed : 0xf7f7f7;
    addBox(harbor, x - half, x + half, y, y, z - half, z + half, band);
  }

  addBox(harbor, x - 2, x + 2, 14, 14, z - 2, z + 2, 0x50575e);
  addBox(harbor, x - 1, x + 1, 15, 15, z - 1, z + 1, 0xfff1b0);
  addBox(harbor, x, x, 16, 16, z, z, 0x2e363f);
}
buildLighthouse(-12, 10);

/* Right beacon */
addBox(harbor, 14, 14, 1, 5, 4, 4, P.woodDark);
const beaconLampMat = new THREE.MeshBasicMaterial({ color: 0xffd367 });
const beaconLamp = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), beaconLampMat);
beaconLamp.position.set(14, 5.6, 4);
scene.add(beaconLamp);

/* Lighthouse lamp glow + rotating beam */
const lampGlowMat = new THREE.MeshBasicMaterial({ color: 0xffef9a });
const lampGlow = new THREE.Mesh(new THREE.BoxGeometry(1.5, 1.0, 1.5), lampGlowMat);
lampGlow.position.set(-12, 15.2, 10);
scene.add(lampGlow);

const beamGroup = new THREE.Group();
const beamMat = new THREE.MeshBasicMaterial({
  color: 0xffe9a8,
  transparent: true,
  opacity: 0.09,
  depthWrite: false,
  side: THREE.DoubleSide
});
const beamGeo = new THREE.BoxGeometry(24, 1.4, 3.5);
beamGeo.translate(12, 0, 0);
const beam = new THREE.Mesh(beamGeo, beamMat);
beamGroup.add(beam);
beamGroup.position.set(-12, 15.2, 10);
beamGroup.renderOrder = 2;
scene.add(beamGroup);

harbor.build();

/* ----------------------------------------------------------
   Buoys
---------------------------------------------------------- */
const buoys = [];

function addBuoy(x, z, baseColor, lightColor) {
  const g = new THREE.Group();

  const base = new THREE.Mesh(
    new THREE.BoxGeometry(1, 1, 1),
    new THREE.MeshPhongMaterial({ color: baseColor })
  );
  g.add(base);

  const mid = new THREE.Mesh(
    new THREE.BoxGeometry(0.6, 1, 0.6),
    new THREE.MeshPhongMaterial({ color: 0xf5f5f5 })
  );
  mid.position.y = 1;
  g.add(mid);

  const lampMat = new THREE.MeshBasicMaterial({ color: lightColor });
  const lamp = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.5, 0.5), lampMat);
  lamp.position.y = 2;
  g.add(lamp);

  g.position.set(x, 0.45, z);
  scene.add(g);

  buoys.push({
    g,
    lampMat,
    onColor: new THREE.Color(lightColor),
    offColor: new THREE.Color(0x2b2b2b),
    phase: rnd() * Math.PI * 2,
    freq: 1.0 + rnd() * 0.7
  });
}

addBuoy(18, 2, 0xd04b39, 0xffd86b);
addBuoy(-20, 16, 0x2f7f4f, 0xffd86b);
addBuoy(8, 20, 0xd04b39, 0xffd86b);

/* ----------------------------------------------------------
   Ship
---------------------------------------------------------- */
const shipGroup = new THREE.Group();
const ship = new VoxelBuilder(shipGroup, 35000);

function buildShip(v) {
  const hullDark = 0x2e1d12;
  const hullWood = 0x8c5a30;
  const hullMid = 0xa46f3d;
  const trim = 0xe5c97f;
  const deck = 0xa98051;
  const deckDark = 0x8f6942;
  const mastWood = 0x5d3f26;
  const sailA = 0xf3ecd8;
  const sailB = 0xe6dbc1;

  function halfBeam(x) {
    let h = 5;

    if (x > -7 && x < 6) h = 6;
    else if (x < -9) h = Math.max(1, 5 - (-9 - x));
    else if (x > 9) h = Math.max(2, 5 - (x - 9));

    return h;
  }

  /* Hull */
  for (let x = -13; x <= 12; x++) {
    const half = halfBeam(x);
    for (let z = -half; z <= half; z++) {
      const edge = Math.abs(z) === half;

      if (edge) {
        v.add(x, 0, z, 0x362214);
        v.add(x, 1, z, Math.abs(x) % 4 === 0 ? trim : hullMid);
      } else {
        v.add(x, 0, z, hullDark);
        v.add(x, 1, z, hullWood);
      }
    }
  }

  /* Main deck */
  for (let x = -12; x <= 11; x++) {
    const half = halfBeam(x) - 1;
    if (half < 0) continue;

    for (let z = -half; z <= half; z++) {
      if (x >= 9 && Math.abs(z) <= 3) continue;
      v.add(x, 2, z, Math.abs(x + z) % 3 === 0 ? deckDark : deck);
    }
  }

  /* Railings */
  for (let x = -12; x <= 12; x++) {
    const half = halfBeam(x);
    if (half <= 1) continue;

    for (let z = -half; z <= half; z++) {
      if (x >= 9 && Math.abs(z) <= 3) continue;

      if (Math.abs(z) === half) {
        if (x % 2 === 0 || Math.abs(z) % 2 === 0) {
          v.add(x, 3, z, mastWood);
        }
      }

      if ((x === -12 || x === 12) && Math.abs(z) < half) {
        v.add(x, 3, z, mastWood);
      }
    }
  }

  /* Stern castle */
  addBox(v, 9, 12, 2, 3, -3, 3, hullDark);
  addBox(v, 8, 12, 4, 4, -3, 3, deck);
  addBox(v, 9, 11, 5, 5, -2, 2, hullDark);

  for (let wx = 9; wx <= 12; wx += 1) {
    if (wx % 2 === 1) {
      v.add(wx, 3, 4, 0x2b363f);
      v.add(wx, 3, -4, 0x2b363f);
    }
  }

  /* Bowsprit */
  addLineVox(v, -13, 2, 0, -17, 3, 0, mastWood);

  /* Masts */
  function mast(x, h) {
    for (let y = 3; y <= h; y++) {
      v.add(x, y, 0, mastWood);
    }
  }
  mast(-8, 13);   /* fore mast */
  mast(0, 15);    /* main mast */
  mast(8, 11);    /* mizzen mast */

  function yard(x, y, w) {
    addBox(v, x, x, y, y, -Math.floor(w / 2), Math.floor(w / 2), mastWood);
  }

  function sail(x, y1, y2, w) {
    const hw = Math.floor(w / 2);
    for (let y = y1; y <= y2; y++) {
      for (let z = -hw; z <= hw; z++) {
        v.add(x, y, z, ((y + z) % 2 === 0) ? sailA : sailB);
      }
    }
  }

  /* Square sails. Sails are offset 1 voxel along x so they do not overlap masts. */
  sail(-7, 9, 12, 8);
  yard(-7, 13, 9);

  sail(-7, 5, 8, 9);
  yard(-7, 9, 10);

  sail(1, 10, 14, 10);
  yard(1, 15, 11);

  sail(1, 5, 9, 11);
  yard(1, 10, 12);

  sail(9, 5, 10, 8);
  yard(9, 11, 9);
}

buildShip(ship);
ship.build();
scene.add(shipGroup);
shipGroup.position.set(4, 0.18, 6);

/* Flags */
const flagGroups = [];

function addFlag(x, y, z, color) {
  const g = new THREE.Group();
  const geo = new THREE.BoxGeometry(2.2, 1.0, 0.08);
  geo.translate(1.1, 0, 0);

  const mesh = new THREE.Mesh(
    geo,
    new THREE.MeshBasicMaterial({ color, side: THREE.DoubleSide })
  );
  mesh.castShadow = false;
  g.add(mesh);

  g.position.set(x, y, z);
  shipGroup.add(g);

  flagGroups.push({ g, phase: rnd() * Math.PI * 2 });
}

addFlag(0, 16, 0, 0xd94f3f);
addFlag(-8, 13, 0, 0xf5f3e8);
addFlag(8, 11, 0, 0x2e6f51);

/* Rigging lines */
const rigPoints = [];
const V = (x, y, z) => new THREE.Vector3(x, y, z);
const line = (a, b) => rigPoints.push(a, b);

line(V(0, 15, 0), V(-13, 3, -5));
line(V(0, 15, 0), V(-13, 3, 5));
line(V(0, 15, 0), V(12, 3, -4));
line(V(0, 15, 0), V(12, 3, 4));

line(V(-8, 13, 0), V(-17, 4, 0));
line(V(-8, 13, 0), V(-17, 4, -3));
line(V(-8, 13, 0), V(-17, 4, 3));
line(V(-8, 13, 0), V(0, 3, -4));
line(V(-8, 13, 0), V(0, 3, 4));

line(V(8, 11, 0), V(12, 3, -3));
line(V(8, 11, 0), V(12, 3, 3));
line(V(8, 11, 0), V(0, 3, -4));
line(V(8, 11, 0), V(0, 3, 4));

line(V(0, 15, 0), V(12, 4, 0));
line(V(1, 15, 5), V(0, 15, 0));
line(V(1, 15, -5), V(0, 15, 0));
line(V(-7, 13, 4), V(-8, 13, 0));
line(V(-7, 13, -4), V(-8, 13, 0));
line(V(9, 11, 4), V(8, 11, 0));
line(V(9, 11, -4), V(8, 11, 0));

const rig = new THREE.LineSegments(
  new THREE.BufferGeometry().setFromPoints(rigPoints),
  new THREE.LineBasicMaterial({ color: 0x2f2f2f, transparent: true, opacity: 0.45 })
);
shipGroup.add(rig);

/* ----------------------------------------------------------
   Clouds
---------------------------------------------------------- */
const cloudGroups = [];

function createCloud(cx, cy, cz, scale = 1) {
  const group = new THREE.Group();
  const b = new VoxelBuilder(group, 150);

  const c1 = 0xf5f9ff;
  const c2 = 0xdfedf5;

  for (let i = 0; i < 20; i++) {
    const x = Math.round((rnd() - 0.5) * 10 * scale);
    const z = Math.round((rnd() - 0.5) * 7 * scale);
    const y = Math.round(rnd() * 2);
    b.add(x, y, z, Math.abs(x + z) % 2 ? c1 : c2);
  }

  for (let i = 0; i < 8; i++) {
    const x = Math.round((rnd() - 0.5) * 5 * scale);
    const z = Math.round((rnd() - 0.5) * 4 * scale);
    const y = 3 + Math.round(rnd());
    b.add(x, y, z, c1);
  }

  const mesh = b.build();
  if (mesh) {
    mesh.castShadow = false;
    mesh.receiveShadow = false;
  }

  group.position.set(cx, cy, cz);
  scene.add(group);

  cloudGroups.push({
    g: group,
    speed: 0.6 + rnd() * 1.8,
    phase: rnd() * 100
  });
}

for (let i = 0; i < 12; i++) {
  createCloud(
    -150 + i * 27 + rnd() * 12,
    34 + rnd() * 18,
    -80 + rnd() * 160,
    0.8 + rnd() * 1.3
  );
}

/* ----------------------------------------------------------
   Animation
---------------------------------------------------------- */
const clock = new THREE.Clock();
let prevT = 0;

function animate() {
  const t = clock.getElapsedTime();
  const dt = Math.min(0.1, t - prevT);
  prevT = t;

  controls.update(dt);

  /* Ship motion */
  shipGroup.position.y = 0.18 + Math.sin(t * 0.65) * 0.14;
  shipGroup.rotation.z = Math.sin(t * 0.45) * 0.02;
  shipGroup.rotation.x = Math.sin(t * 0.38 + 1.3) * 0.012;
  shipGroup.rotation.y = Math.sin(t * 0.31) * 0.006;

  /* Flags */
  for (const f of flagGroups) {
    f.g.rotation.x = Math.sin(t * 5.0 + f.phase) * 0.25;
    f.g.rotation.z = Math.sin(t * 3.3 + f.phase) * 0.08;
  }

  /* Buoys */
  for (const b of buoys) {
    b.g.position.y = 0.45 + Math.sin(t * 1.15 + b.phase) * 0.16;
    b.lampMat.color.copy(
      Math.sin(t * b.freq + b.phase) > 0.35 ? b.onColor : b.offColor
    );
  }

  /* Beacon blink */
  beaconLampMat.color.copy(
    Math.sin(t * 2.0) > 0 ? new THREE.Color(0xffd367) : new THREE.Color(0x222222)
  );

  /* Clouds */
  for (const c of cloudGroups) {
    c.g.position.x += dt * c.speed * 0.22;
    if (c.g.position.x > 180) c.g.position.x = -180;
  }

  /* Lighthouse beam */
  beamGroup.rotation.y = t * 0.35;

  renderer.render(scene, camera);
}

renderer.setAnimationLoop(animate);

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
</script>
</body>
</html>
```