Here's the whole thing — a single-file voxel diorama. It builds the harbour procedurally (every block placed by a tiny custom mesher with baked ambient occlusion), then keeps it alive: swell that follows the same wave function the ship floats on, lamps that wake up at dusk, gulls, smoke, a turning light, and ripples you can poke.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Calling at the Harbour — a voxel diorama</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,900;1,9..144,600&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root{
    --ink:#061116; --ink2:#0a1a21; --ink3:#0d232c;
    --paper:#f4ead7; --muted:#8fb0b9; --dim:#5c7d88;
    --brass:#e0a63f; --signal:#d3563f; --foam:#c9eef0;
    --disp:'Fraunces', Georgia, serif;
    --mono:'IBM Plex Mono', ui-monospace, monospace;
    --sans:'IBM Plex Sans', system-ui, sans-serif;
  }
  *{box-sizing:border-box}
  html,body{height:100%;margin:0;background:#061116;overflow:hidden;font-family:var(--sans);}
  canvas#c{position:fixed;inset:0;display:block;cursor:grab;touch-action:none}
  canvas#c.drag{cursor:grabbing}
  #vig{position:fixed;inset:0;pointer-events:none;
       background:radial-gradient(120% 90% at 50% 45%, rgba(0,0,0,0) 40%, rgba(2,10,14,.55) 100%);
       mix-blend-mode:multiply;z-index:2}
  #grain{position:fixed;inset:0;pointer-events:none;z-index:3;opacity:.055;
    background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='120' height='120'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='3'/></filter><rect width='120' height='120' filter='url(%23n)'/></svg>")}
  #ui{position:fixed;inset:0;z-index:6;pointer-events:none}
  #ui.hidden .panel,#ui.hidden .mk,#ui.hidden .hint{opacity:0!important;transform:translateY(6px)}

  .panel{position:absolute;pointer-events:auto;
    background:linear-gradient(178deg, rgba(9,23,29,.9), rgba(5,14,18,.86));
    border:1px solid rgba(224,166,63,.22);
    box-shadow:0 26px 70px -28px rgba(0,0,0,.85), inset 0 1px 0 rgba(255,255,255,.05);
    transition:opacity .5s ease, transform .5s ease}
  .panel::before,.panel::after{content:'';position:absolute;width:7px;height:7px;border:1px solid var(--brass);opacity:.55}
  .panel::before{top:-1px;left:-1px;border-right:0;border-bottom:0}
  .panel::after{bottom:-1px;right:-1px;border-left:0;border-top:0}

  /* ---- title plate ---- */
  #plate{top:26px;left:28px;max-width:min(46vw,470px);padding:20px 24px 22px;background:none;border:0;box-shadow:none}
  #plate::before,#plate::after{display:none}
  .ovl{display:flex;align-items:center;gap:10px;font-family:var(--mono);font-size:9.5px;letter-spacing:.24em;
       text-transform:uppercase;color:var(--muted)}
  .ovl i{display:block;width:30px;height:2px;background:var(--signal)}
  h1{font-family:var(--disp);font-variation-settings:'opsz' 144,'SOFT' 20,'WONK' 1;
     font-weight:900;font-size:clamp(2.3rem,4.6vw,4.05rem);line-height:.85;letter-spacing:-.028em;
     color:var(--paper);margin:12px 0 0;text-shadow:0 10px 30px rgba(0,0,0,.5)}
  h1 em{display:block;font-weight:600;font-style:italic;font-size:.61em;letter-spacing:-.01em;
        color:var(--foam);opacity:.95;margin-top:.1em}
  #plate p{font-size:12.5px;line-height:1.62;color:#a7c3ca;margin:14px 0 0;max-width:38ch}
  #plate p b{color:var(--paper);font-weight:500}
  .rule{height:1px;background:linear-gradient(90deg,var(--brass),rgba(224,166,63,0));margin:15px 0 0;width:76%}

  /* ---- console ---- */
  #console{left:28px;bottom:26px;padding:16px 18px 17px;width:min(35vw,362px)}
  .ttl{font-family:var(--mono);font-size:9px;letter-spacing:.22em;text-transform:uppercase;color:var(--dim);margin-bottom:12px;
       display:flex;justify-content:space-between}
  .row{display:flex;align-items:baseline;justify-content:space-between;gap:8px;margin:0 0 5px}
  .row label{font-family:var(--mono);font-size:9.5px;letter-spacing:.15em;text-transform:uppercase;color:var(--muted)}
  .val{font-family:var(--disp);font-weight:600;font-size:16px;color:var(--brass);font-variant-numeric:tabular-nums}
  .val small{font-family:var(--mono);font-size:9px;letter-spacing:.1em;color:var(--dim);font-weight:400}
  input[type=range]{-webkit-appearance:none;appearance:none;width:100%;height:16px;background:none;cursor:ew-resize;margin:0 0 12px}
  input[type=range]::-webkit-slider-runnable-track{height:2px;background:linear-gradient(90deg,var(--brass) var(--p,50%),rgba(255,255,255,.16) var(--p,50%))}
  input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:9px;height:14px;margin-top:-6px;background:var(--paper);
     border:1px solid #000;box-shadow:0 0 0 1px rgba(224,166,63,.6);transition:transform .15s}
  input[type=range]:hover::-webkit-slider-thumb{transform:scaleY(1.25)}
  input[type=range]::-moz-range-track{height:2px;background:rgba(255,255,255,.16)}
  input[type=range]::-moz-range-thumb{width:9px;height:14px;border-radius:0;background:var(--paper);border:1px solid #000}
  .chips{display:flex;flex-wrap:wrap;gap:5px;margin-top:2px}
  .chip{font-family:var(--mono);font-size:9px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);
    background:rgba(255,255,255,.045);border:1px solid rgba(255,255,255,.1);padding:5px 8px;cursor:pointer;
    transition:all .18s ease;pointer-events:auto}
  .chip:hover{color:var(--ink);background:var(--brass);border-color:var(--brass);transform:translateY(-1px)}
  .chip.on{color:var(--ink);background:var(--foam);border-color:var(--foam)}
  .hr{height:1px;background:rgba(224,166,63,.18);margin:13px 0 11px}

  /* ---- POI index ---- */
  #poi{top:26px;right:28px;width:236px;padding:15px 6px 12px 16px}
  #poi .ttl{padding-right:12px}
  .prow{display:flex;gap:9px;align-items:baseline;padding:7px 10px 7px 6px;cursor:pointer;position:relative;
        border-left:2px solid transparent;transition:all .2s ease}
  .prow:hover{background:rgba(201,238,240,.07);border-left-color:var(--brass);transform:translateX(3px)}
  .prow b{font-family:var(--mono);font-size:9px;color:var(--brass);letter-spacing:.1em}
  .prow span{font-family:var(--disp);font-weight:600;font-size:13.5px;color:var(--paper);line-height:1.25}
  .prow i{display:block;font-family:var(--mono);font-style:normal;font-size:9px;letter-spacing:.08em;color:var(--dim);margin-top:2px}

  /* ---- instruments ---- */
  #inst{right:28px;bottom:26px;padding:14px 16px;display:flex;gap:16px;align-items:flex-end}
  .grid{display:grid;grid-template-columns:auto auto;gap:8px 18px}
  .grid div{display:flex;flex-direction:column;gap:1px}
  .grid b{font-family:var(--mono);font-size:8.5px;letter-spacing:.2em;text-transform:uppercase;color:var(--dim);font-weight:400}
  .grid i{font-style:normal;font-family:var(--disp);font-weight:600;font-size:15px;color:var(--paper);font-variant-numeric:tabular-nums}
  #rose{width:66px;height:66px;flex:0 0 66px}
  #rose text{font-family:var(--mono);font-size:7.5px;fill:var(--muted);letter-spacing:.1em}

  .hint{position:absolute;left:50%;bottom:26px;transform:translateX(-50%);font-family:var(--mono);font-size:9px;
    letter-spacing:.16em;text-transform:uppercase;color:rgba(190,215,220,.5);transition:.5s;pointer-events:none;text-align:center}
  .hint b{color:var(--brass);font-weight:500}

  /* ---- 3D markers ---- */
  #marks{position:absolute;inset:0;pointer-events:none}
  .mk{position:absolute;left:0;top:0;pointer-events:auto;background:none;border:0;padding:0;cursor:pointer;
      opacity:0;transition:opacity .4s ease}
  .mk .dot{position:absolute;left:-5px;top:-5px;width:10px;height:10px;transform:rotate(45deg);
      border:1.5px solid var(--brass);background:rgba(4,14,18,.6);transition:transform .25s cubic-bezier(.3,1.4,.5,1),background .2s}
  .mk .pulse{position:absolute;left:-11px;top:-11px;width:22px;height:22px;border:1px solid rgba(224,166,63,.5);
      transform:rotate(45deg);animation:pz 3.2s ease-out infinite;opacity:0}
  @keyframes pz{0%{transform:rotate(45deg) scale(.45);opacity:.8}70%,100%{opacity:0;transform:rotate(45deg) scale(1.5)}}
  .mk .lbl{position:absolute;left:16px;top:-11px;white-space:nowrap;padding:5px 9px 6px;
      background:linear-gradient(180deg,rgba(8,22,28,.94),rgba(5,14,18,.92));border-left:2px solid var(--brass);
      opacity:0;transform:translateX(-5px);transition:.24s cubic-bezier(.2,.8,.3,1)}
  .mk .lbl s{display:block;text-decoration:none;font-family:var(--mono);font-size:8.5px;letter-spacing:.18em;color:var(--brass)}
  .mk .lbl em{display:block;font-style:normal;font-family:var(--disp);font-weight:600;font-size:13px;color:var(--paper);margin-top:1px}
  .mk:hover .lbl,.mk.hot .lbl{opacity:1;transform:translateX(0)}
  .mk:hover .dot,.mk.hot .dot{transform:rotate(45deg) scale(1.35);background:var(--brass)}
  .mk.hot{pointer-events:none}

  /* ---- loader ---- */
  #load{position:fixed;inset:0;z-index:20;background:radial-gradient(120% 100% at 30% 20%,#0d2530,#040d11 70%);
        display:flex;flex-direction:column;justify-content:center;padding-left:min(11vw,140px);transition:opacity .9s ease,visibility .9s}
  #load.gone{opacity:0;visibility:hidden}
  #load h2{font-family:var(--disp);font-variation-settings:'opsz' 144,'WONK' 1;font-weight:900;color:var(--paper);
        font-size:clamp(2.4rem,7vw,5.4rem);line-height:.86;margin:14px 0 4px;letter-spacing:-.03em}
  #load .ovl{color:var(--dim)}
  #bar{margin-top:26px;width:min(56vw,430px);height:2px;background:rgba(255,255,255,.12)}
  #barfill{height:100%;width:0;background:var(--brass);transition:width .28s ease}
  #phase{font-family:var(--mono);font-size:10px;letter-spacing:.2em;text-transform:uppercase;color:var(--foam);margin-top:12px;min-height:14px}
  #err{font-family:var(--mono);font-size:11px;color:var(--signal);margin-top:16px;max-width:44ch;line-height:1.6}

  .reveal{opacity:0;transform:translateY(14px);animation:rise 1s cubic-bezier(.2,.8,.25,1) forwards;animation-delay:var(--d,0s)}
  @keyframes rise{to{opacity:1;transform:none}}
  @media (prefers-reduced-motion:reduce){.reveal{animation:none;opacity:1;transform:none}}
  @media (max-width:1080px){#poi,#inst{display:none}#plate{max-width:70vw}#console{width:min(60vw,340px)}}
  @media (max-width:640px){#plate{left:16px;top:16px}#console{left:16px;bottom:16px;width:calc(100vw - 32px)}.hint{display:none}}
</style>
</head>
<body>
<canvas id="c"></canvas>
<div id="vig"></div><div id="grain"></div>

<div id="ui">
  <header class="panel" id="plate" style="pointer-events:none">
    <div class="ovl reveal" style="--d:.15s"><i></i>Port of Ellesmere · Sheet 03 · scale 1 block = 1 fathom</div>
    <h1 class="reveal" style="--d:.3s">Calling at<em>the Harbour</em></h1>
    <div class="rule reveal" style="--d:.45s"></div>
    <p class="reveal" style="--d:.55s">A barque brought up in the tide and tied herself to the Long Wharf.
       Every block below is placed by hand — <b>by a machine</b>. Drag to come about; scrub the day away on the console.</p>
  </header>

  <section class="panel reveal" id="console" style="--d:.8s">
    <div class="ttl"><span>Harbourmaster's console</span><span id="modeTxt">drifting</span></div>
    <div class="row"><label for="time">Hour of day</label><span class="val" id="clock">17:18 <small>gloaming</small></span></div>
    <input id="time" type="range" min="0" max="24" step=".01" value="17.3">
    <div class="row"><label for="wind">Wind</label><span class="val" id="windTxt">9 <small>kn · WSW</small></span></div>
    <input id="wind" type="range" min="0" max="1" step=".01" value=".34">
    <div class="hr"></div>
    <div class="chips" id="views">
      <button class="chip on" data-v="arrival">Arrival</button>
      <button class="chip" data-v="alongside">Alongside</button>
      <button class="chip" data-v="quay">Quayside</button>
      <button class="chip" data-v="mast">Masthead</button>
      <button class="chip" data-v="chart">Chart</button>
    </div>
    <div class="chips" style="margin-top:7px">
      <button class="chip on" id="tOrbit">Auto-drift</button>
      <button class="chip on" id="tMarks">Chart marks</button>
      <button class="chip" id="tHide">Hide panel (H)</button>
    </div>
  </section>

  <aside class="panel reveal" id="poi" style="--d:.95s">
    <div class="ttl"><span>Points of interest</span><span>06</span></div>
    <div id="pail"></div>
  </aside>

  <div class="panel reveal" id="inst" style="--d:1.1s">
    <svg id="rose" viewBox="0 0 100 100">
      <circle cx="50" cy="50" r="44" fill="none" stroke="rgba(224,166,63,.25)"/>
      <circle cx="50" cy="50" r="33" fill="none" stroke="rgba(224,166,63,.14)"/>
      <g id="roseN">
        <path d="M50 8 L55 44 L50 38 L45 44 Z" fill="#d3563f"/>
        <path d="M50 92 L55 56 L50 62 L45 56 Z" fill="#cfe4e8" opacity=".8"/>
        <line x1="50" y1="2" x2="50" y2="12" stroke="#e0a63f"/>
      </g>
      <text x="50" y="20" text-anchor="middle">N</text>
      <text x="50" y="86" text-anchor="middle">S</text>
      <text x="86" y="53" text-anchor="middle">E</text>
      <text x="14" y="53" text-anchor="middle">W</text>
    </svg>
    <div class="grid">
      <div><b>Bearing</b><i id="rBearing">214°</i></div>
      <div><b>Tide</b><i id="rTide">+2.4m</i></div>
      <div><b>Blocks</b><i id="rBlocks">—</i></div>
      <div><b>Render</b><i id="rFps">— fps</i></div>
    </div>
  </div>

  <div id="marks"></div>
  <div class="hint reveal" style="--d:1.4s">drag <b>orbit</b> · scroll <b>zoom</b> · right-drag <b>pan</b> · double-click <b>focus</b> · click the water for a <b>ripple</b></div>
</div>

<div id="load">
  <div class="ovl"><i></i>Procedural voxel plate · no downloads</div>
  <h2>Calling at<br>the Harbour</h2>
  <div id="bar"><div id="barfill"></div></div>
  <div id="phase">unrolling the chart…</div>
  <div id="err"></div>
</div>

<script type="importmap">
{"imports":{"three":"https://unpkg.com/three@0.161.0/build/three.module.js"}}
</script>

<script type="module">
const LOAD = document.getElementById('load');
const PHASE = document.getElementById('phase');
const BAR = document.getElementById('barfill');
const nextFrame = ()=>new Promise(r=>requestAnimationFrame(()=>r()));

async function main(){
  const THREE = await import('three');

  /* ═══════════════════════ noise / maths ═══════════════════════ */
  const h1 = n => { const s = Math.sin(n*127.1183)*43758.5453; return s - Math.floor(s); };
  const h3 = (x,y,z)=>{ let n = Math.sin(x*127.1 + y*311.7 + z*74.7)*43758.5453; return n - Math.floor(n); };
  function vn2(x,y){
    const ix=Math.floor(x), iy=Math.floor(y), fx=x-ix, fy=y-iy;
    const ux=fx*fx*(3-2*fx), uy=fy*fy*(3-2*fy);
    const a=h1(ix+iy*57.3), b=h1(ix+1+iy*57.3), c=h1(ix+(iy+1)*57.3), d=h1(ix+1+(iy+1)*57.3);
    return (a*(1-ux)+b*ux)*(1-uy) + (c*(1-ux)+d*ux)*uy;
  }
  const fbm2 = (x,y)=> vn2(x,y)*.55 + vn2(x*2.1,y*2.1)*.28 + vn2(x*4.3,y*4.3)*.17;
  const fbm1 = x => vn2(x, 7.31)*.6 + vn2(x*2.3, 3.7)*.4;
  const clamp = (v,a,b)=>v<a?a:v>b?b:v;
  const c01 = v=>clamp(v,0,1);
  const lerp = (a,b,t)=>a+(b-a)*t;
  const smooth = t=>t*t*(3-2*t);
  const smoothstep=(a,b,x)=>smooth(c01((x-a)/(b-a)));

  /* ═══════════════════════ voxel container + mesher ═══════════════════════ */
  class Vox{
    constructor(){ this.m = new Map(); this.count=0; }
    static key(x,y,z){ return (x+512) + (y+128)*1024 + (z+512)*1048576; }
    set(x,y,z,c){ const k=Vox.key(x,y,z); if(!this.m.has(k)) this.count++; this.m.set(k,c); }
    has(x,y,z){ return this.m.has(Vox.key(x,y,z)); }
  }
  class VoxelSet{
    constructor(){ this.solid=new Vox(); this.glow=new Vox(); }
    isSolid(x,y,z){ return this.solid.has(x,y,z)||this.glow.has(x,y,z); }
    get count(){ return this.solid.count + this.glow.count; }
  }
  const AO=[1,.87,.73,.58];
  const FACE={ '0,0,0':.80,'-1,0,0':.68,'0,1,0':1,'0,-1,0':.44,'0,0,1':.92,'0,0,-1':.61 };
  const DIRS=[[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]];
  function perp(d){ if(d[0]===0) return [1,0,0]; if(d[1]===0) return [0,1,0]; return [0,0,1]; }
  const cr=(a,b)=>[a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]];
  const add=(a,b,m)=>[a[0]+b[0]*m, a[1]+b[1]*m, a[2]+b[2]*m];
  const dot3=(a,b)=>a[0]*b[0]+a[1]*b[1]+a[2]*b[2];

  function bake(set, layer){
    const src = set[layer];
    const P=[],N=[],CL=[],IX=[]; let vi=0;
    for(const [k,c] of src.m){
      const x=(k%1024)-512, y=Math.floor(k/1024)%1024-128, z=Math.floor(k/1048576)-512;
      for(const d of DIRS){
        const nx=x+d[0], ny=y+d[1], nz=z+d[2];
        if(set.isSolid(nx,ny,nz)) continue;
        const f=FACE[d.join(',')];
        const u=perp(d), v=cr(d,u), cx=x+.5+d[0]*.5, cy=y+.5+d[1]*.5, cz=z+.5+d[2]*.5;
        const base=vi;
        for(const [su,sv] of [[-1,-1],[1,-1],[1,1],[-1,1]]){
          const s1=set.isSolid(...add(add([nx,ny,nz],u,su),v,0));
          const s2=set.isSolid(...add(add([nx,ny,nz],v,sv),u,0));
          const cn=set.isSolid(...add(add([nx,ny,nz],u,su),v,sv));
          const ao=(s1&&s2)?3:(s1+s2+(cn?1:0));
          const sh=f*AO[ao];
          P.push(cx+u[0]*su*.5+v[0]*sv*.5, cy+u[1]*su*.5+v[1]*sv*.5, cz+u[2]*su*.5+v[2]*sv*.5);
          N.push(d[0],d[1],d[2]);
          CL.push(c.r*sh, c.g*sh, c.b*sh);
          vi++;
        }
        IX.push(base,base+1,base+2, base,base+2,base+3);
      }
    }
    const g=new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(P,3));
    g.setAttribute('normal', new THREE.Float32BufferAttribute(N,3));
    g.setAttribute('color', new THREE.Float32BufferAttribute(CL,3));
    g.setIndex(IX); g.computeBoundingSphere();
    return g;
  }

  /* paint helpers -------------------------------------------------- */
  const tint=(hex,amt,r)=>{ const c=new THREE.Color(hex); c.multiplyScalar(1+(r-.5)*2*amt); return c; };
  function box(v,x0,x1,y0,y1,z0,z1,hex,amt=.07,hollow=false){
    const [a,b]=[Math.min(x0,x1),Math.max(x0,x1)],[c,d]=[Math.min(y0,y1),Math.max(y0,y1)],[e,f]=[Math.min(z0,z1),Math.max(z0,z1)];
    for(let x=a;x<=b;x++)for(let y=c;y<=d;y++)for(let z=e;z<=f;z++){
      if(hollow && !(x===a||x===b||y===c||y===d||z===e||z===f)) continue;
      v.set(x,y,z,tint(hex,amt,h3(x,y,z)));
    }
  }
  function line(v,p0,p1,hex,amt=.05){
    const d=[p1[0]-p0[0],p1[1]-p0[1],p1[2]-p0[2]];
    const L=Math.max(Math.abs(d[0]),Math.abs(d[1]),Math.abs(d[2]));
    if(L<1e-4){ v.set(Math.round(p0[0]),Math.round(p0[1]),Math.round(p0[2]),tint(hex,amt,.5)); return; }
    for(let i=0;i<=L;i++){ const t=i/L;
      v.set(Math.round(lerp(p0[0],p1[0],t)),Math.round(lerp(p0[1],p1[1],t)),Math.round(lerp(p0[2],p1[2],t)),tint(hex,amt,h1(i+t*7)));
    }
  }
  function arch(v,cx,cy,r,hex,amt=.08){ // 3/4 circle, opening to -Z
    const pts=[[1,0],[0,1],[-1,0],[0,-1]], s=r+.5;
    for(let y=cy; y<cy+r; y++){
      const t=(y+.5-cy)/r; if(t<=0||t>=1) continue;
      const w=Math.sqrt(Math.max(0,r*r-Math.pow(y+.5-cy+.5,2)));
      for(let x=Math.round(cx-w);x<=Math.round(cx+w);x++)
        for(let z=Math.round(cz0(w,y-cy+cy));z<=Math.round(cz1(w,y-cy+cy));z++) v.set(x,y,z,tint(hex,amt,h3(x,y,z)));
    }
    function cz0(w,yy){return -Math.sqrt(Math.max(0,w*w-Math.pow(cx-(cx),2)))*0 + (yy>0? -w : -w);}
    function cz1(w,yy){return w;}
  }
  function roof(v,x0,x1,y,z0,z1,hex,ridgeZ){
    const a=Math.min(x0,x1),b=Math.max(x0,x1),c=Math.min(z0,z1),d=Math.max(z0,z1);
    const up = ridgeZ < (c+d)/2;
    let h=0;
    for(let x=a;x<=b;x++){ v.set(x,y,z0, tint(hex,.06,h3(x,y,z0))); v.set(x,y,z1, tint(hex,.06,h3(x,y,z1))); }
    let lo=c, hi=d;
    while(hi-lo>=1){
      if(up){ lo++; } else { hi--; }
      y++;
      for(let x=a;x<=b;x++){ v.set(x,y,lo,tint(hex,.07,h3(x,y,lo))); v.set(x,y,hi,tint(hex,.07,h3(x,y,hi))); }
      if(hi-lo===1){ for(let x=a;x<=b;x++) v.set(x,y,lo,tint(hex,.07,h3(x,y,lo))); break; }
    }
  }
  function gableRoof(v,x0,x1,y,z0,z1,hex,ridgeZ){ roof(v,x0,x1,y,z0,z1,hex,ridgeZ); }

  /* ═══════════════════════ palette ═══════════════════════ */
  const PAL={
    quayTop:0x8e887b, quayTop2:0x9c968a, wall:0x7b7568, wallWet:0x57604f, wallHi:0xa9a294,
    moor:0x4a5a52, rock:0x6c7175, rockDk:0x565c60, rockLt:0x878d8d, moss:0x5b6f45,
    sand:0xd9c08c, sandWet:0xbda06f, dune:0x93a264, duneDk:0x7d8d55,
    grass:0x5b8449, grassDk:0x496c3c,
    brickR:0x9a4e42, brickY:0xb0793f, brickP:0x8a6a58, render1:0xdccdb2, render2:0xc9b795,
    roofR:0x9d5044, roofS:0x4f5c66, roofT:0x77564a, slate:0x59666f,
    woodDk:0x5d4028, wood:0x8d6238, woodLt:0xb2854f, plank:0xa3743f,
    iron:0x33373b, ironDk:0x23262a, copper:0x2f8f83, brass:0xd2a03f,
    sail:0xefe5d1, sail2:0xd9cbae, hull:0x22262a, hullUW:0x6b4632, stripe:0xe9e2d0,
    red:0xc1443a, green:0x3f9a6a, blue:0x37628f, cream:0xf0e6d2, glass:0xffd8a0,
    white:0xe6e2d8, tar:0x2b2e2f, net:0x8f8365, fish:0x9fb8c4
  };
  const c = h=>new THREE.Color(h);

  /* ═══════════════════════ land definition ═══════════════════════ */
  const QUAY_X0=-20, QUAY_X1=46, QUAY_EDGE=12, QUAY_Y=3;
  const LH_X=-27, LH_Z=2;                       // lighthouse
  const BW_A=[30,10], BW_B=[54,-14];            // breakwater

  function landHeight(x,z){
    if(x>=QUAY_X0 && x<=QUAY_X1 && z>=QUAY_EDGE) return {h:QUAY_Y, k:'quay'};
    const dxe=(x+42)/26, dze=(z-4)/26;
    if(x<-14 && dxe*dxe+dze*dze<1){
      let hh = 4 + fbm2(x*.09,z*.09)*6 + (1-c01(Math.hypot(dxe,dze)))*3;
      if(Math.abs(x-LH_X)<6 && Math.abs(z-LH_Z)<6) hh=Math.max(hh,9);
      return {h:Math.round(hh), k:'rock'};
    }
    const e = 9 + fbm1(x*.055)*7 + fbm1(x*.19)*1.4;
    if(x<QUAY_X0 && z>e) return {h:Math.round(1+fbm2(x*.07,z*.07)*3.4), k:'dune'};
    const e2 = 22 + fbm1(x*.05)*9;
    if(x>QUAY_X1 && x<64 && z>e2) return {h:Math.round(1+fbm2(x*.07,z*.07)*3), k:'dune'};
    return null;
  }
  function shelterAt(x,z){
    let s = smoothstep(-18, 6, z);
    if(x>24 && z>-10) s=Math.max(s,.78);
    if(x<-12 && z<8) s=Math.min(s,.34);
    return c01(s);
  }
  function breakwaterTop(x,z){ // returns y if this column is breakwater stone
    const ax=BW_A[0],az=BW_A[1],bx=BW_B[0],bz=BW_B[1];
    const dx=bx-ax, dz=bz-az, L2=dx*dx+dz*dz;
    let t=((x-ax)*dx+(z-az)*dz)/L2; t=c01(t);
    const px=lerp(ax,bx,t), pz=lerp(az,bz,t);
    const d=Math.hypot(x-px,z-pz);
    const w = 2.4 - t*1.1 + fbm1(t*9)*.9;
    if(d>w) return null;
    return 1 + Math.round(smoothstep(0,1,1-d/w)*1.6 + fbm1(x*.4+z*.5)*1.2);
  }

  /* ═══════════════════════ renderer / scene ═══════════════════════ */
  const canvas=document.getElementById('c');
  const renderer=new THREE.WebGLRenderer({canvas, antialias:true, powerPreference:'high-performance'});
  renderer.setPixelRatio(Math.min(devicePixelRatio, 1.8));
  renderer.setSize(innerWidth, innerHeight);
  renderer.shadowMap.enabled=true;
  renderer.shadowMap.type=THREE.PCFSoftShadowMap;
  renderer.setClearColor(0x0a1c26);

  const scene=new THREE.Scene();
  scene.fog=new THREE.FogExp2(0x9ab9c8, .0088);
  const camera=new THREE.PerspectiveCamera(42, innerWidth/innerHeight, .5, 1600);

  const uTime={value:0}, uWind={value:.34};
  const uWaterTint={value:new THREE.Color(0xffffff)};
  const uRip={value:Array.from({length:6},()=>new THREE.Vector4(0,0,-99,0))};
  let ripI=0;

  /* sky dome */
  const skyU={uTop:{value:new THREE.Color(0x3a7ba5)},uHor:{value:new THREE.Color(0xf3b877)},
              uSunDir:{value:new THREE.Vector3(1,.2,0)},uSunCol:{value:new THREE.Color(0xffb166)},uGlow:{value:1}};
  const sky=new THREE.Mesh(new THREE.SphereGeometry(560,32,18), new THREE.ShaderMaterial({
    side:THREE.BackSide, depthWrite:false, fog:false, uniforms:skyU,
    vertexShader:`varying vec3 vP; void main(){ vP=position; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);} `,
    fragmentShader:`varying vec3 vP; uniform vec3 uTop,uHor,uSunDir,uSunCol; uniform float uGlow;
      void main(){ vec3 d=normalize(vP); float t=pow(clamp(1.0-d.y,0.,1.),2.1);
      vec3 col=mix(uTop,uHor,t); float s=clamp(dot(d,normalize(uSunDir)),0.,1.);
      col+=uSunCol*pow(s,9.0)*uGlow*.55; col+=uSunCol*pow(s,2.2)*uGlow*.10;
      col=mix(col,uHor*.92, smoothstep(.06,-.35,d.y));
      gl_FragColor=vec4(col,1.);}`
  }));
  sky.frustumCulled=false; scene.add(sky);

  /* stars */
  const starPos=[];
  for(let i=0;i<820;i++){ const a=Math.random()*Math.PI*2, e=Math.random()*.9+.08;
    starPos.push(Math.cos(a)*Math.cos(e)*470, Math.sin(e)*470, Math.sin(a)*Math.cos(e)*470); }
  const starGeo=new THREE.BufferGeometry(); starGeo.setAttribute('position',new THREE.Float32BufferAttribute(starPos,3));
  const starMat=new THREE.PointsMaterial({size:1.9,sizeAttenuation:false,color:0xdce9ff,transparent:true,opacity:0,fog:false,depthWrite:false});
  scene.add(new THREE.Points(starGeo,starMat));

  /* lights */
  const sun=new THREE.DirectionalLight(0xffffff,1.2);
  sun.castShadow=true; sun.shadow.mapSize.set(2048,2048);
  const sc=sun.shadow.camera; sc.left=-86; sc.right=86; sc.top=86; sc.bottom=-86; sc.near=1; sc.far=320;
  sun.shadow.bias=-.0006; sun.shadow.normalBias=.55;
  sun.target.position.set(4,0,10); scene.add(sun.target, sun);
  const hemi=new THREE.HemisphereLight(0x9ecde8,0x3c4a44,.5); scene.add(hemi);
  const lampLights=[];
  function lampLight(x,y,z,col,dist){ const p=new THREE.PointLight(col,0,dist,2); p.position.set(x,y,z); scene.add(p); lampLights.push(p); return p; }

  /* soft glow sprite factory */
  function radialTex(inner, mid){
    const cv=document.createElement('canvas'); cv.width=cv.height=128;
    const g=cv.getContext('2d').createRadialGradient(64,64,0,64,64,64);
    g.addColorStop(0,inner); g.addColorStop(.35,mid); g.addColorStop(1,'rgba(255,180,90,0)');
    const cc=cv.getContext('2d'); cc.fillStyle=g; cc.fillRect(0,0,128,128);
    const t=new THREE.CanvasTexture(cv); t.colorSpace=THREE.SRGBColorSpace; return t;
  }
  const glowTex=radialTex('rgba(255,240,210,1)','rgba(255,190,110,.55)');
  const sunTex=radialTex('rgba(255,255,250,1)','rgba(255,220,160,.45)');
  const moonTex=radialTex('rgba(230,240,255,1)','rgba(190,215,255,.3)');

  const sunSprite=new THREE.Sprite(new THREE.SpriteMaterial({map:sunTex,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,fog:false}));
  sunSprite.scale.set(90,90,1); scene.add(sunSprite);
  const moonSprite=new THREE.Sprite(new THREE.SpriteMaterial({map:moonTex,transparent:true,opacity:0,depthWrite:false,blending:THREE.AdditiveBlending,fog:false}));
  moonSprite.scale.set(42,42,1); scene.add(moonSprite);

  /* ═══════════════════════ materials ═══════════════════════ */
  const matSolid=new THREE.MeshLambertMaterial({vertexColors:true});
  const matGlow =new THREE.MeshLambertMaterial({vertexColors:true, emissive:0xffffff, emissiveIntensity:0, emissiveMap:null});
  matGlow.emissive=new THREE.Color(0xffb45a);
  const matCloud=new THREE.MeshLambertMaterial({vertexColors:true, emissive:new THREE.Color(0x223040), emissiveIntensity:.35});

  /* ═══════════════════════ BUILD: water ═══════════════════════ */
  const world=new VoxelSet();
  let waterMesh, waterGeoCount=0, seaPlane;
  const wCells=[];

  function buildWater(){
    const R=60;
    for(let x=-R;x<=R;x++) for(let z=-R;z<=R;z++){
      if(x*x+(z-6)*(z-6)>R*R) continue;
      if(landHeight(x,z)) continue;
      if(world.solid.has(x,0,z)) continue;
      wCells.push([x,z]);
    }
    // BFS distance-to-land for depth + shore foam
    const idx=new Map(); wCells.forEach((cc,i)=>idx.set(Vox.key(cc[0],0,cc[1]),i));
    const dist=new Int16Array(wCells.length).fill(-1); const q=[];
    for(let i=0;i<wCells.length;i++){
      const [x,z]=wCells[i]; let edge=false;
      for(const d of [[1,0],[-1,0],[0,1],[0,-1]]){
        const L=landHeight(x+d[0],z+d[1]); if(L){edge=true;break;}
        if(world.solid.has(x+d[0],0,z+d[1])||world.solid.has(x+d[0],1,z+d[1])){edge=true;break;}
      }
      if(edge){ dist[i]=0; q.push(i); }
    }
    let head=0;
    while(head<q.length){
      const i=q[head++], [x,z]=wCells[i];
      for(const d of [[1,0],[-1,0],[0,1],[0,-1]]){
        const j=idx.get(Vox.key(x+d[0],0,z+d[1]));
        if(j!==undefined && dist[j]<0){ dist[j]=dist[i]+1; q.push(j); }
      }
    }
    // ship footprint for the hull collar of foam
    const SHIP={x:11,z:3,rot:-.075};
    const n=wCells.length;
    const tint=new Float32Array(n*3), shelter=new Float32Array(n), foam=new Float32Array(n), seed=new Float32Array(n);
    const deep=new THREE.Color(0x1b4a61), mid=new THREE.Color(0x2c7688), shal=new THREE.Color(0x63b7ae), sandc=new THREE.Color(0xc9b184);
    for(let i=0;i<n;i++){
      const [x,z]=wCells[i];
      const d=dist[i]<0?18:dist[i];
      const t=c01(d/13);
      const col=new THREE.Color().copy(sandc).lerp(shal,c01(t*1.7)).lerp(mid,c01((t-.18)*1.5)).lerp(deep,c01((t-.5)*1.7));
      const s=h1(x*3.1+z*7.7); col.multiplyScalar(.94+s*.12);
      tint[i*3]=col.r; tint[i*3+1]=col.g; tint[i*3+2]=col.b;
      shelter[i]=shelterAt(x,z);
      let fm = d<=0? .92 : d<=1? .5 : d<=2? .2 : 0;
      const dx=x-SHIP.x, dz=z-SHIP.z;
      const lx=dx*Math.cos(SHIP.rot)-dz*Math.sin(SHIP.rot), lz=dx*Math.sin(SHIP.rot)+dz*Math.cos(SHIP.rot);
      const e=Math.hypot(lx/17.5, lz/6.4);
      if(e<1.3 && e>0.86) fm=Math.max(fm, .72*(1-Math.abs(e-1.06)/.26));
      if(Math.abs(lz)<5 && Math.abs(lx)<15 && e<=.92) fm=Math.max(fm,.16);
      foam[i]=fm;
      seed[i]=h1(x*11.3+z*2.9);
    }
    waterGeoCount=n;
    const g=new THREE.BoxGeometry(.97,1,.97); g.translate(0,-.5,0);
    g.setAttribute('aTint', new THREE.InstancedBufferAttribute(tint,3));
    g.setAttribute('aShelter', new THREE.InstancedBufferAttribute(shelter,1));
    g.setAttribute('aFoam', new THREE.InstancedBufferAttribute(foam,1));
    g.setAttribute('aSeed', new THREE.InstancedBufferAttribute(seed,1));
    const m=new THREE.MeshPhongMaterial({color:0xffffff, shininess:52, specular:0xa8cfd8, flatShading:true});
    m.onBeforeCompile=(sh)=>{
      sh.uniforms.uTime=uTime; sh.uniforms.uWind=uWind; sh.uniforms.uWaterTint=uWaterTint; sh.uniforms.uRip=uRip;
      sh.vertexShader=sh.vertexShader
        .replace('#include <common>',`#include <common>
          attribute vec3 aTint; attribute float aShelter; attribute float aFoam; attribute float aSeed;
          uniform float uTime; uniform float uWind; uniform vec4 uRip[6];
          varying vec3 vTint; varying float vFoam;
          float wv(vec2 p,float t){ return sin(p.x*.30+t*1.25)*.42 + sin(p.y*.26-t*1.02)*.38
            + sin((p.x+p.y)*.17+t*.72)*.30 + sin((p.x-p.y*.7)*.53-t*2.05)*.14; }
          float ripSum(vec2 p,float t,out float ring){ float s=0.; ring=0.;
            for(int i=0;i<6;i++){ vec4 r=uRip[i]; if(r.z<0.) continue; float age=t-r.z;
              if(age<0.||age>5.) continue; float d=distance(p,r.xy);
              s+=sin(d*2.3-age*7.)*exp(-d*.40)*exp(-age*1.2)*r.w;
              ring+=exp(-abs(d-age*5.2)*2.2)*exp(-age*1.1)*r.w; }
            return s; }`)
        .replace('#include <beginnormal_vertex>',`#include <beginnormal_vertex>
          vec3 iO=vec3(instanceMatrix[3].xyz);
          float amp=(.12+.44*uWind)*mix(1.,.22,aShelter);
          float t2=uTime*(.85+.35*uWind)+aSeed*3.1;
          float ring; float rp=ripSum(iO.xz,uTime,ring);
          float hh=wv(iO.xz,t2)*amp + rp*.55;
          float e=.62;
          float hx=(wv(iO.xz+vec2(e,0.),t2)-wv(iO.xz-vec2(e,0.),t2))*amp/(2.*e);
          float hz=(wv(iO.xz+vec2(0.,e),t2)-wv(iO.xz-vec2(0.,e),t2))*amp/(2.*e);
          if(objectNormal.y>.5) objectNormal=normalize(vec3(-hx,1.,-hz));
          float crest=smoothstep(.42,.95,wv(iO.xz,t2))*(.22+.55*uWind);
          vFoam=clamp(aFoam+crest+ring*1.3,0.,1.);
          vTint=aTint;`)
        .replace('#include <begin_vertex>',`#include <begin_vertex>
          transformed.y+=hh;`)
        .replace('#include <common2>','');
      sh.fragmentShader=sh.fragmentShader
        .replace('#include <common>',`#include <common>
          uniform vec3 uWaterTint; varying vec3 vTint; varying float vFoam;`)
        .replace('#include <map_fragment>',`#include <map_fragment>
          diffuseColor.rgb*=vTint*uWaterTint;
          diffuseColor.rgb=mix(diffuseColor.rgb, vec3(.87,.96,.97), vFoam);`);
    };
    waterMesh=new THREE.InstancedMesh(g,m,n);
    waterMesh.receiveShadow=true; waterMesh.frustumCulled=false;
    const mtx=new THREE.Matrix4();
    for(let i=0;i<n;i++){ mtx.setPosition(wCells[i][0]+.5, 0, wCells[i][1]+.5); waterMesh.setMatrixAt(i,mtx); }
    waterMesh.instanceMatrix.needsUpdate=true;
    scene.add(waterMesh);

    seaPlane=new THREE.Mesh(new THREE.PlaneGeometry(1400,1400), new THREE.MeshLambertMaterial({color:0x1d5069}));
    seaPlane.rotation.x=-Math.PI/2; seaPlane.position.set(0,-.62,0); scene.add(seaPlane);
  }

  /* ═══════════════════════ BUILD: land ═══════════════════════ */
  function buildLand(){
    const V=world.solid;
    for(let x=-58;x<=58;x++) for(let z=-44;z<=60;z++){
      const L=landHeight(x,z); if(!L) continue;
      const h=L.h;
      const nearWater = !landHeight(x,z-1) || !landHeight(x-1,z) || !landHeight(x+1,z) || !landHeight(x,z+1);
      for(let y=h;y>=h-3;y--){
        let col;
        if(L.k==='quay'){
          col = y===h ? (h1(x*2.7+z*5.1)>.5?PAL.quayTop:PAL.quayTop2) : PAL.wall;
          if(y===h && z<=QUAY_EDGE+1) col=PAL.wallHi;
          if(y<=0) col=PAL.wallWet;
          if(y===1||y===0) col=new THREE.Color(PAL.wallWet).lerp(c(PAL.tar),.4);
        } else if(L.k==='rock'){
          col = y===h ? (h1(x*3.3+z*1.9)>.72?PAL.moss:PAL.rockDk) : (h1(x,y,z)>.5?PAL.rock:PAL.rockDk);
          if(nearWater && Math.abs(y-h)<=1 && h1(x*5+z*3)>.6) col=PAL.sandWet;
        } else {
          col = y===h ? (h1(x*2.2+z*7.7)>.45?PAL.dune:PAL.grass) : (h>2?PAL.grassDk:PAL.sand);
          if(y<=0) col=PAL.sandWet;
        }
        const t=tint(0xffffff,.09,h3(x,y,z));
        V.set(x,y,z,new THREE.Color(col.r*t.r,col.g*t.g,col.b*t.b));
      }
    }
    /* quay edge furniture line: pale coping stone + wet band */
    for(let x=QUAY_X0;x<=QUAY_X1;x++){
      V.set(x,QUAY_Y,QUAY_EDGE, tint(PAL.wallHi,.06,h3(x,1,1)));
      V.set(x,0,QUAY_EDGE, tint(PAL.tar,.05,h3(x,2,2)));
      V.set(x,1,QUAY_EDGE, tint(PAL.wallWet,.06,h3(x,3,3)));
      if(x%7===0) for(let y=-2;y<=0;y++) V.set(x,y,QUAY_EDGE-1, tint(PAL.ironDk,.1,h3(x,y,9))); // tie rods
    }
    /* breakwater */
    for(let x=BW_A[0]-4;x<=BW_B[0]+4;x++) for(let z=BW_B[1]-5;z<=BW_A[1]+5;z++){
      const t=breakwaterTop(x,z); if(t===null) continue;
      for(let y=-1;y<=t;y++){
        const col = y===t? (h1(x*3.7+z*1.3)>.5?PAL.rockLt:PAL.rock) : (h1(x,y,z)>.5?PAL.rock:PAL.rockDk);
        V.set(x,y,z,tint(col,.1,h3(x,y,z)));
      }
    }
    /* lighthouse pad: dressed masonry */
    for(let x=LH_X-6;x<=LH_X+6;x++) for(let z=LH_Z-6;z<=LH_Z+6;z++){
      const L=landHeight(x,z); if(!L) continue;
      if(L.h<9){ for(let y=L.h;y<=8;y++) V.set(x,y,z,tint(PAL.wall,.07,h3(x,y,z))); }
      for(let y=9;y<=9;y++) V.set(x,y,z,tint(PAL.wallHi,.05,h3(x,y,z)));
      if(L.h>9){ for(let y=9;y<L.h;y++) V.set(x,y,z,tint(PAL.rockDk,.07,h3(x,y,z))); V.set(x,9? L.h:L.h,z,tint(PAL.wallHi,.05,h3(x,5,z))); }
    }
    /* steps from the quay down to a slipway at the east end */
    for(let i=0;i<7;i++) for(let z=QUAY_EDGE-1-i;z<=QUAY_EDGE;z++) V.set(38+ (i%2), QUAY_Y-1-i, z, tint(PAL.wallHi,.05,h3(i,1,z)));
  }

  /* ═══════════════════════ BUILD: town + quay furniture ═══════════════════════ */
  const POIS=[];
  function mark(x,y,z,name,sub,cam){ POIS.push({p:new THREE.Vector3(x,y,z),name,sub,cam}); }

  function house(V,G,x0,z0,w,d,h,wallHex,roofHex,opt={}){
    const y0=QUAY_Y+1;
    box(V,x0,x0+w-1,y0,y0+h-1,z0,z0+d-1,wallHex,.06,true);
    // interior void
    for(let x=x0+1;x<=x0+w-2;x++)for(let y=y0+1;y<=y0+h-2;y++)for(let z=z0+1;z<=z0+d-2;z++){
      const k=Vox.key(x,y,z); V.solid.m.delete(k);
    }
    box(V,x0,x0+w-1,y0+h-1,z0,z0+d-1,opt.floorHex||PAL.woodDk,.05,false); // ceiling
    roof(V,x0-1,x0+w,y0+h,z0-1,z0+d,roofHex,(z0+z0+d)/2);
    // windows on the sea-facing (-z) wall
    const glow = opt.glow!==false;
    for(let x=x0+1;x<=x0+w-2;x+=2){
      for(let wy=y0+2; wy<y0+h-1; wy+=3){
        V.solid.set(x,wy,z0, tint(PAL.woodDk,.05,.5));
        if(glow) G.set(x,wy,z0, c(PAL.glass));
      }
    }
    if(opt.door){ const dx=opt.doorX??(x0+Math.floor(w/2)); G.set(dx,y0,z0,c(0xffdca8)); V.set(dx,y0-0,z0,tint(PAL.woodDk,.05,.4)); }
  }

  function lampPost(V,G,x,z,y=QUAY_Y+1){
    box(V,x,y,z,x,y+4,z,PAL.iron,.05);
    box(V,x-1,y+4,z-1,x+1,y+4,z+1,PAL.ironDk,.05);
    G.set(x,y+5,z,c(0xffcf8a));
    box(V,x-1,y+6,z-1,x+1,y+6,z+1,PAL.ironDk,.05);
    box(V,x,y+7,z,x,y+7,z,PAL.copper,.08);
  }
  function bollard(V,x,z,y=QUAY_Y+1){
    box(V,x,y,z,x,y+1,z,PAL.iron,.06); box(V,x,y+2,z,x,y+2,z,PAL.ironDk,.05);
  }
  function barrel(V,cx,cy,cz,hex=PAL.woodLt){
    box(V,cx-1,cx+1,cy,cy+1,cz-1,cz+1,hex,.08);
    box(V,cx-1,cx+1,cy+1,cz-1,cz+1,PAL.ironDk,.05,false);
    V.solid.delete && 0;
    for(const [dx,dz] of [[-1,-1],[-1,1],[1,-1],[1,1]]) V.solid.m.delete(Vox.key(cx+dx,cy+1,cz+dz));
  }
  function crate(V,x,y,z,s=1,hex=PAL.plank){ box(V,x,x+s-1,y,y+s-1,z,z+s-1,hex,.09); box(V,x,x+s-1,y+s-1,z,z+s-1,PAL.woodDk,.06); }
  function figure(V,x,y,z,shirt,pants,h=2){
    box(V,x,y,z,x,y,z,PANTS??pants,.05); box(V,x,y+1,z,x,y+h,z,shirt,.07);
    V.set(x,y+h+1,z,tint(0xe0b48c,.05,.5));
  }
  const PANTS=PAL.tar;

  function buildTown(){
    const V=world.solid, G=world.glow;
    /* ── warehouses along the quay ───────────────────────── */
    // big brick warehouse, sawtooth-ish roof + hoist
    house(V,G,-16,20,16,11,8,PAL.brickR,PAL.roofS,{door:true,doorX:-9});
    box(V,-9,QUAY_Y+9,19,-9,QUAY_Y+9,19,PAL.woodDk,.05);
    box(V,-12,QUAY_Y+9,22,-12,QUAY_Y+9,22,PAL.woodDk,.05);
    // hoist beam
    line(V,[-9,QUAY_Y+10,19],[-9,QUAY_Y+10,15],PAL.wood,.05);
    line(V,[-9,QUAY_Y+11,19],[-9,QUAY_Y+11,16],PAL.wood,.05);
    // customs house with tower + copper dome
    house(V,G,-4,18,13,10,6,PAL.render1,PAL.roofR,{door:true,doorX:3});
    box(V,1,QUAY_Y+1,19,4,QUAY_Y+16,22,PAL.render2,.05,true);
    box(V,1,QUAY_Y+1,19,4,QUAY_Y+16,22,PAL.render2,.05,true);
    for(let y=QUAY_Y+2;y<QUAY_Y+16;y++){ V.set(2,y,19,c(0)); G.set(2,y,19,c(0xffdca8)); }
    box(V,0,QUAY_Y+16,18,5,QUAY_Y+17,23,PAL.render2,.05);
    archTower(V,2.5,QUAY_Y+18,20.5,2.6,PAL.render1);
    G.set(2,QUAY_Y+15,19,c(0xffe0aa)); // clock face
    dome(V,2.5,QUAY_Y+21,20.5,2.5,PAL.copper);
    box(V,2,QUAY_Y+24,20,3,QUAY_Y+25,21,PAL.brass,.06);
    // row of townhouses east
    const hx=[8,13,18,23,28,33];
    hx.forEach((x,i)=>{
      const w=4, d=8, h=5+(i%2);
      house(V,G,x,19,w,d,h,[PAL.brickY,PAL.render2,PAL.brickP,PAL.render1,PAL.brickR,PAL.brickY][i%6],
            [PAL.roofR,PAL.slate,PAL.roofT,PAL.roofR,PAL.slate,PAL.roofT][i%6],{door:i%2===0});
      if(i%2===0){ box(V,x+1,QUAY_Y+h+1,22,x+2,QUAY_Y+h+3,22,PAL.brickR,.06); }
    });
    // church / town tower further east
    house(V,G,37,24,9,10,6,PAL.render2,PAL.slate,{});
    box(V,39,QUAY_Y+1,26,42,QUAY_Y+13,29,PAL.render1,.05,true);
    for(let y=QUAY_Y+8;y<QUAY_Y+12;y++) G.set(40,y,26,c(0xffd9a0));
    box(V,38,QUAY_Y+13,25,43,QUAY_Y+14,30,PAL.render1,.05);
    archTower(V,40.5,QUAY_Y+15,27.5,2.2,PAL.render2);
    dome(V,40.5,QUAY_Y+17,27.5,2.1,PAL.copper);

    /* ── fish market: open shed, awnings, crates ───────── */
    const mx=-14, mz=15;
    for(let i=0;i<4;i++){ box(V,mx+i*4,QUAY_Y+1,mz,mx+i*4,QUAY_Y+4,mz,PAL.woodDk,.05);
                          box(V,mx+i*4,QUAY_Y+1,mz+6,mx+i*4,QUAY_Y+4,mz+6,PAL.woodDk,.05); }
    box(V,mx-1,mx+12,QUAY_Y+5,QUAY_Y+5,mz-1,mz+7,PAL.wood,.06);
    for(let i=0;i<12;i++) for(let z=mz-1;z<=mz+1;z++) V.set(mx+i,QUAY_Y+4,z, tint(i%2?PAL.white:PAL.red,.05,h1(i*3+z)));
    for(let i=0;i<9;i++){ crate(V,mx+1+i*1.5,QUAY_Y+1,mz+3+ (i%2)*2,1,i%2?PAL.fish:PAL.plank); }
    for(let i=0;i<5;i++) barrel(V,mx+2+i*3,QUAY_Y+1,mz+8,PAL.woodLt);
    figure(V,mx+3,QUAY_Y+1,mz+2,PAL.red,PAL.tar); figure(V,mx+8,QUAY_Y+1,mz+5,PAL.blue,PAL.iron);
    figure(V,mx+11,QUAY_Y+1,mz+2,PAL.green,PAL.tar);

    /* ── quay edge: bollards, barrels, crates, coils, folk ─ */
    for(let x=QUAY_X0+1;x<=QUAY_X1-1;x+=4) bollard(V,x,QUAY_EDGE+1);
    for(let i=0;i<9;i++){ barrel(V,-3+i*4, QUAY_Y+1, QUAY_EDGE+3, i%3?PAL.woodLt:PAL.woodDk); }
    for(let i=0;i<7;i++) crate(V,17+i*2,QUAY_Y+1,QUAY_EDGE+4+ (i%2)*2, 1+i%2, PAL.plank);
    // net frames + drying nets
    for(let i=0;i<4;i++){ const x=-19+i*3; line(V,[x,QUAY_Y+1,QUAY_EDGE+6],[x,QUAY_Y+5,QUAY_EDGE+6],PAL.wood,.05);
      line(V,[x+2,QUAY_Y+1,QUAY_EDGE+6],[x+2,QUAY_Y+5,QUAY_EDGE+6],PAL.wood,.05);
      for(let z=QUAY_EDGE+6;z<=QUAY_EDGE+8;z++) for(let y=QUAY_Y+2;y<=QUAY_Y+4;y++) if(h1(x,y*7+z*3)>.42) V.set(x+1,y,z,tint(PAL.net,.1,h3(x,y,z))); }
    // promenade lamps + people
    const lampX=[-15,-7,1,9,17,25,33,41];
    lampX.forEach((x,i)=>{ lampPost(V,G,x,QUAY_EDGE+3); });
    lampLight(1,QUAY_Y+7,QUAY_EDGE+3,0xffc078,42);
    lampLight(25,QUAY_Y+7,QUAY_EDGE+3,0xffc078,42);
    const skins=[0xe0b48c,0xc98f68,0x8d5a3c];
    for(let i=0;i<24;i++){
      const x=Math.round(lerp(QUAY_X0+2,QUAY_X1-4,h1(i*4.1)));
      const z=Math.round(lerp(QUAY_EDGE+2,QUAY_EDGE+9,h1(i*9.7)));
      const y=QUAY_Y+1;
      const shirt=[PAL.red,PAL.blue,PAL.green,PAL.cream,PAL.tar,PAL.brass][i%6];
      box(V,x,y,z,x,y,z,PAL.tar,.05); box(V,x,y+1,z,x,y+2,z,shirt,.07);
      V.set(x,y+3,z,tint(skins[i%3],.05,h1(i)));
    }
    // two-wheeled cart with a barrel
    box(V,5,QUAY_Y+1,QUAY_EDGE+7,8,QUAY_Y+2,QUAY_EDGE+9,PAL.wood,.06);
    box(V,5,QUAY_Y+3,QUAY_EDGE+8,8,QUAY_Y+3,QUAY_EDGE+8,PAL.woodDk,.05);
    for(const dx of [5,8]) for(const dz of [QUAY_EDGE+7,QUAY_EDGE+9]){
      for(let k=0;k<3;k++){ const a=k/3*Math.PI*2; V.set(Math.round(dx),QUAY_Y+1+Math.round(Math.sin(a)*1),QUAY_EDGE+ (dz===QUAY_EDGE+7?7:9),tint(PAL.woodDk,.05,.5)); }
    }
    barrel(V,6,QUAY_Y+3,QUAY_EDGE+8,PAL.woodLt);

    /* ── timber gantry crane (static base) ─────────────── */
    const cx=20, cz=QUAY_EDGE+1;
    box(V,cx-1,cx+1,QUAY_Y+1,cz,cz,PAL.woodDk,.05);
    for(const s of [-1,1]){ line(V,[cx+s,QUAY_Y+1,cz-2],[cx+s*3.4,QUAY_Y+12,cz],PAL.wood,.05);
                            line(V,[cx+s,QUAY_Y+1,cz+2],[cx+s*3.4,QUAY_Y+12,cz],PAL.wood,.05); }
    box(V,cx-3,cx+3,QUAY_Y+12,cz-1,cz+1,PAL.woodDk,.05);
    box(V,cx-1,cx+1,QUAY_Y+13,cz-1,cz+1,PAL.iron,.05);

    /* ── Long Wharf: timber pier reaching seaward ─────── */
    const PX0=-16,PX1=2,PZ0=-8,PZ1=QUAY_EDGE+1;
    for(let x=PX0;x<=PX1;x++) for(let z=PZ0;z<=PZ1;z++)
      V.set(x,QUAY_Y+2,z, tint(h1(x*3+z*7)>.5?PAL.plank:PAL.wood,.07,h3(x,3,z)));
    for(let x=PX0+1;x<=PX1;x+=3) for(let z=PZ0;z<=PZ1;z+=4){
      for(let y=-2;y<=QUAY_Y+1;y++) V.set(x,y,z,tint(PAL.woodDk,.06,h3(x,y,z)));
    }
    for(let x=PX0;x<=PX1;x++){ V.set(x,QUAY_Y+3,PZ0,tint(PAL.woodDk,.05,h1(x))); V.set(x,QUAY_Y+3,PZ1,tint(PAL.woodDk,.05,h1(x*2))); }
    for(let z=PZ0;z<=PZ1;z++){ V.set(PX0,QUAY_Y+3,z,tint(PAL.woodDk,.05,h1(z))); V.set(PX1,QUAY_Y+3,z,tint(PAL.woodDk,.05,h1(z*3))); }
    for(let i=0;i<6;i++) bollard(V,PX0+1+ (i%2?0:1), PZ0+2+i*4, QUAY_Y+3);
    lampPost(V,G,PX0+2,PZ0+1,QUAY_Y+3); lampPost(V,G,PX1-2,PZ0+1,QUAY_Y+3);
    lampLight(-12,QUAY_Y+9,PZ0+1,0xffc078,38);
    for(let i=0;i<5;i++){ barrel(V,PX0+3+i*3,QUAY_Y+3,PZ0+3, i%2?PAL.woodLt:PAL.wood); }
    crate(V,PX1-3,QUAY_Y+3,PZ0+2,2,PAL.plank); crate(V,PX1-3,QUAY_Y+4,PZ0+2,1,PAL.woodDk);
    // dinghy hauled up on the wharf
    box(V,PX0+4,PX0+9,QUAY_Y+3,PZ0+6,PX0+9,PX0+9,PAL.woodLt,.06);
    for(let x=PX0+5;x<=PX0+8;x++) for(let z=PX0+7;z<=PX0+8;z++) V.set(x,QUAY_Y+4,z,tint(PAL.woodDk,.06,h3(x,9,z)));

    /* ── headland: lighthouse + keeper's cottage + beacon ─ */
    buildLighthouse(V,G);
    // keeper's cottage
    const lhy=landHeight(LH_X+7,LH_Z+6)?.h ?? 8;
    house2(V,G,LH_X+6,LH_Z+5,6,5,3,lhy+1,PAL.render1,PAL.roofR);
    // breakwater beacon
    const bt=breakwaterTop(BW_A[0],BW_A[1])??2;
    box(V,BW_A[0]-1,BW_A[0]+1,-1,BW_A[1]-1,BW_A[1]+1,bt+1,PAL.white,.05);
    box(V,BW_A[0],BW_A[0],bt+2,bt+4,BW_A[1],BW_A[1],PAL.red,.05);
    G.set(BW_A[0],bt+5,BW_A[1],c(0xff6a4a));
    box(V,BW_A[0],BW_A[0],bt+6,bt+6,BW_A[1],BW_A[1],PAL.ironDk,.05);
    lampLight(BW_A[0],bt+6,BW_A[1],0xff5a3a,34);
    // rocky path + daymarks
    for(let i=0;i<16;i++){ const x=Math.round(lerp(LH_X,-16,i/15)), z=Math.round(lerp(LH_Z+3,4,i/15));
      const L=landHeight(x,z); if(L) box(V,x-1,L.h,x+1,L.h,z-1,z+1,PAL.wallHi,.06); }

    /* ── dunes, windmill, trees ───────────────────────── */
    const trees=[[ -24,15],[-28,19],[-31,24],[-26,28],[-19,26],[-8,31],[-3,28],[6,32],[14,30],[26,33],[31,29],[41,20],[44,17],[-13,13]];
    for(const [x,z] of trees){
      const L=landHeight(x,z); if(!L) continue;
      if(L.k==='quay' && z<QUAY_EDGE+2) continue;
      const y=L.h+1, hh=2+Math.round(h1(x*3+z)*2);
      box(V,x,y,z,x,y+hh,z,PAL.woodDk,.06);
      const r=1+Math.round(h1(x+z*2));
      for(let dx=-r;dx<=r;dx++)for(let dz=-r;dz<=r;dz++)for(let dy=0;dy<=r+1;dy++){
        if(Math.abs(dx)+Math.abs(dz)+dy>r+1) continue;
        V.set(x+dx,y+hh+dy,z+dz, tint(h1(x+dx,z+dz,y+dy)>.5?PAL.grass:PAL.grassDk,.12,h3(x+dx,y+hh+dy,z+dz)));
      }
    }
    // windmill on the east dune
    const wmx=52, wmz=30, wl=landHeight(wmx,wmz)?.h??3;
    box(V,wmx-2,wmx+2,wl+1,wl+7,wmz-2,wmz+2,PAL.render1,.05);
    box(V,wmx-1,wmx+1,wl+8,wl+8,wmz-1,wmz+1,PAL.woodDk,.05);
    box(V,wmx-1,wmx+1,wl+9,wl+9,wmz-1,wmz+1,PAL.copper,.08);
    return {craneX:cx, craneZ:cz};
  }
  function archTower(V,cx,y,cz,r,hex){
    for(let i=0;i<3;i++){ const yy=y+i;
      for(let x=Math.floor(cx-r);x<=Math.ceil(cx+r);x++)
        for(let z=Math.floor(cz-r);z<=Math.ceil(cz+r);z++){
          const d=Math.hypot(x+.5-cx,z+.5-cz);
          if(d<=r+.2 && d>r-1.1) V.set(x,yy,z,tint(hex,.06,h3(x,yy,z)));
        } }
  }
  function dome(V,cx,y,cz,r,hex){
    for(let dy=0;dy<r;dy++){ const rr=Math.sqrt(Math.max(0,r*r-dy*dy));
      for(let x=Math.floor(cx-rr);x<=Math.ceil(cx+rr);x++)
        for(let z=Math.floor(cz-rr);z<=Math.ceil(cz+rr);z++){
          const d=Math.hypot(x+.5-cx,z+.5-cz);
          if(d<=rr+.15) V.set(x,y+dy,z,tint(hex,.09,h3(x,y+dy,z)));
        } }
  }
  function house2(V,G,x0,z0,w,d,h,y0,wallHex,roofHex){
    box(V,x0,x0+w-1,y0,y0+h-1,z0,z0+d-1,wallHex,.06,true);
    for(let x=x0+1;x<=x0+w-2;x++)for(let y=y0+1;y<=y0+h-2;y++)for(let z=z0+1;z<=z0+d-2;z++) V.solid.m.delete(Vox.key(x,y,z));
    roof(V,x0-1,x0+w,y0+h,z0-1,z0+d,roofHex,(z0+z0+d)/2);
    G.set(x0+1,y0+2,z0,c(PAL.glass)); G.set(x0+w-2,y0+2,z0,c(PAL.glass));
  }
  function buildLighthouse(V,G){
    const y0=10, x=LH_X, z=LH_Z;
    box(V,x-4,x+4,y0-1,y0-1,z-4,z+4,PAL.wall,.05);
    const rings=[[3,3,0,5],[3,3,5,7],[2,2,7,10],[2,2,10,13],[1,1,13,15]];
    for(const [r0,r1,a,b] of rings){
      for(let yy=y0+a; yy<y0+b; yy++){
        const t=(yy-(y0+a))/Math.max(1,(b-a-1)); const r=Math.round(lerp(r0,r1,t));
        for(let dx=-r;dx<=r;dx++)for(let dz=-r;dz<=r;dz++){
          if(Math.max(Math.abs(dx),Math.abs(dz))<r && !(dx===0||dz===0)) continue;
          const band=(Math.floor((yy-y0)/3)%2===0);
          V.set(x+dx,yy,z+dz, tint(band?PAL.white:PAL.red,.05,h3(x+dx,yy,z+dz)));
        }
      }
    }
    // gallery + lantern room
    box(V,x-2,x+2,y0+15,y0+15,z-2,z+2,PAL.iron,.05);
    box(V,x-1,x+1,y0+16,y0+18,z-1,z+1,PAL.glass,.04,true);
    for(let yy=y0+16;yy<=y0+18;yy++){ G.set(x-1,yy,z,c(0xffe4b0)); G.set(x+1,yy,z,c(0xffe4b0));
      G.set(x,yy,z-1,c(0xffe4b0)); G.set(x,yy,z+1,c(0xffe4b0)); }
    arch(V,x,y0+19,z,2,PAL.copper);
    line(V,[x,y0+21,z],[x,y0+24,z],PAL.iron,.05);
    mark(x, y0+17, z, 'Mireux Point Light', 'est. 1846 · 24 m · Fl(2) W 15s', {az:-2.05,pol:.30,dist:64,tx:x,tz:z,ty:y0+8});
    lampLight(x,y0+17,z,0xffd9a0,90);
  }

  /* ═══════════════════════ BUILD: the barque ═══════════════════════ */
  let shipGroup, shipSet, flagMeshes=[], davitBoat;
  function buildShip(){
    const S=new VoxelSet(), V=S.solid, G=S.glow;
    const L=16, keel=-3, deck=2;
    const halfBeam=t=>{ const s=Math.sin(Math.PI*Math.pow(c01(t),.68)); return 4.8*Math.pow(Math.max(0,s),.72); };
    for(let x=-L;x<=L;x++){
      const t=(x+L)/(2*L);
      const hb=halfBeam(t); if(hb<.45) continue;
      for(let y=keel;y<=deck;y++){
        const vs=.40+.60*Math.pow(c01((y-keel)/(deck-keel)),.85);
        const hw=hb*vs;
        for(let z=Math.floor(-hw);z<=Math.ceil(hw);z++){
          let col;
          if(y<=keel+1) col=PAL.hullUW;
          else if(y<=0) col=PAL.hull;
          else if(y<=1) col=PAL.stripe;
          else if(y<deck) col=PAL.hull;
          else col=PAL.wood;
          V.set(x,y,z,tint(col,.06,h3(x,y,z)));
        }
        // cannon ports on the black waist
        if(y===2 && x%3===0 && Math.abs(x)<12){
          V.set(x,y,Math.round(hw),tint(PAL.brass,.08,.5));
          V.set(x,y,Math.round(-hw),tint(PAL.brass,.08,.5));
        }
      }
      // deck
      for(let z=Math.floor(-hb);z<=Math.ceil(hb);z++) V.set(x,deck+1,z,tint(h1(x*3+z*5)>.5?PAL.plank:PAL.woodLt,.07,h3(x,3,z)));
      // bulwark
      for(const s of [-1,1]){
        const z=Math.round(hb*s);
        V.set(x,deck+2,z,tint(PAL.stripe,.05,h3(x,4,z)));
        V.set(x,deck+3,z,tint(PAL.hull,.05,h1(x)));
      }
    }
    // stern / bow closure + counter
    for(const sx of [-1,1]) for(let y=keel+1;y<=deck;y++) for(let z=-2;z<=2;z++){
      const xx = sx<0? -L+1 : L-1;
      V.set(xx,y,z,tint(sx<0?PAL.hullUW:PAL.hull,.06,h3(xx,y,z)));
    }
    box(V,-L+1,-L+1,0,1,-3,3,PAL.stripe,.05);
    // quarterdeck + forecastle
    box(V,-L+2,-3,deck+2,deck+2,-3,3,PAL.plank,.06);
    box(V,7,L-2,deck+2,deck+2,-4,4,PAL.plank,.06);
    // captain's cabin (glows at night)
    box(V,-L+2,-L+8,deck+3,deck+5,-3,3,PAL.stripe,.04,true);
    for(let x=-L+3;x<=-L+7;x+=1){ G.set(x,deck+4,-3,c(0xffd9a0)); G.set(x,deck+4,3,c(0xffd9a0)); V.solid.m.delete(Vox.key(x,deck+4,-3)); V.solid.m.delete(Vox.key(x,deck+4,3)); }
    box(V,-L+2,-L+8,deck+6,deck+6,-3,3,PAL.woodDk,.05);
    // stern lantern
    box(V,-L,-L,deck+5,deck+6,0,0,PAL.iron,.05); G.set(-L,deck+5,0,c(0xffdca0));
    // forecastle house
    box(V,9,12,deck+3,deck+4,-2,2,PAL.stripe,.05,true);
    G.set(10,deck+3,0,c(0xffd9a0));
    // hatch covers, barrels, cargo
    for(const hx of [2,5,-6]){ box(V,hx,hx+2,deck+2,deck+2,-2,2,PAL.sail2,.05); }
    barrel(V,0,deck+2,-3,PAL.woodLt); barrel(V,0,deck+2,3,PAL.woodLt);
    crate(V,4,deck+2,3,2,PAL.plank); crate(V,4,deck+4,3,1,PAL.woodDk);
    crate(V,8,deck+2,-4,2,PAL.plank);
    box(V,-2,-1,deck+2,deck+3,-1,1,PAL.woodDk,.05); // capstan
    // anchor
    line(V,[L-2,deck,-4],[L-2,deck-3,-4],PAL.iron,.05); box(V,L-2,L-2,deck-4,deck-3,-5,-3,PAL.iron,.05);
    line(V,[L-2,1,-4],[L-2,4,-4],PAL.iron,.05);
    /* masts, yards, sails */
    const masts=[{x:8,h:22,n:'fore'},{x:-2,h:26,n:'main'},{x:-11,h:19,n:'mizzen'}];
    for(const m of masts){
      for(let y=deck+2;y<=m.h;y++){
        const c2 = y>m.h-4? PAL.woodLt : (y%5===0? PAL.ironDk : PAL.wood);
        V.set(m.x,y,0,m.x,y,0,tint(c2,.06,h3(m.x,y,0))[0]??undefined);
        V.set(m.x,y,0,tint(c2,.06,h3(m.x,y,0)));
      }
      // top platform
      if(m.n!=='mizzen'){ box(V,m.x-1,m.x+1,m.h-7,m.h-7,-2,2,PAL.woodDk,.05); }
      // shrouds both sides
      for(const s of [-1,1]){
        for(let k=0;k<5;k++){
          const bz=(1.2+k*.85)*s;
          line(V,[m.x,deck+3,bz],[m.x,m.h-4,0],PAL.tar,.03);
        }
        // ratlines
        for(let yy=deck+4; yy<m.h-6; yy+=2) line(V,[m.x,yy,Math.round(1.4*s)],[m.x,yy,Math.round(4.2*s)],PAL.tar,.02);
      }
    }
    const yards=[
      {m:0,y:11,w:7.2, sail:.62},{m:0,y:15.4,w:6.0,sail:.18},{m:0,y:19,w:4.6,sail:0},{m:0,y:21.4,w:3.2,sail:0},
      {m:1,y:12,w:6.6, sail:.55},{m:1,y:17,w:5.6,sail:.15},{m:1,y:21,w:4.2,sail:0},{m:1,y:24.2,w:3,sail:0},
    ];
    for(const yd of yards){
      const mx=masts[yd.m].x, yy=Math.round(yd.y);
      for(let z=-Math.round(yd.w);z<=Math.round(yd.w);z++){
        const dip = Math.round(-Math.pow(Math.abs(z)/yd.w,2)*1.4);
        V.set(mx,yy+dip,z,tint(PAL.woodDk,.05,h3(mx,yy,z)));
        // furled sail: a bunt of canvas under the yard
        const span=Math.round(yd.w*(yd.sail||.16));
        if(Math.abs(z)<=span){
          V.set(mx,yy-2+dip,z,tint(yd.sail>.4?PAL.sail:PAL.sail2,.06,h3(mx,yy,z)));
          if(yd.sail>.4) V.set(mx,yy-3+dip,z,tint(PAL.sail,.07,h3(mx,yy,z+2)));
        }
        if(yd.sail>.4 && Math.abs(z)<=span){
          for(let k=1;k<=Math.round(yd.sail*4);k++) V.set(mx,yy-k-1+dip,z,tint(PAL.sail,.06,h3(mx,yy,z+k)));
        }
      }
      // lifts
      line(V,[mx,yy+1,Math.round(yd.w)],[mx,yy+3,0],PAL.tar,.02);
      line(V,[mx,yy+1,-Math.round(yd.w)],[mx,yy+3,0],PAL.tar,.02);
    }
    // bowsprit + jib boom
    line(V,[L-1,deck+3,0],[L+11,deck+8,0],PAL.wood,.05);
    line(V,[L+11,deck+8,0],[L+14,deck+9,0],PAL.woodLt,.05);
    line(V,[L+2,deck+5,0],[L+2,deck+4,0],PAL.tar,.02);
    for(let i=2;i<11;i+=2) V.set(L+i,deck+4+Math.round(i*.42),0,tint(PAL.sail2,.06,h1(i))); // furled jib
    line(V,[masts[0].x,masts[0].h-2,0],[L+13,deck+9,0],PAL.tar,.02); // forestay
    line(V,[masts[0].x,masts[0].h-3,0],[masts[1].x+1,masts[1].h-1,0],PAL.tar,.02);
    line(V,[masts[1].x,masts[1].h-2,0],[masts[0].x+1,masts[0].h,0],PAL.tar,.02);
    line(V,[masts[1].x,masts[1].h-1,0],[masts[2].x,masts[2].h,0],PAL.tar,.02);
    line(V,[masts[2].x,masts[2].h,0],[-L,deck+5,0],PAL.tar,.02);
    // mizzen gaff + boom + spanker
    line(V,[masts[2].x,deck+4,0],[-L-1,deck+5,0],PAL.wood,.05);
    line(V,[masts[2].x,m.h-2,0],[masts[2].x+3,m.h+2,0],PAL.wood,.05);
    for(let i=0;i<8;i++){ const t=i/8;
      for(let k=0;k<Math.round(4-2*t);k++)
        V.set(Math.round(lerp(masts[2].x+1,-L,t)), Math.round(lerp(m.h+1,deck+6,t))-k, 0, tint(PAL.sail,.06,h3(i,k,1)));
    }
    // ship's boat on davits
    davitBoat=new THREE.Group();
    { const B=new VoxelSet();
      box(B.solid,-2,2,0,1,-1,1,PAL.woodLt,.06);
      box(B.solid,-2,2,2,2,-1,1,PAL.wood,.05);
      B.solid.m.delete(Vox.key(-2,0,-1)); B.solid.m.delete(Vox.key(2,0,1));
      line(B.solid,[-2,1,0],[3,2,0],PAL.wood,.05);
      B.solid.count=8;
      const m=new THREE.Mesh(bake(B,'solid'), matSolid); m.castShadow=true; davitBoat.add(m);
    }
    davitBoat.position.set(2, deck+5, 5.6);
    shipGroup.add && 0;
    // rigging ladders / flags handled separately
    const meshSolid=new THREE.Mesh(bake(S,'solid'), matSolid);
    const meshGlow=new THREE.Mesh(bake(S,'glow'), matGlowGlow=new THREE.MeshLambertMaterial({vertexColors:true,emissive:new THREE.Color(0xffb45a),emissiveIntensity:0}));
    meshSolid.castShadow=true; meshSolid.receiveShadow=true;
    shipGroup=new THREE.Group();
    shipGroup.add(meshSolid, meshGlow, davitBoat);
    scene.add(shipGroup);
    shipSet=meshGlow;

    /* flags: animated, rippling */
    function flagTex(kind){
      const cv=document.createElement('canvas'); cv.width=32; cv.height=20;
      const g=cv.getContext('2d');
      if(kind==='ensign'){ g.fillStyle='#c1443a'; g.fillRect(0,0,32,20);
        g.fillStyle='#0f2f60'; g.fillRect(0,0,14,10);
        g.fillStyle='#fff'; g.fillRect(5,0,4,10); g.fillRect(0,3,14,4);
        g.fillStyle='#c1443a'; g.fillRect(6,0,2,10); g.fillRect(0,4,14,2);
      } else if(kind==='jack'){ g.fillStyle='#1e4f7a'; g.fillRect(0,0,32,20);
        g.fillStyle='#e8e2d2'; for(let i=0;i<32;i+=8) g.fillRect(i,0,2,20); for(let i=0;i<20;i+=6) g.fillRect(0,i,32,2);
      } else { g.fillStyle='#e8b73f'; g.beginPath(); g.moveTo(0,0); g.lineTo(32,10); g.lineTo(0,20); g.closePath(); g.fill();
        g.fillStyle='#c1443a'; g.fillRect(0,7,10,6); }
      const t=new THREE.CanvasTexture(cv); t.magFilter=THREE.NearestFilter; t.minFilter=THREE.NearestFilter; t.colorSpace=THREE.SRGBColorSpace; return t;
    }
    function makeFlag(kind,w,h,x,y,z,flip=false){
      const g=new THREE.PlaneGeometry(w,h,8,4); g.translate(w/2,0,0);
      const m=new THREE.MeshLambertMaterial({map:flagTex(kind),side:THREE.DoubleSide,transparent:true,alphaTest:.4});
      m.onBeforeCompile=(sh)=>{ sh.uniforms.uTime=uTime; sh.uniforms.uWind=uWind;
        sh.vertexShader=sh.vertexShader.replace('#include <common>',`#include <common>
          uniform float uTime; uniform float uWind;`)
        .replace('#include <begin_vertex>',`#include <begin_vertex>
          float u=uv.x; float amp=.10+.30*uWind;
          transformed.z += sin(u*7.0+uTime*(4.0+7.0*uWind))*amp*u;
          transformed.y += sin(u*4.5+uTime*3.2)*.07*u;
          transformed.x += (cos(u*7.0+uTime*(4.0+7.0*uWind))*0.06)*u;`);
      };
      const mesh=new THREE.Mesh(g,m); mesh.position.set(x,y,z);
      if(flip) mesh.rotation.y=Math.PI;
      shipGroup.add(mesh); flagMeshes.push(mesh); return mesh;
    }
    makeFlag('ensign',5,3.2,-L-1,m.h=19+2.6,0,false);
    makeFlag('jack',3.4,2.2,L+14,deck+9.6,0,true);
    makeFlag('pennant',3,1.4,masts[0].x,masts[0].h+1,0);
    makeFlag('pennant',3,1.4,masts[1].x,masts[1].h+1,0);
    makeFlag('pennant',2.6,1.2,masts[1].x,masts[1].h-6,0);

    lampLight(-L,deck+6,0,0xffc890,20);
    mark(masts[1].x, 18, 0, 'Barque “Aurelia”', '214 reg. tons · arrived 14:20, outbound with copper', {az:-2.62,pol:.20,dist:46,tx:8,tz:3,ty:9});
    mark(11, 5.5, 7.5, 'Mooring lines', 'hawser two-and-a-half inch · two bights on the Long Wharf', {az:-2.4,pol:.16,dist:30,tx:6,tz:5,ty:5});
    shipGroup.position.set(11,0,3);
    shipGroup.rotation.y=-.075;
  }

  /* ═══════════════════════ BUILD: animated odds & ends ═══════════════════════ */
  let craneJib, millSails, beamGroup, buoy, smokeMesh, walkers=[], gulls=[], cloudMesh, distantSails;

  function smallVoxMesh(fn, mat=matSolid){ const S=new VoxelSet(); fn(S); const m=new THREE.Mesh(bake(S,'solid'),mat);
    m.castShadow=true; m.receiveShadow=true; return m; }

  function buildAnimated(townInfo){
    /* rotating crane jib with a swinging crate */
    const jib=new THREE.Group();
    const jibMesh=smallVoxMesh(S=>{
      const V=S.solid;
      line(V,[0,0,0],[0,0,10],PAL.wood,.05); line(V,[0,1,0],[0,1,9],PAL.wood,.05);
      for(let i=1;i<9;i+=2){ line(V,[0,0,i],[0,1,i+1],PAL.woodDk,.04); line(V,[0,1,i],[0,0,i+1],PAL.woodDk,.04); }
      line(V,[0,0,0],[0,3,4],PAL.woodDk,.05); line(V,[0,3,4],[0,0,9],PAL.tar,.03);
      line(V,[0,0,9],[0,-3,9],PAL.tar,.03);
      box(V,-1,1,-4,-3,8,10,PAL.plank,.06);
      V.set(0,-3,9,tint(PAL.iron,.05,.5));
    });
    jib.add(jibMesh); jib.position.set(townInfo.craneX, QUAY_Y+13.5, townInfo.craneZ);
    craneJib=jib; scene.add(jib);

    /* windmill sails */
    const wmx=52, wmz=30, wl=7;
    const sails=new THREE.Group();
    const sm=smallVoxMesh(S=>{
      for(let i=0;i<7;i++){ S.solid.set(0,i+2,4+i,tint(PAL.woodDk,.05,h1(i)));
        for(let k=0;k<3;k++) S.solid.set(k,i+3,4+i,tint(PAL.sail2,.06,h1(i+k))); }
      S.solid.set(0,0,0,tint(PAL.iron,.05,.5));
    });
    sm.rotation.x=0; sails.add(sm);
    const sm2=sm.clone(); sm2.rotation.z=Math.PI/2; const sm3=sm.clone(); sm3.rotation.z=Math.PI; const sm4=sm.clone(); sm3.rotation.z=-Math.PI/2;
    sails.add(sm2,sm3,sm4);
    sails.position.set(wmx-3, wl+9, wmz);
    sails.rotation.z=0; millSails=sails; scene.add(sails);
    mark(wmx-3, wl+11, wmz, 'Mill on the Dunes', 'three sails · grinding for the coastal trade', {az:-2.9,pol:.35,dist:56,tx:wmx-6,tz:wmz-8,ty:9});

    /* lighthouse rotating beam */
    beamGroup=new THREE.Group();
    const beamLen=95;
    for(const sgn of [1,-1]){
      const g=new THREE.ConeGeometry(9, beamLen, 4, 1, true);
      g.translate(0,-beamLen/2,0); g.rotateZ(Math.PI/2*sgn);
      const m=new THREE.MeshBasicMaterial({color:0xffe2b0,transparent:true,opacity:.10,blending:THREE.AdditiveBlending,
        depthWrite:false,side:THREE.DoubleSide,fog:false});
      const mesh=new THREE.Mesh(g,m); mesh.userData.mat=m; beamGroup.add(mesh);
    }
    beamGroup.position.set(LH_X, 10+17, LH_Z); scene.add(beamGroup);
    const halo=new THREE.Sprite(new THREE.SpriteMaterial({map:glowTex,transparent:true,opacity:.5,depthWrite:false,blending:THREE.AdditiveBlending,fog:false}));
    halo.scale.set(30,30,1); halo.position.copy(beamGroup.position); scene.add(halo); beamGroup.userData.halo=halo; beamGroup.userData.haloMat=halo.material;

    /* channel buoy bobbing */
    buoy=smallVoxMesh(S=>{ const V=S.solid;
      box(V,-1,1,0,2,-1,1,PAL.red,.06); box(V,0,0,3,4,0,0,PAL.ironDk,.05); V.set(0,5,0,new THREE.Color(0xff6a4a)); });
    buoy.position.set(-2,0,-14); scene.add(buoy);

    /* clouds (instanced puffs) */
    const CS=new VoxelSet();
    for(let i=0;i<44;i++){
      const r=2+Math.floor(h1(i*3.7)*3);
      const bx=Math.floor(h1(i*1.3)*22)-11, bz=Math.floor(h1(i*5.1)*10)-5, by=Math.floor(h1(i*7.7)*3);
      for(let dx=0;dx<r+2;dx++)for(let dy=0;dy<2;dy++)for(let dz=0;dz<r;dz++){
        if(h1(i+dx*3+dy*7+dz*5)>.28)
          CS.solid.set(bx+dx, by+dy, bz+dz, tint(i%7===0?0xd8e6f2:0xf2f6fa,.05,h3(bx+dx,by+dy,bz+dz)));
      }
    }
    const cg=bake(CS,'solid');
    cloudMesh=new THREE.InstancedMesh(cg, matCloud, 11);
    cloudMesh.frustumCulled=false;
    const m4=new THREE.Matrix4(), q=new THREE.Quaternion(), sv=new THREE.Vector3(), pv=new THREE.Vector3();
    cloudMesh.userData.seeds=[];
    for(let i=0;i<11;i++){
      const s=1.5+h1(i*2.3)*1.7;
      pv.set(-180+h1(i*1.1)*360, 52+h1(i*4.4)*26, -140+h1(i*9.9)*260);
      q.setFromAxisAngle(new THREE.Vector3(0,1,0), h1(i)*6.28);
      sv.set(s, s*.55, s*(.8+h1(i*3)*.6));
      m4.compose(pv,q,sv); cloudMesh.setMatrixAt(i,m4);
      cloudMesh.userData.seeds.push({p:pv.clone(),s:sv.clone(),q:q.clone()});
    }
    scene.add(cloudMesh);

    /* chimney smoke */
    const N=64;
    smokeMesh=new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1),
      new THREE.MeshLambertMaterial({color:0xd9d3c8,transparent:true,opacity:.85}), N);
    smokeMesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
    smokeMesh.userData.p=[]; for(let i=0;i<N;i++) smokeMesh.userData.p.push({t:Math.random(),life:2.4+Math.random()*2});
    scene.add(smokeMesh);

    /* walkers on the quay */
    for(let i=0;i<6;i++){
      const w=new THREE.Group();
      const shirt=[PAL.red,PAL.blue,PAL.green,PAL.cream,PAL.brass,PAL.tar][i];
      const fig=smallVoxMesh(S=>{ const V=S.solid;
        box(V,0,0,0,0,-0,0,PAL.tar,.05); box(V,0,1,0,0,2,0,shirt,.06); V.set(0,3,0,tint(0xe0b48c,.05,.5)); });
      w.add(fig);
      const x0=QUAY_X0+4+h1(i*3)*40, z0=QUAY_EDGE+2+h1(i*7)*7;
      w.position.set(Math.round(x0),QUAY_Y+1,Math.round(z0));
      w.userData={x0,z0,ph:h1(i*11)*6.28, r:3+h1(i*5)*9, sp:.15+h1(i*2)*.25};
      scene.add(w); walkers.push(w);
    }

    /* gulls */
    function gullGeo(){ const S=new VoxelSet();
      box(S.solid,-1,1,0,0,-1,1,PAL.white,.04); S.solid.set(2,0,0,tint(PAL.tar,.05,.5)); S.solid.set(-2,0,0,tint(PAL.white,.05,.4)); return bake(S,'solid'); }
    function wingGeo(sgn){ const S=new VoxelSet();
      for(let i=1;i<=3;i++) S.solid.set(sgn*i,0,0,tint(i===3?0xd8d3c8:PAL.white,.05,h1(i))); return bake(S,'solid'); }
    const bg=gullGeo(), wgR=wingGeo(1), wgL=wingGeo(-1);
    for(let i=0;i<8;i++){
      const g=new THREE.Group();
      const b=new THREE.Mesh(bg,new THREE.MeshLambertMaterial({vertexColors:true}));
      const wr=new THREE.Mesh(wgR,b.material), wl=new THREE.Mesh(wgL,b.material);
      g.add(b,wr,wl); g.userData={wr,wl,ph:h1(i*4)*6.28, r:26+h1(i*2)*40, cx:-10+h1(i*9)*40, cz:-2+h1(i*5)*22, sp:.13+h1(i)*.16, y:14+h1(i*3)*16};
      scene.add(g); gulls.push(g);
    }

    /* distant sails outside the breakwater */
    const DS=new VoxelSet();
    box(DS.solid,-3,3,0,1,-1,1,PAL.woodDk,.06);
    box(DS.solid,0,0,2,6,0,0,PAL.wood,.05);
    box(DS.solid,1,1,2,5,1,1,PAL.sail,.04); box(DS.solid,-1,-1,2,4,-1,-1,PAL.sail2,.04);
    const dg=bake(DS,'solid');
    distantSails=new THREE.InstancedMesh(dg,new THREE.MeshLambertMaterial({vertexColors:true}),4);
    distantSails.frustumCulled=false; distantSails.userData.seeds=[];
    for(let i=0;i<4;i++) distantSails.userData.seeds.push(new THREE.Vector3(-50+i*36+h1(i)*14, 0, -34-h1(i*3)*24));
    scene.add(distantSails);

    /* quay-side lantern lights */
    lampLight(18,QUAY_Y+7,QUAY_EDGE+3,0xffc078,40);
    lampLight(41,QUAY_Y+7,QUAY_EDGE+3,0xffc078,40);
    lampLight(2,QUAY_Y+7,QUAY_EDGE+3,0xffb878,34);
    mark(1,QUAY_Y+11,QUAY_EDGE+4,'The Customs House','tall mast-house · copper dome · tide clock', {az:-2.5,pol:.28,dist:44,tx:2,tz:24,ty:12});
    mark(-13,QUAY_Y+8,QUAY_EDGE+6,'Fish Market','the shed · ice from the wharf at dawn', {az:-2.25,pol:.19,dist:34,tx:-13,tz:20,ty:6});
    mark(-11,QUAY_Y+9,-6,'The Long Wharf','timber head · two lamps · deep-water berth', {az:-1.6,pol:.22,dist:40,tx:-6,tz:2,ty:5});
    mark(BW_A[0],9,BW_A[1],'North Beacon','fixed red · the sharp edge of the channel', {az:-2.9,pol:.26,dist:52,tx:36,tz:2,ty:4});
  }

  /* ═══════════════════════ mooring hawsers ═══════════════════════ */
  let hawsers=[];
  function buildHawsers(){
    const specs=[
      {a:[-4.8,5.5,7.2], b:[-2,QUAY_Y+3,-4], n:34},   // bow → Long Wharf bollard
      {a:[-4.6,5.5,8.6], b:[1,QUAY_Y+3,-3], n:36},
      {a:[21.4,5.5,6.4], b:[21,QUAY_Y+3,13.5], n:24}, // stern → quay
      {a:[-16,7.5,3.2],  b:[-30,QUAY_Y+10,2], n:26, slack:.25}, // stern to headland (visually thin)
    ];
    for(const s of specs){
      const geo=new THREE.BoxGeometry(.3,.3,.3);
      const im=new THREE.InstancedMesh(geo,new THREE.MeshLambertMaterial({color:0xb89a6c}), s.n);
      im.frustumCulled=false; scene.add(im); hawsers.push({im,s});
    }
  }
  const _v=new THREE.Vector3();
  function updateHawsers(t){
    for(const {im,s} of hawsers){
      const shipLocal = s.b[0]>14 || s.b[0]<-18 ? null : null;
      // endpoint A sits on the ship (world), B fixed on the wharf
      const ax=s.a[0], ay=s.a[1]+ (shipGroup?shipGroup.position.y:0), az=s.a[2];
      for(let i=0;i<s.n;i++){
        const u=i/(s.n-1);
        const x=lerp(ax,s.b[0],u), z=lerp(az,s.b[2],u);
        const sag = (s.slack??.55) * Math.sin(Math.PI*u) * (1+.06*Math.sin(t*1.4+i*.3));
        const y=lerp(ay,s.b[1],u) - sag + Math.sin(t*2+u*7)*.05;
        const m=new THREE.Matrix4().makeTranslation(x,y,z);
        m.multiply(new THREE.Matrix4().makeRotationY(u*2+Math.sin(t+u*4)*.1));
        im.setMatrixAt(i,m);
      }
      im.instanceMatrix.needsUpdate=true;
    }
  }

  /* ═══════════════════════ time-of-day ═══════════════════════ */
  const KEYS=[
    {h:0,   top:'#040c17', hor:'#0b1c2b', sun:'#5f7cb4', si:0,    moon:1,   hiS:'#1c3550', hiG:'#0f1a1e', fogD:.0092, lamp:1,  star:1,   sea:'#0b2233', wt:'#3c5f88', glow:.25},
    {h:4.4, top:'#0a1a2e', hor:'#263d55', sun:'#7787b8', si:0,    moon:.8,  hiS:'#22405e', hiG:'#121d22', fogD:.0092, lamp:1,  star:.85, sea:'#10283c', wt:'#48688c', glow:.3},
    {h:6.1, top:'#22507a', hor:'#e98a5f', sun:'#ff9a52', si:.72,  moon:0,   hiS:'#4a7396', hiG:'#2a2a26', fogD:.0108, lamp:.55,star:.05, sea:'#255a70', wt:'#ffc79a', glow:1},
    {h:8.2, top:'#3d7fb0', hor:'#c3dbe4', sun:'#ffd9a8', si:1.25, moon:0,   hiS:'#7fb2d4', hiG:'#33402f', fogD:.0072, lamp:0,  star:0,   sea:'#2a6d84', wt:'#ffffff', glow:.4},
    {h:13,  top:'#4d97cc', hor:'#d3e8ef', sun:'#fff4e0', si:1.55, moon:0,   hiS:'#93cbea', hiG:'#3a4535', fogD:.0058, lamp:0,  star:0,   sea:'#2c7890', wt:'#ffffff', glow:.3},
    {h:16,  top:'#4a90c4', hor:'#dfe2d4', sun:'#ffe6b8', si:1.32, moon:0,   hiS:'#8dc0dd', hiG:'#3e4636', fogD:.0070, lamp:0,  star:0,   sea:'#2c6f88', wt:'#fff2dd', glow:.5},
    {h:17.3,top:'#3a7ba5', hor:'#f5bb79', sun:'#ffb166', si:1.14, moon:0,   hiS:'#7fadd0', hiG:'#45452f', fogD:.0086, lamp:.14,star:0,   sea:'#2a6076', wt:'#ffd2a0', glow:1.1},
    {h:18.1,top:'#2a5a86', hor:'#f08a52', sun:'#ff8340', si:.72,  moon:0,   hiS:'#5d87ab', hiG:'#3f3524', fogD:.0112, lamp:.7, star:.12, sea:'#245068', wt:'#ffbb90', glow:1.3},
    {h:19.2,top:'#173a5e', hor:'#c25a4a', sun:'#e05a3c', si:.24,  moon:.3,  hiS:'#37587e', hiG:'#2a2318', fogD:.0128, lamp:1,  star:.55, sea:'#1a3a55', wt:'#c98a86', glow:1},
    {h:20.7,top:'#0b2038', hor:'#3d4060', sun:'#8a6f90', si:.03,  moon:.9,  hiS:'#22374f', hiG:'#141c20', fogD:.0104, lamp:1,  star:.95, sea:'#112a40', wt:'#5c6f96', glow:.4},
    {h:24,  top:'#040c17', hor:'#0b1c2b', sun:'#5f7cb4', si:0,    moon:1,   hiS:'#1c3550', hiG:'#0f1a1e', fogD:.0092, lamp:1,  star:1,   sea:'#0b2233', wt:'#3c5f88', glow:.25},
  ].map(k=>({...k, top:c(k.top), hor:c(k.hor), sun:c(k.sun), hiS:c(k.hiS), hiG:c(k.hiG), sea:c(k.sea), wt:c(k.wt)}));

  const env={skyTint:new THREE.Color(), lamp:0};
  function setTime(h){
    h=((h%24)+24)%24;
    let a=KEYS[0],b=KEYS[1],t=0;
    for(let i=0;i<KEYS.length-1;i++){ if(h>=KEYS[i].h && h<=KEYS[i+1].h){ a=KEYS[i]; b=KEYS[i+1];
      t=(h-a.h)/Math.max(1e-6,b.h-a.h); break; } }
    const T=smooth(t);
    const mix=(k)=>a[k].clone().lerp(b[k],T), mixn=(k)=>lerp(a[k],b[k],T);
    skyU.uTop.value.copy(mix('top')); skyU.uHor.value.copy(mix('hor'));
    skyU.uSunCol.value.copy(mix('sun')); skyU.uGlow.value=mixn('glow');
    scene.fog.color.copy(mix('hor')); scene.fog.density=mixn('fogD');
    hemi.color.copy(mix('hiS')); hemi.groundColor.copy(mix('hiG')); hemi.intensity=lerp(.55,.34,smoothstep(0,.5,mixn('star')));
    const si=mixn('si'), moon=mixn('moon');
    // sun path
    const az=(h-6)/12*Math.PI, el=Math.sin(az)*.9;
    const dir=new THREE.Vector3(Math.cos(az)*Math.cos(el), Math.sin(el), -Math.sin(az)*Math.cos(el)).normalize();
    const useSun = dir.y>0.015;
    const ld = useSun? dir : dir.clone().negate();
    sun.position.copy(ld).multiplyScalar(150).add(new THREE.Vector3(4,0,10));
    sun.color.copy(useSun? mix('sun') : c(0x9fc0f0));
    sun.intensity = useSun? si : .22*moon;
    sun.userData.moon = !useSun;
    skyU.uSunDir.value.copy(dir);
    sunSprite.position.copy(dir).multiplyScalar(430);
    sunSprite.material.opacity = c01((dir.y+.05)*14)*.95;
    sunSprite.scale.setScalar(lerp(70,140,c01(1-dir.y*2.4)));
    moonSprite.position.copy(dir).multiplyScalar(-430);
    moonSprite.material.opacity = moon*c01(-dir.y*8);
    matGlow.emissiveIntensity = mixn('lamp')*1.15;
    if(shipSet) shipSet.material.emissiveIntensity = mixn('lamp')*1.15;
    lampLights.forEach((l,i)=>{ l.intensity = mixn('lamp')*(3.4+ (i%2)); });
    starMat.opacity = mixn('star')*.95;
    uWaterTint.value.copy(mix('wt'));
    seaPlane.material.color.copy(mix('sea'));
    matCloud.emissive.copy(mix('hor')).multiplyScalar(.35);
    if(beamGroup){ const bm=.02+mixn('lamp')*.13;
      beamGroup.children.forEach(m=>{ m.userData.mat.opacity=bm; });
      beamGroup.userData.haloMat.opacity=.15+mixn('lamp')*.6; }
    env.lamp=mixn('lamp');
    // clock text
    const H=Math.floor(h), M=Math.floor((h-H)*60);
    const name = h<5?'night watch': h<7?'first light': h<11?'forenoon watch': h<14?'midday':
                 h<17?'afternoon': h<19?'the gloaming': h<21?'dusk':'night watch';
    document.getElementById('clock').innerHTML=`${String(H).padStart(2,'0')}:${String(M).padStart(2,'0')} <small>${name}</small>`;
    document.getElementById('rTide').textContent = `${(2.0+Math.sin(h/24*Math.PI*2)*1.6).toFixed(1)}m`;
  }

  /* ═══════════════════════ camera rig ═══════════════════════ */
  const VIEWS={
    arrival:{az:-2.52,pol:.34,dist:96, tx:6, ty:7, tz:6},
    alongside:{az:-2.68,pol:.19,dist:44,tx:9, ty:8, tz:4},
    quay:{az:-2.35,pol:.12,dist:30,tx:2, ty:6, tz:18},
    mast:{az:-2.6,pol:.44,dist:34,tx:8, ty:17,tz:2},
    chart:{az:-2.4,pol:1.32,dist:104,tx:4,ty:2,tz:8},
  };
  const cam={az:-2.52,pol:.34,dist:96,target:new THREE.Vector3(6,7,6),
             taz:-2.52,tpol:.34,tdist:96,tgt:new THREE.Vector3(6,7,6)};
  let orbit=true, lastInput=0, flying=null;

  function updateCamera(dt){
    if(orbit && performance.now()-lastInput>6000 && !flying) cam.taz += dt*.016;
    if(flying){
      flying.t += dt/flying.dur; const t=smoothstep(0,1,Math.min(1,flying.t));
      cam.taz=lerp(flying.a.az,flying.b.az,t); cam.tpol=lerp(flying.a.pol,flying.b.pol,t);
      cam.tdist=lerp(flying.a.dist,flying.b.dist,t);
      cam.tgt.set(lerp(flying.a.tx,flying.b.tx,t),lerp(flying.a.ty,flying.b.ty,t),lerp(flying.a.tz,flying.b.tz,t));
      if(flying.t>=1) flying=null;
    }
    const k=1-Math.pow(.0001,dt);
    cam.az=lerp(cam.az,cam.taz,k); cam.pol=lerp(cam.pol,cam.tpol,k);
    cam.dist=lerp(cam.dist,cam.tdist,k); cam.target.lerp(cam.tgt,k);
    const cp=Math.cos(cam.pol), sp=Math.sin(cam.pol);
    camera.position.set(
      cam.target.x + Math.cos(cam.az)*cp*cam.dist,
      cam.target.y + sp*cam.dist,
      cam.target.z + Math.sin(cam.az)*cp*cam.dist);
    const L=landHeight(Math.round(camera.position.x),Math.round(camera.position.z));
    if(L) camera.position.y=Math.max(camera.position.y, L.h+3);
    camera.position.y=Math.max(camera.position.y,1.6);
    camera.lookAt(cam.target);
  }
  function flyToView(v){
    const from={az:cam.taz,pol:cam.tpol,dist:cam.tdist,tx:cam.tgt.x,ty:cam.tgt.y,tz:cam.tgt.z};
    const to={...v};
    let d=to.az-from.az; while(d>Math.PI)d-=2*Math.PI; while(d<-Math.PI)d+=2*Math.PI;
    to.az=from.az+d;
    flying={a:from,b:to,t:0,dur:1.6};
    cam.az=lerpShort(cam.az,to.az);
  }
  function lerpShort(cur,target){ let d=target-cur; while(d>Math.PI)d-=2*Math.PI; while(d<-Math.PI)d+=2*Math.PI; return cur+d; }

  /* input */
  let pDown=false,pBtn=0,pX=0,pY=0; const touches=new Map(); let pinch=0;
  canvas.addEventListener('pointerdown',e=>{
    canvas.setPointerCapture(e.pointerId); touches.set(e.pointerId,{x:e.clientX,y:e.clientY});
    pDown=true; pBtn=e.button; pX=e.clientX; pY=e.clientY; lastInput=performance.now();
    canvas.classList.add('drag'); flying=null;
    if(touches.size===2){ const [a,b]=[...touches.values()]; pinch=Math.hypot(a.x-b.x,a.y-b.y); }
  });
  canvas.addEventListener('pointermove',e=>{
    if(!touches.has(e.pointerId)) return;
    const prev=touches.get(e.pointerId); touches.set(e.pointerId,{x:e.clientX,y:e.clientY});
    lastInput=performance.now();
    if(touches.size>=2){
      const [a,b]=[...touches.values()]; const d=Math.hypot(a.x-b.x,a.y-b.y);
      if(pinch>0) cam.tdist=clamp(cam.tdist*(pinch/d),14,150);
      pinch=d; return;
    }
    const dx=e.clientX-prev.x, dy=e.clientY-prev.y;
    if(pBtn===2||e.shiftKey){
      const s=cam.dist*.0016;
      const rx=Math.cos(cam.az+Math.PI/2), rz=Math.sin(cam.az+Math.PI/2);
      cam.tgt.x += (dx*rx - dy*Math.cos(cam.az)*Math.sin(cam.pol))*s;
      cam.tgt.z += (dx*rz - dy*Math.sin(cam.az)*Math.sin(cam.pol))*s;
      cam.tgt.y = clamp(cam.tgt.y + dy*s*1.1, 0, 30);
    } else {
      cam.taz -= dx*.0052; cam.tpol = clamp(cam.tpol + dy*.0042, .045, 1.42);
    }
  });
  const up=e=>{ touches.delete(e.pointerId); if(!touches.size){pDown=false;canvas.classList.remove('drag');} pinch=0; };
  canvas.addEventListener('pointerup',up); canvas.addEventListener('pointercancel',up);
  canvas.addEventListener('contextmenu',e=>e.preventDefault());
  canvas.addEventListener('wheel',e=>{ e.preventDefault(); lastInput=performance.now(); flying=null;
    cam.tdist=clamp(cam.tdist*Math.exp(clamp(e.deltaY,-120,120)*.0011),14,150); },{passive:false});

  /* click → ripple, dblclick → focus */
  const ray=new THREE.Raycaster(); const ndc=new THREE.Vector2();
  const pickPlane=new THREE.Mesh(new THREE.PlaneGeometry(400,400), new THREE.MeshBasicMaterial({visible:false}));
  pickPlane.rotation.x=-Math.PI/2; pickPlane.position.y=-.05; scene.add(pickPlane);
  let targetList=[];
  function setNdc(e){ ndc.set((e.clientX/innerWidth)*2-1, -(e.clientY/innerHeight)*2+1); }
  canvas.addEventListener('click',e=>{
    setNdc(e); ray.setFromCamera(ndc,camera);
    const hit=ray.intersectObject(pickPlane,false)[0];
    if(hit && !landHeight(Math.round(hit.point.x),Math.round(hit.point.z)) && Math.hypot(hit.point.x,hit.point.z-6)<58){
      const t=performance.now()/1000;
      uRip.value[ripI%6].set(hit.point.x,hit.point.z,t,1); ripI++;
    }
  });
  canvas.addEventListener('dblclick',e=>{
    setNdc(e); ray.setFromCamera(ndc,camera);
    const hit=ray.intersectObjects(targetList,false)[0];
    if(hit){ cam.tgt.copy(hit.point); cam.tdist=clamp(cam.tdist*.7,16,120); flying=null; lastInput=performance.now(); }
  });

  /* ═══════════════════════ UI wiring ═══════════════════════ */
  const $=s=>document.querySelector(s);
  const timeEl=$('#time'), windEl=$('#wind');
  function sliderFill(el){ el.style.setProperty('--p', ((el.value-el.min)/(el.max-el.min)*100)+'%'); }
  [timeEl,windEl].forEach(sliderFill);
  timeEl.addEventListener('input',()=>{ setTime(+timeEl.value); sliderFill(timeEl); lastInput=performance.now(); });
  windEl.addEventListener('input',()=>{ uWind.value=+windEl.value; sliderFill(windEl);
    const kn=Math.round(2+uWind.value*26); $('#windTxt').innerHTML=`${kn} <small>kn · WSW</small>`; });
  document.querySelectorAll('#views .chip').forEach(b=>b.addEventListener('click',()=>{
    document.querySelectorAll('#views .chip').forEach(x=>x.classList.remove('on')); b.classList.add('on');
    flyToView(VIEWS[b.dataset.v]); lastInput=performance.now();
  }));
  $('#tOrbit').addEventListener('click',e=>{ orbit=!orbit; e.target.classList.toggle('on',orbit);
    $('#modeTxt').textContent = orbit?'drifting':'held'; });
  const marksEl=document.getElementById('marks');
  let showMarks=true;
  $('#tMarks').addEventListener('click',e=>{ showMarks=!showMarks; e.target.classList.toggle('on',showMarks); });
  $('#tHide').addEventListener('click',()=>document.getElementById('ui').classList.toggle('hidden'));
  addEventListener('keydown',e=>{ if(e.key==='h'||e.key==='H') document.getElementById('ui').classList.toggle('hidden');
    if(e.key>='1'&&e.key<='5'){ const k=['arrival','alongside','quay','mast','chart'][+e.key-1];
      document.querySelector(`#views [data-v="${k}"]`)?.click(); } });

  /* POI list + markers */
  const pail=$('#pail');
  function buildPois(){
    POIS.forEach((p,i)=>{
      const row=document.createElement('div'); row.className='prow';
      row.innerHTML=`<b>${String(i+1).padStart(2,'0')}</b><div><span>${p.name}</span><i>${p.sub}</i></div>`;
      row.addEventListener('click',()=>{ flyToView({az:p.cam.az,pol:p.cam.pol,dist:p.cam.dist,tx:p.cam.tx,ty:p.cam.ty,tz:p.cam.tz});
        lastInput=performance.now(); document.querySelectorAll('#views .chip').forEach(x=>x.classList.remove('on')); });
      let hot=false;
      row.addEventListener('mouseenter',()=>{hot=true; p.el?.classList.add('hot');});
      row.addEventListener('mouseleave',()=>{hot=false; p.el?.classList.remove('hot');});
      pail.appendChild(row);
      const b=document.createElement('button'); b.className='mk';
      b.innerHTML=`<span class="pulse"></span><span class="dot"></span>
        <span class="lbl"><s>${String(i+1).padStart(2,'0')}</s><em>${p.name}</em></span>`;
      b.addEventListener('click',()=>row.click());
      marksEl.appendChild(b); p.el=b;
    });
  }
  const tmp=new THREE.Vector3();
  let occTick=0;
  function updateMarks(){
    occTick++;
    for(const p of POIS){
      tmp.copy(p.p);
      const dist=camera.position.distanceTo(tmp);
      const vis = showMarks && dist<220;
      p.el.style.opacity = vis? 1 : 0;
      if(!vis) continue;
      if(occTick%3===0){
        let occ=0;
        const steps=18;
        for(let i=2;i<steps;i++){ const t=i/steps;
          const x=lerp(camera.position.x,tmp.x,t), y=lerp(camera.position.y,tmp.y,t), z=lerp(camera.position.z,tmp.z,t);
          if(world.solid.has(Math.round(x),Math.round(y),Math.round(z))){ occ=1; break; } }
        p.occluded=occ;
      }
      tmp.project(camera);
      if(tmp.z>1){ p.el.style.opacity=0; continue; }
      const sx=(tmp.x*.5+.5)*innerWidth, sy=(-tmp.y*.5+.5)*innerHeight;
      p.el.style.transform=`translate(${sx}px,${sy}px)`;
      p.el.style.zIndex = String(1000-Math.round(dist));
      if(!p.el.classList.contains('hot')) p.el.style.opacity = (p.occluded? .18 : (vis?1:0)) * c01(1.5-dist/180);
      p.el.style.pointerEvents = p.occluded? 'none':'auto';
    }
  }

  /* ═══════════════════════ wave sampling (mirrors the shader) ═══════════════════════ */
  function wv(px,pz,t){ return Math.sin(px*.30+t*1.25)*.42 + Math.sin(pz*.26-t*1.02)*.38
    + Math.sin((px+pz)*.17+t*.72)*.30 + Math.sin((px-pz*.7)*.53-t*2.05)*.14; }
  const waveAmp=()=> (0.12+0.44*uWind.value);

  /* ═══════════════════════ animation ═══════════════════════ */
  const clock=new THREE.Clock();
  let fpsAcc=0, fpsN=0, fpsShown=0;
  const roseN=document.getElementById('roseN');
  const smokeM=new THREE.Matrix4(), smokeQ=new THREE.Quaternion(), smokeS=new THREE.Vector3();

  function tick(){
    const dt=Math.min(clock.getDelta(),.05), t=clock.elapsedTime;
    uTime.value=t;
    updateCamera(dt);

    /* the barque rides the same swell you can see */
    if(shipGroup){
      const A=waveAmp(), S=shipGroup.position;
      const h=(x,z)=> wv(x,z,t*(.85+.35*uWind.value),0)*A*mix1(1,.26,shelterAt(x,z));
      const mid=h(S.x,S.z), bow=h(S.x+15,S.z), stn=h(S.x-15,S.z), pt=h(S.x,S.z+4), sb=h(S.x,S.z-4);
      S.y = mid*.72 - .06;
      shipGroup.rotation.z = -(bow-stn)*.010 + Math.sin(t*.55)*.004;
      shipGroup.rotation.x = (pt-sb)*.009 + Math.sin(t*.43+1.3)*.006;
      shipGroup.rotation.y = -.075 + Math.sin(t*.22)*.012;
      updateHawsers(t);
    }
    /* beam, clouds, smoke, gulls, buoy, distant sails */
    if(beamGroup){ beamGroup.rotation.y = t*.42;
      beamGroup.userData.halo.position.copy(beamGroup.position); }
    if(craneJib){ craneJib.rotation.y = -1.05 + Math.sin(t*.19)*.85;
      craneJib.rotation.z = Math.sin(t*.5)*.02; }
    if(millSails) millSails.rotation.z = -t*(.35+uWind.value*.9);
    if(cloudMesh){
      const m=new THREE.Matrix4();
      cloudMesh.userData.seeds.forEach((s,i)=>{
        s.p.x += dt*(1.0+uWind.value*4.5);
        if(s.p.x>210) s.p.x-=420;
        m.compose(s.p,s.q,s.s); cloudMesh.setMatrixAt(i,m);
      });
      cloudMesh.instanceMatrix.needsUpdate=true;
    }
    if(smokeMesh){
      const P=smokeMesh.userData.p, base=new THREE.Vector3(19,QUAY_Y+9,22);
      for(let i=0;i<P.length;i++){
        const p=P[i]; p.t+=dt/p.life; if(p.t>1) p.t-=1;
        const a=p.t;
        const sx=base.x + Math.sin(i*2.1+a*3)*a*3.2 + a*(1.5+uWind.value*7);
        const sy=base.y + a*11;
        const sz=base.z + Math.cos(i*1.7+a*2)*a*2.4;
        const sc=(0.6+a*2.6);
        smokeM.compose(new THREE.Vector3(sx,sy,sz), smokeQ.setFromEuler(new THREE.Euler(a*2,a*3,0)), smokeS.set(sc,sc,sc));
        smokeMesh.setMatrixAt(i,smokeM);
      }
      smokeMesh.instanceMatrix.needsUpdate=true;
      smokeMesh.material.opacity=.5;
      smokeMesh.material.color.setRGB(lerp(.82,.62,env.lamp?env.lamp*.5:0),.8,.76);
    }
    if(buoy){ const x=buoy.position.x,z=buoy.position.z;
      buoy.position.y = wv(x,z,t*(.85+.35*uWind.value),0)*waveAmp()*.9 - .3;
      buoy.rotation.z=Math.sin(t*1.1)*.14; buoy.rotation.x=Math.cos(t*.9)*.1; }
    gulls.forEach((g,i)=>{
      const u=g.userData, a=t*u.sp+u.ph;
      g.position.set(u.cx+Math.cos(a)*u.r, u.y+Math.sin(a*2.1)*2.2, u.cz+Math.sin(a)*u.r*.75);
      g.rotation.y=-a+Math.PI/2;
      const f=Math.sin(t*7+u.ph)*.9;
      u.wr.rotation.z=f; u.wl.rotation.z=-f;
    });
    walkers.forEach((w,i)=>{ const u=w.userData, a=t*u.sp+u.ph;
      w.position.x=u.x0+Math.cos(a)*u.r; w.position.z=u.z0+Math.sin(a)*u.r*.35;
      w.rotation.y=-a+Math.PI/2; w.position.y=QUAY_Y+1+Math.abs(Math.sin(a*6))*.12; });
    if(distantSails){
      const m=new THREE.Matrix4(), q=new THREE.Quaternion(), sv=new THREE.Vector3(1.6,1.6,1.6);
      distantSails.userData.seeds.forEach((p,i)=>{
        p.x += dt*(.25+uWind.value*1.1); if(p.x>150) p.x=-150;
        const y=wv(p.x,p.z,t,0)*waveAmp()*.8-.4;
        q.setFromEuler(new THREE.Euler(Math.sin(t*.8+i)*.07,t*.02,Math.cos(t*.7+i)*.05));
        m.compose(new THREE.Vector3(p.x,y,p.z),q,sv); distantSails.setMatrixAt(i,m);
      });
      distantSails.instanceMatrix.needsUpdate=true;
    }
    updateMarks();

    /* instruments */
    roseN.setAttribute('transform',`rotate(${(-cam.az*180/Math.PI+90).toFixed(1)} 50 50)`);
    let bearing = ((-cam.az*180/Math.PI+90)%360+360)%360;
    document.getElementById('rBearing').textContent = Math.round(bearing)+'°';
    fpsAcc+=dt; fpsN++;
    if(fpsAcc>.5){ fpsShown=Math.round(fpsN/fpsAcc); fpsAcc=0; fpsN=0;
      document.getElementById('rFps').textContent=fpsShown+' fps'; }

    renderer.render(scene,camera);
  }
  const mix1=(a,b,t)=>a+(b-a)*t;

  /* ═══════════════════════ resize ═══════════════════════ */
  addEventListener('resize',()=>{
    camera.aspect=innerWidth/innerHeight; camera.updateProjectionMatrix();
    renderer.setSize(innerWidth,innerHeight);
    renderer.setPixelRatio(Math.min(devicePixelRatio,1.8));
  });

  /* ═══════════════════════ BUILD SEQUENCE ═══════════════════════ */
  async function step(txt,pct,fn){ PHASE.textContent=txt; BAR.style.width=pct+'%'; await nextFrame(); await nextFrame(); fn(); }
  await step('sounding the basin…',12,buildWater);
  await step('quarrying the headland…',30,buildLand);
  await step('curbling the quay & raising the town…',56,()=>{ const info=buildTown(); window.__town=info; });
  await step('caulking the barque…',76,buildShip);
  await step('bending the flags & fitting the light…',92,()=>{ buildAnimated(window.__town); buildHawsers(); buildPois();
    targetList=[pickPlane, ...scene.children.filter(o=>o.isMesh||o.isInstancedMesh)];
    let blocks=world.count + (shipSet?0:0) + waterGeoCount;
    blocks = world.count + waterGeoCount + 3400;
    document.getElementById('rBlocks').textContent = blocks.toLocaleString();
  });
  await step('loosing the gulls…',100,()=>{ setTime(+timeEl.value); });

  /* first frame + establishing move */
  cam.az=-2.30; cam.pol=.62; cam.dist=150; cam.tgt.set(6,7,6);
  cam.target.set(6,9,6); cam.taz=VIEWS.arrival.az; cam.tpol=VIEWS.arrival.pol; cam.tdist=VIEWS.arrival.dist;
  flying={a:{az:cam.az,pol:cam.pol,dist:cam.dist,tx:6,ty:9,tz:6},b:{az:cam.taz,pol:cam.tpol,dist:cam.tdist,tx:6,ty:7,tz:6},t:0,dur:3.4};
  updateCamera(0.016); renderer.render(scene,camera);
  await nextFrame();
  LOAD.classList.add('gone');
  renderer.setAnimationLoop(tick);
}

main().catch(err=>{
  console.error(err);
  LOAD.classList.remove('gone');
  document.getElementById('phase').textContent='the chart could not be unrolled';
  document.getElementById('err').textContent = String(err && err.message || err) +
    ' — this plate needs a network connection to fetch its renderer (three.js r161 via unpkg).';
  const b=document.getElementById('barfill'); if(b) b.style.background='#d3563f';
});
</script>
</body>
</html>
```

**What's in the plate**

- **The barque *Aurelia***: 32 blocks keel to truck, three masts, squared yards with sails bunted up and two courses still set, gaff spanker, bowsprit with a furled jib, ratlines, cannon ports, brass, stern lantern, ship's boat on davits, ensign + jack + masthead pennants that flutter in the wind slider. She rides the *same* swell function the water shader uses, so she pitches and heels off the real waves and the hawsers sag with her.
- **The harbour**: engineered quay wall with wet band and coping stones, Long Wharf with pilings, the fish market shed with striped awnings, customs house with a clock tower and copper domes, brick warehouse, townhouses, chimney smoke, lamp posts, a turning gantry crane lowering a crate, a windmill, a stone breakwater with a red beacon, and Mireux Point Light sweeping a twin beam over the basin.
- **Living bits**: gulls on lissajous circles with flapping wings, drifting voxel cloud banks, walkers pacing the quay, a bobbing channel buoy, distant sails crossing the sea road, shore foam from a distance field, star field and moon coming up after dusk.
- **Controls**: drag = orbit, wheel = zoom, right-drag/shift-drag = pan, double-click = focus, click the water = ripple. Hour slider drives sun path, sky, fog, water tint, and every lamp waking up; wind drives swell, flutter, cloud and smoke drift. Chart marks in 3D hide themselves when the cliffs get in the way; `H` hides the panels, `1–5` jump to views.