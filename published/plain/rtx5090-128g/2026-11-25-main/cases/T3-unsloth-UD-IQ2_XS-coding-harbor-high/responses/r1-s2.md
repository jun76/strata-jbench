Here is a complete single-file 3D voxel scene. Paste it into a `.html` file and open it in Chrome. It loads Three.js from a CDN and renders immediately with mouse orbit/zoom/pan.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Voxel Harbor — Sailing Ship Calling</title>
  <style>
    html, body {
      margin: 0;
      height: 100%;
      overflow: hidden;
      background: #102438;
    }
    canvas { display: block; }
    #ui {
      position: fixed;
      left: 12px;
      top: 12px;
      color: #fff;
      font: 12px/1.4 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
      background: rgba(0, 0, 0, 0.38);
      padding: 8px 10px;
      border-radius: 8px;
      pointer-events: none;
    }
  </style>
</head>
<body>
  <div id="ui">Drag: rotate · Scroll/pinch: zoom · Right-drag: pan</div>

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

    const renderer = new THREE.WebGLRenderer({ antialias: false });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.NoToneMapping;
    document.body.appendChild(renderer.domElement);

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xa4d0f0);
    scene.fog = new THREE.Fog(0xa4d0f0, 115, 330);

    const camera = new THREE.PerspectiveCamera(
      50,
      window.innerWidth / window.innerHeight,
      0.1,
      1000
    );
    camera.position.set(-36, 26, 2);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.target.set(0, 8, 0);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.minDistance = 20;
    controls.maxDistance = 170;
    controls.maxPolarAngle = Math.PI * 0.45;

    scene.add(new THREE.AmbientLight(0x223344, 0.35));

    const hemi = new THREE.HemisphereLight(0xc8e8ff, 0x334038, 1.0);
    scene.add(hemi);

    const sun = new THREE.DirectionalLight(0xfff3d0, 1.6);
    sun.position.set(60, 70, 25);
    scene.add(sun);

    const box = new THREE.BoxGeometry(1, 1, 1);

    function noise(x, y, z = 0) {
      const s = Math.sin(x * 127.1 + y * 311.7 + z * 74.7) * 43758.5453123;
      return s - Math.floor(s);
    }

    function pick(arr, x = 0, y = 0, z = 0) {
      return arr[Math.floor(Math.abs(noise(x, y, z)) * arr.length) % arr.length];
    }

    const COL = {
      darkWood: "#3b2a1b",
      wood: "#6f4c2c",
      woodDark: "#4a3624",
      woodLight: "#9b6e49",
      sail: "#f4f1e7",
      sailDark: "#dcd5c5",
      stone: ["#8c8d89", "#737470", "#a6a7a2"],
      sand: ["#d4c091", "#c1ad81", "#e0cc9d"],
      grass: ["#49a35e", "#3e8d4f", "#58b56c"],
      dirt: ["#7a654e", "#635142"],
      water: ["#2b87c4", "#1f6f9f", "#35a0cc", "#2888c0"],
      white: "#f6f6f6",
      red: "#c84747",
      glass: "#aee7ff",
      woodPal: ["#5f4028", "#6f4c2c", "#7d5732"]
    };

    const occupied = new Set();

    function occupy(x, z) {
      occupied.add(Math.round(x) + "," + Math.round(z));
    }

    function isOccupied(x, z) {
      return occupied.has(Math.round(x) + "," + Math.round(z));
    }

    const staticMap = new Map();

    function addTo(map, x, y, z, c) {
      if (!map.has(c)) map.set(c, []);
      map.get(c).push([x, y, z]);
    }

    function addVoxel(x, y, z, c) {
      addTo(staticMap, x, y, z, c);
    }

    function addOccupiedVoxel(x, y, z, c) {
      addVoxel(x, y, z, c);
      occupy(x, z);
    }

    function makeMapGroup(map) {
      const group = new THREE.Group();
      const m = new THREE.Matrix4();

      for (const [color, pts] of map) {
        if (!pts.length) continue;

        const mat = new THREE.MeshLambertMaterial({ color });
        const inst = new THREE.InstancedMesh(box, mat, pts.length);

        pts.forEach((p, i) => {
          m.makeTranslation(p[0], p[1], p[2]);
          inst.setMatrixAt(i, m);
        });

        group.add(inst);
      }

      return group;
    }

    // ---------------- Harbor land ----------------

    const shoreAt = (z) =>
      14 + Math.sin(z * 0.075) * 5 + Math.cos(z * 0.225) * 3;

    function landHeight(x, z) {
      const sh = shoreAt(z);
      if (x < sh) return 0;

      // Flat harbor town area
      if (x >= 17 && x <= 42 && z >= -16 && z <= 16) return 2;

      let h = Math.floor((x - sh) * 0.20) + 1;

      const hill =
        Math.sin((x - 18) * 0.09) *
          Math.cos((z + 12) * 0.11) *
          1.6 +
        Math.sin((x + z) * 0.04) *
          0.8;

      h = Math.max(1, Math.min(5, Math.floor(h + hill + 0.3)));
      return h;
    }

    for (let x = 6; x <= 65; x++) {
      for (let z = -55; z <= 55; z++) {
        const h = landHeight(x, z);
        if (h <= 0) continue;

        for (let layer = 0; layer < h; layer++) {
          const y = layer + 0.5;
          let c;

          if (layer === h - 1) {
            if (x < shoreAt(z) + 1.5 || h === 1) {
              c = pick(COL.sand, x, z, y);
            } else {
              c = pick(COL.grass, x, z, y);
            }
          } else {
            c = pick(COL.dirt, x, z, y);
          }

          addOccupiedVoxel(x, y, z, c);
        }
      }
    }

    // ---------------- Rocks and breakwater ----------------

    function addRockColumn(x, z, h) {
      if (isOccupied(x, z)) return;

      for (let layer = 0; layer < h; layer++) {
        addOccupiedVoxel(
          x,
          layer + 0.5,
          z,
          pick(COL.stone, x, z, layer)
        );
      }
    }

    // Lighthouse rocky islet
    for (let dx = -6; dx <= 6; dx++) {
      for (let dz = -6; dz <= 6; dz++) {
        const d2 = dx * dx + dz * dz;
        if (d2 <= 30) {
          const h = d2 <= 9 ? 3 : 2;
          addRockColumn(6 + dx, -22 + dz, h);
        }
      }
    }

    // Breakwater arm toward shore
    for (let x = 7; x <= 15; x++) {
      const cz = -17 + (x - 15) * 0.555555;
      for (let dz = -2; dz <= 2; dz++) {
        const z = Math.round(cz + dz);
        const h =
          1 +
          (Math.abs(dz) === 0 ? 1 : 0) +
          (noise(x, z, 7) > 0.6 ? 1 : 0);
        addRockColumn(x, z, h);
      }
    }

    // ---------------- Lighthouse ----------------

    const lampMaterial = new THREE.MeshBasicMaterial({
      color: 0xffdd66,
      fog: false
    });

    const lampMesh = new THREE.Mesh(box, lampMaterial);
    lampMesh.position.set(6, 14.5, -22);
    scene.add(lampMesh);

    const lampLight = new THREE.PointLight(0xffdd77, 2, 90, 0);
    lampLight.position.set(6, 14.5, -22);
    scene.add(lampLight);

    (function addLighthouse() {
      const lx = 6;
      const lz = -22;

      // Tower
      for (let layer = 0; layer < 10; layer++) {
        const y = 3.5 + layer;
        const color = layer % 2 === 0 ? COL.white : COL.red;
        const r = layer < 7 ? 1 : 0;

        for (let dx = -r; dx <= r; dx++) {
          for (let dz = -r; dz <= r; dz++) {
            addVoxel(lx + dx, y, lz + dz, color);
          }
        }
      }

      // Gallery
      for (let dx = -1; dx <= 1; dx++) {
        for (let dz = -1; dz <= 1; dz++) {
          addVoxel(lx + dx, 13.5, lz + dz, COL.woodDark);
        }
      }

      // Cap
      addVoxel(lx, 15.5, lz, COL.red);
    })();

    // ---------------- Town / harbor buildings ----------------

    function addHouse(ox, oz) {
      const w = 3;
      const d = 3;

      const wall = pick(
        ["#e8d7b7", "#d8c5a8", "#cbb395", "#f0e4cc"],
        ox,
        oz,
        1
      );

      const roof = pick(
        ["#b5553e", "#7d4236", "#5f4438", "#c96a48"],
        ox,
        oz,
        2
      );

      const h = 3 + Math.floor(noise(ox, oz, 3) * 3);
      const y0 = 2.5;

      for (let x = ox; x < ox + w; x++) {
        for (let z = oz; z < oz + d; z++) {
          for (let ly = 0; ly < h; ly++) {
            let c = wall;

            const perimeter =
              x === ox ||
              x === ox + w - 1 ||
              z === oz ||
              z === oz + d - 1;

            if (perimeter && ly >= 1 && noise(x, z, ly) < 0.16) {
              c = COL.glass;
            }

            if (perimeter && ly === 0 && z === oz + d - 1 && x === ox + 1) {
              c = COL.woodDark;
            }

            addVoxel(x, y0 + ly, z, c);
          }
        }
      }

      const layers = Math.ceil(Math.max(w, d) / 2);

      for (let r = 0; r < layers; r++) {
        const x0 = ox + r;
        const x1 = ox + w - 1 - r;
        const z0 = oz + r;
        const z1 = oz + d - 1 - r;

        if (x1 < x0 || z1 < z0) break;

        const y = y0 + h + r;

        for (let x = x0; x <= x1; x++) {
          for (let z = z0; z <= z1; z++) {
            addVoxel(x, y, z, roof);
          }
        }
      }
    }

    for (let x = 20; x <= 38; x += 6) {
      for (let z = -12; z <= 12; z += 6) {
        if (noise(x, z, 4) > 0.22) {
          addHouse(x, z);
        }
      }
    }

    // ---------------- Pier ----------------

    const dockPal = ["#7a5633", "#6d4c2b", "#86603b"];

    for (let x = 5; x <= 17; x++) {
      for (let z = -1; z <= 1; z++) {
        if (!isOccupied(x, z)) {
          addVoxel(x, 1.5, z, pick(dockPal, x, z, 0));
        }
      }
    }

    // Posts just outside the deck, above waterline
    for (let x = 5; x <= 17; x += 4) {
      for (const z of [-2, 2]) {
        if (!isOccupied(x, z)) {
          addVoxel(x, 0.5, z, COL.woodDark);
          addVoxel(x, 1.5, z, COL.woodDark);
        }
      }
    }

    // Bollards
    for (let x = 7; x <= 17; x += 4) {
      if (!isOccupied(x, 1)) {
        addVoxel(x, 2.5, 1, COL.darkWood);
      }
    }

    // Crates
    for (let x = 9; x <= 10; x++) {
      for (let z = -1; z <= 0; z++) {
        if (!isOccupied(x, z)) {
          addVoxel(x, 2.5, z, COL.woodLight);
        }
      }
    }

    if (!isOccupied(9, 0)) addVoxel(9, 3.5, 0, COL.woodDark);
    if (!isOccupied(10, -1)) addVoxel(10, 3.5, -1, COL.woodLight);

    // ---------------- Water ----------------

    const waterData = [];

    for (let x = -70; x <= 70; x++) {
      for (let z = -70; z <= 70; z++) {
        if (isOccupied(x, z)) continue;

        waterData.push({
          x,
          z,
          color: new THREE.Color(pick(COL.water, x, z, 0))
        });
      }
    }

    const waterMesh = new THREE.InstancedMesh(
      box,
      new THREE.MeshLambertMaterial({ color: 0xffffff }),
      waterData.length
    );

    waterMesh.instanceColor = new THREE.InstancedBufferAttribute(
      new Float32Array(waterData.length * 3),
      3
    );

    const waterMatrix = new THREE.Matrix4();

    waterData.forEach((d, i) => {
      waterMatrix.makeTranslation(d.x, -0.5, d.z);
      waterMesh.setMatrixAt(i, waterMatrix);
    });

    scene.add(waterMesh);

    function updateWater(t) {
      const arr = waterMesh.instanceColor.array;

      for (let i = 0; i < waterData.length; i++) {
        const d = waterData[i];

        const s = 0.5 + 0.5 * Math.sin(d.x * 0.25 + d.z * 0.18 + t * 1.4);
        const c = 0.5 + 0.5 * Math.cos(d.x * 0.12 - d.z * 0.28 + t * 0.9);
        const wave = s * c;

        const white = Math.pow(wave, 4) * 0.26;

        arr[i * 3] = Math.min(
          1,
          Math.max(0, d.color.r * (1 - wave * 0.15) + white)
        );

        arr[i * 3 + 1] = Math.min(
          1,
          Math.max(0, d.color.g * (1 - wave * 0.15) + white)
        );

        arr[i * 3 + 2] = Math.min(
          1,
          Math.max(0, d.color.b * (1 - wave * 0.15) + white)
        );
      }

      waterMesh.instanceColor.needsUpdate = true;
    }

    // ---------------- Ship ----------------

    const shipMap = new Map();

    function addShip(x, y, z, c) {
      addTo(shipMap, x, y + 0.5, z, c);
    }

    function hullHalfWidth(x) {
      if (x >= 13 || x <= -13) return 0;
      if (x < -9) return Math.max(1, Math.round(6 - (-9 - x) * 0.7));
      if (x > 8) return Math.max(0, Math.round(6 - (x - 8) * 1.2));
      return 6;
    }

    function hullTop(x, z) {
      let t =
        4 -
        Math.max(0, Math.abs(z) - 3) * 0.5 -
        Math.max(0, Math.abs(x) - 8) * 0.45;

      // Support for forecastle / aftcastle
      if (x >= 7 && x <= 11 && Math.abs(z) <= 3) t = Math.max(t, 4);
      if (x >= -11 && x <= -7 && Math.abs(z) <= 4) t = Math.max(t, 4);

      return Math.max(0, Math.round(t));
    }

    // Hull
    for (let x = -12; x <= 12; x++) {
      const hw = hullHalfWidth(x);

      for (let z = -hw; z <= hw; z++) {
        for (let y = 0; y <= 4; y++) {
          if (y > hullTop(x, z)) continue;

          let c;

          if (y === 0) {
            c = COL.darkWood;
          } else if (y === 1) {
            c = pick(["#563a23", "#634228"], x, z, y);
          } else if (y === 2) {
            c = pick(COL.woodPal, x, z, y);
          } else if (y === 3) {
            c = pick(["#7d5732", "#8a6236"], x, z, y);
          } else {
            c = pick(["#9b6e49", "#8f6342"], x, z, y);
          }

          addShip(x, y, z, c);
        }
      }
    }

    // Open deck
    for (let x = -11; x <= 11; x++) {
      const hw = hullHalfWidth(x);

      for (let z = -hw + 1; z <= hw - 1; z++) {
        if (x >= 7 && x <= 11 && Math.abs(z) <= 3) continue;
        if (x <= -7 && x >= -11 && Math.abs(z) <= 4) continue;
        if ((x === 8 || x === 0 || x === -9) && z === 0) continue;

        let c = pick(["#9b6e49", "#a87c55", "#8c6342"], x, 5, z);
        if (noise(x, z, 9) > 0.86) c = COL.woodDark;

        addShip(x, 5, z, c);
      }
    }

    // Forecastle
    for (let x = 8; x <= 11; x++) {
      const zlim = Math.min(3, hullHalfWidth(x));

      for (let z = -zlim; z <= zlim; z++) {
        for (let y = 5; y <= 7; y++) {
          if (y === 7 && (Math.abs(z) === zlim || x === 11)) continue;

          let c = COL.wood;
          if (noise(x, y, z) < 0.08) c = COL.glass;

          addShip(x, y, z, c);
        }
      }
    }

    // Aftcastle
    for (let x = -11; x <= -7; x++) {
      const zlim = Math.min(4, hullHalfWidth(x));

      for (let z = -zlim; z <= zlim; z++) {
        for (let y = 5; y <= 8; y++) {
          if (y === 8 && (Math.abs(z) === zlim || x === -11)) continue;

          let c = COL.wood;
          if (noise(x, y, z) > 0.9) c = COL.glass;

          addShip(x, y, z, c);
        }
      }
    }

    // Masts, yards, sails
    const masts = [
      {
        x: 8,
        top: 20,
        yards: [
          { y: 15, lower: 11, half: 5 },
          { y: 19, lower: 17, half: 3 }
        ]
      },
      {
        x: 0,
        top: 25,
        yards: [
          { y: 17, lower: 12, half: 6 },
          { y: 22, lower: 19, half: 4 },
          { y: 25, lower: 23, half: 3 }
        ]
      },
      {
        x: -9,
        top: 18,
        yards: [
          { y: 14, lower: 10, half: 4 },
          { y: 17, lower: 15, half: 2 }
        ]
      }
    ];

    function isMastBlocked(m, y) {
      for (const yard of m.yards) {
        if (y === yard.y) return true;
        if (y >= yard.lower && y < yard.y) return true;
      }
      return false;
    }

    for (const m of masts) {
      // Mast
      for (let y = 6; y <= m.top; y++) {
        if (!isMastBlocked(m, y)) {
          addShip(m.x, y, 0, COL.woodDark);
        }
      }

      // Sails and yards
      for (const yard of m.yards) {
        for (let y = yard.lower; y < yard.y; y++) {
          for (let z = -yard.half; z <= yard.half; z++) {
            const c = noise(m.x, y, z) > 0.25 ? COL.sail : COL.sailDark;
            addShip(m.x, y, z, c);
          }
        }

        for (let z = -yard.half; z <= yard.half; z++) {
          addShip(m.x, yard.y, z, COL.woodDark);
        }
      }
    }

    // Bowsprit
    for (let x = 13; x <= 20; x++) {
      const y = 3 + Math.floor((x - 13) / 2);
      addShip(x, y, 0, COL.woodDark);
    }

    // Small jibs
    for (let i = 0; i < 5; i++) {
      const x = 16 - i;
      const y = 5 + Math.floor(i * 1.2);
      addShip(x, y, 0, COL.sail);
    }

    // Flags
    addShip(0, 26, 0, COL.woodDark);
    for (let i = 1; i <= 5; i++) {
      addShip(i, 26, 0, i % 2 ? COL.red : COL.white);
    }

    addShip(-13, 12, 0, COL.woodDark);
    for (let y = 9; y <= 11; y++) {
      addShip(-14, y, 0, COL.red);
    }

    const shipGroup = new THREE.Group();
    shipGroup.add(makeMapGroup(shipMap));

    const shipBaseYaw = -0.36;
    shipGroup.position.set(-9, 0.05, 10);
    shipGroup.rotation.y = shipBaseYaw;
    scene.add(shipGroup);

    // ---------------- Clouds ----------------

    const cloudMap = new Map();

    function addCloudCluster(x, y, z) {
      const r = 3 + Math.floor(noise(x, z) * 4);

      for (let dx = -r; dx <= r; dx++) {
        for (let dz = -r; dz <= r; dz++) {
          if (dx * dx + dz * dz <= r * r) {
            if (noise(x + dx, y + dz, z) < 0.7) {
              addTo(
                cloudMap,
                x + dx,
                y,
                z + dz,
                pick(["#ffffff", "#f2f7fc", "#e8f0f8"], x, y, z)
              );
            }
          }
        }
      }
    }

    for (let i = 0; i < 18; i++) {
      const x = -100 + i * 12 + noise(i) * 8;
      const z = -55 + noise(i, 13) * 110;
      const y = 32 + noise(i, 5) * 8;
      addCloudCluster(x, y, z);
    }

    const cloudGroup = makeMapGroup(cloudMap);
    scene.add(cloudGroup);

    // ---------------- Birds ----------------

    const birdGeo = new THREE.BoxGeometry(1.2, 0.25, 0.35);
    const birdMat = new THREE.MeshLambertMaterial({ color: 0x20232b });
    const birds = [];

    for (let i = 0; i < 8; i++) {
      const mesh = new THREE.Mesh(birdGeo, birdMat);
      scene.add(mesh);

      birds.push({
        mesh,
        r: 18 + noise(i) * 22,
        a: noise(i, 2) * Math.PI * 2,
        s: 0.12 + noise(i, 3) * 0.18,
        y: 28 + noise(i, 4) * 7,
        phase: noise(i, 5) * Math.PI * 2
      });
    }

    // Add all remaining static voxels
    scene.add(makeMapGroup(staticMap));

    updateWater(0);

    const clock = new THREE.Clock();

    function animate() {
      requestAnimationFrame(animate);

      const t = clock.getElapsedTime();

      controls.update();
      updateWater(t);

      shipGroup.position.y = 0.05 + Math.sin(t * 1.1) * 0.05;
      shipGroup.rotation.z = Math.sin(t * 0.8) * 0.012;
      shipGroup.rotation.y = shipBaseYaw + Math.sin(t * 0.45) * 0.004;

      cloudGroup.rotation.y = t * 0.014;

      const pulse = 0.5 + 0.5 * Math.sin(t * 2.2);
      lampLight.intensity = 1.4 + pulse * 2.4;
      lampMesh.scale.setScalar(1 + pulse * 0.18);

      for (const b of birds) {
        b.a += b.s * 0.01;

        const bx = Math.cos(b.a) * b.r;
        const bz = Math.sin(b.a) * b.r - 8;

        b.mesh.position.set(
          bx,
          b.y + Math.sin(t * 2.0 + b.phase) * 0.8,
          bz
        );

        b.mesh.rotation.y = -b.a;
        b.mesh.rotation.z = Math.sin(t * 8.0 + b.phase) * 0.35;
      }

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