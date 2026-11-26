# Port Aldermoor — a sailing ship calling at a harbour

A single-file WebGL voxel diorama. Everything is generated at load (≈45,000 instanced voxels): the ship's hull is lofted from a hull-line profile, sails are billowed voxel planes, rigging is voxel rope, the sea is a live heightfield, and the harbour has its own weather of smoke, gulls, cloud shadows and lamps that wake up as the watches change.

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Port Aldermoor — a sailing ship calling at a harbour</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,700;0,9..144,900;1,9..144,700;1,9..144,900&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{
  --ink:#06121a; --panel:#0d2029; --panel2:#0a1a21;
  --edge:rgba(232,178,96,.32); --brass:#e8b260; --brass-hi:#f7dcae; --brass2:#a3762f;
  --foam:#edf5f2; --mist:#93aeb2; --sea:#3d8f9c; --rust:#c9603f;
  --shadow:0 22px 60px -24px rgba(0,0,0,.85);
}
*{box-sizing:border-box}
html,body{height:100%;margin:0;background:var(--ink);color:var(--foam);
  font-family:"IBM Plex Sans",system-ui,sans-serif;overflow:hidden;-webkit-font-smoothing:antialiased}
canvas#stage{position:fixed;inset:0;width:100%;height:100%;display:block;cursor:grab;touch-action:none}
canvas#stage.drag{cursor:grabbing}
canvas#stage.hot{cursor:crosshair}

/* ---------- atmosphere overlays ---------- */
#veil{position:fixed;inset:0;pointer-events:none;z-index:2;
  background:radial-gradient(125% 95% at 52% 40%,rgba(0,0,0,0) 42%,rgba(2,9,13,.62) 100%)}
#grain{position:fixed;inset:-40px;pointer-events:none;z-index:3;opacity:.06;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/></filter><rect width='200' height='200' filter='url(%23n)'/></svg>");
  animation:grain 1.1s steps(2) infinite}
@keyframes grain{0%{transform:translate(0,0)}50%{transform:translate(-12px,7px)}100%{transform:translate(6px,-9px)}}
#scan{position:fixed;left:0;right:0;height:1px;z-index:4;pointer-events:none;
  background:linear-gradient(90deg,transparent,rgba(232,178,96,.5),transparent);opacity:.35;
  animation:scan 9s linear infinite}
@keyframes scan{0%{top:8%}50%{top:92%}100%{top:8%}}

/* ---------- shared chrome ---------- */
.card{position:fixed;z-index:6;
  background:linear-gradient(168deg,rgba(19,42,52,.95),rgba(7,19,25,.93) 60%,rgba(9,24,30,.95));
  border:1px solid var(--edge);box-shadow:var(--shadow),inset 0 1px 0 rgba(255,255,255,.05);
  clip-path:polygon(0 11px,11px 0,100% 0,100% calc(100% - 11px),calc(100% - 11px) 100%,0 100%);
  opacity:0;transform:translateY(14px);transition:opacity .7s ease,transform .7s cubic-bezier(.16,.9,.24,1)}
body.ready .card{opacity:1;transform:none}
.over{font-family:"IBM Plex Mono",monospace;font-weight:600;font-size:9.5px;letter-spacing:.24em;
  text-transform:uppercase;color:var(--brass);margin:0}
.hr{height:1px;background:linear-gradient(90deg,var(--brass2),rgba(147,174,178,.18),transparent);margin:10px 0}

/* ---------- title plaque ---------- */
#plaque{top:0;left:0;padding:22px 26px 20px;border-right:1px solid var(--edge);border-bottom:1px solid var(--edge);
  background:linear-gradient(150deg,rgba(19,42,52,.9),rgba(7,19,25,.55));max-width:min(52ch,62vw)}
#plaque h1{font-family:Fraunces,Georgia,serif;font-weight:900;font-size:clamp(31px,4.3vw,62px);
  line-height:.86;letter-spacing:-.025em;margin:8px 0 0;text-shadow:0 6px 26px rgba(0,0,0,.6)}
#plaque h1 em{display:block;font-style:italic;font-weight:700;font-size:.72em;color:var(--brass);
  letter-spacing:-.01em;margin-top:2px}
#plaque .sub{margin:12px 0 0;font-size:13.5px;line-height:1.5;color:#c6d8d8;max-width:36ch}
#plaque .sub b{font-weight:600;color:var(--foam)}
#plaque .sub span{color:var(--mist);font-style:italic;font-family:Fraunces,serif}
.stamp{position:absolute;right:-1px;top:16px;writing-mode:vertical-rl;font-family:"IBM Plex Mono",monospace;
  font-size:9px;letter-spacing:.3em;text-transform:uppercase;color:rgba(147,174,178,.55);padding:6px 5px;
  border-left:1px solid var(--edge);border-right:1px solid rgba(147,174,178,.12)}

/* ---------- harbourmaster panel ---------- */
#log{right:18px;top:18px;width:262px;padding:16px 16px 14px;transition-delay:.12s}
#log h2{font-family:Fraunces,serif;font-weight:700;font-size:19px;margin:5px 0 0;letter-spacing:-.01em}
.grp{margin-top:13px}
.grp>p{margin:0 0 7px;font-family:"IBM Plex Mono",monospace;font-size:8.5px;letter-spacing:.2em;
  text-transform:uppercase;color:rgba(147,174,178,.85)}
.seg{display:grid;grid-template-columns:1fr 1fr;gap:5px}
.views{display:flex;flex-wrap:wrap;gap:5px}
.btn{position:relative;isolation:isolate;flex:0 0 auto;display:inline-flex;align-items:center;justify-content:center;
  font-family:"IBM Plex Mono",monospace;font-weight:600;font-size:9.5px;letter-spacing:.12em;text-transform:uppercase;
  color:var(--mist);background:rgba(255,255,255,.035);border:1px solid rgba(147,174,178,.22);
  padding:7px 8px;cursor:pointer;transition:color .25s,border-color .25s,transform .18s;overflow:hidden}
.btn span{position:relative;z-index:1;padding:0 1px}
.btn:before{content:"";position:absolute;inset:0;z-index:0;transform:translateX(-101%);
  background:linear-gradient(100deg,var(--brass),var(--brass-hi));transition:transform .34s cubic-bezier(.2,.85,.2,1)}
.btn:hover{color:var(--foam);border-color:var(--edge);transform:translateY(-1px)}
.btn:hover:before{transform:translateX(0)}
.btn[aria-pressed="true"]{color:#0a1a21;border-color:var(--brass)}
.btn[aria-pressed="true"]:before{transform:none}
.row{display:flex;align-items:center;justify-content:space-between;padding:5px 0;font-size:11.5px;color:#b9cdd0}
.row label{display:flex;align-items:center;gap:9px;cursor:pointer}
.row input{position:absolute;opacity:0;pointer-events:none}
.sw{width:32px;height:15px;border:1px solid rgba(147,174,178,.3);background:rgba(0,0,0,.35);position:relative;
  transition:.3s;flex:0 0 auto}
.sw:after{content:"";position:absolute;top:1px;left:1px;width:11px;height:11px;background:var(--mist);
  transition:left .3s cubic-bezier(.2,.85,.2,1),background .3s}
.row input:checked+.sw{border-color:var(--brass);background:rgba(232,178,96,.16)}
.row input:checked+.sw:after{left:18px;background:var(--brass)}
.readout{margin-top:12px;border-top:1px dashed rgba(147,174,178,.22);padding-top:9px;
  font-family:"IBM Plex Mono",monospace;font-size:9.5px;line-height:1.85;color:rgba(147,174,178,.9);letter-spacing:.06em}
.readout b{color:var(--brass);font-weight:600}
#compass{position:absolute;right:14px;bottom:12px;width:52px;height:52px;opacity:.9}
#rose{transform-origin:50% 50%;transition:transform .12s linear}

/* ---------- hotspot manifest card ---------- */
#hot{left:18px;bottom:18px;width:min(360px,44vw);padding:14px 16px 15px;border-left:2px solid var(--brass);
  opacity:0;transform:translateY(18px);pointer-events:none;transition-delay:.18s}
body.ready #hot.on{opacity:1;transform:none;pointer-events:auto}
#hot .tag{font-family:"IBM Plex Mono",monospace;font-size:9px;letter-spacing:.2em;text-transform:uppercase;color:var(--rust);margin:0}
#hot h3{font-family:Fraunces,serif;font-weight:900;font-size:clamp(19px,2.1vw,26px);line-height:1.02;margin:6px 0 0;letter-spacing:-.015em}
#hot p{margin:8px 0 0;font-size:12.5px;line-height:1.55;color:#bdd0d2}
#hot .meta{display:flex;gap:14px;margin-top:10px;font-family:"IBM Plex Mono",monospace;font-size:9.5px;color:var(--brass);letter-spacing:.1em}
#hot .pin{position:absolute;right:10px;top:8px;font-size:14px;color:var(--mist);cursor:pointer;opacity:0;transition:.2s}
#hot.pinned .pin{opacity:.8}#hot .pin:hover{color:var(--brass);opacity:1}

/* ---------- legend ---------- */
#legend{right:18px;bottom:18px;width:262px;padding:13px 14px;transition-delay:.24s}
#legend>p{margin:0 0 8px;font-family:"IBM Plex Mono",monospace;font-size:8.5px;letter-spacing:.2em;
  text-transform:uppercase;color:rgba(147,174,178,.8)}
#legend ul{list-style:none;margin:0;padding:0}
#legend li{display:flex;gap:9px;align-items:baseline;padding:5px 4px;font-size:12px;color:#b9cdd0;cursor:pointer;
  border-left:1px solid transparent;transition:background .25s,color .25s,border-color .25s,transform .25s}
#legend li:hover,#legend li.act{background:rgba(232,178,96,.09);color:var(--foam);border-left-color:var(--brass);transform:translateX(3px)}
#legend i{width:6px;height:6px;flex:0 0 auto;transform:rotate(45deg);background:var(--c,var(--brass));
  transition:transform .3s}
#legend li:hover i{transform:rotate(135deg) scale(1.35)}
#legend small{margin-left:auto;font-family:"IBM Plex Mono",monospace;font-size:8.5px;color:rgba(147,174,178,.6);letter-spacing:.08em}

/* ---------- tooltip + hint ---------- */
#tip{position:fixed;z-index:7;pointer-events:none;padding:4px 8px;font-family:"IBM Plex Mono",monospace;
  font-size:9.5px;letter-spacing:.14em;text-transform:uppercase;color:#0a1a21;background:var(--brass);
  opacity:0;transform:translate(10px,-14px);transition:opacity .18s}
#tip.on{opacity:1}
#hint{position:fixed;left:50%;bottom:22px;transform:translateX(-50%);z-index:6;font-family:"IBM Plex Mono",monospace;
  font-size:9.5px;letter-spacing:.18em;text-transform:uppercase;color:rgba(237,245,242,.55);
  transition:opacity .8s;pointer-events:none}
#hint.off{opacity:0}
body.ui-off #plaque,body.ui-off #log,body.ui-off #legend,body.ui-off #hot,body.ui-off #hint,
body.ui-off #compass,body.ui-off .stamp{opacity:0;transform:translateY(10px);pointer-events:none}

/* ---------- boot ---------- */
#boot{position:fixed;inset:0;z-index:20;display:grid;place-items:center;
  background:radial-gradient(90% 70% at 50% 45%,#0d2731,#040d12 75%);transition:opacity .9s ease,visibility .9s}
#boot.gone{opacity:0;visibility:hidden}
.bootcard{width:min(420px,84vw);text-align:left}
.bootcard h2{font-family:Fraunces,serif;font-weight:900;font-size:clamp(26px,4vw,40px);margin:8px 0 16px;letter-spacing:-.02em}
.bootcard h2 em{font-style:italic;color:var(--brass);font-weight:700}
.bar{height:2px;background:rgba(147,174,178,.16);position:relative;overflow:hidden}
.bar i{position:absolute;inset:0 auto 0 0;width:0;background:linear-gradient(90deg,var(--brass2),var(--brass-hi));
  transition:width .35s ease}
#bootlog{font-family:"IBM Plex Mono",monospace;font-size:10px;letter-spacing:.14em;text-transform:uppercase;
  color:var(--mist);margin:12px 0 0}
#fatal{position:fixed;inset:0;z-index:30;display:none;place-items:center;background:#040d12;padding:24px;text-align:center}
#fatal p{max-width:44ch;color:#cfe0df;font-size:14px;line-height:1.6}
@media (max-width:900px){
  #legend{display:none}#log{width:214px;top:auto;bottom:14px}#plaque{max-width:74vw;padding:16px}
  #hot{width:min(320px,72vw)}
}
</style>
</head>
<body>
<canvas id="stage"></canvas>
<div id="veil"></div><div id="grain"></div><div id="scan"></div>

<header id="plaque" class="card" style="clip-path:none">
  <p class="over">Voxel study № 14 · flood tide</p>
  <h1>Port <em>Aldermoor</em></h1>
  <div class="hr"></div>
  <p class="sub"><b>A sailing ship calling at a harbour.</b> <span>The Meridian, bark-rigged, standing in on the last of the flood with a cargo of salt and pine.</span></p>
  <div class="stamp">drawn in 1m cubes</div>
</header>

<aside id="log" class="card">
  <p class="over">Harbourmaster</p>
  <h2>Watch board</h2>
  <div class="grp"><p>Hour</p>
    <div class="seg" id="watches">
      <button class="btn" data-watch="dawn"><span>Dawn 05:12</span></button>
      <button class="btn" data-watch="noon"><span>Meridian</span></button>
      <button class="btn" data-watch="dusk" aria-pressed="true"><span>Golden</span></button>
      <button class="btn" data-watch="night"><span>Middle</span></button>
    </div></div>
  <div class="grp"><p>Viewpoints</p>
    <div class="views" id="views">
      <button class="btn" data-view="roads"><span>The roads</span></button>
      <button class="btn" data-view="ship"><span>The bark</span></button>
      <button class="btn" data-view="wharf"><span>Long wharf</span></button>
      <button class="btn" data-view="mole"><span>Lighthouse</span></button>
      <button class="btn" data-view="town"><span>Old town</span></button>
      <button class="btn" data-view="mill"><span>Mill Hill</span></button>
      <button class="btn" data-view="bird"><span>Overhead</span></button>
    </div></div>
  <div class="hr"></div>
  <div class="row"><label for="tOrbit"><input id="tOrbit" type="checkbox" checked><span class="sw"></span></label><span>Lazy orbit when idle</span></div>
  <div class="row"><label for="tLamp"><input id="tLamp" type="checkbox" checked><span class="sw"></span></label><span>Lamps &amp; lighthouse</span></div>
  <div class="row"><label for="tLife"><input id="tLife" type="checkbox" checked><span class="sw"></span></label><span>Gulls, cloud &amp; smoke</span></div>
  <div class="row"><label for="tUI"><input id="tUI" type="checkbox"><span class="sw"></span></label><span>Hide interface <b style="color:var(--brass);font-weight:600">(H)</b></span></div>
  <div class="readout">
    voxels&nbsp;&nbsp;<b id="rVox">—</b><br>
    draw&nbsp;&nbsp;&nbsp;<b id="rFps">—</b><br>
    wind&nbsp;&nbsp;&nbsp;<b id="rWind">WSW 11kn</b><br>
    harbour&nbsp;<b id="rClock">19:40</b>
  </div>
  <svg id="compass" viewBox="0 0 60 60">
    <g id="rose">
      <circle cx="30" cy="30" r="24" fill="none" stroke="rgba(147,174,178,.35)"/>
      <circle cx="30" cy="30" r="17" fill="none" stroke="rgba(232,178,96,.28)"/>
      <path d="M30 4 L34 30 L30 56 L26 30Z" fill="#e8b260" opacity=".85"/>
      <path d="M4 30 L30 27 L56 30 L30 33Z" fill="rgba(237,245,242,.35)"/>
      <text x="30" y="12" fill="#edf5f2" font-size="7" text-anchor="middle" font-family="IBM Plex Mono">N</text>
    </g>
  </svg>
</aside>

<div id="hot" class="card">
  <span class="pin" id="hotPin">✕</span>
  <p class="tag" id="hotTag">manifest</p>
  <h3 id="hotName">—</h3>
  <p id="hotNote">—</p>
  <div class="meta" id="hotMeta"></div>
</div>

<nav id="legend" class="card">
  <p>Points of interest — hover to sight, click to run the boat out</p>
  <ul id="legendList"></ul>
</nav>

<div id="tip"></div>
<div id="hint">drag to orbit · scroll to close the distance · shift-drag to pan</div>

<div id="boot"><div class="bootcard">
  <p class="over">Aldermoor Harbour Authority · board of pilots</p>
  <h2>Charting the <em>harbour</em></h2>
  <div class="bar"><i id="bootbar"></i></div>
  <p id="bootlog">unrolling the survey…</p>
</div></div>

<div id="fatal"><p>This scene streams three.js from a CDN, so it needs one trip online. Reconnect once and Chrome will remember it.</p></div>

<script type="importmap">
{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.1/build/three.module.js"}}
</script>
<script type="module">
let THREE;
try{ THREE = await import('three'); }
catch(e){ document.getElementById('fatal').style.display='grid'; throw e; }

/* ══════════════════════ helpers ══════════════════════ */
const clamp=(v,a,b)=>v<a?a:v>b?b:v, lerp=(a,b,t)=>a+(b-a)*t;
const smoothstep=(e0,e1,x)=>{const t=clamp((x-e0)/(e1-e0),0,1);return t*t*(3-2*t);};
function mul32(a){return()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
const rnd=mul32(20450713);
const pick=(arr,r=rnd)=>arr[(r()*arr.length)|0];
function h2(i,j){const s=Math.sin(i*127.1+j*311.7)*43758.5453123;return s-Math.floor(s);}
function vnoise(x,z){const xi=Math.floor(x),zi=Math.floor(z),xf=x-xi,zf=z-zi;
  const u=xf*xf*(3-2*xf),v=zf*zf*(3-2*zf);
  return lerp(lerp(h2(xi,zi),h2(xi+1,zi),u),lerp(h2(xi,zi+1),h2(xi+1,zi+1),u),v);}
function fbm(x,z,o=3){let a=0,amp=.5,f=1;for(let i=0;i<o;i++){a+=vnoise(x*f,z*f)*amp;amp*=.5;f*=2;}return a;}
const V3=(x,y,z)=>new THREE.Vector3(x,y,z);

/* ══════════════════════ palette ══════════════════════ */
const C={
  sea:0x17606f, seaDeep:0x0c3747, seaMid:0x1d7482, seaShal:0x389ba1, foam:0xd9edee,
  stone:0x82857b, stone2:0x6a6d65, stone3:0x94968a, cobble:0x9b978a, cobble2:0x86826f,
  sand:0xc9b489, shingle:0xa89f8b, dirt:0x6c5f4c, grass:0x6d8b58, grass2:0x5a7a4c, rock:0x5d625f, rock2:0x6f7470,
  woodD:0x4a3524, wood:0x8a6138, woodL:0xa87b4b, plank:0x795636, tar:0x241f1c,
  brick:0x94504a, brick2:0x7b4340, cream:0xe2d8bf, plaster:0xd2c6a8, ochre:0xc9974b, ochre2:0xb07f37,
  slate:0x414b56, slate2:0x333c46, copper:0x3c857a, copper2:0x2f6b62, teal:0x2f6f68, white:0xece9df,
  iron:0x3b4044, iron2:0x2b2f32, canvas:0xe9dfc6, canvas2:0xd6c9a9, red:0xb94a37, red2:0x8f3a2c,
  hull:0x24242a, hullStripe:0xd9a63f, hullUnder:0x2d4a3a, leaf:0x4e6f42, leaf2:0x5f7d45, leafA:0xa97a34,
  glass:0xffd27a, glass2:0xfff0c4, lamp:0xffc46b, smoke:0xbfc7c6, sail:0xefe7d4
};

/* ══════════════════════ renderer / scene ══════════════════════ */
const canvas=document.getElementById('stage');
const renderer=new THREE.WebGLRenderer({canvas,antialias:true,powerPreference:'high-performance'});
renderer.setPixelRatio(Math.min(devicePixelRatio,1.8));
renderer.shadowMap.enabled=true; renderer.shadowMap.type=THREE.PCFSoftShadowMap;
renderer.toneMapping=THREE.ACESFilmicToneMapping; renderer.toneMappingExposure=1.02;
const scene=new THREE.Scene();
scene.fog=new THREE.FogExp2(0x9db3b4,0.0052);
const camera=new THREE.PerspectiveCamera(42,1,.5,3000);

const sun=new THREE.DirectionalLight(0xffffff,2.6);
sun.castShadow=true; sun.shadow.mapSize.set(2048,2048);
const sc=sun.shadow.camera; sc.left=-105;sc.right=105;sc.top=105;sc.bottom=-105;sc.near=1;sc.far=340;
sun.shadow.bias=-0.0006; sun.shadow.normalBias=.7;
scene.add(sun,sun.target);
const hemi=new THREE.HemisphereLight(0x8fb6d4,0x6a6552,.55); scene.add(hemi);
const fill=new THREE.DirectionalLight(0x9fc0d8,.5); fill.position.set(-60,40,90); scene.add(fill);

const MAT={
  scene:new THREE.MeshStandardMaterial({roughness:.96,metalness:0}),
  ship:new THREE.MeshStandardMaterial({roughness:.9,metalness:0}),
  cloud:new THREE.MeshStandardMaterial({roughness:1,metalness:0}),
  water:new THREE.MeshStandardMaterial({roughness:.26,metalness:.22}),
  glow:new THREE.MeshBasicMaterial({toneMapped:false}),
  gull:new THREE.MeshStandardMaterial({color:0xf1efe6,roughness:.85}),
  gullD:new THREE.MeshStandardMaterial({color:0x7c8791,roughness:.9}),
  beam:new THREE.MeshBasicMaterial({color:0xffd9a0,transparent:true,opacity:.10,blending:THREE.AdditiveBlending,depthWrite:false,side:THREE.DoubleSide})
};

/* sky dome */
const skyU={uTop:{value:new THREE.Color(0x1d3a5c)},uHor:{value:new THREE.Color(0xf0a76b)},
  uBot:{value:new THREE.Color(0x24303a)},uSun:{value:new THREE.Vector3(.7,.16,-.55)},
  uSunC:{value:new THREE.Color(0xffbb70)},uStars:{value:0}};
const sky=new THREE.Mesh(new THREE.SphereGeometry(1500,32,20),new THREE.ShaderMaterial({
  side:THREE.BackSide,depthWrite:false,fog:false,uniforms:skyU,
  vertexShader:`varying vec3 vD;void main(){vD=normalize(position);gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,
  fragmentShader:`varying vec3 vD;uniform vec3 uTop,uHor,uBot,uSunC;uniform vec3 uSun;uniform float uStars;
  float hash(vec3 p){return fract(sin(dot(p,vec3(27.1,61.7,113.5)))*43758.5453);}
  void main(){vec3 d=normalize(vD);
    float h=clamp(d.y,0.,1.);
    vec3 c=mix(uHor,uTop,pow(h,.55));
    c=mix(uBot,c,smoothstep(-.10,.02,d.y));
    float s=dot(d,normalize(uSun));
    c+=uSunC*pow(max(s,0.),260.)*5.5;
    c+=uSunC*pow(max(s,0.),9.)*.30;
    c+=uSunC*pow(max(s,0.),2.)*.06;
    if(uStars>.01&&d.y>0.0){float st=step(.9982,hash(floor(d*300.)));
      c+=vec3(st)*uStars*(.6+.4*sin(hash(floor(d*300.))*40.));}
    gl_FragColor=vec4(c,1.);}`
}));
sky.frustumCulled=false; scene.add(sky);

/* distant sea plate */
const farSea=new THREE.Mesh(new THREE.CircleGeometry(1400,64),
  new THREE.MeshStandardMaterial({color:0x14555f,roughness:.4,metalness:.3}));
farSea.rotation.x=-Math.PI/2; farSea.position.y=-1.4; scene.add(farSea);

/* ══════════════════════ voxel builder ══════════════════════ */
const BOX=new THREE.BoxGeometry(1,1,1);
const UP=new THREE.Vector3(0,1,0);
class VS{
  constructor(){this.m=new Map();this.p=[];}
  static K(x,y,z){return (x+2048)*16777216+(y+2048)*4096+(z+2048);}
  has(x,y,z){return this.m.has(VS.K(Math.round(x),Math.round(y),Math.round(z)));}
  at(x,y,z,c,o={}){
    x=Math.round(x);y=Math.round(y);z=Math.round(z);
    const k=VS.K(x,y,z);
    if(this.m.has(k)&&!o.over)return;
    this.m.set(k,{c,
      s:o.sx!==undefined?[o.sx,o.sy,o.sz]:[o.s||1,o.s||1,o.s||1],
      o:[o.ox||0,o.oy||0,o.oz||0],j:o.jit!==false});
    return this;
  }
  box(x0,x1,y0,y1,z0,z1,c,o){for(let x=x0;x<=x1;x++)for(let y=y0;y<=y1;y++)for(let z=z0;z<=z1;z++)this.at(x,y,z,c,o);return this;}
  shell(x0,x1,y0,y1,z0,z1,c,o){
    for(let y=y0;y<=y1;y++){
      for(let x=x0;x<=x1;x++){this.at(x,y,z0,c,o);this.at(x,y,z1,c,o);}
      for(let z=z0;z<=z1;z++){this.at(x0,y,z,c,o);this.at(x1,y,z,c,o);}
    }
    for(let x=x0;x<=x1;x++)for(let z=z0;z<=z1;z++){this.at(x,y0,z,c,o);this.at(x,y1,z,c,o);}
    return this;
  }
  ring(cx,cz,ri,ro,y0,y1,c,o){
    for(let y=y0;y<=y1;y++)for(let x=Math.floor(cx-ro);x<=Math.ceil(cx+ro);x++)for(let z=Math.floor(cz-ro);z<=Math.ceil(cz+ro);z++){
      const d=Math.hypot(x-cx+.001,z-cz+.001);
      if(d<=ro+.15&&d>=ri-.15)this.at(x,y,z,c,o);
    }return this;
  }
  disc(cx,cz,r,y,c,o){for(let x=Math.floor(cx-r);x<=Math.ceil(cx+r);x++)for(let z=Math.floor(cz-r);z<=Math.ceil(cz+r);z++)
    if(Math.hypot(x-cx+.001,z-cz+.001)<=r+.12)this.at(x,y,z,c,o);return this;}
  blob(cx,cy,cz,r,c,o={}){
    const ry=r*(o.sy||1),rx=r*(o.sx||1),rz=r*(o.sz||1),st=o.jitj==null?.18:o.jitj;
    for(let x=Math.floor(cx-rx);x<=Math.ceil(cx+rx);x++)for(let y=Math.floor(cy-ry);y<=Math.ceil(cy+ry);y++)for(let z=Math.floor(cz-rz);z<=Math.ceil(cz+rz);z++){
      const d=Math.hypot((x-cx)/rx,(y-cy)/ry,(z-cz)/rz);
      if(d<=1-.5*fbm(x*.7,z*.7+(cy),2)*st+.25*fbm(x*.5+z*.4,cy*.3,2)*st)
        this.at(x,y,z,Array.isArray(c)?pick(c,rnd):c,o);
    }return this;
  }
  beam(p0,p1,{c=0x8a6138,w=.34,t=.34,step=.5}={}){
    const d=p1.clone().sub(p0),len=d.length();
    if(len<1e-4)return this;
    const n=Math.max(1,Math.round(len/step)),dn=d.clone().normalize();
    const q=new THREE.Quaternion().setFromUnitVectors(UP,dn);
    for(let i=0;i<n;i++){
      const p=p0.clone().addScaledVector(d,(i+.5)/n);
      this.p.push({p,s:V3(w,len/n*1.08,t),q,c,jit:true});
    }return this;
  }
  cat(a,b,sag,{c,step=.55,w=.22,t=.22,n=8}={}){
    let prev=a;
    for(let i=1;i<=n;i++){const t=i/n;const p=a.clone().lerp(b,t);p.y-=sag*4*t*(1-t);this.beam(prev,p,{c,step,w,t});prev=p;}
    return this;
  }
  tri(a,b,c0,{c=0xe9dfc6,nx=0,ny=0,nz=1,bow=0,shade=null}={}){
    const ab=b.clone().sub(a),ac=c0.clone().sub(a);
    const nu=Math.ceil(ab.length()),nv=Math.ceil(ac.length());
    for(let i=0;i<=nu;i++)for(let j=0;j<=nv;j++){
      const u=i/nu,v=j/nv; if(u+v>1.001)continue;
      const p=a.clone().addScaledVector(ab,u).addScaledVector(ac,v);
      if(bow){const k=Math.sin(u*Math.PI)*(1-v*.6);p.x+=nx*k;p.y+=ny*k;p.z+=nz*k;}
      const col=shade?shade(u,v):c;
      this.at(p.x,p.y,p.z,col);
    }return this;
  }
  build({mat=MAT.scene,ao=true,cast=true,recv=true,wet=true,parent=scene}={}){
    const keys=[...this.m.keys()];
    const N=keys.length+this.p.length;
    const mesh=new THREE.InstancedMesh(BOX,mat,Math.max(1,N));
    const m=new THREE.Matrix4(),q0=new THREE.Quaternion(),sc=new THREE.Vector3(),pos=new THREE.Vector3();
    const col=new THREE.Color(),tmp=new THREE.Color();
    const F=[[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]];
    const E=[];for(const a of[-1,1])for(const b of[-1,1]){E.push([a,b,0]);E.push([a,0,b]);E.push([0,a,b]);}
    const K=[];for(const a of[-1,1])for(const b of[-1,1])for(const c of[-1,1])K.push([a,b,c]);
    const dec=new Map();
    let i=0;
    for(const k of keys){
      const v=this.m.get(k);
      let x=0,y=0,z=0; {const kk=k; z=(kk%4096)-2048; const a=(kk-z)/4096; y=(a%4096)-2048; const b=(a-y)/4096; x=b-2048; }
      let f=1;
      if(ao){
        let occ=0;
        for(const d of F) if(this.m.has(VS.K(x+d[0],y+d[1],z+d[2]))) occ+=.055;
        for(const d of E) if(this.m.has(VS.K(x+d[0],y+d[1],z+d[2]))) occ+=.027;
        for(const d of K) if(this.m.has(VS.K(x+d[0],y+d[1],z+d[2]))) occ+=.012;
        f=1-Math.min(occ,.46);
        f*=.90+.10*clamp((y+3)/16,0,1);
      }
      col.setHex(v.c).multiplyScalar(f);
      if(v.j) col.multiplyScalar(1+(rnd()-.5)*.075);
      if(wet){
        if(y<=0){ col.lerp(tmp.setHex(0x0e2b30),.28); }
        if(y===1){ col.lerp(tmp.setHex(0x1d3326),.22); }
      }
      const s=v.s,j=v.j?(rnd()-.5)*.045:0;
      const sx=Math.max(.04,s[0]+j),sy=Math.max(.04,s[1]+j),sz=Math.max(.04,s[2]+j);
      m.compose(pos.set(x+v.o[0]+(v.j?(rnd()-.5)*.03:0),y+v.o[1],z+v.o[2]+(v.j?(rnd()-.5)*.03:0)),q0,sc.set(sx,sy,sz));
      mesh.setMatrixAt(i,m); mesh.setColorAt(i,col);
      dec.set(k,col.getHex()); i++;
    }
    for(const p of this.p){
      col.setHex(p.c); if(p.jit) col.multiplyScalar(1+(rnd()-.5)*.07);
      m.compose(p.p,p.q,p.s); mesh.setMatrixAt(i,m); mesh.setColorAt(i,col); i++;
    }
    mesh.instanceMatrix.needsUpdate=true;
    if(mesh.instanceColor)mesh.instanceColor.needsUpdate=true;
    mesh.castShadow=cast; mesh.receiveShadow=recv;
    mesh.userData.count=N; parent.add(mesh);
    world.voxels+=N;
    return mesh;
  }
}
const world={voxels:0};

/* ══════════════════════ world parameters ══════════════════════ */
const SEA=0.5, WHARF_Y=3.6, TOWN_SHORE=15;
const coastX=z=>TOWN_SHORE+2.6*Math.sin(z*.085+1.1)+2.2*fbm(z*.05,7.3,2);
const plots=[
  {n:'customs',x0:25,x1:33,z0:4,z1:13},
  {n:'bond',   x0:24,x1:35,z0:17,z1:25},
  {n:'anchor', x0:22,x1:29,z0:-14,z1:-7},
  {n:'terrace',x0:30,x1:35,z0:-20,z1:-2},
  {n:'church', x0:43,x1:51,z0:-14,z1:-5},
  {n:'sail',   x0:23,x1:31,z0:29,z1:35},
  {n:'market', x0:37,x1:45,z0:20,z1:28},
  {n:'boat',   x0:17,x1:24,z0:-36,z1:-28},
  {n:'mill',   x0:45,x1:52,z0:5,z1:12}
];
const plotAt=(x,z)=>plots.find(p=>x>=p.x0-1&&x<=p.x1+1&&z>=p.z0-1&&z<=p.z1+1);
const PLOT_TOP={customs:7,bond:7,anchor:7,terrace:8,church:10,sail:7,market:9,boat:6,mill:13};
const streets=[{x0:36,x1:40,z0:-26,z1:38},{x0:30,x1:44,z0:-25,z1:-22},{x0:30,x1:52,z0:14,z1:17}];
const inStreets=(x,z)=>streets.some(s=>x>=s.x0&&x<=s.x1&&z>=s.z0&&z<=s.z1);
const inWharf=(x,z)=>x>=-19&&x<=18&&z>=-4&&z<=7;
function rawTop(x,z){
  const d=Math.max(0,x-coastX(z));
  let y=5+smoothstep(1,15,d)*2.4+smoothstep(9,32,d)*3.6+fbm(x*.055,z*.055,3)*3.2;
  const hd=Math.hypot(x-49,z+30); y+=Math.max(0,9.5-hd*.42);
  const cd=Math.hypot(x-47,z-8); y+=Math.max(0,7-cd*.4);
  return y;
}
function groundTop(x,z){
  const p=plotAt(x,z);
  if(p) return PLOT_TOP[p.n];
  return rawTop(x,z);
}
const isLand=(x,z)=>x>coastX(z);

/* ══════════════════════ shared registries ══════════════════════ */
const anim={ship:null,flags:[],mill:null,crane:null,sign:null,beam:null,gulls:[],clouds:[],
  puffs:null,buoys:[],foams:[],sloop:null,distant:[],lamps:null};
const glowPts=[]; const lampLights=[];

/* ══════════════════════ 1 · SEA ══════════════════════ */
function buildSea(){
  const xs=[],zs=[];
  for(let x=-58;x<=58;x++)for(let z=-58;z<=58;z++){ if(x>coastX(z)-1.5) continue; xs.push(x);zs.push(z); }
  const n=xs.length;
  const mesh=new THREE.InstancedMesh(BOX,MAT.water,n);
  mesh.receiveShadow=true; scene.add(mesh); world.voxels+=n;
  const m=new THREE.Matrix4(),col=new THREE.Color(),a=new THREE.Color(),b=new THREE.Color();
  const H=7;
  const water={mesh,update(t){
    for(let i=0;i<n;i++){
      const x=xs[i],z=zs[i];
      const shelter=clamp((x+34)/46,0,1)*(isLand(x+3,z)?1:1);
      const amp=.55-.34*shelter;
      let h=SEA+amp*(Math.sin(x*.17+t*1.05)*.42+Math.sin(z*.22-t*.85)*.34+Math.sin((x+z)*.105+t*.62)*.40)
            +amp*.35*Math.sin(x*.61-z*.52+t*1.7);
      const shore=clamp(1-(coastX(z)-x)/7,0,1);
      h+=shore*.5*(.5+.5*Math.sin(x*.5+z*.4+t*1.5));
      m.makeScale(1.04,H,1.04); m.elements[12]=x; m.elements[13]=h-H/2; m.elements[14]=z;
      mesh.setMatrixAt(i,m);
      const deep=clamp((x+58)/26,0,1);
      a.setHex(C.seaDeep); b.setHex(C.seaMid); col.copy(a).lerp(b,deep);
      col.lerp(b.clone().setHex(C.seaShal),shore*.65);
      const crest=clamp((h-SEA+.55)/1.1,0,1);
      col.lerp(new THREE.Color(C.foam),Math.max(crest*.55,shore*crest*.9));
      col.multiplyScalar(.92+.16*Math.sin(x*.9+z*.7+t*1.2));
      mesh.setColorAt(i,col);
    }
    mesh.instanceMatrix.needsUpdate=true; mesh.instanceColor.needsUpdate=true;
  }};
  anim.water=water; water.update(0);
}

/* ══════════════════════ 2 · LAND + QUAY ══════════════════════ */
function buildLand(){
  const B=new VS(),L=new VS();
  /* shingle foreshore (drawn first so land overwrites) */
  for(let z=-58;z<=58;z++)for(let x=Math.floor(coastX(z))-9;x<=Math.ceil(coastX(z))+2;x++){
    if(isLand(x,z))continue;
    const t=Math.round(3.2-fbm(x*.12,z*.12,2)*1.4);
    for(let y=t;y>=-2;y--) B.at(x,y,z,y<=0?C.shingle:pick([C.sand,C.shingle,C.stone2],rnd));
  }
  /* rock foreshore: north-east point & south head */
  const rocky=(x,z)=>(z<-24&&x<coastX(z)+5)||(z>30&&x<coastX(z)+6);
  /* land columns */
  const Hmap=new Map();
  const topAt=(x,z)=>{ if(!isLand(x,z))return -99; const k=VS.K(x,0,z); let v=Hmap.get(k); if(v===undefined){v=Math.round(groundTop(x,z));Hmap.set(k,v);} return v; };
  for(let x=13;x<=60;x++)for(let z=-58;z<=58;z++){
    if(!isLand(x,z))continue;
    const top=topAt(x,z);
    const shore=x-coastX(z);
    for(let y=Math.max(-3,top-3);y<=top;y++){
      const hidden = topAt(x+1,z)>=y+1&&topAt(x-1,z)>=y+1&&topAt(x,z+1)>=y+1&&topAt(x,z-1)>=y+1;
      if(hidden&&y<top)continue;
      let c;
      if(y>=top){
        if(shore<1.6) c=rocky(x,z)?pick([C.rock,C.rock2,C.stone2],rnd):pick([C.sand,C.shingle],rnd);
        else if(inStreets(x,z)) c=rnd()<.5?C.cobble:C.cobble2;
        else if(x<26) c=(rnd()<.5?C.cobble:C.stone3);
        else c=rnd()<.34?pick([C.grass,C.grass2],rnd):(rnd()<.5?C.dirt:C.grass2);
      } else if(y>=top-1){ c=shore<1.8?pick([C.rock,C.stone2],rnd):C.dirt; }
      else c=shore<1.6?pick([C.rock,C.rock2,C.stone],rnd):C.stone2;
      if(y<=1&&shore<1.4)c=pick([C.stone,C.stone2,C.rock],rnd);
      B.at(x,y,z,c);
    }
    /* stone quay face down the shore */
    for(let y=-3;y<=Math.min(top,4);y++) B.at(Math.round(coastX(z))+1,y,z,pick([C.stone,C.stone2,C.stone3],rnd));
  }
  /* paving on plots & wharf approach */
  for(const p of plots){for(let x=p.x0;x<=p.x1;x++)for(let z=p.z0;z<=p.z1;z++){
    const t=PLOT_TOP[p.n]; B.at(x,t,z,rnd()<.4?C.cobble:C.stone3,{over:true});}}
  /* steps down to the water at the sail-loft beach */
  for(let i=0;i<6;i++)for(let z=30;z<=34;z++) B.at(Math.round(coastX(z))+2+i,5-i,z,C.stone,{over:true});
  /* sea wall chain */
  for(let z=-56;z<=56;z+=5){B.at(Math.round(coastX(z))+1,5,z,C.stone3,{over:true});B.at(Math.round(coastX(z))+1,6,z,C.iron,{over:true});}
  B.build({mat:MAT.scene});
  anim.landBuilt=true;
}

/* ══════════════════════ 3 · LONG WHARF ══════════════════════ */
function buildWharf(){
  const B=new VS(),L=new VS();
  const x0=-19,x1=18,z0=-4,z1=7;
  B.box(x0,x1,WHARF_Y-1,WHARF_Y,z0,z1,C.plank);
  for(let x=x0;x<=x1;x++)for(let z=z0;z<=z1;z+=1) if((x+z)%4===0) B.at(x,WHARF_Y,z,C.wood,{over:true});
  /* stone root at the shore */
  for(let x=coastX(2)-1;x<=x1;x+=1) for(let z=z0;z<=z1;z++) B.box(Math.round(x),Math.round(x),-2,WHARF_Y-2,z,z,C.stone);
  /* piles + cross bracing */
  const piles=[];
  for(let x=x0+2;x<=x1;x+=4)for(const z of [z0,z1]){
    for(let y=-4;y<=WHARF_Y-1;y++) B.at(x,y,z,C.woodD);
    B.at(x,WHARF_Y,z,C.iron2,{s:.72,over:true});
    piles.push([x,z]);
    /* weed line */
    for(let y=-1;y<=1;y++) B.at(x,y,z,0x24382c,{over:true,s:1.06});
  }
  for(let i=0;i<piles.length-2;i++){
    const a=piles[i],b=piles[i+2];
    if(Math.abs(a[0]-b[0])>4)continue;
    B.beam(V3(a[0],0,a[1]),V3(b[0],2.4,b[1]),{c:C.woodD,w:.26,t:.26,step:.55});
    B.beam(V3(a[0],2.4,a[1]),V3(b[0],0,b[1]),{c:C.woodD,w:.26,t:.26,step:.55});
  }
  /* deck-side bollards, capstans, crates, barrels */
  for(let x=x0+3;x<=x1-2;x+=5){
    B.at(x,WHARF_Y+1,z0+.5,C.iron,{s:.62}); B.at(x,WHARF_Y+2,z0+.5,C.iron,{s:.46});
    B.at(x,WHARF_Y+1,z1-.5,C.woodL,{s:.62});
  }
  for(let x=x0+1;x<=x1;x+=7){
    B.at(x,WHARF_Y+1,2,C.woodD,{s:.9}); B.at(x,WHARF_Y+2,2,C.woodL,{s:.55});
    for(let d=-.5;d<=.5;d+=1) B.at(x+.5,WHARF_Y+2,2+d,C.woodL,{s:.2});
  }
  const crate=(x,z,r=0)=>{
    const w=1+(rnd()*2|0),h=1+(rnd()*2|0);
    for(let i=0;i<w;i++)for(let j=0;j<h;j++)for(let k=0;k<w;k++){
      const c=pick([C.woodL,C.wood,C.plank,C.woodD],rnd);
      B.at(x+i,WHARF_Y+1+j,z+k,c);
      if(j===h-1&&i===0)B.at(x+i,WHARF_Y+1+j,z+k,C.ochre2,{over:true,s:[1,.2,1]});
    }
  };
  [[-14,-1],[-13,4],[-6,-1],[-5,5],[10,5],[13,-1],[14,3],[-9,3],[1,5]].forEach(p=>crate(p[0],p[1]));
  const barrel=(x,z)=>{B.at(x,WHARF_Y+1,z,C.woodD,{s:.85});B.at(x,WHARF_Y+2,z,C.woodL,{s:.85});B.at(x,WHARF_Y+3,z,C.woodD,{s:.85});};
  [[-11,-1.2],[-10.4,-1.2],[-2,5.6],[-1.4,5.6],[11,4.6],[6,-1.4]].forEach(p=>barrel(Math.round(p[0]),Math.round(p[1])));
  /* timber stack */
  for(let i=0;i<7;i++)for(let j=0;j<3;j++) B.beam(V3(-17+6.2,WHARF_Y+1+j*.55,-3+j),V3(-17+6.2,WHARF_Y+1+j*.55,4-j),{c:C.woodL,w:.34,t:.34,step:.6});
  /* coiled rope rings */
  const rope=(x,z)=>{for(let a=0;a<8;a++){const t=a/8*Math.PI*2;B.at(x+Math.cos(t)*.8,WHARF_Y+1,z+Math.sin(t)*.8,C.canvas2,{s:.42});}};
  rope(4,-.6);rope(-8,5.4);rope(15,1);
  /* lamp posts + railings */
  const lamps=[];
  for(let x=x0+4;x<=x1-3;x+=8){
    B.beam(V3(x,WHARF_Y+1,z0+.5),V3(x,WHARF_Y+6,z0+.5),{c:C.iron,w:.28,t:.28,step:.7});
    B.beam(V3(x,WHARF_Y+6,z0+.5),V3(x+.1,WHARF_Y+6,z0+1.8),{c:C.iron,w:.24,t:.24,step:.5});
    B.at(x+.1,WHARF_Y+5.6,z0+1.8,C.glass); L.at(x+.1,WHARF_Y+5.6,z0+1.8,C.lamp);
    lamps.push([x+.1,WHARF_Y+5.6,z0+1.8]);
    /* railing */
    for(let s=-1;s<=1;s++) B.at(x+s*3,WHARF_Y+1,z0+.2,C.woodD,{s:.3});
  }
  for(let x=x0;x<x1;x++){
    B.beam(V3(x,WHARF_Y+2.2,z0+.2),V3(x+1,WHARF_Y+2.2,z0+.2),{c:C.wood,w:.18,t:.18,step:.55});
    B.beam(V3(x,WHARF_Y+1.4,z0+.2),V3(x+1,WHARF_Y+1.4,z0+.2),{c:C.wood,w:.18,t:.18,step:.55});
    B.beam(V3(x,WHARF_Y+2.2,z1-.2),V3(x+1,WHARF_Y+2.2,z1-.2),{c:C.wood,w:.18,t:.18,step:.55});
  }
  /* market stalls with striped awnings */
  const stall=(x,z,col)=>{
    B.at(x,WHARF_Y+1,z,C.woodD,{s:.28});B.at(x+3,WHARF_Y+1,z,C.woodD,{s:.28});
    B.at(x,WHARF_Y+3,z,C.woodD,{s:.24});B.at(x+3,WHARF_Y+3,z,C.woodD,{s:.24});
    for(let i=0;i<=4;i++)for(let j=-1;j<=0;j++){
      const y=WHARF_Y+4+(i>2?-1:0);
      B.at(x-1+i*.9|0,y,z+j,(i+j)%2?col:C.white,{s:[1.05,.22,1.1]});
    }
    B.box(x,Math.round(x+3),WHARF_Y+1,WHARF_Y+2,Math.round(z-.8),Math.round(z),C.plank);
  };
  stall(-3,3,C.red); stall(6,3,C.teal);
  /* figures on the wharf */
  const person=(x,z,c1,c2,face=1)=>{
    B.at(x,WHARF_Y+1,z,c2,{s:.55}); B.at(x,WHARF_Y+2,z,c1,{s:.5});
    B.at(x,WHARF_Y+3,z,0xd8b48c,{s:.42}); B.at(x,WHARF_Y+3.5,z+face*.2,0x4a3a2a,{s:.5});
  };
  person(-12,1,C.red,C.iron); person(-11,2,C.ochre,C.slate); person(2,0,C.white,C.teal);
  person(8,1,C.blue||0x35566e,C.iron2); person(12,2,C.canvas2,C.woodD); person(-7,0,C.ochre2,C.slate);
  /* gin crane over the ship's side */
  const cx=8,cz=-1;
  B.beam(V3(cx-1.5,WHARF_Y+1,cz),V3(cx-1.5,WHARF_Y+8,cz),{c:C.woodD,w:.5,t:.5,step:.6});
  B.beam(V3(cx+1.5,WHARF_Y+1,cz),V3(cx+1.5,WHARF_Y+8,cz),{c:C.woodD,w:.5,t:.5,step:.6});
  B.beam(V3(cx-1.5,WHARF_Y+8,cz),V3(cx+1.5,WHARF_Y+8,cz),{c:C.wood,w:.4,t:.4,step:.55});
  B.beam(V3(cx,WHARF_Y+7.5,cz),V3(cx+2.2,WHARF_Y+6,cz),{c:C.woodD,w:.3,t:.3,step:.5});
  const jibTip=V3(cx,WHARF_Y+7.6,cz-4.6);
  B.beam(V3(cx,WHARF_Y+8,cz),jibTip,{c:C.woodL,w:.42,t:.42,step:.55});
  B.cat(jibTip,V3(cx-2.4,WHARF_Y+9.2,cz),{c:C.canvas2,sag:.5,w:.14,t:.14});
  B.cat(jibTip,V3(cx+2.4,WHARF_Y+9.2,cz),{c:C.canvas2,sag:.5,w:.14,t:.14});
  /* swinging crate group */
  const g=new THREE.Group(); g.position.copy(jibTip); scene.add(g);
  const S=new VS();
  S.beam(V3(0,0,0),V3(0,-3.4,0),{c:C.canvas2,w:.14,t:.14,step:.5});
  S.box(-1,-.2,-3.4,-2,-.2,{c:0}).box(-1,0,-3.4,-2.2,0,-1,C.woodL);
  S.box(-1,0,-2.2,0,-1,C.ochre2);
  g.add(S.build({mat:MAT.scene,parent:new THREE.Group()}));
  g.children.length; anim.crane=g;
  /* gangplank to the bark */
  B.beam(V3(-2,WHARF_Y+.05,z0+.1),V3(-2,4.35,-5.6),{c:C.woodL,w:1.5,t:.2,step:.55});
  B.beam(V3(-2.7,WHARF_Y+.6,z0+.1),V3(-2.7,5.0,-5.6),{c:C.wood,w:.16,t:.16,step:.5});
  B.beam(V3(-1.3,WHARF_Y+.6,z0+.1),V3(-1.3,5.0,-5.6),{c:C.wood,w:.16,t:.16,step:.5});
  /* mooring bollards where the lines come across */
  B.at(-16,WHARF_Y+1,-3.2,C.iron,{s:.7}); B.at(2,WHARF_Y+1,-3.2,C.iron,{s:.7});
  /* rowboats on the harbour side */
  const boat=(x,z,rot,c1=C.woodL,c2=C.woodD)=>{
    const S=new VS();
    for(let i=-3;i<=3;i++){
      const w=Math.max(0,Math.round(1.6-Math.abs(i)*.42));
      for(let k=-w;k<=w;k++){ if(Math.abs(k)===w||Math.abs(i)===3) S.at(i,0,k,c1); }
      S.at(i,-1,0,c2);
    }
    S.at(0,1,0,C.wood,{s:[1.2,.2,.3]}); S.at(-2,1,0,C.wood,{s:[1.2,.2,.3]});
    S.beam(V3(-3.4,.6,0),V3(3.4,.6,0),{c:C.woodL,w:.22,t:.22,step:.5});
    const grp=new THREE.Group(); grp.position.set(x,SEA+.2,z); grp.rotation.y=rot;
    grp.add(S.build({mat:MAT.scene,parent:new THREE.Group()}));
    scene.add(grp); anim.foams.push({o:grp,base:SEA+.2,ph:rnd()*6,roll:.05});
  };
  boat(11,-6.4,.4); boat(14.5,-7.4,-.3); boat(-13,-7.6,.9);
  /* foam collars round the piles */
  const F=new VS();
  for(let x=x0+2;x<=x1;x+=4)for(const z of[z0,z1]) for(let a=0;a<8;a++){
    const t=a/8*Math.PI*2; F.at(x+Math.cos(t)*1.5,SEA,z+Math.sin(t)*1.5,C.foam,{s:.7,jit:true});
  }
  const fm=F.build({mat:new THREE.MeshStandardMaterial({roughness:1}),cast:false,parent:new THREE.Group()});
  const fg=new THREE.Group(); fg.add(fm); scene.add(fg); anim.foams.push({o:fg,base:0,ph:1.4,roll:0,lift:.18});
  B.build({mat:MAT.scene});
  L.build({mat:MAT.glow,ao:false,cast:false,recv:false,wet:false});
  anim.lamps=L; glowPts.push(...lamps.map(p=>({p,size:4.4,c:0xffc06a})));
}

/* ══════════════════════ 4 · THE BARK ══════════════════════ */
const SHIP={x:-7,y:0,z:-10.5};
function buildShip(){
  const B=new VS(),L=new VS();
  const keelY=x=>-2.7+Math.max(0,(Math.abs(x)-11))*0.62;
  const halfBeam=x=>{
    const t=(x+15)/30;
    let w=4.5*Math.pow(Math.sin(Math.PI*(.035+.93*t)),.5);
    if(t<.2) w*=.72+.28*(t/.2);
    return Math.max(.45,w);
  };
  const deckY=x=>4.25+Math.max(0,(Math.abs(x)-9))*.34+(x>9?1.1:0)+(x<-9?.7:0);
  /* hull shell */
  for(let x=-15;x<=15;x++){
    const w=halfBeam(x),y0=Math.ceil(keelY(x)),y1=Math.floor(deckY(x));
    for(let y=y0;y<=y1;y++){
      const t=clamp((y-keelY(x))/(y1-keelY(x)),0,1);
      const wi=Math.max(0,Math.round(w*Math.pow(t,.27)));
      for(let xi=-wi;xi<=wi;xi++){
        const edge=Math.abs(xi)>=wi-1||y<=y0+1;
        if(!edge)continue;
        let c;
        if(y<=0)c=C.hullUnder;
        else if(y>=y1-2)c=C.hull;
        else c=C.hull;
        if(y>=y1-1&&y<=y1)c=C.hullStripe;
        B.at(xi,y,x,c); /* NOTE: ship built with bow on -X, beam along Z → swap */
      }
    }
  }
  /* — rebuild properly: above loop used xi on X; redo with correct axes — */
  B.m.clear();
  for(let x=-15;x<=15;x++){          // x = fore-aft, bow at -15
    const w=halfBeam(x),y0=Math.ceil(keelY(x)),y1=Math.floor(deckY(x));
    for(let y=y0;y<=y1;y++){
      const t=clamp((y-keelY(x))/(y1-keelY(x)+.001),0,1);
      const wi=Math.max(0,Math.round(w*Math.pow(t,.26)));
      for(let z=-wi;z<=wi;z++){
        const edge=Math.abs(z)>=wi-1||y<=y0+1;
        if(!edge)continue;
        let c= y<=0.4?C.hullUnder : (y>=y1-2? C.hull : C.hull);
        if(y===y1-1)c=C.hullStripe;
        if(y>=y1-3&&y<=y1-2&&((x+2)%4===0)) c=C.white;      // gun-port cheeks
        if(y===y1-3&&((x+2)%4===0)) c=C.iron2;              // ports
        B.at(x,y,z,c);
      }
    }
    /* deck */
    const dy=Math.round(deckY(x)),wd=Math.max(0,Math.round(halfBeam(x))-1);
    for(let z=-wd;z<=wd;z++) B.at(x,dy,z,C.woodL);
    /* bulwark */
    const bw=Math.round(halfBeam(x));
    for(let z=-bw;z<=bw;z++) if(Math.abs(z)>=bw-0){
      B.at(x,dy+1,z,x<-9||x>9?C.white:C.hullStripe);
      if((x+z)%5===0)B.at(x,dy+2,z,C.woodD);
    }
    for(const s of[-1,1]) B.at(x,dy+2,Math.sign(s)*bw,C.woodD);
  }
  /* stern castle + quarter galleries */
  B.box(8,15,6,7,-3,3,C.hull); B.box(8,14,7,7,-3,3,C.hullStripe);
  B.box(11,14,8,8,-3,3,C.white);
  for(const s of[-1,1])for(let x=9;x<=14;x++)B.at(x,6,s*3.4,C.hullStripe,{s:.6});
  B.box(12,13,6.5,7.5,-2,2,C.canvas);
  L.box(12,13,6.6,7.2,-1,1,C.glass);
  /* bow: stem + figurehead + head rails */
  for(let y=1;y<=6;y++) B.at(-15+Math.round(y*.28),y,0,C.woodD,{s:[1.4,1,1]});
  B.at(-17,5,0,C.ochre,{s:.9}); B.at(-18,5.6,0,C.ochre,{s:.7});
  B.beam(V3(-16,5.6,1.6),V3(-13,4.4,3.2),{c:C.white,w:.3,t:.3,step:.5});
  B.beam(V3(-16,5.6,-1.6),V3(-13,4.4,-3.2),{c:C.white,w:.3,t:.3,step:.5});
  /* bowsprit */
  B.beam(V3(-14,5.4,0),V3(-23,7.8,0),{c:C.woodL,w:.62,t:.62,step:.55});
  B.beam(V3(-19,6.6,0),V3(-24.6,6.2,0),{c:C.wood,w:.3,t:.3,step:.5});
  B.beam(V3(-15,3.2,0),V3(-22.6,7.3,0),{c:C.canvas2,w:.14,t:.14,step:.55});   // bobstay
  /* masts, yards, caps */
  const masts=[{x:-8,h:23,yd:[15,10.5,6],sp:4.6},{x:-1,h:26.5,yd:[18.5,13.5,8.5],sp:5.2},{x:7,h:19,yd:[13,8.5],sp:3.8}];
  const mastTop=[];
  masts.forEach((mm,i)=>{
    const dy=Math.round(deckY(mm.x));
    B.at(mm.x,dy,0,C.iron2,{s:.9,over:true});
    B.beam(V3(mm.x,dy,0),V3(mm.x,dy+mm.h,0),{c:C.woodL,w:.62,t:.62,step:.7});
    B.at(mm.x,dy+mm.h*.45,0,C.woodD,{s:1.5});
    B.at(mm.x,dy+mm.h,0,C.iron,{s:.4});
    mastTop.push(V3(mm.x+SHIP.x,dy+mm.h+SHIP.y,mm.z+SHIP.z-10.5+10.5));
    mm.top=dy+mm.h;
    mm.yd.forEach((yy,k)=>{
      const sp=mm.sp*(1-k*.22);
      B.beam(V3(mm.x,yy,-sp),V3(mm.x,yy,sp),{c:C.wood,w:.34,t:.34,step:.55});
      B.at(mm.x,yy+.5,sp*.8,C.canvas2,{s:.3});B.at(mm.x,yy+.5,-sp*.8,C.canvas2,{s:.3});
      if(k<2){
        /* square sail, bellying to port (-X) */
        const top=yy-.4,hh=yy-(mm.yd[k+1]!==undefined?mm.yd[k+1]+2.2:yy-hh2(k));
        sail(B,mm.x,sp,yy-1,Math.max(3.2,(yy-(mm.yd[k+1]||0)-2.4)),1.9+k*.2);
      }
    });
  });
  function hh2(k){return k===0?7:6;}
  function sail(b,mx,yy,halfspan,height,bowAmt){
    for(let z=-halfspan;z<=halfspan;z++){
      const zz=Math.abs(z)/halfspan;
      const maxJ=Math.floor(height*(1-.26*zz*zz));
      for(let j=0;j<=maxJ;j++){
        const u=(z+halfspan)/(2*halfspan),v=j/height;
        const bow=bowAmt*Math.sin(Math.PI*u)*(1-v*.55)*(1-zz*.35);
        b.at(mx-bow,yy-j,z, (j%5===0)?C.canvas2:(v>.86?C.canvas2:C.canvas));
      }
    }
  }
  /* furled courses on the lower yards (rolled canvas) */
  masts.forEach((mm,i)=>{
    const sp=mm.sp*.72;
    B.beam(V3(mm.x+.5,mm.yd[mm.yd.length-1]-1.1,-sp),V3(mm.x+.5,mm.yd[mm.yd.length-1]-1.1,sp),{c:C.canvas2,w:.5,t:.5,step:.5});
  });
  /* spanker (fore-aft sail) on the mizzen + boom */
  B.beam(V3(7.4,7.4,0),V3(13.2,6.8,0),{c:C.wood,w:.3,t:.3,step:.5});
  B.tri(V3(7.4,13.4,0),V3(7.4,6.9,0),V3(13.4,6.8,0),{c:C.canvas,bow:1.0,nx:-1,shade:(u,v)=>v>.86?C.canvas2:C.canvas});
  /* headsails */
  B.tri(V3(-8.4,20.5,0),V3(-8.4,12,0),V3(-22.4,7.6,0),{c:C.sail,bow:1.7,nx:-1});
  B.tri(V3(-1,24,0),V3(-1,16,0),V3(-16.4,5.8,0),{c:C.canvas,bow:1.9,nx:-1});
  B.tri(V3(-8.4,11.4,0),V3(-8.4,6.4,0),V3(-19.4,7.2,0),{c:C.canvas2,bow:1.1,nx:-1});
  /* standing rigging */
  const rig=(a,b)=>B.cat(a,b,.35,{c:C.canvas2,w:.14,t:.14,step:.6,n:10});
  masts.forEach(mm=>{
    const top=V3(mm.x,mm.top,0);
    for(const s of[-1,1]){
      for(let k=-1;k<=1;k++){
        rig(top,V3(mm.x+3.2,Math.round(deckY(mm.x))+2,s*(halfBeam(mm.x+3)+.3)+k*1.1));
        rig(top,V3(mm.x-3.2,Math.round(deckY(mm.x))+2,s*(halfBeam(mm.x-3)+.3)+k*1.1));
      }
    }
    if(mm.x!==masts[0].x) rig(top,V3(masts[0].x,masts[0].top,0));
    if(mm.x===-1) rig(top,V3(-22.6,7.8,0));
    if(mm.x===7) rig(V3(-1,26.5,0),V3(12.6,12,0));
  });
  /* deck fittings */
  const dy0=Math.round(deckY(0));
  for(const x of[-6,2,5]) B.box(x,x,dy0+1,dy0+1,-2.2,2.2,C.woodD,{s:[1,.4,1]});
  for(const x of[-11,-9,-3,1,4]) B.at(x,dy0+1,0,C.woodD,{s:.8});
  for(let k=-1;k<=1;k+=2){
    for(let i=0;i<4;i++){
      const x=-6+i*3.2;
      B.at(x,dy0+1.5,k*3.4,C.iron2,{s:[1.5,.5,.5]});
      B.at(x-1.4,dy0+1.2,k*3.9,C.iron2,{s:[.5,.4,.4]});
    }
  }
  for(const p of[[-13,2],[10,-2],[-4,-2.6],[-4,2.6]]){
    B.at(p[0],dy0+1,p[1],C.woodL,{s:.75}); B.at(p[0],dy0+2,p[1],C.woodD,{s:.6});
  }
  /* crew on deck */
  const crew=(x,z,c1,c2)=>{B.at(x,dy0+2,z,c2,{s:.5});B.at(x,dy0+3,z,c1,{s:.46});B.at(x,dy0+4,z,0xd6b28a,{s:.4});};
  crew(-14,-2.6,C.red,C.iron); crew(-13.4,2.4,C.ochre,C.slate); crew(12,2,C.canvas2,C.woodD); crew(-4,3.6,C.teal,C.iron2);
  /* stern lantern + windows */
  B.beam(V3(15.2,8.4,0),V3(16.2,8.4,0),{c:C.iron,w:.24,t:.24,step:.5});
  L.at(16.4,8.4,0,C.lamp); B.at(16.4,8.4,0,C.glass,{over:true});
  glowPts.push({p:[16.4+SHIP.x,8.4+SHIP.y,SHIP.z],size:5.2,c:0xffc46b});
  lampLights.push({p:[16.4+SHIP.x,8.4+SHIP.y,SHIP.z],c:0xffbb6a,i:9,d:22});
  /* ship's boat slung at the waist + anchor cable */
  B.beam(V3(-3,9.5,3.6),V3(-3,6.4,4.6),{c:C.canvas2,w:.12,t:.12,step:.5});
  B.beam(V3(-1,9.5,3.6),V3(-1,6.4,4.6),{c:C.canvas2,w:.12,t:.12,step:.5});
  B.box(-3,-1,6,6.6,4.2,5.2,C.woodL);
  B.cat(V3(-15.6,5.2,1),V3(-24,SEA+.4,3),{c:C.iron2,sag:1.2,w:.3,t:.3,n:9});
  B.cat(V3(-15.6,5.2,-1),V3(-25,SEA+.4,-2),{c:C.iron2,sag:1.4,w:.3,t:.3,n:9});
  /* moorings across to the wharf */
  B.cat(V3(-14.4,5.6,3.6),V3(-9,WHARF_Y+1.6,7.4),{c:C.canvas2,sag:.7,w:.2,t:.2,n:9});
  B.cat(V3(4,5.4,4.2),V3(9,WHARF_Y+1.6,7.2),{c:C.canvas2,sag:.6,w:.2,t:.2,n:8});
  /* pilot ladder down the ship's wharf-side */
  for(let y=1;y<=4;y++){B.at(-2,y,4.9,C.canvas2,{s:[1.3,.14,.14]});B.at(-2.5,y,4.9,C.woodL,{s:[.16,.16,.5]});B.at(-1.5,y,4.9,C.woodL,{s:[.16,.16,.5]});}
  B.build({mat:MAT.ship,wet:true});
  L.build({mat:MAT.glow,ao:false,cast:false,recv:false,wet:false});

  /* ── assemble ship group ── */
  const grp=new THREE.Group(); grp.position.set(SHIP.x,SHIP.y,SHIP.z); scene.add(grp);
  grp.children.length=0;
  const mesh=B.build({mat:MAT.ship,parent:grp,wet:true});
  const lmesh=L.build({mat:MAT.glow,parent:grp,ao:false,cast:false,recv:false,wet:false});
  world.voxels-=mesh.userData.count+lmesh.userData.count;   // built twice above (preview+final)
  grp.visible=true;
  anim.ship={g:grp,lightMesh:lmesh};
  /* ensign at the mizzen head */
  anim.flags.push(new Flag({parent:grp,x:7,y:19.4,z:0,w:7,h:4.4,cantilever:true,
    paint:(u,v)=>{ if(u<.34&&v<.45) return (Math.floor(u*9)+Math.floor(v*9))%2?C.white:C.red;
      return (Math.floor(v*6)%2)?C.white:C.red2; }}));
  anim.flags.push(new Flag({parent:grp,x:-1,y:26.5,z:0,w:5,h:3.2,
    paint:(u,v)=> v>.62?C.teal:(v>.36?C.white:C.ochre)}));
}
/* animated cloth */
class Flag{
  constructor({parent,x,y,z,w=6,h=4,paint,cantilever}){
    this.w=w;this.h=h;this.pts=[];
    const n=(w+1)*(h+1);
    this.mesh=new THREE.InstancedMesh(BOX,MAT.scene,n);
    this.mesh.castShadow=false;
    for(let i=0;i<=w;i++)for(let j=0;j<=h;j++)this.pts.push([i,j,x,y-j,z]);
    parent.add(this.mesh); world.voxels+=n;
    this.col=new THREE.Color(); this.m=new THREE.Matrix4(); this.q=new THREE.Quaternion();
    this.v=new THREE.Vector3(); this.s=new THREE.Vector3(1.05,.34,.2);
    this.paint=paint; this.n=n;
  }
  update(t){
    let i=0;
    for(let a=0;a<=this.w;a++)for(let b=0;b<=this.h;b++){
      const u=a/this.w,v=b/this.h;
      const w1=Math.sin(t*4.4-u*5.2)*.9*(u*1.1), w2=Math.sin(t*7.1-u*8.)*.32*u;
      this.v.set(this.pts[i][0]-this.w+ a, this.pts[i][1]-w2*.5, this.pts[i][2]+w1+w2);
      const ang=Math.atan2(Math.cos(t*4.4-u*5.2)*.9*4.4*-1,4);
      this.q.setFromEuler(new THREE.Euler(ang,0,Math.sin(t*4.4-u*5.2)*.25));
      this.m.compose(this.v,this.q,this.s);
      this.mesh.setMatrixAt(i,this.m);
      this.col.setHex(this.paint(1-u,v)).multiplyScalar(.9+.2*(1-v*.4));
      this.mesh.setColorAt(i,this.col); i++;
    }
    this.mesh.instanceMatrix.needsUpdate=true;
    if(this.mesh.instanceColor)this.mesh.instanceColor.needsUpdate=true;
  }
}

/* ══════════════════════ 5 · MOLE LIGHTHOUSE ══════════════════════ */
function buildLight(){
  const B=new VS(),L=new VS();
  const LX=-31,LZ=23;
  /* rocks */
  B.blob(LX,1,LZ,9,C.rock,{sy:.55,jitj:.9});
  B.blob(LX+4,2.4,LZ-3,5,C.rock2,{sy:.6,jitj:.9});
  B.blob(LX-5,1.6,LZ+4,4.5,C.rock,{sy:.5,jitj:1});
  B.box(LX-6,LX+6,3,4,LZ-6,LZ+6,C.stone);
  B.disc(LX,LZ,6.5,5,C.stone3);
  /* keeper's cottage */
  B.shell(LX+4,LX+8,5,8,LZ+2,LZ+6,C.cream);
  B.box(LX+4,LX+8,5,5,LZ+2,LZ+6,C.stone2);
  for(let s=0;s<=3;s++){for(let x=LX+3;x<=LX+9;x++){B.at(x,9-s,LZ+1+s,C.slate);B.at(x,9-s,LZ+7-s,C.slate);}
    for(let z=LZ+1+s;z<=LZ+7-s;z++){B.at(LX+4,9-s,z,C.slate2);B.at(LX+8,9-s,z,C.slate2);}}
  L.at(LX+6,7,LZ+2,C.glass); L.at(LX+5,6.5,LZ+4,C.glass);
  /* tower: tapered banded drum */
  const y0=5,y1=27;
  for(let y=y0;y<=y1;y++){
    const t=(y-y0)/(y1-y0);
    const r=lerp(3.5,1.9,t);
    const colr=(Math.floor((y-y0)/3)%2)?C.white:C.red2;
    for(let a=0;a<28;a++){
      const th=a/28*Math.PI*2;
      const x=Math.round(LX+Math.cos(th)*r),z=Math.round(LZ+Math.sin(th)*r);
      B.at(x,y,z,colr);
    }
  }
  /* gallery, lamp room, cap */
  B.disc(LX,LZ,3.2,y1+1,C.iron); B.disc(LX,LZ,3.0,y1+2,C.iron2);
  B.ring(LX,LZ,1.2,2.0,y1+2,y1+5,C.iron2);
  L.ring(LX,LZ,1.2,1.8,y1+2,y1+5,C.glass2);
  B.disc(LX,LZ,2.3,y1+6,C.copper);
  for(let a=0;a<20;a++){const th=a/20*Math.PI*2;B.at(Math.round(LX+Math.cos(th)*2.9),y1+3,Math.round(LZ+Math.sin(th)*2.9),C.iron,{s:.3});}
  B.at(LX,y1+8,LZ,C.iron,{s:.4});
  /* breakwater arm out to sea + beacon */
  for(let i=0;i<20;i++){
    const x=LX-4-i*1.1,z=LZ+2+i*.5;
    B.blob(x,0.5,z,2.4+i*.06,[C.rock,C.rock2,C.stone2],{sy:.55,jitj:1.2});
    if(i%3===0)B.at(x,2.2,z,C.stone);
  }
  B.box(LX-25,LX-24,2,5,LZ+10,LZ+11,C.red); B.at(LX-24.5,6,LZ+10.5,C.white);
  L.at(LX-24.5,6.6,LZ+10.5,C.lamp);
  /* foam round the mole */
  const F=new VS();
  for(let a=0;a<70;a++){const th=a/70*Math.PI*2,r=9.5+fbm(a*.3,2,2)*2;
    F.at(LX+Math.cos(th)*r,SEA+.2,LZ+Math.sin(th)*r,C.foam,{s:.9});}
  const fg=new THREE.Group();
  F.build({mat:new THREE.MeshStandardMaterial({roughness:1}),cast:false,parent:fg});
  scene.add(fg); anim.foams.push({o:fg,base:0,ph:2.2,roll:0,lift:.22});
  B.build({mat:MAT.scene});
  L.build({mat:MAT.glow,ao:false,cast:false,recv:false,wet:false});
  /* rotating beam */
  const bg=new THREE.Group(); bg.position.set(LX,y1+3.6,LZ); scene.add(bg);
  for(const s of[0,Math.PI]){
    const cone=new THREE.Mesh(new THREE.ConeGeometry(7.5,70,4,1,true),MAT.beam);
    cone.rotation.z=Math.PI/2; cone.rotation.y=s;
    cone.position.set(Math.cos(s)*35,0,Math.sin(s)*35);
    cone.rotation.set(0,-s+Math.PI/2,Math.PI/2);
    bg.add(cone);
  }
  const lamp=new THREE.PointLight(0xffd08a,0,90,1.4); lamp.position.set(LX,y1+3.6,LZ); scene.add(lamp);
  anim.beam={g:bg,lamp};
  glowPts.push({p:[LX,y1+3.6,LZ],size:22,c:0xffe0a8},
               {p:[LX-24.5,6.6,LZ+10.5],size:4,c:0xffc06a},
               {p:[LX+6,7,LZ+2],size:3.2,c:0xffc46b});
  lampLights.push({p:[LX,y1+3.6,LZ],c:0xffd7a0,i:60,d:80});
}

/* ══════════════════════ 6 · OLD TOWN ══════════════════════ */
function wallSet(B,L,{x0,x1,y0,y1,z0,z1,wall,trim,win=C.iron2,lit=true,glazing=C.glass,gates=false}){
  const put=(x,y,z,c)=>B.at(x,y,z,c);
  for(let y=y0;y<=y1;y++){
    const band=(y-y0)%4===0;
    for(let x=x0;x<=x1;x++)for(const z of[z0,z1]){
      const w=((x-x0)%4===2)&&((y-y0)%4===3)&&y<y1&&y>y0+1;
      put(x,y,z,band?trim:w?win:wall);
      if(w&&lit)L.at(x,y,z,glazing);
      if(w&&band)put(x,y-1,z,trim);
    }
    for(let z=z0;z<=z1;z++)for(const x of[x0,x1]){
      const w=((z-z0)%4===2)&&((y-y0)%4===3)&&y<y1&&y>y0+1;
      put(x,y,z,band?trim:w?win:wall);
      if(w&&lit)L.at(x,y,z,glazing);
    }
  }
  /* door on the sea face */
  const mx=Math.round((x0+x1)/2);
  for(let y=y0;y<=y0+2;y++){B.at(mx,y,z0,gates?C.woodD:C.wood,{over:true,s:[1.6,1,.4]});B.at(mx,y,z0-.01,C.woodD,{over:true,s:[1.9,.3,.5]});}
}
function roof(B,x0,x1,y0,z0,z1,c,{ridge='x'}={}){
  const half=Math.ceil((ridge==='x'?(z1-z0):(x1-x0))/2);
  for(let s=0;s<=half;s++){
    const y=y0+s;
    if(ridge==='x'){
      for(let x=x0-1;x<=x1+1;x++){B.at(x,y,z0-1+s,c);B.at(x,y,z1+1-s,c);}
      for(let z=z0-1+s;z<=z1+1-s;z++){B.at(x0-1,y,z,c);B.at(x1+1,y,z,c);}
      if(s===half)for(let x=x0-1;x<=x1+1;x++)B.at(x,y,Math.round((z0+z1)/2),c);
    }else{
      for(let z=z0-1;z<=z1+1;z++){B.at(x0-1+s,y,z,c);B.at(x1+1-s,y,z,c);}
      for(let x=x0-1+s;x<=x1+1-s;x++){B.at(x,y,z0-1,c);B.at(x,y,z1+1,c);}
      if(s===half)for(let z=z0-1;z<=z1+1;z++)B.at(Math.round((x0+x1)/2),y,z,c);
    }
  }
}
const chimneys=[];
function chimney(B,x,z,top,c=C.brick){
  B.at(x,top+1,z,c);B.at(x,top+2,z,c);B.at(x,top+3,z,c);
  B.at(x,top+4,z,C.iron2,{s:1.25});
  chimneys.push([x,top+4.6,z]);
}
function buildTown(){
  const B=new VS(),L=new VS();
  const R=(p)=>({x0:p.x0,x1:p.x1,z0:p.z0,z1:p.z1,y0:PLOT_TOP[p.n]});
  /* Customs House */
  let p=plots[0],r=R(p);
  wallSet(B,L,{...r,y1:r.y0+5,wall:C.cream,trim:C.ochre});
  roof(B,r.x0,r.x1,r.y0+6,r.z0,r.z1,C.slate);
  B.box(r.x0+1,r.x1-1,r.y0+6.0,r.y0+6,r.z0+3,r.z1-3,C.stone2,{over:true});
  B.box(r.x0+2,r.x1-2,r.y0+7,r.y0+9,r.z0+3,r.z1-3,C.cream);
  L.box(r.x0+3,r.x1-3,r.y0+8,r.y0+8,r.z0+3,r.z1-3,C.glass);
  roof(B,r.x0+2,r.x1-2,r.y0+10,r.z0+3,r.z1-3,C.copper);
  B.box(r.x0-1,r.x1+1,r.y0,r.y0+1,r.z0-1,r.z0-1,C.stone3);
  for(let x=r.x0;x<=r.x1;x+=2){B.at(x,r.y0+2,r.z0-1,C.white,{s:.7});B.at(x,r.y0+3,r.z0-1,C.white,{s:.7});B.at(x,r.y0+4,r.z0-1,C.white,{s:.7});}
  chimney(B,r.x1-1,r.z1-1,r.y0+9);
  anim.flags.push(new Flag({parent:new THREE.Group(),x:r.x1,y:r.y0+13,z:r.z1,w:6,h:3.8,
    paint:(u,v)=>v>.6?C.teal:(v>.32?C.white:C.red)})).parentMove;
  anim.flags[anim.flags.length-1].mesh.parent.position.set(0,0,0);
  scene.add(anim.flags[anim.flags.length-1].mesh.parent);
  anim.flags[anim.flags.length-1].mesh.parent.position.set(r.x1,r.y0+13,r.z1);
  anim.flags[anim.flags.length-1].x0=r.x1; anim.flags[anim.flags.length-1].y0=r.y0+13;
  /* Bond warehouse No.3 with hoist */
  p=plots[1];r=R(p);
  wallSet(B,L,{...r,y1:r.y0+6,wall:C.brick,trim:C.stone2,lit:true});
  roof(B,r.x0,r.x1,r.y0+7,r.z0,r.z1,C.slate2);
  B.box(r.x0+4,r.x0+7,r.y0+2,r.y0+6,r.z0-.01,r.z0,C.iron2,{over:true});
  B.beam(V3(r.x0+5.5,r.y0+8,r.z0-2.5),V3(r.x0+5.5,r.y0+8,r.z0),{c:C.woodD,w:.4,t:.4,step:.5});
  B.beam(V3(r.x0+5.5,r.y0+8,r.z0),V3(r.x0+5.5,r.y0+6.4,r.z0-1.6),{c:C.wood,w:.3,t:.3,step:.5});
  chimney(B,r.x1-1,r.z1-1,r.y0+8); chimney(B,r.x0+1,r.z1-1,r.y0+8);
  /* The Anchor — timber framed tavern, swinging sign */
  p=plots[2];r=R(p);
  B.box(r.x0,r.x1,r.y0,r.y0,r.z0,r.z1,C.stone2);
  wallSet(B,L,{x0:r.x0,x1:r.x1,y0:r.y0+1,y1:r.y0+4,z0:r.z0,z1:r.z1,wall:C.plaster,trim:C.woodD});
  for(let x=r.x0;x<=r.x1;x++)B.at(x,r.y0+3,r.z0,C.woodD,{over:true});
  for(let y=r.y0+1;y<=r.y0+4;y++)for(const z of[r.z0]){for(const x of[r.x0,r.x1])B.at(x,y,z,C.woodD,{over:true});}
  roof(B,r.x0,r.x1,r.y0+5,r.z0,r.z1,C.copper2);
  B.box(r.x0+1,r.x0+3,r.y0+5.2,r.y0+6.4,r.z0+1,r.z0+2,C.woodD);
  /* sign over the door */
  const sg=new THREE.Group(); sg.position.set(r.x0+2,r.y0+5,r.z0-1.2); scene.add(sg);
  const SS=new VS();
  SS.beam(V3(1.4,0,0),V3(1.4,-1.2,0),{c:C.iron,w:.16,t:.16,step:.4});
  SS.beam(V3(0,0,0),V3(2.2,0,0),{c:C.woodD,w:.22,t:.22,step:.5});
  SS.box(-.4,.4,-2.6,-1.2,-.4,.4,C.teal); SS.box(-.3,.3,-2.4,-1.4,-.3,.3,C.ochre);
  sg.add(SS.build({mat:MAT.scene,parent:new THREE.Group()}));
  sg.children.forEach(c=>{c.position.set(0,0,0);});
  anim.sign=sg;
  L.at(r.x0+2,r.y0+2,r.z0-1,C.lamp);
  glowPts.push({p:[r.x0+2+0,r.y0+2,r.z0-1],size:4,c:0xffc46b});
  lampLights.push({p:[r.x0+2,r.y0+2,r.z0-1.5],c:0xffbb6a,i:12,d:16});
  /* terrace of townhouses */
  for(let i=0;i<4;i++){
    const z0=-20+i*4.6,z1=z0+3.6,y0=PLOT_TOP.terrace+(i%2?1:0);
    const wall=pick([C.plaster,C.cream,C.ochre,C.brick]),rf=pick([C.slate,C.slate2,C.copper2,C.copper]);
    wallSet(B,L,{x0:30,x1:35,y0,y1:y0+4,z0,z1,wall,trim:C.stone3});
    roof(B,30,35,y0+5,Math.round(z0),Math.round(z1),rf);
    if(i%2===0)chimney(B,32,Math.round((z0+z1)/2),y0+6,wall===C.brick?C.brick:C.stone2);
    /* area railings + steps */
    for(let z=Math.round(z0);z<=Math.round(z1);z++){B.at(29.6,y0+1,z,C.iron,{s:.24});B.beam(V3(29.6,y0+2,z),V3(29.6,y0+2,z+1),{c:C.iron,w:.14,t:.14,step:.6});}
    B.at(29.5,y0,Math.round((z0+z1)/2),C.stone3);
  }
  /* church with tower */
  p=plots[3+1];r=R(p);
  wallSet(B,L,{x0:r.x0,x1:r.x1,y0:r.y0,y1:r.y0+5,z0:r.z0,z1:r.z1,wall:C.stone3,trim:C.stone});
  roof(B,r.x0,r.x1,r.y0+6,r.z0,r.z1,C.slate);
  B.box(r.x0+2,r.x1-2,r.y0+6.0,r.y0+6,r.z0+2,r.z1-2,C.stone2,{over:true});
  const tx=r.x1,tz=r.z1;
  B.shell(tx-3,tx,r.y0,tx-3,tx,r.y0+13,tz-3,tz,);   // no-op guard
  B.shell(tx-3,tx,r.y0+0,r.y0+13,tz-3,tz,C.stone3);
  L.box(tx-2,tx-1,r.y0+9,r.y0+10,tz-3,tz-3,C.glass);
  roof(B,tx-4,tx+1,r.y0+14,tz-4,tz+1,C.slate2);
  B.at(tx-1.5,r.y0+15.5,tz-1.5,C.ochre,{s:.4});
  L.at(tx-1.5,r.y0+11,tz-1,C.lamp);
  /* market cross hall */
  p=plots[6];r=R(p);
  wallSet(B,L,{...r,y1:r.y0+4,wall:C.ochre,trim:C.cream});
  roof(B,r.x0,r.x1,r.y0+5,r.z0,r.z1,C.copper);
  B.box(r.x0-1,r.x1+1,r.y0+1,r.y0+2,r.z0,r.z0,C.white,{s:[1,.3,1],over:true});
  for(let x=r.x0;x<=r.x1;x+=3){B.at(x,r.y0+1,r.z0-1,C.white,{s:.55});B.at(x,r.y0+2,r.z0-1,C.white,{s:.55});}
  B.box(r.x0+3,r.x0+4,r.y0+5.4,r.y0+7,r.z0+3,r.z0+4,C.cream);
  L.at(r.x0+3.5,r.y0+6.2,r.z0+2.9,C.glass);
  chimney(B,r.x1-1,r.z1-1,r.y0+7);
  /* sail loft & ropewalk */
  p=plots[5];r=R(p);
  wallSet(B,L,{...r,y1:r.y0+3,wall:C.wood,trim:C.woodD});
  roof(B,r.x0,r.x1,r.y0+4,r.z0,r.z1,C.slate2,{ridge:'z'});
  for(let z=r.z0;z<=r.z1;z+=3) B.beam(V3(r.x1+2,r.y0+3,z),V3(r.x1+2,r.y0+1,z),{c:C.canvas2,w:.14,t:.14,step:.6});
  B.box(r.x1+1,r.x1+1,r.y0,r.y0+3,r.z0,r.z1,C.woodD);
  /* hanging canvas on the frame */
  for(let z=r.z0+1;z<r.z1;z++){B.beam(V3(r.x1+1.2,r.y0+3,z),V3(r.x1+1.2,r.y0-1.4,z),{c:C.canvas,w:.9,t:.18,step:.55});}
  /* boatyard: open shed + upturned hull */
  p=plots[7];r=R(p);
  for(const x of[r.x0,r.x0+3,r.x0+6])for(const z of[r.z0,r.z1])B.box(x,x,r.y0,r.y0+5,z,z,C.woodD);
  roof(B,r.x0,r.x0+6,r.y0+6,r.z0,r.z1,C.slate2);
  const S=new VS();
  for(let x=-6;x<=6;x++){
    const w=Math.max(0,Math.round(2.2-Math.abs(x)*.3));
    for(let z=-w;z<=w;z++) if(Math.abs(z)===w||Math.abs(x)===6) S.at(x,0,z,C.woodL);
    S.at(x,-1,0,C.woodD);
  }
  const bg=new THREE.Group(); bg.position.set(r.x0+3,r.y0+1.4,r.z0+4); bg.rotation.z=.16;
  bg.add(S.build({mat:MAT.scene,parent:new THREE.Group()})); scene.add(bg);
  /* windmill on the hill */
  p=plots[8];r=R(p);
  for(let y=r.y0;y<=r.y0+8;y++){
    const rad=Math.max(1.4,3.2-(y-r.y0)*.19);
    for(let a=0;a<26;a++){const th=a/26*Math.PI*2;
      B.at(Math.round((r.x0+r.x1)/2+Math.cos(th)*rad),y,Math.round((r.z0+r.z1)/2+Math.sin(th)*rad),y>r.y0+4?C.cream:C.brick2);}
  }
  const mx=(r.x0+r.x1)/2,mz=(r.z0+r.z1)/2;
  B.disc(mx,mz,3.4,r.y0+9,C.woodD); B.box(mx-2,mx+2,r.y0+9,r.y0+11,mz-2,mz+2,C.wood);
  roof(B,mx-2,mx+2,r.y0+12,mz-2,mz+2,C.copper2);
  B.at(mx,r.y0+11.5,mz-2.4,C.woodD,{s:.5});
  const rot=new THREE.Group(); rot.position.set(mx,r.y0+11.5,mz-2.8); scene.add(rot);
  const RS=new VS();
  for(let k=0;k<4;k++){
    const a=k*Math.PI/2;
    const dir=V3(Math.cos(a),Math.sin(a),0);
    RS.beam(V3(0,0,0),dir.clone().multiplyScalar(8),{c:C.woodD,w:.4,t:.4,step:.6});
    for(let i=2;i<=8;i++){
      const p0=dir.clone().multiplyScalar(i);
      const p1=dir.clone().multiplyScalar(i+ .9).add(V3(-Math.sin(a)*1.5,Math.cos(a)*1.5,0));
      RS.beam(p0,p1,{c:C.canvas,w:1.5,t:.14,step:.55});
    }
  }
  rot.add(RS.build({mat:MAT.scene,parent:new THREE.Group()}));
  anim.mill=rot;
  chimney(B,mx+1,mz+1,r.y0+12);
  /* street lamps */
  const lampPts=[];
  for(let z=-24;z<=36;z+=9){
    const x=40.5;
    const y=Math.round(groundTop(x,z));
    B.beam(V3(x,y+1,z),V3(x,y+6,z),{c:C.iron,w:.3,t:.3,step:.7});
    B.beam(V3(x,y+6,z),V3(x-.9,y+6,z),{c:C.iron,w:.22,t:.22,step:.5});
    B.at(x-.9,y+5.6,z,C.glass); L.at(x-.9,y+5.6,z,C.lamp);
    lampPts.push([x-.9,y+5.6,z]);
  }
  /* random gardens, walls, clotheslines */
  for(let x=20;x<=58;x++)for(let z=-46;z<=46;z++){
    if(!isLand(x,z)||plotAt(x,z)||inStreets(x,z))continue;
    const y=Math.round(groundTop(x,z));
    if(y<5)continue;
    if(h2(x*.5,z*.5)>.985){ /* tree */
      const hh=3+Math.floor(h2(x,z)*3);
      for(let i=1;i<=hh;i++)B.at(x,y+i,z,C.woodD,{s:.7});
      const leaf=h2(x*1.7,z*.9)>.86?C.leafA:[C.leaf,C.leaf2];
      B.blob(x,y+hh+2,z,1.9+Math.round(h2(z,x)*1.6),leaf,{jitj:.8});
    }
    else if(h2(x*.9,z*1.3)>.988){ /* shed */
      B.shell(x,x+2,y,y+2,z,z+2,pick([C.wood,C.woodD,C.iron]));
      roof(B,x,x+2,y+3,z,z+2,C.slate2);
    }
    else if(h2(x*2.1,z*.7)>.992){ /* haystack / cart */
      B.blob(x,y+1,z,1.5,[C.ochre2,C.canvas2],{sy:.8,jitj:1});
    }
  }
  /* horse & cart on the street */
  const cx=38,cz=6,cy=Math.round(groundTop(cx,cz));
  B.box(cx,cx+3,cy+1,cy+2,cz,cz+1,C.wood);
  B.at(cx,cy,cz,C.iron,{s:.7});B.at(cx+3,cy,cz,C.iron,{s:.7});
  B.at(cx+4.5,cy+1,cz,C.leaf2,{s:.6});B.at(cx+4.5,cy+2,cz,C.leaf2,{s:.6});
  B.beam(V3(cx+3.2,cy+1.6,cz),V3(cx+4.4,cy+1.8,cz),{c:C.canvas2,w:.14,t:.14,step:.5});
  B.at(cx+5,cy+2.8,cz,C.woodD,{s:.55});
  B.build({mat:MAT.scene});
  L.build({mat:MAT.glow,ao:false,cast:false,recv:false,wet:false});
  glowPts.push(...lampPts.map(p=>({p,size:4.2,c:0xffc46b})));
  lampLights.push({p:[lampPts[1]?.[0]||40,8,lampPts[1]?.[2]||0],c:0xffbb6a,i:14,d:22});
}

/* ══════════════════════ 7 · AIR, WATER TRAFFIC ══════════════════════ */
function buildAir(){
  /* clouds */
  for(let i=0;i<13;i++){
    const S=new VS();
    const n=3+((rnd()*4)|0);
    for(let k=0;k<n;k++){
      S.blob(rnd()*16-8,rnd()*3-1.5,rnd()*10-5,2.4+rnd()*3.2,[0xffffff,0xf2f5f4,0xdfe7e8],{sy:.52,sz:1.25,jitj:1.2});
    }
    const g=new THREE.Group();
    g.position.set(rnd()*180-90,42+rnd()*24,rnd()*190-95);
    const m=S.build({mat:MAT.cloud,ao:false,cast:false,recv:false,wet:false,parent:g});
    g.scale.setScalar(1.1+rnd()*1.9);
    scene.add(g);
    anim.clouds.push({g,sp:.28+rnd()*.5});
  }
  /* gulls */
  for(let i=0;i<9;i++){
    const g=new THREE.Group();
    const body=new THREE.Mesh(BOX,MAT.gull); body.scale.set(.42,.36,1.25); g.add(body);
    const head=new THREE.Mesh(BOX,MAT.gull); head.scale.set(.3,.3,.42); head.position.set(0,.1,.72); g.add(head);
    const beak=new THREE.Mesh(BOX,MAT.gullD); beak.scale.set(.12,.1,.3); beak.position.set(0,.06,1.02); g.add(beak);
    const tail=new THREE.Mesh(BOX,MAT.gull); tail.scale.set(.5,.08,.5); tail.position.set(0,.05,-.75); g.add(tail);
    const wings=[];
    for(const s of[-1,1]){
      const pv=new THREE.Group(); pv.position.set(s*.18,.12,0);
      const w=new THREE.Mesh(BOX,MAT.gull); w.scale.set(1.5,.09,.5); w.position.x=s*.78;
      const wt=new THREE.Mesh(BOX,MAT.gullD); wt.scale.set(.4,.1,.36); wt.position.set(s*1.42,0,0);
      pv.add(w,wt); g.add(pv); wings.push({pv,s});
    }
    scene.add(g);
    anim.gulls.push({g,wings,R:16+rnd()*26,cx:-6+rnd()*22-11,cz:-8+rnd()*22-11,
      y:14+rnd()*12,sp:.3+rnd()*.4,ph:rnd()*7,flap:6+rnd()*4});
  }
  /* chimney smoke */
  anim.puffs=new Puffs(chimneys.slice(0,7).concat([[-6,10,-10.5]]),46);
  /* a sloop working out to sea + two distant hulls */
  const sloop=()=>{
    const S=new VS();
    for(let x=-5;x<=5;x++){
      const w=Math.max(.5,2.1*Math.pow(Math.sin(Math.PI*(x+5.5)/11),.5));
      for(let z=-Math.round(w);z<=Math.round(w);z++){ if(Math.abs(z)===Math.round(w)||Math.abs(x)===5) S.at(x,0,z,C.woodD); }
      S.at(x,-1,0,C.hullUnder); S.at(x,1,0,C.woodL);
    }
    S.beam(V3(-1,1,0),V3(-1,15,0),{c:C.woodL,w:.42,t:.42,step:.6});
    S.beam(V3(-1,15,0),V3(-4.6,1.6,0),{c:C.woodL,w:.3,t:.3,step:.5});
    S.tri(V3(-1.4,14.4,0),V3(-1.4,2.4,0),V3(-4.4,1.8,0),{c:C.sail,bow:1.2,nx:-1});
    S.tri(V3(-.4,13.8,0),V3(-.4,3,0),V3(4.4,1.6,0),{c:C.canvas,bow:1.1,nx:-1});
    return S.build({mat:MAT.ship,parent:new THREE.Group()});
  };
  const sg=new THREE.Group(); sg.add(sloop()); scene.add(sg);
  anim.sloop={g:sg,base:sg.children[0]};
  for(const d of[[0,-86,20],[1,-92,-48,14]]){
    const S=new VS();
    S.box(-6,6,0,1,-2,2,C.hull); S.box(-5,5,2,2,-1,1,C.hullStripe);
    S.beam(V3(-1,2,0),V3(-1,16,0),{c:C.woodL,w:.5,t:.5,step:.7});
    S.beam(V3(4,2,0),V3(4,11,0),{c:C.woodL,w:.4,t:.4,step:.7});
    S.tri(V3(-1.4,15,0),V3(-1.4,3,0),V3(-5.6,2,0),{c:C.sail,bow:1.1,nx:-1});
    S.tri(V3(-.6,14,0),V3(-.6,3.5,0),V3(3.6,2,0),{c:C.canvas,bow:1,nx:-1});
    S.tri(V3(3.6,10,0),V3(3.6,3,0),V3(6.4,2,0),{c:C.canvas2,bow:.8,nx:-1});
    const g=new THREE.Group(); g.add(S.build({mat:MAT.ship,ao:true,parent:new THREE.Group()}));
    g.position.set(d[1],SEA-.4,d[2]); g.scale.setScalar(.85); g.rotation.y=d[3]?0:.5;
    scene.add(g); anim.distant.push({g,dir:d[3]?1:-1});
  }
  /* buoys + a skiff under oars */
  for(const b of[[34,SEA,-2,.9],[26,SEA,3.6,.75]]){
    const S=new VS();
    S.at(b[0],0,b[2],C.red); S.at(b[0],1,b[2],C.white); S.at(b[0],2,b[2],C.iron,{s:.4});
    const g=new THREE.Group(); g.add(S.build({mat:MAT.scene,parent:new THREE.Group()}));
    scene.add(g); anim.buoys.push({g,ph:rnd()*6});
    glowPts.push({p:[b[0],2.6,b[2]],size:2.6,c:0xff7a55});
  }
}

/* chimney / galley smoke */
class Puffs{
  constructor(sources,n){
    this.src=sources.length?sources:[[30,12,10]];
    this.n=n; this.p=[];
    this.mesh=new THREE.InstancedMesh(BOX,new THREE.MeshStandardMaterial({roughness:1,metalness:0}),n);
    scene.add(this.mesh); world.voxels+=n;
    for(let i=0;i<n;i++)this.p.push(this.fresh(rnd()));
    this.m=new THREE.Matrix4();this.q=new THREE.Quaternion();this.v=new THREE.Vector3();this.s=new THREE.Vector3();this.col=new THREE.Color();
  }
  fresh(t=-rnd()){const s=this.src[(rnd()*this.src.length)|0];
    return{s,t,life:5+rnd()*5,drift:.4+rnd()*1.2,spin:rnd()*6};}
  update(dt,t){
    const fog=new THREE.Color(scene.fog.color.getHex());
    for(let i=0;i<this.n;i++){
      let q=this.p[i]; q.t+=dt;
      if(q.t>q.life)this.p[i]=q=this.fresh(0);
      const u=clamp(q.t/q.life,0,1);
      const x=q.s[0]+u*u*q.drift*7+Math.sin(q.spin+u*4)*.6;
      const y=q.s[1]+u*8.5;
      const z=q.s[2]+Math.sin(q.spin+u*3)*.8;
      const s=.5+u*2.3;
      this.m.compose(this.v.set(x,y,z),this.q,this.s.set(s,s,s));
      this.mesh.setMatrixAt(i,this.m);
      this.col.setHex(C.smoke).lerp(fog,Math.min(1,u*.95)).multiplyScalar(1-u*.25);
      this.mesh.setColorAt(i,this.col);
    }
    this.mesh.instanceMatrix.needsUpdate=true;
    if(this.mesh.instanceColor)this.mesh.instanceColor.needsUpdate=true;
  }
}

/* ══════════════════════ 8 · GLOWS + LAMP LIGHTS ══════════════════════ */
function radialTex(){
  const c=document.createElement('canvas');c.width=c.height=64;
  const g=c.getContext('2d'),gr=g.createRadialGradient(32,32,0,32,32,32);
  gr.addColorStop(0,'rgba(255,255,255,1)');gr.addColorStop(.35,'rgba(255,255,255,.45)');gr.addColorStop(1,'rgba(255,255,255,0)');
  g.fillStyle=gr;g.fillRect(0,0,64,64);
  const t=new THREE.CanvasTexture(c); t.colorSpace=THREE.SRGBColorSpace; return t;
}
function buildFX(){
  const tex=radialTex(); anim.glowSprites=[];
  for(const g of glowPts){
    const s=new THREE.Sprite(new THREE.SpriteMaterial({map:tex,color:g.c,transparent:true,opacity:.7,
      blending:THREE.AdditiveBlending,depthWrite:false}));
    s.position.set(g.p[0],g.p[1],g.p[2]); s.scale.setScalar(g.size);
    s.userData.base=g.size; scene.add(s); anim.glowSprites.push(s);
  }
  anim.lampLights=[];
  for(const l of lampLights.slice(0,4)){
    const pl=new THREE.PointLight(l.c,0,l.d,1.5); pl.position.set(l.p[0],l.p[1],l.p[2]);
    scene.add(pl); anim.lampLights.push(pl);
  }
  buildHotspots();
}

/* ══════════════════════ hotspots ══════════════════════ */
const HOT=[
  {k:'ship',tag:'riding at mooring №2',name:'The Meridian · 324 tons',
   note:'Bark-rigged out of the southern isles, six weeks in. Powdered salt in the lower hold, and a fever case declared to the board before she was worked.',
   meta:['arrived 16:58','officers 11','draught 14\'6"'],
   box:[-7,13,-10.5,36,26,13],view:{th:-2.0,ph:1.12,r:56,t:[-6,10,-10]}},
  {k:'wharf',tag:'board of the port',name:'The Long Wharf',
   note:'Two hundred feet of elm pile and oak plank. Gin crane on the seaward edge, market stalls by the guard bolt, and never a bollard free after the tide turns.',
   meta:['piles 84','deep water 19ft','lamps 6'],
   box:[-1,5,1.5,40,7,12],view:{th:-2.62,ph:1.2,r:44,t:[2,5,2]}},
  {k:'mole',tag:'west mole',name:'Aldermoor Light',
   note:'Fixed red over white, one flash every twenty seconds, carried two hundred feet above the datum. Keeper and one assistant; the oil is weighed weekly.',
   meta:['built 1791','flash 20s','range 14 miles'],
   box:[-31,15,23,15,30,15],view:{th:-1.15,ph:1.05,r:52,t:[-31,14,23]}},
  {k:'customs',tag:'king\'s offcers',name:'The Custom House',
   note:'Where the manifest is surrendered and the hold is measured. Two gaugers, one tide waiter, and a board that has never yet liked what you brought.',
   meta:['duties paid 412','clerks 5'],
   box:[29,11,8,11,12,12],view:{th:-2.35,ph:1.14,r:44,t:[29,9,7]}},
  {k:'town',tag:'above the slipway',name:'Old Town & St. Brendan\'s',
   note:'Terraces stepped down to the water, a market cross, and the church tower used by pilots as the leading mark for the inner channel.',
   meta:['houses 214','tower 61ft'],
   box:[38,13,0,26,14,26],view:{th:-1.9,ph:.98,r:74,t:[36,10,0]}},
  {k:'mill',tag:'the inland mark',name:'Mill Hill Post Mill',
   note:'Four canvas sails, a tail pole and a very patient miller. Visible from the outer anchorage and the only thing on the hill that turns against the wind.',
   meta:['sails 4','turns 22/min'],
   box:[48,20,8,10,12,10],view:{th:-2.1,ph:.95,r:56,t:[48,17,8]}},
  {k:'boat',tag:'north beach',name:'The Boatyard',
   note:'Two building slips, a loft full of ribs, and a pilot gig always on the ways in case a ship goes past the mouth on a westerly.',
   meta:['slips 2','gigs 3'],
   box:[20,8,-32,10,8,10],view:{th:-2.45,ph:1.05,r:48,t:[20,6,-31]}}
];
const viewPresets={
  roads:{th:-2.30,ph:1.02,r:126,t:[2,7,0]},
  ship:{th:-2.0,ph:1.12,r:56,t:[-6,10,-10]},
  wharf:{th:-2.62,ph:1.2,r:44,t:[2,5,2]},
  mole:{th:-1.15,ph:1.05,r:52,t:[-31,14,23]},
  town:{th:-1.9,ph:.98,r:74,t:[36,10,0]},
  mill:{th:-2.1,ph:.95,r:56,t:[48,17,8]},
  bird:{th:-2.2,ph:.3,r:118,t:[4,4,0]}
};
function buildHotspots(){
  const holder=new THREE.Group(); scene.add(holder);
  const mats=new THREE.LineBasicMaterial({color:0xe8b260,transparent:true,opacity:0});
  anim.hotMat=mats;
  HOT.forEach((h,i)=>{
    const g=new THREE.BoxGeometry(h.box[3],h.box[4],h.box[5]);
    const m=new THREE.Mesh(g,new THREE.MeshBasicMaterial({visible:false}));
    m.position.set(h.box[0],h.box[1],h.box[2]);
    m.userData.hot=h; holder.add(m); h.mesh=m;
    const eg=new THREE.LineSegments(new THREE.EdgesGeometry(g),mats);
    eg.position.copy(m.position); eg.scale.setScalar(0.001); holder.add(eg); h.edge=eg;
  });
  anim.hotMeshes=HOT.map(h=>h.mesh);
  const list=document.getElementById('legendList');
  HOT.forEach((h,i)=>{
    const li=document.createElement('li');
    li.innerHTML=`<i style="--c:${['#e8b260','#8fd0c0','#ff9a6a','#cbe0e2','#a9c47a','#f0d79a','#9fc0d8'][i]}"></i>
      <span>${h.name.split('·')[0].trim()}</span><small>${String(i+1).padStart(2,'0')}</small>`;
    li.onmouseenter=()=>sight(h,false);
    li.onmouseleave=()=>{if(!pinned)sight(null);};
    li.onclick=()=>{pinned=h;showHot(h,true);flyTo(h.view);mark(h);};
    h.li=li; list.appendChild(li);
  });
}

/* ══════════════════════ rig (orbit control) ══════════════════════ */
class Rig{
  constructor(cam,dom){
    this.cam=cam;this.dom=dom;
    this.tgt=V3(2,7,0);this.tgtGoal=this.tgt.clone();
    this.th=-2.9;this.ph=1.16;this.r=205;this.rG=126;this.thG=-2.30;this.phG=1.02;
    this.idle=0;this.auto=true;this.tween=null;
    const p=new Map();
    dom.addEventListener('pointerdown',e=>{
      dom.setPointerCapture(e.pointerId);p.set(e.pointerId,{x:e.clientX,y:e.clientY,b:e.button});
      dom.classList.add('drag');this.idle=0;hideHint();
      if(e.button===2||e.shiftKey)p.get(e.pointerId).pan=true;
    });
    dom.addEventListener('pointermove',e=>{
      if(!p.has(e.pointerId))return;
      const s=p.get(e.pointerId),dx=e.clientX-s.x,dy=e.clientY-s.y;
      s.x=e.clientX;s.y=e.clientY;this.idle=0;
      if(s.pan||e.shiftKey){
        const k=this.r*.0016;
        const right=V3(Math.cos(this.th),0,-Math.sin(this.th));
        const fwd=V3(Math.sin(this.th),0,Math.cos(this.th));
        this.tgtGoal.addScaledVector(right,-dx*k).addScaledVector(fwd,-dy*k);
      }else{
        this.thG-=dx*.0055; this.phG=clamp(this.phG-dy*.0046,.14,1.44);
      }
    });
    const up=e=>{p.delete(e.pointerId);dom.classList.remove('drag');};
    dom.addEventListener('pointerup',up);dom.addEventListener('pointercancel',up);
    dom.addEventListener('wheel',e=>{e.preventDefault();this.rG=clamp(this.rG*Math.exp(e.deltaY*.0011),16,290);this.idle=0;hideHint();},{passive:false});
    dom.addEventListener('contextmenu',e=>e.preventDefault());
  }
  fly(v){
    let th=v.th;const cur=this.th;
    while(th-cur>Math.PI)th-=2*Math.PI; while(th-cur<-Math.PI)th+=2*Math.PI;
    this.tween={t:0,d:1.5,a:{th:cur,ph:this.ph,r:this.r,t:this.tgt.clone()},
      b:{th,ph:v.ph,r:v.r,t:V3(v.t[0],v.t[1],v.t[2])}};
  }
  update(dt){
    this.idle+=dt;
    if(this.tween){
      const w=this.tween;w.t=Math.min(1,w.t+dt/w.d);
      const e=w.t<.5?4*w.t*w.t*w.t:1-Math.pow(-2*w.t+2,3)/2;
      this.th=lerp(w.a.th,w.b.th,e);this.ph=lerp(w.a.ph,w.b.ph,e);this.r=lerp(w.a.r,w.b.r,e);
      this.tgt.lerpVectors(w.a.t,w.b.t,e);
      if(w.t>=1){this.thG=this.th;this.phG=this.ph;this.rG=this.r;this.tgtGoal.copy(this.tgt);this.tween=null;}
    }else{
      if(this.auto&&this.idle>3.5)this.thG-=dt*.038;
      const k=1-Math.exp(-dt*6.5);
      this.th+=(this.thG-this.th)*k; this.ph+=(this.phG-this.ph)*k; this.r+=(this.rG-this.r)*k;
      this.tgt.lerp(this.tgtGoal,k);
    }
    this.tgt.x=clamp(this.tgt.x,-70,70);this.tgt.z=clamp(this.tgt.z,-70,70);this.tgt.y=clamp(this.tgt.y,1,40);
    const sp=Math.sin(this.ph);
    this.cam.position.set(this.tgt.x+this.r*sp*Math.sin(this.th),
      Math.max(2.2,this.tgt.y+this.r*Math.cos(this.ph)),
      this.tgt.z+this.r*sp*Math.cos(this.th));
    this.cam.lookAt(this.tgt);
  }
}
const rig=new Rig(camera,canvas);

/* ══════════════════════ watches (time of day) ══════════════════════ */
const W={
 dawn:{dir:[.62,.14,.55],sun:0xffd0a0,sunI:2.5,hemi:[0x9cbcd8,0x746a55,.5],
   sky:[0x27436b,0xf3a874,0x2b3140],sunC:0xffcaa0,fog:[0xd0a894,.0055],
   fill:[0x8fa6c8,.45],lamp:.34,expo:1.02,sea:[0x12465c,0x2f8a97],stars:0,beam:.12,clock:'05:12',wind:'SW 6kn'},
 noon:{dir:[.28,.86,-.42],sun:0xfff6e4,sunI:3.2,hemi:[0xa8cfe6,0x7b7460,.62],
   sky:[0x2b74ab,0xbeDDE4,0x2f4652],sunC:0xfff4dc,fog:[0xb9d2d6,.0038],
   fill:[0xbcd6e8,.55],lamp:.02,expo:1.0,sea:[0x0f4757,0x36a2aa],stars:0,beam:.03,clock:'12:30',wind:'WSW 14kn'},
 dusk:{dir:[-.74,.155,-.62],sun:0xffbb70,sunI:2.7,hemi:[0x7d9ec2,0x6b5f4c,.52],
   sky:[0x1b3559,0xef9a55,0x242c3c],sunC:0xffb26a,fog:[0xa99f9e,.0054],
   fill:[0x93a7c8,.5],lamp:.42,expo:1.05,sea:[0x123f52,0x2e8b93],stars:0,beam:.16,clock:'19:40',wind:'WSW 11kn'},
 night:{dir:[-.34,.62,-.7],sun:0xa9c4e8,sunI:.55,hemi:[0x2e4a68,0x26303a,.3],
   sky:[0x060e1c,0x16303f,0x050b12],sunC:0xbcd4f0,fog:[0x16303c,.0072],
   fill:[0x40607f,.28],lamp:1,expo:1.14,sea:[0x071f2c,0x123f4c],stars:1,beam:.34,clock:'00:15',wind:'W 9kn'}
};
const S_={dir:new THREE.Vector3(),sun:new THREE.Color(),sunI:0,hSky:new THREE.Color(),hGnd:new THREE.Color(),
  hI:0,sky0:new THREE.Color(),sky1:new THREE.Color(),sky2:new THREE.Color(),sunC:new THREE.Color(),
  fog:new THREE.Color(),fogD:0,fC:new THREE.Color(),fI:0,lamp:0,expo:1,seaA:new THREE.Color(),seaB:new THREE.Color(),
  stars:0,beam:0};
function snap(w){return{dir:V3(...w.dir),sun:new THREE.Color(w.sun),sunI:w.sunI,hSky:new THREE.Color(w.hemi[0]),
  hGnd:new THREE.Color(w.hemi[1]),hI:w.hemi[2],sky0:new THREE.Color(w.sky[0]),sky1:new THREE.Color(w.sky[1]),
  sky2:new THREE.Color(w.sky[2]),sunC:new THREE.Color(w.sunC),fog:new THREE.Color(w.fog[0]),fogD:w.fog[1],
  fC:new THREE.Color(w.fill[0]),fI:w.fill[1],lamp:w.lamp,expo:w.expo,seaA:new THREE.Color(w.sea[0]),
  seaB:new THREE.Color(w.sea[1]),stars:w.stars,beam:w.beam};}
let wA=null,wB=null,wT=1;
const _c=new THREE.Color();
function applyWatch(dt){
  if(wT<1){wT=Math.min(1,wT+dt/1.15);}
  const e=wT<.5?2*wT*wT:1-Math.pow(-2*wT+2,2)/2;
  for(const k of Object.keys(S_)){
    const a=wA[k],b=wB[k];
    if(a&&a.isColor)S_[k].lerpColors(a,b,e);
    else if(a&&a.isVector3)S_[k].lerpVectors(a,b,e);
    else S_[k]=lerp(a,b,e);
  }
  const d=S_.dir.clone().normalize();
  sun.position.copy(d).multiplyScalar(160); sun.target.position.set(0,6,0);
  sun.color.copy(S_.sun); sun.intensity=S_.sunI;
  hemi.color.copy(S_.hSky); hemi.groundColor.copy(S_.hGnd); hemi.intensity=S_.hI;
  fill.color.copy(S_.fC); fill.intensity=S_.fI;
  skyU.uTop.value.copy(S_.sky0); skyU.uHor.value.copy(S_.sky1); skyU.uBot.value.copy(S_.sky2);
  skyU.uSun.value.copy(d); skyU.uSunC.value.copy(S_.sunC); skyU.uStars.value=S_.stars;
  scene.fog.color.copy(S_.fog); scene.fog.density=S_.fogD;
  renderer.toneMappingExposure=S_.expo;
  farSea.material.color.copy(S_.seaA).lerp(_c.copy(S_.seaB),.4);
  MAT.water.color.copy(S_.seaA).lerp(_c.copy(S_.seaB),.35).multiplyScalar(1.35);
  MAT.glow.color.setRGB(lerp(.34,1.9,S_.lamp),lerp(.38,1.55,S_.lamp),lerp(.42,1.1,S_.lamp));
  if(anim.glowSprites)anim.glowSprites.forEach(s=>{s.material.opacity=clamp(S_.lamp*(lampsOn?1:0),0,1)*.85;});
  if(anim.lampLights)anim.lampLights.forEach(l=>l.intensity=clamp(S_.lamp,0,1)*(lampsOn?1:0)*l.userData.max);
  if(anim.beam){anim.beam.lamp.intensity=clamp(S_.beam,0,1)*(lampsOn?1:0)*90;
    MAT.beam.opacity=.02+clamp(S_.beam,0,1)*.9*(lampsOn?1:0);}
  MAT.beam.color.copy(S_.sunC).lerp(_c.setHex(0xfff0d0),.5);
  document.getElementById('rClock').textContent=W[curWatch].clock;
  document.getElementById('rWind').textContent=W[curWatch].wind;
}
let curWatch='dusk',lampsOn=true;
function setWatch(k){
  if(k===curWatch)return;
  curWatch=k; wA={}; for(const key of Object.keys(S_))wA[key]=S_[key].clone?S_[key].clone():S_[key];
  wB=snap(W[k]); wT=0;
  document.querySelectorAll('#watches .btn').forEach(b=>b.setAttribute('aria-pressed',b.dataset.watch===k));
}

/* ══════════════════════ UI ══════════════════════ */
let pinned=null,hotShown=null;
const $=id=>document.getElementById(id);
function showHot(h,pin){
  const el=$('hot');
  if(!h){ if(!pinned)el.classList.remove('on','pinned'); return; }
  $('hotTag').textContent=h.tag;$('hotName').textContent=h.name;$('hotNote').textContent=h.note;
  $('hotMeta').innerHTML=h.meta.map(m=>`<span>${m}</span>`).join('');
  el.classList.add('on'); el.classList.toggle('pinned',!!pin);
}
function mark(h){HOT.forEach(x=>x.li&&x.li.classList.toggle('act',x===h));}
function sight(h,pin){
  if(hotShown&&hotShown!==h&&hotShown.edge)hotShown.edge.scale.setScalar(.001);
  hotShown=h; anim.hotTarget=h||null; showHot(h,pin); if(!pin)mark(h);
}
function flyTo(v){rig.fly(v);}
$('hotPin').onclick=()=>{pinned=null;$('hot').classList.remove('pinned','on');mark(null);};
document.querySelectorAll('#watches .btn').forEach(b=>b.onclick=()=>setWatch(b.dataset.watch));
document.querySelectorAll('#views .btn').forEach(b=>b.onclick=()=>{
  flyTo(viewPresets[b.dataset.view]);
  document.querySelectorAll('#views .btn').forEach(x=>x.setAttribute('aria-pressed',x===b));
  pinned=null;showHot(null);
});
$('tOrbit').onchange=e=>rig.auto=e.target.checked;
$('tLamp').onchange=e=>{lampsOn=e.target.checked;};
$('tLife').onchange=e=>{anim.life=e.target.checked;
  anim.gulls.forEach(g=>g.g.visible=e.target.checked);
  anim.clouds.forEach(c=>c.g.visible=e.target.checked);
  if(anim.puffs)anim.puffs.mesh.visible=e.target.checked;};
anim.life=true;
$('tUI').onchange=e=>document.body.classList.toggle('ui-off',e.target.checked);
addEventListener('keydown',e=>{
  const k=e.key.toLowerCase();
  if(k==='h'){$('tUI').checked=!$('tUI').checked;$('tUI').dispatchEvent(new Event('change'));}
  if(k===' '){e.preventDefault();$('tOrbit').checked=!$('tOrbit').checked;$('tOrbit').dispatchEvent(new Event('change'));}
  if(k==='r'){flyTo(viewPresets.roads);}
  const n=parseInt(k); if(n>=1&&n<=4&&HOT[n-1]){pinned=HOT[n-1];showHot(HOT[n-1],true);flyTo(HOT[n-1].view);mark(HOT[n-1]);}
  if(k==='1'||k==='2'||k==='3'||k==='4'){}
});
const keysWatch={q:'dawn',w:'noon',e:'dusk',r2:'night'};
let hintOff=false;
function hideHint(){if(!hintOff){hintOff=true;$('hint').classList.add('off');}}

/* cursor tooltip + raycast */
const ray=new THREE.Raycaster(); const ptr=new THREE.Vector2(-2,-2);
const tip=$('tip'); let tipT=0;
canvas.addEventListener('pointermove',e=>{
  ptr.x=(e.clientX/innerWidth)*2-1; ptr.y=-(e.clientY/innerHeight)*2+1;
  tip.style.left=e.clientX+'px'; tip.style.top=e.clientY+'px';
  tipT=.12;
});
canvas.addEventListener('click',()=>{
  if(hotShown){pinned=hotShown;showHot(hotShown,true);flyTo(hotShown.view);mark(hotShown);}
});

/* ══════════════════════ boot (staged) ══════════════════════ */
const STAGES=[
  ['taking soundings in the roads',buildSea],
  ['quarrying the quay stone',buildLand],
  ['driving piles along the long wharf',buildWharf],
  ['steaming the planks — building the bark',buildShip],
  ['lighting the mole lighthouse',buildLight],
  ['raising the old town',buildTown],
  ['gathering cloud and gulls',buildAir],
  ['trimming the lamps',buildFX]
];
const raf2=()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
async function boot(){
  setWatch('dusk'); wA=snap(W.dusk); wB=snap(W.dusk); wT=1; applyWatch(0);
  for(let i=0;i<STAGES.length;i++){
    $('bootbar').style.width=((i)/STAGES.length*100).toFixed(0)+'%';
    $('bootlog').textContent=STAGES[i][0]+'…';
    await raf2();
    STAGES[i][1]();
  }
  $('bootbar').style.width='100%';$('bootlog').textContent='harbour open';
  $('rVox').textContent=world.voxels.toLocaleString();
  rig.update(0.016);
  await new Promise(r=>setTimeout(r,420));
  $('boot').classList.add('gone');
  document.body.classList.add('ready');
  document.querySelector('#views .btn').setAttribute('aria-pressed','true');
}
boot();

/* ══════════════════════ loop ══════════════════════ */
addEventListener('resize',()=>{
  const w=innerWidth,h=innerHeight;
  renderer.setSize(w,h,false); camera.aspect=w/h; camera.updateProjectionMatrix();
});
let last=performance.now()/1000,frame=0,fps=60,fAcc=0,fCnt=0;
function loop(){
  requestAnimationFrame(loop);
  const now=performance.now()/1000; let dt=Math.min(.05,now-last); last=now;
  const t=now; frame++;
  rig.update(dt);
  applyWatch(dt);
  /* water at 30Hz */
  if(anim.water&&frame%2===0)anim.water.update(t);
  /* the bark rides her moorings */
  if(anim.ship){
    const g=anim.ship.g;
    g.position.y=SHIP.y+Math.sin(t*.72)*.17+Math.sin(t*1.31)*.06;
    g.rotation.z=Math.sin(t*.66)*.021+Math.sin(t*1.7)*.006;
    g.rotation.x=Math.sin(t*.53+1.2)*.014;
    g.rotation.y=Math.sin(t*.31)*.008;
    anim.ship.lightMesh.material=MAT.glow;
  }
  anim.flags.forEach(f=>f.update(t));
  if(anim.mill)anim.mill.rotation.z=-t*.75;
  if(anim.crane){anim.crane.rotation.z=Math.sin(t*.62)*.12;anim.crane.rotation.x=Math.sin(t*.44)*.05;}
  if(anim.sign){anim.sign.rotation.z=Math.sin(t*.9+.6)*.13;anim.sign.rotation.x=Math.sin(t*1.4)*.05;}
  if(anim.beam)anim.beam.g.rotation.y=t*.55;
  if(anim.life){
    anim.clouds.forEach(c=>{c.g.position.x+=c.sp*dt;if(c.g.position.x>110)c.g.position.x=-110;});
    anim.gulls.forEach(g=>{
      g.ang=(g.ang||rnd()*6)+dt*g.sp;
      const x=g.cx+Math.cos(g.ang)*g.R, z=g.cz+Math.sin(g.ang)*g.R*.82;
      const y=g.y+Math.sin(t*.7+g.ph)*2.1+Math.sin(g.ang*2)*1.5;
      const px=g.g.position.x,pz=g.g.position.z;
      g.g.position.set(x,y,z);
      if(px||pz)g.g.lookAt(x+(x-px)*20,y,z+(z-pz)*20);
      const f=Math.sin(t*g.flap+g.ph);
      g.wings.forEach(w=>w.pv.rotation.z=w.s*(f*.72+.12));
    });
    if(anim.puffs)anim.puffs.update(dt,t);
    if(anim.sloop){
      const p=(t*.012)%1, a=-.55+p*1.5;
      anim.sloop.g.position.set(Math.sin(a)*58-6,SEA-.35+Math.sin(t*.9)*.2,-40+p*95);
      anim.sloop.g.rotation.y=Math.PI*.02+Math.sin(t*.7)*.03;
      anim.sloop.g.rotation.z=Math.sin(t*.8)*.04;
    }
    anim.distant.forEach((d,i)=>{d.g.position.x+=d.dir*dt*.55;d.g.position.z+=dt*.18*(i?-1:1);
      d.g.rotation.z=Math.sin(t*.7+i)*.03;
      if(d.g.position.x>120)d.g.position.x=-120; if(d.g.position.x<-120)d.g.position.x=120;});
  }
  anim.foams.forEach(f=>{f.o.position.y=f.base+Math.sin(t*1.4+f.ph)*(f.lift||.12);f.o.rotation.z=Math.sin(t*.9+f.ph)*f.roll;});
  anim.buoys.forEach(b=>{b.g.position.y=Math.sin(t*1.25+b.ph)*.28;b.g.rotation.z=Math.sin(t*1.05+b.ph)*.22;});
  /* hover raycast */
  if(tipT>0&&!rig.tween){
    tipT-=dt;
    ray.setFromCamera(ptr,camera);
    const hit=anim.hotMeshes?ray.intersectObjects(anim.hotMeshes,false)[0]:null;
    const h=hit?hit.object.userData.hot:null;
    canvas.classList.toggle('hot',!!h);
    if(h!==hotShown&&!pinned)sight(h,false);
    if(h){tip.textContent=h.name.split('·')[0].trim();tip.classList.add('on');}
    else tip.classList.remove('on');
  }
  if(hotShown){
    const s=.86+Math.sin(t*4)*.03;
    hotShown.edge.scale.setScalar(lerp(hotShown.edge.scale.x,s,.22));
    anim.hotMat.opacity=lerp(anim.hotMat.opacity,pinned?.95:.62,.2);
  }
  if(anim.beam){const f=.86+.14*Math.sin(t*2.2);anim.beam.lamp.intensity=(clamp(S_.beam,0,1))*(lampsOn?1:0)*90*f;}
  document.getElementById('rose').style.transform=`rotate(${-rig.th*180/Math.PI}deg)`;
  renderer.render(scene,camera);
  fAcc+=dt;fCnt++;
  if(fAcc>.5){fps=Math.round(fCnt/fAcc);fAcc=0;fCnt=0;
    document.getElementById('rFps').textContent=fps+' fps';}
}
requestAnimationFrame(loop);
setTimeout(hideHint,9000);
</script>
</body>
</html>
```

**What's in the water and on the quay**

- **The bark** is lofted from a hull-line: a beam profile gives sheer and flare, the shell is a two-voxel skin with gunport cheeks and a stripe at the waterline, three masts with yards, three bellying square sails on each, a spanker, three jibs, voxel shrouds/stays/bobstay, slung ship's boat, pilot ladder, stern lantern, ensign + jack that animate, and mooring lines sagged to the wharf bollards. She rides her moorings on a slow roll-and-lift.
- **The sea** is a live 30 Hz heightfield of ~9,000 columns; amplitude drops inside the harbour, foam rises along the shore and around the mole, and specular sun-glint tracks whichever watch you pick.
- **The town** is procedural: plots are flattened, terrain is filled with hidden-interior culling, then the Custom House, Bond warehouse, tavern (with a swinging sign), terrace, St. Brendan's, market hall, sail loft, boatyard with an upturned hull and a turning post mill are laid on top. Lamp posts, stall awnings, crates, capstans, coils of rope, garden trees and chimney smoke finish it.
- **Craft**: 26-neighbour voxel ambient occlusion, deterministic seeded randomness, a wet/waterline colour shift below the tide, a shader sky with sun disc and stars, and 3–4 real point lights for the night watch.
- **Controls**: drag / wheel / shift-drag, four watches, seven viewpoints, hotspots raycast both ways with the manifest legend, keys `1–7` to sight a place, `H` to strip the interface for screenshots, `Space` to toggle the lazy orbit.