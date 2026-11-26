# Harbor Call — a voxel sailing ship at anchor

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Harbor Call · voxel scene</title>
<link rel="preconnect" href="https://fonts.gstatic.com">
<link href="https://fonts.googleapis.com/css2?family=Alfa+Slab+One&family=Cabin:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root{
    --navy:#0b1622; --navy2:#132330; --brass:#d9b26b; --brass2:#8d6f3c;
    --paper:#f2ece1; --red:#c8483a;
  }
  *{box-sizing:border-box}
  html,body{margin:0;height:100%;overflow:hidden;background:#0b1622;
    font-family:'Cabin',system-ui,sans-serif;color:var(--paper)}
  canvas{display:block;touch-action:none}

  .plate{
    background:linear-gradient(180deg,rgba(11,22,34,.9),rgba(11,22,34,.72));
    border:1px solid var(--brass2);
    box-shadow:0 0 0 1px rgba(217,178,107,.18) inset, 0 10px 40px rgba(0,0,0,.45);
  }

  /* ---- title plate ---- */
  #title{position:absolute;left:22px;top:20px;display:flex;gap:14px;align-items:stretch;
    padding:12px 18px 12px 14px;max-width:min(92vw,560px)}
  #rose{width:52px;height:52px;flex:0 0 auto;filter:drop-shadow(0 1px 0 rgba(255,255,255,.12))}
  #title h1{font-family:'Alfa Slab One',serif;font-weight:400;margin:0;
    font-size:clamp(20px,3.1vw,32px);letter-spacing:.02em;line-height:1;color:#f6e9d2;
    text-shadow:0 2px 0 rgba(0,0,0,.35)}
  #title h1 em{font-style:normal;color:var(--brass)}
  #title .rule{height:1px;background:linear-gradient(90deg,var(--brass),transparent);margin:8px 0 7px}
  #title p{margin:0;font-size:12.5px;letter-spacing:.14em;text-transform:uppercase;
    color:rgba(242,236,225,.62)}

  /* ---- dials (time of day) ---- */
  #dials{position:absolute;right:22px;top:20px;padding:10px 12px;display:flex;flex-direction:column;gap:8px}
  #dials .cap{font-size:10px;letter-spacing:.22em;text-transform:uppercase;color:var(--brass);padding-left:2px}
  .row{display:flex;gap:6px;flex-wrap:wrap}
  button{font-family:'Cabin',sans-serif;cursor:pointer;color:#e9dfcd;
    background:rgba(255,255,255,.04);border:1px solid rgba(217,178,107,.35);
    padding:7px 10px;font-size:11.5px;letter-spacing:.06em;transition:.18s;
    border-radius:2px}
  button:hover{background:rgba(217,178,107,.16);border-color:var(--brass);transform:translateY(-1px)}
  button.on{background:var(--brass);color:#14202b;border-color:var(--brass);font-weight:600}
  button b{display:block;font-size:9px;letter-spacing:.14em;opacity:.7;font-weight:400}

  /* ---- legend ---- */
  #legend{position:absolute;left:22px;bottom:20px;padding:11px 14px;max-width:min(92vw,380px)}
  #legend .k{font-size:10px;letter-spacing:.22em;text-transform:uppercase;color:var(--brass);margin-bottom:7px}
  #legend .li{display:flex;gap:8px;font-size:12.5px;color:rgba(242,236,225,.8);line-height:1.75}
  #legend .li span{color:var(--brass);min-width:74px;display:inline-block;font-size:11px;letter-spacing:.08em}

  /* ---- inspector ---- */
  #log{position:absolute;right:22px;bottom:20px;width:250px;padding:12px 14px;
    opacity:0;transform:translateY(10px);transition:.35s cubic-bezier(.2,.8,.2,1);pointer-events:none}
  #log.show{opacity:1;transform:none}
  #log .sw{width:12px;height:12px;display:inline-block;border:1px solid rgba(255,255,255,.35);margin-right:8px;vertical-align:-1px}
  #log h3{font-family:'Alfa Slab One',serif;font-weight:400;font-size:16px;margin:0 0 6px;color:#f6e9d2;line-height:1.2}
  #log p{margin:0;font-size:12.5px;color:rgba(242,236,225,.72);line-height:1.55}

  #hud{position:absolute;left:50%;bottom:22px;transform:translateX(-50%);text-align:center;
    font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:rgba(242,236,225,.42);
    pointer-events:none}
  #hud b{color:var(--brass);font-weight:600}

  #boot{position:absolute;inset:0;background:#0b1622;display:flex;flex-direction:column;
    gap:16px;align-items:center;justify-content:center;transition:opacity .7s;z-index:9}
  #boot .ship{width:74px;height:44px;animation:rock 2.4s ease-in-out infinite}
  #boot .t{font-family:'Alfa Slab One',serif;font-size:14px;letter-spacing:.26em;color:var(--brass)}
  #boot .b{width:200px;height:2px;background:rgba(217,178,107,.22);overflow:hidden}
  #boot .b i{display:block;height:100%;width:30%;background:var(--brass);animation:sweep 1.1s ease-in-out infinite}
  @keyframes sweep{0%{transform:translateX(-100%)}100%{transform:translateX(330%)}}
  @keyframes rock{0%,100%{transform:rotate(-7deg) translateY(2px)}50%{transform:rotate(7deg) translateY(-2px)}}
  .gone{opacity:0!important;pointer-events:none}
</style>
</head>
<body>
<div id="boot">
  <svg class="ship" viewBox="0 0 40 24" fill="none">
    <path d="M4 16h32l-4 6H8z" fill="#d9b26b"/>
    <path d="M20 2v14M20 3l9 11H20zM18 4L9 14h9z" stroke="#f2ece1" stroke-width="1.6" stroke-linejoin="round"/>
  </svg>
  <div class="t">UNFURLING THE SAILS</div>
  <div class="b"><i></i></div>
</div>

<div id="title" class="plate">
  <svg id="rose" viewBox="0 0 100 100">
    <circle cx="50" cy="50" r="46" fill="none" stroke="#8d6f3c" stroke-width="2"/>
    <circle cx="50" cy="50" r="34" fill="none" stroke="rgba(217,178,107,.35)" stroke-width="1"/>
    <path d="M50 4 L57 44 L96 50 L57 56 L50 96 L43 56 L4 50 L43 44Z" fill="#d9b26b"/>
    <path d="M50 4 L57 44 L50 50Z M50 96 L43 56 L50 50Z M96 50 L57 56 L50 50Z M4 50 L43 44 L50 50Z" fill="#f2ece1"/>
    <circle cx="50" cy="50" r="5" fill="#0b1622" stroke="#d9b26b" stroke-width="2"/>
  </svg>
  <div>
    <h1>HARBOR <em>CALL</em></h1>
    <div class="rule"></div>
    <p>The barque <b>Meridian</b> · 1862 · berthing in the deep-water basin</p>
  </div>
</div>

<div id="dials" class="plate">
  <div class="cap">Watch · time of day</div>
  <div class="row" id="timeRow">
    <button data-t="dawn"><b>04:40</b>Dawn</button>
    <button data-t="day"><b>12:00</b>Noon</button>
    <button data-t="golden"><b>18:20</b>Golden</button>
    <button data-t="dusk" class="on"><b>20:10</b>Dusk</button>
    <button data-t="night"><b>23:30</b>Night</button>
  </div>
  <div class="cap">Viewport</div>
  <div class="row">
    <button data-c="sea">Sea</button>
    <button data-c="deck">Deck</button>
    <button data-c="light">Lighthouse</button>
    <button data-c="town">Town</button>
    <button id="spin" class="on">Auto-orbit</button>
  </div>
</div>

<div id="legend" class="plate">
  <div class="k">Ship's log — click any voxel</div>
  <div class="li"><span>drag</span> orbit the roads</div>
  <div class="li"><span>scroll</span> zoom · <span>right-drag</span> pan</div>
</div>

<div id="log" class="plate"><h3 id="logT"></h3><p id="logB"></p></div>
<div id="hud">drag to orbit · scroll to zoom · <b>click to identify</b></div>

<script type="importmap">
{"imports":{
 "three":"https://unpkg.com/three@0.160.0/build/three.module.js",
 "three/addons/":"https://unpkg.com/three@0.160.0/examples/jsm/"
}}
</script>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* ══════════════════════════════════════════════════════════
   0 · palette + math helpers
   ══════════════════════════════════════════════════════════ */
const P = {
  seaDeep:0x14384c, seaMid:0x1d5a6e, seaLit:0x28819a, seaTop:0x3a9fb2, foam:0xcfe6ea,
  stoneDark:0x5d5850, stone:0x87816f, stoneLit:0x9c9684, slate:0x465260, cobble:0x767a72,
  grass:0x4e6b39, grassLit:0x61804a, grassDark:0x3b5430, dirt:0x6b4d33, sand:0xc6ad7f, shingle:0x9a9080,
  plank:0x8f6c45, plankDk:0x6c5033, plankLt:0xa9854f, oak:0x4b3327, oakDk:0x36241c, oakLt:0x5f4230,
  hullBlk:0x2b2c31, hullRed:0x7a3028, white:0xe9e2d2, cream:0xefe4cb, creamDk:0xd7c8a7, gold:0xc9a34a,
  roofRed:0xa8442f, roofSl:0x3d4b58, roofGr:0x556b52, wallW:0xe7ddcb, wallC:0xd9c6a3, wallB:0x5d7080,
  wallO:0xc99442, wallG:0x8f9a7a, wallP:0x8b6f86,
  glass:0xffc96b, lamp:0xffd98a, iron:0x2f3338, ironLt:0x666c73, rope:0xd6c39a,
  crate:0xb18a52, barrel:0x8b6338, sailW:0xefe4cb, sailS:0xd6c6a4,
  ltRed:0xc2392e, ltWhite:0xf2ede2, gull:0xf2f1ee, gullDk:0x3a3d42,
  flagRed:0xc0392b, flagBl:0x25476b, flagY:0xf2c14e, cloud:0xf3d9c4, cloudDk:0xc9b6ac
};
const EMISSIVE = { [P.glass]:1.5, [P.lamp]:1.8 };

const clamp=(v,a,b)=>v<a?a:v>b?b:v;
const rnd=(s=>()=>{s=(s*1664525+1013904223)%4294967296;return s/4294967296;})(20250613);
function hash(x,z){const n=Math.sin(x*127.1+z*311.7)*43758.5453;return n-Math.floor(n);}
function vnoise(x,z){const xi=Math.floor(x),zi=Math.floor(z),xf=x-xi,zf=z-zi;
  const a=hash(xi,zi),b=hash(xi+1,zi),c=hash(xi,zi+1),d=hash(xi+1,zi+1);
  const u=xf*xf*(3-2*xf),v=zf*zf*(3-2*zf);
  return a*(1-u)*(1-v)+b*u*(1-v)+c*(1-u)*v+d*u*v;}
const fbm=(x,z)=>vnoise(x,z)*.6+vnoise(x*2.1+11.3,z*2.1-7.7)*.28+vnoise(x*4.7-5.1,z*4.7+3.3)*.12;

/* ══════════════════════════════════════════════════════════
   1 · renderer / scene / camera
   ══════════════════════════════════════════════════════════ */
const renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
renderer.shadowMap.autoUpdate = false;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x7b6a86, 0.0066);

const camera = new THREE.PerspectiveCamera(42, innerWidth/innerHeight, .5, 1400);
camera.position.set(52, 34, -26);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(6, 10, 20);
controls.enableDamping = true; controls.dampingFactor = .06;
controls.minDistance = 16; controls.maxDistance = 210;
controls.maxPolarAngle = 1.52;
controls.autoRotateSpeed = -.32;

const SUN = new THREE.DirectionalLight(0xfff3df, 2.2);
SUN.castShadow = true;
SUN.shadow.mapSize.set(2048,2048);
SUN.shadow.camera.left=-78; SUN.shadow.camera.right=78;
SUN.shadow.camera.top=78;  SUN.shadow.camera.bottom=-78;
SUN.shadow.camera.near=1;  SUN.shadow.camera.far=320;
SUN.shadow.bias=-.0007; SUN.shadow.normalBias=.5;
scene.add(SUN, SUN.target);
SUN.target.position.set(6,6,20);

const HEMI = new THREE.HemisphereLight(0x6d7ea8, 0x3f3a44, .5);
scene.add(HEMI);
const AMB  = new THREE.AmbientLight(0x24384f, .35); scene.add(AMB);
const TOWER = new THREE.PointLight(0xffd08a, 0, 130, 2); scene.add(TOWER);
const DUCK = new THREE.PointLight(0xffb96b, 0, 70, 2);  DUCK.position.set(12,11,36);

/* ══════════════════════════════════════════════════════════
   2 · sky dome
   ══════════════════════════════════════════════════════════ */
const skyU = {
  topColor:{value:new THREE.Color(0x2b3f6b)},
  horizonColor:{value:new THREE.Color(0xf07a4e)},
  glowColor:{value:new THREE.Color(0xffdca8)},
  sunDir:{value:new THREE.Vector3(.9,.12,.3)},
  glowPower:{value:.7}
};
const sky = new THREE.Mesh(
  new THREE.SphereGeometry(430, 34, 18),
  new THREE.ShaderMaterial({
    uniforms:skyU, side:THREE.BackSide, depthWrite:false, fog:false,
    vertexShader:`varying vec3 vD; void main(){ vD=position; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
    fragmentShader:`
      varying vec3 vD; uniform vec3 topColor,horizonColor,glowColor,sunDir; uniform float glowPower;
      void main(){
        vec3 d=normalize(vD);
        float t=pow(clamp(d.y,0.,1.),.42);
        vec3 col=mix(horizonColor, topColor, t);
        float g=pow(max(dot(d,normalize(sunDir)),0.),7.);
        col+=glowColor*g*glowPower;
        col=mix(col,horizonColor,smoothstep(.16,0.,d.y)*.55);
        gl_FragColor=vec4(col,1.);
      }`
  }));
sky.renderOrder = -2; scene.add(sky);

const sunOrb = new THREE.Mesh(new THREE.SphereGeometry(13,16,16),
  new THREE.MeshBasicMaterial({color:0xffe9c0, fog:false, transparent:true, opacity:.95}));
sunOrb.renderOrder=-1; scene.add(sunOrb);

/* ══════════════════════════════════════════════════════════
   3 · voxel builder
   ══════════════════════════════════════════════════════════ */
const matCache = new Map(); const windowMats = [];
function matFor(hex){
  if(matCache.has(hex)) return matCache.get(hex);
  const m = new THREE.MeshStandardMaterial({color:hex, roughness:.84, metalness:.04, flatShading:true});
  if(EMISSIVE[hex]){ m.emissive=new THREE.Color(hex); m.emissiveIntensity=EMISSIVE[hex]; windowMats.push(m); }
  matCache.set(hex,m); return m;
}
class VB{
  constructor(){ this.map=new Map(); this.n=0; }
  add(x,y,z,c,sx=1,sy=1,sz=1){
    let e=this.map.get(c); if(!e){e={c,list:[]};this.map.set(c,e);}
    e.list.push([x,y,z,sx,sy,sz]); this.n++;
  }
  box(x0,y0,z0,x1,y1,z1,c){
    this.add((x0+x1)/2,(y0+y1)/2,(z0+z1)/2, c, x1-x0, y1-y0, z1-z0); this.n++;
  }
  build(parent, meta){
    const meshes=[];
    this.map.forEach(e=>{
      const m=new THREE.MeshStandardMaterial();
      const mat=matFor(e.c);
      const im=new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1), mat, e.list.length);
      im.castShadow=true; im.receiveShadow=true;
      const mtx=new THREE.Matrix4();
      e.list.forEach((v,i)=>{ mtx.compose(new THREE.Vector3(v[0],v[1],v[2]),
        new THREE.Quaternion(), new THREE.Vector3(v[3],v[4],v[5])); im.setMatrixAt(i,mtx); });
      im.instanceMatrix.needsUpdate=true; im.computeBoundingSphere();
      im.userData=Object.assign({color:e.c}, meta||{});
      im.userData.list=e.list;
      parent.add(im); meshes.push(im);
    });
    return meshes;
  }
}
const groups={};
function buildGroup(name, vb, parent, meta){
  const g=new THREE.Group(); g.name=name;
  vb.build(g, meta);
  (parent||scene).add(g); groups[name]=g; return g;
}

/* ══════════════════════════════════════════════════════════
   4 · geography
   ══════════════════════════════════════════════════════════ */
const BASIN = {x0:-14, x1:42, z0:14, z1:36};
const isBasin=(x,z)=> x>=BASIN.x0 && x<=BASIN.x1 && z>=BASIN.z0 && z<=BASIN.z1;
function groundTop(x,z){
  if (z < 12) return -3;
  if (isBasin(x,z)) return -3;
  const d = Math.max(0, z-16);
  const n = fbm(x*.055+40, z*.055+11);
  let y = 6.2 + d*.052 + n*4.6 + Math.max(0,x-8)*.012 + Math.max(0,-x-16)*.01;
  if (x>26 && z>40) y += 3.2;
  if (x<-30 && z>30) y += 1.6;
  return clamp(Math.round(y*2)/2, 5.5, 15);
}
function inRect(x,z,x0,z0,x1,z1){return x>=x0&&x<=x1&&z>=z0&&z<=z1;}

const vLand=new VB();
for(let x=-58; x<=58; x+=2){
  for(let z=12; z<=58; z+=2){
    if(isBasin(x,z)) continue;
    const top=groundTop(x,z);
    const stony = z<16.5;
    for(let y=top; y>top-3; y-=1){
      let c;
      if(y===top){
        if(stony) c = (hash(x,z)>.55)?P.stone:P.stoneDark;
        else{
          const n=fbm(x*.09,z*.09);
          c = top>11.5 ? (n>.5?P.slate:P.stoneDark)
            : (n>.62?P.grassLit : n>.34?P.grass : P.grassDark);
          if(x>44 && z<22) c = P.shingle;
        }
      } else c = (top>11? P.slate : P.dirt);
      vLand.add(x,y-.5,z,c,2,1,2);
    }
  }
}
vLand.box(-58,0,12,58,-4.2,58,P.dirt);           // earth core
// seawall face along z = 12
for(let x=-58;x<=58;x+=2) vLand.add(x, 1.5, 11.4, (hash(x,7)>.5?P.stone:P.stoneDark), 2, 8, 1.2);

/* ── quays ringing the basin ─────────────────────────── */
const vQuay=new VB();
function quay(x0,z0,x1,z1){
  vQuay.box(x0,6.1,z0,x1,1.1,z1, P.stoneLit);
  vQuay.box(x0,1.1,z0,x1,-4.2,z1, P.stoneDark);
  for(const bx of [x0+.5, x1-.5]) for(let bz=z0+.5; bz<z1; bz+=2.4)
    vQuay.add(bx, 4.2, (bz+z1)/2-.25, P.stone, .9, 6, Math.max(.9,(z1-bz)/2));
}
quay(BASIN.x0,12.0, BASIN.x1,14.0);              // north quay
quay(42,14.0, 44,40);                            // east quay
quay(-20,36.0, 44,40.4);                         // far quay (the wharf)
quay(-18,14.0, -14,36);                          // west quay
// wharf planking + steps
for(let x=-19;x<=43;x+=2) vQuay.add(x,6.75,37.1, P.plank, 2,.35,2.1);
for(let x=-19;x<=43;x+=2) if(((x+20)/2)%4<2) vQuay.add(x,6.75,35.0, P.plankLt, 2,.35,1.6);
for(let x=-4;x<=2;x+=2){ vQuay.add(x,5.9,35.4,P.stoneLit,2,.6,1.4); vQuay.add(x,5.1,36.1,P.stone,2,.6,1.4); }
// north-quay steps to the water
for(let x=16;x<=22;x+=2){ vQuay.add(x,5.9,13.4,P.stoneLit,2,.6,1.2); vQuay.add(x,4.9,12.7,P.stone,2,.6,1.2); }
// jetties flanking the entrance
vQuay.box(-14,6.1,8, -8,1.1,14, P.stone); vQuay.box(-14,1.1,8, -8,-4,14, P.stoneDark);
vQuay.box( 2,6.1,8,  8,1.1,14, P.stone); vQuay.box(  2,1.1,8,  8,-4,14, P.stoneDark);
buildGroup('quay', vQuay, scene, {kind:'quay', label:'The Wharf',
  sub:'Ashlar granite, rebuilt 1841. Every bollard is rated for a six-masted barque.'});

/* ── breakwater / groyne field ───────────────────────── */
const vGroynes=new VB();
for(let x=-58;x<=-18;x+=2){
  const zc = 16.5 + Math.sin(x*.22)*1.6;
  const h = 4.2 + fbm(x*.13,9)*2.4;
  vGroynes.add(x, (h-3)/2, zc, P.stoneDark, 2.2, h+3, 3.4);
  vGroynes.add(x, h-.3, zc+.4, (hash(x,3)>.5?P.stone:P.stoneLit), 2, .8, 3);
}
vGroynes.box(-58,-4,14, -18,-1.5,19, P.stoneDark);
buildGroup('groynes', vGroynes, scene, {kind:'groynes', label:'Groyne Field',
  sub:'Rubble pitched by hand; the seas that spill over it keep the roads clear of sand.'});

/* ── lighthouse on the point ─────────────────────────── */
const LX=-18, LZ=17, LB=6;
const vLight=new VB();
for(let x=LX-8;x<=LX+8;x+=2) for(let z=LZ-8;z<=LZ+8;z+=2){
  const d=Math.hypot((x-LX)/9,(z-LZ)/9);
  if(d>1) continue;
  const h=LB+2.2*(1-d*d)+fbm(x*.3,z*.3)*1.4;
  vLight.add(x,(h-LB)/2+LB,z,P.stoneDark,2,h-LB+3,2);
  if(hash(x,z)>.62) vLight.add(x,h+.3,z,P.stone,1.4,.8,1.4);
}
const TOPY=LB+22;
for(let y=LB;y<TOPY;y+=1){
  const r = y<LB+1?3.2 : clamp(3.2-(y-LB-1)*.085,1.55,3.2);
  const c = ((y-LB)%6)<3 ? P.ltRed : P.ltWhite;
  const rr = Math.ceil(r);
  for(let x=-rr;x<=rr;x++) for(let z=-rr;z<=rr;z++){
    const d=Math.hypot(x,z);
    if(d<=r+.15) vLight.add(LX+x, y+.5, LZ+z, (d>r-.5&&hash(x+y,z)>.55)?P.ltWhite:c, 1,1,1);
  }
}
vLight.box(LX-2.6, TOPY+.5, LZ-2.6, LX+2.6, TOPY+1.2, LZ+2.6, P.iron);       // gallery
for(let a=0;a<8;a++){const t=a/8*Math.PI*2;
  vLight.add(LX+Math.cos(t)*1.5, TOPY+2.2, LZ+Math.sin(t)*1.5, P.glass, 1.1,1.4,1.1);}
vLight.box(LX-1.7, TOPY+1.4, LZ-1.7, LX+1.7, TOPY+3.1, LZ+1.7, P.iron);      // lantern frame
vLight.add(LX, TOPY+2.25, LZ, 0xfff2cf, 2.1,1.7,2.1);
vLight.add(LX, TOPY+3.7, LZ, P.iron, 2.6,1.1,2.6);
vLight.add(LX, TOPY+4.6, LZ, P.iron, 1,.9,1);
vLight.add(LX+3.4, LB+4, LZ, P.wallW, 3.6,4,4);
vLight.add(LX+3.4, LB+6.4, LZ, P.roofRed, 4.2,1,4.8);
vLight.add(LX+3.4, LB+2.2, LZ+1.1, P.glass, 1.1,1.1,.4);
buildGroup('lighthouse', vLight, scene, {kind:'lighthouse', label:'Harbor Light · 24 m',
  sub:'Fixed red on white, one flash every fifteen seconds. The keeper still winds the clockwork by hand.'});
TOWER.position.set(LX, TOPY+2.2, LZ);

/* rotating beam */
const beamG = new THREE.Group(); beamG.position.set(LX, TOPY+2.2, LZ); scene.add(beamG);
for(const s of [0, Math.PI]){
  const cone = new THREE.Mesh(new THREE.ConeGeometry(9, 78, 18, 1, true),
    new THREE.MeshBasicMaterial({color:0xffe6bb, transparent:true, opacity:.10,
      blending:THREE.AdditiveBlending, depthWrite:false, side:THREE.DoubleSide, fog:true}));
  cone.rotation.z = Math.PI/2; cone.position.x = 39*Math.sign(s===0?1:-1)*0;
  cone.position.set(Math.cos(s)*39, 0, Math.sin(s)*39);
  cone.rotation.y = -s + Math.PI/2; cone.rotation.z = Math.PI/2;
  cone.renderOrder = 3;
  const holder=new THREE.Group(); holder.add(cone); cone.position.set(39,0,0); cone.rotation.set(0,0,Math.PI/2);
  holder.rotation.y = s; beamG.add(holder);
}

/* ══════════════════════════════════════════════════════════
   5 · town
   ══════════════════════════════════════════════════════════ */
const vTown=new VB(), lamps=[], flags=[];
function roof(yb, x0,z0,x1,z1, rc, ridgeX=true){
  const w = ridgeX ? (x1-x0) : (z1-z0), steps=Math.ceil(w/2);
  const hgt=Math.max(1.6, steps*1.05);
  const h=Math.ceil(hgt);
  for(let i=0;i<h;i++){
    const y = yb + hgt - i + .4;
    if(ridgeX){
      const inset = i*Math.max(1,Math.floor(w/2)/ (h));
      vTown.box(x0+inset, y, z0, x1-inset, y+.4, z1, rc);
    } else {
      const inset = i*Math.max(1,Math.floor(w/2)/ (h));
      vTown.box(x0, y, z0+inset, x1, y+.4, z1-inset, rc);
    }
  }
  vTown.box(x0-.7, yb+hgt+.4, z0, x1+.7, yb+hgt+.9, z1, P.wallC);
}
function gableWindows(yb,y1,zc){
  for(let y=yb+2.4;y<y1-1;y+=3) vTown.add(3.7, y, zc, P.glass, .4,1.1,1.1);
}
function house(cx,cz,w,d,h,wc,rc,ridgeX=true,roofY){
  const gy=groundTop(cx,cz), y0=(roofY!==undefined)?roofY:gy-.5;
  vTown.box(cx-w/2,y0,cz-d/2,cx+w/2,y0+h,cz+d/2,wc);
  const zr=ridgeX?1.05:.6, zx=ridgeX?.6:1.05;
  roof(y0+h, cx-w/2+zx, cz-d/2+zr, cx+w/2-zx, cz+d/2-zr, rc, ridgeX);
  // door on the sea side
  vTown.box(cx-1,y0,cz-d/2-.1,cx+1,y0+2.6,cz-d/2+.5,P.oakDk);
  vTown.add(cx,y0+3.1,cz-d/2-.1,P.glass,1.3,.5,.3);
  for(let x=cx-w/2+1.5;x<=cx+w/2-1.5;x+=3){
    for(let y=y0+3.4;y<y0+h-1.2;y+=3){
      vTown.add(x,y,cz-d/2-.12,P.glass,1.2,1.4,.35);
      vTown.add(x,y,cz+d/2+.12,P.glass,1.2,1.4,.35);
      vTown.add(x-.5-w/2,y,cz,P.glass,.35,1.4,1.2);
      vTown.add(x-.5+w/2,y,cz,P.glass,.35,1.4,1.2);
    }
  }
  // chimney
  vTown.box(cx+w/2-3,y0+h*.55,cz+1,cx+w/2-1.6,y0+h+2.4,cz+2.4,P.stoneDark);
  return {cx,cz,y0,h};
}
function lamp(cx,cz,y,arm){
  vTown.add(cx,y+3.6,cz,P.iron,.34,7.2,.34);
  vTown.add(cx,y+7.4,cz,P.ironLt,.9,.3,.9);
  vTown.add(cx,y+8.2,cz,P.lamp,.95,1.1,.95);
  vTown.add(cx,y+9,cz,P.iron,1.1,.35,1.1);
  if(arm){ vTown.add(cx+arm/2,y+6.4,cz,P.iron,Math.abs(arm),.3,.3);
    vTown.add(cx+arm,y+5.8,cz,P.lamp,.8,1,.8); }
  lamps.push({x:cx,y:y+8.2,z:cz,ph:rnd()*9});
}
function flagpole(cx,cz,y,hgt,c1,c2){
  vTown.add(cx,y+hgt/2,cz,P.ironLt,.32,hgt,.32);
  vTown.add(cx,y+hgt+.4,cz,P.gold,.5,.7,.5);
  flags.push({x:cx,y:y+hgt-1.4,z:cz,w:6,h:3,c1,c2});
}

/* warehouse row on the wharf */
house(2,38.6, 13,9, 7.2, P.wallW, P.roofRed, true);
house(15,38.8, 11,8, 5.6, P.wallC, P.roofSl, false);
house(27,38.8, 12,9, 8.2, P.wallB, P.roofSl, true);
house(38,38.6,  9,8, 5.2, P.wallG, P.roofRed, false);
/* custom house, two storeys up on the north quay */
house(29,11.0, 14,8, 6.4, P.wallW, P.roofSl, true);
flagpole(29, 11, 6.2+6.4+4, 7, P.flagRed, P.gold);
/* customs shed + chandlery on the north quay */
house(6,11.2, 10,7, 4.4, P.wallO, P.roofRed, false);
house(-6,11.2, 9,6, 3.6, P.wallC, P.roofSl, false);
/* town climbing the hill */
house(-26,26,10,9,6,P.wallW,P.roofRed,true, groundTop(-26,26)-.5);
house(-12,29,9,8,5,P.wallC,P.roofGr,true, groundTop(-12,29)-.5);
house(2,31,11,9,7,P.wallB,P.roofSl,true, groundTop(2,31)-.5);
house(16,27.5,8,7,4.4,P.wallW,P.roofRed,true, groundTop(16,27.5)-.5);
house(30,27,10,8,6,P.wallO,P.roofSl,true, groundTop(30,27)-.5);
house(-18,40,9,8,5,P.wallC,P.roofRed,true, groundTop(-18,40)-.5);
house(-4,43,10,9,6.4,P.wallW,P.roofSl,true, groundTop(-4,43)-.5);
house(10,44,9,8,5,P.wallG,P.roofRed,true, groundTop(10,44)-.5);
house(24,42,11,9,7,P.wallB,P.roofSl,true, groundTop(24,42)-.5);
house(-30,34,8,7,4.4,P.wallW,P.roofGr,true, groundTop(-30,34)-.5);
house(36,33,8,7,4,P.wallP,P.roofSl,true, groundTop(36,33)-.5);
/* church on the rise */
{
  const cx=-40, cz=44, gy=groundTop(cx,cz)-.5;
  vTown.box(cx-9,gy,cz-6,cx+9,gy+8,cz+6,P.stoneLit);
  roof(gy+8, cx-8, cz-5, cx+8, cz+5, P.roofSl, false);
  vTown.box(cx+7,gy,cz-4,cx+11,gy+13,cz+4,P.stone);
  roof(gy+13, cx+6.4, cz-4.6, cx+11.6, cz+4.6, P.roofRed, false);
  vTown.add(cx+9,gy+9,cz,P.glass,.5,2.4,2.4);
  vTown.add(cx+9,gy+11.6,cz,P.glass,.5,1.4,1.4);
  vTown.add(cx,gy+10,cz-6.1,P.glass,3,2.4,.4);
  vTown.add(cx-5,gy+3,cz-6.1,P.oakDk,3,3,.5);
}
/* fort on the east headland */
{
  const gy=groundTop(44,48)-.5;
  vTown.box(34,gy,42,54,gy+5.4,54,P.stoneLit);
  vTown.box(35,gy+5.4,43,53,gy+6,53,P.stone);
  for(const tx of [34,54]) for(const tz of [42,54]){
    vTown.box(tx-2.6,gy,tz-2.6,tx+2.6,gy+9,tz+2.6,P.stone);
    vTown.box(tx-3,gy+9,tz-3,tx+3,gy+9.6,tz+3,P.stoneDark);
    for(let i=0;i<4;i++) vTown.add(tx-2.4+i*1.6, gy+10.2, tz, P.stoneDark,1.2,.9,1.2);
    flagpole(tx, tz, gy+9.6, 5, P.flagRed, P.flagBl);
  }
  vTown.box(42,gy,41.4,46,gy+3.4,42.6,P.oakDk);
  for(let x=34.6;x<=53;x+=2) vTown.add(x, gy+6.2, 41.9, P.stoneDark, 1.2,.9,1.2);
}
/* windmill */
const millPivot=new THREE.Group();
{
  const cx=-46, cz=30, gy=groundTop(cx,cz)-.5;
  for(let i=0;i<9;i++){ const r=3.4-i*.24, rr=Math.ceil(r);
    for(let x=-rr;x<=rr;x++) for(let z=-rr;z<=rr;z++)
      if(Math.hypot(x,z)<=r+.2) vTown.add(cx+x, gy+i+.5, cz+z, i%2?P.wallW:P.wallC,1,1,1); }
  vTown.add(cx, gy+9.6, cz, P.roofRed, 5,1.4,5);
  millPivot.position.set(cx, gy+8.2, cz-3.4);
  vTown.add(cx, gy+8.2, cz-3.2, P.oakDk, 1.6,1.6,1.6);
}
/* street furniture */
for(const [lx,lz] of [[-8,35.4],[-1,35.4],[6,35.4],[13,35.4],[20,35.4],[27,35.4],[34,35.4],[41,35.4],
  [8,13.4],[16,13.4],[24,13.4],[36,13.4],[-16,20],[-16,30],[43,22],[43,31]])
  lamp(lx,lz,6.6, lz>30?2:-2);
buildGroup('town', vTown, scene, {kind:'town', label:'Old Town',
  sub:'Fourteen hundred roofs, all of them watching the same mouth of the harbor.'});
scene.add(millPivot);

/* animated flag meshes */
const flagMeshes=[];
flags.forEach(f=>{
  const vb=new VB();
  for(let x=0;x<f.w;x++) for(let y=0;y<f.h;y++)
    vb.add(f.x+.7+x, f.y+y, f.z, (y===0||y===f.h-1)?f.c2:f.c1, 1,1,.28);
  const g=new THREE.Group(); const ms=vb.build(g,{kind:'flag',label:'Ensign',
    sub:'Striped red and gold: the harbor authority pays the flag dues every January.'});
  g.position.set(0,0,0); scene.add(g);
  flagMeshes.push({ms, list:vb.map.get(f.c1).list.concat(vb.map.get(f.c2).list), f});
});

/* ══════════════════════════════════════════════════════════
   6 · dockside props
   ══════════════════════════════════════════════════════════ */
const vProps=new VB();
function crate(x,y,z,s=1.6,c=P.crate){
  vProps.add(x,y+s/2,z,c,s,s,s);
  vProps.add(x,y+s/2,z+s/2+.02,P.plankDk,s*.8,.24,.1);
  vProps.add(x,y+s/2,z+s/2+.02,P.plankDk,.24,s*.8,.1);
}
function barrel(x,y,z,c=P.barrel){
  vProps.add(x,y+.9,z,c,1.6,1.8,1.6);
  vProps.add(x,y+.45,z,P.ironLt,1.75,.24,1.75);
  vProps.add(x,y+1.35,z,P.ironLt,1.75,.24,1.75);
  vProps.add(x,y+1.85,z,P.plankLt,1.3,.2,1.3);
}
function bollard(x,z){
  vProps.add(x,7.3,z,P.iron,.9,1.4,.9);
  vProps.add(x,8.15,z,P.ironLt,1.3,.5,1.3);
}
function coil(x,z){
  for(let a=0;a<10;a++){const t=a/10*Math.PI*2;
    vProps.add(x+Math.cos(t)*1.15,7.0,z+Math.sin(t)*1.15,P.rope,1.1,.3,1.1);}
  vProps.add(x,7.05,z,P.rope,1.5,.35,1.5);
}
function bench(x,z,r=0){
  vProps.add(x,7.1,z,P.plankLt,4.4,.3,1.2);
  vProps.add(x,7.6,z-.55,P.plankLt,4.4,1.1,.3);
  vProps.add(x-1.8,6.75,z,P.oakDk,.4,1.2,1.2);
  vProps.add(x+1.8,6.75,z,P.oakDk,.4,1.2,1.2);
}
function fishStall(x,z){
  vProps.add(x,7.6,z,P.plank,6,.3,3.4);
  for(const s of [[-1,0],[1,0]]) vProps.add(x+s[0]*2.6,6.85,z,P.oakDk,.5,1.6,.5);
  for(let i=-2;i<=2;i++){ vProps.add(x+i*1.1,7.95,z-.6,P.seaLit,1,.35,1.7);
    vProps.add(x+i*1.1,7.95,z+1.1,P.seaTop,1,.35,1.7); }
  vProps.add(x,9.4,z,P.creamDk,7.2,.4,4.4);
  for(const s of [-1,1]) vProps.add(x+s*3,8.6,z,P.plankDk,.4,1.6,.4);
}
function cart(x,z){
  vProps.add(x,8.1,z,P.plank,5,1.2,2.4);
  vProps.add(x-2.6,8.6,z-.9,P.plankDk,.4,1.2,2.4);
  vProps.add(x-2.6,8.4,z-1.6,P.plank,3,.3,.3);
  for(const s of [[-1.6,-1.3],[-1.6,1.3],[1.7,-1.3],[1.7,1.3]])
    vProps.add(x+s[0],6.9,z+s[1],P.oakDk,1.7,.4,1.7);
}
function derrick(x,z){
  vProps.add(x,9.4,z,P.oakDk,1.1,5.4,1.1);
  for(const s of [[1,0],[-1,0],[0,1],[0,-1]])
    vProps.add(x+s[0]*1.3,7.1,z+s[1]*1.3,P.ironLt,.3,1.4,.3);
  vProps.add(x+3.4,12,z,P.plank,7,.7,.7);
  vProps.add(x+6.6,11.2,z,P.iron,.4,1.6,.4);
  vProps.add(x+6.6,10.1,z,P.crate,1.9,1.9,1.9);
  vProps.add(x,12.3,z,P.ironLt,.7,.7,.7);
}
/* wharf line */
for(let x=-16;x<=42;x+=5.6) bollard(x,35.2);
[[ -13,37.4],[-9.4,38.2],[-6,37.2],[34,37.6],[37.6,38.2],[41,37.2]].forEach(([x,z])=>{
  crate(x,6.9,z,1.7); crate(x+.1,8.6,z,1.1); });
[[19,37.8],[22.4,38.4],[25.6,37.4],[31,37.8]].forEach(([x,z])=>barrel(x,6.9,z));
[[12,38.4],[15,37.2]].forEach(([x,z])=>{barrel(x,6.9,z,P.oakLt);crate(x+1.9,6.9,z,1.4);});
[[8,13.4],[-16,35],[26,13.4],[40,35]].forEach(([x,z])=>coil(x,z));
bench(23,13.6); bench(-9,35.2,0); bench(31,13.6);
fishStall(17,39.2); cart(-3,37.4); derrick(41,32);
/* rowboats on the shingle */
for(const [bx,bz,rot] of [[48,20,.5],[52,25,-.3],[50,31,.9]]){
  const gy=groundTop(bx,bz);
  vProps.add(bx,gy+1,bz,P.plankLt,6.4,1.1,2.6);
  vProps.add(bx,gy+1.6,bz,P.plankDk,5.4,.5,1.6);
  vProps.add(bx,gy+1.9,bz,P.plank,1.4,.3,2.2);
  vProps.add(bx-3.6,gy+1.4,bz,P.plankLt,.9,.9,.9);
}
/* jetty lanterns */
for(const [jx,jz] of [[-11,11],[5,11]]){
  vProps.add(jx,7.6,jz,P.oakDk,.7,3,.7);
  vProps.add(jx,9.4,jz,P.glass,1.1,1.2,1.1);
  vProps.add(jx,10.2,jz,P.iron,1.4,.4,1.4);
  lamps.push({x:jx,y:9.4,z:jz,ph:rnd()*7});
}
/* basin mooring rings + a coaling stage */
for(let x=-12;x<=40;x+=9) vProps.add(x,6.9,14.6,P.ironLt,1.4,.5,1.4);
vProps.box(36,6.1,17,40,10.5,19,P.plankDk);
vProps.box(35,10.5,16.6,41,11.1,19.4,P.plank);
for(let x=36;x<=40;x+=2) vProps.add(x,6.6,17.8,P.oakDk,.8,1,2);
vProps.box(36,11.1,17,40,13.6,18.4,P.coal||P.iron);
buildGroup('props', vProps, scene, {kind:'props', label:'Cargo',
  sub:'Casks, crates and cod — the ledger of a small harbor written in wood.'});

/* ══════════════════════════════════════════════════════════
   7 · the barque “Meridian”
   ══════════════════════════════════════════════════════════ */
const SHIP = new THREE.Group();
SHIP.position.set(10, 0, 24.6);
SHIP.rotation.y = Math.PI/2 - .42;    // beam toward the wharf, bow to the northeast
scene.add(SHIP);
const vShip=new VB(), rig=[];

const hullHalf=x=>3.7*(1-.86*Math.pow(Math.abs(x/17.5),4))+.34;
const sheer=x=>3.1+1.55*Math.pow(Math.abs(x/17.5),2.4)+(x>0?.95*Math.pow(x/17.5,2):0);

for(let x=-17;x<=17;x++){
  const hb=Math.round(hullHalf(x)*10)/10, dk=Math.round(sheer(x)*10)/10;
  const bowTaper=Math.max(0,(x-13)/4);
  for(let y=-1.6;y<=dk;y++){
    for(let z=-Math.ceil(hb);z<=Math.ceil(hb);z++){
      const zz=Math.abs(z);
      const hEdge = zz>hb-.65, inner = zz<hb-.9;
      if(zz>hb) continue;
      if(y<0 && inner) continue;
      if(y>0 && inner && y<dk-.9) continue;
      let c;
      if(y<.35) c=P.hullRed;
      else if(y<2.05) c=(y>=1.55&&y<1.95)?P.gold:P.hullBlk;
      else c=(hash(x,y)>.72)?P.oakLt:P.oak;
      if(hEdge && y>dk-.9) c=P.plankLt;
      vShip.add(x,y,zz*(hb-Math.round(hb))+z*0+ (z>0?hb:0)*0 + z*(hb/Math.max(hb,1))*0 + z, c, 1,1,1);
    }
  }
  // deck & bulwark
  vShip.add(x, dk+.1, 0, P.plank, 1, .35, Math.max(1,hb*2-.6));
  for(const s of [-1,1]){
    const zz=(hb-.25)*s;
    vShip.add(x, dk+.65, zz, P.plankLt, 1,.85,.42);
    if(((x+20)%4)<2) vShip.add(x, dk+1.25, zz, P.plankDk, .5,.5,.42);
  }
  // gunports
  if(((x+18)%3)===0 && x>-14 && x<14 && dk<5.2){
    for(const s of [-1,1]) vShip.add(x,2.6,s*(hb+.02),P.gold,1.15,1.15,.4);
  }
}
/* sterncastle + quarter gallery */
vShip.box(-16,4.9,-3.1,-10.5,6.9,3.1,P.oak);
vShip.box(-15.4,6.9,-2.6,-11,7.15,2.6,P.plankLt);
for(const s of [-1,1]) vShip.box(-16.4,3.6,s*3.4,-15.9,6.4,s*3.9,P.plankLt);
for(let y=5.4;y<6.6;y+=1.1) vShip.add(-16.2,y,0,P.glass,1.1,1.1,.4);
for(let z=-2.4;z<=2.4;z+=1.4) vShip.add(-10.6,y=5.4,z,P.glass,.4,1.1,1.1);
vShip.add(-16.6,6.4,0,P.gold,1,1.6,4.4);
/* forecastle */
vShip.box(11,4.4,2.7,15.4,5.4,-2.7,P.oak);
vShip.box(10.6,5.4,2.9,15.8,5.65,-2.9,P.plankLt);
/* boats, coals, cargo on deck */
vShip.add(-6,7.5,0,P.plankLt,5.6,1.1,2.2);
vShip.add(-6,8.2,0,P.plankDk,4.6,.5,1.3);
vShip.add(2,5.9,0,P.crate,1.7,1.7,1.7);
vShip.add(2,7.7,0,P.crate,1.3,1.3,1.3);
vShip.add(4.4,5.9,.9,P.barrel,1.4,1.6,1.4);
vShip.add(4.4,5.9,-.9,P.barrel,1.4,1.6,1.4);
for(const s of [-1,1]) vShip.add(7,5.6,s*2,P.creamDk,2.2,.9,1.4);
/* bowsprit + jib boom */
for(let i=0;i<17;i++) vShip.add(16+i, 4.4+i*.34, 0, i<11?P.oakLt:P.plankLt, 1.1,.95,1.1);
vShip.add(33.4,10.2,0,P.plankLt,.8,.7,.8);
/* figurehead */
vShip.add(17.2,3.4,0,P.gold,1.6,1.6,1.1); vShip.add(17.9,4.4,0,P.gold,.8,.9,.7);
/* masts, tops, yards, sails */
const masts=[{x:-11,h:20,tag:'mizzen'},{x:-1,h:26,tag:'main'},{x:9,h:22,tag:'fore'}];
const sailC=P.sailW, sailS=P.sailS;
masts.forEach((m,mi)=>{
  for(let y=4;y<m.h;y+=1){
    const s=clamp(1.1-(y-4)/m.h*.75,.42,1.1);
    vShip.add(m.x, y+.5, 0, y>m.h-3?P.plankDk:P.plankLt, s,1,s);
  }
  vShip.add(m.x, m.h*.62, 0, P.oakLt, 2.6,1,2.6);
  vShip.add(m.x, m.h+.5, 0, P.ironLt, .6,1.2,.6);
  const yards=[m.h*.34, m.h*.56, m.h*.78, m.h*.96];
  yards.forEach((yy,i)=>{
    const w=Math.round((m.h*.56-i*m.h*.12));
    vShip.add(m.x, yy, 0, P.oakDk, 1,.8,w*2);
    for(const s of [-1,1]) vShip.add(m.x, yy, s*w, P.ironLt,.9,.9,.9);
    if(i<3){
      const y2=yards[i+1], hgt=Math.round((y2-yy)*10)/10;
      const bill = 1.35+i*.28, col = (i===1)?sailS:sailC;
      vShip.add(m.x+bill, (yy+y2)/2-.35, 0, col, 1.05, hgt-1.1, w*2-1.4);
      for(const s of [-1,1]) vShip.add(m.x+bill+.25, (yy+y2)/2-.35, s*(w-.7), sailS, 1.3,hgt-1.1,.9);
      rig.push([[m.x,yy,-w],[m.x,yy+.6,0]]); rig.push([[m.x,yy,w],[m.x,yy+.6,0]]);
      rig.push([[m.x,yy,-w],[m.x-2.6,4.6,-3]]); rig.push([[m.x,yy,w],[m.x-2.6,4.6,3]]);
      rig.push([[m.x,yy,-w],[m.x+2.6,4.6,-3]]); rig.push([[m.x,yy,w],[m.x+2.6,4.6,3]]);
    }
  });
  // square sails set, braced to the wind
  rig.push([[m.x,m.h+.4,0],[m.x+16,5.4,0]]);
  if(mi>0) rig.push([[m.x,m.h*.94,0],[masts[mi-1].x,masts[mi-1].h*.55,0]]);
  rig.push([[m.x,m.h*.5,0],[m.x-9,5.2,0]]);
});
/* headsails: triangular stacks from bowsprit to foremast */
function tri(x0,y0,x1,y1,z0,z1,col,thick=1.05){
  for(let x=Math.ceil(x0);x<=Math.floor(x1);x++){
    const t=(x-x0)/(x1-x0);
    const top=y0+(y1-y0)*t, bot=lerp(y0,y0-1.9,t)+ (z1>0?0:0);
    const yb = -1.9 + (x-16)*.34 + .9;
    for(let y=Math.ceil(Math.max(yb+.7,y0-2.6)); y<=Math.floor(top-.5); y++)
      for(let z=z0;z<=z1;z+=.9) vShip.add(x,y,(z0+z1)/2, col, thick, 1, Math.abs(z1-z0)+.9);
  }
}
const lerp=(a,b,t)=>a+(b-a)*t;
tri(17,13.6, 9.2,20.6, -1.1,1.1, P.sailW);
tri(17,13.6, 9.2,20.6, -1.1,1.1, P.sailW);
tri(21,11.6, -1,23,   -1.1,1.1, P.sailS);
tri(27,9.4,  -1,25.6, -1.1,1.1, P.sailW);
rig.push([[17,5,0],[9,13.5,0]]); rig.push([[24,6.8,0],[9,10,0]]);
rig.push([[33.4,10.2,0],[9,21.5,0]]);
/* spanker (fore–aft) on the mizzen */
for(let y=8;y<15;y++) vShip.add(-11.5, y, 0, (y%3===0)?P.sailS:P.sailW, 1, 1, 5.6-(y-8)*.3);
vShip.add(-11,11.4,3.4,P.oakDk,1,.7,7.2);
vShip.add(-11,14.6,2.4,P.oakDk,1,.7,4.2);
/* rigging lines */
const rpos=[], rcol=[]; const cLine=new THREE.Color(0x2a2b30);
rig.forEach(([a,b])=>{
  const steps=8;
  for(let i=0;i<steps;i++){
    const t0=i/steps, t1=(i+1)/steps;
    rpos.push(lerp(a[0],b[0],t0),lerp(a[1],b[1],t0),lerp(a[2],b[2],t0),
              lerp(a[0],b[0],t1),lerp(a[1],b[1],t1),lerp(a[2],b[2],t1));
    rcol.push(cLine.r,cLine.g,cLine.b,cLine.r,cLine.g,cLine.b);
  }
});
const rGeo=new THREE.BufferGeometry();
rGeo.setAttribute('position', new THREE.Float32BufferAttribute(rpos,3));
rGeo.setAttribute('color', new THREE.Float32BufferAttribute(rcol,3));
SHIP.add(new THREE.LineSegments(rGeo, new THREE.LineBasicMaterial({vertexColors:true, transparent:true, opacity:.75})));

/* shrouds as tubes for a chunkier voxel look */
masts.forEach(m=>{
  for(const s of [-1,1]){
    const g=new THREE.TubeGeometry(new THREE.CatmullRomCurve3([
      new THREE.Vector3(m.x, m.h*.62, s*1.4),
      new THREE.Vector3(m.x-2.2, 5.0, s*(hullHalf(m.x)+.2)),
      new THREE.Vector3(m.x+2.2, 5.0, s*(hullHalf(m.x)+.2))
    ]), 16, .11, 4, false);
    SHIP.add(new THREE.Mesh(g, matFor(P.rope)));
  }
});
const shipMeshes = vShip.build(SHIP, {kind:'ship', label:'The Meridian',
  sub:'Three-masted barque, 312 tons. Outward with salt and tin, homeward with everything else.'});
/* ship flags */
const shipFlags=[];
masts.forEach((m,i)=>{
  const vb=new VB();
  const c1=[P.flagRed,P.flagBl,P.flagY][i], c2=P.white;
  for(let x=0;x<5;x++) for(let y=0;y<3;y++)
    vb.add(m.x+.7+x, m.h+.5+y, 0, (y===1)?c1:c2, 1,1,.26);
  const g=new THREE.Group(); vb.build(g,{kind:'flag',label:'Mast flag',
    sub:'Coded by the harbour master’s board: “seeking a berth, two days water left.”'});
  SHIP.add(g); shipFlags.push({list:vb.map.get(c1).list.concat(vb.map.get(c2).list), g});
});

/* mooring lines from the ship to the wharf bollards (world space) */
function moor(a,b){
  const c=new THREE.QuadraticBezierCurve3(a.clone(),
    new THREE.Vector3((a.x+b.x)/2, Math.min(a.y,b.y)-1.6, (a.z+b.z)/2), b.clone());
  const m=new THREE.Mesh(new THREE.TubeGeometry(c,30,.13,5,false), matFor(P.rope));
  m.castShadow=true; scene.add(m);
}
moor(new THREE.Vector3(24,7,20.5), new THREE.Vector3(20,7.6,35.2));
moor(new THREE.Vector3(24,7,28.7), new THREE.Vector3(26,7.6,35.2));
moor(new THREE.Vector3(-3,7,20.6), new THREE.Vector3(-9,7.6,35.2));
moor(new THREE.Vector3(-3,7,28.6), new THREE.Vector3(-16,7.6,35.2));

/* ══════════════════════════════════════════════════════════
   8 · water (animated)
   ══════════════════════════════════════════════════════════ */
const seaFloor=new THREE.Mesh(new THREE.BoxGeometry(190,1,190),
  new THREE.MeshStandardMaterial({color:0x0d2635, roughness:1}));
seaFloor.position.set(0,-5.6,0); seaFloor.receiveShadow=true; scene.add(seaFloor);

const cols=[];
for(let x=-76;x<=76;x+=2) for(let z=-82;z<=13;z+=2) cols.push({x,z,base:P.seaMid,sea:true});
for(let x=BASIN.x0+1;x<=BASIN.x1-1;x+=2) for(let z=BASIN.z0;z<=BASIN.z1;z+=2) cols.push({x,z,base:P.seaDeep,sea:false});
const wGeo=new THREE.BoxGeometry(1,1,1);
const waterMat=new THREE.MeshStandardMaterial({color:0xffffff, transparent:true, opacity:.9,
  roughness:.16, metalness:.42});
const water=new THREE.InstancedMesh(wGeo, waterMat, cols.length);
water.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
water.receiveShadow=true; water.castShadow=false;
water.userData={kind:'water', label:'The Roads', sub:'Ten fathoms at the entrance, shoaling to four over the bar.'};
const cc=new THREE.Color();
cols.forEach((c,i)=>water.setColorAt(i, cc.setHex(c.base)));
const wDepth=new THREE.MeshDepthMaterial({depthPacking:THREE.RGBADepthPacking,transparent:true,opacity:.85});
water.customDepthMaterial=wDepth;
scene.add(water);
const _p=new THREE.Vector3(), _q=new THREE.Quaternion(), _e=new THREE.Euler(), _s=new THREE.Vector3(1.02,1,1.02);

/* foam collars */
const foam=[];
for(let i=0;i<150;i++){
  const a=rnd()*Math.PI*2;
  if(rnd()<.55) foam.push({x:10+Math.cos(a)*(19+rnd()*7), z:24.6+Math.sin(a)*(7+rnd()*5)});
  else foam.push({x:-18+(rnd()*46-12), z:15+rnd()*4});
}
const foamMesh=new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1),
  new THREE.MeshBasicMaterial({color:0xdff0f2, transparent:true, opacity:.55, depthWrite:false}), foam.length);
foamMesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
scene.add(foamMesh);

/* ══════════════════════════════════════════════════════════
   9 · sky traffic — clouds, gulls, smoke
   ══════════════════════════════════════════════════════════ */
const cloudList=[];
for(let i=0;i<22;i++){
  const n=3+Math.floor(rnd()*4), cubes=[];
  const cx=rnd()*420-210, cy=34+rnd()*22, cz=rnd()*420-210;
  for(let j=0;j<n;j++) cubes.push([rnd()*22-11, rnd()*3-1.5, rnd()*16-8, 8+rnd()*12, 2+rnd()*3, 6+rnd()*9]);
  cloudList.push({cubes, x:cx, y:cy, z:cz, spd:1.1+rnd()*1.6, n});
}
const cloudMesh=new THREE.InstancedMesh(wGeo,
  new THREE.MeshStandardMaterial({color:0xf3d9c4, transparent:true, opacity:.86, roughness:1, fog:true,
    emissive:0x514066, emissiveIntensity:.25}), cloudList.reduce((a,c)=>a+c.n,0));
cloudMesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
scene.add(cloudMesh);

const gulls=[];
for(let i=0;i<7;i++) gulls.push({r:18+rnd()*30, spd:(.16+rnd()*.18)*(rnd()<.5?1:-1),
  ph:rnd()*7, y:20+rnd()*13, cx:8+rnd()*10-5, cz:22+rnd()*10-5, flap:rnd()*7});
const gullMesh=new THREE.InstancedMesh(wGeo,
  new THREE.MeshStandardMaterial({color:0xffffff, roughness:.9, flatShading:true}), gulls.length*4);
gullMesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
const gullC=new THREE.Color();
gulls.forEach((g,i)=>{
  gullMesh.setColorAt(i*4+0, gullC.setHex(P.gull));
  gullMesh.setColorAt(i*4+1, gullC.setHex(P.gull));
  gullMesh.setColorAt(i*4+2, gullC.setHex(P.gull));
  gullMesh.setColorAt(i*4+3, gullC.setHex(P.gullDk));
});
scene.add(gullMesh);
const smokeList=[];
[[-8,13.4,38.6],[2,14.6,38.6],[15,12.4,38.8],[27,15.4,38.8],[38,11.4,38.6],
 [-26,12.4,26],[-12,11.4,29],[2,14.2,31],[16,11.4,27.5],[-4,13.4,43]].forEach(([x,y,z])=>{
  for(let i=0;i<4;i++) smokeList.push({x:x+3.4,y:y,z,off:i/4, sp:.32+rnd()*.2});
});
const smokeMesh=new THREE.InstancedMesh(new THREE.SphereGeometry(.62,6,5),
  new THREE.MeshStandardMaterial({color:0xb9c3cc, transparent:true, opacity:.34, roughness:1, depthWrite:false}),
  smokeList.length);
smokeMesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
scene.add(smokeMesh);
/* lamp glow sprites */
const glowMesh=new THREE.InstancedMesh(new THREE.SphereGeometry(.9,8,6),
  new THREE.MeshBasicMaterial({color:0xffd08a, transparent:true, opacity:.5,
    blending:THREE.AdditiveBlending, depthWrite:false}), lamps.length);
glowMesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
scene.add(glowMesh);

/* ══════════════════════════════════════════════════════════
   10 · time of day
   ══════════════════════════════════════════════════════════ */
const T={
  dawn:  {skyTop:0x3a5c93, hor:0xf2a877, glow:0xffe2bb, gp:.6, fog:0xc2a898, fd:.0072,
          sun:[.86,.13,.34], sunC:0xffb37a, sunI:2.0, hs:0x8fa8cc, hg:0x6b5f4a, hi:.55,
          amb:0x2c3c58, ambI:.42, lamp:.85, win:1.0, exp:1.03, wCol:0x2a6c86, wOp:.9, orb:.7},
  day:   {skyTop:0x3f86c4, hor:0xc2dced, glow:0xfff6e0, gp:.42, fog:0xb9d4e6, fd:.0052,
          sun:[.5,.66,.3], sunC:0xfff7e6, sunI:3.1, hs:0xa6cdec, hg:0x6f8258, hi:.78,
          amb:0x3c5878, ambI:.4, lamp:0, win:.08, exp:1.0, wCol:0x2f8ba6, wOp:.88, orb:.9},
  golden:{skyTop:0x4b7ba8, hor:0xf3b377, glow:0xffdcac, gp:.75, fog:0xe6c69d, fd:.0060,
          sun:[.92,.2,.35], sunC:0xffb066, sunI:3.3, hs:0xbcd2e6, hg:0x7d6b52, hi:.5,
          amb:0x3d4a68, ambI:.4, lamp:.55, win:.9, exp:1.02, wCol:0x2c7f97, wOp:.89, orb:1},
  dusk:  {skyTop:0x2b3f6b, hor:0xf07a4e, glow:0xffd0a0, gp:.9, fog:0x7b6a86, fd:.0066,
          sun:[.95,.09,.3], sunC:0xff8a4a, sunI:2.1, hs:0x6d7ea8, hg:0x3f3a44, hi:.46,
          amb:0x24384f, ambI:.36, lamp:1.25, win:1.7, exp:1.06, wCol:0x24536f, wOp:.9, orb:1},
  night: {skyTop:0x060b1c, hor:0x1b2c4b, glow:0x9fbcе6, gp:.34, fog:0x0c1426, fd:.0084,
          sun:[.36,.52,-.42], sunC:0x9ab8e8, sunI:.72, hs:0x22355c, hg:0x141824, hi:.34,
          amb:0x18263c, ambI:.3, lamp:1.6, win:2.1, exp:1.16, wCol:0x10293e, wOp:.94, orb:.35},
};
T.night.glow = 0x9fbce6;
let cur=null, tgt=null, lerpT=1;
function applyPreset(name, animate){
  const p=T[name];
  const target={
    skyTop:new THREE.Color(p.skyTop), hor:new THREE.Color(p.hor), glow:new THREE.Color(p.glow), gp:p.gp,
    fog:new THREE.Color(p.fog), fd:p.fd, sun:new THREE.Vector3(...p.sun).normalize(),
    sunC:new THREE.Color(p.sunC), sunI:p.sunI, hs:new THREE.Color(p.hs), hg:new THREE.Color(p.hg),
    hi:p.hi, amb:new THREE.Color(p.amb), ambI:p.ambI, lamp:p.lamp, win:p.win, exp:p.exp,
    wCol:new THREE.Color(p.wCol), wOp:p.wOp, orb:p.orb
  };
  if(!cur||!animate){ cur=target; bake(target); lerpT=1; }
  else { tgt=target; lerpT=0; }
}
function bake(c){
  skyU.topColor.value.copy(c.skyTop); skyU.horizonColor.value.copy(c.hor);
  skyU.glowColor.value.copy(c.glow); skyU.glowPower.value=c.gp; skyU.sunDir.value.copy(c.sun);
  scene.fog.color.copy(c.fog); scene.fog.density=c.fd;
  SUN.color.copy(c.sunC); SUN.intensity=c.sunI;
  SUN.position.set(6+c.sun.x*110, c.sun.y*110+6, 20+c.sun.z*110);
  HEMI.color.copy(c.hs); HEMI.groundColor.copy(c.hg); HEMI.intensity=c.hi;
  AMB.color.copy(c.amb); AMB.intensity=c.ambI;
  TOWER.intensity=c.lamp*2.4; DUCK.intensity=c.lamp*.9;
  renderer.toneMappingExposure=c.exp;
  waterMat.color.copy(c.wCol); waterMat.opacity=c.wOp;
  windowMats.forEach(m=>{ m.emissiveIntensity=c.win;
    m.emissive.setHex(m.color.getHex()===P.lamp? P.lamp : P.glass); });
  sunOrb.position.set(c.sun.x*320, c.sun.y*320, c.sun.z*320);
  sunOrb.material.color.copy(c.sunC).lerp(new THREE.Color(0xffffff),.35);
  sunOrb.material.opacity=c.orb;
  cloudMesh.material.color.copy(c.hor).lerp(new THREE.Color(0xffffff),.42);
  cloudMesh.material.emissive.copy(c.fog);
  foamMesh.material.color.copy(c.hor).lerp(new THREE.Color(0xffffff),.6);
  smokeMesh.material.color.copy(c.fog).lerp(new THREE.Color(0xffffff),.42);
}
applyPreset('dusk', false);

/* ══════════════════════════════════════════════════════════
   11 · picking
   ══════════════════════════════════════════════════════════ */
const pickables=[];
scene.traverse(o=>{ if(o.isInstancedMesh) pickables.push(o); });
const ray=new THREE.Raycaster(), mouse=new THREE.Vector2();
const logEl=document.getElementById('log'), logT=document.getElementById('logT'), logB=document.getElementById('logB');
let down=null, timer=null;
renderer.domElement.addEventListener('pointerdown',e=>{down={x:e.clientX,y:e.clientY,t:performance.now()};});
renderer.domElement.addEventListener('pointerup',e=>{
  if(!down) return;
  const d=Math.hypot(e.clientX-down.x, e.clientY-down.y);
  if(d<6 && performance.now()-down.t<600){
    mouse.x=(e.clientX/innerWidth)*2-1; mouse.y=-(e.clientY/innerHeight)*2+1;
    ray.setFromCamera(mouse, camera);
    const hit=ray.intersectObjects(pickables, false)[0];
    if(hit){
      const ud=hit.object.userData;
      const hex='#'+new THREE.Color(ud.color||0xffffff).getHexString();
      logT.innerHTML='<span class="sw" style="background:'+hex+'"></span>'+(ud.label||'Voxel');
      const y=hit.point.y.toFixed(1);
      logB.textContent=(ud.sub||'')+ '  [ '+ (ud.kind||'object') +' · '+ y +' m ]';
      logEl.classList.add('show');
      clearTimeout(timer); timer=setTimeout(()=>logEl.classList.remove('show'), 5200);
    }
  }
  down=null;
});

/* ══════════════════════════════════════════════════════════
   12 · UI
   ══════════════════════════════════════════════════════════ */
let tour=true, tourT=0;
controls.autoRotate = true;
document.getElementById('timeRow').addEventListener('click',e=>{
  const b=e.target.closest('button'); if(!b) return;
  [...e.currentTarget.children].forEach(x=>x.classList.toggle('on', x===b));
  applyPreset(b.dataset.t, true);
});
document.querySelectorAll('[data-c]').forEach(b=>b.addEventListener('click',()=>{
  const map={
    sea:{pos:[-24,26,-44],tgt:[6,10,22]},
    deck:{pos:[24,13,10],tgt:[8,9,25]},
    light:{pos:[-52,32,-6],tgt:[-18,22,17]},
    town:{pos:[6,44,86],tgt:[2,12,32]}
  }[b.dataset.c];
  flyTo(map.pos, map.tgt); tour=false; controls.autoRotate=false;
  document.getElementById('spin').classList.remove('on');
}));
const spinBtn=document.getElementById('spin');
spinBtn.addEventListener('click',()=>{ tour=false; controls.autoRotate=!controls.autoRotate;
  spinBtn.classList.toggle('on', controls.autoRotate); });
controls.addEventListener('start',()=>{ tour=false; if(controls.autoRotate){controls.autoRotate=false;spinBtn.classList.remove('on');} });

let fly=null;
function flyTo(pos,tgt){
  fly={t:0, p0:camera.position.clone(), p1:new THREE.Vector3(...pos),
       g0:controls.target.clone(), g1:new THREE.Vector3(...tgt)};
}
const ease=t=>t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2;

/* ══════════════════════════════════════════════════════════
   13 · animation loop
   ══════════════════════════════════════════════════════════ */
const clock=new THREE.Clock();
function frame(){
  const dt=Math.min(clock.getDelta(),.05), t=clock.elapsedTime;

  /* preset cross-fade */
  if(tgt && lerpT<1){
    lerpT=Math.min(1, lerpT+dt/1.25); const k=ease(lerpT);
    const c={};
    for(const key in tgt){
      const a=cur[key], b=tgt[key];
      c[key]=(a&&a.isColor)?a.clone().lerp(b,k):(a&&a.isVector3)?a.clone().lerp(b,k):a+(b-a)*k;
    }
    bake(c); cur=c;
    if(lerpT>=1){ cur=tgt; tgt=null; }
  }

  /* water */
  for(let i=0;i<cols.length;i++){
    const c=cols[i];
    const k=c.sea?1:.42;
    const a=.34*k, a2=.2*k;
    const y=-.5 + Math.sin(c.x*.16 + t*1.25)*a + Math.cos(c.z*.19 - t*.95)*a2
                  + Math.sin((c.x+c.z)*.075 + t*.55)*.22*k;
    _p.set(c.x, y, c.z);
    _e.set(Math.cos(c.z*.19 - t*.95)*.09*k, 0, Math.sin(c.x*.16 + t*1.25)*.11*k);
    _q.setFromEuler(_e);
    water.setMatrixAt(i, new THREE.Matrix4().compose(_p,_q,_s));
  }
  water.instanceMatrix.needsUpdate=true;

  /* ship motion */
  SHIP.position.y = Math.sin(t*.72)*.19 + Math.sin(t*1.31+1.2)*.07;
  SHIP.rotation.z = Math.sin(t*.58)*.016;
  SHIP.rotation.x = Math.sin(t*.83+2.1)*.011;
  shipFlags.forEach(f=>{
    f.list.forEach((v,i)=>{
      const o=v[0]-Math.round(v[0])+ (v[0]-0);
      const n=Math.max(0,(v[0]-Math.floor(v[0]))+ (v[0]-v[0]));
      const d=v[0]-Math.round(v[0]);
      f.ms;
    });
    f.g.children.forEach(im=>{
      const list=im.userData.list;
      const mtx=new THREE.Matrix4();
      list.forEach((v,i)=>{
        const dx=v[0]-Math.min(...list.map(q=>q[0]));
        const zz=Math.sin(dx*1.15 + t*6.2)*.42*(dx/5) + Math.cos(dx*.7+t*4)*.1;
        mtx.compose(new THREE.Vector3(v[0],v[1]+Math.sin(dx*2+t*5)*.06,zz),
          new THREE.Quaternion(), new THREE.Vector3(1,1,.26));
        im.setMatrixAt(i,mtx);
      });
      im.instanceMatrix.needsUpdate=true;
    });
  });

  /* flags on shore */
  flagMeshes.forEach(f=>{
    f.ms.forEach(im=>{
      const list=im.userData.list;
      const minX=Math.min(...list.map(q=>q[0]));
      const mtx=new THREE.Matrix4();
      list.forEach((v,i)=>{
        const d=v[0]-minX;
        const zz=Math.sin(d*1.05+t*5.4)*.5*(d/6)+.15;
        mtx.compose(new THREE.Vector3(v[0], v[1]+Math.sin(d*2.2+t*4.4)*.09, zz),
          new THREE.Quaternion(), new THREE.Vector3(1,1,.28));
        im.setMatrixAt(i,mtx);
      });
      im.instanceMatrix.needsUpdate=true;
    });
  });

  /* foam pulse */
  const fScale=new THREE.Vector3();
  foam.forEach((f,i)=>{
    const ph=Math.sin(t*2.1+i*1.7)*.5+.5;
    _p.set(f.x, .12+ph*.1, f.z);
    _q.identity();
    fScale.set(.7+ph*.9, .25, .7+ph*.9);
    foamMesh.setMatrixAt(i, new THREE.Matrix4().compose(_p,_q,fScale));
  });
  foamMesh.instanceMatrix.needsUpdate=true;
  foamMesh.material.opacity = .32 + Math.sin(t*1.3)*.1;

  /* clouds */
  let ci=0;
  cloudList.forEach(c=>{
    c.x += c.spd*dt; if(c.x>250) c.x=-250;
    c.cubes.forEach(b=>{
      _p.set(c.x+b[0], c.y+b[1]+Math.sin(t*.35+c.z*.1)*.5, c.z+b[2]);
      _q.identity(); _s.set(b[3],b[4],b[5]);
      cloudMesh.setMatrixAt(ci++, new THREE.Matrix4().compose(_p,_q,_s));
    });
  });
  cloudMesh.instanceMatrix.needsUpdate=true;

  /* gulls */
  gulls.forEach((g,i)=>{
    g.ph += g.spd*dt; g.flap += dt*11;
    const x=g.cx+Math.cos(g.ph)*g.r, z=g.cz+Math.sin(g.ph)*g.r;
    const y=g.y+Math.sin(g.ph*2.2)*2.2;
    const yaw=-g.ph - (g.spd>0?Math.PI/2:-Math.PI/2);
    const flap=Math.sin(g.flap)*.75;
    const q=new THREE.Quaternion().setFromEuler(new THREE.Euler(0,yaw,Math.sin(g.ph*2.2)*.25,'YXZ'));
    const put=(k,px,py,pz,sx,sy,sz,rx)=>{
      const qq=new THREE.Quaternion().setFromEuler(new THREE.Euler(0,0,rx,'ZXB')).multiply(q);
      const local=new THREE.Vector3(px,py,pz).applyQuaternion(q);
      _s.set(sx,sy,sz);
      gullMesh.setMatrixAt(i*4+k, new THREE.Matrix4().compose(
        new THREE.Vector3(x,py,pz).add(new THREE.Vector3(x,y,z).sub(new THREE.Vector3(x,y,z))).set(x+local.x,y+local.y,z+local.z),
        qq, _s));
    };
    put(0, 0,0,0, 1.5,.6,.6, 0);
    put(1, 0,.15,1.15, 2.2,.22,1.05,  flap);
    put(2, 0,.15,-1.15, 2.2,.22,1.05, -flap);
    put(3, .95,.05,0, .8,.3,.3, 0);
    gullMesh.setColorAt(i*4+0, gullC.setHex(P.gull));
  });
  gullMesh.instanceMatrix.needsUpdate=true;

  /* chimney smoke */
  smokeList.forEach((s,i)=>{
    const p=((t*s.sp + s.off)%1);
    const sc=.35+p*1.6;
    _p.set(s.x+Math.sin((s.off+p*4)*2.2)*p*3.2, s.y+p*9.5, s.z+Math.cos(p*5+s.off*7)*p*2.4);
    _q.identity(); _s.set(sc,sc,sc);
    smokeMesh.setMatrixAt(i, new THREE.Matrix4().compose(_p,_q,_s));
  });
  smokeMesh.instanceMatrix.needsUpdate=true;

  /* lamp glow flicker */
  lamps.forEach((L,i)=>{
    const f=.8+Math.sin(t*7+L.ph)*.12+Math.sin(t*17+L.ph*3)*.06;
    _p.set(L.x,L.y,L.z); _q.identity(); _s.setScalar(1.15*f);
    glowMesh.setMatrixAt(i, new THREE.Matrix4().compose(_p,_q,_s));
  });
  glowMesh.instanceMatrix.needsUpdate=true;
  glowMesh.material.opacity=clamp(cur.lamp*.5,0,.55);
  TOWER.intensity=(cur.lamp)*(2.1+Math.sin(t*8)*.22);

  /* lighthouse beam + sun orb follow */
  beamG.rotation.y += dt*.42;
  beamG.children.forEach(h=>{ h.children[0].material.opacity = .04+cur.lamp*.11*(.7+Math.sin(t*1.6)*.3); });

  /* intro tour */
  if(tour){ tourT+=dt; if(tourT>11){ tour=false; controls.autoRotate=false; spinBtn.classList.remove('on'); } }
  if(fly){
    fly.t=Math.min(1, fly.t+dt/.85); const k=ease(fly.t);
    camera.position.lerpVectors(fly.p0, fly.p1, k);
    controls.target.lerpVectors(fly.g0, fly.g1, k);
    if(fly.t>=1) fly=null;
  }

  controls.update();
  sky.position.copy(camera.position);
  renderer.render(scene, camera);
  renderer.shadowMap.needsUpdate = true;   // keep shadows fresh, one frame at a time
  renderer.shadowMap.autoUpdate = false;
  requestAnimationFrame(frame);
}

addEventListener('resize',()=>{
  camera.aspect=innerWidth/innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight);
  renderer.shadowMap.needsUpdate=true;
});

/* first render, then drop the curtain */
renderer.shadowMap.needsUpdate=true;
renderer.render(scene,camera);
requestAnimationFrame(()=>{
  document.getElementById('boot').classList.add('gone');
  frame();
});
</script>
</body>
</html>
```

**What's in the frame**

- **The barque Meridian** — 2400+ hand-placed voxels: carvel hull with antifouling red, gold boot-stripe and gunports, bulwarks, quarter gallery, forecastle, deck cargo, bowsprit, three tapered masts with tops, braced square sails, triple headsails, spanker, shroud tubes, stays, and four fluttering flags. It rolls and heaves on its own sine, and hawsers run taut to the wharf bollards.
- **The harbor** — an ashlar basin cut into the headland, wharf planking, bollards, rope coils, casks, crates, a fish stall, a coaling derrick, rowboats on the shingle, a lighthouse with a sweeping volumetric beam, a groyne field, a fort on the eastern heights, a windmill, and fourteen roofs climbing the hill — every window lit from inside.
- **Living layers** — animated per-column water (gentler inside the basin), pulsing foam collars, chimney smoke, drifting cloud slabs, gulls with flapping wings, flickering brass lamp glows.
- **Five watches** — dawn, noon, golden, dusk, night cross-fade the sky shader, fog, shadow direction, exposure, water tint and window emissives over 1.25 s.
- **Interaction** — orbit/zoom/pan, four camera flights, auto-orbit, and click any voxel to identify it in the ship's-log plate (color swatch, name, lore line, elevation).