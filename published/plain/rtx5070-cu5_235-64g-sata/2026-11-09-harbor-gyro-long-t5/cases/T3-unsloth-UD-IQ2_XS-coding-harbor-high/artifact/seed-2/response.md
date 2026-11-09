# Calling at Harbour — a voxel diorama

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Calling at Harbour — Voxel Diorama</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=Manrope:wght@400;500;700;800&display=swap" rel="stylesheet">
<style>
  :root{
    --ink:#0a1218; --paper:#e8ded0; --brass:#d9a441; --slate:#1b2a32;
    --line:rgba(232,222,208,.18);
  }
  *{box-sizing:border-box;margin:0;padding:0}
  html,body{height:100%;overflow:hidden;background:#08111a;font-family:'Manrope',system-ui,sans-serif;color:var(--paper)}
  canvas{display:block;position:fixed;inset:0}
  .grain,.vig{position:fixed;inset:0;pointer-events:none}
  .vig{background:radial-gradient(120% 90% at 50% 45%, rgba(0,0,0,0) 40%, rgba(4,8,12,.55) 100%);z-index:3}
  .grain{z-index:4;opacity:.055;mix-blend-mode:overlay;
    background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='140' height='140'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3'/></filter><rect width='140' height='140' filter='url(%23n)'/></svg>")}

  /* ---------- notice board ---------- */
  #ui{position:fixed;inset:0;z-index:6;pointer-events:none}
  .plate{
    background:linear-gradient(180deg, rgba(14,22,28,.82), rgba(10,16,21,.72));
    border:1px solid var(--line);
    box-shadow:0 18px 40px -22px rgba(0,0,0,.9), inset 0 1px 0 rgba(255,255,255,.05);
    backdrop-filter:blur(3px);
  }
  #title{position:absolute;top:22px;left:24px;padding:14px 18px 13px;max-width:440px}
  #title .eyebrow{font-size:10px;letter-spacing:.42em;color:#8ba69d;text-transform:uppercase;margin-bottom:6px}
  #title h1{font-family:'Archivo Black',Impact,sans-serif;font-size:clamp(26px,3.4vw,44px);line-height:.92;
    letter-spacing:-.015em;text-transform:uppercase;color:#f6ecd9}
  #title h1 em{font-style:normal;color:var(--brass)}
  #title .rule{height:2px;background:linear-gradient(90deg,var(--brass),rgba(217,164,65,0));margin:12px 0 9px}
  #title p{font-size:12.5px;line-height:1.5;color:#b9c6c2;max-width:38ch}
  #title p b{color:#e9dcbf;font-weight:700}

  #log{position:absolute;left:24px;bottom:26px;padding:9px 13px;display:flex;gap:16px;align-items:baseline;
    font-size:10px;letter-spacing:.18em;text-transform:uppercase;color:#7f938c}
  #log span{font-family:'Archivo Black';font-size:14px;letter-spacing:0;color:#e9dcbf}
  #log .dot{width:6px;height:6px;background:var(--brass);border-radius:50%;box-shadow:0 0 10px var(--brass);animation:pulse 2.2s infinite ease-in-out}
  @keyframes pulse{0%,100%{opacity:.35;transform:scale(.8)}50%{opacity:1;transform:scale(1.15)}}

  #chips{position:absolute;top:24px;right:24px;display:flex;flex-direction:column;gap:8px;align-items:flex-end;pointer-events:auto}
  .chip{font-family:'Manrope';font-size:10.5px;font-weight:700;letter-spacing:.22em;text-transform:uppercase;
    padding:9px 14px;border:1px solid var(--line);background:rgba(10,16,21,.6);color:#a9bab5;cursor:pointer;
    position:relative;transition:transform .22s cubic-bezier(.2,.9,.25,1), color .22s, border-color .22s, background .3s}
  .chip:hover{color:#f6ecd9;border-color:rgba(217,164,65,.55);transform:translateX(-4px)}
  .chip:after{content:'';position:absolute;left:0;bottom:-1px;width:0;height:2px;background:var(--brass);transition:width .28s}
  .chip:hover:after{width:100%}
  .chip.on{background:var(--brass);color:#0d1720;border-color:var(--brass)}
  #hint{position:absolute;right:24px;bottom:26px;padding:8px 12px;font-size:10px;letter-spacing:.18em;
    text-transform:uppercase;color:#7f938c;max-width:300px;line-height:1.7;text-align:right;transition:opacity .8s}
  #hint b{color:#d9a441}

  #compass{position:absolute;right:24px;bottom:78px;width:88px;height:88px;pointer-events:auto;
    border-radius:50%;border:1px solid var(--line);background:radial-gradient(circle at 50% 50%, rgba(12,20,26,.85), rgba(8,14,19,.6))}
  #needle{position:absolute;inset:0;transition:transform .12s linear}
  #compass .card{position:absolute;left:50%;transform:translateX(-50%);font-size:9px;font-weight:800;letter-spacing:.15em;color:#93a69f}
  #compass .n{top:8px;color:var(--brass)}#compass .s{bottom:8px}#compass .e{right:8px;top:50%;transform:translateY(-50%);left:auto}
  #compass .w{left:8px;top:50%;transform:translateY(-50%)}
  #compass svg{position:absolute;inset:0}

  #toast{position:absolute;left:50%;top:52px;transform:translate(-50%,-14px);padding:9px 16px;
    font-size:11px;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:#f6ecd9;
    opacity:0;transition:opacity .35s, transform .35s;pointer-events:none}
  #toast.show{opacity:1;transform:translate(-50%,0)}

  #load{position:fixed;inset:0;z-index:20;background:#0a1218;display:flex;flex-direction:column;
    align-items:center;justify-content:center;gap:18px;transition:opacity .8s}
  #load.done{opacity:0;pointer-events:none}
  #load .t{font-family:'Archivo Black';font-size:clamp(20px,3vw,34px);letter-spacing:.1em;text-transform:uppercase;color:#f6ecd9}
  #load .bar{width:220px;height:2px;background:rgba(232,222,208,.15);overflow:hidden}
  #load .bar i{display:block;height:100%;width:40%;background:var(--brass);animation:slide 1.1s infinite ease-in-out}
  @keyframes slide{0%{transform:translateX(-110%)}100%{transform:translateX(260%)}}
  #load small{font-size:10px;letter-spacing:.3em;color:#7f938c;text-transform:uppercase}
</style>
<script type="importmap">
{ "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.160.1/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.1/examples/jsm/"
}}
</script>
</head>
<body>
<div id="ui">
  <div id="title" class="plate">
    <div class="eyebrow">Voxel Diorama · No. 04</div>
    <h1>Calling at <em>Harbour</em></h1>
    <div class="rule"></div>
    <p>A three-masted barque rides at her mooring off the town quay, topsails still full,
       colours flying. <b>Drag to orbit</b>, scroll to stand closer, and click the hull for a powder-damp salute.</p>
  </div>

  <div id="chips">
    <button class="chip" data-p="day">Forenoon watch</button>
    <button class="chip on" data-p="golden">Golden hour</button>
    <button class="chip" data-p="night">Night watch</button>
  </div>

  <div id="compass" class="plate">
    <svg viewBox="0 0 88 88"><g stroke="rgba(232,222,208,.22)" stroke-width="1">
      <circle cx="44" cy="44" r="34" fill="none"/>
      <path d="M44 12 L44 20 M44 68 L44 76 M12 44 L20 44 M68 44 L76 44" />
    </g></svg>
    <div id="needle">
      <div class="card n">N</div><div class="card e">E</div><div class="card s">S</div><div class="card w">W</div>
    </div>
  </div>

  <div id="hint" class="plate">drag · <b>orbit</b> &nbsp;|&nbsp; wheel · <b>zoom</b> &nbsp;|&nbsp; right-drag · <b>pan</b> &nbsp;|&nbsp; click · <b>interact</b></div>
  <div id="log" class="plate"><i class="dot"></i>voxels <span id="vcount">0</span> · <span id="fps">60</span> fps</div>
  <div id="toast" class="plate"></div>
</div>
<div class="vig"></div><div class="grain"></div>
<div id="load"><div class="t">Charting the course</div><div class="bar"><i></i></div><small>quarrying voxels</small></div>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* ══════════════════════════════════════════════════════════
   0 · UTILITIES
   ══════════════════════════════════════════════════════════ */
const clamp=(v,a,b)=>v<a?a:v>b?b:v;
function mulberry32(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
const rnd=mulberry32(0xB0B5A1C);
const rr=(a,b)=>a+(b-a)*rnd();
const ri=(a,b)=>Math.floor(a+(b-a+1)*rnd());
const pick=a=>a[ri(0,a.length-1)];
const jc=(hex,amt=0.05)=>new THREE.Color(hex).multiplyScalar(1+(rnd()*2-1)*amt);

const P = {
  hull:0x2a3a46, hullHi:0x384b57, bottom:0x18222a, copper:0x8f5a3a, stripe:0xc9913c,
  deck:0x9c7440, deckDk:0x7b5a31, spar:0x8a6a44, sparDk:0x634a2e, rig:0x4a3b2c,
  sail:0xe8dec4, sailDk:0xd2c5a5, gold:0xdcae46,
  stone:0x8e8674, stoneDk:0x6f6859, granite:0xa49c8a, brick:0x8f4b3c, brickDk:0x743a30,
  roof:0x48555e, roofDk:0x38434b, wood:0x8a6438, woodDk:0x5a4330, iron:0x373d43,
  grass:0x5f8b46, grassDk:0x4f7739, sand:0xd6c99a, dirt:0x77603f, cobble:0x8d8778,
  red:0xc2412f, white:0xece5d8, cream:0xe6d8b8, glass:0xffd27a, lamp:0xffc25e,
  leaf:0x4a7b3c, leafDk:0x3c6531, trunk:0x6a4d31, copper2:0xb8703a
};

/* ══════════════════════════════════════════════════════════
   1 · VOXEL BUILDER
   ══════════════════════════════════════════════════════════ */
class Vox{
  constructor(){ this.solid=new Map(); this.glow=new Map(); }
  add(x,y,z,c,glow=false){ if(glow) this.glow.set(x+','+y+','+z,c); else this.solid.set(x+','+y+','+z,c); return this; }
  has(x,y,z){ return this.solid.has(x+','+y+','+z)||this.glow.has(x+','+y+','+z); }
  box(x0,x1,y0,y1,z0,z1,c,j=0.05){
    for(let x=x0;x<=x1;x++)for(let y=y0;y<=y1;y++)for(let z=z0;z<=z1;z++) this.add(x,y,z,jc(c,j)); return this;
  }
  cyl(cx,cz,r,y0,y1,c,j=0.05){
    for(let x=Math.floor(cx-r);x<=Math.ceil(cx+r);x++)for(let z=Math.floor(cz-r);z<=Math.ceil(cz+r);z++){
      const dx=x-cx,dz=z-cz; if(dx*dx+dz*dz>r*r+0.35) continue;
      for(let y=y0;y<=y1;y++) this.add(x,y,z,jc(c,j));
    } return this;
  }
  line(x0,y0,z0,x1,y1,z1,c,j=0.04){
    const n=Math.max(1,Math.ceil(Math.max(Math.abs(x1-x0),Math.abs(y1-y0),Math.abs(z1-z0))));
    for(let i=0;i<=n;i++){ const t=i/n;
      this.add(Math.round(x0+(x1-x0)*t),Math.round(y0+(y1-y0)*t),Math.round(z0+(z1-z0)*t),jc(c,j)); }
    return this;
  }
  ball(cx,cy,cz,r,c,j=0.06){
    for(let x=-r;x<=r;x++)for(let y=-r;y<=r;y++)for(let z=-r;z<=r;z++)
      if(x*x+y*y+z*z<=r*r+0.6) this.add(cx+x,cy+y,cz+z,jc(c,j)); return this;
  }
}

/* geometry for a sparse voxel mesh (uses my own attribute name so
   nothing collides with three's internal instanceColor handling) */
function makeVoxMesh(b, mat, cast, receive, glowMat){
  const solids=[], glows=[];
  for(const [k,c] of b.solid){
    const p=k.split(','), x=+p[0], y=+p[1], z=+p[2];
    if(b.has(x+1,y,z)&&b.has(x-1,y,z)&&b.has(x,y+1,z)&&b.has(x,y-1,z)&&b.has(x,y,z+1)&&b.has(x,y,z-1)) continue;
    solids.push(x,y,z,c.r,c.g,c.b);
  }
  for(const [k,c] of b.glow){
    const p=k.split(','), x=+p[0], y=+p[1], z=+p[2];
    if(b.solid.has(x+1,y,z)&&b.solid.has(x-1,y,z)&&b.solid.has(x,y+1,z)&&b.solid.has(x,y-1,z)&&b.solid.has(x,y,z+1)&&b.solid.has(x,y,z-1)) continue;
    glows.push(x,y,z,c.r,c.g,c.b);
  }
  const out=[];
  if(solids.length) out.push(instanced(new THREE.BoxGeometry(1,1,1), solids, mat, cast, receive, 'color'));
  if(glows.length)  out.push(instanced(new THREE.BoxGeometry(1,1,1), glows, glowMat, false, false, 'aColor'));
  return {meshes:out, count:(solids.length+glows.length)/6};
}
function instanced(geo, data, mat, cast, receive, attr){
  const n=data.length/6;
  const pos=new Float32Array(n*3), col=new Float32Array(n*3);
  for(let i=0;i<n;i++){
    pos[i*3]=data[i*6]; pos[i*3+1]=data[i*6+1]; pos[i*3+2]=data[i*6+2];
    col[i*3]=data[i*6+3]; col[i*3+1]=data[i*6+4]; col[i*3+2]=data[i*6+5];
  }
  geo.setAttribute(attr, new THREE.InstancedBufferAttribute(col,3));
  const im=new THREE.InstancedMesh(geo, mat, n);
  const d=new THREE.Object3D();
  for(let i=0;i<n;i++){ d.position.set(pos[i*3],pos[i*3+1],pos[i*3+2]); d.updateMatrix(); im.setMatrixAt(i,d.matrix); }
  im.instanceMatrix.needsUpdate=true;
  im.castShadow=!!cast; im.receiveShadow=!!receive;
  im.frustumCulled=false;
  return im;
}

/* emissive material — unlit, globally scaled so lamps can swell at night */
const GLOW={i:{value:1}};
function glowMaterial(){
  return new THREE.ShaderMaterial({
    uniforms:{ uI:GLOW.i },
    vertexShader:`attribute vec3 aColor; varying vec3 vC;
      void main(){ vC=aColor; gl_Position=projectionMatrix*modelViewMatrix*instanceMatrix*vec4(position,1.0); }`,
    fragmentShader:`uniform float uI; varying vec3 vC;
      void main(){ gl_FragColor=vec4(vC*uI,1.0); }`,
    toneMapped:false, fog:false
  });
}

/* thin spar / rope used for rigging & beams */
const UNIT=new THREE.BoxGeometry(1,1,1);
function spar(parent, x0,y0,z0, x1,y1,z1, size, color, glow=false){
  const a=new THREE.Vector3(x0,y0,z0), b=new THREE.Vector3(x1,y1,z1);
  const dir=b.clone().sub(a); const len=dir.length();
  const m=new THREE.Mesh(UNIT, glow? glowMaterial() : new THREE.MeshLambertMaterial({color}));
  m.scale.set(size,size,len); m.position.copy(a.clone().add(b).multiplyScalar(0.5));
  m.quaternion.setFromUnitVectors(new THREE.Vector3(0,0,1), dir.normalize());
  m.castShadow=!glow; parent.add(m); return m;
}

/* ══════════════════════════════════════════════════════════
   2 · RENDERER · SCENE · SKY · LIGHTS
   ══════════════════════════════════════════════════════════ */
const scene=new THREE.Scene();
const camera=new THREE.PerspectiveCamera(46, innerWidth/innerHeight, 0.5, 1600);
camera.position.set(-58, 27, -44);

const renderer=new THREE.WebGLRenderer({antialias:true, powerPreference:'high-performance'});
renderer.setSize(innerWidth,innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.shadowMap.enabled=true;
renderer.shadowMap.type=THREE.PCFSoftShadowMap;
renderer.toneMapping=THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure=1.02;
renderer.outputColorSpace=THREE.SRGBColorSpace;
document.body.appendChild(renderer.domElement);

const controls=new OrbitControls(camera, renderer.domElement);
controls.target.set(2,11,-1);
controls.enableDamping=true; controls.dampingFactor=0.06;
controls.minDistance=14; controls.maxDistance=240;
controls.maxPolarAngle=1.40; controls.minPolarAngle=0.15;
controls.rotateSpeed=0.55; controls.zoomSpeed=0.9;

scene.fog=new THREE.FogExp2(0xd8b28c, 0.0026);

/* --- sky dome (posterised so the horizon steps like the voxels) --- */
const skyU={
  uTop:{value:new THREE.Color(0x1f4a66)}, uHor:{value:new THREE.Color(0xe9a35c)},
  uGlow:{value:new THREE.Color(0xffd9a0)}, uSunDir:{value:new THREE.Vector3(0.3,0.15,0.9)},
  uPow:{value:16}, uBands:{value:15}
};
const skyMat=new THREE.ShaderMaterial({
  uniforms:skyU, side:THREE.BackSide, depthWrite:false, fog:false,
  vertexShader:`varying vec3 vD; void main(){ vD=normalize(position); gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0); }`,
  fragmentShader:`
    uniform vec3 uTop,uHor,uGlow; uniform vec3 uSunDir; uniform float uPow,uBands;
    varying vec3 vD;
    void main(){
      float h=clamp(vD.y*1.25+0.06,0.0,1.0);
      vec3 c=mix(uHor,uTop,pow(h,0.62));
      float d=max(dot(vD,normalize(uSunDir)),0.0);
      c+=uGlow*pow(d,3.0)*0.55;
      c+=uGlow*pow(d,60.0)*0.9;
      c=floor(c*uBands+0.5)/uBands;
      gl_FragColor=vec4(c,1.0);
    }`
});
skyMat.fragmentShader+='\n#include <tonemapping_fragment>\n#include <colorspace_fragment>';
scene.add(new THREE.Mesh(new THREE.SphereGeometry(700,32,20), skyMat));

/* --- lights --- */
const hemi=new THREE.HemisphereLight(0x9fc2d0, 0x4d5740, 0.55); scene.add(hemi);
const amb=new THREE.AmbientLight(0xffffff,0.18); scene.add(amb);
const sun=new THREE.DirectionalLight(0xffb46b, 2.1);
const SUNDIR=new THREE.Vector3(0.30,0.155,0.94).normalize();
sun.position.copy(SUNDIR).multiplyScalar(240);
sun.castShadow=true;
sun.shadow.mapSize.set(2048,2048);
sun.shadow.camera.left=-95; sun.shadow.camera.right=95;
sun.shadow.camera.top=95;  sun.shadow.camera.bottom=-95;
sun.shadow.camera.near=40; sun.shadow.camera.far=520;
sun.shadow.bias=-0.0004; sun.shadow.normalBias=0.55;
scene.add(sun);

const lamps=[];
function lamp(x,y,z,color=0xffc25e,intensity=170,dist=46){
  const l=new THREE.PointLight(color,intensity,dist,2.1); l.position.set(x,y,z); scene.add(l); lamps.push(l); return l;
}

/* --- shared materials --- */
const solidMat=new THREE.MeshLambertMaterial({vertexColors:true, flatShading:true});
const glowMat=glowMaterial();
const solidOpts=[true,true];

/* ══════════════════════════════════════════════════════════
   3 · LAND, SEA BED, COAST
   ══════════════════════════════════════════════════════════ */
const SEAMIN=-64, SEAMAX=63;
const landTop=new Map();
const coastX=z=>33+7*Math.sin(z*0.14)+4*Math.sin(z*0.06+1.7);
function baseTop(x,z){
  let h=10+Math.round(2.0*Math.sin(x*0.11+z*0.045)+1.5*Math.sin(z*0.09-x*0.032)+1.1*Math.sin(x*0.04-z*0.07));
  const dx=x-52,dz=z+46; const r=Math.sqrt(dx*dx+dz*dz);
  if(r<18) h+=Math.round(7*Math.max(0,1-r/18));          // south-west headland
  const ix=x+44, iz=z+46; const ir=Math.sqrt(ix*ix+iz*iz);
  if(ir<11) h+=Math.round(5*Math.max(0,1-ir/11));        // little islet
  return clamp(h,8,24);
}
function topAt(x,z){
  if(x>=35&&x<=52&&z>=-32&&z<=22) return 11;             // town plateau
  return baseTop(x,z);
}
function groundAt(x,z){ return landTop.get(x+','+z) ?? (inQuay(x,z)?8:11); }

const land=new Vox();
{
  for(let z=SEAMIN;z<=SEAMAX;z++){
    const c0=Math.ceil(coastX(z));
    for(let x=c0;x<=SEAMAX;x++){
      const top=topAt(x,z); landTop.set(x+','+z,top);
      const d=x-c0;
      for(let y=Math.min(5,top-3);y<=top;y++){
        let c;
        if(y===top){
          if(d<2) c=P.sand;
          else if(d<5) c= rnd()<0.25?P.dirt:P.sand;
          else if(x>=35&&x<=52&&z>=-32&&z<=22) c= rnd()<0.14?P.dirt:P.grass;
          else c= top>15?P.grassDk:(rnd()<0.12?P.dirt:P.grass);
        } else if(y>=top-2) c= d<5?P.sand:P.dirt;
        else c= x<38?P.stoneDk:P.dirt;
        land.add(x,y,z,jc(c,0.07));
      }
      /* town plateau retaining wall on the seaward lip */
      if(x===35) for(let y=8;y<=11;y++) land.add(x,y,z,jc(P.granite,0.06));
    }
  }
  /* distant town silhouette on the far shore */
  let z=-50;
  while(z<40){
    const w=ri(4,8), h=ri(5,14);
    const x=ri(56,60);
    for(let zz=z;zz<z+w&&zz<=SEAMAX;zz++) for(let xx=x;xx<x+5&&xx<=SEAMAX;xx++)
      for(let y=12;y<=12+h;y++) land.add(xx,y,zz,jc(y===12+h?P.roofDk:P.brickDk,0.03));
    z+=w+ri(1,4);
  }
}

/* ══════════════════════════════════════════════════════════
   4 · QUAY (the built dock)
   ══════════════════════════════════════════════════════════ */
const QX0=8, QX1=32, QZ0=-28, QZ1=20, QY=8;
function inQuay(x,z){
  if(x<QX0||x>QX1||z<QZ0||z>QZ1) return false;
  if(Math.abs(x-18)<4&&Math.abs(z-16)<3) return false;   // boat-landing notch
  return true;
}
const quay=new Vox();
{
  for(let z=QZ0;z<=QZ1;z++)for(let x=QX0;x<=QX1;x++){
    for(let y=4;y<QY;y++) quay.add(x,y,z,jc(P.stone+(y%2?0x050505:0),0.07));
    let c=P.wood;
    if(x<=QX0+1||z<=QZ0+1||z>=QZ1-1) c=P.granite;
    else if(x>=27) c=P.cobble;
    quay.add(x,QY,z,jc(c,0.06));
  }
  /* kerb + fenders */
  for(let z=QZ0;z<=QZ1;z++) if((z+QZ0)%2===0&&inQuay(QX0,z)) quay.add(QX0,QY+1,z,jc(P.granite,0.05));
  for(let z=QZ0+2;z<QZ1-1;z+=3){ for(let y=QY-1;y>=0;y-=2) quay.box(QX0-1,QX0-1,y,y,z,z,P.woodDk,0.05); }
  /* wall face down to the water + rings + ladders */
  for(let z=QZ0;z<=QZ1;z++)for(let y=-2;y<4;y++) if(inQuay(QX0,z)) quay.add(QX0,y,z,jc(y<-1?P.stoneDk:P.granite,0.08));
  for(let z of [-20,-2,12]) for(let y=4;y<QY;y+=3) quay.add(QX0-1,y,z,jc(P.iron,0.02));
  [-14,6].forEach(z=>{ for(let y=-1;y<QY;y+=1) quay.add(QX0-1,y,z+2,y===0?P.iron:P.woodDk,0.04); });
  /* steps into the sea at the notch */
  [ [10,9],[9,7],[8,5],[7,3],[6,1],[5,-1] ].forEach(([x,y])=>quay.box(x,x,y,y,14,18,P.granite,0.06));
  /* pilings */
  for(let x=QX0+1;x<QX1;x+=6)for(let z=QZ0+2;z<QZ1-1;z+=6){
    if(!inQuay(x,z)) continue;
    quay.cyl(x,z,1,-4,QY-1,P.woodDk,0.06);
  }
  /* bollards */
  for(let z=QZ0+3;z<QZ1-2;z+=6){ if(!inQuay(QX0,z))continue;
    quay.box(QX0+1,QX0+1,QY+1,QY+2,z,P.iron,0.04); quay.add(QX0+1,QY+3,z,jc(P.granite,0.03)); }
  /* cobble road along the quay */
  quay.box(27,QX1,QY,QY,QZ0,QZ1,P.cobble,0.08);
}

/* ══════════════════════════════════════════════════════════
   5 · TOWN · WAREHOUSE · LIGHTHOUSE
   ══════════════════════════════════════════════════════════ */
const town=new Vox();
function gable(b,x0,x1,z0,z1,yb,rise,c1,c2,alongX){
  const L=alongX?(x1-x0):(z1-z0);
  for(let i=-1;i<=L+1;i++){
    const t=clamp(Math.min(i,L-i)/L,0,1);
    const y=yb+Math.round(2*rise*t);
    if(alongX){ b.box(x0+i,x0+i,y,y,z0-1,z1+1, t>0.02?c1:c2, 0.05); }
    else { b.box(x0-1,x1+1,y,y,z0+i,z0+i, t>0.02?c1:c2, 0.05); }
  }
  /* gable ends */
  for(let z=z0;z<=z1;z++){
    const t=clamp(Math.min(z-z0,z1-z)/L,0,1);
    const y=yb+Math.round(2*rise*t);
    b.box(x0,x0,yb+1,y,z,jc(c2,0.04)); b.box(x1,x1,yb+1,y,z,jc(c2,0.04));
  }
}
/* warehouse */
{
  const yb=11;
  town.box(38,48,yb+1,19,-22,-9,P.brick,0.07);
  town.box(38,48,yb,yb,-22,-9,P.granite,0.04);
  gable(town,37,49,-23,-8,19,5,P.roof,P.roofDk,false);
  town.box(38,38,11,14,-17,-14,P.woodDk,0.05);          // big door
  town.box(39,40,14,15,-17,-14,P.wood,0.05);
  for(let x=40;x<=47;x+=3)for(let z=-20;z<=-11;z+=3){
    if(x===38&&z>-18&&z<-13) continue;
    town.add(x,16,z,jc(Math.random()<0.4?P.lamp:P.iron,0.02), Math.random()<0.4);
  }
  town.box(46,47,20,30,-12,-11,P.brickDk,0.05);         // chimney
  town.box(45,48,20,20,-13,-10,P.stoneDk,0.04);
  /* lean-to + stacked crates */
  town.box(49,52,12,16,-22,-14,P.wood,0.06);
  gable(town,48,53,-23,-13,16,3,P.roofDk,P.roof,false);
}
/* tavern with sign post */
{
  const yb=11;
  town.box(38,44,yb+1,15,-2,8,P.brickDk,0.06);
  gable(town,37,45,-3,9,15,4,P.roofDk,P.roof,false);
  town.box(38,38,11,13,2,3,P.woodDk,0.04);
  for(let z=-1;z<=7;z+=3){ town.add(38,14,z,jc(P.lamp,0.02),true); }
  town.add(44,14,4,jc(P.lamp,0.02),true);
  town.box(45,46,16,25,-1,0,P.stoneDk,0.05);
}
/* cottages + chapel */
function cottage(x0,z0,w,d,c){
  const yb=11;
  town.box(x0,x0+w-1,yb+1,yb+5,z0,z0+d-1,jc(c,0.06),0.04);
  gable(town,x0-1,x0+w,yb+5,z0-1,z0+d,5,3,P.roof,P.roofDk,false);
  town.box(x0,x0,yb+1,yb+3,z0+Math.floor(d/2),jc(P.woodDk,0.03));
  town.add(x0+w-1,yb+3,z0+1,jc(P.lamp,0.02),true);
  town.add(x0,yb+4,z0+d-1,jc(P.lamp,0.02),rnd()<0.6);
  town.box(x0+w-2,x0+w-1,yb+6,yb+11,z0+1,jc(P.brickDk,0.05));
}
cottage(46,14,6,6,P.cream); cottage(53,17,5,5,P.white);
cottage(36,-31,6,5,P.cream);
/* chapel with bell tower */
{
  const yb=11;
  town.box(45,51,yb+1,17,15,22,P.stone,0.06);
  gable(town,44,52,14,23,17,4,P.roofDk,P.roof,false);
  town.box(47,50,yb+1,24,18,19,P.stone,0.05);
  town.box(46,51,24,24,17,20,P.granite,0.04);
  town.box(46,51,23,23,17,20,P.iron,0.02);
  town.add(48,23,18,jc(0xf0e0a0,0.02),true);
  gable(town,46,51,17,20,24,3,P.roofDk,P.roof,true);
  town.add(47,26,18,jc(P.gold,0.02),true);
}
/* well, walls, gate, flagpole */
town.cyl(50,7,2.5,12,13,P.granite,0.05); town.box(48,52,14,14,5,P.wood,0.05);
town.box(44,44,12,13,10,13,P.stone,0.05); town.box(43,44,14,14,10,13,P.granite,0.04);
town.box(53,53,12,13,-30,14,P.stone,0.05);
/* flagpole on the green */
town.box(49,49,12,26,4,jc(P.white,0.01));
town.box(48,50,26,26,3,5,jc(P.red,0.03)); town.box(48,50,25,25,3,5,jc(P.white,0.03));

/* ══════════════════════════════════════════════════════════
   6 · BREAKWATER + LIGHTHOUSE
   ══════════════════════════════════════════════════════════ */
const phare=new Vox();
{
  const path=[[24,20],[20,23],[16,26],[12,29],[9,32],[8,34]];
  for(let i=0;i<path.length-1;i++){
    const [ax,az]=path[i],[bx,bz]=path[i+1];
    const n=Math.max(2,Math.ceil(Math.max(Math.abs(bx-ax),Math.abs(bz-az))));
    for(let k=0;k<=n;k++){
      const x=Math.round(ax+(bx-ax)*k/n), z=Math.round(az+(bz-az)*k/n);
      for(let y=2;y<=11;y++){
        if(Math.abs(y-11)<1&&rnd()<0.35) continue;
        phare.add(x,y,z,jc(y>=10?P.granite:(rnd()<0.2?P.stoneDk:P.stone),0.09));
      }
      if(rnd()<0.55) phare.add(x+ri(-1,1),12,z+ri(-1,1),jc(P.stoneDk,0.1));
    }
  }
  const LX=8, LZ=34;
  phare.cyl(LX,LZ,4,12,14,P.granite,0.05);
  phare.cyl(LX,LZ,3,15,29,P.white,0.02);
  for(let y=16;y<29;y+=4) phare.cyl(LX,LZ,3,y,y+1,P.red,0.03);
  for(let x=LX-4;x<=LX+4;x++)for(let z=LZ-4;z<=LZ+4;z++)
    if((x-LX)*(x-LX)+(z-LZ)*(z-LZ)<=16.5) phare.add(x,30,z,jc(P.iron,0.04));
  phare.cyl(LX,LZ,2.5,31,34,P.glass,0.02);
  for(let x=LX-3;x<=LX+3;x++)for(let z=LZ-3;z<=LZ+3;z++){
    if((x-LX)*(x-LX)+(z-LZ)*(z-LZ)>9.4) continue;
    if(Math.abs(x-LX)===3||Math.abs(z-LZ)===3) phare.add(x,32,z,jc(P.iron,0.02));
  }
  for(let r=3;r>=0;r--) phare.cyl(LX,LZ,r,35,35+(3-r),P.iron,0.04);
  /* keeper's cottage */
  const yb=11;
  phare.box(15,20,yb+1,15,36,41,P.cream,0.05);
  gable(phare,14,21,35,42,15,3,P.roofDk,P.roof,false);
  phare.add(15,13,38,jc(P.lamp,0.02),true);
  phare.box(19,20,16,21,37,P.brickDk,0.05);
}

/* ══════════════════════════════════════════════════════════
   7 · DOCK PROPS · SLIPWAY · FISH FARM · FLORA
   ══════════════════════════════════════════════════════════ */
const props=new Vox();
function crate(x,y,z,s=3){ props.box(x,x+s-1,y,y+s-1,z,z+s-1,jc(P.wood,0.07));
  for(let i=0;i<s;i++){ props.add(x+i,y,z,jc(P.woodDk,0.04)); props.add(x+i,y+s-1,z+s-1,jc(P.woodDk,0.04)); } }
function barrel(x,y,z){ props.cyl(x,z,1,y,y+2,jc(P.woodDk,0.06)); props.cyl(x,z,1.1,y+1,y+1,jc(P.copper2,0.05)); }
{
  const spots=[[14,-24],[17,-20],[13,-14],[21,-17],[24,4],[19,10],[26,-4],[15,-8]];
  spots.forEach(([x,z])=>{ const s=ri(2,3); crate(x,9,z,s); if(rnd()<0.45) crate(x+1,9+s,z,s-1); });
  for(let i=0;i<10;i++) barrel(ri(12,29),9,ri(QZ0+2,QZ1-2));
  /* coils of rope + sacks */
  for(let i=0;i<5;i++){ const x=ri(11,28),z=ri(QZ0+2,QZ1-2);
    props.box(x,x,9,9,z,jc(P.rope,0.05)); props.box(x,x,9,9,z+1,jc(P.rope,0.05));
    props.box(x+1,x+1,9,9,z,jc(P.rope,0.05)); }
  for(let i=0;i<6;i++) props.box(ri(12,26),9,ri(QZ0+2,QZ1-2),ri(12,26),10,ri(QZ0+2,QZ1-2),jc(P.cream,0.05));
  /* fish stall + market awning */
  props.box(19,25,9,11,-8,-4,P.woodDk,0.05);
  for(let x=19;x<=25;x++) for(let z=-8;z<=-4;z+=2) props.add(x,12,z,jc(P.wood,0.04));
  for(let x=18;x<=26;x++) for(let z=-9;z<=-3;z++){
    const y=13+Math.round((z+9)*0.35);
    props.add(x,y,z,jc(((x+z)%2)?P.red:P.cream,0.03)); }
  for(let x=20;x<=24;x++) for(let z=-7;z<=-5;z++) if(rnd()<0.6) props.add(x,12,z,jc(pick([0xc2412f,0xe0b03a,0x7a3b5c]),0.05));
  /* drying nets between poles */
  [28].forEach(()=>{});
  props.box(26,26,9,15,-26,jc(P.woodDk,0.04)); props.box(31,31,9,15,-26,jc(P.woodDk,0.04));
  for(let x=27;x<=30;x++)for(let y=11;y<=14;y++) if((x+y)%2===0) props.add(x,y,-26,jc(P.rope,0.05));
  props.box(26,26,9,15,-24,jc(P.woodDk,0.04)); props.box(31,31,9,15,-24,jc(P.woodDk,0.04));
  for(let x=27;x<=30;x++)for(let y=11;y<=14;y++) if((x+y)%2===1) props.add(x,y,-24,jc(P.rope,0.05));
  /* lamp posts on the quay */
  [-16,-2,12].forEach(z=>{
    props.box(11,11,9,12,z,jc(P.iron,0.04));
    props.box(10,12,13,13,z,jc(P.iron,0.03));
    props.add(11,13,z,jc(P.lamp,0.02),true);
    props.box(10,12,14,14,z,jc(P.iron,0.03));
  });
  /* slipway ramp + half-built hull */
  for(let i=0;i<9;i++) props.box(24+i,24+i,1+i,1+i,15,18,jc(P.wood,0.05));
  props.box(24,32,17,17,16,jc(P.woodDk,0.04));
  props.box(26,30,18,20,16,jc(P.wood,0.06)); props.box(27,29,21,21,16,jc(P.woodDk,0.04));
  /* fish farm cages */
  for(let i=0;i<3;i++){ const z=25+i*9;
    for(let a=0;a<Math.PI*2;a+=0.55){ const x=5+Math.round(Math.cos(a)*3.5), zz=z+Math.round(Math.sin(a)*3.5);
      props.add(x,8,zz,jc(P.wood,0.05)); props.add(x,9,zz,jc(P.net,0.05)); } }
  /* trees, rocks, haystacks */
  const pine=(x,z)=>{const g=groundAt(x,z); props.box(x,x,g+1,g+5,z,jc(P.trunk,0.05));
    for(let i=0;i<4;i++){ const r=3-i; props.cyl(x,z,r,g+6+i*2,g+7+i*2,jc(i%2?P.leafDk:P.leaf,0.08)); }};
  const oak=(x,z)=>{const g=groundAt(x,z); props.box(x,x,g+1,g+4,z,jc(P.trunk,0.05));
    props.ball(x,g+6,z,3,jc(P.leaf,0.1)); props.ball(x+1,g+5,z-1,2,jc(P.leafDk,0.1));};
  [[55,-24],[57,-14],[56,-4],[58,6],[55,26],[53,28],[47,-30],[44,-32],[57,40],[59,32]].forEach(([x,z])=>pine(x,z));
  [[43,24],[52,-24],[46,6]].forEach(([x,z])=>oak(x,z));
  [[38,20],[52,22],[44,10]].forEach(([x,z])=>props.box(x,x+1,groundAt(x,z)+1,groundAt(x,z)+3,z,z+1,jc(0xc9a94e,0.08)));
  const rock=(x,z,r)=>{const g=groundAt(x,z); props.ball(x,g+Math.round(r/2),z,r,jc(P.stoneDk,0.09));};
  [[-30,-52,4],[-24,-58,3],[48,-38,5],[42,-42,3],[60,-2,4],[62,-10,3]].forEach(([x,z,r])=>rock(x,z,r));
  /* headland signal flag */
  props.box(52,52,baseTop(52,-46),baseTop(52,-46)+11,-46,jc(P.white,0.02));
  props.box(53,56,baseTop(52,-46)+9,baseTop(52,-46)+11,-46,jc(P.red,0.04));
}
/* breakwater rocks near the harbour mouth */
props.ball(-11,-44,3,jc(P.stoneDk,0.09)); props.ball(-13,42,3,jc(P.stoneDk,0.09));

/* ══════════════════════════════════════════════════════════
   8 · THE BARQUE
   ══════════════════════════════════════════════════════════ */
const shipV=new Vox();
{
  const L0=-23, L1=22;
  const hb=z=>{
    if(z>=23) return 0;
    const t=(z-L0)/(L1-L0);
    let v=7*Math.pow(Math.max(0,Math.sin(Math.PI*(t*0.79+0.20))),0.42);
    if(z<=-21) v-=1;
    return Math.max(0,Math.round(v));
  };
  const deckY=z=>7+(z>0?Math.min(3,Math.round(z*0.22)):Math.min(3,Math.round(-z*0.15)));

  for(let z=L0;z<=L1;z++){
    const w=hb(z); if(!w) continue;
    const dy=deckY(z);
    for(let y=-6;y<=dy;y++){
      let lw=w;
      if(y<=-4) lw=Math.max(0,w-3);
      else if(y<=-2) lw=Math.max(1,w-1);
      else if(y>=4) lw=Math.max(1,w-1);
      for(let x=-lw;x<=lw;x++){
        if(y>=2&&Math.abs(x)<lw) continue;                 // hollow topsides
        let c;
        if(y<=-5) c=P.bottom;
        else if(y<=-2) c=P.copper;
        else if(y===2) c=P.stripe;
        else if(y===dy) c=(Math.abs(x)===lw)?P.deckDk:P.deck;
        else c=(Math.abs(x)===lw&&y>=3)?P.hullHi:P.hull;
        /* gun ports */
        if(Math.abs(x)===lw&&y===2&&(z+16)%4===0&&z>=-16&&z<=12) c=0x0b1116;
        shipV.add(x,y,z,jc(c,0.045));
      }
    }
    /* transom + stern windows */
    if(z===L0){
      for(let x=-w;x<=w;x++)for(let y=-6;y<=dy;y++){
        if(y>=dy-2&&Math.abs(x)<=3&&Math.abs(x)%2===1) shipV.add(x,y,L0,jc(P.lamp,0.02),true);
        else if(y>=2) shipV.add(x,y,L0,jc(y===dy?P.deckDk:P.hullHi,0.04));
        else shipV.add(x,y,L0,jc(y<=-2?P.copper:P.hull,0.04));
      }
    }
    /* bulwark rail with gaps */
    if((z+23)%2===0){
      for(const s of [-1,1]) shipV.add(s*w,dy+1,z,jc(P.deckDk,0.05));
    }
  }
  /* figurehead + trailboard */
  shipV.line(0,8,22, 0,11,27, P.gold,0.03);
  shipV.line(1,9,23, 1,10,25, P.gold,0.03);
  shipV.line(-1,9,23,-1,10,25, P.gold,0.03);
  shipV.box(-2,2,10,10,24,jc(P.gold,0.03));
  shipV.box(-1,1,12,12,26,jc(P.white,0.03));
  /* quarterdeck house */
  shipV.box(-3,3,9,12,-16,-11,jc(P.hullHi,0.05));
  gable(shipV,-4,4,-17,-10,12,2,P.deckDk,P.deck, true);
  for(let x=-2;x<=2;x+=2) shipV.add(x,11,-16,jc(P.lamp,0.02),true);
  /* deck furniture */
  shipV.box(-2,2,8,8,2,jc(P.deckDk,0.04));               // hatch
  shipV.cyl(0,0,-4,1,0,-3,8,P.deckDk,0.05);              // capstan (small)
  for(const [x,z] of [[-4,-6],[4,-5],[-4,4],[3,7],[0,-19]]) shipV.cyl(x,z,1,deckY(z)+1,deckY(z)+3,P.woodDk,0.06);
  for(const s of [-1,1]) for(let z=-14;z<=10;z+=6){
    shipV.box(s*4,s*4,deckY(z)+1,deckY(z)+2,z,jc(P.iron,0.04));
    shipV.box(s*3,s*3,deckY(z)+1,deckY(z)+2,z,jc(P.copper2,0.04));
  }
  /* crew on deck */
  const crew=(x,z,col,coat)=>{ const dy=deckY(z)+1;
    shipV.box(x,x,dy,dy+1,z,col); shipV.box(x,x,dy+2,dy+2,z,0xd9a178);
    if(coat) shipV.box(x,x,dy+1,dy+1,z+1,coat); };
  crew(0,18,P.navy||0x2b3f55,P.white); crew(-3,10,0x7a3b2c,P.cream); crew(3,-8,0x3b4a3a,P.cream);
  /* ship's boat on davits */
  shipV.box(-3,3,14,14,-23,P.wood,0.05);
  shipV.box(-2,2,13,13,-23,jc(P.cream,0.05));

  /* masts, yards, sails */
  const mast=(cz,top)=>{ const dy=deckY(cz); for(let y=dy;y<=top;y++) shipV.add(0,y,cz,jc(y>top-2?P.sparDk:P.spar,0.03)); };
  const yard=(cz,y,len)=>{ shipV.box(-Math.round(len),Math.round(len),y,y,cz,jc(P.sparDk,0.03));
    shipV.add(0,y+1,cz,jc(P.spar,0.03)); };
  const furl=(cz,y,len)=>{ for(let x=-Math.round(len);x<=Math.round(len);x++){
    const b=Math.round(Math.cos((x/len)*1.35)*0.9);
    shipV.add(x,y,b===1?cz:cz+1,jc(P.sail,0.03));
    if(b===1) shipV.add(x,y,cz-1,jc(P.sailDk,0.03)); } };
  function sail(cz,len,y0,y1,bulge){
    for(let y=y0;y<=y1;y++){
      const vy=1-Math.pow((y-(y0+y1)/2)/((y1-y0)/2+0.001),2);
      const c=(y%3===0)?P.sailDk:P.sail;
      for(let x=-len;x<=len;x++){
        const vx=1-Math.pow(x/len,2);
        const o=Math.round(bulge*vx*Math.max(0.25,vy));
        shipV.add(x,y,cz+o,jc(c,0.02));
        if(o>=2) shipV.add(x,y,cz+o-1,jc(P.sailDk,0.02));
      }
    }
  }
  function tri(ax,ay,az,bx,by,bz,cx,cy,cz,c){
    const n=Math.max(Math.abs(by-cy),1)*3;
    for(let i=0;i<=n;i++){ const t=i/n;
      shipV.line(ax,ay,az, bx+(cx-bx)*t, by+(cy-by)*t, bz+(cz-bz)*t, c,0.02); }
  }
  /* fore */
  mast(14,30); yard(14,15,8); furl(14,16,8);
  yard(14,21,7); sail(14,7,22,27,3); yard(14,26,5); furl(14,27,5);
  /* main */
  mast(-1,37); yard(-1,14,9); furl(-1,15,9);
  yard(-1,22,8); sail(-1,8,23,29,4); yard(-1,28,6); furl(-1,29,6);
  /* mizzen */
  mast(-15,28); yard(-15,14,6); sail(-15,6,15,19,3); yard(-15,20,4); furl(-15,21,4);
  /* spanker + jibs */
  tri(0,10,-16, 0,20,-19, 0,10,-25, P.sail);
  tri(0,13,33, 0,29,14, 0,18,22, P.sail);
  tri(0,11,28, 0,24,15, 0,15,21, P.sailDk);
}

/* --- ship assembly --- */
const ship=new THREE.Group();
{
  const built=makeVoxMesh(shipV, solidMat, true, true, glowMaterial());
  built.meshes.forEach(m=>{ m.castShadow=true; m.userData.ship=true; ship.add(m); });
  /* standing rigging */
  const rig=(x0,y0,z0,x1,y1,z1)=>spar(ship,x0,y0,z0,x1,y1,z1,0.28,P.rig);
  const masts=[[14,30,9],[ -1,37,7],[-15,28,8]];
  masts.forEach(([cz,top,dy])=>{
    for(const s of [-1,1]) for(const dz of [-3,0,3]){
      rig(s*6, dy+1, cz+dz, 0, top-1, cz);
    }
    rig(0,top-1,cz, 0, 13, cz+16);
    rig(0,top-1,cz, 0, 10, cz-14);
  });
  rig(0,15,33, 0,29,14, 0.3, P.rig);                     // jib stays
  /* bowsprit */
  spar(ship,0,8,18, 0,15,33, 1.1, P.spar);
  spar(ship,0,13,30, 0,13,33, 0.7, P.sparDk);
  /* ensign staff */
  spar(ship,0,13,-24, -1,20,-29, 0.55, P.sparDk);
}
ship.position.set(-19,0,-2);
ship.rotation.y=-Math.PI/2+0.22;
scene.add(ship);

/* --- waving flags --- */
function makeFlag(cols,rows,colorFn,anchor,amp){
  const n=cols*rows;
  const geo=new THREE.BoxGeometry(1.15,1.15,0.35);
  const mat=new THREE.MeshLambertMaterial({side:THREE.DoubleSide});
  const im=new THREE.InstancedMesh(geo,mat,n);
  const d=new THREE.Object3D(), base=[];
  for(let i=0;i<cols;i++)for(let j=0;j<rows;j++){
    const k=i*rows+j, x=-(i+0.5)*1.15, y=-(j+0.5)*1.15;
    base.push([x,y]); d.position.set(x,y,0); d.updateMatrix(); im.setMatrixAt(k,d.matrix);
    im.setColorAt(k,colorFn(i,j));
  }
  im.instanceMatrix.needsUpdate=true; im.castShadow=false;
  im.position.copy(anchor); ship.add(im);
  return {im, base, amp, n, cols};
}
const ensign=makeFlag(11,6,(i,j)=> (i<4&&j<3)? ((i+j)%2? 0xf2f0ea : 0x1f3f7a) : 0xc2331f,
  new THREE.Vector3(-1,19.4,-29), 0.55);
const pennant=makeFlag(14,3,(i,j)=> i%4<2? 0xe8dec4 : 0x2e4a6b,
  new THREE.Vector3(0,36.4,-1), 0.75);
function animateFlag(f,t){
  const d=new THREE.Object3D();
  for(let k=0;k<f.n;k++){
    const u=f.base[k][0];
    d.position.set(f.base[k][0], f.base[k][1]+Math.sin(t*4+u*0.55)*f.amp*(-u/12), Math.sin(t*5.5+u*0.8)*0.35);
    d.rotation.z=Math.sin(t*4+u*0.55)*0.18*f.amp;
    d.updateMatrix(); f.im.setMatrixAt(k,d.matrix);
  }
  f.im.instanceMatrix.needsUpdate=true;
}

/* ══════════════════════════════════════════════════════════
   9 · WATER
   ══════════════════════════════════════════════════════════ */
const surfDefs=[
  [15,24,16],[-3,-28,12],[47,15,22],[10,36,14],[-22,-2,11],[-40,-19,3.2],[18,-13,10],
  [-5,18,8],[5,28,7],[-11,-44,4],[-13,42,4],[43,-34,3],[6,6,9],[34,12,8]
];
const surfVecs=surfDefs.map(([x,z,r])=>new THREE.Vector3(x,z,r));
const waterMat=new THREE.MeshLambertMaterial({vertexColors:true, flatShading:true});
waterMat.onBeforeCompile=s=>{
  s.uniforms.uTime=U.time; s.uniforms.uSurf={value:surfVecs};
  s.vertexShader='varying vec3 vWPos;\n'+s.vertexShader.replace('#include <project_vertex>',
    '#include <project_vertex>\n vWPos=(modelMatrix*instanceMatrix*vec4(transformed,1.0)).xyz;');
  s.fragmentShader=[
    'uniform float uTime; uniform vec3 uSurf[14]; varying vec3 vWPos;',
    'float srect(float p,float lo,float hi,float e){return smoothstep(lo-e,lo+e,p)*(1.0-smoothstep(hi-e,hi+e,p));}'
  ].join('\n')+'\n'+s.fragmentShader.replace('#include <dithering_fragment>',`
    #include <dithering_fragment>
    vec3 wp=vWPos; float surf=0.0;
    for(int i=0;i<14;i++){ float d=length(wp.xz-uSurf[i].xy); surf+=smoothstep(uSurf[i].z+3.5,0.0,d); }
    surf=clamp(surf,0.0,1.6)*(0.62+0.38*sin(wp.x*1.9+wp.z*1.1+uTime*3.2));
    float crest=smoothstep(0.10,0.85,wp.y);
    float wake=srect(wp.x,-32.0,-6.0,6.0)*srect(wp.z,-8.0,4.0,5.0);
    surf+=wake*0.55*(0.5+0.5*sin(wp.x*2.3+uTime*2.4));
    gl_FragColor.rgb=mix(gl_FragColor.rgb*(0.82+0.14*crest), vec3(0.93,0.97,0.98), clamp(surf,0.0,1.0));
    float g=pow(max(0.0,sin(wp.x*2.7+wp.z*1.7+uTime*4.0)*sin(wp.z*3.1-uTime*2.2)),18.0)*0.55;
    gl_FragColor.rgb+=vec3(1.0,0.88,0.7)*g*step(0.15,wp.y);
  `);
};
const U={time:{value:0}};
const geoW=new THREE.BoxGeometry(1,3,1); geoW.translate(0,-1.5,0);
const wx=[],wz=[],wc=[];
for(let z=SEAMIN;z<=SEAMAX;z++)for(let x=SEAMIN;x<=SEAMAX;x++){
  if(landTop.has(x+','+z)) continue;
  wx.push(x); wz.push(z);
  const shore=clamp((coastX(z)-x)/9,0,1);
  const shelter=clamp(srect(x,QX0-2,QX1+2,4)*srect(z,QZ0-3,QZ1+3,4),0,1);
  const c=new THREE.Color(0x0f3143).lerp(new THREE.Color(0x2e7488), shore*0.95+shelter*0.06);
  c.multiplyScalar(1+(rnd()*2-1)*0.05);
  wc.push(c);
}
const water=new THREE.InstancedMesh(geoW, waterMat, wx.length);
water.receiveShadow=true; water.frustumCulled=false;
{ const d=new THREE.Object3D();
  for(let i=0;i<wx.length;i++){ d.position.set(wx[i],0,wz[i]); d.updateMatrix(); water.setMatrixAt(i,d.matrix); water.setColorAt(i,wc[i]); }
  water.instanceMatrix.needsUpdate=true; }
scene.add(water);
function srect(p,lo,hi,e){ return clamp(1-Math.max(0,(lo-p)/e, (p-hi)/e),0,1); }

const wArr=water.instanceMatrix.array;
function wave(x,z,t){
  let e = 0.55*Math.sin(x*0.19+t*1.10)
        + 0.40*Math.sin(x*0.070-z*0.150+t*0.70)
        + 0.35*Math.sin(z*0.210+x*0.050+t*1.35)
        + 0.28*Math.sin((x+z)*0.090-t*0.55);
  const calm=clamp(srect(x,QX0-4,QX1+4,6)*srect(z,QZ0-5,QZ1+5,6),0,1);
  e*= 0.32+0.68*(1-calm);
  return Math.round(e*2)/2;
}
function updateWater(t){
  for(let i=0, k=0; k<wx.length; k++, i+=16){
    wArr[i+12]=wx[k]; wArr[i+13]=wave(wx[k],wz[k],t); wArr[i+14]=wz[k];
  }
  water.instanceMatrix.needsUpdate=true;
}

/* ══════════════════════════════════════════════════════════
   10 · SKY FURNITURE · ANIMATED BITS
   ══════════════════════════════════════════════════════════ */
/* sun / moon */
const sunMesh=new THREE.Group();
const sunCoreMat=glowMaterial(); sunCoreMat.uniforms=THREE.UniformsUtils.clone({uI:{value:1}});
const sunHaloMat=glowMaterial(); sunHaloMat.uniforms=THREE.UniformsUtils.clone({uI:{value:0.32}});
sunHaloMat.blending=THREE.AdditiveBlending; sunHaloMat.transparent=true; sunHaloMat.depthWrite=false;
{
  const b=new Vox(); b.ball(0,0,0,7,0xfff3d2,0);
  const m=makeVoxMesh(b, sunCoreMat,false,false,sunCoreMat).meshes[0]; sunMesh.add(m);
  const b2=new Vox(); b2.ball(0,0,0,11,0xffd9a0,0);
  const m2=makeVoxMesh(b2, sunHaloMat,false,false,sunHaloMat).meshes[0]; sunMesh.add(m2);
}
scene.add(sunMesh);

/* stars */
const starMesh=(()=>{
  const n=420, geo=new THREE.BoxGeometry(1.6,1.6,1.6);
  const mat=new THREE.ShaderMaterial({
    uniforms:{uO:{value:0}},
    vertexShader:`attribute vec3 aColor; varying vec3 vC;
      void main(){vC=aColor; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}`,
    fragmentShader:`uniform float uO; varying vec3 vC; void main(){gl_FragColor=vec4(vC*uO,uO);}`,
    transparent:true, depthWrite:false, blending:THREE.AdditiveBlending, fog:false
  });
  const im=new THREE.InstancedMesh(geo,mat,n);
  const d=new THREE.Object3D(), col=new Float32Array(n*3);
  for(let i=0;i<n;i++){
    const v=new THREE.Vector3().randomDirection().multiplyScalar(560); v.y=Math.abs(v.y)*0.95+30;
    d.position.copy(v); d.scale.setScalar(0.6+rnd()*1.4); d.updateMatrix(); im.setMatrixAt(i,d.matrix);
    const c=new THREE.Color().setHSL(0.12+rnd()*0.1,0.25,0.85).multiplyScalar(0.5+rnd()*0.7);
    col[i*3]=c.r; col[i*3+1]=c.g; col[i*3+2]=c.b;
  }
  geo.setAttribute('aColor',new THREE.InstancedBufferAttribute(col,3));
  scene.add(im); return im;
})();

/* clouds (two drifting decks) */
const clouds=[];
function cloudDeck(count, y, spread, scale){
  const b=new Vox(); const items=[];
  for(let c=0;c<count;c++){
    const cx=ri(-spread,spread), cz=ri(-spread,spread);
    items.push({cx,cz});
    const r=ri(4,7);
    for(let i=0;i<r*6;i++){
      const a=rnd()*Math.PI*2, rad=r*Math.sqrt(rnd());
      const x=Math.round(cx+Math.cos(a)*rad), z=Math.round(cz+Math.sin(a)*rad);
      const h=Math.round((1-rad/r)*(2+rnd()*3));
      for(let yy=0;yy<=h;yy++) b.add(x,y+yy,z,jc(0xf6f2ea,0.03));
    }
  }
  const mesh=makeVoxMesh(b, new THREE.MeshLambertMaterial({vertexColors:true}), false,false,glowMaterial()).meshes[0];
  const g=new THREE.Group(); g.add(mesh); scene.add(g);
  clouds.push({g, speed:0.35+rnd()*0.5, spread});
  return g;
}
cloudDeck(7,52,70,1); cloudDeck(5,66,90,1.3);

/* gulls */
class Gull{
  constructor(cx,cy,cz,r,sp){
    this.g=new THREE.Group();
    const body=new THREE.Mesh(new THREE.BoxGeometry(1.6,0.8,0.9), new THREE.MeshLambertMaterial({color:0xf4efe4}));
    this.g.add(body);
    this.wings=[-1,1].map(s=>{
      const w=new THREE.Group();
      const pane=new THREE.Mesh(new THREE.BoxGeometry(2.6,0.28,1.0), new THREE.MeshLambertMaterial({color:0xe9e3d6}));
      pane.position.x=s*1.4; w.add(pane); this.g.add(w); return {w,s};
    });
    this.g.traverse(o=>{if(o.isMesh)o.castShadow=true;});
    scene.add(this.g);
    this.cx=cx;this.cy=cy;this.cz=cz;this.r=r;this.sp=sp;this.ph=rnd()*7;
  }
  update(t){
    const a=t*this.sp+this.ph;
    this.g.position.set(this.cx+Math.cos(a)*this.r, this.cy+Math.sin(t*0.9+this.ph)*2.2, this.cz+Math.sin(a)*this.r);
    this.g.rotation.y=-a+(this.sp>0?Math.PI:0);
    const f=Math.sin(t*6.5+this.ph)*0.6;
    this.wings.forEach(({w,s})=>w.rotation.z=s*f);
  }
}
const gulls=[ new Gull(20,22,-10,16,0.36), new Gull(16,26,6,20,0.29), new Gull(-16,20,-14,12,0.44),
              new Gull(24,30,26,14,0.33), new Gull(6,18,-22,18,-0.27) ];

/* bobbing objects: buoys, boats, fenders */
class Bobber{
  constructor(vox, x,z, opts={}){
    const b=new Vox(); const g=new THREE.Group();
    const built=makeVoxMesh(vox, solidMat,true,true,glowMaterial());
    built.meshes.forEach(m=>g.add(m));
    this.lights=opts.lights||[];
    g.position.set(x,0,z); scene.add(g); this.g=g; this.ph=opts.phase||rnd()*6; this.roll=opts.roll||0.04;
  }
  update(t){
    const x=this.g.position.x, z=this.g.position.z;
    this.g.position.y=wave(x,z,t)*0.75+0.12;
    this.g.rotation.z=Math.sin(t*1.1+this.ph)*this.roll;
    this.g.rotation.x=Math.cos(t*0.9+this.ph)*this.roll*0.7;
    this.lights.forEach(L=>L.visible=(Math.floor(t*1.2+this.ph)%2===0));
  }
}
/* buoy */
{
  const b=new Vox();
  b.cyl(0,0,2,-2,2,P.iron,0.04); b.cyl(0,0,2.6,-3,-3,P.red,0.04);
  b.box(-1,1,2,4,0,jc(P.white,0.03)); b.add(0,5,0,jc(0xff5a3c,0.01),true);
  const lampBox=new THREE.Mesh(new THREE.BoxGeometry(1,1,1), glowMaterial());
  lampBox.material.uniforms=THREE.UniformsUtils.clone({uI:{value:1}});
  const bob=new Bobber(b,-6,12,{lights:[lampBox]});
  lampBox.position.set(0,5,0); bob.g.add(lampBox); bobberList.push(bob); bob.lampMat=lampBox.material;
}
/* mooring line from bow to the buoy */
spar(scene, -16,8,-2, -9,3.5,6, 0.35, P.rig);
spar(scene, -9,3.5,6, -6,2.5,12, 0.35, P.rig);

/* rowboat with rower */
{
  const b=new Vox();
  for(let z=-3;z<=3;z++){ const w=1+(z*z<2?1:0); for(let x=-w;x<=w;x++){ b.add(x,-1,z,jc(P.wood,0.06)); if(Math.abs(x)===w) b.add(x,0,z,jc(P.woodDk,0.06)); } }
  b.box(-1,1,0,0,-1,jc(P.cream,0.04)); b.box(0,0,0,1,0,jc(0x6a5031,0.04));
  b.box(0,0,1,1,-2,jc(0xc2a878,0.02)); b.box(0,0,2,2,-2,jc(P.red,0.02));
  const bob=new Bobber(b,-40,-19,{roll:0.07,phase:2.1});
  spar(bob.g,-2,0,-1,-4,0,-1,0.3,P.sparDk); spar(bob.g,2,0,-1,4,0,-1,0.3,P.sparDk);
  bobberList.push(bob);
}
/* two fishing cobles tied up outside the quay */
[[-3,-22,0.7],[6,-25,1.9]].forEach(([x,z,ph])=>{
  const b=new Vox();
  for(let zz=-4;zz<=4;zz++){ const w=zz*zz<4?2:1; for(let xx=-w;xx<=w;xx++){
    b.add(xx,-1,zz+Math.round(x)-Math.round(x),jc(P.wood,0.06)); if(Math.abs(xx)===w) b.add(xx,0,zz,jc(P.woodDk,0.06)); } }
  b.cyl(0,0,1,0,2,jc(P.copper2,0.05)); b.box(-1,1,0,0,3,jc(P.cobble,0.06));
  const bob=new Bobber(b, x-14, z, {roll:0.06,phase:ph});
  bobberList.push(bob);
});
/* ship wreck */
{
  const b=new Vox();
  for(let i=0;i<4;i++) b.line(0,-1,-6+i*4, 0,7-i,  -6+i*4+3, P.woodDk,0.05);
  b.line(-2,0,-4,-2,4,-4,P.sparDk,0.04);
  b.cyl(2,0,-1,2,2,2,P.woodDk,0.06);
  const bob=new Bobber(b,-42,44,{roll:0.01,phase:5}); bobberList.push(bob);
}
const bobberList=window.__bob=(bobberList=[]);
function srect2(){}

/* derrick crane with a swinging crate */
const cranePivot=new THREE.Group();
{
  const c=new Vox();
  const bx=27, bz=-14, y0=9;
  [[-1,-1],[1,-1],[-1,1],[1,1]].forEach(([sx,sz])=>c.line(bx+sx,y0,bz+sz, bx+sx*0,y0+8,bz+sz*0,P.woodDk,0.04));
  c.box(bx-2,bx+2,y0+8,y0+8,bz-1,bz+1,P.wood,0.04);
  c.box(bx-1,bx+1,y0+9,y0+10,bz,jc(P.iron,0.03));
  const built=makeVoxMesh(c, solidMat,true,true,glowMaterial());
  built.meshes.forEach(m=>scene.add(m));
  spar(scene, bx,y0+10,bz, 14,14,-12, 0.9, P.sparDk);
  /* swinging crate */
  const cc=new Vox();
  cc.line(0,0,0, 0,-6,0, P.rope,0.02);
  cc.box(-1,1,-8,-6,-1,jc(P.wood,0.07));
  const cb=makeVoxMesh(cc, solidMat,true,true,glowMaterial());
  cb.meshes.forEach(m=>cranePivot.add(m));
  cranePivot.position.set(14,14,-12); scene.add(cranePivot);
  cranePivot.userData.base=cranePivot.rotation;
}
/* tavern sign that swings */
const signPivot=new THREE.Group();
{
  spar(scene,45,15,3,49,15,3,0.6,P.iron);
  const s=new Vox();
  s.box(46,49,13,14,2,jc(0x2b3f2f,0.05)); s.add(47,13,1,jc(P.gold,0.02),true);
  const b=makeVoxMesh(s,solidMat,true,false,glowMaterial());
  b.meshes.forEach(m=>signPivot.add(m));
  signPivot.position.set(0,0,0); scene.add(signPivot);
}
/* lighthouse beam */
const beacon=new THREE.Group();
{
  for(const dir of [0,Math.PI]){
    const geo=new THREE.BoxGeometry(3.2,2.4,1);
    const mat=new THREE.MeshBasicMaterial({color:0xffe3a8,transparent:true,opacity:0.16,blending:THREE.AdditiveBlending,depthWrite:false,fog:false});
    const m=new THREE.Mesh(geo,mat); m.scale.z=72;
    m.position.set(0,0,dir?36:-36); m.rotation.y=dir?Math.PI:0; beacon.add(m);
  }
  beacon.position.set(8,32.5,34); scene.add(beacon);
  const bl=new THREE.PointLight(0xffe6bd,900,180,2.0); bl.position.set(8,32.5,34); scene.add(bl); lamps.push(bl);
}
/* smoke / splash pool */
class PuffPool{
  constructor(n){
    this.n=n; this.p=[];
    this.mesh=new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1),
      new THREE.MeshLambertMaterial({vertexColors:true,transparent:true,opacity:0.85,flatShading:true}), n);
    this.mesh.frustumCulled=false;
    for(let i=0;i<n;i++){ this.p.push({alive:false}); this.mesh.setColorAt(i,new THREE.Color(0x000000)); }
    scene.add(this.mesh);
  }
  emit(x,y,z,{vy=2.6,ttl=4,r0=1,r1=3,col=0x8d8a84,drift=0}={}){
    for(let i=0;i<this.n;i++){ const p=this.p[i];
      if(!p.alive){ p.alive=true; p.t=0; p.ttl=ttl; p.x=x; p.y=y; p.z=z; p.vy=vy; p.r0=r0; p.r1=r1;
        p.col=new THREE.Color(col); p.dx=(rnd()-0.5)*drift; p.dz=(rnd()-0.5)*drift;
        this.mesh.setColorAt(i,p.col); return; } }
  }
  update(dt){
    const d=new THREE.Object3D();
    for(let i=0;i<this.n;i++){ const p=this.p[i];
      if(!p.alive){ d.position.set(0,-999,0); d.scale.setScalar(0.001); d.updateMatrix(); this.mesh.setMatrixAt(i,d.matrix); continue; }
      p.t+=dt; const k=p.t/p.ttl;
      if(k>=1){ p.alive=false; d.position.set(0,-999,0); d.scale.setScalar(0.001); d.updateMatrix(); this.mesh.setMatrixAt(i,d.matrix); continue; }
      const s=(p.r0+(p.r1-p.r0)*k)*(k<0.15?k/0.15:(k>0.8?(1-k)/0.2:1));
      p.y+=p.vy*dt*(1-k*0.4); p.x+=p.dx*dt; p.z+=p.dz*dt;
      d.position.set(p.x,p.y,p.z); d.scale.setScalar(Math.max(0.02,s)); d.rotation.set(p.t*0.6,p.t*0.4,i);
      d.updateMatrix(); this.mesh.setMatrixAt(i,d.matrix);
      this.mesh.setColorAt(i,p.col.clone().lerp(new THREE.Color(0xe8e2d6),k*0.8));
    }
    this.mesh.instanceMatrix.needsUpdate=true; this.mesh.instanceColor.needsUpdate=true;
  }
}
const puffs=new PuffPool(34);
/* muzzle flashes for the salute */
const flashMat=glowMaterial(); flashMat.uniforms=THREE.UniformsUtils.clone({uI:{value:1}});
const flashMesh=new THREE.InstancedMesh(new THREE.BoxGeometry(1.8,1.4,2.2), flashMat, 8);
flashMesh.frustumCulled=false;
{ const d=new THREE.Object3D(); d.scale.setScalar(0.001); d.updateMatrix();
  for(let i=0;i<8;i++) flashMesh.setMatrixAt(i,d.matrix); }
ship.add(flashMesh);
let flashTime=-1, flashZ=[];

/* ══════════════════════════════════════════════════════════
   11 · COMPOSITE THE STATIC WORLD
   ══════════════════════════════════════════════════════════ */
let voxTotal=0;
[[land,false],[quay,true],[town,true],[phare,true],[props,true]].forEach(([b,cast])=>{
  const r=makeVoxMesh(b, solidMat, cast, true, glowMat);
  r.meshes.forEach(m=>scene.add(m)); voxTotal+=r.count;
});
{ const r=makeVoxMesh(shipV,solidMat,true,true,glowMat); /* already added with ship */ }
voxTotal += (shipV.solid.size+shipV.glow.size)/2;
voxTotal += wx.length;
document.getElementById('vcount').textContent=Math.round(voxTotal).toLocaleString();

/* ══════════════════════════════════════════════════════════
   12 · TIME OF DAY
   ══════════════════════════════════════════════════════════ */
const K=(hex,lin=0)=>{const c=new THREE.Color(hex); return [c.r,c.g,c.b];};
const PRESETS=[
  { // FORENOON
    top:K(0x2b6a94), hor:K(0xb8d8e0), glow:K(0xfff3c8),
    fog:K(0x9dbcc7), fogD:0.0022, hemS:K(0xa8cbe0), hemG:K(0x5a6748),
    sunC:K(0xfff2cf), sunI:3.0, amb:0.22, hemi:0.62,
    sunDir:[0.18,0.78,0.60], sunCol:K(0xfff0cd), sunScale:0.85, halo:0.20, star:0.0, lamp:0.0, bands:20 },
  { // GOLDEN HOUR
    top:K(0x1f4a66), hor:K(0xe9a35c), glow:K(0xffd9a0),
    fog:K(0xd8b28c), fogD:0.0026, hemS:K(0x9fc2d0), hemG:K(0x4d5740),
    sunC:K(0xffb46b), sunI:2.15, amb:0.18, hemi:0.55,
    sunDir:[0.30,0.155,0.94], sunCol:K(0xffb46b), sunScale:1.0, halo:0.34, star:0.0, lamp:0.35, bands:15 },
  { // NIGHT WATCH
    top:K(0x04101a), hor:K(0x1a3247), glow:K(0x5f7fae),
    fog:K(0x0b1a25), fogD:0.0035, hemS:K(0x2c4358), hemG:K(0x1b2318),
    sunC:K(0xbfd3e8), sunI:0.55, amb:0.07, hemi:0.22,
    sunDir:[-0.55,0.45,-0.62], sunCol:K(0xdfe6f2), sunScale:0.55, halo:0.14, star:1.0, lamp:1.0, bands:11 }
];
let weights=[0,1,0], target=1;
const mix=i=>PRESETS.map(p=>p[i]).reduce((a,c,k)=>a+c*weights[k],0);
const mixV=i=>{ const r=[0,0,0]; PRESETS.forEach((p,k)=>{const a=p[i]; r[0]+=a[0]*weights[k];r[1]+=a[1]*weights[k];r[2]+=a[2]*weights[k];}); return new THREE.Color(r[0],r[1],r[2]); };
const mixDir=()=>{ const v=new THREE.Vector3(); PRESETS.forEach((p,k)=>{v.x+=p.sunDir[0]*weights[k];v.y+=p.sunDir[1]*weights[k];v.z+=p.sunDir[2]*weights[k];}); return v.normalize(); };

function applyPalette(){
  skyU.uTop.value.copy(mixV('top')); skyU.uHor.value.copy(mixV('hor')); skyU.uGlow.value.copy(mixV('glow'));
  skyU.uBands.value=mix('bands'); skyU.uPow.value=14+mix('sunScale')*10;
  const d=mixDir(); skyU.uSunDir.value.copy(d);
  scene.fog.color.copy(mixV('fog')); scene.fog.density=mix('fogD');
  hemi.color.copy(mixV('hemS')); hemi.groundColor.copy(mixV('hemG')); hemi.intensity=mix('hemi');
  amb.intensity=mix('amb');
  sun.color.copy(mixV('sunC')); sun.intensity=mix('sunI');
  sun.position.copy(SUNDIR).multiplyScalar(240);
  sunMesh.position.copy(d).multiplyScalar(400);
  sunMesh.scale.setScalar(mix('sunScale'));
  sunCoreMat.uniforms.uI.value=1.0; sunHaloMat.uniforms.uI.value=mix('halo');
  sunCoreMat.color=sunHaloMat.color;
  const sc=mixV('sunCol'); sunMesh.traverse(o=>{ if(o.isInstancedMesh) o.material.uniforms.uI.value=mix('halo'); });
  glowMat.uniforms.uI.value=0.85+mix('lamp')*0.75;
  const lm=mix('lamp');
  lamps.forEach((l,i)=>{ l.intensity=(i===lamps.length-1?900:170)*lm; });
  starMesh.material.uniforms.uO.value=mix('star');
  beacon.children.forEach(c=>{ if(c.material) c.material.opacity=0.05+0.28*lm; });
}
applyPalette();

const chips=[...document.querySelectorAll('.chip')];
chips.forEach(c=>c.addEventListener('click',()=>{
  chips.forEach(x=>x.classList.remove('on')); c.classList.add('on');
  target={day:0,golden:1,night:2}[c.dataset.p];
  toast({day:'Forenoon — the tide is making',golden:'Golden hour — lamps are being lit',night:'Night watch — the light is revolving'}[c.dataset.p]);
}));

/* ══════════════════════════════════════════════════════════
   13 · INTERACTION
   ══════════════════════════════════════════════════════════ */
const ray=new THREE.Raycaster();
const mouse=new THREE.Vector2();
const pickables=[...ship.children.filter(o=>o.isInstancedMesh), water];
let downAt=0, downX=0, downY=0;
renderer.domElement.addEventListener('pointerdown',e=>{downAt=performance.now();downX=e.clientX;downY=e.clientY;});
renderer.domElement.addEventListener('pointerup',e=>{
  if(performance.now()-downAt>420) return;
  if(Math.abs(e.clientX-downX)+Math.abs(e.clientY-downY)>6) return;
  mouse.set((e.clientX/innerWidth)*2-1, -(e.clientY/innerHeight)*2+1);
  ray.setFromCamera(mouse,camera);
  const hitS=ray.intersectObjects(pickables.filter(o=>o.userData.ship),false)[0];
  if(hitS){ salute(); return; }
  const hitW=ray.intersectObject(water,false)[0];
  if(hitW){ const p=hitW.point;
    for(let i=0;i<10;i++) puffs.emit(p.x+(rnd()-0.5)*2, 0.4, p.z+(rnd()-0.5)*2,
      {vy:5+rnd()*4, ttl:1.6+rnd(), r0:0.6, r1:2.2, col:0xcfeef6, drift:2});
    toast('A mark in the water — soundings hold at nine fathoms');
  }
});
function salute(){
  flashZ=[-12,-4,4,12,-8,8]; flashTime=0.34;
  flashZ.forEach(z=>{
    const y=2.5, x=Math.round(7*Math.pow(Math.max(0,Math.sin(Math.PI*((z+23)/45)*0.79+0.20)),0.42));
    for(let i=0;i<4;i++) puffs.emit(-19+ (z+2)*0.55, 3.2, -2+x+i*1.2, {vy:1.6, ttl:3.4, r0:1.2, r1:4.2, col:0x6a6a66, drift:3});
    puffs.emit(-19+ (z+2)*0.55, 2.4, -2+x, {vy:4.5, ttl:1.1, r0:1.5, r1:3.5, col:0xffd9a0});
  });
  toast('Fair salute — thirty-two guns, and the powder is damp');
}
const toastEl=document.getElementById('toast'); let toastT=0;
function toast(msg){ toastEl.textContent=msg; toastEl.classList.add('show'); toastT=4.2; }

/* ══════════════════════════════════════════════════════════
   14 · LOOP
   ══════════════════════════════════════════════════════════ */
const clock=new THREE.Clock(); let t=0, fpsAcc=0, fpsN=0, fpsTimer=0;
const fpsEl=document.getElementById('fps'), needle=document.getElementById('needle'), hint=document.getElementById('hint');
let hintFaded=false;

function loop(){
  const dt=Math.min(0.05, clock.getDelta()); t+=dt;
  U.time.value=t;

  /* smooth time-of-day crossfade */
  const w=weights; const goal=target;
  for(let i=0;i<3;i++){ w[i]+= ((i===goal)?1:0 - w[i])*Math.min(1,dt*1.6); }
  const s=w[0]+w[1]+w[2]; for(let i=0;i<3;i++) w[i]/=s;
  applyPalette();

  /* the barque rides at her mooring */
  ship.position.y=wave(-19,-2,t)*0.8+0.15;
  ship.rotation.z=Math.sin(t*0.62)*0.024;
  ship.rotation.x=Math.sin(t*0.47+1.2)*0.014;
  ship.rotation.y=-Math.PI/2+0.22+Math.sin(t*0.23)*0.02;
  animateFlag(ensign,t); animateFlag(pennant,t*1.35);

  updateWater(t);

  /* muzzle flash lifetime */
  if(flashTime>=0){
    flashTime-=dt;
    const d=new THREE.Object3D();
    flashZ.forEach((z,i)=>{
      const x=Math.round(7*Math.pow(Math.max(0,Math.sin(Math.PI*((z+23)/45)*0.79+0.20)),0.42));
      const on=flashTime>0?(i%2? Math.sin(t*40)>0 : Math.sin(t*40)<0):false;
      d.position.set(-x*(1), 2.5, z); d.scale.setScalar(on?1.6:0.001); d.updateMatrix();
      flashMesh.setMatrixAt(i,d.matrix);
    });
    flashMesh.instanceMatrix.needsUpdate=true;
    if(flashTime<0) flashMesh.position.set(0,-999,0);
  } else flashMesh.position.set(0,-999,0);

  /* beacon sweeps the bay */
  beacon.rotation.y=t*0.62;

  /* chimneys */
  if((t*1.0)%0.42<dt){ puffs.emit(46.5,30,-11.5,{vy:2.4,ttl:6,r0:0.9,r1:3.4,col:0x4b4a47,drift:1.4}); }
  if((t*1.0)%0.68<dt){ puffs.emit(19.5,22,37,{vy:2.0,ttl:5,r0:0.8,r1:2.8,col:0x5a5854,drift:1.2}); }
  if((t*1.0)%0.95<dt){ puffs.emit(49.5,17,14.5,{vy:1.8,ttl:5,r0:0.8,r1:2.6,col:0x5f5d59,drift:1.1}); }
  puffs.update(dt);

  /* gulls, bobbers, clouds, crane, sign */
  gulls.forEach(g=>g.update(t));
  bobberList.forEach(b=>b.update(t));
  clouds.forEach(c=>{ c.g.position.x=(c.g.position.x+c.speed*dt*2)>c.spread*2? -c.spread*2 : c.g.position.x+c.speed*dt*2; });
  cranePivot.rotation.z=Math.sin(t*0.95)*0.075;
  cranePivot.rotation.x=Math.sin(t*0.7+1)*0.045;
  signPivot.rotation.z=Math.sin(t*1.05)*0.10;
  bobberList.forEach(b=>{ if(b.lampMat) b.lampMat.uniforms.uI.value=(Math.floor(t*1.1+b.ph)%2?2.4:0.15); });

  controls.update();
  needle.style.transform=`rotate(${-controls.getAzimuthalAngle()}rad)`;
  if(!hintFaded && t>9){ hint.style.opacity='0.25'; hintFaded=true; }
  if(toastT>0){ toastT-=dt; if(toastT<=0) toastEl.classList.remove('show'); }

  fpsTimer+=dt; fpsN++;
  if(fpsTimer>0.5){ fpsEl.textContent=Math.round(fpsN/fpsTimer); fpsN=0; fpsTimer=0; }

  renderer.render(scene,camera);
  requestAnimationFrame(loop);
}
addEventListener('resize',()=>{
  camera.aspect=innerWidth/innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight);
});

/* fade in */
requestAnimationFrame(()=>{
  loop();
  setTimeout(()=>document.getElementById('load').classList.add('done'),260);
  setTimeout(()=>toast('The barque rides off the town quay · click her hull'),1600);
});
</script>
</body>
</html>
```

**What's in it**

- **One draw call per material family.** A `Vox` builder fills a hash-map of voxel keys, then hides every fully-surrounded cube before it ever reaches the GPU — the whole town, quay, breakwater and hull land in a handful of instanced meshes.
- **The sea is voxels too:** ~9,000 tall cubes whose tops snap to a quantised wave field (3-float writes per frame), so the harbour terraces in half-unit steps like any hand-built voxel set. Foam, wake, crest brightening and sun-glints are computed in a patched Lambert fragment shader, so shadows and fog stay physically consistent.
- **A sky that steps:** the dome gradient is posterised into 11–20 hard bands, so the horizon reads as stacked blocks rather than a soft wash — and it re-tunes itself for each of three watches (*Forenoon / Golden hour / Night*), cross-fading fog, hemispheres, lamp intensity, star opacity and the colour of the sun itself.
- **Alive on purpose:** the barque rolls at her mooring, her ensign and pennant animate per-instance, the lighthouse beam sweeps the bay while the point lights swell at dusk, chimney smoke rises from three stacks, five gulls flap on tilted orbits, clouds drift on two parallax decks, the derrick's crate swings, the tavern sign ticks in the wind, buoys blink and a rowboat bobs.
- **It answers back:** click the hull for a gun-port salute with muzzle flashes and drifting powder smoke; click the sea to drop a mark and kick up a splash. A brass compass in the corner tracks your orbit, and the type is a ship's placard — Archivo Black over Manrope.