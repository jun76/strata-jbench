```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Voxel Harbor — Sailing Ship</title>
  <style>
    html, body {
      margin: 0;
      width: 100%;
      height: 100%;
      overflow: hidden;
      background: #9ad9f0;
    }
    canvas { display: block; }
    #hint {
      position: fixed;
      left: 16px;
      bottom: 14px;
      padding: 8px 12px;
      color: #143547;
      background: rgba(255, 255, 255, 0.72);
      border-radius: 10px;
      font: 13px/1.35 system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
      pointer-events: none;
      box-shadow: 0 6px 18px rgba(0, 0, 0, 0.12);
    }
    #loading {
      position: fixed;
      left: 50%;
      top: 50%;
      transform: translate(-50%, -50%);
      color: #123;
      font: 600 16px/1.4 system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
      pointer-events: none;
    }
  </style>
</head>
<body>
  <div id="hint">Drag to orbit · Scroll to zoom · Ship calling at a voxel harbor</div>
  <div id="loading">Loading Three.js from CDN…</div>

  <script type="importmap">
    {
      "imports": {
        "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
        "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
      }
    }
  </script>

  <script type="module">
    import * as THREE from 'three';
    import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x9ad9f0);
    scene.fog = new THREE.Fog(0x9ad9f0, 95, 190);

    const camera = new THREE.PerspectiveCamera(55, innerWidth / innerHeight, 0.1, 500);
    camera.position.set(26, 31, -64);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(innerWidth, innerHeight);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    document.body.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.target.set(0, 4, 0);
    controls.enableDamping = true;
    controls.dampingFactor = 0.06;
    controls.enablePan = false;
    controls.minDistance = 12;
    controls.maxDistance = 130;
    controls.maxPolarAngle = Math.PI / 2 - 0.03;
    controls.autoRotate = true;
    controls.autoRotateSpeed = 0.35;

    renderer.domElement.addEventListener('pointerdown', () => {
      controls.autoRotate = false;
    });

    scene.add(new THREE.HemisphereLight(0xcfeeff, 0x335847, 0.95));

    const sun = new THREE.DirectionalLight(0xfff1c8, 1.15);
    sun.position.set(-35, 55, 15);
    scene.add(sun);

    const boxGeo = new THREE.BoxGeometry(1, 1, 1);

    function createVoxelMesh(voxels) {
      if (!voxels.length) return null;

      const material = new THREE.MeshLambertMaterial({ color: 0xffffff });
      const mesh = new THREE.InstancedMesh(boxGeo, material, voxels.length);
      const dummy = new THREE.Object3D();
      const col = new THREE.Color();

      for (let i = 0; i < voxels.length; i++) {
        const v = voxels[i];
        dummy.position.set(v.x, v.y, v.z);
        dummy.updateMatrix();
        mesh.setMatrixAt(i, dummy.matrix);
        mesh.setColorAt(i, col.set(v.c));
      }

      mesh.instanceMatrix.needsUpdate = true;
      if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
      mesh.frustumCulled = false;
      return mesh;
    }

    const world = [];
    const waterVoxels = [];

    function wAdd(x, y, z, c) {
      world.push({ x, y, z, c });
    }

    function waterAdd(x, y, z, c) {
      waterVoxels.push({ x, y, z, c });
    }

    function rnd(a, b, c = 0) {
      const n = Math.sin(a * 127.1 + b * 311.7 + c * 74.7) * 43758.5453;
      return n - Math.floor(n);
    }

    function inBreakwater(x, z) {
      return x >= 24 && x <= 34 && z >= 0 && z <= 14;
    }

    // Water surface voxels.
    for (let x = -60; x <= 60; x++) {
      for (let z = -60; z <= 11; z++) {
        // Avoid overlapping water voxels around the ship hull.
        if (x >= -16 && x <= 16 && z >= -13 && z <= -1) continue;
        if (inBreakwater(x, z)) continue;

        const r = rnd(x, z, 1);
        let c;

        if (Math.abs(x) > 57 || z < -57) c = 0x17537d;
        else if (z > 7) c = 0x8fd4ee;
        else if (z > 2) c = 0x5cb8e0;
        else if (z > -10) c = r > 0.55 ? 0x3e93c9 : 0x2f7fb8;
        else c = r > 0.65 ? 0x256897 : 0x1f5e8c;

        waterAdd(x, 0, z, c);
      }
    }

    // Opaque sea base just below the voxel water surface.
    const seaBase = new THREE.Mesh(
      new THREE.BoxGeometry(340, 20, 340),
      new THREE.MeshLambertMaterial({ color: 0x2a74a8 })
    );
    seaBase.position.y = -9.51; // top is at 0.49, just below water voxels
    scene.add(seaBase);

    // Shore sand and grass.
    for (let x = -60; x <= 60; x++) {
      if (!inBreakwater(x, 11)) wAdd(x, 1, 11, 0xd9c497);
    }

    for (let x = -60; x <= 60; x++) {
      for (let z = 12; z <= 50; z++) {
        if (inBreakwater(x, z) && z <= 14) continue;

        const r = rnd(x, z, 2);
        let c = r > 0.75 ? 0x4d8b44 : 0x5aa24c;
        wAdd(x, 2, z, c);

        if (z > 16 && r > 0.86) wAdd(x, 3, z, 0x3d7535);
      }
    }

    // Harbor quay.
    const wood = 0x8b5a2b;
    const woodLight = 0xa87540;
    const woodDark = 0x5a381f;

    for (let x = -16; x <= 16; x++) {
      for (let z = 0; z <= 11; z++) {
        let c = ((x + z) % 4 < 2) ? wood : woodLight;
        if (x % 5 === 0) c = ((z + 1) % 4 < 2) ? woodLight : wood;
        wAdd(x, 2, z, c);
      }

      if (x === -16 || x === 16) {
        for (let z = 0; z <= 11; z++) wAdd(x, 1, z, woodDark);
      }
    }

    // Quay pilings.
    for (let x = -15; x <= 15; x += 4) {
      for (const z of [1, 10]) {
        for (let y = -2; y <= 1; y++) wAdd(x, y, z, woodDark);
      }
    }

    // Bollards.
    for (const x of [-12, -4, 4, 12]) {
      wAdd(x, 3, 1, woodDark);
    }

    function addBlock(cx, cz, y, sx, sz, sy, c) {
      for (let x = cx; x < cx + sx; x++) {
        for (let z = cz; z < cz + sz; z++) {
          for (let yy = y; yy < y + sy; yy++) {
            wAdd(x, yy, z, c);
          }
        }
      }
    }

    // Cargo on the quay.
    addBlock(7, 3, 3, 2, 2, 2, 0x9b6a3c);
    addBlock(9, 3, 3, 2, 2, 2, 0x7f512b);
    addBlock(7, 3, 5, 2, 2, 1, 0xb1885b);

    addBlock(-9, 3, 3, 2, 2, 2, 0x9b6a3c);
    addBlock(-7, 3, 4, 2, 2, 2, 0x7f512b);
    addBlock(-8, 3, 5, 2, 2, 1, 0xb1885b);

    for (const [bx, bz] of [[-2, 4], [12, 2]]) {
      addBlock(bx, bz, 3, 2, 2, 2, 0x6d4526);
      addBlock(bx, bz, 5, 1, 1, 1, 0x3f2716);
    }

    function addLantern(x, z) {
      for (let y = 3; y <= 5; y++) wAdd(x, y, z, 0x333333);
      wAdd(x, 6, z, 0xffdd66);
      wAdd(x - 1, 6, z, 0xffc94d);
      wAdd(x + 1, 6, z, 0xffc94d);
      wAdd(x, 6, z - 1, 0xffc94d);
      wAdd(x, 6, z + 1, 0xffc94d);
    }

    addLantern(-6, 2);
    addLantern(6, 2);

    // Breakwater and lighthouse.
    for (let x = 24; x <= 34; x++) {
      for (let z = 0; z <= 14; z++) {
        if (rnd(x, z, 3) > 0.08) {
          const c = rnd(x, z, 4) > 0.5 ? 0x9a9a9a : 0x777777;
          wAdd(x, 1, z, c);
          if (z > 3 && rnd(x, z, 5) > 0.18) wAdd(x, 2, z, c);
        }
      }
    }

    for (let y = 3; y <= 16; y++) {
      for (let x = 27; x <= 29; x++) {
        for (let z = 1; z <= 3; z++) {
          let c;

          if (x === 28 && (y === 3 || y === 7 || y === 11) && z === 1) {
            c = 0x223344;
          } else if (y <= 13) {
            c = (Math.floor((y - 3) / 3) % 2 === 0) ? 0xf7f7f7 : 0xc83c3c;
          } else if (y === 14) {
            c = 0x4a4a4a;
          } else if (y === 15) {
            c = 0xffdf66;
          } else {
            c = 0xc83c3c;
          }

          wAdd(x, y, z, c);
        }
      }
    }

    // Harbor buildings.
    function addHouse(cx, cz, w, d, h, wall, roof) {
      const x0 = cx - Math.floor(w / 2);
      const x1 = cx + Math.floor((w - 1) / 2);
      const z0 = cz - Math.floor(d / 2);
      const z1 = cz + Math.floor((d - 1) / 2);

      for (let y = 3; y <= 2 + h; y++) {
        for (let x = x0; x <= x1; x++) {
          for (let z = z0; z <= z1; z++) {
            if (x === x0 || x === x1 || z === z0 || z === z1) {
              let c = wall;
              if (y === 3 && x === cx && z === z0) c = 0x4a2c16;
              if (
                y >= 4 &&
                (z === z0 || z === z1) &&
                ((x - cx) % 2 === 0) &&
                (y % 2 === 0)
              ) {
                c = 0x24394f;
              }
              wAdd(x, y, z, c);
            }
          }
        }
      }

      const tiers = Math.ceil(Math.max(w, d) / 2);
      for (let r = 0; r < tiers; r++) {
        const xS = x0 + r;
        const xE = x1 - r;
        const zS = z0 + r;
        const zE = z1 - r;

        if (xS > xE || zS > zE) break;

        for (let x = xS; x <= xE; x++) {
          for (let z = zS; z <= zE; z++) {
            wAdd(x, 3 + h + r, z, roof);
          }
        }
      }
    }

    addHouse(-34, 26, 5, 5, 4, 0xf1e3c7, 0x8d4b4b);
    addHouse(-22, 32, 5, 5, 4, 0xdac5a8, 0x5f7b88);
    addHouse(-8, 24, 5, 5, 3, 0xc2d6e8, 0x607d8c);
    addHouse(6, 34, 7, 5, 5, 0xe9d9b7, 0x6d8d82);
    addHouse(18, 26, 5, 5, 4, 0xd1bb9d, 0x7d4f3a);

    function addTree(x, z) {
      for (let y = 3; y <= 5; y++) wAdd(x, y, z, 0x5b3b21);

      for (let y = 6; y <= 7; y++) {
        for (let dx = -1; dx <= 1; dx++) {
          for (let dz = -1; dz <= 1; dz++) {
            if (Math.abs(dx) + Math.abs(dz) <= 2) {
              wAdd(x + dx, y, z + dz, 0x3b7f45);
            }
          }
        }
      }

      wAdd(x, 8, z, 0x3b7f45);
    }

    for (const [tx, tz] of [
      [-43, 17],
      [-40, 33],
      [-29, 18],
      [-16, 20],
      [-12, 38],
      [-3, 18],
      [2, 30],
      [17, 34],
      [19, 18]
    ]) {
      addTree(tx, tz);
    }

    const worldMesh = createVoxelMesh(world);
    if (worldMesh) scene.add(worldMesh);

    const waterMesh = createVoxelMesh(waterVoxels);
    if (waterMesh) scene.add(waterMesh);

    // The sailing ship.
    function buildShip() {
      const v = [];
      const add = (x, y, z, c) => v.push({ x, y, z, c });

      const hull = 0x7a4b26;
      const dark = 0x432918;
      const deck = 0xc79a61;
      const sail = 0xf4eedb;
      const mast = 0x58391f;
      const black = 0x222222;

      function lengthProfile(x) {
        let lf = 1;

        if (x > 9) {
          const t = (x - 9) / 6.2;
          lf = Math.sqrt(Math.max(0, 1 - t * t));
        }

        if (x < -10) {
          const t = (-10 - x) / 6.2;
          lf = Math.sqrt(Math.max(0, 1 - t * t));
        }

        return Math.max(0, lf);
      }

      function hw(x, y) {
        const hf =
          y === -3 ? 0.18 :
          y === -2 ? 0.55 :
          y === -1 ? 0.82 :
          y === 0 ? 1.0 :
          y === 1 ? 1.0 :
          y === 2 ? 0.82 : 0;

        return Math.round(5 * lengthProfile(x) * hf);
      }

      // Hull.
      for (let x = -15; x <= 15; x++) {
        for (let y = -3; y <= 2; y++) {
          const h = hw(x, y);
          if (h < 0) continue;

          for (let z = -h; z <= h; z++) {
            let c;

            if (y === 2) {
              c = Math.abs(z) < h ? deck : dark;
            } else if (y === 1) {
              c = dark;
            } else if (y === 0 && Math.abs(z) === h) {
              c = black;
            } else if (y < 0 && Math.abs(z) === h) {
              c = dark;
            } else {
              c = hull;
            }

            add(x, y, z, c);
          }
        }
      }

      // Railing posts.
      for (let x = -13; x <= 13; x += 2) {
        const h = hw(x, 0);
        if (h > 1) {
          add(x, 3, h, dark);
          add(x, 3, -h, dark);
        }
      }

      // Forecastle deck.
      for (let x = 8; x <= 14; x++) {
        const h = hw(x, 1);
        for (let z = -h + 1; z <= h - 1; z++) {
          if (h > 1) add(x, 3, z, deck);
        }
      }

      // Aftcastle and cabin.
      for (let x = -14; x <= -7; x++) {
        const h = hw(x, 1);
        for (let z = -h + 1; z <= h - 1; z++) {
          if (h > 1) add(x, 3, z, 0x9b6a41);
        }
      }

      for (let x = -13; x <= -8; x++) {
        const h = hw(x, 1) - 2;
        for (let z = -h; z <= h; z++) {
          if (h > 0) add(x, 4, z, 0x9b6a41);
        }
      }

      for (let x = -12; x <= -9; x += 2) {
        add(x, 4, -1, 0x24394f);
        add(x, 4, 1, 0x24394f);
      }

      function makeMast(mx, top, start = 3) {
        for (let y = start; y <= top; y++) add(mx, y, 0, mast);
      }

      function makeYard(mx, y, h) {
        for (let z = -h; z <= h; z++) add(mx, y, z, mast);
        add(mx, y + 1, 0, mast);
        add(mx - 1, y, 0, mast);
        add(mx + 1, y, 0, mast);
      }

      function makeSail(sx, y0, y1, zh) {
        for (let y = y0; y <= y1; y++) {
          const yc = (y0 + y1) / 2;
          const shrink = Math.round(Math.abs(y - yc) * 0.2);
          const m = Math.max(1, zh - shrink);

          for (let z = -m; z <= m; z++) {
            add(sx, y, z, sail);
          }
        }
      }

      // Masts.
      makeMast(0, 23, 3);   // main
      makeMast(8, 19, 3);   // fore
      makeMast(-10, 17, 5); // mizzen

      // Main rig.
      makeYard(0, 11, 6);
      makeYard(0, 15, 4);
      makeYard(0, 19, 2);
      makeSail(1, 6, 10, 6);
      makeSail(1, 12, 14, 4);
      makeSail(1, 16, 18, 2);

      // Fore rig.
      makeYard(8, 9, 5);
      makeYard(8, 13, 3);
      makeSail(9, 5, 8, 5);
      makeSail(9, 10, 12, 3);

      // Mizzen rig.
      makeYard(-10, 10, 4);
      makeYard(-10, 13, 2);
      makeSail(-9, 7, 9, 4);
      makeSail(-9, 11, 12, 2);

      // Bowsprit.
      for (let x = 16; x <= 20; x++) add(x, 4, 0, mast);
      add(20, 5, 0, mast);

      // Flag.
      for (let z = 1; z <= 4; z++) add(0, 23, z, 0xd62828);

      return v;
    }

    const shipGroup = new THREE.Group();
    const shipMesh = createVoxelMesh(buildShip());
    if (shipMesh) shipGroup.add(shipMesh);

    shipGroup.position.set(0, 0.5, -7);
    scene.add(shipGroup);

    // Drifting voxel clouds.
    const clouds = [];

    function makeCloud(seed) {
      const ox = -80 + rnd(seed, 1) * 160;
      const oz = -80 + rnd(seed, 2) * 160;
      const oy = 32 + rnd(seed, 3) * 14;

      const vox = [];
      const seen = new Set();
      const n = 20 + Math.floor(rnd(seed, 4) * 15);

      for (let i = 0; i < n; i++) {
        const a = rnd(seed + i * 13, 5);
        const b = rnd(seed + i * 17, 6);
        const c = rnd(seed + i * 23, 7);

        const dx = Math.floor((a - 0.5) * 16);
        const dz = Math.floor((b - 0.5) * 10);
        const dy = Math.floor(c * 2);

        if (Math.abs(dx) + Math.abs(dz) < 11) {
          const key = `${dx},${dy},${dz}`;
          if (!seen.has(key)) {
            seen.add(key);
            vox.push({ x: dx, y: dy, z: dz, c: 0xffffff });
          }
        }
      }

      const mesh = createVoxelMesh(vox);
      if (mesh) {
        const g = new THREE.Group();
        g.add(mesh);
        g.position.set(ox, oy, oz);
        scene.add(g);
        clouds.push({ g, speed: 0.004 + rnd(seed, 8) * 0.008 });
      }
    }

    for (let i = 0; i < 8; i++) makeCloud(i * 101 + 1);

    window.addEventListener('resize', () => {
      camera.aspect = innerWidth / innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(innerWidth, innerHeight);
    });

    const clock = new THREE.Clock();

    function animate() {
      requestAnimationFrame(animate);

      const t = clock.getElapsedTime();

      shipGroup.position.y = 0.5 + Math.sin(t * 0.7) * 0.22;
      shipGroup.rotation.z = Math.sin(t * 0.5) * 0.015;
      shipGroup.rotation.y = Math.sin(t * 0.25) * 0.025;

      for (const c of clouds) {
        c.g.position.x += c.speed;
        if (c.g.position.x > 110) c.g.position.x = -110;
      }

      controls.update();
      renderer.render(scene, camera);
    }

    animate();

    const loading = document.getElementById('loading');
    if (loading) loading.remove();
  </script>
</body>
</html>
```