Save this as a single `.html` file and open it in Chrome. It uses Three.js from a CDN, renders immediately, and lets you orbit/zoom/pan with the mouse.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>Voxel Scene: A Sailing Ship Calling at a Harbor</title>
<style>
  html, body {
    margin: 0;
    height: 100%;
    overflow: hidden;
    background: #a3d1e8;
  }
  canvas {
    display: block;
  }
  #hud {
    position: absolute;
    left: 14px;
    top: 14px;
    padding: 10px 12px;
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.72);
    color: #213;
    font: 14px system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
    box-shadow: 0 2px 10px rgba(0,0,0,.15);
    pointer-events: none;
  }
</style>
</head>
<body>
<div id="hud">
  🖱️ Drag to orbit • Scroll to zoom • Right-drag to pan<br>
  A sailing ship calling at a harbor
</div>

<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
  }
}
</script>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const COL = {
  sky: 0xa3d1e8,
  foam: 0xd7ecf3,
  sand: 0xd9c197,
  grass: 0x61a14f,
  dirt: 0x8d6b45,
  stone: 0x898b8c,
  stoneDark: 0x616161,
  stoneLight: 0xa19f9b,
  wood: 0x8d6136,
  woodDark: 0x452814,
  plank: 0xb8854f,
  plankDark: 0x8f6534,
  hull: 0x7d4827,
  hullDark: 0x482412,
  deck: 0xb1814d,
  mast: 0x452814,
  sail: 0xf5efe1,
  sail2: 0xe8dfd2,
  flag: 0xd4493b,
  gold: 0xf0c645,
  lamp: 0xffd386
};

const waterColors = [0x1f4f87, 0x2461a4, 0x2e74bd, 0x1b5590];
const shallowWaterColors = [0x4c9ed2, 0x66b4dd];
const houseColors = [0xf2dcb2, 0xe7c9a7, 0xd9a77f, 0x9b6f59, 0x7f95a7, 0xc9c7c7];
const roofColors = [0x913838, 0x3e4854, 0x446b4c, 0x7a4e30];
const leafColors = [0x549b4c, 0x3f7d43, 0x64a857];

function pick(a) {
  return a[(Math.random() * a.length) | 0];
}

const boxGeo = new THREE.BoxGeometry(1, 1, 1);

class VoxelBuilder {
  constructor() {
    this.blocks = [];
  }

  add(x, y, z, color) {
    this.blocks.push({ x, y, z, color });
  }

  addBox(x0, x1, y0, y1, z0, z1, color) {
    const sx = Math.min(x0, x1);
    const ex = Math.max(x0, x1);
    const sy = Math.min(y0, y1);
    const ey = Math.max(y0, y1);
    const sz = Math.min(z0, z1);
    const ez = Math.max(z0, z1);

    for (let x = sx; x <= ex; x++) {
      for (let y = sy; y <= ey; y++) {
        for (let z = sz; z <= ez; z++) {
          this.add(x, y, z, color);
        }
      }
    }
  }

  build(material) {
    const n = this.blocks.length;
    if (n === 0) return new THREE.Group();

    const mesh = new THREE.InstancedMesh(boxGeo, material, n);
    const mat = new THREE.Matrix4();
    const col = new THREE.Color();

    for (let i = 0; i < n; i++) {
      const b = this.blocks[i];
      mat.makeTranslation(b.x, b.y, b.z);
      mesh.setMatrixAt(i, mat);
      col.setHex(b.color);
      mesh.setColorAt(i, col);
    }

    mesh.instanceMatrix.needsUpdate = true;
    if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
    return mesh;
  }
}

const worldBuilder = new VoxelBuilder();
const shipBuilder = new VoxelBuilder();
const emissiveBuilder = new VoxelBuilder();
const cloudBuilder = new VoxelBuilder();

function isLand(x, z) {
  return x >= -28 && x <= 28 && z >= -34 && z <= -10;
}

function isBreakwater(x, z) {
  return (x >= -18 && x <= -14 && z >= -9 && z <= 10) ||
         (x >= 14 && x <= 18 && z >= -9 && z <= 10);
}

function isPier(x, z) {
  return x >= -8 && x <= -2 && z >= -9 && z <= 0;
}

function isLighthouse(x, z) {
  return x >= 14 && x <= 16 && z >= 8 && z <= 10;
}

const warehouseBoxes = [
  { x: -22, z: -22, w: 6, d: 4 },
  { x: 10, z: -22, w: 6, d: 4 },
  { x: -4, z: -26, w: 6, d: 4 }
];

function isWarehouseZone(x, z) {
  for (const b of warehouseBoxes) {
    if (x >= b.x && x <= b.x + b.w && z >= b.z && z <= b.z + b.d) return true;
  }
  return false;
}

function landHeight(x, z) {
  if (!isLand(x, z)) return 0;

  if (z > -18) return 1;
  if (z > -27 && x > -23 && x < 23) return 1;

  let h = 1;
  h += Math.round(2.4 * Math.exp(-((x + 17) * (x + 17) + (z + 30) * (z + 30)) / 130));
  h += Math.round(3.0 * Math.exp(-((x - 21) * (x - 21) + (z + 33) * (z + 33)) / 150));
  h += Math.round(1.6 * Math.exp(-(x * x + (z + 29) * (z + 29)) / 100));
  h += Math.round(
    0.55 * Math.sin(x * 0.33 + z * 0.17) +
    0.4 * Math.cos(z * 0.29 - x * 0.13)
  );

  return Math.max(1, Math.min(5, h));
}

function addBreakwater(x0, x1, z0, z1) {
  for (let x = x0; x <= x1; x++) {
    for (let z = z0; z <= z1; z++) {
      if (isLighthouse(x, z)) continue;

      let h = z >= 5 ? 3 : 2;
      if (Math.random() < 0.18) h = Math.max(2, h - 1);

      for (let y = 1; y <= h; y++) {
        let c;
        if (y === h) {
          c = Math.random() < 0.35 ? COL.stoneLight : COL.stone;
        } else {
          c = Math.random() < 0.35 ? COL.stoneDark : COL.stone;
        }
        worldBuilder.add(x, y, z, c);
      }
    }
  }
}

function addLighthouse() {
  const cx = 16;
  const cz = 10;

  worldBuilder.addBox(cx - 2, cx, cz - 2, cz, 1, 3, COL.stoneDark);
  worldBuilder.addBox(cx - 1, cx, cz - 1, cz, 4, 5, 0xf4efe8);
  worldBuilder.addBox(cx - 1, cx, cz - 1, cz, 6, 6, 0xc0392b);
  worldBuilder.addBox(cx - 1, cx, cz - 1, cz, 7, 7, 0xf4efe8);
  worldBuilder.addBox(cx - 1, cx, cz - 1, cz, 8, 8, 0xc0392b);

  emissiveBuilder.addBox(cx - 1, cx, 9, 9, cz - 1, cz, COL.lamp);

  worldBuilder.addBox(cx - 1, cx, 10, 10, cz - 1, cz, 0x2a2a2a);
}

function addPier() {
  for (let x = -8; x <= -2; x++) {
    for (let z = -9; z <= 0; z++) {
      worldBuilder.add(x, 1, z, ((x + z) % 2 === 0) ? COL.plank : COL.plankDark);
    }
  }

  for (const x of [-8, -5, -2]) {
    for (const z of [-8, -4, -1]) {
      worldBuilder.add(x, 0, z, COL.woodDark);
    }
  }

  for (const x of [-7, -4, -3]) {
    for (const z of [-8, -4, -1]) {
      worldBuilder.add(x, 2, z, COL.woodDark);
    }
  }

  worldBuilder.addBox(-7, -6, 2, 3, -6, -5, COL.wood);
  worldBuilder.addBox(-3, -2, 2, 2, -7, -6, COL.plankDark);
  worldBuilder.addBox(-6, -5, 2, 2, -1, 0, COL.woodDark);

  worldBuilder.add(-6, 2, -7, COL.woodDark);
  worldBuilder.add(-6, 3, -7, COL.woodDark);
  worldBuilder.add(-6, 4, -7, COL.gold);

  worldBuilder.add(-4, 2, -1, COL.woodDark);
  worldBuilder.add(-4, 3, -1, COL.woodDark);
  worldBuilder.add(-4, 4, -1, COL.gold);

  for (let x = -16; x <= 16; x += 4) {
    worldBuilder.add(x, 2, -10, COL.woodDark);
  }
}

function addWarehouse(x, z) {
  const baseY = landHeight(x, z) + 1;
  const w = 6;
  const d = 4;
  const h = 3;

  for (let xx = x; xx <= x + w; xx++) {
    for (let yy = baseY; yy < baseY + h; yy++) {
      for (let zz = z; zz <= z + d; zz++) {
        let c = Math.random() < 0.25 ? COL.stoneDark : COL.stone;

        if (yy === baseY && zz === z + d && Math.abs(xx - (x + 3)) <= 1) {
          c = COL.woodDark;
        }

        if (yy === baseY + 2 && zz === z + d && (xx - x) % 2 === 1) {
          c = 0x322f2d;
        }

        if (yy === baseY + 1 && Math.random() < 0.15) {
          c = COL.wood;
        }

        worldBuilder.add(xx, yy, zz, c);
      }
    }
  }

  worldBuilder.addBox(x, x + w, baseY + h, z, z + d, 0x5b5f63);
  worldBuilder.add(x + w, baseY + h + 1, z, 0x3b3b3b);
  worldBuilder.add(x + w, baseY + h + 2, z, 0x3b3b3b);
}

function addHouse(x, z) {
  const baseY = landHeight(x, z);
  if (baseY !== 1) return;

  const w = 2 + (Math.random() * 2 | 0);
  const d = 2 + (Math.random() * 2 | 0);

  for (let xx = x; xx <= x + w; xx += 2) {
    for (let zz = z; zz <= z + d; zz += 2) {
      if (!isLand(xx, zz)) return;
      if (isWarehouseZone(xx, zz)) return;
    }
  }

  const wallBase = baseY + 1;
  const h = 2 + (Math.random() * 2 | 0);

  const wall = pick(houseColors);
  const roof = pick(roofColors);
  const win = 0x35312f;

  for (let xx = x; xx <= x + w; xx++) {
    for (let yy = wallBase; yy < wallBase + h; yy++) {
      for (let zz = z; zz <= z + d; zz++) {
        let c = wall;

        const front = zz === z + d;
        const side = xx === x + w;
        const topRow = yy === wallBase + h - 1;
        const midRow = yy === wallBase + 1;

        if ((topRow || midRow) &&
          ((front && (xx - x) % 2 === 1 && Math.random() < 0.85) ||
           (side && (zz - z) % 2 === 1 && Math.random() < 0.55))) {
          c = win;
        }

        worldBuilder.add(xx, yy, zz, c);
      }
    }
  }

  const topY = wallBase + h;
  const layers = (w >> 1) + 1;

  for (let r = 0; r < layers; r++) {
    const rx0 = x + r;
    const rx1 = x + w - r;
    if (rx0 > rx1) break;
    worldBuilder.addBox(rx0, rx1, topY + r, z, z + d, roof);
  }

  if (Math.random() < 0.45) {
    worldBuilder.add(x + (w >> 1), topY + layers, z, 0x3d3d3d);
  }
}

function addTree(x, z) {
  const h = landHeight(x, z);
  if (h <= 0) return;

  const th = 3 + (Math.random() < 0.35 ? 1 : 0);

  for (let y = 1; y <= th; y++) {
    worldBuilder.add(x, h + y, z, COL.woodDark);
  }

  const leaf = pick(leafColors);
  worldBuilder.addBox(x - 1, x + 1, h + th + 1, h + th + 2, z - 1, z + 1, leaf);
  worldBuilder.addBox(x, x, h + th + 3, z, z, leaf);
}

function addCloud(b, cx, cy, cz) {
  b.addBox(cx - 4, cx + 3, cy, cy, cz - 2, cz + 2, 0xf7fbff);
  b.addBox(cx - 3, cx + 2, cy + 1, cy + 1, cz - 1, cz + 1, 0xffffff);
  b.addBox(cx - 1, cx + 1, cy + 2, cy + 2, cz - 1, cz + 1, 0xf0f7ff);
}

function addMast(b, z, top, widths) {
  const sz = z + 1;

  b.addBox(0, 0, 3, top, z, z, COL.mast);

  const yardY = [6, 9, 12];
  const sailY = [[4, 5], [7, 8], [10, 11]];

  for (let i = 0; i < yardY.length; i++) {
    const w = widths[i] || 1;
    const y = yardY[i];

    for (let x = -w; x <= w; x++) {
      b.add(x, y, sz, COL.mast);
    }

    const [sy0, sy1] = sailY[i];
    const c = (i === 0 ? COL.sail : COL.sail2);

    for (let x = -w; x <= w; x++) {
      for (let yy = sy0; yy <= sy1; yy++) {
        b.add(x, yy, sz, c);
      }
    }
  }
}

function addFlag(b, z, top, color) {
  b.add(0, top + 1, z, color);
  b.add(0, top + 2, z, color);
}

function buildShip(b) {
  b.addBox(-3, 3, 1, 1, -8, 9, COL.hull);
  b.addBox(-2, 2, 1, 1, 10, 10, COL.hull);
  b.addBox(-1, 1, 1, 1, 11, 11, COL.hull);

  b.addBox(-2, 2, -1, -1, -7, 8, COL.hullDark);
  b.addBox(-1, 1, -1, -1, 9, 10, COL.hullDark);

  for (let z = -7; z <= 8; z++) {
    b.add(-3, 2, z, COL.hullDark);
    b.add(3, 2, z, COL.hullDark);
  }

  b.addBox(-3, 3, 2, 2, 9, 9, COL.hullDark);
  b.addBox(-2, 2, 2, 2, 10, 10, COL.hullDark);
  b.addBox(-1, 1, 2, 2, 11, 11, COL.hullDark);

  b.addBox(-2, 2, 2, 3, -8, -6, COL.hull);
  b.addBox(-2, 2, 2, 2, 7, 8, COL.wood);

  b.addBox(-2, 2, 2, 2, -5, 6, COL.deck);

  b.addBox(-2, -1, 3, 4, -3, -2, COL.wood);
  b.addBox(2, 3, 3, 3, 3, 4, COL.woodDark);
  b.addBox(-1, 1, 3, 3, 1, 2, COL.plankDark);

  addMast(b, -4, 13, [3, 2, 1]);
  addMast(b, 0, 16, [6, 4, 2]);
  addMast(b, 5, 14, [4, 3, 1]);

  for (let i = 0; i < 5; i++) {
    b.add(0, 3 + i, 11 + i, COL.mast);
  }

  addFlag(b, -4, 13, COL.gold);
  addFlag(b, 0, 16, COL.flag);
  addFlag(b, 5, 14, COL.sail);
}

// Water
for (let x = -39; x <= 39; x++) {
  for (let z = -39; z <= 39; z++) {
    if (isLand(x, z) || isBreakwater(x, z) || isPier(x, z)) continue;

    let c = waterColors[(Math.random() * waterColors.length) | 0];

    const shallow =
      (z >= -15 && z <= -9 && x >= -28 && x <= 28) ||
      (z >= -12 && z <= 12 && ((x >= -22 && x <= -8) || (x >= 8 && x <= 22)));

    if (shallow) {
      c = shallowWaterColors[(Math.random() * shallowWaterColors.length) | 0];
    }

    if (z === -9 && x >= -27 && x <= 27 && Math.random() < 0.35) {
      c = COL.foam;
    }

    worldBuilder.add(x, 0, z, c);
  }
}

// Land
for (let x = -28; x <= 28; x++) {
  for (let z = -34; z <= -10; z++) {
    const h = landHeight(x, z);

    for (let y = 1; y <= h; y++) {
      let c;

      if (y === h) {
        if (h === 1 && z >= -13) c = COL.sand;
        else if (h >= 4) c = Math.random() < 0.35 ? COL.stone : COL.dirt;
        else c = Math.random() < 0.82 ? COL.grass : COL.dirt;
      } else if (y === 1) {
        c = Math.random() < 0.35 ? COL.stoneDark : COL.stone;
      } else {
        c = Math.random() < 0.15 ? COL.stone : COL.dirt;
      }

      worldBuilder.add(x, y, z, c);
    }
  }
}

// Breakwaters
addBreakwater(-18, -14, -9, 10);
addBreakwater(14, 18, -9, 10);
addLighthouse();

// Pier
addPier();

// Warehouses
addWarehouse(-22, -22);
addWarehouse(10, -22);
addWarehouse(-4, -26);

// Harbor town houses
for (let x = -20; x <= 18; x += 6) {
  for (let z = -32; z <= -16; z += 6) {
    if (Math.random() < 0.45) {
      addHouse(x, z);
    }
  }
}

// Trees
for (let x = -27; x <= 27; x += 3) {
  for (let z = -33; z <= -12; z += 3) {
    const h = landHeight(x, z);
    if (
      h > 0 &&
      !isWarehouseZone(x, z) &&
      (h > 1 || z < -20) &&
      Math.random() < 0.11
    ) {
      addTree(x, z);
    }
  }
}

// Harbor mouth buoys
worldBuilder.add(-13, 1, 16, COL.woodDark);
worldBuilder.add(-13, 2, 16, COL.flag);
worldBuilder.add(13, 1, 16, COL.stoneDark);
worldBuilder.add(13, 2, 16, COL.sail);

// Ship
buildShip(shipBuilder);

// Clouds
addCloud(cloudBuilder, -18, 25, -5);
addCloud(cloudBuilder, 12, 27, 8);
addCloud(cloudBuilder, -2, 26, 20);
addCloud(cloudBuilder, 25, 24, -12);

// Scene renderer setup
const scene = new THREE.Scene();
scene.background = new THREE.Color(COL.sky);
scene.fog = new THREE.Fog(COL.sky, 80, 220);

const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 400);
camera.position.set(48, 34, 60);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(2, 7, 4);
controls.enableDamping = true;
controls.dampingFactor = 0.07;
controls.minDistance = 10;
controls.maxDistance = 180;
controls.maxPolarAngle = Math.PI / 2.05;
controls.rotateSpeed = 0.8;

const hemi = new THREE.HemisphereLight(0xffffff, 0x4e6a88, 1.0);
scene.add(hemi);

const sun = new THREE.DirectionalLight(0xfff4dc, 1.2);
sun.position.set(55, 70, 15);
scene.add(sun);

// Build meshes
const worldMat = new THREE.MeshLambertMaterial({ color: 0xffffff });
const worldMesh = worldBuilder.build(worldMat);
scene.add(worldMesh);

const shipMat = new THREE.MeshLambertMaterial({ color: 0xffffff });
const shipMesh = shipBuilder.build(shipMat);

const shipYaw = new THREE.Group();
shipYaw.position.set(4.4, -0.15, 7.7);
shipYaw.rotation.y = Math.PI;

const shipBob = new THREE.Group();
shipBob.add(shipMesh);
shipYaw.add(shipBob);
scene.add(shipYaw);

const emissiveMat = new THREE.MeshLambertMaterial({
  color: 0xffffff,
  emissive: 0xffb855,
  emissiveIntensity: 2.2
});
const emissiveMesh = emissiveBuilder.build(emissiveMat);
scene.add(emissiveMesh);

const lampLight = new THREE.PointLight(0xffbb66, 10, 35, 2);
lampLight.position.set(15.5, 9.5, 9.5);
scene.add(lampLight);

const cloudMat = new THREE.MeshLambertMaterial({ color: 0xffffff, fog: false });
const cloudMesh = cloudBuilder.build(cloudMat);
const cloudGroup = new THREE.Group();
cloudGroup.add(cloudMesh);
scene.add(cloudGroup);

// Resize
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// Animation loop
const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);

  const t = clock.getElapsedTime();

  controls.update();

  shipBob.position.y = Math.sin(t * 1.1) * 0.08;
  shipBob.rotation.z = Math.sin(t * 0.55) * 0.018;
  shipBob.rotation.x = Math.sin(t * 0.37) * 0.010;

  cloudGroup.rotation.y += 0.0004;
  lampLight.intensity = 8 + Math.sin(t * 3.0) * 3;

  renderer.render(scene, camera);
}

animate();
</script>
</body>
</html>
```