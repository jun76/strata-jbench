```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Voxel Scene — A Sailing Ship Calling at a Harbor</title>
  <style>
    html, body {
      margin: 0;
      height: 100%;
      overflow: hidden;
      background: #9cd8ef;
    }
    canvas {
      display: block;
      touch-action: none;
    }
    #hint {
      position: fixed;
      left: 12px;
      bottom: 10px;
      color: #102;
      font: 13px system-ui, sans-serif;
      background: rgba(255, 255, 255, 0.58);
      padding: 6px 9px;
      border-radius: 8px;
      pointer-events: none;
      user-select: none;
    }
  </style>
</head>
<body>
  <div id="hint">Drag to orbit · Right-drag to pan · Scroll to zoom</div>

  <!-- Three.js -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>

  <script>
    if (typeof THREE === "undefined") {
      document.body.innerHTML =
        '<p style="font:16px system-ui;color:#fff;background:#223;padding:2rem;margin:2rem;border-radius:8px;">' +
        "Could not load Three.js from CDN. Check your internet connection and reload." +
        "</p>";
    } else {
      (function () {
        "use strict";

        // -----------------------------------------------------------------
        // Renderer / scene / camera
        // -----------------------------------------------------------------
        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);

        const scene = new THREE.Scene();

        const C = {
          sky: 0x9cd8ef,
          cloud: 0xffffff,

          water: 0x2f8ec2,
          waterDeep: 0x1f649a,
          waterLight: 0x63bde0,
          foam: 0xd4f3ff,

          stone: 0x9aa3a8,
          stoneDark: 0x6f787f,
          path: 0xc1b8a6,
          grass: 0x63a94d,
          grassDark: 0x4e8c3a,

          dock: 0x9b6b43,
          dockDark: 0x6c4628,
          crate: 0xb7864f,
          crateDark: 0x7f5430,
          barrel: 0x8c5a36,
          barrelBand: 0x595e65,

          shipHull: 0x6b3d26,
          shipHullDark: 0x382216,
          shipTrim: 0x8d5a35,
          deck: 0xc89663,
          mast: 0x714d2f,
          sail: 0xf5f0e3,
          sailShadow: 0xd8ccba,
          rigging: 0xcfc5b4,
          flagBlue: 0x2d5e94,
          flagRed: 0xc64545,

          window: 0xfff4a6,
          wallCream: 0xe7d5ae,
          wallBlue: 0x7ea6c9,
          wallPink: 0xd59f9f,
          roofRed: 0xa73b2b,
          roofBlue: 0x4875a8,
          roofDark: 0x343f46,

          metal: 0x7c8790,
          lamp: 0xffe27c,
          leaf: 0x458e4f,
          trunk: 0x694329,
          bird: 0x22272d
        };

        scene.background = new THREE.Color(C.sky);
        scene.fog = new THREE.Fog(C.sky, 130, 280);

        const camera = new THREE.PerspectiveCamera(
          45,
          window.innerWidth / window.innerHeight,
          0.1,
          1600
        );

        // -----------------------------------------------------------------
        // Lights
        // -----------------------------------------------------------------
        const hemi = new THREE.HemisphereLight(0xe9f6ff, 0x8a7d5c, 0.75);
        scene.add(hemi);

        const sun = new THREE.DirectionalLight(0xfff1cc, 0.95);
        sun.position.set(30, 45, 20);
        scene.add(sun);

        // -----------------------------------------------------------------
        // Voxel storage and builder helpers
        // -----------------------------------------------------------------
        const geo = new THREE.BoxGeometry(1, 1, 1);
        const worldMap = new Map();
        const shipMap = new Map();

        function addTo(map, x, y, z, c) {
          const xi = Math.round(x);
          const yi = Math.round(y);
          const zi = Math.round(z);
          const key = xi + "," + yi + "," + zi;
          map.set(key, { x: xi, y: yi, z: zi, c: c });
        }

        function fill(map, x1, x2, y1, y2, z1, z2, c) {
          const xs = Math.round(Math.min(x1, x2));
          const xe = Math.round(Math.max(x1, x2));
          const ys = Math.round(Math.min(y1, y2));
          const ye = Math.round(Math.max(y1, y2));
          const zs = Math.round(Math.min(z1, z2));
          const ze = Math.round(Math.max(z1, z2));

          for (let x = xs; x <= xe; x++) {
            for (let y = ys; y <= ye; y++) {
              for (let z = zs; z <= ze; z++) {
                addTo(map, x, y, z, c);
              }
            }
          }
        }

        function addWorld(x, y, z, c) {
          addTo(worldMap, x, y, z, c);
        }

        function fillWorld(x1, x2, y1, y2, z1, z2, c) {
          fill(worldMap, x1, x2, y1, y2, z1, z2, c);
        }

        function addShip(x, y, z, c) {
          addTo(shipMap, x, y, z, c);
        }

        function fillShip(x1, x2, y1, y2, z1, z2, c) {
          fill(shipMap, x1, x2, y1, y2, z1, z2, c);
        }

        function addCrate(map, x, z, s) {
          if (s === undefined) s = 2;
          fill(map, x, x + s - 1, 2, 2 + s - 1, z, z + s - 1, C.crate);
          fill(
            map,
            x,
            x + s - 1,
            2 + s - 1,
            2 + s - 1,
            z,
            z + s - 1,
            C.crateDark
          );
        }

        function addBarrel(map, x, z) {
          fill(map, x, x, 2, 3, z, z, C.barrel);
          fill(map, x, x, 3, 3, z, z, C.barrelBand);
        }

        function addTree(map, x, z) {
          fill(map, x, x, 2, 3, z, z, C.trunk);
          fill(map, x - 1, x + 1, 4, 6, z - 1, z + 1, C.leaf);
        }

        function addCloud(map, x, z) {
          fill(map, x, x + 4, 18, 18, z, z + 3, C.cloud);
          fill(map, x + 1, x + 3, 19, 19, z + 1, z + 2, C.cloud);
          fill(map, x + 2, x + 2, 20, 20, z + 1, z + 2, C.cloud);
        }

        function addBird(map, x, y, z) {
          addTo(map, x, y, z, C.bird);
          addTo(map, x - 1, y + 1, z, C.bird);
          addTo(map, x + 1, y + 1, z, C.bird);
        }

        function buildMap(map, parent) {
          const groups = new Map();

          for (const v of map.values()) {
            let arr = groups.get(v.c);
            if (!arr) {
              arr = [];
              groups.set(v.c, arr);
            }
            arr.push(v);
          }

          const dummy = new THREE.Object3D();

          for (const pair of groups.entries()) {
            const color = pair[0];
            const items = pair[1];

            const material = new THREE.MeshLambertMaterial({ color: color });
            const mesh = new THREE.InstancedMesh(geo, material, items.length);
            mesh.frustumCulled = false;

            for (let i = 0; i < items.length; i++) {
              const v = items[i];
              dummy.position.set(v.x, v.y, v.z);
              dummy.rotation.set(0, 0, 0);
              dummy.scale.set(1, 1, 1);
              dummy.updateMatrix();
              mesh.setMatrixAt(i, dummy.matrix);
            }

            mesh.instanceMatrix.needsUpdate = true;
            parent.add(mesh);
          }
        }

        // -----------------------------------------------------------------
        // Infinite-ish sea plane beneath the voxel water
        // -----------------------------------------------------------------
        const seaBase = new THREE.Mesh(
          new THREE.PlaneGeometry(1200, 1200),
          new THREE.MeshLambertMaterial({ color: C.waterDeep })
        );
        seaBase.rotation.x = -Math.PI / 2;
        seaBase.position.y = -0.52;
        scene.add(seaBase);

        // -----------------------------------------------------------------
        // World construction
        // -----------------------------------------------------------------
        function buildWater() {
          for (let x = -42; x <= 9; x++) {
            for (let z = -42; z <= 42; z++) {
              let c = C.water;

              const n =
                (((x * 73 + z * 131 + 17) % 23) + 23) % 23;

              if (n === 0) c = C.waterLight;
              else if (n === 7 || n === 13) c = C.waterDeep;

              if (x >= 8 && z % 5 === 0) c = C.foam;

              addWorld(x, -1, z, c);
            }
          }
        }

        function buildLand() {
          // Main harbor quay / island surface
          fillWorld(10, 32, 1, 1, -34, 34, C.stone);
          fillWorld(16, 32, 1, 1, -34, 34, C.grass);
          fillWorld(15, 15, 1, 1, -34, 34, C.path);

          // Quay face
          fillWorld(10, 10, -1, 0, -34, 34, C.stoneDark);

          // Breakwater / little jetty at the right
          fillWorld(8, 10, -1, 0, 28, 42, C.stoneDark);
          fillWorld(8, 10, 1, 1, 28, 42, C.stone);
          fillWorld(9, 9, 2, 3, 42, 42, C.metal);
          fillWorld(9, 9, 4, 4, 42, 42, C.lamp);

          // Soft hills
          fillWorld(25, 32, 2, 2, 20, 32, C.grass);
          fillWorld(26, 31, 3, 3, 21, 31, C.grassDark);
          fillWorld(27, 30, 4, 4, 22, 30, C.grass);
        }

        function buildDock() {
          // Pier reaching out to the ship
          fillWorld(5, 10, 1, 1, -2, 2, C.dock);

          // Plank stripes
          for (let x = 5; x <= 10; x += 2) {
            fillWorld(x, x, 1, 1, -2, 2, C.dockDark);
          }

          // Pilings
          for (const x of [5, 8, 10]) {
            for (const z of [-2, 2]) {
              fillWorld(x, x, -1, 0, z, z, C.dockDark);
            }
          }

          // Gangplank from ship to pier
          fillWorld(4, 5, 1, 1, -1, 1, C.crateDark);
          fillWorld(4, 5, 2, 2, -1, -1, C.metal);
          fillWorld(4, 5, 2, 2, 1, 1, C.metal);
        }

        function buildBuildings() {
          // Large warehouse
          fillWorld(16, 21, 2, 4, -12, -6, C.wallCream);
          fillWorld(15, 22, 5, 6, -13, -5, C.roofRed);
          fillWorld(17, 20, 7, 7, -12, -6, C.roofDark);

          // Warehouse front windows and door
          fillWorld(16, 16, 3, 3, -11, -11, C.window);
          fillWorld(16, 16, 3, 3, -9, -8, C.window);
          fillWorld(16, 16, 3, 3, -7, -7, C.window);
          fillWorld(16, 16, 4, 4, -11, -11, C.window);
          fillWorld(16, 16, 4, 4, -8, -8, C.window);
          fillWorld(16, 16, 2, 2, -9, -8, C.crateDark);

          // Side window
          fillWorld(18, 19, 3, 3, -12, -12, C.window);

          // House 1
          fillWorld(17, 21, 2, 3, 4, 8, C.wallBlue);
          fillWorld(16, 22, 4, 4, 3, 9, C.roofRed);
          fillWorld(17, 21, 5, 5, 4, 8, C.roofDark);
          fillWorld(17, 17, 3, 3, 5, 5, C.window);
          fillWorld(17, 17, 3, 3, 7, 7, C.window);
          fillWorld(17, 17, 2, 2, 6, 6, C.crateDark);

          // House 2
          fillWorld(22, 26, 2, 3, -3, 1, C.wallPink);
          fillWorld(21, 27, 4, 5, -4, 2, C.roofBlue);
          fillWorld(22, 26, 6, 6, -3, 1, C.roofDark);
          fillWorld(22, 22, 3, 3, -1, -1, C.window);
          fillWorld(22, 22, 3, 3, 0, 0, C.window);
          fillWorld(22, 22, 2, 2, -2, -2, C.crateDark);

          // Small dock office
          fillWorld(12, 14, 2, 3, 6, 9, C.wallCream);
          fillWorld(11, 15, 4, 4, 5, 10, C.roofRed);
          fillWorld(12, 14, 5, 5, 6, 9, C.roofDark);
          fillWorld(12, 12, 3, 3, 7, 8, C.window);
          fillWorld(12, 12, 2, 2, 8, 8, C.crateDark);
        }

        function buildLighthouse() {
          fillWorld(25, 27, 1, 2, -18, -16, C.stoneDark);
          fillWorld(25, 27, 3, 8, -18, -16, C.lighthouseWhite);

          for (let y = 4; y <= 8; y += 2) {
            fillWorld(25, 27, y, y, -18, -16, C.lighthouseRed);
          }

          fillWorld(24, 28, 9, 9, -19, -15, C.stoneDark);
          fillWorld(25, 27, 10, 10, -18, -16, C.lamp);
          fillWorld(25, 27, 11, 11, -18, -16, C.roofDark);
          fillWorld(26, 26, 12, 12, -17, -17, C.roofDark);

          fillWorld(26, 26, 3, 3, -18, -18, C.crateDark);
          fillWorld(26, 26, 5, 5, -18, -18, C.window);
          fillWorld(26, 26, 7, 7, -18, -18, C.window);
        }

        function buildDockDetails() {
          // Bollards
          for (let z = -30; z <= 30; z += 6) {
            if (Math.abs(z) > 4) addWorld(10, 2, z, C.metal);
          }

          // Dock lamps
          const lamps = [-27, -15, 15, 27];
          for (const z of lamps) {
            fillWorld(11, 11, 2, 4, z, z, C.metal);
            fillWorld(11, 11, 5, 5, z, z, C.lamp);
          }

          // Cargo around the quay
          addCrate(worldMap, 12, -4, 2);
          addCrate(worldMap, 14, 3, 2);
          addCrate(worldMap, 13, 13, 2);
          addCrate(worldMap, 12, 22, 2);

          addBarrel(worldMap, 13, -13);
          addBarrel(worldMap, 14, 11);
          addBarrel(worldMap, 13, 24);

          // Trees
          const trees = [
            [18, 18],
            [20, 22],
            [23, 17],
            [27, 24],
            [30, 28],
            [21, 27],
            [29, 20],
            [31, 31]
          ];

          for (const p of trees) addTree(worldMap, p[0], p[1]);

          // Clouds
          addCloud(worldMap, -32, -22);
          addCloud(worldMap, -20, 18);
          addCloud(worldMap, 18, -30);
          addCloud(worldMap, 30, 8);
          addCloud(worldMap, -24, 4);
          addCloud(worldMap, 6, 32);

          // A few tiny birds
          addBird(worldMap, -6, 16, -6);
          addBird(worldMap, -9, 17, 2);
          addBird(worldMap, -1, 15, 12);
        }

        // -----------------------------------------------------------------
        // Ship construction
        // -----------------------------------------------------------------
        function hullHalfWidth(z) {
          const r = 11;
          const v = 1 - (z * z) / (r * r);
          if (v <= 0) return 0;
          let w = Math.round(3.0 * Math.sqrt(v));
          if (w < 0) w = 0;
          return Math.min(3, w);
        }

        function addMast(z, top, yards, width) {
          // Mast pole
          fillShip(0, 0, 2, top, z, z, C.mast);

          for (let i = 0; i < yards.length; i++) {
            const y = yards[i];

            // Yardarm
            fillShip(-width, width, y, y, z, z, C.mast);

            // Square sail hanging below the yard
            const sailBottom = y - 3;
            const sailTop = y - 1;

            if (sailBottom >= 2) {
              const sw = Math.max(1, width - 1);
              fillShip(-sw, sw, sailBottom, sailTop, z, z, C.sail);
              fillShip(-sw, sw, sailTop, sailTop, z, z, C.sailShadow);
            }
          }
        }

        function addLineShip(x1, y1, z1, x2, y2, z2, c) {
          const steps = Math.max(
            Math.abs(x2 - x1),
            Math.abs(y2 - y1),
            Math.abs(z2 - z1)
          );

          if (steps === 0) {
            addShip(x1, y1, z1, c);
            return;
          }

          for (let i = 0; i <= steps; i++) {
            const t = i / steps;
            addShip(
              Math.round(x1 + (x2 - x1) * t),
              Math.round(y1 + (y2 - y1) * t),
              Math.round(z1 + (z2 - z1) * t),
              c
            );
          }
        }

        function buildShip() {
          // Rounded hull
          for (let z = -10; z <= 10; z++) {
            const halfW = hullHalfWidth(z);
            if (halfW <= 0) continue;

            // Underwater hull
            fillShip(-halfW, halfW, -3, -1, z, z, C.shipHullDark);

            // Waterline / upper hull
            fillShip(-halfW, halfW, 0, 0, z, z, C.shipHull);

            // Deck inside hull
            if (halfW > 1) {
              fillShip(-halfW + 1, halfW - 1, 1, 1, z, z, C.deck);
            } else {
              fillShip(0, 0, 1, 1, z, z, C.deck);
            }

            // Hull sides above deck line
            fillShip(halfW, halfW, 1, 1, z, z, C.shipHull);
            fillShip(-halfW, -halfW, 1, 1, z, z, C.shipHull);

            // Rail cap
            if (Math.abs(z) < 11) {
              fillShip(halfW, halfW, 2, 2, z, z, C.shipTrim);
              fillShip(-halfW, -halfW, 2, 2, z, z, C.shipTrim);
            }
          }

          // Stern cabin
          fillShip(-2, 2, 2, 3, -10, -7, C.deck);
          fillShip(-1, 1, 4, 4, -10, -8, C.shipHullDark);
          fillShip(-2, -2, 3, 3, -9, -8, C.window);
          fillShip(2, 2, 3, 3, -9, -8, C.window);
          fillShip(-1, 1, 3, 3, -10, -10, C.window);

          // Small forecastle
          fillShip(-1, 1, 2, 2, 8, 10, C.deck);
          fillShip(-1, 1, 3, 3, 9, 9, C.shipHullDark);

          // Bowsprit
          fillShip(0, 0, 2, 2, 11, 12, C.mast);
          fillShip(0, 0, 3, 3, 13, 13, C.mast);

          // Masts and square sails
          addMast(0, 17, [7, 11, 15], 5);   // Main mast
          addMast(5, 16, [6, 10, 13], 4);   // Foremast
          addMast(-5, 14, [5, 9, 12], 4);   // Mizzen mast

          // Simple rigging
          addLineShip(0, 16, 5, 0, 3, 13, C.rigging);
          addLineShip(0, 17, 0, 0, 3, -10, C.rigging);
          addLineShip(0, 14, -5, 0, 3, -10, C.rigging);
          addLineShip(-4, 2, 0, 0, 15, 0, C.rigging);
          addLineShip(4, 2, 0, 0, 15, 0, C.rigging);
          addLineShip(-3, 2, 5, 0, 14, 5, C.rigging);
          addLineShip(3, 2, 5, 0, 14, 5, C.rigging);

          // Flags
          fillShip(1, 3, 16, 17, 0, 0, C.flagBlue);
          fillShip(2, 3, 18, 18, 0, 0, C.flagRed);

          fillShip(0, 0, 4, 8, -10, -10, C.mast);
          fillShip(1, 3, 7, 8, -10, -10, C.flagRed);

          fillShip(1, 2, 3, 4, 11, 11, C.flagBlue);

          // Cargo on deck
          addCrate(shipMap, -2, 2, 2);
          addCrate(shipMap, -1, -2, 1);
          addBarrel(shipMap, 1, -6);
          addBarrel(shipMap, -2, -5);
          addBarrel(shipMap, 2, 3);
        }

        // -----------------------------------------------------------------
        // Build the world
        // -----------------------------------------------------------------
        const shipGroup = new THREE.Group();
        scene.add(shipGroup);

        buildWater();
        buildLand();
        buildDock();
        buildBuildings();
        buildLighthouse();
        buildDockDetails();
        buildShip();

        buildMap(shipMap, shipGroup);
        buildMap(worldMap, scene);

        // -----------------------------------------------------------------
        // Mouse / touch orbit controls
        // -----------------------------------------------------------------
        const controls = {
          theta: Math.PI * 0.72,
          phi: 1.08,
          radius: 68,
          target: new THREE.Vector3(0, 6, 0),
          dragging: false,
          panning: false,
          lastX: 0,
          lastY: 0
        };

        function updateCamera() {
          const t = controls.target;
          const sinP = Math.sin(controls.phi);

          camera.position.set(
            t.x + controls.radius * sinP * Math.cos(controls.theta),
            t.y + controls.radius * Math.cos(controls.phi),
            t.z + controls.radius * sinP * Math.sin(controls.theta)
          );

          camera.lookAt(t);
          camera.updateMatrixWorld();
        }

        updateCamera();

        const dom = renderer.domElement;

        dom.addEventListener("pointerdown", function (e) {
          controls.dragging = true;
          controls.panning = e.button === 2;
          controls.lastX = e.clientX;
          controls.lastY = e.clientY;

          try {
            dom.setPointerCapture(e.pointerId);
          } catch (err) {
            // Ignore if capture fails.
          }

          e.preventDefault();
        });

        dom.addEventListener("pointermove", function (e) {
          if (!controls.dragging) return;

          const dx = e.clientX - controls.lastX;
          const dy = e.clientY - controls.lastY;

          controls.lastX = e.clientX;
          controls.lastY = e.clientY;

          if (controls.panning) {
            const right = new THREE.Vector3();
            const up = new THREE.Vector3();
            const forward = new THREE.Vector3();

            camera.matrixWorld.extractBasis(right, up, forward);

            const scale = controls.radius * 0.0012;
            controls.target.addScaledVector(right, -dx * scale);
            controls.target.addScaledVector(up, dy * scale);
          } else {
            controls.theta -= dx * 0.005;
            controls.phi -= dy * 0.005;

            if (controls.phi < 0.18) controls.phi = 0.18;
            if (controls.phi > 1.54) controls.phi = 1.54;
          }

          updateCamera();
        });

        dom.addEventListener("pointerup", function (e) {
          controls.dragging = false;

          try {
            dom.releasePointerCapture(e.pointerId);
          } catch (err) {
            // Ignore release errors.
          }
        });

        dom.addEventListener("pointercancel", function () {
          controls.dragging = false;
        });

        dom.addEventListener("wheel", function (e) {
          e.preventDefault();

          controls.radius *= Math.exp(e.deltaY * 0.001);

          if (controls.radius < 18) controls.radius = 18;
          if (controls.radius > 150) controls.radius = 150;

          updateCamera();
        }, { passive: false });

        dom.addEventListener("contextmenu", function (e) {
          e.preventDefault();
        });

        window.addEventListener("resize", function () {
          camera.aspect = window.innerWidth / window.innerHeight;
          camera.updateProjectionMatrix();
          renderer.setSize(window.innerWidth, window.innerHeight);
        });

        // -----------------------------------------------------------------
        // Animation loop
        // -----------------------------------------------------------------
        let t0 = performance.now();

        function animate(now) {
          requestAnimationFrame(animate);

          const t = (now - t0) * 0.001;

          // Gentle bobbing at anchor
          shipGroup.position.y = Math.sin(t * 0.65) * 0.07;
          shipGroup.rotation.z = Math.sin(t * 0.45) * 0.008;
          shipGroup.rotation.x = Math.sin(t * 0.35) * 0.005;

          renderer.render(scene, camera);
        }

        requestAnimationFrame(animate);
      })();
    }
  </script>
</body>
</html>
```