```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Voxel Harbor: A Sailing Ship Calling at Harbor</title>
  <style>
    html, body {
      margin: 0;
      width: 100%;
      height: 100%;
      overflow: hidden;
      background: #1b334b;
      font-family: sans-serif;
    }
    canvas {
      display: block;
    }
    #overlay {
      position: absolute;
      top: 12px;
      left: 12px;
      color: #ffffff;
      background: rgba(0, 0, 0, 0.55);
      padding: 10px 14px;
      border-radius: 10px;
      font-size: 14px;
      line-height: 1.35;
    }
    #overlay strong {
      display: block;
      margin-bottom: 4px;
    }
    #overlay span {
      color: #b8d8ff;
    }
  </style>
</head>
<body>
  <div id="overlay">
    <strong>🌊🎨 Voxel Harbor: A Sailing Ship Calling at Harbor</strong>
    <span>Drag to rotate, scroll to zoom. Auto-rotate is enabled.</span>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>

  <script>
    const voxelData = new Map();

    function addVoxel(x, y, z, color) {
      if (!voxelData.has(color)) {
        voxelData.set(color, []);
      }
      voxelData.get(color).push([x, y, z]);
    }

    function addBox(x0, x1, y0, y1, z0, z1, color) {
      for (let x = x0; x <= x1; x++) {
        for (let y = y0; y <= y1; y++) {
          for (let z = z0; z <= z1; z++) {
            addVoxel(x, y, z, color);
          }
        }
      }
    }

    function buildScene() {
      /*
        Coordinate system:
        x: left/right
        y: up/down
        z: front/back

        Water surface is at y = 0.
        Dock/quay surface is at y = 2.
        Ship hull floats above the water.
      */

      // Ocean surface
      for (let x = -32; x <= 32; x++) {
        for (let z = -32; z <= 32; z++) {
          let color = "#103d68";

          if ((x + z) % 5 === 0) color = "#174d83";
          if ((x - z) % 7 === 0) color = "#0f3052";

          // Foam/waves around the ship
          if (Math.abs(x) <= 6 && Math.abs(z) <= 4) color = "#91cbe1";
          if (Math.abs(x) <= 5 && Math.abs(z) <= 3) color = "#c5e6ee";

          addVoxel(x, 0, z, color);
        }
      }

      // Harbor quay
      addBox(8, 26, 1, 2, -13, 13, "#d6c59a");

      // Pier extending toward the ship
      addBox(6, 10, 2, 2, 0, 6, "#e9d7ab");

      // Breakwater/rocks on the harbor entrance
      addBox(4, 12, 1, 1, -18, -15, "#6d7a80");
      addBox(4, 12, 1, 1, 15, 18, "#6d7a80");

      // Dock bollards
      addBox(8, 8, 3, 3, -4, -4, "#544333");
      addBox(8, 8, 3, 3, 1, 1, "#544333");
      addBox(11, 11, 3, 3, -1, -1, "#544333");

      // Harbor buildings
      addBox(12, 16, 3, 5, -9, -4, "#b36a52");
      addBox(11, 17, 6, 6, -8, -3, "#51332e");
      addBox(12, 16, 4, 4, -5, -5, "#d8e9e5");

      addBox(19, 23, 3, 4, -12, -8, "#c69f86");
      addBox(18, 24, 5, 5, -11, -7, "#65524d");
      addBox(19, 23, 4, 4, -8, -8, "#d4e4e2");

      // Lighthouse
      addBox(20, 22, 3, 3, 4, 6, "#888888");

      for (let y = 4; y <= 9; y++) {
        addBox(21, 21, y, y, 5, 5, y % 2 === 0 ? "#f3efe4" : "#d64646");
      }

      addBox(21, 21, 10, 10, 5, 5, "#f6f6f0");
      addBox(21, 21, 11, 11, 5, 5, "#fff7a0");

      // Palm trees
      const palm = (x, z) => {
        addBox(x, x, 3, 5, z, z, "#8e5a39");
        addBox(x - 2, x + 2, 6, 6, z - 2, z + 2, "#2b7d58");
        addBox(x, x, 7, 7, z, z, "#256c4d");
      };

      palm(14, -6);
      palm(16, 8);
      palm(23, -11);

      // Small buoys
      const buoy = (x, z) => {
        addBox(x, x, 1, 1, z, z, "#ff6b3c");
        addBox(x, x, 2, 2, z, z, "#ff9c4f");
      };

      buoy(7, -10);
      buoy(12, -10);
      buoy(24, -16);
      buoy(24, 17);

      // Sailing ship hull
      const maxZ = (x) => {
        if (x <= -6) return 1;
        if (x <= -2) return 3;
        if (x <= 2) return 2;
        if (x <= 4) return 1;
        return 0;
      };

      for (let x = -6; x <= 5; x++) {
        const m = maxZ(x);

        for (let y = 1; y <= 3; y++) {
          let color;
          if (y === 1) color = "#37291e";
          else if (y === 2) color = "#4f3427";
          else color = "#684b38";

          for (let z = -m; z <= m; z++) {
            addVoxel(x, y, z, color);
          }
        }
      }

      // Bow extension / bowsprit
      addVoxel(6, 3, 0, "#7d6141");

      // Cabin
      addBox(-4, 1, 4, 5, -1, 1, "#7b5839");
      addBox(-4, 1, 4, 4, -2, -2, "#d5e6e1");
      addBox(-4, 1, 4, 4, 2, 2, "#d5e6e1");

      // Masts
      const mast = (x, top) => {
        for (let y = 4; y <= top; y++) {
          addVoxel(x, y, 0, "#6a4733");
        }
      };

      mast(-5, 10);
      mast(-1, 11);
      mast(3, 10);
      mast(-6, 7);

      // Flag
      addBox(-6, -6, 8, 9, -1, 1, "#e2524b");

      // Sails
      addBox(-4, -3, 5, 7, -2, 2, "#f8f0dc");
      addBox(-4, -3, 8, 9, -1, 1, "#f8f0dc");

      addBox(0, 1, 5, 9, -3, 3, "#fff8ea");
      addBox(0, 1, 10, 11, -2, 2, "#fff8ea");

      addBox(4, 5, 5, 7, -2, 2, "#f8f0dc");
      addBox(4, 5, 8, 9, -1, 1, "#f8f0dc");

      // Rope/gangway to the dock
      addBox(5, 7, 3, 3, 2, 2, "#b8c9b6");
    }

    buildScene();

    const scene = new THREE.Scene();
    scene.background = new THREE.Color("#1b334b");
    scene.fog = new THREE.Fog("#1b334b", 60, 150);

    const camera = new THREE.PerspectiveCamera(
      45,
      window.innerWidth / window.innerHeight,
      0.1,
      250
    );

    camera.position.set(28, 22, 32);
    camera.lookAt(5, 4, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.target.set(5, 4, 0);
    controls.autoRotate = true;
    controls.autoRotateSpeed = 0.75;
    controls.enableDamping = true;
    controls.update();

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.45);
    scene.add(ambientLight);

    const sun = new THREE.DirectionalLight(0xffefc8, 0.9);
    sun.position.set(28, 40, 20);
    scene.add(sun);

    const geometry = new THREE.BoxGeometry(0.96, 0.96, 0.96);
    const matrix = new THREE.Matrix4();

    for (const [color, voxelList] of voxelData.entries()) {
      if (!voxelList.length) continue;

      const material = new THREE.MeshLambertMaterial({
        color: new THREE.Color(color)
      });

      const mesh = new THREE.InstancedMesh(geometry, material, voxelList.length);

      for (let i = 0; i < voxelList.length; i++) {
        const [x, y, z] = voxelList[i];

        matrix.set(
          1, 0, 0, x,
          0, 1, 0, y,
          0, 0, 1, z,
          0, 0, 0, 1
        );

        mesh.setMatrixAt(i, matrix);
      }

      mesh.instanceMatrix.needsUpdate = true;
      scene.add(mesh);
    }

    window.addEventListener("resize", () => {
      renderer.setSize(window.innerWidth, window.innerHeight);
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
    });

    function animate() {
      controls.update();
      renderer.render(scene, camera);
      requestAnimationFrame(animate);
    }

    animate();
  </script>
</body>
</html>
```