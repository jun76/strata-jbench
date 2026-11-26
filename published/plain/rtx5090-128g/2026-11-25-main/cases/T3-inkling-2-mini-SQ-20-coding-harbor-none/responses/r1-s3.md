I can help with that. Below is a single-file HTML page using Three.js from a CDN. It renders a voxel-art sailing ship in a harbor with an ocean plane, sky gradient, simple buoys, and orbit controls so you can rotate/zoom with the mouse.

Because this is a coding task, I can’t embed a live rendered preview directly, but this code should run immediately in Chrome once you paste it into a `.html` file and open it.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>Harbor Sailing Ship — Voxel Art</title>
<style>
  html, body {
    margin: 0;
    padding: 0;
    overflow: hidden;
    background: #8fd3ff;
    font-family: Arial, sans-serif;
  }
  #info {
    position: absolute;
    top: 12px;
    left: 12px;
    background: rgba(255,255,255,0.75);
    padding: 10px 12px;
    border-radius: 8px;
    font-size: 14px;
    line-height: 1.4;
    color: #1c2a3a;
    box-shadow: 0 2px 10px rgba(0,0,0,0.15);
    max-width: 320px;
  }
</style>
</head>
<body>
<div id="info">
  <strong>Sailing Ship Calling at a Harbor</strong><br>
  Drag to orbit · Scroll to zoom · Right-drag to pan
</div>

<script type="importmap">
{
  "imports": {
    "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
    "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
  }
}
</script>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x8fd3ff);
scene.fog = new THREE.Fog(0x8fd3ff, 60, 160);

const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 300);
camera.position.set(22, 18, 26);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 5, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.08;

// Lighting
const ambient = new THREE.AmbientLight(0xffffff, 0.65);
scene.add(ambient);

const sun = new THREE.DirectionalLight(0xfff1d6, 1.6);
sun.position.set(18, 28, 12);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -35;
sun.shadow.camera.right = 35;
sun.shadow.camera.top = 35;
sun.shadow.camera.bottom = -35;
sun.shadow.camera.far = 90;
scene.add(sun);

const rim = new THREE.DirectionalLight(0x9fd8ff, 0.5);
rim.position.set(-20, 12, -15);
scene.add(rim);

// Materials
const mat = {
  hull: new THREE.MeshStandardMaterial({ color: 0x6b3f2a, roughness: 0.85 }),
  hullDark: new THREE.MeshStandardMaterial({ color: 0x3e2417, roughness: 0.9 }),
  deck: new THREE.MeshStandardMaterial({ color: 0xc79a5d, roughness: 0.8 }),
  wood: new THREE.MeshStandardMaterial({ color: 0x8a5a34, roughness: 0.8 }),
  mast: new THREE.MeshStandardMaterial({ color: 0x5a3a22, roughness: 0.75 }),
  sail: new THREE.MeshStandardMaterial({ color: 0xfff2d1, roughness: 0.95, side: THREE.DoubleSide }),
  sailShade: new THREE.MeshStandardMaterial({ color: 0xf1d7a0, roughness: 0.95, side: THREE.DoubleSide }),
  rope: new THREE.MeshStandardMaterial({ color: 0x3b2d20, roughness: 1 }),
  flag: new THREE.MeshStandardMaterial({ color: 0xd94f3d, roughness: 0.8, side: THREE.DoubleSide }),
  gold: new THREE.MeshStandardMaterial({ color: 0xe2b84b, roughness: 0.45, metalness: 0.35 }),
  ocean: new THREE.MeshStandardMaterial({ color: 0x1d7fa8, roughness: 0.55, metalness: 0.05 }),
  pier: new THREE.MeshStandardMaterial({ color: 0x8b6b4f, roughness: 0.9 }),
  pierDark: new THREE.MeshStandardMaterial({ color: 0x5d4636, roughness: 0.9 }),
  rock: new THREE.MeshStandardMaterial({ color: 0x6f7780, roughness: 0.95 }),
  buoy: new THREE.MeshStandardMaterial({ color: 0xff7a2f, roughness: 0.75 }),
  buoyTop: new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.7 }),
  cloud: new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 1 }),
  sand: new THREE.MeshStandardMaterial({ color: 0xe0c27b, roughness: 0.95 }),
  grass: new THREE.MeshStandardMaterial({ color: 0x67b26f, roughness: 0.95 }),
};

function box(w, h, d, material, x = 0, y = 0, z = 0, parent = scene) {
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), material);
  mesh.position.set(x, y, z);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  parent.add(mesh);
  return mesh;
}

function voxel(x, y, z, size, material, parent = scene) {
  return box(size, size, size, material, x, y, z, parent);
}

function makeBoxSail(width, height, depth, material) {
  // Simple stylized voxel-ish sail made from a few stepped blocks
  const group = new THREE.Group();
  const steps = 7;
  for (let i = 0; i < steps; i++) {
    const t = i / (steps - 1);
    const w = THREE.MathUtils.lerp(width, width * 0.45, t);
    const h = height / steps;
    box(w, h, depth, material, 0, h / 2 + i * h, 0, group);
  }
  return group;
}

// Ocean
const ocean = new THREE.Mesh(new THREE.PlaneGeometry(180, 180, 1, 1), mat.ocean);
ocean.rotation.x = -Math.PI / 2;
ocean.position.y = 0;
ocean.receiveShadow = true;
scene.add(ocean);

// Stylized waves (flat voxel rows)
for (let i = -7; i <= 7; i++) {
  for (let j = -5; j <= 5; j++) {
    if ((i * j) % 3 === 0) {
      const w = 1.8 + Math.random() * 2.2;
      const wave = box(w, 0.18, 0.45, new THREE.MeshStandardMaterial({ color: 0x62c2df, roughness: 0.7 }), i * 5.5, 0.12, j * 6 + Math.sin(i + j) * 1.1);
      wave.castShadow = false;
      wave.receiveShadow = true;
    }
  }
}

// Harbor ground / pier
box(30, 2, 12, mat.pier, -18, 1, -10);
box(30, 0.8, 1.4, mat.pierDark, -18, 2.2, -15.6);
box(30, 0.8, 1.4, mat.pierDark, -18, 2.2, -4.4);

// Pier posts
for (let x = -31; x <= -5; x += 4) {
  box(1, 4, 1, mat.pierDark, x, 0.8, -14.7);
  box(1, 4, 1, mat.pierDark, x, 0.8, -5.3);
}

// Land strip
box(22, 2.2, 10, mat.sand, -25, 1.1, -28);
box(22, 1.1, 3, mat.grass, -25, 2.55, -31.5);

// Rocks
[[-3.5, 0.8, 8.5, 2.2], [-1.2, 0.6, 11.5, 1.6], [13, 0.9, 9.5, 2.0]].forEach(([x,y,z,s]) => {
  const rock = box(s, s * 0.75, s * 0.85, mat.rock, x, y, z);
  rock.rotation.y = Math.random() * Math.PI;
});

// Buoys
function makeBuoy(x, z) {
  const g = new THREE.Group();
  g.position.set(x, 0.35, z);
  box(1.3, 0.5, 1.3, mat.buoy, 0, 0.25, 0, g);
  box(0.8, 0.9, 0.8, mat.buoy, 0, 0.95, 0, g);
  box(0.45, 0.75, 0.45, mat.buoyTop, 0, 1.65, 0, g);
  scene.add(g);
  return g;
}
const buoys = [makeBuoy(8, 5), makeBuoy(14, 0), makeBuoy(-5, 10)];

// Sailing ship
const ship = new THREE.Group();
ship.position.set(3.5, 1.05, 2.2);
ship.rotation.y = -0.18;
scene.add(ship);

// Hull (voxel-stepped)
const hullBlocks = [
  [-4.6, -1.0, 0.0, 0.8],
  [-3.6, -1.25, 0.55, 0.85],
  [-2.4, -1.45, 0.85, 1.0],
  [-1.0, -1.6, 1.1, 1.15],
  [0.5, -1.6, 1.15, 1.15],
  [2.0, -1.45, 0.95, 1.05],
  [3.4, -1.15, 0.65, 0.9],
  [4.5, -0.85, 0.25, 0.75]
];
for (const [x, y, z, s] of hullBlocks) {
  box(1.15, 1.15, 1.15 + Math.max(0, (4.5 - Math.abs(x)) * 0.12), mat.hull, x, y, z, ship);
}

// Hull bottom keel
box(8.4, 0.55, 0.75, mat.hullDark, 0, -2.05, 0, ship);
box(7.4, 0.45, 0.65, mat.hullDark, 0, -2.35, 0, ship);

// Deck
box(8.6, 0.45, 2.15, mat.deck, 0, -0.25, 0, ship);
box(7.8, 0.35, 1.75, mat.wood, 0, 0.05, 0, ship);

// Bulwarks / rails
for (let x = -3.6; x <= 3.6; x += 0.9) {
  box(0.28, 0.55, 0.28, mat.hullDark, x, 0.35, 1.05, ship);
  box(0.28, 0.55, 0.28, mat.hullDark, x, 0.35, -1.05, ship);
}
box(7.8, 0.18, 0.18, mat.hullDark, 0, 0.68, 1.05, ship);
box(7.8, 0.18, 0.18, mat.hullDark, 0, 0.68, -1.05, ship);

// Bow and stern castle
box(2.0, 1.0, 1.6, mat.hull, -3.6, 0.55, 0, ship);
box(1.6, 0.8, 1.25, mat.deck, -3.6, 1.35, 0, ship);
box(2.0, 1.05, 1.55, mat.hull, 3.75, 0.55, 0, ship);
box(1.55, 0.85, 1.25, mat.deck, 3.75, 1.4, 0, ship);

// Cabin details
box(0.9, 0.65, 0.9, mat.gold, -3.6, 1.95, 0, ship);
box(0.9, 0.65, 0.9, mat.gold, 3.75, 2.0, 0, ship);

// Masts and yards
const mastPositions = [-1.9, 1.5];
for (const mx of mastPositions) {
  box(0.38, 7.8, 0.38, mat.mast, mx, 3.9, 0, ship);
  box(0.24, 1.0, 0.24, mat.gold, mx, 8.0, 0, ship);
}

// Sails
function addSail(mastX, y, width, height, shade = false) {
  const sailGroup = makeBoxSail(width, height, 0.28, shade ? mat.sailShade : mat.sail);
  sailGroup.position.set(mastX, y, 0.42);
  ship.add(sailGroup);

  // Slight backward curve by shifting sail blocks
  sailGroup.children.forEach((child, i) => {
    child.position.z = 0.18 * Math.sin((i / sailGroup.children.length) * Math.PI);
  });
}

addSail(-1.9, 2.0, 3.3, 4.8);
addSail(-1.9, 5.15, 2.45, 2.0, true);
addSail(1.5, 2.2, 3.0, 4.5);
addSail(1.5, 5.25, 2.2, 1.8, true);

// Yards / spars
box(3.8, 0.22, 0.22, mat.wood, -1.9, 6.95, 0, ship);
box(2.9, 0.22, 0.22, mat.wood, -1.9, 7.45, 0, ship);
box(3.35, 0.22, 0.22, mat.wood, 1.5, 6.7, 0, ship);
box(2.65, 0.22, 0.22, mat.wood, 1.5, 7.3, 0, ship);

// Flags
box(0.1, 1.15, 0.1, mat.mast, -1.9, 8.75, 0, ship);
const flag1 = new THREE.Mesh(new THREE.PlaneGeometry(1.2, 0.65), mat.flag);
flag1.position.set(-1.25, 9.15, 0);
flag1.castShadow = true;
ship.add(flag1);

box(0.1, 1.05, 0.1, mat.mast, 1.5, 8.35, 0, ship);
const flag2 = new THREE.Mesh(new THREE.PlaneGeometry(1.0, 0.55), mat.flag);
flag2.position.set(1.9, 8.75, 0);
flag2.castShadow = true;
ship.add(flag2);

// Ropes (thin boxes)
const ropeMaterial = mat.rope;
function rope(from, to, thickness = 0.06) {
  const start = new THREE.Vector3(...from);
  const end = new THREE.Vector3(...to);
  const dir = new THREE.Vector3().subVectors(end, start);
  const length = dir.length();
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(thickness, length, thickness), ropeMaterial);
  mesh.position.copy(start).add(end).multiplyScalar(0.5);
  mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir.normalize());
  mesh.castShadow = true;
  ship.add(mesh);
}
rope([-1.9, 8.25, 0], [-4.2, 1.15, 0]);
rope([-1.9, 8.25, 0], [0.4, 1.05, 0]);
rope([1.5, 8.0, 0], [-1.0, 1.1, 0]);
rope([1.5, 8.0, 0], [4.2, 1.15, 0]);
rope([-1.9, 4.9, 0], [1.5, 4.7, 0], 0.045);

// Cargo crates on deck
box(0.72, 0.72, 0.72, mat.wood, -0.35, 0.55, 0.42, ship);
box(0.72, 0.72, 0.72, mat.wood, 0.45, 0.55, -0.38, ship);
box(0.58, 0.58, 0.58, mat.gold, -0.05, 1.15, -0.1, ship);

// Lantern
box(0.38, 0.42, 0.38, mat.gold, 4.45, 2.2, 0, ship);

// Clouds
function makeCloud(x, y, z, scale = 1) {
  const g = new THREE.Group();
  const parts = [
    [0, 0, 0, 2.0],
    [1.2, 0.25, 0, 1.45],
    [-1.2, 0.18, 0, 1.35],
    [0.35, 0.62, 0, 1.2]
  ];
  for (const [px, py, pz, s] of parts) {
    const puff = box(s, s * 0.75, s, mat.cloud, px, py, pz, g);
    puff.castShadow = false;
    puff.receiveShadow = false;
  }
  g.position.set(x, y, z);
  g.scale.setScalar(scale);
  scene.add(g);
  return g;
}
const clouds = [
  makeCloud(-28, 22, -28, 1.6),
  makeCloud(20, 25, -34, 1.9),
  makeCloud(6, 28, 22, 1.35)
];

// Seagulls (simple voxel wings)
function makeGull(x, y, z) {
  const g = new THREE.Group();
  box(0.22, 0.08, 0.08, new THREE.MeshStandardMaterial({ color: 0xffffff }), -0.25, 0, 0, g);
  box(0.22, 0.08, 0.08, new THREE.MeshStandardMaterial({ color: 0xffffff }), 0.25, 0, 0, g);
  box(0.28, 0.1, 0.12, new THREE.MeshStandardMaterial({ color: 0xffffff }), 0, 0.03, 0, g);
  g.position.set(x, y, z);
  scene.add(g);
  return g;
}
const gulls = [makeGull(-8, 14, 4), makeGull(12, 16, -3)];

// Gentle animation
const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);
  const t = clock.getElapsedTime();

  ship.position.y = 1.05 + Math.sin(t * 1.15) * 0.16;
  ship.rotation.z = Math.sin(t * 0.8) * 0.025;
  ship.rotation.x = Math.cos(t * 0.9) * 0.02;

  buoys.forEach((b, i) => {
    b.position.y = 0.35 + Math.sin(t * 1.35 + i * 1.7) * 0.12;
    b.rotation.z = Math.sin(t * 1.1 + i) * 0.08;
  });

  clouds.forEach((c, i) => {
    c.position.x += Math.sin(t * 0.18 + i) * 0.004;
  });

  gulls.forEach((g, i) => {
    g.position.x = (i === 0 ? -8 : 12) + Math.sin(t * 0.55 + i * 2.0) * 5.5;
    g.position.y = (i === 0 ? 14 : 16) + Math.sin(t * 1.6 + i) * 0.45;
    g.rotation.z = Math.sin(t * 2.1 + i) * 0.12;
  });

  flag1.rotation.y = Math.sin(t * 3.0) * 0.18;
  flag2.rotation.y = Math.sin(t * 3.3 + 0.8) * 0.18;

  controls.update();
  renderer.render(scene, camera);
}
animate();

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
</script>
</body>
</html>
```

Save it as `harbor-ship.html`, then open it in Chrome.

Notes:
- Uses Three.js via CDN, so it needs internet access the first time.
- You can orbit, zoom, and pan with the mouse.
- The ship gently bobs, buoys float, clouds drift, and gulls move.
- If you want it fully offline, download `three.module.js` and the OrbitControls file locally and replace the CDN import URLs.