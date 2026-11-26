Here's a complete, self‑contained voxel diorama. Save it as an `.html` file and open it in Chrome — it renders instantly, you can drag to orbit, scroll to zoom, and click the "⚓" button to set the ship in motion into the harbor.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Harbor Call — Voxel Diorama</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,600;0,9..144,900;1,9..144,500&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
  :root{
    --paper:#f2e7d2; --ink:#20303f; --ink-soft:#4a5a66; --gold:#c99a3e;
    --line:rgba(32,48,63,.28); --panel:rgba(246,238,222,.82);
  }
  *{box-sizing:border-box}
  html,body{margin:0;height:100%;overflow:hidden;background:#8fb4d0}
  #app{position:fixed;inset:0}
  canvas{display:block;cursor:grab}
  .vignette{position:fixed;inset:0;pointer-events:none;z-index:2;
    box-shadow:inset 0 0 170px 22px rgba(14,30,44,.42)}
  .grain{position:fixed;inset:0;pointer-events:none;z-index:3;opacity:.045;mix-blend-mode:multiply;
    background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")}

  .overlay{position:fixed;z-index:5;pointer-events:none;transition:opacity .9s ease,transform .9s ease}
  .overlay.hide{opacity:0;transform:translateY(10px)}

  .topbar{top:0;left:0;right:0;display:flex;justify-content:space-between;align-items:flex-start;
    padding:22px 26px;gap:16px}
  .brand{display:flex;align-items:center;gap:12px}
  .brand svg{width:34px;height:34px;color:var(--paper);filter:drop-shadow(0 2px 4px rgba(0,0,0,.35))}
  .brand b{font-family:'Space Mono',monospace;font-weight:700;font-size:15px;letter-spacing:.28em;
    color:var(--paper);text-transform:uppercase;text-shadow:0 2px 6px rgba(0,0,0,.4)}
  .brand small{display:block;font-family:'Space Mono',monospace;font-size:10px;letter-spacing:.18em;
    color:rgba(242,231,210,.7);margin-top:2px}

  .hud{background:var(--panel);backdrop-filter:blur(3px);border:1.5px solid var(--line);
    border-radius:3px;padding:9px 13px;display:flex;align-items:center;gap:11px;
    box-shadow:0 8px 24px rgba(20,30,40,.25)}
  .compass{width:30px;height:30px}
  .compass .ring{fill:none;stroke:var(--ink);stroke-width:1.4;opacity:.85}
  .compass .needle{transition:transform .12s linear;transform-box:fill-box;transform-origin:center}
  .compass text{font-family:'Space Mono',monospace;font-size:7px;fill:var(--ink-soft)}
  .coord{font-family:'Space Mono',monospace;font-size:12px;color:var(--ink);min-width:118px}
  .coord .k{color:var(--ink-soft)}
  .clock{font-family:'Space Mono',monospace;font-size:12px;color:var(--gold);font-weight:700;
    letter-spacing:.06em;padding-left:11px;border-left:1px solid var(--line)}

  .plaque{left:26px;bottom:26px;max-width:min(48vw,540px);
    background:var(--panel);backdrop-filter:blur(3px);border:1.5px solid var(--line);
    border-radius:4px;padding:18px 22px 16px;box-shadow:0 14px 40px rgba(20,30,40,.3)}
  .kicker{font-family:'Space Mono',monospace;font-size:11px;letter-spacing:.22em;text-transform:uppercase;
    color:var(--ink-soft);margin:0 0 6px}
  .title{font-family:'Fraunces',serif;font-weight:900;font-size:clamp(26px,4.4vw,44px);line-height:.94;
    color:var(--ink);margin:0;letter-spacing:-.01em}
  .title em{font-style:italic;font-weight:600;color:#b0532a}
  .sub{font-family:'Fraunces',serif;font-style:italic;font-size:15px;color:var(--ink-soft);margin:6px 0 0}
  .spec{margin:12px 0 0;font-family:'Space Mono',monospace;font-size:10.5px;letter-spacing:.14em;
    text-transform:uppercase;color:var(--ink-soft)}

  .controls{right:26px;bottom:26px;display:flex;flex-direction:column;align-items:flex-end;gap:10px}
  button{font-family:'Space Mono',monospace;cursor:pointer;pointer-events:auto;border:1.5px solid var(--ink);
    border-radius:3px;transition:transform .16s ease,background .2s,box-shadow .2s,opacity .2s}
  .btn-primary{display:flex;align-items:center;gap:9px;background:var(--gold);color:#241a08;border-color:#8a6a1f;
    padding:12px 18px;font-size:13px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;
    box-shadow:0 8px 22px rgba(20,30,40,.3),inset 0 1px 0 rgba(255,255,255,.4)}
  .btn-primary:hover{transform:translateY(-2px);background:#d7a94c;box-shadow:0 12px 28px rgba(20,30,40,.35)}
  .btn-primary:active{transform:translateY(0)}
  .btn-primary svg{width:18px;height:18px}
  .btn-primary.running{background:var(--ink);color:var(--paper);border-color:var(--ink)}
  .btn-ghost{background:rgba(242,231,210,.72);color:var(--ink);padding:9px 13px;font-size:11px;
    letter-spacing:.1em;text-transform:uppercase}
  .btn-ghost:hover{transform:translateY(-2px);background:var(--paper)}
  .btn-ghost.on{background:var(--ink);color:var(--paper);border-color:var(--ink)}
  .btn-ghost:focus-visible,.btn-primary:focus-visible{outline:2px solid var(--gold);outline-offset:2px}

  .hint{position:fixed;left:50%;bottom:16px;transform:translateX(-50%);z-index:5;pointer-events:none;
    font-family:'Space Mono',monospace;font-size:11px;letter-spacing:.14em;text-transform:uppercase;
    color:rgba(242,231,210,.82);text-shadow:0 1px 4px rgba(0,0,0,.5);transition:opacity .5s}
  .hint.gone{opacity:0}
  .loader{position:fixed;inset:0;z-index:9;display:grid;place-items:center;background:#8fb4d0;
    font-family:'Space Mono',monospace;font-size:12px;letter-spacing:.24em;text-transform:uppercase;color:#22323f}
  .loader.gone{opacity:0;pointer-events:none;transition:opacity .6s}

  @media (max-width:720px){
    .coord{display:none}
    .plaque{left:14px;right:14px;bottom:14px;max-width:none}
    .controls{right:14px;bottom:96px}
    .hint{bottom:186px}
  }
</style>
</head>
<body>
  <div id="app"></div>
  <div class="vignette"></div>
  <div class="grain"></div>

  <div class="overlay topbar">
    <div class="brand">
      <svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M16 4v24M6 24a10 10 0 0 0 20 0M4 12h24M8 8h16"/>
        <circle cx="16" cy="7" r="3"/>
      </svg>
      <div><b>Harbor Call</b><small>voxel diorama · three.js</small></div>
    </div>
    <div class="hud">
      <svg class="compass" viewBox="0 0 30 30">
        <circle class="ring" cx="15" cy="15" r="12"/>
        <text x="15" y="6" text-anchor="middle">N</text>
        <g class="needle" id="needle">
          <path d="M15 6 L18 15 L15 13 L12 15 Z" fill="#b0532a"/>
          <path d="M15 24 L12 15 L15 17 L18 15 Z" fill="#5a6a76"/>
        </g>
      </svg>
      <div class="coord"><span class="k">HEADING</span> <span id="heading">000°</span></div>
      <div class="clock" id="clock">—</div>
    </div>
  </div>

  <div class="overlay plaque">
    <p class="kicker">No. 03 · coastal approach</p>
    <h1 class="title">Calling at the <em>Harbor</em></h1>
    <p class="sub">a three-masted brig, all sails set, riding the evening tide toward the quay.</p>
    <p class="spec">128³ voxel world · one draw call · hand-cut geometry</p>
  </div>

  <div class="overlay controls">
    <button class="btn-primary" id="sail">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 3v18M5 21a7 7 0 0 0 14 0M3 12h18M7 8h10"/><circle cx="12" cy="6" r="2"/>
      </svg>
      <span>Set Sail</span>
    </button>
    <button class="btn-ghost" id="pause">Pause</button>
    <button class="btn-ghost" id="reset">Reset View</button>
  </div>

  <div class="hint" id="hint">Drag to orbit · scroll to zoom · click ⚓ to set sail</div>
  <div class="loader" id="loader">Laying keel…</div>

<script type="importmap">
{ "imports": {
  "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
  "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
}}
</script>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

/* ---------- renderer / scene ---------- */
const app = document.getElementById('app');
const renderer = new THREE.WebGLRenderer({ antialias:true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
app.appendChild(renderer.domElement);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(42, innerWidth/innerHeight, 0.1, 600);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true; controls.dampingFactor = 0.06;
controls.minDistance = 12; controls.maxDistance = 150;
controls.maxPolarAngle = 1.5;

/* ---------- shared state ---------- */
const world = new THREE.Group(); scene.add(world);
const ship = new THREE.Group(); world.add(ship);
let shipSway = 0;
const shipPath = [ new THREE.Vector3(-34,0,6), new THREE.Vector3(-16,0,5),
                   new THREE.Vector3(-4,0,3), new THREE.Vector3(1,0,1) ];
const shipCurve = new THREE.CatmullRomCurve3(shipPath);
const shipBox = new THREE.Box3(new THREE.Vector3(-6,-3,-1.6), new THREE.Vector3(6,6,1.6));

/* ---------- helpers ---------- */
const rand = (a,b)=> a + Math.random()*(b-a);
const hsl = (h,s,l)=> new THREE.Color().setHSL(h,s,l);
const shade = (hex,amt)=> new THREE.Color(hex).offsetHSL(0,0,amt);

function shadePalette(base, n=5){
  const c=[]; for(let i=0;i<n;i++) c.push(shade(base, 0.10 - i*0.05)); return c;
}
function makePalette(hex){
  const base = new THREE.Color(hex);
  const dark = base.clone().multiplyScalar(0.70);
  const light = base.clone().multiplyScalar(1.16);
  const pal = [];
  for(let i=0;i<5;i++) pal.push(light.clone().lerp(dark, i/4));
  return pal;
}

/* ---------- sky (gradient dome) ---------- */
const sky = new THREE.Mesh(
  new THREE.SphereGeometry(400, 32, 24),
  new THREE.ShaderMaterial({
    side:THREE.BackSide, depthWrite:false,
    uniforms:{ top:{value:new THREE.Color('#3a6ea5')}, bot:{value:new THREE.Color('#f2dca6')} },
    vertexShader:`varying float h; void main(){ h=normalize(position).y; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);} `,
    fragmentShader:`uniform vec3 top; uniform vec3 bot; varying float h;
      void main(){ float t=clamp(h*0.5+0.5,0.0,1.0); t=pow(t,0.85); gl_FragColor=vec4(mix(bot,top,t),1.0);} `
  })
);
sky.renderOrder=-1; scene.add(sky);

/* ---------- lights ---------- */
const sunDir = new THREE.Vector3(-0.55, 0.5, 0.35).normalize();
const sun = new THREE.DirectionalLight(0xffd6a0, 2.7);
sun.position.copy(sunDir).multiplyScalar(140);
sun.castShadow = true;
sun.shadow.mapSize.set(2048,2048);
sun.shadow.camera.near=1; sun.shadow.camera.far=340;
sun.shadow.camera.left=-72; sun.shadow.camera.right=72;
sun.shadow.camera.top=72; sun.shadow.camera.bottom=-72;
sun.shadow.bias=-0.0006; sun.shadow.normalBias=0.6;
scene.add(sun); scene.add(sun.target);
scene.add(new THREE.HemisphereLight(0xbcd6ea, 0x6e5a44, 0.55));
scene.add(new THREE.AmbientLight(0x404a55, 0.25));

/* ---------- sun disc + glow ---------- */
const sunPos = sunDir.clone().multiplyScalar(300);
const sunDisc = new THREE.Mesh(new THREE.SphereGeometry(14,24,24),
  new THREE.MeshBasicMaterial({color:0xfff2cf, toneMapped:false}));
sunDisc.position.copy(sunPos); scene.add(sunDisc);
const glowTex = (()=>{ const c=document.createElement('canvas'); c.width=c.height=128;
  const g=c.getContext('2d'); const gr=g.createRadialGradient(64,64,0,64,64,64);
  gr.addColorStop(0,'rgba(255,242,205,0.9)'); gr.addColorStop(1,'rgba(255,242,205,0)');
  g.fillStyle=gr; g.fillRect(0,0,128,128); return new THREE.CanvasTexture(c); })();
const glow = new THREE.Sprite(new THREE.SpriteMaterial({map:glowTex, color:0xfff0cf,
  transparent:true, blending:THREE.AdditiveBlending, depthWrite:false, opacity:0.85}));
glow.position.copy(sunPos); glow.scale.set(150,150,1); scene.add(glow);

/* ---------- water ---------- */
const SIZE=128, HALF=64;
const waterGeo = new THREE.PlaneGeometry(SIZE, SIZE, 48, 48);
const waterMat = new THREE.MeshStandardMaterial({ color:0x2f6f78, roughness:0.30, metalness:0.12 });
const water = new THREE.Mesh(waterGeo, waterMat);
water.rotation.x = -Math.PI/2; water.receiveShadow = true; scene.add(water);
const waterBase = Float32Array.from(waterGeo.attributes.position.array);

/* ---------- voxel system ---------- */
const voxels = [];
const addVoxel = (x,y,z,color)=> voxels.push({x,y,z,color});
const addBox = (x0,y0,z0,x1,y1,z1,color)=>{
  for(let x=Math.min(x0,x1);x<=Math.max(x0,x1);x++)
   for(let y=Math.min(y0,y1);y<=Math.max(y0,y1);y++)
    for(let z=Math.min(z0,z1);z<=Math.max(z0,z1);z++) addVoxel(x,y,z,color);
};

/* ---------- terrain ---------- */
const heightAt = (x,z)=>{
  let h = 18 + Math.cos(z*0.05)*12 + Math.sin(x*0.06)*6 + Math.cos((x+z)*0.03)*5;
  const d = Math.hypot(x-2, z-26);
  h -= Math.exp(-(d*d)/160)*18;              // harbor basin
  h += Math.exp(-((x+20)**2)/70 - ((z+10)**2)/70)*10; // far headland
  return h;
};
const land = [];
for(let x=-HALF;x<HALF;x++) for(let z=-HALF;z<HALF;z++){
  let h = heightAt(x,z);
  let type=null;
  if(h<=1) type='sand';
  else if(h<=3) type='grass';
  else if(h<=6) type='grass';
  else if(h<=9) type='rock';
  else if(h<=12) type='rock';
  else type='snow';
  if(type==='sand' && z>30 && x>4 && x<40) type='grass'; // beach
  if(x>2 && x<20 && z>-6 && z<6) type='sand';            // docked area
  land.push({x,z,h:Math.round(h),type});
}
const landMap = new Map(); land.forEach(t=> landMap.set(t.x+','+t.z, t));
const isLand = (x,z)=>{ const t=landMap.get(x+','+z); return !!t && t.h>1; };

/* ---------- trees ---------- */
const trunkPal = makePalette('#7a4a24');
const leafPal  = makePalette('#3f7a38');
function addTree(x, z, h){
  addBox(x, h, z, x, h+2, z, trunkPal);
  const t = h+2;
  addBox(x-1, t,   z-1, x+1, t,   z+1, leafPal);
  addBox(x-1, t+1, z-1, x+1, t+1, z,   leafPal);
  addBox(x,   t+2, z,   x,   t+2, z,   leafPal);
}

/* ---------- lighthouse ---------- */
function addLighthouse(cx, cz){
  const base = landMap.get(cx+','+cz).h;
  for(let y=1;y<=15;y++){
    const r = y<=6 ? 2 : (y<=12 ? 1 : 0);
    for(let dx=-r;dx<=r;dx++) for(let dz=-r;dz<=r;dz++){
      if(dx*dx+dz*dz > r*r+0.4) continue;
      let col = shade(0xefe6d6, 0.10);
      if(y>2 && (y%2===0)) col = shade(0xb23a2e, 0.06);
      addVoxel(cx+dx, base+y, cz+dz, col);
    }
  }
  for(let dx=-1;dx<=1;dx++) for(let dz=-1;dz<=1;dz++) addVoxel(cx+dx, base+16, cz+dz, shade(0x2b2f36,0.05));
  addVoxel(cx, base+17, cz, '#ffe6a0');
}

/* ---------- dock ---------- */
function addDock(){
  const bx=2, bz=2;
  const topY=4, deckH=1, legH=2;
  for(let z=-6;z<=6;z++) addBox(bx,topY,bz, bx,topY+deckH,bz, makePalette('#9c6f3c'));
  for(let z=-6;z<=6;z+=3) for(let y=0;y<legH;y++) addVoxel(bx, y, z, shade(0x5b3f22,0.02));
  addVoxel(bx, topY+2, 6, '#ffe6a0');
  addVoxel(bx, topY+1, 6, shade(0x2b2f36,0.05));
}

/* ---------- ship ---------- */
const hullPal = makePalette('#6b4a2a');
const trimPal = makePalette('#d9c9a0');
const deckPal = makePalette('#a87c4a');
const sailPal = makePalette('#efe6d2');
const mastPal = makePalette('#5b3f22');
const yardPal = makePalette('#4a3119');
function addMast(x,z,h){ addBox(x,0,z, x,h,z, mastPal); }
function addSails(x,z,bottom){
  const cols=[-1,1];
  for(let xoff of cols){
    const mx=x+xoff;
    addBox(mx, bottom+2, z-1, mx, bottom+9, z+1, sailPal);
    addBox(mx, bottom+10, z-1, mx, bottom+13, z, sailPal);
    addBox(mx-1, bottom+1, z, mx+1, bottom+1, z, yardPal);
    addBox(mx-1, bottom+9, z, mx+1, bottom+9, z, yardPal);
    addBox(mx-1, bottom+13, z, mx+1, bottom+13, z, yardPal);
  }
  addBox(x, bottom+1, z, x, bottom+7, z, sailPal);
  addBox(x-1, bottom, z, x+1, bottom, z, yardPal);
}
function buildShip(){
  const W=5, L=13, D=2, y0=0, y1=3;
  for(let y=y0;y<=y1;y++){
    const inset = y===0 ? 1 : 0;
    for(let dx=-W+inset; dx<=W-inset; dx++)
      for(let dz=-L+inset; dz<=L-inset; dz++){
        const bow = dz>9; let cut = 0;
        if(bow){ cut = Math.round((dz-9)*0.8); if(Math.abs(dx)>W-1-cut) continue; }
        addVoxel(dx, y, dz, hullPal);
      }
  }
  for(let z=-L+1; z<=L-1; z++) for(let x=-W; x<=W; x++) addVoxel(x, y1, z, deckPal);
  for(let x=-W; x<=W; x++) for(let z=-L; z<=L; z++){
    if(Math.abs(z)>L-2){ addVoxel(x,4,z, trimPal); continue; }
    if(Math.abs(x)>W-1){ addVoxel(x,4,z, trimPal); continue; }
    addVoxel(x,4,z, deckPal);
  }
  for(let dx=-W+1; dx<=W-1; dx+=2) for(let z=-L+2; z<=L-2; z++) addVoxel(dx,5,z, shade(0x3a2a18,0.02));
  addBox(-3, 5, -6, 3, 7, 2, hullPal);
  addBox(-2, 8, -5, 2, 9, 1, shade(0x7a4a24,0.06));
  for(let z=-5; z<=1; z+=2) for(let x=-2; x<=2; x+=2) addVoxel(x, 6, z, '#cfe0ea');
  addMast(-2, 0, 16); addMast(2, 0, 19);
  addSails(0, 0, y1);
  addBox(0, 10, 0, 0, 22, 0, mastPal);
  addBox(-5, 5, -1, 5, 6, -1, trimPal);
  addBox(0, 19, -6, 0, 22, 6, trimPal);
  addVoxel(0, 23, 0, '#ffe6a0');
}

/* ---------- populate world ---------- */
buildShip();
addDock();

const placedTrees = [];
for(const t of land){
  if(t.type==='snow') continue;
  addBox(t.x, 0, t.z, t.x, t.h, t.z, makePalette('#d8cbae'));
}
for(const t of land){
  if(t.type==='snow') continue;
  addVoxel(t.x, t.h+1, t.z, makePalette(t.type==='grass' ? '#6f9a4a' : (t.type==='sand' ? '#e2d6b8' : '#8a837a')));
}
for(const t of land){
  if(t.type!=='grass' || t.h<3 || t.z>20) continue;
  if(Math.random()>0.10) continue;
  let ok=true;
  for(const p of placedTrees) if(Math.hypot(p.x-t.x, p.z-t.z)<3){ ok=false; break; }
  if(ok){ placedTrees.push(t); addTree(t.x, t.z, t.h); }
}
addLighthouse(14, 24);

/* ---------- build merged instanced mesh ---------- */
const n = voxels.length;
const geo = new THREE.BoxGeometry(1,1,1);
const mesh = new THREE.InstancedMesh(geo, new THREE.MeshLambertMaterial(), n);
mesh.castShadow = true; mesh.receiveShadow = true;
const dummy = new THREE.Object3D(), col = new THREE.Color();
const baseColors = [];
for(let i=0;i<n;i++){
  const v=voxels[i];
  dummy.position.set(v.x+0.5, v.y+0.5, v.z+0.5); dummy.updateMatrix();
  mesh.setMatrixAt(i, dummy.matrix);
  col.set(v.color); baseColors[i]=col.clone(); mesh.setColorAt(i, col);
}
mesh.instanceMatrix.needsUpdate=true;
if(mesh.instanceColor) mesh.instanceColor.needsUpdate=true;
world.add(mesh);

/* ---------- reflections (mirrored ship) ---------- */
const refl = new THREE.Group();
refl.rotation.x = Math.PI;
refl.scale.y = 0.55;
refl.position.y = -0.1;
world.add(refl);
const reflMat = new THREE.MeshLambertMaterial({ transparent:true, opacity:0.16, depthWrite:false, color:0x9fb7c0 });
const reflMesh = new THREE.InstancedMesh(geo, reflMat, n);
for(let i=0;i<n;i++){ reflMesh.setMatrixAt(i, mesh.getMatrixAt(i, new THREE.Matrix4()));
  reflMesh.setColorAt(i, baseColors[i]); }
reflMesh.instanceMatrix.needsUpdate=true;
if(reflMesh.instanceColor) reflMesh.instanceColor.needsUpdate=true;
refl.add(reflMesh);

/* ---------- foam ---------- */
const foam = new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1),
  new THREE.MeshLambertMaterial({ color:0xeaf3f0 }), 260);
foam.castShadow=false;
const foamData=[];
for(let i=0;i<260;i++){
  let x,z;
  if(Math.random()<0.45){ x=rand(-40,40); z=rand(-40,40); }
  else { const a=rand(0,Math.PI*2), r=rand(5,13); x=Math.cos(a)*r; z=Math.sin(a)*r; }
  foamData.push({x,z, s:rand(0.4,1.0), ph:rand(0,Math.PI*2)});
}
world.add(foam);

/* ---------- birds ---------- */
const birdMat = new THREE.MeshLambertMaterial({ color:0x2b2a26 });
const birds=[];
for(let i=0;i<5;i++){
  const g=new THREE.Group();
  g.add(new THREE.Mesh(new THREE.BoxGeometry(0.6,0.4,1.6), birdMat));
  const w1=new THREE.Mesh(new THREE.BoxGeometry(2.4,0.2,0.5), birdMat); w1.position.set(1.5,0.25,0);
  const w2=new THREE.Mesh(new THREE.BoxGeometry(2.4,0.2,0.5), birdMat); w2.position.set(-1.5,0.25,0);
  g.add(w1,w2);
  birds.push({g, w1, w2, r:rand(18,34), a:rand(0,6.28), sp:rand(0.1,0.22),
    y:rand(22,34), ph:rand(0,6.28), dir:Math.random()<0.5?1:-1});
  world.add(g);
}

/* ---------- post processing ---------- */
const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
const bloom = new UnrealBloomPass(new THREE.Vector2(innerWidth, innerHeight), 0.55, 0.5, 0.82);
composer.addPass(bloom);
composer.addPass(new OutputPass());

/* ---------- camera intro ---------- */
const target = new THREE.Vector3(0, 3, 0);
const camEnd = new THREE.Vector3(50, 30, 62);
const camFrom = new THREE.Vector3(130, 90, 170);
camera.position.copy(camFrom);
controls.target.copy(target);
let intro = true, introT = 0;

/* ---------- UI ---------- */
const headingEl = document.getElementById('heading');
const clockEl = document.getElementById('clock');
const needle = document.getElementById('needle');
const hint = document.getElementById('hint');
const sailBtn = document.getElementById('sail');
const pauseBtn = document.getElementById('pause');
const resetBtn = document.getElementById('reset');

let running=false, paused=false;
sailBtn.addEventListener('click', ()=>{
  running = !running;
  sailBtn.classList.toggle('running', running);
  sailBtn.querySelector('span').textContent = running ? 'Drop Anchor' : 'Set Sail';
});
pauseBtn.addEventListener('click', ()=>{ paused=!paused; pauseBtn.textContent = paused?'Resume':'Pause'; });
resetBtn.addEventListener('click', ()=>{ intro=false; introT=0; camera.position.copy(camFrom); controls.target.copy(target); });

renderer.domElement.addEventListener('pointerdown', ()=> hint.classList.add('gone'), {once:true});
window.addEventListener('keydown', e=>{
  if(e.code==='Space'){ e.preventDefault(); sailBtn.click(); }
  if(e.key==='p'||e.key==='P') pauseBtn.click();
  if(e.key==='r'||e.key==='R') resetBtn.click();
});

/* ---------- animation ---------- */
const clock = new THREE.Clock();
const tmpC = new THREE.Color();
function animate(){
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const et = clock.elapsedTime;

  if(intro){ introT += dt/2.4;
    const e = introT>=1 ? 1 : 1-Math.pow(1-introT,3);
    camera.position.lerpVectors(camFrom, camEnd, e);
    if(introT>=1){ intro=false; controls.update(); }
  }

  // water
  const pa = waterGeo.attributes.position;
  for(let i=0;i<pa.count;i++){
    const x=waterBase[i*3], y=waterBase[i*3+1];
    pa.array[i*3+2] = Math.sin(x*0.35+et*1.6)*0.18 + Math.cos(y*0.4+et*1.1)*0.16
                    + Math.sin((x+y)*0.18+et*0.8)*0.10;
  }
  pa.needsUpdate = true;

  // ship
  shipSway += dt;
  if(running){
    const tt = (Math.sin(shipSway*0.16)*0.5+0.5)*0.999;
    ship.position.copy(shipCurve.getPoint(tt));
    ship.rotation.y = Math.atan2(shipCurve.getTangent(tt).x, shipCurve.getTangent(tt).z);
  } else {
    ship.position.set(1, 0, 1);
    ship.rotation.y = -Math.PI/2;
  }
  ship.rotation.x = Math.sin(shipSway*1.4)*0.02;
  ship.rotation.z = Math.cos(shipSway*1.1)*0.018;
  ship.position.y = Math.sin(shipSway*1.6)*0.12;
  refl.position.y = -0.1 + ship.position.y*0.55;

  // foam
  for(let i=0;i<foamData.length;i++){
    const f=foamData[i];
    dummy.position.set(f.x, 0.35 + Math.sin(et*2+f.ph)*0.15, f.z);
    const s = f.s*(0.8 + 0.2*Math.sin(et*3+f.ph));
    dummy.scale.set(s, 0.2, s); dummy.updateMatrix();
    foam.setMatrixAt(i, dummy.matrix);
  }
  foam.instanceMatrix.needsUpdate = true;

  // birds
  for(const b of birds){
    b.a += b.sp*dt;
    b.g.position.set(Math.cos(b.a)*b.r, b.y + Math.sin(et*0.6+b.ph)*1.2, Math.sin(b.a)*b.r);
    b.g.rotation.y = -b.a + (b.dir>0?0:Math.PI);
    const fl = Math.sin(et*6+b.ph)*0.5;
    b.w1.rotation.z = fl; b.w2.rotation.z = -fl;
  }

  // lights
  sun.position.copy(sunDir).multiplyScalar(140);
  const day = 0.5 + 0.5*Math.sin(et*0.12);
  const warm = new THREE.Color().setHSL(0.07 + (1-day)*0.02, 0.6, 0.55 + day*0.12);
  sun.color.copy(warm); sun.intensity = 1.6 + day*1.6;
  sky.material.uniforms.bot.value.copy(warm).lerp(new THREE.Color('#f6e6c0'), day);
  sky.material.uniforms.top.value.copy(new THREE.Color('#2c5a8c')).lerp(new THREE.Color('#6f9ecb'), day);
  sunDisc.color.copy(warm).lerp(new THREE.Color('#ffffff'), day*0.4);

  // reflections
  reflMat.opacity = 0.11 + day*0.09;

  // HUD
  const dir = new THREE.Vector3().subVectors(camera.position, controls.target);
  const az = ((Math.atan2(dir.x, dir.z)*180/Math.PI)+360)%360;
  headingEl.textContent = String(Math.round(az)).padStart(3,'0')+'°';
  needle.style.transform = `rotate(${az}deg)`;
  const secs = Math.floor(et);
  clockEl.textContent = String(Math.floor(secs/60)).padStart(2,'0')+':'+String(secs%60).padStart(2,'0');

  if(!intro) controls.update();
  composer.render();
}
animate();
document.getElementById('loader').classList.add('gone');

/* ---------- resize ---------- */
addEventListener('resize', ()=>{
  const w=innerWidth, h=innerHeight;
  camera.aspect = w/h; camera.updateProjectionMatrix();
  renderer.setSize(w,h); composer.setSize(w,h); bloom.setSize(w,h);
});
</script>
</body>
</html>
```

**Controls**
- **Drag** to orbit, **scroll** to zoom, **click** to pan.
- **Set Sail** (or `Space`) — the brig glides in along a curved approach and settles at the dock.
- **Pause** (`P`) freezes the whole scene; **Reset View** (`R`) re-runs the cinematic pull‑in.

Everything is one merged instanced draw call (plus a mirrored ship for reflections, animated foam, circling gulls, and a breathing sun), so it stays fast while the tide, sails, and light keep moving.