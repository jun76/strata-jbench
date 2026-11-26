**Calling at the Harbour** — a single-file voxel diorama. Everything (about 40k blocks) is generated procedurally at load, batched into a handful of instanced meshes, and animated on the GPU where it matters.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Calling at the Harbour — a voxel diorama</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,600;0,9..144,900;1,9..144,600&family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root{
    --ink:#080b10; --panel:#101621; --panel2:#0c1219; --line:#2a3546;
    --brass:#d6a44c; --brass-dim:#8a7345; --paper:#ece3d0; --muted:#8fa0b5;
    --teal:#5fbfd4;
  }
  *{box-sizing:border-box;margin:0;padding:0}
  html,body{height:100%;overflow:hidden;background:var(--ink);color:var(--paper);
    font-family:"IBM Plex Sans",system-ui,sans-serif;-webkit-font-smoothing:antialiased}
  canvas{display:block;position:fixed;inset:0;cursor:grab}
  canvas:active{cursor:grabbing}

  .vig{position:fixed;inset:0;pointer-events:none;z-index:2;
    background:radial-gradient(120% 85% at 50% 42%,transparent 42%,rgba(4,6,10,.55) 100%);}
  .vig:after{content:"";position:absolute;inset:0;opacity:.22;mix-blend-mode:overlay;
    background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3'/%3E%3C/filter%3E%3Crect width='140' height='140' filter='url(%23n)' opacity='.5'/%3E%3C/svg%3E")}

  /* ---------- plaque ---------- */
  .plaque{position:fixed;left:34px;top:30px;z-index:4;max-width:39ch;pointer-events:none}
  .kicker{display:flex;align-items:center;gap:10px;font:500 10px/1 "IBM Plex Mono",monospace;
    letter-spacing:.34em;text-transform:uppercase;color:var(--brass);opacity:0;
    animation:rise .8s .15s cubic-bezier(.2,.8,.3,1) forwards}
  .kicker i{display:block;width:38px;height:1px;background:var(--brass);opacity:.6}
  h1{font-family:"Fraunces",serif;font-weight:900;font-size:clamp(2.5rem,4.4vw,4.3rem);
    line-height:.9;letter-spacing:-.025em;margin:.28em 0 .3em;text-shadow:0 12px 34px rgba(0,0,0,.6);
    opacity:0;animation:rise .9s .3s cubic-bezier(.2,.8,.3,1) forwards}
  h1 em{font-style:italic;font-weight:600;color:#f0c987;display:inline-block}
  .blurb{font-weight:300;font-size:14.5px;line-height:1.6;color:#a9bacd;max-width:33ch;
    opacity:0;animation:rise .9s .45s cubic-bezier(.2,.8,.3,1) forwards}
  .rule{width:64px;height:2px;background:linear-gradient(90deg,var(--brass),transparent);margin-top:16px;
    opacity:0;animation:rise .9s .55s cubic-bezier(.2,.8,.3,1) forwards}
  @keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}

  /* ---------- coords strip ---------- */
  .strip{position:fixed;right:26px;top:34px;z-index:4;text-align:right;pointer-events:none;
    font:400 10px/1.9 "IBM Plex Mono",monospace;letter-spacing:.18em;color:#6f8296;
    opacity:0;animation:rise .9s .7s forwards}
  .strip b{color:var(--brass-dim);font-weight:500}

  /* ---------- console ---------- */
  .console{position:fixed;right:26px;bottom:26px;z-index:5;width:302px;padding:18px 18px 15px;
    background:linear-gradient(180deg,rgba(19,26,37,.96),rgba(11,16,23,.96));
    border:1px solid var(--line);border-top:2px solid var(--brass);
    box-shadow:0 26px 60px -20px rgba(0,0,0,.85),inset 0 1px 0 rgba(255,255,255,.05);
    transform:translateY(18px);opacity:0;animation:rise .9s .6s cubic-bezier(.2,.8,.3,1) forwards}
  .console h2{font:500 9.5px/1 "IBM Plex Mono",monospace;letter-spacing:.3em;text-transform:uppercase;
    color:var(--brass);margin-bottom:14px;display:flex;justify-content:space-between;align-items:center}
  .console h2 span{color:#5c6c80;letter-spacing:.12em}
  .row{display:grid;grid-template-columns:1fr auto;align-items:center;gap:6px;margin-bottom:4px}
  .row label{font:400 10px/1 "IBM Plex Mono",monospace;letter-spacing:.2em;color:#8095ab;text-transform:uppercase}
  .row output{font:500 11.5px/1 "IBM Plex Mono",monospace;color:var(--paper);letter-spacing:.04em}
  input[type=range]{-webkit-appearance:none;appearance:none;width:100%;height:22px;background:transparent;
    margin:0 0 13px;cursor:ew-resize;grid-column:1/-1}
  input[type=range]::-webkit-slider-runnable-track{height:3px;border-radius:2px;
    background:linear-gradient(90deg,#2a3444,#3d4c62)}
  input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:14px;height:14px;margin-top:-5.5px;
    border-radius:50%;background:var(--brass);border:2px solid #14202c;
    box-shadow:0 0 0 0 rgba(214,164,76,.35);transition:box-shadow .18s,transform .18s}
  input[type=range]:hover::-webkit-slider-thumb{box-shadow:0 0 0 6px rgba(214,164,76,.16);transform:scale(1.12)}
  input[type=range]:active::-webkit-slider-thumb{box-shadow:0 0 0 9px rgba(214,164,76,.22)}
  input[type=range]::-moz-range-track{height:3px;background:#2a3444;border-radius:2px}
  input[type=range]::-moz-range-thumb{width:13px;height:13px;border:2px solid #14202c;border-radius:50%;background:var(--brass)}
  .btns{display:flex;flex-wrap:wrap;gap:6px;margin:2px 0 13px}
  button{font:500 9.5px/1 "IBM Plex Mono",monospace;letter-spacing:.14em;text-transform:uppercase;
    color:#9fb2c6;background:#151d28;border:1px solid #27323f;padding:8px 9px;cursor:pointer;
    transition:all .18s cubic-bezier(.2,.8,.3,1)}
  button:hover{color:#0c1219;background:var(--brass);border-color:var(--brass);transform:translateY(-1px)}
  button.on{background:#1d2b34;border-color:#3d6b6a;color:var(--teal)}
  button.on:hover{background:var(--teal);color:#08131a}
  .meta{border-top:1px solid var(--line);padding-top:11px;display:flex;justify-content:space-between;
    font:400 9.5px/1 "IBM Plex Mono",monospace;letter-spacing:.16em;color:#5d6e82;text-transform:uppercase}
  .meta b{color:#9fb2c6;font-weight:500}

  .hint{position:fixed;left:34px;bottom:28px;z-index:4;font:400 10px/1.8 "IBM Plex Mono",monospace;
    letter-spacing:.16em;color:#5b6c80;text-transform:uppercase;pointer-events:none;
    opacity:0;animation:rise .9s .85s forwards}
  .hint kbd{color:var(--brass-dim)}

  /* ---------- landmark tag ---------- */
  .tag{position:fixed;left:0;top:0;z-index:6;width:268px;padding:14px 16px 13px;pointer-events:none;
    background:linear-gradient(180deg,rgba(20,27,38,.97),rgba(12,17,25,.97));
    border:1px solid #32415a;border-left:3px solid var(--brass);
    box-shadow:0 20px 44px -14px rgba(0,0,0,.85);
    opacity:0;transform:translate(-50%,-118%) scale(.92);transition:opacity .22s,transform .34s cubic-bezier(.16,1.1,.3,1)}
  .tag.show{opacity:1;transform:translate(-50%,-118%) scale(1)}
  .tag .t-k{font:500 9px/1 "IBM Plex Mono",monospace;letter-spacing:.26em;color:var(--brass);text-transform:uppercase}
  .tag .t-n{font-family:"Fraunces",serif;font-weight:600;font-size:20px;line-height:1.12;margin:8px 0 7px;letter-spacing:-.01em}
  .tag .t-d{font-weight:300;font-size:12.5px;line-height:1.55;color:#9fb0c4}
  .tag .t-c{margin-top:10px;padding-top:9px;border-top:1px solid #232e3d;
    font:400 9px/1 "IBM Plex Mono",monospace;letter-spacing:.16em;color:#586a7e;display:flex;justify-content:space-between}

  /* ---------- loader ---------- */
  #loader{position:fixed;inset:0;z-index:9;display:grid;place-items:center;background:#080b10;
    transition:opacity .8s ease;text-align:center}
  #loader.gone{opacity:0;pointer-events:none}
  #loader .l1{font:500 10px/1 "IBM Plex Mono",monospace;letter-spacing:.4em;color:var(--brass);text-transform:uppercase}
  #loader .l2{margin-top:18px;width:180px;height:1px;background:#1d2733;overflow:hidden}
  #loader .l2 i{display:block;height:100%;width:36%;background:var(--brass);animation:sweep 1.15s infinite cubic-bezier(.6,0,.4,1)}
  #loader p{margin-top:16px;font-weight:300;font-size:12px;color:#5b6c80;max-width:26ch;line-height:1.6}
  @keyframes sweep{0%{transform:translateX(-110%)}100%{transform:translateX(320%)}}
  .dots::after{content:"";animation:dots 1.2s steps(4,end) infinite}
  @keyframes dots{0%{content:""}25%{content:"."}50%{content:".."}75%{content:"..."}}
  @media (max-width:760px){.plaque{left:18px;top:18px}.console{right:12px;bottom:12px;width:262px}
    .hint{display:none}.strip{display:none}}
</style>
</head>
<body>
<div class="vig"></div>

<header class="plaque">
  <div class="kicker"><i></i>Voxel diorama · no. 03</div>
  <h1>Calling at<br>the <em>Harbour</em></h1>
  <p class="blurb">A barque comes in on the evening tide — topsails still sheeted, colours running up
     the rigging, and the whole quay leaning in to watch her tie up.</p>
  <div class="rule"></div>
</header>

<div class="strip">
  50°22′47″<b>N</b> &nbsp; 04°07′12″<b>W</b><br>
  FLOOD <b>+2.4 m</b> &nbsp; WIND <b id="wnd">SSW 3</b><br>
  ANCHORAGE <b>GOOD HOLDING</b>
</div>

<aside class="console">
  <h2>Watch Console <span id="stateTxt">Clear</span></h2>
  <div class="row"><label>Hour of day</label><output id="hourOut">18:05</output></div>
  <input id="hour" type="range" min="5" max="20.5" step="0.05" value="18.05">
  <div class="row"><label>Sea state</label><output id="seaOut">Slight</output></div>
  <input id="sea" type="range" min="0" max="1" step="0.01" value="0.42">
  <div class="btns">
    <button data-h="5.25">Dawn</button>
    <button data-h="12.6">Noon</button>
    <button data-h="18.05" class="on">Golden</button>
    <button data-h="20.3">Blue hour</button>
  </div>
  <div class="btns">
    <button id="orbit" class="on">Auto‑orbit</button>
    <button id="reset">Reset view</button>
  </div>
  <div class="meta"><span>Blocks <b id="blocks">—</b></span><span>FPS <b id="fps">60</b></span></div>
</aside>

<div class="hint"><kbd>drag</kbd> orbit &nbsp;·&nbsp; <kbd>scroll</kbd> zoom &nbsp;·&nbsp; <kbd>right‑drag</kbd> pan &nbsp;·&nbsp; <kbd>click</kbd> read a plaque</div>
<div class="tag" id="tag"></div>

<div id="loader">
  <div>
    <div class="l1">Charting the approach</div>
    <div class="l2"><i></i></div>
    <p class="dots">Cutting blocks from granite, fir and canvas</p>
  </div>
</div>

<script>window.__ok=false;setTimeout(function(){if(!window.__ok){var d=document.querySelector('#loader p');if(d){d.style.color='#c98a5a';d.textContent='This scene streams three.js from a CDN — reconnect and reload to build the harbour.';}}},9000);</script>

<script type="importmap">
{"imports":{
  "three":"https://cdn.jsdelivr.net/npm/three@0.161.0/build/three.module.js",
  "three/addons/":"https://cdn.jsdelivr.net/npm/three@0.161.0/examples/jsm/"
}}
</script>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* ============================================================
   1 · UTILITIES
   ============================================================ */
const clamp=(v,a,b)=>v<a?a:v>b?b:v;
const lerp=(a,b,t)=>a+(b-a)*t;
function hash3(x,y,z){
  let h=Math.imul(x|0,374761393)+Math.imul(y|0,668265263)+Math.imul(z|0,1274126177);
  h=Math.imul(h^(h>>>13),1274126177); h^=h>>>16;
  return (h>>>0)/4294967296;
}
const _c=new THREE.Color();
function j(hex,amt,x,y,z){ _c.setHex(hex); _c.offsetHSL(0,(hash3(x,y,z)-.5)*.05,(hash3(x,y+7,z)-.5)*amt); return _c.getHex(); }
function interp(t,pts){
  if(t<=pts[0][0])return pts[0][1];
  for(let i=1;i<pts.length;i++){ if(t<=pts[i][0]){const a=pts[i-1],b=pts[i];return lerp(a[1],b[1],(t-a[0])/(b[0]-a[0]));} }
  return pts[pts.length-1][1];
}

/* ============================================================
   2 · VOXEL SET  (insertion order preserved, hidden blocks culled)
   ============================================================ */
class VSet{
  constructor(){ this.map=new Map(); this.gid=0; this.groups=[]; }
  pick(name,blurb){ this.gid=this.groups.length+1; this.groups.push({gid:this.gid,name,blurb}); return this; }
  nop(){ this.gid=0; }
  put(x,y,z,c){
    x=Math.round(x); y=Math.round(y); z=Math.round(z);
    const k=x+'|'+y+'|'+z;
    const e=this.map.get(k);
    if(e) e.c=c; else this.map.set(k,{c:c|0,g:this.gid});
  }
  box(x0,x1,y0,y1,z0,z1,c,jit=0){
    for(let x=Math.round(x0);x<=Math.round(x1);x++)
    for(let y=Math.round(y0);y<=Math.round(y1);y++)
    for(let z=Math.round(z0);z<=Math.round(z1);z++)
      this.put(x,y,z,jit?j(c,jit,x,y,z):c);
  }
  shell(x0,x1,y0,y1,z0,z1,c,jit=0){
    for(let x=Math.round(x0);x<=Math.round(x1);x++)
    for(let y=Math.round(y0);y<=Math.round(y1);y++)
    for(let z=Math.round(z0);z<=Math.round(z1);z++){
      const e=(x===Math.round(x0)||x===Math.round(x1)||y===Math.round(y0)||y===Math.round(y1)||z===Math.round(z0)||z===Math.round(z1));
      if(e) this.put(x,y,z,jit?j(c,jit,x,y,z):c);
    }
  }
  disc(cx,cz,y,r,c,flat=true,jit=0){
    for(let x=Math.ceil(cx-r);x<=Math.floor(cx+r);x++)
    for(let z=Math.ceil(cz-r);z<=Math.floor(cz+r);z++){
      const dx=x-cx,dz=z-cz;
      if(dx*dx+dz*dz<=r*r+.4){ this.put(x,y,z,jit?j(c,jit,x,y,z):c); if(flat)this.put(x,y+1,z,jit?j(c,jit,x,y+1,z):c); }
    }
  }
  line(p0,p1,c,g){
    const d=new THREE.Vector3().subVectors(p1,p0);
    const n=Math.max(1,Math.ceil(Math.max(Math.abs(d.x),Math.abs(d.y),Math.abs(d.z))));
    for(let i=0;i<=n;i++){ const t=i/n;
      this.put(lerp(p0.x,p1.x,t),lerp(p0.y,p1.y,t),lerp(p0.z,p1.z,t), typeof c==='function'?c(t):c); }
    return this;
  }
}

function toMesh(vs,material,{cast=true,receive=true,boxSize=1}={}){
  const data=[];
  for(const [k,v] of vs.map){
    const p=k.split('|'), x=+p[0], y=+p[1], z=+p[2];
    if(vs.map.has((x+1)+'|'+y+'|'+z)&&vs.map.has((x-1)+'|'+y+'|'+z)&&
       vs.map.has(x+'|'+(y+1)+'|'+z)&&vs.map.has(x+'|'+(y-1)+'|'+z)&&
       vs.map.has(x+'|'+y+'|'+(z+1))&&vs.map.has(x+'|'+y+'|'+(z-1))) continue;
    data.push(x,y,z,v.c,v.g);
  }
  const n=data.length;
  const geo=new THREE.BoxGeometry(boxSize,boxSize,boxSize);
  const mesh=new THREE.InstancedMesh(geo,material,n);
  const m=new THREE.Matrix4(), col=new THREE.Color();
  const bounds=new Map();
  const base=new Float32Array(n*3);
  for(let i=0;i<n;i++){
    const x=data[i*5],y=data[i*5+1],z=data[i*5+2],c=data[i*5+3],g=data[i*5+4];
    m.makeTranslation(x,y,z); mesh.setMatrixAt(i,m);
    col.setHex(c); mesh.setColorAt(i,col);
    base[i*3]=col.r;base[i*3+1]=col.g;base[i*3+2]=col.b;
    let b=bounds.get(g);
    if(!b){b={x0:x,y0:y,z0:z,x1:x,y1:y,z1:z};bounds.set(g,b);}
    else{b.x0=Math.min(b.x0,x);b.y0=Math.min(b.y0,y);b.z0=Math.min(b.z0,z);
         b.x1=Math.max(b.x1,x);b.y1=Math.max(b.y1,y);b.z1=Math.max(b.z1,z);}
  }
  mesh.instanceMatrix.needsUpdate=true;
  if(mesh.instanceColor) mesh.instanceColor.needsUpdate=true;
  mesh.castShadow=cast; mesh.receiveShadow=receive;
  mesh.userData={bounds,base,count:n};
  return mesh;
}

/* ============================================================
   3 · RENDERER / SCENE
   ============================================================ */
const renderer=new THREE.WebGLRenderer({antialias:true,powerPreference:'high-performance'});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.setSize(innerWidth,innerHeight);
renderer.shadowMap.enabled=true;
renderer.shadowMap.type=THREE.PCFSoftShadowMap;
renderer.shadowMap.autoUpdate=false;
renderer.toneMapping=THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure=1.0;
document.body.appendChild(renderer.domElement);

const scene=new THREE.Scene();
scene.fog=new THREE.Fog(0x9fb3c6,120,430);

const camera=new THREE.PerspectiveCamera(42,innerWidth/innerHeight,0.6,4000);
const DEF_POS=new THREE.Vector3(64,30,72), DEF_TGT=new THREE.Vector3(-2,8,-6);
camera.position.copy(DEF_POS).multiplyScalar(1.85);

const controls=new OrbitControls(camera,renderer.domElement);
controls.enableDamping=true; controls.dampingFactor=.055;
controls.target.copy(DEF_TGT);
controls.minDistance=22; controls.maxDistance=175;
controls.maxPolarAngle=Math.PI*.493; controls.minPolarAngle=.1;
controls.autoRotate=true; controls.autoRotateSpeed=.32;
controls.panSpeed=.6; controls.rotateSpeed=.75;

/* lights */
const sun=new THREE.DirectionalLight(0xffffff,2.2);
sun.castShadow=true;
sun.shadow.mapSize.set(2048,2048);
const sc=sun.shadow.camera; sc.left=-118; sc.right=118; sc.top=112; sc.bottom=-112; sc.near=1; sc.far=520;
sun.shadow.bias=-.0006; sun.shadow.normalBias=.6;
scene.add(sun,sun.target);
const hemi=new THREE.HemisphereLight(0x9fc0e0,0x36413a,.7); scene.add(hemi);
const amb=new THREE.AmbientLight(0xffffff,.12); scene.add(amb);
const lampTown=new THREE.PointLight(0xffb35c,0,90,2); lampTown.position.set(4,11,-34); scene.add(lampTown);
const lampLight=new THREE.PointLight(0xa8dcff,0,120,2); lampLight.position.set(-38,28,17); scene.add(lampLight);

/* sky */
const skyU={
  uTop:{value:new THREE.Color(0x2f6ea8)}, uHor:{value:new THREE.Color(0xd8e6ef)},
  uSunCol:{value:new THREE.Color(0xfff2d4)}, uSun:{value:new THREE.Vector3(0,1,0)}
};
const skyMat=new THREE.ShaderMaterial({
  side:THREE.BackSide,depthWrite:false,fog:false,uniforms:skyU,
  vertexShader:`varying vec3 vD;void main(){vD=position;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,
  fragmentShader:`
    varying vec3 vD; uniform vec3 uTop,uHor,uSunCol,uSun;
    void main(){
      vec3 d=normalize(vD);
      float h=clamp(d.y*1.18,0.,1.);
      vec3 col=mix(uHor,uTop,pow(h,.52));
      float sd=max(dot(d,normalize(uSun)),0.);
      col+=uSunCol*pow(sd,5.5)*.32;
      col+=uSunCol*pow(sd,320.)*2.6;
      col=mix(col,uHor*1.12,smoothstep(.075,0.,abs(d.y)));
      col+=uSunCol*0.06*pow(max(0.,1.-abs(d.y)*4.),3.);
      gl_FragColor=vec4(col,1.);
      #include <tonemapping_fragment>
      #include <colorspace_fragment>
    }`
});
scene.add(new THREE.Mesh(new THREE.SphereGeometry(1400,26,18),skyMat));

/* deep-water horizon plane */
const horizonMat=new THREE.MeshBasicMaterial({color:0x184a5f});
const horizon=new THREE.Mesh(new THREE.PlaneGeometry(6000,6000),horizonMat);
horizon.rotation.x=-Math.PI/2; horizon.position.y=-3.2; scene.add(horizon);

/* ============================================================
   4 · WATER (instanced blocks, GPU waves)
   ============================================================ */
const U={ time:{value:0}, amp:{value:.55}, deep:{value:new THREE.Color(0x0e3f56)},
          shal:{value:new THREE.Color(0x2f93a8)}, sunSpec:{value:new THREE.Color(0xffe9c4)} };
const waterMat=new THREE.MeshPhongMaterial({color:0xffffff,specular:0xffffff,shininess:38});
waterMat.onBeforeCompile=(sh)=>{
  sh.uniforms.uTime=U.time; sh.uniforms.uAmp=U.amp; sh.uniforms.uDeep=U.deep;
  sh.uniforms.uShallow=U.shal; sh.uniforms.uSpec=U.sunSpec;
  sh.vertexShader=`
    uniform float uTime,uAmp; varying float vW; varying vec3 vWP;
    float wv(vec2 p,float t){
      float h = sin(p.x*0.13+t*0.90)*0.55
              + sin(p.y*0.185-t*1.15)*0.45
              + sin((p.x+p.y)*0.085+t*0.62)*0.42
              + sin((p.x*0.31-p.y*0.22)+t*1.70)*0.17
              + sin((p.x*0.052+p.y*0.041)-t*0.31)*0.70;
      return h*uAmp;
    }`+sh.vertexShader
    .replace('#include <beginnormal_vertex>',`
      vec3 ipos=vec3(instanceMatrix[3][0],instanceMatrix[3][1],instanceMatrix[3][2]);
      float w_=wv(ipos.xz,uTime);
      float ex=wv(ipos.xz+vec2(1.5,0.0),uTime)-w_;
      float ez=wv(ipos.xz+vec2(0.0,1.5),uTime)-w_;
      vec3 objectNormal=normalize(vec3(-ex*1.15,1.0,-ez*1.15));`)
    .replace('#include <begin_vertex>',`
      vec3 transformed=vec3(position);
      transformed.y+=w_; vW=w_; vWP=ipos.xz;`);
  sh.fragmentShader=`varying float vW; varying vec3 vWP;
    uniform vec3 uDeep,uShallow,uSpec; uniform float uAmp;`+sh.fragmentShader
    .replace('#include <color_fragment>',`
      float h=clamp(vW/max(uAmp*1.95,.001)*0.5+0.5,0.,1.);
      vec3 wc=mix(uDeep,uShallow,smoothstep(0.05,0.95,h));
      wc=mix(wc,vec3(0.86,0.96,1.0),smoothstep(0.80,1.0,h)*0.75);
      float rip=sin(vWP.x*1.7+vWP.y*1.2)*0.5+0.5;
      wc=mix(wc,wc*1.10,rip*0.35);
      diffuseColor.rgb*=wc;`)
    .replace('#include <specularmap_fragment>',`
      diffuseColor.rgb*=1.0;`);
};
const waterCells=[];
for(let z=-16;z<200;z+=2) for(let x=-150;x<150;x+=2){
  if(x>=-88&&x<88&&z>=-16&&z<88){
    for(const dz of [0,1]) for(const dx of [0,1]) waterCells.push([x+dx,z+dz,1]);
  } else waterCells.push([x,z,2]);
}
const wgeo=new THREE.BoxGeometry(1,14,1); wgeo.translate(0,-7,0);
const water=new THREE.InstancedMesh(wgeo,waterMat,waterCells.length);
{
  const m=new THREE.Matrix4(), q=new THREE.Quaternion(), s=new THREE.Vector3(), p=new THREE.Vector3();
  waterCells.forEach((c,i)=>{
    p.set(c[0]+c[2]/2,0,c[1]+c[2]/2); s.set(c[2],1,c[2]);
    m.compose(p,q,s); water.setMatrixAt(i,m);
  });
  water.instanceMatrix.needsUpdate=true;
}
water.receiveShadow=true; water.castShadow=false; scene.add(water);

/* ============================================================
   5 · MATERIALS for blocks
   ============================================================ */
const matWorld=new THREE.MeshLambertMaterial({color:0xffffff});
const matGlow =new THREE.MeshBasicMaterial({color:0xffffff});
const glowMeshes=[];
const pickables=[];
function addProxies(vs,mesh,parent,skip=new Set()){
  for(const g of vs.groups){
    if(skip.has(g.gid))continue;
    const b=mesh.userData.bounds.get(g.gid); if(!b)continue;
    const sx=b.x1-b.x0+3, sy=b.y1-b.y0+3, sz=b.z1-b.z0+3;
    if(sx*sy*sz>90000||sx*sy*sz<8) continue;
    const pm=new THREE.Mesh(new THREE.BoxGeometry(sx,sy,sz),new THREE.MeshBasicMaterial({visible:false}));
    pm.position.set((b.x0+b.x1)/2,(b.y0+b.y1)/2,(b.z0+b.z1)/2);
    pm.userData.info=g; parent.add(pm); pickables.push(pm);
  }
}
function registerGlow(mesh){ glowMeshes.push(mesh); }

/* flag flutter material */
const flagMat=new THREE.MeshLambertMaterial({color:0xffffff,side:THREE.DoubleSide});
flagMat.onBeforeCompile=(sh)=>{
  sh.uniforms.uTime=U.time;
  sh.vertexShader=`uniform float uTime;`+sh.vertexShader.replace('#include <begin_vertex>',`
    vec3 transformed=vec3(position);
    vec3 ip=vec3(instanceMatrix[3][0],instanceMatrix[3][1],instanceMatrix[3][2]);
    float f=ip.x+position.x;
    float a=min(f*0.16,1.35);
    transformed.y+=sin(f*1.05-uTime*4.6)*a;
    transformed.z+=sin(f*0.8-uTime*3.1)*a*0.6;
    transformed.x-=a*0.25;`);
};

/* ============================================================
   6 · THE HARBOUR
   ============================================================ */
function buildHarbour(){
  const v=new VSet(), g=new VSet();
  const stone=0x6d727a, stone2=0x61666d;

  /* ---- QUAY ---- */
  v.pick('The Long Quay','Dartmoor granite, laid 1861. Six hundred feet of it, and every morning the tide sweeps the seaward row.')
  for(let x=-70;x<=70;x++)for(let z=-40;z<=-16;z++){
    const h=hash3(x,11,z); let c=[0x747a81,0x6a7076,0x7c8188,0x646a70][(h*4)|0];
    if(z<=-19&&z>=-23) c=[0x8a7a5f,0x93836a,0x7e7059][(h*3)|0];      // slipway strip
    v.put(x,4,z,j(c,.16,x,4,z));
  }
  for(let x=-70;x<=70;x++) v.put(x,5,-16,j(0x99917c,.14,x,5,-16));  // coping
  for(let x=-70;x<=70;x++)for(let y=-7;y<=4;y++)for(let z=-16;z>=-18;z--){
    let c=((x+y*3)%4===0)?stone2:stone;
    if(y<=0) c=0x38474b;
    v.put(x,y,z,j(c,.2,x,y,z));
  }
  for(let x=-70;x<=70;x+=17) for(let y=-4;y<=1;y++) v.put(x,y,-16,j(0x2e3d40,.2,x,y,-16)); // weed line
  for(let i=0;i<7;i++){const bx=-66+i*22; v.put(bx,6,-16,0x3a3f47); v.put(bx,7,-16,0x2f343b);} // rings

  /* ---- LAND ---- */
  v.pick(false);
  for(let x=-90;x<=90;x++)for(let z=-84;z<=-41;z++){
    const h=hash3(x,3,z); let c=[0x4f7a45,0x59854d,0x486e3f][(h*3)|0];
    if(z>-46) c=0x6f6656;
    if(Math.abs(x+2)<3&&z<-46) c=[0x7b7163,0x71685b][(h*2)|0];       // cart road
    v.put(x,4,z,j(c,.18,x,4,z));
  }
  v.shell(-90,90,-3,3,-84,-41,0x4d4a44,.1);
  // back headland
  v.pick(false);
  for(let x=-140;x<=130;x+=2)for(let z=-160;z<=-120;z+=2){
    const h=hash3(x,9,z);
    const hh=Math.max(0, 14*Math.exp(-Math.pow((x+40)/95,2))*Math.exp(-Math.pow((z+142)/34,2)) + 10*Math.exp(-Math.pow((x-95)/70,2))*Math.exp(-Math.pow((z+150)/30,2)));
    for(let y=0;y<=hh;y+=2) v.put(x,y,z,j(0x3d5a55,.18,x,y,z));
  }

  /* ---- LIGHTHOUSE ---- */
  v.pick('The Light','First lit 1849. Twenty‑three seconds of dark between flashes — every skipper on this coast counts them.')
  g.pick(false);
  const LX=-38,LZ=17;
  v.box(LX-6,LX+6,-1,5,LZ-6,LZ+6,0x60564c,.16);
  v.box(LX-5,LX+5,5,6,LZ-5,LZ+5,0x544b43,.14);
  for(let y=6;y<=25;y++){
    const r=4.1-(y-6)*.062;
    const band=Math.floor((y-6)/5)%2===0;
    for(let dx=-5;dx<=5;dx++)for(let dz=-5;dz<=5;dz++){
      if(dx*dx+dz*dz<=r*r+.5){
        const c=band?j(0xece6da,.07,LX+dx,y,LZ+dz):j(0xb5442f,.09,LX+dx,y,LZ+dz);
        v.put(LX+dx,y,LZ+dz,c);
      }
    }
  }
  v.box(LX-5,LX+5,26,26,LZ-5,LZ+5,0x353b43,.1);
  for(let dx=-4;dx<=4;dx++)for(let dz=-4;dz<=4;dz++)
    if(dx*dx+dz*dz<=13){ g.put(LX+dx,27,LZ+dz,0xffe6ad); g.put(LX+dx,28,LZ+dz,0xfff3cf); }
  for(let a=0;a<8;a++){const ang=a/8*Math.PI*2; v.put(LX+Math.cos(ang)*4,29,LZ+Math.sin(ang)*4,0x2b3139);}
  for(let y=0;y<4;y++) v.box(LX-2+y,LX+2-y,29+y,29+y,LZ-2+y,LZ+2-y,0x30373f,.1);
  v.put(LX,33,LZ,0x2b3139); v.put(LX,34,LZ,0x8d949c);
  v.box(LX-9,LX-3,4,7,LZ+4,LZ+9,0xd9cfbd,.1);
  v.box(LX-9,LX-3,8,9,LZ+4,LZ+9,0x9d4f34,.14);
  for(let y=5;y<=6;y++){g.put(LX-6,y,LZ+9,0xffd28a);g.put(LX-4,y,LZ+9,0xffd28a);}

  /* ---- BREAKWATER ---- */
  v.pick('The Breakwater','Forty years of rejected blocks. It takes the swell on its shoulder so the berths stay flat.')
  for(let s=0;s<=1.02;s+=.045){
    const cx=lerp(-64,LX+2,s), cz=lerp(-12,LZ+3,s);
    const w=lerp(6.5,4.2,s);
    for(let i=-w;i<=w;i+=1){
      const px=Math.round(cx+i*1.15), pz=Math.round(cz+i*.28);
      const top=Math.round(lerp(3.2,5.4,s)+(hash3(px,5,pz)-.5)*2.4);
      for(let y=-5;y<=top;y++){
        const c=y>top-2?0x767b80:0x5d6268;
        v.put(px,y,Math.round(pz),j(c,.24,px,y,Math.round(pz)));
      }
    }
  }

  /* ---- CUSTOM HOUSE ---- */
  v.pick('The Custom House','Officers of the Revenue, 1861. The clock has been fast by four minutes ever since.')
  const CX0=-56,CX1=-30,CZ0=-60,CZ1=-46,CT=11;
  v.box(CX0,CX1,5,CT,CZ0,CZ1,j(0xd8cdb6,.1,CX0,5,CZ0));
  for(let x=CX0;x<=CX1;x++)for(let z=CZ0;z<=CZ1;z++){
    v.put(x,5,z,j(0x8c8478,.1,x,5,z));
    if(z===CZ1) for(let y=6;y<=7;y++) v.put(x,y,z,j(0x7c7468,.08,x,y,z)); // plinth
  }
  for(let i=0;i<=6;i++) v.box(CX0-1+i,CX1+1-i,CT+1+i,CT+1+i,CZ0-1,CZ1+1,j(i%2?0x414b5c:0x3a4453,.12,CX0+i,i,CZ0));
  for(let y=6;y<=10;y+=2)for(let x=CX0+2;x<=CX1-2;x+=4){
    g.put(x,y,CZ1,0xffd28a); g.put(x+1,y,CZ1,0xffd28a);
    g.put(x,y+1,CZ1,0xffc676); g.put(x+1,y+1,CZ1,0xffc676);
    v.put(x,y-1,CZ1,0x585049); v.put(x+1,y-1,CZ1,0x585049);
  }
  const KX=-34,KZ=-53;
  v.box(KX,KX+5,5,19,KZ,KZ+5,j(0xd8cdb6,.1,KX,5,KZ));
  for(let i=0;i<=3;i++) v.box(KX-1+i,KX+5-i,20+i,20+i,KZ-1+i,KZ+5-i,j(0x37414f,.1,KX,i,KZ));
  v.put(KX+2,24,KZ+2,0xd6a44c); v.put(KX+2,25,KZ+2,0xd6a44c);
  for(let dz=0;dz<=5;dz++)for(let y=14;y<=17;y++){
    const isHand=((dz===2||dz===3)&&(y===15||y===16));
    g.put(KX-1,y,KZ+dz,isHand?0x2b2f36:0xf3e6c6);
  }
  v.box(-29,-27,5,7,-45,-44,0x5b4a38,.1);

  /* ---- TOWNHOUSES ---- */
  v.pick('Tidewhalers’ Row','Three families, one shared well, and a running argument about who owns which gull.')
  const houses=[[ -26,-19,0xa1462f,0xd9c4a6],[ -18,-11,0x3f4d5c,0xe0d3bd],[ -10,-3,0x9c4a34,0xd2c2a4]];
  for(const [a,b,roof,wall] of houses){
    const h=8+((hash3(a,2,0)>0.5)?1:0);
    v.box(a,b,5,h,-58,-48,j(wall,.1,a,5,-58));
    v.box(a,b,5,6,-58,-48,j(0x9d9384,.1,a,5,-58));
    for(let i=0;i<=4;i++) v.box(a+i,b-1-i,h+1+i,h+1+i,-59,-47,j(roof,.16,a+i,i,-59));
    for(let y=7;y<=h-1;y+=3)for(let x=a+1;x<=b-1;x+=3){
      g.put(x,y,-58,0xffcf85); g.put(x,y+1,-58,0xffcf85);
      v.put(x,y-1,-58,0x54463a);
    }
    const dx=a+2; v.box(dx,dx+1,5,7,-48,-48,0x4a3626,.1);
    v.put((a+b)>>1,h+5,-53,0xd6a44c);
  }
  v.pick(false);
  for(let x=-27;x<=-2;x++) v.put(x,5,-45,j(0x8d8578,.1,x,5,-45));

  /* ---- BOND WAREHOUSE ---- */
  v.pick('Bonded Warehouse','Wool from the colonies, tea from Foochow, and six hundred casks of pine resin nobody has claimed.')
  const B0=4,B1=30,BZ0=-58,BZ1=-46;
  v.box(B0,B1,5,11,BZ0,BZ1,j(0x8f4b37,.14,B0,5,BZ0));
  v.box(B0,B1,5,6,BZ0,BZ1,j(0x6f3a2b,.12,B0,5,BZ0));
  for(let x=B0;x<=B1;x++){ v.put(x,12,x%2?BZ0:BZ1,0x3c4653); }
  for(let z=BZ0;z<=BZ1;z++){ v.box(B0-1,B1+1,12,12,z,z,0x3c4653,.08); }
  for(let i=0;i<=4;i++) v.box(B0+i,B1-i,13+i,13+i,BZ0+i,BZ1-i,0x37414d,.1);
  for(let x=B0+2;x<=B1-2;x+=4){
    v.box(x,x+1,8,8,BZ1,BZ1,0x4a3626,.1); v.box(x,x+1,9,10,BZ1,BZ1,0x4a3626,.1);
    g.put(x,10,BZ1,0xffc676);
    v.box(x,x+1,11,11,BZ1,BZ1,0x6b533a,.1);
    v.line(new THREE.Vector3(x+.5,11.5,BZ1+.5),new THREE.Vector3(x+.5,14,BZ1+.5),0x54402e);
  }
  v.box(B1+1,B1+3,5,9,BZ1-1,BZ1+1,0x757b83,.14); // stair tower
  for(let y=6;y<=8;y+=2) g.put(B1+2,y,BZ1+1,0xffd28a);

  /* ---- SAIL LOFT (on the quay) ---- */
  v.pick('The Sail Loft','Canvas, palm and palm‑wax. The sheets for tomorrow’s set are cut to the inch on this floor.')
  const S0=36,S1=54,SZ0=-34,SZ1=-24;
  v.box(S0,S1,5,9,SZ0,SZ1,j(0xc9b79a,.1,S0,5,SZ0));
  for(let i=0;i<=3;i++) v.box(S0-1+i,S1+1-i,10+i,10+i,SZ0-1+i,SZ1+1-i,j(i%2?0xa8492e:0x92402a,.14,S0,i,SZ0));
  v.box(S0+3,S0+11,5,8,SZ1,SZ1,0x33302c,.05);  // big open door
  v.box(S0+3,S0+11,8,8,SZ1,SZ1,0x24221f,.05);
  for(let z=SZ0+1;z<SZ1;z+=2) for(let y=5;y<=9;y++) v.put(S0+3,y,z,0x2a2724);
  for(let x=S0+3;x<=S0+11;x++) v.put(x,9,SZ1,0xe8dcc2);  // hanging sail header
  for(let x=S0+4;x<=S0+10;x+=2) for(let y=5;y<=8;y++) v.put(x,y,SZ1,j(0xf0e6d0,.06,x,y,SZ1));
  v.put(S0+2,10,SZ1,0xd6a44c);
  v.pick(false);
  for(let z=SZ0;z<=SZ1;z++)for(let x=S0;x<=S1;x++){ if((x+z)%6===0) v.put(x,5,z,j(0x8a7a5f,.14,x,5,z)); }

  /* ---- HARBOURMASTER'S COTTAGE ---- */
  v.pick('The Harbourmaster’s House','Ezekiel Crowe, forty‑one years on this foreshore. He still lights the beacon by hand.')
  const H0=-16,H1=-4,HZ0=-56,HZ1=-48;
  v.box(H0,H1,5,9,HZ0,HZ1,j(0xe3d7c0,.1,H0,5,HZ0));
  for(let i=0;i<=5;i++) v.box(H0-1+i,H1+1-i,10+i,10+i,HZ0-1,HZ1+1,j(i%2?0xa8492e:0x8f3f2b,.15,H0,i,HZ0));
  for(let y=7;y<=8;y++){g.put(H0+2,y,HZ1,0xffcf85);g.put(H0+6,y,HZ1,0xffcf85);}
  v.box(H0+3,H0+4,5,7,HZ1,HZ1,0x46331f,.1);
  v.box(H0+9,H0+10,5,8,HZ0+2,HZ0+2,0x9d5c3c,.1);
  v.box(H0+8,H0+11,13,13,HZ0+1,HZ0+3,0x6e4630,.12);
  v.pick(false);
  for(let x=-19;x<=-1;x++){ v.put(x,5,-46,j(0x6f6555,.14,x,5,-46)); if(x%5===0){v.put(x,6,-46,0x5b5347);v.put(x,7,-46,0x4a443b);} }
  for(let x=-18;x<=-2;x+=4) tree(v,x,5,-52,.8+hash3(x,0,0)*.5);

  /* ---- FISH MARKET + STALLS ---- */
  v.pick('Fish Market','Laid on by four o’clock. By noon there is nothing left but scales and gulls.')
  for(let i=0;i<4;i++){
    const sx=-22+i*7;
    for(let x=sx;x<=sx+5;x++){
      v.put(x,5,-13,0x6b4f34);
      v.put(x,6,-13,j(0x8a6440,.1,x,6,-13));
      for(let y=7;y<=9;y++) v.put(x,y,-13,((Math.floor((x-sx)/2)+y)%2)?0xc74f38:0xf1e8d6);
    }
    v.put(sx,5,-14,0x54402e); v.put(sx+5,5,-14,0x54402e);
    for(let y=5;y<=9;y++){ v.put(sx,y,-12,0x54402e); v.put(sx+5,y,-12,0x54402e); }
    for(let x=sx+1;x<=sx+4;x++){ v.put(x,5,-11,j(0x8a6440,.12,x,5,-11),0); }
    barrel(v,sx+1,5,-11); crate(v,sx+4,5,-11,1);
  }

  /* ---- CRANE ---- */
  v.pick('The Old Crane','Hand‑winched, six‑ton purchase. She has stepped every mast in this harbour.')
  const RX=24,RZ=-19;
  for(let y=5;y<=15;y++){ v.box(RX,RX+1,y,y,RZ,RZ,0x6b4f34,.12); }
  v.box(RX-1,RX+2,5,5,RZ-1,RZ+1,0x4a4033,.1);
  const armP0=new THREE.Vector3(RX,RZ,-0); // placeholder
  for(let i=0;i<=10;i++){
    const x=RX-i-1, y=15-Math.round(i*0.45), z=RZ;
    v.put(x,y,z,j(0x7b5b3a,.1,x,y,z)); v.put(x,y+1,z,0x5b4330);
  }
  v.put(RX+1,16,RZ,0x3c434c);
  v.line(new THREE.Vector3(RX-11,11,RZ),new THREE.Vector3(RX-11,4,RZ),0x3a3229);
  v.line(new THREE.Vector3(RX+1,15.5,RZ-1),new THREE.Vector3(RX-11,11,RZ),0x3a3229);

  /* ---- BOATHOUSE + SLIP ---- */
  v.pick('Boathouse No. 4','The lifeboat is still manned by volunteers. They get called out eleven nights a year.')
  v.box(44,58,5,9,-32,-24,j(0xb8ac96,.1,44,5,-32));
  for(let i=0;i<=4;i++) v.box(43+i,59-i,10+i,10+i,-33,-23,j(0x3c4653,.12,43,i,-33));
  v.box(48,54,5,8,-24,-24,0x2e2b27,.05);
  smallBoat(v,51,-28,5,9,0);
  v.pick(false);
  for(let x=40;x<=62;x++)for(let z=-23;z<=-16;z++) v.put(x,4,z,j(0x7b7163,.16,x,4,z));

  /* ---- JETTY ---- */
  v.pick('The Town Jetty','Elm piles, creosote twice a decade. At low water you can read the whole tide in the weed.')
  const JZ0=-16,JZ1=14,JX0=56,JX1=61;
  v.box(JX0,JX1,4,4,JZ0,JZ1,0x8a6440,.13);
  for(let z=JZ0;z<=JZ1;z+=3)for(let x=JX0;x<=JX1;x+=2)
    for(let y=-5;y<=3;y++) v.put(x,y,z,j(0x4f3d2c,.15,x,y,z));
  for(let z=JZ0;z<=JZ1;z+=4){ v.put(JX0,5,z,0x5b4330); v.put(JX0,6,z,0x4a3626); v.put(JX1,5,z,0x5b4330); v.put(JX1,6,z,0x4a3626); }

  /* ---- LAMP POSTS / BOLLARDS / PROPS ---- */
  v.pick(false);
  for(let x=-64;x<=66;x+=13){
    for(let y=5;y<=10;y++) v.put(x,y,-14,0x2f3640);
    v.put(x,11,-14,0x3c444f);
    g.put(x,11,-13,0xffe6ae); g.put(x,12,-14,0xfff1cd); g.put(x,11,-15,0xffe6ae);
    v.put(x,13,-14,0x2a3037);
  }
  for(let x=-58;x<=62;x+=10){
    v.put(x,5,-15,0x4a4033); v.put(x,6,-15,0x5f5244); v.put(x,7,-15,0x6b5c4c);
    v.put(x,8,-15,0x5f5244);
  }
  for(let i=0;i<26;i++){
    const px=-62+Math.floor(hash3(i,1,7)*126), pz=-40+Math.floor(hash3(i,2,3)*22);
    const kind=hash3(i,3,1);
    if(kind<.4) crate(v,px,5,pz,1+((hash3(i,4,0)*2)|0));
    else if(kind<.72) barrel(v,px,5,pz);
    else sack(v,px,5,pz);
  }
  for(let i=0;i<6;i++){
    const px=-52+i*20;
    v.put(px,5,-38,j(0x6f6656,.2,px,5,-38));
    for(let k=0;k<3;k++) v.put(px+k,5,-37,0x8a6440);
  }
  // stone steps down to the water
  for(let k=0;k<9;k++){ const y=4-k, z=-19+k; v.box(34,37,y,y,z,z,j(0x6d727a,.16,34,y,z)); }
  // mooring buoys
  v.pick(false);
  // barrels & crates near warehouse
  for(let i=0;i<10;i++){ barrel(v,6+i*2+(i%2),5,-44); }
  return {v,g};
}

function tree(v,x,y,z,s=1){
  const h=Math.round(3+2*s);
  for(let i=0;i<h;i++) v.box(x,x,y+i,y+i,z,z,0x5a4230,.12);
  const r=Math.round(2+s);
  for(let dy=-1;dy<=r;dy++)for(let dx=-r;dx<=r;dx++)for(let dz=-r;dz<=r;dz++){
    const d=Math.abs(dx)+Math.abs(dy*1.3)+Math.abs(dz);
    if(d<=r+1&&hash3(x+dx,y+dy,z+dz)>.16)
      v.put(x+dx,y+h+dy,z+dz,j(dy>r-1?0x5f8a4a:0x4e7a40,.22,x+dx,y+dy,z+dz));
  }
}
function barrel(v,x,y,z){
  const c=0x7a5230, c2=0x8a6440;
  for(let dy=0;dy<3;dy++){
    v.put(x,y+dy,z,j(dy===1?c:c2,.12,x,y+dy,z));
    if(dy!==1){ v.put(x+1,y+dy,z,j(c,.1,x+1,y+dy,z)); v.put(x-1,y+dy,z,j(c,.1,x-1,y+dy,z));
                v.put(x,y+dy,z+1,j(c,.1,x,y+dy,z+1)); v.put(x,y+dy,z-1,j(c,.1,x,y+dy,z-1)); }
  }
  v.put(x,y+3,z,0x6b4a2c);
}
function crate(v,x,y,z,n=1){
  const w=1+n, c=0x9a7245;
  for(let dx=0;dx<w;dx++)for(let dy=0;dy<w;dy++)for(let dz=0;dz<w;dz++)
    v.put(x+dx,y+dy,z+dz,j(dy===w-1?0xa97e4e:c,.14,x+dx,y+dy,z+dz));
  for(let dx=0;dx<w;dx++){ v.put(x+dx,y+z*0+0+0+Math.round(y*0)+0,z,0); } // no-op guard
  for(let k=0;k<w;k++){ v.put(x+k,y,z-1,j(0x6f5333,.1,x+k,y,z-1)); v.put(x+k,y+w-1,z-1,j(0x6f5333,.1,x+k,y+w-1,z-1)); }
}
function sack(v,x,y,z){
  for(let dx=0;dx<2;dx++)for(let dy=0;dy<2;dy++)for(let dz=0;dz<2;dz++)
    if(hash3(x+dx,y+dy,z+dz)>.2) v.put(x+dx,y+dy,z+dz,j(0xb0a184,.15,x+dx,y+dy,z+dz));
}
function smallBoat(v,cx,cz,y,axis){ // axis 0 = along x, 1 = along z
  const L=9,B=3;
  for(let i=0;i<L;i++){
    const t=i/(L-1);
    const hw=Math.max(0,Math.round(B*(0.35+0.65*Math.sin(Math.PI*Math.min(1,t*0.85+0.08)))));
    for(let b=0;b<2;b++){
      for(let k=-hw;k<=hw;k++){
        const X=axis?cx+k:cx+i-L/2, Z=axis?cz+i-L/2:cz+k;
        const col=b===0?j(0x2f6b62,.1,X,y+b,Z):j(0xd8cdb8,.08,X,y+b,Z);
        v.put(X,y+b,Z,col);
      }
    }
    if(i===2||i===6) for(let k=-hw+1;k<=hw-1;k++) v.put(axis?cx+k:cx+i-L/2,y+1,axis?cz+i-L/2:cz+k,0xb8895a);
  }
  if(axis!==0){ /* masted */ }
}

/* ============================================================
   7 · THE SHIP
   ============================================================ */
function buildShip(){
  const v=new VSet(), g=new VSet(), rig=[];
  const X0=-23,X1=23;
  const beam = t=>interp(t,[[0,4.0],[0.06,5.9],[0.18,7.2],[0.42,7.5],[0.63,7.0],[0.80,5.3],[0.90,3.4],[0.965,1.7],[1,0.3]]);
  const bot  = t=>interp(t,[[0,1.1],[0.10,-1.3],[0.32,-2.1],[0.60,-2.1],[0.80,-1.2],[1,1.2]]);
  const sheer= t=>5.0+interp(t,[[0,1.8],[0.14,0.35],[0.45,0.0],[0.72,0.35],[1,2.1]]);
  const sail=0xf0e6d0, sailD=0xd7caad;

  /* ---- HULL ---- */
  v.pick('The Barque “Aurelia”','1867 — four hundred and twelve tons of Oregon fir. She has come in light: the wool and the tea are already ashore, and the crew are already in the town.')
  for(let x=X0;x<=X1;x++){
    const t=(x-X0)/(X1-X0);
    const hb=beam(t),b=bot(t),top=sheer(t);
    const yT=Math.floor(top)-1,yB=Math.floor(b);
    for(let y=yB;y<=yT;y++){
      const u=clamp((y-b)/(top-b),0,1);
      const mw=Math.max(0,Math.round(hb*(0.34+0.66*Math.pow(u,.42))));
      for(let z=-mw;z<=mw;z++){
        const edge=Math.abs(z)===mw;
        let c;
        if(y<=0) c=j(0x5c2f2a,.2,x,y,z);
        else if(y===yT) c=j(x%2?0xb78a58:0xab7e4f,.1,x,y,z);
        else if(!edge) c=0x3a2b1d;
        else if(y===1) c=j(0x161d26,.16,x,y,z);
        else if(y===2) c=j(0xc29840,.1,x,y,z);
        else if(y===3) c=((x+80)%4===0&&t>.08&&t<.85)?0x0b0f14:j(0x1e2733,.16,x,y,z);
        else if(y===4) c=j(0x223040,.14,x,y,z);
        else c=j(0xe7ddca,.08,x,y,z);
        v.put(x,y,z,c);
      }
    }
    const yTop=Math.floor(top);
    const mw=Math.max(0,Math.round(beam(t)*.99));
    for(const z of [-mw,mw]) v.put(x,yTop,z,j(0xd7ccb6,.08,x,yTop,z));
  }
  /* gunports + cannon */
  for(let x=X0+4;x<=X1-6;x+=4){
    const t=(x-X0)/(X1-X0); if(t<.1||t>.85)continue;
    const mw=Math.round(beam(t)*(0.34+0.66*Math.pow(.55,.42)));
    for(const s of[-1,1]){
      v.put(x,3,mw*s,0x0a0e13);
      v.put(x,3,(mw-1)*s,0x2b2b2f);
      v.put(x,3,(mw-2)*s,0x3a3a40);
    }
  }
  /* transom */
  { const t=0, hb=beam(t), yTop=Math.floor(sheer(t));
    for(let y=2;y<=yTop;y++)for(let z=-Math.round(hb*.85);z<=Math.round(hb*.85);z++){
      v.put(X0,y,z,y%2?j(0xe7ddca,.06,X0,y,z):j(0xd4c8b0,.06,X0,y,z));
    }
    for(const zz of[-3,0,3]){ g.put(X0-1,3,zz,0xffd08a); g.put(X0-1,4,zz,0xffd08a);
      v.put(X0-1,2,zz,0xc29840); v.put(X0-1,5,zz,0xc29840); }
    v.box(X0-1,X0-1,yTop+1,yTop+1,-2,2,0xc29840,.1);
  }
  /* bowsprit figurehead */
  v.box(24,26,3,4,0,0,0xe0d6c0,.08);
  v.put(27,4,0,0xd8cdb8); v.put(26,5,0,0xcfc3ab);
  /* ---- DECK FITTINGS ---- */
  v.pick('Main Deck','Holystone and sheepshank. She smells of tar, horse manure from the cart, and tomorrow’s weather.')
  for(const hx of [-14,-2,9]){
    for(let dx=-1;dx<=1;dx++)for(let dz=-2;dz<=2;dz++){
      v.put(hx+dx,Math.floor(sheer((hx+dx-X0)/(X1-X0)))-1,dz,j(0x8a6440,.1,hx+dx,0,dz));
    }
  }
  for(const [cx,cz] of [[12,4],[12,-4],[5,4],[5,-4],[0,-4],[-8,4],[-8,-4]]) barrel(v,cx,Math.floor(sheer((cx-X0)/(X1-X0)))-1,cz);
  /* capstan */
  for(let y=0;y<2;y++) v.disc(15,0,Math.floor(sheer((15-X0)/(X1-X0)))+y,1.4,0x6f5333,y===1,.1);
  /* spare spars along the bulwark */
  for(const s of[-1,1]) for(let x=-8;x<=6;x++) v.put(x,4,Math.round(beam((x-X0)/(X1-X0))*.82)*s,0x7b5b3a);
  /* ship's boat stowed amidships */
  smallBoat(v,-6,0,Math.floor(sheer((-6-X0)/(X1-X0)))+1,0);
  /* ---- MASTS & YARDS ---- */
  v.pick('Rig & Yards','Three hundred and forty‑two running rigging, and a bosun who knows every one of them by name.')
  const masts=[
    {x:-3, top:28, r:1,  name:'main'},
    {x:9,  top:25, r:1,  name:'fore'},
    {x:-16,top:21, r:1,  name:'mizzen'}
  ];
  for(const m of masts){
    const d=Math.floor(sheer((m.x-X0)/(X1-X0)));
    for(let y=d;y<=m.top;y++){
      const s=y>m.top-7?1:2;
      for(let dx=0;dx<s;dx++)for(let dz=-Math.floor(s/2);dz<Math.ceil(s/2);dz++)
        v.put(m.x+dx,y,dz,j(y%9===0?0x4a3826:0x7b5b3a,.08,m.x+dx,y,dz));
    }
    v.put(m.x,m.top+1,0,0xe7ddca);
    if(m.name==='main') for(let y=0;y<3;y++) g.put(m.x-1,d+1+y,0,0xffcf85); // sternhouse lights
  }
  function yard(x,y,half,roll){
    for(let z=-half;z<=half;z++){
      v.put(x,y,z,j(0x7b5b3a,.07,x,y,z));
      if(roll){ v.put(x,y+1,z,j(0xe3d8c0,.08,x,y+1,z)); v.put(x-1,y,z,0x6a4e30); }
    }
  }
  /* fighting tops */
  for(const [mx,ty] of [[-3,14],[9,12.5]]){
    const x0=Math.round(mx)-1,x1=Math.round(mx)+1;
    v.box(x0,x1,ty,ty,-4,4,j(0x7b5b3a,.08,x0,ty,0));
    for(const s of[-1,1]) for(let z=-4;z<=4;z++) v.put(mx+ (z%2? 1:-1),ty+1,z,0x5b4330);
    for(let z=-4;z<=4;z+=4){ v.put(mx-2,ty+1,z,0x5b4330); v.put(mx+2,ty+1,z,0x5b4330); }
  }
  const yards=[[-3,14.5,8,1],[-3,20,6.1,0],[-3,24,4,0],
               [9,12.5,7.2,1],[9,17.5,5.4,0],[9,21,3.4,0],
               [-16,15.5,4.4,1]];
  for(const y of yards) yard(...y);
  /* square sails */
  function squareSail(cx,yB,yT,zh,belly,seed){
    for(let z=-zh;z<=zh;z++){
      const zt=1-Math.pow(z/zh,2);
      const yb=Math.round(yB-1.4*zt);
      for(let y=yb;y<=yT;y++){
        const yt=Math.sin(Math.PI*clamp((y-yb)/Math.max(1,(yT-yb)),0,1));
        const d=Math.round(belly*zt*yt);
        for(let i=0;i<=d;i++){
          let c=sail;
          if(y===yb) c=sailD;
          else if(i===0) c=0xe4dac1;
          if(((y-yb)%5)===2) c=0xe0d5ba;
          v.put(cx+i,y,z,j(c,.05,seed+y,z));
        }
      }
    }
  }
  squareSail(-4,7.6,14,7.4,3.0,1);
  squareSail(-4,14.8,19.5,5.8,2.3,2);
  squareSail(-4,20.4,23.5,3.9,1.5,3);
  squareSail(8,6.6,12,6.6,2.6,4);
  squareSail(8,12.6,17,5.1,2.0,5);
  squareSail(8,17.6,20.5,3.3,1.2,6);
  squareSail(-17,11,15,4.1,1.6,7);
  /* spanker */
  for(let x=-25;x<=-16;x++){
    const u=(-16-x)/9;
    const yB=Math.round(9.6-u*1.2), yT=Math.round(15+u*1.3);
    for(let y=yB;y<=yT;y++){ v.put(x,y,0,j(y===yB?0xdccfb4:sail,.05,x,y,0)); v.put(x,y,1,j(sail,.05,x,y,1)); }
  }
  v.line(new THREE.Vector3(-16,9.6,0),new THREE.Vector3(-25,8.4,0),0x7b5b3a);
  v.line(new THREE.Vector3(-16,15,0),new THREE.Vector3(-22.5,16.6,0),0x7b5b3a);
  /* jibs */
  function staysail(x1,y1,x2,y2,drop){
    const n=Math.abs(x2-x1);
    for(let i=0;i<=n;i++){
      const u=i/n, x=x1+(x2-x1)*u, y=y1+(y2-y1)*u, h=Math.round(drop*(1-u)*Math.pow(Math.sin(Math.PI*u*.9+.25),.5)*1.4);
      for(let k=0;k<=h;k++) v.put(Math.round(x),Math.round(y)-k,0,j(k===h?0xe2d7bd:sail,.05,x,k,0));
    }
  }
  staysail(33,10.5,9,20.5,3.2);
  staysail(28,12.5,9,23,4.5);
  /* bowsprit */
  const bp0=new THREE.Vector3(22,5.4,0), bp1=new THREE.Vector3(32,10.2,0);
  v.line(bp0,bp1,()=>j(0x7b5b3a,.07,0,0,0));
  for(let i=0;i<=12;i++){ const t=i/12; v.put(lerp(bp0.x,bp1.x,t),lerp(bp0.y,bp1.y,t)+1,0,j(0x6a4e30,.07,i,0,0)); }
  v.line(new THREE.Vector3(28,8.4,0),new THREE.Vector3(30,5.5,0),0x6a4e30);
  /* ---- DRESSED OVERALL ---- */
  const sig=[0xd6453c,0xf1e8d6,0x2f5fa8,0x3f8f5c,0xf0b52f,0x2b2f36,0xe8733a,0x6fa8dc];
  const dress=[[32,10.2,9,23.5],[9,23.5,-3,26],[-3,26,-16,19],[-16,19,-24,8]];
  let si=0;
  for(const [ax,ay,bx,by] of dress){
    const n=Math.floor(Math.hypot(bx-ax,by-ay)/2.6);
    for(let i=1;i<n;i++){ const t=i/n;
      const sag=Math.sin(t*Math.PI)*1.6;
      v.box(Math.round(lerp(ax,bx,t)),Math.round(lerp(ay,by,t)-sag),Math.round(lerp(ay,by,t)-sag),0,0,0,0);
      v.put(Math.round(lerp(ax,bx,t)),Math.round(lerp(ay,by,t)-sag),0,sig[(si++)%sig.length]);
    }
  }
  /* ---- RIGGING ---- */
  for(const m of masts){
    const t=(m.x-X0)/(X1-X0), d=Math.floor(sheer(t)), B=Math.round(beam(t));
    for(const side of[-1,1]){
      for(let k=0;k<6;k++){
        const a=new THREE.Vector3(m.x-2+k*.4,m.top-9,side*1.4);
        const b2=new THREE.Vector3(m.x-3+k*1.25,d+.5,side*(B+.4));
        rig.push(a,b2);
      }
      for(let r=0;r<12;r++){
        const u=r/12;
        const y=lerp(d+.5,m.top-9,u);
        for(let k=0;k<5;k++){
          const a=new THREE.Vector3(m.x-3+k*1.25*d/(m.top-9-d)*0+lerp(m.x-2+k*.4,m.x-3+k*1.25,u),y,lerp(side*1.4,side*(B+.4),u));
          const b2=new THREE.Vector3(lerp(m.x-2+(k+1)*.4,m.x-3+(k+1)*1.25,u),y,lerp(side*1.4,side*(B+.4),u));
          rig.push(a,b2);
        }
      }
    }
  }
  rig.push(new THREE.Vector3(9,24.5,0),new THREE.Vector3(32,10.4,0));
  rig.push(new THREE.Vector3(-3,27.5,0),new THREE.Vector3(9,24.5,0));
  rig.push(new THREE.Vector3(-16,20.5,0),new THREE.Vector3(-3,27.5,0));
  rig.push(new THREE.Vector3(-3,27.5,0),new THREE.Vector3(-23.5,7,0));
  rig.push(new THREE.Vector3(9,24.5,0),new THREE.Vector3(-3,14,0));
  return {v,g,rig};
}

/* ============================================================
   8 · ASSEMBLE
   ============================================================ */
const H=buildHarbour();
const harbourMesh=toMesh(H.v,matWorld); scene.add(harbourMesh);
const glowH=toMesh(H.g,matGlow,{cast:false,receive:false}); scene.add(glowH); registerGlow(glowH);
addProxies(H.v,harbourMesh,scene,new Set([false]));

const S=buildShip();
const shipGroup=new THREE.Group(); shipGroup.position.set(-2,-1,-5.5); scene.add(shipGroup);
const shipMesh=toMesh(S.v,matWorld); shipGroup.add(shipMesh);
const glowS=toMesh(S.g,matGlow,{cast:false,receive:false}); shipGroup.add(glowS); registerGlow(glowS);
addProxies(S.v,shipMesh,shipGroup);

/* rigging */
{
  const pos=[]; for(const p of S.rig) pos.push(p.x,p.y,p.z);
  const gg=new THREE.BufferGeometry();
  gg.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));
  const rigMesh=new THREE.LineSegments(gg,new THREE.LineBasicMaterial({color:0x2a251f,transparent:true,opacity:.85}));
  shipGroup.add(rigMesh);
}

/* ---- MOORING LINES ---- */
function rope(a,b,sag,r=.16,col=0x6d5b45){
  const pts=[];
  const n=18;
  for(let i=0;i<=n;i++){
    const t=i/n;
    pts.push(new THREE.Vector3(lerp(a.x,b.x,t),lerp(a.y,b.y,t)-Math.sin(t*Math.PI)*sag,lerp(a.z,b.z,t)));
  }
  const curve=new THREE.CatmullRomCurve3(pts);
  const m=new THREE.Mesh(new THREE.TubeGeometry(curve,20,r,5,false),
    new THREE.MeshLambertMaterial({color:col}));
  m.castShadow=false; scene.add(m); return m;
}
rope(new THREE.Vector3(13,5.0,-10.5),new THREE.Vector3(25,5.6,-17.6),1.5);
rope(new THREE.Vector3(15,4.6,-12),new THREE.Vector3(31,5.6,-17.6),2.1);
rope(new THREE.Vector3(-19,5.2,-11),new THREE.Vector3(-26,5.6,-17.6),1.3);
rope(new THREE.Vector3(-21,4.8,-9),new THREE.Vector3(-34,5.6,-17.6),2.0);
/* gangway from quay to the waist */
{
  const gv=new VSet(); gv.pick('Gangway','Chocked, lashed, and greased. Nobody drops a cask down her on my watch.')
  for(let i=0;i<=7;i++){
    const z=-17+i*1.0, y=5+Math.round(i*.55);
    for(let x=-3;x<=1;x++) gv.put(x,y,z,j(0x8a6440,.14,x,y,z));
    if(i%2===0){ for(let x=-3;x<=1;x+=4) gv.put(x,y+1,z,0x6f5333); }
  }
  gv.pick(false);
  for(let i=0;i<=7;i++){ const z=-17+i, y=6+Math.round(i*.55); gv.put(-3,y,z,0x5b4330); gv.put(1,y,z,0x5b4330); }
  const gm=toMesh(gv,matWorld); scene.add(gm); addProxies(gv,gm,scene);
}
/* ---- THE SHIP'S COLOURS (fluttering) ---- */
function makeFlag(w,h,pal){
  const fv=new VSet();
  for(let x=0;x<w;x++)for(let y=0;y<h;y++) fv.put(x,y,0,pal(x,y,w,h));
  const fm=toMesh(fv,flagMat,{cast:false,receive:false});
  return fm;
}
const ensign=makeFlag(7,4,(x,y,w,h)=>((x%3===0||y===Math.floor(h/2))?0xf1e8d6:0x27457f));
ensign.position.set(-26.5,7.5,0.6); shipGroup.add(ensign);
const pennant=makeFlag(9,3,(x,y,w,h)=>(x>w-3?(y===1?0xf1e8d6:0x27457f):(y===0||y===2?0xd6453c:0xf1e8d6)));
pennant.position.set(-2,28.5,1.2); shipGroup.add(pennant);
const houseflag=makeFlag(4,3,(x,y,w,h)=>(y===1?0xf1e8d6:0x3f8f5c));
houseflag.position.set(-23.5,11.5,0.6); shipGroup.add(houseflag);

/* ---- MOORED FISHING SMACK + ROWBOAT ---- */
function littleVessel(fn,home,roll){
  const sv=new VSet(); sv.pick('A Friend in Harbour','Longer than she is sound. Her nets are drying on the wall and her name is painted over twice.')
  fn(sv);
  const m=toMesh(sv,matWorld);
  const grp=new THREE.Group(); grp.add(m); grp.position.copy(home); scene.add(grp);
  addProxies(sv,m,grp);
  return {grp,roll};
}
const smack=littleVessel(sv=>{ smallBoat(sv,0,0,0,11,1);
  for(let y=1;y<=9;y++) sv.put(0,y,0,j(0x7b5b3a,.1,0,y,0));
  for(let y=1;y<=6;y++) sv.put(-1,y,0,0x6a4e30);
  for(let i=-4;i<=4;i+=4) sv.put(i,0,0,0x5b4330);
},new THREE.Vector3(42,0,-8),.03);
const gig=littleVessel(sv=>{ smallBoat(sv,0,0,0,7,0); sv.put(-2,0,0,0x6f5333); sv.put(2,0,0,0x6f5333); },
  new THREE.Vector3(6,0,-12),.055);
for(const [bx,bz,col] of [[-46,4,0xb5442f],[-30,10,0x2f6b52],[16,22,0xd6a44c],[48,26,0xb5442f]]){
  const bv=new VSet(); bv.pick(false);
  bv.box(bx-1,bx+1,-1,0,bz-1,bz+1,j(col,.1,bx,0,bz));
  bv.put(bx,1,bz,0x2b3139); bv.put(bx,2,bz,j(col,.1,bx,2,bz));
  const bm=toMesh(bv,matWorld); scene.add(bm);
}
/* distant ship on the horizon */
{
  const dv=new VSet(); dv.pick(false);
  dv.box(96,104,-3,-2,-190,-190,0x3d4c55,.05);
  for(let y=-1;y<=6;y++) dv.put(99,y,-190,0x4a5a63);
  dv.box(97,101,0,4,-190,-190,0x556670,.05);
  const dm=toMesh(dv,matWorld,{cast:false,receive:false}); scene.add(dm);
}

/* ---- CLOUDS ---- */
const cloudMat=new THREE.MeshBasicMaterial({color:0xffffff});
const cv=new VSet(); cv.pick(false);
for(let i=0;i<24;i++){
  const cx=-380+hash3(i,1,1)*760, cy=52+hash3(i,2,2)*34, cz=-380+hash3(i,3,3)*700;
  const w=8+hash3(i,4,4)*16;
  for(let n=0;n<w;n++){
    const px=Math.round(cx+(hash3(i,n,5)-.5)*22);
    const py=Math.round(cy+(hash3(i,n,6)-.5)*5);
    const pz=Math.round(cz+(hash3(i,n,7)-.5)*16);
    cv.box(px,px+2+((hash3(i,n,8)*3)|0),py,py+1+((hash3(i,n,9)*2)|0),pz,pz+2+((hash3(i,n,10)*3)|0),
      py>cy?0xffffff:0xc9d2dd,0);
  }
}
const clouds=toMesh(cv,cloudMat,{cast:false,receive:false}); scene.add(clouds);

/* ---- LIGHTHOUSE BEAM ---- */
const beamGrp=new THREE.Group(); beamGrp.position.set(-38,27.5,17); scene.add(beamGrp);
function beamMesh(rad,len,op){
  const geo=new THREE.ConeGeometry(rad,len,16,1,true);
  geo.translate(0,-len/2,0); geo.rotateZ(-Math.PI/2);
  const m=new THREE.Mesh(geo,new THREE.MeshBasicMaterial({color:0xffe3ac,transparent:true,opacity:op,
    blending:THREE.AdditiveBlending,depthWrite:false,side:THREE.DoubleSide,fog:true}));
  return m;
}
const beamA=beamMesh(11,120,.075), beamB=beamMesh(4,90,.09);
beamGrp.add(beamA,beamB);
const lampCore=new THREE.Mesh(new THREE.SphereGeometry(1.5,10,8),
  new THREE.MeshBasicMaterial({color:0xfff2cc,transparent:true,opacity:.9,blending:THREE.AdditiveBlending,depthWrite:false}));
scene.add(lampCore);

/* ---- CHIMNEY SMOKE ---- */
const smokeMat=new THREE.MeshLambertMaterial({color:0xa8adb5,transparent:true,opacity:.42});
const smoke=[];
for(let i=0;i<11;i++){
  const m=new THREE.Mesh(new THREE.BoxGeometry(1,1,1),smokeMat);
  m.userData.p=i/11; smoke.push(m); scene.add(m);
}
/* ---- GULLS ---- */
const gullW=new THREE.MeshLambertMaterial({color:0xf2f2ef});
const gullD=new THREE.MeshLambertMaterial({color:0x3c434a});
const gullO=new THREE.MeshLambertMaterial({color:0xe0a23c});
const gulls=[];
const gBody=new THREE.BoxGeometry(.8,.75,2.3), gWing=new THREE.BoxGeometry(3,.16,1), gBeak=new THREE.BoxGeometry(.5,.22,.5);
for(let i=0;i<7;i++){
  const grp=new THREE.Group();
  const b=new THREE.Mesh(gBody,gullW); b.position.z=-.2; grp.add(b);
  const head=new THREE.Mesh(gBody,gullW); head.scale.set(.62,.62,.42); head.position.set(0,.42,-1.2); grp.add(head);
  const beak=new THREE.Mesh(gBeak,gullO); beak.position.set(0,.36,-1.75); grp.add(beak);
  const wl=new THREE.Group(), wr=new THREE.Group();
  const ml=new THREE.Mesh(gWing,gullW); ml.position.x=1.5; wl.add(ml); wl.position.x=-.4; grp.add(wl);
  const mr=new THREE.Mesh(gWing,gullW); mr.position.x=1.5; wr.add(mr); wr.position.x=.4; grp.add(wr);
  grp.traverse(o=>{o.castShadow=false;o.receiveShadow=false;});
  scene.add(grp);
  gulls.push({grp,wl,wr,ph:hash3(i,5,5)*99,R:28+hash3(i,6,6)*36,sp:.09+hash3(i,7,7)*.07,
              cy:20+hash3(i,8,8)*14,cx:-10+hash3(i,9,9)*30,cz:-20+hash3(i,10,10)*30});
}

/* ============================================================
   9 · TIME OF DAY
   ============================================================ */
const STOPS=[
 {h:5.20, dir:[.78,.10,.55], sun:.95, sunC:0xffab6b, hemiSky:0x5f78a4, hemiG:0x2c3340, hemiI:.55, amb:.20,
  top:0x1c2f56, hor:0xf0a173, fog:0x8d93a8, deep:0x12384c, shal:0x3c7c92, spec:0xffd9a8, expo:1.22, glow:1.0,
  cloud:0xb9a6b4, st:'Mist'},
 {h:8.40, dir:[.88,.40,.30], sun:2.1, sunC:0xffe3bc, hemiSky:0x9dc2e2, hemiG:0x3c4a3e, hemiI:.72, amb:.14,
  top:0x2f74b4, hor:0xd6e7f0, fog:0xb6cbdb, deep:0x125670, shal:0x3fa0b4, spec:0xffffff, expo:1.0, glow:.15,
  cloud:0xf6f8fa, st:'Clear'},
 {h:12.60,dir:[.18,.95,.25], sun:2.9, sunC:0xfff7e8, hemiSky:0xa9cdec, hemiG:0x46543f, hemiI:.82, amb:.13,
  top:0x2a72bd, hor:0xc3dcec, fog:0xbdd4e3, deep:0x0f5c7d, shal:0x35adc4, spec:0xffffff, expo:.93, glow:0,
  cloud:0xffffff, st:'Bright'},
 {h:16.30,dir:[-.52,.55,.63], sun:2.5, sunC:0xffd9a4, hemiSky:0x9fc3dd, hemiG:0x4a4b3c, hemiI:.7, amb:.13,
  top:0x2d6aa8, hor:0xefd2ac, fog:0xbfb4ab, deep:0x114c64, shal:0x37a1ad, spec:0xffeccd, expo:1.0, glow:.12,
  cloud:0xf4e5d6, st:'Hazy'},
 {h:18.05,dir:[-.90,.30,.40], sun:2.35, sunC:0xffb066, hemiSky:0x93a8c8, hemiG:0x454034, hemiI:.62, amb:.16,
  top:0x24548c, hor:0xf4a765, fog:0xc39a80, deep:0x123f57, shal:0x3c94a3, spec:0xffd7a0, expo:1.06, glow:.45,
  cloud:0xf0b28a, st:'Golden'},
 {h:20.30,dir:[-.93,.13,.33], sun:.55, sunC:0xff7a48, hemiSky:0x3f5480, hemiG:0x242a34, hemiI:.5, amb:.24,
  top:0x10214a, hor:0xd06a4e, fog:0x5b5871, deep:0x0b2436, shal:0x1d5a72, spec:0xa9d2ff, expo:1.30, glow:1.0,
  cloud:0x9c7f92, st:'Blue hour'},
];
const tcA=new THREE.Color(), tcB=new THREE.Color(), tmpV=new THREE.Vector3();
let glowLevel=.45;
function applyTime(hour){
  let i=0; while(i<STOPS.length-2&&hour>STOPS[i+1].h) i++;
  const a=STOPS[i], b=STOPS[i+1];
  const u=clamp((hour-a.h)/(b.h-a.h),0,1);
  tmpV.set(lerp(a.dir[0],b.dir[0],u),lerp(a.dir[1],b.dir[1],u),lerp(a.dir[2],b.dir[2],u)).normalize();
  sun.position.copy(tmpV).multiplyScalar(230);
  sun.target.position.set(0,0,0);
  sun.intensity=lerp(a.sun,b.sun,u);
  tcA.setHex(a.sunC); tcB.setHex(b.sunC); sun.color.copy(tcA).lerp(tcB,u);
  hemi.intensity=lerp(a.hemiI,b.hemiI,u);
  hemi.color.copy(tcA.setHex(a.hemiSky)).lerp(tcB.setHex(b.hemiSky),u);
  hemi.groundColor.copy(tcA.setHex(a.hemiG)).lerp(tcB.setHex(b.hemiG),u);
  amb.intensity=lerp(a.amb,b.amb,u);
  skyU.uTop.value.copy(tcA.setHex(a.top)).lerp(tcB.setHex(b.top),u);
  skyU.uHor.value.copy(tcA.setHex(a.hor)).lerp(tcB.setHex(b.hor),u);
  skyU.uSunCol.value.copy(tcA.setHex(a.sunC)).lerp(tcB.setHex(b.sunC),u);
  skyU.uSun.value.copy(tmpV);
  scene.fog.color.copy(tcA.setHex(a.fog)).lerp(tcB.setHex(b.fog),u);
  U.deep.value.copy(tcA.setHex(a.deep)).lerp(tcB.setHex(b.deep),u);
  U.shal.value.copy(tcA.setHex(a.shal)).lerp(tcB.setHex(b.shal),u);
  U.spec.value.copy(tcA.setHex(a.spec)).lerp(tcB.setHex(b.spec),u);
  horizonMat.color.copy(U.deep.value);
  renderer.toneMappingExposure=lerp(a.expo,b.expo,u);
  cloudMat.color.copy(tcA.setHex(a.cloud)).lerp(tcB.setHex(b.cloud),u);
  glowLevel=lerp(a.glow,b.glow,u);
  lampTown.intensity=glowLevel*26; lampLight.intensity=glowLevel*10;
  beamA.material.opacity=.075*glowLevel; beamB.material.opacity=.10*glowLevel;
  lampCore.material.opacity=.25+.7*glowLevel;
  smokeMat.opacity=.28+.2*glowLevel;
  for(const mesh of glowMeshes){
    const base=mesh.userData.base, ic=mesh.instanceColor;
    if(!ic) continue;
    const f=.55+glowLevel*1.9;
    for(let k=0;k<base.length;k+=3){
      ic.array[k]=Math.min(1,base[k]*f);
      ic.array[k+1]=Math.min(1,base[k+1]*f);
      ic.array[k+2]=Math.min(1,base[k+2]*f*1.02);
    }
    ic.needsUpdate=true;
  }
  renderer.shadowMap.needsUpdate=true;
  return (u<.5?a:b).st;
}

/* ============================================================
   10 · UI
   ============================================================ */
const $=s=>document.querySelector(s);
const hourEl=$('#hour'), seaEl=$('#sea'), hourOut=$('#hourOut'), seaOut=$('#seaOut'), stateTxt=$('#stateTxt');
const SEAS=['Glassy','Ripple','Slight','Moderate','Fresh','Rough'];
function fmtHour(h){ const hh=Math.floor(h), mm=Math.floor((h-hh)*60); return String(hh).padStart(2,'0')+':'+String(mm).padStart(2,'0'); }
function updHour(){
  const h=parseFloat(hourEl.value);
  stateTxt.textContent=applyTime(h);
  hourOut.textContent=fmtHour(h);
  document.querySelectorAll('[data-h]').forEach(b=>b.classList.toggle('on',Math.abs(parseFloat(b.dataset.h)-h)<.02));
  const wind=Math.round(1+ (parseFloat(seaEl.value)*5) + (h>16?1.4:0));
  $('#wnd').textContent='SSW '+Math.min(7,wind);
}
function updSea(){
  const s=parseFloat(seaEl.value);
  U.amp.value=.16+s*.85;
  seaOut.textContent=SEAS[Math.min(5,Math.floor(s*5.99))];
  renderer.shadowMap.needsUpdate=true;
}
hourEl.addEventListener('input',updHour);
seaEl.addEventListener('input',updSea);
document.querySelectorAll('[data-h]').forEach(b=>b.addEventListener('click',()=>{hourEl.value=b.dataset.h;updHour();}));
const orbitBtn=$('#orbit');
orbitBtn.addEventListener('click',()=>{controls.autoRotate=!controls.autoRotate;orbitBtn.classList.toggle('on',controls.autoRotate);});
$('#reset').addEventListener('click',()=>{ tweenCam(DEF_POS,DEF_TGT,1.1); });
addEventListener('keydown',e=>{
  if(e.code==='Space'){e.preventDefault();orbitBtn.click();}
  if(e.key==='r'||e.key==='R'){$('#reset').click();}
});
let idleT=0;
controls.addEventListener('start',()=>{controls.autoRotate=false;orbitBtn.classList.remove('on');idleT=0;});
controls.addEventListener('end',()=>{idleT=0;});

/* camera tween */
let tween=null;
function tweenCam(pos,tgt,dur){ tween={p0:camera.position.clone(),t0:controls.target.clone(),p1:pos.clone(),t1:tgt.clone(),t:0,d:dur}; controls.enabled=false; }

/* click-to-read */
const ray=new THREE.Raycaster();
const tag=$('#tag'); let tagTimer=0, downPos=null;
renderer.domElement.addEventListener('pointerdown',e=>{downPos=[e.clientX,e.clientY]; skipIntro();});
renderer.domElement.addEventListener('pointerup',e=>{
  if(!downPos) return;
  if(Math.hypot(e.clientX-downPos[0],e.clientY-downPos[1])>5) return;
  ray.setFromCamera(new THREE.Vector2((e.clientX/innerWidth)*2-1,-(e.clientY/innerHeight)*2+1),camera);
  const hit=ray.intersectObjects(pickables,false)[0];
  if(hit&&hit.object.userData.info){
    const info=hit.object.userData.info;
    const p=hit.point.clone(); p.y+=hit.object.geometry.parameters.height/2+2;
    tag.innerHTML=`<div class="t-k">Berth log · entry</div><div class="t-n">${info.name}</div>
      <div class="t-d">${info.blurb}</div>
      <div class="t-c"><span>GRID ${Math.round(p.x)} / ${Math.round(p.z)}</span><span>ELEV ${Math.round(p.y)} m</span></div>`;
    tag.classList.add('show');
    tag.dataset.wx=p.x+','+(p.y)+','+p.z;
    clearTimeout(tagTimer); tagTimer=setTimeout(()=>tag.classList.remove('show'),7000);
  } else tag.classList.remove('show');
});
renderer.domElement.addEventListener('pointermove',e=>{
  if(downPos) return;
  const now=performance.now(); if(now< (renderer.domElement._t||0)) return; renderer.domElement._t=now+70;
  ray.setFromCamera(new THREE.Vector2((e.clientX/innerWidth)*2-1,-(e.clientY/innerHeight)*2+1),camera);
  const hit=ray.intersectObjects(pickables,false)[0];
  renderer.domElement.style.cursor=hit?'pointer':'grab';
});

/* ============================================================
   11 · LOOP
   ============================================================ */
const clock=new THREE.Clock();
let frames=0,fpsT=0;
const fpsEl=$('#fps'), blocksEl=$('#blocks');
let intro=true, introT=0;
function skipIntro(){ if(intro){intro=false; controls.enabled=true;} }
addEventListener('wheel',skipIntro,{passive:true});

updHour(); updSea();
let totalBlocks=0;
scene.traverse(o=>{ if(o.isInstancedMesh&&o!==water) totalBlocks+=o.count; });
blocksEl.textContent=totalBlocks.toLocaleString();

function tick(){
  requestAnimationFrame(tick);
  const dt=Math.min(.05,clock.getDelta());
  const t=clock.elapsedTime;
  U.time.value=t;

  /* intro dolly */
  if(intro){
    introT+=dt;
    const k=clamp(introT/4.4,0,1), e=1-Math.pow(1-k,3);
    const p0=DEF_POS.clone().multiplyScalar(1.95), p1=DEF_POS.clone();
    camera.position.lerpVectors(p0,p1,e);
    camera.position.y=lerp(58,DEF_POS.y,e);
    controls.target.copy(DEF_TGT);
    camera.lookAt(controls.target);
    if(k>=1){intro=false;controls.enabled=true;}
  } else {
    controls.update();
    idleT+=dt;
    if(idleT>6&&!controls.autoRotate&&!document.hidden){controls.autoRotate=true;orbitBtn.classList.add('on');}
  }

  /* ship motion */
  shipGroup.position.y=-1+Math.sin(t*.55)*.17+Math.sin(t*.31+1.2)*.07;
  shipGroup.rotation.z=Math.sin(t*.42+.6)*.014;
  shipGroup.rotation.x=Math.sin(t*.33)*.008;

  /* small boats */
  smack.grp.position.y=Math.sin(t*.7+1)*.19-.05; smack.grp.rotation.z=Math.sin(t*.5)*smack.roll; smack.grp.rotation.x=Math.sin(t*.63+.4)*smack.roll*.7;
  gig.grp.position.y=Math.sin(t*.9+2.4)*.16-.04;  gig.grp.rotation.z=Math.sin(t*1.1+1)*gig.roll;  gig.grp.rotation.x=Math.cos(t*.8)*gig.roll;

  /* clouds */
  clouds.position.x=(t*1.3)%900-450;

  /* gulls */
  for(const g of gulls){
    const a=t*g.sp+g.ph;
    const px=g.cx+Math.cos(a)*g.R, pz=g.cz+Math.sin(a*1.13)*g.R*.72;
    const py=g.cy+Math.sin(t*.6+g.ph)*2.4;
    g.grp.position.set(px,py,pz);
    const nx=g.cx+Math.cos(a+.05)*g.R, nz=g.cz+Math.sin((a+.05)*1.13)*g.R*.72;
    g.grp.lookAt(nx,py,nz);
    const flap=Math.sin(t*6+g.ph)*.62;
    g.wl.rotation.z=flap; g.wr.rotation.z=-flap;
  }

  /* smoke */
  smoke.forEach((m,i)=>{
    let p=(m.userData.p+t*.13)%1;
    const bx=-5.5+hash3(i,1,1)*1.4, bz=-54.5+hash3(i,2,2)*1.6;
    m.position.set(bx+p*p*7.5,13.4+p*13,bz+p*p*2.6+Math.sin(t*.7+i)*.4);
    const s=.6+p*2.4; m.scale.set(s,s,s);
    m.rotation.y=t*.4+i;
  });

  /* lighthouse */
  beamGrp.rotation.y=t*.55;
  lampCore.position.set(-38,27.5,17);
  lampCore.scale.setScalar(1+Math.sin(t*2.2)*.08+glowLevel*.5);

  /* tag follow */
  if(tag.classList.contains('show')&&tag.dataset.wx){
    const [x,y,z]=tag.dataset.wx.split(',').map(Number);
    const p=new THREE.Vector3(x,y,z).project(camera);
    if(p.z<1){ tag.style.left=((p.x*.5+.5)*innerWidth)+'px'; tag.style.top=((-p.y*.5+.5)*innerHeight)+'px'; }
  }

  /* shadow refresh (static scene: update at 15 Hz) */
  frames++;
  if(frames%4===0) renderer.shadowMap.needsUpdate=true;
  fpsT+=dt;
  if(fpsT>.5){ fpsEl.textContent=Math.round(frames/fpsT); frames=0; fpsT=0; }

  renderer.render(scene,camera);
  if(!window.__ok){ window.__ok=true; const l=$('#loader'); l.classList.add('gone'); setTimeout(()=>l.remove(),900); }
}
tick();

addEventListener('resize',()=>{
  camera.aspect=innerWidth/innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight);
  renderer.shadowMap.needsUpdate=true;
});
</script>
</body>
</html>
```

A few things worth poking at:

- **Hour of day** drives one shared keyframe ramp: sun vector, light colours, hemisphere, fog, sky shader, sea gradient, specular tint, exposure, cloud tint, window/lamp emission and the lighthouse beam's strength all interpolate together — so the shadow geometry genuinely travels around the harbour.
- **Sea state** feeds the GPU wave amplitude, which also re-derives per-column normals (finite differences in the vertex shader), so wave crests catch the low sun as moving glints.
- The scene is **instanced with hidden-block culling** — only surface voxels are uploaded; shadow maps refresh at 15 Hz instead of per frame since everything but the ship is static.
- **Click anything** — every named structure registered an invisible picking box, so the quay, the barque, the sail loft, the crane, the breakwater and the Light each raise their own plaque with live grid/elevation readout.
- Any input skips the opening dolly; auto-orbit resumes after six idle seconds.