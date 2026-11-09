```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Voxel Art: A Sailing Ship Calling at a Harbor</title>
  <style>
    html, body {
      margin: 0;
      height: 100%;
      overflow: hidden;
      background: #87ceeb;
      font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
    }
    #info {
      position: fixed;
      left: 14px;
      bottom: 14px;
      color: #fff;
      background: rgba(0, 0, 0, 0.38);
      padding: 9px 12px;
      border-radius: 10px;
      font-size: 13px;
      pointer-events: none;
      text-shadow: 0 1px 2px rgba(0,0,0,.45);
      max-width: 420px;
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
  <div id="info">
    <b>A sailing ship calling at a harbor</b><br />
    Drag mouse to orbit · scroll to zoom · right-drag to pan
  </div>

  <script type="module">
    import * as THREE from 'three';
    import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x9bd6f7);
    scene.fog = new THREE.Fog(0x9bd6f7, 70, 180);

    const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 600);
    camera.position.set(30, 22, 36);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.target.set(0, 5, 0);
    controls.enableDamping = true;
    controls.dampingFactor = 0.06;
    controls.autoRotate = true;
    controls.autoRotateSpeed = 0.45;
    controls.maxPolarAngle = Math.PI / 2 - 0.02;
    controls.minDistance = 9;
    controls.maxDistance = 150;

    scene.add(new THREE.HemisphereLight(0xd7f0ff, 0x26303a, 0.78));
    const sunLight = new THREE.DirectionalLight(0xfff2c8, 0.95);
    sunLight.position.set(80, 70, -45);
    scene.add(sunLight);
    scene.add(new THREE.AmbientLight(0xffffff, 0.22));

    // ---- Voxel builder -------------------------------------------------------
    const voxelList = [];

    function addVoxel(x, y, z, color, sx = 1, sy = 1, sz = 1) {
      voxelList.push({ x, y, z, color, sx, sy, sz });
    }

    function buildVoxels(list, material) {
      if (!list.length) return new THREE.Object3D();

      const geo = new THREE.BoxGeometry(1, 1, 1);
      const mat = material || new THREE.MeshLambertMaterial({ color: 0xffffff, flatShading: true });
      const mesh = new THREE.InstancedMesh(geo, mat, list.length);

      const dummy = new THREE.Object3D();
      const color = new THREE.Color();

      for (let i = 0; i < list.length; i++) {
        const v = list[i];
        dummy.position.set(v.x, v.y, v.z);
        dummy.scale.set(v.sx, v.sy, v.sz);
        dummy.updateMatrix();
        mesh.setMatrixAt(i, dummy.matrix);
        mesh.setColorAt(i, color.set(v.color));
      }

      mesh.instanceMatrix.needsUpdate = true;
      if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
      return mesh;
    }

    function addRect(x0, z0, x1, z1, y0, y1, color) {
      const xs = Math.min(x0, x1), xe = Math.max(x0, x1);
      const zs = Math.min(z0, z1), ze = Math.max(z0, z1);
      const ys = Math.min(y0, y1), ye = Math.max(y0, y1);
      for (let x = xs; x <= xe; x++) {
        for (let z = zs; z <= ze; z++) {
          for (let y = ys; y <= ye; y++) {
            addVoxel(x, y, z, color);
          }
        }
      }
    }

    // ---- Terrain / coastline -------------------------------------------------
    const sand = 0xe0c07b;
    const grass = 0x59b04b;
    const darkGrass = 0x4a9a40;
    const stone = 0x9c9c9c;
    const darkStone = 0x777777;
    const wood = 0x8b5a2b;
    const darkWood = 0x6b4b2a;
    const sail = 0xf8f1e0;
    const mast = 0xa67c52;
    const rope = 0x2f2f2f;

    function shoreX(z) {
      let s = 8 + 2.0 * Math.sin(z * 0.18) + 1.3 * Math.sin(z * 0.31 + 1.7);
      if (z > 22) s += (z - 22) * 0.4;
      if (z < -22) s += (-z - 22) * 0.4;
      return s;
    }

    function isLand(x, z) {
      const s = shoreX(z);
      if (x >= s) return true;

      // Harbor jetties
      if (z >= 24 && z <= 38 && x >= 5 && x <= 12) return true;
      if (z >= -38 && z <= -24 && x >= 5 && x <= 12) return true;

      return false;
    }

    function terrainHeight(x, z) {
      if (!isLand(x, z)) return 0;

      // Keep harbor structures flat.
      if (z >= 24 && z <= 38 && x >= 5 && x <= 12) return 1;
      if (z >= -38 && z <= -24 && x >= 5 && x <= 12) return 1;

      const s = shoreX(z);
      const inland = Math.max(0, x - s);

      let h = 1 + Math.floor(inland * 0.16);
      h += Math.round(Math.max(0, Math.sin(z * 0.17 + x * 0.08) * 1.7 + Math.cos(z * 0.11) * 1.2));
      if (z > 20) h += Math.floor((z - 20) * 0.28);
      if (z < -20) h += Math.floor((-z - 20) * 0.28);
      if (x > 28) h += Math.floor((x - 28) * 0.14);

      return Math.min(11, Math.max(1, h));
    }

    // Terrain
    for (let x = -55; x <= 55; x++) {
      for (let z = -55; z <= 55; z++) {
        if (!isLand(x, z)) continue;

        const h = terrainHeight(x, z);
        const distToShore = x - shoreX(z);

        for (let y = 0; y < h; y++) {
          let col;
          if (y === h - 1) {
            if (h >= 5) col = stone;
            else if (distToShore < 2.5) col = distToShore < 1 ? sand : grass;
            else col = grass;
          } else {
            col = (y < 1 && distToShore < 2.5) ? sand : 0x704a2a;
          }
          addVoxel(x, y, z, col);
        }
      }
    }

    // ---- Harbor works --------------------------------------------------------
    // Main quay
    addRect(7, -18, 9, 18, 0, 0, 0x9b9b9b);
    addRect(10, -18, 12, 18, 0, 0, 0x9b9b9b);

    // North jetty
    addRect(6, 24, 11, 38, 0, 0, 0x8f8f8f);

    // South pier
    addRect(6, -38, 11, -24, 0, 0, 0x8f8f8f);

    // ---- Buildings -----------------------------------------------------------
    function addBuilding(bx, bz, w, d, h, wall, roof, windowColor = 0xffd856) {
      const baseY = terrainHeight(bx, bz) - 1;
      const x0 = Math.floor(bx - w / 2);
      const x1 = Math.floor(bx + w / 2);
      const z0 = Math.floor(bz - d / 2);
      const z1 = Math.floor(bz + d / 2);

      for (let y = baseY + 1; y <= baseY + h; y++) {
        for (let x = x0; x <= x1; x++) {
          for (let z = z0; z <= z1; z++) {
            const onPerim = (x === x0 || x === x1 || z === z0 || z === z1);
            let col = onPerim ? wall : 0x303030;

            if (
              onPerim &&
              (y === baseY + 2 || y === baseY + 3) &&
              (
                ((z === z0 || z === z1) && (x % 2 === 0)) ||
                ((x === x0 || x === x1) && (z % 2 === 0))
              )
            ) {
              col = windowColor;
            }

            if (y === baseY + 1 && z === z0 && x === Math.floor(bx)) {
              col = 0x4a2a12;
            }

            addVoxel(x, y, z, col);
          }
        }
      }

      const roofH = Math.max(1, Math.floor(d / 2));
      for (let k = 0; k <= roofH; k++) {
        const y = baseY + h + 1 + k;
        const xs = x0 + k;
        const xe = x1 - k;
        const zs = z0 + k;
        const ze = z1 - k;
        if (xs <= xe && zs <= ze) {
          addRect(xs, zs, xe, ze, y, y, roof);
        }
      }
    }

    addBuilding(17, -8, 8, 7, 4, 0xb5651d, 0x5d4037);
    addBuilding(17, 1, 8, 7, 3, 0x8c9aa6, 0x7d3c2c);
    addBuilding(17, 10, 8, 7, 5, 0xc19a6b, 0x455a64);
    addBuilding(26, -1, 7, 7, 3, 0xa87548, 0x37474f);

    // ---- Lighthouse ----------------------------------------------------------
    function addLighthouse(x, z) {
      addRect(x - 3, z - 3, x + 3, z + 3, 0, 0, 0x9b9b9b);

      for (let y = 1; y <= 14; y++) {
        const radius = Math.max(1, Math.round(2.1 - (y > 10 ? (y - 10) * 0.12 : 0)));
        for (let dx = -radius; dx <= radius; dx++) {
          for (let dz = -radius; dz <= radius; dz++) {
            if (dx * dx + dz * dz <= radius * radius + 0.2) {
              const stripe = Math.floor(y / 2) % 2;
              addVoxel(x + dx, y, z + dz, stripe ? 0xd03a2e : 0xf7f7f7);
            }
          }
        }
      }

      addRect(x - 2, z - 2, x + 2, z + 2, 15, 15, 0x333333);
      for (let dx = -1; dx <= 1; dx++) {
        for (let dz = -1; dz <= 1; dz++) {
          addVoxel(x + dx, 16, z + dz, 0xffe066);
        }
      }
      addRect(x - 2, z - 2, x + 2, z + 2, 17, 17, 0x333333);

      for (let r = 2; r >= 0; r--) {
        const y = 18 + (2 - r);
        addRect(x - r, z - r, x + r, z + r, y, y, 0x455a64);
      }
    }

    addLighthouse(8, 31);

    // ---- Cranes --------------------------------------------------------------
    function addCrane(x, z, dir = -1) {
      for (let y = 1; y <= 6; y++) addVoxel(x, y, z, 0x8b5a2b);

      for (let i = 1; i <= 7; i++) addVoxel(x + dir * i, 6, z, 0xa67c52);
      for (let i = 1; i <= 4; i++) addVoxel(x + dir * i, 5, z, 0x8b5a2b);

      for (let y = 1; y <= 3; y++) {
        addVoxel(x, y, z - 1, 0x8b5a2b);
        addVoxel(x, y, z + 1, 0x8b5a2b);
      }

      for (let y = 5; y >= 2; y--) addVoxel(x + dir * 5, y, z, rope);

      const bx = x + dir * 5;
      addVoxel(bx, 1, z, 0x8b5a2b);
      addVoxel(bx + 1, 1, z, 0x8b5a2b);
      addVoxel(bx, 2, z, 0x8b5a2b);
      addVoxel(bx + 1, 2, z, 0x8b5a2b);
    }

    addCrane(8, 12, -1);
    addCrane(8, -6, -1);

    // ---- Cargo / small boats -------------------------------------------------
    function addQuayCrate(x, z) {
      const y = 1;
      addVoxel(x, y, z, 0xb08048);
      addVoxel(x + 1, y, z, 0xb08048);
      addVoxel(x, y, z + 1, 0xb08048);
      addVoxel(x + 1, y, z + 1, 0xb08048);

      const y2 = 2;
      addVoxel(x, y2, z, 0x8b5a2b);
      addVoxel(x + 1, y2, z, 0x8b5a2b);
      addVoxel(x, y2, z + 1, 0x8b5a2b);
      addVoxel(x + 1, y2, z + 1, 0x8b5a2b);
    }

    addQuayCrate(10, 4);
    addQuayCrate(11, -3);
    addQuayCrate(10, -10);

    for (let z = -34; z <= -28; z += 3) {
      addQuayCrate(9, z);
      addQuayCrate(11, z);
    }

    function addRowboat(x, z, oy = 0.5) {
      for (let dx = -1; dx <= 1; dx++) {
        for (let dz = -2; dz <= 2; dz++) {
          const r = Math.abs(dx) + Math.abs(dz);
          if (r <= 2) addVoxel(x + dx, oy, z + dz, 0x7b4a24);
          if (r <= 1) addVoxel(x + dx, oy, z + dz, 0x4a2a12);
        }
      }
      addVoxel(x + 2, oy + 0.1, z, 0x333333);
    }

    addRowboat(4, 6);
    addRowboat(4, -4);
    addRowboat(4, -20);

    // ---- Sailing ship --------------------------------------------------------
    function hullHalf(z) {
      return Math.max(0, Math.round(4.6 * (1 - Math.pow(Math.abs(z) / 13, 1.55)) + 0.3));
    }

    function hullH(z) {
      return Math.max(1, Math.round(4.2 * (1 - Math.pow(Math.abs(z) / 14, 2.0)) + 0.6));
    }

    function lineVoxel(x1, y1, z1, x2, y2, z2, color) {
      if (x1 === x2 && y1 === y2 && z1 === z2) {
        addVoxel(Math.round(x1), Math.round(y1), Math.round(z1), color);
        return;
      }

      const steps = Math.max(
        1,
        Math.ceil(Math.max(Math.abs(x2 - x1), Math.abs(y2 - y1), Math.abs(z2 - z1)) * 2)
      );

      for (let i = 0; i <= steps; i++) {
        const t = i / steps;
        addVoxel(
          Math.round(x1 + (x2 - x1) * t),
          Math.round(y1 + (y2 - y1) * t),
          Math.round(z1 + (z2 - z1) * t),
          color
        );
      }
    }

    function addBarrel(x, y, z) {
      for (let dx = 0; dx <= 1; dx++) {
        for (let dz = 0; dz <= 1; dz++) {
          addVoxel(x + dx, y, z + dz, 0x7b4a24);
          addVoxel(x + dx, y + 1, z + dz, 0x7b4a24);
        }
      }
      addVoxel(x, y + 2, z, 0x4a2a12);
      addVoxel(x + 1, y + 2, z, 0x4a2a12);
      addVoxel(x, y + 2, z + 1, 0x4a2a12);
      addVoxel(x + 1, y + 2, z + 1, 0x4a2a12);
    }

    function addCrateShip(x, y, z) {
      for (let dx = 0; dx <= 1; dx++) {
        for (let dz = 0; dz <= 1; dz++) {
          addVoxel(x + dx, y, z + dz, 0xb08048);
          addVoxel(x + dx, y + 1, z + dz, 0xb08048);
        }
      }
    }

    function buildShip(ox, oz, oy, flagColor) {
      const masts = [
        { z: -7, h: 14, yStart: 6, step: 3, ys: [2, 3, 4] },
        { z: 0, h: 18, yStart: 7, step: 4, ys: [4, 6, 7] },
        { z: 7, h: 13, yStart: 6, step: 3, ys: [2, 4, 4] }
      ];

      // Bowsprit
      for (let i = 0; i <= 5; i++) {
        addVoxel(ox, oy + 4, oz + 12 + i, mast);
      }

      // Jibs
      for (let z = 9; z <= 13; z++) {
        const yy = oy + 7 - (z - 8);
        if (yy > oy + 3) {
          for (let x = -1; x <= 1; x++) addVoxel(ox + x, yy, oz + z, sail);
        }
      }

      for (let z = 11; z <= 15; z++) {
        const yy = oy + 10 - (z - 9);
        if (yy > oy + 4) {
          for (let x = -1; x <= 1; x++) addVoxel(ox + x, yy, oz + z, sail);
        }
      }

      // Hull
      for (let z = -12; z <= 12; z++) {
        const half = hullHalf(z);
        const h = hullH(z);

        for (let y = 0; y < h; y++) {
          for (let x = -half; x <= half; x++) {
            let col;
            if (y === 0) col = 0x8b2e2e;
            else if (y === 1) col = 0x9c3636;
            else if (y === h - 1) col = 0x6b4b2a;
            else if (x === -half || x === half) col = 0x8b5a2b;
            else col = 0x75503a;

            addVoxel(ox + x, oy + y, oz + z, col);
          }
        }

        // Deck
        const dh = Math.max(0, half - 1);
        for (let x = -dh; x <= dh; x++) {
          addVoxel(ox + x, oy + h, oz + z, 0xc99a5c);
        }

        // Gun ports
        if (h >= 3 && Math.abs(z) % 2 === 0 && Math.abs(z) < 11) {
          addVoxel(ox + half, oy + 2, oz + z, 0x222222);
          addVoxel(ox - half, oy + 2, oz + z, 0x222222);
        }
      }

      // Sterncastle
      for (let z = -9; z <= -5; z++) {
        const h = hullH(z);
        for (let x = -3; x <= 3; x++) {
          addVoxel(ox + x, oy + h, oz + z, 0x9c6b3f);
          addVoxel(ox + x, oy + h + 1, oz + z, 0x9c6b3f);
          addVoxel(ox + x, oy + h + 2, oz + z, 0x6b4b2a);

          if (Math.abs(x) === 3) {
            addVoxel(ox + x, oy + h, oz + z, 0xffe066);
          }
          if (z === -5 && Math.abs(x) <= 2) {
            addVoxel(ox + x, oy + h, oz + z, 0xffe066);
          }
        }
      }

      // Forecastle
      for (let z = 8; z <= 11; z++) {
        const h = hullH(z);
        for (let x = -2; x <= 2; x++) {
          addVoxel(ox + x, oy + h, oz + z, 0x8b5a2b);
          addVoxel(ox + x, oy + h + 1, oz + z, 0x8b5a2b);
          addVoxel(ox + x, oy + h + 2, oz + z, 0x5a3a1f);
        }
      }

      // Masts, yards, sails, rigging
      for (const m of masts) {
        const baseY = oy + hullH(m.z) + 1;

        for (let y = baseY; y <= oy + m.h; y++) {
          addVoxel(ox, y, oz + m.z, mast);
        }

        m.ys.forEach((w, idx) => {
          const yy = oy + m.yStart + idx * m.step;

          for (let x = -w; x <= w; x++) {
            addVoxel(ox + x, yy, oz + m.z, 0x8b5a2b);
          }

          for (let y = yy - 3; y <= yy - 1; y++) {
            for (let x = -w + 1; x <= w - 1; x++) {
              addVoxel(ox + x, y, oz + m.z, sail);
              addVoxel(ox + x, y, oz + m.z + 1, sail);
            }
          }
        });

        const topY = oy + m.h - 2;
        addRect(ox - 1, oz + m.z - 1, ox + 1, oz + m.z + 1, topY, topY, 0x8b5a2b);

        const sideX = Math.max(1, hullHalf(m.z) - 1);

        lineVoxel(ox + sideX, oy + hullH(m.z), oz + m.z, ox, oy + m.h - 3, oz + m.z, rope);
        lineVoxel(ox - sideX, oy + hullH(m.z), oz + m.z, ox, oy + m.h - 3, oz + m.z, rope);
        lineVoxel(ox + sideX, oy + hullH(m.z), oz + m.z, ox, oy + 10, oz + m.z, rope);
        lineVoxel(ox - sideX, oy + hullH(m.z), oz + m.z, ox, oy + 10, oz + m.z, rope);

        for (let x = 1; x <= 2; x++) {
          addVoxel(ox + x, oy + m.h + 1, oz + m.z, flagColor);
        }
        addVoxel(ox, oy + m.h + 2, oz + m.z, 0x222222);
      }

      // Bow rigging
      lineVoxel(ox, oy + masts[2].h, oz + masts[2].z, ox, oy + 4, oz + 17, rope);

      // Ensign
      for (let x = 2; x <= 4; x++) {
        addVoxel(ox + x, oy + 6, oz - 12, 0x1565c0);
      }

      // Deck cargo
      addBarrel(ox - 2, oy + hullH(-2) + 1, oz - 2);
      addBarrel(ox - 2, oy + hullH(3) + 1, oz + 3);
      addCrateShip(ox + 1, oy + hullH(-5) + 1, oz - 4);
      addCrateShip(ox + 1, oy + hullH(5) + 1, oz + 5);
    }

    buildShip(-3, 0, 0.6, 0xe53935);

    // ---- Trees ---------------------------------------------------------------
    function hash(x, z) {
      const n = Math.sin(x * 12.9898 + z * 78.233) * 43758.5453;
      return n - Math.floor(n);
    }

    function inBuildingArea(x, z) {
      return x >= 13 && x <= 30 && z >= -15 && z <= 15;
    }

    function inLighthouseArea(x, z) {
      return x >= 3 && x <= 13 && z >= 24 && z <= 38;
    }

    function inSouthPierArea(x, z) {
      return x >= 3 && x <= 13 && z >= -38 && z <= -24;
    }

    function addTree(x, z, baseY) {
      for (let y = baseY + 1; y <= baseY + 2; y++) {
        addVoxel(x, y, z, 0x7b4a24);
      }

      for (let y = baseY + 3; y <= baseY + 4; y++) {
        for (let dx = -2; dx <= 2; dx++) {
          for (let dz = -2; dz <= 2; dz++) {
            const r = dx * dx + dz * dz;
            if (r <= 5) {
              addVoxel(x + dx, y, z + dz, r <= 2 ? 0x5fb050 : darkGrass);
            }
          }
        }
      }

      addVoxel(x, baseY + 5, z, 0x66bb55);
      addVoxel(x + 1, baseY + 5, z, 0x66bb55);
      addVoxel(x - 1, baseY + 5, z, 0x66bb55);
      addVoxel(x, baseY + 5, z + 1, 0x66bb55);
      addVoxel(x, baseY + 5, z - 1, 0x66bb55);
    }

    for (let x = 14; x <= 54; x += 2) {
      for (let z = -46; z <= 46; z += 2) {
        if (!isLand(x, z)) continue;
        const h = terrainHeight(x, z);
        if (
          h >= 1 &&
          hash(x, z) < 0.12 &&
          !inBuildingArea(x, z) &&
          !inLighthouseArea(x, z) &&
          !inSouthPierArea(x, z)
        ) {
          addTree(x, z, h - 1);
        }
      }
    }

    // ---- Harbor lamps --------------------------------------------------------
    function addLamp(x, z) {
      addVoxel(x, 0, z, stone);
      for (let y = 1; y <= 3; y++) addVoxel(x, y, z, 0x8b5a2b);

      addVoxel(x, 4, z, 0x222222);
      addVoxel(x + 1, 4, z, 0x222222);
      addVoxel(x, 4, z + 1, 0x222222);
      addVoxel(x, 4, z - 1, 0x222222);
      addVoxel(x, 4, z, 0xffe066);
    }

    addLamp(8, 16);
    addLamp(8, 0);
    addLamp(8, -14);

    // ---- Clouds --------------------------------------------------------------
    function addCloud(cx, cy, cz, s) {
      const n = 170 + s * 28;
      for (let i = 0; i < n; i++) {
        const x = cx + (Math.random() - 0.5) * s;
        const y = cy + (Math.random() - 0.5) * Math.min(6, s * 0.35);
        const z = cz + (Math.random() - 0.5) * s * 0.7;

        const dist = Math.hypot((x - cx) / s, (z - cz) / (s * 0.7));
        if (dist > 1 || Math.random() < 0.25) continue;

        addVoxel(
          Math.round(x),
          Math.round(y),
          Math.round(z),
          Math.random() < 0.22 ? 0xf4f4f4 : 0xffffff,
          1 + Math.random() * 0.7,
          1,
          1 + Math.random() * 0.7
        );
      }
    }

    for (let i = 0; i < 10; i++) {
      addCloud(
        -40 + Math.random() * 70,
        26 + Math.random() * 8,
        -35 + Math.random() * 70,
        10 + Math.random() * 12
      );
    }

    // ---- Static voxel world --------------------------------------------------
    scene.add(buildVoxels(voxelList));

    // ---- Animated water ------------------------------------------------------
    const waterList = [];
    const waterData = [];

    for (let x = -55; x <= 55; x++) {
      for (let z = -55; z <= 55; z++) {
        if (isLand(x, z)) continue;

        const s = shoreX(z);
        const dist = Math.min(Math.abs(x - s), 22);

        let col;
        if (x < -12) col = 0x1d5f91;
        else if (dist < 3) col = 0x3586c7;
        else col = 0x2c7fb8;

        if (Math.abs(x - s) < 1.8 && x < s) col = 0x7fc7e6;

        waterList.push({ x, y: -0.5, z, color: col, sx: 1, sy: 1, sz: 1 });
        waterData.push({ x, z, baseY: -0.5 });
      }
    }

    const waterMaterial = new THREE.MeshLambertMaterial({ color: 0xffffff, flatShading: true });
    const waterMesh = buildVoxels(waterList, waterMaterial);
    scene.add(waterMesh);

    // ---- Sun -----------------------------------------------------------------
    const sun = new THREE.Mesh(
      new THREE.SphereGeometry(6, 16, 12),
      new THREE.MeshBasicMaterial({ color: 0xffdf6b, fog: false })
    );
    sun.position.set(90, 75, -45);
    scene.add(sun);

    // ---- Animation loop ------------------------------------------------------
    const clock = new THREE.Clock();
    const dummy = new THREE.Object3D();

    function animate() {
      requestAnimationFrame(animate);

      const t = clock.getElapsedTime();

      for (let i = 0; i < waterData.length; i++) {
        const d = waterData[i];

        const y =
          d.baseY +
          Math.sin(t * 1.1 + d.x * 0.18 + d.z * 0.13) * 0.18 +
          Math.sin(t * 0.65 + d.z * 0.21) * 0.09 +
          Math.cos(t * 0.9 + d.x * 0.12) * 0.05;

        dummy.position.set(d.x, y, d.z);
        dummy.scale.set(1, 1, 1);
        dummy.updateMatrix();
        waterMesh.setMatrixAt(i, dummy.matrix);
      }

      waterMesh.instanceMatrix.needsUpdate = true;

      controls.update();
      renderer.render(scene, camera);
    }

    animate();

    window.addEventListener('resize', () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    });
  </script>
</body>
</html>
```