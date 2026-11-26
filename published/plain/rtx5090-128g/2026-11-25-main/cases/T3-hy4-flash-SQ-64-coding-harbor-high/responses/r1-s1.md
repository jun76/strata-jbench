Paste this into a single `.html` file and open it in Chrome:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Voxel Harbor Scene</title>
  <style>
    html, body {
      margin: 0;
      height: 100%;
      overflow: hidden;
      background: #86d3ff;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
    }
    canvas { display: block; }
    #hud {
      position: fixed;
      top: 16px;
      left: 16px;
      padding: 10px 14px;
      background: rgba(8, 32, 56, 0.72);
      color: white;
      border-radius: 10px;
      pointer-events: none;
      box-shadow: 0 8px 24px rgba(0,0,0,0.18);
    }
    #hud h1 {
      margin: 0 0 6px;
      font-size: 18px;
      font-weight: 700;
    }
    #hud p {
      margin: 0;
      font-size: 12px;
      opacity: 0.85;
    }
  </style>
</head>
<body>
  <div id="hud">
    <h1>A sailing ship calling at a harbor</h1>
    <p>Drag to orbit &bull; scroll to zoom &bull; right-drag to pan</p>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>

  <script>
    // ---------- Basic setup ----------
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x86d3ff);
    scene.fog = new THREE.Fog(0x86d3ff, 65, 170);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.outputEncoding = THREE.sRGBEncoding;
    document.body.appendChild(renderer.domElement);

    const camera = new THREE.PerspectiveCamera(
      45,
      window.innerWidth / window.innerHeight,
      0.1,
      500
    );
    camera.position.set(42, 30, 50);

    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.target.set(-5, 6, 0);
    controls.enableDamping = true;
    controls.dampingFactor = 0.06;
    controls.minDistance = 16;
    controls.maxDistance = 160;
    controls.maxPolarAngle = Math.PI * 0.495;
    controls.update();

    // ---------- Lighting ----------
    scene.add(new THREE.AmbientLight(0xffffff, 0.35));
    scene.add(new THREE.HemisphereLight(0xffffff, 0x365f7a, 0.6));

    const sun = new THREE.DirectionalLight(0xfff0d0, 0.85);
    sun.position.set(35, 55, 25);
    scene.add(sun);

    const fill = new THREE.DirectionalLight(0x9cc8ff, 0.35);
    fill.position.set(-30, 20, -25);
    scene.add(fill);

    // ---------- Helpers ----------
    let seed = 20240917;
    function rand() {
      seed = (seed * 1664525 + 1013904223) >>> 0;
      return seed / 4294967296;
    }

    const materials = {};
    function material(color) {
      if (!materials[color]) {
        materials[color] = new THREE.MeshLambertMaterial({ color });
      }
      return materials[color];
    }

    const unitBox = new THREE.BoxGeometry(1, 1, 1);

    function addBox(parent, x, y, z, w, h, d, color) {
      const mesh = new THREE.Mesh(unitBox, material(color));
      mesh.position.set(x, y, z);
      mesh.scale.set(w, h, d);
      parent.add(mesh);
      return mesh;
    }

    function addVoxel(parent, x, y, z, size, color) {
      return addBox(parent, x, y, z, size, size, size, color);
    }

    // ---------- Water ----------
    const waterMat = new THREE.MeshLambertMaterial({
      color: 0x1686bf,
      transparent: true,
      opacity: 0.96,
      side: THREE.DoubleSide
    });

    const water = new THREE.Mesh(new THREE.PlaneGeometry(120, 120), waterMat);
    water.rotation.x = -Math.PI / 2;
    water.position.y = 0;
    scene.add(water);

    // Voxel-ish waves
    for (let i = 0; i < 150; i++) {
      const x = -42 + rand() * 84;
      const z = -42 + rand() * 84;
      if (x < -16 && z > -25 && z < 25) continue;

      const w = 1 + rand() * 2.4;
      const d = 0.35 + rand() * 1.2;
      const color = rand() > 0.5 ? 0x2ca6d7 : 0x3bb8e5;
      addBox(scene, x, 0.08, z, w, 0.12, d, color);
    }

    // ---------- Shore / quay / dock ----------
    const harbor = new THREE.Group();
    scene.add(harbor);

    addBox(harbor, -30, 0.55, 0, 24, 1.5, 80, 0x6f8c55);
    addBox(harbor, -18.5, 0.85, 0, 3, 1.7, 48, 0x7b8b87);

    // Stone quay blocks
    for (let z = -22; z <= 22; z += 2) {
      const stone = rand() > 0.5 ? 0x8d9b97 : 0x6f7f7d;
      addBox(harbor, -18.5, 1.78, z, 2.8, 0.35, 1.9, stone);
    }

    // Wooden pier planks
    for (let z = -11; z <= 11; z += 1.2) {
      const wood = rand() > 0.5 ? 0x9a663e : 0x8a5b35;
      addBox(harbor, -14, 1.75, z, 8, 0.35, 1.05, wood);
    }

    // Pilings
    for (const x of [-17.5, -10.5]) {
      for (const z of [-10, -5, 0, 5, 10]) {
        addBox(harbor, x, 0.9, z, 0.55, 2.4, 0.55, 0x5a3527);
      }
    }

    // Bollards
    for (const z of [-7, 6]) {
      addBox(harbor, -10.5, 2.25, z, 0.6, 0.65, 0.6, 0x303a44);
    }

    // Gangplank from dock to ship
    const plank = addBox(scene, -7.25, 2.44, 0, 5.7, 0.25, 2.0, 0xc08a56);
    plank.rotation.z = Math.atan2(1.18, 5.5);

    // ---------- Harbor buildings ----------
    const warehouse = new THREE.Group();
    harbor.add(warehouse);

    addBox(warehouse, -29, 4.3, 10, 12, 6, 11, 0xd8c08a);
    addBox(warehouse, -29, 7.55, 10, 13, 0.7, 12, 0xa64d3f);
    addBox(warehouse, -29, 2.85, 15.6, 2.2, 3.2, 0.25, 0x493b32);

    for (const x of [-32.5, -29, -25.5]) {
      addBox(warehouse, x, 5.25, 15.6, 1.5, 1.2, 0.25, 0x2f6f91);
    }

    // Lighthouse
    const lighthouse = new THREE.Group();
    harbor.add(lighthouse);

    for (let level = 0; level < 11; level++) {
      const w = Math.max(3.0, 5.0 - level * 0.17);
      const color = level % 2 === 0 ? 0xf3f0df : 0xc94d3d;
      addBox(lighthouse, -34, 1.3 + level * 1.5 + 0.75, -16, w, 1.5, w, color);
    }

    addBox(lighthouse, -34, 19.2, -16, 2.8, 2.2, 2.8, 0xffd166);
    addBox(lighthouse, -34, 20.7, -16, 3.4, 0.7, 3.4, 0xc94d3d);
    addBox(lighthouse, -34, 21.35, -16, 1.0, 0.4, 1.0, 0x2f2f2f);

    // Crane
    const crane = new THREE.Group();
    harbor.add(crane);

    addBox(crane, -18, 1.0, -12, 4.0, 1.8, 4.0, 0x6d5a3d);
    addBox(crane, -18, 6.4, -12, 2.5, 10, 2.5, 0xe0a22b);
    addBox(crane, -14, 10.5, -12, 10, 0.8, 1.0, 0xe0a22b);
    addBox(crane, -9.5, 8.8, -12, 0.22, 2.4, 0.22, 0x333333);
    addBox(crane, -9.5, 7.4, -12, 0.8, 0.5, 0.8, 0x333333);

    // Crates and barrels on dock
    addVoxel(harbor, -16, 2.55, -6, 1.2, 0xa66f42);
    addVoxel(harbor, -16, 3.75, -6, 1.2, 0xbd8047);
    addVoxel(harbor, -14.8, 2.55, -6, 1.2, 0x9a663e);
    addBox(harbor, -13, 2.55, 8, 0.9, 1.2, 0.9, 0x6b8d52);
    addBox(harbor, -13, 2.55, 9.2, 0.9, 1.2, 0.9, 0x6b8d52);

    // ---------- Sailing ship ----------
    const ship = new THREE.Group();
    scene.add(ship);

    // Hull half-width per z row
    function hullHalfWidth(iz) {
      if (iz === -15) return 1;
      if (iz === -14) return 2;
      if (iz <= -12) return 3;
      if (iz <= -10) return 4;
      if (iz <= 9) return 5;
      if (iz === 10) return 4;
      if (iz === 11) return 3;
      if (iz === 12) return 2;
      if (iz === 13) return 1;
      return 0;
    }

    const cell = 0.9;
    const voxel = 0.86;

    // Hull, three layers
    for (let iz = -15; iz <= 14; iz++) {
      const hw = hullHalfWidth(iz);

      for (let layer = 0; layer < 3; layer++) {
        const layerHW = Math.max(0, hw - (2 - layer));
        const color =
          layer === 0 ? 0x3c241c :
          layer === 1 ? 0x7b4a2c :
          0xa46a3d;

        for (let ix = -layerHW; ix <= layerHW; ix++) {
          addVoxel(ship, ix * cell, 0.6 + layer * cell, iz * cell, voxel, color);
        }
      }
    }

    // Deck surface rows
    for (let iz = -15; iz <= 14; iz++) {
      const hw = hullHalfWidth(iz);
      const width = Math.max(1, 2 * hw * cell + 0.4);
      const deckColor = (iz % 2 === 0) ? 0xc58a55 : 0xb97b49;
      addBox(ship, 0, 3.02, iz * cell, width, 0.16, cell * 0.86, deckColor);
    }

    // Rail posts
    for (let iz = -12; iz <= 11; iz += 2) {
      const hw = hullHalfWidth(iz);
      const x = hw * cell + 0.32;
      addBox(ship, x, 3.35, iz * cell, 0.22, 0.62, 0.22, 0x6b422a);
      addBox(ship, -x, 3.35, iz * cell, 0.22, 0.62, 0.22, 0x6b422a);
    }

    // Stern cabin
    addBox(ship, 0, 4.1, -11, 5.2, 2.0, 4.0, 0xe6d8b3);
    addBox(ship, 0, 5.35, -11, 6.0, 0.5, 4.8, 0xa34a38);

    // Cabin windows
    for (const x of [-1.6, 0, 1.6]) {
      addBox(ship, x, 4.35, -8.9, 0.85, 0.65, 0.15, 0x2c6b8f);
    }
    for (const z of [-12.5, -10]) {
      addBox(ship, 2.63, 4.35, z, 0.15, 0.65, 0.8, 0x2c6b8f);
      addBox(ship, -2.63, 4.35, z, 0.15, 0.65, 0.8, 0x2c6b8f);
    }

    // Bowsprit
    addBox(ship, 0, 3.25, 16.0, 0.45, 0.45, 7.0, 0x6a4028);

    // Masts
    function addMast(z, height) {
      for (let y = 3.1; y <= 3.1 + height; y += 0.7) {
        addVoxel(ship, 0, y, z, 0.62, 0x6b422a);
      }
    }

    addMast(-2, 16.5);
    addMast(7, 12.5);

    // Yards
    addBox(ship, 0, 10.0, -2, 10.0, 0.35, 0.35, 0x5c3925);
    addBox(ship, 0, 14.8, -2, 8.0, 0.35, 0.35, 0x5c3925);
    addBox(ship, 0, 8.2, 7, 7.0, 0.32, 0.32, 0x5c3925);
    addBox(ship, 0, 12.3, 7, 5.0, 0.32, 0.32, 0x5c3925);

    // Square sails, built from voxel cubes
    function addSail(parent, z, cols, rows, centerY, sailCell, bulge) {
      const mid = (cols - 1) / 2;
      for (let i = 0; i < cols; i++) {
        for (let j = 0; j < rows; j++) {
          const x = (i - mid) * sailCell;
          const y = centerY + (j - (rows - 1) / 2) * sailCell;
          const curve = Math.cos(((i - mid) / Math.max(1, mid)) * Math.PI / 2) * bulge;
          const shade = (i + j) % 3 === 0 ? 0xf4f0df : 0xe6e0cd;
          addBox(parent, x, y, z + curve, sailCell * 0.94, sailCell * 0.94, 0.22, shade);
        }
      }
    }

    addSail(ship, -2.3, 11, 4, 8.6, 0.85, 0.42);
    addSail(ship, -2.3, 9, 3, 13.4, 0.85, 0.35);
    addSail(ship, 6.7, 9, 3, 6.9, 0.8, 0.32);
    addSail(ship, 6.7, 7, 3, 11.1, 0.8, 0.26);

    // Triangular jib sail
    for (let row = 0; row < 8; row++) {
      const z = 8.2 + row * 1.15;
      const y = 11.2 - row * 1.0;
      const cols = Math.max(1, 6 - row);
      for (let i = 0; i < cols; i++) {
        const x = (i - (cols - 1) / 2) * 0.72;
        const shade = (row + i) % 2 === 0 ? 0xf1ebd8 : 0xe4dec9;
        addBox(ship, x, y, z, 0.68, 0.68, 0.2, shade);
      }
    }

    // Flags
    addBox(ship, 1.2, 20.2, -2, 1.4, 0.42, 0.12, 0xd64232);
    addBox(ship, -1.1, 16.4, 7, 1.0, 0.35, 0.12, 0x3b82f6);

    // ---------- Small harbor boat ----------
    const boat = new THREE.Group();
    scene.add(boat);

    addBox(boat, 13, 0.5, -11, 3.0, 0.8, 6.0, 0x7b4a2c);
    addBox(boat, 13, 0.95, -11, 2.3, 0.3, 5.0, 0xd8c08a);
    addBox(boat, 13, 2.1, -11, 0.28, 2.3, 0.28, 0x6b422a);
    addBox(boat, 13.7, 2.8, -11, 0.8, 0.5, 0.1, 0xf3f0df);

    // ---------- Buoys ----------
    addVoxel(scene, 10, 0.42, -18, 0.85, 0xd94836);
    addVoxel(scene, 17, 0.42, 14, 0.85, 0x2f9e57);

    // ---------- Tiny dock workers ----------
    function addPerson(parent, x, z, yBase, shirtColor) {
      addBox(parent, x - 0.16, yBase + 0.45, z, 0.22, 0.8, 0.25, 0x2b3548);
      addBox(parent, x + 0.16, yBase + 0.45, z, 0.22, 0.8, 0.25, 0x2b3548);
      addBox(parent, x, yBase + 1.08, z, 0.52, 0.78, 0.35, shirtColor);
      addBox(parent, x, yBase + 1.65, z, 0.42, 0.42, 0.42, 0xe2b98b);
      addBox(parent, x, yBase + 1.91, z, 0.62, 0.16, 0.62, 0xf0d66b);
    }

    addPerson(harbor, -13, 4, 1.9, 0xf0a23a);
    addPerson(harbor, -15, -2, 1.9, 0x2b7a9e);
    addPerson(ship, -2, -7, 3.05, 0xdd5d4d);

    // ---------- Voxel clouds ----------
    const clouds = new THREE.Group();
    scene.add(clouds);

    function addCloud(x, y, z, scale) {
      const white = 0xf7fbff;
      const soft = 0xe8f1fa;
      addBox(clouds, x, y, z, 6 * scale, 1.2 * scale, 2.2 * scale, white);
      addBox(clouds, x - 2 * scale, y + 0.8 * scale, z, 3.5 * scale, 1.0 * scale, 2.0 * scale, soft);
      addBox(clouds, x + 2.4 * scale, y + 0.7 * scale, z, 3.0 * scale, 1.0 * scale, 2.0 * scale, soft);
    }

    addCloud(-26, 31, -30, 1.2);
    addCloud(8, 35, -36, 1.0);
    addCloud(27, 30, 26, 1.3);

    // ---------- Render loop ----------
    window.addEventListener('resize', function () {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    });

    function animate() {
      requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    }

    animate();
  </script>
</body>
</html>
```