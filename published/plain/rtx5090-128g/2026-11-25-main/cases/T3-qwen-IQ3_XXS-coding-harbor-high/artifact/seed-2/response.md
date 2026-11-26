Save this as a single `.html` file and open it in Chrome:

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
      width: 100%;
      height: 100%;
      overflow: hidden;
      background: #101418;
    }
    canvas { display: block; }
    #hint {
      position: fixed;
      left: 12px;
      bottom: 12px;
      color: #f8fbff;
      background: rgba(0, 0, 0, 0.35);
      padding: 8px 12px;
      border-radius: 8px;
      font: 14px/1.3 system-ui, sans-serif;
      opacity: 0.85;
      transition: opacity 1s;
      pointer-events: none;
    }
  </style>
</head>
<body>
  <div id="hint">Drag to orbit • Scroll to zoom • Right-drag to pan</div>

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

    // ------------------------------------------------------------------
    // Basic scene setup
    // ------------------------------------------------------------------
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xa9d6f0);
    scene.fog = new THREE.Fog(0xa9d6f0, 135, 360);

    const camera = new THREE.PerspectiveCamera(
      50,
      window.innerWidth / window.innerHeight,
      0.1,
      1000
    );
    camera.position.set(-54, 36, 62);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    document.body.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.target.set(0, 9, 4);
    controls.enableDamping = true;
    controls.dampingFactor = 0.06;
    controls.minDistance = 24;
    controls.maxDistance = 240;
    controls.minPolarAngle = 0.12;
    controls.maxPolarAngle = Math.PI * 0.47;
    controls.autoRotate = true;
    controls.autoRotateSpeed = 0.45;
    controls.update();

    renderer.domElement.addEventListener(
      "pointerdown",
      () => { controls.autoRotate = false; },
      { once: true }
    );

    // Lights
    scene.add(new THREE.AmbientLight(0xffffff, 0.55));
    scene.add(new THREE.HemisphereLight(0xbfdfff, 0x586b50, 0.65));

    const sun = new THREE.DirectionalLight(0xfff3dc, 1.2);
    sun.position.set(-55, 80, 25);
    scene.add(sun);

    // ------------------------------------------------------------------
    // Instanced voxel renderer
    // ------------------------------------------------------------------
    const MAX_VOXELS = 110000;
    const boxGeometry = new THREE.BoxGeometry(1, 1, 1);
    const voxelMaterial = new THREE.MeshLambertMaterial({ color: 0xffffff });
    const voxels = new THREE.InstancedMesh(boxGeometry, voxelMaterial, MAX_VOXELS);
    voxels.count = 0;
    voxels.frustumCulled = false;
    scene.add(voxels);

    const dummy = new THREE.Object3D();
    const tmpColor = new THREE.Color();
    let voxelCount = 0;

    const C = {
      water:       0x2780bf,
      waterMid:    0x1e6aa7,
      waterDeep:   0x154a7c,
      foam:        0xf4f7f7,

      dock:        0xa07047,
      dockDark:    0x6f4a2f,
      deck:        0xd0aa72,
      deckDark:    0x8a6540,
      woodDark:    0x443022,
      rope:        0xd6c39c,

      hull:        0x7c4a22,
      hullDark:    0x4c2b14,
      hullStripe:  0xe9e3d4,

      cabin:       0xe4d3b3,
      cabinDark:   0xc0ad8d,
      window:      0xffdf8f,
      door:        0x3b2a1d,

      mast:        0x8a7146,
      mastDark:    0x5e4a2d,
      sail:        0xf6f1e4,
      sailDark:    0xd7cfc2,

      flag:        0xd94a3d,
      flagDark:    0xa83227,

      stone:       0x8f98a3,
      stoneDark:   0x68717b,
      lamp:        0xffdc7c,

      crate:       0xb07f46,
      crateDark:   0x7c562f,
      barrel:      0x8f5d33,
      barrelDark:  0x5b391e,

      grass:       0x679c57,
      grassDark:   0x4f7c42,
      dirt:        0x8d7352,

      warehouse:   0x9f8f7d,
      roof:        0xb14b3d,

      trunk:       0x64462d,
      leaf:        0x568f4b,

      white:       0xffffff
    };

    function addVoxel(x, y, z, color, sx = 1, sy = 1, sz = 1) {
      if (voxelCount >= MAX_VOXELS) return -1;
      const id = voxelCount;

      dummy.position.set(x, y, z);
      dummy.scale.set(sx, sy, sz);
      dummy.rotation.set(0, 0, 0);
      dummy.updateMatrix();

      voxels.setMatrixAt(id, dummy.matrix);
      voxels.setColorAt(id, tmpColor.set(color));

      voxelCount++;
      return id;
    }

    function addFill(minX, maxX, minY, maxY, minZ, maxZ, color) {
      for (let x = minX; x <= maxX; x++) {
        for (let y = minY; y <= maxY; y++) {
          for (let z = minZ; z <= maxZ; z++) {
            addVoxel(x, y, z, color);
          }
        }
      }
    }

    // ------------------------------------------------------------------
    // Scene layout
    // ------------------------------------------------------------------
    const shipX = 0;
    const shipZ = 4;

    const DOCK = { xMin: -40, xMax: 18, zMin: -36, zMax: -4 };
    const SIDE_PIER = { xMin: 19, xMax: 28, zMin: -12, zMax: 6 };
    const LAND = { xMin: -44, xMax: 24, zMin: -48, zMax: -37 };
    const SHIP_BOX = {
      xMin: shipX - 16,
      xMax: shipX + 16,
      zMin: shipZ - 6,
      zMax: shipZ + 6
    };

    function inRect(x, z, r) {
      return x >= r.xMin && x <= r.xMax && z >= r.zMin && z <= r.zMax;
    }

    // ------------------------------------------------------------------
    // Water
    // ------------------------------------------------------------------
    const waterData = [];

    function buildWater() {
      for (let x = -52; x <= 48; x++) {
        for (let z = -48; z <= 62; z++) {
          if (
            inRect(x, z, DOCK) ||
            inRect(x, z, SIDE_PIER) ||
            inRect(x, z, LAND) ||
            inRect(x, z, SHIP_BOX)
          ) continue;

          const n = (((x * 7 + z * 13) % 13) + 13) % 13;
          let color = C.water;
          if (n < 2) color = C.waterDeep;
          else if (n < 6) color = C.waterMid;

          const baseY = -0.45;
          const sx = 1.08;
          const sy = 1.8;
          const sz = 1.08;

          const id = addVoxel(x, baseY, z, color, sx, sy, sz);
          if (id >= 0) {
            waterData.push({
              id,
              x,
              y: baseY,
              z,
              sx,
              sy,
              sz,
              phase: x * 0.17 + z * 0.23
            });
          }
        }
      }
    }

    // ------------------------------------------------------------------
    // Harbor structures
    // ------------------------------------------------------------------
    function addBollard(x, z) {
      addVoxel(x, 1, z, C.woodDark);
      addVoxel(x, 2, z, C.deckDark, 1.1, 0.6, 1.1);
    }

    function addCrate(cx, cz) {
      for (let x = cx; x <= cx + 1; x++) {
        for (let z = cz; z <= cz + 1; z++) {
          addVoxel(x, 0, z, C.crate);
          addVoxel(x, 1, z, C.crateDark);
        }
      }
    }

    function addBarrel(cx, cz) {
      for (let x = cx; x <= cx + 1; x++) {
        for (let z = cz; z <= cz + 1; z++) {
          addVoxel(x, 0, z, C.barrel);
          addVoxel(x, 1, z, C.barrel);
          addVoxel(x, 2, z, C.barrelDark);
        }
      }
    }

    function buildQuay() {
      for (let x = DOCK.xMin; x <= DOCK.xMax; x++) {
        for (let z = DOCK.zMin; z <= DOCK.zMax; z++) {
          addVoxel(x, 0, z, ((x + z) & 1) ? C.dock : C.dockDark);
        }
      }

      // Dock pilings
      for (let x = DOCK.xMin; x <= DOCK.xMax; x += 4) {
        for (let z = DOCK.zMin; z <= DOCK.zMax; z += 4) {
          for (let y = -3; y <= -1; y++) {
            addVoxel(x, y, z, C.dockDark);
          }
        }
      }

      // Bollards along quay edge
      for (let x = DOCK.xMin + 2; x <= DOCK.xMax - 2; x += 5) {
        addBollard(x, -3);
      }
    }

    function buildSidePier() {
      for (let x = SIDE_PIER.xMin; x <= SIDE_PIER.xMax; x++) {
        for (let z = SIDE_PIER.zMin; z <= SIDE_PIER.zMax; z++) {
          addVoxel(x, 0, z, ((x + z) & 1) ? C.deck : C.deckDark);
        }
      }

      // Side pier pilings
      for (let x = 20; x <= 27; x += 3) {
        for (let z = -11; z <= 5; z += 3) {
          for (let y = -3; y <= -1; y++) {
            addVoxel(x, y, z, C.dockDark);
          }
        }
      }

      // Bollards on the side pier
      addBollard(20, 6);
      addBollard(21, 6);
      addBollard(26, 6);
      addBollard(27, 6);
    }

    function buildLand() {
      for (let x = LAND.xMin; x <= LAND.xMax; x++) {
        for (let z = LAND.zMin; z <= LAND.zMax; z++) {
          const n = (((x * 5 + z * 7) % 9) + 9) % 9;
          const color = n === 0 ? C.dirt : n < 3 ? C.grassDark : C.grass;
          addVoxel(x, 0, z, color);
        }
      }
    }

    function buildWarehouse() {
      const minX = -36;
      const maxX = -24;
      const minZ = -45;
      const maxZ = -36;

      for (let y = 1; y <= 5; y++) {
        for (let x = minX; x <= maxX; x++) {
          for (let z = minZ; z <= maxZ; z++) {
            const onWall =
              x === minX || x === maxX || z === minZ || z === maxZ;
            if (!onWall) continue;

            let color = C.warehouse;

            // Front windows
            if (
              z === maxZ &&
              y >= 3 &&
              y <= 4 &&
              (x === -35 || x === -33 || x === -27 || x === -25)
            ) {
              color = C.window;
            }

            // Front door
            if (z === maxZ && x >= -31 && x <= -29 && y <= 3) {
              color = C.door;
            }

            addVoxel(x, y, z, color);
          }
        }
      }

      addFill(minX - 1, maxX + 1, 6, 8, minZ - 1, maxZ + 1, C.roof);
    }

    function addTree(x, z) {
      for (let y = 1; y <= 3; y++) {
        addVoxel(x, y, z, C.trunk);
      }

      for (let y = 4; y <= 5; y++) {
        for (let dx = -1; dx <= 1; dx++) {
          for (let dz = -1; dz <= 1; dz++) {
            if (dx === 0 && dz === 0) continue;
            addVoxel(x + dx, y, z + dz, C.leaf);
          }
        }
      }

      addVoxel(x, 6, z, C.leaf);
    }

    function buildTrees() {
      addTree(-42, -43);
      addTree(-40, -47);
      addTree(-18, -46);
    }

    function addLamp(x, z) {
      for (let y = 1; y <= 5; y++) {
        addVoxel(x, y, z, C.woodDark);
      }
      addVoxel(x, 6, z, C.lamp);
    }

    function buildCrane(bx, bz) {
      // Vertical post
      for (let y = 1; y <= 8; y++) {
        addVoxel(bx, y, bz, C.woodDark);
        addVoxel(bx + 1, y, bz, C.woodDark);
      }

      // Jib
      for (let i = 0; i <= 8; i++) {
        const x = bx + 2 + i;
        const y = 8 - Math.floor(i / 2);
        addVoxel(x, y, bz, C.deckDark);
      }

      // Cable and load
      const cableX = bx + 10;
      for (let i = 0; i <= 3; i++) {
        addVoxel(cableX, 4 - i, bz, C.rope, 0.6, 0.6, 0.6);
      }

      addCrate(cableX - 1, bz - 1);
    }

    function buildQuayDetails() {
      const lampSpots = [
        [-37, -33],
        [-29, -18],
        [-21, -11],
        [-13, -32],
        [-5, -14],
        [3, -25],
        [11, -19]
      ];

      for (const [lx, lz] of lampSpots) {
        addLamp(lx, lz);
      }

      addCrate(-38, -29);
      addCrate(-31, -33);
      addCrate(-23, -27);
      addCrate(-17, -15);
      addCrate(-3, -23);
      addCrate(5, -26);
      addCrate(13, -20);

      addBarrel(-36, -24);
      addBarrel(-28, -31);
      addBarrel(-12, -18);
      addBarrel(-8, -34);
      addBarrel(2, -21);
      addBarrel(15, -23);

      buildCrane(-15, -25);
    }

    function buildLighthouse(cx = 23, cz = 4) {
      // Base
      for (let x = cx - 1; x <= cx + 1; x++) {
        for (let z = cz - 1; z <= cz + 1; z++) {
          for (let y = 1; y <= 3; y++) {
            addVoxel(x, y, z, C.stone);
          }
        }
      }

      // Tower
      for (let y = 4; y <= 13; y++) {
        const r = y < 8 ? 2 : y < 11 ? 2 : 1;
        const color =
          Math.floor((y - 4) / 2) % 2 === 0 ? C.white : C.flag;

        for (let x = cx - r; x <= cx + r; x++) {
          for (let z = cz - r; z <= cz + r; z++) {
            const dx = x - cx;
            const dz = z - cz;
            if (dx * dx + dz * dz <= r * r + 0.7) {
              addVoxel(x, y, z, color);
            }
          }
        }
      }

      // Lantern room and cap
      addFill(cx - 1, cx + 1, 14, 15, cz - 1, cz + 1, C.lamp);
      addFill(cx - 1, cx + 1, 16, 16, cz - 1, cz + 1, C.stoneDark);
    }

    // ------------------------------------------------------------------
    // Ship
    // ------------------------------------------------------------------
    function hullHalfWidth(x) {
      const ax = Math.abs(x);
      if (ax <= 12) return 6;
      if (ax <= 16) {
        const t = (ax - 12) / 4;
        return 6 * Math.sqrt(Math.max(0, 1 - t * t));
      }
      return 0;
    }

    function buildSternCabin(cx, cz) {
      for (let x = 10; x <= 15; x++) {
        for (let z = -3; z <= 3; z++) {
          for (let y = 5; y <= 6; y++) {
            let color = C.cabin;

            if (
              (z === 3 || z === -3) &&
              y === 6 &&
              (x === 11 || x === 13 || x === 14)
            ) {
              color = C.window;
            }

            if (x === 15 && y === 5 && z === 0) {
              color = C.door;
            }

            addVoxel(cx + x, y, cz + z, color);
          }
        }
      }

      addFill(cx + 10, cx + 16, 7, 7, cz - 3, cz + 3, C.cabinDark);
    }

    function buildForeCabin(cx, cz) {
      addFill(cx - 15, cx - 11, 5, 6, cz - 2, cz + 2, C.cabinDark);
      addFill(cx - 14, cx - 12, 7, 7, cz - 1, cz + 1, C.deckDark);
    }

    function addRope(x1, y1, z1, x2, y2, z2, color = C.rope, sag = 1, density = 1.15) {
      const dist = Math.hypot(x2 - x1, y2 - y1, z2 - z1);
      const steps = Math.max(2, Math.ceil(dist * density));

      for (let i = 1; i <= steps; i++) {
        const t = i / steps;
        const x = x1 + (x2 - x1) * t;
        const y = y1 + (y2 - y1) * t - sag * Math.sin(Math.PI * t);
        const z = z1 + (z2 - z1) * t;

        addVoxel(x, y, z, color, 0.55, 0.55, 0.55);
      }
    }

    function addSail(cx, cz, mx, y0, y1, halfW) {
      for (let y = y0; y <= y1; y++) {
        for (let z = -halfW; z <= halfW; z++) {
          const billow =
            Math.sin((z + y * 0.45) * 0.55) * 1.8 +
            Math.cos(y * 0.35) * 0.6;

          const x = Math.round(cx + mx + billow);

          let color = C.sail;
          if (Math.abs(z) % 4 === 3 || (y - y0) % 5 === 4) {
            color = C.sailDark;
          }

          addVoxel(x, y, cz + z, color, 1, 1, 0.85);
        }
      }
    }

    function addMastWithSails(cx, cz, mx, topY, yards) {
      for (let y = 5; y <= topY; y++) {
        addVoxel(cx + mx, y, cz, C.mast);
      }

      for (const yard of yards) {
        for (let z = -yard.halfW; z <= yard.halfW; z++) {
          addVoxel(cx + mx, yard.y, cz + z, C.mastDark, 1, 0.8, 0.8);
        }

        addSail(cx, cz, mx, yard.y0, yard.y1, yard.halfW);
      }
    }

    function addShroud(cx, cz, mx, offsetX, yardY, halfW) {
      const side = [-1, 1];
      for (const s of side) {
        addRope(
          cx + mx + offsetX,
          5,
          cz + s * 4,
          cx + mx + offsetX,
          yardY,
          cz + s * halfW,
          C.rope,
          1.3,
          1.15
        );
      }
    }

    function buildMasts(cx, cz) {
      const masts = [
        {
          mx: -8,
          top: 21,
          yards: [{ y: 18, halfW: 6, y0: 12, y1: 17 }]
        },
        {
          mx: 0,
          top: 26,
          yards: [
            { y: 15, halfW: 8, y0: 8, y1: 14 },
            { y: 23, halfW: 6, y0: 17, y1: 22 }
          ]
        },
        {
          mx: 8,
          top: 21,
          yards: [{ y: 18, halfW: 5, y0: 12, y1: 17 }]
        }
      ];

      for (const m of masts) {
        addMastWithSails(cx, cz, m.mx, m.top, m.yards);
      }

      for (const m of masts) {
        for (const yard of m.yards) {
          addShroud(cx, cz, m.mx, 3, yard.y, yard.halfW);
        }
      }
    }

    function buildBowsprit(cx, cz) {
      for (let i = 0; i <= 4; i++) {
        addVoxel(cx + 16 + i, 5, cz, C.mastDark);
      }

      // Small bowsprit tip detail
      addVoxel(cx + 20, 4, cz, C.deckDark);
    }

    function buildShipDetails(cx, cz) {
      // Deck cargo
      addVoxel(cx - 4, 5, cz + 3, C.crate);
      addVoxel(cx + 6, 5, cz - 3, C.barrel);
      addVoxel(cx + 8, 5, cz + 4, C.crate);
      addVoxel(cx - 8, 5, cz - 4, C.barrel);

      // Stern lantern
      addVoxel(cx - 16, 7, cz, C.window);
      addVoxel(cx - 16, 8, cz, C.window, 0.8, 0.8, 0.8);
    }

    function buildShipFoam(cx, cz) {
      for (let x = -16; x <= 16; x++) {
        const hwRaw = hullHalfWidth(x);
        const side = Math.round(hwRaw);
        if (side < 1) continue;

        const z1 = side + 1;
        const z2 = -side - 1;

        addVoxel(cx + x, -0.15, cz + z1, C.foam, 1, 0.7, 1);
        addVoxel(cx + x, -0.15, cz + z2, C.foam, 1, 0.7, 1);
      }

      // Bow/stern foam
      addVoxel(cx + 16, -0.15, cz, C.foam, 1, 0.7, 1);
      addVoxel(cx - 16, -0.15, cz, C.foam, 1, 0.7, 1);
    }

    function buildShip(cx, cz) {
      // Hull shell/solid voxel body
      for (let x = -16; x <= 16; x++) {
        const hwRaw = hullHalfWidth(x);
        const hwInt = Math.round(hwRaw);

        for (let y = 0; y <= 3; y++) {
          const taper = 1 - y * 0.12;
          const side = Math.max(0, Math.round(hwRaw * taper));

          if (side === 0) {
            if (y === 0) addVoxel(cx + x, y, cz, C.hullDark);
            continue;
          }

          for (let z = -side; z <= side; z++) {
            const boundary = z === -side || z === side;
            let color;

            if (y === 0) {
              color = C.hullDark;
            } else if (y === 1) {
              color = boundary ? C.hullDark : C.hull;
            } else if (y === 2) {
              color = boundary ? C.hullStripe : C.hull;
            } else {
              color = boundary ? C.hullDark : C.hull;
            }

            addVoxel(cx + x, y, cz + z, color);
          }
        }

        // Deck
        const sideDeck = Math.max(0, Math.round(hwRaw * 0.95));
        if (sideDeck === 0) {
          addVoxel(cx + x, 4, cz, C.deck);
        } else {
          for (let z = -sideDeck; z <= sideDeck; z++) {
            addVoxel(cx + x, 4, cz + z, C.deck);
          }
        }

        // Bulwark / rail
        const sideRail = hwInt;
        if (sideRail > 0) {
          for (let z = -sideRail; z <= sideRail; z++) {
            if (z === -sideRail || z === sideRail) {
              addVoxel(cx + x, 5, cz + z, C.deckDark);
            }
          }
        }

        if (Math.abs(x) >= 15) {
          addVoxel(cx + x, 4, cz, C.deckDark);
        }
      }

      buildSternCabin(cx, cz);
      buildForeCabin(cx, cz);
      buildMasts(cx, cz);
      buildFlag(cx, cz);
      buildBowsprit(cx, cz);
      buildShipDetails(cx, cz);
      buildShipFoam(cx, cz);
    }

    function buildMooringLines() {
      const xs = [-12, -5, 1, 7, 12];

      for (const x of xs) {
        addRope(x, 2.25, -3.35, x, 2.45, -2.15, C.rope, 0.25, 1.65);
      }
    }

    // ------------------------------------------------------------------
    // Dynamic extras
    // ------------------------------------------------------------------
    const dynamicFlags = [];
    const dynamicBirds = [];

    function addCloud(cx, cz, y) {
      for (let dx = -3; dx <= 3; dx++) {
        for (let dz = -2; dz <= 2; dz++) {
          if (Math.abs(dx) + Math.abs(dz) < 5) {
            addVoxel(cx + dx, y, cz + dz, C.white, 1.1, 1.1, 1.1);
          }
        }
      }
    }

    function buildClouds() {
      addCloud(-28, 44, 28);
      addCloud(4, 47, 32);
      addCloud(30, 38, 26);
    }

    function addFlag(cx, cz) {
      for (let i = 0; i < 4; i++) {
        const z = cz + 1 + i;

        const idTop = addVoxel(cx, 24, z, C.flag);
        if (idTop >= 0) {
          dynamicFlags.push({
            id: idTop,
            x: cx,
            y: 24,
            z,
            phase: i * 0.9
          });
        }

        const idBottom = addVoxel(cx, 23, z, C.flagDark);
        if (idBottom >= 0) {
          dynamicFlags.push({
            id: idBottom,
            x: cx,
            y: 23,
            z,
            phase: i * 0.9 + 0.5
          });
        }
      }
    }

    function addBird(cx, cz, radius, speed, phase) {
      const ids = [
        addVoxel(cx, 18, cz, C.white, 1, 1, 1),
        addVoxel(cx - 1, 18, cz, C.white, 2, 0.4, 1),
        addVoxel(cx + 1, 18, cz, C.white, 2, 0.4, 1)
      ];

      if (ids[0] >= 0 && ids[1] >= 0 && ids[2] >= 0) {
        dynamicBirds.push({
          ids,
          cx,
          cz,
          radius,
          speed,
          phase
        });
      }
    }

    function buildBirds() {
      addBird(10, 35, 12, 0.35, 0.0);
      addBird(-18, 25, 10, 0.42, 2.1);
      addBird(28, 18, 14, 0.30, 4.2);
      addBird(-8, 55, 11, 0.38, 1.0);
    }

    // ------------------------------------------------------------------
    // Beacon glow
    // ------------------------------------------------------------------
    const beacon = new THREE.Mesh(
      new THREE.BoxGeometry(1.5, 1.5, 1.5),
      new THREE.MeshBasicMaterial({ color: 0xfff6bb })
    );
    beacon.position.set(23, 14.7, 4);
    scene.add(beacon);

    const halo = new THREE.Mesh(
      new THREE.BoxGeometry(3.2, 3.2, 3.2),
      new THREE.MeshBasicMaterial({
        color: 0xfff6bb,
        transparent: true,
        opacity: 0.18,
        depthWrite: false
      })
    );
    halo.position.copy(beacon.position);
    scene.add(halo);

    // ------------------------------------------------------------------
    // Build scene
    // ------------------------------------------------------------------
    buildWater();
    buildQuay();
    buildSidePier();
    buildLand();
    buildWarehouse();
    buildTrees();
    buildQuayDetails();
    buildLighthouse();
    buildShip(shipX, shipZ);
    buildMooringLines();
    buildClouds();
    buildBirds();

    voxels.count = voxelCount;
    voxels.instanceMatrix.needsUpdate = true;
    if (voxels.instanceColor) {
      voxels.instanceColor.needsUpdate = true;
    }

    // ------------------------------------------------------------------
    // Update dynamic voxels
    // ------------------------------------------------------------------
    function updateWater(t) {
      for (const d of waterData) {
        dummy.rotation.set(0, 0, 0);
        dummy.position.set(
          d.x,
          d.y + Math.sin(t * 1.15 + d.phase) * 0.24,
          d.z
        );
        dummy.scale.set(d.sx, d.sy, d.sz);
        dummy.updateMatrix();
        voxels.setMatrixAt(d.id, dummy.matrix);
      }
    }

    function updateFlags(t) {
      for (const f of dynamicFlags) {
        dummy.rotation.set(0, 0, 0);
        dummy.position.set(
          f.x,
          f.y + Math.sin(t * 7 + f.phase) * 0.25,
          f.z + Math.sin(t * 5 + f.phase) * 0.35
        );
        dummy.scale.set(1, 1, 1);
        dummy.updateMatrix();
        voxels.setMatrixAt(f.id, dummy.matrix);
      }
    }

    function updateBirds(t) {
      for (const b of dynamicBirds) {
        const angle = t * b.speed + b.phase;
        const x = b.cx + Math.cos(angle) * b.radius;
        const z = b.cz + Math.sin(angle) * b.radius;
        const y = 18 + Math.sin(t * 0.45 + b.phase) * 1.2;
        const flap = Math.sin(t * 9 + b.phase) * 0.7;

        dummy.rotation.set(0, 0, 0);

        // Body
        dummy.position.set(x, y, z);
        dummy.scale.set(1, 1, 1);
        dummy.updateMatrix();
        voxels.setMatrixAt(b.ids[0], dummy.matrix);

        // Left wing
        dummy.position.set(x - 1.7, y + flap, z);
        dummy.scale.set(2.4, 0.4, 1.1);
        dummy.updateMatrix();
        voxels.setMatrixAt(b.ids[1], dummy.matrix);

        // Right wing
        dummy.position.set(x + 1.7, y + flap, z);
        dummy.scale.set(2.4, 0.4, 1.1);
        dummy.updateMatrix();
        voxels.setMatrixAt(b.ids[2], dummy.matrix);
      }
    }

    // ------------------------------------------------------------------
    // Animation loop
    // ------------------------------------------------------------------
    function animate() {
      requestAnimationFrame(animate);

      const t = performance.now() * 0.001;

      updateWater(t);
      updateFlags(t);
      updateBirds(t);

      const pulse = Math.sin(t * 4);
      const beaconScale = 1.25 + pulse * 0.3;
      beacon.scale.set(beaconScale, beaconScale, beaconScale);

      halo.scale.set(
        1.8 + pulse * 0.25,
        1.8 + pulse * 0.25,
        1.8 + pulse * 0.25
      );
      halo.material.opacity = 0.16 + pulse * 0.08;

      controls.update();
      voxels.instanceMatrix.needsUpdate = true;

      renderer.render(scene, camera);
    }

    animate();

    // ------------------------------------------------------------------
    // Resize handling and UI hint fade
    // ------------------------------------------------------------------
    window.addEventListener("resize", () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    });

    setTimeout(() => {
      const hint = document.getElementById("hint");
      if (hint) hint.style.opacity = "0";
    }, 7000);
  </script>
</body>
</html>
```