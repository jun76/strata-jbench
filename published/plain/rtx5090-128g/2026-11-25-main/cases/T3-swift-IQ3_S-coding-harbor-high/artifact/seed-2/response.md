```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Voxel Harbor — A Sailing Ship Calling At A Harbor</title>
  <style>
    html, body {
      margin: 0;
      width: 100%;
      height: 100%;
      overflow: hidden;
      background: #87ceeb;
    }
    canvas { display: block; }
    #hint {
      position: fixed;
      left: 12px;
      bottom: 12px;
      color: rgba(255,255,255,0.9);
      font: 12px system-ui, sans-serif;
      text-shadow: 0 1px 2px rgba(0,0,0,0.35);
      pointer-events: none;
    }
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
  <div id="hint">drag: orbit • wheel: zoom • right-drag: pan</div>

  <script type="module">
    import * as THREE from "three";
    import { OrbitControls } from "three/addons/controls/OrbitControls.js";

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x8ed8f5);
    scene.fog = new THREE.Fog(0xb9dcf1, 70, 215);

    const camera = new THREE.PerspectiveCamera(
      45,
      window.innerWidth / window.innerHeight,
      0.1,
      500
    );
    camera.position.set(52, 30, 62);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    document.body.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.target.set(-2, 10, 0);
    controls.enableDamping = true;
    controls.dampingFactor = 0.06;
    controls.minDistance = 18;
    controls.maxDistance = 150;
    controls.maxPolarAngle = Math.PI / 2 - 0.03;
    controls.update();

    const hemiLight = new THREE.HemisphereLight(0xcfefff, 0x234b70, 0.65);
    scene.add(hemiLight);

    const sunMesh = new THREE.Mesh(
      new THREE.SphereGeometry(7, 16, 16),
      new THREE.MeshBasicMaterial({ color: 0xfff6b5, fog: false })
    );
    sunMesh.position.set(88, 95, -35);
    scene.add(sunMesh);

    const sunLight = new THREE.DirectionalLight(0xfff0c0, 1.55);
    sunLight.position.copy(sunMesh.position);
    sunLight.castShadow = true;
    sunLight.shadow.mapSize.set(1024, 1024);
    sunLight.shadow.camera.left = -80;
    sunLight.shadow.camera.right = 80;
    sunLight.shadow.camera.top = 80;
    sunLight.shadow.camera.bottom = -80;
    sunLight.shadow.camera.near = 1;
    sunLight.shadow.camera.far = 260;
    sunLight.shadow.bias = -0.0005;
    sunLight.shadow.normalBias = 0.02;
    scene.add(sunLight);

    const fillLight = new THREE.DirectionalLight(0x88bbff, 0.35);
    fillLight.position.set(-55, 45, 60);
    scene.add(fillLight);

    const staticMat = new THREE.MeshLambertMaterial({ color: 0xffffff });
    const shipMat = new THREE.MeshLambertMaterial({ color: 0xffffff });
    const waterMat = new THREE.MeshLambertMaterial({ color: 0xffffff });
    const cloudMat = new THREE.MeshLambertMaterial({ color: 0xffffff });

    const staticData = [];
    const shipData = [];
    const waterData = [];
    const cloudData = [];

    function cube(x, y, z, color, data = staticData) {
      data.push({ x, y, z, w: 1, h: 1, d: 1, color: new THREE.Color(color) });
    }

    function box(cx, cy, cz, w, h, d, color, data = staticData) {
      data.push({ x: cx, y: cy, z: cz, w, h, d, color: new THREE.Color(color) });
    }

    function shipZmax(x) {
      if (x <= -11) return Math.min(7, 3 + (x + 14));
      if (x >= 11) return Math.max(1, 7 - (x - 10));
      return 7;
    }

    function buildLand() {
      box(-30.5, 2, 0, 29, 5, 89, 0x5d4037);
      box(-30.5, 5, 0, 29, 1, 89, 0x7cb342);

      for (let z = -34; z <= 34; z += 4) {
        cube(-15, 5, z, 0x757575);
        if (z % 12 === 0) cube(-15, 6, z, 0x9e9e9e);
      }
    }

    function buildQuay() {
      box(-13, 2, 0, 5, 5, 65, 0x9a9a9a);
      box(-13, 5, 0, 5, 1, 65, 0xc4c4c4);
      box(-11, 5, 0, 1, 1, 65, 0x616161);

      for (let z = -30; z <= 30; z += 4) {
        cube(-11, 0, z, 0x795548);
        cube(-11, 6, z, 0x424242);
        cube(-11, 7, z, 0x424242);
      }

      const plank = [
        [-11, 5],
        [-10, 5],
        [-9, 4],
        [-8, 3],
      ];
      for (const [x, y] of plank) {
        for (let z = -1; z <= 1; z++) cube(x, y, z, 0x8d6e63);
      }
    }

    function warehouse(z0, z1, wallColor) {
      const zC = (z0 + z1) / 2;
      const d = z1 - z0 + 1;

      box(-13, 8, zC, 4, 5, d, wallColor);

      for (let k = 0; k < 3; k++) {
        const w = 4 - 2 * k;
        const dd = d - 2 * k;
        if (w > 0 && dd > 0) box(-13, 11 + k, zC, w, 1, dd, 0x795548);
      }

      for (let yy = 7; yy <= 9; yy += 2) {
        for (let zz = z0 + 1; zz <= z1 - 1; zz += 2) {
          cube(-11, yy, zz, 0x263238);
        }
      }

      cube(-11, 6, zC, 0x5d4037);
    }

    function lighthouse(z) {
      box(-13, 11, z, 3, 11, 3, 0xf4f4f4);

      for (let y = 7; y <= 15; y += 2) {
        box(-13, y, z, 3, 1, 3, 0xc62828);
      }

      box(-13, 17, z, 4, 1, 4, 0x263238);
      box(-13, 19, z, 2, 3, 2, 0x263238);
      box(-13, 21, z, 3, 1, 3, 0x263238);
    }

    function crane(z) {
      box(-12, 7, z, 1, 3, 1, 0x37474f);

      for (let y = 8; y <= 14; y++) cube(-12, y, z, 0x37474f);

      box(-9, 14, z, 7, 1, 1, 0x455a64);
      box(-12, 12, z, 3, 1, 1, 0x546e7a);
      box(-6, 10, z, 1, 4, 1, 0x78909c);
      box(-6, 8, z, 2, 1, 2, 0x8d6e63);
    }

    function buildContainers() {
      const spots = [
        [-30, 3, 0xd32f2f],
        [-16, 2, 0x1976d2],
        [-1, 3, 0xfbc02d],
        [13, 2, 0x388e3c],
        [25, 2, 0x8e24aa],
      ];

      for (const [z, d, c] of spots) {
        box(-10.5, 6, z, 1, 1, d, c);
        box(-10.5, 7, z, 1, 1, d, c);
      }
    }

    function buildCrates() {
      const crateZ = [-30, -16, -1, 13, 25];
      for (const z of crateZ) {
        cube(-10.5, 6, z, 0x8d6e63);
        cube(-10.5, 7, z, 0xa1887f);
      }
    }

    function buoy(x, z, color) {
      cube(x, 1, z, color);
      cube(x, 2, z, 0xffffff);
      cube(x, 3, z, color);
      cube(x, 4, z, 0x212121);
    }

    function buildBuoys() {
      buoy(18, -28, 0xd32f2f);
      buoy(18, 28, 0x2e7d32);
      buoy(30, 0, 0xd32f2f);
    }

    function buildHarbor() {
      warehouse(-28, -22, 0xb34141);
      warehouse(-14, -8, 0x7c5e4f);
      warehouse(4, 12, 0x2b6d8e);
      warehouse(16, 22, 0x5d8b45);

      lighthouse(28);
      crane(0);
      crane(-18);

      buildContainers();
      buildCrates();
      buildBuoys();
    }

    function buildShip() {
      for (let x = -14; x <= 14; x++) {
        const zmax = shipZmax(x);

        for (let z = -zmax; z <= zmax; z++) {
          for (let y = 0; y <= 2; y++) {
            let col = 0x4e342e;
            if (y === 2) col = 0x6d4c41;
            if (Math.abs(z) === zmax) col = 0x795548;
            if (x >= -14 && x <= -13) col = 0x5d4037;
            cube(x, y, z, col, shipData);
          }

          if (Math.abs(z) < zmax) cube(x, 3, z, 0xc68a4f, shipData);
          if (Math.abs(z) === zmax) cube(x, 4, z, 0x8d6e63, shipData);
        }
      }

      for (let x = -13; x <= 13; x++) {
        const zmax = shipZmax(x);
        cube(x, 2, zmax, 0xa03a2e, shipData);
        cube(x, 2, -zmax, 0xa03a2e, shipData);
      }

      // Stern castle
      for (let x = -13; x <= -9; x++) {
        for (let z = -3; z <= 3; z++) {
          for (let y = 4; y <= 6; y++) {
            let col = 0xeceff1;
            if (Math.abs(z) === 3) col = 0xcfd8dc;
            if (y === 5 && z === -3 && x >= -11 && x <= -10) col = 0x263238;
            cube(x, y, z, col, shipData);
          }
        }
      }
      box(-11, 7, 0, 6, 1, 8, 0x5d4037, shipData);

      // Forecastle
      for (let x = 9; x <= 13; x++) {
        for (let z = -3; z <= 3; z++) {
          cube(x, 4, z, 0xeceff1, shipData);
        }
      }
      box(11, 5, 0, 6, 1, 8, 0x5d4037, shipData);

      // Deck cargo
      for (let x = -4; x <= 4; x += 2) {
        if (x === 0) continue;
        for (let z = -2; z <= 2; z += 2) {
          cube(x, 4, z, 0x8d6e63, shipData);
        }
      }
      cube(4, 4, 3, 0xa1887f, shipData);

      const masts = [
        { x: -10, y0: 7, y1: 27, half: 5, yards: [24, 20, 16] },
        { x: 0, y0: 4, y1: 31, half: 6, yards: [28, 23, 18, 13] },
        { x: 9, y0: 5, y1: 26, half: 4, yards: [23, 19] },
      ];

      for (const m of masts) {
        for (let y = m.y0; y <= m.y1; y++) {
          cube(m.x, y, 0, 0xbcaaa4, shipData);
        }

        for (const yd of m.yards) {
          for (let z = -m.half; z <= m.half; z++) {
            cube(m.x, yd, z, 0x8d6e63, shipData);
          }

          const yTop = yd - 1;
          const yBottom = yd - 6;

          for (let y = yBottom; y <= yTop; y++) {
            const t =
              yTop === yBottom ? 0 : (y - yBottom) / (yTop - yBottom);

            for (let z = -m.half + 1; z <= m.half - 1; z++) {
              const edge = 1 - Math.abs(z) / (m.half - 1);
              const billow = Math.round(edge * 2.2 * (0.75 + 0.25 * (1 - t)));
              const sx = m.x + billow;

              const c = y % 2 === 0 ? 0xf5f0e1 : 0xe6dec6;
              cube(sx, y, z, c, shipData);
              cube(sx + 1, y, z, c, shipData);
            }
          }
        }

        cube(m.x, m.y1 + 1, 0, 0xd32f2f, shipData);
        cube(m.x, m.y1 + 2, 0, 0xf44336, shipData);
        cube(m.x + 1, m.y1 + 2, 0, 0xf44336, shipData);
      }

      // Bowsprit
      for (let x = 15; x <= 20; x++) {
        const y = 9 + Math.round((x - 15) * 0.4);
        cube(x, y, 0, 0xbcaaa4, shipData);
        cube(x, y - 1, 0, 0x8d6e63, shipData);
      }
      cube(21, 12, 0, 0xd32f2f, shipData);

      // Jib sails on the sides
      for (let x = -9; x <= 20; x++) {
        const t = (x + 9) / 29;
        const top = Math.round(24 + (11 - 24) * t);
        const bottom = Math.round(6 + (11 - 6) * t);

        for (let y = bottom; y <= top; y++) {
          const c = y % 2 === 0 ? 0xf5f0e1 : 0xe6dec6;
          cube(x, y, 7, c, shipData);
          cube(x, y, -7, c, shipData);
        }
      }

      // Small lifeboat
      for (let x = -7; x <= -2; x++) {
        cube(x, 5, 8, 0xf5f5f5, shipData);
        cube(x, 4, 8, 0xd7ccc8, shipData);
      }
      cube(-4, 4, 9, 0xbcaaa4, shipData);

      // Stern flag
      cube(-14, 7, 0, 0x1e88e5, shipData);
      cube(-15, 7, 0, 0x42a5f5, shipData);
    }

    function buildSea() {
      const color = new THREE.Color();

      for (let x = -10; x <= 44; x++) {
        for (let z = -44; z <= 44; z++) {
          const dist = Math.hypot(x - 5, z);
          if (dist > 54) continue;

          // Keep water out of the ship footprint.
          if (x >= -9 && x <= 7 && Math.abs(z) <= 16) continue;

          let h, s, l;

          if (x < -2 && Math.abs(z) < 34) {
            h = 0.52;
            s = 0.72;
            l = 0.46 + Math.random() * 0.08;
          } else if (dist > 34) {
            h = 0.57;
            s = 0.75;
            l = 0.24 + Math.random() * 0.05;
          } else {
            h = 0.535;
            s = 0.70;
            l = 0.36 + Math.random() * 0.08;
          }

          color.setHSL(h, s, l);

          if (x === -10 && Math.abs(z) < 32) {
            color.setHSL(0.55, 0.4, 0.78);
          }

          waterData.push({
            x,
            z,
            y: -0.5,
            phase: Math.random() * Math.PI * 2,
            color: color.clone(),
          });
        }
      }
    }

    function buildClouds() {
      function puff(cx, cy, cz) {
        const parts = [
          [0, 0, 0, 3, 1, 3],
          [3, 0, 0, 2, 1, 2],
          [-3, 0, 0, 2, 1, 2],
          [0, 0, 3, 2, 1, 2],
          [0, 0, -3, 2, 1, 2],
          [0, 1, 0, 2, 1, 2],
          [2, 1, 0, 1, 1, 1],
          [-2, 1, 0, 1, 1, 1],
          [0, 1, 2, 1, 1, 1],
          [0, 1, -2, 1, 1, 1],
        ];

        for (const p of parts) {
          box(cx + p[0], cy + p[1], cz + p[2], p[3], p[4], p[5], 0xffffff, cloudData);
        }
      }

      puff(18, 43, -22);
      puff(-22, 47, 26);
      puff(40, 39, 8);
      puff(-4, 52, 36);
      puff(52, 37, -14);
    }

    function buildInstanced(data, material, castShadow, receiveShadow) {
      if (!data.length) return null;

      const geometry = new THREE.BoxGeometry(1, 1, 1);
      const mesh = new THREE.InstancedMesh(geometry, material, data.length);
      const dummy = new THREE.Object3D();

      for (let i = 0; i < data.length; i++) {
        const d = data[i];

        dummy.position.set(d.x, d.y, d.z);
        dummy.scale.set(d.w, d.h, d.d);
        dummy.rotation.set(0, 0, 0);
        dummy.updateMatrix();

        mesh.setMatrixAt(i, dummy.matrix);
        mesh.setColorAt(i, d.color);
      }

      mesh.instanceMatrix.needsUpdate = true;
      if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;

      mesh.castShadow = castShadow;
      mesh.receiveShadow = receiveShadow;
      scene.add(mesh);

      return mesh;
    }

    buildLand();
    buildQuay();
    buildHarbor();
    buildShip();
    buildSea();
    buildClouds();

    const staticMesh = buildInstanced(staticData, staticMat, true, true);
    const shipMesh = buildInstanced(shipData, shipMat, true, true);
    const waterMesh = buildInstanced(waterData, waterMat, false, true);
    const cloudMesh = buildInstanced(cloudData, cloudMat, false, false);

    if (shipMesh) {
      shipMesh.rotation.y = Math.PI / 2;
      shipMesh.position.set(-1, 0, 0);
    }

    const lighthouseLight = new THREE.Mesh(
      new THREE.SphereGeometry(1.1, 14, 14),
      new THREE.MeshBasicMaterial({ color: 0xfff59d, fog: false })
    );
    lighthouseLight.position.set(-13, 20, 28);
    scene.add(lighthouseLight);

    const lightGlow = new THREE.Mesh(
      new THREE.SphereGeometry(2.2, 14, 14),
      new THREE.MeshBasicMaterial({
        color: 0xfff59d,
        transparent: true,
        opacity: 0.18,
        fog: false,
      })
    );
    lightGlow.position.copy(lighthouseLight.position);
    scene.add(lightGlow);

    const clock = new THREE.Clock();
    const dummy = new THREE.Object3D();

    function animate() {
      requestAnimationFrame(animate);

      const t = clock.getElapsedTime();

      if (waterMesh) {
        for (let i = 0; i < waterData.length; i++) {
          const w = waterData[i];

          const y =
            w.y +
            Math.sin(t * 0.65 + w.phase + w.x * 0.18 + w.z * 0.14) * 0.30;

          dummy.position.set(w.x, y, w.z);
          dummy.scale.set(1, 1, 1);
          dummy.rotation.set(0, 0, 0);
          dummy.updateMatrix();

          waterMesh.setMatrixAt(i, dummy.matrix);
        }

        waterMesh.instanceMatrix.needsUpdate = true;
      }

      if (shipMesh) {
        shipMesh.position.y = Math.sin(t * 0.7) * 0.12;
        shipMesh.rotation.z = Math.sin(t * 0.55) * 0.016;
        shipMesh.rotation.x = Math.sin(t * 0.45) * 0.011;
      }

      const pulse = Math.max(0, Math.sin(t * 2.5));
      lighthouseLight.scale.setScalar(1 + pulse * 0.45);
      lightGlow.scale.setScalar(2.0 + pulse * 1.45);
      lightGlow.material.opacity = 0.12 + pulse * 0.18;

      if (cloudMesh) {
        cloudMesh.position.x = Math.sin(t * 0.04) * 12;
      }

      controls.update();
      renderer.render(scene, camera);
    }

    animate();

    window.addEventListener("resize", () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    });
  </script>
</body>
</html>
```