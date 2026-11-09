Below is a complete single-file build — a voxel harbour at golden hour: a three-master running in with the flood, a shingled breakwater light with a turning beam, a sandstone town on the quay, cypresses, a working windmill, a ship's boat pulling for the steps, gulls, drift-wood clouds and a GPU-driven chunky sea that the ship genuinely rides.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
<title>Calling at the Harbour — a voxel study</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IM+Fell+English+SC&family=Space+Grotesk:wght@300;400;500;700&display=swap" rel="stylesheet">
<style>
  :root{
    --ink: rgba(11,21,25,.84);
    --ink2: rgba(9,17,20,.92);
    --brass: #c9a24a;
    --brass-hi: #f2cd7f;
    --paper: #efe2c8;
    --red: #b5443c;
    --line: rgba(201,162,74,.28);
  }
  *{ box-sizing:border-box; }
  html,body{ margin:0; height:100%; overflow:hidden; background:#0b1418; color:var(--paper);
    font-family:'Space Grotesk', system-ui, sans-serif; -webkit-font-smoothing:antialiased; }
  canvas{ display:block; }
  #stage{ position:fixed; inset:0; }

  /* ---------- overlays ---------- */
  #vig{ position:fixed; inset:0; pointer-events:none; z-index:4;
    background:
      radial-gradient(120% 90% at 50% 45%, rgba(0,0,0,0) 45%, rgba(4,10,12,.55) 100%),
      linear-gradient(to bottom, rgba(7,14,16,.42), rgba(0,0,0,0) 22%, rgba(0,0,0,0) 76%, rgba(5,11,13,.5)); }
  #grain{ position:fixed; inset:-50%; width:200%; height:200%; pointer-events:none; z-index:5; opacity:.055;
    background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='140' height='140'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3'/></filter><rect width='140' height='140' filter='url(%23n)'/></svg>");
    animation: grain 1.1s steps(3) infinite; }
  @keyframes grain{ 0%{transform:translate(0,0)} 33%{transform:translate(-6px,4px)} 66%{transform:translate(4px,-7px)} 100%{transform:translate(0,0)} }

  /* ---------- panels ---------- */
  #ui{ position:fixed; inset:0; z-index:6; pointer-events:none; }
  .panel{ pointer-events:auto; background:linear-gradient(170deg, var(--ink), var(--ink2));
    border:1px solid var(--line); box-shadow:0 18px 40px rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.05);
    backdrop-filter:blur(3px); }
  .panel::before,.panel::after{ content:''; position:absolute; width:9px; height:9px; border:1px solid var(--brass); opacity:.7; }
  .panel::before{ left:4px; top:4px; border-right:0; border-bottom:0; }
  .panel::after{ right:4px; bottom:4px; border-left:0; border-top:0; }

  #title{ position:absolute; left:26px; top:24px; width:330px; padding:18px 20px 16px;
    animation: rise .9s cubic-bezier(.2,.8,.2,1) both .15s; }
  #title .kicker{ font-size:9.5px; letter-spacing:.34em; color:var(--brass); opacity:.9; text-transform:uppercase; }
  #title h1{ font-family:'IM Fell English SC', serif; font-weight:400; line-height:.98;
    font-size:37px; margin:10px 0 0; color:#f6ecd6; text-shadow:0 2px 0 rgba(0,0,0,.35); }
  #title h1 em{ display:block; font-style:normal; font-size:22px; color:var(--brass-hi); }
  #title .rule{ height:1px; margin:14px 0 10px; background:linear-gradient(90deg,var(--brass),rgba(201,162,74,0)); }
  #title p{ font-size:11.5px; line-height:1.55; color:rgba(239,226,200,.72); margin:0; font-weight:300; }
  #title p b{ color:var(--paper); font-weight:500; }

  #dock{ position:absolute; left:26px; bottom:24px; width:330px; padding:15px 16px 16px;
    animation: rise .9s cubic-bezier(.2,.8,.2,1) both .3s; }
  .lbl{ font-size:9px; letter-spacing:.3em; color:var(--brass); text-transform:uppercase; opacity:.85; margin:0 0 8px; }
  .lbl span{ float:right; letter-spacing:.14em; color:rgba(239,226,200,.5); }
  .seg{ display:flex; gap:5px; }
  .seg button{ flex:1; pointer-events:auto; cursor:pointer; font:inherit; font-size:9.5px; font-weight:500;
    letter-spacing:.15em; text-transform:uppercase; color:rgba(239,226,200,.68); background:rgba(255,255,255,.03);
    border:1px solid rgba(201,162,74,.22); padding:8px 4px; position:relative; overflow:hidden;
    transition:color .18s, background .18s, border-color .18s, transform .18s; }
  .seg button i{ position:absolute; left:0; top:0; height:2px; width:100%; background:var(--brass);
    transform:scaleX(0); transform-origin:left; transition:transform .3s cubic-bezier(.2,.8,.2,1); }
  .seg button:hover{ color:#fff; background:rgba(201,162,74,.12); border-color:rgba(201,162,74,.5); transform:translateY(-1px); }
  .seg button.on{ color:#0f1a1d; background:linear-gradient(180deg,var(--brass-hi),var(--brass)); border-color:var(--brass-hi); }
  .seg button.on i{ transform:scaleX(1); }
  .group{ margin-top:14px; }
  .group:first-child{ margin-top:0; }

  input[type=range]{ -webkit-appearance:none; width:100%; height:20px; background:transparent; cursor:pointer; }
  input[type=range]::-webkit-slider-runnable-track{ height:3px; background:linear-gradient(90deg,var(--brass),rgba(201,162,74,.18)); }
  input[type=range]::-webkit-slider-thumb{ -webkit-appearance:none; width:13px; height:13px; margin-top:-5px;
    background:var(--brass-hi); border:1px solid #6a5322; box-shadow:0 0 0 3px rgba(201,162,74,.16); transition:transform .15s; }
  input[type=range]:hover::-webkit-slider-thumb{ transform:scale(1.2); }
  .switch{ display:flex; align-items:center; justify-content:space-between; margin-top:9px;
    font-size:10px; letter-spacing:.16em; text-transform:uppercase; color:rgba(239,226,200,.7); }
  .tog{ pointer-events:auto; cursor:pointer; width:34px; height:14px; border:1px solid rgba(201,162,74,.4);
    background:rgba(0,0,0,.3); position:relative; transition:background .2s; }
  .tog::after{ content:''; position:absolute; left:1px; top:1px; width:14px; height:10px; background:rgba(239,226,200,.5);
    transition:transform .22s cubic-bezier(.2,.8,.2,1), background .22s; }
  .tog.on{ background:rgba(201,162,74,.25); } .tog.on::after{ transform:translateX(18px); background:var(--brass-hi); }

  #compass{ position:absolute; right:26px; top:24px; width:104px; padding:12px 10px 9px; text-align:center;
    animation: rise .9s cubic-bezier(.2,.8,.2,1) both .45s; }
  #compass svg{ display:block; margin:0 auto; }
  #head{ font-family:'IM Fell English SC',serif; font-size:15px; color:var(--brass-hi); margin-top:2px; }
  #compass .lbl{ margin:0 0 6px; }

  #readout{ position:absolute; right:26px; top:168px; width:104px; padding:9px 10px 10px; font-size:9.5px;
    letter-spacing:.1em; color:rgba(239,226,200,.55); text-align:center; line-height:1.7;
    animation: rise .9s cubic-bezier(.2,.8,.2,1) both .55s; }
  #readout b{ color:var(--brass-hi); font-weight:500; }

  #hint{ position:absolute; right:26px; bottom:24px; max-width:300px; text-align:right; font-size:10px;
    letter-spacing:.16em; text-transform:uppercase; color:rgba(239,226,200,.42); line-height:2;
    animation: rise .9s cubic-bezier(.2,.8,.2,1) both .7s; }
  #hint k{ color:var(--brass); }

  #log{ position:absolute; left:50%; bottom:24px; transform:translateX(-50%); max-width:520px; text-align:center;
    font-size:12px; letter-spacing:.04em; color:rgba(239,226,200,.8); padding:9px 18px; opacity:.95;
    transition:opacity .35s; pointer-events:none; }
  #log.flash{ opacity:0; }
  #log i{ font-style:normal; color:var(--brass-hi); }

  #tip{ position:fixed; z-index:7; pointer-events:none; opacity:0; transform:translate(-50%,-150%) scale(.96);
    transition:opacity .16s, transform .16s; background:rgba(8,15,17,.9); border:1px solid rgba(201,162,74,.5);
    padding:6px 10px 7px; font-size:10px; letter-spacing:.18em; text-transform:uppercase; white-space:nowrap; }
  #tip.show{ opacity:1; transform:translate(-50%,-140%) scale(1); }
  #tip b{ color:var(--brass-hi); font-weight:500; }

  #loader{ position:fixed; inset:0; z-index:9; background:#0b1418; display:flex; align-items:center; justify-content:center;
    transition:opacity .8s ease .2s, visibility 0s linear .8s; }
  #loader.done{ opacity:0; visibility:hidden; }
  #loader .box{ width:320px; text-align:center; }
  #loader .t{ font-family:'IM Fell English SC',serif; font-size:26px; color:#f6ecd6; margin-bottom:16px; }
  #bar{ height:2px; background:rgba(201,162,74,.2); }
  #bar > div{ height:100%; width:0%; background:var(--brass); transition:width .25s; }
  #lmsg{ margin-top:10px; font-size:9.5px; letter-spacing:.3em; text-transform:uppercase; color:rgba(239,226,200,.45); }
  @keyframes rise{ from{ opacity:0; transform:translateY(16px); } to{ opacity:1; transform:none; } }
  .hidden-ui{ opacity:0 !important; pointer-events:none !important; transition:opacity .35s; }
</style>
</head>
<body>
<div id="stage"></div>
<div id="vig"></div>
<div id="grain"></div>

<div id="ui">
  <section class="panel" id="title">
    <div class="kicker">voxel study №3 · 1 voxel = 1 foot</div>
    <h1>Calling at the<em>Harbour</em></h1>
    <div class="rule"></div>
    <p>A <b>three-master</b> runs in on the flood with a pilot flag at the fore. Everything below is cubes — <b id="vcount">—</b>.</p>
  </section>

  <section class="panel" id="dock">
    <div class="group"><div class="lbl">Berths <span>keys 1–5</span></div>
      <div class="seg" id="views"></div>
    </div>
    <div class="group"><div class="lbl">The light <span>key M</span></div>
      <div class="seg" id="moods"></div>
    </div>
    <div class="group">
      <div class="lbl">Wind <span id="windv">4 · moderate</span></div>
      <input id="wind" type="range" min="12" max="175" value="100" />
      <div class="switch">Lanterns lit <div class="tog on" id="togLamps"></div></div>
      <div class="switch">Auto-orbit the roads <div class="tog" id="togOrbit"></div></div>
    </div>
  </section>

  <section class="panel" id="compass">
    <div class="lbl">Heading</div>
    <svg width="82" height="82" viewBox="-41 -41 82 82">
      <g id="rose">
        <circle r="33" fill="none" stroke="rgba(201,162,74,.28)" stroke-width="1"/>
        <circle r="24" fill="none" stroke="rgba(201,162,74,.14)" stroke-width="1"/>
        <g id="ticks"></g>
        <g id="needle" style="transition:none">
          <path d="M0,-30 L6,3 L0,-4 L-6,3 Z" fill="#f2cd7f"/>
          <path d="M0,30 L4,2 L0,7 L-4,2 Z" fill="rgba(239,226,200,.35)"/>
        </g>
        <circle r="2.4" fill="#0b1418" stroke="#c9a24a"/>
      </g>
      <text x="0" y="-33" text-anchor="middle" font-size="9" fill="rgba(201,162,74,.8)" font-family="Space Grotesk">N</text>
      <text x="36" y="3" text-anchor="middle" font-size="8" fill="rgba(239,226,200,.4)" font-family="Space Grotesk">E</text>
      <text x="0" y="39" text-anchor="middle" font-size="8" fill="rgba(239,226,200,.4)" font-family="Space Grotesk">S</text>
      <text x="-36" y="3" text-anchor="middle" font-size="8" fill="rgba(239,226,200,.4)" font-family="Space Grotesk">W</text>
    </svg>
    <div id="head">000°</div>
  </section>

  <section class="panel" id="readout">
    <div>fps <b id="fps">–</b></div>
    <div>draws <b id="draws">–</b></div>
    <div>wind sea <b id="sea">0.6 m</b></div>
  </section>

  <div id="hint">
    <div><k>drag</k> orbit · <k>scroll</k> zoom</div>
    <div><k>hover</k> identify · <k>click</k> focus</div>
    <div><k>H</k> hide panels · <k>R</k> reset</div>
  </div>

  <div id="log">— the Meridian, three-master, has taken the tack off the point and is working up the reach —</div>
  <div id="tip"></div>
</div>

<div id="loader"><div class="box">
  <div class="t">Sounding the roads</div>
  <div id="bar"><div></div></div>
  <div id="lmsg">unfurling the chart…</div>
</div></div>

<script type="importmap">
{ "imports": {
    "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
    "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
}}
</script>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* ============================================================
   0. helpers
   ============================================================ */
const clamp=(v,a,b)=>v<a?a:v>b?b:v;
const lerp=(a,b,t)=>a+(b-a)*t;
const sstep=(e0,e1,x)=>{ const t=clamp((x-e0)/(e1-e0),0,1); return t*t*(3-2*t); };
const D2R=Math.PI/180;
function mulberry32(a){ return function(){ a|=0; a=a+0x6D2B79F5|0; let t=Math.imul(a^a>>>15,1|a);
  t=t+Math.imul(t^t>>>7,61|t)^t; return ((t^t>>>14)>>>0)/4294967296; }; }
const rnd=mulberry32(0x5E11A7);
const rr=(a,b)=>a+rnd()*(b-a); const ri=(a,b)=>Math.floor(a+rnd()*(b-a+1));
const jit=(c,a)=>c.r+rr(-a,a);
function vary(c,a){ return `rgb(${clamp(c.r+rr(-a,a),0,1)},${clamp(c.g+rr(-a,a),0,1)},${clamp(c.b+rr(-a,a),0,1)})`; }
const rgb=h=>{ const c=new THREE.Color(); c.setHex(h); return {r:c.r,g:c.g,b:c.b}; };
const col=c=>`rgb(${c.r},${c.g},${c.b})`;
function mixC(a,b,t){ return {r:lerp(a.r,b.r,t),g:lerp(a.g,b.g,t),b:lerp(a.b,b.b,t)}; }

/* ============================================================
   1. palette  (warm sandstone town, teal sea, brass & ink UI)
   ============================================================ */
const P = {
  deepSea:  rgb(0x0f313f),  midSea: rgb(0x175a6c),  shallow: rgb(0x2e8e95),
  foam:     rgb(0xf1e9d8),
  sand:     rgb(0xdcc39a),  wetSand: rgb(0xb99b70), shingle: rgb(0xa39583),
  grass:    rgb(0x5c7b45),  grassD:  rgb(0x466236), gorse: rgb(0xb9a83f),
  rock:     rgb(0x8c8474),  rockD:   rgb(0x6b6559), stone: rgb(0x9a8f7b),
  cobble:   rgb(0x7d7465),  cobble2: rgb(0x8f8674), kerb: rgb(0xa8a08c),
  wood:     rgb(0x8a6540),  woodD:   rgb(0x5d4430), woodL: rgb(0xa5825a),
  plank:    rgb(0xa97d4b),  plankD:  rgb(0x8a6440),
  hull:     rgb(0x2b2622),  hullW:   rgb(0xe8ddc7), copper: rgb(0x9c5f38), pitch: rgb(0x1c1917),
  sail:     rgb(0xf0e7d3),  sailD:   rgb(0xd3c6ae),
  rope:     rgb(0x7a6a52),  iron:    rgb(0x35322e),
  brass:    rgb(0xc9933f),  gold:    rgb(0xe0b764),
  roof:     rgb(0xa8553c),  roofD:   rgb(0x8a4530), slate: rgb(0x4a5158),
  plaster:  rgb(0xe8dcc4), plasterD:rgb(0xd8c9ad), wall: rgb(0xc3b394),
  shutter:  rgb(0x4e6b60), door: rgb(0x5d4430),
  glow:     rgb(0xffc85c),  dark:    rgb(0x2b2a27),
  cypress:  rgb(0x33502f),  olive:   rgb(0x6c7a4c),
  red:      rgb(0xb5443c), blue:    rgb(0x33506b), cream: rgb(0xf2ead8),
  white:    rgb(0xf4efe2),
};

/* ============================================================
   2. terrain field  (shared, in spirit, with the water shader)
   ============================================================ */
const shoreZ = x => 26 + 8*Math.sin(x*0.055) + 3*Math.cos(x*0.021) - 32*sstep(34,68,x);
function landTop(x,z){
  const s = shoreZ(x);
  let h = (z - s)*0.45 + 3.2;
  const d = Math.hypot(x-58, z-24);
  h = Math.max(h, 15*(1 - d/46));                 // the east point
  h += 1.8*Math.sin(x*0.085+z*0.05) + 1.4*Math.sin(z*0.12-x*0.06);
  const inTown = x>-40 && x<44 && z>26 && z<66;
  if (inTown) h = clamp(h, 6, 6);
  if (z>66) h = Math.min(h, 6 + (z-66)*0.32 + 2.2);
  if (z>s && z<s+12 && Math.abs(x)<40) h = 6;     // the quay
  return h>0 ? Math.floor(h) : 0;
}

/* ============================================================
   3. voxel builder
   ============================================================ */
class Vox{
  constructor(label='',desc=''){ this.items=[]; this.label=label; this.desc=desc; }
  set(label,desc){ this.label=label; this.desc=desc||label; return this; }
  v(x,y,z,c,sx=1,sy=1,sz=1){
    if (!(this._n=(this._n||0)+1 % 1e6) ) {}
    if ((this.items.length & 511)===0 && this._skip) return;
    this.items.push({x,y,z,c,sx,sy,sy,sz,label:this.label,desc:this.desc,cx:x,cy:y,cz:z});
    this.items[this.items.length-1]={x,y,z,c,sx,sy,sz,cx:x,cy:y,cz:z,label:this.label,desc:this.desc};
    return this;
  }
  box(x0,x1,y0,y1,z0,z1,c){ const a=[x0,x1],b=[y0,y1],d=[z0,z1];
    const mn=[Math.min(...a),Math.min(...b),Math.min(...d)], mx=[Math.max(...a),Math.max(...b),Math.max(...d)];
    this.items.push({cx:(mn[0]+mx[0])/2+0.5, cy:(mn[1]+mx[1])/2+0.5, cz:(mn[2]+mx[2])/2+0.5,
      sx:mx[0]-mn[0]+1, sy:mx[1]-mn[1]+1, sz:mx[2]-mn[2]+1, c, label:this.label, desc:this.desc});
    return this;
  }
  line(p,q,c,t=0.22){
    const dx=q[0]-p[0], dy=q[1]-p[1], dz=q[2]-p[2];
    const len=Math.hypot(dx,dy,dz), steps=Math.max(1,Math.round(len*1.35)), u=[dx,dy,dz].map(v=>v/(steps||1));
    const m=new THREE.Matrix4(), look=new THREE.Matrix4().lookAt(new THREE.Vector3(0,0,0),new THREE.Vector3(dx,dy,dz),new THREE.Vector3(0,1,0));
    const q4=new THREE.Quaternion().setFromRotationMatrix(look);
    for(let i=0;i<steps;i++){
      this.items.push({cx:p[0]+u[0]*(i+0.5), cy:p[1]+u[1]*(i+0.5), cz:p[2]+u[2]*(i+0.5),
        sx:t, sy:t, sz:1.06, c, q:q4, label:this.label, desc:this.desc});
    }
    return this;
  }
  cyl(x,y,z,r,h,c,base=0){
    for(let i=0;i<h;i++) for(let a=-r;a<=r;a++) for(let b=-r;b<=r;b++)
      if(a*a+b*b<=r*r+0.3) this.v(x+a,y+base+i,z+b,c);
    return this;
  }
  add(other){ for(const it of other.items) this.items.push(it); return this; }
}
const tmpM=new THREE.Matrix4(), tmpP=new THREE.Vector3(), tmpQ=new THREE.Quaternion(), tmpS=new THREE.Vector3();
let TOTAL=0;
function makeMesh(vox, mat, {cast=true, recv=true, meta=null}={}){
  const n=vox.items.length; if(!n) return null;
  const geo=new THREE.BoxGeometry(1,1,1);
  const mesh=new THREE.InstancedMesh(geo, mat, n);
  const arr=[];
  for(let i=0;i<n;i++){
    const it=vox.items[i];
    tmpP.set(it.cx,it.cy,it.cz);
    if(it.q) tmpQ.copy(it.q); else tmpQ.identity();
    tmpS.set(it.sx,it.sy,it.sz);
    tmpM.compose(tmpP,tmpQ,tmpS);
    mesh.setMatrixAt(i,tmpM);
    mesh.setColorAt(i, new THREE.Color().setRGB(it.c.r,it.c.g,it.c.b));
    arr.push({label:it.label, desc:it.desc});
  }
  mesh.instanceMatrix.needsUpdate=true;
  if(mesh.instanceColor) mesh.instanceColor.needsUpdate=true;
  mesh.castShadow=cast; mesh.receiveShadow=recv;
  mesh.userData.meta=arr;
  TOTAL+=n;
  return mesh;
}

/* ============================================================
   4. renderer / scene / lights
   ============================================================ */
const stage=document.getElementById('stage');
const renderer=new THREE.WebGLRenderer({antialias:true, powerPreference:'high-performance'});
renderer.setPixelRatio(Math.min(devicePixelRatio,1.75));
renderer.setSize(innerWidth,innerHeight);
renderer.outputColorSpace=THREE.SRGBColorSpace;
renderer.toneMapping=THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure=1.05;
renderer.shadowMap.enabled=true;
renderer.shadowMap.type=THREE.PCFSoftShadowMap;
stage.appendChild(renderer.domElement);

const scene=new THREE.Scene();
scene.fog=new THREE.FogExp2(0xd8ae84, 0.0042);

const camera=new THREE.PerspectiveCamera(50, innerWidth/innerHeight, 0.5, 2600);
camera.position.set(52,26,52);

const controls=new OrbitControls(camera, renderer.domElement);
controls.enableDamping=true; controls.dampingFactor=0.06;
controls.target.set(0,10,0);
controls.minDistance=14; controls.maxDistance=320;
controls.minPolarAngle=0.12; controls.maxPolarAngle=1.40;
controls.rotateSpeed=0.55; controls.zoomSpeed=0.9; controls.panSpeed=0.6;

const hemi=new THREE.HemisphereLight(0x9dc4d8, 0x6b5a42, 0.55); scene.add(hemi);
const sun=new THREE.DirectionalLight(0xffd39a, 2.6);
sun.castShadow=true;
sun.shadow.mapSize.set(2048,2048);
sun.shadow.camera.left=-140; sun.shadow.camera.right=140;
sun.shadow.camera.top=140;   sun.shadow.camera.bottom=-140;
sun.shadow.camera.near=1;    sun.shadow.camera.far=700;
sun.shadow.bias=-0.0007;     sun.shadow.normalBias=0.35;
const sunTarget=new THREE.Object3D(); sunTarget.position.set(0,8,0);
sun.target=sunTarget; scene.add(sun,sunTarget);
const fill=new THREE.DirectionalLight(0x6e8fa6, 0.35); fill.position.set(-120,90,140); scene.add(fill);

const lampLights=[];
function lamp(x,y,z,intensity,color=0xffc26a,dist=34){
  const l=new THREE.PointLight(color, intensity, dist, 2); l.position.set(x,y,z); scene.add(l); lampLights.push(l); return l;
}

/* static material shared by every static voxel */
const staticMat=new THREE.MeshLambertMaterial({color:0xffffff});

/* ============================================================
   5. sky
   ============================================================ */
const skyU={ uTop:{value:new THREE.Color(0x2d5c77)}, uHorizon:{value:new THREE.Color(0xf6b26e)},
  uSun:{value:new THREE.Vector3()}, uSunCol:{value:new THREE.Color(0xffd9a0)} };
const sky=new THREE.Mesh(new THREE.SphereGeometry(1100,40,22), new THREE.ShaderMaterial({
  side:THREE.BackSide, depthWrite:false, depthTest:false,
  uniforms:skyU,
  vertexShader:`varying vec3 vW; void main(){ vW=(modelMatrix*vec4(position,1.)).xyz;
    gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
  fragmentShader:`varying vec3 vW; uniform vec3 uTop,uHorizon,uSunCol,uSun;
    void main(){
      vec3 d=normalize(vW);
      float h=clamp(d.y,-1.,1.);
      vec3 c=mix(uHorizon,uTop,smoothstep(0.01,0.52,h));
      c=mix(c,uHorizon*0.9,smoothstep(0.0,-0.3,h));
      float sd=max(dot(d,normalize(uSun)),0.);
      c+=uSunCol*pow(sd,900.)*3.4;
      c+=uSunCol*pow(sd,26.)*0.55;
      c+=uSunCol*pow(sd,4.)*0.20;
      c+=(fract(sin(dot(gl_FragCoord.xy,vec2(12.9898,78.233)))*43758.5453)-0.5)*0.008;
      gl_FragColor=vec4(c,1.);
    }`
}));
sky.renderOrder=-1; sky.frustumCulled=false; scene.add(sky);

const seaFloor=new THREE.Mesh(new THREE.PlaneGeometry(4000,4000), new THREE.MeshLambertMaterial({color:0x0e2c38}));
seaFloor.rotation.x=-Math.PI/2; seaFloor.position.y=-2.6; scene.add(seaFloor);

/* ============================================================
   6. the voxel sea (GPU displaced columns)
   ============================================================ */
const WU={ uTime:{value:0}, uWind:{value:1}, uSunDir:{value:new THREE.Vector3(-0.73,0.13,0.46)},
  uSunCol:{value:new THREE.Color(0xffd39a)}, uSunInt:{value:2.6},
  uDeep:{value:new THREE.Color(0x0f313f)}, uShallow:{value:new THREE.Color(0x2e8e95)},
  uFoam:{value:new THREE.Color(0xf1e9d8)}, uSpark:{value:1},
  uShip:{value:new THREE.Vector2()}, uFwd:{value:new THREE.Vector2(0,1)} };

let waterMesh;
function buildWater(){
  const cells=[];
  for(let x=-48;x<=48;x++) for(let z=-48;z<=48;z++) cells.push([x,1,z]);
  for(let x=-96;x<=96;x+=2) for(let z=-96;z<=96;z+=2) if(Math.max(Math.abs(x),Math.abs(z))>=49) cells.push([x,2,z]);
  for(let x=-196;x<=196;x+=4) for(let z=-196;z<=196;z+=4) if(Math.max(Math.abs(x),Math.abs(z))>=97) cells.push([x,4,z]);

  const geo=new THREE.BoxGeometry(1,1,1);
  const aPos=new Float32Array(cells.length*3);
  const mesh=new THREE.InstancedMesh(geo, new THREE.MeshLambertMaterial({color:0xffffff, vertexColors:false}), cells.length);
  for(let i=0;i<cells.length;i++){
    const [x,c,z]=cells[i];
    tmpP.set(x,-6,z); tmpQ.identity(); tmpS.set(c*1.18, 14, c*1.18);
    tmpM.compose(tmpP,tmpQ,tmpS); mesh.setMatrixAt(i,tmpM);
    aPos[i*3]=x; aPos[i*3+1]=-6; aPos[i*3+2]=z;
  }
  geo.setAttribute('aPos', new THREE.InstancedBufferAttribute(aPos,3));
  mesh.instanceMatrix.needsUpdate=true;
  mesh.castShadow=false; mesh.receiveShadow=true; mesh.frustumCulled=false;
  TOTAL+=cells.length;

  const mat=mesh.material;
  mat.onBeforeCompile=(sh)=>{
    Object.assign(sh.uniforms, WU);
    sh.vertexShader=`
uniform float uTime; uniform float uWind;
uniform vec2 uShip; uniform vec2 uFwd;
attribute vec3 aPos;
varying vec3 vWC; varying vec3 vSN; varying float vFoam; varying float vSpk;
float wv(vec2 p,float t,float w){
  float h = 0.55*sin(p.x*0.140 + t*1.15)
          + 0.42*sin(p.y*0.115 - t*0.95)
          + 0.30*sin((p.x+p.y)*0.072 + t*0.62)
          + 0.18*sin(p.x*0.310 - p.y*0.240 + t*1.90)*(0.4+0.6*w);
  return h*w;
}
float sZ(float x){ return 26.0 + 8.0*sin(x*0.055) + 3.0*cos(x*0.021) - 32.0*smoothstep(34.0,68.0,x); }
float dseg(vec2 p,vec2 a,vec2 b){ vec2 pa=p-a, ba=b-a; float h=clamp(dot(pa,ba)/dot(ba,ba),0.,1.); return length(pa-ba*h); }
void main(){
  vec3 transformed=vec3(position);
  vec3 ip=aPos;
  float sy=length(instanceMatrix[1].xyz);
  vec2 q=ip.xz;
  float t=uTime, w=uWind;
  float H=wv(q,t,w);
  float E=1.1;
  float hx=wv(q+vec2(E,0.),t,w)-wv(q-vec2(E,0.),t,w);
  float hz=wv(q+vec2(0.,E),t,w)-wv(q-vec2(0.,E),t,w);
  vec3 n=normalize(vec3(-hx/(2.0*E),1.0,-hz/(2.0*E)));
  objectNormal=n;
  vec3 wp=(modelMatrix*instanceMatrix*vec4(transformed,1.)).xyz;
  float ang=atan(uFwd.y,uFwd.x); float cs=cos(-ang), sn=sin(-ang);
  vec2 rel=wp.xz-uShip; vec2 rl=vec2(rel.x*cs-rel.y*sn, rel.x*sn+rel.y*cs);
  float under=smoothstep(14.5,4.0,length(vec2(rl.x*0.52, rl.y)));
  vec2 wakeDir=vec2(-1.0,0.0);
  float behind=smoothstep(-6.0,-30.0,rl.x)*smoothstep(6.5,1.2,abs(rl.y));
  float churn=under*0.85+behind*0.42;
  churn*=0.55+0.45*sin(wp.x*0.9+wp.z*1.3+t*3.4);
  churn=clamp(churn,0.,1.);
  float sf=smoothstep(6.0,0.5,sZ(wp.x)-wp.z)*0.55;
  sf=max(sf, smoothstep(5.0,0.8,dseg(wp.xz,vec2(-34.0,25.0),vec2(-46.0,-42.0)))*0.55);
  vWC=wp;
  vSN=n;
  vFoam=clamp(churn*0.9+sf,0.,1.35);
  transformed.y += H/sy;
  vSpk = length(n);
  gl_Position=projectionMatrix*modelViewMatrix*instanceMatrix*vec4(transformed,1.);
}`.replace(/^\s+/,'');
    /* fully replace the vertex shader above (instancing done by hand) */
    sh.fragmentShader=sh.fragmentShader.replace('void main() {',`
uniform vec3 uDeep,uShallow,uFoam,uSunCol,uSunDir; uniform float uSunInt,uSpark;
varying vec3 vWC; varying vec3 vSN; varying float vFoam; varying float vSpk;
void main() {`);
    sh.fragmentShader=sh.fragmentShader.replace('#include <color_fragment>',`#include <color_fragment>
  float dm=clamp(length(vWC.xz)/150.0,0.0,1.0);
  vec3 wc=mix(uShallow,uDeep,smoothstep(0.18,0.95,dm));
  wc=mix(wc,uShallow,0.18+0.22*abs(sin(vWC.x*0.31)+cos(vWC.z*0.27))*0.5);
  diffuseColor.rgb=mix(wc,uFoam,clamp(vFoam,0.0,1.0));
  diffuseColor.rgb*=0.90+0.16*vSpk;`);
    sh.fragmentShader=sh.fragmentShader.replace('#include <dithering_fragment>',`#include <dithering_fragment>
  vec3 V=normalize(cameraPosition-vWC);
  vec3 H2=normalize(V+uSunDir);
  float ndl=max(dot(normalize(vSN),V),0.0);
  float g=step(0.44,fract(sin(dot(floor(vWC.xz*1.35),vec2(21.7,75.3)))*43758.5453));
  float spk=pow(max(dot(normalize(vSN),H2),0.0),42.0)*ndl*g;
  float fg=1.0;
  #ifdef USE_FOG
    fg=exp(-fogDensity*fogDensity*vFogDepth*vFogDepth);
  #endif
  gl_FragColor.rgb+=uSunCol*spk*uSunInt*2.4*uSpark*fg;
  gl_FragColor.rgb+=uSunCol*pow(max(dot(normalize(vSN),H2),0.0),7.0)*ndl*0.10*uSpark*fg;`);
  };
  mesh.customProgramCacheKey=()=> 'voxsea';
  scene.add(mesh);
  waterMesh=mesh;
}

/* ============================================================
   7. land, quay, breakwater
   ============================================================ */
const metas=[];   // {mesh}
function addMesh(vox, opts){ const m=makeMesh(vox, staticMat, opts); if(m){ metas.push(m); scene.add(m); } return m; }

function buildLand(){
  const v=new Vox('the green hill','granite, gorse and one bad road');
  for(let x=-96;x<=76;x++) for(let z=-58;z<=96;z++){
    const h=landTop(x,z); if(h<=0) continue;
    if (x*x+z*z>78*78 && h<7) continue;
    const s=shoreZ(x);
    const isQuay = (z>s && z<s+11 && x>-40 && x<44);
    const slope = Math.abs(landTop(x+1,z)-landTop(x-1,z))+Math.abs(landTop(x,z+1))-Math.abs(landTop(x,z-1));
    let top;
    if (isQuay) top=vary(P.cobble,0.045);
    else if (z<=s+2.5 && x>-40 && x<44) top=vary(P.wetSand,0.03);
    else if (h<=2) top=vary(P.shingle,0.04);
    else if (h>11 || slope>3.4) top=vary(P.rock,0.05);
    else if (h>7 && rnd()<0.10) top=vary(P.gorse,0.06);
    else top=rnd()<0.28?vary(P.grassD,0.03):vary(P.grass,0.04);
    v.v(x,h,z,top);
    const nb=Math.min(landTop(x+1,z),landTop(x-1,z),landTop(x,z+1),landTop(x,z-1));
    const bot=Math.min(h-2, nb-1, z<=s+1.5? -3 : 99);
    const face=(z<=s+1.5 && x>-40 && x<44);
    for(let y=h-1;y>=Math.max(-3,bot);y--){
      v.v(x,y,z, face? vary(P.stone,0.05) : (h>9? vary(P.rockD,0.05): vary(P.wall,0.04)) );
    }
    /* kerb along the quay edge */
    if (isQuay && z===Math.ceil(s)+1) v.v(x,h,z,P.kerb);
  }
  addMesh(v.set('the quay cobbles','nine inch granite, cambered to the gully'),{});
}

function buildBreakwater(){
  const v=new Vox('the breakwater','a pier of granite blocks, laid 1861');
  const A=[-34,25], B=[-46,-42];
  for(let i=0;i<=70;i++){
    const t=i/70;
    const cx=lerp(A[0],B[0],t)+Math.sin(t*9)*1.4, cz=lerp(A[1],B[1],t)+Math.cos(t*7)*1.6;
    const w=lerp(4.2,3.0,t);
    for(let a=-w;a<=w;a++) for(let b=-w;b<=w;b++){
      if(a*a+b*b>w*w+0.4) continue;
      const hh=Math.round(lerp(2.6,6.4,1-Math.abs(t-0.5)*1.2)+rr(-1.1,1.1));
      for(let y=-2;y<=hh;y++) v.v(Math.round(cx+a),y,Math.round(cz+b),
        y<1? vary(P.rockD,0.06) : (y>=hh? vary(P.stone,0.06): vary(P.rock,0.06)));
    }
  }
  addMesh(v);
}

function buildLighthouse(){
  const v=new Vox('the harbour light','fixed and revolving — 12 flashes every minute');
  const BX=-44, BZ=-42;
  for(let y=-2;y<=4;y++) for(let a=-5;a<=5;a++) for(let b=-5;b<=5;b++)
    if(a*a+b*b<=27) v.v(BX+a,y,BZ+b, vary(P.rockD,0.05));
  const bands=[[0,4,P.white],[4,8,P.red],[8,12,P.white],[12,16,P.red],[16,20,P.white]];
  for(const [y0,y1,c] of bands)
    for(let y=y0;y<y1;y++){ const r=y<10?3:2;
      for(let a=-4;a<=4;a++) for(let b=-4;b<=4;b++){ const d=a*a+b*b;
        if(d<=r*r+0.4 && d>=Math.max(0,(r-1.5)*(r-1.5)-0.5))
          v.v(BX+a,y+4,BZ+b, c===P.red? vary(P.red,0.05): vary(P.cream,0.04));
      }
    }
  v.box(BX-1,BX+1,6,20,BZ-1,BZ+1,vary(P.cream,0.02));           // solid core
  v.box(BX-3,BX+3,24,24,BZ-3,BZ+3,P.iron);                       // gallery
  v.box(BX-2,BX+2,25,27,BZ-2,BZ+2,P.glass||P.glow);               // lantern room (emissive later)
  for(const [a,b] of [[-3,0],[3,0],[0,-3],[0,3],[2,2],[-2,2],[2,-2],[-2,-2]]) v.v(BX+a,25,BZ+b,P.iron);
  for(let y=25;y<=27;y++) v.box(BX-1,BX+1,y,y,BZ-1,BZ+1,P.glow);
  for(let a=-3;a<=3;a++) for(let b=-3;b<=3;b++) if(a*a+b*b<=10) v.v(BX+a,28,BZ+b,vary(P.iron,0.03));
  v.v(BX,29,BZ+0,P.brass); v.v(BX,30,BZ,P.brass);
  /* keeper's cottage */
  const CX=BX+9, CZ=-32;
  v.set('the keeper\'s cottage','four families, three lights, one log book');
  v.box(CX-4,CX+4,5,11,CZ-3,CZ+3,vary(P.plaster,0.03));
  for(let i=0;i<5;i++) v.box(CX-4+i,CX-3+i,12+i,12+i,CZ-3,CZ+3,vary(P.slate,0.03));
  v.box(CX+4,CX-4+4,12,12,CZ-3,CZ+3,vary(P.slate,0.03));
  v.box(CX-1,CX,5,8,CZ+4,CZ+4,P.door);
  v.v(CX-3,8,CZ+4,P.glow); v.v(CX+3,8,CZ+4,P.glow);
  v.box(CX-3,CX-2,12,15,CZ+1,CZ+2,vary(P.stone,0.03));
  addMesh(v);
  lamp(BX,26.5,BZ,0,P.glow,120);
  return {x:BX, y:26.5, z:BZ};
}

/* ============================================================
   8. the town
   ============================================================ */
function house(v,x,z,w,d,h,o={}){
  const y=6;
  v.set(o.label||'the town', o.desc||'sandstone, terracotta, salt');
  v.box(x-w,x+w,y,y+h,z-d,z+d, vary(o.wall||P.plaster,0.035));
  const ridge=o.ridge||Math.ceil(w/2);
  for(let i=0;i<=ridge;i++) v.box(x-w+i, x+w-i, y+h+i, y+h+i, z-d, z+d, vary(o.roof||P.roof,0.045));
  for(let i=0;i<=ridge;i++) v.v(x-w+i,y+h+i,z-d-1,vary(P.roofD,0.04)), v.v(x+w-i,y+h+i,z-d-1,vary(P.roofD,0.04));
  v.box(x-1,x,y,y+3,z+d,z+d,P.door);
  const rows=Math.floor(h/4);
  for(let r=0;r<rows;r++) for(let c=-1;c<=1;c++){
    if(Math.abs(c)*3>=w) continue;
    const lit=rnd()<o.litRate??0.55;
    v.v(x+c*3,y+2+r*4,z+d+0.0? z+d+1:z+d, lit? P.glow : P.dark);
    v.v(x+c*3,y+3+r*4, z+d, lit? vary(P.glow,0.02):P.dark);
  }
  if(o.chimney) { v.box(x+w-2,x+w-1,y+h+1,y+h+5,z-1,z, vary(P.stone,0.03)); }
  if(o.pillars) for(let px=-w+1;px<=w-1;px+=3) v.box(x+px,x+px,y,y+4,z+d,z+d,vary(P.kerb,0.02));
}
function tree(x,z,type='cypress'){
  const t=new Vox(type==='cypress'?'the cypress grove':'the avenue', 'wind-shaped, salt-burnt');
  if(type==='cypress'){
    t.v(x,7,z,P.woodD); const h=ri(7,11);
    for(let i=0;i<h;i++){ const r=i<2?1:1; t.v(x-1,8+i,z-1,P.cypress); t.v(x-1,8+i,z+1,P.cypress); t.v(x+1,8+i,z-1,P.cypress); t.v(x+1,8+i,z+1,P.cypress);
      t.v(x,8+i,z-1,P.cypress); t.v(x,8+i,z+1,P.cypress); t.v(x-1,8+i,z,P.cypress); t.v(x+1,8+i,z,P.cypress); t.v(x,8+i,z,vary(P.cypress,0.03)); }
  } else {
    for(let i=0;i<4;i++) t.v(x,7+i,z,P.woodD);
    for(let a=-3;a<=3;a++) for(let b=-3;b<=3;b++) for(let c=-2;c<=2;c++)
      if(a*a+b*b+c*c<11 && rnd()<0.85) t.v(x+a,11+c,z+b, rnd()<0.3?vary(P.olive,0.04):vary(P.grass,0.05));
  }
  addMesh(t);
}
function lanternPost(x,z,h=6){
  const v=new Vox('the quay lamps','colza oil, wick trimmed at dusk');
  v.box(x,x,7,6+h,z,z,P.iron);
  v.v(x-1,7+h,z-1,P.iron); v.v(x+1,7+h,z-1,P.iron); v.v(x-1,7+h,z+1,P.iron); v.v(x+1,7+h,z+1,P.iron);
  v.v(x,7+h,z,P.glow); v.v(x,8+h,z,P.iron);
  addMesh(v);
  lamp(x,7.6+h,z,0);
}
function buildTown(){
  const v=new Vox();
  /* the customs house — the seat of harbour authority */
  house(v,-14,44,7,5,7,{wall:P.plaster,roof:P.roof,litRate:0.6,chimney:true,pillars:true,
    label:'the custom house',desc:'tides, tonnage, and three barrels of forbidden lace'});
  /* warehouses */
  house(v,6,50,8,7,6,{wall:P.wall,roof:P.slate,litRate:0.3,label:'No. 2 warehouse',desc:'guano, jute, and a great deal of rope'});
  house(v,22,42,6,5,5,{wall:P.plasterD,roof:P.roof,litRate:0.45,label:'the sail loft',desc:'canvas cut by daylight, stitched by candle'});
  house(v,-30,38,5,4,5,{wall:P.plaster,roof:P.roof,litRate:0.7,chimney:true,label:'the tavern',desc:'a room upstairs, a rowboat downstairs'});
  house(v,-4,58,6,5,6,{wall:P.plasterD,roof:P.roof,litRate:0.55,label:"the pilot's house",desc:'his flag is the signal you have been waiting for'});
  addMesh(v);
  /* windmill on the rise */
  const mv=new Vox('the mill','sea wind, stone ground, no wheat');
  const MX=32, MZ=64;
  for(let y=6;y<=19;y++){ const r=y<10?3:y<15?2:2;
    for(let a=-3;a<=3;a++) for(let b=-3;b<=3;b++){ const d=a*a+b*b; if(d<=r*r+0.4) mv.v(MX+a,y,MZ+b,vary(P.stone,0.05)); } }
  mv.box(MX-2,MX+2,20,20,MZ-2,MZ+2,P.woodD);
  addMesh(mv);
  const millHub=new THREE.Group(); millHub.position.set(MX-3.5,21,MZ); scene.add(millHub);
  const sailVox=new Vox('the mill sails','four canvases, strung with rope');
  for(let k=0;k<4;k++){
    const a=k*Math.PI/2;
    for(let i=1;i<=9;i++){ const px=Math.cos(a)*i, py=Math.sin(a)*i;
      sailVox.v(0,py+ (i*0.0), px*1, P.woodL);
      sailVox.v(0,py,px, P.woodL);
      for(let j=0;j<2;j++) sailVox.v(0,py+j,px+(j?1:0), P.woodL);
      if(i%2===0) sailVox.v(1,py,MX*0, P.sail);
    }
  }
  /* rebuild sails cleanly in the mill's own frame */
  sailVox.items.length=0;
  for(let k=0;k<4;k++){
    const a=k*Math.PI/2, ca=Math.cos(a), sa=Math.sin(a);
    for(let i=1;i<=10;i++){
      const px=ca*i, py=sa*i;
      const r=new THREE.Vector3(px,py,0);
      sailVox.items.push({cx:r.x, cy:r.y, cz:1.1, sx:1, sy:1, sz:1, c:vary(P.sail,0.02), label:'the mill sails', desc:'four canvases, strung with rope'});
      if(i%2===0) sailVox.items.push({cx:r.x, cy:r.y, cz:-0.9, sx:1, sy:1, sz:1, c:P.woodL, label:'the mill sails', desc:'four canvases, strung with rope'});
    }
    sailVox.items.push({cx:ca*5, cy:sa*5, cz:0, sx:Math.abs(ca)*11+0.9, sy:Math.abs(sa)*11+0.9, sz:0.8, c:vary(P.woodL,0.02), label:'the mill sails', desc:'four canvases, strung with rope'});
  }
  const millSails=makeMesh(sailVox, staticMat); millHub.add(millSails);
  millHub.userData.spin=true;
  animated.push({type:'mill', obj:millHub});
  lamp(32,20,64,0);
  /* trees, lamp posts, quay furniture */
  const cyp=[[-34,34],[-24,55],[-6,64],[10,62],[28,52],[40,44],[46,30],[-18,64],[18,66]];
  for(const [tx,tz] of cyp) tree(tx,tz,'cypress');
  tree(20,74,'round'); tree(-22,72,'round'); tree(4,78,'round');
  lanternPost(-16,20); lanternPost(4,24); lanternPost(24,18); lanternPost(-32,26);
  buildQuayFurniture();
  buildHeadland();
  buildHills();
}

function buildQuayFurniture(){
  const v=new Vox('quay cargo','jute, gin, machine parts, one live goat');
  for(let x=-36;x<=40;x+=9) v.box(x,x,7,8,shoreZ(x)+14|0,shoreZ(x)+14|0,P.iron);   // bollards
  /* crates & barrels in drifts along the wall */
  for(let i=0;i<26;i++){
    const x=ri(-34,38), z=shoreZ(x)+ri(4,10), s=ri(1,2), h=ri(1,3);
    v.box(x,x+s-1,7,7+h-1,z,z+s-1, rnd()<0.5?vary(P.wood,0.05):vary(P.woodL,0.05));
    if(rnd()<0.4) v.cyl(x+s,z+h+1,z,1,2,vary(P.woodD,0.05),0);
  }
  /* timber stack */
  for(let i=0;i<7;i++) for(let j=0;j<4;j++) v.box(-26+i,-26+i,7+j,7+j,17,22,vary(P.woodD,0.04));
  /* capstan */
  v.cyl(12,7,15,2,3,vary(P.woodL,0.04),0); v.v(12,11,15,P.iron);
  for(const [a,b] of [[-3,0],[3,0],[0,-3],[0,3]]) v.v(12+a,10,15+b,P.woodD);
  /* anchor display */
  v.box(-8,-8,7,11,22,22,P.iron); v.v(-10,8,22,P.iron); v.v(-6,8,22,P.iron); v.v(-8,12,22,P.iron);
  /* fish racks */
  for(let i=0;i<4;i++){ const x=-20+i*4; v.v(x,7,26,P.woodD); v.v(x,8,26,P.woodD); v.v(x,9,26,P.woodD); v.box(x-1,x+1,9,9,26,26,P.woodD); }
  /* steps down to the sea at the pier */
  for(let i=0;i<6;i++) v.box(30-i,32-i,7+i-0,7+i-0,26,29,P.stone);
  addMesh(v);
  /* pier out to the mooring */
  const p=new Vox('the landing steps','the only dry spot for a mile');
  for(let z=25;z<=33;z++) for(let x=20;x<=26;x++) p.v(x,6,z, vary(P.cobble2,0.04));
  for(let z=20;z<25;z++) for(let x=21;x<=25;x++) p.v(x,6,z,vary(P.wood,0.03));
  for(let i=0;i<5;i++) p.v(21,3,20+i,P.woodD), p.v(25,3,20+i,P.woodD);
  addMesh(p);
}

function buildHeadland(){
  const v=new Vox('the east point','a signal station, a flagstaff, a long view');
  const cx=58, cz=22;
  v.box(cx-4,cx+4,7,12,cz-3,cz+3,vary(P.plaster,0.03));
  for(let i=0;i<5;i++) v.box(cx-4+i,cx+4-i,13+i,13+i,cz-3,cz+3,vary(P.slate,0.03));
  v.box(cx-1,cx,7,10,cz+4,cz+4,P.door);
  v.v(cx-3,10,cz+5,P.glow);
  for(let y=12;y<=22;y++) v.v(cx+6,y,cz,P.woodD);
  addMesh(v);
  tree(cx-10,cz+6,'cypress'); tree(cx-12,cz-2,'cypress'); tree(cx+4,cz+12,'cypress');
}

function buildHills(){
  const v=new Vox('the far ridges','unmapped, unfrequented, unbothered');
  for(let i=-24;i<=24;i++){
    const a=i*0.055;
    const x=Math.sin(a)*220, z=120+Math.cos(a*0.7)*70;
    const h=10+14*Math.abs(Math.sin(i*0.41))+7*Math.sin(i*0.17);
    const s=6+Math.abs(Math.sin(i*0.3))*6;
    for(let a2=-s;a2<=s;a2++) for(let b2=-s;b2<=s;b2++){
      const hh=Math.max(0,h-Math.sqrt(a2*a2+b2*b2)*0.55);
      if(hh<=0) continue;
      v.v(Math.round(x+a2*2.2), Math.round(hh*1.2), Math.round(z+b2*2.2),
        hh>16? mixC(P.rockD,{r:.62,g:.66,b:.7},0.5): vary(P.grassD,0.03), 2.3, hh*2.5, 2.3);
    }
  }
  addMesh(v,{cast:false});
}

/* ============================================================
   9. the ship — the MERIDIAN
   ============================================================ */
const shipGroup=new THREE.Group(); scene.add(shipGroup);
let ensign, pilotFlag;
function buildShip(){
  const v=new Vox('the MERIDIAN','barque, 312 tons, arrived with the flood');
  const L=17, B=6;
  const beam=z=>{ const t=z/L; const s=t>=0 ? 1-Math.pow(t,1.75)*0.95 : 1-Math.pow(-t,2.6)*0.42; return B*Math.max(0.06,s); };
  const keelY=z=>1+2.8*Math.pow(Math.abs(z)/L,1.9);
  const deckY=z=>{ let y=9; if(z>11) y+=(z-11)*0.4; if(z<-9) y+=(-9-z)*0.35; return Math.round(y); };

  for(let z=-L;z<=L;z++){
    const b=beam(z), yb=Math.floor(keelY(z)), yd=deckY(z);
    for(let y=yb;y<yd;y++){
      const f=(y-yb)/Math.max(1,(yd-1-yb));
      const wf=0.42+0.58*Math.pow(Math.min(1,f+0.15),0.45);
      const w=Math.max(0,Math.round(b*wf));
      let c;
      if(y<2) c=P.pitch; else if(y<5) c=vary(P.copper,0.045);
      else if(y===5) c=vary(P.hull,0.02);
      else if(y===6||y===7) c=vary(P.hullW,0.025);
      else c=vary(P.hull,0.025);
      for(let x=-w;x<=w;x++){
        const edge=Math.abs(x)===w;
        if(edge && rnd()<0.12) continue;
        v.v(x,y,z,c);
      }
    }
    /* deck */
    const w=Math.max(0,Math.round(b*0.94)), yd2=deckY(z);
    for(let x=-w;x<=w;x++) v.v(x,yd2,z, (x%3===0)? vary(P.plankD,0.03):vary(P.plank,0.03));
    /* bulwark rail */
    const yr=yd2+1;
    for(let x=-w-1;x<=w+1;x++){
      if(Math.abs(x)>w) { if(z%2!==0) continue; }
      v.v(x,yr,z,vary(P.woodL,0.03));
    }
    if(Math.abs(z)>=L-1) v.box(-Math.round(b*0.5),Math.round(b*0.5),yd2-2,yd2+1,z,z,vary(P.woodL,0.02)); // transom
  }
  /* forecastle & poop decks */
  v.box(-4,4,11,11,11,17,vary(P.plank,0.03));
  v.box(-4,4,11,11,-17,-9,vary(P.plank,0.03));
  /* stern windows + name board */
  for(let x=-3;x<=3;x++) v.v(x,8,-18,P.glow);
  v.box(-4,4,6,6,-18,-18,P.gold);
  /* figurehead */
  v.v(0,11,18,mixC(P.cream,P.brass,0.3)); v.v(0,12,18,P.cream); v.v(0,13,17,P.cream); v.v(0,10,18,vary(P.woodD,0.02));
  /* anchor off the bow */
  v.v(5,10,16,P.iron); v.v(5,9,17,P.iron); v.v(5,11,15,P.iron);
  /* deck fittings */
  for(const hz of [-6,1,9]) v.box(-2,2,12,12,hz-1,hz+1, vary(P.plankD,0.02));
  v.cyl(3,10,-3,1,3,vary(P.woodL,0.03),0);
  for(let i=0;i<5;i++){ const x=Math.round(Math.cos(i*1.25)*2), z=Math.round(Math.sin(i*1.25)*2); v.v(3+x,12,-3+z,P.woodD); }
  /* cargo on deck */
  for(let i=0;i<6;i++){ const x=ri(-3,3), z=ri(-4,7); v.box(x,x+1,13,13+i%2,z,z+1, vary(P.wood,0.05)); }
  v.cyl(-3,13,4,1,2,vary(P.woodD,0.05),0); v.cyl(-3,13,-7,1,2,vary(P.woodD,0.05),0);
  /* crew */
  const crew=[[-1,12,3],[2,12,8],[0,12,-2],[-3,12,-11],[3,12,13],[0,12,16]];
  for(const [x,y,z] of crew){
    v.v(x,y,z, rnd()<0.5?P.blue:P.red); v.v(x,y+1,z,vary(P.wood,0.02));
    v.v(x,y+2,z, mixC(P.cream,P.sand,0.4));
  }
  /* masts, yards, sails */
  const masts=[
    {z:6,  low:10, top:22, head:30, yards:[{y:20,w:13,set:false},{y:25,w:11,set:true},{y:28,w:8,set:true}]},
    {z:-2, low:10, top:25, head:35, yards:[{y:22,w:14,set:false},{y:27,w:12,set:true},{y:31,w:9,set:true}]},
    {z:-11,low:10, top:19, head:25, yards:[{y:17,w:11,set:false},{y:21,w:9,set:false},{y:24,w:7,set:false}]},
  ];
  for(const m of masts){
    v.box(-1,1,m.low,m.top,m.z,m.z, vary(P.woodD,0.02));
    v.v(0,m.top+1,m.z, vary(P.woodD,0.02)); v.v(0,m.top+2,m.z, vary(P.woodD,0.02));
    for(let y=m.top+3;y<=m.head;y++) v.v(0,y,m.z,vary(P.woodL,0.02));
    v.v(0,m.head+1,m.z,P.brass);
    for(const yd of m.yards){
      v.box(-yd.w/2,yd.w/2,yd.y,yd.y,m.z,m.z, vary(P.woodL,0.025));
      if(!yd.set){ /* furled */
        for(let x=-yd.w/2+1;x<=yd.w/2-1;x++) v.v(x,yd.y-1,m.z,vary(P.sail,0.02));
        for(let x=-yd.w/2+1;x<=yd.w/2-1;x++) v.v(x,yd.y-2,m.z,vary(P.sailD,0.02));
      } else squareSail(v, m.z, yd.y, yd.w, yd.y>=27?6:7);
    }
    /* crosstrees & rigging */
    v.box(-2,2,m.top,m.top,m.z,m.z,P.woodD);
    v.box(m.z===-2?-3:-2, m.z===-2?3:2, m.top,m.top, m.z-1,m.z+1, P.woodD);
    v.line([0,m.head,m.z],[0,18,30],P.rope,0.24);                       // forestay
    v.line([0,m.head,m.z],[0,10,-16],P.rope,0.2);                       // backstay
    for(const s of [-1,1]){
      v.line([0,m.top,m.z],[s*7,11,m.z+2],P.rope,0.18);
      v.line([0,m.top,m.z],[s*7,11,m.z-2],P.rope,0.18);
      v.line([0,m.head,m.z],[s*5,13,m.z],P.rope,0.16);
    }
    for(const yd of m.yards){
      v.line([0,m.head,m.z],[-yd.w/2,yd.y+1,m.z],P.rope,0.14);
      v.line([0,m.head,m.z],[ yd.w/2,yd.y+1,m.z],P.rope,0.14);
    }
  }
  /* bowsprit & jibs */
  v.line([0,10,14],[0,17,27],P.woodL,1.3);
  v.line([0,17,27],[0,20,33],P.woodL,0.7);
  triSail(v,[0,30,6],[0,17,27],[0,21,14]);
  triSail(v,[0,25,6],[0,17,27],[0,19,18]);
  triSail(v,[0,35,-2],[0,30,6],[0,24,10]);
  /* halyards & braces */
  v.line([0,18,30],[0,20,14],P.rope,0.14);
  /* davit boat at the stern */
  for(const s of [-1,1]){ v.box(s*3,s*3,12,14,-15,-15,P.woodD); v.v(s*3,15,-14,P.woodD); }
  v.box(-2,2,12,12,-16,-13,vary(P.cream,0.02));
  /* ensign gaff + flagpole */
  v.line([0,20,-11],[0,25,-17],P.woodL,0.5);
  addMesh(v);
  const shipStatic=makeMesh(v, staticMat);
  /* we already added; keep reference for raycasting */
  metas[metas.length-1].userData.ship=true;

  /* flags */
  ensign=makeFlag(0,25.5,-18,7,4,[[0.55,0.62,P.red],[0.55,0.62,P.blue]], -1);
  shipGroup.add(ensign.mesh);
  pilotFlag=makeFlag(0,29,6,4,3,[[0.5,0.5,P.glow],[0.5,0.5,P.blue]], 0);
  shipGroup.add(pilotFlag.mesh);

  shipGroup.position.set(0,5,12);
}
function squareSail(v, cz, cy, w, h){
  const half=Math.round(w/2);
  for(let x=-half;x<=half;x++){
    const nx=x/half;
    const billow=-1.4*(1-Math.abs(nx)*0.6);
    const foot=Math.round(-1.2*(1-nx*nx));
    for(let dy=0;dy<h;dy++){
      const yy=cy-dy+ (dy>2? foot*(dy/h):0);
      const zz=cz+Math.round(billow*Math.min(1,dy/(h*0.55)));
      const c=(Math.abs(x)%4===0)?vary(P.sailD,0.015):(rnd()<0.12?vary(P.sailD,0.02):vary(P.sail,0.015));
      v.v(x,yy,zz,c);
      if(dy<h-1) v.v(x,yy,zz-1,rnd()<0.3?vary(P.sailD,0.02):vary(P.sail,0.02));
    }
    v.v(x,cy-h+foot,cz,vary(P.sailD,0.02));
  }
}
function triSail(v,A,B,C){
  for(let i=1;i<=14;i++){
    const t=i/14;
    const p=[lerp(A[0],B[0],t),lerp(A[1],B[1],t),lerp(A[2],B[2],t)];
    const q=[lerp(A[0],C[0],t),lerp(A[1],C[1],t),lerp(A[2],C[2],t)];
    const steps=Math.max(1,Math.round(Math.hypot(q[0]-p[0],q[1]-p[1],q[2]-p[2])));
    for(let k=0;k<=steps;k++){
      const s=k/steps;
      const x=Math.round(lerp(p[0],q[0],s)), y=Math.round(lerp(p[1],q[1],s)), z=Math.round(lerp(p[2],q[2],s));
      v.v(x,y,z, k%3===0?vary(P.sailD,0.02):vary(P.sail,0.018));
    }
  }
}
function makeFlag(x,y,z,w,h,pattern,dir=1){
  const items=[];
  for(let i=0;i<w;i++) for(let j=0;j<h;j++){
    const pu=(i+0.5)/w, pv=(j+0.5)/h;
    let c=pattern[0][2];
    if(pattern.length>1){ c = (pu<pattern[0][0]&&pv<pattern[0][1])?pattern[0][2]:pattern[1][2]; }
    items.push({i,j,c});
  }
  const geo=new THREE.BoxGeometry(1,1,1);
  const mesh=new THREE.InstancedMesh(geo, staticMat, items.length);
  for(let k=0;k<items.length;k++) mesh.setColorAt(k,new THREE.Color().setRGB(items[k].c.r,items[k].c.g,items[k].c.b));
  mesh.instanceColor.needsUpdate=true; mesh.castShadow=true;
  TOTAL+=items.length;
  const obj={mesh,x,y,z,w,h,items,dir};
  animated.push({type:'flag',obj});
  return obj;
}

/* ============================================================
   10. living things
   ============================================================ */
const animated=[];
let gulls=[], smoke, smokeP=[], clouds, cloudDrift=0, millHub;
let rowboat, boatOars=[];

function waveH(x,z,t,w){
  let h = 0.55*Math.sin(x*0.140 + t*1.15)
        + 0.42*Math.sin(z*0.115 - t*0.95)
        + 0.30*Math.sin((x+z)*0.072 + t*0.62)
        + 0.18*Math.sin(x*0.310 - z*0.240 + t*1.90)*(0.4+0.6*w);
  return h*w;
}

function buildLife(){
  /* gulls */
  const white=new THREE.MeshLambertMaterial({color:0xf4efe2});
  const dark=new THREE.MeshLambertMaterial({color:0x4a4f58});
  const beak=new THREE.MeshLambertMaterial({color:0xe0b764});
  const bg=new THREE.BoxGeometry(1,1,1);
  for(let i=0;i<7;i++){
    const g=new THREE.Group();
    const body=new THREE.Mesh(bg,white); body.scale.set(1.2,1.2,3.4); g.add(body);
    const head=new THREE.Mesh(bg,white); head.position.set(0,0.6,2.1); g.add(head);
    const b=new THREE.Mesh(bg,beak); b.position.set(0,0.4,3.2); g.add(b);
    const wl=new THREE.Mesh(bg,dark); wl.geometry=bg;
    const wr=new THREE.Mesh(bg,dark);
    const pl=new THREE.Group(), pr=new THREE.Group();
    wl.scale.set(6,0.4,1.8); wr.scale.set(6,0.4,1.8);
    wl.position.set(3.2,0.3,0); wr.position.set(-3.2,0.3,0);
    pl.add(wl); pr.add(wr); g.add(pl,pr);
    g.userData={r:rr(28,62), a:rr(0,6.28), sp:rr(0.11,0.22)*(rnd()<.5?1:-1), y:rr(19,34), cx:rr(-14,26), cz:rr(-18,14), pl, pr, ph:rr(0,6)};
    g.castShadow=true; g.traverse(o=>{o.castShadow=true;});
    scene.add(g); gulls.push(g);
    animated.push({type:'gull', obj:g});
  }
  /* chimney & deck smoke */
  const N=110;
  const geo=new THREE.BoxGeometry(1,1,1);
  smoke=new THREE.InstancedMesh(geo, new THREE.MeshLambertMaterial({}), N);
  smoke.castShadow=false; smoke.frustumCulled=false;
  for(let i=0;i<N;i++) smokeP.push({age:rnd()*4, life:rr(3.5,6), src:i%2, s:rr(0.7,1.4), dx:rr(-1,1), dz:rr(-1,1)});
  TOTAL+=N; scene.add(smoke);
  /* clouds */
  const cv=new Vox('the weather','a soft bank coming over the point');
  for(let c=0;c<16;c++){
    const cx=rr(-220,220), cy=rr(58,96), cz=rr(-220,220);
    const n=ri(14,34);
    for(let k=0;k<n;k++){
      const s=ri(3,8);
      cv.v(Math.round(cx+rr(-18,18)), Math.round(cy+rr(-7,7)), Math.round(cz+rr(-18,18)),
        mixC(P.white,{r:.86,g:.84,b:.82},rnd()*0.5), s, s*0.55, s);
    }
  }
  clouds=makeMesh(cv, new THREE.MeshLambertMaterial({fog:false}), {cast:false, recv:false});
  scene.add(clouds);
  /* the ship's boat */
  const bv=new Vox('the ship\'s boat','four oars, one cox, a good argument');
  for(let z=-4;z<=4;z++){
    const w=Math.round(2*Math.sqrt(1-(z/4.5)**2))+ (z>2?1:0);
    for(let x=-w;x<=w;x++) bv.v(x,0,z, vary(P.wood,0.04));
    if(Math.abs(x)===w) for(let y=1;y<=2;y++) bv.v(x,y,z,vary(P.woodL,0.03));
  }
  for(let z=-3;z<=3;z++){ bv.v(-2,1,z,vary(P.woodD,0.02)); bv.v(2,1,z,vary(P.woodD,0.02)); }
  bv.v(0,2,1,vary(P.blue,0.02)); bv.v(1,2,1,vary(P.red,0.02)); bv.v(0,3,1,P.sand);
  bv.v(0,2,-2,vary(P.cream,0.02)); bv.v(0,3,-2,P.sand);
  rowboat=new THREE.Group();
  const bmesh=makeMesh(bv, staticMat); bmesh.position.y=0; rowboat.add(bmesh);
  for(const s of [-1,1]) for(const z of [-1,2]){
    const oar=new THREE.Group(); const m=new THREE.Mesh(new THREE.BoxGeometry(0.4,0.4,5), new THREE.MeshLambertMaterial({color:0xa5825a}));
    m.position.z=2.2; m.castShadow=true; oar.add(m); oar.position.set(s*2.2,1.6,z); rowboat.add(oar); boatOars.push(oar);
  }
  rowboat.traverse(o=>o.castShadow=true);
  scene.add(rowboat);
}

/* ============================================================
   11. moods
   ============================================================ */
const MOODS={
  golden:{ label:'GOLDEN HOUR',
    sun:{a:145, e:7.6, c:0xffd39a, i:2.6}, hemi:{s:0x9dc4d8,g:0x6b5a42,i:0.55},
    sky:{top:0x2d5c77, hor:0xf7b26e, sun:0xffd9a0},
    fog:{c:0xd8ae84, d:0.0042}, sea:{deep:0x0f313f, sh:0x2e8e95, fo:0xf1e9d8, sp:1},
    exp:1.05, lamp:0.55, beam:0.055 },
  blue:{ label:'BLUE HOUR',
    sun:{a:168, e:1.5, c:0x93aed0, i:0.75}, hemi:{s:0x37536b,g:0x2c2a28,i:0.38},
    sky:{top:0x0a1626, hor:0x31597a, sun:0xa9c4e0},
    fog:{c:0x1c3347, d:0.0055}, sea:{deep:0x071a26, sh:0x17495a, fo:0xa8c6cf, sp:0.55},
    exp:1.18, lamp:2.6, beam:0.14 },
  fret:{ label:'SEA FRET',
    sun:{a:60, e:34, c:0xc7d0d4, i:1.35}, hemi:{s:0x9aa4a8,g:0x59544a,i:0.9},
    sky:{top:0x99a3a7, hor:0xbec4c4, sun:0xd7dedb},
    fog:{c:0xa9b2b5, d:0.0078}, sea:{deep:0x1f3137, sh:0x3f5b62, fo:0xe4e8e5, sp:0.22},
    exp:1.0, lamp:1.3, beam:0.075 },
};
let moodName='golden';
const cur={ sunCol:new THREE.Color(), sunI:0, sunA:145, sunE:7.6,
  hemiS:new THREE.Color(), hemiG:new THREE.Color(), hemiI:0,
  skyT:new THREE.Color(), skyH:new THREE.Color(), skyS:new THREE.Color(),
  fogC:new THREE.Color(), fogD:0.0042, deep:new THREE.Color(), shal:new THREE.Color(),
  foamC:new THREE.Color(), spark:1, exp:1.05, lamp:0.55, beam:0.055 };
function applyMood(name){ moodName=name; setLog(name==='golden'? '— golden hour on the roads; the flood makes three feet in the reach —'
  : name==='blue' ? '— dusk. every window in town a square of amber; the light every four seconds —'
  : '— sea fret rolling up the reach, the town gone, only the bell on the point —'); }
function initMood(){
  const m=MOODS[moodName];
  cur.sunCol.setHex(m.sun.c); cur.sunI=m.sun.i; cur.sunA=m.sun.a; cur.sunE=m.sun.e;
  cur.hemiS.setHex(m.hemi.s); cur.hemiG.setHex(m.hemi.g); cur.hemiI=m.hemi.i;
  cur.skyT.setHex(m.sky.top); cur.skyH.setHex(m.sky.hor); cur.skyS.setHex(m.sky.sun);
  cur.fogC.setHex(m.fog.c); cur.fogD=m.fog.d;
  cur.deep.setHex(m.sea.deep); cur.shal.setHex(m.sea.sh); cur.foamC.setHex(m.sea.fo); cur.spark=m.sea.sp;
  cur.exp=m.exp; cur.lamp=m.lamp; cur.beam=m.beam;
}
let lampsOn=true, beamOpacity=0.055;
function tickMood(dt){
  const m=MOODS[moodName], k=1-Math.pow(0.001,dt);
  cur.sunCol.lerp(new THREE.Color(m.sun.c),k); cur.sunI=lerp(cur.sunI,m.sun.i,k);
  cur.sunA=lerp(cur.sunA,m.sun.a,k); cur.sunE=lerp(cur.sunE,m.sun.e,k);
  cur.hemiS.lerp(new THREE.Color(m.hemi.s),k); cur.hemiG.lerp(new THREE.Color(m.hemi.g),k); cur.hemiI=lerp(cur.hemiI,m.hemi.i,k);
  cur.skyT.lerp(new THREE.Color(m.sky.top),k); cur.skyH.lerp(new THREE.Color(m.sky.hor),k); cur.skyS.lerp(new THREE.Color(m.sky.sun),k);
  cur.fogC.lerp(new THREE.Color(m.fog.c),k); cur.fogD=lerp(cur.fogD,m.fog.d,k);
  cur.deep.lerp(new THREE.Color(m.sea.deep),k); cur.shal.lerp(new THREE.Color(m.sea.sh),k);
  cur.foamC.lerp(new THREE.Color(m.sea.fo),k); cur.spark=lerp(cur.spark,m.sea.sp,k);
  cur.exp=lerp(cur.exp,m.exp,k); cur.lamp=lerp(cur.lamp,m.lamp,k); cur.beam=lerp(cur.beam,m.beam,k);
  const a=cur.sunA*D2R, e=cur.sunE*D2R;
  const sp=new THREE.Vector3(Math.cos(e)*Math.cos(a), Math.sin(e), Math.cos(e)*Math.sin(a)).multiplyScalar(260).add(new THREE.Vector3(0,8,0));
  sun.position.copy(sp); sun.color.copy(cur.sunCol); sun.intensity=cur.sunI;
  fill.intensity=lerp(0.1,0.5,1-sun.intensity/3);
  hemi.color.copy(cur.hemiS); hemi.groundColor.copy(cur.hemiG); hemi.intensity=cur.hemiI;
  skyU.uTop.value.copy(cur.skyT); skyU.uHorizon.value.copy(cur.skyH); skyU.uSunCol.value.copy(cur.skyS);
  skyU.uSun.value.copy(sp).normalize();
  scene.fog.color.copy(cur.fogC); scene.fog.density=cur.fogD;
  seaFloor.material.color.copy(cur.deep);
  renderer.toneMappingExposure=cur.exp;
  WU.uSunDir.value.copy(sp).normalize(); WU.uSunCol.value.copy(cur.sunCol);
  WU.uSunInt.value=cur.sunI; WU.uDeep.value.copy(cur.deep); WU.uShallow.value.copy(cur.shal);
  WU.uFoam.value.copy(cur.foamC); WU.uSpark.value=cur.spark;
  const li=lampsOn?cur.lamp:0;
  for(const l of lampLights) l.intensity=li;
  beamMat.opacity=beamOpacity=cur.beam*(lampsOn?1.6:0.25);
  lanternGlow.forEach((m,i)=>{ m.color.copy(cur.glow||new THREE.Color(0xffc85c)).multiplyScalar(lampsOn?1.4:0.6); });
}

/* rotating light beam */
let beamGroup, beamMat, lanternGlow=[];
function buildBeam(){
  beamGroup=new THREE.Group();
  beamMat=new THREE.MeshBasicMaterial({color:0xffe6b8, transparent:true, opacity:0.05,
    blending:THREE.AdditiveBlending, depthWrite:false, fog:false, side:THREE.DoubleSide});
  for(const dir of [0, Math.PI]){
    const g=new THREE.Group();
    for(let i=0;i<7;i++){
      const m=new THREE.Mesh(new THREE.BoxGeometry(70-i*9, 3.4-i*0.32, 5+i*1.6), beamMat);
      m.position.set(4+i*7, 0, 0); g.add(m);
    }
    g.rotation.y=dir; beamGroup.add(g);
  }
  beamGroup.position.set(-44,26.5,-42); scene.add(beamGroup);
}

/* ============================================================
   12. interface
   ============================================================ */
const VIEWS={
  roads:  {p:[52,26,52],   t:[0,10,0],   cap:'the roads at anchor — the whole reach in one glass'},
  quay:   {p:[26,9.5,16],  t:[2,12,-10], cap:'from the landing steps, where the pilot comes off'},
  light:  {p:[-22,13,-16], t:[-44,22,-42],cap:'the point — twelve flashes a minute, 12 miles'},
  quarter:{p:[24,17,32],   t:[0,14,-4],  cap:'a bow quarter aboard the MERIDIAN'},
  chart:  {p:[2,122,58],   t:[0,4,0],    cap:'the chart — shoal, quay, and the fairway between'}
};
let curView='roads', autoOrbit=false;
function setView(name, dur=1500){
  curView=name; const v=VIEWS[name];
  tweenCam(new THREE.Vector3(...v.p), new THREE.Vector3(...v.t), dur);
  setLog('— '+v.cap+' —');
  [...document.querySelectorAll('#views button')].forEach(b=>b.classList.toggle('on', b.dataset.k===name));
}
function tweenCam(pos,tgt,dur=1400){
  const p0=camera.position.clone(), t0=controls.target.clone(), s0=performance.now();
  tween={p0,t0,p1:pos,t1:tgt,s0,dur};
}
let tween=null;
const ui=document.getElementById('ui');
const logEl=document.getElementById('log');
function setLog(txt){ logEl.classList.add('flash'); setTimeout(()=>{ logEl.innerHTML=txt; logEl.classList.remove('flash'); },300); }

function buildUI(){
  const vw=document.getElementById('views');
  const labels={roads:'Roads', quay:'Quay', light:'The Light', quarter:'Quarter', chart:'Chart'};
  for(const k in VIEWS){ const b=document.createElement('button'); b.dataset.k=k; b.innerHTML=`<i></i>${labels[k]}`;
    b.onclick=()=>setView(k); if(k===curView) b.classList.add('on'); vw.appendChild(b); }
  const mm=document.getElementById('moods');
  for(const k in MOODS){ const b=document.createElement('button'); b.dataset.k=k; b.innerHTML=`<i></i>${MOODS[k].label}`;
    b.onclick=()=>applyMood(k); if(k===moodName) b.classList.add('on'); mm.appendChild(b); }
  const wind=document.getElementById('wind'), windv=document.getElementById('windv');
  const names=[[0,'light air'],[20,'light breeze'],[40,'gentle'],[60,'moderate'],[80,'fresh'],[100,'strong gale'],[120,'whole gale'],[999,'storm']];
  const upd=()=>{ const w=wind.value/100; WU.uWind.value=0.35+w*1.25;
    let n='storm'; for(const [v,s] of names) if(wind.value<v){n=s;break;}
    windv.textContent=`${Math.round(wind.value/12)} · ${n}`;
    document.getElementById('sea').textContent=(0.25+w*2.6).toFixed(2)+' m'; };
  wind.addEventListener('input',upd); upd();
  document.getElementById('togLamps').onclick=e=>{ lampsOn=!lampsOn; e.currentTarget.classList.toggle('on',lampsOn); };
  document.getElementById('togOrbit').onclick=e=>{ autoOrbit=!autoOrbit; e.currentTarget.classList.toggle('on',autoOrbit); };
  addEventListener('keydown',e=>{
    const k=e.key.toLowerCase();
    if(k>='1'&&k<='5'){ const n=Object.keys(VIEWS)[+k-1]; if(n) setView(n); }
    if(k==='m'){ const ks=Object.keys(MOODS); applyMood(ks[(ks.indexOf(moodName)+1)%ks.length]);
      [...document.querySelectorAll('#moods button')].forEach(b=>b.classList.toggle('on', b.dataset.k===moodName)); }
    if(k==='h') ui.classList.toggle('hidden-ui');
    if(k==='r') setView('roads');
  });
  /* compass ticks */
  const g=document.getElementById('ticks'); let s='';
  for(let i=0;i<36;i++){ const a=i*10*D2R, r0=i%3?28:31;
    s+=`<line x1="${Math.sin(a)*r0}" y1="${-Math.cos(a)*r0}" x2="${Math.sin(a)*33}" y2="${-Math.cos(a)*33}" stroke="rgba(201,162,74,${i%3?.2:.5})" stroke-width="1"/>`; }
  g.innerHTML=s;
}

/* hover identify */
const ray=new THREE.Raycaster(); ray.params.Line={threshold:0};
const ptr=new THREE.Vector2(), tip=document.getElementById('tip');
let hoverTimer=0, hovered=null;
const hlGeo=new THREE.BoxGeometry(1,1,1);
const hl=new THREE.LineSegments(new THREE.EdgesGeometry(hlGeo), new THREE.LineBasicMaterial({color:0xf2cd7c, transparent:true, opacity:.9, depthTest:true}));
hl.visible=false; scene.add(hl);
let mouseX=0, mouseY=0, mouseIn=false;
addEventListener('pointermove',e=>{ mouseX=e.clientX; mouseY=e.clientY; ptr.set((e.clientX/innerWidth)*2-1, -(e.clientY/innerHeight)*2+1); mouseIn=true; });
addEventListener('pointerleave',()=>mouseIn=false);
renderer.domElement.addEventListener('click',()=>{
  if(!hovered) return;
  const p=hovered.point;
  const dir=new THREE.Vector3().subVectors(camera.position, p).normalize();
  const d=clamp(p.distanceTo(camera.position)*0.62, 16, 90);
  tweenCam(new THREE.Vector3().copy(p).addScaledVector(dir, d).setY(Math.max(p.y+d*0.22, 8)), p.clone(), 1100);
});
function pick(){
  if(!mouseIn) return;
  ray.setFromCamera(ptr, camera);
  const hits=ray.intersectObjects(metas, false);
  if(hits.length){
    const h=hits[0], id=h.instanceId, m=h.object, meta=m.userData.meta[id];
    if(!hovered || hovered.id!==id || hovered.mesh!==m){
      hovered={id,mesh:m,meta,point:h.point.clone(),mat:h.object.getMatrixAt};
      m.getMatrixAt(id, tmpM);
      hl.visible=true; hl.matrixAutoUpdate=false;
      tmpM.decompose(tmpP, tmpQ, tmpS);
      hl.position.copy(tmpP); hl.scale.copy(tmpS).multiplyScalar(1.04);
      tip.innerHTML=`<b>${meta.label}</b>`;
      tip.classList.add('show');
      setLog(`— <i>${meta.label}</i> · ${meta.desc} —`);
    }
    tip.style.left=mouseX+'px'; tip.style.top=mouseY+'px';
    /* ship wake uniform needs the point even when not on the ship */
  } else { hovered=null; hl.visible=false; tip.classList.remove('show'); }
}

/* ============================================================
   13. loop
   ============================================================ */
const clock=new THREE.Clock();
let frames=0, fpsT=0, fps=0, downgraded=false;
const needle=document.getElementById('needle'), headEl=document.getElementById('head');
const SHIP={ x:0, z:12, yaw:-0.32, speed:0 };
const shipHome=new THREE.Vector3(0,5,12);

function animate(){
  requestAnimationFrame(animate);
  const dt=Math.min(clock.getDelta(),0.05), t=clock.elapsedTime;
  WU.uTime.value=t;
  tickMood(dt);

  /* --- camera tween --- */
  if(tween){
    const k=clamp((performance.now()-tween.s0)/tween.dur,0,1);
    const e=k<0.5? 4*k*k*k : 1-Math.pow(-2*k+2,3)/2;
    camera.position.lerpVectors(tween.p0,tween.p1,e);
    controls.target.lerpVectors(tween.t0,tween.t1,e);
    if(k>=1) tween=null;
  } else if(autoOrbit){
    const a=camera.position.clone().sub(controls.target);
    const ang=dt*0.06;
    camera.position.set(controls.target.x + a.x*Math.cos(ang)-a.z*Math.sin(ang), camera.position.y,
                        controls.target.z + a.x*Math.sin(ang)+a.z*Math.cos(ang));
  }
  controls.update();

  /* --- the ship rides the sea --- */
  const w=WU.uWind.value;
  SHIP.yaw=-0.32+Math.sin(t*0.07)*0.05;
  SHIP.x=shipHome.x+Math.sin(t*0.035)*6;
  SHIP.z=shipHome.z+Math.cos(t*0.028)*4.5;
  const fx=Math.sin(SHIP.yaw), fz=Math.cos(SHIP.yaw);
  const sam=(lx,lz)=>{ const wx=SHIP.x+fx*lx+fz*lz, wz=SHIP.z-fx*lz+fz*lx; return waveH(wx,wz,t,w*0.75); };
  const hF=sam(0,15), hA=sam(0,-15), hR=sam(5.5,0), hL=sam(-5.5,0);
  shipGroup.position.set(SHIP.x, (hF+hA+hR+hL)/4 + 4.1, SHIP.z);
  shipGroup.rotation.y=SHIP.yaw+Math.PI;
  shipGroup.rotation.z=lerp(shipGroup.rotation.z,(hL-hR)/11*0.9,0.08);
  shipGroup.rotation.x=lerp(shipGroup.rotation.x,(hA-hF)/30*0.7,0.08);
  WU.uShip.value.set(SHIP.x,SHIP.z); WU.uFwd.value.set(fx,fz);

  /* --- flags --- */
  for(const a of animated){
    if(a.type==='flag'){
      const o=a.obj;
      for(let k=0;k<o.items.length;k++){
        const it=o.items[k];
        const ph=o.dir*1;
        const wob=Math.sin(t*(2.2+w*1.6)+it.i*0.7+it.j*0.35)*(0.18+0.35*w)*(it.i/o.w);
        const sag=-Math.sin(it.i/o.w*Math.PI)*0.25;
        tmpP.set(o.x+it.i*1.05*ph, o.y+it.j + sag + wob*0.35, o.z+wob);
        tmpQ.identity(); tmpS.set(1,1,1);
        tmpM.compose(tmpP,tmpQ,tmpS); o.mesh.setMatrixAt(k,tmpM);
      }
      o.mesh.instanceMatrix.needsUpdate=true;
    }
    if(a.type==='mill') a.obj.rotation.z -= dt*(0.15+w*0.22);
    if(a.type==='gull'){
      const g=a.obj, d=g.userData;
      d.a+=dt*d.sp*(0.7+w*0.2);
      const x=d.cx+Math.cos(d.a)*d.r, z=d.cz+Math.sin(d.a)*d.r, y=d.y+Math.sin(t*1.4+d.ph)*2.4;
      g.position.set(x,y,z);
      g.rotation.y=-d.a-Math.PI/2*(d.sp>0?1:-1);
      g.rotation.z=Math.sin(d.a*2)*0.18+0.18*(d.sp>0?1:-1);
      const f=Math.sin(t*(7+w)+d.ph);
      d.pl.rotation.x=f*0.9; d.pr.rotation.x=-f*0.9;
    }
  }

  /* --- smoke --- */
  if(smoke){
    const srcs=[[14,20,-42,0],[2,16,14,1]];   /* keeper's chimney, ship's galley */
    for(let i=0;i<smokeP.length;i++){
      const p=smokeP[i]; p.age+=dt;
      if(p.age>p.life){ p.age=0; p.life=rr(3.5,6.5); p.s=rr(0.7,1.4); }
      const k=p.age/p.life;
      const s0=srcs[p.src===0?0:1];
      const px=s0[0]+p.dx*k*3 + Math.cos(t*0.3)*(1.5+k*10)*w;
      const py=s0[1]+p.age*3.6;
      const pz=s0[2]+p.dz*k*3 + Math.sin(t*0.25)*(1.5+k*10)*w;
      const sc=p.s*(0.5+k*2.4);
      tmpP.set(px,py,pz); tmpQ.setFromAxisAngle(new THREE.Vector3(1,0,1), p.age+p.src); tmpS.set(sc,sc,sc);
      tmpM.compose(tmpP,tmpQ,tmpS); smoke.setMatrixAt(i,tmpM);
      const c=mixC(mixC(P.plaster,{r:.4,g:.4,b:.42},0.4), cur.fogC, Math.pow(k,0.7));
      smoke.setColorAt(i,new THREE.Color().setRGB(c.r,c.g,c.b));
    }
    smoke.instanceMatrix.needsUpdate=true; smoke.instanceColor.needsUpdate=true;
  }

  /* --- clouds --- */
  if(clouds){ cloudDrift+=dt*(1.2+w*2.4); clouds.position.x=cloudDrift; clouds.position.z=cloudDrift*0.35;
    if(cloudDrift>340) cloudDrift=-340; }

  /* --- beam --- */
  if(beamGroup){ beamGroup.rotation.y+=dt*0.9;
    beamMat.color.copy(cur.skyS||cur.sunCol).multiplyScalar(1.1); }

  /* --- the ship's boat --- */
  if(rowboat){
    const cycle=(t*0.055)%2;
    const u=cycle<1? cycle : 2-cycle;
    const from=new THREE.Vector3(SHIP.x+fx*12- fz*3, 0, SHIP.z+fz*12+fx*3);
    const to=new THREE.Vector3(23,0,22);
    const px=lerp(from.x,to.x,u), pz=lerp(from.z,to.z,u);
    const dirx=to.x-from.x, dirz=to.z-from.z, dl=Math.hypot(dirx,dirz);
    const yaw=Math.atan2(dirx*(cycle<1?1:-1), dirz*(cycle<1?1:-1));
    rowboat.position.set(px, waveH(px,pz,t,w*0.85)+0.35, pz);
    rowboat.rotation.y=yaw+Math.PI*(cycle<1?0:1);
    rowboat.rotation.z=Math.sin(t*1.3)*0.06; rowboat.rotation.x=Math.sin(t*1.1)*0.04;
    const ph=t*(2.4+w*0.9)+(cycle<1?0:Math.PI);
    boatOars.forEach((o,i)=>{ o.rotation.x=Math.sin(ph+(i%2)*0.0)*0.75; o.rotation.z=(i<2?-1:1)*(0.35+Math.cos(ph)*0.25); });
  }

  /* --- pick + hud --- */
  hoverTimer-=dt;
  if(hoverTimer<=0){ hoverTimer=0.08; pick(); }
  const hx=Math.atan2(camera.position.x-controls.target.x, camera.position.z-controls.target.z);
  let hd=(90-hx/D2R)%360; if(hd<0) hd+=360;
  needle.style.transform=`rotate(${hx/D2R}rad)`;
  headEl.textContent=String(Math.round(hd/10)*10).padStart(3,'0')+'°';
  frames++; fpsT+=dt;
  if(fpsT>0.5){ fps=Math.round(frames/fpsT); frames=0; fpsT=0;
    document.getElementById('fps').textContent=fps;
    document.getElementById('draws').textContent=renderer.info.render.calls;
    if(!downgraded && fps<42 && clock.elapsedTime>4){ downgraded=true;
      renderer.setPixelRatio(1); renderer.shadowMap.enabled=false; scene.traverse(o=>{o.castShadow=false;o.receiveShadow=false;}); }
  }
  renderer.render(scene,camera);
}

/* ============================================================
   14. build it, in stages, behind the curtain
   ============================================================ */
const bar=document.querySelector('#bar > div'), lmsg=document.getElementById('lmsg');
const STEPS=[
  ['sounding the shoal water', ()=>{ initMood(); buildWater(); }],
  ['carrying stone for the wall', ()=>{ buildLand(); buildBreakwater(); }],
  ['raising the light on the point', ()=>{ buildLighthouse(); buildBeam(); }],
  ['tiling the town', ()=>{ buildTown(); }],
  ['spars and canvas', ()=>{ buildShip(); }],
  ['a bit of weather, and gulls', ()=>{ buildLife(); }],
  ['coiling down', ()=>{ finish(); }],
];
let si=0;
function finish(){
  document.getElementById('vcount').textContent=TOTAL.toLocaleString()+' cubes';
  buildUI();
  animate();
  requestAnimationFrame(()=>requestAnimationFrame(()=>{
    document.getElementById('loader').classList.add('done');
    setView('roads',1800);
  }));
}
function step(){
  if(si>=STEPS.length) return;
  const [msg,fn]=STEPS[si];
  lmsg.textContent=msg;
  bar.style.width=(si/STEPS.length*100).toFixed(0)+'%';
  requestAnimationFrame(()=>{ fn(); si++;
    bar.style.width=(si/STEPS.length*100).toFixed(0)+'%';
    if(si<STEPS.length) setTimeout(step, 18); else setTimeout(step, 40);
  });
}
addEventListener('resize',()=>{
  camera.aspect=innerWidth/innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight);
});
step();
</script>
</body>
</html>
```

**What's in there**

- **The sea is a shader**: ~24k instanced columns, three levels of chunkiness, displaced on the GPU. Sun glitter is analytic slope-normal specular, speckled into a voxel-like sparkle and properly fogged. Foam is procedural: churn around the hull, a wake behind her, and surf along the quay wall and breakwater computed from the same shoreline function the geometry was built from.
- **The ship actually rides**: fore/aft/port/starfboard wave samples drive her roll and pitch every frame, so she lifts into a swell rather than bobbing on a sine.
- **The beam turns, the mill spins, oars work, gulls bank, flags snap harder as you push the wind slider** — the slider also drives sea amplitude, cloud drift, and smoke lean.
- **Hover anything to identify it** (raycast against the instanced meshes with per-instance metadata — "the sail loft", "twelve flashes a minute"), click to fly the camera there, keys 1–5 for berths, M for golden hour / blue hour / sea fret (all lights, fog, water colour and exposure cross-fade), H to strip the panels, R to reset.
- Auto-degrades pixel ratio and drops shadows if the frame rate sags. Everything is instanced — roughly 70–90k cubes in about 40 draw calls.