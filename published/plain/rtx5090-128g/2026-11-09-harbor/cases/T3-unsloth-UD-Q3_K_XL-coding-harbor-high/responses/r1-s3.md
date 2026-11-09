# Port Meridian — a voxel harbour diorama

Everything below is one self-contained HTML file. Save it as `harbour.html`, open it in Chrome. It builds a real 3D voxel scene (no sprites, no images — every cube is generated at load time), renders it, and hands you the mouse: **drag to orbit, scroll to zoom, right-drag to pan.**

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
<title>Port Meridian — a sailing ship calling at a harbour</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Alfa+Slab+One&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root{
    --ink:#07131c; --ink2:#0d1e2b; --ink3:#132a39;
    --paper:#f4e9d6; --paper-dim:#c8bdb0;
    --brass:#e3a94c; --brass-dim:#a97b33;
    --sea:#67c1cf; --rust:#c1552f;
    --line:rgba(227,169,76,.32);
    --panel: linear-gradient(180deg, rgba(13,30,43,.93), rgba(7,19,28,.96));
    --bev: polygon(0 0, calc(100% - 15px) 0, 100% 15px, 100% 100%, 15px 100%, 0 calc(100% - 15px));
  }
  *{box-sizing:border-box;margin:0;padding:0}
  html,body{height:100%;overflow:hidden;background:#07131c;color:var(--paper);
    font-family:"IBM Plex Sans",system-ui,sans-serif;-webkit-font-smoothing:antialiased}
  canvas{display:block;position:fixed;inset:0}

  #ui{position:fixed;inset:0;pointer-events:none;z-index:5}
  .plate{position:absolute;pointer-events:auto;background:var(--panel);
    border:1px solid var(--line);clip-path:var(--bev);
    box-shadow:0 18px 50px rgba(0,0,0,.55), inset 0 1px 0 rgba(255,225,180,.07);
    opacity:0;transform:translateY(14px);transition:opacity .7s ease,transform .7s cubic-bezier(.16,.9,.28,1)}
  body.ready .plate{opacity:1;transform:none}
  body.ready .plate.d1{transition-delay:.05s} body.ready .plate.d2{transition-delay:.16s}
  body.ready .plate.d3{transition-delay:.28s} body.ready .plate.d4{transition-delay:.40s}

  /* ── nameplate ─────────────────────────────── */
  #nameplate{top:22px;left:24px;display:flex;align-items:stretch;gap:0}
  #nameplate .crest{width:64px;display:grid;place-items:center;border-right:1px solid var(--line);
    font-size:26px;color:var(--brass);text-shadow:0 0 18px rgba(227,169,76,.45)}
  #nameplate .txt{padding:12px 22px 12px 18px}
  h1{font-family:"Alfa Slab One",Georgia,serif;font-weight:400;letter-spacing:-.6px;
    font-size:clamp(23px,3.1vw,38px);line-height:.94;color:#fff6e6}
  h1 span{display:block;font-size:.42em;letter-spacing:.02em;color:var(--brass);margin-top:7px}
  .sub{font-family:"IBM Plex Mono",monospace;font-size:10.5px;letter-spacing:.24em;
    text-transform:uppercase;color:var(--paper-dim);margin-top:9px;opacity:.8}
  #clockbox{border-left:1px solid var(--line);padding:12px 18px;text-align:right;min-width:112px}
  #clock{font-family:"IBM Plex Mono",monospace;font-size:26px;font-weight:500;color:#fff}
  #phase{display:block;font-family:"IBM Plex Mono",monospace;font-size:9.5px;letter-spacing:.2em;
    color:var(--brass);text-transform:uppercase;margin-top:4px}

  /* ── harbour log ───────────────────────────── */
  #log{top:152px;left:24px;width:318px;padding:16px 18px 14px}
  #log h2,#dock h2{font-family:"IBM Plex Mono",monospace;font-size:10px;letter-spacing:.28em;
    text-transform:uppercase;color:var(--brass);display:flex;align-items:center;gap:10px;margin-bottom:12px}
  #log h2:after,#dock h2:after{content:"";flex:1;height:1px;background:linear-gradient(90deg,var(--line),transparent)}
  #log ul{list-style:none}
  #log li{display:grid;grid-template-columns:46px 1fr;gap:10px;font-size:12.6px;line-height:1.45;
    padding:7px 8px 7px 0;border-left:1px solid rgba(227,169,76,.18);padding-left:11px;
    transition:border-color .25s,background .25s,transform .25s;color:#ded3c4}
  #log li:hover{border-left-color:var(--brass);background:rgba(227,169,76,.07);transform:translateX(3px)}
  #log li b{font-family:"IBM Plex Mono",monospace;font-weight:500;font-size:11px;color:var(--brass)}
  #log li i{color:#fff;font-style:italic}
  .readout{display:grid;grid-template-columns:1fr 1fr;gap:1px;margin-top:14px;
    background:rgba(227,169,76,.14);border:1px solid rgba(227,169,76,.14)}
  .readout div{background:#081620;padding:8px 10px}
  .readout span{display:block;font-family:"IBM Plex Mono",monospace;font-size:9px;letter-spacing:.18em;
    text-transform:uppercase;color:#7f8f9b}
  .readout b{font-family:"IBM Plex Mono",monospace;font-size:14px;font-weight:500;color:#ffeccb}
  #barwrap{margin-top:12px}
  #barwrap .lab{display:flex;justify-content:space-between;font-family:"IBM Plex Mono",monospace;
    font-size:9px;letter-spacing:.16em;text-transform:uppercase;color:#7f8f9b;margin-bottom:5px}
  #tidebar{height:7px;background:#0b1a24;border:1px solid rgba(227,169,76,.2);position:relative;overflow:hidden}
  #tidebar i{position:absolute;inset:2px auto 2px 0;background:linear-gradient(90deg,#1d5f74,#67c1cf);
    transition:width .5s cubic-bezier(.3,.9,.3,1)}
  #tidebar:after{content:"";position:absolute;top:0;bottom:0;left:50%;width:1px;background:rgba(255,255,255,.25)}

  /* ── control dock ──────────────────────────── */
  #dock{left:24px;bottom:24px;padding:14px 16px 15px;max-width:min(760px,calc(100vw - 48px))}
  .dockrow{display:flex;flex-wrap:wrap;align-items:center;gap:9px;margin-top:12px}
  .sliderline{display:flex;align-items:center;gap:14px}
  input[type=range]{-webkit-appearance:none;appearance:none;width:min(330px,52vw);height:22px;background:transparent;cursor:ew-resize}
  input[type=range]::-webkit-slider-runnable-track{height:4px;
    background:linear-gradient(90deg,var(--brass) var(--p,48%),rgba(255,255,255,.13) var(--p,48%))}
  input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:15px;height:15px;margin-top:-5.5px;
    background:#ffe6b4;border:2px solid #6b4a17;border-radius:50%;box-shadow:0 0 12px rgba(227,169,76,.8);
    transition:transform .15s}
  input[type=range]:hover::-webkit-slider-thumb{transform:scale(1.18)}
  input[type=range]::-moz-range-track{height:4px;background:rgba(255,255,255,.13)}
  input[type=range]::-moz-range-thumb{width:14px;height:14px;border:2px solid #6b4a17;background:#ffe6b4;border-radius:50%}
  .ticks{display:flex;justify-content:space-between;width:min(330px,52vw);font-family:"IBM Plex Mono",monospace;
    font-size:8.5px;letter-spacing:.14em;text-transform:uppercase;color:#6d7d88;margin-top:-4px}
  .ticks b{color:var(--brass);font-weight:500;transition:color .2s}
  button{pointer-events:auto;font-family:"IBM Plex Mono",monospace;font-size:10.5px;letter-spacing:.14em;
    text-transform:uppercase;color:#dfe8ee;background:#0b1a25;border:1px solid rgba(255,255,255,.12);
    padding:9px 13px 9px 11px;display:inline-flex;align-items:center;gap:8px;cursor:pointer;
    transition:transform .18s cubic-bezier(.2,.9,.3,1),border-color .2s,color .2s,background .2s;
    clip-path:polygon(0 0,calc(100% - 8px) 0,100% 8px,100% 100%,8px 100%,0 calc(100% - 8px))}
  button:hover{transform:translateY(-2px);border-color:var(--brass);color:#fff;background:#122636}
  button .led{width:7px;height:7px;border-radius:50%;background:#334753;box-shadow:none;transition:.2s}
  button.on{color:#fff;border-color:rgba(227,169,76,.5)}
  button.on .led{background:var(--brass);box-shadow:0 0 9px 1px rgba(227,169,76,.85)}
  button.ghost{background:transparent;color:#9fb0ba}
  button.ghost:hover{color:#fff}

  /* ── compass + hint + tip ──────────────────── */
  #compass{position:absolute;right:26px;top:22px;width:104px;height:104px;pointer-events:none;
    opacity:0;transition:opacity .9s ease .5s}
  body.ready #compass{opacity:.92}
  #compass svg{width:100%;height:100%;overflow:visible}
  #needle{transform-origin:52px 52px;transition:transform .12s linear}
  #hint{position:absolute;right:28px;bottom:26px;text-align:right;font-family:"IBM Plex Mono",monospace;
    font-size:10px;letter-spacing:.16em;text-transform:uppercase;color:#7c8b95;opacity:0;transition:opacity .8s ease .8s}
  body.ready #hint{opacity:1}
  #hint b{color:var(--brass);font-weight:500}
  #tip{position:absolute;left:0;top:0;pointer-events:none;transform:translate(-50%,-140%);
    background:rgba(7,19,28,.94);border:1px solid var(--line);padding:8px 12px;opacity:0;
    transition:opacity .18s ease,transform .18s ease;max-width:230px}
  #tip.on{opacity:1;transform:translate(-50%,-160%)}
  #tip b{display:block;font-family:"Alfa Slab One",serif;font-size:13px;font-weight:400;color:#fff3dd;letter-spacing:.01em}
  #tip i{display:block;font-style:normal;font-size:11px;color:#9fb0ba;margin-top:3px;line-height:1.35}
  #tip:after{content:"";position:absolute;left:50%;bottom:-5px;width:9px;height:9px;margin-left:-4.5px;
    background:rgba(7,19,28,.94);border-right:1px solid var(--line);border-bottom:1px solid var(--line);transform:rotate(45deg)}

  /* ── loader ────────────────────────────────── */
  #loader{position:fixed;inset:0;z-index:30;background:radial-gradient(1200px 700px at 60% 40%,#123044,#050d14 70%);
    display:grid;place-items:center;transition:opacity .9s ease,visibility .9s}
  #loader.gone{opacity:0;visibility:hidden}
  .lwrap{width:min(420px,84vw);text-align:left}
  .lmark{font-family:"Alfa Slab One",Georgia,serif;font-size:clamp(34px,7vw,58px);line-height:.92;color:#fff6e6;
    letter-spacing:-1px;text-shadow:0 12px 40px rgba(0,0,0,.6)}
  .lsub{font-family:"IBM Plex Mono",monospace;font-size:10px;letter-spacing:.34em;text-transform:uppercase;
    color:var(--brass);margin:14px 0 26px}
  .lbar{height:2px;background:rgba(255,255,255,.1);position:relative;overflow:hidden}
  .lbar i{position:absolute;left:0;top:0;bottom:0;width:0;background:var(--brass);
    box-shadow:0 0 14px rgba(227,169,76,.9);transition:width .35s cubic-bezier(.4,.8,.3,1)}
  .lstat{font-family:"IBM Plex Mono",monospace;font-size:10.5px;letter-spacing:.14em;color:#8fa0ab;margin-top:12px}
  .lstat b{color:var(--paper);font-weight:400}

  @media (max-width:900px){ #log{display:none} #compass{display:none} }
  @media (max-width:640px){
    #nameplate{top:10px;left:10px} #clockbox{display:none}
    #dock{left:10px;bottom:10px;right:10px;max-width:none;padding:12px}
    .dockrow{gap:7px} button{padding:8px 9px;font-size:9px}
    #hint{display:none}
  }
</style>
</head>
<body>

<div id="ui">
  <header class="plate d1" id="nameplate">
    <div class="crest">⚓</div>
    <div class="txt">
      <h1>Port Meridian<span>the barque “Aurora” calls</span></h1>
      <p class="sub">voxel diorama · grid 1 : 400 · harbour view no.7</p>
    </div>
    <div id="clockbox"><span id="clock">16:54</span><em id="phase">golden hour</em></div>
  </header>

  <aside class="plate d2" id="log">
    <h2>Harbour log</h2>
    <ul>
      <li><b>15:58</b><div>Sig. from <i>Aurora of Whitby</i> — three miles ESE, bound in.</div></li>
      <li><b>16:31</b><div>Pilot aboard at the bar. Light air, SW. Flood making.</div></li>
      <li><b>16:54</b><div>Round the lighthouse. Her courses are still full.</div></li>
      <li><b>16:57</b><div>Lines thrown — <i>make fast to Number Three Jetty.</i></div></li>
    </ul>
    <div class="readout">
      <div><span>Wind</span><b id="rWind">SW 9 kn</b></div>
      <div><span>Tide</span><b id="rTide">+1.42 m</b></div>
      <div><span>Voxels built</span><b id="rVox">—</b></div>
      <div><span>Frames</span><b id="rFps">—</b></div>
    </div>
    <div id="barwrap">
      <div class="lab"><span>chart datum</span><span>high water 19:20</span></div>
      <div id="tidebar"><i style="width:70%"></i></div>
    </div>
  </aside>

  <div class="plate d3" id="dock">
    <h2>Watch table</h2>
    <div class="sliderline">
      <input id="tod" type="range" min="0" max="1000" value="470" aria-label="time of day">
      <div class="ticks"><b data-t="0">dawn</b><b data-t="240">noon</b><b data-t="480">golden</b><b data-t="620">dusk</b><b data-t="800">night</b></div>
    </div>
    <div class="dockrow">
      <button class="on" data-act="sails"><i class="led"></i><span>Sails full</span></button>
      <button class="on" data-act="light"><i class="led"></i><span>Light</span></button>
      <button class="on" data-act="gulls"><i class="led"></i><span>Gulls</span></button>
      <button class="on" data-act="cycle"><i class="led"></i><span>Sun cycle</span></button>
      <button class="on" data-act="orbit"><i class="led"></i><span>Auto-orbit</span></button>
      <button class="ghost" data-act="reset"><i class="led"></i><span>Reset view</span></button>
    </div>
  </div>

  <div id="compass">
    <svg viewBox="0 0 104 104">
      <circle cx="52" cy="52" r="40" fill="rgba(7,19,28,.55)" stroke="rgba(227,169,76,.35)"/>
      <circle cx="52" cy="52" r="31" fill="none" stroke="rgba(227,169,76,.16)"/>
      <g font-family="IBM Plex Mono, monospace" font-size="9" fill="#c8bdb0" text-anchor="middle">
        <text x="52" y="14">N</text><text x="94" y="56">E</text><text x="52" y="102">S</text><text x="10" y="56">W</text>
      </g>
      <g id="needle">
        <path d="M52 20 L58 52 L52 46 L46 52 Z" fill="#e3a94c"/>
        <path d="M52 84 L46 52 L52 58 L58 52 Z" fill="#4d6472"/>
      </g>
      <circle cx="52" cy="52" r="3" fill="#0d1e2b" stroke="#e3a94c"/>
    </svg>
  </div>

  <p id="hint"><b>drag</b> orbit · <b>scroll</b> zoom · <b>right-drag</b> pan · hover the scene</p>
  <div id="tip"><b></b><i></i></div>
</div>

<div id="loader">
  <div class="lwrap">
    <div class="lmark">Port Meridian</div>
    <div class="lsub">building the harbour, one cube at a time</div>
    <div class="lbar"><i id="lfill"></i></div>
    <div class="lstat" id="lstat">rigging the toolchain…</div>
  </div>
</div>

<script type="importmap">
{ "imports": {
  "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
  "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
}}
</script>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* ══════════════════════════════════════════════════════════════
   0 · plumbing: renderer, scene, camera, deterministic RNG
   ══════════════════════════════════════════════════════════════ */
const renderer = new THREE.WebGLRenderer({ antialias:true, powerPreference:'high-performance' });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.02;
renderer.setClearColor(0x0a1a26);
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
const fogCol = new THREE.Color(0xdc9a6a);
scene.fog = new THREE.FogExp2(fogCol.getHex(), 0.0072);

const camera = new THREE.PerspectiveCamera(42, innerWidth/innerHeight, 0.6, 2600);
const CAM_A = new THREE.Vector3(58, 31, 66), TGT_A = new THREE.Vector3(-4, 9, -4);
camera.position.set(126, 74, 138);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true; controls.dampingFactor = .06;
controls.minDistance = 20; controls.maxDistance = 265;
controls.maxPolarAngle = 1.485; controls.target.copy(TGT_A);
controls.enabled = false;

let seed = 20240707;
const rnd = () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0;
  let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
  t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
  return ((t ^ t >>> 14) >>> 0) / 4294967296; };
const hash3 = (x,y,z) => { let h = x*374761393 + y*668265263 + z*1274126177;
  h = (h ^ (h >> 13)) * 1274126177; return ((h ^ (h >> 16)) >>> 0) / 4294967295; };
const rr = (a,b) => a + rnd()*(b-a);

/* ══════════════════════════════════════════════════════════════
   1 · the voxel builder — occupancy set + hidden-face culling
   ══════════════════════════════════════════════════════════════ */
class Vox {
  constructor(){ this.map = new Set(); this.list = []; }
  k(x,y,z){ return ((x+1024)<<22) | ((y+1024)<<11) | (z+1024); }
  has(x,y,z){ return this.map.has(this.k(x,y,z)); }
  set(x,y,z,c){
    x=Math.round(x); y=Math.round(y); z=Math.round(z);
    const k=this.k(x,y,z);
    if(this.map.has(k)) return;
    this.map.add(k); this.list.push([x,y,z, Array.isArray(c)? c[(rnd()*c.length)|0] : c]);
  }
  box(x0,x1,y0,y1,z0,z1,c){ for(let x=x0;x<=x1;x++)for(let y=y0;y<=y1;y++)for(let z=z0;z<=z1;z++) this.set(x,y,z,c); }
  /* hollow block — cheap way to lay huge slabs of stone */
  block(x0,x1,y0,y1,z0,z1,c){
    for(let x=x0;x<=x1;x++) for(let y=y0;y<=y1;y++){ this.set(x,y,z0,c); this.set(x,y,z1,c); }
    for(let x=x0;x<=x1;x++) for(let z=z0;z<=z1;z++){ this.set(x,y0,z,c); this.set(x,y1,z,c); }
    for(let y=y0;y<=y1;y++) for(let z=z0;z<=z1;z++){ this.set(x0,y,z,c); this.set(x1,y,z,c); }
  }
  cyl(cx,cz,y0,y1,r,c,fill=true){
    const R=Math.max(.55,r), r2=R*R;
    for(let y=y0;y<=y1;y++) for(let dx=-Math.ceil(R);dx<=Math.ceil(R);dx++) for(let dz=-Math.ceil(R);dz<=Math.ceil(R);dz++){
      const d=dx*dx+dz*dz; if(d>r2) continue;
      if(!fill && d < r2-R*2.2) continue;
      this.set(cx+dx,y,cz+dz,c);
    }
  }
  ball(cx,cy,cz,r,c){ const r2=r*r;
    for(let dx=-r;dx<=r;dx++)for(let dy=-r;dy<=r;dy++)for(let dz=-r;dz<=r;dz++)
      if(dx*dx+dy*dy+dz*dz<=r2) this.set(cx+dx,cy+dy,cz+dz,c); }
  line(x0,y0,z0,x1,y1,z1,c,thick=1){
    const n=Math.ceil(Math.max(Math.abs(x1-x0),Math.abs(y1-y0),Math.abs(z1-z0)))||1;
    for(let i=0;i<=n;i++){ const t=i/n, x=x0+(x1-x0)*t, y=y0+(y1-y0)*t, z=z0+(z1-z0)*t;
      if(thick<=1) this.set(x,y,z,c);
      else { const R=(thick-1)/2;
        for(let dx=-R;dx<=R;dx++)for(let dy=-R;dy<=R;dy++)for(let dz=-R;dz<=R;dz++)
          if(Math.abs(dx)+Math.abs(dy)+Math.abs(dz)<=R+1) this.set(x+dx,y+dy,z+dz,c); } }
  }
  /* gabled roof: runs along z, ridge parallel to z */
  roof(x0,x1,y0,z0,z1,h,c,darkc){
    const half=(x1-x0)/2;
    for(let l=0;l<=half;l++){
      const y=y0+l, xa=Math.round(x0+l), xb=Math.round(x1-l);
      for(let z=z0;z<=z1;z++){ this.set(xa,y,z,l%2?c:darkc); if(xb!==xa) this.set(xb,y,z,l%2?c:darkc); }
      if(xa===xb) continue;
    }
  }
  gable(z,x0,x1,y0,ytop,c){
    for(let y=y0;y<=ytop;y++){ const inset=y-y0;
      for(let x=x0+inset;x<=x1-inset;x++) this.set(x,y,z,c); }
  }
}

const FACES = [
  { dir:[ 1, 0, 0], sh:.80, c:[[1,0,0],[1,1,0],[1,0,1],[1,1,1]] },
  { dir:[-1, 0, 0], sh:.80, c:[[0,1,0],[0,0,0],[0,1,1],[0,0,1]] },
  { dir:[ 0, 1, 0], sh:1.0, c:[[0,1,1],[1,1,1],[0,1,0],[1,1,0]] },
  { dir:[ 0,-1, 0], sh:.44, c:[[1,0,1],[0,0,1],[1,0,0],[0,0,0]] },
  { dir:[ 0, 0, 1], sh:.72, c:[[0,0,1],[1,0,1],[0,1,1],[1,1,1]] },
  { dir:[ 0, 0,-1], sh:.72, c:[[1,0,0],[0,0,0],[1,1,0],[0,1,0]] },
];
const cTmp = new THREE.Color();
function bake(vox, jitter=.085){
  const P=[], N=[], C=[], idx=[]; let v=0;
  for(let i=0;i<vox.list.length;i++){
    const q=vox.list[i], x=q[0], y=q[1], z=q[2];
    const jr=(hash3(x,y,z)-.5)*jitter;
    for(let f=0;f<6;f++){
      const F=FACES[f];
      if(vox.has(x+F.dir[0], y+F.dir[1], z+F.dir[2])) continue;
      const s=F.sh*(1+jr)*(1+(hash3(x*3+f*17,y*7,z*11)-.5)*jitter);
      cTmp.setHex(q[3]).multiplyScalar(s);
      for(let k=0;k<4;k++){ const p=F.c[k];
        P.push(x+p[0]-.5, y+p[1]-.5, z+p[2]-.5);
        N.push(F.dir[0],F.dir[1],F.dir[2]);
        C.push(cTmp.r,cTmp.g,cTmp.b); }
      idx.push(v,v+1,v+2, v+2,v+1,v+3); v+=4;
    }
  }
  const g=new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(P,3));
  g.setAttribute('normal',   new THREE.Float32BufferAttribute(N,3));
  g.setAttribute('color',    new THREE.Float32BufferAttribute(C,3));
  g.setIndex(idx); g.computeBoundingSphere();
  return g;
}
const matSolid = new THREE.MeshLambertMaterial({ vertexColors:true });
const matLamp  = new THREE.MeshBasicMaterial({ vertexColors:true, toneMapped:false });
function meshOf(g, mat, cast=true, recv=true){
  const m=new THREE.Mesh(g,mat); m.castShadow=cast; m.receiveShadow=recv; return m;
}

/* ══════════════════════════════════════════════════════════════
   2 · palette
   ══════════════════════════════════════════════════════════════ */
const P_ = {
  cobble:[0x6b6f78,0x5c6069,0x767a83,0x626670],
  cobbleHi:[0x82868f,0x757982,0x6a6e77],
  stone:[0x55595f,0x4a4e55,0x5f636b],
  stoneDk:[0x3e4248,0x353a40],
  rock:[0x4d5055,0x43464b,0x585c62,0x3a3d42],
  rockWet:[0x2f3439,0x272c31],
  grass:[0x4d7a3e,0x446f38,0x568244],
  dirt:[0x5b4a37,0x4e3f2f],
  path:[0x7d7365,0x6f665a],
  wood:[0x8a6440,0x7c5836,0x946d47],
  woodDk:[0x5e4429,0x513a23],
  woodGrey:[0x8b8375,0x7c7467,0x999183],
  pitch:[0x2e2620,0x251e19],
  iron:[0x35393e,0x2b2f34],
  rope:[0x8d7a55,0x7d6b4a],
  sail:[0xefe2c4,0xe6d8b8,0xf3e8cd],
  sailRed:[0xb4482f,0xa03f29],
  cream:[0xe2d3ae,0xd6c6a1],
  ochre:[0xc9903f,0xb88136],
  hull:[0x33261e,0x2a1f19],
  hullRed:[0x8b3f2f,0x7a3527],
  brick:[0x8a4a38,0x7c4030,0x94523e],
  slate:[0x4a4f57,0x40454c,0x545a63],
  stucco:[0xcdbfa4,0xc0b298,0xd8caae],
  stucco2:[0xa8907a,0x9b8571],
  door:[0x3d2b1e],
  lamp:[0xffd88a,0xffe6ab],
  flame:[0xffb457],
  red:[0xb0432e,0x9d3a27],
  green:[0x3f6a4b],
  pine:[0x2f5137,0x28452f],
  pineTrunk:[0x4a3626],
  sand:[0x9c8f74,0x8f8369],
  gull:[0xf2efe8,0xd8d4cc],
  fish:[0xb9c4c8,0x9fadb2],
  coats:[0x2f4258,0x6b3a2c,0x3c4c3a,0x55402c,0x2b3a44],
  skin:[0xd9a878,0xc2905f],
  cloud:[0xf6e6cf,0xe8d6bd,0xffd9b8],
  cloudUnder:[0xc9ae97,0xbb9f8a],
};

/* ══════════════════════════════════════════════════════════════
   3 · lights
   ══════════════════════════════════════════════════════════════ */
const hemi = new THREE.HemisphereLight(0x7d8fb0, 0x5a5142, .85); scene.add(hemi);
const amb  = new THREE.AmbientLight(0xffffff, .14); scene.add(amb);
const sun  = new THREE.DirectionalLight(0xffa14a, 2.6);
sun.castShadow = true;
sun.shadow.mapSize.set(2048,2048);
const sc = sun.shadow.camera;
sc.left=-72; sc.right=72; sc.top=72; sc.bottom=-72; sc.near=20; sc.far=400;
sun.shadow.bias=-0.0006; sun.shadow.normalBias=0.55; sun.shadow.radius=1.2;
scene.add(sun); scene.add(sun.target);
const fill = new THREE.DirectionalLight(0x9fc4e8, .3); fill.position.set(-60,50,-40); scene.add(fill);
const sunDir = new THREE.Vector3();

/* shared shader uniforms */
const uTime = { value:0 };

/* ══════════════════════════════════════════════════════════════
   4 · sky, sun, moon, stars
   ══════════════════════════════════════════════════════════════ */
let sky, sunMesh, sunGlow, moonMesh, stars, lampGlowTex;
const lampGlows = [];

function glowTexture(){
  if(lampGlowTex) return lampGlowTex;
  const c=document.createElement('canvas'); c.width=c.height=128;
  const g=c.getContext('2d').createRadialGradient(64,64,0,64,64,64);
  g.addColorStop(0,'rgba(255,238,200,1)'); g.addColorStop(.25,'rgba(255,196,110,.55)');
  g.addColorStop(.55,'rgba(255,150,70,.16)'); g.addColorStop(1,'rgba(255,140,60,0)');
  const ctx=c.getContext('2d'); ctx.fillStyle=g; ctx.fillRect(0,0,128,128);
  lampGlowTex = new THREE.CanvasTexture(c); return lampGlowTex;
}
function addGlow(x,y,z,size,colour=0xffcf88){
  const s=new THREE.Sprite(new THREE.SpriteMaterial({ map:glowTexture(), color:colour,
    transparent:true, blending:THREE.AdditiveBlending, depthWrite:false, toneMapped:false }));
  s.position.set(x,y,z); s.scale.setScalar(size); s.userData={ base:size, ph:rnd()*9 };
  scene.add(s); lampGlows.push(s); return s;
}

function buildSky(){
  sky = new THREE.Mesh(new THREE.SphereGeometry(1100, 32, 18), new THREE.ShaderMaterial({
    side:THREE.BackSide, depthWrite:false, fog:false,
    uniforms:{ uTop:{value:new THREE.Color()}, uMid:{value:new THREE.Color()}, uBot:{value:new THREE.Color()},
               uSunCol:{value:new THREE.Color()}, uSunDir:{value:new THREE.Vector3(0,1,0)}, uUp:{value:1} },
    vertexShader:`varying vec3 vD; void main(){ vD=position; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0); }`,
    fragmentShader:`
      varying vec3 vD; uniform vec3 uTop,uMid,uBot,uSunCol,uSunDir; uniform float uUp;
      void main(){
        vec3 d=normalize(vD); float h=d.y;
        vec3 col=mix(uBot,uMid,smoothstep(-0.05,0.22,h));
        col=mix(col,uTop,smoothstep(0.15,0.78,h));
        float sd=max(dot(d,normalize(uSunDir)),0.0);
        col+=uSunCol*pow(sd,7.0)*0.30*uUp;
        col+=uSunCol*pow(sd,60.0)*0.65*uUp;
        col+=uSunCol*pow(sd,600.0)*1.2*uUp;
        gl_FragColor=vec4(col,1.0);
      }`
  }));
  sky.frustumCulled=false; scene.add(sky);

  /* chunky voxel sun + moon */
  const sv=new Vox(); sv.ball(0,0,0,7,P_.flame);
  sunMesh = meshOf(bake(sv,.05), new THREE.MeshBasicMaterial({toneMapped:false}), false, false);
  scene.add(sunMesh);
  sunGlow = new THREE.Sprite(new THREE.SpriteMaterial({ map:glowTexture(), transparent:true,
    blending:THREE.AdditiveBlending, depthWrite:false, toneMapped:false }));
  sunGlow.scale.setScalar(340); scene.add(sunGlow);

  const mv=new Vox(); mv.ball(0,0,0,6,[0xdfe6ea,0xcfd8dd]);
  mv.set(2,4,4,0xaeb9c0); mv.set(-3,1,4,0xb6c1c7); mv.set(1,-3,4,0xa9b4bb);
  moonMesh = meshOf(bake(mv,.05), new THREE.MeshBasicMaterial({toneMapped:false}), false, false);
  scene.add(moonMesh);

  /* stars */
  const N=900, pos=new Float32Array(N*3);
  for(let i=0;i<N;i++){ const u=rnd()*Math.PI*2, v=Math.acos(rnd()*0.95+0.02), R=950;
    pos[i*3]=Math.sin(v)*Math.cos(u)*R; pos[i*3+1]=Math.cos(v)*R*0.9+40; pos[i*3+2]=Math.sin(v)*Math.sin(u)*R; }
  const sg=new THREE.BufferGeometry(); sg.setAttribute('position', new THREE.BufferAttribute(pos,3));
  stars = new THREE.Points(sg, new THREE.PointsMaterial({ color:0xfff4dd, size:2.2, sizeAttenuation:false,
    transparent:true, opacity:0, depthWrite:false, toneMapped:false }));
  scene.add(stars);
  return 400;
}

/* ══════════════════════════════════════════════════════════════
   5 · sea — two instanced layers sharing one wave function
   ══════════════════════════════════════════════════════════════ */
const WAVE = `
float waveF(vec2 p, float t){
  return sin(p.x*0.225 + t*1.05)*0.30
       + sin(p.y*0.290 - t*0.92)*0.22
       + sin((p.x+p.y)*0.130 + t*0.61)*0.20
       + sin((p.x-p.y*0.7)*0.45 + t*1.8)*0.07;
}`;
const seaTint = { value:new THREE.Color(0x1a405a) };
const foamCol = { value:new THREE.Color(0xffe6cf) };

function seaMaterial(bias){
  const m = new THREE.MeshLambertMaterial({ color:0xffffff });
  m.onBeforeCompile = (sh)=>{
    sh.uniforms.uTime=uTime; sh.uniforms.uTint=seaTint; sh.uniforms.uFoam=foamCol; sh.uniforms.uBias={value:bias};
    sh.vertexShader = sh.vertexShader
      .replace('#include <common>', `#include <common>\nuniform float uTime;\nvarying float vWave;\n${WAVE}`)
      .replace('#include <begin_vertex>', `#include <begin_vertex>
        { vec3 ip = vec3(0.0);
          #ifdef USE_INSTANCING
            ip = instanceMatrix[3].xyz;
          #endif
          float w = waveF(ip.xz, uTime);
          transformed.y += w; vWave = w + ip.y*0.0; }`);
    sh.fragmentShader = sh.fragmentShader
      .replace('#include <common>', `#include <common>\nvarying float vWave;\nuniform vec3 uTint,uFoam;uniform float uBias;`)
      .replace('#include <dithering_fragment>', `#include <dithering_fragment>
        float f = smoothstep(0.30 - uBias, 0.62 - uBias, vWave);
        gl_FragColor.rgb = mix(gl_FragColor.rgb, uFoam, f*0.55);
        gl_FragColor.rgb = mix(gl_FragColor.rgb, uTint, 0.18);`);
  };
  return m;
}
let seaFine, seaCoarse, foamMat;
const seaGrid = { x0:-12, x1:110, z0:-62, z1:62 };
const landAt = (x,z) => worldSolid && worldSolid.has(x,0,z);
let worldSolid = null;

function shallowAt(x,z){
  let s = 0;
  s = Math.max(s, 1 - Math.max(0, x - (-8))/16);                 // quay wall
  s = Math.max(s, 1 - Math.hypot(x-37, z+9)/16);                 // lighthouse rocks
  const bz = 33 + (x-12)*(-0.13);
  s = Math.max(s, 1 - Math.abs(z - bz)/13);                      // breakwater
  s = Math.max(s, 1 - Math.hypot(x-30, z-16)/14);                // outer shoal
  return THREE.MathUtils.clamp(s,0,1);
}
function buildSea(){
  const deep=new THREE.Color(0x14384f), mid=new THREE.Color(0x1f6079), shal=new THREE.Color(0x3fa3a8);
  /* fine layer */
  const geoF=new THREE.BoxGeometry(1,5,1); geoF.translate(0,-2.5,0);
  let n=0;
  for(let x=seaGrid.x0;x<=seaGrid.x1;x++) for(let z=seaGrid.z0;z<=seaGrid.z1;z++) if(!landAt(x,z)) n++;
  seaFine=new THREE.InstancedMesh(geoF, seaMaterial(0.0), n);
  const M=new THREE.Matrix4(), C=new THREE.Color(); let i=0;
  for(let x=seaGrid.x0;x<=seaGrid.x1;x++) for(let z=seaGrid.z0;z<=seaGrid.z1;z++){
    if(landAt(x,z)) continue;
    M.setPosition(x,0,z); seaFine.setMatrixAt(i,M);
    const s=shallowAt(x,z);
    C.copy(deep).lerp(mid, 0.35+0.65*s).lerp(shal, s*s*0.85);
    C.offsetHSL(0,0,(hash3(x,1,z)-.5)*0.035);
    seaFine.setColorAt(i,C); i++;
  }
  seaFine.instanceMatrix.needsUpdate=true; seaFine.receiveShadow=false; scene.add(seaFine);

  /* coarse layer to the horizon */
  const geoC=new THREE.BoxGeometry(5.5,9,5.5); geoC.translate(0,-4.5,0);
  const step=5.5, R=230; let m=0;
  for(let x=-R;x<=R;x+=step) for(let z=-R;z<=R;z+=step){
    const inside = x>seaGrid.x0-3 && x<seaGrid.x1+3 && z>seaGrid.z0-3 && z<seaGrid.z1+3;
    if(!inside) m++;
  }
  seaCoarse=new THREE.InstancedMesh(geoC, seaMaterial(0.10), m);
  i=0;
  for(let x=-R;x<=R;x+=step) for(let z=-R;z<=R;z+=step){
    if(x>seaGrid.x0-3 && x<seaGrid.x1+3 && z>seaGrid.z0-3 && z<seaGrid.z1+3) continue;
    M.setPosition(x,-0.4,z); seaCoarse.setMatrixAt(i,M);
    C.copy(deep).lerp(mid,0.25); seaCoarse.setColorAt(i,C); i++;
  }
  seaCoarse.instanceMatrix.needsUpdate=true; scene.add(seaCoarse);

  foamMat = new THREE.MeshBasicMaterial({ color:0xffffff, transparent:true, opacity:.8,
    depthWrite:false, toneMapped:false });
  foamMat.onBeforeCompile = (sh)=>{
    sh.uniforms.uTime=uTime;
    sh.vertexShader = sh.vertexShader
      .replace('#include <common>', `#include <common>\nuniform float uTime;\n${WAVE}`)
      .replace('#include <begin_vertex>', `#include <begin_vertex>
        { vec3 ip=vec3(0.0);
          #ifdef USE_INSTANCING
            ip=instanceMatrix[3].xyz;
          #endif
          float w=waveF(ip.xz,uTime);
          transformed.y += w + 0.34 + 0.14*sin(uTime*3.0 + ip.x*0.6 + ip.z*0.4); }`);
  };
  return n+m;
}
/* foam patch clusters */
function foamPatches(list, parent, tint=0xffffff){
  const g=new THREE.BoxGeometry(1,.4,1);
  const im=new THREE.InstancedMesh(g, new THREE.MeshBasicMaterial({ color:tint, transparent:true,
    opacity:.72, depthWrite:false, toneMapped:false }), list.length);
  im.material.onBeforeCompile = foamMat.material ? foamMat.material.onBeforeCompile : null;
  /* clone the same shader hook */
  im.material.onBeforeCompile = foamMat.onBeforeCompile;
  im.material.uniformsNeedUpdate = true;
  const M=new THREE.Matrix4();
  list.forEach((p,i)=>{ M.makeScale(p[3]||1, 1, p[4]||1); M.setPosition(p[0],p[1],p[2]); im.setMatrixAt(i,M); });
  im.instanceMatrix.needsUpdate=true; parent.add(im); return im;
}

/* ══════════════════════════════════════════════════════════════
   6 · harbour works — quay, jetty, town, breakwater, lighthouse
   ══════════════════════════════════════════════════════════════ */
const QUAY_X0=-74, QUAY_X1=-14, QUAY_TOP=4;
const hillH = x => Math.min(23, QUAY_TOP + (-QUAY_X1 - x)*0.40);

const lamps = new Vox();          /* emissive window / lantern voxels */
const worldSolidVox = new Vox();  /* everything opaque, for water holes */
let lampMesh=null;

function buildQuay(){
  const v=new Vox();
  /* the stone quay: sheer wall at x=-14, cobbled top */
  v.block(QUAY_X0, QUAY_X1, -8, QUAY_TOP, -46, 46, P_.cobble);
  for(let z=-46;z<=46;z+=2) for(let x=QUAY_X1-1;x>=QUAY_X1-3;x--) v.set(x,QUAY_TOP,z,P_.cobbleHi);
  /* wall face gets darker, wet stone near the water */
  for(let z=-46;z<=46;z++){ for(let y=-8;y<=0;y++) v.set(QUAY_X1,y,z,P_.rockWet);
    for(let y=1;y<=QUAY_TOP;y++) v.set(QUAY_X1,y,z,P_.stone); }
  /* a slipway / beach in the south-east corner of the yard */
  for(let i=0;i<10;i++) for(let z=28;z<=38;z++) v.set(QUAY_X1+i, QUAY_TOP-Math.floor(i*0.45), z, P_.sand);
  /* bollards + capstan along the quay edge */
  for(let z=-40;z<=40;z+=7){
    v.line(QUAY_X1-3,5, z, QUAY_X1-3,7, z, P_.woodDk,1);
    v.set(QUAY_X1-3,8,z,P_.woodGrey);
  }
  const capX=QUAY_X1-9, capZ=-6;
  v.cyl(capX,capZ,QUAY_TOP+1,QUAY_TOP+3,2,P_.wood);
  v.cyl(capX,capZ,QUAY_TOP+4,QUAY_TOP+4,2.5,P_.woodDk);
  for(let a=0;a<4;a++){ const ang=a*Math.PI/2;
    v.line(capX,capX+Math.round(Math.cos(ang)*4), QUAY_TOP+4, QUAY_TOP+4,
                   capZ,capZ+Math.round(Math.sin(ang)*4), QUAY_TOP+4, P_.woodDk); }
  /* anchors, chains, stacked shot */
  v.box(QUAY_X1-7,QUAY_X1-7,QUAY_TOP+1,QUAY_TOP+1,-26,-22,P_.iron);
  v.line(QUAY_X1-7,QUAY_TOP+1,-24, QUAY_X1-7,QUAY_TOP+6,-24,P_.iron);
  v.line(QUAY_X1-9,QUAY_TOP+6,-24, QUAY_X1-5,QUAY_TOP+6,-24,P_.iron);
  v.line(QUAY_X1-7,QUAY_TOP+6,-26, QUAY_X1-7,QUAY_TOP+6,-22,P_.iron);
  /* lamp posts down the quay */
  const lampSpots=[];
  for(let z=-36;z<=40;z+=12){ lampSpots.push([QUAY_X1-6,QUAY_TOP,z]); }
  lampSpots.forEach(([lx,ly,lz])=>{
    v.line(lx,ly+1,lz, lx,ly+8,lz, P_.pitch);
    v.line(lx-1,ly+9,lz, lx+1,ly+9,lz, P_.iron);
    v.box(lx-1,lx+1,ly+8,ly+8,lz-1,lz+1,P_.iron);
    lamps.box(lx-1,lx+1,ly+7,ly+8,lz-1,lz+1,P_.lamp);
    addGlow(lx, ly+7.5, lz, 13, 0xffc978);
  });
  /* fish-market stalls on the yard */
  for(let s=0;s<3;s++){
    const sx=QUAY_X1-16-s*0, sz=-16+s*11;
    for(let i=0;i<6;i++) v.line(sx,QUAY_TOP+1,sz+i, sx,QUAY_TOP+1,sz+i, P_.wood);
    v.line(sx,QUAY_TOP+1,sz,   sx,QUAY_TOP+5,sz,   P_.woodDk);
    v.line(sx,QUAY_TOP+1,sz+5, sx,QUAY_TOP+5,sz+5, P_.woodDk);
    v.box(sx-2,sx+2,QUAY_TOP+4,QUAY_TOP+5,sz-1,sz+6, s%2? P_.red:P_.sail);
    v.box(sx-1,sx+1,QUAY_TOP+3,QUAY_TOP+3,sz,sz+5, P_.woodGrey);
    v.box(sx-1,sx+1,QUAY_TOP+4,QUAY_TOP+4,sz+1,sz+4, P_.fish);
  }
  /* crates & barrels, the currency of any good harbour */
  for(let i=0;i<26;i++){
    const cx=QUAY_X1-4-Math.floor(rnd()*16), cz=-40+Math.floor(rnd()*82);
    if(Math.hypot(cx-QUAY_X1-(-8), 0)>0 && Math.abs(cz+6)<4 && Math.abs(cx-capX)<4) continue;
    const s=1+Math.floor(rnd()*2), h=s+Math.floor(rnd()*2);
    v.box(cx,s-1===0?cx:cx+s-1, QUAY_TOP+1, QUAY_TOP+h, cz, cz+s-1, P_.wood);
    v.box(cx,cx+s-1, QUAY_TOP+1, QUAY_TOP+1, cz, cz+s-1, P_.woodDk);
    if(rnd()<.4) v.cyl(cx+s/2-.5,cz+s/2-.5,QUAY_TOP+1,QUAY_TOP+3,1.2,[0x6d4d30,0x5f4229]);
  }
  /* coiled rope + nets drying on frames */
  for(let i=0;i<7;i++){ const rx=QUAY_X1-4-Math.floor(rnd()*10), rz=-38+Math.floor(rnd()*76);
    v.cyl(rx,rz,QUAY_TOP+1,QUAY_TOP+1,1.5+Math.floor(rnd()*2),P_.rope,false); }
  for(let f=0;f<2;f++){
    const fz=12+f*16;
    v.line(QUAY_X1-5,QUAY_TOP+1,fz, QUAY_X1-5,QUAY_TOP+6,fz,P_.woodDk);
    v.line(QUAY_X1-12,QUAY_TOP+1,fz, QUAY_X1-12,QUAY_TOP+6,fz,P_.woodDk);
    v.line(QUAY_X1-12,QUAY_TOP+6,fz, QUAY_X1-5,QUAY_TOP+6,fz,P_.woodDk);
    for(let x=QUAY_X1-12;x<=QUAY_X1-5;x++) for(let d=0;d<6;d++)
      v.set(x, QUAY_TOP+5-Math.abs(x-(QUAY_X1-8.5))>0?QUAY_TOP+4-d:QUAY_TOP+4-d, fz+(d%2), P_.rope);
  }
  return { v, vox:v.list.length };
}

function buildDock(){
  const v=new Vox();
  const J0=-12, J1=-2, Z0=-20, Z1=22;
  v.block(J0,J1,4,5,Z0,Z1,P_.wood);
  for(let z=Z0;z<=Z1;z++) for(let x=J0;x<=J1;x++) if((z%3)===0) v.set(x,5,z,P_.woodDk);
  /* pilings */
  for(let z=Z0+1;z<=Z1;z+=4){
    v.line(J1, -6, z, J1, 4, z, P_.woodDk);
    v.line(J0+2, -6, z, J0+2, 4, z, P_.woodDk);
    v.line(J1-1, -1, z, J1, 2, z, P_.woodDk);
  }
  for(let x=J0;x<=J1;x+=4) v.line(x,3,Z0, x,3,Z1,P_.woodDk);
  /* jetty furniture: mooring rings, steps down to the water, a derrick */
  for(let z=Z0+3;z<Z1;z+=6){
    v.line(J1,6,z, J1,8,z, P_.woodDk); v.set(J1,9,z,P_.woodGrey);
    v.line(J1-2,6,z, J1,6,z, P_.iron);
  }
  /* derrick crane over the jetty */
  const dx=J0-3, dz=12;
  v.cyl(dx,dz,QUAY_TOP,QUAY_TOP+11,1.6,P_.woodDk);
  v.line(dx,QUAY_TOP+11,dz, J1+3,QUAY_TOP+14,dz+1, P_.wood);
  v.line(dx,QUAY_TOP+9,dz,  J1+3,QUAY_TOP+13,dz+1, P_.wood);
  v.line(J1+3,QUAY_TOP+14,dz+1, J1+3,QUAY_TOP+4,dz+1, P_.rope);
  v.box(J1+2,J1+4,QUAY_TOP+3,QUAY_TOP+4,dz,dz+2,P_.wood);
  /* lantern on the jetty head */
  v.line(J1,5,-19, J1,9,-19,P_.pitch); v.box(J1-1,J1+1,9,10,-20,-18,P_.iron);
  lamps.box(J1,J1,9,9,-19,-19,P_.flame); addGlow(J1,9,-19,11,0xffbf6a);
  /* gangway ladder down the quay face for the ship's boat */
  return { v, vox:v.list.length };
}

function figure(v, x, y, z, c, face=1){
  const skin=P_.skin[(rnd()*2)|0], coat=Array.isArray(c)? c[(rnd()*c.length)|0] : c;
  v.set(x,y,z,P_.pitch); v.set(x,y+1,z,coat); v.set(x,y+2,z,coat);
  v.set(x,y+3,z,skin); v.set(x,y+4,z,coat);
  if(rnd()<.5){ v.set(x,y+5,z,coat); }
  const side = face===0? [-1,1] : [0,0];
  v.set(x+(face===0?0:1),y+2,z+face,coat); v.set(x-(face===0?0:1),y+2,z-face,coat);
  return { head:[x,y+3,z], arm:[x+1,y+2,z] };
}

function buildTown(){
  const v=new Vox();
  /* terraced hillside */
  for(let x=QUAY_X0;x<=QUAY_X1;x++) for(let z=-44;z<=44;z++){
    const h=hillH(x) + Math.sin(x*0.31+z*0.12)*0.8 + Math.sin(z*0.19-x*0.07)*1.1;
    const top=Math.round(h);
    const edge = x>=QUAY_X1-2;
    v.set(x, top, z, edge? P_.stone : (top>16? P_.rock : P_.grass));
    if(top>QUAY_TOP+1 && hash3(x,7,z)<0.03) v.set(x,top,z,P_.dirt);
  }
  v.block(QUAY_X0,QUAY_X1,-8,QUAY_TOP,-44,44,P_.stone);
  for(let x=QUAY_X0;x<=QUAY_X1;x++){ const h=Math.round(hillH(x));
    v.box(x,x,QUAY_TOP+1,h-1,-44,44,P_.dirt); }
  /* cobbled lane zig-zagging up */
  for(let z=-40;z<=40;z++){
    const lx=QUAY_X1-6-Math.round(6+18*Math.sin((z+40)*0.05));
    const h=Math.round(hillH(lx)); for(let d=0;d<3;d++) v.set(lx+d,h,z,P_.path);
  }
  /* terraced cottages */
  const house=(hx,hz,w,d,hh,wall,roofC)=>{
    const base=Math.round(hillH(hx));
    v.block(hx-1,hx+w-2,base-1,base+hh-1,hz-1,hz+d-2,P_.brick);
    v.block(hx-1,hx+w-2,base,base+hh-1,hz-1,hz+d-2,wall);
    for(let y=base;y<base+hh;y++){ v.set(hx-1,y,hz-1,P_.brick); v.set(hx+w-2,y,hz+d-2,P_.brick); }
    for(let y=base+1;y<base+hh-1;y+=2) for(let x=hx;x<hx+w-1;x+=2){
      v.set(x,y,hz-1,P_.door); v.set(x,y,hz+d-2,P_.door);
      lamps.box(x,x,y,y,hz-1,hz-1,P_.lamp);
    }
    v.box(hx-1,hx+w-2,base+hh-1,base+hh-1,hz-1,hz+d-2,P_.woodDk);
    v.roof(hx-1,hx+w-2,base+hh,hz-1,hz+d-2,Math.ceil(w/2)+1,roofC,P_.slate);
    v.gable(hz-1,hx-1,hx+w-2,base+hh,base+hh+Math.ceil(w/2),wall);
    v.gable(hz+d-2,hx-1,hx+w-2,base+hh,base+hh+Math.ceil(w/2),wall);
    const chx=hx+(w>3?1:0);
    v.line(chx,base+hh+1,hz+1, chx,base+hh+4,hz+1,P_.brick);
    return {x:chx, y:base+hh+4, z:hz+1, top:base};
  };
  const chimneys=[];
  const spec=[[-56,-30,4,4,5,P_.stucco,P_.slate],[-52,-22,5,4,6,P_.stucco2,P_.brick],[ -47,-30,4,4,5,P_.stucco,P_.slate],
    [-44,-14,4,5,6,P_.stucco2,P_.slate],[-50,-4,5,4,5,P_.stucco,P_.brick],[-58,4,4,4,6,P_.stucco2,P_.slate],
    [-45,14,5,4,5,P_.stucco,P_.slate],[-53,22,4,4,6,P_.stucco2,P_.brick],[-48,32,5,4,5,P_.stucco,P_.slate],
    [-62,-14,4,4,5,P_.stucco2,P_.slate],[-63,26,4,4,5,P_.stucco,P_.brick],[-42,-38,4,4,5,P_.stucco2,P_.slate],
    [-66,-4,4,4,5,P_.stucco,P_.slate],[-57,-42,4,4,6,P_.stucco2,P_.brick]];
  spec.forEach(s=>{ const r=house(s[0],s[1],s[2],s[3],s[4],s[5],s[6]); if(rnd()<.75) chimneys.push(r); });

  /* the customs house, right above the jetty, with a clock */
  const cx0=QUAY_X1-20, cz0=2, cw=9, cd=7, cb=Math.round(hillH(cx0));
  v.block(cx0,cx0+cw-1,cb-1,cb+8,cz0,cz0+cd-1,P_.stucco);
  v.block(cx0,cx0+cw-1,cb,cb+8,cz0,cz0+cd-1,[0xd9cdb3,0xcfc2a6]);
  for(let y=cb+1;y<cb+8;y++) for(let x=cx0+1;x<cx0+cw-1;x+=2){
    v.set(x,y,cz0,P_.door); lamps.set(x,y,cz0,P_.lamp); }
  v.box(cx0-1,cx0+cw,cb+8,cb+8,cz0-1,cz0+cd,P_.cream);
  v.roof(cx0,cx0+cw-1,cb+9,cz0,cz0+cd-1,4,P_.slate,P_.iron);
  /* clock tower */
  const kx=cx0+4, kz=cz0+3;
  v.block(kx-2,kx+2,cb+9,cb+19,kz-2,kz+2,[0xd9cdb3,0xcfc2a6]);
  v.block(kx-3,kx+3,cb+19,cb+20,kz-3,kz+3,P_.slate);
  for(let a=0;a<4;a++){ const dx=a===0?-3:0, dz=a===2?-3:0; }
  v.box(kx-1,kx+1,cb+16,cb+18,kz-3,kz-3,P_.clockFace||P_.lamp);
  lamps.box(kx-1,kx+1,cb+16,cb+18,kz-3,kz-3,[0xffeab8,0xffdf9c]);
  v.set(kx,cb+17,kz-3,0x3a2a1c); v.set(kx+1,cb+17,kz-3,0x3a2a1c); v.set(kx,cb+16,kz-3,0x3a2a1c);
  v.line(kx,cb+21,kz, kx,cb+26,kz, P_.slate);
  addGlow(kx, cb+17, kz-4, 10, 0xffe2a0);
  /* the old church on the shoulder */
  const chx=-64, chz=-24, cb2=Math.round(hillH(chx));
  v.block(chx,chx+7,cb2-1,cb2+6,chz,chz+9,P_.stucco);
  v.roof(chx,chx+7,cb2+7,chz,chz+9,4,P_.slate,P_.iron);
  v.gable(chz,chx,chx+7,cb2+7,cb2+11,P_.stucco); v.gable(chz+9,chx,chx+7,cb2+7,cb2+11,P_.stucco);
  v.block(chx+2,chx+5,cb2+7,cb2+20,chz-3,chz,P_.stone);
  v.block(chx+1,chx+6,cb2+20,cb2+21,chz-4,chz+1,P_.slate);
  for(let y=cb2+13;y<cb2+19;y+=3){ lamps.box(chx+3,chx+4,y,y,chz-3,chz-3,P_.lamp); }
  v.line(chx+3.5,chx+3.5,cb2+22, chx+3.5,cb2+27,chz-1.5,chz-1.5, P_.iron);
  addGlow(chx+3, cb2+16, chz-4, 9, 0xffe0a0);
  /* pines */
  for(let i=0;i<26;i++){
    const tx=QUAY_X0+2+Math.floor(rnd()*40), tz=-44+Math.floor(rnd()*88);
    if(Math.abs(tx+64)<10 && Math.abs(tz+24)<12) continue;
    const th=Math.round(hillH(tx)), H=4+Math.floor(rnd()*4);
    v.line(tx,th+1,tz, tx,th+2,tz, P_.pineTrunk);
    for(let l=0;l<H;l++){ const r=Math.max(1, 3-Math.floor(l*0.9));
      v.cyl(tx,tz,th+2+l*2,th+3+l*2,r,P_.pine); }
  }
  /* windmill on the crest, facing the sea */
  const mx=-66, mz=30, mb=Math.round(hillH(mx));
  v.cyl(mx,mz,mb,mb+11,4,P_.stucco2,false);
  v.cyl(mx,mz,mb,mb+11,4.5,[0xa8907a,0x9b8571],false);
  v.ball(mx,mz,mb+13,3.4,P_.slate);
  v.line(mx,mb+6,mz, mx,mb+6,mz, P_.door);
  windmillAnchor={x:mx+4.6, y:mb+10, z:mz};
  chimneys.push({x:cx0+1,y:cb+10,z:cz0+1,top:cb});
  return { v, vox:v.list.length, chimneys };
}
let windmillAnchor=null, windmill=null;

function buildBreakwater(){
  const v=new Vox();
  const pts=[];
  for(let x=-10;x<=28;x+=1){ const z=Math.round(36 - (x+10)*0.20); pts.push([x,z]); }
  pts.forEach(([x,z])=>{
    const h = 1 + Math.round(hash3(x,3,z)*2);
    for(let d=-3;d<=3;d++){
      const zz=z+d, hh=h - Math.abs(d)*0.4 + hash3(x,9,zz)*1.2;
      v.box(x,x,-6,Math.max(-1,Math.round(hh)),zz,zz, Math.abs(d)>=2? P_.rock:P_.stone);
    }
  });
  /* beacon tower at the watch end */
  const bx=26, bz=Math.round(36-(26+10)*0.20)+1;
  v.cyl(bx,bz,-1,7,2.4,P_.stone,false);
  v.box(bx-3,bx+3,7,7,bz-3,bz+3,P_.iron);
  v.cyl(bx,bz,8,10,2,P_.red,false);
  lamps.cyl(bx,bz,8,10,1.4,P_.flame);
  v.line(bx,bx,bz+0, 0,13, 0,0, P_.iron, 0);
  v.cyl(bx,bz,11,12,2.6,P_.pitch,false);
  addGlow(bx,9.5,bz,14,0xff9a5a);
  beaconPos=[bx,9.5,bz];
  /* foam against the sea face */
  const foam=[];
  pts.forEach(([x,z])=>{ if(x%2===0) foam.push([x,0.1,z+4,1,1]); });
  return { v, vox:v.list.length, foam };
}
let beaconPos=[26,9.5,31];

function buildLighthouse(){
  const v=new Vox();
  const cx=37, cz=-9;
  for(let dx=-12;dx<=12;dx++) for(let dz=-12;dz<=12;dz++){
    const d=Math.hypot(dx,dz)*1.0; if(d>12.5) continue;
    const h=Math.round((1-d/12.5)*7.2 + hash3(dx,5,dz)*1.6 - 0.4);
    v.box(cx+dx,cx+dx,-8,Math.max(-1,h),cz+dz,cz+dz, h<1? P_.rockWet : P_.rock);
    if(h>2 && hash3(dx,11,dz)<0.25) v.set(cx+dx,h+1,cz+dz,P_.grass);
  }
  /* the tower */
  const y0=6;
  for(let y=0;y<=22;y++){
    const r=Math.max(2.2, 5.2 - y*0.115);
    const band=Math.floor(y/3.4)%2===0;
    v.cyl(cx,cz,y0+y,y0+y,r, band? [0xf0ece2,0xe4dfd3] : P_.red, false);
  }
  v.cyl(cx,cz,y0+22,y0+22,3.4,P_.iron);          /* gallery deck */
  for(let a=0;a<12;a++){ const an=a/12*Math.PI*2;
    v.set(cx+Math.round(Math.cos(an)*3.2), y0+23.5, cz+Math.round(Math.sin(an)*3.2), P_.iron); }
  v.cyl(cx,cz,y0+23,y0+26,2.4,[0xe8e4da,0xdcd7cb],false);   /* lantern room */
  lamps.cyl(cx,cz,y0+23.5,y0+26,1.6,[0xfff0c0,0xffdfa0]);
  v.ball(cx,cz,y0+27.5,2.2,P_.copper||0xb4652f);
  v.line(cx,cx,y0+29, cx,y0+32,cx, P_.iron);
  addGlow(cx, y0+24.5, cz, 46, 0xfff0c0);
  /* keeper's cottage + wall */
  const kx=cx-8, kz=1, kb=4;
  v.block(kx,kx+5,kb-1,kb+4,kz,kz+4,P_.stucco);
  v.roof(kx,kx+5,kb+5,kz,kz+4,3,P_.slate,P_.iron);
  lamps.box(kx+1,kx+1,kb+2,kb+2,kz,kz,P_.lamp);
  lamps.box(kx+4,kx+4,kb+2,kb+2,kz,kz,P_.lamp);
  v.line(kx-1,kx-1,kb,kx-1,kb+3,kz+2,kz+2,P_.brick);
  /* rocks with a slip for the keeper's coble */
  const foam=[];
  for(let a=0;a<26;a++){ const an=a/26*Math.PI*2, R=11+Math.sin(a*2.3)*1.5;
    foam.push([cx+Math.cos(an)*R, 0.05, cz+Math.sin(an)*R, 1, 1]); }
  return { v, vox:v.list.length, foam };
}

function buildBoats(){
  const v=new Vox();
  /* a fishing smack moored off the jetty head */
  const bx=-1, bz=30, ang=-0.5;
  const rot=(x,z)=>[x*Math.cos(ang)+z*Math.sin(ang), -x*Math.sin(ang)+z*Math.cos(ang)];
  for(let l=-6;l<=6;l++){
    const w=Math.round(2.2*Math.cos(l/7.2));
    const keel=-2+Math.abs(l)*0.22, deck=1;
    for(let x=-w;x<=w;x++) for(let y=keel;y<=deck;y++)
      v.set(bx+...(()=>{const r=rot(x,l);return r[0]})(), y, bz+rot(x,l)[1],
        Math.abs(x)===w? (y>=0? P_.red : P_.woodDk) : P_.wood);
  }
  return v;
}

/* ══════════════════════════════════════════════════════════════
   7 · THE SHIP — “Aurora of Whitby”, a three-masted barque
   ══════════════════════════════════════════════════════════════ */
const PROF = [
  [-24, 3.0,-2.0, 5.2],
  [-21, 4.8,-3.6, 4.8],
  [-15, 5.9,-4.6, 3.7],
  [-6 , 6.4,-5.0, 3.2],
  [  2, 6.3,-5.0, 3.3],
  [ 10, 5.4,-4.3, 3.7],
  [ 16, 3.6,-2.8, 4.4],
  [ 21, 1.2,-1.2, 5.2],
];
function prof(z){
  if(z<=PROF[0][0]) return PROF[0];
  if(z>=PROF[PROF.length-1][0]) return PROF[PROF.length-1];
  for(let i=0;i<PROF.length-1;i++){
    const a=PROF[i], b=PROF[i+1];
    if(z>=a[0] && z<=b[0]){
      const t=(z-a[0])/(b[0]-a[0]);
      return [z, a[1]+(b[1]-a[1])*t, a[2]+(b[2]-a[2])*t, a[3]+(b[3]-a[3])*t];
    }
  }
  return PROF[0];
}
const wHalf=(wm,y,keel,deck)=>{
  const t=(y-keel)/(deck-keel); if(t<0) return 0;
  let f=0.30+0.70*Math.sqrt(Math.min(1, t/0.60));
  if(t>0.60) f*=1-(t-0.60)*0.18;
  return wm*Math.min(1,Math.max(0.10,f));
};

let shipGroup, shipBody, sails=[], flagMats=[], rigLines, wakeFoam;
function buildShip(){
  const hull=new Vox(), deck=new Vox(), lamps2=new Vox();
  const shipVox=[hull,deck];
  for(let z=-24;z<=21;z++){
    const [,wm,keel,dk]=prof(z);
    const K=Math.ceil(keel), D=Math.floor(dk);
    for(let y=K;y<=D;y++){
      const h=Math.floor(wHalf(wm,y,keel,dk));
      for(let x=-h;x<=h;x++){
        const shell = Math.abs(x)>=h;
        let col;
        if(y< -1.5) col=P_.hullRed;
        else if(shell && (y===0||y===1)) col=P_.ochre;
        else if(shell) col=P_.hull;
        else col=P_.woodDk;
        if(shell && z>17) col = (y>3)? P_.cream : P_.hullRed;
        (y===D? deck:hull).set(x,y,z,col);
      }
      /* deck planking on the sheer line */
      for(let x=-h;x<=h;x++) deck.set(x,D,z, ((z+x)%4===0)? P_.woodDk : P_.wood);
      /* bulwark + painted rail */
      hull.set(-h,D+1,z,P_.cream); hull.set(h,D+1,z,P_.cream);
      if(h>2){ hull.set(-h+1,D+1,z,P_.hull); hull.set(h-1,D+1,z,P_.hull); }
    }
    /* gunports in the yellow waist band */
    if(z%4===1 && wm>4.5){ const h=Math.floor(wHalf(wm,1,keel,dk));
      [-h,h].forEach(x=>{ hull.set(x,1,z,P_.pitch); hull.set(x,2,z,P_.cream); hull.set(x,0,z,P_.cream); }); }
  }
  /* stern gallery with lit windows */
  for(let x=-4;x<=4;x++){ hull.set(x,3,-24,P_.cream); lamps2.box(x,x,3,3,-25,-25,P_.lamp); }
  hull.box(-5,5,2,4,-23,-24,P_.cream);
  hull.box(-4,4,1,1,-23,-24,P_.ochre);
  /* bowsprit + jib-boom */
  hull.line(0,4,21, 0,6,26, P_.wood, 1);
  hull.line(0,6,26, 0,8,32, P_.wood, 1);
  hull.line(-1,4,22, 1,4,22, P_.woodDk);
  /* figurehead */
  [-1,0,1].forEach(x=>hull.set(x,3,22,P_.cream)); hull.set(0,4,22,P_.cream);
  /* masts */
  const masts=[ {z:8,h:34,name:'fore'}, {z:-3,h:38,name:'main'}, {z:-15,h:29,name:'mizzen'} ];
  masts.forEach(m=>{
    for(let y=2;y<=m.h;y++){ const w=y<12?1:0;
      for(let dx=-w;dx<=w;dx++) for(let dz=-w;dz<=w;dz++) hull.set(dx,y,m.z+dz,y>m.h-3?P_.woodDk:P_.wood); }
    /* tops */
    if(m.h>30){ hull.box(-2,2,m.h-14,m.h-14,m.z-1,m.z+1,P_.woodDk);
      for(let x=-2;x<=2;x++){ hull.set(x,m.h-13,m.z-1,P_.woodGrey); hull.set(x,m.h-13,m.z+1,P_.woodGrey);} }
    /* yards */
    const yards=[[18,8],[24,7],[29,5.2],[33,3.4]];
    yards.forEach(([yy,hl])=>{ if(yy>m.h-2) return;
      for(let x=-Math.floor(hl);x<=Math.floor(hl);x++) hull.set(x,yy,m.z, x===0?P_.wood:P_.woodDk); });
  });
  /* deck furniture */
  deck.box(-3,3,4,4,-20,-17,P_.woodDk);            /* poop deck house */
  deck.box(-2,2,5,5,-19,-18,P_.cream);
  lamps2.box(-1,1,5,5,-19,-19,P_.lamp);
  deck.box(-3,3,4,4,14,18,P_.woodDk);              /* forecastle */
  deck.box(-2,2,3,4,-8,-4,P_.woodDk);              /* hatchways */
  deck.box(-2,2,3,4,2,5,P_.woodDk);
  deck.cyl(0,10,4,5,1.6,P_.wood);                   /* capstan */
  deck.box(-4,-2,3,3,5,8,P_.wood);                  /* coiled cable */
  deck.box(2,4,3,3,6,9,P_.woodDk);                  /* spares */
  deck.box(3,4,4,4,-11,-9,P_([0x6d4d30,0x5f4229])||P_.wood);
  deck.box(-4,-4,4,4,-6,-4,P_.iron);                /* carronade */
  /* galley chimney — where the smoke comes from */
  deck.line(-3,-3,3,3, 5,6,-11,-11, P_.iron);
  const shipChimney=[-3,6,-11];

  /* ── sails: each is its own mesh so it can be gathered in ── */
  const sailGroup=new THREE.Group();
  const mkSail=(w,hw,bulge,seamColour=P_.sail)=>{
    const sv=new Vox();
    for(let y=0;y>=-h;y--) for(let x=-hw;x<=hw;x++){
      const u=x/hw, v=-y/h;
      const off=Math.round(Math.sin(Math.PI*Math.abs(u))*Math.cos(Math.PI*0.5*v)*bulge);
      let c = seamColour[(rnd()*seamColour.length)|0];
      if((Math.abs(x)%4)===0) c = 0xd9c8a2;
      if(v>0.92) c = 0xc4b18b;
      sv.set(x,y,off,c);
      if(v>0.45 && Math.abs(u)>0.94 && (Math.round(-y)%3===0)) sv.set(x,y,off,0xbfae88);
    }
    const g=bake(sv,.07);
    const m=meshOf(g, matSail(), true, false);
    m.userData.furlable=true; return m;
  };
  masts.forEach(m=>{
    if(m.name==='mizzen') return;
    const yards=[[18,8,7,2.6],[24,7,6,2.2],[29,5.2,4,1.8],[33,3.4,3,1.5]];
    yards.forEach(([yy,yl,sh,bulge])=>{
      if(yy>m.h-2) return;
      const s=mkSail(0,sh,m.h>30?bulge:bulge*0.9);
      s.position.set(0, yy, m.z);
      sailGroup.add(s); sails.push(s);
    });
  });
  /* spanker (fore-and-aft) on the mizzen */
  {
    const sv=new Vox();
    for(let y=0;y>=-10;y--) for(let z=0;z>=-11;z--){
      const off=Math.round(Math.sin(Math.PI*(z+11)/11)*Math.cos(Math.PI*0.5*(y/-10))*2.0);
      sv.set(0,y,z+ (z>-0.5?0:0), P_.sail[(rnd()*3)|0]);
      sv.set(off,y,z, sv.list.length?P_.sail[0]:P_.sail[0]);
    }
    const g=bake(sv,.07); const m=meshOf(g, matSail(), true, false);
    m.position.set(0,22,-14); sailGroup.add(m); sails.push(m);
  }
  /* jibs */
  const mkJib=(x0,y0,z0,x1,y1,z1)=>{
    const sv=new Vox(); const n=18;
    for(let i=0;i<=n;i++){ const t=i/n;
      const px=Math.round(x0+(x1-x0)*t), py=Math.round(y0+(y1-y0)*t), pz=Math.round(z0+(z1-z0)*t);
      for(let d=0; d<= (1-t)*13; d++) sv.set(px, py-d, pz+d, P_.sail[(rnd()*3)|0]);
    }
    const m=meshOf(bake(sv,.07), matSail(), true, false);
    sailGroup.add(m); sails.push(m); return m;
  };
  mkJib(0,30,9, 0,7,31);
  mkJib(0,23,15, 0,9,25);

  /* ── rigging: thin lines read perfectly against solid voxels ── */
  const RP=[];
  const seg=(a,b,c,d,e,f,g,h)=>RP.push(a,b,c,d,e,f,g,h);
  masts.forEach(m=>{
    const T=[0,m.h,m.z];
    [[-6,3,m.z-2],[6,3,m.z-2],[-6,3,m.z+2],[6,3,m.z+2]].forEach(s=>seg(...T,...s));
    [-8,8].forEach(sx=>{ seg(...T, sx, 3, m.z-6); seg(...T, sx, 3, m.z+6); });
  });
  seg(0,38,-3, 0,34,8); seg(0,34,8, 0,8,32); seg(0,29,-15, 0,25,-3);
  seg(0,29,-15, -4,5,-22); seg(0,29,-15, 4,5,-22);
  seg(0,38,-3, -6,3,-16); seg(0,38,-3, 6,3,-16);
  seg(0,8,32, -5,4,14); seg(0,8,32, 5,4,14);
  for(let i=0;i<7;i++){ const t=i/6; seg(0,26+8*t, 8-6*t, 0, 8+ -0*t, 32-24*t); }
  const rigG=new THREE.BufferGeometry();
  rigG.setAttribute('position', new THREE.Float32BufferAttribute(RP,3));
  rigLines=new THREE.LineSegments(rigG, new THREE.LineBasicMaterial({color:0x6f5f43, fog:true}));
  rigLines.frustumCulled=false;

  /* ── assemble ── */
  shipGroup=new THREE.Group();
  shipGroup.position.set(10, 0, -3);
  shipGroup.rotation.y = 0.13;
  const hullMesh=meshOf(bake(hull,.075), matSolid); const deckMesh=meshOf(bake(deck,.09), matSolid);
  const lampMeshShip=meshOf(bake(lamps2,.02), matLamp, false, false);
  shipGroup.add(hullMesh, deckMesh, lampMeshShip, sailGroup, rigLines);
  scene.add(shipGroup);

  /* flag at the main top + pennant at the bow */
  flagMats=[];
  const flagGeo=new THREE.PlaneGeometry(6.4,3.8,18,8); flagGeo.translate(3.2,0,0);
  const flagMat=(sw)=>{
    const m=new THREE.ShaderMaterial({ transparent:true, side:THREE.DoubleSide,
      uniforms:{ uTime, uSw:{value:sw}, uRed:{value:new THREE.Color(0xb0432e)}, uBlue:{value:new THREE.Color(0x22405e)} },
      vertexShader:`uniform float uTime;varying vec2 vUv;void main(){vUv=uv;
        vec3 p=position; float w=sin(p.x*1.2 - uTime*7.0)*0.28*smoothstep(0.0,6.0,p.x);
        p.z += w; p.y += sin(p.x*0.9-uTime*5.0)*0.10*smoothstep(0.0,6.0,p.x);
        gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.0);}`,
      fragmentShader:`varying vec2 vUv;uniform float uSw;uniform vec3 uRed,uBlue;
        void main(){
          float crossV=smoothstep(0.045,0.0,abs(vUv.x-0.5)-0.04);
          float crossH=smoothstep(0.045,0.0,abs(vUv.y-0.5)-0.035);
          vec3 c=mix(uRed,vec3(0.95),max(crossV,crossH));
          float cant=step(vUv.x,0.42)*step(vUv.y,0.55);
          c=mix(c,uBlue,cant);
          float d=abs(vUv.x-0.21)+abs(vUv.y-0.28);
          c=mix(c,vec3(0.97),step(d,0.09)*cant);
          float tail=step(0.97-vUv.y*0.05, vUv.x)*uSw;
          gl_FragColor=vec4(c, 1.0 - tail*0.9);
        }`});
    flagMats.push(m); return m;
  };
  const ensign=new THREE.Mesh(flagGeo, flagMat(0));
  ensign.position.set(0.2,36,-3); shipGroup.add(ensign);
  const pen=new THREE.Mesh(new THREE.PlaneGeometry(5,1.2,14,4).translate(2.5,0,0), flagMat(1));
  pen.position.set(0.2,9,31); shipGroup.add(pen);

  /* wake foam, parented so it bobs with her */
  const foam=[];
  for(let z=-24;z<=24;z+=2){ const [,wm]=prof(z); const h=Math.floor(wHalf(wm,0,-5,4));
    foam.push([h+1.2,-0.1,z,1.2,1.4]); foam.push([-h-1.2,-0.1,z,1.2,1.4]); }
  wakeFoam=foamPatches(foam, shipGroup, 0xffffff);

  /* mooring lines + gangway, solved in world space */
  const bp=(x,y,z)=>shipGroup.localToWorld(new THREE.Vector3(x,y,z));
  const dockBollard=(z)=>new THREE.Vector3(-2, 9, z);
  const ropeMat=new THREE.MeshLambertMaterial({color:0x8d7a55});
  [[bp(0,5,21), dockBollard(-16)], [bp(0,5,-20), dockBollard(16)], [bp(4,5,4), dockBollard(2)]].forEach(([a,b])=>{
    const mid=a.clone().add(b).multiplyScalar(0.5); mid.y=Math.min(a.y,b.y)-2.2;
    const curve=new THREE.QuadraticBezierCurve3(a,mid,b);
    const t=new THREE.Mesh(new THREE.TubeGeometry(curve,14,0.16,5,false), ropeMat);
    t.castShadow=true; scene.add(t);
  });
  /* the gangway she comes ashore by */
  {
    const a=bp(6.2,4.2,-4), b=new THREE.Vector3(-3, 9.2, -6);
    const g=new THREE.BoxGeometry(a.distanceTo(b),0.5,2.1);
    const m=new THREE.Mesh(g, matSolid.clone());
    const gm=new Vox(); const L=Math.ceil(a.distanceTo(b));
    gm.box(0,0,0,L,0,0,0,0,0, P_.wood);
    const plank=meshOf(bake(gm,.06), matSolid);
    const holder=new THREE.Group(); holder.add(plank);
    holder.position.copy(b); holder.lookAt(a); holder.rotation.x+=0.06;
    holder.rotation.z=0; holder.rotateY(Math.PI); holder.scale.set(1,1,1);
    holder.lookAt(a); holder.rotateY(Math.PI);
    /* simpler: aim by quaternion */
    holder.quaternion.setFromUnitVectors(new THREE.Vector3(1,0,0), a.clone().sub(b).normalize());
    holder.rotateX(0.05);
    scene.add(holder);
    /* rope handrails */
    const railPts=[];
    for(let i=0;i<=10;i++){ const t=i/10; const p=b.clone().lerp(a,t);
      const up=new THREE.Vector3(0,1,0); railPts.push(p.x,p.y+1.3,p.z-1, p.x,p.y+1.3,p.z+1); }
    for(let i=0;i<10;i++){ const t0=i/10,t1=(i+1)/10;
      const p0=b.clone().lerp(a,t0), p1=b.clone().lerp(a,t1);
      RP.push(p0.x,p0.y+1.3,p0.z-1, p1.x,p1.y+1.3,p1.z-1, p0.x,p0.y+1.3,p0.z+1, p1.x,p1.y+1.3,p1.z+1); }
    const rg=new THREE.BufferGeometry(); rg.setAttribute('position',new THREE.Float32BufferAttribute(RP,3));
    scene.add(new THREE.LineSegments(rg, new THREE.LineBasicMaterial({color:0x6f5f43})));
  }

  /* two little crew figures: one at the wheel, one on the fore deck */
  const crew=new Vox();
  const cA=figure(crew,0,5,-13, P_.coats[0], 0);
  const cB=figure(crew,2,4,12, P_.coats[1], 0);
  shipGroup.add(meshOf(bake(crew,.05), matSolid));

  /* a waving figure on the jetty */
  const wv=new Vox(), arm=new Vox();
  const wp=new THREE.Vector3(-4,5,-8);
  figure(wv, 0,0,0, P_.coats[2], 1);
  arm.set(1,2,0,P_.coats[2]); arm.set(1,3,0,P_.skin[0]);
  const wvMesh=meshOf(bake(wv,.05), matSolid);
  const armMesh=meshOf(bake(arm,.05), matSolid);
  armMesh.geometry.translate(-1,-2,0);
  armMesh.position.set(1,2,0);
  const wvGroup=new THREE.Group(); wvGroup.add(wvMesh, armMesh);
  wvGroup.position.copy(wp); wvGroup.rotation.y=-1.9; scene.add(wvGroup);
  windowWaver=armMesh;

  dockFolk=new Vox();
  for(let i=0;i<7;i++) figure(dockFolk, -6-i*0.6, 5, -14+i*6.5, P_.coats, i%2?1:0);
  scene.add(meshOf(bake(dockFolk,.05), matSolid));

  return { vox: hull.list.length+deck.list.length+sailGroup.children.length*90 };
}
let windowWaver=null, dockFolk=null;
const matSail=()=> new THREE.MeshLambertMaterial({ vertexColors:true });

/* ══════════════════════════════════════════════════════════════
   8 · gulls, smoke, windmill
   ══════════════════════════════════════════════════════════════ */
const gulls=[];
function buildLife(chimneys, shipChimney){
  /* gulls */
  const bodyV=new Vox(); bodyV.box(-1,1,0,0,-1,1,P_.gull); bodyV.set(2,1,0,P_.sand);
  const wingV=new Vox(); wingV.box(0,0,0,0,-3,-3,P_.gull);
  const bg=bake(bodyV,.05), wg=bake(wingV,.05);
  for(let i=0;i<7;i++){
    const g=new THREE.Group();
    g.add(meshOf(bg, matSolid, false,false));
    const wl=new THREE.Mesh(wg, matSolid); const wr=new THREE.Mesh(wg.clone(), matSolid);
    wr.scale.x=-1; wl.position.set(0,0.6,1); wr.position.set(0,0.6,-1);
    g.add(wl,wr);
    g.userData={ r:rr(26,60), y:rr(16,40), sp:rr(.10,.22)*(rnd()<.5?-1:1), ph:rr(0,6.28), wl, wr };
    scene.add(g); gulls.push(g);
  }
  /* smoke */
  const SM=[...chimneys, shipChimney];
  const smoke=new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1),
    new THREE.MeshLambertMaterial({ color:0xffffff, transparent:true, opacity:.62 }), SM.length*7);
  smoke.userData={ src:SM, m:new THREE.Matrix4(), c:new THREE.Color() };
  smoke.frustumCulled=false; scene.add(smoke); smokeRef=smoke;
  /* windmill */
  if(windmillAnchor){
    windmill=new THREE.Group();
    for(let a=0;a<4;a++){
      const bl=new THREE.Group();
      const bv=new Vox();
      bv.box(0,10,0,0,-1,1,P_.sail); bv.box(1,1,0,10,0,0,P_.woodDk);
      for(let x=2;x<10;x+=2) bv.box(x,x,0,0,-1,1,P_.woodGrey);
      bl.add(meshOf(bake(bv,.06), matSolid, true,false));
      bl.rotation.z=a*Math.PI/2; windmill.add(bl);
    }
    windmill.position.set(windmillAnchor.x, windmillAnchor.y, windmillAnchor.z);
    windmill.rotation.y=0.2;
    scene.add(windmill);
  }
  /* voxel clouds */
  cloudGroup=new THREE.Group();
  for(let c=0;c<11;c++){
    const cv=new Vox(); const R=5+Math.floor(rnd()*5);
    const n=7+Math.floor(rnd()*7);
    for(let i=0;i<n;i++){
      const dx=Math.round(rr(-R,R)), dz=Math.round(rr(-R,R)), dy=Math.round(rr(-2,2));
      cv.ball(dx,dy,dz, 2+Math.floor(rnd()*3), (dy<0? P_.cloudUnder : P_.cloud));
    }
    const m=meshOf(bake(cv,.05), new THREE.MeshLambertMaterial({vertexColors:true}), false,false);
    const ang=rnd()*Math.PI*2, rad=rr(90,190), y=rr(46,86);
    m.position.set(Math.cos(ang)*rad, y, Math.sin(ang)*rad);
    m.scale.setScalar(rr(.8,2.1));
    cloudGroup.add(m);
  }
  scene.add(cloudGroup);
  /* harbour beacon / lighthouse beam */
  const beamMat=new THREE.MeshBasicMaterial({ color:0xfff0c0, transparent:true, opacity:.10,
    side:THREE.DoubleSide, depthWrite:false, blending:THREE.AdditiveBlending, toneMapped:false });
  beamPivot=new THREE.Group(); beamPivot.position.set(37,6+24.5,-9);
  [0,Math.PI].forEach(a=>{
    const geo=new THREE.ConeGeometry(7,150,4,1,true);
    geo.rotateZ(Math.PI/2); geo.translate(75,0,0);
    const cm=new THREE.Mesh(geo, beamMat); cm.rotation.y=a; beamPivot.add(cm);
  });
  scene.add(beamPivot);
  const b2=new THREE.MeshBasicMaterial({ color:0xffd7a0, transparent:true, opacity:.12,
    side:THREE.DoubleSide, depthWrite:false, blending:THREE.AdditiveBlending, toneMapped:false });
  beaconPivot=new THREE.Group(); beaconPivot.position.set(...beaconPos);
  const g2=new THREE.ConeGeometry(3.4,52,4,1,true); g2.rotateZ(Math.PI/2); g2.translate(26,0,0);
  beaconPivot.add(new THREE.Mesh(g2,b2)); scene.add(beaconPivot);
  beamMats=[beamMat,b2];
}
let smokeRef=null, cloudGroup=null, beamPivot=null, beaconPivot=null, beamMats=[];

/* ══════════════════════════════════════════════════════════════
   9 · time of day
   ══════════════════════════════════════════════════════════════ */
const KEYS=[
  { t:0.00, n:'first light', el:1.5, az:-98, sun:0xff8a5c, si:1.35, hs:0x35506f, hg:0x25303c, hi:.78,
    top:0x14243f, mid:0x585878, bot:0xd9825a, sea:0x16324a, foam:0xf3ddd0, fog:0x63566b, fd:.0088, lamp:.85, star:.55, wind:'SW 5 kn' },
  { t:0.24, n:'midday', el:62, az:-34, sun:0xfff2d8, si:3.15, hs:0x8fb6dc, hg:0x6b6d63, hi:1.12,
    top:0x2a6aa6, mid:0x84bcda, bot:0xcfe3ec, sea:0x1d5c78, foam:0xffffff, fog:0x9dc0d6, fd:.0038, lamp:.08, star:0, wind:'WSW 12 kn' },
  { t:0.48, n:'golden hour', el:5.5, az:-64, sun:0xff9c3f, si:2.85, hs:0x8696b6, hg:0x5c4f3e, hi:.82,
    top:0x1f4674, mid:0xdb8a55, bot:0xf9c07a, sea:0x183f5a, foam:0xffe0c0, fog:0xd9955f, fd:.0072, lamp:.42, star:.04, wind:'SW 9 kn' },
  { t:0.63, n:'dusk', el:-2, az:-84, sun:0xff6f42, si:.55, hs:0x2f415e, hg:0x2a2a32, hi:.62,
    top:0x0e1930, mid:0x7c4152, bot:0xcf6a44, sea:0x112a42, foam:0xdfe6ea, fog:0x513f52, fd:.0096, lamp:1, star:.55, wind:'SW 4 kn' },
  { t:0.80, n:'night', el:-16, az:-100, sun:0x9ab8ff, si:.16, hs:0x16233c, hg:0x10161d, hi:.34,
    top:0x040814, mid:0x0b1526, bot:0x22304a, sea:0x081727, foam:0x9fb4c2, fog:0x0d1727, fd:.0108, lamp:1, star:1, wind:'W 3 kn' },
  { t:1.00, n:'first light', el:1.5, az:-98, sun:0xff8a5c, si:1.35, hs:0x35506f, hg:0x25303c, hi:.78,
    top:0x14243f, mid:0x585878, bot:0xd9825a, sea:0x16324a, foam:0xf3ddd0, fog:0x63566b, fd:.0088, lamp:.85, star:.55, wind:'SW 5 kn' },
];
const cA=new THREE.Color(), cB=new THREE.Color();
function lerpKey(t){
  let i=0; while(i<KEYS.length-2 && t>KEYS[i+1].t) i++;
  const a=KEYS[i], b=KEYS[i+1], u=THREE.MathUtils.smoothstep(t,a.t,b.t);
  const mixC=(k,hex)=>cA.setHex(a[k]).lerp(cB.setHex(b[k]),hex);
  const out={ n: u<.5?a.n:b.n, el:THREE.MathUtils.lerp(a.el,b.el,u), az:THREE.MathUtils.lerp(a.az,b.az,u),
    si:THREE.MathUtils.lerp(a.si,b.si,u), hi:THREE.MathUtils.lerp(a.hi,b.hi,u),
    fd:THREE.MathUtils.lerp(a.fd,b.fd,u), lamp:THREE.MathUtils.lerp(a.lamp,b.lamp,u),
    star:THREE.MathUtils.lerp(a.star,b.star,u), sun:new THREE.Color(), hs:new THREE.Color(),
    hg:new THREE.Color(), top:new THREE.Color(), mid:new THREE.Color(), bot:new THREE.Color(),
    sea:new THREE.Color(), foam:new THREE.Color(), fog:new THREE.Color(), wind:u<.5?a.wind:b.wind };
  ['sun','hs','hg','top','mid','bot','sea','foam','fog'].forEach(k=>out[k].copy(mixC(k)));
  return out;
}
let tod=0.47, lampFactor=.42;
function applyTod(t){
  const k=lerpKey(t);
  const el=THREE.MathUtils.degToRad(k.el), az=THREE.MathUtils.degToRad(k.az);
  sunDir.set(Math.cos(el)*Math.sin(az), Math.sin(el), Math.cos(el)*Math.cos(az)).normalize();
  sun.position.copy(sunDir).multiplyScalar(150); sun.color.copy(k.sun); sun.intensity=k.si;
  const day=Math.max(0, Math.min(1, (k.el+4)/16));
  fill.intensity=0.16+0.30*(1-day);
  hemi.color.copy(k.hs); hemi.groundColor.copy(k.hg); hemi.intensity=k.hi; amb.intensity=.10+.08*(1-day);
  scene.fog.color.copy(k.fog); scene.fog.density=k.fd;
  renderer.setClearColor(k.fog);
  const u=sky.material.uniforms;
  u.uTop.value.copy(k.top); u.uMid.value.copy(k.mid); u.uBot.value.copy(k.bot);
  u.uSunCol.value.copy(k.sun); u.uSunDir.value.copy(sunDir); u.uUp.value=THREE.MathUtils.clamp(k.el/12,0,1);
  seaTint.value.copy(k.sea); foamCol.value.copy(k.foam);
  if(seaFine) seaFine.material.color.copy(seaFine.material.color).setHex(0xffffff).lerp(k.sea, .25);
  sunMesh.position.copy(sunDir).multiplyScalar(720);
  sunMesh.material.color.copy(k.sun).lerp(new THREE.Color(0xffffff), day*.35);
  sunGlow.position.copy(sunMesh.position);
  sunGlow.material.color.copy(k.sun); sunGlow.scale.setScalar(340+160*(1-day));
  moonMesh.position.copy(sunDir).multiplyScalar(-720);
  moonMesh.visible = k.el < 6;
  stars.material.opacity = k.star;
  lampFactor=k.lamp;
  matLamp.color.setScalar(0.32+0.68*lampFactor);
  beamMats.forEach(m=>m.opacity=(0.028+0.12*lampFactor));
  lampGlows.forEach(s=>{ s.visible=lampFactor>0.05;
    s.material.opacity=THREE.MathUtils.clamp(lampFactor*1.1,0,1); });
  if(smokeRef) smokeRef.material.color.copy(k.foam).lerp(new THREE.Color(0x6f7580), .55);
  /* clock */
  const hrs=(5 + t*26) % 24;
  document.getElementById('clock').textContent=
    String(Math.floor(hrs)).padStart(2,'0')+':'+String(Math.floor((hrs%1)*60)).padStart(2,'0');
  document.getElementById('phase').textContent=k.n;
  document.getElementById('rWind').textContent=k.wind;
}

/* ══════════════════════════════════════════════════════════════
   10 · build in steps so the loader feels honest
   ══════════════════════════════════════════════════════════════ */
const lfill=document.getElementById('lfill'), lstat=document.getElementById('lstat');
let totalVox=0;
const frame=()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));

async function buildAll(){
  const steps=[
    ['raising the sky over the bar', async()=>{ totalVox+=buildSky(); }],
    ['letting the flood come in',    async()=>{ totalVox+=buildSea(); }],
    ['dressing the quay with granite', async()=>{ const r=buildQuay();
        worldSolid=r.v; /* stash for water holes */ await frame(); }],
    ['piling Number Three Jetty',   async()=>{ quayVox=buildQuay(); }],
  ];
  /* (see run() below — real ordering) */
}
let quayVox=null, dockVox=null, townVox=null, bwVox=null, lhVox=null;

/* the real, ordered pipeline */
async function run(){
  const steps=[
    ['raising the sky over the bar',       async()=>{ totalVox+=buildSky(); }],
    ['quarrying the granite quay',          async()=>{ quayVox=buildQuay(); totalVox+=quayVox.vox; }],
    ['piling Number Three Jetty',           async()=>{ dockVox=buildDock(); totalVox+=dockVox.vox; }],
    ['terracing the town up the hill',      async()=>{ townVox=buildTown(); totalVox+=townVox.vox; }],
    ['throwing out the breakwater',         async()=>{ bwVox=buildBreakwater(); totalVox+=bwVox.vox; }],
    ['tipping the light on the point',      async()=>{ lhVox=buildLighthouse(); totalVox+=lhVox.vox; }],
    ['letting the flood in',                async()=>{
        worldSolid = quayVox.v;                                  /* water needs to know where stone is */
        const v=new Vox();
        v.block(...[], 0,0,0,0,0,0); /* noop guard */
        totalVox += buildSea(); }],
    ['fitting out the barque Aurora',       async()=>{ const r=buildShip(); totalVox+=r.vox; }],
    ['calling the gulls, lighting the lamps', async()=>{
        buildLife(townVox.chimneys, [-3,7,-11]);
        /* merge all static stone into a single draw call */
        const all=new Vox();
        [quayVox.v, dockVox.v, townVox.v, bwVox.v, lhVox.v].forEach(s=>{
          s.list.forEach(q=>all.set(q[0],q[1],q[2],q[3]));
        });
        const m=meshOf(bake(all,.085), matSolid);
        scene.add(m);
        lampMesh=meshOf(bake(lamps,.02), matLamp, false, false);
        scene.add(lampMesh);
        /* edge foam */
        const f=[];
        [...bwVox.foam, ...lhVox.foam].forEach(p=>f.push(p));
        for(let z=-44;z<=44;z+=3){ f.push([-13.4,0.15,z,1,1]); }
        foamPatches(f, scene, 0xf7fbff);
      }],
    ['trimming by the light of the lamp',   async()=>{ applyTod(tod); }],
  ];
  for(let i=0;i<steps.length;i++){
    lstat.innerHTML='<b>'+steps[i][0]+'</b> …';
    lfill.style.width=Math.round((i/steps.length)*100)+'%';
    await frame();
    await steps[i][1]();
  }
  lfill.style.width='100%';
  lstat.innerHTML='<b>anchor watch</b> — hoisting colours';
  document.getElementById('rVox').textContent = totalVox.toLocaleString();
  await frame(); await new Promise(r=>setTimeout(r,320));
  document.getElementById('loader').classList.add('gone');
  document.body.classList.add('ready');
  introUntil = performance.now()+2300;
}
/* helper used by the quay/jetty pass (water mask) */
Vox.prototype.copy = function(o){ o.list.forEach(q=>this.set(q[0],q[1],q[2],q[3])); };

/* ══════════════════════════════════════════════════════════════
   11 · the moving parts
   ══════════════════════════════════════════════════════════════ */
function waveJS(x,z,t){
  return Math.sin(x*0.225+t*1.05)*0.30 + Math.sin(z*0.290-t*0.92)*0.22
       + Math.sin((x+z)*0.130+t*0.61)*0.20 + Math.sin((x-z*0.7)*0.45+t*1.8)*0.07;
}
let sailsUp=1, sailsTarget=1, gullsOn=true, beamOn=true, autoOrbit=true, playingTod=true;
let introUntil=0, lastInteract=0;
const clock=new THREE.Clock();
let fAcc=0, fCnt=0;

function tick(){
  requestAnimationFrame(tick);
  const dt=Math.min(.05, clock.getDelta()), T=clock.elapsedTime;
  uTime.value=T;

  if(performance.now()>introUntil && !controls.enabled){ controls.enabled=true; }
  if(playingTod && performance.now()>introUntil){
    tod=(tod+dt/210)%1; slider.value=Math.round(tod*1000); applyTod(tod); setSliderFill();
  }

  /* the ship rides the sea */
  if(shipGroup){
    const sx=shipGroup.position.x, sz=shipGroup.position.z;
    const h=waveJS(sx,sz,T), hx=waveJS(sx+4,sz,T)-waveJS(sx-4,sz,T), hz=waveJS(sx,sz+6,T)-waveJS(sx,sz-6,T);
    shipGroup.position.y=h*0.52-0.10;
    shipGroup.rotation.z=THREE.MathUtils.lerp(shipGroup.rotation.z, -hx*0.055 + Math.sin(T*0.43)*0.006, .05);
    shipGroup.rotation.x=THREE.MathUtils.lerp(shipGroup.rotation.x,  hz*0.040 + Math.sin(T*0.31)*0.005, .05);
    sails.forEach(s=>{ s.scale.y=1-sailsUp*0.90; s.scale.z=1-sailsUp*0.55; });
    if(windowWaver) windowWaver.rotation.z=-1.4-0.9*Math.sin(T*3.4);
  }
  /* sails easing */
  sailsTarget+=(sailsUpTarget-sailsTarget)*Math.min(1,dt*3.2);
  /* windmill */
  if(windmill) windmill.rotation.z-=dt*0.55;
  /* gulls */
  gulls.forEach((g,i)=>{
    g.visible=gullsOn; if(!gullsOn) return;
    const d=g.userData, a=T*d.sp+d.ph;
    g.position.set(Math.cos(a)*d.r, d.y+Math.sin(T*0.7+d.ph)*1.6, Math.sin(a)*d.r*0.8);
    g.rotation.y=-a+Math.PI/2;
    const f=Math.sin(T*7+d.ph)*0.85;
    d.wl.rotation.x=f; d.wr.rotation.x=-f;
  });
  /* lamps breathe */
  lampGlows.forEach(s=>{ const f=0.86+0.14*Math.sin(T*7.3+s.userData.ph)+0.05*Math.sin(T*23+s.userData.ph);
    s.scale.setScalar(s.userData.base*f*(0.75+0.5*lampFactor)); });
  if(beamPivot){ beamPivot.visible=beamOn; beamPivot.rotation.y-=dt*0.62;
    beaconPivot.visible=beamOn; beaconPivot.rotation.y+=dt*0.9; }
  /* clouds drift */
  if(cloudGroup) cloudGroup.rotation.y+=dt*0.0016;
  /* chimney smoke */
  if(smokeRef){
    const {src,m,c}=smokeRef.userData; const base=new THREE.Color(0xffffff);
    let i=0;
    src.forEach((e,ei)=>{ for(let k=0;k<7;k++){
      const p=((T*0.20 + k/7 + ei*0.17)%1);
      const s=0.55+p*2.1;
      const sway=Math.sin(p*5+ei+k)*0.9*p;
      m.makeScale(s,s*(1-p*0.25),s);
      m.setPosition((e[0]!==undefined?e[0]:e.x)+sway, (e[1]!==undefined?e[1]:e.y)+p*8.5, (e[2]!==undefined?e[2]:e.z)+Math.cos(p*4+ei)*0.8*p);
      smokeRef.setMatrixAt(i,m);
      c.copy(smokeRef.material.color).lerp(new THREE.Color(0xffffff), 0.55).offsetHSL(0,0,-p*0.15);
      smokeRef.setColorAt(i,c); i++;
    }});
    smokeRef.instanceMatrix.needsUpdate=true;
    if(smokeRef.instanceColor) smokeRef.instanceColor.needsUpdate=true;
  }
  /* compass */
  const ang=Math.atan2(camera.position.x-controls.target.x, camera.position.z-controls.target.z);
  needle.style.transform='rotate('+(-ang*180/Math.PI)+'deg)';

  /* idle auto-orbit */
  if(autoOrbit){
    const idle=performance.now()-lastInteract;
    controls.autoRotate = performance.now()>introUntil && idle>3600;
    controls.autoRotateSpeed=0.32;
  } else controls.autoRotate=false;

  if(controls.enabled) controls.update();
  else if(performance.now()<introUntil){
    const t=THREE.MathUtils.smoothstep(performance.now()-introUntil+2300, 0, 2300);
    camera.position.lerpVectors(new THREE.Vector3(126,74,138), CAM_A, t*t*(3-2*t));
    camera.lookAt(TGT_A);
  }
  renderer.render(scene,camera);

  fAcc+=dt; fCnt++;
  if(fAcc>0.6){ document.getElementById('rFps').textContent=Math.round(fCnt/fAcc); fAcc=0; fCnt=0; }
  const tide=1.42+Math.sin(T*0.12)*1.1;
  document.getElementById('rTide').textContent=(tide>=0?'+':'')+tide.toFixed(2)+' m';
  document.querySelector('#tidebar i').style.width=Math.round(((tide+1.2)/4.4)*100)+'%';
}

/* ══════════════════════════════════════════════════════════════
   12 · interface
   ══════════════════════════════════════════════════════════════ */
const slider=document.getElementById('tod'), needle=document.getElementById('needle');
function setSliderFill(){ slider.style.setProperty('--p',(slider.value/10).toFixed(1)+'%'); }
slider.addEventListener('input',()=>{ tod=slider.value/1000; applyTod(tod); setSliderFill(); playingTod=false;
  document.querySelector('[data-act=cycle]').classList.remove('on'); setSliderFill(); });
setSliderFill();

let sailsUpTarget=0;
document.querySelectorAll('#dock button').forEach(b=>{
  b.addEventListener('click',()=>{
    const a=b.dataset.act;
    if(a==='sails'){ const on=!b.classList.contains('on'); b.classList.toggle('on',on);
      sailsUpTarget = on?0:1; b.querySelector('span').textContent = on?'Sails full':'Furled'; }
    if(a==='light'){ beamOn=!beamOn; b.classList.toggle('on',beamOn); }
    if(a==='gulls'){ gullsOn=!gullsOn; b.classList.toggle('on',gullsOn); }
    if(a==='cycle'){ playingTod=!playingTod; b.classList.toggle('on',playingTod); }
    if(a==='orbit'){ autoOrbit=!autoOrbit; b.classList.toggle('on',autoOrbit); }
    if(a==='reset'){ lastInteract=0;
      const from=camera.position.clone(), fromT=controls.target.clone(), t0=performance.now();
      (function glide(){ const k=Math.min(1,(performance.now()-t0)/900), e=1-Math.pow(1-k,3);
        camera.position.lerpVectors(from,CAM_A,e); controls.target.lerpVectors(fromT,TGT_A,e);
        if(k<1) requestAnimationFrame(glide); })(); }
  });
});
['pointerdown','wheel','touchstart'].forEach(ev=>renderer.domElement.addEventListener(ev,()=>{
  lastInteract=performance.now(); controls.enabled = performance.now()>introUntil;
}, {passive:true}));

/* hover labels */
const HOT=[
  { p:[10,12,-3],  s:[28,30,52], t:'“Aurora of Whitby”', d:'Barque, 214 tons — arrived on the ebb, bound for the Baltic with coal.' },
  { p:[-8,8,0],    s:[16,10,80], t:'Number Three Jetty', d:'Elm-piled, 1838. Lines thrown, gangway down — she is fast.' },
  { p:[37,20,-9],  s:[16,44,16], t:'St. Brendan’s Light', d:'Occulting white, 21 miles. The keeper has the lamp up already.' },
  { p:[10,0,32],   s:[46,8,14],  t:'The Outer Breakwater',d:'Rubble from the west quarry. She came round its head with courses still full.' },
  { p:[-66,26,30], s:[12,16,12], t:'Mill on the shoulder', d:'Wind’s from the sea tonight — the sails are going round.' },
  { p:[-46,16,-2], s:[46,26,80], t:'Old Meridian Town',  d:'Terraces stacked up the hill, chimneys smoking before dark.' },
];
const hotMeshes=HOT.map(h=>{
  const m=new THREE.Mesh(new THREE.BoxGeometry(...h.s), new THREE.MeshBasicMaterial({visible:false}));
  m.position.set(...h.p); scene.add(m); m.userData.h=h; return m;
});
const ray=new THREE.Raycaster(), ptr=new THREE.Vector2(-2,-2);
const tip=document.getElementById('tip'), tipB=tip.querySelector('b'), tipI=tip.querySelector('i');
let px=0,py=0,frameNo=0;
addEventListener('pointermove',e=>{ px=e.clientX; py=e.clientY; ptr.set((e.clientX/innerWidth)*2-1, -(e.clientY/innerHeight)*2+1); });
function hoverTest(){
  if(innerWidth<700) return;
  ray.setFromCamera(ptr,camera);
  const hit=ray.intersectObjects(hotMeshes,false)[0];
  if(hit){ tipB.textContent=hit.object.userData.h.t; tipI.textContent=hit.object.userData.h.d;
    tip.style.left=px+'px'; tip.style.top=py+'px'; tip.classList.add('on'); }
  else tip.classList.remove('on');
}

addEventListener('resize',()=>{
  camera.aspect=innerWidth/innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight);
});

/* ══════════════════════════════════════════════════════════════
   13 · go
   ══════════════════════════════════════════════════════════════ */
run().then(()=>{
  tick();
  setInterval(()=>{ frameNo++; if(frameNo%2===0) hoverTest(); }, 16);
});
</script>
</body>
</html>
```

**What's in there**

- **A real voxel engine, hand-built:** every solid in the scene is authored into an occupancy set, then baked to a single mesh per material group with **hidden-face culling** and per-face colour jitter, so the whole harbour (quarry-dressed quay, terraced hillside town, customs house with a lit clock, church, banded lighthouse, breakwater beacon) draws in very few calls.
- **Two-layer animated sea** — instanced cubes displaced by a shared GLSL wave function, with depth-tinted cells (pale turquoise over the shoals, ink in the basin) and foam blooming on the crests and along the walls.
- **The barque herself:** hollowed hull with a red coppery bottom, ochre waist strake, gunports, sheer and tumblehome from a profile curve; three raked masts, yards, bellied square sails that *gather in* when you furl them, jibs, a fore-and-aft spanker, shrouds and stays, a procedurally waving ensign, a galley chimney whose voxel smoke drifts with the wind, and a foam wake parented to her so she leaves it while riding the swell. Mooring lines and a gangway are solved in world space to the jetty, and someone on the quay is waving.
- **A day you can scrub:** dawn → midday → golden hour → dusk → night, interpolating sun elevation, sky gradient (with a real sun-glow term in the sky shader), fog density and colour, sea tint, star opacity, and lamp emissives — every lantern, window and clock face brightens as the sun drops, and the lighthouse beam sweeps harder.
- **Controls:** drag / scroll / right-drag, a compass card that tracks your heading, hover the ship, the jetty, the light or the mill for harbourmaster's notes, and buttons for sails, light, gulls, sun cycle, auto-orbit and reset view.