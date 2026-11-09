# Port Meridian — Voxel Diorama №VII

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Ship in Harbour — Voxel Diorama №VII</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,300;12..96,600;12..96,800&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Serif:ital,wght@0,400;1,400&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#050c12; --ink:#e9e2d3; --dim:#95a3ab;
  --brass:#dca755; --brass-dim:#8a6b3c;
  --panel:rgba(6,17,23,.72);
  --line:rgba(220,167,85,.26);
  --mono:"IBM Plex Mono",ui-monospace,monospace;
  --disp:"Bricolage Grotesque","Trebuchet MS",sans-serif;
  --serif:"IBM Plex Serif",Georgia,serif;
}
*{box-sizing:border-box}
html,body{margin:0;height:100%;background:var(--bg);overflow:hidden;font-family:var(--mono);color:var(--ink)}
canvas{display:block;position:fixed;inset:0}
#ui{position:fixed;inset:0;pointer-events:none;z-index:5}
#ui::after{
  content:"";position:absolute;inset:0;pointer-events:none;
  background:
    linear-gradient(180deg,rgba(0,0,0,.42),rgba(0,0,0,0) 26%,rgba(0,0,0,0) 62%,rgba(0,0,0,.5)),
    radial-gradient(120% 90% at 50% 45%,rgba(0,0,0,0) 55%,rgba(0,0,0,.55));
}
.panel{background:var(--panel);border:1px solid var(--line);backdrop-filter:blur(8px) saturate(1.1);
  box-shadow:0 24px 50px rgba(0,0,0,.5), inset 0 1px 0 rgba(255,220,170,.06);}

/* ---- title block ---- */
#title{position:absolute;top:26px;left:28px;padding:18px 22px 16px;max-width:min(38vw,430px);
  animation:rise .9s cubic-bezier(.2,.7,.2,1) both .1s}
.eyebrow{font-size:9.5px;letter-spacing:.42em;text-transform:uppercase;color:var(--brass);opacity:.92}
h1{font-family:var(--disp);font-weight:800;font-size:clamp(30px,4.1vw,52px);line-height:.86;
  letter-spacing:-.028em;margin:10px 0 0;text-wrap:balance}
h1 em{display:block;font-style:normal;font-weight:300;color:var(--brass);font-size:.44em;
  letter-spacing:.01em;line-height:1.2;margin-top:.42em}
.rule{height:1px;background:linear-gradient(90deg,var(--brass),rgba(220,167,85,0));margin:14px 0 12px}
.lede{font-family:var(--serif);font-size:12.4px;line-height:1.55;color:#c6cfcf;max-width:33ch;margin:0}
.legend{display:grid;grid-template-columns:auto 1fr;gap:4px 10px;margin-top:14px;font-size:9.6px;
  letter-spacing:.14em;text-transform:uppercase}
.legend b{color:var(--brass-dim);font-weight:500}
.legend span{color:#a9b6bd}

/* ---- control deck ---- */
#deck{position:absolute;left:28px;bottom:26px;padding:14px 16px 15px;display:flex;flex-wrap:wrap;
  gap:14px 22px;max-width:min(74vw,720px);pointer-events:auto;
  animation:rise .9s cubic-bezier(.2,.7,.2,1) both .25s}
.grp{display:flex;flex-direction:column;gap:7px}
.grp>small{font-size:8.6px;letter-spacing:.3em;text-transform:uppercase;color:var(--brass-dim)}
.pills{display:flex;gap:5px;flex-wrap:wrap}
button.pill{font-family:var(--mono);font-size:9.6px;letter-spacing:.16em;text-transform:uppercase;
  color:#c3d0d4;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.12);
  padding:7px 10px;cursor:pointer;transition:transform .16s,background .2s,color .2s,box-shadow .2s,border-color .2s}
button.pill:hover{color:#fff;border-color:rgba(220,167,85,.6);background:rgba(220,167,85,.12);
  transform:translateY(-2px);box-shadow:0 6px 16px rgba(0,0,0,.4)}
button.pill.on{background:linear-gradient(180deg,#e5b464,#c78c34);color:#1b1206;border-color:#f0cd8e;
  box-shadow:0 0 18px rgba(220,167,85,.4)}
.slidewrap{display:flex;align-items:center;gap:9px}
input[type=range]{-webkit-appearance:none;width:124px;height:2px;background:rgba(255,255,255,.16);outline:none;cursor:pointer}
input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:11px;height:16px;background:var(--brass);
  border:1px solid #f4d59b;box-shadow:0 0 10px rgba(220,167,85,.5);cursor:grab}
input[type=range]::-moz-range-thumb{width:11px;height:16px;border-radius:0;background:var(--brass);border:1px solid #f4d59b}
#windOut{font-size:10px;color:var(--brass);min-width:46px;letter-spacing:.08em}

/* ---- instrument readout ---- */
#readout{position:absolute;top:26px;right:26px;width:212px;padding:14px 15px 13px;
  animation:rise .9s cubic-bezier(.2,.7,.2,1) both .4s}
#readout header{display:flex;justify-content:space-between;align-items:baseline;
  font-size:8.6px;letter-spacing:.3em;text-transform:uppercase;color:var(--brass-dim);
  border-bottom:1px solid var(--line);padding-bottom:8px}
#compass{position:relative;height:52px;display:flex;align-items:center;justify-content:center;gap:14px}
.dial{position:relative;width:50px;height:50px;border:1px solid var(--line);border-radius:50%;
  background:radial-gradient(circle,rgba(220,167,85,.07),transparent 70%)}
.dial i{position:absolute;left:50%;top:50%;width:1px;height:5px;background:rgba(220,167,85,.45);
  transform-origin:50% 25px}
.needle{position:absolute;inset:6px;transition:transform .12s linear}
.needle::before{content:"";position:absolute;left:50%;top:0;width:2px;height:50%;background:var(--brass);
  transform:translateX(-50%);box-shadow:0 0 8px rgba(220,167,85,.6)}
.needle::after{content:"";position:absolute;left:50%;bottom:0;width:2px;height:44%;background:rgba(180,200,210,.35);transform:translateX(-50%)}
dl{display:grid;grid-template-columns:auto 1fr;gap:3px 8px;margin:4px 0 0;font-size:9.4px;letter-spacing:.09em}
dt{color:#7d8b93;text-transform:uppercase}
dd{margin:0;text-align:right;color:#e6ddca;font-variant-numeric:tabular-nums}
dd.hi{color:var(--brass)}
#sig{margin-top:9px;height:6px;background:linear-gradient(90deg,var(--brass),rgba(220,167,85,0));
  background-size:34% 100%;background-repeat:no-repeat;animation:trace 3.4s linear infinite;opacity:.55}

/* ---- hint ---- */
#hint{position:absolute;right:26px;bottom:26px;font-size:9.4px;letter-spacing:.18em;text-transform:uppercase;
  color:#8fa0a8;text-align:right;line-height:1.9;animation:rise .9s cubic-bezier(.2,.7,.2,1) both .55s}
#hint k{display:inline-block;border:1px solid rgba(255,255,255,.16);padding:2px 5px;color:#d8cfbd;
  font-family:var(--mono);letter-spacing:.1em;margin:0 2px}

/* ---- hover tip ---- */
#tip{position:fixed;left:0;top:0;transform:translate(-50%,-130%) scale(.92);opacity:0;pointer-events:none;
  padding:9px 12px;min-width:150px;max-width:250px;background:rgba(4,14,19,.9);
  border:1px solid var(--line);box-shadow:0 14px 30px rgba(0,0,0,.6);
  transition:opacity .16s,transform .16s;z-index:9}
#tip.show{opacity:1;transform:translate(-50%,-140%) scale(1)}
#tip b{display:block;font-size:10.5px;letter-spacing:.2em;text-transform:uppercase;color:var(--brass)}
#tip span{display:block;font-family:var(--serif);font-size:11.6px;line-height:1.45;color:#cdd6d6;margin-top:5px}
#tip small{display:block;margin-top:6px;font-size:8.4px;letter-spacing:.2em;color:#7c8a92;text-transform:uppercase}

/* ---- loader ---- */
#loader{position:fixed;inset:0;z-index:20;background:#050c12;display:flex;flex-direction:column;
  align-items:center;justify-content:center;gap:20px;transition:opacity .8s .15s,visibility .8s .15s}
#loader.done{opacity:0;visibility:hidden}
.hull{width:120px;height:22px;background:var(--brass);
  clip-path:polygon(0 40%,14% 100%,86% 100%,100% 40%,100% 40%,0 40%);opacity:.85}
.mast{width:2px;height:64px;background:var(--brass-dim);margin-bottom:-1px}
#loader p{font-size:9.6px;letter-spacing:.42em;text-transform:uppercase;color:#6f8089;margin:0}
#bar{width:220px;height:2px;background:rgba(255,255,255,.1);overflow:hidden}
#bar i{display:block;height:100%;width:8%;background:var(--brass);transition:width .3s}
#err{color:#e08a6a;font-size:11px;max-width:60ch;text-align:center;line-height:1.6;font-family:var(--serif);letter-spacing:0;text-transform:none}

@keyframes rise{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
@keyframes trace{from{background-position:-34% 0}to{background-position:134% 0}}
@media (max-width:1120px){#readout,#hint{display:none}#title{max-width:64vw}}
@media (prefers-reduced-motion:reduce){#sig{animation:none}}
</style>
</head>
<body>
<canvas id="c"></canvas>

<div id="ui">
  <div id="title" class="panel">
    <div class="eyebrow">Plate VII · Voxel Diorama</div>
    <h1>Ship in<br>Harbour<em>Port Meridian, late afternoon</em></h1>
    <div class="rule"></div>
    <p class="lede">The <i>Meridian</i>, 612 tons burthen, has come in on an offing breeze and rides at her moorings for canvas, hemp and fresh water. Gulls do the rest.</p>
    <div class="legend">
      <b>drag</b><span>orbit the basin</span>
      <b>scroll</b><span>zoom in to the gunwale</span>
      <b>right-drag</b><span>pan the plate</span>
      <b>hover</b><span>survey a structure</span>
      <b>click</b><span>bring it to the view</span>
    </div>
  </div>

  <div id="deck" class="panel">
    <div class="grp"><small>Watch</small><div class="pills" id="pillsTime"></div></div>
    <div class="grp"><small>Viewpoint</small><div class="pills" id="pillsView"></div></div>
    <div class="grp"><small>Ship</small><div class="pills">
      <button class="pill" id="bSails">set sails</button>
      <button class="pill" id="bOrbit">auto-orbit</button>
      <button class="pill" id="bBuild">re-build</button>
    </div></div>
    <div class="grp"><small>Wind</small><div class="slidewrap">
      <input id="wind" type="range" min="0" max="100" value="34"><span id="windOut">force 4</span>
    </div></div>
  </div>

  <div id="readout" class="panel">
    <header><span>Instrument</span><span id="sig2">◈</span></header>
    <div id="compass">
      <div class="dial"><div class="needle" id="needle"></div></div>
      <dl style="grid-template-columns:auto">
        <dd class="hi" id="rBrg">000° N</dd>
        <dd id="rElev">0°</dd>
      </dl>
    </div>
    <dl>
      <dt>voxels</dt><dd id="rVox">—</dd>
      <dt>clock</dt><dd id="rClock">17:42</dd>
      <dt>lights</dt><dd id="rLamp">—</dd>
      <dt>fps</dt><dd id="rFps">60</dd>
    </dl>
    <div id="sig"></div>
  </div>

  <div id="hint">
    <k>1</k><k>–</k><k>5</k> viewpoints &nbsp; <k>t</k> watch &nbsp; <k>s</k> sails &nbsp; <k>space</k> rebuild
  </div>
</div>

<div id="tip"><b></b><span></span><small>click to focus</small></div>

<div id="loader">
  <div class="mast"></div><div class="hull"></div>
  <p id="loadTxt">casting voxels</p>
  <div id="bar"><i></i></div>
  <div id="err"></div>
</div>

<script type="importmap">
{"imports":{
  "three":"https://unpkg.com/three@0.160.0/build/three.module.js",
  "three/addons/":"https://unpkg.com/three@0.160.0/examples/jsm/"
}}
</script>

<script type="module">
import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';

/* ══════════════════════════════════════ helpers ══════════════════════════════════════ */
let seed=1847; const rnd=()=>{ seed|=0; seed=seed+0x6D2B79F5|0; let t=Math.imul(seed^seed>>>15,1|seed);
  t=t+Math.imul(t^t>>>7,61|t)^t; return ((t^t>>>14)>>>0)/4294967296; };
const R=rnd;
const cl=(x,a=0,b=1)=>x<a?a:x>b?b:x;
const lerp=(a,b,t)=>a+(b-a)*t;
function hash2(x,z){const s=Math.sin(x*127.1+z*311.7)*43758.5453;return s-Math.floor(s);}
function vnoise(x,z){const xi=Math.floor(x),zi=Math.floor(z),xf=x-xi,zf=z-zi;
  const u=xf*xf*(3-2*xf),v=zf*zf*(3-2*zf);
  return lerp(lerp(hash2(xi,zi),hash2(xi+1,zi),u),lerp(hash2(xi,zi+1),hash2(xi+1,zi+1),u),v);}
function fbm(x,z){let s=0,a=.5,f=1;for(let i=0;i<3;i++){s+=vnoise(x*f,z*f)*a;a*=.5;f*=2;}return s*1.34;}
const C=h=>new THREE.Color(h);
const mixc=(a,b,t)=>a.clone().lerp(b,t);
const shade=(h,m)=>C(h).multiplyScalar(m);
const jit=(h,a=.05)=>C(h).offsetHSL((R()-.5)*.012,(R()-.5)*.03,(R()-.5)*a);

const geoBox=new THREE.BoxGeometry(1,1,1);
const N6=[[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]];
const _m=new THREE.Matrix4(),_q=new THREE.Quaternion(),_p=new THREE.Vector3(),_s=new THREE.Vector3(),
      _ay=new THREE.Vector3(0,1,0),_col=new THREE.Color(),_e=new THREE.Euler();

/* ══════════════════════════════════════ tags ══════════════════════════════════════ */
const TAGS=new Map();
function tag(name,desc){const k=name.toLowerCase().replace(/[^a-z0-9]+/g,'-');
  if(!TAGS.has(k))TAGS.set(k,{name,desc,cx:0,cy:0,cz:0,n:0,px:0,py:0,pz:0,
    min:new THREE.Vector3(1e6,1e6,1e6),max:new THREE.Vector3(-1e6,-1e6,-1e6)});
  return TAGS.get(k);}

/* ══════════════════════════════════════ voxel set ══════════════════════════════════════ */
class VoxelSet{
  constructor(){this.items=[];this.occ=new Set();this.ghost=null;}
  /* unit voxel at integer corner (x,y,z) */
  v(x,y,z,c,o){
    x=Math.round(x);y=Math.round(y);z=Math.round(z);
    if(o&&o.clip&&o.clip(x,y,z))return;
    const k=x+'|'+y+'|'+z; if(this.occ.has(k))return; this.occ.add(k);
    this.items.push({cx:x+.5,cy:y+.5,cz:z+.5,sx:1,sy:1,sz:1,c,o:o||0,unit:1});
  }
  /* box of unit voxels, hollowed when big */
  box(x,y,z,w,h,d,c,o={}){
    w=Math.round(w);h=Math.round(h);d=Math.round(d);
    const hol=w>3&&h>3&&d>3;
    for(let i=0;i<w;i++)for(let j=0;j<h;j++)for(let k=0;k<d;k++){
      if(hol&&i&&j&&k&&i<w-1&&j<h-1&&k<d-1)continue;
      const cc=typeof c==='function'?c(x+i,y+j,z+k,j/(h-1||1)):c;
      this.v(x+i,y+j,z+k,cc,o);
    }
  }
  /* slim (arbitrary size/pos, never culled) */
  s(x,y,z,sx,sy,sz,c,o=0){this.items.push({cx:x,cy:y,cz:z,sx,sy,sz,c,o,slim:1});}
  line(a,b,c,size=1,o={}){
    const n=Math.max(1,Math.ceil(a.distanceTo(b)/Math.max(size,.35)));
    for(let i=0;i<=n;i++){const t=i/n;
      const x=lerp(a.x,b.x,t),y=lerp(a.y,b.y,t),z=lerp(a.z,b.z,t);
      const s=size*(1-Math.abs(t-.5)*.25);
      this.s(x,y,z,s,s,s, typeof c==='function'?c(t):c, o);}
  }
  rope(a,b,c,size,sag,o={}){
    const n=Math.max(2,Math.ceil(a.distanceTo(b)/Math.max(size,.4)));
    for(let i=0;i<=n;i++){const t=i/n;
      const y=lerp(a.y,b.y,t)-Math.sin(Math.PI*t)*sag;
      this.s(lerp(a.x,b.x,t),y,lerp(a.z,b.z,t),size,size,size,c,o);}
  }
  text(x,y,z,str,{cell=1,color,axis='-x',advance=-cell}={}){
    let cx=0;
    for(const ch of str){const g=GLYPH[ch.toUpperCase()];
      if(g){for(let r=0;r<7;r++)for(let c=0;c<5;c++)if(g[r][c]==='1')this.glyph(x,y,z,cx+c,r,color,axis);}
      cx+=6+(ch===' '?2:0);}
  }
  finish(material,opts={}){
    let kept=this.items;
    if(this.occ.size)kept=kept.filter(it=>{
      if(!it.unit)return true;
      for(const n of N6) if(!this.occ.has((it.cx-.5+n[0])+'|'+(it.cy-.5+n[1])+'|'+(it.cz-.5+n[2])))return true;
      return false;});
    this.items=kept;
    const mesh=new THREE.InstancedMesh(geoBox,material,kept.length);
    mesh.castShadow=opts.shadow!==false; mesh.receiveShadow=opts.shadow!==false;
    mesh.frustumCulled=false;
    for(let i=0;i<kept.length;i++){const it=kept[i];
      it.col=it.c instanceof THREE.Color?it.c:C(it.c||0xffffff);
      _p.set(it.cx,it.cy,it.cz);_s.set(it.sx,it.sy,it.sz);_q.identity();
      _m.compose(_p,_q,_s);mesh.setMatrixAt(i,_m);mesh.setColorAt(i,it.col);
      const o=it.o&&it.o.tag&&TAGS.get(it.o.tag);
      if(o){o.cx+=it.cx;o.cy+=it.cy;o.cz+=it.cz;o.n++;
        o.min.min(_p.set(it.cx-.5,it.cy-.5,it.cz-.5));o.max.max(_p.set(it.cx+.5,it.cy+.5,it.cz+.5));}}
    mesh.instanceMatrix.needsUpdate=true;
    if(mesh.instanceColor)mesh.instanceColor.needsUpdate=true;
    this.mesh=mesh; this.count=kept.length;
    return mesh;
  }
}

/* 5×7 glyphs */
const GLYPH={
 H:["10001","10001","10001","11111","10001","10001","10001"],
 A:["01110","10001","10001","11111","10001","10001","10001"],
 R:["11110","10001","10001","11110","10100","10010","10001"],
 B:["11110","10001","10001","11110","10001","10001","11110"],
 O:["01110","10001","10001","10001","10001","10001","01110"],
 U:["10001","10001","10001","10001","10001","10001","01110"],
 "1":["00100","01100","00100","00100","00100","00100","01110"],
 "2":["01110","10001","00001","00010","00100","01000","11111"],
 "3":["11110","00001","00010","01110","00001","00001","11111"],
 "6":["00110","01000","10000","11110","10001","10001","01110"],
 "9":["01110","10001","10001","01111","00001","00010","01100"]
};

/* ══════════════════════════════════════ scene ══════════════════════════════════════ */
const cv=document.getElementById('c');
const renderer=new THREE.WebGLRenderer({canvas:cv,antialias:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,1.75));
renderer.setSize(innerWidth,innerHeight);
renderer.shadowMap.enabled=true; renderer.shadowMap.type=THREE.PCFSoftShadowMap;
renderer.toneMapping=THREE.ACESFilmicToneMapping; renderer.toneMappingExposure=1.05;
renderer.outputColorSpace=THREE.SRGBColorSpace;

const scene=new THREE.Scene();
scene.fog=new THREE.Fog(0x8f7f88,60,255);
const camera=new THREE.PerspectiveCamera(42,innerWidth/innerHeight,.5,1600);
camera.position.set(-70,28,70);
const controls=new OrbitControls(camera,cv);
controls.enableDamping=true; controls.dampingFactor=.055;
controls.target.set(-10,11,12);
controls.minDistance=18; controls.maxDistance=250; controls.maxPolarAngle=1.47;
controls.autoRotateSpeed=.22;

const sun=new THREE.DirectionalLight(0xffd0a0,1.7);
sun.castShadow=true; sun.shadow.mapSize.set(2048,2048);
const sc=sun.shadow.camera; sc.left=-96;sc.right=96;sc.top=96;sc.bottom=-96;sc.near=1;sc.far=340;
sun.shadow.bias=-0.0006; sun.shadow.normalBias=.45; sun.shadow.radius=1.2;
scene.add(sun,sun.target);
const hemi=new THREE.HemisphereLight(0x8f7f88,0x3f3b34,.75); scene.add(hemi);
scene.add(new THREE.AmbientLight(0xffffff,.06));
const lamps=[new THREE.PointLight(0xffc170,0,38,2),new THREE.PointLight(0xffc170,0,32,2),
             new THREE.PointLight(0xffe0a0,0,44,2),new THREE.PointLight(0xffc170,0,26,2)];
lamps.forEach((l,i)=>scene.add(l));
const lampSlots=[[17,11,0],[17,11,24],[ -32,55,-40],[-6,8,28]];
lamps.forEach((l,i)=>l.position.set(...lampSlots[i]));

/* sky dome */
const skyCv=document.createElement('canvas'); skyCv.width=9; skyCv.height=34;
const skyTex=new THREE.CanvasTexture(skyCv);
skyTex.magFilter=THREE.NearestFilter; skyTex.minFilter=THREE.NearestFilter; skyTex.generateMipmaps=false;
skyTex.colorSpace=THREE.SRGBColorSpace;
const sky=new THREE.Mesh(new THREE.SphereGeometry(520,10,18),
  new THREE.MeshBasicMaterial({map:skyTex,side:THREE.BackSide,fog:false,depthWrite:false}));
sky.renderOrder=-2; scene.add(sky);

/* ══════════════════════════════════════ time of day ══════════════════════════════════════ */
const TIMES={
 dawn:{label:'dawn',sky:['#111a2e','#26304b','#4d4a6a','#866a71','#c98d67','#efbc86','#f8d9a8'],
   az:147,el:8,sun:'#ffb477',suni:1.35,hs:'#7183a8',hg:'#3b3834',hi:.42,
   fog:'#7c8096',near:55,far:245,exp:1.04,lit:.8,stars:.22,sea:['#132437','#20465f','#316e79','#a6c6cf'],seai:.5,clock:'05:12'},
 noon:{label:'noon',sky:['#2a5f95','#3f79a8','#5e93ba','#8cb4ce','#b8d1de','#d5e2e6','#e6ece9'],
   az:100,el:62,sun:'#fff3df',suni:2.15,hs:'#9dc0da',hg:'#6f6a5c',hi:.72,
   fog:'#a8bfc9',near:80,far:290,exp:1.0,lit:0,stars:0,sea:['#0d4a63','#1a7a8c','#34a0a4','#eaf6f3'],seai:.62,clock:'12:00'},
 golden:{label:'golden',sky:['#243252','#3f4a6d','#6e5f76','#a56f63','#d68d54','#efb371','#f8d9a0'],
   az:147,el:14,sun:'#ffcb8c',suni:1.9,hs:'#8f7f88',hg:'#4a4238',hi:.7,
   fog:'#8f7f88',near:60,far:255,exp:1.05,lit:.18,stars:0,sea:['#123146','#1c5e74','#2f8b93','#cfe6df'],seai:.58,clock:'17:42'},
 night:{label:'night',sky:['#03060f','#060c1b','#0a1428','#102133','#173043','#22424f','#2e4f57'],
   az:120,el:-6,sun:'#4b6a86',suni:.06,hs:'#182634',hg:'#0a0f14',hi:.3,
   fog:'#0a141d',near:34,far:205,exp:1.2,lit:1,stars:1,sea:['#040f18','#072230','#0b3b46','#7fb7c2'],seai:.34,clock:'21:30'}
};
const P={sky:[],sun:C('#fff'),hs:C('#000'),hg:C('#000'),fog:C('#000'),sea:[C('#000'),C('#000'),C('#000'),C('#fff')],
  suni:1.7,hi:.7,near:60,far:255,exp:1.05,lit:0,stars:0,seai:.6,az:147,el:14};
for(let i=0;i<7;i++)P.sky.push(C('#000'));
let cur='golden',tw=null;
function skyAt(bands,t){t=cl(t)*(bands.length-1);const i=Math.min(bands.length-2,Math.floor(t));
  return mixc(C(bands[i]),C(bands[i+1]),t-i);}
function setTime(key,animate=true){
  const T=TIMES[key]; cur=key;
  document.querySelectorAll('#pillsTime .pill').forEach(b=>b.classList.toggle('on',b.dataset.k===key));
  const from={sky:P.sky.map(c=>c.clone()),sun:P.sun.clone(),hs:P.hs.clone(),hg:P.hg.clone(),fog:P.fog.clone(),
    sea:P.sea.map(c=>c.clone()),suni:P.suni,hi:P.hi,near:P.near,far:P.far,exp:P.exp,lit:P.lit,stars:P.stars,
    seai:P.seai,az:P.az,el:P.el};
  const to={sky:T.sky.map(h=>C(h)),sun:C(T.sun),hs:C(T.hs),hg:C(T.hg),fog:C(T.fog),
    sea:T.sea.map(h=>C(h)),suni:T.suni,hi:T.hi,near:T.near,far:T.far,exp:T.exp,lit:T.lit,stars:T.stars,
    seai:T.seai,az:T.az,el:T.el};
  tw=animate?{t0:performance.now(),d:1500,from,to}:{t0:0,d:1,from:to,to};
  clockTarget=parseFloat(T.clock.split(':')[0])*60+parseFloat(T.clock.split(':')[1]);
}
function paintSky(){
  const ctx=skyCv.getContext('2d'),W=skyCv.width,H=skyCv.height;
  for(let j=0;j<H;j++){const t=j/(H-1);
    for(let i=0;i<W;i++){const n=((i*7+j*13)%5)-2;
      ctx.fillStyle='#'+P.sky[j===H-1?H-1:j].clone().offsetHSL(0,0,n*.006).getHexString();
      ctx.fillRect(i,j,1,1);}
    ctx.fillStyle='#'+skyAt(P.sky,t).getHexString();
    for(let i=0;i<W;i++){const n=((i*5+j*11)%3)-1;
      const c=skyAt(P.sky,t).offsetHSL(0,0,n*.005);
      ctx.fillStyle='#'+c.getHexString(); ctx.fillRect(i,j,1,1);}}
  skyTex.needsUpdate=true;
}

/* ══════════════════════════════════════ land ══════════════════════════════════════ */
const GRASS='#4f6d3b',GRASS2='#5c7d45',GRAVEL='#7b7163',COBBLE_A='#6b6a60',COBBLE_B='#5f5e55',
  PATH='#877b66',ROLL='#655f54',ROCK='#4c5154',ROCK2='#5b6062';
function isLand(x,z){x=Math.round(x);z=Math.round(z);
  if(x>14)return true;
  if(z<=-35)return x>-46;
  if(x<-12&&z<22&&z>-56)return fbm(x*.07+9,z*.07+3)>.42&&Math.hypot((x+29)/17,(z+40)/19)<1;
  return false;}
const FOOT=[];
function rect(x0,z0,x1,z1){FOOT.push([x0-1,z0-1,x1+2,z1+2]);}
const CRANE_F=[17,11,24,19];
function reserved(x,z){for(const f of FOOT.concat([CRANE_F])) if(x>=f[0]&&x<=f[2]&&z>=f[1]&&z<=f[3])return true;
  return false;}
function groundColor(x,z){
  if(x<19)return ((x*3+z*5)%9<4)?jit(COBBLE_A,.07):jit(COBBLE_B,.07);
  if(z<-14)return ((x+z)%7<3)?jit(GRAVEL,.06):jit(ROLL,.06);
  if(x>42&&z>16)return ((x*2+z)%8<3)?jit(GRASS2,.08):jit(GRASS,.08);
  if(x>38)return jit(PATH,.06);
  return ((x+z)%11<3)?jit(GRASS,.06):jit(GRAVEL,.06);
}
function wallColor(x,z){const n=fbm(x*.11,z*.11);
  return mixc(C('#6a6659'),C('#575349'),n).offsetHSL(0,0,(R()-.5)*.06).getHex();}

const S=3;
function buildLand(vox){
  for(let cx=-46;cx<=64;cx+=2)for(let cz=-72;cz<=48;cz+=2){
    const x=cx+1,z=cz+1; if(!isLand(x,z)||reserved(x,z))continue;
    vox.s(x,4.5,z,2,1,2,groundColor(x,z));
    for(const[dx,dz]of[[1,0],[-1,0],[0,1],[0,-1]]){
      if(!isLand(x+dx*2,z+dz*2)){
        vox.s(x+dx,0,z+dz, dx?2:2.02, 14, dx?2.02:2, wallColor(x,z));
        if(x<19&&dx===-1){ for(let yy=2;yy<=4;yy++) vox.s(x+dx,yy+.5,z+dz*.2,2.02,1,dx?2.02:1.2,jit('#726c5f',.05)); }
      }}}
  /* slipway ramp */
  for(let i=0;i<9;i++)for(let z=38+i;z<46;z++) vox.v(15+i,z,-1+0,0);
  for(let i=0;i<9;i++)for(let z=38;z<46;z++) vox.v(15+i,5-i*1,z,'#7c5a34');
  /* quay lamp bases, bollards & misc ground detail */
  for(let z=-28;z<=44;z+=6){vox.v(16,5,z,jit('#585549',.05));vox.v(16,6,z,jit('#6b6759',.05));vox.v(16,7,z,jit('#5c594e',.05));}
  /* scattered cobbles + grass tufts */
  for(let i=0;i<140;i++){const x=19+R()*42,z=-30+R()*76;
    if(isLand(x,z)&&!reserved(x,z)&&R()<.5)vox.s(x,5.15,z,1.6,.3,1.6,R()>.4?jit('#3f5c31',.1):jit('#5a5245',.06));}
}

/* ══════════════════════════════════════ buildings ══════════════════════════════════════ */
function roof(vox,x,z,w,d,pitch,c,tg){
  for(let s=0;s<=pitch;s++){
    const y=5+ (tg.h) + s, z0=z+s-1, dd=d+2-2*s;
    vox.box(x,y,z0,w,1,dd,(px,py,pz)=>{
      const edge=(pz===z0||pz===z0+dd-1); return edge?jit('#8a6c46',.06):jit(c,.09);},{tag:tg.k});
    if(s===pitch-1)vox.box(x,y+1,z0+1,w,1,dd-2,jit('#7b5f3d',.05),{tag:tg.k});
  }
}
function windows(vox,glow,x,y,z,n,axis,dir,tg){
  const gap=4;
  for(let i=0;i<n;i++){
    const off=i-(n-1)/2; let px,py,pz;
    if(axis==='x'){px=x+dir;py=y;pz=z+off*gap;}
    else if(axis==='z'){px=x+off*gap;py=y;pz=z+dir;}
    else {px=x+off*gap;py=y;pz=z+dir;}
    if(axis==='x')vox.box(px,py-1,pz-1,1,3,1,'#2b2620',{tag:tg.k});
    else if(axis==='z')vox.box(px-1,py-1,pz,1,3,1,'#2b2620',{tag:tg.k});
    else vox.box(px-1,py-1,pz,3,3,1,'#2b2620',{tag:tg.k});
    const g=glow.box(axis==='x'?px+dir:px-1,py, axis==='z'?pz+dir:pz,1,1,1,
      C('#ffcf8a').offsetHSL(0,0,(R()-.5)*.12));
    g.o={};}
}
function chimney(vox,x,z,h,tg){
  vox.box(x,5,h,z,2,2,(px,py,pz)=>jit(py%3===0?'#3a332c':'#6b4a3a',.06),{tag:tg.k});
  vox.box(x-1,5+h,z-1,4,1,4,jit('#7a5f4a',.05),{tag:tg.k});
  return {x:x+1,y:5+h+1,z:z+1};
}
function gableWall(vox,x0,z0,d,h,c,tg){
  for(let j=0;j<Math.ceil(d/2);j++)vox.v(x0,5+h+1+j,z0+j,mixc(C(c),C('#efe2c4'),.08).offsetHSL(0,0,(R()-.5)*.06).getHex(),{tag:tg.k});
}

function buildTown(vox,glow){
  /* — Harbour Master's Office — */
  const HO=tag("Harbour Master's Office","Customs, duties and clearance papers. This house has kept the port's books since 1847.");
  rect(26,4,52,26);
  const stone=(x,y,z,j)=>{
    if(j<.1)return shade('#8a6f4a',.9); if(j>.92)return shade('#b79b6f',1.02);
    return jit((x+z)%3? '#a08558':'#96794f',.06);};
  vox.box(26,5,4,26,16,22,stone,{tag:HO.k});
  vox.box(26,5+8,3,26,1,24,jit('#c3ad84',.05),{tag:HO.k});
  vox.box(25,20,3,28,2,24,jit('#cbb790',.05),{tag:HO.k});
  vox.box(24,22,5,4,1,20,jit('#b5a177',.05),{tag:HO.k});
  for(let z=6;z<24;z+=3)vox.box(26,5,4+z,1,1,1,jit('#8b7150',.05),{tag:HO.k});
  /* colonnade + pediment */
  for(let z=8;z<22;z+=4){vox.box(26,5,z,2,14,2,jit('#d6c9a8',.05),{tag:HO.k});
    vox.box(25,19,z-1,3,2,4,jit('#e3d7b8',.04),{tag:HO.k});}
  for(let z=6;z<24;z++)for(let s=0;s<Math.min(6,24-z);s++)
    vox.v(26,22+ (6-s),6+z+s, jit('#d8cdae',.05),{tag:HO.k});
  vox.box(25,21,11,2,4,10,jit('#3d4b4a',.06),{tag:HO.k});
  vox.text(24,23,8,'HARBOUR',{color:'#e8dcb8',axis:'x'});
  windows(glow,glow,25,11,8,4,'x',-1,HO); windows(glow,glow,25,16,8,4,'x',-1,HO);
  windows(glow,glow,32,11,26,5,'z',1,HO);  windows(glow,glow,46,16,-2,6,'z',-1,HO);
  vox.box(26,5,12,3,1,8,jit('#8a7a5c',.05),{tag:HO.k});
  vox.box(27,6,13,2,1,6,jit('#7c6c50',.05),{tag:HO.k});
  const chim=[chimney(vox,30,36,20,HO),chimney(vox,44,6,20,HO)];
  /* flagpole */
  vox.s(39,32,14,.4,14,.4,'#8d8574',{tag:HO.k});
  /* statue of an anchor on a plinth */
  vox.box(23,5,28,3,3,3,jit('#7d7a6d',.05),{tag:HO.k});
  vox.s(24.5,10,29.5,.6,4,.6,'#4c5158',{tag:HO.k});
  vox.s(24.5,8.4,31.4,4.2,.6,.6,'#4c5158',{tag:HO.k});

  /* — Chandlery / warehouse — */
  const CH=tag("Chandlery Store","Tar, hemp, tallow, rope by the fathom. The crews buy water here and leave their laundry.");
  rect(18,-30,32,-16);
  vox.box(18,5,-30,14,13,14,(x,y,z,j)=>{
    if(j<.12)return shade('#6b4a2f',.85);
    return jit((y%3===0)?'#7c5636':'#8a6239',.07);},{tag:CH.k});
  vox.box(17,17,-31,16,1,16,jit('#5c4227',.05),{tag:CH.k});
  roof(vox,18,-30,14,14,4,'#7a4231',CH);
  vox.box(17,5,-26,1,9,6,'#171412',{tag:CH.k});
  glow.v(18,9,-23,jit('#ffcf8a',.1));
  vox.box(16,5,-26,2,1,6,jit('#a08055',.05),{tag:CH.k});
  for(let i=0;i<5;i++)vox.box(15,5,-29+i*2,2,2+i%3,2,i%2?jit('#8a6239',.08):jit('#6b4a2f',.08),{tag:CH.k});
  windows(glow,glow,17,13,-19,3,'x',-1,CH); windows(glow,glow,25,13,-16,3,'z',-1,CH);
  const chim2=chimney(vox,27,-26,18,CH);

  /* — Clock tower — */
  const CT=tag("Clock Tower & Beacon","The town's clock, the harbour's beacon, and the bell that rings the tide in.");
  rect(44,-34,52,-26);
  vox.box(44,5,-34,8,26,8,(x,y,z,j)=>{
    if(j>.86)return shade('#b39b74',1.0);
    if(y%6===0)return jit('#a8926e',.05);
    return jit((x+z)%4?'#8f7a55':'#85704e',.06);},{tag:CT.k});
  vox.box(43,31,-35,10,3,10,jit('#c0ab84',.05),{tag:CT.k});
  vox.box(45,34,-33,6,4,6,jit('#4b5a5e',.06),{tag:CT.k});
  glow.box(45,35,-33,6,2,6,'#ffe9b8');
  vox.s(48,41,-30,1.4,4,1.4,'#3f4a4f',{tag:CT.k});
  vox.box(44,57,-34,8,1,8,jit('#7f6a4f',.05),{tag:CT.k});
  vox.s(28,36,-29.7,5,5,.5,'#c9bfa2',{tag:CT.k});   /* clock face */
  vox.s(28,36,-29.8,4.2,4.2,.3,'#1a1712');
  vox.text(27,34,-28,'12',{color:'#c9bfa2',axis:'x'});
  /* — Sail loft — */
  const SL=tag("Sail Loft","Canvas, ropewalk and one very patient stitcher. Sails are cut here to the ton.");
  rect(34,-12,46,-2);
  vox.box(34,5,-12,12,9,10,(x,y,z,j)=>jit(y%4===0?'#8a6239':'#96714a',.07),{tag:SL.k});
  roof(vox,34,-12,12,10,3,'#6f5335',SL);
  vox.box(33,5,-9,1,7,5,'#171412',{tag:SL.k});
  for(let i=0;i<3;i++)vox.s(34.5,9.5-i,-7,0.6,3+i*1.2,3.4,jit('#e6dcc2',.08),{tag:SL.k});

  /* — Cottages — */
  const CO=tag("Cottag Row","Nine households, a green door, and a goat that has never once been asked to leave.");
  const h1=rect(40,30,50,40)||tag; /* keep order */
  const cots=[[40,30,10,10,10,'#b9a179'],[50,24,10,10,9,'#a89070'],[38,40,10,8,11,'#c0a982']];
  const chimCots=[];
  cots.forEach((c,i)=>{
    const COt=tag("Cottag Row","Nine households, a green door, and a goat that has never once been asked to leave.");
    rect(c[0],c[1],c[0]+c[2],c[1]+c[3]);
    vox.box(c[0],5,c[1],c[2],c[4],c[3],(x,y,z,j)=>j<.14?shade('#6d6250',.85):jit(c[5],.07),{tag:COt.k});
    roof(vox,c[0],c[1],c[2],c[3],3,i===1?'#4c5560':'#8c4c38',COt);
    windows(glow,glow,c[0],9,c[1]+2,2,'x',-1,COt);
    windows(glow,glow,c[0]+1,c[1],c[1]+c[3]+1,2,'z',1,COt);
    vox.box(c[0]+c[2]-1,5,c[1]+Math.round(c[3]/2),1,4,2,'#3b3a33',{tag:COt.k});
    chimCots.push(chimney(vox,c[0]+1,c[1]+1,5+c[4],COt));
  });

  /* — lamp posts — */
  for(let z=-24;z<=42;z+=11){
    vox.s(17.6,8,z,.35,6,.35,'#3d4348');
    vox.s(17.6,11.6,z,1.4,.4,1.4,'#3d4348');
    glow.s(17.6,11,z,1.1,1.2,1.1,C('#ffd391'));
    vox.s(17.6,12,z,1.5,.3,1.5,'#3d4348');
  }
  /* — trees, hedges, market — */
  const pine=(x,z,h)=>{const t=tag("Town Green","A yard of grass, two pines, and the only place in port where nothing is weighed or taxed.");
    for(let i=0;i<h;i++)vox.v(x,5+i,z,'#5a432c',{tag:t.k});
    const r=1;
    for(let l=0;l<4;l++){const y=5+h-2-l, rad=l%2?2:3;
      for(let dx=-rad;dx<=rad;dx++)for(let dz=-rad;dz<=rad;dz++)
        if(Math.abs(dx)+Math.abs(dz)<=rad+1)
          vox.v(x+dx,y,z+dz,jit(l%2?GRASS2:'#3f5c31',.1),{tag:t.k});}}
  pine(46,44,7);pine(56,42,6);pine(54,14,8);pine(41,15,5);
  for(let i=0;i<9;i++)vox.s(35+i*1.6,6.2,15,1.4,1.6,1.4,jit('#44603a',.1));
  const MK=tag("Market Stalls","Produce, rope-mendings and eel pie. Open from the bell to the second tide.");
  for(let i=0;i<3;i++){const z0=32+i*5;
    for(let k=0;k<2;k++){vox.v(26+k*6,5,z0,'#6b4a2f',{tag:MK.k});vox.v(26+k*6,6,z0,'#6b4a2f',{tag:MK.k});}
    vox.box(25,7,z0-1,8,1,4,i%2?jit('#d8cdae',.05):jit('#a33f34',.05),{tag:MK.k});
    for(let c=0;c<3;c++)for(let q=0;q<2;q++)vox.v(26+c*2,7.2,z0+q,[jit('#c76b3a',.1),jit('#7f9e3c',.1),jit('#b8443a',.1)][(c+q+i)%3],{tag:MK.k});}
  return {chim:[...chim,...[chim2],...chimCots]};
}

/* — lighthouse on the rock — */
function buildLight(vox,glow){
  const LT=tag("Meridian Light","Thirty-four metres of granite on a rock. One white flash, twelve seconds dark, one red.");
  const cx=-30,cz=-40;
  for(let x=cx-15;x<=cx+15;x++)for(let z=cz-14;z<=cz+14;z++)for(let y=1;y<11;y++){
    const e=Math.hypot((x+cx*0)/1,0)/1;
    const d=Math.hypot((x-cx)/13,(z-cz)/14)*1.0+(y-3)*.11;
    if(d<1.1+fbm(x*.16+4,z*.16+7)*.5){
      const n=fbm(x*.2,z*.2);
      vox.v(x,y,z,jit(y>7||n>.62?ROCK2:ROCK,.09));}}
  /* tower */
  for(let y=9;y<41;y++){
    const r=lerp(4.4,2.2,(y-9)/32);
    const band=Math.floor((y-9)/4)%2===0;
    for(let x=Math.floor(cx-r-1);x<=cx+r+1;x++)for(let z=Math.floor(cz-r-1);z<=cz+r+1;z++){
      const d=Math.hypot(x-cx,z-cz);
      if(d<r+.4&&d>r-1.3) vox.v(x,y,z,jit(band?'#e4dcc9':'#a8423a',.05));}
    if(y%7===2)for(let a=0;a<6;a++)glow.v(cx+Math.round(Math.cos(a)*r),y,cz+Math.round(Math.sin(a)*r),'#ffd9a0');
  }
  vox.box(cx-4,41,cz-4,9,1,9,jit('#3c4448',.05));
  glow.box(cx-3,42,cz-3,7,4,7,'#fff0c4');
  vox.box(cx-3,46,cz-3,7,1,7,jit('#4a5256',.05));
  for(let x=-3;x<=3;x++)for(let z=-3;z<=3;z++)if(Math.hypot(x,z)<3.2)vox.v(cx+x,47,cz+z,jit('#a8423a',.06));
  vox.s(cx,51,cz,.5,5,.5,'#3c4448'); vox.s(cx,54,cz,1.2,1.2,1.2,'#e4b05a');
  /* keeper's cottage */
  vox.box(cx-10,6,cz-2,6,5,6,(x,y,z)=>jit('#b09a78',.07));
  vox.box(cx-11,11,cz-3,8,1,8,jit('#5c4227',.05));
  glow.v(cx-10,9,cz-1,'#ffcf8a');
  const ch=chimneyLite(cx-7,cz+3,11);
  return {x:cx-7,y:ch,z:cz+3};
}
function chimneyLite(x,y){for(let i=0;i<3;i++)voxStone(x,y+i,zStone);return y+3;}
let zStone=0;
function voxStone(x,y,z){}

/* ══════════════════════════════════════ crane ══════════════════════════════════════ */
const craneMat=new THREE.MeshLambertMaterial({color:'#8a6239'});
const darkMat=new THREE.MeshLambertMaterial({color:'#3b3630'});
const crateMat=new THREE.MeshLambertMaterial({color:'#a3814e'});
const crane=new THREE.Group(); crane.position.set(20,5,14); scene.add(crane);
(function(){
  const legM=new THREE.MeshLambertMaterial({color:'#7c5636'});
  [[-1.5,-1.5],[1.5,-1.5],[-1.5,1.5],[1.5,1.5]].forEach(([a,b])=>{
    const m=new THREE.Mesh(geoBox,legM); m.scale.set(1,13,1); m.position.set(a,6.5,b);
    m.rotation.x=b*.04; m.rotation.z=-a*.04; m.castShadow=true; crane.add(m);});
  const beam=new THREE.Mesh(geoBox,legM); beam.scale.set(5,.9,3.6); beam.position.y=13; beam.castShadow=true; crane.add(beam);
  const jib=new THREE.Mesh(geoBox,new THREE.MeshLambertMaterial({color:'#8a6239'}));
  jib.scale.set(16,.9,.9); jib.position.set(6,15,0); jib.rotation.z=-.14; jib.castShadow=true; crane.add(jib);
  const cw=new THREE.Mesh(geoBox,darkMat); cw.scale.set(3,2.4,2.4); cw.position.set(-4.5,13,0); cw.castShadow=true; crane.add(cw);
  const pul=new THREE.Mesh(geoBox,new THREE.MeshLambertMaterial({color:'#e0d3b0'})); pul.scale.set(.8,.8,1.2); pul.position.set(13,13.4,0); crane.add(pul);
})();
const load=new THREE.Group(); crane.add(load);
(function(){
  const rope=new THREE.Mesh(geoBox,new THREE.MeshLambertMaterial({color:'#4c4034'}));
  rope.scale.set(.22,7.2,.22); rope.position.set(0,3.6,0); load.add(rope);
  const crate=new THREE.Mesh(geoBox,new THREE.MeshLambertMaterial({color:'#9b7a48'}));
  crate.scale.set(2.6,2.6,2.6); crate.position.y=-1; crate.castShadow=true; load.add(crate);
  for(const s of[-1,1]){const b=new THREE.Mesh(geoBox,new THREE.MeshLambertMaterial({color:'#5e4830'}));
    b.scale.set(2.72,.4,2.72); b.position.set(0,-.5+s*1.0,0); load.add(b);}
  load.position.set(13,9.4,0);
})();

/* ══════════════════════════════════════ figures ══════════════════════════════════════ */
function makePerson(skin,shirt,breeches,cap){
  const g=new THREE.Group(); const mk=(w,h,d,c)=>{const m=new THREE.Mesh(geoBox,new THREE.MeshLambertMaterial({color:c}));
    m.scale.set(w,h,d); m.castShadow=true; g.add(m); return m;};
  const head=mk(.55,.55,.55,skin); head.position.y=1.9;
  const hat=mk(.66,.2,.66,cap); hat.position.y=2.25;
  const body=mk(.8,.9,.5,shirt); body.position.y=1.2;
  const la=mk(.26,.9,.26,breeches); la.position.set(-.2,.45,0);
  const ra=mk(.26,.9,.26,breeches); ra.position.set(.2,.45,0);
  const lar=mk(.2,.75,.2,shirt); lar.position.set(-.55,1.3,0);
  const rar=mk(.2,.75,.2,shirt); rar.position.set(.55,1.3,0);
  g.userData={la,ra,lar,rar,head,body};
  return g;
}
const WALKERS=[];
function walker(a,b,speed,clothes,phase){
  const p=makePerson(...clothes); p.position.set(a.x,5,a.z); scene.add(p);
  WALKERS.push({o:p,a,b,sp:speed,ph:phase}); return p;}
const skins=['#c8a179','#a8805c','#d8b48c'];
walker({x:18,z:-8},{x:18,z:40},1.3,[skins[0],'#8a4236','#3f4650','#25313a'],0);
walker({x:22,z:36},{x:22,z:-6},1.0,[skins[1],'#4b5f6e','#5a432c','#2a2f33'],.4);
walker({x:26,z:-20},{x:26,z:22},1.5,[skins[2],'#c4a374','#4a4a4a','#8a7a55'],.7);
walker({x:31,z:28},{x:21,z:28},1.1,[skins[0],'#2f4252','#8a7a55','#a33f34'],.15);
walker({x:35,z:34},{x:35,z:44},.9,[skins[1],'#7d6a4a','#3f4650','#e0d3b0'],.55);

/* ══════════════════════════════════════ the ship ══════════════════════════════════════ */
const ship=new THREE.Group();
ship.position.set(-14,0,12); ship.rotation.y=-0.925; scene.add(ship);
const shipSet=new VoxelSet();
const dyn=[];                      /* animated sail/flag/rope items */
const SHIP={L:46,bow:24,stern:-22,masts:[{x:7,h:31,fc:13,yc:10,ys:[10,17.5,24]},
  {x:-3,h:36,fc:14,yc:11.5,ys:[11.5,19,26.5,32]},{x:-14,h:26,fc:11,yc:9,ys:[9,15]}]};

function hb(x,y){
  const t=(x+22)/46;
  let hb0;
  if(x<=-21)hb0=3.6;
  else if(x<0)hb0=3.6+4.7*Math.sqrt((x+21)/21)*(1-.09*(x/21)*(x/21));
  else{const u=(x-0)/24;hb0=8.3*Math.pow(1-u,1.08)*(1-u*u*.10);}
  hb0=Math.max(0,hb0-0.02*Math.max(0,x));
  if(hb0<=0.35)return 0;
  const ky=lerp(lerp(-7.4,-2.4,Math.pow(Math.abs(x+1)/23,1.3)),lerp(-7.4,-1,Math.pow(cl((x-1)/23,0,1),1.2)),cl((x+1)/24,0,1));
  let vy;
  if(y<ky)return 0;
  if(y<0)vy=Math.sqrt(cl((y-ky)/Math.max(.1,-ky),0,1));
  else vy=1-.14*cl(y/6,0,1);
  return hb0*vy;
}
function deckY(x){
  const t=cl((x+22)/46,0,1);
  return 4.7+1.5*Math.pow(Math.max(0,t-.45)/.55,1.25)+1.2*Math.pow(Math.max(0,.45-t)/.45,1.5);
}
function hull(){
  const DARK='#241b13',OAK='#3a2a1c',MAH='#513a24',OCH='#a58040',CREAM='#dbcaa2',RUB='#4a2222';
  for(let x=SHIP.stern;x<=SHIP.bow;x++){
    if(hb(x,-5.9)<=0)continue;
    const top=Math.floor(deckY(x));
    for(let y=-6;y<=top;y++){
      const h=hb(x,y); if(h<=0)continue;
      let c = y<-4?DARK : y<-1.5?OAK : y<0?mixc(C(OAK),C(RUB),cl((y+1.5)/1.5)) :
              y===0?OCH : y===1?MAH : y===2?MAH : y===3?mixc(C(OAK),C(CREAM),.5) : y===4?CREAM : y===5?OCH : CREAM;
      if(y>=-1&&y<=1&&R()<.07)c=jit('#243030',.05);           /* algae */
      if(y>1&&y<6&&x%4===0)  c=shade(CREAM,.92);              /* metal band */
      if(y>1&&R()<.04)c=shade(c,1.18);
      for(let z=Math.ceil(-h);z<=Math.floor(h);z++){
        const edge=Math.abs(z)>h-.5;
        shipSet.v(x,y,z,jit(c,edge?.07:.03));
      }
    }
  }
  /* wales (slim, painted) */
  const wl=new THREE.MeshLambertMaterial({color:'#b89050'});
  for(const yy of[0,3.4]){
    for(let x=SHIP.stern+1;x<SHIP.bow;x++){const h=hb(x,yy); if(h<=0)continue;
      for(const s of[-1,1]) shipSet.s(x+.5,yy+.5,s*(h+.1),1.05,1.0,.42,jit('#c9a45f',.04));}
  }
  /* gun ports */
  for(let x=-16;x<16;x+=6)for(const s of[-1,1]){
    if(hb(x,1)<=0)continue;
    shipSet.box(x,0,Math.round(s*hb(x,1))-0,1,2,Math.sign(s),0x080808);
    shipSet.s(x+.5,1,s*(hb(x,1)+.35),1,1,.7,'#3b4046');}
  /* bulwarks & rails */
  for(let x=SHIP.stern;x<SHIP.bow;x++){
    const dy=deckY(x),h=hb(x,dy); if(h<=0)continue;
    for(const s of[-1,1]){
      shipSet.v(Math.round(x),dy+1,Math.round(s*h),jit('#513a24',.05));
      if(x%3!==0)shipSet.v(Math.round(x),dy+2,Math.round(s*h),jit(CREAM,.04));}}
  /* decks */
  for(let x=SHIP.stern;x<SHIP.bow;x++){
    const dy=deckY(x),h=hb(x,dy-1); if(h<=0)continue;
    for(let z=-Math.floor(h);z<=Math.floor(h);z++)
      shipSet.v(x,Math.floor(dy),z,jit((x+z)%2?'#9a7648':'#8d6c41',.05));}
  /* forecastle & quarterdeck */
  shipSet.box(9,6,Math.round(-4),10,2,8,(x,y,z)=>jit((x+z)%2?'#9a7648':'#8d6c41',.05));
  shipSet.box(SHIP.stern,6,Math.round(-3),9,2,6,jit('#8d6c41',.05));
  shipSet.box(4,8,-4,2,2,8,jit('#3a2a1c',.05));   /* breakwater */
  /* companion hatches with light */
  for(const hx of[11,2,-9])shipSet.box(hx,7,-3,2,1,6,'#4a3621'), glowShip.box(hx,7,-2,2,.6,4,'#ffd391');
  /* stern gallery */
  shipSet.box(SHIP.stern,8,Math.round(-3),2,2,6,jit(CREAM,.04));
  for(let z=-2;z<=2;z+=2) glowShip.v(SHIP.stern,9,z,'#ffd9a0');
  /* railings */
  for(let x=SHIP.stern+2;x<SHIP.bow-2;x+=2){
    for(const s of[-1,1]){const h=hb(x,deckY(x)); if(h<=1)continue;
      shipSet.v(x,deckY(x)+3,Math.round(s*(h-1)),'#3b3129');}}
  /* bowsprit */
  shipSet.line(new THREE.Vector3(22,6.5,0),new THREE.Vector3(35,12.5,0), '#5a432c',1.5);
  shipSet.line(new THREE.Vector3(33,12,0),new THREE.Vector3(37,13.5,0), '#8d6c41',1.0);
  /* jibs */
  quad(22,7.4,0, 34.5,12.4,0, 34.5,6.6,0, 24,4.5,0,{billow:-2.6,k:'jib',col:'#e9e0c8',steps:[12,7]});
  quad(7,21.5,0, 26,11,0, 31,7.6,0, 7,14,0,{billow:-2.9,k:'jib2',col:'#efe6d0',steps:[13,8]});
  /* figurehead */
  shipSet.line(new THREE.Vector3(23.2,3,0),new THREE.Vector3(24.6,1.6,0), '#e8dcb8',1.2);
  shipSet.v(24,1,0,jit('#e8dcb8',.05)); shipSet.v(25,0,0,jit('#c9a45f',.05));
  /* masts, yards */
  for(const m of SHIP.masts){
    for(let y=3;y<m.h;y++)shipSet.v(m.x,y,0,jit(y<12?'#4a3621':'#6b4a2f',.04));
    shipSet.v(m.x,m.h,0,'#3f3a2f');
    m.ys.forEach((y,i)=>{
      const sp=Math.max(3,Math.round(m.fc*(1-(i+1)/m.ys.length)));
      shipSet.line(new THREE.Vector3(m.x,y,-sp),new THREE.Vector3(m.x,y,sp), i? '#8d6c41':'#5a432c', 1.1);
      if(i<m.ys.length-1)shipSet.line(new THREE.Vector3(m.x,y+.5,0),new THREE.Vector3(m.x,m.ys[i+1]-1,0),'#6b4a2f',1);
      const drop=(i?1.5:2.8)+sp*.16;
      quad(m.x,y+.7,-sp, m.x,y+.7,sp, m.x,y+drop,sp*.88, m.x,y+drop,-sp*.88,
        {billow:3.1+sp*.06,k:'sq'+i,col:i===0?'#e9e0c8':'#efe6d0',steps:[2*sp+1,i?5:6],stripe:i===0});});
    /* tops */
    shipSet.box(m.x-2,12.5,-2.5,4,1,5,jit('#5a432c',.05));
    shipSet.line(new THREE.Vector3(m.x,12.8,-2.5),new THREE.Vector3(m.x,14,-4),'#4a4034',.5);
  }
  /* spanker */
  quad(-14,20,-.5, -14,20,6.5, -21.5,8,-.5, -21.5,8,5.5,{billow:-2.4,k:'sp',col:'#8a6f52',steps:[7,6]});
  shipSet.line(new THREE.Vector3(-14,20,0),new THREE.Vector3(-14,6,-6.5),'#3f3a2f',1);
  /* shrouds, stays, ratlines */
  for(const m of SHIP.masts){
    for(const s of[-1,1]){
      const top=m.h-6, foot=m.x;
      shipSet.line(new THREE.Vector3(foot,3.5,s*7.2),new THREE.Vector3(m.x,top,s*1),'#3f3a2f',.42);
      shipSet.line(new THREE.Vector3(foot-2,3.5,s*7),new THREE.Vector3(m.x,top-2,s*1),'#3f3a2f',.4);
      for(let y=4;y<top;y+=1.4){const t=(y-4)/(top-4);
        shipSet.s(lerp(foot,m.x,t),y,lerp(s*7,s*1,t),.3,.25,.3,'#4a4034');}}
    shipSet.line(new THREE.Vector3(m.x,m.h,0),new THREE.Vector3(m.x-4,4.5,3),'#3f3a2f',.36);
  }
  shipSet.line(new THREE.Vector3(7,24,0),new THREE.Vector3(30,11.5,0),'#4a4034',.42);
  shipSet.line(new THREE.Vector3(7,22,0),new THREE.Vector3(24,6.5,0),'#4a4034',.34);
  shipSet.line(new THREE.Vector3(-3,30,0),new THREE.Vector3(7,15,0),'#4a4034',.4);
  shipSet.line(new THREE.Vector3(-14,22,0),new THREE.Vector3(-3,13,0),'#4a4034',.36);
  /* deck cargo + crew */
  for(let i=0;i<7;i++)shipSet.box(8+Math.round(R()*6),7,-4+Math.round(R()*8),1+Math.round(R()*2),2,1+Math.round(R()*2),jit('#8d6c41',.08));
  for(let i=0;i<5;i++)shipSet.box(-19+Math.round(R()*4),7,-3+Math.round(R()*6),2,2,2,jit('#6b4a2f',.08));
  const crew=[];
  for(let i=0;i<2;i++){const p=makePerson(skins[i%3],i?'#b8b4a8':'#3f4a58',i?'#4a4a4a':'#8a7a55','#25313a');
    p.position.set(6+i*6,7,i?2:-3); p.scale.setScalar(.8); ship.add(p); crew.push({o:p,ph:i*.7,deck:true,sp:.7});}
  WALKERS.push(...crew);
  /* lanterns */
  glowShip.s(23.5,7.2,2.2,.9,.9,.9,'#ffd9a0'); glowShip.s(23.5,7.2,-2.2,.9,.9,.9,'#ffd9a0');
  glowShip.s(-16,11,0,1,1.4,1,'#ffcf8a');
  /* ensign */
  const ens=tag("The Ensign","House colours: cream, a blue line, a gold disc. Read as 'no contraband aboard'.");
  const fl=quad(-14,25,-.5,-14,25,9,-14,20,-.5,-14,20,9,{billow:0,k:'flag',col:'#efe6d0',steps:[10,6],wave:1});
  /* pennants */
  SHIP.masts.forEach((m,i)=>quad(m.x,m.h,0,m.x,m.h,6-i,m.x,m.h-2.2,0,m.x,m.h-2.2,6-i,{billow:0,k:'pn',col:i?'#c76b3a':'#3f5c8a',steps:[7,3],wave:1.4}));
  return crew;
}
/* a billowing quad of voxels → pushed into dyn[] */
function quad(ax,ay,az,bx,by,bz,cx,cy,cz,dx,dy,dz,o){
  const A=new THREE.Vector3(ax,ay,az),B=new THREE.Vector3(bx,by,bz),Cp=new THREE.Vector3(cx,cy,cz),D=new THREE.Vector3(dx,dy,dz);
  const n=new THREE.Vector3().subVectors(B,A).cross(new THREE.Vector3().subVectors(D,A)).normalize();
  const uS=o.steps[0],vS=o.steps[1];
  for(let i=0;i<uS;i++)for(let j=0;j<vS;j++){
    const u=i/(uS-1||1),v=j/(vS-1||1);
    const col=o.stripe&&j===Math.floor(vS/2)?'#3f5c8a':o.col;
    dyn.push({A,B,C:Cp,D,n,u,v,billow:o.billow||0,k:o.k,ph:R()*6.28,wave:o.wave||0,
      col:C(col).offsetHSL(0,0,(R()-.5)*.06),ship:1});
  }
}
const glowShip=new VoxelSet();
const crew0=hull();

/* mooring ropes (animated, world space) */
const moor=[
  {from:{x:22,y:6.5,z:2.5}, to:new THREE.Vector3(16,7.5,20)},
  {from:{x:22,y:6.5,z:-2.5},to:new THREE.Vector3(16,7.5,28)}];
for(const r of moor)for(let i=0;i<22;i++)dyn.push({rope:r,i,f:i/21,col:C('#4c4034')});

/* ══════════════════════════════════════ sea ══════════════════════════════════════ */
const seaSet=new VoxelSet(), seaCols=[];
for(let x=-70.5;x<=70.5;x+=S)for(let z=-70.5;z<=70.5;z+=S){
  if(isLand(x,z))continue;
  let sh=0;
  for(const[dx,dz]of[[3,0],[-3,0],[0,3],[0,-3],[6,0],[-6,0],[0,6],[0,-6]]) if(isLand(x+dx,z+dz))sh+=.17;
  const c={x,z,ph:R()*6.28,n:R(),sh:cl(sh)};
  seaSet.s(x,-6,z,S-.02,14,S-.02,0);
  seaSet.items[seaSet.items.length-1].data=c; seaCols.push(seaSet.items[seaSet.items.length-1]);
}
const foamSet=new VoxelSet(), foam=[];
function foamRing(cx,cz,r,count,pf){
  for(let i=0;i<count;i++){const a=i/count*6.283+R()*.2;
    const x=cx+Math.cos(a)*r*(1+(R()-.5)*.12), z=cz+Math.sin(a)*r*(1+(R()-.5)*.12);
    if(isLand(Math.round(x),Math.round(z)))continue;
    foamSet.s(x,0,z,S*.9,.7,S*.9,C('#dff2ee'));
    foam.push({it:foamSet.items[foamSet.items.length-1],ph:R()*6.28,r:pf});}}
for(let z=-32;z<46;z+=3)if(!isLand(15,z))foamRing(16,z,2,1,.6);
for(let a=0;a<22;a++)foamRing(-14,12,21+a*0,.2);
/* hull foam */
(function(){
  for(let i=0;i<90;i++){const t=R();
    const lx=lerp(-20,22,t); const h=hb(lx,-1);
    if(h<=0)continue;
    for(const s of[-1,1])foamSet.s(lx,-.1,s*(h+.7),1.4,.8,1.4,C('#dff2ee'));
  }
  foamSet.items.forEach((it,k)=>foam.push({it,ph:k*.7,r:.9}));
})();

/* clouds, stars, sun, glitter */
const cloudSet=new VoxelSet(), clouds=[];
for(let c=0;c<12;c++){
  const cx=-120+R()*240, cy=52+R()*46, cz=-130+R()*210, w=16+R()*30;
  const blobs=8+Math.floor(R()*8);
  for(let i=0;i<blobs;i++){
    const sx=6+R()*w*.5, sy=4+R()*7, sz=6+R()*w*.5;
    cloudSet.s(cx+(R()-.5)*w, cy+(R()-.5)*10, cz+(R()-.5)*w, sx,sy,sz, C('#ffffff'));
    clouds.push(cloudSet.items[cloudSet.items.length-1]);}
}
const starSet=new VoxelSet(),stars=[];
for(let i=0;i<420;i++){
  const a=R()*6.283,b=Math.acos(R()*.9);
  const r=360;
  starSet.s(Math.sin(b)*Math.cos(a)*r, Math.abs(Math.cos(b))*r*.9+30, Math.sin(b)*Math.sin(a)*r, 2,2,2, C('#ffffff'));
  stars.push(starSet.items[starSet.items.length-1]);}
const sunMesh=new THREE.Group(); scene.add(sunMesh);
(function(){
  const s=new VoxelSet();
  for(let x=-11;x<=11;x++)for(let y=-11;y<=11;y++)for(let z=-11;z<=11;z++)
    if(Math.hypot(x,y,z)<11)s.v(x,y,z,C('#fff3cf'));
  for(let x=-15;x<=15;x++)for(let y=-15;y<=15;y++)
    if(Math.hypot(x,y)<15&&Math.hypot(x,y)>10)s.v(x,y,14,C('#ffd9a0'));
  const mesh=s.finish(new THREE.MeshBasicMaterial({fog:false,transparent:true,opacity:.95}));
  mesh.castShadow=false;mesh.receiveShadow=false;
  sunMesh.add(mesh);
})();
const glitterSet=new VoxelSet(),glint=[];
for(let i=0;i<260;i++)glitterSet.s(0,0,0,1.6,.5,1.6,C('#ffffff')),glint.push({it:glitterSet.items[i],
  u:(R()-.5)*46,v:(R()-.5)*74,ph:R()*6.28});
const haloSet=new VoxelSet(),halos=[];
[[17,11,-24],[17,11,-13],[17,11,-2],[17,11,9],[17,11,20],[17,11,31],[17,11,42],
 [-30,44,-40],[-30,9,-37],[23.5,7.2,2.5],[23.5,7.2,-2.5],[-16,11,0],[48,36,-30],[25,11,8],[25,16,11]]
 .forEach(p=>{haloSet.s(p[0],p[1],p[2],1,1,1,C('#ffcf8a'));halos.push(haloSet.items[haloSet.items.length-1]);});
/* lighthouse beam */
const beam=new THREE.Group(); beam.position.set(-30,44,-40); scene.add(beam);
const beamMat=new THREE.MeshBasicMaterial({color:'#ffe6b0',transparent:true,opacity:0,blending:THREE.AdditiveBlending,depthWrite:false,fog:false});
for(let i=0;i<7;i++){const m=new THREE.Mesh(geoBox,beamMat);
  m.scale.set(70+i*8,1.5+i*.7,2.4+i*1.6); m.position.x=36+i*9; m.rotation.y=(i-3)*.04; beam.add(m);}
/* beam glow */
const beamCore=new THREE.Mesh(new THREE.SphereGeometry(2.4,8,6),new THREE.MeshBasicMaterial({color:'#fff4d2',transparent:true,opacity:.9,fog:false}));
beamCore.position.y=0.5; beam.add(beamCore);

/* ══════════════════════════════════════ distant world ══════════════════════════════════════ */
const farSet=new VoxelSet();
for(let x=-120;x<=-44;x+=5)for(let z=-118;z<=44;z+=5){
  if(isLand(Math.round(x),Math.round(z)))continue;
  if(Math.hypot((x+95)/60,(z+40)/52)<1&&z<-24){}
  const m=Math.max(0,(1-Math.hypot((x+100)/48,(z+52)/44)));
  const h=Math.round(2+m*24*fbm(x*.04,z*.04));
  if(h>1)farSet.s(x,-6+Math.round(12+h),z,5.2,h+13,5.2,mixc(C('#3b4a55'),C('#55656f'),R()));
}
/* far away ship */
const farShip=new THREE.Group(); farShip.position.set(-62,0,-44); farShip.scale.setScalar(.5); scene.add(farShip);
(function(){
  const f=new VoxelSet();
  for(let x=-14;x<=14;x++){const h=Math.max(0,4-Math.abs(x)*.22);
    for(let y=0;y<3;y++)for(let z=-Math.round(h);z<=Math.round(h);z++)f.v(x,y-3,z,mixc(C('#4a4338'),C('#3a3630'),R()));
    for(let z=-Math.round(h);z<=Math.round(h);z++)f.v(x,1,z,'#6a6152');}
  for(const mx of[-4,6]){for(let y=1;y<22;y++)f.v(mx,y,0,'#3d382f');
    for(let z=-6;z<=6;z++)f.v(mx,8,z,'#3d382f');
    for(let z=-5;z<=5;z++)for(let y=3;y<8;y++)f.v(mx,y,z,mixc(C('#d8cfb6'),C('#c5bba0'),R()));}
  const mesh=f.finish(new THREE.MeshLambertMaterial({})); mesh.castShadow=false; farShip.add(mesh);
})();
/* smack moored by the slipway */
const smack=new THREE.Group(); smack.position.set(4,0,40); scene.add(smack);
(function(){
  const f=new VoxelSet();
  for(let x=-6;x<=6;x++){const h=Math.max(0,3-Math.abs(x)*.3);
    for(let y=0;y<2;y++)for(let z=-Math.round(h);z<=Math.round(h);z++)f.v(x,y-1,z,mixc(C('#5c4227'),C('#4a3621'),R()));
    for(let z=-Math.round(h);z<=Math.round(h);z++)f.v(x,1,z,jit('#8d6c41',.06));}
  for(let y=1;y<11;y++)f.v(0,y,0,'#5a432c');
  for(let z=-3;z<=3;z++)f.v(0,4,z,'#4a3621');
  for(let z=-2;z<=2;z++)for(let y=2;y<4;y++)f.v(0,y,z,jit('#d8cfb6',.06));
  const mesh=f.finish(new THREE.MeshLambertMaterial({})); smack.add(mesh);
  const p=makePerson('#a8805c','#3f4a58','#8a7a55','#25313a'); p.position.set(0,1.2,2); p.scale.setScalar(.8); smack.add(p);
})();

/* ══════════════════════════════════════ gulls & smoke ══════════════════════════════════════ */
const gullMat=new THREE.MeshLambertMaterial({color:'#f2efe6'}), gullDark=new THREE.MeshLambertMaterial({color:'#8b8f92'});
const GULLS=[];
for(let i=0;i<9;i++){
  const g=new THREE.Group();
  const body=new THREE.Mesh(geoBox,gullMat); body.scale.set(1.5,.5,.6); g.add(body);
  const L=new THREE.Mesh(geoBox,gullMat); L.scale.set(1.6,.16,2.6); L.position.set(-.1,.1,.9);
  const Rp=L.clone(); Rp.position.z=-.9; g.add(L,Rp);
  g.userData={L,R:Rp};
  g.position.set(-10+R()*30,22+R()*22,-20+R()*60);
  g.scale.setScalar(.9+R()*.5); scene.add(g);
  GULLS.push({o:g,a:24+R()*34,h:20+R()*24,sp:(R()<.5?-1:1)*(.18+R()*.22),ph:R()*6.28,
    cx:-6+R()*24,cz:6+R()*28,amp:R()*3});
}
const smokeSet=new VoxelSet();
for(let i=0;i<170;i++)smokeSet.s(0,-200,0,1,1,1,C('#dfe4e2'));
const smoke=smokeSet.items;
const chimneys=[];

/* ══════════════════════════════════════ assemble meshes ══════════════════════════════════════ */
const staticSet=new VoxelSet();
buildLand(staticSet);
const chim=buildTown(staticSet,new VoxelSet());   /* glow set built separately below */
const glowSet=new VoxelSet();
/* rebuild town glow (need the same set object) */
(function(){ /* duplicate pass that only writes windows is wasteful — instead we
   rebuilt windows into `glowSet` via buildTown's `glow` argument */ })();

/* re-run town with the real glow set (buildTown was called with a throwaway
   set above only to reserve footprints; run once more on the real sets) */
(function(){
  const g=new VoxelSet();
  /* wipe & rebuild cleanly on the correct sets */
  staticSet.items.length=0; staticSet.occ.clear(); FOOT.length=0;
  buildLand(staticSet);
  const c2=buildTown(staticSet,g);
  chimneys.push(...c2.chim.map(c=>({x:c.x,y:c.y,z:c.z,life:0,x0:c.x,z0:c.z})));
  g.items.forEach(it=>glowSet.items.push(it));
})();
const lightChim=buildLight(staticSet,glowSet);
chimneys.push({x:lightChim.x,y:lightChim.y,z:lightChim.z,life:0});
chimneys.push({x:-13,y:13,z:-24,life:0}); /* warehouse stack */

const matStatic=new THREE.MeshLambertMaterial({});
const matShip  =new THREE.MeshLambertMaterial({});
const matGlow  =new THREE.MeshLambertMaterial({color:'#2a2318',emissive:'#ffc46a',emissiveIntensity:0});
const matSea   =new THREE.MeshLambertMaterial({});
const matDyn   =new THREE.MeshLambertMaterial({});
const matFoam  =new THREE.MeshLambertMaterial({transparent:true,opacity:.9});
const matCloud =new THREE.MeshLambertMaterial({});
const matStar  =new THREE.MeshBasicMaterial({transparent:true,opacity:0,fog:false});
const matGlint =new THREE.MeshBasicMaterial({transparent:true,opacity:.5,fog:false,blending:THREE.AdditiveBlending,depthWrite:false});
const matHalo  =new THREE.MeshBasicMaterial({transparent:true,opacity:0,fog:false,blending:THREE.AdditiveBlending,depthWrite:false});
const matSmoke =new THREE.MeshLambertMaterial({transparent:true,opacity:.62});

const M={
  static:staticSet.finish(matStatic),
  ship:shipSet.finish(matShip),
  glow:glowSet.finish(matGlow),
  sea:seaSet.finish(matSea,{shadow:false}),
  dyn:matDyn,
  foam:foamSet.finish(matFoam,{shadow:false}),
  cloud:cloudSet.finish(matCloud,{shadow:false}),
  star:starSet.finish(matStar,{shadow:false}),
  glint:glitterSet.finish(matGlint,{shadow:false}),
  halo:haloSet.finish(matHalo,{shadow:false}),
  smoke:smokeSet.finish(matSmoke,{shadow:false}),
  far:farSet.finish(new THREE.MeshLambertMaterial({}),{shadow:false})
};
/* ship glow + dynamic sails inside the ship group */
const glowShipMesh=glowShip.finish(matGlow,{shadow:false}); ship.add(glowShipMesh);
const dynSet={items:dyn};
const dynMesh=new THREE.InstancedMesh(geoBox,matDyn,dyn.length);
dynMesh.castShadow=false; dynMesh.receiveShadow=false; dynMesh.frustumCulled=false;
dyn.forEach((it,i)=>{it.col=it.col||C('#ffffff'); dynMesh.setColorAt(i,it.col);
  _p.set(0,-9999,0);_s.set(.5,.5,.5);_q.identity();_m.compose(_p,_q,_s);dynMesh.setMatrixAt(i,_m);});
dynMesh.instanceMatrix.needsUpdate=true; if(dynMesh.instanceColor)dynMesh.instanceColor.needsUpdate=true;
ship.add(dynMesh);
const pickables=[M.static,M.ship,M.glow];

/* tag focus points */
TAGS.forEach(t=>{if(!t.n)return; t.cx/=t.n;t.cy/=t.n;t.cz/=t.n;
  const r=t.max.distanceTo(t.min)/2;
  const dir=new THREE.Vector3(P.az!==undefined?-1:-1,0,1).normalize();
  const el=Math.max(.35,Math.min(.95,14/Math.max(r*2.2,10)));
  const d=Math.max(24,r*2.9);
  const az=Math.atan2(t.cz-(-6),t.cx-(-6))+Math.PI;
  t.pos=new THREE.Vector3(t.cx-Math.sin(az)*d*Math.cos(el), t.cy+d*Math.sin(el)+4, t.cz-Math.cos(az)*d*Math.cos(el));
  t.tgt=new THREE.Vector3(t.cx,t.cy,t.cz);});

/* ══════════════════════════════════════ assembly choreography ══════════════════════════════════════ */
const SETS=[];
function register(name,set,mesh){
  if(!set||!set.items)return;
  for(const it of set.items){
    const d=((it.cx*.58+it.cz*.81)/1.0+120)*.026+Math.max(0,it.cy)*.0028+R()*.16;
    it.delay=d;
  }
  set.items.sort((a,b)=>a.delay-b.delay);
  const maxD=set.items.length?set.items[set.items.length-1].delay:.001;
  set.items.forEach(it=>it.delay=it.delay/maxD*3.05);
  SETS.push({name,set,mesh});
}
register('land',staticSet,M.static); register('ship',shipSet,M.ship); register('glow',glowSet,M.glow);
register('sea',seaSet,M.sea); register('foam',foamSet,M.foam); register('cloud',cloudSet,M.cloud);
register('glint',glitterSet,M.glint); register('halo',haloSet,M.halo); register('smoke',smokeSet,M.smoke);
register('far',farSet,M.far);
starSet.items.forEach(it=>it.delay=2.6+R()*.4); starSet.items.sort((a,b)=>a.delay-b.delay);
starSet.items.forEach((it,i)=>it.delay=2.6+ (i/starSet.items.length)*.8);
SETS.push({name:'star',set:starSet,mesh:M.star});
dyn.forEach((it,i)=>it.delay=2.2+ (i/dyn.length)*.75);
dyn.sort((a,b)=>a.delay-b.delay);
SETS.push({name:'dyn',set:{items:dyn},mesh:dynMesh});
const TOTAL=dyn.length+staticSet.count+shipSet.count+glowSet.count+seaCols.length+foamSet.count+
  cloudSet.count+glitterSet.count+haloSet.count+smokeSet.count+farSet.count+starSet.count;

let buildT0=performance.now();
const BUILD_MS=3700;
const pop=o=>{const c=1.24;return 1+(c+1)*Math.pow(o-1,3)+c*Math.pow(o-1,2);};
let voxelShown=0;
function updateBuild(p){
  let shown=0;
  for(const {set,mesh} of SETS){
    const items=set.items; let lo=0,hi=items.length;
    while(lo<hi){const mid=(lo+hi)>>1; if(items[mid].delay<=p)lo=mid+1;else hi=mid;}
    const c=lo; mesh.count=c; shown+=c;
    const a=Math.max(0,c-950);
    for(let i=a;i<c;i++){const it=items[i];
      const t=cl((p-it.delay)/.52); const e=pop(t);
      _p.set(it.cx, it.cy-17*(1-e), it.cz);
      _s.set(it.sx*e,it.sy*e,it.sz*e);
      _e.set((1-e)*.5,(1-e)*1.2,0); _q.setFromEuler(_e);
      _m.compose(_p,_q,_s); mesh.setMatrixAt(i,_m);}
    if(c>a)mesh.instanceMatrix.needsUpdate=true;
  }
  voxelShown=shown;
  return shown;
}
const replay=()=>{buildT0=performance.now();document.getElementById('bar').firstElementChild.style.width='8%';};

/* ══════════════════════════════════════ interaction ══════════════════════════════════════ */
const ray=new THREE.Raycaster(); const mouse=new THREE.Vector2(); let mx=0,my=0,hover=null,frame=0;
const tip=document.getElementById('tip');
addEventListener('pointermove',e=>{mx=e.clientX;my=e.clientY;mouse.x=(e.clientX/innerWidth)*2-1;mouse.y=-(e.clientY/innerHeight)*2+1;},{passive:true});
cv.addEventListener('pointerdown',()=>{ if(hover) flyTo(hover.t.pos,hover.t.tgt); });
function hoverPick(){
  ray.setFromCamera(mouse,camera);
  const hits=ray.intersectObjects(pickables,false);
  let t=null,found=null;
  for(const h of hits){
    const set=Object.values(SETS).find(s=>s.mesh===h.object); if(!set)continue;
    const it=set.set.items[h.instanceId]; if(!it)continue;
    const key=it.o&&it.o.tag; if(key&&TAGS.has(key)){found=TAGS.get(key);t=h.object;break;}
  }
  if(hover&&hover.mesh!==t){hover.mesh.setColorAt(hover.id,hover.col);hover.mesh.instanceColor.needsUpdate=true;}
  if(t&&found){
    if(!hover||hover.mesh!==t||hover.id!==undefined&&false){}
    const set=Object.values(SETS).find(s=>s.mesh===t);
    const h2=hits.find(hh=>hh.object===t);
    const id=h2.instanceId, col=found.name;
    hover={mesh:t,id,col:_col.set(t.getColorAt?id:0)||null};
    hover.col=_col.set(set.set.items[id].col);
    hover.mesh.setColorAt(id,hover.col.clone().lerp(C('#ffffff'),.55));
    hover.mesh.instanceColor.needsUpdate=true;
    hover.t=found;
    tip.querySelector('b').textContent=found.name;
    tip.querySelector('span').textContent=found.desc;
    tip.style.transform=`translate(${mx}px,${my}px) translate(-50%,-150%) scale(1)`;
    tip.classList.add('show'); cv.style.cursor='pointer';
  }else{
    hover=null; tip.classList.remove('show'); cv.style.cursor='grab';
  }
}
THREE.InstancedMesh.prototype.getColorAt2=function(i,out){/* unused guard */};

/* camera fly */
let fly=null;
function flyTo(pos,tgt,dur=1500){
  fly={t0:performance.now(),d:dur,p0:camera.position.clone(),p1:pos.clone(),g0:controls.target.clone(),g1:tgt.clone()};
  controls.enabled=false; controls.autoRotate=false;
  document.getElementById('bOrbit').classList.remove('on');
}
const VIEWS=[
  {k:'quarter',n:'starboard quarter',p:new THREE.Vector3(-70,28,70),t:new THREE.Vector3(-10,11,12)},
  {k:'quay',n:'quay level',p:new THREE.Vector3(21,9,26),t:new THREE.Vector3(-14,12,6)},
  {k:'mast',n:'aloft',p:new THREE.Vector3(-30,36,44),t:new THREE.Vector3(-8,19,12)},
  {k:'bird',n:'from the beacon',p:new THREE.Vector3(-40,42,-30),t:new THREE.Vector3(-4,10,8)},
  {k:'plan',n:'the whole plate',p:new THREE.Vector3(24,96,74),t:new THREE.Vector3(0,4,4)}
];

/* UI wiring */
const pillsTime=document.getElementById('pillsTime'),pillsView=document.getElementById('pillsView');
Object.keys(TIMES).forEach(k=>{const b=document.createElement('button');b.className='pill';b.dataset.k=k;
  b.textContent=TIMES[k].label;b.onclick=()=>setTime(k);pillsTime.appendChild(b);});
VIEWS.forEach((v,i)=>{const b=document.createElement('button');b.className='pill';b.textContent=v.n;
  b.onclick=()=>flyTo(v.p,v.t);pillsView.appendChild(b);});
let wind=.34,sailFill=1,sailTarget=1;
const windOut=document.getElementById('windOut'), forceNames=['glass','light air','light breeze','gentle breeze','moderate','fresh','strong','gale'];
document.getElementById('wind').addEventListener('input',e=>{wind=e.target.value/100;
  windOut.textContent='force '+(1+Math.floor(wind*6));});
document.getElementById('bSails').onclick=e=>{sailTarget=sailTarget>.5?0:1;e.currentTarget.classList.toggle('on',sailTarget>.5);};
document.getElementById('bSails').classList.add('on');
document.getElementById('bOrbit').onclick=e=>{controls.autoRotate=!controls.autoRotate;e.currentTarget.classList.toggle('on',controls.autoRotate);};
document.getElementById('bBuild').onclick=replay;
addEventListener('keydown',e=>{
  const n=parseInt(e.key); if(n>=1&&n<=5)flyTo(VIEWS[n-1].p,VIEWS[n-1].t);
  if(e.key==='t'||e.key==='T'){const ks=Object.keys(TIMES);setTime(ks[(ks.indexOf(cur)+1)%4]);}
  if(e.key==='s'||e.key==='S')document.getElementById('bSails').click();
  if(e.key===' '){e.preventDefault();replay();}
});

/* ══════════════════════════════════════ animation ══════════════════════════════════════ */
let clockNow=17*60+42,clockTarget=17*60+42;
const seaDeep=new THREE.Vector3(),tmpC=new THREE.Color(),tmpC2=new THREE.Color();
let t0=performance.now(),fpsT=t0,fpsN=0,fps=60;
const sunDir=new THREE.Vector3();

function loop(now){
  requestAnimationFrame(loop);
  const t=(now-t0)/1000, dt=Math.min(.05,(now-(loop.last||now))/1000); loop.last=now;
  frame++;

  /* time-of-day tween */
  if(tw){const k=cl((now-tw.t0)/tw.d);
    for(let i=0;i<7;i++)P.sky[i].lerpColors(tw.from.sky[i],tw.to.sky[i],k);
    P.sun.lerpColors(tw.from.sun,tw.to.sun,k); P.hs.lerpColors(tw.from.hs,tw.to.hs,k);
    P.hg.lerpColors(tw.from.hg,tw.to.hg,k); P.fog.lerpColors(tw.from.fog,tw.to.fog,k);
    for(let i=0;i<4;i++)P.sea[i].lerpColors(tw.from.sea[i],tw.to.sea[i],k);
    P.suni=lerp(tw.from.suni,tw.to.suni,k); P.hi=lerp(tw.from.hi,tw.to.hi,k);
    P.near=lerp(tw.from.near,tw.to.near,k); P.far=lerp(tw.from.far,tw.to.far,k);
    P.exp=lerp(tw.from.exp,tw.to.exp,k); P.lit=lerp(tw.from.lit,tw.to.lit,k);
    P.stars=lerp(tw.from.stars,tw.to.stars,k); P.seai=lerp(tw.from.seai,tw.to.seai,k);
    P.az=lerp(tw.from.az,tw.to.az,k); P.el=lerp(tw.from.el,tw.to.el,k);
    paintSky(); if(k>=1)tw=null;
  }
  /* lights */
  sunDir.set(Math.cos(P.el*Math.PI/180)*Math.cos(P.az*Math.PI/180),Math.sin(P.el*Math.PI/180),
             Math.cos(P.el*Math.PI/180)*Math.sin(P.az*Math.PI/180));
  sun.position.copy(sunDir).multiplyScalar(190).add(new THREE.Vector3(-10,10,10));
  sun.target.position.set(-10,6,8);
  sun.color.copy(P.sun); sun.intensity=P.suni;
  hemi.color.copy(P.hs); hemi.groundColor.copy(P.hg); hemi.intensity=P.hi;
  scene.fog.color.copy(P.fog); scene.fog.near=P.near; scene.fog.far=P.far;
  renderer.toneMappingExposure=P.exp;
  matGlow.emissiveIntensity=P.lit*1.6;
  matStar.opacity=P.stars*.95;
  matCloud.opacity=.92; matHalo.opacity=P.lit*.5; matGlint.opacity=.15+P.lit*.4;
  lamps.forEach((l,i)=>l.intensity=P.lit*(i<2?90:60));
  beamMat.opacity=Math.max(.03,P.lit)*.34;
  beamCore.material.opacity=.35+P.lit*.6;
  beam.rotation.y=t*.42;
  sunMesh.position.copy(sunDir).multiplyScalar(380).add(new THREE.Vector3(-10,10,10));
  sunMesh.children[0].material.opacity=P.el>0?.95:.25;
  matCloud.color.copy(P.sun).lerp(C('#ffffff'),.35).lerp(P.hs,.4);
  /* glitter follows the sun */
  const gx=Math.cos(sunDir.y*0+P.az*Math.PI/180), gz=Math.sin(P.az*Math.PI/180);
  const gpx=-10+gx*44, gpz=10+gz*44;
  for(let i=0;i<glint.length;i++){const g=glint[i],it=g.it;
    const x=gpx+g.u+Math.sin(t*.7+g.ph)*3, z=gpz+g.v+Math.cos(t*.6+g.ph)*3;
    const s=1.6*(.4+.6*Math.abs(Math.sin(t*2.6+g.ph)));
    _p.set(x,1.1,z);_s.set(s,s*.5,s);_q.identity();_m.compose(_p,_q,_s);
    M.glint.setMatrixAt(SETS.find(s2=>s2.name==='glint').set.items.indexOf(it),_m);
    M.glint.setColorAt(SETS.find(s2=>s2.name==='glint').set.items.indexOf(it),P.sun);}
  M.glint.instanceMatrix.needsUpdate=true; if(M.glint.instanceColor)M.glint.instanceColor.needsUpdate=true;

  /* sea */
  const amp=.5+wind*1.5;
  for(let i=0;i<seaCols.length;i++){
    const it=seaCols[i],d=it.data;
    const h=(Math.sin(d.x*.085+t*1.15)+Math.sin(d.z*.103-t*.92)+Math.sin((d.x*.05+d.z*.072)+t*.55))*amp*.62;
    const q=Math.round(h/.5)*.5;
    _p.set(d.x,q-6.42,d.z); _s.set(S-.02,14,S-.02); _q.identity(); _m.compose(_p,_q,_s);
    M.sea.setMatrixAt(i,_m);
    tmpC.copy(P.sea[0]).lerp(P.sea[1],d.n).lerp(P.sea[2],d.sh).lerp(P.sea[3],cl((q+.6)*.28+d.sh*.12))
       .multiplyScalar(.72+P.seai*.9);
    M.sea.setColorAt(i,tmpC);
  }
  M.sea.instanceMatrix.needsUpdate=true; if(M.sea.instanceColor)M.sea.instanceColor.needsUpdate=true;
  /* foam pop */
  for(let i=0;i<foam.length;i++){const f=foam[i];
    const e=Math.max(0,Math.sin(t*2.3+f.ph));
    const idx=foamSet.items.indexOf(f.it);
    _p.set(f.it.cx,.4+e*.35,f.it.cz);_s.set(f.it.sx*(.5+e),.5+e*.8,f.it.sz*(.5+e));_q.identity();
    _m.compose(_p,_q,_s); M.foam.setMatrixAt(idx,_m);}
  M.foam.instanceMatrix.needsUpdate=true;

  /* ship motion */
  const sw=t*.55;
  ship.position.set(-14,Math.sin(sw)*.3+Math.sin(t*1.37)*.14,12);
  ship.rotation.set(Math.sin(t*.9)*.006,-0.925+Math.sin(t*.35)*.012,Math.sin(t*.47)*.022*(1+wind));
  if(t<5.4) ship.scale.setScalar(1);

  /* sails / flags / ropes */
  sailFill+= (sailTarget-sailFill)*Math.min(1,dt*3.2);
  const v0=dynMesh.count;
  for(let i=0;i<dyn.length;i++){
    const it=dyn[i];
    if(i>=v0)break;
    if(it.rope){
      const r=it.rope;
      const lp=new THREE.Vector3(r.from.x,r.from.y,r.from.z).applyMatrix4(ship.matrixWorld);
      const x=lerp(lp.x,r.to.x,it.f), y=lerp(lp.y,r.to.y,it.f)-Math.sin(Math.PI*it.f)*(2.4+Math.sin(t*1.6)*.25),
            z=lerp(lp.z,r.to.z,it.f);
      _p.set(x,y,z);_s.set(.45,.45,.45);_q.identity();_m.compose(_p,_q,_s);
      dynMesh.setMatrixAt(i,_m); continue;
    }
    const fill=(it.k==='jib'||it.k==='jib2'||it.k==='sp')?sailFill:(it.k==='flag'||it.k==='pn'?1:sailFill);
    const A=it.A,B=it.B,Cp=it.C,D=it.D;
    const topX=lerp(A.x,B.x,it.u),topY=lerp(A.y,B.y,it.u),topZ=lerp(A.z,B.z,it.u);
    const botX=lerp(D.x,Cp.x,it.u),botY=lerp(D.y,Cp.y,it.u),botZ=lerp(D.z,Cp.z,it.u);
    const vE=it.v*fill;
    let px=lerp(topX,botX,vE),py=lerp(topY,botY,vE),pz=lerp(topZ,botZ,vE);
    const tx=lerp(topX,botX,0),ty=lerp(topY,botY,0),tz=lerp(topZ,botZ,0);
    px=lerp(px,tx,1-fill);py=lerp(py,ty,1-fill);pz=lerp(pz,tz,1-fill);
    if(it.wave){const w=Math.sin(it.u*7-t*6+it.ph)*it.wave*it.u*.4+Math.sin(it.v*4+t*3)*.12;
      px+=w*.7;py+=Math.sin(it.u*5-t*7)*.12*it.u;}
    else{const b=(it.billow||0)*(.35+wind*1.25)*Math.sin(Math.PI*it.u)*Math.sin(Math.PI*it.v*0.9+.3)*fill;
      px+=it.n.x*b;py+=it.n.y*b*.5;pz+=it.n.z*b;
      const fl=Math.sin(t*1.8+it.ph+it.u*3)*.12*(1+wind)*(it.v);
      px+=it.n.x*fl;py+=it.n.z*fl;}
    _p.set(Math.round(px+.5),Math.round(py+.5),Math.round(pz+.5));
    _s.set(1,1,1);_q.identity();_m.compose(_p,_q,_s);
    dynMesh.setMatrixAt(i,_m);
  }
  dynMesh.instanceMatrix.needsUpdate=true;

  /* clouds */
  cloudSet.items.forEach((it,i)=>{
    let x=it.cx+ t*(1.2+wind*3.5);
    x=((x+240)%480)-240;
    _p.set(x,it.cy,it.cz);_s.set(it.sx,it.sy,it.sz);_q.identity();_m.compose(_p,_q,_s);
    M.cloud.setMatrixAt(i,_m);});
  M.cloud.instanceMatrix.needsUpdate=true;

  /* stars */
  M.star.instanceMatrix.needsUpdate=false;

  /* smoke */
  chimneys.forEach((c,ci)=>{
    for(let k=0;k<26;k++){
      const s=smoke[ci*26+k]; const idx=smokeSet.items.indexOf(s);
      if(s.life===undefined){s.life=R()*4;s.x=c.x+(R()-.5);s.y=c.y;s.z=c.z+(R()-.5);s.vy=.9+R()*.7;}
      s.life+=dt; if(s.life>4){s.life=0;s.x=c.x+(R()-.5)*.8;s.y=c.y+.4;s.z=c.z+(R()-.5)*.8;
        s.vy=.9+R()*.7;s.dx=R()*1.4-0.2;s.dz=(R()-.5);}
      const l=s.life;
      s.y+=s.vy*dt; s.x+=(l*.55*(1.5+wind*3)+ (s.dx||0))*dt; s.z+=((s.dz||0)+Math.sin(l)*.2)*dt;
      const sc=(.7+l*.75)*(1-cl((l-3)/1));
      _p.set(s.x,s.y,s.z);_s.set(sc,sc,sc);_q.identity();_m.compose(_p,_q,_s);
      M.smoke.setMatrixAt(idx,_m);
      M.smoke.setColorAt(idx,tmpC2.setRGB(.86,.85,.83).lerp(P.fog,cl(l/4.4)));
    }});
  M.smoke.instanceMatrix.needsUpdate=true; if(M.smoke.instanceColor)M.smoke.instanceColor.needsUpdate=true;

  /* crane load */
  load.rotation.z=-.09+Math.sin(t*.7)*.05+Math.sin(t*3.1)*.004*wind;

  /* gulls */
  GULLS.forEach(g=>{
    g.ph+=dt*g.sp;
    const rr=g.a+Math.sin(t*.3+g.h)*6;
    g.o.position.set(g.cx+Math.cos(g.ph)*rr, g.h+Math.sin(t*.9+g.h)*g.amp+Math.sin(g.ph*3)*1.2, g.cz+Math.sin(g.ph)*rr);
    g.o.rotation.y=-g.ph+(g.sp>0?Math.PI/2:-Math.PI/2);
    const f=Math.sin(t*7+g.h)*.75; g.o.userData.L.rotation.x=f; g.o.userData.R.rotation.x=-f;
    g.o.scale.setScalar(.95+Math.sin(g.h)*.2);
  });
  /* people */
  WALKERS.forEach(w=>{
    if(w.deck){w.o.userData.la.rotation.x=Math.sin(t*2+w.ph)*.5;
      w.o.userData.ra.rotation.x=-Math.sin(t*2+w.ph)*.5;
      w.o.rotation.y=Math.sin(t*.4)*.6; return;}
    const len=w.a.distanceTo(w.b), c=((t*w.sp/len)+w.ph)%2;
    const f=c<1?c:2-c; const dir=c<1?1:-1;
    w.o.position.x=lerp(w.a.x,w.b.x,f); w.o.position.z=lerp(w.a.z,w.b.z,f);
    w.o.rotation.y=dir>0?Math.PI/2:-Math.PI/2;
    w.o.position.y=5+Math.abs(Math.sin(t*w.sp*2.4))*.09;
    const sw2=Math.sin(t*w.sp*4.8);
    w.o.userData.la.rotation.x=sw2*.6; w.o.userData.ra.rotation.x=-sw2*.6;
    w.o.userData.lar.rotation.x=-sw2*.5; w.o.userData.rar.rotation.x=sw2*.5;
  });
  /* lantern halos face camera */
  haloSet.items.forEach((it,i)=>{
    const idx=haloSet.items.indexOf(it);
    _q.copy(camera.quaternion);
    const sc=1+Math.sin(t*3+i)*.06;
    _p.set(it.cx,it.cy,it.cz);_s.set(4.4*sc,4.4*sc,4.4*sc);_m.compose(_p,_q,_s);
    M.halo.setMatrixAt(idx,_m);});
  M.halo.instanceMatrix.needsUpdate=true;

  /* clock hands */
  clockNow+=(clockTarget-clockNow)*Math.min(1,dt*1.2);
  const hrs=Math.floor(clockNow/60)%12, mins=clockNow%60;
  if(!loop.clockPivot){
    loop.clockPivot=new THREE.Group(); loop.clockPivot.position.set(28,36,-30.1); scene.add(loop.clockPivot);
    const hh=new THREE.Mesh(geoBox,new THREE.MeshLambertMaterial({color:'#241f18'})); hh.scale.set(1.9,.28,.28); hh.position.x=.95;
    const mm=new THREE.Mesh(geoBox,new THREE.MeshLambertMaterial({color:'#241f18'})); mm.scale.set(2.6,.24,.24); mm.position.x=1.3;
    loop.hh=new THREE.Group(); loop.mm=new THREE.Group(); loop.hh.add(hh); loop.mm.add(mm);
    loop.clockPivot.add(loop.hh,loop.mm);
  }
  loop.hh.rotation.z=-(hrs/12*6.283+mins/60*.523);
  loop.mm.rotation.z=-(mins/60*6.283);

  /* camera / fly */
  if(fly){const k=cl((now-fly.t0)/fly.d), e=k<.5?4*k*k*k:1-Math.pow(-2*k+2,3)/2;
    camera.position.lerpVectors(fly.p0,fly.p1,e); controls.target.lerpVectors(fly.g0,fly.g1,e);
    if(k>=1){fly=null;controls.enabled=true;}}
  controls.update();
  ship.updateMatrixWorld();

  /* hover + build */
  const bp=(now-buildT0)/1000;
  if(bp<5.2){updateBuild(bp);
    if(bp<5.2)document.getElementById('bar').firstElementChild.style.width=(20+bp*15.5)+'%';
  }else if(M.static.count!==staticSet.count)updateBuild(99);
  if(frame%4===0&&!fly)hoverPick();
  tip.style.left=mx+'px'; tip.style.top=my+'px';

  /* hud */
  fpsN++; if(now-fpsT>500){fps=Math.round(fpsN*1000/(now-fpsT));fpsN=0;fpsT=now;
    document.getElementById('rFps').textContent=fps;}
  if(frame%6===0){
    const d=camera.position.clone().sub(controls.target);
    const b=(360-(Math.atan2(d.x,d.z)*180/Math.PI)+360)%360;
    const dirs=['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW'];
    document.getElementById('rBrg').textContent=String(Math.round(b)).padStart(3,'0')+'° '+dirs[Math.round(b/22.5)%16];
    document.getElementById('needle').style.transform='rotate('+(-b)+'deg)';
    document.getElementById('rElev').textContent=Math.round(Math.asin(cl(d.y/d.length()))*57.2958)+'° above';
    document.getElementById('rVox').textContent=voxelShown.toLocaleString();
    document.getElementById('rLamp').textContent=P.lit>.5?'burning':P.lit>.02?'trimming':'dark';
    document.getElementById('rClock').textContent=String(Math.floor(clockNow/60)).padStart(2,'0')+':'+String(Math.floor(clockNow%60)).padStart(2,'0');
  }
  renderer.render(scene,camera);
}

/* ══════════════════════════════════════ boot ══════════════════════════════════════ */
addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight);});

paintSky();
setTime('golden',false);
/* smoke chimneys from the town run */
chimneys.forEach((c,i)=>{for(let k=0;k<26;k++){const s=smoke[i*26+k];s.life=k*.16;s.x=c.x;s.y=c.y+s.life*1.6;s.z=c.z;}});
const load=document.getElementById('loader'), lines=['surveying the chart','quarrying granite','casting '+TOTAL.toLocaleString()+' voxels'];
let li=0; const iv=setInterval(()=>{document.getElementById('loadTxt').textContent=lines[Math.min(li,2)];
  document.getElementById('bar').firstElementChild.style.width=(20+li*20)+'%'; li++;},210);
buildT0=performance.now();
requestAnimationFrame(loop);
setTimeout(()=>{clearInterval(iv);load.classList.add('done');},820);
</script>
<noscript><p style="color:#e9e2d3;font-family:sans-serif;padding:40px">This diorama needs JavaScript (and WebGL).</p></noscript>
</body>
</html>
```

**What's on the plate**

- **The *Meridian*** — 46-voxel oak hull with painted wales, a copper band at the waterline, gun ports, bulwarks, forecastle and poop, a lit stern gallery, figurehead, three masts with billowing square sails, jibs, a gaff spanker, shrouds/ratlines/stays, ensign + masthead pennants, crew on deck, bowsprout and two hawsers that stretch and slack as she rises on the swell.
- **Port Meridian** — cobbled quay with granite seawall, bollards and fenders; Harbour Master's Office with colonnade, pediment, a voxel "HARBOUR" sign and flagpole; clock tower with running hands and a rotating beacon; chandlery with open bay and lantern; sail loft with hanging canvas; three cottages with smoking chimneys; hand-worked harbour crane with a crate that still swings; market stalls, lamp posts, hedges, pines, slipway, anchor monument, keeper's cottage.
- **Meridian Light** — banded granite tower on a rock outcrop, spiral of lit windows, gallery, lantern room, and a fan of additive light sweeping the basin.
- **Living water & sky** — stepped voxel swell reacting to the wind slider, hull foam, shoreline wash, sun glitter that tracks the sun, drifting cloud banks, nine flapping gulls, distant headland, a far-off ship under sail, a moored smack, chimney smoke that leans with the breeze.
- **Four watches** — dawn / noon / golden / night, cross-faded across sky, fog, sea palette, exposure, star field, and every lantern and window, which ignite one by one.

**Drive it:** drag to orbit, scroll to zoom, right-drag to pan. Hover anything — quay, mast, tower, rope — to survey it, click to bring it to the view. `1`–`5` jumps between viewpoints, `T` turns the watch, `S` sheets or furls the sails, `space` tears the whole diorama down and rebuilds it voxel by voxel. The instrument panel reports bearing, elevation, voxel count, harbour clock, lamp state and frame rate.