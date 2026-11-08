以下は単ファイル「マイクラ風 3D box庭 game」の実例。  
開在 in browser and you play with WASD + mouse + place/remove blocks.

```html
<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Micro Box Sandbox 3D</title>

<style>
  html, body {
    margin: 0;
    padding: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
    background: #87c8ff;
  }

  canvas {
    display: block;
    width: 100%;
    height: 100%;
  }

  #ui {
    position: fixed;
    left: 12px;
    top: 12px;
    width: 360px;
    padding: 10px 12px;
    border-radius: 10px;
    background: rgba(0,0,0,0.45);
    color: white;
    font-family: sans-serif;
    font-size: 13px;
    pointer-events: none;
    z-index: 10;
  }

  #cross {
    position: fixed;
    left: calc(50% - 1px);
    top: calc(50% - 1px);
    width: 3px;
    height: 3px;
    border-radius: 3px;
    background: rgba(255,255,255,0.9);
    box-shadow:
      0 0 0 1px rgba(0,0,0,0.7),
      0 0 10px rgba(255,255,255,0.4);
    pointer-events: none;
    z-index: 20;
  }
</style>

<script src="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js"></script>
</head>

<body>
<div id="ui">
  <b>Micro 3D Box Sandbox</b><br>
  Click start / pointer lock<br>
  WASD: move<br>
  Space: jump<br>
  Shift: sprint<br>
  F: toggle flight<br>
  Space up / Shift down in flight<br>
  1..6: block select<br>
  Left click: place block<br>
  Right click: remove block<br>
  Esc / click: unlock pointer<br>
  <span id="now">Now: grass</span>
</div>

<div id="cross"></div>

<script>
(function(){
"use strict";

// ---------- Three.js scene ----------
var scene = new THREE.Scene();
scene.background = new THREE.Color(0x87c8ff);
scene.fog = new THREE.Fog(0x87c8ff, 30, 105);

var renderer = new THREE.WebGLRenderer({ antialias:true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

var camera = new THREE.PerspectiveCamera(72, window.innerWidth/window.innerHeight, 0.05, 260);
camera.rotation.order = "YXZ";
scene.add(camera);

var hemi = new THREE.HemisphereLight(0xffffff, 0x445566, 0.72);
scene.add(hemi);

var sun = new THREE.DirectionalLight(0xffffff, 0.75);
sun.position.set(1, 2, 1);
scene.add(sun);

// ---------- Block types ----------
var TYPES = [
  { name:"grass",  color:0x74bb5b },
  { name:"dirt",   color:0x8b693e },
  { name:"stone",  color:0x8f9090 },
  { name:"wood",   color:0x8a5a2c },
  { name:"leaf",   color:0x3d8a3d },
  { name:"sand",   color:0xe4d79b }
];

var nowType = 0;

// ---------- Instanced voxel renderer ----------
var boxGeo = new THREE.BoxGeometry(1, 1, 1);
var blockMat = new THREE.MeshLambertMaterial({ color:0xffffff });

var MAX_BLOCKS = 120000;
var inst = new THREE.InstancedMesh(boxGeo, blockMat, MAX_BLOCKS);
inst.count = 0;
inst.frustumCulled = false;
scene.add(inst);

var map = new Map();       // "x,y,z" -> block entry
var list = [];             // active block entries
var blockCount = 0;

var tmpObj = new THREE.Object3D();
var tmpColor = new THREE.Color();

function setBlockInstance(index, x, y, z, type){
  tmpObj.position.set(x + 0.5, y + 0.5, z + 0.5);
  tmpObj.scale.set(1,1,1);
  tmpObj.rotation.set(0,0,0);
  tmpObj.updateMatrix();
  inst.setMatrixAt(index, tmpObj.matrix);

  tmpColor.setHex(TYPES[type].color);
  inst.setColorAt(index, tmpColor);
}

function key3(x, y, z){
  return x + "," + y + "," + z;
}

function solidAt(x, y, z){
  return map.has(key3(x, y, z));
}

function addBlock(x, y, z, type){
  var k = key3(x, y, z);
  if (map.has(k)) return;

  var e = { x:x, y:y, z:z, t:type, i:blockCount };
  map.set(k, e);
  list[blockCount] = e;
  blockCount++;

  if (blockCount > inst.count) inst.count = blockCount;

  setBlockInstance(e.i, x, y, z, type);
  inst.instanceMatrix.needsUpdate = true;
  if (inst.instanceColor) inst.instanceColor.needsUpdate = true;
}

function removeBlock(x, y, z){
  var k = key3(x, y, z);
  var e = map.get(k);
  if (!e) return;

  var idx = e.i;
  var last = list[blockCount - 1];

  map.delete(k);

  if (idx < blockCount - 1){
    list[idx] = last;
    if (last) last.i = idx;
    if (last){
      setBlockInstance(idx, last.x, last.y, last.z, last.t);
    }
  }

  blockCount--;
  inst.count = blockCount;
  inst.instanceMatrix.needsUpdate = true;
  if (inst.instanceColor) inst.instanceColor.needsUpdate = true;
}

// ---------- World generation ----------
var R = 24; // square world from -R to R-1
var WORLD_HALF = R;

function hash01(x, z){
  var v = Math.sin(x * 127.1 + z * 311.7) * 43758.5453;
  return v - Math.floor(v);
}

function fbm(x, z){
  var total = 0, amp = 1, freq = 0.055;
  for (var i=0; i<5; i++){
    total += amp * hash01(x * freq, z * freq);
    amp *= 0.5;
    freq *= 2.1;
  }
  return total / 1.9375;
}

function treeHash(x, z){
  var v = Math.sin(x * 51.3 + z * 192.7) * 8123.31;
  return v - Math.floor(v);
}

function heightAt(x, z){
  var base = fbm(x, z);
  var h = 3 + Math.round(base * 11);
  return Math.max(0, Math.min(18, h));
}

function genWorld(){
  var h;
  for (var x = -WORLD_HALF; x < WORLD_HALF; x++){
    for (var z = -WORLD_HALF; z < WORLD_HALF; z++){
      h = heightAt(x, z);

      for (var y = 0; y <= h; y++){
        var t;
        if (h < 2){
          if (y === h) t = 5;
          else t = 1;
        } else {
          if (y === h) t = 0;
          else if (y >= h - 3) t = 1;
          else t = 2;
        }
        addBlock(x, y, z, t);
      }

      // sparse trees
      if (h >= 4 && (x % 7 === 0) && (z % 7 === 0) && treeHash(x, z) > 0.88){
        var base = h + 1;

        var trunkH = 3 + Math.round(treeHash(x + 1, z - 1) * 3);
        for (var ty = 0; ty < trunkH; ty++){
          addBlock(x, base + ty, z, 3);
        }

        var top = base + trunkH;

        // leaf layers
        for (var ly = -1; ly <= 0; ly++){
          for (var lx = -2; lx <= 2; lx++){
            for (var lz = -2; lz <= 2; lz++){
              var d2 = lx*lx + lz*lz + Math.abs(ly)*2;
              if (d2 <= 5) addBlock(x + lx, top + ly, z + lz, 4);
            }
          }
        }
        addBlock(x, top + 1, z, 4);
      }
    }
  }
}

genWorld();

// ---------- Player ----------
var pos = new THREE.Vector3(0, heightAt(0, 0) + 5, 0); // feet position
var vel = new THREE.Vector3(0, 0, 0);

var yaw = 0;
var pitch = 0;

var EYE = 1.6;
var HALF_W = 0.3;
var HEIGHT = 1.7;
var EPS = 0.0005;

var GRAVITY = 22;
var JUMP = 9.2;
var WALK = 5.2;
var RUN = 8.8;
var FLY_SPEED = 10;
var FLY_Y_SPEED = 7;

var grounded = false;
var flying = false;

function collideAt(px, py, pz){
  var minX = Math.floor(px - HALF_W + EPS);
  var maxX = Math.floor(px + HALF_W - EPS);
  var minY = Math.floor(py + EPS);
  var maxY = Math.floor(py + HEIGHT - EPS);
  var minZ = Math.floor(pz - HALF_W + EPS);
  var maxZ = Math.floor(pz + HALF_W - EPS);

  for (var x = minX; x <= maxX; x++){
    for (var y = minY; y <= maxY; y++){
      for (var z = minZ; z <= maxZ; z++){
        if (solidAt(x, y, z)) return true;
      }
    }
  }
  return false;
}

function blockOverlapsPlayer(x, y, z){
  return pos.x + HALF_W > x && pos.x - HALF_W < x + 1 &&
         pos.y + HEIGHT > y && pos.y < y + 1 &&
         pos.z + HALF_W > z && pos.z - HALF_W < z + 1;
}

// ---------- Input ----------
var keys = {};
var locked = false;

window.addEventListener("keydown", function(e){
  keys[e.code] = true;
  if (e.key >= "1" && e.key <= "6"){
    nowType = Math.min(5, parseInt(e.key, 10) - 1);
    updateUI();
  }
});

window.addEventListener("keyup", function(e){
  keys[e.code] = false;

  if (e.code === "KeyF"){
    var oldFlying = flying;
    // toggle on keyup only once? Better on keydown with guard:
  }
});

// Toggle flight with repeated key handling.
var flyToggleDone = false;
window.addEventListener("keydown", function(e){
  if (e.code === "KeyF" && !flyToggleDone){
    flying = !flying;
    grounded = true;
    flyToggleDone = true;
    updateUI();
  }
});
window.addEventListener("keyup", function(e){
  if (e.code === "KeyF") flyToggleDone = false;
});

// Pointer lock and mouse actions
renderer.domElement.addEventListener("contextmenu", function(ev){
  if (locked) ev.preventDefault();
});

renderer.domElement.addEventListener("mousedown", function(ev){
  var button = ev.button; // 0 left, 2 right

  if (button === 2){
    if (locked){
      var hit = raycastVoxel();
      if (hit){
        removeBlock(hit.x, hit.y, hit.z);
      }
    }
    return;
  }

  if (button === 0){
    if (!locked){
      renderer.domElement.requestPointerLock();
      // pointerlockchange event will set locked.
    } else {
      var hit = raycastVoxel();
      if (hit){
        var px = hit.x - hit.nx;
        var py = hit.y - hit.ny;
        var pz = hit.z - hit.nz;

        if (!blockOverlapsPlayer(px, py, pz)){
          addBlock(px, py, pz, nowType);
        }
      }
    }
  }
});

document.addEventListener("pointerlockchange", function(){
  locked = (document.pointerLockElement === renderer.domElement);
});

document.addEventListener("mousemove", function(ev){
  if (!locked) return;
  yaw   -= ev.movementX * 0.0023;
  pitch -= ev.movementY * 0.0023;
  pitch = Math.max(-1.45, Math.min(1.45, pitch));
});

// ---------- Ray / cursor target ----------
const RAY_RANGE = 8.0;

function raycastVoxel(){
  var ox = camera.position.x;
  var oy = camera.position.y;
  var oz = camera.position.z;

  var dir = new THREE.Vector3(0, 0, -1).applyQuaternion(camera.quaternion);
  var dx = dir.x, dy = dir.y, dz = dir.z;

  var ix = Math.floor(ox), iy = Math.floor(oy), iz = Math.floor(oz);

  var sx = dx > 0 ? 1 : dx < 0 ? -1 : 0;
  var sy = dy > 0 ? 1 : dy < 0 ? -1 : 0;
  var sz = dz > 0 ? 1 : dz < 0 ? -1 : 0;

  var tMaxX = sx === 0 ? Infinity : ((sx > 0 ? ix + 1 : ix) - ox) / dx;
  var tMaxY = sy === 0 ? Infinity : ((sy > 0 ? iy + 1 : iy) - oy) / dy;
  var tMaxZ = sz === 0 ? Infinity : ((sz > 0 ? iz + 1 : iz) - oz) / dz;

  var tDeltaX = sx === 0 ? Infinity : Math.abs(1 / dx);
  var tDeltaY = sy === 0 ? Infinity : Math.abs(1 / dy);
  var tDeltaZ = sz === 0 ? Infinity : Math.abs(1 / dz);

  var nx = 0, ny = 0, nz = 0;

  while (true){
    if (solidAt(ix, iy, iz)){
      // If camera is inside a block, face normal is roughly opposite view.
      if (nx === 0 && ny === 0 && nz === 0){
        if (Math.abs(dx) >= Math.abs(dy) && Math.abs(dx) >= Math.abs(dz)){
          nx = -Math.sign(dx) || 1;
        } else if (Math.abs(dy) >= Math.abs(dz)){
          ny = -Math.sign(dy) || 1;
        } else {
          nz = -Math.sign(dz) || 1;
        }
      }
      return { x:ix, y:iy, z:iz, nx:nx, ny:ny, nz:nz };
    }

    var t = Math.min(tMaxX, Math.min(tMaxY, tMaxZ));
    if (!isFinite(t) || t > RAY_RANGE) return null;

    if (tMaxX <= tMaxY && tMaxX <= tMaxZ){
      ix += sx;
      tMaxX += tDeltaX;
      nx = -sx; ny = 0; nz = 0;
    } else if (tMaxY <= tMaxZ){
      iy += sy;
      tMaxY += tDeltaY;
      nx = 0; ny = -sy; nz = 0;
    } else {
      iz += sz;
      tMaxZ += tDeltaZ;
      nx = 0; ny = 0; nz = -sz;
    }
  }
}

// Cursor highlight
var hiGeo = new THREE.BoxGeometry(1.03, 1.03, 1.03);
var hiMat = new THREE.MeshBasicMaterial({ color:0xffffff, wireframe:true, transparent:true, opacity:0.75 });
var highlight = new THREE.Mesh(hiGeo, hiMat);
scene.add(highlight);

// ---------- UI ----------
var nowSpan = document.getElementById("now");
function updateUI(){
  var flyText = flying ? "FLIGHT" : "WALK";
  var t = TYPES[nowType].name;
  nowSpan.textContent = "Now: " + t + " / Mode: " + flyText;
}
updateUI();

// ---------- Movement ----------
function getForward(){
  var q = camera.quaternion;
  var v = new THREE.Vector3(0, 0, -1);
  v.applyQuaternion(q);
  v.y = 0;
  if (v.lengthSq() < 0.0001) return new THREE.Vector3(0, 0, 1);
  return v.normalize();
}

function getRight(){
  var f = getForward();
  var r = new THREE.Vector3(f.z, 0, -f.x).normalize();
  return r;
}

function moveHorizontal(amountX, amountZ){
  if (amountX === 0 && amountZ === 0) return;

  var startX = pos.x, startZ = pos.z;

  // X axis
  var targetX = startX + amountX;
  if (!collideAt(targetX, pos.y, pos.z)){
    pos.x = targetX;
  } else {
    // binary search along X
    var lo = startX, hi = targetX;
    for (var i=0; i<16; i++){
      var mid = (lo + hi) * 0.5;
      if (!collideAt(mid, pos.y, pos.z)) lo = mid;
      else hi = mid;
    }
    pos.x = lo;
  }

  // Z axis
  var targetZ = pos.z + amountZ;
  if (!collideAt(pos.x, pos.y, targetZ)){
    pos.z = targetZ;
  } else {
    var loZ = pos.z, hiZ = targetZ;
    for (var j=0; j<16; j++){
      var midZ = (loZ + hiZ) * 0.5;
      if (!collideAt(pos.x, pos.y, midZ)) loZ = midZ;
      else hiZ = midZ;
    }
    pos.z = loZ;
  }
}

function moveVertical(amountY){
  if (amountY === 0) return;

  if (flying){
    // In flight, move freely and stop only if inside block.
    var y = pos.y + amountY;
    if (!collideAt(pos.x, y, pos.z)){
      pos.y = y;
    }
    return;
  }

  // Walking/jumping: sweep Y.
  var lo = pos.y, hi = pos.y + amountY;
  if (collideAt(pos.x, hi, pos.z)){
    // Binary search toward hi, but keep current pos.y as safe if possible.
    if (amountY > 0){
      // moving up
      var a = pos.y, b = hi;
      for (var i=0; i<18; i++){
        var m = (a + b) * 0.5;
        if (!collideAt(pos.x, m, pos.z)) a = m;
        else b = m;
      }
      pos.y = a;
    } else {
      // falling
      var a = pos.y, b = hi;
      for (var j=0; j<18; j++){
        var mid = (a + b) * 0.5;
        if (!collideAt(pos.x, mid, pos.z)) a = mid;
        else b = mid;
      }
      pos.y = a;
      grounded = true;
    }
  } else {
    pos.y = hi;
    grounded = false;
  }
}

function updateGround(){
  // A small downward probe to decide grounded.
  var probe = pos.clone();
  probe.y -= 0.03;
  grounded = flying ? true : collideAt(pos.x, probe.y, pos.z);
}

// ---------- Main loop ----------
var lastTime = performance.now();

function update(){
  var now = performance.now();
  var dt = Math.min(0.033, (now - lastTime) / 1000);
  lastTime = now;

  var moveF = (keys["KeyW"] ? 1 : 0) - (keys["KeyB"] ? 1 : 0);
  var moveR = (keys["KeyD"] ? 1 : 0) - (keys["KeyA"] ? 1 : 0);

  if (flying){
    vel.x = 0;
    vel.z = 0;
    vel.y = 0;

    var f = getForward();
    var r = getRight();

    var mx = f.x * moveF + r.x * moveR;
    var mz = f.z * moveF + r.z * moveR;
    var mlen = Math.hypot(mx, mz);
    if (mlen > 0){
      mx /= mlen;
      mz /= mlen;
    }

    var speed = FLY_SPEED;
    if (keys["ShiftLeft"] || keys["ShiftRight"]){
      speed = FLY_SPEED * 1.35;
    }

    moveHorizontal(mx * speed * dt, mz * speed * dt);

    if (keys["Space"]) moveVertical(FLY_Y_SPEED * dt);
    if (keys["ShiftLeft"] || keys["ShiftRight"]){
      // Shift is sprint in walking mode; in flight use it too for down.
      if (!keys["ShiftLeft"] && !keys["ShiftRight"]) {}
      moveVertical(-FLY_Y_SPEED * dt);
    }
  } else {
    // walking physics
    var f = getForward();
    var r = getRight();

    var mx = f.x * moveF + r.x * moveR;
    var mz = f.z * moveF + r.z * moveR;
    var mlen = Math.hypot(mx, mz);
    if (mlen > 0){
      mx /= mlen;
      mz /= mlen;
    }

    var speed = WALK;
    if (keys["ShiftLeft"] || keys["ShiftRight"]) speed = RUN;

    // ground snap update
    updateGround();

    // jump
    if (grounded && keys["Space"] && vel.y >= -0.1){
      vel.y = JUMP;
    }

    // gravity
    if (!grounded){
      vel.y -= GRAVITY * dt;
      if (vel.y < -220) vel.y = -220;
    } else if (vel.y < 0){
      vel.y = 0;
    }

    moveHorizontal(mx * speed * dt, mz * speed * dt);

    // apply vertical velocity as a small substep to reduce tunneling
    var yStep = vel.y * dt;
    if (Math.abs(yStep) > 0.25){
      // split step
      var steps = Math.ceil(Math.abs(yStep) / 0.12);
      var single = yStep / steps;
      for (var s=0; s<steps; s++) moveVertical(single);
    } else {
      moveVertical(yStep);
    }

    updateGround();
  }

  // respawn
  if (pos.y < -18){
    pos.set(0, heightAt(0, 0) + 5, 0);
    vel.set(0, 0, 0);
    yaw = 0;
    pitch = 0;
  }

  camera.position.set(pos.x, pos.y + EYE, pos.z);
  camera.rotation.x = pitch;
  camera.rotation.y = yaw;
  camera.rotation.z = 0;
  camera.updateMatrixWorld();

  var hit = raycastVoxel();
  if (hit){
    highlight.visible = true;
    highlight.position.set(hit.x + 0.5, hit.y + 0.5, hit.z + 0.5);
  } else {
    highlight.visible = false;
  }
}

function renderLoop(){
  update();
  renderer.render(scene, camera);
}

window.addEventListener("resize", function(){
  renderer.setSize(window.innerWidth, window.innerHeight);
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
});

function startGameLoop(){
  requestAnimationFrame(startGameLoop);
  renderLoop();
}
startGameLoop();

// Optional: make right-click prevent menu while locked
document.addEventListener("contextmenu", function(ev){
  if (locked) ev.preventDefault();
});

})();
</script>
</body>
</html>
```

How to run:
- Save as `sandbox.html`
- Open in browser: Chrome / Edge / Firefox etc.
- Click once to enter pointer lock.
- If your browser blocks pointer lock, try full-screen non-iframe browser window.

Controls:
- `WASD` move
- `Space` jump
- `Shift` sprint / descend in flight
- `F` toggle flight
- `1..6` select block
- `left click` place block
- `right click` remove block

Notes:
- Uses `Three.js` from CDN.
- World is a simple voxel terrain generated procedurally.
- The code is self-contained and expandable to bigger worlds/chunks later.