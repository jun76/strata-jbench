<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Sailing Ship Harbor</title>
<style>
  body { margin: 0; overflow: hidden; background: #0b1a2a; font-family: system-ui, sans-serif; }
  #hud { position: absolute; top: 10px; left: 10px; color: #cfe3ff; background: rgba(10,25,40,0.55);
    padding: 8px 12px; border-radius: 10px; font-size: 13px; pointer-events: none; }
  #hud h1 { margin: 0 0 4px 0; font-size: 16px; }
</style>
</head>
<body>
<div id="hud"><h1>Sailing Ship — Harbor</h1>Drag: orbit • Scroll: zoom</div>
<script type="importmap">
{
  "imports": {
    "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
    "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
  }
}
</script>
<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87b8d6);
scene.fog = new THREE.Fog(0x87b8d6, 60, 160);

const camera = new THREE.PerspectiveCamera(45, innerWidth/innerHeight, 0.1, 500);
camera.position.set(28, 18, 32);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 4, 0);
controls.enableDamping = true;

const hemi = new THREE.HemisphereLight(0xcfe8ff, 0x20303a, 0.9);
scene.add(hemi);
const sun = new THREE.DirectionalLight(0xfff2d8, 1.6);
sun.position.set(30, 40, 20);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -50; sun.shadow.camera.right = 50;
sun.shadow.camera.top = 50; sun.shadow.camera.bottom = -50;
scene.add(sun);

const palette = {
  water: 0x2a6f8e, water2: 0x3a86a8, sand: 0xd8c28a, wood: 0x7a4a2a,
  woodDark: 0x4a2c18, sail: 0xf3ead6, sailAccent: 0xc94f3d, ship: 0x8b3a2a,
  shipDark: 0x5a221a, metal: 0x2e2e34, flag: 0xd93a2e, grass: 0x5a8a3a,
  rock: 0x6f6a63, hut: 0x8a6a4a, roof: 0x4d3a2e
};

const voxelGeo = new THREE.BoxGeometry(1,1,1);
function box(x,y,z,w,h,d,color,parent,shadow=true){
  const m = new THREE.Mesh(voxelGeo, new THREE.MeshLambertMaterial({ color }));
  m.scale.set(w,h,d);
  m.position.set(x,y,z);
  if (shadow) { m.castShadow = true; m.receiveShadow = true; }
  (parent||scene).add(m);
  return m;
}
function vbox(x,y,z,color,parent,scale=1){
  return box(x,y,z,scale,scale,scale,color,parent);
}

// Water
const waterGeo = new THREE.PlaneGeometry(200,200,1,1);
const water = new THREE.Mesh(waterGeo, new THREE.MeshLambertMaterial({ color: palette.water }));
water.rotation.x = -Math.PI/2;
water.position.y = 0;
water.receiveShadow = true;
scene.add(water);

// animated water tiles
const waterTiles = [];
for (let i=0;i<60;i++){
  const x = (Math.random()-0.5)*180, z=(Math.random()-0.5)*180;
  const t = vbox(x, 0.05, z, palette.water2, scene, 1.2);
  t.receiveShadow = false;
  waterTiles.push({ mesh: t, phase: Math.random()*Math.PI*2 });
}

// Sandy harbor shore
box(0, 0.5, -22, 90, 1, 10, palette.sand, scene).receiveShadow = true;
box(0, 0.4, 24, 80, 0.8, 8, palette.sand, scene).receiveShadow = true;

// Dock (wooden pier) extending into water
box(0, 1.2, -8, 10, 0.6, 18, palette.wood, scene);
box(-5, 0.8, -8, 0.8, 1.2, 18, palette.woodDark, scene);
box(5, 0.8, -8, 0.8, 1.2, 18, palette.woodDark, scene);
for (let i=0;i<7;i++){
  box(-4.5, 0.4, -15 + i*3, 0.8, 1.0, 0.8, palette.woodDark, scene);
  box(4.5, 0.4, -15 + i*3, 0.8, 1.0, 0.8, palette.woodDark, scene);
}
// bollards
vbox(-3, 1.7, -14, palette.metal);
vbox(3, 1.7, -14, palette.metal);

// Sailing ship (low-poly voxels)
const ship = new THREE.Group();
ship.position.set(0, 1.0, 4);
scene.add(ship);

// hull
box(0, 0, 0, 3.2, 1.4, 8.5, palette.ship, ship);
box(0, 0.7, 0, 2.6, 0.8, 7.6, palette.shipDark, ship);
box(0, 0.2, 4.3, 2.0, 1.1, 1.0, palette.shipDark, ship);
box(0, 0.2, -4.3, 1.6, 1.0, 1.2, palette.shipDark, ship);

// deck
box(0, 1.1, 0, 2.6, 0.3, 7.4, palette.wood, ship);

// bow & stern trim
vbox(0, 1.1, 4.7, palette.woodDark, ship);

// masts & rigging
box(0, 4.5, 0.8, 0.4, 6.5, 0.4, palette.woodDark, ship);
box(0, 3.8, -2.3, 0.35, 5.2, 0.35, palette.woodDark, ship);

// sails (triangular-ish made of stacked boxes)
function sail(x,y,z,w,h,color){
  const s = box(x, y, z, w, h, 0.2, color, ship);
  s.castShadow = true;
  return s;
}
sail(0, 5.4, 0.8, 2.6, 3.4, palette.sail);
sail(0, 4.6, 0.8, 2.1, 1.8, palette.sailAccent);
sail(0, 4.2, -2.3, 2.2, 2.6, palette.sail);

// flags
box(0, 7.9, 0.8, 0.15, 1.1, 0.15, palette.metal, ship);
box(0.6, 8.0, 0.8, 1.0, 0.5, 0.15, palette.flag, ship);
box(0, 6.6, -2.3, 0.15, 0.9, 0.15, palette.metal, ship);
box(0.5, 6.75, -2.3, 0.8, 0.4, 0.15, palette.flag, ship);

// cannons on deck
vbox(-0.9, 1.45, 2.4, palette.metal, ship);
vbox(0.9, 1.45, 2.4, palette.metal, ship);
vbox(-0.9, 1.45, -0.4, palette.metal, ship);
vbox(0.9, 1.45, -0.4, palette.metal, ship);

// barrels & crates
vbox(-0.9, 1.5, 3.3, palette.wood, ship);
vbox(0.9, 1.5, 3.3, palette.wood, ship);
vbox(0.7, 1.6, -3.2, palette.wood, ship);

// pier hut
box(8, 1.6, -18, 3, 2.4, 3, palette.hut, scene);
box(8, 3.0, -18, 3.6, 0.8, 3.6, palette.roof, scene);
vbox(6.6, 1.7, -16.4, palette.wood, scene);

// lighthouse on sand
box(-14, 2.4, -20, 2.2, 4.8, 2.2, 0xe8e0d0, scene);
box(-14, 5.2, -20, 2.6, 0.9, 2.6, palette.roof, scene);
vbox(-14, 5.3, -20, 0xffe08a, scene);

// rocks & buoys
for (let i=0;i<8;i++){
  const a = Math.random()*Math.PI*2, r = 26 + Math.random()*16;
  const x = Math.cos(a)*r, z = Math.sin(a)*r;
  const s = 1.2 + Math.random()*1.6;
  vbox(x, 0.3, z, palette.rock, scene, s);
}
const buoys = [];
for (let i=0;i<3;i++){
  const b = vbox(-6 + i*6, 0.5, 18, 0xe84d2e, scene, 0.9);
  buoys.push(b);
}

// birds (simple voxel flappers)
const birds = [];
for (let i=0;i<4;i++){
  const g = new THREE.Group();
  const body = vbox(0,0,0, 0x2b2b2b, g, 0.45);
  const wingL = vbox(-0.5,0,0, 0x3a3a3a, g, 0.5);
  const wingR = vbox(0.5,0,0, 0x3a3a3a, g, 0.5);
  scene.add(g);
  birds.push({ g, wingL, wingR, t: Math.random()*Math.PI*2, speed: 0.6 + Math.random()*0.6 });
}

// animation
const clock = new THREE.Clock();
function animate(){
  requestAnimationFrame(animate);
  const dt = clock.getDelta();
  const t = clock.elapsedTime;

  // gentle ship bob & sway
  ship.position.y = 1.0 + Math.sin(t*1.2) * 0.12;
  ship.rotation.z = Math.sin(t*0.9) * 0.04;
  ship.rotation.x = Math.sin(t*0.7) * 0.02;

  // water shimmer
  for (const w of waterTiles){
    w.mesh.position.y = 0.05 + Math.sin(t*1.6 + w.phase) * 0.18;
  }

  // buoys bob
  for (let i=0;i<buoys.length;i++){
    buoys[i].position.y = 0.5 + Math.sin(t*1.5 + i*1.7) * 0.25;
  }

  // birds circle
  for (let i=0;i<birds.length;i++){
    const b = birds[i];
    const ang = t*b.speed + b.t;
    const r = 18 + i*4;
    b.g.position.set(Math.cos(ang)*r, 12 + Math.sin(t*0.8 + i)*2, Math.sin(ang)*r);
    b.g.rotation.y = -ang;
    const flap = Math.sin(t*6 + i) * 0.45;
    b.wingL.position.y = Math.abs(flap) * 0.4;
    b.wingR.position.y = Math.abs(flap) * 0.4;
  }

  controls.update();
  renderer.render(scene, camera);
}
animate();

addEventListener('resize', () => {
  camera.aspect = innerWidth/innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
</script>
</body>
</html>