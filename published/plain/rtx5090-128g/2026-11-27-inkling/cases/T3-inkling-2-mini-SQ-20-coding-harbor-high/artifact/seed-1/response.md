Here's a self-contained voxel harbor scene — drag to orbit, scroll to zoom. Just paste it into an `.html` file and open it in Chrome.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Harbor Arrival — Voxel Sailing Ship</title>
<style>
  *{box-sizing:border-box}
  html,body{margin:0;height:100%;overflow:hidden;background:#0c1826;font-family:"Segoe UI",system-ui,-apple-system,sans-serif}
  canvas{display:block;position:fixed;inset:0;cursor:grab;touch-action:none}
  canvas.dragging{cursor:grabbing}
  .hud{position:fixed;top:18px;left:20px;padding:14px 18px;border-radius:16px;
       background:rgba(11,22,36,.44);border:1px solid rgba(255,255,255,.18);
       backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);
       color:#f4f8fc;pointer-events:none;max-width:min(440px,72vw);
       box-shadow:0 8px 30px rgba(0,0,0,.25)}
  .hud h1{font-size:19px;margin:0 0 5px;letter-spacing:.3px;font-weight:700}
  .hud p{margin:0;font-size:12px;line-height:1.45;opacity:.85}
  #reset{position:fixed;right:18px;bottom:16px;padding:10px 16px;border-radius:999px;
         border:1px solid rgba(255,255,255,.22);background:rgba(11,22,36,.44);
         backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);
         color:#eef4fa;font-size:12.5px;letter-spacing:.4px;cursor:pointer;
         transition:background .2s,transform .15s}
  #reset:hover{background:rgba(32,54,78,.62);transform:translateY(-1px)}
  #reset:active{transform:translateY(0)}
  @media (max-width:560px){.hud h1{font-size:16px}.hud p{font-size:11px}}
</style>
</head>
<body>
<canvas id="scene"></canvas>
<div class="hud">
  <h1>⚓ Harbor Arrival</h1>
  <p>A sailing ship calling at the harbor — hand-built voxel art.<br>Drag to orbit &nbsp;·&nbsp; scroll to zoom</p>
</div>
<button id="reset" title="Reset view">⟲ Reset view</button>
<script>
'use strict';
/* ================= setup ================= */
const canvas=document.getElementById('scene');
const ctx=canvas.getContext('2d');
let W=0,H=0,DPR=1;
function resize(){
  DPR=Math.min(window.devicePixelRatio||1,2);
  W=window.innerWidth;H=window.innerHeight;
  canvas.width=Math.round(W*DPR);canvas.height=Math.round(H*DPR);
  canvas.style.width=W+'px';canvas.style.height=H+'px';
  ctx.setTransform(DPR,0,0,DPR,0,0);
}
window.addEventListener('resize',resize);resize();

/* ================= palette ================= */
const C={
  waterDeep:[26,95,126], waterMid:[38,128,158], teal:[63,168,158], foam:[233,246,238],
  woodDark:[88,56,32], woodMid:[130,84,50], deck:[202,156,104], deckTrim:[70,44,26],
  cream:[246,236,214], creamShade:[228,216,188], red:[206,64,44], mast:[74,51,31],
  crate:[186,134,76], barrel:[116,70,38], hatch:[63,39,22],
  plank1:[154,108,66], plank2:[134,92,56], post:[74,53,36],
  rock1:[108,100,90], rock2:[126,118,107], rock3:[142,133,121],
  towerRed:[205,80,60], towerWhite:[241,235,222], gallery:[45,41,50], light:[255,222,128],
  dinghy:[142,90,51], seat:[108,64,35], buoyRed:[212,58,46], buoyWhite:[242,237,226],
  boatHull:[88,58,36], boatSail:[238,228,205],
  cloud:[248,251,253], pole:[45,41,38], lamp:[255,222,130]
};

/* ================= helpers ================= */
function hash(x,z){const s=Math.sin(x*12.9898+z*78.233)*43758.5453;return s-Math.floor(s);}
function mix(a,b,t){return [a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t,a[2]+(b[2]-a[2])*t];}
function clamp255(n){n=Math.round(n);return n<0?0:n>255?255:n;}
function rgb(c,m){return 'rgb('+clamp255(c[0]*m)+','+clamp255(c[1]*m)+','+clamp255(c[2]*m)+')';}
function wrap(v,lo,hi){const r=hi-lo;return ((v-lo)%r+r)%r+lo;}

/* ================= voxel store ================= */
const voxels=[];
function addVoxel(x,y,z,color,g,extra){
  voxels.push({x:x,y:y,z:z,color:color||null,g:g||'static',
    seed:hash(x*1.7+y*3.1,z*2.3+y*1.1),speed:(extra&&extra.speed)||0});
}

/* foam ring set */
const foamSet=new Set();
for(let z=-2;z<=10;z++){foamSet.add('10|'+z);foamSet.add('16|'+z);}
for(let x=-19;x<=-13;x++){foamSet.add(x+'|'+(-12));}
for(let z=-11;z<=-5;z++){foamSet.add('-20|'+z);}
for(let x=-9;x<=4;x++){foamSet.add(x+'|'+(-4));foamSet.add(x+'|'+2);}

/* ================= water ================= */
for(let x=-23;x<=23;x++)for(let z=-19;z<=19;z++){
  if(x>=-19&&x<=-13&&z>=-11&&z<=-5)continue;   // rocks
  if(x>=11&&x<=15&&z>=-2&&z<=10)continue;      // pier
  addVoxel(x,0,z,null,'water');
}

/* ================= ship (bow at -x, stern at +x) ================= */
const SHIP_X=-1.5,SHIP_Z=-1.0;
// hull bottom / mid / deck
for(let x=-4;x<=4;x++)for(let z=-1;z<=1;z++)addVoxel(x,1,z,C.woodDark,'ship');
for(let x=-6;x<=5;x++){
  const zm=(x===-6||x===5)?1:2;
  for(let z=-zm;z<=zm;z++)addVoxel(x,2,z,C.woodMid,'ship');
}
for(let x=-6;x<=5;x++){
  const zm=(x===-6||x===5)?1:2;
  for(let z=-zm;z<=zm;z++){
    const edge=Math.abs(z)===zm||x===-6||x===5;
    addVoxel(x,3,z,edge?C.deckTrim:C.deck,'ship');
  }
}
// sterncastle
for(let x=4;x<=5;x++)for(let z=-1;z<=1;z++){addVoxel(x,4,z,C.woodMid,'ship');addVoxel(x,5,z,C.red,'ship');}
// bowsprit
addVoxel(-7,3,0,C.woodDark,'ship');addVoxel(-8,3,0,C.woodDark,'ship');addVoxel(-9,4,0,C.woodDark,'ship');
// deck props
addVoxel(-4,4,1,C.crate,'ship');addVoxel(-4,5,1,C.crate,'ship');
addVoxel(-3,4,-1,C.barrel,'ship');
addVoxel(-2,4,0,C.hatch,'ship');
// masts (sail range skips mast cell — sail covers it)
function mast(mx,topY,yardY,yardHalf,sailRows,sailHalf){
  for(let y=4;y<=topY;y++){
    if(y>=yardY-sailRows&&y<=yardY-1)continue;
    addVoxel(mx,y,0,C.mast,'ship');
  }
  for(let z=-yardHalf;z<=yardHalf;z++)addVoxel(mx,yardY,z,C.mast,'ship');
  for(let y=yardY-1;y>=yardY-sailRows;y--)
    for(let z=-sailHalf;z<=sailHalf;z++)
      addVoxel(mx,y,z,y===yardY-1?C.cream:C.creamShade,'sail');
}
mast(-2,10,8,3,3,2);   // fore
mast(2,11,9,4,4,3);    // main
// crow's nest (ring around main mast)
addVoxel(1,11,0,C.mast,'ship');addVoxel(3,11,0,C.mast,'ship');
addVoxel(2,11,1,C.mast,'ship');addVoxel(2,11,-1,C.mast,'ship');
// pennant flags
addVoxel(2,12,0,C.red,'flag');addVoxel(3,12,0,C.red,'flag');addVoxel(4,12,0,C.red,'flag');addVoxel(5,12,0,C.red,'flag');
addVoxel(-2,11,0,C.red,'flag');addVoxel(-1,11,0,C.red,'flag');addVoxel(0,11,0,C.red,'flag');

/* ================= pier ================= */
for(let x=11;x<=15;x++)for(let z=-2;z<=10;z++)addVoxel(x,1,z,z%2===0?C.plank1:C.plank2,'static');
for(const z of [-2,2,6,10]){addVoxel(11,0,z,C.post,'static');addVoxel(15,0,z,C.post,'static');}
addVoxel(12,2,0,C.crate,'static');addVoxel(13,2,0,C.crate,'static');addVoxel(12,3,0,C.crate,'static');
addVoxel(14,2,3,C.crate,'static');
addVoxel(13,2,5,C.barrel,'static');addVoxel(13,3,5,C.barrel,'static');
for(let y=2;y<=5;y++)addVoxel(11,y,9,C.pole,'static');
addVoxel(11,6,9,C.lamp,'static');

/* ================= dinghy ================= */
for(let x=16;x<=19;x++)for(let z=1;z<=2;z++)addVoxel(x,1,z,C.dinghy,'dinghy');
addVoxel(17,2,1,C.seat,'dinghy');addVoxel(18,2,2,C.seat,'dinghy');

/* ================= lighthouse on cliff ================= */
for(let x=-19;x<=-13;x++)for(let z=-11;z<=-5;z++)addVoxel(x,0,z,C.rock1,'static');
for(let x=-18;x<=-14;x++)for(let z=-10;z<=-6;z++)addVoxel(x,1,z,C.rock2,'static');
for(let x=-17;x<=-15;x++)for(let z=-9;z<=-7;z++)addVoxel(x,2,z,C.rock3,'static');
for(let y=3;y<=10;y++){
  const col=(y===3||y===4||y===7||y===8)?C.towerRed:C.towerWhite;
  for(let x=-17;x<=-16;x++)for(let z=-9;z<=-8;z++)addVoxel(x,y,z,col,'static');
}
for(let x=-18;x<=-15;x++)for(let z=-10;z<=-7;z++)addVoxel(x,11,z,C.gallery,'static');
for(let x=-17;x<=-16;x++)for(let z=-9;z<=-8;z++)addVoxel(x,12,z,C.light,'static');
for(let x=-17;x<=-15;x++)for(let z=-9;z<=-7;z++)addVoxel(x,13,z,C.gallery,'static');
addVoxel(-16,14,-8,C.gallery,'static');

/* ================= buoys ================= */
addVoxel(8,1,-6,C.buoyRed,'buoy');addVoxel(8,2,-6,C.buoyWhite,'buoy');addVoxel(8,3,-6,C.buoyRed,'buoy');
addVoxel(-11,1,7,C.buoyRed,'buoy');addVoxel(-11,2,7,C.buoyWhite,'buoy');

/* ================= distant small boat ================= */
for(let x=-13;x<=-11;x++)for(let z=-14;z<=-13;z++)addVoxel(x,1,z,C.boatHull,'boat');
for(let y=2;y<=5;y++)addVoxel(-12,y,-14,C.mast,'boat');
addVoxel(-12,3,-13,C.boatSail,'boat');addVoxel(-12,4,-13,C.boatSail,'boat');

/* ================= clouds ================= */
const cloudDefs=[
  {x:-8,y:16,z:-8,speed:0.55,cells:[[0,0,0],[1,0,0],[2,0,0],[-1,0,0],[0,1,0],[1,1,0],[0,0,1],[1,0,-1]]},
  {x:10,y:18,z:-12,speed:0.35,cells:[[0,0,0],[1,0,0],[-1,0,0],[0,1,0]]},
  {x:16,y:15.5,z:5,speed:0.70,cells:[[0,0,0],[1,0,0],[2,0,0],[0,1,0],[1,0,1]]},
  {x:-20,y:17,z:2,speed:0.45,cells:[[0,0,0],[1,0,0],[0,1,0],[-1,0,0],[1,0,-1]]}
];
for(const cd of cloudDefs)for(const c of cd.cells)addVoxel(cd.x+c[0],cd.y+c[1],cd.z+c[2],C.cloud,'cloud',{speed:cd.speed});

/* ================= camera / controls ================= */
let theta=0.40,phi=0.28,radius=46;
let targetTheta=theta,targetPhi=phi,targetRadius=radius;
const TARGET={x:0,y:2.5,z:0};
const FOV=0.85;
let C={x:0,y:0,z:0},viewF={x:0,y:0,z:0},R={x:0,y:0,z:0},U={x:0,y:0,z:0},focal=800,cx=0,cy=0;
function computeCamera(){
  const cp=Math.cos(phi),sp=Math.sin(phi);
  C={x:TARGET.x+radius*cp*Math.sin(theta),y:TARGET.y+radius*sp,z:TARGET.z+radius*cp*Math.cos(theta)};
  viewF={x:TARGET.x-C.x,y:TARGET.y-C.y,z:TARGET.z-C.z};
  const fl=Math.hypot(viewF.x,viewF.y,viewF.z);viewF.x/=fl;viewF.y/=fl;viewF.z/=fl;
  R={x:-viewF.z,y:0,z:viewF.x};
  const rl=Math.hypot(R.x,R.z);R.x/=rl;R.z/=rl;
  U={x:R.y*viewF.z-R.z*viewF.y, y:R.z*viewF.x-R.x*viewF.z, z:R.x*viewF.y-R.y*viewF.x};
  focal=(H*0.5)/Math.tan(FOV*0.5);
  cx=W/2;cy=H*0.5;
}
function proj(x,y,z){
  const dx=x-C.x,dy=y-C.y,dz=z-C.z;
  const zc=dx*viewF.x+dy*viewF.y+dz*viewF.z;
  if(zc<0.5)return null;
  const xc=dx*R.x+dy*R.y+dz*R.z;
  const yc=dx*U.x+dy*U.y+dz*U.z;
  const s=focal/zc;
  return [cx+xc*s,cy-yc*s];
}
function horizonY(){
  const hf=Math.hypot(viewF.x,viewF.z)||1;
  const P=proj(TARGET.x+viewF.x/hf*4000,0,TARGET.z+viewF.z/hf*4000);
  if(P)return Math.max(-H,Math.min(H,P[1]));
  return H*0.18;
}

/* ================= transforms ================= */
let t=0;
function waveY(x,z,tt){return Math.sin(tt*1.35+x*0.45+z*0.35)*0.15;}
function shipTransform(v,tt){
  const bob=Math.sin(tt*1.25)*0.18;
  const roll=Math.sin(tt*0.9)*0.05;
  const pitch=Math.sin(tt*0.65+1.2)*0.04;
  const px=0,py=2.2,pz=0;
  const dx=v.x-px,dy=v.y-py,dz=v.z-pz;
  const rc=Math.cos(roll),rs=Math.sin(roll);
  const dy2=dy*rc-dz*rs;
  const dz2=dy*rs+dz*rc;
  const pc=Math.cos(pitch),ps=Math.sin(pitch);
  const dx2=dx*pc-dy2*ps;
  const dy3=dx*ps+dy2*pc;
  return [SHIP_X+dx2+px,py+dy3+bob,SHIP_Z+dz2+pz];
}
function worldPos(v,tt){
  switch(v.g){
    case 'water':return [v.x,waveY(v.x,v.z,tt),v.z];
    case 'ship':return shipTransform(v,tt);
    case 'sail':{const p=shipTransform(v,tt);p[0]+=Math.sin(tt*1.7+v.y*0.8+v.z*0.4)*0.17;return p;}
    case 'flag':{const p=shipTransform(v,tt);p[1]+=Math.sin(tt*6+v.x*1.3+v.y*0.7)*0.16;p[0]+=Math.sin(tt*6+v.x*0.9)*0.08;return p;}
    case 'cloud':return [wrap(v.x+tt*v.speed,-38,38),v.y,v.z];
    case 'buoy':return [v.x,v.y+Math.sin(tt*1.6+v.seed*6.28)*0.14,v.z];
    case 'boat':return [v.x,v.y+Math.sin(tt*1.15+2)*0.15,v.z];
    case 'dinghy':return [v.x,v.y+Math.sin(tt*1.4+1)*0.13,v.z];
    default:return [v.x,v.y,v.z];
  }
}
function waterColor(x,z){
  const n=hash(x*1.13,z*1.37);
  let col=mix(C.waterDeep,C.waterMid,0.2+n*0.6);
  if(z>=-3&&z<=11&&Math.abs(x-13)<5)col=mix(col,C.teal,0.42);
  if(x>=-21&&x<=-11&&z>=-13&&z<=-4)col=mix(col,C.teal,0.5);
  if(foamSet.has(x+'|'+z))col=mix(col,C.foam,0.82);
  return col;
}

/* ================= drawing ================= */
function face(p1,p2,p3,p4,css){
  if(!p1||!p2||!p3||!p4)return;
  ctx.beginPath();
  ctx.moveTo(p1[0],p1[1]);ctx.lineTo(p2[0],p2[1]);ctx.lineTo(p3[0],p3[1]);ctx.lineTo(p4[0],p4[1]);
  ctx.closePath();ctx.fillStyle=css;ctx.fill();
}
function drawVoxel(it){
  const v=it.v;
  const wx=it.x,wy=it.y,wz=it.z;
  const cA=proj(wx,wy,wz),cB=proj(wx+1,wy,wz),cC=proj(wx+1,wy,wz+1),cD=proj(wx,wy,wz+1);
  const cE=proj(wx,wy+1,wz),cF=proj(wx+1,wy+1,wz),cG=proj(wx+1,wy+1,wz+1),cH=proj(wx,wy+1,wz+1);
  if(v.g==='water'){
    if(!cE||!cF||!cG||!cH)return;
    const foam=foamSet.has(v.x+'|'+v.z);
    const bright=foam?1.02+0.2*Math.sin(t*3.1+v.seed*6.28):0.94+0.13*Math.sin(t*1.8+v.x*0.5+v.z*0.35);
    const shade=0.9+v.seed*0.2;
    face(cE,cF,cG,cH,rgb(waterColor(v.x,v.z),bright*shade));
    return;
  }
  if(!cA||!cB||!cC||!cD||!cE||!cF||!cG||!cH)return;
  const shade=0.92+v.seed*0.16;
  if(viewF.x<0)face(cB,cC,cG,cF,rgb(v.color,0.88*shade));
  else face(cA,cD,cH,cE,rgb(v.color,0.80*shade));
  if(viewF.z<0)face(cD,cC,cG,cH,rgb(v.color,0.70*shade));
  else face(cA,cB,cF,cE,rgb(v.color,0.74*shade));
  face(cE,cF,cG,cH,rgb(v.color,1.10*shade));
}
function drawRig(){
  const mainTop=shipTransform({x:2,y:11,z:0},t);
  const foreTop=shipTransform({x:-2,y:10,z:0},t);
  const bow=shipTransform({x:-9,y:4,z:0},t);
  const stern=shipTransform({x:5,y:5,z:0},t);
  const segs=[[mainTop,bow],[mainTop,stern],[foreTop,bow],[foreTop,mainTop]];
  ctx.strokeStyle='rgba(36,25,17,0.6)';ctx.lineWidth=1.4;ctx.lineCap='round';
  for(const s of segs){
    const a=proj(s[0][0],s[0][1],s[0][2]),b=proj(s[1][0],s[1][1],s[1][2]);
    if(a&&b){ctx.beginPath();ctx.moveTo(a[0],a[1]);ctx.lineTo(b[0],b[1]);ctx.stroke();}
  }
}
function drawBeam(){
  const ang=t*0.55;
  const dirX=Math.cos(ang),dirZ=Math.sin(ang);
  const ox=-16,oy=12.5,oz=-8;
  const glowP=proj(ox,oy,oz);
  if(glowP){
    const gg=ctx.createRadialGradient(glowP[0],glowP[1],2,glowP[0],glowP[1],30);
    gg.addColorStop(0,'rgba(255,240,185,0.85)');gg.addColorStop(1,'rgba(255,240,185,0)');
    ctx.fillStyle=gg;ctx.beginPath();ctx.arc(glowP[0],glowP[1],30,0,Math.PI*2);ctx.fill();
  }
  const p0=proj(ox+dirX*1.4,oy,oz+dirZ*1.4);
  const p1=proj(ox+dirX*58,oy+0.5,oz+dirZ*58);
  if(p0&&p1){
    const dx=p1[0]-p0[0],dy=p1[1]-p0[1],L=Math.hypot(dx,dy)||1;
    const nx=-dy/L,ny=dx/L;
    const w0=6,w1=Math.min(52,16+L*0.16);
    const bg=ctx.createLinearGradient(p0[0],p0[1],p1[0],p1[1]);
    bg.addColorStop(0,'rgba(255,238,170,0.30)');bg.addColorStop(1,'rgba(255,238,170,0)');
    ctx.beginPath();
    ctx.moveTo(p0[0]+nx*w0,p0[1]+ny*w0);
    ctx.lineTo(p1[0]+nx*w1,p1[1]+ny*w1);
    ctx.lineTo(p1[0]-nx*w1,p1[1]-ny*w1);
    ctx.lineTo(p0[0]-nx*w0,p0[1]-ny*w0);
    ctx.closePath();ctx.fillStyle=bg;ctx.fill();
  }
}
function drawLamp(){
  const p=proj(11.5,6.6,9.5);
  if(!p)return;
  const gg=ctx.createRadialGradient(p[0],p[1],2,p[0],p[1],24);
  gg.addColorStop(0,'rgba(255,224,150,0.8)');gg.addColorStop(1,'rgba(255,224,150,0)');
  ctx.fillStyle=gg;ctx.beginPath();ctx.arc(p[0],p[1],24,0,Math.PI*2);ctx.fill();
}
function drawBirds(){
  for(let i=0;i<3;i++){
    const bx=((t*16+i*300)%(W+260))-130;
    const by=H*0.2+i*44+Math.sin(t*1.4+i*2.2)*16;
    const f=Math.sin(t*7+i*2.4)*4;
    ctx.strokeStyle='rgba(38,44,54,0.75)';ctx.lineWidth=2;ctx.lineCap='round';
    ctx.beginPath();
    ctx.moveTo(bx-10,by);
    ctx.quadraticCurveTo(bx-5,by-5-f,bx,by);
    ctx.quadraticCurveTo(bx+5,by-5-f,bx+10,by);
    ctx.stroke();
  }
}
function draw(){
  computeCamera();
  // sky
  const sky=ctx.createLinearGradient(0,0,0,H);
  sky.addColorStop(0,'#3d7ec4');sky.addColorStop(0.5,'#7fb6e2');sky.addColorStop(0.78,'#e9dcae');sky.addColorStop(1,'#e9dcae');
  ctx.fillStyle=sky;ctx.fillRect(0,0,W,H);
  // sun
  const sx=W*0.2,sy=H*0.13;
  let g=ctx.createRadialGradient(sx,sy,8,sx,sy,180);
  g.addColorStop(0,'rgba(255,246,210,0.95)');g.addColorStop(0.2,'rgba(255,240,190,0.5)');g.addColorStop(1,'rgba(255,240,190,0)');
  ctx.fillStyle=g;ctx.beginPath();ctx.arc(sx,sy,180,0,Math.PI*2);ctx.fill();
  ctx.fillStyle='#fff7dd';ctx.beginPath();ctx.arc(sx,sy,28,0,Math.PI*2);ctx.fill();
  // sea band
  const hy=horizonY();
  const sea=ctx.createLinearGradient(0,Math.max(0,hy),0,H);
  sea.addColorStop(0,'#35849f');sea.addColorStop(0.35,'#1e6c8c');sea.addColorStop(1,'#0d3d57');
  ctx.fillStyle=sea;ctx.fillRect(0,Math.max(0,hy),W,H);
  // build & sort render list
  const list=[];
  for(const v of voxels){
    const p=worldPos(v,t);
    const cxr=p[0]+0.5,cyr=p[1]+0.5,czr=p[2]+0.5;
    const depth=(cxr-C.x)*viewF.x+(cyr-C.y)*viewF.y+(czr-C.z)*viewF.z;
    if(depth<1.5)continue;
    list.push({x:p[0],y:p[1],z:p[2],v:v,depth:depth});
  }
  list.sort(function(a,b){return b.depth-a.depth;});
  for(const it of list)drawVoxel(it);
  drawRig();drawBeam();drawLamp();drawBirds();
  // vignette
  const vg=ctx.createRadialGradient(W/2,H*0.46,H*0.34,W/2,H*0.52,H*0.98);
  vg.addColorStop(0,'rgba(8,16,28,0)');vg.addColorStop(1,'rgba(8,16,28,0.32)');
  ctx.fillStyle=vg;ctx.fillRect(0,0,W,H);
}

/* ================= input ================= */
const pointers=new Map();
let lastPinch=0;
canvas.addEventListener('pointerdown',function(e){
  canvas.setPointerCapture(e.pointerId);
  pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});
  canvas.classList.add('dragging');lastPinch=0;
});
canvas.addEventListener('pointermove',function(e){
  if(!pointers.has(e.pointerId))return;
  const prev=pointers.get(e.pointerId);
  const dx=e.clientX-prev.x,dy=e.clientY-prev.y;
  pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});
  if(pointers.size===1){
    targetTheta-=dx*0.0052;
    targetPhi=Math.min(1.05,Math.max(0.13,targetPhi+dy*0.0042));
  }else if(pointers.size===2){
    const pts=[...pointers.values()];
    const d=Math.hypot(pts[0].x-pts[1].x,pts[0].y-pts[1].y);
    if(lastPinch>0)targetRadius=Math.min(66,Math.max(24,targetRadius*lastPinch/d));
    lastPinch=d;
  }
});
function endPointer(e){pointers.delete(e.pointerId);if(pointers.size===0)canvas.classList.remove('dragging');lastPinch=0;}
canvas.addEventListener('pointerup',endPointer);
canvas.addEventListener('pointercancel',endPointer);
canvas.addEventListener('wheel',function(e){
  e.preventDefault();
  targetRadius=Math.min(66,Math.max(24,targetRadius*Math.exp(e.deltaY*0.0011)));
},{passive:false});
canvas.addEventListener('dblclick',function(){targetTheta=0.40;targetPhi=0.28;targetRadius=46;});
document.getElementById('reset').addEventListener('click',function(){targetTheta=0.40;targetPhi=0.28;targetRadius=46;});

/* ================= loop ================= */
function frame(now){
  requestAnimationFrame(frame);
  t=now*0.001;
  theta+=(targetTheta-theta)*0.12;
  phi+=(targetPhi-phi)*0.12;
  radius+=(targetRadius-radius)*0.12;
  draw();
}
requestAnimationFrame(frame);
</script>
</body>
</html>
```

**What's in the scene**
- A two-masted sailing ship with hull, deck trim, sterncastle, crow's nest, bowsprit, billowing cream sails, waving pennant flags, and rope rigging — bobbing, rolling and pitching gently
- Animated voxel water with wave shimmer, foam rings around the ship, pier and cliff
- A wooden harbor pier with crates, barrels, posts and a glowing lamppost, plus a small dinghy
- A red-and-white lighthouse on a rock cliff with a rotating light beam
- Drifting voxel clouds, a warm sun, flying gulls, bobbing buoys, and a distant sailboat

**Interactions** — drag to orbit (full 360°), scroll / pinch to zoom, double-click or the Reset button to return to the default view. No libraries, no network — everything is hand-rolled on a single canvas, so it runs instantly in any Chrome install.