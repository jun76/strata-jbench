Here's the whole diorama in one file — open it in Chrome and drag to orbit. Every cube (≈26,000) is a GPU instance, the sea is an instanced voxel grid with waves/foam/glitter in GLSL, and time-of-day is a slider that repaints the sky, lights, water, windows and lighthouse beam together.

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Anchor Bay — a sailing ship calls at the harbour</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bungee&family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root{
    --ink:#070c12; --panel:rgba(9,15,22,.84); --line:#2b3b49; --line-2:#425567;
    --amber:#e9a94b; --amber-hi:#ffd08a; --foam:#9fd0d6; --text:#e7edf3; --muted:#93a6b4;
  }
  *{box-sizing:border-box}
  html,body{margin:0;height:100%;overflow:hidden;background:var(--ink);color:var(--text);
    font-family:'IBM Plex Sans',system-ui,-apple-system,sans-serif}
  canvas{display:block;width:100%;height:100%}
  #veil{position:fixed;inset:0;background:#070c12;opacity:1;transition:opacity 1.1s ease;z-index:9;pointer-events:none}
  .hud{position:fixed;inset:0;display:flex;flex-direction:column;justify-content:space-between;
    padding:clamp(12px,2.1vw,26px);pointer-events:none;z-index:5}
  .eyebrow{font-family:'IBM Plex Mono',monospace;font-size:10.5px;letter-spacing:.28em;
    text-transform:uppercase;color:var(--amber);display:flex;gap:10px;align-items:center}
  .eyebrow i{width:26px;height:1px;background:var(--amber);display:inline-block;opacity:.7}
  h1{font-family:'Bungee',cursive;font-weight:400;font-size:clamp(26px,4.1vw,56px);line-height:.92;
    margin:10px 0 0;color:#fff;text-shadow:0 3px 0 rgba(0,0,0,.42),0 0 34px rgba(233,169,75,.22);
    max-width:16ch}
  h1 em{font-style:normal;color:var(--amber-hi)}
  .sub{margin:9px 0 0;max-width:42ch;font-size:13.5px;line-height:1.5;color:#c4d3de;
    text-shadow:0 1px 10px rgba(0,0,0,.6)}
  .sub b{color:#fff;font-weight:600}
  .rail{position:fixed;left:0;right:0;bottom:clamp(96px,13vh,150px);height:1px;
    background:linear-gradient(90deg,transparent,rgba(233,169,75,.32),transparent);pointer-events:none;z-index:4}

  .foot{display:flex;gap:clamp(12px,3vw,40px);align-items:flex-end;flex-wrap:wrap;
    font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.12em;
    text-transform:uppercase;color:var(--muted);text-shadow:0 1px 6px rgba(0,0,0,.8)}
  .foot strong{color:#dde8f0;font-weight:600}
  .foot .k{color:var(--amber)}

  .panel{pointer-events:auto;align-self:flex-end;width:min(330px,94vw);
    background:var(--panel);border:1px solid var(--line);padding:16px 16px 14px;
    box-shadow:0 24px 44px -20px rgba(0,0,0,.9),inset 0 1px 0 rgba(255,255,255,.05)}
  .panel::before,.panel::after{content:"";position:absolute;width:10px;height:10px;border:1px solid var(--amber);opacity:.55}
  .panel::before{left:-1px;top:-1px;border-right:0;border-bottom:0}
  .panel::after{right:-1px;bottom:-1px;border-left:0;border-top:0}
  .panel h2{margin:0;font-family:'IBM Plex Mono',monospace;font-weight:600;font-size:11px;
    letter-spacing:.24em;text-transform:uppercase;color:var(--muted)}
  .panel hr{border:0;border-top:1px solid var(--line);margin:12px 0}
  label{display:block;font-family:'IBM Plex Mono',monospace;font-size:10px;letter-spacing:.2em;
    text-transform:uppercase;color:var(--muted);margin-bottom:6px}
  .timeval{float:right;color:var(--amber-hi);font-weight:600}
  input[type=range]{width:100%;accent-color:var(--amber);height:22px;background:transparent}
  .btns{display:grid;grid-template-columns:1fr 1fr;gap:6px}
  button{font-family:'IBM Plex Mono',monospace;font-size:10.5px;letter-spacing:.14em;
    text-transform:uppercase;color:#cfdbe6;background:rgba(255,255,255,.03);
    border:1px solid var(--line);padding:8px 6px;cursor:pointer;transition:.16s ease}
  button:hover{border-color:var(--amber);color:#fff;background:rgba(233,169,75,.13);transform:translateY(-1px)}
  button.on{border-color:var(--amber);color:#0c1218;background:var(--amber);font-weight:600}
  .stat{margin-top:11px;font-family:'IBM Plex Mono',monospace;font-size:10px;letter-spacing:.14em;
    color:#7f92a1;display:flex;justify-content:space-between}
  .stat b{color:var(--foam);font-weight:600}
  @media (max-width:640px){ .panel{width:100%} .sub{display:none} }
</style>
<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.161.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.161.0/examples/jsm/"
  }
}
</script>
</head>
<body>
<div id="veil"></div>
<canvas id="scene"></canvas>

<div class="hud">
  <header>
    <div class="eyebrow"><i></i>voxel diorama nº 07 · instanced cubes</div>
    <h1>ANCHOR&nbsp;BAY<br><em>the Meridian calls</em></h1>
    <p class="sub"><b>212 tons, arriving from Newlyn.</b> She's tied up off the granite quay at the turn of the tide;
       the fish van's already waiting by the warehouse door.</p>
  </header>
  <div class="foot">
    <span><span class="k">drag</span> orbit</span>
    <span><span class="k">scroll</span> zoom</span>
    <span><span class="k">right-drag</span> pan</span>
    <span><span class="k">1–5</span> views · <span class="k">space</span> spin</span>
    <span style="color:#6d8091">three.js · no textures, only cubes</span>
  </div>
</div>
<div class="rail"></div>

<div class="panel">
  <h2>Bridge console</h2>
  <hr>
  <label>time of day <span class="timeval" id="todLabel">golden hour</span></label>
  <input id="tod" type="range" min="0" max="1000" value="340" aria-label="time of day">
  <div class="btns" style="margin-top:12px">
    <button id="v0" class="on">quay view</button>
    <button id="v1">broadside</button>
    <button id="v2">masthead</button>
    <button id="v3">pier</button>
    <button id="v4">lighthouse</button>
    <button id="spin">auto-orbit ▸</button>
  </div>
  <div class="stat"><span>cubes <b id="cubeCount">—</b></span><span>sea state <b id="seaState">3</b></span></div>
</div>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* ══════════════════════════════════════════════════════════════
   0 · helpers
   ══════════════════════════════════════════════════════════════ */
let _seed = 20250714;
const rnd = () => { _seed = (_seed * 1664525 + 1013904223) >>> 0; return _seed / 4294967296; };
const R   = (a, b) => a + rnd() * (b - a);
const Ri  = (a, b) => Math.floor(a + rnd() * (b - a + 1));
const pick = arr => arr[Math.floor(rnd() * arr.length)];
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const sstep = (a, b, x) => { const t = clamp((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t); };

// shader colours must bypass sRGB→linear conversion, or the sky/sea come out blackish
const rawC = hex => new THREE.Color().setStyle(hex, THREE.LinearSRGBColorSpace);

/* ══════════════════════════════════════════════════════════════
   1 · renderer / scene / camera
   ══════════════════════════════════════════════════════════════ */
const canvas = document.getElementById('scene');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const scene = new THREE.Scene();
const FOGK = 0.0046;
scene.fog = new THREE.FogExp2(rawC('#e0ab7c'), FOGK);

const camera = new THREE.PerspectiveCamera(48, innerWidth / innerHeight, 0.6, 1400);
camera.position.set(54, 34, 84);

const controls = new OrbitControls(camera, canvas);
controls.target.set(6, 10, -4);
controls.enableDamping = true;
controls.dampingFactor = 0.055;
controls.minDistance = 14;
controls.maxDistance = 210;
controls.maxPolarAngle = 1.34;
controls.minPolarAngle = 0.18;
controls.panSpeed = 0.8;
controls.rotateSpeed = 0.75;

/* ══════════════════════════════════════════════════════════════
   2 · the voxel builder — one InstancedMesh per builder
   ══════════════════════════════════════════════════════════════ */
const matSolid  = new THREE.MeshLambertMaterial({ color: 0xffffff });
const matSail   = new THREE.MeshLambertMaterial({ color: 0xffffff, side: THREE.DoubleSide });
const matGlowW  = new THREE.MeshBasicMaterial({ color: 0xffffff });   // windows, lamps
const matGlowH  = new THREE.MeshBasicMaterial({ color: 0xffffff });   // lighthouse lamp
const matFoam   = new THREE.MeshBasicMaterial({ color: 0xeaf4f7, transparent: true, opacity: .8, depthWrite: false });

let CUBE_TOTAL = 0;

class Vox {
  constructor(mat, { cast = true, receive = true, jitter = 0.045 } = {}) {
    this.mat = mat; this.items = []; this.cast = cast; this.receive = receive; this.jitter = jitter;
  }
  add(x, y, z, color, o = {}) {
    this.items.push([x, y, z, color, o]);
    if (!o.quiet) CUBE_TOTAL++;
  }
  box(x0, x1, y0, y1, z0, z1, c, o = {}) {
    for (let x = x0; x <= x1; x++) for (let y = y0; y <= y1; y++) for (let z = z0; z <= z1; z++) this.add(x, y, z, c, o);
  }
  cyl(cx, cz, r, y0, y1, c, o = {}) {
    const R0 = Math.ceil(r);
    for (let x = -R0; x <= R0; x++) for (let z = -R0; z <= R0; z++) {
      const d = Math.hypot(x, z); if (d > r + 0.35) continue;
      if (d > r - 1.05 && rnd() < 0.35) continue;
      this.add(cx + x, Ri(y0, y1), cz + z, c, o);
    }
  }
  line(a, b, c, o = {}) {
    const size = o.size ?? 0.3;
    const n = Math.max(1, Math.round(a.distanceTo(b) / Math.max(0.35, size)));
    const p = new THREE.Vector3();
    for (let i = 0; i <= n; i++) { p.copy(a).lerp(b, i / n); this.add(p.x, p.y, p.z, c, { ...o, sx: size, sy: size, sz: size }); }
  }
  curve(a, b, sag, c, o = {}) {
    const size = o.size ?? 0.32, n = Math.max(2, Math.round(a.distanceTo(b)));
    const p = new THREE.Vector3();
    for (let i = 0; i <= n; i++) {
      const u = i / n; p.copy(a).lerp(b, u); p.y -= sag * 4 * u * (1 - u);
      this.add(p.x, p.y, p.z, c, { ...o, sx: size, sy: size, sz: size });
    }
  }
  build(name) {
    if (!this.items.length) return null;
    const geo = new THREE.BoxGeometry(1, 1, 1);
    const im = new THREE.InstancedMesh(geo, this.mat, this.items.length);
    const d = new THREE.Object3D(), col = new THREE.Color();
    let i = 0;
    for (const [x, y, z, c, o] of this.items) {
      d.position.set(x, y, z);
      d.rotation.set(o.rx || 0, o.ry || 0, o.rz || 0);
      d.scale.set(o.sx ?? 1, o.sy ?? 1, o.sz ?? 1);
      d.updateMatrix();
      im.setMatrixAt(i, d.matrix);
      col.setHex(c);
      if (this.jitter) col.offsetHSL(0, 0, (rnd() - 0.5) * this.jitter);
      im.setColorAt(i, col);
      i++;
    }
    im.instanceMatrix.needsUpdate = true;
    if (im.instanceColor) im.instanceColor.needsUpdate = true;
    im.castShadow = this.cast; im.receiveShadow = this.receive;
    im.frustumCulled = false;
    if (name) im.name = name;
    return im;
  }
}

/* ══════════════════════════════════════════════════════════════
   3 · sky dome (gradient + sun bloom + procedural stars)
   ══════════════════════════════════════════════════════════════ */
const skyU = {
  uTop:    { value: rawC('#3a6090') },
  uHor:    { value: rawC('#f4b978') },
  uSunCol: { value: rawC('#ffd9a0') },
  uSunDir: { value: new THREE.Vector3(-0.42, 0.24, -0.88) },
  uNight:  { value: 0 }, uTime: { value: 0 }
};
const sky = new THREE.Mesh(
  new THREE.SphereGeometry(600, 32, 24),
  new THREE.ShaderMaterial({
    uniforms: skyU, side: THREE.BackSide, depthWrite: false, fog: false,
    vertexShader: `varying vec3 vD; void main(){ vD = normalize(position); gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
    fragmentShader: `
      varying vec3 vD;
      uniform vec3 uTop,uHor,uSunCol,uSunDir; uniform float uNight,uTime;
      float h31(vec3 p){ return fract(sin(dot(p,vec3(17.3,31.7,43.1)))*43758.5453); }
      void main(){
        float y = vD.y;
        vec3 c = mix(uHor, uTop, smoothstep(-0.02, 0.55, y));
        float band = exp(-pow(y*7.0,2.0));
        c = mix(c, uHor*1.12, band*0.45);
        float d = max(dot(normalize(vD), normalize(uSunDir)), 0.0);
        c += uSunCol*pow(d,42.0)*0.85*(1.0-uNight);
        c += uSunCol*pow(d,7.0)*0.13*(1.0-uNight);
        vec3 sp = floor(vD*190.0);
        float n = h31(sp);
        float st = smoothstep(0.9972,1.0,n)*smoothstep(0.04,0.4,y);
        st *= 0.55+0.45*sin(uTime*2.4+n*90.0);
        c += vec3(0.92,0.96,1.0)*st*uNight*1.5;
        gl_FragColor = vec4(c,1.0);
      }`
  })
);
sky.frustumCulled = false;
scene.add(sky);

/* ══════════════════════════════════════════════════════════════
   4 · terrain function (shared by land build + water shading)
   ══════════════════════════════════════════════════════════════ */
const Q = { edgeX: 14, top: 8, surf: 9, z0: -24, z1: 26 };  // granite quay

function shoreX(z) {
  let e;
  if (z < -22)      e = 17 + 3.0 * Math.sin(z * 0.16) + 1.4 * Math.sin(z * 0.041);
  else if (z < -12) { const u = (z + 22) / 10; e = 17 + 13 * sstep(0, 1, u); }
  else if (z < 16)  e = 30 + 2.2 * Math.sin(z * 0.19 + 1.1);
  else if (z < 26)  { const u = (z - 16) / 10; e = 30 - 8.5 * sstep(0, 1, u); }
  else              e = 21.5 + 3.2 * Math.sin(z * 0.13 + 2.0);
  if (z >= Q.z0 && z <= Q.z1) e = Math.min(e, 15);           // the quay replaces the shore here
  return e;
}

function landH(x, z) {
  const e = shoreX(z);
  if (x < e + 0.5) return null;
  const d = x - e;
  let h = 2 + 9 * Math.pow(clamp(d / 20, 0, 1), 0.7)
        + 2.0 * Math.sin(x * 0.107 + 0.6) * Math.cos(z * 0.081 + 1.2)
        + 1.1 * Math.sin(x * 0.24 - z * 0.16);
  if (z >= Q.z0 && z <= Q.z1) {
    if (x <= 34) h = 8;
    else h = Math.max(h, 8 + Math.min(7, (x - 34) * 0.48));
  }
  return 2 * Math.max(2, Math.round(h / 2));
}

/* ══════════════════════════════════════════════════════════════
   5 · the sea — one instanced grid, waves & foam in GLSL
   ══════════════════════════════════════════════════════════════ */
const GMIN = -60, GMAX = 60, GSTEP = 2, GN = (GMAX - GMIN) / GSTEP + 1;   // 61×61

const isLand = [];
for (let iz = 0; iz < GN; iz++) {
  isLand[iz] = [];
  for (let ix = 0; ix < GN; ix++) isLand[iz][ix] = landH(GMIN + ix * GSTEP, GMIN + iz * GSTEP) !== null;
}
// cheap chamfer distance-to-shore transform, used for shore breakers
const dist = [];
for (let iz = 0; iz < GN; iz++) {
  dist[iz] = [];
  for (let ix = 0; ix < GN; ix++) dist[iz][ix] = isLand[iz][ix] ? 0 : 1e4;
}
for (let pass = 0; pass < 2; pass++) {
  for (let iz = 0; iz < GN; iz++) for (let ix = 0; ix < GN; ix++) {
    for (let dz = -1; dz <= 1; dz++) for (let dx = -1; dx <= 1; dx++) {
      const a = iz + dz, b = ix + dx;
      if (a < 0 || b < 0 || a >= GN || b >= GN) continue;
      const step = (dx && dz) ? 1.42 : 1;
      const v = dist[a][b] + step;
      if (v < dist[iz][ix]) dist[iz][ix] = v;
    }
  }
}

const SHIP_X = 4, SHIP_B = 5.5, SHIP_Z0 = -14, SHIP_Z1 = 14;
function rectDist(x, z, x0, x1, z0, z1) {
  const dx = Math.max(x0 - x, 0, x - x1), dz = Math.max(z0 - z, 0, z - z1);
  return Math.hypot(dx, dz);
}

const wPos = [], wDepth = [], wFoam = [], wShade = [];
for (let iz = 0; iz < GN; iz++) for (let ix = 0; ix < GN; ix++) {
  if (isLand[iz][ix]) continue;
  const x = GMIN + ix * GSTEP, z = GMIN + iz * GSTEP;
  const dl = dist[iz][ix] * GSTEP;
  const depth = clamp(dl / 34, 0, 1);

  let foam = clamp(1.35 - dl / 5.5, 0, 1);
  const dHull = rectDist(x, z, SHIP_X - SHIP_B, SHIP_X + SHIP_B, SHIP_Z0, SHIP_Z1);
  foam = Math.max(foam, clamp(1 - dHull / 4, 0, 1) * 0.9);
  const dPier = rectDist(x, z, Q.edgeX, Q.edgeX + 2, Q.z0, Q.z1);
  foam = Math.max(foam, clamp(1 - dPier / 2.6, 0, 1) * 0.7);
  foam += 0.16 * clamp(Math.sin(x * 0.41) * Math.cos(z * 0.33 + x * 0.11) + 0.35, 0, 1);

  let shade = 0;
  shade = Math.max(shade, (1 - clamp(dHull / 7.5, 0, 1)) * 0.55);      // ship's belly
  shade = Math.max(shade, (1 - clamp(dPier / 6.5, 0, 1)) * 0.42);      // quay
  const back = landH(x - 17, z);                                        // town cliffs lie west of the sun
  if (back !== null) shade = Math.max(shade, clamp((back - 6) / 9, 0, 1) * 0.34);
  shade = Math.max(shade, (1 - clamp(rectDist(x, z, 15, 26, -38, -24) / 8, 0, 1)) * 0.3);

  wPos.push(x, -0.5, z);
  wDepth.push(depth); wFoam.push(clamp(foam, 0, 1)); wShade.push(clamp(shade, 0, 1));
}
const WN = wPos.length / 3;
const waterU = {
  uTime: { value: 0 }, uSun: { value: new THREE.Vector3(-0.42, 0.24, -0.88) },
  uDeep: { value: rawC('#17414f') }, uShallow: { value: rawC('#3a8085') },
  uFoamC: { value: rawC('#eef4f6') }, uFogC: { value: rawC('#e0ab7c') },
  uSunC: { value: rawC('#ffd9a0') }, uSunI: { value: 1.0 }, uFogD: { value: FOGK }
};
const waterGeo = new THREE.BoxGeometry(2.02, 2.4, 2.02);
const f32 = a => new THREE.Float32BufferAttribute(a, 1);
waterGeo.setAttribute('aDepth', new THREE.InstancedBufferAttribute(new Float32Array(wDepth), 1));
waterGeo.setAttribute('aFoam',  new THREE.InstancedBufferAttribute(new Float32Array(wFoam), 1));
waterGeo.setAttribute('aShade', new THREE.InstancedBufferAttribute(new Float32Array(wShade), 1));
const waterMat = new THREE.ShaderMaterial({
  uniforms: waterU, fog: false,
  vertexShader: `
    attribute float aDepth, aFoam, aShade;
    varying float vD, vF, vS, vView; varying vec3 vW, vN;
    uniform float uTime;
    void main(){
      vD=aDepth; vF=aFoam; vS=aShade; vN=normalize(normal);
      vec4 wp = modelMatrix * instanceMatrix * vec4(position,1.0);
      float t = uTime;
      float w = sin(wp.x*0.16 + t*1.05)*0.44
              + cos(wp.z*0.215 - t*0.82)*0.34
              + sin((wp.x+wp.z)*0.098 + t*1.65)*0.30
              + sin((wp.x-wp.z)*0.31 + t*2.4)*0.10;
      wp.y += w;
      vW = wp.xyz;
      vec4 mv = viewMatrix * wp;
      vView = -mv.z;
      gl_Position = projectionMatrix * mv;
    }`,
  fragmentShader: `
    precision highp float;
    varying float vD, vF, vS, vView; varying vec3 vW, vN;
    uniform vec3 uDeep, uShallow, uFoamC, uFogC, uSunC, uSun;
    uniform float uSunI, uTime, uFogD;
    float hs(vec2 p){ return fract(sin(dot(p,vec2(19.7,47.3)))*2837.1); }
    void main(){
      vec3 N = normalize(vN);
      float up = max(N.y, 0.0);
      vec3 L = normalize(uSun);
      float ndl = max(dot(N, L), 0.0);
      vec3 col = mix(uShallow, uDeep, vD) * (0.50 + 0.52*ndl) ;
      vec3 V = normalize(cameraPosition - vW);
      vec3 Hh = normalize(L + V);
      col += uSunC * pow(max(dot(N,Hh),0.0), 65.0) * 0.55 * uSunI * up;
      float cell = hs(floor(vW.xz*0.5));
      float spark = smoothstep(0.87,0.995,cell)*(0.5+0.5*sin(uTime*3.1+cell*44.0))*up*pow(ndl,1.5);
      col += uSunC * spark * 0.55 * uSunI;
      float wob = 0.55+0.45*sin(uTime*2.3 + vW.x*0.5 + vW.z*0.7);
      float f = clamp(vF*wob*1.25, 0.0, 1.0);
      col = mix(col, uFoamC, f*0.82);
      col *= (1.0 - vS*0.55);
      float fd = uFogD*vView;
      col = mix(col, uFogC, clamp(1.0-exp(-fd*fd), 0.0, 1.0));
      gl_FragColor = vec4(col, 1.0);
    }`
});
const water = new THREE.InstancedMesh(waterGeo, waterMat, WN);
{
  const d = new THREE.Object3D();
  for (let i = 0; i < WN; i++) { d.position.set(wPos[i*3], wPos[i*3+1], wPos[i*3+2]); d.updateMatrix(); water.setMatrixAt(i, d.matrix); }
  water.instanceMatrix.needsUpdate = true;
}
water.frustumCulled = false;
scene.add(water);

// horizon filler so the sea reads past the grid edge
const deepFill = new THREE.Mesh(
  new THREE.PlaneGeometry(1600, 1600),
  new THREE.MeshBasicMaterial({ color: rawC('#17414f') })
);
deepFill.rotation.x = -Math.PI / 2; deepFill.position.y = -1.75;
scene.add(deepFill);

/* ══════════════════════════════════════════════════════════════
   6 · lights
   ══════════════════════════════════════════════════════════════ */
const hemi = new THREE.HemisphereLight(0xcfe0e6, 0x8a6f52, 0.55);
scene.add(hemi);
const sun = new THREE.DirectionalLight(0xffd9a0, 1.05);
sun.position.set(-42, 24, -88);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
Object.assign(sun.shadow.camera, { left: -95, right: 95, top: 95, bottom: -95, near: 1, far: 340 });
sun.shadow.bias = -0.0014; sun.shadow.normalBias = 0.42;
sun.shadow.camera.updateProjectionMatrix();
scene.add(sun, sun.target);
const fill = new THREE.DirectionalLight(0xbfd8e6, 0.3);
fill.position.set(60, 30, 70);
scene.add(fill);
const beacon = new THREE.SpotLight(0xffe9c0, 0, 300, Math.PI * 0.05, 0.45, 1);
beacon.castShadow = false;
scene.add(beacon);

/* ══════════════════════════════════════════════════════════════
   7 · terrain
   ══════════════════════════════════════════════════════════════ */
const land = new Vox(matSolid);
for (let z = -48; z <= 48; z += 2) for (let x = 0; x <= 52; x += 2) {
  const h = landH(x, z);
  if (h === null) continue;
  for (let y = -4; y <= h; y += 2) {
    let c;
    if (y === h) c = h <= 2 ? 0xbfa877 : pick([0x6f8f4e, 0x7a9a55, 0x66844a, 0x84a05c]);
    else if (y >= h - 2 && h > 2) c = pick([0x8b7c68, 0x7d7160, 0x968874]);
    else if (y <= 0) c = 0x494338;
    else c = pick([0x7c6a56, 0x8a7560, 0x6d5e4e]);
    if (y === h && h > 6 && rnd() < 0.14) c = pick([0x9a9172, 0x849055]); // rock showing on the hill
    land.add(x, y, z, c);
  }
}

/* ══════════════════════════════════════════════════════════════
   8 · quay, harbour walls, jetty
   ══════════════════════════════════════════════════════════════ */
const H = new Vox(matSolid);
const GRAN = [0x8d8578, 0x968d7f, 0x7f7769, 0xa39a8b];

for (let z = Q.z0; z <= Q.z1; z += 2) {
  for (let y = -4; y <= 6; y += 2) H.add(Q.edgeX, y, z, pick(GRAN));          // wall face
  H.add(Q.edgeX + 1, 6, z, pick(GRAN)); H.add(Q.edgeX + 1, 4, z, pick(GRAN)); // backing
  if ((z - Q.z0) % 12 === 0) { H.add(Q.edgeX - 1, 10, z, 0x5c4430); H.add(Q.edgeX - 1, 11, z, 0x6a4f38); } // fender timber
}
for (let x = Q.edgeX; x <= 34; x += 2) for (let z = Q.z0; z <= Q.z1; z += 2)
  H.add(x, Q.top, z, x <= Q.edgeX + 1 ? pick(GRAN) : pick([0x8a8175, 0x958b7d, 0x7e7567]));
// slipway steps down to the water at the south end
for (let i = 0; i < 5; i++) H.box(Q.edgeX - i, Q.edgeX - i, 8 - i, 8 - i, -20 + i, -19 + i, pick(GRAN));

const S = new Vox(matSolid);   // 1-unit props (bollards, crates, barrels, people …)
const W = 0x8a6a3f, DW = 0x4a3624, IRON = 0x3c4147;

function bollard(x, z) { S.cyl(x, z, 1, Q.surf, Q.surf + 2, DW); S.add(x, Q.surf + 3, z, 0x9a9082); }
for (let z = Q.z0 + 4; z <= Q.z1 - 2; z += 9) bollard(Q.edgeX + 2, z);
bollard(Q.edgeX + 2, 18);

function crate(x, y, z, s = 3, c = 0x9a7a4e) {
  S.box(x, x + s - 1, y, y + s - 1, z, z + s - 1, c);
  for (let i = 0; i < s; i++) { S.add(x + i, y, z, 0x6e5434, { sz: 1, sx: 1 }); }
  S.box(x, x + s - 1, y, y, z, z, 0x775c39);
}
function barrel(x, y, z) {
  S.cyl(x, z, 1.4, y, y + 2, 0x6b4a2f);
  S.add(x, y + 1, z, 0x8a6a3f, { sy: 1, sx: 3, sz: 3, quiet: true });
  for (let i = -1; i <= 1; i += 2) S.add(x + i, y + 1, z, 0x2f353b);
}
function coil(x, y, z) { for (let a = 0; a < 8; a++) S.add(x + Math.cos(a / 8 * Math.PI * 2) * 1.6, y, z + Math.sin(a / 8 * Math.PI * 2) * 1.6, 0xc9a96d); }

// stacks of cargo on the apron
let cz = Q.z0 + 8;
while (cz < Q.z1 - 4) {
  const bx = R(19, 30) | 0;
  crate(bx, Q.surf, cz | 0, pick([3, 3, 4]));
  if (rnd() < 0.55) crate(bx + (rnd() < .5 ? 4 : 0), Q.surf, (cz | 0) + 4, 3);
  if (rnd() < 0.4) barrel(bx + 6, Q.surf, cz | 0);
  cz += 8 + rnd() * 5;
}
for (let i = 0; i < 6; i++) coil(R(18, 32) | 0, Q.surf, Ri(Q.z0 + 3, Q.z1 - 3));
for (let i = 0; i < 5; i++) barrel(R(18, 31) | 0, Q.surf, Ri(Q.z0 + 3, Q.z1 - 3));

// lampposts
const glowW = [];
function lamp(x, z) {
  S.box(x, x, Q.surf, Q.surf + 4, z, z, IRON);
  S.add(x, Q.surf + 3, z, 0x2f353b, { sx: 3, sy: .6, sz: .6 });
  S.add(x, Q.surf + 5, z, 0x2f353b, { sx: 1.4, sy: 1.2, sz: 1.4, quiet: true });
  const g = new Vox(matGlowW, { cast: false, receive: false });
  g.add(x, Q.surf + 5, z, 0xffc25e, { sx: 1.15, sy: 1.1, sz: 1.15 });
  glowW.push(g.build());
}
for (let z = Q.z0 + 6; z <= Q.z1 - 4; z += 11) lamp(Q.edgeX + 4, z);
lamp(17, 20);

// wooden jetty reaching south-east out of the apron
for (let x = 10; x <= 14; x += 1) for (let z = 17; z <= 25; z += 1) S.add(x, 9, z, pick([0x8b6d45, 0x7a5d3a]), { sz: 1 });
for (let z = 17; z <= 25; z += 4) for (let x = 10; x <= 14; x += 4) for (let y = -2; y <= 8; y += 1) S.add(x, y, z, 0x54402c, { quiet: true });
for (let z = 17; z <= 25; z += 2) S.add(10, 10, z, 0x5c4430);
crate(12, 10, 22, 2);

/* ══════════════════════════════════════════════════════════════
   9 · town: warehouse, cottages, chapel, windmill
   ══════════════════════════════════════════════════════════════ */
const smokeSources = [];

function cottage(cx, cz, w, d, h, wall, roof, opts = {}) {
  const gy = landH(cx, cz); if (gy === null) return;
  const y0 = gy + 1;
  const B = new Vox(matSolid);
  for (let x = cx - w / 2; x <= cx + w / 2; x++) for (let z = cz - d / 2; z <= cz + d / 2; z++) {
    const edge = (x === cx - w / 2 || x === cx + w / 2 || z === cz - d / 2 || z === cz + d / 2);
    if (!edge) { B.add(x, y0, z, 0x5b4331); continue; }
    B.add(x, y0, z, 0x4a3624);
    for (let y = y0 + 1; y <= y0 + h; y++) B.add(x, y, z, wall);
  }
  // gabled roof, ridge along z
  for (let x = cx - w / 2 - 1; x <= cx + w / 2 + 1; x++) {
    const t = Math.abs(x - cx) / (w / 2 + 1);
    const ry = Math.round(y0 + h + (1 - t) * Math.max(2, w / 2));
    for (let z = cz - d / 2 - 1; z <= cz + d / 2 + 1; z++) {
      B.add(x, ry, z, pick([roof, roof, 0x59402f]));
      if (ry > y0 + h) for (let yy = ry - 1; yy >= y0 + h + 1; yy--) B.add(x, yy, z, 0x6e5a44);
    }
  }
  // chimney + smoke
  if (rnd() < 0.8) {
    const chx = cx + (rnd() < .5 ? -w / 2 + 1 : w / 2 - 1), chz = Math.round(cz - d / 4);
    B.box(chx, chx, y0 + h, y0 + h + 4, chz, chz, 0x7c5c46);
    smokeSources.push(new THREE.Vector3(chx, y0 + h + 4.6, chz));
  }
  // glowing windows on the seaward face
  const G = new Vox(matGlowW, { cast: false, receive: false });
  for (let z = cz - d / 2 + 1; z <= cz + d / 2 - 1; z += 2) for (let y = y0 + 2; y <= y0 + h - 1; y += 2) {
    if (rnd() < 0.72) G.add(cx - w / 2 - 1, y, z, 0xffb84d);
    if (rnd() < 0.6)  G.add(cx + w / 2 + 1, y, z, 0xffb84d);
    B.add(cx - w / 2 - 1, y, z, 0x382b1f, { sx: .2, quiet: true });
  }
  B.add(cx - w / 2 - 1, y0 + 1, cz, 0x3d2a18, { sz: 2 });   // door
  return { mesh: B.build(), glow: G.build() };
}

// the big brick bonded warehouse facing the quay
{
  const B = new Vox(matSolid), G = new Vox(matGlowW, { cast: false, receive: false });
  const x0 = 32, x1 = 40, z0 = -10, z1 = 8, y0 = 9, hh = 11;
  for (let z = z0; z <= z1; z++) for (let y = y0; y <= y0 + hh; y++)
    for (let x = x0; x <= x1; x++) {
      const edge = (x === x0 || x === x1 || z === z0 || z === z1);
      if (!edge) { B.add(x, y, z, 0x513626); continue; }
      B.add(x, y, z, pick([0x8f4536, 0x94493a, 0x874334]));
    }
  for (let x = x0; x <= x1; x++) for (let z = z0 - 1; z <= z1 + 1; z++)
    B.add(x, y0 + hh + 1, z, 0x3d3a38);
  for (let x = x0 - 1; x <= x1 + 1; x++) {                     // shallow pitched roof
    const t = Math.abs(x - (x0 + x1) / 2) / ((x1 - x0) / 2 + 1);
    for (let z = z0 - 1; z <= z1 + 1; z++) B.add(x, Math.round(y0 + hh + 1 + (1 - t) * 3), z, pick([0x403d3b, 0x4a4643]));
  }
  B.box(x0 - 1, x0 - 1, y0, y0 + 4, -2, 2, 0x4a3520);          // loading doors
  B.add(x0 - 1, y0 + 6, 0, 0x2f2a26, { sz: 4, sy: 1 });
  B.add(x0 - 2, y0 + 9, 0, 0x6b5a3f, { sx: 1, sy: 2, sz: 8, quiet: true });  // loading arm
  B.box(x0 - 1, x0 - 1, y0, y0 + 1, -6, -4, 0x6e5c44);          // goods winch
  for (let z = z0 + 1; z <= z1 - 1; z += 3) for (let y = y0 + 7; y <= y0 + 9; y += 2)
    if (rnd() < 0.75) G.add(x0 - 1, y, z, 0xffb84d);
  smokeSources.push(new THREE.Vector3(x1 - 2, y0 + hh + 5, z0 + 2));
  B.box(x1 - 2, x1 - 2, y0 + hh, y0 + hh + 4, z0 + 2, z0 + 2, 0x7c5c46);
  H.add(...[0, 0, 0].map(() => 0)); // no-op guard
  scene.add(B.build()); scene.add(G.build());
  glowW.push(G.build.name = 'wh');
}

// cottages climbing the hill
const cottageSpecs = [
  [38, -18, 7, 6, 4, 0xe0d3bb, 0x8c4034], [44, -12, 6, 6, 4, 0xb9c6c4, 0x46586a],
  [40, -2, 6, 6, 5, 0xe6cfa9, 0x7b4a30], [46, 6, 7, 6, 4, 0xd8cdb6, 0x5b6f4a],
  [37, 14, 6, 6, 5, 0xf0e2c6, 0x8c4034], [44, 20, 6, 6, 4, 0xa8bcc4, 0x3f4f60],
  [50, -4, 6, 6, 5, 0xd3bd9d, 0x6d4630], [48, 12, 7, 6, 4, 0xe2d8c4, 0x77563c],
  [36, 24, 6, 6, 4, 0xced9cf, 0x485c6d], [50, 26, 6, 6, 4, 0xe8d8bd, 0x8c5a34]
];
const townGlows = [];
for (const [x, z, w, d, h, wall, roof] of cottageSpecs) {
  const c = cottage(x, z, w, d, h, wall, roof);
  if (c.mesh) scene.add(c.mesh);
  if (c.glow) scene.add(c.glow);
}

// chapel on the ridge
{
  const B = new Vox(matSolid), G = new Vox(matGlowW, { cast: false, receive: false });
  const gy = landH(46, -26) ?? 10, y0 = gy + 1;
  for (let x = 43; x <= 49; x++) for (let z = -29; z <= -23; z++) {
    const edge = x === 43 || x === 49 || z === -29 || z === -23;
    if (!edge) { B.add(x, y0, z, 0x5a4a3a); continue; }
    for (let y = y0; y <= y0 + 6; y++) B.add(x, y, z, pick([0xd9d2c4, 0xcac2b2]));
    B.add(x, y0, z, 0x8b8272);
  }
  for (let x = 42; x <= 50; x++) for (let z = -30; z <= -22; z++) {
    const t = Math.abs(x - 46) / 4;
    B.add(x, Math.round(y0 + 6 + (1 - t) * 3), z, pick([0x4d5c6b, 0x3f4d5a]));
  }
  for (let y = y0 + 7; y <= y0 + 14; y++) B.add(46, y, -26, y % 2 ? 0xd9d2c4 : 0xcac2b2);
  B.add(46, y0 + 15, -26, 0xe9c86a, { sx: 2.4, sy: .7, sz: 1.1 });
  B.add(46, y0 + 14, -26, 0xe9c86a, { sx: .7, sy: 2.4, sz: 1.1 });
  for (let z = -28; z <= -24; z += 2) G.add(43, y0 + 4, z, 0xffb84d);
  scene.add(B.build()); scene.add(G.build());
}

// windmill on the north promontory — the sails really turn
let millSails = null;
{
  const B = new Vox(matSolid), G = new Vox(matGlowW, { cast: false, receive: false });
  const gy = landH(26, 34) ?? 6, y0 = gy + 1;
  for (let y = 0; y < 9; y++) {
    const r = 3.4 - y * 0.2;
    const R0 = Math.ceil(r);
    for (let x = -R0; x <= R0; x++) for (let z = -R0; z <= R0; z++) {
      const d = Math.hypot(x, z); if (d > r + .3 || d < r - 1.2) continue;
      B.add(26 + x, y0 + y, 34 + z, y > 6 ? 0xa59279 : pick([0x9a8c74, 0x8d7f68]));
    }
  }
  B.box(24, 28, y0 + 9, y0 + 10, 32, 36, 0x5b4431);
  B.add(26, y0 + 11, 34, 0x6b5138, { sx: 2.6, sy: 1.4, sz: 2.6 });
  G.add(26, y0 + 5, 31, 0xffb84d);
  scene.add(B.build()); scene.add(G.build());

  const M = new Vox(matSolid, { jitter: 0.02 });
  for (let a = 0; a < 4; a++) {
    const ang = a / 4 * Math.PI * 2;
    for (let r = 1; r <= 9; r++) {
      const px = Math.cos(ang) * r, py = Math.sin(ang) * r;
      M.add(26 + px, y0 + 11 + py, 34, r < 2 ? 0x6b5138 : 0xd9cfb6, {
        sx: 1.2, sy: 1.2, sz: r % 3 === 0 ? 2.4 : 0.5, rx: ang + Math.PI / 2
      });
    }
  }
  millSails = M.build();
  const g = new THREE.Group();
  g.position.set(26, y0 + 11, 34);
  millSails.position.set(-26, -(y0 + 11), -34);
  g.add(millSails);
  scene.add(g);
  millSails.userData.group = g;
}

// trees
function pine(x, z) {
  const gy = landH(x, z); if (gy === null) return;
  const y0 = gy + 1, h = Ri(5, 9);
  const B = new Vox(matSolid, { jitter: .05 });
  B.box(x, x, y0, y0 + 2, z, z, 0x59422e);
  for (let i = 0; i < h; i++) {
    const r = Math.max(0.5, (h - i) * 0.34);
    const R0 = Math.ceil(r);
    for (let a = -R0; a <= R0; a++) for (let b = -R0; b <= R0; b++) {
      if (Math.hypot(a, b) > r + .3) continue;
      B.add(x + a, y0 + 2 + i, z + b, pick([0x2f5a3e, 0x376343, 0x2b5239]));
    }
  }
  scene.add(B.build());
}
function oak(x, z) {
  const gy = landH(x, z); if (gy === null) return;
  const y0 = gy + 1, h = Ri(3, 5);
  const B = new Vox(matSolid, { jitter: .06 });
  B.box(x, x, y0, y0 + h, z, z, 0x5d4531);
  const r = Ri(3, 4);
  for (let a = -r; a <= r; a++) for (let b = -r; b <= r; b++) for (let c = -2; c <= 2; c++) {
    const d = Math.hypot(a, b * 1.1, c);
    if (d > r + .2 || d < r - 1.4) continue;
    B.add(x + a, y0 + h + 1 + c, z + b, pick([0x5f7b3f, 0x6d884a, 0x4e6b37, 0x7d8f45]));
  }
  scene.add(B.build());
}
[[36, 30], [34, 40], [44, 34], [50, 18], [52, 6], [41, -22], [47, -20], [51, -28],
 [44, 26], [38, -24], [48, -16], [52, 14], [39, 22], [43, 36]].forEach(([x, z]) => rnd() < .55 ? pine(x, z) : oak(x, z));

/* ══════════════════════════════════════════════════════════════
   10 · lighthouse + rotating beam
   ══════════════════════════════════════════════════════════════ */
let beaconLamp = null, beamGroup = null;
{
  const B = new Vox(matSolid);
  for (let a = 0; a < 46; a++) {
    const x = 18 + Ri(0, 8), z = -34 + Ri(0, 8), y = Ri(-4, 6);
    B.add(x, y, z, pick([0x6e6a5e, 0x7b7468, 0x5d594f]), { sx: R(1, 2.2), sy: R(1, 2), sz: R(1, 2.2) });
  }
  const baseY = 6;
  for (let y = baseY; y <= baseY + 18; y++) {
    const r = 3.6 - (y - baseY) * 0.11;
    const R0 = Math.ceil(r);
    const band = Math.floor((y - baseY) / 3) % 2;
    for (let a = -R0; a <= R0; a++) for (let b = -R0; b <= R0; b++) {
      const d = Math.hypot(a, b); if (d > r + .35 || d < r - 1.1) continue;
      B.add(22 + a, y, -30 + b, band ? 0xefe6d8 : pick([0xc04a3b, 0xb8443a]));
    }
  }
  B.cyl(22, -30, 4.2, baseY + 18, baseY + 18, 0x31373d);
  for (let a = 0; a < 12; a++) B.add(22 + Math.cos(a / 12 * Math.PI * 2) * 3.4, baseY + 20, -30 + Math.sin(a / 12 * Math.PI * 2) * 3.4, 0x31373d, { sx: .4, sz: .4 });
  B.box(21, 23, baseY + 19, baseY + 21, -31, -29, 0x2b3136);
  for (let y = baseY + 21; y <= baseY + 24; y++) B.add(22, y, -30, y % 2 ? 0x424a52 : 0x2b3136, { sx: 3, sy: 1, sz: 3 });
  scene.add(B.build());

  const gl = new Vox(matGlowH, { cast: false, receive: false });
  gl.add(22, baseY + 20, -30, 0xfff1c8, { sx: 2.6, sy: 2.4, sz: 2.6 });
  beaconLamp = gl.build(); scene.add(beaconLamp);

  const cone = new THREE.ConeGeometry(6.5, 120, 16, 1, true);
  cone.translate(0, -60, 0); cone.rotateZ(-Math.PI / 2);
  const beamMat = new THREE.MeshBasicMaterial({ color: 0xffe6b0, transparent: true, opacity: 0, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide });
  beamGroup = new THREE.Group();
  beamGroup.position.set(22, baseY + 20, -30);
  const b1 = new THREE.Mesh(cone, beamMat);
  const b2 = new THREE.Mesh(cone, beamMat); b2.rotation.y = Math.PI;
  beamGroup.add(b1, b2);
  scene.add(beamGroup);
  beacon.position.copy(beamGroup.position);
  beacon.target.position.set(22 - 60, baseY + 16, -30);
  scene.add(beacon.target);

  // keeper's cottage
  const gy = landH(28, -34) ?? 6;
  scene.add(cottage(29, -34, 5, 4, 3, 0xe4dcc8, 0x5d6a55).mesh);
  // rocky shoal with breakers
  const Rk = new Vox(matSolid);
  for (let i = 0; i < 16; i++) Rk.add(11 + Ri(0, 5), Ri(-2, 3), -38 + Ri(0, 6), pick([0x556055, 0x4d5851, 0x626b5f]), { sx: R(1, 2.4), sy: R(1, 2), sz: R(1, 2.4) });
  scene.add(Rk.build());
}

/* ══════════════════════════════════════════════════════════════
   11 · moorings, derrick crane, the rowboat
   ══════════════════════════════════════════════════════════════ */
{
  const M = new Vox(matSolid, { jitter: .03 });
  const ROPE = 0xc9a96d;
  // derrick crane
  M.line(new THREE.Vector3(18, 9, -3), new THREE.Vector3(17, 18, -1), DW, { size: .8 });
  M.line(new THREE.Vector3(18, 9, 3), new THREE.Vector3(17, 18, 1), DW, { size: .8 });
  M.line(new THREE.Vector3(17, 17, 0), new THREE.Vector3(9, 16.5, 0), 0x7c6039, { size: .8 });
  M.line(new THREE.Vector3(17, 18, -1), new THREE.Vector3(9, 16.5, 0), IRON, { size: .35 });
  M.add(17, 9, 0, 0x5c4430, { sx: 2, sz: 6 });
  scene.add(M.build());

  // swinging cargo — the load and its tackle live in one pivoting group
  const swing = new THREE.Group();
  swing.position.set(10, 16.5, 0);
  const L = new Vox(matSolid, { jitter: .02 });
  L.line(new THREE.Vector3(0, 0, 0), new THREE.Vector3(0, -6, 0), 0x8a7a52, { size: .3 });
  L.box(-2, 1, -6, -3, -2, 1, 0x9a7a4e);
  L.box(-2, 1, -6, -6, -2, 1, 0x775c39);
  L.add(0, -4, -2, 0x6e5434, { sx: 3, sy: .5, sz: .5 });
  L.add(0, -4, 1, 0x6e5434, { sx: 3, sy: .5, sz: .5 });
  swing.add(L.build());
  scene.add(swing);
  swing.userData.kind = 'swing';

  // hawsers from the quay to the ship
  const P = new Vox(matSolid, { jitter: .03 });
  P.curve(new THREE.Vector3(16, 12, -20), new THREE.Vector3(6.5, 10, -12), 0.55, ROPE);
  P.curve(new THREE.Vector3(16, 12, -11), new THREE.Vector3(6.5, 10, -6), 0.4, ROPE);
  P.curve(new THREE.Vector3(16, 12, 14), new THREE.Vector3(6.5, 10, 12), 0.6, ROPE);
  P.curve(new THREE.Vector3(16, 11, 19), new THREE.Vector3(7.5, 9, 13), 0.5, ROPE);
  // anchor cable slipping into the bay
  P.curve(new THREE.Vector3(4, 10, -15), new THREE.Vector3(-6, -1, -26), 0.9, 0x8c784f, { size: .38 });
  // gangplank
  for (let i = 0; i < 4; i++) P.add(11 + i * 1, 8 + i * 0.35, 10, pick([0x9a7a4e, 0x8a6a44]), { sz: 2 });
  P.line(new THREE.Vector3(11, 10.5, 9), new THREE.Vector3(14.5, 12, 9), DW, { size: .3 });
  P.line(new THREE.Vector3(11, 10.5, 11), new THREE.Vector3(14.5, 12, 11), DW, { size: .3 });
  scene.add(P.build());
}

/* ══════════════════════════════════════════════════════════════
   12 · THE SHIP — "the Meridian"
   ══════════════════════════════════════════════════════════════ */
const shipGroup = new THREE.Group();
shipGroup.position.set(SHIP_X, 0, 0);
scene.add(shipGroup);

function beamAt(z) {
  if (z <= -6) { const u = clamp((z + 14) / 8, 0, 1); return 5.4 * (0.14 + 0.86 * Math.pow(u, 0.42)); }
  if (z >= 8)  { const u = clamp((14 - z) / 6, 0, 1); return 5.4 * (0.40 + 0.60 * Math.pow(u, 0.35)); }
  return 5.4;
}
function sheerY(z) {
  let t = 8;
  if (z < -6) t = 8 + 3.1 * Math.pow(1 - (z + 14) / 8, 1.55);
  if (z > 10) t = 8 + 1.5 * Math.pow((z - 10) / 4, 2);
  return t;
}
function keelY(z) {
  let k = -4;
  if (z < -6) k = -4 + 3.3 * Math.pow(1 - (z + 14) / 8, 1.9);
  if (z > 10) k = -4 + 1.8 * Math.pow((z - 10) / 4, 2);
  return k;
}

{
  const B = new Vox(matSolid, { jitter: .05 });
  const G = new Vox(matGlowW, { cast: false, receive: false });
  const F = new Vox(matFoam, { cast: false, receive: false, jitter: .01 });
  const Ws = new Vox(matSail, { jitter: .02 });

  // ---- hull ----
  for (let z = SHIP_Z0; z <= SHIP_Z1; z++) {
    const b = Math.max(1, Math.round(beamAt(z)));
    const yT = Math.round(sheerY(z)), yB = Math.round(keelY(z));
    for (let y = yB; y <= yT; y++) for (const s of [-1, 1]) {
      const x = s * b;
      if (x === 0 && s < 0) continue;
      let c;
      if (y <= -1) c = 0x211a15;
      else if (y === yT) c = 0xc89a4e;
      else if (y === yT - 3) c = 0xc0913f;
      else if (y === yT - 4 || y === yT - 2) c = 0x2c2119;
      else c = pick([0x6b4a2f, 0x71502f, 0x654629]);
      // gun ports
      if (y === yT - 6 && (z + 14) % 3 === 0 && Math.abs(z) > 2 && Math.abs(z) < 10) {
        B.add(x, y, z, 0x14100d); B.add(x, y + 1, z, 0x14100d);
        B.add(x + s * 0.6, y, z, 0x30363c, { sx: .8, sy: .8, sz: .8, quiet: true });
        B.add(x - s * 0.02, y + 2, z, 0xa7814a); continue;
      }
      B.add(x, y, z, c);
    }
    for (let x = -b; x <= b; x++) B.add(x, yB, z, 0x1c1613);          // keel plate
    if (b === 1) B.add(0, yB + 1, z, 0x1c1613);
  }
  // transom
  for (let z = SHIP_Z1; z <= SHIP_Z1 + 1; z++) {
    const b = Math.round(beamAt(SHIP_Z1 - 1));
    for (let y = -2; y <= Math.round(sheerY(SHIP_Z1)); y++)
      for (let x = -b; x <= b; x++) B.add(x, y, z, y >= 5 ? 0xc0913f : 0x2c2119);
  }

  // ---- decks ----
  const DECK = [0x8a6440, 0x946c46, 0x7f5c3b];
  for (let z = -12; z <= 13; z++) for (let x = -Math.round(beamAt(z)) + 1; x <= Math.round(beamAt(z)) - 1; x++)
    B.add(x, 8, z, pick(DECK));
  for (let z = -12; z <= -6; z++) for (let x = -Math.round(beamAt(z)) + 1; x <= Math.round(beamAt(z)) - 1; x++)
    B.add(x, 10, z, pick(DECK));                                     // forecastle
  for (let z = 9; z <= 13; z++) for (let x = -Math.round(beamAt(z)) + 1; x <= Math.round(beamAt(z)) - 1; x++)
    B.add(x, 10, z, pick([0x9c7748, 0x90704a]));                     // poop
  // bulwarks
  for (let z = -6; z <= 8; z++) { const b = Math.round(beamAt(z)); for (const s of [-1, 1]) { B.add(s * b, 9, z, 0x2c2119); B.add(s * b, 10, z, 0xc89a4e); } }
  for (let z = 9; z <= 13; z++) { const b = Math.round(beamAt(z)); for (const s of [-1, 1]) { B.add(s * b, 11, z, 0x2c2119); B.add(s * b, 12, z, 0xc89a4e); } }
  for (let z = -12; z <= -6; z++) { const b = Math.round(beamAt(z)); for (const s of [-1, 1]) { B.add(s * b, 11, z, 0x2c2119); } }

  // ---- stern galleries ----
  for (let y = 10; y <= 13; y++) for (let x = -3; x <= 3; x++) B.add(x, y, SHIP_Z1 + 2, y === 13 ? 0xc89a4e : 0x2f2620);
  for (let x = -3; x <= 3; x += 2) { G.add(x, 11, SHIP_Z1 + 2, 0xffb84d); G.add(x, 12, SHIP_Z1 + 2, 0xffc860); }
  for (const s of [-1, 1]) { G.add(s * 4, 13, SHIP_Z1 + 1, 0xffd08a, { sx: 1.1, sy: 1.2, sz: 1.1 }); B.add(s * 4, 12, SHIP_Z1 + 1, 0x2f2620); }
  B.add(0, 14, SHIP_Z1 + 2, 0xc89a4e, { sx: 6, sy: 1, sz: 1 });

  // ---- figurehead, bow work ----
  B.add(0, 9, -15, 0xe4d8b6, { sx: 1.6, sy: 2.4, sz: 2.2 });
  B.add(0, 11, -16, 0xe4d8b6, { sx: 1, sy: 1, sz: 2, rx: 0.6 });
  for (let z = -14; z >= -17; z--) B.add(0, 11 + (-14 - z) * 0.35, z, 0x876840, { sx: 1.2, sy: 1.2 });
  B.add(0, 14, -18, 0x4d5a3f, { sx: .6, sy: .6, sz: 2 });           // jack
  B.add(0, 15, -18, 0xc94040, { sx: .6, sy: 1.2, sz: 1.6 });
  // anchors
  for (const s of [-1, 1]) {
    const b = Math.round(beamAt(-12));
    B.add(s * (b + 1), 3, -12, 0x343941, { sx: 1, sy: 2, sz: 1 });
    B.add(s * (b + 1), 5, -13, 0x343941, { sx: 1, sz: 2 });
  }

  // ---- masts, yards, rigging ----
  const SPAR = 0x876840, RIG = 0x33281f;
  const masts = [{ z: -7, top: 27, n: 'fore' }, { z: 1, top: 31, n: 'main' }, { z: 10, top: 23, n: 'mizzen' }];
  for (const m of masts) {
    const yStart = m.z === 10 ? 10 : 8;
    for (let y = yStart; y <= m.top; y++) B.add(0, y, m.z, y < 14 ? 0x6f5436 : SPAR, { sx: y < 12 ? 1.5 : 1.1, sz: y < 12 ? 1.5 : 1.1 });
    if (m.n === 'main') for (let a = 0; a < 8; a++) B.add(Math.cos(a / 8 * Math.PI * 2) * 2, 20, m.z + Math.sin(a / 8 * Math.PI * 2) * 2, 0x5c4430, { sx: .8, sz: .8 });
    B.add(0, m.top + 1, m.z, IRON, { sy: 1.6 });
    const yards = m.n === 'main' ? [[16, 17], [21.5, 14], [26, 9.5], [29.5, 6]]
                : m.n === 'fore' ? [[12.5, 14.5], [18, 11.5], [23, 7.5], [26, 5]]
                                 : [[14.5, 12], [19, 8.5], [22, 5]];
    for (const [yy, ww] of yards) B.line(new THREE.Vector3(-ww / 2 - 1.4, Math.round(yy), m.z), new THREE.Vector3(ww / 2 + 1.4, Math.round(yy), m.z), SPAR, { size: .75 });
    // shrouds
    for (const s of [-1, 1]) for (const off of [-2.6, 0, 2.6]) {
      B.line(new THREE.Vector3(0, m.top - 1, m.z + off * 0.35), new THREE.Vector3(s * (beamAt(m.z) + 0.3), yStart + 1, m.z + off), RIG, { size: .24 });
    }
    B.line(new THREE.Vector3(0, m.top, m.z), new THREE.Vector3(0, yStart + 1, m.z + 6), RIG, { size: .24 });
  }
  // stays
  const V = (x, y, z) => new THREE.Vector3(x, y, z);
  B.line(V(0, 15, -18), V(0, 26, -7), RIG, { size: .28 });
  B.line(V(0, 15, -18), V(-4.6, 11, -13), RIG, { size: .22 });
  B.line(V(0, 15, -18), V(4.6, 11, -13), RIG, { size: .22 });
  B.line(V(0, 26, -7), V(0, 21, 1), RIG, { size: .26 });
  B.line(V(0, 30, 1), V(0, 19, 10), RIG, { size: .26 });
  for (const s of [-1, 1]) {
    B.line(V(0, 30, 1), V(s * 4.2, 12, 13), RIG, { size: .22 });
    B.line(V(0, 26, -7), V(s * 4.6, 11, -12), RIG, { size: .22 });
  }
  // braces
  B.line(V(-8, 21, 1), V(-4.6, 14, -7), RIG, { size: .2 });
  B.line(V(8, 21, 1), V(4.6, 14, -7), RIG, { size: .2 });

  // ---- sails ----
  const SAILS = [
    { z: -7,  y0: 13,  y1: 17, wb: 15,   wt: 11,  belly: 1.5 },
    { z: -7,  y0: 18.5, y1: 22, wb: 11.5, wt: 8,   belly: 1.9 },
    { z: -7,  y0: 23.5, y1: 26, wb: 8,    wt: 5,   belly: 2.1 },
    { z: 1,   y0: 17,  y1: 21, wb: 17,   wt: 13,  belly: 1.6 },
    { z: 1,   y0: 22.5, y1: 25.5, wb: 13.5, wt: 9.5, belly: 2.0 },
    { z: 1,   y0: 27,  y1: 29, wb: 9.5,  wt: 6,   belly: 2.2 },
    { z: 10,  y0: 15,  y1: 18, wb: 12,   wt: 9,   belly: 1.4 },
    { z: 10,  y0: 19.5, y1: 22, wb: 9,   wt: 6,   belly: 1.8 }
  ];
  for (const s of SAILS) {
    for (let y = Math.round(s.y0); y <= Math.round(s.y1); y++) {
      const u = (y - s.y0) / Math.max(1, s.y1 - s.y0);
      const w = s.wb + (s.wt - s.wb) * u, hw = Math.floor(w / 2);
      for (let x = -hw; x <= hw; x++) {
        const t = hw ? x / hw : 0;
        const dz = s.z - s.belly * (1 - t * t) * (0.55 + 0.55 * (1 - u));
        const seam = Math.abs(x) % 4 === 0;
        const grime = 0.06 * (1 - u);
        Ws.add(x, y, dz, seam ? 0xd9cbb2 : 0xefe6d2, { sz: 1.4, sx: 1.02, jitter: 0 });
        if (grime > 0 && y - s.y0 < 1) Ws.add(x, y, dz, 0xcdba9e, { sz: 1.4, quiet: true, jitter: 0 });
      }
      if ((y - Math.round(s.y0)) % 4 === 2) for (let x = -hw; x <= hw; x += 2)
        Ws.add(x, y, s.z - s.belly * 1.02, 0xb9a98d, { sz: .5, sx: .5, quiet: true, jitter: 0 });
    }
  }

  // ---- deck life ----
  B.add(0, 9, 12, 0x6f5436, { sx: 3, sy: .6, sz: 3 });
  for (let a = 0; a < 8; a++) B.add(Math.cos(a / 8 * Math.PI * 2) * 1.6, 10, 12 + Math.sin(a / 8 * Math.PI * 2) * 1.6, 0x8a6a3f, { sx: .5, sz: .5 });
  B.add(0, 10, 12, 0x2f2620, { sx: 1, sy: 1.4, sz: 1 });
  for (const hz of [-3, 5]) { B.box(-2, 2, 9, 9, hz, hz + 2, 0x5f4630); B.box(-2, 2, 10, 10, hz, hz + 2, 0x755841); }
  for (let a = 0; a < 12; a++) B.add(Math.cos(a / 12 * Math.PI * 2) * 2.4, 9, 7 + Math.sin(a / 12 * Math.PI * 2) * 2.4, 0xc9a96d, { sx: .4, sz: .4 });
  B.cyl(-2.5, 13, 1.4, 10, 12, 0x6b4a2f);
  B.cyl(2.5, 13, 1.4, 10, 12, 0x6b4a2f);
  B.add(0, 9, -10, 0x6f5436, { sx: 2.4, sy: 1.2, sz: 2.4 });        // capstan
  // sailors on board
  function crew(x, y, z, coat, hat) {
    B.add(x, y, z, hat, { sx: .9, sy: .7, sz: .9 });
    B.add(x, y - 1, z, hat, { sx: 1.3, sy: .4, sz: 1.3 });
    B.box(x, x, y - 3, y - 2, z, z, coat);
    B.add(x, y - 4, z, 0x2f3548);
  }
  crew(2, 12, 10, 0x8f3b32, 0xe8dcc4);
  crew(-1.5, 10, -9, 0x2f3f5c, 0xe8dcc4);
  crew(3, 10, 2, 0xa0763f, 0x333333);
  crew(9, 10, 10, 0x4a6b4e, 0xe8dcc4);   // on the gangplank

  // ---- bow foam collar (rides with the hull) ----
  for (let z = SHIP_Z0 - 1; z <= SHIP_Z1; z++) {
    const b = Math.round(beamAt(z));
    for (const s of [-1, 1]) for (let d = 0; d < 3; d++) {
      if (rnd() < 0.35) continue;
      F.add(s * (b + 0.5 + d), 0.7 + R(0, .5), z + R(-.5, .5), 0xeaf4f7, { sx: R(.6, 1.3), sy: R(.2, .5), sz: R(.6, 1.3), quiet: true });
    }
  }
  for (let x = -SHIP_B; x <= SHIP_B; x++) if (rnd() < .5) F.add(x, 0.7, SHIP_Z1 + 1, 0xeaf4f7, { sx: 1, sy: .3, sz: 1, quiet: true });

  shipGroup.add(B.build('hull'));
  shipGroup.add(Ws.build('sails'));
  shipGroup.add(G.build('shipGlow'));
  shipGroup.add(F.build('foam'));
  glowW.push(G.build('x'));

  // animated pennant
  const flagB = new Vox(matGlowW, { cast: false, receive: false, jitter: 0 });
  for (let i = 0; i < 18; i++) flagB.add(0, 0, 0, 0xc94040, { quiet: true });
  const flag = flagB.build();
  flag.castShadow = false;
  const flagMesh = new THREE.InstancedMesh(new THREE.BoxGeometry(1, 1, 1), flag.material, 18);
  flagMesh.frustumCulled = false;
  flagMesh.instanceColor = flag.instanceColor;
  flagMesh.geometry = flag.geometry;
  flagMesh.matrixAutoUpdate = false;
  shipGroup.add(flagMesh);

  function updateFlag(t) {
    const d = new THREE.Object3D(), c = new THREE.Color();
    let i = 0;
    for (let x = 1; x <= 3; x++) for (let y = 0; y < 2; y++) for (let z = 0; z < 6; z++) {
      const w = Math.sin(z * 0.85 - t * 7) * (0.18 + z * 0.13);
      d.position.set(x * 0.9, 32.2 + y + w, -z - 1);
      d.scale.set(0.9, 1, 1.05);
      d.rotation.set(0, 0, Math.sin(z * 0.85 - t * 7) * 0.2);
      d.updateMatrix();
      flagMesh.setMatrixAt(i, d.matrix);
      c.setHex(z < 2 ? 0xd8d8d8 : 0xc94040);
      flagMesh.setColorAt(i, c);
      i++;
    }
    flagMesh.instanceMatrix.needsUpdate = true;
    if (flagMesh.instanceColor) flagMesh.instanceColor.needsUpdate = true;
  }
  shipGroup.userData.updateFlag = updateFlag;
}

/* ══════════════════════════════════════════════════════════════
   13 · rowboat, distant schooner, gulls, clouds, smoke
   ══════════════════════════════════════════════════════════════ */
const floaters = [];
{
  const b = new Vox(matSolid, { jitter: .04 });
  for (let z = -4; z <= 4; z++) for (const s of [-1, 1]) b.add(s * 1, 0, z, 0x5f4630);
  for (let z = -4; z <= 4; z++) b.add(0, 0, z, 0x4a3624);
  b.box(-1, 1, 1, 1, -3, -2, 0x8a6a3f); b.box(-1, 1, 1, 1, 1, 2, 0x8a6a3f);
  b.add(0, 1, 4, 0x4a3624, { sy: 1.4 });
  b.line(new THREE.Vector3(-1.4, 1, 0), new THREE.Vector3(-3.6, 2.4, 2.4), 0xa88254, { size: .35 });
  b.line(new THREE.Vector3(1.4, 1, 0), new THREE.Vector3(3.6, 2.4, 2.4), 0xa88254, { size: .35 });
  b.add(-1, 2, -2, 0x2f3f5c, { sx: .8, sy: 1.4, sz: .8 });
  b.add(1, 2, -2, 0x8f3b32, { sx: .8, sy: 1.4, sz: .8 });
  const m = b.build();
  const g = new THREE.Group(); g.position.set(9.5, 0.7, -8); g.add(m);
  g.userData.kind = 'row'; g.userData.phase = 2.2;
  scene.add(g); floaters.push(g);
}

{ // distant schooner
  const b = new Vox(matSolid, { jitter: .05 });
  for (let z = -6; z <= 6; z++) {
    const w = Math.max(1, Math.round(1.8 * Math.pow(clamp((z + 6) / 12, 0.05, 1), 0.4) * 1.4));
    for (const s of [-1, 1]) for (let y = 0; y <= 2; y++) b.add(s * w, y, z, y === 2 ? 0xc0913f : 0x2f2620);
    for (let x = -w; x <= w; x++) b.add(x, 0, z, 0x1c1613);
  }
  b.line(new THREE.Vector3(0, 2, -1), new THREE.Vector3(0, 14, -1), 0x6f5436, { size: .5 });
  b.line(new THREE.Vector3(0, 2, 4), new THREE.Vector3(0, 10, 4), 0x6f5436, { size: .5 });
  b.line(new THREE.Vector3(-5, 14, -1), new THREE.Vector3(5, 14, -1), 0x6f5436, { size: .4 });
  for (let y = 5; y <= 13; y++) for (let x = -4; x <= 4; x++) b.add(x, y, -1 - (1 - (x / 4) ** 2) * 1.2, 0xe7ddc8, { sz: 1.2 });
  for (let y = 4; y <= 9; y++) for (let x = -3; x <= 3; x++) b.add(x, y, 4 - (1 - (x / 3) ** 2), 0xe7ddc8, { sz: 1.2 });
  const m = b.build();
  const g = new THREE.Group(); g.position.set(-30, 0, 26); g.add(m);
  g.userData.kind = 'schooner';
  scene.add(g); floaters.push(g);
}

// gulls
const gullMat = new THREE.MeshLambertMaterial({ color: 0xf2f2f0 });
const wingMat = new THREE.MeshLambertMaterial({ color: 0xdfe4e6 });
const gulls = [];
for (let i = 0; i < 7; i++) {
  const g = new THREE.Group();
  const body = new THREE.Mesh(new THREE.BoxGeometry(1.2, 1, 2.8), gullMat);
  const head = new THREE.Mesh(new THREE.BoxGeometry(.8, .8, .8), gullMat); head.position.set(0, .5, 1.6);
  const beak = new THREE.Mesh(new THREE.BoxGeometry(.4, .4, .8), new THREE.MeshLambertMaterial({ color: 0xf0c04a })); beak.position.set(0, .4, 2.4);
  const wl = new THREE.Mesh(new THREE.BoxGeometry(2.8, .35, 1.4), wingMat); wl.position.set(-1.6, .5, .1);
  const wr = new THREE.Mesh(new THREE.BoxGeometry(2.8, .35, 1.4), wingMat); wr.position.set(1.6, .5, .1);
  g.add(body, head, beak, wl, wr);
  g.userData = { wl, wr, r: 18 + i * 4, sp: 0.13 + i * 0.012, ph: rnd() * 6.28, y: 20 + i * 2.4, cx: 8, cz: -4 };
  scene.add(g); gulls.push(g);
}

// clouds
const clouds = [];
for (let c = 0; c < 11; c++) {
  const b = new Vox(new THREE.MeshLambertMaterial({ color: 0xffffff }), { cast: false, receive: false, jitter: .02 });
  const cx = R(-110, 110), cy = R(40, 72), cz = R(-110, 110);
  const n = Ri(14, 34);
  for (let i = 0; i < n; i++) {
    const x = cx + R(-9, 9), y = cy + R(-2, 5), z = cz + R(-7, 7);
    b.add(x, y, z, y > cy + 1 ? 0xffffff : 0xd8dfe6, { sx: R(3, 7), sy: R(2, 4), sz: R(3, 6), quiet: true });
    CUBE_TOTAL++;
  }
  const m = b.build();
  const g = new THREE.Group(); g.add(m);
  g.userData = { sp: R(0.55, 1.6) };
  scene.add(g); clouds.push(g);
}

// chimney smoke
const smokeSrc = smokeSources.concat([new THREE.Vector3(0, 13, 13)]);
const smokeMat = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: .48, depthWrite: false });
const PUFFS = 110;
const smoke = new InstancedPuffSet();
class InstancedPuffSet {
  constructor() {
    const geo = new THREE.BoxGeometry(1, 1, 1);
    this.mesh = new THREE.InstancedMesh(geo, smokeMat, PUFFS);
    this.mesh.frustumCulled = false; this.mesh.castShadow = false;
    this.puffs = [];
    for (let i = 0; i < PUFFS; i++) this.puffs.push(this.spawn());
    scene.add(this.mesh);
  }
  spawn() {
    const s = smokeSrc[Ri(0, smokeSrc.length - 1)];
    return { x: s.x + R(-.4, .4), y: s.y, z: s.z + R(-.4, .4), t: rnd() * 6, life: R(4, 7), dx: R(-1.4, 1.4), dz: R(-1.6, .4) };
  }
  step(dt, t) {
    const d = new THREE.Object3D(), c = new THREE.Color();
    for (let i = 0; i < PUFFS; i++) {
      const p = this.puffs[i];
      p.t += dt;
      if (p.t > p.life) { this.puffs[i] = this.spawn(); continue; }
      const u = p.t / p.life;
      d.position.set(p.x + p.dx * u * 2.2 + Math.sin(t * .5 + i) * .3, p.y + u * 11, p.z + p.dz * u * 2.2);
      const s = 0.7 + u * 4;
      d.scale.set(s, s, s);
      d.rotation.set(t * .2 + i, t * .15, 0);
      d.updateMatrix();
      this.mesh.setMatrixAt(i, d.matrix);
      c.setHex(0xffffff).lerp(scene.fog.color, 0.25 + u * 0.7);
      this.mesh.setColorAt(i, c);
    }
    this.mesh.instanceMatrix.needsUpdate = true;
    if (this.mesh.instanceColor) this.mesh.instanceColor.needsUpdate = true;
  }
}

/* ══════════════════════════════════════════════════════════════
   14 · people on the quay
   ══════════════════════════════════════════════════════════════ */
const COATS = [0x2f3f5c, 0x8f3b32, 0xa0763f, 0x4a6b4e, 0x6b3f5e, 0x355060];
const hats  = [0xe8dcc4, 0x2b2b2b, 0x8a6a3f];
const people = [];
function person(x, z, dir) {
  const gy = landH(x, z);
  const y0 = (x >= Q.edgeX && x <= 34 && z >= Q.z0 && z <= Q.z1) ? Q.surf : (gy ?? 8) + 1;
  const B = new Vox(matSolid, { jitter: .03 });
  const coat = pick(COATS), hat = pick(hats);
  B.add(x, y0 + 5, z, hat, { sx: .9, sy: .8, sz: .9 });
  B.add(x, y0 + 4, z, 0xd8a981, { sx: .9, sy: 1, sz: .9 });
  B.box(x, x, y0 + 3, y0 + 2, z, z, coat);
  B.add(x - .4, y0 + 3, z, coat, { sx: .5, sy: 1.6, sz: .5 });
  B.add(x + .4, y0 + 3, z, coat, { sx: .5, sy: 1.6, sz: .5 });
  B.add(x, y0 + 1, z, 0x2b2f36);
  B.add(x, y0, z, 0x2b2f36);
  const g = new THREE.Group(); g.add(B.build());
  scene.add(g);
  g.userData = { x, z, x0: x - dir * R(4, 12), x1: x + dir * R(4, 12), z0: z - dir * R(3, 9), z1: z + dir * R(3, 9), sp: R(.12, .35), ph: rnd() * 6.28, dir };
  people.push(g);
}
for (let i = 0; i < 12; i++) person(Math.round(R(17, 30)), Math.round(R(Q.z0 + 4, Q.z1 - 2)), rnd() < .5 ? 1 : -1);
person(12, 20, 1); person(13, 24, -1);

/* ══════════════════════════════════════════════════════════════
   15 · assemble opaque meshes
   ══════════════════════════════════════════════════════════════ */
scene.add(land.build('land'));
scene.add(H.build('harbour'));
scene.add(S.build('props'));
for (const g of glowW) if (g) scene.add(g);

/* ══════════════════════════════════════════════════════════════
   16 · time of day
   ══════════════════════════════════════════════════════════════ */
const STOPS = [
  { t: 0.00, name: 'afternoon',  elev: 36, top: '#2d6f9e', hor: '#b9d5e6', fog: '#a9c4d3', sun: '#fff3d6', si: 1.15,
    hs: '#b9d5e6', hg: '#6f6657', deep: '#1c4b5e', shal: '#3f8a91', foam: '#eef4f6', lamp: 0.0 },
  { t: 0.34, name: 'golden hour', elev: 15, top: '#3a6090', hor: '#f4b978', fog: '#e0ab7c', sun: '#ffd9a0', si: 1.05,
    hs: '#cfe0e6', hg: '#8a6f52', deep: '#17414f', shal: '#3a8085', foam: '#f4e7d8', lamp: 0.15 },
  { t: 0.60, name: 'sunset',      elev: 4.5, top: '#2a4a78', hor: '#f07a55', fog: '#cf7d62', sun: '#ff9d63', si: 0.8,
    hs: '#9a8fb8', hg: '#7b5c4a', deep: '#163147', shal: '#2f6474', foam: '#f0d8cf', lamp: 0.55 },
  { t: 0.80, name: 'blue hour',   elev: -5, top: '#101f40', hor: '#5a5c8f', fog: '#3b4160', sun: '#8fa0c8', si: 0.35,
    hs: '#4a5a80', hg: '#3a3530', deep: '#0e2235', shal: '#20475a', foam: '#d5dde6', lamp: 1.15 },
  { t: 1.00, name: 'night',       elev: -16, top: '#050a18', hor: '#15263f', fog: '#0f1826', sun: '#a8bad8', si: 0.18,
    hs: '#26324a', hg: '#201f1e', deep: '#071826', shal: '#123244', foam: '#c8d4dd', lamp: 1.7 }
];
const tmpA = new THREE.Color(), tmpB = new THREE.Color();
function lerpStop(t) {
  let a = STOPS[0], b = STOPS[STOPS.length - 1];
  for (let i = 0; i < STOPS.length - 1; i++) if (t >= STOPS[i].t && t <= STOPS[i + 1].t) { a = STOPS[i]; b = STOPS[i + 1]; }
  const u = clamp((t - a.t) / Math.max(1e-6, b.t - a.t), 0, 1);
  const col = (ka, kb, out) => { tmpA.set(ka, THREE.SRGBColorSpace); tmpB.set(kb, THREE.SRGBColorSpace); out.copy(tmpA).lerp(tmpB, u); return out; };
  const sunDir = new THREE.Vector3();
  const e = THREE.MathUtils.degToRad(lerp2(a.elev, b.elev, u));
  const hz = Math.cos(e);
  sunDir.set(-0.42 * hz, Math.sin(e), -0.88 * hz).normalize();
  return {
    name: u < 0.5 ? a.name : b.name,
    sunDir, si: lerp2(a.si, b.si, u), lamp: lerp2(a.lamp, b.lamp, u),
    top: col(a.top, b.top, new THREE.Color()), hor: col(a.hor, b.hor, new THREE.Color()),
    fog: col(a.fog, b.fog, new THREE.Color()), sun: col(a.sun, b.sun, new THREE.Color()),
    hs: col(a.hs, b.hs, new THREE.Color()), hg: col(a.hg, b.hg, new THREE.Color()),
    deep: col(a.deep, b.deep, new THREE.Color()), shal: col(a.shal, b.shal, new THREE.Color()),
    foam: col(a.foam, b.foam, new THREE.Color())
  };
}
const lerp2 = (a, b, u) => a + (b - a) * u;

const moon = new THREE.Mesh(new THREE.IcosahedronGeometry(9, 2), new THREE.MeshBasicMaterial({ color: 0xf4f1e0, fog: false }));
scene.add(moon);

const todLabel = document.getElementById('todLabel');
function applyTime(t) {
  const s = lerpStop(t);
  skyU.uTop.value.copy(s.top).convertLinearToSRGB().convertSRGBToLinear();  // keep raw sRGB numbers for the raw shader
  // (the Color objects handed to the custom shaders must stay in sRGB numeric form)
  skyU.uTop.value.copy(new THREE.Color(s.top.getHex(), THREE.SRGBColorSpace));
  skyU.uHor.value.copy(s.hor);
  skyU.uSunCol.value.copy(s.sun);
  skyU.uSunDir.value.copy(s.sunDir);
  skyU.uNight.value = clamp((t - 0.55) / 0.28, 0, 1);

  waterU.uSun.value.copy(s.sunDir);
  waterU.uSunC.value.copy(s.sun);
  waterU.uSunI.value = s.si * 0.9;
  waterU.uFogC.value.copy(s.fog);
  scene.fog.color.copy(s.fog);

  sun.color.copy(s.sun);
  sun.intensity = s.si;
  sun.position.copy(s.sunDir).multiplyScalar(120);
  hemi.color.copy(s.hs); hemi.groundColor.copy(s.hg);
  hemi.intensity = lerp2(0.55, 0.32, clamp(t, 0, 1));
  fill.intensity = lerp2(0.3, 0.1, t);
  deepFill.material.color.copy(s.deep);

  moon.position.copy(s.sunDir).multiplyScalar(-300);
  moon.material.color.copy(s.top).lerp(new THREE.Color(0xf4f1e0), 0.6);
  moon.material.opacity = skyU.uNight.value; moon.material.transparent = true;

  const lampF = s.lamp;
  matGlowW.color.setRGB(lerp2(0.34, 1, lampF / 1.7), lerp2(0.28, 0.72, lampF / 1.7), lerp2(0.20, 0.42, lampF / 1.7));
  matGlowH.color.setRGB(lerp2(0.45, 1, lampF / 1.7), lerp2(0.4, 0.95, lampF / 1.7), lerp2(0.3, 0.78, lampF / 1.7));
  matSail.color.setRGB(lerp2(1, 0.5, clamp(t, 0, 1) * 1.1), lerp2(0.97, 0.55, clamp(t, 0, 1) * 1.1), lerp2(0.87, 0.66, clamp(t, 0, 1) * 1.1));
  if (beamGroup) {
    const o = clamp((t - 0.42) / 0.35, 0, 1) * 0.36;
    beamGroup.children.forEach(c => c.material.opacity = o);
    beacon.intensity = o * 3800;
    beacon.color.copy(s.sun).lerp(new THREE.Color(0xfff0c8), 0.5);
  }
  todLabel.textContent = s.name;
  document.getElementById('seaState').textContent = '012345'[3] ? '3' : '3';
}
applyTime(0.34);
document.getElementById('tod').addEventListener('input', e => applyTime(+e.target.value / 1000));

/* ══════════════════════════════════════════════════════════════
   17 · views & UI
   ══════════════════════════════════════════════════════════════ */
const VIEWS = [
  { pos: [54, 34, 84],  tgt: [6, 10, -4] },   // quay view (opening shot)
  { pos: [-64, 22, -14],tgt: [4, 12, 0] },   // broadside
  { pos: [8, 46, -34],  tgt: [4, 20, 0] },   // masthead
  { pos: [21, 14, 22],  tgt: [14, 10, 4] },  // pier
  { pos: [34, 26, -52], tgt: [22, 24, -30] } // lighthouse
];
let tween = null;
function goView(i) {
  const v = VIEWS[i];
  tween = {
    p0: camera.position.clone(), p1: new THREE.Vector3(...v.pos),
    t0: controls.target.clone(), t1: new THREE.Vector3(...v.tgt), k: 0, dur: 1.15
  };
  document.querySelectorAll('.btns button').forEach((b, j) => b.classList.toggle('on', j === i));
}
VIEWS.forEach((_, i) => {
  const b = document.getElementById('v' + i);
  b.addEventListener('click', () => goView(i));
});
const spinBtn = document.getElementById('spin');
spinBtn.addEventListener('click', () => { controls.autoRotate = !controls.autoRotate; spinBtn.classList.toggle('on', controls.autoRotate); spinBtn.textContent = controls.autoRotate ? 'auto-orbit ▓' : 'auto-orbit ▸'; });
controls.autoRotate = true; controls.autoRotateSpeed = 0.42;
spinBtn.classList.add('on');
addEventListener('keydown', e => {
  if (e.key >= '1' && e.key <= '5') goView(+e.key - 1);
  if (e.code === 'Space') { e.preventDefault(); spinBtn.click(); }
});
canvas.addEventListener('pointerdown', () => { tween = null; });

/* ══════════════════════════════════════════════════════════════
   18 · the loop
   ══════════════════════════════════════════════════════════════ */
const clock = new THREE.Clock();
const swingObj = scene.children.find(c => c.userData?.kind === 'swing');
const rowObj   = scene.children.find(c => c.userData?.kind === 'row');
const schObj   = scene.children.find(c => c.userData?.kind === 'schooner');
if (swingObj) swingObj.position.set(10, 16.5, 0);

function tick() {
  const dt = Math.min(0.05, clock.getDelta());
  const t = clock.elapsedTime;

  waterU.uTime.value = t;
  skyU.uTime.value = t;
  smoke.step(dt, t);

  // the ship breathes with the tide
  shipGroup.position.y = 0.14 * Math.sin(t * 0.85) + 0.06 * Math.sin(t * 1.7);
  shipGroup.rotation.z = 0.014 * Math.sin(t * 0.62);
  shipGroup.rotation.x = 0.008 * Math.sin(t * 0.47);
  shipGroup.userData.updateFlag(t);

  if (millSails) millSails.userData.group.rotation.x = t * 0.55;
  if (beamGroup) beamGroup.rotation.y = t * 0.55;
  if (beaconLamp) beaconLamp.rotation.y = t * 0.55;

  if (swingObj) { swingObj.rotation.z = 0.05 * Math.sin(t * 1.1); swingObj.rotation.x = 0.03 * Math.sin(t * 0.8 + 1); }
  if (rowObj) {
    rowObj.position.y = 0.7 + 0.16 * Math.sin(t * 1.4);
    rowObj.rotation.z = 0.03 * Math.sin(t * 0.9);
    rowObj.rotation.x = 0.02 * Math.sin(t * 1.2);
  }
  if (schObj) {
    schObj.position.x += dt * 0.9;
    if (schObj.position.x > 6) schObj.position.x = -76;
    schObj.position.y = 0.12 * Math.sin(t * 0.7 + 1.2);
    schObj.rotation.z = 0.02 * Math.sin(t * 0.5);
  }

  for (const g of gulls) {
    const u = g.userData;
    const a = t * u.sp + u.ph;
    g.position.set(u.cx + Math.cos(a) * u.r, u.y + Math.sin(t * 0.6 + u.ph) * 2.2, u.cz + Math.sin(a) * u.r * 0.8);
    g.rotation.y = -a + Math.PI / 2;
    const flap = Math.sin(t * 7.5 + u.ph);
    u.wl.rotation.z = -flap * 0.55; u.wr.rotation.z = flap * 0.55;
  }
  for (const c of clouds) {
    c.position.x += dt * c.userData.sp;
    if (c.position.x > 150) c.position.x = -150;
  }
  for (const p of people) {
    const u = p.userData;
    const s = (Math.sin(t * u.sp + u.ph));
    p.position.x = u.x + s * 7 * u.dir;
    p.position.z = u.z + Math.sin(t * u.sp * 0.7 + u.ph * 2) * 5;
    p.position.y = Math.abs(Math.sin(t * 5 * u.sp + u.ph)) * 0.25;
    p.rotation.y = Math.cos(t * u.sp + u.ph) * 0.3 + (u.dir > 0 ? 1.57 : -1.57);
  }

  if (tween) {
    tween.k += dt / tween.dur;
    const e = 1 - Math.pow(1 - Math.min(1, tween.k), 3);
    camera.position.lerpVectors(tween.p0, tween.p1, e);
    controls.target.lerpVectors(tween.t0, tween.t1, e);
    if (tween.k >= 1) tween = null;
  }
  controls.update();
  sky.position.copy(camera.position);
  renderer.render(scene, camera);
  requestAnimationFrame(tick);
}

/* ══════════════════════════════════════════════════════════════
   19 · go
   ══════════════════════════════════════════════════════════════ */
addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
renderer.render(scene, camera);       // first paint immediately
document.getElementById('cubeCount').textContent = CUBE_TOTAL.toLocaleString('en-GB');
requestAnimationFrame(() => {
  document.getElementById('veil').style.opacity = '0';
  clock.start();
  tick();
});
</script>
</body>
</html>
```

**What's alive in it**

- **The sea** is a 61×61 grid of instanced cubes; waves, shore breakers, foam collar around the hull, sun glitter and baked shadows from the quay/cliffs are all computed in the shader.
- **The Meridian** bobs and rolls as one group — hull banding follows the sheer line, sails belly downwind with panel seams and reef lines, rigging is voxelised, the pennant flutters by re-writing 18 instance matrices per frame.
- **Living details:** turning windmill, lighthouse with rotating beam + spotlight, swinging derrick load, drifting cumulus, circling gulls with flapping wings, chimney smoke rising and fading into the fog, sailors pacing the quay, a rowboat rocking against the hull, and a distant schooner crossing the bay.
- **Time-of-day slider** re-tunes sun vector, sky gradient, star field, fog, water colour, window glow, beam intensity and sail tint through five keyframes (afternoon → night). Keys `1–5` jump to camera angles, `space` toggles the auto-orbit.