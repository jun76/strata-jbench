Here is a complete single-file Three.js voxel scene. Save it as something like `harbor.html` and open it in Chrome. It uses CDN imports, so keep an internet connection for the first load.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Voxel Harbor — Sailing Ship Calling At Harbor</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    html, body {
      margin: 0;
      height: 100%;
      overflow: hidden;
      background: #9bd2ef;
    }
    #ui {
      position: fixed;
      left: 12px;
      top: 12px;
      color: #102331;
      font: 600 13px/1.35 system-ui, Segoe UI, Arial;
      background: rgba(255,255,255,0.58);
      padding: 8px 10px;
      border-radius: 8px;
      backdrop-filter: blur(5px);
      pointer-events: none;
      z-index: 10;
    }
    #fallback {
      display: none;
      position: fixed;
      inset: 0;
      background: white;
      color: #222;
      padding: 22px;
      font: 16px system-ui, Segoe UI, Arial;
      z-index: 20;
    }
  </style>
</head>
<body>
  <div id="ui">
    Voxel sailing ship calling at harbor<br>
    Drag: orbit &nbsp;•&nbsp; Scroll: zoom &nbsp;•&nbsp; Right-drag: pan
  </div>
  <div id="fallback">
    Could not load Three.js from the CDN. Use a modern browser with internet and allow import maps.
  </div>

  <script>
    window.addEventListener('error', () => {
      document.getElementById('fallback').style.display = 'block';
    });
  </script>

  <script type="importmap">
  {
    "imports": {
      "three": "https://cdn.jsdelivr.net/npm/three@0.160.1/build/three.module.js",
      "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.1/examples/jsm/"
    }
  }
  </script>

  <script type="module">
    import * as THREE from 'three';
    import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

    const C = {
      waterDeep: 0x1867a8,
      waterMid: 0x2d8bc9,
      waterShallow: 0x55a6d8,
      harborWater: 0x3d9fd0,

      sand: 0xdcc578,
      grass: 0x5fb04e,
      grassDark: 0x438a39,
      rock: 0x8c8f93,
      stone: 0xa5a7aa,
      stoneDark: 0x83868a,

      earth: 0x7e5e3c,
      earthDark: 0x5d452c,

      woodQuay: 0x9d6a38,
      woodDark: 0x623e23,
      deck: 0xc9a063,

      shipDark: 0x2b2d31,
      shipRed: 0x8f3c30,
      shipWhite: 0xe9dbbb,
      shipWood: 0xb78354,
      mast: 0xbe996a,
      sail: 0xf4ecda,
      rig: 0x2f2f2f,

      redWarehouse: 0xc25040,
      blueWarehouse: 0x4c7fa8,
      cream: 0xf2e8d4,
      roofRed: 0xb14030,
      roofBlue: 0x3a5e9b,
      roofGray: 0x7b7f83,
      door: 0x533722,
      window: 0x8cc7e8,

      lighthouseWhite: 0xf7f7f7,
      lighthouseRed: 0xd1443d,
      light: 0xffe566,

      crane: 0xa77040,
      crate: 0xb57c44,
      barrel: 0x8b5f36,

      treeTrunk: 0x6d4728,
      treeLeaf: 0x4b9a45,

      flagRed: 0xd1443d,
      flagBlue: 0x3f6db0,
    };

    function frac(n) { return n - Math.floor(n); }

    function rand(x, z) {
      return frac(Math.sin(x * 12.9898 + z * 78.233) * 43758.5453);
    }

    function terrainNoise(x, z) {
      return 0.5 + 0.5 * Math.sin(x * 0.17 + z * 0.07) * Math.cos(x * 0.07 - z * 0.19);
    }

    function isLand(x, z) {
      // Mainland north of harbor.
      if (z >= 11) return true;

      // East / west harbor walls and breakwater connections.
      if ((x <= -31 || x >= 31) && z >= -32) return true;

      // Mouth breakwaters, leaving a narrow channel through the center.
      if (z >= -32 && z <= -31 && Math.abs(x) >= 12 && Math.abs(x) <= 30) return true;

      return false;
    }

    function landHeight(x, z) {
      if (!isLand(x, z)) return null;

      if (z >= 11) {
        // Flat harbor-side town area, then hills farther north.
        if (z <= 35 && Math.abs(x) <= 40) return 2;
        return 2 + Math.floor(Math.max(0, terrainNoise(x, z) * 3));
      }

      if (Math.abs(x) >= 31 && z >= -32) return 3;

      if (z >= -32 && z <= -31 && Math.abs(x) >= 12 && Math.abs(x) <= 30) return 2;

      return 2;
    }

    function landTopColor(x, z, h) {
      if (z >= 11) {
        if (z <= 17 && Math.abs(x) <= 30) return C.woodQuay;
        if (z <= 35 && Math.abs(x) <= 40) return C.grass;
        return terrainNoise(x, z) > 0.62 ? C.rock : C.grassDark;
      }

      if (Math.abs(x) >= 31 && z >= -32) return C.stone;

      if (z >= -32 && z <= -31 && Math.abs(x) >= 12 && Math.abs(x) <= 30) return C.stoneDark;

      return C.sand;
    }

    function landFillColor(x, z, y) {
      if (Math.abs(x) >= 31 && z >= -32) return y >= 0 ? C.stone : C.stoneDark;

      if (z >= -32 && z <= -31 && Math.abs(x) >= 12 && Math.abs(x) <= 30) {
        return y >= 0 ? C.stone : C.stoneDark;
      }

      return y <= -2 ? C.earthDark : C.earth;
    }

    const staticBlocks = [];
    const waterExclude = new Set();

    function addBlock(x, y, z, color) {
      staticBlocks.push({ x, y, z, color });
    }

    function addBoxRegion(x1, x2, y1, y2, z1, z2, color) {
      if (x1 > x2) [x1, x2] = [x2, x1];
      if (y1 > y2) [y1, y2] = [y2, y1];
      if (z1 > z2) [z1, z2] = [z2, z1];

      for (let x = x1; x <= x2; x++) {
        for (let y = y1; y <= y2; y++) {
          for (let z = z1; z <= z2; z++) {
            addBlock(x, y, z, color);
          }
        }
      }
    }

    // Terrain.
    const G = 50;

    for (let x = -G; x <= G; x++) {
      for (let z = -G; z <= G; z++) {
        const h = landHeight(x, z);
        if (h === null) continue;

        const top = landTopColor(x, z, h);

        for (let y = -3; y <= h; y++) {
          addBlock(x, y, z, y === h ? top : landFillColor(x, z, y));
        }
      }
    }

    // Dock along north harbor side.
    function addDock() {
      for (let x = -24; x <= 24; x++) {
        addBlock(x, 2, 10, C.woodQuay);
        addBlock(x, 1, 10, C.woodDark);
        addBlock(x, 0, 10, C.woodDark);
        waterExclude.add(x * 1000 + 10);
      }
    }

    function addQuayProps() {
      const cratePositions = [-18, -15, -12, 12, 15, 18];

      for (const x of cratePositions) {
        addBoxRegion(x, x + 1, 3, 4, 12, 13, C.crate);
      }

      for (const x of [-8, 8]) {
        addBoxRegion(x, x + 1, 3, 4, 13, 14, C.barrel);
        addBoxRegion(x, x + 1, 5, 5, 13, 14, C.barrel);
      }
    }

    function addWarehouse(cx, cz, w, d, h, wall, roof) {
      const x2 = cx + w - 1;
      const z2 = cz + d - 1;
      const y0 = 3;
      const y1 = 3 + h - 1;

      for (let x = cx; x <= x2; x++) {
        for (let z = cz; z <= z2; z++) {
          addBlock(x, y0, z, C.woodDark); // floor

          for (let y = y0 + 1; y <= y1; y++) {
            const edge = (x === cx || x === x2 || z === cz || z === z2);
            if (!edge) continue;

            let col = wall;

            // Door on harbor-facing side.
            if (z === cz && x >= cx + Math.floor(w / 2) - 1 && x <= cx + Math.floor(w / 2) && y === y0 + 1) {
              col = C.door;
            }

            // Simple windows.
            if (y === y0 + 2 && (((x + cz) % 3 === 0 && (x === cx || x === x2)) ||
                                 ((z + cx) % 3 === 0 && (z === cz || z === z2)))) {
              col = C.window;
            }

            addBlock(x, y, z, col);
          }
        }
      }

      // Flat overhanging roof.
      addBoxRegion(cx - 1, x2 + 1, y1 + 1, y1 + 1, cz - 1, z2 + 1, roof);
    }

    function addWarehouses() {
      addWarehouse(-20, 16, 10, 7, 5, C.redWarehouse, C.roofRed);
      addWarehouse(10, 16, 10, 7, 5, C.blueWarehouse, C.roofGray);
      addWarehouse(-5, 17, 6, 5, 4, C.cream, C.roofRed);
    }

    function addCrane() {
      // Tower.
      for (let x = -10; x <= -8; x++) {
        for (let z = 10; z <= 12; z++) {
          for (let y = 3; y <= 11; y++) {
            addBlock(x, y, z, C.crane);
          }
        }
      }

      // Arm.
      for (let x = -10; x <= -2; x++) {
        addBlock(x, 12, 11, C.crane);
      }

      // Diagonal support.
      for (let i = 0; i <= 4; i++) {
        const x = -10 + i;
        const y = 7 + i;
        addBlock(x, y, 11, C.crane);
      }

      // Hook rope and cargo crate.
      for (let y = 8; y <= 11; y++) {
        addBlock(-2, y, 11, C.rig);
      }

      addBoxRegion(-3, -1, 5, 7, 10, 12, C.crate);
    }

    function addTree(x, z, baseY = 3) {
      if (baseY < 3) return;

      addBlock(x, baseY, z, C.treeTrunk);
      addBlock(x, baseY + 1, z, C.treeTrunk);

      const leafY = baseY + 2;
      for (let dx = -1; dx <= 1; dx++) {
        for (let dz = -1; dz <= 1; dz++) {
          addBlock(x + dx, leafY, z + dz, C.treeLeaf);
        }
      }

      addBlock(x, leafY + 1, z, C.treeLeaf);
    }

    function addHouse(cx, cz, wall, roof) {
      const size = 4;
      const x2 = cx + size - 1;
      const z2 = cz + size - 1;
      const y0 = 3;
      const yTop = 5;

      for (let x = cx; x <= x2; x++) {
        for (let z = cz; z <= z2; z++) {
          addBlock(x, y0, z, C.woodDark); // floor

          for (let y = y0 + 1; y <= yTop; y++) {
            const edge = (x === cx || x === x2 || z === cz || z === z2);
            if (!edge) continue;

            let col = wall;

            // Door.
            if (z === cz && x >= cx + 1 && x <= cx + 2 && y === y0 + 1) col = C.door;

            // Windows.
            if (y === y0 + 2 &&
                (((x + cz) % 3 === 0 && (x === cx || x === x2)) ||
                 ((z + cx) % 3 === 0 && (z === cz || z === z2)))) {
              col = C.window;
            }

            addBlock(x, y, z, col);
          }
        }
      }

      addBoxRegion(cx - 1, x2 + 1, 6, 6, cz - 1, z2 + 1, roof);
      addBlock(cx + 2, 7, cz + 2, C.stoneDark); // chimney
    }

    function addTown() {
      const palettes = [
        [C.cream, C.roofRed],
        [C.cream, C.roofBlue],
        [C.woodQuay, C.roofGray],
        [C.stone, C.roofGray],
        [C.blueWarehouse, C.roofRed],
        [C.redWarehouse, C.roofGray],
      ];

      for (let x = -25; x <= 25; x += 5) {
        for (let z = 26; z <= 35; z += 5) {
          const r = rand(x, z);

          if (r < 0.12) {
            addTree(x, z, 3);
          } else if (r < 0.22) {
            // empty lot
          } else {
            const p = palettes[Math.floor(r * palettes.length) % palettes.length];
            addHouse(x, z, p[0], p[1]);
          }
        }
      }

      // Trees farther north on hills.
      for (let x = -48; x <= 48; x += 2) {
        for (let z = 36; z <= 49; z += 2) {
          const h = landHeight(x, z);
          if (h !== null && rand(x, z) > 0.88) {
            addTree(x, z, h + 1);
          }
        }
      }
    }

    function addLighthouse(cx, cz, height) {
      // Small support shelf over water toward harbor.
      addBoxRegion(cx - 1, cx + 1, 2, 2, cz + 1, cz + 1, C.stone);

      for (let y = 3; y <= height - 2; y++) {
        const redBand = (Math.floor((y - 3) / 3) % 2) === 0;
        addBoxRegion(cx - 1, cx + 1, y, y, cz - 1, cz + 1, redBand ? C.lighthouseRed : C.lighthouseWhite);
      }

      if (height > 5) {
        // Gallery.
        addBoxRegion(cx - 2, cx + 2, height - 1, height - 1, cz - 2, cz + 2, C.lighthouseWhite);

        // Lamp room, with bright center voxel.
        for (let x = cx - 1; x <= cx + 1; x++) {
          for (let z = cz - 1; z <= cz + 1; z++) {
            const center = (x === cx && z === cz);
            addBlock(x, height, z, center ? C.light : C.lighthouseWhite);
          }
        }

        addBlock(cx, height + 1, cz, C.lighthouseRed);
      }
    }

    const SHIP_X = 0;
    const SHIP_Z = 6;

    function addShipBlock(x, y, z, color) {
      const ax = SHIP_X + x;
      const az = SHIP_Z + z;
      addBlock(ax, y, az, color);

      if (y === 0) {
        waterExclude.add(ax * 1000 + az);
      }
    }

    function addShipBox(x1, x2, y1, y2, z1, z2, color) {
      if (x1 > x2) [x1, x2] = [x2, x1];
      if (y1 > y2) [y1, y2] = [y2, y1];
      if (z1 > z2) [z1, z2] = [z2, z1];

      for (let x = x1; x <= x2; x++) {
        for (let y = y1; y <= y2; y++) {
          for (let z = z1; z <= z2; z++) {
            addShipBlock(x, y, z, color);
          }
        }
      }
    }

    function hullHalf(x) {
      const d = Math.abs(x);
      if (d <= 8) return 3;
      if (d === 9) return 2;
      if (d === 10) return 2;
      if (d === 11) return 1;
      return 0;
    }

    function addSail(xOff, y1, y2, z1, z2) {
      for (let y = y1; y <= y2; y++) {
        for (let z = z1; z <= z2; z++) {
          // Skip the center voxel to avoid duplicating the mast.
          if (z === 0) continue;

          const edge = (y === y1 || y === y2 || z === z1 || z === z2);
          addShipBlock(xOff, y, z, edge ? C.rig : C.sail);
        }
      }
    }

    function addYard(xOff, y, z1, z2) {
      for (let z = z1; z <= z2; z++) {
        if (z === 0) continue;
        addShipBlock(xOff, y, z, C.mast);
      }
    }

    function addMast(xOff, zOff, height) {
      for (let y = 3; y <= height; y++) {
        addShipBlock(xOff, y, zOff, C.mast);
      }
    }

    function addLineShip(x1, y1, z1, x2, y2, z2, color) {
      const steps = Math.max(
        1,
        Math.ceil(
          Math.max(Math.abs(x2 - x1), Math.abs(y2 - y1), Math.abs(z2 - z1)) * 1.5
        )
      );

      // Skip endpoints to avoid exact-color z-fighting with masts / hull blocks.
      for (let i = 1; i < steps; i++) {
        const t = i / steps;
        const x = Math.round(x1 + (x2 - x1) * t);
        const y = Math.round(y1 + (y2 - y1) * t);
        const z = Math.round(z1 + (z2 - z1) * t);

        if (y > 2) addShipBlock(x, y, z, color);
      }
    }

    function addShip() {
      // Hull.
      for (let x = -12; x <= 12; x++) {
        const half = hullHalf(x);

        for (let z = -half; z <= half; z++) {
          for (let y = -2; y <= 2; y++) {
            if (y === -2 && Math.abs(z) === half) continue;

            let col;

            if (y === -2 || y === -1) {
              col = C.shipDark;
            } else if (y === 0) {
              col = C.shipRed;
            } else if (y === 1) {
              const edge = (Math.abs(z) === half || Math.abs(x) === 11 || Math.abs(x) === 12);
              col = edge ? C.shipRed : C.shipWhite;
            } else {
              col = C.deck;
            }

            addShipBlock(x, y, z, col);
          }
        }
      }

      // Sterncastle.
      addShipBox(-12, -9, 3, 5, -2, 2, C.shipWood);
      addShipBox(-12, -9, 6, 6, -3, 3, C.deck);

      // Forecastle.
      addShipBox(10, 12, 3, 4, -2, 2, C.shipWood);
      addShipBox(10, 12, 5, 5, -3, 3, C.deck);

      // Cargo / barrels on deck.
      addShipBox(-4, -3, 3, 4, -2, -1, C.crate);
      addShipBox(3, 4, 3, 4, 1, 2, C.crate);
      addShipBox(-2, -1, 3, 3, 2, 3, C.crate);

      // Bowsprit.
      addLineShip(13, 6, 0, 16, 9, 0, C.mast);

      // Rigging.
      addLineShip(0, 17, 0, 6, 15, 0, C.rig);   // main to fore
      addLineShip(6, 15, 0, 13, 6, 0, C.rig);   // fore to bowsprit stay
      addLineShip(0, 17, 0, -6, 13, 0, C.rig);  // main to mizzen
      addLineShip(-6, 13, 0, -12, 8, 0, C.rig); // mizzen to stern area

      // Masts.
      addMast(0, 0, 18);   // main
      addMast(6, 0, 15);   // fore
      addMast(-6, 0, 13);  // mizzen

      // Yards and square sails.
      addYard(0, 8, -5, 5);
      addSail(0, 9, 11, -4, 4);
      addYard(0, 12, -5, 5);
      addSail(0, 13, 15, -4, 4);
      addYard(0, 16, -4, 4);

      addYard(6, 8, -5, 5);
      addSail(6, 9, 11, -4, 4);
      addYard(6, 12, -5, 5);
      addSail(6, 13, 14, -4, 4);

      addYard(-6, 8, -4, 4);
      addSail(-6, 9, 11, -3, 3);
      addYard(-6, 12, -4, 4);
      addSail(-6, 13, 13, -3, 3);

      // Flags.
      addShipBlock(0, 19, 0, C.flagRed);
      addShipBlock(0, 19, 1, C.flagRed);

      addShipBlock(6, 16, 0, C.flagBlue);
      addShipBlock(6, 16, 1, C.flagBlue);

      addShipBlock(-6, 14, 0, C.flagRed);
    }

    function addSmallBoat(cx, cz) {
      function b(x, y, z, color) {
        addBlock(cx + x, y, cz + z, color);
        if (y === 0) {
          waterExclude.add((cx + x) * 1000 + (cz + z));
        }
      }

      for (let x = -3; x <= 3; x++) {
        const half = Math.abs(x) > 2 ? 0 : 1;

        for (let z = -half; z <= half; z++) {
          b(x, -1, z, C.shipDark);
          b(x, 0, z, C.shipRed);
          b(x, 1, z, C.deck);
        }
      }

      for (let y = 2; y <= 9; y++) {
        b(0, y, 0, C.mast);
      }

      for (let y = 3; y <= 8; y++) {
        for (let z = -2; z <= 2; z++) {
          if (z === 0) continue;
          const edge = (y === 3 || y === 8 || z === -2 || z === 2);
          addBlock(cx, y, cz + z, edge ? C.rig : C.sail);
        }
      }

      addBlock(cx, 10, cz, C.flagBlue);
    }

    function addStructures() {
      addDock();
      addQuayProps();
      addWarehouses();
      addCrane();
      addTown();

      addLighthouse(18, -31, 17);
      addLighthouse(-18, -31, 9);

      addShip();

      addSmallBoat(-16, 4);
      addSmallBoat(16, -8);
    }

    addStructures();

    function isHarborWater(x, z) {
      if (x >= -30 && x <= 30 && z >= -30 && z <= 10) return true;
      if (Math.abs(x) <= 13 && z >= -33 && z <= -30) return true;
      return false;
    }

    function nearShore(x, z) {
      for (let dx = -1; dx <= 1; dx++) {
        for (let dz = -1; dz <= 1; dz++) {
          if (isLand(x + dx, z + dz)) return true;
        }
      }
      return false;
    }

    function waterColor(x, z) {
      if (isHarborWater(x, z)) return C.harborWater;
      if (nearShore(x, z)) return C.waterShallow;
      if (z < -28 || Math.abs(x) > 40) return C.waterDeep;
      return C.waterMid;
    }

    function waterAmp(x, z) {
      if (isHarborWater(x, z) && z >= -29) return 0.06;
      if (Math.abs(x) <= 13 && z <= -30) return 0.18;
      if (z < -30 || x < -32 || x > 32 || z > 20) return 0.28;
      return 0.14;
    }

    const waterList = [];

    for (let x = -G; x <= G; x++) {
      for (let z = -G; z <= G; z++) {
        if (isLand(x, z)) continue;
        if (waterExclude.has(x * 1000 + z)) continue;

        waterList.push({
          x,
          z,
          color: waterColor(x, z),
          amp: waterAmp(x, z),
          phase: rand(x, z) * Math.PI * 2,
        });
      }
    }

    function createInstancedMesh(items, castShadow = true, receiveShadow = true) {
      const geometry = new THREE.BoxGeometry(0.96, 0.96, 0.96);
      const material = new THREE.MeshStandardMaterial({
        vertexColors: true,
        roughness: 0.92,
        metalness: 0.04,
      });

      const mesh = new THREE.InstancedMesh(geometry, material, items.length);
      mesh.frustumCulled = false;
      mesh.castShadow = castShadow;
      mesh.receiveShadow = receiveShadow;

      const dummy = new THREE.Object3D();
      const color = new THREE.Color();

      for (let i = 0; i < items.length; i++) {
        const item = items[i];
        dummy.position.set(item.x, item.y, item.z);
        dummy.scale.set(1, 1, 1);
        dummy.updateMatrix();

        mesh.setMatrixAt(i, dummy.matrix);
        color.setHex(item.color);
        mesh.setColorAt(i, color);
      }

      mesh.instanceMatrix.needsUpdate = true;
      if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;

      return mesh;
    }

    let waterX, waterZ, waterPhase, waterAmpArr;
    let waterMesh;
    const waterScaleY = 0.9;

    function createWaterMesh(items) {
      const count = items.length;

      const geometry = new THREE.BoxGeometry(0.96, 0.96, 0.96);
      const material = new THREE.MeshStandardMaterial({
        vertexColors: true,
        roughness: 0.38,
        metalness: 0.18,
      });

      const mesh = new THREE.InstancedMesh(geometry, material, count);
      mesh.frustumCulled = false;
      mesh.castShadow = false;
      mesh.receiveShadow = true;

      waterX = new Float32Array(count);
      waterZ = new Float32Array(count);
      waterPhase = new Float32Array(count);
      waterAmpArr = new Float32Array(count);

      const dummy = new THREE.Object3D();
      const color = new THREE.Color();

      for (let i = 0; i < count; i++) {
        const item = items[i];

        waterX[i] = item.x;
        waterZ[i] = item.z;
        waterPhase[i] = item.phase;
        waterAmpArr[i] = item.amp;

        dummy.position.set(item.x, 0, item.z);
        dummy.scale.set(1, waterScaleY, 1);
        dummy.updateMatrix();

        mesh.setMatrixAt(i, dummy.matrix);
        color.setHex(item.color);
        mesh.setColorAt(i, color);
      }

      mesh.instanceMatrix.needsUpdate = true;
      if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;

      return mesh;
    }

    // Scene / renderer / camera.
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x9bd2ef);
    scene.fog = new THREE.Fog(0x9bd2ef, 88, 235);

    const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 1200);
    camera.position.set(62, 48, 68);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    document.body.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.target.set(0, 6, 4);
    controls.enableDamping = true;
    controls.dampingFactor = 0.06;
    controls.maxPolarAngle = Math.PI * 0.49;
    controls.minDistance = 10;
    controls.maxDistance = 180;
    controls.autoRotate = true;
    controls.autoRotateSpeed = 0.35;

    // Lights.
    const hemi = new THREE.HemisphereLight(0xc7eaff, 0x5a4332, 0.75);
    scene.add(hemi);

    const ambient = new THREE.AmbientLight(0xffffff, 0.15);
    scene.add(ambient);

    const sun = new THREE.DirectionalLight(0xfff4d6, 1.25);
    sun.position.set(70, 95, -55);
    sun.castShadow = true;
    sun.shadow.mapSize.set(2048, 2048);
    sun.shadow.bias = -0.0005;

    const sc = sun.shadow.camera;
    sc.left = -95;
    sc.right = 95;
    sc.top = 95;
    sc.bottom = -95;
    sc.near = 1;
    sc.far = 260;

    sun.target.position.set(0, 5, 5);
    scene.add(sun);
    scene.add(sun.target);

    // Sea base plane under animated voxel water.
    const seaPlane = new THREE.Mesh(
      new THREE.PlaneGeometry(260, 260),
      new THREE.MeshStandardMaterial({ color: C.waterDeep, roughness: 0.6, metalness: 0.2 })
    );
    seaPlane.rotation.x = -Math.PI / 2;
    seaPlane.position.y = -1.9;
    seaPlane.receiveShadow = false;
    scene.add(seaPlane);

    // Main static voxel terrain, buildings, ship, etc.
    const staticMesh = createInstancedMesh(staticBlocks, true, true);
    scene.add(staticMesh);

    // Animated voxel water.
    waterMesh = createWaterMesh(waterList);
    scene.add(waterMesh);

    // Lighthouse light.
    const lighthousePoint = new THREE.PointLight(0xffe277, 18, 80, 2);
    lighthousePoint.position.set(18, 17, -31);
    scene.add(lighthousePoint);

    // Resize.
    window.addEventListener('resize', () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    });

    const clock = new THREE.Clock();
    const dummy = new THREE.Object3D();

    function animate() {
      requestAnimationFrame(animate);

      const t = clock.getElapsedTime();
      controls.update();

      for (let i = 0; i < waterMesh.count; i++) {
        const x = waterX[i];
        const z = waterZ[i];
        const y = Math.sin(t * 1.35 + waterPhase[i]) * waterAmpArr[i];

        dummy.position.set(x, y, z);
        dummy.scale.set(1, waterScaleY, 1);
        dummy.updateMatrix();

        waterMesh.setMatrixAt(i, dummy.matrix);
      }

      waterMesh.instanceMatrix.needsUpdate = true;

      renderer.render(scene, camera);
    }

    animate();
  </script>
</body>
</html>
```