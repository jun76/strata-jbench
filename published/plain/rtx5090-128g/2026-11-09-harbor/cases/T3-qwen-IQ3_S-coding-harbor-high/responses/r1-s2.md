Save the following as a single file, for example `harbor.html`, then open it in Chrome. It uses Three.js from a CDN, so it needs internet access on first load.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>A sailing ship calling at a harbor</title>

  <style>
    html, body {
      height: 100%;
      margin: 0;
      overflow: hidden;
      background: #9ed7ff;
    }

    canvas {
      display: block;
    }

    #info {
      position: fixed;
      top: 10px;
      left: 12px;
      color: #183142;
      font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
      font-size: 14px;
      pointer-events: none;
      text-shadow: 0 1px 0 rgba(255, 255, 255, 0.6);
      z-index: 10;
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
  <div id="info">A sailing ship calling at a harbor — drag to orbit, scroll to zoom</div>

  <script type="module">
    import * as THREE from 'three';
    import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x9ed7ff);
    scene.fog = new THREE.Fog(0xa9d8ff, 120, 300);

    const camera = new THREE.PerspectiveCamera(
      52,
      window.innerWidth / window.innerHeight,
      0.1,
      1000
    );
    camera.position.set(-42, 30, -36);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    document.body.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.target.set(-2, 6, 0);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.minDistance = 18;
    controls.maxDistance = 190;
    controls.maxPolarAngle = Math.PI * 0.49;

    const hemisphere = new THREE.HemisphereLight(0xbfe7ff, 0x6b5c4b, 0.85);
    scene.add(hemisphere);

    const ambient = new THREE.AmbientLight(0xffffff, 0.2);
    scene.add(ambient);

    const sun = new THREE.DirectionalLight(0xfff1cc, 1.25);
    sun.position.set(70, 85, -10);
    sun.castShadow = true;
    sun.shadow.mapSize.set(2048, 2048);

    const shadowExtent = 95;
    sun.shadow.camera.left = -shadowExtent;
    sun.shadow.camera.right = shadowExtent;
    sun.shadow.camera.top = shadowExtent;
    sun.shadow.camera.bottom = -shadowExtent;
    sun.shadow.camera.near = 1;
    sun.shadow.camera.far = 260;
    sun.shadow.bias = -0.0006;
    sun.shadow.normalBias = 0.02;
    sun.shadow.camera.updateProjectionMatrix();

    sun.target.position.set(0, 0, 0);
    scene.add(sun);
    scene.add(sun.target);

    const geometryCache = new Map();
    function boxGeo(w, h, d) {
      const key = `${w}|${h}|${d}`;
      let geo = geometryCache.get(key);
      if (!geo) {
        geo = new THREE.BoxGeometry(w, h, d);
        geometryCache.set(key, geo);
      }
      return geo;
    }

    const materialCache = new Map();
    function lambert(color) {
      let mat = materialCache.get(color);
      if (!mat) {
        mat = new THREE.MeshLambertMaterial({ color });
        materialCache.set(color, mat);
      }
      return mat;
    }

    function addMesh(geo, material, x, y, z, parent = scene, cast = true, receive = true) {
      const mesh = new THREE.Mesh(geo, material);
      mesh.position.set(x, y, z);
      mesh.castShadow = cast;
      mesh.receiveShadow = receive;
      parent.add(mesh);
      return mesh;
    }

    function addBox(w, h, d, color, x, y, z, parent = scene, cast = true, receive = true) {
      return addMesh(boxGeo(w, h, d), lambert(color), x, y, z, parent, cast, receive);
    }

    function addBasicBox(w, h, d, color, x, y, z, opacity = 1, parent = scene) {
      const material = new THREE.MeshBasicMaterial({
        color,
        transparent: opacity < 1,
        opacity,
        depthWrite: opacity >= 1
      });

      if (opacity < 1) {
        material.blending = THREE.AdditiveBlending;
      }

      const mesh = new THREE.Mesh(boxGeo(w, h, d), material);
      mesh.position.set(x, y, z);
      mesh.castShadow = false;
      mesh.receiveShadow = false;
      parent.add(mesh);
      return mesh;
    }

    /* Water */
    let water = null;
    let waterData = [];
    const waterDummy = new THREE.Object3D();

    function buildWater() {
      const size = 3;
      const geo = new THREE.BoxGeometry(size, 1, size);
      const mat = new THREE.MeshPhongMaterial({
        color: 0xffffff,
        specular: 0x256d8a,
        shininess: 12,
        flatShading: true
      });

      const positions = [];
      for (let x = -66; x <= 66; x += size) {
        for (let z = -66; z <= 66; z += size) {
          positions.push({ x, z });
        }
      }

      waterData = positions;
      water = new THREE.InstancedMesh(geo, mat, positions.length);
      water.receiveShadow = true;
      water.castShadow = false;

      const c = new THREE.Color();
      for (let i = 0; i < positions.length; i++) {
        c.setHSL(
          0.555 + (i % 7) * 0.008,
          0.62,
          0.40 + ((i * 13) % 11) * 0.015
        );
        water.setColorAt(i, c);
      }

      if (water.instanceColor) {
        water.instanceColor.needsUpdate = true;
      }

      scene.add(water);
    }

    function updateWater(t) {
      for (let i = 0; i < waterData.length; i++) {
        const p = waterData[i];

        const y =
          -0.5 +
          0.16 * Math.sin(t * 1.1 + p.x * 0.07 + p.z * 0.05) +
          0.12 * Math.cos(t * 0.8 - p.z * 0.08 + p.x * 0.04);

        waterDummy.position.set(p.x, y, p.z);
        waterDummy.rotation.set(0, 0, 0);
        waterDummy.scale.set(1, 1, 1);
        waterDummy.updateMatrix();

        water.setMatrixAt(i, waterDummy.matrix);
      }

      water.instanceMatrix.needsUpdate = true;
    }

    /* Harbor, land, pier, buildings */
    function addBuilding(x, z, w, d, h, wallColor, roofColor) {
      addBox(w, h, d, wallColor, x, 3 + h / 2, z);

      const roofLayers = Math.max(1, Math.floor(Math.min(w, d) / 3));
      for (let i = 0; i < roofLayers; i++) {
        addBox(w - i * 2, 1, d - i * 2, roofColor, x, 3 + h + 0.5 + i, z);
      }

      const westX = x - w / 2 - 0.05;

      for (let wy = 4.4; wy < 3 + h - 1.0; wy += 2.0) {
        addBox(0.1, 1.1, 0.8, 0xe9f5ff, westX, wy, z - 1.6, scene, true, false);
        addBox(0.1, 1.1, 0.8, 0xe9f5ff, westX, wy, z + 1.6, scene, true, false);
      }

      addBox(0.12, 1.8, 1.0, 0x5d3f28, westX, 3.9, z, scene, true, false);
    }

    function addTree(x, z) {
      addBox(0.5, 2.8, 0.5, 0x6b4a31, x, 4.4, z);
      addBox(3, 1, 3, 0x31733a, x, 5.9, z);
      addBox(2.4, 1, 2.4, 0x3d8c48, x, 6.9, z);
      addBox(1.6, 1, 1.6, 0x4ca15a, x, 7.9, z);
    }

    function buildHarbor() {
      /* Main island / harbor front */
      let ix = 0;
      for (let x = 16; x <= 58; x += 3, ix++) {
        let iz = 0;
        for (let z = -42; z <= 42; z += 3, iz++) {
          addBox(
            3,
            3,
            3,
            ((ix + iz) % 2 === 0) ? 0x76ac5c : 0x87bf68,
            x,
            1.5,
            z
          );
        }
      }

      /* Small hills */
      const hills = [
        [26, -30],
        [34, -36],
        [38, 30],
        [48, -16],
        [50, 20],
        [55, 0]
      ];

      for (const [x, z] of hills) {
        addBox(6, 2, 6, 0x76ac5c, x, 4, z);
        addBox(4, 1.2, 4, 0x87bf68, x, 5.4, z);
      }

      /* Quay wall */
      for (let z = -40; z <= 40; z += 2) {
        addBox(2, 4, 2, 0x756b64, 14, 2, z);
        addBox(2.2, 0.6, 2.2, 0x8f877f, 14, 4.3, z);
      }

      /* Main pier */
      for (let z = -8; z <= 8; z += 2) {
        addBox(12, 0.4, 2, 0xa8764d, 8, 3.7, z);
      }

      for (const x of [4, 8, 12]) {
        for (const z of [-7, -4, 0, 4, 7]) {
          addBox(0.6, 5, 0.6, 0x6f4b30, x, 1.2, z);
        }
      }

      /* Pier railings */
      for (let z = -8; z <= 8; z += 2) {
        addBox(0.25, 1.2, 0.25, 0x8a6143, 13.7, 4.5, z);
        addBox(0.25, 1.2, 0.25, 0x8a6143, 2.3, 4.5, z);
      }

      addBox(0.18, 0.18, 17, 0x8a6143, 13.7, 5.1, 0);
      addBox(0.18, 0.18, 17, 0x8a6143, 2.3, 5.1, 0);

      /* Gangplank toward ship */
      addBox(4.5, 0.15, 1.2, 0xb5966c, 0.5, 3.9, 0);

      /* Cargo crates */
      const cargoSpots = [
        [5, -5, 1.8],
        [6.7, -3.5, 1.5],
        [4.5, -6, 1.4],
        [10, 5.5, 2.0],
        [12, 4, 1.6],
        [3.5, 3.5, 1.8],
        [8, -6.5, 1.4]
      ];

      const cargoColors = [0xc49b5c, 0xb57c47, 0x8c633d, 0x6d5133];

      for (let i = 0; i < cargoSpots.length; i++) {
        const [x, z, s] = cargoSpots[i];
        addBox(s, s, s, cargoColors[i % cargoColors.length], x, 3.9 + s / 2, z);
        addBox(s + 0.12, 0.12, s + 0.12, 0x8c633d, x, 3.9 + s + 0.06, z);
      }

      /* Barrels */
      for (let i = 0; i < 4; i++) {
        const bx = 1.8 + i * 1.6;
        addBox(1.3, 1.6, 1.3, 0x8b5e34, bx, 4.7, 7.2);
        addBox(1.4, 0.12, 1.4, 0x6f4b30, bx, 5.51, 7.2);
      }

      /* Warehouses and buildings */
      addBuilding(24, -20, 8, 10, 5, 0xa54a39, 0x502d27);
      addBuilding(24, 20, 8, 10, 5, 0x456f98, 0x293f5d);
      addBuilding(33, -2, 10, 9, 6, 0x8f6b4a, 0x4e3627);
      addBuilding(43, -32, 8, 8, 5, 0xcab8a1, 0x6c5c50);
      addBuilding(43, 32, 8, 8, 5, 0xcab8a1, 0x6c5c50);
      addBuilding(50, 0, 7, 7, 4, 0xb58d70, 0x5c4435);

      /* Trees */
      const treeSpots = [
        [19, 38],
        [22, -38],
        [30, -40],
        [31, 8],
        [40, -40],
        [40, 40],
        [48, -12],
        [52, 26],
        [55, -24]
      ];

      for (const [x, z] of treeSpots) {
        addTree(x, z);
      }
    }

    /* Breakwaters */
    function buildBreakwaters() {
      for (let x = -16; x <= 14; x += 3) {
        const c = ((x / 3) & 1) ? 0x6a625c : 0x58514b;
        addBox(3, 3, 3, c, x, 1.5, -34);
        addBox(3, 3, 3, c, x, 1.5, 34);
      }

      for (let x = -15; x <= 13; x += 6) {
        addBox(2, 2, 2, 0x5d5650, x + 1, 3.2, -33);
        addBox(2, 2, 2, 0x4e4843, x + 2, 3.2, 33);
      }
    }

    /* Lighthouse */
    let beamGroup = null;

    function buildLighthouse() {
      const x = 14;
      const z = -30;

      addBox(5, 1, 5, 0x9a928a, x, 4.5, z);

      for (let i = 0; i < 7; i++) {
        const size = 4.2 - i * 0.2;
        addBox(
          size,
          1.5,
          size,
          (i % 2 === 0) ? 0xc8524d : 0xf5f1e7,
          x,
          5.75 + i * 1.5,
          z
        );
      }

      addBasicBox(3, 1.8, 3, 0xffe89e, x, 16, z, 1);
      addBox(3.6, 0.7, 3.6, 0x3f4448, x, 17.15, z);

      beamGroup = new THREE.Group();
      beamGroup.position.set(x, 16, z);
      scene.add(beamGroup);

      addBasicBox(38, 1.4, 2.8, 0xffe9a8, 21.5, 0, 0, 0.18, beamGroup);
      addBasicBox(38, 1.4, 2.8, 0xffe9a8, -21.5, 0, 0, 0.18, beamGroup);

      const lampLight = new THREE.PointLight(0xffe7a0, 0.8, 90, 2);
      lampLight.position.set(x, 16, z);
      lampLight.castShadow = false;
      scene.add(lampLight);
    }

    /* Sailing ship */
    let ship = null;

    function buildShip() {
      const g = new THREE.Group();

      const dark = 0x4d3320;
      const wood = 0x7c5232;
      const light = 0xc5a26d;
      const sail = 0xf7f2e8;
      const red = 0xa73c2b;

      const b = (w, h, d, color, x, y, z, cast = true, receive = true) => {
        return addBox(w, h, d, color, x, y, z, g, cast, receive);
      };

      /* Waterline stripe */
      b(8.4, 0.7, 25.8, red, 0, 0.35, 0);

      /* Hull */
      b(6, 3, 26, dark, 0, 1.5, 0);
      b(8, 1.2, 24, wood, 0, 3.4, 0);
      b(8.3, 0.45, 25, dark, 0, 3.85, 0);
      b(7.1, 0.1, 23.5, light, 0, 4.0, 0);

      /* Bow / stern lower hull */
      b(4.5, 2.5, 5, dark, 0, 1.25, -13.5);
      b(5, 2, 4.5, dark, 0, 1.5, 13.5);

      /* Castles */
      b(5.5, 2.2, 5, wood, 0, 5.1, -9.5);
      b(6.6, 2.6, 6.5, wood, 0, 5.3, 10.5);
      b(6.2, 2.2, 3.5, dark, 0, 5.4, 13.8);

      /* Small deckhouse */
      b(4.5, 1.2, 4, wood, 0, 4.6, 2);
      b(4.7, 0.1, 4.2, light, 0, 5.25, 2);

      /* Gunports */
      for (let z = -10; z <= 10; z += 4) {
        b(0.7, 0.8, 0.7, 0x1b1b1b, -3.1, 1.7, z);
        b(0.7, 0.8, 0.7, 0x1b1b1b, 3.1, 1.7, z);
      }

      /* Bowsprit and fore sail */
      b(0.4, 0.4, 10, dark, 0, 5.5, -21);
      b(0.3, 0.3, 4, dark, 0, 5.8, -16);
      b(1.2, 3, 6, sail, 0, 5.5, -21);

      /* Masts */
      function mast(z, bottom, top) {
        b(0.65, top - bottom, 0.65, dark, 0, (top + bottom) / 2, z);
      }

      mast(-9, 4.5, 17);
      mast(0, 4.0, 20);
      mast(10, 6.6, 16);

      /* Sails: [mastZ, centerY, height, lengthAlongShip] */
      const sails = [
        { z: -9, y: 8.0, h: 3.2, l: 4.5 },
        { z: -9, y: 11.5, h: 2.8, l: 3.5 },

        { z: 0, y: 8.5, h: 5.0, l: 7.0 },
        { z: 0, y: 13.5, h: 4.5, l: 6.0 },
        { z: 0, y: 17.5, h: 3.0, l: 4.5 },

        { z: 10, y: 8.5, h: 3.0, l: 4.0 },
        { z: 10, y: 11.5, h: 2.5, l: 3.0 }
      ];

      for (const s of sails) {
        b(1.2, s.h, s.l, sail, 0, s.y, s.z);
        b(0.5, 0.3, s.l, dark, 0, s.y + s.h / 2, s.z);
      }

      /* Flag on main mast */
      b(0.18, 3, 0.18, dark, 0, 21.5, 0);
      b(2.4, 1.3, 0.15, 0x2a4d9a, 1.2, 22.2, 0);

      /* Rigging */
      const linePoints = [];

      function line(ax, ay, az, bx, by, bz) {
        linePoints.push(
          new THREE.Vector3(ax, ay, az),
          new THREE.Vector3(bx, by, bz)
        );
      }

      line(0, 20, 0, 0, 5.5, -26);
      line(0, 20, 0, 0, 5.5, 16);
      line(0, 17, -9, 0, 5.5, -26);
      line(0, 16, 10, 0, 5.5, 16);

      line(0, 17, -9, 4, 4, -9);
      line(0, 17, -9, -4, 4, -9);

      line(0, 20, 0, 4, 4, 0);
      line(0, 20, 0, -4, 4, 0);

      line(0, 16, 10, 4, 4, 10);
      line(0, 16, 10, -4, 4, 10);

      line(0, 17, -9, 4, 4, 0);
      line(0, 17, -9, -4, 4, 0);

      line(0, 20, 0, 4, 4, 10);
      line(0, 20, 0, -4, 4, 10);

      const rigging = new THREE.LineSegments(
        new THREE.BufferGeometry().setFromPoints(linePoints),
        new THREE.LineBasicMaterial({
          color: 0x2f231b,
          transparent: true,
          opacity: 0.8
        })
      );

      rigging.castShadow = false;
      rigging.receiveShadow = false;
      g.add(rigging);

      ship = g;
      ship.position.set(-5, 0, 0);
      scene.add(ship);
    }

    /* Clouds */
    let clouds = [];

    function buildClouds() {
      const spots = [
        [-90, 28, -70],
        [-20, 34, -100],
        [70, 30, -40],
        [130, 36, 20],
        [-80, 38, 70],
        [-140, 32, 0],
        [20, 40, 110],
        [150, 28, -80]
      ];

      spots.forEach(([x, y, z], i) => {
        const group = new THREE.Group();

        addBox(22, 7, 10, 0xffffff, 0, 0, 0, group, false, false);
        addBox(14, 7, 12, 0xf4f8ff, -8, 3, 1, group, false, false);
        addBox(16, 6, 9, 0xffffff, 10, 2, -1, group, false, false);

        group.position.set(x, y, z);
        scene.add(group);

        clouds.push({
          group,
          x,
          speed: 0.35 + i * 0.05,
          phase: i * 17
        });
      });
    }

    function updateClouds(t) {
      for (const c of clouds) {
        const nx = ((c.x + 200 + t * c.speed + c.phase) % 400) - 200;
        c.group.position.x = nx;
      }
    }

    /* Seagulls */
    let birds = [];

    function buildBirds() {
      for (let i = 0; i < 4; i++) {
        const group = new THREE.Group();

        addBox(1.6, 0.3, 0.4, 0xffffff, 0, 0, 0, group, false, false);
        addBox(1.4, 0.18, 0.35, 0xf1f6ff, 0.15, 0.18, 1.0, group, false, false);
        addBox(1.4, 0.18, 0.35, 0xf1f6ff, 0.15, 0.18, -1.0, group, false, false);

        scene.add(group);

        birds.push({
          group,
          radius: 38 + i * 6,
          height: 25 + i * 3,
          speed: 0.11 + i * 0.02,
          phase: i * 1.3
        });
      }
    }

    function updateBirds(t) {
      for (const b of birds) {
        const a = t * b.speed + b.phase;

        b.group.position.set(
          Math.cos(a) * b.radius,
          b.height + Math.sin(t * 2.2 + b.phase) * 1.0,
          Math.sin(a) * b.radius
        );

        b.group.rotation.y = -a - Math.PI / 2;
      }
    }

    buildWater();
    buildHarbor();
    buildBreakwaters();
    buildLighthouse();
    buildShip();
    buildClouds();
    buildBirds();

    const clock = new THREE.Clock();

    function animate() {
      const t = clock.getElapsedTime();

      updateWater(t);
      updateClouds(t);
      updateBirds(t);

      if (ship) {
        const bob =
          0.12 * Math.sin(t * 1.0) +
          0.08 * Math.cos(t * 0.7);

        ship.position.y = bob;
        ship.rotation.z = 0.022 * Math.sin(t * 1.15);
        ship.rotation.x = 0.016 * Math.cos(t * 0.95);
        ship.rotation.y = 0.012 * Math.sin(t * 0.35);
      }

      if (beamGroup) {
        beamGroup.rotation.y += 0.006;
      }

      controls.update();
      renderer.render(scene, camera);
      requestAnimationFrame(animate);
    }

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