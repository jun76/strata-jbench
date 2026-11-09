# Calling at the Harbour — a voxel diorama

Drop this into a single `.html` file and open it in Chrome. Everything builds itself on load: the harbour (quay, breakwater, lighthouse, warehouses, crane, clock tower, lamps), the barque being worked up the channel alongside the dock, animated swell, gulls, mooring lines that string themselves once she's tied up, and a full day-cycle slider. Drag to orbit, scroll to zoom, right-drag to pan.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Calling at the Harbour — voxel diorama</title>
<style>
  :root{ --paper:#e9e4da; --brass:#c8a24a; --ink:#080d11; }
  *{box-sizing:border-box}
  html,body{margin:0;height:100%;overflow:hidden;background:#04080b;
    font-family:ui-monospace,"SFMono-Regular",Menlo,Consolas,monospace;color:var(--paper)}
  canvas{display:block;cursor:grab}
  canvas:active{cursor:grabbing}
  #hud{position:fixed;inset:0;pointer-events:none;z-index:5;user-select:none}
  .p{position:absolute;background:linear-gradient(180deg,rgba(9,15,20,.88),rgba(9,15,20,.72));
     border:1px solid rgba(200,162,74,.34);padding:12px 14px;box-shadow:0 6px 30px rgba(0,0,0,.35)}
  #title{top:18px;left:18px;max-width:min(520px,70vw)}
  #title .k{font-size:10px;letter-spacing:.32em;color:var(--brass);opacity:.9}
  #title .t{font-family:Georgia,"Times New Roman",serif;font-size:32px;letter-spacing:.03em;margin:6px 0 2px}
  #title .s{font-size:11px;opacity:.6;letter-spacing:.04em}
  #title .hint{font-size:10px;opacity:.45;margin-top:6px}
  #log{bottom:18px;left:18px;width:min(430px,72vw);font-size:11px;line-height:1.45}
  #log div{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;opacity:.55;transition:opacity .4s}
  #log div:last-child{opacity:1}
  #log .t{color:#6f8f9e;opacity:.45}
  #log .new{color:var(--brass);text-shadow:0 0 12px rgba(200,162,74,.25)}
  #panel{bottom:18px;right:18px;width:252px}
  #readout{display:grid;grid-template-columns:1fr 1fr;gap:2px 10px;font-size:11px;margin-bottom:10px}
  #readout b{color:var(--brass);font-weight:400;display:block;opacity:.65;font-size:9.5px;letter-spacing:.15em}
  #readout span{display:block;font-variant-numeric:tabular-nums}
  .row{display:flex;gap:6px;margin-top:6px}
  button{flex:1;min-width:0;pointer-events:auto;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.16);
    color:var(--paper);font:inherit;font-size:9.5px;letter-spacing:.12em;padding:6px 4px;cursor:pointer;text-transform:uppercase;transition:.15s}
  button:hover{border-color:var(--brass);color:#fff;background:rgba(200,162,74,.12)}
  button.on{background:rgba(200,162,74,.22);border-color:var(--brass);color:#fff}
  input[type=range]{width:100%;pointer-events:auto;appearance:none;height:3px;background:linear-gradient(90deg,#101a22,#3d5570,#f2a03f,#0a1018);
    border:1px solid rgba(255,255,255,.2);margin:8px 0 4px;cursor:ew-resize}
  input[type=range]::-webkit-slider-thumb{appearance:none;width:11px;height:11px;background:var(--brass);border-radius:2px;box-shadow:0 0 8px rgba(200,162,74,.7)}
  .lab{font-size:9px;letter-spacing:.18em;color:#7f94a1;display:flex;justify-content:space-between}
  #load{position:fixed;inset:0;z-index:9;background:#04080b;display:flex;align-items:center;justify-content:center;
    font-size:11px;letter-spacing:.35em;color:var(--brass);transition:opacity .8s}
</style>
</head>
<body>
<div id="hud">
  <div class="p" id="title">
    <div class="k">PORT OF CALDBRACK · No. 3 ANCHORAGE</div>
    <div class="t">Calling at the Harbour</div>
    <div class="s">a voxel diorama in four-masted-barque scale</div>
    <div class="hint">drag to orbit &nbsp;· scroll to zoom &nbsp;· right-drag to pan</div>
  </div>
  <div class="p" id="log"></div>
  <div class="p" id="panel">
    <div id="readout"></div>
    <div class="lab"><span>TIME OF DAY</span><span id="tl">AFTERNOON</span></div>
    <input id="tod" type="range" min="0" max="1000" value="615">
    <div class="row">
      <button id="bRun">Replay arrival</button>
      <button id="bSail">Set sail</button>
    </div>
    <div class="row">
      <button id="bOrbit" class="on">Auto-orbit</button>
      <button id="bRig">Rigging</button>
      <button id="bBoom">Fire salute</button>
      <button id="bAud">Ambience</button>
    </div>
  </div>
</div>
<div id="load">CHARTING THE CHANNEL…</div>

<script type="importmap">
{ "imports": {
  "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
  "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
}}
</script>
<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* ================= helpers ================= */
const c01 = v => v<0?0:v>1?1:v;
const lerp = (a,b,t)=>a+(b-a)*t;
const sstep = (a,b,x)=>{const t=c01((x-a)/(b-a));return t*t*(3-2*t);};
const R = (a,b)=>a+Math.random()*(b-a);
const RI = (a,b)=>Math.floor(a+Math.random()*(b-a+1));
function vary(hex,amt){
  const r=(hex>>16)&255,g=(hex>>8)&255,b=hex&255;
  const f=1+(Math.random()-0.5)*amt;
  const cl=v=>Math.max(0,Math.min(255,Math.round(v*f)));
  return (cl(r)<<16)|(cl(g)<<8)|cl(b);
}

/* ================= voxel builder ================= */
class Builder{
  constructor(){ this.m=new Map(); this.a=[]; }
  key(x,y,z){ return (x+512)*1048576 + (y+512)*1024 + (z+512); }
  set(x,y,z,c){ x=Math.round(x);y=Math.round(y);z=Math.round(z);
    const k=this.key(x,y,z); let i=this.m.get(k);
    if(i===undefined){ i=this.a.length; this.m.set(k,i); this.a.push([x,y,z,c]); } else this.a[i][3]=c; }
  del(x,y,z){ x=Math.round(x);y=Math.round(y);z=Math.round(z); this.m.delete(this.key(x,y,z)); }
  has(x,y,z){ return this.m.has(this.key(x,y,z)); }
  box(x0,y0,z0,w,h,d,c){
    for(let x=x0;x<x0+w;x++)for(let y=y0;y<y0+h;y++)for(let z=z0;z<z0+d;z++)
      this.set(x,y,z, typeof c==='function'? c(x,y,z) : c);
  }
  line(p,q,c){
    const d=[q[0]-p[0],q[1]-p[1],q[2]-p[2]];
    const n=Math.max(1,Math.ceil(Math.max(Math.abs(d[0]),Math.abs(d[1]),Math.abs(d[2]))));
    for(let i=0;i<=n;i++){const t=i/n; this.set(p[0]+d[0]*t,p[1]+d[1]*t,p[2]+d[2]*t,typeof c==='function'?c(p[0]+d[0]*t,p[1]+d[1]*t,p[2]+d[2]*t):c);}
  }
  mesh({cull=true,cast=true,recv=true,mat=null,geo=new THREE.BoxGeometry(1,1,1)}={}){
    const list=[];
    for(const v of this.a){
      if(!this.m.has(this.key(v[0],v[1],v[2]))) continue;
      if(cull && this.has(v[0]+1,v[1],v[2])&&this.has(v[0]-1,v[1],v[2])&&this.has(v[0],v[1]+1,v[2])
                 &&this.has(v[0],v[1]-1,v[2])&&this.has(v[0],v[1],v[2]+1)&&this.has(v[0],v[1],v[2]-1)) continue;
      list.push(v);
    }
    const m=new THREE.InstancedMesh(geo, mat||new THREE.MeshLambertMaterial(), list.length);
    const d=new THREE.Object3D(), col=new THREE.Color();
    list.forEach((v,i)=>{ d.position.set(v[0],v[1],v[2]); d.updateMatrix(); m.setMatrixAt(i,d.matrix); m.setColorAt(i,col.setHex(v[3])); });
    m.instanceMatrix.needsUpdate=true; if(m.instanceColor) m.instanceColor.needsUpdate=true;
    m.castShadow=cast; m.receiveShadow=recv; m.frustumCulled=false;
    return m;
  }
}

/* ================= palette ================= */
const P={
  seaDeep:0x1b4a63, sea:0x2f7d92, seaShal:0x5fafbd, foam:0xdff2ef,
  rock:0x6f6c64, rockDk:0x4c4b45, mossRock:0x5e6f4f,
  granite:0x9d978c, graniteW:0x6f6c63, graniteD:0x50514a,
  cobble:0x8d867a, cobbleD:0x6b665e, kerb:0xb0a897,
  dirt:0x7d6a4d, sand:0xc7ad7c, grass:0x6c8d4b, grassD:0x53723a,
  fern:0x7a9a56,
  oakDark:0x422c19, oak:0x6b4527, oakLite:0x8b5c34, spar:0x835e36, sparDark:0x563a22,
  deck:0xa67c4b, deckDk:0x88643b, hatch:0xc19a63,
  wale:0xd7a544, hull:0x6b4429, hullDk:0x4d2f1d, hullLt:0x7f5533,
  copper:0x8a4429, boot:0x1d1719, bottom:0x29403a, waterline:0xb27c3e,
  bulwkWhite:0xece5d6, bulwkDk:0x5a3d26, paint:0xb03f36,
  sailA:0xe9dfc7, sailB:0xd3c6a6,
  rope:0xb48e56, iron:0x3c3d41,
  crate:0x9a7145, crateL:0xb98d55, barrel:0x8b5f33, barrelDk:0x4e3218,
  brick:0x8f4539, brickDk:0x6c332c, mortar:0xa05a48,
  plaster:0xe5ddca, plasterDk:0xbdb39d,
  slate:0x4d5660, slateDk:0x374048,
  tile:0xb0523a, tileDk:0x87402f,
  green:0x2f6b68, greenDk:0x24504e,
  win:0x2a3138, lampGlow:0xffd07a, pane:0xffbe62,
  glass:0x1f2c39, white:0xf3efe5,
  gold:0xc8a24a,
};

/* ================= renderer / scene ================= */
const renderer=new THREE.WebGLRenderer({antialias:true,powerPreference:'high-performance'});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.setSize(innerWidth,innerHeight);
renderer.shadowMap.enabled=true;
renderer.shadowMap.type=THREE.PCFSoftShadowMap;
renderer.outputColorSpace=THREE.SRGBColorSpace;
document.body.appendChild(renderer.domElement);

const scene=new THREE.Scene();
scene.fog=new THREE.FogExp2(0xb2c9d9,0.0026);
const camera=new THREE.PerspectiveCamera(42,innerWidth/innerHeight,1,2200);
camera.position.set(34,64,96);
const controls=new OrbitControls(camera,renderer.domElement);
controls.target.set(-2,12,6);
controls.enableDamping=true; controls.dampingFactor=0.06;
controls.minDistance=26; controls.maxDistance=330;
controls.maxPolarAngle=Math.PI*0.485; controls.minPolarAngle=0.12;
controls.autoRotate=true; controls.autoRotateSpeed=0.35;

/* ================= lights ================= */
const hemi=new THREE.HemisphereLight(0x9cc0e4,0x5c5a4c,1.0); scene.add(hemi);
const sunLight=new THREE.DirectionalLight(0xffffff,2.4);
sunLight.castShadow=true;
sunLight.shadow.mapSize.set(2048,2048);
sunLight.shadow.camera.near=40; sunLight.shadow.camera.far=520;
sunLight.shadow.camera.left=-110; sunLight.shadow.camera.right=110;
sunLight.shadow.camera.top=110; sunLight.shadow.camera.bottom=-110;
sunLight.shadow.bias=-0.0005; sunLight.shadow.normalBias=0.22;
sunLight.target.position.set(0,8,0); scene.add(sunLight,sunLight.target);
const moonLight=new THREE.DirectionalLight(0x8fa8d0,0); scene.add(moonLight);

const skyU={top:{value:new THREE.Color()},hor:{value:new THREE.Color()},bot:{value:new THREE.Color()}};
const sky=new THREE.Mesh(new THREE.SphereGeometry(900,32,20),new THREE.ShaderMaterial({
  uniforms:skyU,side:THREE.BackSide,depthWrite:false,fog:false,
  vertexShader:`varying vec3 vP; void main(){ vP=position; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
  fragmentShader:`varying vec3 vP; uniform vec3 top,hor,bot;
    void main(){ float h=normalize(vP).y;
      vec3 c=mix(hor,top,smoothstep(0.0,0.42,h));
      c=mix(bot,c,smoothstep(-0.14,0.02,h));
      gl_FragColor=vec4(c,1.); #include <colorspace_fragment> }`
}));
scene.add(sky);

const sunDisc=new THREE.Mesh(new THREE.SphereGeometry(15,24,16),new THREE.MeshBasicMaterial({fog:false}));
const moonDisc=new THREE.Mesh(new THREE.SphereGeometry(9,24,16),new THREE.MeshBasicMaterial({color:0xd6e6f5,fog:false,transparent:true,opacity:0}));
scene.add(sunDisc,moonDisc);

const starGeo=new THREE.BufferGeometry(); const sp=[];
for(let i=0;i<1600;i++){ const v=new THREE.Vector3().randomDirection().multiplyScalar(780); if(v.y<0)v.y=-v.y*0.9; sp.push(v.x,v.y,v.z); }
starGeo.setAttribute('position',new THREE.Float32BufferAttribute(sp,3));
const stars=new THREE.Points(starGeo,new THREE.PointsMaterial({color:0xffffff,size:2.1,sizeAttenuation:false,transparent:true,opacity:0,fog:false,depthWrite:false}));
scene.add(stars);

/* ================= sea state ================= */
function calm(x,z){
  const wall=sstep(-14,6,(-26*(x-17)+59*(z+28))/64.6);
  const quay=sstep(20,12,x);
  const far=1-sstep(60,90,z);
  return c01(wall*quay*far);
}
function waveY(x,z,t){
  const c=calm(x,z), a=0.28+0.95*(1-c);
  return a*(0.55*Math.sin(x*0.115+t*1.15)+0.38*Math.sin(z*0.085-t*0.9)+0.18*Math.sin((x*0.35+z*0.5)*0.2+t*2.1))*(0.55+0.45*c);
}

/* ================= water ================= */
const cells=[];
for(let z=-90;z<=90;z+=3){
  const maxW=(z>=-22&&z<=58)?16:26;
  for(let x=-105;x<maxW;x+=3) cells.push([x,z]);
}
const waterMat=new THREE.MeshLambertMaterial({color:0xffffff});
const water=new THREE.InstancedMesh(new THREE.BoxGeometry(3,3,3),waterMat,cells.length);
water.castShadow=false; water.receiveShadow=true; water.frustumCulled=false;
scene.add(water);
const bR=new Float32Array(cells.length),bG=new Float32Array(cells.length),bB=new Float32Array(cells.length);
{
  const deep=new THREE.Color(P.seaDeep), mid=new THREE.Color(P.sea), shal=new THREE.Color(P.seaShal), c1=new THREE.Color();
  cells.forEach(([x,z],i)=>{
    const sh=sstep(-26,12,x)*0.85+c01(sstep(-70,-40,z)*(1-sstep(20,40,z))*0.2);
    c1.copy(deep).lerp(mid,sstep(-80,10,x)).lerp(shal,sh*sh*0.75);
    if(calm(x,z)>0.5) c1.lerp(new THREE.Color(0x4a9bab),0.25);
    bR[i]=c1.r; bG[i]=c1.g; bB[i]=c1.b;
  });
}
// distant horizon fill
const horizon=new THREE.Mesh(new THREE.CircleGeometry(800,48),new THREE.MeshLambertMaterial({color:0x1e5468}));
horizon.rotation.x=-Math.PI/2; horizon.position.y=-0.72; horizon.receiveShadow=false; scene.add(horizon);

/* ================= builders ================= */
const HB=new Builder(), GW=new Builder();       // harbour, glowing voxels
const glowMat=new THREE.MeshBasicMaterial({color:0xffffff});

/* ---------- land ---------- */
function g(x,z,r){ return Math.exp(-(x*x+z*z)/(r*r)); }
function groundH(x,z){
  const t=sstep(30,46,x);
  let h=8;
  h+=t*(9*g(x-56,z-46,15)+11*g(x-52,z+18,14)+7*g(x-44,z+58,13)+6*g(x-63,z-8,11));
  h+=1.2*g(x-29,z,4);
  return Math.round(h);
}
for(let x=27;x<=66;x++)for(let z=-70;z<=70;z++){
  const h=Math.max(3,groundH(x,z));
  for(let y=h-1;y>=-1;y--){
    let c;
    if(y===h-1)      c = (h<=9? vary(P.grass,0.16) : vary(h>12?P.rockDk:P.fern,0.15));
    else if(y===h-2) c = (h<=9? vary(P.dirt,0.14) : vary(P.rock,0.14));
    else if(y===0)   c = vary(P.sand,0.12);
    else             c = vary(P.rockDk,0.10);
    HB.set(x,y,z,c);
  }
}

/* ---------- quay ---------- */
const Q0=-22,Q1=58;
for(let z=Q0;z<=Q1;z++){
  HB.set(16,3,z,vary(P.granite,0.1)); HB.set(16,2,z,vary(P.granite,0.1)); HB.set(16,1,z,vary(P.graniteD,0.1));
  HB.set(15,0,z,vary(P.graniteD,0.12)); HB.set(15,-1,z,vary(P.graniteW,0.12)); HB.set(14,-2,z,vary(P.graniteW,0.12));
}
for(let x=17;x<=26;x++)for(let z=Q0;z<=Q1;z++){
  const seam=((x*3+z*5)%9===0);
  HB.set(x,7,z,vary(seam?P.cobbleD:P.cobble,0.11));
  if(z%4===0) HB.set(x,7,z,vary(P.cobbleD,0.08));
  for(let y=3;y<=6;y++) HB.set(x,y,z,vary(z%3===0?P.granite:P.graniteW,0.10));
  for(let y=-4;y<=2;y++) HB.set(x,y,z,vary(y<0?P.graniteD:P.graniteW,0.12));
}
for(let z=Q0;z<=Q1;z++){ HB.set(17,8,z,vary(P.kerb,0.06)); HB.set(18,8,z,vary(P.kerb,0.06)); }
// water stairs
for(let i=0;i<7;i++) HB.box(17+i,7-i,34+i,6-i,1,5,vary(P.granite,0.10));
// bollards + coils
function bollard(b,x,z){ b.box(x,9,z,1,1,1,vary(P.iron,0.1)); b.set(x,10,z,vary(0x6b6b70,0.1)); b.box(x-1,8,z,3,1,3,vary(P.iron,0.15)); }
const BOLL=[26,18,8,-2,-12,-18];
BOLL.forEach(z=>bollard(HB,16,z));
function ropeCoil(b,x,z){ for(let i=0;i<8;i++){const a=i/8*Math.PI*2; b.set(Math.round(x+Math.cos(a)*1.2),8,Math.round(z+Math.sin(a)*1.2),vary(P.rope,0.15));} b.set(x,8,z,vary(P.rope,0.1)); }
[22,10,0,-14].forEach(z=>ropeCoil(HB,19,z));

/* ---------- lamps ---------- */
function lamp(b,g,x,z){
  b.box(x-1,8,z-1,3,1,3,vary(0x44464a,0.1));
  b.line([x,9,z],[x,17,z],vary(0x2f3134,0.1));
  b.box(x-1,18,z-1,3,1,3,vary(0x2f3134,0.1));
  b.set(x,19,z,vary(0x2f3134,0.1));
  for(let y=16;y<=17;y++){ g.set(x-1,y,z,P.lampGlow); g.set(x+1,y,z,P.lampGlow); g.set(x,y,z-1,P.lampGlow); g.set(x,y,z+1,P.lampGlow); g.set(x,y,z,0xffe4a8); }
  b.box(x-2,14,z,5,1,1,vary(0x2f3134,0.1));
}
[2,14,26,42].forEach(z=>lamp(HB,GW,21,z));
const lampLights=[];
[2,14,26,42].forEach(z=>{ const l=new THREE.PointLight(0xffb761,0,50,2); l.position.set(21,16.5,z); scene.add(l); lampLights.push(l); });

/* ---------- breakwater + lighthouse ---------- */
{
  const a=[20,-24],b=[-44,-55], dc=[b[0]-a[0],b[1]-a[1]], len=Math.hypot(dc[0],dc[1]), n=[-dc[1]/len,dc[0]/len];
  for(let s=0;s<len;s+=1){
    const px=a[0]+dc[0]*s/len, pz=a[1]+dc[1]*s/len, t=c01((-s-4)/-len);
    const top=Math.round(2.2+4.6*t+1.1*Math.sin(s*0.7));
    for(let wv=-3;wv<=3;wv++){
      const x=Math.round(px+n[0]*wv), z=Math.round(pz+n[1]*wv);
      const dep=Math.abs(wv), h=top-Math.max(0,Math.round(dep-1.6));
      for(let y=-3;y<=h;y++) HB.set(x,y,z, y===h? vary(dep>2?P.rockDk:P.mossRock,0.15) : vary(P.rock,0.15));
    }
  }
  // lighthouse
  const cx=-44,cz=-55;
  HB.box(cx-4,3,cz-4,9,4,9,(x,y,z)=>vary(y>5?P.graniteW:P.graniteD,0.1));
  const tiers=[[3,7,11,P.plaster],[2,12,16,P.paint],[2,17,21,P.plaster],[1,22,24,P.paint]];
  for(const [r,y0,y1,c] of tiers)
    HB.box(cx-r,y0,cz-r,2*r+1,y1-y0+1,2*r+1,(x,y,z)=>vary((y%2===0)?c:vary(c,0.06),0.05));
  HB.set(cx-1,14,cz-2,P.glass); HB.set(cx-1,17,cz-2,P.glass);
  HB.box(cx-3,25,cz-3,7,1,7,vary(0x33353a,0.1));
  for(let dx=-2;dx<=2;dx++)for(let dz=-2;dz<=2;dz++) if(Math.abs(dx)===2||Math.abs(dz)===2) HB.set(cx+dx,26,cz+dz,vary(0x33353a,0.1));
  for(let y=27;y<=28;y++) for(let dx=-1;dx<=1;dx++) for(let dz=-1;dz<=1;dz++){
    if(Math.abs(dx)+Math.abs(dz)===2) HB.set(cx+dx,y,cz+dz,vary(0x2c2f33,0.1));
    else if(dx===0&&dz===0) GW.set(cx,y,cz,0xfff1c8);
    else GW.set(cx+dx,y,cz+dz,P.lampGlow);
  }
  HB.box(cx-2,29,cz-2,5,1,5,vary(0x9d3b32,0.1)); HB.line([cx,30,cz],[cx,34,cz],0x555a60);
  const beacon=new THREE.PointLight(0xffdf9e,0,260,2); beacon.position.set(cx,27.5,cz); scene.add(beacon);
  const cone=new THREE.Mesh(new THREE.ConeGeometry(11,110,2,1,true),
    new THREE.MeshBasicMaterial({color:0xffe2a0,transparent:true,opacity:0,depthWrite:false,side:THREE.DoubleSide,fog:false,blending:THREE.AdditiveBlending}));
  cone.rotation.z=Math.PI/2; cone.position.x=55; cone.renderOrder=3;
  const piv=new THREE.Group(); piv.position.set(cx,27.5,cz); piv.add(cone); scene.add(piv);
  window.__beacon={piv,cone,beacon};
}

/* ---------- buildings ---------- */
function winCut(b,g,f,fz,fy,w,h,pane){
  for(let z=Math.round(fz-w/2);z<=Math.round(fz+w/2);z++)
    for(let y=Math.round(fy-h/2);y<=Math.round(fy+h/2);y++){ b.del(f,y,z); g.set(f,y,z,pane); }
}
function warehouse(b,gw,o){
  const {x0,x1,z0,z1,h,wall,roof,rh=4,ridge='z'}=o, yb=8;
  for(let x=x0;x<=x1;x++)for(let z=z0;z<=z1;z++)for(let y=yb;y<yb+h;y++){
    if(x===x0||x===x1||z===z0||z===z1) b.set(x,y,z,vary(y===yb+h-1?P.mortar:wall,0.09));
    else if(y===yb) b.set(x,y,z,vary(0x534635,0.08));
  }
  const c0=(ridge==='z')?(z0+z1)/2:(x0+x1)/2, span=(ridge==='z')?z1-z0:x1-x0;
  for(let z=z0-1;z<=z1+1;z++){
    for(let x=x0-1;x<=x1+1;x++){
      const d=Math.abs((ridge==='z')?z-c0:x-c0);
      const top=yb+h+Math.max(0,Math.round(rh-d*0.9));
      for(let y=yb+h;y<=top;y++) b.set(x,y,z, y===top?vary(roof,0.10):(y>=top-1?vary(P.slateDk,0.1):0x453d36));
    }
  }
}
// Bond warehouse
warehouse(HB,GW,{x0:44,x1:62,z0:-20,z1:-2,h:10,wall:P.brick,roof:P.slate,rh:5});
for(let z=-18;z<=-4;z+=4) for(let y=10;y<=12;y++) winCut(HB,GW,44,z,y,1,3,vary(P.pane,0.15));
for(let z=-18;z<=-4;z+=4){ HB.set(44,9,z,vary(P.stone||P.graniteW,0.1)); }
HB.box(43,8,-11,2,3,2,P.oakDark); GW.set(43,10,-11,P.pane);
HB.box(44,14,-11,1,1,1,P.oakDark); HB.line([45,13,-8],[45,13,-14],P.oakDark);
// Customs house
warehouse(HB,GW,{x0:30,x1:44,z0:20,z1:38,h:7,wall:P.plaster,roof:P.tile,rh:3});
for(let z=22;z<=36;z+=4){ winCut(HB,GW,30,11,z,2,2,vary(P.pane,0.1)); winCut(HB,GW,30,15,z,2,2,vary(P.pane,0.1)); }
HB.box(29,8,28,2,4,3,vary(P.graniteW,0.08)); HB.set(28,11,28,vary(P.granite,0.06));
HB.box(29,8,30,2,4,3,vary(P.graniteW,0.08)); HB.set(28,11,30,vary(P.granite,0.06));
HB.box(28,12,27,2,1,7,vary(P.granite,0.05)); HB.box(31,8,29,1,4,1,P.paint); GW.set(31,10,29,P.pane);
HB.line([37,11,37],[37,20,37],0x888070);
// clock tower
{
  const tx=54,tz=32;
  HB.box(tx-4,8,tz-4,9,15,9,(x,y,z)=>vary(y%3===0?P.plasterDk:P.plaster,0.06));
  for(let s=0;s<9;s++){ HB.set(tx-4+s,23,tz-4,s===8?P.granite:vary(P.granite,0.06)); HB.set(tx-4+s,23,tz+4,s===8?P.granite:vary(P.granite,0.06)); }
  HB.box(tx-3,23,tz-3,7,1,7,vary(P.graniteW,0.06));
  HB.box(tx-2,24,tz-2,5,3,5,(x,y,z)=>vary(P.paint,0.08));
  HB.box(tx-1,27,tz-1,3,1,3,vary(P.paint,0.08));
  for(let y=24;y<=26;y++) for(let dx=-2;dx<=2;dx++){ if(Math.abs(dx)<2) GW.set(tx+dx,y,tz-3,0xf7f3ea); }
  for(let y=24;y<=26;y++) for(let dz=-2;dz<=2;dz++){ if(Math.abs(dz)<2) GW.set(tx-3,y,tz+dz,0xf7f3ea); }
  HB.line([tx,28,tz],[tx,34,tz],0x888070);
}
// boat shed
{
  const x0=30,x1=38,z0=-14,z1=-5;
  for(let x=x0;x<=x1;x++)for(let z=z0;z<=z1;z++){
    for(let y=8;y<11;y++){ if(x===x0||x===x1||z===z1) HB.set(x,y,z,vary(y%2?P.oakLite:P.oak,0.1)); else if(y===8) HB.set(x,y,z,vary(0x534635,0.1)); }
    const top=11+Math.round((x-x0)*0.55);
    for(let y=11;y<=top;y++) HB.set(x,y,z, y===top?vary(P.green,0.1):P.greenDk);
  }
  HB.box(36,11,-11,2,5,2,(x,y,z)=>vary(P.brick,0.1));
}
/* ---------- quay props ---------- */
function crate(b,x,z,s,c){
  for(let i=0;i<s;i++)for(let j=0;j<s;j++)for(let k=0;k<s;k++)
    b.set(x+i,8+j,z+k, (j===0||j===s-1)?vary(c,0.05):(((i+k)%2)?vary(c,0.10):vary(c,0.2)));
}
function barrel(b,x,z){ for(let y=0;y<4;y++) for(let dx=-1;dx<=1;dx++) for(let dz=-1;dz<=1;dz++)
  b.set(x+dx,8+y,z+dz, (y===0||y===3)?vary(P.barrelDk,0.08):vary(P.barrel,0.12)); }
function crateStack(b,x,z,n){ for(let i=0;i<n;i++) crate(b,x,z-1+((i%2)*3),2+((i%3)?1:0), [P.crate,P.crateL,0x7f6a44,0x8b6b3a][i%4]); }
function pile(b,x,z,n){ for(let i=0;i<n;i++) b.box(x+RI(-2,2),8+RI(0,2),z+RI(-2,2),1,1,1,vary(0xa89068,0.2)); }
[[-6,24],[3,20],[12,18],[-12,16],[28,10],[36,4],[22,-6],[13,-10]].forEach(([z,x])=>crateStack(HB,x,z,RI(2,4)));
[[20,-8],[23,12],[20,30],[24,-2]].forEach(([z,x])=>{barrel(HB,x,z);barrel(HB,x,z+2);});
HB.box(19,8,44,7,1,2,vary(P.oak,0.1)); HB.box(19,9,44,7,1,2,vary(P.oakLite,0.1)); HB.box(19,10,45,7,1,2,vary(P.oak,0.1));
pile(HB,22,-18,9); pile(HB,23,48,6);
// fish drying racks
for(let i=0;i<7;i++){
  HB.box(20,8,-20+i*2,1,3,1,vary(P.oakDark,0.1));
  for(let y=9;y<=10;y+=1) HB.box(20,y,-20+i*2,1,1,1,vary(0x7fa0ad,0.2));
}
// notice board
HB.box(24,8,13,2,4,1,vary(P.oakDark,0.1)); HB.box(24,10,12,2,2,1,vary(0xd8cbab,0.1));
// gantry crane
{
  HB.box(20,8,-3,1,7,1,vary(P.iron,0.08)); HB.box(25,8,-3,1,7,1,vary(P.iron,0.08));
  HB.box(20,8,-1,1,7,1,vary(P.iron,0.08)); HB.box(25,8,-1,1,7,1,vary(P.iron,0.08));
  HB.box(19,15,-3,8,1,3,vary(P.paint,0.08));
  HB.line([22,15,0],[22,19,-6],[x,y,z]=>vary(P.paint,0.1));
  HB.line([22,15,-2],[22,19,-6],[x,y,z]=>vary(P.paint,0.1));
}
/* ---------- trees, bushes ---------- */
function tree(b,x,z){
  const hh=RI(4,6); HB.line([x,8,z],[x,8+hh,z],P.oakDark);
  const r=RI(2,3);
  for(let dx=-r;dx<=r;dx++)for(let dy=-2;dy<=2;dy++)for(let dz=-r;dz<=r;dz++){
    const d=Math.abs(dx)+Math.abs(dy)*1.4+Math.abs(dz);
    if(d<=r+1) b.set(x+dx,8+hh+dy+1,z+dz, vary(dy>0?P.grass:P.fern,0.22));
  }
}
[[33,50],[40,-46],[46,-40],[60,44],[63,-14],[52,-52],[29,-62],[36,-56]].forEach(([x,z])=>tree(HB,x,z));
for(let i=0;i<40;i++){ const x=RI(30,64),z=RI(-68,68); if(groundH(x,z)<=9) continue; HB.box(x,groundH(x,z),z,1,1,1,vary(P.fern,0.3)); }

/* ---------- people (animated bob) ---------- */
const people=[];
function makePerson(x,z,coat,big){
  const b=new Builder(), g=new Builder();
  const h=big?5:4;
  b.set(x,8,z,vary(0x2c2f3a,0.1)); b.set(x,9,z,vary(0x3a3d48,0.1));
  b.set(x,10,z,vary(coat,0.12)); b.set(x,11,z,vary(0xc99a76,0.06));
  if(big){ b.box(x-1,12,z-1,3,1,3,vary(0x2c2f3a,0.1)); b.set(x,12,z,vary(0x2c2f3a,0.1)); }
  else b.set(x,12,z,vary(0x8a6b45,0.1));
  const m=b.mesh({cull:false,cast:true,recv:true});
  m.castShadow=true; m.frustumCulled=false;
  const gr=new THREE.Group(); gr.add(m); scene.add(gr);
  people.push({g:gr,ph:Math.random()*7,amp:0.06+Math.random()*0.05});
}
[[16,24,P.paint,true],[19,22,0x35456a],[20,40,0x556343],[23,32,0x7a4b31],[18,-8,0x4b4f5c],[21,-16,0x6d5a3a],[24,48,0x59375a]].forEach(a=>makePerson(a[0],a[1],a[2],a[3]));

/* ================= SHIP ================= */
const Y=[-5,-4,-3,-2,-1,0,1,2,3,4,5];
const YS=[0.13,0.28,0.55,0.79,0.93,1,1.02,1,0.98,0.97,0.98];
function beamRaw(z){
  const aft=0.05+0.95*sstep(-22,-15,z);
  const fwd=Math.pow(1-sstep(10,22,z),0.65);
  return 14.2*Math.min(aft,fwd);
}
function beam(z){ return z<=-16? beamRaw(-16): beamRaw(z); }
const ship=new THREE.Group(); scene.add(ship);
const shipGlowMat=new THREE.MeshBasicMaterial({color:0xffffff});
let rigMat;
(function buildShip(){
  const b=new Builder(), g=new Builder(), rig=[];
  const L=(a,c)=>rig.push(a,c);
  // hull
  for(let z=-22;z<=22;z++){
    const w=beam(z);
    for(let li=0;li<Y.length;li++){
      const y=Y[li], hw=Math.round(w*YS[li]);
      for(let x=-hw;x<=hw;x++){
        const side=Math.abs(x)===hw;
        let c;
        if(y<=-4)c=vary(P.bottom,0.10);
        else if(y<=-2)c=vary(P.copper,0.14);
        else if(y===-1)c=vary(P.boot,0.06);
        else if(y===0)c=vary(P.waterline,0.10);
        else if(y===1)c=vary(P.hullDk,0.06);
        else if(y===2)c=vary(P.hull,0.08);
        else if(y===3)c=vary(P.wale,0.05);
        else if(y===4)c=vary(P.hull,0.08);
        else if(y===5)c=vary(P.hullLt,0.07);
        else c=vary(P.deck,0.10);
        if(side&&y===5&&w>4&&(z%3===0)) c=vary(P.hullDk,0.05);
        b.set(x,y,z,c);
      }
    }
  }
  // deck
  for(let z=-22;z<=22;z++){ const hw=Math.round(beam(z));
    for(let x=-hw;x<=hw;x++) b.set(x,6,z,(Math.abs(x)%2)?vary(P.deck,0.08):vary(P.deckDk,0.08)); }
  // forecastle & quarterdeck
  for(let z=13;z<=22;z++){ const hw=Math.round(beam(z)); for(let x=-hw;x<=hw;x++) b.set(x,7,z,(Math.abs(x)%2)?vary(P.deck,0.08):vary(P.deckDk,0.08)); }
  for(let z=-22;z<=-9;z++){ const hw=Math.round(beam(z)); for(let x=-hw;x<=hw;x++) b.set(x,7,z,(Math.abs(x)%2)?vary(P.deck,0.08):vary(P.deckDk,0.08)); }
  b.box(-8,7,12,17,1,1,vary(P.oakDark,0.06));   // break of forecastle
  b.box(-8,7,-8,17,1,1,vary(P.oakDark,0.06));   // break of quarterdeck
  b.line([-2,7,12],[-2,6,10],P.oakDark); b.line([2,7,12],[2,6,10],P.oakDark);
  b.line([-2,7,-8],[-2,6,-6],P.oakDark); b.line([2,7,-8],[2,6,-6],P.oakDark);
  // bulwarks
  function bulwark(z0,z1,yTop){
    for(let z=z0;z<=z1;z++){
      const w=Math.round(beam(z)); if(w<2) continue;
      for(const s of [-1,1]) for(let y=yTop-1;y<=yTop;y++)
        b.set(s*w,y,z, vary(((z%3)===0)?P.bulwkDk:P.bulwkWhite,0.05));
    }
  }
  bulwark(13,22,8); bulwark(-22,-9,8); bulwark(-8,12,7);
  // stern: taffrail + nameboard + windows
  b.box(-6,8,-22,13,1,1,vary(P.gold,0.08));
  b.box(-3,9,-22,7,1,1,vary(P.oakDark,0.06));
  for(const x of [-8,-4,0,4,8]) for(let y=9;y<=10;y++){ b.del(x,y,-20); g.set(x,y,-20,vary(P.pane,0.1)); }
  b.box(-1,11,-22,3,1,1,vary(P.gold,0.05));
  for(const s of[-1,1]){ b.set(s*11,12,-21,vary(P.oakDark,0.06)); g.set(s*11,13,-21,P.lampGlow); }
  // masts / yards / sails
  function mast(z0,y0,y1){
    for(let y=y0;y<=y1;y++){ const t=(y-y0)/(y1-y0), s=Math.max(0,Math.round(1.4-t*1.35));
      b.box(-s,y,z0-s,2*s+1,1,2*s+1,[(x,yy,zz)=>vary(y>y0+3?P.sparDark:P.spar,0.07)][0]); }
  }
  function yard(z0,y,half){
    for(let x=-half;x<=half;x++){ const s=Math.max(0,Math.round(0.95-Math.abs(x)/half));
      b.box(x,y-s,z0-s,1,1+2*s,1+2*s,vary(P.sparDark,0.06)); }
  }
  function squareSail(z0,y0,y1,half,bulge){
    for(let x=-half;x<=half;x++){ const nx=Math.abs(x)/half, off=Math.round(bulge*(1-nx*nx));
      for(let y=y0;y<=y1;y++) b.set(x,y,z0+off, vary((Math.floor((y+x*0.6)/3)%2)?P.sailA:P.sailB,0.05)); }
  }
  function polyX(pts){
    let my0=1e9,my1=-1e9,mz0=1e9,mz1=-1e9;
    for(const p of pts){my0=Math.min(my0,p[1]);my1=Math.max(my1,p[1]);mz0=Math.min(mz0,p[2]);mz1=Math.max(mz1,p[2]);}
    for(let y=Math.round(my0);y<=Math.round(my1);y++)for(let z=Math.round(mz0);z<=Math.round(mz1);z++){
      let inside=true;
      for(let i=0;i<pts.length;i++){ const a=pts[i],c=pts[(i+1)%pts.length];
        if(((z-a[2])*(c[1]-a[1])-(y-a[1])*(c[2]-a[2]))<0){inside=false;break;} }
      if(inside) b.set(0,y,z, vary((y+z)%3?P.sailA:P.sailB,0.06));
    }
  }
  mast(0,7,33);   mast(11,7,30);  mast(-14,7,25);
  const mainY=[12,20,27],foreY=[12,19,26],mizY=[12,19];
  mainY.forEach(y=>yard(0,y,14)); foreY.forEach(y=>yard(11,y,12.5)); mizY.forEach(y=>yard(-14,y,10));
  yard(0,32,8); yard(11,29,7); yard(-14,24,6);
  squareSail(0,13,19,14,3); squareSail(0,21,26,11,2); squareSail(0,28,31,8,1);
  squareSail(11,13,18,12.5,3); squareSail(11,20,25,10,2); squareSail(11,27,29,7,1);
  squareSail(-14,13,18,10,2); squareSail(-14,20,24,8,1);
  polyX([[0,20,-15],[0,24,-14],[0,24,-20],[0,13,-17]]);
  polyX([[0,29,11],[0,7,13],[0,9,21],[0,15,18]]);
  polyX([[0,27,11],[0,7,-3],[0,7,8],[0,17,8]]);
  polyX([[0,31,-1],[0,9,14],[0,9,21],[0,22,15]]);
  // bowsprit & jibboom
  b.line([0,7,20],[0,13,29],(x,y,z)=>vary(P.spar,0.07));
  b.line([0,13,29],[0,15,34],(x,y,z)=>vary(P.spar,0.07));
  for(const s of [-1,1]) b.line([s*1.5,7,20],[s*1,12,28],P.sparDark);
  // deck furniture
  b.box(-7,7,-22,15,3,9,(x,y,z)=>((x===-7||x===7||z===-22||z===-13)?vary(P.plaster,0.06):0x534635));
  for(const x of[-4,0,4]){ b.del(x,9,-13); g.set(x,9,-13,vary(P.pane,0.1)); }
  b.box(-7,10,-22,15,1,9,vary(P.hullDk,0.06));
  b.box(4,11,-18,2,2,2,vary(P.iron,0.1));
  b.box(-6,7,-4,12,1,5,vary(P.hatch,0.08));
  b.box(-6,8,-4,12,1,5,(x,y,z)=>vary(P.hatch,0.12));
  b.box(-5,7,3,10,1,4,vary(P.hatch,0.08));
  b.box(6,7,-18,3,1,3,vary(P.oakDark,0.08)); b.set(7,8,-18,vary(P.oakLite,0.08)); b.line([7,8,-18],[10,8,-15],P.oakDark); b.line([7,8,-18],[4,8,-15],P.oakDark);
  b.box(-6,7,16,3,1,3,vary(P.oakDark,0.08)); b.set(-5,8,17,vary(P.oakLite,0.08));
  b.set(0,8,-18,vary(P.iron,0.05)); g.set(0,9,-18,0xffcf88); b.box(-1,8,-19,3,1,3,vary(P.oakDark,0.1));
  for(const s of[-1,1]){ b.box(s*9,10,-10,1,1,3,vary(P.oakDark,0.08)); b.box(s*9,9,-11,1,3,1,vary(P.oakDark,0.08)); }
  b.box(-13,9,-12,4,1,1,vary(P.oakLite,0.1)); b.box(9,9,-12,4,1,1,vary(P.oakLite,0.1));
  b.box(-12,8,20,2,1,1,vary(P.iron,0.1)); b.box(10,8,20,2,1,1,vary(P.iron,0.1));
  b.line([-11,8,20],[-11,5,22],P.iron); b.line([11,8,20],[11,5,22],P.iron);
  [[-9,14],[8,15],[-8,-4]].forEach(([x,z])=>{ barrel(b,x,z); });
  crate(b,-12,15,2,P.crate); crate(b,10,13,2,P.crateL);
  // rigging
  const heads=[[0,33,0],[11,30,11],[-14,25,-14],[0,15,34]];
  for(const [mx,my,mz] of heads){
    for(let i=-3;i<=3;i++){
      for(const s of[-1,1]){
        L([mx+s*1.5,my-Math.abs(i)*2.2,mz],[s*13.5,6.5,mz+i*3.4]);
        L([mx+s*1.5,my-Math.abs(i)*2.2-2,mz],[s*11,7,mz+i*2.6]);
      }
      L([mx,my-2,mz],[0,6.5,mz-13-i]);
    }
  }
  L([11,30,11],[0,15,34]); L([0,33,0],[11,30,11]); L([0,33,0],[-14,25,-14]);
  L([11,30,11],[0,7,22]); L([0,33,0],[0,7,13]); L([-14,25,-14],[-11,10,-21]); L([14,25,11],[10,7,20]);
  L([-14,25,-14],[14,25,11]);

  const hm=b.mesh({cull:true,cast:true,recv:true}); ship.add(hm);
  const gm=g.mesh({cull:false,cast:false,recv:false,mat:shipGlowMat,geo:new THREE.BoxGeometry(1,1,1)}); ship.add(gm);
  rigMat=new THREE.LineBasicMaterial({color:0xbfb098,transparent:true,opacity:0.45});
  const rg=new THREE.BufferGeometry();
  rg.setAttribute('position',new THREE.Float32BufferAttribute(rig.flat(),3));
  const rigLines=new THREE.LineSegments(rg,rigMat); rigLines.frustumCulled=false; ship.add(rigLines);
  window.__rig=rigLines;
  // flags
  window.__flags=[];
  const flagGeo=new THREE.BoxGeometry(1,1,1);
  function flag(x,y,z,cA,cB,dir){
    const grp=new THREE.Group(); grp.position.set(x,y,z);
    const mats=[new THREE.MeshLambertMaterial({color:cA}),new THREE.MeshLambertMaterial({color:cB})];
    const segs=[];
    for(let i=0;i<6;i++){ const m=new THREE.Mesh(flagGeo,mats[i%2]); m.scale.set(1.5,1,0.9); grp.add(m); segs.push(m); }
    grp.userData.segs=segs; ship.add(grp); window.__flags.push({g:grp,dir:dir||-1});
    return grp;
  }
  flag(0,32,0,0xb83c31,0xf2f0e8);
  flag(0,24,-15,0x2f4f7a,0xc8a24a);
  flag(0,15,34,0xf2f0e8,0x2f4f7a,-1);
})();

const BERTH=new THREE.Vector3(-1.5,0,4);
const curve=new THREE.CatmullRomCurve3([
  new THREE.Vector3(-175,-118),new THREE.Vector3(-128,-104),new THREE.Vector3(-92,-86),
  new THREE.Vector3(-70,-66),new THREE.Vector3(-64,-54),new THREE.Vector3(-56,-40),
  new THREE.Vector3(-44,-22),new THREE.Vector3(-28,-10),new THREE.Vector3(-12,-2),
  new THREE.Vector3(BERTH.x,BERTH.z),new THREE.Vector3(BERTH.x,BERTH.z+14)
].map(p=>new THREE.Vector3(p.x,0,p.z)));
let sEnd=1;
for(let s=1;s>0;s-=0.001){ if(curve.getPoint(s).z<=BERTH.z){ sEnd=s; break; } }

/* ================= animated props ================= */
// clouds
function makeCloud(){
  const b=new Builder();
  const n=RI(30,60), ox=RI(-60,60), oz=RI(-60,60), oy=RI(38,52), sx=0.6+Math.random()*0.8;
  const core=RI(3,5);
  for(let i=0;i<n;i++){
    const a=Math.random()*Math.PI*2, r=Math.pow(Math.random(),0.5)*core*2.2;
    const x=Math.round(Math.cos(a)*r*sx*2), y=Math.round((Math.random()-0.5)*2.2*sx), z=Math.round(Math.sin(a)*r*1.4);
    b.set(x,y,z, vary(y>0?0xfbfaf6:0xc8cfda,0.06));
  }
  const m=b.mesh({cull:false,cast:false,recv:false,mat:new THREE.MeshLambertMaterial()});
  m.position.set(ox,oy,oz); m.frustumCulled=false; scene.add(m);
  return {m,vx:R(0.4,1.1)};
}
const clouds=[]; for(let i=0;i<7;i++) clouds.push(makeCloud());
// gulls
const gullGeo=new THREE.BoxGeometry(1,1,1);
const gullW=new THREE.MeshLambertMaterial({color:0xf6f4ee}), gullD=new THREE.MeshLambertMaterial({color:0x9fa7b0});
const gulls=[];
for(let i=0;i<11;i++){
  const g=new THREE.Group();
  const body=new THREE.Mesh(gullGeo,gullW); body.scale.set(0.45,0.45,1.5); g.add(body);
  const back=new THREE.Mesh(gullGeo,gullD); back.scale.set(0.5,0.2,0.9); back.position.set(0,0.3,0.1); g.add(back);
  const head=new THREE.Mesh(gullGeo,gullW); head.scale.set(0.45,0.4,0.4); head.position.set(0,0.25,0.8); g.add(head);
  const pk=new THREE.Mesh(gullGeo,new THREE.MeshLambertMaterial({color:0xf0b23c})); pk.scale.set(0.2,0.2,0.3); pk.position.set(0,0.25,1.1); g.add(pk);
  const wl=new THREE.Group(), wr=new THREE.Group();
  const lm=new THREE.Mesh(gullGeo,gullW); lm.scale.set(1.5,0.12,0.5); lm.position.x=-0.85; wl.add(lm);
  const rm=new THREE.Mesh(gullGeo,gullW); rm.scale.set(1.5,0.12,0.5); rm.position.x=0.85; wr.add(rm);
  g.add(wl,wr); g.position.set(R(-70,50),R(18,30),R(-70,50)); scene.add(g);
  gulls.push({g,wl,wr,r:R(16,40),cy:R(-40,20),cx:R(-40,-5),h:R(16,30),w:R(0.25,0.6),ph:Math.random()*7,fl:R(8,14),sp:1});
}
// buoys
function makeBuoy(x,z,col,light,kind){
  const b=new Builder(), g=new Builder();
  if(kind==='can'){ b.box(-1,0,-1,3,3,3,vary(col,0.08)); b.set(0,0,0,vary(col,0.1)); b.line([0,3,z>0?0:0],[0,6,0],col); }
  else { b.box(-1,0,-1,2,2,2,vary(col,0.06)); b.box(-1,2,-1,2,2,2,vary(0xe9e4da,0.06)); b.line([0,4,0],[0,7,0],0x33363a); }
  g.set(0,kind==='can'?7:7,0,light);
  const grp=new THREE.Group(); grp.position.set(x,0,z);
  grp.add(b.mesh({cull:false,cast:true,recv:true}));
  const lm=new Builder(); lm.set(0,kind==='can'?7:7,0,light);
  const glowMesh=lm.mesh({cull:false,cast:false,recv:false,mat:new THREE.MeshBasicMaterial()});
  grp.add(glowMesh); scene.add(grp);
  return {g:grp,glow:glowMesh.material};
}
const buoys=[makeBuoy(-76,-26,0xc0392b,0xffd7a0,'can'), makeBuoy(-20,-52,0x2f3134,0x9dffb0,'pillar'), makeBuoy(-92,-64,0x2f3134,0xffd07a,'pillar')];
// rowboat
const rowboat=new THREE.Group();
{
  const b=new Builder();
  for(let z=-3;z<=3;z++){ const w=Math.max(1,Math.round(2.4*(1-Math.pow(Math.abs(z)/3.4,2))));
    for(let x=-w;x<=w;x++){ b.set(x,0,z,vary(P.oak,0.08)); if(Math.abs(x)===w) b.set(x,1,z,vary(P.oakLite,0.06)); } }
  b.box(-1,0,-1,2,1,2,0x00000000);
  b.box(-2,1,0,4,1,1,vary(P.deck,0.1));
  b.line([2,1,2],[-2,2,-2],P.sparDark); b.line([-2,1,-2],[2,2,2],P.sparDark);
  rowboat.add(b.mesh({cull:false,cast:true,recv:true}));
}
rowboat.position.set(10,0,22); scene.add(rowboat);
// crane load
const craneCrate=new THREE.Group();
{
  const b=new Builder();
  b.box(0,0,0,3,3,3,(x,y,z)=>(y===0||y===2)?vary(P.crateL,0.06):((x+z)%2?vary(P.crate,0.1):vary(P.crate,0.2)));
  craneCrate.add(b.mesh({cull:false,cast:true,recv:true}));
}
scene.add(craneCrate);
const cableMat=new THREE.LineBasicMaterial({color:0xbfb098,transparent:true,opacity:0.7});
const cables=new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(),new THREE.Vector3(),new THREE.Vector3(),new THREE.Vector3()]),cableMat);
cables.frustumCulled=false; scene.add(cables);
// clock hands
const clockGroup=new THREE.Group(); scene.add(clockGroup);
{
  const hm=new THREE.Mesh(new THREE.BoxGeometry(0.16,2.1,0.16),new THREE.MeshBasicMaterial({color:0x1c1f22}));
  const mm=new THREE.Mesh(new THREE.BoxGeometry(0.16,3.0,0.16),new THREE.MeshBasicMaterial({color:0x1c1f22}));
  const hg=new THREE.Group(); hg.add(hm); hm.position.y=1.05; hg.position.set(-4,0,-1.6);
  const mg=new THREE.Group(); mg.add(mm); mm.position.y=1.5; mg.position.set(-4,0,-1.6);
  clockGroup.position.set(54,25,32); clockGroup.add(hg,mg); clockGroup.userData={hg,mg};
}

/* ================= FX ================= */
const PUFF_N=360;
const puffMat=new THREE.MeshLambertMaterial({transparent:true,opacity:0.62,depthWrite:false});
const puffs=new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1),puffMat,PUFF_N);
puffs.frustumCulled=false; puffs.castShadow=false; scene.add(puffs);
const ps=[]; for(let i=0;i<PUFF_N;i++) ps.push({t:1,ttl:1,x:0,y:0,z:0,vx:0,vy:0,vz:0,s0:1,s1:1,grow:0,r:1,g:1,b:1});
let pIdx=0;
function puff(x,y,z,o){
  const p=ps[pIdx]; pIdx=(pIdx+1)%PUFF_N;
  p.t=0; p.ttl=o.ttl; p.x=x;p.y=y;p.z=z; p.vx=o.vx||0;p.vy=o.vy||0;p.vz=o.vz||0;
  p.s0=o.s0; p.s1=o.s1; p.grow=o.grow||0; p.r=o.r; p.g=o.g; p.b=o.b;
}
function smoke(x,y,z){ puff(x+R(-0.4,0.4),y,z+R(-0.4,0.4),{ttl:R(2.6,4.4),vy:R(0.6,1.1),vx:R(-0.3,0.1),s0:0.6,s1:3.2,grow:0.7,r:0.85,g:0.85,b:0.85}); }
function wake(x,y,z){ puff(x,y,z,{ttl:R(1.6,2.8),vy:R(-0.1,0.2),s0:0.5,s1:2.4,grow:0.55,r:0.92,g:0.97,b:0.96}); }
function updatePuffs(dt){
  const d=new THREE.Object3D(), col=new THREE.Color();
  for(let i=0;i<PUFF_N;i++){
    const p=ps[i];
    if(p.t>=p.ttl){ d.position.set(0,-999,0); d.scale.set(0.001,0.001,0.001); d.updateMatrix(); puffs.setMatrixAt(i,d.matrix); continue; }
    p.t+=dt; const u=Math.min(1,p.t/p.ttl);
    p.x+=p.vx*dt; p.y+=p.vy*dt; p.z+=p.vz*dt; p.vy*=0.985;
    const s=lerp(p.s0,p.s1,sstep(0,1,u))*(1-sstep(0.55,1,u));
    d.position.set(p.x,p.y,p.z); d.scale.set(s,s,s); d.updateMatrix();
    puffs.setMatrixAt(i,d.matrix);
    const dk=1-p.grow*u*0.7;
    col.setRGB(p.r*dk,p.g*dk,p.b*dk); puffs.setColorAt(i,col);
  }
  puffs.instanceMatrix.needsUpdate=true; if(puffs.instanceColor) puffs.instanceColor.needsUpdate=true;
}
// surf along walls
const surfList=[];
for(let z=Q0;z<=Q1;z+=2) surfList.push([15,-20+0,z]);
for(let z=Q0;z<=Q1;z+=2) surfList.push([16,-20+0,z]);
{ const a=[20,-24],b=[-44,-55],dc=[b[0]-a[0],b[1]-a[1]],len=Math.hypot(dc[0],dc[1]),n=[-dc[1]/len,dc[0]/len];
  for(let s=0;s<len;s+=2){ const px=a[0]+dc[0]*s/len,pz=a[1]+dc[1]*s/len;
    for(const w of[-3.6,3.6]) surfList.push([Math.round(px+n[0]*w),0,Math.round(pz+n[1]*w)]); } }
for(let z=-70;z<Q0;z+=2) surfList.push([26,0,z]);
for(let z=Q1;z<=70;z+=2) surfList.push([26,0,z]);
const surfMat=new THREE.MeshLambertMaterial({color:0xffffff,transparent:true,opacity:0.72,depthWrite:false});
const surf=new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1),surfMat,surfList.length);
surf.frustumCulled=false; surf.castShadow=false; surf.receiveShadow=false; scene.add(surf);
{ const col=new THREE.Color(); surfList.forEach((s,i)=>surf.setColorAt(i,col.setHex(P.foam))); if(surf.instanceColor) surf.instanceColor.needsUpdate=true; }

// mooring lines
const MOOR=[{b:26,l:[13,8,20]},{b:18,l:[13,8,8]},{b:8,l:[13,9,3]},{b:-2,l:[13,8,-6]},{b:-14,l:[13,8,-16]}];
const ropeMat=new THREE.LineBasicMaterial({color:0xa8936a,transparent:true,opacity:0.85});
const ropeGeo=new THREE.BufferGeometry();
const ropePos=new Float32Array(MOOR.length*10*6);
ropeGeo.setAttribute('position',new THREE.BufferAttribute(ropePos,3));
const ropes=new THREE.LineSegments(ropeGeo,ropeMat); ropes.frustumCulled=false; ropes.visible=false; scene.add(ropes);
// gangway
const gang=new THREE.Group(); scene.add(gang); gang.visible=false;
{
  const b=new Builder();
  for(let i=0;i<4;i++) b.line([17-i*1.2,10-i*0.35,4+i*1.2],[17-i*1.2,10-i*0.35,5.2+i*1.2],P.oakLite);
  b.line([17,12,3],[12.4,9,8],P.rope); b.line([17,12,6],[12.4,9,9],P.rope);
  b.box(16,8,3,1,2,1,P.oakDark);
  gang.add(b.mesh({cull:false,cast:true,recv:true}));
}

/* ================= day cycle ================= */
const DAY=[
 {f:0.00,top:0x03050a,hz:0x080d18,fog:0x090d18,sun:0x5a6a9a,si:0.05,hs:0x0d1424,hi:0.30,sea:0.45},
 {f:0.09,top:0x1b2441,hz:0x6a4459,fog:0x312d42,sun:0xff7a4a,si:0.42,hs:0x3a3a5f,hi:0.55,sea:0.6},
 {f:0.19,top:0x31609f,hz:0xdb9a5e,fog:0xa08d7e,sun:0xffb06a,si:1.55,hs:0x84a6ca,hi:0.85,sea:0.85},
 {f:0.34,top:0x2f7fd4,hz:0xa9c5d9,fog:0xa8bccc,sun:0xfff2d8,si:2.35,hs:0x92b7da,hi:1.00,sea:1.0},
 {f:0.50,top:0x1e6ec0,hz:0xbed7e7,fog:0xb6ccdd,sun:0xffffff,si:2.75,hs:0x9cc0e4,hi:1.08,sea:1.06},
 {f:0.66,top:0x3a7fb8,hz:0xe2c99a,fog:0xc4b7a5,sun:0xffe4b2,si:2.20,hs:0xabbacb,hi:0.95,sea:1.0},
 {f:0.80,top:0x2a4f80,hz:0xf28b3e,fog:0xd19a68,sun:0xff9a4a,si:1.35,hs:0x90828f,hi:0.72,sea:0.86},
 {f:0.90,top:0x122244,hz:0x8a3b46,fog:0x503b48,sun:0xc75a3a,si:0.32,hs:0x424c73,hi:0.48,sea:0.58},
 {f:1.00,top:0x03050a,hz:0x080d18,fog:0x090d18,sun:0x5a6a9a,si:0.05,hs:0x0d1424,hi:0.30,sea:0.45},
];
DAY.forEach(d=>{d._t=new THREE.Color(d.top);d._h=new THREE.Color(d.hz);d._f=new THREE.Color(d.fog);d._s=new THREE.Color(d.sun);d._hs=new THREE.Color(d.hs);});
const cA=new THREE.Color(),cB=new THREE.Color();
let dayLight=1, lampF=0;
function setDay(f){
  let i=0; while(i<DAY.length-2 && f>DAY[i+1].f) i++;
  const a=DAY[i],b=DAY[i+1],t=c01((f-a.f)/(b.f-a.f));
  skyU.top.value.copy(a._t).lerp(b._t,t);
  skyU.hor.value.copy(a._h).lerp(b._h,t);
  skyU.bot.value.copy(a._hz||a._h).lerp(b._h,t);
  scene.fog.color.copy(a._f).lerp(b._f,t);
  sunLight.color.copy(a._s).lerp(b._s,t);
  sunLight.intensity=lerp(a.si,b.si,t);
  hemi.color.copy(a._hs).lerp(b._hs,t);
  hemi.intensity=lerp(a.hi,b.hi,t);
  const seaT=lerp(a.sea,b.sea,t);
  // sun arc
  const tt=(f-0.08)/0.84;
  const pos=new THREE.Vector3(lerp(210,-210,tt), Math.sin(Math.PI*c01(tt))*190-6, lerp(-170,60,tt));
  const alt=pos.y/Math.max(1,pos.length());
  dayLight=c01(alt*1.8+0.03);
  sunLight.position.copy(pos);
  moonLight.position.copy(pos).multiplyScalar(-1);
  moonLight.intensity=0.42*(1-dayLight);
  sunDisc.position.copy(pos).multiplyScalar(2.1);
  sunDisc.material.color.copy(sunLight.color);
  sunDisc.material.opacity=c01(alt*6)*0.95;
  sunDisc.material.transparent=true;
  moonDisc.position.copy(pos).multiplyScalar(-2.1);
  moonDisc.material.opacity=c01(1-dayLight*2.5)*0.85;
  stars.material.opacity=c01(1-dayLight*3.2);
  lampF=1-sstep(0.02,0.30,alt);
  const fl=0.9+0.1*Math.sin(perfTime*7.3)+0.03*Math.random();
  glowMat.color.setScalar(lerp(0.14,1.25,lampF));
  shipGlowMat.color.setScalar(lerp(0.10,1.3,lampF));
  lampLights.forEach((l,k)=>l.intensity=lampF*38*(0.94+0.06*Math.sin(perfTime*6+k)));
  window.__beacon.beacon.intensity=lampF*900;
  window.__beacon.cone.material.opacity=lampF*0.16;
  horizon.material.color.setHex(P.seaDeep).multiplyScalar(seaT*0.85);
  seaBright=seaT;
  const names=[[0.02,'NIGHT'],[0.11,'Dawn'],[0.2,'Sunrise'],[0.3,'Early morning'],[0.42,'Morning'],[0.52,'Midday'],[0.64,'Afternoon'],[0.75,'Late afternoon'],[0.84,'Golden hour'],[0.92,'Sundown'],[1.01,'Night']];
  let nm='Night'; for(const [v,n] of names){ if(f<v){nm=n;break;} }
  document.getElementById('tl').textContent=nm.toUpperCase();
  seaTintR=seaT;
}
let seaBright=1,seaTintR=1;

/* ================= audio ================= */
let audio=null;
function initAudio(){
  const AC=window.AudioContext||window.webkitAudioContext; if(!AC) return null;
  const ctx=new AC();
  const make=(type,freq,Q)=>{ const o=ctx.createOscillator? null:null; };
  const buf=ctx.createBuffer(1,ctx.sampleRate*2,ctx.sampleRate);
  const ch=buf.getChannelData(0); let last=0;
  for(let i=0;i<ch.length;i++){ const w=Math.random()*2-1; last=(last+0.02*w)/1.02; ch[i]=last*3.2; }
  const src=ctx.createBufferSource(); src.buffer=buf; src.loop=true;
  const lp=ctx.createBiquadFilter(); lp.type='lowpass'; lp.frequency.value=520;
  const g=ctx.createGain(); g.gain.value=0.14;
  src.connect(lp); lp.connect(g); g.connect(ctx.destination);
  const lfo=ctx.createOscillator(); lfo.frequency.value=0.13;
  const lg=ctx.createGain(); lg.gain.value=0.05; lfo.connect(lg); lg.connect(g.gain);
  const bp=ctx.createBiquadFilter(); bp.type='bandpass'; bp.frequency.value=180; bp.Q.value=0.8;
  const wg=ctx.createGain(); wg.gain.value=0.06; src.connect(bp); bp.connect(wg); wg.connect(ctx.destination);
  src.start(); lfo.start();
  return {ctx,g};
}
function bellSound(){
  if(!audio) return; const c=audio.ctx, t=c.currentTime;
  [[660,0.35],[1188,0.2],[1650,0.1]].forEach(([f,a])=>{
    const o=c.createOscillator(),g=c.createGain(); o.type='triangle'; o.frequency.value=f;
    g.gain.setValueAtTime(a,t); g.gain.exponentialRampToValueAtTime(0.001,t+2.2);
    o.connect(g); g.connect(c.destination); o.start(t); o.stop(t+2.3);
  });
}
function boomSound(){
  if(!audio) return; const c=audio.ctx, t=c.currentTime;
  const b=c.createBuffer(1,c.sampleRate*0.6,c.sampleRate); const d=b.getChannelData(0);
  for(let i=0;i<d.length;i++){ d[i]=(Math.random()*2-1)*Math.pow(1-i/d.length,2.2); }
  const s=c.createBufferSource(); s.buffer=b;
  const lp=c.createBiquadFilter(); lp.type='lowpass'; lp.frequency.value=180;
  const g=c.createGain(); g.gain.value=0.75;
  s.connect(lp); lp.connect(g); g.connect(c.destination); s.start(t);
  const o=c.createOscillator(); o.frequency.setValueAtTime(90,t); o.frequency.exponentialRampToValueAtTime(35,t+0.5);
  const og=c.createGain(); og.gain.setValueAtTime(0.5,t); og.gain.exponentialRampToValueAtTime(0.001,t+0.6);
  o.connect(og); og.connect(c.destination); o.start(t); o.stop(t+0.7);
}

/* ================= UI ================= */
const log=document.getElementById('log'); const logLines=[];
function logAdd(s){
  logLines.forEach(l=>l.classList.remove('new'));
  const d=document.createElement('div'); d.className='new';
  d.innerHTML=`<span class="t">[${new Date().getHours().toString().padStart(2,'0')}:${new Date().getMinutes().toString().padStart(2,'0')}]</span> ${s}`;
  log.appendChild(d); logLines.push(d);
  while(logLines.length>4) logLines.shift().remove();
}
const readout=document.getElementById('readout');
function readoutHTML(){
  const o=[[6,0]];
  return [[0,0]];
}
function updateReadout(){
  const e=ship.rotation;
  const heelDeg=THREE.MathUtils.radToDeg(e.z);
  const rows=[
    ['STATUS',stateName],
    ['SPEED',knots.toFixed(1)+' kn'],
    ['HEEL',(Math.abs(heelDeg)<0.3?'—':(Math.abs(heelDeg).toFixed(1)+'° '+(heelDeg<0?'stbd':'port')))],
    ['SQUALL',calm(ship.position.x,ship.position.z)>0.5?'harbour calm':'open swell'],
  ];
  readout.innerHTML=rows.map(r=>`<b>${r[0]}</b><span>${r[1]}</span>`).join('');
}
let stateName='AT ANCHOR OFF THE BAR', knots=0;
const $=id=>document.getElementById(id);
let autoOrbit=true, pauseUntil=0;
$('bOrbit').onclick=()=>{ autoOrbit=!autoOrbit; $('bOrbit').classList.toggle('on',autoOrbit); };
$('bRig').onclick=()=>{ window.__rig.visible=!window.__rig.visible; $('bRig').classList.toggle('on',!window.__rig.visible); };
$('bRig').classList.add('on');
$('bRun').onclick=()=>{ startArrival(); };
$('bSail').onclick=()=>{ if(state==='moored'||state==='docked'){depart();} };
$('bBoom').onclick=()=>{ salute(); };
$('bAud').onclick=()=>{
  if(!audio){ audio=initAudio(); $('bAud').classList.add('on'); $('bAud').textContent='Ambience on'; logAdd('sea & wind ambience engaged'); }
  else { if(audio.ctx.state==='running') audio.ctx.suspend(); else audio.ctx.resume(); $('bAud').classList.toggle('on'); $('bAud').textContent='Ambience'; }
};
$('tod').oninput=e=>setDay(e.target.value/1000);
renderer.domElement.addEventListener('pointerdown',()=>{ pauseUntil=performance.now()+7000; });
setDay(0.615);

/* ================= ship states ================= */
let state='sailing', s=0, lastS=0, stateName='ENTERING THE CHANNEL', knots=0, prevPos=new THREE.Vector3(), moorT=0;
const tmp=new THREE.Vector3(), tmp2=new THREE.Vector3();
function startArrival(){
  state='sailing'; s=0; ship.visible=true; ropes.visible=false; gang.visible=false;
  logAdd('pilot taken aboard — she makes for the mouth');
}
function moor(){
  state='mooring'; moorT=0; stateName='WORKING HAWSEHOLDERS';
  ropes.visible=true; logAdd('“Bowline, then forward — stern off, then back!”');
}
function docked(){
  state='docked'; stateName='ALL FAST, SIDE TO THE QUAY';
  gang.visible=true; logAdd('“All fast and running out. She lies alongside.”');
  bellSound();
  for(let i=0;i<9;i++) setTimeout(()=>logAdd(i%2?'seagulls overhead, gulls overhead.':'a cart creaks on the cobbles'),i*1400);
}
function depart(){
  state='departing'; stateName='SHUTTING LINES, GETTING UNDER WAY';
  ropes.visible=false; gang.visible=false;
  logAdd('lines up and aboard — out she goes');
  setTimeout(()=>bellSound(),400);
}
function salute(){
  const bow=ship.localToWorld(new THREE.Vector3(0,7.5,20));
  flash=1; logAdd('a salute! — the echo rattles the jibboom');
  boomSound();
  for(let i=0;i<20;i++) puff(bow.x+R(-1,1),bow.y+R(-0.5,0.5),bow.z+R(-1,1),{ttl:R(1.4,3),vy:R(0.5,1.4),vx:R(-0.6,0.6),vz:R(-0.6,0.6),s0:0.7,s1:3.6,grow:0.9,r:1,g:1,b:1});
  gulls.forEach(g=>g.sp=3.2);
}
let flash=0;
const flashLight=new THREE.PointLight(0xffdca8,0,60,2); scene.add(flashLight);
startArrival();
setTimeout(()=>logAdd('the harbour bell at Caldbreck, half a mile off the bar'),900);

/* ================= loop ================= */
let perfTime=0, lastT=performance.now(), readoutTimer=0, gullTimer=0, smokeTimer=0;
const dummy=new THREE.Object3D(), sc=new THREE.Color();
function animate(){
  requestAnimationFrame(animate);
  const now=performance.now(); let dt=Math.min(0.05,(now-lastT)/1000); lastT=now; perfTime+=dt;
  const t=perfTime;

  /* --- day / beacon --- */
  window.__beacon.piv.rotation.y += dt*1.15;

  /* --- ship motion --- */
  if(state==='sailing'){
    const v=lerp(0.021,0.0035,sstep(0.55,0.95,s));
    s=Math.min(sEnd,s+v*dt);
    if(s>=sEnd) moor();
  } else if(state==='departing'){
    s=Math.max(0,s-lerp(0.012,0.02,sstep(0,0.2,1-s))*dt);
    if(s<=0.001){ state='away'; stateName='BEYOND THE BAR, UNDER FULL SAIL'; }
  } else if(state==='mooring'){
    moorT+=dt; if(moorT>7) docked();
  }
  const p=curve.getPoint(s), tan=curve.getTangent(s);
  let hx=Math.atan2(tan.x,tan.z);
  if(s>0.78) hx=lerp(hx,0,sstep(0.85,0.96,s));
  ship.position.set(p.x,0,p.z); ship.rotation.y=hx;
  prevPos.set(p.x,p.z,0);
  knots=Math.hypot(ship.position.x-tmp.x,ship.position.z-tmp.z)/Math.max(dt,1e-4)*1.25; tmp.copy(ship.position);

  // sea state under her
  const bx=ship.position.x, bz=ship.position.z;
  const wl=waveY(bx-6,bz+8,t), wr=waveY(bx+6,bz+8,t);
  const wf=waveY(bx,bz+18,t), wa=waveY(bx,bz-18,t);
  const roll=Math.atan2(wl-wr,12);
  const pitch=Math.atan2(wa-wf,36)*0.4;
  ship.position.y=-0.45+(wl+wr+wf+wa)/4;
  ship.rotation.x=pitch; ship.rotation.z=roll;
  if(state==='docked'||state==='mooring'){
    ship.rotation.z=roll+Math.sin(t*0.7)*0.005; ship.position.y=waveY(bx,bz,t)*0.7-0.45;
  }
  // wake & spray
  if(knots>2.2){
    const st=ship.localToWorld(new THREE.Vector3(0,0,-22));
    wake(st.x+R(-8,8),-0.55+waveY(st.x,st.z,t),st.z+R(-8,8));
    if(knots>4.5){ const bw=ship.localToWorld(new THREE.Vector3(0,4,24)); wake(bw.x+R(-4,4),0.1,bw.z+R(-4,4)); }
  }
  // galley smoke
  smokeTimer-=dt;
  if(smokeTimer<=0){ smokeTimer=0.42;
    const c=ship.localToWorld(new THREE.Vector3(4,12,-18)); smoke(c.x,c.y,c.z); }
  // harbour smoke
  if(Math.random()<0.02) smoke(37,16,-11);
  if(flash>0){ flash-=dt*5; flashLight.intensity=Math.max(0,flash)*420;
    flashLight.position.set(ship.localToWorld(new THREE.Vector3(0,7,20)).x,ship.localToWorld(new THREE.Vector3(0,7,20)).y,ship.localToWorld(new THREE.Vector3(0,7,20)).z); }

  // flags
  window.__flags.forEach((f,i)=>{
    f.g.userData.segs.forEach((m,j)=>{
      m.position.set(0,-0.22*j+0.22*Math.sin(t*5.5+i*2+j*0.9),f.dir*0.9*j);
      m.rotation.z=0.25*Math.sin(t*6+j*0.7+i);
    });
  });

  /* --- mooring lines --- */
  if(ropes.visible){
    let k=0;
    for(const m of MOOR){
      const a=tmp2.set(m.l[0],m.l[1],m.l[2]).applyMatrix4(ship.matrixWorld);
      const b0=new THREE.Vector3(16,10,m.b);
      for(let i=0;i<10;i++){
        const u=i/9, sag=-0.65*Math.sin(u*Math.PI);
        const ax=lerp(a.x,b0.x,u), ay=lerp(a.y,b0.y,u)+sag, az=lerp(a.z,b0.z,u);
        const u2=(i+1)/9, sag2=-0.65*Math.sin(u2*Math.PI);
        ropePos[k++]=ax; ropePos[k++]=ay; ropePos[k++]=az;
        ropePos[k++]=lerp(a.x,b0.x,u2); ropePos[k++]=lerp(a.y,b0.y,u2)+sag2; ropePos[k++]=lerp(a.z,b0.z,u2);
      }
    }
    ropeGeo.attributes.position.needsUpdate=true;
    if(state==='mooring' && moorT>2.5 && !gang.visible && moorT>4.5){ gang.visible=true; }
  }
  if(gang.visible) gang.scale.x=1;

  /* --- water --- */
  const ic=water.instanceColor.array;
  for(let i=0;i<cells.length;i++){
    const [x,z]=cells[i];
    const w=waveY(x,z,t), top=-0.55+w, h=Math.max(2.2,top+4.6);
    dummy.position.set(x,(top-4.6)/2,z); dummy.scale.set(1,h/3,1); dummy.updateMatrix();
    water.setMatrixAt(i,dummy.matrix);
    const crest=1+sstep(0.35,1.1,w)*0.55;
    ic[i*3]=bR[i]*seaTintR*crest; ic[i*3+1]=bG[i]*seaTintR*crest; ic[i*3+2]=bB[i]*seaTintR*crest;
  }
  water.instanceMatrix.needsUpdate=true; water.instanceColor.needsUpdate=true;

  /* --- surf --- */
  for(let i=0;i<surfList.length;i++){
    const s2=surfList[i], ph=s2[0]*0.7+s2[2]*0.5;
    const a=Math.abs(Math.sin(t*1.6+ph))*sstep(0.4,0.05,Math.abs(waveY(s2[0],s2[2],t)+0.4));
    const sc2=0.25+a*0.9;
    dummy.position.set(s2[0],-0.45+a*0.3,s2[2]); dummy.scale.set(1,sc2,1); dummy.updateMatrix();
    surf.setMatrixAt(i,dummy.matrix);
  }
  surf.instanceMatrix.needsUpdate=true;

  /* --- buoys, boat --- */
  buoys.forEach((bu,i)=>{
    const w=waveY(bu.g.position.x,bu.g.position.z,t);
    bu.g.position.y=w*0.9-0.35; bu.g.rotation.x=Math.sin(t*0.9+i)*0.09; bu.g.rotation.z=Math.cos(t*0.7+i*2)*0.09;
    const blink=(Math.sin(t*1.4+i*2)>0.9)?1:0.15;
    bu.glow.opacity=lampF*blink; bu.glow.transparent=true;
  });
  { const w=waveY(rowboat.position.x,rowboat.position.z,t);
    rowboat.position.y=w*0.85-0.5; rowboat.rotation.z=Math.sin(t*0.9)*0.05; rowboat.rotation.x=Math.cos(t*0.8)*0.04; }
  // crane load swing
  { const u=(Math.sin(t*0.35)*0.5+0.5);
    const hx2=lerp(22,14,u), hz2=lerp(-6,-2,u), hy=lerp(11,8,Math.sin(t*0.6)*0.5+0.5);
    craneCrate.position.set(hx2,hy,hz2); craneCrate.rotation.z=Math.sin(t*0.9)*0.03;
    const cp=cables.geometry.attributes.position;
    cp.setXYZ(0,22,19,-6); cp.setXYZ(1,hx2,hy+1.5,hz2-1.4);
    cp.setXYZ(2,22,19,-6); cp.setXYZ(3,hx2,hy+1.5,hz2+1.4);
    cp.needsUpdate=true;
  }
  // clouds
  clouds.forEach(c=>{ c.m.position.x+=c.vx*dt; if(c.m.position.x>170) c.m.position.x=-170; });
  // people
  people.forEach(p=>{ p.g.position.y=Math.sin(t*1.6+p.ph)*p.amp*0; p.g.rotation.y=Math.sin(t*0.3+p.ph)*0.02; });
  // gulls
  gulls.forEach(g=>{
    g.sp=Math.max(1,g.sp-dt*0.6);
    const a=g.ph+t*g.w*g.sp;
    g.g.position.set(g.cx+Math.cos(a)*g.r*(1+0.3*Math.sin(t*0.2+g.ph)), g.h+Math.sin(t*0.7+g.ph)*3+Math.sin(a*2)*1.2, g.cy+Math.sin(a)*g.r*0.8);
    g.g.rotation.y=-a+Math.PI/2;
    g.g.rotation.z=-Math.sin(a*0.5)*0.18;
    const fl=Math.sin(t*g.fl+g.ph); g.wl.rotation.z=fl*0.7; g.wr.rotation.z=-fl*0.7;
    if(g.g.position.z<-90||g.g.position.x<-120){ g.cx=RI(-50,10); g.cy=RI(-60,40); }
  });
  gullTimer-=dt;
  if(gullTimer<=0){ gullTimer=R(6,14); if(audio&&audio.ctx.state==='running'&&Math.random()<0.7){
    const c=audio.ctx,tt=c.currentTime,o=c.createOscillator(),gg=c.createGain();
    o.type='triangle'; o.frequency.setValueAtTime(1250,tt); o.frequency.linearRampToValueAtTime(820,tt+0.22);
    gg.gain.setValueAtTime(0.001,tt); gg.gain.linearRampToValueAtTime(0.035,tt+0.05); gg.gain.exponentialRampToValueAtTime(0.001,tt+0.3);
    o.connect(gg); gg.connect(c.destination); o.start(tt); o.stop(tt+0.35);
  }}
  // harbour clock
  { const hrs=5.5+16*($('tod').value/1000);
    const h=clockGroup.userData; h.hg.rotation.z=-((hrs%12)/12)*Math.PI*2; h.mg.rotation.z=-((hrs*60%360)/360)*Math.PI*2; }

  updatePuffs(dt);

  /* --- readout --- */
  readoutTimer-=dt;
  if(readoutTimer<=0){
    readoutTimer=0.25;
    if(state==='sailing') stateName = s<0.16?'BEYOND THE BAR':s<0.4?'OFF THE LIGHTHOUSE':'ENTERING THE CHANNEL';
    if(state==='departing') stateName='GETTING UNDER WAY';
    if(state==='away') stateName='BEYOND THE BAR, FULL AND BY';
    updateReadout();
  }

  controls.autoRotate=autoOrbit && now>pauseUntil;
  controls.update();
  renderer.render(scene,camera);
}
addEventListener('resize',()=>{
  camera.aspect=innerWidth/innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight);
});
renderer.render(scene,camera);
requestAnimationFrame(animate);
document.getElementById('load').style.opacity='0';
setTimeout(()=>document.getElementById('load').remove(),900);
</script>
</body>
</html>
```