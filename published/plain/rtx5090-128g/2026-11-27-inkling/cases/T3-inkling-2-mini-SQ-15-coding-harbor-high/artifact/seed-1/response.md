Here's a complete single-file voxel scene — a sailing ship at a harbor with an animated voxel sea, a pier, warehouse, lighthouse, gulls, drifting clouds, and a bobbing ship. Save it as `harbor.html` and open it in Chrome.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Harbor Call — Voxel Sailing Ship</title>
<style>
  html, body { margin: 0; height: 100%; overflow: hidden; background: #d8ecf3; }
  canvas { display: block; }
  #vignette { position: fixed; inset: 0; z-index: 5; pointer-events: none;
    background: radial-gradient(ellipse at 50% 45%, transparent 58%, rgba(8,16,26,0.30) 100%); }
  #hud { position: fixed; top: 20px; left: 20px; z-index: 10; pointer-events: none;
    background: rgba(16,26,36,0.62); border: 1px solid rgba(255,255,255,0.16); border-radius: 14px;
    padding: 16px 20px; color: #f6f1e6; font-family: Georgia, 'Times New Roman', serif;
    backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
    box-shadow: 0 8px 30px rgba(10,20,30,0.25); }
  #hud h1 { margin: 0 0 6px; font-size: 21px; font-weight: 600; letter-spacing: 0.05em; }
  #hud .sub { margin: 0 0 10px; font-size: 12.5px; color: #d8cfb9; letter-spacing: 0.03em; }
  #hud .hint { margin: 0; font-size: 11.5px; color: #a9c4d4; letter-spacing: 0.04em; }
  #hud .hint b { color: #f0e9d8; font-weight: 600; }
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
<div id="vignette"></div>
<div id="hud">
  <h1>⚓ Harbor Call</h1>
  <p class="sub">A sailing ship calling at the harbor — single-file voxel scene</p>
  <p class="hint"><b>Drag</b> to orbit &nbsp;·&nbsp; <b>Scroll</b> to zoom &nbsp;·&nbsp; <b>Right-drag</b> to pan</p>
</div>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* ---------------- seeded random ---------------- */
let seed = 20240613;
function rand() { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; }
function rInt(a, b) { return Math.floor(rand() * (b - a + 1)) + a; }
function pick(arr) { return arr[Math.floor(rand() * arr.length)]; }

/* ---------------- renderer / scene ---------------- */
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.1;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xdceef5, 55, 125);

const camera = new THREE.PerspectiveCamera(42, window.innerWidth / window.innerHeight, 0.1, 400);
camera.position.set(17, 12, 21);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 2.5, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.minDistance = 9;
controls.maxDistance = 55;
controls.maxPolarAngle = Math.PI * 0.49;
controls.minPolarAngle = Math.PI * 0.08;
controls.autoRotate = true;
controls.autoRotateSpeed = 0.35;
let idleTimer = null;
controls.addEventListener('start', () => { controls.autoRotate = false; clearTimeout(idleTimer); });
controls.addEventListener('end', () => { clearTimeout(idleTimer); idleTimer = setTimeout(() => { controls.autoRotate = true; }, 5000); });
controls.update();

/* ---------------- sky dome ---------------- */
const sky = new THREE.Mesh(
  new THREE.SphereGeometry(160, 32, 20),
  new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false, fog: false,
    uniforms: { top: { value: new THREE.Color(0x4f9fd0) }, bottom: { value: new THREE.Color(0xeaf6f4) } },
    vertexShader: `varying vec3 vP; void main() { vP = position; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
    fragmentShader: `varying vec3 vP; uniform vec3 top; uniform vec3 bottom;
      void main() { float h = normalize(vP).y; float t = clamp(h * 1.5 + 0.18, 0.0, 1.0); gl_FragColor = vec4(mix(bottom, top, t), 1.0); }`
  })
);
scene.add(sky);

/* ---------------- lights ---------------- */
scene.add(new THREE.HemisphereLight(0xcfe8f2, 0x8a6f4d, 0.9));
const sunLight = new THREE.DirectionalLight(0xfff0d6, 1.4);
sunLight.position.set(-22, 26, -16);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
sunLight.shadow.camera.left = -42; sunLight.shadow.camera.right = 42;
sunLight.shadow.camera.top = 42; sunLight.shadow.camera.bottom = -42;
sunLight.shadow.camera.near = 1; sunLight.shadow.camera.far = 90;
sunLight.shadow.bias = -0.0005;
sunLight.shadow.normalBias = 0.25;
scene.add(sunLight);

/* ---------------- voxel builder ---------------- */
const boxGeo = new THREE.BoxGeometry(1, 1, 1);
function voxelMesh(voxels, opts = {}) {
  const cast = opts.cast !== false;
  const receive = opts.receive !== false;
  const byColor = new Map();
  for (const v of voxels) {
    if (!byColor.has(v.c)) byColor.set(v.c, []);
    byColor.get(v.c).push(v);
  }
  const group = new THREE.Group();
  const m = new THREE.Matrix4();
  for (const [c, list] of byColor) {
    const mat = new THREE.MeshStandardMaterial({ color: new THREE.Color(c), roughness: 0.92, metalness: 0 });
    const im = new THREE.InstancedMesh(boxGeo, mat, list.length);
    list.forEach((v, i) => { m.makeTranslation(v.x, v.y, v.z); im.setMatrixAt(i, m); });
    im.castShadow = cast;
    im.receiveShadow = receive;
    group.add(im);
  }
  return group;
}

/* ---------------- water (animated voxels) ---------------- */
const WATER_X0 = -8, WATER_X1 = 30, WATER_Z0 = -30, WATER_Z1 = 30;
const waterCells = [];
for (let x = WATER_X0; x <= WATER_X1; x++)
  for (let z = WATER_Z0; z <= WATER_Z1; z++) waterCells.push({ x, z });
const waterMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.5, metalness: 0.08 });
const water = new THREE.InstancedMesh(boxGeo, waterMat, waterCells.length);
water.receiveShadow = true;
water.castShadow = false;
{
  const shallow = new THREE.Color(0x58a9c9), deep = new THREE.Color(0x235f86), foam = new THREE.Color(0xd8ece2);
  const m = new THREE.Matrix4(); const col = new THREE.Color();
  waterCells.forEach((c, i) => {
    const t = (c.x - WATER_X0) / (WATER_X1 - WATER_X0);
    col.copy(shallow).lerp(deep, Math.min(1, t * 1.35)).multiplyScalar(0.9 + rand() * 0.2);
    if (c.x <= -6) col.copy(foam).multiplyScalar(0.92 + rand() * 0.12);
    water.setColorAt(i, col);
    m.makeTranslation(c.x, -0.12, c.z);
    water.setMatrixAt(i, m);
  });
  water.instanceMatrix.needsUpdate = true;
  if (water.instanceColor) water.instanceColor.needsUpdate = true;
}
scene.add(water);

const wm = new THREE.Matrix4();
function updateWater(t) {
  for (let i = 0; i < waterCells.length; i++) {
    const c = waterCells[i];
    const y = -0.15 + Math.sin(t * 1.25 + c.x * 0.38 + c.z * 0.31) * 0.22
                  + Math.sin(t * 2.05 + c.z * 0.6) * 0.06;
    wm.makeTranslation(c.x, y, c.z);
    water.setMatrixAt(i, wm);
  }
  water.instanceMatrix.needsUpdate = true;
}

/* ---------------- quay ---------------- */
const quay = [];
for (let x = -30; x <= -9; x++)
  for (let z = -18; z <= 18; z++)
    quay.push({ x, y: 1, z, c: pick(['#b7b2a6', '#aca79b', '#c2bdb1', '#a09b8f']) });
for (let z = -18; z <= 18; z++)
  for (const y of [0, -1])
    quay.push({ x: -9, y, z, c: pick(['#8d887d', '#958f84', '#838074']) });
for (let x = -30; x <= -10; x++)
  for (const y of [0, -1]) {
    quay.push({ x, y, z: -18, c: pick(['#8d887d', '#958f84', '#838074']) });
    quay.push({ x, y, z: 18, c: pick(['#8d887d', '#958f84', '#838074']) });
  }
scene.add(voxelMesh(quay));

/* ---------------- pier ---------------- */
const pier = [];
for (let x = -8; x <= -3; x++)
  for (let z = -2; z <= 2; z++)
    pier.push({ x, y: 1, z, c: (x % 2 === 0) ? '#8a623d' : '#7a5232' });
for (let z = -2; z <= 2; z++) pier.push({ x: -3, y: 0, z, c: '#6b4a2f' });
for (const px of [-3, -7])
  for (const pz of [-2, 2])
    for (let y = -2; y <= 0; y++) pier.push({ x: px, y, z: pz, c: '#3a2b20' });
for (const rx of [-8, -6, -4]) pier.push({ x: rx, y: 2, z: -2, c: '#4a3524' });
for (let x = -8; x <= -3; x++) pier.push({ x, y: 3, z: -2, c: '#4a3524' });
pier.push({ x: -3, y: 2, z: -1, c: '#2e2a26' });
pier.push({ x: -3, y: 2, z: 1, c: '#2e2a26' });
scene.add(voxelMesh(pier));

/* ---------------- warehouse ---------------- */
const wh = [];
for (let x = -17; x <= -12; x++)
  for (let z = -12; z <= -8; z++)
    for (let y = 2; y <= 3; y++) {
      let c = pick(['#e0d2ae', '#d8c8a2', '#e6dcc0']);
      if (x === -12 && z === -10) c = '#2b2320';
      else if (x === -12 && y === 3 && (z === -11 || z === -9)) c = '#2b2320';
      wh.push({ x, y, z, c });
    }
for (let x = -18; x <= -11; x++)
  for (let z = -13; z <= -7; z++) wh.push({ x, y: 4, z, c: '#a8432f' });
for (let x = -17; x <= -12; x++)
  for (let z = -12; z <= -8; z++) wh.push({ x, y: 5, z, c: '#8f3826' });
for (let x = -16; x <= -13; x++)
  for (let z = -11; z <= -9; z++) wh.push({ x, y: 6, z, c: '#7c301f' });
scene.add(voxelMesh(wh));

/* ---------------- crates & barrels ---------------- */
const crates = [];
for (let x = -10; x <= -9; x++) for (let z = 5; z <= 6; z++) for (let y = 2; y <= 3; y++) crates.push({ x, y, z, c: '#8a623d' });
for (let x = -10; x <= -9; x++) for (let z = 7; z <= 8; z++) for (let y = 2; y <= 3; y++) crates.push({ x, y, z, c: '#a97e4f' });
for (let x = -10; x <= -9; x++) for (let z = 5; z <= 6; z++) crates.push({ x, y: 4, z, c: '#7a5232' });
for (let i = 0; i < 2; i++) {
  crates.push({ x: -10 + i, y: 2, z: 10, c: '#5d3f28' });
  crates.push({ x: -10 + i, y: 3, z: 10, c: '#8a623d' });
}
scene.add(voxelMesh(crates));

/* ---------------- rope coil ---------------- */
const rope = [];
for (let dx = -2; dx <= 2; dx++)
  for (let dz = -2; dz <= 2; dz++)
    if (Math.abs(dx) === 2 || Math.abs(dz) === 2) rope.push({ x: -13 + dx, y: 2, z: dz, c: '#b89b6d' });
scene.add(voxelMesh(rope));

/* ---------------- lamp post ---------------- */
const lamp = [];
for (let y = 2; y <= 6; y++) lamp.push({ x: -12, y, z: -6, c: '#2e2a26' });
lamp.push({ x: -12, y: 7, z: -6, c: '#ffd95e' });
lamp.push({ x: -12, y: 8, z: -6, c: '#2e2a26' });
scene.add(voxelMesh(lamp));
const lampLight = new THREE.PointLight(0xffd98a, 6, 10, 2);
lampLight.position.set(-12, 7, -6);
scene.add(lampLight);

/* ---------------- sailing ship ---------------- */
function halfW(z) {
  const a = Math.abs(z);
  if (a >= 7) return 0;
  if (a >= 6) return 1;
  return 2;
}
function buildShip() {
  const v = [];
  for (let z = -7; z <= 7; z++) {
    const h = halfW(z);
    for (let x = -h; x <= h; x++) {
      if (h >= 1 && Math.abs(x) <= h - 1) v.push({ x, y: 0, z, c: '#2c211a' });
      v.push({ x, y: 1, z, c: '#3a2b20' });
      v.push({ x, y: 2, z, c: '#b0493a' });
      v.push({ x, y: 3, z, c: (z % 2 === 0) ? '#d3a866' : '#c1925a' });
    }
  }
  for (let z = -6; z <= -3; z++)
    for (let x = -2; x <= 2; x++) {
      let c4 = '#6b452a';
      if (z === -6 && x >= -1 && x <= 1) c4 = '#241d19';
      v.push({ x, y: 4, z, c: c4 });
      v.push({ x, y: 5, z, c: '#7d5a36' });
    }
  for (let x = -2; x <= 2; x++) v.push({ x, y: 6, z: -6, c: '#2f261f' });
  for (let z = -5; z <= -3; z++) {
    v.push({ x: -2, y: 6, z, c: '#2f261f' });
    v.push({ x: 2, y: 6, z, c: '#2f261f' });
  }
  v.push({ x: 0, y: 4, z: -7, c: '#3d2f26' });
  v.push({ x: 0, y: 5, z: -7, c: '#ffd95e' });
  for (let y = 3; y <= 11; y++) if (y !== 10) v.push({ x: 0, y, z: -2, c: '#4a3524' });
  for (let y = 3; y <= 9; y++) if (y !== 8) v.push({ x: 0, y, z: 4, c: '#4a3524' });
  for (let x = -3; x <= 3; x++) v.push({ x, y: 10, z: -2, c: '#5d422b' });
  for (let x = -2; x <= 2; x++) v.push({ x, y: 8, z: 4, c: '#5d422b' });
  const mainSail = [
    { y: 5, x0: -2, x1: 2, z: -1.8, c: '#f5ead6' },
    { y: 6, x0: -3, x1: 3, z: -1.65, c: '#f5ead6' },
    { y: 7, x0: -3, x1: 3, z: -1.65, c: '#c94f3f' },
    { y: 8, x0: -3, x1: 3, z: -1.65, c: '#f5ead6' },
    { y: 9, x0: -2, x1: 2, z: -1.8, c: '#f5ead6' },
  ];
  for (const r of mainSail) for (let x = r.x0; x <= r.x1; x++) v.push({ x, y: r.y, z: r.z, c: r.c });
  const foreSail = [
    { y: 5, x0: -2, x1: 2, z: 4.3, c: '#f5ead6' },
    { y: 6, x0: -2, x1: 2, z: 4.35, c: '#c94f3f' },
    { y: 7, x0: -1, x1: 1, z: 4.3, c: '#f5ead6' },
  ];
  for (const r of foreSail) for (let x = r.x0; x <= r.x1; x++) v.push({ x, y: r.y, z: r.z, c: r.c });
  v.push({ x: 0, y: 12, z: -3, c: '#d94f3d' });
  v.push({ x: 0, y: 12, z: -4, c: '#d94f3d' });
  v.push({ x: 0, y: 10, z: 5, c: '#d94f3d' });
  v.push({ x: 0, y: 3.5, z: 7, c: '#4a3524' });
  v.push({ x: 0, y: 4, z: 8, c: '#4a3524' });
  v.push({ x: 0, y: 4.5, z: 9, c: '#4a3524' });
  v.push({ x: 0, y: 5, z: 10, c: '#4a3524' });
  v.push({ x: 0, y: 6, z: 10, c: '#d94f3d' });
  v.push({ x: 1, y: 4, z: 5, c: '#a97e4f' });
  v.push({ x: 0, y: 4, z: 6, c: '#a97e4f' });
  v.push({ x: 1, y: 4, z: 6, c: '#7a5232' });
  return v;
}

const shipGroup = new THREE.Group();
{
  shipGroup.add(voxelMesh(buildShip()));
  const lineArr = [];
  const line = (a, b) => { lineArr.push(a[0], a[1], a[2], b[0], b[1], b[2]); };
  line([0, 9, 4], [0, 5.5, 10]);
  line([0, 11, -2], [0, 5.5, -7]);
  line([0, 11, -2], [2.1, 2.6, -2]);
  line([0, 11, -2], [-2.1, 2.6, -2]);
  line([0, 9, 4], [2.1, 2.6, 4]);
  line([0, 9, 4], [-2.1, 2.6, 4]);
  const rg = new THREE.BufferGeometry();
  rg.setAttribute('position', new THREE.Float32BufferAttribute(lineArr, 3));
  shipGroup.add(new THREE.LineSegments(rg, new THREE.LineBasicMaterial({ color: 0x2b241e, transparent: true, opacity: 0.8 })));
  const lantern = new THREE.Mesh(
    new THREE.BoxGeometry(0.45, 0.45, 0.45),
    new THREE.MeshStandardMaterial({ color: 0xffd95e, emissive: 0xffcf4d, emissiveIntensity: 1.4 })
  );
  lantern.position.set(0, 5, -7);
  shipGroup.add(lantern);
  shipGroup.userData.lantern = lantern;
}
shipGroup.position.set(0.5, -0.7, 0);
scene.add(shipGroup);

/* ---------------- buoys ---------------- */
const buoys = [];
function makeBuoy(x, z, phase) {
  const g = new THREE.Group();
  g.add(voxelMesh([{ x: 0, y: 0, z: 0, c: '#d94f3d' }, { x: 0, y: 1, z: 0, c: '#f2ead8' }]));
  g.position.set(x, 0, z);
  g.userData.phase = phase;
  scene.add(g);
  buoys.push(g);
}
makeBuoy(7, 9, 0.5);
makeBuoy(-3.5, 12, 2.4);

/* ---------------- seagulls ---------------- */
const gulls = [];
function makeGull(cx, cz, r, h, speed, phase) {
  const g = new THREE.Group();
  const mat = new THREE.MeshStandardMaterial({ color: 0xf5f2ea, roughness: 1 });
  const body = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.3, 0.75), mat);
  const wingL = new THREE.Mesh(new THREE.BoxGeometry(0.85, 0.12, 0.45), mat);
  const wingR = new THREE.Mesh(new THREE.BoxGeometry(0.85, 0.12, 0.45), mat);
  wingL.position.set(-0.62, 0, 0);
  wingR.position.set(0.62, 0, 0);
  g.add(body, wingL, wingR);
  g.scale.setScalar(1.3);
  g.traverse(o => { if (o.isMesh) o.castShadow = true; });
  scene.add(g);
  gulls.push({ g, wingL, wingR, cx, cz, r, h, speed, phase });
}
makeGull(3, 2, 7, 12.5, 0.32, 0.0);
makeGull(-6, -6, 8.5, 13.5, 0.26, 2.2);
makeGull(8, -4, 6, 11.5, 0.4, 4.4);

/* ---------------- clouds ---------------- */
const clouds = [];
function makeCloud(x, y, z, speed) {
  const shape = [[-2,0,0],[-1,0,0],[0,0,0],[1,0,0],[2,0,0],[-1,1,0],[0,1,0],[1,1,0],[0,1,-0.75],[-2,1,0.6]];
  const voxels = [];
  for (const [dx, dy, dz] of shape) voxels.push({ x: dx, y: dy, z: dz, c: pick(['#fbf7ee', '#f5f0e4', '#ffffff']) });
  const g = voxelMesh(voxels);
  g.scale.setScalar(1.8);
  g.position.set(x, y, z);
  scene.add(g);
  clouds.push({ g, speed, y0: y, phase: rand() * Math.PI * 2 });
}
makeCloud(-18, 15, -14, 0.55);
makeCloud(8, 17, -22, 0.4);
makeCloud(24, 14.5, 6, 0.7);
makeCloud(-6, 16, 16, 0.5);

/* ---------------- voxel sun + halo ---------------- */
const sunShape = [[0,0],[1,0],[-1,0],[0,1],[0,-1],[1,1],[-1,1],[1,-1],[-1,-1]];
const sunVoxels = [];
for (const [dx, dy] of sunShape)
  sunVoxels.push({ x: dx, y: dy, z: 0, c: (dx === 0 && dy === 0) ? '#ffe89a' : '#ffd95e' });
const sunGroup = voxelMesh(sunVoxels, { cast: false, receive: false });
sunGroup.scale.setScalar(2);
sunGroup.position.set(-24, 19, -22);
scene.add(sunGroup);
{
  const c = document.createElement('canvas'); c.width = c.height = 256;
  const ctx = c.getContext('2d');
  const grad = ctx.createRadialGradient(128, 128, 0, 128, 128, 128);
  grad.addColorStop(0, 'rgba(255, 240, 190, 0.9)');
  grad.addColorStop(0.35, 'rgba(255, 225, 150, 0.45)');
  grad.addColorStop(1, 'rgba(255, 225, 150, 0)');
  ctx.fillStyle = grad; ctx.fillRect(0, 0, 256, 256);
  const glow = new THREE.Sprite(new THREE.SpriteMaterial({
    map: new THREE.CanvasTexture(c), transparent: true, depthWrite: false,
    fog: false, blending: THREE.AdditiveBlending
  }));
  glow.scale.set(26, 26, 1);
  glow.position.set(-24, 19, -22);
  scene.add(glow);
}

/* ---------------- breakwater + lighthouse ---------------- */
const rockVoxels = [];
for (let i = 0; i < 46; i++) {
  const x = 18 + rInt(0, 6);
  const z = -23 + rInt(0, 7);
  if ((x === 20 || x === 21) && (z === -20 || z === -19)) continue;
  rockVoxels.push({ x, y: rInt(-1, 1), z, c: pick(['#8a8d92', '#75787d', '#9aa0a6', '#6d7076']) });
}
for (let x = 20; x <= 21; x++)
  for (let z = -20; z <= -19; z++)
    rockVoxels.push({ x, y: 0, z, c: '#8a8d92' });
scene.add(voxelMesh(rockVoxels));

const lhColors = { 1: '#9aa0a6', 2: '#9aa0a6', 3: '#f2ead8', 4: '#f2ead8', 5: '#c94f3f', 6: '#c94f3f', 7: '#f2ead8' };
const lh = [];
for (let y = 1; y <= 7; y++) lh.push({ x: 21, y, z: -19, c: lhColors[y] });
lh.push({ x: 21, y: 8, z: -19, c: '#ffd95e' });
lh.push({ x: 21, y: 9, z: -19, c: '#8f3826' });
lh.push({ x: 21, y: 10, z: -19, c: '#2e2a26' });
scene.add(voxelMesh(lh));

const lightRoom = new THREE.Mesh(
  new THREE.BoxGeometry(0.9, 0.9, 0.9),
  new THREE.MeshStandardMaterial({ color: 0xffd95e, emissive: 0xffdf6e, emissiveIntensity: 1.6 })
);
lightRoom.position.set(21, 8, -19);
scene.add(lightRoom);
const lhLight = new THREE.PointLight(0xffe9a8, 10, 14, 2);
lhLight.position.set(21, 8.5, -19);
scene.add(lhLight);

const beamGroup = new THREE.Group();
beamGroup.position.set(21, 8.3, -19);
{
  const beamGeo = new THREE.ConeGeometry(1.1, 11, 12, 1, true);
  beamGeo.rotateZ(Math.PI / 2);
  beamGeo.translate(5.5, 0, 0);
  const beam = new THREE.Mesh(beamGeo, new THREE.MeshBasicMaterial({
    color: 0xffe9a8, transparent: true, opacity: 0.3,
    blending: THREE.AdditiveBlending, side: THREE.DoubleSide, depthWrite: false, fog: false
  }));
  beamGroup.add(beam);
}
scene.add(beamGroup);

/* ---------------- animation loop ---------------- */
let t = 0;
const clock = new THREE.Clock();
function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  t += dt;
  updateWater(t);
  // ship bobbing
  shipGroup.position.y = -0.7 + Math.sin(t * 0.8) * 0.15;
  shipGroup.rotation.z = Math.sin(t * 0.62 + 1.1) * 0.03;
  shipGroup.rotation.x = Math.sin(t * 0.5) * 0.02;
  shipGroup.userData.lantern.material.emissiveIntensity = 1.2 + Math.sin(t * 3.0) * 0.5;
  // gulls
  for (const gu of gulls) {
    const a = t * gu.speed + gu.phase;
    gu.g.position.set(
      gu.cx + Math.cos(a) * gu.r,
      gu.h + Math.sin(t * 0.8 + gu.phase) * 0.5,
      gu.cz + Math.sin(a) * gu.r
    );
    gu.g.rotation.y = -a;
    const flap = Math.sin(t * 9 + gu.phase * 3) * 0.5;
    gu.wingL.rotation.z = -flap;
    gu.wingR.rotation.z = flap;
  }
  // clouds
  for (const c of clouds) {
    c.g.position.x += c.speed * dt;
    if (c.g.position.x > 45) c.g.position.x = -45;
    c.g.position.y = c.y0 + Math.sin(t * 0.45 + c.phase) * 0.35;
  }
  // buoys
  for (const b of buoys) {
    b.position.y = Math.sin(t * 1.4 + b.userData.phase) * 0.25;
    b.rotation.z = Math.sin(t * 1.1 + b.userData.phase) * 0.16;
    b.rotation.x = Math.sin(t * 0.9 + b.userData.phase * 1.7) * 0.12;
  }
  // beam & lamps
  beamGroup.rotation.y = t * 0.55;
  lampLight.intensity = 5.5 + Math.sin(t * 2.2) * 1.2;
  lhLight.intensity = 9 + Math.sin(t * 2.8) * 2.0;
  lightRoom.material.emissiveIntensity = 1.5 + Math.sin(t * 2.8) * 0.5;
  controls.update();
  renderer.render(scene, camera);
}
animate();

/* ---------------- resize ---------------- */
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
</script>
</body>
</html>
```

**What's in the scene**
- **Sailing ship** — tapered hull with a red strake, plank deck, stern castle with windows and railing, glowing stern lantern, two masts with billowed cream sails and a red stripe, bowsprit, pennants, rigging lines, deck crates — it gently bobs and tilts.
- **Harbor** — stone quay with a gabled warehouse (door + windows), a plank pier with railing, posts, bollards, crates, barrels, rope coil, and a warm lamp post.
- **Environment** — animated voxel sea (shallow-to-deep gradient + foam strip near the quay), drifting clouds casting moving shadows, a voxel sun with a soft halo, gulls flapping in circles, bobbing buoys, and a breakwater with a banded lighthouse and a rotating light beam.
- **Controls** — drag to orbit, scroll to zoom, right-drag to pan; the gentle auto-rotate pauses while you interact and resumes after 5 seconds.

It loads instantly (no external assets beyond the Three.js CDN) and renders on first paint. One caveat: it pulls Three.js from a CDN, so you need an internet connection the first time you open the file.