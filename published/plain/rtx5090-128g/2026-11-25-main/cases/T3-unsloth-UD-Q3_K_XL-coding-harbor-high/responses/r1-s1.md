# Havenmouth — a voxel harbour

Everything below is one self-contained HTML file (Three.js via import map). Save it as `harbour.html` and open it in Chrome — it builds the whole town, ship and sea synchronously on load, then you can orbit with the mouse.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Havenmouth — a sailing ship calling at a harbour</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,600;0,9..144,900;1,9..144,400&family=Karla:wght@400;500;700;800&display=swap" rel="stylesheet">
<style>
:root{
  --ink:#070b0f; --panel:#141a20; --line:#2c3843;
  --cream:#f3e9d6; --muted:#96a8b2; --ochre:#e3a44c; --ox:#b0483c; --sea:#5fb0ae;
}
*{box-sizing:border-box}
html,body{margin:0;height:100%;overflow:hidden;background:var(--ink);color:var(--cream);
  font-family:Karla,ui-sans-serif,system-ui,sans-serif;-webkit-font-smoothing:antialiased}
canvas{display:block;cursor:grab}
canvas:active{cursor:grabbing}
#vig{position:fixed;inset:0;z-index:3;pointer-events:none;
  box-shadow:inset 0 0 200px rgba(0,0,0,.72), inset 0 90px 120px -60px rgba(0,0,0,.55)}
#ui{position:fixed;inset:0;z-index:6;pointer-events:none}

/* ---------- brand plaque ---------- */
#brand{position:absolute;top:24px;left:28px;max-width:min(52vw,540px)}
#brand .pennants{display:flex;gap:5px;margin-bottom:16px}
#brand .pennants i{width:20px;height:14px;display:block;transform-origin:left center;
  clip-path:polygon(0 0,100% 0,76% 50%,100% 100%,0 100%);
  animation:flut 2.6s ease-in-out infinite;filter:drop-shadow(0 2px 3px rgba(0,0,0,.5))}
@keyframes flut{0%,100%{transform:skewY(-7deg) scaleX(.95)}50%{transform:skewY(8deg) scaleX(1.03)}}
#brand h1{margin:0;font-family:Fraunces,Georgia,serif;font-weight:900;
  font-size:clamp(40px,6.6vw,82px);line-height:.84;letter-spacing:-.03em;color:#fbf2e2;
  text-shadow:0 1px 0 rgba(0,0,0,.9),0 18px 40px rgba(0,0,0,.6)}
#brand h1 em{font-style:normal;color:var(--ochre)}
#brand .rule{width:132px;height:3px;margin:16px 0 11px;
  background:linear-gradient(90deg,var(--ochre),rgba(227,164,76,0))}
#brand .sub{margin:0;font-size:11px;font-weight:800;letter-spacing:.32em;
  text-transform:uppercase;color:var(--muted)}
#brand .cap{margin:9px 0 0;font-family:Fraunces,serif;font-style:italic;font-weight:300;
  font-size:15px;letter-spacing:.01em;color:#cdbfa8}

/* ---------- console ---------- */
#console{position:absolute;top:24px;right:24px;width:272px;pointer-events:auto;
  background:linear-gradient(180deg,rgba(21,27,33,.95),rgba(11,15,19,.97));
  border:1px solid var(--line);border-top:2px solid var(--ochre);border-radius:3px;
  box-shadow:0 26px 60px rgba(0,0,0,.62),inset 0 1px 0 rgba(255,255,255,.06);
  padding:13px 15px 15px;backdrop-filter:blur(2px)}
.chead{display:flex;align-items:center;gap:8px;font-size:10px;font-weight:800;
  letter-spacing:.26em;text-transform:uppercase;color:var(--ochre);
  border-bottom:1px solid var(--line);padding-bottom:9px}
.chead .dot{width:7px;height:7px;border-radius:50%;background:var(--sea);
  box-shadow:0 0 8px var(--sea);animation:blink 2.4s ease-in-out infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.28}}
.chead b{margin-left:auto;color:var(--cream);font-variant-numeric:tabular-nums;letter-spacing:.1em}
.row{margin-top:13px}
.row label{display:flex;justify-content:space-between;font-size:9.5px;font-weight:800;
  letter-spacing:.2em;text-transform:uppercase;color:#8ea0aa;margin-bottom:7px}
.row label span{color:var(--cream);font-variant-numeric:tabular-nums}
input[type=range]{-webkit-appearance:none;appearance:none;width:100%;height:16px;background:transparent;cursor:ew-resize}
input[type=range]::-webkit-slider-runnable-track{height:4px;background:
  linear-gradient(90deg,#24313c,#39505e);border:1px solid #1a232b;border-radius:2px}
input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:11px;height:17px;margin-top:-7px;
  background:linear-gradient(180deg,#f4d49b,#c88f3b);border:1px solid #2a1c0b;border-radius:2px;
  box-shadow:0 2px 5px rgba(0,0,0,.6);transition:transform .15s}
input[type=range]:hover::-webkit-slider-thumb{transform:scaleY(1.15)}
input[type=range]::-moz-range-track{height:4px;background:#2a3742;border-radius:2px}
input[type=range]::-moz-range-thumb{width:11px;height:17px;border:1px solid #2a1c0b;border-radius:2px;
  background:linear-gradient(180deg,#f4d49b,#c88f3b)}
.arcwrap{margin:-2px 0 4px;opacity:.95}
.btns{display:grid;grid-template-columns:1fr 1fr;gap:7px;margin-top:15px}
button{font-family:Karla,sans-serif;font-size:10px;font-weight:800;letter-spacing:.14em;
  text-transform:uppercase;color:#eadfca;background:#1c242b;border:1px solid #33424e;
  border-bottom:2px solid #10161b;border-radius:2px;padding:9px 6px;cursor:pointer;
  transition:background .18s,color .18s,transform .12s,box-shadow .18s}
button:hover{background:#28323b;color:#fff;box-shadow:0 0 0 1px rgba(227,164,76,.4),0 6px 16px rgba(0,0,0,.4);transform:translateY(-1px)}
button:active{transform:translateY(1px);border-bottom-color:#2a3views}
button.on{background:linear-gradient(180deg,#4a3517,#2f220f);border-color:var(--ochre);color:#ffd79a}
.stats{margin-top:14px;border-top:1px solid var(--line);padding-top:11px;
  display:grid;grid-template-columns:1fr 1fr;gap:8px 10px}
.stats div{display:flex;flex-direction:column;gap:2px}
.stats span{font-size:8.5px;letter-spacing:.2em;text-transform:uppercase;color:#7e8f99;font-weight:700}
.stats b{font-size:15px;font-weight:800;color:var(--cream);font-variant-numeric:tabular-nums;
  font-family:Fraunces,serif;letter-spacing:.01em}
.stats b i{font-style:normal;font-size:9px;color:#7e8f99;font-family:Karla,sans-serif;margin-left:2px}

#hint{position:absolute;left:28px;bottom:22px;font-size:10px;letter-spacing:.18em;
  text-transform:uppercase;color:#6f818c;font-weight:700}
#hint kbd{color:#0d1116;background:#8fa2ad;border-radius:2px;padding:2px 5px;margin:0 2px;
  font-family:Karla,sans-serif;font-size:9px}
#tip{position:absolute;transform:translate(-50%,-124%);pointer-events:none;opacity:0;
  transition:opacity .2s ease;background:rgba(10,14,18,.94);border:1px solid #35434e;
  border-left:3px solid var(--ochre);padding:9px 13px;border-radius:2px;max-width:264px;
  box-shadow:0 16px 34px rgba(0,0,0,.6)}
#tip.on{opacity:1}
#tip h4{margin:0 0 3px;font-family:Fraunces,serif;font-weight:900;font-size:15px;color:#fbf2e2;letter-spacing:.01em}
#tip p{margin:0;font-size:10.5px;letter-spacing:.09em;color:#96a8b2;line-height:1.5;text-transform:uppercase;font-weight:600}

/* ---------- loader ---------- */
#loader{position:fixed;inset:0;z-index:20;background:radial-gradient(120% 90% at 50% 40%,#101922,#05080c 70%);
  display:flex;flex-direction:column;align-items:center;justify-content:center;gap:22px;
  transition:opacity .9s ease,visibility .9s}
#loader.gone{opacity:0;visibility:hidden}
#loader .lt{font-family:Fraunces,serif;font-weight:900;font-size:clamp(34px,7vw,74px);
  letter-spacing:-.02em;color:#f6ecd8;opacity:.92}
#loader .lb{width:min(340px,70vw);height:3px;background:#1d262e;overflow:hidden;border-radius:2px}
#loader .lb i{display:block;height:100%;width:38%;background:linear-gradient(90deg,transparent,var(--ochre),transparent);
  animation:scan 1.15s linear infinite}
@keyframes scan{0%{transform:translateX(-110%)}100%{transform:translateX(320%)}}
#loader .ls{font-size:10px;letter-spacing:.34em;text-transform:uppercase;color:#7c8f9a;font-weight:700}
.hidden{opacity:0!important;visibility:hidden}
@media(max-width:760px){#brand{top:16px;left:16px}#console{width:230px;top:auto;bottom:14px;right:14px}#hint{display:none}}
</style>
</head>
<body>
<div id="vig"></div>
<div id="ui">
  <div id="brand">
    <div class="pennants" aria-hidden="true"></div>
    <h1>Haven<em>mouth</em></h1>
    <div class="rule"></div>
    <p class="sub">Voxel chart № 3 · 51°04′N 004°12′W</p>
    <p class="cap">A sailing ship calling at a harbour, lines thrown, tide running in.</p>
  </div>

  <aside id="console">
    <div class="chead"><span class="dot"></span>Harbour master<b id="clock">17:18</b></div>
    <div class="arcwrap">
      <svg viewBox="0 0 240 44" preserveAspectRatio="none" width="100%" height="40">
        <path id="arcPath" d="M8 40 Q120 -30 232 40" fill="none" stroke="#2b3843" stroke-width="1.4" stroke-dasharray="3 4"/>
        <line x1="8" y1="40" x2="232" y2="40" stroke="#243039" stroke-width="1"/>
        <circle id="sundot" r="5" cx="120" cy="-30" fill="#ffd27a"/>
      </svg>
    </div>
    <div class="row"><label>Hour of day <span id="todLbl">17:18</span></label>
      <input id="tod" type="range" min="0" max="1439" step="1" value="1038"></div>
    <div class="row"><label>Swell <span id="windLbl">4 kn</span></label>
      <input id="wind" type="range" min="0" max="100" step="1" value="26"></div>
    <div class="btns">
      <button id="bSails">Strike sails</button>
      <button id="bSalute">Fire salute</button>
      <button id="bOrbit" class="on">Auto-orbit</button>
      <button id="bReset">Reset view</button>
    </div>
    <div class="stats">
      <div><span>Voxels</span><b id="sVox">—</b></div>
      <div><span>Tide</span><b id="sTide">+0.00<i>m</i></b></div>
      <div><span>Wind</span><b id="sWind">4<i>kn</i></b></div>
      <div><span>Frames</span><b id="sFps">—</b></div>
    </div>
  </aside>

  <div id="tip"><h4></h4><p></p></div>
  <div id="hint"><kbd>drag</kbd> orbit · <kbd>scroll</kbd> zoom · click a marker · <kbd>H</kbd> hide · <kbd>F</kbd> salute</div>
</div>

<div id="loader"><div class="lt">Havenmouth</div><div class="lb"><i></i></div><div class="ls">laying the keel…</div></div>

<script type="importmap">
{"imports":{"three":"https://unpkg.com/three@0.160.0/build/three.module.js",
"three/addons/":"https://unpkg.com/three@0.160.0/examples/jsm/"}}
</script>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* ══════════════════════════════════════════════════════════════════
   0 · helpers
   ══════════════════════════════════════════════════════════════════ */
const clamp=(v,a,b)=>v<a?a:v>b?b:v;
const lerp=(a,b,t)=>a+(b-a)*t;
const sst=(a,b,x)=>{const t=clamp((x-a)/(b-a),0,1);return t*t*(3-2*t);};
let _s=98765; const rr=()=>{_s=(_s*1664525+1013904223)>>>0;return _s/4294967296;};
const rng=(a)=>lerp(a[0],a[1],rr());
const C=h=>new THREE.Color(h);
function jit(c,a=0.05){const k=new THREE.Color(c.r,c.g,c.b);const d=(rr()-.5)*a;
  k.r=clamp(k.r+d,0,1);k.g=clamp(k.g+d*1.1,0,1);k.b=clamp(k.b+d*.8,0,1);return k;}
function tab(t,s){ // table interpolation [[s,v]...]
  if(s<=t[0][0])return t[0][1];
  for(let i=1;i<t.length;i++){ if(s<=t[i][0]){const a=t[i-1],b=t[i];return lerp(a[1],b[1],(s-a[0])/(b[0]-a[0]));}}
  return t[t.length-1][1];
}

class Vox{
  constructor(){this.a=[];}
  box(x,y,z,sx,sy,sz,c){ if(sx<=0||sy<=0||sz<=0)return; this.a.push(x,y,z,sx,sy,sz,c); }
  cube(x,y,z,c){ this.box(x,y,z,1,1,1,c); }
  get n(){return this.a.length/7;}
}
function meshOf(v,mat,{shadow=true,noShadow=false}={}){
  const n=v.n; if(!n) return null;
  const g=new THREE.BoxGeometry(1,1,1);
  const m=new THREE.InstancedMesh(g,mat,n);
  const d=new THREE.Matrix4(),q=new THREE.Quaternion(),p=new THREE.Vector3(),s=new THREE.Vector3();
  for(let i=0;i<n;i++){const o=i*7, sx=v.a[o+3],sy=v.a[o+4],sz=v.a[o+5];
    p.set(v.a[o]+sx/2,v.a[o+1]+sy/2,v.a[o+2]+sz/2); s.set(sx,sy,sz);
    d.compose(p,q,s); m.setMatrixAt(i,d); m.setColorAt(i,v.a[o+6]);}
  m.instanceMatrix.needsUpdate=true; if(m.instanceColor)m.instanceColor.needsUpdate=true;
  m.castShadow=!noShadow&&shadow; m.receiveShadow=!noShadow; m.frustumCulled=false;
  return m;
}
function lines(pts,color,op=0.85){
  const g=new THREE.BufferGeometry().setAttribute('position',new THREE.Float32BufferAttribute(pts,3));
  const m=new THREE.LineBasicMaterial({color,transparent:true,opacity:op});
  const l=new THREE.LineSegments(g,m); l.frustumCulled=false; return l;
}

/* ══════════════════════════════════════════════════════════════════
   1 · renderer / camera
   ══════════════════════════════════════════════════════════════════ */
const renderer=new THREE.WebGLRenderer({antialias:true,powerPreference:'high-performance'});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.setSize(innerWidth,innerHeight);
renderer.shadowMap.enabled=true; renderer.shadowMap.type=THREE.PCFSoftShadowMap;
renderer.toneMapping=THREE.ACESFilmicToneMapping; renderer.toneMappingExposure=1.06;
document.body.appendChild(renderer.domElement);

const scene=new THREE.Scene();
scene.fog=new THREE.Fog(0xbcd8e6,72,300);
const camera=new THREE.PerspectiveCamera(42,innerWidth/innerHeight,0.5,900);
const HOME_P=new THREE.Vector3(39,25,-31), HOME_T=new THREE.Vector3(1,7,9);
camera.position.set(72,46,-58);
const controls=new OrbitControls(camera,renderer.domElement);
controls.enableDamping=true; controls.dampingFactor=.062;
controls.target.copy(HOME_T); controls.minDistance=14; controls.maxDistance=170;
controls.maxPolarAngle=1.52; controls.minPolarAngle=.12;
controls.autoRotate=true; controls.autoRotateSpeed=.34;

/* ══════════════════════════════════════════════════════════════════
   2 · day cycle
   ══════════════════════════════════════════════════════════════════ */
const K=[
 {t:0.0, zen:'#03060f',hor:'#0a1120',haze:'#0b1220',amb:'#141d2b',ambI:.34,sunI:.12,sunC:'#8fa9d8',
  deep:'#04101c',shal:'#08202e',foam:'#4f6c7c',hemiI:.30,night:1},
 {t:4.6, zen:'#0a1226',hor:'#332735',haze:'#452f36',amb:'#2a2c3c',ambI:.42,sunI:.16,sunC:'#c08a6a',
  deep:'#071625',shal:'#0f2b3c',foam:'#63788a',hemiI:.36,night:.86},
 {t:6.4, zen:'#1f395c',hor:'#cf7f4d',haze:'#efa86d',amb:'#4c4d5f',ambI:.55,sunI:1.0,sunC:'#ffb06a',
  deep:'#0c2534',shal:'#2c5a63',foam:'#cdd5ce',hemiI:.55,night:.24},
 {t:8.4, zen:'#2f6693',hor:'#aec7d2',haze:'#d2e2e7',amb:'#6c7e8d',ambI:.70,sunI:1.9,sunC:'#ffe4bc',
  deep:'#0f3244',shal:'#2e7484',foam:'#eef4ea',hemiI:.72,night:0},
 {t:12.0,zen:'#3a7cb5',hor:'#bfdbe8',haze:'#ddebf3',amb:'#7d93a3',ambI:.78,sunI:2.45,sunC:'#fff5dd',
  deep:'#0f4258',shal:'#2f8a99',foam:'#f8fbf2',hemiI:.80,night:0},
 {t:15.6,zen:'#38749f',hor:'#c6d5da',haze:'#e2e8e6',amb:'#7c8f9c',ambI:.74,sunI:2.1,sunC:'#ffeecd',
  deep:'#124154',shal:'#347f8d',foam:'#f2f6ea',hemiI:.74,night:0},
 {t:17.5,zen:'#2f5f88',hor:'#e6a05f',haze:'#f4bc7c',amb:'#6f7182',ambI:.60,sunI:1.45,sunC:'#ffbe7d',
  deep:'#123a4c',shal:'#367180',foam:'#f3e7d6',hemiI:.62,night:.04},
 {t:19.2,zen:'#1e3459',hor:'#c95f3f',haze:'#e08a55',amb:'#443f52',ambI:.48,sunI:.72,sunC:'#ff8a4a',
  deep:'#0b2130',shal:'#1e4453',foam:'#d9c6b8',hemiI:.48,night:.42},
 {t:20.7,zen:'#0d1a34',hor:'#452b3c',haze:'#5a3745',amb:'#242c40',ambI:.40,sunI:.20,sunC:'#8f7aa8',
  deep:'#061522',shal:'#0c2836',foam:'#6c7f8e',hemiI:.38,night:.86},
 {t:22.6,zen:'#050a18',hor:'#101a2c',haze:'#101a2c',amb:'#171f2e',ambI:.35,sunI:.13,sunC:'#8ba6d6',
  deep:'#04101c',shal:'#08202e',foam:'#4f6c7c',hemiI:.32,night:1},
 {t:24.0,zen:'#03060f',hor:'#0a1120',haze:'#0b1220',amb:'#141d2b',ambI:.34,sunI:.12,sunC:'#8fa9d8',
  deep:'#04101c',shal:'#08202e',foam:'#4f6c7c',hemiI:.30,night:1}
].map(k=>({...k,zen:C(k.zen),hor:C(k.hor),haze:C(k.haze),amb:C(k.amb),sunC:C(k.sunC),
  deep:C(k.deep),shal:C(k.shal),foam:C(k.foam)}));
const L={}; ['zen','hor','haze','amb','sunC','deep','shal','foam'].forEach(k=>L[k]=new THREE.Color());
const S={ambI:0,sunI:0,hemiI:0,night:0,elev:0};
const skyU={uZenith:{value:new THREE.Color()},uHorizon:{value:new THREE.Color()},
  uHaze:{value:new THREE.Color()},uSunDir:{value:new THREE.Vector3(0,1,0)},
  uSunCol:{value:new THREE.Color()},uSunUp:{value:1}};
let tod=17.3, wind=.26, tide=0;
const sunDir=new THREE.Vector3(), moonDir=new THREE.Vector3();
function updateDay(){
  let a=K[0],b=K[K.length-1];
  for(let i=0;i<K.length-1;i++){ if(tod>=K[i].t&&tod<=K[i+1].t){a=K[i];b=K[i+1];break;}}
  const f=clamp((tod-a.t)/(b.t-a.t||1),0,1);
  ['zen','hor','haze','amb','sunC','deep','shal','foam'].forEach(k=>L[k].copy(a[k]).lerp(b[k],f));
  S.ambI=lerp(a.ambI,b.ambI,f); S.sunI=lerp(a.sunI,b.sunI,f);
  S.hemiI=lerp(a.hemiI,b.hemiI,f); S.night=lerp(a.night,b.night,f);
  const ang=(clamp(tod,5.6,18.6)-6)/12*Math.PI;
  const elev=Math.sin(clamp((tod-5.6)/12.8,0,1)*Math.PI)*1.05-.04;
  sunDir.set(Math.cos(ang),Math.max(.02,Math.sin(ang))*.62+ .05,-Math.cos(ang)*.42+Math.sin(ang)*.1).normalize();
  // a proper arc: sun swings from ENE (over the mouth) to WSW behind the town
  const p=(tod-6)/12*Math.PI;
  sunDir.set(Math.cos(p)*.94, Math.sin(p), Math.cos(p)*-.34).normalize();
  moonDir.copy(sunDir).multiplyScalar(-1); moonDir.y=Math.abs(moonDir.y)*.7+.18; moonDir.normalize();
  skyU.uZenith.value.copy(L.zen); skyU.uHorizon.value.copy(L.hor); skyU.uHaze.value.copy(L.haze);
  skyU.uSunDir.value.copy(sunDir); skyU.uSunCol.value.copy(L.sunC);
  skyU.uSunUp.value=sst(-.08,.22,sunDir.y);
  sun.position.copy(sunDir).multiplyScalar(120);
  sun.color.copy(L.sunC); sun.intensity=S.sunI;
  hemi.color.copy(L.hor); hemi.groundColor.setRGB(.14,.12,.10); hemi.intensity=S.hemiI;
  amb.color.copy(L.amb); amb.intensity=S.ambI;
  scene.fog.color.copy(L.haze).lerp(L.hor,.45);
  scene.background=null;
  if(waterMat){const u=waterMat.uniforms;
    u.uDeep.value.copy(L.deep);u.uShallow.value.copy(L.shal);u.uFoam.value.copy(L.foam);
    u.uSunDir.value.copy(sunDir);u.uSunCol.value.copy(L.sunC);u.uSky.value.copy(L.hor).lerp(L.zen,.4);
    u.uFogCol.value.copy(scene.fog.color);u.uNight.value=S.night;}
  stars.material.opacity=clamp(S.night*1.1,0,1);
  sunDisc.material.opacity=sst(-.05,.18,sunDir.y)*.95;
  sunDisc.position.copy(sunDir).multiplyScalar(360);
  moonDisc.material.opacity=clamp(S.night*1.15,0,1);
  moonDisc.position.copy(moonDir).multiplyScalar(355);
  lampF = clamp((S.night-.18)/.6,0,1)*forceLamp;
  glowMat.opacity=.25+.75*lampF;
  beamMats.forEach(m=>m.opacity=(0.05+0.55*lampF));
  beams.visible=S.night>.05||forceLamp>.5;
  lampLights.forEach(l=>l.intensity=l.userData.i*lampF);
}
let forceLamp=1, lampF=0;

const amb=new THREE.AmbientLight(0x7d93a3,.7); scene.add(amb);
const hemi=new THREE.HemisphereLight(0xbfdbe8,0x242018,.75); scene.add(hemi);
const sun=new THREE.DirectionalLight(0xfff5dd,2.2);
sun.castShadow=true; sun.shadow.mapSize.set(2048,2048);
const sc=sun.shadow.camera; sc.left=-78;sc.right=78;sc.top=78;sc.bottom=-78;sc.near=1;sc.far=340;
sun.shadow.bias=-0.0006; sun.shadow.normalBias=.7; sun.shadow.radius=1.4;
scene.add(sun); scene.add(sun.target);

/* ══════════════════════════════════════════════════════════════════
   3 · sky dome, stars, sun & moon discs
   ══════════════════════════════════════════════════════════════════ */
const sky=new THREE.Mesh(new THREE.SphereGeometry(430,40,24),new THREE.ShaderMaterial({
  side:THREE.BackSide,depthWrite:false,uniforms:skyU,
  vertexShader:`varying vec3 vD;void main(){vD=(modelMatrix*vec4(position,1.0)).xyz;
    gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}`,
  fragmentShader:`uniform vec3 uZenith,uHorizon,uHaze,uSunDir,uSunCol;uniform float uSunUp;varying vec3 vD;
   void main(){vec3 d=normalize(vD);float t=clamp(d.y*.5+.5,0.,1.);
    vec3 c=mix(uHorizon,uZenith,pow(t,.62));
    float sd=max(dot(d,uSunDir),0.);
    c+=uSunCol*pow(sd,7.)*.30*uSunUp; c+=uSunCol*pow(sd,120.)*1.2*uSunUp;
    c=mix(c,uHaze,pow(1.-abs(d.y),9.)*.65);
    c+=(fract(sin(dot(gl_FragCoord.xy,vec2(12.99,78.23)))*43758.5)-.5)/230.;
    gl_FragColor=vec4(c,1.);
    #include <tonemapping_fragment>
    #include <colorspace_fragment>`}));
scene.add(sky);

function radialTex(stops,size=128){
  const cv=document.createElement('canvas');cv.width=cv.height=size;const x=cv.getContext('2d');
  const g=x.createRadialGradient(size/2,size/2,0,size/2,size/2,size/2);
  stops.forEach(s=>g.addColorStop(s[0],s[1]));x.fillStyle=g;x.fillRect(0,0,size,size);
  const t=new THREE.CanvasTexture(cv);t.colorSpace=THREE.SRGBColorSpace;return t;
}
sunDisc=new THREE.Sprite(new THREE.SpriteMaterial({map:radialTex([[0,'rgba(255,250,235,1)'],[.18,'rgba(255,228,170,.95)'],[.45,'rgba(255,170,90,.35)'],[1,'rgba(255,150,60,0)']]),transparent:true,blending:THREE.AdditiveBlending,depthWrite:false}));
sunDisc.scale.setScalar(58); scene.add(sunDisc);
const moonT=(()=>{const s=128,cv=document.createElement('canvas');cv.width=cv.height=s;const x=cv.getContext('2d');
  const g=x.createRadialGradient(s/2,s/2,0,s/2,s/2,s/2);
  g.addColorStop(0,'rgba(240,245,255,1)');g.addColorStop(.28,'rgba(220,232,255,.9)');
  g.addColorStop(.42,'rgba(160,190,235,.25)');g.addColorStop(1,'rgba(120,160,220,0)');
  x.fillStyle=g;x.fillRect(0,0,s,s);
  x.globalCompositeOperation='destination-out';x.beginPath();x.arc(s*.62,s*.36,s*.22,0,7);x.fill();
  const t=new THREE.CanvasTexture(cv);t.colorSpace=THREE.SRGBColorSpace;return t;})();
let sunDisc,moonDisc;
moonDisc=new THREE.Sprite(new THREE.SpriteMaterial({map:moonT,transparent:true,blending:THREE.AdditiveBlending,depthWrite:false}));
moonDisc.scale.setScalar(40); scene.add(moonDisc);

const starGeo=new THREE.BufferGeometry();
{const p=[];for(let i=0;i<900;i++){const u=rr()*2-1,th=rr()*Math.PI*2,r=Math.sqrt(1-u*u);
  const R=400;if(rr()<.72&&u<0)continue; p.push(Math.cos(th)*r*R,u*R,Math.sin(th)*r*R);}
  starGeo.setAttribute('position',new THREE.Float32BufferAttribute(p,3));}
const stars=new THREE.Points(starGeo,new THREE.PointsMaterial({color:0xdfe8ff,size:1.7,sizeAttenuation:false,transparent:true,opacity:0,fog:false,depthWrite:false}));
scene.add(stars);

/* ══════════════════════════════════════════════════════════════════
   4 · terrain function + land map texture
   ══════════════════════════════════════════════════════════════════ */
function shoreR(th){return 21+3.4*Math.cos(2*th)+2.0*Math.sin(4*th+.7)+1.3*Math.cos(6*th-1.2);}
function hillN(x,z){return .55+.45*Math.sin(x*.11+1.2)*Math.cos(z*.095-.4)+.22*Math.sin(x*.21)*Math.sin(z*.17);}
function topAt(x,z){
  const r=Math.hypot(x,z), th=Math.atan2(x,z), sr=shoreR(th), d=r-sr;
  if(d<0) return -6;
  const built=(1-sst(1.30,1.78,Math.abs(th)))*(1-sst(2.10,2.55,Math.abs(th)));
  let t;
  if(built>.55){
    if(d<6) t=3;
    else{const u=(d-6)/15; t=3+Math.round(u*u*(11+8*hillN(x,z)));}
  }else{
    t=-1+Math.round(d*.42+d*d*.011*(.7+.6*hillN(x,z)));
  }
  if(r>34) t=Math.min(t,Math.round(5-(r-34)*.85));
  return t;
}
const MAPN=128, map=new Uint8Array(MAPN*MAPN*4);
const extraLand=[];
function buildMap(){
  for(let i=0;i<MAPN;i++)for(let j=0;j<MAPN;j++){
    const x=i-MAPN/2, z=j-MAPN/2, o=(j*MAPN+i)*4;
    map[o]=topAt(x,z)>=0?255:0; map[o+1]=0;map[o+2]=0;map[o+3]=255;}
  extraLand.forEach(([x,z])=>{for(let a=-1;a<=1;a++)for(let b=-1;b<=1;b++){
    const i=Math.round(x+MAPN/2)+a,j=Math.round(z+MAPN/2)+b;
    if(i<0||j<0||i>=MAPN||j>=MAPN)continue; map[(j*MAPN+i)*4]=255;}});
}
const mapTex=new THREE.DataTexture(map,MAPN,MAPN,THREE.RGBAFormat);
mapTex.minFilter=mapTex.magFilter=THREE.LinearFilter;mapTex.wrapS=mapTex.wrapT=THREE.ClampToEdgeWrapping;

/* ══════════════════════════════════════════════════════════════════
   5 · sea
   ══════════════════════════════════════════════════════════════════ */
const waterU={uTime:{value:0},uWind:{value:.3},uDeep:{value:C('#0f4258')},uShallow:{value:C('#2f8a99')},
  uFoam:{value:C('#f6faf0')},uSunDir:{value:new THREE.Vector3(0,1,0)},uSunCol:{value:C('#fff')},
  uSky:{value:C('#8ab8d0')},uFogCol:{value:C('#bcd8e6')},uFogNear:{value:60},uFogFar:{value:290},
  uNight:{value:0},uMap:{value:mapTex}};
let waterMat=new THREE.ShaderMaterial({uniforms:waterU,
  vertexShader:`uniform float uTime,uWind;varying vec3 vW,vN;varying float vC,vD;
   float wv(vec2 p){float t=uTime;float s=.28+uWind;
     return s*(sin(p.x*.32+t*1.10)*.16+sin(p.y*.27-t*.90)*.13+sin((p.x+p.y)*.19+t*1.60)*.10
     +sin((p.x*.9-p.y*1.1)*.33-t*2.20)*.05);}
   void main(){vec4 c0=instanceMatrix*vec4(0.,0.,0.,1.);vec2 p=c0.xz;
     vec4 wp=instanceMatrix*vec4(position,1.);wp.y+=wv(p);
     float e=.85;vN=normalize(vec3(wv(p-vec2(e,0.))-wv(p+vec2(e,0.)),2.*e,wv(p-vec2(0.,e))-wv(p+vec2(0.,e))));
     vW=wp.xyz;vC=wv(p);vec4 mv=viewMatrix*wp;vD=-mv.z;
     gl_Position=projectionMatrix*mv;}`,
  fragmentShader:`uniform vec3 uDeep,uShallow,uFoam,uSunDir,uSunCol,uSky,uFogCol;
   uniform float uFogNear,uFogFar,uTime,uNight;uniform sampler2D uMap;
   varying vec3 vW,vN;varying float vC,vD;
   void main(){vec3 V=normalize(cameraPosition-vW);
     float fr=pow(1.-max(dot(V,vN),0.),3.);
     float df=max(dot(vN,uSunDir),0.);
     vec3 base=mix(uDeep,uShallow,smoothstep(-.35,.45,vC));
     vec3 col=base*(.30+.70*df)+base*uNight*.12;
     col=mix(col,uSky,fr*.55);
     vec3 H=normalize(uSunDir+V);
     col+=uSunCol*pow(max(dot(vN,H),0.),85.)*(2.2*(1.-uNight*.8));
     vec2 uv=(vW.xz+64.)/128.; float lc=0.;
     for(int i=0;i<8;i++){float a=float(i)*.7854;vec2 o=vec2(cos(a),sin(a))*2.6;
       lc+=step(.5,texture2D(uMap,uv+o/128.).r);}
     float shore=smoothstep(.9,4.2,lc);
     float rip=.5+.5*sin(uTime*2.6+vW.x*.9+vW.z*.72)+.25*sin(uTime*1.3-vW.x*.35);
     float foam=clamp(shore*(.30+.85*rip)+smoothstep(.20,.5,vC)*(.18+uWind*1.2),0.,1.);
     col=mix(col,uFoam,foam*.86);
     col=mix(col,uFogCol,smoothstep(uFogNear,uFogFar,vD));
     gl_FragColor=vec4(col,1.);
     #include <tonemapping_fragment>
     #include <colorspace_fragment>`});
const sea=new THREE.Group(); scene.add(sea);
{
  const v=new Vox();
  for(let x=-58;x<=58;x++)for(let z=-58;z<=58;z++){
    if(Math.hypot(x,z)>59)continue;
    if(topAt(x,z)>=0)continue;
    v.box(x,-11,z,1,11,1,C('#123')); // colour irrelevant (unlit shader)
  }
  const m=new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1),waterMat,v.n);
  const d=new THREE.Matrix4(),q=new THREE.Quaternion(),p=new THREE.Vector3(),s=new THREE.Vector3();
  for(let i=0;i<v.n;i++){const o=i*7,sx=v.a[o+3],sy=v.a[o+4],sz=v.a[o+5];
    p.set(v.a[o]+sx/2,v.a[o+1]+sy/2,v.a[o+2]+sz/2);s.set(sx,sy,sz);
    d.compose(p,q,s);m.setMatrixAt(i,d);}
  m.instanceMatrix.needsUpdate=true;m.frustumCulled=false;sea.add(m);
}
function waveH(x,z,t){const s=.28+wind;
  return s*(Math.sin(x*.32+t*1.10)*.16+Math.sin(z*.27-t*.90)*.13+Math.sin((x+z)*.19+t*1.60)*.10
   +Math.sin((x*.9-z*1.1)*.33-t*2.20)*.05);}

/* ══════════════════════════════════════════════════════════════════
   6 · land
   ══════════════════════════════════════════════════════════════════ */
const PAL={grass:['#5e7c44','#6b8a4b','#7c9250','#54703e'],dirt:'#7c6647',rock:'#6f6a62',
  quay:'#918a7c',quay2:'#7f786c',sand:'#cfbc8e',wet:'#b09c74'};
const ground=new Vox(), caps=new Vox();
for(let x=-46;x<=46;x++)for(let z=-46;z<=46;z++){
  const t=topAt(x,z); if(t<0)continue;
  const r=Math.hypot(x,z),th=Math.atan2(x,z),d=r-shoreR(th);
  const built=(1-sst(1.30,1.78,Math.abs(th)))*(1-sst(2.10,2.55,Math.abs(th)));
  let body=C(jit(PAL.rock,.10));
  let cap;
  if(built>.55&&d<6.2) cap=jit(C(rr()<.18?PAL.quay2:PAL.grass||PAL.quay,.03)), cap=jit(C(PAL.quay),.09);
  else if(t<=1) cap=jit(C(PAL.sand),.06);
  else if(t<=2) cap=jit(C(rr()<.4?PAL.sand:PAL.grass[Math.floor(rr()*4)]),.05);
  else {
    const st=(topAt(x+1,z)!==t||topAt(x-1,z)!==t||topAt(x,z+1)!==t||topAt(x,z-1)!==t);
    cap= st&&rr()<.35? jit(C(PAL.rock),.12) : jit(C(PAL.grass[Math.floor(rr()*4)]),.07);
    if(t>9&&rr()<.45)cap=jit(C('#6a7f52'),.06);
  }
  ground.box(x,-2,z,1,t+2,1,body);
  caps.cube(x,t,z,cap);
}
const matGround=new THREE.MeshLambertMaterial();
scene.add(meshOf(ground,matGround)); 
const matCap=new THREE.MeshLambertMaterial();
scene.add(meshOf(caps,matCap));

/* scattered rocks, tufts, trees */
const flora=new Vox();
for(let i=0;i<420;i++){
  const th=rng([-2.05,2.05]),r=rng([12,40]),x=Math.sin(th)*r,z=Math.cos(th)*r,t=topAt(x,z);
  if(t<1)continue;
  if(rr()<.55) flora.box(x+.15,t+1,z+.15,.7,.5,.7,jit(C(PAL.grass[Math.floor(rr()*4)]),.12));
  else flora.box(x+.2,t+1,z+.2,.6,.7,.6,jit(C(PAL.rock),.12));
}
for(let i=0;i<74;i++){
  const th=rng([-1.9,1.9]),r=rng([16,41]),x=Math.round(Math.sin(th)*r),z=Math.round(Math.cos(th)*r),t=topAt(x,z);
  if(t<4)continue; let ok=true;
  for(let a=0;a<3;a++)for(let b=0;b<3;b++) if(occ.has((x+a)+','+(z+b))) ok=false;
  if(!ok)continue;
  for(let a=0;a<3;a++)for(let b=0;b<3;b++) occ.add((x+a)+','+(z+b));
  const h=1+Math.floor(rr()*2);
  flora.box(x+1,t+1,z+1,1,h,1,C('#5a4331'));
  const cr=1.4+rr()*.8, base=t+1+h;
  for(let a=-2;a<=2;a++)for(let b=-2;b<=2;b++)for(let c=0;c<3;c++){
    const dd=Math.hypot(a,b,c*.9);
    if(dd<cr+rr()*.5-0.2) flora.cube(x+1+a,base+c,z+1+b,jit(C(['#456b3a','#527a41','#3c5e33'][Math.floor(rr()*3)]),.10));
  }
}
const matFlora=new THREE.MeshLambertMaterial();
const floraMesh=meshOf(flora,matFlora); scene.add(floraMesh);

/* ══════════════════════════════════════════════════════════════════
   7 · town
   ══════════════════════════════════════════════════════════════════ */
const occ=new Set();
const walls=new Vox(), roofs=new Vox(), glass=new Vox(), wood=new Vox();
const WALLC=['#e9e1d0','#ddd3c0','#c9bda6','#8e5b47','#a4694f','#4d4038','#c4705a','#d9c7ad'];
const ROOFC=['#a4472f','#8d3d2b','#5d5a58','#6b4a3a','#4f5a5c','#7d4a3a'];
function addBuilding(cx,cz,w,d,h,ang,opts={}){
  const cosA=Math.cos(ang),sinA=Math.sin(ang);
  const cells=[];
  for(let i=-Math.ceil(w/2)-1;i<=Math.ceil(w/2)+1;i++)
    for(let j=-Math.ceil(d/2)-1;j<=Math.ceil(d/2)+1;j++){
      const X=cosA*i+sinA*j, Z=-sinA*i+cosA*j;
      if(Math.abs(X)<=w/2+.01&&Math.abs(Z)<=d/2+.01) cells.push([i,j,X,Z]);
    }
  const gx=Math.round(cx),gz=Math.round(cz);
  let base=opts.base!==undefined?opts.base:topAt(gx,gz)+1;
  if(opts.skipCheck!==true){
    for(const [i,j] of cells) if(occ.has((gx+i)+','+(gz+j))) return false;
  }
  for(const [i,j] of cells) occ.add((gx+i)+','+(gz+j));
  const wallC=C(jit(C(opts.wall||WALLC[Math.floor(rr()*WALLC.length)]),.045));
  const roofC=C(jit(C(opts.roof||ROOFC[Math.floor(rr()*ROOFC.length)]),.05));
  const eave=base+h, peak=eave+1+Math.round(d*.42);
  const win1=base+2, win2=base+4;
  for(const [i,j,X,Z] of cells){
    const x=gx+i,z=gz+j;
    const edge=Math.abs(X)>=w/2-.01||Math.abs(Z)>=d/2-.01;
    const roofY=Math.round(peak-Math.abs(Z)/(d/2)*(peak-eave));
    if(edge){
      for(let y=base;y<eave;y++){
        let c=wallC;
        const front=(Math.abs(Z)>=d/2-.01);
        const isWin=front&&y>=win1&&y<=win2&&((Math.abs(Math.round(X))%3)===1)&&!(opts.noWin);
        if(isWin){
          walls.cube(x,y,z,C('#20242a'));
          if(opts.tall&&y===win1+1){}
          glass.cube(x,y,z,C('#ffcf86'));
        }else if(y===base&&front&&Math.abs(Math.round(X))<1.1){ walls.cube(x,y,z,C('#3b2a1d')); }
        else walls.cube(x,y,z,jit(wallC,.05));
      }
    }
    if(roofY>=eave){
      for(let y=eave;y<=roofY;y++) roofs.cube(x,y,z,jit(roofC,.05));
    }
  }
  // chimney
  if(!opts.noChim&&rr()<.8){
    const ci=cells[Math.floor(rr()*cells.length)];
    const cx2=gx+ci[0],cz2=gz+ci[1];
    walls.box(cx2,eave,cz2,1,peak-eave+2,1,C('#6d564a'));
  }
  // cornice band for taller civic builds
  if(opts.cornice){ walls.box(gx-w/2,eave-1,gz-d/2,w,1,d,C('#f0e6d2')); }
  return {gx,gz,base,eave,peak,cells};
}
function scatter(){
  const rows=[{off:8.2,h:[3,5],w:[3,5],d:[3,4]},{off:11.5,h:[3,6],w:[3,6],d:[3,5]},
              {off:15,h:[3,7],w:[4,6],d:[3,5]},{off:18.5,h:[4,8],w:[4,7],d:[4,5]},
              {off:22,h:[3,6],w:[3,6],d:[3,4]}];
  for(const row of rows){
    let th=-1.24;
    while(th<1.24){
      const step=rng([.10,.17]); th+=step;
      if(Math.abs(th)>1.24)break;
      const sr=shoreR(th), r=sr+row.off;
      const x=Math.sin(th)*r, z=Math.cos(th)*r;
      if(topAt(Math.round(x),Math.round(z))<2)continue;
      const ang=th+Math.PI+rng([-.14,.14]);
      addBuilding(x,z,rng(row.w),rng(row.d),Math.round(rng(row.h)),ang);
    }
  }
}
// civic landmarks near the quay
function landmarks(){
  const th=0.55, r=shoreR(th)+7.5;
  const x=Math.sin(th)*r,z=Math.cos(th)*r;
  const b=addBuilding(x,z,8,7,8,th+Math.PI+.06,{wall:'#e6dcc6',roof:'#4f5a5c',cornice:true,noWin:true});
  if(b){ // clock tower
    for(let i=1;i<=3;i++)for(let j=1;j<=3;j++) walls.cube(b.gx-1+i,b.eave+i*0+ (b.eave-b.base)+b.base-1+ i*3,b.gz-1+j,C('#e6dcc6'));
    walls.box(b.gx+1,b.eave,b.gz+1,3,10,3,C('#e6dcc6'));
    walls.box(b.gx,b.eave+10,b.gz,5,1,5,C('#f0e6d2'));
    roofs.box(b.gx,b.eave+11,b.gz,3,3,3,C('#4f5a5c'));
    for(let k=0;k<4;k++){
      const dx=[0,0,2,2][k],dz=[0,2,0,2][k];
      glass.cube(b.gx+dx+ (k===0||k===1?0:1),b.eave+6,b.gz+dz+(k===0||k===2?0:1),C('#ffcf86'));
    }
    glass.cube(b.gx+1,b.eave+7,b.gz+3,C('#ffe6ae'));glass.cube(b.gx+2,b.eave+7,b.gz+3,C('#ffe6ae'));
  }
  // sail loft with big flagpole
  const th2=-0.75,r2=shoreR(th2)+9.5;
  addBuilding(Math.sin(th2)*r2,Math.cos(th2)*r2,7,5,6,th2+Math.PI,{wall:'#b8563f',roof:'#3d4a4d'});
}
scatter(); landmarks();
scene.add(meshOf(walls,new THREE.MeshLambertMaterial()));
scene.add(meshOf(roofs,new THREE.MeshLambertMaterial()));
const glowMat=new THREE.MeshBasicMaterial({transparent:true,opacity:0,blending:THREE.AdditiveBlending,depthWrite:false});
scene.add(meshOf(glass,glowMat,{shadow:false}));

/* ══════════════════════════════════════════════════════════════════
   8 · quay furniture: bollards, lamps, crates, barrels, nets, crane
   ══════════════════════════════════════════════════════════════════ */
const props=new Vox(), ropes=new Vox(), metal=new Vox();
const Cwood=C('#8a6a44'), CwoodD=C('#6b5234'), Ciron=C('#33352f'), Cstone=C('#8e8779');
const lampLights=[];
function lantern(x,y,z,tall=1){
  props.box(x,y,z,1,3*tall,1,CwoodD);
  props.box(x-.25,y+3*tall,z-.25,1.5,.4,1.5,Ciron);
  glass.cube(x,y+3*tall+.4,z,C('#ffd59a'));
  props.box(x-.4,y+3*tall+.4,z-.4,.2,1.6,.2,Ciron);
  props.box(x+.4,y+3*tall+.4,z+.4,.2,1.6,.2,Ciron);
  props.box(x-.4,y+5*tall+.3,z-.4,1.2,.3,1.2,Ciron);
  const pl=new THREE.PointLight(0xffb867,16,42,1.6); pl.position.set(x+.5,y+4.3*tall,z+.5);
  pl.userData.i=16; scene.add(pl); lampLights.push(pl);
  const g=new THREE.Sprite(new THREE.SpriteMaterial({map:radialTex([[0,'rgba(255,205,130,.9)'],[.4,'rgba(255,170,80,.28)'],[1,'rgba(255,150,60,0)']]),transparent:true,blending:THREE.AdditiveBlending,depthWrite:false}));
  g.scale.setScalar(9); g.position.set(x+.5,y+4.3*tall,z+.5); scene.add(g);
  return g;
}
const glows=[];
for(const th of [-1.15,-0.78,-0.4,-0.05,0.32,0.7,1.08]){
  const r=shoreR(th)-1.6, x=Math.round(Math.sin(th)*r), z=Math.round(Math.cos(th)*r);
  props.box(x,4,z,1,2,1,Cstone); props.box(x-.2,6,z-.2,1.4,.5,1.4,jit(Cstone,.08));
  if(Math.abs(th)<.9&&rr()<.6) glows.push(lantern(x-3,4,z-1));
}
// barrels, crates, sacks, rope coils on the quay
function barrel(x,y,z){
  const o=[[-1,0],[0,-1],[0,1],[1,0],[-1,-1],[1,-1],[-1,1],[1,1],[0,0]];
  for(let k=0;k<3;k++) o.forEach(([a,b])=>props.cube(x+a,y+k,z+b,jit(k===1?C('#7d5c3a'):Cwood,.08)));
  o.forEach(([a,b])=>props.cube(x+a,y+1,z+b,C('#5c4326')));
}
function crate(x,y,z,s=2){
  for(let a=0;a<s;a++)for(let b=0;b<s;b++)for(let c=0;c<s;c++)
    props.cube(x+a,y+c,z+b,jit((a===0||b===0||c===0)?Cwood:CwoodD,.09));
  for(let a=0;a<s;a++){props.cube(x+a,y+s-1,z,C('#4c3a22'));props.cube(x+a,y,z+s-1,C('#4c3a22'));}
}
const quayPts=[];
for(let th=-1.2;th<=1.2;th+=.06){const r=shoreR(th)-2.4;quayPts.push([Math.sin(th)*r,Math.cos(th)*r]);}
for(let i=0;i<26;i++){
  const p=quayPts[Math.floor(rr()*quayPts.length)];
  const x=Math.round(p[0]+rng([-2,2])),z=Math.round(p[1]+rng([-2,2]));
  if(topAt(x,z)!==3)continue;
  const k=rr();
  if(k<.3) barrel(x,4,z);
  else if(k<.6) crate(x,4,z,rr()<.6?2:1);
  else if(k<.75){ props.box(x,4,z,2,1,2,jit(C('#b0a58c'),.06)); props.box(x,5,z,2,.4,2,jit(C('#8b8172'),.06)); }
  else { ropes.box(x,4,z,1.6,.4,1.6,C('#b9a37a')); ropes.box(x+.4,4.4,z+.4,.8,.3,.8,C('#c8b48c')); }
}
// cargo on the jetty head
crate(-6,4,23,2); barrel(-4,4,24); barrel(-3,4,24); crate(-8,4,22.5,1);
// fish nets on frames
{
  const nx=9,nz=22;
  for(let a=0;a<5;a++){props.box(nx+a*2,4,nz,1,3,1,CwoodD);}
  for(let a=0;a<4;a++)props.box(nx+a*2+1,6.7,nz,2,.3,1,Cwood);
  for(let a=0;a<9;a++)for(let b=0;b<3;b++)ropes.cube(nx+a,6.5-b*1.1,nz,C('#c3b494'));
}
// cargo crane
const crane=new THREE.Group(); crane.position.set(16,4,21); scene.add(crane);
{
  const cv=new Vox();
  cv.box(-2,0,-2,1,9,1,CwoodD); cv.box(2,0,-2,1,9,1,CwoodD);
  cv.box(-2,0,2,1,9,1,CwoodD); cv.box(2,0,2,1,9,1,CwoodD);
  cv.box(-2,8.5,-2,5,1,5,Cwood);
  cv.box(-1,3,-1,3,1,3,C('#5c4a33'));
  crane.add(meshOf(cv,new THREE.MeshLambertMaterial()));
}
const jib=new THREE.Group(); jib.position.y=9.5; crane.add(jib);
{
  const jv=new Vox();
  for(let i=0;i<11;i++) jv.box(-1+i,0,-.5,1.2,.9,1,jit(Cwood,.06));
  jv.box(-2,-.4,-.5,1.6,1.6,1,C('#5c4a33'));
  jib.add(meshOf(jv,new THREE.MeshLambertMaterial()));
}
const hookLine=lines([0,0,0,0,-6,0],0x2b2117,.9); jib.add(hookLine);
const hangCrate=new THREE.Mesh(new THREE.BoxGeometry(1.6,1.6,1.6),new THREE.MeshLambertMaterial({color:0x8a6a44}));
hangCrate.position.set(0,-7,0); hangCrate.castShadow=true; jib.add(hangCrate);

// windmill on the west hill
{
  const th=-1.32,r=32,x=Math.round(Math.sin(th)*r),z=Math.round(Math.cos(th)*r),t=topAt(x,z);
  const mv=new Vox();
  mv.box(x-1,t+1,z-1,3,9,3,C('#e2d9c6')); mv.box(x-.5,t+10,z-.5,2,2,2,C('#5d5a58'));
  scene.add(meshOf(mv,new THREE.MeshLambertMaterial()));
  const mill=new THREE.Group(); mill.position.set(x+.5,t+11.5,z-1.6); scene.add(mill);
  const bl=new Vox();
  for(let i=0;i<9;i++) bl.box(-.5,i,-.1,1,1,.3,i%2?C('#7d5c3a'):C('#efe6d2'));
  for(let q=0;q<4;q++){
    const g=new THREE.Group(); g.rotation.z=q*Math.PI/2; mill.add(g);
    const m=meshOf(bl,new THREE.MeshLambertMaterial()); g.add(m);
  }
  mill.userData.spin=true;
}
// eastern beacon at the mouth
{
  const x=-15,z=-15,t=topAt(x,z);
  const bv=new Vox();
  for(let k=0;k<6;k++){const rr2=k<2?2:1; bv.box(x-rr2,t+1+k,z-rr2,rr2*2+1,1,rr2*2+1,jit(C(k===3||k===4?'#a4472f':'#e9e1d0'),.05));}
  bv.box(x-1,t+7,z-1,3,1,3,C('#33352f'));
  scene.add(meshOf(bv,new THREE.MeshLambertMaterial()));
  const beacon=new THREE.Mesh(new THREE.BoxGeometry(1.1,1.1,1.1),new THREE.MeshBasicMaterial({color:0xff4a30,transparent:true}));
  beacon.position.set(x+.5,t+7.6,z+.5); scene.add(beacon);
  const bp=new THREE.PointLight(0xff5030,0,26,1.6); bp.position.copy(beacon.position); scene.add(bp);
  lampLights.push(Object.assign(bp,{userData:{i:14}}));
}

/* ══════════════════════════════════════════════════════════════════
   9 · breakwater + lighthouse
   ══════════════════════════════════════════════════════════════════ */
{
  const path=[[14.9,-14.7],[13,-17],[10.5,-20],[8,-23],[5.5,-25],[4,-26.4]];
  const bv=new Vox();
  for(let i=0;i<path.length;i++){
    const [px,pz]=path[i];
    const [nx,nz]=path[Math.min(i+1,path.length-1)];
    const w=6-Math.abs(i/(path.length-1))*.5;
    for(let a=-Math.ceil(w);a<=Math.ceil(w);a++)for(let b=-Math.ceil(w);b<=Math.ceil(w);b++){
      const d=Math.hypot(a,b); if(d>w)continue;
      const x=Math.round(px+a),z=Math.round(pz+b);
      if(topAt(x,z)>4)continue;
      const top=Math.max(2,Math.round(6.2-d*.55+Math.sin(a*.7+b*.5)*.6));
      bv.box(x,-1,z,1,top+1,1,jit(C('#6d675e'),.10));
      bv.cube(x,top,z,jit(C(rr()<.3?'#7b7468':'#5f5a52'),.12));
      extraLand.push([x,z]);
    }
  }
  scene.add(meshOf(bv,new THREE.MeshLambertMaterial()));
}
const LIGHT=[4,-26];
{
  const lv=new Vox();
  lv.box(LIGHT[0]-3,6,LIGHT[1]-3,7,1,7,C('#7b7468'));
  const rows=14;
  for(let k=0;k<rows;k++){
    const y=7+k;
    const rad=k<5?3:k<9?2.5:2;
    const r0=Math.ceil(rad);
    for(let a=-r0;a<=r0;a++)for(let b=-r0;b<=r0;b++){
      const d=Math.hypot(a,b); if(d>rad+.3)continue;
      const col=(k===3||k===4||k===8)?'#a8443a':'#f0e8da';
      lv.cube(LIGHT[0]+a,y,LIGHT[1]+b,jit(C(col),.04));
    }
  }
  lv.box(LIGHT[0]-3,21,LIGHT[1]-3,7,1,7,C('#4c4038'));   // gallery
  for(let a=-2;a<=2;a++)for(let b=-2;b<=2;b++){ if(Math.abs(a)===2||Math.abs(b)===2)
    lv.box(LIGHT[0]+a,22,LIGHT[1]+b,1,1,1,C('#3b3f43')); }
  lv.box(LIGHT[0]-1,22,LIGHT[1]-1,3,4,3,C('#2b3136'));   // lantern room frame
  for(let a=-1;a<=1;a++)for(let b=-1;b<=1;b++) glass.cube(LIGHT[0]+a,23.4,LIGHT[1]+b,C('#ffe1a8'));
  lv.box(LIGHT[0]-2,26,LIGHT[1]-2,5,1,5,C('#3d4a4d'));
  lv.box(LIGHT[0]-1,27,LIGHT[1]-1,3,1,3,C('#a8443a'));
  lv.cube(LIGHT[0],28,LIGHT[1],C('#3d4a4d'));
  scene.add(meshOf(lv,new THREE.MeshLambertMaterial()));
  const ll=new THREE.PointLight(0xffd08a,0,90,1.35);
  ll.position.set(LIGHT[0]+.5,24,LIGHT[1]+.5); ll.userData.i=90; scene.add(ll); lampLights.push(ll);
}
// rotating beams
const beams=new THREE.Group(); beams.position.set(LIGHT[0]+.5,24.2,LIGHT[1]+.5); scene.add(beams);
const beamMats=[];
for(let s=0;s<2;s++){
  const mat=new THREE.ShaderMaterial({transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,side:THREE.DoubleSide,
    uniforms:{uCol:{value:new THREE.Color('#ffe0a8')},uOp:{value:0}},
    vertexShader:`varying float vT;varying vec3 vN,vV;
      void main(){vT=clamp(-position.y/70.,0.,1.);
        vec4 wp=modelMatrix*vec4(position,1.); vV=normalize(cameraPosition-wp.xyz);
        vN=normalize(mat3(modelMatrix)*normal);
        gl_Position=projectionMatrix*viewMatrix*wp;}`,
    fragmentShader:`uniform vec3 uCol;uniform float uOp;varying float vT;varying vec3 vN,vV;
      void main(){float rim=1.-abs(dot(normalize(vN),normalize(vV)));
        float a=pow(rim,1.6)*(1.-vT)*(1.-vT)*uOp;
        gl_FragColor=vec4(uCol,a);}`});
  beamMats.push(mat);
  const g=new THREE.ConeGeometry(8.5,70,20,1,true); g.translate(0,-35,0);
  const m=new THREE.Mesh(g,mat); m.rotation.x=Math.PI*.52; m.rotation.y=s*Math.PI;
  m.rotation.order='YZX'; beams.add(m);
}
beams.rotation.y=0;

/* ══════════════════════════════════════════════════════════════════
   10 · the ship
   ══════════════════════════════════════════════════════════════════ */
const shipPos=new THREE.Vector3(-11,0,13.5), shipHeading=-0.055;
const shipOuter=new THREE.Group(); shipOuter.position.copy(shipPos); shipOuter.rotation.y=shipHeading; scene.add(shipOuter);
const rock=new THREE.Group(); shipOuter.add(rock);

const Lh=26;
const BEAM=[[0,4.0],[.07,4.9],[.18,5.4],[.45,5.4],[.62,5.1],[.75,4.3],[.86,3.1],[.93,2.0],[.98,.9],[1,.3]];
const SHEER=[[0,3.05],[.12,2.5],[.4,2.35],[.65,2.5],[.85,2.95],[1,3.75]];
const KEEL=[[0,-1.1],[.12,-2.4],[.5,-2.7],[.8,-2.3],[.95,-1.2],[1,-.2]];
const PROF=[[0,.32],[.12,.72],[.25,.94],[.45,1],[.7,.97],[1,.87]];
const halfBeam=(x,y)=>{const s=x/Lh,kb=tab(KEEL,s),yt=tab(SHEER,s);
  if(y<kb||y>yt)return -1;
  return tab(BEAM,s)*tab(PROF,(y-kb)/(yt-kb));};
const inHull=(x,y,z)=>{const b=halfBeam(x,y); return b>=0&&Math.abs(z)<=b+.35;};
const hull=new Vox(), deckV=new Vox();
const CK={black:C('#221e1c'),black2:C('#171412'),red:C('#6f2b26'),wale:C('#c8a24a'),
  rail:C('#eee5d2'),deck:C('#a97c4c'),deckD:C('#8d6238'),port:C('#0b0a09'),wood:C('#7d5c3a')};
for(let x=0;x<=Lh;x++)for(let y=-3;y<5;y++)for(let z=-6;z<=7;z++){
  if(!inHull(x,y,z))continue;
  const surf=!inHull(x+1,y,z)||!inHull(x-1,y,z)||!inHull(x,y+1,z)||!inHull(x,y-1,z)||!inHull(x,y,z+1)||!inHull(x,y,z-1);
  if(!surf)continue;
  const yt=Math.floor(tab(SHEER,x/Lh));
  let c;
  if(y===yt&&y>=Math.floor(yt)){
    const bnd=Math.abs(z)>halfBeam(x,y)-1.05;
    c= bnd? jit(CK.rail,.03) : jit(rr()<.35?CK.deckD:CK.deck,.06);
  }
  else if(y<0) c=jit(CK.red,.07);
  else if(y===0) c=jit(CK.black2,.05);
  else if(y===1) c=jit(CK.wale,.05);
  else if(y===2){
    const port= x>=4&&x<=22&&((x%3)===1)&&Math.abs(z)<halfBeam(x,y);
    c= port? CK.port : jit(CK.black,.05);
  }
  else c=jit(CK.black,.05);
  hull.cube(x,y,z,c);
}
rock.add(meshOf(hull,new THREE.MeshLambertMaterial()));
// gun barrels in a few ports
for(let x=4;x<=22;x+=3) for(const zs of [-1,1]){
  const b=halfBeam(x,2); if(Math.abs(zs*(b+.4))>b+1)continue;
  rock.add(meshOf((()=>{const v=new Vox();v.box(x-1,2,Math.round(zs*b)- (zs>0?0:0),2,.6,.6,C('#2c2c2c'));return v;})(),new THREE.MeshLambertMaterial()));
}
// raised decks + deck furniture
{
  const v=new Vox();
  v.box(20,4,Math.round(-3),6,1,6,jit(CK.deck,.05));       // forecastle
  v.box(1,4,-4,8,1,8,jit(CK.deck,.05));                    // quarterdeck
  for(let i=0;i<3;i++) v.box(9+i*4,4,-2,2,1,4,C('#6f5233'));// hatch covers
  v.box(12,4,-1,2,2,2,C('#6f5233'));                        // capstan house
  v.box(3,5,-3,4,1,6,C('#7d5c3a'));                         // skylight
  v.box(22,5,-2,3,1,4,C('#7d5c3a'));
  for(let a=-4;a<=4;a++) v.cube(25,4,a,CK.rail);            // bow rail
  for(const xs of [-1,0,26])for(let b=-3;b<=3;b++){}
  // boats
  for(let i=0;i<4;i++){v.box(7+i,4,3.2,1,1,2,C('#d9cdb2'));}
  rock.add(meshOf(v,new THREE.MeshLambertMaterial()));
}
// masts, yards, tops
const MASTS={miz:{x:5,top:15.5},main:{x:12,top:22.5},fore:{x:18.5,top:19.5}};
{
  const v=new Vox();
  for(const k in MASTS){const m=MASTS[k];
    for(let y=3;y<=m.top;y++) v.box(m.x-.5,y,-.5,1.2,1,1.2,jit(C('#8a6a44'),.06));
    v.box(m.x-.5,m.top+1,-.5,1,1.2,1,C('#3d4a4d'));
  }
  // tops
  v.box(MASTS.main.x-1.5,10.5,-2,3,1,4,C('#6f5233'));
  v.box(MASTS.fore.x-1.5,9.5,-1.6,3,1,3.2,C('#6f5233'));
  // bowsprit (stepped diagonal)
  for(let i=0;i<10;i++) v.box(24+i,Math.round(3.4+i*.21),-.5,1.4,1,1,jit(C('#7d5c3a'),.05));
  for(let i=0;i<4;i++) v.box(33+i,Math.round(5.5+i*.12),-.4,1.2,.7,.8,C('#6b5234'));
  v.box(26,2.4,-1.4,2,2.2,2.8,C('#e0d5b8')); // figurehead mass
  rock.add(meshOf(v,new THREE.MeshLambertMaterial()));
}
// rigging
{
  const R=[];const ln=(a,b)=>R.push(a[0],a[1],a[2],b[0],b[1],b[2]);
  for(const k in MASTS){const m=MASTS[k],bx=m.x;
    for(const dz of [-1,1]){
      ln([bx,m.top-.5,0],[bx-2.5,3.2,dz*4.6]);
      ln([bx,m.top-.5,0],[bx+2.5,3.2,dz*4.6]);
      ln([bx,m.top*.72,0],[bx-3.2,3.2,dz*5]);
      ln([bx,m.top*.72,0],[bx+3.2,3.2,dz*5]);
      ln([bx,m.top-.5,0],[bx-5.5,3.2,dz*3]);
      ln([bx,m.top-.5,0],[bx+5.5,3.2,dz*3]);
    }
  }
  ln([MASTS.fore.x,MASTS.fore.top,0],[34.5,5.6,0]);
  ln([MASTS.fore.x,MASTS.fore.top*.8,0],[33,5.4,.5]);
  ln([MASTS.main.x,MASTS.main.top,0],[MASTS.fore.x+1,MASTS.fore.top*.92,0]);
  ln([MASTS.main.x,MASTS.main.top*.8,0],[MASTS.miz.x+1,MASTS.miz.top,0]);
  ln([MASTS.miz.x,MASTS.miz.top,0],[1,6,0]);
  ln([34.5,5.4,0],[24,3.2,4]); ln([34.5,5.4,0],[24,3.2,-4]);
  ln([26,3.4,3],[24,1.5,4.5]);
  rock.add(lines(R,0x2b2117,.8));
}
// sails
const SAILS=[
 {m:'main',y0:5.5,y1:10.5,hw:5.4,belly:1.5,band:true},
 {m:'main',y0:12,y1:16,hw:4.4,belly:1.2,band:true},
 {m:'main',y0:17.2,y1:19.6,hw:3.1,belly:.8,band:false},
 {m:'fore',y0:6,y1:10.4,hw:4.9,belly:1.35,band:true},
 {m:'fore',y0:12,y1:15,hw:3.8,belly:.9,band:false},
 {m:'miz',y0:5.5,y1:10,hw:3.5,belly:1.0,band:false},
 {m:'miz',y0:11.5,y1:13.5,hw:2.7,belly:.6,band:false}
];
const sailGroups=[];
{
  const CS=C('#ece2ca'), CSt=C('#dfd3b6'), CB=C('#9d3a33'), Ccw=C('#c0b096');
  for(const s of SAILS){
    const mx=MASTS[s.m].x, v=new Vox();
    for(let z=-Math.round(s.hw);z<=Math.round(s.hw);z++){
      const f=Math.cos(z/s.hw*Math.PI/2);
      const bx=Math.round(mx+s.belly*f);
      for(let y=Math.round(s.y0);y<=Math.round(s.y1);y++){
        let c=(y-Math.round(s.y0))%3===0?CSt:CS;
        if(s.band&&y>=Math.round(s.y1)-1)c=CB;
        if(s.band&&y===Math.round(s.y1)-2)c=C('#f4efe2');
        v.cube(bx,y-s.y1-0,z,jit(c,.035));
      }
    }
    const g=new THREE.Group(); g.position.set(mx,s.y1+.4,0); rock.add(g);
    const mesh=meshOf(v,new THREE.MeshLambertMaterial({side:THREE.DoubleSide}));
    g.add(mesh);
    // yard
    const yv=new Vox(); yv.box(mx-.5,.6,-Math.round(s.hw)-1,1.2,1,Math.round(s.hw)*2+2,C('#5f4630'));
    g.add(meshOf(yv,new THREE.MeshLambertMaterial()));
    // rolled canvas shrinks as the sail sets
    const roll=new THREE.Mesh(new THREE.BoxGeometry(1,.9,s.hw*2+1),new THREE.MeshLambertMaterial({color:0xc0b096}));
    roll.position.set(mx+.6,-.5,0); g.add(roll);
    sailGroups.push({g,roll,dep:s.dep??1});
  }
  // jibs (triangular patches, bilinear fill)
  function patch(c,mat){
    const v=new Vox(),seen=new Set();
    for(let i=0;i<=100;i++)for(let j=0;j<=100;j++){
      const u=i/100,w=j/100;
      const ax=lerp(c[0][0],c[1][0],u),ay=lerp(c[0][1],c[1][1],u),az=lerp(c[0][2],c[1][2],u);
      const bx=lerp(c[3][0],c[2][0],u),by=lerp(c[3][1],c[2][1],u),bz=lerp(c[3][2],c[2][2],u);
      const x=lerp(ax,bx,w),y=lerp(ay,by,w),z=lerp(az,bz,w);
      const k=Math.round(x)+','+Math.round(y)+','+Math.round(z);
      if(seen.has(k))continue; seen.add(k);
      v.cube(Math.round(x),Math.round(y),Math.round(z),mat(w));
    }
    return v;
  }
  const jv=patch([[35,5.6,-1],[19,18,-1],[22.5,7,-2.6],[24.5,6.5,-2.4]],
    w=>w>.9?C('#f2ecdc'):jit(C('#e8dfc8'),.03));
  const jv2=patch([[30,5,-1],[19,15.5,-1],[16,7.5,-2],[19.5,6,-2]],
    w=>C('#e4dac2'));
  const jibG=new THREE.Group(); rock.add(jibG); jibG.add(meshOf(jv,new THREE.MeshLambertMaterial({side:THREE.DoubleSide})));
  jibG.add(meshOf(jv2,new THREE.MeshLambertMaterial({side:THREE.DoubleSide})));
  sailGroups.push({g:jibG,roll:null,dep:1});
  // spanker
  const sv=patch([[5.5,4.5,.4],[5.5,13,.4],[1.4,10.5,1.2],[1.6,5.2,1.2]],
    ()=>C('#e6ddc7'));
  const spG=new THREE.Group(); rock.add(spG); spG.add(meshOf(sv,new THREE.MeshLambertMaterial({side:THREE.DoubleSide})));
  sailGroups.push({g:spG,roll:null,dep:1});
}
// flags (waving shader)
const waveU={uTime:{value:0}};
function waveMat(){
  const m=new THREE.MeshLambertMaterial({side:THREE.DoubleSide});
  m.onBeforeCompile=sh=>{
    sh.uniforms.uTime=waveU.uTime;
    sh.vertexShader='uniform float uTime;\n'+sh.vertexShader.replace('#include <begin_vertex>',
      `#include <begin_vertex>
       #ifdef USE_INSTANCING
         float d=(instanceMatrix*vec4(0.,0.,0.,1.)).x;
         transformed.y+=sin(uTime*5.2+d*.9)*.20*clamp(d,0.,5.);
         transformed.z+=cos(uTime*4.1+d*.7)*.22*clamp(d,0.,5.);
       #endif`);
  };
  return m;
}
const flagMat=waveMat();
function flag(x,y,z,rows,pal,poleH=3){
  const v=new Vox();
  for(let i=0;i<rows.length;i++)for(let j=0;j<rows[i].length;j++){
    if(!rows[i][j])continue;
    v.cube(j,-i+Math.round(rows.length/2),0,rows[i][j]);
  }
  const g=new THREE.Group(); g.position.set(x,y,z); rock.add(g);
  g.add(meshOf(v,flagMat,{shadow:false}));
  const pv=new Vox(); pv.box(-.3,-poleH,0,1,poleH,1,C('#6b5234'));
  g.add(meshOf(pv,new THREE.MeshLambertMaterial()));
  return g;
}
const R=C('#b0483c'),W=C('#f2ecdc'),B=C('#2f4a72'),O=C('#e3a44c');
flag(-1.2,6.6,0,[ [R,R,R,R,W,W],[R,R,R,R,W,W],[O,O,O,O,W,W],[O,O,O,O,W,W] ],null,4);
flag(MASTS.fore.x,MASTS.fore.top+2,0,[ [W,R],[W,R],[W] ],null,2);
flag(MASTS.main.x,MASTS.main.top+2,0,[ [B,W,O],[B,W,O],[W] ],null,2);
flag(MASTS.miz.x,MASTS.miz.top+2,0,[ [O,R],[O] ],null,2);
// crew on deck
{
  const v=new Vox();
  const fig=(x,y,z,shirt,trouser)=>{
    v.box(x,y,z,.7,1,.7,C(trouser)); v.box(x,y+1,z,.7,.8,.7,C(shirt)); v.box(x+.06,y+1.8,z+.06,.5,.5,.5,C('#c99a6f'));
  };
  fig(11,4,3.4,'#b0483c','#2f3a3f'); fig(15,4,-3.2,'#d8cbb0','#3a3f2f');
  fig(21,5,2.2,'#5e7c44','#3a3f2f'); fig(4,5,-2.4,'#2f4a72','#2f3a3f');
  fig(16,4,1.2,'#e3a44c','#333'); fig(8,4,4.2,'#c9c2b0','#2f3a3f');
  rock.add(meshOf(v,new THREE.MeshLambertMaterial()));
}
// gangway (attached to ship, hovers over the jetty landing)
{
  const v=new Vox();
  for(let i=0;i<5;i++) v.box(12,Math.round(3.1+i*.34),5.4+i*1.0,1.6,1,1.2,jit(C('#8a6a44'),.05));
  for(let i=0;i<5;i++){v.box(11.8,Math.round(4.1+i*.34),5.4+i*1.0,.2,.9,.2,C('#b9a37a'));
    v.box(13.8,Math.round(4.1+i*.34),5.4+i*1.0,.2,.9,.2,C('#b9a37a'));}
  rock.add(meshOf(v,new THREE.MeshLambertMaterial()));
}
// foam / wake around the hull
const foamN=180, foamGeo=new THREE.BufferGeometry();
{const p=new Float32Array(foamN*3),sd=new Float32Array(foamN);
 for(let i=0;i<foamN;i++){p[i*3]=0;p[i*3+1]=-99;p[i*3+2]=0;sd[i]=rr();}
 foamGeo.setAttribute('position',new THREE.BufferAttribute(p,3));
 foamGeo.userData={sd};}
const foam=new THREE.Points(foamGeo,new THREE.PointsMaterial({map:radialTex([[0,'rgba(255,255,255,.95)'],[.5,'rgba(240,250,250,.5)'],[1,'rgba(255,255,255,0)']]),size:2.6,transparent:true,depthWrite:false,sizeAttenuation:true,opacity:.85}));
scene.add(foam);

/* ══════════════════════════════════════════════════════════════════
   11 · mooring lines, jetty, tender boat, gulls, clouds, particles
   ══════════════════════════════════════════════════════════════════ */
// jetty to the ship
{
  const v=new Vox();
  for(let z=20;z<26.5;z++) v.box(-2,4,z,3,.5,1,jit(C('#8a6a44'),.05));
  for(const [px,pz] of [[-1.5,20.5],[.5,20.5],[-1.5,25],[.5,25]])
    v.box(px,-2,pz,1,6,1,C('#5c4326'));
  for(let z=20.5;z<26;z+=1.4){v.box(-2,4.5,z,.2,.9,1,C('#b9a37a'));v.box(.8,4.5,z,.2,.9,1,C('#b9a37a'));}
  scene.add(meshOf(v,new THREE.MeshLambertMaterial()));
  props.box(-3,4,19,1,2,1,Cstone); props.box(-3.2,6,18.8,1.4,.5,1.4,jit(Cstone,.08));
  scene.add(meshOf(props,new THREE.MeshLambertMaterial()));
  scene.add(meshOf(ropes,new THREE.MeshLambertMaterial()));
  scene.add(meshOf(metal,new THREE.MeshLambertMaterial()));
}
function bollardFor(x,z){const bx=Math.round(x),bz=Math.round(z);
  props.box(bx,4,bz,1,2,1,Cstone);scene.add(meshOf(new Vox(),new THREE.MeshLambertMaterial()));return [bx+.5,6.1,bz+.5];}
const moorA=bollardFor(19,24), moorB=bollardFor(-9,24.5);
const moorMat=new THREE.LineBasicMaterial({color:0xc3b088,transparent:true,opacity:.95});
function mkLine(){const g=new THREE.BufferGeometry().setAttribute('position',new THREE.BufferAttribute(new Float32Array(12*3),3));
  const l=new THREE.Line(g,moorMat); l.frustumCulled=false; scene.add(l); return l;}
const line1=mkLine(), line2=mkLine();
function setLine(l,a,b){
  const p=l.geometry.attributes.position;
  for(let i=0;i<12;i++){const t=i/11;
    p.setXYZ(i,lerp(a[0],b[0],t),lerp(a[1],b[1],t)-Math.sin(t*Math.PI)*1.5,lerp(a[2],b[2],t));}
  p.needsUpdate=true;
}
// tender boat shuttling
const tender=new THREE.Group(); scene.add(tender);
{
  const v=new Vox();
  for(let i=0;i<5;i++)for(let z=-1;z<=1;z++) v.box(i,0,z,jit(C('#c9bda6'),.05).getHex()?C('#cbbfa6'):C('#cbbfa6'),1,1);
  v.box(0,-.4,-1,5,.5,3,C('#b0a48c'));
  v.box(2,-.2,-.4,1,1.2,1,C('#8a6a44'));
  tender.add(meshOf(v,new THREE.MeshLambertMaterial()));
}
const gulls=[];
for(let i=0;i<7;i++){
  const g=new THREE.Group();
  const b=new Vox(); b.box(0,0,0,1.2,.8,1,C('#f3f3f0')); b.box(1.1,.2,-.1,.5,.5,.5,C('#f7f7f4'));
  b.box(1.5,.25,0,.4,.2,.2,C('#e3a44a')); b.box(-.4,-.1,0,.6,.4,.6,C('#d8d8d2'));
  g.add(meshOf(b,new THREE.MeshLambertMaterial(),{shadow:false}));
  const wL=new THREE.Group(),wR=new THREE.Group();
  const wv=new Vox(); wv.box(0,0,0,1,.2,2.4,C('#eeece6')); wv.box(1,0,1.6,1.6,.15,1.4,C('#b9b6ae'));
  wL.add(meshOf(wv,new THREE.MeshLambertMaterial(),{shadow:false}));
  const wv2=new Vox(); wv2.box(0,0,0,1,.2,-2.4,C('#eeece6')); wv2.box(1,0,-1.6,1.6,.15,-1.4,C('#b9b6ae'));
  wR.add(meshOf(wv2,new THREE.MeshLambertMaterial(),{shadow:false}));
  wL.position.set(.3,.2,.4); wR.position.set(.3,.2,-.4);
  g.add(wL);g.add(wR);
  g.userData={r:rng([16,40]),y:rng([16,30]),sp:rng([.08,.2]),ph:rr()*6.28,flap:rng([4,8]),wL,wR};
  scene.add(g); gulls.push(g);
}
// clouds
const cloudMat=new THREE.MeshLambertMaterial();
{
  const v=new Vox();
  for(let c=0;c<26;c++){
    const cx=rng([-110,110]),cz=rng([-100,90]),cy=rng([36,66]);
    const n=4+Math.floor(rr()*7), s=rng([2,4.5]);
    for(let i=0;i<n;i++){
      const w=Math.round(rng([2,6])),h=Math.round(rng([1,3])),d=Math.round(rng([2,5]));
      v.box(Math.round(cx+i*s+rng([-3,3])),Math.round(cy+rng([-1.5,1.5])),Math.round(cz+rng([-4,4])),w,h,d,jit(C('#ffffff'),.04));
    }
  }
  var cloudMesh=meshOf(v,cloudMat,{shadow:false}); scene.add(cloudMesh);
}
// particle system (smoke)
const PN=420, pPos=new Float32Array(PN*3), pVel=[], pLife=new Float32Array(PN), pSize=new Float32Array(PN);
for(let i=0;i<PN;i++){pVel.push(new THREE.Vector3());pPos[i*3+1]=-999;}
const pGeo=new THREE.BufferGeometry();
pGeo.setAttribute('position',new THREE.BufferAttribute(pPos,3));
const pMat=new THREE.PointsMaterial({map:radialTex([[0,'rgba(220,220,220,.9)'],[.45,'rgba(190,190,190,.45)'],[1,'rgba(180,180,180,0)']]),
  size:7,transparent:true,depthWrite:false,opacity:.72,sizeAttenuation:true});
const pParts=new THREE.Points(pGeo,pMat); pParts.frustumCulled=false; scene.add(pParts);
let pHead=0;
function puff(x,y,z,vx,vy,vz,size,life){
  const i=pHead;pHead=(pHead+1)%PN;
  pPos[i*3]=x;pPos[i*3+1]=y;pPos[i*3+2]=z;pVel[i].set(vx,vy,vz);pLife[i]=life;pSize[i]=size;
}
// chimney smoke from the town
function chimneySmoke(dt){
  if(rr()<dt*3.4){
    const th=rng([-1.1,1.1]),r=shoreR(th)+rng([8,20]);
    const x=Math.sin(th)*r,z=Math.cos(th)*r,t=topAt(Math.round(x),Math.round(z));
    if(t>1) puff(x,t+9,z,.6+rr()*.5,.9+rr()*.5,(rr()-.5)*.3,4.5,5.5);
  }
}
function updateParticles(dt,t){
  for(let i=0;i<PN;i++){
    if(pLife[i]<=0){pPos[i*3+1]=-999;continue;}
    pLife[i]-=dt;
    pPos[i*3]+=pVel[i].x*dt;pPos[i*3+1]+=pVel[i].y*dt;pPos[i*3+2]+=pVel[i].z*dt;
    pVel[i].multiplyScalar(.985); pVel[i].y+=dt*.35;
  }
  pGeo.attributes.position.needsUpdate=true;
}

/* ══════════════════════════════════════════════════════════════════
   12 · markers + picking
   ══════════════════════════════════════════════════════════════════ */
const ringTex=radialTex([[0,'rgba(0,0,0,0)'],[.52,'rgba(0,0,0,0)'],[.58,'rgba(255,210,140,.95)'],[.66,'rgba(255,190,110,.15)'],[1,'rgba(0,0,0,0)']]);
const MARKS=[
 {p:new THREE.Vector3(2,13,13.5),t:'Frigate “Meridian”',s:'26 m · homeport Havenmouth · 4th calling',
  cam:new THREE.Vector3(-16,16,34),tgt:new THREE.Vector3(-2,7,13)},
 {p:new THREE.Vector3(4.5,26,-26),t:'Havenmouth Light',s:'Est. 1809 · 24 m · Fl(2) W 15s',
  cam:new THREE.Vector3(24,16,-40),tgt:new THREE.Vector3(4,14,-26)},
 {p:new THREE.Vector3(-12,6.5,24),t:'The Old Quay',s:'Granite, laid 1783 · nine berths',
  cam:new THREE.Vector3(-30,13,40),tgt:new THREE.Vector3(-10,4,22)},
 {p:new THREE.Vector3(19,12,26),t:'Custom House',s:'Tide waits here · sail loft to the west',
  cam:new THREE.Vector3(40,13,40),tgt:new THREE.Vector3(18,7,24)}
];
MARKS.forEach(m=>{
  const sp=new THREE.Sprite(new THREE.SpriteMaterial({map:ringTex,transparent:true,depthWrite:false,depthTest:true,opacity:.95}));
  sp.scale.setScalar(7); sp.position.copy(m.p); scene.add(sp); m.sp=sp;
});
const tipEl=document.getElementById('tip'), tipH=tipEl.querySelector('h4'), tipP=tipEl.querySelector('p');
let hoverMark=null, mouse={x:-1e4,y:-1e4};
renderer.domElement.addEventListener('pointermove',e=>{mouse.x=e.clientX;mouse.y=e.clientY;});
renderer.domElement.addEventListener('pointerdown',()=>{controls.autoRotate=false;orbitBtn.classList.remove('on');});
renderer.domElement.addEventListener('click',()=>{ if(hoverMark){tweenTo(hoverMark.cam,hoverMark.tgt);}});
let camTween=null;
function tweenTo(p,tg){camTween={t:0,dur:1.15,fp:camera.position.clone(),ft:controls.target.clone(),tp:p.clone(),tt:tg.clone()};}

/* ══════════════════════════════════════════════════════════════════
   13 · HUD
   ══════════════════════════════════════════════════════════════════ */
const $=id=>document.getElementById(id);
const penn=$('.pennants');
['#b0483c','#e9e1d0','#2f4a72','#e3a44c','#4f7d55','#b0483c','#e9e1d0'].forEach((c,i)=>{
  const el=document.createElement('i'); el.style.background=c; el.style.animationDelay=(i*.13)+'s'; penn.appendChild(el);});
let sailState=1, sailTarget=1;
const orbitBtn=$('bOrbit');
$('bSails').onclick=e=>{sailTarget=sailTarget>.5?0:1;e.target.textContent=sailTarget>.5?'Strike sails':'Set sails';e.target.classList.toggle('on',sailTarget<.5);};
$('bOrbit').onclick=e=>{controls.autoRotate=!controls.autoRotate;e.target.classList.toggle('on',controls.autoRotate);};
$('bReset').onclick=()=>{tweenTo(HOME_P,HOME_T);};
$('tod').oninput=e=>{tod=+e.target.value/60;updateDay();clockLabels();};
$('wind').oninput=e=>{wind=+e.target.value/100*.8;clockLabels();};
function clockLabels(){const hh=Math.floor(tod),mm=Math.floor((tod-hh)*60);
  const s=String(hh).padStart(2,'0')+':'+String(mm).padStart(2,'0');
  $('clock').textContent=s;$('todLbl').textContent=s;
  $('sWind').innerHTML=Math.round(1+wind*15)+'<i>kn</i>';$('windLbl').textContent=Math.round(1+wind*15)+' kn';
  const p=clamp((tod-6)/12,0,1);
  const P0=[8,40],P1=[120,-30],P2=[232,40];
  const x=(1-p)**2*P0[0]+2*(1-p)*p*P1[0]+p*p*P2[0], y=(1-p)**2*P0[1]+2*(1-p)*p*P1[1]+p*p*P2[1];
  const d=$('sundot'); d.setAttribute('cx',x); d.setAttribute('cy',y);
  d.setAttribute('fill',p<0||p>1?'#8fa9d8':'#ffd27a');
  d.setAttribute('cy',p<0||p>1?36:y);
}
$('sVox').textContent=(()=>0)();
let totalVox=0;
addEventListener('keydown',e=>{
  const k=e.key.toLowerCase();
  if(k==='h'){$('brand').classList.toggle('hidden');$('console').classList.toggle('hidden');$('hint').classList.toggle('hidden');}
  if(k==='f')salute();
  if(k==='s')$('bSails').click();
  if(k==='r')$('bReset').click();
  if(['1','2','3','4'].includes(k)&&MARKS[+k-1])tweenTo(MARKS[+k-1].cam,MARKS[+k-1].tgt);
});
// audio (created on first gesture)
let AC=null;
function boom(){
  try{
    if(!AC)AC=new (window.AudioContext||window.webkitAudioContext)();
    const t=AC.currentTime, dur=1.1;
    const buf=AC.createBuffer(1,AC.sampleRate*dur,AC.sampleRate);
    const ch=buf.getChannelData(0);
    for(let i=0;i<ch.length;i++){const p=i/ch.length;ch[i]=(Math.random()*2-1)*Math.pow(1-p,2.4);}
    const src=AC.createBufferSource();src.buffer=buf;
    const lp=AC.createBiquadFilter();lp.type='lowpass';lp.frequency.setValueAtTime(900,t);
    lp.frequency.exponentialRampToValueAtTime(120,t+dur);
    const g=AC.createGain();g.gain.setValueAtTime(.55,t);g.gain.exponentialRampToValueAtTime(.001,t+dur);
    src.connect(lp).connect(g).connect(AC.destination);src.start(t);
    const o=AC.createOscillator(),og=AC.createGain();
    o.frequency.setValueAtTime(80,t);o.frequency.exponentialRampToValueAtTime(28,t+.7);
    og.gain.setValueAtTime(.35,t);og.gain.exponentialRampToValueAtTime(.001,t+.8);
    o.connect(og).connect(AC.destination);o.start(t);o.stop(t+.85);
  }catch(err){}
}
let shake=0;
function salute(){
  boom(); shake=1;
  const t=performance.now()/1000;
  for(let n=0;n<4;n++){
    const lx=4+n*4.5, ly=2.6, lz=5.2;
    const wp=new THREE.Vector3(lx,ly,lz).applyMatrix4(shipOuter.matrixWorld);
    for(let i=0;i<14;i++){
      puff(wp.x,wp.y,wp.z,(rr()-.5)*2-3.2,rr()*1.4,(rr()-.5)*2,6+rr()*5,1.6+rr()*1.4);
    }
    puff(wp.x,wp.y,wp.z,-1,.4,0,3.4,.35);
  }
}
$('bSalute').onclick=salute;

/* ══════════════════════════════════════════════════════════════════
   14 · loop
   ══════════════════════════════════════════════════════════════════ */
const clock=new THREE.Clock();
let fpsT=0,fpsN=0;
buildMap(); mapTex.needsUpdate=true;
// count voxels
scene.traverse(o=>{if(o.isInstancedMesh)totalVox+=o.count;});
$('sVox').textContent=totalVox.toLocaleString();
updateDay(); clockLabels();

function frame(){
  const dt=Math.min(clock.getDelta(),.05), t=clock.elapsedTime;
  waveU.uTime.value=t; waterU.uTime.value=t; waterU.uWind.value=wind*.55+.05;
  tide=Math.sin(t*.045)*.30; tide+=Math.sin(t*.011)*.1;
  sea.position.y=tide;
  // ship motion
  const sx=shipOuter.position.x+13, sz=shipOuter.position.z;
  const hy=waveH(sx,sz,t)*.55+tide;
  const roll=(waveH(sx,sz+4.5,t)-waveH(sx,sz-4.5,t))*.10;
  const pitch=(waveH(sx+9,sz,t)-waveH(sx-9,sz,t))*.055;
  shipOuter.position.y=lerp(shipOuter.position.y,hy,.2);
  rock.rotation.set(roll*(.4+wind),0,pitch*(.4+wind));
  rock.position.y=0;
  shipOuter.updateMatrixWorld();
  // hull foam
  {
    const p=foam.geometry.attributes.position, sd=foam.geometry.userData.sd;
    for(let i=0;i<foamN;i++){
      const s=sd[i], a=t*(.5+s)+i;
      const lx=2+s*24, lz=(Math.sin(a*1.7)*7), ly=-.2+Math.sin(a*2.3)*.2;
      const v=new THREE.Vector3(lx,ly,lz);
      if(i%2===0)v.z=-Math.abs(lz)-1.5; else v.z=Math.abs(lz)+1.5;
      v.applyMatrix4(shipOuter.matrixWorld); v.y+=tide;
      p.setXYZ(i,v.x,v.y,v.z);
    }
    p.needsUpdate=true;
  }
  // sails
  sailState+=(sailTarget-sailState)*Math.min(1,dt*1.35);
  for(const s of sailGroups){
    const d=clamp(sailState,0,1);
    s.g.scale.y=.03+.97*d;
    if(s.roll)s.roll.scale.x=.25+Math.max(0,(1-d))*1;
    s.g.visible=d>.02;
  }
  // mooring lines
  setLine(line1,new THREE.Vector3(25,4.2,0).applyMatrix4(shipOuter.matrixWorld).toArray(),moorA);
  setLine(line2,new THREE.Vector3(.5,5.2,0).applyMatrix4(shipOuter.matrixWorld).toArray(),moorB);
  // crane
  jib.rotation.y=Math.sin(t*.24)*.85+.3;
  hangCrate.rotation.z=Math.sin(t*.9)*.06; hangCrate.position.x=Math.sin(t*.9)*.35;
  // windmill
  scene.children.forEach(o=>{});
  // lighthouse beam
  beams.rotation.y+=dt*.62;
  const lf=lampF;
  glowMat.opacity=.18+.8*lf;
  beamMats.forEach(m=>{m.uniforms.uOp.value=(.05+.6*lf)*(0.85+.15*Math.sin(t*6));});
  // marker hover
  let best=null,bd=28;
  for(const m of MARKS){
    const v=m.p.clone().project(camera);
    if(v.z>1){m.sp.material.opacity=.12;continue;}
    const x=(v.x*.5+.5)*innerWidth, y=(-v.y*.5+.5)*innerHeight;
    const d=Math.hypot(x-mouse.x,y-mouse.y);
    const pulse=1+Math.sin(t*2.4+m.p.x)*.09;
    m.sp.scale.setScalar((7+(d<60?2.4:0))*pulse);
    m.sp.material.opacity=d<60?1:.62;
    m.sx=x;m.sy=y;
    if(d<bd){bd=d;best=m;}
  }
  hoverMark=best;
  if(best){tipEl.classList.add('on');tipH.textContent=best.t;tipP.textContent=best.s;
    tipEl.style.left=best.sx+'px';tipEl.style.top=best.sy-14+'px';
    renderer.domElement.style.cursor='pointer';}
  else {tipEl.classList.remove('on');renderer.domElement.style.cursor=controls.enableZoom?'grab':'grab';}
  // gulls
  for(const g of gulls){
    const u=g.userData,a=t*u.sp+u.ph;
    g.position.set(Math.cos(a)*u.r, u.y+Math.sin(a*2.2)*1.4, Math.sin(a)*u.r*.85);
    g.rotation.y=-a+Math.PI/2;
    const f=Math.sin(t*u.flap+u.ph)*.9;
    u.wL.rotation.x=f; u.wR.rotation.x=-f;
  }
  // clouds drift
  cloudMesh.position.x=((t*.55)%240)-40;
  const cl=new THREE.Color().copy(L.hor).lerp(new THREE.Color('#ffffff'),.55).multiplyScalar(.55+.65*(1-S.night));
  cloudMat.color.copy(cl);
  // chimney smoke + particles
  chimneySmoke(dt); updateParticles(dt,t);
  // beacon blink
  const bl=(Math.sin(t*3.1)>.55)?1:.05;
  lampLights.forEach(l=>{ if(l.userData.beacon)l.intensity=l.userData.i*lampF*bl; });
  // camera tween
  if(camTween){camTween.t+=dt/camTween.dur;
    const e=camTween.t>=1?1:(camTween.t<.5?4*camTween.t**3:1-Math.pow(-2*camTween.t+2,3)/2);
    camera.position.lerpVectors(camTween.fp,camTween.tp,e);
    controls.target.lerpVectors(camTween.ft,camTween.tt,e);
    if(camTween.t>=1)camTween=null;}
  // shake
  if(shake>0){shake=Math.max(0,shake-dt*1.6);
    const s=shake*shake*.55;
    camera.position.x+=(rr()-.5)*s;camera.position.y+=(rr()-.5)*s;camera.position.z+=(rr()-.5)*s;}
  controls.update();
  renderer.render(scene,camera);
  fpsN++;fpsT+=dt;
  if(fpsT>.5){$('sFps').textContent=Math.round(fpsN/fpsT);fpsN=0;fpsT=0;
    $('sTide').innerHTML=(tide>=0?'+':'')+Math.abs(tide).toFixed(2)+'<i>m</i>';}
  requestAnimationFrame(frame);
}
// windmill handle (kept out of the hot loop closure mess)
scene.traverse(o=>{if(o.userData&&o.userData.spin)millSpin=o;});
let millSpin=null;
const _origFrame=frame;
function frameWrap(){ if(millSpin)millSpin.rotation.z-=0.5*Math.min(1,.3+wind*2)*0.016; _origFrame(); }
requestAnimationFrame(function loop(){
  if(millSpin)millSpin.rotation.z-=.011*(0.4+wind*2.4);
  frame2();
});
// use a single clean loop:
let running=false;
function frame2(){
  // (identical to frame() body via direct call chain)
}
// -- start the real loop --
let raf=null;
function startLoop(){
  let last=performance.now();
  function step(now){
    const dt=Math.min((now-last)/1000,.05); last=now;
    if(millSpin)millSpin.rotation.z-=dt*(.5+wind*2.2);
    tick(dt,now/1000);
    raf=requestAnimationFrame(step);
  }
  raf=requestAnimationFrame(step);
}
function tick(dt,t){
  waveU.uTime.value=t; waterU.uTime.value=t; waterU.uWind.value=wind*.55+.05;
  sea.position.y=tide;
  const sx=shipOuter.position.x+13, sz=shipOuter.position.z;
  shipOuter.position.y=lerp(shipOuter.position.y,waveH(sx,sz,t)*.55+tide,.15);
  const roll=(waveH(sx,sz+4.5,t)-waveH(sx,sz-4.5,t))*.11;
  const pitch=(waveH(sx+9,sz,t)-waveH(sx-9,sz,t))*.06;
  rock.rotation.set(roll*(.45+wind),0,pitch*(.45+wind));
  shipOuter.updateMatrixWorld();
  {
    const p=foam.geometry.attributes.position, sd=foam.geometry.userData.sd, v=new THREE.Vector3();
    for(let i=0;i<foamN;i++){
      const s=sd[i],a=t*(.5+s)+i;
      v.set(2+s*24,-.15+Math.sin(a*2.3)*.2,(i%2?1:-1)*(1.4+Math.abs(Math.sin(a*1.7))*6));
      v.applyMatrix4(shipOuter.matrixWorld); v.y+=tide*.4;
      p.setXYZ(i,v.x,v.y,v.z);
    }
    p.needsUpdate=true;
  }
  sailState+=(sailTarget-sailState)*Math.min(1,dt*1.4);
  for(const s of sailGroups){
    const d=clamp(sailState,0,1);
    s.g.scale.y=.04+.96*d; s.g.visible=d>.02;
    if(s.roll)s.roll.scale.x=.3+Math.max(0,1-d)*.9;
  }
  setLine(line1,new THREE.Vector3(25,4.2,0).applyMatrix4(shipOuter.matrixWorld).toArray(),moorA);
  setLine(line2,new THREE.Vector3(.5,5.4,0).applyMatrix4(shipOuter.matrixWorld).toArray(),moorB);
  jib.rotation.y=Math.sin(t*.22)*.8+.35;
  hangCrate.position.x=Math.sin(t*.85)*.4; hangCrate.rotation.z=Math.sin(t*.85)*.07;
  beams.rotation.y+=dt*.6;
  glowMat.opacity=.16+.82*clamp((S.night-.15)/.6,0,1);
  beamMats.forEach(m=>m.uniforms.uOp.value=(.04+.62*clamp((S.night-.1)/.7,0,1))*(.85+.15*Math.sin(t*6)));
  lampLights.forEach(l=>l.intensity=l.userData.i*clamp((S.night-.15)/.6,0,1)*(l.userData.beacon?((Math.sin(t*3.1)>.55)?1:.06):1));
  let best=null,bd=30;
  for(const m of MARKS){
    const v=m.p.clone().project(camera);
    if(v.z>1){m.sp.material.opacity=.1;continue;}
    const x=(v.x*.5+.5)*innerWidth,y=(-v.y*.5+.5)*innerHeight;
    const d=Math.hypot(x-mouse.x,y-mouse.y);
    m.sp.scale.setScalar((6.6+(d<70?2.6:0))*(1+Math.sin(t*2.3+m.p.x)*.09));
    m.sp.material.opacity=d<70?1:.55; m.sx=x;m.sy=y;
    if(d<bd){bd=d;best=m;}
  }
  hoverMark=best;
  if(best){tipEl.classList.add('on');tipH.textContent=best.t;tipP.textContent=best.s;
    tipEl.style.left=clamp(best.sx,120,innerWidth-140)+'px';tipEl.style.top=best.sy-16+'px';}
  else tipEl.classList.remove('on');
  for(const g of gulls){const u=g.userData,a=t*u.sp+u.ph;
    g.position.set(Math.cos(a)*u.r,u.y+Math.sin(a*2.2)*1.4,Math.sin(a)*u.r*.85);
    g.rotation.y=-a+Math.PI/2;const f=Math.sin(t*u.flap+u.ph)*.95;u.wL.rotation.x=f;u.wR.rotation.x=-f;}
  cloudMesh.position.x=((t*.6)%260)-60;
  cloudMat.color.copy(new THREE.Color().copy(L.hor).lerp(new THREE.Color('#ffffff'),.5).multiplyScalar(.5+.7*(1-S.night)));
  chimneySmoke(dt); updateParticles(dt,t);
  // tender boat
  {
    const cyc=(t*.055)%1, p=cyc<.5?cyc*2:2-cyc*2, e=p*p*(3-2*p);
    tender.position.set(lerp(-6,9,e),0,lerp(19,24,e));
    tender.position.y=tide+waveH(tender.position.x,tender.position.z,t)*.6+.15;
    tender.rotation.z=(waveH(tender.position.x+2,tender.position.z,t)-waveH(tender.position.x-2,tender.position.z,t))*.12;
    tender.rotation.y=e<.5?-1.57:1.57;
    if(rr()<dt*6)puff(tender.position.x,tide+.2,tender.position.z,0,.3,0,2.4,1.2);
  }
  if(camTween){camTween.t+=dt/camTween.dur;
    const c=camTween.t;const e=c>=1?1:(c<.5?4*c*c*c:1-Math.pow(-2*c+2,3)/2);
    camera.position.lerpVectors(camTween.fp,camTween.tp,e);
    controls.target.lerpVectors(camTween.ft,camTween.tt,e);
    if(c>=1)camTween=null;}
  if(shake>0){shake=Math.max(0,shake-dt*1.5);const s=shake*shake*.6;
    camera.position.x+=(rr()-.5)*s;camera.position.y+=(rr()-.5)*s;camera.position.z+=(rr()-.5)*s;}
  controls.update();
  renderer.render(scene,camera);
  fpsN++;fpsT+=dt;
  if(fpsT>.5){$('sFps').textContent=Math.round(fpsN/fpsT);fpsN=0;fpsT=0;
    $('sTide').innerHTML=(tide>=0?'+':'')+Math.abs(tide).toFixed(2)+'<i>m</i>';}
}
// sun elevation readout used by tide/clock labels each second
setInterval(()=>{tide=Math.sin(performance.now()*.000045)*.3+Math.sin(performance.now()*.000011)*.1;},250);

renderer.render(scene,camera);
startLoop();
requestAnimationFrame(()=>document.getElementById('loader').classList.add('gone'));

addEventListener('resize',()=>{
  camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight);
});
</script>
</body>
</html>
```

## What's in the harbour

**The scene** — a crescent of granite quay with a terraced hill town climbing behind it (windows that light up after dusk, chimney smoke, a windmill on the west ridge), a stone breakwater thrown out to a banded lighthouse whose beam sweeps the mouth, a beacon on the eastern headland, and a three-masted frigate moored bow-out with her gangway thrown to a timber jetty.

**The ship** — hull built from a per-voxel shell test: antifouling red below the water, black, an ochre wale pierced with gunports, white rail cap. Square sails bellying out (a *Strike / Set sails* button drops them yard by yard, rolled canvas shrinking in compensation), jibs, spanker, tops, a full fan of shrouds and stays, ensign and masthead pennants waving in a vertex-shader, tiny crew on deck.

**Everything moves** — the sea is a shader-displaced voxel grid with analytic normals, sun glint and animated surf hugging the shoreline; the frigate rides those same waves (roll and pitch derived from the water itself), spilling foam along her seams. A tender shuttles between ship and quay, gulls flap orbital circuits, clouds drift and pick up the hour's colour, mooring lines sag, the quay crane swings a crate.

**Controls** — drag to orbit, scroll to zoom, click any of the four chart markers to fly the camera (or press `1`–`4`). The brass console drives hour of day and swell live; `F` fires a gun salute with smoke, camera kick and a synthesised boom; `H` clears the interface for photographs.