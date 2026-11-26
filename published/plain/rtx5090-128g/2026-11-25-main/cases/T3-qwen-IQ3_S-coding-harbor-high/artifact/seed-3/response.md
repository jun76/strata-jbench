Save the code below as `harbor-voxel.html` and open it in Chrome. It uses Three.js from a CDN, so keep an internet connection on first open.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>A sailing ship calling at a harbor</title>
<style>
  html, body {
    margin: 0;
    height: 100%;
    overflow: hidden;
    background: linear-gradient(#83c7ff 0%, #bfe7f8 48%, #fff2d6 100%);
  }
  canvas {
    display: block;
    width: 100%;
    height: 100%;
    touch-action: none;
    cursor: grab;
  }
  #title {
    position: fixed;
    top: 12px;
    left: 12px;
    color: #123;
    font: 700 16px system-ui, sans-serif;
    background: rgba(255,255,255,.62);
    padding: 7px 11px;
    border-radius: 10px;
    pointer-events: none;
  }
  #ui {
    position: fixed;
    left: 12px;
    bottom: 12px;
    color: #123;
    font: 13px system-ui, sans-serif;
    background: rgba(255,255,255,.68);
    padding: 8px 11px;
    border-radius: 10px;
    pointer-events: none;
  }
</style>
</head>
<body>
<div id="title">A sailing ship calling at a harbor</div>
<div id="ui">Left-drag: orbit · Right-drag / Shift-drag: pan · Scroll: zoom</div>
<canvas id="scene"></canvas>

<script src="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js"></script>
<script>
if (!window.THREE) {
  document.body.innerHTML = '<div style="font-family:system-ui;padding:24px;color:#123;background:#fff">Could not load Three.js from the CDN. Check your internet connection.</div>';
  throw new Error("THREE failed to load");
}

const canvas = document.getElementById("scene");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setClearColor(0x000000, 0);

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xd8e9f7, 95, 280);

const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 600);

const hemi = new THREE.HemisphereLight(0xbfe0ff, 0x6a5f42, 0.72);
scene.add(hemi);

const sun = new THREE.DirectionalLight(0xffffff, 1.0);
sun.position.set(35, 70, -10);
sun.target.position.set(0, 0, 32);
scene.add(sun);
scene.add(sun.target);

const beacon = new THREE.PointLight(0xffe28a, 1.25, 45);
beacon.position.set(-21, 14.5, 11);
scene.add(beacon);

/* ------------------------------------------------------------------ */
/* Voxel scene construction                                            */
/* ------------------------------------------------------------------ */

const voxels = new Map();
const OFF = 256;

function pack(x, y, z) {
  return ((x + OFF) << 20) | ((y + OFF) << 10) | (z + OFF);
}

function addVoxel(x, y, z, color) {
  voxels.set(pack(x, y, z), color);
}

function addBox(x1, y1, z1, x2, y2, z2, color) {
  if (x1 > x2) [x1, x2] = [x2, x1];
  if (y1 > y2) [y1, y2] = [y2, y1];
  if (z1 > z2) [z1, z2] = [z2, z1];
  for (let x = x1; x <= x2; x++) {
    for (let y = y1; y <= y2; y++) {
      for (let z = z1; z <= z2; z++) {
        addVoxel(x, y, z, color);
      }
    }
  }
}

function hash3(x, y, z) {
  let h = x * 374761393 ^ y * 668265263 ^ z * 2147483647;
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  h = Math.imul(h ^ (h >>> 16), 0x27d4eb2d);
  return (h >>> 0) / 4294967295;
}

function stoneColor(x, y, z) {
  const r = hash3(x, y, z);
  if (r < 0.30) return 0x676d73;
  if (r < 0.72) return 0x848b90;
  return 0x9aa2a7;
}

function grassColor(x, y, z) {
  const r = hash3(x, y, z);
  if (r < 0.70) return 0x568041;
  if (r < 0.90) return 0x63914e;
  return 0x4c7037;
}

/* Sea surface */
function buildSea() {
  const R = 90;
  for (let x = -R; x <= R; x++) {
    for (let z = -R; z <= R; z++) {
      const d2 = x * x + z * z;
      if (d2 > R * R) continue;

      let c;
      if (d2 < 32 * 32) c = 0x2e91bd;
      else if (z > 18) c = 0x3396a7;
      else if (z < -25) c = 0x206e97;
      else c = 0x257fb0;

      if (hash3(x, 0, z) < 0.018) c = 0x6bbcd3;
      addVoxel(x, 0, z, c);
    }
  }
}

function setWaterTop(x, z, c) {
  // Only paint on top of water, not over land or structures.
  if (!voxels.has(pack(x, 1, z))) addVoxel(x, 0, z, c);
}

function buildLand() {
  function addLandArea(x1, x2, z1, z2) {
    for (let x = x1; x <= x2; x++) {
      for (let z = z1; z <= z2; z++) {
        const beach = z <= 27;
        addVoxel(x, 0, z, beach ? 0x8a7855 : 0x574833);
        let g;
        if (beach) {
          const r = hash3(x, 1, z);
          g = r < 0.65 ? 0xd0ba8c : 0xbfad82;
        } else {
          g = grassColor(x, 1, z);
        }
        addVoxel(x, 1, z, g);
      }
    }
  }

  addLandArea(-60, -11, 24, 60); // left shore
  addLandArea(11, 60, 24, 60);   // right shore
  addLandArea(-11, 11, 44, 60);  // harbor back shore
}

function buildHills() {
  function hill(x1, z1, x2, z2) {
    for (let x = x1; x <= x2; x++) {
      for (let z = z1; z <= z2; z++) {
        const r = hash3(x, 2, z);
        addVoxel(x, 2, z, r < 0.60 ? 0x4b763b : 0x5d8a49);
        if (r < 0.55) addVoxel(x, 3, z, r < 0.50 ? 0x538142 : 0x64914e);
      }
    }
  }

  hill(24, 48, 35, 58);
  hill(-40, 48, -30, 58);
}

function buildBreakwaters() {
  for (let x = -13; x <= -11; x++) {
    for (let y = 0; y <= 3; y++) {
      for (let z = 14; z <= 24; z++) addVoxel(x, y, z, stoneColor(x, y, z));
    }
  }
  for (let x = 11; x <= 13; x++) {
    for (let y = 0; y <= 3; y++) {
      for (let z = 14; z <= 24; z++) addVoxel(x, y, z, stoneColor(x, y, z));
    }
  }

  // small rocky shoulders
  addBox(-17, 0, 18, -14, 1, 21, 0x7b8288);
  addBox(14, 0, 18, 17, 1, 21, 0x7b8288);
}

function buildFoam() {
  const foam = 0x8ed0df;
  for (let x = -18; x <= -11; x++) {
    for (let z = 13; z <= 25; z++) {
      if (hash3(x, 0, z) > 0.38) setWaterTop(x, z, foam);
    }
  }
  for (let x = 11; x <= 18; x++) {
    for (let z = 13; z <= 25; z++) {
      if (hash3(x, 0, z) > 0.38) setWaterTop(x, z, foam);
    }
  }
}

function buildLighthouse() {
  // rocky base
  for (let y = 0; y <= 2; y++) {
    for (let x = -25; x <= -19; x++) {
      for (let z = 8; z <= 14; z++) addVoxel(x, y, z, stoneColor(x, y, z));
    }
  }

  // tower
  for (let y = 3; y <= 12; y++) {
    const c = (y % 2 === 0) ? 0xd9534f : 0xf5f2ea;
    addBox(-22, y, 10, -20, y, 12, c);
  }

  // lantern
  addBox(-22, 13, 10, -20, 13, 12, 0xffd55b);
  addBox(-21, 14, 11, -21, 14, 11, 0x44494d);
}

function buildPiers() {
  function pier(x1, z1, x2, z2) {
    addBox(x1, 2, z1, x2, 2, z2, 0x9d6a3c);
    for (let x = x1; x <= x2; x++) {
      for (let z = z1 + 1; z <= z2; z += 4) {
        addBox(x, 0, z, x, 1, z, 0x5b3a20);
      }
    }
  }

  // main harbor quay
  pier(-10, 24, -8, 43);

  // secondary pier
  pier(8, 28, 10, 38);

  // crates and cargo
  addBox(-9, 3, 26, -8, 4, 27, 0xb58348);
  addBox(-9, 5, 26, -8, 5, 27, 0xc69a66);
  addBox(-9, 3, 33, -8, 4, 34, 0x8f6536);
  addBox(9, 3, 30, 10, 4, 31, 0xb58348);
  addBox(9, 3, 34, 10, 4, 35, 0x7f5a36);
}

function addBuilding(x, z, w, d, h, wall, roof) {
  for (let bx = x; bx < x + w; bx++) {
    for (let bz = z; bz < z + d; bz++) {
      for (let by = 2; by < 2 + h; by++) {
        const r = hash3(bx, by, bz);
        let c = wall;
        if (by > 2 && r < 0.18) c = 0x30373e; // window-ish voxel
        addVoxel(bx, by, bz, c);
      }
    }
  }

  // roof with slight overhang
  for (let rx = x - 1; rx <= x + w; rx++) {
    for (let rz = z - 1; rz <= z + d; rz++) {
      addVoxel(rx, 2 + h, rz, roof);
    }
  }

  // chimney
  if (h >= 3) {
    addVoxel(x + Math.floor(w / 2), 2 + h + 1, z + Math.floor(d / 2), 0x4f4f4f);
  }
}

function buildTown() {
  // left-side warehouses and houses
  addBuilding(-42, 30, 5, 4, 3, 0xb79c78, 0x4d3025);
  addBuilding(-35, 30, 4, 4, 4, 0xe6d8c2, 0x8a4a46);
  addBuilding(-42, 37, 4, 4, 3, 0xd2d6c9, 0x53697e);
  addBuilding(-35, 37, 5, 5, 4, 0xc9a17a, 0x674a34);
  addBuilding(-27, 26, 4, 3, 3, 0xa8b4b7, 0x44484c);

  // right-side town
  addBuilding(14, 27, 4, 4, 3, 0xf4ecdf, 0x984540);
  addBuilding(19, 27, 4, 4, 4, 0xe8ddc7, 0x4d6f93);
  addBuilding(24, 27, 5, 5, 3, 0xd6cab5, 0x7a513b);
  addBuilding(14, 34, 4, 4, 2, 0xd9d3c8, 0x7f8085);
  addBuilding(19, 35, 5, 4, 4, 0xf1e6d1, 0x5d814d);
  addBuilding(26, 34, 6, 5, 4, 0xc7a97b, 0x5a6b83);
  addBuilding(33, 28, 5, 4, 3, 0xe1d0b6, 0x8b443e);

  // back-of-harbor buildings
  addBuilding(-8, 46, 4, 4, 3, 0xe6ddcb, 0x8a4a46);
  addBuilding(0, 46, 4, 4, 4, 0xb9c4ce, 0x53697e);
  addBuilding(4, 45, 4, 4, 3, 0xf0e7d4, 0x75553d);

  // church with tower
  addBuilding(16, 45, 8, 9, 6, 0xf6f2e9, 0x717781);
  for (let y = 7; y <= 13; y++) addBox(19, y, 48, 21, y, 50, 0xeae6df);
  addBox(19, 14, 48, 21, 14, 50, 0x556371);
}

function addTree(x, z) {
  addBox(x, 2, z, x, 4, z, 0x5b3f27);
  addBox(x - 1, 5, z - 1, x + 1, 6, z + 1, 0x3d7236);
}

function buildTrees() {
  const spots = [
    [-30, 26], [-28, 27], [-25, 33],
    [12, 24], [35, 30], [40, 40],
    [-35, 43], [-25, 45], [30, 54], [33, 52]
  ];
  for (const [x, z] of spots) addTree(x, z);
}

function buildShip() {
  const hullDark = 0x3a2415;
  const hullMid = 0x5e3b21;
  const hullLight = 0x7c522b;
  const deck = 0xa5713b;
  const rail = 0x6c4423;
  const cabin = 0x8f6138;
  const cabinRoof = 0xd6c6a4;
  const mast = 0xbdbdbd;
  const yard = 0x9e9e9e;
  const sail = 0xf2ead7;
  const redFlag = 0xc93a36;
  const greenFlag = 0x2f6f55;

  // hull layers
  addBox(-3, 0, 28, -1, 0, 37, hullDark);
  addBox(-2, 0, 27, -1, 0, 38, hullDark);

  addBox(-4, 1, 27, 0, 1, 38, hullMid);
  addBox(-3, 1, 26, -1, 1, 39, hullMid);

  addBox(-5, 2, 27, 1, 3, 38, hullMid);
  addBox(-4, 2, 26, 0, 3, 39, hullMid);
  addBox(-3, 2, 25, -1, 3, 25, hullLight); // stern cap
  addBox(-3, 2, 39, -1, 3, 39, hullLight); // bow cap

  // black hull stripe
  addBox(-5, 2, 27, 1, 2, 38, 0x2d1d11);

  // deck
  addBox(-6, 4, 28, 1, 4, 37, deck);
  addBox(-5, 4, 27, 0, 4, 38, deck);
  addBox(-4, 4, 26, -1, 4, 39, deck);

  // bulwarks / rails
  addBox(-6, 5, 28, -6, 5, 37, rail);
  addBox(1, 5, 28, 1, 5, 37, rail);
  addBox(-5, 5, 38, 0, 5, 38, rail);
  addBox(-5, 5, 26, 0, 5, 26, rail);

  // stern cabin
  addBox(-6, 5, 25, -1, 6, 27, cabin);
  addBox(-6, 7, 25, -4, 7, 27, cabinRoof);

  // bowsprit
  addBox(-2, 5, 40, -1, 5, 42, mast);

  // masts
  addBox(-2, 4, 28, -2, 18, 28, mast);
  addBox(-2, 4, 32, -2, 21, 32, mast);
  addBox(-2, 4, 36, -2, 17, 36, mast);

  // square sails + yards
  function addSail(z, y1, y2) {
    addBox(-7, y1, z, 3, y2, z, sail);
    addBox(-7, y2 + 1, z, 3, y2 + 1, z, yard);
  }

  addSail(28, 9, 12);
  addSail(28, 14, 16);

  addSail(32, 9, 13);
  addSail(32, 15, 17);
  addSail(32, 19, 20);

  addSail(36, 10, 12);
  addSail(36, 14, 15);

  // pennants
  addBox(-1, 19, 28, 1, 20, 28, redFlag);
  addBox(0, 22, 32, 2, 23, 32, redFlag);
  addBox(-1, 18, 36, 1, 19, 36, greenFlag);

  // simple jib line
  for (let t = 1; t <= 6; t++) {
    const y = 12 - t;
    const z = 29 + t * 2;
    if (z <= 41) addBox(-2, y, z, -1, y, z, sail);
  }

  // small wake foam around the bow/stern
  const foam = 0x8ed0df;
  for (let x = -5; x <= 2; x++) setWaterTop(x, 40, foam);
  for (let x = -5; x <= 2; x++) setWaterTop(x, 25, foam);
}

function addBoat(x, z, hasSail) {
  addBox(x, 0, z, x + 2, 1, z + 2, 0x8a5e34);
  addBox(x + 1, 2, z + 1, x + 1, 4, z + 1, 0xbdbdbd);
  if (hasSail) addBox(x + 1, 3, z + 1, x + 2, 4, z + 1, 0xf2ead7);
}

function buildBoats() {
  addBoat(-16, 16, true);
  addBoat(15, 16, false);
  addBoat(3, 24, false);
}

function addCloud(x, y, z) {
  addBox(x, y, z, x + 5, y, z + 1, 0xf8fbff);
  addBox(x + 1, y + 1, z, x + 3, y + 1, z, 0xffffff);
  addBox(x + 6, y, z, x + 9, y, z + 1, 0xeef5ff);
  addBox(x + 7, y + 1, z, x + 8, y + 1, z, 0xffffff);
  addBox(x + 2, y, z + 2, x + 3, y, z + 2, 0xdde9f2);
}

function buildClouds() {
  addCloud(-48, 24, -26);
  addCloud(-14, 30, -54);
  addCloud(22, 27, -36);
  addCloud(48, 23, -8);
}

/* Build the scene */
buildSea();
buildLand();
buildHills();
buildBreakwaters();
buildFoam();
buildLighthouse();
buildPiers();
buildTown();
buildTrees();
buildShip();
buildBoats();
buildClouds();

/* Convert map to InstancedMesh */
const count = voxels.size;
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshLambertMaterial({ flatShading: true });
const mesh = new THREE.InstancedMesh(geometry, material, count);

const dummy = new THREE.Object3D();
const color = new THREE.Color();
let i = 0;

for (const [packed, col] of voxels) {
  const x = ((packed >> 20) & 1023) - OFF;
  const y = ((packed >> 10) & 1023) - OFF;
  const z = (packed & 1023) - OFF;

  dummy.position.set(x + 0.5, y + 0.5, z + 0.5);
  dummy.updateMatrix();
  mesh.setMatrixAt(i, dummy.matrix);

  color.setHex(col);
  mesh.setColorAt(i, color);

  i++;
}

mesh.instanceMatrix.needsUpdate = true;
if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
scene.add(mesh);

/* ------------------------------------------------------------------ */
/* Camera and mouse controls                                           */
/* ------------------------------------------------------------------ */

const target = new THREE.Vector3(0, 8, 32);
let theta = Math.PI + 0.18;
let phi = 1.12;
let radius = 68;
let autoRotate = true;

function updateCamera() {
  const s = Math.sin(phi);
  const c = Math.cos(phi);
  camera.position.set(
    target.x + radius * s * Math.sin(theta),
    target.y + radius * c,
    target.z + radius * s * Math.cos(theta)
  );
  camera.lookAt(target);
}

function clampPhi() {
  phi = Math.max(0.16, Math.min(1.45, phi));
}

function pan(dx, dy) {
  const factor = radius * 0.0013;
  const s = Math.sin(phi);
  const c = Math.cos(phi);
  const st = Math.sin(theta);
  const ct = Math.cos(theta);

  const right = new THREE.Vector3(-ct, 0, st);
  const up = new THREE.Vector3(-c * st, s, -c * ct);

  target.addScaledVector(right, -dx * factor);
  target.addScaledVector(up, dy * factor);

  target.y = Math.max(0, Math.min(35, target.y));
}

let dragging = false;
let dragButton = 0;
let startX = 0;
let startY = 0;

canvas.addEventListener("pointerdown", (e) => {
  dragging = true;
  dragButton = e.button;
  startX = e.clientX;
  startY = e.clientY;
  autoRotate = false;
  canvas.style.cursor = "grabbing";
});

window.addEventListener("pointermove", (e) => {
  if (!dragging) return;

  const dx = e.clientX - startX;
  const dy = e.clientY - startY;
  startX = e.clientX;
  startY = e.clientY;

  if (dragButton === 2 || e.shiftKey) {
    pan(dx, dy);
  } else {
    theta -= dx * 0.006;
    phi += dy * 0.006;
    clampPhi();
  }
});

window.addEventListener("pointerup", () => {
  dragging = false;
  canvas.style.cursor = "grab";
});

window.addEventListener("pointercancel", () => {
  dragging = false;
  canvas.style.cursor = "grab";
});

canvas.addEventListener("contextmenu", (e) => e.preventDefault());

window.addEventListener("wheel", (e) => {
  e.preventDefault();
  radius *= Math.exp(e.deltaY * 0.001);
  radius = Math.max(20, Math.min(115, radius));
}, { passive: false });

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

/* ------------------------------------------------------------------ */
/* Animation loop                                                      */
/* ------------------------------------------------------------------ */

function animate() {
  if (autoRotate) theta += 0.0007;
  updateCamera();
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}

animate();
</script>
</body>
</html>
```