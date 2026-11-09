Save this as a single `.html` file and open it in Chrome. It uses Three.js from a CDN, so it needs internet access.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Voxel Scene — Sailing Ship Calling at a Harbor</title>
<style>
  html, body {
    margin: 0;
    height: 100%;
    overflow: hidden;
    background: #07111d;
  }
  canvas {
    display: block;
    touch-action: none;
  }
  #hud {
    position: absolute;
    top: 14px;
    left: 14px;
    color: #fff;
    font: 14px system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
    background: rgba(0, 0, 0, 0.45);
    padding: 10px 12px;
    border-radius: 10px;
    pointer-events: none;
    max-width: 380px;
  }
  #hud h1 {
    margin: 0 0 4px;
    font-size: 16px;
  }
  #hud p {
    margin: 0;
    opacity: 0.92;
    font-size: 12px;
  }
  #fallback {
    display: none;
    color: #fff;
    padding: 24px;
    font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
  }
</style>
</head>
<body>
  <div id="hud">
    <h1>Voxel scene: A sailing ship calling at a harbor</h1>
    <p>Left-drag to orbit · Scroll to zoom · Right-drag to pan · Double-click to reset</p>
  </div>
  <div id="fallback">
    <p>Unable to load Three.js or create a WebGL scene. Try opening this file in Chrome with internet access.</p>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/three@0.148.0/build/three.min.js"></script>
  <script>
  (function () {
    if (!window.THREE) {
      document.getElementById("fallback").style.display = "block";
      return;
    }

    let renderer;
    try {
      renderer = new THREE.WebGLRenderer({ antialias: true });
    } catch (e) {
      document.getElementById("fallback").style.display = "block";
      return;
    }

    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x84c5e6);
    scene.fog = new THREE.Fog(0x84c5e6, 78, 210);

    const camera = new THREE.PerspectiveCamera(
      50,
      window.innerWidth / window.innerHeight,
      0.1,
      600
    );

    const hemi = new THREE.HemisphereLight(0xbde7ff, 0x4c5a3c, 0.85);
    scene.add(hemi);

    const sun = new THREE.DirectionalLight(0xffe2b6, 0.95);
    sun.position.set(45, 55, 25);
    scene.add(sun);

    const fillLight = new THREE.DirectionalLight(0x9ecff6, 0.35);
    fillLight.position.set(-30, 30, -20);
    scene.add(fillLight);

    const MAX_VOXELS = 70000;
    const boxGeometry = new THREE.BoxGeometry(1, 1, 1);
    const boxMaterial = new THREE.MeshLambertMaterial({ color: 0xffffff });
    const instanced = new THREE.InstancedMesh(boxGeometry, boxMaterial, MAX_VOXELS);
    instanced.frustumCulled = false;
    scene.add(instanced);

    const dummy = new THREE.Object3D();
    const tmpColor = new THREE.Color();
    let instanceCount = 0;

    function addInstance(cx, cy, cz, color, sx = 1, sy = 1, sz = 1) {
      if (instanceCount >= MAX_VOXELS) return;
      dummy.position.set(cx, cy, cz);
      dummy.scale.set(sx, sy, sz);
      dummy.rotation.set(0, 0, 0);
      dummy.updateMatrix();
      instanced.setMatrixAt(instanceCount, dummy.matrix);
      instanced.setColorAt(instanceCount, tmpColor.set(color));
      instanceCount++;
    }

    function addVoxel(x, y, z, color) {
      addInstance(x + 0.5, y + 0.5, z + 0.5, color, 1, 1, 1);
    }

    function addBox(cx, cy, cz, color, sx = 1, sy = 1, sz = 1) {
      addInstance(cx, cy, cz, color, sx, sy, sz);
    }

    function hash2(x, z) {
      const n = Math.sin(x * 127.1 + z * 311.7) * 43758.5453123;
      return n - Math.floor(n);
    }

    const COL = {
      waterDeep: 0x0f4161,
      waterMid: 0x166b8e,
      waterLight: 0x2188a7,
      waterFoam: 0x45a9be,
      waterFoamLight: 0x6fc7d8,

      hullDark: 0x3a221a,
      hullDark2: 0x24130e,
      hullMid: 0x6a4733,
      hullMidDark: 0x462b1f,
      hullUpper: 0x8c6448,
      hullUpperDark: 0x5a3d29,
      gunwale: 0x6c4b38,
      deck: 0xb8956f,
      deckDark: 0x8e704f,
      cabinWood: 0x9b7254,
      cabinDark: 0x6f513b,
      mast: 0x7b5839,
      mastDark: 0x4b3321,
      sail: 0xf6eedd,
      sailShade: 0xd8c9b1,
      sailEdge: 0xbba891,
      flag: 0xc1382e,
      flagDark: 0x7a261d,
      rope: 0x513d28,

      dockWood: 0xb5895f,
      dockWoodDark: 0x7f5d41,
      stone: 0x8e8b8a,
      stoneDark: 0x656362,
      stoneLight: 0xa8a5a2,
      dirt: 0x6d513a,
      dirtLight: 0x8a6a4b,
      grass: 0x5d8c48,
      grassLight: 0x78a75d,
      crate: 0xa77a49,
      crateDark: 0x795633,
      roof: 0x664034,
      wallBrick: 0xb15c3d,
      wallBrickDark: 0x8e432d,
      window: 0xf1cf75,
      lighthouseWhite: 0xf2ece1,
      lighthouseRed: 0xb4362b,
      lamp: 0xfff2a8
    };

    function fillBox(x1, x2, y1, y2, z1, z2, color, options) {
      const even = (n) => (n % 2) === 0;
      for (let x = x1; x <= x2; x++) {
        for (let y = y1; y <= y2; y++) {
          for (let z = z1; z <= z2; z++) {
            let c = color;
            if (options && options.window) {
              if ((z === z2 && even(x) && even(y)) || (x === x2 && even(z) && even(y))) {
                c = options.window;
              }
            }
            addVoxel(x, y, z, c);
          }
        }
      }
    }

    function addBase() {
      // Large hidden base under everything, helpful if the camera looks low.
      addBox(-8, -5, -2, 0x102b3f, 92, 2, 88);
    }

    function addWater() {
      for (let z = -22; z <= 18; z++) {
        for (let x = -30; x <= 13; x++) {
          const wave =
            Math.sin(x * 0.28 + z * 0.24) * 0.50 +
            Math.sin(x * 0.63 - z * 0.42) * 0.25 +
            Math.sin(x * 1.12 + z * 0.89) * 0.25;

          let t = (wave + 1) * 0.5;
          t += hash2(x, z) * 0.16;

          let c;
          if (t < 0.14) c = COL.waterDeep;
          else if (t < 0.34) c = COL.waterMid;
          else if (t < 0.56) c = COL.waterLight;
          else if (t < 0.80) c = COL.waterFoam;
          else c = COL.waterFoamLight;

          addVoxel(x, 0, z, c);
        }
      }
    }

    function addDock() {
      for (let z = -7; z <= 14; z++) {
        for (let x = 14; x <= 15; x++) {
          for (let y = 0; y <= 4; y++) {
            let c;
            if (y === 4) {
              c = ((x + z) % 2 === 0) ? COL.dockWood : COL.dockWoodDark;
            } else if (y === 3) {
              c = hash2(x, z) > 0.5 ? COL.stoneLight : COL.stone;
            } else if (y === 2) {
              c = hash2(x, z) > 0.7 ? COL.stone : COL.stoneDark;
            } else if (y === 1) {
              c = hash2(x, z) > 0.6 ? COL.stoneDark : COL.stone;
            } else {
              c = COL.stoneDark;
            }
            addVoxel(x, y, z, c);
          }
        }
      }
    }

    function addLand() {
      for (let z = -9; z <= 15; z++) {
        for (let x = 16; x <= 28; x++) {
          for (let y = 1; y <= 4; y++) {
            const h = hash2(x, z);
            let c;
            if (y === 4) {
              c = h > 0.65 ? COL.grassLight : COL.grass;
            } else if (y === 3) {
              c = h > 0.7 ? COL.dirtLight : COL.dirt;
            } else if (y === 2) {
              c = COL.dirt;
            } else {
              c = h > 0.5 ? COL.stoneDark : COL.stone;
            }
            addVoxel(x, y, z, c);
          }
        }
      }
    }

    function addBuildings() {
      // Warehouse 1
      fillBox(18, 22, 5, 7, -3, 1, COL.wallBrick, { window: COL.window });
      fillBox(17, 23, 8, 8, -4, 2, COL.roof);

      // Warehouse 2
      fillBox(21, 25, 5, 7, 4, 8, COL.wallBrickDark, { window: COL.window });
      fillBox(20, 26, 8, 8, 3, 9, COL.roof);

      // Lighthouse
      for (let z = 10; z <= 12; z++) {
        for (let x = 24; x <= 26; x++) {
          for (let y = 5; y <= 13; y++) {
            const stripe = (y - 5) % 4;
            const c = stripe < 2 ? COL.lighthouseWhite : COL.lighthouseRed;
            addVoxel(x, y, z, c);
          }
        }
      }
      fillBox(24, 26, 14, 14, 10, 12, COL.lighthouseRed);
      addBox(25.5, 15.5, 11.5, COL.lamp, 1.2, 1.0, 1.2);
    }

    function addQuayDetails() {
      // Bollards along the quay edge
      for (let z = -6; z <= 14; z += 4) {
        addVoxel(15, 5, z, 0x573f2b);
      }

      // Crates, avoiding the gangplank area
      const crateZ = [-6, -2, 4, 8, 12];
      for (const z of crateZ) {
        addVoxel(15, 5, z, COL.crate);
        addVoxel(14, 5, z, COL.crateDark);
      }

      // Gangplank from quay to ship
      for (let z = 0; z <= 2; z++) {
        addVoxel(13, 4, z, COL.dockWood);
      }

      // Mooring ropes
      addBox(13.7, 5.2, 0.5, COL.rope, 2.8, 0.22, 0.22);
      addBox(13.7, 5.2, 2.5, COL.rope, 2.8, 0.22, 0.22);
    }

    function shipHalfWidth(z) {
      const t = (z + 10.5) / 19;
      if (t <= 0 || t >= 1) return 0;
      return Math.sin(Math.PI * t) * 4.8;
    }

    function addShipHull() {
      for (let z = -10; z <= 8; z++) {
        const half = shipHalfWidth(z);
        if (half < 0.5) continue;

        for (let y = 1; y <= 4; y++) {
          const factor = y === 1 ? 0.88 : y === 2 ? 0.95 : 1.0;
          const halfY = half * factor;

          const xS = Math.max(3, Math.round(7.5 - halfY));
          const xE = Math.min(12, Math.round(7.5 + halfY));

          for (let x = xS; x <= xE; x++) {
            const edge = x === xS || x === xE;
            let c;

            if (y === 1) {
              c = edge ? COL.hullDark2 : COL.hullDark;
            } else if (y === 2) {
              c = edge ? COL.hullMidDark : COL.hullMid;
            } else if (y === 3) {
              c = edge ? COL.hullUpperDark : COL.hullUpper;
            } else {
              c = edge ? COL.gunwale : COL.deck;
            }

            if (y >= 2 && hash2(x, z) > 0.88) {
              c = COL.hullDark2;
            }

            addVoxel(x, y, z, c);
          }
        }
      }
    }

    function addShipSuperstructures() {
      // Forecastle
      fillBox(6, 9, 5, 6, -9, -7, COL.cabinDark);
      fillBox(5, 10, 7, 7, -10, -7, COL.roof);

      // Stern cabin
      fillBox(6, 9, 5, 7, 4, 7, COL.cabinWood, { window: COL.window });
      fillBox(5, 10, 8, 8, 3, 8, COL.roof);
    }

    function addSail(zc, yStart, yEnd, baseHalf, topHalf) {
      for (let y = yStart; y <= yEnd; y++) {
        const span = yEnd - yStart || 1;
        const t = (y - yStart) / span;
        const half = baseHalf + (topHalf - baseHalf) * t;

        const xS = Math.max(3, Math.round(7.5 - half));
        const xE = Math.min(12, Math.round(7.5 + half));

        for (let x = xS; x <= xE; x++) {
          let c = COL.sail;
          if (x === xS || x === xE || y === yEnd) {
            c = COL.sailEdge;
          } else if (((x + y + zc + 30) % 3) === 0) {
            c = COL.sailShade;
          }
          addVoxel(x, y, zc, c);
        }
      }
    }

    function addShipMastsAndSails() {
      const masts = [
        { z: -7, type: "fore" },
        { z: -2, type: "main" },
        { z: 4, type: "mizzen" }
      ];

      for (const m of masts) {
        const zc = m.z + 0.5;

        // Mast, from deck level y=5 to y=14
        addBox(8, 9.5, zc, COL.mast, 0.65, 9, 0.65);

        if (m.type === "main") {
          addBox(8, 9.5, zc, COL.mastDark, 8.6, 0.38, 0.38);
          addBox(8, 11.5, zc, COL.mastDark, 6.5, 0.30, 0.30);
        } else if (m.type === "fore") {
          addBox(8, 8.5, zc, COL.mastDark, 7.0, 0.35, 0.35);
          addBox(8, 10.5, zc, COL.mastDark, 5.0, 0.30, 0.30);
        } else if (m.type === "mizzen") {
          addBox(8, 8.5, zc, COL.mastDark, 6.0, 0.35, 0.35);
          addBox(8, 9.5, zc, COL.mastDark, 4.5, 0.30, 0.30);
        }
      }

      // Sails
      addSail(-7, 6, 10, 3.8, 2.2);
      addSail(-2, 6, 11, 4.4, 2.6);
      addSail(4, 6, 9, 3.2, 2.0);

      // Bowsprit
      addBox(8, 5.7, -10.5, COL.mastDark, 0.45, 0.55, 4.5);

      // Flags
      addBox(8, 14.4, -1.5, COL.flag, 2.2, 1.1, 1.1);
      addBox(8, 14.4, -6.5, COL.flagDark, 1.4, 1.0, 1.0);
      addBox(8, 14.4, 4.5, COL.flag, 1.2, 1.0, 1.0);

      // Simple rigging lines
      addBox(8, 13.5, -4.0, COL.rope, 0.20, 0.20, 4.5);
      addBox(8, 13.5, 1.0, COL.rope, 0.20, 0.20, 4.5);
    }

    function addShip() {
      addShipHull();
      addShipSuperstructures();
      addShipMastsAndSails();
    }

    function buildScene() {
      addBase();
      addWater();
      addDock();
      addLand();
      addBuildings();
      addQuayDetails();
      addShip();
    }

    function finishInstancing() {
      instanced.count = instanceCount;
      instanced.instanceMatrix.needsUpdate = true;
      if (instanced.instanceColor) {
        instanced.instanceColor.needsUpdate = true;
      }
    }

    buildScene();
    finishInstancing();

    // Mouse controls
    const targetDesired = new THREE.Vector3(7, 7, 1);
    const target = targetDesired.clone();

    const state = { radius: 62, phi: 1.08, theta: 0.72 };
    const desired = { radius: 62, phi: 1.08, theta: 0.72 };
    const camOffset = new THREE.Vector3();

    function clamp(v, a, b) {
      return Math.max(a, Math.min(b, v));
    }

    function resetView() {
      desired.radius = 62;
      desired.phi = 1.08;
      desired.theta = 0.72;
      targetDesired.set(7, 7, 1);
    }

    let dragging = false;
    let panMode = false;
    let lastX = 0;
    let lastY = 0;

    const canvas = renderer.domElement;

    canvas.addEventListener("pointerdown", (e) => {
      e.preventDefault();
      dragging = true;
      lastX = e.clientX;
      lastY = e.clientY;
      panMode = (e.button === 2 || e.ctrlKey || e.metaKey);
    });

    window.addEventListener("pointermove", (e) => {
      if (!dragging) return;

      const dx = e.clientX - lastX;
      const dy = e.clientY - lastY;
      lastX = e.clientX;
      lastY = e.clientY;

      if (panMode) {
        panCamera(dx, dy);
      } else {
        desired.theta -= dx * 0.0035;
        desired.phi -= dy * 0.0035;
        desired.phi = clamp(desired.phi, 0.20, 1.45);
      }
    });

    window.addEventListener("pointerup", () => {
      dragging = false;
    });

    window.addEventListener("pointercancel", () => {
      dragging = false;
    });

    canvas.addEventListener("wheel", (e) => {
      e.preventDefault();
      desired.radius *= Math.exp(e.deltaY * 0.001);
      desired.radius = clamp(desired.radius, 14, 170);
    }, { passive: false });

    canvas.addEventListener("dblclick", resetView);
    canvas.addEventListener("contextmenu", (e) => e.preventDefault());

    window.addEventListener("resize", () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    });

    const dir = new THREE.Vector3();
    const worldUp = new THREE.Vector3(0, 1, 0);
    const right = new THREE.Vector3();
    const up = new THREE.Vector3();

    function panCamera(dx, dy) {
      camera.getWorldDirection(dir);
      right.crossVectors(dir, worldUp).normalize();
      if (right.lengthSq() < 1e-8) right.set(1, 0, 0);
      up.crossVectors(right, dir).normalize();

      const scale = state.radius * 0.0022;
      targetDesired.addScaledVector(right, dx * scale);
      targetDesired.addScaledVector(up, -dy * scale);
    }

    function updateView() {
      state.radius += (desired.radius - state.radius) * 0.12;
      state.phi += (desired.phi - state.phi) * 0.12;
      state.theta += (desired.theta - state.theta) * 0.12;
      target.lerp(targetDesired, 0.12);

      state.phi = clamp(state.phi, 0.18, 1.47);

      camOffset.setFromSphericalCoords(state.radius, state.phi, state.theta);
      camera.position.copy(target).add(camOffset);
      camera.lookAt(target);
    }

    function animate() {
      requestAnimationFrame(animate);
      updateView();
      renderer.render(scene, camera);
    }

    updateView();
    renderer.render(scene, camera);
    animate();
  })();
  </script>
</body>
</html>
```