Here's a self-contained single-file 3D voxel art scene — it renders immediately and is viewable with the mouse (orbit/zoom/pan), using Three.js via CDN. Everything (water, harbor quay, pier, lighthouse, hills, clouds, birds, and the sailing ship) is built from voxel cubes.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Voxel Harbor — Sailing Ship</title>
<style>
  html,body{margin:0;height:100%;overflow:hidden;background:#9ed8ef;font-family:Georgia,'Times New Roman',serif;}
  #hud{position:fixed;top:16px;left:16px;z-index:10;padding:12px 16px;background:rgba(16,28,38,.62);border:1px solid rgba(255,255,255,.15);border-radius:10px;color:#eaf2f8;backdrop-filter:blur(6px);box-shadow:0 4px 14px rgba(0,0,0,.25);max-width:340px;}
  #hud .title{font-size:18px;font-weight:700;letter-spacing:.5px;}
  #hud .sub{font-size:12px;opacity:.85;margin-top:3px;font-style:italic;}
  #hud .hint{font-size:11px;opacity:.65;margin-top:8px;line-height:1.5;}
  #hud .row{margin-top:9px;display:flex;gap:8px;}
  #hud button{background:#1c3a52;border:1px solid #3a6a86;color:#eaf2f8;border-radius:6px;padding:6px 12px;cursor:pointer;font-size:12px;font-family:inherit;}
  #hud button:hover{background:#2a4a66;}
  canvas{display:block;}
</style>
<script type="importmap">
{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}
</script>
</head>
<body>
<div id="hud">
  <div class="title">⚓ Voxel Harbor</div>
  <div class="sub">A sailing ship calling at a harbor</div>
  <div class="hint">Drag: orbit &nbsp;•&nbsp; Scroll: zoom &nbsp;•&nbsp; Right-drag: pan</div>
  <div class="row">
    <button id="resetBtn">Reset view</button>
    <button id="spinBtn">Auto-orbit: on</button>
  </div>
</div>
<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x9ed8ef);
scene.fog = new THREE.Fog(0x9ed8ef, 55, 115);

const camera = new THREE.PerspectiveCamera(45, window.innerWidth/window.innerHeight, 0.1, 300);
camera.position.set(17, 12, 19);

const renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0,2,0);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.maxPolarAngle = Math.PI*0.495;
controls.minDistance = 6;
controls.maxDistance = 60;
controls.autoRotate = true;
controls.autoRotateSpeed = 0.7;

const spinBtn = document.getElementById('spinBtn');
function updateSpinBtn(){ spinBtn.textContent = controls.autoRotate ? 'Auto-orbit: on' : 'Auto-orbit: off'; }
updateSpinBtn();
controls.addEventListener('start', ()=>{ controls.autoRotate=false; updateSpinBtn(); });
spinBtn.addEventListener('click', ()=>{ controls.autoRotate = !controls.autoRotate; updateSpinBtn(); });

const DEFAULT_CAM = new THREE.Vector3(17,12,19);
const DEFAULT_TARGET = new THREE.Vector3(0,2,0);
document.getElementById('resetBtn').addEventListener('click', ()=>{
  camera.position.copy(DEFAULT_CAM);
  controls.target.copy(DEFAULT_TARGET);
  controls.autoRotate = true;
  updateSpinBtn();
  controls.update();
});

// ---- lights ----
const hemi = new THREE.HemisphereLight(0xcfe8ff, 0x3a4a3a, 0.85);
scene.add(hemi);
const sun = new THREE.DirectionalLight(0xfff2d8, 1.75);
sun.position.set(16,22,10);
sun.castShadow = true;
sun.shadow.mapSize.set(2048,2048);
sun.shadow.camera.left=-26; sun.shadow.camera.right=26;
sun.shadow.camera.top=26; sun.shadow.camera.bottom=-26;
sun.shadow.camera.near=1; sun.shadow.camera.far=70;
sun.shadow.bias = -0.0004;
sun.shadow.camera.updateProjectionMatrix();
scene.add(sun);

// ---- palette helpers ----
function hash(n){ const s = Math.sin(n*127.1+311.7)*43758.5453; return Math.abs(s)%1; }
function pick(palette, seed){ return palette[Math.floor(hash(seed)*palette.length)%palette.length]; }

// ---- static voxels ----
const staticList = [];
function v(x,y,z,size,color){ staticList.push({x,y,z,size,color}); }

// quay
for (let x=-13; x<=13; x++){
  const c = pick(['#9a9a8e','#8d8d83','#a5a596'], x*1.7);
  v(x,0.8,-7,1.6,c);
  v(x,0.8,-8,1.6,c);
  v(x,0.2,-6.4,1.0,'#7f7f74');
}
// pier
for (let x=-5; x<=-3; x++){
  for (let z=-6; z<=4; z++){
    v(x,0.6,z,1.2, (z%2 ? '#a8763e' : '#9d6f38'));
  }
}
[[-5,4],[-3,4],[-5,-6],[-3,-6]].forEach(([x,z])=> v(x,1.45,z,0.35,'#3d2a1a'));
v(-4,1.55,4,0.28,'#2f2f33');
v(-4,2.2,4,0.28,'#2f2f33');
v(-4,2.85,4,0.28,'#2f2f33');
v(-4,3.35,4,0.42,'#ffd76a');
// crates & barrels
v(-10,2.1,-7.4,0.9,'#b07a3f');
v(-10,2.75,-7.4,0.5,'#8a5c2e');
v(-9.2,2.0,-7.0,0.8,'#c39a5b');
v(-7.6,2.0,-7.6,0.6,'#6f4a2c');
v(-7.6,2.55,-7.6,0.42,'#5a3d23');
// crane
v(-11,1.95,-7.3,0.7,'#3a3f45');
v(-11,2.6,-7.3,0.42,'#3a3f45');
v(-11,3.15,-7.3,0.42,'#3a3f45');
v(-11,3.6,-6.5,0.42,'#e0a23c');
v(-11,3.6,-5.8,0.42,'#e0a23c');
v(-11,3.6,-5.1,0.42,'#e0a23c');
v(-11,2.5,-5.1,0.3,'#2f2f33');
// houses
function house(x,z,s,wall,roof){
  v(x,1.6+s/2,z,s,wall);
  v(x,1.6+s+0.12,z,s*0.75,roof);
  v(x,1.6+s+0.5,z,s*0.5,roof);
  v(x,1.6+s+0.75,z,s*0.28,roof);
  v(x-s*0.25,2.15,z+s/2+0.02,0.28,'#2e2a26');
  v(x+s*0.25,2.15,z+s/2+0.02,0.28,'#2e2a26');
}
house(-2.5,-7.6,1.5,'#e0c9a8','#b0563a');
house(2.0,-7.5,1.3,'#d9c8b8','#6b4a2f');
house(5.5,-7.6,1.1,'#cfd8d4','#3e5a74');
// lighthouse
v(9.5,2.3,-7.6,1.4,'#e8e4da');
for (let i=0;i<7;i++){
  v(9.5,3.2+i*0.45,-7.6,0.85, (i%2===0 ? '#f2efe6' : '#c8452f'));
}
v(9.5,6.5,-7.6,0.55,'#ffd76a');
v(9.5,7.0,-7.6,0.45,'#3a3f45');
v(9.5,7.3,-7.6,0.3,'#3a3f45');
// ground slab + hills
for (let x=-13; x<=13; x+=1){ v(x,-0.2,-10.5,1.0,'#6a6a58'); }
for (let x=-13; x<=13; x+=2){
  const h = 3.0 + Math.sin(x*0.4)*1.4;
  for (let y=0.3; y<h; y+=1.0){
    v(x,y,-10.5,1.0,pick(['#4f8f4f','#5d9a5c','#6aa86a'],x*2+y));
  }
}

const staticMesh = new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1), new THREE.MeshLambertMaterial({color:0xffffff}), staticList.length);
{
  const d = new THREE.Object3D();
  staticList.forEach((s,i)=>{
    d.position.set(s.x,s.y,s.z);
    d.scale.set(s.size,s.size,s.size);
    d.updateMatrix();
    staticMesh.setMatrixAt(i,d.matrix);
    staticMesh.setColorAt(i,new THREE.Color(s.color));
  });
}
staticMesh.castShadow = true;
staticMesh.receiveShadow = true;
scene.add(staticMesh);

// ---- water ----
const waterPal = ['#2f6f9f','#3a7fb0','#25638c','#4a90c2','#3d84b3'];
const waterList = [];
for (let x=-13; x<=13; x++){
  for (let z=-6; z<=9; z++){
    if (x>=-5 && x<=-3 && z>=-6 && z<=4) continue;
    const crest = hash(x*3+z*7) > 0.74;
    waterList.push({x,z,size:0.92,color: crest ? '#eef6fb' : pick(waterPal,x*5+z*3)});
  }
}
const waterMesh = new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1), new THREE.MeshLambertMaterial({color:0xffffff}), waterList.length);
{
  const d = new THREE.Object3D();
  waterList.forEach((w,i)=>{
    d.position.set(w.x,-0.46,w.z);
    d.scale.set(w.size,w.size,w.size);
    d.updateMatrix();
    waterMesh.setMatrixAt(i,d.matrix);
    waterMesh.setColorAt(i,new THREE.Color(w.color));
  });
}
waterMesh.receiveShadow = true;
scene.add(waterMesh);

// ---- ship ----
const shipList = [];
function sv(x,y,z,size,color){ shipList.push({x,y,z,size,color}); }
const widths = [1,2,3,3,3,3,2,2,1];
const bottomW = [1,2,2,3,3,3,2,1,1];
for (let i=0;i<9;i++){
  const x = i-4;
  const w = widths[i];
  const bw = bottomW[i];
  for (let k=0;k<bw;k++){ sv(x,-0.45,k-(bw-1)/2,1,'#4a2f1d'); }
  for (let k=0;k<w;k++){ sv(x,0.55,k-(w-1)/2,1, (i%2 ? '#c9a15e' : '#b98f4e')); }
  const edges = w===1 ? [0] : [-(w-1)/2,(w-1)/2];
  for (const z of edges){ sv(x,1.55,z,1,'#3a2415'); }
}
// cabin
sv(-3.2,2.15,0,1.3,'#e8dcc2');
sv(-3.2,3.0,0,0.95,'#7a4a2e');
sv(-3.2,3.45,0,0.55,'#7a4a2e');
sv(-3.2,3.72,0,0.3,'#5a3a26');
sv(-3.2,2.3,0.72,0.28,'#2e2a26');
// masts, yards, sails
const mastX = [-2.2, 2.2];
for (const mx of mastX){
  for (let y=1.9; y<=6.0; y+=0.5){ sv(mx,y,0,0.34,'#3a2415'); }
  for (let z=-2.0; z<=2.0; z+=0.4){ sv(mx,4.85,z,0.3,'#5a3a26'); }
  let row=0;
  for (let y=2.45; y<=4.6; y+=0.45){
    let col=0;
    for (let z=-1.9; z<=1.9; z+=0.44){
      sv(mx,y,z,0.4, ((row+col)%2) ? '#f4ead6' : '#ede2c8');
      col++;
    }
    row++;
  }
  sv(mx,6.35,0,0.28,'#d9b38c');
}
// flags
sv(2.2,6.55,0.55,0.45,'#d43a2f');
sv(2.2,6.55,1.05,0.45,'#d43a2f');
sv(2.2,6.05,0.55,0.45,'#d43a2f');
sv(-2.2,6.55,0.5,0.4,'#e0a23c');
// bow/stern ornaments
sv(4.15,2.0,0,0.45,'#d9b38c');
sv(-4.15,2.0,0,0.45,'#d9b38c');
// cannons
for (const cx of [-2,0,2]){
  sv(cx,2.25,1.0,0.4,'#2f2f33');
  sv(cx,2.25,-1.0,0.4,'#2f2f33');
}
// foam
for (let i=0;i<9;i++){
  const x = -3.5 + i*1.0;
  const idx = Math.min(8, Math.max(0, Math.round(x)+4));
  const w = widths[idx];
  const z = w/2 + 0.55 + (i%2)*0.2;
  sv(x,0.06,z,0.32,'#ffffff');
  sv(x,0.06,-z,0.32,'#ffffff');
}

const shipGroup = new THREE.Group();
shipGroup.position.set(3.2,0,0.6);
const shipMesh = new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1), new THREE.MeshLambertMaterial({color:0xffffff}), shipList.length);
{
  const d = new THREE.Object3D();
  shipList.forEach((s,i)=>{
    d.position.set(s.x,s.y,s.z);
    d.scale.set(s.size,s.size,s.size);
    d.updateMatrix();
    shipMesh.setMatrixAt(i,d.matrix);
    shipMesh.setColorAt(i,new THREE.Color(s.color));
  });
}
shipMesh.castShadow = true;
shipMesh.receiveShadow = true;
shipGroup.add(shipMesh);
scene.add(shipGroup);

// ---- lighthouse beam & lamp ----
const beamGeo = new THREE.BoxGeometry(0.18,0.18,3.2);
beamGeo.translate(0,0,1.8);
const beam = new THREE.Mesh(beamGeo, new THREE.MeshBasicMaterial({color:0xffe27a, transparent:true, opacity:0.35}));
beam.position.set(9.5,6.5,-7.6);
scene.add(beam);
const lamp = new THREE.PointLight(0xffd76a, 8, 9, 2);
lamp.position.set(9.5,6.7,-7.6);
scene.add(lamp);

// ---- clouds & birds ----
const cloudMat = new THREE.MeshLambertMaterial({color:0xffffff});
const clouds = [];
for (let i=0;i<3;i++){
  const g = new THREE.Group();
  const n = 3+i;
  for (let k=0;k<n;k++){
    const m = new THREE.Mesh(new THREE.BoxGeometry(0.9,0.9,0.9), cloudMat);
    m.position.set(k*1.0 - n*0.5, (k%2)*0.35, (k%2?0.35:0));
    g.add(m);
  }
  g.position.set(-11 + i*9, 11 + i*1.6, -8 - i*2.5);
  scene.add(g);
  clouds.push(g);
}
const birdMat = new THREE.MeshLambertMaterial({color:0x2e2a26});
const birds = [];
for (let i=0;i<3;i++){
  const g = new THREE.Group();
  const body = new THREE.Mesh(new THREE.BoxGeometry(0.32,0.32,0.32), birdMat);
  g.add(body);
  const w1 = new THREE.Mesh(new THREE.BoxGeometry(0.5,0.1,0.5), birdMat);
  w1.position.set(0.42,0.08,0); g.add(w1);
  const w2 = new THREE.Mesh(new THREE.BoxGeometry(0.5,0.1,0.5), birdMat);
  w2.position.set(-0.42,0.08,0); g.add(w2);
  g.userData = {wing1:w1, wing2:w2, phase:i*2.1};
  scene.add(g);
  birds.push(g);
}

// ---- animation ----
const clock = new THREE.Clock();
const dummy = new THREE.Object3D();
function animate(){
  requestAnimationFrame(animate);
  const dt = clock.getDelta();
  const t = clock.elapsedTime;

  // water bob
  for (let i=0;i<waterList.length;i++){
    const w = waterList[i];
    dummy.position.set(w.x, -0.46 + Math.sin(t*1.4 + w.x*0.6 + w.z*0.45)*0.07, w.z);
    dummy.scale.set(w.size,w.size,w.size);
    dummy.updateMatrix();
    waterMesh.setMatrixAt(i,dummy.matrix);
  }
  waterMesh.instanceMatrix.needsUpdate = true;

  // ship rocking
  shipGroup.position.y = Math.sin(t*0.9)*0.09;
  shipGroup.rotation.z = Math.sin(t*0.7)*0.035;
  shipGroup.rotation.x = Math.sin(t*0.55+1)*0.02;

  // clouds drift
  for (const c of clouds){
    c.position.x += dt*0.5;
    if (c.position.x > 16) c.position.x = -16;
  }

  // birds circling
  for (const b of birds){
    const ph = b.userData.phase;
    const a = t*0.35 + ph;
    b.position.set(Math.cos(a)*9, 8.5 + Math.sin(a*2)*0.8 + ph*0.6, Math.sin(a)*6 - 2);
    b.userData.wing1.rotation.z = Math.sin(t*6+ph)*0.5;
    b.userData.wing2.rotation.z = -Math.sin(t*6+ph)*0.5;
  }

  // lighthouse beam & lamp
  beam.rotation.y = t*0.8;
  lamp.intensity = 8 + Math.sin(t*3)*2.5;

  controls.update();
  renderer.render(scene,camera);
}
animate();

window.addEventListener('resize', ()=>{
  camera.aspect = window.innerWidth/window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
</script>
</body>
</html>
```

**What it includes:**
- A **sailing ship** (wood-hulled, deck planks, dark rim, stern cabin, two masts with cream sails, flags, cannons, gold bow/stern ornaments, white foam at the waterline) rocking gently in the harbor.
- **Harbor:** stone quay with houses, a crane, crates/barrels, a wooden pier with posts and a lantern, and a striped lighthouse with a sweeping beam and glowing lamp.
- **Environment:** animated voxel waves, drifting clouds, circling gulls, green hills behind the quay, soft shadows and fog.
- **Mouse view:** drag to orbit, scroll to zoom, right-drag to pan; slow auto-orbit that stops when you take over, plus "Reset view" and an auto-orbit toggle.

Note it loads Three.js from a CDN (jsdelivr), so Chrome needs an internet connection. Everything renders immediately on load — just save it as a `.html` file and open it.