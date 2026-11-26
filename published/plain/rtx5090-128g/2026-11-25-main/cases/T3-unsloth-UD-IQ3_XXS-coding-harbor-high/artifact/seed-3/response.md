Below is a complete single-file voxel diorama — a three-masted packet moored inside a stone harbor at golden hour, with a lit lighthouse, terraced hill town, gulls, chimney smoke, a rotating light, a ship that rocks at its moorings, and a time-of-day that repaints the entire world.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>A Sailing Ship Calling at a Harbor — voxel study</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
  :root{
    --ink:#080f13;
    --brass:#d8a94f;
    --paper:#ece3d0;
    --muted:#93a6ac;
  }
  *{box-sizing:border-box}
  html,body{margin:0;height:100%;overflow:hidden;background:#06090b;
    font-family:'IBM Plex Sans',system-ui,sans-serif;color:var(--paper);
    -webkit-font-smoothing:antialiased}
  #scene{position:fixed;inset:0}
  #scene canvas{display:block;width:100%;height:100%;cursor:grab}
  #scene canvas:active{cursor:grabbing}

  /* ---- atmosphere overlays ---- */
  .vig{position:fixed;inset:0;pointer-events:none;z-index:3;
    background:
      radial-gradient(120% 90% at 50% 42%, rgba(0,0,0,0) 42%, rgba(4,7,9,.55) 100%),
      linear-gradient(180deg, rgba(6,10,12,.42) 0%, rgba(0,0,0,0) 22%);}
  .brk{position:fixed;width:26px;height:26px;pointer-events:none;z-index:4;
    border:1px solid rgba(216,169,79,.35);opacity:0;transition:opacity 1.2s ease .5s}
  .brk.on{opacity:1}
  .brk.tl{top:18px;left:18px;border-right:0;border-bottom:0}
  .brk.tr{top:18px;right:18px;border-left:0;border-bottom:0}
  .brk.bl{bottom:18px;left:18px;border-right:0;border-top:0}
  .brk.br{bottom:18px;right:18px;border-left:0;border-top:0}

  /* ---- title plate ---- */
  header{position:fixed;top:34px;left:38px;z-index:6;max-width:min(52vw,620px);pointer-events:none}
  .eyebrow{font-size:10px;letter-spacing:.42em;text-transform:uppercase;color:var(--brass);
    font-weight:500;opacity:0;transform:translateY(10px);transition:.9s cubic-bezier(.2,.8,.2,1)}
  h1{font-family:'Cinzel',serif;font-weight:500;font-size:clamp(27px,3.6vw,52px);line-height:.96;
    margin:.28em 0 .34em;letter-spacing:.005em;opacity:0;transform:translateY(14px);
    transition:1s cubic-bezier(.2,.8,.2,1) .08s;text-shadow:0 6px 30px rgba(0,0,0,.6)}
  h1 em{font-style:normal;font-weight:700;color:var(--brass);
    display:inline-block;padding:0 .04em}
  h1 .thin{font-weight:500;color:rgba(236,227,208,.62)}
  .sub{font-weight:300;font-size:13.5px;line-height:1.55;max-width:44ch;color:rgba(236,227,208,.78);
    opacity:0;transform:translateY(14px);transition:1s cubic-bezier(.2,.8,.2,1) .18s;
    text-shadow:0 3px 16px rgba(0,0,0,.7)}
  body.ready .eyebrow,body.ready h1,body.ready .sub{opacity:1;transform:none}

  /* ---- instrument panel ---- */
  .panel{position:fixed;left:38px;bottom:34px;z-index:6;width:346px;padding:16px 18px 14px;
    background:linear-gradient(180deg,rgba(11,19,23,.80),rgba(7,12,15,.92));
    border:1px solid rgba(216,169,79,.24);border-radius:3px;
    box-shadow:0 22px 60px rgba(0,0,0,.55),inset 0 1px 0 rgba(255,255,255,.05);
    backdrop-filter:blur(8px);opacity:0;transform:translateY(16px);
    transition:1s cubic-bezier(.2,.8,.2,1) .3s}
  body.ready .panel{opacity:1;transform:none}
  .ph{display:flex;align-items:baseline;justify-content:space-between;
    border-bottom:1px solid rgba(216,169,79,.2);padding-bottom:9px;margin-bottom:12px}
  .ph b{font-family:'Cinzel',serif;font-weight:700;font-size:12.5px;letter-spacing:.16em;color:var(--paper)}
  .ph s{text-decoration:none;font-family:'IBM Plex Mono',monospace;font-size:10px;color:var(--muted);letter-spacing:.1em}

  .row{margin:11px 0}
  .row label{display:flex;justify-content:space-between;align-items:baseline;
    font-size:9.5px;letter-spacing:.24em;text-transform:uppercase;color:var(--muted);
    margin-bottom:7px;cursor:default;transition:color .25s}
  .row:hover label{color:var(--brass)}
  .row label i{font-style:normal;font-family:'IBM Plex Mono',monospace;letter-spacing:.04em;
    font-size:11px;color:var(--paper)}
  .ticks{display:flex;justify-content:space-between;font-size:8.5px;letter-spacing:.14em;
    color:rgba(147,166,172,.55);margin-top:5px;text-transform:uppercase}

  input[type=range]{-webkit-appearance:none;appearance:none;width:100%;height:14px;background:transparent;cursor:pointer}
  input[type=range]::-webkit-slider-runnable-track{height:2px;border-radius:2px;
    background:linear-gradient(90deg,#5c4a26,#c99a3d 30%,#e6c073 52%,#8f6b2c 78%,#3d3628)}
  input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:11px;height:16px;margin-top:-7px;
    background:linear-gradient(180deg,#f3dc9c,#c08f34);border:1px solid #2a2114;border-radius:1px;
    box-shadow:0 2px 6px rgba(0,0,0,.6);transition:box-shadow .25s,transform .25s}
  input[type=range]:hover::-webkit-slider-thumb{transform:scaleY(1.14);box-shadow:0 0 14px rgba(224,178,90,.75)}
  input[type=range]::-moz-range-track{height:2px;background:#8f6b2c}
  input[type=range]::-moz-range-thumb{width:10px;height:16px;background:#dcae54;border:1px solid #2a2114;border-radius:1px}

  .btns{display:flex;gap:8px;margin-top:14px}
  .btn{flex:1;font:inherit;font-size:9.5px;letter-spacing:.2em;text-transform:uppercase;
    padding:8px 4px;color:var(--muted);background:rgba(255,255,255,.035);
    border:1px solid rgba(216,169,79,.22);border-radius:2px;cursor:pointer;
    transition:.22s ease;position:relative;overflow:hidden}
  .btn:hover{color:var(--paper);background:rgba(216,169,79,.13);border-color:rgba(216,169,79,.5)}
  .btn:active{transform:translateY(1px)}
  .btn.on{color:#12181a;background:linear-gradient(180deg,#e8c176,#c2913a);border-color:#e8c176;font-weight:600}
  .btn.on:hover{color:#12181a}

  /* ---- live readout ---- */
  .read{position:fixed;right:38px;bottom:34px;z-index:6;text-align:right;
    font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.05em;
    color:rgba(236,227,208,.72);opacity:0;transform:translateY(16px);
    transition:1s cubic-bezier(.2,.8,.2,1) .42s;text-shadow:0 2px 12px rgba(0,0,0,.8)}
  body.ready .read{opacity:1;transform:none}
  .read div{margin:4px 0}
  .read u{text-decoration:none;color:var(--brass)}
  .read .big{font-size:19px;color:var(--paper);letter-spacing:.02em}
  .hint{position:fixed;right:38px;bottom:12px;z-index:6;font-size:9px;letter-spacing:.2em;
    text-transform:uppercase;color:rgba(147,166,172,.5)}

  body.hide .panel,body.hide header,body.hide .read,body.hide .hint,body.hide .brk{
    opacity:0!important;pointer-events:none;transition:opacity .35s}

  /* ---- loader ---- */
  #loader{position:fixed;inset:0;z-index:20;background:#06090b;display:flex;
    align-items:center;justify-content:center;flex-direction:column;gap:22px;
    transition:opacity .9s ease}
  #loader.gone{opacity:0;pointer-events:none}
  #loader p{font-family:'Cinzel',serif;font-size:13px;letter-spacing:.4em;color:var(--brass);
    text-transform:uppercase;margin:0}
  #loader .bar{width:190px;height:1px;background:rgba(216,169,79,.2);overflow:hidden}
  #loader .bar i{display:block;height:100%;width:40%;background:var(--brass);
    animation:sweep 1.15s ease-in-out infinite}
  @keyframes sweep{0%{transform:translateX(-110%)}100%{transform:translateX(320%)}}
  @media (max-width:820px){
    header{left:22px;top:26px;max-width:78vw}
    .panel{left:18px;right:18px;bottom:18px;width:auto}
    .read{right:20px;bottom:auto;top:24px}
  }
</style>
</head>
<body>
<div id="scene"></div>
<div class="vig"></div>
<div class="brk tl"></div><div class="brk tr"></div><div class="brk bl"></div><div class="brk br"></div>

<header>
  <div class="eyebrow">Voxel study nº 3 · rendered live</div>
  <h1>A Sailing Ship <em>calling at</em><br><span class="thin">a Harbor</span></h1>
  <p class="sub">The packet <i>Meridian</i>, forty-seven days out of the west, works the last of the flood
  tide up the sound. Gunports loose, colours loosed, the light coming round the breakwater.</p>
</header>

<div class="panel">
  <div class="ph"><b>HARBOR STATION</b><s id="clock">17:42</s></div>

  <div class="row">
    <label>Hour of day <i id="todLab">GOLDEN</i></label>
    <input id="tod" type="range" min="0" max="1000" value="730">
    <div class="ticks"><span>dawn</span><span>noon</span><span>golden</span><span>night</span></div>
  </div>

  <div class="row">
    <label>Wind <i id="windLab">7 kn · WSW</i></label>
    <input id="wind" type="range" min="0" max="100" value="42">
  </div>

  <div class="btns">
    <button class="btn on" id="btnOrbit">Auto orbit</button>
    <button class="btn" id="btnReset">Starboard bow</button>
  </div>
</div>

<div class="read">
  <div class="big"><u>◈</u> <span id="brg">232°</span></div>
  <div>BEARING <span id="card">SW</span> · ELEV <span id="alt">18</span> M</div>
  <div id="cond">FLOOD +0.9 M · SLACK IN 40′</div>
</div>
<div class="hint">drag orbit · wheel zoom · right-drag pan · H hides panels</div>

<div id="loader"><p>Sounding the channel</p><div class="bar"><i></i></div></div>

<script>
  setTimeout(function(){
    var l=document.getElementById('loader');
    if(l && !l.classList.contains('gone')) l.innerHTML='<p style="letter-spacing:.2em">three.js did not load — check your connection</p>';
  },9000);
</script>

<script type="module">
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';

/* ══════════════════════════ 0. core ══════════════════════════ */
const renderer = new THREE.WebGLRenderer({antialias:true, powerPreference:'high-performance'});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.NoToneMapping;
document.getElementById('scene').appendChild(renderer.domElement);

const scene  = new THREE.Scene();
scene.fog    = new THREE.Fog(0x9fb6bd, 96, 250);
const camera = new THREE.PerspectiveCamera(41, innerWidth/innerHeight, 0.6, 3000);

let seed = 8847712;
const rnd  = ()=> (seed = (seed*1664525 + 1013904223) % 4294967296) / 4294967296;
const rr   = (a,b)=> a + (b-a)*rnd();
const ri   = (a,b)=> Math.floor(a + (b-a+1)*rnd());
const pick = a => a[Math.floor(rnd()*a.length)];
const clamp= (v,a,b)=> v<a?a:v>b?b:v;
const lerp = (a,b,t)=> a+(b-a)*t;
const ss   = (a,b,x)=>{const t=clamp((x-a)/(b-a),0,1);return t*t*(3-2*t);};
const V3   = (x,y,z)=> new THREE.Vector3(x,y,z);

/* palette */
const C = {
  stone0:0xa09a90, stone1:0x8b847a, stone2:0x746d64, cobble:0xb0a695, stoneDress:0xb9b09d,
  dockWood:0x8c6b45, dockWood2:0x6d5236, pile:0x4d3826,
  hull:0x59392a, wale:0x8f5c33, hullUnder:0x33241d, hullIn:0x452e21,
  deckTop:0xc29b63, deck2:0xa9814f, mast:0xbb9c6d, rope:0x3b2c1f,
  sail:0xf4e8cc, sail2:0xdccaa6, sailRed:0xb2452f,
  sand:0xcdb98f, grass0:0x79854c, grass1:0x6a7644, grass2:0x5d6a3d,
  rock0:0x837f77, rock1:0x6d6a63, rock2:0x5a5751,
  wall0:0xe8dcc4, wall1:0xd9caad, wall2:0xc9b795, wall3:0xb89075,
  roof0:0xb15a3d, roof1:0xc0763f, roof2:0x56646f, roof3:0x7d5945,
  timber:0x7b5636, dark:0x2b2119, iron:0x4a4d52, brass:0xc9a24a,
  lamp:0xffc46a, lamp2:0xffe0a0,
  figA:0x2d4b73, figB:0xa83a30, figC:0x3d3a33, skin:0xd9a276,
  red:0xb23c33, blue:0x33608f, white:0xf2eee4, yellow:0xdfb94f, green:0x3f7a52
};

/* ══════════════════════════ 1. builder ══════════════════════════ */
const FACES = [
  {d:[ 1,0,0], c:[[ 1,-1,-1],[ 1, 1,-1],[ 1, 1, 1],[ 1,-1, 1]]},
  {d:[-1,0,0], c:[[-1,-1,-1],[-1,-1, 1],[-1, 1, 1],[-1, 1,-1]]},
  {d:[0, 1,0], c:[[-1, 1,-1],[-1, 1, 1],[ 1, 1, 1],[ 1, 1,-1]]},
  {d:[0,-1,0], c:[[-1,-1,-1],[ 1,-1,-1],[ 1,-1, 1],[-1,-1, 1]]},
  {d:[0,0, 1], c:[[-1,-1, 1],[ 1,-1, 1],[ 1, 1, 1],[-1, 1, 1]]},
  {d:[0,0,-1], c:[[-1,-1,-1],[-1, 1,-1],[ 1, 1,-1],[ 1,-1,-1]]}
];
const DIRSH = [0.84,0.88,1.0,0.50,0.94,0.90];
const AOS   = [0.48,0.72,0.87,1.0];
const KEYB  = 500;
const kkey  = (x,y,z)=> (x+KEYB)*1e6 + (y+KEYB)*1e3 + (z+KEYB);

function newT(){ return {p:[],n:[],c:[],i:[]}; }
function faceInto(T,cx,cy,cz,hx,hy,hz,fi,r,g,b,ao){
  const base = T.p.length/3, f = FACES[fi], sh = DIRSH[fi];
  for(let k=0;k<4;k++){
    const q = f.c[k];
    T.p.push(cx+hx*q[0], cy+hy*q[1], cz+hz*q[2]);
    T.n.push(f.d[0],f.d[1],f.d[2]);
    const m = sh*(ao?ao[k]:1);
    T.c.push(r*m,g*m,b*m);
  }
  T.i.push(base,base+1,base+2, base,base+2,base+3);
}
const colCache = new Map();
function lin(hex){
  let v = colCache.get(hex);
  if(!v){ const c = new THREE.Color(hex); v=[c.r,c.g,c.b]; colCache.set(hex,v); }
  return v;
}
function finish(T){
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(T.p,3));
  g.setAttribute('normal',   new THREE.Float32BufferAttribute(T.n,3));
  g.setAttribute('color',    new THREE.Float32BufferAttribute(T.c,3));
  g.setIndex(T.i);
  T.p=T.n=T.c=T.i=null;
  g.computeBoundingSphere();
  return g;
}

class Builder{
  constructor(){ this.cells = new Map(); this.fines = []; }
  has(x,y,z){ return this.cells.has(kkey(x,y,z)); }
  set(x,y,z,hex,em){
    this.cells.set(kkey(x|0,y|0,z|0), em ? -hex : hex);
  }
  get(x,y,z){ return this.cells.get(kkey(x|0,y|0,z|0)); }
  fill(x0,x1,y0,y1,z0,z1,hex,em){
    for(let x=x0;x<=x1;x++) for(let y=y0;y<=y1;y++) for(let z=z0;z<=z1;z++) this.set(x,y,z,hex,em);
  }
  add(cx,cy,cz,hx,hy,hz,hex,em){ this.fines.push({cx,cy,cz,hx,hy,hz,hex,em:!!em}); }
  bar(a,b,size,hex){
    const len = a.distanceTo(b), n = Math.max(1, Math.ceil(len/0.6));
    for(let i=0;i<=n;i++){
      const t=i/n, p=a.clone().lerp(b,t);
      this.add(p.x,p.y,p.z,size,size,size,hex);
    }
  }
  line(a,b,size,hex,sag){
    const len=a.distanceTo(b), n=Math.max(1,Math.ceil(len/0.85));
    for(let i=0;i<=n;i++){
      const t=i/n, p=a.clone().lerp(b,t);
      p.y -= (sag||0)*Math.sin(Math.PI*t);
      this.add(p.x,p.y,p.z,size,size,size,hex);
    }
  }
  build(litMat, glowMat){
    const L=newT(), G=newT();
    for(const [k,val] of this.cells){
      const kk = k, z = (kk%1000)-KEYB, t1=(kk-z-KEYB*1)/1000, y=(t1%1000)-KEYB,
                      x=((t1-y-KEYB*1)/1000)-KEYB;
      const em = val<0, T = em?G:L, col = lin(Math.abs(val));
      for(let fi=0;fi<6;fi++){
        const d=FACES[fi].d;
        if(this.cells.has(kkey(x+d[0],y+d[1],z+d[2]))) continue;
        const ao=[1,1,1,1];
        if(!em){
          const f=FACES[fi];
          for(let q=0;q<4;q++){
            const cc=f.c[q], t=[];
            for(let a=0;a<3;a++) if(d[a]===0) t.push(a);
            const A=t[0],B=t[1];
            const s1=off(x,y,z,d,cc,A), s2=off(x,y,z,d,cc,B);
            const sc=off2(x,y,z,d,cc,A,B);
            ao[q]=AOS[(s1&&s2)?0:3-(s1+s2+sc)];
          }
        }
        faceInto(T,x,y,z,0.5,0.5,0.5,fi,col[0],col[1],col[2],ao);
      }
    }
    for(const f of this.fines){
      const col = lin(f.hex);
      for(let fi=0;fi<6;fi++) faceInto(f.em?G:L, f.cx,f.cy,f.cz, f.hx,f.hy,f.hz, fi, col[0],col[1],col[2], null);
    }
    const grp = new THREE.Group();
    if(L.p===null || true){
      const gm = finish(L);
      if(gm.attributes.position.count){
        const m = new THREE.Mesh(gm, litMat);
        m.castShadow = true; m.receiveShadow = true; grp.add(m);
      }
      const gg = finish(G);
      if(gg.attributes.position.count){
        const m2 = new THREE.Mesh(gg, glowMat);
        m2.castShadow = false; grp.add(m2);
      }
    }
    this.cells.clear(); this.fines.length = 0;
    return grp;
    function off(x,y,z,d,cc,a){
      const o=[0,0,0]; o[a]=cc[a];
      return 0; // replaced below
    }
  }
}
/* AO helper (kept outside for speed) */
function aoOf(cells, x,y,z, fi, q){
  const f = FACES[fi], d = f.d, cc = f.c[q];
  const A = d[0]===0?0:(d[1]===0?1:2);
  const B = A===0 ? (d[1]===0?1:2) : (A===1 ? (d[2]===0?2:1) : 1);
  const o1=[0,0,0], o2=[0,0,0]; o1[A]=cc[A]; o2[B]=cc[B];
  const s1 = cells.has(kkey(x+d[0]+o1[0], y+d[1]+o1[1], z+d[2]+o1[2]))?1:0;
  const s2 = cells.has(kkey(x+d[0]+o2[0], y+d[1]+o2[1], z+d[2]+o2[2]))?1:0;
  const sc = cells.has(kkey(x+d[0]+o1[0]+o2[0], y+d[1]+o1[1]+o2[1], z+d[2]+o1[2]+o2[2]))?1:0;
  return AOS[(s1&&s2)?0:3-(s1+s2+sc)];
}
/* patch build() to use the fast helper */
Builder.prototype.build = function(litMat, glowMat){
  const L=newT(), G=newT(), cells=this.cells;
  for(const [k,val] of cells){
    const z=(k%1000)-KEYB, t1=(k-z-KEYB)/1000, y=(t1%1000)-KEYB, x=((t1-y-KEYB)/1000)-KEYB;
    const em = val<0, T = em?G:L, col = lin(Math.abs(val));
    for(let fi=0;fi<6;fi++){
      const d=FACES[fi].d;
      if(cells.has(kkey(x+d[0],y+d[1],z+d[2]))) continue;
      let ao=null;
      if(!em){ ao=[aoOf(cells,x,y,z,fi,0),aoOf(cells,x,y,z,fi,1),aoOf(cells,x,y,z,fi,2),aoOf(cells,x,y,z,fi,3)]; }
      faceInto(T,x,y,z,0.5,0.5,0.5,fi,col[0],col[1],col[2],ao);
    }
  }
  for(const f of this.fines){
    const col=lin(f.hex);
    for(let fi=0;fi<6;fi++) faceInto(f.em?G:L, f.cx,f.cy,f.cz,f.hx,f.hy,f.hz, fi, col[0],col[1],col[2], null);
  }
  const grp=new THREE.Group();
  const gl=finish(L);
  if(gl.attributes.position.count){ const m=new THREE.Mesh(gl,litMat); m.castShadow=true;m.receiveShadow=true;grp.add(m);}
  const gg=finish(G);
  if(gg.attributes.position.count){ const m=new THREE.Mesh(gg,glowMat); grp.add(m); }
  cells.clear(); this.fines.length=0;
  return grp;
};

/* ══════════════════════════ 2. materials & lights ══════════════════════════ */
const litMat  = new THREE.MeshLambertMaterial({vertexColors:true});
const glowMat = new THREE.MeshBasicMaterial({vertexColors:true, fog:true});
const sun = new THREE.DirectionalLight(0xffd9a8, 1.85);
sun.position.set(180,60,120); sun.castShadow = true;
sun.shadow.mapSize.set(2048,2048);
sun.shadow.camera.left=-110; sun.shadow.camera.right=110;
sun.shadow.camera.top=110;   sun.shadow.camera.bottom=-110;
sun.shadow.camera.near=10;   sun.shadow.camera.far=520;
sun.shadow.bias=-0.0004; sun.shadow.normalBias=0.55;
scene.add(sun, sun.target);
const hemi = new THREE.HemisphereLight(0x9fc2d8, 0x6b5b45, 0.65); scene.add(hemi);
const bounce = new THREE.DirectionalLight(0x7fa8c8, 0.30); bounce.position.set(-120,50,-90); scene.add(bounce);
const lampLights = [];
for(const p of [ [4,7,-9], [-14,8,-8], [-26,7,-10], [24,17,15], [0,9,-22] ]){
  const pl = new THREE.PointLight(0xffb763, 0, 34, 2.0);
  pl.position.set(p[0],p[1],p[2]); scene.add(pl); lampLights.push(pl);
}

/* ══════════════════════════ 3. sky ══════════════════════════ */
const skyU = {
  cTop:{value:new THREE.Color(0x1b3f66)}, cMid:{value:new THREE.Color(0x6f8fae)},
  cBot:{value:new THREE.Color(0xffc089)}, uSun:{value:new THREE.Vector3(0.6,0.2,0.5)},
  uSunCol:{value:new THREE.Color(0xffd7a0)}, uNight:{value:0}, uTime:{value:0}
};
const sky = new THREE.Mesh(new THREE.SphereGeometry(1400,32,20), new THREE.ShaderMaterial({
  side:THREE.BackSide, depthWrite:false, uniforms:skyU,
  vertexShader:`varying vec3 vD; void main(){ vD=normalize(position); gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);} `,
  fragmentShader:`
    varying vec3 vD; uniform vec3 cTop,cMid,cBot,uSun,uSunCol; uniform float uNight,uTime;
    float h21(vec2 p){ p=fract(p*vec2(123.34,456.21)); p+=dot(p,p+45.32); return fract(p.x*p.y); }
    void main(){
      vec3 d=normalize(vD); float y=d.y;
      vec3 col = mix(cBot,cMid,smoothstep(-0.02,0.34,y));
      col = mix(col,cTop,smoothstep(0.24,0.86,y));
      float s=max(dot(d,normalize(uSun)),0.0);
      col += uSunCol*pow(s,900.0)*3.2;
      col += uSunCol*pow(s,14.0)*0.30;
      col += uSunCol*pow(s,3.0)*0.07;
      if(uNight>0.01 && y>-0.02){
        vec2 sp=vec2(atan(d.z,d.x)*96.0, asin(clamp(d.y,-1.0,1.0))*150.0);
        float hh=h21(floor(sp));
        float st=step(0.9835,hh);
        float tw=0.55+0.45*sin(uTime*2.4+hh*62.0);
        col += vec3(0.85,0.90,1.0)*st*tw*uNight*smoothstep(-0.02,0.35,y)*1.5;
      }
      gl_FragColor=vec4(pow(clamp(col,0.0,1.5),vec3(0.4545)),1.0);
    }`
}));
sky.frustumCulled=false; sky.renderOrder=-10; scene.add(sky);

/* ══════════════════════════ 4. terrain field ══════════════════════════ */
const pads = [];
function noiseH(x,z){
  return 1.35*Math.sin(x*0.071+0.3)*Math.cos(z*0.058) + 0.9*Math.sin(x*0.021-z*0.043)
       + 0.55*Math.sin(x*0.19)*Math.sin(z*0.17) + 0.35*Math.sin(x*0.31+z*0.27);
}
function rawLand(x,z){
  let h = -7;
  const edge = -13 + 10*Math.sin(x*0.031+0.4) + 5*Math.sin(x*0.083+2.1);
  const t1 = ss(edge+3, edge-1, z);
  let hm = 4.6 + Math.max(0,(-13-z))*0.115 + noiseH(x,z)*1.15;
  hm += 9.5*Math.exp(-(((x+14)**2 + (z+78)**2)/1500));
  hm += 7.5*Math.exp(-(((x-34)**2 + (z+62)**2)/1100));
  hm += 6.0*Math.exp(-(((x+70)**2 + (z+52)**2)/1200));
  h = Math.max(h, lerp(-7, hm, t1));
  const hx=(x+62)/30, hz=(z+16)/26, hd=Math.sqrt(hx*hx+hz*hz);
  if(hd<1.25){
    let hl = 1.5 + 23*Math.pow(Math.max(0,1-hd*0.92),0.52) + noiseH(x*1.7,z*1.7)*1.9;
    h = Math.max(h, lerp(-7, hl, ss(1.2,0.82,hd)));
  }
  const ex=(x-62)/24, ez=(z+36)/30, ed=Math.sqrt(ex*ex+ez*ez);
  if(ed<1.2){
    let el = 2 + 9*Math.pow(Math.max(0,1-ed*0.94),0.6) + noiseH(x*1.4,z*1.4);
    h = Math.max(h, lerp(-7, el, ss(1.15,0.85,ed)));
  }
  const dr = Math.sqrt((x*0.94)**2 + (z+40)**2);
  h = lerp(-7, h, 1-ss(82,124,dr));
  return h;
}
function addPad(cx,cz,w,d,dy){
  const y = Math.round(rawLand(cx,cz) + (dy||0));
  pads.push({x0:Math.round(cx-w/2), x1:Math.round(cx+w/2), z0:Math.round(cz-d/2), z1:Math.round(cz+d/2), y});
  return y;
}
function padAt(x,z){
  for(let i=0;i<pads.length;i++){const p=pads[i];
    if(x>=p.x0&&x<=p.x1&&z>=p.z0&&z<=p.z1) return p.y;}
  return null;
}
function land(x,z){ const p=padAt(x,z); return p!==null?p:Math.round(rawLand(x,z)); }

/* ══════════════════════════ 5. world ══════════════════════════ */
const W = new Builder();
const QUAY_Y = 4, QUA = {x0:-34,x1:26,z0:-34,z1:-14};

function townLayout(){
  const lots=[];
  const churchY = addPad(-6,-43,10,10);
  lots.push({t:'church',x:-6,z:-43,y:churchY});
  const windY = addPad(-46,-52,9,9,2);
  lots.push({t:'wind',x:-46,z:-52,y:windY});
  let tries=0;
  while(lots.length<26 && tries<400){
    tries++;
    const x=rr(-70,30), z=rr(-74,-20);
    if(x>QUA.x0 && x<QUA.x1 && z>QUA.z0-2) continue;
    if(Math.hypot(x+40,z+8) < 34) continue;
    const raw=rawLand(x,z);
    if(raw<4.5 || raw>21) continue;
    let ok=true;
    for(const l of lots){ if(Math.hypot(l.x-x,l.z-z)<12.5){ok=false;break;} }
    if(!ok) continue;
    const w=ri(5,9), d=ri(5,8), y=addPad(x,z,w+2,d+2,0);
    lots.push({t:'house',x,z,w,d,y});
  }
  return lots;
}
const LOTS = townLayout();

/* terrain voxels */
function buildTerrain(){
  for(let x=-124;x<=124;x++){
    for(let z=-150;z<=34;z++){
      if(x>=QUA.x0&&x<=QUA.x1&&z>=QUA.z0&&z<=QUA.z1) continue;
      const h = land(x,z);
      if(h<=0) continue;
      const zSeaward = land(x,z+1), zNext = land(x,z+2);
      let step = 2;
      if(zSeaward>h) step = Math.max(step, zSeaward-h);
      else if(zNext>h) step = Math.max(step, zNext-h);
      step = Math.min(step, 9);
      const y0 = Math.max(-1, h-step);
      const steep = step>=3;
      const beach = h<=2;
      for(let y=y0;y<=h;y++){
        let c;
        if(y===h){
          c = beach ? C.sand : steep ? pick([C.rock0,C.rock1,C.rock2]) : pick([C.grass0,C.grass1,C.grass2]);
        } else if(y>=h-1){
          c = steep ? pick([C.rock1,C.rock2,C.rock0]) : (beach?C.sand:pick([C.grass1,C.rock2,C.grass2]));
        } else {
          c = pick([C.rock1,C.rock2,C.stone2]);
        }
        W.set(x,y,z,c);
      }
    }
  }
  /* distant islets on the horizon */
  for(const isle of [[-104,62,9,7],[-72,96,12,6],[86,84,10,5],[118,26,8,6]]){
    const [ix,iz,r,hh]=isle;
    for(let x=ix-r;x<=ix+r;x++) for(let z=iz-r;z<=iz+r;z++){
      const dd=Math.hypot(x-ix,z-iz); if(dd>r) continue;
      const top = Math.round(hh*Math.pow(1-dd/r,0.7)+rr(-0.4,0.6));
      for(let y=-1;y<=top;y++) W.set(x,y,z, y===top?pick([C.grass2,C.rock1]):C.rock2);
    }
  }
}

/* quay + harbour works */
function buildQuay(){
  for(let x=QUA.x0;x<=QUA.x1;x++) for(let z=QUA.z0;z<=QUA.z1;z++){
    for(let y=-9;y<=QUAY_Y;y++){
      let c;
      if(y===QUAY_Y) c = ((x+z)%2===0)?C.cobble:C.stone0;
      else c = pick([C.stone1,C.stone2,C.stone0]);
      W.set(x,y,z,c);
    }
  }
  /* dressed wall face at z = QUAY.z0 */
  for(let x=QUA.x0;x<=QUA.x1;x++){
    for(let y=-8;y<=QUAY_Y;y++){
      const band = ((x%5)+5)%5;
      W.set(x,y,QUA.z0, (y%3===0&&band<3)?C.stoneDress:pick([C.stone1,C.stone2,C.stone0]));
    }
  }
  /* wall buttresses into the sea */
  for(let x=QUA.x0+4;x<=QUA.x1-2;x+=11){
    for(let z=QUA.z0-3;z<=QUA.z0;z++) for(let y=-9;y<=QUAY_Y-2;y++)
      if(rnd()>0.22) W.set(x,y,z, pick([C.stone1,C.stone2,C.rock1]));
  }
  /* slipway steps down into the water */
  for(let i=0;i<4;i++) for(let zz=0;zz<3;zz++)
    W.fill(14+i*3,16+i*3, QUAY_Y-1-zz, QUAY_Y-1-zz, QUA.z0-1-zz, QUA.z0-1-zz, C.stoneDress);

  /* bollards, cleats, lamps on posts */
  for(let x=QUA.x0+3; x<=QUA.x1-1; x+=7){
    const B=W;
    B.add(x,QUAY_Y+1,-13.4,0.45,1.0,0.45,C.pile);
    B.add(x,QUAY_Y+2.15,-13.4,0.62,0.25,0.62,C.dockWood2);
  }
  for(const lx of [-27,-14,-1,12,23]){
    W.add(lx,QUAY_Y+2.4,-31.5,0.22,2.4,0.22,C.timber);
    W.add(lx,QUAY_Y+4.9,-31.5,0.7,0.55,0.7,C.iron);
    W.fill(lx-1,lx+1,QUAY_Y+4.6,QUAY_Y+4.6,-32.5,-30.5,C.iron);
    for(const zz of [-32,-31,-30]) for(let yy=0;yy<3;yy++) W.set(lx-1+zz+31, QUAY_Y+5.0-yy, zz, 0x000000);
    W.set(lx,QUAY_Y+4.3,-31.5,C.lamp,true);
  }
  /* crates, barrels, nets, fish stall */
  for(let i=0;i<26;i++){
    const x=rr(QUA.x0+2,QUA.x1-3), z=rr(QUA.z0+1.5,-16);
    const t=rnd();
    if(t<0.42){
      const s=rr(0.9,1.5);
      W.add(x,QUAY_Y+s,z,s*0.8,s,rr(0.9,1.4), pick([C.dockWood,C.dockWood2]));
      W.add(x,QUAY_Y+s+0.06,z,s*0.82,0.06,rr(0.92,1.42), pick([C.dockWood2,C.timber]));
    } else if(t<0.72){
      const r=rr(0.8,1.05), h=rr(1.4,1.9);
      W.add(x,QUAY_Y+h/2,z,r,h/2,r*0.95,C.dockWood2);
      W.add(x,QUAY_Y+h*0.72,z,r*1.03,0.12,r*0.98,C.iron);
      W.add(x,QUAY_Y+h*0.28,z,r*1.03,0.12,r*0.98,C.iron);
    } else {
      W.fill(Math.round(x-2),Math.round(x+2),QUAY_Y+1,QUAY_Y+3,Math.round(z-1),Math.round(z+1),
             pick([C.wall1,C.wall2,C.timber]));
    }
  }
  /* the custom house on the quay */
  house(-26,-19, 11, 9, 7, QUAY_Y, 0, true);
  /* derrick crane on the quay */
  const cx=8, cz=-19;
  W.add(cx,QUAY_Y+3.2,cz,0.7,3.2,0.7,C.timber);
  W.bar(V3(cx,QUAY_Y+6.0,cz), V3(cx+8,QUAY_Y+9.2,cz), 0.42, C.timber);
  W.bar(V3(cx,QUAY_Y+4.2,cz), V3(cx+7.2,QUAY_Y+8.6,cz), 0.14, C.rope);
  W.bar(V3(cx+7.6,QUAY_Y+9.0,cz), V3(cx+7.6,QUAY_Y+5.4,cz), 0.1, C.rope);
  W.add(cx+7.6,QUAY_Y+5.0,cz,0.35,0.35,0.35,C.iron);
  W.add(cx+2,QUAY_Y+1.2,cz,1.6,1.2,1.6,C.dockWood);

  /* figures on the quay */
  const figCols=[C.figA,C.figB,C.figC,C.green,C.red];
  for(let i=0;i<12;i++){
    const x=rr(QUA.x0+2,QUA.x1-2), z=rr(QUA.z0+1,-16.5);
    figure(W, x, QUAY_Y+1, z, pick(figCols));
  }
  /* mooring line stubs */
  for(const bx of [-8,4,16]){
    W.bar(V3(bx,QUAY_Y+2.1,-13.4), V3(bx*0.55,QUAY_Y+0.2,-8.4), 0.13, C.rope, 1.2);
  }
}
function figure(B,x,y,z,coat){
  B.add(x,y+0.5,z,0.28,0.5,0.28,C.figC);
  B.add(x,y+1.35,z,0.36,0.42,0.3,coat);
  B.add(x,y+1.95,z,0.24,0.24,0.24,C.skin);
}
function house(x,z,w,d,baseY,overrideWall,big){
  const y0 = land(x,z)+1;
  const h = 4+ri(0,3);
  const wall = overrideWall===0 ? C.wall1 : pick([C.wall0,C.wall1,C.wall2,C.wall3]);
  const roofC = pick([C.roof0,C.roof1,C.roof3,C.roof2]);
  const alongX = w>=d;
  const topY = y0+h;
  /* walls */
  for(let i=x-w>>0;i<=x+(w>>0);i++) for(let k=z-(d>>0);k<=z+(d>>0);k++){
    const edge = (i===x-(w>>0)||i===x+(w>>0)||k===z-(d>>0)||k===z+(d>>0));
    if(!edge){ W.fill(i,i,y0,topY-1,k,k,C.dark); continue; }
    W.fill(i,i,y0,topY-1,k,k,wall);
  }
  /* windows + door */
  for(let i=x-(w>>0)+2;i<=x+(w>>0)-2;i+=3){
    for(const k of [z-(d>>0), z+(d>>0)]){
      const lit = rnd()<0.55;
      W.fill(i,i+1,y0+2,y0+3,k,k, lit?C.lamp:0x2c3238, lit);
    }
  }
  for(let k=z-(d>>0)+2;k<=z+(d>>0)-2;k+=3){
    for(const i of [x-(w>>0), x+(w>>0)]){
      const lit = rnd()<0.4;
      W.fill(i,i,y0+2,y0+3,k,k, lit?C.lamp:0x2c3238, lit);
    }
  }
  W.fill(x,x,y0,y0+2, z+(d>>0), z+(d>>0), C.timber);
  /* roof */
  let hw = (w>>0)+1, hd=(d>>0)+1;
  let ry = topY;
  while(hw>0 && hd>0){
    for(let i=x-hw;i<=x+hw;i++) for(let k=z-hd;k<=z+hd;k++){
      const edge=(i===x-hw||i===x+hw||k===z-hd||k===z+hd);
      if(edge||hw<=1||hd<=1) W.fill(i,i,ry,ry,k,k, ((i+k)&1)?roofC:shadeRoof(roofC));
      else W.fill(i,i,ry,ry,k,k,C.dark);
    }
    ry++; hw--; hd--;
  }
  W.fill(x-1,x+1,ry,ry,z-1,z+1, roofC);
  /* chimney + anchor mark */
  const chimX=x-(w>>0)+1, chimZ=z+(d>>0)-1;
  W.fill(chimX,chimX, topY-1, ry+1, chimZ, chimZ, C.stone2);
  W.set(chimX,ry+1,chimZ,0x35302b);
  if(big){
    W.bar(V3(x+4,baseY+1,z+d/2+1), V3(x+4,baseY+11,z+d/2+1), 0.2, C.timber);
    flagPatch(W, x+4.2, baseY+9.2, z+d/2+1, 4, 2, 0.55, [C.blue,C.white], 0);
  }
  for(let i=0;i<3;i++){
    const px=rr(x-3,x+3), pz=rr(z+d/2+1,z+d/2+3);
    W.add(px, land(px,pz)+0.7, pz, 0.55,0.7,0.55, C.dockWood2);
  }
  return {chim:[chimX,ry+2,chimZ]};
}
function shadeRoof(hex){ const c=new THREE.Color(hex); c.multiplyScalar(0.82); return c.getHex(); }
function flagPatch(B,x0,y0,z0,w,h,cell,cols,dir){
  for(let i=0;i<w;i++) for(let k=0;k<h;k++){
    const c = cols[Math.floor((k/h)*cols.length)%cols.length];
    B.add(x0+i*cell*dir, y0+k*cell, z0, cell*0.5, cell*0.5, cell*0.5, c);
  }
}
function buildTown(){
  const chimneys=[];
  for(const l of LOTS){
    if(l.t==='house'){ const r=house(l.x,l.z,l.w,l.d,0,undefined,false); if(r) chimneys.push(r.chim); }
    else if(l.t==='church'){ chimneys.push(church(l.x,l.z,l.y)); }
    else if(l.t==='wind'){ windmill(l.x,l.z,l.y); }
  }
  return chimneys;
}
function church(x,z,y){
  const y0=y+1;
  W.fill(x-6,x+5,y0,y0+8,z-4,z+4,C.wall0);
  for(let i=x-5;i<=x+4;i+=3) for(const k of [z-4,z+4]) W.fill(i,i+1,y0+3,y0+6,k,k,C.lamp,true);
  for(let k=z-3;k<=z+3;k+=2) for(const i of [x-6,x+5]) W.fill(i,i,y0+3,y0+6,k,k,C.lamp,true);
  /* tower */
  W.fill(x-6,x-1,y0,y0+15,z-3,z+2,C.wall1);
  W.fill(x-6,x-1,y0+12,y0+13,z-3,z+2,C.stoneDress);
  W.set(x-4,y0+12,z,C.lamp,true); W.set(x-3,y0+12,z,C.lamp,true);
  W.set(x-4,y0+13,z,C.lamp,true); W.set(x-3,y0+13,z,C.lamp,true);
  W.fill(x-7,x,y0+15,y0+16,z-4,z+3,C.roof2);
  W.fill(x-5,x-2,y0+17,y0+17,z-2,z+1,C.roof2);
  W.fill(x-4,x-3,y0+18,y0+19,z-1,z,C.roof2);
  W.bar(V3(x-3.5,y0+20,z-0.5),V3(x-3.5,y0+23,z-0.5),0.14,C.brass);
  /* graveyard */
  for(let i=0;i<9;i++){
    const gx=x+ri(2,12), gz=z+ri(-8,8);
    W.add(gx, land(gx,gz)+0.8, gz, 0.35,0.8,0.28, pick([C.stone0,C.stone1]));
  }
  return [x-5,y0+16,z];
}
let windmillRef=null;
function windmill(x,z,y){
  const y0=y+1;
  for(let lvl=0;lvl<10;lvl++){
    const r = Math.max(1, 4 - Math.floor(lvl/3));
    for(let i=x-r;i<=x+r;i++) for(let k=z-r;k<=z+r;k++){
      const edge=(i===x-r||i===x+r||k===z-r||k===z+r);
      if(edge) W.set(i,y0+lvl,k, lvl%3===0?C.stoneDress:C.wall2);
      else if(lvl<3) W.set(i,y0+lvl,k,C.dark);
    }
  }
  W.fill(x-2,x+1,y0+6,z-2,z-2,C.lamp,true);
  W.bar(V3(x-0.5,y0+11,z),V3(x-0.5,y0+12.5,z),0.5,C.timber);
  windmillRef = new THREE.Group();
  windmillRef.position.set(x-0.5, y0+11.5, z+0.9);
  const armMat = new THREE.MeshLambertMaterial({color:0xc9b48d});
  const hubMat = new THREE.MeshLambertMaterial({color:0x6d5236});
  const hub = new THREE.Mesh(new THREE.BoxGeometry(1.1,1.1,1.0), hubMat); windmillRef.add(hub);
  for(let a=0;a<4;a++){
    const arm = new THREE.Group(); arm.rotation.z = a*Math.PI/2; windmillRef.add(arm);
    const spar = new THREE.Mesh(new THREE.BoxGeometry(0.35,8.5,0.3), hubMat);
    spar.position.y = 4.4; arm.add(spar);
    const lat = new THREE.Mesh(new THREE.BoxGeometry(2.1,7.0,0.18), armMat);
    lat.position.set(0.9,4.6,0.15); arm.add(lat);
  }
  scene.add(windmillRef);
}
function buildBreakwater(){
  for(let z=-14;z<=19;z++){
    const w = 3 + (z>8?1:0) + (z>15?1:0);
    for(let x=21;x<=21+w*2;x++){
      const top = QUAY_Y + (z>14?0.5:0);
      for(let y=-9;y<=top;y++){
        const edgeOuter = (x<=21+0.4||x>=21+w*2-0.4||z<=-13.5||z>=19);
        const r = rnd();
        let c = y>top-1.5 ? pick([C.stone0,C.stone1,C.rock0]) : pick([C.stone2,C.rock1,C.rock2]);
        if(edgeOuter && y>top-1 && r<0.28) c = C.rock0;
        W.set(x,y,z, r<0.12?C.rock1:c);
      }
      W.set(x, top+1, z, ((x+z)&1)?C.cobble:C.stone0);
    }
  }
  /* lighthouse */
  const lx=25, lz=17; let base=QUAY_Y+1;
  W.fill(lx-3,lx+4, base-1, base, lz-3, lz+3, C.stoneDress);
  base+=1;
  const levels=[[3,4,3,4],[3,3,4,5],[2,4,2,4]];
  let y=base;
  const bands=[[C.white,C.white],[C.red,C.red],[C.white,C.white],[C.red,C.red],[C.white,C.white]];
  for(let b=0;b<5;b++){
    const r = 3 - Math.floor(b*0.45);
    for(let k=0;k<3;k++){
      for(let i=lx-r;i<=lx+r;i++) for(let j=lz-r;j<=lz+r;j++){
        const edge=(i===lx-r||i===lx+r||j===lz-r||j===lz+r);
        if(!edge) continue;
        const col = bands[b][0];
        W.set(i,y+k,j, ((i+j+k)&3)===0? shadeRoof(col): col);
      }
    }
    y+=3;
  }
  W.fill(lx-4,lx+4,y-1,y-1,lz-4,lz+4,C.iron);
  W.fill(lx-2,lx+2,y,y+3,lz-2,lz+2,C.lamp,true);
  for(let i=lx-2;i<=lx+2;i+=2) for(const j of [lz-2,lz+2]) W.set(i,y+2,j,C.iron);
  W.fill(lx-3,lx+3,y+4,y+4,lz-3,lz+3,C.iron);
  W.fill(lx-1,lx+1,y+5,y+5,lz-1,lz+1,C.iron);
  W.set(lx,y+6,lz,C.lamp,true);
  lampLights[3].position.set(lx, y+2, lz);
  /* keeper's cottage */
  W.fill(lx-7,lx-2,QUAY_Y+1,QUAY_Y+4,lz+2,lz+6,C.wall1);
  W.fill(lx-7,lx-1,QUAY_Y+5,QUAY_Y+5,lz+1,lz+7,C.roof0);
  W.set(lx-5,QUAY_Y+2,lz+2,C.lamp,true);
  return {lampY:y+2, x:lx, z:lz};
}
function buildHeadlandWorks(){
  /* a signal tower on the west point */
  let cx=-56, cz=-8;
  const y=land(cx,cz);
  W.fill(cx-2,cx+2,y,y+12,cz-2,cz+2,pick([C.stone1,C.wall2,C.stone0]));
  W.fill(cx-3,cx+3,y+12,y+12,cz-3,cz+3,C.stoneDress);
  W.fill(cx-1,cx+1,y+13,y+14,cz-1,cz+1,C.lamp,true);
  W.fill(cx-2,cx+2,y+15,y+15,cz-2,cz+2,C.iron);
  for(const s of [[1,0],[-1,0],[0,1],[0,-1]]){
    W.bar(V3(cx+s[0]*3,y+6,cz+s[1]*3), V3(cx+s[0]*3,y+13,cz+s[1]*3), 0.3, C.timber);
  }
  /* beacons on rocks */
  for(const b of [[-36,10],[-28,20]]){
    const yy=Math.max(1,land(b[0],b[1]));
    W.fill(b[0]-1,b[0]+1,yy-2,yy+1,b[1]-1,b[1]+1,C.rock2);
    W.set(b[0],yy+2,b[1],C.lamp,true);
  }
  /* beacon light source follows the big beacon */
  lampLights[4].position.set(-36, land(-36,10)+4, 10);
}

buildTerrain();
buildQuay();
const LH = buildBreakwater();
buildHeadlandWorks();
const CHIMNEYS = buildTown();

const worldMesh = W.build(litMat, glowMat);
scene.add(worldMesh);

/* ══════════════════════════ 6. the ship ══════════════════════════ */
function buildShip(){
  const B=new Builder();
  const PR=[[-16,4.4],[-15.5,4.95],[-13,5.15],[-6,5.45],[0,5.5],[5,5.35],[10,4.5],[13.5,3.1],[15.5,1.8],[17,0.5]];
  const halfBeam = x=>{
    if(x<=PR[0][0]||x>=PR[PR.length-1][0]) return 0;
    for(let i=0;i<PR.length-1;i++){const a=PR[i],b=PR[i+1];
      if(x>=a[0]&&x<=b[0]) return lerp(a[1],b[1],(x-a[0])/(b[0]-a[0]));}
    return 0;
  };
  const yKeel = x => -3.3 + 2.1*Math.pow(Math.abs(x)/17,1.25);
  const yDeck = x => 2.2 + 1.7*Math.pow(Math.abs(x)/17,1.9);

  /* hull */
  for(let x=-16;x<=17;x++){
    const hbr=Math.round(halfBeam(x)); if(hbr<1) continue;
    const yb=Math.round(yKeel(x)), yd=Math.round(yDeck(x));
    for(let y=yb;y<=yd+2;y++){
      let w=hbr;
      if(y<=-2.2) w=Math.max(1,w-2); else if(y<=-1.2) w=Math.max(1,w-1);
      if(y>=yd)   w=Math.min(hbr+1,w+1);
      for(let z=-w;z<=w;z++){
        const edge = (Math.abs(z)===w);
        let c;
        if(y<=-1.2) c=C.hullUnder;
        else if(edge) c=(y===yd||y===yd+1)?C.wale:C.hull;
        else c=C.hullIn;
        if(edge && y===yd-1 && ((x+20)%4===0) && Math.abs(x)<11) c=0x241a14;
        if(edge && y===yd-1 && ((x+22)%4===0) && Math.abs(x)<11) c=C.brass;
        B.set(x,y,z,c);
      }
    }
  }
  /* decks */
  for(let x=-16;x<=17;x++){
    const hbr=Math.round(halfBeam(x)); if(hbr<1) continue;
    const yd=Math.round(yDeck(x));
    const w=Math.min(hbr+1, Math.round(halfBeam(x))+ (y>=yd?1:0));
    for(let z=-hbr-1;z<=hbr+1;z++){
      const wv=Math.round(yKeel(x));
      for(let y=Math.round(yKeel(x))+1;y<=yd;y++){
        if(Math.abs(z)>Math.round(halfBeam(x))) continue;
      }
    }
    for(let z=-(hbr+1);z<=hbr+1;z++){
      if(Math.abs(z)>hbr+1) continue;
      const inside = Math.abs(z)<=hbr+1;
      if(!inside) continue;
      if(Math.abs(z)===hbr+1 && yd<3.5) continue;
      B.set(x,yd,z, (((x+z)&1)?C.deckTop:C.deck2));
    }
  }
  /* bulwark cap rail */
  for(let x=-16;x<=17;x++){
    const hbr=Math.round(halfBeam(x)); if(hbr<1) continue;
    const yd=Math.round(yDeck(x))+2;
    for(const s of [-1,1]){
      const z=(hbr+1)*s;
      if(Math.abs(z)-hbr>1) continue;
      B.set(x,yd,z,C.dockWood);
    }
  }
  /* quarterdeck + forecastle + poop */
  const plat=(x0,x1,yTop,shr)=>{
    for(let x=x0;x<=x1;x++){
      const w=Math.max(1,Math.round((Math.round(halfBeam(x)))*shr));
      for(let z=-w;z<=w;z++) B.set(x,yTop,z, ((x+z)&1)?C.deckTop:C.deck2);
      for(const s of [-1,1]) for(let yy=1;yy<=2;yy++){
        const z=w*s; if(Math.abs(z)>=Math.round(halfBeam(x))) continue;
        B.set(x,yTop+yy,z,C.hull);
      }
    }
  };
  plat(7,15,Math.round(yDeck(11))+2,0.86);
  plat(-14,4,5,0.88);
  /* great cabin */
  for(let x=-15;x<=-6;x++){
    const w=Math.max(1,Math.round(Math.round(halfBeam(x))*0.86));
    for(let y=4;y<=6;y++){
      for(const s of [-1,1]) B.set(x,y,w*s,C.hull);
    }
    for(let z=-w+1;z<=w-1;z++) for(let y=4;y<=6;y++) B.set(x,y,z,C.dark);
    if(((x+20)%3)===0){ B.set(x,5,w,C.lamp,true); B.set(x,5,-w,C.lamp,true); }
    B.set(x,5,0,C.hull);
  }
  plat(-15,-6,7,0.8);
  /* stern windows on the transom */
  for(let z=-3;z<=3;z++) for(let y=5;y<=6;y++) B.set(-16,y,z, (z===0&&y===6)?C.hull:C.lamp, true);
  B.set(-16,7,0,C.lamp,true);
  /* forecastle cabin */
  for(let x=10;x<=14;x++){
    const w=Math.max(1,Math.round(Math.round(halfBeam(x))*0.8));
    for(const s of [-1,1]) B.set(x,4,w*s,C.hull);
    if((x&1)===0) for(const s of [-1,1]) B.set(x,4,w*s,C.lamp,true);
  }
  /* stern lantern */
  B.add(-16.6,8.4,0,0.6,0.9,0.6,C.iron);
  B.add(-16.6,9.5,0,0.45,0.6,0.45,C.lamp,true);
  B.add(-16.6,10.3,0,0.25,0.35,0.25,C.brass);
  /* gangway plank to the quay */
  const gy=6, qy=QUAY_Y+1;
  B.bar(V3(12,gy,-5.0), V3(12,qy,-13.6), 0.42, C.dockWood);
  B.bar(V3(13.1,gy,-5.0), V3(13.1,qy,-13.6), 0.42, C.dockWood);
  for(let i=0;i<8;i++){
    const t=i/7;
    const p=V3(12+ (12-12)*t, lerp(gy,qy,t), lerp(-5,-13.6,t));
    B.add(p.x+0.55,p.y+0.05,p.z,1.2,0.12,0.3,C.deck2);
    B.bar(V3(p.x,p.y+1.5,p.z), V3(p.x+1.1,p.y+1.5,p.z),0.08,C.rope);
  }
  /* masts */
  B.bar(V3(0,2,0), V3(0,28.5,0), 0.62, C.mast);
  B.bar(V3(8.5,2,0), V3(8.5,23,0), 0.55, C.mast);
  B.bar(V3(-8.5,3,0), V3(-8.5,19.5,0), 0.5, C.mast);
  B.bar(V3(14.5,3.2,0), V3(26,8.6,0), 0.5, C.mast);
  B.bar(V3(25.2,8.3,0), V3(31,10.6,0), 0.28, C.mast);
  for(const s of [-1,1]) B.bar(V3(15.6,3.4,s*3.2), V3(22.5,6.6,s*1.2), 0.24, C.mast);
  /* tops + caps */
  for(const m of [[0,17.6,2.6],[8.5,14.6,2.2],[-8.5,12.4,1.9]]){
    B.add(m[0],m[1],0,m[2]*0.55,0.3,m[2],C.timber);
    for(const s of [-1,1]) B.add(m[0],m[1]+0.8,s*m[2],0.28,0.9,0.28,C.timber);
  }
  /* yards */
  const yards=[[0,12.5,9.6],[0,18.6,7.2],[0,23.4,4.6],[8.5,10.6,7.4],[8.5,15.6,5.4],[-8.5,13.6,3.2]];
  for(const yd of yards){
    B.bar(V3(yd[0],yd[1],-yd[2]), V3(yd[0],yd[1],yd[2]), 0.34, C.mast);
    for(const s of [-1,1]) B.add(yd[0],yd[1]-0.5,s*(yd[2]+0.4),0.3,0.3,0.3,C.iron);
  }
  B.bar(V3(-8.5,7.4,0), V3(-15.5,6.2,0), 0.3, C.mast);
  B.bar(V3(-8.5,13.6,0), V3(-14.2,15.4,0), 0.3, C.mast);

  /* square sails */
  const sail=(xm,y0,y1,zh,billow,opts={})=>{
    for(let y=y0;y<=y1;y++){
      for(let z=-zh;z<=zh;z++){
        const u=(z+zh)/(2*zh), vy=(y-y0)/(y1-y0);
        const cu=Math.sin(Math.PI*u), cv=Math.sin(Math.PI*Math.min(1,0.15+vy*1.05));
        const curve=cu*cv;
        let hex = C.sail;
        if(opts.red && Math.abs(z)<1.6 && vy>0.05) hex=C.sailRed;
        if(opts.red && vy>0.46 && vy<0.62) hex=C.sailRed;
        else if(((y+y0)%3)===0) hex=C.sail2;
        if(u<0.06||u>0.94) hex=C.sail2;
        const L=lin(hex), dim=0.78+0.22*Math.min(1,curve*1.5);
        B.add(xm-billow*curve, y, z, 0.22, 0.5, 0.5, hex);
      }
    }
  };
  sail(0, 6.2, 12.2, 9.4, 2.3, {red:true});
  sail(0, 14.2, 18.3, 7.0, 1.9);
  sail(8.5, 5.2, 10.3, 7.2, 2.1);
  sail(8.5, 12.2, 15.3, 5.2, 1.6);
  /* furled topgallants */
  for(const f of [[0,23.0,4.4],[8.5,15.2,5.2]]){
    B.add(f[0]-0.4, f[1]-1.0, 0, 0.5, 0.42, f[2], C.sail2);
  }
  /* spanker (fore-and-aft) */
  const quad=[[ -8.6,13.8],[-14.0,15.2],[-15.2,6.4],[-8.6,6.4]];
  const inside=(px,py)=>{
    let s=true;
    for(let i=0;i<4;i++){
      const a=quad[i], b=quad[(i+1)%4];
      const cr=(b[0]-a[0])*(py-a[1])-(b[1]-a[1])*(px-a[0]);
      if(cr<0) s=false;
    }
    return s;
  };
  for(let x=-16;x<=-8;x++) for(let y=6;y<=16;y++){
    if(inside(x,y)){
      const vy=(y-6)/10;
      B.add(x, y, 0, 0.22, 0.5, 0.5 - vy*0.2, ((x+y)%3===0)?C.sail2:C.sail);
    }
  }
  /* jibs */
  const tri=(a,b,c,col)=>{
    const x0=Math.min(a[0],b[0],c[0])-1, x1=Math.max(a[0],b[0],c[0])+1;
    const y0=Math.min(a[1],b[1],c[1])-1, y1=Math.max(a[1],b[1],c[1])+1;
    for(let x=x0;x<=x1;x++) for(let y=y0;y<=y1;y++){
      let inn=true;
      for(let i=0;i<3;i++){
        const p=a[i],q=b[i],r2=c[i];
        const cr=(q[0]-p[0])*(y-p[1])-(q[1]-p[1])*(x-p[0]);
        if(cr<0) inn=false;
      }
      if(inn){
        const sag=Math.sin(Math.PI*((x-x0)/(x1-x0+1)))*0.7;
        B.add(x,y,sag,0.22,0.5,0.9,col);
      }
    }
  };
  tri([[26,8.4],[9.4,19.5],[13.0,5.0]], C.sail2, C.sail);
  tri([[20,6.2],[9.2,14.0],[10.2,4.6]], C.sail, C.sail2);

  /* rigging */
  const R=C.rope;
  B.line(V3(0,27,0), V3(16.5,4.5,0), 0.16, R, 1.1);
  B.line(V3(0,27,0), V3(-14,6.4,0), 0.16, R, 1.6);
  B.line(V3(0,20,0), V3(-13,6.0,0), 0.14, R, 1.2);
  B.line(V3(8.5,22,0), V3(24.5,8.4,0), 0.15, R, 1.0);
  B.line(V3(8.5,17,0), V3(20,6.4,0), 0.13, R, 0.8);
  B.line(V3(8.5,22,0), V3(-1,6.4,0), 0.14, R, 1.2);
  B.line(V3(-8.5,19,0), V3(-15.4,7.4,0), 0.14, R, 0.5);
  for(const m of [[0,20.5,2.6],[8.5,16.6,2.2],[-8.5,13.4,1.9]]){
    for(const s of [-1,1]){
      for(let k=0;k<3;k++){
        const zf=(k-1)*0.45;
        B.line(V3(m[0],m[1],s*m[2]*0.7), V3(m[0]+zf*2.2, 3.0, s*(4.9+zf*0.6)), 0.12, R, 0.4);
      }
      for(let yy=Math.round(m[1])-1; yy>4.2; yy-=1.15){
        const t=(yy-4.2)/(m[1]-4.2);
        B.add(m[0]+ (1-t)*(-0.2), yy, s*lerp(5.0, m[2]*0.7, t)*0.98, 0.1,0.1,0.1,R);
        B.add(m[0]+ (1-t)*(1.6)-0.2, yy, s*lerp(5.0, m[2]*0.7, t)*0.98, 0.1,0.1,0.1,R);
      }
    }
    B.line(V3(m[0],m[1],m[2]*0.7), V3(m[0]-4,3.4,m[2]*0.9),0.12,R,0.5);
    B.line(V3(m[0],m[1],-m[2]*0.7),V3(m[0]-4,3.4,-m[2]*0.9),0.12,R,0.5);
  }
  for(const yd of [[0,12.5,9.6],[0,18.6,7.2],[8.5,10.6,7.4]]){
    for(const s of [-1,1]){
      B.line(V3(yd[0],yd[1],s*yd[2]), V3(yd[0]+3,3.2,s*4.6),0.12,R,0.7);
      B.line(V3(yd[0],yd[1],s*yd[2]), V3(yd[0]-3,3.2,s*4.6),0.12,R,0.9);
    }
  }
  /* dressing the ship — signal flags aloft */
  const fl=[C.red,C.white,C.blue,C.yellow,C.green,C.white,C.red];
  for(let i=0;i<7;i++){
    const t=(i+1)/8;
    const p=V3(lerp(0,8.5,t), lerp(26.6,21.6,t)+0.6, 0);
    B.add(p.x,p.y-0.9,p.z,0.35,0.5,0.7,fl[i]);
  }
  /* deck furniture */
  for(let i=0;i<4;i++) B.add(-3+i*3.2, 5.9, 2.2, 0.75,0.75,0.75, pick([C.dockWood,C.dockWood2]));
  for(let i=0;i<3;i++) B.add(-4+i*4, 5.9, -2.4, 0.75,0.75,0.75, pick([C.dockWood,C.dockWood2]));
  B.add(4,5.9,0,1.0,0.7,1.0,C.dockWood); B.add(4,6.8,0,1.2,0.2,1.2,C.deck2);
  for(let a=0;a<8;a++){
    const t=a/8*Math.PI*2;
    B.add(4+Math.cos(t)*0.9, 7.0, Math.sin(t)*0.9, 0.16,0.16,0.16,C.timber);
  }
  B.add(-1,5.7,0,0.6,0.6,0.6,C.brass);
  /* guns */
  for(let i=0;i<6;i++){
    const gx=-10+i*3.6;
    for(const s of [-1,1]) B.add(gx, 3.0, s*5.6, 0.25,0.25,0.55, C.iron);
  }
  /* crew */
  for(const p of [[2,4.2,3.5],[5,5.2,2.0],[-4,5.2,-2.6],[-11,7.2,1.4],[9,4.2,-3.2],[12,3.6,1.2],[-6,5.2,2.8]])
    figure(B,p[0],p[1],p[2], pick([C.figA,C.figB,C.red,C.white,C.green]));
  /* colours */
  flagPatch(B, 0.3, 26.0, 0, 7, 4, 0.55, [C.blue,C.white,C.red], 1);
  flagPatch(B, -8.2, 18.4, 0, 5, 3, 0.55, [C.red,C.white], 1);

  /* foam collar */
  const foam = new Builder();
  for(let a=0;a<64;a++){
    const t=a/64*Math.PI*2;
    const x=Math.cos(t)*17.5, z=Math.sin(t)*6.6;
    if(rnd()<0.65) foam.add(x, -0.1, z, rr(0.4,0.9), 0.25, rr(0.4,0.9), 0xf2f6f6);
  }
  for(let x=-15;x<=17;x+=2){
    foam.add(x, -0.1, 5.9, 0.55,0.2,0.5, 0xf2f6f6);
    foam.add(x, -0.1, -5.9, 0.55,0.2,0.5, 0xf2f6f6);
  }
  const ship = new THREE.Group();
  ship.add(B.build(litMat, glowMat));
  const fm = foam.build(litMat, glowMat);
  fm.traverse(o=>{ if(o.isMesh){ o.material=new THREE.MeshBasicMaterial({vertexColors:true,transparent:true,opacity:0.82}); o.castShadow=false; }});
  ship.add(fm);
  return ship;
}
const shipGroup = buildShip();
shipGroup.position.set(0,0,-5.4);
scene.add(shipGroup);

/* ══════════════════════════ 7. other vessels ══════════════════════════ */
function buildBrig(){
  const B=new Builder();
  for(let x=-9;x<=9;x++){
    const t=(x+9)/18;
    const hb=Math.max(1, Math.round(2.6*Math.sin(Math.PI*Math.pow(t,0.8)) + 0.6));
    const yb=Math.round(-1.9+1.1*Math.pow(Math.abs(x)/9,1.3));
    const yd=Math.round(1.3+0.9*Math.pow(Math.abs(x)/9,1.6));
    for(let y=yb;y<=yd+1;y++) for(let z=-hb;z<=hb;z++){
      const e=(Math.abs(z)===hb);
      B.set(x,y,z, y<0?C.hullUnder : e ? (y>=yd?C.wale:C.hull) : C.hullIn);
    }
    for(let z=-hb;z<=hb;z++) B.set(x,yd,z, ((x+z)&1)?C.deckTop:C.deck2);
  }
  B.bar(V3(-1,1,0),V3(-1,17,0),0.45,C.mast);
  B.bar(V3(5.5,1,0),V3(5.5,14,0),0.4,C.mast);
  B.bar(V3(-1,8.5,-5.4),V3(-1,8.5,5.4),0.28,C.mast);
  B.bar(V3(-1,13.2,-4),V3(-1,13.2,4),0.24,C.mast);
  B.bar(V3(5.5,7.6,-4.4),V3(5.5,7.6,4.4),0.26,C.mast);
  const s2=(xm,y0,y1,zh,bl)=>{ for(let y=y0;y<=y1;y++) for(let z=-zh;z<=zh;z++){
    const u=(z+zh)/(2*zh), v=(y-y0)/(y1-y0);
    B.add(xm-bl*Math.sin(Math.PI*u)*Math.sin(Math.PI*Math.min(1,0.2+v)),y,z,0.2,0.5,0.5, ((y%3)===0)?C.sail2:C.sail);
  }};
  s2(-1,4.0,8.2,5.2,1.5); s2(-1,10.0,13.0,3.8,1.2); s2(5.5,3.6,7.4,4.2,1.3);
  B.line(V3(-1,16.6,0),V3(9,1.6,0),0.13,C.rope,0.6);
  B.line(V3(-1,16.6,0),V3(-8.6,2.2,0),0.13,C.rope,0.9);
  B.line(V3(5.5,13.6,0),V3(-6,2.2,0),0.12,C.rope,0.9);
  flagPatch(B,-0.8,15.6,0,5,3,0.5,[C.white,C.red],1);
  const g=new THREE.Group(); g.add(B.build(litMat,glowMat));
  return g;
}
const brig = buildBrig();
brig.position.set(34,0,26); brig.rotation.y=-0.62; brig.scale.setScalar(0.92);
scene.add(brig);

function buildRowboat(){
  const B=new Builder();
  for(let x=-3;x<=3;x++){
    const hb=Math.max(1, Math.round(1.3*Math.cos(x*0.34)+0.4));
    for(let z=-hb;z<=hb;z++){
      B.set(x,-0.3,z, Math.abs(z)===hb?C.dockWood2:C.deck2);
      B.set(x,-1.3,z, Math.abs(z)===hb?C.hull:C.dark);
      if(Math.abs(z)===hb) B.set(x,0.4,z,C.dockWood);
    }
  }
  B.add(0,0.1,0,0.5,0.4,1.0,C.dockWood);
  for(const s of [-1,1]) B.bar(V3(-1,-0.2,s*1.4), V3(-4.5,0.6,s*2.6), 0.14, C.timber);
  const g=new THREE.Group(); g.add(B.build(litMat,glowMat)); return g;
}
const boats=[];
for(let i=0;i<4;i++){
  const b=buildRowboat();
  const bx=[-20,-9,14,-31][i], bz=[-12.6,-12.4,-12.8,-14][i];
  b.position.set(bx,0,bz); b.rotation.y=rr(-0.3,0.3)+ (i===3?1.4:0);
  b.scale.setScalar(i===2?1.15:1);
  scene.add(b); boats.push({o:b,ph:rr(0,6.3),x:bx,z:bz,amp:i===2?0.5:0.9});
}

/* ══════════════════════════ 8. clouds · gulls · smoke ══════════════════════════ */
const cloudData=[];
{
  const geo=new THREE.BoxGeometry(1,1,1);
  const mat=new THREE.MeshLambertMaterial({flatShading:true});
  const total=380;
  const inst=new THREE.InstancedMesh(geo,mat,total);
  inst.castShadow=false; inst.receiveShadow=false;
  const dummy=new THREE.Object3D(), col=new THREE.Color();
  let idx=0;
  for(let c=0;c<11;c++){
    const cx=rr(-140,140), cy=rr(42,72), cz=rr(-100,120);
    const sp=rr(0.45,1.15), parts=ri(24,38), arr=[];
    for(let i=0;i<parts && idx<total;i++,idx++){
      const o={dx:rr(-14,14), dy:rr(-2.6,2.4), dz:rr(-9,9),
               sx:rr(4,11), sy:rr(2.2,4.6), sz:rr(3,8)};
      arr.push(o); cloudData.push({i, c});
      col.setHex(pick([0xffffff,0xf4eee4,0xe6dcd2])); col.multiplyScalar(rr(0.86,1.05));
      inst.setColorAt(idx,col);
    }
    cloudData.push({cloud:true, x:cx,y:cy,z:cz,sp,parts:arr});
  }
  inst.count=idx;
  scene.add(inst);
  var cloudMesh=inst;
}
function updateClouds(dt,t){
  const d=new THREE.Object3D();
  const arr=cloudData;
  const clouds=arr.filter(a=>a.cloud);
  clouds.forEach(cl=>{ cl.x += dt*cl.sp*2.4; if(cl.x>170) cl.x-=340; });
  let ptr=0;
  clouds.forEach((cl,ci)=>{
    cl.parts.forEach((o,oi)=>{
      const i=ci===0?oi:0;
      return;
    });
  });
  /* rebuild matrices (flat list) */
  let n=0;
  for(const cl of clouds){
    for(const o of cl.parts){
      d.position.set(cl.x+o.dx, cl.y+o.dy, cl.z+o.dz);
      d.scale.set(o.sx,o.sy,o.sz);
      d.updateMatrix();
      cloudMesh.setMatrixAt(n++, d.matrix);
    }
  }
  cloudMesh.count=n;
  cloudMesh.instanceMatrix.needsUpdate=true;
}
const cloudData2 = cloudData;

/* gulls */
const gullGeo={};
{
  const T=newT();
  faceInto(T,0,0,0,0.75,0.22,0.28,0,0,0,0);
  for(let f=0;f<6;f++) faceInto(T,0,0,0,0.7,0.22,0.3,f,0.92,0.92,0.92);
  for(let f=0;f<6;f++) faceInto(T,1.0,0.05,0,0.25,0.15,0.15,f,0.95,0.95,0.95);
  for(let f=0;f<6;f++) faceInto(T,1.35,0.02,0,0.2,0.08,0.08,f,0.9,0.6,0.2);
  for(let f=0;f<6;f++) faceInto(T,-0.95,-0.02,0,0.35,0.05,0.28,f,0.86,0.86,0.86);
  gullGeo.body=finish(T);
  const W2=newT();
  for(let f=0;f<6;f++) faceInto(W2,0,0,1.55,0.5,0.08,1.5,f,0.95,0.95,0.95);
  for(let f=0;f<6;f++) faceInto(W2,-0.35,0,2.7,0.3,0.07,0.6,f,0.30,0.32,0.34);
  gullGeo.wing=finish(W2);
}
const gullMat=new THREE.MeshLambertMaterial({vertexColors:true});
const gulls=[];
for(let i=0;i<6;i++){
  const g=new THREE.Group();
  g.add(new THREE.Mesh(gullGeo.body,gullMat));
  const wl=new THREE.Group(), wr=new THREE.Group();
  const ml=new THREE.Mesh(gullGeo.wing,gullMat), mr=new THREE.Mesh(gullGeo.wing,gullMat);
  ml.position.z=0.28; mr.rotation.y=Math.PI; mr.position.z=-0.28;
  wl.add(ml); wr.add(mr); g.add(wl,wr);
  g.traverse(o=>{if(o.isMesh)o.castShadow=false;});
  scene.add(g);
  gulls.push({g,wl,wr,r:rr(24,58),y:rr(16,34),sp:rr(0.11,0.22)*(rnd()<0.5?-1:1),ph:rr(0,6.3),cx:rr(-12,18),cz:rr(-10,26)});
}

/* chimney smoke (voxel puffs) */
const smokeList=[];
{
  const emitters = CHIMNEYS.map(c=>({p:V3(c[0]+0.5,c[1]+0.5,c[2]+0.5)})).slice(0,7);
  emitters.push({p:V3(-4,7.2,-3.5)});
  const geo=new THREE.BoxGeometry(1,1,1);
  const mat=new THREE.MeshLambertMaterial({transparent:true,opacity:0.5,depthWrite:false,flatShading:true});
  const N=110;
  const inst=new THREE.InstancedMesh(geo,mat,N);
  inst.castShadow=false; inst.frustumCulled=false;
  const col=new THREE.Color();
  for(let i=0;i<N;i++){
    const e=emitters[i%emitters.length];
    smokeList.push({e, t:rnd(), life:rr(3.5,6.5), vx:rr(0.2,0.9), vz:rr(-0.4,0.5), s:rr(0.5,1.1), i});
    col.setHex(0xcccccc); inst.setColorAt(i,col);
  }
  scene.add(inst); var smokeMesh=inst;
}
function updateSmoke(dt,wind){
  const d=new THREE.Object3D(), col=new THREE.Color();
  for(const p of smokeList){
    p.t += dt/p.life;
    if(p.t>1){ p.t=0; p.vx=rr(0.2,0.9); p.vz=rr(-0.4,0.5); p.s=rr(0.5,1.1); }
    const t=p.t;
    d.position.set(p.e.x + p.vx*t*7 + wind*t*4.5, p.e.y + t*9.5, p.e.z + p.vz*t*7);
    const sc = p.s*(0.4+t*2.6);
    d.scale.set(sc,sc,sc);
    d.updateMatrix();
    smokeMesh.setMatrixAt(p.i,d.matrix);
    col.setRGB(0.42+0.5*t, 0.40+0.48*t, 0.38+0.46*t);
    smokeMesh.setColorAt(p.i,col);
  }
  smokeMesh.instanceMatrix.needsUpdate=true;
  if(smokeMesh.instanceColor) smokeMesh.instanceColor.needsUpdate=true;
}

/* ══════════════════════════ 9. water ══════════════════════════ */
const wU = {
  uTime:{value:0}, uWind:{value:1.0}, uSunDir:{value:new THREE.Vector3(0.6,0.2,0.5)},
  uGlint:{value:new THREE.Color(0xffe6bf)}, uGlintI:{value:1.4}
};
function makeWaterMat(){
  const m = new THREE.MeshStandardMaterial({color:0xffffff, roughness:0.42, metalness:0.06});
  m.onBeforeCompile = sh=>{
    Object.assign(sh.uniforms, wU);
    sh.vertexShader = 'uniform float uTime;uniform float uWind;uniform vec3 uSunDir;varying float vG;\n'+
      sh.vertexShader.replace('#include <begin_vertex>', `#include <begin_vertex>
      #ifdef USE_INSTANCING
        vec3 ip = instanceMatrix[3].xyz;
      #else
        vec3 ip = vec3(0.0);
      #endif
      float inside = 0.30 + 0.70*smoothstep(-24.0, 34.0, ip.z);
      float amp = 0.40*uWind*inside + 0.06;
      float tt = uTime;
      float h = amp*( sin(ip.x*0.19 + tt*1.15) + sin(ip.z*0.155 - tt*0.95) + 0.55*sin((ip.x+ip.z)*0.112 + tt*0.62) );
      h = floor(h*4.0)/4.0;
      float dx = 0.19*amp*cos(ip.x*0.19 + tt*1.15) + 0.062*amp*cos((ip.x+ip.z)*0.112 + tt*0.62);
      float dz = 0.155*amp*cos(ip.z*0.155 - tt*0.95) + 0.062*amp*cos((ip.x+ip.z)*0.112 + tt*0.62);
      vec3 nn = normalize(vec3(-dx,1.0,-dz));
      #ifdef USE_INSTANCING
        vec4 wp4 = modelMatrix * instanceMatrix * vec4(position,1.0);
      #else
        vec4 wp4 = modelMatrix * vec4(position,1.0);
      #endif
      vec3 vv = normalize(cameraPosition - wp4.xyz);
      vec3 rr2 = reflect(-uSunDir, nn);
      vG = pow(max(dot(rr2,vv),0.0), 52.0);
      transformed.y += h;`);
    sh.fragmentShader = 'varying float vG;uniform vec3 uGlint;uniform float uGlintI;\n'+
      sh.fragmentShader.replace('#include <emissivemap_fragment>',
        `#include <emissivemap_fragment>
         totalEmissiveRadiance += uGlint * (vG*uGlintI);`);
  };
  return m;
}
const waterMat = makeWaterMat();
const waterGroups=[];
{
  const levels=[[1,46],[2,42],[3,40]];
  for(const [sp,cnt] of levels){
    const geo=new THREE.BoxGeometry(sp,3.4,sp);
    const inst=new THREE.InstancedMesh(geo,waterMat,cnt);
    inst.receiveShadow=true; inst.frustumCulled=false;
    inst.userData={sp,list:[],mesh:inst};
    waterGroups.push(inst.userData);
  }
  const d=new THREE.Object3D(), col=new THREE.Color();
  const deep=new THREE.Color(0x123c4e), mid=new THREE.Color(0x1c6a76), shal=new THREE.Color(0x41a0a0);
  function addCell(x,z,sp,slot){
    if(land(x,z) > 0) return;
    for(let i=1;i<=6;i++){
      const nx=Math.round(x+i*sp*0.8), nz=Math.round(z+i*sp*0.8);
      if(land(nx,nz)>0 || land(x-nx===0?nx:nx, nz)>0){}
    }
    let sh=0;
    for(let r=1;r<=4;r++){
      let touched=false;
      for(let a=0;a<8;a++){
        const ang=a*Math.PI/4;
        if(land(Math.round(x+Math.cos(ang)*r*2.2), Math.round(z+Math.sin(ang)*r*2.2))>0.5) touched=true;
      }
      if(touched) sh+=1;
    }
    const f=clamp(sh/4,0,1);
    col.copy(f>0.6?shal:mid).lerp(deep, f>0.6?(1-f)*0.6:clamp(1.15-sh/3.4,0,1));
    col.multiplyScalar(0.92+0.12*Math.sin(x*0.3+z*0.21));
    const u=waterGroups[slot];
    if(u.list.length>= (slot===0?26000:9000)) return;
    u.list.push([x, z]);
  }
  const cx=0, cz=8;
  for(let x=-46;x<=46;x++) for(let z=-40;z<=46;z++){ const r=Math.hypot(x-cx,z-cz); if(r<46) addCell(x,z,1,0); }
  for(let x=-92;x<=92;x+=2) for(let z=-80;z<=90;z+=2){ const r=Math.hypot(x-cx,z-cz); if(r>=44&&r<92) addCell(x,z,2,1); }
  for(let x=-138;x<=138;x+=3) for(let z=-120;z<=135;z+=3){ const r=Math.hypot(x-cx,z-cz); if(r>=90&&r<138) addCell(x,z,3,2); }
  waterGroups.forEach(u=>{
    u.list.forEach((c,i)=>{
      d.position.set(c[0], -1.75, c[1]); d.rotation.set(0,0,0); d.scale.set(1,1,1);
      d.updateMatrix();
      u.mesh.setMatrixAt(i,d.matrix);
    });
    /* recolor pass */
    u.list.forEach((c,i)=>{
      let sh=0;
      for(let r=1;r<=4;r++) for(let a=0;a<8;a++){
        const ang=a*Math.PI/4;
        if(land(Math.round(c[0]+Math.cos(ang)*r*2.4), Math.round(c[1]+Math.sin(ang)*r*2.4))>0.5) sh++;
      }
      const f=clamp(sh/9,0,1);
      col.copy(deep).lerp(mid, clamp(f*1.6,0,1)).lerp(shal, clamp((f-0.55)*2.2,0,1));
      col.multiplyScalar(0.9+0.16*Math.sin(c[0]*0.31+c[1]*0.2));
      u.mesh.setColorAt(i,col);
    });
    u.mesh.count=u.list.length;
    if(u.mesh.instanceColor) u.mesh.instanceColor.needsUpdate=true;
    scene.add(u.mesh);
  });
}
const farSea = new THREE.Mesh(new THREE.CircleGeometry(1400,64),
  new THREE.MeshLambertMaterial({color:0x14414f}));
farSea.rotation.x=-Math.PI/2; farSea.position.set(0,-0.55,0); farSea.receiveShadow=false;
scene.add(farSea);

/* lighthouse beam */
const beamGroup=new THREE.Group();
beamGroup.position.set(LH.x, LH.lampY, LH.z);
const beamMat=new THREE.MeshBasicMaterial({color:0xffd9a0,transparent:true,opacity:0.14,
  blending:THREE.AdditiveBlending,depthWrite:false,side:THREE.DoubleSide});
for(const s of [1,-1]){
  const cone=new THREE.Mesh(new THREE.ConeGeometry(9,86,4,1,true), beamMat);
  cone.rotation.z = Math.PI/2 * (s>0?1:-1);
  cone.rotation.y = s>0?0:Math.PI/4;
  cone.position.x = s*43;
  cone.frustumCulled=false;
  beamGroup.add(cone);
}
scene.add(beamGroup);

/* sprites */
function radialTex(inner){
  const s=64, cv=document.createElement('canvas'); cv.width=cv.height=s;
  const g=cv.getContext('2d');
  const gr=g.createRadialGradient(s/2,s/2,0,s/2,s/2,s/2);
  gr.addColorStop(0,'rgba(255,255,255,1)');
  gr.addColorStop(inner,'rgba(255,236,190,0.45)');
  gr.addColorStop(1,'rgba(255,220,170,0)');
  g.fillStyle=gr; g.fillRect(0,0,s,s);
  const t=new THREE.CanvasTexture(cv); t.colorSpace=THREE.SRGBColorSpace; return t;
}
const glowTex=radialTex(0.25);
const sprites=[];
function addGlow(x,y,z,size,hex){
  const m=new THREE.SpriteMaterial({map:glowTex,color:hex,transparent:true,blending:THREE.AdditiveBlending,depthWrite:false,opacity:0.9});
  const sp=new THREE.Sprite(m); sp.position.set(x,y,z); sp.scale.setScalar(size);
  scene.add(sp); sprites.push(sp); return sp;
}
const sunSprite = addGlow(0,0,0,180,0xfff0d0);
addGlow(LH.x, LH.lampY, LH.z, 20, 0xffc98a);
for(const lx of [-27,-14,-1,12,23]) addGlow(lx, QUAY_Y+4.3, -31.5, 7, 0xffbe78);
addGlow(-16.6+shipGroup.position.x, 9.5, shipGroup.position.z, 6, 0xffbe78);
addGlow(-36, land(-36,10)+3, 10, 7, 0xffbe78);
addGlow(-56, land(-56,-8)+14.6, -8, 8, 0xffbe78);

/* ══════════════════════════ 10. time of day ══════════════════════════ */
const TOD=[
 {p:0.00, az:284, el:3,  top:0x1e3157, mid:0x6f6a85, bot:0xffab72, sun:0xff9f5e, si:1.15, hs:0x4a5f80, hg:0x3b3227, hi:0.55, bs:0x40506e, bi:0.18,
   deep:0x14384a, shal:0x3e8a92, fog:0x8a8496, glint:0xffc28a, gi:1.3, night:0.32},
 {p:0.20, az:266, el:16, top:0x2f6698, mid:0x8fb0c6, bot:0xdfe6df, sun:0xffe0b4, si:1.75, hs:0x9dbcd8, hg:0x6b6146, hi:0.62, bs:0x6f92b6, bi:0.24,
   deep:0x12455a, shal:0x3fa0a2, fog:0xb9c6c8, glint:0xfff0d2, gi:0.85, night:0.0},
 {p:0.46, az:250, el:58, top:0x2a6fb4, mid:0x92c1e0, bot:0xd6eaf2, sun:0xfff3dc, si:2.2,  hs:0xa9cfe8, hg:0x7b7050, hi:0.7,  bs:0x8fb4cf, bi:0.28,
   deep:0x0f4d66, shal:0x48b0aa, fog:0xc2d9e2, glint:0xffffff, gi:0.65, night:0.0},
 {p:0.72, az:300, el:12, top:0x255a8c, mid:0x8e86a2, bot:0xffb46a, sun:0xffb35c, si:2.25, hs:0x7d92b4, hg:0x6a5033, hi:0.6,  bs:0x5f7392, bi:0.22,
   deep:0x123a4e, shal:0x358a8a, fog:0xa08e92, glint:0xffd7a0, gi:1.75, night:0.18},
 {p:0.87, az:318, el:2,  top:0x1b2a4e, mid:0x5b4a6d, bot:0xff7a45, sun:0xff7a3c, si:1.25, hs:0x3d4a70, hg:0x2f2820, hi:0.5,  bs:0x3a4560, bi:0.16,
   deep:0x102f42, shal:0x28707a, fog:0x6f5a63, glint:0xffa860, gi:1.55, night:0.6},
 {p:1.00, az:118, el:32, top:0x050a1c, mid:0x101d36, bot:0x27355a, sun:0xaec4e8, si:0.38, hs:0x243css, hg:0x141a24, hi:0.30, bs:0x223048, bi:0.1,
   deep:0x071d2e, shal:0x123f52, fog:0x16223a, glint:0xbcd0f0, gi:0.9, night:1.0}
];
TOD[5].hs=0x243050;

function sampleTOD(t){
  let a=TOD[0], b=TOD[TOD.length-1];
  for(let i=0;i<TOD.length-1;i++){ if(t>=TOD[i].p && t<=TOD[i+1].p){a=TOD[i];b=TOD[i+1];break;} }
  const f=ss(0,1,(t-a.p)/(b.p-a.p||1));
  const cc=(k)=>{ const ca=new THREE.Color(a[k]), cb=new THREE.Color(b[k]); return ca.lerp(cb,f); };
  return {
    az:lerp(a.az,b.az,f), el:lerp(a.el,b.el,f),
    top:cc('top'), mid:cc('mid'), bot:cc('bot'), sun:cc('sun'), si:lerp(a.si,b.si,f),
    hs:cc('hs'), hg:cc('hg'), hi:lerp(a.hi,b.hi,f), bs:cc('bs'), bi:lerp(a.bi,b.bi,f),
    deep:cc('deep'), shal:cc('shal'), fog:cc('fog'), glint:cc('glint'), gi:lerp(a.gi,b.gi,f),
    night:lerp(a.night,b.night,f)
  };
}
const cDeep=new THREE.Color(), cShal=new THREE.Color();
function applyTOD(t){
  const s=sampleTOD(t);
  const az=s.az*Math.PI/180, el=s.el*Math.PI/180;
  const dir=V3(Math.sin(az)*Math.cos(el), Math.sin(el), Math.cos(az)*Math.cos(el));
  skyU.cTop.value.copy(s.top); skyU.cMid.value.copy(s.mid); skyU.cBot.value.copy(s.bot);
  skyU.uSun.value.copy(dir); skyU.uSunCol.value.copy(s.sun); skyU.uNight.value=s.night;
  sun.color.copy(s.sun); sun.intensity=s.si;
  sun.position.copy(dir).multiplyScalar(230); sun.target.position.set(0,6,-10);
  hemi.color.copy(s.hs); hemi.groundColor.copy(s.hg); hemi.intensity=s.hi;
  bounce.color.copy(s.bs); bounce.intensity=s.bi;
  scene.fog.color.copy(s.fog);
  renderer.setClearColor(s.fog);
  wU.uGlint.value.copy(s.glint); wU.uGlintI.value=s.gi; wU.uSunDir.value.copy(dir);
  cDeep.copy(s.deep); cShal.copy(s.shal);
  farSea.material.color.copy(s.deep);
  glowMat.color.setScalar(clamp(1.25-s.night*0.2,0.25,1.0));
  lampLights.forEach(l=>l.intensity=s.night*3.4);
  beamMat.opacity=0.05+s.night*0.2;
  sprites.forEach(sp=>{ sp.material.opacity = sp===sunSprite ? (0.35+0.55*(1-s.night*0.6)) : (0.25+0.75*s.night); });
  const sunPos=dir.clone().multiplyScalar(1100); sunPos.y=Math.max(-40,sunPos.y);
  sunSprite.position.copy(sunPos);
  sunSprite.scale.setScalar(150+s.night*90);
  sunSprite.material.color.copy(s.sun);
  const hour = 5.5 + t*17;
  const hh=Math.floor(hour)%24, mm=Math.floor((hour%1)*60);
  document.getElementById('clock').textContent = String(hh).padStart(2,'0')+':'+String(Math.floor(mm/5)*5).padStart(2,'0');
  const names=['DAWN','MORNING','MIDDAY','AFTERNOON','GOLDEN','DUSK','NIGHT'];
  document.getElementById('todLab').textContent = names[Math.min(6,Math.floor(t*6.999))];
  const tide=Math.sin(t*Math.PI*2-0.6);
  document.getElementById('cond').textContent =
    (tide>=0?'FLOOD +':'EBB −')+Math.abs(tide).toFixed(1)+' M · VIS '+(s.night>0.5?'3.2':'9.5')+' NM';
}

/* ══════════════════════════ 11. camera + controls ══════════════════════════ */
const ctrl={target:V3(-2,8,-11), r:74, theta:-2.24, phi:1.13,
            gTheta:-2.24, gPhi:1.13, gR:74, gT:V3(-2,8,-11), auto:true, idle:0};
function camUpdate(){
  ctrl.theta += (ctrl.gTheta-ctrl.theta)*0.09;
  ctrl.phi   += (ctrl.gPhi-ctrl.phi)*0.09;
  ctrl.r     += (ctrl.gR-ctrl.r)*0.08;
  ctrl.target.lerp(ctrl.gT,0.08);
  const sp=Math.sin(ctrl.phi), cp=Math.cos(ctrl.phi);
  camera.position.set(
    ctrl.target.x + ctrl.r*sp*Math.sin(ctrl.theta),
    Math.max(1.6, ctrl.target.y + ctrl.r*cp),
    ctrl.target.z + ctrl.r*sp*Math.cos(ctrl.theta));
  camera.lookAt(ctrl.target);
}
const el=renderer.domElement;
let drag=false, pan=false, px=0, py=0, pinch=0;
el.addEventListener('pointerdown',e=>{ drag=true; pan=(e.button===2||e.shiftKey); px=e.clientX; py=e.clientY; ctrl.idle=0; el.setPointerCapture(e.pointerId);});
el.addEventListener('contextmenu',e=>e.preventDefault());
window.addEventListener('pointerup',()=>drag=false);
el.addEventListener('pointermove',e=>{
  if(!drag) return;
  const dx=e.clientX-px, dy=e.clientY-py; px=e.clientX; py=e.clientY; ctrl.idle=0;
  if(pan){
    const s=ctrl.r*0.0016;
    const right=V3(Math.cos(ctrl.theta),0,-Math.sin(ctrl.theta));
    const fwd=V3(Math.sin(ctrl.theta),0,Math.cos(ctrl.theta));
    ctrl.gT.addScaledVector(right,-dx*s).addScaledVector(fwd,dy*s);
    ctrl.gT.x=clamp(ctrl.gT.x,-55,45); ctrl.gT.z=clamp(ctrl.gT.z,-45,45); ctrl.gT.y=clamp(ctrl.gT.y,2,24);
  } else {
    ctrl.gTheta -= dx*0.0055;
    ctrl.gPhi = clamp(ctrl.gPhi - dy*0.0045, 0.30, 1.44);
  }
});
el.addEventListener('wheel',e=>{ e.preventDefault(); ctrl.gR=clamp(ctrl.gR*(1+Math.sign(e.deltaY)*0.09),24,190); ctrl.idle=0;},{passive:false});
el.addEventListener('touchstart',e=>{ if(e.touches.length===2){ const a=e.touches[0],b=e.touches[1]; pinch=Math.hypot(a.clientX-b.clientX,a.clientY-b.clientY);} },{passive:true});
el.addEventListener('touchmove',e=>{
  if(e.touches.length===2){
    const a=e.touches[0],b=e.touches[1]; const d=Math.hypot(a.clientX-b.clientX,a.clientY-b.clientY);
    ctrl.gR=clamp(ctrl.gR*(1+(pinch-d)*0.004),24,190); pinch=d; ctrl.idle=0;
  }
},{passive:true});

/* ══════════════════════════ 12. UI ══════════════════════════ */
const $=id=>document.getElementById(id);
let todVal=0.73;
$('tod').addEventListener('input',e=>{ todVal=e.target.value/1000; applyTOD(todVal); });
let windVal=0.42;
$('wind').addEventListener('input',e=>{
  windVal=e.target.value/100; wU.uWind.value=0.45+windVal*1.9;
  const kn=Math.round(1+windVal*17);
  const dirs=['W','WSW','SW','SSW','S'];
  $('windLab').textContent=kn+' kn · '+dirs[clamp(Math.floor(kn/4),0,4)];
});
$('btnOrbit').addEventListener('click',e=>{ ctrl.auto=!ctrl.auto; e.target.classList.toggle('on',ctrl.auto); });
$('btnReset').addEventListener('click',()=>{ ctrl.gTheta=-2.24; ctrl.gPhi=1.13; ctrl.gR=74; ctrl.gT.set(-2,8,-11); ctrl.idle=0; });
window.addEventListener('keydown',e=>{ if(e.key==='h'||e.key==='H') document.body.classList.toggle('hide'); });

/* ══════════════════════════ 13. loop ══════════════════════════ */
applyTOD(todVal);
wU.uWind.value=0.45+windVal*1.9;
updateClouds(0,0);
let last=performance.now()/1000, first=true, t=0;
const CARD=['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW'];

function frame(now){
  now/=1000; let dt=Math.min(0.05, now-last); last=now; t+=dt;
  ctrl.idle+=dt;
  if(ctrl.auto && ctrl.idle>2.5) ctrl.gTheta += dt*0.045;
  camUpdate();
  sky.position.copy(camera.position);
  skyU.uTime.value=t;
  wU.uTime.value=t;

  /* ship at anchor */
  const heel=0.012+windVal*0.026;
  shipGroup.rotation.z=Math.sin(t*0.52)*heel - windVal*0.035;
  shipGroup.rotation.x=Math.sin(t*0.37+1.1)*0.011;
  shipGroup.position.y=Math.sin(t*0.72)*0.22 - 0.02;
  brig.rotation.z=Math.sin(t*0.61+2.2)*0.02;
  brig.position.y=Math.sin(t*0.83+0.7)*0.24;
  for(const b of boats){
    b.o.position.y=Math.sin(t*1.15+b.ph)*0.16;
    b.o.rotation.z=Math.sin(t*1.4+b.ph)*0.05;
    b.o.rotation.x=Math.cos(t*1.05+b.ph)*0.035;
  }
  /* gulls */
  for(const g of gulls){
    g.ph+=dt*g.sp;
    const flap=Math.sin(t*7.5+g.ph*3);
    g.g.position.set(g.cx+Math.cos(g.ph)*g.r, g.y+Math.sin(t*0.6+g.ph)*2.2, g.cz+Math.sin(g.ph)*g.r*0.8);
    g.g.rotation.y=-g.ph+(g.sp>0?Math.PI/2:-Math.PI/2);
    g.g.rotation.z=-0.25*Math.sign(g.sp);
    g.wl.rotation.x = flap*0.75;
    g.wr.rotation.x = flap*0.75;
  }
  /* clouds + smoke */
  updateClouds(dt,windVal);
  updateSmoke(dt,windVal*1.6);
  /* lighthouse */
  beamGroup.rotation.y = t*0.55;
  /* windmill */
  if(windmillRef) windmillRef.rotation.z = t*(0.35+windVal*1.15);
  /* lantern flicker */
  const fl=1+Math.sin(t*7.3)*0.05+Math.sin(t*13.1)*0.03;
  lampLights.forEach(l=>{ const s=sampleTOD(todVal).night; l.intensity=s*3.4*fl; });

  /* readouts */
  const degs=(Math.round((-ctrl.theta*180/Math.PI)%360+360))%360;
  $('brg').textContent=String(degs).padStart(3,'0')+'°';
  $('card').textContent=CARD[Math.round(degs/22.5)%16];
  $('alt').textContent=Math.round(camera.position.y*2.1);

  renderer.render(scene,camera);
  if(first){
    first=false;
    document.getElementById('loader').classList.add('gone');
    document.body.classList.add('ready');
    document.querySelectorAll('.brk').forEach(b=>b.classList.add('on'));
    setTimeout(()=>document.getElementById('loader').remove(),1200);
  }
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);

addEventListener('resize',()=>{
  camera.aspect=innerWidth/innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight);
});
</script>
</body>
</html>
```

**What's in there**

- **Voxel engine:** a hand-written chunk mesher — occupancy map, hidden-face culling, per-vertex ambient occlusion, directional face shading — merged into one draw call for the world, another for the ship (plus a separate unlit mesh so window and lantern voxels actually glow).
- **The packet:** ~3000 hand-shaped hull voxels from a lofted profile with raked keel, sheer, and flared topsides; gunports, wales, transom lights, forecastle, quarterdeck and poop, bowsprit, three masts, yards, bellied square sails (with a red cross on the course), a spanker, two jibs, ratlines, shrouds with sag, dressed signal flags, a stern lantern, crew on deck, and a gangplank running down to the quay.
- **The harbor:** dressed quay wall with buttresses, a slipway, bollards and lamp posts, a custom house, a derrick crane, barrels and nets, a terraced hill town of 26 procedurally-placed houses with lit windows, a church with a clock tower, a rotating windmill, a west headland with a signal tower, and a banded lighthouse sweeping two additive beams.
- **Alive:** stepped-wave instanced sea with animated sun glitter, three LOD bands of water blocks, foam collar, drifting clouds, six circling gulls, chimney and galley smoke, bobbing rowboats, a moored brig, and a ship that rolls and settles at her moorings.
- **Interaction:** drag/wheel/right-drag orbit with damping and idle auto-orbit, a **time-of-day** scrubber that repaints sky, sun elevation, fog, sea tint, glitter and every lantern across six keyframed looks, and a **wind** slider that drives the swell, the heel of the ship, cloud and smoke drift, and the windmill. Press **H** to drop the panels for a clean view.