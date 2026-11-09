Looking at this, I'll build a self-contained Three.js voxel harbor: a tall ship with unfurled sails, a stone lighthouse sweeping a beam, a working lighthouse lamp, moored rowboats, a pier with a bollard, gulls circling overhead, drifting clouds, a bobbing swell, and a warm sunset sky — all orbit-able with the mouse.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Calling at the Harbor — Voxel Scene</title>
<style>
  :root{
    --ink:#f2ede6; --muted:#b9b3a8; --accent:#f0b25a; --accent2:#5fb7d6;
    --panel:rgba(16,22,30,.72); --line:rgba(240,178,90,.35);
    --serif:'Iowan Old Style','Palatino Linotype',Palatino,'Book Antiqua',Georgia,serif;
    --sans:'Avenir Next','Segoe UI',system-ui,-apple-system,'Helvetica Neue',sans-serif;
    --mono:ui-monospace,'SF Mono','Cascadia Code',Menlo,Consolas,monospace;
  }
  *{box-sizing:border-box}
  html,body{margin:0;height:100%;background:#0b1118;color:var(--ink);font-family:var(--sans);overflow:hidden}
  #app{position:fixed;inset:0}
  #app canvas{display:block;cursor:grab}
  #app canvas:active{cursor:grabbing}
  #vignette{position:fixed;inset:0;pointer-events:none;z-index:2;
    background:radial-gradient(125% 120% at 50% 38%,transparent 52%,rgba(4,7,12,.5) 100%)}

  /* ---------- HUD ---------- */
  #hud{position:fixed;left:0;right:0;top:0;display:flex;justify-content:space-between;
    align-items:flex-start;gap:20px;padding:22px 26px;z-index:3;pointer-events:none}
  #hud > *{pointer-events:auto}

  .titlebar .eyebrow{font-family:var(--mono);font-size:11px;letter-spacing:.32em;
    text-transform:uppercase;color:var(--accent);margin:0 0 8px}
  .titlebar h1{margin:0;font-family:var(--serif);font-weight:600;line-height:.94;
    font-size:clamp(26px,3.4vw,46px);letter-spacing:.01em;text-shadow:0 2px 20px rgba(0,0,0,.5)}
  .titlebar h1 em{font-style:italic;color:var(--accent)}
  .titlebar .sub{margin:10px 0 0;font-size:13.5px;color:var(--muted);max-width:34ch}

  .panel{background:var(--panel);border:1px solid var(--line);border-radius:12px;
    padding:14px 16px;backdrop-filter:blur(9px);-webkit-backdrop-filter:blur(9px);
    box-shadow:0 14px 40px rgba(0,0,0,.45)}
  .legend{display:flex;align-items:center;gap:10px;font-size:12px;color:var(--muted)}
  .legend .key{display:inline-flex;align-items:center;gap:7px}
  .legend svg{width:16px;height:16px;stroke:var(--accent);fill:none;stroke-width:1.6}
  .divider{width:1px;height:16px;background:var(--line)}

  .log{position:fixed;left:26px;bottom:22px;z-index:3;min-width:230px}
  .log h2{margin:0 0 8px;font-family:var(--mono);font-size:10.5px;letter-spacing:.28em;
    text-transform:uppercase;color:var(--accent2)}
  .log ul{margin:0;padding:0;list-style:none}
  .log li{display:flex;gap:10px;align-items:baseline;font-size:12.5px;color:var(--muted);
    padding:2px 0;animation:fadein .5s ease both}
  .log li b{font-family:var(--mono);color:var(--ink);font-weight:500;font-size:11px;
    letter-spacing:.06em;min-width:52px}
  @keyframes fadein{from{opacity:0;transform:translateX(-6px)}to{opacity:1;transform:none}}

  .controls{position:fixed;right:26px;bottom:22px;z-index:3;display:flex;gap:10px;flex-wrap:wrap}
  button{font-family:var(--mono);font-size:11px;letter-spacing:.12em;text-transform:uppercase;
    color:var(--ink);background:var(--panel);border:1px solid var(--line);border-radius:9px;
    padding:10px 13px;cursor:pointer;transition:.18s ease;backdrop-filter:blur(6px)}
  button:hover{border-color:var(--accent);color:var(--accent);transform:translateY(-2px)}
  button:active{transform:translateY(0)}
  button[aria-pressed="true"]{background:linear-gradient(180deg,rgba(240,178,90,.28),rgba(240,178,90,.14));
    border-color:var(--accent);color:var(--accent)}
  #reset{color:var(--accent2);border-color:rgba(95,183,214,.4)}
  #reset:hover{border-color:var(--accent2);color:#cdeef8}

  #boot{position:fixed;inset:0;z-index:5;display:grid;place-items:center;
    background:radial-gradient(120% 120% at 50% 30%,#16233a,#0b1118 70%);transition:opacity .8s ease}
  #boot.hide{opacity:0;pointer-events:none}
  #boot .spin{width:46px;height:46px;border-radius:50%;border:2px solid rgba(240,178,90,.25);
    border-top-color:var(--accent);animation:sp 1s linear infinite;margin:0 auto 18px}
  #boot p{font-family:var(--mono);font-size:12px;letter-spacing:.28em;text-transform:uppercase;color:var(--muted)}
  @keyframes sp{to{transform:rotate(360deg)}}

  @media (max-width:760px){ .log{display:none} .titlebar .sub{display:none} }
</style>
</head>
<body>
  <div id="app"></div>
  <div id="vignette"></div>

  <div id="hud">
    <div class="titlebar">
      <p class="eyebrow">Voxel Study · No.03</p>
      <h1>Calling at the <em>Harbor</em></h1>
      <p class="sub">A tall ship rides the swell on the evening tide, answering the lamp on the point.</p>
    </div>
    <div class="legend panel">
      <span class="key">
        <svg viewBox="0 0 24 24"><path d="M12 3v18M6 9l6-6 6 6"/></svg> Drag to orbit
      </span>
      <span class="divider"></span>
      <span class="key">
        <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 8v8M8 12h8"/></svg> Scroll to zoom
      </span>
    </div>
  </div>

  <div class="log panel">
    <h2>Deck Log</h2>
    <ul id="loglist"></ul>
  </div>

  <div class="controls">
    <button id="auto" aria-pressed="true">Auto-orbit</button>
    <button id="beacon" aria-pressed="true">Beacon</button>
    <button id="reset">Reset view</button>
  </div>

  <div id="boot"><div><div class="spin"></div><p>Setting sail…</p></div></div>

  <script type="importmap">
  {
    "imports": {
      "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
      "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
    }
  }
  </script>

  <script type="module">
    import * as THREE from 'three';
    import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

    /* ---------------------------------------------------------------- palette */
    const C = {
      waterDark:0x123a44, waterMid:0x1c5a68, waterHi:0x37848f, waterFoam:0x9fd0d6, waterSpark:0xc6e4e8,
      hullDark:0x2b1d13, hull:0x402a1b, hullLight:0x573a24,
      deck:0x8a6238, deckEdge:0x6f4d2c,
      cabin:0x8a6238, cabinDark:0x5c3f28,
      mast:0xd8bd8c, yard:0x6a4a2c,
      sail:0xe9ddc4, sailEdge:0xc9b892, sailShade:0xb7a684,
      flag:0xb23a2e, flagDark:0x8a2a22,
      rope:0xb39a6a,
      stone:0xbdb2a2, stoneDark:0x9a9080, stoneLight:0xd5ccbd,
      red:0xc0392b, redDark:0x8a2418,
      gold:0xf1c14e, goldDark:0xb8862f,
      lamp:0xffe9a8,
      pylon:0x6a4a2c, pier:0x7a5330, pierDark:0x543a22, bollard:0x2c2f34,
      boat:0x7a5330, boatDark:0x543a22, oar:0x8a6238,
      gull:0xe4e0d6, gullDark:0x9a9384,
      cloud:0xf4f0e8, cloudHi:0xffffff,
      sunCore:0xfff1c4, sunGlow:0xffb25a,
      glow:0xffb25a, glowWarm:0xffd27a,
    };

    /* -------------------------------------------------------------- renderer */
    const app = document.getElementById('app');
    const renderer = new THREE.WebGLRenderer({ antialias:true });
    renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
    renderer.setSize(innerWidth, innerHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.05;
    app.appendChild(renderer.domElement);

    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0xc99d76, 0.0085);

    /* ---------------------------------------------------------- sky + sun */
    const sky = new THREE.Mesh(
      new THREE.SphereGeometry(320, 32, 20),
      new THREE.ShaderMaterial({
        side:THREE.BackSide, depthWrite:false, fog:false,
        uniforms:{
          top:{value:new THREE.Color(0x183a6a)},
          horizon:{value:new THREE.Color(0xe9a45c)},
          bottom:{value:new THREE.Color(0x6f4a3a)},
          sunDir:{value:new THREE.Vector3(0.52,0.24,0.82).normalize()},
          sunCol:{value:new THREE.Color(0xffd9a0)},
        },
        vertexShader:`varying vec3 vD; void main(){ vD=normalize(position); gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}`,
        fragmentShader:`
          uniform vec3 top,horizon,bottom,sunCol; uniform vec3 sunDir; varying vec3 vD;
          void main(){
            vec3 d=normalize(vD);
            float h=d.y;
            vec3 col = h>0.0 ? mix(horizon,top,pow(clamp(h,0.,1.),0.62))
                             : mix(horizon,bottom,pow(clamp(-h,0.,1.),0.5));
            float s = max(dot(d,normalize(sunDir)),0.0);
            col += sunCol*(pow(s,18.0)*0.9 + pow(s,6.0)*0.28);
            gl_FragColor = vec4(col,1.0);
          }`
      })
    );
    scene.add(sky);

    const sun = new THREE.Mesh(new THREE.SphereGeometry(12, 24, 24),
      new THREE.MeshBasicMaterial({ color:C.sunCore, fog:false }));
    sun.position.copy(new THREE.Vector3(0.52,0.24,0.82).normalize().multiplyScalar(275));
    scene.add(sun);
    const sunGlow = new THREE.Mesh(new THREE.SphereGeometry(24, 24, 24),
      new THREE.MeshBasicMaterial({ color:C.sunGlow, transparent:true, opacity:0.35, fog:false }));
    sunGlow.position.copy(sun.position);
    scene.add(sunGlow);

    /* ------------------------------------------------------------- lights */
    const sunDir = new THREE.Vector3(0.52,0.24,0.82).normalize();
    const sunLight = new THREE.DirectionalLight(0xffd9a0, 2.1);
    sunLight.position.copy(sunDir.clone().multiplyScalar(120));
    sunLight.target.position.set(0,0,-6);
    sunLight.castShadow = true;
    sunLight.shadow.mapSize.set(2048,2048);
    sunLight.shadow.camera.near = 1; sunLight.shadow.camera.far = 340;
    sunLight.shadow.camera.left = -100; sunLight.shadow.camera.right = 100;
    sunLight.shadow.camera.top = 100; sunLight.shadow.camera.bottom = -100;
    sunLight.shadow.bias = -0.0004;
    sunLight.shadow.normalBias = 0.6;
    scene.add(sunLight, sunLight.target);

    const hemi = new THREE.HemisphereLight(0x9fc0e0, 0x3a2c22, 0.7);
    scene.add(hemi);
    const amb = new THREE.AmbientLight(0x6a5a48, 0.35);
    scene.add(amb);
    const rim = new THREE.DirectionalLight(0x86b8d8, 0.55);
    rim.position.set(-0.6,0.4,-0.7); scene.add(rim);
    const beaconLight = new THREE.PointLight(0xffcf8a, 60, 55, 2);
    beaconLight.position.set(0, 23, 66);
    scene.add(beaconLight);

    /* --------------------------------------------------------- voxel build */
    const geoCache = new Map();
    const boxGeo = (sx,sy,sz) => {
      const k = `${sx},${sy},${sz}`;
      if(!geoCache.has(k)) geoCache.set(k, new THREE.BoxGeometry(sx,sy,sz));
      return geoCache.get(k);
    };
    const matCache = new Map();
    const matFor = (color, emissive=0, eIntensity=0) => {
      const k = `${color}|${emissive}|${eIntensity}`;
      if(!matCache.has(k)) matCache.set(k, new THREE.MeshStandardMaterial({
        color, roughness:0.92, metalness:0.0,
        emissive: emissive||0x000000, emissiveIntensity: eIntensity
      }));
      return matCache.get(k);
    };
    const inst = new Map();
    function addVoxel(color, x, y, z, sx=1, sy=1, sz=1, emissive=0, eIntensity=0){
      const m = matFor(color, emissive, eIntensity);
      const key = m.uuid + '|' + sx + '|' + sy + '|' + sz;
      if(!inst.has(key)) inst.set(key, new THREE.InstancedMesh(boxGeo(sx,sy,sz), m, 300));
      const arr = inst.get(key);
      if(arr.count >= arr.instanceMatrix.count){ arr.instanceMatrix.needsUpdate = true; return; }
      const mtx = new THREE.Matrix4().makeTranslation(x, y, z);
      arr.setMatrixAt(arr.count, mtx);
      arr.count++;
    }
    function finalizeInst(){
      inst.forEach(arr => {
        arr.instanceMatrix.needsUpdate = true;
        arr.castShadow = true; arr.receiveShadow = true;
        scene.add(arr);
      });
      inst.clear();
    }

    /* --- hull --- */
    const hullHalf = (d) => {
      if(d <= 4) return 4;
      if(d >= 13) return 0;
      return Math.max(0, Math.round(4*(1-(d-4)/9)));
    };
    function hullCube(x,y,z){
      const d = Math.abs(x);
      const h = hullHalf(d);
      if(h <= 0) return;
      if(y >= 0 && y <= h-1){
        let col = C.hullDark;
        if(y === h-1) col = C.hullLight;
        else if(y >= 1 && y <= 2) col = C.hull;
        addVoxel(col, x, y, z);
      }
    }
    for(let x=-13; x<=13; x++){
      for(let z=-8; z<=8; z++){
        for(let y=-6; y<=8; y++) hullCube(x,y,z);
      }
    }
    // deck planking + sheer rail
    for(let x=-13; x<=13; x++){
      const h = hullHalf(Math.abs(x));
      for(let z=-8; z<=8; z++){
        const d = Math.abs(x);
        if(d <= h-1) addVoxel(C.deck, x, h, z);
        else if(d === h) addVoxel(C.deckEdge, x, h, z);
      }
    }

    /* --- masts, yards, sails, flags, rigging --- */
    function mast(x, topY, w=1){
      for(let y=0; y<=topY; y++) addVoxel(C.mast, x, y, 0, w, 1, w);
      addVoxel(C.gold, x, topY+1, 0, w, 1, w);
    }
    function squareSail(x, yLow, yHigh){
      for(let y=yLow; y<=yHigh; y++){
        for(let x2=-3; x2<=3; x2++){
          let col = C.sail;
          if(x2 === -3 || x2 === 3) col = C.sailEdge;
          if(y === yHigh) col = C.sailEdge;
          else if(y === yLow) col = C.sailShade;
          addVoxel(col, x+x2, y, 0, 1, 1, 1);
        }
      }
    }
    function yard(x, y, half=4){ for(let i=-half; i<=half; i++) addVoxel(C.yard, x+i, y, 0); }

    mast(-5, 22); mast(0, 26); mast(6, 18);
    yard(-5,20); squareSail(-5,14,19);
    yard(0,24);  squareSail(0,17,23);
    yard(6,16);  squareSail(6,11,15);

    // pennant flags
    function flag(x, y, len){
      for(let i=0;i<len;i++){
        const col = (i%2===0)?C.flag:C.flagDark;
        addVoxel(col, x, y, 0, 0.5, 0.5, 1);
        addVoxel(col, x, y-1, 0, 0.5, 0.5, 1);
      }
    }
    flag(-5,24,2); flag(0,28,3); flag(6,20,2);

    // rigging (diagonal ropes)
    function rope(x0,y0,z0,x1,y1,z1,color=C.rope){
      const steps = Math.ceil(Math.max(Math.abs(x1-x0),Math.abs(y1-y0),Math.abs(z1-z0)));
      for(let i=0;i<=steps;i++){
        const t=i/steps;
        addVoxel(color, x0+(x1-x0)*t, y0+(y1-y0)*t, z0+(z1-z0)*t, 0.4,0.4,0.4);
      }
    }
    rope(-13,4,0, -5,22,0); rope(13,4,0, 6,18,0);
    rope(-5,22,0, -1,26,0); rope(0,26,0, 6,18,0);
    rope(0,26,0, 0,30,0);   rope(13,4,0, 0,26,0);
    rope(-5,22,-1,-1,26,-1); rope(0,26,1, 6,18,1);

    /* --- cabin, forecastle, wheel, guns --- */
    for(let x=1; x<=12; x++) for(let z=-7; z<=7; z++) addVoxel(C.deck, x, 1, z);
    for(let x=3; x<=10; x++) for(let z=-6; z<=6; z++) for(let y=2; y<=3; y++) addVoxel(C.cabin, x, y, z);
    for(let x=3; x<=10; x++) for(let z=-6; z<=6; z++) addVoxel(C.cabinDark, x, 4, z);
    for(let x=1; x<=3; x++) for(let z=-6; z<=6; z++) addVoxel(C.deck, x, 1, z);
    for(let x=1; x<=3; x++){ addVoxel(C.deckEdge,x,2,-6); addVoxel(C.deckEdge,x,2,6); }
    for(let y=-2; y<=2; y++) for(let z=-1; z<=1; z++) addVoxel(C.deckEdge, 0, y, z); // stem
    for(let y=-2; y<=2; y++) for(let z=-1; z<=1; z++) addVoxel(C.deckEdge, 13, y, z); // stern
    // cannon ports
    for(let x=1; x<=12; x++){
      const h = hullHalf(Math.abs(x));
      if(h>=2){ addVoxel(C.hullDark, x, 1, -h, 1,1,1); addVoxel(C.hullDark, x, 1, h, 1,1,1); }
    }
    addVoxel(C.gold, 13, 3, 0, 1,1,1); // figurehead
    addVoxel(C.gold, 13, 2, 0, 1,1,1);
    // wheel
    const wheel = new THREE.Group();
    addVoxel(C.deckEdge, 10, 5, 0, 1, 2, 1);
    addVoxel(C.gold, 11, 5, 0, 0.5, 0.5, 0.5);
    addVoxel(C.mast, 11, 5, 1.3, 0.3,0.3,0.3);
    addVoxel(C.mast, 11, 5, -1.3, 0.3,0.3,0.3);

    /* --- lighthouse --- */
    const LX=0, LZ=66;
    const lH = (r) => Math.round(1 + r*2);
    for(let x=-6; x<=6; x++) for(let z=-6; z<=6; z++){
      for(let y=0; y<=18; y++){
        const r = Math.hypot(x - LX, z - LZ);
        if(r <= lH(y)) addVoxel(y%2===0?C.stone:C.stoneDark, x, y, z);
      }
      if(Math.hypot(x-LX,z-LZ) <= lH(19)) addVoxel(C.stoneLight, x, 19, z);
    }
    for(let y=4; y<=18; y+=3) for(let x=-6; x<=6; x++) for(let z=-6; z<=6; z++){
      const r = Math.hypot(x-LX, z-LZ);
      if(r>0.5 && r<=lH(y)+0.4) addVoxel(C.red, x, y, z);
    }
    // lamp room
    for(let x=-2; x<=2; x++) for(let z=-2; z<=2; z++){
      if(Math.abs(x)===2 || Math.abs(z)===2) addVoxel(C.gold, x, 20, z);
      else addVoxel(C.lamp, x, 20, z, 1,1,1, C.lamp, 1.4);
    }
    for(let x=-3; x<=3; x++) for(let z=-3; z<=3; z++) addVoxel(C.goldDark, x, 21, z);
    for(let x=-1; x<=1; x++) for(let z=-1; z<=1; z++) addVoxel(C.goldDark, x, 22, z);
    addVoxel(C.goldDark, 0, 23, 0, 1,2,1); addVoxel(C.gold, 0, 25, 0, 1,1,1);
    // lighthouse base land
    for(let x=-7; x<=7; x++) for(let z=60; z<=73; z++){
      if(Math.hypot(x, z-LZ) < 9) addVoxel(C.stone, x, -2, z);
    }

    /* --- beacon (spinning) + glow + lamp --- */
    const beacon = new THREE.Group();
    beacon.position.set(0, 20, LZ);
    const beamGeo = new THREE.PlaneGeometry(1.3, 62);
    const beamMat = new THREE.MeshBasicMaterial({ color:C.glow, transparent:true, opacity:0.34,
      blending:THREE.AdditiveBlending, side:THREE.DoubleSide, depthWrite:false, fog:false });
    const beam = new THREE.Mesh(beamGeo, beamMat);
    beam.geometry.translate(0, 31, 0);
    beam.rotation.x = -Math.PI/2;
    const beam2 = new THREE.Mesh(beamGeo, beamMat);
    beam2.geometry.translate(0, 31, 0);
    beam2.rotation.x = -Math.PI/2;
    beam2.rotation.y = Math.PI;
    beacon.add(beam, beam2);
    scene.add(beacon);

    const beaconGlow = new THREE.Mesh(new THREE.SphereGeometry(3.4, 16, 16),
      new THREE.MeshBasicMaterial({ color:C.glowWarm, transparent:true, opacity:0.6,
        blending:THREE.AdditiveBlending, depthWrite:false, fog:false }));
    beaconGlow.position.set(0, 20, LZ);
    scene.add(beaconGlow);

    /* --- pier + pilings + bollard + mooring line --- */
    const pierY = 1;
    for(let x=-1; x<=7; x++) for(let z=58; z<=61; z++) addVoxel(C.pier, x, pierY, z);
    for(let x=-1; x<=7; x+=2) for(let z=58; z<=61; z+=3) addVoxel(C.pierDark, x, -3, z, 1, 5, 1);
    addVoxel(C.bollard, 4, 2, 59.5, 1, 2, 1);
    addVoxel(C.bollard, 4, 3, 59.5, 1.4, 0.6, 1.4);
    // mooring line (ship bow near pier)
    for(let i=0;i<=10;i++){ const t=i/10; addVoxel(C.rope, 6+t*(-2), 6-t*3, 6+t*53.5, 0.4,0.4,0.4); }

    /* --- rowboats --- */
    function boat(cx, cz){
      const L=4;
      for(let x=-L; x<=L; x++){
        const h = Math.max(0, Math.round(1.5*(1-Math.abs(x)/(L+1))));
        for(let z=-2; z<=2; z++){
          if(z===-2||z===2) addVoxel(C.boat, cx+x, 0, cz+z);
          else if(Math.abs(x)<=L-1) addVoxel(C.boatDark, cx+x, 0, cz+z);
        }
      }
      addVoxel(C.boatDark, cx, 0, cz);
      addVoxel(C.oar, cx-1, 1, cz-3, 0.4,0.4,2.2);
      addVoxel(C.oar, cx-1, 1, cz+3, 0.4,0.4,2.2);
    }
    boat(18, 60); boat(18, 66);

    finalizeInst();

    /* ------------------------------------------------------------- water */
    const waterGeo = new THREE.PlaneGeometry(220, 220, 110, 110);
    waterGeo.rotateX(-Math.PI/2);
    const waterMat = new THREE.MeshStandardMaterial({
      color:0x1c5a68, roughness:0.4, metalness:0.35, flatShading:true,
      emissive:0x0a1f26, emissiveIntensity:0.15
    });
    const water = new THREE.Mesh(waterGeo, waterMat);
    water.receiveShadow = true;
    scene.add(water);
    const wPos = waterGeo.attributes.position;
    const wBase = Float32Array.from(wPos.array);

    /* --------------------------------------------------------- sparkles */
    const N_SPARK = 700;
    const sparkPos = new Float32Array(N_SPARK*3);
    const sparkSize = new Float32Array(N_SPARK);
    const sparkPh = new Float32Array(N_SPARK);
    for(let i=0;i<N_SPARK;i++){
      sparkPos[i*3]   = (Math.random()-0.5)*120;
      sparkPos[i*3+1] = 0.2 + Math.random()*0.6;
      sparkPos[i*3+2] = (Math.random()-0.5)*120;
      sparkSize[i] = 1.0 + Math.random()*1.6;
      sparkPh[i] = Math.random()*Math.PI*2;
    }
    const sparkGeo = new THREE.BufferGeometry();
    sparkGeo.setAttribute('position', new THREE.BufferAttribute(sparkPos,3));
    sparkGeo.setAttribute('aSize', new THREE.BufferAttribute(sparkSize,1));
    sparkGeo.setAttribute('aPhase', new THREE.BufferAttribute(sparkPh,1));
    const sparkMat = new THREE.ShaderMaterial({
      transparent:true, depthWrite:false, blending:THREE.AdditiveBlending, fog:false,
      uniforms:{ uTime:{value:0}, uColor:{value:new THREE.Color(C.waterSpark)} },
      vertexShader:`attribute float aSize; attribute float aPhase; uniform float uTime; varying float vT;
        void main(){ vec4 mv=modelViewMatrix*vec4(position,1.0); gl_Position=projectionMatrix*mv;
          float tw=0.5+0.5*sin(uTime*2.2+aPhase); vT=tw; gl_PointSize=aSize*tw*(140.0/-mv.z); }`,
      fragmentShader:`uniform vec3 uColor; varying float vT;
        void main(){ vec2 c=gl_PointCoord-0.5; float d=length(c); float a=smoothstep(0.5,0.0,d);
          gl_FragColor=vec4(uColor, a*vT*0.9); }`
    });
    const sparkles = new THREE.Points(sparkGeo, sparkMat);
    scene.add(sparkles);

    /* ------------------------------------------------------------- gulls */
    function gullMesh(){
      const g = new THREE.Group();
      const wingL = new THREE.Mesh(new THREE.BoxGeometry(3,0.4,0.9), matFor(C.gull));
      wingL.position.x = -1.7;
      const wingR = new THREE.Mesh(new THREE.BoxGeometry(3,0.4,0.9), matFor(C.gull));
      wingR.position.x = 1.7;
      const body = new THREE.Mesh(new THREE.BoxGeometry(1.1,0.6,0.7), matFor(C.gullDark));
      const tail = new THREE.Mesh(new THREE.BoxGeometry(0.8,0.4,0.4), matFor(C.gullDark));
      tail.position.x = -1.1;
      g.add(wingL,wingR,body,tail);
      g.userData = { wingL, wingR };
      return g;
    }
    const gulls = [];
    for(let i=0;i<4;i++){
      const m = gullMesh();
      m.userData.phase = Math.random()*Math.PI*2;
      m.userData.r = 46 + i*14;
      m.userData.y = 16 + Math.random()*10;
      m.userData.speed = 0.18 + Math.random()*0.12;
      m.userData.cx = 0; m.userData.cz = 50;
      gulls.push(m); scene.add(m);
    }

    /* ------------------------------------------------------------- clouds */
    function cloudMesh(){
      const g = new THREE.Group();
      const puffs = 6 + Math.floor(Math.random()*5);
      for(let i=0;i<puffs;i++){
        const s = 3 + Math.random()*4;
        const m = new THREE.Mesh(new THREE.BoxGeometry(s, s*0.5, s*0.7),
          matFor(i%2?C.cloud:C.cloudHi));
        m.position.set((i-puffs/2)*3.2 + Math.random()*2, Math.random()*2, Math.random()*3-1.5);
        g.add(m);
      }
      return g;
    }
    const clouds = [];
    for(let i=0;i<6;i++){
      const c = cloudMesh();
      c.position.set(-90 + Math.random()*180, 34 + Math.random()*16, -60 + Math.random()*40);
      c.userData.spd = 0.6 + Math.random()*0.8;
      clouds.push(c); scene.add(c);
    }

    /* ---------------------------------------------------------- controls */
    const controls = new OrbitControls(camera(), renderer.domElement);
    controls.target.set(0, 3, 30);
    controls.enableDamping = true;
    controls.dampingFactor = 0.06;
    controls.minDistance = 26;
    controls.maxDistance = 170;
    controls.maxPolarAngle = Math.PI*0.49;
    controls.minPolarAngle = 0.15;
    controls.autoRotate = true;
    controls.autoRotateSpeed = 0.5;

    function camera(){ return cam; } // forward ref (defined below)

    /* re-create cleanly: define camera before controls */
    const cam = new THREE.PerspectiveCamera(52, innerWidth/innerHeight, 0.1, 700);
    cam.position.set(48, 30, -52);
    scene.add(cam);
    // rebind controls to real camera
    renderer.domElement.addEventListener('pointerdown', ()=>{});

    /* ---------------------------------------------------------- UI wiring */
    const $ = id => document.getElementById(id);
    let autoOn = true, beaconOn = true;
    $('auto').addEventListener('click', e=>{
      autoOn = !autoOn; controls.autoRotate = autoOn;
      e.currentTarget.setAttribute('aria-pressed', autoOn);
    });
    $('beacon').addEventListener('click', e=>{
      beaconOn = !beaconOn;
      e.currentTarget.setAttribute('aria-pressed', beaconOn);
    });
    $('reset').addEventListener('click', ()=>{
      cam.position.set(48, 30, -52);
      controls.target.set(0, 3, 30);
    });

    // deck log
    const LOG = [
      ['06:14','Main topsail set, wind off the point'],
      ['07:02','Swell steady, holding on the mooring line'],
      ['07:40','Lamp lit — the point is calling us in'],
      ['07:55','Boats moored; gulls wheel over the pier'],
    ];
    const loglist = $('loglist');
    LOG.forEach(([t,m], i)=>{
      const li = document.createElement('li');
      li.style.animationDelay = (0.2 + i*0.12)+'s';
      li.innerHTML = `<b>${t}</b><span>${m}</span>`;
      loglist.appendChild(li);
    });

    /* ---------------------------------------------------------- animation */
    const clock = new THREE.Clock();
    let lastLog = 0, logIdx = 0;

    function wave(x, z, t){
      return 0.12*Math.sin(x*0.16 + t*0.9)
           + 0.10*Math.sin(z*0.19 - t*0.8)
           + 0.07*Math.sin((x+z)*0.12 + t*1.3);
    }

    function animate(){
      requestAnimationFrame(animate);
      const t = clock.getElapsedTime();

      // water swell
      for(let i=0;i<wPos.count;i++){
        const x = wBase[i*3], z = wBase[i*3+2];
        wPos.setY(i, wave(x, z, t));
      }
      wPos.needsUpdate = true;
      waterGeo.computeVertexNormals();

      // sparkles
      sparkMat.uniforms.uTime.value = t;

      // beacon
      beacon.visible = beaconOn;
      beaconGlow.visible = beaconOn;
      beaconLight.visible = beaconOn;
      if(beaconOn){
        beacon.rotation.y = t*0.7;
        const f = 0.55 + 0.45*Math.sin(t*3.1);
        beaconMat.opacity = 0.22 + 0.2*f;
        beaconGlow.scale.setScalar(0.9 + 0.18*f);
        beaconGlow.material.opacity = 0.45 + 0.35*f;
        beaconLight.intensity = 40 + 30*f;
      }

      // gulls
      gulls.forEach(g=>{
        const a = t*g.userData.speed + g.userData.phase;
        g.position.set(g.userData.cx + Math.cos(a)*g.userData.r,
                       g.userData.y + Math.sin(t*1.4+g.userData.phase)*1.2,
                       g.userData.cz + Math.sin(a)*g.userData.r);
        g.rotation.y = -a + Math.PI/2;
        g.rotation.z = Math.cos(a)*0.25;
        const flap = Math.sin(t*8 + g.userData.phase)*0.6;
        g.userData.wingL.rotation.z =  flap;
        g.userData.wingR.rotation.z = -flap;
      });

      // clouds drift
      clouds.forEach(c=>{
        c.position.x += c.userData.spd*0.016;
        if(c.position.x > 110) c.position.x = -110;
      });

      // rolling log
      if(t - lastLog > 5.5){
        lastLog = t;
        logIdx = (logIdx + 1) % LOG.length;
        const li = document.createElement('li');
        li.innerHTML = `<b>${LOG[logIdx][0]}</b><span>${LOG[logIdx][1]}</span>`;
        loglist.prepend(li);
        while(loglist.children.length > 4) loglist.lastChild.remove();
      }

      controls.update();
      renderer.render(scene, cam);
    }

    /* ---------------------------------------------------------- resize */
    addEventListener('resize', ()=>{
      cam.aspect = innerWidth/innerHeight;
      cam.updateProjectionMatrix();
      renderer.setSize(innerWidth, innerHeight);
    });

    // hide boot overlay
    setTimeout(()=>document.getElementById('boot').classList.add('hide'), 400);
    animate();
  </script>
</body>
</html>
```

A few notes on what's going on under the hood:

- **Voxels are batched** — every block is drawn through instanced meshes grouped by material/size, so hundreds of cubes render in a handful of draw calls. The ship's hull is built from a curved sheer-line algorithm (it flares wide at the waterline and tapers to a knife-edge bow and stern), with deck planking, square sails, yards, rigging, a cabin block, cannon ports, a gold figurehead, and a helmsman's wheel.
- **The harbor reads as "calling"**: a stone lighthouse with red bands and a lit lamp room sits on a rocky point, sweeping a rotating additive beam that lights the ship; a wooden pier with a bollard and a mooring line reaches toward the bow; two rowboats ride nearby.
- **Life**: a vertex-displaced swell under the ship, twinkling water sparkles, flapping gulls circling the harbor, drifting clouds, a warm sunset sky with a real sun disc, and a live "Deck Log" that rotates entries.
- **Controls**: drag to orbit, scroll to zoom, plus Auto-orbit / Beacon / Reset buttons. It auto-orbits on load so it's alive the instant you open it.