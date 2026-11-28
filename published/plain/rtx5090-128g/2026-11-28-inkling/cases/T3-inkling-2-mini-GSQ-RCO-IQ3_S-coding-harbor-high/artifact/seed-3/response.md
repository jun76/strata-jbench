Here's a complete single-file voxel diorama — a tall ship moored at a wooden pier with a lighthouse, warehouses, cottages, crates, a crane, buoys, gulls and drifting clouds. Open it in Chrome (it loads Three.js from a CDN, so you need internet the first time).

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>A Sailing Ship Calling at a Harbor — Voxel Scene</title>
<style>
  html,body{margin:0;height:100%;overflow:hidden}
  body{font-family:Georgia,'Times New Roman',serif;background:#3e7ca6}
  canvas{display:block}
  .vignette{position:fixed;inset:0;pointer-events:none;
    background:radial-gradient(ellipse at center, transparent 55%, rgba(10,20,30,.38) 100%)}
  #ui{position:fixed;top:18px;left:18px;max-width:330px;z-index:10;
    background:rgba(12,22,30,.55);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);
    border:1px solid rgba(255,255,255,.18);border-radius:16px;padding:16px 20px;color:#f5ead6;
    box-shadow:0 8px 30px rgba(0,0,0,.25)}
  #ui h1{font-size:18px;margin:0 0 6px;letter-spacing:.4px;font-weight:600}
  #ui p{margin:0 0 12px;font-size:12px;line-height:1.55;opacity:.85}
  .btnrow{display:flex;gap:8px}
  button{flex:1;cursor:pointer;border:1px solid rgba(255,255,255,.25);background:rgba(255,255,255,.1);
    color:#f5ead6;padding:7px 10px;border-radius:9px;font-size:11px;letter-spacing:.3px;transition:background .2s}
  button:hover{background:rgba(255,255,255,.22)}
  #hint{position:fixed;bottom:16px;left:18px;z-index:10;color:rgba(245,234,214,.92);font-size:11px;
    letter-spacing:.4px;background:rgba(12,22,30,.4);padding:7px 12px;border-radius:9px;
    border:1px solid rgba(255,255,255,.12);backdrop-filter:blur(8px)}
  #err{display:none;position:fixed;bottom:16px;right:18px;z-index:20;max-width:320px;font-size:12px;
    color:#ffd9a0;background:rgba(40,20,10,.75);border:1px solid rgba(255,200,120,.35);
    padding:10px 14px;border-radius:10px}
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
<div id="ui">
  <h1>⛵ A Sailing Ship Calling at a Harbor</h1>
  <p>Voxel diorama of a tall ship moored at the pier — lighthouse, warehouse, cottages, crates, crane, buoys and gulls.</p>
  <div class="btnrow">
    <button id="autoBtn">⟳ Auto-orbit</button>
    <button id="resetBtn">Reset view</button>
  </div>
</div>
<div id="hint">Drag — orbit &nbsp;·&nbsp; Scroll — zoom &nbsp;·&nbsp; Right-drag — pan</div>
<div id="err"></div>
<div class="vignette"></div>

<script>
window.addEventListener('error', function(e){
  var d = document.getElementById('err');
  if (d){ d.style.display='block'; d.textContent = '⚠ ' + (e.message || 'Script failed') + ' — check internet connection (Three.js CDN).'; }
});

if (typeof THREE === 'undefined' || typeof THREE.OrbitControls === 'undefined'){
  var err = document.getElementById('err');
  err.style.display='block';
  err.textContent = '⚠ Three.js could not be loaded. Check your internet connection, then reload.';
} else {
  init();
}

function makeSkyTexture(){
  var c = document.createElement('canvas'); c.width = 4; c.height = 256;
  var g = c.getContext('2d');
  var grad = g.createLinearGradient(0,0,0,256);
  grad.addColorStop(0, '#3e7ca6');
  grad.addColorStop(0.45, '#82bcd4');
  grad.addColorStop(0.75, '#d8e2d8');
  grad.addColorStop(1, '#f3d9a4');
  g.fillStyle = grad; g.fillRect(0,0,4,256);
  var tex = new THREE.CanvasTexture(c);
  tex.encoding = THREE.sRGBEncoding;
  return tex;
}

function stdMat(color, rough){
  var m = new THREE.MeshStandardMaterial({roughness: rough===undefined?0.92:rough, metalness:0.02});
  m.color.set(color).convertSRGBToLinear();
  return m;
}

function cell(x,y,z,color,s,sy,sz){
  var ss = (s===undefined)?1:s;
  return {x:x,y:y,z:z,color:color,s:ss,sy:(sy===undefined?ss:sy),sz:(sz===undefined?ss:sz)};
}

function addRow(arr,x,y,z0,z1,color){
  for(var z=z0;z<z1;z++) arr.push(cell(x,y+0.5,z+0.5,color));
}

function addRoofRow(arr,x0,x1,y,zCenter,zWidth,color){
  for(var x=x0;x<x1;x++)
    for(var i=0;i<zWidth;i++)
      arr.push(cell(x+0.5, y+0.5, zCenter - zWidth/2 + i + 0.5, color));
}

function makeInstanced(cells){
  var geo = new THREE.BoxGeometry(1,1,1);
  var mat = new THREE.MeshStandardMaterial({color:0xffffff, roughness:0.92, metalness:0.02});
  var m = new THREE.InstancedMesh(geo, mat, cells.length);
  var M=new THREE.Matrix4(), Q=new THREE.Quaternion(), P=new THREE.Vector3(), S=new THREE.Vector3(), C=new THREE.Color();
  cells.forEach(function(c,i){
    P.set(c.x,c.y,c.z); S.set(c.s,c.sy,c.sz);
    M.compose(P,Q,S); m.setMatrixAt(i,M);
    C.set(c.color).convertSRGBToLinear(); m.setColorAt(i,C);
  });
  m.instanceMatrix.needsUpdate = true;
  if (m.instanceColor) m.instanceColor.needsUpdate = true;
  m.castShadow = true; m.receiveShadow = true; m.frustumCulled = false;
  return m;
}

function bigBox(w,h,d,x,y,z,color){
  var mesh = new THREE.Mesh(new THREE.BoxGeometry(w,h,d), stdMat(color,0.95));
  mesh.position.set(x,y,z); mesh.receiveShadow = true;
  sceneRef.add(mesh);
}

function init(){
  var sceneRef = new THREE.Scene();
  sceneGlobal = sceneRef;
  window.__sceneRef = sceneRef;

  // ---------- renderer ----------
  var renderer = new THREE.WebGLRenderer({antialias:true});
  renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.outputEncoding = THREE.sRGBEncoding;
  document.body.appendChild(renderer.domElement);

  // ---------- scene / camera ----------
  var scene = sceneRef;
  scene.background = makeSkyTexture();
  scene.fog = new THREE.Fog(0xe6d9b8, 60, 175);

  var camera = new THREE.PerspectiveCamera(48, window.innerWidth/window.innerHeight, 0.1, 500);
  camera.position.set(26, 17, 32);

  var controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.target.set(6, 3, -2);
  controls.enableDamping = true;
  controls.dampingFactor = 0.06;
  controls.minDistance = 12;
  controls.maxDistance = 95;
  controls.maxPolarAngle = Math.PI/2 - 0.07;
  controls.autoRotateSpeed = 0.7;

  // ---------- lights ----------
  scene.add(new THREE.HemisphereLight(0xbfd9e8, 0x8a6f4d, 0.8));
  var sun = new THREE.DirectionalLight(0xfff2dd, 1.2);
  sun.position.set(36, 46, 20);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  sun.shadow.camera.left = -55; sun.shadow.camera.right = 55;
  sun.shadow.camera.top = 55;  sun.shadow.camera.bottom = -55;
  sun.shadow.camera.near = 5;  sun.shadow.camera.far = 160;
  sun.shadow.bias = -0.0005;   sun.shadow.normalBias = 0.4;
  sun.target.position.set(0, 0, -8);
  scene.add(sun.target); scene.add(sun);

  var lanternLight = new THREE.PointLight(0xffdf8a, 0.9, 34, 2);
  lanternLight.position.set(15, 9.2, -12);
  scene.add(lanternLight);

  // ---------- ground ----------
  bigBox(80, 2, 27, 0, -0.5, -26.5, '#5e9448');   // grass
  bigBox(80, 1.5, 3, 0, -0.25, -11.5, '#e3cf9b');  // sand

  // ---------- world voxels ----------
  var W = [];

  // pier
  for (var z=-10; z<=5; z++){
    var plank = (z%2===0) ? '#b9835a' : '#a9743f';
    for (var x=0; x<4; x++) W.push(cell(x+0.5, 1.5, z+0.5, plank));
  }
  for (var z=-9; z<=5; z+=4){
    W.push(cell(0.5,-0.5,z+0.5,'#4a2e1e')); W.push(cell(0.5,0.5,z+0.5,'#4a2e1e'));
    W.push(cell(3.5,-0.5,z+0.5,'#4a2e1e')); W.push(cell(3.5,0.5,z+0.5,'#4a2e1e'));
  }
  // lamp post
  W.push(cell(0.5,2.5,4.5,'#2c2f35')); W.push(cell(0.5,3.5,4.5,'#2c2f35'));
  W.push(cell(0.5,4.2,4.5,'#ffe9a8',0.7));
  // crates & barrel
  W.push(cell(2.5,2.5,2.5,'#7a4a2b')); W.push(cell(2.5,3.5,2.5,'#8a5a35'));
  W.push(cell(2.5,2.5,3.5,'#96683a')); W.push(cell(1.5,2.5,3.5,'#96683a',0.8));
  // crane
  W.push(cell(3.5,2.5,4.5,'#8a3324')); W.push(cell(3.5,3.5,4.5,'#8a3324')); W.push(cell(3.5,4.5,4.5,'#8a3324'));
  W.push(cell(3.5,5.2,5.5,'#8a3324',0.8)); W.push(cell(3.5,4.85,6.3,'#8a3324',0.7)); W.push(cell(3.5,4.5,7.1,'#8a3324',0.6));
  W.push(cell(3.5,3.8,7.1,'#2c2f35',0.45));
  // warehouse
  var winX = [-17,-14,-11];
  for (var x=-19; x<-9; x++) for (var z=-23; z<-17; z++){
    var col = '#d9c9a8';
    if (y1Window(x,z,winX)) col = '#ffe9a8';
    if (x===-14 && z===-18 && yRow(1)) col = '#4a2e1e'; // placeholder no-op
    W.push(cell(x+0.5, 0.5, z+0.5, (x===-14 && z===-18) ? '#4a2e1e' : col));
    W.push(cell(x+0.5, 1.5, z+0.5, (z===-18 && winX.indexOf(x)>=0) ? '#ffe9a8' : col));
  }
  addRoofRow(W,-19,-9,2,-20,5,'#a0402f');
  addRoofRow(W,-19,-9,3,-20,4,'#a0402f');
  addRoofRow(W,-19,-9,4,-20,3,'#8a3324');
  addRoofRow(W,-19,-9,5,-20,2,'#8a3324');
  W.push(cell(-16.5,6.5,-20.5,'#8a5a35',0.9));
  // cottages
  for (var x=-26; x<-22; x++) for (var z=-24; z<-20; z++){
    var c0 = '#e0d3b4';
    if (x===-24 && z===-21) c0 = '#4a2e1e';
    if (x===-23 && z===-21) c0 = '#ffe9a8';
    W.push(cell(x+0.5,0.5,z+0.5,c0));
    W.push(cell(x+0.5,1.5,z+0.5,(x===-23 && z===-21)?'#ffe9a8':'#e0d3b4'));
  }
  addRoofRow(W,-26,-22,2,-22,3,'#b04a32');
  addRoofRow(W,-26,-22,3,-22,2,'#b04a32');
  for (var x=-4; x<-1; x++) for (var z=-28; z<-24; z++){
    var c0 = '#d8c6a0';
    if (x===-2 && z===-25) c0 = '#4a2e1e';
    W.push(cell(x+0.5,0.5,z+0.5,c0));
    W.push(cell(x+0.5,1.5,z+0.5,(x===-3 && z===-25)?'#ffe9a8':'#d8c6a0'));
  }
  addRoofRow(W,-4,-1,2,-26,3,'#7a4a2b');
  addRoofRow(W,-4,-1,3,-26,2,'#7a4a2b');
  // lighthouse
  var towerRows = [
    {y:0,w:5,c:'#f5f0e6'},{y:1,w:5,c:'#f5f0e6'},
    {y:2,w:4,c:'#c0392b'},{y:3,w:4,c:'#c0392b'},
    {y:4,w:3,c:'#f5f0e6'},{y:5,w:3,c:'#f5f0e6'},
    {y:6,w:2,c:'#c0392b'},{y:7,w:2,c:'#f5f0e6'}
  ];
  towerRows.forEach(function(r){
    var start = -r.w/2;
    for (var i=0;i<r.w;i++) for (var j=0;j<r.w;j++){
      var col = r.c;
      if (r.y===4 && j===r.w-1 && i===Math.floor(r.w/2)) col = '#ffe9a8';
      W.push(cell(15 + start + i + 0.5, r.y+0.5, -12 + start + j + 0.5, col));
    }
  });
  for (var i=0;i<2;i++) for (var j=0;j<2;j++)
    W.push(cell(15 - 1 + i + 0.5, 8.5, -12 - 1 + j + 0.5, '#ffe9a8'));
  for (var i=0;i<2;i++) for (var j=0;j<2;j++)
    W.push(cell(15 - 1 + i + 0.5, 9.5, -12 - 1 + j + 0.5, '#c0392b'));
  W.push(cell(15, 10.5, -12, '#8a3324'));
  // bushes & rocks
  W.push(cell(-30,1.0,-15,'#4e8a3f',0.9)); W.push(cell(-8,1.0,-20,'#4e8a3f',0.9));
  W.push(cell(8,1.0,-22,'#5e9448',0.9));  W.push(cell(24,1.0,-18,'#4e8a3f',0.9));
  W.push(cell(20,1.0,-28,'#4e8a3f',0.9));
  W.push(cell(-8.5,0.7,-11.5,'#9a958c',0.8)); W.push(cell(7.5,0.7,-11.5,'#9a958c',0.7));
  // gangplank
  W.push(cell(4.5,2.1,0.5,'#b9835a',0.9)); W.push(cell(5.5,2.1,0.5,'#b9835a',0.9)); W.push(cell(6.5,2.1,0.5,'#b9835a',0.9));
  // foam around hull
  for (var z=-3; z<=6; z++){
    W.push(cell(6.4,-0.05,z+0.5,'#d8eef2',1,0.3,1));
    W.push(cell(11.6,-0.05,z+0.5,'#d8eef2',1,0.3,1));
  }
  for (var i=0;i<4;i++) W.push(cell(7.5+i,-0.05,6.7,'#d8eef2',0.9,0.3,0.9));

  var worldMesh = makeInstanced(W);
  scene.add(worldMesh);

  // crane hook line
  var hookGeo = new THREE.BufferGeometry();
  hookGeo.setAttribute('position', new THREE.BufferAttribute(new Float32Array([3.5,4.4,7.1, 3.5,3.95,7.1]),3));
  scene.add(new THREE.LineSegments(hookGeo, new THREE.LineBasicMaterial({color:0x2c2f35})));

  // ---------- water ----------
  var waterCells = [];
  var k = 0;
  for (var wx=-40; wx<=40; wx+=1.5) for (var wz=-10; wz<=40; wz+=1.5){
    var alt = (Math.round(wx/1.5)+Math.round(wz/1.5))%2===0;
    var c = alt ? '#2b6f8f' : '#35829f';
    if (k%37===0) c = '#5fa8bf';
    waterCells.push({x:wx,z:wz,c:c}); k++;
  }
  var waterGeo = new THREE.BoxGeometry(1.42,0.35,1.42);
  var waterMat = new THREE.MeshStandardMaterial({roughness:0.5, metalness:0.08, color:0xffffff});
  var water = new THREE.InstancedMesh(waterGeo, waterMat, waterCells.length);
  var C2 = new THREE.Color();
  waterCells.forEach(function(c,i){ C2.set(c.c).convertSRGBToLinear(); water.setColorAt(i,C2); });
  water.instanceColor.needsUpdate = true;
  water.receiveShadow = true; water.castShadow = false; water.frustumCulled = false;
  scene.add(water);

  // ---------- ship ----------
  var S = [];
  var x,y,z,col;
  for (x=-3;x<4;x++) for (z=-1;z<1;z++) S.push(cell(x+0.5,0.5,z+0.5,'#3d2a1c'));
  for (x=-4;x<4;x++) for (z=-2;z<2;z++) S.push(cell(x+0.5,1.5,z+0.5,'#3d2a1c'));
  for (x=-4;x<4;x++) for (z=-2;z<2;z++) S.push(cell(x+0.5,2.5,z+0.5,'#b03a2e'));
  for (x=4;x<5;x++) for (z=-1;z<1;z++){
    S.push(cell(x+0.5,1.5,z+0.5,'#3d2a1c'));
    S.push(cell(x+0.5,2.5,z+0.5,'#b03a2e'));
  }
  for (x=-4;x<4;x++) for (z=-2;z<2;z++){
    col = (z===-2||z===1) ? '#5d3a22' : '#b9835a';
    S.push(cell(x+0.5,3.5,z+0.5,col));
  }
  for (z=-1;z<1;z++) S.push(cell(4.5,3.5,z+0.5,'#5d3a22'));
  for (x=-4;x<-1;x++) for (z=-2;z<2;z++){
    col = (x===-4 && z>=-1 && z<=1) ? '#ffe9a8' : '#a9743f';
    S.push(cell(x+0.5,4.5,z+0.5,col));
  }
  for (x=-4;x<-2;x++) for (z=-1;z<1;z++) S.push(cell(x+0.5,5.5,z+0.5,'#8a5a35'));
  S.push(cell(-2.5,6.35,0,'#ffe9a8',0.8));
  for (y=4;y<=9;y++) S.push(cell(0.5,y+0.5,0,'#6b4226',0.65));
  for (y=4;y<=7;y++) S.push(cell(3.5,y+0.5,0,'#6b4226',0.65));
  var sc1='#f6ead2', sc2='#e9d9b4';
  addRow(S,0.5,4,-2,2,sc1); addRow(S,0.5,5,-2,2,sc2);
  addRow(S,0.5,6,-1.5,1.5,sc1); addRow(S,0.5,7,-1.5,1.5,sc2);
  addRow(S,0.5,8,-1,1,sc1);
  addRow(S,3.5,4,-1.5,1.5,sc1); addRow(S,3.5,5,-1.5,1.5,sc2);
  addRow(S,3.5,6,-1,1,sc1); addRow(S,3.5,7,-0.5,0.5,sc2);
  S.push(cell(5.6,3.6,0,'#6b4226',0.7));
  S.push(cell(6.4,3.95,0,'#6b4226',0.65));
  S.push(cell(7.2,4.3,0,'#6b4226',0.6));
  S.push(cell(1.5,4.4,0,'#5d3a22',0.9));
  S.push(cell(-1.5,4.4,1.3,'#96683a',0.7));
  S.push(cell(-2.5,4.4,1.3,'#7a4a2b',0.7));
  S.push(cell(2.5,4.3,-1.4,'#26221f',0.6));

  var shipGroup = new THREE.Group();
  shipGroup.add(makeInstanced(S));
  shipGroup.position.set(9,-0.5,1);
  shipGroup.rotation.y = -Math.PI/2 + 0.1;
  scene.add(shipGroup);

  // rigging
  var rigGeo = new THREE.BufferGeometry();
  var rigPts = new Float32Array([
    0.5,9.9,0, 7.2,4.3,0,
    0.5,9.9,0, -3.0,6.1,0,
    3.5,7.9,0, 7.2,4.3,0,
    3.5,7.9,0, 0.5,9.9,0
  ]);
  rigGeo.setAttribute('position', new THREE.BufferAttribute(rigPts,3));
  shipGroup.add(new THREE.LineSegments(rigGeo, new THREE.LineBasicMaterial({color:0x2c1e13})));

  // flag
  var flagGroup = new THREE.Group();
  flagGroup.position.set(0.5, 10.15, 0);
  var penn = new THREE.Mesh(new THREE.BoxGeometry(1.7,0.5,0.14), stdMat('#c0392b',0.8));
  penn.position.set(-0.9,0,0); penn.castShadow = true;
  var tip = new THREE.Mesh(new THREE.BoxGeometry(0.3,0.45,0.14), stdMat('#f6ead2',0.8));
  tip.position.set(-1.85,0,0); tip.castShadow = true;
  flagGroup.add(penn); flagGroup.add(tip);
  shipGroup.add(flagGroup);

  // ---------- lighthouse beam ----------
  var beamGeo = new THREE.ConeGeometry(1.6, 9, 12, 1, true);
  beamGeo.translate(0,-4.5,0); beamGeo.rotateZ(Math.PI/2);
  var beamMat = new THREE.MeshBasicMaterial({color:0xffe9a8, transparent:true, opacity:0.15,
    side:THREE.DoubleSide, depthWrite:false, blending:THREE.AdditiveBlending});
  var beamGroup = new THREE.Group();
  beamGroup.position.set(15, 8.5, -12);
  beamGroup.add(new THREE.Mesh(beamGeo, beamMat));
  scene.add(beamGroup);

  // ---------- clouds ----------
  var clouds = [];
  function makeCloud(x,y,z,s,v){
    var g = new THREE.Group();
    var mat = stdMat('#f7f4ec',1.0);
    [[3.2,1.2,1.9,0,0,0],[1.9,1.3,1.6,0.9,0.65,0.2],[1.4,1.0,1.4,-1.2,0.55,0.3],[1.7,0.85,1.2,0.2,0.95,-0.2]].forEach(function(p){
      var m = new THREE.Mesh(new THREE.BoxGeometry(p[0],p[1],p[2]), mat);
      m.position.set(p[3],p[4],p[5]); g.add(m);
    });
    g.scale.set(s,s,s); g.position.set(x,y,z);
    scene.add(g); clouds.push({g:g,v:v});
  }
  makeCloud(-18,17,-18,1.2,0.9); makeCloud(10,20,-8,1.5,0.6);
  makeCloud(30,16,12,1.0,1.1);   makeCloud(-32,19,8,1.3,0.8);

  // ---------- gulls ----------
  var wingGeoL = new THREE.BoxGeometry(1.15,0.09,0.34); wingGeoL.translate(0.575,0,0);
  var wingGeoR = new THREE.BoxGeometry(1.15,0.09,0.34); wingGeoR.translate(-0.575,0,0);
  var gullMat = stdMat('#2b3038',0.9);
  var gulls = [];
  function makeGull(off){
    var g = new THREE.Group();
    var body = new THREE.Mesh(new THREE.BoxGeometry(0.3,0.18,0.8), gullMat);
    var wl = new THREE.Mesh(wingGeoL, gullMat);
    var wr = new THREE.Mesh(wingGeoR, gullMat);
    g.add(body); g.add(wl); g.add(wr); scene.add(g);
    gulls.push({g:g, wl:wl, wr:wr, off:off});
  }
  makeGull(0); makeGull(2.1); makeGull(4.2);

  // ---------- buoys ----------
  var buoys = [];
  function makeBuoy(x,z){
    var g = new THREE.Group();
    var base = new THREE.Mesh(new THREE.BoxGeometry(0.75,0.55,0.75), stdMat('#c0392b'));
    var mid = new THREE.Mesh(new THREE.BoxGeometry(0.5,0.35,0.5), stdMat('#f5f0e6'));
    var top = new THREE.Mesh(new THREE.BoxGeometry(0.3,0.45,0.3), stdMat('#c0392b'));
    base.position.y=0.2; mid.position.y=0.65; top.position.y=1.0;
    base.castShadow = true;
    g.add(base); g.add(mid); g.add(top);
    g.position.set(x,0,z); scene.add(g);
    buoys.push({g:g,x:x,z:z});
  }
  makeBuoy(14.5,7.5); makeBuoy(-5.5,5.5); makeBuoy(19.5,-4.5);

  // ---------- rowboat ----------
  var boat = new THREE.Group();
  function boatCell(sx,sy,sz,x,y,z,color){
    var m = new THREE.Mesh(new THREE.BoxGeometry(sx,sy,sz), stdMat(color));
    m.position.set(x,y,z); m.castShadow = true; boat.add(m);
  }
  for (var i=-2;i<2;i++) boatCell(1,0.5,1, i+0.5,0.4,0,'#3d2a1c');
  for (var i=-2;i<2;i++) boatCell(1.15,0.5,1.05, i+0.5,0.85,0,'#8a5a35');
  for (var i=-2;i<2;i++) boatCell(1.0,0.4,0.9, i+0.5,1.2,0,'#c89b6a');
  var oar = new THREE.Mesh(new THREE.BoxGeometry(0.18,0.12,2.1), stdMat('#6b4226'));
  oar.position.set(0.3,1.45,0); oar.rotation.z = 0.28; oar.castShadow = true; boat.add(oar);
  boat.position.set(13.6, 0, 3.2);
  boat.rotation.y = -Math.PI/2 + 0.22;
  scene.add(boat);

  // ---------- UI ----------
  var autoBtn = document.getElementById('autoBtn');
  autoBtn.addEventListener('click', function(){
    controls.autoRotate = !controls.autoRotate;
    autoBtn.textContent = controls.autoRotate ? '⏸ Auto-orbit' : '⟳ Auto-orbit';
  });
  document.getElementById('resetBtn').addEventListener('click', function(){
    camera.position.set(26,17,32);
    controls.target.set(6,3,-2);
  });

  // ---------- resize ----------
  window.addEventListener('resize', function(){
    camera.aspect = window.innerWidth/window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

  // ---------- animate ----------
  var clock = new THREE.Clock();
  var elapsed = 0;
  var M = new THREE.Matrix4();

  function waveAt(x,z,t){
    return -0.2 + Math.sin(x*0.42 + t*1.5)*0.14 + Math.cos(z*0.36 + t*1.15)*0.14;
  }

  function animate(){
    requestAnimationFrame(animate);
    var dt = clock.getDelta();
    elapsed += dt;
    var t = elapsed;

    // water
    for (var i=0;i<waterCells.length;i++){
      var c = waterCells[i];
      var y = waveAt(c.x, c.z, t);
      M.makeTranslation(c.x, y, c.z);
      water.setMatrixAt(i, M);
    }
    water.instanceMatrix.needsUpdate = true;

    // ship
    shipGroup.position.y = -0.5 + Math.sin(t*1.15)*0.18;
    shipGroup.rotation.x = Math.sin(t*0.85)*0.035;
    shipGroup.rotation.z = Math.sin(t*0.65 + 1.2)*0.02;
    flagGroup.rotation.y = Math.sin(t*5.2)*0.4;

    // lighthouse
    beamGroup.rotation.y = -Math.PI/2 + Math.sin(t*0.6)*1.15;
    lanternLight.intensity = 0.9 + Math.sin(t*2.2)*0.25;

    // clouds
    for (var i=0;i<clouds.length;i++){
      var cl = clouds[i];
      cl.g.position.x += cl.v*dt;
      if (cl.g.position.x > 55) cl.g.position.x = -55;
    }

    // gulls
    for (var i=0;i<gulls.length;i++){
      var gl = gulls[i];
      var theta = t*0.35 + gl.off;
      gl.g.position.set(9 + Math.cos(theta)*12, 10.5 + Math.sin(t*0.9 + gl.off)*0.6, 1 + Math.sin(theta)*12);
      gl.g.rotation.y = -theta;
      var f = Math.sin(t*9 + gl.off*3)*0.55;
      gl.wl.rotation.z = f; gl.wr.rotation.z = -f;
    }

    // buoys
    for (var i=0;i<buoys.length;i++){
      var b = buoys[i];
      b.g.position.y = waveAt(b.x,b.z,t) + 0.15;
      b.g.rotation.z = Math.sin(t*1.2 + b.x)*0.12;
      b.g.rotation.x = Math.cos(t*0.9 + b.z)*0.1;
    }

    // rowboat
    boat.position.y = Math.sin(t*1.35 + 2.0)*0.12;
    boat.rotation.x = Math.sin(t*1.05)*0.045;
    boat.rotation.z = Math.cos(t*0.9)*0.03;

    controls.update();
    renderer.render(scene, camera);
  }
  animate();
}

function y1Window(){ return false; }
function yRow(v){ return false; }

var sceneGlobal = null;
</script>
</body>
</html>
```

A few notes:

- **How to use**: open the file in Chrome → drag to orbit, scroll to zoom, right-drag to pan. Use "Auto-orbit" for a slow cinematic sweep, "Reset view" to snap back.
- **What's in the scene**: a square-rigged ship (hull with red stripe, stern castle with cream windows, hatches, barrels, cannon, staircase bowsprit, waving pennant, rigging), a plank pier with crates, a lamp post and a crane, a striped lighthouse with a sweeping light beam, a warehouse and two cottages, sand/grass shore, bobbing buoys, a rowboat, foam around the hull, drifting clouds and flapping gulls.
- **Performance**: all voxels are drawn via `InstancedMesh` (one draw call per group), and the water is an instanced grid animated per-frame — it runs smoothly in a browser tab.
- If you'd like, I can swap the ship to a clipper/steamer style, add more seafaring details (fishing boats, flags on the pier), or change the palette to a dusk/night harbor with the lighthouse glowing brighter.