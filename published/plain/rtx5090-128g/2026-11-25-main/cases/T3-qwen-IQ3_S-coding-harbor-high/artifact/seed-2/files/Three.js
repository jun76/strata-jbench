<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Voxel Harbor: Sailing Ship Calling at a Harbor</title>
  <style>
    html, body {
      margin: 0;
      height: 100%;
      overflow: hidden;
      background: #6db3d8;
    }
    #info {
      position: absolute;
      top: 12px;
      left: 12px;
      color: #fff;
      font: 14px/1.4 monospace;
      background: rgba(0, 0, 0, 0.38);
      padding: 8px 10px;
      border-radius: 8px;
      pointer-events: none;
      z-index: 10;
    }
  </style>
</head>
<body>
  <div id="info">
    Voxel harbor: drag to orbit, scroll to zoom, right-drag to pan.<br />
    Scene: A sailing ship calling at a harbor.
  </div>

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

    let scene, camera, renderer, controls;
    let waterTex;
    let ship, flagGroup;
    let builder;
    const seagulls = [];
    const clouds = [];

    const sharedBox = new THREE.BoxGeometry(1, 1, 1);
    const lambertCache = new Map();

    let seed = 20260101;
    function rand() {
      seed = (seed * 1664525 + 1013904223) & 0xffffffff;
      return seed / 4294967295;
    }

    function pick(arr) {
      return arr[Math.floor(rand() * arr.length)];
    }

    function lam(color) {
      let m = lambertCache.get(color);
      if (!m) {
        m = new THREE.MeshLambertMaterial({ color });
        lambertCache.set(color, m);
      }
      return m;
    }

    class StaticVoxelBuilder {
      constructor() {
        this.items = [];
      }

      add(x, y, z, color) {
        this.items.push([x, y, z, color]);
      }

      build(parent) {
        const byColor = new Map();

        for (const item of this.items) {
          const color = item[3];
          if (!byColor.has(color)) byColor.set(color, []);
          byColor.get(color).push(item);
        }

        const group = new THREE.Group();
        const matrix = new THREE.Matrix4();

        for (const [color, list] of byColor) {
          const mesh = new THREE.InstancedMesh(sharedBox, lam(color), list.length);
          mesh.castShadow = true;
          mesh.receiveShadow = true;

          list.forEach((p, i) => {
            matrix.makeTranslation(p[0], p[1], p[2]);
            mesh.setMatrixAt(i, matrix);
          });

          mesh.instanceMatrix.needsUpdate = true;
          group.add(mesh);
        }

        parent.add(group);
        this.items.length = 0;
        return group;
      }
    }

    function addGlow(x, y, z, color, size = 1) {
      const mesh = new THREE.Mesh(
        sharedBox,
        new THREE.MeshBasicMaterial({ color })
      );
      mesh.position.set(x, y, z);
      mesh.scale.setScalar(size);
      scene.add(mesh);
      return mesh;
    }

    function makeWaterTexture() {
      const size = 128;
      const c = document.createElement("canvas");
      c.width = size;
      c.height = size;
      const ctx = c.getContext("2d");
      ctx.imageSmoothingEnabled = false;

      ctx.fillStyle = "#216b94";
      ctx.fillRect(0, 0, size, size);

      const cols = [
        "#1d5d87",
        "#256d98",
        "#2e7faa",
        "#3aa0c5"
      ];

      for (let y = 0; y < size; y += 4) {
        for (let x = 0; x < size; x += 4) {
          const v =
            Math.sin(x * 0.11 + y * 0.07) +
            Math.cos(y * 0.17) +
            rand() * 0.4;

          const idx = Math.max(0, Math.min(3, Math.floor((v + 2) / 1.6)));
          ctx.fillStyle = cols[idx];
          ctx.fillRect(x, y, 4, 4);
        }
      }

      for (let i = 0; i < 180; i++) {
        ctx.fillStyle = i % 3 ? "#9fdcff" : "#d8f3ff";
        ctx.fillRect(
          (rand() * size | 0) * 4,
          (rand() * size | 0) * 4,
          2,
          6
        );
      }

      const tex = new THREE.CanvasTexture(c);
      tex.wrapS = THREE.RepeatWrapping;
      tex.wrapT = THREE.RepeatWrapping;
      tex.magFilter = THREE.NearestFilter;
      tex.minFilter = THREE.NearestMipmapLinearFilter;
      tex.repeat.set(8, 8);
      tex.colorSpace = THREE.SRGBColorSpace;
      return tex;
    }

    function addBuilding(bx, bz, w, d, h, wallColor, roofColor) {
      for (let ix = 0; ix < w; ix++) {
        for (let iz = 0; iz < d; iz++) {
          const x = bx + ix;
          const z = bz + iz;

          for (let yy = 0; yy < h; yy++) {
            const y = 1.5 + yy;
            const isWall =
              ix === 0 || ix === w - 1 || iz === 0 || iz === d - 1;

            let color;

            if (isWall) {
              color = wallColor;

              // Windows / door on quay-facing front face.
              if (iz === 0) {
                if (yy === 0 && ix === Math.floor(w / 2)) {
                  color = 0x4d3119; // door
                } else if (
                  yy > 0 &&
                  yy % 2 === 1 &&
                  ix > 0 &&
                  ix < w - 1 &&
                  ix % 3 === 1
                ) {
                  color = 0xf3e9c9; // window
                }
              } else {
                if (yy > 0 && (x + yy) % 3 === 0) {
                  color = 0xf3e9c9; // side window
                }
              }
            } else {
              color = 0x554636; // interior block
            }

            builder.add(x, y, z, color);
          }
        }
      }

      // Stepped voxel roof.
      const maxRoofLayers = Math.min(3, Math.min(w, d) - 1);

      for (let r = 0; r < maxRoofLayers; r++) {
        const x0 = bx - 1 + r;
        const x1 = bx + w - r;
        const z0 = bz - 1 + r;
        const z1 = bz + d - r;
        const y = 1.5 + h + r;

        if (x0 > x1 || z0 > z1) break;

        for (let x = x0; x <= x1; x++) {
          for (let z = z0; z <= z1; z++) {
            builder.add(x, y, z, roofColor);
          }
        }
      }
    }

    function addLighthouse(cx, cz, h = 8) {
      for (let yy = 0; yy < h; yy++) {
        const y = 1.5 + yy;
        const color = yy % 2 === 0 ? 0xf2f2f2 : 0xcf4c48;

        for (let dx = -1; dx <= 1; dx++) {
          for (let dz = -1; dz <= 1; dz++) {
            builder.add(cx + dx, y, cz + dz, color);
          }
        }
      }

      const galleryY = 1.5 + h;

      for (let dx = -2; dx <= 2; dx++) {
        for (let dz = -2; dz <= 2; dz++) {
          builder.add(cx + dx, galleryY, cz + dz, 0x3a3d40);
        }
      }

      addGlow(cx, galleryY + 1, cz, 0xfff2b0, 1.3);

      for (let dx = -1; dx <= 1; dx++) {
        for (let dz = -1; dz <= 1; dz++) {
          builder.add(cx + dx, galleryY + 2, cz + dz, 0x7c2f2f);
        }
      }

      builder.add(cx, galleryY + 3, cz, 0x5a2222);
    }

    function addBreakwater() {
      const stone = [0x8a8171, 0x9a9180, 0x756c5d, 0xa79f8c];

      for (let z = -35; z <= 15; z++) {
        for (let x = 45; x <= 47; x++) {
          builder.add(x, 0.5, z, pick(stone));
        }

        for (const y of [-0.5, -1.5]) {
          builder.add(44, y, z, pick(stone));
          builder.add(48, y, z, pick(stone));
        }
      }
    }

    function addPier(x0, x1, z0, z1) {
      const wood = [0x7d5b3a, 0x8b6945, 0x694a2d, 0x9a7a50];

      for (let x = x0; x <= x1; x++) {
        for (let z = z0; z <= z1; z++) {
          builder.add(x, 0.5, z, pick(wood));
        }
      }

      for (let x = x0; x <= x1; x += 4) {
        for (let z = z0; z <= z1; z += 4) {
          for (const y of [-0.5, -1.5]) {
            builder.add(x, y, z, 0x4d3722);
          }
        }
      }

      for (let z = z0; z <= z1; z++) {
        builder.add(x0, 1.5, z, 0x7b5b3d);
        builder.add(x1, 1.5, z, 0x7b5b3d);
      }

      for (let x = x0; x <= x1; x++) {
        builder.add(x, 1.5, z0, 0x7b5b3d);
        builder.add(x, 1.5, z1, 0x7b5b3d);
      }
    }

    function addStall(x, z, awningColor) {
      for (const dx of [0, 3]) {
        for (const dz of [0, 3]) {
          for (const y of [1.5, 2.5, 3.5]) {
            builder.add(x + dx, y, z + dz, 0x5a4329);
          }
        }
      }

      for (let dx = 1; dx <= 2; dx++) {
        builder.add(x + dx, 1.5, z, 0x8c6b42);
      }

      for (let ax = x - 1; ax <= x + 4; ax++) {
        for (let az = z - 1; az <= z + 4; az++) {
          builder.add(ax, 4.5, az, awningColor);
        }
      }
    }

    function addTree(x, z) {
      builder.add(x, 1.5, z, 0x6d4a2c);
      builder.add(x, 2.5, z, 0x6d4a2c);

      const foliage = [0x4d7c3e, 0x5b8e44, 0x68a04b, 0x406c33];

      for (let y = 3.5; y <= 5.5; y += 1) {
        let r = y === 3.5 ? 1 : y === 4.5 ? 2 : 1;

        for (let dx = -r; dx <= r; dx++) {
          for (let dz = -r; dz <= r; dz++) {
            if (Math.abs(dx) + Math.abs(dz) <= r) {
              builder.add(x + dx, y, z + dz, pick(foliage));
            }
          }
        }
      }
    }

    function addBoat(x, z) {
      const wood = [0x7d5b3a, 0x8b6945, 0x694a2d, 0x9a7a50];

      for (let i = 0; i < 4; i++) {
        builder.add(x + i, 0.5, z, pick(wood));
      }

      for (let i = 1; i < 3; i++) {
        builder.add(x + i, 1.5, z, 0x6d5238);
      }

      builder.add(x + 1, 1.5, z, 0x6c5238);
      builder.add(x + 1, 2.5, z, 0x6c5238);

      for (let y = 2.5; y <= 3.5; y += 1) {
        for (let dz = -1; dz <= 1; dz++) {
          builder.add(x + 2, y, z + dz, 0xf4e9cd);
        }
      }
    }

    function addQuayDetails() {
      const lampPosts = [-30, -15, 0, 15, 30];

      for (const x of lampPosts) {
        for (const y of [1.5, 2.5, 3.5]) {
          builder.add(x, y, 17, 0x3f3f3f);
        }

        builder.add(x + 1, 4.5, 17, 0x3f3f3f);
        addGlow(x + 1, 4.5, 17, 0xffe6a0, 0.6);
      }

      addStall(-9, 20, 0xd94f4f);
      addStall(-3, 20, 0xd5b047);
      addStall(10, 20, 0x5ba46b);

      // Cargo near right warehouse.
      for (let x = 22; x <= 24; x++) {
        for (let z = 18; z <= 19; z++) {
          builder.add(x, 1.5, z, 0xa77c4c);
          if ((x + z) % 2 === 0) {
            builder.add(x, 2.5, z, 0x8b623b);
          }
        }
      }

      // Barrels.
      builder.add(20, 1.5, 19, 0x6f4c2f);
      builder.add(20, 2.5, 19, 0x825a35);
      builder.add(19, 1.5, 20, 0x6f4c2f);
    }

    function buildWorld() {
      builder = new StaticVoxelBuilder();

      const stone = [0x8a8171, 0x9a9180, 0x756c5d, 0xa79f8c];
      const grass = [0x4d7c3e, 0x5b8e44, 0x68a04b, 0x406c33];

      // Main harbor quay.
      for (let x = -42; x <= 42; x++) {
        for (let z = 16; z <= 52; z++) {
          const color = z >= 44 ? pick(grass) : pick(stone);
          builder.add(x, 0.5, z, color);
        }
      }

      // Quay edge walls.
      for (let x = -42; x <= 42; x++) {
        for (const y of [-0.5, -1.5]) {
          builder.add(x, y, 15, pick(stone));
        }
      }

      for (let z = 16; z <= 52; z++) {
        for (const y of [-0.5, -1.5]) {
          builder.add(-43, y, z, pick(stone));
          builder.add(43, y, z, pick(stone));
        }
      }

      for (let x = -43; x <= 43; x++) {
        for (const y of [-0.5, -1.5]) {
          builder.add(x, y, 53, pick(stone));
        }
      }

      // Harbor town.
      addBuilding(-34, 24, 7, 6, 3, 0xb5a58d, 0x87453f);
      addBuilding(-24, 23, 6, 5, 4, 0xa75f55, 0x613f3a);
      addBuilding(-14, 25, 5, 5, 3, 0xd7c7a8, 0x865042);
      addBuilding(6, 23, 7, 6, 3, 0x9fb3bb, 0x566f7d);
      addBuilding(16, 25, 6, 5, 4, 0xc0b775, 0x6c5741);
      addBuilding(27, 23, 8, 7, 3, 0x94806e, 0x4c5864);
      addBuilding(0, 33, 10, 6, 2, 0x8d8174, 0x5b646d);
      addBuilding(20, 18, 8, 6, 3, 0x7c5837, 0x473628);

      // Lighthouse on quay.
      addLighthouse(-38, 19, 8);

      // Breakwater and lighthouse at harbor mouth.
      addBreakwater();
      addLighthouse(46, -30, 9);

      // Piers.
      addPier(-34, -26, 2, 15);
      addPier(22, 30, 2, 15);

      // Quay life.
      addQuayDetails();

      // Greenery behind town.
      for (let x = -38; x <= 38; x += 8) {
        addTree(x, 47);
        addTree(x + 3, 50);
      }

      // Small boats.
      addBoat(-26, -2);
      addBoat(26, -2);
      addBoat(35, -18);
      addBoat(-12, -12);

      builder.build(scene);
    }

    function makeShip() {
      const shipGroup = new THREE.Group();
      ship = shipGroup;

      const hullDark = 0x51301d;
      const hullBrown = 0x6d4227;
      const hullRed = 0x8c3333;
      const deckWood = 0x9d7447;
      const cabinWood = 0x7f5430;
      const roofRed = 0xa84b3d;
      const sailCream = 0xf3ead1;
      const mastWood = 0x6c4c2d;

      function addShipMesh(x, y, z, color) {
        const mesh = new THREE.Mesh(sharedBox, lam(color));
        mesh.position.set(x, y, z);
        mesh.castShadow = true;
        mesh.receiveShadow = true;
        shipGroup.add(mesh);
        return mesh;
      }

      function addShipRect(x1, x2, y, z1, z2, color) {
        for (let x = x1; x <= x2; x++) {
          for (let z = z1; z <= z2; z++) {
            addShipMesh(x, y, z, color);
          }
        }
      }

      function addShipGlow(x, y, z, color, size = 1) {
        const mesh = new THREE.Mesh(
          sharedBox,
          new THREE.MeshBasicMaterial({ color })
        );
        mesh.position.set(x, y, z);
        mesh.scale.setScalar(size);
        shipGroup.add(mesh);
        return mesh;
      }

      function hullMask(x, z) {
        if (x < -14 || x > 13 || Math.abs(z) > 4) return false;

        let w = 4;

        if (x < -7) {
          w = Math.min(4, x + 14);
        }

        if (x > 11) {
          w = Math.min(4, 14 - x);
        }

        return Math.abs(z) <= w;
      }

      function hullEdge(x, z) {
        return (
          !hullMask(x + 1, z) ||
          !hullMask(x - 1, z) ||
          !hullMask(x, z + 1) ||
          !hullMask(x, z - 1)
        );
      }

      // Hull.
      for (let x = -13; x <= 13; x++) {
        for (let z = -4; z <= 4; z++) {
          if (!hullMask(x, z)) continue;

          if (hullEdge(x, z)) {
            const sideColor = (x % 5 === 0) ? hullRed : hullBrown;
            addShipMesh(x, 1, z, sideColor);
            addShipMesh(x, 2, z, hullDark);
          } else {
            addShipMesh(x, 2, z, deckWood);
          }
        }
      }

      // Bow point.
      addShipMesh(-14, 1, 0, hullDark);
      addShipMesh(-14, 2, 0, hullDark);
      addShipMesh(-15, 2, 0, hullDark);

      // Bowsprit.
      for (let x = -16; x <= -19; x++) {
        addShipMesh(x, 2, 0, mastWood);
      }

      for (let x = -17; x <= -18; x++) {
        addShipMesh(x, 3, 0, mastWood);
      }

      // Stern castle.
      addShipRect(9, 13, 3, -3, 3, cabinWood);
      addShipRect(10, 12, 4, -2, 2, cabinWood);
      addShipRect(8, 14, 5, -4, 4, roofRed);
      addShipRect(10, 12, 6, -2, 2, roofRed);

      // Stern windows and lanterns.
      addShipMesh(14, 3, 0, 0xf2e9c9);
      addShipMesh(14, 4, -1, 0xf2e9c9);
      addShipMesh(14, 4, 1, 0xf2e9c9);

      addShipMesh(14, 4, 3, 0x2f2f2f);
      addShipMesh(14, 4, -3, 0x2f2f2f);
      addShipGlow(14, 4, 3, 0xffe8a8, 0.7);
      addShipGlow(14, 4, -3, 0xffe8a8, 0.7);

      // Forward castle.
      addShipRect(-9, -5, 3, -2, 2, cabinWood);
      addShipRect(-10, -4, 4, -3, 3, roofRed);

      // Deck cargo.
      addShipMesh(-6, 3, 2, 0xa77c4c);
      addShipMesh(-7, 3, -2, 0xa77c4c);
      addShipMesh(5, 3, -2, 0x6f4d2e);
      addShipMesh(6, 3, -2, 0x6f4d2e);

      function addMast(x, top) {
        for (let y = 2; y <= top; y++) {
          addShipMesh(x, y, 0, mastWood);
        }
      }

      function addYard(x, y, len) {
        for (let z = -len; z <= len; z++) {
          addShipMesh(x, y, z, mastWood);
        }
      }

      function addSquareSail(x, yStart, yEnd, len, billow) {
        for (let y = yStart; y <= yEnd; y++) {
          for (let z = -len; z <= len; z++) {
            let ox = 0;

            if (billow > 0) {
              ox = Math.abs(z) <= len - 2 ? billow : Math.round(billow / 2);
            }

            const color = (y + z) % 2 ? sailCream : 0xe6dbc0;
            addShipMesh(x + ox, y, z, color);
          }
        }
      }

      // Foremast.
      addMast(-4, 8);
      addYard(-4, 6, 4);
      addSquareSail(-4, 4, 5, 4, 1);
      addYard(-4, 8, 3);
      addSquareSail(-4, 7, 7, 3, 1);

      // Mainmast.
      addMast(1, 10);
      addYard(1, 7, 6);
      addSquareSail(1, 5, 6, 6, 1);
      addYard(1, 9, 5);
      addSquareSail(1, 8, 8, 5, 1);

      // Mizzenmast.
      addMast(8, 7);
      addYard(8, 6, 4);
      addSquareSail(8, 4, 5, 4, 0);

      // Crow nests.
      addShipRect(-5, -3, 6, 0, 0, mastWood);
      addShipRect(0, 2, 8, 0, 0, mastWood);
      addShipRect(7, 9, 6, 0, 0, mastWood);

      // Jib.
      for (let t = 0; t <= 12; t++) {
        const x = Math.round(-19 + t);
        const y = Math.round(3 + t * 0.4);
        addShipMesh(x, y, 0, sailCream);
      }

      for (let z = -1; z <= 1; z++) {
        addShipMesh(-4, 6, z, 0xf3ead1);
      }

      // Flag.
      addShipMesh(13, 5, 0, mastWood);
      addShipMesh(13, 6, 0, mastWood);
      addShipMesh(13, 7, 0, mastWood);

      flagGroup = new THREE.Group();
      flagGroup.position.set(13, 7, 0);

      function addFlagMesh(x, y, z, color) {
        const mesh = new THREE.Mesh(sharedBox, lam(color));
        mesh.position.set(x, y, z);
        mesh.castShadow = true;
        flagGroup.add(mesh);
      }

      for (let x = 1; x <= 3; x++) {
        for (let y = -1; y <= 0; y++) {
          const c = (x + y) % 2 ? 0xd54b4b : 0xf8f4ea;
          addFlagMesh(x, y, 0, c);
        }
      }

      shipGroup.add(flagGroup);

      // Rigging lines.
      const ropePos = [];

      function rope(x1, y1, z1, x2, y2, z2) {
        ropePos.push(x1, y1, z1, x2, y2, z2);
      }

      // Forestays and backstays.
      rope(-4, 8, 0, -19, 3, 0);
      rope(1, 10, 0, -19, 3, 0);
      rope(1, 10, 0, 13, 5, 0);
      rope(8, 7, 0, 13, 5, 0);

      // Main shrouds.
      for (const z of [-4, -2, 2, 4]) {
        rope(1, 9, 0, 1, 2, z);
      }

      // Fore shrouds.
      for (const z of [-3, -1, 1, 3]) {
        rope(-4, 8, 0, -4, 2, z);
      }

      // Mizzen shrouds.
      for (const z of [-3, -1, 1, 3]) {
        rope(8, 7, 0, 8, 2, z);
      }

      const rigGeo = new THREE.BufferGeometry();
      rigGeo.setAttribute("position", new THREE.Float32BufferAttribute(ropePos, 3));

      const rig = new THREE.LineSegments(
        rigGeo,
        new THREE.LineBasicMaterial({
          color: 0x3b352d,
          transparent: true,
          opacity: 0.72
        })
      );

      shipGroup.add(rig);

      // Gangplank to quay.
      for (let z = 5; z <= 8; z++) {
        addShipMesh(7, 2, z, deckWood);

        if (z < 8) {
          addShipMesh(8, 3, z, deckWood);
          addShipMesh(6, 3, z, deckWood);
        }
      }

      shipGroup.position.set(0, -0.5, 10);
      scene.add(shipGroup);
    }

    function makeSeagull(x, y, z) {
      const group = new THREE.Group();

      const body = new THREE.Mesh(sharedBox, lam(0xffffff));
      body.scale.set(2.5, 1, 1.5);
      body.position.set(0, 0, 0);
      group.add(body);

      const head = new THREE.Mesh(sharedBox, lam(0x333333));
      head.scale.set(1, 1, 1);
      head.position.set(1.6, 0.5, 0);
      group.add(head);

      const wing1 = new THREE.Mesh(sharedBox, lam(0xffffff));
      wing1.scale.set(1, 0.2, 3);
      wing1.position.set(0, 0, 1.5);
      group.add(wing1);

      const wing2 = wing1.clone();
      wing2.position.set(0, 0, -1.5);
      group.add(wing2);

      group.position.set(x, y, z);
      group.userData = {
        wings: [wing1, wing2],
        phase: rand() * 10,
        speed: 1.5 + rand() * 2
      };

      scene.add(group);
      seagulls.push(group);
    }

    function makeCloud(x, y, z) {
      const group = new THREE.Group();
      const mat = lam(0xf7fbff);

      for (let i = 0; i < 12; i++) {
        const mesh = new THREE.Mesh(sharedBox, mat);
        mesh.scale.set(
          3 + rand() * 5,
          1 + rand() * 1.5,
          3 + rand() * 5
        );
        mesh.position.set(
          (rand() - 0.5) * 14,
          (rand() - 0.5) * 3,
          (rand() - 0.5) * 14
        );
        mesh.castShadow = false;
        mesh.receiveShadow = false;
        group.add(mesh);
      }

      group.position.set(x, y, z);
      group.userData.speed = 0.4 + rand() * 0.6;
      scene.add(group);
      clouds.push(group);
    }

    function init() {
      scene = new THREE.Scene();
      scene.background = new THREE.Color(0x88c7ef);
      scene.fog = new THREE.Fog(0x9fcdf2, 85, 210);

      camera = new THREE.PerspectiveCamera(
        45,
        window.innerWidth / window.innerHeight,
        0.1,
        500
      );
      camera.position.set(30, 20, 36);

      renderer = new THREE.WebGLRenderer({ antialias: true });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      renderer.setSize(window.innerWidth, window.innerHeight);
      renderer.shadowMap.enabled = true;
      renderer.shadowMap.type = THREE.PCFSoftShadowMap;
      renderer.outputColorSpace = THREE.SRGBColorSpace;
      renderer.toneMapping = THREE.ACESFilmicToneMapping;
      renderer.toneMappingExposure = 1.12;
      document.body.appendChild(renderer.domElement);

      controls = new OrbitControls(camera, renderer.domElement);
      controls.target.set(0, 4, 8);
      controls.enableDamping = true;
      controls.dampingFactor = 0.07;
      controls.minDistance = 14;
      controls.maxDistance = 140;
      controls.maxPolarAngle = Math.PI / 2 - 0.02;
      controls.update();

      const hemi = new THREE.HemisphereLight(0xa9d8ff, 0x4f6b4a, 0.9);
      scene.add(hemi);

      const sun = new THREE.DirectionalLight(0xffe7bf, 1.35);
      sun.position.set(48, 70, 28);
      sun.castShadow = true;
      sun.shadow.mapSize.set(2048, 2048);
      sun.shadow.camera.near = 1;
      sun.shadow.camera.far = 250;
      sun.shadow.camera.left = -95;
      sun.shadow.camera.right = 95;
      sun.shadow.camera.top = 95;
      sun.shadow.camera.bottom = -95;
      sun.shadow.bias = -0.0006;
      scene.add(sun);

      // Water surface as a single voxel-textured plane.
      waterTex = makeWaterTexture();

      const waterMat = new THREE.MeshLambertMaterial({
        map: waterTex,
        color: 0xffffff
      });

      const waterMesh = new THREE.Mesh(
        new THREE.PlaneGeometry(150, 150),
        waterMat
      );
      waterMesh.rotation.x = -Math.PI / 2;
      waterMesh.position.y = 0;
      waterMesh.receiveShadow = true;
      scene.add(waterMesh);

      buildWorld();
      makeShip();

      // Birds.
      for (let i = 0; i < 7; i++) {
        makeSeagull(
          -25 + rand() * 50,
          10 + rand() * 6,
          -8 + rand() * 22
        );
      }

      // Clouds.
      makeCloud(-45, 27, -15);
      makeCloud(15, 31, -35);
      makeCloud(55, 29, 5);
      makeCloud(-20, 34, 40);

      window.addEventListener("resize", onResize);
      animate();
    }

    function onResize() {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    }

    let lastTime = 0;

    function animate(time) {
      requestAnimationFrame(animate);

      const t = time * 0.001;
      const dt = Math.min(0.05, t - lastTime);
      lastTime = t;

      controls.update();

      if (ship) {
        ship.position.y = -0.5 + Math.sin(t * 1.25) * 0.11;
        ship.position.z = 10 + Math.sin(t * 0.38) * 0.16;
        ship.rotation.z = Math.sin(t * 0.82) * 0.013;
        ship.rotation.x = Math.sin(t * 0.67 + 1.7) * 0.010;
      }

      if (flagGroup) {
        flagGroup.rotation.z = Math.sin(t * 9.0) * 0.17;
      }

      if (waterTex) {
        waterTex.offset.x = t * 0.015;
        waterTex.offset.y = t * 0.010;
      }

      for (const bird of seagulls) {
        const u = bird.userData;

        bird.position.x += dt * u.speed;
        if (bird.position.x > 62) bird.position.x = -62;

        bird.position.y =
          10.5 + Math.sin(t * 1.3 + u.phase) * 2.4;
        bird.position.z =
          8 + Math.sin(t * 0.7 + u.phase) * 7;

        for (let i = 0; i < u.wings.length; i++) {
          u.wings[i].scale.z =
            2.4 + Math.sin(t * 14 + u.phase + i * 0.3) * 1.6;
        }
      }

      for (const cloud of clouds) {
        cloud.position.x += dt * cloud.userData.speed;
        if (cloud.position.x > 90) cloud.position.x = -90;
      }

      renderer.render(scene, camera);
    }

    init();
  </script>
</body>
</html>
