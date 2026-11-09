# Greystone Haven — Plate VII  
*“A sailing ship calling at a harbor”, built from ~50 000 voxels.*

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
<title>Greystone Haven — A Sailing Ship Calling at a Harbor</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400..900;1,9..144,400..700&family=IBM+Plex+Mono:wght@400;500;600&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{
  --ink:#12252f; --ink2:#1d3b4a; --ink3:rgba(18,37,47,.34);
  --paper:#f4e9d6; --paper2:#e8dabf; --paper3:#dccbab;
  --red:#c3402e; --gold:#e0a23c; --teal:#22766f; --sea:#1c5a70;
  --shadow:5px 5px 0 rgba(6,18,24,.42);
}
*{box-sizing:border-box}
html,body{margin:0;height:100%;overflow:hidden;background:#0c1a22;color:var(--ink);
  font-family:'Space Grotesk',system-ui,sans-serif;-webkit-font-smoothing:antialiased}
canvas{display:block;position:fixed;inset:0;touch-action:none;cursor:grab}
canvas.drag{cursor:grabbing}
canvas.pick{cursor:crosshair}

/* ---------- chart overlay ---------- */
#chartgrid{position:fixed;inset:0;pointer-events:none;z-index:2;
  background-image:
    repeating-linear-gradient(to right, rgba(244,233,214,.10) 0 1px, transparent 1px 74px),
    repeating-linear-gradient(to bottom, rgba(244,233,214,.10) 0 1px, transparent 1px 74px);
  mix-blend-mode:overlay;opacity:.75}
#vign{position:fixed;inset:0;pointer-events:none;z-index:3;
  background:radial-gradient(120% 90% at 50% 45%, transparent 42%, rgba(4,14,20,.42) 100%)}
#cross{position:fixed;inset:0;pointer-events:none;z-index:4;opacity:0;transition:opacity .25s}
#cross .h,#cross .v{position:fixed;background:linear-gradient(90deg,transparent,rgba(244,233,214,.55),transparent)}
#cross .h{left:0;right:0;height:1px}
#cross .v{top:0;bottom:0;width:1px;background:linear-gradient(180deg,transparent,rgba(244,233,214,.55),transparent)}

/* ---------- panels ---------- */
.panel{background:var(--paper);border:1px solid var(--ink);box-shadow:var(--shadow);position:relative;z-index:10}
.panel::after{content:"";position:absolute;inset:4px;border:1px solid var(--ink3);pointer-events:none}
.mark{position:absolute;width:9px;height:9px;border:1.5px solid var(--ink);opacity:.65}
.mark.tl{top:-5px;left:-5px;border-right:0;border-bottom:0}
.mark.tr{top:-5px;right:-5px;border-left:0;border-bottom:0}
.mark.bl{bottom:-5px;left:-5px;border-right:0;border-top:0}
.mark.br{bottom:-5px;right:-5px;border-left:0;border-top:0}

/* ---------- title block ---------- */
#title{position:fixed;left:22px;top:20px;width:min(46vw,540px);padding:16px 20px 15px}
#title .kick{font-family:'IBM Plex Mono',monospace;font-size:9.5px;letter-spacing:.24em;text-transform:uppercase;color:var(--red);display:flex;gap:10px;align-items:center}
#title .kick::after{content:"";height:1px;flex:1;background:var(--red);opacity:.55}
#title h1{font-family:'Fraunces',serif;font-weight:900;font-variation-settings:'SOFT' 45,'WONK' 1,'opsz' 120;
  font-size:clamp(26px,3.55vw,50px);line-height:.85;letter-spacing:-.022em;text-transform:uppercase;margin:.22em 0 .3em}
#title h1 .l2{display:block;padding-left:.9em;color:var(--sea)}
#title h1 em{font-style:italic;font-weight:700;text-transform:none;letter-spacing:-.01em;position:relative}
#title h1 em::after{content:"";position:absolute;left:0;right:0;bottom:.06em;height:.11em;background:var(--red);opacity:.85}
#title .rule{display:flex;gap:10px;align-items:center;font-family:'IBM Plex Mono',monospace;font-size:8.5px;letter-spacing:.2em;text-transform:uppercase;color:var(--ink2);margin-bottom:9px}
#title .rule b{flex:1;height:3px;background:repeating-linear-gradient(90deg,var(--ink) 0 3px,transparent 3px 6px);opacity:.5}
#title p{font-size:12.6px;line-height:1.55;margin:0;max-width:44ch;color:#26404c}
#title p b{font-weight:700;color:var(--ink)}

/* ---------- log ---------- */
#log{position:fixed;right:22px;top:20px;width:308px;padding:14px 16px 12px;max-height:min(52vh,430px);display:flex;flex-direction:column}
#log .head{display:flex;justify-content:space-between;align-items:baseline;border-bottom:2px solid var(--ink);padding-bottom:8px;margin-bottom:9px}
#log .head h2{font-family:'Fraunces',serif;font-weight:800;font-size:19px;letter-spacing:.01em;margin:0;text-transform:uppercase}
#log .head span{font-family:'IBM Plex Mono',monospace;font-size:11px;font-weight:600;color:var(--red)}
#log ol{list-style:none;margin:0;padding:0;overflow:auto;scrollbar-width:thin}
#log li{border-left:2px solid var(--gold);padding:0 0 8px 10px;margin-bottom:8px;animation:slip .5s cubic-bezier(.2,.9,.2,1)}
#log li time{font-family:'IBM Plex Mono',monospace;font-size:9.5px;letter-spacing:.14em;color:var(--sea);font-weight:600}
#log li p{margin:2px 0 0;font-size:12.3px;line-height:1.45;color:#243c48}
#log li.sig{border-left-color:var(--red)}
#log li.sig p{font-weight:600;color:var(--ink)}
@keyframes slip{from{opacity:0;transform:translateX(14px)}to{opacity:1;transform:none}}

/* ---------- controls ---------- */
#ctl{position:fixed;left:22px;bottom:22px;padding:13px 15px 15px;width:min(50vw,470px)}
#ctl .lbl{font-family:'IBM Plex Mono',monospace;font-size:8.5px;letter-spacing:.22em;text-transform:uppercase;color:var(--ink2);margin-bottom:9px;display:flex;gap:9px}
#ctl .lbl b{flex:1;height:1px;background:var(--ink3)}
#ctl .chips{display:flex;flex-wrap:wrap;gap:7px}
.chip{font-family:'IBM Plex Mono',monospace;font-size:10px;font-weight:600;letter-spacing:.13em;text-transform:uppercase;
  padding:8px 11px;background:transparent;border:1px solid var(--ink);color:var(--ink);cursor:pointer;
  transition:transform .16s cubic-bezier(.2,.85,.25,1),background .16s,color .16s,box-shadow .16s;box-shadow:2px 2px 0 rgba(6,18,24,.22)}
.chip:hover{transform:translate(-1px,-2px);background:var(--ink);color:var(--paper);box-shadow:4px 4px 0 rgba(6,18,24,.35)}
.chip:active{transform:translate(1px,1px);box-shadow:0 0 0 rgba(0,0,0,0)}
.chip.on{background:var(--red);border-color:var(--red);color:#fff6ea}
.chip.on:hover{background:var(--ink);border-color:var(--ink)}
.chip .v{font-family:'Fraunces',serif;font-weight:800;font-size:11px;letter-spacing:.02em;opacity:.85;margin-left:6px}
.sliders{display:grid;grid-template-columns:1fr 1fr;gap:12px 18px;margin-top:14px}
.sl label{font-family:'IBM Plex Mono',monospace;font-size:8.5px;letter-spacing:.2em;text-transform:uppercase;color:var(--ink2);display:flex;justify-content:space-between}
.sl label span{color:var(--red);font-weight:600}
input[type=range]{-webkit-appearance:none;appearance:none;width:100%;height:16px;background:transparent;cursor:ew-resize}
input[type=range]::-webkit-slider-runnable-track{height:2px;background:var(--ink);opacity:.75}
input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:11px;height:11px;background:var(--paper);border:1.5px solid var(--ink);margin-top:-5px;transform:rotate(45deg);transition:background .15s}
input[type=range]:hover::-webkit-slider-thumb{background:var(--red)}
input[type=range]::-moz-range-track{height:2px;background:var(--ink)}
input[type=range]::-moz-range-thumb{width:10px;height:10px;border-radius:0;background:var(--paper);border:1.5px solid var(--ink)}

/* ---------- views ---------- */
#views{position:fixed;right:22px;bottom:22px;display:grid;grid-template-columns:1fr 1fr;gap:7px;width:308px}
.view{text-align:left;background:var(--paper);border:1px solid var(--ink);box-shadow:var(--shadow);cursor:pointer;padding:9px 11px;
  display:flex;gap:10px;align-items:center;transition:transform .18s cubic-bezier(.2,.85,.25,1),background .18s,color .18s}
.view:hover{transform:translate(-2px,-2px);background:var(--ink);color:var(--paper)}
.view .n{font-family:'Fraunces',serif;font-weight:900;font-size:22px;line-height:1;letter-spacing:-.03em}
.view .t{font-family:'IBM Plex Mono',monospace;font-size:9.5px;letter-spacing:.14em;text-transform:uppercase;line-height:1.35}
.view .t i{display:block;font-style:normal;opacity:.6;font-size:8.5px;letter-spacing:.1em}
.view.on{background:var(--sea);border-color:var(--sea);color:#f2e8d6}

/* ---------- readouts ---------- */
#meta{position:fixed;left:50%;transform:translateX(-50%);bottom:22px;display:flex;gap:0;align-items:stretch;z-index:10}
.meta-i{background:rgba(244,233,214,.94);border:1px solid var(--ink);padding:7px 12px;min-width:86px;box-shadow:3px 3px 0 rgba(6,18,24,.35)}
.meta-i + .meta-i{border-left:0}
.meta-i .k{font-family:'IBM Plex Mono',monospace;font-size:7.5px;letter-spacing:.2em;text-transform:uppercase;color:var(--ink2)}
.meta-i .v{font-family:'Fraunces',serif;font-weight:800;font-size:16px;letter-spacing:-.02em;line-height:1.15;font-variation-settings:'SOFT' 40,'WONK' 1}
.meta-i .v small{font-family:'IBM Plex Mono',monospace;font-size:9px;font-weight:500;letter-spacing:.06em;opacity:.65}
#rose{position:fixed;left:22px;top:auto;bottom:232px;width:86px;padding:9px 9px 6px;text-align:center}
#rose svg{width:100%;height:auto;display:block}
#rose .hd{font-family:'IBM Plex Mono',monospace;font-size:9px;letter-spacing:.14em;margin-top:2px;color:var(--sea)}
#rose text{font-family:'Fraunces',serif;font-weight:800;font-size:11px;fill:var(--ink)}
#rose .ring{fill:none;stroke:var(--ink);stroke-width:1.2;opacity:.85}
#rose .ring2{fill:none;stroke:var(--ink3);stroke-width:1}
#rose .needle{fill:var(--red)}
#rose .tail{fill:var(--sea)}
#scalebar{position:fixed;right:22px;bottom:118px;z-index:10;display:flex;align-items:center;gap:8px;
  font-family:'IBM Plex Mono',monospace;font-size:8.5px;letter-spacing:.16em;text-transform:uppercase;color:#e9dcc6;text-shadow:0 1px 3px rgba(0,0,0,.6)}
#scalebar i{display:block;width:88px;height:6px;border:1px solid #e9dcc6;
  background:repeating-linear-gradient(90deg,#e9dcc6 0 11px,transparent 11px 22px)}
#hint{position:fixed;left:50%;transform:translateX(-50%);bottom:74px;z-index:10;
  font-family:'IBM Plex Mono',monospace;font-size:9px;letter-spacing:.2em;text-transform:uppercase;color:#e6d9c2;
  text-shadow:0 1px 4px rgba(0,0,0,.7);opacity:1;transition:opacity 1.2s}
#hint.dim{opacity:.22}
#hint b{color:#f2c26a}

/* ---------- tooltip ---------- */
#tip{position:fixed;z-index:20;pointer-events:none;padding:7px 10px;background:var(--paper);border:1px solid var(--ink);
  box-shadow:3px 3px 0 rgba(6,18,24,.45);opacity:0;transform:translate(12px,12px) scale(.94);transition:opacity .14s,transform .18s cubic-bezier(.2,.9,.2,1);max-width:250px}
#tip.show{opacity:1;transform:translate(12px,12px) scale(1)}
#tip .n{font-family:'Fraunces',serif;font-weight:800;font-size:13.5px;letter-spacing:.01em;text-transform:uppercase}
#tip .d{font-size:11px;color:#31505e;line-height:1.35;margin-top:2px}
#tip .c{font-family:'IBM Plex Mono',monospace;font-size:8.5px;letter-spacing:.14em;color:var(--red);margin-top:4px}

/* ---------- loader ---------- */
#load{position:fixed;inset:0;z-index:60;background:#122029;display:grid;place-items:center;transition:opacity .8s .15s}
#load.gone{opacity:0;pointer-events:none}
#load .plate{width:min(560px,86vw);background:var(--paper);border:1px solid var(--ink);box-shadow:10px 10px 0 rgba(4,14,20,.5);padding:26px 30px 24px;position:relative}
#load .plate::after{content:"";position:absolute;inset:5px;border:1px solid var(--ink3)}
#load .kick{font-family:'IBM Plex Mono',monospace;font-size:9px;letter-spacing:.3em;text-transform:uppercase;color:var(--red)}
#load h2{font-family:'Fraunces',serif;font-weight:900;font-size:clamp(28px,5.6vw,48px);margin:.16em 0 .1em;line-height:.88;text-transform:uppercase;letter-spacing:-.02em}
#load .sub{font-size:12.5px;color:#31505e;margin-bottom:18px}
#load .bar{height:5px;background:var(--paper3);border:1px solid var(--ink)}
#load .bar i{display:block;height:100%;width:0;background:var(--red);transition:width .3s}
#load .st{display:flex;justify-content:space-between;font-family:'IBM Plex Mono',monospace;font-size:9px;letter-spacing:.15em;text-transform:uppercase;margin-top:8px;color:var(--ink2)}
#load .steps{font-family:'IBM Plex Mono',monospace;font-size:10px;margin-top:14px;columns:2;column-gap:22px;color:#31505e}
#load .steps div{break-inside:avoid;padding:1.5px 0;opacity:.35;transition:opacity .25s}
#load .steps div.on{opacity:1;color:var(--ink)}
#load .steps div::before{content:"○ ";color:var(--red)}
#load .steps div.on::before{content:"● "}
.hidden{display:none!important}
body.nohud #title,body.nohud #log,body.nohud #ctl,body.nohud #views,body.nohud #meta,
body.nohud #rose,body.nohud #scalebar,body.nohud #hint,body.nohud #chartgrid,body.nohud #vign{opacity:0;pointer-events:none;transition:opacity .35s}

@media (max-width:1080px){
  #log{width:250px;max-height:38vh}
  #title{width:min(64vw,480px)}
  #rose{display:none}
}
@media (max-width:780px){
  #log{display:none}
  #title{top:12px;left:12px;padding:11px 14px}
  #title p{display:none}
  #ctl{left:12px;right:12px;bottom:12px;width:auto}
  #views{display:none}
  #meta{bottom:auto;top:calc(100% - 302px);display:none}
  #scalebar{bottom:auto;top:12px;right:12px}
  #hint{display:none}
}
</style>
</head>
<body>

<canvas id="c"></canvas>
<div id="chartgrid"></div>
<div id="vign"></div>
<div id="cross"><div class="h"></div><div class="v"></div></div>

<header id="title" class="panel">
  <i class="mark tl"></i><i class="mark tr"></i><i class="mark bl"></i><i class="mark br"></i>
  <div class="kick">Plate VII · Anchorage &amp; Approaches</div>
  <h1>A Sailing Ship<span class="l2">calling at a <em>Harbor</em></span></h1>
  <div class="rule"><span>Greystone Haven</span><b></b><span>Soundings in voxels</span></div>
  <p>Three masts, eleven fathoms at the inner berth, and a tide that only serves the honest. <b>Drag to survey the anchorage</b> — hover any part of the plate to identify it.</p>
</header>

<aside id="log" class="panel">
  <i class="mark tr"></i><i class="mark br"></i>
  <div class="head"><h2>Ship's Log</h2><span id="clock">06:42</span></div>
  <ol id="loglist"></ol>
</aside>

<div id="rose" class="panel">
  <svg viewBox="-40 -40 80 80"><circle class="ring" r="34"/><circle class="ring2" r="27"/>
    <g id="roserot">
      <path class="needle" d="M0 -25 L5.5 -1 L0 5 L-5.5 -1Z"/>
      <path class="tail" d="M0 25 L5.5 1 L0 -5 L-5.5 1Z"/>
      <text x="0" y="-29" text-anchor="middle">N</text>
      <text x="31" y="4" text-anchor="middle" font-size="8">E</text>
      <text x="0" y="36" text-anchor="middle" font-size="8">S</text>
      <text x="-31" y="4" text-anchor="middle" font-size="8">W</text>
    </g>
  </svg>
  <div class="hd" id="heading">HDG 210°</div>
</div>

<section id="ctl" class="panel">
  <i class="mark bl"></i><i class="mark br"></i>
  <div class="lbl"><span>Working the plate</span><b></b></div>
  <div class="chips">
    <button class="chip" id="b-sails">Sails <span class="v">SET</span></button>
    <button class="chip" id="b-hour">Hour <span class="v">GOLDEN</span></button>
    <button class="chip" id="b-tide">Tide <span class="v">HIGH</span></button>
    <button class="chip" id="b-rig">Rigging <span class="v">ON</span></button>
    <button class="chip" id="b-weigh">Weigh anchor</button>
    <button class="chip" id="b-rot">Auto-survey <span class="v">ON</span></button>
    <button class="chip" id="b-hud">Hide HUD</button>
  </div>
  <div class="sliders">
    <div class="sl"><label>Sun elevation <span id="v-sun">12°</span></label><input type="range" id="s-sun" min="3" max="78" value="12"></div>
    <div class="sl"><label>Wind / swell <span id="v-wind">3</span></label><input type="range" id="s-wind" min="0" max="100" value="34"></div>
  </div>
</section>

<div id="views">
  <button class="view on" data-v="0"><span class="n">1</span><span class="t">Anchorage overview<i>full plate</i></span></button>
  <button class="view" data-v="1"><span class="n">2</span><span class="t">Quarterdeck<i>mainmast</i></span></button>
  <button class="view" data-v="2"><span class="n">3</span><span class="t">Quayside market<i>Greystone town</i></span></button>
  <button class="view" data-v="3"><span class="n">4</span><span class="t">The light<i>breakwater end</i></span></button>
</div>

<div id="meta">
  <div class="meta-i"><div class="k">Voxels</div><div class="v"><span id="m-vox">0</span></div></div>
  <div class="meta-i"><div class="k">Parts</div><div class="v"><span id="m-parts">0</span></div></div>
  <div class="meta-i"><div class="k">Fps</div><div class="v"><span id="m-fps">60</span></div></div>
  <div class="meta-i" style="min-width:170px"><div class="k">Cursor sounding</div><div class="v"><small id="m-pos">— —</small></div></div>
</div>

<div id="scalebar"><i></i><span>0 — 100 m</span></div>
<div id="hint"><b>Drag</b> orbit · <b>Wheel</b> zoom · <b>Shift-drag</b> pan · <b>Hover</b> identify · <b>Space</b> weigh anchor</div>
<div id="tip"><div class="n"></div><div class="d"></div><div class="c"></div></div>

<div id="load">
  <div class="plate">
    <div class="kick">Harbor survey · voxel chart</div>
    <h2>Greystone Haven</h2>
    <div class="sub">Drafting the plate: soundings, quay wall, breakwater light, and one barque of 1 400 tons now in the inner berth.</div>
    <div class="bar"><i id="pbar"></i></div>
    <div class="st"><span id="pstat">Sounding the channel…</span><span id="ppct">0%</span></div>
    <div class="steps" id="psteps"></div>
  </div>
</div>

<script type="importmap">
{ "imports": { "three": "https://unpkg.com/three@0.160.0/build/three.module.js" } }
</script>
<script type="module">
import * as THREE from 'three';
import { PMREMGenerator } from 'three';

/* ============================================================
   0 · helpers
   ============================================================ */
const clamp=(v,a,b)=>v<a?a:v>b?b:v;
const lerp=(a,b,t)=>a+(b-a)*t;
const ss=t=>{t=clamp(t,0,1);return t*t*(3-2*t)};
const s3=t=>t*t*(3-2*t);
function mulberry32(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
const rnd=mulberry32(0x9E9BCAF3);
const pick=a=>a[Math.floor(rnd()*a.length)];
function hash2(x,z){let h=(x*73856093)^(z*19349663);h=(h^(h>>>13))*1274126177;return((h^(h>>>16))>>>0)/4294967295}

/* ============================================================
   1 · renderer / scene
   ============================================================ */
const canvas=document.getElementById('c');
const renderer=new THREE.WebGLRenderer({canvas,antialias:true,powerPreference:'high-performance'});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.setSize(innerWidth,innerHeight);
renderer.shadowMap.enabled=true;
renderer.shadowMap.type=THREE.PCFSoftShadowMap;
renderer.outputColorSpace=THREE.SRGBColorSpace;
renderer.toneMapping=THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure=.98;
const scene=new THREE.Scene();
scene.fog=new THREE.FogExp2(new THREE.Color('#e9b487'),.0052);
const camera=new THREE.PerspectiveCamera(43,innerWidth/innerHeight,.6,620);
const pmrem=new PMREMGenerator(renderer);

const sun=new THREE.DirectionalLight(0xffd7a3,2.8);
sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);
sun.shadow.camera.near=1;sun.shadow.camera.far=320;
const SD=86;
sun.shadow.camera.left=-SD;sun.shadow.camera.right=SD;sun.shadow.camera.top=SD;sun.shadow.camera.bottom=-SD;
sun.shadow.bias=-.0009;sun.shadow.normalBias=.55;
scene.add(sun,sun.target);
const hemi=new THREE.HemisphereLight(0xa9cadb,0x6b5c46,.72);scene.add(hemi);
const lampLight=new THREE.PointLight(0xffb35c,0,90,2);lampLight.position.set(44,32,-8);scene.add(lampLight);

const skyTex=makeSky([[0,'#f8dcae'],[.06,'#f0b980'],[.16,'#cfa88f'],[.38,'#87aec7'],[.72,'#4d86b0'],[1,'#2f6695']]);
scene.background=skyTex;scene.environment=pmrem.fromEquirectangular(skyTex).texture;
const sunSprite=new THREE.Sprite(new THREE.SpriteMaterial({map:makeGlow('#fff6d8','#ffbd6a'),blending:THREE.AdditiveBlending,depthWrite:false,fog:false,transparent:true,opacity:.85}));
sunSprite.scale.set(120,120,1);scene.add(sunSprite);

/* ============================================================
   2 · voxel store
   ============================================================ */
const G={};
function grp(name,o={}){if(!G[name])G[name]={name,label:o.label||name,desc:o.desc||'',items:[],opts:o};return G[name]}
function put(g,x,y,z,c,h=1){g.items.push({x,y,z,c,h})}
function box(g,x0,x1,y0,y1,z0,z1,c){for(let x=Math.min(x0,x1);x<=Math.max(x0,x1);x++)for(let y=Math.min(y0,y1);y<=Math.max(y0,y1);y++)for(let z=Math.min(z0,z1);z<=Math.max(z0,z1);z++)put(g,x,y,z,c)}
function shell(g,x0,x1,y0,y1,z0,z1,c){
  for(let x=x0;x<=x1;x++)for(let y=y0;y<=y1;y++)for(let z=z0;z<=z1;z++){
    const e=(x===x0||x===x1||y===y0||y===y1||z===z0||z===z1);
    const inner=(x>x0+1&&x<x1-1&&z>z0+1&&z<z1-1&&y>y0+1&&y<y1-1);
    if(e&&!inner)put(g,x,y,z,c);
  }
}
function seg(g,x0,y0,z0,x1,y1,z1,c,step=.7,h=.4){
  const dx=x1-x0,dy=y1-y0,dz=z1-z0,L=Math.hypot(dx,dy,dz),n=Math.max(1,Math.ceil(L/step));
  for(let i=0;i<=n;i++){const t=i/n;put(g,x0+dx*t,y0+dy*t,z0+dz*t,c,h)}
}
function catenary(g,ax,ay,az,bx,by,bz,c,sag=1.4,step=.62,h=.32){
  const n=Math.ceil(Math.hypot(bx-ax,by-ay,bz-az)/step);
  for(let i=0;i<=n;i++){const t=i/n;put(g,lerp(ax,bx,t),lerp(ay,by,t)-sag*Math.sin(Math.PI*t),lerp(az,bz,t),c,h)}
}
function tree(g,x,y,z,s=1){
  const H=Math.round(3*s);
  for(let i=0;i<H;i++)put(g,x,y+i,z,'6b4a33');
  const r=Math.round(2*s),cy=y+H+1,c1=pick(['3f7a44','47864a','356b3c']),c2=pick(['548f4c','2e5c34']);
  for(let dx=-r;dx<=r;dx++)for(let dz=-r;dz<=r;dz++)for(let dy=-1;dy<=r-1;dy++){
    const d=Math.abs(dx)+Math.abs(dz)+Math.abs(dy);
    if(d>r+1)continue;
    if(d===r+1&&hash2(x+dx,z+dz)>.5)continue;
    put(g,x+dx,cy+dy,z+dz,(dx+dz+dy)%3===0?c2:c1);
  }
}

/* ============================================================
   3 · world math
   ============================================================ */
const seaOf=x=>Math.round(22+3.2*Math.sin(x*0.075)+1.4*Math.sin(x*0.19+1.1));
function isLand(x,z){return z>=seaOf(x)}
function hill(x,z,cx,cz,r){const d=Math.hypot(x-cx,(z-cz)*1.25)/r;return d>1?0:Math.pow(1-d,2)}
function landH(x,z){
  const d=z-seaOf(x);let h=2;
  if(d>3)h=3;if(d>12)h=4;if(d>22)h=5;if(d>32)h=6;
  h+=Math.round(3.4*hill(x,z,-40,56,20));
  h+=Math.round(6.2*hill(x,z,56,56,17));
  h+=Math.round(9*hill(x,z,44,34,13));
  h+=Math.round(7*hill(x,z,-62,42,16));
  return Math.max(2,h);
}
const SAIL={x:-18,z:-4};

/* ============================================================
   4 · the sea & seabed
   ============================================================ */
function buildSea(){
  const sea=grp('TIDE',{dyn:true,label:'The Tide',desc:'Spring range 3.1 m · flood runs east-northeast',noShadow:true});
  const bed=grp('SEABED',{label:'Seabed',desc:'Sand and shell, nine to fourteen fathoms'});
  for(let x=-63;x<=63;x+=1.4)for(let z=-63;z<=63;z+=1.4){
    if(isLand(x,z))continue;
    const d=clamp((seaOf(x)-z+8)/52,0,1);
    put(sea,x,-6,z,d<.5?0x2f7d8c:0x1a4a63,0);
    const dep=seaOf(x)-z;
    put(bed,x,-5.2,z,dep<7?0x8d9078:(dep<16?0x5f7a74:0x33505c));
  }
}

/* ============================================================
   5 · land, quay, town, breakwater
   ============================================================ */
let chimneys=[],lamps=[],windowsLit=[];
function buildLand(){
  const L=grp('QUAY & COBBLES',{label:'Quay & Cobbles',desc:'The long stone berth of Greystone, built 1793'});
  const heights={};
  for(let x=-64;x<=64;x++)for(let z=seaOf(x);z<=64;z++)heights[x+','+z]=landH(x,z);
  const H=(x,z)=>heights[x+','+z]!==undefined?heights[x+','+z]:(z<seaOf(x)?1:landH(x,z));
  for(let x=-64;x<=64;x++)for(let z=seaOf(x);z<=64;z++){
    const h=H(x,z);const d=z-seaOf(x);
    let top;
    if(d<4)top=pick(['a39a88','9b9280','aca290','8f8a7e']);
    else if(d<14)top=pick(['b6ab95','a89d86','c0b59c']);
    else top=pick(['6f8f4e','78964f','63854a']);
    put(L,x,h,z,top);
    const nb=Math.min(H(x-1,z),H(x+1,z),H(x,z-1),H(x,z+1));
    for(let y=h-1;y>=Math.max(2,nb);y--){
      put(L,x,y,z,y>=2&&d<4?pick(['7d766a','8a8375','6d6a63']):pick(['8a7f68','7a6f5a','96896f']));
    }
  }
  // quay edge detail: wall caps, bollards, steps, capstan
  for(let x=-64;x<=64;x++){const s=seaOf(x);
    put(L,x,3,s,pick(['9a9184','8b8376']));
    if(((x+11)%9+9)%9===0){for(let y=4;y<=5;y++)put(L,x,y,s+1,y===5?'3b3a36':'6d6a63')}
    if(((x+5)%17+17)%17===0){for(let y=1;y<=2;y++)put(L,x,y,s-2,'8a8375')}
  }
  // lamps along the quay
  for(let x=-52;x<=52;x+=11){const s=seaOf(x)+3;const h=landH(x,s);
    for(let y=h+1;y<=h+6;y++)put(L,x,y,s,'2f2c28');
    put(L,x,h+7,s,'ffd06a');put(L,x-1,h+7,s,'4a443c');put(L,x+1,h+7,s,'4a443c');
    put(L,x,h+8,s,'4a443c');
    lamps.push([x,h+7,s]);
  }
  // fish-market bonfire
  const bx=-40,bs=seaOf(bx)+1;
  box(L,bx-2,landH(bx,bs)+1,bx+2,bs+2,bs+2,'5f4630');
  for(let i=0;i<7;i++)put(L,bx-2+Math.floor(rnd()*5),landH(bx,bs)+2+Math.floor(rnd()*2),bs,bx-2+Math.floor(rnd()*5),bs,'6b4a2f');
  chimneys.push([bx,landH(bx,bs)+4,bs+1,.9]);
}

function building(g,x0,z0,w,d){
  const h0=landH(x0+1,z0+1);
  const h=5+Math.floor(rnd()*6);
  const wall=pick(['f0e6d3','e4d6bc','d9c9a9','efe3ce']);
  const roof=pick(['4a5560','b05743','36736c','584b46']);
  box(g,x0,h0,x0+w-1,h0+h-1,z0+d-1,wall);
  // quoins & string course
  for(let y=h0;y<h0+h;y+=3)for(let x=x0;x<x0+w;x++)put(g,x,y,z0,'d8cbb2');
  // windows (lit glass + frames)
  for(let y=h0+2;y<h0+h-1;y+=3){
    const inset=(y-h0)%4===3;
    for(let x=x0+(inset?1:0);x<x0+w;x+=(inset?4:3)){
      for(const z of [z0,z0+d-1]){put(g,x,y,z,'2f6e78');put(g,x,y+1,z,'f7f1e3');put(g,x-1,y,z,'cfc3ab');put(g,x+1,y,z,'cfc3ab');windowsLit.push([x,y,z])}
    }
    for(let z=z0+1;z<z0+d-1;z+=3){for(const x of [x0,x0+w-1]){put(g,x,y,z,'2f6e78');windowsLit.push([x,y,z])}}
  }
  // door
  for(let y=h0;y<=h0+2;y++)put(g,x0+2,y,z0,'5b3d2a');
  put(g,x0+2,h0+3,z0,'d8cbb2');
  // gabled roof (ridge along x)
  for(let x=x0-1;x<=x0+w;x++){
    put(g,x,h0+h,z0-1,roof);put(g,x,h0+h,z0+d,roof);
    for(let i=0;i<=Math.ceil(d/2);i++){
      const y=h0+h+i;const z1=z0+i,z2=z0+d-1-i;
      if(z1>z2)break;
      put(g,x,y,z1,roof);put(g,x,y,z2,roof);
      if(i<Math.ceil(d/2)-1)box(g,x,y,z1+1,x,y,z2-1,'e9dfcb');
    }
  }
  for(let y=h0+h;y<h0+h+Math.ceil(d/2);y++){put(g,x0,y,z0+Math.ceil(d/2),'cfc3ab');put(g,x0+w-1,y,z0+Math.ceil(d/2),'cfc3ab')}
  // chimney
  if(rnd()<.75){const cx=x0+1+Math.floor(rnd()*(w-2)),cz=z0+d-2;
    for(let y=h0+h+1;y<=h0+h+4;y++)put(g,cx,y,cz,'a2604c');
    chimneys.push([cx,h0+h+5,cz,.55]);}
  // shop awning at ground
  if(rnd()<.5){const c1=pick(['c1483a','2f5d4a','2a5b7a']),c2='f1e7d5';
    for(let x=x0;x<x0+w;x++)for(let z=z0-3;z<z0;z++)put(g,x,h0+3,z,(x+z)%2?c1:c2);
  }
}

function buildTown(){
  const T=grp('GREYSTONE TOWN',{label:'Greystone Town',desc:'Fourteen dwellings, a custom house, and a fish market'});
  // warehouse row
  const rows=[[64,12,7,32],[50,14,6,42],[38,14,6,52],[26,15,6,62]];
  rows.forEach(([z0,w,d,n])=>{for(let x=-40;x<48;x+=w+n)building(T,clamp(x,-56,54),z0,Math.min(w,62-clamp(x,-56,54)),d)});
  // custom house + clock tower
  customHouse(T,-24,seaOf(-10)+4);
  // market stalls on the quay
  for(let i=0;i<4;i++){
    const x=14+i*8,z=seaOf(x)+2,h=landH(x,z);
    for(const sx of[0,5])for(const sz of[0,3])for(let y=h+1;y<=h+4;y++)put(T,x+sx,y,z+sz,'6b4a2f');
    const c1='c1483a',c2='f1e7d5';
    for(let sx=-1;sx<=6;sx++)for(let sz=-1;sz<=4;sz++)put(T,x+sx,h+5+Math.round(sz/3),z+sz,(sx+sz)%2?c1:c2);
    for(let sx=0;sx<=5;sx++)put(T,x+sx,h+4,z-1,(sx%2)?c2:c1);
    box(T,x+1,h+1,z+1,x+3,h+2,z+2,'b98a52');
    for(let k=0;k<3;k++)put(T,x+4,h+1,k%2?'e6e0d0':'c8402f',z+k);
  }
  // warehouses crates & barrels on the quay
  for(let i=0;i<26;i++){
    const x=Math.round(-56+rnd()*110),z=seaOf(x)+2+Math.floor(rnd()*4),h=landH(x,z);
    if(rnd()<.55){const w=1+Math.floor(rnd()*2);box(T,x,h,z,x+w,h+1+Math.floor(rnd()*2),z+w,'b98a52');}
    else{for(let y=h;y<=h+1;y++)put(T,x,y,z,'9c6b3f');put(T,x,h+2,z,'7c5227')}
  }
  // trees, garden squares
  for(let i=0;i<22;i++){
    const x=Math.round(-58+rnd()*116),z=Math.round(34+rnd()*26);
    if(hill(x,z,56,56,17)>1.2)continue;
    tree(T,x,landH(x,z),z,rnd()<.4?1.4:1);
  }
  // windmill on the west heights
  const wx=-46,wz=54,wh=landH(wx,wz);
  for(let y=wh;y<=wh+9;y++){const r=Math.max(1,Math.round(3-(y-wh)/4));box(T,wx-r,y,wz-r,wx+r,y,wz+r,'d8cbb2')}
  box(T,wx-2,wh+10,wz-2,wx+2,wh+11,wz+2,'584b46');
  // east point beacon
  const px=58,pz=52,ph=landH(px,pz);
  for(let y=ph;y<=ph+5;y++)put(T,px,y,pz,'8f8a7e');
  put(T,px,ph+6,pz,'ffb347');lamps.push([px,ph+6,pz]);
  // fort on the east hill
  const fx=60,fz=58,fh=landH(fx,fz);
  shell(T,fx-6,fx+6,fh,fh+3,fz-5,fz+5,'9a9184');
  for(let x=fx-6;x<=fx+6;x+=2)for(let z=fz-5;z<=fz+5;z+=3)put(T,x,fh+4,z,'7d766a');
  for(let y=fh+4;y<=fh+9;y++)put(T,fx,y,fz,'6b4a2f');
  for(let z=0;z<4;z++)put(T,fx,fh+10,fz+z,z===0?'c8402f':'f1e7d5');
}

function customHouse(g,x0,z0){
  const h0=landH(x0+2,z0+2),H=9;
  box(g,x0,h0,z0,x0+27,h0+H-1,z0+9,'eadfc9');
  for(let x=x0+1;x<=x0+26;x+=4)for(let y=h0;y<h0+H-1;y++)put(g,x,y,z0,'f6eedd');
  for(let y=h0+1;y<h0+H-1;y+=3)for(let x=x0+2;x<x0+27;x+=3){put(g,x,y,z0,'2f6e78');windowsLit.push([x,y,z0])}
  for(let y=h0;y<=h0+2;y++)put(g,x0+13,y,z0,'5b3d2a');
  box(g,x0-1,h0+H,z0-1,x0+28,h0+H+1,z0+10,'f2ead8');
  box(g,x0+9,h0+H+2,z0+2,x0+18,h0+H+4,z0+7,'eadfc9');
  // tower
  box(g,x0+12,h0+H+5,z0+3,x0+15,h0+H+10,z0+6,'f2ead8');
  for(let y=h0+H+6;y<=h0+H+8;y++)put(g,x0+11,y,z0+3,'f7f1e3');  // clock face west
  for(let x=x0+12;x<=x0+15;x++)for(let y=h0+H+6;y<=h0+H+8;y++)put(g,x,y,z0+2,'f7f1e3'); // clock face south
  for(let y=h0+H+11;y<=h0+H+12;y++)box(g,x0+11,y,z0+2,x0+16,y,z0+7,'2f5d52');
  box(g,x0+12,h0+H+13,z0+3,x0+15,h0+H+15,z0+6,'b05743');
  put(g,x0+13,h0+H+16,z0+4,'e0a23c');
  clockFace=[x0+13.5,h0+H+7,z0+1.9];
  chimneys.push([x0+2,h0+H+2,z0+8,.7]);
  chimneys.push([x0+25,h0+H+2,z0+8,.7]);
}
let clockFace=null;

function buildBreakwater(){
  const B=grp('BREAKWATER & LIGHT',{label:'Breakwater & Light',desc:'Fixed white, 42 m · 3rd-order light, lit at dusk'});
  for(let x=36;x<=56;x++)for(let z=-22;z<=24;z++){
    const d=Math.hypot(x-46,z-2)*0.09;
    if(d>1.05)continue;
    const top=Math.max(2,Math.round(5-d*3.6)+Math.round(1.5*Math.sin(x*0.7)*Math.cos(z*0.6)));
    for(let y=-5;y<=top;y++)put(B,x,y,z,y>=top?'8f8a7e':pick(['6d6a63','7d766a','8a8375']));
  }
  // keeper's cottage
  const cx=50,cz=14,ch=4;
  box(B,cx,ch,cz,cx+6,ch+3,cz+4,'efe3ce');
  for(let x=cx-1;x<=cx+7;x++){put(B,x,ch+4,cz,'b05743');put(B,x,ch+4,cz+4,'b05743');for(let z=cz;z<=cz+4;z++)put(B,x,ch+4+Math.round(Math.abs(x-cx-3)/2),z,'b05743')}
  put(B,cx+3,ch+1,cz,'5b3d2a');put(B,cx+1,ch+2,cz,'2f6e78');put(B,cx+5,ch+2,cz,'2f6e78');
  for(let y=ch+5;y<=ch+7;y++)put(B,cx+6,y,cz+1,'a2604c');
  chimneys.push([cx+6,ch+8,cz+1,.5]);
  // tower
  const tx=44,tz=-8;
  for(let y=5;y<=23;y++){
    const r=y<8?4:(y<20?3:3.4);
    const band=Math.floor((y-5)/4)%2;
    for(let dx=-4;dx<=4;dx++)for(let dz=-4;dz<=4;dz++){
      const dd=Math.hypot(dx,dz);
      if(dd>r+0.35||dd<r-0.9)continue;
      put(B,tx+dx,y,tz+dz,band?'c0392b':'f4efe4');
    }
  }
  for(let dx=-4;dx<=4;dx++)for(let dz=-4;dz<=4;dz++)if(Math.hypot(dx,dz)<4.2)put(B,tx+dx,24,tz+dz,'2f2c28');
  for(let dx=-3;dx<=3;dx++)for(let dz=-3;dz<=3;dz++)if(Math.hypot(dx,dz)<3.2)put(B,tx+dx,25,tz+dz,'ffd06a');
  for(let dx=-3;dx<=3;dx++)for(let dz=-3;dz<=3;dz++)if(Math.hypot(dx,dz)<3.2)put(B,tx+dx,26,tz+dz,'2f2c28');
  box(B,tx-2,27,tz-2,tx+2,29,tz+2,'c0392b');
  put(B,tx,30,tz,'e0a23c');
  lamps.push([tx,25,tz]);
  beamPos=[tx,25.5,tz];
  // derrick crane
  const dx0=38,dz0=6,dh=landH(dx0,dz0)||4;
  for(let y=4;y<=10;y++)put(B,dx0,y,dz0,'6b4a2f');
  seg(B,dx0,10,dz0,dx0+7,9,dz0-3,'6b4a2f',.7,.8);
  seg(B,dx0+7,9,dz0-3,dx0+7,6,dz0-3,'6b5a44',.6,.2);
  box(B,dx0+6,5,dz0-4,dx0+8,6,dz0-2,'b98a52');
}
let beamPos=null;

function buildPier(){
  const P=grp('PIER & GANtry',{label:'The Long Pier',desc:'Timber berth, piles of oak, ten fathoms at the head'});
  for(let x=-26;x<=-14;x++)for(let z=2;z<=24;z++)
    put(P,x,3,z,(x+z)%2?'8c6b4a':pick(['8c6b4a','96744f','7f6040']));
  for(let x=-26;x<=-14;x+=4)for(let z=2;z<=24;z+=4){
    for(let y=-5;y<=3;y++){put(P,x,y,z,'5f4630');put(P,x+1,y,z,'54402c')}
    if(z<24)seg(P,x,1,z,x+1,2,z+4,'5f4630',.9,.5);
  }
  for(let z=4;z<=20;z+=8)for(let y=1;y<=3;y++)put(P,-13.5,y,z,'3b3a36'); // fenders
  for(const z of[6,14,20])for(let y=4;y<=5;y++)put(P,-15,y,z,y===5?'3b3a36':'6d6a63');
  // chandlery shed
  for(let x=-26;x<=-18;x++)for(let z=19;z<=24;z++){
    for(let y=4;y<=7;y++)put(P,x,y,z,(x+z)%3?'c9b895':'b8a684');
  }
  for(let x=-27;x<=-17;x++)for(let z=18;z<=25;z++)put(P,x,8+Math.round(Math.abs(x+22)/4),z,'4a5560');
  for(let y=4;y<=6;y++)put(P,-22,y,19,'5b3d2a');
  for(let x=-24;x<=-20;x++)for(let y=5;y<=6;y++)put(P,x,y,18,'f2ead8');
  put(P,-22,7,18,'ffd06a');lamps.push([-22,7,18]);
  // capstan
  for(let dx=-2;dx<=2;dx++)for(let dz=-2;dz<=2;dz++)if(Math.hypot(dx,dz)<2.4)put(P,-20+dx,4,-4+dz+18,'6b4a2f');
  put(P,-20,5,16,'8c6b4a');
  // cargo
  for(let i=0;i<12;i++){
    const x=-25+Math.floor(rnd()*10),z=4+Math.floor(rnd()*13);
    if(rnd()<.5)box(P,x,4,z,x+1,5+Math.floor(rnd()*2),z+1,'b98a52');
    else for(let y=4;y<=5;y++)put(P,x,y,z,'9c6b3f');
  }
  // gangway to the ship (moves with her)
  const GW=grp('GANGWAY',{parent:'ship',label:'Gangway',desc:'Ship’s side made fast — she is shipped, and her men are free'});
  for(let i=0;i<=10;i++){
    const t=i/10,x=lerp(-6.4,-14.6,t),y=lerp(4.6,4,t),z=lerp(-4,14,t);
    for(let w=-1;w<=1;w++)put(GW,Math.round(x),Math.round(y),Math.round(z+w),'8c6b4a');
    put(GW,Math.round(x),Math.round(y+2),Math.round(z),'6b4a2f');
  }
}

/* ============================================================
   6 · the ship
   ============================================================ */
const MASTS=[{z:-12,h:22.5,n:'fore'},{z:-1,h:25,n:'main'},{z:9,h:19,n:'mizzen'}];
const YARDS=[
  {z:-12,y:9.2,w:9.4,h:3.8},{z:-12,y:14,w:7.8,h:3.2},{z:-12,y:18,w:5.4,h:2.4},
  {z:-1,y:8.4,w:10.6,h:4.4},{z:-1,y:14.2,w:8.8,h:3.8},{z:-1,y:19,w:6.4,h:2.6},
  {z:9,y:10,w:7.2,h:3.4},{z:9,y:14.4,w:5.4,h:2.6}
];
const beamT=t=>1.1+4.6*Math.pow(Math.sin(Math.PI*(0.045+0.905*t)),0.78);
const keelT=t=>-4.7+3.0*Math.pow(1-t,2.1)+1.3*Math.pow(t,2.7);
const deckT=t=>3.4+1.42*Math.pow(2*t-1,2);

function buildShip(){
  const hull=grp('HULL',{parent:'ship',label:'Hull',desc:'Oak-frigate built, copper sheathed · 40 m keel · 1 400 tons'});
  const deck=grp('DECKS & BULWARKS',{parent:'ship',label:'Decks & Bulwarks',desc:'Yellow ochre wale, gunports in three tiers'});
  const spars=grp('MASTS & YARDS',{parent:'ship',label:'Masts & Yards',desc:'Pine lower masts, spruce topmasts, hooped and served'});
  const cargo=grp('CREW & CARGO',{parent:'ship',label:'Deck Cargo',desc:'Casks of beef, iron pig, and coiled lines'});
  for(let z=-22;z<=18;z++){
    const t=(z+22)/40,W=Math.round(beamT(t)),keel=Math.ceil(keelT(t)),dk=Math.round(deckT(t));
    for(let x=-W;x<=W;x++){
      const edge=Math.abs(x)>=W;
      const y1=dk;
      if(edge){
        for(let y=keel;y<=y1+2;y++)put(hull,x,y,z,hullCol(y,z,x));
        put(deck,x,y1+1,z,'2f2c28');put(deck,x,y1+2,z,'b98a52');
      }else{
        for(let y=keel;y<=keel+1;y++)put(hull,x,y,z,hullCol(y,z,x));
        put(deck,x,y1,z,((x+z)%2)?'b98a52':'a87f4c');
      }
    }
    if(Math.abs(z+15)%3===0&&z<12&&z>-19){put(hull,W,2,z,'f2e3c4');put(hull,-W,2,z,'f2e3c4')}
  }
  // sterncastle & cabin
  for(let z=6;z<=17;z++){
    const t=(z+22)/40,W=Math.round(beamT(t)),dk=Math.round(deckT(t))+2;
    for(let x=-W+1;x<=W-1;x++)put(deck,x,dk,z,((x+z)%2)?'b98a52':'a87f4c');
    for(const x of[-W+1,W-1])for(let y=dk+1;y<=dk+3;y++)put(deck,x,y,z,'f1e5cc');
    for(let y=dk+1;y<=dk+3;y++)put(deck,0,y,z,'f1e5cc');
    for(let x=-W+2;x<=W-2;x++){put(deck,x,dk+1,z,'f1e5cc');put(deck,x,dk+3,z,'2f5d52')}
    put(deck,0,dk+2,17,'ffd06a');
  }
  // forecastle
  for(let z=-20;z<=-14;z++){
    const t=(z+22)/40,W=Math.round(beamT(t)),dk=Math.round(deckT(t))+1;
    for(let x=-W+1;x<=W-1;x++)put(deck,x,dk,z,'c1913f');
    for(const x of[-W+1,W-1])for(let y=dk+1;y<=dk+2;y++)put(deck,x,y,z,'f1e5cc');
  }
  // figurehead, bow courses, bowsprit
  for(let z=-23;z<=-21;z++)for(let y=-3;y<=1;y++)put(hull,0,y,z,'d8cbb2');
  seg(spars,0,deckT(0)+1.4,-21,0,deckT(0)+5,-32,'7a5634',.75,1.15);
  seg(spars,0,deckT(0)+5,-32,0,deckT(0)+6.6,-37,'7a5634',.7,.7);
  // masts, tops, yards
  for(const m of MASTS){
    const dk=Math.round(deckT((m.z+22)/40));
    for(let y=dk-2;y<=m.h;y++)put(spars,0,y,m.z,y<dk+1?'5f4630':(y%2?'7a5634':'6f4e30'));
    for(let dx=-2;dx<=2;dx++)for(let dz=-2;dz<=2;dz++)if(Math.abs(dx)+Math.abs(dz)<=2.2&&Math.abs(dx)+Math.abs(dz)>1)put(spars,dx,m.h-9.5,m.z+dz,'6b4a2f');
  }
  for(const yd of YARDS){
    seg(spars,-yd.w,yd.y,yd.z,yd.w,yd.y,yd.z,'6b4a2f',.6,.65);
    seg(spars,-1,yd.y-.8,yd.z,1,yd.y-.8,yd.z,'6b4a2f',.5,.5);
  }
  // gaff & boom
  seg(spars,0,15,9,0,17.6,13.4,'6b4a2f',.6,.55);
  seg(spars,0,9.2,9,0,9.2,15.2,'6b4a2f',.6,.55);
  // deck furniture
  for(const gz of[-8,-4,0,4])for(const sx of[-1,1]){
    for(let y=3;y<=4;y++)put(cargo,sx*5,y,gz,'3b3a36');
    put(cargo,sx*6,3,gz,'2f2c28');
  }
  for(const [bx,bz] of [[-3,-11],[2,-13],[3,3],[-2,4],[1,-6]]){
    for(let y=4;y<=6;y++)put(cargo,bx,y,bz,y===5?'9c6b3f':'7c5227');
    put(cargo,bx,7,bz,'d8cbb2');
  }
  box(cargo,-4,4,-19,-2,5,-17,'b98a52');box(cargo,2,4,-19,4,6,-17,'b98a52');
  for(let i=0;i<8;i++){const a=i/8*Math.PI*2;put(cargo,Math.round(Math.cos(a)*1.6),4,Math.round(-2+Math.sin(a)*1.6),'c8b48c',.5)}
  // ship's boat
  for(let z=-2;z<=4;z++)for(let x=0;x<2;x++){put(cargo,7.5+x,0.6,z,'8c6b4a');put(cargo,-7.5-x,0.6,z,'8c6b4a')}
  // stern lanterns
  put(cargo,0,9,17.4,'ffd06a');
  // crew on deck
  for(const [cx,cz] of [[-3,-16],[3,-9],[-1,2],[2,-2]])figure(cargo,cx,5,cz,'c8402f');
  buildSails();
  buildRig();
}
function hullCol(y,z,x){
  if(y<=-3)return pick(['8a4230','7d3b2b','93503c']);
  if(y<=0)return '241f1c';
  if(y<=2)return pick(['d8bd6e','cbb15f']);
  if(y===3)return 'f2e3c4';
  return '241f1c';
}
function figure(g,x,y,z,coat){
  put(g,x,y,z,'243a52');put(g,x,y+1,z,'243a52');
  put(g,x,y+2,z,coat);put(g,x,y+3,z,'e6cfa8');put(g,x,y+4,z,'241f1c');
}
function buildSails(){
  const set=grp('SQUARE SAILS',{parent:'ship',label:'Square Sails',desc:'Nine canvas set — courses, topsails, topgallants'});
  const fur=grp("FURL'D SAILS",{parent:'ship',visible:false,label:"Furl'd Canvas",desc:'Canvas bayed up to the yard — she rides easy'});
  const fa=grp('FORE-AND-AFT',{parent:'ship',label:'Spanker & Jibs',desc:'Spanker on the gaff, two jibs on the bowline'});
  for(const yd of YARDS){
    for(let x=-yd.w;x<=yd.w;x+=.85){
      const bulge=Math.pow(Math.cos(x/yd.w*1.45),2);
      const zc=yd.z+0.9*bulge;
      for(let k=0;k<yd.h;k+=.85){
        const y=yd.y-.5-k;
        const band=Math.abs(y-(yd.y-yd.h*0.42))<.5;
        put(set,x,y,zc,band?'d9603f':(k<1.2?'f7f0dd':'efe6cf'),.9);
        put(set,x,y,zc-1,k<1.2?'f7f0dd':'ddd0b4',.9);
      }
    }
    seg(fur,-yd.w,yd.y-.6,yd.z,yd.w,yd.y-.6,yd.z,'e8dcc0',.5,.8);
  }
  // spanker
  for(let u=0;u<=1;u+=.06){
    for(let v=0;v<=1;v+=.07){
      const y=lerp(9.6,15.2,u), z=lerp(9.2,14.4,v);
      const yEnd=lerp(y,17.2,v*.85);
      put(fa,0,yEnd,z,'efe6cf',.9);
    }
  }
  // jibs
  const jibs=[[[-32,deckT(0)+5,-0.1],[-12,15.5],[-12,8.6]],[[-37,deckT(0)+6.6,0],[-12,19.5],[-12,14]]];
  for(const[[ax,ay],b,c] of jibs){
    for(let u=0;u<=1;u+=.05){
      const p1=[lerp(ax,b[0],u),lerp(ay,b[1],u)],p2=[lerp(ax,c[0],u),lerp(ay,c[1],u)];
      const n=4;
      for(let i=0;i<=n;i++){const t=i/n;put(fa,0,lerp(p1[1],p2[1],t),lerp(p1[0],p2[0],t),'efe6cf',.7)}
    }
  }
  // staysails
  for(let u=0;u<=1;u+=.07){
    const y=lerp(10,18,u),z=lerp(-11.4,-1.6,u);
    for(let v=0;v<=1;v+=.12)put(fa,0,lerp(y-2.2,y+1.4,v),z,'e8dcc0',.8);
  }
}
function buildRig(){
  const R=grp('RIGGING',{parent:'ship',label:'Rigging',desc:'Shrouds, stays, ratlines and braces — every line a voxel'});
  const topY={fore:22,main:24.5,mizzen:18.5};
  for(const m of MASTS){
    const dk=Math.round(deckT((m.z+22)/40)),W=Math.round(beamT((m.z+22)/40));
    for(let i=0;i<5;i++){
      const zz=m.z-3+i*1.5;
      for(const s of[-1,1]){
        const bx=s*W,by=dk+2;
        seg(R,bx,by,zz,s*1,Math.min(topY[m.n],m.h-3),m.z,'6b5a44',.78,.2);
        // ratlines
        const n=Math.ceil(Math.hypot(bx,by)/1.1);
        for(let k=0;k<n;k++){
          const t=(k+1)/(n+1),rx=lerp(bx,s,t),ry=lerp(by,Math.min(topY[m.n],m.h-3),t);
          if(ry>dk+3&&ry<topY[m.n]-1)seg(R,rx,ry,zz-.6,rx,ry,zz+.6,'7a6a50',.5,.14);
        }
      }
    }
  }
  // stays
  seg(R,0,deckT(0)+5,-32,0,24.5,-1,'6b5a44',.85,.24);
  seg(R,0,deckT(0)+5,-32,0,22,-12,'6b5a44',.85,.2);
  seg(R,0,deckT(0)+6.6,-37,0,22,-12,'6b5a44',.9,.16);
  for(const m of MASTS){seg(R,0,topY[m.n],m.z,0,13,17.6,'6b5a44',1,.2)}
  // lifts and braces
  for(const yd of YARDS){for(const s of[-1,1]){
    seg(R,s*yd.w,yd.y,yd.z,0,yd.y+3.2,yd.z+(yd.z<0?3:-3),'7a6a50',1,.14);
    seg(R,s*yd.w,yd.y,yd.z,s*7,Math.round(deckT((yd.z+22)/40))+2,yd.z,'7a6a50',1,.14);
  }}
  // moorings (part of her, made fast at the berth)
  catenary(R,-6.4,5,14,-15+4,5,6,1.1,'6b5a44');
  catenary(R,-6.4,5,-2,-15+4,5,-14+12,1.3,'6b5a44');
  catenary(R,6.4,5,8,12,5,18,1.2,'6b5a44');
  // ensign at the peak, union at the mizzen
  ensign=grp('ENSIGN',{parent:'ship',dyn:true,basic:true,transparent:true,opacity:.97,label:'Ensign',desc:'She pays the flag dues — the harbor master has boarded'});
  const ens=grp('ENSIGN-STATIC',{parent:'ship',label:'Ensign Staff',desc:'Signal halyate'});
  seg(ens,0,24.5,-1,0,26.5,-1,'6b5a44',.6,.2);
}
let ensign=null;

/* ============================================================
   7 · air, light, life
   ============================================================ */
let gulls=[],smoke=[],clouds=[],crew=[],beam=null,wake=null,wheels=null,hands=null,glow=null,foam=null,sailboat=null,windmill=null;
function buildLife(){
  // ensign cloth (dynamic)
  const e=[];for(let ix=0;ix<8;ix++)for(let iy=0;iy<5;iy++)e.push([ix,iy]);
  ensign.data=e;
  // gulls
  const GB=grp('GULLS',{dyn:true,label:'Gulls',desc:'Black-backed, loud, and entirely unimpressed'});
  for(let i=0;i<9;i++)gulls.push({c:[-20+rnd()*70,-20+rnd()*40],r:16+rnd()*26,alt:14+rnd()*11,ph:rnd()*6.28,sp:.18+rnd()*.22,grp:GB});
  GB.data=gulls;
  // chimney smoke + beach fire
  const SM=grp('SMOKE',{dyn:true,basic:true,transparent:true,opacity:.42,depthWrite:false,label:'Chimney Smoke',desc:'Peat and coal fires, drifting east with the tide'});
  for(const c of chimneys)for(let i=0;i<9;i++)smoke.push({x:c[0],y:c[1],z:c[2],t:rnd(),s:c[3],grp:SM});
  SM.data=smoke;
  // clouds
  const CL=grp('CLOUDS',{dyn:true,basic:true,transparent:true,opacity:.62,depthWrite:false,fog:false,label:'Cloud Bank',desc:'High cirrus over the point — weather holding'});
  for(let i=0;i<22;i++){
    const cx=-70+rnd()*150,cz=-70+rnd()*140,cy=30+rnd()*10,r=3+Math.floor(rnd()*4),puffs=[];
    for(let k=0;k<10;k++)puffs.push([Math.round((rnd()*2-1)*r),Math.round((rnd()*2-1)*r*.5),Math.round((rnd()*2-1)*r)]);
    clouds.push({x:cx,y:cy,z:cz,puffs,sp:1.2+rnd()*1.6,grp:CL});
  }
  CL.data=clouds;
  // lanterns & lit windows
  const GL=grp('LANTERN GLOW',{dyn:true,basic:true,transparent:true,opacity:.9,depthWrite:false,fog:false,label:'Lamp & Window Light',desc:'Whale oil and gas — the town begins to kindle at dusk'});
  const gl=[];for(const l of lamps)gl.push([l[0],l[1],l[2],1.15]);
  for(const w of windowsLit.slice(0,120))gl.push([w[0],w[1],w[2],.62]);
  GL.data=gl;
  // lighthouse beam
  beam=grp('LIGHTHOUSE BEAM',{dyn:true,basic:true,transparent:true,opacity:.1,depthWrite:false,blending:THREE.AdditiveBlending,fog:false,label:'The Light',desc:'Fixed white, 42 m above high water'});
  const bl=[];for(let i=0;i<34;i++)bl.push(i);beam.data=bl;
  // foam
  foam=grp('FOAM',{dyn:true,basic:true,transparent:true,opacity:.85,depthWrite:false,label:'Surf & Foam',desc:'The ebb makes a white line along the quay'});
  const fl=[];for(let x=-60;x<=60;x+=2)fl.push([x,seaOf(x)-1]);
  for(let z=2;z<=24;z+=3)fl.push([-13.4,z]);
  for(let i=0;i<26;i++)fl.push([34+i*.4,-20+i*1.4]);
  foam.data=fl;
  // wake
  wake=grp('WAKE',{dyn:true,basic:true,transparent:true,opacity:.7,depthWrite:false,label:'Wake',desc:'She leaves a white seam in the harbor'});
  const wl=[];for(let i=0;i<70;i++)wl.push(i);wake.data=wl;
  // tide-hand & clock hands
  hands=grp('CLOCK & TIDE',{dyn:true,basic:true,label:'Clock Tower',desc:'The harbor clock keeps the tidewaiters’ hours'});
  hands.data=[0,1,2];
  // windmill blades
  wheels=grp('WINDMILL BLADES',{dyn:true,label:'Mill Blades',desc:'The west-heights mill, turning with the off-shore air'});
  wheels.data=[0,1,2,3];
  // pier crew (walking)
  const CR=grp('PIR CREW',{dyn:true,label:'Quayside Folk',desc:'Coopers, porters and a tide-waiter with his book'});
  for(let i=0;i<9;i++)crew.push({a:[-25+rnd()*10,4,3+rnd()*20],b:[-25+rnd()*10,4,3+rnd()*20],t:rnd(),sp:.06+rnd()*.1,col:pick(['c8402f','2f5d4a','243a52','7a4a2f'])});
  CR.data=crew;
  // distant sail
  const DS=grp('DISTANT SAIL',{dyn:true,label:'Distant Sail',desc:'A lugger standing out of the roads'});
  DS.data=[0];
  // gulls' shadow: skip
}

/* ============================================================
   8 · mesh construction
   ============================================================ */
const boxGeo=new THREE.BoxGeometry(1,1,1);boxGeo.translate(0,.5,0);
const lambert=new THREE.MeshLambertMaterial({color:0xffffff});
const tmpCol=new THREE.Color(),tmpHSL={h:0,s:0,l:0};
let totalVox=0,parts=0;
const pickList=[];
function buildMeshes(){
  for(const k in G){
    const g=G[k];if(!g.items.length)continue;
    const o=g.opts;
    let mat;
    if(o.basic){
      mat=new THREE.MeshBasicMaterial({color:0xffffff,transparent:o.transparent!==false,opacity:o.opacity??.9,depthWrite:o.depthWrite!==false,fog:o.fog!==false});
      if(o.blending)mat.blending=o.blending;
    }else{
      mat=lambert.clone();
      if(o.transparent){mat.transparent=true;mat.opacity=o.opacity??.92;mat.depthWrite=o.depthWrite!==false}
    }
    const n=g.items.length;
    const mesh=new THREE.InstancedMesh(boxGeo,mat,n);
    const arr=mesh.instanceMatrix.array;arr.fill(0);
    for(let i=0;i<n;i++)arr[i*16+15]=1;
    if(o.dyn)mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
    mesh.castShadow=!o.basic&&!o.noShadow;
    mesh.receiveShadow=!o.basic&&!o.noShadow;
    mesh.frustumCulled=false;
    for(let i=0;i<n;i++){
      const it=g.items[i],q=i*16;
      arr[q]=it.sx??1;arr[q+5]=it.h;arr[q+10]=it.sz??1;
      arr[q+12]=it.x;arr[q+13]=it.y;arr[q+14]=it.z;
      // voxel texture: subtle value jitter, extra light on tall pieces
      tmpCol.setHex(it.c,THREE.SRGBColorSpace);tmpCol.getHSL(tmpHSL);
      const j=.945+hash2(Math.round(it.x*3),Math.round(it.z*3))*(.11);
      const topLight=(it.h>=1&&it.x%1===0)?1:1;
      tmpCol.setHSL(tmpHSL.h,tmpHSL.s,clamp(tmpHSL.l*j*topLight,.015,.97));
      mesh.setColorAt(i,tmpCol);
    }
    if(o.dyn){
      const len=g.items.length;
      g.px=new Float32Array(len);g.py=new Float32Array(len);g.pz=new Float32Array(len);
      for(let i=0;i<len;i++){g.px[i]=g.items[i].x;g.py[i]=g.items[i].y;g.pz[i]=g.items[i].z}
    }
    g.mesh=mesh;g.n=n;
    g.baseHSL=new Float32Array(len*3);
    for(let i=0;i<len;i++){mesh.getColorAt(i,tmpCol);tmpCol.getHSL(tmpHSL);g.baseHSL[i*3]=tmpHSL.h;g.baseHSL[i*3+1]=tmpHSL.s;g.baseHSL[i*3+2]=tmpHSL.l}
    mesh.userData.gr=g;
    (g.opts.parent?shipRoot:scene).add(mesh);
    totalVox+=n;parts++;
    if(o.pick!==false&&!o.basic)pickList.push(mesh);
    mesh.visible=g.opts.visible!==false;
  }
}
const shipRoot=new THREE.Group();
shipRoot.position.set(SAIL.x,0,SAIL.z);
scene.add(shipRoot);

/* ============================================================
   9 · state
   ============================================================ */
const HOURS={
  golden:{sun:'#ffd7a3',si:2.9,sy:36,sky:'#a9cadb',gnd:'#6b5c46',hemi:.72,fog:'#e9b487',fogD:.0052,exp:.98,beam:.1,glow:.35,
    sky:[[0,'#f8dcae'],[.06,'#f0b980'],[.16,'#cfa88f'],[.38,'#87aec7'],[.72,'#4d86b0'],[1,'#2f6695']],water:1,label:'GOLDEN'},
  noon:{sun:'#fff4dd',si:3.2,sy:150,sky:'#bcd8e6',gnd:'#7a715c',hemi:.86,fog:'#cfe0e6',fogD:.0038,exp:1.03,beam:0,glow:.05,
    sky:[[0,'#eaf3f6'],[.05,'#cfe4ea'],[.2,'#9cc6da'],[.55,'#6ea9c8'],[1,'#487fa5']],water:.8,label:'NOON'},
  dusk:{sun:'#8fb0d8',si:1.35,sy:16,sky:'#5f7fa6',gnd:'#3b3f3c',hemi:.5,fog:'#5d7590',fogD:.0068,exp:1.06,beam:.5,glow:1,
    sky:[[0,'#f0b06a'],[.05,'#d78c68'],[.14,'#8f6e86'],[.36,'#43618c'],[.7,'#274567'],[1,'#16283f']],water:1.15,label:'DUSK'}
};
const state={hour:'golden',sails:'set',tide:'high',rig:true,rot:true,sunEl:12,wind:.34,tideY:.15,tideTarget:.15,
  ship:{mode:'idle',t:0},hud:true};
let view={th:-2.35,ph:.92,d:112,tx:2,ty:6,tz:4},tween=null;
const PRESETS=[
  {th:-2.35,ph:.92,d:112,tx:2,ty:6,tz:4},
  {th:-1.02,ph:1.16,d:27,tx:-2.5,ty:9,tz:-6},
  {th:-1.52,ph:1.27,d:31,tx:-14,ty:5,tz:21},
  {th:2.28,ph:1.02,d:64,tx:40,ty:13,tz:1}
];
function applyHour(){
  const H=HOURS[state.hour];
  sun.color.set(H.sun);sun.intensity=H.si;
  hemi.color.set(H.sky);hemi.groundColor.set(H.gnd);hemi.intensity=H.hemi;
  scene.fog.color.set(H.fog);scene.fog.density=H.fogD;
  renderer.toneMappingExposure=H.exp;
  setSky(H.sky);
  sunSprite.material.color.set(H.sun);
  lampLight.intensity=44*H.glow+8;
  if(beam)beam.mesh.material.opacity=H.beam;
  setSun();
  if(G['LANTERN GLOW'])G['LANTERN GLOW'].mesh.material.opacity=.35+.62*H.glow;
}
function setSky(stops){
  const old=scene.background;
  const t=makeSky(stops);scene.background=t;
  scene.environment=pmrem.fromEquirectangular(t).texture;
  if(old)old.dispose();
}
function setSun(){
  const el=state.sunEl*Math.PI/180,az=-1.15;
  const d=new THREE.Vector3(Math.cos(el)*Math.cos(az),Math.sin(el),Math.cos(el)*Math.sin(az));
  sun.position.copy(d).multiplyScalar(150);sun.target.position.set(0,4,0);
  sunSprite.position.copy(d).multiplyScalar(300);
}
function makeSky(stops){
  const c=document.createElement('canvas');c.width=16;c.height=512;const x=c.getContext('2d');
  const g=x.createLinearGradient(0,0,0,512);
  stops.forEach(([p,col])=>g.addColorStop(1-p,col));
  x.fillStyle=g;x.fillRect(0,0,16,512);
  const t=new THREE.CanvasTexture(c);t.mapping=THREE.EquirectangularReflectionMapping;t.colorSpace=THREE.SRGBColorSpace;return t;
}
function makeGlow(a,b){
  const c=document.createElement('canvas');c.width=c.height=128;const x=c.getContext('2d');
  const g=x.createRadialGradient(64,64,0,64,64,64);
  g.addColorStop(0,a);g.addColorStop(.25,b);g.addColorStop(1,'rgba(255,180,100,0)');
  x.fillStyle=g;x.fillRect(0,0,128,128);
  const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;return t;
}

/* ============================================================
   10 · animation
   ============================================================ */
function waveY(x,z,t){
  const A=.14+state.wind*.55;
  let y=state.tideY+A*(.5*Math.sin(x*.28+t*1.5)+.35*Math.sin(z*.22-t*1.15)+.3*Math.sin((x+z)*.165+t*.8));
  const d=seaOf(x)-z;
  if(d<9&&d>-2)y+=Math.max(0,(9-d)/9)*.28*Math.sin(x*.8+t*3.1);
  return y;
}
let T=0;
function updateWater(t){
  const g=G['TIDE'];if(!g.mesh)return;
  const m=g.mesh.instanceMatrix.array,ia=g.mesh.instanceColor.array,base=g.baseHSL;
  const n=g.n,glow=HOURS[state.hour].glow;
  for(let i=0;i<n;i++){
    const x=g.px[i],z=g.pz[i],y=waveY(x,z,t);
    const q=i*16;
    m[q]=1.4;m[q+5]=y+6;m[q+10]=1.4;
    m[q+12]=x;m[q+13]=(y-6)/2;m[q+14]=z;
    const h=Math.sin(x*.9+t*1.6)*Math.sin(z*1.1-t*1.3);
    const sp=hash2(Math.round(x*2),Math.round(z*2));
    let l=base[i*3+2]+h*.055+(sp>.985?.26*(0.5+0.5*Math.sin(t*4+sp*40)):0);
    if(glow>.3)l*=1-glow*.28;
    tmpCol.setHSL(base[i*3]+(h>.6?.02:0),base[i*3+1]*(1+.06*Math.abs(h)),clamp(l,.02,.96));
    ia[i*3]=tmpCol.r;ia[i*3+1]=tmpCol.g;ia[i*3+2]=tmpCol.b;
  }
  g.mesh.instanceMatrix.needsUpdate=true;g.mesh.instanceColor.needsUpdate=true;
}
function setInst(g,i,x,y,z,sx,sy,sz,col){
  const m=g.mesh.instanceMatrix.array,q=i*16;
  m[q]=sx;m[q+5]=sy;m[q+10]=sz;m[q+12]=x;m[q+13]=y;m[q+14]=z;
  if(col){const ia=g.mesh.instanceColor.array;g.mesh.getColorAt(0,tmpCol);ia[q/16*3]=col.r;ia[q/16*3+1]=col.g;ia[q/16*3+2]=col.b}
}
function updateFlag(t){
  const g=G['ENSIGN'];if(!g.mesh)return;
  const amp=.25+state.wind*1.2;
  g.data.forEach(([ix,iy],i)=>{
    const x=1+ix*.65,y=26.5-iy*.62,z=-1+Math.sin(ix*.8-t*7)*amp*(ix/8);
    const c=(iy<2||(iy>3&&ix>4))?'#f5f1e6':'#c8402f';
    tmpCol.setHex(c,THREE.SRGBColorSpace);
    setInst(g,i,x,y,z,.7,.62,.34,tmpCol);
  });
  g.mesh.instanceMatrix.needsUpdate=true;g.mesh.instanceColor.needsUpdate=true;
}
const q4=new THREE.Quaternion(),v3=new THREE.Vector3(),sc1=new THREE.Vector3(1,1,1),mm=new THREE.Matrix4();
function updateGulls(t){
  const g=G['GULLS'];if(!g.mesh)return;let i=0;
  const spd=.7+state.wind*1.1;
  for(const gu of gulls){
    const a=t*gu.sp*spd+gu.ph;
    const x=gu.c[0]+Math.cos(a)*gu.r,z=gu.c[1]+Math.sin(a)*gu.r*1.4;
    const y=gu.alt+Math.sin(t*.9+gu.ph)*2.4;
    const yaw=Math.atan2(-Math.sin(a)*1.4,-Math.cos(a));
    q4.setFromAxisAngle(v3.set(0,1,0),yaw);
    const flap=Math.sin(t*8.5+gu.ph);
    const vox=[[0,0,0,.9,.7,.9,'f7f1e3'],[0,0,1,.8,.6,.7,'f7f1e3'],[0,0,-1,.7,.5,.7,'e6dcc6'],
      [1.5,flap*.5,0,.5,.28,1.5,'f7f1e3'],[-1.5,flap*.5,0,.5,.28,1.5,'f7f1e3'],
      [2.2,flap*.8,0,.4,.2,1.1,'ddd0b4'],[-2.2,flap*.8,0,.4,.2,1.1,'ddd0b4'],[0,.35,-.5,.4,.4,.6,'2f2c28']];
    for(const[ox,oy,oz,sx,sy,sz,c]of vox){
      v3.set(ox,oy,oz).applyQuaternion(q4);
      mm.compose(v3.set(x+v3.x,y+v3.y,z+v3.z),q4,sc1.set(sx,sy,sz));
      g.mesh.setMatrixAt(i,mm);
      tmpCol.setHex(c,THREE.SRGBColorSpace);g.mesh.setColorAt(i,tmpCol);
      i++;
    }
  }
  g.mesh.instanceMatrix.needsUpdate=true;g.mesh.instanceColor.needsUpdate=true;
}
function updateSmoke(t,dt){
  const g=G['SMOKE'];if(!g.mesh)return;
  const wind=.9+state.wind*3.2,glow=HOURS[state.hour].glow;
  g.data.forEach((p,i)=>{
    p.t+=dt*.11;
    if(p.t>1)p.t-=1;
    const u=p.t;
    const x=p.x+u*wind*1.9+Math.sin(u*5+p.x)*.4;
    const y=p.y+u*9.5, z=p.z+u*wind*.7+Math.cos(u*4+p.z)*.4;
    const s=(.55+u*2.4)*p.s;
    const m=g.mesh.instanceMatrix.array,q=i*16;
    m[q]=s;m[q+5]=s;m[q+10]=s;m[q+12]=x;m[q+13]=y;m[q+14]=z;
    const c=g.mesh.instanceColor.array;
    tmpCol.setHex('a9a89f',THREE.SRGBColorSpace);tmpCol.getHSL(tmpHSL);
    const ff=state.hour==='dusk'?1.06:1;
    tmpCol.setHSL(tmpHSL.h,tmpHSL.s*(1-u*.7),clamp(tmpHSL.l*(1-u*.45)*ff*(1-glow*.2)+.06*glow,.02,.95));
    c[i*3]=tmpCol.r;c[i*3+1]=tmpCol.g;c[i*3+2]=tmpCol.b;
  });
  g.mesh.instanceMatrix.needsUpdate=true;g.mesh.instanceColor.needsUpdate=true;
}
function updateClouds(t){
  const g=G['CLOUDS'];if(!g.mesh)return;let i=0;
  const drift=t*(.5+state.wind*1.5),glow=HOURS[state.hour].glow;
  for(const c of clouds){
    let x=((c.x+drift+90)%180)-90;
    for(const[p,q,r]of c.puffs){
      setInst(g,i++,x+p,c.y+q,c.z+r,3.2,2.2,3.2);
      const cc=g.mesh.instanceColor.array;
      tmpCol.setHex('f7f1e3',THREE.SRGBColorSpace);tmpCol.getHSL(tmpHSL);
      tmpCol.setHSL(tmpHSL.h+(glow>.5?.02:0),tmpHSL.s+.05,clamp(tmpHSL.l*(1-glow*.45)+glow*.16,.05,.98));
      cc[i*3-3]=tmpCol.r;cc[i*3-2]=tmpCol.g;cc[i*3-1]=tmpCol.b;
    }
  }
  g.mesh.instanceMatrix.needsUpdate=true;g.mesh.instanceColor.needsUpdate=true;
}
function updateGlow(t){
  const g=G['LANTERN GLOW'];if(!g.mesh)return;
  const gl=HOURS[state.hour].glow,ia=g.mesh.instanceColor.array;
  g.data.forEach(([x,y,z,s],i)=>{
    const f=.72+.28*Math.abs(Math.sin(t*(2.1+(x%3))+z*.7))+.08*Math.sin(t*9+x);
    const q=i*16,m=g.mesh.instanceMatrix.array;
    const ss2=s*(.86+.3*f*gl);
    m[q]=ss2;m[q+5]=ss2*1.35;m[q+10]=ss2;m[q+12]=x;m[q+13]=y;m[q+14]=z;
    tmpCol.setHSL(.085,.72,clamp(.18+.62*f*gl,.03,.95));
    ia[i*3]=tmpCol.r;ia[i*3+1]=tmpCol.g;ia[i*3+2]=tmpCol.b;
  });
  g.mesh.instanceMatrix.needsUpdate=true;g.mesh.instanceColor.needsUpdate=true;
  lampLight.intensity=(44*gl+6)*(.85+.15*Math.sin(t*5.3));
}
function updateBeam(t){
  const g=G['LIGHTHOUSE BEAM'];if(!g.mesh||!beamPos)return;
  const a=t*.55;
  const ca=Math.cos(a),sa=Math.sin(a);
  const ia=g.mesh.instanceColor.array;
  g.data.forEach((i,idx)=>{
    const d=1+i*1.5;
    const x=beamPos[0]+ca*d,z=beamPos[2]+sa*d,y=beamPos[1]+Math.sin(i*.2)*.15;
    const s=.9+i*.24;
    const m=g.mesh.instanceMatrix.array,q=idx*16;
    m[q]=d*1.5;m[q+5]=s*2.6;m[q+10]=s*1.4;m[q+12]=x;m[q+13]=y;m[q+14]=z;
    const f=Math.pow(1-i/g.data.length,1.5);
    tmpCol.setHSL(.11,.65,.55*f);
    ia[idx*3]=tmpCol.r;ia[idx*3+1]=tmpCol.g;ia[idx*3+2]=tmpCol.b;
  });
  g.mesh.instanceMatrix.needsUpdate=true;g.mesh.instanceColor.needsUpdate=true;
}
function updateFoam(t){
  const g=G['FOAM'];if(!g.mesh)return;
  const ia=g.mesh.instanceColor.array,base=g.baseHSL;
  g.data.forEach(([x,z],i)=>{
    const y=waveY(x,z,t);
    const ph=Math.sin(x*.8+z*.5+t*2.3);
    const s=clamp(.4+.6*ph,0,1);
    const m=g.mesh.instanceMatrix.array,q=i*16;
    m[q]=1.5;m[q+5]=Math.max(.06,s*.9);m[q+10]=1.5;m[q+12]=x;m[q+13]=y-.1;m[q+14]=z;
    tmpCol.setHSL(base[i*3],base[i*3+1]*s,.94*s+.2);
    ia[i*3]=tmpCol.r;ia[i*3+1]=tmpCol.g;ia[i*3+2]=tmpCol.b;
  });
  g.mesh.instanceMatrix.needsUpdate=true;g.mesh.instanceColor.needsUpdate=true;
}
function updateWake(t){
  const g=G['WAKE'];if(!g.mesh)return;
  const ia=g.mesh.instanceColor.array;
  const sp=state.ship.mode==='idle'?0:shipSpeed(t);
  const bx=shipRoot.position.x,bz=shipRoot.position.z;
  g.data.forEach((i,idx)=>{
    const seed=hash2(idx*13,7)*1;
    const life=((t*.5+seed)%1);
    const ang=(seed-.5)*1.5+shipRoot.rotation.y;
    const d=6+life*24;
    const x=bx-Math.cos(ang)*d-Math.sin(ang)*(seed-.5)*10;
    const z=bz-Math.sin(ang)*d+Math.cos(ang)*(seed-.5)*10;
    const y=waveY(x,z,t)+.05;
    const s=(.5+seed)*(1.4-life)*clamp(sp*2.6,0,1);
    const m=g.mesh.instanceMatrix.array,q=idx*16;
    m[q]=s*2.2;m[q+5]=.25;m[q+10]=s*2.2;m[q+12]=x;m[q+13]=y;m[q+14]=z;
    tmpCol.setHSL(.52,.15,.92*(1-life*.8));
    ia[idx*3]=tmpCol.r;ia[idx*3+1]=tmpCol.g;ia[idx*3+2]=tmpCol.b;
  });
  g.mesh.instanceMatrix.needsUpdate=true;g.mesh.instanceColor.needsUpdate=true;
}
function updateHands(t){
  const g=G['CLOCK & TIDE'];if(!g.mesh||!clockFace)return;
  const[cx,cy,cz]=clockFace;
  const minA=t*.9,hrA=t*.075;
  const set=(i,a,len,col)=>{
    const x=cx+Math.sin(a)*len*.5,y=cy+Math.cos(a)*len*.5;
    const m=g.mesh.instanceMatrix.array,q=i*16;
    m[q]=.22;m[q+5]=len;m[q+10]=.3;m[q+12]=x;m[q+13]=y;m[q+14]=cz;
    const c=g.mesh.instanceColor.array;tmpCol.setHex(col,THREE.SRGBColorSpace);
    c[i*3]=tmpCol.r;c[i*3+1]=tmpCol.g;c[i*3+2]=tmpCol.b;
  };
  set(0,minA,2.6,'221c18');set(1,hrA,1.8,'221c18');
  set(2,0,0,0);
  g.mesh.instanceMatrix.needsUpdate=true;g.mesh.instanceColor.needsUpdate=true;
}
function updateMill(t){
  const g=G['WINDMILL BLADES'];if(!g.mesh)return;
  const cx=-46,cz=54,cy=landH(cx,cz)+11.5,a=t*(.5+state.wind*1.8);
  q4.setFromAxisAngle(v3.set(0,0,1),a);
  g.data.forEach((i,idx)=>{
    q4.setFromAxisAngle(v3.set(0,0,1),a+i*Math.PI/2);
    v3.set(0,3.2,0).applyQuaternion(q4);
    mm.compose(v3.set(cx+v3.x,cy+v3.y,cz+.9+v3.z),q4,sc1.set(1.1,6.4,.5));
    g.mesh.setMatrixAt(idx,mm);
    tmpCol.setHex(idx%2?'584b46':'d8cbb2',THREE.SRGBColorSpace);g.mesh.setColorAt(idx,tmpCol);
  });
  g.mesh.instanceMatrix.needsUpdate=true;g.mesh.instanceColor.needsUpdate=true;
}
function updateCrew(t){
  const g=G['PIR CREW'];if(!g.mesh)return;let i=0;
  const cols=[];
  for(const c of crew){
    const u=(Math.sin(t*c.sp*Math.PI+c.t*6.28)+1)/2;
    const x=lerp(c.a[0],c.b[0],u),y=c.a[1],z=lerp(c.a[2],c.b[2],u);
    const step=Math.sin(t*c.sp*22+c.t*10)*.28;
    const vox=[[0,0,0,'243a52'],[0,1,0,'243a52'],[0,2,0,c.col],[0,3,0,'e6cfa8'],[0,4,0,'241f1c'],[0,2,step,'d8cbb2']];
    for(const[ox,oy,oz,cc]of vox){
      setInst(g,i++,x+ox,y+oy,z+oz,.7,.85,.7);
      tmpCol.setHex(cc,THREE.SRGBColorSpace);
      const ia=g.mesh.instanceColor.array;ia[(i-1)*3]=tmpCol.r;ia[(i-1)*3+1]=tmpCol.g;ia[(i-1)*3+2]=tmpCol.b;
    }
  }
  g.mesh.instanceMatrix.needsUpdate=true;g.mesh.instanceColor.needsUpdate=true;
}
function updateSail(t){
  const g=G['DISTANT SAIL'];if(!g.mesh)return;
  const loop=180,x=((t*3.2+loop)%loop)-90,z=-56,y=waveY(x,z,t);
  const set=(i,ox,oy,oz,sx,sy,sz,c)=>{
    const m=g.mesh.instanceMatrix.array,q=i*16;
    m[q]=sx;m[q+5]=sy;m[q+10]=sz;m[q+12]=x+ox;m[q+13]=y+oy;m[q+14]=z+oz;
    const ia=g.mesh.instanceColor.array;tmpCol.setHex(c,THREE.SRGBColorSpace);
    ia[i*3]=tmpCol.r;ia[i*3+1]=tmpCol.g;ia[i*3+2]=tmpCol.b;
  };
  set(0,0,0.4,0,3.4,1.1,7,'3b3a36');set(1,0,4.5,0,.5,7,1,'6b4a2f');
  set(2,1.4,4.4,-.6,2.4,6,1,'efe6cf');set(3,-1.6,3.6,1,2,4.6,1,'e8dcc0');
  g.mesh.instanceMatrix.needsUpdate=true;g.mesh.instanceColor.needsUpdate=true;
}

/* ---- ship motion ---- */
const WAY=[
  [-18,-4,0],[-22,4,.16],[-20,16,.5],[-8,26,.95],[14,30,1.45],[34,22,1.95],[48,4,2.4],[56,-16,2.9],[58,-38,3.25]
];
function shipPath(u){
  const n=WAY.length-1;
  const i=Math.min(n-1,Math.floor(u)),a=WAY[i],b=WAY[i+1],t=ss(u-i);
  let d=b[2]-a[2];while(d>Math.PI)d-=2*Math.PI;while(d<-Math.PI)d+=2*Math.PI;
  return[lerp(a[0],b[0],t),lerp(a[1],b[1],t),a[2]+d*t];
}
function shipSpeed(t){
  const u=shipU(t);const a=shipPath(clamp(u-.05,0,nWay)),b=shipPath(clamp(u+.05,0,nWay));
  return Math.hypot(b[0]-a[0],b[1]-a[1])/0.1/28;
}
let nWay=WAY.length-1;
function shipU(t){return clamp(t,0,nWay)}
function updateShip(dt,t){
  const s=state.ship;
  if(s.mode==='weigh'){s.t+=dt*.42;if(s.t>=nWay){s.t=nWay;s.mode='away';s.hold=0;log('Second anchor let go in nine fathoms, clear of the point. She rides to it like a gull on a wire.','sig')}}
  else if(s.mode==='away'){s.hold+=dt;if(s.hold>7){s.mode='return';log('Full survey made. She comes back on the flood, every sail paying her way.','')}}
  else if(s.mode==='return'){s.t-=dt*.42;if(s.t<=0){s.t=0;s.mode='idle';log('Moored. Lines cast off, gangway down, and the tidewaiter is aboard with his book.','sig')}}
  let pos,yaw;
  if(s.mode==='away'){
    const w=WAY[nWay],a=s.hold*.35;
    pos=[w[0]+Math.cos(a)*7,w[1]+Math.sin(a)*7];yaw=w[2]+Math.sin(a*.6)*.2;
  }else{const p=shipPath(s.t);pos=[p[0],p[1]];yaw=p[2]}
  shipRoot.position.set(pos[0],Math.sin(t*1.05)*.13,pos[1]);
  shipRoot.rotation.y=yaw;
  shipRoot.rotation.z=Math.sin(t*.9)*.018+state.wind*.02*Math.sin(t*.4);
  shipRoot.rotation.x=Math.sin(t*1.3)*.012;
}

/* ============================================================
   11 · UI / log / interaction
   ============================================================ */
const loglist=document.getElementById('loglist');let logN=0,gameMin=6*60+42,seen=new Set();
function fmt(m){const h=Math.floor(m/60)%24,mm=Math.floor(m%60);return String(h).padStart(2,'0')+':'+String(mm).padStart(2,'0')}
function log(txt,cls=''){
  const li=document.createElement('li');li.className=cls;
  li.innerHTML=`<time>${fmt(gameMin)}</time><p>${txt}</p>`;
  loglist.prepend(li);logN++;
  while(loglist.children.length>14)loglist.lastChild.remove();
}
const IDLE=[
  'Gulls over the fish market. The cooper’s boy counts barrels and loses count twice.',
  'A lugger stands out of the roads, her lug set full and flying.',
  'The mill on the west heights turns with the off-shore air.',
  'Tea is landed at the custom house. Fourteen chests, all sound.',
  'The harbor clock strikes the half hour. The tide-waiter marks the tide.',
  'Water carts roll the cobbles. The chandlery lantern is lit before its hour.',
  'Rigging sings in the off-shore air. All fenders aloft.'
];
let idleT=0;
function setSails(m){
  state.sails=m;
  G['SQUARE SAILS'].mesh.visible=(m==='set');
  G["FURL'D SAILS"].mesh.visible=(m!=='set');
  G['FORE-AND-AFT'].mesh.visible=(m==='set');
  document.querySelector('#b-sails .v').textContent=m==='set'?'SET':'FURL’D';
  document.getElementById('b-sails').classList.toggle('on',m!=='set');
  log(m==='set'?'Sails set. She heels a whisper and owns the tide again.':'Sails furl’d, yards piped down. Canvas bayed up, and the crew takes to the slop-chest.');
}
function setHour(h){
  state.hour=h;applyHour();
  document.querySelector('#b-hour .v').textContent=HOURS[h].label;
  document.getElementById('b-hour').classList.toggle('on',h==='dusk');
  log(h==='dusk'?'Dusk. The light is lit, and every window on the quay kindles one by one.'
    :h==='noon'?'Noon sun. The harbor lies flat and blue, and the town shows its plaster.'
    :'Golden hour. Long shadows from the light, and the water goes to copper.');
}
function setTide(v){
  state.tide=v;state.tideTarget=v==='high'?.15:-1.25;
  document.querySelector('#b-tide .v').textContent=v.toUpperCase();
  document.getElementById('b-tide').classList.toggle('on',v==='low');
  log(v==='high'?'Tide riding high. The hull floats easy and the fenders sigh against the stone.'
    :'Tide made low. The quay shows her barnacles, and the chain lies slack at the ring.');
}
function setRig(v){
  state.rig=v;G['RIGGING'].mesh.visible=v;
  document.querySelector('#b-rig .v').textContent=v?'ON':'OFF';
  document.getElementById('b-rig').classList.toggle('on',!v);
  log(v?'Rigging set up again — every line aloft.':'Rigging struck. The masts stand bare as a yard at dawn.');
}
function weigh(){
  if(state.ship.mode==='idle'){state.ship.mode='weigh';log('Weigh, weigh! The turnblocks sing. She comes round with the ebb and answers the tiller.','sig');setView(0)}
  else if(state.ship.mode==='away'){state.ship.mode='return';state.ship.hold=7;log('Bring her home. The berth is clear and the pilot is aboard.','sig')}
  const b=document.getElementById('b-weigh');
  b.classList.toggle('on',state.ship.mode!=='idle');
  b.textContent=(state.ship.mode==='idle')?'Weigh anchor':'Return to berth';
}
function setView(i){
  const p=PRESETS[i];tween={f:{...view},t:{...p},k:0};
  document.querySelectorAll('.view').forEach((b,k)=>b.classList.toggle('on',k===i));
  ['Anchorage full plate. Every spar counted.','At the quarterdeck. Tar, hemp, and the smell of the fish market.','On the cobbles among the porters and the awnings.','The breakwater end, wind off the sea.'],
  log('Survey set: '+(document.querySelectorAll('.view')[i].querySelector('.t').firstChild.textContent||'view').trim()+'.');
}
document.getElementById('b-sails').onclick=()=>setSails(state.sails==='set'?'furled':'set');
document.getElementById('b-hour').onclick=()=>setHour(state.hour==='golden'?'noon':state.hour==='noon'?'dusk':'golden');
document.getElementById('b-tide').onclick=()=>setTide(state.tide==='high'?'low':'high');
document.getElementById('b-rig').onclick=()=>setRig(!state.rig);
document.getElementById('b-weigh').onclick=weigh;
document.getElementById('b-rot').onclick=()=>{state.rot=!state.rot;document.getElementById('b-rot').classList.toggle('on',!state.rot);document.querySelector('#b-rot .v').textContent=state.rot?'ON':'OFF';};
document.getElementById('b-hud').onclick=e=>{state.hud=!state.hud;document.body.classList.toggle('nohud',!state.hud);e.target.textContent=state.hud?'Hide HUD':'Show HUD'};
document.getElementById('s-sun').oninput=e=>{state.sunEl=+e.target.value;document.getElementById('v-sun').textContent=state.sunEl+'°';setSun()};
document.getElementById('s-wind').oninput=e=>{state.wind=+e.target.value/100;document.getElementById('v-wind').textContent=Math.round(state.wind*10);};
document.querySelectorAll('.view').forEach(b=>b.onclick=()=>setView(+b.dataset.v));

/* ---- camera ---- */
let drag=null,pan=false,shiftPan=false;
canvas.addEventListener('pointerdown',e=>{
  drag={x:e.clientX,y:e.clientY};pan=(e.button===2||e.shiftKey);canvas.classList.add('drag');
  canvas.setPointerCapture(e.pointerId);
});
canvas.addEventListener('pointerup',e=>{drag=null;canvas.classList.remove('drag')});
canvas.addEventListener('contextmenu',e=>e.preventDefault());
canvas.addEventListener('pointermove',e=>{
  mouse.x=e.clientX;mouse.y=e.clientY;mouseNdc.x=(e.clientX/innerWidth)*2-1;mouseNdc.y=-(e.clientY/innerHeight)*2+1;
  const cr=document.getElementById('cross');cr.style.opacity='1';
  cr.querySelector('.h').style.top=e.clientY+'px';cr.querySelector('.v').style.left=e.clientX+'px';
  document.getElementById('hint').classList.add('dim');
  if(!drag)return;
  const dx=e.clientX-drag.x,dy=e.clientY-drag.y;drag={x:e.clientX,y:e.clientY};tween=null;
  if(pan){
    const s=view.d*.0016;
    const rx=-Math.sin(view.th),rz=Math.cos(view.th);
    view.tx-=(dx*rx-dy*Math.cos(view.th))*s;view.tz-=(dx*Math.cos(view.th)+dy*(-rx))*s*-1;
    view.tx=clamp(view.tx,-70,70);view.tz=clamp(view.tz,-70,70);
  }else{
    view.th-=dx*.0062;view.ph=clamp(view.ph-dy*.005,.06,1.45);
  }
});
canvas.addEventListener('wheel',e=>{e.preventDefault();view.d=clamp(view.d*Math.exp(e.deltaY*.0011),16,190);tween=null},{passive:false});
addEventListener('keydown',e=>{
  const k=e.key.toLowerCase();
  if('1234'.includes(k))setView(+k-1);
  if(k==='s')setSails(state.sails==='set'?'furled':'set');
  if(k==='h')setHour(state.hour==='golden'?'noon':state.hour==='noon'?'dusk':'golden');
  if(k==='t')setTide(state.tide==='high'?'low':'high');
  if(k==='r')setRig(!state.rig);
  if(k==='q')document.getElementById('b-hud').click();
  if(k===' '){e.preventDefault();weigh()}
});

/* ---- picking ---- */
const ray=new THREE.Raycaster();const mouseNdc=new THREE.Vector2(-2,-2);
const mouse={x:0,y:0};const plane=new THREE.Plane(new THREE.Vector3(0,1,0),0);
const tip=document.getElementById('tip');let pickFrame=0;
function updatePick(){
  if(document.body.classList.contains('nohud')){tip.classList.remove('show');return}
  ray.setFromCamera(mouseNdc,camera);
  let hit=null;
  const hits=ray.intersectObjects(pickList,false);
  if(hits.length)hit=hits[0];
  const p=new THREE.Vector3();
  if(hit){
    const g=hit.object.userData.gr;
    tip.querySelector('.n').textContent=g.label;
    tip.querySelector('.d').textContent=g.desc;
    tip.querySelector('.c').textContent=g.n.toLocaleString()+' VOXELS';
    tip.style.left=mouse.x+'px';tip.style.top=mouse.y+'px';tip.classList.add('show');
    canvas.classList.add('pick');
    if(g.desc&&!seen.has(g.label)){seen.add(g.label);log('Charted: <b>'+g.label+'</b> — '+g.desc,'')}
    locPoint(hit.point);
  }else{
    raycasterPlane(p);
    tip.classList.remove('show');canvas.classList.remove('pick');
    locPoint(p);
  }
}
function raycasterPlane(p){ray.ray.intersectPlane(plane,p)}
function locPoint(p){
  if(!p||!isFinite(p.x)){document.getElementById('m-pos').textContent='— —';return}
  const lat=51+(62-p.z)/100*0.42, lon=-2.35+p.x/100*0.55;
  const f=v=>{const d=Math.floor(Math.abs(v)),m=Math.round((Math.abs(v)-d)*60);return String(d).padStart(2,'0')+'° '+String(m).padStart(2,'0')+'′'};
  document.getElementById('m-pos').textContent=`${f(lat)}${lat>=0?'N':'S'}  ${f(Math.abs(lon))}${lon>=0?'E':'W'}`;
}

/* ============================================================
   12 · build sequence
   ============================================================ */
const STEPS=[
  ['Sounding the channel',()=>{buildSea();buildLand();}],
  ['Quay wall & cobble',()=>{}],
  ['Greystone town',()=>{buildTown()}],
  ['Breakwater & light',()=>{buildBreakwater()}],
  ['Long pier',()=>{buildPier()}],
  ['Hull, decks & spars',()=>{buildShip()}],
  ['Canvas & rigging',()=>{}],
  ['Gulls, smoke & cloud',()=>{buildLife()}],
  ['Lathing the plate',()=>{buildMeshes()}]
];
const psteps=document.getElementById('psteps');
STEPS.forEach(([t])=>{const d=document.createElement('div');d.textContent=t;psteps.appendChild(d)});
let si=0;
function runStep(){
  const [t,fn]=STEPS[si];
  document.getElementById('pstat').textContent=t+'…';
  psteps.children[si].classList.add('on');
  fn();
  si++;
  const pct=Math.round(si/STEPS.length*100);
  document.getElementById('pbar').style.width=pct+'%';
  document.getElementById('ppct').textContent=pct+'%';
  if(si<STEPS.length)setTimeout(runStep,58);
  else setTimeout(finish,220);
}
function finish(){
  applyHour();setSails('set');
  G['ENSIGN'].mesh.visible=true;
  // counts
  const vEl=document.getElementById('m-vox');let c=0;const target=totalVox;const t0=performance.now();
  (function up(){const k=Math.min(1,(performance.now()-t0)/900);vEl.textContent=Math.round(target*(1-Math.pow(1-k,3))).toLocaleString();if(k<1)requestAnimationFrame(up)})();
  document.getElementById('m-parts').textContent=parts;
  log('06:42 Wind ESE 3. Warped into the inner berth, stem to the quay. Ten fathoms, good holding ground.','sig');
  log('Cleared at the custom house. Manifest: iron, salt, and six hundred sacks of flour.');
  document.getElementById('load').classList.add('gone');
  tween={f:{th:view.th-.9,ph:view.ph+.32,d:view.d+52,tx:view.tx,ty:view.ty,tz:view.tz},t:{...view},k:0};
  view={...tween.f};
  running=true;
}
let running=false;
runStep();

/* ============================================================
   13 · loop
   ============================================================ */
const clock=new THREE.Clock();let fpsT=0,fpsN=0;
function loop(){
  requestAnimationFrame(loop);
  const dt=Math.min(.05,clock.getDelta());T+=dt;
  const t=T;
  // tide ease
  state.tideY=lerp(state.tideY,state.tideTarget,Math.min(1,dt*2.2));
  // camera tween
  if(tween){tween.k=Math.min(1,tween.k+dt/1.25);const k=ss(tween.k);
    view.th=lerp(tween.f.th,tween.t.th,k);view.ph=lerp(tween.f.ph,tween.t.ph,k);
    view.d=lerp(tween.f.d,tween.t.d,k);view.tx=lerp(tween.f.tx,tween.t.tx,k);
    view.ty=lerp(tween.f.ty,tween.t.ty,k);view.tz=lerp(tween.f.tz,tween.t.tz,k);
    if(tween.k>=1)tween=null;
  }
  if(state.rot&&!drag&&!tween)view.th+=dt*.052;
  const cp=Math.cos(view.th),sp2=Math.sin(view.th),ph=Math.sin(view.ph);
  camera.position.set(view.tx+view.d*ph*cp,Math.max(1.6,view.ty+view.d*Math.cos(view.ph)),view.tz+view.d*ph*Math.sin(view.th));
  camera.lookAt(view.tx,view.ty,view.tz);
  // heading
  const hdg=(Math.atan2(camera.position.x-view.tx,camera.position.z-view.tz)*180/Math.PI+180+360)%360;
  document.getElementById('roserot').setAttribute('transform',`rotate(${-hdg})`);
  document.getElementById('heading').textContent='HDG '+String(Math.round(hdg)).padStart(3,'0')+'°';
  // clock
  gameMin+=dt*3.2;document.getElementById('clock').textContent=fmt(gameMin);
  idleT+=dt;if(idleT>26){idleT=0;log(IDLE[Math.floor(rnd()*IDLE.length)])}
  // systems
  if(running){
    updateWater(t);updateFlag(t);updateGulls(t);updateSmoke(t,dt);updateClouds(t);
    updateGlow(t);updateBeam(t);updateFoam(t);updateWake(t);updateHands(t);updateMill(t);
    updateCrew(t);updateSail(t);updateShip(dt,t);
    if((pickFrame++&3)===0)updatePick();
    fpsN++;fpsT+=dt;
    if(fpsT>.5){document.getElementById('m-fps').textContent=Math.round(fpsN/fpsT);fpsN=0;fpsT=0}
  }
  renderer.render(scene,camera);
}
loop();
addEventListener('resize',()=>{
  camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight);renderer.setPixelRatio(Math.min(devicePixelRatio,2));
});
</script>
</body>
</html>
```

**What's on the plate**

- **The ship** — a three-masted barque warped into the inner berth: copper sheathing below the waterline, ochre wale with gunports, bulwarks, sterncastle with green-trimmed cabin, bowsprit and jib-boom, nine square sails *plus* spanker, jibs and staysails, and a shroud-by-shroud rigging ladder with ratlines, stays, lifts and braces. Mooring hawsers sag to the pier bollards; the gangway is down, deck cargo and stern lanterns aboard.
- **The harbor** — Greystone town of gabled houses, custom house with a working clock tower, fish-market awnings, warehouse chimneys venting drifting smoke, a windmill turning, a lamp-lit quay with bollards, capstan, fenders and a chandlery, plus a stepped breakwater with keeper's cottage, crane, and a banded lighthouse throwing a rotating additive beam.
- **Living elements** — animated voxel swell with surf foam at the quay, fluttering ensign, nine flapping gulls, walking quayside folk, chimney plumes, high cirrus, lit windows that kindle at dusk, a distant lugger on the roads, and a full departure: *weigh anchor* and she walks out through the breakwater with a white wake, then comes home.
- **Working the plate** — drag to orbit, wheel to zoom, shift-drag to pan, `1–4` for survey views, `S` sails, `H` hour, `T` tide, `R` rigging, `Space` weigh anchor, `Q` to strip the HUD. Hover anything to identify it — charted parts get logged, and the log keeps writing itself as the tide runs.