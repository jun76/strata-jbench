Here's a complete, single-file 3D voxel art scene of a sailing ship calling at a harbor — island, pier, warehouse, cranes, lighthouse (with rotating beam), buoys, seagulls, drifting clouds, an animated wave grid, and a bobbing ship. Save it as `harbor.html` and open it in Chrome (needs an internet connection the first time to load Three.js from a CDN).

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Harbor · Sailing Ship — Voxel Scene</title>
<style>
  html, body { margin:0; height:100%; overflow:hidden; font-family: system-ui, -apple-system, "Segoe UI", sans-serif; }
  #app { position: fixed; inset: 0; }
  #ui {
    position: fixed; top: 14px; left: 14px; z-index: 10;
    background: rgba(12, 24, 36, 0.55); color: #eaf6ff;
    padding: 12px 16px; border-radius: 12px; backdrop-filter: blur(6px);
    max-width: 300px; pointer-events: none;
  }
  #ui h1 { font-size: 15px; margin: 0 0 4px; letter-spacing: .4px; font-weight: 650; }
  #ui p { font-size: 12px; margin: 0 0 10px; opacity: .85; }
  #ui button {
    pointer-events: auto; background: #ffb84d; border: 0; color: #24303a;
    padding: 6px 10px; border-radius: 8px; font-weight: 600; cursor: pointer; margin-right: 6px;
  }
  #ui button:hover { background: #ffc76f; }
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
<div id="app"></div>
<div id="ui">
  <h1>Harbor · Sailing Ship</h1>
  <p>Drag to orbit · scroll to zoom · right-drag to pan</p>
  <button id="rotBtn">⏸ Auto-rotate</button><button id="resetBtn">Reset view</button>
</div>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* ---------- renderer / scene / camera ---------- */
const app = document.getElementById('app');
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.08;
renderer.outputColorSpace = THREE.SRGBColorSpace;
app.appendChild(renderer.domElement);

const scene = new THREE.Scene();

// gradient sky backdrop
const skyCanvas = document.createElement('canvas');
skyCanvas.width = 4; skyCanvas.height = 512;
const sg = skyCanvas.getContext('2d');
const grad = sg.createLinearGradient(0, 0, 0, 512);
grad.addColorStop(0.00, '#3f8fd2');
grad.addColorStop(0.45, '#7cc3e8');
grad.addColorStop(0.78, '#cfe9f6');
grad.addColorStop(1.00, '#eaf8ff');
sg.fillStyle = grad; sg.fillRect(0, 0, 4, 512);
const skyTex = new THREE.CanvasTexture(skyCanvas);
skyTex.colorSpace = THREE.SRGBColorSpace;
scene.background = skyTex;
scene.fog = new THREE.Fog(0xd6ecf7, 55, 120);

const camera = new THREE.PerspectiveCamera(45, innerWidth / innerHeight, 0.1, 300);
camera.position.set(24, 17, 28);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 2.5, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.minDistance = 12;
controls.maxDistance = 70;
controls.maxPolarAngle = 1.45;
controls.autoRotate = true;
controls.autoRotateSpeed = 0.7;

/* ---------- lights ---------- */
scene.add(new THREE.HemisphereLight(0xbfe3ff, 0x5a7d4f, 0.85));
const sun = new THREE.DirectionalLight(0xfff2d8, 1.9);
sun.position.set(20, 26, 12);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -36; sun.shadow.camera.right = 36;
sun.shadow.camera.top = 36; sun.shadow.camera.bottom = -36;
sun.shadow.camera.near = 2; sun.shadow.camera.far = 90;
sun.shadow.bias = -0.0005;
scene.add(sun);

/* ---------- shared box helpers ---------- */
const unitBox = new THREE.BoxGeometry(1, 1, 1);
const matCache = new Map();
function matFor(color, rough = 0.8) {
  const key = color + '|' + rough;
  if (!matCache.has(key)) matCache.set(key, new THREE.MeshStandardMaterial({ color, roughness: rough, metalness: 0.03 }));
  return matCache.get(key);
}
function emissiveMat(color, intensity = 1.4) {
  const key = 'e|' + color;
  if (!matCache.has(key)) matCache.set(key, new THREE.MeshStandardMaterial({ color: '#fff2c0', emissive: color, emissiveIntensity: intensity, roughness: 0.5 }));
  return matCache.get(key);
}
function box(sx, sy, sz, color, rx = 0, ry = 0, rz = 0, mat = null) {
  const mesh = new THREE.Mesh(unitBox, mat || matFor(color));
  mesh.scale.set(sx, sy, sz);
  mesh.rotation.set(rx, ry, rz);
  mesh.castShadow = true; mesh.receiveShadow = true;
  return mesh;
}
function place(m, x, y, z) { m.position.set(x, y, z); return m; }

/* ---------- static voxel world (instanced) ---------- */
const voxelList = [];
function v(x, y, z, sx, sy, sz, color) { voxelList.push({ x, y, z, sx, sy, sz, color }); }

// island: cliff, sand, grass
v(0, -1.55, -1, 34, 3, 20, '#6f5a44');
v(0, 0.45, -1, 34, 0.9, 20, '#e3cd92');
v(0, 1.18, -2, 30, 0.55, 15.5, '#5fa860');

// grass tufts & sand specks (deterministic scatter)
for (let i = 0; i < 26; i++) {
  const fx = Math.abs(Math.sin(i * 91.7));
  const fz = Math.abs(Math.sin(i * 47.3 + 2));
  v(-14 + fx * 28, 1.5, -9 + fz * 14, 0.55, 0.24, 0.55, '#4c8a47');
}
for (let i = 0; i < 20; i++) {
  const fx = Math.abs(Math.sin(i * 127.1));
  const fz = Math.abs(Math.sin(i * 311.7));
  v(-15 + fx * 30, 0.95, 6.8 + fz * 2.0, 0.5, 0.18, 0.5, '#cdb377');
}
// cliff rocks
v(-17.3, -0.4, 2, 1.2, 1.3, 1.5, '#7d7468');
v(17.3, -0.3, -2, 1.3, 1.2, 1.4, '#6f665c');
v(2, -0.5, 9.3, 1.6, 1.0, 1.0, '#7d7468');
v(-6, -0.5, -11.3, 1.5, 1.1, 1.1, '#6f665c');

// dock planks + posts + lamps + crates
for (let i = 0; i < 17; i++) {
  const r = Math.sin(i * 45.7) * 0.5 + 0.5;
  v(-8 + i, 1.0, 8.9, 0.94, 0.4, 3.4, r > 0.5 ? '#a9743f' : '#9a683a');
}
for (const px of [-8, -2.7, 2.7, 8]) v(px, -0.35, 10.25, 0.55, 2.5, 0.55, '#7a5433');
for (const px of [-7.4, 7.4]) v(px, 1.9, 7.75, 0.22, 1.6, 0.22, '#3c3c40');
v(-5.6, 1.5, 8.4, 1.0, 0.9, 1.0, '#b5854c');
v(-4.3, 1.55, 9.4, 0.72, 0.85, 0.72, '#8a5a33');

// sand rocks
v(13.2, 1.0, 7.6, 1.1, 0.7, 1.0, '#8b8578');
v(-13.8, 1.0, 7.9, 0.9, 0.6, 0.9, '#7d7468');
v(1.8, 0.95, 8.1, 0.7, 0.5, 0.7, '#8b8578');

// lighthouse islet rocks + tower (banded)
v(17, 0.55, 13, 4.6, 1.5, 4.0, '#7d7d7d');
v(16.1, 1.35, 12.3, 2.0, 1.1, 2.0, '#6d6d6d');
v(18.2, 1.25, 13.8, 1.7, 1.0, 1.7, '#858585');
v(17, 1.95, 13, 2.3, 1.1, 2.3, '#e8e2d4');
[3.1, 4.2, 5.3, 6.4, 7.5].forEach((y, i) =>
  v(17, y, 13, 1.75, 1.05, 1.75, i % 2 === 0 ? '#e8e2d4' : '#c94f3d'));
v(17, 8.5, 13, 1.2, 0.85, 1.2, '#3a3a3a');
v(17, 9.15, 13, 1.4, 0.4, 1.4, '#c94f3d');
v(17, 9.5, 13, 0.95, 0.4, 0.95, '#c94f3d');
v(17, 9.9, 13, 0.28, 0.5, 0.28, '#e8c25a');

const instGeo = new THREE.BoxGeometry(1, 1, 1);
const instMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.85, metalness: 0.02 });
const inst = new THREE.InstancedMesh(instGeo, instMat, voxelList.length);
const _m = new THREE.Matrix4(), _q = new THREE.Quaternion(), _p = new THREE.Vector3(),
      _s = new THREE.Vector3(), _c = new THREE.Color();
voxelList.forEach((b, i) => {
  _p.set(b.x, b.y, b.z); _s.set(b.sx, b.sy, b.sz); _q.identity();
  _m.compose(_p, _q, _s);
  inst.setMatrixAt(i, _m);
  _c.set(b.color).offsetHSL(0, (Math.random() - 0.5) * 0.02, (Math.random() - 0.5) * 0.05);
  inst.setColorAt(i, _c);
});
inst.castShadow = true; inst.receiveShadow = true; inst.frustumCulled = false;
if (inst.instanceColor) inst.instanceColor.needsUpdate = true;
scene.add(inst);

/* ---------- animated voxel water ---------- */
const waterTiles = [];
for (let x = -24; x <= 24; x += 2)
  for (let z = -18; z <= 26; z += 2) {
    if (Math.abs(x) < 17 && z > -11.5 && z < 8.9) continue; // island footprint
    waterTiles.push({ x, z });
  }
const waterGeo = new THREE.BoxGeometry(1.96, 1, 1.96);
const waterMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.32, metalness: 0.18 });
const water = new THREE.InstancedMesh(waterGeo, waterMat, waterTiles.length);
waterTiles.forEach((t, i) => {
  const fr = Math.abs(Math.sin(t.x * 12.9898 + t.z * 78.233));
  water.setColorAt(i, _c.set('#2f7fb8').offsetHSL(0, 0.02 * (fr - 0.5), 0.05 * (fr - 0.5)));
});
water.receiveShadow = true; water.frustumCulled = false;
if (water.instanceColor) water.instanceColor.needsUpdate = true;
scene.add(water);
const _wm = new THREE.Matrix4(), _wq = new THREE.Quaternion(), _wp = new THREE.Vector3(), _ws = new THREE.Vector3(1, 1, 1);

/* ---------- sailing ship ---------- */
const ship = new THREE.Group();
for (let i = -5; i <= 5; i++) {
  const w = 3.2 * Math.sqrt(Math.max(0.18, 1 - (i / 5.8) ** 2));
  ship.add(place(box(0.96, 0.72, Math.max(0.8, w - 0.7), '#5f2d22'), i, -0.72, 0));
  ship.add(place(box(0.96, 0.78, w, '#7a3b2e'), i, -0.02, 0));
  ship.add(place(box(0.96, 0.5, w + 0.28, '#d9a75f'), i, 0.66, 0));
  ship.add(place(box(0.96, 0.3, w - 0.35, '#c9a06b'), i, 1.0, 0));
}
ship.add(place(box(0.3, 1.1, 0.3, '#d9a75f'), 5.1, 1.75, 0));
ship.add(place(box(2.0, 1.05, 2.3, '#e8dcc0'), -3.4, 1.78, 0));
ship.add(place(box(2.3, 0.28, 2.6, '#7a3b2e'), -3.4, 2.42, 0));
const winMat = emissiveMat('#ffd76a');
ship.add(place(box(0.5, 0.5, 0.08, '#000', 0, 0, 0, winMat), -2.85, 1.85, 1.17));
ship.add(place(box(0.5, 0.5, 0.08, '#000', 0, 0, 0, winMat), -3.85, 1.85, 1.17));
ship.add(place(box(0.34, 7.6, 0.34, '#6b4a2a'), 0.2, 4.8, 0));
ship.add(place(box(0.22, 1.7, 0.22, '#6b4a2a'), 0.2, 9.3, 0));
ship.add(place(box(3.7, 0.2, 0.2, '#6b4a2a'), 0.35, 2.35, 0));
ship.add(place(box(3.1, 3.3, 0.16, '#000', 0, 0, 0, matFor('#f3ead6', 0.9)), 0.35, 4.1, 0.24));
const jib = box(1.4, 2.9, 0.12, '#000', 0, 0, 0.5, matFor('#e9dfc8', 0.9));
place(jib, 3.85, 3.75, 0.05); ship.add(jib);
ship.add(place(box(1.15, 0.42, 0.1, '#d64545'), 0.78, 9.95, 0));
ship.add(place(box(0.28, 0.42, 0.11, '#f3ead6'), 1.26, 9.95, 0));
const bowsprit = box(3.1, 0.15, 0.15, '#6b4a2a', 0, 0, 0.28);
place(bowsprit, 6.3, 2.3, 0); ship.add(bowsprit);
ship.add(place(box(0.75, 0.75, 0.75, '#b5854c'), -1.7, 1.5, -0.6));
ship.add(place(box(0.6, 0.7, 0.6, '#8a5a33'), 1.9, 1.5, 0.7));
ship.position.set(0, 0.62, 13.2);
scene.add(ship);

/* ---------- mooring lines ---------- */
function line(from, to, thick, color) {
  const dir = new THREE.Vector3().subVectors(to, from);
  const len = dir.length();
  const m = new THREE.Mesh(unitBox, matFor(color, 0.6));
  m.scale.set(thick, thick, len);
  m.position.copy(from).addScaledVector(dir, 0.5);
  m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 0, 1), dir.normalize());
  m.castShadow = true;
  return m;
}
scene.add(line(new THREE.Vector3(-3.2, 1.15, 10.55), new THREE.Vector3(-3.2, 1.45, 11.7), 0.09, '#4a3826'));
scene.add(line(new THREE.Vector3(3.2, 1.15, 10.55), new THREE.Vector3(3.2, 1.45, 11.7), 0.09, '#4a3826'));

/* ---------- warehouse / houses / palms ---------- */
const TOP = 1.45;
function buildWarehouse(x, z) {
  const g = new THREE.Group();
  g.add(place(box(5, 3, 4, '#a5573c'), x, TOP + 1.5, z));
  g.add(place(box(5.6, 0.28, 2.5, '#6b3f2e', -0.55, 0, 0), x, TOP + 3.55, z - 1.0));
  g.add(place(box(5.6, 0.28, 2.5, '#6b3f2e', 0.55, 0, 0), x, TOP + 3.55, z + 1.0));
  g.add(place(box(5.7, 0.3, 0.55, '#5a3524'), x, TOP + 4.15, z));
  g.add(place(box(1.15, 1.75, 0.1, '#3d2a1e'), x, TOP + 0.9, z + 2.06));
  g.add(place(box(0.95, 0.95, 0.09, '#000', 0, 0, 0, emissiveMat('#ffd76a')), x - 1.6, TOP + 2.0, z + 2.06));
  g.add(place(box(0.95, 0.95, 0.09, '#000', 0, 0, 0, emissiveMat('#ffd76a')), x + 1.6, TOP + 2.0, z + 2.06));
  scene.add(g);
}
function buildHouse(x, z, color, rotY) {
  const g = new THREE.Group();
  g.rotation.y = rotY;
  g.add(place(box(3, 2.3, 2.6, color), 0, TOP + 1.15, 0));
  g.add(place(box(3.5, 0.26, 1.7, '#6b3f2e', -0.6, 0, 0), 0, TOP + 2.85, -0.95));
  g.add(place(box(3.5, 0.26, 1.7, '#6b3f2e', 0.6, 0, 0), 0, TOP + 2.85, 0.95));
  g.add(place(box(3.6, 0.28, 0.5, '#5a3524'), 0, TOP + 3.35, 0));
  g.add(place(box(0.85, 1.5, 0.09, '#3d2a1e'), 0, TOP + 0.75, 1.31));
  g.add(place(box(0.55, 0.55, 0.08, '#000', 0, 0, 0, emissiveMat('#ffd76a')), -0.9, TOP + 1.4, 1.31));
  g.add(place(box(0.55, 0.55, 0.08, '#000', 0, 0, 0, emissiveMat('#ffd76a')), 0.9, TOP + 1.4, 1.31));
  g.position.set(x, 0, z); scene.add(g);
}
function buildPalm(x, z, lean) {
  const g = new THREE.Group();
  for (let i = 0; i < 4; i++)
    g.add(place(box(0.34, 0.95, 0.34, '#7a5433'), lean * i * 0.22, TOP + 0.45 + i * 0.88, 0));
  const topX = lean * 3 * 0.22;
  for (let i = 0; i < 6; i++) {
    const lg = new THREE.Group();
    lg.position.set(topX, TOP + 3.85, 0);
    lg.rotation.y = i * (Math.PI / 3);
    const leaf = box(2.4, 0.16, 0.72, '#3f7d3a');
    leaf.position.set(1.15, 0, 0); leaf.rotation.z = -0.34;
    lg.add(leaf); g.add(lg);
  }
  g.add(place(box(0.32, 0.32, 0.32, '#6b4a2a'), topX + 0.25, TOP + 3.55, 0.2));
  g.add(place(box(0.3, 0.3, 0.3, '#6b4a2a'), topX - 0.2, TOP + 3.5, -0.2));
  g.position.set(x, 0, z); scene.add(g);
}
buildWarehouse(-8.5, 2.8);
buildHouse(7.5, 3.4, '#e8dcc0', 0.12);
buildHouse(11.8, -1.5, '#d98f6a', -0.15);
buildPalm(-12.5, -6, 0.55);
buildPalm(12.5, -6, -0.5);

/* ---------- dock crane (swaying crate) ---------- */
const crane = new THREE.Group();
crane.position.set(5.2, 0, 8.2);
crane.add(place(box(0.55, 4.6, 0.55, '#c94f3d'), 0, 3.55, 0));
crane.add(place(box(0.45, 0.4, 5.2, '#c94f3d'), 0, 5.85, 1.4));
crane.add(place(box(0.75, 0.75, 0.75, '#3a3a3a'), 0, 5.6, -1.15));
const hangPivot = new THREE.Group();
hangPivot.position.set(0, 5.75, 3.9);
hangPivot.add(place(box(0.09, 2.5, 0.09, '#2b2b2b'), 0, -1.25, 0));
hangPivot.add(place(box(0.34, 0.34, 0.34, '#2b2b2b'), 0, -2.55, 0));
hangPivot.add(place(box(0.9, 0.9, 0.9, '#b5854c'), 0, -3.15, 0));
crane.add(hangPivot);
scene.add(crane);

/* ---------- lighthouse beam + glow ---------- */
const lanternWin = box(1.26, 0.5, 1.26, '#000', 0, 0, 0, emissiveMat('#ffe27a', 1.6));
lanternWin.castShadow = false;
place(lanternWin, 17, 8.5, 13); scene.add(lanternWin);

const beamPivot = new THREE.Group();
beamPivot.position.set(17, 8.5, 13);
const beamGeo = new THREE.ConeGeometry(2.4, 11, 20, 1, true);
beamGeo.translate(0, -5.5, 0);
beamGeo.rotateX(-Math.PI / 2); // extends along +z
const beam = new THREE.Mesh(beamGeo, new THREE.MeshBasicMaterial({
  color: 0xfff0b0, transparent: true, opacity: 0.16,
  side: THREE.DoubleSide, depthWrite: false, blending: THREE.AdditiveBlending
}));
beamPivot.add(beam);
scene.add(beamPivot);
const lampLight = new THREE.PointLight(0xffe2a0, 45, 26, 2);
lampLight.position.set(17, 8.6, 13); scene.add(lampLight);

/* ---------- dock lamp glows ---------- */
for (const px of [-7.4, 7.4]) {
  const head = box(0.42, 0.42, 0.42, '#000', 0, 0, 0, emissiveMat('#ffd76a', 1.5));
  head.castShadow = false;
  place(head, px, 2.78, 7.75); scene.add(head);
  const l = new THREE.PointLight(0xffd76a, 5, 7, 2);
  l.position.set(px, 2.8, 7.75); scene.add(l);
}

/* ---------- buoys ---------- */
const buoys = [];
function buildBuoy(x, z, phase) {
  const g = new THREE.Group();
  g.add(place(box(0.55, 0.75, 0.55, '#d64545'), 0, 0.2, 0));
  g.add(place(box(0.36, 0.34, 0.36, '#f3ead6'), 0, 0.72, 0));
  g.add(place(box(0.14, 0.5, 0.14, '#3a3a3a'), 0, 1.05, 0));
  g.position.set(x, 0, z); scene.add(g);
  buoys.push({ g, phase });
}
buildBuoy(7.5, 15.8, 0);
buildBuoy(-8.5, 15.2, 2);

/* ---------- distant sailboat ---------- */
const distantBoat = new THREE.Group();
distantBoat.add(place(box(1.7, 0.42, 0.75, '#8a5a33'), 0, 0.25, 0));
distantBoat.add(place(box(0.12, 2.3, 0.12, '#5a3f24'), 0, 1.6, 0));
distantBoat.add(place(box(1.15, 1.55, 0.09, '#f3ead6'), 0.12, 1.75, 0));
distantBoat.position.set(-30, 0, -15);
scene.add(distantBoat);

/* ---------- clouds ---------- */
const clouds = [];
function buildCloud(x, y, z, s) {
  const g = new THREE.Group();
  const m = matFor('#ffffff', 1);
  const parts = [[0, 0, 0, 3.2, 1.0, 1.7], [1.9, -0.15, 0.2, 1.7, 0.8, 1.3], [-1.9, -0.2, -0.2, 1.6, 0.75, 1.2], [0.6, 0.62, 0, 1.5, 0.7, 1.1]];
  parts.forEach(p => {
    const b = box(p[3], p[4], p[5], '#000', 0, 0, 0, m);
    b.castShadow = false;
    b.position.set(p[0], p[1], p[2]);
    g.add(b);
  });
  g.position.set(x, y, z); g.scale.setScalar(s);
  g.userData.speed = 0.35 + Math.random() * 0.35;
  scene.add(g); clouds.push(g);
}
buildCloud(-16, 13.5, -8, 1.2); buildCloud(4, 15.5, -13, 1.5); buildCloud(16, 12.5, -4, 0.9);
buildCloud(-8, 14.5, 9, 1.1); buildCloud(24, 13, 7, 1.0); buildCloud(-24, 12.5, 4, 0.85);

/* ---------- seagulls ---------- */
const gulls = [];
function buildGull(r, h, speed, phase, cx, cz) {
  const g = new THREE.Group();
  const m = matFor('#ffffff', 0.9);
  const body = box(0.28, 0.24, 0.75, '#000', 0, 0, 0, m); g.add(body);
  const head = box(0.26, 0.26, 0.3, '#000', 0, 0, 0, m); head.position.set(0, 0.12, 0.5); g.add(head);
  const beak = box(0.1, 0.1, 0.25, '#e8a13a'); beak.position.set(0, 0.05, 0.78); g.add(beak);
  const wingR = new THREE.Group();
  const wr = box(1.15, 0.1, 0.42, '#000', 0, 0, 0, m); wr.position.set(0.55, 0.05, 0); wingR.add(wr);
  const wingL = new THREE.Group();
  const wl = box(1.15, 0.1, 0.42, '#000', 0, 0, 0, m); wl.position.set(-0.55, 0.05, 0); wingL.add(wl);
  g.add(wingR); g.add(wingL);
  g.traverse(o => { if (o.isMesh) o.castShadow = false; });
  scene.add(g);
  gulls.push({ g, wingR, wingL, r, h, speed, phase, cx, cz });
}
buildGull(5, 8.6, 0.55, 0, 0, 11);
buildGull(7, 10.2, -0.42, 2, 0, 11);
buildGull(9, 9.4, 0.7, 4, 0, 11);

/* ---------- sun voxel ---------- */
const sunBox = box(2.6, 2.6, 2.6, '#000', 0, 0, 0, new THREE.MeshBasicMaterial({ color: 0xffe27a }));
sunBox.castShadow = false; sunBox.receiveShadow = false;
sunBox.position.set(26, 24, 14); scene.add(sunBox);
const halo = box(3.6, 3.6, 3.6, '#000', 0, 0, 0, new THREE.MeshBasicMaterial({ color: 0xffe27a, transparent: true, opacity: 0.22 }));
halo.castShadow = false; halo.receiveShadow = false;
halo.position.copy(sunBox.position); scene.add(halo);

/* ---------- UI ---------- */
const rotBtn = document.getElementById('rotBtn');
let auto = true;
rotBtn.addEventListener('click', () => {
  auto = !auto; controls.autoRotate = auto;
  rotBtn.textContent = auto ? '⏸ Auto-rotate' : '▶ Auto-rotate';
});
controls.addEventListener('start', () => {
  if (auto) { auto = false; controls.autoRotate = false; rotBtn.textContent = '▶ Auto-rotate'; }
});
document.getElementById('resetBtn').addEventListener('click', () => {
  camera.position.set(24, 17, 28);
  controls.target.set(0, 2.5, 0);
  controls.update();
});

/* ---------- loop ---------- */
const clock = new THREE.Clock();
function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  // water waves
  for (let i = 0; i < waterTiles.length; i++) {
    const tile = waterTiles[i];
    const y = -0.42 + Math.sin(tile.x * 0.42 + t * 1.5) * 0.2 + Math.sin(tile.z * 0.5 + t * 1.15) * 0.16;
    _wp.set(tile.x, y, tile.z);
    _wm.compose(_wp, _wq, _ws);
    water.setMatrixAt(i, _wm);
  }
  water.instanceMatrix.needsUpdate = true;

  // ship bobbing
  ship.position.y = 0.62 + Math.sin(t * 1.15) * 0.13;
  ship.rotation.x = Math.sin(t * 0.75 + 0.5) * 0.028;
  ship.rotation.z = Math.sin(t * 0.95) * 0.02;

  // lighthouse beam
  beamPivot.rotation.y = t * 0.65;

  // crane crate sway
  hangPivot.rotation.z = Math.sin(t * 0.9) * 0.14;
  hangPivot.rotation.x = Math.sin(t * 0.6 + 1) * 0.08;

  // buoys
  for (const b of buoys) {
    b.g.position.y = Math.sin(t * 1.6 + b.phase) * 0.18 - 0.1;
    b.g.rotation.z = Math.sin(t * 1.2 + b.phase) * 0.12;
  }

  // distant boat
  distantBoat.position.x += dt * 1.5;
  if (distantBoat.position.x > 34) distantBoat.position.x = -34;
  distantBoat.position.y = Math.sin(t * 1.1) * 0.1;
  distantBoat.rotation.z = Math.sin(t * 0.9) * 0.04;

  // clouds drift
  for (const c of clouds) {
    c.position.x += c.userData.speed * dt;
    if (c.position.x > 34) c.position.x = -34;
  }

  // gulls
  for (let i = 0; i < gulls.length; i++) {
    const gl = gulls[i];
    const a = t * gl.speed + gl.phase;
    const x = gl.cx + Math.cos(a) * gl.r;
    const z = gl.cz + Math.sin(a) * gl.r;
    gl.g.position.set(x, gl.h + Math.sin(t * 1.3 + i) * 0.5, z);
    gl.g.rotation.y = Math.atan2(-Math.sin(a) * gl.speed, Math.cos(a) * gl.speed);
    const flap = Math.sin(t * 9 + i * 2) * 0.55;
    gl.wingR.rotation.z = flap; gl.wingL.rotation.z = -flap;
  }

  controls.update();
  renderer.render(scene, camera);
}
animate();

/* ---------- resize ---------- */
addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
</script>
</body>
</html>
```

**What's in the scene**

- **The sailing ship** (center-right): voxel hull with a gold trim, mast, main sail and jib, bowsprit, stern cabin with lit windows, red pennant — it gently bobs, rolls, and pitches, moored to the dock by rope lines.
- **The harbor**: grass-topped island with sand beach, warehouse with gable roof, two houses, palms, lamp-lit dock, a crane swinging a crate over the water, floating buoys, and a distant sailboat crossing behind.
- **The lighthouse** on a rocky islet with alternating red/white bands and a rotating volumetric light beam plus a warm point light.
- **Atmosphere**: animated voxel water grid, drifting clouds, circling flapping seagulls, a voxel sun, gradient sky and soft fog.

**Controls**: drag to orbit, scroll to zoom, right-drag to pan. Auto-rotation starts on and pauses as soon as you grab the scene (the button toggles it back on).

Tips for tweaking: change `controls.autoRotateSpeed` for the spin rate, the water grid step/height for wave feel, or the beam speed (`beamPivot.rotation.y = t * 0.65`) — and everything is plain boxes, so you can easily add your own voxel details.