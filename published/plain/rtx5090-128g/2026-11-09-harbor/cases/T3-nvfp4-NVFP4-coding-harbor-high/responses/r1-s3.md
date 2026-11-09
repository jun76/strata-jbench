Below is a complete, single-file voxel harbor: a three‑masted barque moored alongside the quay, a rock‑cut mole with a turning lighthouse, a custom house with a working cargo davit, a fish market, hillside cottages, a post mill, gulls, gulls, mooring lines, and a shader‑driven voxel sea the ship actually rides. Everything is instanced voxels, so it renders on load.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Graywater Haven — a sailing ship calling at a harbor</title>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Alfa+Slab+One&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&display=swap" rel="stylesheet" />
<style>
  :root{
    --ink:#07131c;
    --ink-2:#0d2130;
    --ink-3:#13303f;
    --paper:#f1e6cf;
    --paper-dim:#c3bda9;
    --brass:#e3a83c;
    --red:#d64530;
    --foam:#8fd2d8;
    --edge:rgba(227,168,60,.34);
    --shadow:0 18px 40px rgba(0,0,0,.55), 0 2px 0 rgba(255,255,255,.06) inset;
    --display:"Alfa Slab One","Rockwell",Georgia,serif;
    --sans:"IBM Plex Sans",system-ui,-apple-system,sans-serif;
    --mono:"IBM Plex Mono",ui-monospace,Menlo,Consolas,monospace;
  }
  *{box-sizing:border-box}
  html,body{height:100%;margin:0;background:#061019;overflow:hidden;
    font-family:var(--sans);color:var(--paper);
    -webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
  canvas#scene{position:fixed;inset:0;display:block;z-index:0;cursor:grab}
  canvas#scene:active{cursor:grabbing}

  /* ---------- ambience overlays ---------- */
  #vig{position:fixed;inset:0;z-index:2;pointer-events:none;
    background:radial-gradient(120% 90% at 50% 45%,rgba(0,0,0,0) 42%,rgba(2,10,16,.55) 100%);}
  #grain{position:fixed;inset:0;z-index:3;pointer-events:none;opacity:.055;mix-blend-mode:overlay;
    background-image:repeating-linear-gradient(0deg,rgba(255,255,255,.9) 0 1px,rgba(0,0,0,.6) 1px 2px);
    background-size:auto 3px}

  .hud{position:fixed;z-index:6}
  .panel{background:linear-gradient(180deg,rgba(13,33,48,.94),rgba(7,19,28,.94));
    border:1px solid var(--edge);box-shadow:var(--shadow);position:relative}
  .panel:before{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--brass)}
  .eyebrow{font-family:var(--mono);font-size:9.5px;letter-spacing:.24em;text-transform:uppercase;
    color:var(--brass);opacity:.95}
  .mono{font-family:var(--mono)}

  /* ---------- plaque ---------- */
  #plaque{top:20px;left:22px;max-width:min(46vw,540px);padding:16px 20px 14px;
    animation:rise .85s cubic-bezier(.2,.85,.25,1) both .1s}
  #plaque h1{font-family:var(--display);font-weight:400;margin:.18em 0 .05em;
    font-size:clamp(28px,4.6vw,52px);line-height:.92;letter-spacing:-.015em;
    text-shadow:0 3px 0 rgba(0,0,0,.35),0 0 26px rgba(227,168,60,.16)}
  #plaque h1 span{color:var(--brass)}
  #plaque .sub{font-size:14px;font-style:italic;color:var(--foam);margin:2px 0 10px;letter-spacing:.01em}
  .rule{height:1px;background:linear-gradient(90deg,var(--brass),rgba(227,168,60,0));margin:8px 0 9px;position:relative}
  .rule:after{content:"◆";position:absolute;left:0;top:-8px;color:var(--brass);font-size:9px}
  .stats{display:flex;flex-wrap:wrap;gap:14px}
  .stats div{font-family:var(--mono);font-size:10px;letter-spacing:.12em;color:var(--paper-dim);text-transform:uppercase}
  .stats b{display:block;font-family:var(--display);font-size:17px;letter-spacing:0;color:var(--paper);
    text-transform:none;margin-top:2px}
  #tidebar{height:4px;background:rgba(255,255,255,.09);margin-top:11px;overflow:hidden}
  #tidebar i{display:block;height:100%;width:46%;background:linear-gradient(90deg,var(--foam),var(--brass));
    animation:tide 9s ease-in-out infinite alternate}

  /* ---------- control panel ---------- */
  #panel{top:20px;right:22px;width:284px;padding:14px 16px 16px;
    animation:rise .85s cubic-bezier(.2,.85,.25,1) both .26s}
  .sec{margin-top:14px}
  .sec:first-of-type{margin-top:6px}
  .sec>h3{font-family:var(--mono);font-size:9.5px;letter-spacing:.24em;text-transform:uppercase;
    color:var(--brass);margin:0 0 8px;display:flex;align-items:center;gap:7px;font-weight:500}
  .sec>h3 i{width:6px;height:6px;background:var(--brass);display:block;transition:transform .25s}
  .sec>h3:hover i{transform:scale(1.7) rotate(45deg)}
  .seg{display:grid;grid-template-columns:1fr 1fr;gap:5px}
  .seg button{font-family:var(--mono);font-size:10px;letter-spacing:.14em;text-transform:uppercase;
    padding:8px 6px;background:rgba(255,255,255,.045);border:1px solid rgba(255,255,255,.10);
    color:var(--paper-dim);cursor:pointer;transition:.22s;text-align:left}
  .seg button:hover{background:rgba(227,168,60,.16);color:var(--paper);transform:translateY(-1px)}
  .seg button.on{background:var(--brass);border-color:var(--brass);color:#0a1720;font-weight:600}
  .row{display:flex;justify-content:space-between;align-items:baseline;
    font-family:var(--mono);font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--paper-dim);margin:12px 0 5px}
  .row em{font-style:normal;color:var(--foam);font-size:11px;letter-spacing:.06em}
  input[type=range]{-webkit-appearance:none;appearance:none;width:100%;height:16px;background:transparent;cursor:pointer}
  input[type=range]::-webkit-slider-runnable-track{height:3px;background:rgba(255,255,255,.16)}
  input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:13px;height:13px;margin-top:-5px;
    background:var(--brass);border:2px solid #0a1720;box-shadow:0 0 0 1px var(--brass);transition:.2s}
  input[type=range]::-webkit-slider-thumb:hover{transform:scale(1.25);box-shadow:0 0 12px rgba(227,168,60,.8)}
  input[type=range]::-moz-range-track{height:3px;background:rgba(255,255,255,.16)}
  input[type=range]::-moz-range-thumb{width:12px;height:12px;border:2px solid #0a1720;background:var(--brass)}
  .sw{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:6px 0;cursor:pointer;
    font-family:var(--mono);font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--paper-dim);transition:color .2s}
  .sw:hover{color:var(--paper)}
  .sw i{width:30px;height:14px;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.16);
    position:relative;flex:0 0 auto;transition:.25s}
  .sw i:after{content:"";position:absolute;top:1px;left:1px;width:10px;height:10px;background:var(--paper-dim);transition:.25s cubic-bezier(.3,1.4,.4,1)}
  .sw.on i{background:rgba(227,168,60,.35);border-color:var(--brass)}
  .sw.on i:after{left:17px;background:var(--brass)}
  #reset{margin-top:14px;width:100%;padding:10px;background:transparent;border:1px solid var(--edge);
    color:var(--paper);font-family:var(--mono);font-size:10px;letter-spacing:.22em;text-transform:uppercase;
    cursor:pointer;transition:.25s}
  #reset:hover{background:var(--red);border-color:var(--red);color:#fff;letter-spacing:.3em}
  #collapse{position:absolute;top:12px;right:12px;width:20px;height:20px;line-height:16px;text-align:center;
    background:rgba(255,255,255,.06);border:1px solid var(--edge);color:var(--brass);cursor:pointer;
    font-family:var(--mono);font-size:12px;padding:0}
  #panel.min .sec,#panel.min #readout{display:none}
  #panel.min{width:150px}

  #readout{margin-top:14px;padding:9px 10px;background:rgba(0,0,0,.35);border-left:2px solid var(--foam);
    font-size:11.5px;line-height:1.5;color:#dfe7e6}
  #readout b{font-family:var(--display);font-weight:400;font-size:13px;color:var(--brass);display:block;margin-bottom:3px;letter-spacing:.02em}

  /* ---------- index (hotspots) ---------- */
  #index{left:22px;bottom:52px;width:min(35vw,330px);padding:12px 14px 8px;
    animation:rise .85s cubic-bezier(.2,.85,.25,1) both .4s}
  #index h3{font-family:var(--mono);font-size:9.5px;letter-spacing:.24em;text-transform:uppercase;color:var(--brass);margin:0 0 8px;font-weight:500}
  #index ol{list-style:none;margin:0;padding:0}
  #index li{border-top:1px solid rgba(255,255,255,.08)}
  #index button{display:flex;width:100%;gap:9px;align-items:baseline;background:none;border:0;padding:7px 2px;
    cursor:pointer;color:var(--paper-dim);text-align:left;transition:.2s}
  #index button span.n{font-family:var(--mono);font-size:9px;color:var(--brass);opacity:.75}
  #index button span.t{font-family:var(--display);font-size:13.5px;letter-spacing:.01em;line-height:1}
  #index button span.d{font-family:var(--mono);font-size:9px;letter-spacing:.1em;opacity:.55;margin-left:auto;text-transform:uppercase}
  #index button:hover,#index button.on{color:var(--brass);transform:translateX(4px)}
  #index button.on span.d{opacity:1}

  /* ---------- tech ---------- */
  #tech{right:22px;bottom:52px;text-align:right;font-family:var(--mono);font-size:9.5px;
    letter-spacing:.14em;text-transform:uppercase;color:rgba(241,230,207,.5);line-height:1.9;
    animation:rise .85s cubic-bezier(.2,.85,.25,1) both .5s;text-shadow:0 1px 6px rgba(0,0,0,.7)}
  #tech b{color:var(--foam);font-weight:500}

  /* ---------- ticker ---------- */
  #ticker{left:0;right:0;bottom:0;height:30px;display:flex;align-items:center;overflow:hidden;
    background:linear-gradient(180deg,rgba(7,19,28,.35),rgba(4,12,18,.92));
    border-top:1px solid var(--edge);z-index:7}
  #ticker .tape{display:flex;white-space:nowrap;animation:tape 74s linear infinite;
    font-family:var(--mono);font-size:10px;letter-spacing:.2em;color:rgba(241,230,207,.62);text-transform:uppercase}
  #ticker .tape em{color:var(--brass);font-style:normal;margin:0 16px}
  #ticker .tape>div{padding-right:60px}

  /* ---------- hotspot markers ---------- */
  #markers{position:fixed;inset:0;z-index:5;pointer-events:none}
  .hot{position:absolute;transform:translate(-50%,-50%);pointer-events:auto;background:none;border:0;
    cursor:pointer;padding:0;display:flex;align-items:center;gap:0;transition:opacity .3s}
  .hot .dot{width:9px;height:9px;background:var(--paper);border:2px solid #06111a;border-radius:50%;
    position:relative;flex:0 0 auto;transition:.25s}
  .hot .dot:before{content:"";position:absolute;inset:-7px;border:1px solid rgba(241,230,207,.55);border-radius:50%;
    animation:pulse 2.6s ease-out infinite}
  .hot .lab{display:flex;flex-direction:column;gap:1px;padding:5px 9px;margin-left:0;
    background:rgba(6,17,26,.86);border-left:2px solid var(--brass);max-width:0;overflow:hidden;opacity:0;
    white-space:nowrap;transition:.32s cubic-bezier(.2,.85,.25,1)}
  .hot .lab b{font-family:var(--display);font-weight:400;font-size:12px;letter-spacing:.02em;color:var(--paper)}
  .hot .lab em{font-family:var(--mono);font-style:normal;font-size:8.5px;letter-spacing:.16em;color:var(--foam);text-transform:uppercase}
  .hot:hover .lab,.hot.on .lab{max-width:260px;opacity:1;margin-left:8px}
  .hot:hover .dot,.hot.on .dot{background:var(--brass);transform:scale(1.35)}
  #markers.hide{opacity:0;pointer-events:none}

  /* ---------- boot ---------- */
  #boot{position:fixed;inset:0;z-index:20;background:#061019;display:grid;place-content:center;gap:16px;
    justify-items:center;transition:opacity .7s ease}
  #boot.gone{opacity:0;pointer-events:none}
  #boot .t{font-family:var(--display);font-size:clamp(26px,5vw,58px);color:var(--paper);letter-spacing:-.01em}
  #boot .b{width:min(340px,62vw);height:2px;background:rgba(255,255,255,.12);overflow:hidden}
  #boot .b i{display:block;height:100%;width:20%;background:var(--brass);animation:load 1.1s ease-in-out infinite}
  #boot .s{font-family:var(--mono);font-size:10px;letter-spacing:.3em;color:var(--brass);text-transform:uppercase}

  @keyframes rise{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
  @keyframes pulse{0%{transform:scale(.6);opacity:.9}70%{transform:scale(1.5);opacity:0}100%{opacity:0}}
  @keyframes tide{from{width:24%}to{width:78%}}
  @keyframes tape{from{transform:translateX(0)}to{transform:translateX(-50%)}}
  @keyframes load{0%{transform:translateX(-100%)}100%{transform:translateX(520%)}}

  @media (max-width:900px){
    #index{display:none}
    #plaque{max-width:70vw;padding:12px 14px}
    #panel{width:242px}
    #tech{bottom:44px;font-size:8.5px}
  }
  @media (prefers-reduced-motion:reduce){*{animation-duration:.001s!important;animation-iteration-count:1!important}}
</style>
</head>
<body>
<canvas id="scene"></canvas>
<div id="vig"></div><div id="grain"></div>
<div id="markers"></div>

<header class="hud" id="plaque">
  <div class="eyebrow">Harbor Authority · Signal Station VII · voxel survey</div>
  <h1>GRAYWATER<br><span>HAVEN</span></h1>
  <div class="sub">a sailing ship calling at a harbor</div>
  <div class="rule"></div>
  <div class="stats">
    <div>Wind<b id="s-wind">SW 11</b></div>
    <div>Tide<b id="s-tide">+2.4</b></div>
    <div>Swell<b id="s-swell">0.5m</b></div>
    <div>Voxels<b id="s-vox">—</b></div>
  </div>
  <div id="tidebar"><i></i></div>
</header>

<section class="hud panel" id="panel">
  <button id="collapse" title="collapse">–</button>
  <div class="eyebrow">Watch board</div>
  <div class="sec"><h3><i></i>Hour</h3>
    <div class="seg" id="watch">
      <button data-w="0">Grey dawn</button><button data-w="1" class="on">Golden ev.</button>
      <button data-w="2">High noon</button><button data-w="3">Night lamps</button>
    </div>
  </div>
  <div class="sec"><h3><i></i>Sea &amp; canvas</h3>
    <div class="row"><span>Sea state</span><em id="v-sea">moderate</em></div>
    <input id="sea" type="range" min="0" max="1.7" step="0.02" value="0.95" />
    <div class="row"><span>Canvas set</span><em id="v-sail">three-quarters</em></div>
    <input id="sail" type="range" min="0" max="1" step="0.01" value="0.72" />
  </div>
  <div class="sec"><h3><i></i>View</h3>
    <div class="sw on" data-t="orbit"><span>Auto-orbit</span><i></i></div>
    <div class="sw on" data-t="marks"><span>Chart labels</span><i></i></div>
    <div class="sw on" data-t="birds"><span>Seabirds</span><i></i></div>
    <div class="sw on" data-t="crew"><span>Hands &amp; dockers</span><i></i></div>
  </div>
  <button id="reset">Return to anchorage</button>
  <div id="readout"><b>From the harbor book</b>Select a marked point on the chart — or drag to orbit, scroll to close the distance.</div>
</section>

<aside class="hud" id="index">
  <h3>Points of call</h3>
  <ol id="idx"></ol>
</aside>

<div class="hud" id="tech">
  <div><b id="t-fps">60</b> fps · <b id="t-tri">0</b> tris</div>
  <div>drag orbit · scroll zoom · keys 1–4 · space auto</div>
</div>

<footer id="ticker"><div class="tape" id="tape"></div></footer>

<div id="boot"><div class="s">Sounding the channel</div><div class="t">GRAYWATER HAVEN</div><div class="b"><i></i></div></div>

<script type="importmap">
{"imports":{
  "three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
  "three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
}}
</script>
<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* ══════════════════════════ helpers ══════════════════════════ */
const clamp=(v,a,b)=>v<a?a:v>b?b:v;
const sstep=(a,b,x)=>{const t=clamp((x-a)/((b-a)||1e-6),0,1);return t*t*(3-2*t);};
const lerp=(a,b,t)=>a+(b-a)*t;
let _seed=987654321;
const rnd=()=>{_seed|0;_seed=(_seed+0x6D2B79F5)|0;let t=Math.imul(_seed^_seed>>>15,1|_seed);
  t=(t+Math.imul(t^t>>>7,61|t))^t;return((t^t>>>14)>>>0)/4294967296;};
const rr=(a,b)=>a+rnd()*(b-a);
const pick=a=>a[(rnd()*a.length)|0];
const smoothDamp=(cur,tgt,k,dt)=>cur+(tgt-cur)*(1-Math.exp(-k*dt));

/* ══════════════════════════ palette ══════════════════════════ */
const P={
  stone:'#8e8577',stoneD:'#6b6458',stoneL:'#a9a08c',granite:'#7c7971',coping:'#b4ab97',
  wood:'#8b5b34',woodD:'#6a4425',woodL:'#a5734c',deck:'#ba8b55',deckD:'#93683c',deckL:'#cea06a',
  slate:'#43505c',slateD:'#323d47',slateL:'#5b6976',
  brick:'#8d4634',brickD:'#6e3628',brickL:'#a25742',
  plaster:'#e3d8c1',plasterW:'#f2eadb',plasterP:'#d8c6b2',plasterG:'#c2cabd',plasterB:'#b5c2c9',
  hullBlack:'#242c33',hullDk:'#191f25',gold:'#c8992f',band:'#e9e2d1',antifoul:'#7c3a2b',
  canvas:'#efe4ca',canvasD:'#dbcca9',canvasS:'#c0473a',
  rig:'#6d5940',rigL:'#8d7657',
  grass:'#4d7a44',grassD:'#3c6337',rock:'#7a7268',sand:'#ccb589',drygrass:'#93935d',
  iron:'#2f363b',copper:'#8f6b3f',red:'#b23a2c',redL:'#cf4f38',blue:'#2b5c87',green:'#2f6b4f',
  yellow:'#ddaf3d',white:'#efeade',skin:'#dba87a',tar:'#20262a',
  sailRed:'#a63b2c',sailBlue:'#2f5578',
  pine:'#2f5641',pineD:'#254636',trunk:'#5a3f28',
  roofRed:'#a2543f',roofBlue:'#3f5f7a',wallCream:'#ecdcc0',wallPink:'#dcbfb0',wallBlue:'#a8b8c2',
  chaff:'#c8b98d',net:'#5f6b52',fish:'#9fb2bd',straw:'#cfae67'
};

/* ══════════════════════════ renderer / scene ══════════════════════════ */
const canvas=document.getElementById('scene');
const renderer=new THREE.WebGLRenderer({canvas,antialias:true,powerPreference:'high-performance'});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.setSize(innerWidth,innerHeight);
renderer.shadowMap.enabled=true;
renderer.shadowMap.type=THREE.PCFSoftShadowMap;

const scene=new THREE.Scene();
scene.fog=new THREE.Fog(0xb5c3cf,72,320);
const camera=new THREE.PerspectiveCamera(42,innerWidth/innerHeight,0.5,900);
const DEF_POS=new THREE.Vector3(-32,20.5,44), DEF_TGT=new THREE.Vector3(4,8,2);
camera.position.set(-70,48,84);

const controls=new OrbitControls(camera,renderer.domElement);
controls.enableDamping=true;controls.dampingFactor=.06;
controls.minDistance=14;controls.maxDistance=165;
controls.minPolarAngle=.12;controls.maxPolarAngle=1.48;
controls.autoRotateSpeed=.26;controls.target.copy(DEF_TGT);controls.enabled=false;

/* lights */
const hemi=new THREE.HemisphereLight(0x93b0cf,0x4a4d3f,.85);scene.add(hemi);
const amb=new THREE.AmbientLight(0xffffff,.22);scene.add(amb);
const sun=new THREE.DirectionalLight(0xffe3b4,2.1);
sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);
const sc=sun.shadow.camera;sc.left=-92;sc.right=92;sc.top=92;sc.bottom=-92;sc.near=1;sc.far=340;
sun.shadow.bias=-.0007;sun.shadow.normalBias=.06;scene.add(sun);
const lamp=new THREE.PointLight(0xffcb77,.0,70,2);scene.add(lamp);

/* ══════════════════════════ sky ══════════════════════════ */
const skyU={
  uTop:{value:new THREE.Color('#2f6fa4')},uMid:{value:new THREE.Color('#a9c4d5')},
  uBot:{value:new THREE.Color('#f0d0a2')},uSunDir:{value:new THREE.Vector3(.5,.4,.6)},
  uSunCol:{value:new THREE.Color('#ffdca8')},uGlow:{value:1}
};
const sky=new THREE.Mesh(new THREE.SphereGeometry(420,26,18),new THREE.ShaderMaterial({
  uniforms:skyU,side:THREE.BackSide,depthWrite:false,fog:false,
  vertexShader:`varying vec3 vD;void main(){vD=normalize(position);gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,
  fragmentShader:`
    uniform vec3 uTop,uMid,uBot,uSunCol;uniform vec3 uSunDir;uniform float uGlow;varying vec3 vD;
    void main(){
      float y=vD.y;
      vec3 c=mix(uBot,uMid,smoothstep(-0.02,0.24,y));
      c=mix(c,uTop,smoothstep(0.17,0.80,y));
      float s=max(dot(normalize(vD),normalize(uSunDir)),0.0);
      c+=uSunCol*pow(s,220.0)*1.35*uGlow;
      c+=uSunCol*pow(s,20.0)*0.30*uGlow;
      c+=uSunCol*pow(s,3.5)*0.10*uGlow;
      gl_FragColor=vec4(c,1.0);
      #include <tonemapping_fragment>
      #include <colorspace_fragment>
    }`
}));
scene.add(sky);

/* ══════════════════════════ sea ══════════════════════════ */
const uTime={value:0},uAmp={value:.95};
const uDeep={value:new THREE.Color('#0f3350')},uShal={value:new THREE.Color('#4a97a8')};
function waveH(x,z,t){
  let h=Math.sin(x*.24+t*.90)*.34 + Math.sin(z*.31-t*.70)*.26
      + Math.sin((x+z)*.13+t*.55)*.40 + Math.sin((x-z)*.47+t*1.60)*.10;
  return h*.42*uAmp.value;
}
const seaMat=new THREE.MeshLambertMaterial({color:0xffffff});
seaMat.onBeforeCompile=sh=>{
  sh.uniforms.uTime=uTime;sh.uniforms.uAmp=uAmp;sh.uniforms.uDeep=uDeep;sh.uniforms.uShal=uShal;
  sh.vertexShader=`uniform float uTime;varying float vW;
    float wv(vec2 p,float t){
      float h=sin(p.x*0.24+t*0.90)*0.34;
      h+=sin(p.y*0.31-t*0.70)*0.26;
      h+=sin((p.x+p.y)*0.13+t*0.55)*0.40;
      h+=sin((p.x-p.y)*0.47+t*1.60)*0.10;
      return h*0.42;
    }`+sh.vertexShader;
  sh.vertexShader=sh.vertexShader.replace('#include <begin_vertex>',`#include <begin_vertex>
    #ifdef USE_INSTANCING
      vec3 ip=vec3(instanceMatrix[3][0],instanceMatrix[3][1],instanceMatrix[3][2]);
    #else
      vec3 ip=vec3(0.0);
    #endif
    float wh=wv(ip.xz,uTime)*uAmp;
    transformed.y+=wh;
    vW=wh/max(0.001,uAmp);`);
  sh.fragmentShader='uniform vec3 uDeep,uShal;varying float vW;'+sh.fragmentShader;
  sh.fragmentShader=sh.fragmentShader.replace('#include <color_fragment>',`#include <color_fragment>
    float f=clamp(vW*1.08*0.5+0.5,0.0,1.0);
    diffuseColor.rgb*=mix(uDeep,uShal,smoothstep(0.28,1.0,f))*1.55;
    diffuseColor.rgb+=vec3(0.30,0.34,0.30)*smoothstep(0.905,1.0,f);`);
};

/* ══════════════════════════ voxel builder ══════════════════════════ */
class VB{
  constructor(){this.items=[];}
  v(x,y,z,c,o={}){
    const col=new THREE.Color(c);
    const j=o.j===undefined?.05:o.j;
    if(j)col.offsetHSL(0,0,(rnd()*2-1)*j);
    this.items.push({x,y,z,c:col,sx:o.sx||1,sy:o.sy||1,sz:o.sz||1,q:o.q||null,anchorY:o.anchorY,buoy:o.buoy});
    return this;
  }
  box(x0,y0,z0,nx,ny,nz,c,o={}){
    for(let i=0;i<nx;i++)for(let k=0;k<ny;k++)for(let l=0;l<nz;l++){
      if(o.hollow&&i>0&&i<nx-1&&k>0&&k<ny-1&&l>0&&l<nz-1)continue;
      if(o.every&&!o.every(i,k,l))continue;
      this.v(x0+i,y0+k,z0+l,c,o);
    }
    return this;
  }
  build(mat,{cast=true,recv=true}={}){
    const n=this.items.length;
    const m=new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1),mat,Math.max(n,1));
    const mm=new THREE.Matrix4(),q=new THREE.Quaternion(),p=new THREE.Vector3(),s=new THREE.Vector3();
    this.items.forEach((it,i)=>{
      p.set(it.x,it.y,it.z);s.set(it.sx,it.sy,it.sz);
      mm.compose(p,it.q||q,s);
      m.setMatrixAt(i,mm);m.setColorAt(i,it.c);
    });
    m.instanceMatrix.needsUpdate=true;if(m.instanceColor)m.instanceColor.needsUpdate=true;
    m.castShadow=cast;m.receiveShadow=recv;m.frustumCulled=false;
    TOTAL+=n;return m;
  }
}
let TOTAL=0;
const matSolid=new THREE.MeshLambertMaterial({color:0xffffff});
const matWin=new THREE.MeshBasicMaterial({color:0xffffff,fog:true});
const matGlow=new THREE.MeshBasicMaterial({color:0xffe0a0,transparent:true,opacity:.16,
  blending:THREE.AdditiveBlending,depthWrite:false,side:THREE.DoubleSide,fog:false});
const matSmoke=new THREE.MeshLambertMaterial({color:0xffffff,transparent:true,opacity:.9});

const UP=new THREE.Vector3(0,1,0);
function seg(vb,a,b,th,c,o={}){
  const d=new THREE.Vector3().subVectors(b,a),len=d.length();
  if(len<.001)return vb;
  const mid=new THREE.Vector3().addVectors(a,b).multiplyScalar(.5);
  const q=new THREE.Quaternion().setFromUnitVectors(UP,d.clone().normalize());
  return vb.v(mid.x,mid.y,mid.z,c,Object.assign({sx:th,sy:len,sz:th,q},o));
}
const V=(x,y,z)=>new THREE.Vector3(x,y,z);
function inTri(p,a,b,c){
  const e1=new THREE.Vector3().subVectors(b,a),e2=new THREE.Vector3().subVectors(c,a),
        pv=new THREE.Vector3().subVectors(p,a),
        d11=e1.dot(e1),d12=e1.dot(e2),d22=e2.dot(e2),d1p=e1.dot(pv),d2p=e2.dot(pv),
        den=d11*d22-d12*d12;
  if(Math.abs(den)<1e-7)return false;
  const u=(d22*d1p-d12*d2p)/den,v=(d11*d2p-d12*d1p)/den;
  return u>=-.02&&v>=-.02&&(u+v)<=1.02;
}
function triFill(vb,a,b,c,col,axis){
  const ax=axis||('x');
  const x0=Math.floor(Math.min(a.x,b.x,c.x)),x1=Math.ceil(Math.max(a.x,b.x,c.x));
  const y0=Math.floor(Math.min(a.y,b.y,c.y)),y1=Math.ceil(Math.max(a.y,b.y,c.y));
  const z0=Math.floor(Math.min(a.z,b.z,c.z)),z1=Math.ceil(Math.max(a.z,b.z,c.z));
  const p=new THREE.Vector3();
  for(let x=x0;x<=x1;x++)for(let y=y0;y<=y1;y++)for(let z=z0;z<=z1;z++){
    p.set(x,y,z);
    if(inTri(p,a,b,c)){
      const o=ax==='x'?{sx:.3,sy:1,sz:1}:ax==='z'?{sx:1,sy:1,sz:.3}:{sx:1,sy:.3,sz:1};
      vb.v(x,y,z,col,{j:.045,...o});
    }
  }
}

/* ══════════════════════════ terrain function ══════════════════════════ */
function blob(x,z,cx,cz,rx,rz,top){
  const d=Math.hypot((x-cx)/rx,(z-cz)/rz);
  return top*(1-sstep(.28,1.04,d))-4;
}
function rawGround(x,z){
  let h=-7;
  if(x>=15&&z<=33){let t=3;if(x>=24)t=4;if(x>=34)t=5;h=Math.max(h,t);}
  if(z<=-17&&x>=-18){let t=3;if(z<=-25)t=4;if(z<=-33)t=5;h=Math.max(h,t);}
  h=Math.max(h,blob(x,z,-40,-4,30,29,18));
  h=Math.max(h,blob(x,z,-25,-29,17,13,11));
  h=Math.max(h,blob(x,z,-47,17,13,11,6));
  h=Math.max(h,blob(x,z,14,-46,32,13,13));
  h=Math.max(h,blob(x,z,44,-40,16,12,8));
  if(h>2)h+=Math.sin(x*.72)*Math.cos(z*.61)*.9+Math.sin(x*.19+z*.27)*.7;
  return h;
}
const isWater=(x,z)=>rawGround(x,z)<1;
const inDock=(x,z)=>((x>=15&&z<=33)||(z<=-17&&x>=-18));
const inBoardwalk=(x,z)=>(x>=15&&x<=17&&z<=33&&z>-17)||(z<=-17&&z>=-19&&x>=-18&&x<15);
function surfCol(x,y,z,top){
  if(y<top)return top<=2?P.sand:P.stoneD;
  if(top<=1.6)return pick([P.sand,P.sand,'#c0a87c']);
  if(inDock(x,z)){
    if(inBoardwalk(x,z))return pick([P.wood,P.woodD,P.woodL,P.wood]);
    return rnd()<.14?P.stoneL:pick([P.stone,P.stone,P.stoneD,P.stoneL]);
  }
  if(top>=12)return rnd()<.3?P.rock:pick([P.grassD,P.grass,P.drygrass]);
  if(top>=7)return rnd()<.22?P.rock:pick([P.grass,P.grassD,P.drygrass]);
  return pick([P.grass,P.grass,P.grassD,P.sand]);
}

/* ══════════════════════════ builders ══════════════════════════ */
const gLand=new VB(),gProps=new VB(),gBuild=new VB(),gSea=new VB(),gWin=new VB();

/* ---- sea ---- */
(function sea(){
  for(let x=-58;x<=58;x++)for(let z=-58;z<=58;z++){
    const far=Math.max(Math.abs(x),Math.abs(z));
    let s=1;
    if(far>36){if((x&1)||(z&1))continue;s=2;}
    else if(far>27){if((x&1)||(z&1))continue;s=2;}
    if(!isWater(x,z))continue;
    const d=Math.hypot(x-6,z-4);
    const deep=clamp((d-10)/44,0,1);
    const c=new THREE.Color('#8fb9c4').lerp(new THREE.Color('#5f7fa0'),deep);
    const near=rawGround(x+3,z)<6||rawGround(x-3,z)<6||rawGround(x,z+3)<6||rawGround(x,z-3)<6;
    if(near)c.lerp(new THREE.Color('#bcd8cd'),.35);
    gSea.items.push({x,y:0,z,c,sx:s,sy:1,sz:s,q:null});
  }
})();

/* ---- land + quay walls ---- */
(function land(){
  const nb=[[1,0],[-1,0],[0,1],[0,-1]];
  for(let x=-58;x<=58;x++)for(let z=-58;z<=58;z++){
    const top=Math.round(rawGround(x,z));
    if(top<1)continue;
    let edge=false;
    for(const[dx,dz]of nb)if(isWater(x+dx,z+dz))edge=true;
    for(let y=top;y>top-4;y--){
      let c=surfCol(x,y,z,top);
      if(edge&&y===top&&top>=2)c=inDock(x,z)?P.coping:pick([P.granite,P.rock,P.stoneL]);
      gLand.v(x,y,z,c,{j:y===top?.06:.10});
    }
    if(edge){for(let y=top-4;y>=-2;y--)gLand.v(x,y,z,y>1?pick([P.granite,P.stoneD]):P.stoneD,{j:.10});}
  }
  // stone steps down to the water at the fish market
  for(let i=0;i<6;i++)gLand.box(-4+i,3-i,-16,3,1,1,P.coping,{j:.06});
  // slipway on the west shore
  for(let i=0;i<7;i++)gLand.box(-19-i,3-i,10,3,1,1,P.stoneD,{j:.08});
})();

/* ---- breakwater / mole ---- */
(function mole(){
  const A=V(26,0,32),B=V(1,0,42);
  for(let s=0;s<=64;s++){
    const t=s/64,p=new THREE.Vector3().lerpVectors(A,B,t);
    p.x+=Math.sin(t*3.1)*1.6;
    const w=3.6+Math.sin(t*4.4)*1.1+(1-t)*.9;
    for(let dx=-w;dx<=w;dx+=1){
      const h=1+Math.round((1-Math.pow(Math.abs(dx)/w,1.6))*(2.6+Math.sin(t*7+dx)*0.5)+rnd()*1.1);
      for(let y=-1;y<=h;y++)
        gLand.v(Math.round(p.x+dx),y,Math.round(p.z),
          y>=h?pick([P.granite,P.rock,P.stoneL]):pick([P.stoneD,'#565059',P.granite]),{j:.12});
    }
  }
  gLand.box(-1,3,40,5,1,5,P.coping,{j:.05});   // lighthouse plinth
})();

/* ---- quay furniture ---- */
(function quay(){
  const post=(x,z,h,mat,c1,c2)=>{
    gProps.box(x,4,z,1,h,1,mat,{j:.05});
    if(c1)gProps.box(x-.15,4+h,z-.15,1.3,1.4,1.3,c1,{j:.03});
    if(c2)gProps.box(x,4+h+1.4,z,1,1.2,1,c2,{j:.05});
  };
  // bollards + lamps along the east quay and north quay
  for(let z=-14;z<=30;z+=7){
    gProps.box(16,4,z,2,1,2,P.iron,{j:.04});gProps.box(16.1,5,z+.1,1.6,1,1.6,P.gold,{j:.05});
    gProps.box(17,4,z+3.5,1,2,1,P.woodD,{j:.06});
  }
  for(let x=-8;x<=40;x+=12){
    gProps.box(x,4,-20,2,1,2,P.iron,{j:.04});gProps.box(x+.1,5,-19.9,1.6,1,1.6,P.gold,{j:.05});
  }
  const lampPost=(x,z)=>{
    gProps.box(x,4,z,1,5,1,P.iron,{j:.04});
    gProps.box(x-.5,9,z-.5,2,1,2,P.tar,{j:.03});
    gWin.v(x,9.6,z,'#ffd68a',{j:.02});
    gProps.box(x-.5,10.3,z-.5,2,.6,2,P.tar,{j:.03});
    gProps.box(x-1.2,8,z-1.2,3,.4,3,P.iron,{j:.04});
  };
  lampPost(19,-8);lampPost(19,10);lampPost(19,26);lampPost(2,-22);lampPost(-10,-22);lampPost(28,-22);
  // crates, barrels, sacks, nets
  for(let i=0;i<26;i++){
    const x=Math.round(rr(17,34)),z=Math.round(rr(-16,31));
    if(rawGround(x,z)<3||rawGround(x,z)>5)continue;
    const h=1+((rnd()*2)|0);
    if(rnd()<.55)gProps.box(x,4,z,2,h,2,pick([P.wood,P.woodD,P.brickL]),{j:.07});
    else if(rnd()<.6){gProps.box(x,4,z,2,2,2,P.straw,{j:.09});if(h>1)gProps.box(x+1,4,z-1,2,1,2,P.straw,{j:.09});}
    else{gProps.box(x,4,z,1,2,1,P.net,{j:.10});gProps.box(x+1,4,z,1,1,1,P.fish,{j:.10});}
  }
  for(let i=0;i<14;i++){
    const x=Math.round(rr(16,30)),z=Math.round(rr(-14,31));
    if(rawGround(x,z)!==3)continue;
    gProps.box(x,4,z,2,3,2,P.woodD,{j:.05});
    gProps.box(x,4,z,2.4,.4,2.4,'#4a3320',{j:.05});
    gProps.box(x,6,z,2.4,.4,2.4,'#4a3320',{j:.05});
    gProps.box(x+.4,7,z+.4,1.2,.5,1.2,P.woodL,{j:.05});
  }
  // fish market shed + stalls on the north quay
  gBuild.box(-12,4,-24,9,1,5,P.stoneD,{j:.05});
  for(let i=0;i<5;i++){gBuild.box(-12+i*2,5,-24,1,4,1,P.woodD,{j:.05});}
  gBuild.box(-12,5,-24,9,1,1,P.wood,{j:.05});gBuild.box(-12,9,-20,9,1,1,P.wood,{j:.05});
  for(let i=0;i<7;i++)gBuild.box(-13+i*2,9.6+i%2,-25+((i%2)?0:4),2,.7,1,i%2?P.red:P.white,{j:.05});
  gBuild.box(-12,9,-24,9,1,5,P.slateD,{j:.06});
  gBuild.box(-11,6,-23,7,2,1,P.woodD,{j:.06});
  for(let i=0;i<6;i++)gBuild.v(-10+i,8.2,-22.6,i%2?P.fish:P.net,{sx:1,sy:.8,sz:1,j:.1});
  // benches, signpost, anchor trophy, coiled ropes
  gProps.box(22,5,18,4,1,1,P.woodL,{j:.05});gProps.box(22,4,18,1,1,1,P.woodD,{j:.05});gProps.box(25,4,18,1,1,1,P.woodD,{j:.05});
  gProps.box(20,4,-4,1,6,1,P.woodD,{j:.05});
  gProps.box(18.9,8,-5,1,2,3,P.red,{j:.03});gProps.box(18.9,8,-5,1,1,1,P.white,{j:.03});
  gProps.box(23,4,-10,5,1,2,P.iron,{j:.05});gProps.box(24,5,-10,3,1,1,P.stoneL,{j:.05});
  for(let i=0;i<10;i++){
    const x=Math.round(rr(16,32)),z=Math.round(rr(-15,31));
    if(rawGround(x,z)!==3)continue;
    gProps.box(x-.3,4,z-.3,1.6,.4,1.6,P.rigL,{j:.05});gProps.box(x-.1,4.4,z-.1,1.2,.3,1.2,P.wood,{j:.05});
  }
})();

/* ---- buildings ---- */
const CHIM=12.5;
(function buildings(){
  /* custom house on the east quay */
  const bx=27,bz=5,w=11,d=10,base=4;
  gBuild.box(bx,base+1,bz,w,6,d,P.brick,{hollow:true,j:.06});
  for(let x=0;x<w;x++)for(let z=0;z<d;z++){
    const h=Math.max(0,Math.round((w/2)-Math.abs(x-(w-1)/2)));
    if(h>0){gBuild.box(bx+x,base+7,bz+z,1,h+1,1,P.slate,{j:.05});gBuild.v(bx+x,base+7+h,bz+z,pick([P.slateL,P.slateD]),{j:.05});}
  }
  gBuild.box(bx-1,base+7,bz-1,w+2,1,d+2,P.slateD,{j:.05});
  for(let z=0;z<d;z+=2){gBuild.v(bx-1,base+5,bz+z,'#f3e7c9',{sx:.4,sy:2,sz:1,j:.02});gWin.v(bx-1,base+5,bz+z,'#f7d municipal'.trim()||'#f6d38a',{sx:.4,sy:1.6,sz:.8});}
  gBuild.box(bx-1,base+1,bz+3,1,4,4,P.woodD,{j:.05});
  gBuild.box(bx+4,base+7,bz+1,2,5,2,P.brickD,{j:.05});gBuild.box(bx+3.8,base+11.8,bz+.8,2.4,1,2.4,'#4b3c38',{j:.06});
  for(let z=1;z<d;z+=2)gWin.v(bx+5.6,base+5,bz+z,'#f6d38a',{sx:.4,sy:1.6,sz:.8});
  gWin.v(bx+3,base+13,bz+4,'#f6d38a',{sx:1.2,sy:1.2,sz:1.2});   // clock face
  /* bonded warehouse */
  const wx=26,wz=-10,ww=8,wd=12;
  gBuild.box(wx,5,wz,ww,7,wd,P.plaster,{hollow:true,j:.05});
  for(let x=0;x<ww;x++){const h=Math.max(0,Math.round((ww/2)-Math.abs(x-(ww-1)/2)*1.15));
    if(h>0)gBuild.box(wx+x,12,wz,1,h,wd,P.slateD,{j:.05});}
  gBuild.box(wx-1,12,wz-1,ww+2,1,wd+2,P.slate,{j:.05});
  for(let z=1;z<wd;z+=2)gWin.v(wx-1,7.5,wz+z,'#f6d38a',{sx:.35,sy:2,sz:1}),gWin.v(wx-1,10,wz+z,'#f6d38a',{sx:.35,sy:1.4,sz:1});
  for(let z=2;z<wd;z+=4)gBuild.box(wx-1,5,wz+z,1,3,2,P.woodD,{j:.06});
  /* chandlery / dwellings on the north quay */
  const houses=[
    {x:-8,z:-31,w:7,d:6,h:4,wall:P.plasterW,roof:P.slateD},
    {x:2,z:-33,w:6,d:6,h:4,wall:P.plasterP,roof:P.roofRed},
    {x:12,z:-32,w:8,d:6,h:5,wall:P.brick,roof:P.slate},
    {x:-24,z:-25,w:6,d:6,h:4,wall:P.plasterG,roof:P.slateD}
  ];
  for(const H of houses){
    const b=Math.round(rawGround(H.x,H.z));
    gBuild.box(H.x,b+1,H.z,H.w,H.h,H.d,H.wall,{hollow:true,j:.05});
    for(let x=0;x<H.w;x++){const h=Math.max(0,Math.round((H.w/2)-Math.abs(x-(H.w-1)/2)));
      if(h>0)gBuild.box(H.x+x,b+1+H.h,H.z,1,h,H.d,H.roof,{j:.05});}
    gBuild.box(H.x-1,b+1+H.h,H.z-1,H.w+2,1,H.d+2,H.roof,{j:.05});
    for(let z=1;z<H.d;z+=2){gWin.v(H.x-1,b+3,H.z+z,'#f6d38a',{sx:.35,sy:1.4,sz:1});}
    gBuild.box(H.x+H.w-2,b+1,H.z+1,1,2,2,P.woodD,{j:.05});
    gBuild.box(H.x+1,b+H.h+2,H.z+1,1,3,1,P.brickD,{j:.06});
  }
})();

/* ---- hillside town, mill, chapel, fort, pines ---- */
(function hill(){
  const H=(x,z)=>Math.round(rawGround(x,z));
  const cottages=[
    {x:-32,z:-15,c:P.wallCream,r:P.roofRed},{x:-37,z:-9,c:P.plasterW,r:P.slateD},
    {x:-28,z:-20,c:P.wallPink,r:P.roofRed},{x:-42,z:-14,c:P.plasterW,r:P.roofBlue},
    {x:-36,z:-22,c:P.wallBlue,r:P.slate},{x:-44,z:-3,c:P.wallCream,r:P.slateD},
    {x:-25,z:-12,c:P.plasterP,r:P.roofRed},{x:-30,z:-30,c:P.plasterW,r:P.slateD}
  ];
  for(const c of cottages){
    const b=H(c.x,c.z);if(b<6)continue;
    const w=4+((rnd()*2)|0),d=4+((rnd()*2)|0);
    gBuild.box(c.x,b+1,c.z,w,3,d,c.c,{hollow:true,j:.05});
    for(let x=0;x<w;x++){const h=Math.max(0,Math.round((w/2)-Math.abs(x-(w-1)/2)));
      if(h>0)gBuild.box(c.x+x,b+4,c.z,1,h,d,c.r,{j:.06});}
    gBuild.box(c.x-1,b+4,c.z-1,w+2,1,d+2,c.r,{j:.05});
    gWin.v(c.x-1,b+2.4,c.z+1,'#f6d38a',{sx:.3,sy:1,sz:1});
    gWin.v(c.x-1,b+2.4,c.z+d-2,'#f6d38a',{sx:.3,sy:1,sz:1});
    gBuild.box(c.x+w-2,b+4,c.z+1,1,3,1,P.brickD,{j:.06});
    for(let i=0;i<4;i++)gBuild.v(c.x-2-i,b-i,c.z+2+((i*2)%3),pick([P.stone,P.stoneL]),{j:.08});
  }
  /* chapel with tower */
  {const cx=-38,cy=H(-38,-24);
   gBuild.box(cx,cy+1,-28,6,4,8,P.plasterW,{hollow:true,j:.04});
   for(let x=0;x<6;x++){const h=Math.max(0,Math.round(3-Math.abs(x-2.5)));if(h>0)gBuild.box(cx+x,cy+5,-28,1,h,8,P.slateD,{j:.05});}
   gBuild.box(cx+1,cy+5,-24,4,8,4,P.plasterW,{j:.04});
   gWin.v(cx+2.6,cy+9,-24.5,'#f6d38a',{sx:1,sy:2.6,sz:.4});
   gBuild.box(cx+1.5,cy+13,-24.5,3,1,3,P.slateD,{j:.04});
   gBuild.box(cx+2.7,cy+14,-23.3,.7,2,.7,P.gold,{j:.04});}
  /* blockhouse on the summit */
  {const fx=-44,fy=H(-44,-18);
   gBuild.box(fx,fy+1,-22,7,4,7,P.stone,{hollow:true,j:.05});
   gBuild.box(fx-1,fy+5,-23,9,1,9,P.stoneD,{j:.05});
   for(let i=0;i<4;i++)gBuild.box(fx+2,fy+6,-19+i*2,4,1,1,P.iron,{j:.05});
   gProps.box(fx+1,fy+6,-25,1,6,1,P.woodD,{j:.04});
   const F=makeFlag();F.build(gProps,gWin,null,fx+1.6,fy+11,-25,'','#c2342a',5,3,0);
   addCannon(gProps,fx+6,fy+1,-19,Math.PI/2);addCannon(gProps,fx-1,fy+1,-15,-Math.PI/2);}
  /* post mill on a knoll */
  let mx=-24,mz=4,my=H(mx,mz);
  if(my<4){mz=-2;my=H(mx,mz);}
  gBuild.box(mx-1,1,mz-1,5,my,5,P.stoneD,{j:.06});
  gBuild.box(mx,my+1,mz,3,4,4,P.plasterW,{j:.04});
  gBuild.box(mx-1,my+5,mz-1,5,1,6,P.slateD,{j:.05});
  gWin.v(mx,my+3,mz+2,'#f6d38a',{sx:1,sy:1,sz:.4});
  millHub=new THREE.Group();millHub.position.set(mx-1.6,my+3.4,mz+2);scene.add(millHub);
  const ms=new VB();
  for(let a=0;a<4;a++){
    for(let i=1;i<=7;i++)
      ms.v(0,Math.cos(a*Math.PI/2)*i,Math.sin(a*Math.PI/2)*i,P.woodD,{sx:.4,sy:1,sz:i>3?.5:1.6,j:.05});
  }
  millHub.add(ms.build(matSolid,{recv:false}));
  /* pines + furze */
  for(let i=0;i<150;i++){
    const x=Math.round(rr(-56,-14)),z=Math.round(rr(-44,20));
    const b=Math.round(rawGround(x,z));
    if(b<4||b>19)continue;
    if(rnd()<.42){
      const h=2+((rnd()*3)|0);
      gProps.box(x,b+1,z,1,h,1,P.trunk,{j:.06});
      for(let k=0;k<3;k++)gProps.box(x-1+k*.4,b+1+h-k,x-1+k*.4,3-k*.8,2,3-k*.8,k===2?P.pine:P.pineD,{j:.08});
    }else if(rnd()<.5){
      gProps.box(x,b+1,z,2,1,2,pick([P.drygrass,P.grass,P.gorse||'#b9a531']),{j:.10});
    }
  }
})();

/* ---- fort cannon helper ---- */
function addCannon(vb,x,y,z,rot){
  vb.box(x,y,z,2,1,2,P.iron,{j:.05});
  vb.v(x+1.2,y+1,z,P.tar,{sx:2.6,sy:.7,sz:.7,j:.03});
}

/* ---- flags ---- */
const flags=[],flagItems=[];
function makeFlag(){return{build(vb,win,dummy,x,y,z,kind,baseColor,w,h,ph){
  const items=[];
  for(let i=0;i<w;i++)for(let j=0;j<h;j++){
    let c=baseColor;
    if(kind==='ensign'){
      c='#c2342a';
      if(i<Math.ceil(w*.45)&&j<h*.55)c='#20406e';
      if(i<Math.ceil(w*.45)&&j<h*.55){if(i%3===1||Math.floor(j)%(Math.max(1,Math.floor(h*.55)))===0)c='#efeade';}
      if(j===Math.floor(h/2))c=(i%2===0)?'#efeade':'#c2342a';
    }else if(kind==='pennant'){c=j%2?'#efeade':'#2f5578';}
    else if(kind==='cheque'){c=((i+j)%2)?'#efeade':'#20262a';}
    else if(kind==='unionjack'&&i<Math.ceil(w*.4)&&j<h*.5){c=((i+j)%2)?'#efeade':'#c2342a';}
    else if(kind==='unionjack'){c=((i+j)%2)?'#efeade':'#c2342a';}
    items.push({x:x+i,y,z:z+j,c,sx:.28,sy:1,sz:1});
  }
  const base=flagItems.length;
  items.forEach(it=>{
    const col=new THREE.Color(it.c);col.offsetHSL(0,0,(rnd()*2-1)*.03);
    flagItems.push({...it,c:col});
  });
  flags.push({base,count:items.length,x0:x,ph:ph||rnd()*6});
  return items.length;
}};}

/* ══════════════════════════ THE BARQUE ══════════════════════════ */
const SHIP_POS=V(6,0,2),SHIP_ROTT=-0.34;
const ship=new THREE.Group();
ship.position.copy(SHIP_POS);ship.rotation.y=SHIP_ROTT;scene.add(ship);
const baseM=new THREE.Matrix4().compose(SHIP_POS,new THREE.Quaternion().setFromEuler(new THREE.Euler(0,SHIP_ROTT,0)),V(1,1,1));
const toWorld=v=>v.clone().applyMatrix4(baseM);

const halfBeam=z=>{
  const t=(z+14)/33;
  const aft=sstep(-.22,.03,t),fore=1-sstep(.52,1,t);
  return 5.0*Math.pow(Math.max(0,fore),.62)*aft;
};
const deckAt=z=>{
  const t=(z+14)/33;
  return Math.round(5+1.15*sstep(.70,.99,t)+1.0*sstep(.14,-.02,t));
};

const gHull=new VB(),gSail=new VB(),gRig=new VB(),gShipWin=new VB();
let sailMesh,sailCount=0;
(function barque(){
  /* hull */
  for(let z=-14;z<=19;z++){
    const b=halfBeam(z),dY=deckAt(z);
    for(let y=-2;y<=dY;y++){
      const flare=.60+.40*sstep(-2,dY-.6,y),w=b*flare,wi=Math.round(w);
      for(let x=-wi;x<=wi;x++){
        const edge=Math.abs(x)===wi;
        if(y>0&&y<dY&&!edge)continue;
        let c;
        if(y<=0)c=P.antifoul;
        else if(y===1)c=P.hullBlack;
        else if(y===2)c=(edge&&((z+16)%4===0)&&z<12)?P.hullDk:P.band;
        else if(y===3)c=edge?P.gold:P.hullBlack;
        else if(y===dY)c=pick([P.deck,P.deck,P.deckD,P.deckL]);
        else c=P.hullBlack;
        gHull.v(x,y,z,c,{j:y===dY?.09:.05});
      }
      if(dY>4){
        gHull.v(wi,dY+1,z,edgeWhite(z),{j:.03});gHull.v(-wi,dY+1,z,edgeWhite(z),{j:.03});
        gHull.v(wi,dY+2,z,P.woodL,{j:.05});gHull.v(-wi,dY+2,z,P.woodL,{j:.05});
      }
    }
  }
  const edgeWhite=z=>((z+14)%7<3)?P.gold:P.band;
  /* wale line + stern dress */
  for(let z=-14;z<=18;z++){const b=Math.round(halfBeam(z));gHull.v(b,1.0,z,P.hullDk,{sx:1,sy:.4,sz:1,j:.03});gHull.v(-b,1.0,z,P.hullDk,{sx:1,sy:.4,sz:1,j:.03});}
  gHull.box(-4,4,-14.6,9,3,1,P.gold,{j:.05});
  gHull.box(-3,4.4,-15.2,7,1,1,'#efe7d3',{j:.03});
  for(const sx of[-1,1])for(let y=4;y<=5;y+=2)gShipWin.v(sx*2.2,y,-14.7,'#f6d38a',{sx:1.1,sy:1,sz:.4});
  /* rudder + figurehead */
  for(let z=-17;z<=-14;z++)gHull.v(0,Math.round(-1.6+(z+17)*.25),z,P.hullDk,{sx:.7,sy:2.6,sz:1,j:.04});
  gHull.v(0,4.4,19.6,'#e7dcc0',{sx:.8,sy:1.4,sz:1.6,j:.05});
  /* bulwark cap rails, channels */
  for(const sx of[-1,1])for(let z=-13;z<=17;z+=2){const b=Math.round(halfBeam(z));if(b>1)gHull.v(sx*(b+.5),3.2,z,P.woodD,{sx:1,sy:.7,sz:1.6,j:.06});}
  /* masts & yards */
  const masts=[{z:8,top:25,n:'fore'},{z:-1,top:27.5,n:'main'},{z:-10,top:22,n:'mizzen'}];
  const heads={};
  for(const m of masts){
    const d0=deckAt(m.z)+.5,H=m.top;
    for(let y=d0;y<=H;y+=1){
      const th=lerp(1.0,.42,(y-d0)/(H-d0));
      gHull.v(0,y,m.z,P.woodD,{sx:th,sy:1,sz:th,j:.04});
    }
    gHull.v(0,H+.35,m.z,P.wood,{sx:1.4,sy:.4,sz:1.4,j:.04});
    heads[m.n]=V(0,H,m.z);
    gHull.box(-.9,H-4.6,m.z-.9,2,1,2,P.woodD,{j:.05});        // top platform
    for(let x=-2;x<=2;x++)if(Math.abs(x)>0)gHull.v(x*.55,H-4.1,m.z,P.wood,{sx:.3,sy:2.4,sz:.3,j:.05});
  }
  const yard=(mx,my,mz,span,bend)=>{
    for(let x=-span;x<=span;x+=1){
      const t=Math.abs(x)/span;
      gRig.v(x,my+bend*t*t,mz,P.woodD,{sx:1,sy:.55,sz:.55,j:.05},{q:null});
    }
    gRig.v(span,my+bend,mz,P.tar,{sx:.5,sy:.5,sz:.5,j:.04});gRig.v(-span,my+bend,mz,P.tar,{sx:.5,sy:.5,sz:.5,j:.04});
  };
  const sail=(yc,span,depth,zPos,belly,stripe)=>{
    const rows=Math.round(depth);
    for(let r=0;r<rows;r++){
      const v=r/(rows-1);
      for(let x=-Math.round(span);x<=Math.round(span);x++){
        const u=(x+span)/(2*span);
        const bulge=belly*Math.sin(Math.PI*clamp(u,0,1))*Math.sin(Math.PI*Math.min(1,v*.92+.06));
        let c=(r%2===1)?P.canvasD:P.canvas;
        if(stripe&&(r===Math.round(rows*.42)||r===Math.round(rows*.43)))c=stripe;
        gSail.items.push({x,y:yc-r,z:zPos+bulge,c:(()=>{const cc=new THREE.Color(c);cc.offsetHSL(0,0,(rnd()*2-1)*.04);return cc;})(),
          sx:1,sy:1,sz:.34,q:null,anchorY:yc});
      }
    }
  };
  yard(0,14.2,8,5.0,1.4);sail(13.6,4.8,5.4,8,1.5,null);
  yard(0,20.2,8,3.7,1.1);sail(19.6,3.5,4.2,8,1.1,null);
  yard(0,13.4,-1,5.8,1.7);sail(12.8,5.6,6.6,-1,1.9,P.sailRed);
  yard(0,20.4,-1,4.2,1.3);sail(19.8,4.0,5.0,-1,1.4,null);
  /* mizzen: gaff, boom, spanker */
  const mz=-10,mzb=deckAt(mz);
  gRig.v(0,mzb+4,mz-2.2,P.woodD,{sx:.4,sy:4.6,sz:.4,j:.05});
  seg(gRig,V(0,mzb+3,mz-.4),V(0,mzb+3,mz-7.4),.5,P.woodD);
  seg(gRig,V(0,mzb+3.2,mz-.4),V(0,mzb+8.2,mz-4.4),.45,P.woodD);
  triFill(gSail,V(0,mzb+7.8,mz-.6),V(0,mzb+3.4,mz-7.0),V(0,mzb+3.4,mz-.6),P.canvas,'x');
  for(const it of gSail.items.slice(-40))if(it.anchorY===undefined)it.anchorY=mzb+8;
  /* bowsprit + jibs */
  seg(gHull,V(0,deckAt(18)+1,19),V(0,10.2,29),1.0,P.woodD);
  seg(gHull,V(0,10.2,29),V(0,12.0,36),.6,P.wood);
  triFill(gSail,V(0,11.7,35),V(0,9.2,26),V(0,19.4,17),P.canvas,'x');
  triFill(gSail,V(0,9.0,25.6),V(0,12.0,19.6),V(0,19.0,17.4),P.canvas,'x');
  const jibStart=gSail.items.length-160;
  for(let i=jibStart;i<gSail.items.length;i++){const it=gSail.items[i];if(it)it.anchorY=it.y;}
  /* rigging */
  for(const m of masts){
    const h=heads[m.n],dY=deckAt(m.z);
    for(const sx of[-1,1]){
      for(let k=0;k<3;k++){
        const zz=m.z+(k-1)*1.7,b=Math.max(1.5,Math.round(halfBeam(zz)));
        seg(gRig,V(sx*b,dY+2,zz),h,.13,P.rig);
      }
      seg(gRig,V(sx*Math.max(1.5,Math.round(halfBeam(m.z+4))),deckAt(m.z+4)+2,V(0,0,0).setX(0).setY(heads[m.n].y-4).setZ(m.z+4)),.1,P.rigL);
    }
    seg(gRig,h,V(0,deckAt(m.z+9)+3,m.z+9),.12,P.rigL);
    if(m.n!=='mizzen')seg(gRig,h.clone().setY(h.y-2),V(0,deckAt(m.z-9)+3,m.z-9),.12,P.rigL);
  }
  seg(gRig,V(0,12.0,36),heads.fore.clone().setY(heads.fore.y-1),.11,P.rigL);
  seg(gRig,V(0,10.2,29),V(0,deckAt(18)+3,18),.14,P.rigL);
  for(const n of['fore','main']){
    const hy=heads[n].y-6;
    for(const sx of[-1,1]){
      seg(gRig,V(sx*(n==='main'?5.8:5.0),hy+1.7,heads[n].z),heads[n].clone().setY(heads[n].y-3),.09,P.rigL);
      seg(gRig,V(sx*(n==='main'?5.8:5.0),hy+1.7,heads[n].z),V(sx*4,deckAt(heads[n].z)+2,heads[n].z-3),.09,P.rigL);
    }
  }
  /* deck furniture */
  gHull.box(-1.4,deckAt(4)+1,3,3,1,4,P.deckD,{j:.07});            // hatch
  gHull.box(-1.4,deckAt(-5)+1,-6,3,1,4,P.deckD,{j:.07});
  for(const zz of[12,-3]){gHull.box(-.9,deckAt(zz)+1,zz-.9,2,1,2,P.woodD,{j:.05});gHull.box(-.6,deckAt(zz)+2,zz-.6,1.4,.6,1.4,P.woodL,{j:.05});}
  for(const sx of[-1,1])for(const zz of[6,0,-8])gHull.v(sx*3,deckAt(zz)+1,zz,P.woodD,{sx:1.2,sy:2.2,sz:1.2,j:.06});
  gHull.box(-2,deckAt(-13)+1,-13,5,2,2,'#efe7d3',{j:.04});        // boat skid
  gHull.box(-1.6,deckAt(-13)+3,-13.4,4,1,1.2,P.wood,{j:.05});
  for(let z=1;z<4;z++)gHull.v(0,deckAt(2)+1.4,z,'#3a2b1c',{sx:3,sy:.3,sz:.3,j:.06});
  /* flagstaffs + flags */
  seg(gHull,V(0,deckAt(-14)+1,-13.5),V(0,deckAt(-14)+7,-15.4),.3,P.woodD);
  const F=makeFlag();
  F.build(null,null,null,-0.4,deckAt(-14)+5.2,-15.6,'ensign','#c2342a',6,4,1.1);
  F.build(null,null,null,-0.4,heads.mizzen.y-1.4,-10,'pennant','#fff',7,2,2.2);
  F.build(null,null,null,-.4,heads.main.y-2.6,-1,'unionjack','#c2342a',6,4,3.4);
  F.build(null,null,null,-.4,heads.fore.y-2.2,8,'cheque','#efeade',5,3,4.1);
  /* the Q flag — she has not yet taken pratique */
  gHull.box(2.6,deckAt(-9)+2,-9.6,.4,4,.4,P.woodD,{j:.04});
  F.build(null,null,null,2.9,deckAt(-9)+4.4,-9.4,'',P.yellow,4,4,5.5);
  sailCount=gSail.items.length;
  gShipWin.items.forEach(()=>{});
})();

const hullMesh=gHull.build(matSolid);ship.add(hullMesh);
const rigMesh=gRig.build(matSolid,{cast:false});ship.add(rigMesh);
sailMesh=gSail.build(matSolid,{cast:true,recv:true});ship.add(sailMesh);
const swMesh=gShipWin.build(matWin,{cast:false,recv:false});ship.add(swMesh);
const flagMesh=new VB();
flagItems.forEach(it=>flagMesh.items.push(it));
const flagInst=flagMesh.build(matSolid,{cast:false,recv:false});ship.add(flagInst);
let sailAmt=.72,sailTarget=.72;

/* ---- moorings, gangway, anchor chain ---- */
(function moorings(){
  const bow=toWorld(V(2.6,deckAt(17)+1,17.5)),stern=toWorld(V(2.6,deckAt(-12)+1,-12.5)),
        mid=toWorld(V(4.6,deckAt(3)+2,3));
  const q1=V(16.9,5.6,12),q2=V(16.9,5.6,-9),q3=V(16.9,5.6,2);
  const hawser=(a,b)=>{
    const n=Math.ceil(a.distanceTo(b)/1.6),p=new THREE.Vector3(),t=new THREE.Vector3();
    for(let i=0;i<n;i++){
      const u0=i/n,u1=(i+1)/n;
      const sag=(a,b,u)=>Math.sin(u*Math.PI)*a.distanceTo(b)*.055;
      p.lerpVectors(a,b,u0);p.y-=sag(a,b,u0);
      t.lerpVectors(a,b,u1);t.y-=sag(a,b,u1);
      seg(gProps,p,t,.24,P.rigL,{cast:false});
    }
  };
  hawser(bow,q1);hawser(stern,q2);hawser(mid,q3);
  /* gangway */
  const g0=V(15.2,3.6,3.2),g1=toWorld(V(5.0,deckAt(3)+2.2,3.2));
  const n=Math.ceil(g0.distanceTo(g1));
  for(let i=0;i<=n;i++){
    const u=i/n,p=new THREE.Vector3().lerpVectors(g0,g1,u);
    gProps.v(Math.round(p.x),Math.round(p.y),Math.round(p.z),pick([P.wood,P.woodL,P.woodD]),{sx:1.6,sy:.4,sz:1.6,j:.06});
    if(i%3===0){gProps.v(Math.round(p.x),Math.round(p.y)+1.4,Math.round(p.z)-.9,P.rigL,{sx:.2,sy:2.6,sz:.2});
                gProps.v(Math.round(p.x),Math.round(p.y)+1.4,Math.round(p.z)+.9,P.rigL,{sx:.2,sy:2.6,sz:.2});}
  }
  /* anchor cable to the chain hawse */
  const haw=toWorld(V(3.4,deckAt(16),16));
  for(let i=0;i<22;i++){const u=i/21;
    gProps.v(Math.round(lerp(haw.x,10,u)),Math.round(lerp(haw.y,.4,u)-Math.sin(u*Math.PI)*1.4),Math.round(lerp(haw.z,22,u)),
      P.tar,{sx:.8,sy:.6,sz:.8,j:.06});}
})();

/* ---- small craft ---- */
const boats=[];
(function smallCraft(){
  const mk=(cx,cz,scale,cols,bobPh)=>{
    const vb=new VB();
    for(let z=-3;z<=3;z++){
      const w=Math.max(1,Math.round(1.6*(1-Math.pow(Math.abs(z)/3.4,2))));
      for(let x=-w;x<=w;x++)
        vb.v(x,0,z,Math.abs(x)===w?cols.hull:cols.deck,{j:.06});
    }
    vb.box(-1,1,-2,3,1,1,cols.trim,{j:.05});
    vb.v(0,2,1,cols.mast,{sx:.35,sy:3.2,sz:.35,j:.04});
    vb.v(0,3.4,1.4,cols.sail,{sx:.3,sy:1.8,sz:1.4,j:.05});
    const g=new THREE.Group();g.position.set(cx,0,cz);g.rotation.y=rnd()*6;
    g.add(vb.build(matSolid));scene.add(g);
    boats.push({g,base:V(cx,0,cz),ph:bobPh,scale});
    return g;
  };
  mk(-8,26,1,{hull:P.redL,deck:P.woodL,trim:P.white,mast:P.woodD,sail:P.canvasD},.4);
  mk(-15,18,1,{hull:P.green,deck:P.wood,trim:P.sand,mast:P.woodD,sail:P.canvasD},2.1);
  mk(11,26,1,{hull:P.woodD,deck:P.woodL,trim:P.blue,mast:P.woodD,sail:P.canvas},4.0);
  const rowboat=toWorld(V(-4.5,1.4,10));
  mk(rowboat.x,rowboat.z,1,{hull:P.hullBlack,deck:P.woodL,trim:P.white,mast:P.woodD,sail:P.white},1.2);
})();

/* ---- buoys ---- */
const buoyItems=[];
(function buoys(){
  const list=[
    {x:-6,z:30,c:P.red,kind:'conical'},{x:9,z:34,c:P.green,kind:'can'},
    {x:-20,z:33,c:P.white,kind:'cheque',kind2:true},{x:20,z:20,c:P.tar,kind:'bell'}
  ];
  list.forEach((b,i)=>{
    const base=buoyItems.length;
    if(b.kind==='cheque'){
      for(let y=0;y<2;y++)for(let x=-1;x<=1;x++)for(let z=-1;z<=1;z++)
        gSea.items.push(buoy(buoyItems.length,x,y,z,((x+y+z)%2===0)?P.white:P.tar));
    }else{
      const w=b.kind==='can'?1:1;
      for(let y=0;y<3;y++){const ww=Math.max(0,Math.round(w-(b.kind==='conical'?y*.4:0)));
        for(let x=-ww;x<=ww;x++)for(let z=-ww;z<=ww;z++)buoyItems.push(buoyItem(buoyItems.length,x,y,z,b.c));}
      for(let x=-1;x<=1;x++)for(let z=-1;z<=1;z++)buoyItems.push(buoyItem(buoyItems.length,x,3,z,i%2?P.gold:'#e6e0d2'));
    }
    if(b.kind==='bell'){buoyItems.push(buoyItem(buoyItems.length,0,4,0,P.gold));buoyItems.push(buoyItem(buoyItems.length,0,4.6,0,P.tar));}
    buoyItems.forEach((it,k)=>{if(k>=base)it.buoy=i;});
  });
  function buoy(idx,x,y,z,c){return buoyItem(idx,x,y,z,c);}
  function buoyItem(idx,x,y,z,c){
    const col=new THREE.Color(c);col.offsetHSL(0,0,(rnd()*2-1)*.05);
    return {x:list[0]?0:0,y,z,c:col,sx:1,sy:1,sz:1,q:null,off:V(x,y,z)};
  }
  // place them at their own spots
  const mesh=new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1),matSolid,buoyItems.length);
  mesh.castShadow=true;mesh.receiveShadow=true;mesh.frustumCulled=false;
  scene.add(mesh);
  buoyItems.forEach((it,i)=>{it.home=V(list[it.buoy].x,0,list[it.buoy].z);it.col=it.c;});
  window.__buoys=buoyItems;window.__buoyMesh=mesh;
})();

/* ---- windows merged (buildings) ---- */
/* ---- lighthouse ---- */
let beaconGroup;
(function lighthouse(){
  const bx=1.2,bz=42,base=3;
  gBuild.box(bx-2,base+1,bz-2,5,2,5,P.granite,{j:.06});
  const bands=['#e9e2d1','#c2342a'];
  for(let y=0;y<10;y++){
    const w=Math.max(1,Math.round(3-y*.19));
    for(let x=-w;x<=w;x++)for(let z=-w;z<=w;z++)
      gBuild.v(bx+x,base+3+y,bz+z,bands[y%2],{j:.05});
  }
  gBuild.box(bx-3,base+13,bz-3,7,1,7,P.iron,{j:.04});
  for(const dx of[-3,3])for(const dz of[-3,3])gBuild.v(bx+dx,base+14.5,bz+dz,P.iron,{sx:.4,sy:3,sz:.4,j:.03});
  gBuild.box(bx-2,base+14,bz-2,5,3,5,'#2b3a44',{hollow:true,j:.03});
  for(let y=0;y<3;y++)gWin.v(bx,base+14.5+y,bz+2.1,'#ffdca0',{sx:3.4,sy:.85,sz:.4});
  for(let y=0;y<3;y++)gWin.v(bx,base+14.5+y,bz-2.1,'#ffdca0',{sx:3.4,sy:.85,sz:.4});
  for(let y=0;y<3;y++){gWin.v(bx+2.1,base+14.5+y,bz,'#ffdca0',{sx:.4,sy:.85,sz:3.4});
                       gWin.v(bx-2.1,base+14.5+y,bz,'#ffdca0',{sx:.4,sy:.85,sz:3.4});}
  gBuild.box(bx-2,base+17,bz-2,5,1,5,P.tar,{j:.04});
  for(let i=0;i<3;i++)gBuild.box(bx-2+i,base+18+i,bz-2+i,5-2*i,1,5-2*i,P.copper,{j:.05});
  gBuild.v(bx,base+21.6,bz,P.tar,{sx:.4,sy:2.4,sz:.4});
  const F=makeFlag();F.build(gProps,null,null,bx+.3,base+21.4,bz,'','#b2342c',4,2,.7);
  beaconGroup=new THREE.Group();beaconGroup.position.set(bx,base+15.5,bz);scene.add(beaconGroup);
  const cone=new THREE.ConeGeometry(3.4,26,4,1,true);
  for(const s of[0,Math.PI]){
    const m=new THREE.Mesh(cone,matGlow);
    m.rotation.z=Math.PI/2;m.rotation.y=s;
    m.position.set(Math.cos(s)*13,0,Math.sin(s)*13);
    beaconGroup.add(m);
  }
})();

/* ---- clouds ---- */
const cloudGroup=new THREE.Group();scene.add(cloudGroup);
(function clouds(){
  const vb=new VB();
  for(let c=0;c<9;c++){
    const cx=rr(-90,90),cy=rr(34,52),cz=rr(-90,70),n=4+((rnd()*4)|0);
    for(let i=0;i<n;i++)
      vb.v(cx+rr(-7,7),cy+rr(-1.5,2),cz+rr(-6,6),pick(['#f6f2ea','#e8e6e2','#fbf6ec']),
        {sx:rr(5,11),sy:rr(1.6,3.2),sz:rr(4,9),j:.03});
  }
  cloudGroup.add(vb.build(matSolid,{cast:false,recv:false}));
})();

/* ---- smoke ---- */
const sources=[V(31,15.5,6),V(24,12,-26),V(-37,10,-12)];
const smokeN=sources.length*9;
const smoke=new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1),matSmoke,smokeN);
smoke.frustumCulled=false;scene.add(smoke);
const puffs=[];for(let i=0;i<smokeN;i++)puffs.push({s:i%sources.length,l:rnd()*3.4,sp:rr(.6,1.15),sw:rr(0,6)});

/* ---- gulls ---- */
const gulls=[];const gullN=7;
const gullMesh=new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1),matSolid,gullN*4);
gullMesh.frustumCulled=false;scene.add(gullMesh);
for(let i=0;i<gullN;i++)gulls.push({c:V(rr(-10,20),rr(14,24),rr(-6,32)),r:rr(11,26),sp:rr(.16,.36)*(rnd()<.5?-1:1),
  ph:rnd()*6.28,fl:rr(5,8),amp:rr(.5,1.0)});

/* ---- people ---- */
const PART=[{w:.5,h:1.25,d:.4,y:.62},{w:.7,h:1.05,d:.5,y:1.72},{w:.44,h:.44,d:.44,y:2.44},{w:.6,h:.22,d:.6,y:2.72}];
const people=[];
(function folks(){
  const path=(pts,loop=true)=>{
    const P0=pts.map(p=>V(p[0],0,p[1]));const segs=[];let total=0;
    const all=loop?P0.concat([P0[0]]):P0;
    for(let i=0;i<all.length-1;i++){const L=all[i].distanceTo(all[i+1]);segs.push([all[i],all[i+1],L]);total+=L;}
    return{segs,total};
  };
  const sailor=['#2b5c87','#2b5c87',P.skin,'#efeade'],docker=['#4b3a26','#8a5a33',P.skin,'#b23a2c'],
        dame=['#2f6b4f','#3f7a5c',P.skin,'#d9b25a'],mate=['#20262a','#c23a2c',P.skin,'#efeade'],
        official=['#b2342c','#b2342c',P.skin,'#20262a'],harb=['#20262a','#2f363b',P.skin,'#ddaf3d'];
  const defs=[
    {p:path([[18,6],[18,-8],[24,-8],[24,10]]),c:sailor,s:.7},
    {p:path([[19,24],[19,4],[26,4]]),c:docker,s:.55},
    {p:path([[17,-16],[17,-24],[6,-24],[-4,-24]]),c:dame,s:.5},
    {p:path([[20,14],[26,14],[26,20],[20,20]]),c:sailor,s:.8},
    {p:path([[24,-22],[34,-22],[34,-28],[24,-28]]),c:official,s:.45},
    {p:path([[16,0],[16,10]]),c:mate,s:.6},
    {p:path([[22,26],[28,26],[30,18]]),c:docker,s:.62},
    {p:path([[0,-21],[8,-21],[8,-19],[0,-19]]),c:dame,s:.42},
    {p:{segs:[[V(3.1,deckAt(6),6),V(3.1,deckAt(6),10),1.2],[V(3.1,deckAt(6),10),V(3.1,deckAt(6),6),1.2]],total:4.8},c:sailor,s:.4,ship:true},
    {p:{segs:[[V(-2.6,deckAt(-4),-4),V(-2.6,deckAt(-4),2),6],[V(-2.6,deckAt(-4),2),V(-2.6,deckAt(-4),-4),6]],total:12},c:mate,s:.32,ship:true},
    {p:null,c:harb,s:0,at:V(0,deckAt(-1)+1,-1.2),ship:true,face:0},
    {p:null,c:harb,s:0,at:V(18.4,4,3.4),face:-1.57},
    {p:null,c:docker,s:0,at:V(18.4,4,12.4),face:1.57},
    {p:null,c:sailor,s:0,at:V(17,4,1.6),face:1.57},
    {p:null,c:dame,s:0,at:V(-8,4,-22.6),face:0},
    {p:null,c:dame,s:0,at:V(-5,4,-22.6),face:0},
    {p:null,c:docker,s:0,at:V(-11,5,-22.6),face:3.14},
    {p:null,c:official,s:0,at:V(16.4,4,2.2),face:1.57},
    {p:path([[-19,-14],[-19,-20],[-24,-24],[-30,-26],[ -24,-20],[-19,-14]]),c:dame,s:.35},
    {p:path([[30,-30],[36,-24],[30,-18]]),c:sailor,s:.4}
  ];
  for(const d of defs){
    const pal=d.c;
    people.push({path:d.p,s:rnd()*20,sp:d.s,cfg:[pal[0],pal[1],pal[2],d.at&&d.face===undefined?pal[3]:pal[3]],
      ship:!!d.ship,at:d.at,face:d.face});
  }
  // a dog
  people.push({dog:true,path:path([[19,2],[24,2],[24,10]]),s:2,sp:1.1,cfg:[P.straw,P.straw,P.straw,'#4a3320']});
})();
const personMesh=new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1),matSolid,people.length*4);
personMesh.castShadow=true;personMesh.frustumCulled=false;scene.add(personMesh);
{const c=new THREE.Color();
 for(let i=0;i<people.length;i++)for(let k=0;k<4;k++){
   c.set(people[i].cfg[k]);c.offsetHSL(0,0,(rnd()*2-1)*.05);personMesh.setColorAt(i*4+k,c);}}
personMesh.instanceColor.needsUpdate=true;

/* ---- sea + static meshes into the scene ---- */
scene.add(gSea.build(seaMat,{cast:false,recv:true}));
scene.add(gLand.build(matSolid));
scene.add(gProps.build(matSolid));
scene.add(gBuild.build(matSolid));
const winMesh=gWin.build(matWin,{cast:false,recv:false});scene.add(winMesh);

/* ---- the cargo davit (animated) ---- */
let davitHook,crateMesh,davitArm;
(function davit(){
  const x=24,z=8,base=4;
  gBuild.box(x,base+1,z,2,7,2,P.woodD,{j:.05});
  gBuild.box(x-1,base+8,z-1,4,1,4,P.woodD,{j:.05});
  davitArm=new THREE.Group();davitArm.position.set(x+.5,base+8,z);scene.add(davitArm);
  const arm=new VB();
  seg(arm,V(0,0,0),V(0,0,6),.9,P.woodD);seg(arm,V(0,1.6,0),V(0,0,5),.6,P.woodD);
  davitArm.add(arm.build(matSolid));
  crateMesh=new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1),matSolid,3);
  crateMesh.castShadow=true;crateMesh.frustumCulled=false;scene.add(crateMesh);
  const cc=[P.wood,P.woodD,P.woodL].map(h=>new THREE.Color(h));
  cc.forEach((c,i)=>crateMesh.setColorAt(i,c));crateMesh.instanceColor.needsUpdate=true;
  davitHook={x:x+.5,z:z+6,base};
})();

/* ══════════════════════════ hotspots ══════════════════════════ */
const HOT=[
 {n:'The barque',d:'214 grt',p:V(0,20,2),cam:[[-30,20,34],[2,9,3]],
  note:'<b>MRS. ADELAIDE RYVES · barque · Plymouth</b>Arrived 14:12 from Falmouth in ballast, flying Q pending pratique. Master: E. Trewinnard. Now made fast to No. 3 berth, taking in 60 tons of china clay.'},
 {n:'Graywater light',d:'fl. 6s',p:V(1,21,42),cam:[[26,17,48],[1,15,42]],
  note:'<b>GRAYWATER LIGHT · 24 ft on the mole</b>Showing a single flash every six seconds from a revolving apparatus. Keeper and assistant maintained by the Trinity Outposts Board; the fog gun stands ready on the plinth.'},
 {n:'The custom house',d:'est. 1806',p:V(29,13,10),cam:[[2,20,28],[29,10,9]],
  note:'<b>THE CUSTOM HOUSE</b>Brick and slate, with the harbour clock over the great door. The davit swings cargo straight from a lighter to the warehouse floor. Cargo gates close at dusk and are not opened for anyone.'},
 {n:'Fish market',d:'nets on',p:V(-8,7,-22),cam:[[-2,16,-40],[-8,5,-22]],
  note:'<b>THE FISH MARKET</b>Under the long shed: mackerel, crab and whatever the inshore smack brings in before tide-fall. Nets are dried on the quay wall and the town clock is the only reason anyone hurries.'},
 {n:'The entrance',d:'bell buoys',p:V(-6,4,30),cam:[[-18,14,46],[-4,3,28]],
  note:'<b>THE NARROWS</b>A shoal of grey stone runs out from the Point, and the flood tide makes it furious in a westerly gale. Conical to starward, can to larboard, and the bell buoy warns off the rest.'},
 {n:'Harbor mill',d:'wind vane',p:V(-23,16,4),cam:[[-2,24,22],[-23,13,4]],
  note:'<b>THE HARBOR MILL</b>A post mill on the knoll, turned by hand to face the wind when the corn ships come in. The cottages behind it climb to the old blockhouse on the summit.'}
];
const markers=document.getElementById('markers'),idx=document.getElementById('idx');
HOT.forEach((h,i)=>{
  const b=document.createElement('button');b.className='hot';
  b.innerHTML=`<i class="dot"></i><span class="lab"><b>${h.n}</b><em>${h.d}</em></span>`;
  b.onclick=()=>select(i);markers.appendChild(b);h.el=b;
  const li=document.createElement('li');
  li.innerHTML=`<button><span class="n">0${i+1}</span><span class="t">${h.n}</span><span class="d">${h.d}</span></button>`;
  li.querySelector('button').onclick=()=>select(i);idx.appendChild(li);h.li=li.querySelector('button');
});
let active=-1;
function select(i){
  active=i;const h=HOT[i];
  HOT.forEach((o,k)=>{o.el.classList.toggle('on',k===i);o.li.classList.toggle('on',k===i);});
  document.getElementById('readout').innerHTML=h.note;
  flyTo(V(...h.cam[0]),V(...h.cam[1]));
  controls.autoRotate=false;swState.orbit=false;syncSwitches();
}

/* ══════════════════════════ time of day ══════════════════════════ */
const C=h=>new THREE.Color(h);
const WATCH=[
 {name:'grey dawn',top:'#1d3a63',mid:'#7d96b2',bot:'#f2c39a',sun:'#ffcf9b',sunI:1.75,
  hs:'#8fa7c6',hg:'#42483f',hi:.62,amb:.20,fog:'#a9bccd',deep:'#14344f',shal:'#5b95a4',
  win:.42,lamp:.35,glow:.9,dir:[-.82,.20,.44],fogFar:300,cloud:'#e8dfd6'},
 {name:'golden evening',top:'#2f6fa4',mid:'#a9c4d5',bot:'#f3c78c',sun:'#ffe0b0',sunI:2.15,
  hs:'#9dbcd8',hg:'#4c4b3d',hi:.80,amb:.22,fog:'#b5c3cf',deep:'#0f3350',shal:'#4a97a8',
  win:.30,lamp:.15,glow:1.0,dir:[-.85,.30,.40],fogFar:320,cloud:'#f7efe4'},
 {name:'high noon',top:'#2b74bd',mid:'#9dc6e4',bot:'#ddeaf0',sun:'#fff7e4',sunI:2.85,
  hs:'#a8cdec',hg:'#5b5c4c',hi:.95,amb:.26,fog:'#cfdfe7',deep:'#0d4260',shal:'#58aec0',
  win:.06,lamp:0,glow:.65,dir:[-.45,.88,.22],fogFar:360,cloud:'#ffffff'},
 {name:'night lamps',top:'#050c1a',mid:'#11223c',bot:'#2b3c58',sun:'#8fb4f0',sunI:.5,
  hs:'#2c4166',hg:'#151a1e',hi:.36,amb:.14,fog:'#16283e',deep:'#051523',shal:'#1b4460',
  win:1.0,lamp:1.0,glow:.35,dir:[.45,.35,-.6],fogFar:230,cloud:'#31405a'}
];
const cur={top:C('#2f6fa4'),mid:C('#a9c4d5'),bot:C('#f3c78c'),sun:C('#ffe0b0'),fog:C('#b5c3cf'),
  deep:C('#0f3350'),shal:C('#4a97a8'),hs:C('#9dbcd8'),hg:C('#4c4b3d'),cloud:C('#f7efe4'),
  sunI:2.15,hi:.80,amb:.22,win:.30,lamp:.15,glow:1,dir:V(-.85,.3,.4)};
let wTarget=1;
function applyWatch(dt){
  const W=WATCH[wTarget],k=1-Math.exp(-2.6*dt);
  cur.top.lerp(C(W.top),k);cur.mid.lerp(C(W.mid),k);cur.bot.lerp(C(W.bot),k);
  cur.sun.lerp(C(W.sun),k);cur.fog.lerp(C(W.fog),k);cur.deep.lerp(C(W.deep),k);
  cur.shal.lerp(C(W.shal),k);cur.hs.lerp(C(W.hs),k);cur.hg.lerp(C(W.hg),k);cur.cloud.lerp(C(W.cloud),k);
  cur.sunI=lerp(cur.sunI,W.sunI,k);cur.hi=lerp(cur.hi,W.hi,k);cur.amb=lerp(cur.amb,W.amb,k);
  cur.win=lerp(cur.win,W.win,k);cur.lamp=lerp(cur.lamp,W.lamp,k);cur.glow=lerp(cur.glow,W.glow,k);
  cur.dir.lerp(V(...W.dir),k).normalize();
  skyU.uTop.value.copy(cur.top);skyU.uMid.value.copy(cur.mid);skyU.uBot.value.copy(cur.bot);
  skyU.uSunCol.value.copy(cur.sun);skyU.uSunDir.value.copy(cur.dir);skyU.uGlow.value=cur.glow;
  scene.fog.color.copy(cur.fog);scene.fog.far=lerp(scene.fog.far,W.fogFar,k);
  renderer.setClearColor(cur.fog);
  sun.color.copy(cur.sun);sun.intensity=cur.sunI;
  sun.position.copy(cur.dir).multiplyScalar(150);
  hemi.color.copy(cur.hs);hemi.groundColor.copy(cur.hg);hemi.intensity=cur.hi;
  amb.intensity=cur.amb;
  uDeep.value.copy(cur.deep);uShal.value.copy(cur.shal);
  const day=1-cur.win;
  matWin.color.setRGB(lerp(1,.16,day),lerp(.86,.20,day),lerp(.62,.26,day));
  lamp.intensity=cur.lamp*1.5;
  matGlow.opacity=.05+cur.lamp*.22;
}

/* ══════════════════════════ UI ══════════════════════════ */
const swState={orbit:true,marks:true,birds:true,crew:true};
const $=s=>document.querySelector(s);
document.querySelectorAll('#watch button').forEach(b=>{
  b.onclick=()=>{document.querySelectorAll('#watch button').forEach(o=>o.classList.remove('on'));
    b.classList.add('on');wTarget=+b.dataset.w;};
});
const sea=$('#sea'),sail=$('#sail');
sea.oninput=()=>{uAmp.value=+sea.value;
  $('#v-sea').textContent=sea.value<.2?'glassy':sea.value<.6?'slight':sea.value<1.1?'moderate':sea.value<1.45?'rough':'boisterous';};
sail.oninput=()=>{sailTarget=+sail.value;
  $('#v-sail').textContent=sail.value<.06?'furled':sail.value<.35?'close-reefed':sail.value<.62?'half':sail.value<.9?'three-quarters':'full canvas';};
document.querySelectorAll('.sw').forEach(s=>{
  s.onclick=()=>{const t=s.dataset.t;swState[t]=!swState[t];s.classList.toggle('on',swState[t]);
    if(t==='marks')markers.classList.toggle('hide',!swState[t]);
    if(t==='birds')gullMesh.visible=swState[t];
    if(t==='crew')personMesh.visible=swState[t];
    if(t==='orbit')controls.autoRotate=swState[t];};
});
function syncSwitches(){document.querySelectorAll('.sw').forEach(s=>s.classList.toggle('on',swState[s.dataset.t]));}
syncSwitches();
$('#collapse').onclick=e=>{const p=$('#panel');p.classList.toggle('min');e.target.textContent=p.classList.contains('min')?'+':'–';};
$('#reset').onclick=()=>{active=-1;HOT.forEach(o=>{o.el.classList.remove('on');o.li.classList.remove('on');});
  flyTo(DEF_POS,DEF_TGT);};

/* ticker */
const NOTICE=`Pilots weigh at the mouth from first light · Cargo gates close at dusk and are not opened for anyone ·
 Gun fired from the mole at noon if weather permits · Masters to show colors before entering the Narrows ·
 Fresh water free at the Custom House spout · Salmon nets off the Point are forbidden on Sundays ·
 The bell buoy at the eastern stone has been newly painted · Harbor hands to the No. 3 berth for the clay loading`;
document.getElementById('tape').innerHTML=`<div>${NOTICE.replace(/·/g,'<em>◆</em>')}</div><div>${NOTICE.replace(/·/g,'<em>◆</em>')}</div>`;

/* ══════════════════════════ camera fly ══════════════════════════ */
let tween={t:9,d:1,p0:camera.position.clone(),t0:DEF_TGT.clone(),p1:DEF_POS.clone(),t1:DEF_TGT.clone()};
function flyTo(p,tg,dur=1.5){
  tween={t:0,d:dur,p0:camera.position.clone(),t0:controls.target.clone(),p1:p.clone(),t1:tg.clone()};
}
let intro=true;
renderer.domElement.addEventListener('pointerdown',()=>{intro=false;tween.t=9;controls.enabled=true;});

/* ══════════════════════════ animation ══════════════════════════ */
const _m=new THREE.Matrix4(),_q=new THREE.Quaternion(),_p=new THREE.Vector3(),_s=new THREE.Vector3();
const _a=new THREE.Vector3(),_b=new THREE.Vector3();
let t=0,last=performance.now()/1000,fpsAcc=0,fpsN=0;
document.getElementById('s-vox').textContent=TOTAL.toLocaleString('en-GB');
document.getElementById('v-sea').textContent='moderate';
document.getElementById('v-sail').textContent='three-quarters';
const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;

function loop(){
  const now=performance.now()/1000;let dt=Math.min(.05,now-last);last=now;t+=dt;
  uTime.value=t;
  applyWatch(dt);

  /* camera tween / intro */
  if(intro&&t>0.4&&!tween.done){tween={t:0,d:2.8,p0:camera.position.clone(),t0:controls.target.clone(),p1:DEF_POS,t1:DEF_TGT};intro=false;controls.enabled=true;}
  if(tween.t<9&&tween.t<tween.d){
    tween.t+=dt;const u=clamp(tween.t/tween.d,0,1),e=u<.5?4*u*u*u:1-Math.pow(-2*u+2,3)/2;
    camera.position.lerpVectors(tween.p0,tween.p1,e);
    controls.target.lerpVectors(tween.t0,tween.t1,e);
    controls.autoRotate=false;
  }else controls.autoRotate=swState.orbit&&!reduce;

  /* the barque rides the sea */
  const w0=waveH(SHIP_POS.x,SHIP_POS.z,t);
  const wX=waveH(SHIP_POS.x+5,SHIP_POS.z,t)-w0;
  const wZ=waveH(SHIP_POS.x,SHIP_POS.z+9,t)-w0;
  ship.position.y=w0*1.05;
  ship.rotation.z=-wX*.42;
  ship.rotation.x=wZ*.30;
  ship.rotation.y=SHIP_ROTT+Math.sin(t*.19)*.006;

  /* canvas hoists */
  if(Math.abs(sailAmt-sailTarget)>.001){
    sailAmt=smoothDamp(sailAmt,sailTarget,3.4,dt);
    for(let i=0;i<sailCount;i++){
      const it=gSail.items[i];
      const dy=it.y-it.anchorY;
      _p.set(it.x,it.anchorY+dy*sailAmt,it.z);
      _s.set(it.sx,Math.max(.02,sailAmt),it.sz);
      _m.compose(_p,_q.identity(),_s);sailMesh.setMatrixAt(i,_m);
    }
    sailMesh.instanceMatrix.needsUpdate=true;
  }

  /* flags */
  for(const f of flags){
    for(let i=0;i<f.count;i++){
      const it=flagItems[f.base+i],d=it.x-f.x0;
      const y=it.y+Math.sin(t*7.6-d*.95+f.ph)*.30*clamp(.2+d*.28,0,1.4);
      const z=it.z+Math.sin(t*5.2-d*.7+f.ph)*.12;
      _m.compose(_p.set(it.x,y,z),_q.identity(),_s.set(it.sx,it.sy,it.sz));
      flagInst.setMatrixAt(f.base+i,_m);
    }
    flagInst.instanceMatrix.needsUpdate=true;
  }

  /* boats bob */
  for(const b of boats){
    const h=waveH(b.g.position.x,b.g.position.z,t);
    b.g.position.y=h*1.05;
    b.g.rotation.z=-((waveH(b.g.position.x+3,b.g.position.z,t)-h)*.5);
    b.g.rotation.x=((waveH(b.g.position.x,b.g.position.z+3,t)-h)*.4);
  }
  /* buoys */
  if(window.__buoys){
    const list=window.__buoys,mm=window.__buoyMesh;
    for(let i=0;i<list.length;i++){
      const it=list[i],home=it.home;
      const h=waveH(home.x,home.z,t);
      _p.set(home.x+it.off.x,h+it.off.y+.2,home.z+it.off.z);
      _q.setFromEuler(new THREE.Euler(waveH(home.x,home.z+3,t)*.2,0,-waveH(home.x+3,home.z,t)*.2));
      _m.compose(_p,_q,_s.set(1,1,1));mm.setMatrixAt(i,_m);
    }
    mm.instanceMatrix.needsUpdate=true;
  }

  /* beacon */
  beaconGroup.rotation.y=t*.95;
  lamp.position.set(1.2,18.5,42);
  lamp.color.copy(cur.sun).lerp(new THREE.Color('#ffd39a'),.6);

  /* cargo davit */
  davitArm.rotation.y=Math.sin(t*.24)*.42+.3;
  const lift=(Math.sin(t*.55)*.5+.5);
  const dropY=lerp(11.4,4.6,lift);
  for(let i=0;i<3;i++){
    _p.set(davitHook.x,dropY-(i===0?0:i===1?1.1:2.2)*0+ (i===1?.9:0)*0 + (i===2?1.9:0)+(i===0?0:0)+ (i===1?-1.0:0),davitHook.z+Math.sin(davitArm.rotation.y)*6);
    _p.z=davitHook.z+Math.sin(davitArm.rotation.y)*6;
    _p.y=dropY-(i===1?-1.0:0)-(i===2?-2.0:0);
    _p.x=davitHook.x+Math.cos(davitArm.rotation.y)*6-6*Math.cos(davitArm.rotation.y)+6*Math.cos(davitArm.rotation.y);
    _s.set(i===2?1.6:.18,i===2?1.6:.55,i===2?1.6:.18);
    if(i===2)_p.y=dropY-1.0;
    _m.compose(_p,_q.identity(),_s);crateMesh.setMatrixAt(i,_m);
  }
  crateMesh.instanceMatrix.needsUpdate=true;

  /* smoke */
  for(let i=0;i<smokeN;i++){
    const p=puffs[i],src=sources[p.s];
    p.l+=dt/p.sp;if(p.l>3.4)p.l=0;
    const f=p.l/3.4,sc=lerp(.5,2.6,f);
    _p.set(src.x+Math.sin(p.sw+f*3+t*.5)*(.6+f*3.2)+f*1.5,src.y+p.l*1.7,src.z+Math.cos(p.sw+f*2.4+t*.4)*(.5+f*2.4));
    const fade=Math.sin(f*Math.PI);
    _m.compose(_p,_q.setFromEuler(new THREE.Euler(f,f*1.3,0)),_s.set(sc,sc,sc));
    smoke.setMatrixAt(i,_m);
    const c=smoke.instanceColor?smoke.instanceColor:null;
  }
  smoke.instanceMatrix.needsUpdate=true;
  matSmoke.opacity=.62;
  {const c=new THREE.Color();for(let i=0;i<smokeN;i++){const f=puffs[i].l/3.4;
    c.setRGB(lerp(1,.62,f),lerp(1,.60,f),lerp(1,.60,f));smoke.setColorAt(i,c);}
   smoke.instanceColor.needsUpdate=true;}

  /* clouds drift */
  cloudGroup.position.x+=dt*1.05;
  if(cloudGroup.position.x>110)cloudGroup.position.x-=220;

  /* gulls */
  if(swState.birds){
    for(let i=0;i<gullN;i++){
      const g=gulls[i],a=t*g.sp+g.ph;
      const x=g.c.x+Math.cos(a)*g.r,z=g.c.z+Math.sin(a)*g.r*.8;
      const y=g.c.y+Math.sin(t*.6+g.ph)*2.2;
      const hd=Math.atan2(Math.cos(a)*g.r,-Math.sin(a)*g.r*.8);
      const flap=Math.sin(t*g.fl+g.ph)*g.amp*(Math.sin(t*.33+g.ph)>-.2?1:.16);
      const white=new THREE.Color('#f3f0e8');
      _q.setFromEuler(new THREE.Euler(0,hd,0));
      _m.compose(_p.set(x,y,z),_q,_s.set(.4,.4,1.5));gullMesh.setMatrixAt(i*4,_m);
      _q.setFromEuler(new THREE.Euler(0,hd,flap));
      _m.compose(_p.set(x,y,z),_q,_s.set(2.2,.12,.55));gullMesh.setMatrixAt(i*4+1,_m);
      _q.setFromEuler(new THREE.Euler(0,hd,-flap));
      _m.compose(_p.set(x,y,z),_q,_s.set(2.2,.12,.55));gullMesh.setMatrixAt(i*4+2,_m);
      _q.setFromEuler(new THREE.Euler(0,hd,0));
      _m.compose(_p.set(x,y+.1,z+.85),_q,_s.set(.2,.2,.4));gullMesh.setMatrixAt(i*4+3,_m);
      for(let k=0;k<4;k++){
        const c=k===3?new THREE.Color('#e0a83c'):k===1?new THREE.Color('#c9ced4'):white;
        gullMesh.setColorAt(i*4+k,c);
      }
    }
    gullMesh.instanceMatrix.needsUpdate=true;gullMesh.instanceColor.needsUpdate=true;
  }

  /* people */
  for(let i=0;i<people.length;i++){
    const p=people[i];
    if(p.path){p.s+=p.sp*dt;let s=p.s%p.path.total;
      for(const[A,B,L]of p.path.segs){
        if(s<=L){_a.copy(A);_b.copy(B).sub(A).multiplyScalar(s/(L||1)).add(A);break;}s-=L;_a.copy(A).copy(_b);}
      _b.y=_a.y;
    }else{_a.copy(p.at);_b.copy(p.at);}
    const dir=Math.atan2(_b.x-_a.x,_b.z-_a.z)||p.face||0;
    const step=p.sp?Math.sin(p.s*4.6):0;
    const ox=p.dog?.0:0;
    for(let k=0;k<4;k++){
      if(p.dog&&k>2)continue;
      const pt=PART[k];
      const sc=p.dog?[.7,.5,.6,.5]:[1,1,1,1];
      _p.set(_a.x+(k===0?step*.12:0),_a.y+pt.y*sc[k]+(p.sp?Math.abs(step)*.09:0),_a.z+(k===0?0:0));
      _q.setFromEuler(new THREE.Euler(0,dir,0));
      _s.set(pt.w*(p.dog?1.1:1),pt.h*(p.dog?(k===0?.75:1):1),pt.d*(p.dog?1.4:1));
      if(p.dog){_p.y=(k===0?pt.y*.8:pt.y*.62);}
      _m.compose(_p,_q,_s);personMesh.setMatrixAt(i*4+k,_m);
    }
  }
  personMesh.instanceMatrix.needsUpdate=true;

  /* hotspot projection */
  if(swState.marks){
    const v=new THREE.Vector3();
    HOT.forEach((h,i)=>{
      v.copy(h.p).project(camera);
      const vis=v.z<1&&v.x>-1.05&&v.x<1.05&&v.y>-1.05&&v.y<1.05;
      h.el.style.opacity=vis?clamp(1.5-Math.abs(v.z)/1.6,.15,1):0;
      h.el.style.pointerEvents=vis?'auto':'none';
      if(vis)h.el.style.transform=`translate(-50%,-50%) translate(${(v.x*.5+.5)*innerWidth}px,${(-v.y*.5+.5)*innerHeight}px)`;
    });
  }

  controls.update();
  renderer.render(scene,camera);

  /* hud numbers */
  fpsAcc+=dt;fpsN++;
  if(fpsAcc>.5){
    document.getElementById('t-fps').textContent=Math.round(fpsN/fpsAcc);
    document.getElementById('t-tri').textContent=renderer.info.render.triangles.toLocaleString('en-GB');
    fpsAcc=0;fpsN=0;
  }
}
renderer.setAnimationLoop(loop);
requestAnimationFrame(()=>{setTimeout(()=>{
  document.getElementById('boot').classList.add('gone');
  select(0);
},260);});

/* readouts tick */
let wind=11,tide=2.4;
setInterval(()=>{
  wind=clamp(wind+(Math.random()*3-1.5),6,21);
  tide=clamp(tide+ (Math.random()*.08-.04),.4,4.6);
  const swell=(uAmp.value*.55).toFixed(1);
  document.getElementById('s-wind').textContent='SW '+wind.toFixed(0);
  document.getElementById('s-tide').textContent=(tide>=0?'+':'')+tide.toFixed(1);
  document.getElementById('s-swell').textContent=swell+'m';
},1500);

addEventListener('resize',()=>{
  camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight);
});
addEventListener('keydown',e=>{
  const k=e.key;
  if('1234'.includes(k)){document.querySelector(`#watch button[data-w="${k-1}"]`).click();}
  if(k===' '){e.preventDefault();swState.orbit=!swState.orbit;syncSwitches();}
  if(k.toLowerCase()==='r')$('#reset').click();
});
</script>
</body>
</html>
```

**A few things worth poking at**

- **Hour** buttons cross‑fade sky, fog, sea colour, lamp glass and light direction (keys `1`–`4`); at *Night lamps* the lighthouse beam, quay lamps and cottage windows all carry the scene.
- **Sea state** drives the shader‑displaced voxel sea — and the barque, the boats and every buoy sample that same wave function, so she rolls and pitches with the swell.
- **Canvas set** hoists the square sails, jibs and spanker from the yards; drop it to zero and she's furled like a ship that's finished her passage.
- Click a **point of call** in the lower‑left index (or a marker on the chart) to fly the camera and read that spot's entry in the harbor book.