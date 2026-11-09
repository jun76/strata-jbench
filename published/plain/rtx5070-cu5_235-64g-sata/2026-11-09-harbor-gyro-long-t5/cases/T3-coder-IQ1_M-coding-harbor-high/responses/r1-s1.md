Save this as an `.html` file and open it in Chrome. Drag to orbit, wheel to zoom.

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Voxel Harbor — A Sailing Ship Calling at Harbor</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  html,body{margin:0;height:100vh;overflow:hidden;background:#111;touch-action:none;}
  canvas{display:block;width:100%;height:100%;}
  #hint{
    position:fixed;left:16px;bottom:16px;pointer-events:none;
    font-family:system-ui,sans-serif;font-size:13px;color:#f5f2e6;
    text-shadow:0 1px 2px rgba(0,0,0,.6);opacity:.9;
  }
</style>
</head>
<body>
<canvas id="c"></canvas>
<div id="hint">Drag to orbit · wheel to zoom</div>

<script type="module">
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';

const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.setSize(window.innerWidth, window.innerHeight, false);
renderer.outputColorSpace = THREE.SRGBColorSpace;

const fogColor = new THREE.Color('#98d6e8');
const scene = new THREE.Scene();
scene.background = fogColor.clone();
scene.fog = new THREE.Fog(fogColor, 75, 210);

// ---------- Voxel store ----------
const voxels = new Map();

function addVoxel(x, y, z, color) {
  voxels.set(`${x},${y},${z}`, color);
}

function addBox(x0, x1, y0, y1, z0, z1, color) {
  for (let x = x0; x <= x1; x++) {
    for (let y = y0; y <= y1; y++) {
      for (let z = z0; z <= z1; z++) {
        addVoxel(x, y, z, color);
      }
    }
  }
}

function createInstancedMesh(map) {
  const entries = [...map.entries()];
  const geo = new THREE.BoxGeometry(1, 1, 1);
  const mat = new THREE.MeshLambertMaterial({
    vertexColors: true,
    flatShading: true
  });

  const mesh = new THREE.InstancedMesh(geo, mat, entries.length);
  const dummy = new THREE.Object3D();
  const col = new THREE.Color();

  entries.forEach((e, i) => {
    const p = e[0].split(',').map(Number);
    const c = e[1];

    dummy.position.set(p[0], p[1], p[2]);
    dummy.scale.set(1, 1, 1);
    dummy.rotation.set(0, 0, 0);
    dummy.updateMatrix();

    mesh.setMatrixAt(i, dummy.matrix);

    col.setHex(c);
    mesh.setColorAt(i, col);
  });

  mesh.instanceMatrix.needsUpdate = true;
  if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
  mesh.frustumCulled = false;
  return mesh;
}

// ---------- Palette ----------
const waterColors = [0x2f6d87, 0x24749b, 0x216077, 0x3480a2];
const stoneColors = [0x918f86, 0x7f7e74, 0x6e6f67];
const grassColors = [0x5e8c51, 0x6f9b58, 0x557b4b];

const hullBottom = 0x23374b;
const hullUpper  = 0x703f2d;
const deckWood   = 0xb68b64;
const deckEdge   = 0x8e6e50;
const shipHouse  = 0x87694d;
const shipRoof   = 0x352724;
const mastWood   = 0x5d3e2b;
const yardWood   = 0x6d4c2d;
const sailWhite  = 0xf4f1e7;
const flagRed    = 0xc63b36;
const woodDark   = 0x8c6b4c;

// ---------- Harbor water ----------
for (let x = -13; x <= 13; x++) {
  for (let z = -11; z <= 11; z++) {
    const c = waterColors[(Math.abs(x) + Math.abs(z)) % waterColors.length];
    addVoxel(x, 0, z, c);
  }
}

// ---------- Quay ring around basin ----------
for (let x = -14; x <= 14; x++) {
  for (let z = -12; z <= 12; z++) {
    const insideWater = x >= -13 && x <= 13 && z >= -11 && z <= 11;
    if (!insideWater) {
      const c = stoneColors[((x + z + 60) % 3)];
      addVoxel(x, 1, z, c);
    }
  }
}

// ---------- Land around harbor ----------
for (let x = -17; x <= 17; x++) {
  for (let z = 13; z <= 16; z++) {
    addVoxel(x, 2, z, grassColors[((x + z + 200) % 3)]);
  }
  for (let z = -16; z <= -13; z++) {
    addVoxel(x, 2, z, grassColors[((x + z + 200) % 3)]);
  }
}

for (let z = -12; z <= 12; z++) {
  for (let x = -17; x <= -15; x++) {
    addVoxel(x, 2, z, grassColors[((x + z + 200) % 3)]);
  }
  for (let x = 15; x <= 17; x++) {
    addVoxel(x, 2, z, grassColors[((x + z + 200) % 3)]);
  }
}

// ---------- Warehouses on north side ----------
function warehouse(x0, x1, z0, z1, wall, roof, window, door) {
  addBox(x0, x1, 3, 5, z0, z1, wall);

  addBox(x0 - 1, x1 + 1, 6, 6, z0, z1, roof);
  if (x0 + 1 <= x1 - 1) {
    addBox(x0 + 1, x1 - 1, 7, 7, z0, z1, roof);
  }

  const mid = Math.floor((x0 + x1) / 2);

  for (let x = x0; x <= x1; x++) {
    if (x !== mid && ((x - x0) % 2 === 0)) {
      addVoxel(x, 4, z0, window);
    }
  }

  addVoxel(mid, 3, z0, door);
  addVoxel(mid, 4, z0, door);
}

warehouse(-11, -7, 14, 16, 0xa95046, 0x52312f, 0xdde9f1, 0x38271f);
warehouse(-4, 0, 14, 16, 0x9c6b51, 0x334c61, 0xdde9f1, 0x38271f);
warehouse(3, 7, 14, 16, 0x647d6d, 0x43382b, 0xdde9f1, 0x38271f);

// ---------- Small trees ----------
function tree(x, z) {
  addVoxel(x, 3, z, 0x6c4b35);
  addVoxel(x, 4, z, 0x5b3f2b);

  for (let dx = -1; dx <= 1; dx++) {
    for (let dz = -1; dz <= 1; dz++) {
      const c = (dx === 0 && dz === 0) ? 0x437449 : 0x4f8a4b;
      addVoxel(x + dx, 5, z + dz, c);
      if (dx === 0 && dz === 0) {
        addVoxel(x + dx, 6, z + dz, c);
      }
    }
  }
}

tree(-15, 14);
tree(-6, 13);
tree(9, 15);
tree(13, 14);

tree(-12, -14);
tree(1, -15);
tree(12, -14);

tree(-16, -2);
tree(-16, 5);

// ---------- Dock bollards ----------
function bollard(x, z) {
  addVoxel(x, 2, z, 0x33363b);
  addVoxel(x, 3, z, 0xc43f3a);
}

const northBollards = [-12, -10, -8, -6, -4, -2, 0, 2, 4, 6, 8, 10, 12];
const southBollards = [-12, -10, -8, -6, -4, -2, 0, 2, 4, 6, 8, 10, 12];
const westBollards = [-10, -8, -6, -4, -2, 2, 4, 6, 8, 10];

for (const x of northBollards) bollard(x, 12);
for (const x of southBollards) bollard(x, -12);
for (const z of westBollards) bollard(-14, z);

// ---------- Shipping containers on east quay ----------
const containerColors = [
  0xd64a39,
  0x2d6d94,
  0x397e5d,
  0xf0bc41,
  0x8c5d91,
  0xc7b698
];

function containerStack(x, z, h, color) {
  addBox(x, x, 2, 1 + h, z, z, color);
}

const eastContainerPositions = [
  [-5, 1], [-4, 2], [-3, 1], [-2, 2], [-1, 1],
  [0, 2], [1, 1], [2, 2], [3, 1], [4, 2]
];

for (const p of eastContainerPositions) {
  const z = p[0];
  const h = p[1];
  const c = containerColors[(Math.abs(z) + 10) % containerColors.length];
  containerStack(14, z, h, c);
}

const innerContainerPositions = [
  [-3, 1], [-1, 2], [1, 2], [3, 1]
];

for (const p of innerContainerPositions) {
  const z = p[0];
  const h = p[1];
  const c = containerColors[(Math.abs(z) + 2) % containerColors.length];
  containerStack(15, z, h, c);
}

// ---------- Dock crane ----------
function crane(baseX, baseZ) {
  addVoxel(baseX, 2, baseZ, 0x4b4f52);

  for (let y = 3; y <= 7; y++) {
    addVoxel(baseX, y, baseZ, 0xd7a52f);
  }

  for (let x = baseX - 5; x < baseX; x++) {
    addVoxel(x, 7, baseZ, 0xc66534);
  }

  addVoxel(baseX - 5, 6, baseZ, 0x5b4332);
  addVoxel(baseX - 5, 5, baseZ, 0xd7a52f);

  addVoxel(baseX + 1, 6, baseZ, 0x4d5055);
  addVoxel(baseX + 1, 7, baseZ, 0xd7a52f);
}

crane(14, 8);

// ---------- Lighthouse on west land ----------
function lighthouse(x, z) {
  addVoxel(x, 2, z, 0x6e6d66);

  for (let y = 3; y <= 7; y++) {
    const c = (y % 2 === 1) ? 0xeee9e1 : 0xa53b3a;
    addVoxel(x, y, z, c);
  }

  addVoxel(x, 8, z, 0xf7c94b);
  addVoxel(x, 9, z, 0xa53b3a);
}

lighthouse(-16, -8);

// ---------- Harbor buoys ----------
function buoy(x, z, topColor) {
  addVoxel(x, 1, z, topColor);
  addVoxel(x, 2, z, 0xf1e3ca);
}

buoy(-6, -10, 0xc43f32);
buoy(6, -10, 0x2a7d3e);

// ---------- Clouds and gulls ----------
function cloud(x, y, z) {
  addBox(x - 2, x + 2, y, y, z - 1, z + 1, 0xf6f4ef);
  addBox(x - 1, x + 1, y + 1, y + 1, z, z, 0xfbf8f2);
}

function gull(x, y, z) {
  addVoxel(x, y, z, 0xf5f1e8);
  addVoxel(x - 1, y, z, 0xe8e5dc);
  addVoxel(x + 1, y, z, 0xe8e5dc);
  addVoxel(x, y + 1, z, 0xfbf7ef);
}

cloud(-12, 18, 17);
cloud(7, 17, -6);
cloud(1, 20, 9);
cloud(13, 18, 14);

gull(-7, 12, -2);
gull(4, 13, 0);
gull(10, 12, 9);

// ---------- Sailing ship ----------
const SHIP_X = -1;
const SHIP_Z = 6;

function shipVoxel(lx, y, lz, color) {
  addVoxel(lx + SHIP_X, y, lz + SHIP_Z, color);
}

function shipBox(lx0, lx1, y0, y1, lz0, lz1, color) {
  for (let x = lx0; x <= lx1; x++) {
    for (let y = y0; y <= y1; y++) {
      for (let z = lz0; z <= lz1; z++) {
        shipVoxel(x, y, z, color);
      }
    }
  }
}

// Hull outline: bow at left, stern at right.
const halfWidths = [0, 1, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 1];

for (let i = 0; i < halfWidths.length; i++) {
  const lx = -7 + i;
  const h = halfWidths[i];

  for (let z = -h; z <= h; z++) {
    shipVoxel(lx, 1, z, hullBottom);
    shipVoxel(lx, 2, z, hullUpper);
    shipVoxel(lx, 3, z, deckWood);
  }

  if (h > 0) {
    shipVoxel(lx, 4, -h, deckEdge);
    shipVoxel(lx, 4, h, deckEdge);
  } else {
    shipVoxel(lx, 4, 0, deckEdge);
  }
}

// Bowsprit
for (let lx = -9; lx <= -7; lx++) {
  shipVoxel(lx, 3, 0, woodDark);
}
shipVoxel(-9, 4, 0, woodDark);

// Forecastle and aft house
shipBox(-6, -5, 4, 5, -2, 2, shipHouse);
shipBox(-6, -5, 6, 6, -1, 1, shipRoof);

shipBox(3, 5, 4, 5, -2, 2, shipHouse);
shipBox(3, 5, 6, 6, -1, 1, shipRoof);

// Three masts, yards, and square sails
const masts = [-4, 0, 4];

for (const mx of masts) {
  for (let y = 4; y <= 9; y++) {
    shipVoxel(mx, y, 0, mastWood);
  }

  for (let y = 10; y <= 11; y++) {
    shipVoxel(mx, y, 0, flagRed);
  }

  for (let dx = -2; dx <= 2; dx++) {
    shipVoxel(mx + dx, 8, 0, yardWood);
  }

  for (let y = 4; y <= 7; y++) {
    for (let dx = -1; dx <= 1; dx++) {
      shipVoxel(mx + dx, y, 0, sailWhite);
    }
  }
}

// Extra sails / rigging silhouette
for (let y = 4; y <= 6; y++) {
  for (let x = -6; x <= -4; x++) {
    shipVoxel(x, y, 0, sailWhite);
  }
}

for (let y = 4; y <= 7; y++) {
  for (let x = 5; x <= 6; x++) {
    shipVoxel(x, y, 0, sailWhite);
  }
}

// Mooring line toward north quay
for (let z = SHIP_Z + 3; z <= 12; z++) {
  addVoxel(SHIP_X, 2, z, 0x55402c);
}

// ---------- Build all voxels ----------
scene.add(createInstancedMesh(voxels));

// ---------- Lighting ----------
const hemi = new THREE.HemisphereLight('#ffffff', '#7c6c5a', 0.72);
scene.add(hemi);

const sun = new THREE.DirectionalLight('#fff0d4', 1.55);
sun.position.set(42, 65, 28);
scene.add(sun);

const fill = new THREE.DirectionalLight('#b9e2f6', 0.55);
fill.position.set(-35, 22, -30);
scene.add(fill);

// ---------- Camera and mouse orbit ----------
const target = new THREE.Vector3(0, 5, 0);

const camera = new THREE.PerspectiveCamera(
  45,
  window.innerWidth / window.innerHeight,
  1,
  400
);

let radius = 88;
let yaw = 0.82;
let pitch = 0.58;

let dragging = false;
let lastX = 0;
let lastY = 0;

window.addEventListener('pointerdown', e => {
  if (e.button === 0) {
    dragging = true;
    lastX = e.clientX;
    lastY = e.clientY;
  }
});

window.addEventListener('pointermove', e => {
  if (!dragging) return;

  const dx = e.clientX - lastX;
  const dy = e.clientY - lastY;

  yaw += dx * 0.0055;
  pitch += dy * 0.0045;

  pitch = Math.max(0.12, Math.min(1.45, pitch));

  lastX = e.clientX;
  lastY = e.clientY;
});

window.addEventListener('pointerup', () => {
  dragging = false;
});

window.addEventListener('wheel', e => {
  radius *= Math.exp(e.deltaY * 0.0012);
  radius = Math.max(28, Math.min(180, radius));
});

window.addEventListener('contextmenu', e => e.preventDefault());

function resizeRendererToDisplaySize() {
  const width = Math.max(1, Math.floor(window.innerWidth));
  const height = Math.max(1, Math.floor(window.innerHeight));

  renderer.setSize(width, height, false);
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
}

window.addEventListener('resize', resizeRendererToDisplaySize);

let lastTime = performance.now();

function animate() {
  const now = performance.now();
  const dt = Math.min(0.05, (now - lastTime) / 1000);
  lastTime = now;

  if (!dragging) {
    yaw += dt * 0.18;
  }

  const cp = Math.cos(pitch);
  const cy = Math.cos(yaw);
  const sy = Math.sin(yaw);
  const sp = Math.sin(pitch);

  camera.position.set(
    target.x + radius * cp * sy,
    target.y + radius * sp,
    target.z + radius * cp * cy
  );

  camera.lookAt(target);
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}

requestAnimationFrame(animate);
</script>
</body>
</html>
```