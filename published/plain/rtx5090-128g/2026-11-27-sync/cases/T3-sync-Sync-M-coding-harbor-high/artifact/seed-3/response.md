Below is a complete single-file scene — a voxel harbour at golden hour: a brig moored at berth three, the lighthouse sweeping the mouth, a gantry crane working cargo, a mill turning on the hill, and tide, wind and hour under your mouse.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>Calling at Belhaven — a voxel harbour</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400..800&family=IBM+Plex+Mono:wght@400;500;600&family=Spline+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box}
html,body{margin:0;height:100%;overflow:hidden;background:#04080f}
#scene{position:fixed;inset:0;display:block;cursor:grab}
#scene.pick{cursor:pointer}
#scene:active{cursor:grabbing}

:root{
  --ink:#060c15; --panel:rgba(8,14,23,.68); --panel2:rgba(8,14,23,.86);
  --line:rgba(231,186,109,.30); --line-soft:rgba(180,205,225,.16);
  --brass:#e7ba6d; --brass-lo:#a97f3e; --foam:#eef4f8; --muted:#9db1c6;
  --sea:#7cc3dd; --rust:#df6a45;
  --disp:'Bricolage Grotesque',ui-serif,Georgia,serif;
  --body:'Spline Sans',system-ui,-apple-system,sans-serif;
  --mono:'IBM Plex Mono',ui-monospace,monospace;
}
/* atmosphere overlay: vignette + faint film grain + horizon haze */
#grain{position:fixed;inset:0;pointer-events:none;z-index:2;
  background:radial-gradient(125% 95% at 52% 42%,rgba(0,0,0,0) 40%,rgba(3,7,14,.62) 100%);}
#grain::after{content:'';position:absolute;inset:0;opacity:.055;mix-blend-mode:overlay;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='120' height='120'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2'/></filter><rect width='120' height='120' filter='url(%23n)'/></svg>");}

#ui{position:fixed;inset:0;z-index:3;pointer-events:none;
  display:grid;grid-template-columns:minmax(250px,330px) 1fr minmax(230px,330px);
  grid-template-rows:auto 1fr auto;gap:16px;padding:22px 24px;color:var(--foam);
  font-family:var(--body);}
#ui>*{pointer-events:auto}
body.hide-ui #ui,body.hide-ui #compass{opacity:0;transform:translateY(10px) scale(.995);pointer-events:none}
#ui,body.hide-ui *{transition:opacity .5s cubic-bezier(.2,.8,.2,1),transform .5s cubic-bezier(.2,.8,.2,1)}

/* ---------- masthead ---------- */
.masthead{grid-area:1/1/2/3;align-self:start;max-width:min(720px,54vw)}
.kicker{font-family:var(--mono);font-size:10.5px;letter-spacing:.3em;text-transform:uppercase;
  color:var(--brass);display:flex;gap:14px;align-items:center}
.kicker i{display:block;width:26px;height:26px;border:1px solid var(--line);position:relative;background:rgba(231,186,109,.07)}
.kicker i::before,.kicker i::after{content:'';position:absolute;background:var(--brass)}
.kicker i::before{left:6px;right:6px;top:7px;height:4px}
.kicker i::after{left:11px;right:11px;top:12px;bottom:5px}
h1{font-family:var(--disp);font-weight:800;font-size:clamp(30px,4.6vw,62px);line-height:.9;
  margin:12px 0 0;letter-spacing:-.028em;text-wrap:balance;text-shadow:0 8px 34px rgba(0,0,0,.55)}
h1 em{font-style:normal;color:var(--brass)}
h1 span{display:block;font-weight:300;font-size:.42em;letter-spacing:.02em;color:#cfe0ec;
  margin-top:6px;opacity:.9}
.lede{max-width:52ch;margin:14px 0 0;font-size:13.5px;line-height:1.62;color:#c9d8e6;
  border-left:2px solid var(--line);padding-left:14px}

/* ---------- readout chips ---------- */
.readout{grid-area:1/3/2/4;justify-self:end;display:grid;grid-template-columns:repeat(3,minmax(78px,1fr));
  gap:8px;max-width:340px}
.chip{border:1px solid var(--line-soft);background:var(--panel);padding:8px 10px 9px;position:relative;
  backdrop-filter:blur(4px);transition:border-color .2s,background .2s,transform .2s}
.chip:hover{border-color:var(--line);transform:translateY(-2px)}
.chip b{display:block;font-family:var(--mono);font-weight:600;font-size:19px;letter-spacing:-.01em;
  color:#fff;line-height:1.15}
.chip s{display:block;text-decoration:none;font-family:var(--mono);font-size:9px;letter-spacing:.22em;
  text-transform:uppercase;color:var(--muted);margin-top:3px}
.chip.wide{grid-column:span 2}
.chip.hot b{color:var(--brass)}

/* ---------- ledger (left) ---------- */
.ledger{grid-area:2/1/3/2;align-self:stretch;justify-self:start;width:min(330px,32vw);
  border:1px solid var(--line-soft);background:var(--panel2);backdrop-filter:blur(7px);
  display:flex;flex-direction:column;min-height:0;max-height:100%;overflow:hidden}
.phead{display:flex;justify-content:space-between;align-items:baseline;padding:11px 13px 9px;
  border-bottom:1px solid var(--line-soft);font-family:var(--mono);font-size:10px;letter-spacing:.26em;
  text-transform:uppercase;color:var(--brass)}
.phead u{text-decoration:none;color:var(--muted)}
.rows{overflow:auto;padding:6px 0 8px;scrollbar-width:thin;scrollbar-color:var(--brass-lo) transparent}
.rows::-webkit-scrollbar{width:5px}.rows::-webkit-scrollbar-thumb{background:var(--brass-lo)}
.row{display:grid;grid-template-columns:22px 1fr auto;gap:10px;align-items:baseline;width:100%;
  background:none;border:0;border-left:2px solid transparent;color:var(--foam);text-align:left;
  padding:8px 13px;font-family:var(--body);cursor:pointer;transition:background .18s,border-color .18s,padding .18s}
.row .idx{font-family:var(--mono);font-size:10px;color:var(--brass-lo)}
.row .nm{font-size:13.5px;font-weight:500;letter-spacing:-.01em}
.row .mt{font-family:var(--mono);font-size:9px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);white-space:nowrap}
.row:hover,.row.hov{background:rgba(231,186,109,.10);border-left-color:var(--brass);padding-left:17px}
.row.sel{background:rgba(231,186,109,.16);border-left-color:var(--brass)}
.row.sel .nm{color:var(--brass)}

/* ---------- notes / dossier / log (right) ---------- */
.notes{grid-area:2/3/3/4;align-self:end;justify-self:end;width:min(330px,32vw);display:flex;
  flex-direction:column;gap:12px;min-height:0}
.dossier{border:1px solid var(--line);background:var(--panel2);backdrop-filter:blur(8px);padding:14px 15px 13px;
  transform-origin:bottom right;animation:rise .6s .5s cubic-bezier(.2,.9,.2,1) both}
.dossier.empty{opacity:.0;pointer-events:none;height:0;padding:0;border:0;overflow:hidden}
.dossier h2{font-family:var(--disp);font-weight:700;font-size:21px;letter-spacing:-.02em;margin:0 0 4px}
.dossier .sub{font-family:var(--mono);font-size:9px;letter-spacing:.24em;text-transform:uppercase;color:var(--brass);margin-bottom:9px}
.dossier p{margin:0 0 10px;font-size:12.6px;line-height:1.6;color:#c7d6e4}
.specs{display:grid;grid-template-columns:1fr 1fr;gap:6px 10px;border-top:1px solid var(--line-soft);padding-top:9px}
.specs div{display:flex;justify-content:space-between;gap:6px;font-family:var(--mono);font-size:10px}
.specs span{color:var(--muted);letter-spacing:.1em;text-transform:uppercase}
.specs b{color:#fff}
.dossier .x{float:right;border:1px solid var(--line-soft);background:none;color:var(--muted);
  font-family:var(--mono);font-size:11px;line-height:1;padding:4px 6px;cursor:pointer;transition:.18s}
.dossier .x:hover{color:var(--rust);border-color:var(--rust)}

.log{border:1px solid var(--line-soft);background:var(--panel);backdrop-filter:blur(5px);min-height:0;
  display:flex;flex-direction:column;animation:rise .6s .72s cubic-bezier(.2,.9,.2,1) both}
.logs{overflow:auto;padding:8px 12px 10px;font-family:var(--mono);font-size:10.6px;line-height:1.5}
.logs p{margin:0 0 6px;color:#b9cbdb;display:grid;grid-template-columns:44px 1fr;gap:8px;
  animation:slidein .45s cubic-bezier(.2,.9,.2,1) both}
.logs p time{color:var(--brass-lo)}
.logs p:nth-child(n+5){opacity:.55}
.logs p:last-child{color:#fff}

/* ---------- console (bottom) ---------- */
.console{grid-area:3/1/4/4;display:flex;flex-wrap:wrap;gap:10px 12px;align-items:center;
  border-top:1px solid var(--line-soft);padding-top:12px;animation:rise .6s .38s cubic-bezier(.2,.9,.2,1) both}
.grp{display:flex;gap:6px;align-items:center;border:1px solid var(--line-soft);background:var(--panel);
  backdrop-filter:blur(5px);padding:7px 9px}
.grp .lab{font-family:var(--mono);font-size:9px;letter-spacing:.24em;text-transform:uppercase;color:var(--muted)}
.btn{font-family:var(--mono);font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;
  border:1px solid var(--line-soft);background:transparent;color:var(--foam);padding:6px 9px;cursor:pointer;
  transition:background .18s,color .18s,border-color .18s,transform .18s}
.btn:hover{background:rgba(231,186,109,.14);border-color:var(--brass);transform:translateY(-1px)}
.btn.on{background:rgba(231,186,109,.2);border-color:var(--brass);color:#fff}
.btn.warn:hover{border-color:var(--rust);color:var(--rust)}
.slide{display:flex;gap:8px;align-items:center;font-family:var(--mono);font-size:10px;color:var(--muted)}
.slide b{color:#fff;min-width:52px;text-align:right;letter-spacing:.06em}
input[type=range]{-webkit-appearance:none;appearance:none;width:112px;height:2px;background:rgba(231,186,109,.35);outline:none}
input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:13px;height:13px;background:var(--brass);
  border:2px solid #23180a;cursor:pointer;box-shadow:0 0 12px rgba(231,186,109,.55);transition:transform .15s}
input[type=range]::-webkit-slider-thumb:hover{transform:scale(1.22)}
input[type=range]::-moz-range-thumb{width:11px;height:11px;background:var(--brass);border:2px solid #23180a;cursor:pointer}
.hint{margin-left:auto;font-family:var(--mono);font-size:9.5px;letter-spacing:.16em;text-transform:uppercase;color:#7f93a8}
.hint kbd{border:1px solid var(--line-soft);padding:2px 5px;margin-right:2px;color:var(--muted)}

/* ---------- compass ---------- */
#compass{position:fixed;left:24px;bottom:96px;z-index:3;width:74px;height:74px;pointer-events:none;
  transition:opacity .4s}
#compass svg{width:100%;height:100%;overflow:visible}
#compass .needle{transition:transform .12s linear}

/* ---------- tooltip + boot ---------- */
#tip{position:fixed;z-index:4;pointer-events:none;opacity:0;transform:translate(-50%,-140%);
  font-family:var(--mono);font-size:10px;letter-spacing:.16em;text-transform:uppercase;white-space:nowrap;
  border:1px solid var(--brass);background:rgba(6,11,19,.9);padding:6px 9px;color:#fff;
  box-shadow:0 10px 28px rgba(0,0,0,.5);transition:opacity .16s}
#tip u{text-decoration:none;color:var(--brass);margin-left:8px}
#boot{position:fixed;inset:0;z-index:6;display:flex;flex-direction:column;justify-content:center;align-items:flex-start;
  gap:14px;padding:0 8vw;background:#04080f;transition:opacity .7s .15s}
#boot .big{font-family:var(--disp);font-weight:800;font-size:clamp(26px,5vw,58px);letter-spacing:-.03em;color:var(--foam)}
#boot .sm{font-family:var(--mono);font-size:11px;letter-spacing:.3em;text-transform:uppercase;color:var(--brass)}
#boot .bar{width:min(420px,60vw);height:3px;background:rgba(231,186,109,.2)}
#boot .bar i{display:block;height:100%;width:6%;background:var(--brass);transition:width .3s}
#boot.gone{opacity:0;pointer-events:none}

@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@keyframes slidein{from{opacity:0;transform:translateX(-10px)}to{opacity:1;transform:none}}

@media (max-width:900px){
  #ui{grid-template-columns:1fr auto;grid-template-rows:auto 1fr auto;padding:14px}
  .masthead{grid-area:1/1/2/2;max-width:none}
  .readout{grid-area:1/2/2/3;grid-template-columns:repeat(2,1fr);max-width:190px}
  .ledger,.notes{display:none}
  .hint{display:none}
  #compass{left:14px;bottom:104px;width:58px;height:58px}
}
</style>
</head>
<body>
<canvas id="scene"></canvas>
<div id="grain"></div>

<div id="ui">
  <header class="masthead">
    <div class="kicker"><i></i> Harbour Authority · Port of Belhaven</div>
    <h1>Calling at <em>Belhaven</em><span>A brig comes in on the flood tide — 30,000-odd blocks, lit live.</span></h1>
    <p class="lede">Drag to walk the quay, scroll to bring the masts closer, click any landmark to have the launch take you there. The tide, the wind and the hour are yours to move.</p>
  </header>

  <section class="readout">
    <div class="chip"><b id="rTime">17:12</b><s>harbour clock</s></div>
    <div class="chip"><b id="rTide">+0.31</b><s>tide, metres</s></div>
    <div class="chip"><b id="rWind">13 kt</b><s>west by north</s></div>
    <div class="chip hot"><b id="rSail">Full</b><s>canvas</s></div>
    <div class="chip"><b id="rBlk">0</b><s>blocks laid</s></div>
    <div class="chip"><b id="rFps">60</b><s>frames / s</s></div>
  </section>

  <aside class="ledger">
    <div class="phead"><span>Berth register</span><u id="regCount">—</u></div>
    <div class="rows" id="rows"></div>
  </aside>

  <aside class="notes">
    <div class="dossier empty" id="dossier">
      <button class="x" id="dClose">✕</button>
      <div class="sub" id="dTag"></div>
      <h2 id="dTitle"></h2>
      <p id="dBody"></p>
      <div class="specs" id="dSpecs"></div>
    </div>
    <div class="log">
      <div class="phead"><span>Harbour log</span><u>watch 3</u></div>
      <div class="logs" id="logs"></div>
    </div>
  </aside>

  <footer class="console">
    <div class="grp">
      <span class="lab">view</span>
      <button class="btn" data-view="overview">Overview</button>
      <button class="btn" data-view="quay">Quay</button>
      <button class="btn" data-view="deck">Deck</button>
      <button class="btn" data-view="light">Lighthouse</button>
      <button class="btn" data-view="chart">Chart</button>
    </div>
    <div class="grp">
      <div class="slide"><span class="lab">hour</span><input id="sHour" type="range" min="0" max="24" step="0.04" value="17.2"><b id="vHour">17:12</b></div>
      <div class="slide"><span class="lab">wind</span><input id="sWind" type="range" min="0" max="1.4" step="0.02" value="0.62"><b id="vWind">0.62</b></div>
      <button class="btn" id="bDrift">Drift time</button>
    </div>
    <div class="grp">
      <span class="lab">rig</span>
      <button class="btn" id="bSail">Canvas: full</button>
      <button class="btn on" id="bRig">Rigging</button>
      <button class="btn on" id="bSky">Sea &amp; sky</button>
      <button class="btn" id="bReset">Trim view</button>
      <button class="btn warn" id="bUI">Hide plate</button>
    </div>
    <div class="hint"><kbd>drag</kbd>orbit <kbd>wheel</kbd>zoom <kbd>1–9</kbd>landmark <kbd>D</kbd>deck <kbd>H</kbd>plate</div>
  </footer>
</div>

<div id="compass">
  <svg viewBox="-50 -50 100 100">
    <circle r="46" fill="rgba(6,11,19,.55)" stroke="rgba(231,186,109,.28)"/>
    <circle r="37" fill="none" stroke="rgba(231,186,109,.16)"/>
    <g font-family="IBM Plex Mono,monospace" font-size="9" fill="rgba(231,186,109,.75)" text-anchor="middle">
      <text y="-38">N</text><text x="39" y="3">E</text><text y="44">S</text><text x="-39" y="3">W</text>
    </g>
    <g class="needle" id="needle">
      <path d="M0,-30 L6,-4 L0,4 L-6,-4 Z" fill="#df6a45"/>
      <path d="M0,30 L6,4 L0,-4 L-6,4 Z" fill="rgba(238,244,248,.55)"/>
      <circle r="2.4" fill="#e7ba6d"/>
    </g>
  </svg>
</div>

<div id="tip"></div>
<div id="boot"><div class="sm">Harbour Authority</div><div class="big">Laying the blocks…</div><div class="bar"><i id="bootBar"></i></div></div>

<script type="importmap">
{ "imports": {
  "three": "https://cdn.jsdelivr.net/npm/three@0.160.1/build/three.module.js",
  "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.1/examples/jsm/"
}}
</script>
<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* ============================================================  CORE  */
const canvas = document.getElementById('scene');
const renderer = new THREE.WebGLRenderer({canvas, antialias:true, powerPreference:'high-performance'});
renderer.setPixelRatio(Math.min(devicePixelRatio, 1.75));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.08;
renderer.outputColorSpace = THREE.SRGBColorSpace;

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xdcc9a9, 62, 235);

const camera = new THREE.PerspectiveCamera(42, innerWidth/innerHeight, 0.4, 1200);
camera.position.set(-58, 33, 47);

const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true; controls.dampingFactor = 0.062;
controls.target.set(6, 4, -1);
controls.maxPolarAngle = Math.PI * 0.492;
controls.minDistance = 5; controls.maxDistance = 240;
controls.autoRotate = true; controls.autoRotateSpeed = 0.22;

const U = { time:{value:0}, wind:{value:0.62}, chop:{value:0.9}, night:{value:0} };

/* lights */
const hemi = new THREE.HemisphereLight(0xa9c6d8, 0x6a5742, 0.62); scene.add(hemi);
const sun  = new THREE.DirectionalLight(0xffc984, 2.3);
sun.castShadow = true; sun.shadow.mapSize.set(2048,2048);
sun.shadow.camera.left=-78; sun.shadow.camera.right=78; sun.shadow.camera.top=78; sun.shadow.camera.bottom=-78;
sun.shadow.camera.near=20; sun.shadow.camera.far=360; sun.shadow.bias=-0.0004; sun.shadow.normalBias=0.35;
scene.add(sun, sun.target);
const fill = new THREE.DirectionalLight(0x9fc7ff, 0.22); fill.position.set(-60,40,-90); scene.add(fill);
const lampA = new THREE.PointLight(0xffb35c, 0, 26, 2); lampA.position.set(21,6.4,-3); scene.add(lampA);
const lampB = new THREE.PointLight(0xffb35c, 0, 26, 2); lampB.position.set(21,6.4,7);  scene.add(lampB);
const lampC = new THREE.PointLight(0xff9a5a, 0, 22, 2); lampC.position.set(-6,6.2,-16); scene.add(lampC);

/* sky dome */
const skyMat = new THREE.ShaderMaterial({
  side:THREE.BackSide, depthWrite:false,
  uniforms:{ uTop:{value:new THREE.Color(0x3a6ea2)}, uHor:{value:new THREE.Color(0xf1c383)},
             uSun:{value:new THREE.Color(0xffc984)}, uSunDir:{value:new THREE.Vector3(0,-1,0)},
             uNight:{value:0}, uTime:{value:0} },
  vertexShader:`varying vec3 vD; void main(){ vD = normalize(position); gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.0);} `,
  fragmentShader:`
    varying vec3 vD; uniform vec3 uTop,uHor,uSun,uSunDir; uniform float uNight,uTime;
    float h31(vec3 p){ return fract(sin(dot(p,vec3(12.9898,78.233,45.164)))*43758.5453); }
    void main(){
      vec3 d = normalize(vD);
      float t = clamp(d.y,0.0,1.0);
      vec3 col = mix(uHor, uTop, pow(t,0.62));
      float sd = dot(d, normalize(uSunDir));
      col += uSun * pow(max(sd,0.0), 26.0) * 0.75;
      col += uSun * pow(max(sd,0.0), 4.0)  * 0.13;
      float disc = smoothstep(0.9955, 0.9982, sd);
      col = mix(col, uSun*1.9, disc*(1.0-uNight));
      vec3 mD = -normalize(uSunDir);
      float md = dot(d, mD);
      float mdisc = smoothstep(0.9955,0.9985,md)*uNight;
      col = mix(col, vec3(0.92,0.94,1.0)*1.4, mdisc);
      col += vec3(0.5,0.62,0.85)*pow(max(md,0.0),70.0)*0.3*uNight;
      float st = step(0.9982, h31(floor(d*230.0)));
      float tw = 0.55+0.45*sin(uTime*1.7+h31(floor(d*230.0))*30.0);
      col += vec3(st)*uNight*tw*(0.25+0.75*t);
      float band = smoothstep(0.22,0.0,t)*0.16;
      col += uHor*band*(1.0-uNight*0.7);
      gl_FragColor = vec4(col,1.0);
    }`
});
const sky = new THREE.Mesh(new THREE.SphereGeometry(420, 40, 20), skyMat);
sky.renderOrder = -10; scene.add(sky);

/* ============================================================  VOXEL HELPERS  */
function B(){ return {a:[]} }
function put(b,x,y,z,c,sx=1,sy=1,sz=1,ry=0){ b.a.push(x,y,z,sx,sy,sz,ry,c); }
function rnd(x,y,z){ const s=Math.sin(x*127.1+y*311.7+z*74.7)*43758.5453; return s-Math.floor(s); }
function sm(t){ return t*t*(3-2*t); }
function nz(x,z,s){ const fx=Math.floor(x/s),fz=Math.floor(z/s);
  const a=rnd(fx,0,fz),b=rnd(fx+1,0,fz),c=rnd(fx,0,fz+1),d=rnd(fx+1,0,fz+1);
  const u=sm(x/s-fx),v=sm(z/s-fz);
  return (a+(b-a)*u)*(1-v)+(c+(d-c)*u)*v; }
function mul(hex,f){ const c=new THREE.Color(hex); c.multiplyScalar(f); return c.getHex(); }
let BLOCKS = 0;
function build(b, mat, poi){
  const n = b.a.length/9; if(!n) return null;
  BLOCKS += n;
  const geo = new THREE.BoxGeometry(1,1,1);
  const m = new THREE.InstancedMesh(geo, mat, n);
  const d = new THREE.Object3D(), col = new THREE.Color();
  for(let i=0;i<n;i++){ const o=i*9;
    d.position.set(b.a[o],b.a[o+1],b.a[o+2]);
    d.scale.set(b.a[o+3],b.a[o+4],b.a[o+5]);
    d.rotation.set(0,b.a[o+6],0);
    d.updateMatrix(); m.setMatrixAt(i,d.matrix);
    col.setHex(b.a[o+7]>>>0); m.setColorAt(i,col);
  }
  m.instanceMatrix.needsUpdate=true; if(m.instanceColor) m.instanceColor.needsUpdate=true;
  m.castShadow = true; m.receiveShadow = true;
  m.computeBoundingBox(); m.computeBoundingSphere();
  if(poi) m.userData.poi = poi;
  return m;
}
/* a couple of loose meshes for animated bits */
const MB = {};
function mb(hex){ if(!MB[hex]) MB[hex]=new THREE.MeshLambertMaterial({color:hex,flatShading:true}); return MB[hex]; }
function box(parent,x,y,z,sx,sy,sz,hex,ry=0){
  const m = new THREE.Mesh(new THREE.BoxGeometry(sx,sy,sz), mb(hex));
  m.position.set(x,y,z); m.rotation.y=ry; m.castShadow=true; m.receiveShadow=true; parent.add(m); return m;
}

/* palette */
const C = {
  hull:0x252d38, hullD:0x1a2028, wale:0xe9e2d0, red:0x8c3326, deck:0x7a5733, deckD:0x5f4227,
  wood:0x6a4a2c, woodD:0x4a3222, woodL:0x8a6238, rope:0xc9b78f,
  sail:0xf2e8d2, sailB:0xd9ccb2,
  stone:0x8f8879, stoneD:0x6d675c, stoneL:0xa9a08d, cobble:0x7d7669, cobbleD:0x66605a,
  brick:0x94462f, brickD:0x793a28, brickL:0xa85a3c, slate:0x4c5462, slateD:0x3b4250,
  grass:0x6f8f57, grassD:0x5a7747, sand:0xc8b88b, sandW:0x9fb0a4,
  metal:0x8b939c, brass:0xd8a549, white:0xeef0ea, dark:0x2a3340, red2:0xc0392f,
  glass:0x2a3648, tar:0x2b2f33, awn:0xd0554b, awnW:0xefe6d6
};

/* ============================================================  TERRAIN  */
const QUAY_X = 18, QUAY_Z = -17;   // quay wall faces sit here; land starts behind them
const PADS = [
  {x0:20,x1:23,z0:-40,z1:22,h:2}, {x0:-36,x1:19,z0:-20,z1:-16,h:2},
  {x0:22,x1:31,z0:-12,z1:-4,h:3}, {x0:33,x1:42,z0:-11,z1:-3,h:3},
  {x0:22,x1:28,z0:5,z1:9,h:3},    {x0:33,x1:43,z0:4,z1:11,h:4},
  {x0:38,x1:45,z0:-26,z1:-20,h:6},{x0:19,x1:26,z0:12,z1:22,h:3},
  {x0:-20,x1:-2,z0:-30,z1:-22,h:3},{x0:4,x1:11,z0:-29,z1:-22,h:4},
  {x0:29,x1:33,z0:12,z1:16,h:3}
];
function hill(x,z,cx,cz,r,a){ const d=Math.hypot(x-cx,z-cz); if(d>r) return 0; const k=1-d/r; return a*k*k; }
function isLand(x,z){
  if(x>48 || x<-46 || z>36 || z<-42) return false;
  if(x>=20 && z<=22 && z>=-36) return true;
  if(z<=-20 && x>=-36 && x<=20) return true;
  if(Math.hypot(x+42,z-31) < 5) return true;           // outer islet
  if(Math.hypot(x+46,z-11) < 2.6) return true;         // beacon rock
  return false;
}
function terrH(x,z){
  for(const p of PADS) if(x>=p.x0&&x<=p.x1&&z>=p.z0&&z<=p.z1) return p.h;
  const d = Math.max(0, Math.max(x-20, -20-z));
  let h = 2 + Math.min(4.4, d*0.22) + (nz(x,z,10)-0.5)*2.3;
  h += hill(x,z,41,-22,10,3.4) + hill(x,z,44,7,7,2.2) + hill(x,z,-14,-30,11,2.4) + hill(x,z,36,17,6,1.6);
  if(x>=19 && z>=12) h = Math.max(h, 4 + hill(x,z,22,17,5,2.6));
  if(Math.hypot(x+42,z-31) < 5) h = 3 + hill(x,z,-42,31,4,2.2);
  if(Math.hypot(x+46,z-11) < 2.6) h = 3;
  return Math.max(2, Math.min(11, Math.round(h)));
}
const blocked = [ // circles where water cells must not intrude
  {x:13.2,z:-1,r:7.6}, {x:-12,z:10,r:4.2}, {x:-6,z:18,r:4.2}, {x:-20,z:4,r:4.2}, {x:9,z:-13,r:3.4}
];

const landB = B(), wallB = B();
for(let x=-46;x<=48;x++) for(let z=-42;z<=36;z++){
  if(!isLand(x,z)) continue;
  const h = terrH(x,z);
  const quayEdge = (x<=24 && z>=-40 && z<=22) || (z<=-18 && x>=-36 && x<=20);
  const wet = h<=2;
  for(let y=h; y>=h-2; y--){
    let c;
    if(y===h){
      if(wet && quayEdge) c = [C.cobble, C.cobbleD, C.stoneL, C.sand][(rnd(x,y,z)*4)|0];
      else if(wet) c = [C.sand, C.sandW, C.stone][(rnd(x,y,z)*3)|0];
      else if(quayEdge) c = [C.cobble, C.cobbleD, C.stoneL][(rnd(x,y,z)*3)|0];
      else c = [C.grass, C.grassD, C.grass, C.stoneL][(rnd(x,y,z)*4)|0];
      if(h>=8) c = [C.stone, C.stoneD, C.grassD][(rnd(x,y,z)*3)|0];
    } else if(y<=1) c = [C.sand, C.stoneD, C.sandW][(rnd(x,y+3,z)*3)|0];
    else c = [C.stone, C.stoneD, C.stoneL][(rnd(x+7,y,z)*3)|0];
    put(landB,x,y,z,c);
  }
}
/* quay walls: granite plinth from the seabed up to the apron */
for(let z=-20;z<=22;z++){ for(let y=-4;y<=2;y++){ for(const x of [18,19])
  put(wallB,x,y,z, y<0 ? [C.stoneD,C.sandW,C.stone][(rnd(x,y,z)*3)|0] : [C.stone,C.stoneL,C.stoneD][(rnd(x,y,z)*3)|0]); } }
for(let x=-36;x<=18;x++){ for(let y=-4;y<=2;y++){ for(const z of [-17,-18])
  put(wallB,x,y,z, y<0 ? [C.stoneD,C.sandW,C.stone][(rnd(x,y,z)*3)|0] : [C.stone,C.stoneL,C.stoneD][(rnd(x,y,z)*3)|0]); } }
/* cap the landmass so nothing see-through */
const slabMat = new THREE.MeshLambertMaterial({color:0x4c4a44, flatShading:true});
function slab(x0,x1,z0,z1){
  const w=x1-x0+1, d=z1-z0+1;
  const m=new THREE.Mesh(new THREE.BoxGeometry(w,9,d), slabMat);
  m.position.set((x0+x1)/2, -4.1, (z0+z1)/2); m.receiveShadow=true; scene.add(m);
}
slab(20,49,-36,22); slab(-36,19,-42,-20); slab(-47,-38,26,36);

/* land mesh */
const landMesh = build(landB, new THREE.MeshLambertMaterial({flatShading:true}), 'quay');
scene.add(landMesh);
const wallMesh = build(wallB, new THREE.MeshLambertMaterial({flatShading:true}), 'quay');
scene.add(wallMesh);

/* ============================================================  BUILDINGS  */
const bldgB = B(), winB = B();
function house(b,w,x0,z0,d,h,wallC,roofC,o={}){
  const base = terrH(x0,z0);
  /* plinth */
  for(let x=x0;x<x0+w;x++) for(let z=z0;z<z0+d;z++) put(b,x,base-1,z,C.stoneD);
  /* walls */
  for(let y=base;y<base+h;y++) for(let x=x0;x<x0+w;x++) for(let z=z0;z<z0+d;z++){
    const edge = (x===x0||x===x0+w-1||z===z0||z===z0+d-1);
    if(!edge) continue;
    put(b,x,y,z, [wallC,C.brickD,wallC,C.brickL][(rnd(x,y,z)*4)|0]);
  }
  /* stepped gable roof, ridge along x */
  const steps = Math.ceil(d/2);
  for(let r=0;r<steps;r++){
    const y = base+h+r;
    for(let x=x0-1;x<x0+w+1;x++) for(let z=z0+r;z<z0+d-r;z++)
      put(b,x,y,z, [roofC,roofC,C.slateD][(rnd(x,y,z)*3)|0]);
  }
  if(o.gable){ // white gable ends
    for(let r=0;r<steps;r++) for(let y=0;y<2;y++){
      put(b, x0+(o.gable==='w'?0:w-1), base+h-2+y, z0+r, C.white);
      put(b, x0+(o.gable==='w'?0:w-1), base+h-2+y, z0+d-1-r, C.white);
    }
  }
  /* windows on the harbour-facing side + street side */
  for(let i=0;i<Math.floor(w/2);i++){
    const x = x0+1+i*2;
    for(let s=0;s<Math.max(1,Math.floor(h/3));s++){
      const y = base+2+s*2; if(y>=base+h) break;
      put(winB, x, y, z0-0.62, 1, 0.9, 0.35, 0);
      put(winB, x, y, z0+d+0.62, 1, 0.9, 0.35, 0);
    }
  }
  for(let i=0;i<Math.floor(d/2);i++){
    const z = z0+1+i*2;
    put(winB, x0-0.62, base+2, z, 0.35, 0.9, 1, 0);
    put(winB, x0+w-0.38, base+2, z, 0.35, 0.9, 1, 0);
  }
  /* door */
  put(b, x0+1, base, z0-0.55, 1.1, 1.6, 0.4, 0, C.woodD);
  /* chimney */
  if(o.chimney){ const cx=o.chimney[0], cz=o.chimney[1];
    for(let y=base+h;y<base+h+4;y++) put(b,cx,y,cz, [C.brickD,C.brick][(rnd(cx,y,cz)*2)|0]);
    for(let y=base+h+2;y<base+h+4;y++) put(b,cx,y,cz, C.brickL, 1.4,1,1.4);
  }
  return base;
}
/* bonded warehouses */
house(bldgB,10,22,-12,9,4,C.brick,C.slate,{chimney:[24,-11]});
house(bldgB,10,33,-11,9,5,C.brick,C.slate,{chimney:[41,-10],gable:'w'});
house(bldgB,7,22,5,5,3,C.brickL,C.slateD,{});
/* chandlery awning over the water */
for(let x=21;x<29;x++) put(bldgB,x,4,4, (x%4<2?C.awn:C.awnW), 1,0.35,2.6);
for(let x=22;x<28;x+=3) put(bldgB,x,3,4, C.woodD, 0.35,1.6,0.35);
/* custom house: white stone, colonnade, pediment, flagpole */
(function(){
  const x0=33,z0=4,w=11,d=8,base=4;
  for(let y=base;y<base+5;y++) for(let x=x0;x<x0+w;x++) for(let z=z0;z<z0+d;z++){
    const edge=(x===x0||x===x0+w-1||z===z0||z===z0+d-1); if(!edge) continue;
    put(bldgB,x,y,z,[0xe9e4d6,0xd8d2c2,0xf0ece2][(rnd(x,y,z)*3)|0]);
  }
  for(let i=0;i<5;i++) put(bldgB,x0+1+i*2,base+1,z0-1.2,0.9,3.2,0.9,0,0xf2eee2);
  for(let r=0;r<3;r++) for(let x=x0-1;x<x0+w+1;x++) for(let z=z0+r;z<z0+d-r;z++)
    put(bldgB,x,base+5+r,z,[C.slate,C.slateD,0x5a6374][(rnd(x,y2(z),z)*3)|0]);
  for(let x=x0;x<x0+w;x++) put(bldgB,x,base+8,z0+3,0xe9e4d6,1,0.4,3);
  for(let i=0;i<Math.floor(d/2);i++) put(winB,x0+w-0.38,base+3,z0+1+i*2,0.35,1.2,1,0);
  for(let i=0;i<4;i++) put(winB,x0+2+i*2,base+3,z0-0.62,1,1.3,0.4,0);
  for(let y=base+9;y<base+15;y++) put(bldgB,x0+w-2,y,z0+1,C.woodD,0.28,1,0.28);
  put(bldgB,x0+w-2,base+15,z0+1,C.red2,1.6,0.9,0.2,0);
})();
/* chapel with tower on the north quay */
(function(){
  const x0=4,z0=-29,w=7,d=6,base=4;
  for(let y=base;y<base+4;y++) for(let x=x0;x<x0+w;x++) for(let z=z0;z<z0+d;z++){
    const edge=(x===x0||x===x0+w-1||z===z0||z===z0+d-1); if(!edge) continue;
    put(bldgB,x,y,z,[C.stoneL,C.stone,C.stoneD][(rnd(x,y,z)*3)|0]);
  }
  for(let r=0;r<3;r++) for(let x=x0-1;x<x0+w+1;x++) for(let z=z0+r;z<z0+d-r;z++) put(bldgB,x,base+4+r,z,C.slateD);
  for(let y=base;y<base+9;y++) for(let x=7;x<10;x++) for(let z=-27;z<=-25;z++) put(bldgB,x,y,z,[C.stone,C.stoneL][(rnd(x,y,z)*2)|0]);
  for(let r=0;r<3;r++) for(let x=6+r;x<11-r;x++) for(let z=-28+r;z<=-24+r;z++) put(bldgB,x,base+9+r,z,C.slate);
  put(bldgB,8,base+12,-26,C.stoneL,1.6,2,1.6);
  put(bldgB,8,base+14,-26,C.slateD,0.6,2,0.6);
  for(const z of [-28,-22]) for(let i=0;i<3;i++) put(winB,x0+1+i*2,base+2,z-0.6,1,1.4,0.35,0);
})();
/* north-quay cooperage sheds */
for(const s of [[-20,-30,6,3],[-12,-30,7,3],[-26,-27,5,2]]){
  const [x0,z0,w,d]=s, base=terrH(x0,z0);
  for(let y=base;y<base+2;y++) for(let x=x0;x<x0+w;x++) for(let z=z0;z<z0+d;z++){
    const edge=(x===x0||x===x0+w-1||z===z0||z===z0+d-1); if(!edge) continue;
    put(bldgB,x,y,z,[C.wood,C.woodD,C.woodL][(rnd(x,y,z)*3)|0]);
  }
  for(let r=0;r<2;r++) for(let x=x0-1;x<x0+w+1;x++) for(let z=z0+r;z<z0+d-r;z++) put(bldgB,x,base+2+r,z,[C.slate,C.woodD][(rnd(x,y2(z),z)*2)|0]);
}
/* helper used above only to vary roof tint */
function y2(z){ return Math.floor(rnd(z,3,1)*7); }
/* drift mill on the hill */
let millHub = null;
(function(){
  const cx=41, cz=-22, base=6;
  for(let y=base;y<base+7;y++){ const r = 3 - (y-base)*0.32;
    for(let x=Math.ceil(cx-r);x<=Math.floor(cx+r);x++) for(let z=Math.ceil(cz-r);z<=Math.floor(cz+r);z++){
      if(Math.hypot(x-cx,z-cz)>r+0.2) continue;
      put(bldgB,x,y,z,[C.stone,C.stoneD,C.brick][(rnd(x,y,z)*3)|0]);
    } }
  for(let r=0;r<2;r++) for(let x=cx-4+r;x<=cx+4-r;x++) for(let z=cz-4+r;z<=cz+4-r;z++) put(bldgB,x,base+7+r,z,C.slateD);
  put(winB,cx-3,base+2,cz-3,1,1,0.4,0);
  const g = new THREE.Group(); g.position.set(cx, base+8.4, cz-3.2); scene.add(g);
  const cap = new THREE.Group(); g.add(cap);
  box(cap,0,0,0,4,2,3.4,C.slateD); box(cap,0,1.3,0,3,1,2.6,C.woodD);
  const hub = new THREE.Group(); hub.position.set(0,0.4,-1.9); cap.add(hub);
  box(hub,0,0,0,0.9,0.9,0.9,C.brass);
  for(let i=0;i<4;i++){
    const arm = new THREE.Group(); arm.rotation.x = i*Math.PI/2; hub.add(arm);
    box(arm,0,3.1,0,0.34,6,0.34,C.woodD);
    box(arm,0.9,3.1,0,1.5,5.4,0.22,0xf0e6d0);
  }
  millHub = hub;
})();
/* keeper's cottage + boat house on the headland */
house(bldgB,4,20,12,3,2,C.stoneL,C.slate,{});
house(bldgB,4,29,12,5,2,C.wood,C.slateD,{});
const bldgMesh = build(bldgB, new THREE.MeshLambertMaterial({flatShading:true}), 'warehouse');
scene.add(bldgMesh);

/* window glow */
const glowMat = new THREE.MeshBasicMaterial({color:new THREE.Color(C.glass)});
const winMesh = (()=>{ const m=build(winB, glowMat); if(m){ m.castShadow=false; m.receiveShadow=false; } return m; })();
scene.add(winMesh);

/* ============================================================  QUAY FURNITURE  */
const propB = B();
/* bollards along the east quay, mooring to the ship */
for(let z=-13;z<=15;z+=3){ put(propB,20,2.9,z, C.stoneD,0.8,1.4,0.8); put(propB,20,3.6,z, C.brass,0.9,0.3,0.9); }
for(let z=-30;z<=-22;z+=4){ put(propB,20,2.9,z, C.stoneD,0.8,1.4,0.8); }
/* lamp posts */
const lampPos = [[21,-11],[21,-3],[21,3],[21,9],[-10,-16],[3,-16],[13,-16]];
const lampHeadB = B();
for(const [x,z] of lampPos){
  for(let y=3;y<7;y++) put(propB,x,y,z,C.woodD,0.4,1,0.4);
  put(propB,x,7,z,C.metal,1.3,0.3,1.3);
  put(lampHeadB,x,7.5,z, 0xffcf7a, 0.9,0.9,0.9);
  put(propB,x,8.1,z,C.slateD,1.1,0.35,1.1);
}
/* crates, barrels, coiled rope, fish baskets, timber stacks */
for(let i=0;i<46;i++){
  const x = 21 + (rnd(i,1,2)*2.4|0), z = -13 + (rnd(i,3,4)*26|0), base=3;
  const k = rnd(i,5,6);
  if(k<0.34) put(propB,x,base,z, [C.wood,C.woodL,C.woodD][(rnd(i,7,8)*3)|0], 1.3,1.2,1.3, rnd(i,9,0)*0.6);
  else if(k<0.6) { put(propB,x,base,z, C.woodD, 1.0,1.1,1.0); put(propB,x,base+0.6,z, C.brass, 1.15,0.16,1.15); }
  else if(k<0.8) put(propB,x,base,z, C.rope, 1.4,0.5,1.4, rnd(i,1,9)*0.9);
  else put(propB,x,base,z, C.stoneL, 1.1,0.7,1.1);
}
for(let i=0;i<12;i++){ const x=35+(rnd(i,2,3)*8|0), z=-24+(rnd(i,4,5)*10|0), base=terrH(x,z)+1;
  for(let s=0;s<3;s++) put(propB,x,base+s,z-0.6+s*0.5, C.woodD, 0.4,0.8,3.2); }
/* market stalls on the north quay */
for(let i=0;i<4;i++){ const x=-19+i*5, z=-19, base=3;
  for(let y=base;y<base+2;y++) put(propB,x,y,z, C.woodD, 0.35,1,0.35);
  put(propB,x+1.5,base+2.1,z, (i%2?C.awn:C.awnW), 3.2,0.3,2.2);
  put(propB,x+1,base+1,z, C.sandW, 1.4,0.5,1.2);
}
/* steps down to the water at the north slip */
for(let i=0;i<5;i++) put(propB,10-i*0.0,2-i,-15+i, C.stone, 2.4,1,1);
/* cart on the wharf */
(function(){ const x=23,z=-7,base=3;
  put(propB,x,base+1,z,C.woodL,3.4,0.7,1.8);
  put(propB,x,base+1.6,z+0.85,C.woodD,3.6,0.3,0.3); put(propB,x,base+1.6,z-0.85,C.woodD,3.6,0.3,0.3);
  for(const dx of [-1.3,1.3]){ put(propB,x+dx,base+0.35,z+0.95,C.woodD,0.3,1.1,1.1); put(propB,x+dx,base+0.35,z-0.95,C.woodD,0.3,1.1,1.1); }
  put(propB,x+2.1,base+1.2,z,C.woodD,0.35,0.35,1.6);
})();
const propMesh = build(propB, new THREE.MeshLambertMaterial({flatShading:true}), 'quay');
scene.add(propMesh);

/* ============================================================  BREAKWATER + LIGHT  */
const bwB = B(), lightB = B();
for(let i=0;i<30;i++){
  const cx = 18 - i*0.95, cz = 21 + i*0.22;
  for(let x=Math.floor(cx-2);x<=Math.ceil(cx+2);x++) for(let z=Math.floor(cz-1.6);z<=Math.ceil(cz+1.6);z++){
    for(let y=-5;y<=1;y++) put(bwB,x,y,z,[C.stoneD,C.stone,C.sandW][(rnd(x,y,z)*3)|0]);
    if(rnd(x,i,7)>0.72) put(bwB,x,2,z,[C.stone,C.stoneL][(rnd(x,y2(z),z)*2)|0]);
  }
}
for(let i=0;i<3;i++) put(bwB, 6-i*8, 3.2, 22+ (i*0.0), C.red2, 0.5,2.2,0.5);
/* light: rocky plinth, banded tower, gallery, lantern */
(function(){
  const cx=22, cz=18;
  for(let x=19;x<=25;x++) for(let z=15;z<=21;z++){ const h=terrH(x,z); for(let y=4;y<=h;y++) put(lightB,x,y,z,[C.stoneD,C.stone][(rnd(x,y,z)*2)|0]); }
  const base=4;
  for(let y=base;y<base+11;y++){ const r = 2.6 - (y-base)*0.14;
    for(let x=Math.ceil(cx-r);x<=Math.floor(cx+r);x++) for(let z=Math.ceil(cz-r);z<=Math.floor(cz+r);z++){
      if(Math.hypot(x-cx,z-cz)>r+0.15) continue;
      const band = (y>=base+7 && y<=base+8) ? C.red2 : [0xf2efe6,0xe4e0d4,0xf6f3ea][(rnd(x,y,z)*3)|0];
      put(lightB,x,y,z,band);
    } }
  for(let x=cx-3;x<=cx+3;x++) for(let z=cz-3;z<=cz+3;z++) put(lightB,x,base+11,z,C.metal,1,0.3,1);
  for(let i=0;i<12;i++){ const a=i/12*Math.PI*2; put(lightB, Math.round(cx+Math.cos(a)*3),base+11.8,Math.round(cz+Math.sin(a)*3),C.slateD,0.35,0.9,0.35); }
  for(let y=base+12;y<base+14;y++) for(let x=cx-2;x<=cx+2;x++) for(let z=cz-2;z<=cz+2;z++)
    if(Math.hypot(x-cx,z-cz)<=2.3) put(lightB,x,y,z,C.slateD,1,1,1);
  put(lightB,cx,base+14,cz,0xfff3c0,3,1.4,3);
  put(lightB,cx,base+15.4,cz,C.slate,3.4,0.4,3.4);
  put(bwB,cx,base+16,cz,C.brass,1,1.6,1);
})();
const bwMesh = build(bwB, new THREE.MeshLambertMaterial({flatShading:true}), 'break');
const lightMesh = build(lightB, new THREE.MeshLambertMaterial({flatShading:true}), 'light');
scene.add(bwMesh, lightMesh);

/* rotating beacon + lamps */
const beaconG = new THREE.Group(); beaconG.position.set(22, 15.6, 18); scene.add(beaconG);
const beamMat = new THREE.MeshBasicMaterial({color:0xfff0bf, transparent:true, opacity:0,
  blending:THREE.AdditiveBlending, depthWrite:false, side:THREE.DoubleSide});
const beamTex = (()=>{ const c=document.createElement('canvas'); c.width=128; c.height=8; const g=c.getContext('2d');
  const grd=g.createLinearGradient(0,0,128,0); grd.addColorStop(0,'rgba(255,244,200,.95)'); grd.addColorStop(.55,'rgba(255,230,170,.25)'); grd.addColorStop(1,'rgba(255,220,150,0)');
  g.fillStyle=grd; g.fillRect(0,0,128,8); const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; return t; })();
const beamMat2 = beamMat.clone(); beamMat2.map = beamTex; beamMat2.opacity = 0;
for(const ang of [0, Math.PI]){
  const p = new THREE.Mesh(new THREE.PlaneGeometry(120, 7), beamMat2);
  p.position.set(60,0,0); p.rotation.z = -0.05; p.rotation.y = 0;
  const pivot = new THREE.Group(); pivot.rotation.y = ang; pivot.add(p); beaconG.add(pivot);
}
const beaconLight = new THREE.SpotLight(0xfff0c0, 0, 170, 0.32, 0.7, 1.2);
beaconLight.position.set(0,0,0);
const bTarget = new THREE.Object3D(); bTarget.position.set(70,-3,0); beaconG.add(bTarget); beaconLight.target = bTarget;
scene.add(beaconLight);

/* glow sprites for lamps + windows at night */
const glowTex = (()=>{ const c=document.createElement('canvas'); c.width=c.height=64; const g=c.getContext('2d');
  const grd=g.createRadialGradient(32,32,0,32,32,32); grd.addColorStop(0,'rgba(255,225,160,.95)');
  grd.addColorStop(.35,'rgba(255,190,110,.4)'); grd.addColorStop(1,'rgba(255,170,90,0)');
  g.fillStyle=grd; g.fillRect(0,0,64,64); const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; return t; })();
const spriteMat = new THREE.SpriteMaterial({map:glowTex, transparent:true, opacity:0, blending:THREE.AdditiveBlending, depthWrite:false});
const lampHeads = [];
for(const [x,z] of lampPos){
  const s = new THREE.Sprite(spriteMat.clone()); s.position.set(x,7.5,z); s.scale.set(4.2,4.2,1); scene.add(s); lampHeads.push(s);
}
const beaconSprite = new THREE.Sprite(spriteMat.clone()); beaconSprite.position.set(22,15.6,18); beaconSprite.scale.set(9,9,1); scene.add(beaconSprite);

/* ============================================================  THE BRIG  */
const ship = new THREE.Group(); ship.position.set(13.2, 0, -1); ship.rotation.y = -0.05; scene.add(ship);
const hullB = B(), shipGlassB = B();
function halfW(z){
  if(z > 4) return Math.max(0.35, 3.6 - (z-4)*0.62);
  if(z < -6) return Math.max(0.5, 3.4 - (-6-z)*0.44);
  return 3.6;
}
function deckY(z){ return 2 + (Math.abs(z)>6 ? (Math.abs(z)-6)*0.13 : 0); }
for(let z=-10; z<=10; z++){
  const hw = halfW(z), dy = deckY(z);
  for(let x=Math.ceil(-hw); x<=Math.floor(hw); x++){
    for(let y=-2; y<=Math.round(dy); y++){
      let c;
      if(y<0) c = [C.red,0x6f2a20,C.red][(rnd(x,y,z)*3)|0];
      else if(y===1) c = C.wale;
      else c = [C.hull,C.hullD,C.hull][(rnd(x,y,z)*3)|0];
      if(Math.abs(x)>=hw-0.15 && y>=0) c = y===Math.round(dy) ? C.woodD : c;
      put(hullB,x,y,z,c);
    }
    /* bulwark cap */
    if(Math.abs(x)>=hw-0.2) put(hullB,x,Math.round(dy)+1,z,C.wood,0.9,0.9,0.9);
  }
  /* portholes */
  if(z>-8 && z<3 && z%2===0){ put(hullB, Math.round(hw), 1, z, C.brass, 0.35,0.9,0.9); put(shipGlassB, Math.round(hw)+0.2, 1, z, 0xffcf7a, 0.5,0.7,0.2,0); }
}
/* stern cabin + transom lights */
for(let z=-10;z<=-6;z++) for(let x=-2;x<=2;x++){ for(let y=3;y<=4;y++) put(hullB,x,y,z,C.woodL); }
put(shipGlassB,0,3.6,-10.2,3.2,1.2,0.3,0,0xffcf7a);
put(hullB,0,5,-8,C.woodD,0.3,1.4,0.3); put(hullB,0,5.9,-8,C.wale,1.6,0.35,0.2,0);
/* forecastle, hatches, barrels, anchor, wheel */
for(let z=6;z<=9;z++) for(let x=-2;x<=2;x++) put(hullB,x,3,z,C.deckD);
for(const z of [1,-3,4]) put(hullB,0,2.4,z,C.deckD,2.6,0.4,1.6);
for(const z of [-1.5,7]) for(const x of [-2.6,2.6]) put(hullB,x,2.6,z,C.woodD,0.9,1,0.9);
put(hullB,-2.6,3.3,7,C.wood,1.1,0.16,1.1);
put(hullB,2.6,3.3,9.4,C.metal,1.2,0.8,1.2);           // capstan
put(hullB,3,2.6,10.2,C.metal,1.6,0.5,0.7);            // anchor stowed
/* bowsprit */
for(let i=0;i<7;i++) put(hullB, Math.round(i*0.2), 3+Math.round(i*0.35), 11+i, i%3?C.woodD:C.wood, 0.5,0.5,1.2);
put(hullB,0,2.8,10.4,C.woodL,0.9,1.3,1.4);            // figurehead
put(hullB,0,2.4,11.4,C.brass,0.7,0.8,0.8);
/* gangplank ashore */
for(let i=0;i<6;i++) put(hullB, 4+i, 2.4 - i*0.06, -1 + (i%2?0.2:-0.2), C.woodL, 1,0.3,1.2);
/* crew on deck */
const crew = [[-1,3,4],[2,3,-4],[0,3.2,7],[-2.4,3,-8],[1.6,3.4,2.5],[0.4,4,-9.6]];
for(const [x,y,z] of crew){
  put(hullB,x,y,z, [0x2f4a63,0x7a4a3a,0x3b5568,0x8a6a48][(rnd(x,z,1)*4)|0], 0.42,1.1,0.34, rnd(x,z,2)*6);
  put(hullB,x,y+1.2,z, [0xe6cfa8,0xd9b78e][(rnd(x,z,3)*2)|0], 0.34,0.4,0.3, rnd(x,z,2)*6);
  if(rnd(x,z,4)>0.5) put(hullB,x,y+1.45,z, [0x26333f,0xd8c9a0][(rnd(x,z,5)*2)|0], 0.5,0.18,0.5, rnd(x,z,2)*6);
}
/* masts + yards */
const masts = [{z:6,h:15},{z:-1,h:18.4},{z:-7,h:13}];
for(const m of masts){
  for(let y=2;y<=m.h;y++) put(hullB, 0, y, m.z, [C.woodD,C.wood][(rnd(0,y,m.z)*2)|0], 0.42,1,0.42);
  put(hullB,0,m.h+0.6,m.z,C.brass,0.5,0.9,0.5);
  for(const yy of [Math.round(m.h*0.55), Math.round(m.h*0.78)]){ put(hullB,0,yy,m.z,C.woodD,2.2,0.28,0.28); }
}
const yards = [
  {x:0,y:7.2,z:6,w:8.6,t:'fore1'}, {x:0,y:11.2,z:6,w:6.6,t:'fore2'}, {x:0,y:14.2,z:6,w:4.6,t:'fore3'},
  {x:0,y:7.6,z:-1,w:9.8,t:'main1'},{x:0,y:11.6,z:-1,w:7.6,t:'main2'},{x:0,y:15.2,z:-1,w:5.2,t:'main3'},
  {x:0,y:7.4,z:-7,w:4.2,t:'mizzen'}
];
for(const yd of yards){ put(hullB,yd.x,yd.y,yd.z,C.woodD,yd.w+1.2,0.32,0.32); }
/* gaff for the mizzen */
for(let i=0;i<4;i++) put(hullB,0,7.8+i*0.5,-7.5+i,C.woodD,0.3,0.3,1.1,i===0?0:0.0);
const furlB = B();
for(const yd of yards) put(furlB, yd.x, yd.y-0.55, yd.z, C.sailB, yd.w,0.55,0.8);
const hullMat = new THREE.MeshLambertMaterial({flatShading:true});
const hullMesh = build(hullB, hullMat, 'ship'); ship.add(hullMesh);
const shipGlassMesh = build(shipGlassB, glowMat, 'ship'); if(shipGlassMesh){ shipGlassMesh.castShadow=false; ship.add(shipGlassMesh); }
const furlMesh = build(furlB, new THREE.MeshLambertMaterial({color:C.sailB,flatShading:true})); ship.add(furlMesh);

/* sails: instanced panels with a cloth shader */
function sailPanel(w,h,rows,cols,hexA,hexB,tri=false){
  const b = B(), cw=w/cols, ch=h/rows;
  for(let r=0;r<rows;r++) for(let c=0;c<cols;c++){
    const v = (c+0.5)/cols, u=(r+0.5)/rows;
    const half = tri ? 0.25+0.6*v : 0.5;                       // taper for jibs
    if(Math.abs(v-0.5) > half) continue;
    if(u>0.9 && Math.abs(v-0.5)>0.36) continue;                 // rounded top corners
    if(u<0.1 && Math.abs(v-0.5)>0.42) continue;
    put(b, (c+0.5)/cols*w - w/2, (r+0.5)/rows*h - h/2, 0, ((r%2===0)?hexA:hexB), cw*0.96, ch*0.96, 0.34);
  }
  return b;
}
function clothMat(w,h,{flutter=1}={}){
  const m = new THREE.MeshLambertMaterial({color:0xffffff, flatShading:true});
  m.customProgramCacheKey = ()=> 'cloth'+h+w+flutter;
  m.onBeforeCompile = sh => {
    sh.uniforms.uTime = U.time; sh.uniforms.uWind = U.wind;
    sh.uniforms.uH = {value:h}; sh.uniforms.uW = {value:w}; sh.uniforms.uFlut = {value:flutter};
    sh.vertexShader = sh.vertexShader
      .replace('#include <common>', '#include <common>\nuniform float uTime,uWind,uH,uW,uFlut;')
      .replace('#include <begin_vertex>', `
        #include <begin_vertex>
        float u = clamp((position.y/uH + 0.5), 0.0, 1.0);
        float v = clamp((position.x/uW + 0.5), 0.0, 1.0);
        float belly = sin(u*PI)*0.5 + (1.0-u)*0.32;
        float edge  = 0.42 + 0.58*sin(v*PI);
        float wob = sin(uTime*2.1 + position.x*0.85 + position.y*0.5)*0.09
                  + sin(uTime*3.9 + v*7.0)*0.055;
        transformed.z += (belly*edge*0.62 + wob*(1.0-u)*uFlut) * uWind * uH * 0.55;
        transformed.y -= (1.0-u)*0.22*uWind;
      `);
  };
  return m;
}
const sails = [];
for(const yd of yards){
  const h = yd.t==='mizzen' ? 3.2 : Math.min(5.2, yd.w*0.55);
  const b = sailPanel(yd.w, h, Math.max(4, Math.round(h)), Math.max(5, Math.round(yd.w*1.1)), C.sail, C.sailB);
  const mat = clothMat(yd.w, h);
  const m = build(b, mat);
  if(!m) continue;
  m.position.set(yd.x, yd.y - h/2, yd.z + 0.35);
  if(yd.t==='mizzen') m.rotation.y = Math.PI/2;
  m.castShadow = true; m.receiveShadow = true;
  m.userData = {yard:yd.y, h, mat};
  ship.add(m); sails.push(m);
}
/* jibs: triangle panels forward */
for(const [w,h,y0,z0] of [[3.4,7.2,3.2,10.6],[2.6,5.4,4.4,9.0]]){
  const b = sailPanel(w,h,7,7,C.sail,C.sailB,true);
  const mat = clothMat(w,h,{flutter:1.4});
  const m = build(b, mat); m.position.set(0, y0 + h/2, z0 - h*0.2);
  m.castShadow = true; m.userData = {yard:y0, h, mat}; ship.add(m); sails.push(m);
}
/* rigging */
const rigPts = [];
const R = (a,b)=>{ rigPts.push(a.x,a.y,a.z,b.x,b.y,b.z); };
for(const m of masts){
  const top = m.h+0.6;
  for(const zz of [m.z-3.2, m.z+3.2]) for(const xx of [-3.1,3.1]) R(new THREE.Vector3(xx,2.6,m.z+0.4), new THREE.Vector3(xx*0.55,top-1.4,m.z));
  R(new THREE.Vector3(0,top,0), new THREE.Vector3(0,2.6, m.z+ (m.z>0?-8:8)));
}
for(const yd of yards){
  for(const s of [-1,1]){
    const tip = new THREE.Vector3(s*(yd.w/2+0.6), yd.y, yd.z);
    const next = masts.find(mm=>Math.abs(mm.z-yd.z)<1);
    R(tip, new THREE.Vector3(s*2.2, 2.6, yd.z + (yd.t==='main1'?4:-4)));
    R(tip, new THREE.Vector3(0, next.h, next.z));
    if(yd.t.endsWith('1')) R(tip, new THREE.Vector3(s*(yd.w/2), yd.y - 4.4, yd.z+2.4));
  }
}
R(new THREE.Vector3(0,15.2,-1), new THREE.Vector3(0,11,6));
R(new THREE.Vector3(0,11,6), new THREE.Vector3(6,4.4,10.8));
R(new THREE.Vector3(0,7.6,-1), new THREE.Vector3(-3,2.6,-6));
const rigGeo = new THREE.BufferGeometry();
rigGeo.setAttribute('position', new THREE.Float32BufferAttribute(rigPts,3));
const rigMesh = new THREE.LineSegments(rigGeo, new THREE.LineBasicMaterial({color:0xc9b78f, transparent:true, opacity:0.72}));
rigMesh.userData.poi = 'ship'; ship.add(rigMesh);

/* flags */
function flag(parent,x,y,z,w,h,hex,ry){
  const b=B(); const cols=Math.round(w*2), rows=Math.round(h*2);
  for(let i=0;i<cols;i++) for(let j=0;j<rows;j++){
    const c = (i%4===0||j%4===0)? C.wale : hex;
    put(b,(i+0.5)/cols*w-w/2,(j+0.5)/rows*h-h/2,0,c,w/cols*0.95,h/rows*0.95,0.22);
  }
  const m=build(b, clothMat(w,h,{flutter:2.4})); m.position.set(x,y,z); m.rotation.y=ry; parent.add(m); return m;
}
const ensign = flag(ship, 1.6, 5.6, -9.6, 3.2, 2, 0xc0392f, 0);
const pennant = flag(ship, 0, 19.2, -1, 2.6, 0.9, 0x2f6f8f, 0);
const jack = flag(ship, 0.2, 4.9, 11.6, 2, 1.2, 0x2f4a63, 0);

/* ============================================================  SMALL CRAFT  */
function sloop(x,z,ry,hex){
  const b=B();
  for(let z2=-3;z2<=3;z2++){ const w = Math.max(0.4, 1.5 - Math.abs(z2)*0.22);
    for(let xx=Math.ceil(-w);xx<=Math.floor(w);xx++) for(let y=-1;y<=1;y++)
      put(b,xx,y,z2, [hex,C.woodD][(rnd(xx,y,z2)*2)|0]);
  }
  for(let z2=-2;z2<=2;z2++) put(b,0,1.6,z2,C.deckD,1.2,0.3,1);
  for(let y=2;y<=7;y++) put(b,0,y,0.4,C.woodD,0.3,1,0.3);
  put(b,0,6.4,0.4,C.sailB,3.4,0.5,0.6);
  for(const z2 of [-2,2]) for(const xx of [-1.2,1.2]) put(b,xx,1.2,z2,C.woodL,0.7,0.6,0.7);
  put(b,0,7.4,0.4,C.red2,1,0.4,0.2);
  const g = new THREE.Group(); g.position.set(x,0,z); g.rotation.y=ry; scene.add(g);
  const m = build(b, new THREE.MeshLambertMaterial({flatShading:true}), 'fleet'); m.userData.poi='fleet'; g.add(m);
  return g;
}
const sloops = [ sloop(-12,10,0.35,C.woodL), sloop(-6,18,-0.6,0x8a6238), sloop(-20,4,0.15,0x6f5236), sloop(9,-13,0.9,C.woodD) ];

/* steam packet patrolling the basin */
const packet = new THREE.Group(); scene.add(packet);
(function(){
  const b=B();
  for(let z=-4;z<=4;z++){ const w=Math.max(0.4,1.7-Math.abs(z)*0.2);
    for(let x=Math.ceil(-w);x<=Math.floor(w);x++) for(let y=-1;y<=1;y++) put(b,x,y,z,[C.hullD,C.metal][(rnd(x,y,z)*2)|0]); }
  for(let z=-2;z<=2;z++) put(b,0,1.7,z,C.woodL,1.4,0.3,1);
  for(let y=2;y<=4;y++) for(let x=-1;x<=1;x++) put(b,x,y,0.5,C.metal,1,1,1);
  for(let y=2;y<=6;y++) put(b,0,y,-1.2,C.hullD,0.8,1,0.8);
  put(b,0,6.2,-1.2,C.red2,1.1,0.4,1.1);
  const m=build(b, new THREE.MeshLambertMaterial({flatShading:true}),'packet'); packet.add(m);
})();

/* distant ships on the roadstead */
function farShip(x,z,ry){
  const b=B();
  for(let i=-8;i<=8;i++){ const w=Math.max(0.5,3.2-Math.abs(i)*0.28);
    for(let xx=Math.ceil(-w);xx<=Math.floor(w);xx++) for(let y=-1;y<=2;y++) put(b,xx,y,i,0x39424d); }
  for(const mz of [-4,0,4]){ for(let y=3;y<=13;y++) put(b,0,y,mz,0x2f3842,0.5,1,0.5);
    for(const yy of [6,9.5]) put(b,0,yy,mz,0x2f3842, 6.5-(yy-6), 0.4,0.4); }
  put(b,0,2.4,7,0x8a6a48,1.6,1,1);
  const g=new THREE.Group(); g.position.set(x,0,z); g.rotation.y=ry; scene.add(g);
  const m=build(b,new THREE.MeshLambertMaterial({flatShading:true})); m.castShadow=false; g.add(m);
  return g;
}
const far = [ farShip(-78,34,0.6), farShip(-58,62,-0.4), farShip(74,72,2.2) ];

/* ============================================================  SEA  */
const seaMat = new THREE.MeshPhongMaterial({color:0xffffff, shininess:44, specular:0xdff2ff, flatShading:true});
seaMat.onBeforeCompile = sh => {
  sh.uniforms.uTime = U.time; sh.uniforms.uChop = U.chop;
  sh.vertexShader = sh.vertexShader
    .replace('#include <common>', '#include <common>\nuniform float uTime,uChop;')
    .replace('#include <begin_vertex>', `
      #include <begin_vertex>
      #ifdef USE_INSTANCING
        vec3 baseP = vec3(instanceMatrix[3][0], instanceMatrix[3][1], instanceMatrix[3][2]);
      #else
        vec3 baseP = transformed;
      #endif
      float w = sin(baseP.x*0.16 + uTime*1.15)
              + sin(baseP.z*0.21 - uTime*0.9)
              + sin((baseP.x + baseP.z*1.3)*0.09 + uTime*0.5);
      transformed.y += floor(w*1.35) * 0.26 * uChop;
    `);
};
const seaB = B();
const CELL = 2;
for(let x=-54;x<=54;x+=CELL) for(let z=-56;z<=48;z+=CELL){
  if(isLand(x,z) && isLand(x+1,z) && isLand(x,z+1) && isLand(x+1,z+1)) continue;
  let skip=false;
  for(const c of blocked){ if(Math.hypot(x-c.x, z-c.z) < c.r) skip=true; }
  if(skip) continue;
  const near = isLand(x-2,z)||isLand(x+2,z)||isLand(x,z-2)||isLand(x,z+2);
  const deep = Math.hypot(x, z) > 40;
  const c = deep ? 0x1d4b60 : (near ? 0x5aa2b4 : [0x2b6f83,0x2f7789,0x256073][(rnd(x,1,z)*3)|0]);
  put(seaB, x, -3.5, z, c, CELL, 8, CELL);
}
const seaMesh = build(seaB, seaMat); seaMesh.receiveShadow = true; seaMesh.castShadow = false; scene.add(seaMesh);

/* foam ringing walls, hull and breakwater */
const foamMat = new THREE.MeshBasicMaterial({color:0xffffff, transparent:true, opacity:.55, depthWrite:false});
const foamCells = [];
for(let z=-20;z<=22;z+=2) foamCells.push([16.4, z]);
for(let x=-36;x<=18;x+=2) foamCells.push([x, -14.4]);
for(let i=0;i<30;i+=2) foamCells.push([18-i*0.95, 21+i*0.22]);
for(let z=-12;z<=10;z+=2){ foamCells.push([9.2,z-1]); foamCells.push([17.2,z-1]); }
for(let i=0;i<foamCells.length;i+=1) if(rnd(i,4,4)<0.72) {} else foamCells.splice(i,1);
const foamB = B();
for(const [x,z] of foamCells) put(foamB, x, 0.7, z, 0xf6fbff, 1.6, 0.5, 1.6);
const foamMesh = build(foamB, foamMat); foamMesh.castShadow=false; scene.add(foamMesh);

/* ============================================================  SKY LIFE  */
const skyG = new THREE.Group(); scene.add(skyG);
/* clouds */
const cloudB = B();
for(let i=0;i<11;i++){
  const cx = -90 + i*24 + rnd(i,1,2)*12, cz = -30 + rnd(i,3,4)*70, cy = 30 + rnd(i,5,6)*12;
  const w = 8 + rnd(i,7,8)*14, d = 5 + rnd(i,9,0)*9;
  for(let k=0;k<Math.round(w*d/3);k++){
    const x = cx + (rnd(i,k,1)-0.5)*w, z = cz + (rnd(i,k,2)-0.5)*d;
    const h = 2 + rnd(i,k,3)*3.2;
    put(cloudB, Math.round(x), Math.round(cy + (rnd(i,k,4)-0.3)*2.5), Math.round(z),
      [0xf3f6fa,0xe6ecf4,0xd6dee9][(rnd(i,k,5)*3)|0], 3+rnd(i,k,6)*4, h, 2.4+rnd(i,k,7)*3);
  }
}
const cloudMesh = build(cloudB, new THREE.MeshLambertMaterial({flatShading:true}));
cloudMesh.castShadow = false; cloudMesh.receiveShadow = false; skyG.add(cloudMesh);

/* gulls */
const gulls = [];
for(let i=0;i<7;i++){
  const g = new THREE.Group();
  box(g,0,0,0,0.5,0.42,1.2,0xf4f7fb);
  box(g,0,0.2,0.3,0.34,0.3,0.4,0xf4f7fb);
  box(g,0.05,0.24,0.62,0.16,0.14,0.3,0xe7ba6d);
  const wl = box(g,-0.7,0.1,0,1.3,0.16,0.5,0xe8eef5);
  const wr = box(g, 0.7,0.1,0,1.3,0.16,0.5,0xdde5ee);
  wl.geometry.translate(0.65,0,0); wr.geometry.translate(-0.65,0,0);
  skyG.add(g);
  gulls.push({g, wl, wr, r:14+rnd(i,2,3)*26, a:rnd(i,4,5)*6.28, y:14+rnd(i,6,7)*16, sp:0.16+rnd(i,8,9)*0.16, ph:rnd(i,1,1)*6.28});
}

/* smoke: instanced puffs with per-instance alpha */
const smokeN = 64;
const smokeGeo = new THREE.BoxGeometry(1,1,1);
const smokeAlpha = new Float32Array(smokeN);
smokeGeo.setAttribute('aAlpha', new THREE.InstancedBufferAttribute(smokeAlpha,1));
const smokeMat = new THREE.ShaderMaterial({
  transparent:true, depthWrite:false, fog:true,
  uniforms:{ uColor:{value:new THREE.Color(0xd8d4cc)}, fogColor:{value:new THREE.Color()}, fogNear:{value:60}, fogFar:{value:230} },
  vertexShader:`attribute float aAlpha; varying float vA;
    #include <fog_pars_vertex>
    void main(){ vec4 p = vec4(position,1.0);
      #ifdef USE_INSTANCING
        p = instanceMatrix * p;
      #endif
      vec4 mvPosition = modelViewMatrix * p;
      gl_Position = projectionMatrix * mvPosition; vA = aAlpha;
      #include <fog_vertex>
    }`,
  fragmentShader:`uniform vec3 uColor; varying float vA;
    #include <fog_pars_fragment>
    void main(){ gl_FragColor = vec4(uColor, vA); #include <fog_fragment> }`
});
const smokeMesh = new THREE.InstancedMesh(smokeGeo, smokeMat, smokeN);
smokeMesh.frustumCulled = false; scene.add(smokeMesh);
const puffs = [];
for(let i=0;i<smokeN;i++) puffs.push({e:null, t:rnd(i,1,2)*3, life:rnd(i,3,4)*2, s:1});
const emitters = [
  {pos:new THREE.Vector3(24,13,-11), rise:2.6, size:0.9, col:0xc8c2ba},
  {pos:new THREE.Vector3(41,14,-10), rise:2.4, size:0.8, col:0xd2ccc4},
  {pos:new THREE.Vector3(41,15,-22), rise:1.6, size:0.5, col:0xcfc9c2, rate:0.35},
  {obj:packet, off:new THREE.Vector3(0,6.6,-1.2), rise:2.2, size:1.1, col:0x3f4550, rate:1.6}
];
let puffIdx = 0;
function spawnPuff(){
  const p = puffs[puffIdx % smokeN]; puffIdx++;
  const e = emitters[(Math.random()*emitters.length)|0];
  p.e = e; p.t = 0; p.life = 2.4 + Math.random()*2.2;
  p.vx = (Math.random()-0.5)*0.5; p.vz = (Math.random()-0.5)*0.5;
}

/* ============================================================  CRANE  */
const craneG = new THREE.Group(); craneG.position.set(22, 3, 8); scene.add(craneG);
box(craneG, 0, 3.2, 0, 1.6, 6.4, 1.6, C.metal);
box(craneG, 0, 6.6, 0, 2.2, 0.5, 2.2, C.slateD);
const jib = new THREE.Group(); jib.position.set(0, 6.9, 0); craneG.add(jib);
box(jib, -3.4, 0.2, 0, 7.4, 0.45, 0.45, C.woodD);
box(jib, -6.4, 0.9, 0, 1.4, 1.4, 0.4, C.metal);
box(jib, 0.9, 1.2, 0, 0.4, 2.2, 0.4, C.woodD);
box(jib, -2.2, -0.6, 0, 2.4, 0.9, 1.6, C.woodL);   // counterweight
const chainMat = new THREE.LineBasicMaterial({color:0x2b3138});
const chainGeo = new THREE.BufferGeometry();
chainGeo.setAttribute('position', new THREE.Float32BufferAttribute([0,0,0,0,0,0],3));
const chain = new THREE.LineSegments(chainGeo, chainMat); scene.add(chain);
const hook = box(scene, 0,0,0, 0.7,0.6,0.7, C.metal);
const cargo = box(scene, 0,0,0, 1.6,1.5,1.6, C.wood);

/* walking crew on the quay */
const walkers = [];
for(let i=0;i<3;i++){
  const g = new THREE.Group();
  box(g,0,0.6,0,0.42,1.2,0.34, [0x2f4a63,0x7a4a3a,0x4a3a2c][i]);
  box(g,0,1.5,0,0.36,0.42,0.32,0xe6cfa8);
  box(g,0,1.78,0,0.52,0.2,0.52, i===1?0xd8c9a0:0x26333f);
  scene.add(g);
  walkers.push({g, z:-10+i*7, dir:i===1?-1:1, x:21.2});
}

/* ============================================================  POIs  */
const POIS = {
  ship:{n:'Brig “Meridian”', meta:'Berth 3 · alongside', body:'Two hundred and fourteen tons, bonded: salted cod, Baltic timber and one cask of claret the custom house keeps arguing about. Moored at flood tide; master says he sails on the ebb, and he says that every day.',
    specs:[['LoA','86 ft'],['Beam','21 ft'],['Tons','214'],['Sails','six + three jibs'],['Master','J. Rusk']], cam:{p:[-17,12,15],t:[13,7,-1],f:44}},
  quay:{n:'Tidewater Quay', meta:'cobble · granite', body:'Three hundred fathoms of cobble and granite, twenty-two bollards, and a cart that has been unloading since the light changed. Gulls work the fish stalls; the tide washes the steps at the north slip.',
    specs:[['Length','300 fm'],['Bollards','22'],['Paving','granite set'],['Lamps','7 oil']]},
  light:{n:'Belhaven Light', meta:'granite · 112 steps', body:'A pair of white flashes every ten seconds. Lit by oil until the council paid for paraffin, and by the keeper’s stubbornness ever since. From the lamp room you can count every ship that means it.',
    specs:[['Tower','118 ft'],['Range','19 miles'],['Character','Fl(2) W 10s'],['Keeper','A. Merle']], cam:{p:[7,15,34],t:[22,12,18],f:40}},
  custom:{n:'Custom House', meta:'stone · colonnade', body:'Flags, columns, ledgers. Nothing leaves the port without a stamp here, and nothing comes in that the tidewaiters have not weighed twice. The claret is still in dispute.',
    specs:[['Duties','2 per cent'],['Clerks','6'],['Flag','red, union corner']]},
  warehouse:{n:'Bonded Warehouses Nos. 1–3', meta:'brick · tar · gables', body:'Casks of herring, bales of wool, crates of machine parts and, in No. 3, two hundred hats nobody has called for. The hoist beams are still good for a ton.',
    specs:[['Nos.','1–3'],['Roof','slate, gabled'],['Hoist','hand-winch'],['Tar','annual']]},
  crane:{n:'Gantry Crane', meta:'iron · hand-winched', body:'Swings a ton from deck to dray in ninety seconds provided the crew are singing. The winch drum is original; the hook is not; the chain is argued about at every audit.',
    specs:[['Lift','1.2 tons'],['Reach','24 ft'],['Operator','H. Cobb']]},
  fleet:{n:'Fishing Fleet', meta:'six in the basin', body:'Lugs, dories and one smart cutter that outsails everything except the tide. They come in at dusk with the day’s catch and are back on the water before the lamps are lit.',
    specs:[['Craft','6'],['Ground','the bank'],['Landed','herring, cod']]},
  break:{n:'The Breakwater', meta:'rubble stone', body:'Stone dumped from a tip rail until it made a calm. In a westerly gale the sea crosses it and the spray reaches as far as the lamp, which is considered a good sign by nobody.',
    specs:[['Length','280 fm'],['Stone','dartmoor granite'],['Overwash','west, 8 force']]},
  mill:{n:'Drift Mill', meta:'four sails · hillhead', body:'Four sails and a miller who trusts the wind more than the clock. When the sails are round, the wharf smells of fresh ground barley and the barges queue.',
    specs:[['Sails','4'],['Miller','T. Pengelly'],['Stone','local granite']]},
  packet:{n:'Steam Packet “Pilot”', meta:'meets ships at the bar', body:'Goes out to meet whatever comes over the bar and brings the pilot back with it. Leaves grumbling fishermen in its wake and a smell of coal that the town has stopped noticing.',
    specs:[['Engine','60 hp'],['Crew','5'],['Runs','tidal']]}
};
/* camera-only presets */
const VIEWS = {
  overview:{p:[-58,33,47], t:[6,4,-1], f:42},
  quay:    {p:[27,6,20],  t:[18,3,3], f:42},
  deck:    {follow:true, off:[1.7,5.2,7.2], tgt:[-0.6,8.4,-2.5], f:52},
  light:   {p:[7,15,34],  t:[22,12,18], f:40},
  chart:   {p:[6,124,6],  t:[6,0,0], f:24},
  town:    {p:[-6,14,6],  t:[32,7,-6], f:44},
  mouth:   {p:[-4,11,44], t:[10,3,24], f:46}
};
const BOXES = {
  quay:[17,0,-14,24,6,16], warehouse:[21,2,-12,44,12,-3], custom:[32,3,3,44,13,12],
  crane:[20,3,5,27,9,11], fleet:[-24,0,-2,-2,6,20], break:[-8,0,19,20,4,24],
  mill:[36,5,-27,46,17,-18]
};
const boxes3 = {};
for(const k in BOXES){ const b=BOXES[k]; boxes3[k] = new THREE.Box3(new THREE.Vector3(b[0],b[1],b[2]), new THREE.Vector3(b[3],b[4],b[5])); }
boxes3.light  = lightMesh.boundingBox.clone();
boxes3.ship   = hullMesh.boundingBox.clone();   // ship-local
boxes3.packet = null;

/* highlight: edges + shell */
function makeHi(hex, op){
  const g = new THREE.Group(); scene.add(g); g.visible = false;
  const shell = new THREE.Mesh(new THREE.BoxGeometry(1,1,1),
    new THREE.MeshBasicMaterial({color:hex, transparent:true, opacity:op, blending:THREE.AdditiveBlending, depthWrite:false}));
  const edges = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(1,1,1)),
    new THREE.LineBasicMaterial({color:hex, transparent:true, opacity:0.9}));
  g.add(shell, edges); g.userData = {shell, edges};
  return g;
}
const hiHover = makeHi(0xe7ba6d, 0.06), hiSel = makeHi(0xf6d9a4, 0.10);
function placeHi(g, box){
  if(!box){ g.visible=false; return; }
  const c = box.getCenter(new THREE.Vector3()), s = box.getSize(new THREE.Vector3());
  g.position.copy(c); g.scale.set(s.x+1.4, s.y+1.4, s.z+1.4); g.visible = true;
}
function worldBox(k){
  let b = boxes3[k] || null;
  if(k==='ship'){ b = hullMesh.boundingBox.clone().applyMatrix4(ship.matrixWorld); }
  if(k==='packet'){ packet.updateMatrixWorld(); const bb = new THREE.Box3().setFromCenterAndSize(packet.position.clone().setY(2), new THREE.Vector3(9,8,9)); b = bb; }
  if(!b && k==='light'){ b = lightMesh.boundingBox.clone(); }
  return b;
}

/* ============================================================  UI WIRING  */
const $ = s=>document.querySelector(s);
const rowsEl = $('#rows');
Object.entries(POIS).forEach(([k,p],i)=>{
  const b = document.createElement('button');
  b.className='row'; b.dataset.poi=k;
  b.innerHTML = `<span class="idx">${String(i+1).padStart(2,'0')}</span><span class="nm">${p.n}</span><span class="mt">${p.meta}</span>`;
  b.addEventListener('mouseenter', ()=> setHover(k));
  b.addEventListener('mouseleave', ()=> setHover(null));
  b.addEventListener('click', ()=> selectPoi(k));
  rowsEl.appendChild(b);
});
$('#regCount').textContent = Object.keys(POIS).length + ' marks';

const logsEl = $('#logs');
function clockStr(){
  const h = Math.floor(hour), m = Math.floor((hour-h)*60);
  return String(h).padStart(2,'0')+':'+String(m).padStart(2,'0');
}
function logLine(txt){
  const p = document.createElement('p');
  p.innerHTML = `<time>${clockStr()}</time><span>${txt}</span>`;
  logsEl.prepend(p);
  while(logsEl.children.length>9) logsEl.lastChild.remove();
}

const tip = $('#tip');
let hovered = null, selected = null;
function setHover(k){
  if(hovered===k) return;
  hovered = k;
  canvas.classList.toggle('pick', !!k);
  document.querySelectorAll('.row').forEach(r=> r.classList.toggle('hov', r.dataset.poi===k));
  if(k) placeHi(hiHover, worldBox(k)); else hiHover.visible=false;
  if(!k) tip.style.opacity = 0;
}
function selectPoi(k){
  selected = k;
  document.querySelectorAll('.row').forEach(r=> r.classList.toggle('sel', r.dataset.poi===k));
  const p = POIS[k];
  $('#dossier').classList.remove('empty');
  $('#dTag').textContent = p.meta;
  $('#dTitle').textContent = p.n;
  $('#dBody').textContent = p.body;
  $('#dSpecs').innerHTML = (p.specs||[]).map(s=>`<div><span>${s[0]}</span><b>${s[1]}</b></div>`).join('');
  placeHi(hiSel, worldBox(k));
  logLine(`Launch detailed for ${p.n}.`);
  if(p.cam) flyTo(p.cam);
}
$('#dClose').addEventListener('click', ()=>{ $('#dossier').classList.add('empty'); hiSel.visible=false; selected=null;
  document.querySelectorAll('.row').forEach(r=>r.classList.remove('sel')); });

/* camera tween + follow */
let tw = null, followObj = null, localAnchor = new THREE.Vector3(), lastAnchor = new THREE.Vector3();
function flyTo(v){
  tw = {t:0, dur:1.25,
    fp:camera.position.clone(), tp:new THREE.Vector3(...v.p),
    ft:controls.target.clone(), tt:new THREE.Vector3(...v.t),
    ff:camera.fov, tf:v.f||42, view:v};
  followObj = null;
}
function enterFollow(v){
  followObj = ship;
  localAnchor = new THREE.Vector3(...v.off);
  const tgt = new THREE.Vector3(...v.tgt);
  lastAnchor.copy(ship.localToWorld(localAnchor.clone()));
  controls.target.copy(ship.localToWorld(tgt));
}
document.querySelectorAll('[data-view]').forEach(b=> b.addEventListener('click', ()=>{
  const v = VIEWS[b.dataset.view];
  if(v.follow){ flyTo({p:ship.localToWorld(new THREE.Vector3(...v.off)).toArray(), t:ship.localToWorld(new THREE.Vector3(...v.tgt)).toArray(), f:v.f});
    tw.after = ()=> enterFollow(v); }
  else flyTo(v);
  markView(b.dataset.view);
}));
function markView(name){ document.querySelectorAll('[data-view]').forEach(b=>b.classList.toggle('on', b.dataset.view===name)); }
markView('overview');

/* raycast */
const ray = new THREE.Raycaster(); const ndc = new THREE.Vector2();
const rayTargets = [hullMesh, lightMesh, bldgMesh, propMesh, landMesh, bwMesh, craneG, ...sloops.map(s=>s.children[0]), packet.children[0]];
let lastRay = 0, downAt = null;
canvas.addEventListener('pointermove', e=>{
  tip.style.left = e.clientX+'px'; tip.style.top = e.clientY+'px';
  const now = performance.now(); if(now-lastRay < 60) return; lastRay = now;
  ndc.x = (e.clientX/innerWidth)*2-1; ndc.y = -(e.clientY/innerHeight)*2+1;
  ray.setFromCamera(ndc, camera);
  const hits = ray.intersectObjects(rayTargets, false);
  const poi = hits.length ? (hits[0].object.userData.poi || null) : null;
  setHover(poi);
  if(poi){ tip.innerHTML = `${POIS[poi].n}<u>click to visit</u>`; tip.style.opacity = 1; }
});
canvas.addEventListener('pointerdown', e=>{ downAt = {x:e.clientX,y:e.clientY}; controls.autoRotate=false; lastInput=performance.now(); });
canvas.addEventListener('pointerup', e=>{
  lastInput = performance.now();
  if(downAt && Math.hypot(e.clientX-downAt.x, e.clientY-downAt.y) < 5 && hovered) selectPoi(hovered);
  downAt = null;
});
canvas.addEventListener('wheel', ()=>{ lastInput = performance.now(); controls.autoRotate=false; }, {passive:true});

/* console */
const sHour = $('#sHour'), sWind = $('#sWind');
let hour = 17.2, drift = false;
sHour.addEventListener('input', ()=>{ hour = +sHour.value; });
sWind.addEventListener('input', ()=>{ U.wind.value = +sWind.value; $('#vWind').textContent = (+sWind.value).toFixed(2); });
$('#bDrift').addEventListener('click', e=>{ drift = !drift; e.target.classList.toggle('on', drift);
  logLine(drift ? 'Watch set; the day runs itself.' : 'Time held at this hour.'); });
let sailState = 0; const SAILN = ['Full','Reefed','Close-reefed'];
$('#bSail').addEventListener('click', e=>{ sailState = (sailState+1)%3; e.target.textContent = 'Canvas: '+SAILN[sailState].toLowerCase();
  $('#rSail').textContent = SAILN[sailState];
  logLine(`Canvas ${SAILN[sailState].toLowerCase()} — ${SAILN[sailState]==='Full'?'the wind keeps it working':'made fast to the yards'}.`;);
});
$('#bRig').addEventListener('click', e=>{ rigMesh.visible = !rigMesh.visible; e.target.classList.toggle('on', rigMesh.visible); });
$('#bSky').addEventListener('click', e=>{ skyG.visible = !skyG.visible; e.target.classList.toggle('on', skyG.visible); });
$('#bReset').addEventListener('click', ()=>{ flyTo(VIEWS.overview); markView('overview'); logLine('View trimmed to the general plan.'); });
$('#bUI').addEventListener('click', ()=> document.body.classList.toggle('hide-ui'));
addEventListener('keydown', e=>{
  const k = e.key.toLowerCase();
  if(k==='h') document.body.classList.toggle('hide-ui');
  if(k==='d'){ const v=VIEWS.deck; flyTo({p:ship.localToWorld(new THREE.Vector3(...v.off)).toArray(), t:ship.localToWorld(new THREE.Vector3(...v.tgt)).toArray(), f:v.f}); tw.after=()=>enterFollow(v); markView('deck'); }
  if(k==='r'){ flyTo(VIEWS.overview); markView('overview'); }
  const num = parseInt(k,10);
  const keys = Object.keys(POIS);
  if(num>=1 && num<=9 && keys[num-1]) selectPoi(keys[num-1]);
});

/* ============================================================  PALETTE  */
const STOPS = [
 {t:0,   top:0x081024, hor:0x101a30, sun:0xa9c4ea, si:0.6,  hs:0x22355a, hg:0x080e18, fog:0x121c30, wt:0x2b4763, n:1},
 {t:5,   top:0x1a2742, hor:0x3a4258, sun:0x9fb4d8, si:0.62, hs:0x33455f, hg:0x141a24, fog:0x2b3446, wt:0x365069, n:0.78},
 {t:6.6, top:0x2e4d74, hor:0xe69a62, sun:0xffb074, si:1.15, hs:0x6e86a6, hg:0x2b2822, fog:0xc79a76, wt:0x4e7f90, n:0.24},
 {t:9,   top:0x4a7cb4, hor:0xbcd6e2, sun:0xffe7c4, si:2.15, hs:0x9dc2df, hg:0x4e564a, fog:0xccdae4, wt:0x9fd3e2, n:0},
 {t:13,  top:0x3d7cc2, hor:0xa8d4ea, sun:0xffffff, si:2.9,  hs:0x9bc6ea, hg:0x585f50, fog:0xa9d0e2, wt:0xa9dcec, n:0},
 {t:17.2,top:0x3a6ea2, hor:0xf1c383, sun:0xffc984, si:2.35, hs:0xa9c6d8, hg:0x6a5742, fog:0xdcc9a9, wt:0xd8b28f, n:0},
 {t:19.4,top:0x2f5480, hor:0xf28f5f, sun:0xff9a58, si:1.5,  hs:0x7f9db4, hg:0x4a382c, fog:0xd08f6c, wt:0xb87f66, n:0.3},
 {t:20.8,top:0x1b2f4e, hor:0x7a5d6c, sun:0xd08f7a, si:0.8,  hs:0x43587a, hg:0x22202a, fog:0x5c4a52, wt:0x51607a, n:0.64},
 {t:22,  top:0x081024, hor:0x101a30, sun:0xa9c4ea, si:0.6,  hs:0x22355a, hg:0x080e18, fog:0x121c30, wt:0x2b4763, n:1}
];
const tmpA = new THREE.Color(), tmpB = new THREE.Color();
function lerpHex(h1,h2,f){ tmpA.setHex(h1); tmpB.setHex(h2); return tmpA.clone().lerp(tmpB, f); }
function paletteAt(t){
  t = ((t%24)+24)%24;
  let i = 0;
  for(let k=0;k<STOPS.length;k++) if(t >= STOPS[k].t) i = k;
  const a = STOPS[i], b = STOPS[Math.min(STOPS.length-1, i+1)];
  const f = b.t>a.t ? (t-a.t)/(b.t-a.t) : 0;
  return { top:lerpHex(a.top,b.top,f), hor:lerpHex(a.hor,b.hor,f), sun:lerpHex(a.sun,b.sun,f),
    hs:lerpHex(a.hs,b.hs,f), hg:lerpHex(a.hg,b.hg,f), fog:lerpHex(a.fog,b.fog,f), wt:lerpHex(a.wt,b.wt,f),
    si: a.si+(b.si-a.si)*f, n: a.n+(b.n-a.n)*f };
}
function applyPalette(){
  const p = paletteAt(hour);
  skyMat.uniforms.uTop.value.copy(p.top);
  skyMat.uniforms.uHor.value.copy(p.hor);
  skyMat.uniforms.uSun.value.copy(p.sun);
  skyMat.uniforms.uNight.value = p.n;
  scene.fog.color.copy(p.fog);
  hemi.color.copy(p.hs); hemi.groundColor.copy(p.hg); hemi.intensity = 0.75 - p.n*0.42;
  const night = p.n; U.night.value = night;
  /* sun / moon direction */
  const th = Math.PI * (((hour-6)/12));
  let dir = new THREE.Vector3(Math.cos(th)*0.92, Math.sin(th), -0.28).normalize();
  if(dir.y < 0.02){ dir.negate(); sun.color.copy(tmpA.setHex(0xbcd4f2)); } else sun.color.copy(p.sun);
  sun.intensity = p.si;
  sun.position.copy(dir).multiplyScalar(190);
  fill.intensity = 0.1 + night*0.12;
  /* glows */
  glowMat.color.copy(tmpA.setHex(C.glass).lerp(tmpB.setHex(0xffcf7a), night));
  shipGlassMatColour(night);
  for(const s of lampHeads) s.material.opacity = night*0.85;
  beaconSprite.material.opacity = 0.12 + night*0.9;
  beaconMat2.opacity = 0.05 + night*0.5;
  beaconLight.intensity = night*55;
  lampA.intensity = lampB.intensity = lampC.intensity = night*16;
  seaMat.color.copy(p.wt);
  foamMat.opacity = 0.32 + 0.28*(1-night);
  smokeMat.uniforms.fogColor.value.copy(scene.fog.color);
  smokeMat.uniforms.fogNear.value = scene.fog.near;
  smokeMat.uniforms.fogFar.value = scene.fog.far;
  /* lamp log once, at dusk */
  const lit = night>0.42;
  if(lit !== wasLit){ wasLit = lit; logLine(lit ? 'Lamp lighters out — the quay and the headland are lit.' : 'Lamps put out; the day is on the water again.'); }
}
let wasLit = null;
function shipGlassMatColour(n){ /* shared glowMat already handles ship windows */ }

/* ============================================================  AMBIENT LOG  */
const AMBIENT = [
  ()=>['A dray backs up under the gantry.'],
  ()=>['The pilot signals two points south-south-west.'],
  ()=>['Herring landed at the north slip — six baskets short of the tally.'],
  ()=>['Gulls mob the packet’s wake.'],
  ()=>['Rigging slacked off; the wind keeps out of the west.'],
  ()=>['Cask of claret checked twice by the tidewaiter.'],
  ()=>['Breakwater overwashing; spray as far as the lamp.'],
  ()=>['Miller has the sails round on the drift; barges queue.'],
  ()=>['Watch set on the brig; anchor watch from midnight.'],
  ()=>['A lugger came in under the quay and asked for berth room.'],
  ()=>['Timber tipped at No. 2; the crane groaned and held.'],
  ()=>['Glass up on the roadstead — three sail, standing off.']
];
setInterval(()=>{
  const a = AMBIENT[(Math.random()*AMBIENT.length)|0];
  logLine(a()[0]);
}, 7200);
logLine('Pilot boarded the Meridian off the bar.');
setTimeout(()=>logLine('Brig moored, berth 3, outside the wharf.'), 900);
setTimeout(()=>logLine('Breakwater washed; lamp at full burn.'), 1800);

/* ============================================================  LOOP  */
let lastInput = performance.now();
let fps = 60, acc = 0, frames = 0, lastT = performance.now();
const clock = new THREE.Clock();
let furl = 0, furlTarget = 0;

function tick(){
  const dt = Math.min(0.05, clock.getDelta());
  const t = clock.elapsedTime;
  U.time.value = t;
  if(drift) hour = (hour + dt*0.28) % 24;
  U.chop.value = 0.42 + U.wind.value*1.15;

  /* tide */
  const tide = Math.sin((hour/24)*Math.PI*2 - 1.2)*0.5;
  seaMesh.position.y = tide;
  foamMesh.position.y = tide;

  /* ship motion */
  ship.position.y = tide*0.92 + Math.sin(t*0.62)*0.13;
  ship.rotation.z = Math.sin(t*0.45)*0.019;
  ship.rotation.x = Math.sin(t*0.38+1.2)*0.013;

  /* sails */
  furlTarget = [0, 0.5, 0.92][sailState];
  furl += (furlTarget - furl) * Math.min(1, dt*3.2);
  for(const s of sails){
    const f = 1 - furl*0.86;
    s.scale.y = f;
    s.position.y = s.userData.yard - f*s.userData.h/2;
    if(s.userData.mat.userData.shader){}
  }
  furlMesh.visible = furl > 0.55;

  /* packet patrol + wake */
  const pa = t*0.13;
  packet.position.set(Math.cos(pa)*20, tide*0.85 + Math.sin(t*0.9)*0.12, 6 + Math.sin(pa)*14);
  packet.rotation.y = -pa + Math.PI/2;
  packet.rotation.z = Math.sin(t*0.7)*0.03;

  /* sloops bob */
  sloops.forEach((s,i)=>{ s.position.y = tide*0.85 + Math.sin(t*0.55+i*1.7)*0.14; s.rotation.z = Math.sin(t*0.5+i)*0.035; });
  far.forEach((s,i)=>{ s.position.y = Math.sin(t*0.3+i)*0.3; s.rotation.z = Math.sin(t*0.2+i)*0.02; });

  /* crane */
  const cyc = (t*0.30)%(Math.PI*2);
  jib.rotation.y = -0.55 + Math.sin(cyc*0.5)*0.9;
  const hy = 6.6 - (0.5+0.5*Math.sin(cyc))*3.4;
  const tipWorld = new THREE.Vector3(-6.4, 0.4, 0).applyMatrix4(jib.matrixWorld);
  hook.position.set(tipWorld.x, hy, tipWorld.z);
  cargo.visible = Math.sin(cyc) > -0.15;
  cargo.position.set(tipWorld.x, hy-0.9, tipWorld.z);
  cargo.rotation.y = jib.rotation.y;
  chain.position.set(0,0,0);
  const cp = chainGeo.attributes.position;
  cp.setXYZ(0, tipWorld.x, tipWorld.y, tipWorld.z);
  cp.setXYZ(1, hook.position.x, hook.position.y+0.3, hook.position.z);
  cp.needsUpdate = true;

  /* windmill */
  if(millHub) millHub.rotation.x = t*(0.25 + U.wind.value*1.35);

  /* gulls */
  for(const g of gulls){
    g.a += dt*g.sp;
    const rr = g.r + Math.sin(t*0.3+g.ph)*4;
    g.g.position.set(Math.cos(g.a)*rr, g.y + Math.sin(t*0.6+g.ph)*2.2, Math.sin(g.a)*rr + 2);
    g.g.rotation.y = -g.a - Math.PI/2;
    const flap = Math.sin(t*6 + g.ph)*(0.5+U.wind.value*0.3);
    g.wl.rotation.z = flap; g.wr.rotation.z = -flap;
  }

  /* clouds drift */
  skyG.position.x = (t*(0.7 + U.wind.value*1.6)) % 240;
  skyG.position.z = Math.sin(t*0.05)*6;

  /* smoke */
  if(Math.random() < dt*8) spawnPuff();
  const dm = new THREE.Object3D();
  for(let i=0;i<smokeN;i++){
    const p = puffs[i];
    if(!p.e){ dm.scale.set(0.001,0.001,0.001); dm.position.set(0,-50,0); dm.updateMatrix(); smokeMesh.setMatrixAt(i,dm.matrix); smokeAlpha[i]=0; continue; }
    p.t += dt;
    if(p.t > p.life){ p.e = null; smokeAlpha[i]=0; dm.scale.set(0.001,0.001,0.001); dm.position.set(0,-50,0); dm.updateMatrix(); smokeMesh.setMatrixAt(i,dm.matrix); continue; }
    const k = p.t/p.life;
    const e = p.e;
    const base = e.pos ? e.pos : e.obj.localToWorld(e.off.clone());
    dm.position.set(base.x + p.vx*p.t + Math.sin(p.t*1.3+i)*0.4,
                    base.y + k*e.rise*3.2,
                    base.z + p.vz*p.t + Math.cos(p.t*1.1+i)*0.4);
    const s = e.size*(0.6 + k*2.2);
    dm.scale.set(s,s,s); dm.rotation.set(p.t*0.4, p.t*0.3, 0); dm.updateMatrix();
    smokeMesh.setMatrixAt(i, dm.matrix);
    smokeAlpha[i] = (1-k)*0.42*(0.5+0.5*(1-U.night.value*0.35));
  }
  smokeMesh.instanceMatrix.needsUpdate = true;
  smokeGeo.attributes.aAlpha.needsUpdate = true;

  /* walkers */
  for(const w of walkers){
    w.z += w.dir*dt*1.3;
    if(w.z>14){w.dir=-1} if(w.z<-13){w.dir=1}
    w.g.position.set(w.x, 2.9, w.z);
    w.g.rotation.y = w.dir>0 ? Math.PI/2 : -Math.PI/2;
    w.g.position.y = 2.9 + Math.abs(Math.sin(t*6))*0.09;
  }

  /* beacon */
  beaconG.rotation.y += dt*0.85;

  /* highlights pulse */
  const pu = 0.5 + 0.5*Math.sin(t*3.4);
  hiHover.userData.shell.material.opacity = 0.04 + pu*0.05;
  hiSel.userData.edges.material.opacity = 0.55 + pu*0.45;
  if(hiSel.visible){ const b = selected==='ship'? worldBox('ship') : (selected==='packet'?worldBox('packet'):boxes3[selected]); if(b) placeHi(hiSel, b); }
  if(hiHover.visible && hovered==='ship') placeHi(hiHover, worldBox('ship'));

  /* camera tween */
  if(tw){
    tw.t += dt;
    const k = Math.min(1, tw.t/tw.dur), e = k<0.5 ? 4*k*k*k : 1-Math.pow(-2*k+2,3)/2;
    camera.position.lerpVectors(tw.fp, tw.tp, e);
    controls.target.lerpVectors(tw.ft, tw.tt, e);
    camera.fov = tw.ff + (tw.tf-tw.ff)*e; camera.updateProjectionMatrix();
    if(k>=1){ if(tw.after) tw.after(); tw = null; }
  } else if(followObj){
    followObj.updateMatrixWorld();
    const a = followObj.localToWorld(localAnchor.clone());
    const d = a.clone().sub(lastAnchor);
    camera.position.add(d); controls.target.add(d); lastAnchor.copy(a);
  }

  applyPalette();
  controls.update();
  sky.position.copy(camera.position);
  renderer.render(scene, camera);

  /* HUD */
  frames++; acc += dt;
  if(acc > 0.4){ fps = Math.round(frames/acc); frames=0; acc=0; $('#rFps').textContent = fps; }
  $('#rTime').textContent = clockStr();
  $('#vHour').textContent = clockStr();
  $('#rTide').textContent = (tide>=0?'+':'−') + Math.abs(tide*1.6).toFixed(2);
  $('#rWind').textContent = Math.round(U.wind.value*20) + ' kt';
  const az = Math.atan2(camera.position.x-controls.target.x, camera.position.z-controls.target.z);
  $('#needle').setAttribute('transform', `rotate(${(-az*180/Math.PI).toFixed(1)})`);

  /* idle drift returns */
  if(performance.now()-lastInput > 24000 && !followObj && !tw) controls.autoRotate = true;

  requestAnimationFrame(tick);
}

/* ============================================================  KICKOFF  */
addEventListener('resize', ()=>{
  camera.aspect = innerWidth/innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
applyPalette();
$('#rBlk').textContent = BLOCKS.toLocaleString();
renderer.render(scene, camera);
requestAnimationFrame(()=>{
  $('#bootBar').style.width = '100%';
  $('#boot .big').textContent = 'Berth 3 — the Meridian is in.';
  setTimeout(()=> $('#boot').classList.add('gone'), 620);
  tick();
});
</script>
</body>
</html>
```

**What's in there**

- **The brig alongside berth 3** — a voxel hull with wale stripe, portholes, bowsprit, figurehead, stern cabin, deck crew, three masts with seven square sails plus two jibs. Sails are instanced panels whose bellies and flutter are displaced in the vertex shader by the wind slider; the *Canvas* button compresses them down onto the yards and reveals the furled bundles beneath. Rigging is real line geometry, so it rides the swell with the hull.
- **The harbour** — a granite quay with bollards, lamps, crates, barrels, rope coils, a market line, a cart and a slipway; bonded warehouses, a colonnaded Custom House, a chapel tower, cooperage sheds and a drift mill whose four sails turn with the wind.
- **Belhaven Light** on its rocky head at the mouth, sweeping a real rotating spotlight plus two additive beams; oil lamps, windows and stern lights warm up as the hour crosses dusk (the harbour log announces it).
- **Sea and sky** — wave blocks stepped into quantised voxel swell with Phong facet glitter, a tide that moves the water, the ship and the foam line, clouds drifting with the wind, seven circling gulls, smoke puffs with per-instance alpha from the mill, the warehouse chimneys and the packet's funnel, stars and a moon that take over when the sun drops below the bar.
- **Interaction** — hover the water to tag a landmark (voxel bracket lights up, the register row mirrors it), click to have the launch fly you there and open its dossier; presets, hour and wind sliders, `1–9` for landmarks, `D` for the deck view (the camera then rides the brig's roll), `H` to stow the plate.