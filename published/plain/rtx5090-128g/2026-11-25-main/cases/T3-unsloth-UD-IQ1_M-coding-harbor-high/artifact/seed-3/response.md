```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>A Sailing Ship Calling at a Harbor — Voxel Art</title>
  <style>
    html, body { height: 100%; margin: 0; }
    body { overflow: hidden; background: #000; }
    canvas { display: block; }
    #ui {
      position: fixed;
      left: 14px;
      top: 14px;
      color: #fff;
      font: 500 14px/1.35 system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
      background: rgba(10, 20, 40, 0.50);
      padding: 10px 12px;
      border-radius: 10px;
      pointer-events: none;
      backdrop-filter: blur(4px);
      text-shadow: 0 1px 2px rgba(0,0,0,.35);
    }
    #ui b { font-size: 16px; display: block; margin-bottom: 4px; }
  </style>
</head>
<body>
  <div id="ui">
    <b>A sailing ship calling at a harbor</b>
    Drag to orbit • Scroll to zoom • Right-drag to pan
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

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x8fd3ff);
    scene.fog = new THREE.Fog(0x8fd3ff, 55, 185);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    document.body.appendChild(renderer.domElement);

    const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 500);
    camera.position.set(-62, 36, 58);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.target.set(4, 11, 0);
    controls.enableDamping = true;
    controls.dampingFactor = 0.06;
    controls.minDistance = 18;
    controls.maxDistance = 180;
    controls.maxPolarAngle = Math.PI * 0.495;
    controls.update();

    const hemi = new THREE.HemisphereLight(0xd8f4ff, 0x203040, 0.75);
    scene.add(hemi);

    const sun = new THREE.DirectionalLight(0xfff2d0, 1.45);
    sun.position.set(65, 95, -35);
    sun.castShadow = true;
    sun.shadow.mapSize.set(1024, 1024);
    sun.shadow.camera.near = 1;
    sun.shadow.camera.far = 350;
    sun.shadow.camera.left = -110;
    sun.shadow.camera.right = 110;
    sun.shadow.camera.top = 110;
    sun.shadow.camera.bottom = -110;
    sun.shadow.bias = -0.0005;
    scene.add(sun);

    const voxelGeo = new THREE.BoxGeometry(0.98, 0.98, 0.98);

    class VoxelBuilder {
      constructor() {
        this.groups = new Map();
      }

      add(x, y, z, color, opts = {}) {
        x = Math.round(x);
        y = Math.round(y);
        z = Math.round(z);
        const key = `${color}|${JSON.stringify(opts)}`;
        let g = this.groups.get(key);
        if (!g) {
          g = { positions: [], color, opts };
          this.groups.set(key, g);
        }
        g.positions.push([x, y, z]);
      }

      addBox(x1, x2, y1, y2, z1, z2, color, opts = {}) {
        const minX = Math.min(x1, x2), maxX = Math.max(x1, x2);
        const minY = Math.min(y1, y2), maxY = Math.max(y1, y2);
        const minZ = Math.min(z1, z2), maxZ = Math.max(z1, z2);

        for (let x = minX; x <= maxX; x++) {
          for (let y = minY; y <= maxY; y++) {
            for (let z = minZ; z <= maxZ; z++) {
              this.add(x, y, z, color, opts);
            }
          }
        }
      }

      addRect(x1, x2, y, z1, z2, color, opts = {}) {
        const minX = Math.min(x1, x2), maxX = Math.max(x1, x2);
        const minZ = Math.min(z1, z2), maxZ = Math.max(z1, z2);

        for (let x = minX; x <= maxX; x++) {
          for (let z = minZ; z <= maxZ; z++) {
            this.add(x, y, z, color, opts);
          }
        }
      }

      build(parent) {
        if (!parent) parent = scene;
        const m = new THREE.Matrix4();

        for (const g of this.groups.values()) {
          if (g.positions.length === 0) continue;

          const opts = g.opts;
          const mat = new THREE.MeshStandardMaterial({
            color: g.color,
            roughness: opts.roughness ?? 0.85,
            metalness: opts.metalness ?? 0.0,
            transparent: !!opts.transparent,
            opacity: opts.opacity ?? 1,
            emissive: opts.emissive ?? 0x000000,
            emissiveIntensity: opts.emissiveIntensity ?? 1
          });

          const inst = new THREE.InstancedMesh(voxelGeo, mat, g.positions.length);
          inst.castShadow = opts.shadow !== false;
          inst.receiveShadow = opts.receive !== false;

          const yAdjust = opts.yAdjust || 0;
          for (let i = 0; i < g.positions.length; i++) {
            const p = g.positions[i];
            m.makeTranslation(p[0], p[1] + 0.5 + yAdjust, p[2]);
            inst.setMatrixAt(i, m);
          }

          inst.instanceMatrix.needsUpdate = true;
          parent.add(inst);
        }
      }
    }

    const C = {
      cloud: 0xf5faff,
      stone: 0x8c9aa3,
      stoneDark: 0x5e7179,
      deck: 0x97714e,
      deckDark: 0x5a412e,
      grass: 0x45a961,
      hull: 0x8a5a35,
      hullDark: 0x472f20,
      hullStripe: 0xeeddb5,
      woodDark: 0x382818,
      mast: 0xa0703f,
      sail: 0xf1e7d2,
      black: 0x111111,
      red: 0xc2433a,
      white: 0xf4f6f8,
      blueWall: 0x2a7fbb,
      yellowWall: 0xf2c451,
      whiteWall: 0xf0f4f8,
      roofRed: 0x9d3d3d,
      roofDark: 0x3b515c,
      roofGreen: 0x327a51,
      roofBrown: 0x7a4c2c,
      glass: 0x9bd7f6,
      crate: 0xb67c48,
      barrel: 0x8a5930,
      barrelBand: 0x3d2718,
      foam: 0xeaf6ff,
      trunk: 0x4e3423,
      leaf: 0x37a14f
    };

    let seed = 987654321;
    function rand() {
      seed = (seed * 1664525 + 1013904223) >>> 0;
      return seed / 4294967296;
    }

    const staticB = new VoxelBuilder();
    const shipB = new VoxelBuilder();
    const cloudB = new VoxelBuilder();

    function makeWaterTexture() {
      const s = 128;
      const canvas = document.createElement("canvas");
      canvas.width = s;
      canvas.height = s;
      const ctx = canvas.getContext("2d");

      const g = ctx.createLinearGradient(0, 0, s, s);
      g.addColorStop(0, "#2e86c1");
      g.addColorStop(1, "#1b5f99");
      ctx.fillStyle = g;
      ctx.fillRect(0, 0, s, s);

      ctx.fillStyle = "rgba(255,255,255,0.06)";
      ctx.fillRect(0, 0, s / 2, s / 2);
      ctx.fillRect(s / 2, s / 2, s / 2, s / 2);

      ctx.strokeStyle = "rgba(0,30,60,0.40)";
      ctx.lineWidth = 3;
      ctx.strokeRect(0, 0, s / 2, s / 2);
      ctx.strokeRect(s / 2, s / 2, s / 2, s / 2);

      ctx.fillStyle = "rgba(255,255,255,0.08)";
      for (let i = 0; i < s; i += 16) {
        ctx.fillRect(i, 0, 8, 8);
        ctx.fillRect(0, i, 8, 8);
      }

      const tex = new THREE.CanvasTexture(canvas);
      tex.wrapS = THREE.RepeatWrapping;
      tex.wrapT = THREE.RepeatWrapping;
      tex.repeat.set(110, 110);
      tex.anisotropy = renderer.maxAnisotropy;
      return tex;
    }

    const waterTex = makeWaterTexture();
    const waterGeo = new THREE.PlaneGeometry(220, 220, 96, 96);
    waterGeo.rotateX(-Math.PI / 2);

    const waterMat = new THREE.MeshStandardMaterial({
      map: waterTex,
      roughness: 0.32,
      metalness: 0.05,
      side: THREE.FrontSide
    });

    const water = new THREE.Mesh(waterGeo, waterMat);
    water.position.set(0, 3, 0);
    water.receiveShadow = true;
    scene.add(water);

    buildHarbor(staticB);
    addWake(staticB);
    addBoats(staticB);
    addTrees(staticB);
    buildClouds(cloudB);

    const staticGroup = new THREE.Group();
    staticB.build(staticGroup);
    scene.add(staticGroup);

    const shipGroup = new THREE.Group();
    buildShip(shipB);
    shipB.build(shipGroup);
    shipGroup.position.set(-10, 0, 0);
    scene.add(shipGroup);

    const cloudGroup = new THREE.Group();
    cloudB.build(cloudGroup);
    scene.add(cloudGroup);

    const beacon = new THREE.PointLight(0xffe080, 4, 130, 1.5);
    beacon.position.set(44, 20.5, -22);
    scene.add(beacon);

    function buildHarbor(b) {
      // Harbor base below the top surface layer.
      b.addBox(16, 50, 0, 2, -28, 28, C.stoneDark);

      // Top surface layer.
      b.addRect(16, 24, 3, -24, 24, C.deck);     // wooden quay
      b.addRect(25, 50, 3, -28, 28, C.grass);    // grassy shore

      // Quay pilings.
      for (let z = -24; z <= 24; z += 3) {
        b.addBox(16, 16, 0, 2, z, z, C.woodDark);
      }

      // Bollards.
      for (let z = -22; z <= 22; z += 5) {
        b.add(17, 4, z, C.red);
        b.add(17, 5, z, C.red);
      }

      // Cargo.
      addCrate(b, 20, -16);
      addCrate(b, 22, -16);
      addCrate(b, 21, -14);
      addCrate(b, 18, 14);
      addCrate(b, 18, 16);
      addCrate(b, 20, 15);
      addBarrel(b, 24, -18);
      addBarrel(b, 24, -17);
      addBarrel(b, 23, -18);
      addBarrel(b, 26, 18);
      addBarrel(b, 27, 18);

      // Large dock anchor.
      b.addBox(19, 20, 4, 6, -2, -2, C.black);
      b.addBox(21, 22, 4, 4, -1, 0, C.black);
      b.addBox(18, 20, 4, 4, -3, -1, C.black);

      // Harbor buildings.
      addBuilding(b, 28, 36, -22, -10, 7, C.brick ?? C.roofRed ? C.brick : C.brick, C.roofRed);
      addBuilding(b, 27, 30, -6, -1, 6, C.blueWall, C.roofDark);
      addBuilding(b, 27, 30, 5, 10, 6, C.yellowWall, C.roofGreen);
      addBuilding(b, 38, 42, -4, 2, 6, C.whiteWall, C.roofBrown);
      addBuilding(b, 35, 38, 12, 18, 7, C.brick ?? C.brick, C.roofDark);

      // Lighthouse.
      addLighthouse(b, 44, -22);
    }

    function addBuilding(b, x0, x1, z0, z1, h, wallColor, roofColor) {
      const midZ = Math.round((z0 + z1) / 2);

      for (let x = x0; x <= x1; x++) {
        for (let z = z0; z <= z1; z++) {
          for (let y = 4; y <= h; y++) {
            let col = wallColor;

            // Windows flush into the solid wall surfaces.
            if (
              (x === x0 || x === x1) &&
              y >= 5 && y <= h - 1 &&
              ((z - z0) % 2 === 1) && z > z0 && z < z1
            ) {
              col = C.glass;
            }

            if (
              (z === z0 || z === z1) &&
              y >= 5 && y <= h - 1 &&
              ((x - x0) % 2 === 1) && x > x0 && x < x1
            ) {
              col = C.glass;
            }

            // Door on the sea-facing wall.
            if (x === x0 && y === 4 && z === midZ) col = C.deckDark;

            b.add(x, y, z, col);
          }
        }
      }

      // Stepped roof.
      b.addBox(x0, x1, h + 1, h + 1, z0, z1, roofColor);
      if (x0 + 2 <= x1 - 2 && z0 + 2 <= z1 - 2) {
        b.addBox(x0 + 2, x1 - 2, h + 2, h + 2, z0 + 2, z1 - 2, roofColor);
      }
    }

    function addCrate(b, x, z, color = C.crate, baseY = 4) {
      for (let y = baseY; y <= baseY + 1; y++) {
        const col = y === baseY + 1 ? C.deckDark : color;
        b.add(x, y, z, col);
        b.add(x + 1, y, z, col);
        b.add(x, y, z + 1, col);
        b.add(x + 1, y, z + 1, col);
      }
    }

    function addBarrel(b, x, z, color = C.barrel, baseY = 4) {
      for (let y = baseY; y <= baseY + 2; y++) {
        const band = y === baseY + 1 ? C.barrelBand : color;
        b.add(x, y, z, band);
        b.add(x + 1, y, z, band);
      }
    }

    function addLighthouse(b, x, z) {
      for (let y = 4; y <= 18; y++) {
        const col = (Math.floor((y - 4) / 3) % 2 === 0) ? C.white : C.red;
        b.addBox(x - 1, x + 1, y, y, z - 1, z + 1, col);
      }

      b.addBox(x - 2, x + 2, 19, 19, z - 2, z + 2, C.deck);
      b.addBox(x - 1, x + 1, 20, 20, z - 1, z + 1, C.glass, {
        emissive: 0xffe590,
        emissiveIntensity: 1.8,
        shadow: false
      });
      b.addBox(x - 2, x + 2, 21, 21, z - 2, z + 2, C.roofDark);
    }

    function addTrees(b) {
      addTree(b, 32, 24);
      addTree(b, 34, 20);
      addTree(b, 46, -12);
      addTree(b, 47, 8);
    }

    function addTree(b, x, z) {
      b.add(x, 4, z, C.trunk);
      b.add(x, 5, z, C.trunk);
      b.add(x, 6, z, C.trunk);

      for (let dx = -2; dx <= 2; dx++) {
        for (let dz = -2; dz <= 2; dz++) {
          for (let dy = 0; dy <= 2; dy++) {
            if (Math.abs(dx) + Math.abs(dz) + dy <= 3) {
              b.add(x + dx, 7 + dy, z + dz, C.leaf);
            }
          }
        }
      }
    }

    function addBoats(b) {
      addRowboat(b, 8, 18);
      addRowboat(b, 12, -20);
    }

    function addRowboat(b, x, z) {
      const cells = [
        [0, -2],
        [-1, -1], [0, -1], [1, -1],
        [-2, 0], [-1, 0], [0, 0], [1, 0], [2, 0],
        [-1, 1], [0, 1], [1, 1],
        [0, 2]
      ];

      for (const [dx, dz] of cells) {
        b.add(x + dx, 3, z + dz, C.deck);
      }

      b.add(x, 4, z, C.deckDark);
      b.add(x + 1, 4, z, C.deckDark);
    }

    function addWake(b) {
      const minX = -26, maxX = 6, minZ = -6, maxZ = 6;

      for (let x = minX; x <= maxX; x++) {
        if ((x - minX) % 3 === 0) {
          b.add(x, 3, minZ - 1, C.foam, { shadow: false });
          b.add(x, 3, maxZ + 1, C.foam, { shadow: false });
        }
      }

      for (let z = minZ; z <= maxZ; z++) {
        if ((z - minZ) % 2 === 0) {
          b.add(minX - 1, 3, z, C.foam, { shadow: false });
          b.add(maxX + 1, 3, z, C.foam, { shadow: false });
        }
      }

      for (let i = 0; i < 10; i++) {
        const x = minX - 1 - i;
        const z = Math.round(Math.sin(i * 0.7) * 3);
        b.add(x, 3, z, C.foam, { shadow: false });
        if (i % 2 === 0) b.add(x, 3, z + 1, C.foam, { shadow: false });
      }
    }

    function buildClouds(b) {
      for (let i = 0; i < 14; i++) {
        const x = Math.round((rand() * 2 - 1) * 75);
        const z = Math.round((rand() * 2 - 1) * 75);
        const y = 32 + Math.floor(rand() * 8);
        addCloudBlob(b, x, y, z);
      }
    }

    function addCloudBlob(b, x, y, z) {
      const r = 2 + Math.floor(rand() * 3);

      for (let dx = -r; dx <= r; dx++) {
        for (let dz = -r; dz <= r; dz++) {
          if (dx * dx + dz * dz <= r * r + 2) {
            b.add(x + dx, y, z + dz, C.cloud, { shadow: false, receive: false });
          }
          if (dx * dx + dz * dz <= (r - 1) * (r - 1) + 2) {
            b.add(x + dx, y + 1, z + dz, C.cloud, { shadow: false, receive: false });
          }
        }
      }
    }

    function buildShip(b) {
      const halfBeam = new Array(32).fill(5);
      halfBeam[0] = 2;
      halfBeam[1] = 3;
      halfBeam[2] = 4;
      halfBeam[28] = 4;
      halfBeam[29] = 3;
      halfBeam[30] = 2;
      halfBeam[31] = 1;

      function deckTop(i) {
        return (i < 5 || i > 27) ? 8 : 7;
      }

      // Hull.
      for (let i = 0; i < 32; i++) {
        const x = i - 16;
        const half = halfBeam[i];
        const top = deckTop(i);

        for (let z = -half; z <= half; z++) {
          for (let y = 3; y <= top; y++) {
            let col = C.hull;

            if (y === 3) col = C.hullDark;
            else if (y === 4) col = C.hullStripe;
            else if (y === top) col = C.deck;
            else if (
              (z === half || z === -half) &&
              y === 5 && i > 5 && i < 26 && i % 3 === 0
            ) {
              col = C.black; // gunports
            }

            b.add(x, y, z, col);
          }
        }
      }

      // Deck railing.
      for (let i = 0; i < 32; i++) {
        const x = i - 16;
        const half = halfBeam[i];
        const y = deckTop(i) + 1;

        b.add(x, y, half, C.woodDark);
        b.add(x, y, -half, C.woodDark);

        if (i === 0) {
          for (let z = -half; z <= half; z++) b.add(x, y, z, C.woodDark);
        }
        if (i === 31) {
          for (let z = -half; z <= half; z++) b.add(x, y, z, C.woodDark);
        }
      }

      // Stern cabin.
      b.addBox(-14, -11, 9, 10, -3, 3, C.deck);

      // Bowsprit.
      for (let j = 0; j <= 6; j++) {
        b.add(16 + j, 9 + Math.floor(j / 2), 0, C.mast);
      }

      // Masts.
      addMast(b, 0, 8, 26);      // main
      addMast(b, 10, 8, 23);     // fore
      addMast(b, -10, 8, 20);    // mizzen

      // Yards.
      addYard(b, 0, 20, 8);
      addYard(b, 0, 25, 5);
      addYard(b, 10, 18, 7);
      addYard(b, 10, 23, 4);
      addYard(b, -10, 18, 5);

      // Sails.
      addSail(b, 0, 8, 13, 20);   // lower main
      addSail(b, 0, 5, 21, 25);   // upper main
      addSail(b, 10, 7, 11, 18);  // lower fore
      addSail(b, 10, 4, 19, 23);  // upper fore
      addSail(b, -10, 5, 12, 18); // mizzen

      // Jib.
      addJib(b, 22, 12, 10, 20);

      // Flags.
      addFlag(b, 0, 27);
      addFlag(b, 10, 24);
      addFlag(b, -10, 21);
      addFlag(b, 22, 12);

      // Deck cargo.
      addCrate(b, -4, -3, C.crate, 8);
      addCrate(b, 2, 3, C.crate, 8);
      addBarrel(b, 5, 0, C.barrel, 8);
    }

    function addMast(b, x, y1, y2) {
      for (let y = y1; y <= y2; y++) b.add(x, y, 0, C.mast);
    }

    function addYard(b, x, y, span) {
      for (let z = -span; z <= span; z++) b.add(x, y, z, C.woodDark);
    }

    function addSail(b, mastX, span, bottom, top, color = C.sail, billow = -1) {
      for (let z = -span; z <= span; z++) {
        const t = Math.abs(z) / span;
        const depth = Math.max(1, Math.min(2, Math.round(1 + (1 - t) * 1.2)));
        const x = mastX + billow * depth;

        for (let y = bottom; y < top; y++) {
          b.add(x, y, z, color);
        }
      }
    }

    function addJib(b, tipX, tipY, mastX, mastTopY, color = C.sail) {
      const steps = tipX - mastX;

      for (let i = 1; i < steps; i++) {
        const t = i / steps;
        const x = tipX - i;
        const y = Math.round(tipY + (mastTopY - tipY) * t);
        const zHalf = Math.round(t * 2.5);

        for (let z = -zHalf; z <= zHalf; z++) {
          b.add(x, y, z, color);
        }
      }
    }

    function addFlag(b, x, yTop, color = C.red) {
      b.addBox(x, x, yTop, yTop + 1, 1, 2, color);
      b.add(x, yTop + 1, 3, C.white);
    }

    window.addEventListener("resize", () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    });

    const clock = new THREE.Clock();

    function animate() {
      requestAnimationFrame(animate);

      const dt = clock.getDelta();
      const t = clock.elapsedTime;

      shipGroup.position.y = Math.sin(t * 0.85) * 0.12;
      shipGroup.rotation.z = Math.sin(t * 0.65) * 0.015;
      shipGroup.rotation.x = Math.sin(t * 0.45) * 0.006;

      cloudGroup.rotation.y += dt * 0.008;

      waterMat.map.offset.x += dt * 0.012;
      waterMat.map.offset.y += dt * 0.004;

      beacon.intensity = 1.6 + Math.sin(t * 4) * 0.9;

      controls.update();
      renderer.render(scene, camera);
    }

    animate();
  </script>
</body>
</html>
```