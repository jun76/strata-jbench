Save this as `index.html` and open it in Chrome. Drag with the mouse to orbit, and scroll to zoom.

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Voxel Sailing Ship at Harbor</title>
  <style>
    html, body {
      margin: 0;
      height: 100%;
      overflow: hidden;
      background: #8ec5e8;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    canvas {
      display: block;
      width: 100%;
      height: 100%;
    }
    #hud {
      position: absolute;
      top: 16px;
      left: 16px;
      padding: 10px 14px;
      background: rgba(0, 20, 40, 0.68);
      color: white;
      border-radius: 10px;
      pointer-events: none;
      line-height: 1.35;
      box-shadow: 0 6px 20px rgba(0,0,0,0.25);
    }
    #hud b {
      font-size: 18px;
      letter-spacing: 0.5px;
    }
  </style>
</head>
<body>
  <div id="hud">
    <b>Voxel Harbor</b><br />
    Drag: orbit &nbsp; • &nbsp; Wheel: zoom
  </div>

  <!-- Three.js from CDN. Requires internet access. -->
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js"></script>

  <script>
    (function () {
      const hud = document.getElementById("hud");

      if (!window.THREE) {
        hud.innerHTML =
          "<b>Unable to load Three.js</b><br />Connect to the internet and reload.";
        return;
      }

      function init() {
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x9ccbea);
        scene.fog = new THREE.Fog(0x9ccbea, 95, 210);

        const camera = new THREE.PerspectiveCamera(
          45,
          window.innerWidth / window.innerHeight,
          0.1,
          1000
        );

        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
        renderer.outputEncoding = THREE.sRGBEncoding;
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        renderer.domElement.style.cursor = "grab";
        document.body.appendChild(renderer.domElement);

        // Simple mouse orbit controls, so no extra library is needed.
        const target = new THREE.Vector3(0, 6, 0);
        let radius = 82;
        let theta = 0.88;
        let phi = 1.05;

        function updateCamera() {
          camera.position.set(
            target.x + radius * Math.sin(phi) * Math.sin(theta),
            target.y + radius * Math.cos(phi),
            target.z + radius * Math.sin(phi) * Math.cos(theta)
          );
          camera.lookAt(target);
        }
        updateCamera();

        let dragging = false;
        let lastX = 0;
        let lastY = 0;
        const canvas = renderer.domElement;

        canvas.addEventListener("pointerdown", function (e) {
          dragging = true;
          lastX = e.clientX;
          lastY = e.clientY;
          canvas.style.cursor = "grabbing";
          canvas.setPointerCapture(e.pointerId);
        });

        canvas.addEventListener("pointermove", function (e) {
          if (!dragging) return;
          const dx = e.clientX - lastX;
          const dy = e.clientY - lastY;
          theta -= dx * 0.004;
          phi += dy * 0.004;
          phi = Math.max(0.25, Math.min(Math.PI * 0.49, phi));
          lastX = e.clientX;
          lastY = e.clientY;
          updateCamera();
        });

        function endDrag(e) {
          dragging = false;
          canvas.style.cursor = "grab";
          try { canvas.releasePointerCapture(e.pointerId); } catch (_) {}
        }

        canvas.addEventListener("pointerup", endDrag);
        canvas.addEventListener("pointercancel", endDrag);
        canvas.addEventListener("contextmenu", e => e.preventDefault());

        canvas.addEventListener("wheel", function (e) {
          e.preventDefault();
          radius *= Math.pow(1.0015, e.deltaY);
          radius = Math.max(25, Math.min(160, radius));
          updateCamera();
        }, { passive: false });

        // Lighting.
        scene.add(new THREE.HemisphereLight(0xffffff, 0x244060, 0.78));

        const sun = new THREE.DirectionalLight(0xfff0cf, 1.05);
        sun.position.set(35, 62, 30);
        sun.castShadow = true;
        sun.shadow.mapSize.set(2048, 2048);
        sun.shadow.camera.left = -70;
        sun.shadow.camera.right = 70;
        sun.shadow.camera.top = 70;
        sun.shadow.camera.bottom = -70;
        sun.shadow.camera.near = 1;
        sun.shadow.camera.far = 220;
        scene.add(sun);

        const fill = new THREE.DirectionalLight(0x9fd4ff, 0.35);
        fill.position.set(-45, 25, -35);
        scene.add(fill);

        // Shared voxel box geometry and cached materials.
        const cubeGeo = new THREE.BoxGeometry(1, 1, 1);
        const matCache = {};

        function material(color) {
          if (!matCache[color]) {
            matCache[color] = new THREE.MeshStandardMaterial({
              color: color,
              roughness: 0.86,
              metalness: 0.0,
              flatShading: true
            });
          }
          return matCache[color];
        }

        function box(parent, x, y, z, w, h, d, color, rot) {
          const mesh = new THREE.Mesh(cubeGeo, material(color));
          mesh.position.set(x, y, z);
          mesh.scale.set(w, h, d);
          if (rot) mesh.rotation.set(rot[0] || 0, rot[1] || 0, rot[2] || 0);
          mesh.castShadow = true;
          mesh.receiveShadow = true;
          parent.add(mesh);
          return mesh;
        }

        function seededRandom() {
          let seed = 123456789;
          return function () {
            seed = (seed * 1664525 + 1013904223) >>> 0;
            return seed / 4294967296;
          };
        }
        const rand = seededRandom();

        function cloud(cx, cy, cz) {
          const parts = [
            [cx, cy, cz, 8, 3, 5],
            [cx - 4, cy + 1, cz + 1, 6, 3, 4],
            [cx + 5, cy + 1, cz - 1, 6, 3, 4],
            [cx + 1, cy + 3, cz, 5, 2, 3]
          ];
          for (const p of parts) {
            const m = box(scene, p[0], p[1], p[2], p[3], p[4], p[5], 0xffffff);
            m.castShadow = false;
            m.receiveShadow = false;
          }
        }

        cloud(-30, 30, -20);
        cloud(25, 34, -35);
        cloud(45, 28, 28);
        cloud(-52, 36, 24);

        // Water.
        box(scene, 0, -0.65, 0, 120, 1.3, 90, 0x1e76b5);
        box(scene, 0, -1.35, 0, 120, 0.7, 90, 0x12548b);

        // Small voxel waves.
        for (let i = 0; i < 170; i++) {
          const x = -55 + rand() * 110;
          const z = -40 + rand() * 80;
          if (x > 3 && x < 22 && z > -23 && z < 23) continue;
          const w = 0.6 + rand() * 2.2;
          const d = 0.4 + rand() * 1.6;
          const c = rand() > 0.25 ? 0x8fd0ee : 0xbfe8f7;
          const m = box(scene, x, 0.08, z, w, 0.12, d, c);
          m.castShadow = false;
        }

        // Foamy wake near the bow.
        for (let i = 0; i < 26; i++) {
          const z = 18 + rand() * 11;
          const x = -14 + (rand() - 0.5) * (7 + rand() * 5);
          const m = box(scene, x, 0.12, z, 0.5 + rand() * 1.6, 0.12, 0.5 + rand() * 1.5, 0xdff5ff);
          m.castShadow = false;
        }

        // Shore / land.
        box(scene, 31, 0.0, 0, 22, 1.0, 90, 0xb9ad8c);

        // Harbor dock/quay.
        box(scene, 12, 0.45, 0, 16, 1.1, 44, 0x898d87);

        for (let z = -21; z <= 21; z += 2.1) {
          const c = Math.round(z) % 4 === 0 ? 0xc38b55 : 0xd19a63;
          box(scene, 12, 1.08, z, 15.5, 0.16, 1.75, c);
        }

        for (const z of [-20, -10, 0, 10, 20]) {
          box(scene, 5, 0, z, 0.9, 3.5, 0.9, 0x6e4c33);
          box(scene, 19, 0, z, 0.9, 3.5, 0.9, 0x6e4c33);
          box(scene, 5, 1.35, z, 1.0, 0.35, 1.0, 0x4a3325);
          box(scene, 19, 1.35, z, 1.0, 0.35, 1.0, 0x4a3325);
        }

        // Gangplank from ship to dock.
        const plank = box(scene, -2.5, 2.0, 0, 13, 0.35, 2.6, 0xc08a52, [0, 0, -0.08]);
        plank.receiveShadow = true;

        for (const x of [-8, -5, -2, 1, 4]) {
          const y = 2.0 - 0.08 * (x + 2.5);
          for (const z of [-1.25, 1.25]) {
            box(scene, x, y + 0.55, z, 0.25, 0.9, 0.25, 0x6d442b);
          }
        }

        // Warehouse.
        box(scene, 30, 5.0, -18, 12, 9, 16, 0xd7b48b);
        box(scene, 30, 10.0, -18, 13, 0.9, 17, 0xb44738);

        box(scene, 23.9, 3.1, -18, 0.12, 5, 3.2, 0x5a3825);
        box(scene, 36.1, 3.1, -18, 0.12, 5, 3.2, 0x5a3825);

        for (const z of [-24, -21, -15, -12]) {
          box(scene, 23.9, 6.5, z, 0.12, 1.4, 1.8, 0x5b8fa6);
          box(scene, 36.1, 6.5, z, 0.12, 1.4, 1.8, 0x5b8fa6);
        }

        // Harbor crane.
        box(scene, 18, 5.5, 12, 2, 9, 2, 0xe0a13c);
        box(scene, 18, 10.2, 12, 2.5, 0.6, 2.5, 0xe0a13c);
        box(scene, 12, 10.5, 12, 14, 0.6, 0.7, 0xf0b84a);
        box(scene, 8.5, 9.2, 12, 0.25, 2.4, 0.25, 0x3f4a4f);
        box(scene, 8.5, 7.6, 12, 1.5, 0.9, 1.5, 0x6f7779);

        // Lighthouse.
        box(scene, 35, 0.8, -32, 10, 0.6, 10, 0x8d8b86);
        for (let i = 0; i < 6; i++) {
          const w = 5.2 - i * 0.35;
          const y = 1.1 + i * 2.15;
          const c = i % 2 === 0 ? 0xe8e3d2 : 0xc63a34;
          box(scene, 35, y, -32, w, 2.1, w, c);
        }
        box(scene, 35, 14.2, -32, 3.0, 2.2, 3.0, 0xffe58a);
        box(scene, 35, 15.8, -32, 3.4, 0.8, 3.4, 0xc22f2b);

        const lamp = new THREE.PointLight(0xffd77a, 0.6, 35);
        lamp.position.set(35, 14, -32);
        scene.add(lamp);

        function crate(x, z, s, baseY) {
          const y = baseY + s / 2;
          box(scene, x, y, z, s, s, s, 0xa86a3a);
          box(scene, x, y, z + s / 2 + 0.04, s * 0.85, 0.12, 0.12, 0x704124);
          box(scene, x, y, z + s / 2 + 0.05, 0.12, s * 0.85, 0.12, 0x704124);
          box(scene, x + s / 2 + 0.04, y, z, 0.12, s * 0.85, 0.12, 0x704124);
          box(scene, x + s / 2 + 0.05, y, z, 0.12, 0.12, s * 0.85, 0x704124);
        }

        function barrel(x, z) {
          box(scene, x, 2, z, 1.5, 2.0, 1.5, 0x8b5a2b);
          box(scene, x, 1.25, z, 1.6, 0.16, 1.6, 0x4b3629);
          box(scene, x, 2.75, z, 1.6, 0.16, 1.6, 0x4b3629);
        }

        function person(parent, x, z, baseY, shirt) {
          box(parent, x - 0.22, baseY + 0.5, z, 0.28, 1.0, 0.3, 0x2b3440);
          box(parent, x + 0.22, baseY + 0.5, z, 0.28, 1.0, 0.3, 0x2b3440);
          box(parent, x, baseY + 1.35, z, 0.85, 1.2, 0.5, shirt);
          box(parent, x - 0.55, baseY + 1.4, z, 0.25, 0.9, 0.25, shirt);
          box(parent, x + 0.55, baseY + 1.4, z, 0.25, 0.9, 0.25, shirt);
          box(parent, x, baseY + 2.15, z, 0.55, 0.55, 0.5, 0xf2c48a);
          box(parent, x, baseY + 2.5, z, 0.75, 0.18, 0.65, 0x333333);
        }

        // Cargo on dock.
        crate(8, -14, 1.8, 1.0);
        crate(10.2, -14, 1.8, 1.0);
        crate(9.1, -14, 1.8, 2.8);
        crate(12, -8, 2.0, 1.0);
        crate(15, 10, 2.0, 1.0);
        crate(17, 10, 2.0, 1.0);
        crate(16, 10, 2.0, 3.0);

        barrel(9, 6);
        barrel(13, 13);
        barrel(18, -6);

        // Dock workers.
        person(scene, 7, -5, 1.0, 0xe6b94a);
        person(scene, 13, 4, 1.0, 0x4f7fa8);
        person(scene, 17, 12, 1.0, 0xcf5b4b);

        // Buoys.
        function buoy(x, z, color) {
          box(scene, x, 0.25, z, 0.9, 0.5, 0.9, color);
          box(scene, x, 0.65, z, 0.35, 0.45, 0.35, 0xffffff);
        }
        buoy(-27, 18, 0xd33b32);
        buoy(-4, 27, 0xf0d35a);
        buoy(28, 14, 0xd33b32);

        // ---------------- Sailing ship ----------------
        const shipGroup = new THREE.Group();
        shipGroup.position.set(-14, 0, 0);
        scene.add(shipGroup);

        // Hull, tapered toward bow/stern.
        for (let z = -17; z <= 17; z += 2) {
          const taper = Math.max(0.52, 1 - Math.max(0, Math.abs(z) - 11) * 0.055);
          const w = 10 * taper;
          box(shipGroup, 0, 1.1, z, w, 1.8, 2.05, 0x5b3021);
          box(shipGroup, 0, 2.15, z, w * 0.98, 1.0, 2.05, 0x75412d);
        }

        // Deck.
        box(shipGroup, 0, 2.78, 0, 8.8, 0.25, 31, 0xc99a62);
        for (let z = -14; z <= 14; z += 2) {
          const c = Math.round(z) % 4 === 0 ? 0xd7a66e : 0xc38d55;
          box(shipGroup, 0, 2.93, z, 8.4, 0.06, 1.55, c);
        }

        // Side rails.
        for (let z = -16; z <= 16; z += 2) {
          const taper = Math.max(0.52, 1 - Math.max(0, Math.abs(z) - 11) * 0.055);
          const half = (10 * taper) / 2;
          box(shipGroup, -half + 0.35, 3.45, z, 0.5, 1.0, 0.45, 0x4d2b20);
          box(shipGroup,  half - 0.35, 3.45, z, 0.5, 1.0, 0.45, 0x4d2b20);
        }
        box(shipGroup, -4.4, 3.95, 0, 0.35, 0.35, 32, 0x4d2b20);
        box(shipGroup,  4.4, 3.95, 0, 0.35, 0.35, 32, 0x4d2b20);

        // Bow and stern.
        box(shipGroup, 0, 2.1, 18, 4.2, 1.6, 3.5, 0x4d2b20);
        box(shipGroup, 0, 3.0, 18.5, 3.0, 0.8, 2.0, 0x6a3b27);
        box(shipGroup, 0, 1.4, -18, 8.2, 1.6, 2.0, 0x4d2b20);
        box(shipGroup, 4.8, 2.1, 16, 0.6, 1.0, 0.6, 0x4b4b4b);

        // Stern cabin.
        box(shipGroup, 0, 4.55, -13, 5.6, 3.2, 5.5, 0xe8d7aa);
        box(shipGroup, 0, 6.35, -13, 6.0, 0.55, 5.9, 0x9c4939);
        for (const z of [-15, -13, -11]) {
          box(shipGroup,  2.9, 5.0, z, 0.12, 0.9, 0.9, 0x5c8ea6);
          box(shipGroup, -2.9, 5.0, z, 0.12, 0.9, 0.9, 0x5c8ea6);
        }

        // Ship wheel.
        box(shipGroup, 0, 4.0, -10.2, 0.6, 1.1, 0.25, 0x8c5a30);

        // Masts, yards, and sails.
        for (const z of [-6, 6]) {
          box(shipGroup, 0, 8.8, z, 0.75, 12.4, 0.75, 0x6d442b);
          box(shipGroup, 0, 10.4, z, 0.45, 0.35, 11.0, 0x6d442b);
          box(shipGroup, 0, 14.4, z, 0.45, 0.35, 12.0, 0x6d442b);

          box(shipGroup, 0.02, 7.1, z, 0.28, 6.4, 9.4, 0xf5efdc);
          box(shipGroup, 0.02, 12.1, z, 0.28, 4.6, 10.6, 0xf7f1df);

          for (let sy = 5.0; sy <= 9.5; sy += 1.5) {
            box(shipGroup, 0.2, sy, z, 0.06, 0.08, 9.4, 0xe1d7bd);
          }
          for (let sy = 11.0; sy <= 14.0; sy += 1.3) {
            box(shipGroup, 0.2, sy, z, 0.06, 0.08, 10.6, 0xe1d7bd);
          }

          // Red emblem on sail face.
          box(shipGroup, 0.22, 7.2, z, 0.06, 1.1, 1.1, 0xc33a32);

          // Flag.
          box(shipGroup, 0, 15.4, z, 0.2, 0.8, 0.2, 0x6d442b);
          box(shipGroup, 0, 15.7, z + 0.7, 0.08, 0.55, 1.4, 0xc33a32);
        }

        // Small deck boat.
        box(shipGroup, 2.6, 3.3, -15, 1.0, 0.8, 4.5, 0xb87943);

        // Ship crew.
        person(shipGroup, 2, -8, 2.95, 0xf2c94c);
        person(shipGroup, -2, 3, 2.95, 0xf0f0e8);

        // Gentle animation loop.
        function animate() {
          const t = performance.now() * 0.001;
          shipGroup.position.y = Math.sin(t * 0.8) * 0.06;
          shipGroup.rotation.z = Math.sin(t * 0.7) * 0.012;
          renderer.render(scene, camera);
          requestAnimationFrame(animate);
        }
        animate();

        window.addEventListener("resize", function () {
          camera.aspect = window.innerWidth / window.innerHeight;
          camera.updateProjectionMatrix();
          renderer.setSize(window.innerWidth, window.innerHeight);
          renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
        });
      }

      init();
    })();
  </script>
</body>
</html>
```