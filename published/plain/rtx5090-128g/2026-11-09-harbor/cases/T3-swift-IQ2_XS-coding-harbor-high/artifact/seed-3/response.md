Below is a complete single-file HTML page. Save it as `ship-harbor.html` and open it in Chrome.

It builds an instant 3D voxel scene: a sailing ship bobbing near a dock, a harbor town, lighthouse, waves, clouds, birds, and a rotating lighthouse beam. Drag to orbit, scroll to zoom, right-drag to pan.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>3D Voxel Harbor — A Sailing Ship Calling at Harbor</title>
<style>
  html, body {
    margin: 0;
    height: 100%;
    overflow: hidden;
    background: #10171f;
    font-family: Arial, sans-serif;
  }
  #ui {
    position: absolute;
    left: 12px;
    top: 12px;
    padding: 10px 12px;
    background: rgba(255,255,255,0.85);
    border-radius: 10px;
    font-size: 13px;
    color: #112230;
    line-height: 1.35;
    box-shadow: 0 2px 8px rgba(0,0,0,0.25);
  }
</style>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
<div id="ui">
  <b>A sailing ship calling at a harbor</b><br>
  Drag: orbit · Scroll: zoom · Right-drag: pan
</div>

<script>
(function () {
  if (typeof THREE === "undefined") {
    document.body.innerHTML =
      '<div style="color:#fff;padding:20px;font-family:Arial;font-size:14px">' +
      'Three.js did not load. Check internet access and reload.</div>';
    return;
  }

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x77b4df);
  scene.fog = new THREE.Fog(0x77b4df, 150, 450);

  const camera = new THREE.PerspectiveCamera(
    58,
    window.innerWidth / window.innerHeight,
    0.5,
    1200
  );
  camera.position.set(105, 46, 112);

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.outputEncoding = THREE.sRGBEncoding;
  document.body.appendChild(renderer.domElement);

  const controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.target.set(20, 12, 0);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.minDistance = 25;
  controls.maxDistance = 380;
  controls.maxPolarAngle = Math.PI / 2.03;

  const hemi = new THREE.HemisphereLight(0xb1e4ff, 0x2b3945, 0.9);
  scene.add(hemi);

  const sun = new THREE.DirectionalLight(0xfff0d8, 1.15);
  sun.position.set(125, 155, -85);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  sun.shadow.camera.near = 20;
  sun.shadow.camera.far = 500;
  sun.shadow.camera.left = -160;
  sun.shadow.camera.right = 160;
  sun.shadow.camera.top = 160;
  sun.shadow.camera.bottom = -160;
  scene.add(sun);

  scene.add(new THREE.AmbientLight(0xffffff, 0.14));

  const sunSphere = new THREE.Mesh(
    new THREE.SphereGeometry(11, 18, 18),
    new THREE.MeshBasicMaterial({ color: 0xffefb5 })
  );
  sunSphere.position.set(150, 175, -125);
  scene.add(sunSphere);

  const sunGlow = new THREE.Mesh(
    new THREE.SphereGeometry(18, 18, 18),
    new THREE.MeshBasicMaterial({
      color: 0xffe6a1,
      transparent: true,
      opacity: 0.36,
      blending: THREE.AdditiveBlending
    })
  );
  sunGlow.position.copy(sunSphere.position);
  scene.add(sunGlow);

  const lists = {
    ship: [],
    harbor: [],
    water: [],
    sails: [],
    flag: [],
    clouds: [],
    beams: [],
    birds: []
  };

  function add(list, x, y, z, color, extra) {
    const obj = { x, y, z, color, sx: 1, sy: 1, sz: 1 };
    if (extra) Object.assign(obj, extra);
    list.push(obj);
  }

  function jitter(color, lum = 0.04, sat = 0.02) {
    const c = new THREE.Color(color);
    c.offsetHSL(
      (Math.random() - 0.5) * sat,
      (Math.random() - 0.5) * sat,
      (Math.random() - 0.5) * lum
    );
    return c.getHex();
  }

  const voxelGeo = new THREE.BoxGeometry(1, 1, 1);

  function createInstanced(list, material, parent, dynamic = false, cast = true, receive = true) {
    if (!list.length) return null;

    const mesh = new THREE.InstancedMesh(voxelGeo, material, list.length);
    const dummy = new THREE.Object3D();
    const col = new THREE.Color();

    for (let i = 0; i < list.length; i++) {
      const v = list[i];
      dummy.position.set(v.x, v.y, v.z);
      dummy.scale.set(v.sx, v.sy, v.sz);
      dummy.rotation.set(0, 0, 0);
      dummy.updateMatrix();
      mesh.setMatrixAt(i, dummy.matrix);

      col.set(v.color);
      mesh.setColorAt(i, col);
    }

    mesh.instanceMatrix.needsUpdate = true;
    if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
    if (dynamic) mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);

    mesh.castShadow = cast;
    mesh.receiveShadow = receive;
    mesh.frustumCulled = false;

    parent.add(mesh);
    mesh.userData.list = list;
    mesh.userData.dummy = dummy;

    return mesh;
  }

  /* =========================================================
     SHIP
     ========================================================= */

  const shipGroup = new THREE.Group();
  scene.add(shipGroup);
  shipGroup.position.set(18, 0.16, 0);

  const woodDark = 0x6d4c41;
  const woodLight = 0x8d6e63;
  const sailColor = 0xf6f8fa;
  const rope = 0x3e2723;
  const gold = 0xffd54f;
  const flagColor = 0xc62828;

  function shipZLimit(x) {
    if (x > 10) return Math.max(0, Math.floor(15 - x));
    if (x < -15) return Math.max(0, Math.floor(x + 18));
    return 5;
  }

  // Hull
  for (let x = -18; x <= 14; x++) {
    const zL = shipZLimit(x);
    if (zL < 1) continue;

    for (let z = -zL; z <= zL; z++) {
      const hullColor = jitter(woodDark, 0.04, 0.02);

      for (let y = 0; y <= 2; y++) add(lists.ship, x, y, z, hullColor);

      if (z > -zL && z < zL) add(lists.ship, x, 3, z, jitter(woodLight, 0.04, 0.02));
      if (z === zL) add(lists.ship, x, 3, z, jitter(woodLight, 0.04, 0.02));
      if (z === -zL) add(lists.ship, x, 3, z, jitter(woodLight, 0.04, 0.02));
    }
  }

  // Rudder
  for (let y = 0; y <= 2; y++) add(lists.ship, -18, y, 0, woodDark);
  add(lists.ship, -17, 3, 0, woodLight);

  // Bowsprit
  for (let i = 1; i <= 10; i++) {
    add(lists.ship, 14 + i, 4 + Math.floor(i * 0.4), 0, jitter(woodDark, 0.03, 0.02));
  }

  // Figurehead
  add(lists.ship, 14, 4, 0, gold);
  add(lists.ship, 15, 5, 0, gold);

  // Cannons
  for (let x = -14; x <= 10; x++) {
    const zL = shipZLimit(x);
    if (zL >= 1) {
      add(lists.ship, x, 3, zL, 0x616161);
      add(lists.ship, x, 3, -zL, 0x616161);
    }
  }

  // Aft cabin
  for (let x = -12; x <= -8; x++) {
    for (let z = -3; z <= 3; z++) {
      for (let y = 4; y <= 5; y++) {
        add(lists.ship, x, y, z, jitter(woodLight, 0.04, 0.02));
      }
    }
  }

  // Cabin windows
  for (let z = -2; z <= 2; z++) add(lists.ship, -8, 4, z, 0x263238);

  // Stern windows
  for (let z = -2; z <= 2; z++) add(lists.ship, -18, 3, z, gold);
  for (let z = -2; z <= 2; z++) add(lists.ship, -18, 4, z, jitter(woodLight, 0.03, 0.02));
  add(lists.ship, -18, 4, 0, gold);

  // Small rowboat on deck
  for (let x = 1; x <= 5; x++) add(lists.ship, x, 4, 5, jitter(woodDark, 0.03, 0.02));
  add(lists.ship, 3, 4, 5, woodLight);

  // Masts
  function addMast(x, top) {
    for (let y = 4; y <= top; y++) {
      add(lists.ship, x, y, 0, jitter(woodDark, 0.03, 0.02));
    }
  }

  addMast(-3, 18);
  addMast(9, 16);
  addMast(-11, 12);

  // Yards
  function addYard(x, y, zL) {
    for (let z = -zL; z <= zL; z++) {
      add(lists.ship, x, y, z, jitter(woodDark, 0.02, 0.01));
    }
  }

  addYard(-3, 6, 5);
  addYard(-3, 12, 5);
  addYard(-3, 18, 5);

  addYard(9, 6, 4);
  addYard(9, 12, 4);
  addYard(9, 16, 4);

  addYard(-11, 6, 3);
  addYard(-11, 12, 3);

  // Shrouds
  function addShrouds(x, top, zL) {
    for (const z of [zL, -zL, 0]) {
      for (let y = 4; y <= top; y++) {
        add(lists.ship, x, y, z, jitter(rope, 0.02, 0.01));
      }
    }
  }

  addShrouds(-3, 18, 5);
  addShrouds(9, 16, 4);
  addShrouds(-11, 12, 3);

  // Animated sails
  function addSail(x, y0, y1, zL, zAmp) {
    for (let y = y0; y <= y1; y++) {
      for (let z = -zL; z <= zL; z++) {
        for (let sx = x - 1; sx <= x + 1; sx++) {
          add(lists.sails, sx, y, z, sailColor, {
            x0: sx,
            y0: y,
            z0: z,
            phase: sx * 0.15 + y * 0.25 + z * 0.35,
            zAmp: zAmp + Math.abs(z) * 0.07,
            xAmp: 0.28,
            sign: z === 0 ? 1 : Math.sign(z)
          });
        }
      }
    }
  }

  addSail(-3, 4, 12, 5, 1.0);
  addSail(-3, 13, 17, 5, 1.0);

  addSail(9, 4, 12, 4, 1.0);
  addSail(9, 13, 16, 4, 1.0);

  addSail(-11, 4, 12, 3, 0.7);
  addSail(-11, 13, 12, 3, 0.7);

  // Jib
  function addJib() {
    for (let x = 14; x <= 24; x++) {
      const dx = x - 14;
      const y = 4 + Math.floor(dx * 0.4);
      const zMax = Math.floor(dx * 0.25);

      for (let z = -zMax; z <= zMax; z++) {
        add(lists.sails, x, y, z, sailColor, {
          x0: x,
          y0: y,
          z0: z,
          phase: x * 0.12 + z * 0.3,
          zAmp: 0.5 + Math.abs(z) * 0.08,
          xAmp: 0.25,
          sign: z === 0 ? 1 : Math.sign(z)
        });
      }
    }
  }

  addJib();

  // Flag
  for (let z = -4; z <= 4; z++) {
    for (let y = 12; y <= 14; y++) {
      add(lists.flag, -11, y, z, flagColor, {
        x0: -11,
        y0: y,
        z0: z,
        phase: z * 0.4 + y * 0.15
      });
    }
  }

  add(lists.ship, -11, 12, 0, rope);

  /* =========================================================
     HARBOR
     ========================================================= */

  // Ocean
  const oceanPalette = [0x1565c0, 0x1976d2, 0x2196f3, 0x0d47a1, 0x30a2c5];

  for (let x = -100; x <= 100; x++) {
    for (let z = -80; z <= 80; z++) {
      const colorIndex = Math.abs((x + z) % oceanPalette.length);
      add(lists.water, x, -0.1, z, jitter(oceanPalette[colorIndex], 0.05, 0.04), {
        x0: x,
        z0: z
      });
    }
  }

  // Land
  for (let x = 35; x <= 80; x++) {
    for (let z = -45; z <= 45; z++) {
      add(lists.harbor, x, 0, z, 0x5c4033);
      add(lists.harbor, x, 1, z, jitter(0x8d6e63, 0.03, 0.02));

      const topColor = ((x + z) & 1) ? 0x8bc34a : 0xe0c289;
      add(lists.harbor, x, 2, z, jitter(topColor, 0.04, 0.02));
    }
  }

  // Dock
  for (let x = 25; x <= 34; x++) {
    for (let z = 8; z <= 12; z++) {
      add(lists.harbor, x, 1, z, jitter(0x6d4c41, 0.03, 0.02));
      add(lists.harbor, x, 0, z, 0x4e342e);
    }
  }

  for (let x = 25; x <= 34; x += 2) {
    for (let z = 8; z <= 12; z += 2) {
      add(lists.harbor, x, 0, z, 0x3e2723);
    }
  }

  for (const x of [25, 34]) {
    for (const z of [8, 12]) {
      add(lists.harbor, x, 2, z, 0x6d4c41);
      add(lists.harbor, x, 3, z, 0x6d4c41);
    }
  }

  add(lists.harbor, 35, 1, 10, 0x6d4c41);

  function addCrate(cx, y, cz) {
    for (let x = cx; x <= cx + 1; x++) {
      for (let z = cz; z <= cz + 1; z++) {
        for (let yy = y; yy <= y + 1; yy++) {
          add(lists.harbor, x, yy, z, jitter(0x8d6e63, 0.05, 0.02));
        }
      }
    }
  }

  function addBarrel(x, y, z) {
    add(lists.harbor, x, y, z, 0x6d4c41);
    add(lists.harbor, x, y + 1, z, 0x79554f);
    add(lists.harbor, x, y + 2, z, 0x6d4c41);
  }

  addCrate(28, 2, 10);
  addCrate(31, 2, 11);
  addBarrel(29, 2, 9);
  addBarrel(32, 2, 9);
  addCrate(37, 3, -10);
  addCrate(43, 3, 20);

  // Breakwater
  for (let x = 20; x <= 70; x++) {
    for (let z = 30; z <= 40; z++) {
      for (let y = 1; y <= 3; y++) {
        add(lists.harbor, x, y, z, jitter(0x607d8b, 0.03, 0.01));
      }
    }
  }

  // Lighthouse
  const beamCenter = { x: 70, y: 20, z: 35 };

  for (let y = 1; y <= 18; y++) {
    const r = y <= 12 ? 3 : 2;
    const color = (y % 4 === 0) ? 0xd32f2f : 0xe0e0e0;

    for (let dx = -r; dx <= r; dx++) {
      for (let dz = -r; dz <= r; dz++) {
        if (dx * dx + dz * dz <= r * r) {
          add(lists.harbor, beamCenter.x + dx, y, beamCenter.z + dz, jitter(color, 0.03, 0.01));
        }
      }
    }
  }

  for (let y = 19; y <= 20; y++) {
    for (let dx = -2; dx <= 2; dx++) {
      for (let dz = -2; dz <= 2; dz++) {
        if (dx * dx + dz * dz <= 4) {
          add(lists.harbor, beamCenter.x + dx, y, beamCenter.z + dz, 0x263238);
        }
      }
    }
  }

  add(lists.harbor, beamCenter.x, beamCenter.y, beamCenter.z, 0xffef5f);

  for (let i = 1; i <= 16; i++) {
    add(lists.beams, beamCenter.x, beamCenter.y, beamCenter.z, 0xffe082, {
      dist: i,
      center: beamCenter
    });
  }

  // Houses
  const wallPalette = [0xb0bec5, 0xcfd8dc, 0x90a4ae, 0xa1887f, 0x78909c, 0x8d6e63];
  const roofPalette = [0x79554f, 0x6d4c41, 0x5d4037, 0x8d6e63];

  function addHouse(x, z, w, d, h) {
    const wi = Math.abs((x + z) % wallPalette.length);
    const ri = Math.abs((x + z) % roofPalette.length);

    const wallColor = wallPalette[wi];
    const roofColor = roofPalette[ri];

    for (let i = 0; i <= w; i++) {
      for (let j = 0; j <= d; j++) {
        for (let y = 3; y <= 3 + h; y++) {
          add(lists.harbor, x + i, y, z + j, jitter(wallColor, 0.04, 0.03));
        }
      }
    }

    const ry = 3 + h + 1;
    for (let i = 0; i <= w; i++) {
      for (let j = 0; j <= d; j++) {
        add(lists.harbor, x + i, ry, z + j, jitter(roofColor, 0.04, 0.02));
      }
    }

    for (let i = 0; i <= w; i++) {
      add(lists.harbor, x + i, ry + 1, z + Math.floor(d / 2), jitter(roofColor, 0.03, 0.01));
    }

    for (let y = 4; y <= 3 + h; y++) {
      add(lists.harbor, x, y, z, 0x263238);
      add(lists.harbor, x + w, y, z + d, 0x263238);
    }

    add(lists.harbor, x + Math.floor(w / 2), 3, z + d, 0x3e2723);
  }

  for (let i = 0; i < 12; i++) {
    for (let j = 0; j < 8; j++) {
      const x = 42 + i * 3;
      const z = -28 + j * 5;
      addHouse(x, z, 2, 2, 2);
    }
  }

  addHouse(45, -10, 6, 4, 4);
  addHouse(52, 10, 5, 5, 4);

  // Trees
  function addTree(x, z) {
    for (let y = 2; y <= 5; y++) {
      add(lists.harbor, x, y, z, 0x4e342e);
    }

    for (let y = 5; y <= 7; y++) {
      const r = y <= 5 ? 2 : 1;

      for (let dx = -r; dx <= r; dx++) {
        for (let dz = -r; dz <= r; dz++) {
          if (dx * dx + dz * dz <= r * r) {
            add(lists.harbor, x + dx, y, z + dz, jitter(0x2e7d32, 0.04, 0.03));
          }
        }
      }
    }
  }

  const treePositions = [
    [38, -25],
    [38, 25],
    [40, -20],
    [65, -25],
    [70, -30],
    [78, 10],
    [40, 15],
    [65, 20],
    [48, 30],
    [55, -35]
  ];

  for (const t of treePositions) {
    addTree(t[0], t[1]);
  }

  // Clouds
  for (let k = 0; k < 12; k++) {
    const cx = -90 + Math.random() * 180;
    const cy = 30 + Math.random() * 22;
    const cz = -80 + Math.random() * 160;
    const speed = 2 + Math.random() * 3;

    for (let i = 0; i < 5; i++) {
      const dx = Math.floor(Math.random() * 6) - 3;
      const dy = Math.floor(Math.random() * 3) - 1;
      const dz = Math.floor(Math.random() * 6) - 3;

      const px = cx + dx;
      const py = cy + dy;
      const pz = cz + dz;

      add(lists.clouds, px, py, pz, 0xffffff, {
        x0: px,
        y0: py,
        z0: pz,
        speed
      });
    }

    for (let i = 0; i < 3; i++) {
      const px = cx;
      const py = cy - 1;
      const pz = cz;

      add(lists.clouds, px, py, pz, 0xffffff, {
        x0: px,
        y0: py,
        z0: pz,
        speed
      });
    }
  }

  // Birds
  for (let b = 0; b < 8; b++) {
    const cx = -20 + Math.random() * 80;
    const cy = 18 + Math.random() * 12;
    const cz = -30 + Math.random() * 60;
    const phase = Math.random() * 6.28;
    const speed = 4 + Math.random() * 2;

    for (let part = -1; part <= 1; part++) {
      const ox = part === 0 ? 0 : 1;
      const oz = part;

      add(lists.birds, cx + ox, cy, cz + oz, 0x37474f, {
        cx,
        cy,
        cz,
        ox,
        oz,
        phase,
        speed
      });
    }
  }

  /* =========================================================
     MATERIALS
     ========================================================= */

  const shipMaterial = new THREE.MeshLambertMaterial();
  const harborMaterial = new THREE.MeshLambertMaterial();
  const waterMaterial = new THREE.MeshLambertMaterial();
  const sailMaterial = new THREE.MeshLambertMaterial();
  const flagMaterial = new THREE.MeshLambertMaterial();

  const cloudMaterial = new THREE.MeshLambertMaterial({
    transparent: true,
    opacity: 0.85
  });

  const beamMaterial = new THREE.MeshBasicMaterial({
    transparent: true,
    opacity: 0.35,
    blending: THREE.AdditiveBlending,
    depthWrite: false
  });

  const birdMaterial = new THREE.MeshBasicMaterial({
    transparent: true,
    opacity: 0.85
  });

  /* =========================================================
     MESHES
     ========================================================= */

  const shipMesh = createInstanced(lists.ship, shipMaterial, shipGroup, true, true, true);
  const harborMesh = createInstanced(lists.harbor, harborMaterial, scene, false, true, true);

  const waterMesh = createInstanced(lists.water, waterMaterial, scene, true, false, true);
  const sailMesh = createInstanced(lists.sails, sailMaterial, shipGroup, true, true, false);
  const flagMesh = createInstanced(lists.flag, flagMaterial, shipGroup, true, true, false);

  const cloudMesh = createInstanced(lists.clouds, cloudMaterial, scene, true, false, false);
  const beamMesh = createInstanced(lists.beams, beamMaterial, scene, true, false, false);
  const birdMesh = createInstanced(lists.birds, birdMaterial, scene, true, false, false);

  /* =========================================================
     ANIMATION
     ========================================================= */

  function updateShip(t) {
    shipGroup.position.y = 0.16 + Math.sin(t * 1.0) * 0.22;
    shipGroup.rotation.z = Math.sin(t * 0.7) * 0.02;
    shipGroup.rotation.x = Math.sin(t * 1.0 + 0.7) * 0.013;
    shipGroup.rotation.y = Math.sin(t * 0.4) * 0.012;
  }

  function updateWater(t) {
    const mesh = waterMesh;
    const dummy = mesh.userData.dummy;

    for (let i = 0; i < lists.water.length; i++) {
      const v = lists.water[i];

      const y = Math.sin(v.x0 * 0.22 + v.z0 * 0.17 + t * 1.6) * 0.45 - 0.25;

      dummy.position.set(v.x0, y, v.z0);
      dummy.scale.set(1, 1, 1);
      dummy.rotation.set(0, 0, 0);
      dummy.updateMatrix();

      mesh.setMatrixAt(i, dummy.matrix);
    }

    mesh.instanceMatrix.needsUpdate = true;
  }

  function updateSails(t) {
    const mesh = sailMesh;
    const dummy = mesh.userData.dummy;

    for (let i = 0; i < lists.sails.length; i++) {
      const v = lists.sails[i];

      const sway = Math.sin(t * 1.4 + v.phase + v.y0 * 0.18) * v.xAmp;
      const billow = Math.sin(t * 1.5 + v.phase + v.z0 * 0.25) * v.zAmp * v.sign;
      const y = v.y0 + Math.sin(t * 1.2 + v.phase) * 0.12;

      dummy.position.set(v.x0 + sway, y, v.z0 + billow);
      dummy.scale.set(1, 1, 1);
      dummy.rotation.set(0, 0, 0);
      dummy.updateMatrix();

      mesh.setMatrixAt(i, dummy.matrix);
    }

    mesh.instanceMatrix.needsUpdate = true;
  }

  function updateFlag(t) {
    const mesh = flagMesh;
    const dummy = mesh.userData.dummy;

    for (let i = 0; i < lists.flag.length; i++) {
      const v = lists.flag[i];

      const wave = Math.sin(t * 2.8 + v.phase + v.z0 * 0.4);
      const x = v.x0 + wave * 0.55;
      const y = v.y0 + Math.sin(t * 2.8 + v.phase) * 0.18;
      const z = v.z0 + wave * 0.62;

      dummy.position.set(x, y, z);
      dummy.scale.set(1, 1, 1);
      dummy.rotation.set(0, 0, 0);
      dummy.updateMatrix();

      mesh.setMatrixAt(i, dummy.matrix);
    }

    mesh.instanceMatrix.needsUpdate = true;
  }

  function updateClouds(t) {
    const mesh = cloudMesh;
    const dummy = mesh.userData.dummy;

    for (let i = 0; i < lists.clouds.length; i++) {
      const v = lists.clouds[i];

      const x = ((v.x0 + t * v.speed + 220) % 440) - 220;
      const y = v.y0 + Math.sin(t + v.z0 * 0.04) * 0.35;

      dummy.position.set(x, y, v.z0);
      dummy.scale.set(1, 1, 1);
      dummy.rotation.set(0, 0, 0);
      dummy.updateMatrix();

      mesh.setMatrixAt(i, dummy.matrix);
    }

    mesh.instanceMatrix.needsUpdate = true;
  }

  function updateBeam(t) {
    const mesh = beamMesh;
    const dummy = mesh.userData.dummy;

    const angle = t * 1.3;

    for (let i = 0; i < lists.beams.length; i++) {
      const v = lists.beams[i];

      const x = beamCenter.x + Math.cos(angle) * v.dist;
      const z = beamCenter.z + Math.sin(angle) * v.dist;
      const y = beamCenter.y + Math.sin(t * 2 + v.dist * 0.2) * 0.45;

      dummy.position.set(x, y, z);
      dummy.scale.set(1, 1, 1);
      dummy.rotation.set(0, 0, 0);
      dummy.updateMatrix();

      mesh.setMatrixAt(i, dummy.matrix);
    }

    mesh.instanceMatrix.needsUpdate = true;
  }

  function updateBirds(t) {
    const mesh = birdMesh;
    const dummy = mesh.userData.dummy;

    for (let i = 0; i < lists.birds.length; i++) {
      const v = lists.birds[i];

      const bx = v.cx + Math.sin(t * v.speed + v.phase) * 30;
      const bz = v.cz + Math.cos(t * v.speed * 0.7 + v.phase) * 40;
      const by = v.cy + Math.sin(t * 2.0 + v.phase) * 2.0;
      const wing = Math.sin(t * 10 + v.phase) * 1.3;

      dummy.position.set(
        bx + v.ox,
        by + (v.oz === 0 ? 0 : wing),
        bz + v.oz
      );

      dummy.scale.set(1, 1, 1);
      dummy.rotation.set(0, 0, 0);
      dummy.updateMatrix();

      mesh.setMatrixAt(i, dummy.matrix);
    }

    mesh.instanceMatrix.needsUpdate = true;
  }

  const clock = new THREE.Clock();

  function animate() {
    requestAnimationFrame(animate);

    const t = clock.getElapsedTime();

    updateShip(t);
    updateWater(t);
    updateSails(t);
    updateFlag(t);
    updateClouds(t);
    updateBeam(t);
    updateBirds(t);

    controls.update();

    renderer.render(scene, camera);
  }

  animate();

  window.addEventListener("resize", () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });
})();
</script>
</body>
</html>
```