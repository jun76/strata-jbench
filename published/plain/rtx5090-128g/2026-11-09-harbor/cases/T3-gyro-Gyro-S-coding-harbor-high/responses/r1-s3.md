Here is a complete single HTML file. Paste it into a file like `voxel-harbor.html` and open it in Chrome. It uses Three.js from a CDN and renders a voxel harbor scene immediately.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Voxel Art Scene — Sailing Ship Calling at a Harbor</title>
  <style>
    html, body {
      height: 100%;
      margin: 0;
      overflow: hidden;
      background: #9cc5d8;
    }
    canvas {
      display: block;
    }
    #hint {
      position: absolute;
      top: 12px;
      left: 12px;
      padding: 8px 10px;
      border-radius: 6px;
      background: rgba(255, 255, 255, 0.68);
      color: #243847;
      font: 13px monospace;
      pointer-events: none;
    }
  </style>
  <script type="importmap">
    {
      "imports": {
        "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
        "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
      }
    }
  </script>
</head>
<body>
  <div id="hint">drag orbit • wheel zoom • right drag pan</div>
  <script type="module">
    import * as THREE from 'three';
    import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

    const scene = new THREE.Scene();
    scene.background = new THREE.Color('#9cc5d8');
    scene.fog = new THREE.Fog('#b6d3e0', 30, 95);

    const camera = new THREE.PerspectiveCamera(45, innerWidth / innerHeight, 0.1, 200);
    camera.position.set(18, 12, 22);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
    renderer.setSize(innerWidth, innerHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    document.body.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.07;
    controls.target.set(3, 1.4, 0);
    controls.minDistance = 8;
    controls.maxDistance = 70;
    controls.maxPolarAngle = Math.PI * 0.48;
    controls.update();

    const hemi = new THREE.HemisphereLight('#cfe8f0', '#3f5a4b', 1.0);
    scene.add(hemi);

    const sun = new THREE.DirectionalLight('#fff2d4', 1.25);
    sun.position.set(20, 24, 14);
    sun.castShadow = true;
    sun.shadow.mapSize.set(1024, 1024);
    sun.shadow.camera.left = -24;
    sun.shadow.camera.right = 26;
    sun.shadow.camera.top = 24;
    sun.shadow.camera.bottom = -22;
    sun.shadow.camera.near = 1;
    sun.shadow.camera.far = 90;
    sun.shadow.bias = -0.0005;
    sun.shadow.normalBias = 0.04;
    sun.shadow.camera.updateProjectionMatrix();
    scene.add(sun);

    const ambient = new THREE.AmbientLight('#6f92a5', 0.25);
    scene.add(ambient);

    const geometry = new THREE.BoxGeometry(1, 1, 1);

    function pushVoxel(list, x, y, z, sx, sy, sz, color, rx = 0, ry = 0, rz = 0) {
      list.push({ x, y, z, sx, sy, sz, color, rx, ry, rz });
    }

    function createInstancedVoxels(list, material, opts = {}) {
      if (!list.length) return null;

      const mesh = new THREE.InstancedMesh(geometry, material, list.length);
      mesh.frustumCulled = false;
      mesh.castShadow = opts.castShadow !== false;
      mesh.receiveShadow = opts.receiveShadow !== false;

      const dummy = new THREE.Object3D();
      const color = new THREE.Color();

      for (let i = 0; i < list.length; i++) {
        const v = list[i];
        dummy.position.set(v.x, v.y, v.z);
        dummy.scale.set(v.sx, v.sy, v.sz);
        dummy.rotation.set(v.rx || 0, v.ry || 0, v.rz || 0);
        dummy.updateMatrix();

        mesh.setMatrixAt(i, dummy.matrix);
        color.set(v.color);
        mesh.setColorAt(i, color);
      }

      mesh.instanceMatrix.needsUpdate = true;
      if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;

      return mesh;
    }

    const mainMat = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      roughness: 0.72,
      metalness: 0,
      flatShading: true
    });

    const waterMat = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      roughness: 0.45,
      metalness: 0.05,
      flatShading: true
    });

    // ---------- Harbor ----------
    const harbor = [];
    function hb(x, y, z, sx, sy, sz, color) {
      pushVoxel(harbor, x, y, z, sx, sy, sz, color);
    }

    // Quay platform
    hb(9.5, 0.25, 0, 17, 0.5, 24, '#9a8f7a');

    // Stone dock edge wall
    for (let z = -12; z <= 12; z += 1) {
      hb(1.0, 0.14, z, 1.0, 0.75, 1.0, '#716453');
    }

    // Wooden pier boards along the edge
    hb(2.2, 0.62, 0, 2.2, 0.25, 24, '#c99b66');

    // Foam at the waterline
    for (let z = -12; z <= 12; z += 1) {
      hb(0.25, 0.03, z, 0.6, 0.12, 1.0, '#d8efe9');
    }

    // Bollards
    for (let z of [-8, -3, 0, 3, 8]) {
      hb(2.4, 0.95, z, 0.5, 0.6, 0.5, '#573f2b');
    }

    function warehouse(cx, cz, w, h, d, wall, roof, roofDark) {
      // Walls
      hb(cx, 0.5 + h / 2, cz, w, h, d, wall);

      // Roof
      hb(cx, 0.5 + h + 0.35, cz, w + 0.25, 0.7, d + 0.25, roof);
      hb(cx, 0.5 + h + 0.85, cz, 0.65, 0.35, d + 0.35, roofDark);

      // Door facing the dock
      const frontX = cx - w / 2 - 0.1;
      hb(frontX, 0.5 + 0.8, cz, 0.25, 1.6, 1.1, '#4c3422');

      // Windows
      hb(frontX, 0.5 + h * 0.65, cz - 1, 0.12, 0.6, 0.6, '#5d6870');
      hb(frontX, 0.5 + h * 0.65, cz + 1, 0.12, 0.6, 0.6, '#5d6870');

      // Chimney
      hb(cx + w * 0.25, 0.5 + h + 1.1, cz, 0.35, 0.8, 0.35, '#6a5042');
    }

    warehouse(6.5, -5, 6, 2.3, 7, '#c8a784', '#793f2f', '#4f2d22');
    warehouse(12, 2, 7, 3.0, 6, '#a87c54', '#5a372b', '#3e281d');
    warehouse(6, 8, 4.5, 2.2, 4.5, '#d6b58c', '#8b503c', '#5a382c');

    // Cargo crates
    function cargo(x, z, sx, h, sz, color) {
      hb(x, 0.5 + h / 2, z, sx, h, sz, color);
    }

    cargo(3.6, 2.5, 1.2, 1.0, 1.2, '#a87a4c');
    hb(3.6, 1.9, 2.5, 0.8, 0.8, 0.8, '#c09a6b');
    cargo(4.4, 2.5, 1.2, 1.1, 1.2, '#865b37');
    cargo(3.8, 5.5, 1.3, 1.1, 1.3, '#b08757');
    cargo(4.6, 5.5, 1.3, 1.2, 1.3, '#7f5433');
    cargo(3.8, 9.0, 1.2, 1.0, 1.2, '#9d6f45');
    cargo(10.5, 8.5, 1.3, 1.2, 1.3, '#865b37');
    cargo(11.5, -5, 1.3, 1.2, 1.3, '#a87a4c');
    cargo(12.6, -8.5, 1.2, 1.0, 1.2, '#9d6f45');
    cargo(14.2, -6.5, 1.3, 1.2, 1.3, '#7f5433');

    // Barrels
    function barrel(x, z, size, h) {
      hb(x, 0.5 + h / 2, z, size, h, size, '#764b30');
      hb(x, 0.5 + h / 2, z, size + 0.08, 0.2, size + 0.08, '#3f2719');
    }

    barrel(3.6, -1, 0.8, 0.7);
    barrel(11.8, -9, 0.9, 0.8);
    barrel(13.0, -5, 0.9, 0.8);

    // Crane lifting cargo
    hb(4.5, 1.0, -6, 1.2, 1.0, 1.2, '#573f2b');
    hb(4.5, 2.6, -6, 0.5, 2.5, 0.5, '#9c6e44');
    hb(2.5, 3.7, -6, 4.0, 0.35, 0.35, '#573f2b');
    hb(2.0, 2.175, -6, 0.12, 2.75, 0.12, '#d6b48c');
    hb(2.0, 1.3, -6, 1.2, 1.0, 1.2, '#a87a4c');

    // Lighthouse
    hb(14, 0.7, 9, 1.8, 1.0, 1.8, '#766a57');
    for (let i = 0; i < 5; i++) {
      const y = 1.7 + i * 1.0;
      const r = 1.4 - i * 0.08;
      const col = i % 2 ? '#c33b2f' : '#efe9db';
      hb(14, y, 9, r, 1.0, r, col);
    }
    hb(14, 6.25, 9, 1.4, 0.25, 1.4, '#4f4638');
    hb(14, 6.65, 9, 1.0, 0.8, 1.0, '#313940');
    hb(14, 6.65, 9, 0.5, 0.5, 0.5, '#ffe98f');
    hb(14, 7.25, 9, 0.9, 0.4, 0.9, '#564a39');

    const harborMesh = createInstancedVoxels(harbor, mainMat, {
      castShadow: true,
      receiveShadow: true
    });
    scene.add(harborMesh);

    // ---------- Sailing Ship ----------
    const ship = [];
    function sh(x, y, z, sx, sy, sz, color, ry = 0) {
      pushVoxel(ship, x, y, z, sx, sy, sz, color, 0, ry, 0);
    }

    // Hull
    sh(0, -0.2, 0, 5.2, 1.0, 16.0, '#352116');
    sh(0, 0.25, 0, 5.0, 0.9, 13.5, '#5a3828');

    // Hull side stripes
    sh(2.55, 0.25, 0, 0.2, 0.55, 13.5, '#2f1d14');
    sh(-2.55, 0.25, 0, 0.2, 0.55, 13.5, '#2f1d14');

    // Bow and stern shaping
    sh(0, 0.35, 8.2, 2.2, 1.2, 2.2, '#5a3828');
    sh(0, 0.45, 8.8, 1.4, 0.8, 1.6, '#6c472f');
    sh(0, 0.4, -8.0, 3.0, 1.2, 2.0, '#422719');
    sh(0, 0.8, -8.2, 1.6, 0.6, 1.0, '#725134');

    // Deck
    sh(0, 1.12, 0, 4.4, 0.22, 12.6, '#b68b5c');
    sh(2.25, 1.38, 0, 0.2, 0.16, 12.6, '#8d5f39');
    sh(-2.25, 1.38, 0, 0.2, 0.16, 12.6, '#8d5f39');

    for (let z = -5; z <= 5; z += 2) {
      sh(2.25, 1.28, z, 0.2, 0.2, 0.2, '#6f4b30');
      sh(-2.25, 1.28, z, 0.2, 0.2, 0.2, '#6f4b30');
    }

    // Cabin near stern
    sh(0, 1.65, -6.0, 2.6, 1.1, 3.2, '#744f32');
    sh(0, 2.25, -6.0, 2.8, 0.35, 3.4, '#472d20');

    sh(-1.4, 1.65, -5.2, 0.25, 0.5, 0.5, '#2b3439');
    sh(1.4, 1.65, -5.2, 0.25, 0.5, 0.5, '#2b3439');
    sh(-1.4, 1.65, -6.6, 0.25, 0.5, 0.5, '#2b3439');
    sh(1.4, 1.65, -6.6, 0.25, 0.5, 0.5, '#2b3439');

    // Cargo on deck
    sh(1.3, 1.60, -2.0, 0.7, 0.6, 0.7, '#a87a4c');
    sh(-1.4, 1.62, 2.5, 0.8, 0.6, 0.8, '#865b37');
    sh(0.4, 1.60, 6.0, 0.7, 0.6, 0.7, '#b08757');
    sh(-0.4, 1.58, 3.5, 0.6, 0.55, 0.6, '#9d6f45');
    sh(1.8, 1.57, -5.5, 0.6, 0.55, 0.6, '#b88b5b');
    sh(-1.9, 1.65, -3.2, 0.6, 0.7, 0.6, '#764b30');
    sh(2.0, 1.65, 3.5, 0.6, 0.7, 0.6, '#6a422c');

    // Mast steps
    sh(0, 1.24, 0, 0.7, 0.12, 0.7, '#4f3526');
    sh(0, 1.24, 4.5, 0.6, 0.12, 0.6, '#4f3526');
    sh(0, 1.24, -4.5, 0.6, 0.12, 0.6, '#4f3526');

    // Masts
    sh(0, 4.4, 0, 0.55, 6.6, 0.55, '#4f3526');
    sh(0, 3.7, 4.5, 0.5, 5.8, 0.5, '#4f3526');
    sh(0, 3.2, -4.5, 0.5, 5.2, 0.5, '#4f3526');

    // Yards
    sh(0, 7.3, 0, 4.2, 0.32, 0.4, '#3b271a');
    sh(0, 5.7, 0, 3.6, 0.32, 0.4, '#3b271a');
    sh(0, 4.1, 0, 3.0, 0.32, 0.4, '#3b271a');
    sh(0, 6.2, 4.5, 3.2, 0.32, 0.4, '#3b271a');
    sh(0, 5.0, 4.5, 2.8, 0.32, 0.4, '#3b271a');
    sh(0, 4.8, -4.5, 2.2, 0.32, 0.4, '#3b271a');

    // Sails
    sh(0, 6.25, 0, 4.0, 2.2, 0.55, '#e9e1cf');
    sh(0, 4.95, 0, 3.4, 1.6, 0.55, '#e2d6c1');
    sh(0, 3.55, 0, 2.8, 1.2, 0.55, '#d8cbb6');
    sh(0, 5.45, 4.5, 3.0, 1.6, 0.55, '#e9e1cf');
    sh(0, 4.25, 4.5, 2.6, 1.2, 0.55, '#d8cbb6');
    sh(0, 4.1, -4.5, 2.2, 1.4, 0.55, '#e2d6c1');

    // Flag
    sh(0.35, 7.9, 0, 0.75, 0.4, 0.2, '#3f7f8c');
    sh(0.15, 8.2, 0, 0.28, 0.25, 0.2, '#d49f3c');

    // Mooring ropes to dock
    sh(3.2, 0.72, 4.5, 3.4, 0.14, 0.14, '#d6b48c');
    sh(3.2, 0.72, -4.5, 3.4, 0.14, 0.14, '#d6b48c');

    const shipGroup = new THREE.Group();
    shipGroup.position.set(-2.5, 0.0, 0);
    const shipMesh = createInstancedVoxels(ship, mainMat, {
      castShadow: true,
      receiveShadow: true
    });
    shipGroup.add(shipMesh);
    scene.add(shipGroup);

    // ---------- Harbor Buoy ----------
    const buoy = [];
    pushVoxel(buoy, 0, -0.35, 0, 0.8, 0.7, 0.8, '#c33b2f');
    pushVoxel(buoy, 0, 0.2, 0, 0.55, 0.5, 0.55, '#efe9db');
    pushVoxel(buoy, 0, 0.55, 0, 0.35, 0.4, 0.35, '#c33b2f');
    pushVoxel(buoy, 0.25, 0.6, 0, 0.4, 0.2, 0.2, '#3f7f8c');

    const buoyGroup = new THREE.Group();
    buoyGroup.position.set(-8, 0.0, 10);
    const buoyMesh = createInstancedVoxels(buoy, mainMat, {
      castShadow: true,
      receiveShadow: true
    });
    buoyGroup.add(buoyMesh);
    scene.add(buoyGroup);

    // ---------- Extras ----------
    const glow = new THREE.Mesh(
      new THREE.BoxGeometry(0.75, 0.75, 0.75),
      new THREE.MeshBasicMaterial({ color: '#fff3a0', fog: false })
    );
    glow.position.set(14, 6.65, 9);
    scene.add(glow);

    const lanternLight = new THREE.PointLight('#ffe599', 1.5, 12, 2);
    lanternLight.position.set(14, 6.7, 9);
    lanternLight.castShadow = false;
    scene.add(lanternLight);

    const sunCube = new THREE.Mesh(
      new THREE.BoxGeometry(6, 6, 6),
      new THREE.MeshBasicMaterial({ color: '#ffd98d', fog: false })
    );
    sunCube.position.set(34, 28, 18);
    scene.add(sunCube);

    // ---------- Animated Water ----------
    const waterCells = [];
    const deep = new THREE.Color('#245b6a');
    const shore = new THREE.Color('#5399a4');
    const tmp = new THREE.Color();

    for (let x = -16; x <= 1; x += 1) {
      for (let z = -12; z <= 12; z += 1) {
        const mix = THREE.MathUtils.clamp((x + 16) / 16, 0, 1);
        tmp.copy(deep).lerp(shore, mix);

        const n = Math.sin(x * 12.9898 + z * 78.233) * 0.5 + 0.5;
        tmp.offsetHSL(0, (n - 0.5) * 0.08, (n - 0.5) * 0.05);

        waterCells.push({
          x,
          baseY: -0.25,
          sx: 0.98,
          sy: 0.42,
          sz: 0.98,
          color: tmp.clone()
        });
      }
    }

    const waterMesh = new THREE.InstancedMesh(geometry, waterMat, waterCells.length);
    waterMesh.castShadow = false;
    waterMesh.receiveShadow = true;
    waterMesh.frustumCulled = false;

    const dummy = new THREE.Object3D();
    for (let i = 0; i < waterCells.length; i++) {
      const w = waterCells[i];
      dummy.position.set(w.x, w.baseY, w.z);
      dummy.scale.set(w.sx, w.sy, w.sz);
      dummy.rotation.set(0, 0, 0);
      dummy.updateMatrix();
      waterMesh.setMatrixAt(i, dummy.matrix);
      waterMesh.setColorAt(i, w.color);
    }

    waterMesh.instanceMatrix.needsUpdate = true;
    if (waterMesh.instanceColor) waterMesh.instanceColor.needsUpdate = true;
    scene.add(waterMesh);

    window.addEventListener('resize', () => {
      camera.aspect = innerWidth / innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(innerWidth, innerHeight);
    });

    const clock = new THREE.Clock();

    function animate() {
      requestAnimationFrame(animate);

      const t = clock.getElapsedTime();

      shipGroup.position.y = 0.04 + Math.sin(t * 1.4) * 0.06;
      shipGroup.rotation.z = Math.sin(t * 0.7) * 0.02;

      buoyGroup.position.y = 0.02 + Math.sin(t * 1.8 + 1) * 0.07;

      glow.scale.setScalar(0.8 + Math.sin(t * 4) * 0.2);

      for (let i = 0; i < waterCells.length; i++) {
        const w = waterCells[i];
        const wave =
          Math.sin(w.x * 0.35 + t * 1.2) * 0.13 +
          Math.cos(w.z * 0.45 + t * 0.9) * 0.11 +
          Math.sin((w.x + w.z) * 0.22 + t * 0.8) * 0.07;

        dummy.position.set(w.x, w.baseY + wave, w.z);
        dummy.scale.set(w.sx, w.sy, w.sz);
        dummy.rotation.set(0, 0, 0);
        dummy.updateMatrix();
        waterMesh.setMatrixAt(i, dummy.matrix);
      }

      waterMesh.instanceMatrix.needsUpdate = true;

      controls.update();
      renderer.render(scene, camera);
    }

    animate();
  </script>
</body>
</html>
```