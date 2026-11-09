Save the following as a single `.html` file and open it in Chrome.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Voxel Harbor — Sailing Ship Calling at a Harbor</title>
<style>
  html, body {
    margin: 0;
    height: 100%;
    overflow: hidden;
    background: #bfe3ff;
  }
  canvas { display: block; }
  #hud {
    position: fixed;
    left: 14px;
    bottom: 12px;
    color: rgba(255,255,255,0.78);
    font: 14px system-ui, sans-serif;
    text-shadow: 0 1px 2px rgba(0,0,0,0.45);
    pointer-events: none;
    user-select: none;
  }
</style>
</head>
<body>
<div id="hud">Drag to orbit • Scroll to zoom</div>

<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js"></script>
<script>
function ensureThree(cb) {
  if (typeof THREE !== "undefined") {
    cb();
    return;
  }

  const urls = [
    "https://unpkg.com/three@0.128.0/build/three.min.js",
    "https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js"
  ];

  function tryLoad(i) {
    if (i >= urls.length) {
      alert("Could not load Three.js from CDN. Please check your internet connection and refresh.");
      return;
    }

    const s = document.createElement("script");
    s.src = urls[i];
    s.onload = cb;
    s.onerror = () => tryLoad(i + 1);
    document.head.appendChild(s);
  }

  tryLoad(0);
}

function init() {
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xbfe3ff);
  scene.fog = new THREE.Fog(0xbfe3ff, 70, 180);

  const camera = new THREE.PerspectiveCamera(48, window.innerWidth / window.innerHeight, 0.1, 500);

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.outputEncoding = THREE.sRGBEncoding;
  renderer.domElement.style.touchAction = "none";
  document.body.appendChild(renderer.domElement);

  scene.add(new THREE.AmbientLight(0xffffff, 0.38));

  const hemi = new THREE.HemisphereLight(0xcfe8ff, 0x4a5c72, 0.65);
  scene.add(hemi);

  const sun = new THREE.DirectionalLight(0xfff2cf, 1.15);
  sun.position.set(-34, 52, 24);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  sun.shadow.camera.left = -70;
  sun.shadow.camera.right = 70;
  sun.shadow.camera.top = 70;
  sun.shadow.camera.bottom = -70;
  sun.shadow.camera.near = 1;
  sun.shadow.camera.far = 220;
  sun.shadow.bias = -0.00085;
  sun.target.position.set(0, 8, 4);
  scene.add(sun);
  scene.add(sun.target);

  const voxelGeo = new THREE.BoxGeometry(1, 1, 1);

  class VoxelBuilder {
    constructor() {
      this.items = [];
    }

    add(x, bottomY, z, sx = 1, sy = 1, sz = 1, color = 0xffffff, rotY = 0) {
      this.items.push({ x, bottomY, z, sx, sy, sz, color, rotY });
    }

    build() {
      if (this.items.length === 0) return new THREE.Object3D();

      const material = new THREE.MeshPhongMaterial({
        vertexColors: true,
        shininess: 10,
        specular: new THREE.Color(0x222222)
      });

      const mesh = new THREE.InstancedMesh(voxelGeo, material, this.items.length);
      const dummy = new THREE.Object3D();
      const c = new THREE.Color();

      this.items.forEach((v, i) => {
        dummy.position.set(v.x, v.bottomY + v.sy / 2, v.z);
        dummy.scale.set(v.sx, v.sy, v.sz);
        dummy.rotation.set(0, v.rotY, 0);
        dummy.updateMatrix();
        mesh.setMatrixAt(i, dummy.matrix);
        mesh.setColorAt(i, c.set(v.color));
      });

      mesh.instanceMatrix.needsUpdate = true;
      if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;

      mesh.castShadow = true;
      mesh.receiveShadow = true;

      return mesh;
    }
  }

  function pr(x, y) {
    const n = Math.sin(x * 127.1 + y * 311.7) * 43758.5453;
    return n - Math.floor(n);
  }

  const world = new VoxelBuilder();

  // Deep sea base.
  world.add(0, -6, 0, 220, 5, 220, 0x163e5d);

  // Harbor quay ground.
  for (let x = -31; x <= 31; x += 2) {
    for (let z = 15; z <= 35; z += 2) {
      const check = (Math.abs(Math.floor(x / 2)) + Math.floor(z / 2)) % 2;
      world.add(x, 0, z, 2, 1, 2, check ? 0x8f9aa8 : 0x818a97);
    }
  }

  // Quay wall and fenders.
  for (let x = -30; x <= 30; x += 2) {
    world.add(x, -2, 14, 2, 2, 1.6, 0x535e6e);
    world.add(x, 0.15, 13.8, 1.2, 0.45, 0.18, 0x232a35);
  }

  // Bollards.
  for (let x = -24; x <= 24; x += 8) {
    world.add(x, 1, 14.3, 0.55, 1.3, 0.55, 0x33404f);
  }

  // Breakwater.
  for (let x = -31; x <= -9; x += 2) {
    for (const z of [-20, -18]) {
      world.add(x, -2, z, 2, 2, 2, 0x566170);
      world.add(x, 0, z, 2, 2, 2, 0x828d9b);
    }
  }

  // Lighthouse.
  const lx = -24;
  const lz = -19;
  world.add(lx, 2, lz, 4.2, 2, 4.2, 0x8f9aa8);

  for (let y = 4; y < 18; y++) {
    const stripe = Math.floor((y - 4) / 2) % 2 === 0 ? 0xf5f7fb : 0xc7443b;
    world.add(lx, y, lz, 2.4, 1, 2.4, stripe);
  }

  world.add(lx, 18, lz, 1.8, 2.2, 1.8, 0xffe27a);
  world.add(lx, 20.2, lz, 1.6, 0.6, 1.6, 0x772b29);
  world.add(lx, 20.8, lz, 0.2, 0.8, 0.2, 0x333333);

  const lighthouseLight = new THREE.PointLight(0xffe6b0, 0.75, 55);
  lighthouseLight.position.set(lx, 19, lz);
  scene.add(lighthouseLight);

  function addTree(x, z) {
    world.add(x, 1, z, 0.45, 2.2, 0.45, 0x5a3a22);
    world.add(x, 3.2, z, 2.2, 1.2, 2.2, 0x3f8f47);
    world.add(x, 4.4, z, 1.4, 1.0, 1.4, 0x53a35b);
  }

  for (let x = -29; x <= -21; x += 4) addTree(x, 17);
  addTree(-29, 19);
  addTree(-25, 19);

  function addBuilding(cx, cz, sx, sz, h, bottomY, wall, roof) {
    world.add(cx, bottomY, cz, sx, h, sz, wall);
    world.add(cx, bottomY + h, cz, sx + 0.22, 0.45, sz + 0.22, roof);

    if (sx > 6 && sz > 4) {
      world.add(cx, bottomY + h + 0.45, cz, sx - 2.8, 0.5, sz - 2, roof);
      world.add(cx, bottomY + h + 0.95, cz, sx - 5, 0.45, sz - 3, roof);
    }
  }

  function addFrontWindows(cx, cz, sx, sz, h, bottomY) {
    const frontZ = cz - sz / 2 - 0.04;
    for (let xi = cx - sx / 2 + 0.9; xi <= cx + sx / 2 - 0.9; xi += 1.7) {
      for (let yi = bottomY + 1.1; yi <= bottomY + h - 1.0; yi += 1.8) {
        const lit = pr(xi, yi) < 0.18;
        world.add(xi, yi, frontZ, 0.58, 0.8, 0.08, lit ? 0xffd58a : 0x67a6cf);
      }
    }
  }

  function addDoor(cx, cz, sz, bottomY) {
    world.add(cx, bottomY, cz - sz / 2 - 0.05, 1.2, 2.1, 0.1, 0x442a16);
  }

  function addFlagPole(x, bottomY, z, color) {
    world.add(x, bottomY, z, 0.08, 3.4, 0.08, 0x33383f);
    world.add(x + 0.45, bottomY + 2.5, z, 0.9, 0.6, 0.08, color);
    world.add(x + 0.45, bottomY + 1.9, z, 0.9, 0.6, 0.08, 0xf7ead0);
  }

  // Large warehouses.
  addBuilding(-17, 22, 11, 7, 7.5, 1, 0xa2533b, 0x3d414a);
  addFrontWindows(-17, 22, 11, 7, 7.5, 1);
  addDoor(-17, 22, 7, 1);
  world.add(-13, 8.5, 22, 1, 3, 1, 0x33373d);
  addFlagPole(-17, 9, 22, 0xe63946);

  addBuilding(21, 22, 9, 6, 6, 1, 0x5a6f86, 0x38424e);
  addFrontWindows(21, 22, 9, 6, 6, 1);
  addDoor(21, 22, 6, 1);

  // Houses.
  function addHouse(cx, cz, sx, sz, h, wall, roof) {
    world.add(cx, 1, cz, sx, h, sz, wall);
    world.add(cx, 1 + h, cz, sx + 0.25, 0.45, sz + 0.25, roof);
    world.add(cx, 1 + h + 0.45, cz, sx - 1.1, 0.4, sz - 1.4, roof);

    const frontZ = cz - sz / 2 - 0.04;
    for (let xi = cx - sx / 2 + 0.6; xi <= cx + sx / 2 - 0.6; xi += 1.1) {
      const lit = pr(xi, cz) < 0.25;
      world.add(xi, 2.2, frontZ, 0.55, 0.75, 0.08, lit ? 0xffd58a : 0x74b5d9);
      world.add(xi, 3.5, frontZ, 0.55, 0.75, 0.08, lit ? 0xffd58a : 0x74b5d9);
    }

    world.add(cx, 1, frontZ, 0.9, 1.8, 0.08, 0x4f311f);
  }

  const houseWalls = [
    0xe9c46a,
    0xf3f0e1,
    0xc9ada0,
    0x9ec7cf,
    0xe5a47b,
    0x98a678,
    0xd9b8c4,
    0x82b6c9
  ];

  const roofColors = [
    0x8d322f,
    0x5e4535,
    0x2f4858,
    0x7d5343
  ];

  let houseIndex = 0;
  for (let cx = 5; cx <= 27; cx += 3.55) {
    addHouse(
      cx,
      21,
      3.2,
      5,
      4.2,
      houseWalls[houseIndex % houseWalls.length],
      roofColors[houseIndex % roofColors.length]
    );
    houseIndex++;
  }

  // Clock tower.
  world.add(18, 1, 26, 3.5, 9, 3.5, 0xcfc7bd);
  world.add(18, 10, 26, 3.8, 0.6, 3.8, 0x6d4739);
  world.add(18, 10.6, 26, 2.2, 2.5, 2.2, 0xcfc7bd);
  world.add(18, 13.1, 26, 2.4, 0.4, 2.4, 0x6d4739);
  world.add(18, 13.5, 26, 1.5, 1.2, 1.5, 0x6d4739);
  world.add(18, 12, 24.25, 0.8, 0.8, 0.1, 0xf5f2ea);
  world.add(18, 12, 24.17, 0.08, 0.55, 0.05, 0x222222);
  world.add(18, 12, 24.17, 0.55, 0.08, 0.05, 0x222222);
  addFlagPole(18, 14.1, 26, 0x2a9d8f);

  // Distant city blocks.
  for (let x = -30; x <= 30; x += 3.2) {
    const h = 2.6 + pr(x, 1) * 3.2;
    const wall = houseWalls[Math.floor((x + 40) * 0.777) % houseWalls.length];
    const roof = roofColors[Math.floor((x + 11) * 1.23) % roofColors.length];
    addBuilding(x, 30, 3.0, 4, h, 1, wall, roof);
  }

  for (let x = -28; x <= 28; x += 4.4) {
    const h = 2.2 + pr(x, 5) * 2.5;
    const wall = houseWalls[Math.floor((x + 55) * 0.41) % houseWalls.length];
    const roof = roofColors[Math.floor((x + 3) * 0.81) % roofColors.length];
    addBuilding(x, 33, 3.8, 4, h, 1, wall, roof);
  }

  // Cranes.
  function addCrane(cx, cz) {
    world.add(cx, 1, cz, 2.5, 0.5, 2.0, 0x4e3520);

    for (let y = 1; y < 5; y += 0.5) {
      world.add(cx, y, cz, 0.4, 0.5, 0.4, 0x6b4a2d);
    }

    world.add(cx - 1.5, 5, cz, 4, 0.25, 0.4, 0x6b4a2d);
    world.add(cx - 3.5, 5.25, cz, 0.3, 0.25, 0.3, 0x333333);

    for (let y = 3.1; y < 5; y += 0.2) {
      world.add(cx - 3.5, y, cz, 0.08, 0.2, 0.08, 0x7a6248);
    }

    world.add(cx - 3.5, 2.0, cz, 1.0, 1.0, 1.0, 0x8d653c);
    world.add(cx - 3.5, 2.15, cz + 0.51, 0.8, 0.15, 0.04, 0x5e3c20);
    world.add(cx - 3.5, 2.15, cz - 0.51, 0.8, 0.15, 0.04, 0x5e3c20);
  }

  addCrane(-8, 17);
  addCrane(15, 18);

  // Market stalls.
  function addStall(cx, cz, stripe1, stripe2) {
    const posts = [[-1, -1], [1, -1], [-1, 1], [1, 1]];
    for (const [dx, dz] of posts) {
      world.add(cx + dx, 1, cz + dz, 0.12, 1.3, 0.12, 0x5a3a22);
    }

    for (let xi = -1.2; xi <= 1.2; xi += 0.5) {
      const color = Math.round((xi + 2) * 2) % 2 === 0 ? stripe1 : stripe2;
      world.add(cx + xi, 2.2, cz, 0.55, 0.18, 2.2, color);
    }

    world.add(cx - 0.45, 1, cz - 0.2, 0.7, 0.7, 0.7, 0x9a6b3a);
    world.add(cx + 0.35, 1, cz + 0.15, 0.6, 0.6, 0.6, 0x8a5f32);
    world.add(cx + 0.8, 1, cz - 0.25, 0.65, 0.9, 0.65, 0x8a4b24);
    world.add(cx - 0.85, 1, cz + 0.3, 0.6, 0.9, 0.6, 0x8a4b24);
  }

  addStall(-13, 17, 0xe76f51, 0xf7ead0);
  addStall(13, 19, 0x2a9d8f, 0xf7ead0);

  // Cargo on quay.
  function addCrate(x, z, level = 0) {
    const y = 1 + level * 1.1;
    world.add(x, y, z, 1.05, 1.05, 1.05, 0x9c6f44);
    world.add(x, y + 0.12, z + 0.53, 0.85, 0.15, 0.02, 0x5e3c20);
    world.add(x, y + 0.12, z - 0.53, 0.85, 0.15, 0.02, 0x5e3c20);
  }

  function addBarrel(x, z) {
    world.add(x, 1, z, 0.85, 1.0, 0.85, 0x8a4b24);
    world.add(x, 1.15, z, 0.9, 0.12, 0.9, 0x4e2a12);
    world.add(x, 1.45, z, 0.9, 0.12, 0.9, 0x4e2a12);
  }

  const cargoPos = [
    [-3, 15.8, 0],
    [-2, 15.8, 0],
    [-1, 15.8, 0],
    [1, 15.8, 0],
    [2, 15.8, 0],
    [0, 16.6, 0],
    [-3, 16.6, 0],
    [2, 16.6, 0],
    [-1, 16.6, 1],
    [0, 16.6, 1],
    [-2, 15.8, 1]
  ];

  for (const [x, z, level] of cargoPos) addCrate(x, z, level);

  const barrelPos = [
    [3.3, 15.8],
    [4.1, 16.4],
    [3.8, 17.1],
    [4.6, 15.9]
  ];

  for (const [x, z] of barrelPos) addBarrel(x, z);

  // Gangplank.
  for (let zz = 12.7; zz <= 14.5; zz += 0.2) {
    world.add(0, 1.18 - (zz - 12.7) * 0.06, zz, 1.2, 0.15, 0.22, 0x6a4526);
  }

  // Mooring ropes.
  for (const x of [-7, -3, 3, 7]) {
    for (let zz = 13.2; zz <= 14.2; zz += 0.2) {
      const p = (zz - 13.2) / 1.0;
      world.add(x, 1.02 - Math.sin(p * Math.PI) * 0.12, zz, 0.12, 0.12, 0.2, 0x8f7757);
    }
  }

  // Small fishing boats.
  function addFishingBoat(x, z, hullColor) {
    world.add(x, -0.9, z, 3.2, 1.2, 1.0, hullColor);
    world.add(x, 0.3, z, 2.2, 0.15, 0.7, 0x8b5e34);
    world.add(x, 0.45, z, 0.12, 2.0, 0.12, 0x3b2417);
    world.add(x + 1.2, 0.2, z, 0.12, 0.6, 0.12, 0x3b2417);
    world.add(x, 2.45, z, 0.08, 0.6, 0.08, 0x333333);
    world.add(x + 0.35, 2.15, z, 0.7, 0.5, 0.08, 0xe63946);
  }

  addFishingBoat(-13, -5, 0x557a33);
  addFishingBoat(16, -9, 0x844d2a);
  addFishingBoat(-18, -10, 0x3a5f88);

  const worldMesh = world.build();
  worldMesh.castShadow = true;
  worldMesh.receiveShadow = true;
  scene.add(worldMesh);

  // Animated voxel sea.
  const water = new VoxelBuilder();
  const seaColors = [
    0x2f88bd,
    0x2678ab,
    0x1f6e9e,
    0x3592c5,
    0x1a608f
  ];

  for (let x = -24; x <= 24; x++) {
    for (let z = -26; z <= 13; z++) {
      const c = seaColors[(Math.abs(x) + Math.abs(z)) % seaColors.length];
      water.add(x, -1, z, 1, 1, 1, c);
    }
  }

  const waterMesh = water.build();
  waterMesh.castShadow = false;
  waterMesh.receiveShadow = false;
  scene.add(waterMesh);

  const waterData = water.items.map(v => ({
    x: v.x,
    z: v.z,
    bottom: v.bottomY,
    sx: v.sx,
    sy: v.sy,
    sz: v.sz
  }));

  // Sailing ship.
  const shipGroup = new THREE.Group();
  const ship = new VoxelBuilder();

  const hullColor = 0x5a3620;
  const hullDark = 0x23140a;
  const deckColor = 0x8c5a32;
  const woodColor = 0x3a2316;
  const sailCream = 0xf7f0df;
  const sailRed = 0xd25b47;
  const sailBlue = 0x4f7fa6;

  const widths = [
    0.70, 1.10, 1.55, 1.95, 2.35,
    2.70, 2.90, 3.00, 3.00, 3.00,
    3.00, 3.00, 3.00, 3.00, 3.00,
    2.90, 2.60, 2.20, 1.60, 0.90,
    0.20
  ];

  for (let i = 0; i < widths.length; i++) {
    const x = -10 + i;
    const w = Math.max(0.15, widths[i]);

    ship.add(x, -1.9, 0, 1, 3.0, 2 * w, hullColor);
    ship.add(x, -1.9, 0, 1, 0.5, 2 * w + 0.05, hullDark);
    ship.add(x, 1.05, 0, 1, 0.18, Math.max(0.18, 2 * w - 0.35), deckColor);

    if (w > 0.6) {
      ship.add(x, 1.23, w - 0.15, 1, 0.35, 0.22, 0x674325);
      ship.add(x, 1.23, -w + 0.15, 1, 0.35, 0.22, 0x674325);
    }
  }

  // Stern castle.
  for (let x = -10; x <= -6; x++) {
    ship.add(x, 1.15, 0, 1, 1.3, 4.4, 0x70432a);
    ship.add(x, 2.45, 0, 1, 0.2, 3.4, 0x8b5e34);

    if (x > -10 && x < -6) {
      ship.add(x, 1.6, -2.15, 0.7, 0.7, 0.1, 0xffe19a);
      ship.add(x, 1.6, 2.15, 0.7, 0.7, 0.1, 0xffe19a);
    }
  }

  // Forecastle.
  for (let x = 7; x <= 10; x++) {
    const w = Math.max(0.25, 2 - (x - 6) * 0.45);
    ship.add(x, 1.15, 0, 1, 1.0, 2 * w, 0x70432a);
  }

  // Bow cargo on deck.
  function shipCrate(x, z, level = 0) {
    const y = 1.23 + level * 1.0;
    ship.add(x, y, z, 1.0, 1.0, 1.0, 0x976941);
    ship.add(x, y + 0.12, z + 0.51, 0.8, 0.15, 0.04, 0x5b391d);
    ship.add(x, y + 0.12, z - 0.51, 0.8, 0.15, 0.04, 0x5b391d);
  }

  function shipBarrel(x, z) {
    ship.add(x, 1.23, z, 0.7, 0.9, 0.7, 0x8a4b24);
    ship.add(x, 1.4, z, 0.75, 0.1, 0.75, 0x43240f);
    ship.add(x, 1.68, z, 0.75, 0.1, 0.75, 0x43240f);
  }

  shipCrate(3, 0.4);
  shipCrate(3, -0.7);
  shipCrate(4, -0.15);
  shipCrate(-2, 0.35);
  shipCrate(-2, -0.7);
  shipCrate(-2, 0.35, 1);
  shipBarrel(0, -1.0);
  shipBarrel(0.8, 0.9);
  shipBarrel(-0.8, 0.9);

  // Bowsprit as stacked voxel steps.
  for (let i = 0; i <= 10; i++) {
    const t = i / 10;
    ship.add(10 + 4.5 * t, 2.3 + 2.3 * t, 0, 0.7, 0.15, 0.15, woodColor);
  }

  // Masts, yards, sails.
  function addMast(x, topY) {
    ship.add(x, 0.9, 0, 0.24, topY - 0.9, 0.24, woodColor);
    ship.add(x, topY, 0, 0.1, 0.4, 0.1, woodColor);
  }

  function addYard(x, y, w) {
    ship.add(x, y, 0, w, 0.22, 0.28, 0x2b1b11);
  }

  function addSail(x, y, h, w, c1, c2) {
    for (let yy = 0; yy < h; yy += 1) {
      ship.add(x, y + yy, 0, w, 1, 0.18, yy % 2 === 0 ? c1 : c2);
    }
  }

  // Foremast.
  addMast(5, 11.8);
  addYard(5, 4.4, 3.9);
  addSail(5, 4.5, 3, 3.5, sailCream, sailRed);
  addYard(5, 7.7, 2.9);
  addSail(5, 7.8, 2, 2.6, sailCream, sailRed);
  addYard(5, 9.9, 1.8);

  // Mainmast.
  addMast(0, 13.8);
  addYard(0, 4.4, 5.8);
  addSail(0, 4.5, 4, 5.5, sailCream, sailRed);
  addYard(0, 8.7, 4.0);
  addSail(0, 8.8, 2, 3.8, sailCream, sailBlue);
  addYard(0, 11.0, 2.5);

  // Mizzenmast.
  addMast(-5, 9.8);
  addYard(-5, 3.9, 3.4);
  addSail(-5, 4.0, 3, 3.0, sailCream, sailRed);
  addYard(-5, 7.1, 2.3);
  addSail(-5, 7.2, 2, 1.9, sailCream, sailRed);

  // Stern flag.
  ship.add(-10.7, 2.5, 0, 0.08, 5.0, 0.08, 0x333333);
  ship.add(-10.1, 6.5, 0, 1.2, 0.7, 0.08, 0xe63946);
  ship.add(-10.1, 5.8, 0, 1.2, 0.7, 0.08, 0xf1faee);

  // Bow flag.
  ship.add(14.9, 4.7, 0, 0.08, 0.9, 0.08, 0x333333);
  ship.add(15.35, 4.75, 0, 0.75, 0.45, 0.08, 0x2a9d8f);

  // Ship pennant.
  ship.add(7, 10.45, 0, 0.55, 0.2, 0.06, 0xf2a65a);

  const shipMesh = ship.build();
  shipMesh.castShadow = true;
  shipMesh.receiveShadow = true;
  shipGroup.add(shipMesh);
  shipGroup.position.set(0, 0, 10);
  scene.add(shipGroup);

  // Clouds.
  const clouds = new VoxelBuilder();

  function addCloud(cx, cy, cz) {
    const cells = [
      [0, 0], [1, 0], [-1, 0], [0, 1], [0, -1],
      [2, 0], [-2, 0], [1, 1], [-1, -1], [1, -1],
      [-1, 1], [0, 2], [0, -2]
    ];

    cells.forEach(([dx, dz], i) => {
      const sx = 1.8 + (i % 3) * 0.35;
      const sz = 1.5 + ((i + 1) % 4) * 0.25;
      const color = i % 4 === 0 ? 0xeef4ff : 0xffffff;
      const yy = cy + (Math.abs(dx) + Math.abs(dz) === 0 ? 0.7 : 0);
      clouds.add(cx + dx * 1.8, yy, cz + dz * 1.8, sx, 1.2, sz, color);
    });
  }

  addCloud(-28, 24, -10);
  addCloud(14, 27, -24);
  addCloud(28, 21, 3);
  addCloud(-8, 25, -32);
  addCloud(24, 24, -7);
  addCloud(-34, 22, 8);

  const cloudMesh = clouds.build();
  cloudMesh.castShadow = false;
  cloudMesh.receiveShadow = false;
  cloudMesh.material.shininess = 0;
  scene.add(cloudMesh);

  // Birds.
  const birds = [];
  const birdBodyMat = new THREE.MeshPhongMaterial({ color: 0xffffff });
  const birdWingMat = new THREE.MeshPhongMaterial({ color: 0xf4f8ff });

  function makeBird(seed) {
    const g = new THREE.Group();

    const body = new THREE.Mesh(voxelGeo, birdBodyMat);
    body.scale.set(0.55, 0.32, 1.15);
    g.add(body);

    const leftWing = new THREE.Mesh(voxelGeo, birdWingMat);
    leftWing.scale.set(0.85, 0.12, 0.35);
    leftWing.position.set(-0.75, 0, 0);
    g.add(leftWing);

    const rightWing = new THREE.Mesh(voxelGeo, birdWingMat);
    rightWing.scale.set(0.85, 0.12, 0.35);
    rightWing.position.set(0.75, 0, 0);
    g.add(rightWing);

    g.userData = {
      angle: seed * 0.9,
      radius: 22 + seed * 3,
      y: 13 + seed * 0.8,
      speed: 0.18 + seed * 0.03,
      phase: seed * 1.7
    };

    return g;
  }

  for (let i = 0; i < 6; i++) {
    const b = makeBird(i);
    b.castShadow = false;
    scene.add(b);
    birds.push(b);
  }

  // Manual orbit camera.
  let theta = Math.PI * 0.94;
  let phi = 1.04;
  let radius = 62;
  const target = new THREE.Vector3(-1, 6.5, 4);

  let dragging = false;
  let lastX = 0;
  let lastY = 0;
  let autoRotate = true;
  let idleTimer = null;

  function updateCamera() {
    const x = target.x + radius * Math.sin(phi) * Math.sin(theta);
    const y = target.y + radius * Math.cos(phi);
    const z = target.z + radius * Math.sin(phi) * Math.cos(theta);
    camera.position.set(x, y, z);
    camera.lookAt(target);
  }

  function scheduleAutoRotate() {
    clearTimeout(idleTimer);
    idleTimer = setTimeout(() => {
      if (!dragging) autoRotate = true;
    }, 3800);
  }

  updateCamera();

  const canvas = renderer.domElement;

  canvas.addEventListener("pointerdown", (e) => {
    dragging = true;
    autoRotate = false;
    lastX = e.clientX;
    lastY = e.clientY;
    try {
      canvas.setPointerCapture(e.pointerId);
    } catch (_) {}
  });

  canvas.addEventListener("pointermove", (e) => {
    if (!dragging) return;

    const dx = e.clientX - lastX;
    const dy = e.clientY - lastY;
    lastX = e.clientX;
    lastY = e.clientY;

    theta -= dx * 0.0055;
    phi = Math.max(0.22, Math.min(1.42, phi - dy * 0.0055));
    updateCamera();
  });

  window.addEventListener("pointerup", () => {
    dragging = false;
    scheduleAutoRotate();
  });

  window.addEventListener("pointercancel", () => {
    dragging = false;
    scheduleAutoRotate();
  });

  canvas.addEventListener("wheel", (e) => {
    e.preventDefault();
    radius *= Math.exp(e.deltaY * 0.001);
    radius = Math.max(18, Math.min(130, radius));
    updateCamera();
    scheduleAutoRotate();
  }, { passive: false });

  window.addEventListener("resize", () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

  canvas.addEventListener("contextmenu", (e) => e.preventDefault());

  const waterDummy = new THREE.Object3D();

  function updateWater(t) {
    waterDummy.rotation.set(0, 0, 0);

    for (let i = 0; i < waterData.length; i++) {
      const b = waterData[i];
      const wave =
        Math.sin(t * 1.45 + b.x * 0.33 + b.z * 0.26) * 0.10 +
        Math.sin(t * 0.78 - b.z * 0.19) * 0.07;

      waterDummy.position.set(b.x, b.bottom + wave + b.sy / 2, b.z);
      waterDummy.scale.set(b.sx, b.sy, b.sz);
      waterDummy.updateMatrix();
      waterMesh.setMatrixAt(i, waterDummy.matrix);
    }

    waterMesh.instanceMatrix.needsUpdate = true;
  }

  const clock = new THREE.Clock();

  function animate() {
    requestAnimationFrame(animate);

    const dt = Math.min(clock.getDelta(), 0.05);
    const t = clock.elapsedTime;

    if (autoRotate && !dragging) {
      theta += dt * 0.055;
      updateCamera();
    }

    updateWater(t);

    shipGroup.position.y = Math.sin(t * 0.88) * 0.09;
    shipGroup.rotation.z = Math.sin(t * 0.55) * 0.013;
    shipGroup.rotation.x = Math.sin(t * 0.73) * 0.007;
    shipGroup.rotation.y = Math.sin(t * 0.31) * 0.003;

    cloudMesh.position.x = Math.sin(t * 0.025) * 2.6;

    birds.forEach((b) => {
      const u = b.userData;
      u.angle += dt * u.speed;

      b.position.set(
        Math.cos(u.angle) * u.radius - 2,
        u.y + Math.sin(u.angle * 1.3 + u.phase) * 1.2,
        4 + Math.sin(u.angle) * u.radius * 0.55
      );

      b.rotation.y = -u.angle + Math.PI * 0.5;

      const flap = Math.sin(t * 8.5 + u.phase) * 0.65;
      b.children[1].rotation.z = flap;
      b.children[2].rotation.z = -flap;
    });

    renderer.render(scene, camera);
  }

  animate();
}

ensureThree(init);
</script>
</body>
</html>
```