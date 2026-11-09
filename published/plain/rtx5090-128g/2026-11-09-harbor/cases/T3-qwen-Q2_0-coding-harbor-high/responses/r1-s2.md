Paste the following into a single `.html` file and open it in Chrome.

It uses Three.js from a CDN (so it needs internet access) and renders a voxel-style harbor with a sailing ship, dock, lighthouse, cargo, small boats, and mouse orbit/zoom.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Voxel Harbor — A Sailing Ship Calling</title>
  <style>
    html, body {
      margin: 0;
      height: 100%;
      overflow: hidden;
      background: #9fb8c8;
    }

    .hint {
      position: fixed;
      left: 12px;
      bottom: 12px;
      color: #f7fbff;
      font-family: Arial, sans-serif;
      font-size: 13px;
      pointer-events: none;
      background: rgba(24, 45, 55, 0.55);
      padding: 8px 10px;
      border-radius: 6px;
    }
  </style>
</head>
<body>
  <div class="hint">Drag to orbit • Scroll to zoom</div>

  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js"></script>
  <script>
    const scene = new THREE.Scene();
    scene.background = new THREE.Color('#9fb8c8');

    const camera = new THREE.PerspectiveCamera(
      45,
      window.innerWidth / window.innerHeight,
      0.1,
      1000
    );

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    document.body.appendChild(renderer.domElement);

    scene.add(new THREE.AmbientLight(0xffffff, 0.45));

    const sun = new THREE.DirectionalLight(0xffffff, 0.8);
    sun.position.set(14, 24, 20);
    scene.add(sun);

    const cube = new THREE.BoxGeometry(1, 1, 1);
    const materialCache = new Map();

    function getMaterial(color) {
      if (!materialCache.has(color)) {
        materialCache.set(color, new THREE.MeshLambertMaterial({ color }));
      }
      return materialCache.get(color);
    }

    function addVoxel(x, y, z, color) {
      const mesh = new THREE.Mesh(cube, getMaterial(color));
      mesh.position.set(x, y, z);
      scene.add(mesh);
    }

    function addBlock(x1, x2, y1, y2, z1, z2, color) {
      for (let x = x1; x <= x2; ++x) {
        for (let y = y1; y <= y2; ++y) {
          for (let z = z1; z <= z2; ++z) {
            addVoxel(x, y, z, color);
          }
        }
      }
    }

    function addWater() {
      const shipX1 = -4, shipX2 = 4, shipZ1 = -2, shipZ2 = 2;
      const dockX1 = 5, dockX2 = 9, dockZ1 = -5, dockZ2 = 5;

      for (let x = -14; x <= 9; ++x) {
        for (let z = -14; z <= 14; ++z) {
          if (
            (x >= shipX1 && x <= shipX2 && z >= shipZ1 && z <= shipZ2) ||
            (x >= dockX1 && x <= dockX2 && z >= dockZ1 && z <= dockZ2)
          ) {
            continue;
          }

          const color = ((x + z) % 4 === 0) ? '#2f86a8' : '#215c77';
          addVoxel(x, 0, z, color);
          addVoxel(x, -1, z, '#184961');
        }
      }
    }

    function addDock() {
      // Dock posts / understructure
      addBlock(5, 9, -1, 0, -5, 5, '#553a25');

      // Dock deck
      addBlock(5, 9, 1, 1, -5, -2, '#8a5a3a');
      addBlock(5, 9, 1, 1, -1, 5, '#986845');

      // Bollards at the dock edge
      for (let z = -5; z <= 5; z += 2) {
        addVoxel(5, 2, z, '#483526');
      }

      // Cargo crates
      addBlock(6, 7, 2, 3, -4, -3, '#d0b990');

      // Barrels
      addBlock(7, 8, 2, 2, 1, 2, '#8f5132');

      // Small cloth crate
      addVoxel(8, 2, -1, '#eef3ef');

      // Dock lamps
      addVoxel(6, 2, -2, '#5b4b3d');
      addVoxel(6, 3, -2, '#f6d59e');

      addVoxel(6, 2, 2, '#5b4b3d');
      addVoxel(6, 3, 2, '#f6d59e');
    }

    function addLand() {
      addBlock(10, 16, 0, 0, -8, 8, '#716555');
      addBlock(10, 16, 1, 1, -8, 8, '#3f7859');
    }

    function addHarborBuildings() {
      // Warehouse / buildings
      addBlock(11, 14, 2, 3, -7, -3, '#d8c7ad');
      addBlock(11, 14, 4, 4, -7, -3, '#a74b31');
      addBlock(12, 13, 5, 5, -6, -5, '#e8b366');

      addBlock(14, 16, 2, 3, 1, 5, '#b56b3b');
      addBlock(14, 16, 4, 4, 1, 5, '#723f28');

      // Lighthouse
      addBlock(14, 15, 2, 3, 6, 7, '#e4e2d6');
      addBlock(14, 15, 4, 4, 6, 7, '#b54e4e');
      addBlock(14, 15, 5, 6, 6, 7, '#e4e2d6');
      addBlock(14, 15, 7, 7, 6, 7, '#b54e4e');
      addBlock(14, 15, 8, 8, 6, 7, '#ff806f');
      addBlock(13, 16, 9, 9, 5, 8, '#5e6871');
    }

    function addRocksAndBreakwater() {
      addBlock(-13, -11, 1, 1, -14, -11, '#6e747a');
      addVoxel(-12, 2, -12, '#6e747a');

      addBlock(9, 11, 1, 1, 10, 13, '#6e747a');
      addVoxel(10, 2, 11, '#6e747a');
    }

    function addClouds() {
      addBlock(-9, -6, 8, 8, -5, -2, '#f3f8fa');
      addBlock(-8, -7, 7, 7, -4, -2, '#eef6f9');

      addBlock(8, 11, 8, 8, -4, -1, '#f3f8fa');
    }

    function addRowboat() {
      addBlock(1, 2, 1, 1, 7, 9, '#8d5838');
      addVoxel(1, 2, 8, '#f1e9d7');
      addVoxel(2, 2, 8, '#f1e9d7');
    }

    function addShip() {
      const hull = '#8d4626';
      const hullDark = '#62311c';
      const deck = '#b88958';
      const sail = '#f2efe6';
      const mast = '#6c5848';
      const rig = '#8f8374';
      const flag = '#d9433c';

      // Lower hull
      addBlock(-2, 1, -2, -2, -2, 2, hullDark);

      // Main hull side
      addBlock(-3, 2, -1, -1, -2, 2, hull);

      // Deck
      addBlock(-3, 2, 0, 0, -2, 2, deck);

      // Bow taper
      addVoxel(3, -1, 0, hull);
      addVoxel(3, 0, 0, deck);

      addVoxel(4, -1, 0, hull);
      addVoxel(4, 0, 0, deck);

      // Stern cap
      addVoxel(-4, -1, 0, hullDark);
      addVoxel(-4, 0, 0, hullDark);

      // Stern cabin
      addBlock(-4, -3, 1, 2, -1, 1, '#7b5942');

      // Masts, sails, and rigging
      for (let mx = -2; mx <= 2; mx += 2) {
        for (let y = 1; y <= 6; ++y) {
          addVoxel(mx, y, 0, mast);
        }

        // Lower sail
        addBlock(mx - 1, mx + 1, 3, 4, 0, 0, sail);

        // Upper sail
        addBlock(mx - 1, mx + 1, 5, 5, 0, 0, sail);

        // Simple rigging blocks
        addVoxel(mx, 3, -1, rig);
        addVoxel(mx, 3, 1, rig);
        addVoxel(mx, 4, -1, rig);
        addVoxel(mx, 4, 1, rig);
      }

      // Flag on the front mast
      addVoxel(2, 6, -1, flag);
      addVoxel(2, 6, -2, flag);
      addVoxel(2, 5, -1, flag);
    }

    function buildScene() {
      addWater();
      addDock();
      addLand();
      addHarborBuildings();
      addRocksAndBreakwater();
      addClouds();
      addRowboat();
      addShip();
    }

    buildScene();

    let yaw = 0.70;
    let pitch = 0.30;
    let distance = 38;
    const target = new THREE.Vector3(2, 2, 0);

    function updateCamera() {
      const x = target.x + distance * Math.cos(pitch) * Math.sin(yaw);
      const y = target.y + distance * Math.sin(pitch);
      const z = target.z + distance * Math.cos(pitch) * Math.cos(yaw);

      camera.position.set(x, y, z);
      camera.lookAt(target);
    }

    let dragging = false;
    let lastX = 0;
    let lastY = 0;

    renderer.domElement.addEventListener('pointerdown', (e) => {
      dragging = true;
      lastX = e.clientX;
      lastY = e.clientY;
    });

    window.addEventListener('pointermove', (e) => {
      if (!dragging) return;

      const dx = e.clientX - lastX;
      const dy = e.clientY - lastY;
      lastX = e.clientX;
      lastY = e.clientY;

      yaw -= dx * 0.01;
      pitch -= dy * 0.01;
      pitch = Math.max(-1.25, Math.min(1.25, pitch));
    });

    window.addEventListener('pointerup', () => {
      dragging = false;
    });

    renderer.domElement.addEventListener('wheel', (e) => {
      distance -= e.deltaY * 0.07;
      distance = Math.max(12, Math.min(70, distance));
    }, { passive: true });

    function animate() {
      updateCamera();
      renderer.render(scene, camera);
      requestAnimationFrame(animate);
    }

    updateCamera();
    renderer.render(scene, camera);
    animate();

    window.addEventListener('resize', () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    });
  </script>
</body>
</html>
```