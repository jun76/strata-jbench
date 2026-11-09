Save the following as a single `.html` file (for example `harbor.html`) and open it in Chrome. It uses Three.js from a CDN, so an internet connection is required the first time.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Voxel Harbor — A Sailing Ship Calling at a Harbor</title>
  <style>
    html, body {
      margin: 0;
      width: 100%;
      height: 100%;
      overflow: hidden;
      background: #8fc7f2;
    }
    canvas { display: block; }
    #info {
      position: absolute;
      left: 14px;
      top: 12px;
      color: #ffffff;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 13px;
      text-shadow: 0 1px 3px #000;
      pointer-events: none;
      z-index: 10;
      user-select: none;
    }
  </style>
</head>
<body>
  <div id="info">Drag: orbit &nbsp;·&nbsp; Scroll: zoom &nbsp;·&nbsp; Right-drag: pan</div>

  <script type="importmap">
  {
    "imports": {
      "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
      "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
    }
  }
  </script>

  <script type="module">
    import * as THREE from "three";
    import { OrbitControls } from "three/addons/controls/OrbitControls.js";

    const C = {
      sky: 0x8fc7f2,
      water: 0x3189c9,
      foam: 0xdff3f7,
      deepSea: 0x174977,
      dirt: 0x7d5632,
      grass: 0x5fa83c,
      stone: 0x8d8d8d,
      rock: 0x5d5d5d,

      pierPillar: 0x4e341f,
      dock: 0x9c6737,
      plank: 0x7a5230,
      crate: 0xc38b4d,
      barrel: 0x7d5326,
      lamp: 0xffd767,

      hullLower: 0x38221a,
      hullMid: 0x6d4629,
      hullUpper: 0x8c6034,
      deck: 0xb38147,
      stern: 0x704629,
      mast: 0x5a3c25,
      sail: 0xf3efe3,
      flag: 0xd7263d,

      wallA: 0xd7b98c,
      wallB: 0xb79875,
      wallC: 0xd08f7a,
      roofA: 0x9c3b34,
      roofB: 0x3c5a83,
      roofC: 0x4d7f5a,

      trunk: 0x5b3a26,
      leaves: 0x3e8f3e,
      cloud: 0xffffff,

      lighthouseWhite: 0xf8f8f8,
      lighthouseRed: 0xd73838,
      light: 0xffe066,
      black: 0x222222,

      warehouse: 0xb45b4a
    };

    const voxelsByColor = new Map();
    const occupied = new Set();

    function addVoxel(x, y, z, color) {
      const key = `${x},${y},${z}`;
      if (occupied.has(key)) return false;
      occupied.add(key);

      if (!voxelsByColor.has(color)) voxelsByColor.set(color, []);
      voxelsByColor.get(color).push([x, y, z]);
      return true;
    }

    function fill(x1, x2, y1, y2, z1, z2, color) {
      if (x1 > x2) { const t = x1; x1 = x2; x2 = t; }
      if (y1 > y2) { const t = y1; y1 = y2; y2 = t; }
      if (z1 > z2) { const t = z1; z1 = z2; z2 = t; }

      for (let x = x1; x <= x2; x++) {
        for (let y = y1; y <= y2; y++) {
          for (let z = z1; z <= z2; z++) {
            addVoxel(x, y, z, color);
          }
        }
      }
    }

    function addCrate(cx, cz, size = 2) {
      fill(cx, cx + size - 1, 4, 4 + size - 1, cz, cz + size - 1, C.crate);
      addVoxel(cx, 4, cz, C.black);
      addVoxel(cx + size - 1, 4, cz + size - 1, C.black);
    }

    function addBarrel(cx, cz) {
      fill(cx, cx + 1, 4, 5, cz, cz + 1, C.barrel);
      addVoxel(cx, 4, cz, C.black);
      addVoxel(cx + 1, 5, cz + 1, C.black);
    }

    function addTree(x, z) {
      fill(x, x, 4, 5, z, z, C.trunk);
      fill(x - 1, x + 1, 6, 7, z - 1, z + 1, C.leaves);
      fill(x, x, 8, 8, z, z, C.leaves);
    }

    function addHouse(x, z, w, d, h, wallColor, roofColor) {
      fill(x, x + w - 1, 4, 4 + h - 1, z, z + d - 1, wallColor);

      const roofSteps = Math.ceil(Math.min(w, d) / 2);
      for (let s = 0; s < roofSteps; s++) {
        const xa = x + s;
        const xb = x + w - 1 - s;
        const za = z + s;
        const zb = z + d - 1 - s;
        const ya = 4 + h + s;
        const yb = ya;
        if (xa > xb || za > zb) break;
        fill(xa, xb, ya, yb, za, zb, roofColor);
      }
    }

    function addLighthouse(x, z) {
      for (let y = 4; y <= 9; y++) {
        const col = (y % 2 === 0) ? C.lighthouseRed : C.lighthouseWhite;
        fill(x, x + 1, y, y, z, z + 1, col);
      }
      fill(x, x + 1, 10, 10, z, z + 1, C.light);
      fill(x, x + 1, 11, 11, z, z + 1, C.black);
    }

    function addCloud(cx, cy, cz, w, d) {
      fill(cx, cx + w - 1, cy, cy, cz, cz + d - 1, C.cloud);
      if (w > 2 && d > 2) {
        fill(cx + 1, cx + w - 2, cy + 1, cy + 1, cz + 1, cz + d - 2, C.cloud);
      }
    }

    function addShip(sx, sz) {
      const half = (x) => {
        if (x === 7) return 0;
        if (x === -7) return 1;
        if (x >= 6) return 1;
        return 2;
      };

      // Hull lower / upper sides
      for (let x = -7; x <= 7; x++) {
        const h = half(x);
        for (let z = -h; z <= h; z++) {
          addVoxel(sx + x, 0, sz + z, C.hullLower);
          addVoxel(sx + x, 1, sz + z, C.hullMid);
          if (Math.abs(z) === h || Math.abs(x) === 7) {
            addVoxel(sx + x, 2, sz + z, C.hullUpper);
          }
        }
      }

      // Bulwark rail
      for (let x = -7; x <= 7; x++) {
        const h = half(x);
        addVoxel(sx + x, 3, sz - h, C.hullUpper);
        if (h > 0) addVoxel(sx + x, 3, sz + h, C.hullUpper);
      }

      // Main deck
      fill(sx - 6, sx + 6, 3, 3, sz - 1, sz + 1, C.deck);

      // Raised sterncastle
      fill(sx - 7, sx - 5, 3, 5, sz - 1, sz + 1, C.stern);

      // Raised forecastle
      fill(sx + 5, sx + 7, 3, 4, sz - 1, sz + 1, C.stern);

      // Bowsprit
      addVoxel(sx + 7, 3, sz, C.mast);
      addVoxel(sx + 8, 4, sz, C.mast);
      addVoxel(sx + 9, 5, sz, C.mast);

      // Cargo on deck
      addVoxel(sx + 1, 4, sz, C.crate);
      addVoxel(sx + 3, 4, sz - 1, C.crate);
      addVoxel(sx + 3, 4, sz + 1, C.crate);

      // Masts
      const masts = [
        [0, 13],   // main
        [4, 11],   // fore
        [-4, 10]   // mizzen
      ];
      for (const [mx, h] of masts) {
        fill(sx + mx, sx + mx, 4, h, sz, sz, C.mast);
      }

      const sail = (mx, y1, y2, halfZ) => {
        fill(sx + mx - 1, sx + mx - 1, y1, y2, sz - halfZ, sz + halfZ, C.sail);
        fill(sx + mx + 1, sx + mx + 1, y1, y2, sz - halfZ, sz + halfZ, C.sail);
      };

      const yard = (mx, y, halfZ) => {
        fill(sx + mx, sx + mx, y, y, sz - halfZ - 1, sz + halfZ + 1, C.mast);
      };

      // Square sails
      sail(0, 6, 8, 3);  yard(0, 9, 3);  sail(0, 10, 12, 2);
      sail(4, 6, 8, 3);  yard(4, 9, 3);  sail(4, 10, 10, 2);
      sail(-4, 6, 8, 2); yard(-4, 9, 2);

      // Flags
      addVoxel(sx + 1, 14, sz, C.flag);
      addVoxel(sx + 2, 14, sz, C.flag);

      addVoxel(sx + 5, 12, sz, C.flag);
      addVoxel(sx + 6, 12, sz, C.flag);

      addVoxel(sx - 5, 11, sz, C.flag);
    }

    // -------------------------------------------------------------------------
    // Build the entire voxel harbor
    // -------------------------------------------------------------------------

    // Land and quay wall
    fill(9, 36, 0, 2, -28, 28, C.dirt);
    fill(9, 36, 3, 3, -28, 28, C.grass);
    fill(8, 8, 0, 3, -28, 28, C.stone);

    // Breakwaters
    fill(4, 7, 0, 3, -26, -16, C.rock);
    fill(4, 7, 0, 3, 16, 26, C.rock);

    // Harbor lighthouse on the quay
    addLighthouse(10, -28);

    // Main dock
    for (const px of [-4, -1, 2, 5, 7]) {
      fill(px, px, 0, 2, -1, 1, C.pierPillar);
    }
    fill(-4, 7, 3, 3, -2, 2, C.dock);

    // Gangplank to the ship
    fill(0, 1, 3, 3, 3, 5, C.plank);

    // Lamp posts
    for (const [lx, lz] of [[-2, -2], [-2, 2]]) {
      fill(lx, lx, 4, 6, lz, lz, C.black);
      addVoxel(lx, 7, lz, C.lamp);
    }

    // Ship calling at the harbor
    addShip(-2, 8);

    // Cargo on the dock
    addCrate(2, -1, 2);
    addCrate(4, -2, 2);
    addCrate(1, 1, 2);
    addBarrel(4, 1);
    addBarrel(0, -2);

    // Warehouse near the quay
    fill(9, 14, 4, 6, 3, 7, C.warehouse);
    fill(9, 14, 7, 7, 3, 7, C.roofA);

    // Town
    addHouse(10, -23, 5, 3, 3, C.wallA, C.roofA);
    addHouse(10, -18, 6, 4, 3, C.wallB, C.roofB);
    addHouse(10, -13, 5, 4, 3, C.wallC, C.roofC);
    addHouse(10, -8, 6, 4, 3, C.wallA, C.roofB);

    addHouse(18, -22, 7, 5, 4, C.wallB, C.roofC);
    addHouse(18, -16, 7, 4, 3, C.wallC, C.roofA);
    addHouse(18, -11, 6, 5, 3, C.wallA, C.roofB);

    addHouse(26, -22, 6, 5, 3, C.wallC, C.roofA);
    addHouse(26, -15, 7, 4, 4, C.wallB, C.roofC);
    addHouse(26, -9, 6, 4, 3, C.wallA, C.roofA);
    addHouse(26, 5, 7, 5, 4, C.wallB, C.roofB);

    // Trees
    addTree(14, 12);
    addTree(16, 20);
    addTree(22, 16);
    addTree(30, 10);
    addTree(32, -18);

    // Clouds
    addCloud(-24, 20, 12, 12, 5);
    addCloud(-6, 22, -18, 14, 6);
    addCloud(16, 20, 22, 12, 5);
    addCloud(24, 23, -4, 14, 6);

    // Sea floor and water surface
    fill(-40, 7, -1, -1, -30, 30, C.deepSea);
    for (let x = -40; x <= 7; x++) {
      for (let z = -30; z <= 30; z++) {
        addVoxel(x, 0, z, x === 7 ? C.foam : C.water);
      }
    }

    // -------------------------------------------------------------------------
    // Three.js scene, camera, controls, lights, instanced voxel rendering
    // -------------------------------------------------------------------------

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(C.sky);
    scene.fog = new THREE.Fog(C.sky, 80, 190);

    const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 600);
    camera.position.set(34, 28, -48);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    document.body.appendChild(renderer.domElement);

    renderer.domElement.addEventListener("contextmenu", e => e.preventDefault());

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.target.set(0, 6, 0);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.minDistance = 10;
    controls.maxDistance = 180;
    controls.maxPolarAngle = Math.PI * 0.495;
    controls.autoRotate = false;
    controls.autoRotateSpeed = 0.5;
    controls.update();

    const hemi = new THREE.HemisphereLight(0xcfe8ff, 0x7a6a55, 0.55);
    scene.add(hemi);

    const sun = new THREE.DirectionalLight(0xfff2d0, 1.15);
    sun.position.set(35, 55, -35);
    sun.target.position.set(0, 0, 0);
    sun.castShadow = true;
    sun.shadow.mapSize.set(2048, 2048);
    sun.shadow.camera.near = 0.5;
    sun.shadow.camera.far = 220;
    sun.shadow.camera.left = -70;
    sun.shadow.camera.right = 70;
    sun.shadow.camera.top = 70;
    sun.shadow.camera.bottom = -70;
    sun.shadow.bias = -0.0004;
    sun.shadow.normalBias = 0.02;
    scene.add(sun);
    scene.add(sun.target);

    const ambient = new THREE.AmbientLight(0xffffff, 0.18);
    scene.add(ambient);

    const box = new THREE.BoxGeometry(1, 1, 1);
    const dummy = new THREE.Object3D();
    const waterDummy = new THREE.Object3D();
    const waterMeshes = [];

    const noCast = new Set([C.water, C.foam, C.deepSea, C.cloud]);

    for (const [color, positions] of voxelsByColor.entries()) {
      if (positions.length === 0) continue;

      const material = new THREE.MeshLambertMaterial({
        color,
        flatShading: true
      });

      const mesh = new THREE.InstancedMesh(box, material, positions.length);
      mesh.frustumCulled = false;
      mesh.castShadow = !noCast.has(color);
      mesh.receiveShadow = true;

      for (let i = 0; i < positions.length; i++) {
        const p = positions[i];
        dummy.position.set(p[0], p[1], p[2]);
        dummy.updateMatrix();
        mesh.setMatrixAt(i, dummy.matrix);
      }

      mesh.instanceMatrix.needsUpdate = true;
      scene.add(mesh);

      if (color === C.water || color === C.foam) {
        waterMeshes.push({ mesh, positions });
      }
    }

    const clock = new THREE.Clock();

    function animate() {
      requestAnimationFrame(animate);

      const t = clock.getElapsedTime();

      for (const w of waterMeshes) {
        const mesh = w.mesh;
        const positions = w.positions;

        for (let i = 0; i < positions.length; i++) {
          const p = positions[i];
          const wave = (Math.sin(t * 1.25 + p[2] * 0.30) * 0.5 + 0.5) * 0.025;
          waterDummy.position.set(p[0], p[1] + wave, p[2]);
          waterDummy.updateMatrix();
          mesh.setMatrixAt(i, waterDummy.matrix);
        }

        mesh.instanceMatrix.needsUpdate = true;
      }

      controls.update();
      renderer.render(scene, camera);
    }

    window.addEventListener("resize", () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    });

    animate();
  </script>
</body>
</html>
```