Below is a single self-contained HTML file — a golden-hour voxel harbor built entirely from cubes (one draw call for the whole static world, animated voxel sea, bobbing ship, rotating light, gulls, chimney smoke). Save as `harbor.html` and open in Chrome.

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Port Aldermoor — a sailing ship calling at a harbor</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bungee&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root{
    --ink:#eaf0f2; --warm:#e8b04b; --dim:#8fa4ac; --plate:rgba(9,21,27,.86);
    --line:rgba(232,176,75,.22);
  }
  *{box-sizing:border-box;margin:0;padding:0}
  html,body{height:100%;overflow:hidden;background:#0c1b23;color:var(--ink);
    font-family:"IBM Plex Sans",system-ui,sans-serif;-webkit-font-smoothing:antialiased}
  canvas{display:block;position:fixed;inset:0}
  .vig{position:fixed;inset:0;pointer-events:none;z-index:2;
    background:radial-gradient(120% 90% at 50% 45%,transparent 45%,rgba(4,12,17,.55) 100%)}
  .ui{position:fixed;inset:0;z-index:3;pointer-events:none}

  .plate{position:absolute;background:var(--plate);border:1px solid var(--line);
    padding:16px 18px 15px;pointer-events:auto;transition:border-color .35s,transform .35s;
    box-shadow:0 18px 44px -20px rgba(0,0,0,.8)}
  .plate:hover{border-color:rgba(232,176,75,.55)}
  .plate::before{content:"";position:absolute;left:-1px;top:-1px;width:10px;height:10px;
    border-left:2px solid var(--warm);border-top:2px solid var(--warm)}
  .plate::after{content:"";position:absolute;right:-1px;bottom:-1px;width:10px;height:10px;
    border-right:2px solid var(--warm);border-bottom:2px solid var(--warm)}

  .tl{top:26px;left:26px;max-width:min(46vw,470px)}
  .kicker{font-family:"IBM Plex Mono",monospace;font-size:10px;letter-spacing:.26em;
    text-transform:uppercase;color:var(--warm)}
  h1{font-family:"Bungee",cursive;font-weight:400;line-height:.92;margin:8px 0 9px;
    font-size:clamp(30px,4.6vw,62px);letter-spacing:.005em;text-transform:uppercase}
  h1 span{display:block;color:#fff}
  h1 em{display:block;font-style:normal;font-size:.42em;letter-spacing:.02em;color:#0e6d70;
    margin-top:2px;text-shadow:0 0 22px rgba(20,180,180,.35)}
  .sub{font-size:13.5px;line-height:1.55;color:#b9c8cd;max-width:40ch}
  .rule{height:1px;background:linear-gradient(90deg,var(--warm),transparent);margin:12px 0 0}

  .tr{top:26px;right:26px;width:236px}
  .compass{position:absolute;right:14px;top:14px;width:44px;height:44px;opacity:.85}
  .compass .rose{transition:transform .12s linear;transform-origin:50% 50%}
  .row{display:flex;justify-content:space-between;align-items:baseline;gap:10px;
    padding:6px 0;border-bottom:1px dashed rgba(255,255,255,.09);
    font-family:"IBM Plex Mono",monospace;font-size:10.5px;letter-spacing:.14em;text-transform:uppercase}
  .row:last-child{border-bottom:0}
  .row span{color:var(--dim)}
  .row b{color:var(--ink);font-weight:500;letter-spacing:.04em;font-size:12px}
  .row b small{color:var(--dim);font-size:9px;margin-left:2px}

  .bl{bottom:26px;left:26px;font-family:"IBM Plex Mono",monospace;font-size:10px;
    letter-spacing:.2em;text-transform:uppercase;color:var(--dim);padding:11px 14px}
  .bl i{color:var(--warm);font-style:normal}

  .br{bottom:26px;right:26px;width:262px}
  .phead{font-family:"IBM Plex Mono",monospace;font-size:10px;letter-spacing:.28em;
    color:var(--warm);text-transform:uppercase;margin-bottom:12px}
  label.cap{display:block;font-family:"IBM Plex Mono",monospace;font-size:9.5px;
    letter-spacing:.2em;text-transform:uppercase;color:var(--dim);margin-bottom:9px}
  input[type=range]{width:100%;height:3px;-webkit-appearance:none;appearance:none;background:
    linear-gradient(90deg,#d98a2b,#ffd27a 45%,#8ec5d8);outline:none;cursor:pointer;margin:6px 0 14px}
  input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:13px;height:13px;
    background:#fff6e2;border:2px solid #b7761f;cursor:grab;box-shadow:0 0 0 4px rgba(232,176,75,.18)}
  .chips{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:11px}
  .chip{font-family:"IBM Plex Mono",monospace;font-size:9.5px;letter-spacing:.11em;
    text-transform:uppercase;padding:8px 7px;background:transparent;color:#c3d1d6;
    border:1px solid rgba(255,255,255,.16);cursor:pointer;transition:.22s}
  .chip:hover{border-color:var(--warm);color:#fff;transform:translateY(-1px)}
  .chip.on{background:var(--warm);border-color:var(--warm);color:#0c1b23;font-weight:500}
  .chk{display:flex;align-items:center;gap:8px;font-family:"IBM Plex Mono",monospace;
    font-size:9.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--dim);cursor:pointer}
  .chk input{accent-color:var(--warm);cursor:pointer}

  #boot{position:fixed;inset:0;z-index:9;background:#0c1b23;display:grid;place-items:center;
    transition:opacity .7s ease .15s,visibility .7s}
  #boot span{font-family:"Bungee",cursive;font-size:12px;letter-spacing:.5em;color:var(--warm);
    text-transform:uppercase;animation:pulse 1.6s ease-in-out infinite}
  @keyframes pulse{0%,100%{opacity:.35}50%{opacity:1}}
  .gone{opacity:0;visibility:hidden}
  @media (max-width:760px){.tr,.sub{display:none}.tl{max-width:70vw}}
</style>
</head>
<body>
<canvas id="c"></canvas>
<div class="vig"></div>

<div class="ui">
  <div class="plate tl">
    <div class="kicker">Voxel chart № 07 · scale 1 : 200</div>
    <h1>Port <span>Aldermoor</span><em>calling at anchor</em></h1>
    <div class="rule"></div>
    <p class="sub" style="margin-top:11px">Bark <i>Aldermoor</i>, three masts, two hundred and forty tons,
      running in on the flood with a westerly behind her — yards laid aback, line sent to the Long Quay.</p>
  </div>

  <div class="plate tr">
    <svg class="compass" viewBox="0 0 40 40">
      <circle cx="20" cy="20" r="18" fill="none" stroke="rgba(232,176,75,.35)"/>
      <g class="rose" id="rose">
        <path d="M20 3 L23.4 20 L20 17 L16.6 20 Z" fill="#e8b04b"/>
        <path d="M20 37 L16.6 20 L20 23 L23.4 20 Z" fill="#5d727b"/>
      </g>
      <text x="20" y="9.6" font-size="5.5" fill="#8fa4ac" text-anchor="middle"
        font-family="IBM Plex Mono">N</text>
    </svg>
    <div class="row"><span>Wind</span><b id="oWind">WSW 12<small>kn</small></b></div>
    <div class="row"><span>Tide</span><b id="oTide">+2.14<small>m</small></b></div>
    <div class="row"><span>Bearing</span><b id="oBrg">042.0°</b></div>
    <div class="row"><span>Soundings</span><b id="oVox">0 voxels</b></div>
  </div>

  <div class="plate bl"><i>drag</i> orbit &nbsp;·&nbsp; <i>wheel</i> zoom &nbsp;·&nbsp; <i>right-drag</i> pan</div>

  <div class="plate br">
    <div class="phead">Harbor dial</div>
    <label class="cap">Hour <span id="oHour" style="color:#eaf0f2">— late afternoon</span></label>
    <input type="range" id="time" min="0" max="100" value="20">
    <label class="cap">Viewpoint</label>
    <div class="chips">
      <button class="chip on" data-v="0">Approach</button>
      <button class="chip" data-v="1">At the berth</button>
      <button class="chip" data-v="2">The light</button>
      <button class="chip" data-v="3">Chart table</button>
    </div>
    <label class="chk"><input type="checkbox" id="drift" checked> Slow drift</label>
  </div>
</div>

<div id="boot"><span>Charting the soundings</span></div>

<script type="importmap">
{"imports":{
  "three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
  "three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
}}
</script>
<script type="module">
import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';

/* ════════════════════════════════ palette ════════════════════════════════ */
const P = {
  stoneD:0x544f47, stone:0x766f62, stoneL:0x92897a, stoneP:0xb3a893,
  cobbles:0x5b5752, cobbles2:0x6c665d, kerb:0x8b8375,
  sand:0xd9c193, sandD:0xb9a073, grass:0x5c7f4a, grassD:0x48683b, dirt:0x77613f,
  wood:0x8b6239, woodL:0xa87c4c, woodD:0x523821, woodG:0x6b5a3f,
  deck:0xa87f4f, deckD:0x84603a, pitch:0x241f1c,
  hull:0x1b2735, hullL:0x2c3f52, red:0x77392b, gold:0xd7a549,
  sail:0xf3e8d2, sailD:0xd9c7a6, rope:0xc3ac7d,
  iron:0x383e45, metal:0x7d8a91, copper:0x5f9c84,
  w1:0xe9dcc2, w2:0xd0bfa0, w3:0xac9a7e,
  roof:0x38515f, roof2:0x2a3d4a, roof3:0x4d6a7a,
  door:0x4a3322, glass:0x2a3a44,
  leaf:0x4a7a44, leaf2:0x3a6338, leaf3:0x5d8d4a, trunk:0x553d27,
  white:0xeee8dc, black:0x22201f, redp:0xb24234, bluep:0x2f5d80, cream:0xf1e7d3,
  foam:0xdfeef0,
  seaDeep:0x14404f, sea:0x256b78, seaL:0x38908f, shoal:0x54a79d
};
const G = {lamp:0xffcf8a, win:0xffd79a, beacon:0xfff0c4, stern:0xffd9a0, ember:0xff9e52};

/* ════════════════════════════════ renderer ═══════════════════════════════ */
const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({canvas, antialias:true, powerPreference:'high-performance'});
renderer.setPixelRatio(Math.min(devicePixelRatio,1.75));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.16;

const scene = new THREE.Scene();
const FOG = new THREE.Color(0x9db8c4);
scene.fog = new THREE.Fog(FOG.getHex(), 95, 255);

const camera = new THREE.PerspectiveCamera(43, innerWidth/innerHeight, 0.5, 900);
camera.position.set(-52, 34, 92);

const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true; controls.dampingFactor = .065;
controls.target.set(4, 7, 4);
controls.maxPolarAngle = 1.47; controls.minDistance = 9; controls.maxDistance = 210;
controls.autoRotateSpeed = .32;
controls.screenSpacePanning = true;

/* ════════════════════════════════ lights ═════════════════════════════════ */
const hemi = new THREE.HemisphereLight(0xa9cee6, 0x6b5a44, .82); scene.add(hemi);
const amb  = new THREE.AmbientLight(0xffffff, .16); scene.add(amb);
const sun  = new THREE.DirectionalLight(0xffd39a, 2.15);
sun.castShadow = true;
sun.shadow.mapSize.set(2048,2048);
const sc = sun.shadow.camera; sc.left=-62; sc.right=62; sc.top=62; sc.bottom=-62; sc.near=1; sc.far=230;
sun.shadow.bias = -0.0005; sun.shadow.normalBias = .09;
scene.add(sun); scene.add(sun.target);

/* ════════════════════════════════ voxel kit ══════════════════════════════ */
class VB{
  constructor(){ this.p=[]; this.c=[]; }
  get n(){ return this.c.length; }
  set(x,y,z,c){ x=Math.round(x); y=Math.round(y); z=Math.round(z); this.p.push(x,y,z); this.c.push(c); }
  fill(x0,y0,z0,x1,y1,z1,c,jit=1){
    const ax0=Math.min(x0,x1),ax1=Math.max(x0,x1),ay0=Math.min(y0,y1),ay1=Math.max(y0,y1),
          az0=Math.min(z0,z1),az1=Math.max(z0,z1);
    for(let x=ax0;x<=ax1;x++)for(let y=ay0;y<=ay1;y++)for(let z=az0;z<=az1;z++) this.set(x,y,z,c);
  }
  tubeY(x,z,y0,y1,c){ for(let y=Math.min(y0,y1);y<=Math.max(y0,y1);y++) this.set(x,y,z,c); }
  tubeX(x0,x1,y,z,c){ for(let x=Math.min(x0,x1);x<=Math.max(x0,x1);x++) this.set(x,y,z,c); }
  tubeZ(x,y,z0,z1,c){ for(let z=Math.min(z0,z1);z<=Math.max(z0,z1);z++) this.set(x,y,z,c); }
  cyl(cx,cz,r,y0,y1,c,solid=false){
    for(let y=y0;y<=y1;y++)for(let x=Math.ceil(cx-r);x<=Math.floor(cx+r);x++)
      for(let z=Math.ceil(cz-r);z<=Math.floor(cz+r);z++){
        const d=Math.hypot(x-cx,z-cz);
        if(d<=r+.02&&(solid||d>r-1.06)) this.set(x,y,z,c);
      }
  }
}
const hash3=(x,y,z)=>{ let n=(x*73856093)^(y*19349663)^(z*83492791); n=(n^(n>>>13))>>>0; return (n%997)/997; };
const boxGeo = new THREE.BoxGeometry(1,1,1);

function bake(vb,{mat,cast=true,receive=true,ao=true}={}){
  const n = vb.n, m = new THREE.InstancedMesh(boxGeo, mat, n);
  const M = new THREE.Matrix4(), col = new THREE.Color();
  const occ = new Set();
  for(let i=0;i<n;i++) occ.add(vb.p[i*3]+','+vb.p[i*3+1]+','+vb.p[i*3+2]);
  for(let i=0;i<n;i++){
    const x=vb.p[i*3], y=vb.p[i*3+1], z=vb.p[i*3+2];
    col.setHex(vb.c[i]);
    let nb=0;
    if(ao){ if(occ.has((x+1)+','+y+','+z))nb++; if(occ.has((x-1)+','+y+','+z))nb++;
      if(occ.has(x+','+(y+1)+','+z))nb++; if(occ.has(x+','+(y-1)+','+z))nb++;
      if(occ.has(x+','+y+','+(z+1)))nb++; if(occ.has(x+','+y+','+(z-1)))nb++; }
    const j = (hash3(x,y,z)-.5)*.085;
    col.multiplyScalar(Math.max(.4, 1 - nb*.042 + j));
    M.makeTranslation(x,y,z);
    m.setMatrixAt(i,M); m.setColorAt(i,col);
  }
  m.castShadow=cast; m.receiveShadow=receive;
  m.instanceMatrix.needsUpdate=true; if(m.instanceColor) m.instanceColor.needsUpdate=true;
  m.computeBoundingSphere();
  return m;
}
const lambert = (o={}) => new THREE.MeshLambertMaterial(Object.assign({color:0xffffff},o));
const basic   = () => new THREE.MeshBasicMaterial({color:0xffffff});
const matSolid = lambert(), matGlow = basic();

/* ══════════════════════════════ geography ════════════════════════════════ */
const QUA = {town:18, north:-24, bq:[-36,16,22], sbw:[6,26,32], hump:[14,22]};
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const inR=(x,z,a,b,c,d)=>x>=a&&x<=b&&z>=c&&z<=d;
function solid(x,y,z){
  if(y<-3) return false;
  if(x>=QUA.town){ if(y<=4){ if(y===4&&x<=20&&z>=-2&&z<=6) return false; return true; } return false; }
  if(z<=QUA.north && x>=-22){ if(y<=4) return !(y===4&&x>=-4&&x<=4&&z>=-28); return false; }
  if(inR(x,z,4,18,26,32)&&y<=3) return true;
  if(x>=-36&&x<=-30&&z>=16&&z<=22&&y<=4) return true;
  if(inR(x,z,14,20,16,24)&&y<=2+Math.max(0,4-Math.floor(Math.hypot(x-17,z-20)/1.6))) return true;
  if(inR(x,z,-30,10,-44,-33)&&y<=-2) return true;
  return false;
}

/* ══════════════════════════════ world mesh ═══════════════════════════════ */
const W = new VB, E = new VB;   // W = solid, E = emissive
let shoreX0=99,shoreX1=-99,shoreZ0=99,shoreZ1=-99;

function terrain(){
  for(let x=-42;x<=42;x++) for(let z=-42;z<=42;z++){
    if(!solid(x,0,z)) continue;
    let top=0; while(top<6 && solid(x,top+1,z)) top++;
    let sub=0; while(sub<7 && solid(x,-2-sub,z)) sub++;
    const shore = !solid(x,0,z-1)||!solid(x,0,z+1)||!solid(x-1,0,z)||!solid(x+1,0,z);
    const beach = top<=2 && !solid(x,-1,z-1)&&!solid(x,-1,z+1)&&!solid(x-1,-1,z)&&!solid(x+1,-1,z);
    shoreX0=Math.min(shoreX0,x);shoreX1=Math.max(shoreX1,x);
    shoreZ0=Math.min(shoreZ0,z);shoreZ1=Math.max(shoreZ1,z);
    for(let y=-2;y<=top;y++){
      let c;
      if(y<0) c = beach? P.sandD : P.stoneD;
      else if(y===top) c = beach? P.sand : (top<=2? P.sand : (shore? P.kerb : P.stoneL));
      else c = (top>=3? P.stone : P.sandD);
      if(y<0 && !solid(x,y,z)) break;
      W.set(x,y,z,c);
    }
    if(top>=3 && !beach){
      if(z<=QUA.north+2||x>=QUA.town+2||z>=25) W.set(x,top,z,P.cobbles);
    }
  }
}

/* ─── generic buildings ─── */
function walls(vb,x0,x1,z0,z1,y0,y1,c,seed){
  const r = hash3(x0,y0,z0);
  for(let y=y0;y<=y1;y++) for(let x=x0;x<=x1;x++) for(let z=z0;z<=z1;z++){
    const edge = x===x0||x===x1||z===z0||z===z1;
    if(!edge){ if(y===y0-1||y===y1) vb.set(x,y,z,P.woodD); continue; }
    let col = c;
    if(y===y0) col = P.stone;
    if((x+z+y+Math.floor(r*9))%5===0) col = P.w3;
    vb.set(x,y,z,col);
  }
}
function windows(vb,x0,x1,z0,z1,y,seeds){
  const glow = (x,y,z,c)=>E.set(x,y,z,c);
  for(let x=x0;x<=x1;x++) for(let z=z0;z<=z1;z++){
    const on = hash3(x,seeds,z)>.42;
    if(x===x0) vb.set(x,y,z,on?P.glass:P.door), on&&glow(x,y,z,G.win);
    if(x===x1) vb.set(x,y,z,on?P.glass:P.door), on&&glow(x,y,z,G.win);
    if(z===z0){vb.set(x,y,z,on?P.glass:P.door); on&&glow(x,y,z,G.win);}
    if(z===z1){vb.set(x,y,z,on?P.glass:P.door); on&&glow(x,y,z,G.win);}
  }
}
function gableRoof(vb,x0,x1,z0,z1,baseY,ridge,c1,c2){
  const longX = (x1-x0) >= (z1-z0);
  const span = longX ? (z1-z0) : (x1-x0);
  const half = Math.ceil(span/2);
  for(let s=0;s<=half;s++){
    const y = baseY+s; if(y>baseY+half+2) break;
    const c = (s%2? c1:c2);
    if(longX){
      const a=z0+s,b=z1-s; if(a>b) break;
      vb.fill(x0-1,y,a,x1+1,y,b,c);
    } else {
      const a=x0+s,b=x1-s; if(a>b) break;
      vb.fill(a,y,z0-1,b,y,z1+1,c);
    }
  }
}
function canted(vb,x0,x1,z0,z1,baseY,c){
  const n=Math.min(3,Math.floor(Math.min(x1-x0,z1-z0)/2));
  for(let s=0;s<=n;s++) vb.fill(x0+s,baseY+s,z0+s,x1-s,baseY+s,z1-s,c);
}
function chimney(vb,x,z,y0,h,smoke){
  vb.fill(x,y0,z,x,y0+h,z,P.brick||0x8b5a48); vb.set(x,y0+h+1,z,P.stoneD);
  E.set(x,y0+h,z,G.ember);
  if(smoke) SMOKERS.push(new THREE.Vector3(x,y0+h+2,z));
}
const BRICK=0x8b5545; P.brick=BRICK;
const SMOKERS=[], LAMPS=[], CRATES=[[16,11],[15,12]];

function house(vb,x0,x1,z0,z1,h,wall,roof){
  walls(vb,x0,x1,z0,z1,5,4+h,wall);
  for(let y=5;y<=4+h;y++) windows(vb,x0,x1,z0,z1,y,y*7);
  gableRoof(vb,x0,x1,z0,z1,5+h,roof,P.roof,P.roof2);
  vb.fill(x0-1,4+h,z0-1,x0-1,4+h,z1+1,P.stoneP);
  vb.fill(x1+1,4+h,z0-1,x1+1,4+h,z1+1,P.stoneP);
}

function town(){
  /* ── great warehouse on the quay ── */
  walls(W,21,28,2,14,5,9,P.w2);
  gableRoof(W,21,28,2,14,10,P.roof,P.roof2);
  for(let y=6;y<=9;y++) windows(W,21,28,2,14,y,y*3);
  for(let x=21;x<=28;x++){ W.set(x,10,2,P.stoneP); W.set(x,10,14,P.stoneP); }
  W.fill(23,5,14,26,8,14,P.door); E.set(24,6,13,G.win); E.set(26,6,13,G.win);
  chimney(W,22,4,11,3,true); chimney(W,27,12,11,3,true);
  // hoist beam
  W.tubeX(21,26,11,15,P.woodD); W.tubeZ(26,9,14,15,P.woodD); W.tubeZ(26,11,14,15,P.wood);
  W.tubeZ(26,12,14,16,P.iron);

  /* ── Customs house with clock tower ── */
  walls(W,22,30,-21,1,P.w1);
  gableRoof(W,22,30,-21,1,10,P.roof3,P.roof);
  for(let y=6;y<=9;y++) windows(W,22,30,-21,1,y,y*11);
  W.fill(24,5,1,27,8,1,P.door);
  W.fill(22,11,-21,30,11,1,P.stoneP);
  W.cyl(26,-19,2.6,5,16,P.w1,true);
  W.cyl(26,-19,3.0,16,16,P.stoneP,true);
  W.cyl(26,-19,2.4,17,19,P.w1,true);
  E.set(26,18,-17,G.beacon); E.set(26,18,-18,G.beacon);
  W.cyl(26,-19,2.6,20,20,P.copper,true); W.cyl(26,-19,1.6,21,21,P.copper,true);
  W.cyl(26,-19,0.6,22,23,P.gold,true); W.set(26,24,-19,P.gold);
  W.fill(23,12,-21,29,12,1,P.stoneP);

  /* ── terrace of houses ── */
  const hs=[[32,36,-14,-8,P.w1],[37,41,-7,-1,P.w2],[31,35,-7,-1,P.w3],
            [36,41,3,9,P.w1],[31,34,2,7,P.w2],[37,41,-21,-15,P.w2]];
  hs.forEach((h,i)=>house(W,h[0],h[1],h[2],h[3],3+(i%2)*2,h[4],i%3?P.roof:P.roof2));
  chimney(W,34,-11,11,3,true); chimney(W,39,6,11,3,false);

  /* ── long shed north of the channel ── */
  walls(W,-16,-6,-23,-17,5,8,P.w3); gableRoof(W,-16,-6,-23,-17,9,P.roof2,P.roof);
  W.fill(-14,5,-17,-10,7,-17,P.door);
  /* ── north-quay houses ── */
  house(W,-2,-4,-42,-37,3,P.w1); house(W,4,9,-42,-36,4,P.w2); house(W,10,15,-42,-37,3,P.w3);

  /* ── seawall chain of lamps ── */
  const posts=[[19,-14],[19,-4],[19,8],[19,18],[19,24],[10,25],[2,25],[-6,25],[-14,25],[12,25],
               [8,27],[8,31],[16,-23],[6,-23],[-4,-23],[18,-23],[-34,17],[-34,21]];
  posts.forEach(([x,z])=>{
    if(solid(x,5,z)){ W.tubeY(x,z,5,7,P.iron); W.set(x,8,z,P.iron); W.fill(x-0+0,8,z-0,x,8,z,P.iron);
      W.set(x,7+1,z,G.lamp); LAMPS.push([x,8,z]); }
  });
  // pier heads
  [[15,2],[15,22]].forEach(([x,z])=>{ W.tubeY(x,z,3,5,P.woodD); W.set(x,6,z,G.lamp); LAMPS.push([x,6,z]); });
  // beacon tower on breakwater
  W.cyl(-33,-0+20,2.6,5,5,P.stone,true); W.cyl(-33,20,2.2,6,6,P.stone,true);
  W.cyl(-33,20,1.9,7,7,P.stoneL,true); W.cyl(-33,20,1.6,8,8,P.stoneP,true);
  W.cyl(-33,20,1.7,9,10,P.iron); W.cyl(-33,20,1.4,11,11,P.copper,true);
  E.set(-33,10,20,G.beacon);
  W.tubeY(-33,20,12,13,P.iron);
  // beacon on south breakwater knee
  W.fill(6,4,25,8,5,25,P.stone); W.tubeY(7,25,5,7,P.iron); E.set(7,8,25,G.lamp); LAMPS.push([7,8,25]);

  /* ── trees ── */
  [[35,-24],[39,-27],[30,-25],[41,-32],[21,-30],[25,-32],[33,12],[38,12],[41,15],[22,12],
   [-8,-26],[-12,-30],[2,-26],[10,-27],[36,-33],[41,-11]].forEach(([x,z])=>tree(W,x,z));

  /* ── cobbled yard markings + kerbs along the quay ── */
  for(let z=-22;z<=24;z++) for(let x=19;x<=21;x++)
    if(!solid(x,5,z)===false&&hash3(x,7,z)>.6) W.set(x,4,z,P.cobbles2);
  // bollards on the quay edge
  for(let z=-18;z<=22;z+=5) for(let x=19;x<=20;x++)
    if(!solid(x,5,z)){ W.tubeY(19,z,5,6,P.iron); W.set(19,7,z,P.metal); }
}
function tree(vb,x,z){
  const h=2+Math.floor(hash3(x,3,z)*2);
  vb.tubeY(x,z,5,4+h,P.trunk);
  const r = 1.9;
  vb.cyl(x,z,r,5+h,5+h,P.leaf,true);
  vb.cyl(x,z,r-.7,6+h,6+h,P.leaf2,true);
  vb.cyl(x,z,r-1.4,7+h,7+h,P.leaf3,true);
}

/* ─── the pier ─── */
function pier(){
  const DECK=3;
  for(let z=4;z<=21;z++) for(let x=15;x<=19;x++){
    W.set(x,DECK,z, hash3(x,z,3)>.5? P.wood : P.woodL);
    if(x===15||x===19) W.set(x,DECK,z,P.woodD);
  }
  W.fill(15,2,14,19,2,16,P.deckD);
  for(let x=14;x<=20;x++){ W.set(x,DECK,3,P.woodD); W.set(x,DECK,22,P.woodD); }
  for(let x=14;x<=20;x+=3) for(let z=3;z<=22;z+=3) W.cyl(x+.0,0,z,DECK,-2,.6,P.woodD,true);
  // railings land-side
  for(let z=4;z<=21;z+=2){ W.tubeY(20,z,DECK+1,DECK+2,P.woodD); }
  W.tubeZ(20,DECK+3,4,21,P.woodD);
  // lamps on the pier
  [7,17].forEach(z=>{ W.tubeY(19,z,DECK+1,DECK+3,P.iron); E.set(19,DECK+4,z,G.lamp); LAMPS.push([19,DECK+4,z]); });
  // bollards berth-side
  [6,10,14,18].forEach(z=>{ W.tubeY(15,z,DECK+1,DECK+2,P.iron); W.set(15,DECK+3,z,P.metal); });
  // crates & barrels
  const st=[[16,7],[18,9],[16,10],[17,13],[16,13]];
  st.forEach(([x,z],i)=>{
    const c=[P.wood,P.deck,P.woodG][i%3];
    W.fill(x,DECK+1,z,x,DECK+1,z,c);
    W.fill(x,DECK+2,z,x,DECK+2,z,i%2?P.deckD:P.woodL);
    if(i===2) W.set(x,DECK+3,z,P.wood);
  });
  [[18,6],[17,6],[18,20],[17,11]].forEach(([x,z])=>{
    W.cyl(x,0,z,DECK+1,DECK+2,1.25,P.deck,true);
    W.tubeY(x-.0,z-.0,DECK+1,DECK+2,P.woodL); W.cyl(x,0,z,DECK+1,DECK+2,1.35,P.iron);
    W.cyl(x,0,z,DECK+3,DECK+3,1.25,P.deck,true);
  });
  // derrick crane
  const cx=19,cz=23;
  W.tubeY(cx,cz,DECK+1,DECK+5,P.iron);
  W.fill(cx-1,DECK+1,cz-1,cx+1,DECK+1,cz+1,P.stone);
  W.tubeX(cx-3,cx-3,DECK+2,cz,P.woodD); W.tubeX(cx+3,cx+3,DECK+2,cz,P.woodD);
  W.tubeZ(cx,DECK+2,cz-3,cz+3,P.woodD); W.tubeZ(cx,DECK+3,cz-3,cz+3,P.woodD);
  W.tubeX(cx-3,cx+3,DECK+4,cz,P.woodG);
  W.tubeX(cx-3,cx-3,DECK+3,cz,P.woodD); W.tubeX(cx+3,cx+3,DECK+3,cz,P.woodD);
  W.tubeY(cx-3,cz,DECK+3,DECK+1,P.rope);
  W.fill(cx-3,DECK,cz,cx-3,DECK,cz,P.deck);
  W.fill(cx-4,DECK+6,cz,cx+4,DECK+6,cz,P.roof2);
  // gangway from pier to the ship's starboard side (ship world-x ≈ 12)
  for(let x=12;x<=15;x++){ const y = DECK - (15-x)*0.34;
    for(let z=12;z<=13;z++) W.set(x,Math.round(y-0.4),z,P.woodL); }
  W.tubeX(12,15,DECK-1+1,11,P.rope); W.tubeX(12,15,DECK-1+1,14,P.rope);
  // net drying frames + coil
  W.fill(17,DECK+1,17,17,DECK+3,18,P.woodD); W.fill(18,DECK+1,17,18,DECK+3,18,P.woodD);
  W.fill(17,DECK+1,16,18,DECK+1,16,P.woodD);
  for(let z=16;z<=18;z++) for(let y=DECK+2;y<=DECK+3;y++) W.set(17,y,z,P.rope);
  // quay-side coals
  for(let x=22;x<=27;x++) for(let z=15;z<=20;z++)
    if(hash3(x,z,9)>.32) W.set(x,5,z, hash3(x,z,2)>.7? 0x2b2b30 : 0x1f1f24);
  // barrels of pitch on the quay
  [[23,23],[24,23],[23,24],[25,20]].forEach(([x,z])=>{
    W.cyl(x,0,z,5,6,1.25,P.woodD,true); W.cyl(x,0,z,7,7,1.2,P.deck,true);
  });
  // cobble strip + kerb along the quay wall
  for(let z=-24;z<=26;z++) for(let x=18;x<=19;x++) if(solid(x,4,z)) W.set(x,4,z,P.kerb);
}

/* ─── little figures (charming scale cues) ─── */
function figure(vb,x,y,z,c,head=0x2a2420){
  vb.fill(x,y,z,x,y+1,z,c); vb.set(x,y+2,z,head);
}
function crowd(){
  const spots=[[16,4,7],[18,4,13],[15,4,20],[20,4,-3],[22,5,-8],[24,5,18],[16,4,15],
               [17,4,18],[21,5,4],[26,5,20],[12,4,26],[9,4,27],[-33,5,19]];
  const cols=[P.redp,P.bluep,P.woodG,P.cream,P.copper,P.black];
  spots.forEach(([x,y,z],i)=>{
    if(!solid(x,y-1,z)) return;
    figure(W,x,y,z,cols[i%cols.length]);
  });
  // cart on the quay
  W.fill(24,6,7,27,6,9,P.wood); W.fill(24,7,7,27,7,9,P.deckD);
  W.set(23,6,7,P.iron); W.set(23,6,9,P.iron);
  W.tubeX(28,30,6,8,P.woodD);
}

/* ══════════════════════════════ the bark ═════════════════════════════════ */
const HW=[2.2,2.9,3.5,3.9,4,4,4,4,4,4,4,4,4,3.95,3.8,3.5,3.1,2.6,2.0,1.3,1.6,2.0];
const hwAt=x=>HW[x+10]!==undefined?HW[x+10]:0;
const halfAt=(x,y)=>{ const hw=hwAt(x); if(hw<=0) return -1;
  const keel = Math.abs(x)>6? -1.4 : -2.6; const t=(y-keel)/(0.5-keel);
  if(t<0) return -1; return hw*Math.sqrt(Math.max(0,1-Math.pow(1-clamp(t,0,1),2))); };

const SHIP = new THREE.Group();
const S = new VB, SE = new VB;
function ship(){
  /* hull */
  for(let x=-10;x<=10;x++){
    const keel = Math.abs(x)>6? -1 : -2;
    for(let y=keel;y<=0;y++){
      const h = Math.floor(halfAt(x,y-0.5)+.001);
      for(let z=-h;z<=h;z++){
        const shell = Math.abs(z)===h;
        let c=P.pitch;
        if(shell){
          if(y===0) c=P.gold;
          else if(y===-1) c=P.hull;
          else c=P.red;
        }
        S.set(x,y,z,c);
      }
    }
    // wale
    const h=Math.floor(halfAt(x,-0.5)+.001);
    if(h>0){ S.set(x,0,-h,P.gold); S.set(x,0,h,P.gold); }
  }
  // stern & bow closures
  S.fill(10,0,-2,10,1,2,P.hullL); S.fill(10,-1,-2,10,-1,2,P.hull);
  S.fill(-10,-1,-2,-10,0,2,P.hull);
  // waterline boot-top
  for(let x=-9;x<=9;x++){ const h=Math.floor(halfAt(x,-0.5)+.001);
    if(h>0){ S.set(x,-1,-h,P.pitch); S.set(x,-1,h,P.pitch);} }
  // bulwarks
  for(let x=-10;x<=10;x++){
    const h=Math.floor(halfAt(x,0.5)+.001);
    if(h<1) continue;
    for(let z=-h;z<=h;z++){
      const edge=Math.abs(z)===h||z===-h||z===h;
      if(edge){ S.set(x,1,z,P.deckD); }
      else S.set(x,1,z, hash3(x,1,z)>.55? P.deck : P.deckD);
    }
    // gunports / ports
    if(x>-7&&x<8&&(x+3)%2===0){ S.set(x,1,-h,P.iron); S.set(x,1,h,P.iron); }
  }
  // sterncastle
  S.fill(-10,2,-3,-4,2,3,P.deck);
  S.fill(-9,3,-2,-5,3,2,P.woodG);
  S.fill(-9,4,-2,-5,4,2,P.deckD);
  S.tubeZ(-7,5,-1,1,P.woodD);
  for(let x=-9;x<=-5;x++){ SE.set(x,3,-2,G.stern); SE.set(x,3,2,G.stern); }
  S.set(-10,4,0,G.lamp); S.fill(-10,3,-1,-10,3,1,P.woodD);
  // forecastle
  S.fill(6,2,-2,9,2,2,P.deck);
  S.fill(6,2,-3,6,2,3,P.deckD); S.fill(9,2,-2,9,2,2,P.deckD);
  S.set(8,3,0,P.woodD); S.fill(7,3,-1,8,3,1,P.cream);
  // figurehead + trailboards
  S.set(11,1,0,P.cream); S.set(11,0,0,P.cream); S.set(12,1,0,P.cream);
  S.set(11,1,-1,P.gold); S.set(11,1,1,P.gold);
  S.tubeX(11,12,2,0,P.gold);
  // rails
  for(let z=-3;z<=3;z++){ S.set(-4,2,z,P.deckD); }
  for(let x=-4;x<=6;x++){ if(Math.abs(x)>2) continue; S.set(x,2,-3,P.deckD); S.set(x,2,3,P.deckD);}
  // cargo on deck
  S.fill(-2,2,-1,0,2,1,P.wood); S.set(-1,3,0,P.deckD); S.fill(2,2,-2,3,2,-1,P.deck);
  S.cyl(4,0,0,1.25,2,2,1.25,P.woodD,true); S.fill(-3,2,2,-2,2,3,P.woodL);
  S.fill(-3,2,-3,-2,2,-2,P.woodL);
  // hatch covers & pumps
  S.fill(1,2,-1,2,2,1,P.deckD); S.tubeY(5,2,2,3,P.woodD); S.tubeY(5,-2,2,3,P.woodD);
  // capstans
  S.cyl(-3,0,0,2,2,1.1,P.wood,true); S.cyl(3,0,0,2,2,1.1,P.wood,true);

  /* masts, yards, sails */
  const MAST=[[-6,-13,16,10,-8],[0,-13,21,12,-10],[6,-13,18,11,-9]]; // x, y0, top, yardsA, yardsB
  MAST.forEach(([mx,y0,top,ya,yb],i)=>{
    for(let y=y0;y<=top;y++) S.set(mx,y,0, y<3? P.pitch : (y%4===0? P.woodL: P.wood));
    // crow's nest
    S.cyl(mx,0,0,1.4,top-5,top-4,1.35,P.wood,true);
    // yards
    [ya,yb].forEach((yy,k)=>{
      const spread = 3.9-1.55*(k===0?0:1.0) + (i===1?0.9:0) - (i===2?0.6:0);
      const h=Math.max(1,Math.round(spread));
      S.tubeZ(mx,yy,-h,h,k? P.woodD:P.wood);
      S.set(mx-h,yy,0,P.iron); S.set(mx+h,yy,0,P.iron);
      // sail belly
      const drop = (k===0? 6.4 : 4.4) - (i===2?1.2:0);
      const sc = i===1? P.sail : (k===0?P.sail:P.sailD);
      for(let dz=-h;dz<=h;dz++){
        const belly = Math.round(1.7*(1-Math.pow(dz/(h+.6),2)));
        for(let sy=1;sy<=drop;sy++){
          const sag = Math.round(1.4*(1-Math.pow(dz/(h+.6),2)));
          const y = yy-sy - sag*0;
          const shade = (sy===drop)||(dz===-h)||(dz===h)? P.sailD : sc;
          S.set(mx+belly,y,dz, hash3(mx,y,dz)>.72? P.sailD : shade);
        }
        for(let sy=1;sy<=drop;sy++) if(Math.abs(dz)>h-1) S.set(mx+belly+1,yy-sy,dz,P.sailD);
      }
      // studding-sail booms on the main
      if(i===1&&k===0){ S.tubeZ(mx,yy,-h-2,-h-1,P.woodD); S.tubeZ(mx,yy,h+1,h+2,P.woodD); }
    });
    // pennant
    S.set(mx+1,top,0,P.redp); S.set(mx+2,top,0,P.cream); S.set(mx+3,top-1,0,P.redp);
  });
  // spanker (fore-aft sail at mizzen)
  for(let x=1;x<=7;x++){
    const bh=Math.round(2.6*(1-Math.pow((x-4)/4,2)));
    for(let dz=-1;dz<=bh;dz++) S.set(x,11,dz,P.sailD);
    for(let dz=-1;dz<=bh;dz++) S.set(x,10,dz,P.sail);
    for(let dz=-1;dz<=bh;dz++) S.set(x,9,dz,P.sail);
  }
  S.tubeX(1,8,12,0,P.woodD);
  // topsail shrouds chains
  S.tubeZ(-6,16,-2,2,P.iron); S.tubeZ(0,21,-2,2,P.iron); S.tubeZ(6,18,-2,2,P.iron);

  /* bowsprit */
  let bx=10,by=3;
  while(bx<=16){ S.set(bx,by,0,P.wood); bx++; if(bx>11) by++; }
  S.set(11,2,0,P.woodD); S.set(12,2,0,P.woodD);
  S.tubeZ(12,4,-2,2,P.woodD); S.tubeZ(14,5,-2,2,P.woodD);
  for(let dz=-2;dz<=2;dz++){ S.set(13,4,dz,P.sailD); S.set(13,3,dz,P.sail); }
  for(let dz=-2;dz<=2;dz++){ S.set(15,5,dz,P.sailD); }
  // jib triangles
  for(let s=0;s<=6;s++){ S.set(16-s,6-s,0,P.sailD); S.set(15-s,5-s,0,P.sail); }
  for(let s=0;s<=4;s++){ S.set(14+s,7,0,P.sailD); }

  /* foam at the waterline */
  for(let x=-10;x<=11;x++){ const h=Math.floor(halfAt(x,0.0)+.4);
    if(h>0){ S.set(x,0,-h-1,P.foam); S.set(x,0,h+1,P.foam); } }
  S.fill(11,0,-1,12,0,1,P.foam);

  /* rigging */
  const rig=[]; const RIG=(a,b)=>rig.push(new THREE.Vector3(...a),new THREE.Vector3(...b));
  const H1=[-6,16,0],H2=[0,21,0],H3=[6,18,0];
  RIG(H1,[16,6,0]); RIG(H2,[16,6,0]); RIG(H1,[-10,4,0]); RIG(H3,[-10,5,0]);
  RIG(H2,[-10,4,0]); RIG(H2,[11,2,0]);
  [[-4.2,0],[4.2,0],[0,-4],[0,4],[-6,-3.6],[-6,3.6],[6,-3.2],[6,3.2]].forEach(([sx,sz])=>{
    const hh = sx===0?H2:(sx<0?H1:H3);
    RIG(hh,[sx,2,sz]);
  });
  RIG(H1,[-6,2,-4]); RIG(H1,[-6,2,4]); RIG(H3,[6,2,-3]); RIG(H3,[6,2,3]);
  return rig;
}
const rigPts = ship();
const shipMesh = bake(S,{mat:matSolid});
const shipGlow = bake(SE,{mat:matGlow,cast:false,receive:false,ao:false});
SHIP.add(shipMesh, shipGlow);
{
  const g=new THREE.BufferGeometry();
  g.setFromPoints(rigPts);
  const lines=new THREE.LineSegments(g,new THREE.LineBasicMaterial({color:0x8f7b58}));
  lines.renderOrder=1; SHIP.add(lines);
}
SHIP.rotation.y = Math.PI/2;
SHIP.position.set(8,0,13);
scene.add(SHIP);

/* ══════════════════════════════ small boats ══════════════════════════════ */
function boat(hull,trim){
  const b=new VB;
  for(let x=-2;x<=2;x++){
    const h = 1 + (Math.abs(x)<=1?1:0);
    for(let z=-h;z<=h;z++) b.set(x,0,z,Math.abs(z)===h?P.woodD:hull);
    b.set(x,-1,z=>0,0); // noop guard
  }
  b.fill(-2,-1,-1,2,-1,1,hull); b.fill(-2,1,-2,-2,1,2,P.deck); b.fill(2,1,-2,2,1,2,P.deck);
  b.fill(-1,1,-1,1,1,1,P.deckD);
  b.tubeY(-1,0,1,3,trim); b.set(0,2,0,trim); b.fill(0,2,-1,0,2,1,P.cream);
  b.cyl(1,0,0,1,1,1.1,P.woodL);
  return b;
}
const boats=[];
function addBoat(vb,x,z,ry,phase,drift){
  const g=new THREE.Group();
  g.add(bake(vb,{mat:matSolid}));
  g.position.set(x,0,z); g.rotation.y=ry; g.userData={phase,drift};
  scene.add(g); boats.push(g); return g;
}
addBoat(boat(P.red,P.woodD),12,6.5,-0.5,0.0,0);
addBoat(boat(P.blue,P.cream),2,-19,2.2,1.7,0);
addBoat(boat(P.hullL,P.gold),-8,27,0.9,3.1,1);   // tender working the channel
addBoat(boat(P.woodG,P.cream),-13,-13,-1.1,4.4,0);
// rowboat tilted at the pier foot
{ const b=new VB; b.fill(-1,0,-1,1,0,1,P.woodD); b.fill(-1,1,-1,1,1,1,P.wood); b.fill(0,1,-1,0,1,1,P.deckD);
  const g=new THREE.Group(); g.add(bake(b,{mat:matSolid})); g.position.set(15.6,-.2,18.5);
  g.rotation.set(.12,.5,.22); scene.add(g); }

/* ══════════════════════════════ build static world ══════════════════════ */
terrain(); town(); pier(); crowd();
scene.add(bake(W,{mat:matSolid}));
scene.add(bake(E,{mat:matGlow,cast:false,receive:false,ao:false}));
const VOXELS = W.n + E.n + S.n + SE.n;
document.getElementById('oVox').textContent = VOXELS.toLocaleString('en-US')+' voxels';

/* ══════════════════════════════ sea ══════════════════════════════════════ */
const SEA_Y=-0.28;
const seaBase = new THREE.Mesh(new THREE.PlaneGeometry(560,560),
  new THREE.MeshLambertMaterial({color:P.seaDeep}));
seaBase.rotation.x=-Math.PI/2; seaBase.position.y=-1.15; seaBase.receiveShadow=true;
scene.add(seaBase);

const wg=[], wc=[];
for(let x=-44;x<=44;x++) for(let z=-44;z<=44;z++){
  if(solid(x,0,z)||solid(x,-1,z)) continue;
  wg.push(x,z);
  const shore = Math.max(0,1-Math.hypot(clamp(x,shoreX0,shoreX1)-x, clamp(z,shoreZ0,shoreZ1)-z)/6);
  const basin = x>QUA.town-4 ? 0 : Math.max(0,1-Math.hypot(x-2,z+2)/44);
  wg.push(shore, basin);
  wc.push(x< -18&&z>10? P.seaDeep : (shore>.4? P.shoal : (basin>.55? P.sea : P.seaL)));
}
const WN = wc.length;
const seaGeo = new THREE.BoxGeometry(0.96,0.9,0.96);
const sea = new THREE.InstancedMesh(seaGeo, lambert(), WN);
sea.receiveShadow=true; sea.castShadow=false;
{
  const M=new THREE.Matrix4(), c=new THREE.Color();
  for(let i=0;i<WN;i++){
    M.makeTranslation(wg[i*4],SEA_Y,wg[i*4+1]); sea.setMatrixAt(i,M);
    c.setHex(wc[i]); sea.setColorAt(i,c);
  }
}
scene.add(sea);
const seaLin = new Float32Array(WN*3);
{ const c=new THREE.Color(); for(let i=0;i<WN;i++){ c.setHex(wc[i]); seaLin[i*3]=c.r;seaLin[i*3+1]=c.g;seaLin[i*3+2]=c.b; } }
const seaMA = sea.instanceMatrix.array, seaCA = sea.instanceColor.array;

/* ══════════════════════════════ sky dome ═════════════════════════════════ */
const skyU = {
  uTop:{value:new THREE.Color(0x1f4d78)}, uHor:{value:new THREE.Color(0xd9ac86)},
  uLow:{value:new THREE.Color(0x31606e)}, uSun:{value:new THREE.Vector3(-1,.25,.4)},
  uSunCol:{value:new THREE.Color(0xffdca6)}
};
const sky = new THREE.Mesh(new THREE.SphereGeometry(430,26,18), new THREE.ShaderMaterial({
  side:THREE.BackSide, depthWrite:false, uniforms:skyU, fog:false,
  vertexShader:`varying vec3 vP; void main(){vP=position; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,
  fragmentShader:`
    varying vec3 vP; uniform vec3 uTop,uHor,uLow,uSun,uSunCol;
    void main(){
      vec3 d=normalize(vP); float h=d.y;
      vec3 col=mix(uHor,uTop,pow(clamp(h,0.,1.),.62));
      col=mix(col,uLow,pow(clamp(-h*2.4,0.,1.),.75));
      float s=max(dot(d,normalize(uSun)),0.);
      col+=uSunCol*pow(s,7.)*.85;
      col+=uSunCol*pow(s,80.)*1.7;
      col+=uSunCol*pow(max(1.-abs(h)*4.,0.),3.)*.14;
      gl_FragColor=vec4(col,1.);
    }`
}));
scene.add(sky);
const sunDisc = new THREE.Mesh(new THREE.SphereGeometry(9,16,16),
  new THREE.MeshBasicMaterial({color:0xfff1cf,fog:false}));
scene.add(sunDisc);

/* ══════════════════════════════ clouds ═══════════════════════════════════ */
const clouds=[];
for(let k=0;k<8;k++){
  const vb=new VB, cx=-90+k*24+Math.random()*14, cz=-70+Math.random()*140, cy=26+Math.random()*16;
  const n=2+(Math.random()*3|0);
  for(let i=0;i<n;i++){
    const px=cx+i*2.6+(Math.random()*4-2), pz=cz+(Math.random()*8-4), py=cy+(Math.random()*2-1);
    const rx=2+(Math.random()*3|0), rz=2+(Math.random()*3|0);
    for(let a=-rx;a<=rx;a++) for(let b=-rz;b<=rz;b++){
      if(Math.abs(a)+Math.abs(b)>rx+rz-1 && Math.random()<.5) continue;
      vb.set(px+a,py,pz+b, hash3(px+a,py,pz+b)>.5?0xfdf3e6:0xf3dfc8);
      vb.set(px+a,py-1,pz+b, hash3(px+a,py-1,pz+b)>.5?0xdcc6bd:0xc9c2c8);
      if(Math.random()<.4) vb.set(px+a,py+1,pz+b,0xffffff);
    }
  }
  const g=new THREE.Group(); g.add(bake(vb,{mat:lambert(),cast:false,receive:false}));
  g.position.set(0,0,0); g.userData.sp=1.1+Math.random()*1.6;
  scene.add(g); clouds.push(g);
}

/* ══════════════════════════════ gulls ════════════════════════════════════ */
const birds=[];
for(let i=0;i<7;i++){
  const g=new THREE.Group();
  const bmat=new THREE.MeshLambertMaterial({color:0xf6f3ea});
  const body=new THREE.Mesh(new THREE.BoxGeometry(.95,.42,.42),bmat); g.add(body);
  const wg=new THREE.BoxGeometry(.28,.1,1.35);
  const l=new THREE.Group(), r=new THREE.Group();
  const lm=new THREE.Mesh(wg,new THREE.MeshLambertMaterial({color:0xdcd8cc}));
  const rm=lm.clone();
  lm.position.z=.8; rm.position.z=-.8; l.add(lm); r.add(rm);
  l.position.z=.18; r.position.z=-.18; g.add(l,r);
  g.userData={l,r,ph:Math.random()*9,rad:16+Math.random()*20,sp:.19+Math.random()*.16,
              cx:2+(Math.random()*16-8),cz:0+(Math.random()*18-9),h:16+Math.random()*12};
  scene.add(g); birds.push(g);
}

/* ══════════════════════════════ chimney smoke ════════════════════════════ */
const puffs=[];
const puffMat = new THREE.MeshLambertMaterial({color:0xcfc7bf,transparent:true,opacity:.55});
SMOKERS.slice(0,4).forEach((p,i)=>{
  for(let k=0;k<5;k++){
    const m=new THREE.Mesh(new THREE.BoxGeometry(1,1,1),puffMat.clone());
    m.position.copy(p); m.userData={o:p,t:k/5,sp:.13+Math.random()*.06,i:i+k};
    scene.add(m); puffs.push(m);
  }
});

/* ══════════════════════════════ lighthouse beam ══════════════════════════ */
const beamGroup = new THREE.Group(); beamGroup.position.set(26,18.6,-19);
const cone = new THREE.Mesh(new THREE.ConeGeometry(3.4,44,4,1,true),
  new THREE.MeshBasicMaterial({color:0xffe6b0,transparent:true,opacity:.16,
    blending:THREE.AdditiveBlending,depthWrite:false,side:THREE.DoubleSide}));
cone.rotation.z=Math.PI/2; cone.position.x=22; beamGroup.add(cone);
const cone2 = cone.clone(); cone2.position.x=-22; cone2.rotation.z=-Math.PI/2; beamGroup.add(cone2);
beamGroup.userData={cone,cone2};
scene.add(beamGroup);
const beacons=[];
[[ -33,10,20,0xfff0c4],[7,8,25,0xffd9a0],[26,18,-17,0xfff4d8]].forEach(([x,y,z,c])=>{
  const l=new THREE.PointLight(c,42,26,2); l.position.set(x,y,z); scene.add(l); beacons.push(l);
  const halo=new THREE.Mesh(new THREE.SphereGeometry(.9,10,8),
    new THREE.MeshBasicMaterial({color:c,transparent:true,opacity:.85,fog:false}));
  halo.position.set(x,y,z); scene.add(halo); beacons.push(halo);
});

/* ══════════════════════════════ mooring lines ════════════════════════════ */
function rope(a,b,sag,col=0xa08a5e){
  const c=new THREE.CatmullRomCurve3([
    new THREE.Vector3(...a),
    new THREE.Vector3((a[0]+b[0])/2,(a[1]+b[1])/2-sag,(a[2]+b[2])/2),
    new THREE.Vector3(...b)]);
  const m=new THREE.Mesh(new THREE.TubeGeometry(c,10,.09,5,false),
    new THREE.MeshLambertMaterial({color:col}));
  m.castShadow=true; scene.add(m); return m;
}
const moorA=[],moorB=[];
for(let z of [5,21]){
  for(let dz=-.4;dz<=.4;dz+=.8)
    (z===5?moorA:moorB).push(rope([12,2.1,13+z+dz],[15,4.1,z],1.35));
}

/* ══════════════════════════════ time of day ══════════════════════════════ */
const C = (a,b,t)=>new THREE.Color(a).lerp(new THREE.Color(b),t);
const waterTint = new THREE.Color(1,1,1);
const hours=['dusk','early evening','sundown','late afternoon','afternoon','high noonsun'];
function applyTime(t){
  const el = THREE.MathUtils.lerp(7,42,t);
  const az = THREE.MathUtils.lerp(232,262,t);
  const r=THREE.MathUtils.degToRad(el), a=THREE.MathUtils.degToRad(az);
  const dir=new THREE.Vector3(Math.sin(a)*Math.cos(r),Math.sin(r),Math.cos(a)*Math.cos(r));
  sun.position.copy(dir).multiplyScalar(118); sun.target.position.set(6,4,2);
  sun.intensity = THREE.MathUtils.lerp(1.55,2.5,t);
  sun.color.copy(C(0xff9d55,0xfff0d2,t));
  hemi.intensity = THREE.MathUtils.lerp(.55,.95,t);
  hemi.color.copy(C(0x7f9dc0,0xbcd8ec,t));
  const warm = 1-t;
  skyU.uTop.value.copy(C(0x123a63,0x2f6ea3,t*0.9+0.1));
  skyU.uHor.value.copy(C(0xf0a166,0xe8cbb0,t));
  skyU.uLow.value.copy(C(0x2b4f62,0x3d7a88,t));
  skyU.uSun.value.copy(dir); skyU.uSunCol.value.copy(C(0xffb066,0xffeec4,t));
  sunDisc.position.copy(dir).multiplyScalar(380);
  sunDisc.material.color.copy(C(0xffb066,0xfff6de,t));
  sunDisc.scale.setScalar(1+warm*.7);
  FOG.copy(C(0xc48d74,0x9db8c4,t));
  scene.fog.color.set(FOG.getHex());
  seaBase.material.color.copy(C(0x173f52,0x14414f,t*0.4+0.3));
  waterTint.copy(C(0xffbb80,0xffffff,t*.85+0.15));
  beacons.forEach(b=>{ const on=THREE.MathUtils.clamp(1.25-t*1.6,0,1.15);
    if(b.isLight){b.intensity=42*on;} else {b.material.opacity=.35+.6*on;b.visible=on>.05;} });
  const h=Math.round(THREE.MathUtils.lerp(5.5,13,t));
  document.getElementById('oHour').textContent='— '+String(h).padStart(2,'0')+':00 '+hours[Math.min(5,Math.floor(t*6))];
}

/* ══════════════════════════════ views ════════════════════════════════════ */
const VIEWS=[
  {p:[-46,31,84], t:[4,7,4]},
  {p:[-16,7.5,26], t:[10,8,12]},
  {p:[46,15,52], t:[16,9,14]},
  {p:[6,96,40], t:[6,0,2]}
];
let fly=null;
function goto(i){
  const v=VIEWS[i];
  fly={p0:camera.position.clone(),t0:controls.target.clone(),
       p1:new THREE.Vector3(...v.p),t1:new THREE.Vector3(...v.t),k:0};
}
document.querySelectorAll('.chip').forEach(b=>b.addEventListener('click',()=>{
  document.querySelectorAll('.chip').forEach(x=>x.classList.remove('on'));
  b.classList.add('on'); goto(+b.dataset.v); userActed();
}));
const slider=document.getElementById('time');
slider.addEventListener('input',()=>{applyTime(+slider.value/100);userActed();});
const drift=document.getElementById('drift');
drift.addEventListener('change',()=>{controls.autoRotate=drift.checked;});

let idle=0, drifting=true;
function userActed(){ idle=0; controls.autoRotate=false; }
['pointerdown','wheel','touchstart'].forEach(e=>canvas.addEventListener(e,userActed,{passive:true}));
controls.addEventListener('start',userActed);

/* ══════════════════════════════ loop ═════════════════════════════════════ */
const clock=new THREE.Clock();
let first=true;
const rose=document.getElementById('rose');
const oBrg=document.getElementById('oBrg'), oTide=document.getElementById('oTide'), oWind=document.getElementById('oWind');

function animate(){
  requestAnimationFrame(animate);
  const dt=Math.min(clock.getDelta(),.05), T=clock.elapsedTime;

  /* water */
  for(let i=0;i<WN;i++){
    const x=wg[i*4], z=wg[i*4+1], shore=wg[i*4+2], basin=wg[i*4+3];
    const amp = (1-basin*.78);
    let h = Math.sin(x*.33+z*.20+T*1.05)*.30 + Math.sin(x*.12-z*.40+T*.72)*.22
          + Math.sin(z*.63+T*1.9)*.07;
    h*=amp;
    h += shore*Math.sin(x*.9+z*.8+T*2.6)*.14;
    seaMA[i*16+13]=SEA_Y+h;
    const gl = Math.pow(Math.max(0,Math.sin(x*1.05+T*1.9)*Math.sin(z*.86-T*1.4)),9)*1.6*amp;
    const k=.80+h*.42, r=seaLin[i*3]*k, g=seaLin[i*3+1]*k, b=seaLin[i*3+2]*k;
    const W1=gl*waterTint.r, W2=gl*waterTint.g*0.95, W3=gl*waterTint.b*0.8;
    seaCA[i*3]=(r+W2*.4+W3*.2)*waterTint.r;
    seaCA[i*3+1]=(g+W1*.3+W3*.2)*waterTint.g;
    seaCA[i*3+2]=(b+W1*.2+W2*.3)*waterTint.b;
  }
  sea.instanceMatrix.needsUpdate=true; sea.instanceColor.needsUpdate=true;

  /* ship */
  SHIP.position.y = Math.sin(T*.62)*.16 + Math.sin(T*1.3)*.05;
  SHIP.rotation.z = Math.sin(T*.55)*.011;
  SHIP.rotation.x = Math.sin(T*.42+1.2)*.007;
  const sy=SHIP.position.y;
  moorA.forEach(m=>{ m.position.y=sy*.8; m.rotation.x=Math.sin(T*.62)*.01; });
  boats.forEach(b=>{
    b.position.y=Math.sin(T*.9+b.userData.phase)*.14;
    b.rotation.z=Math.sin(T*.8+b.userData.phase)*.045;
    b.rotation.x=Math.sin(T*.6+b.userData.phase)*.03;
    if(b.userData.drift){
      const a=T*.11+b.userData.phase;
      b.position.x=-26+Math.cos(a)*20; b.position.z=34+Math.sin(a)*22;
      b.rotation.y=Math.PI/2-a;
    }
  });

  /* clouds */
  clouds.forEach(c=>{
    c.position.x+=dt*c.userData.sp;
    if(c.position.x>150) c.position.x=-150;
    c.position.y=Math.sin(T*.2+c.userData.sp)*.6;
  });

  /* birds */
  birds.forEach(b=>{
    const u=b.userData, a=T*u.sp+u.ph;
    b.position.set(u.cx+Math.cos(a)*u.rad, u.h+Math.sin(a*2.3)*1.6, u.cz+Math.sin(a)*u.rad);
    b.rotation.y=-a+Math.PI/2;
    const f=Math.sin(T*7.4+u.ph)*.75;
    u.l.rotation.x=f; u.r.rotation.x=-f;
  });

  /* smoke */
  puffs.forEach(p=>{
    p.userData.t+=dt*p.userData.sp;
    if(p.userData.t>1) p.userData.t-=1;
    const k=p.userData.t;
    p.position.set(p.userData.o.x+Math.sin(k*7+p.userData.i)*1.6+k*2.4,
                   p.userData.o.y+k*9, p.userData.o.z+Math.cos(k*5+p.userData.i)*1.4);
    const s=.5+k*2.4; p.scale.setScalar(s);
    p.rotation.set(k*2,k*1.4,k);
    p.material.opacity=.5*(1-k)*(k<.08?k/.08:1);
  });

  /* beacons */
  beamGroup.rotation.y += dt*.55;
  const pulse=.12+.10*Math.sin(T*2.2);
  beamGroup.userData.cone.material.opacity=pulse; beamGroup.userData.cone2.material.opacity=pulse;

  /* camera */
  if(fly){
    fly.k=Math.min(1,fly.k+dt*.85);
    const e=fly.k<.5?4*fly.k**3:1-Math.pow(-2*fly.k+2,3)/2;
    camera.position.lerpVectors(fly.p0,fly.p1,e);
    controls.target.lerpVectors(fly.t0,fly.t1,e);
    if(fly.k>=1) fly=null;
  } else {
    idle+=dt;
    if(drift.checked && idle>7 && !drifting){ drifting=true; controls.autoRotate=true; }
    if(!drift.checked) controls.autoRotate=false;
    if(controls.autoRotate) drifting=true;
  }
  controls.update();
  if(!controls.autoRotate) drifting=false;

  /* readouts */
  const ang=(Math.atan2(camera.position.x-controls.target.x,camera.position.z-controls.target.z)*180/Math.PI+360)%360;
  rose.style.transform='rotate('+(360-ang)+'deg)';
  oBrg.textContent=ang.toFixed(1)+'°';
  const tide=2.1+Math.sin(T*.13)*1.25;
  oTide.innerHTML=(tide>0?'+':'')+tide.toFixed(2)+'<small>m</small>';
  oWind.innerHTML='WSW '+Math.round(11+Math.sin(T*.4)*2.4)+'<small>kn</small>';

  renderer.render(scene,camera);
  if(first){ first=false; document.getElementById('boot').classList.add('gone'); goto(0); }
}

addEventListener('resize',()=>{
  camera.aspect=innerWidth/innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight);
});
applyTime(+slider.value/100);
animate();
</script>
</body>
</html>
```

A few things worth poking at:

- **Hour slider** (bottom right) drags the sun from dusk to high afternoon — sky gradient, fog, water tint, sail warmth and the harbor lamps all shift with it.
- **Viewpoint chips** fly the camera to four staged compositions: the channel approach, the berth alongside the Long Quay, the headland light, and a chart-table plan view.
- Auto-drift resumes after ~7 s of idle so the scene keeps breathing; any drag takes the wheel back instantly.
- Everything static (quarries, town, pier, hull, sails) collapses into a handful of instanced draw calls, so the ~110 k cubes plus a 12 000-cell animated sea stay smooth.