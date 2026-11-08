```html
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>ブロッククラフト — 3D箱庭</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root{
    --bg:#0a0f0c;
    --panel:rgba(16,26,19,0.90);
    --panel2:rgba(10,16,12,0.78);
    --line:rgba(120,160,120,0.22);
    --ink:#eef4e6;
    --muted:#94a891;
    --gold:#e6c35c;
    --grass:#5cb044;
    --grass-d:#3f7d31;
    --dirt:#8a5a34;
    --dirt-d:#6d4423;
    --stone:#8f8f97;
    --danger:#e0574a;
    --accent:#79c85f;
    --sel:rgba(230,195,92,0.9);
  }
  *{box-sizing:border-box;margin:0;padding:0}
  html,body{height:100%;overflow:hidden;background:var(--bg);color:var(--ink);
    font-family:'Space Grotesk',system-ui,sans-serif;
    -webkit-font-smoothing:antialiased;touch-action:none}
  #c{position:fixed;inset:0;display:block;width:100%;height:100%;z-index:0;cursor:crosshair}

  /* ---- ambient / overlay fx ---- */
  .scrim{position:fixed;inset:0;z-index:2;pointer-events:none;opacity:0;transition:opacity .25s ease;
    background:radial-gradient(120% 120% at 50% 50%, rgba(0,0,0,0) 55%, rgba(120,20,10,0.55) 100%)}
  .scrim.on{opacity:1}
  .flash{position:fixed;inset:0;z-index:3;pointer-events:none;opacity:0;
    background:radial-gradient(circle at 50% 60%, rgba(10,16,12,0.15), rgba(0,0,0,0.9))}
  .flash.on{animation:flash .55s ease-out}
  @keyframes flash{0%{opacity:1}100%{opacity:0}}
  .vig{position:fixed;inset:0;z-index:2;pointer-events:none;
    box-shadow:inset 0 0 160px 40px rgba(0,0,0,0.55)}

  /* ---- HUD ---- */
  .hud{position:fixed;z-index:5;pointer-events:none;transition:opacity .3s ease}
  .hud.hide{opacity:0}

  #top{top:14px;left:14px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
  .chip{display:flex;align-items:center;gap:8px;padding:8px 12px;background:var(--panel2);
    border:1px solid var(--line);border-radius:10px;backdrop-filter:blur(4px)}
  .chip .k{font-family:'Press Start 2P';font-size:8px;color:var(--muted);letter-spacing:.5px}
  .chip .v{font-size:13px;font-weight:600}
  .chip .dot{width:9px;height:9px;border-radius:50%;box-shadow:0 0 8px currentColor}
  .mode-badge{font-family:'Press Start 2P';font-size:9px;padding:9px 12px;border-radius:10px;
    background:var(--panel2);border:1px solid var(--line);letter-spacing:.5px}
  #modeBadge.build{color:var(--accent);box-shadow:0 0 0 1px rgba(121,200,95,.35) inset}
  #modeBadge.mine{color:var(--danger);box-shadow:0 0 0 1px rgba(224,87,74,.4) inset}
  #modeBadge.fly{color:var(--gold);box-shadow:0 0 0 1px rgba(230,195,92,.4) inset}

  #stats{top:14px;right:14px;display:flex;gap:10px}
  .stat{min-width:96px;padding:10px 12px;background:var(--panel);border:1px solid var(--line);
    border-radius:12px;text-align:right;backdrop-filter:blur(6px)}
  .stat .lab{font-family:'Press Start 2P';font-size:7px;color:var(--muted);margin-bottom:7px;letter-spacing:.5px}
  .stat .big{font-size:24px;font-weight:700;line-height:1}
  .stat .sub{font-size:11px;color:var(--muted);margin-top:5px}
  .stat .row{display:flex;justify-content:space-between;align-items:baseline}
  .clock{display:flex;align-items:center;gap:9px}
  .sun{width:16px;height:16px;border-radius:50%;background:var(--gold);box-shadow:0 0 14px var(--gold);transition:background .4s}
  .sun.moon{background:#cfd6e6;box-shadow:0 0 14px #cfd6e6}

  #cross{position:fixed;z-index:5;left:50%;top:50%;transform:translate(-50%,-50%);pointer-events:none;
    width:26px;height:26px;transition:transform .08s ease}
  #cross::before,#cross::after{content:"";position:absolute;background:rgba(255,255,255,.9);
    box-shadow:0 0 3px rgba(0,0,0,.7)}
  #cross::before{left:50%;top:0;width:2px;height:100%;transform:translateX(-50%)}
  #cross::after{top:50%;left:0;height:2px;width:100%;transform:translateY(-50%)}
  #cross.pop{transform:translate(-50%,-50%) scale(1.55)}

  #selinfo{bottom:150px;left:50%;transform:translateX(-50%);text-align:center;pointer-events:none}
  #selinfo .nm{font-family:'Press Start 2P';font-size:11px;color:var(--gold);text-shadow:0 2px 0 rgba(0,0,0,.5)}
  #selinfo .cnt{font-size:11px;color:var(--muted);margin-top:6px}

  /* ---- hotbar ---- */
  #hotbar{position:fixed;z-index:6;bottom:14px;left:50%;transform:translateX(-50%);
    display:flex;gap:6px;padding:8px;background:var(--panel);border:1px solid var(--line);
    border-radius:14px;backdrop-filter:blur(8px);box-shadow:0 12px 30px rgba(0,0,0,.5)}
  .slot{position:relative;width:54px;height:54px;border-radius:9px;border:2px solid rgba(255,255,255,.08);
    background:rgba(255,255,255,.03);display:grid;place-items:center;cursor:pointer;
    transition:transform .12s cubic-bezier(.2,1.4,.4,1),border-color .15s,box-shadow .15s;pointer-events:auto}
  .slot canvas{width:38px;height:38px;image-rendering:pixelated;filter:drop-shadow(0 3px 0 rgba(0,0,0,.35))}
  .slot .num{position:absolute;top:3px;left:5px;font-family:'Press Start 2P';font-size:7px;color:var(--muted)}
  .slot .qty{position:absolute;bottom:2px;right:4px;font-size:12px;font-weight:700;
    text-shadow:0 1px 2px rgba(0,0,0,.8)}
  .slot:hover{transform:translateY(-3px);border-color:rgba(255,255,255,.25)}
  .slot.active{border-color:var(--gold);box-shadow:0 0 0 2px rgba(230,195,92,.35),0 -6px 18px rgba(230,195,92,.2);
    transform:translateY(-6px)}
  .slot.mine-mode{opacity:.55}

  /* ---- corner hints ---- */
  #hints{bottom:14px;left:14px;display:flex;gap:8px;align-items:center}
  .btn{pointer-events:auto;font-family:'Press Start 2P';font-size:8px;padding:10px 11px;
    background:var(--panel2);border:1px solid var(--line);border-radius:10px;color:var(--ink);
    cursor:pointer;transition:.15s;letter-spacing:.3px}
  .btn:hover{background:rgba(40,60,40,.9);transform:translateY(-2px);border-color:var(--accent)}
  #fps-hint{bottom:14px;right:14px;font-size:11px;color:var(--muted);
    background:var(--panel2);border:1px solid var(--line);padding:8px 11px;border-radius:10px}

  /* ---- overlays ---- */
  .overlay{position:fixed;inset:0;z-index:20;display:grid;place-items:center;padding:24px;
    background:radial-gradient(120% 120% at 30% 10%, rgba(30,50,35,.85), rgba(6,10,7,.96));
    backdrop-filter:blur(6px);transition:opacity .4s ease,visibility .4s}
  .overlay.gone{opacity:0;visibility:hidden}
  .panel{max-width:780px;width:100%;background:var(--panel);border:1px solid var(--line);
    border-radius:18px;padding:34px 36px;box-shadow:0 30px 80px rgba(0,0,0,.6);
    display:grid;grid-template-columns:1.15fr .85fr;gap:34px;align-items:center}

  .eyebrow{font-family:'Press Start 2P';font-size:8px;color:var(--accent);letter-spacing:1px;margin-bottom:16px}
  .title{font-family:'Press Start 2P';font-size:34px;line-height:1.35;color:var(--ink);margin-bottom:18px;
    text-shadow:0 3px 0 var(--grass-d),0 6px 22px rgba(0,0,0,.5)}
  .title .g{color:var(--grass)}
  .lead{color:var(--muted);font-size:15px;line-height:1.6;margin-bottom:22px;max-width:42ch}
  .keys{display:grid;grid-template-columns:auto 1fr;gap:9px 14px;margin-bottom:26px}
  .key{font-family:'Press Start 2P';font-size:8px;padding:7px 8px;border-radius:7px;color:var(--ink);
    background:linear-gradient(180deg,#2a3a2c,#1a271c);border:1px solid rgba(255,255,255,.12);
    box-shadow:0 2px 0 rgba(0,0,0,.4);white-space:nowrap;text-align:center}
  .kd{font-size:13px;color:var(--muted);align-self:center}
  .start{font-family:'Press Start 2P';font-size:12px;padding:16px 26px;border:none;border-radius:12px;
    color:#0a0f0c;background:linear-gradient(180deg,#7fd463,#4fae3d);cursor:pointer;
    box-shadow:0 6px 0 var(--grass-d),0 12px 26px rgba(92,176,68,.35);transition:transform .1s,box-shadow .1s}
  .start:hover{transform:translateY(-2px);box-shadow:0 8px 0 var(--grass-d),0 16px 30px rgba(92,176,68,.45)}
  .start:active{transform:translateY(4px);box-shadow:0 2px 0 var(--grass-d)}
  .credit{margin-top:16px;font-size:11px;color:var(--muted)}

  .art{position:relative;height:300px;display:grid;place-items:center}
  .scene{position:relative;width:230px;height:230px;transform-style:preserve-3d;animation:spin 20s linear infinite}
  @keyframes spin{to{transform:rotateX(-24deg) rotateY(360deg)}}
  .blk{position:absolute;width:64px;height:64px;left:50%;top:50%;margin:-32px 0 0 -32px;image-rendering:pixelated;
    box-shadow:0 0 0 1px rgba(0,0,0,.25)}
  .b1{transform:translate3d(-70px,10px,0)}
  .b2{transform:translate3d(0,10px,70px)}
  .b3{transform:translate3d(70px,10px,0)}
  .b4{transform:translate3d(0,-54px,0)}
  .b5{transform:translate3d(0,10px,-70px);opacity:.9}
  .art .glow{position:absolute;width:180px;height:180px;border-radius:50%;
    background:radial-gradient(circle,rgba(121,200,95,.35),transparent 70%);filter:blur(6px)}
  .art .cap{position:absolute;bottom:-6px;font-family:'Press Start 2P';font-size:8px;color:var(--muted)}

  #pause .panel{grid-template-columns:1fr;text-align:center;max-width:420px}
  #pause h2{font-family:'Press Start 2P';font-size:20px;margin-bottom:14px}
  #pause p{color:var(--muted);font-size:14px;margin-bottom:22px}

  /* touch */
  #touch{position:fixed;inset:0;z-index:8;pointer-events:none;display:none}
  #touch.on{display:block}
  #stick{position:absolute;left:22px;bottom:26px;width:120px;height:120px;border-radius:50%;
    background:rgba(255,255,255,.05);border:1px solid var(--line);pointer-events:auto}
  #stick .knob{position:absolute;left:50%;top:50%;width:52px;height:52px;border-radius:50%;
    background:rgba(255,255,255,.22);transform:translate(-50%,-50%)}
  .tbtn{position:absolute;width:60px;height:60px;border-radius:14px;background:var(--panel2);
    border:1px solid var(--line);color:var(--ink);font-family:'Press Start 2P';font-size:8px;
    pointer-events:auto;display:grid;place-items:center}
  #tjump{right:26px;bottom:150px}
  #tfly{right:100px;bottom:150px}
  #tmode{right:26px;bottom:80px}
  #tbreak{left:160px;bottom:150px;width:74px;height:74px;font-size:9px;color:var(--danger)}
  #tbuild{left:160px;bottom:66px;width:74px;height:74px;font-size:9px;color:var(--accent)}

  @media(max-width:720px){
    .panel{grid-template-columns:1fr;gap:22px;padding:26px 22px}
    .art{height:200px}
    .title{font-size:24px}
    #stats{gap:6px}.stat{min-width:78px;padding:8px 9px}
    #hotbar{gap:4px;padding:6px}.slot{width:44px;height:44px}.slot canvas{width:30px;height:30px}
    #fps-hint{display:none}
  }
</style>
</head>
<body>
<canvas id="c"></canvas>

<div class="vig"></div>
<div class="scrim" id="scrim"></div>
<div class="flash" id="flash"></div>

<!-- HUD -->
<div id="top" class="hud">
  <div class="mode-badge build" id="modeBadge">BUILD</div>
  <div class="chip"><span class="dot" style="color:var(--grass)"></span>
    <div><div class="k">WORLD</div><div class="v" id="pos">0, 0, 0</div></div></div>
  <div class="chip"><div><div class="k">FPS</div><div class="v" id="fps">60</div></div></div>
</div>

<div id="stats" class="hud">
  <div class="stat clock">
    <div class="row"><div class="lab">TIME</div><div class="sun" id="sun"></div></div>
    <div class="big" id="clock">12:00</div>
    <div class="sub" id="phase">Daytime</div>
  </div>
  <div class="stat">
    <div class="lab">PLACED</div>
    <div class="big" id="placed">0</div>
    <div class="sub" id="removed">removed 0</div>
  </div>
</div>

<div id="cross"></div>
<div id="selinfo" class="hud"><div class="nm" id="selName">GRASS BLOCK</div><div class="cnt" id="selCount">∞</div></div>

<div id="hotbar"></div>

<div id="hints" class="hud">
  <button class="btn" id="btnReset">RESET</button>
  <button class="btn" id="btnHelp">HELP</button>
  <button class="btn" id="btnMute">♪ SOUND</button>
</div>
<div id="fps-hint" class="hud">CLICK to lock mouse · ESC to pause</div>

<!-- touch controls -->
<div id="touch">
  <div id="stick"><div class="knob"></div></div>
  <div class="tbtn" id="tjump">JUMP</div>
  <div class="tbtn" id="tfly">FLY</div>
  <div class="tbtn" id="tmode">MINE</div>
  <div class="tbtn" id="tbreak">BREAK</div>
  <div class="tbtn" id="tbuild">BUILD</div>
</div>

<!-- start -->
<div class="overlay" id="start">
  <div class="panel">
    <div>
      <div class="eyebrow">3D VOXEL SANDBOX · WEBGL</div>
      <h1 class="title">BLOCK<br><span class="g">CRAFT</span></h1>
      <p class="lead">見渡す限りのブロックの世界。掘って、積んで、思いのままに。昼と夜が移ろう箱庭で、自由な創造を。</p>
      <div class="keys">
        <div class="key">W A S D</div><div class="kd">移動</div>
        <div class="key">SPACE</div><div class="kd">ジャンプ / 上昇</div>
        <div class="key">SHIFT</div><div class="kd">スニーク / 下降</div>
        <div class="key">L / R</div><div class="kd">置く / 壊す</div>
        <div class="key">F</div><div class="kd">飛行 ON/OFF</div>
        <div class="key">1–9</div><div class="kd">ブロック選択</div>
        <div class="key">ESC</div><div class="kd">一時停止</div>
      </div>
      <button class="start" id="btnStart">▶ START GAME</button>
      <div class="credit">マウスをクリックして視点を操作 · タッチ端末は自動で仮想スティック</div>
    </div>
    <div class="art">
      <div class="glow"></div>
      <div class="scene" id="scene"></div>
      <div class="cap">DRAG · BUILD · EXPLORE</div>
    </div>
  </div>
</div>

<!-- pause -->
<div class="overlay gone" id="pause">
  <div class="panel">
    <h2>PAUSED</h2>
    <p>クリックしてゲームに戻る</p>
    <button class="start" id="btnResume">▶ RESUME</button>
  </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
/* ============================= CONSTANTS ============================= */
const WORLD=46, HEIGHT=26;
const AIR=0, GRASS=1, DIRT=2, STONE=3, SAND=4, LOG=5, PLANK=6, LEAVES=7, GLASS=8, BRICK=9, COBBLE=10, GLOW=11;

const NAMES={1:'GRASS BLOCK',2:'DIRT',3:'STONE',4:'SAND',5:'OAK LOG',6:'OAK PLANKS',7:'OAK LEAVES',8:'GLASS',9:'BRICKS',10:'COBBLESTONE',11:'GLOWSTONE'};
const OPAQUE={1:1,2:1,3:1,4:1,5:1,6:1,7:1,8:0,9:1,10:1,11:1};

/* ============================= BLOCK TEXTURES ============================= */
const S=16;
const rnd=(x,y,s)=>{let h=(x*374761393+y*668265263+s*1442695041)>>>0;h=(h^(h>>13))>>>0;h=(h*1274126177)>>>0;h=(h^(h>>16))>>>0;return h/4294967296;};
function mk(fn){const c=document.createElement('canvas');c.width=c.height=S;const x=c.getContext('2d');for(let yy=0;yy<S;yy++)for(let xx=0;xx<S;xx++){x.fillStyle=fn(xx,yy);x.fillRect(xx,yy,1,1);}return c;}
const T={
  grassTop:mk((x,y)=>`hsl(108,44%,${34+rnd(x,y,3)*15|0}%)`),
  grassSide:mk((x,y)=>y<4?`hsl(108,44%,${34+rnd(x,y,3)*15|0}%)`:`hsl(25,45%,${30+rnd(x,y,5)*16|0}%)`),
  dirt:mk((x,y)=>`hsl(25,45%,${30+rnd(x,y,5)*16|0}%)`),
  stone:mk((x,y)=>`hsl(215,6%,${52+rnd(x,y,7)*16|0}%)`),
  sand:mk((x,y)=>`hsl(45,52%,${72+rnd(x,y,9)*12|0}%)`),
  logTop:mk((x,y)=>{const dx=x-7.5,dy=y-7.5,r=Math.hypot(dx,dy);return `hsl(30,42%,${(Math.sin(r*1.5)*.5+.5)*22+34|0}%)`;}),
  logSide:mk((x,y)=>`hsl(28,40%,${30+(Math.sin(x*1.3)*.5+.5)*14+rnd(x,y,11)*6|0}%)`),
  plank:mk((x,y)=>`hsl(33,44%,${(y%4===0?26:40)+rnd(x,y,13)*10|0}%)`),
  leaves:mk((x,y)=>`hsl(${100+rnd(x,y,15)*20|0},48%,${24+rnd(x,y,17)*20|0}%)`),
  glass:mk((x,y)=>(x===0||y===0||x===15||y===15)?'rgba(235,246,255,0.9)':'rgba(200,232,246,0.10)'),
  brick:mk((x,y)=>{const r=(y/4|0),off=(r%2)*4,bx=((x+off)%8),by=y%4;return (bx<1||by<1)?'hsl(16,20%,58%)':`hsl(12,52%,${34+rnd(x,y,19)*10|0}%)`;}),
  cobble:mk((x,y)=>{const cx=x/4|0,cy=y/4|0;return `hsl(215,6%,${40+rnd(cx,cy,21)*26|0}%)`;}),
  glow:mk((x,y)=>`hsl(${44+rnd(x,y,23)*8|0},88%,${56+rnd(x,y,25)*20|0}%)`),
  grassSideTop:mk((x,y)=>`hsl(108,44%,${36+rnd(x,y,3)*14|0}%)`)
};

/* ============================= CANVAS 2D ICONS ============================= */
function shade(c,a,b){const x=document.createElement('canvas');x.width=x.height=64;const g=x.getContext('2d');g.imageSmoothingEnabled=false;g.drawImage(c,0,0,64,64);g.globalCompositeOperation='multiply';g.fillStyle=`rgba(${a},${a},${a},0.5)`;g.fillRect(0,0,64,64);return x;}
function icon(id){const c=document.createElement('canvas');c.width=c.height=64;const g=c.getContext('2d');g.imageSmoothingEnabled=false;const top=id===8?T.glass:T.grassSideTop, side=id===8?T.glass:T.grassSide;
  // top face (diamond)
  g.save();g.translate(32,10);g.transform(1,0.5,-1,0.5,0,0);g.drawImage(top,-18,-18,36,36);g.restore();
  // left face
  g.save();g.translate(14,19);g.transform(1,0.5,0,1,0,0);g.drawImage(shade(side,90,90),0,0,36,36);g.restore();
  // right face
  g.save();g.translate(32,28);g.transform(1,-0.5,0,1,0,0);g.drawImage(shade(side,130,130),0,0,36,36);g.restore();
  return c;}

/* ============================= THREE SETUP ============================= */
let renderer,scene,camera,worldGroup,borderGroup,cloudGroup,selBox,selBoxMat,particles=[];
let sky,sunLight,hemi,dayLight,starPts,moonMesh;
const clock=new THREE.Clock();
let dayT=0.30; // fraction of day
const DAY_LEN=90; // seconds per full cycle
const sunDir=new THREE.Vector3();
const dayCol=new THREE.Color('#8fc7f0'), nightCol=new THREE.Color('#0b1224'),
      duskCol=new THREE.Color('#e79a5b'), nightFog=new THREE.Color('#0b1224'), dayFog=new THREE.Color('#a8cfe8');

function initThree(){
  const c=document.getElementById('c');
  renderer=new THREE.WebGLRenderer({canvas:c,antialias:true});
  renderer.setPixelRatio(Math.min(devicePixelRatio,2));
  renderer.outputEncoding=THREE.sRGBEncoding;
  renderer.shadowMap.enabled=true;
  renderer.shadowMap.type=THREE.PCFSoftShadowMap;
  renderer.setClearColor(new THREE.Color('#8fc7f0'));

  scene=new THREE.Scene();
  scene.fog=new THREE.Fog(new THREE.Color('#a8cfe8'), 12, 58);
  camera=new THREE.PerspectiveCamera(72, innerWidth/innerHeight, 0.1, 300);

  hemi=new THREE.HemisphereLight(0xbfe0ff,0x5a4a30,0.9); scene.add(hemi);
  dayLight=new THREE.HemisphereLight(0xbfe0ff,0x5a4a30,0); scene.add(dayLight);
  sunLight=new THREE.DirectionalLight(0xffffff,1.1);
  sunLight.castShadow=true;
  sunLight.shadow.mapSize.set(2048,2048);
  const sc=sunLight.shadow.camera; sc.left=-45;sc.right=45;sc.top=45;sc.bottom=-45;sc.near=1;sc.far=160;
  sunLight.shadow.bias=-0.0004;
  scene.add(sunLight); scene.add(sunLight.target);

  // sky sphere
  const skyMat=new THREE.ShaderMaterial({side:THREE.BackSide,depthWrite:false,
    uniforms:{top:{value:new THREE.Color('#8fc7f0')},bot:{value:new THREE.Color('#cfe8f5')}},
    vertexShader:`varying vec3 vp;void main(){vp=position;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,
    fragmentShader:`uniform vec3 top;uniform vec3 bot;varying vec3 vp;void main(){float h=normalize(vp).y*0.5+0.5;gl_FragColor=vec4(mix(bot,top,pow(h,0.85)),1.);}`});
  sky=new THREE.Mesh(new THREE.SphereGeometry(200,24,16),skyMat); scene.add(sky);

  // sun / moon / stars
  sunMesh=new THREE.Mesh(new THREE.SphereGeometry(9,16,16),new THREE.MeshBasicMaterial({color:0xfff2c0}));
  scene.add(sunMesh);
  moonMesh=new THREE.Mesh(new THREE.SphereGeometry(6,16,16),new THREE.MeshBasicMaterial({color:0xdfe6f5}));
  scene.add(moonMesh);
  const sg=new THREE.BufferGeometry(); const sp=[];
  for(let i=0;i<400;i++){const v=new THREE.Vector3().randomDirection();v.multiplyScalar(150);sp.push(v.x,v.y,v.z);}
  sg.setAttribute('position',new THREE.Float32BufferAttribute(sp,3));
  starPts=new THREE.Points(sg,new THREE.PointsMaterial({color:0xffffff,size:1.1,sizeAttenuation:false,transparent:true,opacity:0}));
  scene.add(starPts);

  // clouds
  cloudGroup=new THREE.Group(); scene.add(cloudGroup);
  const clMat=new THREE.MeshLambertMaterial({color:0xffffff,transparent:true,opacity:0.82});
  for(let i=0;i<10;i++){const g=new THREE.Group();const n=3+(Math.random()*3|0);
    for(let j=0;j<n;j++){const s=6+Math.random()*8;const m=new THREE.Mesh(new THREE.BoxGeometry(s,s*0.5,s),clMat);m.position.set(j*7-n*3.5,Math.random()*2,Math.random()*6);g.add(m);}
    g.position.set(Math.random()*WORLD,HEIGHT+8+Math.random()*4,Math.random()*WORLD);cloudGroup.add(g);}

  // selection box
  selBoxMat=new THREE.LineBasicMaterial({color:0xe6c35c,transparent:true,opacity:0.95});
  selBox=new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(1.02,1.02,1.02)),selBoxMat);
  selBox.visible=false; scene.add(selBox);

  worldGroup=new THREE.Group(); scene.add(worldGroup);
  borderGroup=new THREE.Group(); scene.add(borderGroup);

  // border walls (visual only)
  const bm=new THREE.LineBasicMaterial({color:0x3a5a3a,transparent:true,opacity:0.5});
  for(let i=0;i<=WORLD;i++){
    worldGroup; // keep
  }
  const pts=[[-.5,-.5],[-.5,WORLD+.5],[WORLD+.5,WORLD+.5],[WORLD+.5,-.5],[-.5,-.5]];
  for(let h=0;h<=1;h+=1){const arr=[];pts.forEach(p=>arr.push(p[0],h,p[1]));
    const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(arr,3));
    borderGroup.add(new THREE.Line(g,bm));}
}
let sunMesh;

/* ============================= WORLD DATA ============================= */
const vox=new Uint8Array(WORLD*HEIGHT*WORLD);
const P=(x,y,z)=>x+z*WORLD+y*WORLD*WORLD;
const getB=(x,y,z)=>(x<0||y<0||z<0||x>=WORLD||y>=HEIGHT||z>=WORLD)?AIR:vox[P(x,y,z)];
const setB=(x,y,z,v)=>{if(x<0||y<0||z<0||x>=WORLD||y>=HEIGHT||z>=WORLD)return;vox[P(x,y,z)]=v;};

function generate(){
  vox.fill(0);
  const hmap=new Int16Array(WORLD*WORLD);
  for(let x=0;x<WORLD;x++)for(let z=0;z<WORLD;z++){
    const n=Math.sin(x*0.19)*1.7+Math.cos(z*0.16)*1.7+Math.sin((x+z)*0.09)*2.4+Math.sin(x*0.05+z*0.07)*3.2+2.4;
    let h=Math.round(Math.max(2,n)); hmap[z*WORLD+x]=h;
    for(let y=0;y<=h;y++){
      let t; if(y===h)t=(h<=3?SAND:GRASS); else if(y>=h-2)t=(h<=3?SAND:DIRT); else t=STONE;
      setB(x,y,z,t);
    }
  }
  // trees
  for(let x=3;x<WORLD-3;x++)for(let z=3;z<WORLD-3;z++){
    const h=hmap[z*WORLD+x]; if(getB(x,h,z)!==GRASS) continue;
    if(Math.random()>0.02) continue;
    const th=4+(Math.random()*2|0);
    for(let i=1;i<=th;i++) setB(x,h+i,z,LOG);
    const cy=h+th;
    for(let dx=-2;dx<=2;dx++)for(let dz=-2;dz<=2;dz++)for(let dy=-1;dy<=2;dy++){
      if(dx===0&&dz===0&&dy<1)continue;
      const d=Math.abs(dx)+Math.abs(dz)+Math.abs(dy-1);
      if(d>4||Math.random()<0.12)continue;
      if(getB(x+dx,cy+dy,z+dz)===AIR) setB(x+dx,cy+dy,z+dz,LEAVES);
    }
  }
}

/* ============================= CHUNK MESHING ============================= */
const CH=8, NC=(WORLD+CH-1)/CH;
const chunks=[];
for(let i=0;i<NC;i++)for(let j=0;j<NC;j++)chunks.push({cx:i,cz:j,block:null,water:null});

const FACES=[
  {n:[1,0,0], u:[0,0,1], v:[0,1,0], tl:[1,1,0],tr:[1,1,1],bl:[1,0,0],br:[1,0,1]},
  {n:[-1,0,0],u:[0,0,-1],v:[0,1,0], tl:[0,1,1],tr:[0,1,0],bl:[0,0,1],br:[0,0,0]},
  {n:[0,1,0], u:[1,0,0], v:[0,0,1], tl:[0,1,1],tr:[1,1,1],bl:[0,1,0],br:[1,1,0]},
  {n:[0,-1,0],u:[1,0,0], v:[0,0,-1],tl:[0,0,0],tr:[1,0,0],bl:[0,0,1],br:[1,0,1]},
  {n:[0,0,1], u:[-1,0,0],v:[0,1,0], tl:[0,1,1],tr:[0,1,0],bl:[1,1,1],br:[1,1,0]},
  {n:[0,0,-1],u:[1,0,0], v:[0,1,0], tl:[1,1,0],tr:[1,1,1],bl:[0,1,0],br:[0,1,1]}
];
const blockMat={};
function texOf(id,face){ // face: 0 top,1 side,2 bottom-ish (use side)
  if(id===GRASS)return face===0?T.grassTop:(face===2?T.dirt:T.grassSide);
  if(id===LOG)return face===0||face===2?T.logTop:T.logSide;
  return {2:T.dirt,3:T.stone,4:T.sand,6:T.plank,7:T.leaves,8:T.glass,9:T.brick,10:T.cobble,11:T.glow}[id];
}
const faceTex=[0,1,0,2,1,1]; // top,bottom,side... map face index -> top(0)/side(1)/bottom(2)
function buildBlockTex(){
  const c=document.createElement('canvas');c.width=c.height=16*3;const g=c.getContext('2d');
  // col0 top, col1 side, col2 bottom
  const order=[GRASS,DIRT,STONE,SAND,LOG,PLANK,LEAVES,GLASS,BRICK,COBBLE,GLOW];
  order.forEach((id,i)=>{
    g.drawImage(texOf(id,0),i*16,0);
    g.drawImage(texOf(id,1),i*16,16);
    g.drawImage(texOf(id,2),i*16,32);
  });
  const t=new THREE.CanvasTexture(c);t.magFilter=THREE.NearestFilter;t.minFilter=THREE.NearestFilter;t.generateMipmaps=false;
  const mat=new THREE.MeshLambertMaterial({map:t});mat.side=THREE.FrontSide;
  blockMat.opaque=mat;
  const gmat=new THREE.MeshLambertMaterial({map:t,transparent:true,depthWrite:false});
  blockMat.glass=gmat;
}
function isOpaque(x,y,z){return OPAQUE[getB(x,y,z)]===1;}

function buildChunk(ch){
  const x0=ch.cx*CH,z0=ch.cz*CH;
  const pos=[],uv=[],ind=[];const wpos=[],wuv=[],wind=[];let vi=0,wi=0;
  for(let x=x0;x<x0+CH;x++)for(let z=z0;z<z0+CH;z++)for(let y=0;y<HEIGHT;y++){
    const id=getB(x,y,z);if(id===AIR)continue;
    const glass=id===GLASS;const arr=glass?{pos:wpos,uv:wuv,ind:wind}:null;
    const isGlass=id===GLASS;
    for(let f=0;f<6;f++){
      const F=FACES[f];const nx=x+F.n[0],ny=y+F.n[1],nz=z+F.n[2];
      const nb=getB(nx,ny,nz);
      if(isOpaque(nx,ny,nz))continue;
      if(isGlass&&nb===GLASS)continue; // no interior glass faces
      const P0=pos, U=uv, I=ind;
      const base=P0.length/3;
      for(const c of[F.tl,F.tr,F.bl,F.br]){P0.push(x+c[0],y+c[1],z+c[2]);}
      const col=(id-1), row=faceTex[f];
      U.push((col+0.03)/3,(row+0.03)/3,(col+0.97)/3,(row+0.03)/3,(col+0.03)/3,(row+0.97)/3,(col+0.97)/3,(row+0.97)/3);
      I.push(base,base+2,base+1,base,base+3,base+2);
    }
  }
  if(ch.block){ch.block.geometry.dispose();worldGroup.remove(ch.block);}
  if(pos.length){const g=new THREE.BufferGeometry();
    g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));
    g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));
    g.setIndex(ind);g.computeVertexNormals();
    const m=new THREE.Mesh(g,blockMat.opaque);m.castShadow=true;m.receiveShadow=true;worldGroup.add(m);ch.block=m;
  }else ch.block=null;
  if(ch.water){ch.water.geometry.dispose();worldGroup.remove(ch.water);}
  if(wpos.length){const g=new THREE.BufferGeometry();
    g.setAttribute('position',new THREE.Float32BufferAttribute(wpos,3));
    g.setAttribute('uv',new THREE.Float32BufferAttribute(wuv,2));
    g.setIndex(wind);g.computeVertexNormals();
    const m=new THREE.Mesh(g,blockMat.glass);m.renderOrder=2;worldGroup.add(m);ch.water=m;
  }else ch.water=null;
}
function rebuild(){chunks.forEach(buildChunk);}
function rebuildAround(x,y,z){
  const cs=new Set();
  for(let dx=-1;dx<=1;dx++)for(let dz=-1;dz<=1;dz++){
    const cx=Math.floor((x+dx)/CH),cz=Math.floor((z+dz)/CH);
    if(cx<0||cz<0||cx>=NC||cz>=NC)continue;cs.add(cx*NC+cz);
  }
  cs.forEach(k=>buildChunk(chunks[k]));
}

/* ============================= PLAYER ============================= */
const player={x:WORLD/2,y:HEIGHT+2,z:WORLD/2,vx:0,vy:0,vz:0,yaw:0,pitch:0,fly:false,ground:false};
const EYE=1.62, PH=1.8, HALF=0.3;
let mode='build'; // build | mine
let sel=0;
const hotbarItems=[GRASS,DIRT,STONE,COBBLE,SAND,LOG,PLANK,BRICK,GLOW];
const counts=new Array(hotbarItems.length).fill(Infinity);
const inv={}; for(const id of hotbarItems)inv[id]=Infinity;

function collides(px,py,pz){
  const x0=Math.floor(px-HALF),x1=Math.floor(px+HALF);
  const y0=Math.floor(py),y1=Math.floor(py+PH);
  const z0=Math.floor(pz-HALF),z1=Math.floor(pz+HALF);
  for(let x=x0;x<=x1;x++)for(let y=y0;y<=y1;y++)for(let z=z0;z<=z1;z++){
    const b=getB(x,y,z); if(b!==AIR&&b!==GLASS)return true;
  }
  return false;
}
function moveAxis(axis,amt){
  if(axis==='x')player.x+=amt;else if(axis==='y')player.y+=amt;else player.z+=amt;
  if(collides(player.x,player.y,player.z)){
    if(axis==='x')player.x-=amt;else if(axis==='y')player.y-=amt;else player.z-=amt;
    return true;
  }
  return false;
}

/* ============================= INPUT ============================= */
const keys={};
let locked=false;
const canvas=document.getElementById('c');
document.addEventListener('keydown',e=>{
  const k=e.code;keys[k]=true;
  if(k>='Digit1'&&k<='Digit9'){sel=+k.slice(5)-1;updateHot();}
  if(k==='KeyF'){player.fly=!player.fly;player.vy=0;updateMode();}
  if(k==='KeyE')toggleMode();
  if(k==='Escape'){}
  if(['Space','KeyW','KeyA','KeyS','KeyD','ShiftLeft','ShiftRight'].includes(k)&&locked)e.preventDefault();
});
document.addEventListener('keyup',e=>{keys[e.code]=false;});

canvas.addEventListener('click',()=>{ if(!locked) requestLock(); else doAction(); });
document.addEventListener('contextmenu',e=>e.preventDefault());
canvas.addEventListener('mousedown',e=>{ if(!locked)return; if(e.button===0)doAction(); else if(e.button===2)doAction(true); });

function requestLock(){ canvas.requestPointerLock&&canvas.requestPointerLock(); }
document.addEventListener('pointerlockchange',()=>{
  locked=document.pointerLockElement===canvas;
  document.getElementById('start').classList.toggle('gone',locked);
  document.getElementById('pause').classList.toggle('gone',locked);
  document.querySelectorAll('.hud').forEach(h=>h.classList.toggle('hide',!locked));
  if(locked) resumeAudio();
});
document.addEventListener('mousemove',e=>{
  if(!locked)return;
  player.yaw-=e.movementX*0.0022;
  player.pitch-=e.movementY*0.0022;
  player.pitch=Math.max(-1.55,Math.min(1.55,player.pitch));
});
document.addEventListener('wheel',e=>{ if(!locked)return; sel=(sel+(e.deltaY>0?1:-1)+hotbarItems.length)%hotbarItems.length; updateHot(); });

function toggleMode(){ mode=mode==='build'?'mine':'build'; updateMode(); }
function updateMode(){
  const b=document.getElementById('modeBadge');
  const label=player.fly?'FLY':(mode==='build'?'BUILD':'MINE');
  b.textContent=label; b.className='mode-badge '+(player.fly?'fly':mode);
  document.querySelectorAll('.slot').forEach(s=>s.classList.toggle('mine-mode',mode==='mine'));
}

/* ============================= RAYCAST ============================= */
const fwd=new THREE.Vector3();
function updateLook(){
  const cp=Math.cos(player.pitch),sp=Math.sin(player.pitch);
  const sy=Math.sin(player.yaw),cy=Math.cos(player.yaw);
  fwd.set(sy*cp,sp,cy*cp);
}
function raycast(maxDist){
  let x=Math.floor(player.x),y=Math.floor(player.y),z=Math.floor(player.z);
  const sx=Math.sign(fwd.x)||0,sy=Math.sign(fwd.y)||0,sz=Math.sign(fwd.z)||0;
  const dx=fwd.x?Math.abs(1/fwd.x):Infinity;
  const dy=fwd.y?Math.abs(1/fwd.y):Infinity;
  const dz=fwd.z?Math.abs(1/fwd.z):Infinity;
  let tx=fwd.x>0?(x+1-player.x)/dx:fwd.x<0?(player.x-x)/dx:Infinity;
  let ty=fwd.y>0?(y+1-player.y)/dy:fwd.y<0?(player.y-y)/dy:Infinity;
  let tz=fwd.z>0?(z+1-player.z)/dz:fwd.z<0?(player.z-z)/dz:Infinity;
  let nx=0,ny=0,nz=0,d=0;
  for(let i=0;i<120;i++){
    if(tx<ty&&tx<tz){x+=sx;d=tx;tx+=dx;nx=-sx;ny=0;nz=0;}
    else if(ty<tz){y+=sy;d=ty;ty+=dy;nx=0;ny=-sy;nz=0;}
    else{z+=sz;d=tz;tz+=dz;nx=0;ny=0;nz=-sz;}
    if(d>maxDist)return null;
    if(x<0||y<0||z<0||x>=WORLD||y>=HEIGHT||z>=WORLD)continue;
    if(getB(x,y,z)!==AIR)return{x,y,z,nx,ny,nz};
  }
  return null;
}

/* ============================= ACTIONS ============================= */
let placed=0,removed=0,shake=0;
function doAction(alt){
  const build=(alt===true)?(mode==='mine'):mode==='build';
  const hit=raycast(6);
  if(!hit)return;
  if(build){
    const id=hotbarItems[sel];
    const px=hit.x+hit.nx,py=hit.y+hit.ny,pz=hit.z+hit.nz;
    if(px<0||py<0||pz<0||px>=WORLD||py>=HEIGHT||pz>=WORLD)return;
    if(getB(px,py,pz)!==AIR)return;
    // avoid placing into player
    if(px+1>player.x-HALF&&px<player.x+HALF&&py+1>player.y&&py<player.y+PH&&pz+1>player.z-HALF&&pz<player.z+HALF)return;
    setB(px,py,pz,id);rebuildAround(px,py,pz);placed++;updateStats();
    spawnBurst(px+.5,py+.5,pz+.5,id);popCross();sfxPlace();
  }else{
    const id=getB(hit.x,hit.y,hit.z);if(id===AIR)return;
    setB(hit.x,hit.y,hit.z,AIR);rebuildAround(hit.x,hit.y,hit.z);removed++;
    inv[id]=(inv[id]===Infinity?Infinity:inv[id]+1);counts[hotbarItems.indexOf(id)]++;updateStats();
    spawnBurst(hit.x+.5,hit.y+.5,hit.z+.5,id);popCross();sfxMine();
  }
}
function popCross(){const c=document.getElementById('cross');c.classList.add('pop');setTimeout(()=>c.classList.remove('pop'),90);}

/* ============================= PARTICLES ============================= */
const pMat=new THREE.MeshBasicMaterial();
function spawnBurst(x,y,z,id){
  const col={1:'#63a83f',2:'#8a5a34',3:'#8f8f97',4:'#d9c57a',5:'#6b4a2c',6:'#b08a5a',7:'#3f7d31',8:'#bfe0ef',9:'#a8503f',10:'#7a7a82',11:'#f0c84a'}[id]||'#888';
  pMat.color.set(col);
  for(let i=0;i<10;i++){
    const m=new THREE.Mesh(new THREE.BoxGeometry(0.12,0.12,0.12),pMat);
    m.position.set(x,y,z);
    m.userData={vx:(Math.random()-.5)*4,vy:Math.random()*4+1,vz:(Math.random()-.5)*4,life:0.6+Math.random()*0.3};
    scene.add(m);particles.push(m);
  }
}
function updParticles(dt){
  for(let i=particles.length-1;i>=0;i--){const p=particles[i];p.userData.life-=dt;
    if(p.userData.life<=0){scene.remove(p);particles.splice(i,1);continue;}
    p.userData.vy-=14*dt;p.position.x+=p.userData.vx*dt;p.position.y+=p.userData.vy*dt;p.position.z+=p.userData.vz*dt;
    p.material.opacity=1;const s=Math.max(0.02,Math.min(1,p.userData.life));p.scale.setScalar(s);}
}

/* ============================= SKY / DAY ============================= */
function updSky(){
  dayT=(dayT+dtRef/DAY_LEN)%1;
  const ang=dayT*Math.PI*2 - Math.PI/2;
  sunDir.set(Math.cos(ang),Math.sin(ang),0.35).normalize();
  const el=sunDir.y;
  const day=THREE.MathUtils.smoothstep(el,-0.12,0.22);
  const dusk=1-Math.min(1,Math.abs(el)/0.28);
  // colors
  sky.material.uniforms.top.value.copy(nightCol).lerp(dayCol,day).lerp(duskCol,dusk*0.4);
  sky.material.uniforms.bot.value.copy(new THREE.Color('#0e1830')).lerp(new THREE.Color('#cfe8f5'),day).lerp(new THREE.Color('#e79a5b'),dusk*0.5);
  scene.fog.color.copy(nightFog).lerp(dayFog,day);
  scene.fog.far=THREE.MathUtils.lerp(46,58,day);
  renderer.setClearColor(sky.material.uniforms.top.value);
  sunLight.intensity=0.15+day*1.05;
  sunLight.color.setHex(0xffffff).lerp(new THREE.Color('#ffb066'),dusk*0.6);
  hemi.intensity=0.35+day*0.6;
  dayLight.intensity=day*0.4;
  // positions
  sunMesh.position.copy(camera.position).addScaledVector(sunDir,120);
  moonMesh.position.copy(camera.position).addScaledVector(sunDir,-120);
  sunMesh.visible=sunDir.y>-0.3; moonMesh.visible=sunDir.y<0.3;
  starPts.material.opacity=Math.max(0,-el)*1.1;
  // HUD
  const sunEl=document.getElementById('sun');sunEl.classList.toggle('moon',el<0);
  const hrs=(dayT*24+6)%24; const hh=Math.floor(hrs),mm=Math.floor((hrs-hh)*60);
  document.getElementById('clock').textContent=`${String(hh).padStart(2,'0')}:${String(mm).padStart(2,'0')}`;
  document.getElementById('phase').textContent=el>0.15?'Daytime':el>-0.05?'Dusk':el>-0.4?'Night':'Midnight';
  document.getElementById('scrim').classList.toggle('on',el<-0.02);
  document.getElementById('scrim').style.opacity=Math.min(1,Math.max(0,-el-0.02)*2.2);
}

/* ============================= TOUCH ============================= */
const isTouch=matchMedia('(pointer:coarse)').matches;
let tJoy={x:0,y:0,active:false},tLook={dx:0,dy:0};
if(isTouch){
  document.getElementById('touch').classList.add('on');
  const stick=document.getElementById('stick'),knob=stick.querySelector('.knob');
  let sc=0;
  stick.addEventListener('pointerdown',e=>{tJoy.active=true;stick.setPointerCapture(e.pointerId);});
  stick.addEventListener('pointermove',e=>{if(!tJoy.active)return;const r=stick.getBoundingClientRect();
    let dx=e.clientX-(r.left+r.width/2),dy=e.clientY-(r.top+r.height/2);const m=Math.hypot(dx,dy),max=r.width/2-6;
    if(m>max){dx=dx/m*max;dy=dy/m*max;}knob.style.transform=`translate(calc(-50% + ${dx}px),calc(-50% + ${dy}px))`;
    tJoy.x=dx/max;tJoy.y=dy/max;});
  const end=()=>{tJoy.active=false;tJoy.x=tJoy.y=0;knob.style.transform='translate(-50%,-50%)';};
  stick.addEventListener('pointerup',end);stick.addEventListener('pointercancel',end);
  canvas.addEventListener('touchstart',e=>{sc=e.touches[0];},{passive:true});
  canvas.addEventListener('touchmove',e=>{const t=e.touches[0];if(sc){player.yaw-=(t.clientX-sc.clientX)*0.006;player.pitch-=(t.clientY-sc.clientY)*0.006;player.pitch=Math.max(-1.55,Math.min(1.55,player.pitch));}sc=t;},{passive:true});
  canvas.addEventListener('touchend',()=>{sc=null;});
  const bind=(id,fn)=>document.getElementById(id).addEventListener('pointerdown',e=>{e.preventDefault();fn();});
  bind('tjump',()=>{player.fly?player.vy=8:(player.ground&&player.vy<0)&&(player.vy=8);});
  bind('tfly',()=>{player.fly=!player.fly;player.vy=0;updateMode();});
  bind('tmode',()=>toggleMode());
  bind('tbreak',()=>doAction(true));
  bind('tbuild',()=>doAction(false));
  // auto lock-free on touch: hide start after tap
  document.getElementById('btnStart').addEventListener('click',()=>{document.getElementById('start').classList.add('gone');document.querySelectorAll('.hud').forEach(h=>h.classList.remove('hide'));});
}

/* ============================= AUDIO ============================= */
let actx=null,muted=false;
function resumeAudio(){ if(!actx){try{actx=new (window.AudioContext||window.webkitAudioContext)();}catch(e){}} if(actx&&actx.state==='suspended')actx.resume(); }
function tone(freq,dur,type,vol,slide){ if(!actx||muted)return; const o=actx.createOscillator(),g=actx.createGain();
  o.type=type||'square';o.frequency.value=freq;if(slide)o.frequency.exponentialRampToValueAtTime(Math.max(1,slide),actx.currentTime+dur);
  g.gain.value=vol||0.05;g.gain.exponentialRampToValueAtTime(0.0001,actx.currentTime+dur);
  o.connect(g).connect(actx.destination);o.start();o.stop(actx.currentTime+dur);}
function noise(dur,vol){ if(!actx||muted)return; const b=actx.createBuffer(1,actx.sampleRate*dur,actx.sampleRate);
  const d=b.getChannelData(0);for(let i=0;i<d.length;i++)d[i]=(Math.random()*2-1)*(1-i/d.length);
  const s=actx.createBufferSource();s.buffer=b;const g=actx.createGain();g.gain.value=vol||0.12;
  const f=actx.createBiquadFilter();f.type='lowpass';f.frequency.value=1200;s.connect(f).connect(g).connect(actx.destination);s.start();}
function sfxPlace(){tone(360,0.08,'square',0.05,420);}
function sfxMine(){noise(0.09,0.12);tone(180,0.06,'square',0.04,120);}
function sfxJump(){tone(300,0.09,'sine',0.05,180);}
document.getElementById('btnMute').addEventListener('click',e=>{muted=!muted;e.target.textContent=muted?'♪ MUTED':'♪ SOUND';e.target.style.color=muted?'var(--danger)':'';});

/* ============================= HOTBAR UI ============================= */
const hotbar=document.getElementById('hotbar');
function buildHot(){
  hotbar.innerHTML='';
  hotbarItems.forEach((id,i)=>{
    const s=document.createElement('div');s.className='slot';if(i===sel)s.classList.add('active');
    s.innerHTML=`<span class="num">${i+1}</span>`;
    const cv=icon(id);s.appendChild(cv);
    const q=document.createElement('span');q.className='qty';q.id='q'+i;q.textContent='∞';s.appendChild(q);
    s.addEventListener('click',()=>{sel=i;updateHot();});
    hotbar.appendChild(s);
  });
  updateHot();
}
function updateHot(){
  document.querySelectorAll('.slot').forEach((s,i)=>{s.classList.toggle('active',i===sel);
    s.classList.toggle('mine-mode',mode==='mine');});
  document.getElementById('selName').textContent=NAMES[hotbarItems[sel]];
  document.getElementById('selCount').textContent=mode==='mine'?'左クリックでブロックを破壊':(inv[hotbarItems[sel]]===Infinity?'∞':inv[hotbarItems[sel]]);
}
function updateStats(){document.getElementById('placed').textContent=placed;document.getElementById('removed').textContent='removed '+removed;}

/* ============================= RESET ============================= */
document.getElementById('btnReset').addEventListener('click',()=>{generate();rebuild();placed=0;removed=0;updateStats();
  player.x=WORLD/2;player.z=WORLD/2;player.y=HEIGHT+2;player.vy=0;});
document.getElementById('btnHelp').addEventListener('click',()=>{document.exitPointerLock&&document.exitPointerLock();document.getElementById('start').classList.remove('gone');document.querySelectorAll('.hud').forEach(h=>h.classList.add('hide'));locked=false;});
document.getElementById('btnStart').addEventListener('click',requestLock);
document.getElementById('btnResume').addEventListener('click',requestLock);

/* ============================= MAIN LOOP ============================= */
let dtRef=0.016;
function update(dt){
  dtRef=dt;
  updateLook();
  // movement input
  let mx=0,mz=0;
  if(!isTouch){
    if(keys['KeyW'])mz+=1;if(keys['KeyS'])mz-=1;if(keys['KeyA'])mx-=1;if(keys['KeyD'])mx+=1;
  }else{mx=tJoy.x;mz=-tJoy.y;}
  const speed=player.fly?(keys['ShiftLeft']?14:9):4.6;
  const sy=Math.sin(player.yaw),cy=Math.cos(player.yaw);
  let wx=mz*sy - mx*cy; let wz=mz*cy + mx*sy;
  const ml=Math.hypot(wx,wz);if(ml>1){wx/=ml;wz/=ml;}
  const tvx=wx*speed, tvz=wz*speed;
  player.vx=THREE.MathUtils.lerp(player.vx,tvx,Math.min(1,dt*12));
  player.vz=THREE.MathUtils.lerp(player.vz,tvz,Math.min(1,dt*12));
  // vertical
  if(player.fly){
    let vy=0; if(keys['Space'])vy+=1; if(keys['ShiftLeft']||keys['ShiftRight'])vy-=1;
    player.vy=THREE.MathUtils.lerp(player.vy,vy*7,Math.min(1,dt*10));
  }else{
    player.vy-=22*dt; if(keys['Space']&&player.ground){player.vy=8.2;sfxJump();}
    player.vy=Math.max(player.vy,-30);
  }
  // collide & move
  player.ground=false;
  if(moveAxis('x',player.vx*dt))player.vx=0;
  if(moveAxis('z',player.vz*dt))player.vz=0;
  if(moveAxis('y',player.vy*dt)){ if(player.vy<0)player.ground=true; player.vy=0; }
  // ground check
  if(!player.ground)player.ground = collides(player.x,player.y-0.04,player.z) && player.vy<=0;
  // void respawn
  if(player.y<-6){player.x=WORLD/2;player.y=HEIGHT+2;player.z=WORLD/2;player.vy=0;flash();}
  // camera
  const shx=shake>0?(Math.random()-.5)*shake:0, shy=shake>0?(Math.random()-.5)*shake:0;shake=Math.max(0,shake-dt*3);
  camera.position.set(player.x+shx,player.y+EYE+shy,player.z);
  camera.rotation.order='YXZ';camera.rotation.y=player.yaw;camera.rotation.x=player.pitch;
  // sun follow
  sunLight.position.copy(camera.position).addScaledVector(sunDir,60);
  sunLight.target.position.set(camera.position.x,camera.position.y,camera.position.z);
  // selection
  const hit=raycast(6);
  if(hit){selBox.visible=true;selBox.position.set(hit.x+.5,hit.y+.5,hit.z+.5);
    const build=(mode==='build');
    selBoxMat.color.set(build?0xe6c35c:0xe0574a);
  }else selBox.visible=false;
  updParticles(dt);
  updSky();
  cloudGroup.position.x=(cloudGroup.position.x+dt*0.4)%WORLD;
  cloudGroup.position.z=0;
  // HUD pos
  document.getElementById('pos').textContent=`${player.x.toFixed(0)}, ${player.y.toFixed(0)}, ${player.z.toFixed(0)}`;
  // fps
  fpsAcc+=dt;fpsN++;if(fpsAcc>0.4){document.getElementById('fps').textContent=Math.round(fpsN/fpsAcc);fpsAcc=0;fpsN=0;}
}
let fpsAcc=0,fpsN=0;
function flash(){const f=document.getElementById('flash');f.classList.remove('on');void f.offsetWidth;f.classList.add('on');}
function loop(){requestAnimationFrame(loop);const dt=Math.min(0.05,clock.getDelta());update(dt);renderer.render(scene,camera);}

function onResize(){camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);}
addEventListener('resize',onResize);

/* ============================= BOOT ============================= */
(function(){
  initThree();
  buildBlockTex();
  generate();
  rebuild();
  buildHot();
  updateMode();
  updateStats();
  onResize();
  loop();
})();
</script>
</body>
</html>
```

3D箱庭ゲーム「BLOCK CRAFT」を作りました。単一のHTMLファイルで動作します。

**主な特徴**
- **フル3Dボクセル世界** — Three.jsでチャンク分割メッシュ化（46×26×46）。隣接ブロックの面だけ描画する最適化済み
- **ブロックを置く／壊す** — レイキャストで照準位置を検出、境界線ハイライト
- **プロシージャル地形** — 起伏、砂浜、ランダム生成の木（幹と葉）
- **昼夜サイクル** — 太陽・月・星空が動き、空の色・雲・フォグ・影が時間帯で変化
- **11種類のブロック** — 草・土・石・砂・原木・板材・葉・ガラス・レンガ・丸石・発光石（ガラスは半透明）
- **操作系** — WASD移動、Spaceジャンプ、Fで飛行、1〜9で選択、ホイール切替、左クリック=置く/右クリック=壊す
- **演出** — ブロック破壊時の粒子スプラッシュ、画面シェイク、Web Audioによる着地・破壊・設置の効果音、HUD（座標・FPS・時刻・配置数）
- **モバイル対応** — 仮想スティック＋ジャンプ/飛行/破壊/設置ボタン

START GAMEでマウスロックして遊べます。ESCで一時停止。