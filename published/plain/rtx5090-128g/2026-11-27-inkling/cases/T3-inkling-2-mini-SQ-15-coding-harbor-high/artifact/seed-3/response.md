Here's a complete, self-contained voxel harbor scene — ship bobbing in the harbor, animated water, gulls, clouds, a lighthouse with a rotating beam, all orbitable with the mouse. Paste it into one `.html` file and open in Chrome:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>A Sailing Ship Calling at a Harbor — Voxel Art</title>
<style>
  html,body{margin:0;height:100%;overflow:hidden;background:#0e1a24;}
  #hud{position:fixed;top:18px;left:18px;z-index:10;pointer-events:none;color:#fff;
       font-family:Georgia,'Times New Roman',serif;text-shadow:0 2px 8px rgba(0,0,0,.5);}
  #hud h1{font-size:24px;margin:0;letter-spacing:2px;}
  #hud p{font-size:12px;margin:6px 0 0;opacity:.9;letter-spacing:.5px;}
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
<div id="hud"><h1>⛵ HARBOR CALL</h1><p>Drag to orbit &nbsp;·&nbsp; Scroll to zoom &nbsp;·&nbsp; Right-drag to pan</p></div>
<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* ---------- renderer ---------- */
const renderer = new THREE.WebGLRenderer({ antialias:true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.08;
document.body.appendChild(renderer.domElement);

/* ---------- scene & sky ---------- */
const scene = new THREE.Scene();
const skyCanvas = document.createElement('canvas');
skyCanvas.width = 2; skyCanvas.height = 512;
const ctx = skyCanvas.getContext('2d');
const grad = ctx.createLinearGradient(0,0,0,512);
grad.addColorStop(0.0,'#5f9cc4');
grad.addColorStop(0.55,'#a9c9d8');
grad.addColorStop(0.82,'#e8dfc2');
grad.addColorStop(1.0,'#efe6c8');
ctx.fillStyle = grad; ctx.fillRect(0,0,2,512);
const skyTex = new THREE.CanvasTexture(skyCanvas);
skyTex.colorSpace = THREE.SRGBColorSpace;
scene.background = skyTex;
scene.fog = new THREE.Fog(0xd9dcc0, 95, 235);

const camera = new THREE.PerspectiveCamera(50, innerWidth/innerHeight, 0.1, 600);
camera.position.set(30, 21, 37);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 3.5, -2);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.maxPolarAngle = Math.PI * 0.49;
controls.minDistance = 14;
controls.maxDistance = 130;

/* ---------- lights ---------- */
scene.add(new THREE.HemisphereLight(0xcfe0ee, 0x7a6a4a, 0.85));
const sun = new THREE.DirectionalLight(0xfff1d6, 1.5);
sun.position.set(-42, 52, -28);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -58; sun.shadow.camera.right = 58;
sun.shadow.camera.top = 58;  sun.shadow.camera.bottom = -58;
sun.shadow.camera.near = 10; sun.shadow.camera.far = 170;
sun.shadow.bias = -0.0005;   sun.shadow.normalBias = 0.5;
scene.add(sun); scene.add(sun.target);
const fill = new THREE.DirectionalLight(0x9fb8cc, 0.35);
fill.position.set(40, 25, 45);
scene.add(fill);

/* ---------- voxel helpers ---------- */
const staticVoxels = [];
const shipVoxels = [];
function v(list,x,y,z,c){ list.push({x:Math.round(x), y:Math.round(y), z:Math.round(z), c}); }
function box(list,x0,y0,z0,x1,y1,z1,c){
  for(let x=x0;x<=x1;x++) for(let y=y0;y<=y1;y++) for(let z=z0;z<=z1;z++) v(list,x,y,z,c);
}

/* ---------- palette ---------- */
const sandC=0xe3d0a0, dirtC=0xc9a86e, dirtDark=0x9c7a52, grassC=0x5da24a, grassD=0x4c8a3e,
      rockC=0x8b8f94, rockD=0x70757c, woodC=0x8a6134, woodD=0x6b4a28, plankC=0x9c7040;

/* ---------- land (harbor shore) ---------- */
for(let x=-38;x<=38;x++){
  for(let z=-30;z<=-12;z++){
    let top, topColor;
    if(z>=-15){ top=1; topColor=sandC; }
    else if(z>=-20){ top=2; topColor=grassC; }
    else if(z>=-26){ top=3; topColor=grassC; }
    else { top=4; topColor=(Math.abs(x)>26)?rockC:grassC; }
    if((x===-30&&z===-13)||(x===26&&z===-13)||(x===-28&&z===-12)) topColor=rockC;
    for(let y=-2;y<=top;y++){
      if(y===top) v(staticVoxels,x,y,z,topColor);
      else if(y>=0) v(staticVoxels,x,y,z, z>=-15?sandC:dirtC);
      else v(staticVoxels,x,y,z,dirtDark);
    }
  }
}
/* rock outcrops on back band */
box(staticVoxels,-36,4,-25,-34,4,-23,rockC);
box(staticVoxels, 30,4,-27, 32,4,-25,rockD);

/* trees */
function tree(x,z,top){
  box(staticVoxels,x,top+1,z,x,top+2,z,0x6b4a2a);
  box(staticVoxels,x-1,top+3,z-1,x+1,top+4,z+1,0x3f7d36);
  for(const dx of [-1,1]) for(const dz of [-1,1]) v(staticVoxels,x+dx,top+4,z+dz,0x35692e);
  box(staticVoxels,x-1,top+5,z-1,x+1,top+5,z+1,0x4c8a3e);
}
function pine(x,z,top){
  box(staticVoxels,x,top+1,z,x,top+2,z,0x5d3f28);
  box(staticVoxels,x-1,top+3,z-1,x+1,top+4,z+1,0x2f6b3a);
  v(staticVoxels,x,top+5,z,0x3f7d36);
}
tree(-26,-24,3); tree(-20,-26,3); tree(6,-26,3); tree(26,-25,3);
tree(-14,-25,3); tree(8,-18,2);   tree(26,-18,2);
pine(-31,-28,4); pine(33,-28,4);

/* warehouse */
for(let x=10;x<=16;x++) for(let y=3;y<=5;y++) for(let z=-23;z<=-21;z++){
  if(z===-21 && x===13 && y<=4) v(staticVoxels,x,y,z,0x2b3a4a);        // door
  else if(z===-21 && (x===11||x===15) && y===4) v(staticVoxels,x,y,z,0x2b3a4a); // windows
  else v(staticVoxels,x,y,z,0xe8dcc0);
}
box(staticVoxels,9,6,-24,17,6,-20,0x9c4a32);
box(staticVoxels,9,7,-23,17,7,-21,0x8a3f2d);
box(staticVoxels,10,8,-22,16,8,-22,0x8a3f2d);

/* breakwaters */
for(let x=-36;x<=-21;x++){
  const h=1+Math.abs(x*7)%3;
  box(staticVoxels,x,0,-9,x,h,-9,(x%2===0)?rockC:rockD);
}
for(let x=21;x<=30;x++){
  const h=1+Math.abs(x*7)%3;
  box(staticVoxels,x,0,-9,x,h,-9,(x%2===0)?rockD:rockC);
}

/* pier / dock */
for(let x=-11;x<=-5;x++) for(let z=-12;z<=8;z++)
  v(staticVoxels,x,3,z,(z%2===0)?plankC:woodC);
for(let z=-12;z<=8;z++){
  v(staticVoxels,-11,2,z,woodD); v(staticVoxels,-5,2,z,woodD);
}
for(const z of [-11,-6,-1,4,8]){
  box(staticVoxels,-11,-1,z,-11,2,z,0x5d3f28);
  box(staticVoxels,-5,-1,z,-5,2,z,0x5d3f28);
}
box(staticVoxels,-10,4,-9,-9,5,-8,0x9c7040);          // crate
box(staticVoxels,-7,4,-2,-6,5,-1,0x8a6134);           // crate
v(staticVoxels,-10,4,1,0x3a2c20); v(staticVoxels,-10,5,1,0x7a5230); v(staticVoxels,-10,6,1,0x3a2c20);   // barrel
v(staticVoxels,-10,4,6,0x3a2c20); v(staticVoxels,-10,5,6,0x7a5230); v(staticVoxels,-10,6,6,0x3a2c20);   // barrel
box(staticVoxels,-6,4,7,-6,5,7,0x2c2c2e);
box(staticVoxels,-6,4,-11,-6,5,-11,0x2c2c2e);
/* lamp posts */
for(const [lx,lz] of [[-10,-4],[-6,4]]){
  box(staticVoxels,lx,4,lz,lx,6,lz,0x3a3f45);
  v(staticVoxels,lx,7,lz,0xffe08a);
}
/* crane at dock tip */
box(staticVoxels,-9,4,4,-7,4,6,0x6b4a28);
box(staticVoxels,-9,4,3,-7,5,4,0x3a3f45);
box(staticVoxels,-8,5,5,-8,9,5,0x5d3f28);
v(staticVoxels,-8,8,6,0x5d3f28); v(staticVoxels,-8,7,7,0x5d3f28);
v(staticVoxels,-8,6,8,0x5d3f28); v(staticVoxels,-8,5,9,0x5d3f28);
v(staticVoxels,-8,4,9,0x3a2c20); v(staticVoxels,-8,3,9,0x2c2c2e);

/* lighthouse (on east breakwater) */
box(staticVoxels,31,0,-11,35,2,-7,rockD);
for(let y=4;y<=11;y++){
  const c=(Math.floor((y-4)/2)%2===0)?0xf2ede2:0xd8443c;
  box(staticVoxels,32,y,-10,34,y,-8,c);
}
box(staticVoxels,31,12,-11,35,12,-7,0x3a3f45);
for(const [px,pz] of [[31,-11],[35,-11],[31,-7],[35,-7]]) v(staticVoxels,px,13,pz,0x2c2c2e);
box(staticVoxels,32,15,-10,34,15,-8,0x2c2c2e);
v(staticVoxels,33,16,-9,0x2c2c2e);

/* ---------- static instanced mesh ---------- */
const staticMesh = new THREE.InstancedMesh(
  new THREE.BoxGeometry(1,1,1),
  new THREE.MeshLambertMaterial({color:0xffffff}),
  staticVoxels.length
);
staticMesh.frustumCulled = false;
staticMesh.castShadow = true; staticMesh.receiveShadow = true;
{
  const m = new THREE.Matrix4(), col = new THREE.Color();
  staticVoxels.forEach((vox,i)=>{
    m.makeTranslation(vox.x,vox.y,vox.z);
    staticMesh.setMatrixAt(i,m);
    staticMesh.setColorAt(i,col.set(vox.c));
  });
  staticMesh.instanceColor.needsUpdate = true;
}
scene.add(staticMesh);

/* ---------- voxel sun (separate, no shadow) ---------- */
const sunGroup = new THREE.Group();
const sunMat = new THREE.MeshBasicMaterial({color:0xffd97a});
const sunCore = new THREE.Mesh(new THREE.BoxGeometry(3,3,3), sunMat);
sunCore.position.set(-30,23,-35); sunGroup.add(sunCore);
for(const [rx,ry,rz] of [[-33,23,-35],[-27,23,-35],[-30,26,-35],[-30,20,-35],[-30,23,-38],[-30,23,-32]]){
  const ray = new THREE.Mesh(new THREE.BoxGeometry(0.8,0.8,0.8), sunMat);
  ray.position.set(rx,ry,rz); sunGroup.add(ray);
}
scene.add(sunGroup);

/* ---------- ship ---------- */
const shipGroup = new THREE.Group();
shipGroup.position.set(4, 0.35, 3);

const hwMap = {-8:2.3,-7:2.8,-6:3.0,-5:3.15,-4:3.15,-3:3.1,-2:3.1,-1:3.0,0:3.0,1:2.9,2:2.8,3:2.6,4:2.35,5:2.05,6:1.6,7:1.05,8:0.4};
for(let x=-8;x<=8;x++){
  const hw = hwMap[x];
  const nzFull = Math.round(hw);
  const nzKeel = Math.max(1, Math.round(hw*0.5));
  const nzMid  = Math.max(1, Math.round(hw*0.82));
  for(let z=-nzKeel;z<=nzKeel;z++){ v(shipVoxels,x,-2,z,0x33241a); v(shipVoxels,x,-1,z,0x33241a); }
  for(let z=-nzMid;z<=nzMid;z++){ v(shipVoxels,x,0,z,0x4e3018); v(shipVoxels,x,1,z,0x59371f); }
  for(let z=-nzFull;z<=nzFull;z++){ v(shipVoxels,x,2,z,0x6b4226); }
  if(nzFull>=1){
    v(shipVoxels,x,3,nzFull,0xd9a05b); v(shipVoxels,x,3,-nzFull,0xd9a05b);
    for(let z=-(nzFull-1);z<=nzFull-1;z++) v(shipVoxels,x,3,z,(x%2===0)?0xc8a05e:0xb8905a);
  } else v(shipVoxels,x,3,0,0xd9a05b);
}
// stern cap
for(const z of [-1,0,1]) v(shipVoxels,-8,3,z,0xd9a05b);
// stern castle
box(shipVoxels,-7,4,-2,-3,5,2,0xe8dcc0);
for(const z of [-1,0,1]) v(shipVoxels,-3,5,z,0x2b3a4a);
for(const x of [-6,-4]){ v(shipVoxels,x,5,2,0x2b3a4a); v(shipVoxels,x,5,-2,0x2b3a4a); }
box(shipVoxels,-7,6,-2,-3,6,2,0x9c4a32);
v(shipVoxels,-5,7,0,0xffe08a);
// railing posts (skip castle zone)
for(let x=-2;x<=7;x+=2){
  const nz=Math.round(hwMap[x]); if(nz<1) continue;
  v(shipVoxels,x,4,nz,0xd9a05b); v(shipVoxels,x,4,-nz,0xd9a05b);
}
// masts
box(shipVoxels,-1,4,0,-1,11,0,0x5d3f28);
box(shipVoxels,4,4,0,4,9,0,0x5d3f28);
// yards
for(let z=-3;z<=3;z++){ if(z!==0) v(shipVoxels,-1,7,z,0x5d3f28); }
for(let z=-2;z<=2;z++){ if(z!==0) v(shipVoxels,-1,9,z,0x5d3f28); }
for(let z=-2;z<=2;z++){ if(z!==0) v(shipVoxels,4,6,z,0x5d3f28); }
for(let z=-1;z<=1;z++){ if(z!==0) v(shipVoxels,4,8,z,0x5d3f28); }
// sails
for(let y=4;y<=6;y++){
  const xx=(y===5)?-3:-2;
  for(let z=-3;z<=3;z++) v(shipVoxels,xx,y,z,(y===5)?0xead9bd:0xf3e9d2);
}
for(let y=8;y<=10;y++) for(let z=-2;z<=2;z++) v(shipVoxels,-2,y,z,(y===9)?0xd8443c:0xf3e9d2);
for(let y=4;y<=6;y++){
  const xx=(y===5)?2:3;
  for(let z=-2;z<=2;z++) v(shipVoxels,xx,y,z,(y===5)?0xead9bd:0xf3e9d2);
}
for(let z=-2;z<=2;z++) v(shipVoxels,6,4,z,0xefe4cd);
for(let z=-1;z<=1;z++) v(shipVoxels,6,5,z,0xefe4cd);
v(shipVoxels,6,6,0,0xefe4cd);
// deck crates
v(shipVoxels,2,4,-1,0x9c7040);
v(shipVoxels,0,4,1,0xc9a06b);
// anchor
v(shipVoxels,7,3,2,0x2c2c2e); v(shipVoxels,7,2,2,0x2c2c2e); v(shipVoxels,7,1,2,0x2c2c2e);
v(shipVoxels,6,2,2,0x2c2c2e); v(shipVoxels,8,2,2,0x2c2c2e);
v(shipVoxels,7,1,1,0x2c2c2e); v(shipVoxels,7,1,3,0x2c2c2e);

const shipMesh = new THREE.InstancedMesh(
  new THREE.BoxGeometry(1,1,1),
  new THREE.MeshLambertMaterial({color:0xffffff}),
  shipVoxels.length
);
shipMesh.frustumCulled = false;
shipMesh.castShadow = true; shipMesh.receiveShadow = true;
{
  const m = new THREE.Matrix4(), col = new THREE.Color();
  shipVoxels.forEach((vox,i)=>{
    m.makeTranslation(vox.x,vox.y,vox.z);
    shipMesh.setMatrixAt(i,m);
    shipMesh.setColorAt(i,col.set(vox.c));
  });
  shipMesh.instanceColor.needsUpdate = true;
}
shipGroup.add(shipMesh);

/* rigging */
const rigGeo = new THREE.BufferGeometry().setFromPoints([
  new THREE.Vector3(-1,11,0), new THREE.Vector3(8,4,0),
  new THREE.Vector3(-1,11,0), new THREE.Vector3(-8,4,0),
  new THREE.Vector3(-1,11,0), new THREE.Vector3(-1,3,2.6),
  new THREE.Vector3(-1,11,0), new THREE.Vector3(-1,3,-2.6),
  new THREE.Vector3(4,9,0),  new THREE.Vector3(8,4,0),
  new THREE.Vector3(4,9,0),  new THREE.Vector3(-1,11,0),
  new THREE.Vector3(4,9,0),  new THREE.Vector3(4,3,2.2),
  new THREE.Vector3(4,9,0),  new THREE.Vector3(4,3,-2.2),
]);
shipGroup.add(new THREE.LineSegments(rigGeo, new THREE.LineBasicMaterial({color:0x2e241c})));

/* waving flag */
const flagMeshes = [];
const flagColors = [0xd8443c, 0xf2ede2, 0xd8443c, 0xf2ede2];
for(let i=0;i<4;i++){
  const fm = new THREE.Mesh(new THREE.BoxGeometry(0.95,0.65,0.2),
                           new THREE.MeshLambertMaterial({color:flagColors[i]}));
  fm.position.set(-2.1-i*1.0, 11.05, 0);
  shipGroup.add(fm); flagMeshes.push(fm);
}
scene.add(shipGroup);

/* ---------- water ---------- */
const waterCells = [];
for(let x=-57;x<=57;x+=3) for(let z=-57;z<=57;z+=3) waterCells.push({x,z});
const waterMesh = new THREE.InstancedMesh(
  new THREE.BoxGeometry(3,1.5,3),
  new THREE.MeshLambertMaterial({color:0xffffff}),
  waterCells.length
);
waterMesh.frustumCulled = false;
waterMesh.receiveShadow = true;
{
  const col = new THREE.Color();
  waterCells.forEach((c,i)=>{
    const f = Math.max(0, Math.min(1, (c.z + 12) / (57 + 12)));
    col.copy(new THREE.Color(0x46a0b4)).lerp(new THREE.Color(0x1d5d84), Math.pow(f,0.75));
    col.offsetHSL(0,0,(Math.random()-0.5)*0.05);
    waterMesh.setColorAt(i,col);
  });
  waterMesh.instanceColor.needsUpdate = true;
}
scene.add(waterMesh);

function waveY(x,z,t){
  return 0.05 + Math.sin(x*0.22 + t*1.25)*0.3 + Math.cos(z*0.19 + t*0.95)*0.3;
}

/* ---------- lighthouse lamp & beam ---------- */
const lampLight = new THREE.PointLight(0xffd9a0, 2.4, 50, 2);
lampLight.position.set(33,14,-9);
scene.add(lampLight);
const glassMesh = new THREE.Mesh(new THREE.BoxGeometry(2.4,1.9,2.4),
                                new THREE.MeshBasicMaterial({color:0xffe9a8}));
glassMesh.position.set(33,13.9,-9);
scene.add(glassMesh);
const beamGroup = new THREE.Group();
beamGroup.position.set(33,14,-9);
const beamMat = new THREE.MeshBasicMaterial({color:0xfff0c0, transparent:true, opacity:0.26,
                                              blending:THREE.AdditiveBlending, depthWrite:false});
for(const ang of [0, Math.PI]){
  const geo = new THREE.BoxGeometry(0.8,0.5,12); geo.translate(0,0,6.2);
  const beam = new THREE.Mesh(geo, beamMat);
  beam.rotation.y = ang; beamGroup.add(beam);
}
scene.add(beamGroup);

/* ---------- clouds ---------- */
const clouds = [];
function makeCloud(x,y,z,s,speed){
  const g = new THREE.Group();
  const mat = new THREE.MeshLambertMaterial({color:0xf6f8fa});
  const puffs = [[0,0,0,2.6,1.1,1.5],[-1.6,-0.2,0.2,1.4,0.9,1.1],[1.5,0.1,-0.2,1.5,1.0,1.2],[0.3,0.8,0.2,1.1,0.8,0.9]];
  for(const [px,py,pz,sx,sy,sz] of puffs){
    const m = new THREE.Mesh(new THREE.BoxGeometry(sx*s,sy*s,sz*s), mat);
    m.position.set(px*s,py*s,pz*s); g.add(m);
  }
  g.position.set(x,y,z); scene.add(g);
  clouds.push({g,speed});
}
makeCloud(-20,20,-20,1.5,0.9); makeCloud(10,22,-30,1.3,1.1);
makeCloud(30,20,5,1.4,0.7);   makeCloud(-40,21,5,1.2,1.0); makeCloud(0,23,15,1.4,0.8);

/* ---------- seagulls ---------- */
const gulls = [];
function makeGull(cx,cy,cz,r,speed,phase){
  const g = new THREE.Group();
  const mat = new THREE.MeshLambertMaterial({color:0xf2f5f7});
  const body = new THREE.Mesh(new THREE.BoxGeometry(0.55,0.38,0.95), mat);
  const wingL = new THREE.Mesh(new THREE.BoxGeometry(1.0,0.13,0.5).translate(-0.55,0,0), mat);
  const wingR = new THREE.Mesh(new THREE.BoxGeometry(1.0,0.13,0.5).translate(0.55,0,0), mat);
  wingL.position.set(-0.22,0,0); wingR.position.set(0.22,0,0);
  const beak = new THREE.Mesh(new THREE.BoxGeometry(0.16,0.16,0.34),
                             new THREE.MeshLambertMaterial({color:0xe8a33d}));
  beak.position.set(0,-0.03,0.62);
  g.add(body,wingL,wingR,beak); scene.add(g);
  gulls.push({g,wingL,wingR,cx,cy,cz,r,speed,phase});
}
makeGull(3,13,3,8,0.30,0); makeGull(3,14.5,3,11,0.22,1.7);
makeGull(-8,12,2,6,0.38,3.1); makeGull(12,13,6,7,0.28,4.6);

/* ---------- buoys ---------- */
const buoys = [];
function makeBuoy(x,z,phase){
  const g = new THREE.Group();
  const red = new THREE.Mesh(new THREE.BoxGeometry(1.1,0.8,1.1), new THREE.MeshLambertMaterial({color:0xd8443c}));
  red.position.y = 0.4;
  const white = new THREE.Mesh(new THREE.BoxGeometry(0.9,0.5,0.9), new THREE.MeshLambertMaterial({color:0xf2ede2}));
  white.position.y = 1.05;
  const pole = new THREE.Mesh(new THREE.BoxGeometry(0.3,0.9,0.3), new THREE.MeshLambertMaterial({color:0x3a3f45}));
  pole.position.y = 1.65;
  const lamp = new THREE.Mesh(new THREE.BoxGeometry(0.42,0.42,0.42), new THREE.MeshLambertMaterial({color:0xffe08a}));
  lamp.position.y = 2.2;
  g.add(red,white,pole,lamp);
  g.position.set(x,0,z); scene.add(g);
  buoys.push({g,x,z,phase});
}
makeBuoy(14,2,0); makeBuoy(-14,6,2.1);

/* ---------- rowboat ---------- */
let rowboat;
{
  const g = new THREE.Group();
  const hull = new THREE.Mesh(new THREE.BoxGeometry(4.6,0.8,2.2), new THREE.MeshLambertMaterial({color:0x5d3f28}));
  hull.position.y = 0.55;
  const rimL = new THREE.Mesh(new THREE.BoxGeometry(4.6,0.35,0.35), new THREE.MeshLambertMaterial({color:0x8a6134}));
  rimL.position.set(0,1.05,1.05);
  const rimR = rimL.clone(); rimR.position.z = -1.05;
  const bench = new THREE.Mesh(new THREE.BoxGeometry(1.4,0.3,1.7), new THREE.MeshLambertMaterial({color:0xc8a05e}));
  bench.position.set(-0.6,0.9,0);
  const oar = new THREE.Mesh(new THREE.BoxGeometry(3.2,0.22,0.22), new THREE.MeshLambertMaterial({color:0x8a6134}));
  oar.position.set(0.9,0.95,0); oar.rotation.y = 0.35;
  g.add(hull,rimL,rimR,bench,oar);
  g.position.set(-17,0,3); g.rotation.y = 0.35;
  scene.add(g); rowboat = g;
}

/* ---------- animation ---------- */
const clock = new THREE.Clock();
const wm = new THREE.Matrix4();

function animate(){
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  // water
  for(let i=0;i<waterCells.length;i++){
    const c = waterCells[i];
    wm.makeTranslation(c.x, waveY(c.x,c.z,t), c.z);
    waterMesh.setMatrixAt(i, wm);
  }
  waterMesh.instanceMatrix.needsUpdate = true;

  // ship bobbing
  shipGroup.position.y = 0.35 + Math.sin(t*0.85)*0.25 + Math.cos(t*0.6)*0.12;
  shipGroup.rotation.z = Math.sin(t*0.55)*0.028;
  shipGroup.rotation.x = Math.cos(t*0.7+0.8)*0.02;

  // flag wave
  for(let i=0;i<4;i++){
    flagMeshes[i].position.z = Math.sin(t*6 + i*1.4)*0.45;
    flagMeshes[i].position.y = 11.05 + Math.sin(t*4 + i)*0.06;
  }

  // buoys
  for(const b of buoys){
    b.g.position.y = waveY(b.x,b.z,t) - 0.1;
    b.g.rotation.x = Math.sin(t*1.15 + b.phase)*0.1;
    b.g.rotation.z = Math.cos(t*0.9 + b.phase)*0.1;
  }

  // rowboat
  rowboat.position.y = waveY(-17,3,t) - 0.12;
  rowboat.rotation.z = Math.sin(t*0.8+1.2)*0.05;
  rowboat.rotation.x = Math.cos(t*0.65)*0.04;

  // gulls
  for(const b of gulls){
    const a = t*b.speed + b.phase;
    const x = b.cx + Math.cos(a)*b.r;
    const z = b.cz + Math.sin(a)*b.r;
    const y = b.cy + Math.sin(t*1.7 + b.phase)*0.8;
    b.g.position.set(x,y,z);
    const nx = b.cx + Math.cos(a+0.1)*b.r;
    const nz = b.cz + Math.sin(a+0.1)*b.r;
    b.g.lookAt(nx,y,nz);
    const flap = Math.sin(t*9 + b.phase)*0.55;
    b.wingL.rotation.z = -flap;
    b.wingR.rotation.z =  flap;
  }

  // clouds
  for(const c of clouds){
    c.g.position.x += c.speed*dt;
    if(c.g.position.x > 80) c.g.position.x = -80;
  }

  // lighthouse beam + lamp flicker
  beamGroup.rotation.y = t*0.55;
  lampLight.intensity = 2.1 + Math.sin(t*4)*0.5;

  controls.update();
  renderer.render(scene, camera);
}
animate();

addEventListener('resize', ()=>{
  camera.aspect = innerWidth/innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
</script>
</body>
</html>
```

**What's in the scene**

- **The ship** (built entirely from voxels): tapered hull with golden gunwale trim, plank-textured deck, railing, stern castle with lit amber windows and terracotta roof, two masts with yardarms, cream sails with a red band on the topsail, a billowing jib, rigging lines, anchor, deck crates, and an animated waving flag. It bobs and rolls gently on the waves.
- **The harbor**: sandy beach, grassy hill with pines and oaks, a gabled warehouse, a wooden pier with plank deck, posts, crates, barrels, bollards, lamp posts and a crane with a hook over the water.
- **Harbor dressing**: two rock breakwaters with the entry gap, a striped lighthouse on the east breakwater with a rotating light beam and flickering lamp, bobbing buoys, a floating rowboat, 4 circling seagulls with flapping wings, voxel clouds drifting by, and a voxel sun.
- **Water**: ~1,500 voxel cells animated with two layered sine waves, colored shallow-teal near shore fading to deep blue.

Everything is procedural (no image assets), the whole harbor renders instantly, and OrbitControls let you orbit, zoom and pan with the mouse. Shadows are cast from the sun, so the scene has real depth — and since everything is instanced boxes, it stays fast even at 1080p+.