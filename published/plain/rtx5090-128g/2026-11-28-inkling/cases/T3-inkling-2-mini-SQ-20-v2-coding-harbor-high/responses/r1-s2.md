Here's a complete, self-contained voxel art scene — a sailing ship at a harbor with an animated voxel ocean, pier, lighthouse with rotating beam, houses, trees, gulls, clouds, buoys and a rowboat. Just paste it into one `.html` file and open it in Chrome:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Harbor Call — Voxel Sailing Scene</title>
<style>
  html, body { margin: 0; height: 100%; overflow: hidden; background: #9fd0e8; }
  #app { position: fixed; inset: 0; }
  canvas { display: block; }
  .vignette { position: fixed; inset: 0; z-index: 1; pointer-events: none;
    background: radial-gradient(ellipse at center, transparent 52%, rgba(8,34,52,.38) 100%); }
  .hud { position: fixed; top: 18px; left: 20px; z-index: 2; pointer-events: none;
    color: #fff; text-shadow: 0 2px 10px rgba(8,42,66,.55); }
  .hud h1 { margin: 0; font-family: "Courier New", monospace; font-size: 24px; letter-spacing: 3px; font-weight: 700; }
  .hud p { margin: 4px 0 0; font-family: "Courier New", monospace; font-size: 11px; letter-spacing: 2px; opacity: .92; }
  .hint { position: fixed; bottom: 16px; left: 50%; transform: translateX(-50%); z-index: 2; pointer-events: none;
    font-family: "Courier New", monospace; font-size: 11px; letter-spacing: 1.5px; color: #fff;
    background: rgba(10,38,56,.45); border: 1px solid rgba(255,255,255,.25);
    padding: 8px 18px; border-radius: 999px; backdrop-filter: blur(6px); white-space: nowrap; }
</style>
<script type="importmap">
{
  "imports": {
    "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
    "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
  }
}
</script>
</head>
<body>
<div id="app"></div>
<div class="vignette"></div>
<div class="hud"><h1>⛵ HARBOR CALL</h1><p>VOXEL SAILING SCENE · THREE.JS</p></div>
<div class="hint">DRAG · ORBIT&nbsp;&nbsp;&nbsp;SCROLL · ZOOM&nbsp;&nbsp;&nbsp;RIGHT-DRAG · PAN</div>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* ---------------- palette ---------------- */
const C = {
  sand: 0xe8d5a0, sandDark: 0xc4ac74, grass: 0x6fae5c,
  leaf: 0x3f7d3a, leafLight: 0x5da24c, trunk: 0x6b4226,
  wallA: 0xf3e8d2, wallB: 0xead9c0, wallC: 0xf6e2c8,
  roofA: 0xc05746, roofB: 0x4e6e8e, roofC: 0xb56a3c,
  door: 0x5a3a24, window: 0xffe08a, chimney: 0x9a4a3a,
  plankA: 0x9a6b3f, plankB: 0x86582f, rail: 0x6b4a2f, post: 0x4a3220,
  crate: 0xa9763e, barrel: 0x7a5230, barrelBand: 0x5d4030,
  rock: 0x8d8d94, rockDark: 0x74747c,
  lhWhite: 0xf7f3ea, lhRed: 0xd94f3d, gallery: 0x2e2018, finial: 0xd8a13a,
  hull: 0x7a3b2e, hullDark: 0x4a2c20, deck: 0xc9a06b, mast: 0x5d4030,
  yard: 0x4a3220, sail: 0xf5eeda, sail2: 0xeee4c8, jib: 0xf3ecd9,
  flag: 0xd94f3d, flagWhite: 0xf7f3ea, pennant: 0xf2c14e,
  porthole: 0x2e2018, cannon: 0x3a3a3a, rig: 0x3a2a1c,
  castleWood: 0x8a5a35, castleRoof: 0x8a4a38,
  boatHull: 0xb0483a, boatRim: 0x8a5a35, boatBench: 0xc9a06b,
  buoyRed: 0xd94f3d, buoyWhite: 0xf7f3ea,
  waterShallow: 0x63b3cc, waterDeep: 0x2e6d96,
};

/* ---------------- renderer / scene / camera ---------------- */
const app = document.getElementById('app');
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.12;
app.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xcfe3ec, 75, 190);

const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 600);
camera.position.set(30, 19, 36);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 3, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.minDistance = 12;
controls.maxDistance = 95;
controls.maxPolarAngle = Math.PI * 0.49;
controls.autoRotate = true;
controls.autoRotateSpeed = 0.45;
controls.addEventListener('start', () => { controls.autoRotate = false; });

/* ---------------- sky ---------------- */
const skyGeo = new THREE.SphereGeometry(260, 24, 16);
const skyMat = new THREE.ShaderMaterial({
  side: THREE.BackSide, depthWrite: false,
  uniforms: {
    top: { value: new THREE.Color(0x4f9fd0) },
    mid: { value: new THREE.Color(0x9fd0e8) },
    bot: { value: new THREE.Color(0xe8f2e2) },
  },
  vertexShader: `varying vec3 vPos; void main(){ vPos = position; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
  fragmentShader: `varying vec3 vPos; uniform vec3 top; uniform vec3 mid; uniform vec3 bot;
    void main(){
      float h = normalize(vPos).y;
      vec3 col = h > 0.0 ? mix(mid, top, pow(h, 0.75)) : mix(mid, bot, pow(-h, 0.7));
      gl_FragColor = vec4(col, 1.0);
    }`,
});
scene.add(new THREE.Mesh(skyGeo, skyMat));

const sunDisc = new THREE.Mesh(
  new THREE.CircleGeometry(9, 24),
  new THREE.MeshBasicMaterial({ color: 0xfff3c0, fog: false })
);
sunDisc.position.set(93, 112, 64);
sunDisc.lookAt(0, 0, 0);
scene.add(sunDisc);

/* ---------------- lights ---------------- */
const hemi = new THREE.HemisphereLight(0xbfe3ff, 0x8a6f4d, 0.85);
scene.add(hemi);

const sun = new THREE.DirectionalLight(0xfff2dd, 1.7);
sun.position.set(35, 42, 24);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.near = 10;
sun.shadow.camera.far = 140;
sun.shadow.camera.left = -45;
sun.shadow.camera.right = 45;
sun.shadow.camera.top = 45;
sun.shadow.camera.bottom = -45;
sun.shadow.bias = -0.0004;
sun.shadow.normalBias = 0.5;
scene.add(sun);

/* ---------------- voxel builder ---------------- */
function voxelBuilder() {
  const buckets = new Map();
  const api = {
    add(x, y, z, color, s = 1) {
      let arr = buckets.get(color);
      if (!arr) { arr = []; buckets.set(color, arr); }
      arr.push([x, y, z, s]);
    },
    rect(x0, y0, z0, x1, y1, z1, color, s = 1) {
      const xa = Math.min(x0, x1), xb = Math.max(x0, x1);
      const ya = Math.min(y0, y1), yb = Math.max(y0, y1);
      const za = Math.min(z0, z1), zb = Math.max(z0, z1);
      for (let x = xa; x <= xb + 0.001; x += 1)
        for (let y = ya; y <= yb + 0.001; y += 1)
          for (let z = za; z <= zb + 0.001; z += 1)
            api.add(x, y, z, color, s);
    },
    rig(x1, y1, z1, x2, y2, z2, color, s = 0.9) {
      const len = Math.hypot(x2 - x1, y2 - y1, z2 - z1);
      const steps = Math.max(1, Math.round(len / 0.72));
      for (let i = 0; i <= steps; i++) {
        const t = i / steps;
        api.add(x1 + (x2 - x1) * t, y1 + (y2 - y1) * t, z1 + (z2 - z1) * t, color, s);
      }
    },
    build(parent) {
      for (const [color, arr] of buckets) {
        const geo = new THREE.BoxGeometry(1, 1, 1);
        const mat = new THREE.MeshLambertMaterial({ color });
        const inst = new THREE.InstancedMesh(geo, mat, arr.length);
        const m = new THREE.Matrix4();
        for (let i = 0; i < arr.length; i++) {
          const v = arr[i];
          m.makeScale(v[3], v[3], v[3]);
          m.setPosition(v[0], v[1], v[2]);
          inst.setMatrixAt(i, m);
        }
        inst.castShadow = true;
        inst.receiveShadow = true;
        parent.add(inst);
      }
      buckets.clear();
    },
  };
  return api;
}

/* ---------------- world: shore, houses, trees, pier, lighthouse, island ---------------- */
function tree(b, x, z) {
  b.add(x, 2, z, C.trunk); b.add(x, 3, z, C.trunk);
  b.rect(x - 1, 4, z - 1, x + 1, 5, z + 1, C.leaf);
  b.add(x, 6, z, C.leafLight);
}
function palmTree(b, x, z) {
  b.add(x, 1, z, C.trunk); b.add(x, 2, z, C.trunk);
  b.rect(x - 1, 3, z - 1, x + 1, 3, z + 1, C.leaf);
  b.add(x, 4, z, C.leafLight);
}
function house(b, cx, cz, wall, roof) {
  b.rect(cx - 1, 2, cz - 1, cx + 1, 3, cz + 1, wall);
  b.rect(cx - 1, 4, cz - 1, cx + 1, 4, cz + 1, roof);
  b.add(cx, 5, cz, roof);
  b.add(cx - 1, 5, cz - 1, C.chimney);
  b.add(cx + 1, 2, cz, C.door, 1.06); b.add(cx + 1, 3, cz, C.door, 1.06);
  b.add(cx + 1, 3, cz - 1, C.window, 1.06); b.add(cx + 1, 3, cz + 1, C.window, 1.06);
  b.add(cx, 3, cz - 1, C.window, 1.06); b.add(cx, 3, cz + 1, C.window, 1.06);
}

const world = new THREE.Group();
scene.add(world);
const b = voxelBuilder();

// shore
b.rect(-30, 1, -24, -17, 1, 24, C.sand);
b.rect(-19, 2, -12, -18, 2, -10, C.grass);
b.rect(-25, 2, 5, -23, 2, 8, C.grass);
b.rect(-19, 2, 13, -17, 2, 15, C.grass);
house(b, -24, -9, C.wallA, C.roofA);
house(b, -26, 2, C.wallB, C.roofB);
house(b, -22, 9, C.wallC, C.roofC);
[[-19, -15], [-21, -5], [-20, 3], [-26, 11], [-28, -7]].forEach(([x, z]) => tree(b, x, z));

// pier
for (let x = -16; x <= -4; x++) {
  const col = (x % 2 === 0) ? C.plankA : C.plankB;
  for (let z = -2; z <= 2; z++) b.add(x, 1, z, col);
  b.add(x, 2, -2, C.rail); b.add(x, 2, 2, C.rail);
}
[-15, -11, -7].forEach(x => { [-2, 2].forEach(z => { b.add(x, 0, z, C.post); b.add(x, -1, z, C.post); }); });
b.add(-13, 2, -1, C.crate); b.add(-13, 3, -1, C.crate, 0.8);
b.add(-12, 2, 1, C.crate);
b.add(-9, 2, 1, C.barrel); b.add(-9, 3, 1, C.barrelBand, 0.9);
b.add(-8, 2, 1, C.barrel);
b.add(-4, 2, 0, C.post);

// breakwater rocks
for (let x = 12; x <= 26; x++) {
  b.add(x, 0, -15, (x % 2 === 0) ? C.rock : C.rockDark);
  if (x % 2 === 0) b.add(x, 1, -15, C.rock);
}
for (let x = 13; x <= 25; x++) b.add(x, 0, -16, C.rockDark);
b.add(11, 0, -14, C.rock); b.add(27, 0, -16, C.rock);

// lighthouse at (20, -15)
for (let dx = -1; dx <= 1; dx++) for (let dz = -1; dz <= 1; dz++) {
  b.add(20 + dx, 2, -15 + dz, C.lhWhite);
  b.add(20 + dx, 3, -15 + dz, C.lhWhite);
  b.add(20 + dx, 4, -15 + dz, C.lhRed);
  b.add(20 + dx, 5, -15 + dz, C.lhRed);
  b.add(20 + dx, 6, -15 + dz, C.lhWhite);
}
[[19.5, -15.5], [19.5, -14.5], [20.5, -15.5], [20.5, -14.5]].forEach(([x, z]) => {
  b.add(x, 7, z, C.lhWhite);
  b.add(x, 8, z, C.gallery);
  b.add(x, 10, z, C.lhRed);
});
b.add(20, 11, -15, C.finial);
b.add(20, 12, -15, C.gallery, 0.5);

// island with palms
for (let dx = -3; dx <= 3; dx++) for (let dz = -2; dz <= 2; dz++) {
  if (dx * dx / 9 + dz * dz / 4 <= 1) b.add(-2 + dx, 0, -24 + dz, C.sand);
}
palmTree(b, -3, -25); palmTree(b, 0, -23);
b.add(-4, 1, -23, C.rock);

// shoreline rocks
b.add(-17, 0, -18, C.rock); b.add(-17, 0, 18, C.rock);

b.build(world);

// shore + underwater base slabs
const shoreBase = new THREE.Mesh(
  new THREE.BoxGeometry(13, 3, 48),
  new THREE.MeshLambertMaterial({ color: C.sandDark })
);
shoreBase.position.set(-23.5, -0.5, 0);
shoreBase.receiveShadow = true;
scene.add(shoreBase);

const under = new THREE.Mesh(
  new THREE.BoxGeometry(56, 5, 58),
  new THREE.MeshLambertMaterial({ color: 0x1d4b63 })
);
under.position.set(7.5, -3.2, 0);
scene.add(under);

/* ---------------- water ---------------- */
const W = { x0: -17, x1: 32, z0: -26, z1: 26 };
const waterCount = (W.x1 - W.x0 + 1) * (W.z1 - W.z0 + 1);
const waterGeo = new THREE.BoxGeometry(0.98, 1, 0.98);
const waterMat = new THREE.MeshLambertMaterial({ color: 0xffffff });
const water = new THREE.InstancedMesh(waterGeo, waterMat, waterCount);
water.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
water.receiveShadow = true;
const waterData = [];
{
  const cShallow = new THREE.Color(C.waterShallow);
  const cDeep = new THREE.Color(C.waterDeep);
  const c = new THREE.Color();
  let idx = 0;
  for (let x = W.x0; x <= W.x1; x++) for (let z = W.z0; z <= W.z1; z++) {
    const t = (x - W.x0) / (W.x1 - W.x0);
    c.copy(cShallow).lerp(cDeep, Math.min(1, Math.max(0, t * 1.25 - 0.05)));
    c.offsetHSL(0, 0, (Math.random() - 0.5) * 0.05);
    water.setColorAt(idx, c);
    waterData.push({ x, z });
    idx++;
  }
  if (water.instanceColor) water.instanceColor.needsUpdate = true;
}
scene.add(water);

/* ---------------- sailing ship ---------------- */
const ship = new THREE.Group();
ship.position.set(5, -0.4, 3);
ship.rotation.y = -0.35;
scene.add(ship);
const sb = voxelBuilder();

// hull
for (let x = -4; x <= 4; x++) for (let z = -1; z <= 1; z++) sb.add(x, 0, z, C.hullDark);
for (let x = -6; x <= 6; x++) for (let z = -2; z <= 2; z++) sb.add(x, 1, z, C.hull);
for (let x = -7; x <= 7; x++) {
  const hw = Math.abs(x) <= 5 ? 2 : 1;
  for (let z = -hw; z <= hw; z++) sb.add(x, 2, z, C.hull);
}
// deck
for (let x = -7; x <= 7; x++) {
  const hw = Math.abs(x) <= 6 ? 2 : 1;
  for (let z = -hw; z <= hw; z++) sb.add(x, 3, z, C.deck);
}
// rails
for (let x = -2; x <= 6; x++) {
  sb.add(x, 4, -2, C.hullDark, 0.85);
  sb.add(x, 4, 2, C.hullDark, 0.85);
}
// stern castle
sb.rect(-6, 4, -2, -3, 5, 2, C.castleWood);
sb.rect(-6, 6, -2, -3, 6, 2, C.castleRoof);
sb.add(-6, 4, -1, C.porthole, 1.06);
sb.add(-6, 4, 1, C.porthole, 1.06);
sb.add(-6, 5, 0, C.porthole, 1.06);
sb.add(-4, 7, 0, C.mast);
sb.add(-3, 7, 0, C.flag); sb.add(-2, 7, 0, C.flagWhite);
// forecastle platform
sb.rect(5, 4, -1, 7, 4, 1, C.castleWood);
// masts
for (let y = 3; y <= 10; y++) sb.add(-1, y, -0.6, C.mast);
sb.add(-1, 12, -0.6, C.mast);
for (let y = 3; y <= 8; y++) sb.add(5, y, -0.6, C.mast);
sb.add(5, 10, -0.6, C.mast);
// yards
sb.rect(-4, 11, -0.6, 2, 11, -0.6, C.yard);
sb.rect(2, 9, -0.6, 8, 9, -0.6, C.yard);
// main sail
const belly = [0, 1, 2, 1, 0];
for (let y = 6; y <= 10; y++) {
  const zi = belly[y - 6];
  const xa = y === 10 ? -3 : -4, xb = y === 10 ? 1 : 2;
  for (let x = xa; x <= xb; x++) sb.add(x, y, zi, (y % 2 === 0) ? C.sail : C.sail2);
}
// fore sail
for (let y = 6; y <= 8; y++) {
  const zi = y === 7 ? 1 : 0;
  const xa = y === 8 ? 3 : 2, xb = y === 8 ? 7 : 8;
  for (let x = xa; x <= xb; x++) sb.add(x, y, zi, (y % 2 === 0) ? C.sail : C.sail2);
}
// jib
sb.rect(6, 3, -0.2, 6, 5, -0.2, C.jib);
sb.add(7, 3, -0.2, C.jib);
// bowsprit + rigging
sb.rig(7, 3, 0, 10, 4, 0, C.mast, 0.8);
sb.rig(-1, 12, 0.6, 10, 4, 0.6, C.rig, 0.75);
sb.rig(-1, 12, 0.6, -6, 3, 0.6, C.rig, 0.75);
sb.rig(5, 10, 0.6, 10, 4, 0.6, C.rig, 0.75);
sb.rig(5, 10, 0.6, -1, 12, 0.6, C.rig, 0.75);
// flags
sb.add(0, 12, -0.6, C.flag); sb.add(1, 12, -0.6, C.flagWhite); sb.add(2, 12, -0.6, C.flag);
sb.add(6, 10, -0.6, C.pennant); sb.add(7, 10, -0.6, C.flagWhite);
// portholes
[-5, -2, 1, 4].forEach(x => {
  sb.add(x, 1, 2, C.porthole, 1.06);
  sb.add(x, 1, -2, C.porthole, 1.06);
});
// cannons
[[1, 1.5], [1, -1.5], [4, 1.5], [4, -1.5]].forEach(([x, z]) => sb.add(x, 4, z, C.cannon, 0.85));

sb.build(ship);

/* ---------------- rowboat ---------------- */
const boat = new THREE.Group();
boat.position.set(-8, -0.5, 6);
boat.rotation.y = 0.5;
scene.add(boat);
const rb = voxelBuilder();
for (let z = -2; z <= 2; z++) {
  rb.add(-0.5, 0, z, C.boatHull); rb.add(0, 0, z, C.boatHull); rb.add(0.5, 0, z, C.boatHull);
  rb.add(-0.5, 1, z, C.boatRim, 0.9); rb.add(0.5, 1, z, C.boatRim, 0.9);
}
rb.add(0, 1, -1, C.boatBench); rb.add(0, 1, 1, C.boatBench);
rb.build(boat);

/* ---------------- buoys ---------------- */
const buoys = [];
[[8, 8], [-4, -12], [16, 4]].forEach(([x, z], i) => {
  const g = new THREE.Group();
  g.position.set(x, 0, z);
  const m1 = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.8, 0.8), new THREE.MeshLambertMaterial({ color: C.buoyRed }));
  m1.position.y = 0.2;
  const m2 = new THREE.Mesh(new THREE.BoxGeometry(0.55, 0.55, 0.55), new THREE.MeshLambertMaterial({ color: C.buoyWhite }));
  m2.position.y = 0.9;
  const m3 = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.35, 0.35), new THREE.MeshLambertMaterial({ color: C.buoyRed }));
  m3.position.y = 1.35;
  [m1, m2, m3].forEach(m => { m.castShadow = true; g.add(m); });
  g.userData = { phase: i * 2.1 };
  scene.add(g);
  buoys.push(g);
});

/* ---------------- lighthouse lamp + rotating beam ---------------- */
const lamp = new THREE.Mesh(
  new THREE.BoxGeometry(0.9, 0.9, 0.9),
  new THREE.MeshLambertMaterial({ color: 0xfff6c0, emissive: 0xffd76a, emissiveIntensity: 1.3 })
);
lamp.position.set(20, 9, -15);
scene.add(lamp);

const beamGroup = new THREE.Group();
beamGroup.position.set(20, 9, -15);
scene.add(beamGroup);
const beamGeo = new THREE.ConeGeometry(3.4, 16, 12, 1, true);
beamGeo.translate(0, -8, 0);
beamGeo.rotateZ(Math.PI / 2);
const beam = new THREE.Mesh(beamGeo, new THREE.MeshBasicMaterial({
  color: 0xffe9a8, transparent: true, opacity: 0.22,
  blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide, fog: false,
}));
beam.rotation.z = -0.05;
beamGroup.add(beam);

const lampLight = new THREE.PointLight(0xffe6a0, 40, 42, 2);
lampLight.position.set(20, 9.5, -15);
scene.add(lampLight);

// pier lamp
const pierLamp = new THREE.Mesh(
  new THREE.BoxGeometry(0.7, 0.7, 0.7),
  new THREE.MeshLambertMaterial({ color: 0xfff6c0, emissive: 0xffd76a, emissiveIntensity: 1.1 })
);
pierLamp.position.set(-4, 2.95, 0);
scene.add(pierLamp);

/* ---------------- clouds ---------------- */
const clouds = [];
[
  { x: -25, y: 17, z: -10, s: 1.2, speed: 0.9 },
  { x: -5, y: 19, z: -18, s: 1.5, speed: 0.6 },
  { x: 15, y: 16, z: -12, s: 1.0, speed: 1.1 },
  { x: 25, y: 18, z: -4, s: 1.3, speed: 0.8 },
  { x: -12, y: 15, z: 8, s: 0.9, speed: 1.0 },
].forEach(cd => {
  const g = new THREE.Group();
  const mat = new THREE.MeshLambertMaterial({ color: 0xffffff });
  const mat2 = new THREE.MeshLambertMaterial({ color: 0xdfe9ee });
  [[0, 0, 0, mat], [1.2, 0.15, 0, mat], [-1.1, 0.1, 0, mat], [0.4, 0.7, 0, mat],
   [-0.6, 0.6, 0, mat], [2.1, 0, 0, mat], [-2.0, 0, 0, mat], [0, -0.4, 0, mat2]].forEach(([x, y, z, m]) => {
    const s = (1.4 + Math.random() * 0.6) * cd.s;
    const mesh = new THREE.Mesh(new THREE.BoxGeometry(s, s * 0.75, s), m);
    mesh.position.set(x * cd.s, y * cd.s, z * cd.s);
    g.add(mesh);
  });
  g.position.set(cd.x, cd.y, cd.z);
  g.userData = { speed: cd.speed };
  scene.add(g);
  clouds.push(g);
});

/* ---------------- seagulls ---------------- */
const gulls = [];
for (let i = 0; i < 3; i++) {
  const g = new THREE.Group();
  const mat = new THREE.MeshLambertMaterial({ color: 0xffffff });
  const body = new THREE.Mesh(new THREE.BoxGeometry(0.32, 0.26, 0.7), mat);
  const wingGeo = new THREE.BoxGeometry(0.95, 0.09, 0.34);
  const wl = new THREE.Group();
  const wr = new THREE.Group();
  const wlMesh = new THREE.Mesh(wingGeo, mat); wlMesh.position.x = -0.44;
  const wrMesh = new THREE.Mesh(wingGeo, mat); wrMesh.position.x = 0.44;
  wl.add(wlMesh); wr.add(wrMesh);
  g.add(body, wl, wr);
  g.userData = { r: 7 + i * 1.6, h: 11 + i * 1.4, speed: 0.32 + i * 0.07, phase: i * 2.1, wl, wr };
  scene.add(g);
  gulls.push(g);
}

/* ---------------- animation ---------------- */
const clock = new THREE.Clock();
const dummy = new THREE.Object3D();

function animate() {
  requestAnimationFrame(animate);
  const dt = clock.getDelta();
  const t = clock.elapsedTime;

  // water waves
  for (let i = 0; i < waterData.length; i++) {
    const d = waterData[i];
    const y = -0.55 + Math.sin(d.x * 0.32 + t * 1.35) * 0.24 + Math.cos(d.z * 0.3 + t * 1.05) * 0.2;
    dummy.position.set(d.x, y, d.z);
    dummy.updateMatrix();
    water.setMatrixAt(i, dummy.matrix);
  }
  water.instanceMatrix.needsUpdate = true;

  // ship bob
  ship.position.y = -0.4 + Math.sin(t * 0.9) * 0.28;
  ship.rotation.z = Math.sin(t * 0.7) * 0.035;
  ship.rotation.x = Math.sin(t * 0.55 + 1) * 0.02;

  // rowboat
  boat.position.y = -0.5 + Math.sin(t * 1.25 + 2) * 0.22;
  boat.rotation.z = Math.sin(t * 1.05 + 1) * 0.09;
  boat.rotation.x = Math.sin(t * 0.8) * 0.05;

  // buoys
  buoys.forEach(g => {
    g.position.y = Math.sin(t * 1.4 + g.userData.phase) * 0.25;
    g.rotation.z = Math.sin(t * 1.1 + g.userData.phase) * 0.1;
  });

  // clouds drift
  clouds.forEach(g => {
    g.position.x += g.userData.speed * dt;
    if (g.position.x > 42) g.position.x = -42;
  });

  // seagulls
  gulls.forEach(g => {
    const u = g.userData;
    const a = t * u.speed + u.phase;
    g.position.set(5 + Math.cos(a) * u.r, u.h + Math.sin(t * 1.3 + u.phase) * 0.7, 3 + Math.sin(a) * u.r);
    g.rotation.y = -a;
    const flap = Math.sin(t * 9 + u.phase) * 0.6;
    u.wl.rotation.z = -flap;
    u.wr.rotation.z = flap;
  });

  // lighthouse beam + lamp flicker
  beamGroup.rotation.y = t * 0.7;
  lamp.material.emissiveIntensity = 1.2 + Math.sin(t * 6) * 0.25;

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

- **Voxel sailing ship** — two-tone hull with portholes, tapered bow/stern, deck with rails, stern castle with glowing windows, forecastle, two masts with bellying square sails, triangular jib, bowsprit, rigging, red-white flag, pennant and cannons. It bobs and rolls gently.
- **Harbor** — wooden pier with crates, barrels, a glowing end lantern, a beachfront village (3 houses, trees, grass patches), a rock breakwater with a banded lighthouse and rotating light beam, a sandy palm island, buoys bobbing in the water, and a small rowboat.
- **Living sky** — gradient sky with sun disc, drifting voxel clouds, and three flapping seagulls circling the ship.
- **Ocean** — ~2,600 animated voxel waves with shallow-to-deep blue color gradient and soft shadows.

Controls: drag to orbit, scroll to zoom, right-drag to pan. The camera slowly auto-rotates until you grab it. Everything renders immediately on open — no build step, no other files needed.