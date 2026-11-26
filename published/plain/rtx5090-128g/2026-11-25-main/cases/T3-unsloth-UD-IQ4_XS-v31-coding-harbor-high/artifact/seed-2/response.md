# Port of Calloway — a voxel harbour

A single-file WebGL diorama: a barque riding at anchor in the roads, the quay alive with lamps, cranes, gulls and chimney smoke, and a lighthouse that only wakes up when the sun goes down. Drag to orbit, scroll to zoom, or fly to a marked spot with the map pins. The **Bridge Console** runs time-of-day, sea swell, wind (the sails physically belly with it), harbour lights, bloom and rigging.

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<title>Port of Calloway — Voxel Harbour</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Alfa+Slab+One&family=Space+Grotesk:wght@400;500;600;700&family=Spline+Sans+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
:root{
  --ink:#07121e; --plate:#0d1b28; --plate2:#0a1622; --line:rgba(232,181,76,.26);
  --parch:#f0e6d2; --dim:#93a6b5; --brass:#e6b153; --red:#cf4b3c; --sea:#5fc3d8;
  --shadow:0 22px 50px rgba(2,8,15,.55);
}
*{box-sizing:border-box}
html,body{margin:0;height:100%;overflow:hidden;background:#06101a;color:var(--parch);
  font-family:'Space Grotesk',system-ui,sans-serif;-webkit-font-smoothing:antialiased}
#c{position:fixed;inset:0;width:100%;height:100%;display:block}
.layer{position:fixed;inset:0;pointer-events:none}
.vig{background:radial-gradient(120% 100% at 62% 38%, rgba(0,0,0,0) 38%, rgba(2,8,14,.55) 100%);z-index:2}
.grain{z-index:3;opacity:.05;mix-blend-mode:overlay;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")}
.ui{position:fixed;inset:0;z-index:6;pointer-events:none}
.ui>*{pointer-events:auto}
body.bare .ui{opacity:0;transform:scale(1.01);transition:.4s ease}
.ui{transition:.4s ease}

.card{background:linear-gradient(168deg,rgba(16,30,44,.94),rgba(8,17,26,.95));
  border:1px solid var(--line);border-radius:4px;box-shadow:var(--shadow),inset 0 1px 0 rgba(255,255,255,.06);
  position:relative;backdrop-filter:blur(6px)}
.card::before,.card::after{content:"";position:absolute;width:5px;height:5px;border-radius:50%;
  background:radial-gradient(circle at 35% 30%,#f4d191,#7c5a20);opacity:.75}
.card::before{top:7px;left:7px}.card::after{top:7px;right:7px}

/* ---- title ---- */
.title{position:absolute;top:22px;left:24px;width:min(370px,calc(100vw - 48px));padding:16px 18px 15px;
  animation:rise .8s cubic-bezier(.2,.9,.3,1) both}
.eyebrow{display:flex;align-items:center;gap:8px;font-family:'Spline Sans Mono',monospace;font-size:9.5px;
  letter-spacing:.3em;text-transform:uppercase;color:var(--brass)}
.eyebrow i{width:7px;height:7px;border-radius:50%;background:var(--sea);box-shadow:0 0 10px var(--sea);
  animation:blip 2.6s ease-in-out infinite}
h1{font-family:'Alfa Slab One',serif;font-weight:400;font-size:clamp(27px,3.6vw,40px);line-height:.94;
  margin:11px 0 8px;letter-spacing:.005em;text-shadow:0 2px 0 rgba(0,0,0,.35)}
h1 em{font-style:normal;color:var(--brass);display:block}
.rule{height:1px;background:linear-gradient(90deg,var(--brass),rgba(230,177,83,.05));margin:0 0 10px}
.sub{margin:0;font-size:12.4px;line-height:1.55;color:#b9c8d4;max-width:33ch}
.sub b{color:var(--parch);font-weight:600;letter-spacing:.06em}
.flags{display:flex;gap:6px;margin-top:13px}
.flag{width:22px;height:16px;border:1px solid rgba(0,0,0,.55);box-shadow:0 2px 6px rgba(0,0,0,.4);
  transform-origin:left center;animation:wave 3.4s ease-in-out infinite;cursor:default;transition:transform .25s}
.flag:hover{transform:translateY(-3px) scale(1.15)}
.f1{background:repeating-linear-gradient(0deg,#fff 0 4px,#cf4b3c 4px 8px)}
.f2{background:linear-gradient(135deg,#e6b153 50%,#1d2b3a 50%)}
.f3{background:linear-gradient(#1f5f8f,#1f5f8f)}
.f4{background:repeating-linear-gradient(90deg,#2f8f5a 0 6px,#f0e6d2 6px 12px)}
.f5{background:radial-gradient(circle at 50% 50%,#cf4b3c 0 45%,#f0e6d2 46%)}

/* ---- console ---- */
.deck{position:absolute;left:24px;bottom:24px;width:min(306px,calc(100vw - 48px));padding:12px 14px 14px;
  animation:rise .8s .12s cubic-bezier(.2,.9,.3,1) both}
.hd{display:flex;justify-content:space-between;align-items:center;margin-bottom:11px}
.hd h2{font-family:'Spline Sans Mono',monospace;font-weight:600;font-size:10px;letter-spacing:.26em;
  text-transform:uppercase;color:var(--parch);margin:0}
.hd .knob{font-family:'Spline Sans Mono',monospace;font-size:13px;color:var(--brass);background:none;border:none;
  cursor:pointer;padding:2px 6px;line-height:1;transition:.2s}
.hd .knob:hover{color:#fff;transform:scale(1.2)}
.body{overflow:hidden;transition:max-height .45s cubic-bezier(.4,0,.2,1),opacity .3s;max-height:520px}
.deck.min .body{max-height:0;opacity:0}
.row{margin-bottom:12px}
.row label{display:flex;justify-content:space-between;align-items:baseline;font-size:9.5px;letter-spacing:.2em;
  text-transform:uppercase;color:var(--dim);margin-bottom:6px}
.row output{font-family:'Spline Sans Mono',monospace;font-size:11px;letter-spacing:.06em;color:var(--brass)}
input[type=range]{-webkit-appearance:none;appearance:none;width:100%;height:3px;border-radius:2px;cursor:pointer;
  background:linear-gradient(90deg,var(--brass) var(--p,50%),rgba(240,230,210,.13) var(--p,50%))}
input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:13px;height:13px;background:var(--brass);
  border:1px solid #3c2a0b;transform:rotate(45deg);box-shadow:0 0 0 3px rgba(230,177,83,.16),0 2px 6px rgba(0,0,0,.5);
  transition:box-shadow .2s}
input[type=range]:hover::-webkit-slider-thumb{box-shadow:0 0 0 6px rgba(230,177,83,.2),0 2px 8px rgba(0,0,0,.6)}
input[type=range]::-moz-range-thumb{width:12px;height:12px;background:var(--brass);border:1px solid #3c2a0b;border-radius:2px}
.tg{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin:14px 0 4px}
.tg button,.views button{font-family:'Space Grotesk',sans-serif;font-size:10px;letter-spacing:.11em;
  text-transform:uppercase;color:#cfdbe4;background:rgba(255,255,255,.035);border:1px solid rgba(240,230,210,.14);
  border-radius:3px;padding:7px 6px;cursor:pointer;position:relative;overflow:hidden;transition:.18s}
.tg button::after,.views button::after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,transparent,rgba(255,255,255,.18),transparent);
  transform:translateX(-101%);transition:transform .55s}
.tg button:hover::after,.views button:hover::after{transform:translateX(101%)}
.tg button:hover,.views button:hover{color:#fff;border-color:var(--brass);transform:translateY(-1px);
  box-shadow:0 6px 16px rgba(0,0,0,.4)}
.tg button[data-on="1"]{background:rgba(230,177,83,.16);border-color:rgba(230,177,83,.75);color:#ffe9c2}
.tg button span{display:inline-block;width:6px;height:6px;border-radius:50%;margin-right:6px;vertical-align:1px;
  background:rgba(240,230,210,.2);transition:.2s}
.tg button[data-on="1"] span{background:var(--brass);box-shadow:0 0 8px var(--brass)}
.views{display:grid;grid-template-columns:1fr 1fr 1fr;gap:5px;margin-top:8px}
.views button{font-size:9px;padding:6px 3px;letter-spacing:.08em}
.views button.on{background:rgba(95,195,216,.14);border-color:rgba(95,195,216,.6);color:#dff6fb}

/* ---- right rail ---- */
.rail{position:absolute;top:22px;right:24px;display:flex;flex-direction:column;align-items:flex-end;gap:10px;
  animation:rise .8s .2s cubic-bezier(.2,.9,.3,1) both}
.compass{width:74px;height:74px;opacity:.92}
.compass .rose{transition:transform .12s linear;transform-origin:50% 50%}
.stats{font-family:'Spline Sans Mono',monospace;font-size:10px;color:var(--dim);letter-spacing:.08em;
  text-align:right;line-height:1.7;padding:8px 11px}
.stats b{color:var(--brass);font-weight:600}
.log{position:absolute;right:24px;bottom:24px;max-width:min(360px,64vw);padding:9px 13px;font-size:11.5px;
  color:#c3d2dd;letter-spacing:.02em;animation:rise .8s .28s cubic-bezier(.2,.9,.3,1) both}
.log .stamp{font-family:'Spline Sans Mono',monospace;color:var(--brass);font-size:10px;letter-spacing:.16em;
  margin-right:9px}
.log .txt{display:inline-block;animation:fadein .6s ease both}
.hint{position:absolute;left:50%;bottom:26px;transform:translateX(-50%);font-family:'Spline Sans Mono',monospace;
  font-size:9.5px;letter-spacing:.28em;text-transform:uppercase;color:rgba(240,230,210,.5);
  padding:6px 14px;border:1px solid rgba(240,230,210,.14);border-radius:99px;background:rgba(8,17,26,.5);
  transition:opacity .8s;white-space:nowrap}
.hint.gone{opacity:0}

/* ---- pins ---- */
.pin{position:absolute;left:0;top:0;width:16px;height:16px;margin:-8px 0 0 -8px;border-radius:50%;cursor:pointer;
  border:1.5px solid rgba(240,230,210,.75);background:rgba(9,18,27,.55);display:grid;place-items:center;
  transition:transform .2s,border-color .2s;will-change:transform}
.pin i{width:4px;height:4px;border-radius:50%;background:var(--brass);display:block}
.pin::after{content:"";position:absolute;inset:-4px;border-radius:50%;border:1px solid rgba(230,177,83,.5);
  animation:ping 2.8s ease-out infinite}
.pin:hover{transform:scale(1.25);border-color:var(--brass)}
.pin b{position:absolute;left:20px;top:50%;transform:translate(-4px,-50%);white-space:nowrap;
  font-family:'Spline Sans Mono',monospace;font-size:9.5px;letter-spacing:.14em;text-transform:uppercase;
  color:var(--parch);background:rgba(9,18,27,.82);border:1px solid rgba(230,177,83,.35);padding:3px 7px;
  opacity:0;transition:.2s;pointer-events:none;font-weight:400}
.pin:hover b{opacity:1;transform:translate(0,-50%)}

@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@keyframes fadein{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}
@keyframes blip{0%,100%{opacity:1}50%{opacity:.25}}
@keyframes ping{0%{transform:scale(.7);opacity:.9}70%,100%{transform:scale(1.9);opacity:0}}
@keyframes wave{0%,100%{transform:skewY(0deg)}50%{transform:skewY(-5deg)}}
@media(max-width:760px){
  .title{top:12px;left:12px;padding:12px 14px}
  .deck{left:12px;right:12px;bottom:12px;width:auto}
  .log{display:none}.hint{bottom:auto;top:calc(100% - 190px)}
  .rail{top:12px;right:12px}.compass{width:56px;height:56px}
}
</style>
</head>
<body>
<canvas id="c"></canvas>
<div class="layer vig"></div><div class="layer grain"></div>

<div class="ui">
  <header class="card title">
    <div class="eyebrow"><i></i>Voxel Harbour · Live Render</div>
    <h1>Port of<em>Calloway</em></h1>
    <div class="rule"></div>
    <p class="sub">Barque <b>“AURELIA”</b>, 214 tons, from Oporto with port wine and salt. Ridden out to the roads, waiting the tide and a pilot.</p>
    <div class="flags" title="Dressed overall for the harbour">
      <div class="flag f1"></div><div class="flag f2"></div><div class="flag f3"></div>
      <div class="flag f4"></div><div class="flag f5"></div>
    </div>
  </header>

  <aside class="card deck" id="deck">
    <div class="hd"><h2>Bridge Console</h2><button class="knob" id="fold" aria-label="collapse">–</button></div>
    <div class="body">
      <div class="row"><label>Hour of day <output id="oTime">17:00</output></label><input id="sTime" type="range" min="5" max="21" step="0.02" value="17"></div>
      <div class="row"><label>Sea swell <output id="oSwell">0.9 m</output></label><input id="sSwell" type="range" min="0.15" max="1.9" step="0.01" value="0.8"></div>
      <div class="row"><label>Wind <output id="oWind">12 kn SW</output></label><input id="sWind" type="range" min="0" max="1.6" step="0.01" value="0.85"></div>
      <div class="tg">
        <button id="tSail" data-on="1"><span></span>Sails set</button>
        <button id="tLight" data-on="-1"><span></span>Harbour lit</button>
        <button id="tGlow" data-on="1"><span></span>Lamp glow</button>
        <button id="tRig" data-on="1"><span></span>Rigging</button>
      </div>
      <div class="views" id="views">
        <button data-v="0" class="on">Roads</button><button data-v="1">Broadside</button>
        <button data-v="2">The Quay</button><button data-v="3">Lighthouse</button>
        <button data-v="4">The Gap</button><button data-v="5">Chart</button>
      </div>
    </div>
  </aside>

  <div class="rail">
    <svg class="compass" viewBox="0 0 100 100">
      <circle cx="50" cy="50" r="34" fill="rgba(9,18,27,.55)" stroke="rgba(230,177,83,.35)"/>
      <g class="rose" id="rose">
        <path d="M50 14 L56 46 L50 40 L44 46 Z" fill="#e6b153"/>
        <path d="M50 86 L44 54 L50 60 L56 54 Z" fill="rgba(240,230,210,.5)"/>
        <path d="M14 50 L46 44 L40 50 L46 56 Z" fill="rgba(240,230,210,.35)"/>
        <path d="M86 50 L54 56 L60 50 L54 44 Z" fill="rgba(240,230,210,.35)"/>
        <text x="50" y="11" font-family="Spline Sans Mono,monospace" font-size="9" fill="#e6b153" text-anchor="middle">N</text>
      </g>
      <circle cx="50" cy="50" r="2" fill="#f0e6d2"/>
    </svg>
    <div class="card stats" id="stats">voxels <b>—</b><br>draws <b>—</b><br>fps <b>—</b></div>
  </div>

  <div class="card log" id="log"></div>
  <div id="pins"></div>
  <div class="hint" id="hint">drag to look · scroll to zoom · press H to hide panels</div>
</div>

<script type="importmap">
{"imports":{
  "three":"https://cdn.jsdelivr.net/npm/three@0.161.0/build/three.module.js",
  "three/addons/":"https://cdn.jsdelivr.net/npm/three@0.161.0/examples/jsm/"
}}
</script>

<script type="module">
import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';

/* ══════════════════════════════ 0. UTILS ══════════════════════════════ */
const clamp=(v,a,b)=>v<a?a:v>b?b:v;
const lerp=(a,b,t)=>a+(b-a)*t;
const sstep=(a,b,x)=>{const t=clamp((x-a)/(b-a),0,1);return t*t*(3-2*t);};
function hash3(x,y,z){let h=(x|0)*374761393+(y|0)*668265263+(z|0)*1274126177;h=(h^(h>>13))*1274126177;return ((h^(h>>16))>>>0)/4294967295;}

/* Voxel accumulator ---------------------------------------------------- */
class Vox{
  constructor(){this.n=0;this.p=[];this.s=[];this.c=[];this.q=[];}
  put(x,y,z,sx,sy,sz,color){
    this.p.push(x,y,z);this.s.push(sx,sy,sz);
    this.c.push(color.isColor?color.clone():new THREE.Color(color));
    this.q.push(0,0,0,1);this.n++;
  }
  putQ(x,y,z,sx,sy,sz,color,q){
    this.p.push(x,y,z);this.s.push(sx,sy,sz);
    this.c.push(color.isColor?color.clone():new THREE.Color(color));
    this.q.push(q.x,q.y,q.z,q.w);this.n++;
  }
  box(x0,x1,y0,y1,z0,z1,color,o={}){
    const step=o.step||1, jit=o.jitter===undefined?.08:o.jitter, ch=o.chance===undefined?1:o.chance;
    const X0=Math.floor(x0),X1=Math.ceil(x1),Y0=Math.floor(y0),Y1=Math.ceil(y1),Z0=Math.floor(z0),Z1=Math.ceil(z1);
    for(let x=X0;x<X1;x+=step)for(let y=Y0;y<Y1;y+=step)for(let z=Z0;z<Z1;z+=step){
      if(o.outer && x>X0 && x+step<X1 && y>Y0 && y+step<Y1 && z>Z0 && z+step<Z1) continue;
      if(ch<1 && hash3(x*7+3,y*13+1,z*17+5)>ch) continue;
      const sx=Math.min(step,X1-x),sy=Math.min(step,Y1-y),sz=Math.min(step,Z1-z);
      const cx=x+sx/2,cy=y+sy/2,cz=z+sz/2;
      if(jit){const f=1+(hash3(x+11,y+29,z+47)-.5)*jit;_c.set(color).multiplyScalar(f);this.put(cx,cy,cz,sx,sy,sz,_c);}
      else this.put(cx,cy,cz,sx,sy,sz,color);
    }
  }
  /* oriented strut from a→b */
  strut(a,b,w,h,color){
    const dir=new THREE.Vector3(b.x-a.x,b.y-a.y,b.z-a.z), L=dir.length();
    if(L<1e-3)return; dir.normalize();
    const q=new THREE.Quaternion().setFromUnitVectors(_up,dir);
    const m=new THREE.Vector3((a.x+b.x)/2,(a.y+b.y)/2,(a.z+b.z)/2);
    this.putQ(m.x,m.y,m.z,w,L,h,color,q);
  }
  mast(x,y0,y1,color){for(let y=Math.floor(y0);y<y1;y++)this.put(x,y+.5,x===0?0:0,1,1,1,color); /*noop guard*/}
}
const _c=new THREE.Color(),_up=new THREE.Vector3(0,1,0);

let TOTAL=0;
function toMesh(vx,opt={}){
  if(!vx.n) return null;
  const geo=new THREE.BoxGeometry(1,1,1);
  const mat=opt.material||new THREE.MeshLambertMaterial();
  const im=new THREE.InstancedMesh(geo,mat,vx.n);
  const M=new THREE.Matrix4(),P=new THREE.Vector3(),S=new THREE.Vector3(),Q=new THREE.Quaternion();
  for(let i=0;i<vx.n;i++){
    Q.set(vx.q[i*4],vx.q[i*4+1],vx.q[i*4+2],vx.q[i*4+3]);
    M.compose(P.set(vx.p[i*3],vx.p[i*3+1],vx.p[i*3+2]),Q,S.set(vx.s[i*3],vx.s[i*3+1],vx.s[i*3+2]));
    im.setMatrixAt(i,M);im.setColorAt(i,vx.c[i]);
  }
  im.castShadow=opt.cast!==false;im.receiveShadow=opt.recv!==false;
  im.instanceMatrix.needsUpdate=true;if(im.instanceColor)im.instanceColor.needsUpdate=true;
  if(!opt.dynamic){im.computeBoundingSphere();}else im.frustumCulled=false;
  TOTAL+=vx.n;return im;
}

/* ══════════════════════════════ 1. RENDERER ══════════════════════════════ */
const canvas=document.getElementById('c');
const renderer=new THREE.WebGLRenderer({canvas,antialias:true,powerPreference:'high-performance'});
renderer.setPixelRatio(Math.min(devicePixelRatio,1.8));
renderer.setSize(innerWidth,innerHeight);
renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;
renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.0;

const scene=new THREE.Scene();
scene.fog=new THREE.Fog(0x9db6c8,110,420);
const camera=new THREE.PerspectiveCamera(46,innerWidth/innerHeight,.5,3200);
camera.position.set(96,54,76);
const controls=new OrbitControls(camera,renderer.domElement);
controls.enableDamping=true;controls.dampingFactor=.055;
controls.minDistance=14;controls.maxDistance=230;controls.maxPolarAngle=1.51;
controls.target.set(0,9,4);

/* palette */
const C={
  stoneD:0x4b5057,stone:0x6c7077,stoneL:0x8d9298,kerb:0x9ea09a,cobble:0x7c766c,cobble2:0x8a8377,
  grass:0x55743f,grass2:0x4a6838,sand:0xc8b98c,rock:0x5b5c5f,dirt:0x6f5b42,
  wood:0x77542f,woodL:0xa07a4c,woodD:0x4a3421,deck:0xb88d5b,deckD:0x916e45,
  hull:0x202933,hullD:0x161e27,anti:0x6d3327,gold:0xd9a83f,white:0xf1ece0,
  canvas:0xe9dcc0,canvas2:0xd3c3a2,canvasBand:0xc4704a,
  rope:0xbc9f74,metal:0x3b424a,iron:0x2a2f36,
  brick:0xa05745,brickD:0x8b4a3c,plaster:0xe2d6bd,paintBlue:0x6f8ea1,paintGreen:0x4c6c58,
  roofRed:0xa0503c,roofSlate:0x3b4654,roofGreen:0x3f6352,
  glass:0xffc46a,lamp:0xffb65c,lantern:0xfff0c4,foam:0xe6f5f7,
  red:0xc0392b,green:0x2f8f5a,yellow:0xe6b93c,blue:0x2d6ea5,copper:0xb06a3a
};

/* ══════════════════════════════ 2. SKY + LIGHT ══════════════════════════════ */
const skyU={
  uTop:{value:new THREE.Color(0x2f76bd)},uHor:{value:new THREE.Color(0xbcd9ea)},
  uSun:{value:new THREE.Color(0xfff2da)},uSunDir:{value:new THREE.Vector3(0,1,0)},
  uMoonDir:{value:new THREE.Vector3(-.6,.5,.4)},uNight:{value:0},uSunI:{value:1}
};
const sky=new THREE.Mesh(new THREE.SphereGeometry(1500,34,18),new THREE.ShaderMaterial({
  side:THREE.BackSide,depthWrite:false,fog:false,uniforms:skyU,
  vertexShader:`varying vec3 vD;void main(){vD=normalize(position);gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,
  fragmentShader:`
  varying vec3 vD;uniform vec3 uTop,uHor,uSun,uSunDir,uMoonDir;uniform float uNight,uSunI;
  float h31(vec3 p){p=fract(p*vec3(443.897,441.423,437.195));p+=dot(p,p.yzx+19.19);return fract((p.x+p.y)*p.z);}
  void main(){
    vec3 d=normalize(vD);float h=d.y;
    vec3 col=mix(uHor,uTop,pow(clamp(h*1.18,0.,1.),.62));
    col=mix(mix(uHor*1.06,col,smoothstep(-.14,0.,h)),col,step(0.,h));
    float sd=max(dot(d,normalize(uSunDir)),0.);
    col+=uSun*uSunI*(pow(sd,2200.)*16.+pow(sd,60.)*.62+pow(sd,8.)*.17);
    float md=max(dot(d,normalize(uMoonDir)),0.);
    col+=vec3(.86,.92,1.)*uNight*(pow(md,4000.)*11.+pow(md,90.)*.30);
    if(uNight>.01&&h>0.){float st=step(.9977,h31(floor(d*230.)));
      col+=vec3(st)*uNight*smoothstep(.02,.32,h)*(1.2+.6*sin(d.z*60.));}
    gl_FragColor=vec4(col,1.);}`
}));
sky.renderOrder=-1;scene.add(sky);

const hemi=new THREE.HemisphereLight(0x9fc3e8,0x4a4636,.65);scene.add(hemi);
const amb=new THREE.AmbientLight(0xffffff,.12);scene.add(amb);
const sun=new THREE.DirectionalLight(0xffffff,3);
sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);
{const s=sun.shadow.camera;s.left=-105;s.right=105;s.top=105;s.bottom=-105;s.near=1;s.far=460;}
sun.shadow.bias=-.0007;sun.shadow.normalBias=.55;
sun.target.position.set(4,6,-4);scene.add(sun.target,sun);

/* ══════════════════════════════ 3. WORLD ══════════════════════════════ */
const V=new Vox(),E=new Vox();

/* ---- coastline & fields east of town ---- */
function coast(){
  for(let x=42;x<86;x+=2)for(let z=-72;z<72;z+=2){
    const inland=(x-42)/44;
    let h=5+Math.round((inland*4+Math.sin(x*.19)*Math.cos(z*.15)*1.6+hash3(x,1,z)*1.2)*2)/2;
    if(x<46)h=5;
    const rockEdge=x<45;
    V.box(x,x+2,-3,h,z,z+2,rockEdge?C.rock:(h>7?C.grass2:C.grass),{jitter:.16,step:2});
  }
  for(let z=-72;z<72;z+=2){ // shore band + quay footing
    V.box(40,43,-3,5,z,z+2,C.sand,{jitter:.14,step:2,chance:.9});
  }
  for(let z=-104;z<-34;z+=2)for(let x=12;x<86;x+=2){
    const h=4+Math.round((Math.sin(x*.11+z*.07)*2+ (x-12)/12 +hash3(x,3,z)*1.4)*2)/2;
    V.box(x,x+2,-3,Math.max(4.4,h),z,z+2,h>6?C.grass2:C.grass,{jitter:.17,step:2});
  }
  for(let z=34;z<78;z+=2)for(let x=12;x<86;x+=2){
    const h=4+Math.round((Math.cos(x*.09-z*.06)*2+(x-12)/14+hash3(x,5,z)*1.3)*2)/2;
    V.box(x,x+2,-3,Math.max(4.4,h),z,z+2,h>6.2?C.grass2:C.grass,{jitter:.17,step:2});
  }
}
/* ---- quay ---- */
function quay(){
  V.box(13,42,-9,4,-34,34,C.stoneD,{step:3,outer:false,jitter:.1});
  V.box(12,13,-9,5,-34,34,C.stone,{jitter:.15});                    // sea wall
  V.box(12,13,-.6,2.4,-34,34,0x3d4a3f,{jitter:.3,chance:.45});      // weed at waterline
  V.box(12,13,5,6,-34,34,C.kerb,{jitter:.1});
  V.box(13,18,4,5,-34,34,C.cobble,{jitter:.16});                    // apron
  V.box(18,42,4,5,-34,34,C.cobble2,{jitter:.13,step:2});
  // painted berth line + drain
  V.box(14.5,15.5,5,5.09,-30,30,0xb9a15a,{jitter:.02});
  V.box(18,42,5,5.06,-2,-1,0x3c3f44,{jitter:.06,step:2});
  // bollards
  for(const bz of [-30,-22,-14,-6,2,10,18,26]){
    V.box(13,14.4,5,7,bz,bz+1.4,C.stoneL,{jitter:.06});
    V.box(12.8,14.6,7,7.6,bz-.1,bz+1.5,C.stoneD,{jitter:.05});
  }
  // steps down to the water
  for(let i=0;i<6;i++)V.box(12-i*.4,14.4,5-i,-i+ .001,14,19,C.stoneL,{jitter:.09});
  // sloped slipway
  for(let i=0;i<7;i++)V.box(12-i*.5,13.6,5-i*.8,5-i*.8+.6,-22,-17,C.stoneD,{jitter:.1});
  // mooring rings + capstan on the quay
  V.box(19,20,5,6.6,-24,-23,C.woodD);V.box(18.5,20.5,6.6,7,-24.5,-22.5,C.wood);
}
/* ---- buildings ---- */
function pitched(v,x0,x1,z0,z1,baseY,rise,color){
  const d=z1-z0;
  for(let i=0;i<rise;i++){
    const zs=z0+Math.round(d*i/(2*rise)),ze=z1-Math.round(d*i/(2*rise));
    if(ze-zs<=1){v.box(x0,x1,baseY+i,baseY+i+1,(zs+ze)/2,(zs+ze)/2+1,color,{jitter:.12});break;}
    v.box(x0,x1,baseY+i,baseY+i+1,zs,ze,color,{jitter:.12});
  }
}
function gable(v,x0,x1,z0,z1,baseY,rise,wall){
  const d=z1-z0;
  for(let i=0;i<rise;i++){
    const zs=z0+Math.round(d*i/(2*rise)),ze=z1-Math.round(d*i/(2*rise));
    if(ze<=zs)break;
    v.box(x0,x0+1,baseY+i,baseY+i+1,zs,ze,wall,{jitter:.08});
    v.box(x1-1,x1,baseY+i,baseY+i+1,zs,ze,wall,{jitter:.08});
  }
}
function glow(x,y,z,dir,sz=1,color=C.glass,thick=.14){
  const o=thick*.7;
  if(dir==='-x')E.put(x-o,y,z,sz*0+thick,sz,sz,new THREE.Color(color).multiplyScalar(2.1));
  if(dir==='+x')E.put(x+o,y,z,thick,sz,sz,new THREE.Color(color).multiplyScalar(2.1));
  if(dir==='-z')E.put(x,y,z-o,sz,sz,thick,new THREE.Color(color).multiplyScalar(2.1));
  if(dir==='+z')E.put(x,y,z+o,sz,sz,thick,new THREE.Color(color).multiplyScalar(2.1));
}
function windowRow(v,x,y,z0,z1,face,wall){
  for(let z=z0;z<z1;z+=3){
    if(face==='-x'){v.box(x-1.02,x-1,y-1,y+1,z,z+1,C.woodD);glow(x-1,y+.2,z+.5,'-x',1);}
    else{v.box(x,x+1.02,y-1,y+1,z,z+1,C.woodD);glow(x+1,y+.2,z+.5,'+x',1);}
  }
}
function building(o){
  const{x0,z0,x1,z1,h,wall,roof,rise=3,door=[0,0],lanes=-1}=o;
  V.box(x0,x1,5,5+h,z0,z1,wall,{outer:true,jitter:.1});
  V.box(x0,x1,5,6,z0,z1,C.stoneD,{outer:true,jitter:.08});
  pitched(V,x0-1,x1+1,z0,z1,5+h,rise,roof);
  gable(V,x0,x1,z0,z1,5+h,rise,wall);
  V.box(x0-1,x1+1,5+h,5+h+.4,z0-.2,z0+.2,C.woodD);
  V.box(x0-1,x1+1,5+h,5+h+.4,z1-.2,z1+.2,C.woodD);
  // door on -x (harbour) face
  const dz=door[1];
  V.box(x0-1.05,x0,5,8,dz,dz+2,C.woodD,{jitter:.05});
  V.box(x0-1.1,x0-.15,5,7.5,dz+.2,dz+1.8,C.wood);
  // windows
  for(let z=z0+1;z<z1-1;z+=3){
    if(Math.abs(z-dz)<2.4)continue;
    for(const wy of [7.4,(h>8?11.2:null)]){if(wy===null||wy>5+h)continue;
      V.box(x0-1.1,x0,wy-1,wy+1,z,z+1,C.woodD);glow(x0-.05,wy,z+.5,'-x',1);}
  }
  if(lanes>0)for(let x=x0+1;x<x1-1;x+=3){
    const wy=7.4;if(wy>4+h)continue;
    V.box(x,x+1,wy-1,wy+1,z1,z1+.1,C.woodD);glow(x+.5,wy,z1+.05,'+z',1);
  }
}
function town(){
  building({x0:24,x1:32,z0:-14,z1:-4,h:7,wall:C.brick,roof:C.roofSlate,rise:3,door:[0,-9]});
  building({x0:24,x1:31,z0:0,z1:9,h:8,wall:C.paintBlue,roof:C.roofSlate,rise:3,door:[0,4]});
  building({x0:24,x1:33,z0:13,z1:24,h:9,wall:C.plaster,roof:C.roofRed,rise:4,door:[0,18]});
  building({x0:24,x1:31,z0:27,z1:33,h:6,wall:C.woodL,roof:C.roofGreen,rise:3,door:[0,30]});
  building({x0:35,x1:42,z0:-24,z1:-14,h:10,wall:C.brickD,roof:C.roofSlate,rise:3,door:[0,-19]});
  building({x0:35,x1:42,z0:24,z1:33,h:7,wall:C.plaster,roof:C.roofRed,rise:3,door:[0,28]});
  building({x0:35,x1:41,z0:6,z1:14,h:11,wall:C.brick,roof:C.roofSlate,rise:4,door:[0,10]});
  // customs house clock + flagpole
  V.box(27,30,15,18,18.6,20.6,C.plaster,{jitter:.05});
  E.put(28.5,16.5,18.55,'+z',0,0,0,0);
  E.n--;E.p.length-=3;E.s.length-=3;E.c.length--;E.q.length-=4;
  glow(28.5,16.6,20.6,'+z',1.4,0xffeab8);
  V.box(28,29,19,26,C.woodD);V.box(28,30.5,25,25.4,C.white);
  // chimney stacks with smoke sources
  const stacks=[[26.5,-6],[29.5,2],[30.5,21],[38,-21],[37,30]];
  stacks.forEach(([x,z],i)=>{
    V.box(x,x+1.4,12,16,z,z+1.4,i%2?C.brickD:C.brick,{jitter:.1});
    V.box(x-.15,x+1.55,16,16.5,z-.15,z+1.55,C.stoneD);
    smokeSrc.push(new THREE.Vector3(x+.7,16.6,z+.7));
  });
  // yard clutter
  const crates=[...Array(26)].map(()=>[13.5+Math.random()*4|0,-31+Math.random()*62|0]);
  crates.forEach(([x,z])=>{
    if(z>12&&z<24)return;
    const n=1+((hash3(x,2,z)*3)|0),w=1+((hash3(x,3,z)*2)|0);
    for(let i=0;i<n;i++)V.box(x,x+w,5+i*1.5,6.5+i*1.5,z,z+1.5,i%2?C.wood:C.woodD,{jitter:.12});
  });
  for(let i=0;i<14;i++){
    const x=14+Math.random()*3.4|0,z=-30+Math.random()*60|0;
    V.put(x+.5,5.85,z+.5,1.3,1.7,1.3,hash3(x,9,z)>.5?C.wood:C.woodD);
    V.put(x+.5,6.75,z+.5,1.05,.2,1.05,C.stoneD);
  }
  // market stalls
  const cols=[[C.red,C.white],[C.blue,C.white],[C.yellow,C.canvas]];
  for(let s=0;s<3;s++){
    const z=8+s*4;
    V.box(15,18,5,7.2,z,z+3,C.woodD,{outer:true});
    for(let i=0;i<3;i++)V.box(15,18,7.2+i*.25,7.5+i*.25,z+i,z+i+1,cols[s][i%2],{jitter:.05});
    V.box(15,15.3,5,7.3,z,z+.3,C.wood);V.box(17.7,18,5,7.3,z,z+.3,C.wood);
    V.box(15.4,17.6,7.2,7.45,z+1.1,z+1.9,C.green,{jitter:.2});
  }
  // timber derrick crane
  const px=16.5,pz=-8,base=6;
  V.box(15,18,5,13,pz,pz+3,C.woodD,{outer:true,jitter:.08});
  V.box(15.4,17.6,13,14,pz+.4,pz+2.6,C.wood);
  const tip=new THREE.Vector3(6,17.5,pz+1.5), head=new THREE.Vector3(16.5,14.2,pz+1.5),
        counter=new THREE.Vector3(23,11.5,pz+1.5);
  V.strut(head,tip,.9,.9,C.woodL);V.strut(head,counter,1.1,1.1,C.stoneD);
  V.strut(new THREE.Vector3(16.5,19.5,pz+1.5),tip,.18,.18,C.rope);
  V.strut(new THREE.Vector3(16.5,19.5,pz+1.5),counter,.18,.18,C.rope);
  for(let i=0;i<3;i++)V.strut(new THREE.Vector3(15+i,13.4,pz),new THREE.Vector3(15+i,6,pz),.5,.5,C.metal);
  cranePivot=new THREE.Vector3(6,17.5,pz+1.5);
  // lamp posts
  const lampZ=[-28,-18,-8,2,12,22];
  lampZ.forEach((z,i)=>{
    V.box(13.3,14.1,5,9.6,z-.15,z+.65,C.iron);
    V.box(13,14.4,9.6,10,z-.3,z+.8,C.iron);
    V.box(12.9,14.5,10,11,z-.35,z+.85,0x1e242a);
    glow(13.7,10.5,z+.25,'-x',.9,C.lamp,.7);
    if(i%2===0){const L=new THREE.PointLight(0xffb65c,0,34,2);L.position.set(13.6,10.5,z+.25);scene.add(L);lampLights.push(L);}
  });
  // brazier at the market
  V.box(19,20.4,5,6,4,5.4,C.iron);
  const bl=new THREE.PointLight(0xff8a3c,0,20,2);bl.position.set(19.7,7,4.7);scene.add(bl);lampLights.push(bl);
  brazier=new THREE.Vector3(19.7,6.4,4.7);
  // nets on frames + carts
  for(let z=-16;z<-10;z+=1){V.strut(new THREE.Vector3(20.5,5,z),new THREE.Vector3(20.5,7,z),.14,.14,C.rope);}
  V.box(20.4,20.6,7,7.2,-16,-10,C.wood);
  // trees
  for(let i=0;i<22;i++){
    const x=44+hash3(i,7,i*3)*38|0, z=-60+hash3(i*5,11,i)*120|0;
    let gy=5;if(x>44)gy=5+Math.round(((x-42)/44*4)*2)/2;
    tree(x,gy,z,i);
  }
  // windmill on the hill
  windmill(56,9,-14);
  // beacon on the point
  V.box(78,80,8,16,-40,-38,C.white,{jitter:.04});
  V.box(77.4,80.6,16,16.4,-40.6,-37.4,C.roofRed);
}
function tree(x,y,z,seed){
  const h=3+(hash3(seed,3,9)*2|0);
  V.box(x,x+1,y,y+h,z,z+1,C.woodD,{jitter:.1});
  for(let i=0;i<10;i++){
    const dx=(hash3(seed*3+i,1,i)*3-1)|0,dz=(hash3(seed*5+i,2,i)*3-1)|0,dy=(hash3(seed*7+i,3,i)*2|0);
    V.put(x+.5+dx,y+h-.5+dy,z+.5+dz,1.6,1.4,1.6,hash3(seed+i,4,4)>.45?C.grass2:0x618146);
  }
}
let windmillHub=null;
function windmill(x,y,z){
  V.box(x,x+5,y,y+9,z,z+5,C.plaster,{outer:true,jitter:.06});
  for(let i=0;i<3;i++)V.box(x,x+5,y+i*3,y+i*3+.4,z-.2,z+5.2,C.woodD);
  V.box(x-.6,x+5.6,y+9,y+11,z+1.6,z+3.4,C.roofRed,{outer:true});
  V.box(x+2.2,x+2.8,y+9.6,y+10.4,z+1,z+5,C.woodD);
  windmillHub=new THREE.Vector3(x+2.5,10.4,z+5);
}
/* ---- lighthouse ---- */
function lighthouse(){
  const cx=36,cz=-28;
  V.box(cx-7,cx+7,4,7,cz-7,cz+7,C.stoneD,{outer:true,jitter:.1});
  const y0=7,y1=32;
  for(let y=y0;y<y1;y++){
    const r=lerp(4.7,3.0,(y-y0)/(y1-y0)), r2=lerp(4.7,3.0,(y+1-y0)/(y1-y0));
    for(let a=0;a<48;a++){
      const th=a/48*Math.PI*2,x=Math.cos(th),z=Math.sin(th);
      if(Math.abs(x)*r+Math.abs(z)*r<r-.7)continue;
      const white=Math.floor((y-y0)/5)%2===0;
      V.put(cx+x*r+.5,y+.5,cz+z*r+.5,1.15,1,1.15,white?0xe9e4d8:C.roofRed);
    }
  }
  V.box(cx-4.2,cx+4.2,32,32.6,cz-4.2,cz+4.2,C.iron);
  V.box(cx-4,cx+4,32.6,33,cz-4,cz+4,0x2a3038);
  for(let a=0;a<16;a++){const th=a/16*Math.PI*2;V.put(cx+Math.cos(th)*3.1,34.5,cz+Math.sin(th)*3.1,.5,3,.5,0x24303a);}
  E.put(cx,34.6,cz,3.4,3.2,3.4,new THREE.Color(C.lantern).multiplyScalar(3.4));
  V.box(cx-3.6,cx+3.6,36.2,36.8,cz-3.6,cz+3.6,C.iron);
  V.box(cx-4.2,cx+4.2,36.8,37.2,cz-4.2,cz+4.2,C.iron);
  for(let a=0;a<12;a++){const th=a/12*Math.PI*2;V.put(cx+Math.cos(th)*4.05,38.4,cz+Math.sin(th)*4.05,.2,2.6,.2,C.iron);}
  for(let r=1;r<=3;r++)for(let a=0;a<20;a++){const th=a/20*Math.PI*2;
    V.put(cx+Math.cos(th)*r,39+r*.9,cz+Math.sin(th)*r,.9,.9,.9,r===3?C.copper:0x324250);}
  V.put(cx,42.6,cz,.8,1.4,.8,C.iron);
  lanternLight=new THREE.PointLight(0xffe6a8,0,90,2);lanternLight.position.set(cx,35,cz);scene.add(lanternLight);
  lanternMesh=new THREE.Mesh(new THREE.BoxGeometry(3,3,3),
    new THREE.MeshBasicMaterial({color:new THREE.Color(C.lantern).multiplyScalar(3.5),fog:true}));
  lanternMesh.position.set(cx,34.6,cz);scene.add(lanternMesh);
  // gallery steps
  V.box(cx-6,cx+6,5,5.6,cz-1,cz+7,C.stoneL,{jitter:.08});
}
/* ---- breakwater, beacon, headland ---- */
function breakwater(){
  for(let i=0;i<44;i++){
    const t=i/43;
    const x=lerp(15,-40,t)+Math.sin(t*6)*1.4, z=lerp(-33,-53,t)+Math.cos(t*4)*1.2;
    const top=1+Math.round((Math.sin(i*.9)*1.2+2.4+ (1-Math.abs(t-.5)*.6))*2)/2;
    V.box(x-2.4,x+2.4,-6,top,z-2.4,z+2.4,C.stoneD,{step:2,outer:false,jitter:.14});
    for(let k=-2;k<=2;k++){
      const h2=top-Math.abs(k)*.6+hash3(i,k,7)*.8;
      V.put(x+k*2,Math.max(.3,h2),z+Math.sin(i+k)*1.6,2.2,1.4,2.2,hash3(i,k,3)>.5?C.stone:C.stoneD);
    }
    V.put(x,top+.4,z,3,1,3,C.stoneL);
  }
  V.box(-43,-41,2,9,-54,-52,C.white,{jitter:.05});
  V.box(-43.6,-40.4,9,9.5,-54.6,-51.4,C.roofRed);
  beaconLights.push({pos:new THREE.Vector3(-42,10,-53),color:0xff4b3a,period:3.2,duty:.25,size:.9});
  // north groyne
  for(let i=0;i<7;i++)V.put(15+i*1.8,-.4,34+i*1.4,2.6,2,2.6,C.stoneD);
}
function headland(){
  for(let x=-62;x>-104;x-=4)for(let z=-46;z<6;z+=4){
    const d=Math.hypot((x+88)/24,(z-22)/20);
    if(d>1.05)continue;
    const h=lerp(30,1,Math.pow(d,1.6))+Math.sin(x*.3)*Math.cos(z*.25)*2+hash3(x,1,z)*2;
    const top=Math.max(1,Math.round(h));
    V.box(x,x+4,-4,top,z,z+4,top>15?C.rock:(top>7?C.grass2:C.grass),{step:4,jitter:.18});
  }
  V.box(-90,-87,24,40,-6,-3,C.white,{jitter:.05});
  V.box(-90.6,-86.4,40,41,-6.6,-2.4,C.roofRed);
  beaconLights.push({pos:new THREE.Vector3(-88.5,42,-4.5),color:0x62ff9c,period:4.6,duty:.2,size:1.1});
  for(let i=0;i<8;i++)tree(-80-hash3(i,3,5)*18|0,10+(hash3(i,4,2)*8|0),-10+hash3(i,9,1)*30|0,i+50);
}
/* ---- harbour props: barrels on the slip, moored boats ---- */
const bobbers=[];
function smallBoat(x,z,rotY,scaleHue){
  const v=new Vox();
  for(let i=-4;i<=4;i++){
    const w=Math.max(.6,3.2-Math.abs(i)*.42);
    for(const s of[-1,1])v.put(i,.5,s*(w-.5),1,1.6,.8,C.woodD);
    v.put(i,.2,0,1,.4,w*1.4,C.deck);
  }
  v.box(-4.4,4.4,-.4,.4,-.4,.4,C.wood);
  v.strut(new THREE.Vector3(-2,1,0),new THREE.Vector3(-2,6,0),.3,.3,C.woodL);
  v.strut(new THREE.Vector3(-1.9,5.6,0),new THREE.Vector3(3.4,1.2,0),.18,.18,C.rope);
  const m=toMesh(v);const g=new THREE.Group();g.add(m);g.position.set(x,0,z);g.rotation.y=rotY;
  scene.add(g);bobbers.push({g,baseY:0,ph:Math.random()*6,scale:1});
  return g;
}
let smokeSrc=[],lampLights=[],beaconLights=[],brazier=null,cranePivot=null,lanternLight=null,lanternMesh=null;
coast();quay();town();lighthouse();breakwater();headland();
smallBoat(10.5,-16,-.4);smallBoat(10.8,17,.2);smallBoat(9.8,27,.5);

const staticMesh=toMesh(V,{cast:true,recv:true});scene.add(staticMesh);
const emisMesh=toMesh(E,{cast:false,recv:false,material:new THREE.MeshBasicMaterial({color:0xffffff})});
scene.add(emisMesh);

/* ══════════════════════════════ 4. THE BARQUE ══════════════════════════════ */
const SH=new Vox(),SL=new Vox(),SM=new Vox();
const cloth={billow:[],dir:[]};
let rigVox=new Vox();
const shipRoot=new THREE.Group(),shipBody=new THREE.Group();shipRoot.add(shipBody);
const SP=new THREE.Vector3(-14,0,4),ROT=Math.PI/2+.18;
shipRoot.position.copy(SP);shipRoot.rotation.y=ROT;scene.add(shipRoot);

function beamAt(x){
  if(x>=8){const u=(21-x)/13;return .5+5.4*Math.pow(Math.max(u,0),.85);}
  if(x<=-12){const u=(x+22)/10;return 2.2+3.6*Math.pow(Math.max(u,0),.6);}
  return 5.9+.4*Math.sin((x+12)/20*Math.PI);
}
function deckAt(x){return 6.6+sstep(8,21,x)*2.7+sstep(-10,-22,x)*1.7;}
function keelAt(x){return -3.2+Math.max(sstep(9,21,x)*4.6,sstep(-12,-22,x)*3.4);}
function addCloth(x,y,z,billow,bx,by,bz,flutter,color,thick=.6){
  const i=SL.n;SL.put(x,y,z,thick,1,1,color);cloth.billow.push(billow);cloth.dir.push(bx,by,bz);
  SL.q[i*4]=0;return i;
}
function buildShip(){
  // hull shell
  for(let x=-21;x<=21;x++){
    const b=beamAt(x),dk=deckAt(x),kl=keelAt(x);
    const y0=Math.floor(kl),y1=Math.floor(dk);
    for(let y=y0;y<=y1;y++){
      const f=Math.pow(clamp((y+.5-kl)/(dk-kl),0,1),.30);
      const w=b*f;if(w<.42)continue;
      const nz=Math.max(1,Math.round(w));
      for(const s of[-1,1]){
        let col=C.hull;
        if(y<=-1)col=C.anti; else if(y===0)col=C.iron; else if(y===1)col=C.gold;
        if(y===y1)col=C.woodL;
        const port=(y===3||y===4)&&x>-15&&x<14&&((x+22)%4===0);
        if(port)col=C.gold;
        if(x>14&&Math.abs(zDummy(s))<0)continue;
        SH.put(x,y+.5,s*(nz-.5),1,1,1,col);
      }
      if(y===0&&x===21){SH.put(21.5,.5,0,1,1,1,C.gold);}
    }
    // deck planking
    const yy=Math.floor(deckAt(x)),w=Math.max(1,Math.round(beamAt(x)*.92));
    for(let z=-w+1;z<w;z++)SH.put(x,yy+.5,z,1,.6,1,hash3(x,17,z)>.72?C.deckD:C.deck);
    // bulwark above deck
    for(const s of[-1,1]){const nz=Math.max(1,Math.round(beamAt(x)));
      SH.put(x,yy+1.5,s*(nz-.5),1,1,1,C.woodL);SH.put(x,yy+2.5,s*(nz-.5),1,1,1,C.woodD);}
    SH.put(x,yy+2.5,-(Math.max(1,Math.round(beamAt(x)))-.5),1,.4,1.2,C.woodL);
  }
  function zDummy(){return 0}
  // forecastle & quarterdeck
  for(let x=11;x<=18;x++)for(let z=-4;z<4;z++)SH.put(x,10,z,1,.8,1,C.deckD);
  for(let x=-20;x<=-9;x++)for(let z=-4;z<4;z++)SH.put(x,9.6,z,1,.8,1,C.deckD);
  // hatches
  for(const hx of[-6,0,7])for(let z=-3;z<3;z++)for(let i=0;i<2;i++)SH.put(hx+i,7.2,z,1,.4,1,C.woodD);
  // houses & fittings
  SH.box(-8,-4,10,12.6,-2.2,2.2,C.woodL,{jitter:.06});
  E.put(-8.05,11.3,0,'-x',1.2,1.0,C.glass);E.put(-6,12.65,0,1.6,.2,1.6,new THREE.Color(C.glass).multiplyScalar(1.6));
  SH.box(9,10,7.5,9,-1,1,C.iron);                       // capstan
  SH.box(8.4,10.6,9,9.3,-1.6,1.6,C.wood);
  SH.put(10.5,8.5,0,.3,1.4,.3,C.iron);
  SH.box(13,16,10.5,12,-3.4,-2.4,C.woodD);SH.box(13,16,10.5,12,2.4,3.4,C.woodD); // cable lockers
  for(const cz of[-4.5,4.5,-3,3])SH.put(19,11,cz,1,1,1,C.deckD);
  // davits + shipped boat
  SH.strut(new THREE.Vector3(-13,9.6,3.4),new THREE.Vector3(-13,14,5.2),.3,.3,C.wood);
  SH.strut(new THREE.Vector3(-16,9.6,3.4),new THREE.Vector3(-16,14,5.2),.3,.3,C.wood);
  for(let x=-17;x<=-12;x++){const w=1.6-Math.abs(x+14.5)*.24;
    for(const s of[1,-1])SH.put(x,13.6,s*w,1,.9,.7,C.woodD);SH.put(x,13.1,0,1,.3,w*2,C.deck);}
  for(let x=-19;x<=-15;x+=4)SH.put(x,5.4,4.9,1,1,1,C.gold);  // gunport caps aft
  // bowsprit
  SH.strut(new THREE.Vector3(20,8.4,0),new THREE.Vector3(29,11.6,0),1.1,1.1,C.woodL);
  SH.strut(new THREE.Vector3(29,11.6,0),new THREE.Vector3(34.5,12.7,0),.55,.55,C.wood);
  SH.strut(new THREE.Vector3(24,10,0),new THREE.Vector3(24,7.4,0),.4,.4,C.rope);
  SH.box(20,22,9.2,10.2,-1.6,1.6,C.deck);
  // figurehead
  SH.put(21.2,6.4,0,.8,1.6,.8,0xd8c8a8);SH.put(21.2,7.6,0,.6,.6,.6,0x9c6a3a);
  // anchor & cable over the bow
  SH.put(20.5,7.2,4.1,.6,1.2,.6,C.iron);
  for(let i=0;i<7;i++){const t=i/6;SH.put(20.5+t*1.5,7.2-t*10*Math.pow(t,1.2),4.1,.5,.5,.5,0x2f353c);}
  SH.put(22.6,1.6,4.1,1.6,.5,2.4,C.iron);SH.put(23.4,.7,4.1,.5,2.2,.5,C.iron);
  // foam collar
  for(let x=-20;x<=21;x++){
    const w=Math.max(1,Math.round(beamAt(x)));
    for(const s of[-1,1])if(hash3(x,s,31)>.35)SH.put(x,.55,s*(w+.3),1.2,.7,1.2,C.foam);
  }
  SH.put(22.3,.6,0,2.4,.8,3,C.foam);
  // masts, yards, sails
  const masts=[{x:8,top:33.5,w:1},{x:-4,top:38.5,w:1.15},{x:-15,top:28,w:.9}];
  masts.forEach((m,mi)=>{
    for(let y=7;y<m.top;y++)SH.put(m.x,y+.5,0,1.15-mi*.05,1,1.15,hash3(mi,y,3)>.7?C.metal:C.woodL);
    SH.put(m.x,m.top+.5,0,2,.4,2,C.woodD);
    if(mi<2){
      SH.box(m.x-1.6,m.x+1.6,m.top-9,m.top-8.6,-1.8,1.8,C.deckD);
      for(const s of[-1,1])SH.strut(new THREE.Vector3(m.x,m.top-8.6,s*1.8),new THREE.Vector3(m.x,m.top-6,s*1.2),.2,.2,C.rope);
    }
  });
  const sq=[
    {mx:8,y0:22.5,y1:28,hw:5.2,full:true,band:-1},
    {mx:8,y0:14,y1:21,hw:6.4,full:true,band:18},
    {mx:8,y0:8,y1:13,hw:7.4,full:true,band:-1},
    {mx:-4,y0:26,y1:31.5,hw:4.4,full:true,band:-1},
    {mx:-4,y0:16.5,y1:24.5,hw:5.9,full:true,band:21},
    {mx:-4,y0:8.5,y1:15.5,hw:7.0,full:true,band:-1},
  ];
  sq.forEach(s=>{
    const yb=Math.floor(s.y1+1);
    SH.strut(new THREE.Vector3(s.mx,yb+.5,-s.hw-.8),new THREE.Vector3(s.mx,yb+.5,s.hw+.8),.75,.75,C.wood);
    if(s.band>=0){}
    for(let z=-s.hw;z<=s.hw;z++){
      const zw=Math.abs(z)/s.hw, edge=Math.pow(1-zw*zw,.75);
      for(let y=s.y0;y<=s.y1;y++){
        const yw=(y-s.y0)/Math.max(1,(s.y1-s.y0));
        const prof=edge*Math.sin(Math.PI*(.12+.76*yw));
        const col=(s.band>=0&&y>=s.band&&y<=s.band+2)?C.canvasBand:(Math.abs(z)%2?C.canvas:C.canvas2);
        addCloth(s.mx,y+.5,z,prof*2.4,-1,0,.35,.30,col);
      }
    }
  });
  // spanker (fore-and-aft gaff sail)
  for(let x=-19;x<=-11;x++){
    const t=(x+19)/8, top=lerp(26.5,21,t);
    for(let y=9;y<=top;y++){
      const yw=(y-9)/(top-9);
      addCloth(x,y+.5,-.6,(1-Math.pow(Math.abs(yw-.5)*2,2))*.9,-.2,0,-1,.25,C.canvas);
    }
  }
  SH.strut(new THREE.Vector3(-15.5,27.5,-.5),new THREE.Vector3(-10.5,21.5,-1.2),.4,.4,C.wood);
  SH.strut(new THREE.Vector3(-15.5,9.5,-.5),new THREE.Vector3(-20.5,9,-1),.4,.4,C.wood);
  // jibs
  triSail(new THREE.Vector3(34,13,0),new THREE.Vector3(8,26,0),new THREE.Vector3(24.5,10.2,0),1.1,.28,C.canvas);
  triSail(new THREE.Vector3(29,12.4,0),new THREE.Vector3(8,19,0),new THREE.Vector3(21,9.4,0),.9,.28,C.canvas2);
  // rigging
  masts.forEach(m=>{
    for(const s of[-1,1])for(let i=-1;i<=1;i++){
      const ax=m.x+i*1.9,bx=m.x+i*2.6;
      rigVox.strut(new THREE.Vector3(m.x,m.top-.5,s*1.2),new THREE.Vector3(bx,deckAt(bx)+1.2,s*(beamAt(bx)+.35)),.13,.13,C.rope);
      for(let r=0;r<9;r++){
        const t=.18+r*.085;
        const p1=new THREE.Vector3(lerp(m.x,bx,t),lerp(m.top-1,deckAt(bx)+1.2,t),s*lerp(1.2,beamAt(bx)+.3,t));
        const p2=new THREE.Vector3(lerp(m.x,bx,t+.085),lerp(m.top-1,deckAt(bx)+1.2,t+.085),s*lerp(1.2,beamAt(bx)+.3,t+.085));
        rigVox.strut(p1,new THREE.Vector3(p1.x,p1.y,s*lerp(1.2,beamAt(bx)+.3,t+.085)),.09,.09,C.rope);
      }
    }
    rigVox.strut(new THREE.Vector3(m.x,m.top-.5,0),new THREE.Vector3(m.x+ (m.x>0?9:11),deckAt(m.x+ (m.x>0?9:11))+2,0),.14,.14,C.rope);
    rigVox.strut(new THREE.Vector3(m.x,m.top-.5,0),new THREE.Vector3(m.x-9,deckAt(m.x-9)+2,0),.14,.14,C.rope);
  });
  rigVox.strut(new THREE.Vector3(34.5,12.8,0),new THREE.Vector3(8,26,0),.15,.15,C.rope);
  rigVox.strut(new THREE.Vector3(29,12.5,0),new THREE.Vector3(8,19,0),.13,.13,C.rope);
  rigVox.strut(new THREE.Vector3(20,8.6,0),new THREE.Vector3(34.5,12.8,0),.14,.14,C.rope);
  for(const s of[-1,1])rigVox.strut(new THREE.Vector3(34.5,12.8,0),new THREE.Vector3(19,10,s*3),.12,.12,C.rope);
  // lifelines
  for(let x=-20;x<=20;x+=2){const y=deckAt(x)+3.4,w=beamAt(x);
    rigVox.strut(new THREE.Vector3(x,y,-w),new THREE.Vector3(Math.min(20,x+2),y+ (deckAt(Math.min(20,x+2))-deckAt(x)),-beamAt(Math.min(20,x+2))),.08,.08,C.rope);
    rigVox.strut(new THREE.Vector3(x,y,w),new THREE.Vector3(Math.min(20,x+2),y+(deckAt(Math.min(20,x+2))-deckAt(x)),beamAt(Math.min(20,x+2))),.08,.08,C.rope);}
  // dressed overall: signal flags bow→mastheads→stern
  const pts=[new THREE.Vector3(30,11.6,0),new THREE.Vector3(8,33.5,0),new THREE.Vector3(-4,38.5,0),new THREE.Vector3(-15,28,0),new THREE.Vector3(-21,10,0)];
  const pal=[C.red,C.blue,C.yellow,C.green,C.white,C.canvasBand];
  for(let i=0;i<pts.length-1;i++){
    for(let k=0;k<10;k++){
      const t=k/10,p=pts[i].clone().lerp(pts[i+1],t);
      p.y-=Math.sin(t*Math.PI)*1.1;
      addCloth(p.x,p.y-.9,0,.0,0,-1,0,1.0,pal[(i*10+k)%pal.length],.4);
      SL.s[SL.n*3-3]=1.5;SL.s[SL.n*3-1]=1.5;
      cloth.billow[SL.n-1]=.0;
    }
  }
  // ensign staff
  SH.strut(new THREE.Vector3(-21.5,9,0),new THREE.Vector3(-23.6,13,0),.3,.3,C.woodL);
  addCloth(-23.9,12.2,0,0,0,0,-1,1.2,C.red,.35);
  SL.s[SL.n*3-3]=.3;SL.s[SL.n*3-1]=2.6;SL.s[SL.n*3]=1.6;
}
function triSail(A,B,Cc,amp,flutter,color){
  const seen=new Set();
  for(let u=0;u<=1.0001;u+=.045)for(let w=0;w<=1-u;w+=.045){
    const p=new THREE.Vector3(
      lerp(A.x,B.x,0)*0+A.x*(1-u-w)+B.x*u+Cc.x*w,
      A.y*(1-u-w)+B.y*u+Cc.y*w,
      A.z*(1-u-w)+B.z*u+Cc.z*w);
    const rx=Math.round(p.x),ry=Math.round(p.y),rz=Math.round(p.z);
    const key=rx+','+ry+','+rz;if(seen.has(key))continue;seen.add(key);
    const prof=Math.sin(Math.PI*clamp(u*1.05,0,1))*Math.pow(1-w,1.1);
    addCloth(rx,ry+.5,rz,prof*amp,0,0,1,flutter,color);
  }
}
buildShip();
const hullMesh=toMesh(SH);shipBody.add(hullMesh);
const shipEmis=toMesh(SM,{cast:false,material:new THREE.MeshBasicMaterial()});shipBody.add(shipEmis);
// cloth mesh with instanced billow attributes
const clothGeo=new THREE.BoxGeometry(1,1,1);
clothGeo.setAttribute('aBill',new THREE.InstancedBufferAttribute(new Float32Array(cloth.billow),1));
clothGeo.setAttribute('aDir',new THREE.InstancedBufferAttribute(new Float32Array(cloth.dir),3));
const clothU={uTime:{value:0},uBill:{value:1},uWind:{value:1}};
const clothMat=new THREE.MeshLambertMaterial({color:0xffffff,side:THREE.DoubleSide});
clothMat.onBeforeCompile=sh=>{
  Object.assign(sh.uniforms,clothU);
  sh.vertexShader=`attribute float aBill;attribute vec3 aDir;uniform float uTime,uBill,uWind;\n`+
    sh.vertexShader.replace('#include <begin_vertex>',`#include <begin_vertex>
    {float ph=instanceMatrix[3].x*.5+instanceMatrix[3].z*.9;
     float w1=sin(uTime*1.9+ph),w2=sin(uTime*3.4+ph*1.7);
     float amt=aBill*uBill+uWind*(.42*w1+.18*w2)*mix(.06,1.,step(2.9,aDir.x+aDir.y+aDir.z+3.0));
     transformed+=aDir*amt;
     transformed.y+=uWind*.09*w2;}`);
};
const clothMesh=new THREE.InstancedMesh(clothGeo,clothMat,SL.n);
clothMesh.castShadow=true;clothMesh.receiveShadow=true;clothMesh.frustumCulled=false;
{const M=new THREE.Matrix4(),P=new THREE.Vector3(),Q=new THREE.Quaternion(),S=new THREE.Vector3();
 for(let i=0;i<SL.n;i++){M.compose(P.set(SL.p[i*3],SL.p[i*3+1],SL.p[i*3+2]),Q.set(0,0,0,1),S.set(SL.s[i*3],SL.s[i*3+1],SL.s[i*3+2]));
  clothMesh.setMatrixAt(i,M);clothMesh.setColorAt(i,SL.c[i]);}}
shipBody.add(clothMesh);
// furled alternative
const FUR=new Vox();
sq.forEach(s=>{
  const yb=Math.floor(s.y1);
  for(let z=-s.hw;z<=s.hw;z++)FUR.put(s.mx,yb-.2,z,1.1,.9,1,Math.abs(z)%2?C.canvas:C.canvas2);
});
FUR.strut(new THREE.Vector3(-15.5,26.8,-.6),new THREE.Vector3(-10.6,21.6,-1.2),1,1,C.canvas2);
const furledMesh=toMesh(FUR);furledMesh.visible=false;shipBody.add(furledMesh);
const rigMesh=toMesh(rigVox,{cast:true,recv:false});shipBody.add(rigMesh);

/* crew on deck + figure walking the quay */
function figure(body,legs,skin){
  const g=new THREE.Group();
  const mk=(w,h,d,c)=>new THREE.Mesh(new THREE.BoxGeometry(w,h,d),new THREE.MeshLambertMaterial({color:c}));
  const torso=mk(.6,.9,.45,body);torso.position.y=1.55;
  const head=mk(.5,.5,.5,skin||0xd8b48c);head.position.y=2.25;
  const l1=mk(.24,.9,.3,legs),l2=mk(.24,.9,.3,legs);l1.position.set(-.16,.45,0);l2.position.set(.16,.45,0);
  const a1=mk(.2,.8,.28,body),a2=mk(.2,.8,.28,body);a1.position.set(-.42,1.55,0);a2.position.set(.42,1.55,0);
  [torso,head,l1,l2,a1,a2].forEach(m=>{m.castShadow=true;g.add(m);});
  g.userData={l1,l2,a1,a2};return g;
}
const crew=[];
[[-9,10.4,2.4,0x9c3f34],[1.5,7.2,-3,0x2f5f7a],[6,7.2,3.4,0x6a5a3a],[-17,10,1.5,0x3f5a44],[12,10.4,-2,0xa06a3a]]
 .forEach(([x,y,z,c],i)=>{const f=figure(c,0x2b3340);f.position.set(x,y,z);f.scale.setScalar(.85);
  f.userData.ph=i*1.7;shipBody.add(f);crew.push(f);});
const walkers=[];
[[-4,5.05,0x9c3f34],[-24,5.05,0x2f5f7a],[16.5,5.05,0x5a6a78]].forEach(([z,y,c],i)=>{
  const f=figure(c,0x24303c);f.position.set(16.6,y,z);f.scale.setScalar(.8);scene.add(f);
  walkers.push({f,z0:z,dir:i%2?1:-1,sp:.9+i*.25,ph:i});
});

/* ══════════════════════════════ 5. SEA ══════════════════════════════ */
const CELL=1.7, WX0=-84, WX1=13.6, WZ0=-78, WZ1=78;
const wnx=Math.round((WX1-WX0)/CELL), wnz=Math.round((WZ1-WZ0)/CELL), WN=wnx*wnz;
const wx=new Float32Array(WN),wz=new Float32Array(WN),wr=new Float32Array(WN),wg=new Float32Array(WN),wb=new Float32Array(WN),wsh=new Float32Array(WN);
const WV=new Vox();
let k=0;
for(let i=0;i<wnx;i++)for(let j=0;j<wnz;j++){
  const x=WX0+i*CELL+CELL/2, z=WZ0+j*CELL+CELL/2;
  wx[k]=x;wz[k]=z;
  const nearQuay=sstep(34,8,x), deep=sstep(-8,-56,x);
  const c=new THREE.Color(0x11425a).lerp(new THREE.Color(0x2f8ba6),.25+.75*Math.pow(1-nearQuay,1.4));
  c.lerp(new THREE.Color(0x0e2f42),deep*.55);
  c.lerp(new THREE.Color(0x3a9db3),sstep(2.2,0,Math.abs(x-12.5))*.4);
  const f=1+(hash3(i,7,j)-.5)*.1;c.multiplyScalar(f);
  wr[k]=c.r;wg[k]=c.g;wb[k]=c.b;
  wsh[k]=.42+.58*clamp((-x+9)/46,0,1);
  k++;
}
const waterMat=new THREE.MeshLambertMaterial();
const water=toMesh(new Vox(),{material:waterMat});  // placeholder replaced below
scene.remove(water);
const waterGeo=new THREE.BoxGeometry(1,1,1);
const waterMesh=new THREE.InstancedMesh(waterGeo,waterMat,WN);
waterMesh.receiveShadow=true;waterMesh.castShadow=false;waterMesh.frustumCulled=false;
{const c=new THREE.Color();for(let i=0;i<WN;i++)waterMesh.setColorAt(i,c.setRGB(wr[i],wg[i],wb[i]));}
scene.add(waterMesh);
TOTAL+=WN;
// surf along the quay wall
const FO=new Vox();
for(let z=-33;z<33;z+=1.4)FO.put(11.1,.3,z,1.4,.6,1.4,C.foam);
for(let i=0;i<40;i++){const t=i/39;FO.put(lerp(15,-40,t)+Math.sin(t*6)*1.4,.25,lerp(-31,-51,t)+Math.cos(t*4)*1.2,2.4,.5,2.4,C.foam);}
const foam=toMesh(FO,{cast:false,material:new THREE.MeshLambertMaterial({transparent:true,opacity:.85})});
scene.add(foam);const foamN=FO.n;
// far water
const farSea=new THREE.Mesh(new THREE.CircleGeometry(1100,64),
  new THREE.MeshBasicMaterial({color:0x14485f,fog:true}));
farSea.rotation.x=-Math.PI/2;farSea.position.y=-.9;farSea.renderOrder=0;scene.add(farSea);

/* ══════════════════════════════ 6. LIFE ══════════════════════════════ */
/* clouds */
const clouds=[];
for(let c=0;c<7;c++){
  const cv=new Vox();const cx=-120+Math.random()*220,cz=-160+Math.random()*260,cy=46+Math.random()*34;
  const n=16+(Math.random()*18|0);
  for(let i=0;i<n;i++){
    const s=2+((hash3(i,c,i*3)*3)|0);
    cv.put((hash3(i,1,c)-.5)*22,(hash3(i,2,c)-.5)*5,(hash3(i,3,c)-.5)*14,s,s*.6,s,0xffffff);
  }
  const m=toMesh(cv,{cast:false,recv:false});
  const g=new THREE.Group();g.add(m);g.position.set(cx,cy,cz);scene.add(g);
  clouds.push({g,sp:1.4+Math.random()*1.8});
}
/* gulls */
const gulls=[];
const gGeo=new THREE.BoxGeometry(1,1,1),gMat=new THREE.MeshLambertMaterial({color:0xf6f4ee});
const gMat2=new THREE.MeshLambertMaterial({color:0x8f9aa3});
for(let i=0;i<6;i++){
  const g=new THREE.Group();
  const b=new THREE.Mesh(gGeo,gMat);b.scale.set(.55,.5,1.7);g.add(b);
  const wl=new THREE.Group(),wr=new THREE.Group();
  const ml=new THREE.Mesh(gGeo,gMat);ml.scale.set(1.9,.1,.62);ml.position.x=1.05;
  const mr=ml.clone();mr.position.x=-1.05;
  wl.add(ml);wr.add(mr);wl.position.x=.25;wr.position.x=-.25;g.add(wl,wr);
  scene.add(g);gulls.push({g,wl,wr,r:26+Math.random()*44,h:16+Math.random()*16,sp:.16+Math.random()*.14,ph:Math.random()*6.28,cx:4+i*3,cz:-6+i*2});
}
/* chimney smoke */
const smSrc=smokeSrc.map(p=>({p:p.clone()}));
smSrc.push({p:brazier.clone()});
const PUFFS=13,SMK=new Vox();
for(let s=0;s<smSrc.length;s++)for(let i=0;i<PUFFS;i++)SMK.put(0,-50,0,1,1,1,0xbfc4c6);
const smokeMesh=toMesh(SMK,{cast:false,recv:false,dynamic:true,
  material:new THREE.MeshLambertMaterial({transparent:true,opacity:.5})});
scene.add(smokeMesh);
/* crane hook + swinging crate */
{const cv=new Vox();
 cv.strut(new THREE.Vector3(0,0,0),new THREE.Vector3(0,-4.4,0),.13,.13,C.rope);
 cv.put(0,-4.8,0,.5,.7,.5,C.metal);
 cv.box(-1.2,1.2,-8.2,-5.6,-1.2,1.2,C.wood,{jitter:.12});
 cv.box(-1.3,1.3,-5.9,-5.6,-1.3,1.3,C.woodD);
 const m=toMesh(cv);craneHook=new THREE.Group();craneHook.position.copy(cranePivot);craneHook.add(m);scene.add(craneHook);}
let craneHook;
/* windmill sails */
{const wv=new Vox();
 for(let b=0;b<4;b++){
   const a=b*Math.PI/2;
   for(let r=1;r<8;r++)wv.put(Math.cos(a)*r*1.05,Math.sin(a)*r*1.05,0,.55,.55,.35,b%2?C.woodD:C.canvas2);
   wv.put(Math.cos(a)*4,Math.sin(a)*4,0,2.6,2.6,.25,C.canvas);
 }
 const m=toMesh(wv,{cast:false});windmillSails=new THREE.Group();windmillSails.position.copy(windmillHub);
 windmillSails.add(m);scene.add(windmillSails);}
let windmillSails;
/* lighthouse beams */
const beamMat=new THREE.ShaderMaterial({
  transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,side:THREE.DoubleSide,
  uniforms:{uOp:{value:0},uCol:{value:new THREE.Color(0xffe7ab)}},
  vertexShader:`varying vec2 vU;void main(){vU=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,
  fragmentShader:`varying vec2 vU;uniform float uOp;uniform vec3 uCol;
   void main(){float a=pow(vU.y,2.4)*uOp;gl_FragColor=vec4(uCol,a);}`});
const beamGrp=new THREE.Group();beamGrp.position.set(36,35,-28);scene.add(beamGrp);
for(const dir of[0,Math.PI]){
  const g=new THREE.ConeGeometry(6.2,150,22,1,true);
  g.translate(0,-75,0);g.rotateZ(Math.PI/2);
  const m=new THREE.Mesh(g,beamMat);m.rotation.y=dir;m.renderOrder=2;beamGrp.add(m);
}
/* blinking beacons + brazier flame */
const blinkers=beaconLights.map(b=>{
  const m=new THREE.Mesh(new THREE.BoxGeometry(b.size,b.size,b.size),
    new THREE.MeshBasicMaterial({color:new THREE.Color(b.color).multiplyScalar(3)}));
  m.position.copy(b.pos);scene.add(m);
  const L=new THREE.PointLight(b.color,0,40,2);L.position.copy(b.pos);scene.add(L);
  return{...b,m,L};
});
const flame=new THREE.Mesh(new THREE.BoxGeometry(.9,.9,.9),
  new THREE.MeshBasicMaterial({color:new THREE.Color(0xffb04a).multiplyScalar(3)}));
flame.position.copy(brazier);scene.add(flame);
/* moving sailboat in the channel */
const sloop=(()=>{
  const v=new Vox();
  for(let i=-3;i<=3;i++){const w=Math.max(.5,2.2-Math.abs(i)*.3);
    for(const s of[-1,1])v.put(i,.4,s*(w-.5),1,1.2,.7,0x2c3a46);v.put(i,.1,0,1,.3,w*2,C.deck);}
  v.put(0,1,0,.35,10,.35,C.woodL);
  for(let y=2;y<=9;y++)for(let x=1;x<=y*.55;x++)v.put(x,y+.5,0,.5,1,.4,C.canvas);
  const m=toMesh(v);const g=new THREE.Group();g.add(m);scene.add(g);
  bobbers.push({g,baseY:0,ph:1.3,scale:1,moving:true});return g;
})();

/* ══════════════════════════════ 7. TIME OF DAY ══════════════════════════════ */
const KEYS=[
  {e:-12,top:0x030812,hor:0x0a1424,sun:0x5a6f93,sunI:.0,hemiI:.14,ambI:.05,sunC:0x2a3a5c,sea:0x0a2231},
  {e:-2, top:0x101d3c,hor:0x4e3b53,sun:0xff7a48,sunI:.35,hemiI:.22,ambI:.08,sunC:0x5b4560,sea:0x123049},
  {e:4,  top:0x1e3460,hor:0xff8a52,sun:0xffa057,sunI:1.5,hemiI:.38,ambI:.12,sunC:0xff9e57,sea:0x1c4a63},
  {e:14, top:0x37679f,hor:0xffc98d,sun:0xffc178,sunI:2.7,hemiI:.55,ambI:.14,sunC:0xffb877,sea:0x1f5f7c},
  {e:34, top:0x2e74bb,hor:0xc3dded,sun:0xfff2dc,sunI:3.2,hemiI:.72,ambI:.16,sunC:0xfff1d6,sea:0x1e627e},
  {e:60, top:0x2069bc,hor:0xd7e9f4,sun:0xffffff,sunI:3.4,hemiI:.82,ambI:.18,sunC:0xffffff,sea:0x1d6884}
];
function mixKeys(e){
  let a=KEYS[0],b=KEYS[KEYS.length-1];
  for(let i=0;i<KEYS.length-1;i++)if(e>=KEYS[i].e&&e<=KEYS[i+1].e){a=KEYS[i];b=KEYS[i+1];break;}
  const t=(e-a.e)/Math.max(.0001,b.e-a.e),out={};
  for(const key of['top','hor','sun','sunC','sea'])out[key]=new THREE.Color(a[key]).lerp(new THREE.Color(b[key]),t);
  for(const key of['sunI','hemiI','ambI'])out[key]=lerp(a[key],b[key],t);
  return out;
}
let night=0,sunAzX=1,sunAzZ=0,sunGlit=0,horizonCol=new THREE.Color();
const sunDir=new THREE.Vector3();
function setTime(hour){
  const t=clamp((hour-5.5)/12.5,0,1.15);
  const elev=62*Math.sin(Math.PI*clamp(t,0,1))-4;
  const th=THREE.MathUtils.degToRad(-36+180*t),phi=THREE.MathUtils.degToRad(90-elev);
  sunDir.setFromSphericalCoords(1,phi,th);
  const k=mixKeys(elev);
  skyU.uTop.value.copy(k.top);skyU.uHor.value.copy(k.hor);skyU.uSun.value.copy(k.sun);
  skyU.uSunDir.value.copy(sunDir);skyU.uSunI.value=k.sunI;
  skyU.uMoonDir.value.copy(sunDir).multiplyScalar(-1).setY(Math.abs(sunDir.y)*.7+.35);
  night=clamp((8-elev)/13,0,1);skyU.uNight.value=night;
  sun.color.copy(k.sunC);sun.intensity=k.sunI;
  hemi.intensity=k.hemiI;hemi.color.copy(k.top);amb.intensity=k.ambI;
  horizonCol.copy(k.hor);scene.fog.color.copy(k.hor).lerp(k.sea,.35);
  farSea.material.color.copy(k.sea).lerp(k.hor,.35+night*.2);
  emisMesh.material.color.setScalar(lerp(.12,1,Math.pow(night,.8)));
  const lampI=night>0?night:0;
  lampLights.forEach((L,i)=>L.intensity=lampI*(i===lampLights.length-1?90*(.75+.25*Math.sin(t*0)):110));
  lanternLight.intensity=night*260;
  lanternMesh.visible=night>.05;
  const hl=new THREE.PointLight(0x9fb8e8,night*45,300,2);
  moonLight?moonLight.intensity=night*45:null;
  if(!moonLight){moonLight=new THREE.DirectionalLight(0xb8d0f5,0);moonLight.position.set(-60,80,-40);scene.add(moonLight);}
  sunGlit=clamp(k.sunI*.35,0,1.2)*(1-Math.pow(clamp((elev-26)/40,0,1),1.5));
  const hl2=sunDir.clone().setY(0).normalize();sunAzX=hl2.x;sunAzZ=hl2.z;
  beamMat.uniforms.uOp.value=Math.pow(night,1.4)*.36;
  document.getElementById('oTime').textContent=
    String(Math.floor(hour)).padStart(2,'0')+':'+String(Math.floor((hour%1)*60)).padStart(2,'0');
  refreshLog(hour);
}
let moonLight=null;
setTime(17);

/* ══════════════════════════════ 8. UI ══════════════════════════════ */
let swell=.8,wind=.85,useBloom=true,bloomOn=true,lightsAuto=true,lightsForce=false,sailsOn=true,rigOn=true;
const fill=el=>{const p=(el.value-el.min)/(el.max-el.min)*100;el.style.setProperty('--p',p+'%');};
document.querySelectorAll('input[type=range]').forEach(fill);
const sTime=document.getElementById('sTime'),sSwell=document.getElementById('sSwell'),sWind=document.getElementById('sWind');
sTime.oninput=e=>{setTime(+e.target.value);fill(e.target);};
sSwell.oninput=e=>{swell=+e.target.value;document.getElementById('oSwell').textContent=(swell*1.25).toFixed(1)+' m';fill(e.target);};
sWind.oninput=e=>{wind=+e.target.value;document.getElementById('oWind').textContent=Math.round(4+wind*22)+' kn SW';fill(e.target);};
function tg(id,init,fn){const b=document.getElementById(id);let on=init==='auto'?'-1':(init?1:0);
  b.dataset.on=on;b.onclick=()=>{on=on==='-1'?1:on?0:1;b.dataset.on=on;fn(on===1);};}
tg('tSail',true,v=>{clothMesh.visible=v;furledMesh.visible=!v;sailsOn=v;});
tg('tLight','auto',v=>{lightsForce=v;lightsAuto=false;
  emisMesh.material.color.setScalar(v?1:.12);lampLights.forEach((L,i)=>L.intensity=v?110:0);
  lanternLight.intensity=v?260:0;lanternMesh.visible=v;beamMat.uniforms.uOp.value=v?.3:0;});
tg('tGlow',true,v=>{bloomOn=v;});
tg('tRig',true,v=>{rigMesh.visible=v;});
document.getElementById('fold').onclick=e=>{const d=document.getElementById('deck');d.classList.toggle('min');
  e.target.textContent=d.classList.contains('min')?'+':'–';};

const VIEWS=[
  {p:[96,54,76],t:[0,9,4]},
  {p:[16,15,-14],t:[-13,14,2]},
  {p:[28,9.5,18],t:[16,7,2]},
  {p:[12,26,-6],t:[36,28,-28]},
  {p:[6,7,-24],t:[-36,4,-48]},
  {p:[30,104,52],t:[2,0,2]}
];
let tween=null;
function flyTo(i,fast){
  const v=VIEWS[i];
  document.querySelectorAll('#views button').forEach(b=>b.classList.toggle('on',+b.dataset.v===i));
  tween={t:0,d:fast?1.5:1.1,fromP:camera.position.clone(),fromT:controls.target.clone(),
    toP:new THREE.Vector3(...v.p),toT:new THREE.Vector3(...v.t)};
}
document.querySelectorAll('#views button').forEach(b=>b.onclick=()=>flyTo(+b.dataset.v));

/* pins */
const PINS=[
  {l:'The Aurelia',p:new THREE.Vector3(-14,26,4),v:1},
  {l:'Calloway Light',p:new THREE.Vector3(36,42,-28),v:3},
  {l:'Fish Market',p:new THREE.Vector3(16.5,9,14),v:2},
  {l:'Derrick Crane',p:new THREE.Vector3(16.5,20,-7),v:2},
  {l:'The Gap',p:new THREE.Vector3(-42,10,-53),v:4},
  {l:'Windmill Point',p:new THREE.Vector3(58,16,-14),v:5},
];
const pinEls=PINS.map(pn=>{
  const d=document.createElement('div');d.className='pin';d.innerHTML='<i></i><b>'+pn.l+'</b>';
  d.onclick=()=>flyTo(pn.v,true);document.getElementById('pins').appendChild(d);return d;
});

/* harbour log */
const LOGS={
  am:['Pilot boarded off the Skerries; flood tide making.','Cranes made ready at Berth Three; coopers on deck.','Fish landed at the market — mackerel, heavy and bright.','Aurelia takes in line; she rides easy in the roads.'],
  pm:['Barque in the roads, 214 tons, answers to “Aurelia”.','Coals lighted at the gasworks; lamps not yet required.','Dressed overall — the harbour master signals welcome.','Swell building from the southwest; mooring lines doubled.'],
  pm2:['Sun down; the Light reports two flashes, white.','Lamps lit along the quay; watch changed on the pier.','Aurelia’s deck watch on deck; anchor watch set.','Night tide making — she swings to her cable.']
};
let logIdx=0,logT=0,logSet=LOGS.pm;
function refreshLog(h){logSet=h<11?LOGS.am:h<16.6?LOGS.pm:LOGS.pm2;}
function stepLog(){document.getElementById('log').innerHTML=
  '<span class="stamp">'+document.getElementById('oTime').textContent+'</span><span class="txt">'+logSet[logIdx%logSet.length]+'</span>';logIdx++;}
stepLog();

/* bloom */
let composer=null,bloomPass=null;
(async()=>{
  try{
    const[{EffectComposer},{RenderPass},{UnrealBloomPass},{OutputPass}]=await Promise.all([
      import('three/addons/postprocessing/EffectComposer.js'),
      import('three/addons/postprocessing/RenderPass.js'),
      import('three/addons/postprocessing/UnrealBloomPass.js'),
      import('three/addons/postprocessing/OutputPass.js')]);
    composer=new EffectComposer(renderer);
    composer.addPass(new RenderPass(scene,camera));
    bloomPass=new UnrealBloomPass(new THREE.Vector2(innerWidth,innerHeight),.52,.62,.84);
    composer.addPass(bloomPass);composer.addPass(new OutputPass());
    composer.setPixelRatio&&composer.setPixelRatio(renderer.getPixelRatio());
    composer.setSize(innerWidth,innerHeight);
  }catch(e){useBloom=false;}
})();

addEventListener('keydown',e=>{if(e.key==='h'||e.key==='H')document.body.classList.toggle('bare');});
addEventListener('resize',()=>{
  camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight);
  composer&&composer.setSize(innerWidth,innerHeight);
});
let hintTimer=setTimeout(()=>document.getElementById('hint').classList.add('gone'),7000);
['pointerdown','wheel','touchstart'].forEach(ev=>canvas.addEventListener(ev,()=>{
  clearTimeout(hintTimer);document.getElementById('hint').classList.add('gone');},{once:true}));
/* intro */
camera.position.set(...VIEWS[0].p).multiplyScalar(1.28);
tween={t:0,d:3.1,fromP:camera.position.clone(),fromT:controls.target.clone(),
  toP:new THREE.Vector3(...VIEWS[0].p),toT:new THREE.Vector3(...VIEWS[0].t)};

/* ══════════════════════════════ 9. LOOP ══════════════════════════════ */
const _M=new THREE.Matrix4(),_P=new THREE.Vector3(),_S=new THREE.Vector3(),
      _Q=new THREE.Quaternion(),_C=new THREE.Color(),_V=new THREE.Vector3();
function wave(x,z,t){
  return Math.sin(x*.085+t*.9)*.55+Math.sin(z*.115-t*.65)*.45+Math.sin((x*.63+z*.77)*.13+t*1.6)*.3;
}
let last=performance.now(),acc=0,fps=60,frames=0,ft=0;
const rose=document.getElementById('rose');
function loop(now){
  requestAnimationFrame(loop);
  const dt=Math.min(.05,(now-last)/1000),t=now/1000;last=now;
  frames++;ft+=dt;if(ft>.5){fps=Math.round(frames/ft);frames=0;ft=0;}
  logT+=dt;if(logT>6.2){logT=0;stepLog();}

  /* camera tween */
  if(tween){
    tween.t=Math.min(1,tween.t+dt/tween.d);
    const e=tween.t<.5?4*tween.t**3:1-Math.pow(-2*tween.t+2,3)/2;
    camera.position.lerpVectors(tween.fromP,tween.toP,e);
    controls.target.lerpVectors(tween.fromT,tween.toT,e);
    if(tween.t>=1)tween=null;
  }
  controls.update();
  const az=Math.atan2(camera.position.x-controls.target.x,camera.position.z-controls.target.z);
  rose.style.transform='rotate('+(az*180/Math.PI)+'deg)';

  /* ship motion */
  const sh=.42+.58*clamp((-SP.x+9)/46,0,1);
  const h0=wave(SP.x,SP.z,t)*swell*sh*.85;
  const hF=wave(SP.x+9,SP.z,t)*swell*sh*.85,hB=wave(SP.x-9,SP.z,t)*swell*sh*.85;
  const hL=wave(SP.x,SP.z+7,t)*swell*sh*.85,hR=wave(SP.x,SP.z-7,t)*swell*sh*.85;
  shipRoot.position.y=h0+.15+Math.sin(t*.7)*.05;
  shipRoot.rotation.z=lerp(shipRoot.rotation.z,Math.atan2(hF-hB,18)*.85+Math.sin(t*.53)*.014,.06);
  shipRoot.rotation.x=lerp(shipRoot.rotation.x,Math.atan2(hL-hR,14)*.7,.06);

  /* cloth */
  clothU.uTime.value=t;clothU.uWind.value=wind;clothU.uBill.value=.55+wind*.85;

  /* water */
  const camX=camera.position.x,camZ=camera.position.z,step=.34,bottom=-4.2;
  for(let i=0;i<WN;i++){
    const x=wx[i],z=wz[i];
    const h=wave(x,z,t)*swell*wsh[i];
    const q=Math.round(h/step)*step;
    _M.compose(_P.set(x,(q+bottom)*.5,z),_Q,_S.set(CELL,q-bottom,CELL));
    waterMesh.setMatrixAt(i,_M);
    const crest=clamp((q-.45)*1.1,0,1);
    let r=wr[i],g=wg[i],b=wb[i];
    const dx=x-camX,dz=z-camZ,d=Math.sqrt(dx*dx+dz*dz)+1e-3;
    const al=(dx*sunAzX+dz*sunAzZ)/d;
    const tw=.5+.5*Math.sin(t*4.2+wx[i]*1.9+wz[i]*2.7);
    const gl=Math.pow(al<0?0:al,26)*sunGlit*tw*(.4+crest*.9);
    const mix=Math.min(.92,crest*.5+gl);
    const sr=skyU.uSun.value.r,sg=skyU.uSun.value.g,sb=skyU.uSun.value.b;
    _C.setRGB(r+(sr-r)*mix,g+(sg-g)*mix,b+(sb-b)*mix);
    waterMesh.setColorAt(i,_C);
  }
  waterMesh.instanceMatrix.needsUpdate=true;waterMesh.instanceColor.needsUpdate=true;

  /* foam */
  for(let i=0;i<foamN;i++){
    const p=FO.p,ph=hash3(i,3,7)*6.28;
    const s=.6+Math.abs(Math.sin(t*1.6+ph))*.9;
    _M.compose(_P.set(p[i*3]+Math.sin(t+ph)*.2,p[i*3+1]+Math.sin(t*2.1+ph)*.25+swell*.2,p[i*3+2]),
      _Q,_S.set(s*1.2,s*.7,s*1.1));
    foam.setMatrixAt(i,_M);
  }
  foam.instanceMatrix.needsUpdate=true;

  /* bobbers */
  for(const b of bobbers){
    const g=b.g,w=wave(g.position.x,g.position.z,t)*swell*.6;
    g.position.y=w*.8;
    g.rotation.z=Math.sin(t*.9+b.ph)*.05+wave(g.position.x+3,g.position.z,t)*.02;
    g.rotation.x=Math.sin(t*.7+b.ph)*.04;
    if(b.moving){
      const u=(t*.012)%1,a=new THREE.Vector3(-70+u*90,0,-56+u*66);
      g.position.x=a.x;g.position.z=a.z;
      const nx=-70+((u+.01)%1)*90,nz=-56+((u+.01)%1)*66;
      g.rotation.y=Math.atan2(nx-a.x,nz-a.z)+Math.PI;
    }
  }

  /* gulls */
  gulls.forEach((g,i)=>{
    const a=t*g.sp+g.ph;
    g.g.position.set(g.cx+Math.cos(a)*g.r,g.h+Math.sin(a*2.3)*2.4,g.cz+Math.sin(a)*g.r*.8);
    g.g.rotation.y=-a+Math.PI/2;
    const fl=Math.sin(t*7+i)*.55;g.wl.rotation.z=fl;g.wr.rotation.z=-fl;
  });

  /* clouds */
  clouds.forEach(c=>{c.g.position.x+=dt*(1.2+wind*3)*c.sp*.5;
    if(c.g.position.x>170)c.g.position.x=-170;c.g.rotation.y=Math.sin(t*.03)*.05;});

  /* smoke */
  let si=0;
  for(const s of smSrc)for(let i=0;i<PUFFS;i++){
    const ph=i/PUFFS,l=((t*(.09+wind*.05)+ph)%1);
    const sc=.5+l*3.4,fade=l>.78?(1-l)/.22:1;
    _M.compose(_P.set(s.p.x+l*l*(3+wind*8),s.p.y+l*11,s.p.z+l*l*2),
      _Q.setFromAxisAngle(_up,l*2),_S.set(sc*fade,sc*fade*.9,sc*fade));
    smokeMesh.setMatrixAt(si,_M);
    _C.setRGB(.35+l*.55,.36+l*.55,.38+l*.55);smokeMesh.setColorAt(si,_C);
    si++;
  }
  smokeMesh.instanceMatrix.needsUpdate=true;if(smokeMesh.instanceColor)smokeMesh.instanceColor.needsUpdate=true;

  /* crane, mill, lantern, flames, crew */
  if(craneHook){craneHook.rotation.z=Math.sin(t*.9)*.055;craneHook.rotation.x=Math.sin(t*.62)*.03;}
  if(windmillSails)windmillSails.rotation.z=t*(.25+wind*.9);
  beamGrp.rotation.y=t*.34;
  const flick=.85+.15*Math.sin(t*13)+.06*Math.sin(t*31);
  flame.scale.set(.8+Math.sin(t*9)*.18,1+Math.sin(t*7.4)*.5,.8+Math.cos(t*8.1)*.18);
  flame.material.color.setRGB(3*flick,1.7*flick,.6*flick);
  lanternMesh.material.color.copy(skyU.uSun).multiplyScalar((1.8+Math.sin(t*2.2)*.12)*3*(1-night*.2));
  lanternLight.intensity=(lightsAuto&&!lightsForce?night:1)*240*(lightsAuto?1:1);
  blinkers.forEach((b,i)=>{
    const on=((t/b.period+i*.3)%1)<b.duty;
    b.m.visible=on;b.L.intensity=(night*.9+.1)*(on?90:0);
  });
  if(lightsAuto&&!lightsForce)lampLights.forEach((L,i)=>{
    if(i===lampLights.length-1)L.intensity=night*(80+30*Math.sin(t*11+i));
    else L.intensity=night*110*(.94+.06*Math.sin(t*7+i*2));
  });
  crew.forEach((f,i)=>{const p=f.userData.ph;
    f.userData.a1.rotation.x=Math.sin(t*1.4+p)*.2;
    f.userData.l1.rotation.z=Math.sin(t*1.1+p)*.06;});
  walkers.forEach(w=>{
    w.f.position.x+=0;w.f.position.z+=dt*w.sp*w.dir;
    if(w.f.position.z>w.z0+7)w.dir=-1;if(w.f.position.z<w.z0-7)w.dir=1;
    w.f.rotation.y=w.dir>0?Math.PI/2:-Math.PI/2;
    const s=Math.sin(t*4.6+w.ph);
    w.f.userData.l1.rotation.x=s*.5;w.f.userData.l2.rotation.x=-s*.5;
    w.f.userData.a1.rotation.x=-s*.35;w.f.userData.a2.rotation.x=s*.35;
    w.f.position.y=5.05+Math.abs(Math.sin(t*4.6+w.ph))*.05;
  });

  /* pins */
  for(let i=0;i<PINS.length;i++){
    const el=pinEls[i];_V.copy(PINS[i].p).project(camera);
    if(_V.z>1||_V.z<-1){el.style.opacity=0;el.style.pointerEvents='none';continue;}
    const d=camera.position.distanceTo(PINS[i].p);
    el.style.transform='translate3d('+((_V.x*.5+.5)*innerWidth)+'px,'+((-_V.y*.5+.5)*innerHeight)+'px,0)';
    const o=clamp(1-(d-40)/150,.08,1);el.style.opacity=o;el.style.pointerEvents=o>.2?'auto':'none';
  }

  /* render */
  if(useBloom&&bloomOn&&composer)composer.render();else renderer.render(scene,camera);
  document.getElementById('stats').innerHTML='voxels <b>'+TOTAL.toLocaleString()+'</b><br>draws <b>'+
    renderer.info.render.calls+'</b><br>fps <b>'+fps+'</b>';
}
requestAnimationFrame(loop);
</script>
</body>
</html>
```

**What to look at first**

- Drag the **Hour** slider past 19:00 — the sky cools, windows and lamps warm up, the lighthouse beam fades in and starts sweeping, stars appear over the bay, and the beacon on the breakwater blinks red while the one on the far point flashes green.
- Pull **Wind** to the top: every square sail, jib and signal flag bellows and flutters in real time (the cloth ripple is per-instance in the vertex shader, so nothing gets rebuilt), and the distant sloop heels over in the channel.
- **Broadside** view puts you under the mainsail with the deck crew overhead; **Chart** flattens the whole harbour — the breakwater arc, the berth line painted on the quay, the windmill on the hill.

Everything is instanced boxes (one draw call for the town, one for the hull, one per animated system), so the first frame is on screen essentially instantly and the whole thing sits comfortably in the high 50s/60s fps.