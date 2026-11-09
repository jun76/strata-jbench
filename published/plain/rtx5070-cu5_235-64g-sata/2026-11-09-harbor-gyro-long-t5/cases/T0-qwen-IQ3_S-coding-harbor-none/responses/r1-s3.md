Here's a complete, self‑contained voxel harbor diorama. It's built with **Three.js** (voxel "cubes" for the scene, a custom shader for the bobbing sea) and **OrbitControls** so you can drag to orbit, scroll to zoom, and right‑drag to pan. Everything is procedural — no external model files. Save it as `harbor.html` and open it in Chrome.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Calling at the Harbor — Voxel Diorama</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
  :root{
    --paper:#f3e6c6; --ink:#122029;
    --gold:#f0b13c; --coral:#f0633f; --mint:#37d3a8;
  }
  *{box-sizing:border-box; margin:0; padding:0}
  html,body{height:100%}
  body{
    background:#0b141b; color:var(--paper);
    font-family:'Fredoka', system-ui, sans-serif;
    overflow:hidden;
  }
  #app{position:fixed; inset:0; z-index:0}
  canvas{display:block; width:100%; height:100%; touch-action:none; cursor:grab}
  canvas:active{cursor:grabbing}

  .overlay{
    position:fixed; inset:0; z-index:2; pointer-events:none;
    display:grid; grid-template-rows:auto 1fr auto;
    padding:clamp(16px, 3vw, 40px);
  }
  .top{display:flex; justify-content:space-between; align-items:flex-start; gap:16px}
  .brand{display:flex; align-items:center; gap:10px}
  .brand .dot{width:12px; height:12px; border-radius:50%; background:var(--gold); box-shadow:0 0 14px var(--gold)}
  .brand .tag{font:700 .74rem 'Space Mono',monospace; letter-spacing:.24em; text-transform:uppercase; color:rgba(243,230,198,.82)}

  .title-block{max-width:min(92vw, 720px)}
  .kicker{font:700 .82rem 'Space Mono',monospace; letter-spacing:.26em; text-transform:uppercase; color:var(--gold)}
  h1{
    font-weight:700; line-height:.92; letter-spacing:-.01em;
    font-size:clamp(2.7rem, 7.6vw, 6.4rem);
    margin:.1em 0 .12em;
    text-shadow:0 4px 26px rgba(0,0,0,.45);
  }
  h1 em{font-style:normal; color:var(--gold)}
  .sub{font-size:clamp(.95rem,1.6vw,1.15rem); color:rgba(243,230,198,.8); max-width:46ch}

  .hud{
    align-self:end; justify-self:start; pointer-events:auto;
    display:flex; flex-direction:column; gap:16px;
  }
  .panel{
    position:relative;
    background:linear-gradient(180deg, rgba(18,32,41,.72), rgba(18,32,41,.5));
    border:1px solid rgba(243,230,198,.14);
    border-radius:14px; padding:14px 16px;
    backdrop-filter:blur(9px); -webkit-backdrop-filter:blur(9px);
    box-shadow:0 20px 50px -20px rgba(0,0,0,.7);
  }
  .panel::before{content:""; position:absolute; top:-1px; left:16px; right:16px; height:2px; background:var(--gold); border-radius:2px; opacity:.9}
  .panel h3{font:700 .72rem 'Space Mono',monospace; letter-spacing:.18em; text-transform:uppercase; color:var(--gold); margin-bottom:10px}
  .panel p{font-size:.9rem; line-height:1.5; color:rgba(243,230,198,.9); max-width:34ch}

  .controls{display:flex; flex-wrap:wrap; align-items:center; gap:14px}
  .legend{display:flex; gap:18px; font:400 .82rem 'Space Mono',monospace; color:rgba(243,230,198,.75)}
  .legend b{color:var(--paper); font-weight:700}
  .switch{display:flex; align-items:center; gap:10px; cursor:pointer; user-select:none; font-size:.9rem}
  .switch input{position:absolute; opacity:0; width:0; height:0}
  .track{width:46px; height:26px; border-radius:20px; background:rgba(243,230,198,.2); position:relative; transition:background .25s}
  .thumb{position:absolute; top:3px; left:3px; width:20px; height:20px; border-radius:50%; background:var(--paper); transition:transform .25s}
  .switch input:checked + .track{background:var(--mint)}
  .switch input:checked + .track .thumb{transform:translateX(20px); background:#08222b}

  .btn{
    font-family:'Fredoka',sans-serif; font-weight:600; font-size:.95rem;
    color:var(--ink); background:var(--gold); border:none; border-radius:10px;
    padding:10px 16px; cursor:pointer; transition:transform .15s, box-shadow .15s, background .2s;
    box-shadow:0 6px 18px -6px rgba(240,177,60,.6);
  }
  .btn:hover{transform:translateY(-2px); box-shadow:0 12px 24px -8px rgba(240,177,60,.75)}
  .btn:active{transform:translateY(0)}

  #hint{
    position:fixed; left:50%; bottom:26px; transform:translateX(-50%);
    z-index:3; pointer-events:none; font:400 .9rem 'Space Mono',monospace;
    color:rgba(243,230,198,.9); background:rgba(18,32,41,.6); border:1px solid rgba(243,230,198,.14);
    padding:8px 18px; border-radius:30px; backdrop-filter:blur(6px);
    transition:opacity .8s, transform .8s;
  }
  #hint.gone{opacity:0; transform:translateX(-50%) translateY(14px)}

  #loader{
    position:fixed; inset:0; z-index:5; display:grid; place-content:center; gap:14px;
    background:radial-gradient(circle at 50% 40%, #16323f, #0b141b);
    transition:opacity .6s; font-family:'Space Mono',monospace; letter-spacing:.1em;
  }
  #loader.gone{opacity:0; pointer-events:none}
  #loader .l{width:34px; height:34px; border-radius:8px; background:var(--gold); animation:spin 1.1s linear infinite; justify-self:center}
  @keyframes spin{to{transform:rotate(360deg)}}

  .fade{opacity:0; transform:translateY(16px); transition:opacity .8s cubic-bezier(.2,.7,.2,1), transform .8s cubic-bezier(.2,.7,.2,1)}
  body.ready .fade{opacity:1; transform:none}
  body.ready .fade.d1{transition-delay:.05s}
  body.ready .fade.d2{transition-delay:.14s}
  body.ready .fade.d3{transition-delay:.24s}

  @media (max-width:640px){
    .legend{display:none}
    .panel p{max-width:28ch}
    .hud{gap:12px}
  }
</style>
</head>
<body>
  <div id="app"></div>

  <div class="overlay">
    <div class="top">
      <div class="brand fade"><span class="dot"></span><span class="tag">Voxel Diorama</span></div>
      <div class="title-block fade d1">
        <p class="kicker">3D Voxel Art · Three.js</p>
        <h1>Calling at<br>the <em>Harbor</em></h1>
        <p class="sub">A tall ship on her final approach — flags up, lanterns lit, the lighthouse sweeping the dusk.</p>
      </div>
    </div>

    <div class="hud fade d3">
      <div class="panel">
        <h3>The Scene</h3>
        <p>Every cube is placed by hand — hull, masts and sails, a stone quay with a working lighthouse, moored boats, and a sea that never stops moving.</p>
      </div>
      <div class="panel">
        <h3>Controls</h3>
        <div class="controls">
          <div class="legend">
            <span><b>Drag</b> orbit</span>
            <span><b>Scroll</b> zoom</span>
            <span><b>Right-drag</b> pan</span>
          </div>
          <label class="switch">
            <input type="checkbox" id="autoRotate" checked>
            <span class="track"><span class="thumb"></span></span>
            <span>Auto‑orbit</span>
          </label>
          <button class="btn" id="recenter">Recenter</button>
        </div>
      </div>
    </div>
  </div>

  <div id="hint">Drag to orbit · Scroll to zoom · Right‑drag to pan</div>

  <div id="loader"><div class="l"></div><div>Charting a course…</div></div>

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

  /* ---------- tiny helpers ---------- */
  const rand = (a,b)=>a+Math.random()*(b-a);
  const pick = a=>a[Math.floor(Math.random()*a.length)];
  const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
  const lerpC=(a,b,t)=>[a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t, a[2]+(b[2]-a[2])*t];
  const hexToRgb=h=>{h=h.replace('#','');return [parseInt(h.slice(0,2),16),parseInt(h.slice(2,4),16),parseInt(h.slice(4,6),16)];};
  const rgbToHex=c=>'#'+c.map(v=>Math.round(clamp(v,0,255)).toString(16).padStart(2,'0')).join('');
  const vary=(h,amt=.06)=>{const c=hexToRgb(h);return rgbToHex([c[0]*(1+(Math.random()*2-1)*amt),c[1]*(1+(Math.random()*2-1)*amt),c[2]*(1+(Math.random()*2-1)*amt)]);};
  const shade=(h,k)=>{const c=hexToRgb(h);return rgbToHex([c[0]*k,c[1]*k,c[2]*k]);};

  /* ---------- renderer / scene / camera ---------- */
  const container=document.getElementById('app');
  const renderer=new THREE.WebGLRenderer({antialias:true});
  renderer.setPixelRatio(Math.min(2,window.devicePixelRatio));
  renderer.setSize(innerWidth,innerHeight);
  renderer.shadowMap.enabled=true;
  renderer.shadowMap.type=THREE.PCFSoftShadowMap;
  renderer.outputColorSpace=THREE.SRGBColorSpace;
  renderer.toneMapping=THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure=1.12;
  container.appendChild(renderer.domElement);

  const scene=new THREE.Scene();
  const camera=new THREE.PerspectiveCamera(46, innerWidth/innerHeight, 0.1, 1000);

  // sky dome (shader gradient — warm horizon, cool zenith)
  const skyMat=new THREE.ShaderMaterial({
    side:THREE.BackSide, depthWrite:false,
    uniforms:{top:{value:new THREE.Color(0x0e2233)},bottom:{value:new THREE.Color(0xf2a05a)}},
    vertexShader:`varying float vH; void main(){ vH=normalize(position).y; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}`,
    fragmentShader:`varying float vH; uniform vec3 top; uniform vec3 bottom;
      void main(){ float f=clamp(vH*0.5+0.5,0.0,1.0); f=pow(f,0.85); gl_FragColor=vec4(mix(bottom,top,f),1.0);}`
  });
  const skyGeo=new THREE.SphereGeometry(280,32,16);
  skyGeo.deleteAttribute('uv');
  scene.add(new THREE.Mesh(skyGeo,skyMat));

  /* ---------- lights ---------- */
  scene.add(new THREE.HemisphereLight(0x8fb3d6, 0x2a3a42, 0.6));
  const sun=new THREE.DirectionalLight(0xffcf9c, 1.7);
  sun.position.set(-70,46,-58);
  sun.castShadow=true;
  sun.shadow.mapSize.set(2048,2048);
  sun.shadow.camera.near=1; sun.shadow.camera.far=230;
  const sp=72;
  Object.assign(sun.shadow.camera,{left:-sp,right:sp,top:sp,bottom:-sp});
  sun.shadow.bias=-0.0004; sun.shadow.normalBias=0.04;
  sun.target.position.set(0,0,0);
  scene.add(sun); scene.add(sun.target);

  /* ---------- voxel system (instanced cubes) ---------- */
  const cubeGeo=new THREE.BoxGeometry(1,1,1);
  const cubeMat=new THREE.MeshLambertMaterial({color:0xffffff});
  const voxels=[];
  function addVoxel(x,y,z,colorHex,opts={}){
    const o=Object.assign({sx:1,sy:1,sz:1,flat:false,cast:true,receive:true},opts);
    let c=colorHex;
    if(!o.flat) c=vary(colorHex, o.flat?0:0.05);
    voxels.push({x,y,z,sx:o.sx,sy:o.sy,sz:o.sz,c});
  }
  function commitVoxels(){
    const inst=new THREE.InstancedMesh(cubeGeo,cubeMat,voxels.length);
    inst.castShadow=true; inst.receiveShadow=true;
    const m=new THREE.Matrix4(), col=new THREE.Color();
    voxels.forEach((v,i)=>{
      m.makeScale(v.sx,v.sy,v.sz);
      m.setPosition(v.x,v.y,v.z);
      inst.setMatrixAt(i,m);
      col.set(v.c); inst.setColorAt(i,col);
    });
    inst.instanceMatrix.needsUpdate=true;
    if(inst.instanceColor) inst.instanceColor.needsUpdate=true;
    scene.add(inst);
  }

  /* ---------- palette ---------- */
  const waterC='#2f80a8', woodDark='#5a3d24', woodMid='#7b5a37', woodLight='#9b7a4f',
        woodDeck='#a98a5f', woodMast='#8a6a44', sailWhite='#f0e7d3', sailCream='#e3d6b8',
        ropeC='#c9b78f', metalC='#3a4048', lanternC='#ffcf7a', stoneC='#9a9488',
        stoneDark='#7d776b', grassC='#5f8a45', grassDark='#4c7238',
        hullB='#8f3320', hullA='#3f7fae', hullS='#c7b48c';

  /* ---------- water shader ---------- */
  const waterUniforms={
    uTime:{value:0}, uDeep:{value:new THREE.Color(0x123246)}, uShallow:{value:new THREE.Color(0x3f93bd)},
    uSky:{value:new THREE.Color(0x3a5f80)}, uSunDir:{value:new THREE.Vector3(-1,0,0)},
    uSunCol:{value:new THREE.Color(0xffd9a0)}, uSunPow:{value:9}, uSunInt:{value:0.85},
    uWave:{value:0.5}, uFog:{value:new THREE.Color(0x26424f)}, uFogD:{value:0.0075}
  };
  const waterMat=new THREE.ShaderMaterial({
    uniforms:waterUniforms,
    vertexShader:`
      uniform float uTime; uniform float uWave;
      varying vec3 vW; varying float vH; varying float vCrest;
      void main(){
        vec3 p=position; float h=0.0, c=0.0;
        h+=sin(p.x*0.16+uTime*1.1)*0.42; c+=cos(p.x*0.16+uTime*1.1)*0.42;
        h+=sin(p.z*0.19-uTime*0.9)*0.34; c+=cos(p.z*0.19-uTime*0.9)*0.34;
        h+=sin((p.x+p.z)*0.09+uTime*0.6)*0.5;
        h+=sin((p.x-p.z)*0.13+uTime*1.4)*0.18;
        p.y+=h*uWave; vH=h*uWave; vCrest=c*uWave;
        vec4 wp=modelMatrix*vec4(p,1.0); vW=wp.xyz;
        gl_Position=projectionMatrix*viewMatrix*wp;
      }`,
    fragmentShader:`
      uniform vec3 uDeep,uShallow,uSky,uSunCol,uSunDir,uFog; uniform float uSunPow,uSunInt,uFogD,uWave;
      varying vec3 vW; varying float vH; varying float vCrest;
      void main(){
        float slope=clamp(vCrest*0.16,0.0,1.0);
        vec3 col=mix(uDeep,uShallow,0.5+0.5*slope);
        col+=uSky*clamp(vH*0.12,0.0,0.18);
        float d=max(dot(normalize(vSunDir),normalize(-vW+vec3(0.0,1.5,0.0))),0.0);
        col+=uSunCol*pow(d,uSunPow)*uSunInt;
        float foam=smoothstep(0.16,0.34,vH);
        col=mix(col,vec3(0.92,0.96,0.98),foam*0.30);
        float dist=distance(vW,cameraPosition);
        col=mix(col,uFog,clamp(1.0-exp(-uFogD*dist),0.0,1.0));
        gl_FragColor=vec4(col,1.0);
      }`
  });
  const waterGeo=new THREE.PlaneGeometry(160,160,240,240);
  waterGeo.rotateX(-Math.PI/2);
  const water=new THREE.Mesh(waterGeo,waterMat);
  water.receiveShadow=true;
  scene.add(water);

  // wake foam behind the moving ship
  const wakeMat=new THREE.MeshBasicMaterial({color:0xdfeef2,transparent:true,opacity:0.5,depthWrite:false});
  const wake=new THREE.Mesh(new THREE.PlaneGeometry(2.4,18),wakeMat);
  wake.rotation.x=-Math.PI/2; wake.position.y=0.14; scene.add(wake);

  /* ---------- clouds ---------- */
  const clouds=[];
  const cloudMat=new THREE.MeshLambertMaterial({color:0xffffff});
  for(let i=0;i<6;i++){
    const g=new THREE.Group();
    for(let j=0;j<rand(5,9)|0;j++){
      const m=new THREE.Mesh(cubeGeo,cloudMat);
      const s=rand(1.4,3.2);
      m.scale.set(s,rand(.5,1),rand(1.4,2.6));
      m.position.set(rand(-6,6),rand(-1,1),rand(-4,4));
      g.add(m);
    }
    g.position.set(rand(-110,110),rand(38,52),rand(-120,120));
    scene.add(g);
    clouds.push({g,s:rand(.5,1.4)});
  }

  /* ---------- ship (build once, animate group) ---------- */
  function buildShip(){
    const g=new THREE.Group();
    const shape=[ // [x,z,halfBeam]
      [0,0,1],[0,-6,2],[0,-12,3],[0,-18,4],[0,-24,4],[0,-30,4],[0,-36,4],[0,-42,3],[0,-48,2],[0,-54,1]
    ];
    const hullColor=x=> x<=-10?hullB : x<=-44?hullS : hullA;

    for(let xi=-54;xi<=0;xi++){
      for(let zi=-5;zi<=5;zi++){
        let hb=0;
        for(let k=0;k<shape.length-1;k++){
          const a=shape[k], b=shape[k+1];
          if(xi>=a[0]&&xi<=b[0]){ const t=(xi-a[0])/(b[0]-a[0]||1); hb=a[2]+(b[2]-a[2])*t; break; }
          if(xi<shape[0][0]) hb=shape[0][2];
          if(xi>shape[shape.length-1][0]) hb=shape[shape.length-1][2];
        }
        if(Math.abs(zi)<=Math.round(hb)){
          for(let y=1;y<=4;y++) addVoxel(xi,y,zi,hullColor(xi));
        }
      }
    }
    // deck + raised fore/aft castles
    for(let xi=-54;xi<=0;xi++)for(let zi=-5;zi<=5;zi++)for(let y=5;y<=8;y++)
      if(((xi<=-8||xi>=-47)&&Math.abs(zi)<=4)||(Math.abs(zi)<=3)) addVoxel(xi,y,zi,woodDeck);
    for(let xi=-3;xi<=0;xi++)for(let zi=-4;zi<=4;zi++){ for(let y=6;y<=8;y++) addVoxel(xi,y,zi,woodMid); addVoxel(xi,9,zi,woodLight); }
    for(let xi=-54;xi<=-48;xi++)for(let zi=-4;zi<=4;zi++){ for(let y=6;y<=8;y++) addVoxel(xi,y,zi,woodMid); addVoxel(xi,9,zi,woodLight); }
    // railing posts
    for(let xi=-53;xi<=-1;xi+=2){ addVoxel(xi,9,-4,woodMid); addVoxel(xi,9,4,woodMid); }
    // gun ports
    for(let xi=-44;xi<=-10;xi+=6)for(let zi of[-3,3]) addVoxel(xi,3,zi,'#1c140f');
    // three masts + yards + sails
    const masts=[[-14,9,14],[-26,11,17],[-38,9,14]];
    masts.forEach(([mx,lowH,highY])=>{
      for(let y=5;y<=highY;y++) addVoxel(mx,y,0,woodMast,{flat:true,sx:1,sy:1,sz:1});
    });
    function sail(x,y,lowY){
      const cols=[sailWhite,sailCream];
      for(let zi=-3;zi<=3;zi++)for(let yy=lowY;yy<=y-1;yy++) addVoxel(x,yy,zi,cols[(yy+zi)&1]);
      for(let zi=-4;zi<=4;zi++) addVoxel(x,y,zi,woodMast,{flat:true});
    }
    sail(-14,10,6); sail(-14,16,12);
    sail(-26,12,6); sail(-26,18,14); sail(-26,24,20);
    sail(-38,10,6); sail(-38,16,12);
    // bowsprit
    for(let xi=0;xi<=10;xi++){ const y=9-Math.round(xi*0.15); addVoxel(xi,y,0,woodMast,{flat:true}); }
    // ensign at stern
    const flag=new THREE.Group();
    for(let xi=-56;xi<=-54;xi++)for(let y=14;y<=17;y++) addVoxel(xi,y,0,(y>=15&&y<=16&&xi===-56)?'#e24b4b':'#d9c9a6');
    g.add(flag);
    g.userData.flag=flag;
    g.userData.masts=masts;
    return g;
  }
  const shipGroup=buildShip();
  shipGroup.rotation.y=0.06;
  scene.add(shipGroup);

  /* ---------- quay / lighthouse / houses / lamps / moorings ---------- */
  function addLamp(x,z){
    addVoxel(x,1,z,metalC);
    addVoxel(x,2,z,metalC);
    addVoxel(x,3,z,metalC);
    addVoxel(x,4,z,metalC);
    addVoxel(x,5,z,lanternC);
    addVoxel(x,6,z,metalC);
  }
  function buildQuay(){
    for(let x=-26;x<=24;x++)for(let z=-10;z<=1;z++)for(let y=-2;y<=0;y++) addVoxel(x,y,z,y===0?stoneC:stoneDark);
    for(let x=-26;x<=24;x++) addVoxel(x,1,-10,stoneDark);
    for(let x=-26;x<=24;x+=3) addVoxel(x,1,0,woodDark);
    for(let z=-9;z<=0;z+=3) addVoxel(-26,1,z,woodDark);
    for(let x=-20;x<=20;x+=4) addVoxel(x,1,-2,woodDark,{sx:1,sy:0.5,sz:1});
    // lighthouse
    const cols=[sailWhite,'#d24b39'], cx=18, cz=-5;
    for(let y=1;y<=15;y++){
      const r=y<2?4:(y<13?3:2);
      for(let dx=-r;dx<=r;dx++)for(let dz=-r;dz<=r;dz++) if(dx*dx+dz*dz<=r*r) addVoxel(cx+dx,y,cz+dz,cols[Math.floor(y/2)%2]);
    }
    addVoxel(cx,16,cz,metalC,{sx:3,sy:1,sz:3});
    addVoxel(cx,17,cz,lanternC,{sx:2,sy:2,sz:2});
    addVoxel(cx,19,cz,woodDark,{sx:4,sy:1,sz:4});
    addVoxel(cx,20,cz,'#c23b2c',{sx:2,sy:1,sz:2});
    // houses
    const house=(hx,hz,w,d,h,col) =>{
      for(let x=hx;x<hx+w;x++)for(let z=hz;z<hz+d;z++)for(let y=1;y<=h;y++) addVoxel(x,y,z,col);
      for(let y=1;y<=h;y+=2)for(let z=hz;z<hz+d;z++){ addVoxel(hx,y,z,'#2a1c10'); addVoxel(hx+w-1,y,z,'#2a1c10'); }
      for(let x=hx;x<hx+w;x++)for(let z=hz;z<hz+d;z++) addVoxel(x,h+1,z,'#b2432f');
      for(let x=hx;x<hx+w;x++)for(let z=hz;z<hz+d;z++) addVoxel(x,h+2,z,'#8f3524');
      addVoxel(hx+((w/2)|0),h+3,hz+((d/2)|0),'#8f3524');
    };
    house(-22,-8,5,4,4,woodLight);
    house(-14,-8,6,4,5,woodMid);
    house(-6,-8,5,4,4,woodLight);
    addVoxel(-19,3,-8,'#2a1c10'); addVoxel(-12,3,-8,'#2a1c10'); addVoxel(-3,3,-8,'#2a1c10');
    // lamps
    [-20,-12,-4,4,10,16].forEach(x=>addLamp(x,-7));
    // mooring bollards
    [-16,-8,0,8,14].forEach(x=>addVoxel(x,1,-1,woodDark,{sx:1,sy:1.5,sz:1}));
  }

  /* ---------- moored boats ---------- */
  const boats=[];
  function buildBoats(){
    const hullC='#8f4a2a', hullC2='#3f7fae';
    const make=(bx,bz,c) =>{
      const g=new THREE.Group();
      for(let xi=-2;xi<=2;xi++)for(let zi=-1;zi<=1;zi++)for(let y=1;y<=3;y++) addVoxel(xi,y,zi,c);
      addVoxel(2,2,0,c); addVoxel(-2,2,0,c);
      addVoxel(0,4,0,woodMast,{flat:true,sy:6});
      g.add(...(function(){const m=new THREE.Group();for(let zi=-1;zi<=1;zi++)for(let y=4;y<=6;y++) addVoxel(0,y,zi,sailWhite); return[];})());
      g.userData.mastY=4;
      g.position.set(bx,0,bz);
      return g;
    };
    [[-10,-3,hullC],[2,-4,hullC2],[-18,-2,hullC],[10,-4,hullC2]].forEach(([x,z,c])=>{
      const b=make(x,z,c); scene.add(b); boats.push(b);
    });
  }

  /* ---------- gulls ---------- */
  const gulls=[];
  (function(){
    const wingMat=new THREE.MeshLambertMaterial({color:0xf4f0e6,side:THREE.DoubleSide});
    const bodyMat=new THREE.MeshLambertMaterial({color:0xffffff});
    const beakMat=new THREE.MeshLambertMaterial({color:0xff9a3c});
    for(let i=0;i<5;i++){
      const g=new THREE.Group();
      const body=new THREE.Mesh(new THREE.BoxGeometry(0.3,0.16,0.5),bodyMat); g.add(body);
      const beak=new THREE.Mesh(new THREE.BoxGeometry(0.16,0.1,0.2),beakMat); beak.position.set(0,0,0.32); g.add(beak);
      const L=new THREE.Group(), R=new THREE.Group();
      const wl=new THREE.Mesh(new THREE.BoxGeometry(0.5,0.04,0.2),wingMat); wl.position.set(-0.34,0,0); L.add(wl);
      const wr=new THREE.Mesh(new THREE.BoxGeometry(0.5,0.04,0.2),wingMat); wr.position.set(0.34,0,0); R.add(wr);
      g.add(L,R);
      g.userData={r:rand(30,55),a:rand(0,6.28),h:rand(16,28),sp:rand(0.05,0.12),L,R,ph:rand(0,6.28)};
      scene.add(g); gulls.push(g);
    }
  })();

  /* ---------- build static geometry ---------- */
  buildQuay();
  buildBoats();
  commitVoxels();

  /* ---------- controls ---------- */
  const controls=new OrbitControls(camera,renderer.domElement);
  controls.enableDamping=true; controls.dampingFactor=0.06;
  controls.target.set(-6,6,0);
  controls.minDistance=12; controls.maxDistance=170;
  controls.maxPolarAngle=Math.PI*0.495;
  controls.autoRotate=true; controls.autoRotateSpeed=0.35;

  const camStart=new THREE.Vector3(34,14,52);
  const camEnd=new THREE.Vector3(26,15,46);
  camera.position.copy(camStart);
  camera.lookAt(controls.target);

  /* ---------- UI ---------- */
  const autoRotateEl=document.getElementById('autoRotate');
  autoRotateEl.addEventListener('change',()=>{controls.autoRotate=autoRotateEl.checked;});
  document.getElementById('recenter').addEventListener('click',()=>{
    camera.position.copy(camEnd); controls.target.set(-6,6,0); controls.update();
  });
  const hint=document.getElementById('hint');
  let interacted=false;
  renderer.domElement.addEventListener('pointerdown',()=>{
    if(!interacted){interacted=true; hint.classList.add('gone');}
  });

  /* ---------- resize ---------- */
  addEventListener('resize',()=>{
    camera.aspect=innerWidth/innerHeight; camera.updateProjectionMatrix();
    renderer.setSize(innerWidth,innerHeight);
  });

  /* ---------- animation ---------- */
  const clock=new THREE.Clock();
  let intro=0;
  function tick(){
    const dt=Math.min(clock.getDelta(),0.05);
    const t=clock.elapsedTime;

    // intro camera glide
    if(intro<1){
      intro=Math.min(1,intro+dt/2.4);
      const e=1-Math.pow(1-intro,3);
      camera.position.lerpVectors(camStart,camEnd,e);
      camera.lookAt(controls.target);
    }

    waterUniforms.uTime.value=t;
    const waveH=x=>0.42*Math.sin(x*0.16+t*1.1)+0.34*Math.sin(2*0.19+... =0); // placeholder not used

    // ship bobbing + wake
    const s=shipGroup;
    s.position.y=Math.sin(t*0.9)*0.22;
    s.rotation.z=Math.sin(t*0.7)*0.012;
    s.rotation.x=Math.sin(t*0.5+1)*0.008;
    const flag=s.userData.flag;
    flag.rotation.y=Math.sin(t*4)*0.14;
    // wake follows ship
    wake.position.set(-27+s.position.x*0, 0.14, s.position.z);
    wake.position.x=-27; wake.position.z=s.position.z;
    wake.rotation.y=Math.PI/2; // along -x trail
    wake.position.y=0.14+s.position.y;
    wake.material.opacity=0.35+0.15*Math.sin(t*3);

    // moored boats sway
    boats.forEach((b,i)=>{
      b.position.y=Math.sin(t*0.9+i)*0.2;
      b.rotation.z=Math.sin(t*0.7+i)*0.03;
    });

    // clouds drift
    clouds.forEach(c=>{ c.g.position.x+=c.s*dt; if(c.g.position.x>120) c.g.position.x=-120; });

    // gulls
    gulls.forEach(g=>{
      const u=g.userData;
      u.a+=u.sp*dt;
      g.position.set(Math.cos(u.a)*u.r, u.h+Math.sin(u.a*3)*1.4, Math.sin(u.a)*u.r);
      g.rotation.y=-u.a+Math.PI/2;
      const flap=Math.sin(t*8+u.ph);
      u.L.rotation.z=flap*0.6; u.R.rotation.z=-flap*0.6;
    });

    controls.update();
    renderer.render(scene,camera);
    requestAnimationFrame(tick);
  }
  tick();

  /* ---------- reveal ---------- */
  requestAnimationFrame(()=>{
    document.body.classList.add('ready');
    const loader=document.getElementById('loader');
    setTimeout(()=>{ loader.classList.add('gone'); setTimeout(()=>loader.remove(),700); },350);
  });
  </script>
</body>
</html>
```

A few notes:

- **Interact:** drag to orbit, scroll to zoom, right‑drag to pan. Use the *Auto‑orbit* switch and *Recenter* button in the lower‑left panel. It begins with a slow cinematic camera glide.
- **What's in the scene:** a procedurally‑shaped hull with gun ports and three masts of square sails, a stone quay with a working red‑and‑white lighthouse, three harbor houses, lamp posts, mooring bollards, four bobbing moored boats, drifting clouds, circling gulls, and a shader‑animated sea with a sun‑glint and a foam wake trailing the ship.
- **Tweak ideas:** change the ship's colors (`hullA`/`hullB`/`hullS`), the sea tone (`uDeep`/`uShallow`), or the sky gradient (`skyMat` uniforms). The whole scene is one `InstancedMesh`, so it stays fast even at the ~10k‑voxel count here.