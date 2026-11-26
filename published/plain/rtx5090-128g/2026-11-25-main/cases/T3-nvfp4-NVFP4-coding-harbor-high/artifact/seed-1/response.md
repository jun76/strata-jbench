Below is a single self-contained HTML file — a voxel diorama of a three-masted barque coming home on the evening tide. It builds ~25 000 culled voxels into instanced meshes, animates the sea tile-by-tile, and floats the ship on that same wave field so she bobs and rolls realistically against her mooring lines.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Calling at the Harbour — a voxel diorama</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Alfa+Slab+One&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400&display=swap" rel="stylesheet">
<style>
  :root{
    --ink:#07161c; --canvas:#efe4cd; --ochre:#e2953a; --dim:rgba(239,228,205,.45);
    --line:rgba(239,228,205,.2);
  }
  *{box-sizing:border-box}
  html,body{height:100%;margin:0}
  body{background:#08181e;color:var(--canvas);overflow:hidden;
       font-family:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;-webkit-font-smoothing:antialiased}
  canvas#scene{position:fixed;inset:0;width:100%;height:100%;display:block;cursor:grab}
  canvas#scene:active{cursor:grabbing}

  #vignette{position:fixed;inset:0;pointer-events:none;z-index:2;
    background:radial-gradient(125% 95% at 50% 42%,transparent 42%,rgba(3,12,16,.62) 100%)}
  #grain{position:fixed;inset:0;pointer-events:none;z-index:3;opacity:.05;mix-blend-mode:overlay;
    background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3'/%3E%3C/filter%3E%3Crect width='160' height='160' filter='url(%23n)'/%3E%3C/svg%3E")}

  .panel{position:fixed;background:linear-gradient(180deg,rgba(6,24,31,.9),rgba(4,17,23,.76));
    border:1px solid var(--line);box-shadow:0 22px 50px -28px rgba(0,0,0,.95),inset 0 1px 0 rgba(255,255,255,.07)}
  .panel::before{content:'';position:absolute;left:-1px;top:-1px;height:2px;width:46px;
    background:linear-gradient(90deg,var(--ochre),rgba(226,149,58,0))}

  /* ---- title block ---- */
  .tb{position:fixed;left:28px;top:24px;max-width:min(52vw,540px);z-index:6;pointer-events:none;
      animation:rise .9s .15s both cubic-bezier(.2,.8,.2,1)}
  .kicker{font-size:9.5px;letter-spacing:.36em;text-transform:uppercase;color:var(--ochre);
          display:flex;gap:12px;align-items:center}
  .kicker::after{content:'';flex:1;height:1px;background:linear-gradient(90deg,rgba(226,149,58,.65),transparent)}
  .tb h1{font-family:"Alfa Slab One",Georgia,serif;font-weight:400;font-size:clamp(32px,5.3vw,72px);
    line-height:.86;margin:.18em 0 0;letter-spacing:-.015em;text-transform:uppercase;
    text-shadow:0 14px 34px rgba(0,0,0,.6)}
  .tb h1 em{display:block;font-style:normal;color:transparent;-webkit-text-stroke:1.4px rgba(239,228,205,.78)}
  .tb p{font-family:"IBM Plex Sans",system-ui,sans-serif;font-size:12.5px;line-height:1.65;
    color:rgba(239,228,205,.6);max-width:38ch;margin:16px 0 0;border-left:2px solid rgba(226,149,58,.55);padding-left:12px}
  @keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}

  /* ---- index ---- */
  .idx{position:fixed;right:24px;top:26px;width:242px;z-index:6;padding:12px 12px 6px;
       animation:rise .9s .35s both cubic-bezier(.2,.8,.2,1)}
  .idx .hd{font-size:9px;letter-spacing:.3em;text-transform:uppercase;color:var(--dim);padding:2px 4px 10px}
  .idx button{display:grid;grid-template-columns:24px 1fr;gap:10px;width:100%;text-align:left;
    background:none;border:0;border-top:1px solid var(--line);padding:10px 4px;color:inherit;cursor:pointer;
    font-family:inherit;transition:transform .4s cubic-bezier(.2,.8,.2,1),background .3s}
  .idx button:hover{transform:translateX(-7px);background:linear-gradient(270deg,rgba(226,149,58,.16),transparent)}
  .idx .n{font-family:"Alfa Slab One",serif;font-size:10px;color:rgba(226,149,58,.8);padding-top:2px}
  .idx .t{font-size:13px;letter-spacing:.01em;transition:color .3s}
  .idx button:hover .t{color:#ffd79a}
  .idx .s{font-size:9px;letter-spacing:.16em;text-transform:uppercase;color:var(--dim);margin-top:3px}

  /* ---- log ---- */
  .log{position:fixed;left:28px;bottom:26px;width:224px;padding:13px 15px;z-index:6;
       animation:rise .9s .5s both cubic-bezier(.2,.8,.2,1)}
  .log .hd{font-size:9px;letter-spacing:.3em;text-transform:uppercase;color:var(--dim);margin-bottom:10px}
  .log dl{display:grid;grid-template-columns:1fr auto;gap:5px 8px;margin:0;font-size:11px}
  .log dt{color:var(--dim);letter-spacing:.09em;text-transform:uppercase;font-size:9px;align-self:center}
  .log dd{margin:0;text-align:right;font-variant-numeric:tabular-nums;color:#ffe6bd}

  /* ---- console ---- */
  .console{position:fixed;left:50%;transform:translateX(-50%);bottom:26px;display:flex;align-items:center;
    gap:16px;padding:11px 15px;z-index:7;backdrop-filter:blur(7px);
    animation:rise .9s .6s both cubic-bezier(.2,.8,.2,1)}
  .clock{font-family:"Alfa Slab One",serif;font-size:24px;line-height:1;letter-spacing:.01em}
  .clock small{display:block;font-family:"IBM Plex Mono",monospace;font-size:8.5px;letter-spacing:.3em;
    color:rgba(226,149,58,.9);margin-bottom:7px}
  .sep{width:1px;height:34px;background:var(--line)}
  .scrub{display:flex;flex-direction:column;gap:2px}
  .scrub .cap{display:flex;justify-content:space-between;font-size:8px;letter-spacing:.24em;
    text-transform:uppercase;color:var(--dim)}
  input[type=range]{-webkit-appearance:none;appearance:none;width:min(30vw,290px);height:22px;background:none;cursor:pointer;margin:0}
  input[type=range]::-webkit-slider-runnable-track{height:7px;border:1px solid rgba(239,228,205,.3);
    background:linear-gradient(90deg,#2a3550,#c96a3e,#f2c07a,#fdf0d0,#f0a35f,#8f4a54,#16243f,#243css)}
  input[type=range]::-webkit-slider-runnable-track{background:linear-gradient(90deg,#2a3550,#c96a3e,#f2c07a,#fdf0d0,#f0a35f,#8f4a54,#16243f,#31456b)}
  input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:11px;height:21px;margin-top:-8px;
    border-radius:2px;background:var(--canvas);border:1px solid #0a1a20;
    box-shadow:0 0 0 2px rgba(226,149,58,.6),0 6px 14px rgba(0,0,0,.55);transition:transform .2s}
  input[type=range]:hover::-webkit-slider-thumb{transform:scaleY(1.2)}
  .tgl{font-family:inherit;font-size:9px;letter-spacing:.18em;text-transform:uppercase;padding:8px 10px;
    background:rgba(239,228,205,.06);border:1px solid var(--line);color:rgba(239,228,205,.72);cursor:pointer;
    display:flex;gap:7px;align-items:center;transition:.25s}
  .tgl:hover{border-color:rgba(226,149,58,.75);color:#ffd79a}
  .tgl .led{width:6px;height:6px;border-radius:50%;background:rgba(239,228,205,.28);transition:.25s}
  .tgl.on{color:#0a1a20;background:var(--ochre);border-color:var(--ochre)}
  .tgl.on .led{background:#3a1900;box-shadow:0 0 9px #ffce7a}

  /* ---- compass ---- */
  .cmp{position:fixed;right:24px;bottom:26px;width:100px;height:100px;z-index:6;opacity:.9;
       animation:rise .9s .45s both cubic-bezier(.2,.8,.2,1)}
  .cmp text{font-family:"Alfa Slab One",serif;font-size:11px;fill:var(--canvas)}
  .cmp .sm{font-family:"IBM Plex Mono",monospace;font-size:7px;fill:var(--dim);letter-spacing:.2em}

  /* ---- markers ---- */
  #markers{position:fixed;inset:0;z-index:5;pointer-events:none}
  .mk{position:absolute;display:flex;align-items:center;gap:9px;cursor:pointer;will-change:transform}
  .mk .d{width:8px;height:8px;border:1px solid rgba(226,149,58,.95);background:rgba(226,149,58,.35);
    border-radius:50%;position:relative;flex:none}
  .mk .d::after{content:'';position:absolute;inset:-5px;border:1px solid rgba(226,149,58,.45);border-radius:50%;
    animation:ping 2.8s infinite ease-out}
  .mk .l{font-size:9px;letter-spacing:.22em;text-transform:uppercase;white-space:nowrap;padding:4px 9px;
    background:rgba(5,19,25,.82);border-left:2px solid rgba(226,149,58,.85);
    opacity:0;transform:translateX(-7px);transition:.4s cubic-bezier(.2,.8,.2,1)}
  .mk:hover .l{opacity:1;transform:none}
  .mk:hover .d{background:var(--ochre)}
  @keyframes ping{0%{transform:scale(.55);opacity:.95}70%,100%{transform:scale(1.6);opacity:0}}

  /* ---- loader ---- */
  #load{position:fixed;inset:0;z-index:20;background:#08181e;display:grid;place-content:center;justify-items:center;
    gap:18px;font-size:9.5px;letter-spacing:.34em;text-transform:uppercase;color:rgba(239,228,205,.5);
    transition:opacity .9s .15s}
  #load.gone{opacity:0;pointer-events:none}
  #load .bar{width:220px;height:1px;background:rgba(239,228,205,.18);overflow:hidden}
  #load .bar i{display:block;height:100%;width:40%;background:var(--ochre);animation:sweep 1.1s infinite ease-in-out}
  @keyframes sweep{0%{transform:translateX(-110%)}100%{transform:translateX(320%)}}
  #err{position:fixed;inset:0;display:none;place-content:center;text-align:center;padding:30px;z-index:30}

  @media (max-width:900px){ .log,.cmp{display:none} .idx{width:190px} .tb p{display:none} }
  @media (max-width:640px){ .idx{display:none} .console{gap:10px;padding:9px} input[type=range]{width:40vw} }
</style>
</head>
<body>
<canvas id="scene"></canvas>
<div id="vignette"></div>
<div id="grain"></div>
<div id="markers"></div>

<header class="tb">
  <div class="kicker">Voxel diorama · 1:240 · harbour model</div>
  <h1>Calling at<em>the Harbour</em></h1>
  <p>A three-master comes home on the evening tide — canvas full, powder low, the point light turning behind the breakwater. Drag to walk the quay; scrub the daylight and the lanterns will follow.</p>
</header>

<nav class="idx panel">
  <div class="hd">Chart index</div>
  <div id="idxlist"></div>
</nav>

<section class="log panel">
  <div class="hd">Harbour log</div>
  <dl>
    <dt>Watch</dt><dd id="r-watch">—</dd>
    <dt>Tide</dt><dd id="r-tide">—</dd>
    <dt>Wind</dt><dd id="r-wind">—</dd>
    <dt>Swell</dt><dd id="r-swell">—</dd>
    <dt>Bearing</dt><dd id="r-brg">—</dd>
    <dt>Hull</dt><dd id="r-hull">—</dd>
    <dt>Voxels</dt><dd id="r-vox">—</dd>
    <dt>FPS</dt><dd id="r-fps">—</dd>
  </dl>
</section>

<div class="console panel">
  <div class="clock"><small>Harbour time</small><span id="clock">17:12</span></div>
  <div class="sep"></div>
  <div class="scrub">
    <input id="time" type="range" min="0" max="1000" value="700" aria-label="Time of day">
    <div class="cap"><span>Dawn</span><span>Noon</span><span>Night</span></div>
  </div>
  <div class="sep"></div>
  <button class="tgl on" id="b-orbit"><i class="led"></i>Orbit</button>
  <button class="tgl on" id="b-beam"><i class="led"></i>Beam</button>
  <button class="tgl" id="b-reset">Reset view</button>
</div>

<svg class="cmp" viewBox="0 0 100 100" aria-hidden="true">
  <circle cx="50" cy="50" r="45" fill="rgba(6,20,26,.72)" stroke="rgba(239,228,205,.2)"/>
  <circle cx="50" cy="50" r="34" fill="none" stroke="rgba(239,228,205,.14)"/>
  <g id="cmp-rose">
    <polygon points="50,10 54,50 50,58 46,50" fill="#e2953a"/>
    <polygon points="50,90 54,50 50,42 46,50" fill="rgba(239,228,205,.5)"/>
    <polygon points="10,50 50,46 58,50 50,54" fill="rgba(239,228,205,.32)"/>
    <polygon points="90,50 50,46 42,50 50,54" fill="rgba(239,228,205,.32)"/>
    <text x="50" y="9" text-anchor="middle">N</text>
    <text x="50" y="98" text-anchor="middle">S</text>
    <text x="95" y="54" text-anchor="middle">E</text>
    <text x="5" y="54" text-anchor="middle">W</text>
  </g>
  <circle cx="50" cy="50" r="3" fill="#efe4cd"/>
  <text class="sm" x="50" y="72" text-anchor="middle">HEADING</text>
</svg>

<div id="load"><div id="loadmsg">Sounding the bar</div><div class="bar"><i></i></div></div>
<div id="err">This scene needs WebGL. Try opening it in an up-to-date Chrome with hardware acceleration on.</div>

<script type="importmap">
{ "imports": {
  "three": "https://unpkg.com/three@0.161.0/build/three.module.js",
  "three/addons/": "https://unpkg.com/three@0.161.0/examples/jsm/"
}}
</script>
<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* ══════════════ 1 · renderer, camera, controls ══════════════ */
let renderer;
try{
  renderer = new THREE.WebGLRenderer({canvas:document.getElementById('scene'), antialias:true});
}catch(e){ document.getElementById('err').style.display='grid'; document.getElementById('load').classList.add('gone'); throw e; }
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
renderer.outputColorSpace = THREE.SRGBColorSpace;

const scene  = new THREE.Scene();
scene.fog = new THREE.FogExp2(0xd0a184, 0.0046);
const camera = new THREE.PerspectiveCamera(42, innerWidth/innerHeight, 0.5, 1200);
const HOME_POS = new THREE.Vector3(-58,26,-54), HOME_TGT = new THREE.Vector3(-4,7,0);
camera.position.copy(HOME_POS);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.copy(HOME_TGT);
controls.enableDamping = true; controls.dampingFactor = .055;
controls.minDistance = 16; controls.maxDistance = 190;
controls.maxPolarAngle = Math.PI*0.487; controls.minPolarAngle = 0.12;
controls.autoRotate = !matchMedia('(prefers-reduced-motion: reduce)').matches;
controls.autoRotateSpeed = 0.26;

/* ══════════════ 2 · sky dome, sun, lights ══════════════ */
const skyU = {
  uTop:{value:new THREE.Color()}, uHor:{value:new THREE.Color()}, uBot:{value:new THREE.Color()},
  uSunCol:{value:new THREE.Color()}, uSunDir:{value:new THREE.Vector3(0,1,0)}
};
const sky = new THREE.Mesh(new THREE.SphereGeometry(480,36,20), new THREE.ShaderMaterial({
  side:THREE.BackSide, depthWrite:false, uniforms:skyU,
  vertexShader:`varying vec3 vD; void main(){ vD=position; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
  fragmentShader:`
    uniform vec3 uTop,uHor,uBot,uSunCol,uSunDir; varying vec3 vD;
    void main(){
      vec3 d=normalize(vD); float h=d.y;
      vec3 col=mix(uBot,uHor,smoothstep(-0.22,0.10,h));
      col=mix(col,uTop,smoothstep(0.06,0.62,h));
      float s=max(dot(d,normalize(uSunDir)),0.0);
      col+=uSunCol*(pow(s,6.0)*0.30+pow(s,70.0)*0.85);
      gl_FragColor=vec4(col,1.0);
      #include <tonemapping_fragment>
      #include <colorspace_fragment>
    }`
}));
scene.add(sky);

function glowTex(){
  const c=document.createElement('canvas'); c.width=c.height=128;
  const g=c.getContext('2d'), gr=g.createRadialGradient(64,64,0,64,64,64);
  gr.addColorStop(0,'rgba(255,255,255,1)'); gr.addColorStop(.28,'rgba(255,224,168,.55)');
  gr.addColorStop(1,'rgba(255,200,120,0)'); g.fillStyle=gr; g.fillRect(0,0,128,128);
  return new THREE.CanvasTexture(c);
}
const GLOW_TEX = glowTex();
const sunDisc = new THREE.Sprite(new THREE.SpriteMaterial({map:GLOW_TEX,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,fog:false}));
sunDisc.scale.setScalar(150); scene.add(sunDisc);

const sun = new THREE.DirectionalLight(0xffd7a8, 2.3);
sun.castShadow = true;
sun.shadow.mapSize.set(2048,2048);
const sc = sun.shadow.camera;
sc.left=-88; sc.right=88; sc.top=88; sc.bottom=-88; sc.near=1; sc.far=460;
sun.shadow.bias=-0.0006; sun.shadow.normalBias=0.55;
sun.target.position.set(0,4,0); scene.add(sun.target, sun);
const hemi = new THREE.HemisphereLight(0x9fd6e6, 0x3f4a42, 0.5); scene.add(hemi);
const amb  = new THREE.AmbientLight(0xffffff, 0.14); scene.add(amb);

/* ══════════════ 3 · voxel toolkit ══════════════ */
function hash3(x,y,z){
  let n=(x*374761393 + y*668265263 + z*1440662683)|0;
  n=(n^(n>>>13))|0; n=(n*1274126177)|0;
  return ((n^(n>>>16))>>>0)/4294967295;
}
const _c = new THREE.Color();
const shade=(hex,dl,ds=0)=>{ _c.set(hex); _c.offsetHSL(0,ds,dl); return _c.getHex(); };

class Vox{
  constructor(){ this.m=new Map(); }
  get size(){ return this.m.size; }
  set(x,y,z,c,j=0){
    x=Math.round(x); y=Math.round(y); z=Math.round(z);
    this.m.set(x+'_'+y+'_'+z,{x,y,z,c: j? shade(c,(hash3(x,y,z)-.5)*j):c});
  }
  box(x0,x1,y0,y1,z0,z1,c,j=0){
    for(let x=x0;x<=x1;x++)for(let y=y0;y<=y1;y++)for(let z=z0;z<=z1;z++) this.set(x,y,z,c,j);
  }
  shell(x0,x1,y0,y1,z0,z1,c,j=0){
    for(let x=x0;x<=x1;x++)for(let y=y0;y<=y1;y++)for(let z=z0;z<=z1;z++){
      const edge=(x===x0||x===x1||y===y0||y===y1||z===z0||z===z1);
      if(edge) this.set(x,y,z,c,j);
    }
  }
  cyl(cx,cz,y0,y1,r,c,j=0,filled=true){
    const R=Math.ceil(r)+1;
    for(let x=Math.floor(cx-R);x<=Math.ceil(cx+R);x++)
    for(let z=Math.floor(cz-R);z<=Math.ceil(cz+R);z++){
      const d=Math.hypot(x-cx,z-cz);
      if(d<=r+0.05 && (filled || d>r-0.75)) for(let y=y0;y<=y1;y++) this.set(x,y,z,c,j);
    }
  }
  blob(cx,cy,cz,rx,ry,rz,c,j=.12){
    const X=Math.ceil(rx)+1,Y=Math.ceil(ry)+1,Z=Math.ceil(rz)+1;
    for(let x=Math.floor(cx-X);x<=Math.ceil(cx+X);x++)
    for(let y=Math.floor(cy-Y);y<=Math.ceil(cy+Y);y++)
    for(let z=Math.floor(cz-Z);z<=Math.ceil(cz+Z);z++){
      const d=((x-cx)/rx)**2+((y-cy)/ry)**2+((z-cz)/rz)**2;
      if(d<=1+ (hash3(x,y,z)-.5)*0.55) this.set(x,y,z,c,j);
    }
  }
  line3(x0,y0,z0,x1,y1,z1,c,thick=0){
    const d=new THREE.Vector3(x1-x0,y1-y0,z1-z0), len=Math.ceil(d.length())||1;
    d.normalize();
    for(let i=0;i<=len;i++){
      const x=x0+d.x*i,y=y0+d.y*i,z=z0+d.z*i;
      this.set(x,y,z,c,0.08);
      if(thick){ this.set(x+1,y,z,c,0.08); this.set(x,y+1,z,c,0.08); this.set(x,y,z+1,c,0.08); }
    }
  }
  merge(o){ for(const v of o.m.values()) this.m.set(v.x+'_'+v.y+'_'+v.z,v); }
}
let TOTAL_VOXELS = 0;
function buildVox(v, opts={}){
  const items=[], m=v.m;
  for(const o of m.values()){
    if(m.has((o.x+1)+'_'+o.y+'_'+o.z)&&m.has((o.x-1)+'_'+o.y+'_'+o.z)&&
       m.has(o.x+'_'+(o.y+1)+'_'+o.z)&&m.has(o.x+'_'+(o.y-1)+'_'+o.z)&&
       m.has(o.x+'_'+o.y+'_'+(o.z+1))&&m.has(o.x+'_'+o.y+'_'+(o.z-1))) continue;
    items.push(o);
  }
  if(!items.length) return {mesh:new THREE.Group(),idx:new Map()};
  const mat = opts.material || new THREE.MeshLambertMaterial();
  const mesh = new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1), mat, items.length);
  const d=new THREE.Object3D(), col=new THREE.Color(), idx=new Map();
  for(let i=0;i<items.length;i++){
    const o=items[i];
    d.position.set(o.x,o.y,o.z); d.rotation.set(0,0,0); d.scale.setScalar(1); d.updateMatrix();
    mesh.setMatrixAt(i,d.matrix); mesh.setColorAt(i,col.set(o.c));
    idx.set(o.x+'_'+o.y+'_'+o.z,i);
  }
  mesh.instanceMatrix.needsUpdate=true;
  if(mesh.instanceColor) mesh.instanceColor.needsUpdate=true;
  mesh.castShadow = opts.cast!==false;
  mesh.receiveShadow = opts.receive!==false;
  TOTAL_VOXELS += items.length;
  return {mesh, idx, count:items.length, vox:v};
}

/* ══════════════ 4 · coastline / terrain ══════════════ */
const P={
  cobble:0x8a8274, cobble2:0x746d61, granite:0x948f82, wet:0x4a5152,
  grass:0x55724a, dirt:0x7d6a4c, rock:0x5c6062, rockWet:0x454b4e,
  brick:0x8b4a3a, stone:0xc1b294, plaster:0xe2d6bb, dark:0x2e2823,
  slate:0x414e59, slate2:0x35414b, tile:0x9d5a41, wood:0x7a5b39, woodDark:0x40301f,
  iron:0x3a3f45, copper:0x53907c, sail:0xe8dcc0, rope:0xbda272,
  glass:0x8fb0b6, lamp:0xffcf83, gold:0xc4923c
};
const gauss=(u)=>Math.exp(-u*u);
function shoreZ(x){
  return 16 + Math.sin(x*0.07)*1.1 + gauss((x+34)/15)*7 - gauss((x-40)/13)*8;
}
function ground(x,z){
  const s=shoreZ(x);
  if(z < s) return -99;
  let h=5 + Math.min(8,(z-s)*0.15);
  h += gauss((x-42)/17)*6 + gauss((x+36)/19)*3;
  h += 2.4*gauss((x-20)/13)*gauss((z-46)/18);
  h += (hash3(Math.round(x),0,Math.round(z))-.5)*0.6;
  return Math.round(h);
}
const isLand=(x,z)=> z >= shoreZ(x);
const inPier=(x,z)=> x>=-4 && x<=3 && z>=-17 && z<=16;

const terrain=new Vox();
for(let x=-64;x<=58;x++) for(let z=-46;z<=64;z++){
  if(!isLand(x,z)) continue;
  if(inPier(x,z)) continue;
  const h=ground(x,z), s=shoreZ(x);
  const prom = (z - s) < 7.5;
  for(let y=Math.max(-1,h-3); y<=h; y++){
    let c;
    if(y===h)      c = prom ? P.cobble : (z>22 && z<25 ? P.cobble2 : (h>9 ? P.grass : P.dirt));
    else if(y<=1)  c = P.wet;
    else           c = P.granite;
    terrain.set(x,y,z,c,0.10);
  }
  if(z-s<1.2 && h===5) terrain.set(x,5,Math.round(s),P.granite,0.13);   // coping stone
}
// stone stair down to the water, east side
for(let i=0;i<6;i++) for(let x=26;x<=30;x++) terrain.set(x,5-i,Math.round(shoreZ(28))-i,P.granite,0.12);
// beach in the west cove
for(let x=-50;x<=-24;x++) for(let z=20;z<=28;z++){
  if(!isLand(x,z)) continue;
  const h=ground(x,z); if(h<4) continue;
  terrain.set(x,h,z,0xc3ad83,0.10);
}
scene.add(buildVox(terrain).mesh);

// ── the pier ───────────────────────────────────────────
const pierV=new Vox();
for(let z=-17;z<=16;z++) for(let x=-4;x<=3;x++){
  const head = z<-13, r=Math.hypot(x-(-0.5),(z+13));
  if(head && r>4.6) continue;
  pierV.box(x,x,-2,4,z,z,P.granite,0.11);
  pierV.set(x,5,z, (z%3===0? P.cobble2 : P.cobble), 0.10);
  if(x===-4||x===3) pierV.set(x,5,z, 0x5b4230, 0.10);            // timber edge
}
for(let z=-15;z<=14;z+=5){                                        // bollards
  pierV.box(-5,-5,6,7,z,0x33383d,0.06); pierV.set(-5,8,z,0x4c545a,0);
  pierV.box(4,4,6,7,z,0x33383d,0.06);   pierV.set(4,8,z,0x4c545a,0);
}
scene.add(buildVox(pierV).mesh);

/* ══════════════ 5 · harbour buildings ══════════════ */
const town=new Vox(), glow=new Vox(), beacon=new Vox(), halos=[];
function addHalo(x,y,z,r=.42,color=0xffcf8a){
  const s=new THREE.Sprite(new THREE.SpriteMaterial({map:GLOW_TEX,transparent:true,depthWrite:false,
    blending:THREE.AdditiveBlending,color,fog:false,opacity:0}));
  s.position.set(x,y+0.5,z); s.scale.setScalar(r*22); scene.add(s); halos.push(s); return s;
}
function lampPost(g,x,z,h=9,base=5){
  g.box(x,x,base,base+h-2,z,P.iron,0.05);
  g.box(x,x,base+h-1,base+h-1,z,0x2b2f34,0);
  g.box(x,x,base+h,base+h+1,z,P.iron,0);
  g.box(x,x,base+h,base+h,z,0x2b2f34,0);
  glow.set(x,base+h,z,0xffd79a); addHalo(x,base+h,z,.36);
}
function house(g,gl,{x,z,w,d,h,wall,roofC,door=0x5b3f26,ridgeX=true,beam=false,chimney=0,gn=5}){
  const x0=x,x1=x+w-1,z0=z,z1=z+d-1;
  const yb=Math.max(5,ground(x,z)-1);
  const wins=new Set();
  for(let wy=yb+2; wy<yb+h-1; wy+=3) for(let wx=x0+2; wx<=x1-1; wx+=3) wins.add(wx+'_'+wy+'_'+z0);
  for(let wy=yb+2; wy<yb+h-1; wy+=3) for(let wx=x0+2; wx<=x1-1; wx+=3) wins.add(wx+'_'+wy+'_'+z1);
  for(let wy=yb+2; wy<yb+h-1; wy+=3) for(let wz=z0+2; wz<=z1-1; wz+=3){ wins.add(x0+'_'+wy+'_'+wz); wins.add(x1+'_'+wy+'_'+wz); }
  wins.add((x0+Math.floor(w/2))+'_'+(yb+1)+'_'+z0);               // doorway
  for(let y=yb;y<=yb+h;y++)
    for(let xx=x0;xx<=x1;xx++) for(let zz=z0;zz<=z1;zz++){
      if(xx!==x0&&xx!==x1&&zz!==z0&&zz!==z1&&y!==yb) continue;
      const k=xx+'_'+y+'_'+zz;
      if(wins.has(k)){
        if(y===yb+1 && zz===z0 && xx===x0+Math.floor(w/2)){ g.set(xx,y,zz,door,0.08); continue; }
        gl.set(xx,y,zz,0xffd79a); continue;
      }
      let c=wall;
      if(beam && ((xx-x0)%3===0 || (y-yb)===Math.floor(h/2))) c=P.woodDark;
      if(!ridgeX && (xx-x0)%2===1 && y===yb+h) c=shade(wall,0.06);
      g.set(xx,y,zz,c,0.09);
    }
  // gabled roof
  const y0=yb+h+1;
  if(ridgeX){
    const n=Math.ceil((z1-z0)/2)+1;
    g.box(x0-1,x1+1,y0,z0-1,z1+1,P.slate2,0.09);
    for(let i=1;i<n;i++){
      if(z0+i>z1-i) break;
      g.box(x0-1,x1+1,y0+i,z0+i,z1-i,(i%2? P.slate:P.slate2),0.09);
      g.set(x0,y0+i,z0+i,P.plaster,.06); g.set(x1,y0+i,z1-i,P.plaster,.06);
      for(let zz=z0+i;zz<=z1-i;zz++){ g.set(x0,y0+i,zz,P.plaster,.06); g.set(x1,y0+i,zz,P.plaster,.06); }
    }
  }else{
    const n=Math.ceil((x1-x0)/2)+1;
    g.box(x0-1,x1+1,y0,z0-1,z1+1,P.slate2,0.09);
    for(let i=1;i<n;i++){
      if(x0+i>x1-i) break;
      g.box(x0+i,x1-i,y0+i,z0-1,z1+1,(i%2? P.slate:P.slate2),0.09);
      for(let zz=z0;zz<=z1;zz++){ g.set(x0+i,y0+i,zz,P.plaster,.06); g.set(x1-i,y0+i,zz,P.plaster,.06); }
    }
  }
  if(chimney){
    const cx=x0+1, cz=z1-1;
    g.box(cx,cx+1,y0,y0+5,cz,cz+1,P.brick,0.09);
    g.box(cx,cx+1,y0+6,y0+6,cz,cz+1,0x2c2724,0);
    CHIMNEYS.push({x:cx+0.5,y:y0+7,z:cz+0.5,rate:0.9});
  }
}
const CHIMNEYS=[];

house(town,glow,{x:8,z:24,w:16,d:10,h:8,wall:P.stone,roofC:P.slate,gn:6,chimney:1});    // Custom House
for(let i=0;i<6;i++){ town.box(10+i*3,10+i*3,6,10,23,0xdccdb0,0.04); town.set(10+i*3,11,23,0xdccdb0,0);} // portico
town.box(8,23,12,12,22,0xcbbca0,.05); town.box(12,19,13,13,22,0xb9ab90,.05);
town.box(15,16,13,15,25,0x39332c,0);   // door
town.set(16,14,24,0xffd79a); addHalo(16,14,24,.3);

house(town,glow,{x:-20,z:26,w:16,d:11,h:10,wall:P.brick,ridgeX:false,chimney:1});       // bonded warehouse
town.box(-20,-5,4,5,25,0x6f6a61,.08);                                                   // loading stage
town.box(-13,-11,6,8,25,P.woodDark,.08);                                                // hoist door
town.set(-12,9,25,P.lamp); addHalo(-12,9,25,.26);

house(town,glow,{x:27,z:21,w:11,d:8,h:7,wall:P.plaster,beam:true});                     // sail loft
house(town,glow,{x:-46,z:30,w:6,d:6,h:5,wall:0xd9c9ad,ridgeX:false,chimney:1});         // cottages
house(town,glow,{x:-38,z:31,w:6,d:6,h:6,wall:0xc4b092,ridgeX:false});
house(town,glow,{x:-30,z:32,w:7,d:6,h:5,wall:0xb99270,ridgeX:false,chimney:1});
house(town,glow,{x:-1,z:19,w:8,d:5,h:5,wall:0xcaa97c,ridgeX:false});                    // chandler, pier-side
town.box(-1,6,7,7,18,0xb4472f,.06); town.box(0,6,6,6,18,0xe9e0cc,.06);                  // striped awning
house(town,glow,{x:42,z:29,w:7,d:7,h:13,wall:0xb6ab96,ridgeX:true,chimney:1});          // harbour church tower
town.cyl(45,32,14,14,3,0x9aa0a0,.05); town.cyl(45,32,15,17,2,0x8d4a3c,.06);
town.set(45,15,29,P.lamp); beacon.set(45,15,29,0xffe2a8);

// quay furniture: lamps, barrels, crates, nets, folk
lampPost(town,-11,19,9,5); lampPost(town,-2,20,9,5); lampPost(town,12,19,9,5);
lampPost(town,24,19,9,5);  lampPost(town,-4,2,10,5); lampPost(town,-1,-14,10,5);
function crate(x,y,z,s=2,c=0x8b6a44){ town.box(x,x+s-1,y,y+s-1,z,z+s-1,c,0.12); town.box(x,x+s-1,y+s-1,y+s-1,z,z+s-1,shade(c,-.08),.06); }
function barrel(x,y,z,c=0x6d4f33){ town.cyl(x+0.5,z+0.5,y,y+1,0.9,c,0.1); }
const spots=[[-2,-6],[-3,-9],[1,-4],[5,10],[-2,9],[8,17],[13,16],[19,15],[-42,26],[-27,26],[30,18]];
spots.forEach((s,i)=>{ if(isLand(s[0],s[1])) crate(s[0],ground(s[0],s[1])+1,s[1], (i%3?2:3)); });
for(let i=0;i<9;i++){ const x=-8+i*4+((i*7)%3), z=17+((i*5)%4); if(isLand(x,z)) barrel(x,ground(x,z)+1,z, i%2?0x6d4f33:0x53402c); }
// fish drying frames + nets
for(let i=0;i<4;i++){ const bx=-34+i*5, by=ground(bx,24)+1;
  town.box(bx,bx,by,by+3,24,0x6d5537,0); town.box(bx+3,bx+3,by,by+3,24,0x6d5537,0);
  town.box(bx,bx+3,by+3,by+3,24,0x8a7048,0);
  for(let k=0;k<3;k++) town.set(bx+1+k,by+1,24,0xa9a07f,0);
}
function figure(x,z,coats,cap){
  if(!isLand(x,z)) return; const y=ground(x,z)+1;
  town.box(x,x,y,y+1,z,0x33404a,0);
  town.set(x,y+2,z,coats,0.05); town.set(x,y+3,z,cap?0x2f3a44:0xcaa47a,0);
  if(cap) town.set(x,y+4,z,0x2f3a44,0);
}
figure(-6,17,0xa8402f,true); figure(-8,16,0x3d5a6b,false); figure(2,15,0x7a5b39,true);
figure(11,18,0x2f4a5e,true); figure(20,20,0x9c5b3a,false); figure(-33,25,0x48627a,true);
figure(-18,22,0xb0762f,true); figure(6,25,0x6b4a63,false);

// boats hauled on the slip
function boat(x,z,c=0x4f7c86){ const y=ground(x,z)+1;
  for(let i=0;i<7;i++){ const w=Math.max(0,Math.round(1.6-Math.abs(i-3)*0.45));
    town.box(x-w,x+w,y,y+1,z+i,c,0.09); }
  town.box(x-1,x+1,y+2,y+2,z+3,0x8a7048,0);
}
boat(20,12); boat(24,11,0x9c4b39);
// jetty + rowboat on the sand
town.box(-44,-40,3,4,22,26,P.woodDark,.09); town.cyl(-42.5,26,1,2,2.4,0x5f7f88,.08,false);
// trees on the east hill
for(let i=0;i<26;i++){
  const x=32+Math.floor(hash3(i,3,7)*26), z=30+Math.floor(hash3(i,9,1)*28);
  if(!isLand(x,z)) continue; const y=ground(x,z)+1;
  town.box(x,x,y,y+2,z,P.woodDark,0);
  town.blob(x,y+4,z,1.8,2.6,1.8,0x3f6238,0.14);
}
scene.add(buildVox(town,{receive:true}).mesh);

// rocks, breakwater, lighthouse
const rockV=new Vox();
for(let i=0;i<150;i++){
  const x=Math.round(-40+hash3(i,2,5)*80), z=Math.round(-40+hash3(i,8,3)*26);
  if(isLand(x,z)) continue;
  const s=1+Math.floor(hash3(i,4,4)*2.6), h=Math.round(hash3(i,6,1)*2.4);
  rockV.blob(x,h-1,z,s,s*0.7,s*0.9, h<=0? P.rockWet : P.rock, 0.14);
}
for(let i=0;i<70;i++){ // reef bar out front
  const x=Math.round(-34+i*1.0), z=Math.round(-30+Math.sin(i*0.4)*3);
  rockV.blob(x,Math.round(hash3(i,11,2)*1.6),z,1.6+hash3(i,1,9)*1.4,1.2,1.4,P.rock,0.13);
}
rockV.blob(40,7,11,8,5,7,P.rockWet,0.12);  // lighthouse base
for(let x=32;x<=50;x++) for(let z=6;z<=18;z++){ if(isLand(x,z)) continue;
  rockV.blob(x,Math.round(1+hash3(x,1,z)*4),z,2,1.6,2,P.rock,0.12); }
scene.add(buildVox(rockV).mesh);

// lighthouse tower
const lh=new Vox();
for(let y=8;y<=30;y++){
  const r = 4.4 - (y-8)*0.062, band = (y>13&&y<18)||(y>24&&y<27);
  lh.cyl(40,11,y,y,r, band? 0xa63f31 : 0xefe6d8, 0.06, false);
}
lh.cyl(40,11,30,31,3.2,0x2f3438,.05);
lh.cyl(40,11,32,35,2.4,P.copper,.07,false);
lh.box(38,42,36,36,9,13,P.copper,.07);
lh.blob(40,38,11,2.2,2.2,2.2,P.copper,.08);
lh.box(40,40,39,41,11,11,0x2f3438,0);
for(let a=0;a<12;a++) beacon.set(40+Math.round(Math.cos(a/12*6.283)*2), 33, 11+Math.round(Math.sin(a/12*6.283)*2), 0xfff0c8);
for(let a=0;a<12;a++) glow.set(40+Math.round(Math.cos(a/12*6.283+0.3)*2), 34, 11+Math.round(Math.sin(a/12*6.283+0.3)*2), 0xffe9b8);
scene.add(buildVox(lh).mesh);
const lampPos=new THREE.Vector3(40,33.5,11);
addHalo(40,33.5,11,.72,0xfff0c0);
const lampLight=new THREE.PointLight(0xffd79a,0,120,2); lampLight.position.copy(lampPos); scene.add(lampLight);
// rotating beam
const beamGrp=new THREE.Group(); beamGrp.position.copy(lampPos); scene.add(beamGrp);
const beamMat=new THREE.MeshBasicMaterial({color:0xffe6b4,transparent:true,opacity:0.10,
  blending:THREE.AdditiveBlending,depthWrite:false,side:THREE.DoubleSide,fog:false});
for(let s=0;s<2;s++){
  const g=new THREE.ConeGeometry(11,72,4,1,true); g.translate(0,-36,0);
  const m=new THREE.Mesh(g,beamMat); m.rotation.z=Math.PI/2; m.rotation.y=0;
  const holder=new THREE.Group(); holder.rotation.y=s*Math.PI; holder.add(m); beamGrp.add(holder);
}
// port / starboard beacon posts on the reef
lampPost(beacon,-30,-24,7,1); beacon.set(-30,9,-24,0xff5a3c); addHalo(-30,9,-24,.3,0xff6a44);
lampPost(beacon,8,-27,7,0);   beacon.set(8,8,-27,0x62d78a);     addHalo(8,8,-27,.3,0x6ce08f);

// half-timber detail glow mesh
const glowMesh = buildVox(glow,{cast:false,receive:false,material:new THREE.MeshBasicMaterial()});
scene.add(glowMesh.mesh);
const beaconMesh = buildVox(beacon,{cast:false,receive:false,material:new THREE.MeshBasicMaterial()});
scene.add(beaconMesh.mesh);

/* ══════════════ 6 · the ship ══════════════ */
const shipGroup = new THREE.Group();
shipGroup.position.set(-11,0,-2);
scene.add(shipGroup);

function buildShip(){
  const V1=new Vox(), Vg=new Vox();
  const zB=-17,zS=15, L=1;
  const HULL=0x5f4229, HULL2=0x77522f, DARK=0x2c241d, TAR=0x241f1c,
        CREAM=0xe9dab6, RAIL=0xdcc9a0, DECK=0x9d7a50, WALE=0xc99b45, IRON=0x35393e;
  const hw=t=>{
    if(t<0.30) return 1.0 + 4.0*Math.sqrt(t/0.30);
    return Math.max(3.2, 5.0*(1-0.28*Math.pow((t-0.30)/0.70,2)));
  };
  const ky=t=> -4.3 + 3.2*Math.pow(Math.max(0,(0.30-t))/0.30,1.5) + 1.7*Math.pow(Math.max(0,(t-0.86))/0.14,2);
  const gy=t=> 3.1 + 1.7*Math.pow(Math.max(0,(0.27-t))/0.27,1.3) + 1.5*Math.pow(Math.max(0,(t-0.78))/0.22,1.2);

  for(let z=zB; z<=zS; z++){
    const t=(z-zB)/(zS-zB), w=hw(t), k=ky(t), g0=gy(t);
    for(let y=Math.round(k); y<=Math.round(g0); y++){
      const f=(y-k)/Math.max(1,(g0-k)), half=w*(0.42+0.58*Math.min(1,f*1.12)), xr=Math.max(0,Math.round(half));
      let c = y<0 ? TAR : (y<=1 ? HULL2 : (y===2 ? WALE : (y>=Math.round(g0)-1 ? HULL : HULL)));
      for(const s of [-1,1]) V1.set(s*xr, y, z, c, 0.09);
      if(y<=Math.round(k)) for(let x=-xr;x<=xr;x++) V1.set(x,y,z,TAR,0.07);
      if(y>=Math.round(g0)){ for(let x=-xr;x<=xr;x++) V1.set(x,y,z,DECK,0.10); }
      // gun ports
      if(y===1 && xr>2 && (z%3===1) && z>-12 && z<10){
        V1.set(s*xr>0?xr:-xr,1,z,0x14120f,0);
        V1.set(s*xr>0?xr:-xr,2,z,CREAM,0); V1.set(s*xr>0?xr:-xr,0,z,CREAM,0);
      }
    }
    // bulwark rail
    const xr=Math.max(0,Math.round(hw(t))), gyR=Math.round(gy(t));
    for(const s of [-1,1]) V1.set(s*xr,gyR+1,z,RAIL,0.08);
  }
  // stern transom + sterncastle
  const wS=Math.round(hw(1)), zTr=zS;
  for(let x=-wS;x<=wS;x++) for(let y=-2;y<=5;y++) V1.set(x,y,zTr, (y===2? WALE: (y>3?CREAM:HULL)),0.07);
  for(let x=-wS;x<=wS;x++) for(let z=zS-6;z<=zS;z++) V1.box(x,x,4,5,z,z,CREAM,0.07);
  for(const xx of [-3,0,3]) Vg.set(xx,4,zS,0xffd79a);
  V1.box(-4,4,6,6,zS-5,zS,DECK,0.08);
  V1.box(-4,-4,6,7,zS,0x2f2820,.05); V1.box(4,4,6,7,zS,0x2f2820,.05);
  // ship's wheel
  V1.box(-1,1,7,7,zS-2,P.woodDark,0);
  V1.box(-2,2,8,8,zS-2,P.wood,0); V1.box(-1,1,8,8,zS-3,zS-1,P.wood,0);

  // forecastle
  V1.box(-3,3,3,5,-15,-10,HULL,0.08); V1.box(-3,3,6,6,-15,-10,DECK,0.09);
  V1.box(-3,3,6,6,-15,-15,RAIL,.07);
  V1.line3(0,4,-17,0,10,-27,0x6a5340);                     // bowsprit
  V1.line3(-2,4,-17,-2,8,-25,0x6a5340); V1.line3(2,4,-17,2,8,-25,0x6a5340);
  V1.box(-3,3,7,7,-24,-22,CREAM,.06);                      // spritsail yard
  V1.box(-2,2,3,6,-23,-22,0xe2d6b8,.07);

  // masts / yards / sails
  const masts=[{z:-9.5,top:22},{z:-0.5,top:28},{z:9,top:19}];
  masts.forEach((mm,i)=>{
    const zr=Math.round(mm.z);
    for(let y=3;y<=mm.top;y++) V1.set(0,y,zr, (y%7===0? 0x8a6c48 : 0x4d3b28),0.05);
    V1.box(-1,1,mm.top,mm.top,zr-1,zr+1,0x4d3b28,0);
    const yards = i===0? [{y:11,h:6,d:6},{y:16,h:5,d:5},{y:20,h:3.4,d:0}]
              : i===1? [{y:12,h:7.5,d:7},{y:18,h:6.4,d:6},{y:23,h:4.4,d:0}]
                     : [{y:10.5,h:5,d:6},{y:15.5,h:3.8,d:0}];
    yards.forEach((Y,j)=>{
      const yy=Math.round(Y.y);
      for(let x=-Math.round(Y.h);x<=Math.round(Y.h);x++){
        V1.set(x,yy,zr - Math.round(Math.abs(x)/Y.h*0),0x6a5340,0.06);
        if(Math.abs(x)>Y.h-1) V1.set(x,yy-1,zr,0x6a5340,0);
      }
      if(!Y.d) return;                                                  // furled
      const half=Math.round(Y.h)-1, sag=(j===0?2.4:1.7);
      for(let r=0;r<Y.d;r++){
        const f=r/(Y.d-1), yy2=yy-1-r, zo=Math.round(Math.sin(Math.PI*Math.min(1,f*1.15))*sag);
        const ww=Math.round(half*(0.86+0.16*Math.sin(Math.PI*f)));
        for(let x=-ww;x<=ww;x++) V1.set(x,yy2,zr+zo, r>Y.d-3? shade(P.sail,-0.09): (r>1? P.sail: shade(P.sail,0.05)), 0.07);
      }
    });
    // tops + topsides
    if(i<2){ V1.box(-2,2,17,17,zr-1,zr+1,0x4d3b28,.05); V1.box(-2,2,17,18,zr-2,zr-2,0x4d3b28,0); V1.box(-2,2,17,18,zr+2,zr+2,0x4d3b28,0); }
  });
  // lateen trysail on the mizzen
  for(let r=0;r<7;r++) for(let x=0;x<=6-r;x++) V1.set(x,15-r,10+1, P.sail,0.08);
  // deck cargo & fittings
  const dp=(z)=>Math.round(gy((z-zB)/(zS-zB)))+1;
  [[-3,-4],[2,-4],[-3,2],[3,3],[-1,5],[2,-7]].forEach(p=>{ V1.box(p[0],p[0]+1,dp(p[1]),dp(p[1])+1,p[1],p[1]+1,0x8b6a44,0.13); });
  [[-2,-2],[3,-6],[-3,7],[1,7]].forEach(p=> V1.cyl(p[0]+0.5,p[1]+0.5,dp(p[1]),dp(p[1])+1,0.9,0x6d4f33,0.1));
  V1.cyl(0,3,dp(3),dp(3)+1,1.2,0x5a4128,0.06);                          // capstan
  V1.box(-1,1,dp(3)+2,dp(3)+2,2,4,P.woodDark,0);
  for(let x=-2;x<=2;x++) V1.set(x,dp(3)+1,3,P.woodDark,0);
  for(let z=-6;z<=2;z+=4) V1.box(-2,2,dp(z),dp(z),z,z+1,0x33302a,0);      // hatches
  // longboat
  for(let i=0;i<8;i++){ const w=Math.max(0,Math.round(1.4-Math.abs(i-3.5)*0.4));
    V1.box(-w,w,dp(-1)+1,dp(-1)+2,-6+i,-6+i,0x8d6f4a,0.09); }
  // crew
  [[0,dp(-11)+1,-12,0xa8402f],[2,dp(6)+1,6,0x35506b],[-2,dp(1)+1,1,0x7a5b39]].forEach(p=>{
    V1.box(p[0],p[0],p[1],p[1]+1,p[2],p[2],0x2f3640,0);
    V1.set(p[0],p[1]+2,p[2],p[3],0); V1.set(p[0],p[1]+3,p[2],0xc59a70,0);
  });
  Vg.set(0,5,zS+0,0xffd79a);
  return {V1,Vg};
}
const shipBuild = buildShip();
scene.add(new THREE.Object3D());
shipGroup.add(buildVox(shipBuild.V1).mesh);
const shipGlow = buildVox(shipBuild.Vg,{cast:false,receive:false,material:new THREE.MeshBasicMaterial()});
shipGroup.add(shipGlow.mesh);
addHalo(-11,5.5,13,.22);   // stern windows glow

// rigging lines ------------------------------------------------
const rig=[];
const push=(a,b)=>rig.push(a[0],a[1],a[2],b[0],b[1],b[2]);
const mastTop=[[0,22,-9],[0,28,0],[0,19,9]];
push([0,10,-27],mastTop[0]); push([0,22,-9],[0,28,0]); push([0,28,0],[0,19,9]); push([0,19,9],[0,6,14]);
push([0,10,-27],[-5,2,-14]); push([0,10,-27],[5,2,-14]);
[[0,22,-9],[-9,-9],[0,28,0],[-14,0],[0,19,9],[12,9]].forEach((m,i,a)=>{
  if(i%2) return;
  const [mx,my,mz]=m;
  for(const s of [-1,1]){
    push([mx,my,mz],[s*5,3,mz-4]); push([mx,my,mz],[s*5,3,mz]); push([mx,my,mz],[s*5,3,mz+4]);
  }
  push([mx,my,mz],[-8,mz===0?12:10,mz]); push([mx,my,mz],[8,mz===0?12:10,mz]);
});
for(const s of [-1,1]) push([0,10,-27],[s*4.5,3.5,-8]);
const rigGeo=new THREE.BufferGeometry();
rigGeo.setAttribute('position', new THREE.Float32BufferAttribute(rig,3));
const rigLines=new THREE.LineSegments(rigGeo,new THREE.LineBasicMaterial({color:0x2b231a,transparent:true,opacity:.75}));
shipGroup.add(rigLines);

// flags ---------------------------------------------------------
const FLAGS=[];
function makeFlag(color,w,h,pos,parent,taper=0,dir=1){
  const list=[];
  for(let i=0;i<w;i++) for(let j=0;j<h;j++){
    if(j>=h-Math.round(taper*i)) continue;
    list.push({i,j,base:new THREE.Vector3(pos[0],pos[1]+j,pos[2]),dir});
  }
  const m=new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1),
        new THREE.MeshLambertMaterial(color),list.length);
  m.castShadow=false; m.frustumCulled=false; parent.add(m);
  FLAGS.push({m,list,dir});
  return m;
}
makeFlag(0xc03a2e,9,5,[1,27.5,0],shipGroup,2);
makeFlag(0xe9e0cc,7,4,[1,21.5,-9],shipGroup,1);
makeFlag(0xe2b04a,6,3,[1,18,9],shipGroup,1);
makeFlag(0x26414f,5,3,[1,10,-26],shipGroup,0);

// crane on the pier head ---------------------------------------
const craneGrp=new THREE.Group(); craneGrp.position.set(0,6,-13); scene.add(craneGrp);
const craneV=new Vox();
craneV.box(-1,1,0,2,0,0,P.iron,0.05);
craneV.line3(0,2,0,0,6,10,0x6a4a2c); craneV.line3(0,6,10,0,5,-3,0x6a4a2c);
craneV.box(-1,1,5,5,-4,-3,0x4a4f55,.05);
craneGrp.add(buildVox(craneV,{receive:false}).mesh);
const hookRope=new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(),new THREE.Vector3()]),
  new THREE.LineBasicMaterial({color:0xbda272})); scene.add(hookRope);
const hookBox=new THREE.Mesh(new THREE.BoxGeometry(2,2,2),new THREE.MeshLambertMaterial({color:0x8b6a44}));
hookBox.castShadow=true; scene.add(hookBox);

/* ══════════════ 7 · sea ══════════════ */
const WX0=-70,WX1=58,WZ0=-70,WZ1=17;
const seaMat=new THREE.MeshPhongMaterial({color:0xffffff,shininess:120,specular:0xffb877,
  transparent:true,opacity:0.95});
const tiles=[];
for(let x=WX0;x<=WX1;x++) for(let z=WZ0;z<=WZ1;z++){
  if(isLand(x,z)) continue;
  if(inPier(x,z)) continue;
  const d=Math.max(0, shoreZ(x)-z);
  tiles.push({x,z, shallow:Math.max(0,1-d/13), foam:Math.max(0,1-d/3.4), k:hash3(x,1,z)});
}
const wGeo=new THREE.BoxGeometry(1,1.7,1);
const water=new THREE.InstancedMesh(wGeo,seaMat,tiles.length);
water.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
water.castShadow=false; water.receiveShadow=true;
scene.add(water);
// far water to the horizon
const far=new THREE.Mesh(new THREE.BoxGeometry(900,2,900),new THREE.MeshLambertMaterial({color:0x143846}));
far.position.set(0,-1.6,-250); scene.add(far);

function waveH(x,z,t){
  return 0.30*Math.sin(x*0.245 + t*1.05)
       + 0.25*Math.sin(z*0.185 - t*0.82)
       + 0.15*Math.sin((x+z)*0.325 + t*1.55)
       + 0.09*Math.sin((x-2*z)*0.11 - t*0.55);
}
const seaRamp=[];
for(let i=0;i<10;i++) seaRamp.push(new THREE.Color());
let seaDeep=0x14414f, seaShal=0x2f7f86, seaFoam=0xe8f2ef;
function refreshRamp(){
  const a=new THREE.Color(seaDeep), b=new THREE.Color(seaShal), f=new THREE.Color(seaFoam);
  for(let i=0;i<10;i++){
    const t=i/9;
    seaRamp[i].copy(a).lerp(b,t*0.85).lerp(f,Math.max(0,(t-0.55))*0.9);
  }
}
refreshRamp();

/* ══════════════ 8 · clouds · gulls · smoke ══════════════ */
const cloudGrp=new THREE.Group(); scene.add(cloudGrp);
const cloudV=new Vox();
for(let i=0;i<16;i++){
  const cx=-260+hash3(i,1,1)*520, cy=46+hash3(i,2,2)*22, cz=-230+hash3(i,3,3)*330;
  const s=6+hash3(i,4,4)*10;
  for(let j=0;j<4;j++){
    cloudV.blob(cx+j*s*0.55, cy+Math.round(hash3(i,j,9)*2-1), cz,
                s*0.7, s*0.34, s*0.5, j===0? shade(0xf6ead8,0.05): shade(0xcfd6d8,-0.04), 0.09);
  }
  cloudV.blob(cx+s*0.9, cy-2, cz, s*1.1, s*0.2, s*0.55, 0xd9b7a3, 0.09);   // warm underside
}
cloudGrp.add(buildVox(cloudV,{cast:false,receive:false}).mesh);

const gulls=[], gullGeoB=new THREE.BoxGeometry(1.2,0.8,2.6), gullGeoW=new THREE.BoxGeometry(4.2,0.28,1.4);
const gullMat=new THREE.MeshLambertMaterial({color:0xf4f1e8}), gullMatD=new THREE.MeshLambertMaterial({color:0x59606a});
for(let i=0;i<7;i++){
  const g=new THREE.Group();
  const b=new THREE.Mesh(gullGeoB,gullMat); b.castShadow=true; g.add(b);
  const wl=new THREE.Mesh(gullGeoW,gullMat); wl.position.x=-2.4; g.add(wl);
  const wr=new THREE.Mesh(gullGeoW,gullMat); wr.position.x= 2.4; g.add(wr);
  const tipL=new THREE.Mesh(new THREE.BoxGeometry(1.1,0.24,1.2),gullMatD); tipL.position.x=-1.7; wl.add(tipL);
  const tipR=new THREE.Mesh(new THREE.BoxGeometry(1.1,0.24,1.2),gullMatD); tipR.position.x= 1.7; wr.add(tipR);
  scene.add(g);
  gulls.push({g,wl,wr,r:22+hash3(i,5,5)*38,cx:-8+hash3(i,6,6)*40,cz:-14+hash3(i,7,7)*30,
              y:15+hash3(i,8,8)*16,sp:0.16+hash3(i,9,9)*0.14,ph:hash3(i,10,10)*6.28,wl,wr});
}
const SMOKERS=[]; CHIMNEYS.slice(0,3).forEach(c=>SMOKERS.push(c));
SMOKERS.push({x:-11,y:33,z:11,rate:.4}); // (a wisp from the lighthouse stove)
const puffMat=new THREE.MeshLambertMaterial({color:0xa9b0b2,transparent:true,opacity:.42});
const puffs=[]; const puffMesh=new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1),puffMat,64);
puffMesh.castShadow=false; scene.add(puffMesh);
for(let i=0;i<64;i++) puffs.push({src:SMOKERS[i%SMOKERS.length],t:Math.random(),sp:0.10+Math.random()*0.1});

/* ══════════════ 9 · daylight model ══════════════ */
const STOPS=[
 {t:0.00,el:1.5, az:241,si:1.5, sunC:0xff8f52, top:0x153a5e, hor:0xe07a4a, bot:0x1d2f45, hs:0x5c86ad, hi:.42, am:.16, lamp:.55, fog:0x7d7f8a, exp:1.10, sea:0x1a3550, shal:0x35697a, foam:0xd9dfe0, spec:0xff9a58},
 {t:0.14,el:14,  az:224,si:2.2, sunC:0xffb877, top:0x22649a, hor:0xf4b478, bot:0x3c5a72, hs:0x92bcd8, hi:.55, am:.17, lamp:.12, fog:0xc3b09c, exp:1.02, sea:0x1f4a5e, shal:0x3d9198, foam:0xeef4f0, spec:0xffcb86},
 {t:0.40,el:58,  az:196,si:2.95,sunC:0xfff4e2, top:0x2f79b4, hor:0xbddbe6, bot:0x6d97a8, hs:0xb6dcee, hi:.68, am:.20, lamp:.00, fog:0xd6e3e0, exp:.98, sea:0x1d5c6c, shal:0x46a8a6, foam:0xf7fbf6, spec:0xffffff},
 {t:0.58,el:34,  az:212,si:2.65,sunC:0xffd7a0, top:0x2a6f9f, hor:0xf0c08a, bot:0x50748c, hs:0xa6cede, hi:.60, am:.18, lamp:.00, fog:0xd9c7ae, exp:1.00, sea:0x185060, shal:0x3f999b, foam:0xf2f4ea, spec:0xffe0a8},
 {t:0.70,el:14,  az:230,si:2.35,sunC:0xffa85a, top:0x1f5a86, hor:0xef9a55, bot:0x3f5c74, hs:0x8fb4cf, hi:.50, am:.17, lamp:.24, fog:0xd0a184, exp:1.06, sea:0x14414f, shal:0x348a90, foam:0xe8f2ef, spec:0xffa860},
 {t:0.84,el:2,   az:248,si:1.45,sunC:0xff6b4a, top:0x123055, hor:0xce574f, bot:0x1e2a44, hs:0x556f95, hi:.34, am:.14, lamp:.82, fog:0x7a5f6e, exp:1.15, sea:0x122f45, shal:0x2a5f74, foam:0xc8c6c9, spec:0xff7a55},
 {t:0.94,el:-6,  az:258,si:0.30,sunC:0x6f7fc0, top:0x071428, hor:0x1b2c4e, bot:0x0a1424, hs:0x2b4266, hi:.20, am:.11, lamp:1.0, fog:0x1c2740, exp:1.24, sea:0x081a2b, shal:0x123a52, foam:0x8fa2b4, spec:0x8ea6d8},
 {t:1.00,el:38,  az:56, si:0.85,sunC:0xa8c4ff, top:0x081a30, hor:0x24395c, bot:0x0b1826, hs:0x39557c, hi:.28, am:.13, lamp:1.0, fog:0x24344e, exp:1.20, sea:0x0a2233, shal:0x164257, foam:0xa8bccd, spec:0xbcd2ff}
];
const cA=new THREE.Color(), cB=new THREE.Color();
function lerpStop(t){
  let i=0; while(i<STOPS.length-2 && t>STOPS[i+1].t) i++;
  const a=STOPS[i], b=STOPS[i+1], k=(t-a.t)/(b.t-a.t);
  const mixC=(ka,kb)=>cA.setHex(ka).lerp(cB.setHex(kb),k).getHex();
  return {
    el:a.el+(b.el-a.el)*k, az:a.az+(b.az-a.az)*k, si:a.si+(b.si-a.si)*k,
    sunC:mixC(a.sunC,b.sunC), top:mixC(a.top,b.top), hor:mixC(a.hor,b.hor), bot:mixC(a.bot,b.bot),
    hs:mixC(a.hs,b.hs), hi:a.hi+(b.hi-a.hi)*k, am:a.am+(b.am-a.am)*k, lamp:a.lamp+(b.lamp-a.lamp)*k,
    fog:mixC(a.fog,b.fog), exp:a.exp+(b.exp-a.exp)*k,
    sea:mixC(a.sea,b.sea), shal:mixC(a.shal,b.shal), foam:mixC(a.foam,b.foam), spec:mixC(a.spec,b.spec)
  };
}
const glowDay=new THREE.Color(0x2e4550), glowNight=new THREE.Color(0xffce86);
let LAMPF=0.24;
function applyTime(t){
  const s=lerpStop(t);
  const er=THREE.MathUtils.degToRad(s.el), ar=THREE.MathUtils.degToRad(s.az);
  const dir=new THREE.Vector3(Math.cos(ar)*Math.cos(er), Math.sin(er), Math.sin(ar)*Math.cos(er)).normalize();
  sun.position.copy(dir).multiplyScalar(190);
  sun.color.set(s.sunC); sun.intensity=s.si;
  skyU.uTop.value.set(s.top); skyU.uHor.value.set(s.hor); skyU.uBot.value.set(s.bot);
  skyU.uSunCol.value.set(s.sunC); skyU.uSunDir.value.copy(dir);
  hemi.color.set(s.hs); hemi.intensity=s.hi; amb.intensity=s.am;
  scene.fog.color.set(s.fog); renderer.toneMappingExposure=s.exp;
  sunDisc.position.copy(dir).multiplyScalar(400);
  sunDisc.material.color.set(s.sunC); sunDisc.material.opacity=t>0.92?0.55:0.9;
  sunDisc.scale.setScalar(t>0.9? 92:150);
  far.material.color.set(s.sea);
  seaDeep=s.sea; seaShal=s.shal; seaFoam=s.foam; refreshRamp();
  seaMat.specular.set(s.spec);
  LAMPF=s.lamp;
  glowMesh.mesh.material.color.copy(glowDay).lerp(glowNight,LAMPF);
  shipGlow.mesh.material.color.copy(glowDay).lerp(glowNight,LAMPF);
  beaconMesh.mesh.material.color.setHex(0xffffff);
  halos.forEach(h=>h.material.opacity=LAMPF*0.85);
  beamMat.opacity=0.035+LAMPF*0.16;
  lampLight.intensity=LAMPF*2.6;
  puffMat.color.setHex(0xa9b0b2).lerp(new THREE.Color(s.hor),0.35);
}

/* ══════════════ 10 · points of interest + UI ══════════════ */
const POIS=[
 {n:'01',t:'The Merchant',s:'Barque · 214 tons', anchor:new THREE.Vector3(-11,20,-2),  cam:new THREE.Vector3(-33,13,-24), tgt:new THREE.Vector3(-11,10,-2)},
 {n:'02',t:'Point Light', s:'Est. 1798 · 31 m', anchor:new THREE.Vector3(40,36,11),    cam:new THREE.Vector3(15,24,-12),  tgt:new THREE.Vector3(40,22,11)},
 {n:'03',t:'Custom House',s:'Quay · long room', anchor:new THREE.Vector3(16,15,25),    cam:new THREE.Vector3(-2,17,4),    tgt:new THREE.Vector3(15,9,26)},
 {n:'04',t:'Old Pier Head',s:'Berth No. 3',     anchor:new THREE.Vector3(-1,11,-14),   cam:new THREE.Vector3(-27,10,-31), tgt:new THREE.Vector3(-2,6,-11)},
 {n:'05',t:'Full Harbour',s:'Establishing shot',anchor:null,                             cam:HOME_POS.clone(),             tgt:HOME_TGT.clone()}
];
const mkLayer=document.getElementById('markers');
POIS.forEach(p=>{
  const btn=document.createElement('button');
  btn.innerHTML=`<span class="n">${p.n}</span><span><span class="t">${p.t}</span><div class="s">${p.s}</div></span>`;
  btn.onclick=()=>flyTo(p.cam,p.tgt);
  document.getElementById('idxlist').appendChild(btn);
  if(p.anchor){
    const d=document.createElement('div'); d.className='mk';
    d.innerHTML=`<span class="d"></span><span class="l">${p.t}</span>`;
    d.onclick=()=>flyTo(p.cam,p.tgt);
    mkLayer.appendChild(d); p.el=d;
  }
});
let flight=null;
function flyTo(pos,tgt){
  flight={p0:camera.position.clone(),t0:controls.target.clone(),p1:pos.clone(),t1:tgt.clone(),k:0,
          wasOrbit:controls.autoRotate};
  controls.autoRotate=false;
}
const $=id=>document.getElementById(id);
const timeSl=$('time');
timeSl.addEventListener('input',()=>applyTime(timeSl.value/1000));
applyTime(timeSl.value/1000);
const bOrbit=$('b-orbit'), bBeam=$('b-beam'), bReset=$('b-reset');
bOrbit.classList.toggle('on',controls.autoRotate);
bOrbit.onclick=()=>{ controls.autoRotate=!controls.autoRotate; bOrbit.classList.toggle('on',controls.autoRotate); };
bBeam.onclick =()=>{ beamGrp.visible=!beamGrp.visible; bBeam.classList.toggle('on',beamGrp.visible); };
bReset.onclick=()=>flyTo(HOME_POS,HOME_TGT);
addEventListener('keydown',e=>{
  if(e.key==='r'||e.key==='R') flyTo(HOME_POS,HOME_TGT);
  if(e.code==='Space'){ e.preventDefault(); bOrbit.click(); }
});
controls.addEventListener('start',()=>{ controls.autoRotate=false; bOrbit.classList.remove('on'); });
addEventListener('resize',()=>{
  camera.aspect=innerWidth/innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight);
});

/* ══════════════ 11 · animate ══════════════ */
const clock=new THREE.Clock();
const dummy=new THREE.Object3D(), tmpV=new THREE.Vector3(), tmpV2=new THREE.Vector3();
const ropes=[
  {a:new THREE.Vector3(-5,8,-15), b:new THREE.Vector3(0,3,-16)},   // bollard → bow
  {a:new THREE.Vector3(-5,8,5),   b:new THREE.Vector3(0,4.5,13)},  // bollard → quarter
  {a:new THREE.Vector3(-5,8,-5),  b:new THREE.Vector3(0,3,4)}
];
ropes.forEach(r=>{
  r.obj=new THREE.Line(new THREE.BufferGeometry().setFromPoints(
    Array.from({length:14},()=>new THREE.Vector3())),
    new THREE.LineBasicMaterial({color:0xc7ad7c,transparent:true,opacity:.92}));
  scene.add(r.obj);
});
const moorPts=[];
for(let i=0;i<3;i++) moorPts.push(new THREE.Vector3());

let fps=60, fAcc=0, fCnt=0, acc=0;
function tick(){
  const dt=Math.min(0.05,clock.getDelta()), t=clock.elapsedTime;

  /* sea */
  for(let i=0;i<tiles.length;i++){
    const T=tiles[i];
    const swell=0.55+0.45*Math.sin(t*0.21+1.1);
    let h=waveH(T.x,T.z,t)*(0.55+0.55*T.shallow)*swell;
    if(T.foam>0) h+=Math.sin(t*3.1+T.k*9)*0.16*T.foam;
    dummy.position.set(T.x,-0.85+h,T.z); dummy.rotation.set(0,0,0); dummy.scale.set(1,1,1);
    dummy.updateMatrix(); water.setMatrixAt(i,dummy.matrix);
    const hn=THREE.MathUtils.clamp((h+0.55)/1.5,0,1);
    const k=Math.min(9,Math.round(hn*6 + T.foam*3.4));
    water.setColorAt(i,seaRamp[k]);
  }
  water.instanceMatrix.needsUpdate=true;
  if(water.instanceColor) water.instanceColor.needsUpdate=true;

  /* ship rides the same swell */
  const sw=0.55+0.45*Math.sin(t*0.21+1.1);
  shipGroup.position.y = waveH(-11,-2,t)*0.72*sw - 0.25;
  shipGroup.rotation.z = (waveH(-16,-2,t)-waveH(-6,-2,t))*0.055;
  shipGroup.rotation.x = (waveH(-11,-12,t)-waveH(-11,8,t))*0.030;
  shipGroup.updateMatrixWorld();

  /* mooring lines */
  ropes.forEach((r,i)=>{
    const a=r.a, b=shipGroup.localToWorld(moorPts[i].copy(r.b));
    const dist=a.distanceTo(b), sag=Math.max(0.2, 3.4-dist*0.22);
    const pos=r.obj.geometry.attributes.position;
    for(let k=0;k<pos.count;k++){
      const u=k/(pos.count-1);
      tmpV.lerpVectors(a,b,u); tmpV.y -= Math.sin(Math.PI*u)*sag + Math.sin(t*1.6+u*4)*0.06;
      pos.setXYZ(k,tmpV.x,tmpV.y,tmpV.z);
    }
    pos.needsUpdate=true; r.obj.geometry.computeBoundingSphere();
  });

  /* flags */
  FLAGS.forEach(f=>{
    const maxI=f.list.reduce((m,o)=>Math.max(m,o.i),0);
    f.list.forEach((o,i)=>{
      const w=o.i/maxI;
      dummy.position.set(o.base.x + o.dir*o.i*1.0, o.base.y + Math.sin(t*5+o.i*0.7)*0.16*o.j/w,
                         o.base.z + Math.sin(t*6.2+o.i*0.85)*0.55*w);
      dummy.rotation.set(0,0,Math.sin(t*6+o.i)*0.12);
      dummy.scale.set(1,1,1); dummy.updateMatrix(); f.m.setMatrixAt(i,dummy.matrix);
    });
    f.m.instanceMatrix.needsUpdate=true;
  });

  /* pier crane */
  craneGrp.rotation.y=Math.sin(t*0.16)*0.9+0.55;
  const tip=new THREE.Vector3(0,6,10).applyMatrix4(craneGrp.matrixWorld);
  const drop=4.5+Math.sin(t*0.7)*1.1;
  hookBox.position.set(tip.x,tip.y-drop,tip.z);
  hookBox.rotation.y=craneGrp.rotation.y;
  const hp=hookRope.geometry.attributes.position;
  hp.setXYZ(0,tip.x,tip.y,tip.z); hp.setXYZ(1,tip.x,hookBox.position.y+1,tip.z); hp.needsUpdate=true;
  hookRope.geometry.computeBoundingSphere();

  /* gulls */
  gulls.forEach((g,i)=>{
    const a=t*g.sp+g.ph;
    g.g.position.set(g.cx+Math.cos(a)*g.r, g.y+Math.sin(a*1.7+i)*3.4, g.cz+Math.sin(a)*g.r);
    g.g.rotation.y=-a+Math.PI/2;
    g.g.rotation.z=-Math.sin(a)*0.25;
    const f=Math.sin(t*7+g.ph)*0.75;
    g.wl.rotation.z=-f; g.wr.rotation.z=f;
  });

  /* smoke */
  puffs.forEach((p,i)=>{
    p.t+=dt*p.sp;
    if(p.t>1){ p.t=0; p.src=SMOKERS[i%SMOKERS.length]; }
    const s=p.src, k=p.t;
    dummy.position.set(s.x+Math.sin(k*4+s.x)*1.6+k*3.4, s.y+k*9, s.z+Math.cos(k*3+s.z)*1.2+k*1.1);
    dummy.scale.setScalar(0.7+k*2.6); dummy.rotation.set(k*2,k*1.4,0); dummy.updateMatrix();
    puffMesh.setMatrixAt(i,dummy.matrix);
  });
  puffMesh.instanceMatrix.needsUpdate=true;

  /* clouds + lighthouse */
  cloudGrp.position.x=((t*1.1)%220)-110;
  if(beamGrp.visible) beamGrp.rotation.y+=dt*0.55;

  /* markers */
  POIS.forEach(p=>{
    if(!p.el) return;
    tmpV2.copy(p.anchor).project(camera);
    const vis = tmpV2.z<1 && Math.abs(tmpV2.x)<1.05 && Math.abs(tmpV2.y)<1.05;
    const d=camera.position.distanceTo(p.anchor);
    p.el.style.opacity=vis?THREE.MathUtils.clamp(1.25-d/155,0,1):0;
    p.el.style.transform=`translate(${(tmpV2.x*0.5+0.5)*innerWidth}px,${(-tmpV2.y*0.5+0.5)*innerHeight}px) translate(-4px,-50%)`;
    p.el.style.pointerEvents=vis?'auto':'none';
  });

  /* camera flight */
  if(flight){
    flight.k=Math.min(1,flight.k+dt/1.35);
    const e=flight.k<0.5?4*flight.k**3:1-Math.pow(-2*flight.k+2,3)/2;
    camera.position.lerpVectors(flight.p0,flight.p1,e);
    controls.target.lerpVectors(flight.t0,flight.t1,e);
    if(flight.k>=1){ controls.autoRotate=flight.wasOrbit && controls.autoRotate!==undefined; bOrbit.classList.toggle('on',controls.autoRotate); flight=null; }
  }
  controls.update();
  document.getElementById('cmp-rose').setAttribute('transform',
    `rotate(${THREE.MathUtils.radToDeg(Math.atan2(camera.position.x-controls.target.x, camera.position.z-controls.target.z))} 50 50)`);

  /* log readouts */
  acc+=dt; fAcc+=dt; fCnt++;
  if(fAcc>0.5){ fps=Math.round(fCnt/fAcc); fAcc=0; fCnt=0; }
  if(acc>0.25){
    acc=0;
    const tt=timeSl.value/1000, mins=Math.round((4*60)+tt*20*60);
    $('clock').textContent=String(Math.floor(mins/60)%24).padStart(2,'0')+':'+String(mins%60).padStart(2,'0');
    const tide=Math.sin(tt*7.1)*3.1+4.4;
    $('r-watch').textContent = tt<0.2?'Morning':tt<0.45?'Forenoon':tt<0.62?'Afternoon':tt<0.82?'Evening':'First watch';
    $('r-tide').textContent=tide.toFixed(1)+' m '+(Math.cos(tt*7.1)>0?'↑ flood':'↓ ebb');
    $('r-wind').textContent='12 kn WSW';
    $('r-swell').textContent=(0.35+0.42*(0.55+0.45*Math.sin(tt*0.21+1.1)*0+Math.abs(Math.sin(clock.elapsedTime*0.21+1.1)))).toFixed(1).slice(0,3)+' m';
    $('r-brg').textContent=String(Math.round((THREE.MathUtils.radToDeg(Math.atan2(camera.position.x-controls.target.x,camera.position.z-controls.target.z))+360)%360)).padStart(3,'0')+'°';
    $('r-hull').textContent='on berth, starboard';
    $('r-vox').textContent=TOTAL_VOXELS.toLocaleString();
    $('r-fps').textContent=fps;
  }

  renderer.render(scene,camera);
  requestAnimationFrame(tick);
}

/* ══════════════ 12 · go ══════════════ */
renderer.compile(scene,camera);
renderer.render(scene,camera);
document.getElementById('r-vox').textContent=TOTAL_VOXELS.toLocaleString();
requestAnimationFrame(()=>{
  document.getElementById('load').classList.add('gone');
  setTimeout(()=>document.getElementById('load').remove(),1400);
  tick();
});
</script>
</body>
</html>
```

**What's in it**

- **The ship is procedural**: hull profiles (sheer, deadwood rise, flared bow, full stern) are generated by curves, then waled, gunported, planked and railed; three masts with yards, bellied square sails, a mizzen trysail, bowsprit with spritsail, capstan, hatches, coopered cargo, longboat and crew. Rigging is real line geometry so it moves with her.
- **One shared sea**: water tiles and the ship sample the *same* wave field, so she rolls and pitches against three catenary mooring lines that re-sag every frame.
- **Daylight scrubber** interpolates eight keyed phases — sun vector, sky gradient, fog, exposure, sea ramp, specular tint — and the windows, lanterns, beacons, point light and rotating beam all fade up as the sun goes down.
- **Navigation**: drag to orbit, wheel to dolly, `R` to reset, `Space` to pause orbit; the chart index and the pulsing in-world markers fly the camera to framed views; the compass rose tracks your heading.