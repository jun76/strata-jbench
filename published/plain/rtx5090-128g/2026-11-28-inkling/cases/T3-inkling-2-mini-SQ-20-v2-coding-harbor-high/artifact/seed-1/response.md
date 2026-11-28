Here's the complete voxel art scene — a sailing ship at a harbor, fully self-contained in one HTML file (no external libraries, no internet needed):

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sailing Ship — Harbor Voxel Scene</title>
<style>
  html,body{margin:0;padding:0;height:100%;overflow:hidden;background:#20344a;}
  #c{display:block;width:100vw;height:100vh;cursor:grab;touch-action:none;}
  #c.dragging{cursor:grabbing;}
  .hud{position:fixed;pointer-events:none;font-family:Georgia,'Times New Roman',serif;color:#fdf6e3;text-shadow:0 2px 10px rgba(0,0,0,.5);user-select:none;}
  #title{top:18px;left:22px;}
  #title h1{font-size:19px;margin:0;letter-spacing:.14em;font-weight:600;}
  #title p{margin:3px 0 0;font-size:12px;opacity:.88;letter-spacing:.06em;}
  #hint{bottom:16px;left:50%;transform:translateX(-50%);font-size:12px;letter-spacing:.07em;background:rgba(10,20,32,.40);padding:7px 16px;border-radius:999px;backdrop-filter:blur(4px);white-space:nowrap;}
</style>
</head>
<body>
<canvas id="c"></canvas>
<div class="hud" id="title"><h1>&#9875; SAILING SHIP</h1><p>a harbor scene in voxels</p></div>
<div class="hud" id="hint">drag to orbit &nbsp;&middot;&nbsp; scroll to zoom &nbsp;&middot;&nbsp; double-click to reset</div>
<script>
(() => {
'use strict';
/* ================= setup ================= */
const canvas = document.getElementById('c');
const ctx = canvas.getContext('2d');
let W=0, H=0, DPR=1;
function resize(){
  DPR = Math.min(window.devicePixelRatio || 1, 2);
  W = window.innerWidth; H = window.innerHeight;
  canvas.width = Math.round(W*DPR); canvas.height = Math.round(H*DPR);
  canvas.style.width = W+'px'; canvas.style.height = H+'px';
  buildSky(); buildVignette();
}
window.addEventListener('resize', resize);

/* ================= colors ================= */
const C = {
  water:[38,110,150], foam:[238,246,248],
  quay:[180,166,140], quayDark:[150,136,112], base:[72,66,58],
  plank:[154,106,58], plankDark:[120,79,42], post:[93,60,30],
  hullRed:[152,53,36], hullDark:[44,26,14], deck:[158,110,62], deckDark:[128,86,48],
  rail:[72,45,25], mast:[74,46,26], yard:[102,66,36],
  sail:[238,230,206], sailBulge:[222,211,182], jib:[230,220,190],
  flag:[216,64,44], flagWhite:[245,240,226],
  crate:[168,120,62], barrel:[120,72,36],
  brick:[158,84,56], roofRed:[150,62,44], cream:[232,215,176],
  windowLit:[255,205,110], lighWhite:[238,234,224], lighRed:[196,62,48],
  lanternGlass:[255,228,120], frameDark:[52,50,64], dome:[58,56,72],
  crane:[214,128,44], craneDark:[120,74,26], cable:[47,47,56],
  cloud:[242,246,250], cloudTop:[252,253,255], sun:[255,214,90],
  gull:[245,245,240], gullWing:[206,212,218], buoyRed:[216,64,46], buoyWhite:[242,238,228]
};
function rgb(c,f){
  return 'rgb('+Math.min(255,Math.round(c[0]*f))+','+Math.min(255,Math.round(c[1]*f))+','+Math.min(255,Math.round(c[2]*f))+')';
}
function hash3(x,y,z){
  let h=(x*374761393 + y*668265263 + z*1274126177)|0;
  h=Math.imul(h ^ (h>>>13), 1274126177); h^=h>>>16;
  return (h>>>0)/4294967295;
}

/* ================= voxel storage ================= */
const voxels = new Map();
function key(x,y,z){ return x+'|'+y+'|'+z; }
function addVoxel(x,y,z,base,type,overwrite){
  const k = key(x,y,z);
  if(voxels.has(k) && !overwrite) return;
  voxels.set(k,{x,y,z,base,type,baseX:x,baseY:y,baseZ:z});
}
function box(x0,y0,z0,x1,y1,z1,base,type,overwrite){
  for(let x=x0;x<=x1;x++)for(let y=y0;y<=y1;y++)for(let z=z0;z<=z1;z++) addVoxel(x,y,z,base,type,overwrite);
}

/* ================= scene build ================= */
// base slab (diorama pedestal)
box(-27,-1,-19,27,-1,19,C.base,'static');
// water (skip quay strip and pier footprint)
for(let x=-26;x<=26;x++)for(let z=-9;z<=18;z++){
  if(x>=12&&x<=15&&z>=-9&&z<=9) continue;
  addVoxel(x,0,z,C.water,'water');
}
// quay land
for(let x=-26;x<=26;x++)for(let z=-18;z<=-10;z++)for(let y=0;y<=1;y++)
  addVoxel(x,y,z, y===1?C.quay:C.quayDark,'static');
// pier
for(let z=-9;z<=9;z++)for(let x=12;x<=15;x++)
  addVoxel(x,1,z, (z%2===0)?C.plank:C.plankDark,'static');
for(const pz of [-8,-4,0,4,8])for(const px of [12,15])
  addVoxel(px,0,pz,C.post,'static');
// pier shed
box(12,2,6,15,3,9,C.cream,'static');
box(12,4,6,15,4,9,C.roofRed,'static');
box(13,5,7,14,5,8,C.roofRed,'static');
addVoxel(13,2,9,[74,48,24],'static',true);
addVoxel(13,3,9,[74,48,24],'static',true);
// warehouse
box(-22,2,-17,-13,6,-13,C.brick,'static');
box(-22,7,-17,-13,7,-13,C.roofRed,'static');
box(-21,8,-16,-14,8,-14,C.roofRed,'static');
box(-19,9,-15,-16,9,-15,C.roofRed,'static');
addVoxel(-18,2,-13,[58,38,20],'static',true);
addVoxel(-18,3,-13,[58,38,20],'static',true);
addVoxel(-21,4,-13,C.windowLit,'static',true);
addVoxel(-14,4,-13,C.windowLit,'static',true);
// house
box(-8,2,-17,-3,5,-13,C.cream,'static');
box(-9,6,-18,-2,6,-12,C.roofRed,'static');
box(-7,7,-16,-4,7,-14,C.roofRed,'static');
addVoxel(-6,2,-13,[58,38,20],'static',true);
addVoxel(-6,3,-13,[58,38,20],'static',true);
addVoxel(-8,4,-13,C.windowLit,'static',true);
addVoxel(-3,4,-13,C.windowLit,'static',true);
addVoxel(-7,7,-16,C.brick,'static',true);
addVoxel(-7,8,-16,C.brick,'static',true);
// lighthouse
box(14,2,-17,18,4,-14,C.lighWhite,'static');
box(14,5,-17,18,7,-14,C.lighRed,'static');
box(14,8,-17,18,10,-14,C.lighWhite,'static');
box(14,11,-17,18,12,-14,C.lighRed,'static');
box(15,13,-16,17,13,-15,C.frameDark,'static');
addVoxel(16,13,-16,C.lanternGlass,'beacon',true);
addVoxel(16,13,-15,C.lanternGlass,'beacon',true);
box(15,14,-16,17,14,-15,C.dome,'static');
box(16,15,-16,16,15,-15,C.dome,'static');
// crane (reaches over the water)
box(7,2,-13,7,6,-13,C.crane,'static');
box(7,6,-13,7,6,-6,C.crane,'static');
addVoxel(7,6,-14,C.craneDark,'static');
addVoxel(7,5,-7,C.cable,'static');
addVoxel(7,4,-7,C.cable,'static');
addVoxel(7,3,-7,C.craneDark,'static');
addVoxel(7,2,-7,C.crate,'static');
// crates & barrels on quay
addVoxel(-1,2,-12,C.crate,'static');
addVoxel(0,2,-12,C.crate,'static');
addVoxel(-1,3,-12,C.crate,'static');
addVoxel(3,2,-12,C.barrel,'static');
addVoxel(4,2,-12,C.barrel,'static');
addVoxel(3,3,-12,C.barrel,'static');
// buoys + foam rings
function buoy(bx,bz){
  addVoxel(bx,0,bz,C.buoyRed,'static',true);
  addVoxel(bx,1,bz,C.buoyWhite,'static');
  addVoxel(bx,2,bz,C.buoyRed,'static');
  for(const [dx,dz] of [[-1,0],[1,0],[0,-1],[0,1]])
    addVoxel(bx+dx,0,bz+dz,C.foam,'foam',true);
}
buoy(-12,0); buoy(5,7);
// harbor foam: hull sides, bow, wake
for(let z=-6;z<=8;z+=2){
  addVoxel(-7,0,z,C.foam,'foam',true);
  addVoxel(-1,0,z,C.foam,'foam',true);
}
addVoxel(-5,0,10,C.foam,'foam',true);
addVoxel(-4,0,10,C.foam,'foam',true);
addVoxel(-3,0,10,C.foam,'foam',true);
addVoxel(-4,0,-6,C.foam,'foam',true);
addVoxel(-5,0,-7,C.foam,'foam',true);
addVoxel(-3,0,-7,C.foam,'foam',true);
// sun (chunky voxel sun)
box(-20,24,-14,-19,25,-13,C.sun,'static');

/* ---- ship ---- */
const sx=-4, sz=1;
const shipVoxels=[];
function addShip(x,y,z,base){
  const v = voxels.get(key(x,y,z));
  if(v){ v.base = base; v.type='ship'; v.baseX=x; v.baseY=y; v.baseZ=z; }
  else { addVoxel(x,y,z,base,'ship'); const nv = voxels.get(key(x,y,z)); nv.type='ship'; nv.baseX=x; nv.baseY=y; nv.baseZ=z; }
  shipVoxels.push(voxels.get(key(x,y,z)));
}
function sbox(x0,y0,z0,x1,y1,z1,base){
  for(let x=x0;x<=x1;x++)for(let y=y0;y<=y1;y++)for(let z=z0;z<=z1;z++) addShip(x,y,z,base);
}
// hull: keel (in water), deck row (red sides + planks), rails, stern castle
sbox(sx-1,0,sz-5,sx+1,0,sz+7,C.hullDark);            // keel
for(let z=sz-6;z<=sz+8;z++){
  addShip(sx-2,1,z,C.hullRed); addShip(sx+2,1,z,C.hullRed);
  for(let x=sx-1;x<=sx+1;x++) addShip(x,1,z,(z%2===0)?C.deck:C.deckDark);
}
addShip(sx,1,sz+9,C.hullRed);                          // bow tip
sbox(sx-2,2,sz-6,sx-2,2,sz+8,C.rail);                  // rails
sbox(sx+2,2,sz-6,sx+2,2,sz+8,C.rail);
sbox(sx-1,2,sz-6,sx+1,2,sz-3,C.plank);                 // raised stern castle
addShip(sx,3,sz-6,[255,210,74]);                       // stern lantern
// masts
sbox(sx,2,sz+5,sx,12,sz+5,C.mast);                     // fore mast
sbox(sx,2,sz-1,sx,14,sz-1,C.mast);                     // main mast
// yards
sbox(sx-3,11,sz+5,sx+3,11,sz+5,C.yard);                // fore upper yard
sbox(sx-2,6,sz+5,sx+2,6,sz+5,C.yard);                  // fore lower yard
sbox(sx-4,12,sz-1,sx+4,12,sz-1,C.yard);                // main upper yard
sbox(sx-3,6,sz-1,sx+3,6,sz-1,C.yard);                  // main lower yard
// sails (with wind bulge toward bow)
sbox(sx-3,8,sz+5,sx+3,10,sz+5,C.sail);
sbox(sx-2,9,sz+6,sx+2,10,sz+6,C.sailBulge);
sbox(sx-2,3,sz+5,sx+2,5,sz+5,C.sail);
sbox(sx-1,3,sz+6,sx+1,4,sz+6,C.sailBulge);
sbox(sx-4,8,sz-1,sx+4,11,sz-1,C.sail);
sbox(sx-3,9,sz,sx+3,11,sz,C.sailBulge);
sbox(sx-3,3,sz-1,sx+3,5,sz-1,C.sail);
sbox(sx-2,3,sz,sx+2,4,sz,C.sailBulge);
// crow's nest
sbox(sx-1,7,sz-2,sx+1,7,sz,C.plankDark);
// jib (triangle toward bowsprit)
const jibSteps=[[12,4],[11,5],[10,6],[9,7],[8,8],[7,9],[6,10]];
for(const [dz,dy] of jibSteps) addShip(sx,dy,dz,C.jib);
// bowsprit
addShip(sx,2,10,C.mast); addShip(sx,2,11,C.mast); addShip(sx,2,12,C.mast); addShip(sx,3,13,C.mast);
// deck cargo
addShip(sx-1,2,3,C.crate);
addShip(sx+1,2,4,C.barrel);

/* ---- dynamic: flag / gulls / clouds ---- */
function dynVoxel(base){
  return {x:0,y:0,z:0,base,baseX:0,baseY:0,baseZ:0,expTop:true,expPX:true,expNX:true,expPZ:true,expNZ:true,
    _top:rgb(base,1),_sx:rgb(base,0.74),_sz:rgb(base,0.52)};
}
const flagVoxels=[];
for(let i=0;i<3;i++){
  const base = (i===1)?C.flagWhite:C.flag;
  const v = dynVoxel(base); v.i=i; flagVoxels.push(v);
}
const gullSpecs=[
  {cx:sx+1, cy:16.5, cz:2,  r:7,   w:0.26, ph:0.0},
  {cx:-2,   cy:18.5, cz:-2, r:9,   w:0.20, ph:2.1},
  {cx:-14,  cy:17.5, cz:8,  r:5.5, w:0.32, ph:4.2}
];
const gulls=[];
for(const g of gullSpecs){
  gulls.push({...g, body:dynVoxel(C.gull), wl:dynVoxel(C.gullWing), wr:dynVoxel(C.gullWing)});
}
const cloudSpecs=[
  {bx:-12, by:21.5, bz:-6, speed:0.55, pattern:[[0,0,0],[1,0,0],[2,0,0],[3,0,0],[1,1,0],[2,1,0]]},
  {bx:6,   by:23.0, bz:-10,speed:0.42, pattern:[[0,0,0],[1,0,0],[2,0,0],[3,0,0],[4,0,0],[1,1,0],[2,1,0]]},
  {bx:16,  by:20.5, bz:6,  speed:0.70, pattern:[[0,0,0],[1,0,0],[2,0,0],[1,1,0]]}
];
const clouds=[];
for(const c of cloudSpecs){
  const vs=[];
  for(const [dx,dy,dz] of c.pattern){
    const base = dy>0 ? C.cloudTop : C.cloud;
    const v = dynVoxel(base); v.dx=dx; v.dy=dy; v.dz=dz; vs.push(v);
  }
  clouds.push({...c, voxels:vs});
}

/* ================= derived data ================= */
for(const v of voxels.values()){
  const noise = 0.93 + 0.12*hash3(v.baseX,v.baseY,v.baseZ);
  v.expTop = !voxels.has(key(v.baseX,v.baseY+1,v.baseZ));
  v.expPX  = !voxels.has(key(v.baseX+1,v.baseY,v.baseZ));
  v.expNX  = !voxels.has(key(v.baseX-1,v.baseY,v.baseZ));
  v.expPZ  = !voxels.has(key(v.baseX,v.baseY,v.baseZ+1));
  v.expNZ  = !voxels.has(key(v.baseX,v.baseY,v.baseZ-1));
  v.expAny = v.expTop||v.expPX||v.expNX||v.expPZ||v.expNZ;
  if(v.type!=='water' && v.type!=='foam' && v.type!=='beacon'){
    v._top=rgb(v.base,noise); v._sx=rgb(v.base,noise*0.74); v._sz=rgb(v.base,noise*0.52);
  }
}
const waterList=[], foamList=[], beaconList=[];
for(const v of voxels.values()){
  if(v.type==='water') waterList.push(v);
  else if(v.type==='foam') foamList.push(v);
  else if(v.type==='beacon') beaconList.push(v);
}
// re-push duplicated voxels (ship helpers pushed duplicates) — dedupe shipVoxels
const shipSet = new Set();
const shipList = [];
for(const v of shipVoxels){ if(!shipSet.has(v)){ shipSet.add(v); shipList.push(v); } }

/* ================= camera & controls ================= */
const T = {x:0,y:4,z:0};
let az=-2.1, el=0.30, zoom=0.66, zoomTarget=1.0;
let lastInteract=0, introDone=false, lastPinch=0;
const introStart=performance.now();
let dragging=false, lastX=0, lastY=0;
const pointers=new Map();
function clamp(v,a,b){ return v<a?a:(v>b?b:v); }
function wrap(v,a,b){ const r=b-a; return ((v-a)%r + r)%r + a; }

canvas.addEventListener('pointerdown', e=>{
  canvas.setPointerCapture(e.pointerId);
  pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});
  if(pointers.size===1){ dragging=true; lastX=e.clientX; lastY=e.clientY; canvas.classList.add('dragging'); }
  lastPinch=0; introDone=true; lastInteract=performance.now();
});
canvas.addEventListener('pointermove', e=>{
  if(!pointers.has(e.pointerId)) return;
  pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});
  if(pointers.size===1 && dragging){
    const dx=e.clientX-lastX, dy=e.clientY-lastY;
    lastX=e.clientX; lastY=e.clientY;
    az += dx*0.005;
    el = clamp(el + dy*0.004, 0.28, 1.15);
  } else if(pointers.size===2){
    const pts=[...pointers.values()];
    const d=Math.hypot(pts[0].x-pts[1].x, pts[0].y-pts[1].y);
    if(lastPinch>0) zoomTarget = clamp(zoomTarget*d/lastPinch, 0.45, 2.6);
    lastPinch=d;
  }
  lastInteract=performance.now();
});
function endPointer(e){
  pointers.delete(e.pointerId);
  if(pointers.size<2) lastPinch=0;
  if(pointers.size===0){ dragging=false; canvas.classList.remove('dragging'); }
  lastInteract=performance.now();
}
canvas.addEventListener('pointerup', endPointer);
canvas.addEventListener('pointercancel', endPointer);
canvas.addEventListener('wheel', e=>{
  e.preventDefault();
  zoomTarget = clamp(zoomTarget*Math.exp(-e.deltaY*0.0011), 0.45, 2.6);
  introDone=true; lastInteract=performance.now();
},{passive:false});
canvas.addEventListener('dblclick', ()=>{
  az=0.62; el=0.62; zoomTarget=1.0; zoom=Math.max(zoom,0.8);
  introDone=true; lastInteract=performance.now();
});

/* ================= render helpers ================= */
let skyGrad=null, vigGrad=null;
function buildSky(){
  skyGrad = ctx.createLinearGradient(0,0,0,H);
  skyGrad.addColorStop(0,'#3a7bc0');
  skyGrad.addColorStop(0.45,'#7ab8d8');
  skyGrad.addColorStop(0.72,'#f4dfa8');
  skyGrad.addColorStop(1,'#e8cf9a');
}
function buildVignette(){
  vigGrad = ctx.createRadialGradient(W/2,H/2,Math.min(W,H)*0.34, W/2,H/2, Math.max(W,H)*0.75);
  vigGrad.addColorStop(0,'rgba(8,14,24,0)');
  vigGrad.addColorStop(1,'rgba(8,14,24,0.34)');
}
let cosAz=1, sinAz=0, cosEl=1, sinEl=0, scale=14, cx_=0, cy_=0;
function corner(x,y,z){
  const dx=x-T.x, dy=y-T.y, dz=z-T.z;
  const rx = dx*cosAz - dz*sinAz;
  const ry = -(dx*sinAz + dz*cosAz)*sinEl + dy*cosEl;
  return [cx_ + rx*scale, cy_ - ry*scale];
}
function project(x,y,z){
  const p = corner(x,y,z); return {x:p[0], y:p[1]};
}
function face(p1,p2,p3,p4,color,stroke){
  ctx.beginPath();
  ctx.moveTo(p1[0],p1[1]); ctx.lineTo(p2[0],p2[1]); ctx.lineTo(p3[0],p3[1]); ctx.lineTo(p4[0],p4[1]);
  ctx.closePath();
  ctx.fillStyle=color; ctx.fill();
  if(stroke){ ctx.strokeStyle='rgba(20,16,12,0.22)'; ctx.lineWidth=1; ctx.stroke(); }
}
function drawVoxel(v){
  const x0=v.x-0.5, x1=v.x+0.5, y0=v.y-0.5, y1=v.y+0.5, z0=v.z-0.5, z1=v.z+0.5;
  // cull far off-screen
  const dx=v.x-T.x, dy=v.y-T.y, dz=v.z-T.z;
  const rx = dx*cosAz - dz*sinAz;
  const ry = -(dx*sinAz + dz*cosAz)*sinEl + dy*cosEl;
  const px = cx_ + rx*scale, py = cy_ - ry*scale;
  if(px<-120||px>W+120||py<-120||py>H+120) return;
  const A=corner(x0,y1,z0), B=corner(x1,y1,z0), D=corner(x0,y1,z1), C=corner(x1,y1,z1);
  const E=corner(x0,y0,z0), F=corner(x1,y0,z0), G=corner(x1,y0,z1), H2=corner(x0,y0,z1);
  const drawPX = sinAz>0, drawPZ = cosAz>0;
  if(drawPX){ if(v.expPX) face(B,C,G,F,v._sx,false); }
  else { if(v.expNX) face(A,D,H2,E,v._sx,false); }
  if(drawPZ){ if(v.expPZ) face(C,D,H2,G,v._sz,false); }
  else { if(v.expNZ) face(A,B,F,E,v._sz,false); }
  if(v.expTop) face(A,B,C,D,v._top,true);
}

/* ================= animation ================= */
const items=[];
let lastFrame=0;
function frame(now){
  const t=now/1000;
  const dt=Math.min(0.05, (now-lastFrame)/1000 || 0.016);
  lastFrame=now;
  // intro / idle auto-rotate
  if(!introDone){
    const p=Math.min(1,(now-introStart)/2300);
    const e=1-Math.pow(1-p,3);
    az = -2.1 + (0.62+2.1)*e;
    el = 0.30 + (0.62-0.30)*e;
    zoom = 0.66 + (1.0-0.66)*e;
    zoomTarget=1.0;
    if(p>=1) introDone=true;
  } else if(now-lastInteract>3000){
    az += dt*0.055;
  }
  zoom += (zoomTarget-zoom)*Math.min(1,dt*7);

  // ship bob / roll / pitch
  const bob = Math.sin(t*0.85)*0.22;
  const roll = Math.sin(t*0.55)*0.05;
  const pitch = Math.sin(t*0.45+1.0)*0.02;
  for(const v of shipList){
    v.y = v.baseY + bob + roll*(v.baseX-sx) + pitch*(v.baseZ-sz);
  }
  // flag wave
  for(let i=0;i<flagVoxels.length;i++){
    const v=flagVoxels[i];
    v.x=sx; v.y=14.55 + Math.sin(t*6 - i*1.3)*0.3; v.z=-1-i;
  }
  // gulls
  for(const g of gulls){
    const p=t*g.w + g.ph;
    const gx=g.cx + Math.cos(p)*g.r;
    const gz=g.cz + Math.sin(p)*g.r*0.6;
    const gy=g.cy + Math.sin(t*0.8+g.ph)*1.3;
    g.body.x=gx; g.body.y=gy; g.body.z=gz;
    const flap=Math.sin(t*7+g.ph)*0.75;
    g.wl.x=gx-1; g.wl.y=gy+flap; g.wl.z=gz;
    g.wr.x=gx+1; g.wr.y=gy+flap; g.wr.z=gz;
  }
  // clouds drift
  for(const c of clouds){
    const cx=wrap(c.bx + t*c.speed, -36, 36);
    for(const v of c.voxels){ v.x=cx+v.dx; v.y=c.by+v.dy; v.z=c.bz+v.dz; }
  }
  // water shimmer
  for(const v of waterList){
    const f=1 + 0.13*Math.sin(t*1.7 + v.baseX*0.55 + v.baseZ*0.42) + 0.06*Math.sin(t*2.9 + (v.baseX+v.baseZ)*0.3);
    v._top=rgb(v.base,f); v._sx=rgb(v.base,f*0.74); v._sz=rgb(v.base,f*0.52);
  }
  // foam pulse
  for(const v of foamList){
    const f=0.80 + 0.28*Math.sin(t*3.1 + v.baseX*1.7 + v.baseZ*2.3);
    v._top=rgb(v.base,f); v._sx=rgb(v.base,f*0.74); v._sz=rgb(v.base,f*0.52);
  }
  // beacon pulse
  for(const v of beaconList){
    const f=0.72 + 0.40*Math.sin(t*2.2);
    v._top=rgb(v.base,f); v._sx=rgb(v.base,f*0.74); v._sz=rgb(v.base,f*0.52);
  }

  // camera basis
  cosAz=Math.cos(az); sinAz=Math.sin(az); cosEl=Math.cos(el); sinEl=Math.sin(el);
  cx_=W/2; cy_=H*0.55;
  scale=Math.min(W/72, H/58)*zoom;

  // build & sort draw list
  items.length=0;
  for(const v of voxels.values()){ if(v.expAny) items.push(v); }
  for(const g of gulls){ items.push(g.body,g.wl,g.wr); }
  for(const c of clouds){ for(const v of c.voxels) items.push(v); }
  for(const v of flagVoxels) items.push(v);
  for(const v of items){
    const dx=v.x-T.x, dy=v.y-T.y, dz=v.z-T.z;
    v._depth=(dx*sinAz + dz*cosAz)*cosEl + dy*sinEl;
  }
  items.sort((a,b)=>a._depth-b._depth);

  /* ---------- draw ---------- */
  ctx.setTransform(DPR,0,0,DPR,0,0);
  ctx.fillStyle=skyGrad; ctx.fillRect(0,0,W,H);
  for(const v of items) drawVoxel(v);

  // lighthouse beam (rotating sweep)
  const bp=project(16,13.6,-15);
  const beamLen=Math.min(W,H)*0.8;
  ctx.save();
  ctx.translate(bp.x,bp.y); ctx.rotate(t*0.45);
  const beamGrad=ctx.createLinearGradient(0,0,beamLen,0);
  beamGrad.addColorStop(0,'rgba(255,238,170,0.28)');
  beamGrad.addColorStop(1,'rgba(255,238,170,0)');
  ctx.fillStyle=beamGrad;
  ctx.beginPath(); ctx.moveTo(0,-9); ctx.lineTo(beamLen,-2); ctx.lineTo(beamLen,2); ctx.lineTo(0,9); ctx.closePath(); ctx.fill();
  ctx.restore();
  // sun glow
  const sp=project(-19.5,24.7,-13.5);
  ctx.save(); ctx.globalCompositeOperation='screen';
  const sg=ctx.createRadialGradient(sp.x,sp.y,0,sp.x,sp.y,150);
  sg.addColorStop(0,'rgba(255,235,160,0.8)');
  sg.addColorStop(1,'rgba(255,235,160,0)');
  ctx.fillStyle=sg; ctx.beginPath(); ctx.arc(sp.x,sp.y,150,0,Math.PI*2); ctx.fill();
  ctx.restore();
  // vignette
  ctx.fillStyle=vigGrad; ctx.fillRect(0,0,W,H);

  requestAnimationFrame(frame);
}

resize();
requestAnimationFrame(frame);
})();
</script>
</body>
</html>
```

**What's in the scene:** a voxel harbor diorama — a red-striped sailing ship with cream sails (two masts, wind-bulge sails, jib, crow's nest, stern lantern, waving flag, bobbing/pitching animation), a stone quay with a brick warehouse, a cottage with chimney, an orange crane with a hanging crate, crates and barrels, a striped lighthouse with a pulsing beacon and rotating light beam, a wooden pier with a little shed, drifting clouds, flapping seagulls, red-and-white buoys, foam and wake, and an animated shimmering water plane — all inside a floating diorama base.

**Controls:** drag to orbit, scroll (or pinch) to zoom, double-click to reset. The camera slowly auto-rotates when idle and sweeps in on load. Just paste into an `.html` file and open in Chrome — it works fully offline.