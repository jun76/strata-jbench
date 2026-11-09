Save this as `harbor-voxel.html` and open it in Chrome. It uses Three.js from a CDN, creates a voxel harbor and sailing ship, and renders immediately. Drag with the mouse to orbit, scroll to zoom.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Voxel Harbor — Sailing Ship Calling at Harbor</title>
  <style>
    html, body {
      margin: 0;
      height: 100%;
      overflow: hidden;
      background: #0b1e30;
    }
    canvas {
      display: block;
      touch-action: none;
      cursor: grab;
    }
    canvas:active {
      cursor: grabbing;
    }
    #hint {
      position: fixed;
      left: 14px;
      bottom: 14px;
      color: #fff;
      font: 14px system-ui, sans-serif;
      opacity: 0.72;
      pointer-events: none;
      text-shadow: 0 1px 2px rgba(0,0,0,0.45);
    }
  </style>
</head>
<body>
  <div id="hint">drag to orbit · scroll to zoom</div>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>

  <script>
(function () {
  if (!window.THREE) {
    document.body.innerHTML =
      '<div style="color:#fff;padding:24px;font:16px system-ui;">Failed to load three.js from the CDN. Check your internet connection.</div>';
    return;
  }

  // Deterministic pseudo-random for reproducible voxel placement.
  let seed = 987654321;
  function rnd() {
    seed = (seed * 1664525 + 1013904223) & 0x7fffffff;
    return seed / 0x7fffffff;
  }
  function rr(a, b) { return a + rnd() * (b - a); }
  function ri(a, b) { return Math.floor(rr(a, b + 1)); }
  function pick(arr) { return arr[Math.floor(rnd() * arr.length)]; }

  const cube = new THREE.BoxGeometry(1, 1, 1);

  const materialCache = new Map();
  function getMat(color) {
    let m = materialCache.get(color);
    if (!m) {
      m = new THREE.MeshStandardMaterial({
        color,
        roughness: 0.88,
        metalness: 0.03,
        flatShading: true
      });
      materialCache.set(color, m);
    }
    return m;
  }

  function addBlock(parent, x, y, z, sx, sy, sz, color, rx = 0, ry = 0, rz = 0) {
    const mesh = new THREE.Mesh(cube, getMat(color));
    mesh.position.set(x, y, z);
    mesh.scale.set(sx, sy, sz);
    mesh.rotation.set(rx, ry, rz);
    parent.add(mesh);
    return mesh;
  }

  class VoxelBatch {
    constructor(scene, material, capacity) {
      this.geometry = cube;
      this.material = material;
      this.capacity = capacity;
      this.mesh = new THREE.InstancedMesh(cube, material, capacity);
      this.mesh.count = 0;
      this.mesh.frustumCulled = false;
      this.dummy = new THREE.Object3D();
      this.color = new THREE.Color();
      this.count = 0;
      scene.add(this.mesh);
    }

    add(x, y, z, sx, sy, sz, color, rx = 0, ry = 0, rz = 0) {
      if (this.count >= this.capacity) return;

      this.dummy.position.set(x, y, z);
      this.dummy.scale.set(sx, sy, sz);
      this.dummy.rotation.set(rx, ry, rz);
      this.dummy.updateMatrix();

      this.mesh.setMatrixAt(this.count, this.dummy.matrix);
      this.mesh.setColorAt(this.count, this.color.set(color));
      this.count++;
    }

    finish() {
      this.mesh.count = this.count;
      this.mesh.instanceMatrix.needsUpdate = true;
      if (this.mesh.instanceColor) this.mesh.instanceColor.needsUpdate = true;
    }
  }

  // Scene, camera, renderer.
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x8fc3e8);
  scene.fog = new THREE.Fog(0x8fc3e8, 110, 260);

  const camera = new THREE.PerspectiveCamera(
    50,
    window.innerWidth / window.innerHeight,
    1,
    1200
  );

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(window.innerWidth, window.innerHeight);
  if (THREE.sRGBEncoding) renderer.outputEncoding = THREE.sRGBEncoding;
  document.body.appendChild(renderer.domElement);

  // Lights.
  const hemi = new THREE.HemisphereLight(0xbfe6ff, 0x53624a, 0.6);
  scene.add(hemi);

  const sun = new THREE.DirectionalLight(0xffd39b, 1.25);
  sun.position.set(65, 85, -35);
  scene.add(sun);

  const fill = new THREE.DirectionalLight(0x5687a5, 0.35);
  fill.position.set(-45, 35, 65);
  scene.add(fill);

  // Static voxel world batch.
  const batchMaterial = new THREE.MeshStandardMaterial({
    color: 0xffffff,
    roughness: 0.92,
    metalness: 0.02,
    flatShading: true
  });

  const batch = new VoxelBatch(scene, batchMaterial, 16000);
  const V = (...args) => batch.add(...args);

  const stone = [0x9b8f82, 0x887b6e, 0x746a5e, 0x6a6055];
  const sand = [0xd4bf7a, 0xc8b26d, 0xe2d39a];
  const grass = [0x679553, 0x5c8b46, 0x75a55f, 0x83a95f];

  // Harbor land base.
  V(0, -1, 27, 92, 10, 40, 0x6e5b41);

  // Stone quay edge.
  for (let x = -44; x <= 44; x += 1) {
    V(x, 2.0, 9.0, 1.1, 4.0, 1.1, pick(stone));
    if ((x & 1) === 0) {
      V(
        x + rr(-0.25, 0.25),
        0.45,
        8.35,
        rr(1.0, 1.7),
        1.3,
        1.0,
        pick(stone)
      );
    }
  }

  // Top voxel surface.
  for (let x = -44; x <= 44; x += 1) {
    for (let z = 10; z <= 46; z += 1) {
      const col = z < 13 ? pick(sand) : pick(grass);
      const yy = 3.5 + (rnd() < 0.08 ? 0.35 : 0);
      V(x, yy, z, 1, 1, 1, col);
    }
  }

  // Road.
  V(0, 4.08, 20, 86, 0.16, 4.2, 0xb49875);
  V(0, 4.22, 20, 86, 0.10, 1.1, 0xd6c29a);

  // Houses.
  function house(x, z, w, h, d, wall, roof) {
    V(x, 4 + h / 2, z, w, h, d, wall);

    // Stepped roof.
    V(x, 4 + h + 0.6, z, w + 1, 1, d + 1, roof);
    V(x, 4 + h + 1.55, z, w * 0.7, 1, d * 0.7, roof);

    // Chimney.
    V(x + w * 0.3, 4 + h + 2.7, z + d * 0.3, 1.1, 3.4, 1.1, 0x774f41);

    // Front/back windows.
    for (let yy = 5; yy < 4 + h; yy += 2) {
      for (let xx = -w / 2 + 1; xx <= w / 2 - 1; xx += 2) {
        V(x + xx, yy, z - d / 2 - 0.08, 0.9, 1.1, 0.15, 0xffd98c);
        V(x + xx, yy, z + d / 2 + 0.08, 0.9, 1.1, 0.15, 0xffd98c);
      }
    }

    // Side windows.
    for (let yy = 5; yy < 4 + h; yy += 2) {
      for (let zz = -d / 2 + 1; zz <= d / 2 - 1; zz += 2) {
        V(x - w / 2 - 0.08, yy, z + zz, 0.15, 1.1, 0.9, 0xffd98c);
        V(x + w / 2 + 0.08, yy, z + zz, 0.15, 1.1, 0.9, 0xffd98c);
      }
    }

    // Door.
    V(x, 4.7, z - d / 2 - 0.08, 1, 1.4, 0.15, 0x4b3724);
  }

  const walls = [0xd7c7ac, 0xc7aa8f, 0xaeb4c4, 0xd19b7b, 0xbfc1b3];
  const roofs = [0x8f3c30, 0x3f678c, 0x57745f, 0xb48942, 0x6d4f6f];

  for (let i = 0; i < 7; i++) {
    house(
      -34 + i * 10,
      24,
      7 + ri(0, 2),
      5 + ri(0, 2),
      6 + ri(0, 2),
      pick(walls),
      pick(roofs)
    );
  }

  for (let i = 0; i < 5; i++) {
    house(
      -20 + i * 12,
      30,
      8 + ri(0, 3),
      6 + ri(0, 3),
      7 + ri(0, 2),
      pick(walls),
      pick(roofs)
    );
  }

  // Warehouse near dock.
  const warehouseX = 16, warehouseZ = 14;
  V(warehouseX, 6.8, warehouseZ, 10, 5.6, 7, 0xb0997f);
  V(warehouseX, 9.9, warehouseZ, 11, 1.2, 8, 0x7c433a);
  V(warehouseX, 10.7, warehouseZ, 7, 0.8, 5.5, 0x6b352f);
  V(warehouseX, 5.4, warehouseZ - 3.55, 2.0, 2.4, 0.2, 0x553d28);
  for (let xx = warehouseX - 3; xx <= warehouseX + 3; xx += 3) {
    V(xx, 7.0, warehouseZ - 3.55, 1.0, 1.4, 0.2, 0xffd98c);
  }

  // Market stalls.
  for (let sx = -14; sx <= 14; sx += 8) {
    V(sx, 4.6, 17, 3, 1.2, 2, pick([0xa5764d, 0x8d6341, 0xb19a6a]));
    V(sx, 5.7, 17.25, 4, 0.3, 3.5, pick([0xc0453c, 0x3f678c, 0x679553]));
    for (let i = 0; i < 4; i++) {
      V(
        sx + rr(-1.2, 1.2),
        4.95,
        17 + rr(-0.6, 0.6),
        0.7,
        0.7,
        0.7,
        pick([0xd3b25a, 0xc0453c, 0x679553, 0x8d6341])
      );
    }
  }

  // Trees.
  function tree(x, z) {
    V(x, 5, z, 1, 2, 1, 0x695035);
    V(x, 7.4, z, 3, 3, 3, pick([0x4f8c46, 0x669d51]));
    V(x, 9.4, z, 2, 2, 2, pick([0x4f8c46, 0x669d51]));
  }

  for (let i = 0; i < 26; i++) {
    const x = rr(-42, 42);
    const z = i < 14 ? rr(12, 18) : rr(34, 44);
    if (x > 10 && z < 22) continue;
    tree(x, z);
  }

  // Lighthouse.
  const lx = -34, lz = 11;

  for (let i = 0; i < 16; i++) {
    V(
      lx + rr(-2.4, 2.4),
      rr(2.0, 3.8),
      lz + rr(-2.4, 2.4),
      rr(1.3, 2.3),
      rr(1.2, 2.0),
      rr(1.3, 2.3),
      pick(stone)
    );
  }

  for (let i = 0; i < 5; i++) {
    V(
      lx,
      5.5 + i * 1.8,
      lz,
      2.3,
      1.8,
      2.3,
      i % 2 ? 0xc0453c : 0xf1e3c6
    );
  }

  V(lx, 13.8, lz, 2.8, 1.0, 2.8, 0x4f585f);
  V(lx, 15.0, lz, 1.8, 1.6, 1.8, 0xfff1bc);
  V(lx, 16.0, lz, 2.4, 0.8, 2.4, 0xc0453c);
  V(lx, 16.8, lz, 0.3, 1.2, 0.3, 0xc0453c);

  const lanternLight = new THREE.PointLight(0xffe4a0, 1.3, 95, 2);
  lanternLight.position.set(lx, 15, lz);
  scene.add(lanternLight);

  // Dock flags.
  for (let fx = -8; fx <= 12; fx += 6) {
    V(fx, 5.6, 7, 0.12, 3.2, 0.12, 0x6b4f33);
    V(fx + 0.9, 6.8, 7, 1.8, 1.0, 0.12, pick([0xc0453c, 0x3f678c, 0xd3b25a]));
  }

  // Pier.
  V(1, 3.5, 6, 26, 1, 4, 0x956a42);

  for (let x = -11; x <= 13; x += 1) {
    V(x, 4.02, 6, 0.8, 0.1, 4, pick([0xa07246, 0x7d5737, 0x8b6340]));
  }

  for (let x = -10; x <= 12; x += 4) {
    V(x, 1.6, 4.4, 0.8, 3.8, 0.8, 0x5e3f28);
    V(x, 1.6, 7.6, 0.8, 3.8, 0.8, 0x5e3f28);
  }

  for (let x = -8; x <= 12; x += 4) {
    V(x, 4.5, 4.3, 0.85, 1, 0.85, 0x3b342c);
    if (x < 12) V(x + 2, 4.45, 4.3, 4.2, 0.08, 0.08, 0x9f8a72);
  }

  // Gangplank.
  V(-2, 4.15, 4.0, 1.3, 0.12, 1.4, 0xc2a071);
  V(-2, 4.55, 3.55, 1.3, 0.55, 0.1, 0x6b4b31);
  V(-2, 4.55, 4.45, 1.3, 0.55, 0.1, 0x6b4b31);

  // Cargo crates and barrels on dock.
  const crateColors = [0xa5764d, 0x8d6341, 0xb19a6a, 0x9e6149, 0x57745f];
  for (let i = 0; i < 38; i++) {
    const x = rr(-10, 12);
    const z = rr(5.2, 7.6);
    const s = rr(0.8, 1.6);
    V(x, 4 + s / 2, z, s, s, s, pick(crateColors));
  }

  for (let i = 0; i < 18; i++) {
    const x = rr(-12, 14);
    const z = rr(5.2, 7.8);
    V(x, 4.8, z, 1, 1.2, 1, pick([0x6a492f, 0x7e5736]));
  }

  // Crane.
  const cx = 8, cz = 6.5;
  V(cx, 4.5, cz, 2.6, 1, 2.6, 0x6b4f33);
  V(cx, 7.5, cz, 1, 4, 1, 0x956a42);
  V(cx, 9.7, cz, 1.2, 1.6, 1.2, 0x6b4f33);

  V(cx - 2.6, 9.3, cz, 2.5, 0.35, 0.5, 0x7a5b3d, 0, 0, 0.15);
  V(cx - 3.8, 10.0, cz, 1.4, 1.4, 1.4, 0x47403a);

  V(cx + 4.0, 9.1, cz, 6.5, 0.35, 0.5, 0x7a5b3d, 0, 0, -0.22);
  V(cx + 6.9, 7.6, cz, 0.18, 2.2, 0.18, 0x3a3531);
  V(cx + 6.9, 5.7, cz, 1.4, 1.4, 1.4, 0x9e6149);

  // Breakwater rocks.
  for (let i = 0; i < 70; i++) {
    const right = i < 35;
    const x = right ? rr(18, 34) : rr(-34, -18);
    const z = rr(4.5, 8);
    V(
      x,
      rr(0.3, 2),
      z,
      rr(1.4, 2.6),
      rr(1, 2.2),
      rr(1.4, 2.6),
      pick(stone)
    );
  }

  // Small boats and buoy.
  function smallBoat(x, z) {
    V(x, -0.2, z, 4.2, 1.3, 1.6, 0x2b4a6a);
    V(x, 0.7, z, 3.4, 0.4, 1.2, 0xc2a071);
    V(x, 2.7, z, 0.12, 3.5, 0.12, 0x8c6b47);
    V(x, 3.2, z, 0.3, 2.2, 2.0, 0xf3ead2);
    V(x + 1.0, 3.0, z, 0.18, 0.45, 0.8, 0xc0453c);
  }

  smallBoat(-24, -1);
  smallBoat(-29, -2);

  V(16, -0.2, -10, 1.2, 2.0, 1.2, 0xc0453c);
  V(16, 1.2, -10, 0.7, 0.8, 0.7, 0xf3ead2);

  // Foam.
  for (let i = 0; i < 60; i++) {
    V(
      rr(-18, 26),
      0.62,
      rr(-4.5, 3.5),
      rr(0.8, 1.7),
      0.16,
      rr(0.8, 1.7),
      0xe9f5ff
    );
  }

  for (let i = 0; i < 70; i++) {
    V(
      rr(-42, 42),
      0.75,
      rr(8.2, 9.6),
      rr(0.8, 1.8),
      0.18,
      rr(0.8, 1.8),
      0xe9f5ff
    );
  }

  // Clouds.
  for (let i = 0; i < 40; i++) {
    const x = rr(-90, 90);
    const z = rr(-90, 90);
    const y = 38 + rr(0, 16);

    if (Math.hypot(x, z) < 30) continue;

    V(x, y, z, rr(8, 18), rr(2, 4), rr(6, 15), 0xffffff);
    V(
      x + rr(-5, 5),
      y + rr(0, 2),
      z + rr(-5, 5),
      rr(4, 12),
      rr(1.5, 3),
      rr(3, 9),
      0xf8fbff
    );
  }

  batch.finish();

  // Animated ship group.
  const shipGroup = new THREE.Group();
  scene.add(shipGroup);

  const B = (...args) => addBlock(shipGroup, ...args);

  const hullDark = 0x243d58;
  const hullMid = 0x3f6d8f;
  const deckWood = 0xc9a678;
  const sail = 0xf4ead4;
  const mastWood = 0x8e6e50;
  const woodDark = 0x5c4230;
  const gold = 0xd0b25e;
  const red = 0xc0453c;
  const rig = 0x2f2f35;
  const dark = 0x2a241f;

  // Hull.
  B(0, -3.5, 0, 24, 1.2, 3.0, hullDark);
  B(-15.0, -2.4, 0, 1.3, 3.0, 1.6, hullDark);
  B(0, -1.2, 0, 26, 3.2, 6.2, hullDark);
  B(0, 1.3, 0, 27.2, 3.6, 6.6, hullMid);
  B(0, -0.3, 0, 27.8, 0.55, 7.0, gold);

  // Deck and rails.
  B(0, 3.7, 0, 24.8, 0.75, 5.6, deckWood);
  B(0, 4.1, 3.0, 26.5, 0.5, 0.25, mastWood);
  B(0, 4.1, -3.0, 26.5, 0.5, 0.25, mastWood);

  // Bow taper.
  for (let i = 0; i < 8; i++) {
    B(
      13 + i * 1.4,
      1.2 + i * 0.22,
      0,
      2.0,
      3.3 - i * 0.33,
      6.0 - i * 0.65,
      i % 2 ? hullMid : hullDark
    );
  }

  B(25.5, 2.1, 0, 2.0, 1.6, 1.6, hullDark, 0, 0.65, 0);

  // Bowsprit.
  B(20, 4.9, 0, 8, 0.4, 0.4, mastWood, 0, 0, 0.17);

  // Stern.
  B(-14.5, 1.3, 0, 3.0, 3.2, 6.2, hullMid);
  B(-15.2, 3.0, 0, 3.2, 3.0, 6.2, woodDark);
  B(-17, 3.0, 0, 0.35, 1.6, 5.2, gold);
  B(-16.8, 4.8, 0, 3.4, 0.6, 6.2, woodDark);
  B(-18.5, 5.8, 0, 0.18, 2.6, 1.3, red);

  // Cannons / gunports.
  for (let x = -9; x <= 9; x += 3) {
    B(x, 0.5, 3.4, 1.1, 0.7, 0.7, dark);
    B(x, 0.5, -3.4, 1.1, 0.7, 0.7, dark);
  }

  function mast(x, top) {
    B(x, (3.7 + top) / 2, 0, 0.75, top - 3.7, 0.75, mastWood);
    B(x, top + 0.6, 0, 0.3, 1.3, 0.3, mastWood);
    B(x, top + 1.4, 0, 0.15, 0.9, 0.15, dark);
    B(x, top + 1.8, 0, 0.1, 1.4, 0.8, red);
  }

  function sails(x, ys, ws) {
    for (let i = 0; i < ys.length; i++) {
      const y = ys[i];
      const w = ws[i];

      // Yard.
      B(x, y + 1.35, 0, 0.8, 0.35, w * 1.08, woodDark);

      // Sail.
      B(x, y, 0, 0.45, 2.6, w * 0.8, sail);
    }
  }

  mast(-6, 14.5);
  sails(-6, [7.2, 11.3], [7, 8.6]);

  mast(0, 17.6);
  sails(0, [7.0, 11.2, 15.3], [10.5, 12.5, 8.0]);

  mast(8, 15.6);
  sails(8, [7.2, 11.3], [8, 10]);

  // Jib sails.
  B(16.5, 9.2, 0, 10, 3.2, 0.32, sail, 0, 0, 2.55);
  B(18.5, 7.3, 0, 7, 2.2, 0.28, sail, 0, 0, 2.85);

  function stay(x1, y1, x2, y2, z, color) {
    const dx = x2 - x1;
    const dy = y2 - y1;
    const len = Math.hypot(dx, dy);
    const ang = Math.atan2(dy, dx);
    B((x1 + x2) / 2, (y1 + y2) / 2, z, len, 0.12, 0.12, color, 0, 0, ang);
  }

  // Rigging.
  stay(8, 15, 24, 5, 0, rig);
  stay(0, 17.5, -17, 5, 0, rig);
  stay(0, 17.5, 8, 15, 0, rig);
  stay(8, 15, 0, 17.5, 0, rig);
  stay(-6, 14.5, -15, 5, 0, rig);
  stay(-6, 14.5, 0, 17.5, 0, rig);
  stay(8, 15, 14, 4, 0, rig);
  stay(-6, 14.5, 8, 15, 0, rig);

  // Deck cargo.
  B(-2, 4.5, 1, 2, 1.2, 2.2, 0xa5764d);
  B(4, 4.5, -1, 2.2, 1, 2, 0x8d6341);
  B(6, 4.5, 1, 1.2, 1, 1.2, 0x9e6149);
  B(-9, 4.6, 0, 1.6, 1.5, 1.1, 0x7e5736);
  B(-6, 4.6, 1.5, 1.0, 1.0, 1.0, 0xd0b25e);

  // Birds.
  const birds = [];
  const birdMat = getMat(0x223240);

  for (let i = 0; i < 9; i++) {
    const g = new THREE.Group();

    const body = new THREE.Mesh(cube, birdMat);
    body.scale.set(1.2, 0.25, 0.25);
    g.add(body);

    const wingL = new THREE.Mesh(cube, birdMat);
    wingL.scale.set(0.6, 0.06, 1.6);
    wingL.position.set(0, 0, 0.85);
    g.add(wingL);

    const wingR = new THREE.Mesh(cube, birdMat);
    wingR.scale.set(0.6, 0.06, 1.6);
    wingR.position.set(0, 0, -0.85);
    g.add(wingR);

    g.userData = {
      r: rr(35, 70),
      y: 30 + rr(0, 18),
      a: rnd() * Math.PI * 2,
      sp: rr(0.08, 0.18),
      flap: 6 + rr(0, 6),
      size: rr(0.8, 1.4)
    };

    g.scale.setScalar(g.userData.size);
    scene.add(g);
    birds.push(g);
  }

  // Animated sea plane.
  const seaGeo = new THREE.PlaneGeometry(260, 260, 40, 40);
  const sea = new THREE.Mesh(
    seaGeo,
    new THREE.MeshStandardMaterial({
      color: 0x2d749f,
      roughness: 0.85,
      metalness: 0.06,
      flatShading: true
    })
  );
  sea.rotation.x = -Math.PI / 2;
  sea.position.y = 0;
  scene.add(sea);

  const seaPos = seaGeo.attributes.position;
  const seaBase = new Float32Array(seaPos.array);

  function updateSea(t) {
    for (let i = 0, l = seaPos.count; i < l; i++) {
      const x = seaBase[i * 3];
      const y = seaBase[i * 3 + 1];

      const z =
        Math.sin(x * 0.12 + t * 0.9) * 0.45 +
        Math.cos(y * 0.16 + t * 0.65) * 0.32 +
        Math.sin((x + y) * 0.08 + t * 0.35) * 0.24;

      seaPos.array[i * 3 + 2] = z;
    }

    seaPos.needsUpdate = true;
    seaGeo.computeVertexNormals();
  }

  // Simple orbit controls.
  const controls = {
    target: new THREE.Vector3(0, 5, 2),
    radius: 75,
    theta: -0.45,
    phi: 1.08
  };

  let dragging = false;
  let lastX = 0;
  let lastY = 0;
  let lastInteract = performance.now();

  function updateControls() {
    const sp = controls.radius * Math.sin(controls.phi);

    camera.position.set(
      controls.target.x + sp * Math.cos(controls.theta),
      controls.target.y + controls.radius * Math.cos(controls.phi),
      controls.target.z + sp * Math.sin(controls.theta)
    );

    camera.lookAt(controls.target);
  }

  const el = renderer.domElement;

  el.addEventListener("pointerdown", (e) => {
    dragging = true;
    lastX = e.clientX;
    lastY = e.clientY;
    lastInteract = performance.now();
    el.setPointerCapture(e.pointerId);
  });

  window.addEventListener("pointermove", (e) => {
    if (!dragging) return;

    const dx = e.clientX - lastX;
    const dy = e.clientY - lastY;

    lastX = e.clientX;
    lastY = e.clientY;

    controls.theta -= dx * 0.005;
    controls.phi -= dy * 0.005;
    controls.phi = Math.max(0.25, Math.min(1.5, controls.phi));

    lastInteract = performance.now();
  });

  window.addEventListener("pointerup", () => {
    dragging = false;
    lastInteract = performance.now();
  });

  el.addEventListener("wheel", (e) => {
    e.preventDefault();
    controls.radius *= Math.exp(e.deltaY * 0.001);
    controls.radius = Math.max(22, Math.min(160, controls.radius));
    lastInteract = performance.now();
  }, { passive: false });

  el.addEventListener("contextmenu", (e) => e.preventDefault());

  window.addEventListener("resize", () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

  // Animation loop.
  const clock = new THREE.Clock();

  function animate() {
    const dt = Math.min(clock.getDelta(), 0.05);
    const t = clock.elapsedTime;

    updateSea(t);

    shipGroup.position.y = Math.sin(t * 0.75) * 0.22;
    shipGroup.rotation.z = Math.sin(t * 0.62) * 0.014;
    shipGroup.rotation.y = Math.sin(t * 0.33) * 0.02;

    lanternLight.intensity = 1.35 + Math.sin(t * 2.7) * 0.25;

    for (const b of birds) {
      const d = b.userData;
      d.a += dt * d.sp;

      b.position.set(
        Math.cos(d.a) * d.r,
        d.y + Math.sin(d.a * 3) * 1.5,
        Math.sin(d.a) * d.r
      );

      b.rotation.y = -d.a - Math.PI / 2;

      const flap = Math.sin(t * d.flap) * 0.75;
      b.children[1].rotation.x = flap;
      b.children[2].rotation.x = -flap;
    }

    if (!dragging && performance.now() - lastInteract > 3000) {
      controls.theta += dt * 0.035;
    }

    updateControls();
    renderer.render(scene, camera);
    requestAnimationFrame(animate);
  }

  animate();
})();
</script>
</body>
</html>
```