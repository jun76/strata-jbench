Paste this into a file such as `voxel-harbor.html`, then open it in Chrome.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Voxel Harbor — Sailing Ship</title>
  <style>
    html, body {
      margin: 0;
      width: 100%;
      height: 100%;
      overflow: hidden;
      background: linear-gradient(to bottom, #dff6ff 0%, #9cd6ee 45%, #cfe7dc 100%);
    }
    canvas {
      display: block;
      touch-action: none;
    }
    #title, #hint {
      position: absolute;
      color: #0b3a5c;
      font: 13px/1.4 sans-serif;
      background: rgba(255, 255, 255, 0.55);
      padding: 6px 8px;
      border-radius: 6px;
      pointer-events: none;
    }
    #title {
      left: 12px;
      top: 12px;
      font-size: 15px;
    }
    #hint {
      left: 12px;
      bottom: 12px;
    }
  </style>
</head>
<body>
  <div id="title">A sailing ship calling at a harbor</div>
  <div id="hint">Drag: orbit • Wheel: zoom • Right-drag or Shift-drag: pan</div>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script>
    (function () {
      if (!window.THREE) {
        document.body.innerHTML =
          "Could not load Three.js from the CDN. Please check your internet connection.";
        return;
      }

      const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
      renderer.setSize(window.innerWidth, window.innerHeight);
      renderer.setClearColor(0x000000, 0);
      renderer.shadowMap.enabled = true;
      renderer.shadowMap.type = THREE.PCFSoftShadowMap;
      document.body.appendChild(renderer.domElement);

      const scene = new THREE.Scene();
      scene.fog = new THREE.Fog(0x9cd6ee, 65, 135);

      const camera = new THREE.PerspectiveCamera(
        45,
        window.innerWidth / window.innerHeight,
        0.1,
        1000
      );

      const controls = {
        target: new THREE.Vector3(-1, 7, 3),
        theta: 1.12,
        phi: 1.04,
        radius: 54,
        dragging: false,
        panning: false,
        lastX: 0,
        lastY: 0
      };

      function updateCamera() {
        const sinPhi = Math.sin(controls.phi);
        camera.position.set(
          controls.target.x + controls.radius * sinPhi * Math.sin(controls.theta),
          controls.target.y + controls.radius * Math.cos(controls.phi),
          controls.target.z + controls.radius * sinPhi * Math.cos(controls.theta)
        );
        camera.lookAt(controls.target);
      }

      updateCamera();

      const hemi = new THREE.HemisphereLight(0xdff6ff, 0x3d3026, 0.85);
      scene.add(hemi);

      const sun = new THREE.DirectionalLight(0xfff2d0, 1.05);
      sun.position.set(28, 36, 18);
      sun.castShadow = true;
      sun.shadow.mapSize.set(1024, 1024);
      sun.shadow.camera.near = 1;
      sun.shadow.camera.far = 150;
      sun.shadow.camera.left = -45;
      sun.shadow.camera.right = 45;
      sun.shadow.camera.top = 45;
      sun.shadow.camera.bottom = -45;
      sun.shadow.bias = -0.0006;
      scene.add(sun);
      scene.add(sun.target);
      sun.target.position.set(0, 2, 3);

      const beaconLight = new THREE.PointLight(0xffcf66, 1.3, 30, 1.8);
      beaconLight.position.set(-22, 11.2, 0);
      scene.add(beaconLight);

      const staticVoxels = [];
      const waterVoxels = [];
      const shipVoxels = [];

      const COLORS = {
        seaDeep: 0x0d294b,
        seaTop: 0x2d77a7,
        seaLight: 0x4aa8c6,
        seaDark: 0x19577c,

        quayStone: 0x9a9888,
        quayAlt: 0x858379,
        road: 0x77756c,
        roadAlt: 0x67655e,
        grass: 0x678e47,
        grassAlt: 0x78a258,
        landBase: 0x423022,

        brick: 0xa95345,
        brickDark: 0x804138,
        warehouse: 0x536b78,
        roof: 0x394250,
        door: 0x312118,
        window: 0x8fd1df,

        wood: 0x8b5a36,
        woodDark: 0x4c301d,
        deck: 0xc9a96e,
        hullStripe: 0xb7473e,
        sail: 0xf0e8d2,
        sailShadow: 0xd9cfb8,
        mast: 0x5d3e22,
        flag: 0xa33025,

        crate: 0xb0844b,
        crateAlt: 0x8f6939,
        barrel: 0x6b4a28,
        crane: 0x8d4a3b,
        black: 0x1d1d1d,
        lamp: 0xf0bd4a,

        stone: 0x8e8d82,
        stoneAlt: 0x77766e,
        beaconWhite: 0xebe5d6,
        beaconRed: 0xc44f45,
        lighthouseCap: 0x2f2f2f
      };

      function push(arr, x, y, z, sx = 1, sy = 1, sz = 1, color = 0xffffff) {
        arr.push({ x, y, z, sx, sy, sz, color });
      }

      function rectXZ(arr, x0, x1, z0, z1, y, color) {
        for (let x = x0; x <= x1; x++) {
          for (let z = z0; z <= z1; z++) {
            push(arr, x, y, z, 1, 1, 1, color);
          }
        }
      }

      function boxXYZ(arr, x0, x1, y0, y1, z0, z1, color) {
        for (let x = x0; x <= x1; x++) {
          for (let y = y0; y <= y1; y++) {
            for (let z = z0; z <= z1; z++) {
              push(arr, x, y, z, 1, 1, 1, color);
            }
          }
        }
      }

      function panelZ(arr, x0, x1, y0, y1, z, color) {
        for (let x = x0; x <= x1; x++) {
          for (let y = y0; y <= y1; y++) {
            push(arr, x, y, z, 1, 1, 1, color);
          }
        }
      }

      function buildWater() {
        const arr = waterVoxels;

        for (let x = -24; x <= 15; x++) {
          for (let z = -24; z <= 5; z++) {
            if (x >= -24 && x <= -16 && z >= -2 && z <= 2) continue;

            const r = Math.random();
            let col = COLORS.seaTop;
            if (r < 0.13) col = COLORS.seaLight;
            else if (r > 0.89) col = COLORS.seaDark;

            push(arr, x, 0, z, 1, 1, 1, col);
          }
        }

        push(staticVoxels, -4.5, -1, -9.5, 41, 2, 31, COLORS.seaDeep);
        push(staticVoxels, 0, -1, 15, 45, 2, 15, COLORS.landBase);
      }

      function buildShore() {
        const arr = staticVoxels;

        for (let x = -18; x <= 18; x++) {
          for (let z = 6; z <= 7; z++) {
            const col = ((x + z) & 1) ? COLORS.quayStone : COLORS.quayAlt;
            push(arr, x, 0, z, 1, 1, 1, col);
          }
        }

        for (let x = -22; x <= 22; x++) {
          for (let z = 8; z <= 9; z++) {
            const col = ((x + z) & 1) ? COLORS.road : COLORS.roadAlt;
            push(arr, x, 0, z, 1, 1, 1, col);
          }
        }

        for (let x = -22; x <= 22; x++) {
          for (let z = 10; z <= 22; z++) {
            let col = COLORS.grass;
            if (((x * 3 + z * 7) & 7) === 0) col = COLORS.grassAlt;
            push(arr, x, 0, z, 1, 1, 1, col);
          }
        }
      }

      function buildBreakwaterLighthouse() {
        const arr = staticVoxels;

        for (let x = -24; x <= -16; x++) {
          for (let z = -2; z <= 2; z++) {
            const col = ((x + z) & 1) ? COLORS.stone : COLORS.stoneAlt;
            push(arr, x, 0, z, 1, 1, 1, col);
          }
        }

        for (let y = 1; y <= 9; y++) {
          for (let x = -23; x <= -21; x++) {
            for (let z = -1; z <= 1; z++) {
              const col = (y % 2 === 0) ? COLORS.beaconWhite : COLORS.beaconRed;
              push(arr, x, y, z, 1, 1, 1, col);
            }
          }
        }

        rectXZ(arr, -23, -21, -1, 1, 10, COLORS.lighthouseCap);
        push(arr, -22, 11, 0, 1, 1, 1, COLORS.lamp);
      }

      function buildBuildings() {
        const arr = staticVoxels;

        for (let x = 8; x <= 14; x++) {
          for (let y = 1; y <= 3; y++) {
            for (let z = 10; z <= 14; z++) {
              let col = COLORS.brick;
              if (((x + y + z) & 5) === 0) col = COLORS.brickDark;
              push(arr, x, y, z, 1, 1, 1, col);
            }
          }
        }

        for (let z = 10; z <= 14; z++) {
          const top = 4 + Math.max(0, 2 - Math.abs(z - 12));
          for (let x = 8; x <= 14; x++) {
            for (let y = 4; y <= top; y++) {
              push(arr, x, y, z, 1, 1, 1, COLORS.roof);
            }
          }
        }

        panelZ(arr, 10, 11, 1, 2, 9, COLORS.door);
        panelZ(arr, 9, 9, 2, 2, 9, COLORS.window);
        panelZ(arr, 13, 13, 2, 2, 9, COLORS.window);

        for (let x = -14; x <= -9; x++) {
          for (let y = 1; y <= 3; y++) {
            for (let z = 10; z <= 13; z++) {
              let col = COLORS.warehouse;
              if (((x + y + z) & 5) === 0) col = COLORS.black;
              push(arr, x, y, z, 1, 1, 1, col);
            }
          }
        }

        rectXZ(arr, -14, -9, 10, 13, 4, COLORS.roof);
        rectXZ(arr, -13, -10, 11, 12, 5, COLORS.roof);

        panelZ(arr, -12, -11, 1, 2, 9, COLORS.door);
        panelZ(arr, -13, -13, 2, 2, 9, COLORS.window);
        panelZ(arr, -10, -10, 2, 2, 9, COLORS.window);

        boxXYZ(arr, -3, 1, 1, 2, 11, 12, COLORS.warehouse);
        rectXZ(arr, -3, 1, 11, 12, 3, COLORS.flag);
      }

      function buildDockFurniture() {
        const arr = staticVoxels;

        for (let x = -15; x <= 15; x += 5) {
          if (x === 0) continue;
          push(arr, x, 1, 6, 0.75, 1, 0.75, COLORS.black);
        }

        const crates = [
          [-14, 7], [-12, 8], [-10, 7], [-7, 8], [-5, 7],
          [-3, 8], [10, 7], [12, 8], [14, 7], [16, 8]
        ];

        crates.forEach((p, i) => {
          const c = (i % 2) ? COLORS.crate : COLORS.crateAlt;
          push(arr, p[0], 1, p[1], 1, 1, 1, c);
          if (i % 3 === 0) {
            push(arr, p[0], 2, p[1], 1, 1, 1, (i % 2) ? COLORS.crateAlt : COLORS.crate);
          }
        });

        const barrels = [[-13, 8], [-11, 7], [11, 8], [13, 7]];
        barrels.forEach((p) => {
          push(arr, p[0], 1, p[1], 0.75, 1, 0.75, COLORS.barrel);
        });

        const lamps = [-12, -6, 6, 12];
        lamps.forEach((x) => {
          for (let y = 1; y <= 3; y++) {
            push(arr, x, y, 7, 0.55, 1, 0.55, COLORS.black);
          }
          push(arr, x, 4, 7, 1, 1, 1, COLORS.lamp);
        });

        push(arr, -18, 1, -18, 0.8, 1, 0.8, COLORS.flag);
        push(arr, 12, 1, -18, 0.8, 1, 0.8, COLORS.lamp);

        boxXYZ(arr, -10, -7, 1, 1, -10, -9, COLORS.woodDark);
        boxXYZ(arr, -9, -8, 2, 2, -10, -9, COLORS.deck);
        push(arr, -9, 2, -9, 1, 1, 1, COLORS.sail);
      }

      function buildCrane() {
        const arr = staticVoxels;

        boxXYZ(arr, -1, 1, 1, 2, 6, 7, COLORS.crateAlt);

        for (let y = 3; y <= 5; y++) {
          push(arr, 0, y, 6, 1, 1, 1, COLORS.crane);
        }

        rectXZ(arr, -4, 4, 6, 6, 6, COLORS.crane);
        push(arr, 5, 6, 6, 2, 2, 1, COLORS.stone);

        for (let y = 2; y <= 5; y++) {
          push(arr, 2, y, 6, 0.25, 1, 0.25, COLORS.black);
        }

        push(arr, 2, 1, 6, 1, 1, 1, COLORS.crate);
      }

      function buildShip() {
        const arr = shipVoxels;

        rectXZ(arr, -11, 7, -2, 2, 1, COLORS.woodDark);
        rectXZ(arr, -12, 8, -2, 2, 2, COLORS.wood);
        rectXZ(arr, -12, 8, -2, 2, 3, COLORS.hullStripe);

        rectXZ(arr, -12, 8, 2, 2, 4, COLORS.deck);
        rectXZ(arr, -12, 8, -2, -2, 4, COLORS.deck);
        rectXZ(arr, -11, 7, -1, 1, 4, COLORS.deck);

        rectXZ(arr, -9, 4, 2, 2, 5, COLORS.deck);
        rectXZ(arr, -9, 4, -2, -2, 5, COLORS.deck);

        boxXYZ(arr, -14, -10, 5, 7, -2, 2, COLORS.woodDark);
        rectXZ(arr, -14, -10, -2, 2, 8, COLORS.wood);

        boxXYZ(arr, 5, 7, 5, 6, -2, 2, COLORS.woodDark);
        rectXZ(arr, 5, 7, -2, 2, 7, COLORS.wood);

        push(arr, 9, 4, 0, 1, 1, 1, COLORS.deck);

        panelZ(arr, -13, -11, 6, 6, 3, COLORS.window);
        panelZ(arr, -13, -11, 6, 6, -3, COLORS.window);
        panelZ(arr, 6, 6, 5, 5, 3, COLORS.window);
        panelZ(arr, 6, 6, 5, 5, -3, COLORS.window);

        const masts = [4, -2, -9];
        for (const m of masts) {
          for (let y = 5; y <= 6; y++) push(arr, m, y, 0, 1, 1, 1, COLORS.mast);
          for (let y = 14; y <= 15; y++) push(arr, m, y, 0, 1, 1, 1, COLORS.mast);
        }

        panelZ(arr, -7, 0, 8, 10, 1, COLORS.sail);
        panelZ(arr, -7, 0, 8, 10, -1, COLORS.sailShadow);
        panelZ(arr, -7, 0, 11, 11, 1, COLORS.mast);
        panelZ(arr, -6, 0, 12, 13, 1, COLORS.sail);
        panelZ(arr, -6, 0, 12, 13, -1, COLORS.sailShadow);
        panelZ(arr, -6, 0, 14, 14, 1, COLORS.mast);

        panelZ(arr, 2, 5, 9, 11, 1, COLORS.sail);
        panelZ(arr, 2, 5, 9, 11, -1, COLORS.sailShadow);
        panelZ(arr, 2, 5, 12, 12, 1, COLORS.mast);
        panelZ(arr, 2, 4, 13, 14, 1, COLORS.sail);
        panelZ(arr, 2, 4, 13, 14, -1, COLORS.sailShadow);
        panelZ(arr, 2, 4, 15, 15, 1, COLORS.mast);

        panelZ(arr, -11, -8, 9, 11, 1, COLORS.sail);
        panelZ(arr, -11, -8, 9, 11, -1, COLORS.sailShadow);
        panelZ(arr, -11, -8, 12, 12, 1, COLORS.mast);
        panelZ(arr, -10, -9, 13, 14, 1, COLORS.sail);
        panelZ(arr, -10, -9, 13, 14, -1, COLORS.sailShadow);
        panelZ(arr, -10, -9, 15, 15, 1, COLORS.mast);

        push(arr, 3, 16, 0, 1, 1, 1, COLORS.flag);
        push(arr, -3, 16, 0, 1, 1, 1, COLORS.flag);
        push(arr, -10, 16, 0, 1, 1, 1, COLORS.flag);

        push(arr, -4, 5, 1, 1, 1, 1, COLORS.crate);
        push(arr, 0, 5, 1, 1, 1, 1, COLORS.crateAlt);
        push(arr, 4, 5, 1, 1, 1, 1, COLORS.crate);
      }

      buildWater();
      buildShore();
      buildBreakwaterLighthouse();
      buildBuildings();
      buildDockFurniture();
      buildCrane();
      buildShip();

      const voxelMaterial = new THREE.MeshStandardMaterial({
        roughness: 0.85,
        metalness: 0.02,
        flatShading: true
      });

      const waterMaterial = new THREE.MeshStandardMaterial({
        roughness: 0.35,
        metalness: 0.05,
        flatShading: true
      });

      function makeInstancedMesh(arr, material) {
        if (!arr.length) return null;

        const geometry = new THREE.BoxGeometry(1, 1, 1);
        const mesh = new THREE.InstancedMesh(geometry, material, arr.length);

        const m = new THREE.Matrix4();
        const q = new THREE.Quaternion();
        const p = new THREE.Vector3();
        const s = new THREE.Vector3();
        const c = new THREE.Color();

        for (let i = 0; i < arr.length; i++) {
          const v = arr[i];
          p.set(v.x, v.y, v.z);
          s.set(v.sx, v.sy, v.sz);
          m.compose(p, q, s);
          mesh.setMatrixAt(i, m);
          mesh.setColorAt(i, c.setHex(v.color));
        }

        mesh.instanceMatrix.needsUpdate = true;
        if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
        mesh.castShadow = true;
        mesh.receiveShadow = true;
        return mesh;
      }

      const staticMesh = makeInstancedMesh(staticVoxels, voxelMaterial);
      const waterMesh = makeInstancedMesh(waterVoxels, waterMaterial);
      const shipMesh = makeInstancedMesh(shipVoxels, voxelMaterial);

      if (staticMesh) scene.add(staticMesh);
      if (waterMesh) scene.add(waterMesh);

      const shipGroup = new THREE.Group();
      shipGroup.position.set(-1, 0.065, 3);
      if (shipMesh) shipGroup.add(shipMesh);
      scene.add(shipGroup);

      const dom = renderer.domElement;

      dom.addEventListener("contextmenu", (e) => e.preventDefault());

      dom.addEventListener("pointerdown", (e) => {
        controls.dragging = true;
        controls.panning = (e.button === 2 || e.button === 1 || e.shiftKey);
        controls.lastX = e.clientX;
        controls.lastY = e.clientY;
        dom.setPointerCapture(e.pointerId);
        e.preventDefault();
      });

      window.addEventListener("pointerup", () => {
        controls.dragging = false;
        controls.panning = false;
      });

      dom.addEventListener("pointermove", (e) => {
        if (!controls.dragging) return;

        const dx = e.clientX - controls.lastX;
        const dy = e.clientY - controls.lastY;
        controls.lastX = e.clientX;
        controls.lastY = e.clientY;

        if (controls.panning) {
          const factor = controls.radius * 0.0011;
          const camDir = new THREE.Vector3().subVectors(controls.target, camera.position).normalize();
          const right = new THREE.Vector3().crossVectors(camDir, new THREE.Vector3(0, 1, 0)).normalize();
          const screenUp = new THREE.Vector3().crossVectors(right, camDir).normalize();

          controls.target.addScaledVector(right, -dx * factor);
          controls.target.addScaledVector(screenUp, -dy * factor);
          updateCamera();
        } else {
          controls.theta -= dx * 0.005;
          controls.phi = Math.max(0.08, Math.min(Math.PI * 0.95, controls.phi - dy * 0.005));
          updateCamera();
        }
      });

      dom.addEventListener(
        "wheel",
        (e) => {
          controls.radius *= 1 + e.deltaY * 0.0011;
          controls.radius = Math.max(12, Math.min(115, controls.radius));
          updateCamera();
          e.preventDefault();
        },
        { passive: false }
      );

      const waterMatrix = new THREE.Matrix4();
      const waterQuat = new THREE.Quaternion();
      const waterPos = new THREE.Vector3();
      const waterScale = new THREE.Vector3();

      function animate() {
        requestAnimationFrame(animate);
        const t = performance.now() * 0.001;

        if (waterMesh) {
          for (let i = 0; i < waterVoxels.length; i++) {
            const v = waterVoxels[i];
            const wave =
              0.009 * Math.sin(t * 1.1 + v.x * 0.28 + v.z * 0.21) +
              0.005 * Math.sin(t * 0.83 - v.x * 0.13 + v.z * 0.31);

            waterPos.set(v.x, v.y + wave, v.z);
            waterScale.set(v.sx, v.sy, v.sz);
            waterMatrix.compose(waterPos, waterQuat, waterScale);
            waterMesh.setMatrixAt(i, waterMatrix);
          }
          waterMesh.instanceMatrix.needsUpdate = true;
        }

        shipGroup.position.y = 0.065 + 0.022 * Math.sin(t * 0.73);
        shipGroup.rotation.x = 0.0035 * Math.sin(t * 0.41);
        shipGroup.rotation.y = 0.005 * Math.sin(t * 0.23);
        shipGroup.rotation.z = 0.0009 * Math.sin(t * 0.29);

        beaconLight.intensity = 1.3 + 0.45 * Math.sin(t * 2.2);

        renderer.render(scene, camera);
      }

      animate();

      window.addEventListener("resize", () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
      });
    })();
  </script>
</body>
</html>
```