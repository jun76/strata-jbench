Paste this as a single `.html` file and open it in Chrome.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Voxel Harbor — Sailing Ship in Harbor</title>
  <style>
    html, body { margin:0; width:100%; height:100%; overflow:hidden; background:#9fd8ef; }
    canvas { display:block; }
    #hint {
      position:fixed; left:12px; bottom:12px;
      color:#fff; font:14px/1.3 system-ui, sans-serif;
      text-shadow:0 1px 3px rgba(0,0,0,.65);
      pointer-events:none; opacity:.95;
    }
  </style>
</head>
<body>
  <div id="hint">Drag to orbit • Scroll to zoom • Right-drag to pan</div>

  <script type="importmap">
  {
    "imports": {
      "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
      "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
    }
  }
  </script>

  <script type="module">
  import * as THREE from 'three';
  import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x9fd8ef);
  scene.fog = new THREE.Fog(0x9fd8ef, 78, 190);

  const camera = new THREE.PerspectiveCamera(52, window.innerWidth / window.innerHeight, 0.1, 500);
  camera.position.set(28, 19, 34);

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.06;
  document.body.appendChild(renderer.domElement);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.target.set(0, 4, 0);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.minDistance = 9;
  controls.maxDistance = 95;
  controls.maxPolarAngle = Math.PI * 0.49;
  controls.update();

  const hemi = new THREE.HemisphereLight(0xcbeeff, 0x475c35, 0.72);
  scene.add(hemi);

  const sunLight = new THREE.DirectionalLight(0xfff1d6, 1.75);
  sunLight.position.set(40, 58, 28);
  sunLight.castShadow = true;
  sunLight.shadow.mapSize.set(2048, 2048);
  sunLight.shadow.camera.left = -58;
  sunLight.shadow.camera.right = 58;
  sunLight.shadow.camera.top = 58;
  sunLight.shadow.camera.bottom = -58;
  sunLight.shadow.camera.near = 1;
  sunLight.shadow.camera.far = 170;
  sunLight.shadow.bias = -0.0012;
  sunLight.target.position.set(0, 3, 0);
  scene.add(sunLight);
  scene.add(sunLight.target);

  const unit = new THREE.BoxGeometry(1, 1, 1);
  const matCache = new Map();

  function mat(color) {
    let m = matCache.get(color);
    if (!m) {
      m = new THREE.MeshStandardMaterial({
        color,
        flatShading: true,
        roughness: 0.84,
        metalness: 0.02
      });
      matCache.set(color, m);
    }
    return m;
  }

  function addBox(parent, color, x, y, z, w = 1, h = 1, d = 1) {
    const mesh = new THREE.Mesh(unit, mat(color));
    mesh.position.set(x, y, z);
    mesh.scale.set(w, h, d);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    parent.add(mesh);
    return mesh;
  }

  const staticMap = new Map();

  function addStatic(color, x, y, z, w = 1, h = 1, d = 1) {
    if (!staticMap.has(color)) staticMap.set(color, []);
    staticMap.get(color).push([x, y, z, w, h, d]);
  }

  function flushStatic() {
    const matrix = new THREE.Matrix4();
    const pos = new THREE.Vector3();
    const quat = new THREE.Quaternion();
    const scale = new THREE.Vector3();

    for (const [color, items] of staticMap) {
      const mesh = new THREE.InstancedMesh(unit, mat(color), items.length);

      items.forEach((it, i) => {
        matrix.compose(
          pos.set(it[0], it[1], it[2]),
          quat,
          scale.set(it[3], it[4], it[5])
        );
        mesh.setMatrixAt(i, matrix);
      });

      mesh.castShadow = true;
      mesh.receiveShadow = true;
      scene.add(mesh);
    }

    staticMap.clear();
  }

  const palette = {
    grass: 0x5fa53e,
    grassDark: 0x48852c,
    dirt: 0x7e5a3b,
    sand: 0xdcc58a,
    dock: 0xb08055,
    dockDark: 0x7b5636,
    stone: 0x8d8d8d,
    stoneDark: 0x696969,
    brick: 0xb45f56,
    roof: 0x6b4231,
    white: 0xf5f5f5,
    red: 0xd64545,
    blue: 0x2e6fb0,
    wood: 0x8b5a2b,
    darkWood: 0x5a391e,
    trim: 0xcfa45f,
    deck: 0xb88b55,
    sail: 0xf2ead8,
    sailShade: 0xd7cdb5,
    mast: 0x4b3520,
    black: 0x1f1f1f,
    green: 0x46b04a
  };

  const flags = [];
  const flagGeo = new THREE.BoxGeometry(1, 0.62, 0.08);

  function addFlag(parent, x, y, z, color, size = 2) {
    const group = new THREE.Group();
    group.position.set(x, y, z);

    const mesh = new THREE.Mesh(
      flagGeo,
      new THREE.MeshStandardMaterial({ color, flatShading: true, roughness: 0.9 })
    );

    mesh.scale.set(size, 1, 1);
    mesh.position.set(size / 2, 0, 0);
    mesh.castShadow = false;
    mesh.receiveShadow = false;
    group.add(mesh);
    parent.add(group);

    flags.push({ mesh, base: size, phase: Math.random() * Math.PI * 2 });
  }

  function addTree(x, z) {
    addStatic(0x6b4226, x, 2, z, 0.8, 2, 0.8);
    addStatic(0x3a7a2e, x, 4, z, 3, 2, 3);
    addStatic(0x2f6b25, x, 5.2, z, 2, 1, 2);
  }

  function addCrateStatic(x, z) {
    addStatic(palette.dock, x, 1.75, z, 1.1, 1.1, 1.1);
    addStatic(palette.darkWood, x, 1.75, z, 1.25, 0.12, 1.25);
    addStatic(palette.darkWood, x, 1.75, z, 0.12, 1.25, 1.25);
  }

  function addBarrelStatic(x, z) {
    addStatic(palette.wood, x, 1.55, z, 0.9, 1.1, 0.9);
    addStatic(palette.black, x, 1.55, z, 1.05, 0.12, 1.05);
    addStatic(palette.black, x, 1.55, z, 0.12, 1.05, 1.05);
  }

  function addFlagPole(x, z) {
    addStatic(palette.dockDark, x, 2, z, 0.25, 2, 0.25);
    addFlag(scene, x, 3.1, z, palette.blue, 2.2);
  }

  function addShed(x, z) {
    addStatic(palette.wood, x, 2.75, z, 3.2, 2.5, 3);
    addStatic(0x5d3828, x, 4.25, z, 3.6, 0.8, 3.4);
    addStatic(palette.black, x, 2.2, z + 1.65, 1.6, 2, 0.2);
  }

  function buildGround() {
    for (let x = -34; x <= 34; x++) {
      for (let z = -46; z <= -15; z++) {
        const c = ((x * 7 + z * 11) % 7 === 0) ? palette.grassDark : palette.grass;
        addStatic(c, x, 0.5, z);
        addStatic(palette.dirt, x, -0.5, z);
        addStatic(palette.dirt, x, -1.5, z);
      }
    }

    for (let x = -34; x <= 34; x++) {
      for (let z = -14; z <= -13; z++) {
        addStatic(palette.sand, x, 0.5, z);
        addStatic(palette.dirt, x, -0.5, z);
        addStatic(palette.dirt, x, -1.5, z);
      }
    }
  }

  function buildBreakwater() {
    for (let x = -31; x <= -22; x++) {
      for (let z = -12; z <= 26; z++) {
        addStatic(palette.stone, x, 0.5, z);
        addStatic(palette.stone, x, 1.5, z);
        addStatic(palette.stoneDark, x, 2.5, z);
      }
    }

    for (let x = 22; x <= 31; x++) {
      for (let z = -12; z <= 26; z++) {
        addStatic(palette.stone, x, 0.5, z);
        addStatic(palette.stone, x, 1.5, z);
        addStatic(palette.stoneDark, x, 2.5, z);
      }
    }

    for (let z = 24; z <= 26; z++) {
      for (let x = -31; x <= 31; x++) {
        if (x >= -3 && x <= 3) continue;
        addStatic(palette.stone, x, 0.5, z);
        addStatic(palette.stone, x, 1.5, z);
        addStatic(palette.stoneDark, x, 2.5, z);
      }
    }

    addStatic(palette.red, -26, 3.5, 24, 1.2, 1.2, 1.2);
    addStatic(palette.green, 26, 3.5, 24, 1.2, 1.2, 1.2);
  }

  function buildDock() {
    for (let x = -2; x <= 2; x++) {
      for (let z = -13; z <= 5; z++) {
        addStatic(palette.dock, x, 0.75, z);
      }
    }

    for (let z = -12; z <= 4; z += 4) {
      for (const x of [-2, 0, 2]) {
        addStatic(palette.dockDark, x, -0.25, z, 0.8, 1.5, 0.8);
        addStatic(palette.dockDark, x, -1.5, z, 0.7, 1.2, 0.7);
      }
    }

    for (let x = 3; x <= 9; x++) {
      for (let z = -1; z <= 1; z++) {
        addStatic(palette.dock, x, 0.75, z);
      }
    }

    for (const x of [4, 6, 8]) {
      addStatic(palette.dockDark, x, -0.25, 0, 0.7, 1.5, 0.7);
      addStatic(palette.dockDark, x, -1.5, 0, 0.6, 1.2, 0.6);
    }

    addStatic(palette.dock, 5.5, 1.95, 0, 7.2, 0.22, 1.1);

    for (let z = -11; z <= 4; z += 3) {
      addStatic(palette.black, -2.5, 1.1, z, 0.4, 0.6, 0.4);
      addStatic(palette.black, 2.5, 1.1, z, 0.4, 0.6, 0.4);
    }

    addShed(-1, 4);

    addCrateStatic(0, 4);
    addCrateStatic(0, -10);
    addCrateStatic(5, 0);
    addCrateStatic(8, 0);

    addBarrelStatic(-4, -14);
    addBarrelStatic(-6, -13);
    addBarrelStatic(6, -14);
    addBarrelStatic(7, 0);

    addFlagPole(-2, -10);
    addFlagPole(8, 0);
  }

  function addBuilding(x, z, w, h, d, wall, roof) {
    addStatic(wall, x, 1 + h / 2, z, w, h, d);
    addStatic(roof, x, 1 + h + 0.5, z, w + 0.4, 1, d + 0.4);
    addStatic(palette.black, x, 2.5, z + d / 2 + 0.15, 2.4, 3, 0.2);

    for (let wx = x - Math.floor(w / 2) + 1; wx <= x + Math.floor(w / 2) - 1; wx += 2) {
      addStatic(0x8bb7d6, wx, 1 + h / 2, z + d / 2 + 0.15, 0.8, 0.8, 0.12);
    }

    addStatic(0x444444, x + w / 2 - 1, 1 + h + 1.5, z - 1, 1, 2, 1);
  }

  function buildBuildings() {
    addBuilding(-12, -24, 9, 6, 7, palette.brick, palette.roof);
    addBuilding(-1, -25, 8, 5, 6, 0xe7e2d7, 0x7a4e3a);
    addBuilding(11, -24, 9, 5, 7, 0xa76c43, 0x5d3828);
    addBuilding(20, -25, 6, 4, 5, 0xd7d0c4, 0x7a3b3b);
  }

  function buildLighthouse() {
    const x = 24;
    const z = -18;

    addStatic(palette.stone, x, 1.5, z, 6, 2, 6);
    addStatic(palette.stoneDark, x, 2.5, z, 5, 1, 5);

    for (let i = 0; i < 8; i++) {
      const y = 3.5 + i;
      const size = i < 2 ? 4 : (i < 5 ? 3 : 2);
      const col = (i % 2 === 0) ? palette.white : palette.red;
      addStatic(col, x, y, z, size, 1, size);
    }

    addStatic(palette.black, x, 11.5, z, 2.2, 1, 2.2);
    addStatic(palette.white, x, 12.2, z, 1.8, 0.5, 1.8);
    addStatic(palette.red, x, 12.8, z, 2.3, 0.6, 2.3);

    const beacon = new THREE.Group();
    beacon.position.set(x, 11.5, z);
    scene.add(beacon);

    const glass = new THREE.Mesh(
      unit,
      new THREE.MeshStandardMaterial({
        color: 0xfff2a8,
        emissive: 0xffc43c,
        emissiveIntensity: 1.2,
        flatShading: true
      })
    );
    glass.scale.set(1.4, 1.2, 1.4);
    beacon.add(glass);

    const beamMat = new THREE.MeshBasicMaterial({
      color: 0xfff3b0,
      transparent: true,
      opacity: 0.11,
      depthWrite: false,
      side: THREE.DoubleSide
    });

    const beam = new THREE.Mesh(
      new THREE.ConeGeometry(7, 80, 4, 1, true),
      beamMat
    );
    beam.rotation.z = -Math.PI / 2;
    beam.position.x = 40;
    beam.castShadow = false;
    beam.receiveShadow = false;
    beacon.add(beam);

    const spot = new THREE.SpotLight(0xfff0a0, 3, 120, 0.22, 0.6, 1.4);
    spot.position.set(0, 0, 0);
    beacon.add(spot);

    const target = new THREE.Object3D();
    target.position.set(x + 90, 8, z);
    scene.add(target);
    spot.target = target;

    return { beacon, beam };
  }

  const clouds = [];
  const gulls = [];
  const buoys = [];
  const boats = [];
  const cranes = [];

  function addCloud(x, y, z, s = 1) {
    const g = new THREE.Group();

    addBox(g, palette.white, 0, 0, 0, 5, 1, 3);
    addBox(g, palette.white, 2.5, 0.9, 0, 3, 1, 2);
    addBox(g, palette.white, -2.5, 0.6, 0.8, 2.6, 1, 2);
    addBox(g, palette.white, 1.1, 0.5, -1, 2.4, 1, 2);

    g.position.set(x, y, z);
    g.scale.setScalar(s);
    g.traverse(o => {
      if (o.isMesh) {
        o.castShadow = false;
        o.receiveShadow = false;
      }
    });

    scene.add(g);
    clouds.push(g);
    return g;
  }

  function makeGull() {
    const g = new THREE.Group();

    addBox(g, palette.white, 0, 0, 0, 0.5, 0.25, 1.2);
    addBox(g, palette.white, 0, 0.15, 0.55, 0.25, 0.12, 0.25);

    const l = addBox(g, palette.white, -0.9, 0, 0, 1.5, 0.08, 0.5);
    const r = addBox(g, palette.white, 0.9, 0, 0, 1.5, 0.08, 0.5);

    g.userData.l = l;
    g.userData.r = r;

    g.traverse(o => {
      if (o.isMesh) {
        o.castShadow = false;
        o.receiveShadow = false;
      }
    });

    scene.add(g);
    return g;
  }

  function addBuoy(x, z, color) {
    const g = new THREE.Group();
    addBox(g, color, 0, 0.45, 0, 1, 1, 1);
    addBox(g, palette.white, 0, 1.15, 0, 0.25, 0.5, 0.25);
    g.position.set(x, 0.55, z);
    scene.add(g);
    return g;
  }

  function addRowboat(x, z) {
    const g = new THREE.Group();
    addBox(g, palette.wood, 0, 0, 0, 3, 0.7, 1.2);
    addBox(g, palette.trim, 0, 0.45, 0, 3.1, 0.18, 1.3);
    addBox(g, palette.dock, 0, 0.35, 0, 1.6, 0.12, 0.5);
    g.position.set(x, 0.65, z);
    scene.add(g);
    return g;
  }

  function makeCrane(x, z) {
    const g = new THREE.Group();
    g.position.set(x, 1, z);
    scene.add(g);

    addBox(g, palette.dockDark, 0, 0, 0, 1.2, 1, 1.2);
    addBox(g, palette.dockDark, 0, 1, 0, 1.1, 1, 1.1);

    const arm = new THREE.Group();
    arm.position.set(0, 1.6, 0);
    g.add(arm);

    addBox(arm, palette.dock, 0, 0, 0, 1, 1, 1);

    for (let i = 1; i <= 6; i++) {
      addBox(arm, palette.dock, 0, 0, i, 0.6, 0.6, 0.6);
    }

    addBox(arm, palette.black, 0, 0, -2.5, 1.2, 1.2, 1.2);

    const cable = new THREE.Line(
      new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(0, 0, 6),
        new THREE.Vector3(0, -3.2, 6)
      ]),
      new THREE.LineBasicMaterial({ color: 0x222222 })
    );
    arm.add(cable);

    addBox(arm, palette.dock, 0, -3.9, 6, 1.2, 1.2, 1.2);

    g.userData.arm = arm;
    cranes.push(g);
    return g;
  }

  function buildScenery() {
    addTree(-24, -20);
    addTree(-19, -28);
    addTree(2, -32);
    addTree(16, -30);
    addTree(27, -22);
    addTree(-30, -24);

    addCloud(-20, 22, 10, 1.0);
    addCloud(12, 25, -5, 1.2);
    addCloud(28, 20, 18, 0.8);
    addCloud(-10, 24, 28, 1.1);

    for (let i = 0; i < 5; i++) gulls.push(makeGull());

    buoys.push(addBuoy(-6, 22, palette.red));
    buoys.push(addBuoy(6, 22, palette.green));
    buoys.push(addBuoy(14, 12, palette.red));

    boats.push(addRowboat(3, 6));
    boats.push(addRowboat(-5, -2));

    makeCrane(0, -7);
    makeCrane(8, -3);
    makeCrane(-1, 2);
  }

  function buildWater() {
    const xs = [];
    for (let x = -30; x <= 30; x += 1.5) xs.push(x);

    const zs = [];
    for (let z = -12; z <= 36; z += 1.5) zs.push(z);

    const count = xs.length * zs.length;

    const waterMat = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      flatShading: true,
      roughness: 0.18,
      metalness: 0.06
    });

    const mesh = new THREE.InstancedMesh(unit, waterMat, count);
    mesh.castShadow = false;
    mesh.receiveShadow = true;
    scene.add(mesh);

    const data = [];
    const col = new THREE.Color();
    const cShallow = new THREE.Color(0x35aecb);
    const cMid = new THREE.Color(0x1e88b8);
    const cDeep = new THREE.Color(0x155f95);

    let i = 0;

    for (const x of xs) {
      for (const z of zs) {
        data.push({ x, z });

        const t = THREE.MathUtils.clamp((z + 12) / 48, 0, 1);

        if (t < 0.35) col.lerpColors(cShallow, cMid, t / 0.35);
        else col.lerpColors(cMid, cDeep, (t - 0.35) / 0.65);

        mesh.setColorAt(i, col);
        i++;
      }
    }

    mesh.instanceColor.needsUpdate = true;
    return { mesh, data };
  }

  function buildShip() {
    const g = new THREE.Group();

    function s(color, x, y, z, w = 1, h = 1, d = 1) {
      return addBox(g, color, x, y, z, w, h, d);
    }

    for (let z = -9; z <= 9; z++) {
      const w = Math.max(1, 4 - Math.floor(Math.abs(z) / 3));

      for (let y = -2; y <= 1; y++) {
        for (let x = -w; x <= w; x++) {
          if (y === -2) {
            if (Math.abs(x) <= w - 1) s(palette.darkWood, x, y, z);
          } else if (y === 1) {
            if (Math.abs(x) === w) s(palette.wood, x, y, z);
            else s(palette.deck, x, y, z);
          } else {
            if (Math.abs(x) === w) s(palette.wood, x, y, z);
            else s(palette.darkWood, x, y, z);
          }
        }
      }

      s(palette.trim, -w, 1, z, 1, 0.2, 1);
      s(palette.trim, w, 1, z, 1, 0.2, 1);
    }

    for (let z = 5; z <= 8; z++) {
      s(palette.deck, 0, 2, z, 3, 1, 1);
    }

    s(palette.white, 0, 2.6, 6.5, 3.2, 1.3, 2.6);
    s(palette.black, 1, 2.6, 5.15, 0.9, 0.55, 0.15);
    s(palette.black, -1, 2.6, 5.15, 0.9, 0.55, 0.15);
    s(palette.mast, 0, 4, 8, 0.2, 4, 0.2);

    s(palette.wood, 0, 1, 9, 1, 1, 1);
    s(palette.trim, 0, 1.6, 9, 1.5, 0.2, 1.5);

    const sprit = s(palette.mast, 0, 3, 11.5, 0.55, 0.55, 4.5);
    sprit.rotation.x = -0.45;

    const masts = [
      { z: -4, y: 5, h: 11 },
      { z: 0, y: 6, h: 13 },
      { z: 4, y: 5.5, h: 12 }
    ];

    const rigPts = [];
    function rope(a, b) {
      rigPts.push(
        new THREE.Vector3(a[0], a[1], a[2]),
        new THREE.Vector3(b[0], b[1], b[2])
      );
    }

    for (const m of masts) {
      s(palette.mast, 0, m.y, m.z, 0.8, m.h, 0.8);
      s(palette.darkWood, 0, m.y + m.h / 2 - 0.8, m.z, 1.6, 0.4, 1.6);

      const yards = [m.y - 3, m.y, m.y + 3];
      const widths = [7, 5.5, 4];

      yards.forEach((y, i) => {
        s(palette.mast, 0, y, m.z, widths[i] + 0.8, 0.22, 0.22);
        s(palette.sail, 0, y + 1.15, m.z, widths[i], 2.2, 0.45);
        s(palette.sailShade, 0, y + 1.15, m.z + 0.3, widths[i] - 0.8, 1.8, 0.1);
      });

      const topY = m.y + m.h / 2 - 0.2;
      addFlag(g, 0, topY + 0.8, m.z, palette.red, 1.5);

      rope([0, topY, m.z], [0, 1.6, 11]);
      rope([0, topY, m.z], [0, 1.6, -10]);
      rope([0, topY, m.z], [-3, 1.6, m.z]);
      rope([0, topY, m.z], [3, 1.6, m.z]);
    }

    addFlag(g, 0, 6.4, 8, palette.red, 1.8);

    const rigGeo = new THREE.BufferGeometry().setFromPoints(rigPts);
    const rig = new THREE.LineSegments(
      rigGeo,
      new THREE.LineBasicMaterial({ color: 0x222222 })
    );
    rig.castShadow = false;
    rig.receiveShadow = false;
    g.add(rig);

    [
      [-2, 2.2, -1],
      [2, 2.2, 2],
      [-1, 2.2, 3],
      [2, 2.2, -3],
      [-2, 2.2, 5],
      [1, 2.2, -5]
    ].forEach(p => {
      s(palette.dock, p[0], p[1], p[2], 1.1, 1.1, 1.1);
      s(palette.darkWood, p[0], p[1], p[2], 1.25, 0.12, 1.25);
    });

    return g;
  }

  const sunMesh = new THREE.Mesh(
    unit,
    new THREE.MeshBasicMaterial({ color: 0xfff4bd })
  );
  sunMesh.scale.set(7, 7, 7);
  sunMesh.position.set(68, 44, 92);
  sunMesh.castShadow = false;
  scene.add(sunMesh);

  let lighthouse = null;
  let ship = null;
  let water = null;

  buildGround();
  buildBreakwater();
  buildDock();
  buildBuildings();
  lighthouse = buildLighthouse();
  buildScenery();

  flushStatic();

  ship = buildShip();
  ship.position.set(6, 0.5, 0);
  scene.add(ship);

  water = buildWater();

  const _m = new THREE.Matrix4();
  const _p = new THREE.Vector3();
  const _q = new THREE.Quaternion();
  const _s = new THREE.Vector3();

  function updateWater(t) {
    const { mesh, data } = water;

    for (let i = 0; i < data.length; i++) {
      const { x, z } = data[i];

      const y = 0.5 + Math.sin(t * 1.4 + x * 0.22 + z * 0.18) * 0.10;
      const sy = 1 + Math.sin(t * 1.7 + x * 0.15 - z * 0.12) * 0.06;

      _m.compose(_p.set(x, y, z), _q, _s.set(1.5, sy, 1.5));
      mesh.setMatrixAt(i, _m);
    }

    mesh.instanceMatrix.needsUpdate = true;
  }

  const clock = new THREE.Clock();

  function animate() {
    requestAnimationFrame(animate);

    const dt = Math.min(clock.getDelta(), 0.05);
    const t = clock.elapsedTime;

    controls.update();

    updateWater(t);

    ship.position.y = 0.5 + Math.sin(t * 1.15) * 0.12;
    ship.rotation.z = Math.sin(t * 0.92) * 0.035;
    ship.rotation.x = Math.sin(t * 0.68 + 1) * 0.014;

    for (const f of flags) {
      f.mesh.scale.x = f.base * (1 + Math.sin(t * 7 + f.phase) * 0.18);
      f.mesh.rotation.y = Math.sin(t * 2.4 + f.phase) * 0.18;
    }

    lighthouse.beacon.rotation.y += dt * 0.65;
    lighthouse.beam.material.opacity = 0.08 + Math.sin(t * 3) * 0.035;

    for (const b of buoys) {
      b.position.y = 0.55 + Math.sin(t * 2 + b.position.x) * 0.14;
      b.rotation.z = Math.sin(t * 1.3 + b.position.z) * 0.12;
    }

    for (const [i, b] of boats.entries()) {
      b.position.y = 0.65 + Math.sin(t * 1.8 + i) * 0.08;
      b.rotation.z = Math.sin(t * 1.1 + i) * 0.08;
    }

    for (const [i, c] of cranes.entries()) {
      c.userData.arm.rotation.y = Math.sin(t * 0.35 + i * 1.7) * 0.55;
    }

    for (const [i, c] of clouds.entries()) {
      c.position.x += dt * (0.45 + i * 0.18);
      if (c.position.x > 65) c.position.x = -65;
    }

    for (const [i, g] of gulls.entries()) {
      const a = t * 0.28 + i * 1.25;
      const r = 18 + i * 3;

      g.position.set(
        Math.cos(a) * r,
        10 + Math.sin(t * 1.5 + i) * 1.2,
        Math.sin(a) * r
      );
      g.rotation.y = -a + Math.PI / 2;

      const flap = Math.sin(t * 10 + i * 0.8) * 0.75;
      g.userData.l.rotation.z = flap;
      g.userData.r.rotation.z = -flap;
    }

    renderer.render(scene, camera);
  }

  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

  animate();
  </script>
</body>
</html>
```