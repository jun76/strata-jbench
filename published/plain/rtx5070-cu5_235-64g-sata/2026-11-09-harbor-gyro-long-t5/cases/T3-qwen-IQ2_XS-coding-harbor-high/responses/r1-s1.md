Save this as `harbor.html` and open it in Chrome.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>A sailing ship calling at a harbor — voxel scene</title>
  <style>
    html, body {
      margin: 0;
      height: 100%;
      overflow: hidden;
      background: #84c5f6;
    }
    canvas {
      display: block;
      cursor: grab;
    }
    #hud {
      position: fixed;
      left: 12px;
      top: 12px;
      color: white;
      font: 14px/1.45 system-ui;
      text-shadow: 0 1px 2px rgba(0, 0, 0, .35);
      pointer-events: none;
    }
    #error {
      position: fixed;
      left: 12px;
      top: 40px;
      color: white;
      font: 14px/1.45 system-ui;
    }
  </style>
</head>
<body>
  <div id="hud">A sailing ship calling at a harbor. Drag to orbit, scroll to zoom.</div>
  <div id="error"></div>
  <noscript>This page requires JavaScript.</noscript>

  <script type="module">
    const errorEl = document.getElementById('error');

    window.addEventListener('error', e => {
      errorEl.textContent = e.message || String(e);
    });

    import('https://cdn.jsdelivr.net/npm/three@0.164.0/build/three.module.js')
      .then(THREE => start(THREE))
      .catch(e => {
        errorEl.textContent = 'Failed to load Three.js from CDN: ' + String(e.message || e);
      });

    function start(THREE) {
      try {
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x78c7f6);
        scene.fog = new THREE.Fog(0x78c7f6, 36, 90);

        const camera = new THREE.PerspectiveCamera(
          42,
          window.innerWidth / window.innerHeight,
          0.1,
          250
        );

        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.outputColorSpace = THREE.SRGBColorSpace;
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.05;
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        document.body.appendChild(renderer.domElement);

        const hemisphere = new THREE.HemisphereLight(0xd4ecf4, 0x2d3941, 0.72);
        scene.add(hemisphere);

        const sun = new THREE.DirectionalLight(0xffe9b9, 0.70);
        sun.position.set(18, 28, -10);
        sun.castShadow = true;
        sun.shadow.mapSize.set(1024, 1024);
        sun.shadow.camera.left = -34;
        sun.shadow.camera.right = 34;
        sun.shadow.camera.top = 34;
        sun.shadow.camera.bottom = -34;
        sun.shadow.camera.near = 1;
        sun.shadow.camera.far = 120;
        sun.shadow.bias = -0.0004;
        scene.add(sun);

        const voxelGeo = new THREE.BoxGeometry(1, 1, 1);
        const materialCache = new Map();

        function getMaterial(color, emissive = 0) {
          const key = String(color) + ':' + emissive;
          if (!materialCache.has(key)) {
            materialCache.set(
              key,
              new THREE.MeshLambertMaterial({
                color,
                emissive,
                flatShading: true
              })
            );
          }
          return materialCache.get(key);
        }

        function addBlock(parent, x, y, z, color, cast = true, receive = false, emissive = 0) {
          const mesh = new THREE.Mesh(voxelGeo, getMaterial(color, emissive));
          mesh.position.set(x, y, z);
          mesh.castShadow = cast;
          mesh.receiveShadow = receive;
          parent.add(mesh);
          return mesh;
        }

        function addRect(parent, x0, x1, z0, z1, y, color, cast = true, receive = false) {
          for (let x = x0; x <= x1; x++) {
            for (let z = z0; z <= z1; z++) {
              addBlock(parent, x, y, z, color, cast, receive);
            }
          }
        }

        function makeBuilding(parent, x0, x1, z0, z1, yStart, height, color, roofColor) {
          for (let x = x0; x <= x1; x++) {
            for (let z = z0; z <= z1; z++) {
              for (let y = yStart; y <= height; y++) {
                addBlock(
                  parent,
                  x,
                  y,
                  z,
                  y === height ? roofColor : color,
                  true,
                  true
                );
              }
            }
          }
        }

        const harbor = new THREE.Group();
        scene.add(harbor);

        // Quay top
        addRect(harbor, 12, 24, -10, 20, 1, 0x8e8f95, false, true);

        // Land behind the harbor
        addRect(harbor, 12, 24, 21, 30, 1, 0x46834d, false, true);

        // Quay edge posts
        for (let z = -10; z <= 20; z += 4) {
          addBlock(harbor, 11, 2, z, 0x5b3f28, true, true);
          addBlock(harbor, 11, 3, z, 0x412d1d, true, false);
        }

        for (let x = 13; x <= 23; x += 3) {
          addBlock(harbor, x, -11, 2, 0x5b3f28, true, true);
          addBlock(harbor, x, -11, 3, 0x412d1d, true, false);
        }

        // Buildings on the town side
        makeBuilding(harbor, 20, 24, 25, 29, 2, 4, 0xa44747, 0x663033);
        makeBuilding(harbor, 16, 18, 25, 27, 2, 3, 0x567a9e, 0x37505d);
        makeBuilding(harbor, 22, 24, 21, 23, 2, 3, 0x8b724c, 0x5e4d31);

        // Simple front windows
        for (let x = 20; x <= 24; x += 2) {
          addBlock(harbor, x, 3, 24, 0xf4f1b4, false, false);
        }
        for (let x = 16; x <= 18; x += 2) {
          addBlock(harbor, x, 3, 24, 0xf4f1b4, false, false);
        }

        // Warehouse door
        addBlock(harbor, 22, 2, 24, 0x2e3f51, false, false);

        // Lighthouse
        for (let y = 2; y <= 7; y++) {
          const color = (y % 2 === 0) ? 0xf2f4f5 : 0xd23635;
          addBlock(harbor, 14, y, 30, color, true, true);
        }

        addBlock(harbor, 14, 8, 30, 0xffd14a, false, false, 0xffd14a);

        const lampLight = new THREE.PointLight(0xffd25a, 1.2, 44);
        lampLight.position.set(14, 8, 30);
        scene.add(lampLight);

        // Harbor crane
        const craneColor = 0x6f4b2e;
        for (let y = 2; y <= 5; y++) {
          addBlock(harbor, 20, y, -6, craneColor, true, true);
        }
        for (let z = -7; z <= -3; z++) {
          addBlock(harbor, 20, 5, z, craneColor, true, false);
        }
        addBlock(harbor, 20, 4, -6, 0x916441, true, true);

        // Cargo on the quay
        function addCrate(parent, x, z, color) {
          addBlock(parent, x, 2, z, color, true, true);
          addBlock(parent, x, 3, z, color, true, true);
        }

        function addBarrel(parent, x, z, color) {
          addBlock(parent, x, 2, z, color, true, true);
          addBlock(parent, x, 3, z, color, true, true);
        }

        addCrate(harbor, 14, -8, 0x8c6742);
        addCrate(harbor, 15, -7, 0x775134);
        addCrate(harbor, 16, -6, 0x757332);
        addCrate(harbor, 15, -4, 0x8a613f);
        addCrate(harbor, 17, -3, 0x824932);
        addCrate(harbor, 14, -3, 0x6d5a32);

        addBarrel(harbor, 13, -6, 0x6b4e35);
        addBarrel(harbor, 18, -7, 0x685243);

        // Bollard and mooring line from the ship
        addBlock(harbor, 12, 2, 0, 0x423427, true, true);
        for (let x = -2; x <= 11; x++) {
          addBlock(harbor, x, 3, 0, 0x4d4331, false, false);
        }

        // Buoys
        addBlock(harbor, 6, 2, -20, 0xc14040, true, true);
        addBlock(harbor, 6, 3, -20, 0xc14040, false, false);

        addBlock(harbor, -18, 2, 14, 0x2c8c4e, true, true);
        addBlock(harbor, -18, 3, 14, 0x2c8c4e, false, false);

        // Sailing ship
        const shipGroup = new THREE.Group();
        shipGroup.position.set(-6, 0, 0);
        scene.add(shipGroup);

        const sailGroup = new THREE.Group();
        shipGroup.add(sailGroup);

        const flagGroup = new THREE.Group();
        flagGroup.position.set(-8, 5, 0);
        shipGroup.add(flagGroup);

        function addShip(x, y, z, color, cast = true, receive = false) {
          return addBlock(shipGroup, x, y, z, color, cast, receive);
        }

        // Hull
        addRect(shipGroup, -8, -1, -3, 3, 0, 0x5c3e25, true, true);
        addRect(shipGroup, -8, -1, -3, 3, 1, 0x6b4930, true, true);
        addRect(shipGroup, -8, -1, -3, 3, 2, 0x735233, true, true);
        addRect(shipGroup, -8, -1, -3, 3, 3, 0x8b5d36, true, true);

        // Bow taper
        for (let y = 0; y <= 2; y++) {
          for (let x = 0; x <= 4; x++) {
            const halfWidth = Math.max(0, 2 - x);
            for (let z = -halfWidth; z <= halfWidth; z++) {
              addShip(x, y, z, y === 2 ? 0x735233 : 0x6b4930);
            }
          }
        }

        addShip(4, 1, 0, 0x735233);
        addShip(4, 2, 0, 0x735233);

        // Bowsprit
        for (let x = 0; x <= 4; x++) {
          addShip(x, 4, 0, 0x543c2a);
        }

        // Stern cabin
        addRect(shipGroup, -8, -7, -2, 2, 4, 0x4d301f, true, false);

        addBlock(shipGroup, -8, 4, -2, 0xf7f1bd, false, false);
        addBlock(shipGroup, -8, 4, 2, 0xf7f1bd, false, false);

        // Flag
        addBlock(flagGroup, 0, 0, 0, 0x493324, false, false);
        addBlock(flagGroup, 0, 1, 0, 0x493324, false, false);
        addBlock(flagGroup, 1, 1, 0, 0xd64a3e, false, false);
        addBlock(flagGroup, 2, 1, 0, 0xd64a3e, false, false);

        // Masts, yards, sails
        function addMast(x, height, sailColor = 0xf2f2ef) {
          for (let y = 3; y <= height; y++) {
            addShip(x, y, 0, 0x553d2d, true, false);
          }

          for (let z = -3; z <= 3; z++) {
            addShip(x, height - 1, z, 0x4a3426, true, false);
          }

          const sailTopY = height - 1;
          const sailBottomY = height - 4;

          for (let y = sailBottomY; y <= sailTopY; y++) {
            for (let z = -3; z <= 3; z++) {
              addBlock(sailGroup, x + 1, y, z, sailColor, false, false);
            }
          }
        }

        addMast(-7, 10, 0xf2f2ef);
        addMast(-4, 12, 0xf2f2ef);
        addMast(-1, 9, 0xf2f2ef);

        // Cargo on deck
        const cargo = [
          { x: -6, z: -1, color: 0x875e3b, h: 2 },
          { x: -5, z: 1, color: 0x807134, h: 2 },
          { x: -4, z: -2, color: 0x724a31, h: 2 },
          { x: -3, z: 0, color: 0x8d5e3b, h: 2 },
          { x: -2, z: 2, color: 0x696335, h: 1 },
          { x: -2, z: -2, color: 0x6f4c30, h: 1 },
          { x: -1, z: -1, color: 0x8a6d42, h: 1 }
        ];

        for (const c of cargo) {
          for (let dy = 0; dy < c.h; dy++) {
            addShip(c.x, 4 + dy, c.z, c.color, true, false);
          }
        }

        // Portholes
        addBlock(shipGroup, -7, 2, -3, 0x273338, false, false);
        addBlock(shipGroup, -7, 2, 3, 0x273338, false, false);

        // Seagulls
        const seagulls = [];

        function makeSeagull(x, y, z) {
          const g = new THREE.Group();
          g.position.set(x, y, z);
          scene.add(g);

          const body = addBlock(g, 0, 0, 0, 0xf4f4f3, false, false);
          const head = addBlock(g, 2, 0, 0, 0xf4f4f3, false, false);
          const tail = addBlock(g, -2, 0, 0, 0xf4f4f3, false, false);
          const wing1 = addBlock(g, 1, 1, 0, 0xf4f4f3, false, false);
          const wing2 = addBlock(g, -1, 1, 0, 0xf4f4f3, false, false);

          seagulls.push({
            g,
            wing1,
            wing2,
            x,
            y,
            z,
            phase: Math.random() * Math.PI * 2,
            speed: 0.5 + Math.random() * 0.3
          });
        }

        makeSeagull(4, 20, -8);
        makeSeagull(-8, 22, 6);
        makeSeagull(10, 21, -4);

        // Clouds
        const clouds = [];

        function makeCloud(x, y, z, size) {
          const g = new THREE.Group();
          g.position.set(x, y, z);
          scene.add(g);

          for (let i = 0; i < size; i++) {
            addBlock(
              g,
              (i % 3) - 1,
              -i % 2,
              Math.floor(i / 2),
              0xf7f7fa,
              false,
              false
            );
          }

          clouds.push({
            g,
            speed: 0.3 + Math.random() * 0.2
          });
        }

        makeCloud(-18, 25, -18, 8);
        makeCloud(12, 27, 16, 9);
        makeCloud(-4, 28, -26, 6);

        // Voxel water
        const waterMaterial = new THREE.MeshLambertMaterial({
          color: 0xffffff,
          flatShading: true
        });

        const waterCells = [];

        const waterMinX = -30;
        const waterMaxX = 30;
        const waterMinZ = -30;
        const waterMaxZ = 20;

        for (let x = waterMinX; x <= waterMaxX; x++) {
          for (let z = waterMinZ; z <= waterMaxZ; z++) {
            const color = new THREE.Color();

            if (z < 0 && x > -5) {
              color.setHSL(0.54, 0.50, 0.34);
            } else {
              color.setHSL(0.56, 0.55, 0.30 + Math.random() * 0.08);
            }

            waterCells.push({ x, z, color });
          }
        }

        const waterMesh = new THREE.InstancedMesh(voxelGeo, waterMaterial, waterCells.length);
        waterMesh.receiveShadow = true;
        scene.add(waterMesh);

        const waterDummy = new THREE.Object3D();

        for (let i = 0; i < waterCells.length; i++) {
          const cell = waterCells[i];

          waterDummy.position.set(cell.x, -0.5, cell.z);
          waterDummy.updateMatrix();
          waterMesh.setMatrixAt(i, waterDummy.matrix);
          waterMesh.setColorAt(i, cell.color);
        }

        waterMesh.instanceMatrix.needsUpdate = true;
        waterMesh.instanceColor.needsUpdate = true;

        function animateWater(t) {
          for (let i = 0; i < waterCells.length; i++) {
            const cell = waterCells[i];

            const wave =
              Math.sin((cell.x + cell.z) * 0.32 + t * 1.2) * 0.20 +
              Math.sin((cell.x - cell.z) * 0.48 + t * 1.8) * 0.08;

            waterDummy.position.set(cell.x, -0.5 + wave, cell.z);
            waterDummy.updateMatrix();
            waterMesh.setMatrixAt(i, waterDummy.matrix);
          }

          waterMesh.instanceMatrix.needsUpdate = true;
        }

        // Mouse orbit controls
        function clamp(value, min, max) {
          return Math.max(min, Math.min(max, value));
        }

        const controls = {
          target: new THREE.Vector3(0, 4, 0),
          theta: -0.75,
          phi: 1.10,
          radius: 34,
          minRadius: 14,
          maxRadius: 70,
          autoRotate: true
        };

        let pointerDown = false;
        let lastX = 0;
        let lastY = 0;

        function updateCamera() {
          const x =
            controls.target.x +
            controls.radius * Math.sin(controls.phi) * Math.sin(controls.theta);

          const y =
            controls.target.y +
            controls.radius * Math.cos(controls.phi);

          const z =
            controls.target.z +
            controls.radius * Math.sin(controls.phi) * Math.cos(controls.theta);

          camera.position.set(x, y, z);
          camera.lookAt(controls.target);
        }

        const canvas = renderer.domElement;
        canvas.style.touchAction = 'none';

        canvas.addEventListener('pointerdown', e => {
          pointerDown = true;
          lastX = e.clientX;
          lastY = e.clientY;
          controls.autoRotate = false;
        });

        window.addEventListener('pointermove', e => {
          if (!pointerDown) return;

          const dx = e.clientX - lastX;
          const dy = e.clientY - lastY;
          lastX = e.clientX;
          lastY = e.clientY;

          controls.theta -= dx * 0.010;
          controls.phi = clamp(controls.phi + dy * 0.010, 0.18, Math.PI - 0.18);
        });

        window.addEventListener('pointerup', () => {
          pointerDown = false;
          controls.autoRotate = true;
        });

        canvas.addEventListener(
          'wheel',
          e => {
            controls.radius *= Math.exp(e.deltaY * 0.0015);
            controls.radius = clamp(controls.radius, controls.minRadius, controls.maxRadius);
          },
          { passive: true }
        );

        window.addEventListener('resize', () => {
          camera.aspect = window.innerWidth / window.innerHeight;
          camera.updateProjectionMatrix();
          renderer.setSize(window.innerWidth, window.innerHeight);
        });

        let lastTime = performance.now();

        function loop(now) {
          try {
            const dt = Math.max(0, (now - lastTime) / 1000);
            lastTime = now;
            const t = now / 1000;

            if (controls.autoRotate) {
              controls.theta += dt * 0.05;
            }

            updateCamera();

            animateWater(t);

            shipGroup.position.y = Math.sin(t * 1.2) * 0.18;
            shipGroup.rotation.z = Math.sin(t * 1.3) * 0.018;
            shipGroup.rotation.x = Math.sin(t * 1.7) * 0.008;

            sailGroup.rotation.z = Math.sin(t * 2.2) * 0.04;

            flagGroup.position.y = 5 + Math.sin(t * 2.3) * 0.12;

            for (const s of seagulls) {
              s.g.position.x = s.x + Math.sin(t * s.speed + s.phase) * 4;
              s.g.position.y = s.y + Math.sin(t * 2.0 + s.phase) * 0.35;

              const flap = Math.sin(t * 3 + s.phase) * 0.35;
              s.wing1.rotation.z = flap;
              s.wing2.rotation.z = -flap;
            }

            for (const c of clouds) {
              c.g.position.x += dt * c.speed;

              if (c.g.position.x > 35) {
                c.g.position.x = -35;
              }
            }

            renderer.render(scene, camera);
            requestAnimationFrame(loop);
          } catch (e) {
            errorEl.textContent = 'Render error: ' + String(e.message || e);
          }
        }

        updateCamera();
        requestAnimationFrame(loop);
      } catch (e) {
        errorEl.textContent = 'Scene error: ' + String(e.message || e);
      }
    }
  </script>
</body>
</html>
```