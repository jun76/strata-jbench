# Calling at Harbour — a single-file voxel scene

Everything below is one HTML file. It builds ~40k culled voxel instances (town, quay, breakwater, lighthouse, a three‑masted merchantman at her moorings), animates the sea in a vertex shader, and links a harbour‑log panel to hotspots in the 3D scene.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Calling at Harbour · voxel scene</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,300;12..96,500;12..96,800&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500&display=swap" rel="stylesheet">
<style>
:root{
  --ink:#eae4d7; --dim:#98a2a8; --ochre:#e3b35e; --signal:#d16a4a; --sea:#5ea8a4;
  --board:rgba(12,17,22,.87); --line:rgba(227,179,94,.20);
}
*{box-sizing:border-box}
html,body{margin:0;height:100%;overflow:hidden;background:#070b10;color:var(--ink);
  font-family:"IBM Plex Sans",system-ui,sans-serif;-webkit-font-smoothing:antialiased}
#c{position:fixed;inset:0;display:block}
.vig{position:fixed;inset:0;pointer-events:none;z-index:2;
  background:radial-gradient(125% 95% at 52% 42%,transparent 52%,rgba(3,6,9,.62) 100%)}
.hud{position:fixed;inset:0;z-index:3;pointer-events:none;display:grid;
  grid-template-columns:minmax(240px,25vw) 1fr minmax(230px,23vw);
  grid-template-rows:auto 1fr auto;gap:14px;padding:clamp(12px,1.5vw,26px)}

/* ---------- masthead ---------- */
.mast{grid-column:1;grid-row:1;align-self:start;animation:rise .9s .1s both}
.mast .rule{display:flex;align-items:center;gap:9px;font-family:"IBM Plex Mono";font-size:10px;
  letter-spacing:.24em;text-transform:uppercase;color:var(--ochre)}
.pulse{width:7px;height:7px;border-radius:50%;background:var(--signal);
  box-shadow:0 0 0 0 rgba(209,106,74,.55);animation:pulse 2.6s infinite}
@keyframes pulse{70%{box-shadow:0 0 0 11px rgba(209,106,74,0)}100%{box-shadow:0 0 0 0 rgba(209,106,74,0)}}
.mast h1{font-family:"Bricolage Grotesque";font-weight:800;font-size:clamp(36px,5.4vw,76px);
  line-height:.84;letter-spacing:-.028em;margin:.3em 0 .2em;text-shadow:0 10px 34px rgba(0,0,0,.65)}
.mast h1 em{display:block;font-style:normal;font-weight:300;color:var(--ochre);letter-spacing:.01em}
.mast .dek{max-width:33ch;font-size:12.5px;line-height:1.55;color:#b7c0c5;
  border-left:2px solid var(--line);padding-left:12px}
.mast .dek b{color:var(--sea);font-family:"IBM Plex Mono";font-weight:500}

/* ---------- panels ---------- */
.panel{position:relative;background:var(--board);border:1px solid var(--line);
  box-shadow:0 22px 60px rgba(0,0,0,.5),inset 0 1px 0 rgba(255,255,255,.05);
  backdrop-filter:blur(7px);padding:13px 15px 15px;pointer-events:auto}
.panel::before{content:"";position:absolute;top:-1px;left:14px;right:14px;height:2px;
  background:linear-gradient(90deg,transparent,var(--ochre),transparent);opacity:.55}
.panel::after{content:"";position:absolute;right:6px;bottom:6px;width:9px;height:9px;
  border-right:1px solid var(--line);border-bottom:1px solid var(--line)}
.ptitle{display:flex;justify-content:space-between;align-items:baseline;gap:10px;margin:0 0 11px;
  font-family:"IBM Plex Mono";font-size:10px;letter-spacing:.22em;text-transform:uppercase;
  color:var(--ink);border-bottom:1px solid rgba(255,255,255,.08);padding-bottom:8px}
.ptitle span{color:var(--dim);letter-spacing:.1em;text-transform:none;font-size:9.5px}

/* ---------- watch panel ---------- */
.watch{grid-column:1;grid-row:3;align-self:end;max-width:360px;animation:rise .9s .35s both}
.clockRow{display:flex;align-items:flex-end;gap:10px;margin-bottom:4px}
.clockRow .big{font-family:"Bricolage Grotesque";font-weight:500;font-size:40px;line-height:.9;
  letter-spacing:-.02em}
.clockRow .ph{font-family:"IBM Plex Mono";font-size:10px;letter-spacing:.18em;text-transform:uppercase;
  color:var(--ochre);padding-bottom:5px}
.ctl{display:block;margin:11px 0 3px}
.ctl .lab{display:flex;justify-content:space-between;font-size:10px;letter-spacing:.14em;
  text-transform:uppercase;color:var(--dim);font-family:"IBM Plex Mono";margin-bottom:6px}
.ctl .lab b{color:var(--ink);font-weight:500;letter-spacing:.06em}
input[type=range]{-webkit-appearance:none;appearance:none;width:100%;height:4px;cursor:pointer;
  background:linear-gradient(90deg,var(--ochre) var(--p,50%),rgba(255,255,255,.13) var(--p,50%))}
input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:15px;height:15px;border-radius:2px;
  transform:rotate(45deg);background:var(--ink);border:1px solid #0a0e12;
  box-shadow:0 0 0 3px rgba(227,179,94,.18);transition:box-shadow .2s}
input[type=range]:hover::-webkit-slider-thumb{box-shadow:0 0 0 6px rgba(227,179,94,.22)}
input[type=range]::-moz-range-thumb{width:14px;height:14px;border-radius:2px;background:var(--ink);
  border:1px solid #0a0e12}
.tele{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin:14px 0 12px;
  padding:10px 0;border-top:1px solid rgba(255,255,255,.07);border-bottom:1px solid rgba(255,255,255,.07)}
.tele div b{display:block;font-family:"IBM Plex Mono";font-size:14px;color:var(--sea);font-weight:500}
.tele div i{font-style:normal;font-size:9px;letter-spacing:.14em;text-transform:uppercase;color:var(--dim)}
.row{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.sw{font-family:"IBM Plex Mono";font-size:9.5px;letter-spacing:.14em;text-transform:uppercase;
  padding:7px 9px;border:1px solid var(--line);background:rgba(255,255,255,.03);color:var(--dim);
  cursor:pointer;transition:.2s;position:relative;overflow:hidden}
.sw:hover{color:var(--ink);border-color:rgba(227,179,94,.5);transform:translateY(-1px)}
.sw[data-on="1"]{background:var(--ochre);border-color:var(--ochre);color:#12181d}
.dial{margin-left:auto;width:50px;height:50px;border-radius:50%;border:1px solid var(--line);
  position:relative;flex:0 0 auto;
  background:radial-gradient(circle at 50% 42%,rgba(94,168,164,.13),transparent 70%)}
.dial::after{content:"N";position:absolute;top:2px;left:50%;transform:translateX(-50%);
  font-family:"IBM Plex Mono";font-size:8px;color:var(--dim)}
.needle{position:absolute;inset:0;transition:transform .45s cubic-bezier(.2,.8,.2,1)}
.needle::before{content:"";position:absolute;left:50%;top:6px;width:2px;height:19px;margin-left:-1px;
  background:var(--signal);clip-path:polygon(50% 0,100% 100%,0 100%)}

/* ---------- log ---------- */
.log{grid-column:3;grid-row:1 / span 2;align-self:start;width:min(23vw,300px);animation:rise .9s .5s both}
.log ul{list-style:none;margin:0;padding:0}
.log li{display:grid;grid-template-columns:auto 1fr;gap:10px;padding:9px 6px 9px 10px;cursor:pointer;
  border-left:2px solid transparent;transition:.22s}
.log li+li{border-top:1px solid rgba(255,255,255,.06)}
.log li .t{font-family:"IBM Plex Mono";font-size:10px;color:var(--ochre);padding-top:2px}
.log li .n{font-size:12px;line-height:1.4;color:#c3cbd0}
.log li .n i{color:var(--ink);font-style:italic}
.log li:hover,.log li.hl{background:rgba(227,179,94,.09);border-left-color:var(--ochre);transform:translateX(-3px)}
.log li:hover .n,.log li.hl .n{color:#fff}

/* ---------- chips ---------- */
.cameo{grid-column:3;grid-row:3;align-self:end;display:flex;flex-direction:column;gap:8px;
  align-items:flex-end;animation:rise .9s .65s both}
.chips{display:flex;gap:7px;flex-wrap:wrap;justify-content:flex-end}
.chip{font-family:"IBM Plex Mono";font-size:9.5px;letter-spacing:.14em;text-transform:uppercase;
  padding:8px 11px;border:1px solid var(--line);background:rgba(12,17,22,.8);color:#c9d1d5;
  cursor:pointer;transition:.22s;backdrop-filter:blur(6px);pointer-events:auto}
.chip:hover{background:var(--ochre);color:#0e1418;transform:translateY(-2px)}
.chip.on{border-color:var(--sea);color:var(--sea)}
.hint{font-family:"IBM Plex Mono";font-size:9.5px;letter-spacing:.13em;color:var(--dim);
  text-align:right;text-transform:uppercase;pointer-events:none}

/* ---------- tooltip + loader ---------- */
#tip{position:fixed;z-index:5;pointer-events:none;opacity:0;transform:translate(-50%,-130%);
  transition:opacity .18s;max-width:240px;background:rgba(9,13,17,.94);border:1px solid var(--line);
  padding:9px 11px;box-shadow:0 16px 40px rgba(0,0,0,.55)}
#tip.on{opacity:1}
#tip b{display:block;font-family:"Bricolage Grotesque";font-weight:500;font-size:14px;letter-spacing:.01em}
#tip s{display:block;text-decoration:none;font-size:11px;color:var(--dim);line-height:1.4;margin-top:3px}
#load{position:fixed;inset:0;z-index:9;background:#070b10;display:grid;place-items:center;
  transition:opacity .9s ease}
#load.off{opacity:0;pointer-events:none}
#load .in{text-align:center}
#load .bar{width:210px;height:2px;background:rgba(255,255,255,.1);overflow:hidden;margin:16px auto 10px}
#load .bar i{display:block;height:100%;width:38%;background:var(--ochre);
  animation:slide 1.1s cubic-bezier(.6,.05,.3,.95) infinite}
@keyframes slide{0%{transform:translateX(-110%)}100%{transform:translateX(370%)}}
#load p{font-family:"IBM Plex Mono";font-size:10px;letter-spacing:.3em;text-transform:uppercase;color:var(--dim);margin:0}
#load h2{font-family:"Bricolage Grotesque";font-weight:800;font-size:clamp(30px,4.4vw,54px);
  margin:0;letter-spacing:-.03em;line-height:.9}
#load h2 em{display:block;font-style:normal;font-weight:300;color:var(--ochre)}
@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@media (max-width:1020px){.log{display:none}.hud{grid-template-columns:minmax(230px,42vw) 1fr 1fr}}
@media (max-width:680px){.mast h1{font-size:34px}.mast .dek{display:none}
  .watch{max-width:none;grid-column:1 / span 3}.cameo{grid-column:1 / span 3;align-items:flex-start}
  .chips{justify-content:flex-start}.hint{display:none}}
</style>
</head>
<body>
<canvas id="c"></canvas>
<div class="vig"></div>

<div class="hud">
  <header class="mast">
    <div class="rule"><span class="pulse"></span>Voxel Harbour · Sheet 03 · live build</div>
    <h1>Calling at<em>Harbour</em></h1>
    <p class="dek">A three‑masted merchantman rides her moorings on the ebb, smoke from the
      galley, topsails to the land wind. <b id="vox">loading</b> voxels, one draw call per material.</p>
  </header>

  <aside class="panel log">
    <h2 class="ptitle">Harbour Log <span>hover to locate</span></h2>
    <ul id="logList"></ul>
  </aside>

  <section class="panel watch">
    <h2 class="ptitle">Watch Panel <span>harbour master</span></h2>
    <div class="clockRow"><span class="big" id="clock">17:16</span><span class="ph" id="phase">Golden Hour</span></div>
    <label class="ctl"><span class="lab">Harbour time <b id="hourOut">17:16</b></span>
      <input id="hour" type="range" min="4.5" max="23" step="0.02" value="17.27"></label>
    <label class="ctl"><span class="lab">Sea state <b id="seaOut">Moderate</b></span>
      <input id="sea" type="range" min="0" max="4" step="0.01" value="1.2"></label>
    <div class="tele">
      <div><b id="windVal">SW 12</b><i>kn · wind</i></div>
      <div><b id="tideVal">+0.8</b><i>m tide</i></div>
      <div><b id="fpsVal">—</b><i>fps</i></div>
    </div>
    <div class="row">
      <button class="sw" id="sailBtn" data-on="1">Sails set</button>
      <button class="sw" id="rigBtn" data-on="1">Rigging</button>
      <button class="sw" id="orbitBtn" data-on="1">Auto‑orbit</button>
      <div class="dial" title="wind"><div class="needle" id="needle"></div></div>
    </div>
  </section>

  <nav class="cameo">
    <div class="chips" id="chips"></div>
    <div class="hint">drag · orbit &nbsp;/&nbsp; scroll · zoom &nbsp;/&nbsp; right‑drag · pan</div>
  </nav>
</div>

<div id="tip"><b></b><s></s></div>
<div id="load"><div class="in">
  <h2>Calling at<em>Harbour</em></h2>
  <div class="bar"><i></i></div>
  <p>Charting the sound</p>
</div></div>

<script type="importmap">
{"imports":{"three":"https://unpkg.com/three@0.161.0/build/three.module.js",
"three/addons/":"https://unpkg.com/three@0.161.0/examples/jsm/"}}
</script>
<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* ══════════════════ 0 · helpers ══════════════════ */
function mulberry32(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);
  t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
let rnd=mulberry32(84211);
const RI=n=>(rnd()*n)|0, pick=a=>a[(rnd()*a.length)|0];
const clamp=THREE.MathUtils.clamp;

const C={
  cobble:[0x6c655b,0x7a736a,0x5f584f,0x837b6e], quayCap:[0x8c8478,0x968e80],
  ashlar:[0x8b8375,0x7e766a,0x958c7e,0x716a5f], wet:[0x4d5350,0x464c4a],
  seaweed:0x33513c, rock:[0x6d7075,0x63666b,0x797c81,0x585c61], rockD:0x4d5155,
  grass:[0x4e7042,0x587a48,0x456438,0x5f844c], earth:[0x6a5540,0x5c4a38],
  oak:[0x7d5734,0x8b6440,0x6c4a2d], deck:[0x9c7547,0x8c6a41,0xa8814f],
  hullDark:0x2b2622, hullTop:0x3b342d, antifoul:0x6e352b, antifoul2:0x5a2b24,
  cream:0xd9cbac, gold:0xc79a4b, trim:0x1c1a18,
  sail:0xe6dcbf, sailDeep:0xcbbf9f, sailHem:0xd4c8a8,
  rope:0xb59b6c, iron:[0x4a4f55,0x40454b], slate:[0x454b56,0x3c424c,0x525a68],
  brick:[0x8b5240,0x7a4636,0x95604b], plaster:[0xd9cfb9,0xcfc3aa,0xe3dac5],
  paintRed:[0xa8483a,0x96402f], paintBlue:[0x39567a,0x31496a], paintGreen:[0x3f6b5c],
  lamp:0xffc86a, win:0xffd39a, copper:0x9d6a4f, awn:[0xd8cfb8,0xa8483a]
};

/* ══════════════════ 1 · renderer / scene ══════════════════ */
const canvas=document.getElementById('c');
const renderer=new THREE.WebGLRenderer({canvas,antialias:true,powerPreference:'high-performance'});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.setSize(innerWidth,innerHeight);
renderer.shadowMap.enabled=true;
renderer.shadowMap.type=THREE.PCFSoftShadowMap;
renderer.toneMapping=THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure=1.15;

const scene=new THREE.Scene();
scene.fog=new THREE.Fog(0x9db2bd,70,265);

const camera=new THREE.PerspectiveCamera(46,innerWidth/innerHeight,0.5,1500);
camera.position.set(-52,27,-38);
const controls=new OrbitControls(camera,renderer.domElement);
controls.enableDamping=true; controls.dampingFactor=.055;
controls.target.set(-2,9,2);
controls.minDistance=14; controls.maxDistance=155;
controls.minPolarAngle=.12; controls.maxPolarAngle=1.44;
controls.autoRotate=true; controls.autoRotateSpeed=.28;
controls.addEventListener('start',()=>{if(controls.autoRotate){controls.autoRotate=false;
  orbitBtn.dataset.on='0';orbitBtn.textContent='Auto‑orbit';}});

/* lights */
const hemi=new THREE.HemisphereLight(0xbcd3e2,0x4b4a44,.7); scene.add(hemi);
const amb=new THREE.AmbientLight(0xffffff,.18); scene.add(amb);
const sun=new THREE.DirectionalLight(0xffffff,2.7); sun.castShadow=true;
sun.shadow.mapSize.set(2048,2048);
Object.assign(sun.shadow.camera,{left:-96,right:96,top:96,bottom:-96,near:20,far:340});
sun.shadow.bias=-0.0007; sun.shadow.normalBias=.06;
scene.add(sun); sun.target.position.set(-4,6,0); scene.add(sun.target);

/* sky dome */
const skyU={uTop:{value:new THREE.Color()},uBot:{value:new THREE.Color()},
  uSun:{value:new THREE.Vector3(0,1,0)},uSunCol:{value:new THREE.Color()},
  uStars:{value:0},uGlow:{value:1}};
scene.add(new THREE.Mesh(new THREE.SphereGeometry(700,32,18),new THREE.ShaderMaterial({
  side:THREE.BackSide,depthWrite:false,fog:false,uniforms:skyU,
  vertexShader:`varying vec3 vP;void main(){vP=normalize(position);
    gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,
  fragmentShader:`varying vec3 vP;uniform vec3 uTop,uBot,uSun,uSunCol;uniform float uStars,uGlow;
    float h21(vec3 p){return fract(sin(dot(p,vec3(12.9898,78.233,45.164)))*43758.545);}
    void main(){
      float y=clamp(vP.y*1.12,-1.,1.);
      vec3 col=mix(uBot,uTop,smoothstep(-0.10,0.62,y));
      float d=max(dot(normalize(vP),normalize(uSun)),0.);
      col+=uSunCol*pow(d,1100.)*7.5*uGlow;
      col+=uSunCol*pow(d,9.)*0.34*uGlow;
      col+=uSunCol*pow(d,2.)*0.055*uGlow;
      if(uStars>.01&&vP.y>-0.02){
        vec3 g=floor(vP*300.);float s=h21(g);
        col+=vec3(step(0.9977,s)*uStars*(0.45+0.55*fract(s*31.)))
             *smoothstep(-0.02,0.34,vP.y);}
      gl_FragColor=vec4(col,1.);
      #include <tonemapping_fragment>
      #include <colorspace_fragment>
    }`})));
skyMeshFix(); function skyMeshFix(){}

/* ══════════════════ 2 · voxel stores ══════════════════ */
const W={solid:new Map(),glow:new Map()};
const SH={solid:new Map(),glow:new Map(),sail:new Map(),furled:new Map()};
const K=(x,y,z)=>(x|0)+','+(y|0)+','+(z|0);
const P=(m,x,y,z,c)=>m.set(K(x,y,z),c);
const E=(m,x,y,z,c)=>m.set(K(x,y,z),{c,e:1});
function box(m,x0,y0,z0,x1,y1,z1,c){
  for(let x=Math.min(x0,x1);x<=Math.max(x0,x1);x++)
  for(let y=Math.min(y0,y1);y<=Math.max(y0,y1);y++)
  for(let z=Math.min(z0,z1);z<=Math.max(z0,z1);z++) P(m,x,y,z,c);}
function boxV(m,x0,y0,z0,x1,y1,z1,pal){
  for(let x=Math.min(x0,x1);x<=Math.max(x0,x1);x++)
  for(let y=Math.min(y0,y1);y<=Math.max(y0,y1);y++)
  for(let z=Math.min(z0,z1);z<=Math.max(z0,z1);z++) P(m,x,y,z,pick(pal));}
function shell(m,x0,y0,z0,x1,y1,z1,c){
  for(let x=x0;x<=x1;x++)for(let y=y0;y<=y1;y++)for(let z=z0;z<=z1;z++){
    if(x===x0||x===x1||y===y0||y===y1||z===z0||z===z1) P(m,x,y,z,c);}}
function shellV(m,x0,y0,z0,x1,y1,z1,pal){
  for(let x=x0;x<=x1;x++)for(let y=y0;y<=y1;y++)for(let z=z0;z<=z1;z++){
    if(x===x0||x===x1||y===y0||y===y1||z===z0||z===z1) P(m,x,y,z,pick(pal));}}
function beam(m,x0,y0,z0,x1,y1,z1,c){
  const d=Math.max(Math.abs(x1-x0),Math.abs(y1-y0),Math.abs(z1-z0));
  for(let i=0;i<=d;i++){const t=i/d;
    P(m,x0+(x1-x0)*t,y0+(y1-y0)*t,z0+(z1-z0)*t,c);}}
function cyl(m,cx,cz,r,y0,y1,c,hollow){
  for(let x=-r;x<=r;x++)for(let z=-r;z<=r;z++){const d=Math.hypot(x,z);
    if(d<=r&&(!hollow||d>r-1.15)) for(let y=y0;y<=y1;y++) P(m,cx+x,y,cz+z,c);}}

/* bake: cull fully-enclosed voxels → InstancedMesh per material */
const stats={vox:0};
const glowBatches=[];
const boxGeo=new THREE.BoxGeometry(1,1,1);
const matSolid=new THREE.MeshLambertMaterial({vertexColors:true});
const matSail=new THREE.MeshLambertMaterial({vertexColors:true});
const matBasic=new THREE.MeshBasicMaterial({vertexColors:true});
const dummy=new THREE.Object3D(), tmpC=new THREE.Color();

function bake(map,material,cast=true){
  const px=[],cx=[];
  for(const [k,v] of map){
    const p=k.split(','),x=+p[0],y=+p[1],z=+p[2];
    if(map.has((x+1)+','+y+','+z)&&map.has((x-1)+','+y+','+z)&&
       map.has(x+','+(y+1)+','+z)&&map.has(x+','+(y-1)+','+z)&&
       map.has(x+','+y+','+(z+1))&&map.has(x+','+y+','+(z-1))) continue;
    px.push(x,y,z); cx.push(typeof v==='object'?v.c:v);
  }
  const n=px.length/3; stats.vox+=n;
  const mesh=new THREE.InstancedMesh(boxGeo,material,n);
  for(let i=0;i<n;i++){dummy.position.set(px[i*3],px[i*3+1],px[i*3+2]);dummy.updateMatrix();
    mesh.setMatrixAt(i,dummy.matrix); mesh.setColorAt(i,tmpC.setHex(cx[i]));}
  mesh.instanceMatrix.needsUpdate=true; if(mesh.instanceColor) mesh.instanceColor.needsUpdate=true;
  mesh.castShadow=cast; mesh.receiveShadow=true; mesh.frustumCulled=false;
  mesh.userData.base=cx.slice();
  return mesh;
}

/* ══════════════════ 3 · geography ══════════════════ */
function isLand(x,z){
  if(x>=11) return true;
  if(z>=24&&z<=42&&x>=11-(z-24)*1.25) return true;   // north headland
  return false;
}
function landH(x,z){
  if(!isLand(x,z)) return 0;
  const rise=Math.max(0,(x-24)/22)*3.6, head=Math.max(0,(z-26)/16)*3.2;
  let h=5+rise+head;
  if(rise+head>.5){const w=.9*Math.sin(x*.19+z*.11)+.8*Math.sin(z*.15-x*.07);
    h+=w*Math.min(1,(rise+head)/3);}
  return Math.max(5,Math.round(h));
}

function buildTerrain(){
  const m=W.solid;
  for(let x=11;x<=58;x++) for(let z=-46;z<=46;z++){
    const h=landH(x,z); if(!h) continue;
    const edge=!isLand(x-1,z)||!isLand(x-1,z-1)||!isLand(x-1,z+1);
    let surf,sub;
    if(x<=23){surf=pick(C.cobble);sub=C.earth;}
    else if(edge){surf=pick(C.rock);sub=C.rockD;}
    else {surf=pick(C.grass);sub=pick(C.earth);}
    for(let y=h-2;y<=h;y++) P(m,x,y,z,y===h?surf:sub);
    if(x>23&&edge) for(let y=0;y<=h;y++) if(rnd()<.45) P(m,x,y,z,pick(C.rock));
  }
  /* quay revetment, x = 9..10 */
  for(let z=-46;z<=46;z++){
    if(!isLand(11,z)) continue;
    for(let x=9;x<=10;x++) for(let y=-3;y<=5;y++){
      let c=pick(C.ashlar);
      if(y<=1) c=pick(C.wet);
      if(y<=0&&rnd()<.34) c=C.seaweed;
      P(m,x,y,z,c);
    }
    P(m,9,5,z,pick(C.quayCap)); P(m,10,5,z,pick(C.quayCap));
    if(z%7===0){P(m,9,4,z,C.wet);P(m,9,3,z,C.wet);}   /* tide marks */
  }
  /* steps down to the water */
  for(let i=0;i<6;i++) boxV(m,8-i,5-i,18,8-i,5-i,22,i>3?C.wet:C.ashlar);
  /* deep-sea floor so the translucent sea reads as depth */
  const deep=new THREE.Mesh(new THREE.PlaneGeometry(1200,1200),
    new THREE.MeshStandardMaterial({color:0x0c3040,roughness:1}));
  deep.rotation.x=Math.PI/2; deep.position.y=-2.6; scene.add(deep);
}

/* ══════════════════ 4 · quay props ══════════════════ */
function bollard(m,x,y,z){boxV(m,x,y,z,x,y+1,z,C.granite||C.ashlar);P(m,x,y+2,z,0x3c4147);}
function lampPost(x,z){
  const m=W.solid,y=5;
  boxV(m,x,y,z,x,y+4,z,C.iron);
  box(m,x-1,y+5,z,x+1,y+5,z,0x30353a);
  P(m,x,y+6,z,0x30353a);
  E(W.glow,x,y+5,z,C.lamp);
  addGlow(x,y+5.2,z,3.4);
}
function crateProp(m,x,y,z,s,c){
  boxV(m,x,y,z,x+s-1,y+s-1,z+s-1,c||C.oak);
  for(let a=0;a<s;a++)for(let b=0;b<s;b++) P(m,x+a,y+s-1,z+b,pick(C.deck));
  P(m,x,y+1,z,C.trim);P(m,x+s-1,y+1,z+s-1,C.trim);
}
function barrel(x,y,z,c){const m=W.solid;
  for(let a=0;a<2;a++)for(let b=0;b<2;b++){P(m,x+a,y,z+b,c);P(m,x+a,y+1,z+b,c);}
  P(m,x,y+2,z,c);P(m,x+1,y+2,z+1,c);}
function tree(x,y,z){
  const m=W.solid,h=3+RI(3);
  box(m,x,y,z,x,y+h,z,0x5c4227);
  for(let dx=-2;dx<=2;dx++)for(let dy=-1;dy<=2;dy++)for(let dz=-2;dz<=2;dz++){
    const d=Math.hypot(dx,dy*.9,dz);
    if(d<2.35-(rnd()*.5)) P(m,x+dx,y+h+dy,z+dz,pick(C.grass));}
}
function person(x,y,z,coat,legs){
  const m=W.solid, skin=0xb98a63;
  P(m,x,y,z,legs);P(m,x,y+1,z,coat);P(m,x,y+2,z,skin);P(m,x,y+3,z,pick([0x3a3f45,0x7a4636,0xd9cfb9]));
}
function buildQuayProps(){
  const m=W.solid;
  for(let z=-24;z<=22;z+=6) bollard(m,11,5,z);
  for(let z=-21;z<=21;z+=7) lampPost(13,z);
  /* crates, barrels, nets, market clutter on the flat */
  for(let i=0;i<26;i++){const x=12+RI(9),z=-30+RI(52);
    if(rnd()<.62) crateProp(m,x,6,z,rnd()<.5?2:1,pick([0x7d5734,0x6c4a2d,0x8b6440]));
    else barrel(x,6,z,pick([0x6a4a2e,0x5c4028,0x7a5a38]));}
  /* rope coils */
  for(let i=0;i<5;i++){const x=12+RI(8),z=-28+RI(50);
    for(let a=0;a<3;a++){const r=a+1;
      for(let t=0;t<12;t++){const ang=t/12*Math.PI*2;
        P(m,x+Math.round(Math.cos(ang)*r),6,z+Math.round(Math.sin(ang)*r),C.rope);}}}
  /* people */
  [[12,-6,0xa8483a],[14,-4,0x39567a],[17,2,0x4e6b52],[13,10,0x8b5240],[19,15,0x39567a],
   [16,-14,0x7a736a],[21,8,0xa8483a],[12,4,0x39567a],[15,20,0x4e6b52],[23,-10,0x8b5240]]
   .forEach(p=>person(p[0],6,p[1],p[2],0x2f343a));
  /* cart on the cobbles */
  const cx=20,cz=-18;
  boxV(m,cx,8,cz,cx+3,8,cz+1,C.oak);
  boxV(m,cx+1,9,cz,cx+2,9,cz+1,pick(C.deck));
  [[cx,cz],[cx+3,cz]].forEach(w=>{for(let t=0;t<8;t++){const a=t/8*Math.PI*2;
    P(m,w[0]+Math.round(Math.cos(a)),7,cz+Math.round(Math.sin(a)*0)+w[1],0x3a2b1c);
    P(m,w[0]+Math.round(Math.cos(a)*.5),7,w[1],0x3a2b1c);}});
  P(m,cx+4,8,cz,0x5c4227);
  /* wooden jetty out to the ship */
  for(let x=4;x<=10;x++) for(let z=-6;z<=-2;z++){
    if(z===-6||z===-2||x===4) P(m,x,6,z,0x6c4a2d); else P(m,x,6,z,pick(C.deck));}
  for(let x=5;x<=10;x+=3) for(const zz of[-5,-3]) box(m,x,1,zz,x,5,zz,0x4c3a24);
  lampPost(9,-7);
  /* gangway leaning to the rail */
  for(let i=0;i<4;i++){const x=6-i,y=6+Math.round(i*.7);
    box(m,x,y,-6,x,y,-2,0x6c4a2d);}
}

/* ══════════════════ 5 · breakwater, lighthouse, beacon ══════════════════ */
function buildBreakwater(){
  const m=W.solid;
  const p0=new THREE.Vector3(-3,0,34), p1=new THREE.Vector3(-25,0,7);
  for(let i=0;i<=92;i++){
    const t=i/92, x=Math.round(p0.x+(p1.x-p0.x)*t), z=Math.round(p0.z+(p1.z-p0.z)*t);
    const w= t<.06?4:(t>.9?4:3);
    const top=6+(t>.86?2:0);
    for(let dx=-w;dx<=w;dx++) for(let dz=-w;dz<=w;dz++){
      if(Math.hypot(dx,dz)>w+0.3) continue;
      const hh=Math.round(top-Math.hypot(dx,dz)*.14);
      for(let y=-3;y<=hh;y++)
        P(m,x+dx,y,z+dz, y>hh-1?pick(C.granite||C.rock):pick(C.rock));
      if(hh<top) continue;
    }
    if(i%11===5){ P(m,x,top+1,z+ (rnd()<.5?w:-w),pick(C.rock)); }
  }
  /* lighthouse */
  const lx=-26,lz=6,gy=8;
  cyl(m,lx,lz,5,gy,gy+1,pick(C.rock));
  for(let ring=4;ring>=1;ring--){
    const y0=gy+2+(4-ring)*4, y1=gy+5+(4-ring)*4;
    for(let x=-ring;x<=ring;x++)for(let z=-ring;z<=ring;z++){
      if(Math.hypot(x,z)>ring+.4) continue;
      const band=Math.round((y0-gy)/4)%2===0;
      for(let y=y0;y<=y1;y++) P(m,lx+x,y,lz+z,band?0xe6e0d3:0xb8453a);}
  }
  box(m,lx-2,gy+22,lz-2,lx+2,gy+22,lz+2,0x3a3f45);
  E(W.glow,lx,gy+21,lz,0xfff0c0);
  E(W.glow,lx+1,gy+21,lz,0xfff0c0);E(W.glow,lx-1,gy+21,lz,0xfff0c0);
  E(W.glow,lx,gy+21,lz+1,0xfff0c0);E(W.glow,lx,gy+21,lz-1,0xfff0c0);
  box(m,lx,gy+23,lx,lx,gy+24,lz,0xb8453a); P(m,lx,gy+25,lz,0x3a3f45);
  for(let a=0;a<10;a++){const ang=a/10*Math.PI*2;
    P(m,lx+Math.round(Math.cos(ang)*3),gy+20,lz+Math.round(Math.sin(ang)*3),0x3a3f45);}
  addGlow(lx,gy+21,lz,7);
  lighthouseY=gy+21;
  /* beacon on the headland */
  const bx=3,bz=32;
  boxV(m,bx-1,landH(bx,bz),bz-1,bx+1,landH(bx,bz)+3,bz+1,C.plaster);
  box(m,bx-2,landH(bx,bz)+4,bz-2,bx+2,landH(bx,bz)+4,bz+2,0xb8453a);
  E(W.glow,bx,landH(bx,bz)+3,bz,C.lamp); addGlow(bx,landH(bx,bz)+3.2,bz,3);
  beam(m,bx,landH(bx,bz)+5,bz,bx,landH(bx,bz)+9,bz,0x5c4227);
  for(let i=0;i<4;i++) P(m,bx+1,landH(bx,bz)+6+i,bz,0xb8453a);
}
let lighthouseY=20;

/* ══════════════════ 6 · town ══════════════════ */
function gable(m,x0,z0,x1,z1,yBase){
  const w=x1-x0;
  boxV(m,x0-1,yBase,z0-1,x1+1,yBase,z1+1,C.slate);
  for(let i=1;i<=Math.ceil(w/2);i++)
    boxV(m,x0+i,yBase+i,z0,x1-i,yBase+i,z1,C.slate);
}
function windowsRow(m,x,y,z0,z1,step,face){
  for(let z=z0;z<=z1;z+=step){
    if(face==='x'){E(W.glow,x,y,z,C.win);E(W.glow,x,y+1,z,C.win);}
    else {E(W.glow,z,y,x,C.win);E(W.glow,z,y+1,x,C.win);}
  }
}
function chimneySmoke(x,y,z){smokeSources.push({x,y,z});}
function buildTown(){
  const m=W.solid;
  /* ---- warehouse (the cargo shed) ---- */
  let gy=5, x0=22,z0=-22,x1=34,z1=-8;
  boxV(m,x0,gy,z0,x1,gy,z1,C.brick);
  boxV(m,x0,gy+1,z0,x1,gy+8,z1,C.brick);
  gable(m,x0,z0,x1,z1,gy+9);
  for(let z=z0+1;z<z1;z+=2) for(let y=gy+2;y<=gy+7;y+=3) E(W.glow,x0,y,z,0x2f3a42);
  box(m,x0,gy,z0+4,x0,gy+5,z0+6,0x3a2b1c);          /* loading door */
  box(m,x0-2,gy+6,z0+5,x0,gy+6,z0+5,0x5c4227);      /* hoist beam */
  beam(m,x0-1,gy+6,z0+5,x0-1,gy+2,z0+5,C.rope);
  crateProp(m,x0-2,6,z0+4,2,pick(C.oak));
  windowsRow(m,x1,gy+3,z0+1,z1-1,3,'x');
  boxV(m,x1-1,gy+12,z0+2,x1-1,gy+16,z0+3,C.brick);  /* chimney */
  chimneySmoke(x1-1,gy+17,z0+2);
  /* ---- custom house + clock tower ---- */
  x0=22;z0=-4;x1=36;z1=12;
  shellV(m,x0,gy,z0,x1,gy+6,z1,C.plaster);
  shellV(m,x0,gy+1,z0,x1,gy+6,z1,C.plaster);
  gable(m,x0,z0,x1,z1,gy+7);
  windowsRow(m,x0,gy+2,z0+1,z1-1,3,'x');
  windowsRow(m,x0,gy+4,z0+1,z1-1,3,'x');
  box(m,x0,gy,z0+7,x0,gy+3,z0+9,C.paintBlue);
  const tx=28,tz=4;
  shellV(m,tx-2,gy,tz-2,tx+2,gy+17,tz+2,C.plaster);
  shellV(m,tx-2,gy+1,tz-2,tx+2,gy+17,tz+2,C.plaster);
  boxV(m,tx-3,gy+18,tz-3,tx+3,gy+18,tz+3,C.granite||C.ashlar);
  cyl(m,tx,tz,2,gy+19,gy+22,0xd9cfb9);
  boxV(m,tx-2,gy+23,tz-2,tx+2,gy+23,tz+2,C.paintGreen);
  beam(m,tx,gy+23,tz,tx,gy+27,tz,0xc79a4b);
  /* clock face on the harbour side, live hands added later */
  for(let dx=-1;dx<=1;dx++)for(let dy=-1;dy<=1;dy++){
    E(W.glow,tx-3,gy+15+dy,tz+dx,0xf3ead4);}
  box(m,tx-4,gy+14,tz-2,tx-4,gy+17,tz+2,0xb9ae96);
  /* ---- market shed ---- */
  x0=14;z0=14;x1=22;z1=22;
  for(let x=x0;x<=x1;x+=4)for(let z=z0;z<=z1;z+=4) boxV(m,x,gy,z,x,gy+4,z,C.oak);
  for(let i=0;i<=8;i++){const y=gy+5+Math.round(i*.35);box(m,x0-1,y,z0+i,x1+1,y,z0+i,pick(C.awn));}
  for(let i=0;i<=8;i++){const y=gy+5+Math.round(i*.35);box(m,x0-1,y,z1-i,x1+1,y,z1-i,pick(C.awn));}
  for(let i=0;i<5;i++){const x=x0+1+RI(7),z=z0+1+RI(7);
    boxV(m,x,gy+1,z,x+1,gy+1,z+1,pick(C.deck));
    for(let a=0;a<2;a++)for(let b=0;b<2;b++) P(m,x+a,gy+2,z+b,pick([0xa8483a,0xd8cfb8,0x4e6b52]));}
  /* ---- cottages ---- */
  const cott=[[15,26,6,5],[24,32,7,5],[32,28,6,6],[15,-34,7,5],[26,-32,6,5],[36,-24,6,5],
              [28,20,6,5],[40,-8,7,5],[40,4,6,4]];
  for(const c of cott){
    const [cx,cz,w,h]=c, g=landH(cx,cz);
    const wall=pick([C.plaster,C.plaster,C.brick]);
    shellV(m,cx,g,cz,cx+w,g+h,cz+w,wall);
    shellV(m,cx,g+1,cz,cx+w,g+h,cz+w,wall);
    boxV(m,cx,g,cz,cx+w,g,cz+w,pick(C.deck));
    gable(m,cx,cz,cx+w,cz+w,g+h+1);
    for(let z=cz+1;z<cz+w;z+=2) for(let y=g+2;y<g+h;y+=2) E(W.glow,cx,y,z,C.win);
    box(m,cx,g,cz+1,cx,g+2,cz+2,0x4c3a24);
    boxV(m,cx+w-1,g+h+2,cz+1,cx+w-1,g+h+4,cz+1,C.brick);
    if(rnd()<.7) chimneySmoke(cx+w-1,g+h+5,cz+1);
    tree(cx-2,g,cz-2);
  }
  /* ---- boatyard on the headland: hull on stocks ---- */
  const by=landH(11,28);
  boxV(m,11,by,26,17,by,31,C.deck);
  for(let z=0;z<10;z++){const hw=Math.round(3.2-Math.abs(z-5)*.28);
    for(let x=-hw;x<=hw;x++) P(m,14+x,by+1+Math.round(Math.abs(z-5)*.15),26+z,0x8b6440);}
  box(m,14,by+5,26,14,by+9,26,0x7d5734); box(m,14,by+5,35,14,by+8,35,0x7d5734);
  /* ---- windmill ---- */
  const wx=42,wz=30,wg=landH(wx,wz);
  for(let i=0;i<10;i++) cyl(m,wx,wz,3-(i>6?1:0),wg+i,wg+i,pick(C.rock));
  boxV(m,wx-2,wg+10,wz-2,wx+2,wg+11,wz+2,0x4c3a24);
  beam(m,wx-3,wg+11,wz,wx-6,wg+13,wz,0xd9cfb9);
  windmill=new THREE.Group(); windmill.position.set(wx-6,wg+13,wz); scene.add(windmill);
  for(let b=0;b<4;b++){
    const blade=new THREE.Group(); blade.rotation.x=b*Math.PI/2;
    const arm=new THREE.Mesh(new THREE.BoxGeometry(.6,9,.5),new THREE.MeshLambertMaterial({color:0x7d5734}));
    arm.position.y=4.5; blade.add(arm);
    const sailc=new THREE.Mesh(new THREE.BoxGeometry(2.2,7,.15),
      new THREE.MeshLambertMaterial({color:0xe6dcbf,transparent:true,opacity:.92}));
    sailc.position.set(1.3,5,0); blade.add(sailc);
    windmill.add(blade);
  }
  for(let i=0;i<8;i++) tree(24+RI(22),landH(24+RI(22),-40+RI(20))||6,-40+RI(20));
}
let windmill=null;
const smokeSources=[];

/* ══════════════════ 7 · crane, boats, buoys ══════════════════ */
function buildSmallStuff(){
  const m=W.solid, gy=5;
  /* harbour crane */
  const cx=17,cz=8;
  beam(m,cx,gy,cz,cx,gy+9,cz,0x6c4a2d);
  beam(m,cx-3,gy,cz,cx,gy+7,cz,0x5c4227);
  beam(m,cx+3,gy,cz,cx,gy+7,cz,0x5c4227);
  beam(m,cx,gy+9,cz,cx-10,gy+4,cz-6,0x8b6440);
  beam(m,cx,gy+9,cz,cx-8,gy+10,cz+2,0x5c4227);
  for(let y=0;y<7;y++) P(m,cx-6,gy+9-y,cz-4,C.rope);
  crateProp(m,cx-8,gy+1,cz-5,2,pick(C.oak));
  /* fishing smack moored in the basin */
  smack=new THREE.Group(); smack.position.set(-14,0,22); scene.add(smack);
  const sm=new Map();
  for(let z=-5;z<=5;z++) for(let y=-2;y<=1;y++){
    const hw=Math.max(0,2.6-Math.abs(z)*.18-y*.3);
    for(let x=-3;x<=3;x++) if(Math.abs(x)<=hw) P(sm,x,y,z,y<0?C.paintRed:pick(C.deck));}
  for(let z=-5;z<=5;z++){const hw=Math.max(0,2.7-Math.abs(z)*.18);
    for(let x=-3;x<=3;x++) if(Math.abs(x)<=hw&&Math.abs(x)>hw-1.05) P(sm,x,2,z,0x8b4a3a);}
  beam(sm,0,2,0,0,12,0,0x7d5734); beam(sm,-3,9,0,3,9,0,0x7d5734);
  for(let x=-2;x<=2;x++) for(let y=5;y<=9;y++)
    P(sm,x,y,Math.round(Math.sin((x+2)/4*Math.PI)*1.4),pick(C.sail));
  const smM=bake(sm,matSolid); smack.add(smM);
  /* rowboat hauled up on the quay */
  for(let z=-3;z<=3;z++){const hw=Math.max(0,1.6-Math.abs(z)*.2);
    for(let x=-2;x<=2;x++) if(Math.abs(x)<=hw) P(m,13+x,6,30+z,0x8b6440);}
  /* channel buoys */
  [[-18,-14],[-22,20],[-30,-2]].forEach((b,i)=>{
    const g=new THREE.Group(); g.position.set(b[0],0,b[1]); scene.add(g);
    const mm=new Map();
    cyl(mm,0,0,1,-1,0,i%2?0xb8453a:0x39567a);
    P(mm,0,1,0,i%2?0xb8453a:0x39567a); P(mm,0,2,0,0x1c1a18);
    g.add(bake(mm,matSolid,false));
    buoys.push(g);
  });
}
let smack=null; const buoys=[];

/* ══════════════════ 8 · the ship ══════════════════ */
const YAW=-0.115, SHIP_X=-3, SHIP_Z=-2;
function shipW(x,y,z){const s=Math.sin(YAW),c=Math.cos(YAW);
  return new THREE.Vector3(SHIP_X+x*c+z*s,y,SHIP_Z-x*s+z*c);}
function buildShip(){
  const m=SH.solid,g=SH.glow,sa=SH.sails,fu=SH.furled;
  const yK=-3,yR=8;
  function hw(z,y){
    const t=(z+19)/41; let bw;
    if(t<.14){bw=3.1+2.7*Math.sin(t/.14*Math.PI/2);}
    else if(t>.66){bw=6.1*Math.pow(Math.max(0,1-(t-.66)/.34),.72)+.15;}
    else {bw=5.2+.95*Math.sin((t-.14)/.52*Math.PI);}
    const v=clamp((y-yK)/(yR-yK),0,1.25);
    let vs=.30+.70*Math.pow(v,.62);
    vs*=1+.10*Math.max(0,v-.85);
    return bw*vs;
  }
  /* hull */
  for(let z=-19;z<=22;z++){
    for(let y=yK;y<=6;y++){
      const w=hw(z,y), lim=Math.ceil(w);
      for(let x=-lim;x<=lim;x++){
        if(Math.abs(x)>w) continue;
        let c;
        if(y<=-1) c=C.antifoul; else if(y===0) c=C.antifoul2;
        else if(y===3||y===4) c=C.cream; else if(y>=6) c=C.hullTop; else c=C.hullDark;
        P(m,x,y,z,c);
      }
    }
    /* gunports on the cream strake */
    if(z%3===0){const lim=Math.floor(hw(z,4));
      for(const s of[-1,1]){P(m,s*lim,3,z,C.trim);P(m,s*lim,4,z,C.trim);
        if(s>0) P(m,s*lim,4,z,0x2b2622);}}
  }
  /* decks, bulwarks, sheer */
  for(let z=-19;z<=22;z++){
    const t=(z+19)/41, raised=(t<.2||t>.72), yD=raised?8:7;
    const wD=hw(z,yD);
    for(let x=-Math.floor(wD);x<=Math.floor(wD);x++) P(m,x,yD,z,pick(C.deck));
    for(let y=yD-0;y<=yD+1;y++){
      const w=hw(z,y+ (y>yD?1:0)), lim=Math.ceil(w);
      for(let x=-lim;x<=lim;x++){const ax=Math.abs(x);
        if(ax<=w&&ax>w-1.05) P(m,x,y,z,y>yD?C.hullDark:C.trim);}}
    const wl=Math.ceil(hw(z,yD+1));
    for(let x=-wl;x<=wl;x++){const ax=Math.abs(x);
      if(ax<=wl&&ax>wl-1.05) P(m,x,yD+2,z,0x3b342d);}
    if(z%4===0&&raised) P(m,Math.round(wD),yD+2,z,C.gold);
  }
  /* stern gallery + quarterdeck cabin */
  for(let y=4;y<=6;y++) for(let x=-3;x<=3;x+=2) E(g,x,y,-19,C.win);
  box(m,-3,4,-19,3,6,-19,C.trim);
  shell(m,-4,9,-17,4,11,-10,0xe0d7c2);
  for(let z=-16;z<=-11;z+=2){E(g,-4,10,z,C.win);E(g,4,10,z,C.win);}
  E(g,-2,10,-19,C.win);E(g,0,10,-19,C.win);E(g,2,10,-19,C.win);
  box(m,-5,12,-18,5,12,-9,0x3b342d);
  box(m,-3,12,-16,3,12,-11,pick(C.deck));
  /* forecastle + stowed boat */
  boxV(m,-3,9,12,3,9,19,C.deck);
  for(let z=-3;z<=3;z++){const w=Math.max(0,1.7-Math.abs(z)*.22);
    for(let x=-2;x<=2;x++) if(Math.abs(x)<=w) P(m,x,10,15+z,0xe0d7c2);}
  beam(m,0,11,13,0,11,17,0xc79a4b);
  /* capstan, hatch, cargo on deck */
  cyl(m,0,0,1,8,9,0x6c4a2d); P(m,0,10,0,0x8b6440);
  box(m,-3,8,-5,3,8,-1,0x3b342d);
  crateProp(m,-2,8,4,2,0x7d5734); crateProp(m,1,8,6,1,0x8b6440);
  barrel(2,8,-3,0x6a4a2e); barrel(-4,8,-6,0x5c4028);
  person(-1,9,3,0xa8483a,0x2f343a); person(3,9,-8,0x39567a,0x2f343a);
  /* masts + yards */
  const masts=[{z:0,top:30,name:'main'},{z:11,top:28,name:'fore'},{z:-13,top:25,name:'mizzen'}];
  for(const M of masts){
    beam(m,0,yD0(M.z),M.z,0,M.top,M.z,0x7d5734);
    for(let y=M.top-2;y<=M.top;y++) P(m,0,y,M.z,0x5c4227);
    P(m,0,M.top+1,M.z,0xc79a4b);
    for(const yy of[M.top*.68,M.top*.85]){
      for(let x=-2;x<=2;x++) P(m,x,Math.round(yy),M.z,0x5c4227);}
  }
  function yD0(){return 8;}
  const yards=[
    {z:0,y:15,hw:5.4,sh:6,belly:2.2},{z:0,y:22,hw:3.8,sh:4,belly:1.6},{z:0,y:26.5,hw:2.3,sh:3,belly:1.1},
    {z:11,y:14,hw:5.0,sh:5.6,belly:2.2},{z:11,y:20.5,hw:3.5,sh:3.6,belly:1.5},{z:11,y:24.5,hw:2.1,sh:2.6,belly:1},
    {z:-13,y:13,hw:4.0,sh:4.6,belly:1.9},{z:-13,y:19,hw:2.8,sh:3.2,belly:1.3}
  ];
  for(const Y of yards){
    box(m,-Y.hw,Y.y,Y.z,Y.hw,Y.y,Y.z,0x6c4a2d);
    P(m,-Y.hw-1,Y.y,Y.z,0x5c4227);P(m,Y.hw+1,Y.y,Y.z,0x5c4227);
    squareSail(sa,Y.z,Y.y,Y.sh,Y.hw,Y.belly);
    /* furled alternative */
    for(let x=-Y.hw+1;x<=Y.hw-1;x++){
      P(fu,x,Y.y-1,Y.z,C.sailDeep);P(fu,x,Y.y-2,Y.z,C.sail);
      P(fu,x,Y.y-1,Y.z+1,C.sail);P(fu,x,Y.y-2,Y.z+1,C.sailHem);}
  }
  function squareSail(map,mz,yTop,h,hw,belly){
    for(let x=-hw;x<=hw;x++){
      const u=(x+hw)/(2*hw), b=Math.sin(Math.PI*u);
      const foot=Math.round(yTop-h+1.3*b);
      for(let y=foot;y<=yTop;y++){
        const yy=(y-foot)/Math.max(1,yTop-foot);
        const off=Math.round(belly*b*(.3+.7*(1-Math.pow(Math.abs(yy*2-1),2))));
        let c=C.sail;
        if(y===yTop) c=C.sailDeep; else if(y===foot) c=C.sailHem;
        if(mz===0&&y===yTop-2&&u>.35&&u<.65) c=0xd9a25f;
        P(map,x,y,mz+off,c);
      }
    }
  }
  /* bowsprit, jibs */
  beam(m,0,7.5,20,0,12.5,29,0x6c4a2d);
  beam(m,0,12.5,29,0,13.5,33,0x5c4227);
  for(let z=9;z<=28;z++){
    const t=(z-9)/19;
    const top=Math.round(20-8.5*t), bot=Math.round(9+3.2*t);
    for(let y=bot;y<=top;y++){
      const off=Math.round(Math.sin(t*Math.PI)*1.4);
      P(sa,off,y,z,t>.6?C.sail:C.sailDeep);}
  }
  for(let z=14;z<=28;z++){
    const t=(z-14)/14;
    const top=Math.round(15-4*t), bot=Math.round(9+3.2*t);
    for(let y=bot;y<=top;y++){const off=Math.round(Math.sin(t*Math.PI)*1.1);
      P(sa,off,y,z,C.sail);}
  }
  /* anchor hanging off the port bow */
  beam(m,-5,1,17,-5,5,17,0x3a3f45);
  beam(m,-6,5,17,-4,5,17,0x3a3f45);
  beam(m,-6,1,16,-5,2,17,0x3a3f45);beam(m,-4,1,18,-5,2,17,0x3a3f45);
  /* stern staff + ensign gaff */
  beam(m,0,7,-18,0,14,-20,0x6c4a2d);
  /* rigging */
  const pts=[];
  const ln=(a,b)=>pts.push(a[0],a[1],a[2],b[0],b[1],b[2]);
  const MT={main:[0,30,0],fore:[0,28,11],miz:[0,25,-13]},B=[0,13.2,32];
  ln(MT.fore,B); ln(MT.main,MT.fore); ln(MT.miz,MT.main); ln(MT.miz,[0,14,-20]);
  ln([0,15,0],[0,7.5,20]);
  for(const M of masts){
    const side=hw(M.z,9);
    for(const s of[-1,1]) for(const o of[-2.2,0,2.2]){
      ln([s*(side+.4),8,M.z+o],[s*.55,M.top*.92,M.z]);
    }
  }
  for(const Y of yards){
    ln([-Y.hw-1,Y.y,Y.z],[0,Y.y+5,Y.z]);
    ln([Y.hw+1,Y.y,Y.z],[0,Y.y+5,Y.z]);
  }
  for(let y=12;y<26;y+=2) for(const s of[-1,1]){
    const side=hw(0,8);
    ln([s*(side+.3),y,0],[s*(side+.6),y-1,0]);
  }
  const rigGeo=new THREE.BufferGeometry();
  rigGeo.setAttribute('position',new THREE.Float32BufferAttribute(pts,3));
  rigLines=new THREE.LineSegments(rigGeo,
    new THREE.LineBasicMaterial({color:0x2b241c,transparent:true,opacity:.85}));
  rigLines.frustumCulled=false;
}
let rigLines=null;

/* ── flags (animated instanced strips) ── */
const flags=[];
function makeFlag(origin,dir,w,h,cols,phase){
  const mesh=new THREE.InstancedMesh(boxGeo,new THREE.MeshLambertMaterial({side:THREE.DoubleSide}),w*h);
  const cells=[];let i=0;
  for(let a=0;a<w;a++) for(let b=0;b<h;b++){
    cells.push({a,b}); mesh.setColorAt(i,tmpC.setHex(cols[a<h/2?0:1]!==undefined?pick(cols):cols[0]));
    mesh.setColorAt(i,tmpC.setHex(cols[(b>=h/2)?Math.min(cols.length-1,1):0])); i++;}
  mesh.instanceColor.needsUpdate=true; mesh.frustumCulled=false;
  mesh.castShadow=false;
  flags.push({mesh,cells,w,h,origin,dir,phase:phase||rnd()*10});
  return mesh;
}
function updateFlags(t){
  for(const F of flags){
    let i=0;
    for(const c of F.cells){
      const wob=Math.sin(c.a*.85-t*7.2+F.phase)*.42*(c.a/F.w+.15);
      dummy.position.set(F.origin.x+F.dir.x*c.a, F.origin.y+c.b, F.origin.z+F.dir.z*c.a+wob);
      dummy.rotation.set(0,0,Math.sin(c.a*.85-t*7.2+F.phase)*.12*(c.a/F.w));
      dummy.scale.set(1,1,1); dummy.updateMatrix();
      F.mesh.setMatrixAt(i++,dummy.matrix);
    }
    F.mesh.instanceMatrix.needsUpdate=true;
  }
}

/* ══════════════════ 9 · sea ══════════════════ */
const waterU={uTime:{value:0},uAmp:{value:.34},uWind:{value:.5},
  uDeep:{value:new THREE.Color()},uShallow:{value:new THREE.Color()},
  uFoam:{value:new THREE.Color(0xeef6f4)},uSpark:{value:1}};
function buildWater(){
  const solid=W.solid;
  const foam=new Map();
  const ring=(x,z,val)=>{const k=x+','+z; if(!foam.has(k)||foam.get(k)<val) foam.set(k,val);};
  /* shoreline foam */
  const c0=[];
  for(let x=-30;x<=8;x++) for(let z=-46;z<=46;z++){
    if(solid.has(x+',0,'+z)||solid.has(x+',-1,'+z)||solid.has(x+',-2,'+z)) continue;
    let touch=false;
    for(const d of[[1,0],[-1,0],[0,1],[0,-1]])
      if(solid.has((x+d[0])+',0,'+(z+d[1]))||solid.has((x+d[0])+',-1,'+(z+d[1]))||
         solid.has((x+d[0])+',1,'+(z+d[1]))||solid.has((x+d[0])+',-2,'+(z+d[1]))){touch=true;break;}
    if(touch){ring(x,z,1);c0.push([x,z]);}
  }
  for(const c of c0) for(const d of[[1,0],[-1,0],[0,1],[0,-1]]) ring(c[0]+d[0],c[1]+d[1],.4);
  /* foam collar round the hull */
  const a=7,b=20.5,s=Math.sin(-YAW),co=Math.cos(-YAW);
  for(let x=-40;x<=2;x++) for(let z=-30;z<=30;z++){
    const dx=x-SHIP_X,dz=z-SHIP_Z;
    const rx=dx*co-dz*s, rz=dx*s+dz*co;
    const q=Math.hypot(rx/a,rz/b);
    if(q>.84&&q<1.06){const k=x+','+z; if(!foam.has(k)||foam.get(k)<.75) foam.set(k,.75);}
  }
  const pos=[],fv=[];
  for(let x=-104;x<=10;x++) for(let z=-104;z<=104;z++){
    const d=Math.hypot(x+10,z-4); if(d>112) continue;
    const step=d<62?1:2;
    if(((x%step)+step)%step||((z%step)+step)%step) continue;
    if(isLand(x,z)) continue;
    if(solid.has(x+',0,'+z)||solid.has(x+',-1,'+z)||solid.has(x+',-2,'+z)) continue;
    pos.push(x,-0.5,z); fv.push(foam.get(x+','+z)||0);
  }
  const geo=boxGeo.clone();
  const n=pos.length/3;
  const mesh=new THREE.InstancedMesh(geo,new THREE.MeshStandardMaterial({
    roughness:.22,metalness:0,transparent:true,opacity:.87,flatShading:true}),n);
  for(let i=0;i<n;i++){dummy.position.set(pos[i*3],pos[i*3+1],pos[i*3+2]);
    dummy.rotation.set(0,0,0);dummy.scale.set(1,1,1);dummy.updateMatrix();mesh.setMatrixAt(i,dummy.matrix);}
  geo.setAttribute('aFoam',new THREE.InstancedBufferAttribute(new Float32Array(fv),1));
  mesh.instanceMatrix.needsUpdate=true;
  mesh.receiveShadow=true; mesh.castShadow=false; mesh.frustumCulled=false;
  const mat=mesh.material;
  mat.onBeforeCompile=sh=>{
    Object.assign(sh.uniforms,waterU);
    sh.vertexShader=`uniform float uTime;uniform float uAmp;uniform float uWind;
      attribute float aFoam;varying float vFoam;varying float vH;varying vec3 vW;
      float wv(vec2 p,float t){
        float h=sin(p.x*0.22+t*1.02)*0.28+sin(p.y*0.27-t*0.86)*0.24
              +sin((p.x+p.y)*0.135+t*0.62)*0.30
              +sin(p.x*0.78-p.y*0.63+t*2.2)*0.10*uWind;
        return h*uAmp;}`+sh.vertexShader
      .replace('#include <beginnormal_vertex>',`
        vec3 iP=instanceMatrix[3].xyz;vec2 wq=iP.xz;
        float h=wv(wq,uTime);
        float gx=wv(wq+vec2(0.55,0.),uTime)-h;
        float gz=wv(wq+vec2(0.,0.55),uTime)-h;
        vec3 objectNormal=vec3(normal);
        if(normal.y>0.5) objectNormal=normalize(vec3(-gx*2.3,1.0,-gz*2.3));
        else objectNormal=normalize(objectNormal+vec3(-gx,0.,-gz)*0.9);
        vFoam=aFoam;vH=h;vW=iP+position;`)
      .replace('#include <begin_vertex>',`vec3 transformed=vec3(position.x,position.y+h,position.z);`);
    sh.fragmentShader=`uniform float uTime;uniform vec3 uDeep,uShallow,uFoam;uniform float uSpark;
      varying float vFoam;varying float vH;varying vec3 vW;`+sh.fragmentShader
      .replace('#include <color_fragment>',`
        #include <color_fragment>
        vec3 base=mix(uDeep,uShallow,clamp(0.32+vH*0.55,0.0,1.0));
        float n=sin(vW.x*2.3+vW.z*1.7+uTime*0.9)*0.5+0.5;
        base*=0.90+0.20*n;
        float crest=smoothstep(0.30,0.62,vH);
        float spark=pow(max(0.,sin(vW.x*2.7+uTime*3.3)*sin(vW.z*2.5-uTime*2.7)),12.0);
        float f=clamp(vFoam+crest*0.5+spark*0.8*uSpark,0.0,1.0);
        diffuseColor.rgb=mix(base,uFoam,f*0.88);
        diffuseColor.a=mix(diffuseColor.a,0.97,f*0.55);`);
  };
  scene.add(mesh);
}
function wave(x,z,t,amp=.34){
  let h=Math.sin(x*.22+t*1.02)*.28+Math.sin(z*.27-t*.86)*.24
       +Math.sin((x+z)*.135+t*.62)*.30+Math.sin(x*.78-z*.63+t*2.2)*.10*.5;
  return h*amp;
}

/* ══════════════════ 10 · glow sprites, gulls, smoke ══════════════════ */
const glowSprites=[];
function glowTexture(){
  const cv=document.createElement('canvas');cv.width=cv.height=128;
  const g=cv.getContext('2d'),grd=g.createRadialGradient(64,64,0,64,64,64);
  grd.addColorStop(0,'rgba(255,236,190,1)');grd.addColorStop(.35,'rgba(255,196,110,.42)');
  grd.addColorStop(1,'rgba(255,170,60,0)');
  g.fillStyle=grd;g.fillRect(0,0,128,128);
  const t=new THREE.Texture(cv);t.colorSpace=THREE.SRGBColorSpace;return t;
}
const glowTex=glowTexture();
function addGlow(x,y,z,size){
  const s=new THREE.Sprite(new THREE.SpriteMaterial({map:glowTex,transparent:true,
    blending:THREE.AdditiveBlending,depthWrite:false,opacity:0}));
  s.position.set(x,y,z);s.scale.setScalar(size);scene.add(s);glowSprites.push(s);
}
const gulls=[];
function buildGulls(){
  const white=new THREE.MeshLambertMaterial({color:0xf2f0e8});
  const dark=new THREE.MeshLambertMaterial({color:0x59606a});
  for(let i=0;i<7;i++){
    const g=new THREE.Group();
    const body=new THREE.Mesh(new THREE.BoxGeometry(.5,.45,1.7),white);g.add(body);
    const head=new THREE.Mesh(new THREE.BoxGeometry(.4,.4,.5),white);head.position.set(0,.15,-1);g.add(head);
    const wl=new THREE.Group(),wr=new THREE.Group();
    const L=new THREE.Mesh(new THREE.BoxGeometry(1.9,.12,.55),white);L.position.x=-.95;wl.add(L);
    const R=new THREE.Mesh(new THREE.BoxGeometry(1.9,.12,.55),white);R.position.x=.95;wr.add(R);
    const LT=new THREE.Mesh(new THREE.BoxGeometry(.5,.13,.55),dark);LT.position.x=-1.75;wl.add(LT);
    const RT=new THREE.Mesh(new THREE.BoxGeometry(.5,.13,.55),dark);RT.position.x=1.75;wr.add(RT);
    g.add(wl,wr);
    g.userData={wl,wr,r:16+rnd()*26,sp:.16+rnd()*.16,ph:rnd()*99,y:18+rnd()*15,cx:-4+rnd()*10-5,cz:2+rnd()*8-4,sc:.7+rnd()*.7};
    g.scale.setScalar(g.userData.sc);
    scene.add(g);gulls.push(g);
  }
}
let smoke=null;const smokeN=34,smokeP=[];
function buildSmoke(){
  smoke=new THREE.InstancedMesh(boxGeo,
    new THREE.MeshLambertMaterial({transparent:true,opacity:.5,depthWrite:false,vertexColors:true}),smokeN);
  smoke.frustumCulled=false;smoke.castShadow=false;scene.add(smoke);
  for(let i=0;i<smokeN;i++) respawnSmoke(i,true);
}
function respawnSmoke(i,init){
  const s=smokeSources[i%smokeSources.length]; if(!s) return;
  smokeP[i]={x:s.x+(rnd()-.5)*.6,y:s.y,z:s.z+(rnd()-.5)*.6,
    age:init?rnd()*7:0,life:5+rnd()*3.5,vx:.28+rnd()*.3,vz:.1*rnd()-.05,vy:.9+rnd()*.5};
}

/* ══════════════════ 11 · hotspots / log ══════════════════ */
const SPOTS=[
 {t:'15:42',n:'Pilot flags her <i>off the point</i>',h:'Channel Buoy',
  d:'Number two buoy, safe water to starboard. She has been sighted.',
  box:[-32,-4,-22,-14,4,-6]},
 {t:'16:04',n:'Breakwater lit, <i>ebb running strong</i>',h:'The Breakwater',
  d:'Fifteen years of granite pitched by hand to quiet the swell.',
  box:[-30,-3,2,-18,10,20]},
 {t:'16:11',n:'Barque <i>“Meridian”</i> answers the harbour master',h:'Barque “Meridian”',
  d:'312 tons, three masts. Lines thrown, moorings fast at the long berth.',
  box:[-13,-6,-24,9,34,20]},
 {t:'16:20',n:'Light on the <i>northern head</i>',h:'Lighthouse',
  d:'Fixed white, twenty‑two feet of focused flame over the channel.',
  box:[-30,6,2,-22,26,10]},
 {t:'16:47',n:'Tackle aloft, cargo coming ashore',h:'Cargo Crane',
  d:'The iron‑timber’d crane at No. 4 berth, working the ebb tide.',
  box:[6,5,2,20,17,14]},
 {t:'17:03',n:'Customs boat alongside the <i>long quay</i>',h:'Custom House',
  d:'Clock, coat of arms, and a queue of clerks already an hour old.',
  box:[20,5,-6,38,26,14]},
 {t:'17:20',n:'Fish carts and <i>the market crowd</i>',h:'Market Shed',
  d:'Stripted awnings, salt cod, and gulls with no patience at all.',
  box:[13,5,12,23,13,23]},
];
const hitMeshes=[],spotMarks=[];
function buildSpots(){
  const mat=new THREE.LineBasicMaterial({color:0xe3b35e,transparent:true,opacity:.9});
  SPOTS.forEach((s,i)=>{
    const b=s.box,sx=b[2]-b[0],sy=b[3]-b[1],sz=b[4]-b[3];
    const cx=(b[0]+b[2])/2,cy=(b[1]+b[3])/2,cz=(b[3]!==undefined?(b[1]+b[3])/2:0);
    const geo=new THREE.BoxGeometry(sx,sy,sz);
    const mark=new THREE.LineSegments(new THREE.EdgesGeometry(geo),mat.clone());
    mark.position.set(cx,(b[1]+b[3])/2,(b[2]+b[4])/2);
    mark.visible=false;scene.add(mark);spotMarks.push(mark);
    const hit=new THREE.Mesh(geo,new THREE.MeshBasicMaterial({visible:false}));
    hit.position.copy(mark.position);hit.userData.i=i;scene.add(hit);hitMeshes.push(hit);
  });
}
/* live clock hands on the tower */
let hourHand=null,minHand=null;
function buildClock(){
  const g=new THREE.Group(); g.position.set(27-1.1,20,4); scene.add(g);
  const mk=(len,wd,col)=>{
    const grp=new THREE.Group();
    const m=new THREE.Mesh(new THREE.BoxGeometry(.18,wd,len),new THREE.MeshLambertMaterial({color:col}));
    m.position.y=0; grp.add(m); grp.rotation.order='XYZ';
    const pivot=new THREE.Group(); m.position.y=len/2-.2; pivot.add(m); g.add(pivot); return pivot;};
  hourHand=new THREE.Group(); minHand=new THREE.Group();
  const mkHand=(len,col)=>{
    const p=new THREE.Group();
    const m=new THREE.Mesh(new THREE.BoxGeometry(.16,.22,len),new THREE.MeshLambertMaterial({color:col}));
    m.position.z=len/2-.15; p.add(m); g.add(p); return p;};
  hourHand=mkHand(1.1,0x2a2f34); minHand=mkHand(1.7,0x2a2f34);
  const cap=new THREE.Mesh(new THREE.BoxGeometry(.28,.28,.28),new THREE.MeshLambertMaterial({color:0xc79a4b}));
  g.add(cap);
}

/* ══════════════════ 12 · time of day ══════════════════ */
const KEY=[
 {h:4.8, nm:'First Light', top:'#1c2c4d', bot:'#e58a62', sun:'#ff9d5e', si:2.0, dir:[0.96,0.10,0.42],
  amb:'#4a5a7d', hs:'#4e6488', hg:'#3a3a3a', hg2:'', fog:'#7d7f92', deep:'#153a48', shal:'#2e6f7d',
  cloud:'#e5a083', stars:.42, expo:1.18},
 {h:8.6, nm:'Morning Tide', top:'#3f7cb8', bot:'#bcd6e2', sun:'#fff2da', si:2.7, dir:[0.82,0.52,0.44],
  amb:'#9fb6c8', hs:'#a9c6dc', hg:'#4f5049', fog:'#a8c0ca', deep:'#0f4b5c', shal:'#2f95a4',
  cloud:'#f2eee6', stars:0, expo:1.05},
 {h:13, nm:'Midday', top:'#2f76bf', bot:'#cfe4ea', sun:'#ffffff', si:3.2, dir:[0.16,0.97,-0.18],
  amb:'#b6c9d6', hs:'#b9d5e8', hg:'#585a50', fog:'#bcd3da', deep:'#0f5364', shal:'#36a3b0',
  cloud:'#ffffff', stars:0, expo:1.0},
 {h:17.4,nm:'Golden Hour', top:'#356fa6', bot:'#f5bb7c', sun:'#ffc27a', si:2.8, dir:[-0.86,0.24,-0.45],
  amb:'#a99b8f', hs:'#a3b6cf', hg:'#6a5b47', fog:'#d3b392', deep:'#124a5c', shal:'#3f9aa2',
  cloud:'#f7c99b', stars:0, expo:1.15},
 {h:19.6,nm:'Dusk', top:'#22355c', bot:'#dd7c55', sun:'#ff8d57', si:1.4, dir:[-0.95,0.06,-0.30],
  amb:'#61627e', hs:'#5f76a0', hg:'#3f3d3a', fog:'#8f7d84', deep:'#0f3346', shal:'#27667a',
  cloud:'#e0906f', stars:.28, expo:1.22},
 {h:22.8,nm:'Night Watch', top:'#080f22', bot:'#172a44', sun:'#b7cbe8', si:.45, dir:[-0.42,0.62,0.66],
  amb:'#2b3550', hs:'#39476a', hg:'#24262c', fog:'#20304a', deep:'#071c2b', shal:'#114052',
  cloud:'#465572', stars:1, expo:1.3},
];
const skyCol={top:new THREE.Color(),bot:new THREE.Color(),sun:new THREE.Color(),
  amb:new THREE.Color(),hs:new THREE.Color(),hg:new THREE.Color(),fog:new THREE.Color(),
  deep:new THREE.Color(),shal:new THREE.Color(),cloud:new THREE.Color()};
let night=0,curHour=17.27;
function applyLight(h){
  curHour=h;
  let a=KEY[0],b=KEY[KEY.length-1];
  for(let i=0;i<KEY.length-1;i++) if(h>=KEY[i].h&&h<=KEY[i+1].h){a=KEY[i];b=KEY[i+1];break;}
  if(h<KEY[0].h){a=b=KEY[0];} if(h>KEY[KEY.length-1].h){a=b=KEY[KEY.length-1];}
  const k=clamp((h-a.h)/(b.h-a.h||1),0,1);
  const lc=(t,s)=>skyCol[t].set(s.a).lerp(new THREE.Color(s.b),k);
  const mixC=(t)=>{const ca=new THREE.Color(a[t]),cb=new THREE.Color(b[t]);skyCol[t].copy(ca).lerp(cb,k);};
  ['top','bot','sun','amb','hs','hg','fog','deep','shal','cloud'].forEach(mixC);
  const si=a.si+(b.si-a.si)*k;
  const dir=new THREE.Vector3(
    a.dir[0]+(b.dir[0]-a.dir[0])*k, a.dir[1]+(b.dir[1]-a.dir[1])*k, a.dir[2]+(b.dir[2]-a.dir[2])*k
  ).normalize();
  sun.position.copy(dir).multiplyScalar(150).add(new THREE.Vector3(-4,0,0));
  sun.intensity=si; sun.color.copy(skyCol.sun);
  amb.intensity=.10+.16*(1-Math.abs(dir.y-.5)); amb.color.copy(skyCol.amb);
  hemi.color.copy(skyCol.hs); hemi.groundColor.copy(skyCol.hg);
  hemi.intensity=.34+.5*clamp(dir.y+.25,0,1);
  scene.fog.color.copy(skyCol.fog);
  renderer.setClearColor(skyCol.bot);
  skyU.uTop.value.copy(skyCol.top); skyU.uBot.value.copy(skyCol.bot);
  skyU.uSun.value.copy(dir); skyU.uSunCol.value.copy(skyCol.sun);
  skyU.uGlow.value=clamp(si/2.6,.25,1.15);
  const starA=new THREE.Color(a.stars),starB=new THREE.Color(b.stars);
  skyU.uStars.value=a.stars+(b.stars-a.stars)*k;
  waterU.uDeep.value.copy(skyCol.deep); waterU.uShallow.value.copy(skyCol.shal);
  waterU.uSpark.value=clamp(si/2.4,0,1);
  night=clamp((1.55-Math.abs(dir.y-.5)*2.2)*.9 + (skyU.uStars.value>0? .6:0),0,1);
  night=clamp(1.05-(dir.y*1.35+ (h>11&&h<17?.9:0))*.9,0,1);
  const lampLevel=clamp((h<8?(8-h)/3.4:0)+(h>16.6?(h-16.6)/2.4:0),0,1);
  lampOn=lampLevel;
  for(const s of glowSprites) s.material.opacity=lampLevel*.75;
  const dayGlass=new THREE.Color(0x3d4750);
  for(const mesh of glowBatches){
    const base=mesh.userData.base;
    for(let i=0;i<base.length;i++)
      mesh.setColorAt(i,tmpC.setHex(base[i]).lerp(dayGlass,(1-lampLevel)*.86));
    if(mesh.instanceColor) mesh.instanceColor.needsUpdate=true;
  }
  renderer.toneMappingExposure=KEY[0]?(a.expo+(b.expo-a.expo)*k):1.1;
  if(windmill) windmill.traverse(o=>{if(o.material&&o.material.color)o.material.color.copy(skyCol.cloud)
      .lerp(new THREE.Color(0xffffff),.3);});
  /* clock readout */
  const hh=Math.floor(h), mm=Math.floor((h-hh)*60);
  const str=String(hh).padStart(2,'0')+':'+String(mm).padStart(2,'0');
  clockEl.textContent=str; hourOut.textContent=str;
  phaseEl.textContent=(k<.5?a.nm:b.nm);
  if(hourHand){const t=h%12; hourHand.rotation.x=-t/12*Math.PI*2; minHand.rotation.x=-(h%1)*Math.PI*2;}
  const tide=Math.sin(h*.52-1.2);
  tideVal.textContent=(tide>=0?'+':'')+tide.toFixed(1);
  tideLevel=tide;
}
let lampOn=1,tideLevel=0;

/* ══════════════════ 13 · HUD ══════════════════ */
const clockEl=document.getElementById('clock'),hourOut=document.getElementById('hourOut'),
  phaseEl=document.getElementById('phase'),seaOut=document.getElementById('seaOut'),
  windVal=document.getElementById('windVal'),tideVal=document.getElementById('tideVal'),
  fpsVal=document.getElementById('fpsVal'),voxEl=document.getElementById('vox'),
  needle=document.getElementById('needle'),tip=document.getElementById('tip'),
  logList=document.getElementById('logList'),chipsEl=document.getElementById('chips'),
  sailBtn=document.getElementById('sailBtn'),rigBtn=document.getElementById('rigBtn'),
  orbitBtn=document.getElementById('orbitBtn');
const SEA_WORDS=['Glassy','Light','Moderate','Fresh','Gale'];
let seaState=1.2;
function syncFill(el){const p=(el.value-el.min)/(el.max-el.min)*100;el.style.setProperty('--p',p+'%');}
const hourEl=document.getElementById('hour'),seaEl=document.getElementById('sea');
[syncFill(hourEl),syncFill(seaEl)];
hourEl.addEventListener('input',()=>{syncFill(hourEl);applyLight(+hourEl.value);});
seaEl.addEventListener('input',()=>{
  syncFill(seaEl);seaState=+seaEl.value;
  seaOut.textContent=SEA_WORDS[Math.min(4,Math.round(seaState))];
  windVal.textContent='SW '+Math.round(4+seaState*11);
  needle.style.transform='rotate('+(215+Math.sin(performance.now()/900)*4+seaState*2)+'deg)';
});
SPOTS.forEach((s,i)=>{
  const li=document.createElement('li');
  li.innerHTML=`<span class="t">${s.t}</span><span class="n">${s.n}</span>`;
  li.addEventListener('mouseenter',()=>focusSpot(i,true));
  li.addEventListener('mouseleave',()=>focusSpot(i,false));
  li.addEventListener('click',()=>flyTo(i));
  logList.appendChild(li);
});
const VIEWS=[
  {n:'Roads',p:[-52,27,-38],t:[-2,9,2]},
  {n:'Quayside',p:[15,8.4,14],t:[-4,11,-6]},
  {n:'Masthead',p:[10,34,-13],t:[-3,12,0]},
  {n:'The Mouth',p:[-40,16,-8],t:[-25,12,6]},
  {n:'Town Hill',p:[42,24,26],t:[4,6,0]},
];
const spotView={0:[-34,12,-30,-18,1,-8],3:[-40,16,-8,-25,12,6],2:[-26,20,-30,-3,12,-2],
  1:[-38,14,24,-24,10,10],4:[-2,10,16,16,10,6],5:[8,12,20,28,14,4],6:[6,10,4,18,9,18],7:[22,14,34,30,10,20]};
VIEWS.forEach((v,i)=>{
  const b=document.createElement('button');b.className='chip'+(i===0?' on':'');b.textContent=v.n;
  b.onclick=()=>{document.querySelectorAll('.chip').forEach(c=>c.classList.remove('on'));
    b.classList.add('on');fly(v.p,v.t);};
  chipsEl.appendChild(b);
});
let tween=null;
function fly(p,t){
  tween={t0:performance.now(),dur:1500,
    fp:camera.position.clone(),tp:new THREE.Vector3(...p),
    ft:controls.target.clone(),tt:new THREE.Vector3(...t)};
  controls.autoRotate=false;orbitBtn.dataset.on='0';orbitBtn.textContent='Auto‑orbit';
}
function flyTo(i){
  const v=spotView[i]||[ -40,24,-30,0,9,0 ];
  fly([v[0],v[1],v[2]],[v[3],v[4],v[5]]);
}
sailBtn.onclick=()=>{const on=sailBtn.dataset.on==='1'?'0':'1';sailBtn.dataset.on=on;
  sailBtn.textContent=on==='1'?'Sails set':'Sails furled';
  if(shipSailMesh)shipSailMesh.visible=on==='1';
  if(shipFurlMesh)shipFurlMesh.visible=on!=='1';
  if(jibMesh)jibMesh.visible=on==='1';};
rigBtn.onclick=()=>{const on=rigBtn.dataset.on==='1'?'0':'1';rigBtn.dataset.on=on;
  rigBtn.textContent=on==='1'?'Rigging':'Rigging off';if(rigLines)rigLines.visible=on==='1';};
orbitBtn.onclick=()=>{const on=orbitBtn.dataset.on==='1'?'0':'1';orbitBtn.dataset.on=on;
  orbitBtn.textContent=on==='1'?'Auto‑orbit':'Auto‑orbit';controls.autoRotate=on==='1';};
let hovered=-1;
function focusSpot(i,on){
  spotMarks[i].visible=on;
  logList.children[i].classList.toggle('hl',on);
  hovered=on?i:(hovered===i?-1:hovered);
  if(on){tip.querySelector('b').textContent=SPOTS[i].h;
    tip.querySelector('s').textContent=SPOTS[i].d;tip.classList.add('on');}
  else tip.classList.remove('on');
}
addEventListener('pointermove',e=>{
  pointer.set(e.clientX,innerHeight-e.clientY);
  tip.style.left=e.clientX+'px';tip.style.top=(e.clientY-14)+'px';
  pointerDirty=true;
});
const ray=new THREE.Raycaster(),pointer=new THREE.Vector2();
let pointerDirty=false;
function doHover(){
  if(!pointerDirty)return;pointerDirty=false;
  ray.setFromCamera(new THREE.Vector2((pointer.x/innerWidth)*2-1,(pointer.y/innerHeight)*2-1),camera);
  const hit=ray.intersectObjects(hitMeshes,false);
  const idx=hit.length?hit[0].object.userData.i:-1;
  if(idx!==hovered){
    if(hovered>=0)focusSpot(hovered,false);
    if(idx>=0)focusSpot(idx,true);
  }
}

/* ══════════════════ 14 · assemble ══════════════════ */
let shipRoot,shipTilt,shipYawG,shipSailMesh,shipFurlMesh,jibMesh,buoyG=[];
function assemble(){
  buildTerrain();
  buildBreakwater();
  buildTown();
  buildQuayProps();
  buildSmallStuff();
  buildClock();
  /* world meshes */
  const wS=bake(W.solid,matSolid); scene.add(wS);
  const wG=bake(W.glow,matBasic,false); scene.add(wG); glowBatches.push(wG);
  buildWater();
  buildShip();
  shipRoot=new THREE.Group(); shipRoot.position.set(SHIP_X,0,SHIP_Z);
  shipYawG=new THREE.Group(); shipYawG.rotation.y=YAW;
  shipTilt=new THREE.Group();
  shipRoot.add(shipYawG); shipYawG.add(shipTilt); scene.add(shipRoot);
  shipTilt.add(bake(SH.solid,matSolid));
  const sg=bake(SH.glow,matBasic,false); shipTilt.add(sg); glowBatches.push(sg);
  shipSailMesh=bake(SH.sail,matSail); shipTilt.add(shipSailMesh);
  shipFurlMesh=bake(SH.furled,matSail); shipFurlMesh.visible=false; shipTilt.add(shipFurlMesh);
  shipTilt.add(rigLines);
  /* mooring hawsers + anchor chain (world space) */
  const ropeMat=new THREE.MeshLambertMaterial({color:0xb59b6c});
  const hawser=(a,b,sag)=>{
    const mid=a.clone().lerp(b,.5); mid.y-=sag;
    const curve=new THREE.CatmullRomCurve3([a,mid,b]);
    const m=new THREE.Mesh(new THREE.TubeGeometry(curve,20,.17,5,false),ropeMat);
    m.castShadow=true; scene.add(m);};
  hawser(shipW(5.2,8.5,13),new THREE.Vector3(11,7.6,-12),1.2);
  hawser(shipW(5.2,8.5,-13),new THREE.Vector3(11,7.6,12),1.3);
  hawser(shipW(5.5,7.2,2),new THREE.Vector3(11,7.6,0),.9);
  const chain=[shipW(0,6,21),new THREE.Vector3(-3+3,2,10),new THREE.Vector3(-3+7,-1,18),
               new THREE.Vector3(-3+9,-3,26)];
  const cm=new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(chain),26,.18,4,false),
    new THREE.MeshLambertMaterial({color:0x33383d}));
  scene.add(cm);
  /* flags */
  shipTilt.add(makeFlag([0,13.5,-20],[0,0,-1],5,4,[0xb04434,0xd8cfb8],1.2));
  shipTilt.add(makeFlag([0,30.4,0],[0,0,1],4,1,[0x3a5f8a],2.4));
  shipTilt.add(makeFlag([0,28.4,11],[0,0,1],4,1,[0xd8cfb8],4.1));
  buildGulls(); buildSmoke(); buildSpots();
  /* lighthouse beam */
  beamPivot=new THREE.Group(); beamPivot.position.set(-26,lighthouseY,6); scene.add(beamPivot);
  const beamMat=new THREE.MeshBasicMaterial({color:0xffe9bf,transparent:true,opacity:.11,
    blending:THREE.AdditiveBlending,depthWrite:false,side:THREE.DoubleSide});
  for(const s of[0,Math.PI]){
    const cone=new THREE.Mesh(new THREE.ConeGeometry(6,44,14,1,true),beamMat);
    cone.rotation.z=-Math.PI/2; cone.position.set(s===0?22:-22,0,0);
    if(s!==0) cone.rotation.z=Math.PI/2;
    beamPivot.add(cone);
  }
  const lamp=new THREE.PointLight(0xffcf8a,0,80,2); lamp.position.set(-26,lighthouseY+1,6);
  scene.add(lamp); beamLamp=lamp;
  const qL=new THREE.PointLight(0xffc070,0,26,2); qL.position.set(13,11,-7); scene.add(qL);
  quayLamp=qL;
  voxEl.textContent=stats.vox.toLocaleString('en-US');
}
let beamPivot=null,beamLamp=null,quayLamp=null;

/* ══════════════════ 15 · loop ══════════════════ */
const clock=new THREE.Clock();
let frames=0,fpsT=0;
function animate(){
  requestAnimationFrame(animate);
  const dt=Math.min(clock.getDelta(),.05),t=clock.elapsedTime;
  waterU.uTime.value=t;
  const amp=.16+seaState*.16;
  waterU.uAmp.value+=(amp-waterU.uAmp.value)*.04;
  waterU.uWind.value=clamp(seaState/4,0,1);
  /* ship rides the swell */
  if(shipRoot){
    const h=wave(SHIP_X,SHIP_Z,t,waterU.uAmp.value);
    const hx=wave(SHIP_X+3,SHIP_Z,t,waterU.uAmp.value), hz=wave(SHIP_X,SHIP_Z+3,t,waterU.uAmp.value);
    shipRoot.position.y=h*.95;
    shipTilt.rotation.z+=((-hx*0.09)-shipTilt.rotation.z)*.06;
    shipTilt.rotation.x+=((hz*0.055)-shipTilt.rotation.x)*.06;
    shipTilt.rotation.z+=Math.sin(t*.53)*.0035;
  }
  for(const b of buoys){
    b.position.y=wave(b.position.x,b.position.z,t,waterU.uAmp.value)*1.15;
    b.rotation.z=Math.sin(t*1.1+b.position.x)*.12; b.rotation.x=Math.cos(t*.9+b.position.z)*.1;
  }
  if(smack){
    smack.position.y=wave(smack.position.x,smack.position.z,t,waterU.uAmp.value)*1.05;
    smack.rotation.z=Math.sin(t*.7+2)*.06;
  }
  updateFlags(t);
  if(beamPivot) beamPivot.rotation.y=t*.62;
  if(beamLamp) beamLamp.intensity=lampOn*2.4;
  if(quayLamp) quayLamp.intensity=lampOn*1.1;
  if(windmill) windmill.rotation.x=t*(.25+seaState*.28);
  /* gulls */
  for(const g of gulls){
    const u=g.userData,a=t*u.sp+u.ph;
    const rr=u.r+Math.sin(t*.21+u.ph)*6;
    g.position.set(u.cx+Math.cos(a)*rr,u.y+Math.sin(t*.9+u.ph)*2.2,u.cz+Math.sin(a)*rr*.75);
    g.rotation.y=-a+Math.PI/2;
    const flap=Math.sin(t*7+u.ph)*.75;
    u.wl.rotation.z=flap; u.wr.rotation.z=-flap;
  }
  /* smoke */
  if(smoke){
    for(let i=0;i<smokeN;i++){
      const p=smokeP[i]; if(!p) continue;
      p.age+=dt;
      if(p.age>p.life) respawnSmoke(i,false);
      const k=p.age/p.life;
      p.x+=p.vx*dt*(1+seaState*.5); p.z+=p.vz*dt; p.y+=p.vy*dt*.8;
      dummy.position.set(p.x,p.y,p.z);
      dummy.scale.setScalar(.55+k*2.6);
      dummy.rotation.set(k*2,k,k*.5); dummy.updateMatrix();
      smoke.setMatrixAt(i,dummy.matrix);
      smoke.setColorAt(i,tmpC.copy(skyCol.cloud).lerp(new THREE.Color(0x585858),1-k*.85));
    }
    smoke.instanceMatrix.needsUpdate=true;
    if(smoke.instanceColor) smoke.instanceColor.needsUpdate=true;
  }
  /* hotspot pulse */
  for(let i=0;i<spotMarks.length;i++) if(spotMarks[i].visible){
    const s=1+Math.sin(t*3.4)*.012; spotMarks[i].scale.setScalar(s);
    spotMarks[i].material.opacity=.55+Math.sin(t*3.4)*.3;
  }
  doHover();
  /* camera tween */
  if(tween){
    const k=clamp((performance.now()-tween.t0)/tween.dur,0,1);
    const e=k<.5?4*k*k*k:1-Math.pow(-2*k+2,3)/2;
    camera.position.lerpVectors(tween.fp,tween.tp,e);
    controls.target.lerpVectors(tween.ft,tween.tt,e);
    if(k>=1) tween=null;
  }
  controls.update();
  renderer.render(scene,camera);
  frames++;
  if(performance.now()-fpsT>700){fpsVal.textContent=Math.round(frames*1000/(performance.now()-fpsT));
    frames=0;fpsT=performance.now();}
}

/* ══════════════════ 16 · boot ══════════════════ */
addEventListener('resize',()=>{
  camera.aspect=innerWidth/innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight);
});
setTimeout(()=>{
  assemble();
  applyLight(+hourEl.value);
  seaOut.textContent=SEA_WORDS[Math.round(seaState)];
  needle.style.transform='rotate(215deg)';
  renderer.render(scene,camera);
  animate();
  setTimeout(()=>document.getElementById('load').classList.add('off'),260);
},40);
</script>
</body>
</html>
```

**What's in there**

- **Culled voxel engine** — every structure is written into a `Map`, fully‑enclosed voxels are dropped, and each material group becomes a single `InstancedMesh` (one draw call for the world, one for lamps/windows, one for the hull, one for sails, one for the sea).
- **Animated sea** in a custom vertex/fragment shader hooked into `MeshStandardMaterial`: swells displace the voxel columns, normals are re-derived analytically, crests and baked foam rings (quay wall, breakwater, and a foam collar hugging the hull) lighten the surface.
- **The ship floats on the same wave function** the shader uses — heave plus pitch/roll from the sampled gradient; buoys and the fishing smack ride it too.
- **Living details** — rotating lighthouse beam and point light, chimney smoke drifting with the sea state, circling gulls with flapping wings, a windmill, waving ensign and pennants, a tower clock whose hands show the slider time, gulls, hanging cargo.
- **Harbour time keyframes** drive the sun vector, sky gradient + sun disc + stars, fog, sea colours, cloud tint, exposure — and windows dim to slate glass in daylight, warm amber at dusk, with additive lamp halos.
- **Harbour Log ↔ scene linking**: hovering the 3D or the list highlights a pulsing bounding marker and a tooltip; clicking flies the camera. Five camera presets, damped orbit, auto‑orbit that yields to your first drag.