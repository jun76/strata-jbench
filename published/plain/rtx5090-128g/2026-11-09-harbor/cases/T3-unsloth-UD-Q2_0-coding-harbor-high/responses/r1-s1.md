Save this as a single `.html` file (for example `harbor-ship.html`) and open it in Chrome.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>Voxel Sailing Ship Harbor</title>
<style>
  html, body {
    margin: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
    background: #a6d8f5;
  }
  canvas {
    display: block;
    touch-action: none;
  }
  #help {
    position: absolute;
    top: 12px;
    left: 12px;
    padding: 8px 10px;
    color: #fff;
    background: rgba(0,0,0,.35);
    border-radius: 6px;
    font: 13px system-ui, sans-serif;
    pointer-events: none;
  }
</style>
</head>
<body>
<div id="help">Left-drag: orbit · Right-drag: pan · Scroll: zoom</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function () {
  if (!window.THREE) {
    document.body.innerHTML =
      '<div style="color:#fff;padding:20px;font-family:system-ui,sans-serif;background:#111;">' +
      'Failed to load Three.js. Check your internet connection and reload.' +
      '</div>';
    return;
  }

  const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));

  const staticVoxels = new Map();
  const shipVoxels = new Map();

  const waterColors = ['#1c6c9f', '#2480bd', '#155f90'];
  const waterColorSet = new Set(waterColors);

  function key(x, y, z) {
    return x + '|' + y + '|' + z;
  }

  function addStatic(x, y, z, color) {
    staticVoxels.set(key(x, y, z), color);
  }

  function addStaticBox(x0, x1, z0, z1, y0, y1, color) {
    for (let x = x0; x <= x1; x++) {
      for (let z = z0; z <= z1; z++) {
        for (let y = y0; y <= y1; y++) {
          addStatic(x, y, z, color);
        }
      }
    }
  }

  function addPitchedRoof(x0, x1, z0, z1, baseY, color) {
    let sx = x0, ex = x1, sz = z0, ez = z1, y = baseY;
    while (sx <= ex && sz <= ez) {
      addStaticBox(sx, ex, sz, ez, y, y, color);
      sx++; ex--; sz++; ez--; y++;
    }
  }

  function addBuilding(x0, x1, z0, z1, height, wallColor, roofColor, opts) {
    opts = opts || {};
    addStaticBox(x0, x1, z0, z1, 2, 1 + height, wallColor);

    const winColor = opts.windowColor || '#ffe082';
    const doorColor = opts.doorColor || '#5a3927';
    const frontZ = opts.front === 'back' ? z0 : z1;
    const backZ = opts.front === 'back' ? z1 : z0;

    if (height >= 3) {
      const wy = 4;
      for (let x = x0 + 1; x < x1; x += 2) {
        addStatic(x, wy, frontZ, winColor);
        addStatic(x, wy, backZ, winColor);
      }
    }

    const cx = Math.floor((x0 + x1) / 2);
    addStatic(cx, 2, frontZ, doorColor);
    if (height >= 3) addStatic(cx, 3, frontZ, doorColor);

    if (opts.type === 'flat') {
      addStaticBox(x0, x1, z0, z1, 2 + height, 2 + height, roofColor);
    } else {
      addPitchedRoof(x0, x1, z0, z1, 2 + height, roofColor);
    }
  }

  function addBarrel(x, z) {
    addStaticBox(x, x, z, z, 2, 3, '#8d6e63');
    addStatic(x, 4, z, '#5d4037');
  }

  function addCrate(x, z) {
    addStaticBox(x, x + 1, z, z + 1, 2, 3, '#b07e4e');
    addStatic(x, 4, z + 1, '#8d6436');
  }

  function addTree(x, z) {
    addStatic(x, 2, z, '#7a5336');
    addStatic(x, 3, z, '#7a5336');

    for (let dx = -2; dx <= 2; dx++) {
      for (let dz = -2; dz <= 2; dz++) {
        const r = Math.abs(dx) + Math.abs(dz);
        if (r > 3) continue;
        addStatic(x + dx, 4, z + dz, '#4d8b57');
        addStatic(x + dx, 5, z + dz, '#58a367');
        if (r <= 1) addStatic(x + dx, 6, z + dz, '#58a367');
      }
    }
  }

  function buildLighthouse() {
    // Low breakwater connecting from land into the harbor.
    addStaticBox(21, 34, 0, 1, 0, 1, '#9e9e9e');
    addStaticBox(33, 35, 2, 14, 0, 1, '#9e9e9e');
    addStaticBox(33, 35, 15, 17, 0, 1, '#9e9e9e');

    // Rocks around the breakwater.
    addStaticBox(21, 22, -1, 1, 0, 0, '#756555');
    addStaticBox(25, 26, -1, 1, 0, 0, '#857767');

    // Lighthouse base.
    addStaticBox(33, 37, 10, 14, 1, 2, '#e8e8e8');

    // Red/white tower.
    for (let y = 3; y <= 13; y++) {
      const c = (Math.floor((y - 3) / 2) % 2 === 0) ? '#f0f0f0' : '#d32f2f';
      addStaticBox(34, 36, 11, 13, y, y, c);
    }

    // Lamp room, light, cap.
    addStaticBox(33, 37, 10, 14, 14, 14, '#506070');
    addStaticBox(34, 36, 11, 13, 15, 15, '#ffe57f');
    addStaticBox(34, 36, 11, 13, 16, 16, '#2f3e46');
  }

  function buildHarbor() {
    const landX0 = -55, landX1 = 20;
    const landZ0 = -50, landZ1 = 0;

    // Sea.
    for (let x = -65; x <= 65; x++) {
      for (let z = -45; z <= 80; z++) {
        // Skip water where land is placed.
        if (x >= landX0 && x <= landX1 && z >= landZ0 && z <= landZ1) continue;
        const c = waterColors[Math.abs(x * 3 + z * 5) % 3];
        addStatic(x, 0, z, c);
      }
    }

    // Land / shore.
    for (let x = landX0; x <= landX1; x++) {
      for (let z = landZ0; z <= landZ1; z++) {
        let c;
        if (z >= -1) c = '#e8ce9a';
        else if (z >= -4) c = '#f0d2a0';
        else c = (Math.abs(x * 7 + z * 13) % 29 === 0) ? '#8b7652' : '#71b04b';
        addStatic(x, 1, z, c);
      }
    }

    // Main wooden pier.
    addStaticBox(-25, 20, 0, 7, 1, 1, '#a16831');
    for (let x = -25; x <= 20; x++) {
      for (let z = 0; z <= 7; z++) {
        if (((x + z) % 3) === 0) addStatic(x, 1, z, '#8c5627');
      }
    }

    // Pier supports.
    for (let x = -22; x <= 20; x += 6) {
      for (let z = 2; z <= 6; z += 3) {
        addStatic(x, 0, z, '#68441f');
      }
    }

    // Bollards.
    for (let x = -22; x <= 18; x += 6) {
      addStatic(x, 2, 7, '#746b5f');
      addStatic(x, 3, 7, '#8f8476');
    }

    // Warehouses and dock sheds.
    addBuilding(-15, -6, -10, -5, 4, '#b5651d', '#8f1f1f', { type: 'flat' });
    addBuilding(-3, 8, -9, -4, 3, '#c98f5a', '#274690', { type: 'pitched' });
    addBuilding(11, 18, -7, -3, 2, '#8a6254', '#544235', { type: 'flat' });

    // Cargo near the dock.
    for (let x = -20; x <= 18; x += 7) {
      addBarrel(x, -2);
      addCrate(x + 1, -1);
    }

    // Townhouses.
    const houses = [
      { x0: -50, x1: -44, z0: -35, z1: -29, h: 2, w: '#e57373', r: '#b71c1c' },
      { x0: -42, x1: -36, z0: -36, z1: -30, h: 3, w: '#64b5f6', r: '#0d47a1' },
      { x0: -34, x1: -28, z0: -34, z1: -28, h: 2, w: '#ffd54f', r: '#e65100' },
      { x0: -26, x1: -19, z0: -35, z1: -29, h: 2, w: '#81c784', r: '#1b5e20' },
      { x0: -50, x1: -45, z0: -18, z1: -12, h: 2, w: '#b39ddb', r: '#311b92' },
      { x0: -43, x1: -37, z0: -21, z1: -15, h: 3, w: '#f48fb1', r: '#880e4f' },
      { x0: -34, x1: -26, z0: -22, z1: -16, h: 2, w: '#90caf9', r: '#0d47a1' },
      { x0: -22, x1: -15, z0: -19, z1: -13, h: 3, w: '#a5d6a7', r: '#2e7d32' }
    ];

    for (const h of houses) {
      addBuilding(h.x0, h.x1, h.z0, h.z1, h.h, h.w, h.r);
    }

    // Trees.
    const treeSpots = [
      [-50, -48], [-47, -44], [-50, -40], [-44, -39], [-39, -42],
      [-35, -46], [-30, -43], [-25, -40], [-48, -24], [-44, -20],
      [-38, -26], [-33, -22], [-27, -18], [-21, -25], [-15, -42],
      [-10, -37], [-5, -33], [0, -42], [6, -36], [12, -32],
      [16, -40], [18, -46], [-12, -12], [-8, -16], [-4, -12],
      [8, -14], [14, -18]
    ];
    for (const t of treeSpots) addTree(t[0], t[1]);

    // Harbor flagpole.
    addStaticBox(19, 21, -5, -3, 1, 1, '#c29b65');
    addStaticBox(20, 20, -4, -4, 2, 10, '#7a5336');

    buildLighthouse();
  }

  function buildShip() {
    const colors = {
      hullDark: '#573a26',
      hullMed: '#8d5a2f',
      hullLight: '#a7713c',
      deck: '#c8a06f',
      rail: '#6d4b31',
      cabin: '#d9b48f',
      mast: '#7d5636',
      yard: '#5e412b',
      sail1: '#f4ecd8',
      sail2: '#e4d5b5',
      trim: '#3f2a1d'
    };

    function s(x, y, z, c) {
      shipVoxels.set(key(x, y, z), c);
    }

    function sBox(x0, x1, z0, z1, y0, y1, c) {
      for (let x = x0; x <= x1; x++) {
        for (let y = y0; y <= y1; y++) {
          for (let z = z0; z <= z1; z++) {
            s(x, y, z, c);
          }
        }
      }
    }

    function hullHalf(x) {
      if (x < -13 || x > 14) return 0;
      let h = 5;
      if (x <= -10) h = Math.max(1, 3 + (x + 11));
      if (x >= 11) h = Math.max(1, 5 - (x - 10));
      return h;
    }

    function rnd(x, y, z) {
      const n = Math.sin(x * 12.9898 + y * 78.233 + z * 37.719) * 43758.5453;
      return n - Math.floor(n);
    }

    function line(x0, y0, z0, x1, y1, z1, c) {
      const dx = x1 - x0, dy = y1 - y0, dz = z1 - z0;
      const n = Math.max(1, Math.max(Math.abs(dx), Math.abs(dy), Math.abs(dz)));
      for (let i = 0; i <= n; i++) {
        const t = i / n;
        s(
          Math.round(x0 + dx * t),
          Math.round(y0 + dy * t),
          Math.round(z0 + dz * t),
          c
        );
      }
    }

    // Hull.
    for (let x = -13; x <= 14; x++) {
      const h = hullHalf(x);
      if (h <= 0) continue;

      for (let y = 0; y <= 3; y++) {
        let b = h - (3 - y);
        if (b < 1) b = 1;
        for (let z = -b; z <= b; z++) {
          const c = (y < 2) ? colors.hullDark : (y === 2 ? colors.hullMed : colors.hullLight);
          s(x, y, z, c);
        }
      }

      // Deck.
      for (let z = -h; z <= h; z++) {
        s(x, 4, z, colors.deck);
      }

      // Rail.
      for (let z = -h; z <= h; z++) {
        if (z === -h || z === h || h === 1) {
          s(x, 5, z, colors.rail);
        }
      }
    }

    // Quarterdeck / stern castle.
    sBox(-12, -11, -2, 2, 5, 6, colors.cabin);
    s(-12, 6, 0, '#ffe082');
    s(-11, 6, 0, '#ffe082');

    // Forecastle.
    sBox(9, 12, -1, 1, 5, 6, colors.cabin);

    // Deck details.
    for (let x = -6; x <= 8; x += 4) {
      if (hullHalf(x) > 2) {
        s(x, 5, 2, '#8d6e63');
        s(x, 5, -2, '#b07e4e');
      }
    }

    // Cannon ports.
    for (let x = -8; x <= 6; x += 2) {
      if (hullHalf(x) > 3) {
        s(x, 4, 2, '#303030');
        s(x, 4, -2, '#303030');
      }
    }

    // Masts.
    const masts = [
      { x: -6, height: 18 },
      { x: 0, height: 24 },
      { x: 6, height: 21 }
    ];
    for (const m of masts) {
      for (let y = 6; y <= m.height; y++) {
        s(m.x, y, 0, colors.mast);
      }
    }

    // Square sails.
    const squareSails = [
      { x: -6, layers: [[10, 4], [14, 3], [17, 2]] },
      { x: 0, layers: [[13, 7], [18, 6], [23, 5]] },
      { x: 6, layers: [[11, 6], [16, 5], [20, 4]] }
    ];

    for (const set of squareSails) {
      for (const [yardY, h] of set.layers) {
        for (let z = -h; z <= h; z++) {
          s(set.x, yardY, z, colors.yard);
        }

        for (let y = yardY - 3; y <= yardY - 1; y++) {
          for (let z = -h + 1; z <= h - 1; z++) {
            if (rnd(set.x, y, z) > 0.14) {
              const c = ((y + z) % 5 === 0) ? colors.sail2 : colors.sail1;
              s(set.x, y, z, c);
            }
          }
        }
      }
    }

    // Bowsprit.
    line(14, 6, 0, 22, 10, 0, colors.mast);

    // Jib sail.
    for (let x = 8; x <= 20; x++) {
      const t = (x - 8) / 12;
      const yTop = Math.floor(18 - t * 8);
      for (let y = 10; y <= yTop; y++) {
        if (rnd(x, y, 0) > 0.18) {
          s(x, y, 0, colors.sail1);
        }
      }
    }
  }

  function buildInstancedMap(map, parent, cast, receive) {
    const byColor = new Map();

    map.forEach((color, k) => {
      const parts = k.split('|');
      const x = +parts[0], y = +parts[1], z = +parts[2];
      const arr = byColor.get(color);
      if (arr) arr.push([x, y, z]);
      else byColor.set(color, [[x, y, z]]);
    });

    const geo = new THREE.BoxGeometry(1, 1, 1);
    const dummy = new THREE.Object3D();

    byColor.forEach((points, color) => {
      if (points.length === 0) return;

      const mat = new THREE.MeshLambertMaterial({ color });
      const mesh = new THREE.InstancedMesh(geo, mat, points.length);

      const isWater = waterColorSet.has(color);
      mesh.castShadow = cast && !isWater;
      mesh.receiveShadow = receive;
      mesh.frustumCulled = false;

      for (let i = 0; i < points.length; i++) {
        const p = points[i];
        dummy.position.set(p[0], p[1], p[2]);
        dummy.rotation.set(0, 0, 0);
        dummy.scale.set(1, 1, 1);
        dummy.updateMatrix();
        mesh.setMatrixAt(i, dummy.matrix);
      }

      mesh.instanceMatrix.needsUpdate = true;
      parent.add(mesh);
    });
  }

  // Renderer
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  if (THREE.sRGBEncoding) renderer.outputEncoding = THREE.sRGBEncoding;
  document.body.appendChild(renderer.domElement);

  // Scene
  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#a6d8f5');
  scene.fog = new THREE.Fog('#cfeeff', 160, 340);

  // Camera
  const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 1000);

  // Lights
  const hemi = new THREE.HemisphereLight('#d4f3ff', '#2f5c7d', 0.75);
  scene.add(hemi);

  const sun = new THREE.DirectionalLight('#fff1c1', 1.0);
  sun.position.set(-40, 70, 40);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  sun.shadow.camera.near = 1;
  sun.shadow.camera.far = 260;
  sun.shadow.camera.left = -85;
  sun.shadow.camera.right = 85;
  sun.shadow.camera.top = 85;
  sun.shadow.camera.bottom = -85;
  sun.shadow.bias = -0.0012;
  sun.shadow.camera.updateProjectionMatrix();
  scene.add(sun);

  // Build scene voxels
  buildHarbor();
  buildShip();

  // Ship group for gentle floating animation.
  const ship = new THREE.Group();
  const shipBaseY = 0.15;
  const shipBaseYaw = -0.15;
  ship.position.set(0, shipBaseY, 14);
  ship.rotation.y = shipBaseYaw;
  scene.add(ship);

  buildInstancedMap(shipVoxels, ship, true, true);
  buildInstancedMap(staticVoxels, scene, true, true);

  // Animated flags
  const flags = [];

  function addFlag(parent, x, y, z, color, w = 3, h = 1.2) {
    const g = new THREE.Group();
    g.position.set(x, y, z);

    const geo = new THREE.BoxGeometry(w, h, 0.15);
    const mat = new THREE.MeshLambertMaterial({ color });
    const mesh = new THREE.Mesh(geo, mat);
    mesh.position.set(w * 0.5, -h * 0.5, 0);
    mesh.castShadow = false;
    mesh.receiveShadow = false;
    g.add(mesh);
    parent.add(g);

    flags.push({ obj: g, phase: Math.random() * 6.283 });
    return g;
  }

  addFlag(ship, 0, 24, 0, '#d32f2f', 4, 2);
  addFlag(ship, 6, 21, 0, '#ffca28', 3, 1.5);
  addFlag(ship, -6, 18, 0, '#1976d2', 3, 1.5);
  addFlag(scene, 20, 10, -4, '#ffcc00', 3, 1.6);

  // Simple mouse orbit controls.
  const orbit = {
    theta: -0.85,
    phi: 0.62,
    radius: 78,
    target: new THREE.Vector3(0, 4, 12),
    minPhi: 0.10,
    maxPhi: Math.PI / 2 - 0.08,
    minRadius: 18,
    maxRadius: 220
  };

  function updateOrbit() {
    const sinP = Math.sin(orbit.phi);
    const cosP = Math.cos(orbit.phi);
    camera.position.set(
      orbit.target.x + orbit.radius * sinP * Math.sin(orbit.theta),
      orbit.target.y + orbit.radius * cosP,
      orbit.target.z + orbit.radius * sinP * Math.cos(orbit.theta)
    );
    camera.lookAt(orbit.target);
  }

  let dragging = false;
  let dragButton = 0;
  let lastX = 0;
  let lastY = 0;

  const dom = renderer.domElement;
  dom.addEventListener('contextmenu', e => e.preventDefault());

  dom.addEventListener('pointerdown', e => {
    dragging = true;
    dragButton = e.button;
    lastX = e.clientX;
    lastY = e.clientY;
  });

  window.addEventListener('pointermove', e => {
    if (!dragging) return;

    const dx = e.clientX - lastX;
    const dy = e.clientY - lastY;
    lastX = e.clientX;
    lastY = e.clientY;

    if (dragButton === 0 || e.ctrlKey || e.metaKey) {
      if (dragButton === 2 && !(e.ctrlKey || e.metaKey)) {
        panCamera(dx, dy);
      } else {
        orbit.theta -= dx * 0.006;
        orbit.phi = clamp(orbit.phi - dy * 0.006, orbit.minPhi, orbit.maxPhi);
      }
    } else if (dragButton === 2) {
      panCamera(dx, dy);
    }
  });

  window.addEventListener('pointerup', () => {
    dragging = false;
  });

  dom.addEventListener('wheel', e => {
    e.preventDefault();
    orbit.radius = clamp(orbit.radius * Math.exp(e.deltaY * 0.0012), orbit.minRadius, orbit.maxRadius);
  }, { passive: false });

  function panCamera(dx, dy) {
    const dir = new THREE.Vector3();
    camera.getWorldDirection(dir);
    const right = new THREE.Vector3().crossVectors(dir, camera.up).normalize();
    const up = new THREE.Vector3().crossVectors(right, dir).normalize();

    const scale = orbit.radius * 0.0018;
    orbit.target.addScaledVector(right, dx * scale);
    orbit.target.addScaledVector(up, -dy * scale);
    orbit.target.y = Math.max(1, orbit.target.y);
  }

  // Resize
  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

  // Animation loop
  const clock = new THREE.Clock();

  function animate() {
    requestAnimationFrame(animate);

    const t = clock.getElapsedTime();

    ship.position.y = shipBaseY + Math.sin(t * 1.15) * 0.07;
    ship.rotation.y = shipBaseYaw + Math.sin(t * 0.27) * 0.028;
    ship.rotation.z = Math.sin(t * 0.72) * 0.018;

    for (const f of flags) {
      f.obj.rotation.y = Math.sin(t * 2.4 + f.phase) * 0.28;
      f.obj.rotation.z = Math.sin(t * 1.7 + f.phase) * 0.06;
    }

    updateOrbit();
    renderer.render(scene, camera);
  }

  updateOrbit();
  animate();
})();
</script>
</body>
</html>
```