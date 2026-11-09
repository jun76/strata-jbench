Save this as an `.html` file and open it directly in Chrome. It uses Three.js from a CDN, but everything else is in the single file.

```html
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>3D Voxel Harbor — Sailing Ship Calling at Harbor</title>
  <style>
    html, body {
      margin: 0;
      height: 100%;
      overflow: hidden;
      background: #8ecbe8;
    }
    canvas {
      display: block;
      width: 100%;
      height: 100%;
      touch-action: none;
    }
    #info {
      position: fixed;
      left: 14px;
      bottom: 14px;
      font-family: system-ui, -apple-system, Arial, sans-serif;
      font-size: 13px;
      color: #ffffff;
      text-shadow: 0 1px 3px rgba(0,0,0,0.65);
      pointer-events: none;
      user-select: none;
    }
  </style>
</head>
<body>
  <script src="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js"></script>

  <script>
    (function () {
      const renderer = new THREE.WebGLRenderer({ antialias: true });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
      renderer.setSize(window.innerWidth, window.innerHeight);
      renderer.outputColorSpace = THREE.sRGBColorSpace;
      renderer.shadowMap.enabled = true;
      renderer.shadowMap.type = THREE.PCFSoftShadowMap;
      document.body.appendChild(renderer.domElement);

      const scene = new THREE.Scene();
      scene.background = new THREE.Color('#87cbe8');
      scene.fog = new THREE.Fog('#a9cbe5', 70, 210);

      const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 1, 500);

      // Lights
      const hemi = new THREE.HemisphereLight('#cbefff', '#3f5544', 0.65);
      scene.add(hemi);

      const sun = new THREE.DirectionalLight('#fff3d5', 1.25);
      sun.position.set(75, 115, 45);
      sun.castShadow = true;
      sun.shadow.mapSize.set(2048, 2048);
      sun.shadow.camera.left = -115;
      sun.shadow.camera.right = 115;
      sun.shadow.camera.top = 115;
      sun.shadow.camera.bottom = -115;
      sun.shadow.camera.near = 1;
      sun.shadow.camera.far = 320;
      sun.shadow.bias = -0.0008;
      sun.shadow.normalBias = 0.38;

      const sunTarget = new THREE.Object3D();
      sunTarget.position.set(5, 6, 0);
      sun.target = sunTarget;
      scene.add(sun);
      scene.add(sunTarget);

      // Deterministic pseudo-random
      let rng = 123456789;
      function rnd() {
        rng = (rng * 1664525 + 1013904223) & 0x7fffffff;
        return rng / 0x80000000;
      }

      function colorToInt(hex) {
        return parseInt(hex.slice(1), 16);
      }

      function clamp255(v) {
        return v < 0 ? 0 : v > 255 ? 255 : Math.round(v);
      }

      function jitterColor(c, amount) {
        if (!amount) return c;
        const r = clamp255(((c >> 16) & 255) + (rnd() - 0.5) * amount);
        const g = clamp255(((c >> 8) & 255) + (rnd() - 0.5) * amount);
        const b = clamp255((c & 255) + (rnd() - 0.5) * amount);
        return (r << 16) | (g << 8) | b;
      }

      const voxels = [];

      function add(x, y, z, color) {
        voxels.push({ x: x, y: y, z: z, color: color });
      }

      function addBox(x0, x1, y0, y1, z0, z1, colorBase, amount = 0) {
        if (x0 > x1) { const t = x0; x0 = x1; x1 = t; }
        if (y0 > y1) { const t = y0; y0 = y1; y1 = t; }
        if (z0 > z1) { const t = z0; z0 = z1; z1 = t; }

        const base = typeof colorBase === 'number' ? colorBase : colorToInt(colorBase);

        for (let y = y0; y <= y1; y++) {
          for (let z = z0; z <= z1; z++) {
            for (let x = x0; x <= x1; x++) {
              add(x, y, z, jitterColor(base, amount));
            }
          }
        }
      }

      function pick(a) {
        return a[(rnd() * a.length) | 0];
      }

      const WHITE = '#d8d2c1';
      const WOOD = '#8d6240';
      const DARKWOOD = '#624329';
      const RED = '#c4392c';
      const STONE = '#9e9a92';
      const FORE = '#1f5d82';
      const MID = '#266597';
      const SHALLOW = '#3f92b8';
      const VERYSHALLOW = '#56a8bc';
      const FOAM = '#bde7ef';

      // Water only where the harbor opens; land/quay cover the rest.
      for (let z = -55; z <= 55; z++) {
        for (let x = -55; x <= 22; x++) {
          const wave = Math.sin(x * 0.37 + z * 0.55) * 0.5 + 0.5;
          const distShore = 22 - x;
          let c;
          if (distShore < 17) {
            c = wave > 0.62 ? VERYSHALLOW : SHALLOW;
          } else {
            c = wave > 0.72 ? MID : wave > 0.45 ? '#25547c' : FORE;
          }
          if (x === 22 && rnd() < 0.18) c = FOAM;
          add(x, 0, z, jitterColor(colorToInt(c), 32));
        }
      }

      // Land
      addBox(25, 70, 0, 2, -55, 55, '#6c5b3e', 30);
      addBox(25, 25, 0, 3, -55, 55, '#7d7a70', 18); // rocky shore edge
      addBox(26, 70, 3, 3, -55, 55, '#5f9f45', 22);

      // Stone quay edge
      addBox(23, 24, 0, 3, -55, 55, '#9f9b92', 18);

      // Wooden pier jutting out beside the ship
      addBox(15, 24, 3, 3, 0, 4, '#a16d42', 22);
      for (let z of [0, 2, 4]) {
        addBox(15, 16, 1, 2, z, z, DARKWOOD, 10);
        addBox(23, 24, 1, 2, z, z, DARKWOOD, 10);
      }

      // Bollards
      function addBollard(x, z) {
        addBox(x, x, 4, 5, z, z, '#2f2d2b', 6);
      }
      addBollard(17, 0);
      addBollard(17, 4);
      addBollard(21, 0);
      addBollard(21, 4);
      addBollard(19, 2);

      // Gangway between ship side and pier
      addBox(14, 16, 4, 4, 1, 3, '#a8754c', 12);

      // Quay lamps
      function addLamp(x, z) {
        addBox(x, x, 4, 7, z, z, '#35322e', 4);
        addBox(x, x, 8, 8, z, z, '#f3d15f', 0);
      }
      addLamp(27, -25);
      addLamp(31, 38);
      addLamp(48, -38);

      // Harbor warehouse
      addBox(32, 44, 4, 8, 16, 30, '#6d7d8b', 18);
      addBox(31, 45, 9, 9, 15, 31, '#a94134', 12);
      addBox(36, 37, 4, 6, 15, 15, '#4a3320', 8);
      addBox(33, 34, 6, 7, 15, 15, '#27374f', 0);
      addBox(42, 43, 6, 7, 15, 15, '#27374f', 0);

      // Harbor house
      addBox(40, 48, 4, 6, -6, 4, '#a85340', 18);
      addBox(39, 49, 7, 7, -7, 5, '#37414a', 8);
      addBox(44, 45, 4, 5, -7, -7, '#3b2d21', 0);
      addBox(42, 42, 5, 5, -7, -7, '#2b3c53', 0);
      addBox(47, 47, 5, 5, -7, -7, '#2b3c53', 0);
      addBox(44, 44, 5, 5, 5, 5, '#2b3c53', 0);

      // Containers
      addBox(26, 28, 4, 5, 10, 12, RED, 10);
      addBox(30, 32, 4, 5, 10, 12, '#2b6b95', 10);
      addBox(26, 28, 6, 7, 10, 12, '#e0a631', 10);
      addBox(30, 32, 4, 5, 14, 16, '#2f7a50', 10);

      // Cargo crane
      addBox(24, 26, 4, 16, 14, 16, '#3d434b', 10);
      addBox(24, 34, 17, 17, 14, 14, '#3d434b', 10);
      addBox(32, 32, 15, 16, 14, 14, '#8a9098', 8);
      addBox(31, 33, 13, 14, 13, 15, '#df9f32', 10);

      // Lighthouse
      for (let y = 4; y <= 19; y++) {
        const c = (y % 4 < 2) ? WHITE : RED;
        for (let x = 28; x <= 30; x++) {
          for (let z = -40; z <= -38; z++) {
            add(x, y, z, jitterColor(colorToInt(c), 7));
          }
        }
      }
      addBox(27, 31, 20, 20, -41, -37, '#2f343b', 0);
      addBox(28, 30, 21, 21, -40, -38, '#f6df58', 0);
      addBox(27, 31, 22, 22, -41, -37, '#b53b31', 8);

      // Trees on land
      function addTree(x, z) {
        addBox(x, x, 4, 5, z, z, '#7c5432', 10);
        addBox(x - 1, x + 1, 6, 7, z - 1, z + 1, '#4d8d3c', 18);
        addBox(x, x, 8, 8, z, z, '#4d8d3c', 12);
      }
      addTree(58, -35);
      addTree(55, 40);
      addTree(48, -45);
      addTree(62, 15);
      addTree(66, -5);

      // Small channel buoys
      function addBuoy(x, z, lower, upper) {
        addBox(x, x, 0, 1, z, z, lower, 8);
        addBox(x, x, 2, 2, z, z, upper, 0);
      }
      addBuoy(-22, -28, RED, '#f0ead2');
      addBuoy(-30, 18, '#2f7a50', '#f0ead2');

      // Small sailboats
      function addSmallBoat(x, z) {
        addBox(x - 1, x + 1, 1, 1, z - 1, z + 1, '#7f5538', 15);
        addBox(x, x, 2, 3, z, z, '#614025', 8);
        addBox(x + 1, x + 2, 2, 4, z, z, '#eee7d5', 10);
        addBox(x + 1, x + 2, 5, 5, z, z, '#c8382b', 0);
      }
      addSmallBoat(-15, -18);
      addSmallBoat(-22, 10);

      // Main sailing ship. Length along z, center around x=6.
      const CX = 6;

      function hullHalfWidth(z) {
        const az = Math.abs(z);
        if (az <= 12) return 8;
        if (az <= 15) return 5;
        return 3;
      }

      for (let z = -18; z <= 18; z++) {
        const hw = hullHalfWidth(z);
        const x0 = CX - hw;
        const x1 = CX + hw;

        addBox(x0, x1, 1, 2, z, z, '#3c2416', 22);
        addBox(x0, x1, 3, 3, z, z, WOOD, 25);

        // Bulwark / rail
        addBox(x0 - 1, x0 - 1, 4, 4, z, z, WHITE, 10);
        addBox(x1 + 1, x1 + 1, 4, 4, z, z, WHITE, 10);

        if (z === -18 || z === 18) {
          addBox(x0 - 1, x1 + 1, 4, 4, z, z, WHITE, 10);
        }
      }

      // Foam around the widest part of the hull
      for (let z = -12; z <= 12; z += 2) {
        add(CX - 9, 0, z, jitterColor(colorToInt(FOAM), 35));
        add(CX + 9, 0, z, jitterColor(colorToInt(FOAM), 35));
      }

      // Wake behind the stern
      for (let z = 19; z <= 36; z++) {
        const w = Math.max(1, 7 - Math.floor((z - 18) / 4));
        addBox(CX - w, CX + w, 0, 0, z, z, pick(['#69a8bd', '#82b7c8']), 45);
      }

      // Forecastle
      addBox(2, 10, 4, 6, -18, -14, WHITE, 10);
      addBox(1, 11, 7, 7, -19, -13, '#5a3525', 8);
      addBox(10, 10, 5, 5, -16, -15, '#28384d', 0);
      addBox(2, 2, 5, 5, -16, -15, '#28384d', 0);

      // Quarterdeck / sterncastle
      addBox(2, 10, 4, 7, 14, 18, WHITE, 10);
      addBox(1, 11, 8, 8, 13, 19, '#5a3525', 8);
      addBox(11, 11, 6, 6, 14, 16, '#25374d', 0);
      addBox(1, 1, 6, 6, 14, 16, '#25374d', 0);

      // Masts, yards, sails. Place masts slightly inside so sails do not sit in cabins.
      const mastZ = [-11, 0, 11];
      const sailStripe = [colorToInt('#c43a2d'), colorToInt('#2e6b91'), colorToInt('#2b7a55')];
      const flagColor = [colorToInt('#c53a2d'), colorToInt('#f3eee2'), colorToInt('#2c7b50')];

      for (let i = 0; i < mastZ.length; i++) {
        const mz = mastZ[i];

        addBox(CX, CX, 4, 28, mz, mz, '#5d3b22', 12);
        addBox(CX, CX, 28, 28, mz, mz, '#433b33', 0);
        addBox(7, 9, 29, 29, mz, mz, flagColor[i], 6);

        for (let y of [12, 18, 24]) {
          // Yard arm
          addBox(0, 12, y, y, mz, mz, '#6b4527', 8);

          // Square sail
          for (let x = 0; x <= 12; x++) {
            for (let yy = y - 5; yy <= y - 1; yy++) {
              const striped = (x % 6 < 2) || (yy % 5 == 0);
              const c = striped ? sailStripe[i] : colorToInt('#efe8d7');
              add(x, yy, mz, jitterColor(c, 14));
            }
          }
        }
      }

      // Build the InstancedMesh from the voxel list.
      const geometry = new THREE.BoxGeometry(0.96, 0.96, 0.96);
      const material = new THREE.MeshStandardMaterial({
        color: 0xffffff,
        roughness: 0.9,
        metalness: 0.0,
        flatShading: true
      });

      const mesh = new THREE.InstancedMesh(geometry, material, voxels.length);
      const dummy = new THREE.Object3D();
      const tmpColor = new THREE.Color();

      for (let i = 0; i < voxels.length; i++) {
        const v = voxels[i];
        dummy.position.set(v.x, v.y, v.z);
        dummy.updateMatrix();
        mesh.setMatrixAt(i, dummy.matrix);
        tmpColor.setHex(v.color);
        mesh.setColorAt(i, tmpColor);
      }

      mesh.instanceMatrix.needsUpdate = true;
      mesh.instanceColor.needsUpdate = true;
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      scene.add(mesh);

      // Mouse orbit view
      const view = {
        target: new THREE.Vector3(5, 13, 0),
        radius: 95,
        theta: 2.45,
        phi: 1.08
      };

      function clamp(v, a, b) {
        return v < a ? a : v > b ? b : v;
      }

      function updateCamera() {
        const r = view.radius;
        const sinPhi = Math.sin(view.phi);
        camera.position.set(
          view.target.x + r * sinPhi * Math.cos(view.theta),
          view.target.y + r * Math.cos(view.phi),
          view.target.z + r * sinPhi * Math.sin(view.theta)
        );
        camera.lookAt(view.target);
      }

      let dragging = false;
      let lastX = 0;
      let lastY = 0;

      window.addEventListener('pointerdown', function (e) {
        dragging = true;
        lastX = e.clientX;
        lastY = e.clientY;
      });

      window.addEventListener('pointermove', function (e) {
        if (!dragging) {
          lastX = e.clientX;
          lastY = e.clientY;
          return;
        }

        const dx = e.clientX - lastX;
        const dy = e.clientY - lastY;

        view.theta -= dx * 0.0065;
        view.phi = clamp(view.phi - dy * 0.0055, 0.35, 1.45);

        lastX = e.clientX;
        lastY = e.clientY;
      });

      window.addEventListener('pointerup', function () {
        dragging = false;
      });

      window.addEventListener('wheel', function (e) {
        view.radius = clamp(view.radius * (e.deltaY > 0 ? 1.08 : 0.92), 28, 185);
      });

      window.addEventListener('dblclick', function () {
        view.radius = 95;
        view.theta = 2.45;
        view.phi = 1.08;
      });

      window.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowLeft') view.theta -= 0.035;
        if (e.key === 'ArrowRight') view.theta += 0.035;
        if (e.key === 'ArrowUp') view.phi = clamp(view.phi - 0.025, 0.35, 1.45);
        if (e.key === 'ArrowDown') view.phi = clamp(view.phi + 0.025, 0.35, 1.45);
      });

      window.addEventListener('resize', function () {
        renderer.setSize(window.innerWidth, window.innerHeight);
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
      });

      const info = document.createElement('div');
      info.id = 'info';
      info.textContent = 'A sailing ship calling at a harbor — drag to rotate, wheel to zoom';
      document.body.appendChild(info);

      // Render immediately, then animate. Freeze static shadows after first frame.
      updateCamera();
      renderer.render(scene, camera);
      sun.shadow.autoUpdate = false;

      function animate() {
        updateCamera();
        renderer.render(scene, camera);
        requestAnimationFrame(animate);
      }

      animate();
    })();
  </script>
</body>
</html>
```