```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Voxel Art: Sailing Ship Calling at a Harbor</title>
  <style>
    html, body {
      margin: 0;
      height: 100%;
      overflow: hidden;
      background: #8fbfe0;
    }

    canvas {
      display: block;
      touch-action: none;
    }

    #info {
      position: fixed;
      left: 12px;
      bottom: 12px;
      padding: 8px 12px;
      border-radius: 10px;
      background: rgba(0, 0, 0, 0.35);
      color: #eaf6ff;
      font: 13px/1.4 system-ui, sans-serif;
      pointer-events: none;
    }
  </style>
</head>
<body>
  <div id="info">
    Drag: orbit • Scroll: zoom • Right-drag: pan
  </div>

  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js"></script>

  <script>
    (function () {
      if (typeof THREE === "undefined") {
        document.body.textContent = "Failed to load Three.js from CDN.";
        return;
      }

      const COLORS = {
        sky: 0x8fbfe0,
        sea1: 0x2f839f,
        sea2: 0x4294a4,
        sea3: 0x27708d,
        foam: 0xb6dfec,
        stoneTop: 0x909aa3,
        stoneFace: 0x768088,
        stoneDeep: 0x687178,
        deckWood: 0xa76d42,
        wood: 0x8b5a32,
        woodDark: 0x4c3422,
        mast: 0x966c47,
        yard: 0x714c2b,
        sail: 0xece8df,
        sailShade: 0xbcb4a2,
        hullLow: 0x2b1d14,
        hullMid: 0x3a2718,
        hullWater: 0x1f1a16,
        hullTop: 0x6a4932,
        rail: 0x433124,
        cannon: 0x262626,
        house1: 0x8c6240,
        house2: 0x755034,
        roof: 0x553825,
        window: 0x9fd3e3,
        door: 0x4a3524,
        flag: 0xc2313a,
        white: 0xf3f2ef,
        red: 0xd03c36,
        lamp: 0xffd360
      };

      // Renderer / scene / camera
      const scene = new THREE.Scene();
      scene.background = new THREE.Color(COLORS.sky);
      scene.fog = new THREE.Fog(COLORS.sky, 70, 210);

      const camera = new THREE.PerspectiveCamera(
        55,
        window.innerWidth / window.innerHeight,
        0.1,
        500
      );

      const renderer = new THREE.WebGLRenderer({ antialias: true });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      renderer.setSize(window.innerWidth, window.innerHeight);
      if (THREE.sRGBEncoding) renderer.outputEncoding = THREE.sRGBEncoding;
      document.body.appendChild(renderer.domElement);

      // Lights
      scene.add(new THREE.HemisphereLight(0xbfdfff, 0x45606c, 0.85));
      const sun = new THREE.DirectionalLight(0xffffff, 0.55);
      sun.position.set(35, 55, 20);
      scene.add(sun);
      scene.add(new THREE.AmbientLight(0x404040, 0.45));

      // Occupancy avoids z-fighting / duplicate voxels.
      const OCC = new Set();

      function occKey(x, y, z) {
        return (x + 128) + ((y + 64) << 8) + ((z + 128) << 16);
      }

      class Builder {
        constructor() {
          this.pos = [];
          this.col = [];
        }

        add(x, y, z, color) {
          this.pos.push([x, y, z]);
          this.col.push(color);
        }
      }

      function addVoxel(b, x, level, z, color) {
        const k = occKey(x, level, z);
        if (OCC.has(k)) return false;
        OCC.add(k);
        b.add(x, level - 0.5, z, color);
        return true;
      }

      const boxGeo = new THREE.BoxGeometry(1, 1, 1);
      const voxelMat = new THREE.MeshLambertMaterial({
        color: 0xffffff,
        flatShading: true
      });

      function makeInstancedMesh(b) {
        if (b.pos.length === 0) return null;

        const mesh = new THREE.InstancedMesh(boxGeo, voxelMat, b.pos.length);
        const dummy = new THREE.Object3D();
        const color = new THREE.Color();

        for (let i = 0; i < b.pos.length; i++) {
          const p = b.pos[i];
          dummy.position.set(p[0], p[1], p[2]);
          dummy.rotation.set(0, 0, 0);
          dummy.scale.set(1, 1, 1);
          dummy.updateMatrix();
          mesh.setMatrixAt(i, dummy.matrix);

          color.setHex(b.col[i]);
          mesh.setColorAt(i, color);
        }

        mesh.instanceMatrix.needsUpdate = true;
        if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
        return mesh;
      }

      // Builders
      const shipB = new Builder();
      const flagB = new Builder();
      const quayB = new Builder();
      const seaB = new Builder();

      // ---------- SHIP ----------
      function addShip(b) {
        function halfBeam(x) {
          if (x < -7) return Math.max(1, Math.min(4, 4 + x + 7));
          if (x > 4) return Math.max(1, Math.min(4, 8 - x));
          return 4;
        }

        // Hull: levels -3 to 2 are mostly solid.
        for (let x = -10; x <= 7; x++) {
          const h = halfBeam(x);

          for (let z = -h; z <= h; z++) {
            for (let y = -3; y <= 0; y++) {
              let c;
              if (y === 0) c = COLORS.hullWater;
              else if (y <= -3) c = COLORS.hullLow;
              else c = COLORS.hullMid;
              addVoxel(b, x, y, z, c);
            }

            addVoxel(b, x, 1, z, COLORS.hullTop);

            if (Math.abs(z) < h) {
              addVoxel(b, x, 2, z, COLORS.deckWood);
            }
          }

          // Rail / bulwarks
          if (h > 0) {
            addVoxel(b, x, 3, h, COLORS.rail);
            addVoxel(b, x, 3, -h, COLORS.rail);
          }

          if (x === -10 || x === 7) {
            for (let z = -h; z <= h; z++) addVoxel(b, x, 3, z, COLORS.rail);
          }
        }

        // Cannon barrels
        for (let x = -7; x <= 4; x += 2) {
          const h = halfBeam(x);
          if (h >= 2) {
            addVoxel(b, x, 1, h + 1, COLORS.cannon);
            addVoxel(b, x, 1, -h - 1, COLORS.cannon);
          }
        }

        // Sterncastle
        for (let x = -10; x <= -8; x++) {
          for (let z = -2; z <= 2; z++) {
            for (let y = 3; y <= 5; y++) {
              addVoxel(b, x, y, z, y === 5 ? 0x593a24 : 0x745033);
            }
          }

          // Side windows
          addVoxel(b, x, 4, -3, COLORS.window);
          addVoxel(b, x, 4, 3, COLORS.window);
        }

        // Bow forecastle
        for (let x = 5; x <= 6; x++) {
          for (let z = -1; z <= 1; z++) {
            for (let y = 3; y <= 4; y++) addVoxel(b, x, y, z, 0x715034);
          }
        }

        // Bowsprit
        const bowsprit = [
          [8, 4],
          [9, 5],
          [10, 5],
          [11, 6],
          [12, 6],
          [13, 7]
        ];
        for (const p of bowsprit) addVoxel(b, p[0], p[1], 0, 0x8a5a32);

        // Small jib sail hint
        addVoxel(b, 10, 4, 0, COLORS.sail);
        addVoxel(b, 11, 5, 0, COLORS.sail);
        addVoxel(b, 12, 6, 0, COLORS.sail);
        addVoxel(b, 12, 5, 0, COLORS.sail);

        function mast(x, base, height) {
          for (let y = base; y <= height; y++) addVoxel(b, x, y, 0, COLORS.mast);
        }

        function yard(x, y, half) {
          for (let z = -half - 1; z <= half + 1; z++) {
            addVoxel(b, x, y, z, COLORS.yard);
          }
        }

        function sail(x, y0, y1, half) {
          for (let y = y0; y <= y1; y++) {
            const c = (y % 2 === 0) ? COLORS.sail : COLORS.sailShade;
            for (let z = -half; z <= half; z++) {
              addVoxel(b, x, y, z, c);
            }
          }
        }

        // Main, fore, mizzen masts
        mast(-1, 3, 15);
        mast(4, 3, 11);
        mast(-7, 6, 10);

        // Main sails
        yard(-1, 9, 5);
        sail(-1, 6, 8, 5);

        yard(-1, 14, 4);
        sail(-1, 11, 13, 4);

        // Fore sails
        yard(4, 7, 3);
        sail(4, 4, 6, 3);

        yard(4, 11, 2);
        sail(4, 8, 10, 2);

        // Mizzen sail
        yard(-7, 10, 3);
        sail(-7, 7, 9, 3);
      }

      function buildFlag(shipBuilder, flagBuilder) {
        // Flag pole
        addVoxel(shipBuilder, -1, 16, 0, 0x555555);

        // Dynamic pennant voxels
        for (let i = 1; i <= 5; i++) {
          const color = (i === 5) ? 0xf7f7f7 : COLORS.flag;
          flagBuilder.add(-1 + i, 16 - 0.5, 0, color);
        }
      }

      // ---------- HARBOR ----------
      function addWarehouse(b, x1, x2, z1, z2, wallColor) {
        for (let x = x1; x <= x2; x++) {
          for (let z = z1; z <= z2; z++) {
            for (let y = 1; y <= 3; y++) addVoxel(b, x, y, z, wallColor);
            addVoxel(b, x, 4, z, COLORS.roof);
          }
        }

        // Harbor-facing windows / door
        const sx = x1 - 1;
        for (let z = z1 + 2; z <= z2 - 2; z++) {
          addVoxel(b, sx, 1, z, COLORS.door);
          addVoxel(b, sx, 2, z, COLORS.window);
          addVoxel(b, sx, 3, z, COLORS.window);
        }
      }

      function addBarrel(b, x, z, body, lid) {
        addVoxel(b, x, 1, z, body);
        addVoxel(b, x, 2, z, lid);
      }

      function addCrate(b, x, z) {
        addVoxel(b, x, 1, z, 0xb0763b);
        addVoxel(b, x, 2, z, 0x88552c);
      }

      function addLamp(b, x, z) {
        addVoxel(b, x, 1, z, 0x4a382c);
        addVoxel(b, x, 2, z, 0x4a382c);
        addVoxel(b, x, 3, z, COLORS.lamp);
      }

      function addLighthouse(b) {
        // Tower
        for (let y = 1; y <= 8; y++) {
          const c = ((y - 1) % 4 < 2) ? COLORS.white : COLORS.red;
          for (let x = 25; x <= 26; x++) {
            for (let z = 19; z <= 20; z++) {
              addVoxel(b, x, y, z, c);
            }
          }
        }

        // Gallery
        for (let x = 24; x <= 27; x++) {
          for (let z = 18; z <= 21; z++) {
            addVoxel(b, x, 9, z, 0x2f2f2f);
          }
        }

        // Lantern room / cap
        for (let x = 25; x <= 26; x++) {
          for (let z = 19; z <= 20; z++) {
            addVoxel(b, x, 10, z, COLORS.lamp);
            addVoxel(b, x, 11, z, 0x222222);
          }
        }

        // Tiny static flag
        addVoxel(b, 25, 12, 19, 0x555555);
        addVoxel(b, 26, 12, 19, COLORS.flag);
      }

      function addCrane(b) {
        // Base
        for (let x = 18; x <= 19; x++) {
          for (let z = 5; z <= 6; z++) {
            addVoxel(b, x, 1, z, 0x8d949a);
            addVoxel(b, x, 2, z, 0x6e757b);
          }
        }

        // Mast
        for (let y = 3; y <= 7; y++) addVoxel(b, 18, y, 5, 0x8a5a32);

        // Arm
        for (let x = 15; x <= 18; x++) addVoxel(b, x, 8, 5, 0x8a5a32);

        // Counterweight / cable / load
        addVoxel(b, 20, 8, 5, 0x666666);
        addVoxel(b, 19, 8, 6, 0x666666);

        addVoxel(b, 15, 7, 5, 0x333333);
        addVoxel(b, 15, 6, 5, 0x333333);
        addVoxel(b, 15, 5, 5, 0x333333);
        addVoxel(b, 15, 4, 5, 0x7a4129);
      }

      function addQuay(b) {
        // Land
        for (let x = 17; x <= 28; x++) {
          for (let z = -22; z <= 22; z++) {
            for (let y = 0; y >= -3; y--) {
              const c = y === 0 ? (x === 17 ? COLORS.stoneFace : COLORS.stoneTop) : COLORS.stoneDeep;
              addVoxel(b, x, y, z, c);
            }
          }
        }

        // Wooden pier deck
        for (let x = 8; x <= 16; x++) {
          for (let z = -1; z <= 1; z++) {
            addVoxel(b, x, 0, z, (x % 2) ? COLORS.deckWood : COLORS.wood);
          }
        }

        // Pier posts
        for (let x = 9; x <= 15; x += 2) {
          for (let z = -1; z <= 1; z++) {
            for (let y = -1; y >= -3; y--) addVoxel(b, x, y, z, COLORS.woodDark);
          }
        }

        // Bollards
        const bollards = [10, 13, 16];
        for (const x of bollards) {
          for (const z of [-1, 1]) {
            addVoxel(b, x, 1, z, 0x694b34);
            addVoxel(b, x, 2, z, 0x4b3626);
          }
        }

        // Lamps
        addLamp(b, 16, 0);
        addLamp(b, 18, 10);
        addLamp(b, 18, -17);

        // Cargo
        addBarrel(b, 11, -1, 0x9b5c38, 0x7a4127);
        addBarrel(b, 12, 1, 0x4b7a8f, 0x325a6f);
        addBarrel(b, 15, 0, 0x9b5c38, 0x7a4127);

        addCrate(b, 14, -1);
        addCrate(b, 14, 1);
        addCrate(b, 19, -18);
        addCrate(b, 19, -17);
        addCrate(b, 24, -12);

        // Warehouses
        addWarehouse(b, 20, 23, -15, -9, COLORS.house1);
        addWarehouse(b, 20, 22, 10, 14, COLORS.house2);

        // Harbor structures
        addLighthouse(b);
        addCrane(b);
      }

      // ---------- SEA ----------
      function addSea(b) {
        for (let x = -28; x <= 16; x++) {
          for (let z = -22; z <= 22; z++) {
            if (!OCC.has(occKey(x, 0, z))) {
              const n =
                Math.sin(x * 0.7 + z * 0.5) +
                Math.cos(z * 0.9 - x * 0.3);

              let c = COLORS.sea1;
              if (n > 0.8) c = COLORS.sea2;
              else if (n < -0.8) c = COLORS.sea3;

              const foam =
                OCC.has(occKey(x + 1, 0, z)) ||
                OCC.has(occKey(x - 1, 0, z)) ||
                OCC.has(occKey(x, 0, z + 1)) ||
                OCC.has(occKey(x, 0, z - 1));

              if (foam) c = COLORS.foam;

              b.add(x, -0.5, z, c);
            }

            if (!OCC.has(occKey(x, -1, z))) b.add(x, -1.5, z, 0x276f8f);
            if (!OCC.has(occKey(x, -2, z))) b.add(x, -2.5, z, 0x215c77);
            if (!OCC.has(occKey(x, -3, z))) b.add(x, -3.5, z, 0x18485f);
          }
        }
      }

      // Build world geometry
      addShip(shipB);
      buildFlag(shipB, flagB);
      addQuay(quayB);
      addSea(seaB);

      // Meshes
      const shipGroup = new THREE.Group();
      scene.add(shipGroup);

      const shipMesh = makeInstancedMesh(shipB);
      if (shipMesh) shipGroup.add(shipMesh);

      const flagMesh = makeInstancedMesh(flagB);
      if (flagMesh) shipGroup.add(flagMesh);

      const quayMesh = makeInstancedMesh(quayB);
      if (quayMesh) scene.add(quayMesh);

      const seaMesh = makeInstancedMesh(seaB);
      if (seaMesh) scene.add(seaMesh);

      // Rigging inside ship group
      function buildRig(group) {
        const pts = [];

        function seg(x1, y1, z1, x2, y2, z2) {
          pts.push(x1, y1 - 0.5, z1, x2, y2 - 0.5, z2);
        }

        // Main mast shrouds
        for (const z of [-4, 4]) {
          seg(-1, 15, 0, -6, 3, z);
          seg(-1, 15, 0, 2, 3, z);
          seg(-1, 14, 0, -7, 2, z);
          seg(-1, 14, 0, 1, 2, z);
        }

        // Fore mast shrouds
        for (const z of [-3, 3]) {
          seg(4, 11, 0, 1, 3, z);
          seg(4, 11, 0, 7, 3, z);
        }

        // Mizzen shrouds
        for (const z of [-2, 2]) {
          seg(-7, 10, 0, -10, 5, z);
          seg(-7, 10, 0, -4, 4, z);
        }

        // Bowsprit / stays / backstays
        seg(-1, 15, 0, 13, 7, 0);
        seg(4, 11, 0, 13, 7, 0);
        seg(13, 7, 0, 11, 5, 0);
        seg(-1, 15, 0, -10, 5, 0);

        const geo = new THREE.BufferGeometry();
        geo.setAttribute("position", new THREE.Float32BufferAttribute(pts, 3));

        const mat = new THREE.LineBasicMaterial({
          color: 0x87705a,
          transparent: true,
          opacity: 0.85
        });

        group.add(new THREE.LineSegments(geo, mat));
      }

      buildRig(shipGroup);

      // Mooring lines from ship to pier
      const moorPos = new Float32Array(12);
      const moorGeom = new THREE.BufferGeometry();
      moorGeom.setAttribute("position", new THREE.BufferAttribute(moorPos, 3));

      const moorLines = new THREE.LineSegments(
        moorGeom,
        new THREE.LineBasicMaterial({ color: 0x9a7a5b })
      );
      scene.add(moorLines);

      const moorAttach = [
        { lx: 7, ly: 2.5, lz: -1, wx: 10, wy: 0.5, wz: -1 },
        { lx: -10, ly: 3.5, lz: 2, wx: 13, wy: 0.5, wz: 1 }
      ];

      const tmp = new THREE.Vector3();

      function updateMooring() {
        for (let i = 0; i < moorAttach.length; i++) {
          const a = moorAttach[i];
          const idx = i * 6;

          tmp.set(a.lx, a.ly, a.lz);
          shipGroup.localToWorld(tmp);

          moorPos[idx] = tmp.x;
          moorPos[idx + 1] = tmp.y;
          moorPos[idx + 2] = tmp.z;

          moorPos[idx + 3] = a.wx;
          moorPos[idx + 4] = a.wy;
          moorPos[idx + 5] = a.wz;
        }

        moorGeom.attributes.position.needsUpdate = true;
      }

      // Camera orbit controls
      const target = new THREE.Vector3(-2, 4, 0);
      let theta = 2.36;
      let phi = 1.15;
      let radius = 62;

      function clampRadius() {
        radius = Math.max(14, Math.min(170, radius));
      }

      function updateCamera() {
        const p = Math.max(0.15, Math.min(Math.PI - 0.15, phi));
        const s = Math.sin(p);

        camera.position.set(
          target.x + radius * s * Math.cos(theta),
          target.y + radius * Math.cos(p),
          target.z + radius * s * Math.sin(theta)
        );

        camera.lookAt(target);
      }

      updateCamera();

      const pointers = new Map();
      let lastPinch = 0;

      function onPointerDown(e) {
        e.preventDefault();
        renderer.domElement.setPointerCapture(e.pointerId);

        pointers.set(e.pointerId, {
          x: e.clientX,
          y: e.clientY,
          button: e.button,
          type: e.pointerType
        });

        if (pointers.size === 2) {
          const vals = Array.from(pointers.values());
          lastPinch = Math.hypot(vals[0].x - vals[1].x, vals[0].y - vals[1].y);
        }
      }

      function onPointerMove(e) {
        if (!pointers.has(e.pointerId)) return;
        e.preventDefault();

        const p = pointers.get(e.pointerId);
        const dx = e.clientX - p.x;
        const dy = e.clientY - p.y;
        p.x = e.clientX;
        p.y = e.clientY;

        if (pointers.size === 2) {
          const vals = Array.from(pointers.values());
          const dist = Math.hypot(vals[0].x - vals[1].x, vals[0].y - vals[1].y);

          if (lastPinch > 0) {
            radius *= lastPinch / dist;
            clampRadius();
          }

          lastPinch = dist;
        } else {
          if (p.button === 2) {
            // Pan
            const forward = new THREE.Vector3().subVectors(camera.position, target).normalize();
            const right = new THREE.Vector3().crossVectors(forward, camera.up).normalize();
            const up = new THREE.Vector3().crossVectors(right, forward).normalize();

            target.addScaledVector(right, -dx * radius * 0.001);
            target.addScaledVector(up, dy * radius * 0.001);
          } else {
            // Orbit
            theta -= dx * 0.005;
            phi += dy * 0.005;
          }
        }

        updateCamera();
      }

      function onPointerUp(e) {
        pointers.delete(e.pointerId);
        lastPinch = 0;
      }

      renderer.domElement.addEventListener("contextmenu", e => e.preventDefault());
      renderer.domElement.addEventListener("pointerdown", onPointerDown);
      renderer.domElement.addEventListener("pointermove", onPointerMove);
      renderer.domElement.addEventListener("pointerup", onPointerUp);
      renderer.domElement.addEventListener("pointercancel", onPointerUp);

      renderer.domElement.addEventListener(
        "wheel",
        e => {
          e.preventDefault();
          radius *= Math.exp(e.deltaY * 0.001);
          clampRadius();
          updateCamera();
        },
        { passive: false }
      );

      window.addEventListener("resize", () => {
        renderer.setSize(window.innerWidth, window.innerHeight);
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        updateCamera();
      });

      // Animation
      const clock = new THREE.Clock();
      const dummy = new THREE.Object3D();
      const flagBase = flagB.pos;

      function animate() {
        requestAnimationFrame(animate);

        const t = clock.getElapsedTime();

        // Gentle moored bobbing
        shipGroup.position.set(
          0,
          Math.sin(t * 1.7) * 0.18,
          0
        );
        shipGroup.rotation.x = Math.sin(t * 1.3) * 0.012;
        shipGroup.rotation.y = Math.sin(t * 0.7) * 0.008;
        shipGroup.updateMatrixWorld(true);

        // Waving ship pennant
        if (flagMesh) {
          for (let i = 0; i < flagBase.length; i++) {
            const p = flagBase[i];
            const phase = (p[0] + 1) * 1.1;
            const off =
              Math.sin(t * 4.5 + phase) * 0.05 +
              Math.sin(t * 7.0 + phase * 0.5) * 0.02;

            dummy.position.set(p[0], p[1] + off, p[2]);
            dummy.rotation.set(0, 0, 0);
            dummy.scale.set(1, 1, 1);
            dummy.updateMatrix();
            flagMesh.setMatrixAt(i, dummy.matrix);
          }
          flagMesh.instanceMatrix.needsUpdate = true;
        }

        updateMooring();

        renderer.render(scene, camera);
      }

      animate();
    })();
  </script>
</body>
</html>
```