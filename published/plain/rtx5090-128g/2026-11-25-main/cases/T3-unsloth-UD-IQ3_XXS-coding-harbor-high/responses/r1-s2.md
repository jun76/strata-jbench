# Graywater Harbour — a voxel scene

Everything below is one self-contained HTML file (Three.js via CDN import-map; the orbit controls, all geometry, animation and UI are hand-written). Save it as `harbor.html` and open it in Chrome.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,shrink-to-fit=no">
<title>Graywater Harbour — a ship calling in</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Rye&family=Karla:wght@300;400;500;700&display=swap" rel="stylesheet">
<style>
  :root{
    --brass:#d5a658; --brass-2:#f0cd90; --paper:#f1e7d4; --paper-2:rgba(240,232,216,.58);
    --ink:rgba(10,12,15,.78); --ink-2:rgba(10,12,15,.55); --line:rgba(213,166,88,.34);
  }
  *{box-sizing:border-box}
  html,body{margin:0;height:100%;overflow:hidden;background:#050a0f;
    font-family:Karla,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
    -webkit-font-smoothing:antialiased}
  #scene{position:fixed;inset:0;width:100%;height:100%;display:block;touch-action:none;cursor:grab}
  #scene.dragging{cursor:grabbing}
  #vig{position:fixed;inset:0;pointer-events:none;z-index:3;
    background:
      radial-gradient(118% 92% at 48% 40%, rgba(0,0,0,0) 42%, rgba(3,5,8,.62) 100%),
      linear-gradient(to top, rgba(3,5,8,.5) 0%, rgba(3,5,8,0) 26%);}

  .panel{position:fixed;z-index:4;background:linear-gradient(178deg,rgba(18,21,26,.86),rgba(11,14,18,.80));
    border:1px solid rgba(255,255,255,.09);border-top:2px solid var(--brass);
    box-shadow:0 18px 44px -18px rgba(0,0,0,.8), inset 0 1px 0 rgba(255,255,255,.05);
    color:var(--paper);padding:14px 17px 15px;backdrop-filter:blur(3px);}

  /* ---- plate ---- */
  #plate{top:20px;left:20px;width:342px;transform:translateY(-12px);opacity:0;
    animation:rise .9s .15s cubic-bezier(.2,.7,.2,1) forwards}
  #plate .rule{height:1px;background:var(--line);margin:11px 0 9px}
  .eyebrow{font-size:9.5px;letter-spacing:.28em;text-transform:uppercase;color:var(--brass);font-weight:700}
  h1{font-family:Rye,Georgia,serif;font-weight:400;font-size:33px;line-height:.96;margin:9px 0 2px;
     color:#f7ecd8;letter-spacing:.005em;text-shadow:0 2px 0 rgba(0,0,0,.35)}
  h1 em{font-style:normal;color:var(--brass-2)}
  .sub{font-size:12.5px;line-height:1.5;color:var(--paper-2);font-weight:300}
  #log{font-size:12px;line-height:1.45;color:#e6d9c0;min-height:2.5em;transition:opacity .4s ease}
  #log.swap{opacity:0}
  #clockrow{display:flex;align-items:baseline;gap:9px;margin-top:10px}
  #clock{font-family:Rye,Georgia,serif;font-size:19px;color:var(--brass-2);letter-spacing:.02em}
  #wind{font-size:10px;letter-spacing:.2em;text-transform:uppercase;color:var(--paper-2)}

  /* ---- rail ---- */
  #rail{left:20px;bottom:20px;width:342px;transform:translateY(12px);opacity:0;
    animation:rise .9s .38s cubic-bezier(.2,.7,.2,1) forwards}
  .ctl{margin-top:12px}
  .lab{display:flex;justify-content:space-between;align-items:center;font-size:9.5px;letter-spacing:.24em;
    text-transform:uppercase;color:var(--paper-2);margin-bottom:7px}
  .lab b{color:var(--brass-2);letter-spacing:.06em;font-weight:500;text-transform:none;font-size:11px}
  input[type=range]{-webkit-appearance:none;appearance:none;width:100%;height:16px;background:transparent;cursor:pointer}
  input[type=range]::-webkit-slider-runnable-track{height:3px;background:linear-gradient(90deg,var(--brass) 0%,rgba(213,166,88,.2) 0%);border-radius:2px}
  input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:11px;height:11px;border-radius:50%;
    background:#f6e2be;margin-top:-4px;border:1px solid #7c5a24;box-shadow:0 0 0 3px rgba(213,166,88,.18);transition:box-shadow .2s,transform .2s}
  input[type=range]:hover::-webkit-slider-thumb{transform:scale(1.15);box-shadow:0 0 0 6px rgba(213,166,88,.22)}
  input[type=range]::-moz-range-track{height:3px;background:rgba(213,166,88,.28)}
  input[type=range]::-moz-range-thumb{width:11px;height:11px;border:1px solid #7c5a24;border-radius:50%;background:#f6e2be}
  .btns{display:flex;flex-wrap:wrap;gap:5px;margin-top:6px}
  button{font-family:Karla,sans-serif;font-size:9.5px;letter-spacing:.16em;text-transform:uppercase;
    color:#e4d9c3;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.13);
    padding:6px 9px;cursor:pointer;transition:all .18s ease;position:relative;overflow:hidden}
  button:hover{background:rgba(213,166,88,.16);border-color:var(--brass);color:#fff5e2;transform:translateY(-1px)}
  button:active{transform:translateY(0)}
  button.on{background:linear-gradient(180deg,#e0b167,#c4934a);color:#1b1610;border-color:#e6bc79;font-weight:700}
  #hint{position:fixed;right:20px;bottom:20px;z-index:4;font-size:10px;letter-spacing:.2em;
    text-transform:uppercase;color:rgba(240,232,216,.42);text-align:right;line-height:1.9;pointer-events:none}
  #hint span{color:var(--brass);font-weight:700}

  /* ---- hover tag ---- */
  #tag{position:fixed;z-index:5;pointer-events:none;max-width:260px;padding:9px 12px 10px;
    background:linear-gradient(180deg,rgba(20,23,28,.94),rgba(12,15,19,.92));
    border-left:2px solid var(--brass);box-shadow:0 14px 30px -12px rgba(0,0,0,.85);
    opacity:0;transform:translateY(6px) scale(.98);transition:opacity .18s ease,transform .18s ease}
  #tag.show{opacity:1;transform:translateY(0) scale(1)}
  #tag .t{font-family:Rye,Georgia,serif;font-size:14px;color:#f7ecd8;line-height:1.1}
  #tag .d{font-size:11px;color:rgba(238,228,208,.6);margin-top:3px;line-height:1.4}
  #tag .c{font-size:8.5px;letter-spacing:.22em;text-transform:uppercase;color:var(--brass);margin-top:6px}

  #veil{position:fixed;inset:0;z-index:9;background:#0a0d12;display:grid;place-content:center;
    transition:opacity 1s ease;text-align:center}
  #veil .v{font-family:Rye,Georgia,serif;font-size:26px;color:#e9d6ae;letter-spacing:.02em}
  #veil .s{font-size:10px;letter-spacing:.3em;text-transform:uppercase;color:rgba(230,214,180,.5);margin-top:12px}
  #veil.gone{opacity:0;pointer-events:none}
  #fail{position:fixed;inset:0;z-index:10;display:none;place-content:center;color:#e9d6ae;
    font-size:13px;text-align:center;padding:24px;line-height:1.7}
  @keyframes rise{to{transform:translateY(0);opacity:1}}
  @media (max-width:780px){
    #plate{width:calc(100% - 28px);left:14px;top:14px}#rail{width:calc(100% - 28px);left:14px;bottom:14px}
    #hint{display:none}h1{font-size:27px}
  }
</style>
</head>
<body>
<canvas id="scene"></canvas>
<div id="vig"></div>

<div id="plate" class="panel">
  <div class="eyebrow">Voxel chart no. 07 &nbsp;·&nbsp; n&nbsp;54°21′ w&nbsp;004°08′</div>
  <h1>Graywater <em>Harbour</em></h1>
  <div class="sub">A ship calls in on the evening tide. Every block — 20,000 of them — laid by hand.</div>
  <div class="rule"></div>
  <div id="log">Barque <b>Cormorant</b> of Whitstable, inward bound, takes berth off the long wharf.</div>
  <div id="clockrow"><div id="clock">17:04</div><div id="wind">SW 6 kn · falling light</div></div>
</div>

<div id="rail" class="panel">
  <div class="eyebrow">Harbour master's console</div>
  <div class="ctl">
    <div class="lab"><span>Time of day</span><b id="todLbl">17:04</b></div>
    <input id="tod" type="range" min="0" max="24" step="0.02" value="17.05">
  </div>
  <div class="ctl">
    <div class="lab"><span>Sea state</span><b id="seaLbl">moderate</b></div>
    <input id="sea" type="range" min="0.15" max="1.5" step="0.01" value="0.62">
  </div>
  <div class="ctl">
    <div class="lab"><span>Viewpoint</span><b>click a marker · dbl-click to release</b></div>
    <div class="btns">
      <button data-view="0" class="on">Harbour</button>
      <button data-view="1">Quayside</button>
      <button data-view="2">Crow's nest</button>
      <button data-view="3">The light</button>
      <button data-view="4">Ashore</button>
    </div>
    <div class="btns" style="margin-top:5px">
      <button id="spin" class="on">Auto-orbit</button>
      <button id="cycle">Day cycle</button>
      <button id="dress">Dressed overall</button>
    </div>
  </div>
</div>

<div id="hint"><span>Drag</span> orbit &nbsp;·&nbsp; <span>Wheel</span> zoom<br><span>Right-drag</span> pan &nbsp;·&nbsp; hover to survey</div>

<div id="tag"><div class="t"></div><div class="d"></div><div class="c">survey · click to focus</div></div>

<div id="veil"><div class="v">Graywater Harbour</div><div class="s">placing the blocks…</div></div>
<div id="fail">WebGL could not start in this browser.<br>Try Chrome or Edge with hardware acceleration enabled.</div>

<script type="importmap">
{ "imports": { "three": "https://unpkg.com/three@0.160.0/build/three.module.js" } }
</script>

<script type="module">
import * as THREE from 'three';

/* ══════════════════════════ 0. helpers ══════════════════════════ */
const clamp=(v,a,b)=>v<a?a:v>b?b:v;
const lerp=(a,b,t)=>a+(b-a)*t;
const sstep=(e0,e1,x)=>{const t=clamp((x-e0)/(e1-e0),0,1);return t*t*(3-2*t);};
const mod=(a,b)=>((a%b)+b)%b;
function mulberry32(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
const rnd=mulberry32(774281);
const rr=(a,b)=>a+rnd()*(b-a), ri=(a,b)=>Math.floor(a+rnd()*(b-a+0.999));
const sh=(hex,f)=>{let r=clamp((hex>>16&255)*f,0,255)|0,g=clamp((hex>>8&255)*f,0,255)|0,b=clamp((hex&255)*f,0,255)|0;return (r<<16)|(g<<8)|b;};

/* ══════════════════════════ 1. renderer ══════════════════════════ */
const canvas=document.getElementById('scene');
let renderer;
try{ renderer=new THREE.WebGLRenderer({canvas,antialias:true,powerPreference:'high-performance'}); }
catch(e){ document.getElementById('veil').classList.add('gone'); document.getElementById('fail').style.display='grid'; throw e; }
renderer.setPixelRatio(Math.min(devicePixelRatio,1.75));
renderer.setSize(innerWidth,innerHeight);
renderer.shadowMap.enabled=true; renderer.shadowMap.type=THREE.PCFSoftShadowMap;
renderer.toneMapping=THREE.ACESFilmicToneMapping; renderer.toneMappingExposure=1.02;

const scene=new THREE.Scene();
scene.fog=new THREE.FogExp2(0x8fb0bd,0.0048);
const camera=new THREE.PerspectiveCamera(41,innerWidth/innerHeight,0.5,4000);

/* ══════════════════════════ 2. palette ══════════════════════════ */
const P={
 seaDeep:0x0f3a50, seaMid:0x1a6080, seaHi:0x2f93a8, foam:0xdceff2,
 stone:0x6f7268, stoneD:0x54564d, stoneL:0x8c8c7c, cobble:0x757465, cobbleD:0x5f5e51,
 rock:0x6a695e, rockD:0x505047, grass:0x587f46, grassD:0x456a38, grassL:0x6b9350,
 wood:0x6b4a2c, woodD:0x4b3220, woodL:0x8b6238, deck:0xa87a41, deckD:0x8c6234,
 hull:0x22384a, hullL:0x2a455b, hullBot:0x533028, gold:0xc39a4a, ivory:0xe6e0d0,
 sail:0xe9dcc0, sailSh:0xd2c1a0, rope:0x8d7a52, iron:0x2e3138,
 brick:0x8c4f43, brickD:0x6d3c33, plaster:0xd8ccb2, plaster2:0xc5b697, plaster3:0xe2dac6,
 roofRed:0x9a4a3c, roofSlate:0x486470, roofBrown:0x76513a, roofTeal:0x36707a,
 winDay:0x87a0b3, winWarm:0xffc169, winCool:0x27364a, lantern:0xffbb52,
 red:0xb5443b, blue:0x2f5f8f, yellow:0xdcb249, green:0x4a8154, cream:0xf1e7cf,
 crate:0x8a6134, crateL:0xa87c46, barrel:0x7a5030, hoop:0xc2a26d, gull:0xf4f1e8
};

/* ══════════════════════════ 3. voxel stores ══════════════════════════ */
const solid=[], glow=[];   // stride 7: x,y,z,w,h,d,color
function B(x,y,z,w,h,d,c){ if(w>0&&h>0&&d>0) solid.push(x,y,z,w,h,d,c); }
function G(x,y,z,w,h,d,c){ if(w>0&&h>0&&d>0) glow.push(x,y,z,w,h,d,c); }
const occ=new Set(); const pk=(x,z)=>x+','+z;
function claim(x0,x1,z0,z1){for(let x=x0;x<=x1;x++)for(let z=z0;z<=z1;z++)occ.add(pk(x,z));}
const taken=(x,z)=>occ.has(pk(x,z));

const _m=new THREE.Matrix4(),_v=new THREE.Vector3(),_q=new THREE.Quaternion(),_c=new THREE.Color();
function bake(arr,mat,cast=true,recv=true){
  const n=arr.length/7;
  const im=new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1),mat,n);
  for(let i=0;i<n;i++){const o=i*7,w=arr[o+3],h=arr[o+4],d=arr[o+5];
    _m.compose(_v.set(arr[o]+w/2,arr[o+1]+h/2,arr[o+2]+d/2),_q,_v.set(w,h,d));
    im.setMatrixAt(i,_m); im.setColorAt(i,_c.setHex(arr[o+6]));}
  im.castShadow=cast; im.receiveShadow=recv;
  im.instanceMatrix.needsUpdate=true; if(im.instanceColor)im.instanceColor.needsUpdate=true;
  return im;
}

/* ══════════════════════════ 4. sky / lights ══════════════════════════ */
const skyU={uTop:{value:new THREE.Color(0x2f6ba0)},uMid:{value:new THREE.Color(0xcfe0e8)},
 uLow:{value:new THREE.Color(0xf1c78d)},uSun:{value:new THREE.Color(0xffe6bf)},
 uSunDir:{value:new THREE.Vector3(0,1,0)},uSunI:{value:1}};
const sky=new THREE.Mesh(new THREE.SphereGeometry(1000,32,20),new THREE.ShaderMaterial({
  side:THREE.BackSide,depthWrite:false,fog:false,uniforms:skyU,
  vertexShader:`varying vec3 vD;void main(){vD=position;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}`,
  fragmentShader:`varying vec3 vD;uniform vec3 uTop,uMid,uLow,uSun,uSunDir;uniform float uSunI;
   void main(){vec3 d=normalize(vD);float h=clamp(d.y*0.5+0.5,0.0,1.0);
    vec3 c=mix(uLow,uMid,smoothstep(0.42,0.56,h));c=mix(c,uTop,smoothstep(0.54,0.94,h));
    float s=max(dot(d,normalize(uSunDir)),0.0);
    c+=uSun*pow(s,5.0)*0.42*uSunI;c+=uSun*pow(s,48.0)*1.1*uSunI;c+=uSun*pow(s,360.0)*1.4*uSunI;
    gl_FragColor=vec4(c,1.0);#include <tonemapping_fragment>#include <colorspace_fragment>}`
}));
sky.renderOrder=-2; scene.add(sky);

const dirLight=new THREE.DirectionalLight(0xffffff,2.4);
dirLight.castShadow=true; dirLight.shadow.mapSize.set(2048,2048);
dirLight.shadow.camera.left=-78;dirLight.shadow.camera.right=78;
dirLight.shadow.camera.top=78;dirLight.shadow.camera.bottom=-78;
dirLight.shadow.camera.near=1;dirLight.shadow.camera.far=320;
dirLight.shadow.bias=-0.0004; dirLight.shadow.normalBias=0.55; dirLight.shadow.radius=1.6;
scene.add(dirLight,dirLight.target);
const hemi=new THREE.HemisphereLight(0xbcd8e6,0x4d5b52,0.7); scene.add(hemi);
const lhLight=new THREE.PointLight(0xffd9a0,0,200,2); lhLight.position.set(-18,25,22); scene.add(lhLight);
const lampA=new THREE.PointLight(0xffa94f,0,72,2); lampA.position.set(15.5,10,-14); scene.add(lampA);
const lampB=new THREE.PointLight(0xffa94f,0,72,2); lampB.position.set(15.5,10,26); scene.add(lampB);

/* radial sprite texture */
function radialTex(inner,outer,pw){
  const s=128,c=document.createElement('canvas');c.width=c.height=s;const g=c.getContext('2d');
  const gr=g.createRadialGradient(s/2,s/2,0,s/2,s/2,s/2);
  gr.addColorStop(0,inner);gr.addColorStop(pw,outer);gr.addColorStop(1,'rgba(0,0,0,0)');
  g.fillStyle=gr;g.fillRect(0,0,s,s);const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;return t;
}
const texSun=radialTex('rgba(255,255,255,1)','rgba(255,220,150,.42)',0.22);
const texSoft=radialTex('rgba(255,230,180,.9)','rgba(255,190,110,.18)',0.3);
const texDot=radialTex('rgba(255,255,255,.95)','rgba(255,255,255,.28)',0.35);
function halo(size,color,opacity){
  const s=new THREE.Sprite(new THREE.SpriteMaterial({map:texSoft,color,transparent:true,opacity,
    blending:THREE.AdditiveBlending,depthWrite:false,fog:false}));
  s.scale.set(size,size,1); return s;
}
const sunSprite=new THREE.Sprite(new THREE.SpriteMaterial({map:texSun,color:0xfff3d8,transparent:true,opacity:0,
  blending:THREE.AdditiveBlending,depthWrite:false,fog:false})); sunSprite.scale.set(90,90,1); scene.add(sunSprite);
const sunHalo=new THREE.Sprite(new THREE.SpriteMaterial({map:texSoft,color:0xffc98a,transparent:true,opacity:0,
  blending:THREE.AdditiveBlending,depthWrite:false,fog:false})); sunHalo.scale.set(360,360,1); scene.add(sunHalo);
const moonSprite=new THREE.Sprite(new THREE.SpriteMaterial({map:texSun,color:0xd8e4f2,transparent:true,opacity:0,
  depthWrite:false,fog:false})); moonSprite.scale.set(46,46,1); scene.add(moonSprite);

/* stars */
{
  const N=900,pos=new Float32Array(N*3);
  for(let i=0;i<N;i++){
    const u=rnd()*2-1,th=rnd()*Math.PI*2,r=760,s=Math.sqrt(1-u*u);
    pos[i*3]=r*Math.cos(th)*s*0.98; pos[i*3+1]=Math.abs(u)*r*0.9+40; pos[i*3+2]=r*Math.sin(th)*s*0.98;
  }
  const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.BufferAttribute(pos,3));
  var starMat=new THREE.PointsMaterial({color:0xffffff,size:2.4,sizeAttenuation:false,transparent:true,opacity:0,depthWrite:false,fog:false});
  var stars=new THREE.Points(g,starMat); scene.add(stars);
}

/* ══════════════════════════ 5. sea ══════════════════════════ */
const SEA_Y=0, QUAY_X=13, CELL=2, GRD=26;
const seaBase=new THREE.Mesh(new THREE.BoxGeometry(960,3,960),
  new THREE.MeshLambertMaterial({color:0x103a4e}));
seaBase.position.set(0,-1.55,0); seaBase.receiveShadow=false; scene.add(seaBase);

const waterMat=new THREE.MeshLambertMaterial({color:0xffffff});
const waterGeo=new THREE.BoxGeometry(CELL*1.02,1,CELL*1.02);
const cols=[];
for(let ix=0;ix<GRD;ix++)for(let iz=0;iz<GRD*2;iz++){
  const x=-88+ix*CELL*1.35, z=-86+iz*CELL;
  if(x>14.5) continue;
  cols.push({x,z,o:cols.length*7});
}
const wIM=new THREE.InstancedMesh(waterGeo,waterMat,cols.length);
wIM.receiveShadow=true; wIM.castShadow=false; scene.add(wIM);
{ const a=wIM.instanceMatrix.array;
  for(let i=0;i<cols.length;i++){const o=i*16;a[o]=1;a[o+5]=1;a[o+10]=1;a[o+15]=1;
    a[o+12]=cols[i].x; a[o+14]=cols[i].z; a[o+1]=0;a[o+2]=0;a[o+3]=0;a[o+4]=0;a[o+6]=0;a[o+7]=0;a[o+8]=0;a[o+9]=0;a[o+11]=0;a[o+13]=0;}
  wIM.instanceColor=new THREE.InstancedBufferAttribute(new Float32Array(cols.length*3),3);
}
let waveAmp=0.62;
function waveY(x,z,t){
  return waveAmp*(0.55*Math.sin(x*0.135+t*1.15)+0.44*Math.sin(z*0.112-t*0.95)
   +0.33*Math.sin((x*0.7+z*0.75)*0.168+t*1.72)+0.2*Math.sin((x-z)*0.245-t*2.35));
}
const wDeep=new THREE.Color(),wMid=new THREE.Color();
function updateWater(t){
  const a=wIM.instanceMatrix.array, ca=wIM.instanceColor.array;
  for(const c of cols){
    const y=waveY(c.x,c.z,t), mo=i=>ca[i*3+mo];
    const f=sstep(-0.5*waveAmp,0.62*waveAmp,y);
    const o=c.o;
    const rr_=lerp(wDeep.r,wMid.r,f), gg=lerp(wDeep.g,wMid.g,f), bb=lerp(wDeep.b,wMid.b,f);
    const sp=0.03*Math.sin(c.x*0.55+c.z*0.41+t*2.4);
    ca[o]=clamp(rr_+sp,0,1); ca[o+1]=clamp(gg+sp,0,1); ca[o+2]=clamp(bb+sp,0,1);
    const o16=c.o/7*16;
    const h=y+4.2; a[o16+5]=h; a[o16+13]=(SEA_Y-4.2+y)/2;
  }
  wIM.instanceMatrix.needsUpdate=true; wIM.instanceColor.needsUpdate=true;
}

/* foam collars */
const foamMat=new THREE.MeshBasicMaterial({color:0xe6f4f6,transparent:true,opacity:.55,depthWrite:false});
const foam=[];
for(let i=0;i<70;i++) foam.push({x:rr(-16,11),z:rr(-40,40),ph:rr(0,6.28),s:rr(.8,2.4)});
for(let i=0;i<46;i++) foam.push({x:QUAY_X-0.2+rr(-.9,.4),z:-70+i*3+rr(-.8,.8),ph:rr(0,6.28),s:rr(1,2.6)});
const foamIM=new THREE.InstancedMesh(new THREE.BoxGeometry(1,0.18,1),foamMat,foam.length);
scene.add(foamIM);
function updateFoam(t){
  for(let i=0;i<foam.length;i++){const f=foam[i],v=sstep(0.55,1,0.5+0.5*Math.sin(t*1.7+f.ph));
    const s=f.s*(0.4+v*0.9);
    _m.compose(_v.set(f.x,SEA_Y+0.18+waveY(f.x,f.z,t)*0.5,f.z),_q,_v.set(s,0.08,s));
    foamIM.setMatrixAt(i,_m);}
  foamIM.instanceMatrix.needsUpdate=true;
}

/* glint points */
const glintMat=new THREE.ShaderMaterial({
  uniforms:{uTime:{value:0},uSunDir:{value:new THREE.Vector3(0,1,0)},uCam:{value:new THREE.Vector3()},
    uSunCol:{value:new THREE.Color(0xfff0d0)},uAmp:{value:0.62},uInt:{value:1}},
  vertexShader:`attribute float aSeed;uniform float uTime,uAmp,uInt;uniform vec3 uSunDir,uCam;
   varying float vA;
   void main(){vec3 p=position;
    float t=uTime;
    p.y=uAmp*(0.55*sin(p.x*0.135+t*1.15)+0.44*sin(p.z*0.112-t*0.95)
      +0.33*sin((p.x*0.7+p.z*0.75)*0.168+t*1.72)+0.2*sin((p.x-p.z)*0.245-t*2.35))+0.16;
    vec3 vd=normalize(p-uCam);vec3 rf=normalize(vec3(-uSunDir.x,abs(uSunDir.y)+0.12,-uSunDir.z));
    float m=pow(max(dot(vd,rf),0.0),14.0);
    float tw=0.5+0.5*sin(t*7.0+aSeed*40.0);
    float fade=smoothstep(190.0,40.0,distance(p,uCam));
    vA=m*tw*fade*uInt;
    gl_PointSize=(1.5+4.5*tw)*clamp(80.0/distance(p,uCam),0.35,3.0);
    gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.0);}`,
  fragmentShader:`uniform vec3 uSunCol;varying float vA;
   void main(){float d=length(gl_PointCoord-0.5);if(d>0.5)discard;
    float a=vA*(1.0-d*2.0);gl_FragColor=vec4(uSunCol,a);}`,
  transparent:true,depthWrite:false,blending:THREE.AdditiveBlending
});
{
  const N=700,pos=new Float32Array(N*3),sd=new Float32Array(N);
  for(let i=0;i<N;i++){pos[i*3]=rr(-84,12);pos[i*3+1]=0;pos[i*3+2]=rr(-84,84);sd[i]=rnd();}
  const g=new THREE.BufferGeometry();
  g.setAttribute('position',new THREE.BufferAttribute(pos,3));
  g.setAttribute('aSeed',new THREE.BufferAttribute(sd,1));
  var glints=new THREE.Points(g,glintMat); glints.frustumCulled=false; scene.add(glints);
}

/* ══════════════════════════ 6. terrain + town ══════════════════════════ */
const pads=new Map();
function setPad(x0,x1,z0,z1,h){for(let x=x0;x<=x1;x++)for(let z=z0;z<=z1;z++)pads.set(pk(x,z),h);}
function terrainH(x,z){
  if(x<QUAY_X) return null;
  const p=pads.get(pk(x,z)); if(p!==undefined) return p;
  if(x<26) return 5;
  if(x<30) return 6;
  let h=6+(x-30)*0.10+Math.sin(z*0.068)*0.9+Math.cos(x*0.10+z*0.05)*0.8;
  if(x>52) h+=(x-52)*0.24;
  return clamp(Math.round(h),5,14);
}
const buildings=[];
function addBuilding(o){ buildings.push(o); claim(o.x-1,o.x+o.w+1,o.z-1,o.z+o.d+1);
  setPad(o.x,o.x+o.w-1,o.z,o.z+o.d-1,o.y); }

/* --- town plan --- */
(function plan(){
  addBuilding({x:28,y:5,z:-6,w:13,d:11,h:7,wall:P.plaster3,roof:null,big:true,label:'The Custom House',
    note:'Long room, quick pen. Everything ashore is weighed here first.'});
  addBuilding({x:45,y:7,z:-30,w:9,d:13,h:5,wall:P.stoneL,roof:null,church:true,label:"St Brendan's",
    note:'Clock tower, lead spire, weather vane turning to whatever is out there.'});
  addBuilding({x:27,y:5,z:24,w:10,d:15,h:8,wall:P.brick,roof:P.roofBrown,hoist:true,label:'Bale Warehouse',
    note:'Five floors of hemp, tallow and tin. The derrick takes in the cargo.'});
  addBuilding({x:41,y:7,z:22,w:8,d:7,h:4,wall:P.plaster,roof:P.roofRed,chimney:true,label:'The Salt Dog',
    note:'Public house. Smoke on the chimney, boots on the pavement.'});
  addBuilding({x:52,y:8,z:6,w:8,d:7,h:4,wall:P.plaster2,roof:P.roofSlate,chimney:true,label:'Ropewalk',
    note:'Hemp in, cable out.'});
  addBuilding({x:56,y:9,z:-14,w:6,d:6,h:4,wall:P.stoneL,roof:P.roofTeal,mill:true,label:'Upland Mill',
    note:'Four sails, still turning. The sails face out to sea.'});
  addBuilding({x:46,y:7,z:34,w:7,d:6,h:3,wall:P.plaster,roof:P.roofBrown,chimney:true,label:'Net Loft',});
  addBuilding({x:36,y:6,z:-40,w:7,d:6,h:3,wall:P.plaster2,roof:P.roofRed,chimney:true,label:'Chandlery',
    note:'Tar, oakum, candles, chart paper.'});
  addBuilding({x:53,y:8,z:-40,w:7,d:6,h:4,wall:P.plaster,roof:P.roofSlate,chimney:true,label:"Cooper's Yard",});
  addBuilding({x:60,y:10,z:20,w:6,d:6,h:3,wall:P.stone,roof:P.roofRed,chimney:true,label:'Beacon Cottage',});
  const rows=[[31,5],[33,6],[36,6],[44,7],[48,7],[42,7],[50,7],[56,8],[58,9],[34,5],[38,6],[46,7],[54,8],[60,10],[63,10]];
  for(const [x,yy] of rows){
    let z=ri(-60,54), tries=0, w=ri(5,7), d=ri(5,7);
    while(tries++<40 && (taken(x-1,z-1)||taken(x+w,z+d)||z<-64||z>64||
      (x<42&&Math.abs(z)<6)||Math.abs(z-22)<9)) z=ri(-62,56);
    if(taken(x,z)) continue;
    addBuilding({x,y:yy,z,w,d,h:ri(3,5),wall:pick([P.plaster,P.plaster2,P.plaster3,P.stoneL,P.brick]),
      roof:pick([P.roofRed,P.roofSlate,P.roofBrown,P.roofBrown,P.roofTeal]),
      chimney:rnd()<0.62,label:'Harbourman\'s Cottage',note:'Built against the weather, painted against the gloom.'});
  }
})();

/* --- terrain --- */
const T=2;
for(let x=QUAY_X;x<=76;x+=T){
  for(let z=-76;z<=76;z+=T){
    const h=terrainH(x+T/2,z+T/2); if(h===null) continue;
    const top=(x<27)?pick([P.cobble,P.cobble,P.cobbleD,P.stone]):(h>=9?pick([P.grass,P.grassD,P.stone]):pick([P.grass,P.grass,P.grassL,P.grassD]));
    B(x,-6,z,T,h+6,T,sh(x<27?P.rockD:P.rock,rr(0.9,1.1)));
    B(x,h,z,T,1,T,sh(top,rr(0.88,1.14)));
  }
}
/* quay face + buttresses + steps */
for(let z=-76;z<76;z+=2){
  B(QUAY_X-1,-6,z,1.1,11.6,2,sh(P.stone,rr(0.86,1.08)));
  B(QUAY_X-1.9,-1,z,1,4,2,sh(P.stoneD,rr(0.85,1.1)));
  if(mod(z,12)<2) B(QUAY_X-2.4,-3.5,z,2.4,9,3,sh(P.stoneL,rr(0.86,1.05)));
}
for(let s=0;s<6;s++){ const z=-52+s*18;
  for(let i=0;i<3;i++) B(24+i*2,5+i,z,2,0.6,4,sh(P.stoneL,rr(0.9,1.08))); }

/* --- long wharf + fish quay --- */
function pier(x0,x1,z0,z1,topY,c1,c2){
  for(let x=Math.min(x0,x1);x<Math.max(x0,x1);x+=2)
    for(let z=z0;z<=z1;z+=3){ B(x,-4.5,z,1,topY+4.6,1,sh(P.woodD,rr(0.85,1.05)));
      B(x-0.35,topY-0.15,z-0.35,1.7,0.5,1.7,sh(P.woodD,0.8)); }
  for(let x=Math.min(x0,x1);x<=Math.max(x0,x1);x++)
    for(let z=z0;z<=z1;z++) B(x,topY-0.5,z,1,0.5,1,sh((x+z)%2?c1:c2,rr(0.9,1.1)));
  for(let x=Math.min(x0,x1);x<=Math.max(x0,x1);x++){ B(x,topY-0.42,z0-0.4,1,0.6,0.5,sh(P.woodD,0.9)); B(x,topY-0.42,z1+0.4-0.1,1,0.6,0.5,sh(P.woodD,0.9)); }
}
pier(13,-17,20,24,P.deck+0.4,P.wood,P.woodL);
pier(13,-4,-23,-19,4.2,P.wood,P.woodL);
claim(12,-18,19,25); claim(12,-5,-24,-18);

/* --- lighthouse --- */
{
  const cx=-18,cz=22,base=4.5;
  B(-20,3.4,19,6,1.4,7,sh(P.stoneD,1));
  B(cx-2,base,cz-2,5,1.6,5,sh(P.stone,1.02));
  const rings=[[4,3,'#w'],[3,6],[3,6],[2,6],[2,5],[1,5]];
  let y=base+1.6, r=3;
  for(let i=0;i<12;i++){
    const h=3, col=(mod(i,2)===0)?P.ivory:sh(P.red,0.95);
    B(cx-r,y,cz-r,2*r+1,h,2*r+1,sh(col,i%2?rr(0.9,1):rr(0.98,1.06)));
    y+=h; if(i===1)r=3; if(i===4)r=2; if(i===7)r=2;
  }
  B(cx-3,y,cz-3,7,0.7,7,sh(P.iron,1.05));           // gallery
  B(cx-2,y+0.7,cz-2,5,2.6,5,P.iron);                // lantern room frame
  G(cx-1.6,y+0.9,cz-1.6,4.2,2.2,4.2,0xfff0c4);      // the lamp
  B(cx-2,y+3.3,cz-2,5,0.6,5,sh(P.iron,1.1));
  B(cx-1,y+3.9,cz-1,3,0.9,3,sh(P.red,0.9));         // cap
  B(cx-0.2,y+4.8,cz-0.2,0.4,1.6,0.4,sh(P.iron,1.2));
  // keeper's cottage on the pier head
  B(-14,4.8,26,6,3,5,sh(P.plaster3,rr(0.96,1.04)));
  for(let i=0;i<3;i++) B(-14+i*3,7.8,25.6,3.2,1,5.8,sh(P.roofSlate,rr(0.88,1.06)));
  G(-12.5,6,25.9,1.1,1.2,0.18,P.winWarm); G(-16,6,25.9,1.1,1.2,0.18,P.winWarm);
  B(-13,7.8,27,1,2,1,sh(P.brick,1));
  smokeSources.push(new THREE.Vector3(-12.5,10.1,27));
}
/* rotating beam */
const beamMat=new THREE.MeshBasicMaterial({color:0xffe6b4,transparent:true,opacity:0,
  blending:THREE.AdditiveBlending,depthWrite:false,side:THREE.DoubleSide,fog:true});
const beams=new THREE.Group(); beams.position.set(-18,25.4,22); scene.add(beams);
for(let i=0;i<2;i++){
  const g=new THREE.ConeGeometry(17,150,5,1,true); g.translate(0,-75,0);
  const m=new THREE.Mesh(g,beamMat); m.rotation.z=Math.PI/2*(i?1:-1)+ (i?0:0);
  m.rotation.set(0,0,i?Math.PI:0); m.position.set(i?0:0,0,0);
  const cm=new THREE.Mesh(new THREE.ConeGeometry(17,150,5,1,true),beamMat);
  cm.rotation.z=-Math.PI/2; cm.position.set(75,0,0);
  const cm2=new THREE.Mesh(new THREE.ConeGeometry(17,150,5,1,true),beamMat);
  cm2.rotation.z=Math.PI/2; cm2.position.set(-75,0,0);
  if(i===0) beams.add(cm,cm2);
}
const lhHalo=halo(46,0xffdcac,0); lhHalo.position.set(-18,25.4,22); scene.add(lhHalo);

/* ══════════════════════════ 7. buildings ══════════════════════════ */
const winRefs=[];
function facade(x0,y,z0,w,h,d,o){
  const wallc=o.wall;
  // walls + floor slab
  for(let a=0;a<w;a++)for(let b=0;b<h;b++)for(let c=0;c<d;c++){
    const edge=(a===0||a===w-1)||(c===0||c===d-1);
    if(!edge && b!==h-1) continue;
    B(x0+a,y+b,z0+c,1,1,1,sh(wallc,rr(0.93,1.06)));
  }
  // corner quoins
  for(let b=0;b<h;b++){B(x0,y+b,z0,1,1,1,sh(P.stoneL,rr(1,1.1)));B(x0+w-1,y+b,z0,1,1,1,sh(P.stoneL,rr(1,1.1)));
    B(x0,y+b,z0+d-1,1,1,1,sh(P.stoneL,rr(1,1.1)));B(x0+w-1,y+b,z0+d-1,1,1,1,sh(P.stoneL,rr(1,1.1)));}
  // string course
  if(h>=5) for(let a=0;a<w;a++)for(let c=0;c<d;c++){const e=(a===0||a===w-1)||(c===0||c===d-1);
    if(e&&b_unused()) 0; }
  // windows on the two side faces (x±) and end faces (z±)
  const rows=Math.max(1,Math.floor((h-1)/2.4)), colsA=Math.max(1,Math.floor((d-1)/2.4)), colsB=Math.max(1,Math.floor((w-2)/2.4));
  const putWin=(wx,wy,wz,ww,wh,wd)=>{
    const lit=rnd()<0.72;
    const idx=glow.length/7;
    G(wx,wy,wz,ww,wh,wd,P.winDay); winRefs.push({i:idx,lit,warmrr:rr(0.8,1)});
  };
  for(let r=0;r<rows;r++)for(let c=0;c<colsA;c++){
    const yw=y+1.4+r*2.4, zz=z0+1+Math.round(c*(d-2.4)/colsA);
    if(yw+1>y+h-1) continue;
    putWin(x0-0.16,yw,zz,0.32,1.3,1.1); putWin(x0+w-0.84,yw,zz,0.32,1.3,1.1);
    // lintel + sill
    B(x0-0.1,yw+1.3,zz-0.1,1.1,0.3,1.3,sh(P.stoneL,1.02));
    B(x0+w-0.9,yw+1.3,zz-0.1,1.1,0.3,1.3,sh(P.stoneL,1.02));
  }
  for(let r=0;r<rows;r++)for(let c=0;c<colsB;c++){
    const yw=y+1.4+r*2.4, xx=x0+1+Math.round(c*(w-2.4)/colsB);
    if(yw+1>y+h-1) continue;
    putWin(xx,yw,z0-0.16,1.1,1.3,0.32); putWin(xx,yw,z0+d-0.84,1.1,1.3,0.32);
  }
}
function b_unused(){return false;}
function roofGable(x,y,z,w,d,col,ridgeAlongZ){
  if(ridgeAlongZ){ const half=Math.ceil(w/2);
    for(let i=0;i<half;i++){ const ww=w-2*i; if(ww<=0)break; B(x+i,y+i,z,ww,1,d,sh(col,rr(0.88,1.05))); }
    B(x+half-1,y+half-1,z-0.6,1.6,0.8,d+1.2,sh(col,1.15));
  } else { const half=Math.ceil(d/2);
    for(let i=0;i<half;i++){ const dd=d-2*i; if(dd<=0)break; B(x,y+i,z+i,w,1,dd,sh(col,rr(0.88,1.05))); }
    B(x-0.6,y+half-1,z+half-1,w+1.2,0.8,1.6,sh(col,1.15));
  }
}
for(const o of buildings){
  if(o.mill) continue;
  facade(o.x,o.y,o.z,o.w,o.h,o.d,o);
  if(o.church){
    const tx=o.x+1,tz=o.z+4;
    B(tx,o.y,tz,7,15,7,sh(P.stoneL,rr(0.97,1.04)));
    facade(tx,o.y+15,tz,7,3,7,{wall:sh(P.stoneL,1.02)});
    for(let i=0;i<5;i++) B(tx+1-i*0.5?tx+1:tx,o.y+18+i,tz+1,7-(i*1.4)>0?7-i*1.4:1,1,7-i*1.4>0?7-i*1.4:1,sh(P.roofSlate,rr(0.9,1.05)));
    for(let i=0;i<6;i++){const s=5-i*0.85; if(s<0.4)break; B(tx+3.5-s/2,o.y+19+i,tz+3.5-s/2,s,1,s,sh(P.roofSlate,rr(0.88,1.04)));}
    // clock
    G(tx+3.5-1.2,o.y+15.8,tz-0.2,2.4,2.4,0.3,0xf2e6c6);
    // weathervane
    B(tx+3.4,o.y+25,tz+3.4,0.3,2.4,0.3,sh(P.iron,1.2));
  }
  else if(o.big){
    // Custom house: colonnade, pediment, cupola
    for(let i=0;i<5;i++){ const zz=o.z+1.5+i*2.1;
      B(o.x-1.4,o.y,zz,1.2,6.2,1.2,sh(P.plaster3,1.06)); B(o.x-1.8,o.y+6.2,zz-0.3,2,0.7,1.8,sh(P.stoneL,1.02)); }
    B(o.x-2,o.y+6.9,o.z-0.6,o.w+2,1.2,o.d+1.2,sh(P.plaster3,1.02));
    B(o.x-2.4,o.y+8.1,o.z+1,o.w+3,0.8,o.d-2,sh(P.stoneL,1.0));
    B(o.x+o.w/2-2,o.y+8.9,o.z+o.d/2-2,4,2.4,4,sh(P.plaster3,1.04));
    for(let i=0;i<3;i++) B(o.x+o.w/2-2+i*0.6,o.y+11.3-i*0.6,o.z+o.d/2-2+i*0.6,4-i*1.2,0.7,4-i*1.2,sh(P.roofTeal,rr(0.9,1.05)));
    B(o.x+o.w/2-0.2,o.y+13.3,o.z+o.d/2-0.2,0.4,2,0.4,sh(P.gold,1.05));
    G(o.x+2,o.y+2.2,o.z-0.16,2.4,2.6,0.3,P.winWarm); winRefs.push({i:glow.length/7-1,lit:true});
    // flagpoles
    for(const fz of [o.z+1,o.z+o.d-2]){ B(o.x-2.4,o.y+8.9,fz,0.3,6,0.3,sh(P.woodL,1));
      addFlag(o.x-2.4,o.y+14.2,fz,3.2,2.2,[P.red,P.cream,P.blue][ri(0,2)],0,1,0); }
  }
  if(o.hoist){
    // derrick over the quay + hanging crate
    B(o.x-3,o.y+5,o.z+6,4.5,0.8,0.8,sh(P.wood,1));
    B(o.x-4.6,o.y+2.5,o.z+6,0.8,3.4,0.8,sh(P.woodD,1));
    B(o.x-6,o.y+1.2,o.z+5.6,2.2,2.2,2.2,sh(P.crate,rr(0.95,1.05)));
  }
  if(o.roof) roofGable(o.x,o.y+o.h,o.z,o.w,o.d,o.roof,true);
  else if(o.church||o.big) {}
  else roofGable(o.x,o.y+o.h,o.z,o.w,o.d,pick([P.roofSlate,P.roofBrown]),true);
  if(o.chimney){ const cx=o.x+ri(1,o.w-2), cz=o.z+ri(1,o.d-2);
    B(cx,o.y+o.h+1,cz,1.1,3,1.1,sh(P.brickD,rr(0.9,1.1)));
    smokeSources.push(new THREE.Vector3(cx+0.5,o.y+o.h+4.2,cz+0.5)); }
  // shop awning on the sea-facing wall of a few
  if(!o.big&&!o.church&&!o.mill&&rnd()<0.5&&o.y<=7){
    const aw=o.x-1.2, ay=o.y+2.2;
    for(let i=0;i<3;i++) B(aw-0.3,ay-0.35*i,o.z+1+i,1.1,0.28,2.4,i%2?P.cream:P.red);
    B(o.x-1.3,o.y,ay?o.z+1:0,0.25,2.2,0.25,sh(P.woodD,1));
  }
}

/* ══════════════════════════ 8. quay props ══════════════════════════ */
const pickables=[], pickMat=new THREE.MeshBasicMaterial({visible:false});
function pickBox(x,y,z,w,h,d,label,note){
  const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),pickMat);
  m.position.set(x+w/2,y+h/2,z+d/2); m.userData={label,note:note||''};
  scene.add(m); pickables.push(m); return m;
}
pickBox(-22,4,18,12,23,9,'Graywater Light','Est. 1781 · 24 m focal plane · two flashes every twelve seconds');
pickBox(-19,3.4,19.5,26,2,7,'The Long Wharf','Cargo side. Crates by the ton, gulls by the thousand.');
pickBox(-6,3,-24,20,3,6,'Fish Quay','Nets drying, crates stacked, the tide doing the rest.');
pickBox(-19,0,-30,7,5,6,'Tug “Brimstone”','Coal-fired, brass-bellied. Hauls anything that floats, slowly.');
pickBox(-56,0,-56,13,14,13,'Schooner “Nelly”','Outward bound on the morning tide, sails furled for the night.');

/* bollards + lamps along the quay */
for(let z=-70,i=0;z<70;z+=9,i++){
  const x=14.4;
  B(x,5,z,1.1,1.3,1.1,sh(P.woodD,rr(0.85,1.05))); B(x-0.15,6.3,z-0.15,1.4,0.4,1.4,sh(P.iron,1.1));
  if(mod(i,2)===1){
    const lz=z+4;
    B(16,5.2,lz,0.45,4.6,0.45,sh(P.iron,1.05));
    B(16,9.8,lz-0.7,0.45,0.4,1.8,sh(P.iron,1.1));
    G(16,9.2,lz-1.5,0.9,0.9,0.9,P.lantern);
    G(16,9.2,lz+0.1,0.9,0.9,0.9,P.lantern);
    B(15.6,10.2,lz-1.9,1.3,0.5,1.7,sh(P.iron,1.2));
    const h=halo(7,0xffb45a,0); h.position.set(16,9.6,lz-0.7); scene.add(h); lampHalos.push(h);
  }
}
/* crates, barrels, ropes, carts */
function crate(x,y,z,s,c){ B(x,y,z,s,s,s,sh(c||P.crate,rr(0.9,1.1)));
  B(x+s*0.08,y+s*0.42,z-0.12,s*0.84,0.18,0.2,sh(P.crateL,1.1));
  B(x+s*0.08,y-s*0.42,z-0.12,s*0.84,0.18,0.2,sh(P.crateL,1.1)); }
function barrel(x,y,z,c){ B(x,y,z,1.4,1.9,1.4,sh(c||P.barrel,rr(0.92,1.06)));
  B(x-0.08,y-0.4,z-0.08,1.56,0.22,1.56,sh(P.hoop,1)); B(x-0.08,y+0.42,z-0.08,1.56,0.22,1.56,sh(P.hoop,1)); }
for(let i=0;i<26;i++){
  const z=rr(-66,66), x=rr(16,24.5), s=pick([1,1,1.4,2]);
  crate(x,5,z,s); if(rnd()<0.4) crate(x+0.2,5+s,z+0.2,s*0.8);
}
for(let i=0;i<16;i++) barrel(rr(16,24),5,rr(-64,64));
for(let i=0;i<10;i++){ const z=rr(-60,60),x=rr(16.5,24),y=5;
  for(let k=0;k<7;k++){const a=k/7*Math.PI*2; B(x+Math.cos(a)*0.9,y,z+Math.sin(a)*0.9,0.4,0.24,0.4,sh(P.rope,1));}
  B(x,y+0.24,z,0.6,0.2,0.6,sh(P.rope,1.1)); }
/* hand cart */
{ const x=19,z=8; B(x,5.9,z,3.2,1.2,2,sh(P.wood,1)); B(x-0.1,7.1,z-0.1,3.4,0.24,2.2,sh(P.woodL,1));
  for(const s of [-1,1]){ for(let k=0;k<8;k++){const a=k/8*Math.PI*2;
    B(x+1.6+Math.cos(a)*1.05,5+Math.abs(Math.sin(a))*1.0,z+s*1.1,0.35,0.35,0.3,sh(P.woodD,1));} }
  B(x+3.2,5.9,z+0.6,2.2,0.24,0.24,sh(P.woodL,1)); B(x+3.2,5.9,z-0.6,2.2,0.24,0.24,sh(P.woodL,1)); }
/* fish-market awnings + nets on the fish quay */
for(let i=0;i<4;i++){ const z=-23+i*1.4, x=rr(6,10.5);
  for(let k=0;k<3;k++){ B(x-2,6.4-k*0.4,z+1.5-k*1.1,4,0.3,1.1,i%2?P.cream:P.roofRed); }
  B(x-2,4.7,z+1.4,0.3,1.9,0.3,sh(P.woodD,1)); B(x+1.6,4.4,z-0.6,0.3,2.4,0.3,sh(P.woodD,1)); }
for(let i=0;i<5;i++){ const z=-20.5, x=-4+i*1.6;
  B(x,4.7,z,1.2,1.2,1.2,sh(P.crate,0.95)); B(x,5.9,z,1.2,0.4,1.2,sh(P.seaMid||P.blue,1.05)); }
/* anchor monument */
{ const x=17.5,z=-30; B(x,5,z,0.5,3,0.5,sh(P.iron,1.15)); B(x-1.2,7.6,z,2.9,0.4,0.4,sh(P.iron,1.1));
  for(const s of[-1,1]) for(let k=0;k<5;k++) B(x+s*(0.5+k*0.32),5+0.35+k*0.28,z,0.34,0.5,0.42,sh(P.iron,1)); B(x,5,z,0.5,3,0.5,sh(P.iron,1.05)); }
/* trees */
function tree(x,z){
  const h=terrainH(x,z); if(h===null) return;
  const t=ri(2,4); B(x,h+1,z,0.8,t,0.8,sh(P.woodD,rr(0.9,1.1)));
  const r=ri(1,2);
  B(x-r,h+1+t,z-r,2*r+1,2,2*r+1,sh(pick([P.grassD,P.grass,P.grassL]),rr(0.86,1.06)));
  B(x-r+0.5,h+3+t,z-r+0.5,2*r-0.5?2*r-0.4:1,1.4,2*r-0.4?2*r-0.4:1,sh(pick([P.grassD,P.grass]),rr(0.88,1.08)));
  claim(x-2,x+2,z-2,z+2);
}
for(let i=0;i<34;i++){ const x=rr(28,72), z=rr(-70,70); if(!taken(Math.round(x),Math.round(z))) tree(Math.round(x),Math.round(z)); }
/* hedges & tufts */
for(let i=0;i<60;i++){ const x=rr(26,74),z=rr(-72,72),h=terrainH(Math.round(x),Math.round(z));
  if(h===null||taken(Math.round(x),Math.round(z)))continue;
  B(x,h+1,z,rr(1,2.6),rr(0.4,1.1),rr(1,2.6),sh(pick([P.grassD,P.grass]),rr(0.82,1.05))); }

/* ══════════════════════════ 9. windmill ══════════════════════════ */
const millHub=new THREE.Group();
{
  const x=56,z=-14,y=9;
  B(x,y,z,6,2,6,sh(P.stone,1.02)); B(x+0.5,y+2,z+0.5,5,4,5,sh(P.stoneL,1.02));
  B(x+1,y+6,z+1,4,1.6,4,sh(P.roofBrown,1));
  B(x+1.6,y+7.6,z+1.6,2.8,2,2.8,sh(P.roofRed,1.05));
  B(x-1,y+8.4,z+2.8,1,1.2,0.5,sh(P.woodD,1));
  millHub.position.set(x-1.1,y+8.6,z+3); scene.add(millHub);
  for(let b=0;b<4;b++){ const g=new THREE.Group(); g.rotation.z=b*Math.PI/2;
    const m=new THREE.Mesh(new THREE.BoxGeometry(0.5,10,0.5),new THREE.MeshStandardMaterial({color:P.woodL,roughness:1}));
    m.position.y=5; m.castShadow=false; g.add(m);
    for(let s=0;s<6;s++){ const p=new THREE.Mesh(new THREE.BoxGeometry(1.3,0.7,0.22),
      new THREE.MeshStandardMaterial({color:P.cream,roughness:1})); p.position.set(0.75,2+s*1.4,0); g.add(p);}
    millHub.add(g);
  }
  millHub.children.forEach(g=>g.children.forEach(c=>c.castShadow=false));
}

/* ══════════════════════════ 10. THE SHIP ══════════════════════════ */
const ship=new THREE.Group(); ship.position.set(-3.5,0,0); scene.add(ship);
const SHIP={keel:-3.2,deck:4.15,rail:5.0,len:32};
function halfWidth(z){
  const t=clamp((z+16)/32,0,1);
  if(t<0.055) return Math.max(0.06,t*11);
  if(t>0.94) return 3.0;
  return 5.6*(0.06+0.94*Math.pow(Math.sin(Math.PI*Math.pow(t,0.72)),0.52));
}
function sheerY(z){ return SHIP.rail+1.15*Math.pow(Math.abs(z)/16,2.3); }
{
  const arr=[];
  for(let z=-16;z<=15;z++){
    const hw=halfWidth(z); if(hw<0.15) continue;
    const top=sheerY(z), n=Math.round(hw);
    for(let y=SHIP.keel;y<top;y++){
      const yf=0.68+0.32*sstep(-3.2,2.0,y);
      const w=Math.min(n,Math.round(hw*yf));
      if(w<0) continue;
      for(let x=-w;x<=w;x++){
        let c;
        if(y<=-1.5) c=sh(P.hullBot,rr(0.86,1.02));
        else if(y<=-0.5) c=sh(P.barrel,rr(0.95,1.06));
        else if(y>=top-0.5) c=sh(P.woodL,rr(0.94,1.08));
        else if(y===2) c=sh(P.gold,rr(0.95,1.05));
        else c=((mod(z,3)===0)?P.hullL:P.hull);
        if(mod(x,1)===0 && y>=0 && y<2 && mod(z+40,4)===0 && Math.abs(x)===w) c=0x191a1d;
        arr.push(x,y,z,1,1,1,sh(c,rr(0.95,1.06)));
      }
    }
    arr.push(-n,SHIP.deck,z,2*n+1,0.5,1,sh((mod(z,2))?P.deck:P.deckD,rr(0.93,1.07)));
    // channels
    if(mod(z+40,5)===0 && z>-13 && z<14){
      arr.push(n+0.2,3.0,z,0.9,0.4,3,sh(P.wood,1)); arr.push(-n-1.1,3.0,z,0.9,0.4,3,sh(P.wood,1));
    }
  }
  // raised decks & furniture
  arr.push(-4,SHIP.deck+0.5,-14,9,0.5,7,sh(P.deck,1.02));      // forecastle
  arr.push(-4,SHIP.deck+0.9,7,9,0.5,8,sh(P.deck,1.0));          // quarterdeck
  for(let i=0;i<4;i++) arr.push(-3.6+i*0.9,SHIP.deck+0.3+i*0.2,1.6-i*0.5,0.9,0.3,1.6,sh(P.deckD,1));
  arr.push(-2,SHIP.deck+0.5,3.4,2,1.6,2,sh(P.deckD,1));         // companion
  arr.push(-1.5,SHIP.deck+2.1,3.4,1,0.3,2,sh(P.wood,1));
  arr.push(-1,SHIP.deck+0.6,-8,2,1.2,2,sh(P.wood,1.05));        // capstan
  arr.push(-1.2,SHIP.deck+1.8,-8.2,2.4,0.35,2.4,sh(P.woodL,1));
  for(const hz of [-5.5,1.5,8]){ arr.push(-3,SHIP.deck+0.6,hz,6,0.35,3,sh(P.sail,1.02));
    arr.push(-3,SHIP.deck+0.95,hz-0.15,6,0.2,0.4,sh(P.sailSh,1)); }
  for(const [bx,bz] of [[-4,-2],[2,-2],[-4,5.5],[2.4,5.5],[3,10.5]]){
    arr.push(bx,SHIP.deck+0.5,bz,1.5,1.7,1.5,sh(P.barrel,1.02));
    arr.push(bx-0.08,SHIP.deck+1.0,bz-0.08,1.66,0.2,1.66,sh(P.hoop,1)); }
  arr.push(-4.5,SHIP.deck+0.5,-11,3,1.6,2.2,sh(P.crate,1)); arr.push(-4.5,SHIP.deck+2.1,-11,2,1,2,sh(P.crateL,1));
  // figurehead + bowsprit
  arr.push(-0.7,3.6,-16.9,1.4,1.6,2.4,sh(P.ivory,1.04)); arr.push(-0.4,3.2,-17.9,0.8,0.9,1.4,sh(P.ivory,0.95));
  for(let i=0;i<10;i++){ const t=i/9; arr.push(-0.35,4.6+t*1.5,-16.5-t*6.2,0.9-t*0.45,0.9-t*0.4,1.1,sh(P.woodL,1.03)); }
  arr.push(-0.25,6.5,-22.4,0.4,0.4,4.4,sh(P.woodL,1));
  arr.push(-2.4,7.0,-20.4,0.3,1.4,0.3,sh(P.wood,1)); arr.push(2.4,7.0,-20.4,0.3,1.4,0.3,sh(P.wood,1));
  // stern: transom, windows, rail, lantern
  for(let y=-1;y<5.6;y++) for(let x=-3;x<=2;x++) arr.push(x,y,15,1,1,1,sh(y===5?P.woodL:P.hull,rr(0.96,1.06)));
  arr.push(-2.5,2.6,15.2,6,0.3,0.3,sh(P.gold,1.05));
  for(const wxx of [-2,0,2]){ glow.push(wxx,1.1,15.25,1.6,1.5,0.2,P.winWarm); winRefs.push({i:glow.length/7-1,lit:true,ship:true}); }
  arr.push(-3.5,5.4,14.2,0.4,1.4,0.4,sh(P.gold,1)); arr.push(3,5.4,14.2,0.4,1.4,0.4,sh(P.gold,1));
  arr.push(-3.5,6.6,14.2,0.4,0.9,0.4,sh(P.iron,1.1));
  glow.push(-3.8,6.6,14.2,1.1,1.1,1.1,P.lantern); winRefs.push({i:glow.length/7-1,lit:true});
  // bulwark inner rail stripe
  for(let z=-15;z<=14;z++){ const hw=halfWidth(z),n=Math.round(hw),top=sheerY(z);
    if(hw>1){ arr.push(n,top-1.4,z,1,0.35,1,sh(P.gold,0.95)); arr.push(-n,top-1.4,z,1,0.35,1,sh(P.gold,0.95)); } }
  // mast shafts + tops + yards + sails
  const mastArr=[], sailArr=[];
  function mast(mz,htop,wd){
    for(let y=SHIP.deck;y<htop;y++){ const w=(y>htop-3)?1:wd; mastArr.push(-Math.floor(w/2),y,mz,w,1,w,sh(P.wood,rr(0.95,1.05))); }
    mastArr.push(-1.5,htop*0.72,mz-1.5,3,0.5,3,sh(P.woodL,1));       // top platform
    for(const s of[-1,1]) mastArr.push(1.6*s,htop*0.72+1.2,mz,0.3,2.4,0.3,sh(P.wood,1));
    mastArr.push(-0.2,htop,mz-0.2,0.4,2.2,0.4,sh(P.woodL,1.05));
  }
  function yard(yz,w){ for(let x=-Math.floor(w/2);x<=Math.floor(w/2);x++)
    mastArr.push(x,yz,yz===0?0:0,1,1,1,sh(P.woodL,1)); }
  function yardAt(y,yz,w){ for(let x=-Math.floor(w/2);x<=Math.floor(w/2);x++) mastArr.push(x,y,yz+Math.round(w/2)-Math.abs(x)>w*0.44?0:0,1,1,1,sh(P.woodL,1.02)); }
  function sail(x0,yTop,yBot,zc,halfW,bulge,phase){
    for(let x=Math.ceil(-halfW);x<=Math.floor(halfW);x++){
      for(let y=yBot;y<=yTop;y++){
        const u=x/halfW;
        const dep=bulge*Math.sin(Math.PI*Math.abs(u))*sstep(yTop-0.2,yTop-1.6,y)*(0.75+0.35*(1-Math.abs(u)));
        sailArr.push(x,y,zc,1,1,1,dep,phase,u);
      }
    }
  }
  const M=[{z:-8.5,h:22,ys:[[10.4,10.5,3.6,13.2],[15.2,8.6,2.9,18.4]]},
           {z:1.5,h:25.6,ys:[[9.8,11.4,4.1,14.2],[15.8,9.6,3.1,19.0],[19.8,7.8,2.4,22.2]]},
           {z:11.5,h:19,ys:[[11.6,7.2,2.9,14.6],[15.4,5.6,2.2,17.6]]}];
  for(const m of M){
    mast(m.z,m.h,m.z===1.5?2:1);
    for(const [y,w,dz,ss] of m.ys){
      for(let x=-Math.floor(w/2);x<=Math.floor(w/2);x++){
        const droop=Math.abs(x)/(w/2); mastArr.push(x,y-m.dz,m.z,1,1,1,sh(P.woodL,1.02)); }
      sail(y, y-0.0, y-ss, m.z, w/2, dz===0?0.4:(w>9?1.9:1.4), Math.random()*6.28);
    }
  }
  // spanker on mizzen (fore-aft gaff sail)
  for(let z=11.5;z<=15;z++) for(let y=6;y<=10.5;y++){
    const u=(z-11.5)/3.5; sailArr.push(2.0,y,z,1,1,1,0.5*Math.sin(Math.PI*u)*(1-u*0.4),1.1,u); }
  for(let z=11;z<=15.4;z++) mastArr.push(2,6,z,1,1,1,sh(P.woodL,1));
  for(let z=11;z<=15;z++) mastArr.push(2,10.5,z,1,1,1,sh(P.wood,1));

  const shipMat=new THREE.MeshLambertMaterial({color:0xffffff});
  const hullIM=bake(arr,shipMat); ship.add(hullIM);
  const mastIM=bake(mastArr,shipMat); ship.add(mastIM);
  // sails instanced & animated
  var sailData=[], sailIM;
  {
    const n=sailArr.length/9;
    sailIM=new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1),
      new THREE.MeshLambertMaterial({color:0xffffff,side:THREE.DoubleSide}),n);
    sailIM.castShadow=true;
    for(let i=0;i<n;i++){const o=i*9;
      sailData.push({x:sailArr[o],y:sailArr[o+1],z:sailArr[o+2],dep:sailArr[o+6],ph:sailArr[o+7],u:sailArr[o+8]});
      _c.setHex(sh(P.sail,0.94+0.10*Math.random())); sailIM.setColorAt(i,_c);}
    ship.add(sailIM);
  }
  // rigging
  {
    const pts=[]; const seg=(a,b)=>pts.push(a[0],a[1],a[2],b[0],b[1],b[2]);
    const heads=[[-0,22,-8.5],[0,25.6,1.5],[0,19,11.5]];
    seg([0,5.4,-21.5],heads[0]); seg(heads[0],heads[1]); seg(heads[1],heads[2]); seg(heads[2],[0,7.4,15]);
    seg([0,3.6,-16.9],[0,25.6,1.5]);
    for(const [hx,hy,hz] of heads){
      for(const s of[-1,1]){
        for(const [rz,rw] of [[hz-4,4.2],[hz,5.4],[hz+4,4.2]]){
          const zc=clamp(rz,-14,14), w=Math.max(1,Math.round(halfWidth(zc)));
          seg([s*w,sheerY(zc)-0.2,zc],[s*0.4,hy*0.72+0.4,hz]);
          seg([s*(w+0.6),3.2,zc],[s*0.4,hy*0.5,hz]);
        }
        seg([s*0.4,hy-0.4,hz],[s*0.4,hy*0.72+0.5,hz]);
      }
      seg([hx-3.2,hy+1.4,hz],[hx+3.2,hy+1.4,hz]);
    }
    const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.Float32BufferAttribute(pts,3));
    var rig=new THREE.LineSegments(g,new THREE.LineBasicMaterial({color:0x1b232a,transparent:true,opacity:.8}));
    ship.add(rig);
    // dressing line
    var dressPts=[];
    { const path=[[0,5.2,-21.5],[0,22,-8.5],[0,25.6,1.5],[0,19,11.5],[0,8,15]];
      for(let i=0;i<path.length-1;i++){ const a=path[i],b=path[i+1],N=9;
        for(let k=0;k<N;k++){const t=k/N;
          dressPts.push([lerp(a[0],b[0],t),lerp(a[1],b[1],t)-Math.sin(t*Math.PI)*1.15,lerp(a[2],b[2],t)]); } } }
    { const dp=[]; for(let i=0;i<dressPts.length;i++){const p=dressPts[i],q=dressPts[(i+1)%dressPts.length];
        dp.push(p[0],p[1],p[2],q[0],q[1],q[2]);}
      const dg=new THREE.BufferGeometry(); dg.setAttribute('position',new THREE.Float32BufferAttribute(dp,3));
      dressLine=new THREE.LineSegments(dg,new THREE.LineBasicMaterial({color:0x28323a,transparent:true,opacity:.65}));
      ship.add(dressLine);
      for(let i=0;i<dressPts.length;i++){const p=dressPts[i];
        addFlagShip(p[0],p[1]-0.75,p[2],1.05,0.8,pick([P.red,P.blue,P.yellow,P.cream,P.green,P.brick]),0,1,0);}
    }
  }
  // crew aboard
  addPerson(-0.4,SHIP.deck+1.9,1.4,0.0,0xff6b4a,true);
  addPerson(2,SHIP.deck+1.3,-11,Math.PI,0x3f6f9c,true);
  addPerson(-2.6,SHIP.deck+1.4,10.5,1.2,0x9c8648,true);
  addPerson(2.6,SHIP.deck+1.4,-4,Math.PI/2,0x4a5f3c,true);
  // ship's boat on davits
  { const bx=5.0; for(let z=-1;z<=3;z++){ const t=(z+1)/4; B(bx,3.0,z,1.4-t*0.4,0.9,1,sh(P.woodL,1.02)); }
    B(bx-0.2,3.9,-0.4,1.8,0.25,4.4,sh(P.wood,1)); for(const zz of[-0.2,2.6]) B(bx-0.9,3.9,zz,0.24,1.4,0.24,sh(P.woodD,1)); }
}

/* ══════════════════════════ 11. small craft ══════════════════════════ */
function boatMesh(w,l,c1,c2){
  const a=[];
  for(let z=-l/2;z<l/2;z++){ const t=clamp((z+l/2)/l,0,1); const hw=Math.max(0.6,w/2*Math.pow(Math.sin(Math.PI*Math.pow(t,0.7)),0.5));
    for(let x=-Math.round(hw);x<=Math.round(hw);x++) a.push(x,0,z,1,1,1,sh(Math.abs(x)===Math.round(hw)?c2:c1,rr(0.92,1.06)));
    a.push(0,-0.2,z,Math.round(hw)*2+1,0.4,1,sh(P.deck,1)); }
  return a;
}
function makeBoat(x,z,scl,c1,c2,label){
  const g=new THREE.Group(); g.position.set(x,0,z);
  const arr=boatMesh(3,8,c1,c2); for(let i=0;i<arr.length;i+=7){arr[i]*=scl;arr[i+1]*=scl;arr[i+2]*=scl;}
  g.add(bake(arr,new THREE.MeshLambertMaterial({color:0xffffff})));
  scene.add(g); return g;
}
const boatA=makeBoat(-2.5,-27,0.8,P.woodL,P.woodD);
const boatB=makeBoat(4.5,30,0.65,P.woodL,P.red);
/* tug */
const tug=new THREE.Group(); tug.position.set(-30,0,-30); scene.add(tug);
{
  const a=[];
  for(let z=-3;z<=4;z++){const hw=z<0?1:2; for(let x=-hw;x<=hw;x++) for(let y=-1;y<1;y++)
    a.push(x,y,z,1,1,1,sh(Math.abs(x)===hw?(y<0?P.hullBot:P.hull):P.hull,rr(0.94,1.06)));}
  a.push(-2,1,-3,5,0.4,8,sh(P.deck,1));
  a.push(-1.5,1.4,-1,3,2,4,sh(P.plaster3,1.0)); a.push(-1.4,3.4,-0.8,2.8,0.4,3.6,sh(P.roofRed,1));
  for(const wx of[-1.6,0.6]) a.push(wx,2.0,1.6,1,1,0.2,sh(P.iron,1.1));
  a.push(0.2,1.4,2.4,1.6,1.6,1.6,sh(P.iron,1.05));
  a.push(-1.2,1.4,2.4,1,1.4,1,sh(P.wood,1));
  a.push(0.6,3.4,1.4,1.2,2.4,1.2,sh(P.iron,1.1)); a.push(0.5,5.6,1.3,1.4,0.5,1.4,sh(P.red,1.05));
  tug.add(bake(a,new THREE.MeshLambertMaterial({color:0xffffff})));
  glow.push(-1.8,2.2,1.6,0.3,1,1,P.winWarm); winRefs.push({i:glow.length/7-1,lit:true});
  smokeSources.push(new THREE.Vector3(0.6,6.4,1.4));
}
/* moored schooner, far out */
const schooner=new THREE.Group(); schooner.position.set(-60,0,-60); schooner.rotation.y=0.7; scene.add(schooner);
{
  const a=boatMesh(5,12,P.hull,P.woodL);
  a.push(-2.5,-0.5,2,5,0.5,4,sh(P.deck,1)); a.push(-1.5,0,-1,3,1.4,2,sh(P.plaster2,1));
  a.push(-1.4,1.4,-1.2,3.2,0.5,2.4,sh(P.roofRed,1));
  for(const mz of[-2.5,2.5]) for(let y=0;y<(mz<0?12:9);y++) a.push(0,y,mz,1,1,1,sh(P.wood,rr(0.95,1.05)));
  for(const mz of[-2.5,2.5]){ a.push(-2.5,9,mz,6,1,1,sh(P.woodL,1));
    for(let y=7;y<8.6;y++) for(let x=-2;x<=2;x++) a.push(x,y,mz,1,1,1,sh(P.sailSh,rr(0.9,1.04))); }
  schooner.add(bake(a,new THREE.MeshLambertMaterial({color:0xffffff})));
}
/* buoys */
const buoys=[];
for(let i=0;i<7;i++){ const x=rr(-30,4), z=rr(-56,52);
  if(Math.abs(x)<6&&Math.abs(z)<18) continue;
  const g=new THREE.Group(); g.position.set(x,0,z); const a=[];
  const c=pick([P.red,P.red,P.green,P.blue]);
  for(let y=-1;y<2;y++) for(let xx=-1;xx<=1;xx++) for(let zz=-1;zz<=1;zz++)
    if(Math.abs(xx)+Math.abs(zz)<3) a.push(xx,y,zz,1,1,1,sh(y<1?c:sh(P.ivory,1),rr(0.94,1.06)));
  a.push(0,2,0,0.3,1.4,0.3,sh(P.iron,1));
  g.add(bake(a,new THREE.MeshLambertMaterial({color:0xffffff})));
  if(i%3===0){const hl=halo(3.2,c===P.red?0xff5a44:0x63e08a,0); hl.position.set(x,2.2,z); scene.add(hl); lampHalos.push(hl);}
  scene.add(g); buoys.push({g,ph:rr(0,6.3)});
}

/* ══════════════════════════ 12. people ══════════════════════════ */
const walkers=[];
const personMat=new THREE.MeshLambertMaterial({color:0xffffff});
function addPerson(x,y,z,ry,shirt,onShip){
  const g=new THREE.Group();
  const mk=(px,py,pz,w,h,d,c)=>{const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),personMat.clone());
    m.material.color.setHex(c); m.position.set(px,py,pz); m.castShadow=true; g.add(m); return m;};
  mk(0,0.32,0,0.34,0.64,0.3,0x35322f);
  const torso=mk(0,0.85,0,0.46,0.46,0.32,shirt);
  mk(0,1.24,0,0.3,0.3,0.28,0xc99a72);
  g.position.set(x,y,z); g.rotation.y=ry||0;
  if(onShip) ship.add(g); else scene.add(g);
  return g;
}
for(let i=0;i<9;i++){
  const z=rr(-58,56), x=rr(15,24), g=addPerson(x,5,z,rr(0,6.28),pick([P.red,P.blue,P.cream,P.green,P.brick,P.yellow]));
  walkers.push({g,x0:x-rr(2,6),x1:x+rr(2,6),z0:z-rr(1,7),z1:z+rr(1,7),t:rnd(),sp:rr(0.04,0.12),ph:rr(0,6.3)});
}
const helm=addPerson(18,5,-24.5,0,P.cream,false);
walkers.push({g:helm,x0:17.5,x1:11,z0:-24.5,z1:-24.5,t:0.3,sp:0.055,ph:1.2});
const boatsCrew=[];
{
  const g=new THREE.Group(); scene.add(g);
  g.add(addPerson(0,0.9,0.4,0,P.yellow)); g.children.forEach(c=>c.castShadow=false);
  boatsCrew.push(g);
}

/* ══════════════════════════ 13. clouds ══════════════════════════ */
const cloudArr=[];
for(let i=0;i<13;i++){
  const cx=rr(-120,120),cz=rr(-130,110),cy=rr(38,64),s=rr(1,2.4),n=ri(8,15);
  for(let k=0;k<n;k++){
    const w=rr(3,9)*s,h=rr(2,4)*s,d=rr(3,8)*s;
    const b=rr(0.86,1.06);
    cloudArr.push(cx+rr(-9,9)*s,cy+rr(-2,3)*s,cz+rr(-9,9)*s,w,h,d,sh(P.ivory,b));
    cloudArr.push(cx+rr(-9,9)*s,cy-rr(1,3.4)*s,cz+rr(-9,9)*s,w*0.8,h*0.6,d*0.8,sh(P.stoneL,rr(0.55,0.78)));
  }
}
const cloudMat=new THREE.MeshLambertMaterial({color:0xffffff});
const cloudIM=bake(cloudArr,cloudMat,false,false); cloudIM.frustumCulled=false; scene.add(cloudIM);
const cloudBase=cloudArr.filter((_,i)=>i%7===0).map((_,i)=>0);
const cloudX=new Float32Array(cloudArr.length/7);
for(let i=0;i<cloudArr.length/7;i++) cloudX[i]=cloudArr[i*7];

/* ══════════════════════════ 14. flags & pennants ══════════════════════════ */
const flagDefs=[];
function addFlag(x,y,z,w,h,c,nx,ny,nz){ flagDefs.push({x,y,z,w,h,c,nx,ny,nz,ship:false,ph:rnd()*6.3}); }
function addFlagShip(x,y,z,w,h,c,nx,ny,nz){ flagDefs.push({x,y,z,w,h,c,nx,ny,nz,ship:true,ph:rnd()*6.3}); }
// ensign on the stern gaff, jack at the bow, pennant at the main head
flagDefs.push({x:3.3,y:7.2,z:14.6,w:3.4,h:2.3,c:P.red,nx:1,ny:0,nz:0,ship:true,ph:0,ensign:true});
flagDefs.push({x:-2.5,y:8.4,z:-20.4,w:2.4,h:1.6,c:P.blue,nx:1,ny:0,nz:0,ship:true,ph:1.4});
flagDefs.push({x:0.0,y:27.6,z:1.5,w:3.4,h:1.2,c:P.yellow,nx:1,ny:0,nz:0,ship:true,ph:2.1});
for(const b of [[25,14,-52],[25,12,10],[52,17,6]]) addFlag(b[0],b[1],b[2],2.6,1.7,pick([P.red,P.blue,P.cream,P.green]),0,0,1);
const flagMat=new THREE.MeshLambertMaterial({color:0xffffff,side:THREE.DoubleSide});
const flagIM=new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1),flagMat,flagDefs.length);
flagIM.castShadow=false; scene.add(flagIM);
const ensignTex=[['RRRRRRR','RWBWBWR','WBWDWBW','BWDWDBW','WBWDWBW','RWBWBWR','RRRRRRR']][0];
function updateFlags(t){
  const par=ship;
  for(let i=0;i<flagDefs.length;i++){
    const f=flagDefs[i];
    let px=f.x,py=f.y,pz=f.z;
    if(f.ship){ const v=_v.set(f.x,f.y,f.z); par.localToWorld(v); px=v.x; py=v.y; pz=v.z; }
    const n=8, cells=[];
    let cnt=0; for(let a=0;a<n;a++)for(let b=0;b<4;b++) cnt++;
    _m.compose(_v.set(px,py,pz),_q.identity(),_v.set(0.05,f.h/4,f.w/n));
    flagIM.setMatrixAt(i,_m);
    _c.setHex(f.c); flagIM.setColorAt(i,_c);
  }
  // wave by rebuilding a subset cheaply: single instance per flag but stretched
  for(let i=0;i<flagDefs.length;i++){
    const f=flagDefs[i];
    let px=f.x,py=f.y,pz=f.z;
    if(f.ship){ const v=_v.set(f.x,f.y,f.z); par.localToWorld(v); px=v.x;py=v.y;pz=v.z; }
    const sway=Math.sin(t*3.1+f.ph)*0.16+Math.sin(t*7.3+f.ph*2)*0.06;
    _q.setFromEuler(new THREE.Euler(0, sway*0.5, sway*0.9));
    const len=f.w*(0.9+0.06*Math.sin(t*4+f.ph));
    const v2=_v.set(px+ (f.nx?len/2:0)+ (f.nz?0:0), py - f.h*0.02, pz+(f.nz?len/2:0));
    _m.compose(v2,_q,_v.set(f.nx?len:0.08, f.h, f.nz?len:0.08));
    flagIM.setMatrixAt(i,_m);
  }
  flagIM.instanceMatrix.needsUpdate=true;
  if(!flagIM.instanceColor) return;
  flagIM.instanceColor.needsUpdate=true;
}
{ // initial colors + ensign cross pattern is drawn as two overlaid strips
  const tmp=new THREE.Color();
  for(let i=0;i<flagDefs.length;i++) flagIM.setColorAt(i,tmp.setHex(flagDefs[i].c));
}
/* flag detail cubes (crosses / stripes) — a second small mesh */
{
  const a=[];
  const f=flagDefs[0];
  a.push(-0.14,0.6,0.9,1,1.2,0.5,P.cream);
}

/* ══════════════════════════ 15. moorings & gangway ══════════════════════════ */
const ropeMat=new THREE.MeshLambertMaterial({color:0xffffff});
const ropeIM=new THREE.InstancedMesh(new THREE.BoxGeometry(0.3,0.3,0.3),ropeMat,64);
ropeIM.castShadow=false; scene.add(ropeIM);
const ropeDefs=[
 {a:[-1.5,5.6,-14.5],b:[13.5,6.4,-12]},
 {a:[ 2.5,5.6,-14.0],b:[13.5,6.4, -3]},
 {a:[-1.5,6.0, 14.4],b:[13.5,6.4, 12]},
 {a:[ 2.5,5.4, 14.0],b:[14.0,6.4, 21]}
];
const _p0=new THREE.Vector3(),_p1=new THREE.Vector3(),_pm=new THREE.Vector3();
function updateRopes(t){
  let i=0;
  for(const rd of ropeDefs){
    _p0.set(rd.a[0],rd.a[1],rd.a[2]); ship.localToWorld(_p0);
    _p1.set(rd.b[0],rd.b[1],rd.b[2]);
    for(let k=0;k<16;k++){
      const u=k/15;
      _pm.lerpVectors(_p0,_p1,u); _pm.y-=Math.sin(u*Math.PI)*(1.6+0.1*Math.sin(t*0.8+i*0.3));
      _m.compose(_pm,_q.setFromEuler(new THREE.Euler(u*0.6,0.3,0)),_v.set(0.3,0.3,0.3));
      ropeIM.setMatrixAt(i,_m); ropeIM.setColorAt(i,_c.setHex(sh(P.rope,0.9+0.25*u)));
      i++; if(i>=64) return;
    }
  }
  ropeIM.count=i;
  ropeIM.instanceMatrix.needsUpdate=true; if(ropeIM.instanceColor) ropeIM.instanceColor.needsUpdate=true;
}
const gang=new THREE.Group(); scene.add(gang);
{
  const mk=(w,h,d,c,ox,oy,oz)=>{const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),
    new THREE.MeshStandardMaterial({color:c,roughness:1})); m.position.set(ox,oy,oz); m.castShadow=true; gang.add(m); return m;};
  mk(1.9,0.14,1,sh(P.woodL,1),0,0,0.5);
  for(const s of[-1,1]){ const r=mk(0.14,0.14,1,sh(P.wood,1),s*0.85,0.35,0.5);
    r.scale.set(1,1,1); const p=mk(0.1,0.5,0.1,sh(P.woodD,1),s*0.85,0.2,0.02);
    const p2=mk(0.1,0.5,0.1,sh(P.woodD,1),s*0.85,0.2,0.5);
    const p3=mk(0.1,0.5,0.1,sh(P.woodD,1),s*0.85,0.2,0.98); }
  gang.children.forEach(m=>{ if(m.geometry.parameters.depth===1) m.scale.z=9; });
}
const gangA=new THREE.Vector3(12.7,5.55,4), _gb=new THREE.Vector3();
function updateGang(t){
  _gb.set(4.9,4.85,4).applyMatrix4(ship.matrixWorld);
  gang.position.copy(gangA); gang.lookAt(_gb);
  gang.scale.z=gangA.distanceTo(_gb)/9;
  gang.rotateY(0);
}

/* ══════════════════════════ 16. smoke ══════════════════════════ */
const smokeSources=[];
const SM_N=220, SM_SRC=8;
const smokeMat=new THREE.ShaderMaterial({
  uniforms:{uTime:{value:0},uMax:{value:SM_N},uFog:{value:new THREE.Color(0x8fb0bd)},
    uCol:{value:new THREE.Color(0x2c2c30)},uWind:{value:new THREE.Vector2(-1.4,-0.8)},uSrc:{value:Array.from({length:SM_SRC},()=>new THREE.Vector3(0,-40,0))}},
  vertexShader:`attribute float aSeed;uniform float uTime,uMax;uniform vec3 uSrc[8];uniform vec2 uWind;varying float vA;
   void main(){int si=int(mod(aSeed*8.0,8.0));vec3 s=uSrc[si];
    float ph=fract(aSeed*13.7);float age=fract(uTime*0.085+ph);
    float sp=0.75+ph*0.6;
    vec3 p=s+vec3(uWind.x*age*sp*4.0, age*16.0*sp, uWind.y*age*sp*4.0);
    p.x+=sin(uTime*0.6+aSeed*30.0+age*4.0)*age*2.2;
    p.z+=cos(uTime*0.5+aSeed*22.0+age*3.0)*age*2.2;
    vA=smoothstep(0.0,0.09,age)*(1.0-smoothstep(0.35,1.0,age))*0.62;
    float sz=1.4+age*14.0;
    gl_PointSize=sz*(clamp(170.0/distance(p,cameraPosition),0.25,3.4));
    gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.0);}`,
  fragmentShader:`varying float vA;uniform vec3 uFog,uCol;
   void main(){float d=length(gl_PointCoord-0.5);if(d>0.5)discard;
    float a=vA*(1.0-d*1.85);vec3 c=mix(uCol,uFog,0.35);gl_FragColor=vec4(c,a);}`,
  transparent:true,depthWrite:false
});
{
  const pos=new Float32Array(SM_N*3),sd=new Float32Array(SM_N);
  for(let i=0;i<SM_N;i++){sd[i]=rnd();pos[i*3]=0;pos[i*3+1]=-40;pos[i*3+2]=0;}
  const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.BufferAttribute(pos,3));
  g.setAttribute('aSeed',new THREE.BufferAttribute(sd,1)); g.boundingSphere=new THREE.Sphere(new THREE.Vector3(0,10,0),400);
  var smoke=new THREE.Points(g,smokeMat); smoke.frustumCulled=false; scene.add(smoke);
}
while(smokeSources.length<SM_SRC) smokeSources.push(new THREE.Vector3(0,-60,0));
smokeMat.uniforms.uSrc.value=smokeSources.slice(0,SM_SRC);

/* ══════════════════════════ 17. gulls ══════════════════════════ */
const gullMat=new THREE.MeshStandardMaterial({color:P.gull,roughness:0.9});
const gulls=[];
for(let i=0;i<6;i++){
  const g=new THREE.Group();
  const body=new THREE.Mesh(new THREE.BoxGeometry(1.5,0.42,0.42),gullMat); body.castShadow=false; g.add(body);
  const head=new THREE.Mesh(new THREE.BoxGeometry(0.45,0.35,0.35),gullMat); head.position.set(0.8,0.15,0); g.add(head);
  const ws=[];
  for(const s of[-1,1]){
    const w=new THREE.Group(); w.position.set(0,0.12,s*0.2);
    const wm=new THREE.Mesh(new THREE.BoxGeometry(0.65,0.1,1.5),gullMat); wm.position.set(-0.05,0,s*0.95); w.add(wm);
    g.add(w); ws.push(w);
  }
  scene.add(g);
  gulls.push({g,ws,r:rr(18,46),a:rr(0,6.3),sp:rr(0.10,0.2)*(rnd()<0.5?-1:1),cy:rr(9,26),bob:rr(0,6.3),
    cx:rr(-24,20),cz:rr(-24,24)});
}
const bellRipple=document.getElementById('tag');

/* ══════════════════════════ 18. time of day ══════════════════════════ */
const KEYS=[
 {h:0.0, top:0x050a1a, mid:0x0d1a30, low:0x152539, sun:0x6688c4, si:0.16, hi:0.14, hc:0x2a3f6b, hg:0x10161f,
  fog:0x101a2c, deep:0x061c2c, mids:0x0d3348, sea:0.30, lamp:1, star:1},
 {h:4.4, top:0x0b1730, mid:0x2d2f4c, low:0x7b4a4e, sun:0x8f7fa6, si:0.3, hi:0.22, hc:0x4a4f78, hg:0x1b2130,
  fog:0x3b2f3c, deep:0x0a2434, mids:0x1d4257, sea:0.42, lamp:0.95, star:0.6},
 {h:6.2, top:0x2a4670, mid:0x9a6a63, low:0xf0a45c, sun:0xffb070, si:1.0, hi:0.42, hc:0x8f86a0, hg:0x3b3a3a,
  fog:0xcf8e63, deep:0x123044, mids:0x276277, sea:0.55, lamp:0.55, star:0.05},
 {h:8.2, top:0x4b83bf, mid:0xa8c8dc, low:0xd8e2e2, sun:0xfff0dc, si:2.0, hi:0.62, hc:0xa8c8dc, hg:0x4c5b4e,
  fog:0xbccfda, deep:0x144a63, mids:0x23748e, sea:0.72, lamp:0.05, star:0},
 {h:12.5,top:0x3a7cc0, mid:0xb4d2e4, low:0xe0e9ef, sun:0xfffbf0, si:2.8, hi:0.78, hc:0xbcd8e6, hg:0x556455,
  fog:0xc6d9e4, deep:0x125068, mids:0x2b8098, sea:0.8, lamp:0, star:0},
 {h:16.2,top:0x3772a8, mid:0xd6b98f, low:0xf6cf94, sun:0xffd79c, si:2.55,hi:0.62, hc:0xa9c2d4, hg:0x556049,
  fog:0xd9b98c, deep:0x124c63, mids:0x2b7d95, sea:0.75, lamp:0.1, star:0},
 {h:18.0,top:0x2a5588, mid:0xef9a58, low:0xffb862, sun:0xff9640, si:1.85,hi:0.42, hc:0x8fa2c0, hg:0x44443a,
  fog:0xe0985f, deep:0x103a52, mids:0x216176, sea:0.55, lamp:0.75, star:0.05},
 {h:19.4,top:0x1c3660, mid:0x8b4a58, low:0xc06a52, sun:0xb96a5c, si:0.85,hi:0.26, hc:0x4d5a86, hg:0x241f26,
  fog:0x8a5a58, deep:0x0b2b40, mids:0x184a60, sea:0.42, lamp:0.95, star:0.45},
 {h:21.0,top:0x070e22, mid:0x0f1c34, low:0x1a2540, sun:0x6688c4, si:0.2, hi:0.15, hc:0x2a3f6b, hg:0x10161f,
  fog:0x131d31, deep:0x061c2c, mids:0x0d3348, sea:0.31, lamp:1, star:1},
 {h:24.0,top:0x050a1a, mid:0x0d1a30, low:0x152539, sun:0x6688c4, si:0.16, hi:0.14, hc:0x2a3f6b, hg:0x10161f,
  fog:0x101a2c, deep:0x061c2c, mids:0x0d3348, sea:0.3, lamp:1, star:1}
];
const S={top:new THREE.Color(),mid:new THREE.Color(),low:new THREE.Color(),sun:new THREE.Color(),
  hc:new THREE.Color(),hg:new THREE.Color(),fog:new THREE.Color(),deep:new THREE.Color(),mids:new THREE.Color(),
  si:2,hi:0.6,sea:0.7,lamp:0,star:0};
const _tmpC=new THREE.Color();
function paletteAt(h){
  h=mod(h,24); let i=0; while(i<KEYS.length-2&&KEYS[i+1].h<h) i++;
  const a=KEYS[i],b=KEYS[i+1],t=clamp((h-a.h)/(b.h-a.h),0,1);
  const mix=(ka,kb)=>{S[kb].setHex(a[ka]);_tmpC.setHex(b[ka]);S[kb].lerp(_tmpC,t);};
  mix('top','top');mix('mid','mid');mix('low','low');mix('sun','sun');mix('hc','hc');mix('hg','hg');
  mix('fog','fog');mix('deep','deep');mix('mids','mids');
  S.si=lerp(a.si,b.si,t);S.hi=lerp(a.hi,b.hi,t);S.sea=lerp(a.sea,b.sea,t);
  S.lamp=lerp(a.lamp,b.lamp,t);S.star=lerp(a.star,b.star,t);
}
const sunDir=new THREE.Vector3();
function updateSky(h){
  paletteAt(h);
  const u=clamp((h-5.9)/13.0,0,1), ang=u*Math.PI;
  const az=THREE.MathUtils.degToRad(10+u*258), el=Math.sin(ang);
  const hh=Math.sqrt(Math.max(0.0001,1-Math.pow(el*0.82,2)));
  sunDir.set(Math.cos(az)*hh,el*0.82,Math.sin(az)*hh).normalize();
  dirLight.position.copy(sunDir).multiplyScalar(140); dirLight.target.position.set(0,4,0);
  dirLight.color.copy(S.sun); dirLight.intensity=S.si;
  hemi.color.copy(S.hc); hemi.groundColor.copy(S.hg); hemi.intensity=S.hi;
  scene.fog.color.copy(S.fog); scene.fog.density=lerp(0.0042,0.0058,1-S.sea*0.5);
  skyU.uTop.value.copy(S.top); skyU.uMid.value.copy(S.mid); skyU.uLow.value.copy(S.low);
  skyU.uSun.value.copy(S.sun); skyU.uSunDir.value.copy(sunDir); skyU.uSunI.value=clamp(S.si/2.4,0.05,1.1);
  sunSprite.position.copy(sunDir).multiplyScalar(650);
  sunHalo.position.copy(sunSprite.position);
  const up=smoothstep(-0.06,0.06,el);
  sunSprite.material.opacity=up*0.95; sunHalo.material.opacity=up*0.42*clamp(S.si/2.4,0,1);
  sunSprite.material.color.copy(S.sun); sunHalo.material.color.copy(S.sun);
  moonSprite.position.copy(sunDir).multiplyScalar(-650);
  moonSprite.material.opacity=smoothstep(0.02,0.2,-el)*0.9;
  starMat.opacity=S.star*0.9;
  wDeep.copy(S.deep); wMid.copy(S.mids); seaBase.material.color.copy(S.deep);
  glintMat.uniforms.uSunDir.value.copy(sunDir); glintMat.uniforms.uSunCol.value.copy(S.sun);
  glintMat.uniforms.uInt.value=clamp((S.si-0.4)/1.6,0,1.2)*0.85;
  lampA.intensity=lampB.intensity=80*S.lamp; lhLight.intensity=200*S.lamp;
  beamMat.opacity=0.10+0.32*S.lamp; lhHalo.material.opacity=0.12+0.55*S.lamp;
  for(const h2 of lampHalos) h2.material.opacity=(0.06+0.5*S.lamp)*(0.9+0.1*Math.random());
  smokeMat.uniforms.uFog.value.copy(S.fog);
  cloudMat.color.setRGB(1,1,1).lerp(S.mid.clone().multiplyScalar(1.25),0.35).lerp(_tmpC.setHex(0xffffff),0.4);
  cloudMat.color.copy(S.mid).lerp(_tmpC.setHex(0xffffff),0.55).multiplyScalar(lerp(0.5,1.25,S.sea));
  rig.material.opacity=0.4+0.45*S.sea;
  // windows
  for(const w of winRefs){
    const day=S.winDay||(S.winDay=new THREE.Color(P.winDay));
    const warm=new THREE.Color(P.winWarm), cool=new THREE.Color(P.winCool);
    _c.copy(day).multiplyScalar(0.9);
    if(S.lamp>0.02){ const target=w.lit?warm:cool; _c.lerp(target,clamp(S.lamp*1.15,0,1)); }
    if(w.warmrr!==undefined) _c.multiplyScalar(lerp(0.94,1.06,w.warmrr));
    waterMat.color.setHex(0xffffff);
    glowIM.setColorAt(w.i,_c);
  }
  if(glowIM.instanceColor) glowIM.instanceColor.needsUpdate=true;
}
let lampHalos=[];
lampHalos=[];

/* ══════════════════════════ 19. controls ══════════════════════════ */
class Orbit{
  constructor(cam,dom){
    this.cam=cam; this.dom=dom;
    this.tgt=new THREE.Vector3(-4,9,-2); this.tGoal=this.tgt.clone();
    this.s=new THREE.Spherical(72,1.33,-0.84); this.g=this.s.clone();
    this.ptr=new Map(); this.mode=null; this.pinch=0; this.idle=99; this.moved=false;
    dom.addEventListener('pointerdown',e=>{dom.setPointerCapture(e.pointerId);
      this.ptr.set(e.pointerId,{x:e.clientX,y:e.clientY});
      this.mode=(e.button===2||e.shiftKey)?'pan':'rot'; this.idle=0; this.moved=false;
      dom.classList.add('dragging'); if(this.ptr.size===2){this.mode='pinch';this.pinch=this.dist();}});
    dom.addEventListener('pointermove',e=>{
      if(!this.ptr.has(e.pointerId)){ onHoverMove(e); return; }
      const p=this.ptr.get(e.pointerId), dx=e.clientX-p.x, dy=e.clientY-p.y;
      p.x=e.clientX; p.y=e.clientY; this.idle=0;
      if(Math.abs(dx)+Math.abs(dy)>2) this.moved=true;
      if(this.mode==='rot'){ this.g.theta-=dx*0.0042; this.g.phi=clamp(this.g.phi-dy*0.0035,0.10,1.44); }
      else if(this.mode==='pan'){ this.pan(dx,dy); }
      else if(this.mode==='pinch'){ const d=this.dist(); this.g.radius=clamp(this.g.radius*(this.pinch/d),9,260); this.pinch=d; }
    });
    const up=e=>{this.ptr.delete(e.pointerId); if(this.ptr.size===0){this.mode=null;dom.classList.remove('dragging');
        if(!this.moved) onClickPick(e);} else if(this.ptr.size===1){this.mode='rot';}};
    dom.addEventListener('pointerup',up); dom.addEventListener('pointercancel',up);
    dom.addEventListener('contextmenu',e=>e.preventDefault());
    dom.addEventListener('wheel',e=>{e.preventDefault(); this.idle=0;
      this.g.radius=clamp(this.g.radius*Math.exp(e.deltaY*0.0009),9,260);},{passive:false});
  }
  dist(){ const a=[...this.ptr.values()]; return Math.hypot(a[0].x-a[1].x,a[0].y-a[1].y); }
  pan(dx,dy){
    const f=this.s.radius*0.0016;
    const right=new THREE.Vector3().setFromMatrixColumn(this.cam.matrix,0);
    const up=new THREE.Vector3().setFromMatrixColumn(this.cam.matrix,1);
    this.tGoal.addScaledVector(right,-dx*f).addScaledVector(up,dy*f);
    this.tGoal.y=clamp(this.tGoal.y,1,40);
    this.tGoal.x=clamp(this.tGoal.x,-90,80); this.tGoal.z=clamp(this.tGoal.z,-90,90);
  }
  flyTo(tgt,r,phi,theta){
    this.tGoal.copy(tgt);
    const nt=this.g.theta+Math.atan2(Math.sin(theta-this.g.theta),Math.cos(theta-this.g.theta));
    this.g.set(r,clamp(phi,0.1,1.44),nt);
  }
  update(dt,auto){
    this.idle+=dt;
    if(auto&&this.idle>5.5&&this.mode===null) this.g.theta+=0.05*dt;
    const k=1-Math.exp(-dt*4.2);
    this.s.radius+=(this.g.radius-this.s.radius)*k;
    this.s.phi+=(this.g.phi-this.s.phi)*k;
    this.s.theta+=(this.g.theta-this.s.theta)*k;
    this.tgt.lerp(this.tGoal,k);
    this.cam.position.setFromSpherical(this.s).add(this.tgt);
    this.cam.lookAt(this.tgt);
  }
}
const ctl=new Orbit(camera,canvas);
const VIEWS=[
 {p:[-56,23,44],t:[-4,9,-2]},{p:[9,4.2,26],t:[-8,7,-2]},
 {p:[-2.6,20.5,3],t:[-1,11,-6]},{p:[-30,12,34],t:[-15,14,20]},{p:[30,10,-26],t:[40,8,10]}
];
function setView(i){
  const v=VIEWS[i], tgt=new THREE.Vector3(...v.t), pos=new THREE.Vector3(...v.p);
  const sph=new THREE.Spherical().setFromVector3(pos.sub(tgt));
  ctl.flyTo(tgt,sph.radius,sph.phi,sph.theta);
  document.querySelectorAll('[data-view]').forEach(b=>b.classList.toggle('on',+b.dataset.view===i));
}
document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>setView(+b.dataset.view)));

/* hover + click picking */
const ray=new THREE.Raycaster(), mouse=new THREE.Vector2(-9,-9);
let hover=null, lastPick=0, tagEl=document.getElementById('tag');
function onHoverMove(e){ mouse.x=(e.clientX/innerWidth)*2-1; mouse.y=-(e.clientY/innerHeight)*2+1;
  tagEl.style.left=Math.min(e.clientX+18,innerWidth-280)+'px'; tagEl.style.top=Math.min(e.clientY+14,innerHeight-120)+'px'; }
canvas.addEventListener('pointermove',e=>{ if(!ctl.ptr.size) onHoverMove(e); });
const selBox=new THREE.Box3Helper(new THREE.Box3(),new THREE.Color(0xd5a658));
selBox.material.transparent=true; selBox.material.opacity=0; scene.add(selBox);
function doPick(){
  ray.setFromCamera(mouse,camera);
  const hit=ray.intersectObjects(pickables,false)[0];
  if(hit&&hover!==hit.object){ hover=hit.object;
    tagEl.querySelector('.t').textContent=hover.userData.label;
    tagEl.querySelector('.d').textContent=hover.userData.note||'';
    tagEl.classList.add('show');
    const b=new THREE.Box3().setFromObject(hover); selBox.box.copy(b);
    selBox.material.opacity=0.75;
  } else if(!hit&&hover){ hover=null; tagEl.classList.remove('show'); selBox.material.opacity=0; }
}
canvas.addEventListener('dblclick',()=>setView(0));
function onClickPick(e){
  if(hover){ const c=new THREE.Vector3(); hover.geometry.computeBoundingSphere();
    c.copy(hover.position);
    const b=new THREE.Box3().setFromObject(hover); b.getCenter(c);
    const size=b.getSize(new THREE.Vector3()).length();
    const dir=new THREE.Vector3().subVectors(camera.position,ctl.tgt).normalize();
    ctl.flyTo(c,size*0.9+14,clamp(ctl.g.phi,0.5,1.25),ctl.g.theta);
  }
}

/* ══════════════════════════ 20. UI ══════════════════════════ */
let hour=17.05, dayCycle=false, autoSpin=true, dressed=false;
const tod=document.getElementById('tod'), sea=document.getElementById('sea');
const todLbl=document.getElementById('todLbl'), clockEl=document.getElementById('clock'),
      windEl=document.getElementById('wind'), logEl=document.getElementById('log');
function hhmm(h){const H=Math.floor(mod(h,24)),M=Math.floor(mod(h%1,1)*60);return String(H).padStart(2,'0')+':'+String(M).padStart(2,'0');}
function fillSlider(el){const p=(el.value-el.min)/(el.max-el.min)*100;
  el.style.setProperty('--p',p);
  el.style.background=`linear-gradient(90deg,var(--brass) ${p}%, rgba(213,166,88,.18) ${p}%)`;}
tod.addEventListener('input',()=>{hour=+tod.value;fillSlider(tod);});
sea.addEventListener('input',()=>{waveAmp=+sea.value;fillSlider(sea);
  const n=waveAmp<0.35?'glassy':waveAmp<0.7?'moderate':waveAmp<1.1?'rough':'a good blow';
  document.getElementById('seaLbl').textContent=n;});
document.getElementById('spin').addEventListener('click',e=>{autoSpin=!autoSpin;e.target.classList.toggle('on',autoSpin);});
document.getElementById('cycle').addEventListener('click',e=>{dayCycle=!dayCycle;e.target.classList.toggle('on',dayCycle);});
document.getElementById('dress').addEventListener('click',e=>{dressed=!dressed;
  dressLine.visible=dressed; e.target.classList.toggle('on',dressed);
  setLog(dressed?'Dressed overall for the harbour festival — every masthead to the rail in signal bunting.'
    :'Bunting struck. She rides plain now, ready for the next tide.');});
dressLine.visible=false;
const LOGS=[[4,'Harbour lights burning. A cat watches the quay from the custom house steps.'],
 [7,'Morning tide. Nets off the fish quay, gulls arguing over the first crates.'],
 [10,'The cooper has the yard full again. Wind steady from the southwest.'],
 [13,'Slack water. Paint coming off the hull in good light — best hour for a drawing.'],
 [16,'<b>Cormorant</b> signals for a berth. The pilot is already in the boat.'],
 [18,'She takes the long wharf. Four lines out, gangway down, cargo next light.'],
 [20,'Harbour lamps lit. The light flashes twice every twelve seconds.'],
 [23,'Quiet water. Only the mill sails and the swell are still moving.']];
let curLog=-1;
function setLog(html){ logEl.classList.add('swap'); setTimeout(()=>{logEl.innerHTML=html;logEl.classList.remove('swap');},380); }
function updateLog(){
  let idx=0; for(let i=0;i<LOGS.length;i++) if(hour>=LOGS[i][0]) idx=i;
  if(idx!==curLog){curLog=idx; setLog(LOGS[idx][1]);}
}

/* ══════════════════════════ 21. loop ══════════════════════════ */
let glowIM;
{ const g=bake(glow,new THREE.MeshBasicMaterial({color:0xffffff}),false,false); glowIM=g; scene.add(glowIM); }
const baked=bake(solid,new THREE.MeshLambertMaterial({color:0xffffff}),true,true);
scene.add(baked);

setView(0); ctl.s.set(VIEWS[0][0]?ctl.g.radius:72,ctl.g.phi,ctl.g.theta);
ctl.s.radius=118; ctl.s.phi=1.18; ctl.s.theta=2.15;
fillSlider(tod); fillSlider(sea); updateLog();

const clock=new THREE.Clock(); let frames=0;
function tick(){
  const dt=Math.min(clock.getDelta(),0.05), t=clock.elapsedTime;
  if(dayCycle){ hour=mod(hour+dt*0.42,24); tod.value=hour; fillSlider(tod); updateLog(); }
  updateSky(hour);
  updateWater(t); updateFoam(t);
  glintMat.uniforms.uTime.value=t; glintMat.uniforms.uCam.value.copy(camera.position);
  glintMat.uniforms.uAmp.value=waveAmp;
  smokeMat.uniforms.uTime.value=t;
  for(let i=0;i<SM_SRC;i++){ const s=smokeSources[i];
    if(i===5){ smokeMat.uniforms.uSrc.value[i].copy(tug.position).add(new THREE.Vector3(0.6,6.4,1.4)); }
    else smokeMat.uniforms.uSrc.value[i].copy(s);
  }
  // ship motion
  const roll=0.020*Math.sin(t*0.52)+0.011*Math.sin(t*0.87+1.3);
  const pitch=0.012*Math.sin(t*0.41+0.7);
  ship.rotation.set(pitch,roll,Math.sin(t*0.31)*0.004);
  ship.position.y=waveY(ship.position.x,ship.position.z,t)*0.55-0.05+0.06*Math.sin(t*0.62);
  ship.updateMatrixWorld(true);
  // sails flutter
  for(let i=0;i<sailData.length;i++){
    const s=sailData[i];
    const f=0.13*Math.sin(t*2.1+s.ph+s.u*2.4)+0.07*Math.sin(t*3.7+s.ph*2+s.y*0.3);
    const d=s.dep*(1+0.16*Math.sin(t*1.3+s.ph));
    _m.compose(_v.set(s.x+f*0.2,s.y+0.02*Math.sin(t*2.4+s.ph),s.z+d+f),_q.identity(),_v.set(1,1,1));
    sailIM.setMatrixAt(i,_m);
  }
  sailIM.instanceMatrix.needsUpdate=true;
  updateFlags(t);
  updateRopes(t); updateGang(t);
  // small craft follow the sea
  const bob=(g,x,z,r)=>{ g.position.y=waveY(x,z,t)*0.62-0.04;
    g.rotation.z=Math.sin(x*0.11+t*1.15)*0.05*waveAmp+Math.sin(t*0.7+r)*0.02;
    g.rotation.x=Math.cos(z*0.09-t*0.95)*0.05*waveAmp; };
  bob(boatA,-2.5,-27,0); bob(boatB,4.5,30,1.7); bob(tug,-30,-30,2.4); bob(schooner,-60,-60,3.1);
  boatsCrew[0].position.copy(boatA.position); boatsCrew[0].rotation.copy(boatA.rotation);
  for(const b of buoys) bob(b.g,b.g.position.x,b.g.position.z,b.ph);
  // gulls
  for(const g of gulls){
    g.a+=g.sp*dt;
    const x=g.cx+Math.cos(g.a)*g.r, z=g.cz+Math.sin(g.a)*g.r*0.8;
    const y=g.cy+Math.sin(t*0.8+g.bob)*2.2;
    g.g.position.set(x,y,z);
    g.g.rotation.y=-g.a+(g.sp>0?Math.PI/2:-Math.PI/2);
    g.g.rotation.z=Math.sin(g.a*2)*0.12;
    const fl=Math.sin(t*9+g.bob);
    g.ws[0].rotation.x=-fl*0.75; g.ws[1].rotation.x=fl*0.75;
    g.g.children[0].rotation.x=fl*0.06;
  }
  // clouds drift
  const a=cloudIM.instanceMatrix.array;
  const spd=[0.55,1.0,1.7][0]||0.55;
  for(let i=0;i<cloudArr.length/7;i++){
    let x=cloudX[i]+t*0.55; x=mod(x+140,280)-140;
    const o=i*16; a[o+12]=x;
  }
  cloudIM.instanceMatrix.needsUpdate=true;
  millHub.rotation.z-=dt*0.55;
  beams.rotation.y+=dt*0.55;
  // walkers
  for(const w of walkers){
    w.t+=w.sp*dt; if(w.t>1) w.t-=1;
    const u=0.5-0.5*Math.cos(w.t*Math.PI*2);
    const x=lerp(w.x0,w.x1,u), z=lerp(w.z0,w.z1,u);
    const y=terrainH(Math.round(x),Math.round(z))||5;
    w.g.position.set(x,y,z);
    const dx=lerp(w.x1,w.x0,u), dz=lerp(w.z1,w.z0,u);
    w.g.rotation.y=Math.atan2(-dx,-dz)+Math.PI;
    w.g.position.y+=Math.abs(Math.sin(w.t*40+w.ph))*0.07;
  }
  // hover pick throttle
  if(t-lastPick>0.07){ lastPick=t; if(!ctl.ptr.size) doPick(); }
  ctl.update(dt,autoSpin);
  renderer.render(scene,camera);
  if(frames++===2){ document.getElementById('veil').classList.add('gone'); }
  requestAnimationFrame(tick);
}
requestAnimationFrame(tick);

/* clock text */
setInterval(()=>{ todLbl.textContent=hhmm(hour); clockEl.textContent=hhmm(hour);
  const el=Math.sin(clamp((hour-5.9)/13,0,1)*Math.PI);
  const az=10+clamp((hour-5.9)/13,0,1)*258;
  const dirs=['E','ENE','NE','NNE','N','NNW','NW','WNW','W','WSW','SW','SSW','S','SSE','SE','ESE'];
  const wd=dirs[Math.round(((270-az)%360+360)%360/22.5)%16];
  windEl.textContent=(hour>6&&hour<19)?`${wd} ${Math.round(4+waveAmp*4)} kn · ${el<0.35?(hour<12?'dawn light':'falling light'):'high sun'}`
    :`${wd} ${Math.round(3+waveAmp*3)} kn · lights`;
},600);

addEventListener('resize',()=>{ camera.aspect=innerWidth/innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight); });
</script>
</body>
</html>
```

**What's in there**

- **The ship:** a three-masted barque built block by block — sheer line, raked bow with figurehead and bowsprit, gold wale, gunports, lit stern windows and stern lantern, forecastle, capstan, hatches, barrels, a boat on davits, four crew, and a gangway whose ship-side end actually tracks the hull as she rolls. Four mooring lines sag between the ship's bits and the quay bollards, re-solved every frame.
- **The harbor:** dressed quay wall with buttresses, long wharf and fish quay on timber piles, bale warehouse with a loading derrick, custom house with colonnade and cupola, St Brendan's with clock tower and lead spire, cottages terraced up the hillside, an upland windmill with turning sails, ropewalks, chimneys trailing drifting smoke, lampposts, crates, barrels, rope coils, a hand cart, hedges, trees and nine dockworkers walking their beats.
- **Graywater Light** at the wharf head with a rotating additive beam, and a coal tug and a furled schooner out in the roads.
- **The sea:** ~3,400 animated water columns (a single instanced draw), a physically-suggestive sun-glitter path, foam collars at the waterline, buoys, gulls with flapping wings.
- **Time of day** is a full keyframed lighting rig: sun azimuth/elevation, sky gradient, fog, hemisphere, water tint, star field, moon, lamp glows and window glass all lerp between nine stops — drag the slider or hit **Day cycle** and watch the harbour go from dawn to watch-time.
- **Interaction:** drag to orbit, wheel to zoom, right-drag to pan, hover the wharf/lighthouse/tug/schooner for a survey card with a bracket, click to focus the camera there, double-click to return to the wide view.