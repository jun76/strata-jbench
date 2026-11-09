Save the following as a single `.html` file and open it in Chrome. It uses Three.js from a CDN, so the page needs internet access.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Sailing Ship Calling at a Voxel Harbor</title>

  <style>
    html, body {
      margin: 0;
      height: 100%;
      overflow: hidden;
      background: #9adcf2;
    }
    canvas {
      display: block;
    }
    #ui {
      position: fixed;
      left: 12px;
      bottom: 12px;
      color: rgba(255, 255, 255, 0.9);
      font: 13px/1.4 system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
      background: rgba(0, 0, 0, 0.35);
      padding: 6px 10px;
      border-radius: 8px;
      pointer-events: none;
      user-select: none;
    }
  </style>

  <script type="importmap">
    {
      "imports": {
        "three": "https://cdn.jsdelivr.net/npm/three@0.169.0/build/three.module.js",
        "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.169.0/examples/jsm/"
      }
    }
  </script>
</head>
<body>
  <div id="ui">Drag: rotate • Wheel: zoom • Right-drag: pan</div>

  <script type="module">
    import * as THREE from "three";
    import { OrbitControls } from "three/addons/controls/OrbitControls.js";

    const C = {
      water:       0x39a9d8,
      waterLight:  0x6fcde6,
      waterMid:    0x2a86b7,
      waterDeep:   0x1c6b9c,

      sand:        0xd9c59c,
      sandDark:    0xb7a079,
      grass:       0x6f9c5a,
      grass2:      0x8ab865,
      dirt:        0x8a6a45,
      rock:        0x9a9a96,
      rockDark:    0x6d6d69,

      stone:       0xa8a49c,
      stonePath:   0x8e8a83,

      deck:        0xa97a4e,
      wood:        0x8a5c33,
      woodDark:    0x4c3321,
      crate:       0xa67b46,
      barrel:      0x6e4a2f,

      sail:        0xf2e8d7,
      sailAlt:     0xd8c8ad,
      mast:        0x6a452b,
      rope:        0x3b2a1c,
      flag:        0xd84c4c,

      hull:        0x8b5e35,
      hullDark:    0x5a3923,
      cabin:       0xb58350,
      cabinRoof:   0x7a4f2e,
      rail:        0x6b4a2b,

      wallWhite:   0xf3efe5,
      wallBlue:    0xb5c9dd,
      wallTan:     0xe6d2ad,
      roofRed:     0xc0514f,
      roofBrown:   0x8b5a3c,
      roofGray:    0x7d8a97,

      window:      0x3f74a8,
      door:        0x654027,
      doorLarge:   0x52341f,

      lighthouseWhite: 0xf5f5f5,
      lighthouseRed:   0xd84c4c,
      cloud:           0xffffff,

      trunk: 0x5c3e29,
      leaves: 0x5c8a4a
    };

    function rand2(a, b) {
      const n = Math.sin(a * 127.1 + b * 311.7) * 43758.5453123;
      return n - Math.floor(n);
    }

    const voxels = new Map();
    const cloudEntries = new Map();

    function key(x, y, z) {
      return (x + 100) * 100000 + (y + 100) * 1000 + (z + 100);
    }

    function addVoxel(x, y, z, color) {
      voxels.set(key(x, y, z), { x, y, z, color });
    }

    function addCloudVoxel(x, y, z, color) {
      cloudEntries.set(key(x, y, z), { x, y, z, color });
    }

    function addBox(x1, y1, z1, x2, y2, z2, color) {
      if (x1 > x2) { const t = x1; x1 = x2; x2 = t; }
      if (y1 > y2) { const t = y1; y1 = y2; y2 = t; }
      if (z1 > z2) { const t = z1; z1 = z2; z2 = t; }

      for (let x = x1; x <= x2; x++) {
        for (let y = y1; y <= y2; y++) {
          for (let z = z1; z <= z2; z++) {
            addVoxel(x, y, z, color);
          }
        }
      }
    }

    function addBoxLocal(cx, cz, x1, y1, z1, x2, y2, z2, color) {
      addBox(cx + x1, y1, cz + z1, cx + x2, y2, cz + z2, color);
    }

    function addCylinder(cx, cz, y, r, color, skipCenter = false) {
      for (let dx = -r; dx <= r; dx++) {
        for (let dz = -r; dz <= r; dz++) {
          if (dx * dx + dz * dz > r * r + 0.5) continue;
          if (skipCenter && dx === 0 && dz === 0) continue;
          addVoxel(cx + dx, y, cz + dz, color);
        }
      }
    }

    function makeShip(cx, cz) {
      // Lower hull
      addBoxLocal(cx, cz, -5, 0, -3, 4, 1, 3, C.hull);
      addBoxLocal(cx, cz, -5, 0, -3, 4, 0, 3, C.hullDark);

      // Deck / upper hull
      addBoxLocal(cx, cz, -5, 2, -3, 4, 2, 3, C.deck);

      // Bow
      addBoxLocal(cx, cz, 5, 0, -2, 6, 2, 2, C.hull);
      addBoxLocal(cx, cz, 5, 0, -2, 6, 0, 2, C.hullDark);
      addBoxLocal(cx, cz, 7, 1, -1, 8, 2, 1, C.hull);

      // Stern
      addBoxLocal(cx, cz, -6, 0, -2, -6, 2, 2, C.hull);
      addBoxLocal(cx, cz, -6, 0, -2, -6, 0, 2, C.hullDark);
      addBoxLocal(cx, cz, -7, 1, -1, -7, 2, 1, C.hull);

      // Aft cabin and small forward cabin
      addBoxLocal(cx, cz, -5, 3, -2, -2, 4, 2, C.cabin);
      addBoxLocal(cx, cz, -6, 5, -1, -3, 5, 1, C.cabinRoof);
      addBoxLocal(cx, cz, 2, 3, -2, 4, 3, 2, C.cabin);

      // Railing
      addBoxLocal(cx, cz, -5, 3, -3, -5, 3, 3, C.rail);
      addBoxLocal(cx, cz, 4, 3, -3, 4, 3, 3, C.rail);
      addBoxLocal(cx, cz, -4, 3, -3, 4, 3, -3, C.rail);
      addBoxLocal(cx, cz, -4, 3, 3, 4, 3, 3, C.rail);

      // Bowsprit
      addBoxLocal(cx, cz, 9, 3, 0, 9, 3, 0, C.mast);
      addBoxLocal(cx, cz, 10, 4, 0, 11, 4, 0, C.mast);

      // Masts and square sails
      const masts = [
        { x: -3, height: 10, sailY: 5, sailEnd: 7, half: 2 },
        { x:  0, height: 12, sailY: 5, sailEnd: 9, half: 3 },
        { x:  3, height:  9, sailY: 5, sailEnd: 7, half: 2 }
      ];

      for (const m of masts) {
        addBoxLocal(cx, cz, m.x, 3, 0, m.x, m.height, 0, C.mast);

        // Main sail
        addBoxLocal(cx, cz, m.x, m.sailY, -m.half, m.x, m.sailEnd, m.half, C.sail);
        addBoxLocal(cx, cz, m.x + 1, m.sailY + 1, -m.half + 1, m.x + 1, m.sailEnd - 1, m.half - 1, C.sailAlt);

        // Yards
        addBoxLocal(cx, cz, m.x, m.sailY - 1, -m.half, m.x, m.sailY - 1, m.half, C.mast);
        addBoxLocal(cx, cz, m.x, m.sailEnd + 1, -m.half, m.x, m.sailEnd + 1, m.half, C.mast);
        addBoxLocal(cx, cz, m.x, m.height - 1, -1, m.x, m.height - 1, 1, C.mast);
      }

      // Flags
      addBoxLocal(cx, cz, 0, 13, -1, 0, 13, -1, C.flag);
      addBoxLocal(cx, cz, -3, 11, -1, -3, 11, -1, C.flag);
      addBoxLocal(cx, cz, 3, 10, -1, 3, 10, -1, C.flag);
    }

    function makeHouse(cx, cz, w, d, h, wall, roof) {
      const x1 = cx - Math.floor(w / 2);
      const x2 = x1 + w - 1;
      const z1 = cz - Math.floor(d / 2);
      const z2 = z1 + d - 1;

      addBox(x1, 1, z1, x2, h, z2, wall);

      if (h >= 2) {
        addVoxel(x1, 2, cz, C.window);
        addVoxel(x2, 2, cz, C.window);
        addVoxel(cx, 2, z1, C.window);
        addVoxel(cx, 2, z2, C.window);
      }

      if (h >= 3) {
        addVoxel(cx - 1, 3, z1, C.window);
        addVoxel(cx + 1, 3, z1, C.window);
        addVoxel(cx - 1, 3, z2, C.window);
        addVoxel(cx + 1, 3, z2, C.window);
      }

      // Door
      addBox(cx - 1, 1, z1, cx, 1, z1, C.door);

      // Roof
      addBox(x1 - 1, h + 1, z1 - 1, x2 + 1, h + 1, z2 + 1, roof);

      for (let i = 1; i <= Math.floor(w / 2); i++) {
        const ax = x1 + i;
        const bx = x2 - i;
        const az = z1 + i;
        const bz = z2 - i;
        if (ax > bx || az > bz) break;
        addBox(ax, h + 1 + i, az, bx, h + 1 + i, bz, roof);
      }
    }

    function makeWarehouse(cx, cz, w, d, h, wall, roof) {
      const x1 = cx - Math.floor(w / 2);
      const x2 = x1 + w - 1;
      const z1 = cz - Math.floor(d / 2);
      const z2 = z1 + d - 1;

      addBox(x1, 1, z1, x2, h, z2, wall);
      addBox(x1 - 1, h + 1, z1 - 1, x2 + 1, h + 1, z2 + 1, roof);

      addBox(cx - 2, 1, z1, cx + 2, 2, z1, C.doorLarge);
      if (h >= 3) addVoxel(cx, 3, z1, C.window);
    }

    function makeLighthouse(cx, cz) {
      addCylinder(cx, cz, -1, 3, C.rock);
      addCylinder(cx, cz, 0, 3, C.stone);

      for (let y = 1; y <= 9; y++) {
        const color = (Math.floor(y / 2) % 2 === 0) ? C.lighthouseWhite : C.lighthouseRed;
        addCylinder(cx, cz, y, 2, color);
      }

      addCylinder(cx, cz, 10, 2, C.lighthouseWhite);
      addCylinder(cx, cz, 11, 1, C.lighthouseWhite, true);
      addCylinder(cx, cz, 12, 1, C.lighthouseRed);
      addVoxel(cx, 13, cz, C.lighthouseRed);

      addVoxel(cx, 6, cz - 2, C.window);
      addVoxel(cx, 8, cz + 2, C.window);
    }

    function addSmallTree(cx, cz) {
      addBox(cx, 1, cz, cx, 2, cz, C.trunk);
      addVoxel(cx - 1, 3, cz, C.leaves);
      addVoxel(cx + 1, 3, cz, C.leaves);
      addVoxel(cx, 3, cz - 1, C.leaves);
      addVoxel(cx, 3, cz + 1, C.leaves);
      addVoxel(cx, 3, cz, C.leaves);
      addVoxel(cx, 4, cz, C.leaves);
    }

    function addCloudCluster(cx, cy, cz) {
      for (let x = cx - 6; x <= cx + 6; x++) {
        for (let z = cz - 4; z <= cz + 4; z++) {
          if (rand2(x, z) > 0.38) addCloudVoxel(x, cy, z, C.cloud);
          if (rand2(x * 3 + 17, z * 3 + 11) > 0.68) addCloudVoxel(x, cy + 1, z, C.cloud);
          if (rand2(x * 5 + 7, z * 5 + 29) > 0.86) addCloudVoxel(x, cy + 2, z, C.cloud);
        }
      }
    }

    // ----------------------------------------------------------------------
    // Build the voxel world
    // ----------------------------------------------------------------------

    const LH_X = 20;
    const LH_Z = -18;
    const waterEntries = [];

    // Sea surface entries and sea floor
    for (let x = -30; x <= 16; x++) {
      for (let z = -22; z <= 22; z++) {
        const r = rand2(x, z);
        let color = C.water;
        if (r < 0.15) color = C.waterLight;
        else if (r > 0.87) color = C.waterMid;

        waterEntries.push({
          x, y: -1, z,
          phase: rand2(x * 3 + 5, z * 3 + 9) * Math.PI * 2,
          color
        });

        addVoxel(x, -2, z, C.waterMid);
        addVoxel(x, -3, z, C.waterDeep);
      }
    }

    // Beach strip
    for (let z = -22; z <= 22; z++) {
      addVoxel(17, 0, z, C.sand);
      addVoxel(17, -1, z, C.sandDark);
      addVoxel(17, -2, z, C.sandDark);
    }

    // Harbor land
    for (let x = 18; x <= 34; x++) {
      for (let z = -22; z <= 22; z++) {
        let top;
        if (x <= 21 && Math.abs(z) <= 8) {
          top = C.stone;
        } else {
          const r = rand2(x, z);
          top = r < 0.62 ? C.grass : r < 0.87 ? C.grass2 : C.rock;
        }

        addVoxel(x, 0, z, top);
        addVoxel(x, -1, z, C.dirt);
        addVoxel(x, -2, z, C.rockDark);
        addVoxel(x, -3, z, C.rockDark);
      }
    }

    // Dock
    addBox(8, 0, -6, 18, 0, 6, C.deck);

    addBox(8, 0, -6, 18, 0, -6, C.woodDark);
    addBox(8, 0, 6, 18, 0, 6, C.woodDark);
    addBox(8, 0, -6, 8, 0, 6, C.woodDark);
    addBox(18, 0, -6, 18, 0, 6, C.woodDark);

    // Harbor path
    addBox(18, 0, -6, 21, 0, 6, C.stonePath);

    // Dock pilings
    for (let x = 8; x <= 17; x += 3) {
      for (const z of [-6, 0, 6]) {
        addBox(x, -3, z, x, -1, z, C.woodDark);
      }
    }

    // Dock cargo
    addBox(11, 1, -4, 12, 2, -3, C.crate);
    addBox(14, 1, 3, 15, 2, 4, C.crate);
    addBox(16, 1, -1, 16, 2, 0, C.barrel);
    addBox(16, 1, 1, 16, 2, 2, C.barrel);

    // Ship
    makeShip(-1, 0);

    // Mooring line and bollards
    addBox(7, 3, 2, 9, 3, 2, C.rope);
    addBox(10, 1, 2, 10, 2, 2, C.woodDark);
    addBox(10, 1, -2, 10, 2, -2, C.woodDark);

    // Harbor buildings
    makeWarehouse(21, -10, 5, 5, 3, C.stone, C.roofBrown);
    makeHouse(25, -2, 5, 5, 4, C.wallWhite, C.roofRed);
    makeHouse(29, 8, 5, 5, 4, C.wallBlue, C.roofBrown);
    makeHouse(28, -14, 5, 5, 4, C.wallTan, C.roofRed);
    makeWarehouse(27, 18, 5, 5, 3, C.stone, C.roofGray);

    // Small trees along the far shore
    addSmallTree(33, -18);
    addSmallTree(33, -5);
    addSmallTree(33, 3);
    addSmallTree(33, 14);

    // Lighthouse
    makeLighthouse(LH_X, LH_Z);

    // Clouds
    addCloudCluster(0, 20, -10);
    addCloudCluster(18, 21, 12);
    addCloudCluster(-18, 19, 5);

    // ----------------------------------------------------------------------
    // Scene, renderer, camera, controls
    // ----------------------------------------------------------------------

    const scene = new THREE.Scene();
    const skyColor = new THREE.Color(0x9adcf2);
    scene.background = skyColor;
    scene.fog = new THREE.Fog(skyColor, 55, 145);

    const camera = new THREE.PerspectiveCamera(48, window.innerWidth / window.innerHeight, 0.1, 500);
    camera.position.set(18, 16, 26);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.05;
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    document.body.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.target.set(0, 4, 0);
    controls.enableDamping = true;
    controls.dampingFactor = 0.06;
    controls.minDistance = 8;
    controls.maxDistance = 95;
    controls.maxPolarAngle = Math.PI * 0.49;
    controls.update();

    // Lights
    const hemi = new THREE.HemisphereLight(0xbfe7ff, 0x453224, 0.58);
    scene.add(hemi);

    const sun = new THREE.DirectionalLight(0xfff3d6, 2.15);
    sun.position.set(-22, 32, 18);
    sun.castShadow = true;
    sun.shadow.mapSize.set(2048, 2048);
    sun.shadow.camera.left = -55;
    sun.shadow.camera.right = 55;
    sun.shadow.camera.top = 55;
    sun.shadow.camera.bottom = -55;
    sun.shadow.camera.near = 1;
    sun.shadow.camera.far = 160;
    sun.shadow.bias = -0.00055;
    sun.shadow.normalBias = 0.05;
    scene.add(sun);
    scene.add(sun.target);

    // ----------------------------------------------------------------------
    // Static voxel instanced mesh
    // ----------------------------------------------------------------------

    const entries = Array.from(voxels.values());

    const staticGeo = new THREE.BoxGeometry(0.98, 0.98, 0.98);
    const staticMat = new THREE.MeshStandardMaterial({
      roughness: 0.82,
      metalness: 0.04,
      flatShading: true
    });

    const staticMesh = new THREE.InstancedMesh(staticGeo, staticMat, entries.length);
    staticMesh.castShadow = true;
    staticMesh.receiveShadow = true;
    staticMesh.frustumCulled = false;

    const dummy = new THREE.Object3D();
    const tempColor = new THREE.Color();

    for (let i = 0; i < entries.length; i++) {
      const e = entries[i];
      dummy.position.set(e.x, e.y, e.z);
      dummy.rotation.set(0, 0, 0);
      dummy.scale.set(1, 1, 1);
      dummy.updateMatrix();

      staticMesh.setMatrixAt(i, dummy.matrix);
      tempColor.set(e.color);
      staticMesh.setColorAt(i, tempColor);
    }

    staticMesh.instanceMatrix.needsUpdate = true;
    if (staticMesh.instanceColor) staticMesh.instanceColor.needsUpdate = true;
    scene.add(staticMesh);

    // ----------------------------------------------------------------------
    // Animated water surface
    // ----------------------------------------------------------------------

    const waterGeo = new THREE.BoxGeometry(0.95, 0.95, 0.95);
    const waterMat = new THREE.MeshStandardMaterial({
      roughness: 0.55,
      metalness: 0.15,
      flatShading: true
    });

    const waterMesh = new THREE.InstancedMesh(waterGeo, waterMat, waterEntries.length);
    waterMesh.castShadow = false;
    waterMesh.receiveShadow = true;
    waterMesh.frustumCulled = false;

    for (let i = 0; i < waterEntries.length; i++) {
      const w = waterEntries[i];
      dummy.position.set(w.x, w.y, w.z);
      dummy.rotation.set(0, 0, 0);
      dummy.scale.set(1, 1, 1);
      dummy.updateMatrix();

      waterMesh.setMatrixAt(i, dummy.matrix);
      tempColor.set(w.color);
      waterMesh.setColorAt(i, tempColor);
    }

    waterMesh.instanceMatrix.needsUpdate = true;
    if (waterMesh.instanceColor) waterMesh.instanceColor.needsUpdate = true;
    scene.add(waterMesh);

    // ----------------------------------------------------------------------
    // Clouds
    // ----------------------------------------------------------------------

    const cloudList = Array.from(cloudEntries.values());
    const cloudGroup = new THREE.Group();
    scene.add(cloudGroup);

    if (cloudList.length > 0) {
      const cloudGeo = new THREE.BoxGeometry(1, 1, 1);
      const cloudMat = new THREE.MeshBasicMaterial({ color: C.cloud, fog: true });
      const cloudMesh = new THREE.InstancedMesh(cloudGeo, cloudMat, cloudList.length);
      cloudMesh.frustumCulled = false;
      cloudMesh.castShadow = false;
      cloudMesh.receiveShadow = false;

      for (let i = 0; i < cloudList.length; i++) {
        const e = cloudList[i];
        dummy.position.set(e.x, e.y, e.z);
        dummy.rotation.set(0, 0, 0);
        dummy.scale.set(1, 1, 1);
        dummy.updateMatrix();
        cloudMesh.setMatrixAt(i, dummy.matrix);
      }

      cloudMesh.instanceMatrix.needsUpdate = true;
      cloudGroup.add(cloudMesh);
    }

    // ----------------------------------------------------------------------
    // Lighthouse lamp and light
    // ----------------------------------------------------------------------

    const lampMat = new THREE.MeshBasicMaterial({
      color: 0xffe37a,
      transparent: true,
      opacity: 0.85
    });

    const lamp = new THREE.Mesh(new THREE.BoxGeometry(1.15, 1.15, 1.15), lampMat);
    lamp.position.set(LH_X, 11, LH_Z);
    scene.add(lamp);

    const lampLight = new THREE.PointLight(0xffe07a, 2.2, 55, 2);
    lampLight.position.copy(lamp.position);
    scene.add(lampLight);

    // ----------------------------------------------------------------------
    // Animation
    // ----------------------------------------------------------------------

    const clock = new THREE.Clock();

    function animate() {
      requestAnimationFrame(animate);

      const t = clock.getElapsedTime();

      // Animate water
      for (let i = 0; i < waterEntries.length; i++) {
        const w = waterEntries[i];
        const wave =
          Math.sin(t * 1.25 + w.phase) * 0.07 +
          Math.cos((w.x * 0.18 + w.z * 0.13) + t * 0.72) * 0.03;

        dummy.position.set(w.x, w.y + wave, w.z);
        dummy.rotation.set(0, 0, 0);
        dummy.scale.set(1, 1, 1);
        dummy.updateMatrix();
        waterMesh.setMatrixAt(i, dummy.matrix);
      }
      waterMesh.instanceMatrix.needsUpdate = true;

      // Beacon flicker
      let pulse = 0.72 + 0.28 * Math.sin(t * 2.7) + 0.10 * Math.sin(t * 9.3);
      pulse = Math.max(0, Math.min(1, pulse));

      lampLight.intensity = 1.6 + pulse * 2.4;
      lampMat.opacity = 0.62 + pulse * 0.32;
      lamp.scale.setScalar(0.88 + pulse * 0.18);

      // Drifting clouds
      cloudGroup.position.x = Math.sin(t * 0.055) * 10;
      cloudGroup.position.z = Math.sin(t * 0.042) * 7;

      controls.update();
      renderer.render(scene, camera);
    }

    window.addEventListener("resize", () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    });

    animate();
  </script>
</body>
</html>
```