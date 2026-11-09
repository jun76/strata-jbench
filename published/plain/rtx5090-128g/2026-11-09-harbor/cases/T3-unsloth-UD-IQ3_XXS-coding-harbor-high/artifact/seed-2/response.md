# Calling at Harbor — a single-file voxel maritime scene

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Calling at Harbor — voxel maritime scene</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bungee&family=Barlow:ital,wght@0,400;0,600;0,800;1,400&family=Barlow+Condensed:wght@600;700&display=swap" rel="stylesheet">
<style>
  :root{
    --ink:#f4ecdf; --dim:#93a8a4; --sea:#0b1a21; --line:rgba(255,255,255,.14);
    --amber:#ffb340; --teal:#5ecfc3; --red:#e8623c;
  }
  *{box-sizing:border-box}
  html,body{margin:0;height:100%;overflow:hidden;background:#04080c;
    font-family:'Barlow',system-ui,sans-serif;color:var(--ink)}
  canvas#c{position:fixed;inset:0;width:100%;height:100%;display:block;touch-action:none}

  .panel{position:fixed;background:rgba(9,20,26,.86);border:1px solid var(--line);
    box-shadow:10px 10px 0 rgba(0,0,0,.42), inset 0 1px 0 rgba(255,255,255,.05);
    backdrop-filter:blur(2px)}

  /* ---- title plaque ---- */
  #plaque{left:22px;top:22px;width:min(370px,calc(100vw - 44px));padding:20px 22px 18px;
    animation:rise .9s .05s cubic-bezier(.16,1,.3,1) both}
  #plaque::before,#plaque::after{content:"";position:absolute;width:13px;height:13px;border:2px solid var(--amber)}
  #plaque::before{left:-6px;top:-6px;border-right:0;border-bottom:0}
  #plaque::after{right:-6px;bottom:-6px;border-left:0;border-top:0}
  .kick{font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:11px;
    letter-spacing:.28em;text-transform:uppercase;color:var(--teal);display:flex;gap:9px;align-items:center}
  .kick i{width:7px;height:7px;background:var(--red);transform:rotate(45deg);display:block;flex:none}
  h1{font-family:'Bungee',cursive;font-weight:400;margin:11px 0 9px;line-height:.94;
    font-size:clamp(28px,3.6vw,44px);letter-spacing:.005em;text-transform:uppercase}
  h1 em{font-style:normal;color:var(--amber);text-shadow:4px 4px 0 rgba(232,98,60,.28)}
  .sub{margin:0;color:#c3cfc9;font-size:14.5px;line-height:1.5;max-width:33ch}
  .rule{height:1px;background:repeating-linear-gradient(90deg,var(--line) 0 6px,transparent 6px 11px);margin:15px 0 12px}
  dl{margin:0;font-size:12.5px;line-height:1.45}
  dl div{display:grid;grid-template-columns:74px 1fr;gap:10px;padding:3.5px 0}
  dt{font-family:'Barlow Condensed',sans-serif;font-weight:700;letter-spacing:.14em;
    text-transform:uppercase;font-size:10.5px;color:var(--dim);padding-top:2px}
  dd{margin:0;color:#dfe6e0}

  /* ---- console ---- */
  #console{left:22px;bottom:22px;width:min(370px,calc(100vw - 44px));padding:15px 18px 16px;
    animation:rise .9s .18s cubic-bezier(.16,1,.3,1) both}
  .crow{display:grid;grid-template-columns:52px 1fr 58px;align-items:center;gap:11px;margin-bottom:11px}
  .crow label{font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:10.5px;
    letter-spacing:.16em;text-transform:uppercase;color:var(--dim)}
  .crow output{font-variant-numeric:tabular-nums;font-size:12.5px;color:var(--amber);text-align:right}
  input[type=range]{-webkit-appearance:none;appearance:none;height:14px;background:transparent;cursor:pointer}
  input[type=range]::-webkit-slider-runnable-track{height:3px;background:linear-gradient(90deg,var(--teal),var(--amber))}
  input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:12px;height:16px;margin-top:-7px;
    background:var(--ink);border:1px solid #000;box-shadow:2px 2px 0 rgba(0,0,0,.5)}
  input[type=range]::-moz-range-track{height:3px;background:linear-gradient(90deg,var(--teal),var(--amber))}
  input[type=range]::-moz-range-thumb{width:12px;height:16px;border-radius:0;background:var(--ink);border:1px solid #000}
  .chips,.views{display:flex;flex-wrap:wrap;gap:6px;margin-top:9px}
  .views{border-top:1px solid var(--line);padding-top:11px}
  .vlabel{width:100%;font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:10.5px;
    letter-spacing:.16em;text-transform:uppercase;color:var(--dim);margin-bottom:2px}
  button{font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:11.5px;letter-spacing:.13em;
    text-transform:uppercase;color:var(--ink);background:#142830;border:1px solid var(--line);
    padding:6px 9px;cursor:pointer;transition:transform .12s,background .18s,color .18s,box-shadow .18s}
  button:hover{background:#1d3b45;transform:translate(-2px,-2px);box-shadow:3px 3px 0 rgba(0,0,0,.5)}
  button:active{transform:translate(0,0);box-shadow:none}
  button.on{background:var(--amber);color:#101d16;border-color:var(--amber)}

  /* ---- readout + compass ---- */
  #readout{right:22px;bottom:22px;padding:12px 15px;font-size:11.5px;min-width:176px;
    font-variant-numeric:tabular-nums;animation:rise .9s .3s cubic-bezier(.16,1,.3,1) both}
  #readout b{color:var(--teal);font-family:'Barlow Condensed',sans-serif;font-weight:700;
    letter-spacing:.14em;text-transform:uppercase;font-size:10.5px}
  #readout div{display:flex;justify-content:space-between;gap:14px;padding:2px 0;color:#d9e2dc}
  #compass{right:22px;top:22px;width:96px;height:96px;display:grid;place-items:center;
    animation:rise .9s .24s cubic-bezier(.16,1,.3,1) both}
  #compass svg{width:78px;height:78px}

  /* ---- hover tag ---- */
  #tip{position:fixed;left:0;top:0;pointer-events:none;opacity:0;transform:translate(-50%,-140%) scale(.9);
    transition:opacity .16s,transform .16s;background:rgba(9,20,26,.93);border:1px solid var(--line);
    padding:8px 11px;max-width:262px;box-shadow:7px 7px 0 rgba(0,0,0,.4)}
  #tip.show{opacity:1;transform:translate(-50%,-125%) scale(1)}
  #tip b{display:block;font-family:'Bungee',cursive;font-weight:400;font-size:12.5px;
    letter-spacing:.04em;color:var(--amber)}
  #tip span{font-size:12px;color:#c8d2cc;line-height:1.35}
  #hint{position:fixed;left:50%;bottom:18px;transform:translateX(-50%);font-size:11px;letter-spacing:.2em;
    text-transform:uppercase;color:rgba(255,255,255,.4);pointer-events:none;font-family:'Barlow Condensed',sans-serif;
    font-weight:700}
  @keyframes rise{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
  @media (max-width:820px){#readout,#compass{display:none}#plaque,#console{width:calc(100vw - 32px);left:16px}
    #console{bottom:16px}#hint{display:none}}
</style>
<script type="importmap">
{"imports":{"three":"https://unpkg.com/three@0.160.0/build/three.module.js",
"three/addons/":"https://unpkg.com/three@0.160.0/examples/jsm/"}}
</script>
</head>
<body>
<canvas id="c"></canvas>

<aside id="plaque" class="panel">
  <div class="kick"><i></i>voxel study №685 · harbor station</div>
  <h1>Calling at<br><em>Harbor</em></h1>
  <p class="sub">A three-masted barque rides at anchor off the breakwater. Fish market folding, lamps lit,
     tide on the turn.</p>
  <div class="rule"></div>
  <dl>
    <div><dt>Subject</dt><dd><b>Meridian</b> — barque, 214 tons</dd></div>
    <div><dt>Method</dt><dd>Every cube merged to a handful of draws</dd></div>
    <div><dt>Input</dt><dd>drag · wheel · click a landmark</dd></div>
  </dl>
</aside>

<section id="console" class="panel">
  <div class="crow"><label for="time">Clock</label><input id="time" type="range" min="0" max="24" step="0.02" value="18.55"><output id="timeOut">18:33</output></div>
  <div class="crow"><label for="wind">Wind</label><input id="wind" type="range" min="0" max="100" step="1" value="42"><output id="windOut">4 bft</output></div>
  <div class="chips">
    <button data-time="6.35">Dawn</button><button data-time="11.4">Noon</button>
    <button data-time="18.55" class="on">Golden</button><button data-time="22.6">Night</button>
    <button id="play">Time-lapse</button>
  </div>
  <div class="views">
    <span class="vlabel">Viewpoints</span>
    <button data-v="0">Broadside</button><button data-v="1">Quay</button>
    <button data-v="2">Lighthouse</button><button data-v="3">Deck</button><button data-v="4">Aerial</button>
  </div>
</section>

<div id="readout" class="panel">
  <div><b>Instrument</b><b>Readout</b></div>
  <div><span>frames</span><span id="fps">—</span></div>
  <div><span>voxels</span><span id="vx">—</span></div>
  <div><span>draws</span><span id="dc">—</span></div>
  <div><span>sea state</span><span id="st">—</span></div>
</div>

<div id="compass" class="panel">
  <svg viewBox="0 0 100 100">
    <circle cx="50" cy="50" r="37" fill="none" stroke="rgba(255,255,255,.16)" stroke-width="1"/>
    <g stroke="rgba(255,255,255,.28)" stroke-width="1">
      <line x1="50" y1="8" x2="50" y2="15"/><line x1="50" y1="85" x2="50" y2="92"/>
      <line x1="8" y1="50" x2="15" y2="50"/><line x1="85" y1="50" x2="92" y2="50"/>
    </g>
    <text x="50" y="24" fill="#93a8a4" font-size="9" font-family="Barlow Condensed" font-weight="700" text-anchor="middle">N</text>
    <g id="needle" transform="rotate(0 50 50)">
      <path d="M50 28 L56 52 L50 46 L44 52 Z" fill="#e8623c"/>
      <path d="M50 72 L44 48 L50 54 L56 48 Z" fill="#dfe6e0"/>
    </g>
    <circle cx="50" cy="50" r="2.6" fill="#ffb340"/>
  </svg>
</div>

<div id="tip"><b></b><span></span></div>
<div id="hint">drag to orbit · scroll to zoom · click landmarks · keys 1–5, space</div>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* ══════════════════════════════════════════════════════════════
   0. helpers — deterministic randomness, colour ramps
══════════════════════════════════════════════════════════════ */
let seed = 2068534;
const rnd = () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296);
const rr  = (a, b) => a + rnd() * (b - a);
const ri  = (a, b) => Math.floor(rr(a, b + 1));
const pick = a => a[Math.floor(rnd() * a.length)];
const lerp = (a, b, t) => a + (b - a) * t;
const clamp = (v, a, b) => v < a ? a : v > b ? b : v;
const smoothstep = (a, b, x) => { const t = clamp((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t); };

/* ── palette ───────────────────────────────────────────────── */
const PAL = {
  oak:'#7b5836', oakLt:'#9d7444', pine:'#4b6b45', pineD:'#37502f', pineT:'#5d7f51',
  stone:'#8f8577', stoneD:'#7a7164', stoneL:'#a49a8a', rock:'#6d6e6a', rockD:'#575853',
  cobble:'#9a9081', slip:'#a89e8c', iron:'#3a3b3e', ironD:'#2a2b2e', rope:'#c2a878',
  dark:'#221d1a', darkRed:'#7a382b', sail:'#efe7d3', sailShade:'#d9cfb8',
  gold:'#c9a24c', cream:'#e7d9b4', glass:'#ffd28a', copper:'#3f7a6a', slate:'#5b6670',
  terra:'#b4653f', terraD:'#93502f'
};

/* ══════════════════════════════════════════════════════════════
   1. voxel builder — every cube is pushed into one merged buffer
      with per-face shading + per-block colour jitter (voxel-art look)
══════════════════════════════════════════════════════════════ */
let VOXELS = 0;
const FACES = [
  { n:[0, 1,0], c:[[0,1,1],[1,1,1],[1,1,0],[0,1,0]], s:1.17 },
  { n:[0,-1,0], c:[[0,0,0],[1,0,0],[1,0,1],[0,0,1]], s:0.55 },
  { n:[1, 0,0], c:[[1,0,1],[1,0,0],[1,1,0],[1,1,1]], s:0.95 },
  { n:[-1,0,0], c:[[0,0,0],[0,0,1],[0,1,1],[0,1,0]], s:0.855 },
  { n:[0, 0,1], c:[[0,0,1],[1,0,1],[1,1,1],[0,1,1]], s:1.02 },
  { n:[0, 0,-1], c:[[1,0,0],[0,0,0],[0,1,0],[1,1,0]], s:0.80 }
];
class VB {
  constructor(){ this.p=[]; this.n=[]; this.c=[]; this.i=[]; this.v=0; this._c=new THREE.Color(); }
  box(x, y, z, sx, sy, sz, col, jit=0.055, sh=1){
    const c = this._c.set(col), r0=c.r*sh, g0=c.g*sh, b0=c.b*sh,
          j = 1 + (rnd()-0.5)*jit*2, x0=x-sx/2, y0=y-sy/2, z0=z-sz/2;
    const P=this.p, N=this.n, C=this.c, I=this.i;
    for (let f=0; f<6; f++){
      const F=FACES[f], start=this.v;
      for (let k=0;k<4;k++){
        const q=F.c[k];
        P.push(x0+q[0]*sx, y0+q[1]*sy, z0+q[2]*sz);
        N.push(F.n[0], F.n[1], F.n[2]);
        const m=F.s*j; C.push(r0*m, g0*m, b0*m);
        this.v++;
      }
      I.push(start,start+1,start+2, start,start+2,start+3);
    }
    VOXELS++;
  }
  geo(){
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(this.p,3));
    g.setAttribute('normal',   new THREE.Float32BufferAttribute(this.n,3));
    g.setAttribute('color',    new THREE.Float32BufferAttribute(this.c,3));
    g.setIndex(this.i);
    return g;
  }
}

/* ══════════════════════════════════════════════════════════════
   2. renderer / scene / camera
══════════════════════════════════════════════════════════════ */
const canvas   = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({ canvas, antialias:true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type    = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.02;

const scene  = new THREE.Scene();
scene.fog    = new THREE.FogExp2(0xbfc9cf, 0.0030);
const camera = new THREE.PerspectiveCamera(46, innerWidth/innerHeight, 0.5, 4000);
camera.position.set(-82, 38, -66);

const controls = new OrbitControls(camera, canvas);
controls.target.set(-4, 10, -8);
controls.enableDamping = true;
controls.dampingFactor = 0.055;
controls.minDistance   = 16;
controls.maxDistance   = 300;
controls.maxPolarAngle = Math.PI * 0.492;
controls.autoRotateSpeed = 0.26;

/* shared materials */
const solidMat = new THREE.MeshLambertMaterial({ vertexColors:true });
const glowMat  = new THREE.MeshBasicMaterial  ({ vertexColors:true, toneMapped:false });
glowMat.color.setRGB(0.35, 0.33, 0.30);

/* ══════════════════════════════════════════════════════════════
   3. sky dome + sun / moon / stars
══════════════════════════════════════════════════════════════ */
const skyU = {
  uTop:{value:new THREE.Color()}, uMid:{value:new THREE.Color()}, uBot:{value:new THREE.Color()},
  uSun:{value:new THREE.Color()}, uSunDir:{value:new THREE.Vector3(0,1,0)}, uGlow:{value:0.6}
};
const sky = new THREE.Mesh(
  new THREE.SphereGeometry(1200, 24, 16),
  new THREE.ShaderMaterial({
    uniforms: skyU, side: THREE.BackSide, depthWrite:false, fog:false,
    vertexShader:`varying vec3 vP; void main(){ vP=position; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
    fragmentShader:`
      varying vec3 vP; uniform vec3 uTop,uMid,uBot,uSun,uSunDir; uniform float uGlow;
      void main(){
        vec3 d = normalize(vP); float h = clamp(d.y,-0.32,1.0);
        vec3 col = mix(uBot,uMid,smoothstep(-0.22,0.09,h));
             col = mix(col,uTop,smoothstep(0.04,0.60,h));
        float s = max(dot(d, normalize(uSunDir)), 0.0);
        col += uSun*pow(s, 260.0)*1.35;
        col += uSun*pow(s, 11.0)*0.34*uGlow;
        col += uSun*pow(s,  2.1)*0.11*uGlow;
        float dith = fract(sin(dot(gl_FragCoord.xy, vec2(12.9898,78.233)))*43758.5453);
        col += (dith-0.5)*0.0035;
        gl_FragColor = vec4(col, 1.0);
      }`
  }));
sky.renderOrder = -2; scene.add(sky);

/* stars */
const starPos = [];
for (let i=0;i<900;i++){
  const v = new THREE.Vector3(rr(-1,1), Math.abs(rr(0.02,1)), rr(-1,1)).normalize().multiplyScalar(1100);
  starPos.push(v.x, v.y, v.z);
}
const starGeo = new THREE.BufferGeometry();
starGeo.setAttribute('position', new THREE.Float32BufferAttribute(starPos,3));
const stars = new THREE.Points(starGeo, new THREE.PointsMaterial({
  color:0xdfe8ff, size:2.2, sizeAttenuation:false, transparent:true, opacity:0, fog:false, depthWrite:false }));
scene.add(stars);

/* voxel sun + moon discs */
function discMesh(col, r, rows){
  const b = new VB();
  for (const [oy, oz, w, h] of rows) b.box(0, oy, oz, 1, h, w, col, 0.02, 1.35);
  const m = new THREE.Mesh(b.geo(), new THREE.MeshBasicMaterial({ vertexColors:true, fog:false,
    transparent:true, toneMapped:false, depthWrite:false }));
  m.scale.setScalar(r); m.renderOrder = 1; return m;
}
const sunMesh  = discMesh(0xffdf9a, 26, [[-4,0,11,1.2],[-3,0,15,1.2],[-2,0,18,1.2],[-1,0,20,1.2],
  [0,0,21,1.2],[1,0,20,1.2],[2,0,18,1.2],[3,0,15,1.2],[4,0,11,1.2]]);
const moonMesh = discMesh(0xdfe6ff, 17, [[-3,0,10,1.2],[-2,0,13,1.2],[-1,0,14,1.2],[0,0,15,1.2],
  [1,0,14,1.2],[2,0,13,1.2],[3,0,10,1.2]]);
scene.add(sunMesh, moonMesh);

/* ══════════════════════════════════════════════════════════════
   4. lights
══════════════════════════════════════════════════════════════ */
const sun = new THREE.DirectionalLight(0xffffff, 3);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.bias = -0.0007;
const sc = sun.shadow.camera;
sc.left=-96; sc.right=96; sc.top=96; sc.bottom=-96; sc.near=1; sc.far=560;
scene.add(sun, sun.target);
sun.target.position.set(-4, 6, -8);

const hemi = new THREE.HemisphereLight(0x9fc4dd, 0x6a5b45, 0.6); scene.add(hemi);
const amb  = new THREE.AmbientLight(0x8fa7b6, 0.45); scene.add(amb);
const fill = new THREE.DirectionalLight(0xffd6a8, 0.35); fill.position.set(60, 40, -80); scene.add(fill);

const lampLights = [];
for (const [x, y, z, col, dist] of [
  [-32, 11.6, 2.5, 0xffb45e, 46], [-10, 11.6, 2.5, 0xffb45e, 46],
  [12, 11.6, 2.5, 0xffb45e, 46],  [30, 11.6, -12, 0xffb45e, 46],
  [-22, 16.6, 12.5, 0xffa94e, 40], [34, 40.5, -26, 0xffe0a0, 120]
]) {
  const pl = new THREE.PointLight(col, 0, dist, 0);
  pl.position.set(x, y, z); scene.add(pl); lampLights.push(pl);
}
const beamLight = new THREE.SpotLight(0xffe2a8, 0, 340, 0.19, 0.65, 0);
beamLight.castShadow = false;

/* ══════════════════════════════════════════════════════════════
   5. land — terraced harbour town cut into cliffs
══════════════════════════════════════════════════════════════ */
const W = new VB(), GW = new VB();          // W = solid world, GW = emissive windows

const TER = [
  { x0:-46, x1:46, z0:-1.5, z1: 9, top: 4.6, c:PAL.stone,  skin:[PAL.slip,PAL.cobble,PAL.stoneL,PAL.stoneD] },
  { x0:-46, x1:50, z0:  9,  z1:18, top: 8.4, c:PAL.stoneD, skin:[PAL.cobble,PAL.stone,PAL.stoneL] },
  { x0:-46, x1:56, z0: 18,  z1:29, top:12.6, c:PAL.stone,  skin:[PAL.stoneL,PAL.stone,PAL.cobble] },
  { x0:-44, x1:62, z0: 29,  z1:40, top:17.4, c:PAL.stoneD, skin:[PAL.stone,PAL.stoneL,PAL.rock] },
  { x0:-40, x1:68, z0: 40,  z1:58, top:23.6, c:PAL.rockD,  skin:[PAL.rock,PAL.stoneD,PAL.stone] }
];
const land = [];
for (const t of TER){
  land.push([t.x0-2.6, t.x1+2.6, t.z0-2.6, t.z1+2.6]);
  W.box((t.x0+t.x1)/2, (t.top-8)/2, (t.z0+t.z1)/2, t.x1-t.x0, t.top+8, t.z1-t.z0, t.c, 0.05);
  /* paved skin */
  for (let x=t.x0; x<t.x1-1; x+=4) for (let z=t.z0; z<t.z1-1; z+=4)
    if (rnd()<0.78) W.box(x+2, t.top+0.16, z+2, 4.1, 0.55, 4.1, pick(t.skin), 0.085);
  /* masonry courses on the exposed riser */
  for (let x=t.x0; x<t.x1-1; x+=3){
    for (let y=t.top-1.1; y>-3.5; y-=2.3){
      if (rnd()<0.34) continue;
      W.box(x+1.5, y+0.55, t.z0-0.16, 2.75, 1.05, 0.42,
            pick([PAL.stoneL,PAL.stone,PAL.stoneD,PAL.rock]), 0.1);
    }
  }
  /* wet / barnacle band at the waterline */
  for (let x=t.x0; x<t.x1-1; x+=2.4)
    if (rnd()<0.6) W.box(x+1.2, rr(-2.4,-1.0), t.z0-0.22, 2.5, 1.1, 0.5, pick(['#3d4a3c','#4b5140','#2f3a33']), 0.14);
}
const isLand = (x, z) => {
  if (x < -42 && z > -14 && Math.hypot((x+62)/22, (z-8)/17) < 1.15) return true;   // headland
  for (const [a,b,c,d] of land) if (x>=a && x<=b && z>=c && z<=d) return true;
  return false;
};

/* ── rocky headland + windmill (left, closes the frame) ───── */
(function headland(){
  for (let i=0;i<80;i++){
    const a=rr(0,Math.PI*2), r=Math.pow(rnd(),0.55)*21;
    const x=-62+Math.cos(a)*r, z=8+Math.sin(a)*r*0.78;
    const hgt = Math.max(1.4, 13.5 - Math.hypot((x+62)/22,(z-8)/17)*13 + rr(-1.2,1.6));
    W.box(x, hgt/2 - 5, z, rr(3,6), hgt+5, rr(3,6), pick([PAL.rock,PAL.rockD,'#787a72','#5e6059']), 0.11);
  }
  /* windmill */
  const mx=-62, mz=8, base=8.6;
  for (let i=0;i<7;i++) W.box(mx, base+i*1.55, mz, 6-i*0.55, 1.6, 6-i*0.55, i%2?PAL.cream:PAL.terraD, 0.05);
  W.box(mx, base+11.3, mz, 5.4, 1.1, 5.4, PAL.ironD, 0.05);
  GW.box(mx, base+6.5, mz-2.7, 1.3, 1.5, 0.25, PAL.glass);
  /* pines */
  const pine=(x,z,h)=>{
    W.box(x, h*0.32, z, 1.1, h*0.66, 1.1, '#5a432c', 0.08);
    for (let i=0;i<4;i++) W.box(x, h*0.5+i*(h*0.17), z, 4.6-i*1.05, h*0.2, 4.6-i*1.05, pick([PAL.pine,PAL.pineD,PAL.pineT]), 0.1);
  };
  for (let i=0;i<12;i++){
    const a=rr(0,6.28), r=rr(10,21), x=-62+Math.cos(a)*r, z=8+Math.sin(a)*r*0.8;
    if (Math.hypot((x+62)/22,(z-8)/17) > 0.94) continue;
    const g = 13 - Math.hypot((x+62)/22,(z-8)/17)*13;
    if (g > 3) pine(x, z, rr(5,8)+g*0.2);
  }
})();

/* ══════════════════════════════════════════════════════════════
   6. town buildings
══════════════════════════════════════════════════════════════ */
const WALLS = ['#e6d3ad','#dbb98a','#c98f68','#a8b39c','#8fa6ac','#d9c3c0','#b9a27e','#c8a24a'];
const ROOFS = [PAL.terra, PAL.terraD, '#9a4b34', '#7d5a4a', PAL.slate];

function house(x, z, g, w, d, h, opt={}){
  const wall = opt.wall || pick(WALLS), roof = opt.roof || pick(ROOFS);
  W.box(x, g+h/2, z, w, h, d, wall, 0.05);
  W.box(x, g+0.35, z, w+0.5, 0.7, d+0.5, PAL.stoneL, 0.07);           // plinth
  /* gabled roof with eaves + ridge beam */
  const steps = Math.max(2, Math.round(d/2.4));
  W.box(x, g+h+0.45, z, w+1.2, 0.9, d+1.0, roof, 0.07);
  for (let i=1;i<=steps;i++)
    W.box(x, g+h+0.45+i*1.05, z, w+1.2-i*0.15, 1.05, Math.max(0.6, d+1.0 - i*(d+1.0)/steps), roof, 0.08);
  /* windows on the sea face + sides */
  const cols = Math.max(1, Math.floor(w/3.2)), rows = Math.max(1, Math.floor((h-1.6)/3.0));
  for (let c=0;c<cols;c++) for (let r=0;r<rows;r++){
    if (rnd()<0.18) continue;
    const wx = x - w/2 + (c+0.5)*(w/cols), wy = g + 2.4 + r*3.0;
    W.box(wx, wy, z-d/2-0.12, 2.1, 2.4, 0.24, PAL.ironD, 0.05);
    GW.box(wx, wy, z-d/2-0.26, 1.5, 1.7, 0.2, PAL.glass);
    W.box(wx, wy-1.42, z-d/2-0.2, 2.3, 0.3, 0.3, PAL.stoneL, 0.06);
  }
  /* door + a hint of interior light */
  W.box(x - w/2 + 1.9, g+1.7, z-d/2-0.14, 1.7, 2.9, 0.3, '#5a3c28', 0.06);
  GW.box(x - w/2 + 1.9, g+1.55, z-d/2-0.28, 0.7, 1.0, 0.16, '#ffbe6a');
  /* chimney */
  W.box(x + (rnd()<0.5?-1:1)*(w/2-1.5), g+h+steps*1.05+1.2, z + (rnd()-0.5)*d*0.4, 1.5, 2.8, 1.5,
        pick([PAL.stoneD, PAL.terraD]), 0.08);
  /* flower boxes for the harbour charm */
  if (rnd()<0.55) for (let c=0;c<cols;c++) if (rnd()<0.6)
    W.box(x - w/2 + (c+0.5)*(w/cols), g+1.15, z-d/2-0.35, 1.9, 0.6, 0.7, '#5d3f2c', 0.08),
    W.box(x - w/2 + (c+0.5)*(w/cols), g+1.6, z-d/2-0.35, 1.6, 0.5, 0.5, pick(['#d6572f','#e0902f','#c74f6e']), 0.12);
  return { x, z, g, h: g+h+steps*1.05+2 };
}

/* harbour church with clock tower on the crown terrace */
(function church(){
  const x=6, z=47, g=23.6;
  W.box(x, g+4.5, z, 15, 9, 20, PAL.cream, 0.05);
  for (let i=0;i<8;i++) W.box(x, g+9+i*1.1, z, 15.6-i*0.2, 1.1, 20.6-i*1.4, PAL.terraD, 0.08);
  W.box(x-2.5, g+6.5, z-10.1, 2.4, 4.4, 0.4, PAL.terraD, 0.05);
  GW.box(x-2.5, g+6.5, z-10.28, 1.6, 3.4, 0.2, '#ffd07a');
  /* tower */
  W.box(x+9, g+9, z+4, 8, 18, 8, PAL.cream, 0.05);
  W.box(x+9, g+19.5, z+4, 9.2, 1.6, 9.2, PAL.stone, 0.06);
  for (let i=0;i<4;i++) W.box(x+9+Math.cos(i*1.5708)*4.4, g+21.2, z+4+Math.sin(i*1.5708)*4.4, 1.2, 2.2, 1.2, PAL.stoneD, 0.06);
  GW.box(x+9, g+16.5, z+4-4.1, 2.4, 3.2, 0.3, '#ffe3a8');
  GW.box(x+9-4.1, g+16.5, z+4, 0.3, 3.2, 2.4, '#ffe3a8');
  GW.box(x+9, g+12.6, z+4-4.1, 2.2, 2.2, 0.3, '#e8efee');   // clock face
  W.box(x+9, g+12.6, z+4-4.2, 0.28, 1.6, 0.24, PAL.iron, 0.02);
  W.box(x+9, g+12.6, z+4-4.2, 1.3, 0.28, 0.24, PAL.iron, 0.02);
  for (let i=0;i<4;i++) W.box(x+9, g+22.6+i*1, z+4, 9-i*2.4, 1, 9-i*2.4, PAL.slate, 0.07);
  W.box(x+9, g+27.2, z+4, 0.5, 3.2, 0.5, PAL.gold);
  W.box(x+9, g+28.2, z+4, 2.4, 0.35, 1.5, PAL.gold, 0.02);
})();

/* warehouses + terraced house rows */
const smokeSrc = [];
(function town(){
  const row = (g, z, from, to, step) => { for (let x=from; x<to; x+=step) house(x+rr(-0.7,0.7), z+rr(-0.8,0.8), g, ri(8,12), ri(9,11), ri(7,10)); };
  /* big warehouse on the quay level */
  const wx=-11, wz=14.5, g=4.6;
  W.box(wx, g+5, wz, 20, 10, 13, '#c1704a', 0.045);
  for (let i=0;i<6;i++) W.box(wx, g+10.4+i*0.9, wz, 20.8, 0.95, 13.8-i*1.4, '#8d4f33', 0.07);
  W.box(wx, g+1.6, wz-6.6, 6.2, 3.2, 0.4, PAL.ironD, 0.05);          // great door
  W.box(wx, g+3.0, wz-6.9, 6.6, 0.5, 0.8, PAL.oakLt, 0.06);
  GW.box(wx, g+7.6, wz-6.6, 2.6, 2.2, 0.3, '#ffcf86');
  W.box(wx-4, g+12.6, wz, 2.2, 4.4, 2.2, PAL.stoneD, 0.06);
  smokeSrc.push([wx-4, g+15.2, wz]);
  for (let i=0;i<4;i++) W.box(wx+7-i*4.6, g+6.4, wz-6.5, 2.4, 2.6, 0.35, PAL.ironD, 0.05),
                          GW.box(wx+7-i*4.6, g+6.4, wz-6.62, 1.7, 1.9, 0.2, '#ffc97e');

  row(8.4, 13.5, -42, 44, 12.4);
  row(12.6, 23.5, -40, 50, 13.5);
  row(17.4, 34.5, -34, 54, 13.0);
  /* hillside cottages */
  for (let i=0;i<9;i++) house(rr(-34, 56), rr(43, 55), 23.6, ri(7,10), ri(7,9), ri(5,7));
})();

/* ══════════════════════════════════════════════════════════════
   7. quay furniture — lamps, bollards, crates, market, crane
══════════════════════════════════════════════════════════════ */
function lamp(x, y, z, h=5.4){
  W.box(x, y+h/2, z, 0.6, h, 0.6, PAL.iron, 0.05);
  W.box(x, y+h+0.2, z, 1.7, 1.5, 1.7, PAL.ironD, 0.05);
  GW.box(x, y+h+0.2, z, 1.15, 1.1, 1.15, '#ffcf8c');
  W.box(x, y+h+1.25, z, 1.9, 0.4, 1.9, PAL.iron, 0.04);
  W.box(x, y+0.4, z, 1.4, 0.8, 1.4, PAL.ironD, 0.05);
}
function crate(x, y, z, s=2.2, c=PAL.oak){
  W.box(x, y+s/2, z, s, s, s, c, 0.1);
  W.box(x, y+s/2, z, s+0.12, s*0.22, s+0.12, PAL.oakLt, 0.06);
  W.box(x, y+s/2, z, s*0.22, s+0.12, s+0.12, PAL.oakLt, 0.06);
}
function barrel(x, y, z){
  W.box(x, y+0.9, z, 2.2, 1.8, 2.2, PAL.oak, 0.08);
  W.box(x, y+0.45, z, 2.4, 0.35, 2.4, '#57402a', 0.05);
  W.box(x, y+1.35, z, 2.4, 0.35, 2.4, '#57402a', 0.05);
  W.box(x, y+1.85, z, 1.7, 0.2, 1.7, PAL.oakLt, 0.06);
}
function bollard(x, y, z){
  W.box(x, y+0.9, z, 1.3, 1.8, 1.3, PAL.ironD, 0.05);
  W.box(x, y+1.95, z, 1.9, 0.5, 1.9, PAL.iron, 0.04);
}
function coil(x, y, z){ for (let i=0;i<3;i++) W.box(x, y+0.2+i*0.32, z, 2.8-i*0.4, 0.3, 2.8-i*0.4, PAL.rope, 0.1); }
function stall(x, z, g){
  W.box(x, g+2.6, z-1.6, 6.4, 0.5, 3.6, PAL.oakLt, 0.07);
  for (const s of [-1,1]) W.box(x+s*3, g+1.3, z-1.6, 0.4, 2.6, 0.4, PAL.oak, 0.05);
  for (let i=0;i<5;i++) W.box(x-3+i*1.5, g+3.6, z-1.6, 1.5, 0.4, 3.8, i%2?'#d6572f':PAL.cream, 0.08);
  W.box(x, g+4.0, z-1.6, 6.8, 0.3, 0.4, PAL.oak, 0.05);
  for (let i=0;i<6;i++) W.box(x-2.4+i*0.95, g+3.1, z-1.1, 0.75, 0.6, 0.75, pick(['#d6572f','#e0902f','#6d8f3a','#c74f6e','#e8b93a']), 0.14);
}
function netRack(x, z, g){
  for (const s of [-1,1]) W.box(x+s*3.5, g+2.4, z, 0.45, 4.8, 0.45, PAL.oak, 0.05);
  W.box(x, g+4.6, z, 7.4, 0.35, 0.35, PAL.oakLt, 0.05);
  for (let i=0;i<8;i++) W.box(x-3.2+i*0.9, g+3.2, z, 0.22, 2.4, 0.22, '#b9ad8d', 0.14);
  for (let i=0;i<4;i++) W.box(x, g+2.2+i*0.8, z, 7, 0.16, 0.16, '#c2b795', 0.14);
}
function pineSmall(x, z, g, h=6){
  W.box(x, g+h*0.32, z, 1, h*0.65, 1, '#54402b', 0.08);
  for (let i=0;i<4;i++) W.box(x, g+h*0.5+i*h*0.16, z, 4.2-i*0.95, h*0.2, 4.2-i*0.95, pick([PAL.pine,PAL.pineD,PAL.pineT]), 0.11);
}
function person(x, z, g, c1, c2){
  const grp = new THREE.Group();
  const parts = [];
  const mk = (w,h,d,col,oy,oz=0)=>{ const b=new VB(); b.box(0,oy,oz,w,h,d,col,0.05);
    const m=new THREE.Mesh(b.geo(), solidMat); m.castShadow=true; grp.add(m); return m; };
  mk(0.95,1.15,0.68,c1,0.6); mk(1.35,1.3,0.85,c2,1.85); mk(0.95,0.85,0.7,'#3c2a20',0.25,0);
  mk(1.05,0.95,0.8,'#d9b08c',3.0);
  parts.push(grp.children[0]);
  grp.position.set(x, g+0.05, z);
  grp.userData = { legs:parts[0], phase:rnd()*6.28, dir:rnd()<0.5?-1:1 };
  return grp;
}

/* quay apron furniture (top y = 4.6) */
const G0 = 4.6;
for (const x of [-38,-30,-22,-14,12,20,28]) lamp(x, G0, 2.5);
for (const x of [-36,-29,-20,-8,4,14,24,33]) bollard(x, G0, -0.4);
for (let i=0;i<7;i++) coil(rr(-36,30), G0, rr(0.8,3.2));
for (let i=0;i<30;i++) crate(rr(-40,34), G0, rr(1.4,7.2), rr(1.7,2.8), pick([PAL.oak,PAL.oakLt,'#6b4d31']));
for (let i=0;i<14;i++) barrel(rr(-40,34), G0, rr(1.4,7.0));
/* crate pyramids */
for (const px of [-26, 8, 26]){
  for (let a=0;a<3;a++) for (let b=0;b<=a;b++) crate(px+a*2.4, G0+(2-a)*2.4, 5.0-b*2.4, 2.3, PAL.oak);
}
for (const [x,z] of [[-16,-0.2],[-2,-0.2],[18,-0.2]]) stall(x, z+4.6, G0);
for (let i=0;i<3;i++) netRack(rr(20,34), rr(2,6), G0);
for (let i=0;i<5;i++) pineSmall(rr(-44,-34), rr(10.5,16.5), 8.4, rr(5,7));

/* harbour crane on the quay, with a swinging crate */
const craneHook = new THREE.Group();
(function crane(){
  const cx=24, cz=4.0;
  for (const s of [-1,1]){
    const b=new VB();
    for (let i=0;i<7;i++) b.box(0, 1.7+i*1.5, 0, 0.8, 1.6, 0.8, PAL.oak, 0.07);
    for (let i=0;i<5;i++) b.box(0, 2.0+i*2.0, 0, 0.55, 0.55, 1.9, PAL.oakLt, 0.07);   // ladder rungs
    const leg=new THREE.Mesh(b.geo(), solidMat); leg.castShadow=true;
    leg.position.set(cx+s*1.6, G0, cz+1.4); leg.rotation.x=0; scene.add(leg);
  }
  W.box(cx, G0+11.6, cz, 4.2, 1.2, 3.6, PAL.oak, 0.06);
  const jib=new THREE.Mesh(new THREE.BoxGeometry(15,1,1.2), solidMat);
  jib.position.set(cx-4.5, G0+12.2, cz); jib.rotation.z=0.16; jib.castShadow=true; scene.add(jib);
  W.box(cx+1, G0+12.9, cz, 3.2, 1.6, 2.6, PAL.oakLt, 0.06);
  GW.box(cx+1, G0+12.9, cz-1.35, 1.2, 1.0, 0.3, '#ffcd84');
  const rope=new THREE.Mesh(new THREE.BoxGeometry(0.16,4.4,0.16), new THREE.MeshLambertMaterial({color:0xbfae8c}));
  rope.position.set(cx-10.5, G0+7.9, cz); craneHook.add(rope);
  const hookCrate=new VB(); hookCrate.box(0,0,0,2.6,2.6,2.6,PAL.oak,0.1);
  const hc=new THREE.Mesh(hookCrate.geo(), solidMat); hc.castShadow=true; hc.position.y=5.6; craneHook.add(hc);
  craneHook.position.set(cx-10.5, G0+11.6, cz); scene.add(craneHook);
})();

/* ── breakwater + lighthouse ─────────────────────────────────── */
(function mole(){
  const bx=30;
  for (let z=-1; z>-31; z-=2.2){
    const t = smoothstep(-1,-30,z);
    const top = 6.8 - t*0.4, hw = 5.2 + t*1.8;
    W.box(bx, (top-8)/2, z-1.1, hw*2, top+8, 2.4, PAL.stone, 0.05);
    for (const s of [-1,1]) for (let k=0;k<3;k++){
      const y = top - 1.4 - k*1.9 - rr(0,0.6);
      W.box(bx + s*(hw+rr(0.3,1.5)), y-0.5, z-1.1+rr(-1,1), rr(1.6,3), rr(1.4,2.6), rr(1.6,3),
            pick([PAL.rock,PAL.stoneD,PAL.rockD]), 0.14);
    }
  }
  for (let i=0;i<9;i++) W.box(bx-3.2+i*0.8, 5.9-i*0.7, -8+rr(-0.4,0.4), 0.9, 0.5, 4.6, PAL.stoneL, 0.08); // slip steps
  /* lamp on the mole */
  W.box(bx, 6.8, -6, 0.7, 4.6, 0.7, PAL.iron, 0.05);
  GW.box(bx, 11.6, -6, 1.2, 1.2, 1.2, '#ffcf8c');
  W.box(bx, 12.4, -6, 1.6, 0.4, 1.6, PAL.ironD, 0.04);
  /* lighthouse */
  const lz=-26, g=6.4;
  W.box(bx, g+2.2, lz, 15, 4.4, 15, PAL.stoneD, 0.05);
  GW.box(bx-3.4, g+2.6, lz-7.6, 1.8, 1.7, 0.3, '#ffcd84');
  W.box(bx+4, g+1.7, lz-7.6, 2.2, 3.2, 0.4, PAL.ironD, 0.05);
  const bands=[PAL.cream,PAL.cream,PAL.terra,PAL.cream,PAL.cream,PAL.terra,PAL.cream];
  let y=g+4.4, rad=4.6;
  for (let i=0;i<bands.length;i++){
    for (let k=0;k<3;k++){
      W.box(bx, y+1.35, lz, rad*2, 2.7, rad*2, bands[i], 0.045);
      y+=2.7; if (i>0) rad-=0.24;
    }
    if (rnd()<1) W.box(bx, y-1.5, lz-rad-0.1, 1.7, 2.4, 0.5, PAL.ironD, 0.05),
                  GW.box(bx, y-1.5, lz-rad-0.28, 1.1, 1.6, 0.25, '#ffdc96');
  }
  W.box(bx, y+0.6, lz, 10.4, 1.2, 10.4, PAL.ironD, 0.05);
  for (let a=0;a<8;a++) W.box(bx+Math.cos(a/8*6.283)*4.6, y+2.1, lz+Math.sin(a/8*6.283)*4.6, 0.4, 1.8, 0.4, PAL.iron, 0.05);
  W.box(bx, y+2.1, lz, 10, 0.3, 10, PAL.iron, 0.04);
  GW.box(bx, y+4.6, lz, 6.4, 4.4, 6.4, '#ffe4a6');
  for (const s of [-1,1]){ W.box(bx+s*3.3, y+4.6, lz, 0.4, 4.6, 6.8, PAL.ironD, 0.05);
                           W.box(bx, y+4.6, lz+s*3.3, 6.8, 4.6, 0.4, PAL.ironD, 0.05); }
  for (let i=0;i<4;i++) W.box(bx, y+7.4+i*1, lz, 7.4-i*1.6, 1, 7.4-i*1.6, PAL.terraD, 0.06);
  W.box(bx, y+11.6, lz, 0.5, 2.4, 0.5, PAL.gold, 0.03);
  lampLights[5].position.set(bx, y+4.6, lz);
  /* rotating beam */
  const beam = new THREE.Group(); beam.position.set(bx, y+4.6, lz);
  const beamMat = new THREE.MeshBasicMaterial({ color:0xffe1a4, transparent:true, opacity:0.11,
    blending:THREE.AdditiveBlending, depthWrite:false, side:THREE.DoubleSide, toneMapped:false });
  for (const s of [1,-1]){
    const g2 = new THREE.CylinderGeometry(2.2, 10.5, 118, 5, 1, true); g2.rotateZ(-Math.PI/2);
    const m = new THREE.Mesh(g2, beamMat);
    m.position.x = s*59; if (s<0) m.rotation.y = Math.PI; m.renderOrder = 4; beam.add(m);
  }
  beam.add(beamLight); beamLight.target.position.set(120, -6, 0); beam.add(beamLight.target);
  scene.add(beam); scene.userData.beam = beam;
})();

/* ══════════════════════════════════════════════════════════════
   8. the ship — a barque at anchor
══════════════════════════════════════════════════════════════ */
const ship = new THREE.Group();
const rig = [];   // rope line endpoints
(function buildShip(){
  const B=new VB(), G=new VB();
  const DARK='#2b2421', RED=PAL.darkRed, TAN='#a5793f', WOOD=PAL.oak, WOODL=PAL.oakLt;
  const hb = z => z < -12 ? 4.3 + (z+18)*0.267
                 : z <  4 ? 5.9
                 : 5.9*(1-Math.pow((z-4)/13,2)) + 0.45*((z-4)/13);
  const keel = z => -3.5 + Math.max(0,(z-6))*0.22 + Math.max(0,(-z-12))*0.30;
  const deck = z =>  4.0 + Math.max(0,(z-8))*0.18 + Math.max(0,(-z-11))*0.26;

  for (let zi=-18; zi<18; zi++){
    const z=zi+0.5, w=hb(z), k=keel(z), d=deck(z);
    B.box(0, k+1.2, z, Math.max(0.3,w*1.32), 2.5, 1.08, RED, 0.06);
    if (k+2.5 < d-1.0) B.box(0, (k+2.4+d-1.2)/2, z, Math.max(0.3,w*1.76), d-1.2-(k+2.4)+0.2, 1.08, DARK, 0.05);
    B.box(0, d-0.7, z, w*2, 1.5, 1.08, DARK, 0.05);
    B.box(0, d-0.55, z, w*2+0.18, 0.55, 1.06, PAL.cream, 0.05);         // wale
    B.box(0, d+0.12, z, Math.max(0.4,w*2-1), 0.36, 1.08, TAN, 0.09);    // deck
    if (w > 1.4){
      for (const s of [-1,1]){
        B.box(s*(w-0.28), d+0.95, z, 0.62, 1.7, 1.08, WOOD, 0.07);
        B.box(s*(w-0.28), d+1.85, z, 0.34, 0.3, 1.08, WOODL, 0.06);     // rail cap
      }
    }
  }
  /* gunports + cannon muzzles */
  let gun=0;
  for (let z=-13; z<10; z+=3.3){
    if (hb(z) < 4.6) continue;
    const d=deck(z);
    for (const s of [-1,1]){
      B.box(s*(hb(z)+0.06), d-2.5, z, 0.5, 1.9, 1.9, PAL.cream, 0.05);
      B.box(s*(hb(z)+0.26), d-2.5, z, 0.5, 1.05, 1.05, '#141210', 0.02);
      if (gun++ % 3 === 0) B.box(s*(hb(z)+1.1), d-2.5, z, 1.5, 0.55, 0.55, PAL.iron, 0.05);
    }
  }
  /* transom + stern cabin */
  const dz=deck(-17);
  B.box(0, (keel(-17.4)+dz+0.6)/2, -18.1, 8.4, dz+0.6-keel(-17.4), 0.7, DARK, 0.05);
  B.box(0, dz+2.1, -12.4, 10.4, 3.6, 9.4, PAL.gold, 0.05);
  B.box(0, dz+3.95, -12.4, 11.2, 0.6, 10.2, '#3b2f22', 0.05);
  for (let i=0;i<3;i++){ B.box(-3.2+i*3.2, dz+2.2, -17.35, 1.9, 2.3, 0.3, '#3b2f22', 0.04);
                          G.box(-3.2+i*3.2, dz+2.2, -17.5, 1.4, 1.7, 0.2, '#ffd48a'); }
  for (const s of [-1,1]) for (let i=0;i<2;i++){
    B.box(s*5.3, dz+2.2, -10.4-i*3.2, 0.3, 2.1, 1.7, '#3b2f22', 0.04);
    G.box(s*5.42, dz+2.2, -10.4-i*3.2, 0.2, 1.5, 1.2, '#ffd48a');
  }
  G.box(0, dz+5.1, -16.4, 1.3, 1.1, 1.3, '#ffe0a0');
  B.box(0, dz+5.9, -16.4, 1.9, 0.4, 1.9, PAL.ironD, 0.04);
  /* forecastle */
  B.box(0, deck(13)+1.15, 12.6, 8.6, 2.2, 6.2, WOOD, 0.06);
  B.box(0, deck(13)+2.35, 12.6, 9.2, 0.5, 6.8, WOODL, 0.06);
  B.box(0, deck(13)+3.6, 12.6, 3.4, 2.1, 3.0, PAL.cream, 0.05);
  G.box(0, deck(13)+3.7, 11.05, 1.2, 1.2, 0.25, '#ffd48a');
  /* figurehead */
  B.box(0, deck(17)+0.4, 17.9, 1.1, 2.2, 1.6, PAL.cream, 0.05);
  B.box(0, deck(17)+1.9, 17.7, 1.3, 1.2, 1.2, PAL.cream, 0.05);
  /* bowsprit */
  for (let i=0;i<9;i++){
    const t=i/8, z=15+t*15.5, y=4.4+t*4.8;
    B.box(0, y, z, 1.1-t*0.35, 1.1-t*0.35, 2.4, WOOD, 0.06);
  }
  /* masts, tops, yards, sails */
  const mast=(mz, wLow, wTop, topY, platY)=>{
    B.box(0, (deck(mz)+platY)/2, mz, wLow, platY-deck(mz), wLow, WOOD, 0.06);
    B.box(0, (platY+topY)/2, mz, wTop, topY-platY+0.5, wTop, WOODL, 0.06);
    B.box(0, platY, mz, 5.2, 0.6, 3.6, WOOD, 0.06);
    for (const s of [-1,1]) B.box(s*2.4, platY+1.1, mz, 0.35, 1.6, 3.4, WOODL, 0.06);
    B.box(0, platY+2, mz, 0.5, 0.4, 3.6, WOODL, 0.05);
  };
  mast(7.5, 2.3, 1.5, 30.5, 21.2);
  mast(-3, 2.7, 1.7, 34.5, 23.4);
  mast(-13, 2.1, 1.3, 25.5, 17.2);

  const furl=(yz, len, z)=>{
    B.box(0, yz, z, len, 0.8, 0.8, WOOD, 0.06);
    for (const s of [-1,1]) B.box(s*(len/2-0.5), yz+0.55, z, 1.4, 0.5, 0.7, WOODL, 0.06);
    B.box(0, yz-1.15, z, len*0.92, 1.5, 2.2, PAL.sail, 0.09);
    for (let i=0;i<4;i++) B.box((i-1.5)*len*0.22, yz-0.5, z+0.6, 0.3, 0.3, 2.4, PAL.rope, 0.1);
  };
  const sail=(yz, len, h, z, wind)=>{
    B.box(0, yz, z, len, 0.8, 0.8, WOOD, 0.06);
    for (const s of [-1,1]) B.box(s*(len/2-0.5), yz+0.55, z, 1.4, 0.5, 0.7, WOODL, 0.06);
    const y0=yz-1.0-h;
    for (let i=0;i<3;i++){                                              // 3 panels → billow
      const off=(i===0?-0.35:i===1?0.5+wind*0.9:1.2+wind*0.2);
      B.box((i-1)*(len/3), y0+h/2, z+off, len/3*1.02, h, 0.5, PAL.sail, 0.075);
    }
    for (let s=1;s<3;s++) B.box(0, y0+h*s/3, z+0.45, len*0.99, 0.35, 0.55, PAL.sailShade, 0.05);
    for (let i=0;i<3;i++) B.box((i-1)*(len/3), y0-0.25, z+0.4, len/3, 0.55, 0.7, PAL.sailShade, 0.07);
  };
  const W0 = 0.45;
  sail(21.5, 14.5, 5.6, 7.5, W0);  sail(27.6, 10.6, 4.4, 7.5, W0);  furl(13.6, 16.4, 7.5);
  sail(22.6, 15.8, 5.9, -3, W0);   sail(29.2, 11.6, 4.5, -3, W0);   furl(13.0, 18.2, -3);
  sail(33.6, 6.6, 2.6, -3, W0);
  /* spanker + spanker topsail */
  B.box(0, 13.6, -9.6, 0.55, 0.7, 8.2, WOOD, 0.06);
  B.box(0, 6.9, -9.2, 0.75, 0.8, 8.6, WOOD, 0.06);
  B.box(0.45, 10.3, -9.6, 0.55, 6.0, 8.0, PAL.sail, 0.08);
  B.box(-0.45, 10.3, -9.6, 0.55, 6.0, 8.0, PAL.sailShade, 0.08);
  for (let i=0;i<4;i++) B.box(0, 15.0+i*1.3, -10.4+i*1.0, 0.5, 1.35, 6.4-i*1.4, PAL.sail, 0.08);
  /* headsails (stepped triangles — pure voxel) */
  const headsail=(ay,az,by,bz,cy,cz,rows)=>{
    for (let i=0;i<rows;i++){
      const t=i/(rows-1);
      const p1y=lerp(ay,by,t), p1z=lerp(az,bz,t), p2y=lerp(ay,cy,t), p2z=lerp(az,cz,t);
      B.box(0, (p1y+p2y)/2, (p1z+p2z)/2, 0.5, Math.abs(p1y-p2y)+0.9, Math.abs(p1z-p2z)+0.9, PAL.sail, 0.08);
    }
  };
  headsail(9.4, 30, 21.5, 8.5, 5.4, 13.5, 9);
  headsail(9.4, 30, 16.0, 9.5, 5.2, 18.0, 7);
  /* deck clutter */
  for (let i=0;i<5;i++) B.box(rr(-4,4), deck(rr(-6,8))+1.1, rr(-6,8), rr(2,3), 1.6, rr(2,3), PAL.oak, 0.1);
  for (let i=0;i<4;i++) B.box(rr(-4.4,4.4), deck(rr(-9,-4))+1.0, rr(-9,-4.5), 1.9, 1.8, 1.9, PAL.oakLt, 0.1);
  B.box(0, 5.4, -6.5, 2.4, 0.4, 2.4, WOODL, 0.06);            // capstan
  B.box(0, 6.0, -6.5, 3.2, 0.35, 0.35, WOOD, 0.06);
  for (const s of [-1,1]) B.box(s*1.9, deck(0)+0.9, 3.4, 0.4, 1.4, 0.4, WOODL, 0.06);
  /* rigging */
  const push=(a,b)=>rig.push(a[0],a[1],a[2],b[0],b[1],b[2]);
  const bowTip=[0,9.2,30], mainTop=[0,34.5,-3], foreTop=[0,30.5,7.5], mizTop=[0,25.5,-13];
  push(bowTip, mainTop); push(mainTop, foreTop); push(mizTop, [0,10.5,-16]);
  push(bowTip, foreTop); push([0,16,22],[0,21.5,8.5]);
  for (const m of [[7.5,30.5],[ -3,34.5],[-13,25.5]]){
    for (const s of [-1,1]) for (let k=-1;k<=1;k++){
      push([s*5.4, deck(m[0])+1.5, m[0]+k*2.6], [s*1.1, m[1]-2.5, m[0]+k*0.5]);
      push([s*4.0, deck(m[0])+2.4, m[0]+k*2.0], [s*1.1, m[1]-9.0, m[0]+k*0.5]);
    }
  }
  for (const y of [[7.5,21.5,14.5],[7.5,27.6,10.6],[-3,22.6,15.8],[-3,29.2,11.6],[-3,13,18.2],[7.5,13.6,16.4]])
    for (const s of [-1,1]) push([s*y[2]/2, y[1], y[0]], [s*5.4, deck(y[0])+1.6, y[0]-1.4]);
  for (const y of [[7.5,21.5,14.5],[7.5,27.6,10.6],[-3,22.6,15.8],[-3,29.2,11.6]])
    for (const s of [-1,1]) push([s*y[2]/2, y[1], y[0]+0.35], [s*y[2]/2+ s*1.2, y[1]-5.5, y[0]-2.4]);

  /* anchor + cable running forward */
  B.box(3.9, 3.0, 14.6, 1.0, 3.0, 0.7, PAL.iron, 0.05);
  B.box(3.9, 1.6, 14.6, 2.6, 0.6, 0.6, PAL.iron, 0.05);
  B.box(-3.9, 3.0, 14.6, 1.0, 3.0, 0.7, PAL.iron, 0.05);
  B.box(-3.9, 1.6, 14.6, 2.6, 0.6, 0.6, PAL.iron, 0.05);

  const hull = new THREE.Mesh(B.geo(), solidMat);
  hull.castShadow = hull.receiveShadow = true;
  const glow = new THREE.Mesh(G.geo(), glowMat);
  ship.add(hull, glow);

  const rl = new THREE.LineSegments(new THREE.BufferGeometry().setAttribute('position',
    new THREE.Float32BufferAttribute(rig,3)),
    new THREE.LineBasicMaterial({ color:0x2f2721, transparent:true, opacity:0.85 }));
  ship.add(rl);
})();

/* ── fluttering ensigns (animated voxel cloth) ───────────────── */
const flags = [];
function makeFlag(x, y, z, cols, rows, w, h, pal, pivotDir=1){
  const grp = new THREE.Group(); grp.position.set(x,y,z);
  for (let i=0;i<cols;i++){
    const b=new VB();
    for (let r=0;r<rows;r++)
      b.box((i+0.5)*(w/cols)*pivotDir, (r-(rows-1)/2)*(h/rows), 0, w/cols+0.14, h/rows+0.06, 0.3, pal(r,i), 0.05);
    const m=new THREE.Mesh(b.geo(), solidMat); m.castShadow=false; grp.add(m);
  }
  ship.add(grp); flags.push({ grp, cols, w, phase:rnd()*6.3 });
  return grp;
}
makeFlag(0, 36.2, -3, 7, 4, 7.4, 4.4, (r,c)=> (r===1||r===2||c===2||c===3) ? '#e6d9b6' : '#1e3556');
makeFlag(0, 27.6, 7.5, 5, 3, 4.6, 2.6, (r,c)=> (r+c)%2 ? '#d1552f' : '#e6d9b6');
makeFlag(0, 9.4, 30.4, 4, 3, 3.4, 2.0, (r,c)=> (r===1)?'#e6d9b6':'#2c6f5e');
/* dressed-ship signal flags strung along the fore stay */
(function dres(){
  const a=[0,9.4,30], b=[0,30.5,7.5];
  for (let i=1;i<9;i++){
    const t=i/9;
    const p=[lerp(a[0],b[0],t), lerp(a[1],b[1],t)-0.9-0.6*Math.sin(t*Math.PI), lerp(a[2],b[2],t)];
    const b2=new VB();
    b2.box(0,-1.1,0, 2.2, 2.2, 0.25, pick(['#d1552f','#e6d9b6','#1e3556','#2c6f5e','#e8b93a']), 0.08);
    const m=new THREE.Mesh(b2.geo(), solidMat); m.position.set(...p); ship.add(m);
  }
})();

/* town & quay flags (animate with the wind) */
const townFlags = [];
for (const [x,y,z] of [[6,52.4,47],[-11,20.5,13.5],[30,7.4,-14]]){
  W.box(x, y-2.2, z, 0.35, 4.4, 0.35, PAL.iron, 0.04);
  const grp = new THREE.Group(); grp.position.set(x+0.2, y-1.2, z);
  for (let i=0;i<5;i++){
    const b=new VB(); b.box(i*0.72+0.36, 0, 0, 0.86, 2.2, 0.25, i<2?'#c1704a':PAL.cream, 0.06);
    grp.add(new THREE.Mesh(b.geo(), solidMat));
  }
  scene.add(grp); townFlags.push({ grp, cols:5, w:3.6 });
}

/* ══════════════════════════════════════════════════════════════
   9. moving water — instanced columns with wave displacement
══════════════════════════════════════════════════════════════ */
const CS = 2.5, SX0=-92, SX1=76, SZ0=-104, SZ1=4;
const cols = [];
for (let x=SX0; x<=SX1; x+=CS) for (let z=SZ0; z<=SZ1; z+=CS){
  if (isLand(x, z)) continue;
  let near = 999;
  for (const [a,b,c,d] of land) near = Math.min(near,
    Math.max(a-x, x-b, c-z, z-d) > 0 ? Math.hypot(Math.max(a-x,0,x-b), Math.max(c-z,0,z-d)) : 0);
  near = Math.min(near, Math.max(0, Math.max(-2-x, x-34.5, -31-z)) * 0 + Math.min(
    Math.abs(x-30) < 6 ? Math.max(0, -z-1) * 0 + Math.abs(x-30)-5.5 : 999, near));
  cols.push({ x, z, near: Math.min(near, 40) });
}
const seaGeo = new THREE.BoxGeometry(CS, 1, CS);
const seaMesh = new THREE.InstancedMesh(seaGeo, new THREE.MeshStandardMaterial({
  vertexColors:true, roughness:0.26, metalness:0.05 }), cols.length);
seaMesh.receiveShadow = true;
seaMesh.frustumCulled = false;
{
  const im = new THREE.Matrix4();
  for (let i=0;i<cols.length;i++) seaMesh.setMatrixAt(i, im);
  seaMesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
  seaMesh.instanceColor = new THREE.InstancedBufferAttribute(new Float32Array(cols.length*3), 3);
  seaMesh.instanceColor.setUsage(THREE.DynamicDrawUsage);
}
scene.add(seaMesh);

const farSea = new THREE.Mesh(new THREE.PlaneGeometry(4200, 4200),
  new THREE.MeshLambertMaterial({ color:0x1d4152 }));
farSea.rotation.x = -Math.PI/2; farSea.position.y = -0.2; scene.add(farSea);

function waveH(x, z, t, amp){
  return amp*(0.62*Math.sin(x*0.075 + t*0.95) + 0.48*Math.sin(z*0.062 - t*0.75)
       + 0.34*Math.sin((x*0.5+z*0.86)*0.075 + t*1.55) + 0.2*Math.sin((x-z)*0.14 + t*2.4));
}

/* ══════════════════════════════════════════════════════════════
   10. small craft, birds, clouds, smoke, people
══════════════════════════════════════════════════════════════ */
/* rowboats */
function rowboat(col){
  const b=new VB();
  for (let z=-3.2; z<=3.2; z+=0.8){
    const w = 1.75*(1-Math.pow(Math.abs(z)/3.6,2));
    b.box(0, -0.35, z, w*2, 0.7, 0.9, col, 0.07);
    for (const s of [-1,1]) b.box(s*(w+0.15), 0.25, z, 0.34, 0.9, 0.9, col, 0.07);
  }
  for (const z of [-1.2, 1.2]) b.box(0, 0.35, z, 3.4, 0.24, 0.7, PAL.oakLt, 0.06);
  b.box(0, 0.3, 0.4, 0.24, 0.3, 4.6, PAL.oakLt, 0.05);
  b.box(0.55, 0.6, 1.7, 0.18, 0.18, 2.6, PAL.oak, 0.06);
  b.box(0.55, 1.6, 2.5, 0.7, 0.5, 0.7, PAL.oakLt, 0.08);
  const m=new THREE.Mesh(b.geo(), solidMat); m.castShadow=true; return m;
}
const boats = [];
for (const [x,z,ry] of [[-24,-6,0.5],[-20,-9.5,1.4],[26,3,1.9]]){
  const bt = rowboat(pick([PAL.oak, '#3f7a6a', PAL.terraD]));
  bt.position.set(x, 0, z); bt.rotation.y = ry; scene.add(bt); boats.push(bt);
}

/* seagulls */
const birds = [];
for (let i=0;i<7;i++){
  const g = new THREE.Group();
  const body=new VB(); body.box(0,0,0,1.3,0.9,3.2,'#f4f1ea',0.05); body.box(0,0.15,1.8,1.0,0.8,1.0,'#e8e2d4',0.05);
  body.box(0.35,0.2,2.5,0.3,0.25,0.5,'#e8a33a',0.03);
  g.add(new THREE.Mesh(body.geo(), solidMat));
  const wings=[];
  for (const s of [-1,1]){
    const wg=new THREE.Group(); const w=new VB();
    w.box(s*1.9,0,0,3.0,0.3,1.5,'#f8f6f1',0.05); w.box(s*3.6,0,0.2,1.0,0.28,1.2,'#4a4f56',0.05);
    const m=new THREE.Mesh(w.geo(), solidMat); wg.add(m); g.add(wg); wings.push({wg,s});
  }
  g.children.forEach(c=>c.castShadow=false);
  scene.add(g);
  birds.push({ g, wings, r:rr(34,78), cx:rr(-24,26), cz:rr(-28,4), y:rr(24,44),
               spd:rr(0.10,0.22)*(rnd()<0.5?-1:1), ph:rnd()*6.3, flap:rr(5,8) });
}

/* voxel clouds */
const clouds = [];
for (let i=0;i<9;i++){
  const b=new VB(), cx0=rr(-160,170), cz0=rr(-160,120), cy0=rr(52,86);
  const n=ri(14,26);
  for (let k=0;k<n;k++){
    const sx=rr(6,16), sy=rr(4,8), sz=rr(6,15);
    b.box(cx0+rr(-16,16), cy0+rr(-3,6), cz0+rr(-14,14), sx, sy, sz, pick(['#f3f4f6','#e6e9ef','#dfe4ec']), 0.05, 1.0);
  }
  const mat = new THREE.MeshLambertMaterial({ vertexColors:true, fog:false });
  const m = new THREE.Mesh(b.geo(), mat); m.frustumCulled=false; scene.add(m);
  clouds.push({ m, spd:rr(0.35,1.0) });
}

/* chimney smoke */
const smokes = [];
for (const src of smokeSrc) for (let i=0;i<9;i++){
  const m=new THREE.Mesh(new THREE.BoxGeometry(1,1,1),
    new THREE.MeshBasicMaterial({ color:0xbcc2c6, transparent:true, opacity:0.35, depthWrite:false }));
  scene.add(m);
  smokes.push({ m, base:new THREE.Vector3(src[0]+rr(-0.4,0.4), src[1], src[2]+rr(-0.4,0.4)),
                t:rnd(), spd:rr(0.055,0.09) });
}

/* strolling folk on the quay */
const folks = [];
for (let i=0;i<9;i++){
  const p = person(rr(-38,32), rr(0.5,6.5), G0, pick(['#39566f','#7c3f38','#2f5d52','#6b4a7a','#3a3f45']),
                   pick([PAL.oakLt,'#5d6f7e','#8b4a3a','#455a4a']));
  p.userData.x0=rr(-40,10); p.userData.x1=p.userData.x0+rr(14,30);
  scene.add(p); folks.push(p);
}

/* ══════════════════════════════════════════════════════════════
   11. world meshes + pick proxies
══════════════════════════════════════════════════════════════ */
const worldMesh = new THREE.Mesh(W.geo(), solidMat);
worldMesh.castShadow = worldMesh.receiveShadow = true; scene.add(worldMesh);
const glowMesh = new THREE.Mesh(GW.geo(), glowMat); scene.add(glowMesh);
const SHIP_ANCHOR = new THREE.Vector3(-19, 0, -30), SHIP_YAW = 1.53;
ship.position.copy(SHIP_ANCHOR); ship.rotation.y = SHIP_YAW; scene.add(ship);

const pickables = [];
const pickMat = new THREE.MeshBasicMaterial({ colorWrite:false, depthWrite:false, transparent:true, opacity:0 });
function pickable(x,y,z,sx,sy,sz,name,desc){
  const m = new THREE.Mesh(new THREE.BoxGeometry(sx,sy,sz), pickMat);
  m.position.set(x,y,z); m.userData = { name, desc };
  scene.add(m); pickables.push(m); return m;
}
pickable(-19, 12, -30, 46, 40, 30, 'MERIDIAN', 'Barque, 214 tons — riding at anchor off the mole. Topsails still set; courses struck and furled.');
pickable(30, 34, -26, 16, 52, 16, 'THE LONG LIGHT', 'Built 1704. Keeper reports four calls a night; the beam carries eleven miles.');
pickable(30, 3, -16, 14, 16, 32, 'NORTH MOLE', 'Rubble pier thrown out to break the swell that used to undo the fishing fleet.');
pickable(24, 12, 4, 16, 16, 14, 'THE GREAT CRANE', 'Cable and counterweight. Ten tons off the lighters, an afternoon’s work.');
pickable(-11, 10, 14.5, 22, 14, 16, 'CUSTOMS WAREHOUSE', 'Salt, hides, tallow and half a crate of Portuguese tin plates.');
pickable(6, 34, 47, 22, 26, 24, 'HARBOUR CHURCH', 'St. Brendan of the Anchorage — the clock has run three minutes fast since the storm.');
pickable(-62, 12, 8, 20, 20, 20, 'GULL’S POINT', 'Windmill above the rocks; the miller signals weather by tilting a single sail.');
pickable(-3, 5, 1, 80, 10, 12, 'THE LONG QUAY', 'Two hundred fathoms of granite, cobbled twice since the sea took the first.');
pickable(-22, 1, -8, 10, 5, 10, 'MARGIN', 'A pilot gig, hired for the trip out to the anchorage.');

const hilite = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(1,1,1)),
  new THREE.LineBasicMaterial({ color:0xffb340, transparent:true, opacity:0.9, depthTest:false, toneMapped:false }));
hilite.visible = false; hilite.renderOrder = 20; scene.add(hilite);

/* ══════════════════════════════════════════════════════════════
   12. time-of-day engine
══════════════════════════════════════════════════════════════ */
const C = h => new THREE.Color(h);
const KEYS = [
  { t:0,    top:'#03060f', mid:'#0a1430', bot:'#16273d', sunC:'#8fb6ff', sunI:0.55, hemiS:'#2b4a78', hemiG:'#141c26', hemiI:0.42, ambI:0.36, ambC:'#6a86b0', fog:'#111f33', far:'#0a1d31', seaD:'#041019', seaS:'#123649', win:1.65, glow:1.7, star:1, moon:1 },
  { t:4.4,  top:'#071229', mid:'#173258', bot:'#3d5675', sunC:'#a9c4f5', sunI:0.62, hemiS:'#3b5c8c', hemiG:'#20262f', hemiI:0.48, ambI:0.38, ambC:'#7e96bb', fog:'#25405c', far:'#163349', seaD:'#081927', seaS:'#1b4358', win:1.45, glow:1.55, star:0.72, moon:0.75 },
  { t:6.35, top:'#24456f', mid:'#8e6f80', bot:'#f4a65e', sunC:'#ffb877', sunI:1.7,  hemiS:'#87a6c6', hemiG:'#4b4136', hemiI:0.56, ambI:0.40, ambC:'#c98f6c', fog:'#d8a982', far:'#5a7280', seaD:'#153444', seaS:'#3a7383', win:0.85, glow:1.05, star:0.12, moon:0.05 },
  { t:9.4,  top:'#2f6cb2', mid:'#83b6da', bot:'#d9e6e8', sunC:'#fff0d4', sunI:2.9,  hemiS:'#9dc6e6', hemiG:'#6d6046', hemiI:0.60, ambI:0.42, ambC:'#b4c9d6', fog:'#cfe0e6', far:'#2f7286', seaD:'#16495f', seaS:'#2f8ba0', win:0.30, glow:0.55, star:0, moon:0 },
  { t:13.0, top:'#2a6fbd', mid:'#8dc0e2', bot:'#e3eff0', sunC:'#ffffff', sunI:3.55, hemiS:'#a8d2ef', hemiG:'#786a4d', hemiI:0.62, ambI:0.44, ambC:'#c3d8e4', fog:'#dfeaf0', far:'#2b8497', seaD:'#165a72', seaS:'#2f9db5', win:0.22, glow:0.45, star:0, moon:0 },
  { t:16.4, top:'#34699f', mid:'#94b6cf', bot:'#f0d3a4', sunC:'#ffd8a0', sunI:3.05, hemiS:'#9dbdd6', hemiG:'#6f6146', hemiI:0.58, ambI:0.42, ambC:'#d3b793', fog:'#e3d0b4', far:'#33788a', seaD:'#164e61', seaS:'#3390a4', win:0.42, glow:0.7, star:0, moon:0 },
  { t:18.55,top:'#22456f', mid:'#a86a5f', bot:'#ffb054', sunC:'#ff9a3f', sunI:2.55, hemiS:'#7a9ec2', hemiG:'#5b4a36', hemiI:0.56, ambI:0.40, ambC:'#e8a875', fog:'#eab285', far:'#3d6a76', seaD:'#123448', seaS:'#2f6f86', win:1.05, glow:1.25, star:0.05, moon:0 },
  { t:19.75,top:'#122445', mid:'#573d61', bot:'#f0714a', sunC:'#ff7b3e', sunI:1.1,  hemiS:'#4b5c86', hemiG:'#3a3228', hemiI:0.50, ambI:0.37, ambC:'#b06a5a', fog:'#93606a', far:'#26394d', seaD:'#0b1f31', seaS:'#1f4c63', win:1.42, glow:1.55, star:0.45, moon:0.25 },
  { t:21.3, top:'#060c22', mid:'#11224a', bot:'#27405e', sunC:'#8fb0e8', sunI:0.7,  hemiS:'#2f4a78', hemiG:'#191f28', hemiI:0.44, ambI:0.35, ambC:'#6d84a8', fog:'#1a2c44', far:'#0f2437', seaD:'#061525', seaS:'#133c52', win:1.62, glow:1.7, star:0.9, moon:0.9 },
  { t:24,   top:'#03060f', mid:'#0a1430', bot:'#16273d', sunC:'#8fb6ff', sunI:0.55, hemiS:'#2b4a78', hemiG:'#141c26', hemiI:0.42, ambI:0.36, ambC:'#6a86b0', fog:'#111f33', far:'#0a1d31', seaD:'#041019', seaS:'#123649', win:1.65, glow:1.7, star:1, moon:1 }
];
for (const k of KEYS) for (const key of ['top','mid','bot','sunC','hemiS','hemiG','fog','far','seaD','seaS','ambC'])
  k[key] = C(k[key]);

const A = { top:C('#000'), mid:C('#000'), bot:C('#000'), sunC:C('#000'), hemiS:C('#000'), hemiG:C('#000'),
            fog:C('#000'), far:C('#000'), seaD:C('#000'), seaS:C('#000'), ambC:C('#000') };
let T = 18.55, wind = 0.42, timeLapse = false;

function applyTime(t){
  let i = 0; while (i < KEYS.length-2 && KEYS[i+1].t <= t) i++;
  const a = KEYS[i], b = KEYS[i+1], k = clamp((t-a.t)/(b.t-a.t), 0, 1);
  for (const key in A) A[key].copy(a[key]).lerp(b[key], k);
  const g = (f) => lerp(a[f], b[f], k);

  skyU.uTop.value.copy(A.top); skyU.uMid.value.copy(A.mid); skyU.uBot.value.copy(A.bot);
  skyU.uSun.value.copy(A.sunC); skyU.uGlow.value = g('glow');
  scene.fog.color.copy(A.fog); scene.fog.density = lerp(0.0034, 0.0026, g('sunI')/3.55);
  farSea.material.color.copy(A.far);

  const dayT = (t - 5.4) / 13.8;
  const el = Math.sin(Math.PI*clamp(dayT,0,1)) * 58 - 1.5;
  const az = THREE.MathUtils.degToRad(180 + 120*(dayT - 0.5));
  const dir = new THREE.Vector3(Math.sin(az)*Math.cos(el*Math.PI/180), Math.sin(el*Math.PI/180), Math.cos(az)*Math.cos(el*Math.PI/180));
  if (dir.lengthSq() < 0.02) dir.set(0,0.5,-1).normalize();
  skyU.uSunDir.value.copy(dir);
  sun.color.copy(A.sunC); sun.intensity = g('sunI');
  sun.position.copy(dir).multiplyScalar(150).add(new THREE.Vector3(-8,0,-12));
  sunMesh.position.copy(dir).multiplyScalar(620); moonMesh.position.copy(dir).multiplyScalar(-620);
  sunMesh.material.opacity  = smoothstep(-0.02, 0.10, dir.y);
  moonMesh.material.opacity = (1-smoothstep(-0.02,0.10,dir.y)) * g('moon');
  sunMesh.visible = sunMesh.material.opacity > 0.02; moonMesh.visible = !sunMesh.visible;

  hemi.color.copy(A.hemiS); hemi.groundColor.copy(A.hemiG); hemi.intensity = g('hemiI');
  amb.color.copy(A.ambC); amb.intensity = g('ambI');
  fill.intensity = 0.10 + 0.28*(1-smoothstep(0,0.25,dir.y));

  const night = 1 - smoothstep(0.02, 0.28, dir.y);
  glowMat.color.setRGB(0.16,0.15,0.14).lerp(new THREE.Color(1,1,1), g('win')*0.62);
  for (const l of lampLights) l.intensity = night * (l === lampLights[5] ? 1.9 : 0.85);
  beamLight.intensity = night * 2.4;
  scene.userData.beam.children.forEach(c=>{ if (c.material && c.material.blending === THREE.AdditiveBlending) c.material.opacity = 0.02 + night*0.13; });
  stars.material.opacity = g('star') * 0.9;
  for (const cl of clouds) cl.m.material.color.copy(A.mid).lerp(new THREE.Color(1,1,1), 0.42 + 0.4*g('sunI')/3.55);

  seaColDeep.copy(A.seaD); seaColShal.copy(A.seaS);
  seaMesh.material.color.copy(A.far).lerp(new THREE.Color(1,1,1), 0.18);
  const st = g('seaS'); document.getElementById('st').textContent = ['glassy','slight','smooth','moderate','rough','very rough'][clamp(Math.round(1+wind*4.5),0,5)];
  return { night };
}
const seaColDeep = new THREE.Color(), seaColShal = new THREE.Color();
const tmpCol = new THREE.Color(), F1 = new THREE.Color(), F2 = new THREE.Color();
F1.setHex(0x123549); F2.setRGB(0.7,0.75,0.78);
applyTime(T);

/* ══════════════════════════════════════════════════════════════
   13. interaction — hover tags, click-to-focus, viewpoints
══════════════════════════════════════════════════════════════ */
const ray = new THREE.Raycaster(); const ndc = new THREE.Vector2(2,2);
const tip = document.getElementById('tip'), tipB = tip.querySelector('b'), tipS = tip.querySelector('span');
let mouse = { x:0, y:0 }, hovered = null, lastAct = performance.now();
const act = () => { lastAct = performance.now(); };
canvas.addEventListener('pointermove', e => {
  mouse.x = e.clientX; mouse.y = e.clientY;
  ndc.x = (e.clientX/innerWidth)*2 - 1; ndc.y = -(e.clientY/innerHeight)*2 + 1;
});
canvas.addEventListener('pointerdown', e => {
  act();
  ndc.x = (e.clientX/innerWidth)*2 - 1; ndc.y = -(e.clientY/innerHeight)*2 + 1;
  ray.setFromCamera(ndc, camera);
  const hit = ray.intersectObjects(pickables, false)[0];
  if (hit) {
    const box = new THREE.Box3().setFromObject(hit.object);
    const c = box.getCenter(new THREE.Vector3());
    const r = box.getSize(new THREE.Vector3()).length();
    const dir = camera.position.clone().sub(c).normalize();
    flyTo(c.clone().add(dir.multiplyScalar(Math.max(22, r*0.85))), c);
  }
}, { passive:true });
canvas.addEventListener('wheel', act, { passive:true });
canvas.addEventListener('touchstart', act, { passive:true });

const VIEWS = [
  new THREE.Vector3(-82, 38, -66), new THREE.Vector3(-6, 10, -8),
  new THREE.Vector3(-6, 15, -52),  new THREE.Vector3(4, 12, 30),
  new THREE.Vector3(14, 20, -52),  new THREE.Vector3(30, 22, -26),
  new THREE.Vector3(-14, 12, -34), new THREE.Vector3(-19, 26, -30),
  new THREE.Vector3(48, 128, -58), new THREE.Vector3(-4, 6, -10)
];
let tween = null;
const ease = x => x<0.5 ? 4*x*x*x : 1-Math.pow(-2*x+2,3)/2;
function flyTo(p, t, dur=1500){
  tween = { t0:performance.now(), dur, p0:camera.position.clone(), t0v:controls.target.clone(), p1:p.clone(), t1v:t.clone() };
  act();
}
function setView(i){
  flyTo(VIEWS[i*2], VIEWS[i*2+1]);
  document.querySelectorAll('[data-v]').forEach(b=>b.classList.toggle('on', +b.dataset.v === i));
}
document.querySelectorAll('[data-v]').forEach(b => b.onclick = () => setView(+b.dataset.v));
setView(0); tween = null;

const timeEl = document.getElementById('time'), timeOut = document.getElementById('timeOut');
const windEl = document.getElementById('wind'), windOut = document.getElementById('windOut');
const fmt = t => `${String(Math.floor(t)%24).padStart(2,'0')}:${String(Math.floor((t%1)*60)).padStart(2,'0')}`;
timeEl.oninput = () => { T = +timeEl.value; timeOut.textContent = fmt(T); document.querySelectorAll('[data-time]').forEach(b=>b.classList.remove('on')); applyTime(T); act(); };
windEl.oninput = () => { wind = +windEl.value/100; windOut.textContent = `${clamp(Math.round(1+wind*8),1,9)} bft`; act(); };
document.querySelectorAll('[data-time]').forEach(b => b.onclick = () => {
  T = +b.dataset.time; timeEl.value = T; timeOut.textContent = fmt(T);
  document.querySelectorAll('[data-time]').forEach(x=>x.classList.toggle('on', x===b));
  timeLapse = false; play.classList.remove('on');
  applyTime(T);
});
const play = document.getElementById('play');
play.onclick = () => { timeLapse = !timeLapse; play.classList.toggle('on', timeLapse); };
let autoOrbit = true;
addEventListener('keydown', e => {
  if (e.key >= '1' && e.key <= '5') setView(+e.key - 1);
  if (e.code === 'Space'){ e.preventDefault(); autoOrbit = !autoOrbit; }
  if (e.key === 't' || e.key === 'T') play.click();
});

/* ══════════════════════════════════════════════════════════════
   14. animate
══════════════════════════════════════════════════════════════ */
document.getElementById('vx').textContent = VOXELS.toLocaleString();
timeOut.textContent = fmt(T); windOut.textContent = '4 bft';

const clock = new THREE.Clock();
let fpsAcc = 0, fpsN = 0, fpsT = 0;
const needle = document.getElementById('needle');
const bobPos = new THREE.Vector3();

function loop(){
  requestAnimationFrame(loop);
  const dt = Math.min(clock.getDelta(), 0.05), t = clock.elapsedTime;

  if (timeLapse){ T = (T + dt*0.42) % 24; timeEl.value = T; timeOut.textContent = fmt(T); }
  const { night } = applyTime(T);

  /* ── water ─────────────────────────────────────────────────── */
  const amp = 0.55 + wind*1.7;
  const M = seaMesh.instanceMatrix.array, Cc = seaMesh.instanceColor.array;
  for (let i=0; i<cols.length; i++){
    const c = cols[i];
    const h = waveH(c.x, c.z, t, amp) + 0.4;
    const o = i*16;
    M[o]=CS; M[o+5]=Math.max(0.6,h+7); M[o+10]=CS;
    M[o+12]=c.x; M[o+13]=-7 + (h+7)/2; M[o+14]=c.z;
    const crest = smoothstep(0.62*amp, 1.15*amp, h-0.4);
    const shore  = crest * smoothstep(11, 2, c.near) * 0.9;
    const foam   = clamp(crest*0.75 + shore, 0, 1);
    tmpCol.copy(seaColDeep).lerp(seaColShal, smoothstep(-1.4, 1.6, h));
    tmpCol.lerp(F2, foam*0.85);
    const co=i*3; Cc[co]=tmpCol.r; Cc[co+1]=tmpCol.g; Cc[co+2]=tmpCol.b;
  }
  seaMesh.instanceMatrix.needsUpdate = true;
  seaMesh.instanceColor.needsUpdate  = true;

  /* ── the ship rides the tide ───────────────────────────────── */
  const S = SHIP_ANCHOR;
  const hC = waveH(S.x, S.z, t, amp*0.92);
  const hB = waveH(S.x+Math.sin(SHIP_YAW)*14, S.z+Math.cos(SHIP_YAW)*14, t, amp*0.92);
  const hS = waveH(S.x-Math.sin(SHIP_YAW)*14, S.z-Math.cos(SHIP_YAW)*14, t, amp*0.92);
  const hL = waveH(S.x+Math.cos(SHIP_YAW)*6,  S.z-Math.sin(SHIP_YAW)*6,  t, amp*0.92);
  const hR = waveH(S.x-Math.cos(SHIP_YAW)*6,  S.z+Math.sin(SHIP_YAW)*6,  t, amp*0.92);
  ship.position.set(S.x + Math.sin(t*0.35)*0.35, hC - 0.35, S.z + Math.cos(t*0.28)*0.3);
  ship.rotation.set(Math.atan2(hS-hB, 28)*0.85, SHIP_YAW + Math.sin(t*0.18)*0.012,
                    Math.atan2(hL-hR, 12)*0.8 + wind*0.05);

  for (const b of boats){
    const y = waveH(b.position.x, b.position.z, t, amp) - 0.15;
    b.position.y += (y - b.position.y)*0.25;
    b.rotation.x = Math.sin(t*0.9 + b.position.x)*0.05;
    b.rotation.z = Math.sin(t*1.1 + b.position.z)*0.06;
  }
  craneHook.rotation.z = Math.sin(t*0.55)*0.07;

  /* flags */
  for (const f of flags) for (let i=0;i<f.cols;i++){
    const m = f.grp.children[i], k = i/(f.cols-1);
    m.rotation.y = Math.sin(t*3.2 + f.phase + k*2.1)*0.34*(0.35+wind);
    m.position.z = Math.sin(t*2.6 + f.phase + k*1.7)*0.42*(0.3+wind);
    m.position.y = -Math.pow(k,1.6)*0.9;
  }
  for (const f of townFlags) for (let i=0;i<f.cols;i++){
    const m = f.grp.children[i], k=i/(f.cols-1);
    m.rotation.y = Math.sin(t*2.4 + k*1.9)*0.3*(0.3+wind);
    m.position.z = Math.sin(t*2.0 + k*1.5)*0.3*(0.3+wind);
  }

  /* birds */
  for (const b of birds){
    b.ph += dt*b.spd;
    const y = b.y + Math.sin(t*0.7 + b.flap)*2.2;
    b.g.position.set(b.cx + Math.cos(b.ph)*b.r, y, b.cz + Math.sin(b.ph)*b.r*0.8);
    b.g.rotation.y = -b.ph + (b.spd>0 ? Math.PI/2 : -Math.PI/2);
    const flap = Math.sin(t*b.flap + b.y)*0.55;
    for (const w of b.wings) w.wg.rotation.z = -w.s*(0.15 + flap);
  }

  /* clouds */
  for (const c of clouds){
    c.m.position.x += dt*c.spd*(0.4+wind*1.5);
    if (c.m.position.x > 260) c.m.position.x = -300;
  }

  /* smoke */
  for (const s of smokes){
    s.t += dt*s.spd*(0.6+wind);
    if (s.t > 1) s.t -= 1;
    const k = s.t;
    s.m.position.set(s.base.x + k*k*(6+wind*26), s.base.y + k*15, s.base.z + k*(2+wind*10));
    const sc = 0.9 + k*4.6; s.m.scale.set(sc, sc*0.75, sc);
    s.m.material.opacity = 0.42*Math.sin(Math.PI*clamp(k,0.02,1))*(1-night*0.45);
    s.m.rotation.y = k*2;
  }

  /* strolls */
  for (const p of folks){
    const u = p.userData;
    p.position.x += u.dir*dt*1.5;
    if (p.position.x > u.x1) u.dir = -1; if (p.position.x < u.x0) u.dir = 1;
    p.rotation.y = u.dir > 0 ? Math.PI/2 : -Math.PI/2;
    const step = Math.sin(t*7 + u.phase);
    p.position.y = G0 + 0.05 + Math.abs(step)*0.13;
    u.legs.rotation.z = step*0.22;
  }

  /* lighthouse sweep */
  scene.userData.beam.rotation.y = t*0.42;

  /* hover pick */
  ray.setFromCamera(ndc, camera);
  const hit = ray.intersectObjects(pickables, false)[0];
  if (hit && hit.object !== hovered){
    hovered = hit.object;
    tipB.textContent = hovered.userData.name; tipS.textContent = hovered.userData.desc;
    tip.classList.add('show');
    hilite.visible = true;
    const box = new THREE.Box3().setFromObject(hovered);
    const ctr = box.getCenter(new THREE.Vector3()), sz = box.getSize(new THREE.Vector3()).addScalar(1.2);
    hilite.position.copy(ctr); hilite.scale.copy(sz);
  } else if (!hit && hovered){
    hovered = null; tip.classList.remove('show'); hilite.visible = false;
  }
  if (hovered){
    tip.style.left = mouse.x + 'px'; tip.style.top = mouse.y - 6 + 'px';
    const k = 1 + Math.sin(t*4)*0.012;
    hilite.scale.multiplyScalar(1 + (k - hilite.scale.x/hilite.userData.sx || 0));
    hilite.material.opacity = 0.55 + Math.sin(t*4)*0.25;
    canvas.style.cursor = 'pointer';
  } else canvas.style.cursor = 'grab';

  /* camera */
  if (tween){
    const k = ease(clamp((performance.now()-tween.t0)/tween.dur, 0, 1));
    camera.position.lerpVectors(tween.p0, tween.p1, k);
    controls.target.lerpVectors(tween.t0v, tween.t1v, k);
    if (k >= 1) tween = null;
  }
  controls.autoRotate = autoOrbit && !tween && performance.now() - lastAct > 3800;
  controls.update();

  const ang = Math.atan2(camera.position.x - controls.target.x, camera.position.z - controls.target.z);
  needle.setAttribute('transform', `rotate(${(-ang*180/Math.PI).toFixed(1)} 50 50)`);

  renderer.render(scene, camera);

  fpsAcc += dt; fpsN++;
  if (fpsAcc > 0.5){
    document.getElementById('fps').textContent = Math.round(fpsN/fpsAcc);
    document.getElementById('dc').textContent  = renderer.info.render.calls;
    fpsAcc = 0; fpsN = 0;
  }
}
loop();

addEventListener('resize', () => {
  camera.aspect = innerWidth/innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
</script>
</body>
</html>
```

**What's in there**

- **One draw per material** — ~2,500 cubes (terrain, town, ship, breakwater) are merged into a single vertex-coloured buffer with per-face fake-AO shading and per-block colour jitter, so it's the classic voxel-art look at very little cost. Only the sea, clouds, birds, smoke and flags move.
- **The sea is alive**: 2,300 instanced columns displaced by four summed wave trains, with white foam on crests and heavier foam where the swell meets the quay and the mole. The barque samples the swell at bow/stern/port/starboard, so it genuinely pitches, rolls and heels with the wind slider — and the rowboats rock alongside.
- **The ship** is a three-masted barque at anchor: courses struck and furled on the yards, topsails still set and billowing, stepped-triangle jibs, spanker, dressed-ship signal flags strung up the fore stay, gunports with cannon muzzles, stern gallery windows lit, and a fluttering quartered ensign.
- **Harbour life**: rotating lighthouse beam with a real spotlight sweep, masonry-coursed terraces, church with a working clock face, warehouse, great crane with a swaying crate, market stalls, nets, bollards and coils, lanterns that strike up at dusk, chimney smoke drifting with the wind, circling gulls and nine dockworkers on the stroll.
- **Time of day** is a full keyframed engine (sky gradient, sun path, fog, sea colour ramps, window luminance, stars, lamp glow) — scrub it, hit a preset, or let the time-lapse run.
- **Interaction**: orbit/zoom/pan, hover any landmark for a tagged label with a blocky highlight cage, click to fly the camera there, keys 1–5 for viewpoints, space to free the slow auto-orbit.