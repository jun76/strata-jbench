Save this as something like `harbor.html` and open it in Chrome. It loads Three.js from a CDN, so the first open needs an internet connection.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>A sailing ship calling at a harbor</title>
<style>
  html, body { margin:0; height:100%; overflow:hidden; background:#08141f; }
  canvas { display:block; }
  #info {
    position:absolute; left:14px; top:12px; color:#f4fbff;
    font:14px/1.35 system-ui, Segoe UI, Roboto, Arial, sans-serif;
    text-shadow:0 1px 6px rgba(0,0,0,.7); pointer-events:none;
  }
  #info b { font-size:16px; }
  #fallback {
    display:none; position:absolute; inset:auto 16px 16px 16px; padding:12px;
    color:#fff; background:rgba(120,30,30,.85); font:14px system-ui; border-radius:8px;
  }
</style>
</head>
<body>
<div id="info">
  <b>A sailing ship calling at a harbor</b><br>
  Drag: orbit • Scroll: zoom • Right-drag: pan
</div>
<div id="fallback">Three.js could not load. Check the internet connection / CDN access.</div>

<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
  }
}
</script>

<script>
window.addEventListener("load", () => {
  setTimeout(() => {
    if (!window.__sceneLoaded) {
      document.getElementById("fallback").style.display = "block";
    }
  }, 4500);
});
</script>

<script type="module">
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

/* ---------- Deterministic randomness ---------- */
function mulberry32(a) {
  return function() {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
const rand = mulberry32(2012718169);

/* ---------- Renderer / Scene / Camera / Controls ---------- */
const scene = new THREE.Scene();

function makeSky() {
  const canvas = document.createElement("canvas");
  canvas.width = 16;
  canvas.height = 256;
  const ctx = canvas.getContext("2d");
  const g = ctx.createLinearGradient(0, 0, 0, 256);
  g.addColorStop(0.00, "#0f4f7f");
  g.addColorStop(0.35, "#4aa6cd");
  g.addColorStop(0.70, "#b9dcea");
  g.addColorStop(1.00, "#f1e7d3");
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

scene.background = makeSky();
scene.fog = new THREE.Fog(0xb7dcea, 80, 230);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
document.body.appendChild(renderer.domElement);

const camera = new THREE.PerspectiveCamera(48, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(43, 29, 47);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(-2, 4, -1);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.minDistance = 18;
controls.maxDistance = 185;
controls.maxPolarAngle = Math.PI * 0.495;
controls.autoRotate = true;
controls.autoRotateSpeed = 0.45;
controls.update();

/* ---------- Lights ---------- */
const hemi = new THREE.HemisphereLight(0xbfe6ff, 0x7c6a52, 0.7);
scene.add(hemi);

const sunLight = new THREE.DirectionalLight(0xfff2d8, 1.35);
sunLight.position.set(55, 78, 30);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
const sd = 85;
sunLight.shadow.camera.left = -sd;
sunLight.shadow.camera.right = sd;
sunLight.shadow.camera.top = sd;
sunLight.shadow.camera.bottom = -sd;
sunLight.shadow.camera.near = 1;
sunLight.shadow.camera.far = 260;
sunLight.shadow.bias = -0.0007;
sunLight.shadow.normalBias = 0.45;
sunLight.target.position.set(-8, 0, 0);
scene.add(sunLight, sunLight.target);

/* ---------- Palette ---------- */
const C = {
  quay: 0xa99f91,
  quayDark: 0x8c8376,
  grass: 0x6aa84f,
  grassDark: 0x578a46,
  dirt: 0x8c6c46,
  sand: 0xdcc496,
  stone: 0x9f9a8e,
  darkStone: 0x69655f,
  lightStone: 0xcac3b8,

  wood: 0x9b6a3d,
  deck: 0xb98c55,
  darkWood: 0x56371f,
  crate: 0x9f7342,
  barrel: 0x7d4f2f,

  shipHull: 0x7b4d2a,
  shipDark: 0x3b2516,
  shipWaterline: 0x2a1b11,
  shipDeck: 0xa7773f,
  shipCabin: 0xa0673a,
  white: 0xece3cf,
  sail: 0xf2e8d3,

  red: 0xc74539,
  blue: 0x31699a,
  yellow: 0xe8c95f,
  wallWhite: 0xe8e0d0,
  wallYellow: 0xe3c77a,
  woodWall: 0xa9784b,
  roofRed: 0x8e352c,
  roofGray: 0x5d646c,
  roofDark: 0x4b3322,

  glass: 0xb8d8e8,
  lantern: 0xffe28a,
  light: 0xffd88c,
  lighthouse: 0xfff1a8
};

/* ---------- Voxel builder ---------- */
class VoxelBuilder {
  constructor(scene, material, capacity, castShadow = true, receiveShadow = true) {
    this.scene = scene;
    this.capacity = capacity;
    this.count = 0;

    this.geometry = new THREE.BoxGeometry(1, 1, 1);
    this.material = material;
    this.mesh = new THREE.InstancedMesh(this.geometry, material, capacity);
    this.mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
    this.mesh.castShadow = castShadow;
    this.mesh.receiveShadow = receiveShadow;

    this.dummy = new THREE.Object3D();
    this.color = new THREE.Color();
  }

  add(x, y, z, color, sx = 1, sy = 1, sz = 1, rx = 0, ry = 0, rz = 0) {
    if (this.count >= this.capacity) return;

    const d = this.dummy;
    d.position.set(x, y, z);
    d.rotation.set(rx, ry, rz);
    d.scale.set(Math.max(0.0001, sx), Math.max(0.0001, sy), Math.max(0.0001, sz));
    d.updateMatrix();

    this.mesh.setMatrixAt(this.count, d.matrix);
    this.color.set(color);
    this.mesh.setColorAt(this.count, this.color);
    this.count++;
  }

  box(x0, y0, z0, x1, y1, z1, color, rx = 0, ry = 0, rz = 0) {
    if (x1 < x0) [x0, x1] = [x1, x0];
    if (y1 < y0) [y0, y1] = [y1, y0];
    if (z1 < z0) [z0, z1] = [z1, z0];

    const sx = Math.max(0.0001, x1 - x0 + 1);
    const sy = Math.max(0.0001, y1 - y0 + 1);
    const sz = Math.max(0.0001, z1 - z0 + 1);

    this.add((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2, color, sx, sy, sz, rx, ry, rz);
  }

  finish() {
    this.mesh.count = this.count;
    this.mesh.instanceMatrix.needsUpdate = true;
    if (this.mesh.instanceColor) this.mesh.instanceColor.needsUpdate = true;
    this.mesh.computeBoundingSphere();
    this.scene.add(this.mesh);
  }
}

const mainMat = new THREE.MeshStandardMaterial({
  color: 0xffffff,
  roughness: 0.88,
  metalness: 0.02,
  flatShading: true
});

const glowMat = new THREE.MeshBasicMaterial({
  color: 0xffffff,
  transparent: true,
  opacity: 0.72,
  depthWrite: false,
  toneMapped: false
});

const cloudMat = new THREE.MeshBasicMaterial({
  color: 0xffffff,
  transparent: true,
  opacity: 0.92,
  depthWrite: true
});

const main = new VoxelBuilder(scene, mainMat, 130000, true, true);
const glow = new VoxelBuilder(scene, glowMat, 6000, false, false);
const clouds = new VoxelBuilder(scene, cloudMat, 5000, false, false);

glow.mesh.renderOrder = 30;
clouds.mesh.renderOrder = 20;

/* ---------- Terrain helpers ---------- */
function isMainLand(x, z) {
  return x <= -22 && x >= -50 && z >= -46 && z <= 46;
}

function terrainHeight(x, z) {
  if (!isMainLand(x, z)) return -1;
  if (x >= -42) return 1;

  let h = 1 + Math.round(
    2.2 +
    1.6 * Math.sin(x * 0.11 + z * 0.07) +
    1.1 * Math.sin(x * 0.07 - z * 0.17) +
    0.8 * Math.sin((x + z) * 0.04)
  );

  if (x > -46) h = Math.max(1, Math.round(h * 0.55));
  return Math.max(1, Math.min(7, h));
}

/* ---------- Generic scene pieces ---------- */
function addTree(x, z) {
  const h = terrainHeight(x, z);
  if (h < 0) return;

  const trunkH = 2 + Math.floor(rand() * 3);
  for (let y = 1; y <= trunkH; y++) {
    main.add(x, h + y, z, C.darkWood, 0.65, 1, 0.65);
  }

  const leafY = h + trunkH + 1;
  const leafW = 2 + Math.floor(rand() * 2);

  main.box(x - leafW, leafY, z - leafW, x + leafW, leafY + 1, z + leafW, C.grass);
  main.box(x - leafW + 1, leafY + 2, z - leafW + 1, x + leafW - 1, leafY + 2, z + leafW - 1, C.grassDark);
}

function buildLand() {
  for (let x = -50; x <= -22; x++) {
    for (let z = -46; z <= 46; z++) {
      const h = terrainHeight(x, z);
      if (h < 0) continue;

      for (let y = -1; y <= h; y++) {
        let col;

        if (y === h) {
          if (x >= -42) col = C.quay;
          else if (z < -30 || z > 30) col = C.grassDark;
          else col = C.grass;
        } else if (y <= 0) {
          if (x >= -42 && y === 0) col = C.quay;
          else if (x > -45 && y === 0) col = C.sand;
          else if (h > 2 && y === 0) col = C.sand;
          else if (y === -1) col = C.darkStone;
          else col = C.dirt;
        } else {
          col = (x >= -42 ? C.quay : C.dirt);
        }

        main.add(x, y, z, col);
      }
    }
  }

  // Quay wall and road
  main.box(-22, 0, -46, -22, 1, 46, C.stone);
  main.box(-24, 1, -45, -23, 1, 45, C.quayDark);
}

function addBuilding(cx, cz, w, d, h, wall, roof, windows = true) {
  const x0 = cx - Math.floor(w / 2);
  const x1 = cx + Math.floor(w / 2);
  const z0 = cz - Math.floor(d / 2);
  const z1 = cz + Math.floor(d / 2);

  main.box(x0, 2, z0, x1, 2 + h - 1, z1, wall);

  const layers = Math.floor(Math.min(w, d) / 2);
  for (let l = 0; l <= layers; l++) {
    main.box(x0 + l, 2 + h + l, z0 + l, x1 - l, 2 + h + l, z1 - l, roof);
  }

  // Door facing harbor
  main.add(x1 + 0.55, 2.45, cz, C.darkWood, 0.14, 1.5, 1.05);

  if (windows) {
    for (let yy = 3; yy <= 2 + h - 1; yy += 2) {
      for (let zz = z0 + 1; zz <= z1 - 1; zz += 2) {
        if (rand() < 0.58) glow.add(x1 + 0.55, yy, zz, C.light, 0.14, 0.62, 0.62);
        if (rand() < 0.18) glow.add(x0 - 0.55, yy, zz, C.light, 0.14, 0.62, 0.62);
      }
    }
  }

  // Chimney
  if (rand() < 0.65) {
    const chimneyX = x0 + 1 + Math.floor(rand() * Math.max(1, x1 - x0 - 2));
    main.box(chimneyX, 2 + h + layers + 1, cz, chimneyX, 2 + h + layers + 2, cz, C.darkStone);
  }
}

function addDockside() {
  addBuilding(-28, -20, 7, 5, 3, C.wallWhite, C.roofRed);
  addBuilding(-34, -11, 11, 7, 4, C.stone, C.roofGray);
  addBuilding(-34, -1, 13, 7, 4, C.woodWall, C.roofDark);
  addBuilding(-34, 10, 9, 7, 4, C.stone, C.roofRed);
  addBuilding(-28, 16, 5, 5, 3, C.wallYellow, C.roofGray);

  addBuilding(-26, 4, 3, 3, 2, C.stone, C.roofRed);
  addBuilding(-26, -8, 3, 3, 2, C.woodWall, C.roofDark);
}

function addLamp(x, z) {
  main.box(x, 2, z, x, 5, z, C.darkWood);
  glow.add(x, 6, z, C.lantern, 0.95, 0.95, 0.95);
}

function addStall(x, z, roofColor) {
  const posts = [[-1, -1], [1, -1], [-1, 1], [1, 1]];
  for (const [px, pz] of posts) {
    main.add(x + px, 2.75, z + pz, C.darkWood, 0.25, 2.5, 0.25);
  }
  main.add(x, 4.15, z, roofColor, 3.4, 0.3, 3.4);

  main.add(x - 0.55, 2.75, z - 0.55, C.crate, 0.8, 0.8, 0.8, 0, rand() * 1.2, 0);
  main.add(x + 0.65, 2.7, z + 0.45, C.barrel, 0.75, 0.75, 0.75, 0, rand() * 1.2, 0);
}

function addPier() {
  // Deck
  main.box(-21, 1, -22, -17, 1, 16, C.deck);

  // Pilings
  for (let z = -20; z <= 14; z += 4) {
    main.box(-19, -3, z, -19, 0, z, C.darkWood);
    main.box(-17, -3, z, -17, 0, z, C.darkWood);
  }

  // Bollards
  for (let z = -12; z <= 12; z += 12) {
    main.add(-18, 2, z, C.darkStone, 0.8, 1, 0.8);
  }

  // Lamps
  addLamp(-18, -18);
  addLamp(-18, -6);
  addLamp(-18, 6);

  // Gangplank
  main.box(-17, 1, -4, -16, 1, 2, C.deck);
  main.add(-17.45, 2.1, -1, C.darkWood, 0.2, 1.0, 6.2);
  main.add(-15.55, 2.1, -1, C.darkWood, 0.2, 1.0, 6.2);

  // Cargo / clutter
  const skip = new Set([-18, -12, -6, 0, 6, 12]);
  for (let z = -20; z <= 16; z += 3) {
    if (skip.has(z)) continue;

    if (rand() < 0.52) {
      const side = -19 + (rand() < 0.4 ? 1 : 0);
      main.add(side, 2, z, C.crate, 1, 1, 1, 0, rand() * 1.6, 0);
    }

    if (rand() < 0.38) {
      main.add(-20, 2.2, z, C.barrel, 0.95, 0.95, 0.95, 0, rand() * 1.6, 0);
    }

    if (rand() < 0.22) {
      main.add(-19, 3, z, C.crate, 1, 1, 1, 0, rand() * 1.6, 0);
    }
  }

  addStall(-24, -2, C.red);
  addStall(-24, 12, C.blue);
}

/* ---------- Ship ---------- */
function addMast(cx, cz, rz, height) {
  const z = cz + rz;
  const baseY = 2;
  const topY = baseY + height;
  main.add(cx, (baseY + topY) / 2, z, C.darkWood, 0.35, height, 0.35);
}

function addSail(cx, cz, bottomY, topY, width, color = C.sail) {
  const h = topY - bottomY;
  const y = (bottomY + topY) / 2;
  main.add(cx, y, cz, color, width, h, 0.25);

  // Yards
  main.add(cx, topY, cz, C.darkWood, width + 1.0, 0.25, 0.25);
  if (bottomY > 6) main.add(cx, bottomY, cz, C.darkWood, width * 0.82, 0.25, 0.25);
}

function addShip() {
  const sx = -12;
  const sz = -1;
  const len = 9;

  // Hull
  for (let rz = -len; rz <= len; rz++) {
    const z = sz + rz;
    const t = rz / len;
    let hw = Math.round(3.15 * Math.sqrt(Math.max(0, 1 - t * t)));
    if (Math.abs(t) > 0.92) hw = Math.max(0, hw - 1);

    const hwBottom = Math.max(0, hw - 1);

    for (let dx = -hw; dx <= hw; dx++) {
      const x = sx + dx;

      // Lower hull
      for (let y = -1; y <= 0; y++) {
        const col = (y === -1 ? C.shipWaterline : C.shipHull);
        main.add(x, y, z, col);
      }

      if (Math.abs(dx) <= hwBottom) {
        main.add(x, -2, z, C.shipDark);
      }

      if (hw > 0) {
        main.add(x, 1, z, C.shipDeck);
        if (Math.abs(dx) === hw) main.add(x, 2, z, C.white);
      } else {
        main.add(x, 1, z, C.shipDeck);
      }
    }
  }

  // Sterncastle
  for (let rz = -8; rz <= -5; rz++) {
    for (let dx = -2; dx <= 2; dx++) {
      main.add(sx + dx, 2, sz + rz, C.shipCabin);
      main.add(sx + dx, 3, sz + rz, C.shipCabin);
    }
  }

  // Forecastle
  for (let rz = 5; rz <= 7; rz++) {
    for (let dx = -1; dx <= 1; dx++) {
      main.add(sx + dx, 2, sz + rz, C.shipCabin);
    }
  }

  // Stern windows
  for (let dx = -1; dx <= 1; dx++) {
    glow.add(sx + dx, 2.5, sz - 8.55, C.light, 0.16, 0.7, 0.7);
  }

  // Bowsprit
  main.add(sx, 4.2, sz + 10, C.darkWood, 0.35, 0.35, 6, -0.28, 0, 0);
  main.add(sx, 4.8, sz + 13, C.darkWood, 0.25, 0.25, 2, -0.18, 0, 0);

  // Masts
  addMast(sx, sz, 0, 16);   // main
  addMast(sx, sz, 4, 14);   // fore
  addMast(sx, sz, -6, 12);  // mizzen

  // Sails
  addSail(sx, sz, 8, 15, 7.0, C.sail);
  addSail(sx, sz, 15.5, 17.2, 4.2, C.sail);

  addSail(sx, sz + 4, 7, 12, 6.0, C.sail);
  addSail(sx, sz + 4, 12.3, 13.8, 3.5, C.sail);

  addSail(sx, sz - 6, 6, 10, 5.0, C.sail);

  // Flag
  main.add(sx + 1.8, 18, sz, C.red, 3.3, 0.9, 0.08, 0, 0, 0.16);

  // Deck cargo
  main.add(sx - 1, 2, sz + 2, C.crate, 1, 1, 1, 0, 0.35, 0);
  main.add(sx + 1, 2, sz + 2, C.crate, 1, 1, 1, 0, 0.8, 0);
  main.add(sx, 2.2, sz + 3, C.crate, 1.2, 1.2, 1.2, 0, 0.2, 0);
  main.add(sx - 1, 2.2, sz - 2, C.barrel, 0.9, 0.9, 0.9, 0, 0.4, 0);
  main.add(sx + 1, 2.2, sz - 2, C.barrel, 0.9, 0.9, 0.9, 0, 1.1, 0);
}

/* ---------- Breakwater and lighthouse ---------- */
function addLighthouse(cx, cz) {
  main.box(cx - 3, 3, cz - 3, cx + 3, 4, cz + 3, C.darkStone);

  for (let y = 5; y <= 16; y++) {
    const r = (y < 14 ? 2 : 1);
    const stripe = Math.floor((y - 5) / 2) % 2 === 0 ? C.white : C.red;
    main.box(cx - r, y, cz - r, cx + r, y, cz + r, stripe);
  }

  main.box(cx - 2, 17, cz - 2, cx + 2, 17, cz + 2, C.darkStone);
  main.box(cx - 1, 18, cz - 1, cx + 1, 18, cz + 1, C.glass);
  glow.add(cx, 18, cz, C.lighthouse, 5.0, 3.8, 5.0);
  main.box(cx - 1, 19, cz - 1, cx + 1, 19, cz + 1, C.darkStone);
  main.add(cx, 20.5, cz, C.red, 0.45, 1.5, 0.45);
}

function addBreakwaterAndLighthouse() {
  for (let i = 0; i < 64; i++) {
    const t = i / 63;
    const x = Math.round(10 + 17 * t + Math.sin(t * 2.2) * 2);
    const z = Math.round(-22 + 24 * t + Math.sin(t * 1.5) * 2);
    const w = i > 54 ? 3 : 2;

    for (let dx = -w; dx <= w; dx++) {
      for (let dz = -w; dz <= w; dz++) {
        if (Math.abs(dx) + Math.abs(dz) > w + 1) continue;

        let h = 1 + (rand() < 0.22 ? 1 : 0) + (i > 54 ? 1 : 0);
        for (let y = -1; y <= h; y++) {
          let col;
          if (y === h) col = rand() < 0.25 ? C.lightStone : C.stone;
          else if (y <= 0) col = C.darkStone;
          else col = C.stone;

          main.add(x + dx, y, z + dz, col);
        }
      }
    }

    if (i === 63) addLighthouse(x, z);
  }
}

/* ---------- Harbor details ---------- */
function addBuoys() {
  const buoys = [
    [6, -16, C.red],
    [-4, -20, C.green],
    [16, -8, C.red],
    [12, 14, C.green],
    [2, 20, C.red]
  ];

  for (const [x, z, col] of buoys) {
    main.box(x, 1, z, x, 2, z, col);
    main.box(x, 3, z, x, 3, z, C.darkWood);
    glow.add(x, 3.8, z, col, 0.75, 0.75, 0.75);
  }
}

function addBoat(cx, cz, ry) {
  main.add(cx, 0.55, cz, C.wood, 1.15, 0.75, 3.2, 0, ry, 0);
  main.add(cx, 1.0, cz, C.darkWood, 1.3, 0.22, 3.5, 0, ry, 0);
}

function addBoats() {
  addBoat(-16.5, 12, Math.PI * 0.25);
  addBoat(-9, 15, -0.3);
}

function addClouds() {
  for (let i = 0; i < 14; i++) {
    const x = -45 + rand() * 100;
    const y = 26 + rand() * 8;
    const z = -45 + rand() * 100;

    const sx = 7 + rand() * 12;
    const sz = 7 + rand() * 9;

    clouds.add(x, y, z, 0xffffff, sx, 1, sz);
    clouds.add(x + rand() * 6 - 3, y + 1, z + rand() * 6 - 3, 0xffffff, sx * 0.72, 1, sz * 0.72);
    clouds.add(x + rand() * 4 - 2, y - 1, z + rand() * 4 - 2, 0xffffff, sx * 0.55, 1, sz * 0.55);
  }
}

function addTrees() {
  for (let x = -50; x <= -43; x += 2) {
    for (let z = -44; z <= 44; z += 2) {
      if (rand() < 0.24) addTree(x, z);
    }
  }
}

/* ---------- Water ---------- */
const waterMat = new THREE.MeshStandardMaterial({
  color: 0xffffff,
  transparent: true,
  opacity: 0.82,
  roughness: 0.32,
  metalness: 0.06,
  depthWrite: true
});

function buildWater() {
  const range = 54;
  const max = (range * 2 + 1) ** 2;

  const geo = new THREE.BoxGeometry(1, 1, 1);
  const mesh = new THREE.InstancedMesh(geo, waterMat, max);
  mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
  mesh.castShadow = false;
  mesh.receiveShadow = false;

  const dummy = new THREE.Object3D();
  const color = new THREE.Color();

  const waterX = [];
  const waterZ = [];

  let idx = 0;

  for (let x = -range; x <= range; x++) {
    for (let z = -range; z <= range; z++) {
      if (isMainLand(x, z)) continue;

      waterX.push(x);
      waterZ.push(z);

      dummy.position.set(x, -0.5, z);
      dummy.rotation.set(0, 0, 0);
      dummy.scale.set(1, 1, 1);
      dummy.updateMatrix();
      mesh.setMatrixAt(idx, dummy.matrix);

      const dist = Math.sqrt(x * x + z * z);
      const l = Math.max(0.24, Math.min(0.56, 0.40 + 0.07 * Math.sin(x * 0.12) + 0.07 * Math.cos(z * 0.14) - dist * 0.0008));
      color.setHSL(0.55, 0.58, l);
      mesh.setColorAt(idx, color);

      idx++;
    }
  }

  mesh.count = idx;
  if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
  mesh.computeBoundingSphere();
  scene.add(mesh);

  return { mesh, waterX, waterZ };
}

/* ---------- Birds ---------- */
function createBirds() {
  const count = 8;
  const geo = new THREE.BoxGeometry(1, 0.25, 1);
  const mat = new THREE.MeshBasicMaterial({ color: 0x27323a, fog: false });
  const mesh = new THREE.InstancedMesh(geo, mat, count);
  mesh.frustumCulled = false;
  scene.add(mesh);

  const dummy = new THREE.Object3D();
  const birds = [];

  for (let i = 0; i < count; i++) {
    birds.push({
      r: 28 + rand() * 18,
      s: 0.12 + rand() * 0.18,
      y: 22 + rand() * 8,
      a: rand() * Math.PI * 2
    });
  }

  function update(t) {
    for (let i = 0; i < count; i++) {
      const b = birds[i];
      const a = b.a + t * b.s;

      const x = Math.cos(a) * b.r;
      const z = Math.sin(a) * b.r;
      const flap = 0.5 + 0.55 * Math.sin(t * 7 + b.a);

      dummy.position.set(x, b.y + Math.sin(t * 5 + b.a) * 0.9, z);
      dummy.rotation.set(0, -a + Math.PI / 2, Math.sin(t * 6 + b.a) * 0.35);
      dummy.scale.set(1.15, 0.35 + flap * 0.8, 1.15);
      dummy.updateMatrix();

      mesh.setMatrixAt(i, dummy.matrix);
    }
    mesh.instanceMatrix.needsUpdate = true;
  }

  return { mesh, update };
}

/* ---------- Build scene ---------- */
buildLand();
addDockside();
addPier();
addShip();
addBreakwaterAndLighthouse();
addBuoys();
addBoats();
addTrees();
addClouds();

main.finish();
glow.finish();
clouds.finish();

const water = buildWater();
const birds = createBirds();

const dummy = new THREE.Object3D();
const clock = new THREE.Clock();

/* ---------- Sun visual ---------- */
const sun = new THREE.Mesh(
  new THREE.IcosahedronGeometry(3.5, 0),
  new THREE.MeshBasicMaterial({ color: 0xfff1c4, fog: false })
);
sun.position.set(72, 74, -32);
scene.add(sun);

/* ---------- Animation loop ---------- */
function animate() {
  requestAnimationFrame(animate);

  const t = clock.getElapsedTime();

  controls.update();

  // Animate water
  const { mesh, waterX, waterZ } = water;
  for (let i = 0; i < waterX.length; i++) {
    const x = waterX[i];
    const z = waterZ[i];

    const y =
      -0.5 +
      0.12 * Math.sin(x * 0.15 + t * 1.15) +
      0.08 * Math.cos(z * 0.17 - t * 0.95) +
      0.05 * Math.sin((x + z) * 0.09 + t * 0.75);

    dummy.position.set(x, y, z);
    dummy.rotation.set(0, 0, 0);
    dummy.scale.set(1, 1, 1);
    dummy.updateMatrix();
    mesh.setMatrixAt(i, dummy.matrix);
  }
  mesh.instanceMatrix.needsUpdate = true;

  // Gentle cloud drift
  clouds.mesh.position.x = Math.sin(t * 0.03) * 8;
  clouds.mesh.position.z = Math.cos(t * 0.025) * 5;

  birds.update(t);

  renderer.render(scene, camera);
}

function onResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}
window.addEventListener("resize", onResize);

window.__sceneLoaded = true;
animate();
</script>
</body>
</html>
```