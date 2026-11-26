Save this as a single `.html` file and open it in Chrome. It uses Three.js from a CDN, so you need an internet connection.

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Voxel Harbor Scene</title>
  <style>
    body {
      margin: 0;
      overflow: hidden;
      background: #9dd8ff;
    }
    #hint {
      position: fixed;
      left: 16px;
      bottom: 16px;
      padding: 10px 14px;
      color: white;
      background: rgba(0, 0, 0, 0.35);
      font-family: system-ui, sans-serif;
      font-size: 14px;
      border-radius: 8px;
      pointer-events: none;
      z-index: 10;
    }
  </style>
</head>
<body>
  <div id="hint">Drag to orbit · scroll to zoom · right-drag to pan</div>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>

  <script>
    (function () {
      const scene = new THREE.Scene();
      scene.background = new THREE.Color(0x9dd8ff);
      scene.fog = new THREE.Fog(0x9dd8ff, 55, 150);

      const renderer = new THREE.WebGLRenderer({ antialias: true });
      renderer.setSize(window.innerWidth, window.innerHeight);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      renderer.shadowMap.enabled = true;
      renderer.shadowMap.type = THREE.PCFSoftShadowMap;
      renderer.outputEncoding = THREE.sRGBEncoding;
      renderer.toneMapping = THREE.ACESFilmicToneMapping;
      renderer.toneMappingExposure = 1.15;
      document.body.appendChild(renderer.domElement);

      const camera = new THREE.PerspectiveCamera(
        50,
        window.innerWidth / window.innerHeight,
        0.1,
        250
      );
      camera.position.set(38, 24, 34);

      const controls = new THREE.OrbitControls(camera, renderer.domElement);
      controls.target.set(0, 5, 8);
      controls.enableDamping = true;
      controls.dampingFactor = 0.08;
      controls.minDistance = 18;
      controls.maxDistance = 110;
      controls.maxPolarAngle = Math.PI * 0.495;

      const hemi = new THREE.HemisphereLight(0xffffff, 0x2b5a75, 0.65);
      scene.add(hemi);

      const sun = new THREE.DirectionalLight(0xfff0cc, 0.95);
      sun.position.set(28, 48, 30);
      sun.castShadow = true;
      sun.shadow.mapSize.width = 2048;
      sun.shadow.mapSize.height = 2048;
      sun.shadow.camera.left = -60;
      sun.shadow.camera.right = 60;
      sun.shadow.camera.top = 60;
      sun.shadow.camera.bottom = -60;
      sun.shadow.camera.near = 1;
      sun.shadow.camera.far = 120;
      sun.shadow.bias = -0.0005;
      sun.target.position.set(0, 0, 8);
      scene.add(sun);
      scene.add(sun.target);

      const materialCache = {};
      function getMat(color, opts) {
        opts = opts || {};
        const key = color + "|" + JSON.stringify(opts);
        if (!materialCache[key]) {
          materialCache[key] = new THREE.MeshLambertMaterial(
            Object.assign({ color: color }, opts)
          );
        }
        return materialCache[key];
      }

      const cubeGeo = new THREE.BoxGeometry(1, 1, 1);

      function addBox(parent, x, y, z, w, h, d, material, cast, receive) {
        const mesh = new THREE.Mesh(cubeGeo, material);
        mesh.position.set(x, y, z);
        mesh.scale.set(w, h, d);
        mesh.castShadow = cast === undefined ? true : cast;
        mesh.receiveShadow = receive === undefined ? true : receive;
        parent.add(mesh);
        return mesh;
      }

      function v(parent, x, y, z, material) {
        return addBox(parent, x, y, z, 1, 1, 1, material, true, true);
      }

      // Deterministic pseudo-random for consistent water waves
      let seed = 12345;
      function rand() {
        seed = (seed * 1664525 + 1013904223) >>> 0;
        return seed / 4294967296;
      }

      // Water
      const waterMat = getMat(0x247fbf, { transparent: true, opacity: 0.96 });
      const water = new THREE.Mesh(new THREE.PlaneGeometry(170, 170), waterMat);
      water.rotation.x = -Math.PI / 2;
      water.position.y = 0;
      water.receiveShadow = true;
      scene.add(water);

      const waves = [];
      const waveColors = [0x2c8fc9, 0x3b9bd2, 0x1f78b8, 0x4aa9dc];
      for (let i = 0; i < 150; i++) {
        const x = -45 + rand() * 90;
        const z = -40 + rand() * 52;
        const w = 1.2 + rand() * 4.2;
        const d = 0.25 + rand() * 0.8;
        const y = 0.06 + rand() * 0.03;
        const wave = addBox(
          scene,
          x,
          y,
          z,
          w,
          0.12,
          d,
          getMat(waveColors[Math.floor(rand() * waveColors.length)]),
          false,
          false
        );
        wave.userData.baseY = y;
        wave.userData.phase = rand() * Math.PI * 2;
        waves.push(wave);
      }

      const foamMat = getMat(0xdff6ff, { transparent: true, opacity: 0.75 });
      for (let x = -10; x <= 10; x += 2) {
        addBox(scene, x, 0.14, 3.8, 1.6, 0.12, 0.45, foamMat, false, false);
        addBox(scene, x, 0.14, -3.8, 1.6, 0.12, 0.45, foamMat, false, false);
      }

      // Shore / quay
      addBox(scene, 0, 0.8, 27, 100, 3.4, 24, getMat(0xd2b27a));
      addBox(scene, 0, 2.35, 15.2, 100, 0.3, 2, getMat(0x777b80));

      // Wooden pier
      const pierWoodA = getMat(0x8a552b);
      const pierWoodB = getMat(0x9b6334);
      const pierDark = getMat(0x5d351c);

      for (let z = 7; z <= 17; z++) {
        for (let x = -4; x <= 10; x++) {
          const m = ((x + z) % 2 === 0) ? pierWoodA : pierWoodB;
          addBox(scene, x, 2.25, z, 0.96, 0.5, 0.96, m);
        }
      }

      for (let x = -4; x <= 10; x += 4) {
        for (let z = 8; z <= 17; z += 4) {
          addBox(scene, x, 0.75, z, 0.65, 3.5, 0.65, pierDark);
        }
      }

      for (const x of [-3, 1, 6, 10]) {
        addBox(scene, x, 2.8, 8, 0.65, 0.6, 0.65, pierDark);
        addBox(scene, x, 2.8, 16, 0.65, 0.6, 0.65, pierDark);
      }

      // Harbor crane
      const craneMat = getMat(0xe0a32c);
      const ropeMat = getMat(0x333333);
      const crateMat = getMat(0x9c642e);
      addBox(scene, -10, 5.1, 12, 0.6, 6, 0.6, craneMat);
      addBox(scene, -8, 8.0, 12, 5.5, 0.5, 0.5, craneMat);
      addBox(scene, -5.5, 5.6, 12, 0.12, 4.8, 0.12, ropeMat, false, false);
      addBox(scene, -5.5, 3.2, 12, 1.2, 1.2, 1.2, crateMat);

      // Warehouse
      addBox(scene, 18, 5, 29, 12, 5, 9, getMat(0xe8dec3));
      addBox(scene, 18, 7.8, 29, 13, 0.6, 10, getMat(0xb34c3b));
      const windowMat = getMat(0x76c6e8, { emissive: 0x123344 });
      for (const x of [14, 18, 22]) {
        addBox(scene, x, 5.2, 24.35, 1.2, 1.2, 0.2, windowMat, false, true);
      }
      addBox(scene, 18, 3.5, 24.3, 2.5, 2, 0.2, getMat(0x4a3325));

      // Lighthouse
      const whiteBand = getMat(0xf2f0e6);
      const redBand = getMat(0xd64b3c);
      for (let y = 3.1; y < 13.5; y += 1.8) {
        addBox(scene, -21, y, 30, 3.2, 1.6, 3.2, Math.round(y) % 2 ? whiteBand : redBand);
      }
      const lampGlow = getMat(0xffd36b, { emissive: 0x553300 });
      addBox(scene, -21, 14.0, 30, 2.3, 1.2, 2.3, lampGlow);
      addBox(scene, -21, 15.0, 30, 3.5, 1, 3.5, redBand);

      // Pier lamps
      function addLamp(x, z) {
        addBox(scene, x, 3.4, z, 0.3, 2.0, 0.3, getMat(0x333333));
        addBox(scene, x, 4.6, z, 0.8, 0.6, 0.8, lampGlow);
      }
      addLamp(6, 9);
      addLamp(6, 16);

      // Cargo
      const bandMat = getMat(0x4a2e19);
      function addCrate(parent, x, y, z, size) {
        size = size || 1;
        addBox(parent, x, y, z, size, size, size, crateMat);
        addBox(parent, x, y, z + size / 2 + 0.02, size * 0.95, 0.1, 0.08, bandMat, false, true);
        addBox(parent, x, y, z - size / 2 - 0.02, size * 0.95, 0.1, 0.08, bandMat, false, true);
      }
      function addBarrel(x, y, z) {
        addBox(scene, x, y, z, 1, 1.25, 1, getMat(0x6b3f2a));
        addBox(scene, x, y + 0.42, z, 1.05, 0.12, 1.05, bandMat, false, true);
        addBox(scene, x, y - 0.42, z, 1.05, 0.12, 1.05, bandMat, false, true);
      }
      addCrate(scene, 2, 3, 12, 1);
      addCrate(scene, 2, 4, 12, 1);
      addCrate(scene, 3, 3, 12, 1);
      addCrate(scene, 9, 3, 10, 1.2);
      addCrate(scene, 8, 3, 11, 1);
      addBarrel(4, 3.125, 14);
      addBarrel(5, 3.125, 14);
      addBarrel(5, 4.375, 14);

      // Gangplank
      const plankMat = getMat(0xa56c3a);
      const railMat = getMat(0x6b3618);
      for (let z = 3.6; z <= 7.4; z += 0.6) {
        addBox(scene, 3, 2.6, z, 2.6, 0.2, 0.5, plankMat);
      }
      for (let z = 3.6; z <= 7.4; z += 1.2) {
        addBox(scene, 1.6, 3.05, z, 0.2, 0.65, 0.35, railMat);
        addBox(scene, 4.4, 3.05, z, 0.2, 0.65, 0.35, railMat);
      }

      // Ship group
      const ship = new THREE.Group();
      scene.add(ship);

      const hullBottom = getMat(0x2b1d12);
      const hullSide = getMat(0x7a3f1d);
      const hullUpper = getMat(0x9a5525);
      const hullTrim = getMat(0xd9a441);
      const deckMat = getMat(0xc78a48);

      // Hull
      for (let x = -10; x <= 10; x++) {
        const a = Math.abs(x);
        const bottomHalf = a <= 7 ? 2 : (a <= 9 ? 1 : 0);
        const upperHalf = a <= 7 ? 3 : (a <= 9 ? 2 : 1);

        for (let z = -bottomHalf; z <= bottomHalf; z++) {
          v(ship, x, 0.5, z, hullBottom);
        }
        for (let z = -upperHalf; z <= upperHalf; z++) {
          v(ship, x, 1.3, z, hullSide);
          v(ship, x, 2.1, z, hullUpper);
        }
      }

      // Deck and rails
      for (let x = -8; x <= 8; x++) {
        for (let z = -3; z <= 3; z++) {
          addBox(ship, x, 2.55, z, 1, 0.3, 1, deckMat);
        }
      }
      for (let x = -8; x <= 8; x++) {
        addBox(ship, x, 3.0, 3.4, 0.45, 0.6, 0.45, railMat);
        addBox(ship, x, 3.0, -3.4, 0.45, 0.6, 0.45, railMat);
      }
      addBox(ship, 0, 3.25, 3.4, 17, 0.2, 0.25, railMat);
      addBox(ship, 0, 3.25, -3.4, 17, 0.2, 0.25, railMat);
      addBox(ship, 0, 1.55, 3.55, 17, 0.25, 0.2, hullTrim);
      addBox(ship, 0, 1.55, -3.55, 17, 0.25, 0.2, hullTrim);

      // Stern cabin
      const cabinMat = getMat(0xe2c68c);
      const roofMat = getMat(0x8b3e2f);
      for (let x = 7; x <= 10; x++) {
        for (let z = -2; z <= 2; z++) {
          v(ship, x, 3.1, z, cabinMat);
          v(ship, x, 3.9, z, cabinMat);
          v(ship, x, 4.7, z, roofMat);
        }
      }
      addBox(ship, 8.5, 3.55, 2.55, 2.4, 0.45, 0.2, windowMat, false, true);
      addBox(ship, 8.5, 3.55, -2.55, 2.4, 0.45, 0.2, windowMat, false, true);

      // Masts, yards, sails
      const mastMat = getMat(0x6b3e20);
      const yardMat = getMat(0x4a2a16);
      const sailA = getMat(0xf6f0df);
      const sailB = getMat(0xe9dec5);
      const flagMat = getMat(0xd74336);

      function addSail(m, xStart, xEnd, yStart, yEnd, z) {
        for (let x = xStart; x <= xEnd; x++) {
          for (let y = yStart; y <= yEnd; y++) {
            const s = ((x + y) % 2 === 0) ? sailA : sailB;
            addBox(ship, x, y, z, 0.92, 0.92, 0.18, s, true, false);
          }
        }
      }

      for (const m of [-5, 3]) {
        addBox(ship, m, 8.1, 0, 0.55, 10.8, 0.55, mastMat);
        addBox(ship, m, 7.8, 0, 8, 0.3, 0.3, yardMat);
        addBox(ship, m, 11.5, 0, 5.5, 0.3, 0.3, yardMat);
        addBox(ship, m, 13.5, 0, 1.4, 0.5, 1.4, railMat);
        addBox(ship, m + 0.1, 14.2, 0, 0.2, 1.0, 0.2, mastMat);
        addBox(ship, m + 1.2, 14.4, 0, 2.2, 0.55, 0.12, flagMat);
      }

      addSail(-5, -8, -2, 5, 9, 0.55);
      addSail(-5, -7, -3, 10, 13, 0.55);
      addSail(3, 0, 6, 5, 9, 0.55);
      addSail(3, 1, 5, 10, 13, 0.55);

      // Bowsprit and anchor detail
      addBox(ship, -11.5, 3.2, 0, 4, 0.35, 0.35, mastMat);
      addBox(ship, -9.5, 2.2, 3.55, 1.2, 0.35, 0.25, getMat(0x222222));
      addBox(ship, -9.5, 2.9, 3.55, 0.25, 1.4, 0.25, getMat(0x222222));

      // Voxel people
      const skinMat = getMat(0xe4b58a);
      const pantsMat = getMat(0x34445c);
      const shirtRed = getMat(0xc74336);
      const shirtBlue = getMat(0x3c76b8);
      const shirtYellow = getMat(0xd9b13a);
      const shirtGreen = getMat(0x4b9360);
      const hatMat = getMat(0x4a3325);

      function addPerson(parent, x, y, z, shirt, hat) {
        const g = new THREE.Group();
        g.position.set(x, y, z);
        parent.add(g);

        addBox(g, 0, 1.55, 0, 0.55, 0.55, 0.55, skinMat);
        addBox(g, 0, 0.95, 0, 0.7, 0.8, 0.45, shirt);
        addBox(g, -0.48, 1.0, 0, 0.18, 0.65, 0.2, skinMat);
        addBox(g, 0.48, 1.0, 0, 0.18, 0.65, 0.2, skinMat);
        addBox(g, -0.18, 0.3, 0, 0.22, 0.6, 0.25, pantsMat);
        addBox(g, 0.18, 0.3, 0, 0.22, 0.6, 0.25, pantsMat);
        addBox(g, 0, 1.95, 0, 0.75, 0.18, 0.75, hat);

        return g;
      }

      addPerson(ship, -1, 2.7, 1.4, shirtRed, hatMat);
      addPerson(ship, 6, 2.7, -1.2, shirtBlue, hatMat);
      addPerson(scene, 0, 2.5, 11, shirtYellow, hatMat);
      addPerson(scene, 6, 2.5, 14, shirtGreen, hatMat);
      addPerson(scene, -3, 2.5, 9, shirtRed, hatMat);

      // Voxel clouds
      function addCloud(cx, cy, cz) {
        const cloud = new THREE.Group();
        cloud.position.set(cx, cy, cz);
        scene.add(cloud);
        const cloudMat = getMat(0xffffff);
        addBox(cloud, 0, 0, 0, 7, 2, 3, cloudMat, false, false);
        addBox(cloud, 4, 1.1, 0, 4, 2, 3, cloudMat, false, false);
        addBox(cloud, -4, 0.7, 0, 3, 1.6, 3, cloudMat, false, false);
      }
      addCloud(-25, 23, -45);
      addCloud(18, 27, -55);
      addCloud(35, 20, -35);

      const clock = new THREE.Clock();

      function animate() {
        requestAnimationFrame(animate);
        const t = clock.getElapsedTime();

        // Gentle ship rocking
        ship.rotation.x = Math.sin(t * 0.45) * 0.012;
        ship.rotation.z = Math.sin(t * 0.32) * 0.006;

        // Gentle waves
        for (const wave of waves) {
          wave.position.y =
            wave.userData.baseY + Math.sin(t * 1.1 + wave.userData.phase) * 0.05;
        }

        controls.update();
        renderer.render(scene, camera);
      }

      animate();

      window.addEventListener("resize", function () {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
      });
    })();
  </script>
</body>
</html>
```