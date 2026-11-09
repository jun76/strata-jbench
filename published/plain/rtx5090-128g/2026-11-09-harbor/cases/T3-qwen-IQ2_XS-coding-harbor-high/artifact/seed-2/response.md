Save the following as a single `.html` file and open it in Chrome.

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>3D Voxel Harbor Scene</title>
  <style>
    html, body {
      margin: 0;
      height: 100%;
      overflow: hidden;
      background: #97d1e4;
      font-family: system-ui, -apple-system, sans-serif;
    }
    canvas {
      display: block;
    }
    #hint {
      position: absolute;
      top: 14px;
      left: 14px;
      padding: 10px 14px;
      background: rgba(0, 0, 0, 0.35);
      color: #fff;
      border-radius: 8px;
      pointer-events: none;
      font-size: 14px;
      line-height: 1.35;
      z-index: 10;
    }
  </style>
</head>
<body>
  <div id="hint">
    Drag to orbit, scroll to zoom, double-click to reset.
  </div>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script>
    (function () {
      if (typeof THREE === "undefined") {
        document.getElementById("hint").textContent =
          "Three.js failed to load from CDN. Please check your internet connection.";
        return;
      }

      const C = {
        water: "#337185",
        waterLight: "#4a8295",
        waterDark: "#286070",

        shore: "#897856",
        path: "#a59680",
        quay: "#a3794d",
        pier: "#8b633d",
        wood: "#6b4323",
        cargo: "#5c7543",

        hull: "#834c2f",
        hullDark: "#3c2511",
        deck: "#77553d",
        trim: "#a5694a",
        cabin: "#7a4b2c",

        mast: "#b48151",
        sail: "#f2efe5",
        rope: "#635128",
        flag: "#d64844",
        metal: "#7d8890",

        stone: "#8f8167",
        wallCream: "#c9b483",
        wallStone: "#8b7759",
        wallBrick: "#b6614d",
        roofRed: "#b64b42",
        roofBlue: "#3f648c",
        roofGreen: "#597b59",

        window: "#466064",
        door: "#5e432a",

        lamp: "#f5d664",
        cloud: "#f5f6f6",
        lightWhite: "#f2efe9",
        lighthouseRed: "#b64b42"
      };

      const world = {};
      const ship = {};

      function addCube(obj, x, y, z, color) {
        obj[color] = obj[color] || [];
        obj[color].push([x, y, z]);
      }

      function fill(obj, x1, y1, z1, x2, y2, z2, color) {
        for (let x = x1; x <= x2; x++) {
          for (let y = y1; y <= y2; y++) {
            for (let z = z1; z <= z2; z++) {
              addCube(obj, x, y, z, color);
            }
          }
        }
      }

      function line(obj, x0, y0, z0, x1, y1, z1, color) {
        const max = Math.max(Math.abs(x1 - x0), Math.abs(y1 - y0), Math.abs(z1 - z0));
        for (let i = 0; i <= max; i++) {
          const step = max === 0 ? 0 : i / max;
          const x = Math.round(x0 + (x1 - x0) * step);
          const y = Math.round(y0 + (y1 - y0) * step);
          const z = Math.round(z0 + (z1 - z0) * step);
          addCube(obj, x, y, z, color);
        }
      }

      function addPerimeter(obj, x1, z1, x2, z2, y, color) {
        for (let x = x1; x <= x2; x++) {
          addCube(obj, x, y, z1, color);
          addCube(obj, x, y, z2, color);
        }
        for (let z = z1; z <= z2; z++) {
          addCube(obj, x1, y, z, color);
          addCube(obj, x2, y, z, color);
        }
      }

      function addRoof(obj, cx, cz, hx, hz, y0, color) {
        for (let dy = 0; dy < 4; dy++) {
          const sx = Math.max(0, hx - dy);
          const sz = Math.max(0, hz - dy);
          fill(obj, cx - sx, y0 + dy, cz - sz, cx + sx, y0 + dy, cz + sz, color);
        }
      }

      function addBuilding(obj, cx, cz, halfX, halfZ, height, wall, roof) {
        fill(obj, cx - halfX, 2, cz - halfZ, cx + halfX, height + 1, cz + halfZ, wall);
        addRoof(obj, cx, cz, halfX, halfZ, height + 2, roof);
        addCube(obj, cx, 3, cz - halfZ, C.window);
        addCube(obj, cx - 1, 3, cz - halfZ, C.window);
        addCube(obj, cx, 2, cz - halfZ, C.door);
      }

      let seed = 2024;
      function rand() {
        seed = (seed * 9301 + 49297) % 233280;
        return seed / 233280;
      }

      /* Water */
      fill(world, -30, 0, -28, 30, 0, 15, C.water);

      for (let i = 0; i < 140; i++) {
        const x = Math.floor(rand() * 62) - 31;
        const z = Math.floor(rand() * 44) - 28;
        if (x >= -30 && x <= 30 && z >= -28 && z <= 15) {
          const waveColor = rand() < 0.55 ? C.waterLight : C.waterDark;
          addCube(world, x, 1, z, waveColor);
        }
      }

      /* Harbor shore and quay edge */
      fill(world, -30, 1, 18, 30, 1, 34, C.shore);
      fill(world, -30, 1, 17, 30, 1, 17, C.quay);

      /* Pier */
      fill(world, -5, 0, -1, -3, 0, 17, C.wood);
      fill(world, -5, 1, 0, -3, 1, 17, C.pier);

      for (let z = 2; z <= 17; z += 3) {
        addCube(world, -4, 2, z, C.wood);
        addCube(world, -4, 3, z, C.wood);
        addCube(world, -4, 4, z, C.wood);
        addCube(world, -5, 4, z, C.wood);
        addCube(world, -3, 4, z, C.wood);
        addCube(world, -4, 5, z, C.wood);
        addCube(world, -4, 6, z, C.wood);
      }

      /* Cargo crates */
      fill(world, -4, 1, 4, -3, 3, 5, C.cargo);
      fill(world, -4, 1, 10, -3, 3, 11, C.cargo);

      /* Small rowboat */
      fill(world, 7, 1, 10, 9, 3, 12, C.wood);
      line(world, 8, 4, 10, 8, 6, 10, C.metal);
      fill(world, 8, 5, 10, 8, 6, 10, C.sail);
      addCube(world, 8, 4, 11, C.rope);

      /* Buildings */
      addBuilding(world, 2, 22, 2, 2, 3, C.wallStone, C.roofBlue);
      addBuilding(world, 7, 22, 3, 2, 4, C.wallCream, C.roofRed);
      addBuilding(world, 12, 22, 3, 2, 4, C.wallBrick, C.roofBlue);

      addBuilding(world, -20, 24, 3, 3, 4, C.wallCream, C.roofGreen);
      addBuilding(world, -14, 24, 3, 3, 4, C.wallStone, C.roofRed);
      addBuilding(world, -8, 25, 4, 3, 4, C.wallCream, C.roofBlue);

      addBuilding(world, 20, 23, 2, 3, 4, C.wallBrick, C.roofRed);

      /* Lighthouse */
      fill(world, 27, 1, 24, 29, 1, 26, C.path);
      fill(world, 27, 2, 25, 29, 9, 27, C.lightWhite);

      for (let y = 3; y <= 8; y++) {
        if (y % 3 === 0) {
          fill(world, 27, y, 25, 29, y, 27, C.lighthouseRed);
        }
      }

      fill(world, 27, 10, 25, 29, 10, 27, C.stone);
      fill(world, 27, 11, 25, 29, 11, 27, C.lamp);
      fill(world, 28, 12, 25, 28, 12, 26, C.stone);

      /* Light beam */
      line(world, 28, 12, 26, 33, 12, 30, C.lamp);

      /* Harbor crane */
      line(world, -6, 1, 19, -6, 5, 19, C.mast);
      line(world, -6, 5, 19, -3, 5, 19, C.mast);
      line(world, -3, 5, 19, -3, 4, 19, C.rope);
      addCube(world, -3, 3, 19, C.cargo);
      addCube(world, -5, 6, 19, C.rope);

      /* Shore lamp and flag */
      line(world, 5, 1, 18, 5, 5, 18, C.metal);
      addCube(world, 5, 6, 18, C.lamp);

      line(world, 11, 1, 18, 11, 6, 18, C.rope);
      addCube(world, 12, 7, 18, C.flag);
      addCube(world, 13, 7, 18, C.flag);

      /* Anchor / mooring rope */
      line(world, -3, 1, 14, 0, 1, 14, C.rope);

      /* Clouds */
      fill(world, -8, 16, -6, -5, 18, -3, C.cloud);
      fill(world, -2, 17, 4, 3, 18, 5, C.cloud);
      fill(world, 12, 16, -1, 15, 18, 2, C.cloud);
      fill(world, 17, 17, 18, 19, 18, 19, C.cloud);

      /* Voxel sailing ship, local coordinates relative to shipGroup origin */
      fill(ship, -2, 1, -8, 2, 2, 8, C.hull);
      fill(ship, -2, 3, -7, 2, 3, 7, C.deck);
      addPerimeter(ship, -2, -7, 2, 7, 4, C.trim);

      fill(ship, -1, 3, -8, 1, 4, -6, C.cabin);
      addCube(ship, 0, 4, -7, C.window);

      fill(ship, -1, 3, 7, 1, 3, 8, C.deck);
      addCube(ship, 0, 4, 8, C.trim);

      /* Gun ports */
      for (let z = -6; z <= 6; z++) {
        addCube(ship, 2, 2, z, C.hullDark);
        addCube(ship, -2, 2, z, C.hullDark);
      }

      /* Main mast and sail */
      line(ship, 0, 3, 0, 0, 10, 0, C.mast);
      fill(ship, -4, 8, 0, 4, 8, 0, C.mast);
      fill(ship, -3, 4, 0, 3, 7, 0, C.sail);

      /* Foremast */
      line(ship, 0, 3, 4, 0, 10, 4, C.mast);
      fill(ship, -2, 7, 4, 2, 7, 4, C.mast);
      fill(ship, -2, 4, 4, 2, 6, 4, C.sail);

      /* Mizzen mast */
      line(ship, 0, 3, -4, 0, 8, -4, C.mast);
      fill(ship, -1, 7, -4, 1, 7, -4, C.mast);
      fill(ship, -1, 4, -4, 1, 6, -4, C.sail);

      /* Bowsprit */
      line(ship, 0, 4, 8, 0, 4, 12, C.mast);

      /* Jib sail */
      fill(ship, -1, 4, 8, 1, 6, 8, C.sail);

      /* Rigging */
      line(ship, 0, 4, 0, 0, 8, 0, C.rope);
      line(ship, 0, 4, 4, 0, 7, 4, C.rope);
      line(ship, 0, 4, -4, 0, 7, -4, C.rope);

      /* Top platforms */
      line(ship, -2, 6, 0, 2, 6, 0, C.deck);
      line(ship, -1, 6, 4, 1, 6, 4, C.deck);

      /* Flags */
      addCube(ship, 0, 10, 0, C.flag);
      line(ship, 0, 10, 0, 2, 10, 0, C.flag);

      addCube(ship, 0, 10, 4, C.flag);
      line(ship, 0, 10, 4, 1, 10, 4, C.flag);

      addCube(ship, 0, 8, -4, C.flag);
      line(ship, 0, 8, -4, 1, 8, -4, C.flag);

      /* Renderer / scene */
      const renderer = new THREE.WebGLRenderer({ antialias: true });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      renderer.setSize(window.innerWidth, window.innerHeight);
      renderer.setClearColor(0x97d1e4);
      document.body.appendChild(renderer.domElement);

      const scene = new THREE.Scene();
      scene.background = new THREE.Color(0x97d1e4);
      scene.fog = new THREE.Fog(0x97d1e4, 90, 220);

      const camera = new THREE.PerspectiveCamera(
        55,
        window.innerWidth / window.innerHeight,
        0.1,
        1000
      );

      const focus = new THREE.Vector3(-1, 5, 2);
      let theta = -0.85;
      let phi = 0.82;
      let radius = 52;

      function updateCamera() {
        const sinPhi = Math.sin(phi);
        camera.position.set(
          focus.x + radius * sinPhi * Math.cos(theta),
          focus.y + radius * Math.cos(phi),
          focus.z + radius * sinPhi * Math.sin(theta)
        );
        camera.lookAt(focus);
      }

      scene.add(new THREE.HemisphereLight(0xddeeff, 0x614e36, 0.8));
      scene.add(new THREE.AmbientLight(0xffffff, 0.35));

      const sun = new THREE.DirectionalLight(0xffffff, 0.75);
      sun.position.set(30, 35, 18);
      scene.add(sun);

      const lampLight = new THREE.PointLight(0xffd583, 0.8, 40);
      lampLight.position.set(28, 12, 26);
      scene.add(lampLight);

      const cube = new THREE.BoxGeometry(0.96, 0.96, 0.96);

      function buildMeshes(obj, group) {
        for (const color in obj) {
          const points = obj[color];
          if (!points.length) continue;

          const material = new THREE.MeshLambertMaterial({
            color: new THREE.Color(color),
            flatShading: true
          });

          const mesh = new THREE.InstancedMesh(cube, material, points.length);
          const dummy = new THREE.Object3D();

          for (let i = 0; i < points.length; i++) {
            const [x, y, z] = points[i];
            dummy.position.set(x, y, z);
            dummy.updateMatrix();
            mesh.setMatrixAt(i, dummy.matrix);
          }

          mesh.instanceMatrix.needsUpdate = true;
          group.add(mesh);
        }
      }

      const worldGroup = new THREE.Group();
      const shipGroup = new THREE.Group();

      buildMeshes(world, worldGroup);
      buildMeshes(ship, shipGroup);

      shipGroup.position.set(0, 0, 3);
      scene.add(worldGroup);
      scene.add(shipGroup);

      /* Mouse controls */
      const canvas = renderer.domElement;
      canvas.style.touchAction = "none";

      let dragging = false;
      let prev = { x: 0, y: 0 };

      canvas.addEventListener("contextmenu", (e) => e.preventDefault());

      canvas.addEventListener("pointerdown", (e) => {
        if (e.button !== 0) return;
        e.preventDefault();
        dragging = true;
        prev = { x: e.clientX, y: e.clientY };
      });

      window.addEventListener("pointerup", () => {
        dragging = false;
      });

      window.addEventListener("pointermove", (e) => {
        if (!dragging) return;
        const dx = e.clientX - prev.x;
        const dy = e.clientY - prev.y;
        prev = { x: e.clientX, y: e.clientY };

        theta += dx * 0.009;
        phi = Math.max(0.1, Math.min(1.4, phi - dy * 0.007));

        updateCamera();
      });

      canvas.addEventListener("wheel", (e) => {
        e.preventDefault();
        radius = Math.max(12, Math.min(160, radius + e.deltaY * 0.08));
        updateCamera();
      }, { passive: false });

      function reset() {
        theta = -0.85;
        phi = 0.82;
        radius = 52;
        focus.set(-1, 5, 2);
        updateCamera();
      }

      canvas.addEventListener("dblclick", reset);

      window.addEventListener("resize", () => {
        renderer.setSize(window.innerWidth, window.innerHeight);
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        updateCamera();
      });

      updateCamera();

      const clock = new THREE.Clock();
      const baseShipY = 0;

      function renderLoop() {
        const t = clock.getElapsedTime();

        shipGroup.position.y = baseShipY + Math.sin(t * 1.1) * 0.08;
        shipGroup.rotation.z = Math.sin(t * 0.6) * 0.018;

        renderer.render(scene, camera);
        requestAnimationFrame(renderLoop);
      }

      renderLoop();
    })();
  </script>
</body>
</html>
```