Here's a complete, single-file voxel harbor scene. Save it as `.html` and open it in Chrome — it renders on load and you can orbit/pan/zoom with the mouse.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sailing Ship Calling at a Harbor — 3D Voxel Scene</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400..800&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
  :root{
    --ink:#0a0c10; --paper:#f3ecdd; --dim:#94a0ad;
    --amber:#f2b45c; --amber2:#e79a3a; --teal:#39c6c0; --red:#e5634b;
  }
  *{box-sizing:border-box;margin:0;padding:0}
  html,body{height:100%}
  body{
    background:#16222e; color:var(--paper);
    font-family:'Space Mono',ui-monospace,monospace;
    overflow:hidden; -webkit-font-smoothing:antialiased;
  }
  #scene{position:fixed;inset:0;z-index:0}
  #scene canvas{display:block;cursor:grab}
  #scene canvas:active{cursor:grabbing}

  .ui{position:fixed;inset:0;z-index:5;pointer-events:none}

  .frame{position:absolute;inset:14px;border:1px solid rgba(255,255,255,.10);border-radius:8px;
    pointer-events:none;
    background:
      linear-gradient(to bottom,rgba(6,10,14,.5),transparent 20%,transparent 78%,rgba(6,10,14,.55)),
      radial-gradient(130% 100% at 78% 18%,transparent 55%,rgba(4,8,12,.5));
  }

  .tl{position:absolute;top:40px;left:44px;max-width:min(52ch,44vw)}
  .eyebrow{font-size:11px;letter-spacing:.34em;text-transform:uppercase;color:var(--amber);font-weight:700}
  .title{font-family:'Bricolage Grotesque',sans-serif;font-weight:800;line-height:.94;
    font-size:clamp(30px,5.4vw,66px);margin:.14em 0 .18em;letter-spacing:-.01em}
  .title em{font-style:normal;color:var(--amber)}
  .sub{font-size:13px;color:var(--dim);max-width:44ch;line-height:1.5}

  .legend{position:absolute;top:40px;right:44px;display:flex;gap:8px 18px;flex-wrap:wrap;
    justify-content:flex-end;max-width:46vw}
  .legend span{display:inline-flex;align-items:center;gap:7px;font-size:11px;
    letter-spacing:.12em;text-transform:uppercase;color:var(--dim)}
  .legend i{width:11px;height:11px;border-radius:3px;box-shadow:0 0 0 1px rgba(0,0,0,.4)}

  .hud{position:absolute;bottom:40px;left:44px;display:flex;gap:10px}
  .btn{pointer-events:auto;font-family:'Space Mono',monospace;font-weight:700;font-size:11px;
    letter-spacing:.14em;text-transform:uppercase;color:var(--paper);background:rgba(255,255,255,.06);
    border:1px solid rgba(255,255,255,.16);padding:9px 13px;border-radius:6px;cursor:pointer;
    transition:.18s ease;display:inline-flex;gap:7px;align-items:center}
  .btn:hover{background:var(--amber);color:#1a1206;border-color:var(--amber);transform:translateY(-2px)}
  .btn:active{transform:translateY(0)}
  .btn.on{background:rgba(57,198,192,.18);border-color:var(--teal);color:var(--teal)}

  .readout{position:absolute;bottom:40px;right:44px;text-align:right;font-size:11px;
    letter-spacing:.16em;text-transform:uppercase;color:var(--dim);line-height:1.9}
  .readout b{color:var(--amber);font-weight:700}

  .hint{position:absolute;bottom:18px;left:50%;transform:translateX(-50%);font-size:11px;
    letter-spacing:.14em;text-transform:uppercase;color:rgba(243,236,221,.45)}

  .vignette{position:absolute;inset:0;pointer-events:none;
    background:radial-gradient(120% 90% at 50% 42%,transparent 58%,rgba(0,0,0,.42))}

  .toast{position:absolute;bottom:96px;left:50%;transform:translate(-50%,10px);opacity:0;
    font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--teal);
    background:rgba(6,10,14,.72);border:1px solid rgba(57,198,192,.45);padding:10px 16px;border-radius:8px;
    transition:.4s ease}
  .toast.show{opacity:1;transform:translate(-50%,0)}

  #loader{position:fixed;inset:0;z-index:20;background:#16222e;display:flex;align-items:center;
    justify-content:center;transition:opacity .8s ease}
  #loader.hidden{opacity:0;pointer-events:none}
  #loader span{font-family:'Bricolage Grotesque',sans-serif;font-weight:700;font-size:clamp(20px,4vw,40px);
    color:var(--amber);letter-spacing:.02em;animation:pulse 1.6s ease-in-out infinite}
  @keyframes pulse{0%,100%{opacity:.35}50%{opacity:1}}

  @media (max-width:640px){
    .tl{top:22px;left:22px;max-width:74vw}
    .legend{top:22px;right:22px;max-width:52vw}
    .hud{bottom:22px;left:22px}
    .readout{bottom:24px;right:22px}
    .hint{display:none}
  }
</style>
</head>
<body>
  <div id="scene"></div>

  <div class="ui">
    <div class="frame"></div>
    <div class="tl">
      <div class="eyebrow">Voxel diorama · golden hour</div>
      <h1 class="title">Calling at<br>a <em>Harbor</em></h1>
      <p class="sub">A three-master glides past the breakwater, sails full of the last warm light,
         and turns her bow toward the quay.</p>
    </div>
    <div class="legend">
      <span><i style="background:#e5634b"></i>Sailing ship</span>
      <span><i style="background:#39c6c0"></i>Lighthouse</span>
      <span><i style="background:#b9a37a"></i>Harbor town</span>
      <span><i style="background:#f2b45c"></i>Breakwater</span>
    </div>
    <div class="hud">
      <button class="btn" id="bOrbit">◐ Auto-orbit</button>
      <button class="btn" id="bTime">☀ Time of day</button>
      <button class="btn" id="bReset">⟲ Reset view</button>
    </div>
    <div class="readout">
      <div>Orbit <b>drag</b> · Pan <b>right-drag</b> · Zoom <b>scroll</b></div>
      <div>Heading <b id="hdg">140°</b> · Bearing <b id="brg">E-NE</b></div>
    </div>
    <div class="hint">drag to look around</div>
    <div class="toast" id="toast"></div>
    <div class="vignette"></div>
  </div>

  <div id="loader"><span>Charting the harbor…</span></div>

<script type="importmap">
{
  "imports": {
    "three": "https://unpkg.com/three@0.161.0/build/three.module.js",
    "three/addons/": "https://unpkg.com/three@0.161.0/examples/jsm/"
  }
}
</script>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const S = 1;                 // voxel size
const WORLD = 40;            // half-extent of the water plane
const P = (x,y,z) => ({x,y,z});

/* ---------- palette ---------- */
const COL = {
  waterDeep:0x256b84, waterMid:0x328ba1, waterShal:0x3fa6b6,
  sand:0xd9c59b, sandWet:0xb9a37a, stone:0x8a8f97, stoneTop:0xa6abb2,
  stoneDark:0x6d7178, quay:0xb9a37a, dock:0x9c8a63,
  hullDark:0x33281d, hull:0x5c452e, hullTrim:0x8a6a45, deck:0xa07d52, deckDark:0x8a6a45,
  sail:0xf3ecdd, sailWarm:0xe8d7b4, sailRed:0xc0392b,
  mast:0x7a5c3c, mastDark:0x5c452e, spar:0x6f5537,
  rope:0x6b5a44,
  houseWall:0xe7e0d0, houseWall2:0xdfb8a0, houseWall3:0xe0d2b0,
  roofRed:0xb5483a, roofBlue:0x3f5f78, roofGreen:0x6c8f63, roofTeal:0x3f8f8a,
  door:0x5c452e, frame:0x2b2b2b,
  lamp:0x26262a, glass:0xffcf6b,
  crate:0x8a6a45, crate2:0x6f5537, barrel:0x5c452e, barrelBand:0x3a2c1d,
  treeTrunk:0x5c452e, treeLeaf:0x5f8f5a, treeLeaf2:0x78a86a,
  buoyRed:0xc0392b, buoyWhite:0xf3ecdd,
  flagRed:0xc0392b, flagBlue:0x2f6f8f, flagYellow:0xf2b45c,
  chimney:0x8a4a3a, chimneyLight:0xa6abb2,
};

/* ---------- renderer / scene / camera ---------- */
const wrap = document.getElementById('scene');
const renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
wrap.appendChild(renderer.domElement);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(48, innerWidth/innerHeight, 0.1, 4000);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.minDistance = 34;
controls.maxDistance = 360;
controls.maxPolarAngle = Math.PI*0.492;
controls.minPolarAngle = 0.12;
controls.autoRotateSpeed = 0.5;
controls.target.set(0, 3, 0);

/* ---------- sky dome (hemispheric) ---------- */
const skyGeo = new THREE.SphereGeometry(1800, 32, 20);
const skyMat = new THREE.ShaderMaterial({
  side: THREE.BackSide, depthWrite:false,
  uniforms:{ top:{value:new THREE.Color()}, mid:{value:new THREE.Color()}, bot:{value:new THREE.Color()} },
  vertexShader:`varying vec3 vDir; void main(){ vDir=normalize(position); gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}`,
  fragmentShader:`uniform vec3 top,mid,bot; varying vec3 vDir;
    void main(){ float h=clamp(vDir.y*0.5+0.5,0.0,1.0);
      vec3 c = h<0.5 ? mix(bot,mid,h/0.5) : mix(mid,top,(h-0.5)/0.5);
      gl_FragColor=vec4(c,1.0);}`
});
const sky = new THREE.Mesh(skyGeo, skyMat);
sky.renderOrder = -1;
scene.add(sky);

/* ---------- lights ---------- */
const sun = new THREE.DirectionalLight(0xffffff, 2.2);
sun.castShadow = true;
sun.shadow.mapSize.set(2048,2048);
const sc = 90;
sun.shadow.camera.left=-sc; sun.shadow.camera.right=sc;
sun.shadow.camera.top=sc; sun.shadow.camera.bottom=-sc;
sun.shadow.camera.near=1; sun.shadow.camera.far=420;
sun.shadow.bias=-0.0006; sun.shadow.normalBias=0.05;
scene.add(sun); scene.add(sun.target);

const hemi = new THREE.HemisphereLight(0xffffff, 0x000000, 0.5);
scene.add(hemi);

/* ---------- fog ---------- */
const fogColor = new THREE.Color();
scene.fog = new THREE.FogExp2(fogColor, 0.0038);

/* ---------- lighting presets ---------- */
const PRESETS = {
  golden:{ label:'Golden Hour', sunPos:[150,150,70], sunCol:0xffdca8, sunInt:2.5, hemiSky:0xffe6c0, hemiGnd:0x2f4a52, hemiInt:0.55,
           top:0x2f7fa8, mid:0x86bcd0, bot:0xffcf99, fog:0x9fc0cf, fogD:0.0036, water:0x3a90a6, waterDeep:0x256b84, waterShal:0x46b0bd, exp:1.05 },
  dawn:{   label:'Blue Hour',  sunPos:[110,45,120], sunCol:0xbcd0ff, sunInt:1.4, hemiSky:0x9fb4d8, hemiGnd:0x24384a, hemiInt:0.6,
           top:0x243a5c, mid:0x5a7297, bot:0xa98f74, fog:0x6d7f96, fogD:0.0045, water:0x2c5570, waterDeep:0x1e3f58, waterShal:0x37708c, exp:1.15 },
  noon:{   label:'Midday',     sunPos:[40,230,120], sunCol:0xffffff, sunInt:2.2, hemiSky:0xdfefff, hemiGnd:0x4a5a63, hemiInt:0.7,
           top:0x2f83c4, mid:0x9cc4de, bot:0xd8e6ef, fog:0xcfe0ea, fogD:0.0028, water:0x3f9fb5, waterDeep:0x2f7d97, waterShal:0x52b6c4, exp:1.0 },
};
const presetOrder = ['golden','dawn','noon'];
let presetIdx = 0;

/* ---------- voxel engine ---------- */
const geoCache = new Map();
const matCache = new Map();
function getGeo(){ if(!geoCache.has(S)) geoCache.set(S,new THREE.BoxGeometry(S,S,S)); return geoCache.get(S); }
function getMat(hex){
  if(!matCache.has(hex)){
    const h = hex & 0xffffff;
    const c = new THREE.Color(h);
    const sat = c.getHSL({h:0,s:0,l:0}).s;
    const m = new THREE.MeshStandardMaterial({color:h, roughness:0.82, metalness:0.04, flatShading:true});
    if(sat<0.12 && l<0.18){ m.roughness=0.45; m.metalness=0.7; }   // dark metal (lamps)
    matCache.set(hex,m);
  }
  return matCache.get(hex);
}
const voxels = [];   // {x,y,z,hex}
function addVoxel(x,y,z,hex){ voxels.push({x,y,z,hex}); }

function buildInstancedMeshes(){
  const groups = new Map();
  for(const v of voxels){
    let m = groups.get(v.hex);
    if(!m){ m=[]; groups.set(v.hex,m); }
    m.push(v);
  }
  const dummy = new THREE.Object3D();
  for(const [hex,list] of groups){
    const mesh = new THREE.InstancedMesh(getGeo(), getMat(hex), list.length);
    mesh.castShadow = true; mesh.receiveShadow = true;
    for(let i=0;i<list.length;i++){
      dummy.position.set(list[i].x, list[i].y, list[i].z);
      dummy.updateMatrix();
      mesh.setMatrixAt(i, dummy.matrix);
    }
    mesh.instanceMatrix.needsUpdate = true;
    scene.add(mesh);
  }
  voxels.length = 0;
}

/* ---------- helpers ---------- */
function box(x0,y0,z0,x1,y1,z1,hex){
  for(let y=y0;y<=y1;y++)
    for(let x=x0;x<=x1;x++)
      for(let z=z0;z<=z1;z++) addVoxel(x,y,z,hex);
}
function rect(x0,z0,x1,z1,hex,y0=0){
  for(let x=x0;x<=x1;x++)
    for(let z=z0;z<=z1;z++) addVoxel(x,y0,z,hex);
}
function rectHollow(x0,z0,x1,z1,hex,y){
  for(let x=x0;x<=x1;x++){ addVoxel(x,y,z0,hex); addVoxel(x,y,z1,hex); }
  for(let z=z0+1;z<=z1-1;z++){ addVoxel(x0,y,z,hex); addVoxel(x1,y,z,hex); }
}
function line(x0,y0,z0,x1,y1,z1,hex){
  const dx=x1-x0, dy=y1-y0, dz=z1-z0, n=Math.max(1,Math.max(Math.abs(dx),Math.max(Math.abs(dy),Math.abs(dz))));
  for(let i=0;i<=n;i++){
    addVoxel(Math.round(x0+dx*i/n), Math.round(y0+dy*i/n), Math.round(z0+dz*i/n), hex);
  }
}
function diamond(cx,cz,r,hex,y){
  for(let x=-r;x<=r;x++) for(let z=-r;z<=r;z++)
    if(Math.abs(x)+Math.abs(z)<=r) addVoxel(cx+x,y,cz+z,hex);
}
function tree(x,z){
  for(let y=0;y<2;y++) addVoxel(x,y,z,COL.treeTrunk);
  addVoxel(x,3,z,COL.treeTrunk);
  for(let y=3;y<7;y++){
    const r = y<6?2:1;
    for(let dx=-r;dx<=r;dx++) for(let dz=-r;dz<=r;dz++){
      if(dx*dx+dz*dz>r*r+r*0.5) continue;
      addVoxel(x+dx,y,z+dz, (dx+dz)&1 ? COL.treeLeaf : COL.treeLeaf2);
    }
  }
  addVoxel(x,7,z,COL.treeLeaf2);
}
function lamp(x,z){
  addVoxel(x,0,z,COL.lamp); addVoxel(x,1,z,COL.lamp); addVoxel(x,2,z,COL.lamp);
  addVoxel(x,3,z,COL.glass); addVoxel(x,4,z,COL.lamp);
}
function crate(x,z){ box(x,0,z,x,1,z,COL.crate); }
function barrel(x,z){ addVoxel(x,0,z,COL.barrelBand); addVoxel(x,1,z,COL.barrel); addVoxel(x,2,z,COL.barrelBand); }

/* ---------- water ---------- */
const waterGeo = new THREE.PlaneGeometry(WORLD*2, WORLD*2, 72, 72);
waterGeo.rotateX(-Math.PI/2);
const waterBase = waterGeo.attributes.position.array.slice();
const waterMat = new THREE.ShaderMaterial({
  transparent:true,
  uniforms:{
    uTime:{value:0}, uWave:{value:0.35}, uDeep:{value:new THREE.Color(COL.waterDeep)},
    uMid:{value:new THREE.Color(COL.waterMid)}, uShallow:{value:new THREE.Color(COL.waterShal)},
    uFog:{value:new THREE.Color()}, uFogDensity:{value:0.0038},
    uSunDir:{value:new THREE.Vector3()}, uSunCol:{value:new THREE.Color()}, uSpec:{value:0.5},
  },
  vertexShader:`
    uniform float uTime,uWave; varying vec3 vW; varying float vH;
    float wv(vec2 p){
      float t=uTime;
      float h=sin(p.x*0.16+t*1.5)*0.6 + sin(p.y*0.20-t*1.2)*0.6
             + sin((p.x+p.y)*0.09+t*0.8)*0.5 + sin((p.x-p.y)*0.13+t*1.1)*0.35;
      return h*uWave;
    }
    void main(){
      vec3 p=position; float h=wv(p.xz); p.y+=h; vH=h;
      vec4 wp=modelMatrix*vec4(p,1.0); vW=wp.xyz;
      gl_Position=projectionMatrix*viewMatrix*wp;
    }`,
  fragmentShader:`
    uniform vec3 uDeep,uMid,uShallow,uFog,uSunCol,uSunDir;
    uniform float uFogDensity,uSpec; uniform float uTime;
    varying vec3 vW; varying float vH;
    void main(){
      float a=0.16,t=0.12; float r=0.15;
      float h=sin(vW.x*a+t*1.8)*0.5+0.5;
      float g=sin(vW.z*t*1.4+r)*0.5+0.5;
      float f=0.5+0.5*sin((vW.x+vW.z)*0.11+uTime*1.05);
      float m=clamp(h*0.45+g*0.45+f*0.25,0.0,1.0);
      vec3 col=mix(uDeep,uMid,clamp(m*1.15,0.0,1.0));
      col=mix(col,uShallow,smoothstep(0.82,1.0,m));
      vec3 V=normalize(cameraPosition-vW);
      vec3 H=normalize(uSunDir+V);
      float fres=0.05+0.95*pow(1.0-max(dot(V,uSunDir),0.0),3.0);
      col=mix(col,uMid,fres*0.75);
      float diff=max(dot(uSunDir,vec3(0.0,1.0,0.0)),0.0);
      col*=0.55+0.45*diff;
      float s=pow(max(dot(normalize(vec3(0.0,1.0,0.0)),H),0.0),120.0);
      col+=uSunCol*s*uSpec;
      float dist=length(cameraPosition-vW);
      col=mix(col,uFog,1.0-exp(-uFogDensity*uFogDensity*dist*dist));
      gl_FragColor=vec4(col,1.0);
    }`
});
const water = new THREE.Mesh(waterGeo, waterMat);
water.renderOrder = 1;
water.frustumCulled = false;
scene.add(water);

/* ---------- ground / quay / dock ---------- */
function buildDock(){
  rect(-15,-40,15,40,COL.sand,-1);                 // sea bed
  box(-40,-1,-4,-1,0,-40,COL.sand,-1);             // shore (fills to edge)
  box(-38,-1,-3,38,0,1,COL.sand,-1);               // beach
  box(-33,0,-3,33,0,3,COL.quay);                   // promenade
  box(-33,0,3,33,1,4,COL.stone);                   // quay wall
  box(-30,1,4,30,1,13,COL.dock);                   // dock apron
  for(let x=-30;x<=30;x+=4) addVoxel(x,1,-4,COL.stoneDark);  // bollards along edge
}

/* ---------- buildings ---------- */
function house(x,z,w,d,wall,roof){
  box(x,0,z, x+w,3, z+d, wall);
  rect(x,z,x+w,z+d,COL.door);                       // floor
  rect(x,z,x+w,z+d,COL.roofRed);                    // flat top fill
  for(let y=4;y<=6;y++){
    let off=6-y;
    for(let bx=x-off;bx<=x+w+off;bx++)
      for(let bz=z-off;bz<=z+d+off;bz++)
        if(bx<x-off+1||bx>x+w+off-1||bz<z-off+1||bz>z+d+off-1) addVoxel(bx,y,bz,roof);
  }
  let off=1;
  for(let bx=x-off;bx<=x+w+off;bx++)
    for(let bz=z-off;bz<=z+d+off;bz++)
      if(bx<x-off+1||bx>x+w+off-1||bz<z-off+1||bz>z+d+off-1) addVoxel(bx,7,bz,roof);
  addVoxel(x+w,7,z+d,roof);
}
function chimneyAt(x,z,roof){ addVoxel(x,4,z,COL.chimney); addVoxel(x,5,z,roof); }

function buildTown(){
  house(-30,-18,7,9, COL.houseWall, COL.roofRed); chimneyAt(-27,-14,COL.roofRed);
  house(-21,-18,6,7, COL.houseWall2, COL.roofBlue);
  house(-13,-18,7,8, COL.houseWall, COL.roofGreen); chimneyAt(-10,-15,COL.roofGreen);
  house(-4,-18,6,7, COL.houseWall3, COL.roofBlue);
  house(5,-18,7,9, COL.houseWall, COL.roofRed); chimneyAt(8,-14,COL.roofRed);
  house(14,-18,6,7, COL.houseWall2, COL.roofGreen);
  house(22,-18,7,8, COL.houseWall, COL.roofBlue);
  // second row
  house(-27,-30,6,7, COL.houseWall2, COL.roofGreen);
  house(-17,-30,7,8, COL.houseWall, COL.roofBlue); chimneyAt(-14,-27,COL.roofBlue);
  house(-6,-30,6,7, COL.houseWall3, COL.roofRed);
  house(4,-30,7,8, COL.houseWall, COL.roofGreen);
  house(14,-30,6,7, COL.houseWall2, COL.roofBlue);

  // market
  box(-30,0,9,30,0,1,COL.sandWet);
  for(let x=-28;x<=28;x+=4){
    line(x,1,12,x,2,12,COL.frame); line(x+2,1,12,x+2,2,12,COL.frame);
    line(x,1,16,x,2,16,COL.frame); line(x+2,1,16,x+2,2,16,COL.frame);
    for(let z=12;z<=16;z++) for(let bx=x-1;bx<=x+3;bx++)
      if(((x+z)&1)===0) addVoxel(bx,3,z,COL.crate2); else addVoxel(bx,3,z,COL.crate);
  }
  for(let z=12;z<=16;z++) for(let x=-28;x<=28;x++)
    if(((x+z)&1)===0) addVoxel(x,3,z,COL.crate2); else addVoxel(x,3,z,COL.crate);

  // trees + lamps
  const trees=[[-31,-8],[-31,-12],[-31,-16],[-31,-22],[-31,-28],[-31,-33],
               [31,-8],[31,-12],[31,-16],[31,-22],[31,-28],[31,-33],
               [-25,-5],[-15,-5],[-5,-5],[5,-5],[15,-5],[25,-5]];
  trees.forEach(([x,z])=>tree(x,z));
  const lamps=[[-24,-1],[-16,-1],[-8,-1],[0,-1],[8,-1],[16,-1],[24,-1]];
  lamps.forEach(([x,z])=>lamp(x,z));

  // crates / barrels on apron
  const crates=[[-27,6],[-26,7],[-25,6],[-24,7],[-27,8],[-26,9],[-25,8]];
  crates.forEach(([x,z])=>crate(x,z));
  [[-12,7],[-11,8],[-10,7],[-13,9],[-12,10]].forEach(([x,z])=>barrel(x,z));

  // mooring bollards on dock edge
  [-20,-10,0,10,20].forEach(x=>{ addVoxel(x,1,14,COL.stoneDark); addVoxel(x,2,14,COL.stoneDark); });
}

/* ---------- breakwater ---------- */
function buildBreakwater(){
  for(let x=-40;x<=12;x++){
    for(let z=26;z<=28;z++) addVoxel(x,0,z,COL.stone);
    for(let z=26;z<=28;z++) addVoxel(x,1,z,COL.stoneDark);
    for(let z=26;z<=28;z++) addVoxel(x,2,z,COL.stoneTop);
    if((x+z)&1) addVoxel(x,2,z,COL.stoneDark);
  }
  for(let x=12;x<=22;x++){
    addVoxel(x,0,27,COL.stone); addVoxel(x,1,27,COL.stoneDark);
    addVoxel(x,2,27,COL.stoneTop);
  }
  // beacon at the end
  addVoxel(13,3,27,COL.lamp);
  addVoxel(14,3,27,COL.flagRed);
  addVoxel(15,3,27,COL.lamp);
  addVoxel(14,4,27,COL.lamp);
  addVoxel(14,5,27,COL.glass);
  addVoxel(14,6,27,COL.lamp);
}

/* ---------- lighthouse ---------- */
function buildLighthouse(){
  const bx=34, bz=2;
  box(bx,bz,0,bx,bz,0,COL.stone); box(bx+1,bz,0,bx+1,bz,0,COL.stone);
  box(bx,bz+1,0,bx,bz+1,0,COL.stone); box(bx+1,bz+1,0,bx+1,bz+1,0,COL.stone);
  diamond(bx,bz+1,1,COL.stone,1);
  diamond(bx,bz+1,1,COL.stone,2);
  diamond(bx,bz+1,1,COL.stone,3);
  // red/white bands
  for(let y=4;y<=5;y++) diamond(bx,bz+1,1,COL.stone, y);
  for(let y=6;y<=7;y++) diamond(bx,bz+1,1,COL.flagRed, y);
  for(let y=8;y<=9;y++) diamond(bx,bz+1,1,COL.stone, y);
  // lantern
  for(let dx=-1;dx<=1;dx++) for(let dz=-1;dz<=1;dz++) addVoxel(bx+dx,10,bz+1+dz,COL.lamp);
  addVoxel(bx,11,bz+1,COL.glass);
  addVoxel(bx,11,bz,COL.glass);   addVoxel(bx,11,bz+2,COL.glass);
  addVoxel(bx+1,11,bz+1,COL.glass); addVoxel(bx-1,11,bz+1,COL.glass);
  addVoxel(bx,12,bz+1,COL.lamp);
  // cap + finial
  addVoxel(bx,13,bz+1,COL.stoneTop);
  addVoxel(bx,14,bz+1,COL.stoneDark);
  addVoxel(bx,15,bz+1,COL.flagRed);
  // keeper's house + fence
  box(bx-3,bz+1,0,bx-1,bz+3,2,COL.houseWall);
  for(let x=bx-3;x<=bx-1;x++) for(let z=bz+1;z<=bz+3;z++) addVoxel(x,3,z,COL.roofRed);
  line(bx-4,bz,1,bx-4,bz,5,COL.stoneDark);
  line(bx-4,bz,5,bx+2,bz,5,COL.stoneDark);
}

/* ---------- buoys ---------- */
function buoy(x,z,hex){
  addVoxel(x,0,z,COL.stoneDark); addVoxel(x,1,z,hex); addVoxel(x,2,z,hex); addVoxel(x,3,z,COL.lamp);
}

/* ---------- THE SHIP ---------- */
const ship = new THREE.Group();
const SHIP = {
  mast:[[-11,7],[0,10],[11,7]],
  yards:[
    {z:-11,x0:-5,x1:-2,y:5},{z:-11,x0:-1,x1:2,y:6},
    {z:0,x0:-4,x1:4,y:6},{z:0,x0:-7,x1:7,y:9},
    {z:11,x0:-5,x1:-2,y:5},{z:11,x0:-1,x1:2,y:6},
  ],
  sails:[
    {z:-11,x0:-5,x1:-2,y0:1,y1:4,c:COL.sail},
    {z:-11,x0:-1,x1:2,y0:2,y1:5,c:COL.sail},
    {z:0,x0:-4,x1:4,y0:2,y1:5,c:COL.sail},
    {z:0,x0:-7,x1:7,y0:6,y1:8,c:COL.sail},
    {z:0,x0:-4,x1:4,y0:6,y1:8,c:COL.sail},
    {z:11,x0:-5,x1:-2,y0:1,y1:4,c:COL.sail},
    {z:11,x0:-1,x1:2,y0:2,y1:5,c:COL.sail},
  ],
  jibs:[
    {z:-11,x0:-12,x1:-9,y0:3,y1:5,c:COL.sailWarm},
    {z:-11,x0:-10,x1:-7,y0:5,y1:7,c:COL.sailWarm},
  ],
  rig:[
    [[0,10,0],[-13,2,0]],[[0,10,0],[13,2,0]],
    [[-11,7,0],[-13,2,0]],[[11,7,0],[13,2,0]],
    [[-11,7,0],[0,9,0]],[[11,7,0],[0,9,0]],
    [[0,10,-4],[0,10,4]],[[-11,7,-3],[-11,7,3]],[[11,7,-3],[11,7,3]],
  ]
};

function buildShip(){
  // hull
  for(let z=-13;z<=13;z++){
    const w = Math.round(6 - Math.abs(z)*6/13);
    for(let y=0;y<=3;y++)
      for(let x=-w;x<=w;x++) addVoxel(x,y,z,COL.hull);
  }
  for(let z=-13;z<=13;z++){
    const w = Math.round(6 - Math.abs(z)*6/13);
    addVoxel(-w-1,2,z,COL.hullTrim); addVoxel(w+1,2,z,COL.hullTrim);
    addVoxel(-w-1,3,z,COL.hullTrim); addVoxel(w+1,3,z,COL.hullTrim);
  }
  for(let x=-6;x<=6;x++){ addVoxel(x,4,-12,COL.deckDark); addVoxel(x,4,12,COL.deckDark); }
  for(let z=-12;z<=12;z++){ addVoxel(-6,4,z,COL.deck); addVoxel(6,4,z,COL.deck); }
  addVoxel(0,4,13,COL.deckDark); addVoxel(0,4,-13,COL.deckDark);

  // bulwark
  for(let z=-12;z<=12;z++){ const w=Math.round(6-Math.abs(z)*6/13);
    addVoxel(-w-1,5,z,COL.hullDark); addVoxel(w+1,5,z,COL.hullDark); }
  for(let x=-6;x<=6;x++){ addVoxel(x,5,-12,COL.hullDark); addVoxel(x,5,12,COL.hullDark); }

  // deck interior
  for(let z=-11;z<=11;z++) for(let x=-5;x<=5;x++) addVoxel(x,4,z,COL.deck);
  // gun ports
  for(let z=-9;z<=9;z+=3){ addVoxel(-6,2,z,COL.hullDark); addVoxel(6,2,z,COL.hullDark); }
  // sterncastle
  box(-3,5,-11,3,6,-8,COL.deckDark);
  box(-3,7,-11,3,7,-8,COL.hullDark);
  for(let x=-3;x<=3;x++) addVoxel(x,8,-11,COL.hullDark);
  // forecastle
  box(-3,5,8,3,6,11,COL.deckDark);
  // masts + yards + sails + jibs + rigging
  SHIP.mast.forEach(([z,h])=>{ for(let y=4;y<=h;y++) addVoxel(0,y,z,COL.mast); addVoxel(0,h+1,z,COL.mastDark); });
  SHIP.yards.forEach(y=>{ for(let x=y.x0;x<=y.x1;x++) addVoxel(x,y.y,y.z,COL.spar); });
  SHIP.sails.forEach(s=>{ for(let y=s.y0;y<=s.y1;y++) for(let x=s.x0;x<=s.x1;x++) addVoxel(x,y,s.z,s.c); });
  SHIP.jibs.forEach(s=>{ for(let y=s.y0;y<=s.y1;y++) for(let x=s.x0;x<=s.x1;x++) addVoxel(x,y,s.z,s.c); });
  SHIP.rig.forEach(([a,b])=>line(a[0],a[1],a[2],b[0],b[1],b[2],COL.rope));
  // ensign at stern
  for(let z=-14;z>=-12;z--) for(let y=7;y<=9;y++){
    addVoxel(0,y,z, y===8?COL.flagYellow:COL.flagRed);
  }
  // pennant at main mast
  for(let x=1;x<=6;x++) addVoxel(x,10,0, (x&1)?COL.flagRed:COL.flagYellow);
}

/* ---------- gulls ---------- */
const gullGeo = new THREE.BoxGeometry(1.2,0.35,0.35);
const gullMat = new THREE.MeshStandardMaterial({color:0xf3ecdd, roughness:0.7, flatShading:true});
const gullGroup = new THREE.Group();
const gulls = [];
for(let i=0;i<12;i++){
  const m = new THREE.Mesh(gullGeo, gullMat);
  m.castShadow = false;
  gullGroup.add(m);
  gulls.push({mesh:m, r:38+Math.random()*30, ang:Math.random()*Math.PI*2,
    y:22+Math.random()*10, spd:0.12+Math.random()*0.12, ph:Math.random()*6.28});
}
scene.add(gullGroup);

/* ---------- clouds (voxel) ---------- */
function buildClouds(){
  const cloudMat = new THREE.MeshStandardMaterial({color:0xf4efe6, roughness:1, flatShading:true});
  cloudMat.fog = true;
  const cloudGroup = new THREE.Group();
  const seed = (n)=>{ let s=n; return ()=>{ s=(s*16807+11)%2147483647; return s/2147483647; }; };
  for(let c=0;c<6;c++){
    const g = new THREE.Group();
    const rnd = seed(c*13+7);
    const blobs = 5 + Math.floor(rnd()*4);
    for(let b=0;b<blobs;b++){
      const w=4+Math.floor(rnd()*4), h=2+Math.floor(rnd()*2), d=3+Math.floor(rnd()*4);
      const bx=Math.floor(rnd()*18-9), bz=Math.floor(rnd()*18-9);
      const m = new THREE.InstancedMesh(getGeo(), cloudMat, w*h*d);
      m.castShadow=false; m.receiveShadow=false;
      const dm=new THREE.Object3D(); let i=0;
      for(let x=0;x<w;x++)for(let y=0;y<h;y++)for(let z=0;z<d;z++){ dm.position.set(bx+x,y,bz+z); dm.updateMatrix(); m.setMatrixAt(i++,dm.matrix); }
      m.instanceMatrix.needsUpdate=true; g.add(m);
    }
    g.position.set(-150+c*60+rnd()*30, 60+rnd()*14, -160+rnd()*120);
    cloudGroup.add(g);
  }
  scene.add(cloudGroup);
  return cloudGroup;
}
const clouds = buildClouds();

/* ---------- assemble all static voxels ---------- */
buildDock(); buildTown(); buildBreakwater(); buildLighthouse();
[-16, 2, 20].forEach(x=>buoy(x, 16, x<0?COL.buoyRed:COL.buoyWhite));
buildShip();
// ship → its own instanced meshes inside the ship group (kept separate from static batch)
{
  const groups = new Map();
  for(const v of voxels){ let m=groups.get(v.hex); if(!m){m=[];groups.set(v.hex,m);} m.push(v); }
  const dummy=new THREE.Object3D();
  for(const [hex,list] of groups){
    const mesh=new THREE.InstancedMesh(getGeo(), getMat(hex), list.length);
    mesh.castShadow=true; mesh.receiveShadow=true;
    for(let i=0;i<list.length;i++){ dummy.position.set(list[i].x,list[i].y,list[i].z); dummy.updateMatrix(); mesh.setMatrixAt(i,dummy.matrix); }
    mesh.instanceMatrix.needsUpdate=true; ship.add(mesh);
  }
  voxels.length=0;
}
// now static
buildDock(); buildTown(); buildBreakwater(); buildLighthouse();
[-16, 2, 20].forEach(x=>buoy(x, 16, x<0?COL.buoyRed:COL.buoyWhite));
buildInstancedMeshes();

/* ---------- apply lighting preset (with tween) ---------- */
let cur=null, tgt=null, tw=1;
const tmp=new THREE.Color();
function applyPreset(name){
  const p=PRESETS[name];
  tgt={
    sunPos:new THREE.Vector3(...p.sunPos), sunCol:new THREE.Color(p.sunCol), sunInt:p.sunInt,
    hemiSky:new THREE.Color(p.hemiSky), hemiGnd:new THREE.Color(p.hemiGnd), hemiInt:p.hemiInt,
    top:new THREE.Color(p.top), mid:new THREE.Color(p.mid), bot:new THREE.Color(p.bot),
    fog:new THREE.Color(p.fog), fogD:p.fogD,
    waterDeep:new THREE.Color(p.waterDeep), waterMid:new THREE.Color(p.water), waterShal:new THREE.Color(p.waterShal),
    exp:p.exp
  };
  cur = cur || structuredClone(tgt);
  tw=0;
}
applyPreset('golden');

/* ---------- intro camera move ---------- */
const camA = new THREE.Vector3(150,110,150), camB = new THREE.Vector3(52,26,60);
camera.position.copy(camA);
let intro = true, introT = 0;

/* ---------- UI ---------- */
let autoOn=false;
const bOrbit=document.getElementById('bOrbit'), bTime=document.getElementById('bTime'),
      bReset=document.getElementById('bReset'), toastEl=document.getElementById('toast');
function showToast(t){ toastEl.textContent=t; toastEl.classList.add('show'); clearTimeout(showToast._t);
  showToast._t=setTimeout(()=>toastEl.classList.remove('show'),1600); }
bOrbit.onclick=()=>{ autoOn=!autoOn; controls.autoRotate=autoOn; bOrbit.classList.toggle('on',autoOn); };
bTime.onclick=()=>{ presetIdx=(presetIdx+1)%presetOrder.length; const n=presetOrder[presetIdx];
  applyPreset(n); bTime.innerHTML='☀ '+PRESETS[n].label; showToast('Time of day: '+PRESETS[n].label); };
bReset.onclick=()=>{ intro=true; introT=0; camera.position.copy(camA); controls.target.set(0,3,0); showToast('View reset'); };
const hdgEl=document.getElementById('hdg'), brgEl=document.getElementById('brg');

/* ---------- animate ---------- */
const clock=new THREE.Clock();
let elapsed=0;
const shipHome=new THREE.Vector3(24,0,-14), shipYaw=0.14;

function updateWater(t){
  const pos=waterGeo.attributes.position, arr=pos.array;
  for(let i=0;i<arr.length;i+=3){
    const x=waterBase[i], z=waterBase[i+2];
    arr[i+1]=(Math.sin(x*0.16+t*1.5)*0.6 + Math.sin(z*0.20-t*1.2)*0.6
      + Math.sin((x+z)*0.09+t*0.8)*0.5 + Math.sin((x-z)*0.13+t*1.1)*0.35)*0.35;
  }
  pos.needsUpdate=true;
}

function lerpColor(a,b,f){ return tmp.copy(a).lerp(b,f).clone(); }

function step(dt){
  elapsed+=dt;

  // preset tween
  if(tw<1){
    tw=Math.min(1,tw+dt/1.6); const f=tw*tw*(3-2*tw);
    cur.sunPos.lerp(tgt.sunPos,f); cur.sunCol.lerp(tgt.sunCol,f); cur.sunInt+=(tgt.sunInt-cur.sunInt)*f;
    cur.hemiSky.lerp(tgt.hemiSky,f); cur.hemiGnd.lerp(tgt.hemiGnd,f); cur.hemiInt+=(tgt.hemiInt-cur.hemiInt)*f;
    cur.top.lerp(tgt.top,f); cur.mid.lerp(tgt.mid,f); cur.bot.lerp(tgt.bot,f);
    cur.fog.lerp(tgt.fog,f); cur.fogD+=(tgt.fogD-cur.fogD)*f;
    cur.waterDeep.lerp(tgt.waterDeep,f); cur.waterMid.lerp(tgt.waterMid,f); cur.waterShal.lerp(tgt.waterShal,f);
    cur.exp+=(tgt.exp-cur.exp)*f;
  }
  sun.position.copy(cur.sunPos); sun.target.position.set(0,0,0);
  sun.color.copy(cur.sunCol); sun.intensity=cur.sunInt;
  hemi.color.copy(cur.hemiSky); hemi.groundColor.copy(cur.hemiGnd); hemi.intensity=cur.hemiInt;
  skyMat.uniforms.top.value.copy(cur.top); skyMat.uniforms.mid.value.copy(cur.mid); skyMat.uniforms.bot.value.copy(cur.bot);
  fogColor.copy(cur.fog); scene.fog.color.copy(cur.fog); scene.fog.density=cur.fogD;
  renderer.toneMappingExposure=cur.exp;
  const sunDir=cur.sunPos.clone().normalize();
  waterMat.uniforms.uTime.value=elapsed;
  waterMat.uniforms.uDeep.value.copy(cur.waterDeep);
  waterMat.uniforms.uMid.value.copy(cur.waterMid);
  waterMat.uniforms.uShallow.value.copy(cur.waterShal);
  waterMat.uniforms.uFog.value.copy(cur.fog);
  waterMat.uniforms.uFogDensity.value=cur.fogD;
  waterMat.uniforms.uSunDir.value.copy(sunDir);
  waterMat.uniforms.uSunCol.value.copy(cur.sunCol);
  waterMat.uniforms.uSpec.value=cur.sunInt*0.22;
  updateWater(elapsed);

  // ship bobbing
  const bobY=Math.sin(elapsed*0.9)*0.4;
  const pitch=Math.sin(elapsed*0.7+0.6)*0.02;
  const roll=Math.sin(elapsed*0.55)*0.03;
  ship.position.set(shipHome.x, bobY, shipHome.z);
  ship.rotation.set(pitch, shipYaw, roll);

  // gulls
  for(const g of gulls){
    g.ang+=g.spd*dt;
    g.mesh.position.set(Math.cos(g.ang)*g.r, g.y+Math.sin(elapsed*0.8+g.ph)*1.2, Math.sin(g.ang)*g.r);
    g.mesh.rotation.y=-g.ang+Math.PI/2;
    g.mesh.rotation.z=Math.sin(elapsed*8+g.ph)*0.25;
  }

  // clouds drift
  clouds.position.x=(clouds.position.x+dt*1.6);
  if(clouds.position.x>60) clouds.position.x=-40;

  // intro
  if(intro){
    introT+=dt/3.4; const f=Math.min(1,introT); const e=f*f*(3-2*f);
    camera.position.lerpVectors(camA,camB,e);
    if(f>=1) intro=false;
  }

  // readout
  const az=controls.getAzimuthalAngle();
  let deg=((-az*180/Math.PI)%360+360)%360;
  hdgEl.textContent=Math.round(deg)+'°';
  const dirs=['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW'];
  brgEl.textContent=dirs[Math.round(deg/22.5)%16];
}

let last=performance.now();
function loop(){
  requestAnimationFrame(loop);
  const now=performance.now(); const dt=Math.min(0.05,(now-last)/1000); last=now;
  controls.update();
  step(dt);
  renderer.render(scene,camera);
}

addEventListener('resize',()=>{
  camera.aspect=innerWidth/innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight);
});

renderer.render(scene,camera);
loop();
setTimeout(()=>document.getElementById('loader').classList.add('hidden'),500);
</script>
</body>
</html>
```

**What's in the scene**
- A three‑master **sailing ship** (hull, masts, yards, square sails, jibs, rigging, ensign + pennant) sitting on the water, gently bobbing.
- A **lighthouse** with rotating‑look lantern glass + keeper's cottage, a **stone breakwater** with a beacon, a **harbor town** (rooftops, chimneys, trees, lamps, market stalls, crates/barrels), a quay, and a sandy shore.
- **Animated ocean** (custom water shader: swell, foam, sun specular, distance fog), drifting **voxel clouds**, and **gulls** circling.

**Controls**
- Drag to orbit · right‑drag to pan · scroll to zoom.
- `Auto‑orbit`, `Time of day` (Golden Hour → Blue Hour → Midday, each re‑lights the whole scene), and `Reset view`.

Everything is a single self‑contained file — no build step, just open it.