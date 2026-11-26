# Calling at the Harbor

A fully procedural voxel diorama — a 46‑voxel‑long frigate gliding in under short canvas, a stone harbor, a working lighthouse, a windmill, a quay alive with cargo, lamp‑glow and gulls. It builds itself at load time (no downloads beyond Three.js), rocks on a stepped shader sea, and everything reacts to the sun slider.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Calling at the Harbor — 3D voxel scene</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root{ --ink:#1b2a32; --paper:#f5efe3; --copper:#b06a3d; --rule:rgba(27,42,50,.28); }
*{box-sizing:border-box}
html,body{margin:0;height:100%;overflow:hidden;background:#0a1219}
body{font-family:Georgia,"Iowan Old Style","Times New Roman",serif;color:var(--ink)}
canvas{display:block}
#ui{position:fixed;left:22px;bottom:22px;width:286px;padding:16px 18px;
  background:linear-gradient(180deg,rgba(245,239,227,.94),rgba(236,226,207,.92));
  border:1px solid var(--rule);border-left:3px solid var(--copper);
  box-shadow:0 18px 44px rgba(6,14,20,.45);backdrop-filter:blur(8px) saturate(1.1);
  transition:opacity .35s ease,transform .35s ease;user-select:none;z-index:10}
#ui.hidden{opacity:0;transform:translateY(10px);pointer-events:none}
#kicker{font:600 10px/1.2 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;letter-spacing:.24em;color:var(--copper);text-transform:uppercase}
#ttl{font-size:27px;line-height:1.02;margin:.4em 0 .15em;font-variant:small-caps;letter-spacing:.015em}
#ttl small{font-size:13px;font-variant:normal;letter-spacing:0;color:rgba(27,42,50,.55);font-style:italic}
#sub{font-size:12px;font-style:italic;color:rgba(27,42,50,.68);margin-bottom:14px;line-height:1.5}
.ctl{display:flex;justify-content:space-between;align-items:baseline}
.lbl{font:600 10px/1 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;letter-spacing:.14em;text-transform:uppercase;color:rgba(27,42,50,.66)}
.val{font:11px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;color:var(--copper);letter-spacing:.06em}
input[type=range]{width:100%;margin:3px 0 7px;-webkit-appearance:none;height:3px;background:rgba(27,42,50,.22);outline:none;cursor:pointer}
input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:13px;height:13px;border-radius:50%;background:var(--copper);box-shadow:0 1px 3px rgba(0,0,0,.4)}
input[type=range]::-moz-range-thumb{width:13px;height:13px;border:none;border-radius:50%;background:var(--copper)}
.row{display:flex;flex-wrap:wrap;gap:5px;margin-top:6px}
button{font:600 10px/1 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;letter-spacing:.11em;text-transform:uppercase;
  padding:6px 8px;border:1px solid rgba(27,42,50,.35);background:rgba(255,253,247,.5);color:var(--ink);cursor:pointer;transition:.15s}
button:hover{background:var(--ink);color:var(--paper);border-color:var(--ink)}
button.on{background:var(--copper);border-color:var(--copper);color:#fff6ea}
#hint{margin-top:12px;font-size:11px;line-height:1.6;color:rgba(27,42,50,.58)}
#hint b{font-weight:400;color:var(--ink)}
#brand{position:fixed;right:24px;top:22px;font:600 10px/1 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  letter-spacing:.26em;color:rgba(255,246,232,.5);text-shadow:0 1px 8px rgba(0,0,0,.55);text-transform:uppercase;pointer-events:none;z-index:10}
.vig{position:fixed;inset:0;pointer-events:none;background:radial-gradient(135% 95% at 50% 38%,transparent 52%,rgba(4,9,14,.44) 100%);z-index:5}
#boot{position:fixed;inset:0;background:#101a23;color:#e7ddc9;display:flex;flex-direction:column;gap:14px;align-items:center;justify-content:center;
  font:600 11px/1 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;letter-spacing:.3em;text-transform:uppercase;transition:opacity .9s ease;z-index:30}
#boot.gone{opacity:0;pointer-events:none}
#boot i{display:block;width:120px;height:2px;background:rgba(231,221,201,.2);overflow:hidden}
#boot i:after{content:"";display:block;width:40%;height:100%;background:var(--copper);animation:s 1.1s ease-in-out infinite}
@keyframes s{0%{transform:translateX(-100%)}100%{transform:translateX(300%)}}
</style>
</head>
<body>
<div id="boot">Charting the harbor<i></i></div>
<div class="vig"></div>
<div id="brand">voxel survey · no. 4</div>
<div id="ui">
  <div id="kicker">Arrivals · 17:42 · fresh breeze</div>
  <div id="ttl">Calling at the Harbor<br><small>a voxel study</small></div>
  <div id="sub">Three‑masted frigate off the town pier — short canvas, hawsers sent, the evening lites lit.</div>

  <div class="ctl"><span class="lbl">Sun</span><span class="val" id="vHour">18:57</span></div>
  <input id="sHour" type="range" min="0" max="1" step="0.001" value="0.905">
  <div class="ctl"><span class="lbl">Swell</span><span class="val" id="vSwell">moderate</span></div>
  <input id="sSwell" type="range" min="0.15" max="2.2" step="0.01" value="1">

  <div class="row" id="cams">
    <button data-c="0" class="on">Overview</button>
    <button data-c="1">Quay</button>
    <button data-c="2">Masthead</button>
    <button data-c="3">Lighthouse</button>
    <button data-c="4">Bow</button>
  </div>
  <div class="row">
    <button id="bOrbit" class="on">Drift ⬤</button>
    <button id="bHide">Hide panel</button>
  </div>
  <div id="hint"><b>Drag</b> to orbit · <b>Wheel</b> to zoom · <b>H</b> toggles this panel · <b>1‑5</b> views</div>
</div>

<script type="importmap">
{ "imports": {
  "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
  "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
}}
</script>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* ═══════════════════════ helpers ═══════════════════════ */
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const d2r=THREE.MathUtils.degToRad;
function hashi(x,y,z){
  let h=(x*374761393)+(y*668265263)+(z*1573909111);
  h=(h^(h>>>13))*1274126177; h=h^(h>>>16);
  return (h>>>0)/4294967295;
}
function n2(x,y){
  const xi=Math.floor(x),yi=Math.floor(y),xf=x-xi,yf=y-yi;
  const u=xf*xf*(3-2*xf),v=yf*yf*(3-2*yf);
  const a=hashi(xi,yi,11),b=hashi(xi+1,yi,11),c=hashi(xi,yi+1,11),d=hashi(xi+1,yi+1,11);
  return (a*(1-u)+b*u)*(1-v)+(c*(1-u)+d*u)*v;
}
const pick=(arr,x,y,z)=>arr[Math.floor(hashi(x,y,z)*arr.length)];

/* ── voxel builder: Map lets upper layers overwrite lower ones ── */
class Vox{
  constructor(){this.m=new Map();}
  set(x,y,z,c,g=0){
    x=Math.round(x);y=Math.round(y);z=Math.round(z);
    this.m.set(((x+2048)*4096+(y+1024))*4096+(z+2048),{x,y,z,c,g});
    return this;
  }
  box(x,y,z,w,h,d,c,g=0){for(let i=0;i<w;i++)for(let j=0;j<h;j++)for(let k=0;k<d;k++)this.set(x+i,y+j,z+k,c,g);return this;}
  rect(x,y,z,w,d,c,g=0){return this.box(x,y,z,w,1,d,c,g);}
  line(x0,y0,z0,x1,y1,z1,c,g=0){
    const dx=x1-x0,dy=y1-y0,dz=z1-z0;
    const n=Math.max(1,Math.ceil(Math.abs(dx)+Math.abs(dy)+Math.abs(dz)));
    for(let i=0;i<=n;i++){const t=i/n;this.set(x0+dx*t,y0+dy*t,z0+dz*t,c,g);}
    return this;
  }
  merge(o,dx=0,dy=0,dz=0){for(const e of o.m.values())this.set(e.x+dx,e.y+dy,e.z+dz,e.c,e.g);return this;}
  build(mat,cast=true,recv=true){
    const n=this.m.size, im=new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1),mat,n);
    im.castShadow=cast;im.receiveShadow=recv;im.frustumCulled=false;
    const o=new THREE.Object3D(),col=new THREE.Color(),glow=new Float32Array(n);
    let i=0;
    for(const e of this.m.values()){
      o.position.set(e.x+0.5,e.y+0.5,e.z+0.5);o.updateMatrix();
      im.setMatrixAt(i,o.matrix);
      col.setHex(e.c).multiplyScalar(0.87+0.26*hashi(e.x,e.y,e.z));
      im.setColorAt(i,col);
      glow[i]=e.g; i++;
    }
    im.geometry.setAttribute('glow',new THREE.InstancedBufferAttribute(glow,1));
    im.instanceMatrix.needsUpdate=true;
    if(im.instanceColor)im.instanceColor.needsUpdate=true;
    return im;
  }
}

/* ═══════════════ shared uniforms & materials ═══════════════ */
const U={ time:{value:0}, glow:{value:.6},
          ampN:{value:.34}, ampF:{value:.55}, stepN:{value:.34}, stepF:{value:.7} };

function voxMaterial(opt={}){
  const m=new THREE.MeshStandardMaterial(Object.assign({roughness:.84,metalness:.02},opt));
  m.onBeforeCompile=(sh)=>{
    sh.uniforms.uGlow=U.glow;
    sh.vertexShader='uniform float uGlow;\nattribute float glow;\nvarying float vGlow;\n'+sh.vertexShader
      .replace('#include <begin_vertex>','#include <begin_vertex>\nvGlow = glow * uGlow;');
    sh.fragmentShader='varying float vGlow;\n'+sh.fragmentShader
      .replace('#include <emissivemap_fragment>',
        '#include <emissivemap_fragment>\ntotalEmissiveRadiance += vec3(1.0,0.66,0.35) * vGlow;');
  };
  m.userData.hook=true;
  return m;
}

function seaMaterial(near){
  const m=new THREE.MeshStandardMaterial({color:0x2f6a86,roughness:.3,metalness:.04});
  m.onBeforeCompile=(sh)=>{
    sh.uniforms.uTime=U.time;
    sh.uniforms.uAmp=near?U.ampN:U.ampF;
    sh.uniforms.uStep=near?U.stepN:U.stepF;
    sh.vertexShader='uniform float uTime,uAmp,uStep;\nvarying float vW;\n'+sh.vertexShader
      .replace('#include <begin_vertex>',`
        #include <begin_vertex>
        #ifdef USE_INSTANCING
          float ix=instanceMatrix[3][0], iz=instanceMatrix[3][2];
          float w = sin(ix*0.130+uTime*0.85)*0.55
                  + sin(iz*0.105-uTime*0.71)*0.45
                  + sin((ix*0.62+iz*0.78)*0.086+uTime*0.52)*0.35
                  + sin((ix*0.30-iz*0.36)*0.20+uTime*1.25)*0.18;
          w = floor(w/uStep + 0.5) * uStep;
          transformed.y += w*uAmp;
          vW = w;
        #endif`);
    sh.fragmentShader='varying float vW;\n'+sh.fragmentShader
      .replace('#include <color_fragment>',`
        #include <color_fragment>
        diffuseColor.rgb *= mix(1.0, 0.66, 1.0 - smoothstep(-1.15, 0.2, vW));
        diffuseColor.rgb = mix(diffuseColor.rgb, vec3(0.72,0.82,0.86), smoothstep(1.05, 1.75, vW)*0.75);`);
  };
  return m;
}

function flagMaterial(phase){
  const m=new THREE.MeshStandardMaterial({color:0xffffff,roughness:.92,metalness:0,side:THREE.DoubleSide});
  m.onBeforeCompile=(sh)=>{
    sh.uniforms.uTime=U.time;
    sh.vertexShader='uniform float uTime,uPhase;\n'+sh.vertexShader.replace('#include <begin_vertex>',`
      #include <begin_vertex>
      #ifdef USE_INSTANCING
        float fx = instanceMatrix[3][0] + transformed.x;
        float a  = clamp(fx/7.0, 0.0, 1.0);
        transformed.y += sin(uTime*4.4 + fx*1.45 + uPhase)*0.40*a;
        transformed.z += cos(uTime*3.1 + fx*1.20 + uPhase)*0.45*a;
      #endif`);
  };
  m.userData={phase};
  return m;
}

/* ═══════════════════════ renderer / scene ═══════════════════════ */
const renderer=new THREE.WebGLRenderer({antialias:true,powerPreference:'high-performance'});
renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
renderer.setSize(innerWidth,innerHeight);
renderer.shadowMap.enabled=true;
renderer.shadowMap.type=THREE.PCFSoftShadowMap;
renderer.toneMapping=THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure=1.0;
document.body.appendChild(renderer.domElement);

const scene=new THREE.Scene();
scene.fog=new THREE.FogExp2(0xdcc4a8,0.0058);

const camera=new THREE.PerspectiveCamera(38,innerWidth/innerHeight,0.5,4200);
camera.position.set(69,39,-56);

const controls=new OrbitControls(camera,renderer.domElement);
controls.target.set(-2,10,8);
controls.enableDamping=true;controls.dampingFactor=.055;
controls.minDistance=30;controls.maxDistance=230;
controls.maxPolarAngle=Math.PI*0.445;controls.minPolarAngle=0.12;
controls.autoRotate=true;controls.autoRotateSpeed=0.26;

/* lights */
const sun=new THREE.DirectionalLight(0xffe9c4,3.0);
sun.castShadow=true;
sun.shadow.mapSize.set(2048,2048);
sun.shadow.camera.left=-170;sun.shadow.camera.right=170;
sun.shadow.camera.top=170;sun.shadow.camera.bottom=-170;
sun.shadow.camera.near=1;sun.shadow.camera.far=640;
sun.shadow.bias=-0.0004; sun.shadow.normalBias=0.32;
scene.add(sun,sun.target);
const hemi=new THREE.HemisphereLight(0x9fc0e0,0x5b5246,0.35);
scene.add(hemi);
const amb=new THREE.AmbientLight(0xffffff,0.12);
scene.add(amb);

/* ═══════════════════════ sky ═══════════════════════ */
const skyMat=new THREE.ShaderMaterial({
  side:THREE.BackSide,depthWrite:false,fog:false,
  uniforms:{uTop:{value:new THREE.Color()},uHor:{value:new THREE.Color()},
            uSunC:{value:new THREE.Color()},uSunDir:{value:new THREE.Vector3()},uHaze:{value:0.35}},
  vertexShader:`varying vec3 vW; void main(){ vW=(modelMatrix*vec4(position,1.0)).xyz;
    gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}`,
  fragmentShader:`varying vec3 vW; uniform vec3 uTop,uHor,uSunC,uSunDir; uniform float uHaze;
    void main(){
      vec3 d=normalize(vW); float y=d.y;
      float k=pow(clamp(1.0-y,0.0,1.0),2.4);
      vec3 c=mix(uTop,uHor,k);
      c=mix(c,uHor*0.55,clamp(-y*9.0,0.0,1.0));
      float s=max(dot(d,normalize(uSunDir)),0.0);
      c+=uSunC*pow(s,2.4)*0.13*uHaze;
      c+=uSunC*pow(s,16.0)*0.30;
      float disc=1.0-smoothstep(0.9986,0.9993,s);
      c=mix(c,uSunC*1.25,disc);
      gl_FragColor=vec4(c,1.0);
      #include <tonemapping_fragment>
      #include <colorspace_fragment>
    }`
});
const sky=new THREE.Mesh(new THREE.SphereGeometry(1600,32,18),skyMat);
sky.frustumCulled=false; scene.add(sky);

/* distant smooth sea + land (the voxel grid fades into fog before reaching them) */
const farSea=new THREE.Mesh(new THREE.CircleGeometry(1550,64),new THREE.MeshBasicMaterial({color:0x2f6a86}));
farSea.geometry.rotateX(-Math.PI/2); farSea.position.y=-1.4; scene.add(farSea);
const farLand=new THREE.Mesh(new THREE.PlaneGeometry(3200,2600),new THREE.MeshBasicMaterial({color:0x74835a}));
farLand.geometry.rotateX(-Math.PI/2); farLand.position.set(0,13.1,1400); scene.add(farLand);

/* ═══════════════════════ THE VESSEL ═══════════════════════ */
/* ship-local: bow = +Z, up = +Y, waterline = y0, keel y=-5 */
const MAST=[{z:10,top:30,dy:7,deck:6},{z:0,top:36,dy:6,deck:5},{z:-14,top:26,dy:7,deck:6}];
const YARD=[
  {m:10,y:13,h:10},{m:10,y:19,h:7.5},{m:10,y:24,h:5},
  {m:0,y:14,h:11},{m:0,y:22,h:9},{m:0,y:28,h:6.5},
  {m:-14,y:13,h:9},{m:-14,y:19,h:6.5}
];
const SAIL=[
  {m:10,y:13,top:12,bot:7,bulge:3,furled:false},
  {m:10,y:19,furled:true},
  {m:10,y:24,furled:true},
  {m:0,y:14,top:13,bot:7,bulge:3.6,furled:false},
  {m:0,y:22,top:21,bot:18,bulge:3,furled:false},
  {m:-14,y:13,top:12,bot:7,bulge:3,furled:false},
  {m:-14,y:19,furled:true}
];
const YARDHALF={ '10_13':10,'10_19':7.5,'10_24':5,'0_14':11,'0_22':9,'0_28':6.5,'-14_13':9,'-14_19':6.5 };

function hullCol(x,y,z,side){
  if(y<0){
    if(y===-1) return side ? (z%5===0?0x8a4b35:0x5d3327) : 0x3a2720;
    return 0x33221d;
  }
  if(y===0) return side ? 0xc9a24f : 0x3c2a22;
  if(y===1||y===2) return side ? 0x443128 : 0x3a2b23;
  if(y===3||y===4){
    const gold=((Math.floor((z+24)/2)+y)%2)===0;
    if(side && z%4===1) return 0x14110f;              // gunport
    return gold?0xdcae5c:0x302722;
  }
  return side ? 0x2f5b6b : 0x3a2b23;
}
const PROF=[[-5,0.18],[-4,0.45],[-3,0.72],[-2,0.90],[-1,0.98],[0,1],[1,1],[2,0.995],[3,0.98],[4,0.95],[5,0.90]];
const py=y=>(y<-5||y>5)?0:PROF[y+5][1];
function longF(z){
  if(z>=0){const d=24-z;return Math.pow(Math.min(1,(d+1.5)/9),0.8);}
  const d=z+24; if(d<=2) return 0.84;
  return Math.pow(Math.min(1,(d+1)/10),0.62);
}

function buildShip(){
  const b=new Vox(), rig=[];
  const R=(a,c)=>rig.push(a,c);
  const V=(x,y,z)=>new THREE.Vector3(x,y,z);

  /* hull */
  for(let z=-24;z<=24;z++){
    const f=longF(z);
    for(let y=-5;y<=5;y++){
      const hw=Math.round(6*py(y)*f);
      if(hw<0) continue;
      for(let x=-hw;x<=hw;x++) b.set(x,y,z,hullCol(x,y,z,Math.abs(x)===hw));
    }
  }
  /* decks, bulwarks, sheer */
  for(let z=-24;z<=24;z++){
    const hw5=Math.round(6*py(5)*longF(z)); if(hw5<=0) continue;
    const raised=Math.abs(z)>=10, deckY=raised?6:5;
    for(let x=-hw5+1;x<=hw5-1;x++) b.set(x,deckY,z,(z%2===0)?0xa37b52:0x8f6946);
    let rh=2; if(Math.abs(z)>=20) rh=3;
    for(let k=1;k<=rh;k++){
      const y=deckY+k, c=(k===rh)?0xe2d4b8:0x2f5b6b;
      b.set(hw5,y,z,c); b.set(-hw5,y,z,c);
    }
  }
  /* stern windows (glow) */
  for(let x=-4;x<=4;x++){
    const win=Math.abs(x)%2===0;
    b.set(x,5,-24, win?0xffd7a2:0xdcae5c, win?0.85:0);
  }
  b.box(-5,7,-24,11,1,1,0xdcae5c);
  /* bowsprit + jacks */
  b.line(0,6,20,0,15,40,0x6b4a30);
  b.line(0,7,20,0,16,40,0x6b4a30);
  b.box(-1,6,20,3,2,2,0x4a3425);
  /* figurehead */
  b.line(0,3,22,0,6,28,0xdcae5c); b.set(0,7,28,0xdcae5c); b.set(0,7,29,0xb8913f);
  /* masts, tops, yards */
  for(const m of MAST){
    for(let y=m.deck;y<=m.top;y++) b.set(0,y,m.z, y>m.top-4?0x5c4030:0x8f6946);
    const plat=m===MAST[1]?24:(m===MAST[0]?20:17);
    b.box(-3,plat,m.z-2,7,1,5,0x6b4a30);
    for(let x=-3;x<=3;x++){ b.set(x,plat+1,m.z-2,0x5c4030); b.set(x,plat+1,m.z+2,0x5c4030); }
    for(let dz=-2;dz<=2;dz++){ b.set(-3,plat+1,m.z+dz,0x5c4030); b.set(3,plat+1,m.z+dz,0x5c4030); }
  }
  for(const yd of YARD){
    const h=Math.round(YARDHALF[yd.m+'_'+yd.y]);
    b.line(-h,yd.y,yd.m,h,yd.y,yd.m,0x5c4030);
    b.set(0,yd.y,yd.m,0x4a3425);
  }
  /* sails */
  for(const s of SAIL){
    const yd=YARD.find(q=>q.m===s.m&&q.y===s.y); const h=Math.round(YARDHALF[yd.m+'_'+yd.y]);
    if(s.furled){
      for(let x=-h;x<=h;x++){
        const u=1-(x/h)**2, dz=Math.round(u*1.2);
        b.set(x,yd.y-1,yd.m+dz,0xe6dcc6);
        if(u>0.2) b.set(x,yd.y-2,yd.m+dz,0xc4b092);
      }
    }else{
      for(let x=-h;x<=h;x++){
        const u=1-(x/h)**2, bz=yd.m-Math.round(u*s.bulge), yB=s.bot+Math.round(u*1.2);
        for(let y=yB;y<=s.top;y++)
          b.set(x,y,bz,((y%4===0)||(Math.abs(x)%6===0))?0xcdbca0:0xe8dcc2);
      }
    }
  }
  /* jibs + spanker */
  const tri=(A,B,C,bulge)=>{
    const e1=B.clone().sub(A),e2=C.clone().sub(A),N=44;
    for(let i=0;i<=N;i++)for(let j=0;j<=N-i;j++){
      const u=i/N,v=j/N,p=A.clone().addScaledVector(e1,u).addScaledVector(e2,v);
      const k=Math.sin(u*Math.PI)*(0.4+0.6*v);
      b.set(p.x,p.y,p.z-Math.round(k*bulge), (i%9===0)?0xcdbca0:0xe8dcc2);
    }
  };
  tri(V(0,26,10),V(0,15,34),V(0,8,22),2.5);
  tri(V(0,25,12),V(0,19,40),V(0,7,26),3);
  tri(V(0,17,-16),V(0,7,-16),V(0,10,-26),2.5);

  /* deck furniture */
  b.box(-1,7,16,3,2,3,0x4a3425);
  for(const d of [[2,0],[0,2],[-2,0],[0,-2]]) b.set(2+d[0],8,16+d[1],0x8f6946);
  for(let a=0;a<32;a++){const t=a/32*6.283;b.set(0,9+Math.sin(t)*2,-18+Math.cos(t)*2,0x8f6946);}
  b.set(0,9,-18,0x4a3425); b.line(2,9,-18,-2,9,-18,0x5c4030); b.set(-3,9,-20,0x8f6946);
  b.box(-3,6,-6,6,1,4,0x7a5a3a); b.box(3,6,4,5,1,3,0x7a5a3a);
  for(const p of [[0,-4],[1,-9],[-1,13]]){ b.box(p[0],7,p[1],2,2,2,0x8f6946);
    b.set(p[0],7,p[1],0x6b4a30);b.set(p[0]+1,7,p[1],0x6b4a30);b.set(p[0],7,p[1]+1,0x6b4a30);b.set(p[0]+1,7,p[1]+1,0x6b4a30); }
  const crew=[[0,7,2],[0,7,-4],[-1,7,-10],[1,7,20],[0,7,23],[-1,21,0],[1,20,10]];
  for(const c of crew){ b.set(c[0],c[1],c[2],0xe0aa82); b.set(c[0],c[1]+1,c[2],c[2]>0?0x2f4f6b:0x8f3f35); b.set(c[0],c[1]+2,c[2],0x22272c); }
  b.set(1,11,-22,0xffd9a0,0.6); b.set(-1,11,-22,0xffd9a0,0.6);

  /* rigging */
  for(const m of MAST){
    for(const s of [-1,1]){
      R(V(0,m.top-1,m.z),V(s*5,m.deck+1,m.z-3));
      R(V(0,m.top-2,m.z),V(s*5,m.deck+1,m.z));
      R(V(0,m.top-3,m.z),V(s*5,m.deck+1,m.z+3));
    }
    R(V(0,m.top,m.z),V(0,m.deck+2,-22));
    R(V(0,m.top-2,m.z),V(0,m.deck+1,-24));
  }
  for(const yd of YARD){
    const h=Math.round(YARDHALF[yd.m+'_'+yd.y]);
    R(V(h,yd.y,yd.m),V(2,yd.m>0?7:7,yd.m-9));
    R(V(-h,yd.y,yd.m),V(-2,7,yd.m-9));
    R(V(h,yd.y,yd.m),V(-2,yd.m>0?9:9,yd.m+9));
  }
  R(V(0,7,23),V(0,19,40)); R(V(0,15,34),V(0,26,10));
  R(V(0,6,22),V(0,15,40)); R(V(-1,8,24),V(0,19,40));
  R(V(0,30,10),V(0,26,10));
  return {vox:b,rig};
}

/* ═══════════════════════ THE HARBOR ═══════════════════════ */
const QY=12;
function buildHarbor(){
  const b=new Vox();

  /* --- main quay --- */
  for(let x=-80;x<=80;x++)for(let z=34;z<=36;z++)for(let y=-4;y<=QY;y++){
    let c;
    if(y===QY) c=(x%2===0)?0xb2aa9c:0xa69e90;
    else if(z===34) c=pick([0x8b8378,0x7d756b,0x999284],x,y,z);
    else c=pick([0x6f675d,0x7a7369],x,y,z);
    b.set(x,y,z,c);
  }
  /* --- land --- */
  for(let x=-80;x<=80;x++)for(let z=37;z<=96;z++){
    const hill=z<52?0:clamp((z-52)/18,0,1)*2.4+n2(x*0.07,z*0.07)*0.8;
    const h=QY+1+Math.round(hill);
    b.set(x,h,z,pick([0x6d8057,0x748a5d,0x65754f],x,h,z));
    b.set(x,h-1,z,0x6a5744);
  }
  /* --- bollards, lamps, street paving --- */
  for(let x=-72;x<=72;x+=12) b.box(x,QY+1,34,1,2,1,0x4a3425);
  for(const x of [-68,-46,-24,12,30,54]){
    b.box(x,QY+1,35,1,4,1,0x3a3f45);
    b.set(x,QY+6,35,0xffdca6,1.3);
    b.set(x,QY+7,35,0x3a3f45); b.set(x-1,QY+6,35,0x3a3f45); b.set(x+1,QY+6,35,0x3a3f45);
  }
  /* --- warehouses --- */
  const walls=[0xb3563f,0x9e9082,0x8a5f3c];
  for(let i=0;i<3;i++){
    const x0=14+i*20, z0=46, w=16, d=12, h=9;
    const wc=walls[i%3], rc=i%2?0x2e5c74:0x8f3f2f;
    b.box(x0,QY+1,z0,w,h,1,wc); b.box(x0,QY+1,z0+d-1,w,h,1,wc);
    b.box(x0,QY+1,z0+1,1,h,d-2,wc); b.box(x0+w-1,QY+1,z0+1,1,h,d-2,wc);
    for(let s=0;s<4;s++){
      const y=QY+2+s*2;
      b.box(x0+s*4+2,y,z0,3,2,1,0x1d1814,0.28);
      b.box(x0+s*4+2,y-1,z0-1,3,1,1,0x8f6946);
    }
    b.box(x0+6,QY+1,z0-1,4,5,2,0x4a3425);
    b.line(x0,z0-1,QY+10,x0+w,z0-1,QY+10,rc);
    for(let s=1;s<Math.floor(w/2);s++){ const y=QY+10+s; b.box(x0+2*s,y-1,z0-1,2,1,2,rc); }
  }
  /* --- townhouses --- */
  const house=(x,z,w,d,h,wc,rc)=>{
    b.box(x,QY+1,z,w,h,1,wc); b.box(x,QY+1,z+d-1,w,h,1,wc);
    b.box(x,QY+1,z+1,1,h,d-2,wc); b.box(x+w-1,QY+1,z+1,1,h,d-2,wc);
    for(let i=1;i<w;i+=3){
      b.set(x+i,QY+4,z,0xffd9a0,0.5); b.set(x+i,QY+6,z,0xffd9a0,0.5);
      b.box(x+i-1,QY+7,z,1,1,1,0xf2e8d2);
    }
    b.box(x+Math.floor(w/2),QY+1,z-1,2,3,1,0x4a3425);
    for(let s=0;s<Math.floor(w/2);s++){ const y=QY+h+s; b.box(x,y,z-1+w-s,1,1,2+s,rc); }
    b.box(x+2,QY+h+3,z+d/2-1,1,2,1,0x5c4030);
  };
  house(-24,64,10,8,6,0xf0e4cc,0x8f3f2f);
  house(-12,66,12,9,7,0xc9a887,0x2e5c74);
  house(0,64,9,8,6,0xe6d7bc,0x54637a);
  /* --- church --- */
  const cH=QY+1;
  b.box(28,cH,62,18,9,1,0xbfb4a0); b.box(28,cH,77,18,9,1,0xbfb4a0);
  b.box(28,cH,63,1,9,14,0xbfb4a0); b.box(45,cH,63,1,9,14,0xbfb4a0);
  for(let s=0;s<9;s++){ b.box(28,cH+9+s,62+s,18,1,1,0x54637a); b.box(28,cH+9+s,77-s,18,1,1,0x54637a); }
  for(let i=0;i<4;i++) b.box(31+i*4,cH+2,61,2,4,1,0xffd9a0,0.35);
  b.box(34,cH,50,7,7,12,0xb4a895); b.box(34,cH,50,7,25,12,0xb4a895);
  b.box(34+1,cH+22,52,5,3,8,0xffe0ab,0.25);
  for(let s=0;s<4;s++) b.box(33+s,cH+25+s,49+s,5-2*s,1,10-2*s,0x54637a);
  b.set(36,cH+30,48,0xffe0ab,0.4);
  /* --- trees --- */
  const tree=(x,z)=>{
    const g=n2(x*0.07,z*0.07), h=QY+1+Math.round(clamp((z-52)/18,0,1)*2.4+g*0.8);
    const th=4+Math.round(hashi(x,z,3)*2);
    b.box(x,h+1,z,1,th,1,0x4a3425);
    for(let k=0;k<3;k++){ const r=2-k, y=h+th+k;
      for(let dx=-r;dx<=r;dx++)for(let dz=-r;dz<=r;dx!==0||dz!==0?true:false&&dx!==0:
        (Math.abs(dx)+Math.abs(dz)<=r+1)){ if(Math.abs(dx)+Math.abs(dz)>r+1)continue;
          b.set(x+dx,y,z+dz,pick([0x4b6e43,0x5d8251,0x39563a],x+dx,y,z+dz)); } }
  };
  for(const p of [[-70,58],[-62,64],[-54,72],[-46,66],[-34,72],[-26,78],[-8,74],[4,76],[16,70],[22,82],[46,64],[58,58],[66,70],[72,78],[-66,80],[10,84],[40,78],[52,86]]) tree(p[0],p[1]);
  /* --- market stalls --- */
  for(let i=0;i<3;i++){ const x=8+i*6;
    b.box(x,QY+1,39,4,2,3,0x8f6946);
    b.set(x,QY+3,38,0xf2e8d2); b.set(x+2,QY+3,38,0xb2523e);
    b.box(x,QY+3,38,4,1,3,(i%2)?0xb2523e:0x2e5c74);
  }
  /* --- town pier --- */
  for(let z=-12;z<=33;z++){ const zc=(z%3===0)?0x8f6946:0x9c7247;
    for(let x=-5;x<=1;x++) b.set(x,10,z,zc);
    if(z%4===0){ b.line(-4,3,z,-4,10,z,0x4a3425); b.line(1,3,z,1,10,z,0x4a3425);
      b.box(-4,9,z,6,1,1,0x5c4030); }
  }
  /* --- boat pier --- */
  for(let z=16;z<=33;z++){ for(let x=10;x<=13;x++) b.set(x,10,z,(z%3===0)?0x8f6946:0x9c7247);
    if(z%4===1){ b.line(10,4,z,10,10,z,0x4a3425); b.line(13,4,z,13,10,z,0x4a3425); } }
  /* --- props --- */
  const crate=(x,z)=>{ b.box(x,11,z,2,2,2,0x9c7247);
    for(const d of [[0,0],[1,0],[0,1],[1,1]]){ b.set(x+d[0],11,z+d[1],0x6b4a30); b.set(x+d[0],12,z+d[1],0x6b4a30); } };
  const barrel=(x,z)=>{ b.box(x,11,z,1,2,1,0x8a6141); b.set(x,13,z,0x6b4a30); b.set(x,11,z,0x6b4a30); };
  const sack=(x,z)=>{ b.box(x,11,z,2,1,2,0xb7a170); };
  for(const p of [[-2,24],[-3,20],[0,18],[-4,15],[1,12],[-1,4],[0,-3],[-3,-8],[9,22],[12,26],[11,19],[14,30]]) barrel(p[0],p[1]);
  for(const p of [[-1,22],[1,20],[-4,12],[0,8],[-2,0],[2,-9],[10,24],[13,17]]) crate(p[0],p[1]);
  for(const p of [[-3,26],[2,16],[-2,6],[12,21]]) sack(p[0],p[1]);
  for(const p of [[-2,-11],[1,-11]]) b.box(p[0],11,p[1],1,1,4,0x7a5a3a);
  const rope=(x,z)=>{ for(let a=0;a<16;a++){const t=a/16*6.283; b.set(x+Math.round(Math.cos(t)*2),11,z+Math.round(Math.sin(t)*2),0x9c8361);} b.set(x,12,z,0x9c8361); };
  rope(-4,6); rope(14,28);
  for(const x of [-2,6,18,34]) b.box(x,11,38,1,1,1,0xb2523e);
  const fig=(x,z,c)=>{ b.set(x,11,z,0x1f2732); b.set(x,12,z,c); b.set(x,13,z,0xe0aa82); b.set(x,14,z,0x2f3a45); };
  fig(-2,28,0x2f4f6b); fig(-1,27,0x8f3f35); fig(13,18,0x54637a);
  fig(-3,30,0x6b5a3e); fig(11,31,0x2f4f6b); fig(24,36,0x8f3f35); fig(30,37,0x54637a);
  /* flagpole on the quay */
  b.line(44,13,44,44,24,44,0x3a3f45);
  /* --- breakwater + lighthouse --- */
  for(let x=22;x<=66;x++)for(let z=30;z<=44;z++){
    const r=Math.hypot((x-44)/2.4,z-37);
    if(r>9.5) continue;
    const top=QY+Math.max(0,Math.round(3*(1-r/9.5)))-1;
    for(let y=-3;y<=top;y++) b.set(x,y,z,pick([0x7d756b,0x8b8378,0x6a6359],x,y,z));
    if(z<=30-0.4||(z<=31&&x%3===0)) b.set(x,top,z,0x9a9385);
  }
  const lhx=44,lhz=37;
  for(let dy=0;dy<22;dy++){
    const r=dy<5?5:(dy<11?4:3), y=12+dy;
    for(let dx=-r;dx<=r;dx++)for(let dz=-r;dz<=r;dz++){
      if(dx*dx+dz*dz>r*r+0.5) continue;
      const band=Math.floor(dy/4)%2===0;
      b.set(lhx+dx,y,lhz+dz, band?0xece4d6:0xa84432);
    }
  }
  b.box(lhx-5,33,lhz-5,11,1,11,0x3a3f45);
  for(let a=0;a<24;a++){const t=a/24*6.283;b.set(lhx+Math.round(Math.cos(t)*5),34,lhz+Math.round(Math.sin(t)*5),0x3a3f45);}
  for(let dx=-3;dx<=3;dx++)for(let dz=-3;dz<=3;dz++){
    if(dx*dx+dz*dz>10) continue;
    b.set(lhx+dx,35,lhz+dz, (Math.abs(dx)===3||Math.abs(dz)===3)?0x3a3f45:0xffe8bc,
      (Math.abs(dx)===3||Math.abs(dz)===3)?0.9:2.2);
  }
  b.set(lhx,36,lhz,0xfff3d8,2.4);
  for(let s=0;s<3;s++){ const w=7-2*s; b.box(lhx-s,36+s,lhz-s,w,1,w,s===2?0xa84432:0x8f3f2f); }
  b.set(lhx,39,lhz,0xdcae5c,0.6);
  b.line(lhx-3,33,lhz+6,lhx-3,34,lhz+6,0x3a3f45);
  /* --- windmill --- */
  const mhx=-72,mhz=78,mg=QY+1+2;
  for(let dy=0;dy<17;dy++){
    const r=dy<4?4:(dy<11?3:2);
    for(let dx=-r;dx<=r;dx++)for(let dz=-r;dz<=r;dz++){
      if(dx*dx+dz*dz>r*r+0.5) continue;
      b.set(mhx+dx,mg+dy,mhz+dz,dy%5===0?0x8f6946:0xa8835a);
    }
  }
  b.box(mhx,mg+8,mhz-5,1,3,2,0xffd9a0,0.5);
  b.box(mhx-1,mg+1,mhz-5,3,4,2,0x4a3425);
  for(let s=0;s<4;s++) b.box(mhx-s,mg+17+s,mhz-s,7-2*s,1,7-2*s,0x54637a);
  b.line(mhx,mg+19,mhz,mhx,mg+21,mhz-3,0x5c4030);
  /* --- the vessel footprint gets the mooring rings on the quay --- */
  return b;
}

/* ═══════════════════════ assemble vessel ═══════════════════════ */
const mainMat=voxMaterial();
const {vox:shipVox,rig}=buildShip();
const harborVox=buildHarbor();

const shipGroup=new THREE.Group();
shipGroup.position.set(-13,0,0);
const shipMesh=shipVox.build(mainMat,true,true);
shipGroup.add(shipMesh);

const rigGeo=new THREE.BufferGeometry().setFromPoints(rig);
shipGroup.add(new THREE.LineSegments(rigGeo,new THREE.LineBasicMaterial({color:0x2a1f16,transparent:true,opacity:0.82})));

/* foam ring riding the waterline (child of the ship so it rocks with her) */
const foamVox=new Vox();
for(let z=-25;z<=27;z++){
  for(const s of [-1,1]){
    for(let i=0;i<3;i++){
      const x=s*(7+i)+(z%2);
      if(Math.abs(z)>22&&i>0) continue;
      if(hashi(x,z,77)>0.62) foamVox.set(x,0,z,0xf3f7f5);
    }
  }
}
const foamMesh=foamVox.build(new THREE.MeshStandardMaterial({color:0xffffff,roughness:0.15,metalness:0}),false,true);
shipGroup.add(foamMesh);

/* flags aboard */
function rectFlag(w,h,fn){ const f=new Vox();
  for(let x=0;x<w;x++)for(let y=0;y<h;y++){const c=fn(x,y,w,h); if(c) f.set(x,y,0,c);} return f; }
const flagMatA=flagMaterial(0.0), flagMatB=flagMaterial(2.1);

const ensign=rectFlag(8,5,(x,y)=>((y<2&&x<4)||(y===2||x===4)?0xf2e8d2:0x24415f));
const ensG=new THREE.Group(); ensG.position.set(0,21,-22); ensG.rotation.set(0.15,Math.PI/2,0.12);
ensG.add(ensign.build(flagMatA,false,false)); shipGroup.add(ensG);
shipGroup.add(new THREE.Mesh(new THREE.BoxGeometry(0.4,4.5,0.4),
  new THREE.MeshStandardMaterial({color:0x4a3425,roughness:.9})).translateOnAxis(new THREE.Vector3(0,1,0),20.5));

const jack=rectFlag(6,4,(x,y)=>((x+y)%2===0?0x24415f:0xe8dcc2));
const jackG=new THREE.Group(); jackG.position.set(0,19,40); jackG.rotation.set(0.1,Math.PI/2,0.2);
jackG.add(jack.build(flagMatB,false,false)); shipGroup.add(jackG);

const pen=rectFlag(12,3,(x,y,w,h)=>(y>=2-Math.floor(x/4))?((x<6)?0x2d7f9c:0xe8dcc2):0);
const penG=new THREE.Group(); penG.position.set(0,34,0); penG.rotation.y=Math.PI/2;
penG.add(pen.build(flagMatA,false,false)); shipGroup.add(penG);

scene.add(shipGroup);

/* ═══════════════════════ harbor mesh ═══════════════════════ */
const harborMesh=harborVox.build(mainMat,true,true);
scene.add(harborMesh);

/* quay flag */
const qFlag=rectFlag(7,4,(x,y,w,h)=>(y>h-2)?0xf2e8d2:(x<3?0x2d7f9c:0xc0392b));
const qFlagG=new THREE.Group(); qFlagG.position.set(44,24,44); qFlagG.rotation.y=0.6;
qFlagG.add(qFlag.build(flagMatB,false,false)); scene.add(qFlagG);

/* ═══════════════════════ moorings + gangway ═══════════════════════ */
const ropeMat=new THREE.LineBasicMaterial({color:0x6b5136,transparent:true,opacity:0.92});
function sagLine(aLocal,bWorld,sag){
  const N=14,pos=new Float32Array(N*3);
  const geo=new THREE.BufferGeometry();
  geo.setAttribute('position',new THREE.BufferAttribute(pos,3));
  const l=new THREE.Line(geo,ropeMat); l.frustumCulled=false; scene.add(l);
  return ()=>{
    const a=shipGroup.localToWorld(aLocal.clone());
    for(let i=0;i<N;i++){
      const t=i/(N-1);
      pos[i*3]=a.x+(bWorld.x-a.x)*t;
      pos[i*3+1]=a.y+(bWorld.y-a.y)*t-Math.sin(t*Math.PI)*sag;
      pos[i*3+2]=a.z+(bWorld.z-a.z)*t;
    }
    geo.attributes.position.needsUpdate=true;
  };
}
const updaters=[
  sagLine(new THREE.Vector3(6,7,15),new THREE.Vector3(-4,13,24),1.1),
  sagLine(new THREE.Vector3(6,7,-15),new THREE.Vector3(-4,13,-11),1.3),
  sagLine(new THREE.Vector3(6,8,-2),new THREE.Vector3(-4,12,18),0.6)
];

const gang=new THREE.Group();
{
  const g=new THREE.BoxGeometry(1.4,0.3,4.6); g.translate(0,0,2.3);
  gang.add(new THREE.Mesh(g,new THREE.MeshStandardMaterial({color:0x9c7247,roughness:.85})));
  const pts=[new THREE.Vector3(-0.7,0.9,0.4),new THREE.Vector3(-0.7,0.75,4.3),
             new THREE.Vector3(0.7,0.9,0.4),new THREE.Vector3(0.7,0.75,4.3)];
  gang.add(new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(pts),ropeMat));
  for(const d of [-0.7,0.7]) gang.add(new THREE.Mesh(new THREE.BoxGeometry(0.2,1,0.2),
    new THREE.MeshStandardMaterial({color:0x4a3425})).translateX(d).translateZ(4.1).translateY(0.5));
}
gang.position.set(-3.5,11,10); scene.add(gang);

/* ═══════════════════════ sea ═══════════════════════ */
function makeSea(near,box,r1,r2,stride){
  const cells=[];
  for(let x=-r2;x<=r2;x+=stride)for(let z=-r2;z<=33;z+=stride){
    const rr=x*x+z*z;
    if(rr<r1*r1||rr>r2*r2) continue;
    cells.push(x,z);
  }
  const im=new THREE.InstancedMesh(box,seaMaterial(near),cells.length/2);
  im.castShadow=false; im.receiveShadow=true; im.frustumCulled=false;
  const o=new THREE.Object3D(),col=new THREE.Color();
  for(let i=0;i<cells.length/2;i++){
    const x=cells[i*2],z=cells[i*2+1];
    o.position.set(x,-(box.parameters.height/2),z); o.updateMatrix();
    im.setMatrixAt(i,o.matrix);
    const h=hashi(x,z,5);
    col.setHex(0x2f6a86).multiplyScalar(0.86+0.3*h);
    im.setColorAt(i,col);
  }
  im.instanceMatrix.needsUpdate=true; if(im.instanceColor) im.instanceColor.needsUpdate=true;
  scene.add(im); return im;
}
makeSea(true,new THREE.BoxGeometry(1.02,12,1.02),0,86,1);
makeSea(false,new THREE.BoxGeometry(2.06,20,2.06),86,186,2);

/* ═══════════════════════ clouds ═══════════════════════ */
const cloudVox=new Vox();
for(let c=0;c<20;c++){
  const a=hashi(c,9,1)*6.283, r=250+hashi(c,3,7)*170, y=58+hashi(c,21,5)*55;
  const cx=Math.cos(a)*r, cz=Math.sin(a)*r;
  const n=3+Math.floor(hashi(c,2,2)*4);
  for(let p=0;p<n;p++){
    const dx=Math.round((hashi(c,p,1)-0.5)*26), dz=Math.round((hashi(c,p,2)-0.5)*30),
          dy=Math.round(hashi(c,p,3)*6), w=4+Math.floor(hashi(c,p,4)*8),
          h=2+Math.floor(hashi(c,p,5)*3), d=3+Math.floor(hashi(c,p,6)*7);
    cloudVox.box(cx+dx,y+dy,cz+dz,w,h,d, pick([0xf7f4ec,0xeae4d8,0xfdfbf6],c,p,dy), 0.02);
  }
}
const cloudMat=new THREE.MeshStandardMaterial({color:0xffffff,roughness:1,metalness:0});
cloudMat.onBeforeCompile=mainMat.onBeforeCompile;
const cloudGrp=new THREE.Group();
cloudGrp.add(cloudVox.build(cloudMat,false,false));
scene.add(cloudGrp);

/* ═══════════════════════ animated bits ═══════════════════════ */
/* windmill */
const mill=new THREE.Group(); mill.position.set(-72,32,78);
{
  const armMat=new THREE.MeshStandardMaterial({color:0x4a3425,roughness:.9});
  const sailMat=new THREE.MeshStandardMaterial({color:0xe8dcc2,roughness:.95,side:THREE.DoubleSide});
  for(let i=0;i<4;i++){
    const bl=new THREE.Group(); bl.rotation.z=i*Math.PI/2;
    const arm=new THREE.Mesh(new THREE.BoxGeometry(0.5,11,0.5),armMat); arm.position.y=5.8; bl.add(arm);
    const sail=new THREE.Mesh(new THREE.BoxGeometry(1.3,8.5,0.25),sailMat); sail.position.set(1.15,6.2,0.1); bl.add(sail);
    mill.add(bl);
  }
  mill.add(new THREE.Mesh(new THREE.BoxGeometry(1,1,3),armMat));
}
scene.add(mill);

/* lighthouse beam */
const beamMat=new THREE.MeshBasicMaterial({color:0xffe6b8,transparent:true,opacity:0.06,
  blending:THREE.AdditiveBlending,depthWrite:false,side:THREE.DoubleSide,fog:true});
const beams=new THREE.Group(); beams.position.set(44,36,37);
for(let i=0;i<2;i++){
  const g=new THREE.ConeGeometry(11,200,22,1,true);
  g.rotateX(Math.PI/2); g.translate(100,0,0);
  const m=new THREE.Mesh(g,beamMat); m.rotation.y=i*Math.PI; beams.add(m);
}
beams.frustumCulled=false; scene.add(beams);

/* rowboats */
function boat(withRowers){
  const b=new Vox();
  b.rect(0,0,0,5,3,0x6b4a30);
  b.rect(0,1,0,5,1,0x8f6946); b.rect(0,1,2,5,1,0x8f6946);
  b.set(0,1,1,0x7a5a3a);
  for(const x of [0,4]) b.set(x,1,0,0x4a3425);
  b.rect(1,0,1,3,1,0xa37b52);
  if(withRowers){
    for(const z of [0.5,2]){ b.set(2,2,z,0xe0aa82); b.set(2,3,z,0x2f4f6b); }
  }else{
    b.box(1,1,1,2,1,1,0x9c8361);
  }
  const g=new THREE.Group(); g.add(b.build(mainMat,true,true));
  if(withRowers){
    const oarG=new THREE.Group(), oars=[];
    for(const z of [0,2]){
      const o=new THREE.Group();
      const m=new THREE.Mesh(new THREE.BoxGeometry(0.22,0.22,4.2),new THREE.MeshStandardMaterial({color:0x8f6946}));
      m.position.z=-1.4; o.add(m); o.position.set(2,2,z); o.rotation.z=0.55; oars.push(o); g.add(o);
    }
    g.userData.oars=oars;
  }
  return g;
}
const boat1=boat(false); boat1.position.set(9,0.4,22); boat1.rotation.y=0.4; scene.add(boat1);
const boat2=boat(true);  boat2.position.set(28,0.4,-14); boat2.rotation.y=2.1; scene.add(boat2);
const boat3=boat(false); boat3.position.set(11,10.2,24); boat3.rotation.y=1.4; scene.add(boat3);

/* gulls */
const gullMatW=new THREE.MeshStandardMaterial({color:0xf4f2ea,roughness:.9});
const gullMatD=new THREE.MeshStandardMaterial({color:0x3a3f45,roughness:.9});
const gulls=[];
for(let i=0;i<8;i++){
  const g=new THREE.Group();
  g.add(new THREE.Mesh(new THREE.BoxGeometry(0.5,0.4,1.8),gullMatW));
  const lw=new THREE.Group(), rw=new THREE.Group();
  const lm=new THREE.Mesh(new THREE.BoxGeometry(1.9,0.15,0.7),gullMatD); lm.position.x=-1.1; lw.add(lm);
  const rm=new THREE.Mesh(new THREE.BoxGeometry(1.9,0.15,0.7),gullMatD); rm.position.x=1.1; rw.add(rm);
  g.add(lw,rw);
  g.userData={r:26+hashi(i,4,4)*34,y:24+hashi(i,5,5)*16,spd:0.14+hashi(i,6,6)*0.12,ph:hashi(i,7,7)*6.283,lw,rw};
  g.position.set(0,g.userData.y,0); g.frustumCulled=false;
  scene.add(g); gulls.push(g);
}

/* ═══════════════════════ time of day ═══════════════════════ */
const STOPS=[
 {el:3,  top:'#111d38', hor:'#ee8f5e', sun:'#ff8851', fog:'#cb9a82', wat:'#234256', amb:0.10,sunI:1.7,glow:1.05,exp:1.16,haze:.55},
 {el:9,  top:'#1d3659', hor:'#f2a573', sun:'#ffa266', fog:'#d6a98f', wat:'#25516c', amb:0.14,sunI:2.2,glow:0.90,exp:1.12,haze:.48},
 {el:17, top:'#2a4e80', hor:'#f4c395', sun:'#ffca8e', fog:'#e0c3a6', wat:'#285b77', amb:0.21,sunI:2.7,glow:0.55,exp:1.05,haze:.40},
 {el:34, top:'#2e6ba9', hor:'#dcdad0', sun:'#ffe9c8', fog:'#cfd5d2', wat:'#2b6b86', amb:0.34,sunI:3.1,glow:0.18,exp:1.00,haze:.30},
 {el:62, top:'#2f7bb6', hor:'#d6e7f0', sun:'#ffffff', fog:'#c9dbe4', wat:'#2e7490', amb:0.46,sunI:3.3,glow:0.05,exp:0.98,haze:.24}
];
const tmpA=new THREE.Color(),tmpB=new THREE.Color();
function sampleStops(el){
  let i=0; while(i<STOPS.length-2 && el>STOPS[i+1].el) i++;
  const a=STOPS[i],b=STOPS[i+1],t=clamp((el-a.el)/(b.el-a.el),0,1);
  const out={};
  for(const k of ['amb','sunI','glow','exp','haze']) out[k]=a[k]+(b[k]-a[k])*t;
  for(const k of ['top','hor','sun','fog','wat']){
    tmpA.set(a[k]); tmpB.set(b[k]); out[k]=tmpA.clone().lerp(tmpB,t);
  }
  return out;
}
function applyTime(t){
  const el=3+62*Math.sin(Math.PI*t);
  const az=d2r(100+170*t);
  const s=sampleStops(el);
  const dir=new THREE.Vector3(Math.cos(az)*Math.cos(d2r(el)),Math.sin(d2r(el)),Math.sin(az)*Math.cos(d2r(el)));
  sun.position.copy(dir).multiplyScalar(260);
  sun.color.copy(s.sun); sun.intensity=s.sunI;
  hemi.color.copy(s.top).lerp(s.hor,0.4); hemi.groundColor.setHex(0x5b5246).lerp(s.wat,0.5);
  hemi.intensity=s.amb; amb.intensity=0.08+s.amb*0.18;
  renderer.toneMappingExposure=s.exp;
  scene.fog.color.copy(s.fog);
  skyMat.uniforms.uTop.value.copy(s.top);
  skyMat.uniforms.uHor.value.copy(s.hor);
  skyMat.uniforms.uSunC.value.copy(s.sun);
  skyMat.uniforms.uSunDir.value.copy(dir);
  skyMat.uniforms.uHaze.value=s.haze;
  farSea.material.color.copy(s.wat).lerp(s.fog,0.55);
  farLand.material.color.setHex(0x74835a).lerp(s.fog,0.45);
  U.glow.value=s.glow*(0.94+0.06*Math.sin(clock.getElapsedTime()*3.3));
  beamMat.opacity=clamp(s.glow*0.11,0,0.12);
  beamMat.visible=s.glow>0.12;
  const hh=Math.floor(5+t*15), mm=Math.floor(((5+t*15)%1)*60);
  document.getElementById('vHour').textContent=String(hh).padStart(2,'0')+':'+String(Math.round(mm/15)*15%60).padStart(2,'0');
}

/* ═══════════════════════ UI ═══════════════════════ */
const PRESETS=[
  {p:[69,39,-56], t:[-2,10,8],   spd:0.26},
  {p:[26,19,-36], t:[8,13,32],   spd:0.16},
  {p:[16,52,-28], t:[-12,26,0],  spd:0.34},
  {p:[86,34,78],  t:[44,26,37],  spd:0.20},
  {p:[-44,26,-52],t:[-13,10,14], spd:0.22}
];
const fly={active:false,t:0,dur:1.7,fromP:new THREE.Vector3(),fromT:new THREE.Vector3(),toP:new THREE.Vector3(),toT:new THREE.Vector3()};
function flyTo(i){
  const pr=PRESETS[i];
  fly.fromP.copy(camera.position); fly.fromT.copy(controls.target);
  fly.toP.set(...pr.p); fly.toT.set(...pr.t);
  fly.t=0; fly.active=true; controls.autoRotate=false;
  controls.minDistance=1;
  document.getElementById('sOrbit')?.classList.remove('on');
}
document.querySelectorAll('#cams button').forEach((btn,i)=>btn.addEventListener('click',()=>{
  document.querySelectorAll('#cams button').forEach(b=>b.classList.remove('on'));
  btn.classList.add('on'); flyTo(i);
}));
const sHour=document.getElementById('sHour');
sHour.addEventListener('input',()=>applyTime(parseFloat(sHour.value)));
const sSwell=document.getElementById('sSwell');
sSwell.addEventListener('input',()=>{
  const s=parseFloat(sSwell.value);
  U.ampN.value=0.34*s; U.ampF.value=0.55*s; U.stepN.value=0.34*Math.max(0.75,s*0.85);
  document.getElementById('vSwell').textContent=s<0.6?'glassy':s<1.1?'moderate':s<1.7?'lively':'heavy';
});
const bOrbit=document.createElement('button');
bOrbit.id='sOrbit'; bOrbit.className='on'; bOrbit.textContent='Drift ⬤';
document.getElementById('bOrbit').replaceWith(bOrbit);
bOrbit.addEventListener('click',()=>{
  controls.autoRotate=!controls.autoRotate;
  bOrbit.classList.toggle('on',controls.autoRotate);
});
const ui=document.getElementById('ui');
document.getElementById('bHide').addEventListener('click',()=>ui.classList.add('hidden'));
window.addEventListener('keydown',e=>{
  if(e.key==='h'||e.key==='H') ui.classList.toggle('hidden');
  const n=parseInt(e.key); if(n>=1&&n<=5) document.querySelector(`#cams button[data-c="${n-1}"]`)?.click();
});

/* ═══════════════════════ loop ═══════════════════════ */
const clock=new THREE.Clock();
applyTime(parseFloat(sHour.value));

function tick(){
  const dt=Math.min(0.05,clock.getDelta()), t=clock.elapsedTime;
  U.time.value=t;
  applyTime(parseFloat(sHour.value));

  /* hull rocking on the swell */
  const sw=clamp(parseFloat(sSwell.value),0.15,2.2);
  shipGroup.rotation.z=Math.sin(t*0.55)*0.018*sw+Math.sin(t*0.31+1.7)*0.011*sw;
  shipGroup.rotation.x=Math.sin(t*0.43+0.6)*0.012*sw;
  shipGroup.position.y=Math.sin(t*0.8)*0.14*sw+0.02;
  shipGroup.position.x=-13+Math.sin(t*0.27)*0.1;
  shipGroup.updateMatrixWorld(true);

  for(const u of updaters) u();
  gang.lookAt(shipGroup.localToWorld(new THREE.Vector3(6.2,8,10)));

  mill.rotation.z-=dt*0.42;
  beams.rotation.y+=dt*0.55;
  cloudGrp.rotation.y+=dt*0.0035;

  boat1.position.y=0.4+Math.sin(t*1.1)*0.22*sw;
  boat1.rotation.x=Math.sin(t*0.9)*0.06*sw; boat1.rotation.z=Math.cos(t*1.3)*0.05*sw;
  boat2.position.y=0.4+Math.sin(t*1.05+2)*0.24*sw;
  boat2.rotation.z=Math.cos(t*1.2+1)*0.06*sw;
  boat2.rotation.x=Math.sin(t*0.8+2)*0.05*sw;
  if(boat2.userData.oars){
    const o=Math.sin(t*2.2)*0.35;
    boat2.userData.oars[0].rotation.z=0.55+o; boat2.userData.oars[1].rotation.z=0.55-o;
  }

  for(const g of gulls){
    const u=g.userData, a=t*u.spd+u.ph;
    g.position.set(Math.cos(a)*u.r,u.y+Math.sin(a*2.3+u.ph)*2.2,Math.sin(a)*u.r);
    g.rotation.y=-a+Math.PI/2;
    g.rotation.z=-0.25*Math.sin(a);
    const f=Math.sin(t*8+u.ph)*0.55;
    u.lw.rotation.z=f; u.rw.rotation.z=-f;
  }

  /* camera fly */
  if(fly.active){
    fly.t+=dt/fly.dur;
    const e=fly.t>=1?1:(1-Math.pow(1-fly.t,3));
    camera.position.lerpVectors(fly.fromP,fly.toP,e);
    controls.target.lerpVectors(fly.fromT,fly.toT,e);
    if(fly.t>=1){ fly.active=false; controls.autoRotate=bOrbit.classList.contains('on');
      controls.minDistance=30; }
  }
  controls.update();
  renderer.render(scene,camera);
}
renderer.setAnimationLoop(tick);

window.addEventListener('resize',()=>{
  camera.aspect=innerWidth/innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight);
});

/* boot fade after the first rendered frame */
requestAnimationFrame(()=>requestAnimationFrame(()=>document.getElementById('boot').classList.add('gone')));
</script>
</body>
</html>
```

**What's in the water and on it**

- **The frigate** (~46 voxels long) is generated from a hull profile + longitudinal sheer, so she gets rounded bow ends, a flat transom, tumble‑home, a checkered gun‑deck course, gunports, a lit stern gallery, bowsprit, figurehead, capstan, wheel, hatches, deckers and a mix of **short canvas** — full courses and an upper topsail, the rest furred into rolls on the yards. Three jibs + a spanker are rasterized from triangles with a belly bulge; the rigging is ~120 fine lines over the chunky forms.
- **The harbor** grew out of a single voxel map: a granite quay with paving and bollards, warehouses with shadowed doors, gabled townhouses, a church with a lit clock, market stalls, trees, a lamp‑lit pier with planking pilings, coiled rope, crates, barrels, sacks, sailors, a gangway that **swings itself onto the rail every frame**, and a stepped lighthouse on a stone breakwater with a sweeping beam.
- **Motion:** the sea is instanced columns displaced (and quantized) in the vertex shader, with crest‑foam and dark troughs computed from the same wave value — so you get stepped voxel swells with correct flat normals. The ship rocks, shears and drifts on that swell; the foam ring, hawsers and gangway follow. Plus windmill sails, oars, drifting cloud banks, eight circling gulls and flickering lamps.
- **Sun slider** rekeys the sky shader, fog, light color/intensity, exposure, water tint, lamp/window glow and lighthouse beam. `H` hides the panel; `1‑5` jump between camera studies.