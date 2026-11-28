Here's a self-contained voxel art scene — sailing ship in a harbor, with an animated water shader, bobbing ship, flapping gulls, drifting clouds, a pulsing lighthouse, and mouse-orbit controls. Paste it into one `.html` file and open in Chrome:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Harbor Calls — Voxel Art</title>
<style>
  * { box-sizing: border-box; }
  html, body { margin: 0; height: 100%; overflow: hidden; background: #9fd0ea; font-family: "Segoe UI", system-ui, sans-serif; }
  #app { position: fixed; inset: 0; }
  #title { position: fixed; top: 18px; left: 18px; z-index: 10; padding: 12px 18px; background: rgba(8, 34, 52, 0.55); color: #eaf6ff; border-radius: 14px; backdrop-filter: blur(8px); box-shadow: 0 4px 18px rgba(0,20,40,.25); border: 1px solid rgba(255,255,255,.18); pointer-events: none; }
  #title h1 { margin: 0; font-size: 20px; letter-spacing: .5px; font-weight: 700; }
  #title p { margin: 4px 0 0; font-size: 12px; opacity: .85; }
  #hint { position: fixed; bottom: 16px; left: 50%; transform: translateX(-50%); z-index: 10; padding: 8px 16px; background: rgba(8,34,52,.5); color: #dff0fa; border-radius: 999px; font-size: 12px; letter-spacing: .3px; border: 1px solid rgba(255,255,255,.15); pointer-events: none; white-space: nowrap; }
</style>
</head>
<body>
<div id="app"></div>
<div id="title"><h1>⚓ Harbor Calls</h1><p>Voxel art · a sailing ship calling at a harbor</p></div>
<div id="hint">Drag to orbit &nbsp;·&nbsp; Scroll to zoom &nbsp;·&nbsp; Right-drag to pan</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
const app = document.getElementById('app');
const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xd6eaf4, 48, 110);

// ---- sky gradient background ----
(function () {
  const c = document.createElement('canvas'); c.width = 2; c.height = 256;
  const g = c.getContext('2d');
  const grad = g.createLinearGradient(0, 0, 0, 256);
  grad.addColorStop(0.0, '#3f97d6');
  grad.addColorStop(0.45, '#7ec0e6');
  grad.addColorStop(0.78, '#c9e6f2');
  grad.addColorStop(1.0, '#eef7fa');
  g.fillStyle = grad; g.fillRect(0, 0, 2, 256);
  scene.background = new THREE.CanvasTexture(c);
})();

const camera = new THREE.PerspectiveCamera(45, innerWidth / innerHeight, 0.1, 250);
camera.position.set(20, 14, 26);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
app.appendChild(renderer.domElement);

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.target.set(2, 2.6, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.minDistance = 8;
controls.maxDistance = 70;
controls.maxPolarAngle = Math.PI * 0.49;
controls.update();

// ---- lights ----
scene.add(new THREE.HemisphereLight(0xd8ecff, 0x41596b, 0.9));
const sunLight = new THREE.DirectionalLight(0xfff1d6, 1.25);
sunLight.position.set(22, 28, 14);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
sunLight.shadow.camera.left = -34; sunLight.shadow.camera.right = 34;
sunLight.shadow.camera.top = 34; sunLight.shadow.camera.bottom = -34;
sunLight.shadow.camera.near = 2; sunLight.shadow.camera.far = 90;
sunLight.shadow.bias = -0.0006;
scene.add(sunLight); scene.add(sunLight.target);

// ---- voxel helpers ----
const boxGeo = new THREE.BoxGeometry(1, 1, 1);
const matCache = new Map();
function voxelMat(color) {
  if (!matCache.has(color)) matCache.set(color, new THREE.MeshLambertMaterial({ color }));
  return matCache.get(color);
}
function voxel(parent, x, y, z, color, sx = 1, sy = 1, sz = 1, cast = true, recv = true) {
  const m = new THREE.Mesh(boxGeo, voxelMat(color));
  m.position.set(x, y, z); m.scale.set(sx, sy, sz);
  m.castShadow = cast; m.receiveShadow = recv;
  parent.add(m); return m;
}

// ---- water (instanced voxels) ----
const WATER_X0 = -22, WATER_X1 = 22, WATER_Z0 = -18, WATER_Z1 = 18;
const COLS = WATER_X1 - WATER_X0 + 1, ROWS = WATER_Z1 - WATER_Z0 + 1;
const COUNT = COLS * ROWS;
const shipX = 5.5, shipZ = 2.5;
const water = new THREE.InstancedMesh(boxGeo, new THREE.MeshLambertMaterial({ color: 0xffffff }), COUNT);
water.receiveShadow = true;
water.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
const waterCells = [];
let wi = 0;
for (let ix = 0; ix < COLS; ix++) {
  for (let iz = 0; iz < ROWS; iz++) {
    const x = WATER_X0 + ix, z = WATER_Z0 + iz;
    const dShip = Math.hypot(x - shipX, z - shipZ);
    const inDock = (x >= -4 && x <= 1 && z >= -11 && z <= 6);
    const col = new THREE.Color(0x2e6b9a);
    if (dShip < 4.8 && dShip > 2.6) col.setHex(0xdff0ea);       // foam around hull
    else if (inDock) col.setHex(0x5f9cbf);                       // lively around dock
    else if (z <= -11) col.setHex(0x7fb4c9);                     // near shore
    col.offsetHSL(0, 0, Math.sin(ix * 12.9898 + iz * 78.233) * 0.035);
    waterCells.push({ x, z });
    water.setColorAt(wi++, col);
  }
}
water.instanceColor.needsUpdate = true;
scene.add(water);
const dummy = new THREE.Object3D();
function updateWater(t) {
  for (let i = 0; i < COUNT; i++) {
    const c = waterCells[i];
    const h = Math.sin(t * 1.5 + c.x * 0.55 + c.z * 0.75) * 0.14
            + Math.sin(t * 0.8 + c.x * 0.22 - c.z * 0.35) * 0.1;
    dummy.position.set(c.x, h, c.z);
    dummy.updateMatrix();
    water.setMatrixAt(i, dummy.matrix);
  }
  water.instanceMatrix.needsUpdate = true;
}

// ---- seabed ----
const seabed = new THREE.Mesh(new THREE.PlaneGeometry(110, 110), new THREE.MeshLambertMaterial({ color: 0x12384e }));
seabed.rotation.x = -Math.PI / 2; seabed.position.y = -1.3; seabed.receiveShadow = true;
scene.add(seabed);

// ---- land ----
const land = new THREE.Group(); scene.add(land);
for (let x = -22; x <= 22; x++) {
  for (let z = -18; z <= -12; z++) {
    const height = (z <= -14) ? 2 : 1;
    for (let y = 0; y < height; y++) {
      const isTop = (y === height - 1);
      let color;
      if (isTop) {
        color = (z >= -13)
          ? 0xe0cb92
          : new THREE.Color(0x5fa04e).offsetHSL(0, 0, Math.sin(x * 7.3 + z * 3.1) * 0.045).getHex();
      } else color = 0x7a5a3a;
      voxel(land, x, y + 0.5, z, color, 1, 1, 1, false, true);
    }
  }
}

// ---- dock ----
const dock = new THREE.Group(); scene.add(dock);
for (let x = -3; x <= 0; x++) {
  for (let z = -11; z <= 5; z++) {
    voxel(dock, x, 1.15, z, ((x + z) % 2 === 0) ? 0x8a6138 : 0x7a5230, 1, 0.3, 0.9);
  }
}
[-9, -5, -1, 3, 5.2].forEach(z => {
  [-3.4, 0.4].forEach(x => voxel(dock, x, 0.25, z, 0x4e3520, 0.55, 2.3, 0.55));
});
// crates + barrels
voxel(dock, -2.4, 1.55, -2, 0x9a6a38, 0.85, 0.85, 0.85);
voxel(dock, -2.4, 2.02, -2, 0x6d4a26, 0.9, 0.1, 0.22);
voxel(dock, -2.4, 2.02, -2, 0x6d4a26, 0.22, 0.1, 0.9);
voxel(dock, -1.3, 1.5, -2.3, 0x8a6138, 0.75, 0.75, 0.75);
voxel(dock, -2.4, 2.45, -2, 0xa9743c, 0.65, 0.65, 0.65);
[[-0.5, -6], [-2.6, -7.5]].forEach(([bx, bz]) => {
  voxel(dock, bx, 1.65, bz, 0x6d4a26, 0.7, 0.9, 0.7);
  voxel(dock, bx, 1.42, bz, 0x3a2a1a, 0.74, 0.12, 0.74);
  voxel(dock, bx, 1.9, bz, 0x3a2a1a, 0.74, 0.12, 0.74);
});

// ---- houses ----
function house(px, pz, body, roof) {
  const g = new THREE.Group(); scene.add(g);
  const w = 3, d = 3, y0 = 2;
  for (let dx = 0; dx < w; dx++) for (let dz = 0; dz < d; dz++) for (let dy = 0; dy < 2; dy++)
    voxel(g, px - 1 + dx, y0 + dy + 0.5, pz - 1 + dz, body);
  for (let r = 0; r < 3; r++) {
    const rw = w - r, rd = d - r;
    for (let dx = 0; dx < rw; dx++) for (let dz = 0; dz < rd; dz++)
      voxel(g, px - (rw - 1) / 2 + dx, y0 + 2 + r + 0.5, pz - (rd - 1) / 2 + dz, roof);
  }
  voxel(g, px + 0.9, y0 + 3.1, pz - 0.9, 0x7a4a38, 0.55, 0.9, 0.55);
  const door = new THREE.Mesh(boxGeo, voxelMat(0x4a2e1c));
  door.position.set(px, y0 + 0.65, pz + 1.5); door.scale.set(0.75, 1.3, 0.12); g.add(door);
  const winMat = new THREE.MeshLambertMaterial({ color: 0xffe08a, emissive: 0xffc44d, emissiveIntensity: 0.55 });
  [-0.9, 0.9].forEach(wx => {
    const win = new THREE.Mesh(boxGeo, winMat);
    win.position.set(px + wx, y0 + 1.35, pz + 1.5); win.scale.set(0.55, 0.55, 0.12); g.add(win);
  });
}
house(-6, -16, 0xf0e6d2, 0xb85c3e);
house(8, -16.5, 0xe8d8b8, 0x8a4a3a);

// ---- lighthouse ----
let lanternMat, lamp;
(function () {
  const px = -17, pz = -16;
  const g = new THREE.Group(); scene.add(g);
  voxel(g, px, 2.25, pz, 0x707070, 3.2, 0.5, 3.2);
  voxel(g, px, 2.7, pz, 0x828282, 2.3, 0.5, 2.3);
  const bands = [0xf3f0e8, 0xf3f0e8, 0xc0392b, 0xc0392b, 0xf3f0e8, 0xf3f0e8, 0xc0392b];
  bands.forEach((c, i) => voxel(g, px, 3.45 + i, pz, c, 2, 1, 2));
  voxel(g, px, 10.05, pz, 0x2e2a26, 2.2, 0.2, 2.2);
  lanternMat = new THREE.MeshLambertMaterial({ color: 0xffe08a, emissive: 0xffc44d, emissiveIntensity: 1.4 });
  const lantern = new THREE.Mesh(boxGeo, lanternMat);
  lantern.position.set(px, 10.5, pz); lantern.scale.set(1.5, 0.75, 1.5); g.add(lantern);
  voxel(g, px, 11.0, pz, 0x2e2a26, 1.9, 0.3, 1.9);
  voxel(g, px, 11.3, pz, 0x2e2a26, 0.35, 0.3, 0.35);
  voxel(g, px - 2.2, 2.35, pz + 1.2, 0x6a6a6a, 1.2, 0.7, 1.0);
  voxel(g, px + 2.0, 2.3, pz - 1.3, 0x787878, 0.9, 0.6, 0.9);
  lamp = new THREE.PointLight(0xffd98a, 1.3, 22, 2);
  lamp.position.set(px, 10.5, pz);
  scene.add(lamp);
})();

// ---- crane ----
(function () {
  const px = 13.5, pz = -16.5;
  const g = new THREE.Group(); scene.add(g);
  voxel(g, px, 2.5, pz, 0x3f6d8e, 0.9, 1.0, 0.9);
  voxel(g, px, 3.75, pz, 0x3f6d8e, 0.6, 3.0, 0.6);
  const boom = new THREE.Mesh(boxGeo, voxelMat(0xc0392b));
  boom.scale.set(0.32, 0.32, 5.2); boom.position.set(px, 5.35, pz + 1.6);
  boom.rotation.x = -0.42; boom.castShadow = true; g.add(boom);
  const tip = new THREE.Vector3(0, Math.sin(0.42) * 2.6, Math.cos(0.42) * 2.6);
  const tipPos = new THREE.Vector3(px, 5.35, pz + 1.6).add(tip);
  const cable = new THREE.Mesh(boxGeo, voxelMat(0x222222));
  cable.scale.set(0.07, 1.1, 0.07); cable.position.set(tipPos.x, tipPos.y - 0.55, tipPos.z); g.add(cable);
  voxel(g, tipPos.x, tipPos.y - 1.15, tipPos.z, 0x222222, 0.35, 0.35, 0.35);
})();

// ---- rocks in water ----
voxel(scene, 13.2, 0.35, -9, 0x6f6f6f, 1.3, 1.1, 1.1);
voxel(scene, 15.0, 0.3, -7.8, 0x7a7a7a, 0.9, 0.8, 0.9);
voxel(scene, 12.3, 0.2, -6.6, 0x656565, 0.7, 0.6, 0.7);

// ---- ship ----
const ship = new THREE.Group();
ship.position.set(shipX, 0.15, shipZ);
ship.rotation.y = -0.1;
scene.add(ship);

const hullW = { 6: 0.5, 5: 1.5, 4: 2.2, 3: 2.5, 2: 2.5, 1: 2.5, 0: 2.5, -1: 2.5, -2: 2.5, -3: 2.5, -4: 2.5, -5: 2.3, -6: 2.2 };
for (let z = -6; z <= 6; z++) {
  const half = hullW[z];
  for (let x = -3; x <= 3; x++) {
    if (Math.abs(x) <= half * 0.6 + 0.2) voxel(ship, x, 0, z, 0x4e2e1a);
    if (Math.abs(x) <= half * 0.85 + 0.2) voxel(ship, x, 1, z, 0x6d4023);
    if (Math.abs(x) <= half + 0.2) voxel(ship, x, 2, z, 0xa03d2b);
    if (Math.abs(x) <= half - 0.7 + 0.2) voxel(ship, x, 3, z, 0xd9b382);
  }
}
// stern castle + forecastle
for (let dx = -1; dx <= 1; dx++) for (let dz = -1; dz <= 0; dz++) voxel(ship, dx, 4, -5 + dz, 0x6d4023);
voxel(ship, 0, 4.7, -5.5, 0xd9b382, 3.2, 0.35, 2.2);
voxel(ship, 0, 4, 4, 0x6d4023); voxel(ship, 0, 4, 5, 0x6d4023);
voxel(ship, 0, 4.7, 4.5, 0xd9b382, 1.2, 0.3, 2.2);
// masts
const mastMainZ = -1, mastForeZ = 3;
[mastMainZ, mastForeZ].forEach(mz => {
  for (let y = 3.5; y <= 8.5; y += 1) voxel(ship, 0, y, mz, 0x4a2c18);
  voxel(ship, 0, 9.3, mz, 0x2e1a0e, 0.5, 0.5, 0.5);
});
// yards
voxel(ship, 0, 7.3, mastMainZ, 0x3a2412, 5.4, 0.3, 0.3);
voxel(ship, 0, 7.0, mastForeZ, 0x3a2412, 4.6, 0.3, 0.3);
// sails (billow toward bow)
for (let x = -2; x <= 2; x++) {
  const z = mastMainZ + 0.45 * (1 - Math.abs(x) / 2.5);
  voxel(ship, x, 4.5, z, 0xefe6cf, 1.05, 1.05, 0.14);
  voxel(ship, x, 5.5, z, 0xf3ead6, 1.05, 1.05, 0.14);
  voxel(ship, x, 6.5, z, 0xf7f0de, 1.05, 1.05, 0.14);
}
[-1.5, -0.5, 0.5, 1.5].forEach(x => {
  const z = mastForeZ + 0.4 * (1 - Math.abs(x) / 2);
  voxel(ship, x, 4.5, z, 0xefe6cf, 1.05, 1.05, 0.14);
  voxel(ship, x, 5.5, z, 0xf3ead6, 1.05, 1.05, 0.14);
  voxel(ship, x, 6.2, z, 0xf7f0de, 1.05, 1.05, 0.14);
});
// bowsprit + jib
voxel(ship, 0, 3.7, 6.8, 0x4a2c18, 0.28, 0.28, 1.2);
voxel(ship, 0, 3.95, 8.0, 0x4a2c18, 0.26, 0.26, 1.2);
voxel(ship, 0, 4.2, 9.1, 0x4a2c18, 0.24, 0.24, 1.0);
for (let i = 0; i <= 5; i++) {
  voxel(ship, 0, 4.0 + i * 0.55, 8.6 - i * 0.92, 0xeadfc4, 0.16, 0.55, 0.95);
}
// deck cargo
voxel(ship, -1.6, 3.7, -2.5, 0x9a6a38, 0.8, 0.8, 0.8);
voxel(ship, 1.6, 3.7, 0.5, 0x6d4a26, 0.65, 0.85, 0.65);
// pennants
const pennantMain = new THREE.Group();
pennantMain.position.set(0, 9.0, mastMainZ);
voxel(pennantMain, 0, 0, -0.85, 0xd64533, 0.85, 0.16, 1.6);
ship.add(pennantMain);
const pennantFore = new THREE.Group();
pennantFore.position.set(0, 9.0, mastForeZ);
voxel(pennantFore, 0, 0, -0.7, 0xd64533, 0.7, 0.14, 1.3);
ship.add(pennantFore);
// rigging
function rigLine(p1, p2) {
  const g = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(...p1), new THREE.Vector3(...p2)]);
  ship.add(new THREE.Line(g, new THREE.LineBasicMaterial({ color: 0x2b2b2b })));
}
rigLine([0, 9.1, mastMainZ], [0, 3.7, 6.5]);
rigLine([0, 9.1, mastMainZ], [0, 4.4, -6.2]);
rigLine([0, 9.1, mastMainZ], [-2.4, 3.5, mastMainZ]);
rigLine([0, 9.1, mastMainZ], [2.4, 3.5, mastMainZ]);
rigLine([0, 9.1, mastForeZ], [0, 4.1, 9.1]);
rigLine([0, 9.1, mastForeZ], [-2.2, 3.5, mastForeZ]);
rigLine([0, 9.1, mastForeZ], [2.2, 3.5, mastForeZ]);
// foam cubes around hull
const foamCubes = [];
[[-2.7, -3.5], [2.7, -1.5], [-2.7, 0.5], [2.7, 2.5], [-2.6, 3.5], [2.6, 4.5]].forEach(([fx, fz]) => {
  foamCubes.push(voxel(ship, fx, 0.25, fz, 0xffffff, 0.55, 0.22, 0.55, false, false));
});

// ---- buoys ----
const buoys = [];
[[10.5, 7], [-8, -5], [11, -3]].forEach(([bx, bz]) => {
  const g = new THREE.Group(); g.position.set(bx, 0.05, bz); scene.add(g);
  voxel(g, 0, 0, 0, 0xc0392b, 0.55, 0.55, 0.55);
  voxel(g, 0, 0.45, 0, 0xf3f0e8, 0.32, 0.3, 0.32);
  buoys.push(g);
});

// ---- gulls ----
const gulls = [];
function makeGull(phase, radius, speed, height, cx, cz) {
  const g = new THREE.Group();
  const mat = voxelMat(0xf4f6f8);
  const body = new THREE.Mesh(boxGeo, mat); body.scale.set(0.4, 0.24, 0.8); g.add(body);
  const tail = new THREE.Mesh(boxGeo, mat); tail.scale.set(0.28, 0.1, 0.3); tail.position.set(0, 0, -0.5); g.add(tail);
  const wingL = new THREE.Group(); wingL.position.set(-0.18, 0, 0);
  const wl = new THREE.Mesh(boxGeo, mat); wl.scale.set(0.95, 0.1, 0.55); wl.position.set(-0.6, 0, 0); wingL.add(wl); g.add(wingL);
  const wingR = new THREE.Group(); wingR.position.set(0.18, 0, 0);
  const wr = new THREE.Mesh(boxGeo, mat); wr.scale.set(0.95, 0.1, 0.55); wr.position.set(0.6, 0, 0); wingR.add(wr); g.add(wingR);
  scene.add(g);
  gulls.push({ g, wingL, wingR, phase, radius, speed, height, cx, cz });
}
makeGull(0.0, 6.0, 0.35, 10, 5.5, 2.5);
makeGull(1.7, 8.0, 0.28, 11, -2, -2);
makeGull(3.4, 5.5, 0.40, 9.5, 12, -4);
makeGull(5.1, 9.0, 0.22, 12, 0, 6);

// ---- clouds ----
const clouds = [];
function makeCloud(x, y, z, scale, speed) {
  const g = new THREE.Group(); g.position.set(x, y, z); g.scale.setScalar(scale);
  const mat = new THREE.MeshLambertMaterial({ color: 0xf7fafd });
  [[0, 0, 0, 2.6, 1.1, 1.6], [-1.5, 0.1, 0.2, 1.6, 0.9, 1.2], [1.5, 0.15, -0.2, 1.5, 0.85, 1.3], [0.3, 0.75, 0, 1.7, 0.7, 1.2]].forEach(([cx, cy, cz, sx, sy, sz]) => {
    const m = new THREE.Mesh(boxGeo, mat);
    m.position.set(cx, cy, cz); m.scale.set(sx, sy, sz);
    g.add(m);
  });
  scene.add(g);
  clouds.push({ g, speed, baseY: y });
}
makeCloud(-15, 16, -12, 1.0, 0.45);
makeCloud(8, 18, -16, 1.3, 0.35);
makeCloud(20, 15, -4, 0.9, 0.55);
makeCloud(-4, 17.5, 6, 1.15, 0.4);

// ---- sun ----
const sunGroup = new THREE.Group();
sunGroup.position.set(-19, 18, -14);
const sunMat = new THREE.MeshBasicMaterial({ color: 0xffd76a, fog: false });
function sunVoxel(x, y, s) {
  const m = new THREE.Mesh(boxGeo, sunMat);
  m.position.set(x, y, 0); m.scale.set(s, s, s * 0.35);
  sunGroup.add(m);
}
sunVoxel(0, 0, 1.6);
sunVoxel(1.9, 0, 1.1); sunVoxel(-1.9, 0, 1.1);
sunVoxel(0, 1.9, 1.1); sunVoxel(0, -1.9, 1.1);
sunVoxel(1.35, 1.35, 0.85); sunVoxel(-1.35, 1.35, 0.85);
sunVoxel(1.35, -1.35, 0.85); sunVoxel(-1.35, -1.35, 0.85);
scene.add(sunGroup);

// ---- animation ----
const clock = new THREE.Clock();
let last = 0;
function animate() {
  requestAnimationFrame(animate);
  const t = clock.getElapsedTime();
  const dt = Math.min(t - last, 0.05); last = t;

  updateWater(t);

  // ship bobbing
  ship.position.y = 0.15 + Math.sin(t * 0.85) * 0.18;
  ship.rotation.z = Math.sin(t * 0.6) * 0.035;
  ship.rotation.x = Math.sin(t * 0.5 + 1.2) * 0.022;

  // pennants waving
  pennantMain.rotation.y = Math.sin(t * 3.2) * 0.3;
  pennantFore.rotation.y = Math.sin(t * 3.8 + 1) * 0.3;

  // foam pulsing
  foamCubes.forEach((m, i) => {
    const s = 0.4 + 0.3 * (0.5 + 0.5 * Math.sin(t * 2.3 + i * 1.7));
    m.scale.set(s, 0.18, s);
  });

  // buoys
  buoys.forEach((b, i) => {
    b.position.y = 0.05 + Math.sin(t * 1.7 + i * 2.1) * 0.14;
    b.rotation.z = Math.sin(t * 1.3 + i) * 0.1;
  });

  // gulls
  gulls.forEach(gu => {
    const a = t * gu.speed + gu.phase;
    gu.g.position.set(
      gu.cx + Math.cos(a) * gu.radius,
      gu.height + Math.sin(t * 0.7 + gu.phase) * 0.6,
      gu.cz + Math.sin(a) * gu.radius
    );
    gu.g.rotation.y = -a;
    const flap = Math.sin(t * 8.5 + gu.phase * 3) * 0.65;
    gu.wingL.rotation.z = flap;
    gu.wingR.rotation.z = -flap;
  });

  // clouds drift
  clouds.forEach((c, i) => {
    c.g.position.x += c.speed * dt;
    c.g.position.y = c.baseY + Math.sin(t * 0.5 + i * 1.4) * 0.3;
    if (c.g.position.x > 52) c.g.position.x = -52;
  });

  // lighthouse pulse
  lanternMat.emissiveIntensity = 1.3 + Math.sin(t * 2.4) * 0.9;
  lamp.intensity = 1.2 + Math.sin(t * 2.4) * 0.7;

  controls.update();
  renderer.render(scene, camera);
}
animate();

addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
</script>
</body>
</html>
```

**What's in the scene:** a two-masted sailing ship with cream square sails, a jib, pennants, rigging lines and pulsing foam cubes; a wooden dock with crates, barrels and posts; a voxel harbor with two houses, a red-and-white lighthouse (with a pulsing lamp), a crane, rocks and bobbing buoys; animated instanced-voxel water; flying gulls, drifting voxel clouds, a voxel sun and a gradient sky.

**Controls:** drag to orbit, scroll to zoom, right-drag to pan. No libraries to install — just the file and Chrome. If you want it smaller, the water grid (`WATER_X0..Z1`) and `COLS × ROWS` count can be reduced, but the default runs comfortably.