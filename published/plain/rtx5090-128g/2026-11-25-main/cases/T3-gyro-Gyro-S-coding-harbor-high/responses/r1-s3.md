Save the following as a single `.html` file (for example `harbor.html`) and open it in Chrome. It uses Three.js from a CDN.

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
      height: 100%;
      overflow: hidden;
      background: #9bc6d4;
    }
    canvas {
      display: block;
    }
    #hint {
      position: fixed;
      bottom: 12px;
      left: 12px;
      padding: 8px 11px;
      border-radius: 6px;
      background: rgba(0, 0, 0, 0.38);
      color: #f2f2f2;
      font: 13px/1.3 system-ui, sans-serif;
    }
  </style>
</head>
<body>
  <div id="hint">Drag to orbit • scroll to zoom • right-drag to pan</div>

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

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x9bc6d4);
    scene.fog = new THREE.Fog(0x9bc6d4, 45, 120);

    const camera = new THREE.PerspectiveCamera(
      45,
      window.innerWidth / window.innerHeight,
      0.1,
      220
    );
    camera.position.set(-22, 16, 24);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.target.set(2, 4, 0);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.autoRotate = true;
    controls.autoRotateSpeed = 0.55;
    controls.minDistance = 10;
    controls.maxDistance = 70;
    controls.maxPolarAngle = Math.PI / 2;
    controls.update();

    scene.add(new THREE.HemisphereLight(0xb9e4ff, 0x3f5561, 0.65));

    const sun = new THREE.DirectionalLight(0xffd6a5, 1.05);
    sun.position.set(20, 30, 14);
    scene.add(sun);

    const unitBox = new THREE.BoxGeometry(1, 1, 1);

    function voxel(parent, x, y, z, sx, sy, sz, colorHex, opts = {}) {
      const mat = new THREE.MeshPhongMaterial({
        color: colorHex,
        flatShading: true,
        shininess: opts.shininess ?? 8,
        transparent: opts.transparent ?? false,
        opacity: opts.opacity ?? 1
      });

      const mesh = new THREE.Mesh(unitBox, mat);
      mesh.position.set(x, y, z);
      mesh.scale.set(sx, sy, sz);

      if (opts.rotation) {
        mesh.rotation.set(
          opts.rotation.x || 0,
          opts.rotation.y || 0,
          opts.rotation.z || 0
        );
      }

      parent.add(mesh);
      return mesh;
    }

    function segment(parent, a, b, colorHex, thickness = 0.15) {
      const dir = new THREE.Vector3().subVectors(b, a);
      const len = dir.length();
      dir.normalize();

      const mesh = new THREE.Mesh(
        new THREE.BoxGeometry(thickness, thickness, len),
        new THREE.MeshPhongMaterial({ color: colorHex, flatShading: true })
      );

      mesh.position.copy(a).addScaledVector(dir, len / 2);
      mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 0, 1), dir);
      parent.add(mesh);
      return mesh;
    }

    const ropeColor = 0x2b2622;
    const sailColor = 0xf3e5c4;
    const sailColor2 = 0xe4d2b1;
    const wood = 0x7b543b;
    const woodLight = 0x9c6c48;
    const stone = 0x8b8675;
    const stoneDark = 0x666255;
    const dockTop = 2.85;

    // ---------- Animated voxel water ----------
    const waterCenterX = 4;
    const waterCenterZ = 0;
    const waterN = 44;
    const waterSpacing = 1.45;
    const waterCount = waterN * waterN;

    const waterGeo = new THREE.BoxGeometry(1.65, 1.65, 1.65);
    const waterMat = new THREE.MeshPhongMaterial({
      vertexColors: true,
      flatShading: true,
      shininess: 20
    });

    const water = new THREE.InstancedMesh(waterGeo, waterMat, waterCount);
    scene.add(water);

    const waterPositions = [];
    const dummy = new THREE.Object3D();

    const cDeep = new THREE.Color(0x25476b);
    const cMid = new THREE.Color(0x397099);
    const cLight = new THREE.Color(0x54a3c4);

    let waterIdx = 0;
    for (let j = 0; j < waterN; j++) {
      for (let i = 0; i < waterN; i++) {
        const x = waterCenterX - (waterN / 2) * waterSpacing + i * waterSpacing;
        const z = waterCenterZ - (waterN / 2) * waterSpacing + j * waterSpacing;

        waterPositions.push({ x, z });

        const rnd = Math.sin(x * 12.9898 + z * 78.233) * 43758.5453;
        const frac = rnd - Math.floor(rnd);

        const col = new THREE.Color();
        if (frac < 0.25) {
          col.lerpColors(cDeep, cMid, 0.3 + frac * 1.6);
        } else if (frac < 0.75) {
          col.lerpColors(cMid, cLight, (frac - 0.25) / 0.5);
        } else {
          col.lerpColors(cLight, cMid, (frac - 0.75) / 0.25);
        }

        water.setColorAt(waterIdx, col);

        dummy.position.set(x, -0.85, z);
        dummy.updateMatrix();
        water.setMatrixAt(waterIdx, dummy.matrix);

        waterIdx++;
      }
    }

    water.instanceColor.needsUpdate = true;

    // ---------- Harbor quay / dock ----------
    const dock = new THREE.Group();
    scene.add(dock);

    // Stone quay wall facing the ship
    voxel(dock, 5.6, 1.1, 0, 1.2, 4.2, 18, stoneDark);

    // Land behind the dock
    voxel(dock, 12.2, 1.25, 0, 13.2, 2.5, 28, stone);

    // Wooden dock deck
    voxel(dock, 12.2, 2.6, 0, 13.2, 0.5, 28, wood);

    // Dock plank seams
    for (let z = -12; z <= 12; z += 4) {
      voxel(dock, 12.2, 2.72, z, 13.2, 0.16, 0.5, 0x6f533b);
    }
    for (let x = 6; x <= 18; x += 4) {
      voxel(dock, x, 2.72, 0, 0.5, 0.16, 28, 0x6f533b);
    }

    // Bollards and mooring ropes
    const mooringZ = [-3, 0, 3];
    for (const z of mooringZ) {
      voxel(dock, 5.8, 2.7, z, 0.45, 1.1, 0.45, 0x3f362d);
      voxel(dock, 5.8, 3.3, z, 0.65, 0.35, 0.65, 0x2b2622);
      segment(
        dock,
        new THREE.Vector3(2.0, 2.55, z),
        new THREE.Vector3(5.8, 2.95, z),
        ropeColor,
        0.12
      );
    }

    // Cargo crates stacked along the dock edge
    for (let k = 0; k < 14; k++) {
      const x = 6.8 + (k % 3) * 1.1;
      const z = -10 + Math.floor(k / 3) * 3.5;
      if (z <= 9) {
        voxel(dock, x, 3.2, z, 1.1, 1.0, 1.1, k % 2 ? 0xa37f54 : 0x8a6341);
      }
    }

    // ---------- Harbor town / warehouse ----------
    const town = new THREE.Group();
    scene.add(town);

    function house(parent, x, z, w, d, h, bodyHex, roofHex) {
      voxel(parent, x, dockTop + h / 2, z, w, h, d, bodyHex);

      for (let step = 0; step < 4; step++) {
        const rw = w + 1.0 - step * 0.7;
        const rd = d + 1.0 - step * 0.7;
        voxel(
          parent,
          x,
          dockTop + h + 0.3 + step * 0.35,
          z,
          rw,
          0.35,
          rd,
          roofHex
        );
      }

      // Window strip on the quay-facing side
      voxel(
        parent,
        x - w / 2 - 0.1,
        dockTop + h / 2,
        z - d / 2 + 1,
        0.2,
        h * 0.5,
        1.0,
        0xe2d7b6
      );
    }

    house(town, 14.5, -10, 4.5, 5.5, 3.2, 0xd0b58f, 0x7e4a38);
    house(town, 18.5, -6, 4.0, 4.0, 3.8, 0xc7a882, 0x8a493a);
    house(town, 17.0, 4, 5.0, 5.0, 2.8, 0xd6c099, 0x6f4436);
    house(town, 13.5, 10, 3.5, 3.5, 2.6, 0xc1a379, 0x784636);

    // Warehouse near the dock
    voxel(town, 13, dockTop + 1.2, 8, 3.6, 2.4, 3.6, 0xa79178);
    voxel(town, 13, dockTop + 2.5, 8, 4.2, 0.4, 4.2, 0x654238);

    // ---------- Lighthouse ----------
    const lighthouse = new THREE.Group();
    scene.add(lighthouse);

    voxel(lighthouse, 21, 3.3, -13, 3.2, 1.0, 3.2, stoneDark);

    for (let y = 3.5; y < 10; y += 0.5) {
      const stripe = Math.floor(y * 2) % 2 === 0 ? 0xe9eee3 : 0xd44a45;
      voxel(lighthouse, 21, y, -13, 2.2, 0.5, 2.2, stripe);
    }

    voxel(lighthouse, 21, 10.1, -13, 2.0, 0.7, 2.0, 0x303030);
    voxel(lighthouse, 21, 10.6, -13, 1.2, 0.8, 1.2, 0xffcf68, { shininess: 35 });
    voxel(lighthouse, 21, 11.15, -13, 1.6, 0.3, 1.6, 0xa23b32);

    // ---------- Crane ----------
    const crane = new THREE.Group();
    scene.add(crane);

    voxel(crane, 7, dockTop + 1.5, -9, 0.6, 3.0, 0.6, wood);
    voxel(crane, 7, dockTop + 1.7, -8.2, 1.2, 0.4, 1.2, woodLight);
    segment(
      crane,
      new THREE.Vector3(7, dockTop + 1.8, -8.2),
      new THREE.Vector3(10.5, dockTop + 2.5, -6),
      woodLight,
      0.22
    );
    segment(
      crane,
      new THREE.Vector3(7, dockTop + 1.8, -8.2),
      new THREE.Vector3(7, dockTop + 1.2, -8.2),
      ropeColor,
      0.1
    );
    voxel(crane, 9.4, dockTop + 0.7, -6.7, 1.2, 1.2, 1.2, 0x8d6747);

    // ---------- Sailing ship ----------
    const shipGroup = new THREE.Group();
    scene.add(shipGroup);

    const hull = new THREE.Group();
    shipGroup.add(hull);

    const deckTop = 2.55;

    // Hull blocks along the ship length
    for (let z = -6; z <= 6; z += 1) {
      const t = (z + 6) / 12;
      let w = 0.8 + 2.6 * Math.sin(Math.PI * t);
      w = Math.max(0.8, w);

      // Submerged lower hull
      voxel(hull, 0, -0.5, z, w * 0.75, 1.2, 1, 0x452a1d);

      // Main hull side
      voxel(hull, 0, 1.0, z, w, 2.0, 1, 0x5f3a2a);

      // Deck cap
      voxel(hull, 0, 2.25, z, w + 0.2, 0.6, 1, woodLight);

      // Rail / gunwale
      voxel(hull, 0, 2.5, z, w + 0.5, 0.25, 1, 0x6f4832);
    }

    // Bow extension
    voxel(hull, 0, 1.0, 6.8, 0.5, 1.8, 1.0, 0x5f3a2a);
    voxel(hull, 0, 2.25, 6.8, 0.7, 0.5, 1.0, woodLight);

    // Stern extension
    voxel(hull, 0, 1.0, -6.8, 0.5, 1.8, 1.0, 0x5f3a2a);
    voxel(hull, 0, 2.25, -6.8, 0.7, 0.5, 1.0, woodLight);

    // Bowsprit
    segment(
      shipGroup,
      new THREE.Vector3(0, 2.6, 6.8),
      new THREE.Vector3(0, 3.7, 9.3),
      0x6d4b33,
      0.18
    );
    voxel(shipGroup, 0, 3.7, 9.4, 0.5, 0.3, 0.5, 0x6d4b33);

    // Stern cabin
    voxel(hull, 0, deckTop + 1.1, -4, 2.3, 2.2, 3.2, 0x8b4334);
    voxel(hull, 0, deckTop + 2.35, -4, 2.7, 0.35, 3.5, 0x5f3128);
    voxel(hull, 1.2, deckTop + 1.1, -2.5, 0.2, 0.5, 1.2, 0xd7c093);
    voxel(hull, 1.2, deckTop + 1.1, -5.5, 0.2, 0.5, 1.2, 0xd7c093);

    // Cargo on ship deck
    const shipCargo = [
      [-1.1, 3.1, 1.4, 0.9, 0.9, 0.9, 0x9f704b],
      [1.1, 3.1, 1.4, 0.9, 0.9, 0.9, 0x846041],
      [-0.8, 3.15, -0.8, 0.7, 0.7, 0.7, 0xaa7754],
      [1.0, 3.15, -1.0, 1.1, 1.1, 1.1, 0x75523a],
      [0, 3.3, 2.3, 0.75, 0.75, 0.75, 0xb07c55]
    ];
    for (const c of shipCargo) {
      voxel(hull, c[0], c[1], c[2], c[3], c[4], c[5], c[6]);
    }

    // Masts, yards, sails, rigging
    const masts = [
      { z: -3.4, h: 7.5, sailW: [4.2, 3.2] },
      { z: 0, h: 11.5, sailW: [7.2, 5.8, 4.2] },
      { z: 3.4, h: 8.0, sailW: [5.2, 3.6] }
    ];

    for (const m of masts) {
      const mastTop = deckTop + m.h;

      voxel(shipGroup, 0, deckTop + m.h / 2, m.z, 0.55, m.h, 0.55, 0x4a3428);
      voxel(shipGroup, 0, mastTop + 0.1, m.z, 0.6, 0.2, 0.6, 0x4a3428);

      const n = m.sailW.length;
      for (let i = 0; i < n; i++) {
        const tt = n === 1 ? 0.5 : i / (n - 1);
        const yardY = deckTop + 3.0 + tt * (m.h - 5.0);
        const w = m.sailW[i];

        // Yard
        voxel(shipGroup, 0, yardY, m.z, w + 1.1, 0.35, 0.35, 0x4a3428);

        // Sail below the yard
        const bottom = Math.max(
          deckTop + 0.5,
          yardY - Math.min(3.2, yardY - deckTop - 1.0)
        );
        const sailH = Math.max(1.0, yardY - bottom);
        const col = i === 0 ? sailColor : sailColor2;

        voxel(
          shipGroup,
          0,
          (yardY + bottom) / 2,
          m.z,
          w,
          sailH,
          0.5,
          col
        );
      }

      // Flag
      voxel(shipGroup, 0, mastTop + 0.75, m.z, 1.1, 0.35, 0.3, 0xc83b3b);

      // Shroud lines
      const top = new THREE.Vector3(0, mastTop, m.z);
      for (const sx of [-1.6, 1.6]) {
        segment(
          shipGroup,
          top,
          new THREE.Vector3(sx, deckTop, m.z + 2),
          ropeColor,
          0.12
        );
        segment(
          shipGroup,
          top,
          new THREE.Vector3(sx, deckTop, m.z - 2),
          ropeColor,
          0.12
        );
      }
    }

    // Main stays
    const mainTop = deckTop + 11.5;
    segment(
      shipGroup,
      new THREE.Vector3(0, mainTop, 0),
      new THREE.Vector3(0, deckTop, 6),
      ropeColor,
      0.14
    );
    segment(
      shipGroup,
      new THREE.Vector3(0, mainTop, 0),
      new THREE.Vector3(0, deckTop, -6),
      ropeColor,
      0.14
    );

    // Fore and mizzen stays
    segment(
      shipGroup,
      new THREE.Vector3(0, deckTop + 8.0, 3.4),
      new THREE.Vector3(0, deckTop, 6),
      ropeColor,
      0.12
    );
    segment(
      shipGroup,
      new THREE.Vector3(0, deckTop + 7.5, -3.4),
      new THREE.Vector3(0, deckTop, -6),
      ropeColor,
      0.12
    );

    // ---------- Blocky clouds ----------
    const clouds = new THREE.Group();
    scene.add(clouds);

    function cloud(x, y, z, s = 1) {
      voxel(clouds, x, y, z, 3.2 * s, 1.1 * s, 2.6 * s, 0xf1efe9);
      voxel(clouds, x + 2 * s, y + 0.35 * s, z + 1.1 * s, 2.2 * s, 0.9 * s, 1.8 * s, 0xf8f6f1);
      voxel(clouds, x - 1.3 * s, y + 0.25 * s, z - 1.1 * s, 2.1 * s, 0.9 * s, 1.7 * s, 0xe6e1d8);
    }

    cloud(-16, 18, -12, 1.0);
    cloud(24, 19, 16, 1.2);
    cloud(-6, 22, 18, 1.1);
    cloud(26, 23, -20, 0.9);

    // ---------- Animation ----------
    const clock = new THREE.Clock();

    function animate() {
      const t = clock.getElapsedTime();

      // Gentle water waves
      for (let i = 0; i < waterPositions.length; i++) {
        const p = waterPositions[i];
        const wave =
          Math.sin(t * 1.2 + p.x * 0.22 + p.z * 0.17) * 0.13 +
          Math.sin(t * 1.8 + p.x * 0.18 - p.z * 0.24) * 0.09;

        dummy.position.set(p.x, -0.85 + wave, p.z);
        dummy.updateMatrix();
        water.setMatrixAt(i, dummy.matrix);
      }

      water.instanceMatrix.needsUpdate = true;

      // Ship gently bobbing at mooring
      shipGroup.position.y = Math.sin(t * 1.1) * 0.07;
      shipGroup.rotation.z = Math.sin(t * 0.65) * 0.015;

      // Clouds drift very slowly
      clouds.position.x = Math.sin(t * 0.04) * 2.0;
      clouds.position.z = Math.cos(t * 0.03) * 1.0;

      controls.update();
      renderer.render(scene, camera);
    }

    renderer.setAnimationLoop(animate);

    window.addEventListener("resize", () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    });
  </script>
</body>
</html>
```