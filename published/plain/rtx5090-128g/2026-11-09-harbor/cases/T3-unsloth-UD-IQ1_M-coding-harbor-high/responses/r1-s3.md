Save this as `harbor-voxels.html` and open it in Chrome.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>A Sailing Ship Calling at a Harbor — Voxel Scene</title>
  <style>
    html, body {
      margin: 0;
      height: 100%;
      overflow: hidden;
      background: #9dd4ff;
      font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
    }

    canvas {
      display: block;
      width: 100%;
      height: 100%;
      outline: none;
    }

    #info {
      position: fixed;
      left: 14px;
      top: 14px;
      padding: 8px 12px;
      border-radius: 10px;
      color: #1c2835;
      background: rgba(255, 255, 255, 0.72);
      backdrop-filter: blur(6px);
      font-size: 13px;
      line-height: 1.35;
      pointer-events: none;
      user-select: none;
      opacity: 1;
      transition: opacity 1.2s ease;
    }

    #info b {
      font-weight: 600;
    }
  </style>
</head>
<body>
  <div id="info">
    <b>A Sailing Ship Calling at a Harbor</b><br />
    Drag to orbit • Scroll / pinch to zoom
  </div>

  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js"></script>
  <script>
    if (typeof THREE === "undefined") {
      document.body.innerHTML = "<h2>Could not load Three.js from CDN. Check internet connection.</h2>";
    } else {
      /* -----------------------------------------------------------
         Renderer, scene, camera, lights
      ----------------------------------------------------------- */
      const renderer = new THREE.WebGLRenderer({ antialias: true });
      renderer.setSize(window.innerWidth, window.innerHeight);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
      renderer.shadowMap.enabled = true;
      renderer.shadowMap.type = THREE.PCFSoftShadowMap;
      if (THREE.sRGBEncoding !== undefined) renderer.outputEncoding = THREE.sRGBEncoding;
      document.body.appendChild(renderer.domElement);
      renderer.domElement.style.touchAction = "none";

      const scene = new THREE.Scene();
      const skyColor = new THREE.Color(0x9dd4ff);
      scene.background = skyColor;
      scene.fog = new THREE.Fog(skyColor, 70, 180);

      const camera = new THREE.PerspectiveCamera(
        55,
        window.innerWidth / window.innerHeight,
        0.1,
        500
      );

      const hemi = new THREE.HemisphereLight(0xd7ecff, 0x302923, 0.62);
      scene.add(hemi);

      const sun = new THREE.DirectionalLight(0xffe6b8, 1.05);
      sun.position.set(36, 48, 24);
      sun.castShadow = true;
      sun.shadow.mapSize.set(1024, 1024);
      sun.shadow.camera.left = -58;
      sun.shadow.camera.right = 58;
      sun.shadow.camera.top = 58;
      sun.shadow.camera.bottom = -58;
      sun.shadow.camera.near = 1;
      sun.shadow.camera.far = 190;
      sun.shadow.bias = -0.0008;
      if ("normalBias" in sun.shadow) sun.shadow.normalBias = 0.02;
      sun.target.position.set(0, 0, 5);
      scene.add(sun);
      scene.add(sun.target);

      const fillLight = new THREE.DirectionalLight(0x89b8ff, 0.22);
      fillLight.position.set(-25, 18, -30);
      scene.add(fillLight);

      /* -----------------------------------------------------------
         Voxel builder: turns many boxes into instanced meshes
      ----------------------------------------------------------- */
      class VoxelBuilder {
        constructor() {
          this.items = [];
        }

        add(x, y, z, color, dynamic = false, phase = 0) {
          if (Array.isArray(color)) {
            const h =
              ((x * 374761393) ^ (y * 668265263) ^ (z * 2654435761)) >>> 0;
            color = color[h % color.length];
          }
          this.items.push({ x, y, z, color, dynamic, phase });
        }

        box(x0, x1, y0, y1, z0, z1, color, dynamic = false) {
          for (let x = x0; x <= x1; x++) {
            for (let y = y0; y <= y1; y++) {
              for (let z = z0; z <= z1; z++) {
                this.add(x, y, z, color, dynamic);
              }
            }
          }
        }

        build(scene, material, castShadow = false, receiveShadow = false, dynamic = false) {
          if (this.items.length === 0) return null;

          const geometry = new THREE.BoxGeometry(1, 1, 1);
          const mesh = new THREE.InstancedMesh(geometry, material, this.items.length);
          const dummy = new THREE.Object3D();
          const tmpColor = new THREE.Color();
          const dyn = [];

          for (let i = 0; i < this.items.length; i++) {
            const it = this.items[i];

            dummy.position.set(it.x + 0.5, it.y + 0.5, it.z + 0.5);
            dummy.rotation.set(0, 0, 0);
            dummy.scale.set(1, 1, 1);
            dummy.updateMatrix();

            mesh.setMatrixAt(i, dummy.matrix);

            tmpColor.set(it.color);
            if (mesh.setColorAt) mesh.setColorAt(i, tmpColor);

            if (dynamic && it.dynamic) {
              dyn.push({
                i,
                bx: it.x + 0.5,
                by: it.y + 0.5,
                bz: it.z + 0.5,
                phase: it.phase || 0
              });
            }
          }

          mesh.instanceMatrix.needsUpdate = true;
          if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;

          mesh.castShadow = !!castShadow;
          mesh.receiveShadow = !!receiveShadow;
          mesh.frustumCulled = false;

          scene.add(mesh);
          return { mesh, dyn };
        }
      }

      const mainB = new VoxelBuilder();
      const waterB = new VoxelBuilder();
      const cloudB = new VoxelBuilder();
      const waterExclude = new Set();

      const PAL = {
        waterTop: [0x1d7db2, 0x2591bd, 0x31a5cb, 0x1b78ab],
        waterDeep: [0x09577c, 0x0a5173, 0x126c8b],

        stone: [0x8a857c, 0x7d7771, 0x948e85],
        stoneDark: [0x5f5a55, 0x6a6560],
        grass: [0x4f7848, 0x56824f, 0x5f8f5a],
        dirt: [0x8c6a4a, 0x977250],

        quayWood: [0xb3814b, 0xa67542, 0xc29160],
        hullDark: [0x3e271a, 0x4b3122],
        hull: [0x8d5a35, 0x7a4e2d, 0x99673d, 0x845530],
        waterline: [0xd2b47a, 0xc9aa72],
        deck: [0xb78a55, 0xaa7e4c, 0xc79a66],
        deckDark: [0x916338, 0x835730],

        cream: [0xe8dfc9, 0xf0e7d4, 0xded4bd],
        brick: [0x9c4a38, 0xb05643, 0x8a4132],

        woodDark: [0x533526, 0x603e2c],
        rope: [0x6b5239, 0x7a5f43],
        crate: [0xa57341, 0x926438, 0xb18152],
        barrel: [0x7a4e2f, 0x8b5f3a, 0x693e27],

        sail: [0xf6f1e6, 0xe9e3d4, 0xf1ead9],
        cloud: [0xf7fbff, 0xeaf3ff, 0xddeff8],

        white: [0xf3f2ed, 0xffffff],
        red: [0xb23838, 0xc44545, 0x9c2f2f],
        teal: [0x3f6f73, 0x4b7d82, 0x375c61],
        brownRoof: [0x5c4033, 0x6a493a],
        lamp: [0xffdf99, 0xffc968]
      };

      const mainMat = new THREE.MeshStandardMaterial({
        color: 0xffffff,
        roughness: 0.78,
        metalness: 0.02,
        flatShading: true
      });

      const waterMat = new THREE.MeshStandardMaterial({
        color: 0xffffff,
        roughness: 0.38,
        metalness: 0.05,
        flatShading: true
      });

      const cloudMat = new THREE.MeshStandardMaterial({
        color: 0xffffff,
        roughness: 0.9,
        metalness: 0.0,
        transparent: true,
        opacity: 0.72,
        depthWrite: true,
        flatShading: true
      });

      /* -----------------------------------------------------------
         The ship
      ----------------------------------------------------------- */
      const SHIP_X = 0;
      const SHIP_Z = -1;

      function addHullVoxel(x, y, z, color) {
        const ax = SHIP_X + x;
        const az = SHIP_Z + z;
        mainB.add(ax, y, az, color);
        if (y === 0) waterExclude.add(ax + "," + az);
      }

      function shipHalf(x) {
        if (x < -11) return 0;
        if (x < -9) return x + 12;       // -11 -> 1, -10 -> 2
        if (x < -7) return 3;            // -9, -8 -> 3
        if (x < 7) return 5;             // -7..6 -> 5
        if (x < 11) return 11 - x;       // 7..10 taper
        return 0;
      }

      function buildShip() {
        // Hull: solid below/near waterline, then blocky side planking.
        for (let x = -11; x <= 10; x++) {
          const hw = shipHalf(x);
          if (hw <= 0) continue;

          for (let y = -2; y <= -1; y++) {
            for (let z = -hw; z <= hw; z++) {
              addHullVoxel(x, y, z, PAL.hullDark);
            }
          }

          for (let y = 0; y <= 2; y++) {
            for (let z = -hw; z <= hw; z++) {
              let c = PAL.hull;
              if (y === 0) c = PAL.waterline;
              if (y === 2) c = PAL.deckDark;
              addHullVoxel(x, y, z, c);
            }
          }
        }

        // Main deck and gunwale.
        for (let x = -10; x <= 9; x++) {
          const hw = shipHalf(x);
          if (hw <= 0) continue;

          if (hw > 1) {
            for (let z = -hw + 1; z <= hw - 1; z++) {
              mainB.add(SHIP_X + x, 3, SHIP_Z + z, PAL.deck);
            }
          }

          mainB.add(SHIP_X + x, 3, SHIP_Z + hw, PAL.deck);
          mainB.add(SHIP_X + x, 3, SHIP_Z - hw, PAL.deck);
        }

        // Sparse railing posts.
        for (let x = -9; x <= 9; x += 2) {
          const hw = shipHalf(x);
          if (hw <= 0) continue;
          mainB.add(SHIP_X + x, 4, SHIP_Z + hw, PAL.woodDark);
          mainB.add(SHIP_X + x, 4, SHIP_Z - hw, PAL.woodDark);
        }

        // Stern quarterdeck / cabin.
        mainB.box(SHIP_X - 10, SHIP_X - 7, 4, 5, SHIP_Z - 3, SHIP_Z + 3, PAL.cream);
        mainB.box(SHIP_X - 9, SHIP_X - 8, 6, 6, SHIP_Z - 2, SHIP_Z + 2, PAL.brownRoof);

        // Portholes / side windows.
        mainB.add(SHIP_X - 9, 4, SHIP_Z - 4, 0x15283a);
        mainB.add(SHIP_X - 8, 4, SHIP_Z - 4, 0x15283a);
        mainB.add(SHIP_X - 8, 4, SHIP_Z + 4, 0x15283a);
        mainB.add(SHIP_X - 9, 4, SHIP_Z + 4, 0x15283a);

        // Forecastle.
        mainB.box(SHIP_X + 7, SHIP_X + 9, 4, 5, SHIP_Z - 2, SHIP_Z + 2, PAL.cream);
        mainB.box(SHIP_X + 8, SHIP_X + 8, 6, 6, SHIP_Z - 1, SHIP_Z + 1, PAL.brownRoof);

        // Deck cargo.
        function addCrate(x, y, z) {
          mainB.box(x, x + 1, y, y + 1, z, z + 1, PAL.crate);
        }

        addCrate(SHIP_X - 4, 4, SHIP_Z + 2);
        addCrate(SHIP_X + 3, 4, SHIP_Z + 2);
        addCrate(SHIP_X + 3, 4, SHIP_Z + 3);

        // Bowsprit.
        for (let i = 0; i <= 8; i++) {
          const y = 5 + Math.round((i * 3) / 8);
          mainB.add(SHIP_X + 11 + i, y, SHIP_Z, PAL.woodDark);
        }

        // Jib.
        for (let i = 0; i <= 9; i++) {
          const x = 18 - i;
          const y = 8 + Math.round((i * 4) / 9);
          for (let z = -1; z <= 1; z++) {
            mainB.add(SHIP_X + x, y, SHIP_Z + z, PAL.sail);
          }
        }

        function addMast(mastX, topY) {
          for (let y = 4; y <= topY; y++) {
            mainB.add(SHIP_X + mastX, y, SHIP_Z, PAL.woodDark);
          }
        }

        function addYard(mastX, y, zHalf) {
          for (let z = -zHalf; z <= zHalf; z++) {
            if (z === 0) continue;
            mainB.add(SHIP_X + mastX, y, SHIP_Z + z, PAL.woodDark);
          }
        }

        function addSail(mastX, y0, y1, zHalf, side = 1) {
          for (let dx = side; dx <= side + 1; dx++) {
            for (let y = y0; y <= y1; y++) {
              for (let z = -zHalf; z <= zHalf; z++) {
                mainB.add(SHIP_X + mastX + dx, y, SHIP_Z + z, PAL.sail);
              }
            }
          }
        }

        // Foremast.
        addMast(5, 18);
        addYard(5, 11, 4);
        addSail(5, 8, 10, 4, 1);
        addYard(5, 15, 3);
        addSail(5, 12, 14, 3, 1);
        addYard(5, 18, 2);
        addSail(5, 16, 17, 2, 1);

        // Mainmast.
        addMast(-1, 18);
        addYard(-1, 11, 5);
        addSail(-1, 6, 10, 5, 1);
        addYard(-1, 15, 4);
        addSail(-1, 12, 14, 4, 1);
        addYard(-1, 18, 3);
        addSail(-1, 16, 17, 3, 1);

        // Mizzenmast.
        addMast(-5, 13);
        addYard(-5, 10, 3);
        addSail(-5, 7, 9, 3, -1);
        addYard(-5, 13, 2);
        addSail(-5, 11, 12, 2, -1);

        // Flag.
        mainB.add(SHIP_X - 1, 19, SHIP_Z + 1, 0xc94040);
        mainB.add(SHIP_X - 1, 20, SHIP_Z + 1, 0xf05050);
        mainB.add(SHIP_X - 1, 20, SHIP_Z + 2, 0xc94040);
      }

      buildShip();

      /* -----------------------------------------------------------
         Harbor: quay, piers, land, buildings, props
      ----------------------------------------------------------- */
      const beaconPos = new THREE.Vector3();

      function addHouse(x1, x2, z1, z2, h, wall, roof) {
        mainB.box(x1, x2, 2, 2 + h - 1, z1, z2, wall);

        const roofStart = 2 + h;
        const roofLayers = Math.max(1, Math.floor(h / 2));

        for (let i = 0; i <= roofLayers; i++) {
          const rx0 = x1 + i;
          const rx1 = x2 - i;
          const rz0 = z1 + i;
          const rz1 = z2 - i;
          if (rx0 <= rx1 && rz0 <= rz1) {
            mainB.box(rx0, rx1, roofStart + i, roofStart + i, rz0, rz1, roof);
          }
        }

        const cx = Math.floor((x1 + x2) / 2);
        mainB.box(cx, cx + 1, 2, 3, z1 - 1, z1 - 1, 0x2d2420);

        for (let x = x1 + 1; x <= x2 - 1; x += 2) {
          if (x >= cx && x <= cx + 1) continue;
          mainB.add(x, 3, z1 - 1, 0x1d2b36);
          if (h >= 4) mainB.add(x, 4, z1 - 1, 0x1d2b36);
        }
      }

      function addBarrel(x, z) {
        mainB.add(x, 2, z, PAL.barrel);
        mainB.add(x, 3, z, PAL.barrel);
        mainB.add(x, 4, z, PAL.barrel);
      }

      function addLamp(x, z) {
        mainB.box(x, x, 2, 4, z, z, PAL.woodDark);
        mainB.add(x, 5, z, PAL.lamp);
        mainB.add(x, 5, z + 1, 0xffd79a);
      }

      function addLighthouse(cx, cz) {
        mainB.box(cx - 2, cx + 2, 2, 2, cz - 2, cz + 2, PAL.stoneDark);

        for (let level = 0; level < 10; level++) {
          const y = 3 + level;
          let s;
          if (level < 6) s = 2;
          else if (level < 8) s = 1;
          else s = 0;

          const color = Math.floor(level / 2) % 2 === 0 ? PAL.white : PAL.red;

          if (s > 0) {
            mainB.box(cx - s, cx + s, y, y, cz - s, cz + s, color);
          } else {
            mainB.add(cx, y, cz, color);
          }
        }

        mainB.box(cx - 2, cx + 2, 13, 13, cz - 2, cz + 2, 0x4b4b4b);
        mainB.box(cx - 1, cx + 1, 14, 15, cz - 1, cz + 1, 0x15303a);

        beaconPos.set(cx + 0.5, 16.5, cz + 0.5);
      }

      function buildHarbor() {
        // Quay: stone substructure and wooden deck surface.
        mainB.box(-18, 17, 0, 0, 5, 17, PAL.stoneDark);
        mainB.box(-18, 17, 1, 1, 5, 17, PAL.quayWood);

        // Two side piers extending into the basin.
        mainB.box(-18, -14, 0, 0, -8, 17, PAL.stoneDark);
        mainB.box(-18, -14, 1, 1, -8, 17, PAL.quayWood);

        mainB.box(14, 18, 0, 0, -8, 17, PAL.stoneDark);
        mainB.box(14, 18, 1, 1, -8, 17, PAL.quayWood);

        // Harbor land.
        mainB.box(-32, 32, 0, 0, 18, 32, PAL.stoneDark);
        mainB.box(-32, 32, 1, 1, 18, 32, PAL.grass);

        // Quay bollards.
        [
          [-16, 5],
          [-8, 5],
          [0, 5],
          [8, 5],
          [16, 5]
        ].forEach(([x, z]) => mainB.add(x, 2, z, PAL.rope));

        // Pier bollards.
        mainB.add(-16, 2, -4, PAL.rope);
        mainB.add(16, 2, -4, PAL.rope);

        // Cargo on quay.
        mainB.box(-12, -10, 2, 3, 12, 13, PAL.crate);
        mainB.box(-10, -9, 2, 3, 12, 13, PAL.crate);
        mainB.box(-11, -10, 4, 5, 12, 13, PAL.crate);

        mainB.box(10, 11, 2, 3, 12, 13, PAL.crate);
        mainB.box(10, 11, 4, 5, 12, 13, PAL.crate);

        mainB.box(-6, -4, 2, 3, 14, 15, PAL.crate);

        // Barrels.
        addBarrel(-14, 10);
        addBarrel(13, 10);
        addBarrel(-3, 14);

        // Quay lamps.
        addLamp(-14, 12);
        addLamp(0, 14);
        addLamp(14, 12);

        // Warehouses and houses.
        addHouse(-28, -20, 22, 28, 4, PAL.brick, PAL.red);
        addHouse(-16, -8, 24, 30, 3, PAL.cream, PAL.teal);
        addHouse(-2, 6, 22, 28, 3, PAL.cream, PAL.brownRoof);
        addHouse(10, 18, 26, 32, 4, PAL.brick, PAL.teal);

        // Lighthouse.
        addLighthouse(28, 20);
      }

      buildHarbor();

      /* -----------------------------------------------------------
         Water and clouds
      ----------------------------------------------------------- */
      function isQuayPier(x, z) {
        if (z >= 5) return true;

        if (x >= -18 && x <= -14 && z >= -8) return true;
        if (x >= 14 && x <= 18 && z >= -8) return true;

        return false;
      }

      function wavePhase(x, z) {
        const s = Math.sin(x * 12.9898 + z * 78.233) * 43758.5453;
        return (s - Math.floor(s)) * Math.PI * 2;
      }

      function buildWater() {
        for (let x = -32; x <= 31; x++) {
          for (let z = -32; z <= 4; z++) {
            if (!isQuayPier(x, z) && !waterExclude.has(x + "," + z)) {
              waterB.add(x, -1, z, PAL.waterDeep);
            }

            if (!isQuayPier(x, z) && !waterExclude.has(x + "," + z)) {
              waterB.add(x, 0, z, PAL.waterTop, true, wavePhase(x, z));
            }
          }
        }
      }

      function addCloud(cx, cz) {
        cloudB.box(cx, cx + 7, 34, 35, cz, cz + 5, PAL.cloud);
        cloudB.box(cx + 2, cx + 9, 35, 36, cz + 1, cz + 4, PAL.cloud);
        cloudB.box(cx - 1, cx + 6, 33, 33, cz + 2, cz + 5, PAL.cloud);
      }

      buildWater();

      function buildClouds() {
        addCloud(-25, -22);
        addCloud(8, -34);
        addCloud(28, -10);
        addCloud(-18, 26);
        addCloud(16, 34);
        addCloud(-4, -4);
      }

      buildClouds();

      /* -----------------------------------------------------------
         Build instanced meshes
      ----------------------------------------------------------- */
      const mainRes = mainB.build(scene, mainMat, true, true, false);
      const waterRes = waterB.build(scene, waterMat, false, false, true);
      const cloudRes = cloudB.build(scene, cloudMat, false, false, false);

      /* -----------------------------------------------------------
         Beacon, ropes, rigging
      ----------------------------------------------------------- */
      const beaconGeo = new THREE.BoxGeometry(0.9, 0.9, 0.9);
      const beaconMat = new THREE.MeshBasicMaterial({ color: 0xffd37a });
      const beacon = new THREE.Mesh(beaconGeo, beaconMat);
      beacon.position.copy(beaconPos);
      scene.add(beacon);

      const beaconLight = new THREE.PointLight(0xffd37a, 0, 36, 2);
      beaconLight.position.copy(beacon.position);
      scene.add(beaconLight);

      const ropeMat = new THREE.MeshStandardMaterial({
        color: 0x4a3020,
        roughness: 0.95,
        metalness: 0.0
      });

      function addRope(ax, ay, az, bx, by, bz) {
        const a = new THREE.Vector3(ax, ay, az);
        const b = new THREE.Vector3(bx, by, bz);
        const dir = b.clone().sub(a);
        const len = dir.length();
        if (len < 0.1) return;

        const mesh = new THREE.Mesh(
          new THREE.CylinderGeometry(0.11, 0.11, len, 6),
          ropeMat
        );
        mesh.position.copy(a).add(b).multiplyScalar(0.5);
        mesh.quaternion.setFromUnitVectors(
          new THREE.Vector3(0, 1, 0),
          dir.clone().normalize()
        );
        mesh.castShadow = false;
        scene.add(mesh);
      }

      // Mooring lines.
      addRope(SHIP_X + 11, 4, SHIP_Z, 16, 3, 2);
      addRope(SHIP_X - 10, 4, SHIP_Z, -16, 3, 2);
      addRope(SHIP_X, 4, SHIP_Z, 0, 3, 5);

      // Simple rigging.
      const rigMat = new THREE.LineBasicMaterial({
        color: 0x3a291e,
        transparent: true,
        opacity: 0.72
      });

      const rigPts = [];
      function addRig(a, b) {
        rigPts.push(a, b);
      }

      const mastTops = [
        [-1, 18],
        [5, 18],
        [-5, 13]
      ];

      mastTops.forEach(([mx, ty]) => {
        const top = new THREE.Vector3(SHIP_X + mx, ty + 0.5, SHIP_Z);
        const bow = new THREE.Vector3(SHIP_X + 11, 4, SHIP_Z);
        const stern = new THREE.Vector3(SHIP_X - 10, 4, SHIP_Z);
        const left = new THREE.Vector3(SHIP_X + mx, 4, SHIP_Z - 5);
        const right = new THREE.Vector3(SHIP_X + mx, 4, SHIP_Z + 5);

        addRig(top, bow);
        addRig(top, stern);
        addRig(top, left);
        addRig(top, right);
      });

      const rigGeo = new THREE.BufferGeometry().setFromPoints(rigPts);
      scene.add(new THREE.LineSegments(rigGeo, rigMat));

      /* -----------------------------------------------------------
         Custom orbit controls (mouse / touch)
      ----------------------------------------------------------- */
      function clamp(v, min, max) {
        return Math.max(min, Math.min(max, v));
      }

      const target = new THREE.Vector3(0, 7, 7);
      const desired = new THREE.Spherical(74, 1.02, 0.72);
      const current = new THREE.Spherical(74, 1.02, 0.72);
      const camOffset = new THREE.Vector3();

      function updateCamera() {
        camOffset.setFromSpherical(current);
        camera.position.copy(target).add(camOffset);
        camera.lookAt(target);
      }

      const pointers = new Map();
      let prevX = 0;
      let prevY = 0;
      let prevPinchDist = 0;
      const dom = renderer.domElement;

      dom.addEventListener("contextmenu", e => e.preventDefault());

      dom.addEventListener("pointerdown", e => {
        dom.setPointerCapture(e.pointerId);
        pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });

        if (pointers.size === 1) {
          prevX = e.clientX;
          prevY = e.clientY;
        } else if (pointers.size === 2) {
          const arr = Array.from(pointers.values());
          prevPinchDist = Math.hypot(arr[0].x - arr[1].x, arr[0].y - arr[1].y);
        }
      });

      dom.addEventListener("pointermove", e => {
        if (!pointers.has(e.pointerId)) return;

        const p = pointers.get(e.pointerId);
        const nx = e.clientX;
        const ny = e.clientY;

        if (pointers.size === 1) {
          const dx = nx - prevX;
          const dy = ny - prevY;

          desired.theta -= dx * 0.0085;
          desired.phi = clamp(desired.phi - dy * 0.0085, 0.15, Math.PI / 2 - 0.04);

          prevX = nx;
          prevY = ny;
        } else if (pointers.size === 2) {
          p.x = nx;
          p.y = ny;

          const arr = Array.from(pointers.values());
          const d = Math.hypot(arr[0].x - arr[1].x, arr[0].y - arr[1].y);

          if (prevPinchDist > 0 && d > 0) {
            desired.radius = clamp(desired.radius * (prevPinchDist / d), 24, 175);
          }

          prevPinchDist = d;
        }

        p.x = nx;
        p.y = ny;
      });

      function endPointer(e) {
        pointers.delete(e.pointerId);

        if (pointers.size === 1) {
          const arr = Array.from(pointers.values());
          prevX = arr[0].x;
          prevY = arr[0].y;
        }

        if (pointers.size === 0) {
          prevPinchDist = 0;
        }
      }

      dom.addEventListener("pointerup", endPointer);
      dom.addEventListener("pointercancel", endPointer);

      dom.addEventListener(
        "wheel",
        e => {
          e.preventDefault();
          const factor = 1 + clamp(e.deltaY, -220, 220) * 0.001;
          desired.radius = clamp(desired.radius * factor, 24, 175);
        },
        { passive: false }
      );

      /* -----------------------------------------------------------
         Animation
      ----------------------------------------------------------- */
      const waterDummy = new THREE.Object3D();
      let shadowFrames = 0;

      function updateWater(time) {
        if (!waterRes) return;

        const t = time * 0.001;

        for (let i = 0; i < waterRes.dyn.length; i++) {
          const d = waterRes.dyn[i];

          const dy =
            Math.sin(t * 1.65 + d.phase) * 0.035 +
            Math.sin(t * 0.85 + d.phase * 1.7) * 0.018;

          const dz = Math.cos(t * 1.25 + d.phase) * 0.012;

          waterDummy.position.set(d.bx, d.by + dy, d.bz + dz);
          waterDummy.rotation.set(0, 0, 0);
          waterDummy.scale.set(1, 1, 1);
          waterDummy.updateMatrix();

          waterRes.mesh.setMatrixAt(d.i, waterDummy.matrix);
        }

        waterRes.mesh.instanceMatrix.needsUpdate = true;
      }

      function updateBeacon(time) {
        const pulse = 0.5 + 0.5 * Math.sin(time * 0.004);
        beaconLight.intensity = 0.75 + pulse * 2.8;
        beacon.scale.setScalar(0.62 + pulse * 0.55);
      }

      function animate(time) {
        if (time === undefined) time = 0;

        updateWater(time);
        updateBeacon(time);

        current.radius += (desired.radius - current.radius) * 0.10;
        current.phi += (desired.phi - current.phi) * 0.10;
        current.theta += (desired.theta - current.theta) * 0.10;
        updateCamera();

        renderer.render(scene, camera);

        // Shadows are static after a few frames; water/props are not casting.
        if (shadowFrames < 5) {
          shadowFrames++;
        } else if (renderer.shadowMap.autoUpdate) {
          renderer.shadowMap.autoUpdate = false;
        }

        requestAnimationFrame(animate);
      }

      function onResize() {
        renderer.setSize(window.innerWidth, window.innerHeight);
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
      }

      window.addEventListener("resize", onResize);
      requestAnimationFrame(animate);

      // Fade the hint after a few seconds.
      setTimeout(() => {
        const info = document.getElementById("info");
        if (info) info.style.opacity = "0";
      }, 6500);
    }
  </script>
</body>
</html>
```