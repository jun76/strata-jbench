<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Sailing Ship at a Harbor — 3D Voxel Scene</title>
<style>
  html, body { margin:0; padding:0; overflow:hidden; background:#0a0f1e; font-family: Georgia, serif; }
  #info {
    position: absolute; top: 14px; left: 14px; color:#e8e2d0;
    background: rgba(10,15,30,0.55); padding: 10px 14px; border-radius: 8px;
    pointer-events: none; font-size: 13px; line-height: 1.5; max-width: 280px;
    border: 1px solid rgba(232,226,208,0.2); backdrop-filter: blur(4px);
  }
  #info h1 { font-size: 16px; margin: 0 0 4px 0; letter-spacing: 0.5px; color:#f2e9c8; }
  #hint {
    position: absolute; bottom: 14px; left: 50%; transform: translateX(-50%);
    color:#cfc9b8; font-size: 12px; background: rgba(10,15,30,0.5);
    padding: 6px 14px; border-radius: 20px; pointer-events: none;
    border: 1px solid rgba(232,226,208,0.15);
  }
</style>
</head>
<body>
<div id="info">
  <h1>⛵ Sailing Ship at a Harbor</h1>
  Voxel-style scene. Drag to orbit, scroll to zoom.
</div>
<div id="hint">🖱 drag = orbit &nbsp;·&nbsp; wheel = zoom &nbsp;·&nbsp; right-drag = pan</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
// ---------- Renderer / Scene / Camera ----------
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x1a2a45); // dusk sky
scene.fog = new THREE.Fog(0x1a2a45, 60, 160);

const camera = new THREE.PerspectiveCamera(45, window.innerWidth/window.innerHeight, 0.1, 500);
camera.position.set(28, 20, 28);

const renderer = new THREE.WebGLRenderer({ antialias:true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

// ---------- Lights ----------
const hemi = new THREE.HemisphereLight(0x8fb0d8, 0x2a1d10, 0.7);
scene.add(hemi);

const sun = new THREE.DirectionalLight(0xffd9a0, 1.15);
sun.position.set(30, 40, 20);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -50; sun.shadow.camera.right = 50;
sun.shadow.camera.top = 50; sun.shadow.camera.bottom = -50;
sun.shadow.camera.near = 1; sun.shadow.camera.far = 120;
scene.add(sun);

const rim = new THREE.DirectionalLight(0x6fa8ff, 0.35);
rim.position.set(-20, 15, -25);
scene.add(rim);

// ---------- Materials (flat-ish voxel colors) ----------
const MAT = {
  wood: new THREE.MeshStandardMaterial({ color: 0x7a4a2b, roughness: 0.85, metalness: 0.05 }),
  woodDark: new THREE.MeshStandardMaterial({ color: 0x4a2c18, roughness: 0.9 }),
  woodLight: new THREE.MeshStandardMaterial({ color: 0xa66a3c, roughness: 0.8 }),
  hull: new THREE.MeshStandardMaterial({ color: 0x3a2a20, roughness: 0.8 }),
  hullStripe: new THREE.MeshStandardMaterial({ color: 0xc9a14a, roughness: 0.6, metalness: 0.3 }),
  sail: new THREE.MeshStandardMaterial({ color: 0xf2e6c8, roughness: 0.9, side: THREE.DoubleSide }),
  sailShade: new THREE.MeshStandardMaterial({ color: 0xe0d2ac, roughness: 0.9, side: THREE.DoubleSide }),
  mast: new THREE.MeshStandardMaterial({ color: 0x5a3a22, roughness: 0.85 }),
  rope: new THREE.MeshStandardMaterial({ color: 0x2a2018, roughness: 0.95 }),
  stone: new THREE.MeshStandardMaterial({ color: 0x6b6b6b, roughness: 0.95 }),
  stoneLight: new THREE.MeshStandardMaterial({ color: 0x8a8a86, roughness: 0.95 }),
  water: new THREE.MeshStandardMaterial({ color: 0x14384a, roughness: 0.25, metalness: 0.35 }),
  sand: new THREE.MeshStandardMaterial({ color: 0xc9a96a, roughness: 0.95 }),
  grass: new THREE.MeshStandardMaterial({ color: 0x3d6b35, roughness: 0.95 }),
  roof: new THREE.MeshStandardMaterial({ color: 0x6e3a2a, roughness: 0.85 }),
  roof2: new THREE.MeshStandardMaterial({ color: 0x2a3a5e, roughness: 0.85 }),
  wall: new THREE.MeshStandardMaterial({ color: 0xcfc2a4, roughness: 0.9 }),
  flagRed: new THREE.MeshStandardMaterial({ color: 0xc0392b, roughness: 0.7 }),
  flagGold: new THREE.MeshStandardMaterial({ color: 0xe6b34a, roughness: 0.7 }),
  lamp: new THREE.MeshStandardMaterial({ color: 0xffe08a, emissive: 0xffc44a, emissiveIntensity: 0.8 }),
  window: new THREE.MeshStandardMaterial({ color: 0xffd27a, emissive: 0xffb347, emissiveIntensity: 0.9 }),
  crate: new THREE.MeshStandardMaterial({ color: 0x8a5a32, roughness: 0.9 }),
  barrel: new THREE.MeshStandardMaterial({ color: 0x5a3a22, roughness: 0.85 }),
  lantern: new THREE.MeshStandardMaterial({ color: 0xffd27a, emissive: 0xffb347, emissiveIntensity: 1.2 }),
  rock: new THREE.MeshStandardMaterial({ color: 0x5a5a55, roughness: 0.95 }),
  flagPole: new THREE.MeshStandardMaterial({ color: 0x3a2a1a, roughness: 0.8 }),
};

// ---------- Helpers ----------
function box(w,h,d, mat, x,y,z, parent, castShadow=true, receiveShadow=true){
  const m = new THREE.Mesh(new THREE.BoxGeometry(w,h,d), mat);
  m.position.set(x,y,z);
  m.castShadow = castShadow;
  m.receiveShadow = receiveShadow;
  (parent||scene).add(m);
  return m;
}
function cyl(rTop,rBottom,h, seg, mat, x,y,z, parent, castShadow=true){
  const m = new THREE.Mesh(new THREE.CylinderGeometry(rTop,rBottom,h,seg), mat);
  m.position.set(x,y,z);
  m.castShadow = castShadow;
  m.receiveShadow = true;
  (parent||scene).add(m);
  return m;
}
function cone(r,h,seg,mat,x,y,z,parent,castShadow=true){
  const m = new THREE.Mesh(new THREE.ConeGeometry(r,h,seg), mat);
  m.position.set(x,y,z);
  m.castShadow = castShadow;
  m.receiveShadow = true;
  (parent||scene).add(m);
  return m;
}

// ---------- Water ----------
const water = new THREE.Mesh(new THREE.PlaneGeometry(220,220), MAT.water);
water.rotation.x = -Math.PI/2;
water.position.y = -0.05;
water.receiveShadow = true;
scene.add(water);

// subtle water grid lines (voxel feel)
const gridLines = new THREE.GridHelper(220, 44, 0x2a5a6a, 0x1a4050);
gridLines.position.y = 0.0;
gridLines.material.opacity = 0.35;
gridLines.material.transparent = true;
scene.add(gridLines);

// ---------- Harbor island / landmass ----------
const land = new THREE.Group();
scene.add(land);

// sand base
box(70, 2, 30, MAT.sand, 0, 1, -22, land);
// grass on top
box(70, 0.6, 28, MAT.grass, 0, 2.3, -22, land);
// back rock ridge
for(let i=0;i<9;i++){
  const rx = -30 + i*7 + (Math.random()-0.5)*2;
  const rh = 2 + Math.random()*3;
  box(4 + Math.random()*3, rh, 5, MAT.rock, rx, 2 + rh/2, -34 + (Math.random()-0.5)*2, land);
}

// ---------- Dock / pier ----------
const dock = new THREE.Group();
scene.add(dock);
// main pier deck
box(2.4, 0.5, 26, MAT.woodLight, -14, 2.6, -8, dock);
// planks detail
for(let i=0;i<12;i++){
  box(2.5, 0.15, 0.4, MAT.woodDark, -14, 2.95, -19 + i*2.2, dock, false);
}
// pier posts
for(let i=0;i<6;i++){
  const py = 1.2;
  cyl(0.35, 0.4, 4.5, 6, MAT.woodDark, -15.1, py, -18 + i*4.5, dock);
  cyl(0.35, 0.4, 4.5, 6, MAT.woodDark, -12.9, py, -18 + i*4.5, dock);
}
// small side dock (to the right)
box(14, 0.5, 2.4, MAT.woodLight, -6, 2.6, -20, dock);
for(let i=0;i<6;i++){
  cyl(0.35, 0.4, 4.5, 6, MAT.woodDark, -12 + i*2.6, 1.2, -20, dock);
}

// ---------- Lighthouse (left) ----------
const lighthouse = new THREE.Group();
lighthouse.position.set(-26, 2.5, -28);
land.add(lighthouse);
cyl(2.6, 3.0, 1.2, 8, MAT.stoneLight, 0, 0.6, 0, lighthouse);
cyl(1.8, 2.4, 9, 8, MAT.wall, 0, 5.5, 0, lighthouse);
// red bands
cyl(1.95, 2.15, 1.4, 8, MAT.flagRed, 0, 3.2, 0, lighthouse);
cyl(1.85, 2.05, 1.4, 8, MAT.flagRed, 0, 7.2, 0, lighthouse);
cyl(2.2, 2.2, 0.7, 8, MAT.stone, 0, 10.4, 0, lighthouse);
cyl(1.5, 1.5, 1.8, 8, MAT.lantern, 0, 11.7, 0, lighthouse);
cone(1.9, 1.6, 8, MAT.roof2, 0, 13.3, 0, lighthouse);
cyl(0.15, 0.15, 0.8, 6, MAT.flagPole, 0, 14.4, 0, lighthouse);
box(0.9, 0.6, 0.1, MAT.flagGold, 0.45, 14.6, 0, lighthouse);

// ---------- Harbor buildings ----------
function building(x, z, w, h, d, wallMat, roofMat){
  const g = new THREE.Group();
  g.position.set(x, 2.6, z);
  land.add(g);
  box(w, h, d, wallMat, 0, h/2, 0, g);
  // roof (pyramid-ish using cone)
  cone(Math.max(w,d)*0.72, 2.6, 4, roofMat, 0, h + 1.3, 0, g).rotation.y = Math.PI/4;
  // windows
  const rows = Math.floor(h/2.5);
  for(let r=0;r<rows;r++){
    for(let c=0;c<Math.floor(w/1.6);c++){
      const wx = -w/2 + 1 + c*1.6;
      box(0.6, 0.8, 0.1, MAT.window, wx, 1.4 + r*2.2, d/2 + 0.05, g, false);
    }
  }
  // door
  box(1.2, 1.8, 0.12, MAT.woodDark, 0, 0.9, d/2 + 0.06, g, false);
  return g;
}
building(-8, -28, 5, 5, 4, MAT.wall, MAT.roof);
building(2, -30, 6, 6.5, 5, MAT.wall, MAT.roof2);
building(11, -28, 4.5, 4, 4, MAT.wall, MAT.roof);
building(-18, -30, 4, 4.5, 4, MAT.wall, MAT.roof2);

// ---------- Trees ----------
function tree(x, z, s=1){
  const g = new THREE.Group();
  g.position.set(x, 2.6, z);
  land.add(g);
  cyl(0.4*s, 0.5*s, 1.6*s, 6, MAT.woodDark, 0, 0.8*s, 0, g);
  box(2.4*s, 2.4*s, 2.4*s, MAT.grass, 0, 2.6*s, 0, g);
  box(1.6*s, 1.4*s, 1.6*s, MAT.grass, 0, 4.2*s, 0, g);
}
tree(-24, -18, 1.1);
tree(-3, -22, 0.9);
tree(7, -22, 1.0);
tree(16, -24, 1.2);
tree(-13, -24, 0.8);

// ---------- Crates & barrels on dock ----------
box(1.1, 1.1, 1.1, MAT.crate, -13, 3.55, -10, scene);
box(0.9, 0.9, 0.9, MAT.crate, -13.5, 4.6, -10.2, scene);
box(1.0, 1.0, 1.0, MAT.crate, -13, 3.5, -13, scene);
cyl(0.55, 0.55, 1.3, 10, MAT.barrel, -13.5, 3.6, -6.5, scene);
cyl(0.55, 0.55, 1.3, 10, MAT.barrel, -12.6, 3.6, -6.8, scene);
// lantern on dock post
cyl(0.12, 0.12, 1.6, 6, MAT.flagPole, -15.2, 4.2, -20, scene);
box(0.5, 0.6, 0.5, MAT.lantern, -15.2, 5.1, -20, scene, false);
cyl(0.12, 0.12, 1.6, 6, MAT.flagPole, -12.8, 4.2, -20, scene);
box(0.5, 0.6, 0.5, MAT.lantern, -12.8, 5.1, -20, scene, false);

// ---------- The sailing ship ----------
const ship = new THREE.Group();
scene.add(ship);
ship.position.set(-8, 0.4, 4);
ship.rotation.y = -0.25;

// Hull — layered boxes for voxel look
box(6.5, 1.6, 2.6, MAT.hull, 0, 1.4, 0, ship);
box(5.4, 1.0, 2.2, MAT.hull, 0, 0.6, 0, ship);
box(5.6, 0.35, 2.35, MAT.hullStripe, 0, 2.3, 0, ship);
// bow & stern taper
box(1.6, 1.2, 1.8, MAT.hull, 3.6, 1.4, 0, ship);
box(1.4, 1.2, 1.6, MAT.hull, -3.6, 1.4, 0, ship);
// deck
box(5.6, 0.3, 2.2, MAT.woodLight, 0, 2.3, 0, ship);
// railing posts
for(let i=0;i<7;i++){
  box(0.18, 0.7, 0.18, MAT.woodDark, -2.6 + i*0.85, 2.85, 1.05, ship, false);
  box(0.18, 0.7, 0.18, MAT.woodDark, -2.6 + i*0.85, 2.85, -1.05, ship, false);
}
// stern cabin
box(1.6, 1.4, 1.8, MAT.wood, -2.2, 3.2, 0, ship);
box(1.7, 0.3, 1.9, MAT.woodDark, -2.2, 3.95, 0, ship);
box(0.9, 0.7, 0.1, MAT.window, -2.2, 3.3, 0.95, ship, false);
box(0.9, 0.7, 0.1, MAT.window, -2.2, 3.3, -0.95, ship, false);

// Masts
const mastX = [0.6, -1.6];
const mastH = [8.5, 6.5];
mastX.forEach((mx, idx)=>{
  cyl(0.28, 0.34, mastH[idx], 8, MAT.mast, mx, 2.6 + mastH[idx]/2, 0, ship);
  // yard (horizontal crossbar)
  cyl(0.16, 0.16, 4.6, 6, MAT.mast, mx, 2.6 + mastH[idx]*0.78, 0, ship).rotation.z = Math.PI/2;
});
// top flag
box(1.1, 0.7, 0.08, MAT.flagRed, 0.6 + 0.55, 2.6 + 8.5 + 0.3, 0, ship, false);

// Sails — plane-ish boxes slightly angled
function sail(mx, baseY, w, h, mat){
  const g = new THREE.Group();
  g.position.set(mx, baseY, 0);
  ship.add(g);
  // main sail (curved look via two stacked boxes)
  box(w, h*0.55, 0.12, mat, 0, h*0.27, 0, g, true);
  box(w*0.85, h*0.4, 0.12, mat, 0, h*0.72, 0, g, true);
  // bottom seam
  box(w*1.05, 0.18, 0.16, MAT.woodDark, 0, 0.05, 0, g, false);
  // vertical crease
  box(0.1, h*0.85, 0.14, MAT.sailShade, 0, h*0.45, 0, g, false);
  return g;
}
sail(0.6, 3.0, 3.6, 4.4, MAT.sail);
sail(-1.6, 3.0, 3.0, 3.4, MAT.sailShade);

// rigging lines (thin boxes)
function line(x1,y1,z1, x2,y2,z2, parent){
  const dx=x2-x1, dy=y2-y1, dz=z2-z1;
  const len = Math.sqrt(dx*dx+dy*dy+dz*dz);
  const m = new THREE.Mesh(new THREE.CylinderGeometry(0.05,0.05,len,4), MAT.rope);
  m.position.set((x1+x2)/2,(y1+y2)/2,(z1+z2)/2);
  m.lookAt(new THREE.Vector3(x2,y2,z2).add(parent.position));
  // simpler: orient via quaternion
  const dir = new THREE.Vector3(dx,dy,dz).normalize();
  m.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0), dir);
  parent.add(m);
}
line(0.6, 11.0, 0, 3.4, 2.6, 0, ship);
line(0.6, 11.0, 0, -3.2, 2.6, 0, ship);
line(-1.6, 9.0, 0, 3.4, 2.6, 0, ship);
line(-1.6, 9.0, 0, -3.2, 2.6, 0, ship);
line(0.6, 11.0, 0, -1.6, 9.0, 0, ship);

// Anchor
cyl(0.18, 0.18, 1.4, 6, MAT.rope, 3.4, 1.6, 1.1, ship);
box(0.9, 0.18, 0.18, MAT.rope, 3.4, 0.9, 1.1, ship);

// Lantern at bow
box(0.4, 0.5, 0.4, MAT.lantern, 3.7, 2.7, 0, ship, false);

// ---------- Small rowboat ----------
const rowboat = new THREE.Group();
rowboat.position.set(-2, 0.4, 12);
scene.add(rowboat);
box(3.2, 0.9, 1.5, MAT.wood, 0, 0.55, 0, rowboat);
box(2.6, 0.5, 1.2, MAT.woodLight, 0, 1.05, 0, rowboat);
box(0.5, 0.4, 1.3, MAT.woodDark, 1.2, 1.3, 0, rowboat);
box(0.5, 0.4, 1.3, MAT.woodDark, -1.2, 1.3, 0, rowboat);

// ---------- Clouds (voxel) ----------
const clouds = new THREE.Group();
scene.add(clouds);
function cloud(x,y,z, s){
  const g = new THREE.Group();
  g.position.set(x,y,z);
  const mat = new THREE.MeshStandardMaterial({ color: 0xe8e2d0, roughness: 1 });
  box(3*s, 1.2*s, 1.6*s, mat, 0, 0, 0, g, false, false);
  box(2*s, 1.0*s, 1.3*s, mat, -1.4*s, -0.2*s, 0, g, false, false);
  box(2.2*s, 1.1*s, 1.4*s, mat, 1.6*s, -0.1*s, 0, g, false, false);
  box(1.4*s, 0.9*s, 1.2*s, mat, 0.3*s, 1.0*s, 0, g, false, false);
  clouds.add(g);
}
cloud(-35, 26, -50, 1.4);
cloud(20, 30, -55, 1.8);
cloud(40, 24, -30, 1.2);
cloud(-15, 28, -45, 1.1);

// ---------- Stars / sparkles (subtle) ----------
const starGeo = new THREE.BufferGeometry();
const starPos = [];
for(let i=0;i<180;i++){
  const a = Math.random()*Math.PI*2;
  const r = 90 + Math.random()*40;
  starPos.push(Math.cos(a)*r, 30 + Math.random()*40, Math.sin(a)*r);
}
starGeo.setAttribute('position', new THREE.Float32BufferAttribute(starPos, 3));
const starMat = new THREE.PointsMaterial({ color: 0xfff2c0, size: 0.5, sizeAttenuation: true, transparent: true, opacity: 0.9 });
scene.add(new THREE.Points(starGeo, starMat));

// ---------- Orbit controls (manual simple) ----------
let isDown = false, lastX=0, lastY=0;
let camTheta = Math.atan2(camera.position.z, camera.position.x);
let camPhi = Math.atan2(camera.position.y, Math.sqrt(camera.position.x**2 + camera.position.z**2));
let camR = Math.sqrt(camera.position.x**2 + camera.position.y**2 + camera.position.z**2);
const target = new THREE.Vector3(0, 4, -10);

const el = renderer.domElement;
el.addEventListener('pointerdown', e => { isDown = true; lastX = e.clientX; lastY = e.clientY; el.setPointerCapture(e.pointerId); });
window.addEventListener('pointerup', () => { isDown = false; });
window.addEventListener('pointermove', e => {
  if(!isDown) return;
  const dx = e.clientX - lastX, dy = e.clientY - lastY;
  lastX = e.clientX; lastY = e.clientY;
  camTheta -= dx * 0.005;
  camPhi = Math.max(0.15, Math.min(1.45, camPhi + dy * 0.005));
});
el.addEventListener('wheel', e => {
  e.preventDefault();
  camR = Math.max(10, Math.min(120, camR + e.deltaY * 0.03));
}, { passive:false });

// touch pinch
let lastPinch = 0;
el.addEventListener('touchstart', e => {
  if(e.touches.length === 2){
    lastPinch = Math.hypot(e.touches[0].clientX - e.touches[1].clientX, e.touches[0].clientY - e.touches[1].clientY);
  }
});
el.addEventListener('touchmove', e => {
  if(e.touches.length === 2){
    const p = Math.hypot(e.touches[0].clientX - e.touches[1].clientX, e.touches[0].clientY - e.touches[1].clientY);
    if(lastPinch > 0) camR = Math.max(10, Math.min(120, camR - (p - lastPinch) * 0.05));
    lastPinch = p;
    e.preventDefault();
  }
}, { passive:false });

// ---------- Animation ----------
const clock = new THREE.Clock();
function animate(){
  requestAnimationFrame(animate);
  const t = clock.getElapsedTime();

  // ship gentle bob
  ship.position.y = 0.4 + Math.sin(t * 0.9) * 0.25;
  ship.rotation.z = Math.sin(t * 0.7) * 0.035;
  ship.rotation.x = Math.sin(t * 0.55 + 1) * 0.02;

  rowboat.position.y = 0.35 + Math.sin(t * 1.1 + 2) * 0.18;
  rowboat.rotation.z = Math.sin(t * 0.8 + 0.5) * 0.04;

  // clouds drift
  clouds.children.forEach((c, i) => {
    c.position.x += 0.008 + i*0.002;
    if(c.position.x > 70) c.position.x = -70;
  });

  // water subtle shimmer via grid opacity
  gridLines.material.opacity = 0.28 + Math.sin(t*1.5) * 0.08;

  // camera position from spherical coords
  camera.position.set(
    target.x + camR * Math.sin(camPhi) * Math.cos(camTheta),
    target.y + camR * Math.cos(camPhi),
    target.z + camR * Math.sin(camPhi) * Math.sin(camTheta)
  );
  camera.lookAt(target);

  renderer.render(scene, camera);
}
animate();

// ---------- Resize ----------
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
</script>
</body>
</html>