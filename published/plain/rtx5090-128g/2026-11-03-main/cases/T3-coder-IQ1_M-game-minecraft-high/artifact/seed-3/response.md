진안. 아래는 한 HTML의 **Minecraft-лиke 3D voxel sandbox game** you can save as `minecraft-3d.html` and open directly in a browser.

Controls:

- Click once: mouse lock / FPS view
- After lock: Left click = block destroy, Right click = block place
- Mouse move = camera view
- `WASD` = move
- `J` or `Space` = jump
- `Shift` = run
- `Q` = destroy block
- `E` = place block
- `Wheel mouse scroll` = select block type
- `1-8` keys = select block type
- `R` = respawn

---

```html
<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>MicroCraft 3D Sandbox</title>
<style>
html,body{margin:0;overflow:hidden;background:#000;height:100%;}
canvas{display:block;width:100%;height:100%;}
#ui{
  position:fixed;
  top:14px;
  left:14px;
  pointer-events:none;
  user-select:none;
  font-family:system-ui, sans-serif;
  font-size:13px;
  color:#e8f4e8;
  background:rgba(0,0,0,.38);
  padding:10px 12px;
  border-radius:10px;
  line-height:1.45;
  max-width:430px;
}
#cross{
  position:fixed;
  left:50%;
  top:50%;
  transform:translate(-50%,-50%);
  pointer-events:none;
  width:16px;
  height:16px;
  border:2px solid rgba(255,255,255,.95);
  background:rgba(255,255,255,.08);
  border-radius:2px;
  box-shadow:0 0 8px rgba(0,0,0,.35);
}
</style>
</head>
<body>
<div id="ui">
<strong>MicroCraft 3D Sandbox</strong><br>
Click to mouse lock.<br>
Mouse move: camera.<br>
Left click: destroy, Right click: place.<br>
WASD move, J/Space jump, Shift run.<br>
Q destroy, E place.<br>
Wheel/1-8 select block.<br>
R respawn.
</div>
<div id="cross"></div>
<canvas id="c"></canvas>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function(){
const canvas = document.getElementById("c");
const ui = document.getElementById("ui");

let renderer = new THREE.WebGLRenderer({canvas:canvas, antialias:true});
renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
renderer.setSize(window.innerWidth, window.innerHeight);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x9fdfff);
scene.fog = new THREE.Fog(0x9fdfff, 35, 150);

const camera = new THREE.PerspectiveCamera(72, window.innerWidth/window.innerHeight, 0.01, 240);
camera.rotation.order = "YXZ";

scene.add(new THREE.HemisphereLight(0xffffff, 0x777777, 1.15));
const sun = new THREE.DirectionalLight(0xffffff, 0.75);
sun.position.set(45,80,30);
scene.add(sun);

const geometry = new THREE.BoxGeometry(1,1,1);

const types = ["grass","dirt","stone","wood","leaf","sand","brick","glass"];
let selected = 0;

const materials = {};
const meshes = {};
const counts = {};
const capacities = {};
const slotKeys = {};
const slotMap = new Map(); // voxel key -> slot index
const blocks = new Map();  // voxel key -> type

const WORLD_R = 22;
const MAX_Y = 70;
const OFF = 512;

function key(x,y,z){
  return (x+OFF)*1000000 + (y+OFF)*1000 + (z+OFF);
}
function unkey(k){
  const z = (k%1000)-OFF;
  k = Math.floor(k/1000);
  const y = (k%1000)-OFF;
  k = Math.floor(k/1000);
  const x = (k%1000000)-OFF;
  return {x,y,z};
}
function valid(x,y,z){
  return Math.abs(x)<=WORLD_R+2 && Math.abs(z)<=WORLD_R+2 && y>=-8 && y<=MAX_Y;
}
function hasBlock(x,y,z){
  return blocks.has(key(x,y,z));
}

function makeTexture(type){
  const size = 32;
  const c = document.createElement("canvas");
  c.width = size; c.height = size;
  const ctx = c.getContext("2d");

  let base = "#808080";
  if(type==="grass") base="#58a943";
  else if(type==="dirt") base="#8a5d3f";
  else if(type==="stone") base="#8d939c";
  else if(type==="wood") base="#77542e";
  else if(type==="leaf") base="#3f8b35";
  else if(type==="sand") base="#d8c89b";
  else if(type==="brick") base="#a3423f";
  else if(type==="glass") base="#9ad9ed";

  ctx.fillStyle = base;
  ctx.fillRect(0,0,size,size);

  for(let i=0;i<260;i++){
    const x = Math.floor(Math.random()*size);
    const y = Math.floor(Math.random()*size);
    const a = Math.random()*0.10;
    ctx.fillStyle = `rgba(0,0,0,${a})`;
    ctx.fillRect(x,y,1,1);
  }
  for(let i=0;i<200;i++){
    const x = Math.floor(Math.random()*size);
    const y = Math.floor(Math.random()*size);
    const a = Math.random()*0.10;
    ctx.fillStyle = `rgba(255,255,255,${a})`;
    ctx.fillRect(x,y,1,1);
  }

  if(type==="grass"){
    ctx.fillStyle = "rgba(45,120,35,.45)";
    for(let i=0;i<18;i++){
      ctx.fillRect(Math.floor(Math.random()*size), Math.floor(Math.random()*size), 1, Math.floor(Math.random()*4)+1);
    }
  }

  if(type==="dirt"){
    ctx.fillStyle = "rgba(95,55,25,.55)";
    for(let i=0;i<12;i++){
      ctx.beginPath();
      ctx.arc(Math.random()*size, Math.random()*size, Math.random()*2+.5, 0, Math.PI*2);
      ctx.fill();
    }
  }

  if(type==="stone"){
    ctx.strokeStyle = "rgba(70,80,85,.7)";
    ctx.lineWidth = 1;
    for(let i=0;i<5;i++){
      ctx.beginPath();
      ctx.moveTo(Math.random()*size, Math.random()*size);
      ctx.lineTo(Math.random()*size, Math.random()*size);
      ctx.stroke();
    }
  }

  if(type==="wood"){
    ctx.strokeStyle = "rgba(55,30,15,.75)";
    ctx.lineWidth = 2;
    for(let y=3;y<size;y+=7){
      ctx.beginPath();
      ctx.moveTo(0,y);
      ctx.lineTo(size,y+Math.random()*2-1);
      ctx.stroke();
    }
  }

  if(type==="leaf"){
    ctx.fillStyle = "rgba(25,90,20,.35)";
    for(let i=0;i<30;i++){
      ctx.fillRect(Math.floor(Math.random()*size), Math.floor(Math.random()*size), 2, 2);
    }
  }

  if(type==="sand"){
    ctx.fillStyle = "rgba(255,230,180,.35)";
    for(let i=0;i<28;i++){
      ctx.fillRect(Math.floor(Math.random()*size), Math.floor(Math.random()*size), 1, 1);
    }
  }

  if(type==="brick"){
    ctx.strokeStyle = "rgba(180,180,180,.75)";
    ctx.lineWidth = 2;
    for(let y=0;y<size;y+=8){
      ctx.beginPath();
      ctx.moveTo(0,y+3);
      ctx.lineTo(size,y+3);
      ctx.stroke();
    }
    for(let y=0;y<size;y+=16){
      ctx.beginPath();
      ctx.moveTo(size/2,y);
      ctx.lineTo(size/2,y+8);
      ctx.stroke();
    }
  }

  if(type==="glass"){
    ctx.fillStyle = "rgba(255,255,255,.78)";
    ctx.fillRect(0,0,size,2);
    ctx.fillRect(0,size-2,size,2);
    ctx.fillRect(0,0,2,size);
    ctx.fillRect(size-2,0,2,size);
  }

  const tex = new THREE.CanvasTexture(c);
  tex.magFilter = THREE.NearestFilter;
  tex.minFilter = THREE.NearestFilter;
  return tex;
}

function makeMaterial(type){
  const tex = makeTexture(type);
  if(type==="glass"){
    return new THREE.MeshLambertMaterial({map:tex, transparent:true, opacity:0.65});
  }
  return new THREE.MeshLambertMaterial({map:tex});
}

function ensureCapacity(type){
  if(counts[type] < capacities[type]) return meshes[type];

  const old = meshes[type];
  const oldCount = counts[type];
  const newCap = capacities[type] * 2;
  const mat = materials[type];

  const mesh = new THREE.InstancedMesh(geometry, mat, newCap);
  const tmp = new THREE.Matrix4();
  for(let i=0;i<oldCount;i++){
    old.getMatrixAt(i, tmp);
    mesh.setMatrixAt(i, tmp);
  }
  mesh.count = oldCount;
  mesh.instanceMatrix.needsUpdate = true;

  scene.remove(old);
  scene.add(mesh);

  meshes[type] = mesh;
  capacities[type] = newCap;
  return mesh;
}

const dummy = new THREE.Object3D();

function setBlockMatrix(type, idx, x,y,z){
  dummy.position.set(x+0.5,y+0.5,z+0.5);
  dummy.rotation.set(0,0,0);
  dummy.scale.set(1,1,1);
  dummy.updateMatrix();
  meshes[type].setMatrixAt(idx, dummy.matrix);
  meshes[type].instanceMatrix.needsUpdate = true;
}

function addBlock(x,y,z,type){
  const k = key(x,y,z);
  if(blocks.has(k)) return false;
  if(!valid(x,y,z)) return false;

  if(counts[type] === capacities[type]) ensureCapacity(type);

  const idx = counts[type];
  setBlockMatrix(type, idx, x,y,z);

  blocks.set(k,type);
  slotKeys[type].push(k);
  slotMap.set(k, idx);
  counts[type]++;
  meshes[type].count = counts[type];
  return true;
}

function removeBlock(type,k){
  if(!blocks.has(k)) return false;
  const arr = slotKeys[type];
  const c = counts[type];
  const idx = slotMap.get(k);
  const lastIdx = c-1;
  const lastKey = arr[lastIdx];

  const tmp = new THREE.Matrix4();
  if(idx !== lastIdx){
    meshes[type].getMatrixAt(lastIdx, tmp);
    meshes[type].setMatrixAt(idx, tmp);
    arr[idx] = lastKey;
    slotMap.set(lastKey, idx);
  }

  arr.length = lastIdx;
  counts[type] = lastIdx;
  meshes[type].count = lastIdx;
  meshes[type].instanceMatrix.needsUpdate = true;

  blocks.delete(k);
  slotMap.delete(k);
  return true;
}

for(const t of types){
  const mat = makeMaterial(t);
  materials[t] = mat;

  const cap = 512;
  const mesh = new THREE.InstancedMesh(geometry, mat, cap);
  mesh.count = 0;
  scene.add(mesh);

  meshes[t] = mesh;
  counts[t] = 0;
  capacities[t] = cap;
  slotKeys[t] = [];
}

const D = WORLD_R*2+1;
const top = new Int32Array(D*D);
function topIndex(x,z){
  return (x+WORLD_R)*D + (z+WORLD_R);
}

function terrainHeight(x,z){
  const a = Math.sin(x*0.22)*Math.cos(z*0.18)*1.5;
  const b = Math.sin((x+z)*0.07)*1.25;
  const c = Math.sin(x*0.31)*Math.cos(z*0.17)*0.9;
  let h = Math.floor(4 + a + b + c);
  return Math.max(1, Math.min(8,h));
}

for(let x=-WORLD_R; x<=WORLD_R; x++){
  for(let z=-WORLD_R; z<=WORLD_R; z++){
    const h = terrainHeight(x,z);
    top[topIndex(x,z)] = h + 1;
    for(let y=0; y<=h; y++){
      let type = "stone";
      if(y === h) type = "grass";
      else if(y >= h-2) type = "dirt";
      addBlock(x,y,z,type);
    }
  }
}

function placeTree(cx,cz){
  if(Math.abs(cx) < 5 && Math.abs(cz) < 5) return;
  const idx = topIndex(cx,cz);
  const gy = top[idx];
  const trunk = 4;

  for(let y=gy; y<gy+trunk; y++) addBlock(cx,y,cz,"wood");

  const ty = gy + trunk - 1;
  for(let dy=-2; dy<=2; dy++){
    for(let dx=-2; dx<=2; dx++){
      for(let dz=-2; dz<=2; dz++){
        const dist2 = dx*dx + dz*dz + dy*dy*1.5;
        if(dist2 <= 5.5){
          addBlock(cx+dx,ty+dy,cz+dz,"leaf");
        }
      }
    }
  }
}

for(let i=0;i<16;i++){
  const x = Math.floor((Math.random()*2-1)*(WORLD_R-3));
  const z = Math.floor((Math.random()*2-1)*(WORLD_R-3));
  placeTree(x,z);
}

const PLAYER_H = 1.7;
const PLAYER_W = 0.6;
const HALF_W = PLAYER_W/2;
const HALF_H = PLAYER_H/2;
const GRAVITY = 16;
const JUMP = 8.4;
const WALK = 4.2;
const RUN = 7.4;

const spawnTop = top[topIndex(0,0)];
let px = 0.5;
let pz = 0.5;
let py = spawnTop + HALF_H + 0.1;
let vy = 0;

let yaw = 0;
let pitch = -0.12;

const keys = new Set();
let locked = false;
let lockTime = 0;
let lastAction = 0;
let lastRespawn = 0;

function clamp(v,a,b){ return Math.max(a,Math.min(b,v)); }

function updateUI(){
  ui.innerHTML =
    `<strong>MicroCraft 3D Sandbox</strong><br>` +
    `Selected: ${types[selected]}<br>` +
    `Blocks: ${blocks.size}<br>` +
    `Mouse move: camera.<br>` +
    `Left click: destroy, Right click: place.<br>` +
    `WASD move, J/Space jump, Shift run.<br>` +
    `Q destroy, E place.<br>` +
    `Wheel/1-8 select block.<br>` +
    `R respawn.`;
}

function requestLock(){
  if(locked) return;
  try{
    document.requestPointerLock();
    lockTime = performance.now();
  }catch(e){}
}

document.addEventListener("pointerlockchange", () => {
  locked = document.pointerLockElement === canvas;
  if(locked) lockTime = performance.now();
});

canvas.addEventListener("click", requestLock);

document.addEventListener("mousemove", (e) => {
  if(!locked) return;
  yaw -= e.movementX * 0.0023;
  pitch -= e.movementY * 0.0023;
  pitch = clamp(pitch, -1.55, 1.55);
});

document.addEventListener("contextmenu", (e) => e.preventDefault());

function camPos(){
  const v = new THREE.Vector3();
  camera.getWorldPosition(v);
  return v;
}
function camDir(){
  const v = new THREE.Vector3();
  camera.getWorldDirection(v);
  v.normalize();
  return v;
}

function raycastVoxel(origin, dir, maxDist=100){
  let x = Math.floor(origin.x);
  let y = Math.floor(origin.y);
  let z = Math.floor(origin.z);

  const sx = dir.x > 0 ? 1 : dir.x < 0 ? -1 : 0;
  const sy = dir.y > 0 ? 1 : dir.y < 0 ? -1 : 0;
  const sz = dir.z > 0 ? 1 : dir.z < 0 ? -1 : 0;

  const dX = Math.abs(dir.x), dY = Math.abs(dir.y), dZ = Math.abs(dir.z);

  const tDX = sx===0 ? Infinity : 1/dX;
  const tDY = sy===0 ? Infinity : 1/dY;
  const tDZ = sz===0 ? Infinity : 1/dZ;

  let tX = Infinity, tY = Infinity, tZ = Infinity;

  if(sx > 0) tX = (x + 1 - origin.x)/dir.x;
  if(sx < 0) tX = (x - origin.x)/dir.x;
  if(sy > 0) tY = (y + 1 - origin.y)/dir.y;
  if(sy < 0) tY = (y - origin.y)/dir.y;
  if(sz > 0) tZ = (z + 1 - origin.z)/dir.z;
  if(sz < 0) tZ = (z - origin.z)/dir.z;

  let travelled = 0;
  let nx = 0, ny = 0, nz = 0;

  for(let i=0;i<700 && travelled<=maxDist;i++){
    if(blocks.has(key(x,y,z))){
      return {x,y,z,nx,ny,nz, dist:travelled};
    }

    if(tX <= tY && tX <= tZ){
      nx = -sx; ny = 0; nz = 0;
      x += sx;
      travelled = tX;
      tX += tDX;
    } else if(tY <= tZ){
      nx = 0; ny = -sy; nz = 0;
      y += sy;
      travelled = tY;
      tY += tDY;
    } else {
      nx = 0; ny = 0; nz = -sz;
      z += sz;
      travelled = tZ;
      tZ += tDZ;
    }
  }
  return null;
}

function collidesAt(px,py,pz){
  const eps = 0.001;
  const minX = Math.floor(px - HALF_W + eps);
  const maxX = Math.floor(px + HALF_W - eps);
  const minY = Math.floor(py - HALF_H + eps);
  const maxY = Math.floor(py + HALF_H - eps);
  const minZ = Math.floor(pz - HALF_W + eps);
  const maxZ = Math.floor(pz + HALF_W - eps);

  for(let y=minY; y<=maxY; y++){
    for(let x=minX; x<=maxX; x++){
      for(let z=minZ; z<=maxZ; z++){
        if(hasBlock(x,y,z)) return true;
      }
    }
  }
  return false;
}

function touchesGround(px,py,pz){
  const feet = py - HALF_H;
  const minX = Math.floor(px - HALF_W + 0.001);
  const maxX = Math.floor(px + HALF_W - 0.001);
  const minZ = Math.floor(pz - HALF_W + 0.001);
  const maxZ = Math.floor(pz + HALF_W - 0.001);

  const yA = Math.floor(feet - 0.04);
  const yB = Math.floor(feet - 0.01);

  for(let y=yA; y<=yB; y++){
    for(let x=minX; x<=maxX; x++){
      for(let z=minZ; z<=maxZ; z++){
        if(hasBlock(x,y,z)) return true;
      }
    }
  }
  return false;
}

function collidesPlayerWithCell(cx,cy,cz){
  const minX = px - HALF_W;
  const maxX = px + HALF_W;
  const minY = py - HALF_H;
  const maxY = py + HALF_H;
  const minZ = pz - HALF_W;
  const maxZ = pz + HALF_W;

  const cxmin = cx;
  const cxmax = cx + 1;
  const cymin = cy;
  const cymax = cy + 1;
  const czmin = cz;
  const czmax = cz + 1;

  return minX < cxmax && maxX > cxmin &&
         minY < cymax && maxY > cymin &&
         minZ < czmax && maxZ > czmin;
}

function doAction(type){
  const now = performance.now();
  if(now - lastAction < 110) return;

  const op = camPos();
  const dir = camDir();
  const hit = raycastVoxel(op, dir, 8.2);
  if(!hit) return;

  const k = key(hit.x,hit.y,hit.z);
  const t = blocks.get(k);
  if(!t) return;

  if(type==="destroy"){
    removeBlock(t,k);
  }else if(type==="place"){
    const tx = hit.x + hit.nx;
    const ty = hit.y + hit.ny;
    const tz = hit.z + hit.nz;

    if(hit.nx===0 && hit.ny===0 && hit.nz===0){
      tx = hit.x - Math.sign(dir.x);
      ty = hit.y - Math.sign(dir.y);
      tz = hit.z - Math.sign(dir.z);
    }

    if(collidesPlayerWithCell(tx,ty,tz)) return;
    addBlock(tx,ty,tz,types[selected]);
  }

  lastAction = performance.now();
  updateUI();
}

document.addEventListener("mousedown", (e) => {
  if(!locked) return;
  if(performance.now() - lockTime < 400) return;
  if(e.button === 0) doAction("destroy");
  else if(e.button === 2) doAction("place");
});

document.addEventListener("keydown", (e) => {
  if(e.repeat) return;
  keys.add(e.code);

  if(e.code==="Digit1") selected=0;
  else if(e.code==="Digit2") selected=1;
  else if(e.code==="Digit3") selected=2;
  else if(e.code==="Digit4") selected=3;
  else if(e.code==="Digit5") selected=4;
  else if(e.code==="Digit6") selected=5;
  else if(e.code==="Digit7") selected=6;
  else if(e.code==="Digit8") selected=7;

  updateUI();

  if(e.key==="Q" || e.key==="q") doAction("destroy");
  if(e.key==="E" || e.key==="e") doAction("place");
  if(e.key==="R" || e.key==="r"){
    const now = performance.now();
    if(now - lastRespawn < 300) return;
    lastRespawn = now;
    respawn();
  }
});

document.addEventListener("keyup", (e) => {
  keys.delete(e.code);
});

window.addEventListener("wheel", (e) => {
  selected = (selected + (e.deltaY > 0 ? 1 : -1) + types.length) % types.length;
  updateUI();
}, {passive:true});

function respawn(){
  px = 0.5;
  pz = 0.5;
  py = spawnTop + HALF_H + 0.5;
  vy = 0;
}

function resize(){
  renderer.setSize(window.innerWidth, window.innerHeight);
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
}
window.addEventListener("resize", resize);

let last = performance.now();

function loop(){
  const now = performance.now();
  const dt = Math.min(0.045, (now - last) / 1000);
  last = now;

  const forward =
    (keys.has("KeyW") ? 1 : 0) -
    (keys.has("KeyS") ? 1 : 0);

  const side =
    (keys.has("KeyD") ? 1 : 0) -
    (keys.has("KeyA") ? 1 : 0);

  const sprint = keys.has("ShiftLeft") || keys.has("ShiftRight") ? RUN : WALK;

  const fx = Math.sin(yaw);
  const fz = -Math.cos(yaw);
  const rx = Math.cos(yaw);
  const rz = Math.sin(yaw);

  let mx = (fx*forward + rx*side) * sprint * dt;
  let mz = (fz*forward + rz*side) * sprint * dt;

  function moveX(amount){
    if(amount === 0) return;
    const sign = amount > 0 ? 1 : -1;
    let rem = Math.abs(amount);
    while(rem > 0){
      const step = Math.min(rem, 0.08);
      const nx = px + sign*step;
      if(!collidesAt(nx,py,pz)){
        px = nx;
        rem -= step;
      }else{
        break;
      }
    }
  }

  function moveZ(amount){
    if(amount === 0) return;
    const sign = amount > 0 ? 1 : -1;
    let rem = Math.abs(amount);
    while(rem > 0){
      const step = Math.min(rem, 0.08);
      const nz = pz + sign*step;
      if(!collidesAt(px,py,nz)){
        pz = nz;
        rem -= step;
      }else{
        break;
      }
    }
  }

  function moveY(amount){
    if(amount === 0) return;
    const sign = amount > 0 ? 1 : -1;
    let rem = Math.abs(amount);
    while(rem > 0){
      const step = Math.min(rem, 0.06);
      const ny = py + sign*step;
      if(!collidesAt(px,ny,pz)){
        py = ny;
        rem -= step;
      }else{
        break;
      }
    }
  }

  if(
    (keys.has("KeyJ") || keys.has("Space")) &&
    touchesGround(px,py,pz)
  ){
    vy = JUMP;
  }

  vy -= GRAVITY * dt;

  moveX(mx);
  moveZ(mz);
  moveY(vy);

  if(touchesGround(px,py,pz)){
    if(vy < 0) vy = 0;
  }

  if(py < -25) respawn();

  camera.position.set(px,py,pz);
  camera.rotation.x = pitch;
  camera.rotation.y = yaw;

  renderer.render(scene,camera);
  requestAnimationFrame(loop);
}

renderer.render(scene,camera);
requestAnimationFrame(loop);
})();
</script>
</body>
</html>
```