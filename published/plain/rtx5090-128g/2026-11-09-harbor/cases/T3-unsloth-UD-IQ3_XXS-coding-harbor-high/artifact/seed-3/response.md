# A Sailing Ship Calling at a Harbour

A single-file voxel diorama — Port Anwyn, the evening before the tide turns. Everything (ship, town, sea, sky, sound) is generated in code; no external assets beyond Three.js and two webfonts.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
<title>Port Anwyn — A Sailing Ship Calling at a Harbour</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Alfa+Slab+One&family=Barlow+Condensed:wght@500;600;700&family=Barlow:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root{
    --ink:#070d11;
    --panel:rgba(9,17,22,.90);
    --panel-2:rgba(9,17,22,.78);
    --bone:#f3ecdf;
    --bone-dim:#a8b3b1;
    --amber:#f0a83c;
    --brass:#b98a44;
    --sea:#3f8f96;
    --line:rgba(240,168,60,.22);
    --disp:'Alfa Slab One', Georgia, serif;
    --cond:'Barlow Condensed', Impact, sans-serif;
    --body:'Barlow', system-ui, sans-serif;
  }
  *{box-sizing:border-box}
  html,body{margin:0;height:100%;overflow:hidden;background:var(--ink);color:var(--bone);
    font-family:var(--body);-webkit-font-smoothing:antialiased}
  canvas{display:block;position:fixed;inset:0}
  button{font:inherit;color:inherit;background:none;border:0;cursor:pointer}

  /* ---------------- HUD shell ---------------- */
  #hud{position:fixed;inset:0;z-index:10;pointer-events:none}
  #hud > *{pointer-events:auto}
  .rise{opacity:0;transform:translateY(14px);animation:rise .9s cubic-bezier(.16,.84,.28,1) forwards;animation-delay:var(--d,0s)}
  @keyframes rise{to{opacity:1;transform:none}}

  /* ---------------- Masthead ---------------- */
  .masthead{position:absolute;top:clamp(16px,2.4vw,34px);left:clamp(16px,2.4vw,36px);max-width:min(46ch,52vw);
    padding-left:14px;border-left:3px solid var(--amber)}
  .masthead .kick{font-family:var(--cond);font-weight:600;font-size:11px;letter-spacing:.34em;text-transform:uppercase;
    color:var(--amber);display:flex;gap:10px;align-items:center}
  .masthead .kick:after{content:'';height:1px;flex:1;background:linear-gradient(90deg,var(--line),transparent);max-width:110px}
  .masthead h1{font-family:var(--disp);font-weight:400;margin:.28em 0 0;line-height:.92;
    font-size:clamp(27px,3.7vw,56px);letter-spacing:-.015em;text-shadow:0 3px 22px rgba(0,0,0,.6)}
  .masthead h1 em{display:block;font-family:var(--cond);font-style:normal;font-weight:600;
    font-size:clamp(12px,1.05vw,15px);letter-spacing:.3em;text-transform:uppercase;color:var(--sea);margin-top:.85em}
  .masthead .waves{display:block;margin-top:12px;width:150px;height:14px;overflow:hidden;opacity:.75}
  .masthead .waves svg{animation:drift 9s linear infinite}
  @keyframes drift{to{transform:translateX(-40px)}}

  /* ---------------- Log / POI index ---------------- */
  .log{position:absolute;left:clamp(16px,2.4vw,36px);bottom:clamp(16px,2.4vw,32px);width:min(340px,42vw);
    background:var(--panel);border:1px solid var(--line);border-radius:3px;
    box-shadow:0 26px 60px rgba(0,0,0,.5), inset 0 1px 0 rgba(255,255,255,.05);overflow:hidden}
  .log:before{content:'';position:absolute;inset:0;pointer-events:none;
    background:repeating-linear-gradient(135deg,rgba(255,255,255,.028) 0 2px,transparent 2px 6px)}
  .log > h2{position:relative;font-family:var(--cond);font-weight:700;font-size:12px;letter-spacing:.26em;text-transform:uppercase;
    margin:0;padding:13px 16px 11px;color:var(--bone);border-bottom:1px solid rgba(255,255,255,.07);
    display:flex;justify-content:space-between;align-items:center}
  .log > h2 span{color:var(--brass);letter-spacing:.14em;font-size:10px}
  #poiList{list-style:none;margin:0;padding:6px 0;max-height:34vh;overflow:auto}
  #poiList::-webkit-scrollbar{width:5px}#poiList::-webkit-scrollbar-thumb{background:var(--brass);opacity:.4}
  #poiList li{position:relative;display:grid;grid-template-columns:26px 1fr;gap:10px;padding:9px 16px 9px 14px;cursor:pointer;
    transition:transform .26s cubic-bezier(.16,.84,.28,1),background .26s}
  #poiList li:before{content:'';position:absolute;left:0;top:6px;bottom:6px;width:2px;background:var(--amber);
    transform:scaleY(0);transform-origin:top;transition:transform .3s cubic-bezier(.16,.84,.28,1)}
  #poiList li:hover,#poiList li.on{background:rgba(240,168,60,.07);transform:translateX(6px)}
  #poiList li:hover:before,#poiList li.on:before{transform:scaleY(1)}
  #poiList .n{font-family:var(--cond);font-size:12px;letter-spacing:.1em;color:var(--brass);padding-top:3px;transition:color .25s}
  #poiList li:hover .n,#poiList li.on .n{color:var(--amber)}
  #poiList b{display:block;font-family:var(--cond);font-weight:700;font-size:15px;letter-spacing:.13em;text-transform:uppercase;line-height:1.15}
  #poiList i{display:block;font-style:normal;font-size:11.5px;letter-spacing:.05em;color:var(--bone-dim);margin-top:2px}
  .entry{border-top:1px solid rgba(255,255,255,.07);padding:13px 16px 15px;font-size:13px;line-height:1.55;color:#cbd5d2;
    min-height:86px;transition:opacity .3s}
  .entry.out{opacity:0}
  .entry b{font-family:var(--cond);color:var(--amber);letter-spacing:.18em;text-transform:uppercase;font-size:11px;display:block;margin-bottom:5px}

  /* ---------------- Instruments ---------------- */
  .instr{position:absolute;top:clamp(16px,2.4vw,34px);right:clamp(16px,2.4vw,36px);width:206px;
    background:var(--panel-2);border:1px solid var(--line);border-radius:3px;padding:14px 15px 12px;
    box-shadow:0 20px 48px rgba(0,0,0,.45)}
  .compass{display:flex;gap:13px;align-items:center}
  .compass svg{flex:0 0 74px}
  .needle{transform-origin:37px 37px;transition:transform .35s linear}
  .hdg{font-family:var(--disp);font-size:26px;line-height:1;letter-spacing:-.02em}
  .hdg small{display:block;font-family:var(--cond);font-size:10px;letter-spacing:.24em;color:var(--sea);margin-top:6px}
  .read{display:grid;grid-template-columns:1fr auto;gap:2px 8px;margin-top:13px;padding-top:11px;border-top:1px solid rgba(255,255,255,.08)}
  .read dt{font-family:var(--cond);font-size:10.5px;letter-spacing:.2em;text-transform:uppercase;color:#8b9c9b}
  .read dd{margin:0;font-family:var(--cond);font-weight:600;font-size:13px;letter-spacing:.08em;text-align:right;color:var(--bone)}
  .read dd.hot{color:var(--amber)}

  /* ---------------- Console ---------------- */
  .console{position:absolute;right:clamp(16px,2.4vw,36px);bottom:clamp(16px,2.4vw,32px);width:296px;
    background:var(--panel);border:1px solid var(--line);border-radius:3px;padding:14px 15px 15px;
    box-shadow:0 26px 60px rgba(0,0,0,.5)}
  .fld{margin-bottom:14px}
  .fld label{display:flex;justify-content:space-between;align-items:baseline;font-family:var(--cond);font-size:10.5px;
    letter-spacing:.24em;text-transform:uppercase;color:#93a4a3;margin-bottom:8px}
  .fld label b{font-family:var(--cond);font-weight:600;font-size:13px;letter-spacing:.08em;color:var(--amber)}
  input[type=range]{-webkit-appearance:none;appearance:none;width:100%;height:16px;background:transparent;cursor:pointer}
  input[type=range]::-webkit-slider-runnable-track{height:3px;background:
    linear-gradient(90deg,#173039,#3b6d74 45%,#c07a3c 76%,#1a2a3a);border-radius:2px}
  input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:13px;height:13px;margin-top:-5px;background:var(--amber);
    border-radius:2px;transform:rotate(45deg);box-shadow:0 0 0 1px rgba(0,0,0,.6),0 0 12px rgba(240,168,60,.6);
    transition:transform .2s}
  input[type=range]:hover::-webkit-slider-thumb{transform:rotate(45deg) scale(1.25)}
  input[type=range]::-moz-range-track{height:3px;background:#3b6d74;border-radius:2px}
  input[type=range]::-moz-range-thumb{width:12px;height:12px;border:0;background:var(--amber);border-radius:2px}
  .chips{display:flex;flex-wrap:wrap;gap:7px}
  .chip{position:relative;overflow:hidden;font-family:var(--cond);font-weight:600;font-size:11px;letter-spacing:.19em;
    text-transform:uppercase;padding:8px 11px;border:1px solid rgba(240,168,60,.34);color:#d9e3e0;border-radius:2px;
    transition:color .25s,border-color .25s}
  .chip:before{content:'';position:absolute;inset:0;background:var(--amber);transform:scaleX(0);transform-origin:left;
    transition:transform .3s cubic-bezier(.16,.84,.28,1);z-index:-1}
  .chip:hover{color:#12181b;border-color:var(--amber)}
  .chip:hover:before{transform:scaleX(1)}
  .chip[aria-pressed=true]{color:#12181b;border-color:var(--amber)}
  .chip[aria-pressed=true]:before{transform:scaleX(1)}
  .chip span{position:relative}
  .note{margin:12px 0 0;font-size:11.5px;line-height:1.5;color:#8fa0a0;letter-spacing:.02em}
  kbd{font-family:var(--cond);font-weight:600;background:rgba(255,255,255,.09);border-radius:2px;padding:0 4px;color:var(--bone)}

  /* ---------------- World pins ---------------- */
  .pin{position:absolute;left:0;top:0;pointer-events:none;opacity:0;transition:opacity .3s;will-change:transform}
  .pin.show{opacity:.55}.pin.show.hot,.pin.show.on{opacity:1}
  .pin .dia{position:absolute;left:-5px;top:-5px;width:10px;height:10px;background:var(--amber);transform:rotate(45deg);
    box-shadow:0 0 0 1px rgba(0,0,0,.5),0 0 14px rgba(240,168,60,.8);transition:transform .3s cubic-bezier(.16,.84,.28,1)}
  .pin.hot .dia,.pin.on .dia{transform:rotate(45deg) scale(1.55)}
  .pin .lbl{position:absolute;left:12px;top:-9px;white-space:nowrap;font-family:var(--cond);font-weight:700;font-size:11px;
    letter-spacing:.2em;text-transform:uppercase;color:var(--bone);text-shadow:0 2px 10px #000,0 0 3px #000}
  .pin .lbl:after{content:attr(data-sub);display:block;font-weight:500;letter-spacing:.1em;font-size:9.5px;color:var(--amber);opacity:0;
    transition:opacity .25s}
  .pin.hot .lbl:after,.pin.on .lbl:after{opacity:1}

  /* ---------------- Boot ---------------- */
  #boot{position:fixed;inset:0;z-index:40;background:radial-gradient(120% 90% at 70% 20%,#16303c,#050a0d 70%);
    display:flex;flex-direction:column;justify-content:center;padding-left:clamp(22px,7vw,110px);
    transition:opacity .9s ease,visibility .9s}
  #boot.done{opacity:0;visibility:hidden}
  #boot .kick{font-family:var(--cond);font-size:11px;letter-spacing:.4em;text-transform:uppercase;color:var(--amber)}
  #boot h2{font-family:var(--disp);font-weight:400;font-size:clamp(32px,7vw,86px);margin:.2em 0 .5em;line-height:.9;letter-spacing:-.02em}
  #boot .bar{width:min(360px,60vw);height:2px;background:rgba(255,255,255,.12)}
  #boot .bar i{display:block;height:100%;width:0;background:var(--amber);transition:width .25s ease}
  #boot .stat{font-family:var(--cond);font-size:12px;letter-spacing:.22em;text-transform:uppercase;color:#8ba0a0;margin-top:14px}
  #oops{position:fixed;inset:0;z-index:50;display:none;place-content:center;text-align:center;padding:32px;
    font-family:var(--cond);letter-spacing:.14em;font-size:16px;color:var(--bone-dim)}

  #fade{position:fixed;inset:0;z-index:8;pointer-events:none;transition:opacity 1.1s ease}
  #fade.wipe{background:#050a0d;opacity:1;transition:none}
  #fade.clear{opacity:0}
  body.bare #hud{opacity:0;transition:opacity .4s}

  @media (max-width:900px){ .log{width:270px} #poiList{max-height:24vh} .instr{width:176px} }
  @media (max-width:680px){
    .log,.instr{display:none}
    .console{left:12px;right:12px;bottom:12px;width:auto}
    .masthead{max-width:70vw}
  }
</style>
</head>
<body>
<canvas id="scene"></canvas>
<div id="fade" class="wipe"></div>

<div id="hud">
  <header class="masthead rise" style="--d:.15s">
    <div class="kick">Port Anwyn · Harbour Register</div>
    <h1>A Sailing Ship<br>Calling at a Harbour<em>Voxelled diorama · 1:180</em></h1>
    <span class="waves"><svg width="190" height="14" viewBox="0 0 190 14" fill="none"><path d="M0 9 Q10 3 20 9 T40 9 T60 9 T80 9 T100 9 T120 9 T140 9 T160 9 T180 9 T200 9" stroke="#3f8f96" stroke-width="1.6"/><path d="M0 13 Q10 8 20 13 T40 13 T60 13 T80 13 T100 13 T120 13 T140 13 T160 13 T180 13 T200 13" stroke="#f0a83c" stroke-width="1.2" opacity=".5"/></svg></span>
  </header>

  <section class="log rise" style="--d:.45s">
    <h2>The Anchorage <span id="clock">—</span></h2>
    <ul id="poiList"></ul>
    <div class="entry" id="entry"><b>Morning watch, 06:12</b>A ship shows off the west shoal, three hours out of Falmouth. She takes no pilot until the bell on the mole has swung twice.</div>
  </section>

  <aside class="instr rise" style="--d:.62s">
    <div class="compass">
      <svg width="74" height="74" viewBox="0 0 74 74">
        <circle cx="37" cy="37" r="30" fill="none" stroke="rgba(240,168,60,.25)"/>
        <circle cx="37" cy="37" r="22" fill="none" stroke="rgba(255,255,255,.07)"/>
        <g stroke="rgba(255,255,255,.3)" stroke-width="1">
          <path d="M37 7v6M37 61v6M7 37h6M61 37h6"/>
        </g>
        <text x="37" y="16" text-anchor="middle" font-family="Barlow Condensed" font-size="9" fill="#f0a83c" letter-spacing="1">N</text>
        <g class="needle" id="needle">
          <path d="M37 14 L41 39 L37 35 L33 39 Z" fill="#f0a83c"/>
          <path d="M37 60 L33 37 L37 41 L41 37 Z" fill="#4e6a72"/>
        </g>
        <circle cx="37" cy="37" r="2.4" fill="#f3ecdf"/>
      </svg>
      <div class="hdg"><span id="hdgNum">000°</span><small id="hdgPts">COURSE</small></div>
    </div>
    <dl class="read">
      <dt>Ship</dt><dd id="rShip">Mistral</dd>
      <dt>Sail</dt><dd id="rSail">Course set</dd>
      <dt>Wind</dt><dd id="rWind">SW 12</dd>
      <dt>Sea</dt><dd id="rSea">Moderate</dd>
      <dt>Voxels</dt><dd id="rVox">—</dd>
      <dt>Tris</dt><dd id="rTri">—</dd>
      <dt>FPS</dt><dd class="hot" id="rFps">—</dd>
    </dl>
  </aside>

  <div class="console rise" style="--d:.8s">
    <div class="fld">
      <label>Hour of the day <b id="todLabel">Golden hour</b></label>
      <input id="tod" type="range" min="0" max="1" step="0.001" value="0.80">
    </div>
    <div class="fld">
      <label>Wind in the roads <b id="windLabel">Force 3</b></label>
      <input id="wind" type="range" min="0" max="1" step="0.001" value="0.34">
    </div>
    <div class="chips">
      <button class="chip" id="bRotate" aria-pressed="true"><span>Drift</span></button>
      <button class="chip" id="bHorn"><span>Ship’s horn</span></button>
      <button class="chip" id="bBell"><span>Mole bell</span></button>
      <button class="chip" id="bSound" aria-pressed="false"><span>Sea</span></button>
      <button class="chip" id="bReset"><span>Reset view</span></button>
    </div>
    <p class="note">Drag to orbit · wheel to zoom · click the water for a wake. <kbd>1</kbd>–<kbd>5</kbd> stations, <kbd>␣</kbd> drift, <kbd>H</kbd> hide panels.</p>
  </div>

  <div id="pins"></div>
</div>

<div id="boot">
  <div class="kick">Chart no. 14 · Soundings in fathoms</div>
  <h2>Port&nbsp;Anwyn</h2>
  <div class="bar"><i id="bootBar"></i></div>
  <div class="stat" id="bootStat">Surveying the bay…</div>
</div>
<div id="oops">This scene needs WebGL — try a recent Chrome with hardware acceleration on.</div>

<script type="importmap">
{ "imports": {
  "three": "https://unpkg.com/three@0.169.0/build/three.module.js",
  "three/addons/": "https://unpkg.com/three@0.169.0/examples/jsm/"
}}
</script>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';

/* ==================================================================
   0 · SMALL TOOLBOX
   ================================================================== */
let _seed = 20447;
const rnd  = () => ((_seed = (_seed*1664525 + 1013904223) >>> 0) / 4294967296);
const rr   = (a,b) => a + rnd()*(b-a);
const ri   = (a,b) => Math.floor(a + rnd()*(b-a+1));
const pick = a => a[(rnd()*a.length)|0];
const clamp= (v,a,b) => v<a?a:v>b?b:v;
const lerp = (a,b,t) => a+(b-a)*t;
const smoothstep=(a,b,x)=>{const t=clamp((x-a)/(b-a),0,1);return t*t*(3-2*t);};

const _cc = new Map();
function rgb(hex){
  if(!_cc.has(hex)){ const c = new THREE.Color(hex); _cc.set(hex,[c.r,c.g,c.b]); }
  return _cc.get(hex);
}
function hash3(x,y,z){
  let h = (x*374761393 + y*668265263 + z*1442695041) | 0;
  h = (h ^ (h>>13)) * 1274126177;
  return ((h ^ (h>>16)) >>> 0) / 4294967295;
}
function lerpHSL(c1,c2,t,out){
  const a=new THREE.Color(c1), b=new THREE.Color(c2);
  const h1={}, h2={}; a.getHSL(h1); b.getHSL(h2);
  out.setHSL(h1.h+(h2.h-h1.t?0:0)+ (h2.h-h1.h)*t, h1.s+(h2.s-h1.s)*t, h1.l+(h2.l-h1.l)*t);
  return out;
}

/* ==================================================================
   1 · VOXEL BUILDER
   ================================================================== */
const FACES = [
  { d:[ 1,0,0], c:[[1,1,1],[1,0,1],[1,1,0],[1,0,0]] },
  { d:[-1,0,0], c:[[0,1,0],[0,0,0],[0,1,1],[0,0,1]] },
  { d:[ 0,1,0], c:[[0,1,1],[1,1,1],[0,1,0],[1,1,0]] },
  { d:[ 0,-1,0],c:[[0,0,0],[1,0,0],[0,0,1],[1,0,1]] },
  { d:[ 0,0,1], c:[[0,1,1],[0,0,1],[1,1,1],[1,0,1]] },
  { d:[ 0,0,-1],c:[[1,1,0],[1,0,0],[0,1,0],[0,0,0]] },
];
class Vox{
  constructor(){ this.m = new Map(); }
  get size(){ return this.m.size; }
  set(x,y,z,c){ this.m.set((Math.round(x))+','+(Math.round(y))+','+(Math.round(z)), c); }
  del(x,y,z){ this.m.delete(Math.round(x)+','+Math.round(y)+','+Math.round(z)); }
  has(x,y,z){ return this.m.has(Math.round(x)+','+Math.round(y)+','+Math.round(z)); }
  box(x0,x1,y0,y1,z0,z1,c){
    const a=[Math.round(x0),Math.round(x1)]; x0=Math.min(...a);x1=Math.max(...a);
    const b=[Math.round(y0),Math.round(y1)]; y0=Math.min(...b);y1=Math.max(...b);
    const d=[Math.round(z0),Math.round(z1)]; z0=Math.min(...d);z1=Math.max(...d);
    for(let x=x0;x<=x1;x++)for(let y=y0;y<=y1;y++)for(let z=z0;z<=z1;z++) this.m.set(x+','+y+','+z,c);
  }
  /** hollow rectangular shell */
  shell(x0,x1,y0,y1,z0,z1,c){
    for(let x=x0;x<=x1;x++)for(let z=z0;z<=z1;z++){ this.set(x,y0,z,c); this.set(x,y1,z,c); }
    for(let y=y0;y<=y1;y++)for(let z=z0;z<=z1;z++){ this.set(x0,y,z,c); this.set(x1,y,z,c); }
    for(let x=x0;x<=x1;x++)for(let y=y0;y<=y1;y++){ this.set(x,y,z0,c); this.set(x,y,z1,c); }
  }
  disc(cx,cz,y,r,c){
    const R=Math.round(r);
    for(let x=cx-R;x<=cx+R;x++)for(let z=cz-R;z<=cz+R;z++)
      if(Math.hypot(x-cx,z-cz)<=r+0.15) this.set(x,y,z,c);
  }
  ring(cx,cz,y,r,c){
    const R=Math.ceil(r);
    for(let x=cx-R;x<=cx+R;x++)for(let z=cz-R;z<=cz+R;z++){
      const d=Math.hypot(x-cx,z-cz); if(d<=r+0.3&&d>r-0.75) this.set(x,y,z,c);
    }
  }
  blob(cx,cy,cz,r,c){
    const R=Math.ceil(r);
    for(let x=cx-R;x<=cx+R;x++)for(let y=cy-R;y<=cy+R;y++)for(let z=cz-R;z<=cz+R;z++){
      const d=Math.hypot(x-cx,(y-cy)*1.35,z-cz);
      if(d<=r*(0.8+0.34*hash3(x,y,z))) this.set(x,y,z,c);
    }
  }
  line(x0,y0,z0,x1,y1,z1,c){
    const n=Math.ceil(Math.hypot(x1-x0,y1-y0,z1-z0));
    for(let i=0;i<=n;i++){ const t=i/n; this.set(lerp(x0,x1,t),lerp(y0,y1,t),lerp(z0,z1,t),c); }
  }
  build(){
    const pos=[],nor=[],col=[],idx=[]; let v=0;
    const K=[...this.m.keys()];
    for(let k=0;k<K.length;k++){
      const key=K[k], c=this.m.get(key), p=key.split(',');
      const x=+p[0],y=+p[1],z=+p[2];
      const sh=0.935+hash3(x,y,z)*0.13;
      const cr=c[0]*sh, cg=c[1]*sh, cb=c[2]*sh;
      for(let f=0;f<6;f++){
        const F=FACES[f];
        if(this.m.has((x+F.d[0])+','+(y+F.d[1])+','+(z+F.d[2]))) continue;
        for(let i=0;i<4;i++){
          const q=F.c[i];
          pos.push(q[0]-0.5+x, q[1]-0.5+y, q[2]-0.5+z);
          nor.push(F.d[0],F.d[1],F.d[2]);
          col.push(cr,cg,cb);
        }
        idx.push(v,v+1,v+2,v+2,v+1,v+3); v+=4;
      }
    }
    const g=new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(pos,3));
    g.setAttribute('normal',   new THREE.Float32BufferAttribute(nor,3));
    g.setAttribute('color',    new THREE.Float32BufferAttribute(col,3));
    g.setIndex(idx);
    return g;
  }
  mesh(mat,{cast=true,recv=true}={}){
    const m=new THREE.Mesh(this.build(),mat);
    m.castShadow=cast; m.receiveShadow=recv; m.frustumCulled=false;
    return m;
  }
}

/* ==================================================================
   2 · PALETTE
   ================================================================== */
const P = {
  grass:0x6f9a4e, grass2:0x638e45, grass3:0x7fae58, grassDry:0x8b9a4e,
  dirt:0x7d6045, mud:0x5f4a37,
  rock:0x777c83, rock2:0x666b72, rock3:0x8a9198, rockDark:0x4e535a,
  sand:0xd7c096, sand2:0xc6ae82,
  stone:0x9d9486, stone2:0x8b8377, stone3:0xafa596, stoneDark:0x6d675e,
  brick:0x98543f, brick2:0x844735,
  woodDark:0x48341f, wood:0x694b2f, woodLight:0x8d6a42, plank:0xa07d52, deck:0x8f6d45,
  mast:0x6d5136, mastDark:0x4a3623, yard:0x5c432b, rope:0xd2c49f,
  hullB:0x2b2018, hullM:0x4d3620, hullT:0x67472a, stripe:0xd2a75f,
  sail:0xefe6d2, sail2:0xd9c9ab, sailShade:0xc9b997,
  roof:0xa4503e, roof2:0x8b4436, slate:0x55636f, slate2:0x47535f, thatch:0xa8874e,
  wall:0xe2d8c6, wall2:0xd0c2ac, wall3:0xdccdae, wallG:0xb6c3c4,
  iron:0x2f333a, iron2:0x444a52, gold:0xc9902f,
  red:0xb44130, blue:0x2f4f7a, navy:0x27405f, green:0x3f6d43,
  white:0xe9e2d5, black:0x1a1c1f, canvas:0xd8cbb0,
  leaf:0x4f7d3b, leaf2:0x62934a, pine:0x35593a, pine2:0x406844,
  glow:0xffbe63, glowHot:0xffd79a,
};

/* ==================================================================
   3 · SCENE BOOT
   ================================================================== */
const canvas = document.getElementById('scene');
let renderer;
try{
  renderer = new THREE.WebGLRenderer({canvas, antialias:true, powerPreference:'high-performance'});
}catch(e){ document.getElementById('oops').style.display='grid'; throw e; }
renderer.setPixelRatio(Math.min(devicePixelRatio, 1.75));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
renderer.outputColorSpace = THREE.SRGBColorSpace;

const scene  = new THREE.Scene();
scene.fog    = new THREE.FogExp2(0xd6b091, 0.0060);
const camera = new THREE.PerspectiveCamera(42, innerWidth/innerHeight, 0.6, 1200);
camera.position.set(88, 54, -78);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true; controls.dampingFactor = 0.055;
controls.minDistance = 16; controls.maxDistance = 230;
controls.maxPolarAngle = 1.50; controls.minPolarAngle = 0.15;
controls.autoRotate = true; controls.autoRotateSpeed = 0.22;
controls.target.set(-2, 8, -2);

const DEF_CAM = new THREE.Vector3(48, 26.5, -42);
const DEF_TGT = new THREE.Vector3(-2, 8, -2);

/* ---- materials ---- */
const matWorld = new THREE.MeshStandardMaterial({vertexColors:true, roughness:0.96, metalness:0.01});
const matGlow  = new THREE.MeshBasicMaterial({vertexColors:true, toneMapped:true});
const matWoodSolid = new THREE.MeshStandardMaterial({vertexColors:true, roughness:.92});

const world = new Vox(), glowVox = new Vox();
const shipVox = new Vox(), shipGlow = new Vox();

/* ---- lights ---- */
const sun = new THREE.DirectionalLight(0xffffff, 2.5);
sun.castShadow = true;
sun.shadow.mapSize.set(2048,2048);
sun.shadow.camera.left=-80; sun.shadow.camera.right=80;
sun.shadow.camera.top=80;  sun.shadow.camera.bottom=-80;
sun.shadow.camera.near=30; sun.shadow.camera.far=420;
sun.shadow.bias=-0.0006; sun.shadow.normalBias=0.09;
scene.add(sun, sun.target);

const hemi = new THREE.HemisphereLight(0x86a8c8, 0x5a4a3c, 0.6);
scene.add(hemi);

const lampA = new THREE.PointLight(0xffa64d, 0, 40, 1.8); lampA.position.set(-16, 9, 12);  scene.add(lampA);
const lampB = new THREE.PointLight(0xffa64d, 0, 40, 1.8); lampB.position.set(12, 9, 12);   scene.add(lampB);
const lampC = new THREE.PointLight(0x9ecfff, 0, 90, 1.4); lampC.position.set(24, 24, -17); scene.add(lampC);

/* ==================================================================
   4 · SKY, SUN, MOON, STARS
   ================================================================== */
const skyU = {
  uTop:{value:new THREE.Color(0x3f6f9e)}, uHor:{value:new THREE.Color(0xf2b178)},
  uSunDir:{value:new THREE.Vector3(0,1,0)}, uSunTint:{value:new THREE.Color(0xffa95e)},
  uBand:{value:0.75}
};
const sky = new THREE.Mesh(
  new THREE.SphereGeometry(620, 32, 20),
  new THREE.ShaderMaterial({
    side:THREE.BackSide, depthWrite:false, fog:false, uniforms:skyU,
    vertexShader:`varying vec3 vP; void main(){ vP=position; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0); }`,
    fragmentShader:`
      varying vec3 vP; uniform vec3 uTop,uHor,uSunDir,uSunTint; uniform float uBand;
      void main(){
        vec3 d = normalize(vP);
        vec3 c = mix(uHor, uTop, pow(max(d.y,0.0), 0.58));
        float sd = max(dot(d, normalize(uSunDir)), 0.0);
        c += uSunTint * pow(sd, 4.0)  * 0.30 * uBand;
        c += uSunTint * pow(sd, 46.0) * 0.55 * uBand;
        c  = mix(c, uHor*1.06, pow(1.0-abs(d.y), 14.0)*0.7);
        c *= 1.0 - smoothstep(-0.05,-0.35,d.y)*0.55;
        gl_FragColor = vec4(c,1.0);
      }`
  })
);
sky.frustumCulled=false; scene.add(sky);

const sunDisc = new THREE.Mesh(new THREE.SphereGeometry(13,20,16),
  new THREE.MeshBasicMaterial({fog:false, transparent:true}));
sunDisc.material.color.setRGB(3.6,2.5,1.5);
scene.add(sunDisc);
const moonDisc = new THREE.Mesh(new THREE.SphereGeometry(9,18,14),
  new THREE.MeshBasicMaterial({fog:false, transparent:true, opacity:0}));
moonDisc.material.color.setRGB(1.7,1.85,2.15);
scene.add(moonDisc);

const starGeo = new THREE.BufferGeometry();
{
  const n=1400, arr=new Float32Array(n*3);
  for(let i=0;i<n;i++){
    const a=Math.random()*Math.PI*2, y=Math.random()*0.95+0.05, r=Math.sqrt(1-y*y);
    arr[i*3]=Math.cos(a)*r*540; arr[i*3+1]=y*540; arr[i*3+2]=Math.sin(a)*r*540;
  }
  starGeo.setAttribute('position', new THREE.Float32BufferAttribute(arr,3));
}
const stars = new THREE.Points(starGeo, new THREE.PointsMaterial({
  color:0xffffff, size:1.7, sizeAttenuation:false, transparent:true, opacity:0, fog:false, depthWrite:false}));
scene.add(stars);

/* ==================================================================
   5 · THE SEA
   ================================================================== */
const seaU = {
  uTime:{value:0}, uAmp:{value:0.55},
  uDeep:{value:new THREE.Color(0x0d3040)}, uMid:{value:new THREE.Color(0x1d5a63)},
  uFoam:{value:new THREE.Color(0xe8f4ea)}, uSkyRef:{value:new THREE.Color(0xf2b178)},
  uSunDir:{value:new THREE.Vector3()}, uSunCol:{value:new THREE.Color(0xff9a4d)}, uGlint:{value:0.4},
  uRip:{value:Array.from({length:6},()=>new THREE.Vector4(0,0,-999,0))},
  uFoamPts:{value:Array.from({length:8},()=>new THREE.Vector4(0,0,0,0))},
};
function patchSea(shader, isDepth){
  Object.assign(shader.uniforms, seaU);
  shader.vertexShader = `
    uniform float uTime; uniform float uAmp; uniform vec4 uRip[6];
    varying float vW; varying vec2 vWP;
    float seaH(vec2 p){
      float t=uTime; float h=0.0;
      h += sin(p.x*0.155 + t*0.85)*0.34;
      h += sin(p.y*0.128 - t*0.72)*0.27;
      h += sin((p.x+p.y)*0.104 + t*1.22)*0.22;
      h += sin((p.x*0.72-p.y*1.28)*0.285 + t*1.95)*0.11;
      for(int i=0;i<6;i++){
        vec4 r=uRip[i]; float d=length(p-r.xy); float age=t-r.z;
        if(r.w>0.0 && age>0.0 && age<3.6){
          float q=max(d-age*3.4,0.0);
          h += sin(d*1.15 - age*5.0) * exp(-age*1.25) * exp(-q*q*0.055) * smoothstep(0.0,1.4,d) * r.w * 1.5;
        }
      }
      return floor(h*uAmp/0.16 + 0.5)*0.16;
    }
  ` + shader.vertexShader.replace('#include <begin_vertex>', `
    #include <begin_vertex>
    #ifdef USE_INSTANCING
      vec2 wp = vec2(instanceMatrix[3][0], instanceMatrix[3][2]);
    #else
      vec2 wp = vec2(0.0);
    #endif
    float hh = seaH(wp);
    transformed.y += hh;
    vW = hh; vWP = wp;
  `);
  if(isDepth) return;
  shader.fragmentShader = `
    uniform vec3 uDeep,uMid,uFoam,uSkyRef,uSunDir,uSunCol; uniform float uGlint; uniform vec4 uFoamPts[8];
    varying float vW; varying vec2 vWP;
    float seaF(vec2 p,float h){
      float f = smoothstep(0.30,0.62,h);
      for(int i=0;i<8;i++){
        vec4 fp=uFoamPts[i];
        if(fp.w>0.0){
          float d=length(p-fp.xy);
          float band = 1.0 - smoothstep(fp.z*0.42, fp.z, d);
          float wob = 0.55+0.45*sin(p.x*0.82 + p.y*0.66 + uTime*2.1);
          f = max(f, band*wob*fp.w);
        }
      }
      return clamp(f,0.0,1.0);
    }
  ` + shader.fragmentShader.replace('#include <color_fragment>', `
    #include <color_fragment>
    vec3 sea = mix(uDeep, uMid, smoothstep(-0.55,0.78,vW));
    sea *= 0.88 + 0.24*smoothstep(-0.6,0.7,vW);
    sea = mix(sea, uSkyRef, 0.10);
    vec3 Vv = normalize(cameraPosition - vNormal.xyz*0.0);
    float fr = pow(1.0 - clamp(dot(normalize(vNormal), vec3(0.0,1.0,0.0)),0.0,1.0), 3.0);
    sea = mix(sea, uSkyRef, fr*0.22);
    sea = mix(sea, uFoam, seaF(vWP,vW));
    diffuseColor.rgb = sea;
  `).replace('#include <lights_fragment_end>', `
    #include <lights_fragment_end>
    vec3 rv = reflect(-normalize(uSunDir), normalize(vNormal));
    totalDiffuseLight += uSunCol * uGlint * pow(max(dot(rv, normalize(vViewPosition)),0.0), 42.0) * 1.8;
  `);
}
const seaMat = new THREE.MeshStandardMaterial({color:0xffffff, roughness:0.24, metalness:0.18});
seaMat.onBeforeCompile = s => patchSea(s,false);
const seaDepth = new THREE.MeshDepthMaterial({depthPacking:THREE.RGBADepthPacking});
seaDepth.onBeforeCompile = s => patchSea(s,true);

const SEA_STEP=1.7, SEA_N=76;
const sea = new THREE.InstancedMesh(new THREE.BoxGeometry(1.6,0.9,1.6), seaMat, SEA_N*SEA_N);
sea.customDepthMaterial = seaDepth;
sea.castShadow=false; sea.receiveShadow=true; sea.frustumCulled=false; sea.matrixAutoUpdate=false;
{
  const mtx=new THREE.Matrix4(); let i=0;
  for(let a=0;a<SEA_N;a++)for(let b=0;b<SEA_N;b++){
    const x=-62+a*SEA_STEP+rr(-0.12,0.12), z=-62+b*SEA_STEP+rr(-0.12,0.12);
    const s=rr(0.93,1.0);
    mtx.makeScale(s,rr(0.8,1.5),s); mtx.setPosition(x,0,z);
    sea.setMatrixAt(i++,mtx);
  }
}
scene.add(sea);

const farSea = new THREE.Mesh(new THREE.PlaneGeometry(1500,1500),
  new THREE.MeshStandardMaterial({roughness:0.42, metalness:0.15}));
farSea.rotation.x=-Math.PI/2; farSea.position.y=-0.5; farSea.receiveShadow=false;
scene.add(farSea);

/* JS mirror of seaH() — used for floating props */
function seaHJS(x,z,t){
  let h = Math.sin(x*0.155+t*0.85)*0.34 + Math.sin(z*0.128-t*0.72)*0.27
        + Math.sin((x+z)*0.104+t*1.22)*0.22 + Math.sin((x*0.72-z*1.28)*0.285+t*1.95)*0.11;
  return Math.round(h*seaU.uAmp.value/0.16)*0.16;
}

/* ==================================================================
   6 · LAND, TOWN, HARBOUR
   ================================================================== */
function shoreZ(x){
  if(x>=-34 && x<=24) return 11;
  if(x<-34) return 11 + (-34-x)*0.42;
  return 14 + (x-24)*0.8;
}
function townTerrace(x,z){
  if(x<-32||x>24) return null;
  if(z<=22) return 3;
  if(z<=24) return 6;
  if(z<=36) return 6;
  if(z<=38) return 9;
  if(z<=48) return 9;
  return null;
}
function landTop(x,z){
  const sz=shoreZ(x);
  if(z<sz) return null;
  const terr=townTerrace(x,z);
  if(terr!==null && z>=11) return terr;
  const d=z-sz;
  let h = 4.5 + 3.2*Math.sin(x*0.098+1.3) + 2.4*Math.cos(z*0.083-0.4) + 1.5*Math.sin((x*0.6+z*0.5)*0.17);
  h = Math.max(h, 17.5 - Math.hypot((x+14)*0.26,(z-56)*0.26));
  h = Math.max(h, 13.5 - Math.hypot((x-34)*0.30,(z-30)*0.30));
  h = Math.max(h, 15.5 - Math.hypot((x+47)*0.22,(z-26)*0.22));
  if(terr!==null) h = Math.max(terr, 3 + d*0.55);
  h = Math.min(h, 2 + d*1.0);
  return Math.max(1, Math.round(h));
}

function buildLand(){
  const B=world, cols=[];
  for(let x=-62;x<=46;x++) for(let z=-4;z<=64;z++){
    const h=landTop(x,z); if(h===null) continue; cols.push(x,z,h);
  }
  const hm=new Map();
  for(let i=0;i<cols.length;i+=3) hm.set(cols[i]+','+cols[i+1], cols[i+2]);
  const NB=[[1,0],[-1,0],[0,1],[0,-1]];
  for(let i=0;i<cols.length;i+=3){
    const x=cols[i], z=cols[i+1], h=cols[i+2];
    let lo=h, steep=false;
    for(const [dx,dz] of NB){
      const nh=hm.get((x+dx)+','+(z+dz));
      if(nh===undefined){ lo=Math.min(lo,-4); steep=true; }
      else if(nh<h-1){ lo=Math.min(lo,nh); steep=true; }
      else lo=Math.min(lo,h-1);
    }
    const terr=townTerrace(x,z);
    for(let y=h;y>=Math.max(lo,-4);y--){
      let c;
      if(y===h){
        if(terr!==null) c = (terr===3)?pick([P.stone,P.stone2,P.stone3]) : pick([P.stone,P.stone2,P.stone3,P.grass]);
        else if(h<=2) c=pick([P.sand,P.sand2]);
        else if(h>=14) c=pick([P.rock,P.rock2,P.rock3]);
        else c=pick([P.grass,P.grass2,P.grass3,P.grassDry]);
      } else if(steep && terr!==null){
        c=pick([P.stone2,P.stoneDark,P.brick,P.stone]);
      } else {
        c=pick([P.dirt,P.mud,P.rockDark,P.rock2]);
      }
      B.set(x,y,z,c);
    }
  }
}

/* ---- quay, walls, steps, jetty ---- */
function buildQuay(){
  const B=world;
  for(let x=-34;x<=24;x++) for(let z=11;z<=22;z++){
    const p=((x+z)&1)===0;
    B.set(x,3,z, p?pick([P.stone,P.stone3]):pick([P.stone2,P.stoneDark]));
    B.set(x,2,z,P.stone2); B.set(x,1,z,P.rock2);
  }
  for(let x=-34;x<=24;x++) for(let y=-5;y<=0;y++) B.set(x,y,11,(y%3===0)?P.stone3:pick([P.stone2,P.stoneDark,P.rock2]));
  /* slipway */
  for(let k=0;k<5;k++) for(let x=7;x<=11;x++) B.set(x,3-k,10-k, pick([P.stone,P.stone2,P.stoneDark]));
  /* terrace retaining walls */
  B.box(-32,24,4,6,23,24, P.brick);
  B.box(-32,24,5,5,23,24, P.stone3);
  B.box(-32,24,7,9,37,38, P.brick);
  B.box(-32,24,8,8,37,38, P.stone3);
  for(let x=-32;x<=24;x+=2){ B.set(x,6,23,P.stone3); B.set(x,9,37,P.stone3); }
  /* town paving on the middle terrace */
  for(let x=-32;x<=24;x++) for(let z=25;z<=28;z++) B.set(x,6,z, ((x&1)^(z&1))?P.stone2:P.stone);
  for(let x=-32;x<=24;x++) for(let z=39;z<=41;z++) B.set(x,9,z, pick([P.grass,P.grass2,P.grassDry]));
  /* staircases */
  [[1,2],[-17,-16]].forEach(([x0,x1])=>{
    for(let k=0;k<3;k++) B.box(x0,x1,3+k,3+k,24-k,24-k, P.stone3);
  });
  /* jetty out to the anchorage */
  for(let z=-7;z<=11;z++) for(let x=2;x<=6;x++)
    B.set(x,3,z, ((x+z)&1)?P.plank:P.woodLight);
  for(let z=-6;z<=10;z+=4) for(const x of [2,6]){ for(let y=-4;y<=2;y++){ B.set(x,y,z,P.woodDark); B.set(x+1,y,z,P.woodDark);} }
  B.box(1,7,3,3,-7,-6, P.woodLight);
  /* jetty head hut */
  hut(B, 1, -11, 4, 4, 3, {wall:P.wall2, roof:P.slate, door:[3,-6,-11]});
}

/* ---- harbour furniture ---- */
function lampPost(B,x,z,gy){
  B.box(x,gy+1,gy+6,x,gy+1,z,P.iron);
  B.box(x-1,x+1,gy+7,gy+7,x-1,x+1,P.iron2);
  B.box(x,x,gy+8,gy+8,x,x,glowHot(P.glowHot));
  B.box(x-1,x+1,gy+9,gy+9,x-1,x+1,P.iron);
  LAMPS.push(new THREE.Vector3(x,gy+8,z));
}
function glowHot(hex){ glowVox.set._g=1; return null; }
function lampGlow(x,y,z,hex){ glowVox.set(x,y,z,rgb(hex||P.glowHot)); }
function bollard(B,x,z,gy){ B.set(x,gy+1,z,P.iron); B.set(x,gy+2,z,P.iron2); B.set(x,gy+3,z,P.iron2); }
function barrel(B,x,y,z,c){
  B.box(x,x, y,   y+2, z,   c||P.wood);
  B.set(x,y+1,z,P.woodDark); B.box(x,x,y,y,z,z,P.woodDark);
}
function crate(B,x,y,z,s,c){
  B.box(x,x+s-1,y,y+s-1,z,z+s-1,c||P.woodLight);
  for(let i=0;i<s;i++){ B.set(x+i,y,z,P.woodDark); B.set(x,y+i,z,P.woodDark); }
}
function buildQuayProps(){
  const B=world;
  for(let x=-30;x<=20;x+=7) if(x<1||x>7) bollard(B,x,12,3);
  for(let x=-26;x<=22;x+=9) if(x<1||x>7) lampPost(B,x,13,3);
  for(let x=-20;x<=18;x+=13){
    crate(B,x,4,17,2,P.woodLight); if(rnd()<0.6) crate(B,x,6,17,1,P.plank);
    barrel(B,x+3,4,19); barrel(B,x+3,5,19);
    B.box(x+5,x+7,4,4,19,21, P.canvas); B.box(x+5,x+7,5,5,20,20, P.canvas);
  }
  /* fish market stalls */
  for(let k=0;k<3;k++){
    const x=-12+k*7, z=18;
    B.box(x,x+4,4,5,z,z+2,P.wood);
    for(let i=0;i<=4;i++) B.set(x+i,6,z+((i&1)?0:2), (i&1)?P.white:P.red);
    for(let i=0;i<=4;i++) B.set(x+i,6,z+1,(i&1)?P.red:P.white);
    B.box(x,x+4,6,6,z+2,z+2,P.white);
    B.box(x,x+4,7,7,z,z,P.red);
    B.box(x+1,x+3,4,4,z+1,z+1,P.sail);
  }
  /* quayside crane */
  const cx=-2, cz=14;
  B.box(cx,cx,4,8,cz,cz,P.woodDark); B.box(cx+1,cx+1,4,8,cz,cz,P.woodDark);
  B.box(cx,cx+1,8,8,cz,cz,P.woodDark);
  for(let k=1;k<=7;k++) B.set(cx+1,8+Math.round(k*0.35),cz-k,P.wood);
  B.line(cx+1,8,cz-7,cx+1,4.2,cz-7,P.rope);
  B.box(cx+1,cx+1,4,4,cz-7,cz-7,P.iron);
  /* net racks + timber stacks */
  for(let k=0;k<2;k++){
    const x=12+k*5;
    B.box(x,x,4,6,15,15,P.woodLight); B.box(x,x,4,6,19,19,P.woodLight); B.box(x,x,6,6,15,19,P.canvas);
  }
  for(let k=0;k<4;k++) B.box(16,20,4+k%2,4+k%2,15,16,P.wood);
  /* jetty lamps & clutter */
  lampPost(B,2,-5,3); lampPost(B,6,6,3);
  crate(B,3,-6+3,0,2,P.plank); barrel(B,6,4,-2);
  /* bollards along jetty */
  bollard(B,2,2,3); bollard(B,6,-2,3);
}

/* ---- moored fishing boats ---- */
const floaters=[];
function fishingBoat(B,x0,z0,gy,rot){
  const L=8;
  for(let k=0;k<L;k++){
    const t=k/(L-1);
    const w=Math.max(1, Math.round(1+2.1*Math.sin(Math.PI*Math.min(1,t*0.92+0.06))));
    for(let x=-w;x<=w;x++){
      B.set(x, gy,   z0+k, x===0?P.sand:P.woodLight);
      B.set(x, gy-1, z0+k, P.wood);
    }
  }
  B.box(0,0,gy+1,gy+4,z0+3,z0+3,P.white);
  B.box(-1,1,gy+1,gy+1,z0+3,z0+3,P.sail);
  const fx=Math.round(x0); // local coords used; world placement handled by group
}
function buildSmallBoats(){
  for(const spec of [[1,2,-3,0.15],[5,-4,1,-0.35],[-6,-4,1,0.9]]){
    const [ox,oz,rz] = spec;
    const V=new Vox();
    const L=8, w0=1;
    for(let k=0;k<L;k++){
      const t=k/(L-1);
      const w=Math.max(1, Math.round(1+2.1*Math.sin(Math.PI*Math.min(1,t*0.9+0.06))));
      for(let x=-w;x<=w;x++){ V.set(x,0,z0rel(k), x===0?P.sand:pick([P.woodLight,P.red,P.blue])); V.set(x,-1,z0rel(k),P.wood); }
    }
    V.set(0,1,3,P.white); V.set(0,2,3,P.white);
    function z0rel(k){ return k-4; }
    const g=new THREE.Group();
    const m=V.mesh(matWoodSolid); g.add(m);
    g.position.set(ox, 1.1, oz); g.rotation.y=rz;
    g.userData.wob=rr(0,6); g.userData.base=g.position.clone();
    scene.add(g); floaters.push(g);
  }
}

/* ---- windmill (animated) ---- */
let millPivot=null;
function buildWindmill(x,z,gy){
  const B=world;
  for(let y=1;y<=9;y++) B.disc(x,z,gy+y, Math.max(1.15, 3.0-y*0.17), (y&3)===0?P.stone3:pick([P.stone,P.stone2]));
  B.disc(x,z,gy+10,2.1,P.slate); B.disc(x,z,gy+11,1.3,P.slate2);
  B.box(x,x,gy+1,gy+3,x+2,x+2,P.woodDark);
  lampGlow(x,gy+2,x+2,P.glow);
  millPivot=new THREE.Group(); millPivot.position.set(x+3.1, gy+9, z);
  const bladeV=new Vox();
  bladeV.box(0,0,0,6,0,P.woodDark);
  for(let k=0;k<5;k++) bladeV.box(0,1+k,0,1+k,-1,0,P.canvas);
  bladeV.box(0,0,0,0,-1,0,P.wood);
  for(let i=0;i<4;i++){
    const arm=new THREE.Group(); arm.rotation.x=i*Math.PI/2;
    const bm=bladeV.mesh(matWoodSolid); bm.position.y=0.6; arm.add(bm); millPivot.add(arm);
  }
  scene.add(millPivot);
}

/* ---- generic hut ---- */
function hut(B,x0,z0,w,d,h,opts={}){
  const gy=opts.gy!==undefined?opts.gy:landTop(x0,z0)-1;
  const wall=opts.wall||pick([P.wall,P.wall2,P.wall3]);
  const roof=opts.roof||pick([P.roof,P.roof2,P.slate]);
  B.shell(x0,x0+w-1,gy+1,gy+h,z0,z0+d-1,wall);
  const steps=Math.floor(w/2);
  for(let i=0;i<=steps;i++){
    const y=gy+h+1+i, xa=x0+i, xb=x0+w-1-i;
    if(xb<xa){ B.box(xa-1,xa,y,y,z0-1,z0+d,roof); continue; }
    B.box(xa,xa,y,y,z0-1,z0+d,roof);
    B.box(xb,xb,y,y,z0-1,z0+d,roof);
    B.box(xa,xb,y,y,z0-1,z0-1,roof);
    B.box(xa,xb,y,y,z0+d,z0+d,roof);
    if(i===steps) B.box(xa,xb,y,y,z0-1,z0+d,P.roof2);
  }
  B.box(x0+Math.floor(w/2),x0+Math.floor(w/2), gy+h+steps+1, gy+h+steps+3, z0+1, z0+1, P.brick);
  return gy;
}
function windowsFor(x0,x1,y0,y1,z0,z1,face){
  for(let y=y0;y<=y1;y+=3) for(let s=0;s<3;s++){
    let x,z;
    if(face==='x'){ x = x0 + Math.round((x1-x0)*(s+0.5)/3); z = s%2? z0 : z1; }
    else          { z = z0 + Math.round((z1-z0)*(s+0.5)/3); x = s%2? x0 : x1; }
    for(const yy of [y,y+1]){
      world.del(x,yy,z);
      const lit = rnd()<0.55;
      if(lit){ glowVox.set(x,yy,z,rgb(y===y0?P.glowHot:P.glow)); }
      else world.set(x,yy,z,rgb(P.navy));
    }
    if(y===y0) world.set(x,y0,z,rgb(P.woodDark));
  }
}

/* ---- the town ---- */
function buildTown(){
  const B=world;
  const specs=[
    [-30,30,7,6,4,{}],[-22,29,6,7,5,{wall:P.wallG}], [-15,31,8,5,4,{roof:P.thatch}],
    [-6,29,7,7,5,{}],[3,31,6,5,4,{roof:P.slate}], [10,29,8,6,5,{}],[19,30,5,6,4,{wall:P.wall3}],
    [-27,41,6,5,4,{}],[-18,40,7,6,5,{wall:P.wall2}], [8,42,6,5,4,{roof:P.slate}],
  ];
  for(const s of specs){
    const [x,z,w,d,h,o]=s;
    const gy=landTop(x,z)-1;
    hut(B,x,z,w,d,h,o);
    windowsFor(x, x+w-1, gy+2, gy+h, z, z+d-1, 'z');
    windowsFor(x, x+w-1, gy+2, gy+h, z, z+d-1, 'x');
  }
  /* custom house + clock tower */
  const gx=0, gz=32, gy=landTop(gx,gz)-1;
  hut(B,gx-1,gz,10,7,6,{wall:P.wall2, roof:P.slate});
  B.box(2,5,gy+7,gy+15,gz+1,gz+4,P.wall);
  B.box(2,5,gy+9,gy+9,gz+1,gz+4,P.stone3);
  B.box(2,5,gy+13,gy+13,gz+1,gz+4,P.stone3);
  B.box(1,6,gy+16,gy+16,gz,gz+5,P.slate); B.box(2,5,gy+17,gy+18,gz+1,gz+4,P.slate2);
  B.box(3,4,gy+19,gy+20,gz+2,gz+3,P.slate2);
  for(const [dz,dx] of [[gz+1,4],[gz+4,3]]){
    B.box(3,4,gy+11,gy+12,dz,dz, rgb(P.glowHot)); glowVox.del(3,gy+11,dz);
  }
  glowVox.box(3,4,gy+11,gy+12,gz+1,gz+4, rgb(P.glow));
  B.box(3,4,gy+11,gy+12,gz+1,gz+4, rgb(P.navy));
  glowVox.set(3,gy+11,gz+1,rgb(P.white)); glowVox.set(4,gy+12,gz+4,rgb(P.white));
  lampGlow(4,gy+14,gz+2,P.glowHot);
  B.box(4,4,gy+14,gy+16,gz+2,gz+2,P.gold);

  /* church of St Elmo */
  const c0=hut(B,-24,44,10,7,5,{wall:P.wall, roof:P.slate});
  B.box(-20,-20,c0+6,c0+18,45,48,P.wall2);
  B.box(-21,-19,c0+19,c0+19,44,49,P.slate);
  B.box(-20,-20,c0+20,c0+22,45,48,P.slate2);
  B.box(-20,-20,c0+23,c0+25,46,47,P.slate2);
  B.box(-20,-20,c0+26,c0+26,46,47,P.gold);
  glowVox.box(-20,-20,c0+12,c0+14,45,48, rgb(P.glow));
  B.box(-20,-20,c0+12,c0+14,45,48, rgb(P.navy));
  glowVox.set(-20,c0+13,45,rgb(P.glowHot)); glowVox.set(-20,c0+13,48,rgb(P.glowHot));

  /* the keep */
  const kx=14,kz=44,ky=landTop(kx,kz)-1;
  B.shell(kx,kx+9,ky+1,ky+8,kz,kz+6,P.stone2);
  for(let x=kx;x<=kx+9;x++) for(let z=kz;z<=kz+6;z+=1) if(((x+z)&1)===0) B.set(x,ky+9,z,P.stone3);
  for(let x=kx;x<=kx+9;x+=3) B.box(x,x+1,ky+9,ky+12,kz,kz,P.stone);
  B.box(kx+4,kx+6,ky+1,ky+3,kz-1,kz-1,rgb(P.woodDark));
  glowVox.box(kx+4,kx+6,ky+1,ky+2,kz-1,kz-1,rgb(P.glow));
  for(const [ox,oz] of [[0,0],[9,0],[0,6],[9,6]]){
    B.shell(kx+ox-0,kx+ox,ky+13,ky+13,kz+oz,kz+oz,P.iron);
  }
  B.line(kx+9,ky+12,kz+3,kx+9,ky+18,kz+3,P.iron);
  buildWindmill(22,42,landTop(22,42)-1);

  /* trees */
  const spots=[[-38,16],[-44,22],[-50,30],[-40,34],[-28,20],[-8,44],[6,46],[20,36],[28,20],[32,26],[-46,44],[-52,38],[16,50],[26,48],[-34,10]];
  for(const [x,z] of spots){ const h=landTop(x,z); if(h===null) continue; (rnd()<0.6?pine:oak)(world,x,z,h); }
  for(let i=0;i<22;i++){
    const x=Math.round(rr(-58,30)), z=Math.round(rr(30,58)); const h=landTop(x,z);
    if(h===null||h<4) continue; (rnd()<0.55?pine:oak)(world,x,z,h);
  }
}
function pine(B,x,z,h){
  const H=ri(4,7); B.box(x,x,h+1,h+3,z,z,P.woodDark);
  for(let k=0;k<4;k++){
    const r=3-k*0.8, y=h+3+k*Math.ceil(r*0.8);
    for(let dx=-r;dx<=r;dx++)for(let dz=-r;dz<=r;dz++)
      if(Math.abs(dx)+Math.abs(dz)<=r+0.4) B.set(x+dx,y,z+dz,pick([P.pine,P.pine2]));
  }
}
function oak(B,x,z,h){
  const r=ri(2,3), y=h+ri(3,4);
  B.box(x,x,h+1,y-1,z,z,P.woodDark);
  for(let dx=-r;dx<=r;dx++)for(let dy=-r;dy<=r;dy++)for(let dz=-r;dz<=r;dz++)
    if(Math.hypot(dx,dy*1.2,dz)<=r+0.35*hash3(x+dx,y+dy,z+dz)) B.set(x+dx,y+dy,z+dz,pick([P.leaf,P.leaf2,P.grass]));
}

/* ---- breakwater + lighthouse ---- */
const LAMP = new THREE.Vector3(24,24,-17);
function buildMole(){
  const B=world;
  for(let z=-15;z<=14;z++){
    const cx = 24 + Math.sin((z+15)*0.06)*1.1;
    for(let y=-5;y<=4;y++){
      const half = Math.round(lerp(6.2,2.1,(y+5)/9));
      for(let x=Math.round(cx-half);x<=Math.round(cx+half);x++){
        let c = y===4 ? pick([P.stone,P.stone2,P.stone3])
                      : (hash3(x,y,z)<0.18? pick([P.stone,P.stoneDark]) : pick([P.rock,P.rock2,P.rock3,P.rockDark]));
        B.set(x,y,z,c);
      }
    }
  }
  for(let z=-12;z<=10;z+=7) lampPost(B,Math.round(24+Math.sin((z+15)*0.06)),z,4);
  for(let k=0;k<3;k++) crate(B,22,5,-4+k*5,2,P.wood);
  /* lighthouse */
  const lx=24, lz=-17;
  for(let y=-4;y<=2;y++) B.disc(lx,lz,y, 6.4-(y+4)*0.4, pick([P.rock,P.rock2,P.rockDark,P.rock3]));
  B.disc(lx,lz,3,4.0,P.stone); B.disc(lx,lz,4,3.9,P.stone2);
  for(let y=5;y<=19;y++){
    const r=3.0-(y-5)*0.055;
    const band=(y>=8&&y<=10)||(y>=14&&y<=16);
    B.disc(lx,lz,y, r, band?pick([P.red,P.roof2]):pick([P.white,0xf1ece1]));
  }
  B.ring(lx,lz,20,2.9,P.iron); B.ring(lx,lz,21,2.4,P.iron2);
  for(let a=0;a<8;a++){ const t=a/8*Math.PI*2; B.set(Math.round(lx+Math.cos(t)*2.4),22,Math.round(lz+Math.sin(t)*2.4),P.iron); }
  for(let y=22;y<=24;y++) B.disc(lx,lz,y,1.9,rgb(P.glow));
  for(let y=22;y<=24;y++) B.disc(lx,lz,y,2.1,P.iron);
  for(let a=0;a<6;a++){ const t=a/6*Math.PI*2; glowVox.set(Math.round(lx+Math.cos(t)*1.9),23,Math.round(lz+Math.sin(t)*1.9),rgb(P.glowHot)); }
  for(let y=0;y<=3;y++) B.disc(lx,lz,25+y,2.0-y*0.55,P.slate2);
  B.box(lx,lz,29,30,lz,lz,P.iron);
  B.line(lx,30,lz,lx,31.5,lz,P.gold);
  LAMP.set(lx,23,lz);
}

/* ==================================================================
   7 · THE SHIP
   ================================================================== */
const SHIP_POS = new THREE.Vector3(-12, 0, -14);
const SHIP_HEADING = 1.02;
function buildShip(){
  const B=shipVox, G=shipGlow;
  const Z0=-14, Z1=14, L=Z1-Z0;
  const prof=[[0,1.8],[0.06,3.2],[0.14,4.2],[0.28,4.9],[0.45,5.15],[0.62,5.1],[0.76,4.4],[0.88,3.1],[0.95,2.0],[1,0.9]];
  const keelP=[[0,0.3],[0.08,-1.5],[0.2,-2.6],[0.42,-3.1],[0.64,-3.1],[0.84,-2.1],[0.94,-1.0],[1,0.2]];
  const deckP=[[0,7.0],[0.14,6.4],[0.42,5.9],[0.64,5.85],[0.82,6.15],[1,6.9]];
  const S=(a,t)=>{ for(let i=1;i<a.length;i++){ if(t<=a[i][0]){ const k=(t-a[i-1][0])/(a[i][0]-a[i-1][0]); return lerp(a[i-1][1],a[i][1],k);} } return a[a.length-1][1]; };

  for(let z=Z0;z<=Z1;z++){
    const t=(z-Z0)/L;
    const hb=Math.max(0.5, Math.round(S(prof,t)));
    const yb=Math.round(S(keelP,t)), yd=Math.round(S(deckP,t));
    for(let y=yb;y<=yd;y++){
      for(let x=-hb;x<=hb;x++){
        const fx=Math.abs(x)/(hb+0.01), fy=(y-yb)/Math.max(1,yd-yb);
        if(fy<0.42 && fx>1-(0.42-fy)*1.5) continue;
        let c;
        if(y<=0) c=P.hullB;
        else if(y<3) c=P.hullM;
        else if(y<4) c=(z%3===0)?P.stripe:P.stripe;
        else c=P.hullT;
        if(y===yd) c=(z&1)?P.deck:P.plank;
        B.set(x,y,z,c);
      }
    }
    /* bulwarks */
    if(hb>1) for(const sx of [-1,1]){
      for(let y=yd+1;y<=yd+2;y++) B.set(sx*hb,y,z, (y===yd+2)?P.woodLight:P.hullT);
    }
    /* gunports */
    if(yb<0 && hb>=3 && (z%3===1) && Math.abs(z)<11){
      for(const sx of [-1,1]){
        const gx=sx*(hb);
        B.set(gx,3,z,P.black); B.set(gx,4,z,P.black);
        if(z%6===1){ B.set(gx+sx,3,z,P.iron); B.set(gx+sx,3,z,P.iron); }
      }
    }
  }
  /* wales + rail trim */
  for(let z=Z0+1;z<=Z1-1;z++){
    const hb=Math.round(S(prof,(z-Z0)/L));
    if(hb>1){ B.set(hb,4,z,P.stripe); B.set(-hb,4,z,P.stripe); }
  }
  /* forecastle + quarterdeck + poop */
  B.box(-4,4,6,7,8,12,P.deck);
  B.box(-5,5,7,8,-13,-6,P.deck);
  B.box(-4,4,9,10,-13,-11,P.plank);
  B.shell(-4,4,9,11,-13,-9,P.hullT);
  for(let x=-4;x<=4;x++) for(const zz of [-13,-9]) for(let y=9;y<=11;y++) B.set(x,y,zz,rgb(P.hullM));
  for(const z of [-12,-11,-10]) for(let y=9;y<=11;y++) glowVox.set(0,y,z,rgb(P.glow));
  for(const x of [-3,3]){ for(let y=9;y<=11;y++) glowVox.set(x,y,-13,rgb(P.glowHot)); }
  B.box(-4,4,11,11,10,10,P.woodDark);
  /* capstans, hatches, clutter */
  B.box(-1,1,6,7,-1,1,P.woodDark); B.box(0,0,8,8,0,0,P.iron);
  B.box(-2,2,6,6,3,5,P.plank); B.box(-2,2,6,6,-5,-3,P.plank);
  barrel(B,3,7,4); barrel(B,-3,7,4); barrel(B,-3,7,2);
  crate(B,3,7,-4,2,P.woodLight);
  B.box(-1,1,6,6,-8,-8,P.canvas);
  for(let a=0;a<4;a++){ barrel(B, (a%2? -5:5), 7, -6+a); }
  /* anchors hanging at the bow */
  for(const sx of [-4,4]){
    B.set(sx,5,12,P.iron); B.set(sx,4,12,P.iron); B.set(sx,3,12,P.iron);
    B.set(sx-1,3,12,P.iron); B.set(sx+1,3,12,P.iron); B.set(sx,3,13,P.iron);
    B.line(sx,5,12,sx,7,11,P.rope);
  }
  /* figurehead */
  B.set(0,4,15,P.white); B.set(0,3,15,P.white); B.set(0,2,15,P.gold);

  /* masts & yards */
  const masts=[
    {z:6,  top:29, hw:5.2, name:'fore'},
    {z:-2, top:32, hw:6.0, name:'main'},
    {z:-9, top:23, hw:3.8, name:'mizzen'},
  ];
  const rig=[];
  for(const m of masts){
    const gy = m.name==='mizzen'?9 : (m.name==='main'?9:7);
    for(let y=gy;y<=m.top;y++){
      const s = y<gy+3?1 : (y<m.top-7?1:0);
      for(let dx=-s;dx<=s;dx++) for(let dz=-s;dz<=s;dz++) B.set(dx,y,m.z+dz, (y&3)===0?P.mastDark:P.mast);
    }
    B.ring(0,m.z,m.top-5,1.6,P.mastDark);
    const yards=[
      {y:gy+4, hw:m.hw,   sail:5, belly:1.6, stripe:true},
      {y:gy+10,hw:m.hw*0.8, sail:4, belly:1.4},
      {y:gy+15,hw:m.hw*0.6, sail:0, belly:0},
      {y:gy+19,hw:m.hw*0.45,sail:0, belly:0},
    ];
    for(const yd of yards){
      if(yd.y>m.top-2) continue;
      B.box(-Math.round(yd.hw),Math.round(yd.hw), yd.y,yd.y, m.z,m.z, P.yard);
      for(const e of [-1,1]) B.set(e*Math.round(yd.hw), yd.y+1, m.z, P.yard);
      if(yd.sail>0){
        for(let x=-Math.round(yd.hw);x<=Math.round(yd.hw);x++){
          const bx=1-(x/yd.hw)**2;
          for(let k=0;k<yd.sail;k++){
            const dz=Math.round(yd.belly*Math.sqrt(Math.max(bx,0))*(1-k/yd.sail*0.45));
            let c = (Math.abs(x)%4===0)?P.sail2:P.sail;
            if(yd.stripe && k===1) c=P.stripe;
            B.set(x, yd.y-1-k, m.z+dz, c);
          }
        }
      } else {
        for(let x=-Math.round(yd.hw);x<=Math.round(yd.hw);x++){
          B.set(x,yd.y-1,m.z+1, (x&1)?P.sail:P.sailShade);
          if(Math.abs(x)<yd.hw-0.5) B.set(x,yd.y-1,m.z+2,P.sail2);
        }
      }
      rig.push([-yd.hw,yd.y,m.z, 0,m.top,m.z],[yd.hw,yd.y,m.z, 0,m.top,m.z]);
    }
    /* shrouds */
    for(const sx of [-1,1]){
      for(let i=0;i<3;i++){
        rig.push([0,m.top-3,m.z, sx*(2+i*0.9), gy, m.z-3+i*3]);
      }
    }
  }
  /* stays & backstays */
  rig.push([0,29,6, 0,11,22],[0,32,-2, 0,29,6],[0,23,-9, 0,32,-2],
           [0,32,-2, -5,9,-13],[0,32,-2, 5,9,-13],[0,29,6, 4,7,12],[0,29,6,-4,7,12],
           [0,23,-9, 0,11,10]);
  /* bowsprit */
  B.line(0,7,13, 0,11,22, P.mast);
  B.line(0,11,22, 0,12.4,26, P.mastDark);
  B.set(0,9,17,P.mast); B.set(0,10,19,P.mast);
  /* jib */
  triSail(B, {z:25,y:11},{z:8,y:27},{z:12,y:9}, 1.2);
  triSail(B, {z:22,y:11},{z:8,y:22},{z:12,y:8}, 1.0);
  function triSail(BV,p0,p1,p2,bulge){
    const minZ=Math.min(p0.z,p1.z,p2.z), maxZ=Math.max(p0.z,p1.z,p2.z);
    const minY=Math.min(p0.y,p1.y,p2.y), maxY=Math.max(p0.y,p1.y,p2.y);
    const inT=(z,y)=>{
      const d=(x1,y1,x2,y2,x3,y3,px,py)=>((x2-x1)*(py-y1)-(px-x1)*(y2-y1));
      const a=d(p0.z,p0.y,p1.z,p1.y,p2.z,p2.y,z,y);
      const b=d(p1.z,p1.y,p2.z,p2.y,p0.z,p0.y,z,y);
      const c=d(p2.z,p2.y,p0.z,p0.y,p1.z,p1.y,z,y);
      return (a>=0&&b>=0&&c>=0)||(a<=0&&b<=0&&c<=0);
    };
    for(let z=minZ;z<=maxZ;z++) for(let y=minY;y<=maxY;y++){
      if(!inT(z,y)) continue;
      const u=(z-minZ)/(maxZ-minZ), v=(y-minY)/(maxY-minY);
      const b=Math.round(bulge*Math.sin(Math.PI*u)*Math.sin(Math.PI*Math.min(1,v+0.25)));
      BV.set(b,y,z,(z&3===0)?P.sail2:P.sail);
    }
  }
  /* crew (little figures, ship scale) */
  for(const [x,z,c1] of [[2,9,P.red],[-2,-6,P.navy],[0,-11,P.white],[-4,-2,P.blue],[3,-8,P.red],[0,2,P.white]]){
    const gy=(z<-6)?10:7;
    B.set(x,gy+1,z,c1); B.set(x,gy+2,z,c1); B.set(x,gy+3,z,P.sand); B.set(x,gy+4,z,P.woodDark);
  }
  /* rigging lines */
  const g=new THREE.BufferGeometry(); const arr=[];
  for(const r of rig) arr.push(r[0],r[1],r[2],r[3],r[4],r[5]);
  g.setAttribute('position', new THREE.Float32BufferAttribute(arr,3));
  const lines=new THREE.LineSegments(g, new THREE.LineBasicMaterial({color:0x241c14, transparent:true, opacity:0.78}));
  lines.frustumCulled=false;
  return {lines};
}

/* ---- ship assembly ---- */
const shipGroup = new THREE.Group();
let ensign=null, jack=null;
function assembleShip(){
  shipGroup.position.copy(SHIP_POS);
  shipGroup.rotation.y = SHIP_HEADING;
  const m = shipVox.mesh(matWorld); shipGroup.add(m);
  const gm = shipGlow.mesh(matGlow,{cast:false,recv:false}); shipGroup.add(gm);
  const {lines} = buildShipRig();
  shipGroup.add(lines);
  ensign = makeFlag(5,3.2,'ensign'); ensign.position.set(0,24,-9.4); shipGroup.add(ensign);
  jack   = makeFlag(3.2,2,'jack');   jack.position.set(0,12.2,24.5);  shipGroup.add(jack);
  scene.add(shipGroup);
}
function buildShipRig(){ return buildShip(); }

const flagUni = {uTime:{value:0}, uAmp:{value:1}};
function flagTex(kind){
  const c=document.createElement('canvas'); c.width=128; c.height=80;
  const x=c.getContext('2d');
  x.fillStyle='#a53b2b'; x.fillRect(0,0,128,80);
  if(kind==='ensign'){
    x.fillStyle='#1f3f66'; x.fillRect(0,0,54,36);
    x.strokeStyle='#efe6d2'; x.lineWidth=5;
    x.beginPath(); x.moveTo(0,0); x.lineTo(54,36); x.moveTo(54,0); x.lineTo(0,36); x.stroke();
    x.strokeStyle='#a53b2b'; x.lineWidth=2; x.beginPath();
    x.arc(27,18,9,0,Math.PI*2); x.stroke();
    x.strokeStyle='#efe6d2'; x.lineWidth=3; x.beginPath(); x.arc(27,18,9,0,Math.PI*2); x.stroke();
    x.fillStyle='#efe6d2'; x.fillRect(78,34,4,18); x.fillRect(70,30,20,5); x.fillRect(74,52,12,4);
  } else {
    x.fillStyle='#efe6d2'; x.fillRect(0,0,128,80);
    x.fillStyle='#2f4f7a'; x.beginPath(); x.arc(64,40,24,0,Math.PI*2); x.fill();
    x.strokeStyle='#efe6d2'; x.lineWidth=6; x.beginPath(); x.arc(64,40,24,0,Math.PI*2); x.stroke();
  }
  const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; return t;
}
function makeFlag(w,h,kind){
  const geo=new THREE.PlaneGeometry(w,h,10,4); geo.translate(w/2,0,0);
  const mat=new THREE.MeshStandardMaterial({map:flagTex(kind), side:THREE.DoubleSide, roughness:.92});
  mat.onBeforeCompile=s=>{
    s.uniforms.uT=flagUni.uTime; s.uniforms.uA=flagUni.uAmp;
    s.vertexShader='uniform float uT; uniform float uA;\n'+s.vertexShader.replace('#include <begin_vertex>',
      `#include <begin_vertex>
       float k = position.x/ ${w.toFixed(1)};
       transformed.z += sin(position.x*1.5 - uT*6.0)*0.20*uA*k*k + sin(position.y*2.2 - uT*3.0)*0.05*uA*k;`);
  };
  const m=new THREE.Mesh(geo,mat); m.castShadow=false; return m;
}

/* ==================================================================
   8 · CLOUDS, GULLS, BOAT, SMOKE, GLOW SPRITES
   ================================================================== */
function glowSpriteTex(){
  const c=document.createElement('canvas'); c.width=c.height=64; const g=c.getContext('2d');
  const gr=g.createRadialGradient(32,32,0,32,32,32);
  gr.addColorStop(0,'rgba(255,255,255,1)'); gr.addColorStop(.32,'rgba(255,255,255,.42)'); gr.addColorStop(1,'rgba(255,255,255,0)');
  g.fillStyle=gr; g.fillRect(0,0,64,64);
  const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; return t;
}
const SPR = glowSpriteTex();
const sprites=[];
function addSprite(x,y,z,size,hex,kind){
  const s=new THREE.Sprite(new THREE.SpriteMaterial({map:SPR, color:new THREE.Color(hex).multiplyScalar(1.9),
    transparent:true, blending:THREE.AdditiveBlending, depthWrite:false, fog:kind==='smoke'}));
  if(kind==='smoke'){ s.material.blending=THREE.NormalBlending; s.material.color.setRGB(0.62,0.6,0.58); s.material.opacity=0.36; }
  s.scale.set(size,size,1); s.position.set(x,y,z); scene.add(s);
  return s;
}

function buildClouds(){
  const groups=[];
  for(let i=0;i<9;i++){
    const V=new Vox();
    const cx=rr(-90,90), cy=rr(38,64), cz=rr(-80,70), s=rr(1.1,2.4);
    const n=ri(5,9);
    for(let k=0;k<n;k++){
      const px=Math.round(cx+(rnd()*10-5)*s), py=Math.round(cy+(rnd()*3-1.5)*s*0.5), pz=Math.round(cz+(rnd()*8-4)*s);
      const r=Math.max(1, Math.round(1+rnd()*2.2*s));
      V.blob(px,py,pz,r, pick([0xfdf6ec,0xf2e8d8,0xe6d8c4,0xf8f0e2]));
    }
    const m=V.mesh(new THREE.MeshStandardMaterial({vertexColors:true, roughness:1}),{cast:false,recv:false});
    m.userData.spd=rr(0.4,1.1);
    scene.add(m); groups.push(m);
  }
  return groups;
}
let clouds=[];

function buildGulls(){
  const list=[];
  const mat=new THREE.MeshStandardMaterial({vertexColors:true, roughness:.85, side:THREE.DoubleSide});
  const bodyV=new Vox(); bodyV.set(0,0,0,0xf6f2ea); bodyV.set(0,0,1,0xeae5da); bodyV.set(0,0,2,0xd8d2c6);
  const wingV=new Vox(); wingV.set(1,0,0,0xffffff); wingV.set(2,0,0,0xe6e1d6); wingV.set(3,0,1,0xcfc9bd);
  for(let i=0;i<5;i++){
    const g=new THREE.Group();
    g.add(bodyV.mesh(mat,{cast:false,recv:false}));
    const wR=wingV.mesh(mat,{cast:false,recv:false}); wR.position.set(0.6,0,0);
    const wL=wingV.mesh(mat,{cast:false,recv:false}); wL.position.set(-0.6,0,0); wL.scale.x=-1;
    g.add(wR,wL); g.userData={wR,wL,a:rnd()*6.28,r:rr(16,34),h:rr(14,30),sp:rr(0.16,0.32),cx:rr(-14,14),cz:rr(-24,10)};
    scene.add(g); list.push(g);
  }
  return list;
}
let gulls=[];

function buildRowboat(){
  const V=new Vox();
  const prof=[[0,0.4],[0.2,1.1],[0.5,1.5],[0.8,1.1],[1,0.3]];
  for(let k=0;k<9;k++){
    const t=k/8; const S=(a,tt)=>{for(let i=1;i<a.length;i++){if(tt<=a[i][0]){const q=(tt-a[i-1][0])/(a[i][0]-a[i-1][1]*0+a[i-1][0]-a[i-1][0]); return lerp(a[i-1][1],a[i][1],(tt-a[i-1][0])/(a[i][0]-a[i-1][0]));}}return a[a.length-1][1];};
    const w=Math.max(1, Math.round(S(prof,t)));
    for(let x=-w;x<=w;x++){ V.set(x,0,k-4, x===0?P.sand:P.woodLight); V.set(x,-1,k-4,P.wood); }
  }
  V.set(0,1,-4,P.white);
  for(const rz of [-1,2]){ V.set(0,1,rz,P.white); V.set(0,2,rz,P.red); V.set(0,3,rz,P.sand); }
  const g=new THREE.Group(); g.add(V.mesh(matWoodSolid,{recv:false}));
  const oarV=new Vox(); for(let i=0;i<4;i++) oarV.set(0,0,i,P.woodLight);
  const oR=new THREE.Group(), oL=new THREE.Group();
  const o1=oarV.mesh(matWoodSolid,{cast:false,recv:false}); o1.position.set(0,0,0.5); oR.add(o1);
  const o2=oarV.mesh(matWoodSolid,{cast:false,recv:false}); o2.position.set(0,0,0.5); o2.scale.z=-1; oL.add(o2);
  oR.position.set(1.4,0.4,0); oL.position.set(-1.4,0.4,0);
  g.add(oR,oL); g.userData={oR,oL};
  scene.add(g);
  return g;
}
let rowboat=null;

const puffs=[];
function buildSmoke(){
  const chim=[[-27,36],[3,35],[13,32],[-19,46]];
  for(const [x,z] of chim){
    const gy=(landTop(x,z)||6)+7;
    for(let k=0;k<5;k++) puffs.push({x:x+0, y:gy+2+k*1.6, z:z+0, t:rnd()*4, sp:rr(0.7,1.3),
      s:addSprite(x, gy+2, z, 3, 0x9a968f,'smoke')});
  }
}

function buildGlows(){
  for(const p of LAMPS) addSprite(p.x,p.y,p.z, 4.2, 0xffa53c,'lamp');
  const beacon = addSprite(LAMP.x,LAMP.y,LAMP.z, 22, 0xffd79a,'lamp');
  const stern  = addSprite(SHIP_POS.x+Math.sin(SHIP_HEADING)*13, 10, SHIP_POS.z+Math.cos(SHIP_HEADING)*13, 6, 0xffb257,'lamp');
  return [beacon, stern];
}
let glows=[];

/* ---- rotating lighthouse beam ---- */
const beamGroup=new THREE.Group(); beamGroup.position.copy(LAMP);
function buildBeam(){
  const mat=new THREE.ShaderMaterial({
    uniforms:{uCol:{value:new THREE.Color(0xffd7a0)}, uI:{value:0.4}},
    transparent:true, depthWrite:false, blending:THREE.AdditiveBlending, side:THREE.DoubleSide, fog:false,
    vertexShader:`varying vec2 vU; void main(){ vU=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);} `,
    fragmentShader:`varying vec2 vU; uniform vec3 uCol; uniform float uI;
      void main(){ float a=pow(vU.y,2.2)*uI; gl_FragColor=vec4(uCol*a, a); }`
  });
  for(const sgn of [1,-1]){
    const cone=new THREE.Mesh(new THREE.ConeGeometry(9,72,22,1,true), mat);
    cone.geometry.translate(0,-36,0);
    cone.rotation.z = sgn>0 ? -Math.PI/2 : Math.PI/2;
    cone.frustumCulled=false; beamGroup.add(cone);
  }
  scene.add(beamGroup);
}

/* ==================================================================
   9 · TIME OF DAY
   ================================================================== */
const STOPS=[
 {t:0.00,name:'Deep watch', el:-16, az:210, sunC:0x24304a, sunI:0.0,  mC:0xa8c6e8, mI:0.55,
  hS:0x1b2c46, hG:0x0a1017, hI:0.42, skyT:0x050b16, skyH:0x142436, deep:0x071824, mid:0x0e2c39, foam:0xa9c0c2,
  fog:0x101f2c, fogD:0.0088, band:0.2, glow:1.0, star:1.0, exp:1.06},
 {t:0.13,name:'First light', el:1,  az:216, sunC:0xd08b62, sunI:0.55, mC:0xa8c6e8, mI:0.18,
  hS:0x46618a, hG:0x241f22, hI:0.55, skyT:0x183055, skyH:0xc07a5f, deep:0x0d2632, mid:0x1d4757, foam:0xd6c7bd,
  fog:0x6f6066, fogD:0.0085, band:0.85, glow:0.78, star:0.22, exp:1.03},
 {t:0.22,name:'Sunrise', el:6,  az:222, sunC:0xff9d55, sunI:2.1,  mC:0xa8c6e8, mI:0.0,
  hS:0x7d93b4, hG:0x45372c, hI:0.62, skyT:0x2f6196, skyH:0xf0a167, deep:0x0e3446, mid:0x26696f, foam:0xffe0c8,
  fog:0xba8f78, fogD:0.0076, band:1.0, glow:0.42, star:0.0, exp:1.0},
 {t:0.42,name:'Forenoon', el:34, az:230, sunC:0xffe6c6, sunI:2.7,  mC:0xa8c6e8, mI:0.0,
  hS:0x93b6d6, hG:0x5c4f40, hI:0.68, skyT:0x4b86bd, skyH:0xc3dce7, deep:0x0f4356, mid:0x2f7f82, foam:0xe9f3ee,
  fog:0xb8ccd6, fogD:0.0056, band:0.5, glow:0.10, star:0.0, exp:0.98},
 {t:0.56,name:'Midday', el:52, az:238, sunC:0xfff4e2, sunI:2.95, mC:0xa8c6e8, mI:0.0,
  hS:0x9cc0dd, hG:0x63564a, hI:0.72, skyT:0x4d8fce, skyH:0xd0e6f0, deep:0x114a5f, mid:0x399092, foam:0xf2fbf6,
  fog:0xc4dae2, fogD:0.0048, band:0.4, glow:0.04, star:0.0, exp:0.97},
 {t:0.70,name:'Afternoon', el:30, az:232, sunC:0xffdfae, sunI:2.75, mC:0xa8c6e8, mI:0.0,
  hS:0x94b3cf, hG:0x61513f, hI:0.64, skyT:0x4f88bd, skyH:0xdfdfc9, deep:0x104253, mid:0x358383, foam:0xf1ead8,
  fog:0xc8c3ac, fogD:0.0054, band:0.6, glow:0.16, star:0.0, exp:0.99},
 {t:0.80,name:'Golden hour', el:10, az:227, sunC:0xffb164, sunI:2.55, mC:0xa8c6e8, mI:0.0,
  hS:0x86a0c4, hG:0x5b4535, hI:0.6,  skyT:0x3f6f9e, skyH:0xf2b178, deep:0x0f3c4a, mid:0x2f7d80, foam:0xffe6cf,
  fog:0xd6b091, fogD:0.0060, band:1.0, glow:0.6, star:0.0, exp:1.0},
 {t:0.89,name:'Sunset', el:1.5, az:244, sunC:0xff7a3c, sunI:1.9,  mC:0xa8c6e8, mI:0.0,
  hS:0x6f7fa8, hG:0x4a352a, hI:0.5,  skyT:0x2c5183, skyH:0xef7f52, deep:0x0d2f3e, mid:0x215f6a, foam:0xffd2b4,
  fog:0xbe7f66, fogD:0.0082, band:1.1, glow:0.95, star:0.25, exp:1.03},
 {t:1.00,name:'Dusk', el:-12, az:210, sunC:0x2a3550, sunI:0.0,  mC:0xbcd4f0, mI:0.6,
  hS:0x1e3049, hG:0x0b1119, hI:0.42, skyT:0x070f1c, skyH:0x1a2c40, deep:0x081a26, mid:0x0f2f3d, foam:0xa9c0c2,
  fog:0x13222f, fogD:0.0090, band:0.35, glow:1.0, star:0.95, exp:1.05},
];
const S = {el:0,az:0,sunC:new THREE.Color(),mC:new THREE.Color(),hS:new THREE.Color(),hG:new THREE.Color(),
  skyT:new THREE.Color(),skyH:new THREE.Color(),deep:new THREE.Color(),mid:new THREE.Color(),foam:new THREE.Color(),
  fog:new THREE.Color(),sunDir:new THREE.Vector3(),moonDir:new THREE.Vector3()};
const state={ t:0.80, wind:0.34, rot:true, poi:null, hover:null, sound:false };

function setTime(t){
  t=clamp(t,0,1);
  let i=0; while(i<STOPS.length-2 && t>STOPS[i+1].t) i++;
  const A=STOPS[i], B=STOPS[i+1], k=smoothstep(0,1,clamp((t-A.t)/(B.t-A.t),0,1));
  const N=(a,b)=>lerp(a,b,k);
  S.el=N(A.el,B.el); S.az=N(A.az,B.az);
  S.sunC.lerpHSL(new THREE.Color(A.sunC), new THREE.Color(B.sunC), k);
  S.mC.copy(new THREE.Color(B.mC));
  S.hS.lerpHSL(new THREE.Color(A.hS), new THREE.Color(B.hS), k);
  S.hG.lerpHSL(new THREE.Color(A.hG), new THREE.Color(B.hG), k);
  S.skyT.lerpHSL(new THREE.Color(A.skyT), new THREE.Color(B.skyT), k);
  S.skyH.lerpHSL(new THREE.Color(A.skyH), new THREE.Color(B.skyH), k);
  S.deep.lerpHSL(new THREE.Color(A.deep), new THREE.Color(B.deep), k);
  S.mid.lerpHSL(new THREE.Color(A.mid),  new THREE.Color(B.mid),  k);
  S.foam.lerpHSL(new THREE.Color(A.foam),new THREE.Color(B.foam),k);
  S.fog.lerpHSL(new THREE.Color(A.fog),  new THREE.Color(B.fog),  k);
  const sunI=N(A.sunI,B.sunI), mI=N(A.mI,B.mI);
  scene.fog.color.copy(S.fog); scene.fog.density=N(A.fogD,B.fogD);
  renderer.toneMappingExposure=N(A.exp,B.exp);

  const e=THREE.MathUtils.degToRad(S.el), a=THREE.MathUtils.degToRad(S.az);
  S.sunDir.set(Math.cos(e)*Math.sin(a), Math.sin(e), Math.cos(e)*Math.cos(a)).normalize();
  S.moonDir.set(-S.sunDir.x, Math.max(0.30, -S.sunDir.y*0.9), -S.sunDir.z).normalize();

  const main = sunI>0 ? S.sunDir : S.moonDir;
  sun.position.copy(main).multiplyScalar(170);
  sun.color.copy(sunI>0 ? S.sunC : S.mC);
  sun.intensity = Math.max(sunI, mI*0.75);
  sun.target.position.set(0,0,0);
  hemi.color.copy(S.hS); hemi.groundColor.copy(S.hG); hemi.intensity=N(A.hI,B.hI);

  skyU.uTop.value.copy(S.skyT); skyU.uHor.value.copy(S.skyH);
  skyU.uSunDir.value.copy(sunI>0?S.sunDir:S.moonDir);
  skyU.uSunTint.value.copy(sunI>0?S.sunC:S.mC).lerp(S.skyH,0.25);
  skyU.uBand.value=N(A.band,B.band);

  sunDisc.position.copy(S.sunDir).multiplyScalar(430);
  sunDisc.material.opacity = clamp((S.el+4)/7,0,1);
  sunDisc.material.color.setRGB(3.9,2.6,1.45).lerp(new THREE.Color(0xffe0b0), clamp(S.el/40,0,1));
  moonDisc.position.copy(S.moonDir).multiplyScalar(430);
  moonDisc.material.opacity = clamp((0.5-S.el)/6,0,1);
  stars.material.opacity = clamp(N(A.star,B.star),0,1)*(0.75+0.25*Math.sin(performance.now()*0.0006));

  seaU.uDeep.value.copy(S.deep); seaU.uMid.value.copy(S.mid); seaU.uFoam.value.copy(S.foam);
  seaU.uSkyRef.value.copy(S.skyH);
  seaU.uSunDir.value.copy(S.sunDir); seaU.uSunCol.value.copy(S.sunC);
  seaU.uGlint.value = sunI>0 ? clamp(N(A.sunI,B.sunI)/2.4,0,1)*0.9 : 0.1;
  farSea.material.color.copy(S.mid).lerp(S.fog,0.35);
  farSea.material.emissive?.setRGB?.(0,0,0);

  const gk=N(A.glow,B.glow);
  matGlow.color.setScalar(0.18+gk*3.0);
  lampA.intensity=lampB.intensity= gk*70;
  lampC.intensity= 40+gk*260;
  for(const s of glows){ s.material.opacity=clamp(0.06+gk*0.95,0,1); }
  for(const m of beamGroup.children) m.material.uniforms.uI.value = 0.10+gk*0.42;
  document.getElementById('clock').textContent = N(A.sunI,B.sunI)>0 ? 'Day · ' + new Date(1900,1,1,Math.round(lerp(4,t*24)),Math.round((t*24%1)*60)%60).toTimeString().slice(0,5) : 'Night';
}

/* ==================================================================
   10 · POST PROCESSING
   ================================================================== */
const rt=new THREE.WebGLRenderTarget(innerWidth,innerHeight,{type:THREE.HalfFloatType, samples:4});
const composer=new EffectComposer(renderer, rt);
composer.addPass(new RenderPass(scene,camera));
const bloom=new UnrealBloomPass(new THREE.Vector2(innerWidth,innerHeight), 0.46, 0.55, 1.02);
composer.addPass(bloom);
composer.addPass(new OutputPass());
const grade=new ShaderPass({
  uniforms:{tDiffuse:{value:null},uRes:{value:new THREE.Vector2(1,1)},uT:{value:0},uVig:{value:0.9}},
  vertexShader:`varying vec2 vUv; void main(){vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);} `,
  fragmentShader:`
    uniform sampler2D tDiffuse; uniform vec2 uRes; uniform float uT,uVig; varying vec2 vUv;
    void main(){
      vec4 c=texture2D(tDiffuse,vUv);
      vec2 p=(vUv-0.5)*vec2(uRes.x/uRes.y,1.0);
      c.rgb*= 1.0 - dot(p,p)*uVig*0.62;
      float n=fract(sin(dot(vUv*uRes+uT, vec2(12.9898,78.233)))*43758.5453);
      c.rgb += (n-0.5)*0.022;
      c.r*=1.015; c.b*=1.005;
      gl_FragColor=c;
    }`
});
grade.uniforms.uRes.value.set(innerWidth,innerHeight);
composer.addPass(grade);

/* ==================================================================
   11 · POINTS OF INTEREST
   ================================================================== */
const POIS=[
  {id:'ship', n:'1', name:'Mistral', sub:'Merchant galleon', blurb:'<b>She lies to in the roads.</b> Three days out of Falmouth with a hire of tin and two live geese. No anchor goes down until the pilot has been rowed out.',
   mark:[-12,26,-14], cam:[6,12,-30], tgt:[-12,9,-14]},
  {id:'light', n:'2', name:'Lighthouse Point', sub:'The mole head', blurb:'<b>Twenty-two steps of dressed granite.</b> The keeper still winds the clockwork by hand at dusk; the lamp burns nine hundred nights of the year.',
   mark:[24,32,-17], cam:[34,22,-34], tgt:[24,18,-17]},
  {id:'quay', n:'3', name:'The Old Quay', sub:'Customs & fish market', blurb:'<b>The last crane in the county worked by hand.</b> Crates, nets and three awnings, all out before the tide comes up the apron stones.',
   mark:[-10,14,15], cam:[-6,14,-12], tgt:[-6,6,17]},
  {id:'mouth', n:'4', name:'The Mouth', sub:'Channel, 40 ft', blurb:'<b>A channel forty feet wide</b> between the mole head and the west shoal. No ship enters before the bell on the mole has swung twice.',
   mark:[6,11,-13], cam:[-14,10,-32], tgt:[8,3,-8]},
  {id:'town', n:'5', name:'The Upper Town', sub:'Keep · St Elmo · the mill', blurb:'<b>Above the second wall</b> the church keeps the hours and the mill catches what the harbour mouth cannot.',
   mark:[12,26,44], cam:[-12,34,4], tgt:[10,14,42]},
];
const pinEls=[];
function buildPins(){
  const ul=document.getElementById('poiList'), wrap=document.getElementById('pins');
  POIS.forEach((p,i)=>{
    const li=document.createElement('li');
    li.innerHTML=`<span class="n">${p.n}</span><div><b>${p.name}</b><i>${p.sub}</i></div>`;
    li.onclick=()=>focusPOI(p);
    li.onmouseenter=()=>setHover(p); li.onmouseleave=()=>setHover(null);
    ul.appendChild(li); p.li=li;

    const el=document.createElement('div');
    el.className='pin';
    el.innerHTML=`<span class="dia"></span><span class="lbl" data-sub="${p.sub}">${p.name}</span>`;
    wrap.appendChild(el); pinEls.push(el); p.pin=el;

    const m=new THREE.Mesh(new THREE.OctahedronGeometry(1.05),
      new THREE.MeshBasicMaterial({color:0xf0a83c, transparent:true, opacity:0.85, toneMapped:false, fog:false}));
    m.position.set(...p.mark); m.userData.poi=p; scene.add(m);
    const hit=new THREE.Mesh(new THREE.SphereGeometry(3.6), new THREE.MeshBasicMaterial({visible:false}));
    hit.position.set(...p.mark); hit.userData.poi=p; scene.add(hit);
    p.mark3=m; p.hit=hit;
  });
}
function setHover(p){
  if(state.hover===p) return;
  POIS.forEach(q=>{ q.li.classList.toggle('on', q===state.poi); q.li.classList.toggle('hov', q===p);
    q.pin.classList.toggle('hot', q===p); });
  state.hover=p;
  canvas.style.cursor = p ? 'pointer' : 'grab';
}
function focusPOI(p){
  state.poi=p;
  flyTo(new THREE.Vector3(...p.cam), new THREE.Vector3(...p.tgt), 1500);
  const e=document.getElementById('entry'); e.classList.add('out');
  setTimeout(()=>{ e.innerHTML=`<b>${p.name}</b>${p.blurb}`; e.classList.remove('out'); },260);
  POIS.forEach(q=>{ q.li.classList.toggle('on', q===p); q.pin.classList.toggle('on', q===p); });
  if(state.sound) bell();
}
let fly=null;
function flyTo(pos,tgt,dur=1400){
  fly={p0:camera.position.clone(), t0:controls.target.clone(), p1:pos, t1:tgt, st:performance.now(), dur};
}

/* ==================================================================
   12 · INTERACTION
   ================================================================== */
const rc=new THREE.Raycaster(), ptr=new THREE.Vector2();
const seaPlane=new THREE.Plane(new THREE.Vector3(0,1,0), -0.1);
let ripIdx=0; const ringPool=[];
const ringGeo=new THREE.RingGeometry(0.55,0.68,26); ringGeo.rotateX(-Math.PI/2);
function splash(x,z){
  seaU.uRip.value[ripIdx].set(x,z,clock.elapsedTime,1); ripIdx=(ripIdx+1)%6;
  const m=new THREE.Mesh(ringGeo, new THREE.MeshBasicMaterial({color:0xdff2ea, transparent:true, opacity:0.55,
    depthWrite:false, blending:THREE.AdditiveBlending, fog:true}));
  m.position.set(x, 0.55, z); scene.add(m); ringPool.push({m,t:0});
}
let down=null;
canvas.addEventListener('pointerdown', e=>{ down={x:e.clientX,y:e.clientY,t:performance.now()}; canvas.style.cursor='grabbing'; });
canvas.addEventListener('pointerup', e=>{
  canvas.style.cursor=state.hover?'pointer':'grab';
  if(!down) return;
  const moved=Math.hypot(e.clientX-down.x, e.clientY-down.y);
  if(moved<6 && performance.now()-down.t<500){
    ptr.set((e.clientX/innerWidth)*2-1, -(e.clientY/innerHeight)*2+1);
    rc.setFromCamera(ptr,camera);
    const hits=rc.intersectObjects(POIS.map(p=>p.hit),false);
    if(hits.length) focusPOI(hits[0].object.userData.poi);
    else{
      const v=new THREE.Vector3();
      if(rc.ray.intersectPlane(seaPlane,v)) splash(v.x,v.z);
    }
  }
  down=null;
});
canvas.addEventListener('pointermove', e=>{
  ptr.set((e.clientX/innerWidth)*2-1, -(e.clientY/innerHeight)*2+1);
  rc.setFromCamera(ptr,camera);
  const hits=rc.intersectObjects(POIS.map(p=>p.hit),false);
  setHover(hits.length?hits[0].object.userData.poi:null);
});
canvas.style.cursor='grab';

const $=id=>document.getElementById(id);
$('tod').addEventListener('input', e=>{ state.t=+e.target.value; setTime(state.t); updateTod(); });
$('wind').addEventListener('input', e=>{ state.wind=+e.target.value; seaU.uAmp.value=0.28+state.wind*0.9; updateWind(); });
$('bRotate').onclick=e=>{ state.rot=!state.rot; controls.autoRotate=state.rot; e.currentTarget.setAttribute('aria-pressed',state.rot); };
$('bReset').onclick=()=>{ flyTo(DEF_CAM.clone(), DEF_TGT.clone(), 1300); state.poi=null; POIS.forEach(q=>{q.li.classList.remove('on');q.pin.classList.remove('on');}); };
$('bHorn').onclick=()=>{ ensureAudio(); horn(); };
$('bBell').onclick=()=>{ ensureAudio(); bell(); };
$('bSound').onclick=e=>{ ensureAudio(); state.sound=!state.sound; surfGain.gain.value=state.sound?0.16:0; e.currentTarget.setAttribute('aria-pressed',state.sound); };
addEventListener('keydown', e=>{
  if(e.key>='1'&&e.key<='5'){ const p=POIS[+e.key-1]; if(p) focusPOI(p); }
  if(e.code==='Space'){ e.preventDefault(); $('bRotate').click(); }
  if(e.key==='h'||e.key==='H') document.body.classList.toggle('bare');
});

function updateTod(){
  const lbl=['Deep watch','First light','Sunrise','Forenoon','Midday','Afternoon','Golden hour','Sunset','Dusk'];
  let best=STOPS[0], d=1e9;
  for(const s of STOPS){ const q=Math.abs(s.t-state.t); if(q<d){d=q;best=s;} }
  $('todLabel').textContent=best.name;
}
function updateWind(){
  const f=Math.round(1+state.wind*8);
  $('windLabel').textContent='Force '+f;
  $('rWind').textContent='SW '+Math.round(4+state.wind*26);
  $('rSea').textContent = state.wind<0.22?'Slight':state.wind<0.45?'Moderate':state.wind<0.7?'Fresh':'Rough';
}

/* ---- audio (all synthesised) ---- */
let AC=null, surfGain=null;
function ensureAudio(){
  if(AC) return;
  AC=new (window.AudioContext||window.webkitAudioContext)();
  const len=AC.sampleRate*3, buf=AC.createBuffer(1,len,AC.sampleRate), d=buf.getChannelData(0);
  let b0=0,b1=0,b2=0;
  for(let i=0;i<len;i++){ const w=Math.random()*2-1;
    b0=0.997*b0+w*0.055; b1=0.985*b1+w*0.08; b2=0.95*b2+w*0.30;
    d[i]=(b0+b1+b2)*0.22; }
  const src=AC.createBufferSource(); src.buffer=buf; src.loop=true;
  const f=AC.createBiquadFilter(); f.type='lowpass'; f.frequency.value=520; f.Q.value=0.7;
  surfGain=AC.createGain(); surfGain.gain.value=state.sound?0.16:0;
  const lfo=AC.createOscillator(); lfo.frequency.value=0.08;
  const lg=AC.createGain(); lg.gain.value=0.09;
  lfo.connect(lg).connect(surfGain.gain); lfo.start();
  src.connect(f).connect(surfGain).connect(AC.destination); src.start();
}
function horn(){
  if(!AC) return; const t=AC.currentTime;
  const g=AC.createGain(); g.gain.setValueAtTime(0,t);
  g.gain.linearRampToValueAtTime(0.22,t+0.12); g.gain.setValueAtTime(0.22,t+1.25);
  g.gain.exponentialRampToValueAtTime(0.0001,t+2.1);
  const lp=AC.createBiquadFilter(); lp.type='lowpass'; lp.frequency.value=680;
  for(const [hz,mul] of [[92,1],[138,0.5],[184,0.22]]){
    const o=AC.createOscillator(); o.type='sawtooth'; o.frequency.value=hz*mul;
    const gg=AC.createGain(); gg.gain.value=1/mul; o.connect(gg).connect(lp); o.start(t); o.stop(t+2.2);
  }
  lp.connect(g).connect(AC.destination);
}
function bell(){
  if(!AC) return;
  for(let k=0;k<2;k++){
    const t=AC.currentTime+k*0.62;
    const o=AC.createOscillator(), o2=AC.createOscillator(), g=AC.createGain();
    o.type='sine'; o.frequency.value=784; o2.type='sine'; o2.frequency.value=1176;
    g.gain.setValueAtTime(0.0001,t); g.gain.exponentialRampToValueAtTime(0.16,t+0.012);
    g.gain.exponentialRampToValueAtTime(0.0001,t+1.5);
    o.connect(g); o2.connect(g); g.connect(AC.destination);
    o.start(t); o2.start(t); o.stop(t+1.6); o2.stop(t+1.6);
  }
}

/* ==================================================================
   13 · BUILD SEQUENCE
   ================================================================== */
const clock=new THREE.Clock();
const steps=[
  ['Charting the headlands…', ()=>{ buildLand(); }],
  ['Laying the quay stones…', ()=>{ buildQuay(); buildMole(); }],
  ['Raising the upper town…', ()=>{ buildTown(); buildQuayProps(); }],
  ['Rigging the galleon…',    ()=>{ assembleShip(); }],
  ['Trimming the tide…',      ()=>{
      const w=world.mesh(matWorld); scene.add(w);
      const g=glowVox.mesh(matGlow,{cast:false,recv:false}); scene.add(g);
      VOXCOUNT = world.size + glowVox.size + shipVox.size + shipGlow.size;
      seaU.uFoamPts.value[0].set(SHIP_POS.x, SHIP_POS.z, 11, 0.9);
      seaU.uFoamPts.value[1].set(24,-6, 6, 0.85);
      seaU.uFoamPts.value[2].set(24,-17, 9, 1.0);
      seaU.uFoamPts.value[3].set(2,0, 5, 0.45);
      seaU.uFoamPts.value[4].set(-30,11, 6, 0.4);
    }],
  ['Filling the sky…',        ()=>{
      clouds=buildClouds(); gulls=buildGulls(); rowboat=buildRowboat();
      buildSmallBoats(); buildSmoke(); buildBeam(); glows=buildGlows();
      buildPins();
    }],
  ['Sounding the hour…',      ()=>{
      setTime(state.t); seaU.uAmp.value=0.28+state.wind*0.9;
      updateTod(); updateWind();
    }],
];
let VOXCOUNT=0, si=0;
function runSteps(){
  if(si>=steps.length) return finish();
  const [label,fn]=steps[si++];
  $('bootStat').textContent=label;
  $('bootBar').style.width=(si/steps.length*100)+'%';
  requestAnimationFrame(()=>{ fn(); requestAnimationFrame(runSteps); });
}
function finish(){
  $('boot').classList.add('done');
  const f=$('fade'); f.classList.remove('wipe'); f.classList.add('clear');
  flyTo(DEF_CAM.clone(), DEF_TGT.clone(), 5200);
  setTimeout(()=>{ const p=POIS[0]; state.poi=p; p.pin.classList.add('on'); },5400);
}
requestAnimationFrame(runSteps);

/* ==================================================================
   14 · ANIMATION LOOP
   ================================================================== */
let frames=0, fpsT=0, fps=60, hudTick=0;
function tick(){
  requestAnimationFrame(tick);
  const dt=Math.min(clock.getDelta(),0.05), T=clock.elapsedTime;
  seaU.uTime.value=T; flagUni.uTime.value=T; grade.uniforms.uT.value=T*60;

  /* camera flight */
  if(fly){
    const k=Math.min(1,(performance.now()-fly.st)/fly.dur);
    const e=k<0.5?4*k*k*k:1-Math.pow(-2*k+2,3)/2;
    camera.position.lerpVectors(fly.p0,fly.p1,e);
    controls.target.lerpVectors(fly.t0,fly.t1,e);
    if(k>=1) fly=null;
  }
  controls.update();

  /* ship motion */
  const w=state.wind;
  shipGroup.position.y = seaHJS(SHIP_POS.x, SHIP_POS.z, T)*0.7 - 0.1
                       + Math.sin(T*0.62)*0.10;
  shipGroup.rotation.z = THREE.MathUtils.degToRad(1.6+w*6.5) + Math.sin(T*0.75)*0.012;
  shipGroup.rotation.x = Math.sin(T*0.47+1.1)*0.013 + Math.sin(T*0.93)*0.006;
  shipGroup.rotation.y = SHIP_HEADING + Math.sin(T*0.23)*0.022;

  /* floating props */
  for(const f of floaters){
    const p=f.userData.base;
    f.position.y = p.y + seaHJS(p.x,p.z,T)*0.85;
    f.rotation.z = Math.sin(T*0.9+f.userData.wob)*0.05 - Math.sin(T*0.6+f.userData.wob)*0.03;
    f.rotation.x = Math.sin(T*0.75+f.userData.wob)*0.04;
  }
  if(rowboat){
    const u=(Math.sin(T*0.115)*0.5+0.5);
    const A={x:3.5,z:-4.5}, C={x:-6.5,z:-11.5};
    const bx=lerp(A.x,C.x,u), bz=lerp(A.z,C.z,u) - Math.sin(u*Math.PI)*2.2;
    const dx=lerp(C.x,A.x,1)*(1-2*u)*-1, dz=(C.z-A.z)*(1-2*u)*-1;
    rowboat.position.set(bx, 1.15+seaHJS(bx,bz,T)*0.9, bz);
    const want=Math.atan2(C.x-A.x, C.z-A.z) + (u>0.5?Math.PI:0);
    rowboat.rotation.y += Math.atan2(Math.sin(want-rowboat.rotation.y), Math.cos(want-rowboat.rotation.y))*0.04;
    rowboat.rotation.z=Math.sin(T*1.5)*0.05;
    const sw=Math.sin(T*2.6)*0.55;
    rowboat.userData.oR.rotation.z=-0.35+sw; rowboat.userData.oL.rotation.z=-0.35-sw;
  }

  /* windmill, beam, clouds, gulls */
  if(millPivot) millPivot.rotation.x -= dt*(0.25+w*1.5);
  beamGroup.rotation.y += dt*0.42;
  for(const c of clouds){ c.position.x += dt*c.userData.spd*(0.3+w); if(c.position.x>120) c.position.x=-120; }
  for(const g of gulls){
    const u=g.userData; u.a+=dt*u.sp;
    const r=u.r+Math.sin(T*0.3+u.h)*4;
    g.position.set(u.cx+Math.cos(u.a)*r, u.h+Math.sin(T*0.5+u.h)*1.6, u.cz+Math.sin(u.a)*r);
    g.rotation.y=-u.a+Math.PI/2;
    const fl=Math.sin(T*7.5+u.h)*0.55;
    u.wR.rotation.z=fl; u.wL.rotation.z=-fl;
    g.rotation.z=Math.sin(u.a*2)*0.2;
  }
  /* smoke */
  for(const p of puffs){
    p.t+=dt*p.sp; if(p.t>4) p.t=0;
    const k=p.t/4;
    p.s.position.set(p.x+Math.sin(p.t*0.7)*1.6+k*4, p.y+k*8, p.z+Math.cos(p.t*0.6)*1.2+k*1.4);
    p.s.scale.setScalar(2.2+k*7);
    p.s.material.opacity = Math.sin(k*Math.PI)*0.30;
  }
  /* lamp flicker + markers */
  const fl=1+Math.sin(T*7.3)*0.035+Math.sin(T*11.7)*0.02;
  for(const s of glows) s.scale.setScalar(s.userData?.base ? s.userData.base*fl : s.scale.x);
  POIS.forEach(p=>{
    p.mark3.rotation.y+=dt*0.7; p.mark3.rotation.x+=dt*0.3;
    const hov=(state.hover===p||state.poi===p);
    p.mark3.scale.setScalar(lerp(p.mark3.scale.x, hov?1.5:0.85, 0.12));
    p.mark3.position.y = p.mark[1] + Math.sin(T*1.6+p.mark[0])*0.45;
    p.hit.position.y = p.mark3.position.y;
    const v=new THREE.Vector3(p.mark3.position.x,p.mark3.position.y,p.mark3.position.z).project(camera);
    const on = v.z<1 && (hov || true);
    const x=(v.x*0.5+0.5)*innerWidth, y=(-v.y*0.5+0.5)*innerHeight;
    p.pin.style.transform=`translate(${x.toFixed(1)}px, ${y.toFixed(1)}px)`;
    p.pin.classList.toggle('show', on);
  });
  /* click ripples */
  for(let i=ringPool.length-1;i>=0;i--){
    const r=ringPool[i]; r.t+=dt;
    const s=1+r.t*9; r.m.scale.set(s,1,s);
    r.m.position.y=0.55+seaHJS(r.m.position.x,r.m.position.z,T)*0.8;
    r.m.material.opacity=0.5*Math.max(0,1-r.t/1.5);
    if(r.t>1.5){ scene.remove(r.m); r.m.material.dispose(); ringPool.splice(i,1); }
  }

  composer.render();

  /* HUD */
  frames++; fpsT+=dt;
  if(fpsT>0.5){ fps=Math.round(frames/fpsT); frames=0; fpsT=0; }
  if(++hudTick%6===0){
    const az=Math.atan2(camera.position.x-controls.target.x, camera.position.z-controls.target.z);
    let bearing=(THREE.MathUtils.radToDeg(az)+180+360)%360;
    $('needle').style.transform=`rotate(${-bearing}deg)`;
    $('hdgNum').textContent=String(Math.round(bearing)).padStart(3,'0')+'°';
    const pts=['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW'];
    $('hdgPts').textContent='FACE '+pts[Math.round(bearing/22.5)%16];
    $('rFps').textContent=fps;
    $('rTri').textContent=(renderer.info.render.triangles/1000).toFixed(0)+'k';
    $('rVox').textContent=VOXCOUNT.toLocaleString();
    $('rSail').textContent = state.wind>0.62?'Close-hauled':state.wind>0.3?'Course set':'Lying by';
    $('rWind').textContent='SW '+Math.round(4+state.wind*26);
  }
}
setTime(state.t);
tick();

/* ==================================================================
   15 · RESIZE
   ================================================================== */
addEventListener('resize', ()=>{
  camera.aspect=innerWidth/innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight);
  composer.setSize(innerWidth,innerHeight);
  bloom.setSize(innerWidth,innerHeight);
  grade.uniforms.uRes.value.set(innerWidth,innerHeight);
});
</script>
</body>
</html>
```

**What's in the water and on the shore**

- **The ship** — a hollow-shelled galleon generated from lofted hull profiles: rounded bilges, gunports with protruding cannons, sheer at bow and stern, lit stern windows, three masts with partly-furled courses, set topsails with real billow, a jib, a shroud/stay rig, four crew, ensign and jack that physically flap.
- **The harbour** — terraced quays of checkered paving, a slipway, brick retaining walls with staircases, a hand-worked crane, fish stalls, barrels, a jetty driven on piles, a rubble mole with a banded lighthouse, and a town of fifteen procedural buildings with lit windows, a clock tower, the church of St Elmo and a working windmill.
- **Living layers** — GPU-quantised voxel sea with foam, sun glint, a rotating sweep-beam, drifting clouds, wheeling gulls, a shuttle rowboat with working oars, chimney smoke, and buoyant props that ride the exact same wave field as the shader.
- **Interactions** — drag to orbit, wheel to zoom, **click the water** to launch a real ripple through the wave shader, hover or click the amber pins (or the log, or keys **1–5**) to fly the camera, scrub the hour from deep watch to golden hour, and dial the wind, which heels the ship, stiffens the sea and drives the mill. Buttons synthesise the surf, the ship's horn and the mole bell entirely in WebAudio. **H** hides the chrome for a clean shot.