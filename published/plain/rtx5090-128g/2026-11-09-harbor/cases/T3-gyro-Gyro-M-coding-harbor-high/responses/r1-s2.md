# Calling at Harbor — a voxel chart

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Calling at Harbor — voxel chart, sheet 03</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@400;500;700;800;900&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{
  --ink:#071820; --slate:#0e2a34; --deep:#0a2029;
  --paper:#efe4cf; --paper-dim:#bfae94;
  --amber:#f2a83e; --rust:#c05233; --foam:#a9dcc9; --sea:#4b9aa7;
  --line:rgba(239,228,207,.22);
}
*{box-sizing:border-box}
html,body{margin:0;height:100%;overflow:hidden;background:var(--ink)}
body{font-family:'IBM Plex Mono',ui-monospace,monospace;color:var(--paper);-webkit-font-smoothing:antialiased}
canvas{display:block}
#scene{position:fixed;inset:0}
.overlay{position:fixed;inset:0;pointer-events:none}
.vignette{position:fixed;inset:0;pointer-events:none;
  background:radial-gradient(120% 90% at 50% 45%,transparent 35%,rgba(3,14,20,.42) 78%,rgba(2,10,15,.72) 100%)}
.grain{position:fixed;inset:0;pointer-events:none;opacity:.06;mix-blend-mode:soft-light;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='180' height='180'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='3'/></filter><rect width='180' height='180' filter='url(%23n)'/></svg>")}
#ui{position:fixed;inset:0;pointer-events:none}
#ui > *{pointer-events:auto}

/* reveal */
.rise{opacity:0;transform:translateY(14px);animation:rise .9s cubic-bezier(.2,.7,.2,1) forwards}
@keyframes rise{to{opacity:1;transform:none}}

/* ---- plate / title ---- */
.plate{position:absolute;left:26px;top:24px;max-width:min(46vw,520px)}
.plate .rule{width:62px;height:3px;background:var(--amber);margin-bottom:14px}
.eyebrow{font-size:11px;letter-spacing:.28em;text-transform:uppercase;color:var(--paper-dim)}
h1{font-family:'Big Shoulders Display',sans-serif;font-weight:900;
  font-size:clamp(44px,6.4vw,92px);line-height:.82;margin:.18em 0 .1em;letter-spacing:-.01em;text-transform:uppercase}
h1 em{display:block;font-style:normal;color:var(--amber);font-weight:700;font-size:.52em;letter-spacing:.16em}
.plate .meta{font-size:11.5px;line-height:1.7;color:var(--paper-dim);border-left:1px solid var(--line);padding-left:10px;margin-top:12px}
.plate .meta b{color:var(--foam);font-weight:500}

/* ---- ledger ---- */
.ledger{position:absolute;left:26px;bottom:24px;width:330px;background:linear-gradient(180deg,rgba(14,42,52,.94),rgba(7,24,32,.94));
  border:1px solid var(--line);border-left:3px solid var(--amber);padding:14px 16px 12px;
  box-shadow:0 18px 40px rgba(0,0,0,.45)}
.ledger h2{font-family:'Big Shoulders Display',sans-serif;font-size:17px;letter-spacing:.18em;margin:0 0 10px;text-transform:uppercase;color:var(--amber)}
.ledger .row{display:flex;justify-content:space-between;gap:10px;font-size:11.5px;padding:4px 0;border-bottom:1px dotted rgba(239,228,207,.14)}
.ledger .row span{color:var(--paper-dim);letter-spacing:.1em;text-transform:uppercase;font-size:10px}
.ledger .row b{font-weight:500;text-align:right}
.ledger .status{margin-top:10px;font-size:11px;color:var(--foam);min-height:32px;line-height:1.55}
.stamp{position:absolute;right:12px;top:8px;font-family:'Big Shoulders Display',sans-serif;font-weight:800;font-size:13px;
  letter-spacing:.16em;color:var(--rust);border:2px solid var(--rust);padding:3px 7px;transform:rotate(-9deg) scale(.6);
  opacity:0;transition:opacity .5s ease,transform .5s cubic-bezier(.2,.8,.2,1)}
.stamp.on{opacity:.85;transform:rotate(-9deg) scale(1)}

/* ---- console ---- */
.console{position:absolute;right:24px;top:24px;width:228px;display:flex;flex-direction:column;gap:12px}
.box{background:rgba(9,28,36,.9);border:1px solid var(--line);padding:11px 12px}
.box > h3{font-family:'Big Shoulders Display',sans-serif;font-size:12px;letter-spacing:.24em;text-transform:uppercase;
  margin:0 0 9px;color:var(--paper-dim);display:flex;justify-content:space-between;align-items:center}
.box > h3 i{font-style:normal;color:var(--amber);font-size:11px;font-family:'IBM Plex Mono',monospace;letter-spacing:.06em}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{font-family:'IBM Plex Mono',monospace;font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;
  background:transparent;color:var(--paper);border:1px solid var(--line);padding:6px 9px;cursor:pointer;
  transition:transform .18s ease,background .2s ease,color .2s ease,border-color .2s ease}
.chip:hover{border-color:var(--amber);color:var(--amber);transform:translateY(-2px)}
.chip.on{background:var(--amber);color:#0b2028;border-color:var(--amber);font-weight:600}
.slider{width:100%;-webkit-appearance:none;appearance:none;height:3px;background:rgba(239,228,207,.25);outline:none;margin:8px 0 2px}
.slider::-webkit-slider-thumb{-webkit-appearance:none;width:14px;height:14px;background:var(--amber);border:2px solid #0b2028;cursor:grab}
.slider::-moz-range-thumb{width:14px;height:14px;background:var(--amber);border:2px solid #0b2028;cursor:grab}
.kn{font-size:10px;letter-spacing:.1em;color:var(--paper-dim);display:flex;justify-content:space-between}

/* ---- markers ---- */
.marker{position:absolute;left:0;top:0;transform:translate(-50%,-50%);pointer-events:auto;cursor:pointer}
.marker .dot{width:9px;height:9px;border-radius:50%;background:var(--amber);box-shadow:0 0 0 2px rgba(242,168,62,.28),0 0 14px rgba(242,168,62,.5)}
.marker .ring{position:absolute;left:-9px;top:-9px;width:26px;height:26px;border:1px solid rgba(242,168,62,.5);border-radius:50%;animation:pulse 2.8s ease-out infinite}
@keyframes pulse{0%{transform:scale(.4);opacity:.9}70%{transform:scale(1.3);opacity:0}100%{opacity:0}}
.marker .card{position:absolute;left:16px;top:-14px;white-space:nowrap;background:rgba(7,24,32,.94);border:1px solid var(--line);
  border-left:2px solid var(--amber);padding:7px 10px;opacity:0;transform:translate(-6px,0);transition:opacity .22s ease,transform .22s ease;pointer-events:none}
.marker:hover .card{opacity:1;transform:none}
.marker .card b{display:block;font-family:'Big Shoulders Display',sans-serif;font-size:14px;letter-spacing:.12em;text-transform:uppercase}
.marker .card span{font-size:10px;color:var(--paper-dim);letter-spacing:.08em}
.marker.dim{opacity:.35}

/* ---- footer ---- */
.foot{position:absolute;left:26px;bottom:0;height:0}
.hint{position:absolute;left:50%;bottom:20px;transform:translateX(-50%);font-size:10px;letter-spacing:.2em;
  text-transform:uppercase;color:rgba(239,228,207,.5);text-align:center}
.hint b{color:var(--amber);font-weight:500}
.compass{position:absolute;right:26px;bottom:22px;width:86px;text-align:center}
.compass svg{width:74px;height:74px;display:block;margin:0 auto}
.compass .lbl{font-size:10px;letter-spacing:.16em;color:var(--paper-dim);margin-top:2px}

/* ---- loader ---- */
#boot{position:fixed;inset:0;background:#071820;display:flex;align-items:center;justify-content:center;z-index:20;
  transition:opacity .8s ease;font-size:11px;letter-spacing:.3em;text-transform:uppercase;color:var(--paper-dim)}
#boot.gone{opacity:0;pointer-events:none}
@media (max-width:780px){.plate{max-width:70vw}.console{width:180px}.ledger{width:250px}.compass{display:none}}
</style>
</head>
<body>
<div id="scene"></div>
<div class="vignette"></div><div class="grain"></div>

<div id="ui">
  <header class="plate rise" style="animation-delay:.15s">
    <div class="rule"></div>
    <div class="eyebrow">Voxel chart · sheet 03 · griffin point</div>
    <h1>Calling<em>at the harbor</em></h1>
    <div class="meta">51°14′N&nbsp;&nbsp;004°02′W — <b>three masts, brigantine</b><br>
      Stone pier, bonded stores, fixed white light<br>
      <span id="tstate">approaching · canvas up</span></div>
  </header>

  <section class="ledger rise" style="animation-delay:.4s">
    <div class="stamp" id="stamp">cleared</div>
    <h2>Harbor master’s ledger</h2>
    <div class="row"><span>vessel</span><b>BRIGANTINE “MERIDIAN”</b></div>
    <div class="row"><span>registry</span><b>LIV · 214 GT · 1868</b></div>
    <div class="row"><span>master</span><b>E. HOLLOWAY</b></div>
    <div class="row"><span>cargo</span><b>48 CASES · 12 T COAL</b></div>
    <div class="row"><span>berth</span><b>gRIFFIN PIER, EAST</b></div>
    <div class="row"><span>draft</span><b id="draft">4.2 m aft</b></div>
    <div class="status" id="status">04:12 — off the light, requesting berthing.</div>
    <div class="row" style="border:0;padding-top:8px"><span>voxels rendered</span><b id="vc">—</b></div>
  </section>

  <aside class="console">
    <div class="box rise" style="animation-delay:.25s">
      <h3>Time of day <i id="tl">golden</i></h3>
      <div class="chips" id="timers"></div>
    </div>
    <div class="box rise" style="animation-delay:.35s">
      <h3>Movement</h3>
      <div class="chips" id="moves"></div>
      <h3 style="margin-top:11px">Rig</h3>
      <div class="chips" id="rigs"></div>
    </div>
    <div class="box rise" style="animation-delay:.45s">
      <h3>Wind <i id="kn">14 kn</i></h3>
      <input class="slider" id="wind" type="range" min="0" max="100" value="50">
      <div class="kn"><span>calm</span><span>fresh breeze</span></div>
    </div>
    <div class="box rise" style="animation-delay:.55s">
      <h3>Watch</h3>
      <div class="chips" id="toggles"></div>
      <div class="chips" style="margin-top:7px"><button class="chip" id="reset">reset view</button></div>
    </div>
  </aside>

  <div id="markers"></div>
  <div class="hint">drag to orbit · scroll to zoom · <b>click the amber marks</b> · keys 1–4 · space</div>
  <div class="compass rise" style="animation-delay:.6s">
    <svg viewBox="0 0 100 100">
      <circle cx="50" cy="50" r="34" fill="none" stroke="rgba(239,228,207,.25)"/>
      <circle cx="50" cy="50" r="26" fill="none" stroke="rgba(239,228,207,.12)"/>
      <text x="50" y="14" font-size="10" fill="#a9dcc9" text-anchor="middle" font-family="Big Shoulders Display">N</text>
      <text x="50" y="92" font-size="10" fill="rgba(239,228,207,.5)" text-anchor="middle" font-family="Big Shoulders Display">S</text>
      <text x="88" y="54" font-size="10" fill="rgba(239,228,207,.5)" text-anchor="middle" font-family="Big Shoulders Display">E</text>
      <text x="12" y="54" font-size="10" fill="rgba(239,228,207,.5)" text-anchor="middle" font-family="Big Shoulders Display">W</text>
      <g id="needle"><polygon points="50,20 54,52 50,58 46,52" fill="#f2a83e"/><polygon points="50,80 46,52 50,46 54,52" fill="rgba(239,228,207,.45)"/></g>
      <circle cx="50" cy="50" r="3" fill="#0e2a34" stroke="#f2a83e"/>
    </svg>
    <div class="lbl" id="brg">bearing 000°</div>
  </div>
</div>

<div id="boot">foring the sea · setting canvas</div>

<script type="importmap">
{"imports":{"three":"https://unpkg.com/three@0.160.0/build/three.module.js",
"three/addons/":"https://unpkg.com/three@0.160.0/examples/jsm/"}}
</script>
<script type="module">
import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';

/* ================= palette ================= */
const PAL={
  rust:0x8c4a30, hull:0x243642, hullDark:0x18272f, gun:0xe9dcc2, deck:0xb98552, deckDark:0x8a5f36,
  timber:0xa2703f, timberDark:0x6c4726, sail:0xe9dcc0, sailDark:0xc7b18b, rope:0xd0b079,
  iron:0x3b4550, brass:0xd8a441, stone:0x8a8676, stoneDark:0x606054, stoneLight:0xa9a392,
  brick:0x9c4a38, brickDark:0x7a3729, roof:0x46414e, foam:0xdcf1e6, white:0xf2ece0,
  red:0xb8432f, green:0x527f66, gold:0xe6a83f, cloud:0xe7d8c4, cloudDark:0xa6b3b2
};
const V=(x,y,z)=>new THREE.Vector3(x,y,z);
const rnd=(a,b)=>a+Math.random()*(b-a);
const clamp=(v,a,b)=>v<a?a:v>b?b:v;
const ease=t=>t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2;
function sh(col,amt=.05){const c=new THREE.Color(col);c.offsetHSL(rnd(-amt*.3,amt*.3),rnd(-amt*.2,amt*.2),rnd(-amt,amt));return c;}

/* ================= voxel builder ================= */
const _o=new THREE.Object3D(), _up=V(0,1,0);
class Vox{
  constructor(){this.m=[];this.c=[];}
  add(x,y,z,sx=1,sy=1,sz=1,col){
    _o.position.set(x,y,z);_o.scale.set(sx,sy,sz);_o.rotation.set(0,0,0);_o.updateMatrix();
    this.m.push(_o.matrix.clone());this.c.push(col instanceof THREE.Color?col:sh(col));
  }
  fill(x0,x1,y0,y1,z0,z1,col,step=1,amt=.05){
    for(let x=x0;x<=x1;x+=step)for(let y=y0;y<=y1;y+=step)for(let z=z0;z<=z1;z+=step)
      this.add(x,y,z,step,step,step,sh(col,amt));
  }
  beam(a,b,th,col,amt=.04){
    const d=new THREE.Vector3().subVectors(b,a),L=d.length(),mid=new THREE.Vector3().addVectors(a,b).multiplyScalar(.5);
    _o.position.copy(mid);_o.quaternion.setFromUnitVectors(_up,d.clone().normalize());
    _o.scale.set(th,Math.max(L,.05),th);_o.updateMatrix();
    this.m.push(_o.matrix.clone());this.c.push(sh(col,amt));
  }
  rope(a,b,th,col,sag=1.1,segs=7){
    for(let i=0;i<segs;i++){
      const s=i/segs,e=(i+1)/segs;
      const p=new THREE.Vector3().lerpVectors(a,b,s),q=new THREE.Vector3().lerpVectors(a,b,e);
      p.y-=Math.sin(Math.PI*s)*sag; q.y-=Math.sin(Math.PI*e)*sag;
      this.beam(p,q,th,col);
    }
  }
  tri(A,B,C,col,o={}){
    const bulge=o.bulge||0, mn=Math.min(A.x,B.x,C.x), mx=Math.max(A.x,B.x,C.x);
    const mny=Math.min(A.y,B.y,C.y), mxy=Math.max(A.y,B.y,C.y);
    const d=(B.y-C.y)*(A.x-C.x)+(C.x-B.x)*(A.y-C.y);
    for(let x=Math.ceil(mn);x<=Math.floor(mx);x++)for(let y=Math.ceil(mny);y<=Math.floor(mxy);y++){
      const a=((B.y-C.y)*(x-C.x)+(C.x-B.x)*(y-C.y))/d;
      const b=((C.y-A.y)*(x-C.x)+(A.x-C.x)*(y-C.y))/d;
      const c=1-a-b; if(a<-.02||b<-.02||c<-.02) continue;
      const z=(o.z||A.z)+bulge*Math.sin(Math.PI*(x-mn)/Math.max(mx-mn,1));
      this.add(x,y,z,1,1,o.thick||1,sh(col,o.amt||.05));
    }
  }
  mesh(mat,{cast=true,rec=true}={}){
    const g=new THREE.BoxGeometry(1,1,1);
    const im=new THREE.InstancedMesh(g,mat,Math.max(this.m.length,1));
    for(let i=0;i<this.m.length;i++){im.setMatrixAt(i,this.m[i]);im.setColorAt(i,this.c[i]);}
    if(this.m.length===0) im.visible=false;
    im.instanceMatrix.needsUpdate=true; if(im.instanceColor) im.instanceColor.needsUpdate=true;
    im.castShadow=cast; im.receiveShadow=rec; im.frustumCulled=false;
    im.userData.count=this.m.length;
    return im;
  }
}

/* ================= renderer / scene ================= */
const host=document.getElementById('scene');
const renderer=new THREE.WebGLRenderer({antialias:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.setSize(innerWidth,innerHeight);
renderer.shadowMap.enabled=true; renderer.shadowMap.type=THREE.PCFSoftShadowMap;
renderer.toneMapping=THREE.ACESFilmicToneMapping; renderer.toneMappingExposure=1.06;
renderer.outputColorSpace=THREE.SRGBColorSpace;
host.appendChild(renderer.domElement);

const scene=new THREE.Scene();
scene.fog=new THREE.FogExp2(0xb57f5e,.0048);
const camera=new THREE.PerspectiveCamera(42,innerWidth/innerHeight,.5,2600);
camera.position.set(-95,62,-112);
const controls=new OrbitControls(camera,renderer.domElement);
controls.enableDamping=true; controls.dampingFactor=.06;
controls.target.set(2,12,4); controls.minDistance=22; controls.maxDistance=320;
controls.maxPolarAngle=1.47; controls.autoRotate=false; controls.autoRotateSpeed=.32;

const sun=new THREE.DirectionalLight(0xffc489,1.6);
sun.position.set(-130,46,-120); sun.castShadow=true;
sun.shadow.mapSize.set(2048,2048); sun.shadow.bias=-0.0006; sun.shadow.normalBias=.6;
const sc=sun.shadow.camera; sc.left=-95; sc.right=95; sc.top=95; sc.bottom=-95; sc.near=1; sc.far=420;
scene.add(sun);
const hemi=new THREE.HemisphereLight(0x7fb3bd,0x4b5c55,.55); scene.add(hemi);
const fill=new THREE.DirectionalLight(0x8fc6d6,.35); fill.position.set(70,40,60); scene.add(fill);
const lampL1=new THREE.PointLight(0xffb862,2,90,1.8); lampL1.position.set(-16,15,10); scene.add(lampL1);
const lampL2=new THREE.PointLight(0xffb862,2,90,1.8); lampL2.position.set(24,15,10); scene.add(lampL2);
const lantern=new THREE.PointLight(0xffd79a,3.2,140,1.7); lantern.position.set(-46,38,32); scene.add(lantern);

/* ================= sky canvas ================= */
const skyC=document.createElement('canvas'); skyC.width=1024; skyC.height=512;
const sg=skyC.getContext('2d');
const skyTex=new THREE.CanvasTexture(skyC); skyTex.colorSpace=THREE.SRGBColorSpace;
const sky=new THREE.Mesh(new THREE.SphereGeometry(900,40,20),
  new THREE.MeshBasicMaterial({map:skyTex,side:THREE.BackSide,fog:false,toneMapped:false,depthWrite:false}));
scene.add(sky);
const starPts=[]; for(let i=0;i<260;i++) starPts.push({u:Math.random(),v:Math.random()*.46,m:rnd(.4,1)});
function paintSky(c){
  sg.clearRect(0,0,1024,512);
  const g=sg.createLinearGradient(0,0,0,512);
  g.addColorStop(0,c.zen); g.addColorStop(.34,mixHex(c.zen,c.hor,.45));
  g.addColorStop(.5,c.hor); g.addColorStop(.62,mixHex(c.hor,c.low,.65)); g.addColorStop(1,c.low);
  sg.fillStyle=g; sg.fillRect(0,0,1024,512);
  if(c.stars>0){
    sg.globalCompositeOperation='lighter';
    for(const s of starPts){ sg.fillStyle=`rgba(255,246,225,${(0.25+0.75*s.m)*c.stars})`;
      sg.fillRect(s.u*1024,s.v*512,1.4*s.m+1,1.4*s.m+1); }
  }
  const dir=new THREE.Vector3(...c.sunPos).normalize();
  const th=Math.atan2(dir.z,-dir.x); const u=((th/(Math.PI*2))%1+1)%1;
  const v=Math.acos(clamp(dir.y,-1,1))/Math.PI; const px=u*1024, py=(1-v)*512;
  sg.globalCompositeOperation='lighter';
  for(const off of [-1024,0,1024]){
    const rg=sg.createRadialGradient(px+off,py,0,px+off,py,240+c.haze*140);
    rg.addColorStop(0,`rgba(255,244,220,${.85})`); rg.addColorStop(.18,c.sun);
    rg.addColorStop(.5,`rgba(255,200,140,${.22*c.haze+.08})`); rg.addColorStop(1,'rgba(0,0,0,0)');
    sg.fillStyle=rg; sg.fillRect(px+off-420,py-420,840,840);
    sg.fillStyle=`rgba(255,252,240,${.9})`; sg.beginPath(); sg.arc(px+off,py,dir.y>0?13:9,0,Math.PI*2); sg.fill();
  }
  sg.globalCompositeOperation='source-over';
  skyTex.needsUpdate=true;
}
function mixHex(a,b,t){const ca=new THREE.Color(a),cb=new THREE.Color(b);ca.lerp(cb,t);return '#'+ca.getHexString();}

/* ================= presets ================= */
const PRESETS={
  golden:{key:'golden hour',zen:'#15384c',hor:'#f3a35c',low:'#6f4a3c',sun:'#ffd8a0',sunPos:[-130,46,-120],
    dirC:'#ffc489',dirI:1.6,hemiS:'#7fb3bd',hemiG:'#4b5c55',hemiI:.55,fog:'#b57f5e',fogD:.0048,
    sea:'#1e6675',deep:'#0b303b',lamps:.25,stars:0,beam:.12,exp:1.06,haze:.55,glit:.5},
  noon:{key:'high noon',zen:'#1b5d8a',hor:'#c3e4ea',low:'#8fb6bd',sun:'#fff8e6',sunPos:[-60,150,60],
    dirC:'#fff4dc',dirI:2.05,hemiS:'#bcdff0',hemiG:'#6f7a6e',hemiI:.8,fog:'#a8c9d2',fogD:.0033,
    sea:'#217a8c',deep:'#0d3b49',lamps:0,stars:0,beam:.06,exp:1.0,haze:.3,glit:.7},
  dusk:{key:'blue hour',zen:'#123048',hor:'#dd8b58',low:'#3a2d3a',sun:'#ffb27a',sunPos:[-150,14,-90],
    dirC:'#e08a56',dirI:.95,hemiS:'#4d7188',hemiG:'#2e3a3b',hemiI:.45,fog:'#4a5d70',fogD:.0072,
    sea:'#154a5c',deep:'#082330',lamps:1.1,stars:.4,beam:.35,exp:1.14,haze:.62,glit:.85},
  night:{key:'night watch',zen:'#05172a',hor:'#1c4257',low:'#081a22',sun:'#a8bfce',sunPos:[110,72,-70],
    dirC:'#7e96b4',dirI:.5,hemiS:'#264255',hemiG:'#152026',hemiI:.3,fog:'#163243',fogD:.0095,
    sea:'#0d3a4a',deep:'#061a25',lamps:1.7,stars:1,beam:.55,exp:1.22,haze:.45,glit:.95}
};
const cur=structuredClone(PRESETS.golden);
let target=PRESETS.golden;
function applySky(){
  sun.color.set(cur.dirC); sun.intensity=cur.dirI; sun.position.set(...cur.sunPos);
  hemi.color.set(cur.hemiS); hemi.groundColor.set(cur.hemiG); hemi.intensity=cur.hemiI;
  scene.fog.color.set(cur.fog); scene.fog.density=cur.fogD;
  renderer.toneMappingExposure=cur.exp;
  paintSky(cur);
  lampMats.forEach(m=>m.emissiveIntensity=.25+cur.lamps*2.1);
  lampL1.intensity=lampL2.intensity=cur.lamps*2.2; lantern.intensity=cur.lamps*3.4;
  beamMat.forEach(b=>b.material.opacity=cur.beam);
  starMat.opacity=cur.stars; stars.visible=cur.stars>.02;
  lampL1.visible=lampL2.visible=lantern.visible=cur.lamps>.1;
}
const lampMats=[]; const beamMat=[]; let starMat, stars;

/* ================= water ================= */
const WATER_Y=1.2, WSTEP=2.4, WR=62;
const wx=[],wz=[];
for(let x=-WR;x<=WR;x+=WSTEP)for(let z=-WR;z<=WR;z+=WSTEP){wx.push(x);wz.push(z);}
const WN=wx.length;
const water=new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1),
  new THREE.MeshLambertMaterial({color:0xffffff,roughness?0:0}),WN);
water.material=new THREE.MeshLambertMaterial({vertexColors:false});
water.receiveShadow=true; water.frustumCulled=false;
scene.add(water);
{const c=new THREE.Color(0x1e6675); for(let i=0;i<WN;i++) water.setColorAt(i,c);}
const _m=new THREE.Matrix4();

function wave(x,z,t,A){
  let h=Math.sin(x*.11+t*.9)*.42+Math.sin(x*.055-z*.09+t*1.25)*.36+Math.sin(z*.13+t*.75)*.28;
  h+=Math.sin(x*.31+z*.22+t*2.1)*.12;
  return h*A;
}
const seaC=new THREE.Color(),deepC=new THREE.Color(),foamC=new THREE.Color(0xdcf1e6),tmpC=new THREE.Color();
function updateWater(t){
  const A=.18+wind*1.05;
  seaC.set(cur.sea); deepC.set(cur.deep);
  const colArr=water.instanceColor.array;
  const dirx=Math.cos(shipGroup.rotation.y), dirz=-Math.sin(shipGroup.rotation.y);
  const sx=shipGroup.position.x-dirx*24, sz=shipGroup.position.z-dirz*24;
  const moving=approach<.985?1:0;
  for(let i=0;i<WN;i++){
    const x=wx[i],z=wz[i];
    const h=wave(x,z,t,A);
    // wake behind stern
    let wake=0;
    if(moving){
      const dx=x-sx,dz=z-sz; const along=dx*dirx+dz*dirz;
      if(along>0&&along<76){
        const perp=Math.abs(dx*dirz-dz*dirx);
        const band=3.5+along*.24;
        if(perp<band) wake=(1-along/76)*(1-perp/band)*.85;
      }
      const hd=Math.hypot(x-shipGroup.position.x,(z-shipGroup.position.z)/.24);
      if(hd<22&&hd>16) wake=Math.max(wake,(1-(hd-16)/6)*.5);
    }
    const top=WATER_Y+h+wake*.5;
    _m.set(WSTEP,0,0,0, 0,12,0,0, 0,0,WSTEP,0, x,top-6,z,1);
    water.setMatrixAt(i,_m);
    const f=clamp((h+A)/ (A*2.1),0,1);
    tmpC.copy(deepC).lerp(seaC,f);
    const gl=cur.glit*(.06+.16*Math.sin(x*.7+z*.55+t*3.4))*Math.max(.35,cur.dirI/2);
    tmpC.offsetHSL(0,0,gl);
    if(wake>0) tmpC.lerp(foamC,wake*.8);
    colArr[i*3]=tmpC.r; colArr[i*3+1]=tmpC.g; colArr[i*3+2]=tmpC.b;
  }
  water.instanceMatrix.needsUpdate=true; water.instanceColor.needsUpdate=true;
}

/* ================= the brigantine ================= */
function hullHalf(t){
  if(t<.05) return 4.3;
  if(t<.18) return 4.3+(t-.05)/.13*2.4;
  if(t<.58) return 6.7+Math.sin((t-.18)/.4*Math.PI)*.9;
  const b=(t-.58)/.42; return Math.max(.8,7.4*Math.pow(1-b,1.25));
}
function railY(t){ return 6+2.2*Math.pow(Math.max(0,(t-.62)/.38),1.3)+1.6*Math.pow(1-t,2.2); }
const deckY=t=>Math.round(railY(t))-1;
const LEN=48;
const xs0=-24;
const MASTS=[
  {x:-14,tiers:[{y:15,half:8,span:6},{y:21,half:6,span:5}],top:27},
  {x:-1,tiers:[{y:17,half:12,span:8},{y:25,half:9,span:7},{y:31,half:6,span:5}],top:35},
  {x:12,tiers:[{y:15,half:10,span:7},{y:22,half:8,span:6},{y:28,half:5,span:4}],top:31}
];
const shipGroup=new THREE.Group(); scene.add(shipGroup);

const hull=new Vox(), rig=new Vox(), deck=new Vox();
for(let x=xs0;x<=24;x++){
  const t=(x-xs0)/LEN, W=Math.max(1,Math.round(hullHalf(t)),), R=Math.round(railY(t));
  for(let z=-W;z<=W;z++){
    const az=Math.abs(z);
    for(let y=0;y<=R;y++){
      const side=az===W, bottom=y<=2;
      if(!side&&!bottom) continue;
      let c;
      if(y<=1) c=PAL.rust;
      else if(y===2) c=mixHex2(PAL.rust,PAL.hullDark,.55);
      else if(y===5&&side) c=PAL.gun;
      else c=(y%2===0)?PAL.hull:PAL.hullDark;
      hull.add(x,y,z,1,1,1,sh(c,.05));
    }
  }
  const dy=R-1;
  for(let z=-W+1;z<=W-1;z++) hull.add(x,dy,z,1,1,1,sh(((x+z)%3===0)?PAL.deckDark:PAL.deck,.05));
  hull.add(x,R+1,-W,1,1,1,sh(PAL.timber,.05)); hull.add(x,R+1,W,1,1,1,sh(PAL.timber,.05));
  for(let y=dy+1;y<=R;y++){ hull.add(x,y,-W+1,1,1,1,sh(PAL.deckDark,.05)); hull.add(x,y,W-1,1,1,1,sh(PAL.deckDark,.05)); }
}
function mixHex2(a,b,t){const ca=new THREE.Color(a),cb=new THREE.Color(b);return ca.lerp(cb,t);}
// deck furniture
const dAt=x=>deckY((x-xs0)/LEN);
for(const hx of [-16,-8,-2,5,11,17]) deck.fill(hx,hx+2,dAt(hx)+1,dAt(hx)+1,-3,3,PAL.deckDark,1,.04);
deck.fill(3,10,dAt(5)+2,dAt(5)+6,-4,4,PAL.timber,1,.06);         // cargo cases
deck.fill(3,10,dAt(5)+7,dAt(5)+7,-4,4,PAL.rope,1,.05);           // lashings
deck.fill(-20,-17,dAt(-19)+2,dAt(-19)+5,-4,-1,PAL.timberDark,1,.06);
deck.fill(-19,-18,dAt(-19)+2,dAt(-19)+4,2,3,PAL.brickDark,1,.06);
deck.fill(14,16,dAt(15)+2,dAt(15)+3,-2,2,PAL.rust,1,.05);        // coal hoist staging
deck.add(-4,dAt(-4)+2,0,2,2,2,PAL.timberDark);                    // capstan
deck.add(-4,dAt(-4)+4,0,1,1,1,PAL.brass);
deck.fill(-16,-14,dAt(-15)+2,dAt(-15)+4,4,6,PAL.brick,.5,.05);    // galley
deck.add(-15,dAt(-15)+5,5,1,3,1,PAL.iron);                        // chimney
for(let x=-18;x<=18;x+=4){ deck.add(x,dAt(x)+1,-5,1,2,1,PAL.timberDark); deck.add(x,dAt(x)+1,5,1,2,1,PAL.timberDark); }
// figurehead
deck.add(25,dAt(24)+2,0,2,2,2,PAL.gun); deck.add(26,dAt(24)+3,0,1,2,1,PAL.gold);
// masts, yards, crosstrees
for(const m of MASTS){
  const base=dAt(m.x);
  for(let y=base;y<=m.top;y++) rig.add(m.x,y,0,y<base+5?1.5:1,y<base+5?1.6:1,y<base+5?1.5:1,sh(PAL.timber,.05));
  rig.add(m.x,m.top+1,0,2,1,2,sh(PAL.timberDark,.04));
  for(const tr of m.tiers){
    rig.beam(V(m.x,tr.y,-tr.half),V(m.x,tr.y,tr.half),1.1,PAL.timberDark);
    rig.add(m.x,tr.y,-tr.half,1.6,1,1.6,sh(PAL.timberDark,.05));
    rig.add(m.x,tr.y,tr.half,1.6,1,1.6,sh(PAL.timberDark,.05));
    rig.beam(V(m.x,tr.y+2,-tr.half*.6),V(m.x,tr.y+2,tr.half*.6),.6,PAL.timberDark);
  }
  // shrouds + ratlines
  const foot=base+2, side=Math.round(hullHalf((m.x-xs0)/LEN));
  for(const sgn of [-1,1]){
    const foot2=V(m.x,foot,sgn*(side+.5)), head=V(m.x,m.top-2,0);
    const foot3=V(m.x-3,foot,sgn*(side+.5));
    rig.beam(head,foot2,.6,PAL.rope); rig.beam(head,foot3,.5,PAL.rope);
    for(let s=.14;s<.86;s+=.11){
      rig.beam(new THREE.Vector3().lerpVectors(head,foot2,s),new THREE.Vector3().lerpVectors(head,foot3,s),.4,PAL.rope,.02);
    }
  }
}
// stays, bowlines, bowsprit
rig.beam(V(12,29,0),V(24,7,0),.6,PAL.rope); rig.beam(V(12,29,0),V(28,12,0),.55,PAL.rope);
rig.beam(V(-1,33,0),V(12,29,0),.6,PAL.rope); rig.beam(V(-14,25,0),V(-1,33,0),.5,PAL.rope);
rig.beam(V(-1,33,0),V(-21,8,0),.6,PAL.rope); rig.beam(V(-14,25,0),V(-23,7,0),.5,PAL.rope);
rig.beam(V(23,railY(.99)+1,0),V(37,railY(.99)+6,0),1.2,PAL.timberDark);
rig.beam(V(30,15,0),V(34,12,0),.6,PAL.timberDark);
for(const m of MASTS) for(const tr of m.tiers){
  rig.beam(V(m.x,tr.y,tr.half),V(m.x+4,tr.y+4,0),.4,PAL.rope,.02);
  rig.beam(V(m.x,tr.y,-tr.half),V(m.x+4,tr.y+4,0),.4,PAL.rope,.02);
}
// gaff
rig.beam(V(-14,21,0),V(-28,16,0),.9,PAL.timberDark);
rig.beam(V(-14,7,0),V(-28,6,0),.7,PAL.timberDark);

const hullMesh=hull.mesh(shipMat(),{cast:true,rec:true});
function shipMat(){return new THREE.MeshStandardMaterial({color:0xffffff,roughness:.72,metalness:.02});}
shipGroup.add(hullMesh,deck.mesh(shipMat()),rig.mesh(shipMat()));
let voxTotal=hull.m.length+deck.m.length+rig.m.length;

/* ---- dynamic sails ---- */
const sails=[];
for(const m of MASTS) for(const tr of m.tiers){
  for(let z=-tr.half+1;z<=tr.half-1;z++) for(let r=0;r<=tr.span;r++){
    const band=(r===Math.round(tr.span*.55))?PAL.sailDark:(((r+tr.half)%6===0)?PAL.sailDark:PAL.sail);
    sails.push({k:'sq',mx:m.x,y:tr.y,z,r,u:z/tr.half,half:tr.half,col:sh(band,.05)});
  }
}
const jt=V(34,12,0);
for(const tri of [
  {A:jt,B:V(12,29,0),C:V(13,7,0)},
  {A:V(28,12,0),B:V(-1,33,0),C:V(11,7,0)},
  {A:V(-14,21,0),B:V(-28,16,0),C:V(-14,7,0),C2:V(-24,6,0)}
]){
  const parts=[tri];
  if(tri.C2){ parts.push({A:tri.B,B:tri.C2,C:tri.C}); }
  for(const p of parts){
    const mn=Math.min(p.A.x,p.B.x,p.C.x), mx=Math.max(p.A.x,p.B.x,p.C.x);
    const mny=Math.min(p.A.y,p.B.y,p.C.y), mxy=Math.max(p.A.y,p.B.y,p.C.y);
    const d=(p.B.y-p.C.y)*(p.A.x-p.C.x)+(p.C.x-p.B.x)*(p.A.y-p.C.y);
    for(let x=Math.ceil(mn);x<=Math.floor(mx);x++)for(let y=Math.ceil(mny);y<=Math.floor(mxy);y++){
      const a=((p.B.y-p.C.y)*(x-p.C.x)+(p.C.x-p.B.x)*(y-p.C.y))/d;
      const b=((p.C.y-p.A.y)*(x-p.C.x)+(p.A.x-p.C.x)*(y-p.C.y))/d;
      const c=1-a-b; if(a<-.02||b<-.02||c<-.02) continue;
      sails.push({k:'tri',x,y,z:0,tack:p.A,u:(x-mn)/Math.max(mx-mn,1),col:sh(PAL.sail,.05)});
    }
  }
}
const sailMat=new THREE.MeshStandardMaterial({color:0xffffff,roughness:.85,metalness:0,side:THREE.DoubleSide});
const sailMesh=new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1),sailMat,sails.length);
sailMesh.castShadow=true; sailMesh.frustumCulled=false; shipGroup.add(sailMesh);
voxTotal+=sails.length;
function updateSails(t){
  for(let i=0;i<sails.length;i++){
    const s=sails[i];
    if(s.k==='sq'){
      const o=sailOpen, fl=.5+.5*Math.sin(t*2.4+s.z*.6+s.mx*.3);
      const bulge=(wind*2.1*(1-s.u*s.u)+.15)*(o)*(1+fl*.4);
      const zz=s.z*(.3+.7*o), yy=s.y-.6-s.r*o;
      _m.set(.9,0,0,0, 0,.5+.55*o,0,0, 0,0,1,0, s.mx+bulge, yy, zz,1);
    }else{
      const f=.02+sailOpen*.98;
      const bulge=wind*2.2*sailOpen*Math.sin(Math.PI*s.u)*(.8+.2*Math.sin(t*3+s.x));
      _m.set(.3+.7*sailOpen,0,0,0, 0,.3+.7*sailOpen,0,0, 0,0,.9,0,
        s.tack.x+(s.x-s.tack.x)*f, s.tack.y+(s.y-s.tack.y)*f, s.tack.z+(s.z)+bulge,1);
    }
    sailMesh.setMatrixAt(i,_m); sailMesh.setColorAt(i,s.col);
  }
  sailMesh.instanceMatrix.needsUpdate=true; if(sailMesh.instanceColor) sailMesh.instanceColor.needsUpdate=true;
}

/* ---- flags ---- */
const flags=[];
for(let i=0;i<7;i++) flags.push({b:V(-27-i,15+((i%2)?1:0),0),col:i<3?sh(PAL.red,.04):sh(PAL.white,.04),k:'ens',i});
for(let i=0;i<5;i++) flags.push({b:V(-14+i,27,0),col:sh(PAL.gold,.05),k:'pen',i});
for(let i=0;i<5;i++) flags.push({b:V(-1+i,35,0),col:sh(PAL.foam,.05),k:'pen',i});
for(let i=0;i<5;i++) flags.push({b:V(12+i,31,0),col:sh(PAL.green,.05),k:'pen',i});
const flagMesh=new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1),
  new THREE.MeshStandardMaterial({color:0xffffff,roughness:.8,side:THREE.DoubleSide}),flags.length);
flagMesh.frustumCulled=false; shipGroup.add(flagMesh); voxTotal+=flags.length;
function updateFlags(t){
  flags.forEach((f,i)=>{
    const a=.5+wind*1.6;
    const z=(f.k==='ens'?Math.sin(f.i*.8-t*6)*a:Math.sin(f.i*.9-t*5)*a*.6);
    const droop=f.k==='ens'?0:Math.sin(f.i*.5+t*2)*.3-f.k==='pen'?0:0;
    _m.set(1,.9,1,0, 0,1,0,0, 0,0,1,0, f.b.x,f.b.y+droop,z,1);
    flagMesh.setMatrixAt(i,_m); flagMesh.setColorAt(i,f.col);
  });
  flagMesh.instanceMatrix.needsUpdate=true; if(flagMesh.instanceColor) flagMesh.instanceColor.needsUpdate=true;
}

/* ---- crew ---- */
const crewMat=new THREE.MeshStandardMaterial({color:0xffffff,roughness:.85});
function figure(c1,c2){
  const g=new THREE.Group();
  const body=new THREE.Mesh(new THREE.BoxGeometry(1.1,1.7,1),new THREE.MeshStandardMaterial({color:c1,roughness:.85}));
  body.position.y=1.7; const leg=new THREE.Mesh(new THREE.BoxGeometry(.9,.9,.8),new THREE.MeshStandardMaterial({color:c2,roughness:.9}));
  leg.position.y=.5; const head=new THREE.Mesh(new THREE.BoxGeometry(.8,.8,.8),new THREE.MeshStandardMaterial({color:0xd9b48a,roughness:.9}));
  head.position.y=2.9; body.castShadow=leg.castShadow=head.castShadow=true;
  g.add(leg,body,head); return g;
}
const shipCrew=[figure(PAL.red,PAL.hullDark),figure(PAL.sail,PAL.iron)];
shipCrew[0].position.set(6,dAt(6)+1,3); shipCrew[1].position.set(-8,dAt(-8)+1,-3.4);
shipCrew.forEach(c=>shipGroup.add(c));
const quayCrew=[];
for(let i=0;i<4;i++){
  const f=figure([PAL.rust,PAL.green,PAL.gun,PAL.timberDark][i],[PAL.iron,PAL.hullDark,PAL.rust,PAL.iron][i]);
  f.position.set(rnd(-26,30),9.5,rnd(14,24)); f.userData={x0:f.position.x,sp:rnd(.4,.9),ph:rnd(0,6)};
  scene.add(f); quayCrew.push(f);
}

/* ---- mooring lines + gangplank ---- */
const ropeMat=new THREE.MeshStandardMaterial({color:PAL.rope,roughness:.9});
const ropes=new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1),ropeMat,4*7);
ropes.frustumCulled=false; scene.add(ropes); voxTotal+=28;
const ropeDefs=[
  {ship:V(16,dAt(16)+2,7),pier:V(26,10,12)},
  {ship:V(10,dAt(10)+2,7),pier:V(16,10,12)},
  {ship:V(-16,dAt(-16)+2,7),pier:V(-24,10,12)},
  {ship:V(-20,dAt(-20)+2,7),pier:V(-32,10,12)}
];
function updateRopes(t){
  const vis=clamp((approach-.72)/.28,0,1);
  for(let r=0;r<4;r++){
    const a=shipGroup.localToWorld(ropeDefs[r].ship.clone()), b=ropeDefs[r].pier.clone();
    for(let i=0;i<7;i++){
      const s=i/7,e=(i+1)/7;
      const p=new THREE.Vector3().lerpVectors(a,b,s), q=new THREE.Vector3().lerpVectors(a,b,e);
      const sag=(1.5+wind*.6)*Math.sin(Math.PI*s)+Math.sin(t*2+r)*.12;
      const sag2=(1.5+wind*.6)*Math.sin(Math.PI*e)+Math.sin(t*2+r+.5)*.12;
      p.y-=sag; q.y-=sag2;
      const d=new THREE.Vector3().subVectors(q,p),L=d.length();
      _o.position.copy(p).add(d.clone().multiplyScalar(.5));
      _o.quaternion.setFromUnitVectors(_up,d.clone().normalize());
      _o.scale.set(.55*vis,Math.max(L*.001,0),.55*vis); _o.updateMatrix();
      ropes.setMatrixAt(r*7+i,_o.matrix); ropes.setColorAt(r*7+i,tmpC.set(PAL.rope));
    }
  }
  ropes.instanceMatrix.needsUpdate=true; if(ropes.instanceColor) ropes.instanceColor.needsUpdate=true;
}
const plank=new THREE.Mesh(new THREE.BoxGeometry(1,1,1),new THREE.MeshStandardMaterial({color:PAL.timber,roughness:.8}));
plank.castShadow=true; scene.add(plank);

/* ================= harbor ================= */
const H=new Vox();
// pier mass (chunky LOD)
H.fill(-36,36,2,7,13,30,PAL.stoneDark,4,.05);
H.fill(-36,36,6,8,13,30,PAL.stone,4,.05);
// face courses
for(let x=-36;x<=36;x+=2) for(let y=3;y<=8;y+=2) H.add(x,y,12,2,2,1.6,sh((y%4===0)?PAL.stoneLight:PAL.stone,.07));
// paving
for(let x=-34;x<=34;x+=2) for(let z=13;z<=30;z+=2.6){
  const wet=(Math.abs(x+18)<4&&Math.abs(z-24)<3)||(Math.abs(x-8)<3&&Math.abs(z-19)<2);
  H.add(x,9,z,2,1,2.6,sh(wet?0x2c4c56:((x+z)%4===0?PAL.stoneLight:PAL.stone),.08));
}
// timber fenders + steps
for(let x=-36;x<=36;x+=3) H.add(x,8,11.4,2.2,2.4,1.4,sh(PAL.timberDark,.06));
for(let i=0;i<4;i++) H.add(20+i*1.6,8-i*2,11-i*1.4,2,2,2,sh(PAL.stoneLight,.05));
// bollards & rings
for(let x=-32;x<=32;x+=8){
  H.add(x,11,12,1.6,3,1.6,sh(PAL.iron,.04)); H.add(x,13,12,2.4,.9,2.4,sh(PAL.iron,.04));
  H.add(x+4,10,12,1,.7,1.4,sh(PAL.brass,.05));
  H.rope(V(x,11.5,12),V(x+2.2,9.6,12.6),.45,PAL.rope,.4,4);
  H.fill(x-2,x+2,9.4,9.4,14,17,PAL.rope,1,.06);
}
// warehouse
const W=new Vox();
W.fill(-30,-8,9,18,17,27,PAL.brick,3,.05);
for(let y=9;y<=18;y+=2) for(let x=-30;x<=-8;x+=3) W.add(x,y,16.6,3,2,1,sh(PAL.brickDark,.05));
for(let x=-29;x<=-9;x+=2){ W.add(x,19.5,22,2,2,12,sh(PAL.roof,.05)); }
for(let y=19;y<=22;y+=2) W.fill(-31,-7,y,y,17,27,PAL.roof,3,.05);
W.fill(-19,-13,9,15,16,17.4,PAL.timberDark,1,.05); // loading door
for(const lx of [-27,-23,-15,-11]) for(const ly of [12,16]) W.add(lx,ly,16.6,2,2.6,1,sh(0x182b31,.03));
W.fill(-30,-8,18.6,19,16,17.4,PAL.stoneLight,3,.04);
// anchor sign
const S=new Vox();
S.beam(V(-19,19,15),V(-19,22,15),.8,PAL.iron);
S.fill(-23,-15,21,24,15,15,PAL.timberDark,1,.05);
S.fill(-22,-20,22,23,14.6,14.6,PAL.gold,1,.05);
S.add(-21,21,14.6,3,1,1,PAL.gold); S.add(-21,24,14.6,1,2,1,PAL.gold);
scene.add(W.mesh(new THREE.MeshStandardMaterial({color:0xffffff,roughness:.85})),S.mesh(new THREE.MeshStandardMaterial({color:0xffffff,roughness:.8})));
const winMat=new THREE.MeshStandardMaterial({color:0x1a2a2e,emissive:new THREE.Color(0xffb45a),emissiveIntensity:.25,roughness:.5});
lampMats.push(winMat);
const win=new Vox();
for(const lx of [-27,-23,-15,-11]) for(const ly of [12,16]) win.add(lx,ly,16.4,1.6,2.2,.6,sh(0xffc672,.05));
scene.add(win.mesh(winMat,{cast:false}));
voxTotal+=W.m.length+S.m.length+win.m.length;

// customs house + clock tower
const T=new Vox();
T.fill(14,26,9,17,18,28,PAL.stoneLight,3,.05);
for(let x=14;x<=26;x+=2) T.add(x,17.6,23,2,2,11,sh(PAL.brickDark,.05));
for(let y=18;y<=21;y+=2) T.fill(13,27,y,y,17,29,PAL.brickDark,3,.05);
T.fill(18,24,9,26,20,26,PAL.stone,3,.05);
for(let y=9;y<=27;y+=3) T.add(21,y,19.4,3,3,1,sh((y%9===0)?PAL.red:PAL.white,.05));
T.fill(17,25,27,28,19,27,PAL.stoneLight,2,.04);
T.fill(19,23,28,32,21,25,PAL.stoneDark,2,.05);
for(let y=12;y<=24;y+=4) for(const zx of [20.4]) T.add(21,y,zx,2,2.4,.6,sh(0x182b31,.03));
scene.add(T.mesh(new THREE.MeshStandardMaterial({color:0xffffff,roughness:.85})));
voxTotal+=T.m.length;
const tWin=new Vox();
for(let y=12;y<=24;y+=4) tWin.add(21,y,20.2,1.8,2.2,.5,sh(0xffc672,.05));
scene.add(tWin.mesh(winMat,{cast:false})); voxTotal+=tWin.m.length;
const clock=new THREE.Group(); clock.position.set(21,30.2,20.2); scene.add(clock);
const face=new THREE.Mesh(new THREE.BoxGeometry(4.4,4.4,.7),new THREE.MeshStandardMaterial({color:PAL.gun,roughness:.6}));
face.castShadow=true; clock.add(face); voxTotal+=1;
const handMat=new THREE.MeshStandardMaterial({color:PAL.hullDark,roughness:.6});
const h1=new THREE.Mesh(new THREE.BoxGeometry(.5,2.6,.4),handMat), h2=new THREE.Mesh(new THREE.BoxGeometry(.4,1.6,.4),handMat);
h1.position.set(0,1.3,.5); h2.position.set(0,.8,.6); clock.add(h1,h2); voxTotal+=2;

// lighthouse + breakwater
const L=new Vox();
for(let y=4;y<=30;y++){
  const r=4.4-Math.pow(y/30,1.5)*2.1;
  for(let a=0;a<Math.PI*2;a+=Math.PI/(r*1.6)){
    const x=-46+Math.cos(a)*r, z=32+Math.sin(a)*r;
    const band=Math.floor((y-4)/4)%2===0;
    L.add(x,y,z,1.3,1,1.3,sh(band?PAL.white:PAL.red,.06));
  }
}
L.fill(-51,-41,2,5,27,37,PAL.stoneDark,3,.06);
L.fill(-50,-42,31,31,28,36,PAL.iron,2,.04);
L.fill(-49,-43,32,36,29,35,PAL.glass,2,.03);
L.fill(-50,-42,37,38,28,36,PAL.iron,2,.05);
L.add(-46,39,32,2,2,2,PAL.brass);
scene.add(L.mesh(new THREE.MeshStandardMaterial({color:0xffffff,roughness:.8})));
voxTotal+=L.m.length;
const lanternGlass=new Vox();
lanternGlass.fill(-49,-43,32,36,29,35,PAL.lampOn||0xffd79a,2,.03);
const glassMat=new THREE.MeshStandardMaterial({color:0x2b2415,emissive:new THREE.Color(0xffd28f),emissiveIntensity:1,roughness:.4});
lampMats.push(glassMat);
scene.add(lanternGlass.mesh(glassMat,{cast:false})); voxTotal+=lanternGlass.m.length;

const beamPivot=new THREE.Group(); beamPivot.position.set(-46,34,32); scene.add(beamPivot);
for(const s of [1,-1]){
  const cg=new THREE.ConeGeometry(13,150,6,1,true);
  cg.translate(0,-75,0); cg.rotateX(Math.PI/2);
  const bm=new THREE.MeshBasicMaterial({color:0xffd9a0,transparent:true,opacity:.12,side:THREE.DoubleSide,
    blending:THREE.AdditiveBlending,depthWrite:false,fog:false,toneMapped:false});
  const c=new THREE.Mesh(cg,bm); c.rotation.y=s>0?0:Math.PI; beamPivot.add(c); beamMat.push(bm);
}
const B=new Vox();
B.fill(-58,-38,1,7,28,36,PAL.stoneDark,3,.07);
for(let x=-58;x<=-38;x+=2) for(let y=2;y<=7;y+=2) B.add(x,y,27,2,2,1.5,sh(PAL.stone,.08));
scene.add(B.mesh(new THREE.MeshStandardMaterial({color:0xffffff,roughness:.9}))); voxTotal+=B.m.length;

// derricks
const D=new Vox();
for(const cx of [8,22]){
  D.fill(cx-1,cx+2,9,16,cx===8?12:13,cx===8?14:15,PAL.timberDark,1,.05);
  D.beam(V(cx,16,cx===8?13:14),V(cx+12,22,cx===8?9:10),1.1,PAL.timber);
  D.beam(V(cx,16,cx===8?13:14),V(cx-5,20,cx===8?17:18),1,PAL.timber);
  D.fill(cx-2,cx+3,9.2,9.2,cx===8?15:16,cx===8?18:19,PAL.rust,1,.05); // coal pile
  D.fill(cx-2,cx+2,9,9,cx===8?11:12,cx===8?12:13,PAL.stoneLight,1,.04);
}
scene.add(D.mesh(new THREE.MeshStandardMaterial({color:0xffffff,roughness:.85}))); voxTotal+=D.m.length;
const hook=new THREE.Group(); scene.add(hook);
const chain=new THREE.Mesh(new THREE.BoxGeometry(.4,1,.4),new THREE.MeshStandardMaterial({color:PAL.iron,roughness:.6}));
const crate=new THREE.Mesh(new THREE.BoxGeometry(3,2.6,3),new THREE.MeshStandardMaterial({color:PAL.timber,roughness:.8}));
crate.castShadow=true; crate.position.y=-2; hook.add(chain,crate); voxTotal+=2;
// barrels, crates, nets, lamps
const P=new Vox();
for(let i=0;i<14;i++){
  const x=rnd(-34,34),z=rnd(15,29);
  P.fill(x,x+1,9.2,12,z,z+1,PAL.timberDark,1,.07);
  P.fill(x,x+1,10.4,10.9,z,z+1,PAL.brass,1,.04);
}
for(let i=0;i<10;i++){
  const x=rnd(-32,34),z=rnd(16,28);
  P.fill(x,x+2,9.2,9.2+rnd(2,4),z,z+2,(Math.random()>.5)?PAL.timber:PAL.brickDark,1,.08);
}
for(let i=0;i<5;i++){ const x=rnd(-24,28),z=rnd(15,28); P.fill(x,x+3,9.3,9.3,z,z,PAL.rope,1,.06); }
for(let x=-30;x<=30;x+=12){
  P.add(x,12,24,1,7,1,PAL.iron); P.add(x,16,24,2,1,2,PAL.iron);
  P.add(x,17,24,2.4,2.4,2.4,sh(0xffd28f,.02));
}
P.fill(-2,-2,9,11,26,29,PAL.green,1,.06); // nets rack
scene.add(P.mesh(new THREE.MeshStandardMaterial({color:0xffffff,roughness:.85})));
const lampGlow=new Vox();
for(let x=-30;x<=30;x+=12) lampGlow.add(x,17,24,2,2,2,sh(0xffd28f,.02));
scene.add(lampGlow.mesh(winMat,{cast:false})); voxTotal+=P.m.length+lampGlow.m.length;
// signal mast
const SM=new Vox();
SM.add(32,14,18,1,10,1,PAL.timberDark);
for(let i=0;i<3;i++) SM.add(32,12+i*2.2,18,2,1.4,2,sh([PAL.red,PAL.gold,PAL.foam][i],.04));
SM.beam(V(32,23,18),V(38,22,18),.4,PAL.rope);
scene.add(SM.mesh(new THREE.MeshStandardMaterial({color:0xffffff,roughness:.85}))); voxTotal+=SM.m.length;
scene.add(H.mesh(new THREE.MeshStandardMaterial({color:0xffffff,roughness:.9}))); voxTotal+=H.m.length;

/* ================= atmosphere ================= */
const cloudMat=new THREE.MeshStandardMaterial({color:0xffffff,roughness:.95,metalness:0});
const clouds=[];
for(let i=0;i<7;i++){
  const cv=new Vox(); const cx=rnd(-120,120),cy=rnd(46,78),cz=rnd(-120,60),n=Math.floor(rnd(6,14));
  for(let k=0;k<n;k++) cv.add(cx+rnd(-14,14),cy+rnd(-3,3),cz+rnd(-8,8),rnd(6,16),rnd(3,7),rnd(6,14),
    sh(k%3===0?PAL.cloudDark:PAL.cloud,.05));
  const m=cv.mesh(cloudMat,{cast:false,rec:false}); m.userData={sp:rnd(.6,1.7)};
  scene.add(m); clouds.push(m); voxTotal+=cv.m.length;
}
starMat=new THREE.MeshBasicMaterial({color:0xfff4dc,transparent:true,opacity:0,fog:false,toneMapped:false});
const st=new Vox();
for(let i=0;i<700;i++){
  const dir=new THREE.Vector3(rnd(-1,1),rnd(.06,1),rnd(-1,1)).normalize().multiplyScalar(780);
  st.add(dir.x,dir.y,dir.z,rnd(1.4,3.4),rnd(1.4,3.4),rnd(1.4,3.4),sh(0xfff6e2,.06));
}
stars=st.mesh(starMat,{cast:false,rec:false}); stars.visible=false; scene.add(stars); voxTotal+=st.m.length;

const foamMat=new THREE.MeshBasicMaterial({color:0xe8f6ee,toneMapped:false});
const foamN=220, foam=new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1),foamMat,foamN);
foam.frustumCulled=false; scene.add(foam); voxTotal+=foamN;
const foamData=[]; for(let i=0;i<foamN;i++){
  const b=Math.random()<.5?V(shipGroup.position.x,0,shipGroup.position.z):V(rnd(-58,-40),0,rnd(25,38));
  foamData.push({b,a:rnd(0,Math.PI*2),r:rnd(2,7),sp:rnd(.6,1.6),ph:rnd(0,9)});
}
function updateFoam(t){
  for(let i=0;i<foamN;i++){
    const f=foamData[i];
    const base=f.b.z>20?V(rnd(-58,-40),0,rnd(27,37)):V(shipGroup.position.x,0,shipGroup.position.z);
    const x=base.x+Math.cos(f.a)*f.r*(1+t*.02%1), z=base.z+Math.sin(f.a)*f.r;
    const s=(.6+wind*1.4)*(.5+.5*Math.abs(Math.sin(t*f.sp+f.ph)));
    _m.set(1.6*s,1.2*s,1.6*s,0, 0,1,0,0, 0,0,1,0, x,WATER_Y+1.1+Math.sin(t*f.sp+f.ph)*.4,z,1);
    foam.setMatrixAt(i,_m);
  }
  foam.instanceMatrix.needsUpdate=true;
}
const smokeMat=new THREE.MeshLambertMaterial({color:0xd8d2c6});
const smokeN=52, smoke=new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1),smokeMat,smokeN);
smoke.frustumCulled=false; scene.add(smoke); voxTotal+=smokeN;
const smData=[]; for(let i=0;i<smokeN;i++) smData.push({src:i%2,l:rnd(0,1),a:rnd(0,6)});
function updateSmoke(t,dt){
  for(let i=0;i<smokeN;i++){
    const s=smData[i]; s.l+=dt*(.13+wind*.16); if(s.l>1){s.l=0;s.a=rnd(0,6);}
    const src=s.src===0?shipGroup.localToWorld(V(-15,dAt(-15)+7,5)):V(-26,23,22);
    const rise=s.l*26, dr=s.l*s.l*(6+wind*22);
    const sc=(1.4+s.l*5.2)*(1-s.l*.45);
    _m.set(sc,sc,sc,0, 0,1,0,0, 0,0,sc,0, src.x+Math.sin(s.a)*s.l*3+dr, src.y+rise, src.z+Math.cos(s.a)*s.l*3+s.l*2,1);
    smoke.setMatrixAt(i,_m);
  }
  smoke.instanceMatrix.needsUpdate=true;
}
// gulls
const gullMat=new THREE.MeshStandardMaterial({color:0xf4efe3,roughness:.85});
const gullDark=new THREE.MeshStandardMaterial({color:0x59687a,roughness:.9});
const gulls=[];
for(let i=0;i<7;i++){
  const g=new THREE.Group();
  const b=new THREE.Mesh(new THREE.BoxGeometry(.7,.7,2.2),gullMat); b.castShadow=true; g.add(b);
  const wL=new THREE.Mesh(new THREE.BoxGeometry(3,.28,.9),gullMat); wL.position.set(-1.8,0,0); g.add(wL);
  const wR=new THREE.Mesh(new THREE.BoxGeometry(3,.28,.9),gullMat); wR.position.set(1.8,0,0); g.add(wR);
  const t=new THREE.Mesh(new THREE.BoxGeometry(.4,.3,.6),gullDark); t.position.set(0,.1,1.3); g.add(t);
  g.userData={a:rnd(0,6.2),r:rnd(30,54),h:rnd(22,40),sp:rnd(.16,.34),fl:rnd(2.6,4.4),cx:rnd(-20,26),cz:rnd(-34,16)};
  scene.add(g); gulls.push(g); voxTotal+=4;
}

/* ================= state ================= */
let wind=.5, sailOpen=1, sailTarget=1, approach=0, approachTarget=0;
let lampsOverride=-1, plankT=0;
const HOME={p:V(-58,33,-64),t:V(2,12,4)};
let tween=null;
function focusTo(tp,tt,dur=1.2){
  const dir=new THREE.Vector3().subVectors(camera.position,tp).normalize();
  tween={fp:camera.position.clone(),ft:controls.target.clone(),tp:tp.clone(),tt:tt.clone(),t:0,d:dur};
}
controls.addEventListener('start',()=>{tween=null;});
const pathA=V(-56,0,-34), pathB=V(-26,0,-6), pathC=V(2,0,4);
function bezier(u){
  const s=ease(u);
  const p=new THREE.Vector3();
  p.addScaledVector(pathA,(1-s)*(1-s)); p.addScaledVector(pathB,2*(1-s)*s); p.addScaledVector(pathC,s*s);
  return p;
}
let statusLines={
  approach:["04:12 — off the light, requesting berthing.","Wind on the quarter; canvas up, holding 6 kn.","Pilot aboard. Standing in from the west.","Signals flagged: ‘by the lead, enter.’"],
  moored:["04:41 — made fast, starboard quarter.","Cargo working: cotton cases, derrick No. 1.","Gangway down. Customs aboard.","Watch set: anchor watch, light tender."]
};
let statusTimer=0;

/* ================= UI ================= */
const markersEl=document.getElementById('markers');
const MARKS=[
  {n:'brigantine “meridian”',s:'214 gt · cotton & coal · master E. Holloway',d:52,f:()=>shipGroup.localToWorld(V(0,16,0))},
  {n:'griffin point light',s:'fixed white · 12 s · 34 m above MH',d:46,f:()=>V(-46,36,32)},
  {n:'pier derrick No.1',s:'cargo working · 2 tons per lift',d:36,f:()=>V(14,20,12)},
  {n:'harbor master’s office',s:'customs house · clock 04:41',d:42,f:()=>V(21,26,22)},
  {n:'bonded store',s:'48 cases · one hatch working',d:44,f:()=>V(-19,17,22)},
  {n:'sea wall & spray',s:'breakwater · heavy swell on the head',d:50,f:()=>V(-50,9,31)}
];
const marks=MARKS.map(m=>{
  const el=document.createElement('div'); el.className='marker rise';
  el.innerHTML='<div class="ring"></div><div class="dot"></div><div class="card"><b>'+m.n+'</b><span>'+m.s+'</span></div>';
  el.addEventListener('click',()=>focusTo(m.f(),V(m.d*.55,m.d*.42,m.d*.75).add(m.f())));
  markersEl.appendChild(el); return el;
});
function mkChips(el,items,on,group){
  items.forEach((it,i)=>{
    const b=document.createElement('button'); b.className='chip'+(it.on?' on':''); b.textContent=it.t;
    b.addEventListener('click',()=>{
      if(group) [...el.children].forEach(c=>c.classList.remove('on'));
      b.classList.toggle('on',group?true:!b.classList.contains('on'));
      on(it,b);
    });
    el.appendChild(b);
  });
}
const timers=document.getElementById('timers');
mkChips(timers,Object.entries(PRESETS).map(([k,p],i)=>({t:p.key,on:k==='golden',k})),it=>{target=PRESETS[it.k];document.getElementById('tl').textContent=it.k;},true);
const moves=document.getElementById('moves');
mkChips(moves,[{t:'approach',on:true,k:0},{t:'moor',on:false,k:1}],it=>{
  approachTarget=it.k; if(it.k){sailTarget=0;rigChips.children[1].classList.add('on');rigChips.children[0].classList.remove('on');}
  else{sailTarget=1;rigChips.children[0].classList.add('on');rigChips.children[1].classList.remove('on');}
},true);
const rigs=document.getElementById('rigs'); const rigChips=rigs;
mkChips(rigs,[{t:'canvas up',on:true,k:1},{t:'furled',on:false,k:0}],it=>{sailTarget=it.k;},true);
const toggles=document.getElementById('toggles');
mkChips(toggles,[{t:'lamps',on:false},{t:'auto-orbit',on:false}],it=>{
  if(it.t==='lamps'){ lampsOverride=it.t==='lamps'&&it.on?1.9:((lampsOverride===1.9)?-1:lampsOverride); target=PRESETS[document.getElementById('tl').textContent]; }
  else controls.autoRotate=it.on;
},false);
document.getElementById('reset').addEventListener('click',()=>focusTo(HOME.t,HOME.p.clone().sub(HOME.t).add(HOME.t)));
const windEl=document.getElementById('wind');
windEl.addEventListener('input',()=>{wind=windEl.value/100;document.getElementById('kn').textContent=Math.round(wind*28)+' kn';});
addEventListener('keydown',e=>{
  const k=Object.keys(PRESETS)[parseInt(e.key)-1]; if(k){target=PRESETS[k];document.getElementById('tl').textContent=k;
    [...timers.children].forEach((c,i)=>c.classList.toggle('on',Object.keys(PRESETS)[i]===k));}
  if(e.code==='Space'){e.preventDefault();sailTarget=sailTarget>.5?0:1;approachTarget=approachTarget>.5?0:1;
    [...rigChips.children].forEach((c,i)=>c.classList.toggle('on',(i===0)===(sailTarget>.5)));
    [...moves.children].forEach((c,i)=>c.classList.toggle('on',(i===1)===(approachTarget>.5)));}
});

/* ================= loop ================= */
document.getElementById('vc').textContent=voxTotal.toLocaleString();
const needle=document.getElementById('needle'), brg=document.getElementById('brg'),
      statusEl=document.getElementById('status'), tstate=document.getElementById('tstate'), stamp=document.getElementById('stamp');
let lastT=performance.now()/1000;
function frame(){
  const now=performance.now()/1000; const dt=Math.min(.05,now-lastT); lastT=now;
  const t=now;
  // preset tween
  const k=1-Math.pow(.03,dt);
  for(const key of Object.keys(target)){
    if(typeof target[key]==='number') cur[key]+=(target[key]-cur[key])*k*1.4;
    else if(Array.isArray(target[key])) cur[key]=target[key];
    else cur[key]=mixHex(cur[key],target[key],k*1.4);
  }
  applySky();
  // ship motion
  approach+=(approachTarget-approach)*Math.min(1,dt*.9);
  sailOpen+=(sailTarget-sailOpen)*Math.min(1,dt*1.6);
  const bp=bezier(approach);
  const tan=new THREE.Vector3().subVectors(bezier(Math.min(1,approach+.02)),bezier(Math.max(0,approach-.02))).normalize();
  let hd=Math.atan2(-tan.z,tan.x);
  hd=hd*(1-clamp((approach-.78)/.22,0,1));
  shipGroup.rotation.y=hd;
  const wh=wave(bp.x,bp.z,t,.18+wind*1.05);
  shipGroup.position.set(bp.x,WATER_Y+wh-3+ (approach>.9?0:0),bp.z);
  shipGroup.rotation.z=Math.sin(t*.75)*(.02+wind*.05);
  shipGroup.rotation.x=Math.sin(t*.5+1.3)*(.012+wind*.03);
  updateSails(t); updateFlags(t); updateRopes(t);
  plankT+=((approach>.92?1:0)-plankT)*Math.min(1,dt*1.4);
  {
    const a=shipGroup.localToWorld(V(2,dAt(2)+1,7.4)), b=new THREE.Vector3().lerpVectors(
      shipGroup.localToWorld(V(2,dAt(2)+11,7.4)),V(11,9.4,12),plankT);
    const d=new THREE.Vector3().subVectors(b,a);
    plank.position.copy(a).addScaledVector(d,.5);
    plank.quaternion.setFromUnitVectors(_up,d.clone().normalize());
    plank.scale.set(2.6,Math.max(d.length(),.4),3.4);
    plank.visible=plankT>.05;
  }
  // crane / hook
  const work=clamp((approach-.8)/.2,0,1);
  const sw=Math.sin(t*.5);
  const tip=V(8+12*(.4+.6*(sw*.5+.5)),22-(sw*.4),12-3*(sw*.5+.5));
  hook.position.copy(new THREE.Vector3().lerpVectors(V(8+6,22,10),V(12,20,5),work));
  hook.rotation.z=Math.sin(t*1.3)*.06*(1+wind);
  chain.scale.set(1,Math.max(1,20-((approach>.9)?10:0)),1);
  crate.position.y=-chain.scale.y-1.4; crate.rotation.y=t*.2;
  // clock
  const mins=(t*24)%720; h1.rotation.z=-mins/720*Math.PI*2; h2.rotation.z=-(mins%60)/60*Math.PI*2;
  // water & atmosphere
  updateWater(t); updateFoam(t); updateSmoke(t,dt);
  beamPivot.rotation.y+=dt*.55;
  for(const c of clouds){ c.position.x+=dt*c.userData.sp*(.4+wind); if(c.position.x>150) c.position.x=-150; }
  gulls.forEach((g,i)=>{
    const u=g.userData; u.a+=dt*u.sp*(.5+wind*1.2);
    g.position.set(u.cx+Math.cos(u.a)*u.r, u.h+Math.sin(u.a*2.3)*3.5, u.cz+Math.sin(u.a)*u.r*.7);
    g.rotation.y=-u.a+Math.PI/2; g.rotation.z=Math.sin(u.a*3)*.2;
    const fl=Math.sin(t*u.fl+i)*.7; g.children[1].rotation.z=fl; g.children[2].rotation.z=-fl;
  });
  quayCrew.forEach(f=>{
    const u=f.userData; const x=u.x0+Math.sin(t*u.sp+u.ph)*9;
    f.position.x=x; f.position.y=9.5+Math.abs(Math.sin(t*4+u.ph))*.28; f.rotation.y=Math.cos(t*u.sp+u.ph)>0?Math.PI/2:-Math.PI/2;
  });
  shipCrew.forEach((c,i)=>{ c.position.y=dAt(c.position.x)+1+Math.abs(Math.sin(t*3+i))*0.2; c.rotation.y=Math.sin(t*.6+i)*.9; });
  // camera tween
  if(tween){
    tween.t=Math.min(1,tween.t+dt/tween.d); const e=ease(tween.t);
    camera.position.lerpVectors(tween.fp,tween.tp,e); controls.target.lerpVectors(tween.ft,tween.tt,e);
    if(tween.t>=1) tween=null;
  }
  controls.update();
  // markers + compass
  const cp=new THREE.Vector3();
  MARKS.forEach((m,i)=>{
    cp.copy(m.f()).project(camera);
    const el=marks[i];
    if(cp.z>1){el.style.display='none';return;}
    el.style.display='';
    el.style.left=(cp.x*.5+.5)*innerWidth+'px'; el.style.top=(-cp.y*.5+.5)*innerHeight+'px';
    const d=camera.position.distanceTo(m.f());
    el.classList.toggle('dim',d>m.d*1.9);
  });
  const bearing=(Math.atan2(camera.position.x-controls.target.x,-(camera.position.z-controls.target.z))*180/Math.PI+360)%360;
  needle.setAttribute('transform','rotate('+(-bearing)+' 50 50)');
  brg.textContent='bearing '+String(Math.round(bearing)).padStart(3,'0')+'°';
  statusTimer+=dt;
  if(statusTimer>3.4){ statusTimer=0;
    const pool=approach>.5?statusLines.moored:statusLines.approach;
    statusEl.textContent=pool[Math.floor(Math.random()*pool.length)]+' · wind '+Math.round(wind*28)+' kn';
  }
  tstate.textContent=approach>.5?'moored · canvas furled':'approaching · canvas up';
  stamp.classList.toggle('on',approach>.6);
  document.getElementById('draft').textContent=(4.2+wind*.4).toFixed(1)+' m aft';
  renderer.render(scene,camera);
}
renderer.setAnimationLoop(frame);
addEventListener('resize',()=>{
  camera.aspect=innerWidth/innerHeight; camera.updateProjectionMatrix(); renderer.setSize(innerWidth,innerHeight);
});
/* boot: paint, intro dolly, fade */
applySky();
setTimeout(()=>{
  document.getElementById('boot').classList.add('gone');
  tween={fp:camera.position.clone(),ft:controls.target.clone(),tp:HOME.p.clone(),tt:HOME.t.clone(),t:0,d:2.6};
},260);
</script>
</body>
</html>
```

**What's in it**

- **Voxel pipeline:** one instanced-box builder (`fill`, `beam`, `rope`, `tri`) → ~40k instanced cubes with per-instance color jitter, chunky LOD masses for the pier so the ship stays the detailed subject.
- **The ship is the hero:** hull shaped by sheer-line/half-breadth functions, hollow interior with deck furniture, three masts with yards, shrouds + ratlines, stays, bowsprit, gaff spanker, and *animated sails* that unfurl, bulge with the wind, or collapse into furled rolls. Flags, pennants and wake all react to the wind slider.
- **Harbor working:** stone pier with paving, fenders, bollards and coiled rope, bonded store with lit windows and an anchor signboard, customs house with a running clock, rotating light on Griffin Point with additive beam cones, two derricks with a swinging cargo hook, mooring lines that sag and tighten, a gangplank that lowers on berthing, barrels, coal piles, lamp posts, signal mast.
- **Living layer:** animated wave field with foam crests + ship wake, drifting clouds, circling gulls with flapping wings, galley and chimney smoke, spray off the breakwater, walking crew, four time-of-day presets that cross-fade sky, fog, lights, stars and exposure.
- **Interaction:** orbit/zoom, clickable amber survey marks that fly the camera to that object, wind slider, approach↔moor and rig controls, `1–4` for time, `space` to arrive/furle, live compass bearing, and a harbor master's ledger that updates as things happen.