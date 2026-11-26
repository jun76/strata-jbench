The user asks for a 3D voxel art scene "A sailing ship calling at a harbor" with immediate rendering and mouse view, pasteable into one HTML file and open in Chrome. This is a benign creative coding request. I need produce HTML/JS. No need to mention safety. Need ensure no unsafe content. Provide code.

Need design voxel art scene. Use three.js via CDN? They said single HTML file paste and open in Chrome. CDN requires internet; okay but maybe prefer self-contained with no external libs? They said use whatever libraries. To be robust, could implement 3D voxel with Canvas? Mouse rotate. But three.js is easier. Single HTML with CDN script. "render immediately" means on open. Could use Three.js from CDN; Chrome can access if internet. Alternatively include minimal voxel rendering with no external dependencies to avoid CDN failure. Need mouse view: drag rotate camera, maybe wheel zoom. Could implement a small 3D voxel scene using pure JavaScript with WebGL? More code. Using Three.js is acceptable.

Need create scene: harbor with voxel grid water, dock/pier, ship with sails, containers, lighthouse, sky. Voxel art = cubes. Use THREE.Scene, PerspectiveCamera, OrbitControls maybe from CDN. But single file paste: include <script src="https://cdnjs...">. Need maybe use three r128. Simpler: no OrbitControls, implement own mouse drag rotate to reduce deps. Use three.js CDN and custom pointer controls. Render immediately.

Let's craft a polished scene:
- Voxel art style: cubes with colors, MeshLambertMaterial? flat shading.
- Sky background, fog.
- Harbor: water plane made of voxel tiles with animated blue hues; dock made of voxel brown planks; ship hull from cubes, mast, sails (white voxels), flag red, smoke? Lighthouse, cargo containers (colored boxes), seagulls? maybe simple cubes.
- Lighting: directional sun, hemisphere. Shadows.
- Mouse: drag to orbit, wheel zoom, auto gentle bobbing ship.
- UI overlay text with controls.
- Use requestAnimationFrame.

Need code concise but complete. Need avoid too much. Let's write HTML with CSS. Contains all. Use Three.js CDN: https://unpkg.com/three@0.128.0/build/three.min.js (stable). Custom camera orbit with yaw/pitch.

Implementation details:
- scene, camera, renderer with antialias, setPixelRatio.
- create voxel(color,x,y,z,sx,sy,sz) mesh BoxGeometry. Use shared materials per color to reduce overhead.
- group harbor: water grid 18x14 tiles at y=0? Let's define coordinates. Water tiles at y=0, size 1, top at 0. Dock at left? Coordinate system x horizontal, z depth, y up.
Scene layout: center ship on harbor at (0, 1.5, 0). Dock along x? Maybe pier at z=-5, x from -8 to 8, y=1, width. Lighthouse at (6,2,-6). Containers on dock. Ship hull at z=1, x=-1, y=1.5.
Water tiles: for x=-10..10, z=-8..8, y=0.5, color varies by sin. Actually water as voxels 1x1x0.3.
Dock: planks row z=-6, x=-9..9, y=2, width 2 depth maybe. Lighthouse on dock.
Ship: hull: rows. Use cubes: bow at x=3, stern at x=-3, sides. Simpler: base row y=2, x -3..3 z 0 (width), plus side rows z=-1 and z=1. Hull color brown/navy. Mast at x=0 y=5. Sails: white cubes stack y 3.5..5 at z=0? Use box sail: thin white boxes. Flag red at top.
Need mouse rotate: pointerdown/move/up; yaw += dx*0.005, pitch clamp; zoom via wheel; update camera pos from target.
- Animation: ship group y bob, rotation z slight; water tiles color subtle? Maybe skip recolor to keep perf.
- Resize.
- Start render immediately.

Need answer: maybe include brief note. Provide single HTML code block. Ensure no markdown excessive. Fine.

Need ensure the code is valid. Let's compose carefully.

Potential pitfalls: Three.js CDN not loading in offline Chrome. Mention internet for CDN. But maybe can include minimal local implementation to avoid CDN. Since user specifically wants paste all into single HTML file. A self-contained file without internet would be better. But writing WebGL voxel engine is complex. Could use CSS 3D? No. Three.js CDN is standard. Mention requires internet once to load Three.js. Could also fallback: if THREE missing, show message. Good.

Let's write robust code.

Details:
const materials = {};
function mat(c){ if(!materials[c]) materials[c]=new THREE.MeshLambertMaterial({color:c, flatShading:true}); return materials[c];}
const geo = new THREE.BoxGeometry(1,1,1);
function v(x,y,z,sx=1,sy=1,sz=1,c=0xffffff,parent=scene){ const m=new THREE.Mesh(geo, mat(c)); m.scale.set(sx,sy,sz); m.position.set(x,y,z); m.castShadow=true; m.receiveShadow=true; parent.add(m); return m; }
Note scaling a unit cube: good.

Water animation: store water meshes with phase, update color maybe not needed. Could change emissive? Keep static but add gentle wave by y = base + sin. store baseY and phase.

Dock:
planks: for x=-9..9, z=-5..-3? Actually dock platform at z=-6, depth 3 (z=-6..-4). Use voxels y=1.5 maybe top. Add posts.
Container boxes on dock at x=-6,-3,4 with colors.
Lighthouse at x=7 z=-5: stack cubes y 2..6, white/red, top light yellow, rotating? maybe simple.
Ship: group ship; hull rows:
base: x=-3..3, y=2.2, z=0, brown, sx=1, sy=0.8, sz=2.4? That's a single box? Better voxel look: row y=1.8: x=-3..3 z=0 sz=2.4; sides z=-1/1 x=-2..2 y=2.3; bow x=3 y=2.4; stern x=-3 y=2.4. Use cubes sx=1. Use navy hull color.
deck: white? mast at x=0 y=4.0, z=0, 0.3 tall 3.5. Sails: for y=3..5, white box x=0 z=0 sz=0.2 sx=1.8? A sail as thin box width 2 (x), height 2 (y), depth .2. Put at y=4.2. Flag red at y=6.0 x=0 sx=0.8 sy=0.4 sz=0.2.
Maybe portholes: small yellow/white cubes sides.
Add crates aboard.

Seagulls: tiny cubes floating.
Add sun? no.

Camera orbit: target (0,3,0); radius 18; yaw=0.7, pitch=0.35. update: camera.position.set(target.x + radius*cos(pitch)*sin(yaw), target.y + radius*sin(pitch), target.z + radius*cos(pitch)*cos(yaw)); lookAt target.
Wheel zoom clamp radius 10..30.
pointer drag: on canvas pointerdown set drag; move if drag; yaw -= dx*0.006; pitch += dy*0.004 clamp 0.08..1.1.
Prevent context menu.

Overlay: absolute top-left, pointer-events none.

Animation loop: ship.position.y = base + sin(t*1.2)*0.25; ship.rotation.z = sin(t*0.9)*0.05; ship.rotation.x = sin(t*0.7)*0.03; water tiles y = base + sin(t*2+phase)*0.08; lighthouse light rotation? light beam maybe skip.

Shadows: renderer.shadowMap.enabled true; directional light position (8,12,6) castShadow with shadow camera bounds. Ground/water receive.

Sky: scene.background = new THREE.Color(0x0b1b2e?) maybe harbor daytime sky #bfe6ff. Use fog.

Ground? Water fills scene. Add sand? Not necessary.

Add subtle vignette via CSS? Not necessary.

Need final answer only code. Ensure code complete.

Let's craft final with intro one sentence and code. Done.Here’s a self-contained voxel harbor scene for Chrome. It uses Three.js from CDN, renders immediately on open, and supports mouse drag-orbit + wheel zoom.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Voxel Harbor — Sailing Ship Calling</title>
<style>
  html,body{margin:0;height:100%;overflow:hidden;background:#0b1722;font-family:ui-sans-serif,system-ui,sans-serif}
  #app{position:fixed;inset:0}
  #hud{position:fixed;left:16px;top:16px;color:#eef7ff;background:rgba(8,18,30,.55);border:1px solid rgba(255,255,255,.18);border-radius:14px;padding:12px 14px;backdrop-filter:blur(6px);pointer-events:none}
  #hud h1{margin:0 0 4px;font-size:16px;letter-spacing:.4px}
  #hud p{margin:0;font-size:12px;opacity:.86}
  #badge{position:fixed;right:16px;bottom:14px;color:#cfe9ff;font-size:11px;background:rgba(8,18,30,.45);padding:8px 10px;border-radius:10px}
</style>
</head>
<body>
<div id="app"></div>
<div id="hud">
  <h1>Voxel Harbor</h1>
  <p>Drag to orbit · wheel to zoom · ship is gently bobbing</p>
</div>
<div id="badge">single-file Three.js voxel scene</div>

<script src="https://unpkg.com/three@0.128.0/build/three.min.js"></script>
<script>
(function(){
  if(!window.THREE){
    document.body.innerHTML = '<div style="padding:30px;color:#fff">Could not load Three.js. Please check your internet connection and open this in Chrome.</div>';
    return;
  }

  const app = document.getElementById('app');
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x9fd8ff);
  scene.fog = new THREE.Fog(0x9fd8ff, 22, 58);

  const camera = new THREE.PerspectiveCamera(50, innerWidth/innerHeight, 0.1, 200);
  const renderer = new THREE.WebGLRenderer({antialias:true});
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.setSize(innerWidth, innerHeight);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  app.appendChild(renderer.domElement);

  const hemi = new THREE.HemisphereLight(0xcfe9ff, 0x1c2f44, 0.75);
  scene.add(hemi);
  const sun = new THREE.DirectionalLight(0xfff2c8, 1.25);
  sun.position.set(10, 14, 7);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  sun.shadow.camera.near = 1;
  sun.shadow.camera.far = 60;
  sun.shadow.camera.left = -18; sun.shadow.camera.right = 18;
  sun.shadow.camera.top = 18; sun.shadow.camera.bottom = -18;
  scene.add(sun);

  const geo = new THREE.BoxGeometry(1,1,1);
  const mats = new Map();
  function mat(color){
    if(!mats.has(color)) mats.set(color, new THREE.MeshLambertMaterial({color, flatShading:true}));
    return mats.get(color);
  }
  function voxel(x,y,z,sx=1,sy=1,sz=1,color=0xffffff,parent=scene){
    const m = new THREE.Mesh(geo, mat(color));
    m.scale.set(sx,sy,sz);
    m.position.set(x,y,z);
    m.castShadow = true;
    m.receiveShadow = true;
    parent.add(m);
    return m;
  }

  const palette = {
    waterA:0x2a6f9f, waterB:0x3b86b5, waterC:0x1f5b86,
    dock:0x7b5a3a, dockDark:0x5b402b,
    hull:0x22314f, hullTrim:0x1d4d5c, deck:0x9a7a55,
    sail:0xf4f1e6, mast:0x4a3222, flag:0xd43f32,
    containerRed:0xd8543c, containerBlue:0x3c68c0, containerYellow:0xe0b24a, containerGreen:0x3f9a5a,
    lighthouseWhite:0xf6f3ea, lighthouseRed:0xd8443a, light:0xffd66b
  };

  // Water: animated voxel tiles
  const waterTiles = [];
  for(let x=-11; x<=11; x++){
    for(let z=-9; z<=9; z++){
      const r = Math.sin(x*0.9 + z*0.7) * 0.5 + 0.5;
      const color = r < 0.36 ? palette.waterA : r < 0.72 ? palette.waterB : palette.waterC;
      const t = voxel(x, 0.45, z, 0.94, 0.28, 0.94, color);
      waterTiles.push({mesh:t, baseY:0.45, phase:(x*1.7+z*2.1)*0.45});
    }
  }

  // Harbor dock
  const dock = new THREE.Group(); scene.add(dock);
  for(let x=-9; x<=9; x++){
    voxel(x, 1.45, -6, 1.0, 0.55, 3.8, palette.dock, dock);
    if(x % 3 === 0) voxel(x, 1.9, -4.6, 0.22, 0.55, 0.22, palette.dockDark, dock);
  }
  // Dock edge posts
  for(let x=-9; x<=9; x+=3) voxel(x, 1.75, -7.7, 0.35, 0.9, 0.35, palette.dockDark, dock);

  // Containers
  voxel(-6.2, 2.45, -5.9, 1.6, 1.25, 1.35, palette.containerRed, dock);
  voxel(-3.7, 2.45, -5.9, 1.6, 1.25, 1.35, palette.containerBlue, dock);
  voxel(-1.2, 2.45, -5.9, 1.6, 1.25, 1.35, palette.containerYellow, dock);
  voxel(3.8, 2.45, -5.9, 1.6, 1.25, 1.35, palette.containerGreen, dock);
  voxel(5.2, 3.6, -5.9, 1.6, 1.05, 1.35, palette.containerBlue, dock);

  // Crane
  const crane = new THREE.Group(); crane.position.set(6.6,1.7,-5.6); dock.add(crane);
  voxel(0,1.0,0,0.55,2.4,0.55,0x2f3440,crane);
  voxel(0,2.55,0,0.55,0.5,3.2,0x2f3440,crane);
  voxel(0,2.15,1.55,0.28,1.35,0.28,0x4b5563,crane);
  voxel(0,1.35,1.55,0.8,0.5,0.8,palette.containerYellow,crane);

  // Lighthouse
  const lighthouse = new THREE.Group(); lighthouse.position.set(-8.2,1.7,-5.8); dock.add(lighthouse);
  for(let i=0;i<5;i++){
    voxel(0,1.2+i*1.0,0, i%2 ? 0.85 : 0.95, 1.0, i%2 ? 0.85 : 0.95, i%2 ? palette.lighthouseRed : palette.lighthouseWhite, lighthouse);
  }
  voxel(0,6.2,0,1.15,0.75,1.15,0x26313f,lighthouse);
  voxel(0,6.75,0,0.55,0.55,0.55,palette.light,lighthouse);

  // Ship
  const ship = new THREE.Group(); ship.position.set(0,0.55,1.4); scene.add(ship);
  const hull = new THREE.Group(); ship.add(hull);
  for(let x=-3; x<=3; x++){
    const bow = x===3 ? 0.55 : 1.0;
    voxel(x, 2.05, 0, 0.95, 0.85, 2.15*bow, palette.hull, hull);
  }
  for(let x=-2; x<=2; x++){
    voxel(x, 2.7, -0.95, 0.85, 0.55, 0.42, palette.hullTrim, hull);
    voxel(x, 2.7, 0.95, 0.85, 0.55, 0.42, palette.hullTrim, hull);
  }
  voxel(-3.15, 2.45, 0, 0.9, 1.0, 1.8, palette.hullTrim, hull);
  voxel(3.35, 2.25, 0, 0.65, 0.7, 1.15, palette.hull, hull);
  for(let x=-2; x<=2; x++) voxel(x, 2.75, 0, 0.8, 0.35, 1.6, palette.deck, hull);

  // Portholes and cargo
  for(let x=-2; x<=2; x+=2){
    voxel(x, 2.18, -1.12, 0.42, 0.42, 0.18, 0xffd66b, hull);
    voxel(x, 2.18, 1.12, 0.42, 0.42, 0.18, 0xffd66b, hull);
  }
  voxel(-1.8, 3.0, -0.35, 0.72, 0.72, 0.72, palette.containerYellow, hull);
  voxel(1.6, 3.0, 0.35, 0.72, 0.72, 0.72, palette.containerRed, hull);

  // Mast, sail, flag
  voxel(0, 4.0, 0, 0.42, 3.0, 0.42, palette.mast, ship);
  voxel(0, 4.75, 0, 2.1, 1.75, 0.16, palette.sail, ship);
  voxel(0, 5.95, 0, 0.95, 0.45, 0.18, palette.flag, ship);
  voxel(0, 6.45, 0, 0.2, 0.35, 0.2, palette.mast, ship);

  // Small boat / rowboat near bow
  const boat = new THREE.Group(); boat.position.set(4.7,0.75,-2.1); scene.add(boat);
  voxel(0,0.35,0,1.5,0.45,0.8,0x6a4630,boat);
  voxel(0,0.75,0,0.9,0.4,0.45,0x8b6a42,boat);

  // Seagulls
  const gulls = [];
  for(let i=0;i<5;i++){
    const g = new THREE.Group();
    voxel(-0.25,0,0,0.28,0.08,0.08,0xf8fbff,g);
    voxel(0.25,0,0,0.28,0.08,0.08,0xf8fbff,g);
    voxel(0,0.02,0,0.2,0.12,0.2,0xf8fbff,g);
    g.position.set(-6+i*3.2, 6.3+Math.sin(i*1.3)*0.8, -3+i*0.8);
    scene.add(g);
    gulls.push({g, baseY:g.position.y, phase:i*1.7});
  }

  // Camera orbit state
  const target = new THREE.Vector3(0, 3.0, 0);
  let yaw = 0.72, pitch = 0.38, radius = 21;
  let dragging = false, lastX = 0, lastY = 0;

  const el = renderer.domElement;
  el.addEventListener('pointerdown', e => { dragging = true; lastX = e.clientX; lastY = e.clientY; el.setPointerCapture(e.pointerId); });
  el.addEventListener('pointermove', e => {
    if(!dragging) return;
    const dx = e.clientX - lastX, dy = e.clientY - lastY;
    lastX = e.clientX; lastY = e.clientY;
    yaw -= dx * 0.006;
    pitch = Math.max(0.12, Math.min(1.05, pitch + dy * 0.004));
  });
  el.addEventListener('pointerup', () => dragging = false);
  el.addEventListener('pointercancel', () => dragging = false);
  el.addEventListener('wheel', e => {
    e.preventDefault();
    radius = Math.max(12, Math.min(34, radius + e.deltaY * 0.02));
  }, {passive:false});

  function updateCamera(){
    camera.position.set(
      target.x + radius * Math.cos(pitch) * Math.sin(yaw),
      target.y + radius * Math.sin(pitch),
      target.z + radius * Math.cos(pitch) * Math.cos(yaw)
    );
    camera.lookAt(target);
  }

  function resize(){
    camera.aspect = innerWidth/innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(innerWidth, innerHeight);
  }
  addEventListener('resize', resize);

  const clock = new THREE.Clock();
  function animate(){
    const t = clock.getElapsedTime();
    ship.position.y = 0.55 + Math.sin(t*1.25)*0.18;
    ship.rotation.z = Math.sin(t*0.85)*0.045;
    ship.rotation.x = Math.sin(t*0.62)*0.03;
    boat.position.y = 0.75 + Math.sin(t*1.7+1.4)*0.12;
    boat.rotation.z = Math.sin(t*1.35+0.7)*0.06;
    for(const w of waterTiles) w.mesh.position.y = w.baseY + Math.sin(t*2.1 + w.phase)*0.09;
    for(const gg of gulls){
      gg.g.position.y = gg.baseY + Math.sin(t*1.8 + gg.phase)*0.45;
      gg.g.rotation.y = Math.sin(t*0.9 + gg.phase)*0.35;
    }
    updateCamera();
    renderer.render(scene, camera);
    requestAnimationFrame(animate);
  }
  resize();
  animate();
})();
</script>
</body>
</html>
```

Chrome should render it immediately. It uses a CDN for Three.js, so the first load needs network access; everything else is in one file.