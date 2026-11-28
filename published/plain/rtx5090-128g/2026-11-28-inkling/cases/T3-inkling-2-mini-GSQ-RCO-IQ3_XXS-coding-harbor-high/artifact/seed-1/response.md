Here's a single self-contained HTML file (voxel ocean, dock, moored two-mast sailing ship with rigging, cabin, crates, lamp, warehouse, rowboat, clouds, gulls — all procedural, no assets). It uses Three.js from a CDN, so Chrome needs internet on first load. Just save it as `harbor.html` and open it.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sailing Ship at Harbor — Voxel Scene</title>
<style>
  html, body { margin: 0; height: 100%; overflow: hidden; background: #8fc9e6; }
  canvas { display: block; }
  #hud {
    position: fixed; top: 18px; left: 18px; z-index: 10;
    background: rgba(16, 28, 38, 0.62); color: #eaf4f8;
    padding: 13px 17px; border-radius: 12px;
    backdrop-filter: blur(6px); pointer-events: none;
    font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
    box-shadow: 0 4px 18px rgba(0,0,0,0.25);
  }
  #hud h1 { margin: 0 0 5px; font-size: 17px; font-weight: 600; letter-spacing: 0.4px; }
  #hud p { margin: 0; font-size: 12px; opacity: 0.85; }
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
<div id="hud">
  <h1>⛵ Sailing Ship at Harbor</h1>
  <p>Drag to orbit · Scroll to zoom · Right-drag to pan</p>
</div>
<canvas id="scene"></canvas>
<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// ---------- renderer / scene / camera ----------
const canvas = document.getElementById('scene');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.12;

const scene = new THREE.Scene();
const skyCanvas = document.createElement('canvas');
skyCanvas.width = 4; skyCanvas.height = 512;
const sg = skyCanvas.getContext('2d');
const grad = sg.createLinearGradient(0, 0, 0, 512);
grad.addColorStop(0.00, '#5fa8dd');
grad.addColorStop(0.45, '#8fc9e6');
grad.addColorStop(0.75, '#cfe7ee');
grad.addColorStop(1.00, '#f7e9c2');
sg.fillStyle = grad; sg.fillRect(0, 0, 4, 512);
const skyTex = new THREE.CanvasTexture(skyCanvas);
skyTex.colorSpace = THREE.SRGBColorSpace;
scene.background = skyTex;
scene.fog = new THREE.Fog(0xcfe0ea, 70, 160);

const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 400);
camera.position.set(21, 13, 24);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(5, 2.6, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.minDistance = 8;
controls.maxDistance = 70;
controls.minPolarAngle = 0.12;
controls.maxPolarAngle = 1.45;

// ---------- lights ----------
scene.add(new THREE.HemisphereLight(0xd4ecff, 0x33544a, 0.85));
scene.add(new THREE.AmbientLight(0xffffff, 0.12));
const sun = new THREE.DirectionalLight(0xfff0d2, 2.3);
sun.position.set(18, 26, 12);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -30; sun.shadow.camera.right = 30;
sun.shadow.camera.top = 30; sun.shadow.camera.bottom = -30;
sun.shadow.camera.near = 2; sun.shadow.camera.far = 80;
sun.shadow.bias = -0.0004;
scene.add(sun);

// ---------- voxel helpers ----------
const matCache = new Map();
function mat(color) {
  if (!matCache.has(color)) {
    matCache.set(color, new THREE.MeshStandardMaterial({ color, roughness: 0.88, metalness: 0.02 }));
  }
  return matCache.get(color);
}
const unitBox = new THREE.BoxGeometry(1, 1, 1);
function addBox(group, w, h, d, x, y, z, color, opts = {}) {
  const m = new THREE.Mesh(unitBox, opts.mat || mat(color));
  m.scale.set(w, h, d);
  m.position.set(x, y, z);
  if (opts.rotX) m.rotation.x = opts.rotX;
  if (opts.rotY) m.rotation.y = opts.rotY;
  if (opts.rotZ) m.rotation.z = opts.rotZ;
  m.castShadow = opts.cast !== false;
  m.receiveShadow = opts.receive !== false;
  group.add(m);
  return m;
}
const winMat = new THREE.MeshStandardMaterial({ color: 0xf2d38a, emissive: 0xe0a83f, emissiveIntensity: 0.55, roughness: 0.6 });

// ---------- ocean (instanced voxel tiles) ----------
const waterData = [];
for (let x = -22; x <= 8; x++) for (let z = -15; z <= 15; z++)
  waterData.push({ x, z, phase: Math.random() * Math.PI * 2 });
const water = new THREE.InstancedMesh(
  new THREE.BoxGeometry(1, 0.6, 1),
  new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.55, metalness: 0.08 }),
  waterData.length
);
water.receiveShadow = true;
water.castShadow = false;
const tmpM = new THREE.Matrix4(), tmpQ = new THREE.Quaternion(), tmpS = new THREE.Vector3(), tmpP = new THREE.Vector3(), tmpC = new THREE.Color();
for (let i = 0; i < waterData.length; i++) {
  const d = waterData[i];
  tmpP.set(d.x, -0.32, d.z); tmpS.set(0.96, 1, 0.96);
  tmpM.compose(tmpP, tmpQ, tmpS);
  water.setMatrixAt(i, tmpM);
  tmpC.setHSL(0.565 + Math.random() * 0.025, 0.52 + Math.random() * 0.12, 0.36 + Math.random() * 0.10);
  water.setColorAt(i, tmpC);
}
water.instanceMatrix.needsUpdate = true;
if (water.instanceColor) water.instanceColor.needsUpdate = true;
scene.add(water);

// ---------- harbor dock ----------
const dock = new THREE.Group(); scene.add(dock);
addBox(dock, 6.2, 1.0, 22.6, 11.5, 0.95, 0, '#5c3a20');                 // skirt
const plankPalette = ['#8a5a33', '#7d5229', '#94643a', '#83562f'];
for (let x = 9; x <= 14; x++) for (let z = -10; z <= 10; z++) {
  addBox(dock, 0.98, 0.3, 0.98, x, 1.45, z, plankPalette[((x * 7 + z * 13) % 4 + 4) % 4]);
}
for (let z = -10; z <= 10; z += 4) addBox(dock, 0.5, 1.9, 0.5, 8.7, 0.55, z, '#4a2f1b'); // posts
// bollards
[-4.5, 0, 4.5].forEach(z => {
  addBox(dock, 0.55, 0.55, 0.55, 8.9, 1.875, z, '#2f343b');
  addBox(dock, 0.30, 0.18, 0.30, 8.9, 2.20, z, '#454b54');
});
// crates
addBox(dock, 1.3, 1.3, 1.3, 10.3, 2.25, -5.5, '#b07f3f');
addBox(dock, 1.1, 1.1, 1.1, 11.6, 2.15, -5.5, '#9c6a33');
addBox(dock, 0.9, 0.9, 0.9, 10.35, 3.35, -5.5, '#c99e5f');
addBox(dock, 1.0, 1.0, 1.0, 10.2, 2.10, 5.7, '#b07f3f');
addBox(dock, 0.8, 0.8, 0.8, 11.3, 2.00, 5.6, '#9c6a33');
// barrels
addBox(dock, 1.1, 1.1, 1.1, 9.7, 2.15, -3.2, '#7a4a26');
addBox(dock, 1.1, 1.1, 1.1, 9.7, 2.15, -1.9, '#6b3f21');
// lamp post
addBox(dock, 0.32, 2.7, 0.32, 13.9, 2.95, -8.5, '#3a3f45');
const lampMat = new THREE.MeshStandardMaterial({ color: 0xffd27a, emissive: 0xffc44d, emissiveIntensity: 1.3, roughness: 0.5 });
addBox(dock, 0.6, 0.6, 0.6, 13.9, 4.45, -8.5, null, { mat: lampMat, cast: false });
addBox(dock, 0.75, 0.18, 0.75, 13.9, 4.82, -8.5, '#3a3f45');
const lampLight = new THREE.PointLight(0xffd27a, 6, 11, 2);
lampLight.position.set(13.9, 4.45, -8.5);
scene.add(lampLight);
// warehouse
addBox(dock, 4.0, 3.4, 4.5, 12.5, 3.3, 8.5, '#e0d3b8');
addBox(dock, 2.5, 0.35, 4.9, 11.55, 4.95, 8.5, '#8a5533', { rotZ: 0.5 });
addBox(dock, 2.5, 0.35, 4.9, 13.45, 4.95, 8.5, '#8a5533', { rotZ: -0.5 });
addBox(dock, 0.5, 0.4, 4.95, 12.5, 5.60, 8.5, '#6e4324');
addBox(dock, 0.3, 2.1, 1.5, 10.42, 2.65, 8.5, '#3d2a1a', { cast: false });
addBox(dock, 0.2, 0.7, 0.7, 10.42, 3.95, 7.15, null, { mat: winMat, cast: false });
addBox(dock, 0.2, 0.7, 0.7, 10.42, 3.95, 9.85, null, { mat: winMat, cast: false });

// ---------- sailing ship ----------
const ship = new THREE.Group();
// hull (stacked voxel layers)
for (let x = -1; x <= 1; x++) for (let z = -4; z <= 4; z++) addBox(ship, 1, 1, 1, x, 0.5, z, '#4e3018');
for (let x = -2; x <= 2; x++) for (let z = -5; z <= 4; z++) addBox(ship, 1, 1, 1, x, 1.5, z, '#6a4022');
for (let x = -2; x <= 2; x++) for (let z = -5; z <= 5; z++) addBox(ship, 1, 1, 1, x, 2.5, z, '#7d4c28');
for (let x = -1; x <= 1; x++) addBox(ship, 1, 1, 1, x, 2.5, 6, '#7d4c28');   // bow tip
addBox(ship, 4.8, 1.0, 0.5, 0, 2.5, -5.6, '#4e3018');                        // transom
addBox(ship, 4.9, 0.35, 10.9, 0, 3.15, 0, '#d9b382');                        // deck
addBox(ship, 0.5, 1.9, 0.5, 0, 3.6, 6.1, '#4e3018');                         // prow post
// cabin
addBox(ship, 3.0, 1.35, 2.7, 0, 3.95, -4.0, '#caa26f');
addBox(ship, 3.5, 0.4, 3.1, 0, 4.80, -4.0, '#4e2f18');
addBox(ship, 0.14, 0.55, 0.55, 1.55, 4.0, -4.0, null, { mat: winMat, cast: false });
addBox(ship, 0.14, 0.55, 0.55, -1.55, 4.0, -4.0, null, { mat: winMat, cast: false });
addBox(ship, 0.7, 0.5, 0.14, 0, 4.0, -5.42, null, { mat: winMat, cast: false });
// masts
addBox(ship, 0.5, 6.4, 0.5, 0, 7.0, 3, '#5b3a22');
addBox(ship, 0.5, 6.0, 0.5, 0, 6.8, -1.5, '#5b3a22');
addBox(ship, 0.75, 0.35, 0.75, 0, 10.30, 3, '#4e3018');
// sails
const foreSailColors = ['#f4ecdc', '#efe4cf', '#f4ecdc', '#ece0c6'];
for (let i = 0; i < 4; i++) addBox(ship, 5.2, 0.95, 0.42, 0, 5.15 + i * 1.08, 2.75, foreSailColors[i]);
addBox(ship, 6.1, 0.26, 0.26, 0, 9.20, 3, '#5b3a22');
const mainSailColors = ['#efe4c8', '#e9dcbe', '#efe4c8', '#e7d9b8'];
for (let i = 0; i < 4; i++) addBox(ship, 4.7, 0.95, 0.42, 0, 4.95 + i * 1.08, -1.75, mainSailColors[i]);
addBox(ship, 5.7, 0.26, 0.26, 0, 8.80, -1.5, '#5b3a22');
// flags
const pennants = [];
pennants.push({ mesh: addBox(ship, 0.16, 0.42, 0.95, 0, 4.55, 6.45, '#d9483b'), phase: 0 });
pennants.push({ mesh: addBox(ship, 0.8, 0.4, 0.14, 0.55, 9.90, -1.5, '#d9483b'), phase: 1.9 });
// rigging lines
function rig(a, b) {
  const g = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(...a), new THREE.Vector3(...b)]);
  ship.add(new THREE.Line(g, new THREE.LineBasicMaterial({ color: 0x3a2c1c })));
}
rig([0, 10.15, 3], [0, 4.5, 6.1]);
rig([0, 10.15, 3], [2.5, 3.9, 3]);
rig([0, 10.15, 3], [-2.5, 3.9, 3]);
rig([0, 9.75, -1.5], [0, 4.6, -5.4]);
rig([0, 9.75, -1.5], [2.5, 3.9, -1.5]);
rig([0, 9.75, -1.5], [-2.5, 3.9, -1.5]);
ship.position.set(4.8, -0.55, 0);
scene.add(ship);

// ---------- mooring ropes (ship -> dock bollards) ----------
const ropeMat = new THREE.LineBasicMaterial({ color: 0x3a2c1c });
const ropes = [];
function addRope(local, bollard) {
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(5 * 3), 3));
  const line = new THREE.Line(geo, ropeMat);
  scene.add(line);
  ropes.push({ line, local: new THREE.Vector3(...local), bollard: new THREE.Vector3(...bollard) });
}
addRope([2.5, 2.9, 4.4], [8.9, 2.2, 4.5]);
addRope([2.5, 2.9, -4.0], [8.9, 2.2, -4.5]);
const ropeTmp = new THREE.Vector3();
function updateRopes() {
  ship.updateMatrixWorld();
  ropes.forEach(r => {
    const a = ropeTmp.copy(r.local).applyMatrix4(ship.matrixWorld);
    const b = r.bollard;
    const pos = r.line.geometry.attributes.position;
    for (let i = 0; i < 5; i++) {
      const t = i / 4;
      pos.setXYZ(i,
        a.x + (b.x - a.x) * t,
        a.y + (b.y - a.y) * t - Math.sin(t * Math.PI) * 0.32,
        a.z + (b.z - a.z) * t);
    }
    pos.needsUpdate = true;
  });
}

// ---------- small rowboat ----------
const boat = new THREE.Group();
addBox(boat, 1.6, 0.5, 3.4, 0, 0.0, 0, '#5e3b21');
addBox(boat, 0.35, 0.6, 3.8, -0.85, 0.45, 0, '#74452a');
addBox(boat, 0.35, 0.6, 3.8, 0.85, 0.45, 0, '#74452a');
addBox(boat, 2.0, 0.6, 0.35, 0, 0.45, -1.75, '#74452a');
addBox(boat, 2.0, 0.6, 0.35, 0, 0.45, 1.75, '#74452a');
addBox(boat, 1.5, 0.14, 0.55, 0, 0.55, -0.7, '#caa26f');
addBox(boat, 1.5, 0.14, 0.55, 0, 0.55, 0.7, '#caa26f');
boat.position.set(-9, 0, 6.5);
scene.add(boat);

// ---------- sun, clouds, gulls ----------
const sunMat = new THREE.MeshStandardMaterial({ color: 0xffe9a3, emissive: 0xffd65e, emissiveIntensity: 1.4, roughness: 0.7 });
addBox(scene, 3.4, 3.4, 1.2, -13, 17, -14, null, { mat: sunMat, cast: false, receive: false });

const clouds = [];
function makeCloud(x, y, z, s, speed) {
  const g = new THREE.Group();
  addBox(g, 2.4 * s, 1.0 * s, 1.5 * s, 0, 0, 0, '#ffffff', { cast: false, receive: false });
  addBox(g, 1.3 * s, 0.8 * s, 1.1 * s, 1.3 * s, -0.1 * s, 0.2 * s, '#f2f7fa', { cast: false, receive: false });
  addBox(g, 1.1 * s, 0.7 * s, 1.0 * s, -1.2 * s, 0.35 * s, -0.15 * s, '#eef5f9', { cast: false, receive: false });
  addBox(g, 1.5 * s, 0.6 * s, 1.0 * s, 0.3 * s, 0.6 * s, 0.1 * s, '#ffffff', { cast: false, receive: false });
  g.position.set(x, y, z);
  g.userData.speed = speed;
  scene.add(g); clouds.push(g);
}
makeCloud(-12, 13.5, -8, 1.6, 0.55);
makeCloud(2, 15.5, -12, 1.9, 0.42);
makeCloud(11, 12.5, 6, 1.3, 0.70);
makeCloud(-4, 14.5, 10, 1.5, 0.50);

const gulls = [];
function makeGull(phase, r, speed, h) {
  const g = new THREE.Group();
  addBox(g, 0.4, 0.3, 0.9, 0, 0, 0, '#ffffff', { cast: false, receive: false });
  addBox(g, 0.16, 0.14, 0.3, 0, -0.02, 0.55, '#f59b3c', { cast: false, receive: false });
  const wingGeoR = new THREE.BoxGeometry(0.95, 0.12, 0.5); wingGeoR.translate(0.475, 0, 0);
  const wingR = new THREE.Mesh(wingGeoR, mat('#f2f5f7')); wingR.position.set(0.15, 0.12, 0); wingR.castShadow = false; g.add(wingR);
  const wingGeoL = new THREE.BoxGeometry(0.95, 0.12, 0.5); wingGeoL.translate(-0.475, 0, 0);
  const wingL = new THREE.Mesh(wingGeoL, mat('#f2f5f7')); wingL.position.set(-0.15, 0.12, 0); wingL.castShadow = false; g.add(wingL);
  g.scale.setScalar(1.4);
  scene.add(g);
  gulls.push({ g, wingR, wingL, phase, r, speed, h });
}
makeGull(0, 8.5, 0.34, 9.6);
makeGull(2.1, 10.5, 0.29, 10.4);
makeGull(4.2, 9.2, 0.38, 8.8);

// ---------- animation ----------
const clock = new THREE.Clock();
function animate() {
  requestAnimationFrame(animate);
  const dt = clock.getDelta();
  const t = clock.elapsedTime;

  // waves
  for (let i = 0; i < waterData.length; i++) {
    const d = waterData[i];
    const y = -0.32 + Math.sin(t * 1.4 + d.x * 0.4 + d.z * 0.35 + d.phase) * 0.13;
    tmpP.set(d.x, y, d.z); tmpS.set(0.96, 1, 0.96);
    tmpM.compose(tmpP, tmpQ, tmpS);
    water.setMatrixAt(i, tmpM);
  }
  water.instanceMatrix.needsUpdate = true;

  // ship bobbing
  ship.position.y = -0.55 + Math.sin(t * 1.15 + 0.6) * 0.16;
  ship.rotation.z = Math.sin(t * 0.9) * 0.045;
  ship.rotation.x = Math.sin(t * 0.75 + 2.0) * 0.03;
  ship.rotation.y = Math.sin(t * 0.4) * 0.03;

  updateRopes();

  // flags
  pennants.forEach(p => { p.mesh.rotation.y = Math.sin(t * 5 + p.phase) * 0.3; });

  // rowboat
  boat.position.y = Math.sin(t * 1.35 + 2.5) * 0.14 - 0.02;
  boat.rotation.z = Math.sin(t * 0.85 + 1) * 0.06;
  boat.rotation.x = Math.sin(t * 0.65) * 0.05;

  // clouds
  clouds.forEach(c => {
    c.position.x += dt * c.userData.speed;
    if (c.position.x > 34) c.position.x = -34;
  });

  // gulls
  gulls.forEach(gl => {
    const th = t * gl.speed + gl.phase;
    const px = 2 + gl.r * Math.cos(th), pz = 1.5 + gl.r * Math.sin(th);
    const nx = 2 + gl.r * Math.cos(th + 0.12), nz = 1.5 + gl.r * Math.sin(th + 0.12);
    const py = gl.h + Math.sin(t * 1.25 + gl.phase) * 0.6;
    gl.g.position.set(px, py, pz);
    gl.g.lookAt(nx, py, nz);
    const flap = Math.sin(t * 7 + gl.phase) * 0.55;
    gl.wingR.rotation.z = flap;
    gl.wingL.rotation.z = -flap;
  });

  // lamp flicker
  lampMat.emissiveIntensity = 1.25 + Math.sin(t * 3.1) * 0.22;

  controls.update();
  renderer.render(scene, camera);
}
animate();

// ---------- resize ----------
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
</script>
</body>
</html>
```

Notes:
- Works by opening the file in Chrome; the only network dependency is the Three.js CDN (jsdelivr) on first load. Everything else (ocean, ship, dock, sky gradient) is generated procedurally.
- Drag to orbit, scroll to zoom, right-drag to pan. The ship bobs, waves move, flags flutter, clouds drift, and gulls circle the harbor.
- If you want it fully offline, I can inline the Three.js module into the file — it's ~1.2 MB, but it removes the CDN requirement.