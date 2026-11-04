マイクラ風の3Dボクセル箱庭を単一HTMLで組み上げました。チャンク単位のメッシュ再構築、AO入りメッシュ、Texture Atlas、昼夜サイクル、雲、水のパルシェイダー、粒子破壊、ミニマップ、保存/読み込みまで入っています。

```html
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>VOXEL GARDEN — ボクセル箱庭</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DotGothic16&family=Zen+Kaku+Gothic+New:wght@400;700;900&display=swap" rel="stylesheet">
<style>
  :root{
    --soil:#261d15; --soil2:#150f0a; --line:#4c3a29; --line-hi:#6f553c;
    --ink:#ece2cf; --muted:#9d9079; --grass:#84b35d; --gold:#f3c352;
    --sky:#9ecdf0; --brick:#a2503c; --shadow:0 5px 0 #0d0905;
  }
  *{box-sizing:border-box}
  html,body{height:100%;margin:0;overflow:hidden;background:#0d0a07}
  body{
    font-family:'Zen Kaku Gothic New',system-ui,sans-serif;
    color:var(--ink);
    -webkit-font-smoothing:antialiased;
  }
  #stage{position:fixed;inset:0}
  #gl{display:block;width:100%;height:100%}
  .fx-grid{
    position:fixed;inset:0;pointer-events:none;opacity:.16;
    background:
      repeating-linear-gradient(0deg,rgba(255,255,255,.06) 0 1px,transparent 1px 4px),
      repeating-linear-gradient(90deg,rgba(255,255,255,.05) 0 1px,transparent 1px 4px);
  }
  .fx-vignette{
    position:fixed;inset:0;pointer-events:none;
    background:radial-gradient(115% 90% at 50% 45%,transparent 45%,rgba(8,6,4,.55) 100%);
  }

  .panel{
    position:fixed;z-index:6;
    background:linear-gradient(180deg,#2d2318,#1b130d 78%);
    border:2px solid var(--line);
    box-shadow:var(--shadow), inset 0 1px 0 var(--line-hi), inset 0 -2px 0 rgba(0,0,0,.5);
    padding:12px 14px;
    animation:rise .55s cubic-bezier(.2,.9,.2,1) both;
  }
  .panel::before,.panel::after{
    content:"";position:absolute;width:4px;height:4px;background:var(--gold);opacity:.75;
  }
  .panel::before{top:-2px;left:-2px}
  .panel::after{bottom:-2px;right:-2px}
  @keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}

  /* top bar */
  .topbar{top:14px;left:14px;display:flex;gap:16px;align-items:center}
  .brand{display:flex;gap:10px;align-items:center}
  #brandIcon{image-rendering:pixelated;border:2px solid var(--line);box-shadow:0 3px 0 #0d0905}
  .brand-title{font-family:'DotGothic16',monospace;font-size:19px;letter-spacing:.14em;line-height:1.1}
  .brand-title em{font-style:normal;color:var(--gold)}
  .brand-sub{font-size:11px;color:var(--muted);letter-spacing:.08em;margin-top:3px}
  .stats{display:flex;gap:14px;padding-left:14px;border-left:2px dashed rgba(111,85,60,.7)}
  .stat{display:flex;flex-direction:column;gap:2px;min-width:56px}
  .stat span{font-family:'DotGothic16',monospace;font-size:9px;letter-spacing:.18em;color:var(--muted)}
  .stat b{font-family:'DotGothic16',monospace;font-size:14px;color:var(--ink)}
  .stat b.hi{color:var(--grass)}

  /* minimap */
  .mapbox{top:14px;right:14px;width:186px}
  .map-title{font-family:'DotGothic16',monospace;font-size:10px;letter-spacing:.2em;color:var(--muted);margin-bottom:8px}
  #map{width:160px;height:160px;image-rendering:pixelated;display:block;border:2px solid var(--line);background:#0e1116}
  .map-legend{display:flex;gap:8px;align-items:center;font-size:11px;color:var(--muted);margin-top:8px}
  .lg{display:inline-block;width:10px;height:10px;border:1px solid #0d0905}
  .lg.grass{background:#6f9c52}.lg.water{background:#3a6ea5}.lg.tree{background:#3d6434}

  /* side box */
  .sidebox{right:14px;bottom:14px;width:236px}
  .sidebox h2{font-family:'DotGothic16',monospace;font-size:11px;letter-spacing:.2em;color:var(--gold);margin:0 0 8px;font-weight:400}
  .keys{list-style:none;margin:0 0 12px;padding:0;display:flex;flex-direction:column;gap:5px;font-size:12px;color:var(--muted)}
  .keys li{display:flex;gap:8px;align-items:baseline}
  kbd{
    font-family:'DotGothic16',monospace;font-size:11px;color:var(--ink);
    background:#3a2c1f;border:1px solid var(--line-hi);padding:2px 6px;box-shadow:0 2px 0 #0d0905;
  }
  .toggles{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:10px}
  .btn{
    font-family:'DotGothic16',monospace;font-size:11px;letter-spacing:.08em;
    background:#332619;color:var(--ink);border:2px solid var(--line);padding:7px 8px;cursor:pointer;
    box-shadow:0 3px 0 #0d0905;transition:transform .12s,background .12s,border-color .12s;
  }
  .btn:hover{transform:translateY(-2px);background:#40301f;border-color:var(--line-hi)}
  .btn:active{transform:translateY(2px);box-shadow:0 1px 0 #0d0905}
  .btn.on{background:#4d6c3c;border-color:#8fbb6c;color:#eef7e0}
  .btn.gold{background:#5a4320;border-color:#c29341;color:#fbe6b4}
  .btn.gold:hover{background:#775827}
  .seedrow{display:flex;gap:6px}
  #seed{
    flex:1;min-width:0;background:#120d09;border:2px solid var(--line);color:var(--ink);
    font-family:'DotGothic16',monospace;font-size:12px;padding:6px 8px;
  }
  #seed:focus{outline:none;border-color:var(--gold)}

  /* hotbar */
  .hotbar{
    position:fixed;z-index:6;left:50%;bottom:16px;transform:translateX(-50%);
    display:flex;gap:5px;padding:9px;
    background:linear-gradient(180deg,#2d2318,#1b130d);border:2px solid var(--line);
    box-shadow:var(--shadow), inset 0 1px 0 var(--line-hi);
    animation:rise .6s .1s cubic-bezier(.2,.9,.2,1) both;
    flex-wrap:wrap;justify-content:center;
  }
  .slot{
    position:relative;width:44px;height:44px;background:#1a130d;border:2px solid #3c2c1f;
    display:flex;align-items:center;justify-content:center;cursor:pointer;
    transition:transform .14s cubic-bezier(.2,.9,.2,1),border-color .14s,box-shadow .14s;
  }
  .slot canvas{width:30px;height:30px;image-rendering:pixelated}
  .slot .num{position:absolute;top:2px;left:3px;font-family:'DotGothic16',monospace;font-size:9px;color:var(--muted)}
  .slot:hover{transform:translateY(-4px);border-color:var(--line-hi)}
  .slot.sel{
    transform:translateY(-7px);border-color:var(--gold);
    box-shadow:0 0 0 2px rgba(243,195,82,.35),0 8px 0 rgba(0,0,0,.4);
    background:#241a11;
  }
  .slot.sel::after{
    content:"";position:absolute;bottom:-2px;left:0;right:0;height:3px;background:var(--gold);
  }
  .chip{
    position:fixed;z-index:6;left:50%;bottom:78px;transform:translateX(-50%);
    font-family:'DotGothic16',monospace;font-size:12px;letter-spacing:.12em;
    background:rgba(20,14,9,.85);border:2px solid var(--line);padding:5px 12px;color:var(--gold);
    box-shadow:0 3px 0 #0d0905;transition:opacity .2s;
  }
  #crosshair{position:fixed;z-index:5;left:50%;top:50%;transform:translate(-50%,-50%);pointer-events:none;mix-blend-mode:difference}
  #crosshair::before,#crosshair::after{content:"";position:absolute;background:#fff}
  #crosshair::before{left:-9px;top:-1px;width:18px;height:2px}
  #crosshair::after{left:-1px;top:-9px;width:2px;height:18px}
  #crosshair.pulse{animation:pulse .18s ease-out}
  @keyframes pulse{from{transform:translate(-50%,-50%) scale(1.5)}to{transform:translate(-50%,-50%) scale(1)}}

  #toast{
    position:fixed;z-index:9;left:50%;top:86px;transform:translate(-50%,-8px);opacity:0;
    font-family:'DotGothic16',monospace;font-size:12px;letter-spacing:.1em;
    background:#2b2013;border:2px solid var(--line-hi);padding:8px 14px;box-shadow:0 4px 0 #0d0905;
    transition:opacity .25s,transform .25s;pointer-events:none;
  }
  #toast.show{opacity:1;transform:translate(-50%,0)}

  /* overlay */
  #overlay{
    position:fixed;inset:0;z-index:12;display:flex;align-items:center;justify-content:center;
    background:
      radial-gradient(90% 70% at 50% 30%,rgba(20,26,34,.45),rgba(10,8,6,.92)),
      repeating-linear-gradient(0deg,rgba(0,0,0,.25) 0 2px,transparent 2px 8px);
    backdrop-filter:none;
  }
  #overlay.hide{display:none}
  .ov-inner{width:min(620px,92vw);text-align:center;animation:rise .6s cubic-bezier(.2,.9,.2,1) both}
  .ov-blocks{display:flex;gap:6px;justify-content:center;margin-bottom:18px}
  .ov-blocks canvas{width:34px;height:34px;image-rendering:pixelated;border:2px solid var(--line);
    box-shadow:0 3px 0 #0d0905;animation:bob 2.4s ease-in-out infinite}
  .ov-blocks canvas:nth-child(2n){animation-delay:.35s}
  .ov-blocks canvas:nth-child(3n){animation-delay:.7s}
  @keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}
  #overlay h1{
    font-family:'DotGothic16',monospace;font-weight:400;font-size:clamp(34px,7vw,58px);
    letter-spacing:.12em;margin:0 0 10px;line-height:1;
    text-shadow:0 3px 0 #0d0905, 0 6px 0 rgba(243,195,82,.25);
  }
  #overlay h1 span{display:block;color:var(--grass);font-size:.72em;letter-spacing:.3em;margin-top:6px}
  .ov-lede{font-size:13px;color:var(--muted);line-height:1.7;margin:0 0 22px}
  .ov-keys{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-bottom:24px;font-size:11px;color:var(--muted)}
  #startBtn{
    font-family:'DotGothic16',monospace;font-size:15px;letter-spacing:.14em;
    background:#4d6c3c;border:2px solid #8fbb6c;color:#f2f8e4;padding:14px 26px;cursor:pointer;
    box-shadow:0 5px 0 #0d0905;transition:transform .14s,background .14s;
  }
  #startBtn:hover{transform:translateY(-3px);background:#5e8247}
  #startBtn:active{transform:translateY(2px);box-shadow:0 1px 0 #0d0905}
  .ov-note{margin-top:16px;font-size:11px;color:#6f6353;letter-spacing:.08em}

  /* touch */
  #touch{position:fixed;z-index:7;inset:auto 0 70px 0;display:none;justify-content:space-between;padding:0 16px;gap:10px}
  #touch .dpad{display:grid;grid-template-columns:44px 44px 44px;grid-template-rows:44px 44px 44px;gap:4px}
  #touch .dpad .btn{height:44px;font-size:13px}
  #touch .dpad .blank{visibility:hidden}
  #touch .tbtns{display:flex;flex-direction:column;gap:6px;align-items:flex-end}
  #touch .tbtns .btn{padding:10px 12px}
  body.touch #touch{display:flex}
  body.touch .sidebox{display:none}
  @media (max-width:760px){
    .sidebox{display:none}
    .stats{flex-wrap:wrap;gap:10px}
    .topbar{left:10px;top:10px;padding:9px 10px}
    .mapbox{right:10px;top:10px;width:150px}
    #map{width:124px;height:124px}
  }
</style>
</head>
<body>
<div id="stage"><canvas id="gl"></canvas></div>
<div class="fx-grid"></div>
<div class="fx-vignette"></div>

<header class="panel topbar">
  <div class="brand">
    <canvas id="brandIcon" width="34" height="34"></canvas>
    <div>
      <div class="brand-title">VOXEL <em>GARDEN</em></div>
      <div class="brand-sub">ボクセル箱庭 — つくる・壊す・植える</div>
    </div>
  </div>
  <div class="stats">
    <div class="stat"><span>FPS</span><b id="fps">—</b></div>
    <div class="stat"><span>座標</span><b id="pos">—</b></div>
    <div class="stat"><span>面数</span><b id="tri">—</b></div>
    <div class="stat"><span>設置</span><b id="placed" class="hi">0</b></div>
    <div class="stat"><span>破壊</span><b id="broken">0</b></div>
    <div class="stat"><span>時刻</span><b id="clock">12:00</b></div>
  </div>
</header>

<div class="panel mapbox">
  <div class="map-title">MAP / TRUE TOP</div>
  <canvas id="map" width="64" height="64"></canvas>
  <div class="map-legend">
    <span class="lg grass"></span>陸 <span class="lg water"></span>水 <span class="lg tree"></span>木
  </div>
</div>

<div class="panel sidebox">
  <h2>CONTROLS</h2>
  <ul class="keys">
    <li><kbd>W A S D</kbd> 移動</li>
    <li><kbd>SPACE</kbd> ジャンプ / 上昇</li>
    <li><kbd>SHIFT</kbd> 走る / 下降(飛行)</li>
    <li><kbd>F</kbd> 飛行モード</li>
    <li><kbd>1〜9</kbd> / <kbd>ホイール</kbd> ブロック</li>
    <li><kbd>左クリック</kbd> 壊す（長押し連打）</li>
    <li><kbd>右クリック</kbd> 置く</li>
    <li><kbd>中クリック</kbd> 対象を採取</li>
    <li><kbd>Esc</kbd> 一時停止</li>
  </ul>
  <h2>OPTIONS</h2>
  <div class="toggles">
    <button class="btn" id="tFly">飛行</button>
    <button class="btn on" id="tCycle">昼夜</button>
    <button class="btn on" id="tCloud">雲</button>
    <button class="btn on" id="tPart">粒子</button>
    <button class="btn" id="tSound">音</button>
    <button class="btn on" id="tStars">星空</button>
  </div>
  <div class="seedrow">
    <input id="seed" value="garden-01">
    <button class="btn gold" id="bGen">再生成</button>
  </div>
  <div class="seedrow" style="margin-top:6px">
    <button class="btn" id="bSave">保存</button>
    <button class="btn" id="bLoad">読込</button>
    <button class="btn" id="bShot">スクショ</button>
  </div>
  <input type="range" id="time" min="0" max="24" step="0.05" value="12" style="width:100%;margin-top:10px">
</div>

<footer class="hotbar" id="hotbar"></footer>
<div class="chip" id="blockName">草ブロック</div>
<div id="crosshair"></div>
<div id="toast"></div>

<div id="touch">
  <div class="dpad">
    <span class="blank"></span><button class="btn" data-k="w">↑</button><span class="blank"></span>
    <button class="btn" data-k="a">←</button><span class="blank"></span><button class="btn" data-k="d">→</button>
    <span class="blank"></span><button class="btn" data-k="s">↓</button><span class="blank"></span>
  </div>
  <div class="tbtns">
    <button class="btn" id="tJump">ジャンプ</button>
    <button class="btn" id="tFly2">飛行</button>
    <button class="btn gold" id="tPlace">置く</button>
    <button class="btn" id="tBreak">壊す</button>
  </div>
</div>

<div id="overlay">
  <div class="ov-inner">
    <div class="ov-blocks" id="ovBlocks"></div>
    <h1>VOXEL<span>GARDEN</span></h1>
    <p class="ov-lede">64×32×64の voxel 庭。地形はシードから生成され、木と花と池が自動で生えます。<br>ブロックを壊し、積み、植えて、庭を自分好みに sculpt してください。</p>
    <div class="ov-keys">
      <kbd>WASD</kbd><kbd>SPACE</kbd><kbd>SHIFT</kbd><kbd>F 飛行</kbd><kbd>左クリック 破壊</kbd><kbd>右クリック 設置</kbd><kbd>1〜9</kbd>
    </div>
    <button id="startBtn">▶ はじめる（ポインターロック）</button>
    <p class="ov-note">Esc で一時停止 / デスクトップ推奨 / 庭は localStorage に保存できます</p>
  </div>
</div>

<script type="module">
let THREE;
try { THREE = await import('https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js'); }
catch { THREE = await import('https://unpkg.com/three@0.160.0/build/three.module.js'); }

/* ============ 定数・ブロック定義 ============ */
const WX=64, WY=32, WZ=64, CH=8, CXN=WX/CH, CZN=WZ/CH, WL=9;

const T = { grass_top:0, grass_side:1, dirt:2, stone:3, sand:4, bark:5, rings:6,
            leaves:7, plank:8, brick:9, glass:10, glow:11, snow:12, cobble:13,
            water:14, flower:15, plant:16, bed:17 };
const NT = 18;

const BLOCKS = {
  1:{name:'草ブロック', tile:{top:T.grass_top, side:T.grass_side, bottom:T.dirt}, solid:true, color:'#6f9c52'},
  2:{name:'土', tile:{all:T.dirt}, solid:true, color:'#8a6248'},
  3:{name:'石', tile:{all:T.stone}, solid:true, color:'#8f8f8f'},
  4:{name:'砂', tile:{all:T.sand}, solid:true, color:'#ded2a0'},
  5:{name:'原木', tile:{top:T.rings, side:T.bark, bottom:T.rings}, solid:true, color:'#6b4f38'},
  6:{name:'葉', tile:{all:T.leaves}, solid:true, color:'#4b7a3f'},
  7:{name:'水', tile:{all:T.water}, solid:false, trans:true, wave:true, color:'#3a6ea5'},
  8:{name:' plank', tile:{all:T.plank}, solid:true, color:'#b98b57'},
  9:{name:'レンガ', tile:{all:T.brick}, solid:true, color:'#a04f3f'},
  10:{name:'ガラス', tile:{all:T.glass}, solid:true, trans:true, color:'#bfe3ef'},
  11:{name:'glowstone', tile:{all:T.glow}, solid:true, emis:true, color:'#e0a72c'},
  12:{name:'雪', tile:{all:T.snow}, solid:true, color:'#eef3f8'},
  13:{name:'石レンガ', tile:{all:T.cobble}, solid:true, color:'#77777a'},
  14:{name:'花', tile:{all:T.flower}, solid:false, cross:true, color:'#d05244'},
  15:{name:'草葉', tile:{all:T.plant}, solid:false, cross:true, color:'#5c8b46'},
  16:{name:'基盤', tile:{all:T.bed}, solid:true, color:'#3a3430'},
};
BLOCKS[8].name = ' plank'.trim();
const HOTBAR = [1,2,3,13,4,5,6,8,9,10,11,7,14,15];

const idx = (x,y,z)=> x + WX*(z + WZ*y);
const getBlock = (x,y,z)=> (x<0||x>=WX||y<0||y>=WY||z<0||z>=WZ) ? 0 : world[idx(x,y,z)];
const opaque = t => !!BLOCKS[t] && BLOCKS[t].solid && !BLOCKS[t].trans && !BLOCKS[t].cross;

/* ============ Texture Atlas ============ */
const atlasCanvas = document.createElement('canvas');
atlasCanvas.width = 16*NT; atlasCanvas.height = 16;
const actx = atlasCanvas.getContext('2d');
function rngFactory(seed){ let s=seed; return ()=>{ s=(s*16807)%2147483647; return s/2147483647; }; }
function speckle(x,y,pal,density=0.45){
  const r = rngFactory(x*77+13);
  for(let py=0;py<16;py++) for(let px=0;px<16;px++){
    if(r()<density) actx.fillStyle = pal[Math.floor(r()*pal.length)];
    actx.fillRect(x*16+px, y, 1, 1);
  }
}
function base(x,y,c){ actx.fillStyle=c; actx.fillRect(x*16,y,16,16); }
function paintTiles(){
  base(0,0,'#6f9c52'); speckle(0,0,['#7fb25a','#628c46','#84b35d'],0.5);
  base(1,0,'#8a6248'); speckle(1,0,['#73523c','#9b755c','#8a6248'],0.45);
  actx.fillStyle='#6f9c52'; actx.fillRect(16,0,16,3);
  actx.fillStyle='#5f8846'; actx.fillRect(16,3,16,1);
  base(2,0,'#8a6248'); speckle(2,0,['#73523c','#9b755c','#7d5a41'],0.45);
  base(3,0,'#8f8f8f'); speckle(3,0,['#7a7a7a','#a0a0a0','#686868'],0.45);
  base(4,0,'#ded2a0'); speckle(4,0,['#cbbd8a','#ece1b4','#d6c896'],0.4);
  base(5,0,'#6b4f38'); { const r=rngFactory(91);
    for(let px=0;px<16;px++){ actx.fillStyle = r()<0.3?'#4f3827':'#7d5c42'; actx.fillRect(5*16+px,0,1,16); } }
  base(6,0,'#a87c52'); { const r=rngFactory(44);
    for(let py=0;py<16;py++) for(let px=0;px<16;px++){
      const d=Math.hypot(px-8,py-8);
      if(Math.floor(d)%2===0) actx.fillStyle='#95693f'; else if(r()<0.2) actx.fillStyle='#bd9468';
      actx.fillRect(6*16+px,py,1,1);
    } }
  base(7,0,'#4b7a3f'); speckle(7,0,['#3d6434','#5b8d4b','#2f5229'],0.55);
  base(8,0,'#b98b57'); { const r=rngFactory(7);
    for(let py=0;py<16;py++){ if(py%4===0){actx.fillStyle='#8f6a43';actx.fillRect(8*16,py,16,1);}
      for(let px=0;px<16;px++){ if(r()<0.12){actx.fillStyle='#a8794b';actx.fillRect(8*16+px,py,1,1);} } } }
  base(9,0,'#a04f3f'); { for(let py=0;py<16;py++){ if(py%4===0){actx.fillStyle='#c9b7a7';actx.fillRect(9*16,py,16,1);}
      for(let px=0;px<16;px++){ if((px+(py>>2)*2)%8===0){actx.fillStyle='#c9b7a7';actx.fillRect(9*16+px,py,1,1);} } } }
  base(10,0,'rgba(190,226,236,0.30)');
  actx.fillStyle='rgba(216,240,246,0.85)';
  actx.fillRect(10*16,0,16,2); actx.fillRect(10*16,14,16,2); actx.fillRect(10*16,0,2,16); actx.fillRect(10*16+14,0,2,16);
  actx.fillStyle='rgba(255,255,255,0.55)'; actx.fillRect(10*16+4,5,6,1); actx.fillRect(10*16+9,9,4,1);
  base(11,0,'#e0a72c'); speckle(11,0,['#f7d466','#c1852a','#ffe08a'],0.5);
  base(12,0,'#eef3f8'); speckle(12,0,['#dfe7ef','#ffffff','#cdd6e0'],0.35);
  base(13,0,'#77777a'); { const r=rngFactory(23);
    for(let py=0;py<16;py++) for(let px=0;px<16;px++){
      const v=r(); if(v<0.25) actx.fillStyle='#54565a'; else if(v<0.42) actx.fillStyle='#8b8f93';
      actx.fillRect(13*16+px,py,1,1);
    }
    actx.fillStyle='#43454a'; actx.fillRect(13*16,7,16,1); actx.fillRect(13*16+7,0,1,7); }
  base(14,0,'rgba(58,110,165,0.78)'); speckle(14,0,['#2f5b8c','#5b8bc8','#4479a9'],0.4);
  // 花
  actx.clearRect(15*16,0,16,16);
  actx.fillStyle='#4c7d3f'; actx.fillRect(15*16+7,11,2,5); actx.fillRect(15*16+6,12,1,2);
  actx.fillStyle='#d05244'; actx.fillRect(15*16+5,7,6,4); actx.fillStyle='#f0705c'; actx.fillRect(15*16+6,6,3,2);
  actx.fillStyle='#f7c85a'; actx.fillRect(15*16+7,8,2,2);
  // 草葉
  actx.clearRect(16*16,0,16,16);
  const blades=[[4,11],[6,8],[8,13],[10,9],[12,12],[5,7],[9,7]];
  for(const [bx,bh] of blades){ actx.fillStyle = bh>10?'#5c8b46':'#4a743a'; actx.fillRect(16*16+bx,16-(bh-3),1,bh-3); }
  base(17,0,'#3a3430'); speckle(17,0,['#2b2622','#4a423c'],0.5);
}
paintTiles();
const atlas = new THREE.CanvasTexture(atlasCanvas);
atlas.magFilter = THREE.NearestFilter; atlas.minFilter = THREE.NearestFilter;
atlas.generateMipmaps = false;
atlas.colorSpace = THREE.SRGBColorSpace;

/* ============ シーン ============ */
const canvas = document.getElementById('gl');
const renderer = new THREE.WebGLRenderer({canvas, antialias:true, preserveDrawingBuffer:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.setSize(innerWidth, innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;

const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x9ecdf0, 0.012);
const camera = new THREE.PerspectiveCamera(70, innerWidth/innerHeight, 0.1, 500);

const hemi = new THREE.HemisphereLight(0xa8d4f2, 0x4a3b2a, 0.55);
scene.add(hemi);
const sun = new THREE.DirectionalLight(0xfff2d6, 0.9);
scene.add(sun);
const moon = new THREE.DirectionalLight(0x8fb0d8, 0.12);
scene.add(moon);

/* sky dome */
const skyMat = new THREE.ShaderMaterial({
  side:THREE.BackSide, depthWrite:false, fog:false,
  uniforms:{ uSun:{value:new THREE.Vector3()}, uMoon:{value:new THREE.Vector3()},
             uZen:{value:new THREE.Color()}, uHor:{value:new THREE.Color()}, uSunCol:{value:new THREE.Color()} },
  vertexShader:`varying vec3 vDir; void main(){ vDir = position; gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.0); }`,
  fragmentShader:`
    varying vec3 vDir; uniform vec3 uSun,uMoon,uZen,uHor,uSunCol;
    void main(){
      vec3 d = normalize(vDir);
      float h = clamp(d.y*0.5+0.5,0.0,1.0);
      vec3 col = mix(uHor, uZen, pow(h,0.75));
      float s = dot(d,uSun);
      col += uSunCol * pow(max(s,0.0),8.0)*0.35;
      col += uSunCol * smoothstep(0.9955,0.9992,s)*2.2;
      float m = dot(d,uMoon);
      col += vec3(0.86,0.92,1.0)*smoothstep(0.9972,0.9995,m)*1.6;
      col += vec3(0.9,0.95,1.0)*pow(max(m,0.0),30.0)*0.18;
      gl_FragColor = vec4(col,1.0);
    }`
});
scene.add(new THREE.Mesh(new THREE.SphereGeometry(400,32,20), skyMat));

/* stars */
const starGeo = new THREE.BufferGeometry();
const sCount=700, sPos=new Float32Array(sCount*3);
for(let i=0;i<sCount;i++){
  const r=330, a=Math.random()*Math.PI*2, b=Math.acos(Math.random());
  sPos[i*3]=Math.sin(b)*Math.cos(a)*r; sPos[i*3+1]=Math.abs(Math.cos(b))*r*0.9+20; sPos[i*3+2]=Math.sin(b)*Math.sin(a)*r;
}
starGeo.setAttribute('position', new THREE.BufferAttribute(sPos,3));
const starMat = new THREE.PointsMaterial({color:0xe8f0ff, size:1.6, transparent:true, opacity:0, fog:false});
const stars = new THREE.Points(starGeo, starMat);
scene.add(stars);

/* clouds */
const cloudGeo = new THREE.BufferGeometry();
{
  const p=[], uv=[];
  const r = rngFactory(1234);
  for(let i=0;i<46;i++){
    const cx=(r()-0.5)*260, cz=(r()-0.5)*260, w=5+r()*11, d=5+r()*11, y=44+r()*6;
    const c=[[cx,y,cz],[cx+w,y,cz],[cx+w,y,cz+d],[cx,y,cz+d]];
    const u=[[0,0],[1,0],[1,1],[0,1]];
    for(let k=0;k<4;k++){ p.push(...c[k]); uv.push(...u[k]); }
    cloudGeo.setAttribute('position', new THREE.BufferAttribute(p,3));
  }
  cloudGeo.setIndex([0,1,2,0,2,3,4,5,6,4,6,7]);
  cloudGeo.setAttribute('uv', new THREE.BufferAttribute(uv,2));
  cloudGeo.setAttribute('normal', new THREE.BufferAttribute(new Float32Array(cloudGeo.attributes.position.count*3).fill(1),3));
  // rebuild properly: two quads
  const cp=[],cu=[],cn=[];
  const rr = rngFactory(987);
  for(let i=0;i<46;i++){
    const x0=(rr()-0.5)*260, z0=(rr()-0.5)*260, w=5+rr()*11, d=5+rr()*11, y=44+rr()*6;
    const corner=[[x0,y,z0],[x0+w,y,z0],[x0+w,y,z0+d],[x0,y,z0+d]];
    const u=[[0,0],[1,0],[1,1],[0,1]];
    for(let k=0;k<4;k++){ cp.push(...corner[k]); cu.push(...u[k]); cn.push(0,1,0); }
  }
  cloudGeo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(cp),3));
  cloudGeo.setAttribute('uv', new THREE.BufferAttribute(new Float32Array(cu),2));
  cloudGeo.setAttribute('normal', new THREE.BufferAttribute(new Float32Array(cn),3));
  cloudGeo.setIndex([0,1,2,0,2,3,4,5,6,4,6,7]);
  cloudGeo.computeBoundingSphere();
}
const cloudMat = new THREE.MeshLambertMaterial({color:0xf4f7fb, transparent:true, opacity:0.85, side:THREE.DoubleSide});
const clouds = new THREE.Mesh(cloudGeo, cloudMat);
scene.add(clouds);

/* materials */
const uTime = { value:0 };
const matSolid = new THREE.MeshLambertMaterial({map:atlas, vertexColors:true});
const matEmis  = new THREE.MeshLambertMaterial({map:atlas, vertexColors:true, emissive:0xffb347, emissiveIntensity:0.55});
const matTrans = new THREE.MeshLambertMaterial({map:atlas, vertexColors:true, transparent:true, depthWrite:false, side:THREE.DoubleSide});
matTrans.onBeforeCompile = sh => {
  sh.uniforms.uTime = uTime;
  sh.vertexShader = 'uniform float uTime;\nattribute float aWave;\n' + sh.vertexShader.replace(
    '#include <begin_vertex>',
    '#include <begin_vertex>\n transformed.y += aWave * sin(uTime*1.6 + position.x*0.8 + position.z*1.1) * 0.09;'
  );
};
const matCross = new THREE.MeshLambertMaterial({map:atlas, vertexColors:true, transparent:true, alphaTest:0.5, side:THREE.DoubleSide});

/* ============ 地形生成 ============ */
let seedNum = 0;
function hash2(x,y,s){ const n=Math.sin(x*127.1+y*311.7+s*7.13)*43758.5453123; return n-Math.floor(n); }
function noise2(x,y,s){
  const xi=Math.floor(x), yi=Math.floor(y), fx=x-xi, fy=y-yi;
  const a=hash2(xi,yi,s), b=hash2(xi+1,yi,s), c=hash2(xi,yi+1,s), d=hash2(xi+1,yi+1,s);
  const sx=fx*fx*(3-2*fx), sy=fy*fy*(3-2*fy);
  return (a*(1-sx)+b*sx)*(1-sy) + (c*(1-sx)+d*sx)*sy;
}
function fbm(x,y,s){
  let v=0, a=0.5, f=1;
  for(let i=0;i<4;i++){ v+=noise2(x*f,y*f,s+i)*a; a*=0.5; f*=2; }
  return v;
}

let world = new Uint8Array(WX*WZ*WY);

function genWorld(seedStr){
  let h=0; for(const ch of String(seedStr)) h=(h*31 + ch.charCodeAt(0))>>>0;
  seedNum = h || 1;
  world.fill(0);
  for(let x=0;x<WX;x++) for(let z=0;z<WZ;z++){
    const n1 = fbm(x*0.035, z*0.035, seedNum);
    const n2 = Math.pow(fbm(x*0.012+7, z*0.012+11, seedNum+3), 2.0);
    let ht = Math.floor(4 + n1*9 + n2*12);
    ht = Math.max(2, Math.min(WY-8, ht));
    const topSnow = ht > 19;
    for(let y=0;y<=ht;y++){
      let t = 3;
      if(y===ht) t = topSnow ? 12 : (ht<=WL ? 4 : 1);
      else if(y>ht-3) t = 2;
      if(y===0) t = 16;
      world[idx(x,y,z)] = t;
    }
    for(let y=ht+1;y<=WL;y++) world[idx(x,y,z)] = 7;
  }
  // 木
  for(let x=3;x<WX-3;x++) for(let z=3;z<WZ-3;z++){
    const h0 = world[idx(x,0,z)]; if(h0===0) continue;
    let ht=-1;
    for(let y=WY-1;y>=0;y--) if(world[idx(x,y,z)]!==0){ ht=y; break; }
    if(world[idx(x,ht,z)]!==1) continue;
    if(hash2(x*3.1,z*7.7,seedNum) > 0.955){
      const th = 4 + Math.floor(hash2(x,z,seedNum+1)*3);
      for(let y=ht+1;y<=ht+th && y<WY-1;y++) world[idx(x,y,z)] = 5;
      const top = ht+th;
      for(let dy=-2;dy<=1;dy++){
        const rad = dy<=-2 ? 2 : (dy===-1?2:1);
        for(let dx=-rad;dx<=rad;dx++) for(let dz=-rad;dz<=rad;dz++){
          if(Math.abs(dx)===rad && Math.abs(dz)===rad && dy>=0) continue;
          if(dx===0&&dz===0&&dy<=0) continue;
          const bx=x+dx, by=top+dy, bz=z+dz;
          if(bx<0||bx>=WX||bz<0||bz>=WZ||by<0||by>=WY) continue;
          if(world[idx(bx,by,bz)]===0) world[idx(bx,by,bz)] = 6;
        }
      }
    } else if(hash2(x*11.3,z*5.7,seedNum+2) > 0.88){
      if(world[idx(x,ht+1,z)]===0) world[idx(x,ht+1,z)] = hash2(x,z,seedNum+5)>0.45 ? 14 : 15;
    }
  }
}

/* ============ メッシュ化（AO付き） ============ */
const FACES = [
  {dir:[1,0,0], bright:0.72, ax:[2,1], corners:[[1,0,0],[1,1,0],[1,1,1],[1,0,1]], uv:[[0,0],[0,1],[1,1],[1,0]]},
  {dir:[-1,0,0], bright:0.72, ax:[2,1], corners:[[0,0,0],[0,0,1],[0,1,1],[0,1,0]], uv:[[0,0],[1,0],[1,1],[0,1]]},
  {dir:[0,1,0], bright:1.0, ax:[0,2], corners:[[0,1,0],[0,1,1],[1,1,1],[1,1,0]], uv:[[0,0],[0,1],[1,1],[1,0]]},
  {dir:[0,-1,0], bright:0.52, ax:[0,2], corners:[[0,0,0],[1,0,0],[1,0,1],[0,0,1]], uv:[[0,0],[1,0],[1,1],[0,1]]},
  {dir:[0,0,1], bright:0.86, ax:[0,1], corners:[[0,0,1],[1,0,1],[1,1,1],[0,1,1]], uv:[[0,0],[1,0],[1,1],[0,1]]},
  {dir:[0,0,-1], bright:0.86, ax:[0,1], corners:[[1,0,0],[0,0,0],[0,1,0],[1,1,0]], uv:[[0,0],[1,0],[1,1],[0,1]]},
];
const AO = [0.42,0.62,0.82,1.0];
const SHADING = [[0,0,0,0,1,1,1,0],[0,0,0,0,1,1,1,0],[0,1,1,0,0,0,0,0],[1,0,0,0,0,1,1,0]];

function group(){ return {pos:[],uv:[],col:[],nrm:[],idx:[],wave:[]}; }
function toGeo(g, wave=false){
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(g.pos,3));
  geo.setAttribute('uv', new THREE.Float32BufferAttribute(g.uv,2));
  geo.setAttribute('color', new THREE.Float32BufferAttribute(g.col,3));
  geo.setAttribute('normal', new THREE.Float32BufferAttribute(g.nrm,3));
  if(wave) geo.setAttribute('aWave', new THREE.Float32BufferAttribute(g.wave,1));
  geo.setIndex(g.idx);
  geo.computeBoundingSphere();
  return geo;
}
function tileFor(b,f){
  const t = b.tile;
  if(f<2) return t.side ?? t.all;
  if(f===2) return t.top ?? t.all;
  if(f===3) return t.bottom ?? t.all;
  if(f===4) return t.side ?? t.all;
  return t.side ?? t.all;
}

const chunks = [];
function buildChunk(cx,cz){
  const sx=cx*CH, sz=cz*CH;
  const solid=group(), emis=group(), trans=group(), cross=group();
  for(let y=0;y<WY;y++) for(let z=0;z<CH;z++) for(let x=0;x<CH;x++){
    const wx=sx+x, wz=sz+z;
    const t = world[idx(wx,y,wz)]; if(!t) continue;
    const b = BLOCKS[t];
    if(b.cross){ pushCross(cross, wx, y, wz, b); continue; }

    const target = b.emis ? emis : (b.trans ? trans : solid);
    const doWave = !!b.wave;
    for(let f=0;f<6;f++){
      const face = FACES[f];
      const n = getBlock(wx+face.dir[0], y+face.dir[1], wz+face.dir[2]);
      if(n === t) continue;
      if(opaque(n)) continue;
      if(n !== 0 && !b.trans && opaque(n)) continue;
      pushFace(target, wx, y, wz, face, tileFor(b,f), face.bright, doWave);
    }
  }

  const c = chunks[cx*CZN+cz];
  const base = {x:sx, y:0, z:sz};
  applyGeo(c.solid, solid, base, false);
  applyGeo(c.emis, emis, base, false);
  applyGeo(c.trans, trans, base, true);
  applyGeo(c.cross, cross, base, false);
}
function applyGeo(mesh, g, pos, wave){
  if(mesh.geometry) mesh.geometry.dispose();
  if(g.pos.length===0){ mesh.visible=false; mesh.geometry=new THREE.BufferGeometry(); return; }
  mesh.geometry = toGeo(g, wave);
  mesh.visible = true;
  mesh.position.set(pos.x,pos.y,pos.z);
}

function pushFace(g, x,y,z, face, tile, bright, wave){
  const tx = 1/NT;
  const u0 = (tile+0.06)*tx, u1 = (tile+0.94)*tx, v0 = 0.04, v1 = 0.96;
  const nb = [x+face.dir[0], y+face.dir[1], z+face.dir[2]];
  const [ax,ay] = face.ax;
  const aoVals = [];
  for(let i=0;i<4;i++){
    const c = face.corners[i];
    const sa = c[ax]===0 ? -1 : 1;
    const sb = c[ay]===0 ? -1 : 1;
    const off = [0,0,0]; off[ax]=sa; off[ay]=sb;
    const s1 = opaque(getBlock(nb[0]+(ax===0?sa:0), nb[1]+(ax===1?sa:0), nb[2]+(ax===2?sa:0)));
    const s2 = opaque(getBlock(nb[0]+(ay===0?sb:0), nb[1]+(ay===1?sb:0), nb[2]+(ay===2?sb:0)));
    const cr = opaque(getBlock(nb[0]+(ax===0?sa:0)+(ay===0?sb:0), nb[1]+(ax===1?sa:0)+(ay===1?sb:0), nb[2]+(ax===2?sa:0)+(ay===2?sb:0)));
    aoVals.push(s1&&s2 ? 0 : 3 - (s1+s2+cr));
  }
  const start = g.pos.length/3;
  for(let i=0;i<4;i++){
    const c = face.corners[i];
    g.pos.push(x+c[0], y+c[1], z+c[2]);
    g.uv.push(face.uv[i][0]?u1:u0, face.uv[i][1]?v1:v0);
    const sh = bright * AO[aoVals[i]];
    g.col.push(sh,sh,sh);
    g.nrm.push(...face.dir);
    g.wave.push(wave && face.dir[1]===1 ? 1 : 0);
  }
  if(aoVals[0]+aoVals[2] > aoVals[1]+aoVals[3]){
    g.idx.push(start,start+1,start+2, start,start+2,start+3);
  } else {
    g.idx.push(start+1,start+2,start+3, start+3,start,start+1);
  }
}
function pushCross(g, x,y,z, b){
  const tile = b.tile.all, tx=1/NT;
  const u0=(tile+0.05)*tx, u1=(tile+0.95)*tx, v0=0.05, v1=0.95;
  const q = [[
    [0.14,0,0.14],[0.86,0,0.86],[0.86,0.95,0.86],[0.14,0.95,0.14],
    [0.86,0,0.14],[0.14,0,0.86],[0.14,0.95,0.86],[0.86,0.95,0.14]
  ]];
  const uv=[[0,0],[1,0],[1,1],[0,1]];
  for(const quad of q[0].length ? [q[0].slice(0,4), q[0].slice(4)] : []){
    const start = g.pos.length/3;
    for(let i=0;i<4;i++){
      const c=quad[i];
      g.pos.push(x+c[0], y+c[1], z+c[2]);
      g.uv.push(uv[i][0]?u1:u0, uv[i][1]?v1:v0);
      g.col.push(0.92,0.95,0.9);
      g.nrm.push(0,1,0);
      g.wave.push(0);
    }
    g.idx.push(start,start+1,start+2, start,start+2,start+3);
    g.idx.push(start,start+2,start+1, start,start+3,start+2);
  }
}

function initChunks(){
  while(scene.children.some(c=>c.userData.chunk)) scene.remove(scene.children.find(c=>c.userData.chunk));
  chunks.length=0;
  for(let cx=0;cx<CXN;cx++) for(let cz=0;cz<CZN;cz++){
    const solid = new THREE.Mesh(new THREE.BufferGeometry(), matSolid);
    const emis  = new THREE.Mesh(new THREE.BufferGeometry(), matEmis);
    const trans = new THREE.Mesh(new THREE.BufferGeometry(), matTrans);
    const cross = new THREE.Mesh(new THREE.BufferGeometry(), matCross);
    [solid,emis,trans,cross].forEach(m=>{ m.userData.chunk=true; m.visible=false; scene.add(m); });
    chunks.push({solid,emis,trans,cross});
  }
  rebuildAll();
}
function rebuildAll(){ for(let cx=0;cx<CXN;cx++) for(let cz=0;cz<CZN;cz++) buildChunk(cx,cz); updateTri(); }
function touch(x,y,z){
  const cx=Math.floor(x/CH), cz=Math.floor(z/CH);
  const set = new Set([cx+'-'+cz]);
  if(x%CH===0) set.set((cx-1)+'-'+cz);
  if(x%CH===CH-1) set.set((cx+1)+'-'+cz);
  if(z%CH===0) set.set(cx+'-'+(cz-1));
  if(z%CH===CH-1) set.set(cx+'-'+(cz+1));
  for(const k of set){ const [a,b]=k.split('-').map(Number); if(a>=0&&a<CXN&&b>=0&&b<CZN) buildChunk(a,b); }
  updateTri();
}
function updateTri(){
  let n=0; for(const c of chunks) for(const m of [c.solid,c.emis,c.trans,c.cross]) if(m.visible) n += m.geometry.index.count/3;
  document.getElementById('tri').textContent = n.toLocaleString();
}

/* ============ 選択ハイライト ============ */
const hl = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(1.002,1.002,1.002)),
  new THREE.LineBasicMaterial({color:0x1a1a1a, transparent:true, opacity:0.85}));
hl.visible=false; scene.add(hl);
const ghost = new THREE.Mesh(new THREE.BoxGeometry(1,1,1),
  new THREE.MeshBasicMaterial({color:0xffffff, transparent:true, opacity:0.22}));
ghost.visible=false; scene.add(ghost);

/* ============ 粒子 ============ */
const PMAX=320;
const particles = new THREE.InstancedMesh(new THREE.BoxGeometry(0.16,0.16,0.16), new THREE.MeshLambertMaterial(), PMAX);
particles.instanceColor = new THREE.InstancedBufferAttribute(new Float32Array(PMAX*3),3);
particles.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
scene.add(particles);
const ps=[]; for(let i=0;i<PMAX;i++) ps.push({life:0,pos:new THREE.Vector3(),vel:new THREE.Vector3(),size:1,color:new THREE.Color()});
const dummy = new THREE.Matrix4();
function spawnParticles(x,y,z,type){
  if(!opts.particles) return;
  const c = new THREE.Color(BLOCKS[type].color);
  for(let i=0;i<12;i++){
    const p = ps.find(q=>q.life<=0); if(!p) break;
    p.life = 0.75+Math.random()*0.5;
    p.pos.set(x+0.5+(Math.random()-0.5)*0.6, y+0.5+(Math.random()-0.5)*0.6, z+0.5+(Math.random()-0.5)*0.6);
    p.vel.set((Math.random()-0.5)*4.5, 2+Math.random()*4, (Math.random()-0.5)*4.5);
    p.size = 0.7+Math.random()*0.6;
    p.color.copy(c).offsetHSL(0,(Math.random()-0.5)*0.1,(Math.random()-0.5)*0.12);
  }
}
function updateParticles(dt){
  let n=0;
  for(const p of ps){
    if(p.life>0){
      p.life-=dt;
      p.vel.y -= 18*dt;
      p.pos.addScaledVector(p.vel, dt);
      p.size = Math.max(0.2, p.life*0.9);
      dummy.compose(new THREE.Vector3(p.pos.x,p.pos.y,p.pos.z), new THREE.Quaternion(), new THREE.Vector3(p.size,p.size,p.size));
      particles.setMatrixAt(n, dummy);
      particles.setColorAt(n, p.color);
      n++;
    }
  }
  for(let i=n;i<PMAX;i++){ dummy.compose(new THREE.Vector3(0,-999,0), new THREE.Quaternion(), new THREE.Vector3(0.001,0.001,0.001)); particles.setMatrixAt(i,dummy); }
  particles.instanceMatrix.needsUpdate=true;
  if(particles.instanceColor) particles.instanceColor.needsUpdate=true;
}

/* ============ プレイヤー ============ */
const player = { pos:new THREE.Vector3(WX/2, WY, WZ/2), vel:new THREE.Vector3(), yaw:0, pitch:0, onGround:false, bob:0 };
function spawn(){
  const x=Math.floor(WX/2), z=Math.floor(WZ/2);
  let y=WY-1; while(y>0 && getBlock(x,y,z)===0) y--;
  player.pos.set(x+0.5, y+1.1, z+0.5); player.vel.set(0,0,0);
}
function solidAt(x,y,z){ const t=getBlock(x,y,z); return !!BLOCKS[t] && BLOCKS[t].solid; }
function collides(px,py,pz){
  const w=0.3, h=1.8;
  const x0=Math.floor(px-w), x1=Math.floor(px+w);
  const y0=Math.floor(py), y1=Math.floor(py+h);
  const z0=Math.floor(pz-w), z1=Math.floor(pz+w);
  for(let x=x0;x<=x1;x++) for(let y=y0;y<=y1;y++) for(let z=z0;z<=z1;z++) if(solidAt(x,y,z)) return true;
  return false;
}
const keys = {};
function updatePlayer(dt){
  const fly = opts.fly;
  const sprint = keys['shift'] && !fly;
  const speed = fly ? (keys['shift'] ? 8 : 16) : (sprint ? 7.4 : 4.6);
  const dir = new THREE.Vector3();
  if(keys['w']) dir.z -= 1;
  if(keys['s']) dir.z += 1;
  if(keys['a']) dir.x -= 1;
  if(keys['d']) dir.x += 1;
  dir.normalize();
  const cs=Math.cos(player.yaw), sn=Math.sin(player.yaw);
  const move = new THREE.Vector3(dir.x*cs - dir.z*sn, 0, dir.x*sn + dir.z*cs).multiplyScalar(speed);

  if(fly){
    player.vel.x = move.x; player.vel.z = move.z;
    player.vel.y = keys[' '] ? 9 : (keys['shift'] ? -9 : 0);
  } else {
    player.vel.x += (move.x - player.vel.x) * Math.min(1, dt*12);
    player.vel.z += (move.z - player.vel.z) * Math.min(1, dt*12);
    player.vel.y -= 24*dt;
    if(keys[' '] && player.onGround){ player.vel.y = 8.4; player.onGround=false; }
  }

  const p = player.pos;
  p.x += player.vel.x*dt;
  if(collides(p.x,p.y,p.z)){ p.x -= player.vel.x*dt; player.vel.x=0; }
  p.z += player.vel.z*dt;
  if(collides(p.x,p.y,p.z)){ p.z -= player.vel.z*dt; player.vel.z=0; }
  p.y += player.vel.y*dt;
  if(collides(p.x,p.y,p.z)){
    if(player.vel.y<0) player.onGround = true;
    p.y -= player.vel.y*dt; player.vel.y=0;
  } else if(player.vel.y<0) player.onGround=false;

  p.x = Math.max(0.2, Math.min(WX-0.2, p.x));
  p.z = Math.max(0.2, Math.min(WZ-0.2, p.z));
  if(p.y < -6){ spawn(); toast('虚空から復帰'); }

  const moving = (Math.abs(player.vel.x)+Math.abs(player.vel.z))>1.2 && player.onGround;
  player.bob += dt * (moving?7:0);
  camera.position.set(p.x, p.y+1.62 + Math.sin(player.bob)*0.05, p.z);
  camera.rotation.set(player.pitch, player.yaw, Math.sin(player.bob*0.5)*0.008);
  const targetFov = sprint ? 82 : (opts.fly ? 76 : 70);
  camera.fov += (targetFov-camera.fov)*Math.min(1,dt*6);
  camera.updateProjectionMatrix();
}

/* ============ voxel raycast ============ */
function raycastVoxel(origin, dir, maxDist){
  let x=Math.floor(origin.x), y=Math.floor(origin.y), z=Math.floor(origin.z);
  const stepX=Math.sign(dir.x), stepY=Math.sign(dir.y), stepZ=Math.sign(dir.z);
  const tDeltaX = stepX!==0 ? Math.abs(1/dir.x) : Infinity;
  const tDeltaY = stepY!==0 ? Math.abs(1/dir.y) : Infinity;
  const tDeltaZ = stepZ!==0 ? Math.abs(1/dir.z) : Infinity;
  let tMaxX = stepX!==0 ? ((stepX>0 ? x+1-origin.x : origin.x-x)*tDeltaX) : Infinity;
  let tMaxY = stepY!==0 ? ((stepY>0 ? y+1-origin.y : origin.y-y)*tDeltaY) : Infinity;
  let tMaxZ = stepZ!==0 ? ((stepZ>0 ? z+1-origin.z : origin.z-z)*tDeltaZ) : Infinity;
  let t=0, last=[x,y,z];
  while(t<maxDist){
    const bt = getBlock(x,y,z);
    if(bt) return {x,y,z,type:bt, nx:last[0], ny:last[1], nz:last[2]};
    last=[x,y,z];
    if(tMaxX < tMaxY && tMaxX < tMaxZ){ x+=stepX; t=tMaxX; tMaxX+=tDeltaX; }
    else if(tMaxY < tMaxZ){ y+=stepY; t=tMaxY; tMaxY+=tDeltaY; }
    else { z+=stepZ; t=tMaxZ; tMaxZ+=tDeltaZ; }
    if(x<-1||x>WX||y<0||y>WY||z<-1||z>WZ) break;
  }
  return null;
}

/* ============ 操作 ============ */
let slot = 0, placed=0, broken=0;
const hotbarEl = document.getElementById('hotbar');
function drawIcon(canvasEl, tile, size){
  const c = canvasEl.getContext('2d');
  canvasEl.width = size; canvasEl.height = size;
  c.imageSmoothingEnabled = false;
  c.clearRect(0,0,size,size);
  c.drawImage(atlasCanvas, tile*16,0,16,16, 0,0,size,size);
}
function buildHotbar(){
  hotbarEl.innerHTML='';
  HOTBAR.forEach((type,i)=>{
    const b = BLOCKS[type];
    const el = document.createElement('div');
    el.className = 'slot'+(i===slot?' sel':'');
    el.title = b.name;
    el.innerHTML = `<span class="num">${i+1}</span>`;
    const cv = document.createElement('canvas');
    drawIcon(cv, b.tile.side ?? b.tile.all ?? b.tile.top, 30);
    el.appendChild(cv);
    el.addEventListener('click', ()=>select(i));
    hotbarEl.appendChild(el);
  });
  document.getElementById('blockName').textContent = BLOCKS[HOTBAR[slot]].name;
}
function select(i