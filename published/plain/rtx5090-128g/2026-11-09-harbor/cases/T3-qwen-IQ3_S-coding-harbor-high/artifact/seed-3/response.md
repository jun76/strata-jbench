Save this as a single `.html` file and open it in Chrome. It uses Three.js from a CDN, so you need an internet connection.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Voxel Harbor: Sailing Ship Calling at Harbor</title>
<style>
  html, body {
    margin: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
    background: #9fd8ff;
  }
  canvas {
    display: block;
    cursor: grab;
  }
  #hint {
    position: fixed;
    left: 12px;
    top: 12px;
    color: #183a55;
    font: 14px/1.35 system-ui, sans-serif;
    background: rgba(255,255,255,0.72);
    padding: 8px 10px;
    border-radius: 10px;
    pointer-events: none;
  }
</style>
</head>
<body>
<div id="hint">Drag with the mouse to orbit. Scroll to zoom. Double-click to reset.</div>

<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js"></script>
<script>
(function () {
  if (typeof THREE === "undefined") {
    document.getElementById("hint").textContent =
      "Could not load Three.js. Please connect to the internet and reload.";
    return;
  }

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x9fd8ff);
  scene.fog = new THREE.Fog(0x9fd8ff, 75, 260);

  const camera = new THREE.PerspectiveCamera(50, innerWidth / innerHeight, 0.1, 1000);
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setSize(innerWidth, innerHeight);
  document.body.appendChild(renderer.domElement);

  scene.add(new THREE.HemisphereLight(0xffffff, 0x76654f, 0.95));
  const sun = new THREE.DirectionalLight(0xffe3bd, 0.78);
  sun.position.set(35, 60, 22);
  scene.add(sun);

  const box = new THREE.BoxGeometry(1, 1, 1);
  const voxelMaterial = new THREE.MeshLambertMaterial({ color: 0xffffff });
  const helper = new THREE.Object3D();

  const staticVoxels = [];
  const shipVoxels = [];
  const waterVoxels = [];

  function makeColor(hex, jitter) {
    const c = new THREE.Color(hex);
    if (jitter) c.offsetHSL(0, 0, (Math.random() - 0.5) * jitter);
    return c;
  }

  function addStatic(x, y, z, hex, jitter = 0.02, scale = 0.96) {
    staticVoxels.push({ x, y, z, c: makeColor(hex, jitter), scale });
  }

  function addShip(x, y, z, hex, jitter = 0.02, scale = 0.95) {
    shipVoxels.push({ x, y, z, c: makeColor(hex, jitter), scale });
  }

  function addWater(x, y, z, hex, jitter = 0.05, scale = 0.98, animate = false) {
    waterVoxels.push({ x, y, z, baseY: y, c: makeColor(hex, jitter), scale, animate });
  }

  function buildWater() {
    for (let x = -48; x <= 13; x++) {
      for (let z = -24; z <= 24; z++) {
        if (x >= 10 && ((z >= -13 && z <= -12) || (z >= 12 && z <= 13))) {
          continue;
        }

        const animate = x >= -26 && x <= 12 && z > -19 && z < 19;
        let hex = 0x1d5d8f;

        if (x > 5) hex = 0x2f7fae;
        if (z > -8 && z < 8 && x < 0) hex = 0x1a4f78;
        if (x >= 12 && Math.abs(z) < 15 && (x + z) % 3 === 0) hex = 0x4890c0;

        addWater(x, 0, z, hex, 0.06, 0.98, animate);
      }
    }
  }

  function buildPier(z1, z2) {
    for (let x = 10; x <= 14; x++) {
      for (let z = z1; z <= z2; z++) {
        addStatic(x, 2, z, 0x8c5f34, 0.03, 0.96);
      }
    }

    const postsX = [10, 13];
    const postsZ = [z1, z2];

    for (const x of postsX) {
      for (const z of postsZ) {
        for (let y = 0; y <= 1; y++) {
          addStatic(x, y, z, 0x5b3a1f, 0.02, 0.88);
        }
      }
    }
  }

  function addTree(x, z) {
    addStatic(x, 3, z, 0x5c3b21, 0.02, 0.85);
    addStatic(x, 4, z, 0x5c3b21, 0.02, 0.85);

    for (let y = 5; y <= 7; y++) {
      for (let dx = -1; dx <= 1; dx++) {
        for (let dz = -1; dz <= 1; dz++) {
          addStatic(x + dx, y, z + dz, 0x4d7d33, 0.05, 0.9);
        }
      }
    }

    addStatic(x, 8, z, 0x4d7d33, 0.04, 0.75);
  }

  function addCrate(x, z) {
    addStatic(x, 3, z, 0x8d6134, 0.03, 0.92);
    addStatic(x, 4, z, 0x8d6134, 0.03, 0.82);
  }

  function addBarrel(x, z) {
    addStatic(x, 3, z, 0x9e7244, 0.02, 0.72);
    addStatic(x, 4, z, 0x9e7244, 0.02, 0.72);
  }

  function buildHarbor() {
    // Land behind the quay.
    for (let x = 38; x <= 58; x++) {
      for (let z = -22; z <= 22; z++) {
        const n = (x * 7 + z * 13 + 11) % 23;
        let y = 2;

        if (n === 0) y = 3;
        if (x > 46 && n === 1) y = 4;

        const c = y === 2 ? 0x72a359 : y === 3 ? 0x5d8a46 : 0x4e7338;
        addStatic(x, y, z, c, 0.05, 0.98);
      }
    }

    // Main quay platform.
    for (let x = 15; x <= 38; x++) {
      for (let z = -14; z <= 14; z++) {
        const palette = [0x919191, 0x848484, 0x7b7b7b, 0x979797];
        addStatic(x, 2, z, palette[(x + z + 100) % 4], 0.04, 0.98);
      }
    }

    // Quay front wall.
    for (let y = 0; y <= 2; y++) {
      for (let z = -15; z <= 15; z++) {
        addStatic(14, y, z, 0x696969, 0.04, 0.98);
      }
    }

    // Quay side walls.
    for (let x = 15; x <= 38; x++) {
      for (let y = 1; y <= 2; y++) {
        addStatic(x, y, -15, 0x696969, 0.04, 0.98);
        addStatic(x, y, 15, 0x696969, 0.04, 0.98);
      }
    }

    // Quay back wall.
    for (let z = -15; z <= 15; z++) {
      for (let y = 1; y <= 2; y++) {
        addStatic(39, y, z, 0x696969, 0.04, 0.98);
      }
    }

    // Low curb along the dock edge.
    for (let z = -14; z <= 14; z++) {
      if (z % 2 === 0) addStatic(15, 3, z, 0x5f5f5f, 0.02, 0.9);
    }

    // Bollards.
    for (let z = -12; z <= 12; z += 4) {
      addStatic(16, 3, z, 0x262626, 0, 0.72);
      addStatic(16, 4, z, 0x353535, 0, 0.55);
    }

    // Two piers framing the ship.
    buildPier(-13, -12);
    buildPier(12, 13);

    // Gangplank toward the ship.
    for (let x = 10; x <= 13; x++) {
      for (let z = -5; z <= -4; z++) {
        addStatic(x, 2, z, 0xbb8250, 0.02, 0.94);
      }
    }
    addStatic(14, 3, -5, 0x333333, 0, 0.75);
    addStatic(14, 3, -4, 0x333333, 0, 0.75);

    // Warehouse.
    for (let y = 3; y <= 5; y++) {
      for (let x = 24; x <= 30; x++) {
        for (let z = 4; z <= 9; z++) {
          addStatic(x, y, z, 0xc1654b, 0.04, 0.95);
        }
      }
    }

    // Warehouse roof.
    for (let x = 23; x <= 31; x++) {
      for (let z = 4; z <= 9; z++) {
        addStatic(x, 6, z, 0x6e4c3b, 0.02, 0.97);
      }
    }
    for (let x = 24; x <= 30; x++) {
      for (let z = 5; z <= 8; z++) {
        addStatic(x, 7, z, 0x6e4c3b, 0.02, 0.95);
      }
    }

    // Warehouse door.
    addStatic(27, 3, 3, 0x4b3323, 0.02, 0.8);
    addStatic(27, 4, 3, 0x4b3323, 0.02, 0.8);

    // Lighthouse.
    for (let y = 3; y <= 10; y++) {
      for (let x = 31; x <= 32; x++) {
        for (let z = -11; z <= -10; z++) {
          const c = y % 2 === 0 ? 0xe9e9e9 : 0xc43f39;
          addStatic(x, y, z, c, 0.02, 0.96);
        }
      }
    }
    for (let x = 31; x <= 32; x++) {
      for (let z = -11; z <= -10; z++) {
        addStatic(x, 11, z, 0x3c3c3c, 0.01, 0.9);
      }
    }

    // Harbor crane.
    addStatic(20, 2, 6, 0x8e5f33, 0.02, 0.9);
    for (let y = 3; y <= 5; y++) {
      addStatic(20, y, 6, 0x8e5f33, 0.02, 0.82);
    }
    for (let x = 18; x <= 24; x++) {
      addStatic(x, 5, 6, 0x8e5f33, 0.02, 0.85);
    }
    addStatic(22, 4, 6, 0x333333, 0, 0.35);
    addStatic(22, 3, 6, 0x6f4a2a, 0.02, 0.9);

    // Crates and barrels on the quay.
    addCrate(18, -10);
    addCrate(19, -10);
    addCrate(18, -9);
    addCrate(21, 11);
    addCrate(22, 11);
    addBarrel(19, -6);
    addBarrel(20, -6);

    // Mooring line suggestion.
    for (let x = 10; x <= 16; x++) {
      addStatic(x, 3, 7, 0x1f1f1f, 0, 0.35);
    }

    // Trees on the land behind.
    addTree(44, -16);
    addTree(48, -6);
    addTree(52, 6);
    addTree(46, 15);
    addTree(55, -12);
  }

  function buildShip() {
    const hullSXLow = 5.0;
    const hullSZLow = 10.5;
    const hullSXHigh = 5.2;
    const hullSZHigh = 10.8;

    // Lower hull.
    for (let x = -5; x <= 5; x++) {
      for (let z = -12; z <= 12; z++) {
        if (Math.pow(x / hullSXLow, 2) + Math.pow(z / hullSZLow, 2) <= 1) {
          addShip(x, 1, z, 0x5a3622, 0.05, 0.96);
        }
      }
    }

    // Upper hull / deck level.
    for (let x = -5; x <= 5; x++) {
      for (let z = -12; z <= 12; z++) {
        if (Math.pow(x / hullSXHigh, 2) + Math.pow(z / hullSZHigh, 2) <= 1) {
          const edge = Math.abs(x) >= 4 || Math.abs(z) >= 9;
          addShip(x, 2, z, edge ? 0x764c2d : 0xa77844, 0.04, 0.95);
        }
      }
    }

    // Sterncastle.
    for (let x = -2; x <= 2; x++) {
      for (let z = -10; z <= -6; z++) {
        addShip(x, 3, z, 0x744c30, 0.03, 0.95);
      }
    }

    // Bowcastle.
    for (let x = -1; x <= 1; x++) {
      for (let z = 7; z <= 10; z++) {
        addShip(x, 3, z, 0x744c30, 0.03, 0.95);
      }
    }

    // Small stern lantern cabin.
    for (let x = -1; x <= 1; x++) {
      addShip(x, 4, -8, 0x7b5335, 0.02, 0.9);
    }

    // Deck rail.
    for (let z = -9; z <= 9; z++) {
      if (Math.pow(-5 / hullSXHigh, 2) + Math.pow(z / hullSZHigh, 2) <= 1) {
        addShip(-5, 3, z, 0x5c3b23, 0.02, 0.8);
      }
      if (Math.pow(5 / hullSXHigh, 2) + Math.pow(z / hullSZHigh, 2) <= 1) {
        addShip(5, 3, z, 0x5c3b23, 0.02, 0.8);
      }
    }

    // Bowsprit.
    for (let z = 10; z <= 14; z++) {
      addShip(0, 3, z, 0x795836, 0.02, 0.88);
    }
    for (let z = 12; z <= 14; z++) {
      addShip(0, 4, z, 0x795836, 0.02, 0.75);
    }

    function addMast(z, maxY) {
      for (let y = 3; y <= maxY; y++) {
        addShip(0, y, z, 0x7c5a37, 0.02, 0.92);
      }
    }

    function addYard(z, y, half) {
      for (let x = -half; x <= half; x++) {
        addShip(x, y, z, 0x7c5a37, 0.02, 0.85);
      }
    }

    function addSail(z, y1, y2, half) {
      for (let y = y1; y <= y2; y++) {
        for (let x = -half; x <= half; x++) {
          addShip(x, y, z, 0xf3efe4, 0.03, 0.94);
        }
      }
    }

    // Mizzen.
    addMast(-6, 11);
    addYard(-6, 4, 2);
    addYard(-6, 7, 2);
    addYard(-6, 9, 1);
    addSail(-6, 5, 6, 2);
    addSail(-6, 8, 8, 1);

    // Main mast.
    addMast(-1, 14);
    addYard(-1, 4, 4);
    addYard(-1, 7, 4);
    addYard(-1, 10, 3);
    addYard(-1, 12, 2);
    addSail(-1, 5, 6, 4);
    addSail(-1, 8, 9, 3);
    addSail(-1, 11, 11, 2);

    // Fore mast.
    addMast(4, 13);
    addYard(4, 4, 4);
    addYard(4, 7, 4);
    addYard(4, 10, 3);
    addYard(4, 12, 2);
    addSail(4, 5, 6, 4);
    addSail(4, 8, 9, 3);
    addSail(4, 11, 11, 2);

    // Flag.
    for (let x = 1; x <= 3; x++) {
      addShip(x, 14, -1, 0xcf4b3c, 0, 0.92);
      addShip(x, 13, -1, 0xcf4b3c, 0, 0.92);
    }
  }

  buildWater();
  buildHarbor();
  buildShip();

  function makeInstanced(arr) {
    if (!arr.length) return null;

    const mesh = new THREE.InstancedMesh(box, voxelMaterial, arr.length);

    for (let i = 0; i < arr.length; i++) {
      const v = arr[i];
      helper.position.set(v.x, v.y, v.z);
      helper.scale.set(v.scale, v.scale, v.scale);
      helper.updateMatrix();
      mesh.setMatrixAt(i, helper.matrix);
      mesh.setColorAt(i, v.c);
    }

    mesh.instanceMatrix.needsUpdate = true;
    if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
    return mesh;
  }

  const staticMesh = makeInstanced(staticVoxels);
  if (staticMesh) scene.add(staticMesh);

  const shipGroup = new THREE.Group();
  const shipMesh = makeInstanced(shipVoxels);
  if (shipMesh) {
    shipGroup.add(shipMesh);
    shipGroup.position.set(5, 0.04, 0);
    scene.add(shipGroup);
  }

  const waterMesh = makeInstanced(waterVoxels);
  if (waterMesh) scene.add(waterMesh);

  const seaPlane = new THREE.Mesh(
    new THREE.PlaneGeometry(650, 650),
    new THREE.MeshLambertMaterial({ color: 0x11374f })
  );
  seaPlane.rotation.x = -Math.PI / 2;
  seaPlane.position.y = -0.75;
  scene.add(seaPlane);

  const beacon = new THREE.PointLight(0xffdf66, 0.9, 70);
  beacon.position.set(31.5, 10.5, -10.5);
  scene.add(beacon);

  const waterAnim = [];
  for (let i = 0; i < waterVoxels.length; i++) {
    if (waterVoxels[i].animate) waterAnim.push(i);
  }

  let target = new THREE.Vector3(4, 4, 0);
  let radius = 48;
  let phi = 1.08;
  let theta = -0.88;

  let dragging = false;
  let px = 0;
  let py = 0;

  function updateCamera() {
    radius = Math.max(10, Math.min(120, radius));
    phi = Math.max(0.2, Math.min(1.5, phi));

    camera.position.set(
      target.x + radius * Math.sin(phi) * Math.sin(theta),
      target.y + radius * Math.cos(phi),
      target.z + radius * Math.sin(phi) * Math.cos(theta)
    );

    camera.lookAt(target);
  }

  const dom = renderer.domElement;

  dom.addEventListener("pointerdown", (e) => {
    dragging = true;
    px = e.clientX;
    py = e.clientY;
    dom.style.cursor = "grabbing";
  });

  window.addEventListener("pointermove", (e) => {
    if (!dragging) return;

    const dx = e.clientX - px;
    const dy = e.clientY - py;
    px = e.clientX;
    py = e.clientY;

    theta -= dx * 0.007;
    phi += dy * 0.005;
    updateCamera();
  });

  window.addEventListener("pointerup", () => {
    dragging = false;
    dom.style.cursor = "grab";
  });

  window.addEventListener("wheel", (e) => {
    e.preventDefault();
    radius *= 1 + e.deltaY * 0.001;
    updateCamera();
  }, { passive: false });

  dom.addEventListener("dblclick", () => {
    radius = 48;
    phi = 1.08;
    theta = -0.88;
    updateCamera();
  });

  window.addEventListener("resize", () => {
    camera.aspect = innerWidth / innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(innerWidth, innerHeight);
  });

  updateCamera();

  function animate() {
    requestAnimationFrame(animate);
    const t = performance.now() * 0.001;

    if (waterMesh) {
      for (const i of waterAnim) {
        const v = waterVoxels[i];
        const y = v.baseY + Math.sin(t * 1.55 + v.x * 0.23 + v.z * 0.2) * 0.14;

        helper.position.set(v.x, y, v.z);
        helper.scale.set(v.scale, v.scale, v.scale);
        helper.updateMatrix();
        waterMesh.setMatrixAt(i, helper.matrix);
      }

      waterMesh.instanceMatrix.needsUpdate = true;
    }

    if (shipGroup) {
      shipGroup.position.y = 0.04 + 0.035 * Math.sin(t * 1.1);
    }

    beacon.intensity = 0.6 + 0.55 * (0.5 + 0.5 * Math.sin(t * 2.4));

    renderer.render(scene, camera);
  }

  animate();
})();
</script>
</body>
</html>
```