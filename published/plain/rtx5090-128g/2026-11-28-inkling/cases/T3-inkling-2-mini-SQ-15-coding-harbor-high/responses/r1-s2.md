Looking at your request, I'll build a polished voxel harbor scene in a single HTML file using Three.js with instanced voxel meshes. Here's the complete scene — a sailing ship moored at a stone quay with a lighthouse, crane, houses, containers, clouds, seagulls, and animated water:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Harbor Voyage — Voxel Ship</title>
<style>
  body{margin:0;overflow:hidden;background:#0b1520;font-family:Georgia,'Times New Roman',serif;}
  canvas{display:block;cursor:grab;}
  canvas:active{cursor:grabbing;}
  #hud{position:fixed;inset:0;pointer-events:none;z-index:10;}
  #title{position:absolute;top:18px;left:20px;background:rgba(12,20,28,.55);backdrop-filter:blur(10px);
    border:1px solid rgba(255,255,255,.14);border-radius:14px;padding:14px 20px;color:#f5efe2;
    box-shadow:0 8px 30px rgba(0,0,0,.35);animation:fadein .9s ease both;}
  #title h1{margin:0;font-size:22px;letter-spacing:2px;font-weight:600;}
  #title p{margin:5px 0 0;font-size:12px;opacity:.75;letter-spacing:1px;}
  #controls{position:absolute;top:18px;right:20px;display:flex;gap:10px;pointer-events:auto;animation:fadein 1.1s ease both;}
  button{font-family:inherit;font-size:12.5px;letter-spacing:.6px;color:#f5efe2;background:rgba(12,20,28,.55);
    border:1px solid rgba(255,255,255,.16);border-radius:10px;padding:9px 13px;cursor:pointer;backdrop-filter:blur(10px);
    transition:all .18s;}
  button:hover{background:rgba(40,58,72,.8);border-color:rgba(255,255,255,.32);}
  button.on{background:rgba(224,163,58,.9);border-color:rgba(255,255,255,.4);color:#1c1608;}
  #hint{position:absolute;bottom:16px;left:50%;transform:translateX(-50%);background:rgba(12,20,28,.5);color:#e8e2d2;
    font-size:12px;letter-spacing:.8px;padding:8px 16px;border-radius:999px;border:1px solid rgba(255,255,255,.12);
    backdrop-filter:blur(8px);white-space:nowrap;animation:fadein 1.3s ease both;}
  @media (max-width:640px){#hint{display:none;}#title h1{font-size:17px;}}
  @keyframes fadein{from{opacity:0;transform:translateY(8px);}to{opacity:1;transform:translateY(0);}}
</style>
<script type="importmap">
{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js"}}
</script>
</head>
<body>
<div id="hud">
  <div id="title"><h1>Harbor Voyage</h1><p>A voxel harbor — the ship is calling</p></div>
  <div id="controls">
    <button id="btnMode">🌇 Sunset</button>
    <button id="btnRotate" class="on">⟳ Auto-rotate</button>
    <button id="btnReset">⌂ Reset view</button>
  </div>
  <div id="hint">Drag to orbit · Scroll to zoom · Right-drag to pan · Double-click to reset</div>
</div>
<script type="module">
import * as THREE from 'three';

/* ============ Renderer / Scene ============ */
const renderer = new THREE.WebGLRenderer({ antialias:true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.12;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xcfe6ef, 70, 170);
const camera = new THREE.PerspectiveCamera(45, innerWidth/innerHeight, 0.1, 500);

function skyTexture(stops){
  const c = document.createElement('canvas'); c.width = 4; c.height = 256;
  const g = c.getContext('2d');
  const grad = g.createLinearGradient(0,0,0,256);
  for(const [o,col] of stops) grad.addColorStop(o,col);
  g.fillStyle = grad; g.fillRect(0,0,4,256);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

/* ============ Lights ============ */
const hemi = new THREE.HemisphereLight(0xbfe0ff, 0x6b7a52, 0.75); scene.add(hemi);
const sun = new THREE.DirectionalLight(0xfff1d0, 1.55);
sun.position.set(40,50,26); sun.castShadow = true;
sun.shadow.mapSize.set(2048,2048);
sun.shadow.camera.left=-52; sun.shadow.camera.right=52;
sun.shadow.camera.top=52; sun.shadow.camera.bottom=-52;
sun.shadow.camera.near=5; sun.shadow.camera.far=160;
sun.shadow.camera.updateProjectionMatrix();
sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.25;
scene.add(sun); scene.add(sun.target);
const lampLight = new THREE.PointLight(0xffd98a, 0.5, 26, 2);
lampLight.position.set(-17.5,13.6,-19.5); scene.add(lampLight);

/* ============ Voxel helpers ============ */
function jitter(hex, amt=0.07){
  const c = new THREE.Color(hex);
  c.multiplyScalar(1 + (Math.random()*2-1)*amt);
  return c;
}
const world = []; const worldKeys = new Set();
function wPush(x,y,z,hex,s=1,j=0.07){
  const k = x+','+y+','+z; if(worldKeys.has(k)) return; worldKeys.add(k);
  world.push({x,y,z,c:jitter(hex,j),s});
}
function box(x0,y0,z0,x1,y1,z1,hex,j=0.07){
  for(let y=y0;y<=y1;y++)for(let z=z0;z<=z1;z++)for(let x=x0;x<=x1;x++) wPush(x,y,z,hex,1,j);
}
function buildVoxelMesh(list, mat, shadows=true){
  const geo = new THREE.BoxGeometry(1,1,1);
  const mesh = new THREE.InstancedMesh(geo, mat, list.length);
  const m = new THREE.Matrix4(); const q = new THREE.Quaternion();
  const p = new THREE.Vector3(); const s = new THREE.Vector3();
  list.forEach((v,i)=>{
    p.set(v.x,v.y,v.z); s.setScalar(v.s||1); m.compose(p,q,s);
    mesh.setMatrixAt(i,m); mesh.setColorAt(i,v.c);
  });
  mesh.instanceMatrix.needsUpdate = true;
  if(mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
  mesh.castShadow = shadows; mesh.receiveShadow = true;
  return mesh;
}

/* ============ Quay ============ */
box(-28,-2,-26, 28,1,-14, '#8d8578', 0.06);                       // stone block
for(let z=-26;z<=-15;z++)for(let x=-28;x<=28;x++) wPush(x,2,z,'#9c927e',1,0.09); // deck
for(let x=-28;x<=28;x++) wPush(x,2,-14,'#ece5d2',1,0.03);         // edge stripe
box(-32,2,-34, 32,2,-27, '#8fa36a', 0.1);                          // grass strip behind
// trees
for(const [tx,tz] of [[-24,-29],[-4,-30],[18,-29]]){
  box(tx,3,tz, tx,4,tz, '#6b4226');
  box(tx-1,5,tz-1, tx+1,6,tz+1, '#4f8a4a', 0.12);
  wPush(tx,7,tz, '#5da05a', 1, 0.1);
}

/* ============ Pier ============ */
box(-6,-2,-13, 6,1,6, '#7d7466', 0.08);                            // stone base
for(let z=-13;z<=6;z++)for(let x=-6;x<=6;x++)
  wPush(x,2,z, (x===-6||x===6)?'#e8d9a0':'#a9743f', 1, 0.09);       // planks + safety line
for(const [px,pz] of [[-6,-12],[6,-12],[-6,5],[6,5]]) box(px,-1,pz, px,1,pz, '#4a3220');
box(5,3,5, 5,3,5, '#3a332c');  wPush(5,4,5,'#3a332c',0.7,0.03);     // bollards
box(5,3,-11, 5,3,-11, '#3a332c'); wPush(5,4,-11,'#3a332c',0.7,0.03);
box(-4,3,-8, -3,4,-7, '#b0813f', 0.12);                            // crate
box(-4,3,-4, -3,3,-3, '#9a6b34', 0.12);                            // small crate
box(4,3,-2, 4,4,-2, '#7a4a2a', 0.1);                               // barrels
box(4,3,-1, 4,3,-1, '#7a4a2a', 0.1);

/* ============ Lighthouse ============ */
box(-19,3,-21, -16,4,-18, '#8d8578', 0.06);
for(let y=5;y<=11;y++){
  const hex = y<=6 ? '#f2eee2' : y<=8 ? '#c94f3d' : y<=10 ? '#f2eee2' : '#c94f3d';
  box(-18,y,-20, -17,y,-19, hex, 0.05);
}
box(-19,12,-21, -16,12,-18, '#3a332c', 0.05);
box(-18,13,-20, -17,13,-19, '#ffdf8a', 0.02);
box(-18,14,-20, -17,14,-19, '#c94f3d', 0.05);
wPush(-18,15,-20, '#3a332c', 1, 0.05);

/* ============ Crane ============ */
box(12,3,-22, 16,4,-18, '#6f6a5e', 0.06);
box(13,5,-21, 14,11,-19, '#e0a33a', 0.05);
box(12,12,-21, 15,12,-19, '#3a332c', 0.05);
wPush(13,12,-18, '#ffe9a0', 1, 0.03); wPush(14,12,-18, '#ffe9a0', 1, 0.03); wPush(15,12,-18, '#ffe9a0', 1, 0.03);
box(13,13,-19, 14,13,-9, '#e0a33a', 0.05);
box(12,12,-24, 15,13,-22, '#3a332c', 0.05);

/* ============ Houses ============ */
for(let y=3;y<=5;y++)for(let z=-23;z<=-20;z++)for(let x=-11;x<=-8;x++){
  let hex='#e2d3ac';
  if(z===-20&&y===4&&(x===-11||x===-8)) hex='#ffe9a0';
  else if(z===-20&&x===-9) hex='#4a3220';
  wPush(x,y,z,hex,1,0.06);
}
box(-10,6,-22, -9,6,-21, '#b3502e', 0.06); wPush(-9,7,-21,'#b3502e',1,0.06);
wPush(-11,6,-22, '#8d6b52', 1, 0.05); wPush(-11,7,-22, '#8d6b52', 1, 0.05);
for(let y=3;y<=5;y++)for(let z=-24;z<=-21;z++)for(let x=1;x<=6;x++){
  let hex='#c2cfae';
  if(z===-21&&y===4&&(x===2||x===5)) hex='#ffe9a0';
  else if(z===-21&&x===3) hex='#4a3220';
  wPush(x,y,z,hex,1,0.06);
}
box(1,6,-23, 6,6,-22, '#c25a34', 0.06);
box(2,7,-23, 5,7,-22, '#c25a34', 0.06);
box(3,8,-23, 4,8,-22, '#c25a34', 0.06);

/* ============ Shed / containers / lamps ============ */
for(let y=3;y<=4;y++)for(let z=-17;z<=-15;z++)for(let x=-15;x<=-13;x++){
  let hex='#d8cba4';
  if(z===-15&&x===-14) hex='#4a3220';
  wPush(x,y,z,hex,1,0.06);
}
box(-15,5,-17, -13,5,-15, '#8d8578', 0.06);
box(-4,3,-18, -1,3,-17, '#c0563e', 0.08);
box(-4,4,-18, -1,4,-17, '#3a6ea8', 0.08);
box(-4,5,-18, -1,5,-17, '#4f8a4a', 0.08);
box(23,3,-17, 26,4,-15, '#4f8a4a', 0.08);
for(const [lx,lz] of [[-24,-15],[-6,-15],[18,-15]]){
  box(lx,3,lz, lx,5,lz, '#3a332c', 0.05);
  wPush(lx,6,lz, '#ffe9a0', 1, 0.03);
}

/* ============ World mesh ============ */
const voxelMat = new THREE.MeshLambertMaterial({ color:0xffffff });
const worldMesh = buildVoxelMesh(world, voxelMat, true);
scene.add(worldMesh);

/* ============ Water ============ */
const waterCells = [];
for(let z=-26;z<=32;z++)for(let x=-32;x<=32;x++){
  if(z>=-26 && z<=-14 && x>=-28 && x<=28) continue;          // quay
  if(x>=-6 && x<=6 && z>=-13 && z<=6) continue;              // pier
  const foam = (z===-13 && !(x>=-6&&x<=6)) || (z>=-13&&z<=6&&(x===-7||x===7)) || (z===7 && x>=-6 && x<=6);
  const t = (z+26)/58;
  const base = new THREE.Color('#4aa3cc').lerp(new THREE.Color('#1d6a9e'), t);
  base.multiplyScalar(1 + (Math.random()*2-1)*0.06);
  waterCells.push({ x, z, foam,
    color: foam ? new THREE.Color('#e9f6fb').multiplyScalar(1+(Math.random()*2-1)*0.04) : base,
    amp: foam ? 0.34 : 0.2, speed: foam ? 1.9 : 1.3 });
}
const waterMesh = new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1), new THREE.MeshLambertMaterial({color:0xffffff}), waterCells.length);
{
  const m = new THREE.Matrix4();
  waterCells.forEach((c,i)=>{ m.makeTranslation(c.x,0,c.z); waterMesh.setMatrixAt(i,m); waterMesh.setColorAt(i,c.color); });
  waterMesh.instanceMatrix.needsUpdate = true; waterMesh.instanceColor.needsUpdate = true;
}
waterMesh.castShadow = false; waterMesh.receiveShadow = true;
scene.add(waterMesh);

/* ============ Ship ============ */
const shipVoxels = []; const shipKeys = new Set();
function sV(x,y,z,hex,j=0.07){
  const k = x+','+y+','+z; if(shipKeys.has(k)) return; shipKeys.add(k);
  shipVoxels.push({x,y,z,c:jitter(hex,j),s:1});
}
function sBox(x0,y0,z0,x1,y1,z1,hex,j=0.07){
  for(let y=y0;y<=y1;y++)for(let z=z0;z<=z1;z++)for(let x=x0;x<=x1;x++) sV(x,y,z,hex,j);
}
const profile = new Map();
profile.set(-11,0);profile.set(-10,1);profile.set(-9,1);profile.set(-8,2);profile.set(-7,2);
for(let z=-6;z<=6;z++) profile.set(z,3);
profile.set(7,2);profile.set(8,2);profile.set(9,1);profile.set(10,1);profile.set(11,0);

for(let z=-11;z<=11;z++){
  const hw = profile.get(z);
  if(Math.abs(z)<=9) for(let x=-1;x<=1;x++) sV(x,-2,z,'#2b2320',0.05);
  const hw1 = Math.min(hw,2);
  for(let x=-hw1;x<=hw1;x++) sV(x,-1,z,'#6b4226',0.06);
  for(let x=-hw;x<=hw;x++) sV(x,0,z,'#6b4226',0.06);
  for(let x=-hw;x<=hw;x++) sV(x,1,z,'#e6dcc0',0.04);
  for(let x=-hw;x<=hw;x++) sV(x,2,z,'#a9743f',0.1);
}
for(let z=-5;z<=6;z++){ const hw=profile.get(z); if(hw===0) sV(0,3,z,'#4a3220',0.05); else { sV(-hw,3,z,'#4a3220',0.05); sV(hw,3,z,'#4a3220',0.05); } }
// stern castle
for(let z=-11;z<=-6;z++){ const hw=profile.get(z); for(let x=-hw;x<=hw;x++) sV(x,3,z,'#a9743f',0.1); }
sV(0,4,-11,'#ffe9a0',0.02);
sV(-3,4,-6,'#4a3220',0.05); sV(3,4,-6,'#4a3220',0.05);
// bow castle
for(let z=7;z<=11;z++){ const hw=profile.get(z); for(let x=-hw;x<=hw;x++) sV(x,3,z,'#a9743f',0.1); }
for(let z=7;z<=10;z++){ const hw=profile.get(z); if(hw===0) sV(0,4,z,'#4a3220',0.05); else { sV(-hw,4,z,'#4a3220',0.05); sV(hw,4,z,'#4a3220',0.05); } }
sV(0,4,11,'#ffe9a0',0.02);
// cabin
for(let y=4;y<=5;y++)for(let z=-10;z<=-7;z++)for(let x=-1;x<=1;x++){
  let hex='#d9c9a8';
  if(z===-7&&y===5) hex='#2e2118';
  sV(x,y,z,hex,0.05);
}
sBox(-1,6,-10, 1,6,-7, '#4a3220', 0.05);
sV(0,4,8,'#8a5a34',0.06);                    // chest
sV(0,4,9,'#3a332c',0.03);                    // bow cleat
sV(0,4,-6,'#3a332c',0.03);                   // stern cleat
// masts & yards
for(let y=2;y<=13;y++) sV(0,y,-3,'#4a3220',0.05);
for(let y=2;y<=11;y++) sV(0,y,4,'#4a3220',0.05);
for(let x=-4;x<=4;x++) sV(x,10,-3,'#6b4226',0.06);
for(let x=-3;x<=3;x++) sV(x,13,-3,'#6b4226',0.06);
for(let x=-3;x<=3;x++) sV(x,9,4,'#6b4226',0.06);
for(let x=-2;x<=2;x++) sV(x,11,4,'#6b4226',0.06);
// sails
function sSail(z, topY, rows, halfTop, halfBot, colr, belly){
  for(let i=0;i<rows;i++){
    const t = rows===1 ? 0 : i/(rows-1);
    const half = Math.round(halfTop + (halfBot-halfTop)*t);
    for(let x=-half;x<=half;x++){
      const bz = -Math.round(belly*(1 - (x/(half+0.6))*(x/(half+0.6))));
      sV(x, topY-i, z+bz, colr, 0.05);
    }
  }
}
sSail(-3, 9, 5, 4, 2, '#f2e8d0', 1.5);
sSail(-3, 12, 3, 3, 2, '#f6eed9', 1.2);
sSail(4, 8, 5, 3, 2, '#f2e8d0', 1.4);
sSail(4, 10, 2, 2, 2, '#f6eed9', 1.1);
// jib
for(let z=6;z<=14;z++){
  const t=(z-6)/8;
  const count=Math.max(1, Math.round(5*(1-t)));
  const cy=5 - 0.4*t;
  for(let k=0;k<count;k++) sV(0, Math.round(cy + (k-(count-1)/2)*1.0), z, '#f6eed9', 0.05);
}
// bowsprit
for(let i=0;i<=5;i++) sV(0, Math.round(3.2+i*0.26), 11+Math.round(i*0.75), '#4a3220', 0.05);

const shipGroup = new THREE.Group();
shipGroup.position.set(10,0,-2);
shipGroup.rotation.y = 0.28;
scene.add(shipGroup);
const shipMesh = buildVoxelMesh(shipVoxels, voxelMat, true);
shipGroup.add(shipMesh);

// flags
function makeFlag(voxels){
  const g = new THREE.Group();
  for(const [x,y,z,col] of voxels){
    const m = new THREE.Mesh(new THREE.BoxGeometry(0.8,0.8,0.8), new THREE.MeshLambertMaterial({color:col}));
    m.position.set(x,y,z); g.add(m);
  }
  return g;
}
const flagMain = makeFlag([[0,0,-1,'#d6453d'],[0,0,-2,'#f5f2e8'],[0,-0.8,-1,'#f5f2e8'],[0,-0.8,-2,'#d6453d']]);
flagMain.position.set(0,14,-3); shipGroup.add(flagMain);
const flagFore = makeFlag([[0,0,-0.9,'#d6453d'],[0,0,-1.8,'#f5f2e8']]);
flagFore.position.set(0,11.5,4); shipGroup.add(flagFore);

// rigging
const rigPts = [];
const R = (a,b)=>{ rigPts.push(a[0],a[1],a[2],b[0],b[1],b[2]); };
R([0,13.5,-3],[0,4.7,15]);  R([0,13.5,-3],[0,3.7,-11]); R([0,13.5,-3],[-4,10,-3]);
R([0,13.5,-3],[4,10,-3]);   R([0,13.5,-3],[0,11.3,4]);  R([0,13.5,-3],[-3,3.7,-6]);
R([0,13.5,-3],[3,3.7,-6]);  R([0,11.3,4],[0,4.7,15]);   R([0,11.3,4],[-3,9,4]);
R([0,11.3,4],[3,9,4]);      R([0,11.3,4],[-2,3.7,8]);   R([0,11.3,4],[2,3.7,8]);
const rigGeo = new THREE.BufferGeometry();
rigGeo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(rigPts),3));
shipGroup.add(new THREE.LineSegments(rigGeo, new THREE.LineBasicMaterial({color:0x2b2118})));

/* ============ Crane hook + cable ============ */
const hookGroup = new THREE.Group();
hookGroup.position.set(14,13.5,-9);
scene.add(hookGroup);
const hookLineGeo = new THREE.BufferGeometry();
hookLineGeo.setAttribute('position', new THREE.BufferAttribute(new Float32Array([0,0,0, 0,-4.3,0]),3));
hookGroup.add(new THREE.Line(hookLineGeo, new THREE.LineBasicMaterial({color:0x2b2118})));
for(let i=-1;i<=1;i++){
  const m = new THREE.Mesh(new THREE.BoxGeometry(0.92,0.92,0.92), new THREE.MeshLambertMaterial({color:0x3a6ea8}));
  m.position.set(i,-5,0); m.castShadow = true; hookGroup.add(m);
}
const hookMesh = new THREE.Mesh(new THREE.BoxGeometry(0.5,0.5,0.5), new THREE.MeshLambertMaterial({color:0x2b2118}));
hookMesh.position.set(0,-4.4,0); hookGroup.add(hookMesh);
const craneCableGeo = new THREE.BufferGeometry();
craneCableGeo.setAttribute('position', new THREE.BufferAttribute(new Float32Array([14,12.5,-20, 14,13.5,-9]),3));
scene.add(new THREE.Line(craneCableGeo, new THREE.LineBasicMaterial({color:0x2b2118})));

/* ============ Rope moorings ============ */
function makeRope(){
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(12*3),3));
  const line = new THREE.Line(geo, new THREE.LineBasicMaterial({color:0xd8c49a}));
  line.frustumCulled = false; scene.add(line); return line;
}
const ropeBow = makeRope(), ropeStern = makeRope();
const bowBollard = new THREE.Vector3(5,3.4,5), sternBollard = new THREE.Vector3(5,3.4,-11);

/* ============ Beam / sun / lamp ============ */
function glowTexture(){
  const c = document.createElement('canvas'); c.width=c.height=128;
  const g = c.getContext('2d');
  const gr = g.createRadialGradient(64,64,0,64,64,64);
  gr.addColorStop(0,'rgba(255,255,255,1)'); gr.addColorStop(0.25,'rgba(255,255,255,.55)'); gr.addColorStop(1,'rgba(255,255,255,0)');
  g.fillStyle = gr; g.fillRect(0,0,128,128);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}
const glowTex = glowTexture();
const beamMat = new THREE.MeshBasicMaterial({color:0xffe9a8, transparent:true, opacity:0.18, side:THREE.DoubleSide, blending:THREE.AdditiveBlending, depthWrite:false, fog:false});
const beamGroup = new THREE.Group();
beamGroup.position.set(-17.5,13.5,-19.5);
scene.add(beamGroup);
{
  const cone = new THREE.ConeGeometry(2.6, 16, 14, 1, true); cone.translate(0,-8,0);
  const c1 = new THREE.Mesh(cone, beamMat); c1.rotation.z = Math.PI/2;
  const c2 = new THREE.Mesh(cone, beamMat); c2.rotation.z = -Math.PI/2;
  beamGroup.add(c1,c2);
}
const lampGlow = new THREE.Sprite(new THREE.SpriteMaterial({map:glowTex, color:0xffd98a, transparent:true, opacity:0.85, blending:THREE.AdditiveBlending, depthWrite:false, fog:false}));
lampGlow.scale.set(5,5,1); lampGlow.position.set(-17.5,13.5,-19.5); scene.add(lampGlow);

const sunMat = new THREE.MeshBasicMaterial({color:0xffdf7e, fog:false});
const sunCluster = new THREE.Group();
for(let j=-1;j<=1;j++)for(let i=-1;i<=1;i++){
  const m = new THREE.Mesh(new THREE.BoxGeometry(2.3,2.3,2.3), sunMat);
  m.position.set(i*2.5, j*2.5, 0); sunCluster.add(m);
}
sunCluster.position.set(40,30,-130); scene.add(sunCluster);
const sunGlow = new THREE.Sprite(new THREE.SpriteMaterial({map:glowTex, color:0xffdf7e, transparent:true, opacity:0.85, blending:THREE.AdditiveBlending, depthWrite:false, fog:false}));
sunGlow.scale.set(20,20,1); sunGlow.position.copy(sunCluster.position); scene.add(sunGlow);

/* ============ Clouds ============ */
const cloudMat = new THREE.MeshLambertMaterial({color:0xffffff});
const cloudOffsets = [[0,0,0],[1,0,0],[-1,0,0],[2,0,0],[-2,0,0],[1,1,0],[-1,1,0],[0,2,0]];
const clouds = [
  {x:-30,y:34,z:-30,s:1.0,speed:1.3},
  {x:4,  y:36,z:-38,s:1.15,speed:0.9},
  {x:30, y:33,z:-26,s:0.9,speed:1.5},
  {x:-16,y:35,z:14, s:1.05,speed:1.1},
  {x:22, y:37,z:10, s:1.2,speed:0.8},
];
const cloudMesh = new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1), cloudMat, clouds.length*8);
{
  const m = new THREE.Matrix4();
  let idx=0;
  for(const c of clouds) for(let oi=0;oi<8;oi++){
    const o = cloudOffsets[oi]; const scale = 2.1*c.s;
    m.makeTranslation(c.x+o[0]*scale, c.y+o[1]*scale, c.z+o[2]*scale);
    m.scale(new THREE.Vector3(scale,scale,scale));
    cloudMesh.setMatrixAt(idx,m);
    cloudMesh.setColorAt(idx, jitter('#ffffff',0.04));
    idx++;
  }
  cloudMesh.instanceMatrix.needsUpdate = true; cloudMesh.instanceColor.needsUpdate = true;
}
cloudMesh.castShadow = false; scene.add(cloudMesh);

/* ============ Birds ============ */
function makeBird(scale=1){
  const g = new THREE.Group();
  const mat = new THREE.MeshLambertMaterial({color:0xf2efe6});
  const body = new THREE.Mesh(new THREE.BoxGeometry(0.4,0.3,0.95), mat); g.add(body);
  const wingGeoL = new THREE.BoxGeometry(1.05,0.13,0.45).translate(-0.55,0,0);
  const wingGeoR = new THREE.BoxGeometry(1.05,0.13,0.45).translate(0.55,0,0);
  const wingL = new THREE.Mesh(wingGeoL, mat); const wingR = new THREE.Mesh(wingGeoR, mat);
  g.add(wingL); g.add(wingR); g.scale.setScalar(scale);
  return {g, wingL, wingR};
}
const birds = [
  Object.assign(makeBird(1.0), {cx:6, cz:-2, y:16, r:10, speed:0.28, phase:0}),
  Object.assign(makeBird(0.8), {cx:0, cz:-4, y:19, r:13, speed:0.22, phase:2.1}),
  Object.assign(makeBird(0.9), {cx:14,cz:0, y:14.5, r:8, speed:0.32, phase:4.2}),
];
birds.forEach(b=>scene.add(b.g));

/* ============ Buoys & rowboat ============ */
function makeBuoy(x,z,phase){
  const g = new THREE.Group();
  const mRed = new THREE.MeshLambertMaterial({color:0xd6453d});
  const mWhite = new THREE.MeshLambertMaterial({color:0xf5f2e8});
  const b1 = new THREE.Mesh(new THREE.BoxGeometry(0.8,0.8,0.8), mRed); b1.position.y=0;
  const b2 = new THREE.Mesh(new THREE.BoxGeometry(0.6,0.6,0.6), mWhite); b2.position.y=0.7;
  const b3 = new THREE.Mesh(new THREE.BoxGeometry(0.4,0.4,0.4), mRed); b3.position.y=1.25;
  b1.castShadow = b2.castShadow = b3.castShadow = true;
  g.add(b1,b2,b3); g.position.set(x,0,z); scene.add(g);
  return {g, phase};
}
const buoys = [makeBuoy(-16,9,0), makeBuoy(-4,13,2.2), makeBuoy(24,11,4.4)];

const boat = new THREE.Group();
{
  const wood = new THREE.MeshLambertMaterial({color:0x7a4a2a});
  const widths=[1,2,2,2,1];
  for(let i=0;i<5;i++){
    const z=i-2, w=widths[i];
    for(let x=-Math.floor(w/2);x<=Math.ceil(w/2)-1;x++){
      const m = new THREE.Mesh(new THREE.BoxGeometry(0.9,0.7,0.9), wood);
      m.position.set(x*0.95,0,z*0.95); m.castShadow = true; boat.add(m);
    }
  }
  const bench = new THREE.Mesh(new THREE.BoxGeometry(1.6,0.22,0.8), new THREE.MeshLambertMaterial({color:0xd8c49a}));
  bench.position.set(0,0.72,0); bench.castShadow = true; boat.add(bench);
}
boat.position.set(-10,0.1,9); scene.add(boat);

/* ============ Presets (day / sunset) ============ */
const PRESETS = {
  day:  { sky:[[0,'#2f6fd0'],[0.5,'#7fb9e6'],[1,'#d9ecf3']], fog:0xcfe6ef, fogNear:70, fogFar:170,
          hemiSky:0xbfe0ff, hemiGround:0x6b7a52, hemiInt:0.75, sunColor:0xfff1d0, sunInt:1.55,
          sunPos:[40,50,26], exposure:1.12, lamp:0.5, sunCluster:[40,30,-130], sunClusterColor:0xffdf7e, cloudTint:0xffffff },
  dusk: { sky:[[0,'#2e2a4f'],[0.45,'#7a4a6b'],[0.75,'#d96b4a'],[1,'#f2b366']], fog:0xe0915c, fogNear:55, fogFar:145,
          hemiSky:0x8a6a92, hemiGround:0x3a3436, hemiInt:0.5, sunColor:0xffa04e, sunInt:1.15,
          sunPos:[30,14,-28], exposure:1.05, lamp:2.4, sunCluster:[34,14,-120], sunClusterColor:0xff9e5e, cloudTint:0xf0c0a8 }
};
let mode = 'day';
function applyPreset(p){
  scene.background = skyTexture(p.sky);
  scene.fog.color.set(p.fog); scene.fog.near=p.fogNear; scene.fog.far=p.fogFar;
  hemi.color.set(p.hemiSky); hemi.groundColor.set(p.hemiGround); hemi.intensity=p.hemiInt;
  sun.color.set(p.sunColor); sun.intensity=p.sunInt; sun.position.set(...p.sunPos);
  renderer.toneMappingExposure = p.exposure;
  lampLight.intensity = p.lamp;
  sunCluster.position.set(...p.sunCluster); sunGlow.position.copy(sunCluster.position);
  sunMat.color.set(p.sunClusterColor); sunGlow.material.color.set(p.sunClusterColor);
  cloudMat.color.set(p.cloudTint);
  beamMat.color.set(p === PRESETS.dusk ? 0xffd27a : 0xffe9a8);
}
scene.background = skyTexture(PRESETS.day.sky);
applyPreset(PRESETS.day);

/* ============ Orbit controls ============ */
const cam = { theta:0.62, phi:1.03, radius:52, target:new THREE.Vector3(0,3.5,-4),
              tTheta:0.62, tPhi:1.03, tRadius:52, tTarget:new THREE.Vector3(0,3.5,-4) };
function resetOrbit(){ cam.tTheta=0.62; cam.tPhi=1.03; cam.tRadius=52; cam.tTarget.set(0,3.5,-4); }
function applyCamera(dt){
  const k = dt===0 ? 1 : (1-Math.exp(-dt*5));
  cam.theta += (cam.tTheta-cam.theta)*k;
  cam.phi += (cam.tPhi-cam.phi)*k;
  cam.radius += (cam.tRadius-cam.radius)*k;
  cam.target.lerp(cam.tTarget,k);
  const sp=Math.sin(cam.phi), cp=Math.cos(cam.phi);
  camera.position.set(cam.target.x + cam.radius*sp*Math.sin(cam.theta),
                      cam.target.y + cam.radius*cp,
                      cam.target.z + cam.radius*sp*Math.cos(cam.theta));
  camera.lookAt(cam.target);
}
applyCamera(0);
let autoRotate = true, lastInteraction = 0;
const dom = renderer.domElement;
const pointers = new Map();
let panning = false, lastX = 0, lastY = 0, lastPinch = 0;
dom.addEventListener('pointerdown', e=>{
  dom.setPointerCapture(e.pointerId);
  pointers.set(e.pointerId, {x:e.clientX, y:e.clientY});
  if(pointers.size===1){ panning = (e.button===2 || e.shiftKey); lastX=e.clientX; lastY=e.clientY; }
  lastPinch = 0; lastInteraction = performance.now();
});
dom.addEventListener('pointermove', e=>{
  if(!pointers.has(e.pointerId)) return;
  const prev = pointers.get(e.pointerId);
  const dx = e.clientX-prev.x, dy = e.clientY-prev.y;
  pointers.set(e.pointerId, {x:e.clientX, y:e.clientY});
  lastInteraction = performance.now();
  if(pointers.size===1){
    if(panning){
      const k = cam.radius*0.0016;
      const right = new THREE.Vector3().setFromMatrixColumn(camera.matrix,0);
      const up = new THREE.Vector3().setFromMatrixColumn(camera.matrix,1);
      cam.tTarget.addScaledVector(right,-dx*k).addScaledVector(up,dy*k);
      cam.tTarget.x = THREE.MathUtils.clamp(cam.tTarget.x,-24,24);
      cam.tTarget.y = THREE.MathUtils.clamp(cam.tTarget.y,0.5,14);
      cam.tTarget.z = THREE.MathUtils.clamp(cam.tTarget.z,-28,18);
    } else {
      cam.tTheta -= dx*0.0055;
      cam.tPhi = THREE.MathUtils.clamp(cam.tPhi + dy*0.0055, 0.18, 1.42);
    }
  } else if(pointers.size===2){
    const [a,b] = [...pointers.values()];
    const d = Math.hypot(a.x-b.x, a.y-b.y);
    if(lastPinch>0) cam.tRadius = THREE.MathUtils.clamp(cam.tRadius*lastPinch/d, 20, 95);
    lastPinch = d;
  }
});
function endPointer(e){ pointers.delete(e.pointerId); lastPinch=0; if(pointers.size===0) panning=false; }
dom.addEventListener('pointerup', endPointer);
dom.addEventListener('pointercancel', endPointer);
dom.addEventListener('wheel', e=>{
  e.preventDefault(); lastInteraction = performance.now();
  cam.tRadius = THREE.MathUtils.clamp(cam.tRadius*(1+e.deltaY*0.0011), 20, 95);
}, {passive:false});
dom.addEventListener('contextmenu', e=>e.preventDefault());
dom.addEventListener('dblclick', resetOrbit);

/* ============ UI ============ */
const btnMode = document.getElementById('btnMode');
const btnRotate = document.getElementById('btnRotate');
const btnReset = document.getElementById('btnReset');
btnMode.addEventListener('click', ()=>{
  mode = mode==='day' ? 'dusk' : 'day';
  applyPreset(PRESETS[mode]);
  btnMode.textContent = mode==='day' ? '🌇 Sunset' : '☀ Day';
});
btnRotate.addEventListener('click', ()=>{
  autoRotate = !autoRotate;
  btnRotate.classList.toggle('on', autoRotate);
  lastInteraction = performance.now();
});
btnReset.addEventListener('click', resetOrbit);

/* ============ Animation ============ */
const clock = new THREE.Clock();
const tmpV = new THREE.Vector3(), tmpS = new THREE.Vector3(), tmpM = new THREE.Matrix4(), tmpQ = new THREE.Quaternion();
const tmpP = new THREE.Vector3(), tmpA = new THREE.Vector3();
function shipLocalToWorld(x,y,z, out){
  const c = Math.cos(shipGroup.rotation.y), s = Math.sin(shipGroup.rotation.y);
  out.set(x*c + z*s, y, -x*s + z*c).add(shipGroup.position);
  return out;
}
function updateRope(line, worldPoint, bollard){
  const pos = line.geometry.attributes.position;
  for(let i=0;i<12;i++){
    const t = i/11;
    tmpP.lerpVectors(worldPoint, bollard, t);
    tmpP.y -= Math.sin(t*Math.PI)*0.7;
    pos.setXYZ(i, tmpP.x, tmpP.y, tmpP.z);
  }
  pos.needsUpdate = true;
}
function animate(){
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  for(let i=0;i<waterCells.length;i++){
    const c = waterCells[i];
    const y = Math.sin(t*c.speed + c.x*0.33 + c.z*0.42)*c.amp;
    tmpV.set(c.x,y,c.z); tmpM.compose(tmpV, tmpQ, tmpS.set(1,1,1));
    waterMesh.setMatrixAt(i, tmpM);
  }
  waterMesh.instanceMatrix.needsUpdate = true;

  shipGroup.position.y = Math.sin(t*0.85)*0.22;
  shipGroup.rotation.z = Math.sin(t*0.62+0.8)*0.018;
  shipGroup.rotation.x = Math.sin(t*0.74)*0.014;
  flagMain.rotation.y = Math.sin(t*3.1)*0.4;
  flagFore.rotation.y = Math.sin(t*3.6+1)*0.4;

  beamGroup.rotation.y = t*0.45;
  hookGroup.rotation.x = Math.sin(t*0.9+0.5)*0.1;
  hookGroup.rotation.z = Math.sin(t*0.63)*0.07;

  for(const b of birds){
    const a = t*b.speed + b.phase;
    b.g.position.set(b.cx + Math.cos(a)*b.r, b.y + Math.sin(t*1.7+b.phase)*0.6, b.cz + Math.sin(a)*b.r);
    b.g.rotation.y = -a;
    const f = Math.sin(t*7 + b.phase)*0.55 + 0.12;
    b.wingL.rotation.z = -f; b.wingR.rotation.z = f;
  }

  for(let ci=0;ci<clouds.length;ci++){
    const c = clouds[ci];
    c.x += c.speed*dt; if(c.x>48) c.x=-48;
    const scale = 2.1*c.s;
    for(let oi=0;oi<8;oi++){
      const o = cloudOffsets[oi];
      tmpV.set(c.x+o[0]*scale, c.y+o[1]*scale, c.z+o[2]*scale);
      tmpM.compose(tmpV, tmpQ, tmpS.set(scale,scale,scale));
      cloudMesh.setMatrixAt(ci*8+oi, tmpM);
    }
  }
  cloudMesh.instanceMatrix.needsUpdate = true;

  for(const bu of buoys){
    bu.g.position.y = Math.sin(t*1.2 + bu.phase)*0.25;
    bu.g.rotation.z = Math.sin(t*0.9 + bu.phase)*0.14;
    bu.g.rotation.x = Math.cos(t*1.05 + bu.phase)*0.1;
  }

  boat.position.y = 0.1 + Math.sin(t*1.05+2)*0.18;
  boat.rotation.z = Math.sin(t*0.9+2)*0.05;
  boat.rotation.x = Math.sin(t*0.8+1.5)*0.03;

  shipLocalToWorld(0,4.3,9,tmpA); updateRope(ropeBow, tmpA, bowBollard);
  shipLocalToWorld(0,4.3,-6,tmpA); updateRope(ropeStern, tmpA, sternBollard);

  if(autoRotate && performance.now()-lastInteraction>3500) cam.tTheta += dt*0.07;

  applyCamera(dt);
  renderer.render(scene, camera);
}
animate();

window.addEventListener('resize', ()=>{
  camera.aspect = innerWidth/innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
</script>
</body>
</html>
```

**What you get in the scene:**

- **A two-masted sailing ship** with stepped voxel hull, cream trim, plank decks, stern/bow castles, cabin, billowing voxel sails, jib, bowsprit, rigging, animated flags, and mooring ropes that sag and sway as the hull bobs
- **A harbor**: stone quay with deck tiles and edge stripe, wooden pier with safety line, pilings, bollards, crates and barrels, plus grass, trees, a red-striped **lighthouse** with a rotating light beam, a yellow **crane** with a swinging container, two houses, a shed, containers, and lamp posts
- **Living water**: ~2,800 animated voxel waves with foam near shore and pier, bobbing buoys, and a drifting rowboat
- **Sky**: drifting clouds, flapping seagulls, voxel sun, and a day/sunset toggle that re-lights the whole scene (plus lamp glow at dusk)

**Controls:** drag to orbit · scroll to zoom · right-drag (or Shift+drag) to pan · double-click to reset · buttons for sunset, auto-rotate, and reset. Everything is one self-contained HTML file using only a Three.js CDN import — paste it into a `.html` file and open it in Chrome.