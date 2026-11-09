# Calling at Harbour — a voxel harbour in one file

Save as `harbour.html`, open in Chrome. Everything (geometry, sea, sky shader, camera rig, UI) is self-contained — only three.js comes from a CDN, and the mouse controls are hand-written so nothing else can fail to load.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1"/>
<title>Calling at Harbour — voxel marine study № 11</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@400;600;700;800;900&family=Barlow:ital,wght@0,400;0,500;0,600;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root{
  --ink:#eaf1f5; --ink-dim:#93a9b8; --amber:#f4b13d; --brass:#c98a2b;
  --panel:rgba(7,15,22,.86); --line:rgba(244,177,61,.26); --line2:rgba(168,197,214,.16);
  --sea:#0a1a24;
}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;overflow:hidden;background:#05090d;color:var(--ink);
  font-family:"Barlow",system-ui,sans-serif;-webkit-font-smoothing:antialiased}
canvas{display:block;width:100%;height:100%;cursor:grab}
canvas.drag{cursor:grabbing}
.fx{position:fixed;inset:0;pointer-events:none}
#vig{background:radial-gradient(120% 95% at 50% 42%,transparent 45%,rgba(2,8,14,.62) 100%);z-index:5}
#grain{z-index:6;opacity:.35;mix-blend-mode:overlay;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='140' height='140'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3'/></filter><rect width='140' height='140' filter='url(%23n)' opacity='.5'/></svg>")}
#scan{z-index:5;background:repeating-linear-gradient(0deg,rgba(255,255,255,.028) 0 1px,transparent 1px 3px);opacity:.5}

/* ---------- shared plate ---------- */
.plate{position:fixed;z-index:10;background:
   linear-gradient(180deg,rgba(13,26,36,.92),rgba(6,13,19,.94));
  border:1px solid var(--line2);box-shadow:0 18px 50px -20px rgba(0,0,0,.85), inset 0 1px 0 rgba(255,255,255,.05);}
.plate::before{content:"";position:absolute;left:0;top:0;height:2px;width:100%;
  background:linear-gradient(90deg,var(--amber),rgba(244,177,61,0) 70%)}
.reveal{opacity:0;transform:translateY(14px);transition:opacity .9s cubic-bezier(.16,.8,.24,1),transform .9s cubic-bezier(.16,.8,.24,1)}
.in{opacity:1;transform:none}

/* ---------- chart badge (top-left) ---------- */
#chart{top:22px;left:24px;display:flex;align-items:stretch;gap:0;padding:0}
#compass{width:86px;height:86px;display:grid;place-items:center;border-right:1px solid var(--line2);
  background:radial-gradient(circle at 50% 45%,rgba(244,177,61,.10),transparent 65%)}
#compass svg{width:64px;height:64px;overflow:visible}
#compass .rose{transition:none}
#readouts{padding:11px 16px 11px 14px;font-family:"IBM Plex Mono",monospace;font-size:10.5px;line-height:1.75;letter-spacing:.06em;color:var(--ink-dim)}
#readouts b{color:var(--ink);font-weight:500}
#readouts .k{color:var(--brass)}
#readouts div+div{border-top:1px dashed rgba(168,197,214,.14);margin-top:3px;padding-top:2px}

/* ---------- title plate (bottom-left) ---------- */
#plate{left:24px;bottom:24px;max-width:min(460px,52vw);padding:20px 24px 18px}
#plate .kick{font:600 10.5px/1 "Barlow";letter-spacing:.3em;text-transform:uppercase;color:var(--amber);display:flex;gap:9px;align-items:center}
#plate .kick::after{content:"";flex:1;height:1px;background:linear-gradient(90deg,var(--line),transparent)}
h1{font-family:"Big Shoulders Display","Barlow",sans-serif;font-weight:900;
   font-size:clamp(38px,5.6vw,74px);line-height:.83;letter-spacing:-.005em;margin:12px 0 0;text-transform:uppercase;
   text-shadow:0 6px 30px rgba(0,0,0,.65)}
h1 em{font-style:normal;color:var(--amber);display:block}
#plate p{margin-top:12px;font-size:14.5px;line-height:1.62;color:#b8cad6;max-width:40ch}
#plate p i{color:var(--ink);font-style:italic}
#log{margin-top:14px;border-top:1px solid var(--line2);padding-top:10px;
  display:grid;grid-template-columns:auto 1fr;gap:3px 14px;
  font-family:"IBM Plex Mono",monospace;font-size:10.5px;letter-spacing:.04em;color:var(--ink-dim)}
#log span:nth-child(odd){color:var(--brass)}
#log span:nth-child(even){color:#cfdde6;text-align:right}

/* ---------- control rail (right) ---------- */
#rail{right:24px;top:22px;width:246px;padding:14px 16px 16px}
#rail h2{font-family:"Big Shoulders Display";font-weight:800;font-size:22px;letter-spacing:.02em;text-transform:uppercase;line-height:1}
#rail .sub{font-family:"IBM Plex Mono",monospace;font-size:9.5px;letter-spacing:.16em;color:var(--brass);margin:2px 0 12px}
.grp{border-top:1px solid var(--line2);padding-top:11px;margin-top:11px}
.grp:first-of-type{border:0;padding-top:0;margin-top:0}
.lbl{display:flex;justify-content:space-between;align-items:baseline;
  font:600 9.5px/1 "Barlow";letter-spacing:.22em;text-transform:uppercase;color:var(--ink-dim);margin-bottom:9px}
.lbl b{font-family:"IBM Plex Mono",monospace;font-size:11px;letter-spacing:.04em;color:var(--amber);font-weight:500}
input[type=range]{-webkit-appearance:none;appearance:none;width:100%;height:16px;background:transparent;cursor:ew-resize}
input[type=range]::-webkit-slider-runnable-track{height:4px;border-radius:0;
  background:linear-gradient(90deg,#14273a,#3d5f7d,#f4b13d,#7a4a24,#101b2b);box-shadow:inset 0 0 0 1px rgba(255,255,255,.08)}
input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:12px;height:16px;margin-top:-6px;background:var(--ink);
  border:1px solid #05090d;box-shadow:0 0 0 1px var(--amber),0 0 14px rgba(244,177,61,.7);border-radius:1px}
input[type=range]::-moz-range-track{height:4px;background:#3d5f7d}
input[type=range]::-moz-range-thumb{width:12px;height:16px;border-radius:1px;background:var(--ink);border:1px solid var(--amber)}
.views{display:grid;grid-template-columns:1fr 1fr;gap:6px}
button.v{position:relative;text-align:left;background:rgba(255,255,255,.035);border:1px solid var(--line2);color:#cfdde6;
  font:700 12px/1 "Big Shoulders Display";letter-spacing:.09em;text-transform:uppercase;padding:9px 9px 9px 17px;cursor:pointer;
  transition:transform .18s ease,background .18s ease,border-color .18s ease,color .18s ease}
button.v::before{content:"";position:absolute;left:8px;top:50%;width:3px;height:0;transform:translateY(-50%);background:var(--amber);transition:height .2s ease}
button.v:hover{transform:translateY(-2px);border-color:var(--line);background:rgba(244,177,61,.1);color:#fff}
button.v:hover::before{height:56%}
button.v.on{background:var(--amber);color:#0b1319;border-color:var(--amber)}
button.v.on::before{height:56%;background:#0b1319}
button.v kbd{position:absolute;right:6px;top:5px;font:500 8.5px/1 "IBM Plex Mono",monospace;opacity:.5}
.tog{display:flex;justify-content:space-between;align-items:center;padding:6px 0;cursor:pointer;
  font:500 11.5px/1 "Barlow";letter-spacing:.05em;color:#b8cad6}
.tog:hover{color:#fff}
.sw{width:34px;height:16px;border:1px solid var(--line2);background:rgba(0,0,0,.45);position:relative;flex:none}
.sw i{position:absolute;left:1px;top:1px;width:14px;height:12px;background:#5a6f7e;transition:.22s cubic-bezier(.4,1.4,.5,1)}
.tog.on .sw{border-color:var(--amber);box-shadow:0 0 12px -2px rgba(244,177,61,.55)}
.tog.on .sw i{left:17px;background:var(--amber)}

/* ---------- hint bar ---------- */
#hint{position:fixed;right:24px;bottom:24px;z-index:10;text-align:right;
  font-family:"IBM Plex Mono",monospace;font-size:9.5px;letter-spacing:.1em;color:#6d8595;line-height:1.9}
#hint b{color:#c98a2b;font-weight:500}
#hint em{font-style:normal;color:#cfdde6}

/* ---------- loader ---------- */
#load{position:fixed;inset:0;z-index:40;background:#05090d;display:grid;place-items:center;transition:opacity .8s ease}
#load.gone{opacity:0;pointer-events:none}
#load .in{width:min(420px,80vw);text-align:left}
#load h3{font-family:"Big Shoulders Display";font-weight:900;font-size:44px;line-height:.9;text-transform:uppercase}
#load small{font-family:"IBM Plex Mono",monospace;font-size:10px;letter-spacing:.22em;color:var(--brass);display:block;margin-bottom:14px}
#bar{height:2px;background:#16232e;margin-top:20px;overflow:hidden}
#bar i{display:block;height:100%;width:12%;background:var(--amber);animation:load 1.6s cubic-bezier(.5,0,.2,1) forwards;box-shadow:0 0 14px var(--amber)}
@keyframes load{to{width:100%}}
#err{position:fixed;inset:0;z-index:50;display:none;place-items:center;background:#05090d;color:#f4b13d;
  font-family:"IBM Plex Mono",monospace;font-size:13px;padding:30px;text-align:center}

@media (max-width:860px){
  #plate{max-width:none;left:14px;right:14px;bottom:14px;padding:14px 16px}
  #plate p{display:none}
  #rail{left:14px;right:14px;top:auto;bottom:auto;width:auto;top:118px;padding:10px 12px}
  #rail .grp:nth-of-type(n+3){display:none}
  #hint{display:none}#chart{left:14px;top:14px}
}
</style>
</head>
<body>
<canvas id="c"></canvas>
<div class="fx" id="scan"></div><div class="fx" id="vig"></div><div class="fx" id="grain"></div>

<div id="chart" class="plate reveal">
  <div id="compass">
    <svg viewBox="-50 -50 100 100">
      <g class="rose" id="rose">
        <circle r="42" fill="none" stroke="rgba(168,197,214,.28)" stroke-width="1"/>
        <circle r="34" fill="none" stroke="rgba(168,197,214,.14)" stroke-width="1" stroke-dasharray="2 4"/>
        <g id="ticks"></g>
        <polygon points="0,-38 5,-4 -5,-4" fill="#f4b13d"/>
        <polygon points="0,38 5,4 -5,4" fill="rgba(234,241,245,.5)"/>
      </g>
      <text x="0" y="-44" font-family="IBM Plex Mono,monospace" font-size="9" fill="#f4b13d" text-anchor="middle">N</text>
    </svg>
  </div>
  <div id="readouts">
    <div><span class="k">BRG</span> <b id="rBrg">000°</b> · <span class="k">RNG</span> <b id="rRng">000</b></div>
    <div><span class="k">WND</span> <b id="rWnd">SW 9kn</b> · <span class="k">SEA</span> <b id="rSea">2</b></div>
    <div><span class="k">LOG</span> <b id="rClock">17:40</b> · <b id="rPhase">GOLDING</b></div>
  </div>
</div>

<section id="plate" class="plate reveal">
  <div class="kick">Voxel marine study № 11 · Bay of St. Orin</div>
  <h1>Calling at<em>Harbour</em></h1>
  <p>A three-masted barque has struck her topgallants and come to in <i>four fathoms</i> off the north quay. The harbourmaster signs the register; the keeper lights the tower an hour early.</p>
  <div id="log">
    <span>01 RIG</span><span>Barque · 3 masts</span>
    <span>02 HULL</span><span>34 m oak &amp; larch</span>
    <span>03 SIGNAL</span><span>Paid off / striking</span>
    <span>04 SOUNDING</span><span>4 fm 2 in at quay head</span>
  </div>
</section>

<aside id="rail" class="plate reveal">
  <h2>Harbour Master</h2>
  <div class="sub">CONSOLE · WATCH SETTINGS</div>

  <div class="grp">
    <div class="lbl">Hour of day <b id="todLbl">GOLDING</b></div>
    <input id="tod" type="range" min="0" max="1000" value="735">
  </div>

  <div class="grp">
    <div class="lbl">Sea state <b id="seaLbl">2 · SLIGHT</b></div>
    <input id="sea" type="range" min="0" max="100" value="34">
  </div>

  <div class="grp">
    <div class="lbl">Viewpoint</div>
    <div class="views" id="views">
      <button class="v on" data-v="0">Quay<kbd>1</kbd></button>
      <button class="v" data-v="1">Quarterdeck<kbd>2</kbd></button>
      <button class="v" data-v="2">Tower<kbd>3</kbd></button>
      <button class="v" data-v="3">Crow's nest<kbd>4</kbd></button>
      <button class="v" data-v="4">Survey<kbd>5</kbd></button>
      <button class="v" data-v="5">Sea buoy<kbd>6</kbd></button>
    </div>
  </div>

  <div class="grp">
    <div class="tog on" id="tOrbit"><span>Slow turn of the watch</span><span class="sw"><i></i></span></div>
    <div class="tog on" id="tGulls"><span>Gulls</span><span class="sw"><i></i></span></div>
    <div class="tog on" id="tBeam"><span>Light sweeping</span><span class="sw"><i></i></span></div>
  </div>
</aside>

<div id="hint">
  <div><b>DRAG</b> orbit · <b>WHEEL</b> zoom · <b>RIGHT-DRAG</b> pan</div>
  <div><b>DBL-CLICK</b> sail to that point · <em>1–6</em> views · <em>R</em> auto-orbit</div>
</div>

<div id="load"><div class="in">
  <small>VOXEL FOUNDRY · RIGGING 40 000 CUBES</small>
  <h3>Calling at Harbour</h3>
  <div id="bar"><i></i></div>
</div></div>
<div id="err">three.js could not be fetched — check the network connection and reopen.</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function(){
"use strict";
if(!window.THREE){document.getElementById('err').style.display='grid';document.getElementById('load').style.display='none';return;}

/* ═══════════════════════ 1 · RENDERER, SKY, LIGHTS ═══════════════════════ */
const canvas=document.getElementById('c');
const renderer=new THREE.WebGLRenderer({canvas,antialias:true,powerPreference:'high-performance'});
renderer.setPixelRatio(Math.min(devicePixelRatio,1.8));
renderer.setSize(innerWidth,innerHeight);
renderer.shadowMap.enabled=true;
renderer.shadowMap.type=THREE.PCFSoftShadowMap;

const scene=new THREE.Scene();
scene.fog=new THREE.Fog(0xa9bcc6,240,950);
const camera=new THREE.PerspectiveCamera(40,innerWidth/innerHeight,0.6,3200);

const hemi=new THREE.HemisphereLight(0x9fc4e2,0x3d4a44,0.62); scene.add(hemi);
const amb=new THREE.AmbientLight(0x24313c,0.35); scene.add(amb);
const sun=new THREE.DirectionalLight(0xffe7c0,1.0);
sun.castShadow=true;
sun.shadow.mapSize.set(2048,2048);
const SC=sun.shadow.camera, SD=175;
SC.left=-SD;SC.right=SD;SC.top=SD;SC.bottom=-SD;SC.near=2;SC.far=1400;
sun.shadow.bias=-0.0009; sun.shadow.normalBias=0.55;
scene.add(sun); sun.target.position.set(0,10,0); scene.add(sun.target);
const fill=new THREE.DirectionalLight(0x8fb6d6,0.24); fill.position.set(-140,70,120); scene.add(fill);

/* sky dome */
const skyU={
  uTop:{value:new THREE.Color(0x2b5f96)},uHor:{value:new THREE.Color(0xf0b878)},
  uSun:{value:new THREE.Vector3(0.6,0.4,-0.7)},uSunCol:{value:new THREE.Color(0xffc178)},
  uCloud:{value:new THREE.Color(0xf4d9c0)},uTime:{value:0}
};
const sky=new THREE.Mesh(new THREE.SphereGeometry(1600,32,18),new THREE.ShaderMaterial({
  side:THREE.BackSide,depthWrite:false,uniforms:skyU,
  vertexShader:`varying vec3 vP;void main(){vP=position;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}`,
  fragmentShader:`
  varying vec3 vP;uniform vec3 uTop,uHor,uSun,uSunCol,uCloud;uniform float uTime;
  float h21(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
  float nz(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.0-2.0*f);
    return mix(mix(h21(i),h21(i+vec2(1,0)),f.x),mix(h21(i+vec2(0,1)),h21(i+vec2(1,1)),f.x),f.y);}
  float fbm(vec2 p){float a=.5,s=0.;for(int i=0;i<4;i++){s+=a*nz(p);p*=2.07;a*=.5;}return s;}
  void main(){
    vec3 d=normalize(vP);
    float t=clamp(d.y*0.5+0.5,0.,1.);
    vec3 col=mix(uHor,uTop,pow(t,0.72));
    float s=max(dot(d,normalize(uSun)),0.);
    col+=uSunCol*pow(s,9.0)*0.42;
    col+=uSunCol*pow(s,2.0)*0.06;
    col+=uSunCol*smoothstep(0.99905,0.99975,s)*1.35;
    float band=smoothstep(0.015,0.30,d.y)*smoothstep(0.85,0.32,d.y);
    float c=fbm(d.xz/(abs(d.y)+0.16)*1.15+vec2(uTime*0.006,0.0));
    float cl=smoothstep(0.50,0.86,c)*band;
    col=mix(col,uCloud,cl*0.62);
    gl_FragColor=vec4(col,1.0);
  }`
}));
sky.frustumCulled=false; scene.add(sky);

/* ═══════════════════════ 2 · VOXEL BUILDER ═══════════════════════ */
function mulberry(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
const R=mulberry(90210);
const lerp=(a,b,t)=>a+(b-a)*t;
const clamp=(v,a,b)=>v<a?a:v>b?b:v;
function sh(hex,f){const c=new THREE.Color(hex);c.r=clamp(c.r*f,0,1);c.g=clamp(c.g*f,0,1);c.b=clamp(c.b*f,0,1);return c.getHex();}

const boxGeo=new THREE.BoxGeometry(1,1,1);
{const n=boxGeo.attributes.position.count,a=new Float32Array(n*3);a.fill(1);
 boxGeo.setAttribute('color',new THREE.BufferAttribute(a,3));}

function Vox(){this.items=[];}
Vox.prototype.add=function(x,y,z,w,h,d,c,q){
  this.items.push({p:new THREE.Vector3(x+w/2,y+h/2,z+d/2),s:new THREE.Vector3(w,h,d),c:c,q:q||null});};
Vox.prototype.v=function(x,y,z,c){this.add(x,y,z,1,1,1,c,null);};
Vox.prototype.box=function(x0,x1,y0,y1,z0,z1,c){this.add(Math.min(x0,x1),Math.min(y0,y1),Math.min(z0,z1),
  Math.abs(x1-x0)+1,Math.abs(y1-y0)+1,Math.abs(z1-z0)+1,c,null);};
Vox.prototype.shell=function(x0,x1,y0,y1,z0,z1,c,fn){
  for(let x=x0;x<=x1;x++)for(let y=y0;y<=y1;y++)for(let z=z0;z<=z1;z++){
    if(x===x0||x===x1||y===y0||y===y1||z===z0||z===z1)
      this.v(x,y,z,fn?fn(x,y,z):c);}};
Vox.prototype.line=function(a,b,c,t){
  const dir=b.clone().sub(a);const len=dir.length();if(len<0.001)return;
  const q=new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0,1,0),dir.normalize());
  this.items.push({p:a.clone().add(b).multiplyScalar(0.5),s:new THREE.Vector3(t,len,t),c:c,q:q});};
Vox.prototype.tri=function(a,b,c,col,bulge){
  const ab=b.clone().sub(a),ac=c.clone().sub(a);
  const nn=ab.clone().cross(ac).normalize();
  const seen=new Set(),N=46;
  for(let i=0;i<=N;i++)for(let j=0;j<=N-i;j++){
    const u=i/N,v=j/N;
    const p=a.clone().addScaledVector(ab,u).addScaledVector(ac,v);
    p.addScaledVector(nn,Math.sin(Math.PI*u)*Math.sin(Math.PI*(u+v))*bulge);
    const x=Math.round(p.x),y=Math.round(p.y),z=Math.round(p.z),k=x+','+y+','+z;
    if(seen.has(k))continue;seen.add(k);this.v(x,y,z,col);}};

function makeMesh(list,mat,cast,recv){
  if(!list.items.length)return null;
  const m=new THREE.InstancedMesh(boxGeo,mat,list.items.length);
  const d=new THREE.Object3D(),col=new THREE.Color();
  for(let i=0;i<list.items.length;i++){const it=list.items[i];
    d.position.copy(it.p);d.scale.copy(it.s);
    if(it.q)d.quaternion.copy(it.q);else d.quaternion.set(0,0,0,1);
    d.updateMatrix();m.setMatrixAt(i,d.matrix);m.setColorAt(i,col.set(it.c));}
  m.instanceMatrix.needsUpdate=true;if(m.instanceColor)m.instanceColor.needsUpdate=true;
  m.castShadow=!!cast;m.receiveShadow=!!recv;m.frustumCulled=false;
  return m;}

const matWorld=new THREE.MeshLambertMaterial({color:0xffffff,vertexColors:true});
const matShip =new THREE.MeshLambertMaterial({color:0xffffff,vertexColors:true});
const matGlow =new THREE.MeshBasicMaterial({color:0xffffff,vertexColors:true});
const matCloud=new THREE.MeshLambertMaterial({color:0xffffff,vertexColors:true,transparent:true,opacity:.96});
const matWater=new THREE.MeshStandardMaterial({color:0xffffff,vertexColors:true,roughness:.20,metalness:.06});

const V=new Vox(), VG=new VGx(), VS=new Vox(), VSG=new VGx(); function VGx(){Vox.call(this);}VGx.prototype=Vox.prototype;

const solid=new Set();
const markCell=(x,z)=>solid.add(x+','+z);
const isLandCell=(x,z)=>solid.has(x+','+z);

/* ═══════════════════════ 3 · PALETTE ═══════════════════════ */
const PAL={
  hullD:0x35251a,hullD2:0x452f1f,red:0x8b3a26,white:0xe9e3d4,gold:0xc9973e,
  deck:0xa8834e,deckD:0x7c5c34,rope:0x50412e,mast:0x6d4c2c,mastD:0x543a21,iron:0x33393f,
  sail:0xf1e7cd,sail2:0xdccba4,sail3:0xcbb890,
  gr1:0x6f747a,gr2:0x5c6167,gr3:0x82888f,sand:0xc4ad81,rock:0x5c5f63,rockM:0x4a5844,
  wood:0x7d5a38,woodD:0x5a3f26,woodL:0x9a7248,
  slate:0x3d4b58,slate2:0x51616f,brick:0x9c5741,cream:0xd9c9a4,blue:0x63798a,och:0xc08a3c,grn:0x4e6a41,
  glass:0xffcd7a,lamp:0xffc65e,flame:0xffa63c,white2:0xf2f0e6
};

/* ═══════════════════════ 4 · TERRAIN & HARBOUR ═══════════════════════ */
const QX=32;                       // quay face
const QT=5;                        // quay cobble layer y (top surface = 6)
const shoreZ=z=>Math.round(33+3.2*Math.sin(z*0.075)+2.1*Math.sin(z*0.21+1.3));
function landEdge(z){return (z>=-30&&z<=34)?QX:shoreZ(z);}
function landTop(z,x){
  if(z>=-30&&z<=34)return 5;
  if(z>34)return 5+Math.min(9,Math.round((z-34)/7));
  return 5+Math.round(2.2*Math.sin(z*0.18)+1.6*Math.sin(x*0.11));
}

/* — sea floor shelf — */
V.box(-720,-720+1440,-14,-2,-720,-720+1440,0x113247);

/* — main land mass — */
for(let z=-74;z<=74;z++){
  const e=landEdge(z),tp=landTop(z,e);
  V.box(e,116,-12,tp-1,z,z, tp>7?0x4a5c46:0x6a6e73);
  markCell(e,z); if(e+1<=116)for(let x=e;x<=Math.min(116,e+3);x++)markCell(x,z);
}
/* grass / earth top dressing (near field only) */
for(let x=QX;x<=92;x++)for(let z=-70;z<=70;z++){
  if(!isLandCell(x,z))continue;
  const tp=landTop(z,x);
  if(x>QX+1&&((x*7+z*13)%5)>1)continue;
  let c;
  if(z>=-30&&z<=34)c=((x+z)%3===0)?PAL.gr2:((x*3+z)%7===0?PAL.gr3:PAL.gr1);
  else if(tp>8)c=((x+z)%4===0)?0x40533c:PAL.grn;
  else if(tp>6)c=((x*2+z)%5===0)?0x5c6f4a:0x4a5c46;
  else c=((x+z*2)%6===0)?PAL.rock:((x+z)%3===0?0x6b6e72:0x565a5e);
  if(x===QX&&z>=-30&&z<=34)continue;
  V.v(x,tp,z,c);
}
/* quay paving, near field fully detailed */
for(let x=QX+1;x<=56;x++)for(let z=-32;z<=40;z++){
  if(!isLandCell(x,z))continue;
  const n=(x*2654435761+z*40503)>>>0;const r=((n>>3)&1023)/1023;
  let c=PAL.gr1;
  if(r<0.10)c=PAL.gr2; else if(r>0.93)c=PAL.gr3; else if((x%9===0&&z%5===0))c=0x767c83;
  V.v(x,QT,z,c);
}
/* quay face wall + yellow safety line */
for(let z=-30;z<=34;z++){
  for(let y=-4;y<=QT;y++){
    const r=R();
    V.v(QX-1,y,z,(z+y*3)%6===0?PAL.gr2:((z*5+y)%9===0?PAL.gr3:PAL.gr1));
  }
  V.v(QX,QT,z,((z+2)%9===0)?PAL.gr2:0xcfa544);
}
/* steps down to the water */
for(let i=0;i<6;i++)V.box(26+i,29+i,QT-5+i,QT-5+i,26,30,PAL.gr3);
/* bollards + capstans */
function bollard(x,z){V.box(x,x,QT+1,QT+3,z,z,PAL.iron);V.box(x-0,x,QT+4,QT+4,z,z,0x4a5158);}
for(let z=-26;z<=30;z+=7)bollard(QX+1,z);
V.box(QX+4,QX+5,QT+1,QT+3,-2,-1,PAL.woodD);V.box(QX+4,QX+5,QT+4,QT+4,-2,-1,PAL.wood);
function cleat(x,z){V.box(x,x+1,QT+1,QT+1,z,z,PAL.iron);V.v(x,QT+2,z,PAL.iron);V.v(x+1,QT+2,z,PAL.iron);}

/* — the long pier (the ship lies here) — */
const PIER={x0:14,x1:QX,z0:6,z1:12};
for(let x=PIER.x0;x<=PIER.x1;x++)for(let z=PIER.z0;z<=PIER.z1;z++)
  V.v(x,QT,z,((x+z)%2===0)?PAL.wood:PAL.woodL);
for(let x=PIER.x0+1;x<=PIER.x1;x+=4)for(let z=PIER.z0;z<=PIER.z1;z+=5){
  for(let y=-4;y<QT;y++)V.v(x,y,z,PAL.woodD);
  if(x+1<=PIER.x1){V.line(new THREE.Vector3(x+1,2,z+.5),new THREE.Vector3(PIER.x1+.5,4.4,PIER.z0+.5),PAL.woodD,.3);}
}
for(let z=PIER.z0;z<=PIER.z1;z++){V.v(PIER.x0-1,QT,z,PAL.woodD);V.v(PIER.x1,QT+1,z,PAL.iron);}
bollard(PIER.x0+1,PIER.z0+1);bollard(PIER.x0+1,PIER.z1-1);bollard(PIER.x0+8,PIER.z0+1);
for(let z=PIER.z0;z<=PIER.z1;z+=2){for(let y=-2;y<=2;y++)V.v(PIER.x0-1,y,z,0x2b241d);}
/* lamp posts on the quay & pier */
const lampPos=[];
function lamp(x,z,h){
  for(let y=QT+1;y<=QT+h;y++)V.v(x,y,z,PAL.iron);
  V.box(x-1,x+1,QT+h+1,QT+h+1,z,z,PAL.iron);
  V.box(x-1,x+1,QT+h+2,QT+h+3,z-1,z+1,0x2c3238);
  for(let a=-1;a<=1;a++)for(let b=-1;b<=1;b++)VG.v(x+a,QT+h+2,z+b,PAL.lamp);
  VG.v(x,QT+h+4,z,0x8b9198);
  lampPos.push([x,QT+h+3,z]);
}
lamp(QX+3,QT? -22:-22,7);lamp(QX+3,8,7);lamp(QX+3,28,7);lamp(PIER.x0+2,PIER.z1-1,5);
/* crates, barrels, nets, coils */
function crate(x,z){const w=1+((R()*2)|0),d=1+((R()*2)|0),h=1+((R()*2)|0);
  V.shell(x,x+w-1,QT+1,QT+h,z,z+d-1,((R()*3)|0)?PAL.wood:PAL.woodL);
  for(let i=x;i<=x+w-1;i++)V.v(i,QT+h+1,z+((d-1)>>1),PAL.woodD);}
function barrel(x,z){const c=R()<.5?PAL.woodD:0x6b4a2c;
  V.box(x,x,QT+1,QT+3,z,z,c);V.v(x,QT+2,z,0x9a8c72);V.v(x,QT+1,z,c);
  V.v(x,QT+4,z,PAL.woodL);}
for(let i=0;i<26;i++){const x=QX+3+((R()*20)|0),z=-28+((R()*64)|0);if(R()<.5)crate(x,z);else barrel(x,z);}
for(let i=0;i<5;i++){const x=PIER.x0+3+((R()*14)|0),z=PIER.z0+((R()*6)|0);if(R()<.6)crate(x,z);else barrel(x,z);}
function netPile(x,z){for(let i=0;i<26;i++)V.v(x+((R()*4)|0),QT+1+((R()*2)|0),z+((R()*3)|0),R()<.5?0x6e6250:0x8a7d63);}
netPile(QX+6,-16);netPile(QX+7,18);
function coil(x,z){V.box(x,x+1,QT+1,QT+1,z,z+1,0x8a7050);V.v(x,QT+2,z,0xa08460);V.v(x+1,QT+2,z+1,0xa08460);}
coil(PIER.x0+4,PIER.z1-1);coil(QX+4,-4);
cleat(PIER.x0,PIER.z0+2);cleat(PIER.x0,PIER.z1-2);

/* — warehouse — */
function warehouse(x,z,w,d,h){
  V.shell(x,x+w-1,QT,QT+h,z,z+d-1,PAL.brick,(a,b,c)=>((c*3+b)%9===0)?sh(PAL.brick,.86):PAL.brick);
  V.box(x+2,x+5,QT,QT+5,z,PAL.iron);                       /* big doors */
  V.box(x+2,x+5,QT+5,QT+5,z,0x3f4650);
  for(let i=0;i<5;i++)V.v(x+2+i,QT+6,z,0x2b3038);
  const steps=(d>>1)+1;
  for(let i=0;i<steps;i++){
    V.box(x-1,x+w,QT+h+i,QT+h+i,z+i,z+i,(i===steps-1)?PAL.slate2:(i%2?PAL.slate:sh(PAL.slate,1.1)));
    V.box(x-1,x+w,QT+h+i,QT+h+i,z+d-1-i,z+d-1-i,(i===steps-1)?PAL.slate2:(i%2?PAL.slate:sh(PAL.slate,1.1)));
  }
  V.box(x-1,x+w,QT+h+steps,QT+h+steps,z+steps-1,z+steps-1,PAL.iron);
  V.box(x+3,x+4,QT+h+steps,QT+h+steps+6,z+d-4,PAL.brick);
  V.box(x+3,x+4,QT+h+steps+7,QT+h+steps+7,z+d-4,0x2c2f34);
  return [x+3.5,QT+h+steps+8,z+d-3.5];
}
const chim=[warehouse(QX+16,-16,16,15,9)];

/* — cottages & town — */
function house(x,z,w,d,h,wall,roof,opts){
  opts=opts||{};
  V.shell(x,x+w-1,QT,QT+h,z,z+d-1,wall,(a,b,c)=>((a+b*2+c)%11===0)?sh(wall,.9):wall);
  const ridgeAlongX=opts.ridge!=='z';
  const steps=(ridgeAlongX?(d>>1):w>>1)+1;
  for(let i=0;i<steps;i++){
    if(ridgeAlongX){
      V.box(x-1,x+w,QT+h+i,QT+h+i,z+i,z+i,(i===steps-1)?PAL.slate2:(i%2?roof:sh(roof,1.12)));
      V.box(x-1,x+w,QT+h+i,QT+h+i,z+d-1-i,z+d-1-i,(i===steps-1)?PAL.slate2:(i%2?roof:sh(roof,1.12)));
    }else{
      V.box(x+i,x+i,QT+h+i,QT+h+i,z-1,z+d, i%2?roof:sh(roof,1.12));
      V.box(x+w-1-i,x+w-1-i,QT+h+i,QT+h+i,z-1,z+d, i%2?roof:sh(roof,1.12));
    }
  }
  if(ridgeAlongX)V.box(x-1,x+w,QT+h+steps,QT+h+steps,z+steps-1,z+steps-1,PAL.iron);
  /* windows on the harbour face */
  for(let wx=x+1;wx<=x+w-2;wx+=2)for(let wy=QT+2;wy<=QT+h-1;wy+=3){
    const lit=R()<0.55;
    VG.v(wx,wy,z,lit?PAL.glass:0x2c3a44); VG.v(wx+1,wy,z,lit?PAL.glass:0x2c3a44);
    V.v(wx,wy+1,z,PAL.woodD);V.v(wx+1,wy+1,z,PAL.woodD);
    V.v(wx,wy-1,z,PAL.woodL);V.v(wx+1,wy-1,z,PAL.woodL);
  }
  V.box(x+(w>>1)-1,x+(w>>1),QT,QT+2,z,PAL.woodD);
  /* chimney + optional tree */
  const cx=x+((R()*Math.max(1,w-2))|0);
  V.box(cx,cx+1,QT+h,QT+h+steps+3,z+d-2,PAL.brick);
  return [cx+.5,QT+h+steps+4,z+d-1.5];
}
const chimneys=[];
const rowA=[PAL.cream,PAL.blue,PAL.och,PAL.cream,PAL.blue,PAL.och];
for(let i=0;i<6;i++){
  const z=-24+i*11, x=QX+13+((i%2)?3:0);
  if(x+11>QX+34)continue;
  chimneys.push(house(x,z,10,10,6,rowA[i%6],PAL.slate));
}
for(let i=0;i<7;i++){
  const x=QX+16+((i%3)*13), z=16+((i/3)|0)*14;
  if(z>60)continue;
  chimneys.push(house(x,z,10,10,6,rowA[(i+2)%6],PAL.slate2));
}
for(let i=0;i<8;i++){
  const x=QX+18+((i%4)*12), z=42+((i/4)|0)*16;
  chimneys.push(house(x,z,9,9,5,R()<.5?PAL.white2:PAL.cream,PAL.slate));
}
/* customs house with clock tower */
(function(){
  const x=QX+7,z=-4,w=7,d=9,h=8;
  V.shell(x,x+w-1,QT,QT+h,z,z+d-1,PAL.cream);
  for(let i=0;i<stepsRoof(0);i++){}
  const st=(d>>1)+1;
  for(let i=0;i<st;i++){V.box(x-1,x+w,QT+h+i,QT+h+i,z+i,z+i,PAL.slate);V.box(x-1,x+w,QT+h+i,QT+h+i,z+d-1-i,z+d-1-i,PAL.slate);}
  /* tower */
  const tx=x+1,tz=z+3;
  V.shell(tx,tx+3,QT+h,QT+h+13,tz,tz+2,PAL.cream);
  for(let yy=QT+h+3;yy<=QT+h+11;yy+=3){VG.v(tx,yy,tz,PAL.glass);VG.v(tx+3,yy,tz,PAL.glass);}
  VG.box(tx+1,tx+2,QT+h+9,QT+h+10,tz,PAL.white2);
  VG.v(tx+1,QT+h+9,tz,0x2b2b2b);VG.v(tx+2,QT+h+10,tz,0x2b2b2b);
  for(let i=0;i<3;i++)V.box(tx-i,tx+3+i,QT+h+14+i,QT+h+14+i,tz-i,tz+2+i,PAL.slate);
  V.v(tx+1,QT+h+17,tz+1,PAL.gold);V.v(tx+2,QT+h+18,tz+1,PAL.gold);
})();
function stepsRoof(){return 0;}
/* church on the heights */
(function(){
  const x=QX+58,z=24,w=13,d=20,h=10,y=QT;
  V.shell(x,x+w-1,y,y+h,z,z+d-1,0x8b9098);
  const st=(d>>1)+1;
  for(let i=0;i<st;i++){V.box(x-1,x+w,y+h+i,y+h+i,z+i,z+i,PAL.slate2);V.box(x-1,x+w,y+h+i,y+h+i,z+d-1-i,z+d-1-i,PAL.slate2);}
  const tx=x+4,tz=z+d-3;
  V.shell(tx,tx+4,y,y+26,tz,tz+4,0x7d838b);
  for(let i=0;i<3;i++)V.box(tx-i,tx+4+i,y+27+i,y+27+i,tz-i,tz+4+i,PAL.slate);
  V.box(tx+1,tx+3,y+24,y+25,tz+1,tz+3,0x39424c);
  for(let a=tx;a<=tx+4;a+=2){VG.v(a,y+22,tz,PAL.glass);VG.v(a,y+22,tz+4,PAL.glass);}
  VG.v(tx+2,y+31,tz+2,PAL.gold);V.v(tx+2,y+32,tz+2,PAL.gold);
  /* yard */
  for(let i=0;i<22;i++){const sx=x-6+((R()*26)|0),sz=z-4+((R()*26)|0);
    V.v(sx,y+1,sz,0x9aa0a6);V.v(sx,y+2,sz,0x8b9198);if(R()<.4)V.v(sx,y+3,sz,0x7c828a);}
})();
/* trees */
function tree(x,y,z,s){
  s=s||1;
  for(let i=1;i<=3*s;i++)V.v(x,y+i,z,PAL.woodD);
  const base=y+3*s,top=base+((R()*2)|0)+2*s;
  for(let yy=base;yy<=top;yy++){
    const r=(yy===base||yy===top)?1:2;
    for(let dx=-r;dx<=r;dx++)for(let dz=-r;dz<=r;dz++){
      if(Math.abs(dx)===r&&Math.abs(dz)===r&&R()<.7)continue;
      V.v(x+dx,yy,z+dz,R()<.22?0x3c5236:(R()<.5?PAL.grn:0x5b7a4c));
    }
  }
}
for(let i=0;i<26;i++){
  const x=QX+6+((R()*58)|0), z=-66+((R()*130)|0);
  if(!isLandCell(x,z))continue;
  if(x<QX+12&&z>-26&&z<32)continue;
  tree(x,landTop(z,x),z,R()<.3?2:1);
}
/* — north quay wall (harbour mouth) + breakwater — */
for(let x=QX;x>=10;x--){
  const z=-30-Math.round((QX-x)*0.55);
  for(let y=-5;y<=6;y++)V.v(x,y,z,(y===6)?PAL.gr3:(((x+y)%4===0)?PAL.gr2:PAL.rock));
  markCell(x,z);markCell(x,z+1);
  if(y=1){}
}
for(let x=QX;x>=10;x--){
  const z=-30-Math.round((QX-x)*0.55);
  V.v(x,7,z,PAL.gr3);
  for(let y=-4;y<=4;y++){V.v(x,y,z+1,(y+z)%3===0?0x4d5a52:PAL.rock);}
  for(let y=-3;y<=2;y++)for(let yy=y;y<=y;y++)V.v(x,y,z+1,PAL.rock);
}
/* beacon at the breakwater head */
(function(){
  const x=11,z=-42;
  for(let y=7;y<=11;y++)V.box(x,x,y,y,z,z,PAL.iron);
  V.box(x-1,x+1,12,12,z-1,z+1,PAL.iron);
  VG.box(x,x,13,14,z,z,PAL.lamp);
  V.box(x-1,x+1,15,15,z-1,z+1,0x2c3238);
  lampPos.push([x,14,z]);
})();

/* — lighthouse on the rocky islet — */
const LH={x:-56,z:-46,y:7};
(function(){
  const cx=LH.x,cz=LH.z;
  for(let dx=-12;dx<=12;dx++)for(let dz=-12;dz<=12;dz++){
    const d2=dx*dx+dz*dz, rr=126+18*Math.sin(dx*0.4)+18*Math.cos(dz*0.43+1.1);
    if(d2>rr)continue;
    const h=Math.round((6.2*(1-d2/150)+1.6*Math.sin(dx*0.7)*Math.cos(dz*0.6))+2);
    const top=Math.max(1,h);
    for(let y=-4;y<=top;y++)
      V.v(cx+dx,y,cz+dz,y<=1?((dx+dz)%3===0?0x3f4c46:PAL.rock):((dx*2+dz)%5===0?0x6a6e72:PAL.rock));
    if(top>1&&R()<.3)V.v(cx+dx,top+1,cz+dz,PAL.grn);
    markCell(cx+dx,cz+dz);
  }
  /* tower */
  let r=4;
  for(let y=LH.y;y<=LH.y+30;y++){
    const band=Math.floor((y-LH.y)/4)%2===0;
    const col=band?PAL.white2:0xb5432f;
    V.shell(cx-r,cx+r,y,y,cx-r? cz-r:cz-r,cz+r,col,(a,b,c)=>((a*3+c)%6===0)?sh(col,.92):col);
    if((y-LH.y)%4===0)r--;
    if(r<2)r=2;
  }
  const ty=LH.y+30;
  V.box(cx-4,cx+4,ty+1,ty+1,cz-4,cz+4,PAL.iron);
  for(let a=-4;a<=4;a+=2){V.v(cx+a,ty+2,cz-4,PAL.iron);V.v(cx+a,ty+2,cz+4,PAL.iron);
    V.v(cx-4,ty+2,cz+a,PAL.iron);V.v(cx+4,ty+2,cz+a,PAL.iron);}
  V.shell(cx-2,cx+2,ty+3,ty+7,cz-2,cz+2,PAL.iron);
  for(let a=-2;a<=2;a++)for(let b=-2;b<=2;b++)if(Math.abs(a)===2||Math.abs(b)===2)VG.v(cx+a,ty+5,cz+b,0xffe0a0);
  VG.box(cx-1,cx+1,ty+4,ty+6,cz-1,cz+1,0xffe6b4);
  V.box(cx-3,cx+3,ty+8,ty+8,cz-3,cz+3,PAL.iron);
  for(let i=0;i<3;i++)V.box(cx-2+i,cx+2-i,ty+9+i,ty+9+i,cz-2+i,cz+2-i,0xb5432f);
  V.v(cx,ty+13,cz,PAL.gold);
  /* keeper's cottage */
  V.shell(cx-9,cx-4,LH.y+2,LH.y+6,cz+2,cz+7,PAL.cream);
  for(let i=0;i<4;i++){V.box(cx-10,cx-3,LH.y+7+i,LH.y+7+i,cz+2+i,cz+2+i,PAL.slate);
    V.box(cx-10,cx-3,LH.y+7+i,LH.y+7+i,cz+7-i,cz+7-i,PAL.slate);}
  VG.v(cx-7,LH.y+4,cz+2,PAL.glass);VG.v(cx-5,LH.y+4,cz+2,PAL.glass);
  lampPos.push([cx-6,LH.y+5,cz+2]);
})();
/* rotating beam */
const beamGroup=new THREE.Group(); beamGroup.position.set(LH.x,LH.y+5,LH.z); scene.add(beamGroup);
const beamMat=new THREE.MeshBasicMaterial({color:0xffd79a,transparent:true,opacity:.14,
  blending:THREE.AdditiveBlending,depthWrite:false,side:THREE.DoubleSide});
for(let s=0;s<2;s++){
  const g=new THREE.ConeGeometry(11,120,4,1,true);
  const m=new THREE.Mesh(g,beamMat);
  m.rotation.z=Math.PI/2; m.rotation.y=s?Math.PI:0;
  m.position.set(s?60:-60,0,0); m.renderOrder=2;
  beamGroup.add(m);
}
const lhLight=new THREE.PointLight(0xffd08a,0,180,2); lhLight.position.set(LH.x,LH.y+5,LH.z); scene.add(lhLight);
const beaconLight=new THREE.PointLight(0xffc060,0,90,2); beaconLight.position.set(11,14,-42); scene.add(beaconLight);
const lampLights=[];
[[QX+3,-22],[QX+3,8],[QX+3,28]].forEach(p=>{
  const l=new THREE.PointLight(0xffb45a,0,60,2);l.position.set(p[0],QT+11,p[1]);scene.add(l);lampLights.push(l);});

/* — moored fishing smack & rowboats — */
const boats=[];
function rowboat(x,z,rot,col){
  const g=new THREE.Group();const vb=new Vox();
  for(let z2=-3;z2<=3;z2++){
    const w=Math.round(2*Math.sqrt(Math.max(0,1-(z2/3.4)**2)))+0;
    for(let xx=-w;xx<=w;xx++){
      if(Math.abs(xx)===w)for(let y=-1;y<=0;y++)vb.v(xx,y,z2,col);
      if(z2%2===0)vb.v(xx,0,z2,sh(col,.8));
    }
  }
  vb.v(0,1,-3,PAL.woodL);vb.v(0,1,3,PAL.woodL);
  vb.line(new THREE.Vector3(0,1,0),new THREE.Vector3(0,5,-2),PAL.woodD,.22);
  const m=makeMesh(vb,matWorld,false,true);g.add(m);
  g.position.set(x,0.1,z);g.rotation.y=rot;scene.add(g);boats.push(g);return g;
}
rowboat(PIER.x0+3,PIER.z1+3,0.2,PAL.wood);
rowboat(PIER.x0-2,PIER.z0-3,-0.6,PAL.grn);
rowboat(-2,-30,1.1,0x8c6136);
function smack(x,z,rot){
  const vb=new Vox();
  for(let z2=-6;z2<=6;z2++){
    const w=Math.max(0,Math.round(3*Math.sin(Math.PI*(z2+7)/13.5)));
    for(let xx=-w;xx<=w;xx++){
      if(Math.abs(xx)===w)for(let y=-2;y<=1;y++)vb.v(xx,y,z2,(y<0)?PAL.red:PAL.wood);
      vb.v(xx,-2,z2,PAL.red); vb.v(xx,1,z2,PAL.woodL);
    }
  }
  for(let y=2;y<=17;y++)vb.v(0,y,0,PAL.mast);
  vb.box(-5,5,15,15,0,0,PAL.mastD);vb.box(-3,3,11,11,0,0,PAL.mastD);
  vb.tri(new THREE.Vector3(0,16,0),new THREE.Vector3(0,2,-5),new THREE.Vector3(0,2,2),PAL.sail2,0);
  vb.tri(new THREE.Vector3(0,15,1),new THREE.Vector3(0,2,6),new THREE.Vector3(0,2,1),PAL.sail3,1);
  vb.line(new THREE.Vector3(-5,15,0),new THREE.Vector3(-3,2,0),PAL.rope,.12);
  vb.line(new THREE.Vector3(5,15,0),new THREE.Vector3(3,2,0),PAL.rope,.12);
  vb.v(0,18,0,PAL.red);
  const g=new THREE.Group();
  const m=makeMesh(vb,matWorld,true,true);g.add(m);
  g.position.set(x,0.1,z);g.rotation.y=rot;scene.add(g);boats.push(g);
}
smack(-4,-20,1.35);

/* — buoys — */
const buoys=[];
function buoy(x,z,c){
  const g=new THREE.Group();const vb=new Vox();
  vb.box(-1,1,-2,1,z-1,z+1===z-1?z+1:z+1,c);vb.box(x-1,x+1,-2,1,z-1,z+1,c);
  const m=makeMesh(vb,matWorld,false,false);g.add(m);
  const t=new THREE.Vox?null:null;
  const vb2=new Vox();vb2.v(0,2,0,PAL.iron);vb2.v(0,3,0,PAL.iron);vb2.v(0,4,0,PAL.white2);
  g.add(makeMesh(vb2,matWorld,false,false));
  g.position.set(x,0,z);scene.add(g);buoys.push(g);
  return g;
}
buoy(-40,28,PAL.red);buoy(-52,-6,PAL.grn);

/* — distant coarse chop band (animated later) — */
const farCells=[];
for(let x=-200;x<200;x+=6)for(let z=-200;z<200;z+=6){
  if(isLandCell(x,z)||isLandCell(x+3,z)||isLandCell(x,z+3))continue;
  farCells.push([x,z]);
}

/* ═══════════════════════ 5 · THE BARQUE ═══════════════════════ */
const SHIP={x:-14,z:6,rot:-0.42};
const shipGroup=new THREE.Group();
shipGroup.rotation.order='YXZ';
shipGroup.position.set(SHIP.x,0,SHIP.z);
shipGroup.rotation.y=SHIP.rot;
scene.add(shipGroup);

(function buildShip(){
  const v=VS, g=VSG;
  const Z0=-28,Z1=29;
  function hb(z){
    if(z<=-25)return 5;
    if(z<-18)return Math.round(lerp(5,8,(z+25)/7));
    if(z<=8)return 8;
    const u=(z-8)/21;return Math.max(0,Math.round(8*Math.pow(1-u,0.8)));
  }
  function keel(z){
    if(z<-20)return -1; if(z<-14)return -2; if(z<-8)return -3; if(z<12)return -4;
    return Math.round(lerp(-4,-1,Math.pow((z-12)/17,0.9)));
  }
  function deck(z){
    let d=7;
    if(z<-14)d=7+Math.round(2*clamp((-14-z)/10,0,1));
    if(z>16)d=7+Math.round(2*clamp((z-16)/11,0,1));
    return d;
  }
  function hullCol(y,x,z,w){
    if(y<=-1)return PAL.red;
    if(y===0)return 0x5b3d27;
    if(y===3)return PAL.gold;
    if(y===5)return ((z&1)?PAL.hullD2:sh(PAL.hullD,1.12));
    return ((z&1)?PAL.hullD:PAL.hullD2);
  }
  const isPort=(y,x,z)=>(y===3&&z>=-15&&z<=11&&(((z+15)%4)===0));
  for(let z=Z0;z<=Z1;z++){
    const w=hb(z),ky=keel(z),dy=deck(z);
    const wp=hb(z-1);
    for(let x=-w;x<=w;x++){
      if(Math.abs(x)===w){
        for(let y=ky;y<=dy;y++)v.v(x,y,z,isPort(y,x,z)?0x171310:hullCol(y,x,z,w));
        if(isPort(3,x,z))v.v(x+(x>0?1:-1),3,z,PAL.iron);
        if(y=1){}
      }else{
        if(y=1){}
      }
    }
    /* wale (proud band) */
    if(z>-20&&z<14)for(let x=-w;x<=w;x++){if(Math.abs(x)===w){v.v(x+(x>0?1:-1),5,z,0x2b1e14);}}
    /* bottom planking */
    for(let x=-w;x<=w;x++)v.v(x,ky,z,0x6d2f20);
    /* deck */
    for(let x=-w;x<=w;x++)v.v(x,dy,z,(x===0)?PAL.deckD:((x+z)&1?PAL.deck:PAL.deckD));
    /* exposed transverse planking where the beam steps in */
    if(wp>w){for(let x=-wp;x<=wp;x++){if(Math.abs(x)<=w)continue;
      for(let y=keel(z);y<=dy;y++)v.v(x,y,z,(y===dy)?PAL.deckD:hullCol(y,x,z,wp));}}
    /* bulwark cap + stanchions */
    if(w>1){
      for(let x=-w;x<=w;x++){if(Math.abs(x)>=w-1)v.v(x,dy+1,z,PAL.woodL);}
      for(let x=-w;x<=w;x+=2)v.v(x,dy+2,z,PAL.woodD);
    }
  }
  /* transom (stern) */
  const wT=hb(Z0),dyT=deck(Z0);
  for(let x=-wT;x<=wT;x++)for(let y=keel(Z0);y<=dyT;y++)v.v(x,y,Z0,(y===dyT)?PAL.deckD:hullCol(y,x,Z0,wT));
  /* quarter gallery + poop house */
  for(const side of[-1,1]){
    const xx=side*(wT+1);
    for(let z=-27;z<=-22;z++)for(let y=9;y<=12;y++){
      v.v(xx,y,z,PAL.hullD2);
      if(y===10&&z%2===0)g.v(xx,y,z,PAL.glass);
    }
    v.box(xx,xx,13,13,-27,-22,PAL.gold);
  }
  v.shell(-5,5,8,12,-27,-15,PAL.hullD2,(x,y,z)=>{
    if(z===-27&&y>=9&&y<=11&&x%2===0&&Math.abs(x)<=4)return PAL.glass;
    if(y===12)return PAL.wood;
    if(y===8)return PAL.hullD;
    return ((z*3+y)%8===0)?PAL.gold:PAL.hullD2;});
  for(let x=-5;x<=5;x++)for(let z=-27;z<=-15;z+=2)v.v(x,13,z,PAL.woodL);
  for(let x=-5;x<=5;x+=2)v.v(x,14,-27,PAL.gold);
  /* forecastle */
  v.shell(-4,4,8,10,17,24,PAL.wood,(x,y,z)=>(y===10)?PAL.deckD:((x&1)?PAL.woodL:PAL.wood));
  v.box(-2,2,11,11,19,21,PAL.deckD);
  for(let x=-4;x<=4;x+=2)v.v(x,11,17,PAL.woodD);
  /* hatches & deck furniture */
  v.box(-3,3,8,8,-4,1,PAL.deckD);v.box(-3,3,8,8,8,11,PAL.deckD);
  v.box(-2,2,9,9,-3,0,PAL.woodD);
  v.box(3,5,8,9,-8,-6,PAL.woodL);v.box(-5,-3,8,9,-8,-6,PAL.woodL);
  for(let z=-13;z<=13;z+=4)v.box(-7,7,8,8,z,z,PAL.woodD);      /* carriages */
  for(let z=-13;z<=13;z+=4){v.v(0,9,z,PAL.iron);v.v(0,8,z,0x2c2f34);}
  v.box(-6,6,8,8,26,27,PAL.woodD);                               /* anchor deck */
  for(const s of[-1,1]){v.v(s*6,7,25,0x4a4a4a);v.v(s*6,6,25,0x4a4a4a);v.line(
    new THREE.Vector3(s*6,7,25.5),new THREE.Vector3(s*6,-1,26),PAL.iron,.28);}
  /* capstan */
  v.box(-1,1,8,9,4,4,PAL.woodD);v.box(-2,2,10,10,3,5,PAL.wood);
  /* masts */
  const masts=[{z:7,h:40,yard:[15,24,32,38],w:[15,11,8,5]},
               {z:-8,h:46,yard:[16,26,34,41],w:[17,13,10,6]},
               {z:-22,h:34,yard:[14,22,28],w:[12,9,6]}];
  masts.forEach((m,i)=>{
    for(let y=8;y<=m.h;y++)v.v(0,y,m.z,(y>m.h-3)?PAL.mastD:PAL.mast);
    v.v(0,m.h+1,m.z,PAL.white2);
    v.line(new THREE.Vector3(0,m.h,m.z),new THREE.Vector3(0,m.h+4,m.z),PAL.mastD,.3);
    /* top platform */
    const ty=m.yard[0]-2;
    v.box(-2,2,ty,ty,m.z-1,m.z+1,PAL.woodD);
    for(const s of[-1,1])v.v(s*2,ty+1,m.z,PAL.woodL);
    v.box(-2,2,ty,ty,m.z-1,m.z+1,PAL.wood);
    m.yard.forEach((yy,k)=>{
      const hw=m.w[k];
      v.box(-hw-1,hw+1,yy,yy,m.z,m.z,PAL.mastD);
      v.v(-hw-1,yy,m.z,0x3f2c19);v.v(hw+1,yy,m.z,0x3f2c19);
      const full=(i===2&&k>1)?false:(k===3?false:true);
      const drop=(i===2&&k===1)?4:(k===0&&i<2?9:(k===1?7:(k===2?5:4)));
      if(full){
        const belly=(k===0&&i===1)?4:(k===0?3:2);
        for(let x=-hw;x<=hw;x++){
          const xn=Math.abs(x)/hw;
          for(let r=0;r<drop;r++){
            const y=yy-1-r;
            const bul=Math.round(belly*Math.sin(Math.PI*(r/drop+0.06))*(1-0.22*xn*xn));
            let c=(r%4===3)?PAL.sail2:((r===0)?PAL.sail:((x%5===0)?PAL.sail3:PAL.sail));
            v.v(x,y,m.z-bul,c);
          }
          v.v(x,yy-drop,m.z-1,PAL.sail2);
        }
      }else{ /* furled */
        for(let x=-hw;x<=hw;x++)for(let r=1;r<=2;r++)v.v(x,yy-r,m.z-(r===2?1:0),PAL.sail2);
      }
      /* braces */
      v.line(new THREE.Vector3(hw+1,yy,m.z),new THREE.Vector3(8,10,m.z+7),PAL.rope,.14);
      v.line(new THREE.Vector3(-hw-1,yy,m.z),new THREE.Vector3(-8,10,m.z+7),PAL.rope,.14);
    });
    /* shrouds */
    for(const s of[-1,1]){
      for(let k=0;k<5;k++){
        const bx=s*(7+ (k<2?0:1)), bz=m.z-3+k*1.6;
        v.line(new THREE.Vector3(bx,9,bz),new THREE.Vector3(s*2,ty,m.z),PAL.rope,.13);
        v.line(new THREE.Vector3(bx,9,bz),new THREE.Vector3(s*2,m.h-2,m.z),PAL.rope,.11);
      }
      /* ratlines */
      for(let y=11;y<ty;y+=2)v.line(new THREE.Vector3(-7,y,m.z-2),new THREE.Vector3(7,y,m.z-2),PAL.rope,.08);
    }
    v.line(new THREE.Vector3(0,m.h,m.z),new THREE.Vector3(0,m.h,m.z+1),PAL.white2,.2);
  });
  /* stays */
  v.line(new THREE.Vector3(0,46,-8),new THREE.Vector3(0,40,7),PAL.rope,.14);
  v.line(new THREE.Vector3(0,40,7),new THREE.Vector3(0,26,23),PAL.rope,.14);
  v.line(new THREE.Vector3(0,34,-22),new THREE.Vector3(0,26,-8),PAL.rope,.14);
  /* bowsprit */
  for(let i=0;i<=18;i++){
    const t=i/18;
    v.v(0,Math.round(9+t*7),Math.round(26+t*19),i<4?PAL.mastD:PAL.mast);
  }
  v.line(new THREE.Vector3(0,9,26),new THREE.Vector3(0,16,45),PAL.rope,.16);
  v.line(new THREE.Vector3(-3,10,29),new THREE.Vector3(0,14,44),PAL.rope,.12);
  v.line(new THREE.Vector3(3,10,29),new THREE.Vector3(0,14,44),PAL.rope,.12);
  v.line(new THREE.Vector3(0,16,45),new THREE.Vector3(0,38,7),PAL.rope,.14);
  /* jibs */
  v.tri(new THREE.Vector3(0,38,7),new THREE.Vector3(0,17,44),new THREE.Vector3(0,20,26),PAL.sail,2.6);
  v.tri(new THREE.Vector3(0,31,7),new THREE.Vector3(0,14,41),new THREE.Vector3(0,15,20),PAL.sail2,2.2);
  /* spanker */
  v.tri(new THREE.Vector3(0,26,-22),new THREE.Vector3(0,15,-31),new THREE.Vector3(0,9,-23),PAL.sail,1.6);
  v.line(new THREE.Vector3(0,15,-22),new THREE.Vector3(0,15,-31),PAL.mastD,.25);
  v.line(new THREE.Vector3(0,9,-22),new THREE.Vector3(0,9,-31),PAL.mastD,.25);
  /* anchor hanging at the bow + rope ladder to the water */
  v.line(new THREE.Vector3(6,8,22),new THREE.Vector3(9,0,24),PAL.rope,.14);
  for(let y=7;y>=0;y--){v.v(6,y,21,PAL.woodL);v.v(7,y,21,PAL.woodL);if(y%2===0)v.line(new THREE.Vector3(6,y,21),new THREE.Vector3(7,y,21),PAL.rope,.1);}
})();
const shipMesh=makeMesh(VS,matShip,true,true); shipGroup.add(shipMesh);
const shipGlow=makeMesh(VSG,matGlow,false,false); shipGroup.add(shipGlow);
/* mark the water out under the hull */
(function(){
  const c=Math.cos(SHIP.rot),s=Math.sin(SHIP.rot);
  for(let z=-29;z<=30;z++){
    const w=(z<=-25)?5:(z<-18)?Math.round(lerp(5,8,(z+25)/7)):(z<=8?8:Math.max(0,Math.round(8*Math.pow(1-(z-8)/21,0.8))));
    for(let x=-w-1;x<=w+1;x++){
      const wx=SHIP.x+(x*c+z*s), wz=SHIP.z+(z*c-x*s);
      markCell(Math.round(wx),Math.round(wz));
    }
  }
})();

/* — fluttering flags (separate so they can wave) — */
const flags=[];
function flag(x,y,z,w,h,cols,dir){
  const grp=new THREE.Group();grp.position.set(x,y,z);shipGroup.add(grp);
  const mats=[],meshes=[];
  const geo=new THREE.BoxGeometry(1,1,0.18);
  for(let i=0;i<w;i++){
    mats.push(new THREE.MeshLambertMaterial({color:cols[i][0]}));
    const col=new THREE.Group();grp.add(col);
    for(let j=0;j<h;j++){
      const m=new THREE.Mesh(geo,mats[Math.min(mats.length-1,Math.floor(i/w*cols.length))]);
      m.material=new THREE.MeshLambertMaterial({color:cols[i][1]!==undefined?cols[i][1]:cols[i][0]});
      m.position.set(i+0.5,j+0.5,0);col.add(m);
    }
    meshes.push(col);
  }
  grp.userData={meshes,w,dir:dir||1};
  flags.push(grp);return grp;
}
(function(){
  const geo=new THREE.BoxGeometry(1,1,0.2);
  function ensign(x,y,z,base,cross){
    const grp=new THREE.Group();grp.position.set(x,y,z);shipGroup.add(grp);
    const w=7,h=4,cols=[];
    for(let i=0;i<w;i++){cols[i]=[];for(let j=0;j<h;j++){
      const on=(i===Math.floor(w/2)||j===Math.floor(h/2));
      const m=new THREE.Mesh(geo,new THREE.MeshLambertMaterial({color:on?cross:base}));
      m.position.set(i+0.5,j+0.5,0);grp.add(m);cols[i][j]=m;}}
    grp.userData={cols,w,h};flags.push(grp);return grp;
  }
  ensign(0,47,-22,0xb5271f,0xf2f0e6);
  ensign(0,41,-8,0xb5271f,0xf2f0e6);
  /* jack at the bowsprit tip */
  const j=new THREE.Group();j.position.set(0,17,44);shipGroup.add(j);
  const jc=[];for(let i=0;i<5;i++){jc[i]=[];for(let k=0;k<3;k++){
    const m=new THREE.Mesh(new THREE.BoxGeometry(1,1,0.2),
      new THREE.MeshLambertMaterial({color:((i+k)%2)?0x1e4f8f:0xf2f0e6}));
    m.position.set(i+0.5,k+0.5,0);j.add(m);jc[i][k]=m;}}
  j.userData={cols:jc,w:5,h:3};flags.push(j);
  /* string of signal flags between the masts */
  const cols=[0xb5271f,0x1e4f8f,0xf2c14e,0x2f7d4f,0xf2f0e6,0x2b2b2b];
  const pts=[[0,44,-8],[0,38,7],[0,32,-22]];
  const sg=new THREE.Group();shipGroup.add(sg);
  const seq=[];
  for(let a=0;a<2;a++){
    const p1=new THREE.Vector3(...pts[a]),p2=new THREE.Vector3(...pts[a+1]);
    for(let i=1;i<9;i++){
      const t=i/9;const p=p1.clone().lerp(p2,t);p.y-=Math.sin(Math.PI*t)*3.2;p.x+=(i%2?0.6:-0.6);
      const m=new THREE.Mesh(new THREE.BoxGeometry(1.1,1.1,0.15),
        new THREE.MeshLambertMaterial({color:cols[(i+a*3)%cols.length]}));
      m.position.copy(p);sg.add(m);seq.push({m,base:p.clone(),ph:i*0.8});
    }
  }
  sg.userData={seq};flags.push(sg);
})();

/* — clouds — */
const cloudGroup=new THREE.Group();scene.add(cloudGroup);
(function(){
  const cv=new Vox();
  for(let i=0;i<34;i++){
    const cx=-420+R()*840, cy=95+R()*70, cz=-420+R()*840;
    const w=8+((R()*16)|0), d=6+((R()*14)|0), h=2+((R()*3)|0);
    for(let x=0;x<w;x++)for(let z=0;z<d;z++)for(let y=0;y<h;y++){
      if(R()<0.35)continue;
      const t=(1-(y/h))*0.5+R()*0.3;
      cv.v(cx+x,cy+y,cz+z, t>0.62?0xffffff:(t>0.36?0xf0f2f5:0xd3dbe3));
    }
  }
  const m=makeMesh(cv,matCloud,false,false);m.castShadow=false;cloudGroup.add(m);
})();

/* — gulls — */
const gullGroup=new THREE.Group();scene.add(gullGroup);
const gulls=[];
(function(){
  const white=new THREE.MeshLambertMaterial({color:0xf4f5f3});
  const dark=new THREE.MeshLambertMaterial({color:0x9fa9b2});
  const beakM=new THREE.MeshLambertMaterial({color:0xe8a33d});
  const bg=new THREE.BoxGeometry(0.9,0.55,2.2), wg=new THREE.BoxGeometry(2.8,0.16,0.9);
  for(let i=0;i<9;i++){
    const gr=new THREE.Group();
    const body=new THREE.Mesh(bg,white);gr.add(body);
    const tail=new THREE.Mesh(new THREE.BoxGeometry(0.5,0.12,0.9),dark);tail.position.set(0,0.05,-1.35);gr.add(tail);
    const bk=new THREE.Mesh(new THREE.BoxGeometry(0.26,0.2,0.7),beakM);bk.position.set(0,0.05,1.4);gr.add(bk);
    const pl=new THREE.Group(),pr=new THREE.Group();
    const wl=new THREE.Mesh(wg,white);wl.position.set(-1.5,0.1,0);pl.add(wl);
    const wr=new THREE.Mesh(wg,white);wr.position.set(1.5,0.1,0);pr.add(wr);
    gr.add(pl);gr.add(pr);
    gr.scale.setScalar(1.5);
    gr.userData={pl,pr,cx:-20+R()*70,cz:-30+R()*70,r:26+R()*40,h:26+R()*26,s:0.16+R()*0.14,ph:R()*6.28};
    gullGroup.add(gr);gulls.push(gr);
  }
})();

/* — chimney smoke — */
const puffs=[];
(function(){
  const chs=chimneys.concat(chim).filter(c=>c&&isLandCell(Math.round(c[0]),Math.round(c[2])));
  const geo=new THREE.BoxGeometry(1.4,1.4,1.4);
  chs.slice(0,7).forEach(c=>{
    for(let i=0;i<5;i++){
      const mat=new THREE.MeshLambertMaterial({color:0xb9c2c9,transparent:true,opacity:.5});
      const m=new THREE.Mesh(geo,mat);
      m.position.set(c[0]+(R()-.5),c[1]+i*2.2,c[2]+(R()-.5));
      m.userData={y0:c[1],x:c[0],z:c[2],t:R()*4.4,sp:1.6+R()*0.9};
      scene.add(m);puffs.push(m);
    }
  });
})();

/* — swinging crane on the quay — */
const crane=new THREE.Group();crane.position.set(QX+2,QT,-12);scene.add(crane);
(function(){
  const cv=new Vox();
  for(let y=1;y<=12;y++){cv.v(0,y,0,PAL.woodD);cv.v(0,y,1,PAL.woodD);}
  for(let y=2;y<=12;y+=3)cv.line(new THREE.Vector3(1,y,0.5),new THREE.Vector3(0,y+3,0.5),PAL.wood,.2);
  cv.box(-1,2,13,13,0,1,PAL.wood);
  cv.line(new THREE.Vector3(1,13,0.5),new THREE.Vector3(9,10,0.5),PAL.wood,.4);
  cv.line(new THREE.Vector3(1,16,0.5),new THREE.Vector3(9,10.5,0.5),PAL.rope,.14);
  cv.line(new THREE.Vector3(1,13,0.5),new THREE.Vector3(1,17,0.5),PAL.woodD,.4);
  const m=makeMesh(cv,matWorld,true,true);crane.add(m);
  const hook=new THREE.Group();hook.position.set(9,10,0.5);crane.add(hook);
  const hv=new Vox();
  hv.line(new THREE.Vector3(0,0,0),new THREE.Vector3(0,-3.5,0),PAL.rope,.11);
  hv.box(-1,1,-6,-4,0,1,PAL.woodL);
  hook.add(makeMesh(hv,matWorld,true,true));
  crane.userData={hook};
})();

/* ═══════════════════════ 6 · ANIMATED SEA ═══════════════════════ */
let water,waterN,wx,wy0,wph,wamp,wfx,wfz,wbase,wcrest,wmArr,wcArr;
(function buildWater(){
  const STEP=2,HALF=96;
  const A=[],P=[],Y=[],AMP=[],FX=[],FZ=[],B=[],CR=[];
  for(let x=-HALF;x<HALF;x+=STEP)for(let z=-HALF;z<HALF;z+=STEP){
    if(isLandCell(x,z)||isLandCell(x+1,z)||isLandCell(x,z+1))continue;
    const dx=x-landEdge(z), dzOut=z;
    const depth=(x<landEdge(z))?(landEdge(z)-x):0;
    const shore=clamp(1-depth/26,0,1);
    let f=1;
    if(x>-46&&x<16&&z>-36&&z<36)f=0.55;          /* sheltered basin */
    if(x<-100&&z<-100)f=1.25;
    const amp=(0.55+0.85*f);
    /* foam around the ship hull & pier */
    const c=Math.cos(SHIP.rot),s=Math.sin(SHIP.rot);
    const lx=(x-SHIP.x),lz=(z-SHIP.z);
    const sx=lx*c-lz*s, sz=lx*s+lz*c;
    let foam=0;
    if(sx>-30&&sx<31&&sz>-10&&sz<10){
      const hw=(sz<=-25)?5:(sz<-18)?lerp(5,8,(sz+25)/7):(sz<=8?8:Math.max(0,8*Math.pow(1-(sz-8)/21,0.8)));
      const d=Math.abs(sx)-hw-1.2;
      if(d>-1.6&&d<3.2)foam=Math.max(foam,clamp(1-Math.abs(d-0.6)/2.6,0,1));
    }
    if(x>=PIER.x0-2&&x<=PIER.x1+1&&z>=PIER.z0-2&&z<=PIER.z1+2)
      foam=Math.max(foam,clamp(1-Math.max(Math.abs(x-(PIER.x1+0.5))/3,Math.abs(z-(PIER.z0+PIER.z1)/2*0-8.8))/2.4,0,1)*0.85);
    for(const b of[[11,-42],[-56,-46]]){
      const dd=Math.hypot(x-b[0],z-b[1]);
      if(dd<16&&dd>10)foam=Math.max(foam,clamp(1-(dd-11)/5,0,1));
    }
    const deep=clamp(depth/60,0,1);
    const base=new THREE.Color(0x2b9fb3).lerp(new THREE.Color(0x11456b),Math.max(deep,shore*0));
    if(shore>0.55)base.lerp(new THREE.Color(0x4ec5c8),0.35*shore);
    const crest=base.clone().lerp(new THREE.Color(0xe8fbff),0.55).lerp(new THREE.Color(0xffffff),0.25);
    A.push(x);P.push(z);Y.push(-0.6);AMP.push(amp);FX.push(foam);FZ.push(f);
    B.push(base.r,base.g,base.b);CR.push(crest.r,crest.g,crest.b);
  }
  waterN=A.length;
  wx=new Float32Array(A);
  const wz=new Float32Array(P);
  wy0=new Float32Array(Y);wph=new Float32Array(wz.length);wamp=new Float32Array(AMP);wfx=new Float32Array(FX);
  for(let i=0;i<waterN;i++)wph[i]=R()*6.283;
  wbase=new Float32Array(B);wcrest=new Float32Array(CR);
  const wq=new Float32Array(wz);
  water=new THREE.InstancedMesh(boxGeo,matWater,waterN);
  wmArr=water.instanceMatrix.array;wcArr=new Float32Array(waterN*3);
  const col=new THREE.Color();
  for(let i=0;i<waterN;i++){
    const o=i*16;
    wmArr[o]=2;wmArr[o+5]=3.4;wmArr[o+10]=2;wmArr[o+15]=1;
    wmArr[o+12]=wx[i]+1;wmArr[o+13]=0;wmArr[o+14]=wq[i]+1;
    col.setRGB(wbase[i*3],wbase[i*3+1],wbase[i*3+2]);
    water.setColorAt(i,col);
  }
  water.instanceMatrix.needsUpdate=true;
  water.instanceColor.needsUpdate=true;
  water.frustumCulled=false;water.receiveShadow=true;water.castShadow=false;
  water.__z=wq;
  scene.add(water);
})();

let farWater=null;
(function buildFar(){
  const cv=new Vox();
  const c1=new THREE.Color(0x14536f),c2=new THREE.Color(0x1b6b86);
  for(const [x,z] of farCells){
    const n=Math.sin(x*0.031)*Math.cos(z*0.027)+Math.sin((x+z)*0.019);
    const c=(n>0?c1:c2).clone().lerp(new THREE.Color(0x2a86a0),clamp(n*0.5+0.5,0,1)*0.5);
    cv.add(x,-2+0.5*n,z,6,5,6,c.getHex(),null);
  }
  farWater=makeMesh(cv,matWater,false,true);
  scene.add(farWater);
})();

/* ═══════════════════════ 7 · TIME OF DAY ═══════════════════════ */
const STOPS=[
 {t:0.00,e:0.03,a:-1.25,sun:0xff9a58,si:0.42,hs:0x3f5d80,hg:0x2a2e38,hi:0.5,top:0x18274a,hor:0xdd8858,fog:0x8d7b80,cl:0xe8b9a0,glow:1.00,name:'CIVILITY DAWN',clk:'05:20'},
 {t:0.24,e:0.42,a:-0.55,sun:0xffd39a,si:0.92,hs:0x9dc4e2,hg:0x40494c,hi:0.6,top:0x2f6b9e,hor:0xd9e2e6,fog:0xa8bfc9,cl:0xf6f2ee,glow:0.22,name:'MORNING WORK',clk:'08:10'},
 {t:0.50,e:1.02,a: 0.15,sun:0xfff4e0,si:1.12,hs:0xb0d6ef,hg:0x4c544a,hi:0.7,top:0x2c74b4,hor:0xd6e6ee,fog:0xc0d5de,cl:0xffffff,glow:0.00,name:'HIGH NOON',clk:'12:30'},
 {t:0.74,e:0.30,a: 2.62,sun:0xffc178,si:1.02,hs:0x9dc0da,hg:0x4d473c,hi:0.58,top:0x2a5f96,hor:0xf2b878,fog:0xd2a888,cl:0xffdcbc,glow:0.30,name:'THE GOLDING',clk:'17:40'},
 {t:0.90,e:0.07,a: 2.95,sun:0xff7f42,si:0.55,hs:0x5c7196,hg:0x2f2a30,hi:0.48,top:0x1c2a4f,hor:0xd06a3a,fog:0x87606c,cl:0xc98d78,glow:0.82,name:'DUSK WATCH',clk:'20:05'},
 {t:1.00,e:0.30,a: 1.05,sun:0x93a9d8,si:0.20,hs:0x2c3d60,hg:0x171c26,hi:0.42,top:0x0b1330,hor:0x2b3557,fog:0x212b45,cl:0x3d4867,glow:1.00,name:'NIGHT AT ANCHOR',clk:'23:15'}
];
const tmpA=new THREE.Color(),tmpB=new THREE.Color();
function mixStop(k,f,target){
  const a=STOPS[k],b=STOPS[k+1];
  for(const key of ['sun','hs','hg','top','hor','fog','cl'])
    target[key]=tmpA.setHex(a[key]).lerp(tmpB.setHex(b[key]),f).getHex();
  target.e=lerp(a.e,b.e,f);target.a=lerp(a.a,b.a,f);target.si=lerp(a.si,b.si,f);
  target.hi=lerp(a.hi,b.hi,f);target.glow=lerp(a.glow,b.glow,f);
  target.name=f<0.5?a.name:b.name;target.clk=f<0.5?a.clk:b.clk;
  return target;
}
const cur={};
function setTime(t){
  t=clamp(t,0,1);
  let k=0;while(k<STOPS.length-2&&t>STOPS[k+1].t)k++;
  const f=(t-STOPS[k].t)/(STOPS[k+1].t-STOPS[k].t);
  mixStop(k,clamp(f,0,1),cur);
  const el=cur.e,az=cur.a;
  const dir=new THREE.Vector3(Math.sin(az)*Math.cos(el),Math.max(0.03,Math.sin(el)),Math.cos(az)*Math.cos(el)).normalize();
  sun.position.copy(dir).multiplyScalar(430).add(new THREE.Vector3(0,10,0));
  sun.color.setHex(cur.sun);sun.intensity=cur.si;
  hemi.color.setHex(cur.hs);hemi.groundColor.setHex(cur.hg);hemi.intensity=cur.hi;
  skyU.uTop.value.setHex(cur.top);skyU.uHor.value.setHex(cur.hor);
  skyU.uSun.value.copy(dir);skyU.uSunCol.value.setHex(cur.sun);skyU.uCloud.value.setHex(cur.cl);
  scene.fog.color.setHex(cur.fog);
  renderer.setClearColor(cur.fog);
  const dk=cur.glow;
  matGlow.color.setRGB(0.36+dk*0.74,0.32+dk*0.72,0.28+dk*0.66);
  lhLight.intensity=dk*2.6; beaconLight.intensity=dk*1.5;
  lampLights.forEach(l=>l.intensity=dk*1.1);
  beamMat.opacity=0.05+dk*0.22;
  matWater.color.setRGB(0.5+0.5*(1-dk*0.55),0.55+0.45*(1-dk*0.55),0.62+0.38*(1-dk*0.5));
  matCloud.color.setHex(cur.cl);
  matCloud.opacity=0.96;
  fill.intensity=0.12+0.16*(1-dk);
}
let tod=0.735/1;
setTime(0.735);

/* ═══════════════════════ 8 · CAMERA RIG (hand-made orbit) ═══════════════════════ */
const VIEWS=[
 {t:[ 8,8,-14], th:-2.12, ph:1.28, r:64},
 {t:[-14,17,4], th:-2.55, ph:1.16, r:38},
 {t:[-56,42,-46],th:-0.55, ph:1.24, r:96},
 {t:[-14,40,1], th:-2.4,  ph:1.35, r:26},
 {t:[ 0,16,0],  th:-0.72, ph:0.62, r:215},
 {t:[-30,4,10], th:-1.35, ph:1.42, r:44}
];
const rig={
  th:VIEWS[0].th,ph:VIEWS[0].ph,r:VIEWS[0].r,
  tth:VIEWS[0].th,tph:VIEWS[0].ph,tr:VIEWS[0].r,
  tgt:new THREE.Vector3(...VIEWS[0].t),ttgt:new THREE.Vector3(...VIEWS[0].t),
  damp:8,orbit:true
};
function applyCam(){
  const sp=Math.sin(rig.ph),cp=Math.cos(rig.ph);
  camera.position.set(
    rig.tgt.x+rig.r*sp*Math.sin(rig.th),
    rig.tgt.y+rig.r*cp,
    rig.tgt.z+rig.r*sp*Math.cos(rig.th));
  camera.lookAt(rig.tgt);
}
applyCam();

let drag=null,moved=0;
canvas.addEventListener('contextmenu',e=>e.preventDefault());
canvas.addEventListener('pointerdown',e=>{
  canvas.setPointerCapture(e.pointerId);
  drag={x:e.clientX,y:e.clientY,btn:e.button,moved:0};
  canvas.classList.add('drag');rig.damp=14;
});
canvas.addEventListener('pointermove',e=>{
  if(!drag)return;
  const dx=e.clientX-drag.x,dy=e.clientY-drag.y;drag.x=e.clientX;drag.y=e.clientY;
  drag.moved+=Math.abs(dx)+Math.abs(dy);
  if(drag.btn===2||drag.btn===1||e.shiftKey){
    const s=rig.r*0.0016;
    const right=new THREE.Vector3().setFromMatrixColumn(camera.matrix,0);
    const up=new THREE.Vector3().setFromMatrixColumn(camera.matrix,1);
    rig.ttgt.addScaledVector(right,-dx*s).addScaledVector(up,dy*s);
    rig.ttgt.y=clamp(rig.ttgt.y,-6,120);
    rig.ttgt.x=clamp(rig.ttgt.x,-260,260);rig.ttgt.z=clamp(rig.ttgt.z,-260,260);
  }else{
    rig.tth-=dx*0.0052; rig.tph=clamp(rig.tph-dy*0.0044,0.10,1.52);
  }
});
function endDrag(e){if(!drag)return;drag=null;canvas.classList.remove('drag');rig.damp=8;}
canvas.addEventListener('pointerup',endDrag);canvas.addEventListener('pointercancel',endDrag);
canvas.addEventListener('wheel',e=>{
  e.preventDefault();
  rig.tr=clamp(rig.tr*Math.exp(clamp(e.deltaY,-140,140)*0.0011),16,520);
},{passive:false});
canvas.addEventListener('dblclick',e=>{
  const nd=new THREE.Vector2((e.clientX/innerWidth)*2-1,-(e.clientY/innerHeight)*2+1);
  const rc=new THREE.Raycaster();rc.setFromCamera(nd,camera);
  const hit=rc.intersectObjects([shipMesh,water,farWater].filter(Boolean),false)[0];
  if(hit){rig.ttgt.copy(hit.point);rig.ttgt.y=clamp(hit.point.y,2,44);rig.damp=3.2;
    clearTimeout(rig._rt);rig._rt=setTimeout(()=>rig.damp=8,1600);}
});
/* touch pinch */
let pinch=0;
canvas.addEventListener('touchmove',e=>{
  if(e.touches.length===2){
    const d=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,e.touches[0].clientY-e.touches[1].clientY);
    if(pinch)rig.tr=clamp(rig.tr*(pinch/d),16,520);
    pinch=d;
  }
},{passive:true});
canvas.addEventListener('touchend',()=>pinch=0);

/* ═══════════════════════ 9 · UI ═══════════════════════ */
const $=s=>document.querySelector(s);
const elTod=$('#tod'),elSea=$('#sea');
let seaAmp=1.0;
function syncTod(){
  tod=(+elTod.value)/1000;setTime(tod);
  const nm=cur.name||'GOLDING';
  $('#todLbl').textContent=nm;$('#rPhase').textContent=nm;$('#rClock').textContent=cur.clk||'17:40';
}
elTod.addEventListener('input',syncTod);
elSea.addEventListener('input',()=>{
  const v=(+elSea.value)/100;seaAmp=0.25+v*2.1;
  const st=Math.round(1+v*5);
  $('#seaLbl').textContent=st+' · '+(st<2?'FLAT':st<3?'SLIGHT':st<4?'MODERATE':st<5?'ROUGH':'HEAVY');
  $('#rSea').textContent=st;
});
let curView=0;
function setView(i){
  curView=i;const v=VIEWS[i];
  rig.tth=v.th;rig.tph=v.ph;rig.tr=v.r;rig.ttgt.set(...v.t);rig.damp=3.0;
  clearTimeout(rig._rt);rig._rt=setTimeout(()=>rig.damp=8,1800);
  document.querySelectorAll('.v').forEach(b=>b.classList.toggle('on',+b.dataset.v===i));
  rig.orbit=false;$('#tOrbit').classList.remove('on');
}
document.querySelectorAll('.v').forEach(b=>b.addEventListener('click',()=>setView(+b.dataset.v)));
function tog(id,fn){const el=$(id);el.addEventListener('click',()=>{el.classList.toggle('on');fn(el.classList.contains('on'));});}
tog('#tOrbit',v=>rig.orbit=v);
tog('#tGulls',v=>gullGroup.visible=v);
tog('#tBeam',v=>beamGroup.visible=v);
addEventListener('keydown',e=>{
  const k=e.key.toLowerCase();
  if('123456'.includes(k))setView(+k-1);
  if(k==='r')$('#tOrbit').click();
  if(k==='n'){elTod.value=985;syncTod();}
  if(k==='g'){elTod.value=735;syncTod();}
  if(k==='d'){elTod.value=500;syncTod();}
});
/* compass ticks */
(function(){
  const g=document.getElementById('ticks');let s='';
  for(let i=0;i<36;i++){
    const a=i*10*Math.PI/180,L=(i%9===0)?9:4;
    s+=`<line x1="${Math.sin(a)*36}" y1="${-Math.cos(a)*36}" x2="${Math.sin(a)*(36-L)}" y2="${-Math.cos(a)*(36-L)}"
      stroke="rgba(168,197,214,${i%9===0?0.75:0.3})" stroke-width="${i%9===0?1.4:0.9}"/>`;
  }
  g.innerHTML=s;
})();
const rose=$('#rose'),rBrg=$('#rBrg'),rRng=$('#rRng');
setTimeout(()=>document.querySelectorAll('.reveal').forEach((el,i)=>{
  el.style.transitionDelay=(i*0.13)+'s';el.classList.add('in');
}),500);

/* ═══════════════════════ 10 · LOOP ═══════════════════════ */
const clock=new THREE.Clock();
let frame=0,acc=0;
function tick(){
  requestAnimationFrame(tick);
  const dt=Math.min(0.05,clock.getDelta()),T=clock.elapsedTime;
  skyU.uTime.value=T;

  /* ── sea ── */
  const z=water.__z,A=wmArr,C=water.instanceColor.array;
  const t1=T*1.15,t2=T*0.86,t3=T*1.7;
  for(let i=0;i<waterN;i++){
    const x=wx[i],zz=z[i];
    const wv=Math.sin(x*0.061+t1)*0.55+Math.sin(zz*0.079-t2)*0.42+Math.sin((x*0.037+zz*0.052)+t3)*0.36;
    A[i*16+13]=wy0[i]+wv*wamp[i]*seaAmp;
    const k=clamp(0.45+wv*0.34+wfx[i],0,1);
    const j=i*3;
    C[j]  =wbase[j]  +(wcrest[j]  -wbase[j])  *k;
    C[j+1]=wbase[j+1]+(wcrest[j+1]-wbase[j+1])*k;
    C[j+2]=wbase[j+2]+(wcrest[j+2]-wbase[j+2])*k;
  }
  water.instanceMatrix.needsUpdate=true;
  water.instanceColor.needsUpdate=true;

  /* ── ship ── */
  shipGroup.position.y=Math.sin(T*0.85)*0.26*seaAmp+Math.sin(T*1.7+1.2)*0.09;
  shipGroup.rotation.z=Math.sin(T*0.72+0.4)*0.020*seaAmp;
  shipGroup.rotation.x=Math.sin(T*0.53)*0.013*seaAmp;

  /* ── flags ── */
  for(const f of flags){
    if(f.userData.cols){
      const {cols,w,h}=f.userData;
      for(let i=0;i<w;i++)for(let j=0;j<h;j++){
        const m=cols[i][j];if(!m)continue;
        const ph=T*7-i*0.85+j*0.14;
        m.position.z=Math.sin(ph)*(0.16+i*0.10);
        m.position.y=j+0.5+Math.sin(ph*0.8)*0.09*(i/w);
        m.rotation.y=Math.cos(ph)*0.20*(i/w);
        m.rotation.x=Math.sin(ph*1.1)*0.10;
      }
    }else if(f.userData.meshes){
      f.userData.meshes.forEach((col,i)=>{
        col.children.forEach(m=>{
          const ph=T*7-i*0.8;
          m.position.z=Math.sin(ph)*(0.14+i*0.09);m.rotation.y=Math.cos(ph)*0.22*(i/f.userData.w);
        });
      });
    }else if(f.userData.seq){
      for(const s of f.userData.seq){
        const ph=T*3.4+s.ph;
        s.m.position.copy(s.base);
        s.m.position.z+=Math.sin(ph)*0.5;s.m.position.y+=Math.sin(ph*0.7)*0.22;
        s.m.rotation.y=Math.sin(ph*0.9)*0.4;s.m.rotation.z=Math.cos(ph)*0.18;
      }
    }
  }

  /* ── boats & buoys ── */
  boats.forEach((b,i)=>{
    b.position.y=0.1+Math.sin(T*1.1+i*1.7)*0.24*seaAmp;
    b.rotation.z=Math.sin(T*0.9+i)*0.045*seaAmp;
    b.rotation.x=Math.sin(T*0.7+i*0.6)*0.03*seaAmp;
  });
  buoys.forEach((b,i)=>{
    b.position.y=Math.sin(T*1.4+i*2.1)*0.35*seaAmp;b.rotation.z=Math.sin(T*1.1+i)*0.12*seaAmp;
  });

  /* ── gulls ── */
  if(gullGroup.visible)for(const gr of gulls){
    const u=gr.userData,a=T*u.s+u.ph;
    gr.position.set(u.cx+Math.cos(a)*u.r,u.h+Math.sin(T*0.8+u.ph)*2.4,u.cz+Math.sin(a)*u.r);
    gr.rotation.y=-a;
    gr.rotation.z=Math.sin(T*0.9+u.ph)*0.18;
    const fl=Math.sin(T*8.5+u.ph);
    u.pl.rotation.z=-fl*0.62;u.pr.rotation.z=fl*0.62;
  }

  /* ── smoke ── */
  for(const p of puffs){
    p.userData.t+=dt*p.userData.sp;
    if(p.userData.t>4.6){p.userData.t=0;p.position.set(p.userData.x+(R()-.5)*1.2,p.userData.y0,p.userData.z+(R()-.5)*1.2);}
    p.position.y=p.userData.y0+p.userData.t*1.9;
    p.position.x=p.userData.x+Math.sin(p.userData.t*0.9)*p.userData.t*0.5+p.userData.t*0.35;
    const s=0.7+p.userData.t*0.55;p.scale.setScalar(s);
    p.material.opacity=clamp(0.5-p.userData.t/9.6,0,0.5);
    p.rotation.y=p.userData.t*0.4;
  }

  /* ── misc life ── */
  beamGroup.rotation.y+=dt*0.42;
  cloudGroup.position.x=((T*2.4)%900)-40;
  crane.userData.hook.rotation.z=Math.sin(T*0.8)*0.09;
  crane.userData.hook.position.y=10+Math.sin(T*0.6)*0.35;
  lampLights.forEach((l,i)=>l.intensity=(cur.glow*1.1)*(0.82+0.18*Math.sin(T*7+i*2.3)+0.06*Math.sin(T*23+i)));
  lhLight.intensity=cur.glow*(2.3+0.3*Math.sin(T*3.1));

  /* ── camera ── */
  if(rig.orbit&&!drag)rig.tth+=dt*0.038;
  const k=1-Math.exp(-rig.damp*dt);
  rig.th+=(rig.tth-rig.th)*k;rig.ph+=(rig.tph-rig.ph)*k;rig.r+=(rig.tr-rig.r)*k;
  rig.tgt.lerp(rig.ttgt,k);
  applyCam();
  const brg=(((-rig.th*180/Math.PI)%360)+360)%360;
  rose.style.transform=`rotate(${brg}deg)`;
  rBrg.textContent=String(Math.round(brg)).padStart(3,'0')+'°';
  rRng.textContent=Math.round(rig.r);

  acc+=dt;frame++;
  if(acc>0.5){acc=0;}
  renderer.render(scene,camera);
}
addEventListener('resize',()=>{
  camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight);
});
syncTod();
renderer.render(scene,camera);
tick();
setTimeout(()=>{const l=document.getElementById('load');l.classList.add('gone');setTimeout(()=>l.remove(),900);},900);
})();
</script>
</body>
</html>
```

**What's in the bay**

- **The barque herself** — hull planked strake by strake from a real shear/keel/beam profile: copper sheathing below the waterline, gold gun‑deck stripe with 12 protruding cannon, quarter galleries, poop deck with lit stern windows, forecastle, capstan, hatches, three masts with yards, shrouds and ratlines, a belaying‑pin‑less but honest rig, partly furled sails with sewn canvas seams, jibs, a spanker, and a dressing of signal flags strung mast to mast. She rolls, pitches and rides on the swell, and her ensigns actually flutter per‑vertex.
- **The harbour** — granite quay with hand‑tinted setts, a bollarded wharf, an iron‑piled timber pier with fenders, a working derrick whose crate still swings, warehouses, a clock tower, a church on the heights, a terraced town climbing away in slate roofs, lit windows, chimney smoke, a shingle beach, and a breakwater ending in a beacon.
- **The light** — the lighthouse on its rock has a beam that sweeps (real geometry, additive), point lights that flicker on lamps and lanterns, and a full time‑of‑day rig: drag the Hour slider from civility dawn through high noon to night and the sun, sky shader, cloud band, fog, sea tint and every lamp in town follow.
- **The sea** — ~9,000 individually animated cubes writing straight into the instance matrix (no per‑frame `compose`), with crest‑height foam shading, a sheltered basin, foam breaking around the hull, the pier and the rocks, plus specular glint off the sun.
- **The mouse** — hand‑rolled orbit rig with damping: drag to orbit, wheel to zoom, right‑drag/shift‑drag to pan, double‑click to sail to that point, `1`–`6` for viewpoints, `R` to resume the slow turn of the watch.