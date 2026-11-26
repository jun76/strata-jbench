Paste the entire file below into a file named `sailing-harbor.html` and open it in Chrome.

It uses Three.js from a CDN, renders immediately, and is mouse-driven:

- **Left-drag**: rotate around the ship/harbor
- **Right-drag**: pan
- **Mouse wheel**: zoom
- **Double-click**: reset view

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Sailing Ship Calling at Harbor</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  html, body {
    height: 100%;
    margin: 0;
    overflow: hidden;
    background: #93c9e7;
    font-family: ui-monospace, Menlo, Consolas, monospace;
  }
  canvas {
    display: block;
    width: 100%;
    height: 100%;
    touch-action: none;
  }
  #ui {
    position: fixed;
    top: 12px;
    left: 12px;
    color: #fff;
    background: rgba(12, 26, 38, 0.55);
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 10px;
    padding: 10px 12px;
    font-size: 12px;
    line-height: 1.35;
    pointer-events: none;
    user-select: none;
    max-width: 330px;
  }
  #ui b {
    color: #ffe894;
  }
</style>
</head>
<body>
<div id="ui">
  <b>Sailing Ship Calling at Harbor</b><br>
  Left-drag: rotate<br>
  Right-drag: pan<br>
  Wheel: zoom<br>
  Double-click: reset view
</div>

<script src="https://cdn.jsdelivr.net/npm/three@0.150.1/build/three.min.js"></script>
<script>
(() => {
  if (typeof THREE === "undefined") {
    document.getElementById("ui").innerHTML =
      "<b>Failed to load Three.js.</b><br>Check your internet connection.";
    return;
  }

  const scene = new THREE.Scene();
  scene.background = new THREE.Color("#93d2f2");
  scene.fog = new THREE.Fog("#a6dbf0", 52, 165);

  const camera = new THREE.PerspectiveCamera(
    48,
    window.innerWidth / window.innerHeight,
    0.1,
    500
  );

  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ antialias: true });
  } catch (e) {
    document.getElementById("ui").innerHTML =
      "<b>WebGL failed.</b><br>Chrome needs hardware acceleration enabled.";
    return;
  }

  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(window.innerWidth, window.innerHeight);
  document.body.appendChild(renderer.domElement);

  const dom = renderer.domElement;
  dom.style.touchAction = "none";

  scene.add(new THREE.HemisphereLight("#ffffff", "#4a7b8f", 0.95));

  const sunLight = new THREE.DirectionalLight("#fff4d0", 0.85);
  sunLight.position.set(60, 45, -15);
  scene.add(sunLight);

  const C = {
    water: "#3a82a8",
    waterLight: "#56a7c8",
    waterDark: "#276582",

    hull: "#472413",
    hullLight: "#6d3a20",
    trim: "#9a6a34",
    deck: "#a67647",
    deckDark: "#7e5330",

    wood: "#8a5a32",
    woodDark: "#5a3820",
    mast: "#6b4427",
    mastDark: "#492d18",

    sail: "#f4efe3",
    sailShade: "#d8d1bf",
    rope: "#b29a72",

    flagRed: "#c23b2e",
    flagBlue: "#2b5fb6",

    stone: "#9a9a8e",
    stoneDark: "#72726a",
    grass: "#60a350",
    grassDark: "#4c8040",
    sand: "#d4bd8e",

    brick: "#9c6849",
    roof: "#b4433a",
    roofDark: "#822f29",

    metal: "#303030",
    lamp: "#ffe88a",

    crate: "#a97a45",
    crateDark: "#764f2a",
    barrel: "#8a5b34",
    barrelDark: "#5a3a1f",
    lid: "#cfa867",

    cannon: "#232323",
    white: "#f6fbff",
    birdDark: "#343b41",
    sun: "#fff2b0"
  };

  const voxGeo = new THREE.BoxGeometry(1, 1, 1);
  const voxMat = new THREE.MeshLambertMaterial();

  const staticVoxels = [];
  const tempObj = new THREE.Object3D();
  const tempColor = new THREE.Color();

  function addVoxel(x, y, z, color) {
    staticVoxels.push([x, y, z, color]);
  }

  function addWorldLine(x0, y0, z0, x1, y1, z1, color) {
    const dx = x1 - x0;
    const dy = y1 - y0;
    const dz = z1 - z0;
    const steps = Math.max(1, Math.ceil(Math.sqrt(dx * dx + dy * dy + dz * dz)));

    for (let i = 0; i <= steps; i++) {
      const t = i / steps;
      addVoxel(
        Math.round(x0 + dx * t),
        Math.round(y0 + dy * t),
        Math.round(z0 + dz * t),
        color
      );
    }
  }

  function makeInstancedMesh(list, material) {
    if (list.length === 0) return null;

    const mesh = new THREE.InstancedMesh(voxGeo, material, list.length);

    for (let i = 0; i < list.length; i++) {
      const v = list[i];

      tempObj.position.set(v[0], v[1], v[2]);
      tempObj.rotation.set(0, 0, 0);
      tempObj.scale.set(1, 1, 1);
      tempObj.updateMatrix();
      mesh.setMatrixAt(i, tempObj.matrix);

      tempColor.setStyle(v[3]);
      mesh.setColorAt(i, tempColor);
    }

    mesh.instanceMatrix.needsUpdate = true;
    if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;

    return mesh;
  }

  function addStaticMesh(list) {
    const mesh = makeInstancedMesh(list, voxMat);
    if (mesh) scene.add(mesh);
    return mesh;
  }

  function addCrate(x, y, z) {
    for (let dx = 0; dx < 2; dx++) {
      for (let dy = 0; dy < 2; dy++) {
        for (let dz = 0; dz < 2; dz++) {
          const c = ((dx + dy + dz) % 2 === 0) ? C.crate : C.crateDark;
          addVoxel(x + dx, y + dy, z + dz, c);
        }
      }
    }
  }

  function addBarrel(x, y, z) {
    for (let dy = 0; dy < 2; dy++) {
      addVoxel(x, y + dy, z, C.barrel);
      addVoxel(x + 1, y + dy, z, C.barrelDark);
      addVoxel(x, y + dy, z + 1, C.barrelDark);
      addVoxel(x + 1, y + dy, z + 1, C.barrel);
    }
    addVoxel(x, y + 2, z, C.lid);
    addVoxel(x + 1, y + 2, z + 1, C.lid);
  }

  function addLamp(x, z) {
    for (let y = 2; y <= 4; y++) {
      addVoxel(x, y, z, C.metal);
    }
    addVoxel(x, 5, z, C.lamp);
    addVoxel(x, 6, z, C.woodDark);
  }

  function addFlagpole(x, z) {
    for (let y = 2; y <= 6; y++) {
      addVoxel(x, y, z, C.woodDark);
    }

    addVoxel(x + 1, 6, z, C.flagBlue);
    addVoxel(x + 2, 6, z, C.white);
    addVoxel(x + 3, 6, z, C.flagRed);
    addVoxel(x + 1, 5, z, C.flagBlue);
    addVoxel(x + 2, 5, z, C.white);
    addVoxel(x + 3, 5, z, C.flagRed);
  }

  function addWarehouse() {
    for (let x = 15; x <= 21; x++) {
      for (let z = 20; z <= 24; z++) {
        for (let y = 2; y <= 5; y++) {
          if (x === 15 || x === 21 || z === 20 || z === 24) {
            const c = (y === 2) ? C.stoneDark : C.brick;
            addVoxel(x, y, z, c);
          }
        }
      }
    }

    for (let x = 14; x <= 22; x++) {
      for (let z = 19; z <= 25; z++) {
        addVoxel(x, 6, z, C.roof);
      }
    }

    for (let x = 15; x <= 21; x++) {
      for (let z = 20; z <= 24; z++) {
        addVoxel(x, 7, z, C.roofDark);
      }
    }

    addVoxel(17, 4, 20, C.lamp);
    addVoxel(19, 4, 20, C.lamp);

    addVoxel(18, 2, 20, C.woodDark);
    addVoxel(18, 3, 20, C.woodDark);
  }

  function addLighthouse(cx = 26, cz = 24) {
    for (let y = 1; y <= 10; y++) {
      const r = (y <= 6) ? 2 : 1;

      for (let dx = -r; dx <= r; dx++) {
        for (let dz = -r; dz <= r; dz++) {
          if (dx * dx + dz * dz > r * r + 0.5) continue;

          let c;
          if (y === 1) {
            c = C.stoneDark;
          } else if (Math.floor(y / 2) % 2 === 0) {
            c = C.white;
          } else {
            c = C.flagRed;
          }

          addVoxel(cx + dx, y, cz + dz, c);
        }
      }
    }

    for (let dx = -2; dx <= 2; dx++) {
      for (let dz = -2; dz <= 2; dz++) {
        if (dx * dx + dz * dz <= 4) {
          addVoxel(cx + dx, 11, cz + dz, C.lamp);
        }
      }
    }

    for (let dx = -1; dx <= 1; dx++) {
      for (let dz = -1; dz <= 1; dz++) {
        addVoxel(cx + dx, 12, cz + dz, C.woodDark);
      }
    }

    addVoxel(cx, 13, cz, C.white);
  }

  function addHarbor() {
    // Shore and grassy quay.
    for (let x = -18; x <= 30; x++) {
      for (let z = 18; z <= 30; z++) {
        let c = C.grass;
        if (x > 16) c = C.sand;
        if (z > 23) c = C.grassDark;
        if (z === 18 || z === 19) c = C.stone;

        addVoxel(x, 1, z, c);
        addVoxel(x, 0, z, C.stoneDark);
      }
    }

    // Dock surface.
    for (let x = -4; x <= 12; x++) {
      for (let z = 13; z <= 17; z++) {
        let c = ((x + z) % 3 === 0) ? C.deckDark : C.deck;
        if (z === 13 || z === 17) c = C.woodDark;
        addVoxel(x, 1, z, c);
      }
    }

    // Dock supports.
    for (let x = -4; x <= 12; x += 4) {
      addVoxel(x, 0, 13, C.woodDark);
      addVoxel(x, 0, 17, C.woodDark);
    }

    // Bollards.
    for (const bx of [2, 7, 11]) {
      addVoxel(bx, 2, 14, C.woodDark);
      addVoxel(bx, 2, 16, C.woodDark);
    }

    // Cargo and street furniture.
    addCrate(0, 2, 14);
    addCrate(1, 2, 14);
    addCrate(5, 2, 16);
    addBarrel(7, 2, 14);
    addBarrel(10, 2, 16);
    addCrate(20, 2, 26);
    addBarrel(22, 2, 26);

    addLamp(-2, 14);
    addLamp(-2, 16);
    addLamp(10, 18);
    addLamp(24, 22);

    addWarehouse();
    addLighthouse();
    addFlagpole(13, 26);
  }

  function hullRadius(x, y) {
    const a = Math.abs(x);
    const f = 1 - a / 11;
    if (f < 0) return 0;

    if (y === 0) return Math.max(0, Math.round(4.5 * f));
    if (y === 1) return Math.max(1, Math.round(4.8 * f));
    if (y === 2) return Math.max(1, Math.round(4.9 * f));
    if (y === 3) return Math.max(1, Math.round(4.2 * f));
    if (y === 4) return Math.max(1, Math.round(3.6 * f));
    return 0;
  }

  function addShip() {
    const ox = -1;
    const oz = 2;

    function v(lx, ly, lz, color) {
      addVoxel(ox + lx, ly, oz + lz, color);
    }

    function mast(x, h) {
      for (let y = 5; y <= h; y++) {
        v(x, y, 0, C.mast);
      }
      v(x, h + 1, 0, C.mastDark);
    }

    function yard(x, y, r) {
      for (let z = -r; z <= r; z++) {
        v(x, y, z, C.mastDark);
      }
    }

    function sail(mastX, y0, y1, zMax, billow) {
      const midY = (y0 + y1) / 2;
      const half = Math.max(1, (y1 - y0) / 2);

      for (let y = y0; y <= y1; y++) {
        const m = 1 - Math.abs(y - midY) / half;
        const width = Math.max(1, Math.round(zMax * (0.8 + 0.25 * m)));
        const x = mastX + Math.round(billow * m);

        for (let z = -width; z <= width; z++) {
          const c = (z % 2 === 0) ? C.sail : C.sailShade;
          v(x, y, z, c);
        }
      }
    }

    function line(lx0, ly0, lz0, lx1, ly1, lz1, color) {
      const dx = lx1 - lx0;
      const dy = ly1 - ly0;
      const dz = lz1 - lz0;
      const steps = Math.max(1, Math.ceil(Math.sqrt(dx * dx + dy * dy + dz * dz)));

      for (let i = 0; i <= steps; i++) {
        const t = i / steps;
        v(
          Math.round(lx0 + dx * t),
          Math.round(ly0 + dy * t),
          Math.round(lz0 + dz * t),
          color
        );
      }
    }

    // Hull.
    for (let x = -11; x <= 11; x++) {
      for (let y = 0; y <= 4; y++) {
        const r = hullRadius(x, y);

        for (let z = -r; z <= r; z++) {
          let c;

          if (y === 4) {
            if (Math.abs(z) === r) {
              c = C.trim;
            } else {
              c = (z % 2 === 0) ? C.deck : C.deckDark;
            }
          } else {
            c = C.hull;

            if (y === 2 && Math.abs(z) === r) c = C.hullLight;

            if (
              y === 1 &&
              Math.abs(z) === r &&
              x >= -6 &&
              x <= 8 &&
              ((x + 6) % 3 === 0)
            ) {
              c = C.cannon;
            }
          }

          v(x, y, z, c);
        }
      }
    }

    // Sterncastle.
    for (let x = 4; x <= 9; x++) {
      for (let z = -2; z <= 2; z++) {
        v(x, 5, z, (z % 2 === 0) ? C.deck : C.deckDark);
      }
    }

    for (let z = -2; z <= 2; z++) {
      v(4, 5, z, C.deckDark);
      v(9, 5, z, C.deckDark);
    }

    for (let x = 4; x <= 9; x++) {
      v(x, 4, -2, C.woodDark);
      v(x, 4, 2, C.woodDark);
      v(x, 5, -2, C.woodDark);
      v(x, 5, 2, C.woodDark);
    }

    for (let x = 3; x <= 10; x++) {
      for (let z = -3; z <= 3; z++) {
        v(x, 6, z, C.roofDark);
      }
    }

    // Forecastle.
    for (let x = -10; x <= -6; x++) {
      for (let z = -2; z <= 2; z++) {
        v(x, 5, z, C.deck);
      }
    }

    for (let x = -11; x <= -5; x++) {
      for (let z = -3; z <= 3; z++) {
        v(x, 6, z, C.roofDark);
      }
    }

    // Masts, yards, sails.
    mast(-5, 15);
    mast(3, 18);
    mast(9, 13);

    yard(-5, 12, 4);
    sail(-5, 8, 11, 4, 1);

    yard(3, 14, 5);
    sail(3, 9, 13, 5, 2);

    yard(9, 10, 3);
    sail(9, 7, 9, 3, 1);

    // Bowsprit.
    for (let x = 12; x <= 15; x++) {
      v(x, 4, 0, C.mast);
    }

    // Rigging.
    line(15, 4, 0, -5, 15, 0, C.rope);
    line(-5, 15, 0, 11, 4, 0, C.rope);
    line(3, 18, 0, 11, 5, 0, C.rope);
    line(3, 18, 0, -11, 5, 0, C.rope);
    line(9, 13, 0, 11, 5, 0, C.rope);
    line(9, 13, 0, -10, 5, 0, C.rope);

    // Flags.
    for (let y = 17; y <= 18; y++) {
      for (let x = 4; x <= 6; x++) {
        v(x, y, 0, C.flagRed);
      }
    }

    for (let y = 4; y <= 6; y++) {
      v(-11, y, 0, C.flagBlue);
    }

    // Small deck cargo.
    v(-3, 5, 2, C.barrel);
    v(-2, 5, 2, C.barrel);
    v(-3, 5, -2, C.barrel);
    v(-2, 5, -2, C.barrel);

    // Mooring ropes to the harbor.
    addWorldLine(10, 4, 2, 7, 2, 14, C.rope);
    addWorldLine(-12, 3, 2, 1, 2, 16, C.rope);
  }

  function addSky() {
    addVoxel(56, 34, -18, C.sun);
    addVoxel(57, 34, -18, C.sun);
    addVoxel(56, 35, -18, C.sun);
    addVoxel(56, 34, -19, "#fff8d0");
  }

  let waterMesh;
  let waterData = [];

  function initWater() {
    waterData = [];

    for (let x = -36; x <= 36; x++) {
      for (let z = -36; z <= 17; z++) {
        waterData.push({ x, z });
      }
    }

    const material = new THREE.MeshLambertMaterial();
    waterMesh = new THREE.InstancedMesh(voxGeo, material, waterData.length);

    for (let i = 0; i < waterData.length; i++) {
      const d = waterData[i];
      const pick = ((d.x * 31 + d.z * 17) % 3 + 3) % 3;

      const c =
        pick === 0 ? C.waterLight :
        pick === 1 ? C.water :
        C.waterDark;

      tempColor.setStyle(c);
      waterMesh.setColorAt(i, tempColor);
    }

    if (waterMesh.instanceColor) waterMesh.instanceColor.needsUpdate = true;
    scene.add(waterMesh);
  }

  function updateWater(t) {
    if (!waterMesh) return;

    for (let i = 0; i < waterData.length; i++) {
      const d = waterData[i];

      const wave =
        Math.sin(d.x * 0.13 + d.z * 0.11 + t * 1.7) * 0.13 +
        Math.sin(d.x * 0.24 - d.z * 0.18 + t * 1.1) * 0.09;

      tempObj.position.set(d.x, -0.55 + wave, d.z);
      tempObj.rotation.set(0, 0, 0);
      tempObj.scale.set(1, 1, 1);
      tempObj.updateMatrix();
      waterMesh.setMatrixAt(i, tempObj.matrix);
    }

    waterMesh.instanceMatrix.needsUpdate = true;
  }

  const cloudData = [];
  let cloudMesh;

  function addCloudCluster(cx, cy, cz, n, seed) {
    for (let i = 0; i < n; i++) {
      cloudData.push({
        cx,
        cy,
        cz,
        dx: Math.floor(Math.random() * 9) - 4,
        dy: Math.floor(Math.random() * 3) - 1,
        dz: Math.floor(Math.random() * 7) - 3,
        sx: 3 + Math.random() * 2,
        sy: 1 + Math.random() * 0.5,
        sz: 2 + Math.random() * 2,
        speed: 0.04 + Math.random() * 0.04,
        seed
      });
    }
  }

  function initClouds() {
    addCloudCluster(-32, 28, -18, 16, 1);
    addCloudCluster(8, 31, -28, 16, 50);
    addCloudCluster(28, 27, -5, 14, 90);
    addCloudCluster(-22, 33, 10, 14, 130);

    const material = new THREE.MeshBasicMaterial({ color: "#f7fbff" });
    cloudMesh = new THREE.InstancedMesh(voxGeo, material, cloudData.length);
    scene.add(cloudMesh);
  }

  function updateClouds(t) {
    if (!cloudMesh) return;

    for (let i = 0; i < cloudData.length; i++) {
      const d = cloudData[i];

      const drift = (t * d.speed + d.seed) % 130;
      const x = d.cx - 60 + drift + d.dx;
      const y = d.cy + d.dy;
      const z = d.cz + d.dz;

      tempObj.position.set(x, y, z);
      tempObj.rotation.set(0, 0, 0);
      tempObj.scale.set(d.sx, d.sy, d.sz);
      tempObj.updateMatrix();
      cloudMesh.setMatrixAt(i, tempObj.matrix);
    }

    cloudMesh.instanceMatrix.needsUpdate = true;
  }

  const birdData = [];
  let birdMesh;

  function initBirds() {
    const material = new THREE.MeshLambertMaterial();
    const count = 8;

    birdMesh = new THREE.InstancedMesh(voxGeo, material, count);

    for (let i = 0; i < count; i++) {
      birdData.push({
        cx: -1,
        cz: 2,
        r: 8 + i * 1.4,
        y: 11 + i * 1.1,
        speed: 0.25 + i * 0.03,
        phase: i * 0.7
      });

      tempColor.setStyle((i % 2 === 0) ? C.white : C.birdDark);
      birdMesh.setColorAt(i, tempColor);
    }

    if (birdMesh.instanceColor) birdMesh.instanceColor.needsUpdate = true;
    scene.add(birdMesh);
  }

  function updateBirds(t) {
    if (!birdMesh) return;

    for (let i = 0; i < birdData.length; i++) {
      const d = birdData[i];

      const angle = d.phase + t * d.speed;
      const x = d.cx + Math.cos(angle) * d.r;
      const z = d.cz + Math.sin(angle) * d.r;
      const y = d.y + Math.sin(t * 2 + d.phase) * 0.7;

      tempObj.position.set(x, y, z);
      tempObj.rotation.set(0, -angle, 0);
      tempObj.scale.set(1.8, 0.6, 2.8);
      tempObj.updateMatrix();
      birdMesh.setMatrixAt(i, tempObj.matrix);
    }

    birdMesh.instanceMatrix.needsUpdate = true;
  }

  // Camera orbit state.
  const target = new THREE.Vector3(-1, 7, 3);
  let radius = 52;
  let theta = -0.85;
  let phi = 1.15;

  function updateCamera() {
    camera.position.set(
      target.x + radius * Math.sin(phi) * Math.sin(theta),
      target.y + radius * Math.cos(phi),
      target.z + radius * Math.sin(phi) * Math.cos(theta)
    );
    camera.lookAt(target);
  }

  const rightVec = new THREE.Vector3();
  const upVec = new THREE.Vector3();

  let dragMode = 0;
  let lastX = 0;
  let lastY = 0;

  dom.addEventListener("contextmenu", (e) => e.preventDefault());

  dom.addEventListener("pointerdown", (e) => {
    e.preventDefault();

    if (e.button === 0) dragMode = 1;
    else if (e.button === 2) dragMode = 2;
    else dragMode = 0;

    lastX = e.clientX;
    lastY = e.clientY;

    try {
      dom.setPointerCapture(e.pointerId);
    } catch (_) {}
  });

  dom.addEventListener("pointermove", (e) => {
    if (dragMode === 0) return;

    const dx = e.clientX - lastX;
    const dy = e.clientY - lastY;
    lastX = e.clientX;
    lastY = e.clientY;

    if (dragMode === 1) {
      theta -= dx * 0.0045;
      phi -= dy * 0.0045;
      phi = Math.max(0.18, Math.min(Math.PI - 0.18, phi));
    } else if (dragMode === 2) {
      rightVec.setFromMatrixColumn(camera.matrixWorld, 0);
      upVec.setFromMatrixColumn(camera.matrixWorld, 1);

      const s = radius * 0.0025;
      target.addScaledVector(rightVec, -dx * s);
      target.addScaledVector(upVec, dy * s);
    }
  });

  dom.addEventListener("pointerup", (e) => {
    dragMode = 0;
    try {
      dom.releasePointerCapture(e.pointerId);
    } catch (_) {}
  });

  window.addEventListener("pointerup", () => {
    dragMode = 0;
  });

  window.addEventListener("wheel", (e) => {
    e.preventDefault();

    const factor = (e.deltaY > 0) ? 1.08 : 1 / 1.08;
    radius = Math.max(14, Math.min(130, radius * factor));
  }, { passive: false });

  dom.addEventListener("dblclick", () => {
    target.set(-1, 7, 3);
    radius = 52;
    theta = -0.85;
    phi = 1.15;
  });

  window.addEventListener("resize", () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

  // Build the scene.
  addSky();
  addHarbor();
  addShip();
  addStaticMesh(staticVoxels);

  initWater();
  initClouds();
  initBirds();

  function animate() {
    const t = performance.now() * 0.001;

    updateWater(t);
    updateClouds(t);
    updateBirds(t);
    updateCamera();

    renderer.render(scene, camera);
    requestAnimationFrame(animate);
  }

  animate();
})();
</script>
</body>
</html>
```