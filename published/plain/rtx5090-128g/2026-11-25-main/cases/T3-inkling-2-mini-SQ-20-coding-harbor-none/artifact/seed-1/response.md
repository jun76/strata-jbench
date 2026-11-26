<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Harbor Ship — Voxel Art</title>
<style>
  html, body { margin: 0; padding: 0; height: 100%; overflow: hidden; background: #1a2a4a; font-family: monospace; }
  #info {
    position: absolute; top: 10px; left: 10px; color: #fff;
    background: rgba(0,0,0,0.45); padding: 8px 12px; border-radius: 6px;
    font-size: 13px; line-height: 1.5; pointer-events: none; z-index: 10;
  }
  #info b { color: #ffd166; }
  canvas { display: block; }
</style>
</head>
<body>
<div id="info">
  <b>Harbor Ship</b> — drag to orbit, scroll to zoom<br>
  Click ship to make it bob
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function(){
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x87ceeb);
  scene.fog = new THREE.Fog(0x87ceeb, 60, 160);

  const camera = new THREE.PerspectiveCamera(55, window.innerWidth/window.innerHeight, 0.1, 300);
  camera.position.set(28, 22, 34);

  const renderer = new THREE.WebGLRenderer({antialias:true});
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  document.body.appendChild(renderer.domElement);

  // Lights
  const ambient = new THREE.AmbientLight(0xffffff, 0.55);
  scene.add(ambient);
  const sun = new THREE.DirectionalLight(0xfff3d6, 1.15);
  sun.position.set(20, 35, 15);
  sun.castShadow = true;
  sun.shadow.mapSize.width = 2048; sun.shadow.mapSize.height = 2048;
  sun.shadow.camera.left = -40; sun.shadow.camera.right = 40;
  sun.shadow.camera.top = 40; sun.shadow.camera.bottom = -40;
  sun.shadow.camera.near = 1; sun.shadow.camera.far = 120;
  sun.shadow.bias = -0.0005;
  scene.add(sun);

  // Hemisphere for softer sky/ground
  const hemi = new THREE.HemisphereLight(0xcfe8ff, 0x5b7a5b, 0.35);
  scene.add(hemi);

  // Materials helper
  function vox(color){ return new THREE.MeshLambertMaterial({color}); }
  const MAT = {
    hull: vox(0x7a3b22),
    hullDark: vox(0x4a2316),
    deck: vox(0xd9a066),
    mast: vox(0x6b4226),
    sail: vox(0xf4f1e6),
    sailShade: vox(0xd8d3c0),
    cabin: vox(0xece0c8),
    cabinRoof: vox(0xb5523c),
    flag: vox(0xe63946),
    flagWhite: vox(0xffffff),
    water: vox(0x2a7f9e),
    waterDark: vox(0x1f6d8a),
    sand: vox(0xe0c48a),
    dock: vox(0x8a6a44),
    dockPost: vox(0x5a4028),
    rock: vox(0x7d7d7d),
    rockDark: vox(0x5e5e5e),
    crane: vox(0xc94f3a),
    containerRed: vox(0xd94f3d),
    containerBlue: vox(0x3d6fd9),
    containerGreen: vox(0x3fa75d),
    containerYellow: vox(0xe0b13a),
    buoy: vox(0xff7f2a),
    buoyWhite: vox(0xffffff),
    lighthouse: vox(0xf5f5f5),
    lighthouseRed: vox(0xe63946),
    roof: vox(0x333333),
    window: vox(0xffd166)
  };

  const world = new THREE.Group();
  scene.add(world);

  // ---- Water plane (voxel-style grid) ----
  const waterGroup = new THREE.Group();
  world.add(waterGroup);
  const waterGeo = new THREE.PlaneGeometry(90, 60, 24, 16);
  const waterMat = new THREE.MeshLambertMaterial({color: 0x2a7f9e, transparent:true, opacity:0.92});
  const water = new THREE.Mesh(waterGeo, waterMat);
  water.rotation.x = -Math.PI/2;
  water.position.y = -0.5;
  water.receiveShadow = true;
  waterGroup.add(water);

  // water ripple squares
  for(let i=0;i<80;i++){
    const w = 1+Math.random()*2;
    const d = 0.4+Math.random()*0.6;
    const sq = new THREE.Mesh(new THREE.PlaneGeometry(w,d), new THREE.MeshLambertMaterial({color: Math.random()>0.5?0x3fa0c2:0x1f6d8a, transparent:true, opacity:0.5}));
    sq.rotation.x = -Math.PI/2;
    sq.position.set((Math.random()-0.5)*80, -0.45, (Math.random()-0.5)*52);
    waterGroup.add(sq);
  }

  // ---- Sandy harbor shore (right side) ----
  const sand = new THREE.Mesh(new THREE.BoxGeometry(28, 2, 60), MAT.sand);
  sand.position.set(24, 0.5, 0);
  sand.receiveShadow = true;
  world.add(sand);

  // ---- Rocky breakwater (left side) ----
  for(let i=0;i<9;i++){
    const r = new THREE.Mesh(new THREE.BoxGeometry(1.4+Math.random()*0.8, 1.2+Math.random()*0.6, 1.4+Math.random()*0.8), Math.random()>0.5?MAT.rock:MAT.rockDark);
    r.position.set(-22, 0.3, -26 + i*6.5);
    r.rotation.y = Math.random()*0.6;
    r.castShadow = true; r.receiveShadow = true;
    world.add(r);
  }

  // ---- Dock ----
  const dock = new THREE.Group();
  const dockDeck = new THREE.Mesh(new THREE.BoxGeometry(10, 0.6, 14), MAT.dock);
  dockDeck.position.set(14, 1.4, -6);
  dockDeck.castShadow = true; dockDeck.receiveShadow = true;
  dock.add(dockDeck);
  // dock posts
  for(let px of [-4.5, 4.5]){
    for(let pz of [-6, 0, 6]){
      const post = new THREE.Mesh(new THREE.BoxGeometry(0.7, 2.4, 0.7), MAT.dockPost);
      post.position.set(14+px, 0.4, -6+pz);
      post.castShadow = true;
      dock.add(post);
    }
  }
  // containers on dock
  const cont1 = new THREE.Mesh(new THREE.BoxGeometry(2.6,2,2.6), MAT.containerRed);
  cont1.position.set(12, 2.7, -8);
  cont1.castShadow = true;
  dock.add(cont1);
  const cont2 = new THREE.Mesh(new THREE.BoxGeometry(2.6,2,2.6), MAT.containerBlue);
  cont2.position.set(15, 2.7, -8);
  cont2.castShadow = true;
  dock.add(cont2);
  const cont3 = new THREE.Mesh(new THREE.BoxGeometry(2.6,2,2.6), MAT.containerGreen);
  cont3.position.set(12, 2.7, -4);
  cont3.castShadow = true;
  dock.add(cont3);
  const cont4 = new THREE.Mesh(new THREE.BoxGeometry(2.6,2,2.6), MAT.containerYellow);
  cont4.position.set(15, 2.7, -4);
  cont4.castShadow = true;
  dock.add(cont4);

  // small crane
  const craneBase = new THREE.Mesh(new THREE.BoxGeometry(1.2, 3.4, 1.2), MAT.crane);
  craneBase.position.set(18, 3.4, 0);
  craneBase.castShadow = true;
  dock.add(craneBase);
  const craneArm = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.6, 6), MAT.crane);
  craneArm.position.set(18, 5.2, 2.6);
  craneArm.castShadow = true;
  dock.add(craneArm);

  world.add(dock);

  // ---- Lighthouse on rocky point (left) ----
  const lh = new THREE.Group();
  const base = new THREE.Mesh(new THREE.BoxGeometry(3.2, 2, 3.2), MAT.rockDark);
  base.position.set(-20, 1.6, 18);
  base.castShadow = true; base.receiveShadow = true;
  lh.add(base);
  const tower = new THREE.Mesh(new THREE.CylinderGeometry(1.1, 1.4, 6, 8), MAT.lighthouse);
  tower.position.set(-20, 5.2, 18);
  tower.castShadow = true;
  lh.add(tower);
  const stripe = new THREE.Mesh(new THREE.CylinderGeometry(1.22, 1.28, 1.1, 8), MAT.lighthouseRed);
  stripe.position.set(-20, 5.6, 18);
  lh.add(stripe);
  const lantern = new THREE.Mesh(new THREE.CylinderGeometry(0.9, 0.9, 1.1, 8), MAT.window);
  lantern.position.set(-20, 8.7, 18);
  lh.add(lantern);
  const lhRoof = new THREE.Mesh(new THREE.ConeGeometry(1.1, 1.2, 8), MAT.roof);
  lhRoof.position.set(-20, 9.9, 18);
  lhRoof.castShadow = true;
  lh.add(lhRoof);
  world.add(lh);

  // ---- Buoys ----
  function makeBuoy(x,z,phase){
    const b = new THREE.Group();
    const body = new THREE.Mesh(new THREE.CylinderGeometry(0.6,0.75,1.2,6), MAT.buoy);
    body.position.y = 0.4;
    body.castShadow = true;
    b.add(body);
    const band = new THREE.Mesh(new THREE.CylinderGeometry(0.62,0.62,0.3,6), MAT.buoyWhite);
    band.position.y = 0.4;
    b.add(band);
    const pole = new THREE.Mesh(new THREE.BoxGeometry(0.2,1.4,0.2), MAT.roof);
    pole.position.y = 1.6;
    b.add(pole);
    const lightTop = new THREE.Mesh(new THREE.SphereGeometry(0.28,6,6), MAT.window);
    lightTop.position.y = 2.35;
    b.add(lightTop);
    b.position.set(x, 0, z);
    b.userData.phase = phase;
    world.add(b);
    return b;
  }
  const buoys = [makeBuoy(-6,-12,0), makeBuoy(4,14,1.7), makeBuoy(10,-18,3.1)];

  // ---- The ship ----
  const ship = new THREE.Group();
  const hullLength = 16;
  // hull body: layered boxes to suggest taper
  const hullParts = [
    {x:0, w:14, h:1.4, d:4.2},
    {x:-2.2, w:3.2, h:1.4, d:3.0},
    {x: 2.2, w:3.2, h:1.4, d:3.0}
  ];
  hullParts.forEach(p=>{
    const m = new THREE.Mesh(new THREE.BoxGeometry(p.w, p.h, p.d), MAT.hull);
    m.position.set(p.x, 1.1, 0);
    m.castShadow = true; m.receiveShadow = true;
    ship.add(m);
  });
  // hull bottom taper
  const bottom = new THREE.Mesh(new THREE.BoxGeometry(10, 1.1, 2.6), MAT.hullDark);
  bottom.position.set(0, 0.2, 0);
  bottom.castShadow = true;
  ship.add(bottom);
  // deck
  const deck = new THREE.Mesh(new THREE.BoxGeometry(13.6, 0.4, 3.9), MAT.deck);
  deck.position.set(0, 2.0, 0);
  deck.castShadow = true; deck.receiveShadow = true;
  ship.add(deck);
  // bow (front, +x)
  const bow = new THREE.Mesh(new THREE.BoxGeometry(1.6, 1.4, 2.2), MAT.hull);
  bow.position.set(7.0, 1.4, 0);
  bow.castShadow = true;
  ship.add(bow);
  const bowTip = new THREE.Mesh(new THREE.ConeGeometry(1.0, 2.0, 4), MAT.hullDark);
  bowTip.rotation.z = -Math.PI/2;
  bowTip.rotation.y = Math.PI/4;
  bowTip.position.set(8.2, 1.4, 0);
  bowTip.castShadow = true;
  ship.add(bowTip);

  // cabin
  const cabin = new THREE.Mesh(new THREE.BoxGeometry(4.4, 1.7, 2.6), MAT.cabin);
  cabin.position.set(2.4, 3.0, 0);
  cabin.castShadow = true; cabin.receiveShadow = true;
  ship.add(cabin);
  const cabinRoof = new THREE.Mesh(new THREE.BoxGeometry(4.8, 0.35, 2.9), MAT.cabinRoof);
  cabinRoof.position.set(2.4, 3.95, 0);
  cabinRoof.castShadow = true;
  ship.add(cabinRoof);
  // cabin windows
  for(let i=0;i<4;i++){
    const win = new THREE.Mesh(new THREE.BoxGeometry(0.55,0.55,0.08), MAT.window);
    win.position.set(1.0+i*0.95, 3.1, 1.32);
    ship.add(win);
    const win2 = win.clone(); win2.position.z = -1.32;
    ship.add(win2);
  }

  // main mast
  const mastMain = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.28, 7.5, 6), MAT.mast);
  mastMain.position.set(0.3, 5.6, 0);
  mastMain.castShadow = true;
  ship.add(mastMain);
  // fore mast
  const mastFore = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.24, 5.6, 6), MAT.mast);
  mastFore.position.set(5.2, 4.8, 0);
  mastFore.castShadow = true;
  ship.add(mastFore);
  // rear mast
  const mastRear = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.24, 5.0, 6), MAT.mast);
  mastRear.position.set(-4.6, 4.6, 0);
  mastRear.castShadow = true;
  ship.add(mastRear);

  // sails (triangular via ShapeGeometry extruded as voxel slab)
  function makeSail(w, h, color){
    const shape = new THREE.Shape();
    shape.moveTo(0, 0);
    shape.lineTo(0, h);
    shape.lineTo(w, 0);
    shape.lineTo(0, 0);
    const geo = new THREE.ExtrudeGeometry(shape, {depth:0.35, bevelEnabled:false});
    const m = new THREE.Mesh(geo, color);
    m.castShadow = true;
    return m;
  }
  const sailMain = makeSail(3.4, 5.2, MAT.sail);
  sailMain.position.set(0.45, 3.6, -0.18);
  ship.add(sailMain);
  // main sail shading panel
  const sailMainShade = makeSail(2.6, 4.2, MAT.sailShade);
  sailMainShade.position.set(0.5, 3.8, -0.16);
  ship.add(sailMainShade);

  const sailFore = makeSail(2.4, 3.8, MAT.sail);
  sailFore.position.set(5.35, 3.2, -0.18);
  ship.add(sailFore);

  const sailRear = makeSail(2.2, 3.4, MAT.sail);
  sailRear.position.set(-4.45, 3.4, -0.18);
  sailRear.rotation.y = Math.PI;
  ship.add(sailRear);

  // flags
  const flagMain = new THREE.Mesh(new THREE.BoxGeometry(1.5, 0.9, 0.12), MAT.flag);
  flagMain.position.set(1.1, 9.2, 0);
  flagMain.castShadow = true;
  ship.add(flagMain);
  const flagWhiteStripe = new THREE.Mesh(new THREE.BoxGeometry(1.5, 0.25, 0.14), MAT.flagWhite);
  flagWhiteStripe.position.set(1.1, 9.2, 0);
  ship.add(flagWhiteStripe);

  const flagFore = new THREE.Mesh(new THREE.BoxGeometry(1.0, 0.6, 0.12), MAT.flagWhite);
  flagFore.position.set(6.0, 7.2, 0);
  flagFore.castShadow = true;
  ship.add(flagFore);

  // rigging lines (thin boxes)
  function rigging(x1,y1,z1,x2,y2,z2,color){
    const dx=x2-x1, dy=y2-y1, dz=z2-z1;
    const len = Math.sqrt(dx*dx+dy*dy+dz*dz);
    const m = new THREE.Mesh(new THREE.BoxGeometry(0.06,len,0.06), color);
    m.position.set((x1+x2)/2,(y1+y2)/2,(z1+z2)/2);
    m.lookAt(x2,y2,z2);
    m.rotateX(Math.PI/2);
    return m;
  }
  const rigMat = vox(0x3a2a1a);
  ship.add(rigging(0.3, 9.4, 0, 7.0, 2.4, 1.4, rigMat));
  ship.add(rigging(0.3, 9.4, 0, 7.0, 2.4, -1.4, rigMat));
  ship.add(rigging(0.3, 9.4, 0, -7.0, 2.4, 1.4, rigMat));
  ship.add(rigging(0.3, 9.4, 0, -7.0, 2.4, -1.4, rigMat));
  ship.add(rigging(5.2, 7.5, 0, 7.0, 2.4, 0, rigMat));
  ship.add(rigging(-4.6, 7.1, 0, -7.0, 2.4, 0, rigMat));

  // anchor (small)
  const anchor = new THREE.Mesh(new THREE.BoxGeometry(0.4, 1.4, 0.4), MAT.roof);
  anchor.position.set(-7.3, 1.3, 0);
  ship.add(anchor);

  ship.position.set(-2, 0.6, 4);
  ship.rotation.y = -0.18;
  world.add(ship);

  // ---- Clouds (voxel-ish) ----
  function makeCloud(x,y,z,s){
    const c = new THREE.Group();
    const n = 4 + Math.floor(Math.random()*3);
    for(let i=0;i<n;i++){
      const sz = s * (0.5 + Math.random()*0.7);
      const m = new THREE.Mesh(new THREE.BoxGeometry(sz*1.6, sz*0.7, sz), new THREE.MeshLambertMaterial({color:0xffffff, transparent:true, opacity:0.9}));
      m.position.set((Math.random()-0.5)*s*2.2, (Math.random()-0.5)*s*0.6, (Math.random()-0.5)*s*1.2);
      c.add(m);
    }
    c.position.set(x,y,z);
    world.add(c);
    return c;
  }
  const clouds = [makeCloud(-25,22,-30,3), makeCloud(15,26,-38,2.4), makeCloud(-5,30,-50,3.4), makeCloud(35,20,-25,2.2)];

  // ---- Gulls (tiny) ----
  const gulls = [];
  function makeGull(x,y,z){
    const g = new THREE.Group();
    const wingMat = vox(0xffffff);
    const w1 = new THREE.Mesh(new THREE.BoxGeometry(0.9,0.08,0.25), wingMat);
    w1.position.set(-0.45,0,0); w1.rotation.z = 0.25;
    const w2 = new THREE.Mesh(new THREE.BoxGeometry(0.9,0.08,0.25), wingMat);
    w2.position.set(0.45,0,0); w2.rotation.z = -0.25;
    g.add(w1); g.add(w2);
    const body = new THREE.Mesh(new THREE.BoxGeometry(0.35,0.22,0.22), wingMat);
    g.add(body);
    g.position.set(x,y,z);
    world.add(g);
    gulls.push({g, baseY:y, phase:Math.random()*Math.PI*2, speed:0.6+Math.random()*0.4, x, z, r:8+Math.random()*10});
  }
  makeGull(0,16,-8); makeGull(8,19,-14); makeGull(-10,17,-18);

  // ---- Camera controls ----
  let camTheta = 0.6, camPhi = 0.9, camDist = 52;
  const camTarget = new THREE.Vector3(0, 5, 0);
  function updateCamera(){
    camera.position.set(
      camTarget.x + camDist*Math.sin(camPhi)*Math.sin(camTheta),
      camTarget.y + camDist*Math.cos(camPhi),
      camTarget.z + camDist*Math.sin(camPhi)*Math.cos(camTheta)
    );
    camera.lookAt(camTarget);
  }
  updateCamera();

  // Mouse drag orbit
  let dragging=false, lastX=0, lastY=0;
  const dom = renderer.domElement;
  dom.addEventListener('mousedown', e=>{dragging=true; lastX=e.clientX; lastY=e.clientY;});
  window.addEventListener('mouseup', ()=> dragging=false);
  window.addEventListener('mousemove', e=>{
    if(!dragging) return;
    const dx = e.clientX-lastX, dy = e.clientY-lastY;
    camTheta -= dx*0.005;
    camPhi = Math.max(0.15, Math.min(1.45, camPhi - dy*0.005));
    lastX = e.clientX; lastY = e.clientY;
    updateCamera();
  });
  dom.addEventListener('wheel', e=>{
    e.preventDefault();
    camDist = Math.max(18, Math.min(120, camDist + e.deltaY*0.04));
    updateCamera();
  }, {passive:false});

  // Touch
  let touchDist = 0;
  dom.addEventListener('touchstart', e=>{
    if(e.touches.length===1){ dragging=true; lastX=e.touches[0].clientX; lastY=e.touches[0].clientY; }
    if(e.touches.length===2){ touchDist = Math.hypot(e.touches[0].clientX-e.touches[1].clientX, e.touches[0].clientY-e.touches[1].clientY); }
  });
  dom.addEventListener('touchmove', e=>{
    if(e.touches.length===1 && dragging){
      const dx = e.touches[0].clientX-lastX, dy = e.touches[0].clientY-lastY;
      camTheta -= dx*0.005;
      camPhi = Math.max(0.15, Math.min(1.45, camPhi - dy*0.005));
      lastX=e.touches[0].clientX; lastY=e.touches[0].clientY;
      updateCamera();
    } else if(e.touches.length===2){
      const nd = Math.hypot(e.touches[0].clientX-e.touches[1].clientX, e.touches[0].clientY-e.touches[1].clientY);
      const delta = nd - touchDist;
      camDist = Math.max(18, Math.min(120, camDist - delta*0.1));
      touchDist = nd;
      updateCamera();
    }
  });
  dom.addEventListener('touchend', ()=> dragging=false);

  // Click ship to bob
  const raycaster = new THREE.Raycaster();
  const mouse = new THREE.Vector2();
  let bobImpulse = 0;
  dom.addEventListener('click', e=>{
    mouse.x = (e.clientX/window.innerWidth)*2-1;
    mouse.y = -(e.clientY/window.innerHeight)*2+1;
    raycaster.setFromCamera(mouse, camera);
    const hits = raycaster.intersectObject(ship, true);
    if(hits.length) bobImpulse = 1.0;
  });

  window.addEventListener('resize', ()=>{
    camera.aspect = window.innerWidth/window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

  // Animation
  const clock = new THREE.Clock();
  function animate(){
    requestAnimationFrame(animate);
    const t = clock.getElapsedTime();

    // ship bobbing
    bobImpulse = Math.max(0, bobImpulse - 0.012);
    const bob = Math.sin(t*1.1)*0.18 + bobImpulse*Math.sin(t*10)*0.5;
    ship.position.y = 0.6 + bob;
    ship.rotation.z = Math.sin(t*0.9)*0.03 + bobImpulse*Math.sin(t*12)*0.06;
    ship.rotation.x = Math.sin(t*0.7)*0.02;

    // buoys bob
    buoys.forEach(b=>{
      b.position.y = Math.sin(t*1.3 + b.userData.phase)*0.25;
      b.rotation.z = Math.sin(t*1.1 + b.userData.phase)*0.08;
      b.rotation.x = Math.cos(t*0.9 + b.userData.phase)*0.08;
    });

    // clouds drift
    clouds.forEach((c,i)=>{
      c.position.x += 0.012 + i*0.003;
      if(c.position.x > 60) c.position.x = -60;
    });

    // gulls
    gulls.forEach(g=>{
      g.phase += 0.02;
      g.g.position.x = g.x + Math.cos(g.phase)*g.r;
      g.g.position.z = g.z + Math.sin(g.phase)*g.r;
      g.g.position.y = g.baseY + Math.sin(g.phase*2.3)*0.8;
      g.g.rotation.y = -g.phase;
      g.g.rotation.z = Math.sin(g.phase*3.5)*0.35;
    });

    // water subtle pulse
    water.material.opacity = 0.88 + Math.sin(t*0.8)*0.04;

    renderer.render(scene, camera);
  }
  animate();
})();
</script>
</body>
</html>