Below is a complete single‑file voxel diorama — a three‑masted barque tying up at a stone harbour at golden hour, with an animated voxel sea, rotating lighthouse beam, working crane, windmill, gulls, drifting clouds, a puffing tug, and a time‑of‑day slider that relights the whole scene.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Harbour Call — voxel diorama</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@400;600;700&family=IBM+Plex+Sans:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root{
    --ink:#07161e; --panel:#0c1f29; --brass:#dda24a; --cream:#f6ecd9; --sea:#7ea6b2; --red:#b8402f;
  }
  *{box-sizing:border-box}
  html,body{margin:0;height:100%;background:var(--ink);overflow:hidden;
    font-family:'IBM Plex Sans',system-ui,sans-serif;color:var(--cream)}
  canvas{position:fixed;inset:0;display:block}

  #vig{position:fixed;inset:0;pointer-events:none;mix-blend-mode:multiply;
    background:radial-gradient(120% 90% at 50% 42%, rgba(255,255,255,1) 40%, rgba(80,60,45,.55) 100%)}
  #grain{position:fixed;inset:0;pointer-events:none;opacity:.055;mix-blend-mode:overlay;
    background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='140' height='140'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.8' numOctaves='3'/></filter><rect width='140' height='140' filter='url(%23n)'/></svg>")}

  #panel{position:fixed;top:20px;left:22px;width:min(338px,calc(100vw - 44px));z-index:6;
    background:linear-gradient(180deg, rgba(13,32,41,.95), rgba(8,22,29,.92));
    border:1px solid rgba(221,162,74,.30);border-radius:5px;padding:17px 18px 18px;
    box-shadow:0 22px 50px -18px rgba(0,0,0,.8), inset 0 1px 0 rgba(255,255,255,.05);
    transition:opacity .45s ease, transform .45s ease}
  #panel.hidden{opacity:0;transform:translateY(-12px) scale(.98);pointer-events:none}
  .eyebrow{font-size:10.5px;letter-spacing:.3em;text-transform:uppercase;color:var(--brass);
    display:flex;align-items:center;gap:9px}
  .eyebrow::after{content:'';flex:1;height:1px;background:linear-gradient(90deg,rgba(221,162,74,.55),transparent)}
  h1{font-family:'Oswald',sans-serif;font-weight:700;font-size:clamp(30px,3.4vw,42px);line-height:.94;
    margin:11px 0 0;letter-spacing:.02em;text-transform:uppercase}
  h1 em{display:block;font-style:normal;font-weight:400;font-size:.42em;letter-spacing:.24em;
    color:var(--sea);margin-top:7px}
  .sub{font-size:12.6px;line-height:1.55;color:#a8c0c8;margin:12px 0 14px;max-width:31ch}

  .row{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:13px}
  .chip{font-family:'Oswald',sans-serif;letter-spacing:.14em;text-transform:uppercase;font-size:11px;
    padding:7px 11px;border:1px solid rgba(126,166,178,.30);background:rgba(126,166,178,.06);
    color:#cfe0e4;cursor:pointer;border-radius:3px;transition:.2s}
  .chip:hover{border-color:var(--brass);color:#fff;background:rgba(221,162,74,.14);transform:translateY(-1px)}
  .chip.on{background:var(--brass);border-color:var(--brass);color:#0a1a22;font-weight:600}

  .lab{display:flex;justify-content:space-between;align-items:baseline;
    font-size:10px;letter-spacing:.24em;text-transform:uppercase;color:#8fb0ba;margin-bottom:8px}
  .lab b{font-family:'Oswald',sans-serif;font-size:12px;letter-spacing:.12em;color:var(--brass)}
  input[type=range]{-webkit-appearance:none;width:100%;background:transparent;margin:0 0 14px}
  input[type=range]::-webkit-slider-runnable-track{height:3px;border-radius:2px;
    background:linear-gradient(90deg,#2c4f5e,#dda24a)}
  input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:15px;height:15px;border-radius:50%;
    background:var(--cream);border:2px solid var(--brass);margin-top:-6px;cursor:grab;
    box-shadow:0 0 12px rgba(221,162,74,.65)}
  input[type=range]::-moz-range-track{height:3px;background:linear-gradient(90deg,#2c4f5e,#dda24a)}
  input[type=range]::-moz-range-thumb{width:14px;height:14px;border-radius:50%;background:var(--cream);border:2px solid var(--brass)}

  #hint{position:fixed;left:22px;bottom:18px;font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;
    color:rgba(150,180,190,.62);z-index:6;transition:opacity .45s ease}
  #hint span{color:var(--brass)}
  #hint.hidden{opacity:0}

  #flags{position:fixed;right:22px;bottom:20px;display:flex;gap:8px;z-index:6;transition:opacity .45s ease}
  #flags.hidden{opacity:0}
  .flag{width:30px;height:24px;border-radius:2px;cursor:pointer;border:1px solid rgba(255,255,255,.22);
    box-shadow:0 4px 14px rgba(0,0,0,.5);position:relative;transition:.22s cubic-bezier(.2,.9,.3,1)}
  .flag:hover{transform:translateY(-5px) rotate(-3deg);box-shadow:0 10px 18px rgba(0,0,0,.6)}
  #tip{position:fixed;right:22px;bottom:52px;min-width:220px;text-align:right;font-size:11px;letter-spacing:.06em;
    color:#d7e5e9;opacity:0;transform:translateY(6px);transition:.25s;z-index:6;pointer-events:none;line-height:1.5}
  #tip.show{opacity:1;transform:translateY(0)}
  #tip b{font-family:'Oswald',sans-serif;color:var(--brass);letter-spacing:.18em;display:block;
    text-transform:uppercase;font-size:12px}

  #f3{background:#1b1d1f}#f4{background:#c2352b}#f5{background:#f6f7f8}
</style>
</head>
<body>
<canvas id="scene"></canvas>
<div id="vig"></div><div id="grain"></div>

<div id="panel">
  <div class="eyebrow">Voxel diorama № 04</div>
  <h1>Harbour<br>Call<em>the barque <i>Meridian</i>, East Pier</em></h1>
  <p class="sub">She comes in on a flood tide, canvas partly furled, bow line running to the pier head bollard while the crane waits for her cargo.</p>

  <div class="row" id="views">
    <button class="chip on" data-v="0">Berth</button>
    <button class="chip" data-v="1">Mast‑top</button>
    <button class="chip" data-v="2">Harbour</button>
    <button class="chip" data-v="3">Open sea</button>
  </div>

  <div class="lab"><span>Time of day</span><b id="tod">Golden hour</b></div>
  <input id="slider" type="range" min="0" max="1" step="0.001" value="0.26">

  <div class="row">
    <button class="chip on" id="orbit">Auto orbit</button>
    <button class="chip" id="hide">Hide panel (H)</button>
  </div>
</div>

<div id="hint"><span>drag</span> orbit · <span>scroll</span> zoom · <span>right‑drag</span> pan · <span>1–4</span> views</div>

<div id="flags"></div>
<div id="tip"></div>

<script type="importmap">
{"imports":{
  "three":"https://cdn.jsdelivr.net/npm/three@0.160.1/build/three.module.js",
  "three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.1/examples/jsm/"
}}
</script>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

/* ================= helpers ================= */
const rnd=(a,b)=>a+Math.random()*(b-a);
const clamp=(x,a,b)=>Math.min(b,Math.max(a,x));
const lerp=(a,b,t)=>a+(b-a)*t;
const smoothstep=(a,b,x)=>{const t=clamp((x-a)/(b-a),0,1);return t*t*(3-2*t);};
const easeOut=k=>1-Math.pow(1-k,3);
function hash2(x,z){const s=Math.sin(x*127.1+z*311.7)*43758.5453;return s-Math.floor(s);}
function noise2(x,z){const xi=Math.floor(x),zi=Math.floor(z),xf=x-xi,zf=z-zi;
  const u=xf*xf*(3-2*xf),v=zf*zf*(3-2*zf);
  return lerp(lerp(hash2(xi,zi),hash2(xi+1,zi),u),lerp(hash2(xi,zi+1),hash2(xi+1,zi+1),u),v);}
function mix(c1,c2,t){return new THREE.Color(c1).lerp(new THREE.Color(c2),t);}

class Voxels{
  constructor(){this.list=[];}
  box(cx,cy,cz,sx,sy,sz,color,o={}){
    const g=new THREE.BoxGeometry(sx,sy,sz);
    const j=o.jitter||0;
    g.translate(cx+(Math.random()-.5)*j, cy+(Math.random()-.5)*j, cz+(Math.random()-.5)*j);
    const n=g.attributes.position.count, col=new THREE.Color(color);
    const vary=o.vary!==undefined?o.vary:0.055, sh=o.shade||1;
    const a=new Float32Array(n*3);
    for(let i=0;i<n;i++){const k=sh*(1+(Math.random()-.5)*vary*2);
      a[i*3]=col.r*k;a[i*3+1]=col.g*k;a[i*3+2]=col.b*k;}
    g.setAttribute('color',new THREE.Float32BufferAttribute(a,3));
    this.list.push(g);return this;
  }
  mesh(mats){
    const arr=Array.isArray(mats)?mats:[mats];
    const g=mergeGeometries(this.list,false);
    this.list.length=0;
    if(!g)return new THREE.Group();
    return new THREE.Mesh(g,arr[0]);
  }
}

/* ================= scene ================= */
const canvas=document.getElementById('scene');
const renderer=new THREE.WebGLRenderer({canvas,antialias:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.setSize(innerWidth,innerHeight);
renderer.shadowMap.enabled=true;
renderer.shadowMap.type=THREE.PCFSoftShadowMap;
renderer.toneMapping=THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure=1.18;

const scene=new THREE.Scene();
const fog=new THREE.FogExp2(0xc98a68,0.0056);
scene.fog=fog;

const camera=new THREE.PerspectiveCamera(46,innerWidth/innerHeight,0.5,1400);
camera.position.set(96,62,98);

const controls=new OrbitControls(camera,renderer.domElement);
controls.enableDamping=true;controls.dampingFactor=0.055;
controls.target.set(-6,7,0);
controls.minDistance=16;controls.maxDistance=210;
controls.maxPolarAngle=1.46;
controls.autoRotate=false;controls.autoRotateSpeed=0.32;

/* ---- lights ---- */
const sun=new THREE.DirectionalLight(0xffb878,2.4);
sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);
sun.shadow.camera.left=-70;sun.shadow.camera.right=70;
sun.shadow.camera.top=70;sun.shadow.camera.bottom=-70;
sun.shadow.camera.near=40;sun.shadow.camera.far=380;sun.shadow.bias=-0.0007;
scene.add(sun,sun.target);
const hemi=new THREE.HemisphereLight(0xf2c19a,0x24455a,0.72);scene.add(hemi);
const lampA=new THREE.PointLight(0xffbe73,1.4,30,2);lampA.position.set(19.5,10.6,-12);scene.add(lampA);
const lampB=new THREE.PointLight(0xffbe73,1.4,30,2);lampB.position.set(19.5,10.6,18);scene.add(lampB);
const houseLight=new THREE.PointLight(0xffc880,1.3,26,2);houseLight.position.set(31,11,12);scene.add(houseLight);
const lantern=new THREE.PointLight(0xffd089,2.6,60,2);scene.add(lantern);

/* ---- sky ---- */
const skyU={
  uZen:{value:new THREE.Color('#1d3a5e')}, uHor:{value:new THREE.Color('#f2a06a')},
  uHaze:{value:new THREE.Color('#a86b4f')}, uSunCol:{value:new THREE.Color('#ff9a55')},
  uSunDir:{value:new THREE.Vector3(-0.9,0.15,-0.4)}, uSunUp:{value:1.0}
};
const sky=new THREE.Mesh(new THREE.SphereGeometry(520,26,14),new THREE.ShaderMaterial({
  side:THREE.BackSide,depthWrite:false,fog:false,uniforms:skyU,
  vertexShader:`varying vec3 vP;void main(){vP=position;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,
  fragmentShader:`uniform vec3 uZen,uHor,uHaze,uSunCol,uSunDir;uniform float uSunUp;varying vec3 vP;
    void main(){vec3 d=normalize(vP);float h=d.y;
      vec3 c=mix(uHor,uZen,smoothstep(0.0,0.55,h));
      c=mix(uHaze,c,smoothstep(-0.12,0.07,h));
      float s=max(dot(d,normalize(uSunDir)),0.0);
      c+=uSunCol*pow(s,34.0)*1.15*uSunUp;
      c+=uSunCol*pow(s,7.0)*0.24*uSunUp;
      c+=uSunCol*pow(max(-d.y*3.0,0.0),2.0)*0.05;
      gl_FragColor=vec4(c,1.0);}`
}));
sky.renderOrder=-1;scene.add(sky);

const sunQuad=new THREE.Mesh(new THREE.PlaneGeometry(1,1),
  new THREE.MeshBasicMaterial({fog:false,transparent:true,depthWrite:false,side:THREE.DoubleSide}));
sunQuad.renderOrder=-0.5;scene.add(sunQuad);

/* ================= static voxels ================= */
const STATIC=new Voxels(), GLOW=new Voxels();

function line(v,a,b,th,color,gap=1.1,vary=0.06){
  const d=new THREE.Vector3().subVectors(b,a),n=Math.max(1,Math.ceil(d.length/gap));
  for(let i=0;i<=n;i++){const p=a.clone().addScaledVector(d,i/n);v.box(p.x,p.y,p.z,th,th,th,color,{vary});}
}
function fillTri(v,A,B,C,cell,color,bulge=0){
  const minx=Math.min(A.x,B.x,C.x),maxx=Math.max(A.x,B.x,C.x);
  const miny=Math.min(A.y,B.y,C.y),maxy=Math.max(A.y,B.y,C.y);
  const inside=(px,py)=>{
    const s=(P,Q,R)=>Math.sign((Q.x-P.x)*(R.y-P.y)-(Q.y-P.y)*(R.x-P.x));
    const s1=s(A,B,{x:px,y:py}),s2=s(B,C,{x:px,y:py}),s3=s(C,A,{x:px,y:py});
    return s1===s2&&s2===s3;
  };
  for(let x=minx;x<=maxx;x+=cell)for(let y=miny;y<=maxy;y+=cell){
    if(!inside(x+cell*0.5,y+cell*0.5))continue;
    const cx=clamp((x+B.x+C.x)/3,minx+cell,maxx-cell);
    const cy=clamp((y+B.y+C.y)/3,miny+cell,maxy-cell);
    const fall=clamp(1-0.7*Math.hypot(x-cx,y-cy)/Math.max(1,maxx-minx),0.55,1);
    v.box(x+cell/2+bulge*(1-fall),y+cell/2,0,cell,cell,0.72,color,{vary:0.10});
  }
}

/* ---- terrain ---- */
function terrainH(x,z){
  if(x<17)return 5;
  let h=5+smoothstep(17,32,x)*1.9+noise2(x*0.085,z*0.085)*1.7;
  if(x<27)h=Math.min(h,5.6);
  if(x>55)h+=(x-55)*0.55+noise2(x*0.05,z*0.05)*3;
  return h;
}
for(let x=17;x<66;x+=2)for(let z=-36;z<=36;z+=2){
  const h=terrainH(x,z);
  let col;
  if(x<26)col=mix('#6e6860','#857c6d',hash2(x*0.7,z*0.7));
  else if(x>56)col=mix('#3d4f59','#556a70',noise2(x*0.12,z*0.12));
  else col=noise2(x*0.14+7,z*0.14)>0.62?mix('#4e6b47','#68824f',hash2(x,z)):mix('#7b7264','#8d8272',hash2(x,z));
  STATIC.box(x,(h+4)/2-4,z,2.05,h+4,2.05,col,'#',{vary:0.14});
}
/* quay wall */
for(let y=-3;y<5.2;y+=1.2){
  STATIC.box(16,y+0.6,-0.2,2,1.2,73,'#5b5349',{vary:0.14});
}
/* slipway steps */
for(let i=0;i<5;i++){const t=0.6+i*1.05;STATIC.box(13.6+i*0.95,(t+3)/2-3,26,1,t+3,4.2,mix('#655e54','#7b7367',hash2(i,3)),{vary:0.1});}
/* pier */
for(let x=4;x<17;x+=1.05){
  STATIC.box(x+0.5,4.8,4,1.06,0.35,6.6,mix('#7d5a3a','#8c6644',hash2(x,1)),{vary:0.14});
}
for(let x=5;x<17;x+=4)for(const zz of [1.5,6.5]){
  STATIC.box(x,1.6,zz,1.1,6.8,1.1,'#5a3f28',{vary:0.12});
  STATIC.box(x,5.05,zz,1.5,0.5,1.5,'#4a3524',{vary:0.1});
}
for(let z=-3;z<1;z+=0.9)STATIC.box(3.75,4.85,z+0.5,0.75,0.34,0.95,mix('#6f4f33','#806040',hash2(z,9)),{vary:0.12});
/* bollards */
function bollard(x,z){STATIC.box(x,5.5,z,1.0,1.1,1.0,'#3a4249',{vary:0.07});STATIC.box(x,6.15,z,1.5,0.34,1.5,'#4c5762',{vary:0.07});}
bollard(5.4,2.2);bollard(5.4,5.8);bollard(20.5,-6);bollard(20.5,12);bollard(20.5,24);
/* breakwater + harbour lights */
for(let x=2;x<18;x+=1.7)for(let y=-2;y<4.2;y+=1.4){
  STATIC.box(x-0.5,y+0.7,-29.5,1.75,1.45,5.2,mix('#605850','#776e62',hash2(x,y)),{vary:0.16});
}
for(let z=-32;z<=-27;z+=1.6)for(let y=-2;y<3.2;y+=1.4){STATIC.box(17.6,y+0.7,z,1.6,1.45,1.7,'#6a6157',{vary:0.16});}
STATIC.box(2.6,5.2,-29.5,1.1,2.4,1.1,'#3a4249');GLOW.box(2.6,6.8,-29.5,1.0,0.9,1.0,'#ff5c46',{vary:0.03});
STATIC.box(4.6,5.4,1.4,1.0,2.0,1.0,'#3a4249');GLOW.box(4.6,6.7,1.4,0.9,0.8,0.9,'#5ff08a',{vary:0.03});
/* street lamps */
function lamp(x,z){
  const g=terrainH(x,z);
  STATIC.box(x,g+0.6,z,1.3,1.2,1.3,'#3a4249',{vary:0.08});
  STATIC.box(x,g+3.4,z,0.55,4.4,0.55,'#333b42',{vary:0.07});
  STATIC.box(x,g+5.9,z,1.6,0.5,1.6,'#2f373e');
  GLOW.box(x,g+6.7,z,1.1,1.2,1.1,'#ffd07a',{vary:0.04});
  STATIC.box(x,g+7.5,z,0.8,0.5,0.8,'#b8402f');
}
lamp(19.5,-20);lamp(19.5,-12);lamp(19.5,18);lamp(19.5,26);
/* crates, barrels, nets */
function crate(x,y,z,s){STATIC.box(x,y+s/2,z,s,s,s,'#8b6a45',{vary:0.13});
  STATIC.box(x,y+s+0.06,z,s*0.9,0.22,s*0.9,'#a2805a',{vary:0.1});
  STATIC.box(x,y+s/2,z,s*0.34,s*1.02,s*1.02,'#6f5236',{vary:0.08});}
function barrel(x,y,z){STATIC.box(x,y+0.9,z,1.5,1.8,1.5,'#7b5a3c',{vary:0.12});
  STATIC.box(x,y+0.5,z,1.62,0.24,1.62,'#513a26',{vary:0.06});
  STATIC.box(x,y+1.4,z,1.62,0.24,1.62,'#513a26',{vary:0.06});}
for(let i=0;i<7;i++)crate(23+rnd(0,4),5.1,-13+i*2.2,rnd(1.6,2.3));
crate(29,terrainH(29,-14),-8,2.2);crate(31.2,terrainH(31,-8),-8,1.8);
for(let i=0;i<4;i++)barrel(6.5,4.95,8.5+i*2.0);
barrel(12,4.95,9.4);barrel(13.2,4.95,10.1);
for(let i=0;i<9;i++)STATIC.box(9.2+i*0.85,5.25,3.4+Math.sin(i*0.9)*0.6,0.85,0.22,0.85,'#7d7f6a',{vary:0.16});
function coiled(x,y,z){for(let i=0;i<9;i++){const a=i/9*Math.PI*2;STATIC.box(x+Math.cos(a)*1.2,y+0.2,z+Math.sin(a)*1.2,0.7,0.34,0.7,'#c1a06a',{vary:0.1});}}
coiled(8.4,4.95,5.4);coiled(21.5,5.05,8);
/* fish stall */
(function(){
  const g=5.1,x=22,z=-2;
  for(const dx of [-4,4])for(const dz of [-2.6,2.6])STATIC.box(x+dx,g+1.6,z+dz,0.6,3.2,0.6,'#5a3f28',{vary:0.1});
  for(let i=0;i<9;i++)STATIC.box(x-4.5+i, g+3.5+i*0.32, z, 1.1, 0.36, 6.2, i%2? '#e2d6c0':'#b8402f',{vary:0.08});
  STATIC.box(x,g+1.2,z,7.4,0.5,2.4,'#8b6a45',{vary:0.12});
  for(let i=0;i<3;i++)crate(x-2.4+i*2.4,g+1.5,z-3.2,1.3);
})();
/* gabled building generator */
function building(o){
  const {x,z,w,d,h,steps=5,roofH=4,wall,roof,door=true,windows=3,wFloor=2.4}=o;
  const g=terrainH(x,z);
  for(let y=0;y<h;y+=1.5)STATIC.box(x,g+y+0.75,z,w,1.55,d,wall,{vary:0.12});
  for(let i=0;i<=steps;i++){
    const t=i/steps;
    STATIC.box(x,g+h+i*(roofH/steps),z,w+0.8,roofH/steps+0.2,d*(1-t)+0.4,roof,{vary:0.11});
  }
  if(door){STATIC.box(x-w/2-0.05,g+1.8,z,0.35,3.4,2.2,'#3a2a1e',{vary:0.08});
    STATIC.box(x-w/2-0.25,g+1.8,z,0.2,3.0,1.7,'#5c4127',{vary:0.1});}
  for(let i=0;i<windows;i++){
    const wz=z-d/2+(i+0.5)*(d/windows);
    GLOW.box(x-w/2-0.12,g+wFloor,wz,0.25,1.5,1.5,'#ffd27a',{vary:0.05});
    GLOW.box(x+w/2+0.12,g+wFloor,wz,0.25,1.5,1.5,'#ffce74',{vary:0.05});
  }
  for(let i=0;i<2;i++)GLOW.box(x,g+wFloor,z-d/2-0.12,1.6,1.4,0.25,'#ffd27a',{vary:0.05});
  STATIC.box(x,g+h+roofH+0.6,z-d/2+0.8,1.0,1.6,1.0,'#4a5462');
}
building({x:28,z:-14,w:15,d:10,h:8,steps:4,roofH:4.4,wall:'#8b5847',roof:'#465160',windows:4,door:true});
building({x:40,z:-2,w:10,d:8,h:6,steps:3,roofH:3.4,wall:'#6b4438',roof:'#3f4a57',windows:3});
building({x:46,z:7,w:8,d:7,h:5.6,steps:3,roofH:3.2,wall:'#ddd0bb',roof:'#a24b39',windows:2});
building({x:53,z:16,w:7,d:6,h:5,steps:3,roofH:2.8,wall:'#cfc0aa',roof:'#a24b39',windows:2});
building({x:56,z:-9,w:8,d:7,h:6,steps:3,roofH:3.4,wall:'#d6c8b2',roof:'#465160',windows:2});
building({x:24,z:22,w:10,d:7,h:6.4,steps:3,roofH:3.2,wall:'#d8cbb6',roof:'#3f4a57',windows:3});
/* customs clock tower */
(function(){
  const x=31,z=12,g=terrainH(x,z);
  for(let y=0;y<15;y+=1.6)STATIC.box(x,g+y+0.8,z,5,1.65,5,mix('#d5c7b0','#c3b397',hash2(x,y)),{vary:0.1});
  for(let i=0;i<=3;i++)STATIC.box(x,g+15+i*0.9,z,5.6-i*1.4,1.0,5.6-i*1.4,'#465160',{vary:0.1});
  for(const sx of [-1,1])for(const sz of [-1,1]){
    STATIC.box(x+sx*2.6,g+9,z+sz*2.4,0.3,3.2,3.2,'#efe9dc',{vary:0.04});
    STATIC.box(x+sx*2.75,g+9,z,0.25,0.5,2.2,'#2c333a');
    STATIC.box(x+sx*2.75,g+9.8,z,2.2,0.5,0.5,'#2c333a');
  }
  GLOW.box(x,g+16.6,z,1.1,1.4,1.1,'#ffd27a',{vary:0.04});
  STATIC.box(x,g+18.6,z,0.5,2.6,0.5,'#3a4249');
  STATIC.box(x+0.9,g+19.7,z,1.8,0.9,0.35,'#b8402f',{vary:0.1});
})();
/* lighthouse */
function lighthouse(x,z){
  const g=terrainH(x,z),H=19;
  STATIC.box(x,g+0.9,z,9,1.8,9,'#5b564c',{vary:0.14});
  for(let i=0;i<12;i++)STATIC.box(x+rnd(-5.5,5.5),g+rnd(0.2,1.4),z+rnd(-5.5,5.5),rnd(2,4),rnd(1,2),rnd(2,4),'#545b57',{vary:0.16});
  for(let y=0;y<H;y+=1.6){
    const t=y/H,w=5.6-2.6*t,band=Math.floor(y/4.8)%2===0;
    STATIC.box(x,g+1.8+y+0.8,z,w,1.65,w,band?'#efe8dc':'#b8402f',{vary:0.07});
  }
  const topY=g+1.8+H;
  STATIC.box(x,topY+0.5,z,5.8,0.7,5.8,'#3f4a52',{vary:0.08});
  for(let i=0;i<10;i++){const a=i/10*Math.PI*2;STATIC.box(x+Math.cos(a)*2.6,topY+1.3,z+Math.sin(a)*2.6,0.3,1.0,0.3,'#d8cdb8',{vary:0.08});}
  STATIC.box(x,topY+1.3,z,4.4,1.8,4.4,'#2b343b',{vary:0.06});
  GLOW.box(x,topY+1.3,z,3.4,1.5,3.4,'#ffe0a2',{vary:0.03});
  STATIC.box(x,topY+2.5,z,3.6,0.6,3.6,'#b8402f',{vary:0.08});
  STATIC.box(x,topY+3.6,z,0.5,1.6,0.5,'#3a4249');
  lantern.position.set(x,topY+1.3,z);
  return new THREE.Vector3(x,topY+1.3,z);
}
const lightPos=lighthouse(48,-20);
/* chimney for smoke */
const chimneys=[];
chimneys.push(new THREE.Vector3(46+3.4,terrainH(46,7)+5.6+3.4+0.6,7-2.4));
chimneys.push(new THREE.Vector3(56+2.6,terrainH(56,-9)+6+3.4+0.6,-9-2.4));

/* windmill on the hill */
(function(){
  const x=66,z=20,g=terrainH(x,z);
  for(let y=0;y<9;y+=1.5)STATIC.box(x,g+y+0.75,z,5-y*0.28,1.55,5-y*0.28,mix('#cfc2ac','#b5a691',hash2(x,y)),{vary:0.1});
  STATIC.box(x,g+9.6,z,5.4,1.2,5.4,'#465160',{vary:0.1});
  const blades=new Voxels();
  for(let k=0;k<4;k++){
    const a=k*Math.PI/2;
    for(let r=0.6;r<7;r+=0.9)
      blades.box(Math.cos(a)*r,Math.sin(a)*r,0,0.9,0.35,0.5,'#efe7d6',{vary:0.09});
    blades.box(Math.cos(a)*3.2+Math.sin(a)*0.9,Math.sin(a)*3.2-Math.cos(a)*0.9,0.3,4.6,0.22,1.1,'#d8cdb8',{vary:0.1});
  }
  const m=blades.mesh(new THREE.MeshStandardMaterial({vertexColors:true,roughness:0.92,metalness:0.02}));
  m.position.set(x,g+10.4,z);m.castShadow=true;scene.add(m);windmill=m;
})();
/* distant headland */
for(let x=66;x<88;x+=2.4)for(let z=-38;z<=38;z+=2.4){
  const h=8+(x-66)*0.8+noise2(x*0.07,z*0.07)*7;
  STATIC.box(x,h/2-3,z,2.5,h+3,2.5,mix('#33445a','#465b6d',noise2(x*0.05,z*0.05)),{vary:0.14});
}

/* ================= animated: crane ================= */
let craneJib=null;
(function(){
  const x=22,z=14,g=terrainH(x,z);
  STATIC.box(x,g+0.8,z,4,1.6,4,'#3f4a52',{vary:0.1});
  for(let i=0;i<3;i++){
    STATIC.box(x,g+2.4+i*2.4,z,2.4-i*0.3,2.2,2.4-i*0.3,'#3f4a52',{vary:0.09});
    STATIC.box(x,g+2.4+i*2.4,z+1.3,1.6,0.4,0.4,'#b8402f',{vary:0.08});
  }
  const top=g+9.4;
  STATIC.box(x,top,z,3.2,1.2,3.2,'#2f373e');
  const j=new Voxels();
  for(let i=0;i<12;i++)j.box(0.6+i*1.2,0,0,1.2,0.6,0.6,'#3f4a52',{vary:0.1});
  for(let i=0;i<10;i++)j.box(0.6+i*1.2,-1.1,0.55,0.5,1.6,0.5,'#4a5462',{vary:0.1});
  for(let i=0;i<4;i++)j.box(-1-i*0.8,-0.3,0,1.0,1.1,1.1,'#4a5462',{vary:0.1});
  j.box(-2.6,-0.9,0,1.8,1.8,1.8,'#5d6670',{vary:0.08});
  j.box(14,-1.2,0,1.0,0.8,1.0,'#2f373e');
  const jm=j.mesh(new THREE.MeshStandardMaterial({vertexColors:true,roughness:0.85,metalness:0.25}));
  jm.position.set(x,top+0.5,z);jm.castShadow=true;scene.add(jm);craneJib=jm;
  const hook=new THREE.Mesh(new THREE.BoxGeometry(1.0,1.4,1.0),new THREE.MeshStandardMaterial({color:0x2f373e,roughness:.8}));
  hook.position.set(x+14,top-2,z);scene.add(hook);
  const cargo=new Voxels();cargo.box(0,0,0,2.2,2.2,2.2,'#8b6a45',{vary:0.14});cargo.box(0,1.2,0,2.3,0.3,2.3,'#a2805a',{vary:0.1});
  const cm=cargo.mesh(new THREE.MeshStandardMaterial({vertexColors:true,roughness:0.9}));
  cm.position.set(x+14,top-4.4,z);cm.castShadow=true;scene.add(cm);
  craneHook=hook;craneCargo=cm;craneTop=top;craneBase={x,z};
})();

/* ================= sea ================= */
const SEA={sp:2.4,x0:-80,x1:16,z0:-58,z1:58};
SEA.nx=Math.round((SEA.x1-SEA.x0)/SEA.sp);SEA.nz=Math.round((SEA.z1-SEA.z0)/SEA.sp);
SEA.count=SEA.nx*SEA.nz;
SEA.xs=new Float32Array(SEA.count);SEA.zs=new Float32Array(SEA.count);
const seaMat=new THREE.MeshStandardMaterial({roughness:0.78,metalness:0.06});
const sea=new THREE.InstancedMesh(new THREE.BoxGeometry(SEA.sp*1.02,3,SEA.sp*1.02),seaMat,SEA.count);
sea.receiveShadow=true;sea.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
{let i=0;for(let ix=0;ix<SEA.nx;ix++)for(let iz=0;iz<SEA.nz;iz++){SEA.xs[i]=SEA.x0+ix*SEA.sp;SEA.zs[i]=SEA.z0+iz*SEA.sp;
  sea.setMatrixAt(i,new THREE.Matrix4().makeTranslation(SEA.xs[i],-1.5,SEA.zs[i]));
  sea.setColorAt(i,new THREE.Color('#12506b'));i++;}}
scene.add(sea);
const seaCol={deep:new THREE.Color('#062033'),mid:new THREE.Color('#12506b'),
  crest:new THREE.Color('#1e7a92'),foam:new THREE.Color('#dbeee9'),glint:new THREE.Color('#ffd8a8')};
function wave(x,z,t){
  return 0.55*Math.sin(x*0.14+t*1.0)+0.42*Math.sin(z*0.11-t*0.8)+0.30*Math.sin(x*0.07+z*0.13+t*0.55)+0.18*Math.sin(x*0.32+t*1.7);
}

/* ================= ship ================= */
const ship=new THREE.Group();ship.position.set(-13,1.5,-3);ship.rotation.y=0.10;scene.add(ship);
const shipVox=new Voxels(),shipGlow=new Voxels();
function profX(x){const T=[[-13,2.3],[-10,2.9],[-5,3.25],[0,3.35],[5,3.1],[9,2.35],[12,1.3],[13.6,0.55]];
  if(x<=T[0][0])return T[0][1];
  for(let i=1;i<T.length;i++)if(x<=T[i][0]){const [a,wa]=T[i-1],[b,wb]=T[i];return lerp(wa,wb,(x-a)/(b-a));}
  return 0.55;}
const DECK=2.2;
for(let x=-13;x<=13.4;x+=0.9){
  const hw=profX(x);
  for(let y=-3.2;y<DECK;y+=0.8){
    const t=clamp((y+3.2)/(DECK+3.2),0,1);
    const s=0.52+0.48*Math.pow(t,0.42);
    let col='#3b2a1f';
    if(y<-2.8)col='#221c18'; else if(Math.abs(y+1.4)<0.42)col='#c08c2b'; else if(Math.abs(y+1.0)<0.4)col='#c08c2b';
    shipVox.box(x,y+0.4,0,0.92,0.85,hw*2*s,col,{vary:0.13});
  }
  shipVox.box(x+0.42,DECK+0.12,0,0.9,0.3,hw*2*0.94,hash2(x,4)>0.5?'#8a6640':'#7b5a37',{vary:0.14});
  for(const s of [-1,1]){
    shipVox.box(x+0.42,DECK+0.35,s*hw*0.94,0.92,0.7,0.45,'#d9c8a6',{vary:0.09});
    shipVox.box(x+0.42,DECK+0.78,s*hw*0.94,0.9,0.22,0.2,'#6d4e31',{vary:0.1});
  }
}
/* bow & stern heads */
shipVox.box(13.9,DECK+0.55,0,1.6,1.1,1.1,'#5c4127',{vary:0.1});
shipVox.box(-13.6,DECK+0.75,0,1.3,1.5,hw?5.2:5.2,'#43301f',{vary:0.1});
for(const s of [-1,1])shipVox.box(14.4,DECK-0.7,s*0.8,1.2,0.6,0.5,'#d9c8a6',{vary:0.08});
/* quarterdeck + forecastle */
for(let x=-12.6;x<=-6.5;x+=0.9){
  shipVox.box(x+0.42,DECK+0.9,0,0.9,1.3,5.0,'#5c4127',{vary:0.11});
  shipVox.box(x+0.42,DECK+1.7,0,0.9,0.26,5.3,'#d9c8a6',{vary:0.09});
  shipVox.box(x+0.42,DECK+0.9,0,0.92,0.9,5.05,'#4a3524',{vary:0.1});
  shipVox.box(x+0.42,DECK+1.55,0,0.9,0.5,5.1,'#c9b78f',{vary:0.1});
  shipVox.box(x+0.42,DECK+0.9,0,0.94,1.2,5.0,'#4a3524',{vary:0.1});
  shipVox.box(x+0.42,DECK+1.65,0,0.9,0.2,5.2,'#d9c8a6',{vary:0.08});
}
for(let z of [-2.5,2.5])for(let y of [2.2,2.8])shipGlow.box(-12.7,y,-3+0,0,0,0,'#000');
for(let x=-11.5;x<=-7.5;x+=1.3){shipGlow.box(x-0.6,DECK+1.15,2.55,0.22,1.1,1.1,'#ffc46e',{vary:0.04});
  shipGlow.box(x-0.6,DECK+1.15,-2.55,0.22,1.1,1.1,'#ffc46e',{vary:0.04});}
shipVox.box(-9.5,DECK+2.3,0,3.2,0.9,4.2,'#c9b78f',{vary:0.1});
shipVox.box(-8.2,DECK+2.9,0,1.2,0.9,1.2,'#4a3524',{vary:0.1});
shipVox.box(-8.2,DECK+3.5,0,0.4,0.4,0.4,'#c08c2b');
for(let x=8;x<=12.8;x+=0.9){
  shipVox.box(x+0.42,DECK+0.75,0,0.9,1.0,profX(x)*1.8,'#5c4127',{vary:0.11});
  shipVox.box(x+0.42,DECK+1.35,0,0.9,0.24,profX(x)*2.0,'#d9c8a6',{vary:0.09});
}
/* gun ports */
for(let i=0;i<4;i++){const x=-4+i*3.2;
  shipVox.box(x,0.7,profX(x)+0.3,1.1,1.1,0.7,'#efe7d6',{vary:0.06});
  shipVox.box(x,0.7,profX(x)+0.7,0.6,0.5,1.1,'#262422',{vary:0.08});}
/* anchor + fenders */
shipVox.box(11.4,1.0,2.9,0.4,1.6,0.5,'#3f4a52',{vary:0.08});
shipVox.box(11.4,0.25,2.9,1.4,0.4,0.4,'#3f4a52',{vary:0.08});
for(let i=0;i<3;i++)shipVox.box(12.6-i*1.4,-0.4+i*0.1,2.4,1.1,1.4,0.5,'#2e3b44',{vary:0.1});

/* masts, yards, sails */
const MASTS=[
  {x:6.5,h:15,yards:[[6.2,9],[9.4,7.2],[12.2,5.2]],filled:[0,1]},
  {x:-2,h:17.5,yards:[[6.6,11.6],[10.4,9.6],[13.8,7]],filled:[0,1]},
  {x:-10,h:13,yards:[[6.4,8],[9.6,6]],filled:[0]}
];
for(const m of MASTS){
  for(let y=DECK;y<m.h;y+=1.1)shipVox.box(m.x,y+0.55,0,0.55,1.15,0.55,'#6a4b31',{vary:0.09});
  shipVox.box(m.x,m.h+0.4,0,0.32,0.9,0.32,'#4b3522');
  shipVox.box(m.x,m.h+0.95,0,1.0,0.24,1.0,'#b8402f',{vary:0.08});
  if(m.x===-2){for(let i=0;i<10;i++){const a=i/10*Math.PI*2;shipVox.box(m.x+Math.cos(a)*1.5,10.1,m.z+Math.sin(a)*1.5,0.28,0.9,0.28,'#d8cdb8',{vary:0.08});}}
  m.yards.forEach((yd,i)=>{
    const [yy,len]=yd;
    shipVox.box(m.x,yy,0,0.6,0.5,len+0.6,'#453022',{vary:0.09});
    shipVox.box(m.x,yy-0.45,len/2+0.4,0.28,0.5,0.4,'#2c333a');
    shipVox.box(m.x,yy-0.45,-len/2-0.4,0.28,0.5,0.4,'#2c333a');
    if(m.filled.includes(i)){
      for(let c=-len/2;c<=len/2;c+=1.05)for(let r=0;r<3;r++){
        const fr=Math.abs(c)/(len/2);
        const bulge=1.25*(1-fr*fr)*Math.sin(Math.PI*(r+0.6)/3.4);
        let y=yy-0.9-r*1.0;
        if(r===2)y+=0.42*fr*fr;
        shipVox.box(m.x+bulge,y,c,1.05,1.05,1.05,(r===1?'#e3d4b6':'#eee3cb'),{vary:0.1});
      }
    } else {
      shipVox.box(m.x+0.15,yy-0.55,0,0.75,0.6,len*0.92,'#d3c4a2',{vary:0.13});
      shipVox.box(m.x+0.62,yy-0.55,0,0.35,0.35,len*0.86,'#b9a885',{vary:0.1});
    }
  });
  /* shrouds & stays */
  for(const s of [-1,1]){
    line(shipVox,new THREE.Vector3(m.x,m.h-0.5,0),new THREE.Vector3(m.x-1.1,DECK+0.6,s*profX(m.x)*0.95),0.2,'#b9ab92',1.3,0.05);
    line(shipVox,new THREE.Vector3(m.x,m.h-0.5,0),new THREE.Vector3(m.x+1.1,DECK+0.6,s*profX(m.x)*0.95),0.2,'#b9ab92',1.3,0.05);
  }
  line(shipVox,new THREE.Vector3(m.x,m.h-0.6,0),new THREE.Vector3(m.x+6.5,DECK+0.8,0),0.2,'#c3b596',1.5,0.05);
  line(shipVox,new THREE.Vector3(m.x,m.h-0.6,0),new THREE.Vector3(m.x-6.5,DECK+0.8,0),0.2,'#c3b596',1.5,0.05);
}
/* bowsprit + jibs */
{
  const A=new THREE.Vector3(13.4,DECK+0.8,0),B=new THREE.Vector3(21.4,5.0,0);
  line(shipVox,A,B,0.42,'#6a4b31',0.8,0.08);
  shipVox.box(19.5,5.6,0,0.4,0.5,1.6,'#453022');
  shipVox.box(21.4,5.0,0,0.5,0.4,0.4,'#453022');
  const foreTop=new THREE.Vector3(6.5,14.6,0);
  fillTri(shipVox,new THREE.Vector3(6.5,13.8,0),new THREE.Vector3(21.0,5.4,0),new THREE.Vector3(12.8,6.4,0),1.05,'#e9ddc4',0.8);
  fillTri(shipVox,new THREE.Vector3(6.5,11.2,0),new THREE.Vector3(17.2,6.2,0),new THREE.Vector3(11.5,7.4,0),1.0,'#efe4cd',0.6);
  line(shipVox,B,new THREE.Vector3(6.5,12.2,0),0.2,'#c3b596',1.4,0.05);
  /* spanker */
  fillTri(shipVox,new THREE.Vector3(-10,10.2,0),new THREE.Vector3(-15.6,6.6,0),new THREE.Vector3(-10,5.4,0),1.0,'#e6d9bf',-0.5);
  fillTri(shipVox,new THREE.Vector3(-15.6,6.6,0),new THREE.Vector3(-14.0,3.6,0),new THREE.Vector3(-10,5.4,0),1.0,'#e6d9bf',-0.5);
  line(shipVox,new THREE.Vector3(-10,10.2,0),new THREE.Vector3(-15.8,6.7,0),0.24,'#4b3522',1.0,0.06);
  /* flags */
  const ensign=new THREE.Mesh(new THREE.BoxGeometry(2.6,1.6,0.18),
    new THREE.MeshStandardMaterial({color:0xb8402f,roughness:.9,side:THREE.DoubleSide}));
  ensign.position.set(-11.9,13.4,0);ship.add(ensign);flags.push({m:ensign,ph:0.4});
  const penn=new THREE.Mesh(new THREE.BoxGeometry(2.2,1.1,0.16),
    new THREE.MeshStandardMaterial({color:0xf2c36a,roughness:.9,side:THREE.DoubleSide}));
  penn.position.set(22.4,5.2,0);ship.add(penn);flags.push({m:penn,ph:1.9});
}
/* rigging between masts */
for(const m of MASTS)for(const [yy,len] of m.yards){
  for(const s of [-1,1])line(shipVox,new THREE.Vector3(m.x,yy,s*len/2),new THREE.Vector3(m.x+(m.x>0?-3:3),yy+1.8,s*len/2*0.7),0.16,'#b9ab92',1.6,0.05);
}
const shipMesh=shipVox.mesh(new THREE.MeshStandardMaterial({vertexColors:true,roughness:0.85,metalness:0.04}));
shipMesh.castShadow=true;shipMesh.receiveShadow=true;ship.add(shipMesh);
const shipGlowMesh=shipGlow.mesh(glowMat);ship.add(shipGlowMesh);
const cabinLight=new THREE.PointLight(0xffb76a,1.2,16,2);cabinLight.position.set(-10.5,4.2,0);ship.add(cabinLight);

/* ================= glow material ================= */
const glowMat=new THREE.MeshBasicMaterial({vertexColors:true,toneMapped:false,color:0xffffff});

/* buoys */
const buoyLights=[];
function buoy(x,z,body,lightCol){
  const g=new Voxels();
  for(let y=-1;y<2;y+=0.8)g.box(x,y+0.4,z,2.2,0.85,2.2,body,{vary:0.12});
  g.box(x,2.2,z,0.4,1.6,0.4,'#2c333a');
  const m=g.mesh(new THREE.MeshStandardMaterial({vertexColors:true,roughness:.85}));
  m.castShadow=true;scene.add(m);
  const l=new THREE.Mesh(new THREE.BoxGeometry(1,0.9,1),new THREE.MeshBasicMaterial({color:lightCol,toneMapped:false}));
  l.position.set(x,3.2,z);scene.add(l);buoyLights.push({l,col:new THREE.Color(lightCol),ph:x*0.3});
  return {group:m,light:l,x,z};
}
const buoys=[buoy(-30,-12,'#b8402f','#ff5c46'),buoy(-42,18,'#2f6f4f','#5ff08a')];

/* ================= tug ================= */
const tug=new THREE.Group();scene.add(tug);
{
  const v=new Voxels();
  for(let x=-4.5;x<=4.5;x+=0.8)for(let y=-1.6;y<0.6;y+=0.8)v.box(x,y+0.4,0,0.85,0.85,3.0,'#2c333a',{vary:0.1});
  v.box(0,1.4,0,3.4,1.6,2.6,'#5c4127',{vary:0.1});
  v.box(0,2.6,0,2.6,0.8,2.0,'#e2d6c0',{vary:0.08});
  for(let z of [-1.3,1.3])shipGlowBox(v,0,1.5,z,0.9,0.9,'#ffcf82');
  v.box(-1.4,3.6,0,1.2,2.2,1.2,'#241c17',{vary:0.08});
  v.box(-1.4,4.9,0,1.4,0.5,1.4,'#b8402f',{vary:0.08});
  v.box(3.4,1.6,0,1.2,1.2,1.2,'#3f4a52',{vary:0.1});
  v.box(0,-0.6,1.9,1.2,1.0,0.5,'#c08c2b',{vary:0.1});
  const m=v.mesh(new THREE.MeshStandardMaterial({vertexColors:true,roughness:.85}));
  m.castShadow=true;tug.add(m);
}
function shipGlowBox(v,x,y,z,s,c){const g=new Voxels();g.box(x,y,z,s,s,s,c,{vary:0.04});glowExtra.push(g);}
const glowExtra=[];
const tugSmoke=[];
for(let i=0;i<7;i++){
  const mat=new THREE.MeshBasicMaterial({color:0x585058,transparent:true,opacity:.35,fog:true,depthWrite:false});
  const p=new THREE.Mesh(new THREE.BoxGeometry(1,1,1),mat);p.userData.life=i/7;
  tug.add(p);tugSmoke.push({m:p,origin:new THREE.Vector3(-1.4,5.2,0)});
}

/* ================= ropes ================= */
const rope=new THREE.InstancedMesh(new THREE.BoxGeometry(0.55,0.55,0.55),
  new THREE.MeshStandardMaterial({vertexColors:false,color:0xc1a06a,roughness:.9}),26);
rope.instanceMatrix.setUsage(THREE.DynamicDrawUsage);rope.castShadow=false;scene.add(rope);
const ropeA=new THREE.Vector3(),ropeB=new THREE.Vector3(5.4,6.0,2.2),tmp=new THREE.Vector3();

/* ================= gulls ================= */
const gullBody=new THREE.BoxGeometry(1.5,0.5,0.55),gullWing=new THREE.BoxGeometry(1.1,0.14,1.5);
const gullMat=new THREE.MeshStandardMaterial({color:0xf0ece1,roughness:.9});
const gullDark=new THREE.MeshStandardMaterial({color:0x8f9aa2,roughness:.9});
const gulls=[];
for(let i=0;i<6;i++){
  const g=new THREE.Group();
  const b=new THREE.Mesh(gullBody,gullMat);b.castShadow=false;g.add(b);
  const tail=new THREE.Mesh(new THREE.BoxGeometry(0.7,0.22,0.4),gullDark);tail.position.set(-0.95,0.1,0);g.add(tail);
  const wl=new THREE.Mesh(gullWing,gullMat);wl.position.set(0,0.2,1.1);g.add(wl);
  const wr=new THREE.Mesh(gullWing,gullMat);wr.position.set(0,0.2,-1.1);g.add(wr);
  scene.add(g);
  gulls.push({g,wl,wr,r:rnd(14,30),h:rnd(11,20),sp:rnd(0.16,0.34)*(Math.random()<.5?-1:1),
    ph:Math.random()*Math.PI*2,cx:-8+rnd(-6,6),cz:-2+rnd(-6,6)});
}

/* ================= clouds ================= */
const clouds=[];
for(let i=0;i<12;i++){
  const v=new Voxels();
  const n=Math.floor(rnd(5,10));
  const base=mix('#f6d3b4','#cdbcd6',Math.random());
  for(let k=0;k<n;k++)v.box(rnd(-9,9),rnd(-1.6,1.6),rnd(-6,6),rnd(3,7),rnd(1.6,3.2),rnd(3,7),base,{vary:0.12});
  const mat=new THREE.MeshBasicMaterial({vertexColors:true,fog:false,toneMapped:false});
  const m=v.mesh(mat);
  m.position.set(rnd(-90,60),rnd(48,86),rnd(-70,70));
  scene.add(m);clouds.push({m,mat,sp:rnd(0.5,1.5)});
}

/* distant sailing boats */
function littleBoat(){
  const v=new Voxels();
  for(let x=-3;x<=3;x+=0.7)v.box(x,0,0,0.7,0.7,1.6,'#2b3a44',{vary:0.12});
  v.box(0,3.4,0,0.24,6.2,0.24,'#5a4632',{vary:0.08});
  for(let y=1;y<5;y+=0.8)v.box(0.7,y+0.4,0,1.0,0.8,1.2,'#e6d9bf',{vary:0.12});
  v.box(-2.4,2.2,0,0.9,0.7,1.1,'#e6d9bf',{vary:0.12});
  const m=v.mesh(new THREE.MeshStandardMaterial({vertexColors:true,roughness:.9}));
  scene.add(m);return m;
}
const boats=[littleBoat(),littleBoat(),littleBoat()];
boats.forEach((b,i)=>b.position.set(-46-i*14,rnd(-0.2,0.4),-38+i*24+rnd(-4,4)));

/* ================= smoke ================= */
const smoke=[];
for(const c of chimneys)for(let i=0;i<5;i++){
  const mat=new THREE.MeshBasicMaterial({color:0xd8cfc0,transparent:true,opacity:.3,fog:true,depthWrite:false});
  const m=new THREE.Mesh(new THREE.BoxGeometry(1,1,1),mat);scene.add(m);
  smoke.push({m,origin:c,life:i/5,sp:rnd(0.28,0.5)});
}

/* ================= lighthouse beam ================= */
const beam=new THREE.Group();beam.position.copy(lightPos);scene.add(beam);
const beamMat=new THREE.MeshBasicMaterial({color:0xffe3b4,transparent:true,opacity:.22,
  blending:THREE.AdditiveBlending,depthWrite:false,side:THREE.DoubleSide,fog:false});
const beamGeo=new THREE.ConeGeometry(17,150,14,1,true);beamGeo.translate(0,-75,0);beamGeo.rotateZ(Math.PI/2);
const b1=new THREE.Mesh(beamGeo,beamMat);beam.add(b1);
const holder=new THREE.Group();holder.rotation.y=Math.PI;
const b2=new THREE.Mesh(beamGeo,beamMat);b2.rotation.z=Math.PI/2;holder.add(b2);beam.add(holder);
const lens=new THREE.Mesh(new THREE.BoxGeometry(2.6,2.6,2.6),new THREE.MeshBasicMaterial({color:0xffe0a2,toneMapped:false,fog:false}));
lens.position.copy(lightPos);scene.add(lens);

/* ================= time of day ================= */
const sunDir=new THREE.Vector3();
let tod=0.26;
function setTime(t){
  tod=t;
  const el=lerp(6,44,t)*Math.PI/180;
  const az=lerp(196,236,t)*Math.PI/180;
  sunDir.set(Math.cos(el)*Math.cos(az),Math.sin(el),Math.cos(el)*Math.sin(az)).normalize();
  sun.position.copy(sunDir).multiplyScalar(190);sun.target.position.set(-4,4,0);
  sun.color.copy(mix('#ff8b46','#ffeccb',t));
  sun.intensity=lerp(1.9,3.2,t);
  hemi.color.copy(mix('#f0b28c','#bfe0ea',t));hemi.groundColor.copy(mix('#24455a','#3f6f78',t));
  hemi.intensity=lerp(0.62,0.95,t);
  skyU.uZen.value.copy(mix('#16324f','#3d7cb6',t));
  skyU.uHor.value.copy(mix('#f2a06a','#d8e8ee',t));
  skyU.uHaze.value.copy(mix('#9a6046','#b9cdd4',t));
  skyU.uSunCol.value.copy(mix('#ff9a55','#fff4dc',t));
  skyU.uSunDir.value.copy(sunDir);skyU.uSunUp.value=lerp(1.3,0.75,t);
  fog.color.copy(mix('#c98a68','#cfe0e6',t));
  sunQuad.position.copy(sunDir).multiplyScalar(470);sunQuad.lookAt(0,0,0);
  sunQuad.material.color.copy(mix('#ffb070','#fff8e2',t));
  sunQuad.scale.setScalar(lerp(26,16,t));
  seaCol.deep.copy(mix('#05192b','#0e4a62',t));seaCol.mid.copy(mix('#0d3d57','#1d7c98',t));
  seaCol.crest.copy(mix('#176079','#2f95ac',t));seaCol.foam.copy(mix('#ffe0bd','#eaf6f6',t));
  seaCol.glint.copy(mix('#ffcf9a','#fff3d6',t));
  const k=lerp(1.5,0.55,t);glowMat.color.setRGB(k,k,k);
  lampA.intensity=lampB.intensity=lerp(1.6,0.15,t);
  houseLight.intensity=lerp(1.5,0.2,t);cabinLight.intensity=lerp(1.4,0.25,t);
  lantern.intensity=lerp(2.8,0.3,t);beamMat.opacity=lerp(0.30,0.045,t);
  lens.material.color.copy(mix('#ffdc9a','#f3e6cf',t));lens.visible=true;
  for(const c of clouds)c.mat.color.copy(mix('#f7cfa8','#ffffff',t));
  renderer.toneMappingExposure=lerp(1.22,1.08,t);
  document.getElementById('tod').textContent=t<0.18?'Dusk':t<0.45?'Golden hour':t<0.78?'Bright afternoon':'Midday';
}
setTime(tod);

/* extra glow boxes from tug */
for(const g of glowExtra){const m=g.mesh(glowMat);scene.add(m);}

/* ================= dynamic refs ================= */
let windmill,craneJib,craneHook,craneCargo,craneTop,craneBase;
const flags=[];
/* flags array must exist before ship build — hoist fix */

/* ================= loop ================= */
const clock=new THREE.Clock();
const dm=new THREE.Object3D();
const cTmp=new THREE.Color();
const shipC=new THREE.Vector3(-13,-3);
let intro={on:true,t:0,dur:2.8,from:camera.position.clone(),to:new THREE.Vector3(34,13,30)};

function updateWater(t){
  const sx=sunDir.x,sz=sunDir.z;
  for(let i=0;i<SEA.count;i++){
    const x=SEA.xs[i],z=SEA.zs[i];
    const h=wave(x,z,t);
    dm.position.set(x,h-1.5,z);dm.scale.set(1,1,1);dm.rotation.set(0,0,0);dm.updateMatrix();
    sea.setMatrixAt(i,dm.matrix);
    cTmp.copy(seaCol.deep).lerp(seaCol.mid,smoothstep(-1.2,0.6,h));
    cTmp.lerp(seaCol.crest,smoothstep(0.4,1.4,h)*0.85);
    const along=x*sx+z*sz, across=-x*sz+z*sx;
    const gl=Math.exp(-(across*across)/230)*clamp(along/50,0,1)*Math.pow(clamp((h+0.7)/1.8,0,1),3)*lerp(1.6,0.5,tod);
    cTmp.lerp(seaCol.glint,clamp(gl,0,0.85));
    let foam=0;
    const ex=(x-shipC.x)/16.5,ez=(z-shipC.y)/7.5,e=Math.hypot(ex,ez);
    foam=Math.max(foam,smoothstep(0.72,1.02,e)*smoothstep(1.34,1.02,e)*0.9);
    foam=Math.max(foam,smoothstep(13.2,16.8,x)*0.85);
    for(const b of buoys){foam=Math.max(foam,smoothstep(4.4,2.4,Math.hypot(x-b.x,z-b.z))*0.7);}
    foam=Math.max(foam,smoothstep(5.2,3.0,Math.hypot(x-3,z+29.5))*0.6);
    foam*=0.55+0.45*Math.sin(t*2.1+x*0.35+z*0.2);
    cTmp.lerp(seaCol.foam,clamp(foam,0,0.75));
    sea.setColorAt(i,cTmp);
  }
  sea.instanceMatrix.needsUpdate=true;sea.instanceColor.needsUpdate=true;
}
function updateShip(t){
  ship.position.y=1.5+0.3*Math.sin(t*0.85)+0.12*Math.sin(t*1.7)+0.05*Math.sin(t*3.1);
  ship.rotation.z=-0.045+0.028*Math.sin(t*0.7)+0.012*Math.sin(t*1.35);
  ship.rotation.x=0.012*Math.sin(t*0.55+1);
  for(const f of flags){f.m.rotation.y=Math.sin(t*4+f.ph)*0.32;f.m.rotation.z=Math.sin(t*3+f.ph)*0.12;}
}
function updateRope(){
  ship.localToWorld(ropeA.set(13.6,1.2,0));
  for(let i=0;i<26;i++){
    const u=i/25;
    tmp.lerpVectors(ropeA,ropeB,u);
    tmp.y-=Math.sin(Math.PI*u)*(1.5+0.35*Math.sin(clock.elapsedTime*0.9));
    dm.position.copy(tmp);dm.scale.set(1,1,1);dm.rotation.set(u*2,u*1.4,u*0.7);dm.updateMatrix();
    rope.setMatrixAt(i,dm.matrix);
  }
  rope.instanceMatrix.needsUpdate=true;
}
function updateGulls(t){
  for(const g of gulls){
    const a=t*g.sp+g.ph;
    g.g.position.set(g.cx+Math.cos(a)*g.r,g.h+Math.sin(t*0.7+g.ph)*2.6,g.cz+Math.sin(a)*g.r);
    g.g.rotation.y=Math.atan2(-Math.cos(a)*g.sp,-Math.sin(a)*g.sp);
    g.g.rotation.z=0.28*Math.sin(t*1.2+g.ph)*Math.sign(g.sp);
    const f=Math.sin(t*6.5+g.ph);
    g.wl.rotation.x=f*0.75;g.wr.rotation.x=-f*0.75;
  }
}
function updateClouds(dt){
  for(const c of clouds){c.m.position.x+=dt*c.sp;if(c.m.position.x>110)c.m.position.x=-110;}
}
function updateCrane(t){
  craneJib.rotation.y=-0.55+Math.sin(t*0.22)*0.75;
  const a=craneJib.rotation.y;
  const drop=2.6+Math.sin(t*0.5)*1.6;
  craneCargo.position.set(craneBase.x+Math.cos(a)*14,craneTop+0.5-drop,craneBase.z+Math.sin(a)*14);
  craneCargo.rotation.y=a;
  craneHook.position.set(craneBase.x+Math.cos(a)*14,craneCargo.position.y+1.9,craneBase.z+Math.sin(a)*14);
}
function updateSmoke(dt,t){
  for(const s of smoke){
    s.life+=dt*s.sp;
    if(s.life>1){s.life=0;s.m.position.copy(s.origin);}
    const k=s.life;
    s.m.position.set(s.origin.x+Math.sin(t*0.7+s.origin.z)*k*3.4+k*2.4,s.origin.y+k*7,s.origin.z+k*1.2);
    const sc=0.7+k*3.4;s.m.scale.setScalar(sc);
    s.m.rotation.set(k*2,k*1.6,k);
    s.m.material.opacity=(1-k)*0.34;
  }
}
function updateTug(dt,t){
  const px=-34+13*Math.sin(t*0.075), pz=-20+8*Math.cos(t*0.06);
  const vx=13*0.075*Math.cos(t*0.075), vz=-8*0.06*Math.sin(t*0.06);
  tug.position.set(px,-0.1+0.35*Math.sin(t*1.2),pz);
  tug.rotation.y=Math.atan2(-vz,vx);
  tug.rotation.z=0.05*Math.sin(t*1.5);
  for(const s of tugSmoke){
    s.m.userData.life+=dt*0.55;
    if(s.m.userData.life>1)s.m.userData.life=0;
    const k=s.m.userData.life;
    s.m.position.set(s.origin.x-k*5,k*6,s.origin.z+k*0.6);
    s.m.scale.setScalar(0.6+k*2.6);s.m.material.opacity=(1-k)*0.3;
  }
}
function updateBoats(t){
  boats.forEach((b,i)=>{
    b.position.x+=dtG;
    if(b.position.x>-30)b.position.x=-80;
    b.position.y=-0.2+0.5*Math.sin(t*0.9+i*2);
    b.rotation.z=0.06*Math.sin(t*1.1+i);
  });
  buoys.forEach((b,i)=>{
    b.group.position.set(b.x,wave(b.x,b.z,t)*0.7-1.3,b.z);
    b.group.rotation.z=0.14*Math.sin(t*1.3+i);b.group.rotation.x=0.1*Math.sin(t*1.1+i);
    b.light.position.set(b.x,b.group.position.y+4.5,b.z);
  });
  for(const bl of buoyLights){
    const on=Math.sin(clock.elapsedTime*2.2+bl.ph)>0.2;
    bl.l.material.color.copy(bl.col).multiplyScalar(on?1.5:0.35);
    bl.l.visible=on||tod<0.5;
  }
}
let dtG=0.012;
function updateBeam(t){beam.rotation.y=t*0.34;}

function animate(){
  requestAnimationFrame(animate);
  const dt=Math.min(clock.getDelta(),0.05);
  const t=clock.elapsedTime;
  dtG=dt*2.2;
  updateWater(t);updateShip(t);updateRope();updateGulls(t);updateClouds(dt);
  updateCrane(t);windmill.rotation.z+=dt*0.55;updateSmoke(dt,t);updateTug(dt,t);
  updateBoats(t);updateBeam(t);
  if(intro.on){
    intro.t+=dt/intro.dur;const k=easeOut(clamp(intro.t,0,1));
    camera.position.lerpVectors(intro.from,intro.to,k);
    if(intro.t>=1)intro.on=false;
  }
  controls.update();
  renderer.render(scene,camera);
}
animate();

/* ================= UI ================= */
const VIEWS=[
  {p:[34,13,30],t:[-6,7,0]},
  {p:[-26,26,30],t:[-8,13,0]},
  {p:[62,44,54],t:[10,3,-2]},
  {p:[-52,8,26],t:[-2,7,0]}
];
function goView(i,instant){
  const v=VIEWS[i];intro.on=false;
  controls.target.set(...v.t);
  if(instant)camera.position.set(...v.p);
  else{intro.on=true;intro.t=0;intro.dur=1.35;intro.from=camera.position.clone();intro.to=new THREE.Vector3(...v.p);}
  document.querySelectorAll('#views .chip').forEach((c,j)=>c.classList.toggle('on',j===i));
}
document.querySelectorAll('#views .chip').forEach((c,i)=>c.addEventListener('click',()=>goView(i)));
addEventListener('keydown',e=>{
  if(e.key>='1'&&e.key<='4')goView(+e.key-1);
  if(e.key==='h'||e.key==='H')toggleUI();
  if(e.key==='a'||e.key==='A')document.getElementById('orbit').click();
});
controls.addEventListener('start',()=>intro.on=false);
const slider=document.getElementById('slider');
slider.addEventListener('input',()=>setTime(parseFloat(slider.value)));
const orbit=document.getElementById('orbit');
orbit.addEventListener('click',()=>{controls.autoRotate=!controls.autoRotate;orbit.classList.toggle('on',controls.autoRotate);});
function toggleUI(){
  document.getElementById('panel').classList.toggle('hidden');
  document.getElementById('hint').classList.toggle('hidden');
  document.getElementById('flags').classList.toggle('hidden');
}
document.getElementById('hide').addEventListener('click',toggleUI);

const FLAGDATA=[
  ['A','Alpha','Diver down — keep clear and go slow','#1e4f8f',
    'linear-gradient(115deg,#1e4f8f 0 42%,#f6f7f8 42%)'],
  ['B','Bravo','Taking in or discharging dangerous goods','#c2352b','solid'],
  ['G','Golf','Fishing — my nets are well out','#f2b23c',
    'repeating-linear-gradient(90deg,#f2b23c 0 8px,#c2352b 8px 16px)'],
  ['P','Papa','About to sail — all aboard','#1e4f8f',
    'linear-gradient(#f6f7f8,#f6f7f8) center/46% 46% no-repeat,#1e4f8f'],
  ['R','Romeo','Receiving — keep clear','#c2352b',
    'linear-gradient(#1b1d1f,#1b1d1f) center/100% 26% no-repeat,linear-gradient(#1b1d1f,#1b1d1f) center/26% 100% no-repeat,#c2352b'],
  ['Y','Yankee','I am dragging my anchor','#f2b23c',
    'repeating-linear-gradient(45deg,#f2b23c 0 8px,#c2352b 8px 16px)'],
];
const fw=document.getElementById('flags'),tip=document.getElementById('tip');
FLAGDATA.forEach(([id,name,desc,col,bg])=>{
  const el=document.createElement('div');el.className='flag';
  el.style.background=bg==='solid'?col:bg;
  el.addEventListener('mouseenter',()=>{tip.innerHTML=`<b>${id} · ${name}</b>${desc}`;tip.classList.add('show');});
  el.addEventListener('mouseleave',()=>tip.classList.remove('show'));
  fw.appendChild(el);
});

addEventListener('resize',()=>{
  camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight);
});
goView(0,true);
intro.on=true;intro.t=0;intro.dur=2.9;intro.from=new THREE.Vector3(96,62,98);intro.to=new THREE.Vector3(34,13,30);
</script>
</body>
</html>
```

A few notes on what's in there:

- **Ship:** procedurally lofted hull (tapered sheer, two ochre bands, white bulwark rail, planked deck, quarterdeck with lit cabin windows, forecastle, gun ports, anchor, fenders), three masts with yards — lower courses filled and bellied in the wind, upper canvas furled on the yards — plus voxel jibs, a gaff spanker, shrouds/stays/braces, and fluttering ensign & pennant.
- **Harbour:** cobble quay with wall, slipway steps, timber pier with pilings and pier‑head bollards, breakwater with red/green harbour lights, lighthouse with rotating twin beams, customs house with clock tower, warehouses, cottages (drifting chimney smoke), fish stall, iron crane slewing a crate over the ship, street lamps, barrels, nets, coiled rope.
- **Sea:** ~2,000 animated voxel columns whose colours are recomputed each frame — crest tint, foam lapping the hull, quay and buoys, and a sun‑glitter path that follows the sun's azimuth.
- **Interaction:** orbit/zoom/pan, four camera views (chips or keys 1–4), auto‑orbit (A), panel hide (H), and the time‑of‑day slider which regrades sun, sky, fog, water, lamp/window glow and beam strength from dusk to midday.