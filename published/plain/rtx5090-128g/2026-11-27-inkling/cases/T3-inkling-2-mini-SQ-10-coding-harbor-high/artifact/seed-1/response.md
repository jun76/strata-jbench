Here's a complete, self-contained voxel-art scene. It renders immediately on load (orbit with the mouse, zoom with the scroll wheel, pan with right-drag).

**What's in the scene**
- A sailing ship (hull, deck, masts, yards, white sails, red flag, portholes, crates) gently bobbing
- A concrete quay with a brick warehouse (smoking chimney), two houses, a striped lighthouse with a glowing lamp, a yellow dock crane, crate/barrel clusters, railings and a road
- A wooden pier with lantern, trees, a green strip, and drifting white clouds
- Animated voxel water, red buoys, circling gulls, and bobbing wave voxels — all in a single HTML file

**How to use it**
- Save as `.html` and open it in Chrome. It pulls Three.js from CDN (needs internet); if you'd like it fully offline, download `three.min.js` and `OrbitControls.js` from jsDelivr and swap the two `<script src>` lines for local paths.
- Mouse: drag = orbit, scroll = zoom, right-drag = pan. Toggle "Auto-rotate" or click "Reset view".

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>A Sailing Ship Calling at a Harbor — Voxel Scene</title>
<style>
  html, body { margin:0; padding:0; width:100%; height:100%; overflow:hidden; background:#8fd0e8; font-family:'Segoe UI', system-ui, sans-serif; }
  #panel { position:absolute; top:14px; left:14px; z-index:10; background:rgba(8,18,28,.72); color:#e8f2f9; padding:12px 16px; border-radius:10px; box-shadow:0 4px 18px rgba(0,0,0,.35); max-width:330px; }
  #panel h1 { margin:0 0 4px; font-size:15px; letter-spacing:.3px; font-weight:600; color:#ffd76b; }
  #panel p { margin:2px 0; font-size:11.5px; line-height:1.55; color:#cfe0ec; }
  #panel .row { display:flex; gap:12px; align-items:center; margin-top:8px; }
  #panel label { font-size:11px; display:flex; gap:6px; align-items:center; cursor:pointer; }
  #panel button { background:#2c4a6b; color:#eaf2f8; border:0; border-radius:6px; padding:5px 10px; cursor:pointer; font-size:11px; }
  #panel button:hover { background:#3a5f82; }
  #panel input[type=checkbox] { accent-color:#ffd76b; }
  canvas { display:block; }
</style>
</head>
<body>
<div id="panel">
  <h1>⚓ A Sailing Ship Calling at a Harbor</h1>
  <p>Drag to orbit · Scroll to zoom · Right-drag to pan</p>
  <div class="row">
    <label><input type="checkbox" id="auto" checked> Auto-rotate</label>
    <button id="reset">Reset view</button>
  </div>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
// ---------- scene setup ----------
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x8fd0e8);
scene.fog = new THREE.Fog(0x8fd0e8, 110, 220);

const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 400);
camera.position.set(40, 26, 48);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.target.set(0, 6, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.maxPolarAngle = Math.PI * 0.49;
controls.minDistance = 18;
controls.maxDistance = 130;
controls.autoRotate = true;
controls.autoRotateSpeed = 1.1;

// ---------- lights ----------
const hemi = new THREE.HemisphereLight(0xcfe6ff, 0x2e4050, 0.9);
scene.add(hemi);
const sun = new THREE.DirectionalLight(0xfff2d8, 1.3);
sun.position.set(45, 60, 30);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -70; sun.shadow.camera.right = 70;
sun.shadow.camera.top = 70; sun.shadow.camera.bottom = -70;
sun.shadow.camera.near = 10; sun.shadow.camera.far = 180;
sun.shadow.bias = -0.0005;
scene.add(sun);
const fill = new THREE.DirectionalLight(0xbcd8ff, 0.35);
fill.position.set(-40, 30, -25);
scene.add(fill);

// ---------- voxel geometry builder ----------
const boxGeo = new THREE.BoxGeometry(1, 1, 1);
const bp = boxGeo.attributes.position.array;
const bn = boxGeo.attributes.normal.array;
const bi = boxGeo.index.array;

function jitter(hex, j) {
  const c = new THREE.Color(hex);
  const f = 1 + (Math.random() * 2 - 1) * j;
  c.r = Math.min(1, c.r * f); c.g = Math.min(1, c.g * f); c.b = Math.min(1, c.b * f);
  return c;
}

function buildVoxelGeometry(voxels) {
  const pos = [], nrm = [], col = [], idx = [];
  let o = 0;
  for (const v of voxels) {
    const c = v.color;
    for (let i = 0; i < bp.length / 3; i++) {
      pos.push(v.cx + bp[3 * i] * v.w, v.cy + bp[3 * i + 1] * v.h, v.cz + bp[3 * i + 2] * v.d);
      nrm.push(bn[3 * i], bn[3 * i + 1], bn[3 * i + 2]);
      col.push(c.r, c.g, c.b);
    }
    for (let i = 0; i < bi.length; i++) idx.push(bi[i] + o);
    o += bp.length / 3;
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute('normal', new THREE.Float32BufferAttribute(nrm, 3));
  g.setAttribute('color', new THREE.Float32BufferAttribute(col, 3));
  g.setIndex(idx);
  return g;
}

const MAT = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.92, metalness: 0.0, flatShading: true });

// ---------- harbor (static voxels) ----------
const V = [];
function B(cx, cy, cz, w, h, d, color, j = 0.04) { V.push({ cx, cy, cz, w, h, d, color: jitter(color, j) }); }

// quay platform
for (let x = -36; x <= 36; x += 2) for (let z = -22; z <= -8; z += 2) B(x, 1, z, 2, 2, 2, '#8d959e', 0.05);
// green strip behind buildings
for (let x = -36; x <= 36; x += 2) for (let z = -28; z <= -22; z += 2) B(x, 0.7, z, 2, 1.4, 2, '#477a3d', 0.06);
// trees
for (const x of [-32, -22, -12, -2, 8, 30]) {
  B(x, 2.4, -25, 1.1, 2.4, 1.1, '#6b4a33');
  B(x, 4.9, -25, 3.4, 2.6, 3.4, '#3e7d46', 0.06);
  B(x, 6.8, -25, 1.5, 1.2, 1.5, '#4d8f52', 0.06);
}
// warehouse
B(-20, 4.0, -19, 20, 6, 6, '#a85536', 0.05);
B(-20, 7.6, -19, 20.4, 1.6, 6.4, '#4a2f28', 0.04);
for (const x of [-28, -24, -20, -16, -12]) B(x, 4.5, -15.8, 1.8, 1.8, 0.3, '#1f2733');
B(-20, 3.0, -15.8, 2.6, 3.6, 0.4, '#2e241a');
B(-27, 9.6, -19, 2.4, 5.2, 2.4, '#8a4a30');
// houses
B(5, 4.2, -19.5, 6.5, 4.5, 4.5, '#e3d7bd', 0.04);
B(5, 7.3, -19.5, 7, 1.6, 5, '#7a4a36', 0.04);
B(5, 2.6, -17.35, 1.8, 2.8, 0.4, '#3a2f22');
B(3.5, 4.6, -17.35, 1.4, 1.4, 0.3, '#26313c');
B(6.5, 4.6, -17.35, 1.4, 1.4, 0.3, '#26313c');
B(12.5, 3.9, -19.5, 5.5, 4, 4, '#d8c8a8', 0.04);
B(12.5, 6.6, -19.5, 6, 1.5, 4.4, '#5d4634', 0.04);
B(12.5, 2.5, -17.35, 1.6, 2.6, 0.4, '#33302a');
B(10.5, 4.4, -17.35, 1.3, 1.3, 0.3, '#26313c');
B(14.5, 4.4, -17.35, 1.3, 1.3, 0.3, '#26313c');
// lighthouse (striped tower + open lantern room)
B(24, 3.2, -19.5, 4.2, 2.4, 4.2, '#f1eee4');
B(24, 5.6, -19.5, 4.2, 2.4, 4.2, '#d9534a');
B(24, 8.0, -19.5, 4.2, 2.4, 4.2, '#f1eee4');
B(24, 10.4, -19.5, 4.2, 2.4, 4.2, '#d9534a');
B(24, 12.8, -19.5, 4.2, 2.4, 4.2, '#f1eee4');
B(22.9, 14.35, -18.1, 0.7, 1.6, 0.7, '#2e2e2e');
B(25.1, 14.35, -18.1, 0.7, 1.6, 0.7, '#2e2e2e');
B(22.9, 14.35, -20.9, 0.7, 1.6, 0.7, '#2e2e2e');
B(25.1, 14.35, -20.9, 0.7, 1.6, 0.7, '#2e2e2e');
B(24, 14.35, -19.5, 1.7, 1.3, 1.7, '#ffd76b');
B(24, 15.5, -19.5, 3.4, 0.7, 3.4, '#d9534a');
// dock crane
B(17, 3.5, -13, 3.2, 3, 3.2, '#e0a93a', 0.05);
B(17, 6.7, -13, 1.7, 5.4, 1.7, '#b9762a');
B(20.2, 9.4, -13, 8.4, 0.8, 0.8, '#b9762a');
B(23.8, 7.9, -13, 0.35, 2.6, 0.35, '#333333');
B(23.8, 6.1, -13, 0.8, 0.8, 0.8, '#333333');
// crates & barrels
B(-8, 3.0, -10.5, 2, 2, 2, '#a3763f');
B(-8, 5.0, -10.5, 1.6, 1.6, 1.6, '#b0824a');
B(8, 2.9, -10.5, 1.4, 1.8, 1.4, '#6e4a2f');
B(8.2, 4.5, -10.5, 1.6, 1.6, 1.6, '#8f6a3d');
B(-26, 3.0, -10.5, 2, 2, 2, '#a3763f');
B(-26, 5.0, -10.5, 1.7, 1.7, 1.7, '#b0824a');
B(-23.5, 2.9, -10.5, 1.4, 1.8, 1.4, '#6e4a2f');
B(-2, 2.9, -10.5, 1.8, 1.8, 1.8, '#a3763f');
// railing
for (let x = -34; x <= 34; x += 4) B(x, 2.9, -8.6, 0.35, 1.4, 0.35, '#3c434a');
B(0, 3.55, -8.6, 69, 0.25, 0.3, '#3c434a');
// road
B(0, 2.06, -11, 58, 0.12, 2.4, '#454b52');
// pier planks
for (let x = 12; x <= 17; x++) for (let z = -8; z <= 12; z++) B(x, 2.25, z, 1.0, 0.5, 1.0, '#8a6a44', 0.07);
// pier posts
for (let z = -8; z <= 11; z += 4) {
  B(12.4, 3.6, z, 0.55, 2.4, 0.55, '#5e4630');
  B(16.6, 3.6, z, 0.55, 2.4, 0.55, '#5e4630');
}
// pier lantern
B(14, 4.2, 11.5, 0.5, 3.4, 0.5, '#4a3a28');
B(14, 6.2, 11.5, 0.8, 0.8, 0.8, '#ffd76b');

const staticGeo = buildVoxelGeometry(V);
const staticMesh = new THREE.Mesh(staticGeo, MAT);
staticMesh.castShadow = true;
staticMesh.receiveShadow = true;
scene.add(staticMesh);

// ---------- water (instanced, animated) ----------
const waterPts = [];
for (let x = -36; x <= 36; x += 2.5) {
  for (let z = -8; z <= 34; z += 2.5) {
    const t = (z + 8) / 42;
    const c = new THREE.Color(0x6cc3e0).lerp(new THREE.Color(0x2b6ba0), t);
    const f = 1 + (Math.random() * 2 - 1) * 0.05;
    c.r = Math.min(1, c.r * f); c.g = Math.min(1, c.g * f); c.b = Math.min(1, c.b * f);
    waterPts.push({ x, z, c });
  }
}
const waterGeo = new THREE.BoxGeometry(2.35, 0.7, 2.35);
const waterMat = new THREE.MeshLambertMaterial({ color: 0xffffff });
const waterMesh = new THREE.InstancedMesh(waterGeo, waterMat, waterPts.length);
const m4 = new THREE.Matrix4();
waterPts.forEach((p, i) => {
  waterMesh.setColorAt(i, p.c);
  m4.makeTranslation(p.x, -0.25, p.z);
  waterMesh.setMatrixAt(i, m4);
});
waterMesh.instanceColor.needsUpdate = true;
waterMesh.castShadow = true;
waterMesh.receiveShadow = true;
scene.add(waterMesh);

// ---------- sailing ship ----------
const shipV = [];
function SB(cx, cy, cz, w, h, d, color, j = 0.04) { shipV.push({ cx, cy, cz, w, h, d, color: jitter(color, j) }); }
function hullHalf(x) { const a = Math.abs(x); if (a > 8) return 1; if (a > 6) return 2; return 3; }
for (let x = -7; x <= 7; x++) SB(x, 0, 0, 1, 1, 5, '#3d2418');                        // keel
for (let x = -9; x <= 9; x++) { const h = hullHalf(x); SB(x, 1, 0, 1, 1, 2 * h + 1, '#5b3a28'); }
for (let x = -8; x <= 8; x++) { const h = hullHalf(x); SB(x, 2, 0, 1, 1, 2 * h + 1, '#c9a06b', 0.06); }
for (let x = -8; x <= 8; x += 2) { const h = hullHalf(x);
  SB(x, 2.95, h + 0.05, 1, 0.6, 0.45, '#3d2418');
  SB(x, 2.95, -(h + 0.05), 1, 0.6, 0.45, '#3d2418');
}
for (const x of [-7, -4, -1, 2, 5, 8]) { const h = hullHalf(x);
  SB(x, 1, h + 0.25, 0.8, 0.8, 0.3, '#1d1d1d');
  SB(x, 1, -(h + 0.25), 0.8, 0.8, 0.3, '#1d1d1d');
}
for (const mx of [-6, 0, 6]) {
  for (let y = 3; y <= 9; y++) SB(mx, y, 0, 0.9, 1, 0.9, '#6b4a33');
  SB(mx, 9.8, 0, 1.0, 0.6, 1.0, '#3d2418');
  SB(mx, 8.4, 0, 0.6, 0.5, 6.2, '#6b4a33');
  SB(mx, 6.2, 0, 0.45, 3.8, 5.6, '#f2eee2', 0.05);
}
SB(0, 10.2, 0, 0.25, 1.4, 0.25, '#3d2418');
SB(0.85, 10.2, 0, 1.7, 0.9, 0.3, '#d94f3d', 0.03);
SB(3, 3.15, -1.2, 1.5, 1.5, 1.5, '#a3763f');
SB(3.4, 4.35, -1.2, 1.2, 1.2, 1.2, '#b0824a');

const shipGeo = buildVoxelGeometry(shipV);
const shipMesh = new THREE.Mesh(shipGeo, MAT);
shipMesh.castShadow = true; shipMesh.receiveShadow = true;
const shipGroup = new THREE.Group();
shipGroup.add(shipMesh);
shipGroup.position.set(-2, 0.35, 6);
shipGroup.rotation.y = 0.06;
scene.add(shipGroup);

// ---------- buoys ----------
const buoyPts = [[-20, 10], [6, 20], [22, 14]];
const buoyGroups = [];
buoyPts.forEach(p => {
  const g = new THREE.Group();
  const body = new THREE.Mesh(new THREE.BoxGeometry(1.2, 1.2, 1.2), new THREE.MeshStandardMaterial({ color: 0xd94f3d, roughness: 0.9 }));
  const cap = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.6, 0.6), new THREE.MeshStandardMaterial({ color: 0xffd76b, roughness: 0.9 }));
  cap.position.y = 1.0;
  body.castShadow = true; cap.castShadow = true;
  g.add(body, cap);
  g.position.set(p[0], 0.45, p[1]);
  scene.add(g);
  buoyGroups.push(g);
});

// ---------- smoke ----------
const smokeMat = new THREE.MeshLambertMaterial({ color: 0xb9b9b9, transparent: true, opacity: 0.8, depthWrite: false });
const smokePuffs = [];
for (let i = 0; i < 4; i++) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(1.6, 1.6, 1.6), smokeMat.clone());
  scene.add(m); smokePuffs.push(m);
}

// ---------- gulls ----------
const gullGroups = [];
for (let i = 0; i < 3; i++) {
  const g = new THREE.Group();
  const mat = new THREE.MeshLambertMaterial({ color: 0xf4f4f4 });
  const body = new THREE.Mesh(new THREE.BoxGeometry(1.1, 0.4, 0.5), mat);
  const wingL = new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.12, 1.3), mat);
  wingL.position.z = 1.0;
  const wingR = new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.12, 1.3), mat);
  wingR.position.z = -1.0;
  g.add(body, wingL, wingR);
  scene.add(g);
  gullGroups.push({ g, wingL, wingR });
}

// ---------- clouds ----------
const cloudGroups = [];
const cloudBase = [[-25, 22, -18], [5, 24, -12], [25, 21, 8], [-8, 23, 14]];
for (let i = 0; i < 4; i++) {
  const voxels = [];
  voxels.push({ cx: 0, cy: 0, cz: 0, w: 4, h: 1.6, d: 3, color: jitter('#f6f6f6', 0.02) });
  voxels.push({ cx: -2, cy: 0.7, cz: 0, w: 2.4, h: 1.4, d: 2.2, color: jitter('#f6f6f6', 0.02) });
  voxels.push({ cx: 2.2, cy: 0.5, cz: 0, w: 2.2, h: 1.3, d: 2.0, color: jitter('#f6f6f6', 0.02) });
  voxels.push({ cx: 0, cy: -0.9, cz: 0, w: 3, h: 0.8, d: 2.4, color: jitter('#ededed', 0.02) });
  const mesh = new THREE.Mesh(buildVoxelGeometry(voxels), MAT);
  mesh.castShadow = false; mesh.receiveShadow = false;
  mesh.position.set(cloudBase[i][0], cloudBase[i][1], cloudBase[i][2]);
  scene.add(mesh);
  cloudGroups.push(mesh);
}

// ---------- animation ----------
const clock = new THREE.Clock();
function animate() {
  requestAnimationFrame(animate);
  const t = clock.getElapsedTime();

  for (let i = 0; i < waterPts.length; i++) {
    const p = waterPts[i];
    const wave = Math.sin(t * 1.5 + p.x * 0.12 + p.z * 0.18) * 0.22 + Math.sin(t * 2.2 + p.z * 0.35) * 0.08;
    m4.makeTranslation(p.x, -0.25 + wave, p.z);
    waterMesh.setMatrixAt(i, m4);
  }
  waterMesh.instanceMatrix.needsUpdate = true;

  shipGroup.position.y = 0.35 + Math.sin(t * 1.15) * 0.12;
  shipGroup.rotation.z = Math.sin(t * 0.8) * 0.025;
  shipGroup.rotation.x = Math.sin(t * 0.65 + 1.2) * 0.02;

  buoyGroups.forEach((g, i) => {
    const p = buoyPts[i];
    g.position.set(p[0], 0.45 + Math.sin(t * 1.8 + i * 2.1) * 0.25, p[1]);
    g.rotation.z = Math.sin(t * 1.3 + i) * 0.12;
  });

  smokePuffs.forEach((m, i) => {
    const age = (t * 0.35 + i * 0.25) % 1;
    m.position.set(-27 + Math.sin(age * 5 + i) * 0.7, 12.0 + age * 5.5, -19);
    const s = 0.55 + age * 1.35;
    m.scale.set(s, s, s);
    m.material.opacity = Math.max(0, 0.85 - age * 0.9);
  });

  gullGroups.forEach((gl, i) => {
    const a = t * 0.45 + i * 2.15;
    gl.g.position.set(Math.cos(a) * 17, 16.5 + Math.sin(t * 0.9 + i) * 2.2, Math.sin(a) * 17 + 4);
    gl.g.rotation.y = -a - Math.PI / 2;
    const flap = Math.sin(t * 9 + i * 1.3) * 0.55;
    gl.wingL.rotation.x = flap;
    gl.wingR.rotation.x = -flap;
  });

  cloudGroups.forEach((m, i) => {
    m.position.x = cloudBase[i][0] + Math.sin(t * 0.06 + i * 1.6) * 16;
    m.rotation.y = Math.sin(t * 0.04 + i) * 0.2;
  });

  controls.update();
  renderer.render(scene, camera);
}

// ---------- UI ----------
document.getElementById('auto').addEventListener('change', e => { controls.autoRotate = e.target.checked; });
document.getElementById('reset').addEventListener('click', () => {
  camera.position.set(40, 26, 48);
  controls.target.set(0, 6, 0);
  controls.update();
});

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

Notes:
- Every mesh (harbor, ship, buoys, clouds) is built from 1-unit voxels with per-voxel color jitter for a hand-painted voxel look, flat-shaded.
- Water is ~500 instanced voxels animated per frame, so it stays smooth. The scene renders immediately and runs in a `requestAnimationFrame` loop.
- If you want it fully offline (no CDN), download `three.min.js` and `OrbitControls.js` and replace the two CDN `<script src>` tags with local relative paths — the rest of the file stays the same.