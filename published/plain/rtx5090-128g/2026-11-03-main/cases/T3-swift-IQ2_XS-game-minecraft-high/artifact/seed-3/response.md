マイクラ風の3D箱庭サンドボックスを作りました。ノイズ生成で地形・洞窟・木を作り、昼夜サイクル・照明・雨・パーティクル・ procedurally 生成テクスチャ、合成音付き。単一HTMLで動作します(Three.jsをCDNから読み込み)。

```html
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>VOXEL CRAFT — 3D箱庭サンドボックス</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&family=DotGothic16&display=swap" rel="stylesheet">
<style>
  :root{
    --edge:#0a0d12; --panel:#1b212b; --panel2:#232b38;
    --gold:#ffd23f; --grass:#7dc95a; --stone:#9aa1ac; --sky:#78a7ff;
  }
  *{box-sizing:border-box; margin:0; padding:0}
  html,body{height:100%; overflow:hidden; background:#0b1026; font-family:'DotGothic16',monospace; color:#e8ecf1}
  canvas#gl{position:fixed; inset:0; display:block}

  /* ============ 共通ピクセルパネル ============ */
  .panel{
    background:linear-gradient(180deg,var(--panel2),var(--panel));
    border:3px solid #05080c;
    box-shadow:0 0 0 2px #3a4453 inset, 0 10px 30px rgba(0,0,0,.55);
    position:relative;
  }
  .panel::before,.panel::after{
    content:''; position:absolute; width:8px;height:8px; background:var(--gold);
    border:2px solid #05080c; top:-6px; left:-6px;
  }
  .panel::after{top:auto; left:auto; bottom:-6px; right:-6px}

  h1,h2,.px{font-family:'Press Start 2P',monospace}

  /* ============ スタート画面 ============ */
  #boot{position:fixed; inset:0; display:flex; flex-direction:column; align-items:center;
       justify-content:center; background:
       radial-gradient(1200px 700px at 70% 20%, #2b3b5e, transparent 60%),
       radial-gradient(900px 600px at 20% 85%, #22313f, transparent 55%),
       linear-gradient(180deg,#121a2e,#0b1026 70%);
       z-index:40; transition:opacity .35s; gap:18px; overflow:hidden}
  #boot.hide{opacity:0; pointer-events:none}
  .stars2{position:absolute; inset:0; background-image:
    radial-gradient(1px 1px at 20% 30%, #fff9, transparent),
    radial-gradient(1px 1px at 60% 60%, #fff7, transparent),
    radial-gradient(1px 1px at 80% 15%, #fff8, transparent),
    radial-gradient(1px 1px at 45% 80%, #fff6, transparent),
    radial-gradient(1px 1px at 90% 70%, #fff5, transparent);
    animation:tw 4s ease-in-out infinite alternate}
  @keyframes tw{from{opacity:.4}to{opacity:1}}

  .title{
    font-size:clamp(26px,5.4vw,64px); letter-spacing:.06em; color:#fff;
    text-shadow:
      0 6px 0 #0d1220, 0 8px 0 #0d1220, 0 10px 24px rgba(0,0,0,.6),
      0 2px 0 #4c5568, 0 -1px 0 #4c5568;
    margin-top:6px
  }
  .title span{color:var(--gold)}
  .title small{display:block; font-family:'DotGothic16'; font-size:18px; color:#9fb0c8; margin-top:14px; letter-spacing:.28em}

  #cubeWrap{perspective:900px; width:120px; height:120px}
  #cube{position:relative; width:120px; height:120px; transform-style:preserve-3d; animation:spin 14s linear infinite}
  #cube div{position:absolute; width:120px; height:120px; background-size:cover; image-rendering:pixelated; opacity:.96; border:2px solid #05080c}
  @keyframes spin{from{transform:rotateX(-18deg) rotateY(0deg)} to{transform:rotateX(-18deg) rotateY(360deg)}}

  .seedbox{display:flex; gap:10px; align-items:center; margin-top:4px}
  .seedbox input{width:200px; background:#101520; color:var(--gold); border:3px solid #05080c;
    box-shadow:0 0 0 2px #39424f inset; padding:10px 12px; font-family:'Press Start 2P'; font-size:11px}
  .btn{
    font-family:'Press Start 2P'; font-size:12px; color:#fff; cursor:pointer;
    background:linear-gradient(180deg,#4c5568,#2b3240); border:3px solid #05080c;
    box-shadow:0 0 0 2px #5a6578 inset, 0 6px 0 #11161f;
    padding:14px 22px; transition:transform .12s, background .12s; letter-spacing:.05em
  }
  .btn:hover{transform:translateY(-2px); background:linear-gradient(180deg,#5a7d4a,#33412f)}
  .btn:active{transform:translateY(2px); box-shadow:0 0 0 2px #5a6578 inset, 0 2px 0 #11161f}
  .btn.gold{background:linear-gradient(180deg,var(--gold),#c98a1f); color:#231a06; box-shadow:0 0 0 2px #ffe28a inset, 0 6px 0 #4a3410}
  .btn.gold:hover{background:linear-gradient(180deg,#ffe28a,var(--gold))}
  .chips{display:flex; gap:10px; flex-wrap:wrap; justify-content:center; margin-top:22px; max-width:860px}
  .chip{font-size:14px; color:#a9b6c8; background:#141a26; border:2px solid #05080c; padding:6px 12px;
    box-shadow:0 0 0 1px #2c3644 inset}
  .chip b{color:#fff}
  #loadTxt{font-size:15px; color:#8fa0b6; margin-top:10px; letter-spacing:.2em}

  /* ============ HUD ============ */
  #hud{position:fixed; inset:0; pointer-events:none; z-index:10; display:none}
  #hud.on{display:block}

  #info{position:fixed; left:14px; top:14px; padding:10px 14px; font-size:13px; line-height:1.9; min-width:220px}
  #info b{color:var(--gold)}
  #debug{display:none; color:#cfd6e2}
  #debug.on{display:block}
  #clock{position:fixed; right:14px; top:14px; width:112px; padding:8px; text-align:center; font-size:12px}
  #clock canvas{image-rendering:pixelated}
  #clock div{margin-top:6px; font-size:11px; color:#cfd6e2}
  #mapwrap{position:fixed; right:14px; top:96px; width:112px; padding:8px}
  #map{image-rendering:pixelated; width:96px; height:96px; border:2px solid #05080c; background:#0b1026}

  #cross{position:fixed; left:50%; top:50%; transform:translate(-50%,-50%); width:22px; height:22px; opacity:.85}
  #cross::before,#cross::after{content:''; position:absolute; background:#fff; mix-blend-mode:difference}
  #cross::before{left:50%; top:0; width:2px; height:100%}
  #cross::after{top:50%; left:0; height:2px; width:100%}

  #hotbar{position:fixed; left:50%; bottom:26px; transform:translateX(-50%); display:flex; gap:6px;
    padding:8px; pointer-events:auto}
  .slot{position:relative; width:46px; height:46px; background:#242c39; border:2px solid #05080c;
    box-shadow:0 0 0 1px #313c4d inset; cursor:pointer; transition:transform .12s}
  .slot canvas{position:absolute; left:3px; top:3px; image-rendering:pixelated}
  .slot.act{border-color:#fff; transform:translateY(-6px); box-shadow:0 0 0 2px #fff inset, 0 0 14px #fff6}
  .slot .num{position:absolute; left:2px; top:1px; font-family:'Press Start 2P'; font-size:8px; color:#cfd6e2}
  #slotName{position:fixed; left:50%; bottom:84px; transform:translateX(-50%); font-size:16px; color:#fff;
    text-shadow:0 2px 0 #000; letter-spacing:.14em}
  #uw{position:fixed; inset:0; background:#1f5e9e; opacity:0; pointer-events:none; transition:opacity .3s; z-index:9}

  #toast{position:fixed; left:50%; top:22%; transform:translateX(-50%); font-size:18px; color:#fff;
    text-shadow:0 3px 0 #000; letter-spacing:.15em; opacity:0; transition:opacity .3s; z-index:11}

  /* ============ ポーズ ============ */
  #pause{position:fixed; inset:0; z-index:30; display:none; background:rgba(6,10,18,.78)}
  #pause.on{display:flex; align-items:center; justify-content:center}
  #pausePanel{width:min(760px,94vw); max-height:86vh; overflow:auto; padding:26px 30px}
  #pausePanel h2{font-size:18px; color:var(--gold); margin-bottom:18px; letter-spacing:.1em}
  .cols{display:grid; grid-template-columns:1.1fr 1fr; gap:20px}
  @media(max-width:700px){.cols{grid-template-columns:1fr}}
  .keytbl{font-size:14px; line-height:1.5; width:100%; border-collapse:collapse}
  .keytbl td{padding:5px 6px}
  .keytbl td:first-child{width:74px}
  kbd{font-family:'Press Start 2P'; font-size:10px; background:#101520; color:#fff; border:2px solid #05080c;
    box-shadow:0 0 0 1px #374152 inset; padding:4px 6px; display:inline-block}
  .set{font-size:14px}
  .set label{display:block; margin:12px 0 4px; color:#9fb0c8; font-size:12px; letter-spacing:.1em}
  input[type=range]{width:100%; accent-color:var(--gold)}
  .rowbtns{display:flex; gap:8px; flex-wrap:wrap; margin-top:14px}
  .rowbtns .btn{font-size:10px; padding:10px 14px}
  #seedIn{width:100%; background:#101520; color:var(--gold); border:3px solid #05080c;
    box-shadow:0 0 0 2px #39424f inset; padding:10px; font-family:'Press Start 2P'; font-size:11px}
  .toggle{display:flex; justify-content:space-between; align-items:center; font-size:14px; margin-top:12px; color:#cfd6e2}
  .toggle input{accent-color:var(--gold); transform:scale(1.4)}
  #tips{font-size:13px; color:#93a2b6; margin-top:14px; line-height:1.7}
</style>
</head>
<body>

<canvas id="gl"></canvas>

<div id="uw"></div>

<!-- ============ スタート画面 ============ -->
<div id="boot">
  <div class="stars2"></div>
  <div id="cubeWrap"><div id="cube"></div></div>
  <div class="title px">VOXEL<span>◆</span>CRAFT<small>ボクセルで遊ぶ3D箱庭</small></div>
  <div class="seedbox">
    <input id="seed" value="minecraft" maxlength="12" spellcheck="false">
    <button class="btn gold" id="btnPlay">遊ぶ ▶</button>
    <button class="btn" id="btnFlat">平坦ワールド</button>
  </div>
  <div id="loadTxt"></div>
  <div class="chips">
    <span class="chip"><b>WASD</b> 移動</span>
    <span class="chip"><b>マウス</b> 視点</span>
    <span class="chip"><b>左クリック</b> 破壊</span>
    <span class="chip"><b>右クリック</b> 設置</span>
    <span class="chip"><b>1〜0</b> 持ち物</span>
    <span class="chip"><b>F</b> 飛ぶ</span>
    <span class="chip"><b>T</b> 天気</span>
    <span class="chip"><b>Esc</b> メニュー</span>
  </div>
  <div class="tips" style="font-size:13px;color:#93a2b6;max-width:820px;text-align:center">
    クリックでマウスを捕まえます。洞窟を掘って、ランプで明るくし、木を切って建築してください。<br>
    時間経過で昼→夜→雨。夜は暗いので明かりを置きましょう。
  </div>
</div>

<!-- ============ HUD ============ -->
<div id="hud">
  <div id="info" class="panel">
    <div><b>XZ</b> <span id="pos">0, 0</span></div>
    <div><b>FPS</b> <span id="fps">0</span> <b>TIME</b> <span id="time">06:00</span></div>
    <div id="debug">
      Chunk: <span id="ck">0</span> · 生成中: <span id="pend">0</span><br>
      飛ぶ: <span id="fly">OFF</span> · 雨: <span id="rainS">OFF</span> · 音: <span id="sfx">ON</span>
    </div>
  </div>
  <div id="clock" class="panel"><canvas id="clockCv" width="96" height="48"></canvas><div>太陽 / 月</div></div>
  <div id="mapwrap" class="panel"><canvas id="map" width="96" height="96"></canvas></div>
  <div id="cross"></div>
  <div id="slotName">草ブロック</div>
  <div id="hotbar" class="panel"></div>
  <div id="toast"></div>
</div>

<!-- ============ ポーズ ============ -->
<div id="pause">
  <div id="pausePanel" class="panel">
    <h2 class="px">一時停止</h2>
    <div class="cols">
      <div>
        <table class="keytbl">
          <tr><td><kbd>W A S D</kbd></td><td>移動 (Ctrlで走る / Shiftで忍び足)</td></tr>
          <tr><td><kbd>Space</kbd></td><td>ジャンプ (水中では浮上)</td></tr>
          <tr><td><kbd>F</kbd></td><td>飛ぶ モード切替 (Space昇 / Shift降)</td></tr>
          <tr><td><kbd>左クリック</kbd></td><td>ブロック破壊</td></tr>
          <tr><td><kbd>右クリック</kbd></td><td>ブロック設置</td></tr>
          <tr><td><kbd>1..9 / 0</kbd></td><td>持ち物スロット (0=消去)</td></tr>
          <tr><td><kbd>ホイール</kbd></td><td>スロット切替</div>
          <tr><td><kbd>T</kbd></td><td>天気を切り替える(晴れ/曇り/雨)</td></tr>
          <tr><td><kbd>M</kbd></td><td>環境音(音楽) ON/OFF</td></tr>
          <tr><td><kbd>P</kbd></td><td>ミュート</td></tr>
          <tr><td><kbd>R</kbd></td><td>時間速度 1× / 6× / 停止</td></tr>
          <tr><td><kbd>F3</kbd></td><td>デバッグ表示</td></tr>
        </table>
        <div id="tips">コツ: 草の下は土、さらに石。洞窟は暗いので Lamp(ランプ) を置くと灯りが広がります。<br>ガラスは透明度、葉は隙間から光が差します。水には当たり判定なし(泳げます)。</div>
      </div>
      <div class="set">
        <label>マウス感度 <span id="sensV"></span></label>
        <input type="range" id="sens" min="1" max="10" value="3">
        <label>視点 FOV <span id="fovV"></span></label>
        <input type="range" id="fov" min="65" max="105" value="75">
        <label>音量 <span id="volV"></span></label>
        <input type="range" id="vol" min="0" max="100" value="35">
        <label>フォグ距離(表示) <span id="fogV"></span></label>
        <input type="range" id="fog" min="20" max="60" value="42">
        <div class="toggle"><span>環境音(風のBGM)</span><input type="checkbox" id="amb" checked></div>
        <div class="toggle"><span>昼/夜サイクル</span><input type="checkbox" id="cycle" checked></div>
        <label style="margin-top:16px">ワールド シード</label>
        <input id="seedIn" value="minecraft" maxlength="12" spellcheck="false">
        <div class="rowbtns">
          <button class="btn gold" id="btnNew">再生成</button>
          <button class="btn" id="btnFlat2">平坦</button>
          <button class="btn" id="btnSave">保存</button>
          <button class="btn" id="btnLoad">読込</button>
          <button class="btn" id="btnResume">再開 ▶</button>
        </div>
      </div>
    </div>
  </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(()=>{
"use strict";
/* =========================================================
   定数・ワールドデータ
========================================================= */
const W=64, Z=64, H=48, N=W*Z*H, CS=16, CX=W/CS, CZ=Z/CS, SEA=8;
const AIR=0,GRASS=1,DIRT=2,STONE=3,SAND=4,LOG=5,PLANK=6,LEAF=7,GLASS=8,
      GLOW=9,SNOW=10,WATER=11,BRICK=12,COBBLE=13;

const NAMES={1:"草ブロック",2:"土",3:"石",4:"砂",5:"原木",6:"木材",7:"葉",8:"ガラス",
             9:"ランプ(灯り)",10:"雪",12:"レンガ",13:"石レンガ",0:"消去ツール"};
const SLOTS=[GRASS,STONE,COBBLE,LOG,PLANK,LEAF,SAND,GLASS,GLOW,0]; // key 1..0
const MINIMAP={0:null,1:"#6fb35c",2:"#866043",3:"#8b8b8b",4:"#dcd4a2",5:"#6a5138",
               6:"#a08050",7:"#3f8f3f",8:"#cfeef0",9:"#b78d3f",10:"#f3f7f7",
               11:"#3c63a8",12:"#9a4d42",13:"#7d7d7d"};
const PART_COLOR={1:[.42,.71,.36],2:[.53,.38,.26],3:[.55,.55,.55],4:[.87,.83,.63],
  5:[.42,.32,.22],6:[.63,.5,.31],7:[.25,.56,.25],8:[.8,.93,.94],9:[.72,.55,.25],
  10:[.95,.97,.97],11:[.24,.39,.66],12:[.61,.31,.26],13:[.49,.49,.49]};

const FACES=[ // 法線, 4隅(適当な順序 — DoubleSide), 面陰影
  {d:[1,0,0], c:[[1,0,0],[1,0,1],[1,1,1],[1,1,0]], s:0.80},
  {d:[-1,0,0],c:[[0,0,0],[0,0,1],[0,1,1],[0,1,0]], s:0.80},
  {d:[0,1,0], c:[[0,1,0],[0,1,1],[1,1,1],[1,1,0]], s:1.00},
  {d:[0,-1,0],c:[[0,0,0],[0,0,1],[1,0,1],[1,0,0]], s:0.62},
  {d:[0,0,1], c:[[0,0,1],[1,0,1],[1,1,1],[0,1,1]], s:0.88},
  {d:[0,0,-1],c:[[0,0,0],[1,0,0],[1,1,0],[0,1,0]], s:0.88},
];
const tileFor=(b,f)=>{
  switch(b){
    case GRASS: return f===2?0: f===3?2:1;
    case DIRT:  return 2;
    case STONE: return 3;
    case SAND:  return 4;
    case LOG:   return (f===2||f===3)?5:6;
    case PLANK: return 7;
    case LEAF:  return 8;
    case GLASS: return 9;
    case GLOW:  return 11;
    case SNOW:  return f===2?12: f===3?2:13;
    case WATER: return 15;
    case BRICK: return 10;
    case COBBLE:return 14;
  } return 2;
};

let blocks, sky, blkL;
function idx(x,y,z){return x+z*W+y*W*Z;}
function getB(x,y,z){ if(x<0||x>=W||z<0||z>=Z||y<0||y>=H) return AIR; return blocks[idx(x,y,z)]; }
function solid(b){ return b!==AIR && b!==WATER; }

/* 乱数 */
function mulberry(a){return ()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);
  t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
let seedNum=1, rng=mulberry(1);
function hashX(x,z){let n=(x*374761393+z*668265263+seedNum*1013904223)|0;
  n=(n^(n>>>13))|0; n=Math.imul(n,1274126177); return ((n^(n>>>16))>>>0)/4294967296;}
const sm=t=>t*t*(3-2*t);
function vnoise(x,z){
  const xi=Math.floor(x), zi=Math.floor(z), xf=x-xi, zf=z-zi;
  const a=hashX(xi,zi),b=hashX(xi+1,zi),c=hashX(xi,zi+1),d=hashX(xi+1,zi+1);
  const u=sm(xf),v=sm(zf);
  return (a+(b-a)*u)+((c+(d-c)*u)-(a+(b-a)*u))*v;
}
function fbm(x,z,o){let s=0,f=1,a=.5;for(let i=0;i<o;i++){s+=vnoise(x*f,z*f)*a;f*=2;a*=.5;}return s;}
function fbm3(x,y,z,o){let s=0,f=1,a=.5;for(let i=0;i<o;i++){s+=vnoise(x*f+i*17,y*f+z*f)*a;f*=2;a*=.5;}return s;}

/* =========================================================
   テクスチャアトlas(16タイル 4x4) を canvas で描く
========================================================= */
function makeAtlas(){
  const T=16, A=document.createElement('canvas'); A.width=T*4; A.height=T*4;
  const g=A.getContext('2d');
  const px=(t,fn)=>{for(let i=0;i<T*T;i++){const x=i%T,y=(i/T)|0; g.fillStyle=fn(x,y,t); g.fillRect(t*4+(x%4),t%4*4+y,1,1);}
    // 4x4 grid position: tile index t → col=t%4,row=(t/4)|0
  };
  const cell=(t,col,row)=>{};
  const paint=(ti,fn)=>{const col=ti%4,row=(ti/4)|0;
    for(let y=0;y<16;y++)for(let x=0;x<16;x++){g.fillStyle=fn(x,y);g.fillRect(col*16+x,row*16+y,1,1);}
  };
  const rnd=(x,y)=>hashX(x+ti*97,y+ti*31); // per tile noise
  const noiseFill=(ti,base,dark,light,dens)=>{
    const col=ti%4,row=(ti/4)|0;
    for(let y=0;y<16;y++)for(let x=0;x<16;x++){
      let r=Math.random();
      let c=base;
      if(r<dens) c=dark; else if(r>1-dens*0.8) c=light;
      g.fillStyle=c; g.fillRect(col*16+x,row*16+y,1,1);
    }
  };
  // 0 grass top
  noiseFill(0,"#6fb35c","#5a9448","#7fc966",.30);
  // 1 grass side
  {const col=1,row=0;for(let y=0;y<16;y++)for(let x=0;x<16;x++){
    let c = y<4 ? (Math.random()<.3?"#5a9448":"#6fb35c") : (Math.random()<.25?"#71533b":"#866043");
    g.fillStyle=c; g.fillRect(col*16+x,row*16+y,1,1);}}
  // 2 dirt
  noiseFill(2,"#866043","#71533b","#977050",.25);
  // 3 stone
  noiseFill(3,"#8b8b8b","#6f6f6f","#a0a0a0",.22);
  // 4 sand
  noiseFill(4,"#dcd4a2","#c9c092","#e9e2b6",.20);
  // 5 log top (rings)
  {const col=1,row=1;for(let y=0;y<16;y++)for(let x=0;x<16;x++){
    const d=Math.hypot(x-7.5,y-7.5); const c = Math.sin(d*1.7)>0 ? "#7c6044":"#5b4531";
    g.fillStyle=c; g.fillRect(col*16+x,row*16+y,1,1);}}
  // 6 log side
  {const col=2,row=1;for(let y=0;y<16;y++)for(let x=0;x<16;x++){
    const c = (x%4===0) ? "#544129" : (Math.random()<.2?"#5b4531":"#6a5138");
    g.fillStyle=c; g.fillRect(col*16+x,row*16+y,1,1);}}
  // 7 planks
  {const col=3,row=1;for(let y=0;y<16;y++)for(let x=0;x<16;x++){
    const band=(y%4===0); const c = band ? "#8a6b3e" : (Math.random()<.15?"#92754a":"#a08050");
    g.fillStyle=c; g.fillRect(col*16+x,row*16+y,1,1);}}
  // 8 leaves (透過)
  {const col=0,row=2;for(let y=0;y<16;y++)for(let x=0;x<16;x++){
    const r=Math.random(); g.fillStyle = r<.55 ? (r<.3?"#357f35":"#3f8f3f") : "rgba(0,0,0,0)";
    g.fillRect(col*16+x,row*16+y,1,1);}}
  // 9 glass
  {const col=1,row=2;for(let y=0;y<16;y++)for(let x=0;x<16;x++){
    let a=0.06; if(x<1||x>14||y<1||y>14) a=.55;
    if((x-y)%6===0 && x>2&&x<13&&y>2&&y<13) a=.20;
    g.fillStyle=`rgba(207,238,240,${a})`; g.fillRect(col*16+x,row*16+y,1,1);}}
  // 10 brick
  {const col=2,row=2;for(let y=0;y<16;y++)for(let x=0;x<16;x++){
    const rowB=(y%4)===0;
    const off=((y/4|0)%2)*8;
    const bX=(x+off)%8;
    const c = rowB ? "#c8c2bd" : (bX===7? "#c8c2bd" : (Math.random()<.2?"#8c4439":"#9a4d42"));
    g.fillStyle=c; g.fillRect(col*16+x,row*16+y,1,1);}}
  // 11 glowstone
  noiseFill(11,"#b78d3f","#8f6b2e","#ffd77f",.42);
  // 12 snow top
  noiseFill(12,"#f3f7f7","#dfe6ea","#ffffff",.12);
  // 13 snow side
  {const col=1,row=3;for(let y=0;y<16;y++)for(let x=0;x<16;x++){
    g.fillStyle = y<4 ? "#f3f7f7" : (Math.random()<.25?"#71533b":"#866043");
    g.fillRect(col*16+x,row*16+y,1,1);}}
  // 14 cobble
  noiseFill(14,"#7d7d7d","#5c5c5c","#9b9b9b",.35);
  // 15 water
  noiseFill(15,"#3c63a8","#2f4f86","#5379bd",.25);

  const tex=new THREE.CanvasTexture(A);
  tex.magFilter=THREE.NearestFilter; tex.minFilter=THREE.NearestFilter;
  tex.generateMipmaps=false;
  return {tex, canvas:A};
}

/* =========================================================
   Three.js セッアップ
========================================================= */
const gl=document.getElementById('gl');
const renderer=new THREE.WebGLRenderer({canvas:gl,antialias:false});
renderer.setPixelRatio(Math.min(2,devicePixelRatio));
const scene=new THREE.Scene();
const camera=new THREE.PerspectiveCamera(75,innerWidth/innerHeight,0.05,200);
camera.rotation.order='YXZ';
scene.add(camera);
scene.fog=new THREE.Fog(0x78a7ff,10,42);
scene.background=new THREE.Color(0x78a7ff);

const atlas=makeAtlas();
const matBlock=new THREE.MeshBasicMaterial({map:atlas.tex,vertexColors:true,alphaTest:0.5,
  transparent:true,side:THREE.DoubleSide,depthWrite:true});
const matWater=new THREE.MeshBasicMaterial({map:atlas.tex,vertexColors:true,transparent:true,
  opacity:0.72,depthWrite:false,side:THREE.DoubleSide});

const chunks=[]; for(let i=0;i<CX*CZ;i++){chunks.push(null);}
const dirty=new Set();

/* 太陽・月・星空 */
function radialTex(c){const cv=document.createElement('canvas');cv.width=cv.height=64;
  const g=cv.getContext('2d');const gr=g.createRadialGradient(32,32,2,32,32,30);
  gr.addColorStop(0,c);gr.addColorStop(1,'rgba(255,255,255,0)');g.fillStyle=gr;g.fillRect(0,0,64,64);
  return new THREE.CanvasTexture(cv);}
const sunSpr=new THREE.Sprite(new THREE.SpriteMaterial({map:radialTex('#fff6cf'),transparent:true,depthWrite:false,fog:false}));
sunSpr.scale.setScalar(26); scene.add(sunSpr);
const moonSpr=new THREE.Sprite(new THREE.SpriteMaterial({map:radialTex('#dfe6ff'),transparent:true,depthWrite:false,fog:false}));
moonSpr.scale.setScalar(17); scene.add(moonSpr);
const starGeo=new THREE.BufferGeometry(); const sp=[];
for(let i=0;i<420;i++){const a=Math.random()*Math.PI*2, b=Math.acos(1-2*Math.random()); const r=160;
  sp.push(r*Math.sin(b)*Math.cos(a), r*Math.cos(b), r*Math.sin(b)*Math.sin(a));}
starGeo.setAttribute('position',new THREE.Float32BufferAttribute(sp,3));
const starMat=new THREE.PointsMaterial({color:0xffffff,size:1.1,transparent:true,opacity:0,fog:false});
scene.add(new THREE.Points(starGeo,starMat));

/* 持つブロック(手) */
const heldGeo=(()=>{
  const pos=[],uv=[];
  for(let f=0;f<6;f++){
    const face=FACES[f], t=tileFor(GLOW? 0:0,0); // placeholder
    // UV は运行时にセット → ジオメトリは面ごとUV属性更新
    for(const c of face.c){pos.push(c[0]-0.5,c[1]-0.5,c[2]-0.5);}
    const ti=tileFor(1,f), col=(ti%4)/4, row=((ti/4)|0)/4;
    uv.push(col,row,col+1/4,row,col+1/4,row+1/4,col,row+1/4);
    pos.push(0); // noop
  }
  return null;
})();
const held=new THREE.Group();
function buildHeld(blockId){
  const g=new THREE.Group();
  const geo=new THREE.BufferGeometry();
  const pos=[],uv=[];
  for(let f=0;f<6;f++){
    const face=FACES[f], ti=tileFor(blockId||GRASS,f);
    const col=(ti%4)/4, row=((ti/4)|0)/4;
    for(const c of face.c){pos.push(c[0]-0.5,c[1]-0.5,c[2]-0.5);}
    uv.push(col,row+1/4, col+1/4,row+1/4, col+1/4,row, col,row);
    geo.addGroup? null:null;
  }
  geo.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));
  geo.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));
  const mesh=new THREE.Mesh(geo,new THREE.MeshBasicMaterial({map:atlas.tex,alphaTest:0.5,transparent:true,side:THREE.DoubleSide}));
  g.add(mesh); g.traverse(m=>m.frustumCulled=false);
  return g;
}
let heldChild=null;
function setHeld(b){
  if(heldChild){held.remove(heldChild);}
  heldChild=buildHeld(b); held.add(heldChild);
  camera.add(held);
  held.position.set(0.42,-0.42,-0.75); held.scale.setScalar(0.45);
  held.rotation.set(0.18,0,0);
}

/* パーティクルプール */
const PART_MAX=260, partGeo=new THREE.BoxGeometry(1,1,1);
const partMat=new THREE.MeshBasicMaterial({vertexColors:false});
const parts=new THREE.InstancedMesh(partGeo,partMat,PART_MAX);
parts.frustumCulled=false; parts.count=0; scene.add(parts);
const pdata=[]; for(let i=0;i<PART_MAX;i++)pdata.push({a:false,x:0,y:0,z:0,vx:0,vy:0,vz:0,l:0});
const tmpM=new THREE.Matrix4(), tmpC=new THREE.Color();
function spawnParticles(x,y,z,b,n){
  const c=PART_COLOR[b]||[1,1,1];
  for(let k=0;k<n;k++){
    const p=pdata.find(p=>!p.a); if(!p)break;
    p.a=true; p.l=1.1; p.x=x+Math.random(); p.y=y+Math.random(); p.z=z+Math.random();
    p.vx=(Math.random()-0.5)*4; p.vy=Math.random()*4+1; p.vz=(Math.random()-0.5)*4;
    tmpC.setRGB(c[0],c[1],c[2]); parts.setColorAt(pdata.indexOf(p),tmpC);
  }
  parts.instanceColor.needsUpdate=true;
}
function updateParticles(dt){
  for(let i=0;i<PART_MAX;i++){
    const p=pdata[i];
    if(p.a){p.l-=dt; if(p.l<=0){p.a=false; tmpM.makeScale(0.0001,0.0001,0.0001); tmpM.setPosition(0,-100,0);}
      else{p.vy-=14*dt; p.x+=p.vx*dt; p.y+=p.vy*dt; p.z+=p.vz*dt;
        tmpM.makeScale(0.13,0.13,0.13); tmpM.setPosition(p.x,p.y,p.z);}
    } else tmpM.makeScale(0.0001,0.0001,0.0001), tmpM.setPosition(0,-100,0);
    parts.setMatrixAt(i,tmpM);
  }
  parts.instanceMatrix.needsUpdate=true;
  parts.count=PART_MAX;
}

/* 雨 */
const RAIN_MAX=420, rainGeo=new THREE.BoxGeometry(0.05,0.5,0.05);
const rainMat=new THREE.MeshBasicMaterial({color:0x9fc3ee,transparent:true,opacity:0.55});
const rain=new THREE.InstancedMesh(rainGeo,rainMat,RAIN_MAX);
rain.frustumCulled=false; scene.add(rain);
const rdata=[]; for(let i=0;i<RAIN_MAX;i++)rdata.push({x:0,y:0,z:0});
let weather=0; // 0晴れ 1曇り 2雨

/* =========================================================
   生成
========================================================= */
function genWorld(seedStr,flat){
  seedNum=0; for(const ch of seedStr) seedNum=(seedNum*31+ch.charCodeAt(0))>>>0;
  rng=mulberry(seedNum);
  blocks=new Uint8Array(N); sky=new Int8Array(N); blkL=new Int8Array(N);
  for(let i=0;i<N;i++)blocks[i]=AIR;
  const hmap=[];
  for(let z=0;z<Z;z++)for(let x=0;x<W;x++){
    let h;
    if(flat){h=12;}
    else{
      const base=8+fbm(x*0.035,z*0.035,4)*22;
      const ridge=fbm(x*0.02+9, z*0.02+3,3);
      h=Math.round(base + ridge*6 - 2);
      h=Math.max(3,Math.min(H-12,h));
    }
    hmap[idx(x,0,z)]=h;
  }
  for(let z=0;z<Z;z++)for(let x=0;x<W;x++){
    const h=hmap[idx(x,0,z)];
    for(let y=0;y<=h;y++){
      let b;
      if(y===0) b=STONE;
      else if(y<h-3) b=STONE;
      else if(y<h) b=DIRT;
      else{ // 表面
        if(h>=24) b=SNOW;
        else if(h<=SEA+1) b=SAND;
        else b=GRASS;
      }
      blocks[idx(x,y,z)]=b;
    }
    for(let y=h+1;y<=SEA;y++) blocks[idx(x,y,z)]=WATER;
    // 洞窟
    if(!flat){
      for(let y=1;y<h-1;y++){
        const n=fbm3(x*0.07,y*0.09,z*0.07,3);
        if(n>0.60) blocks[idx(x,y,z)]=AIR;
      }
    }
  }
  // 木
  for(let z=2;z<Z-2;z++)for(let x=2;x<W-2;x++){
    const h=hmap[idx(x,0,z)];
    if(blocks[idx(x,h,z)]===GRASS && h>SEA+1 && rng()<0.022){
      const th=4+(rng()*3|0);
      for(let y=1;y<=th;y++){
        const yy=h+y; if(yy>=H)break; blocks[idx(x,yy,z)]=LOG;
      }
      const top=h+th;
      for(let dy=-1;dy<=1;dy++)for(let dx=-2;dx<=2;dx++)for(let dz=-2;dz<=2;dz++){
        if(Math.abs(dx)+Math.abs(dz)+Math.abs(dy)>3.4) continue;
        const xx=x+dx,zz=z+dz,yy=top+dy;
        if(xx<0||xx>=W||zz<0||zz>=Z||yy>=H)continue;
        if(blocks[idx(xx,yy,zz)]===AIR) blocks[idx(xx,yy,zz)]=LEAF;
      }
    }
  }
  computeLights();
  for(let c=0;c<CX*CZ;c++)dirty.add(c);
}

/* =========================================================
   照明(スカイライト + ブロックライト) BFS
========================================================= */
const transp=b=>b===AIR||b===WATER||b===GLASS||b===LEAF;
function computeLights(){
  sky.fill(0); blkL.fill(0);
  const q=[];
  // sky: 上から開いている列
  for(let z=0;z<Z;z++)for(let x=0;x<W;x++){
    let L=15;
    for(let y=H-1;y>=0;y--){
      const b=blocks[idx(x,y,z)];
      if(b===AIR){sky[idx(x,y,z)]=L;}
      else if(b===WATER){L=Math.max(0,L-1);sky[idx(x,y,z)]=L;}
      else if(b===GLASS){sky[idx(x,y,z)]=L;}
      else if(b===LEAF){L=Math.max(0,L-2);sky[idx(x,y,z)]=L;}
      else L=0;
    }
  }
  for(let i=0;i<N;i++)if(transp(blocks[i])&&sky[i]>0)q.push(i);
  // BFS sky
  const dirs=[[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]];
  let head=0;
  while(head<q.length){
    const i=q[head++]; const L=sky[i]; if(L<=1)continue;
    const x=i%W, z=(i/W)|0%Z, y=(i/(W*Z))|0;
    for(const[dx,dy,dz]of dirs){
      const xx=x+dx,yy=y+dy,zz=z+dz;
      if(xx<0||xx>=W||yy<0||yy>=H||zz<0||zz>=Z)continue;
      const j=idx(xx,yy,zz); const b=blocks[j];
      if(transp(b)){
        const nL=L-1;
        if(nL>sky[j]){sky[j]=nL; q.push(j);}
      }
    }
  }
  // block light (GLOW)
  q.length=0; head=0;
  for(let i=0;i<N;i++)if(blocks[i]===GLOW){blkL[i]=15;q.push(i);}
  while(head<q.length){
    const i=q[head++]; const L=blkL[i]; if(L<=1)continue;
    const x=i%W, z=(i/W)|0%Z, y=(i/(W*Z))|0;
    for(const[dx,dy,dz]of dirs){
      const xx=x+dx,yy=y+dy,zz=z+dz;
      if(xx<0||xx>=W||yy<0||yy>=H||zz<0||zz>=Z)continue;
      const j=idx(xx,yy,zz); const b=blocks[j];
      if(transp(b)){const nL=L-1; if(nL>blkL[j]){blkL[j]=nL;q.push(j);}}
      else if(b===GLOW && blkL[j]<15){blkL[j]=15;}
    }
  }
}

/* =========================================================
   チャンクメッシュ構築
========================================================= */
function buildChunk(ci){
  const cx=(ci%CX)|0, cz=(ci/CX)|0;
  const x0=cx*CS, z0=cz*CS;
  const pos=[],col=[],uv=[],uvW=[],posW=[],colW=[];
  const T=0.25;
  for(let x=x0;x<x0+CS;x++)for(let z=z0;z<z0+CS;z++)for(let y=0;y<H;y++){
    const b=blocks[idx(x,y,z)];
    if(b===AIR)continue;
    for(let f=0;f<6;f++){
      const[dx,dy,dz]=FACES[f].d;
      const xx=x+dx,yy=y+dy,zz=z+dz;
      const nb=(xx<0||xx>=W||yy<0||yy>=H||zz<0||zz>=Z)?AIR:blocks[idx(xx,yy,zz)];
      if(b===WATER){ if(!(f===2&&nb===AIR))continue; }
      else{
        if(!transp(nb))continue;
        if(b===LEAF&&nb===LEAF)continue;
        if(b===GLASS&&nb===GLASS)continue;
      }
      const L=Math.max(sky[idx(Math.max(0,Math.min(W-1,xx)),Math.max(0,Math.min(H-1,yy)),Math.max(0,Math.min(Z-1,zz)))]||0,
                       blkL[idx(Math.max(0,Math.min(W-1,xx)),Math.max(0,Math.min(H-1,yy)),Math.max(0,Math.min(Z-1,zz)))]||0);
      const shade=FACES[f].s;
      const lf=Math.min(1,(0.18+0.82*(L/15)))*shade;
      const ti=tileFor(b,f);
      const u0=(ti%4)*T, v0=((ti/4)|0)*T;
      const isW=(b===WATER);
      const arrPos=isW?posW:pos, arrCol=isW?colW:col;
      const base=arrPos.length/3;
      for(const c of FACES[f].c){arrPos.push(x+c[0],y+c[1],z+c[2]);}
      const r=lf, g=lf, b2=lf;
      arrCol.push(r,g,b2, r,g,b2, r,g,b2, r,g,b2);
      if(isW) uvW.push(u0,v0+T, u0+T,v0+T, u0+T,v0, u0,v0);
      else    uv.push(u0,v0+T, u0+T,v0+T, u0+T,v0, u0,v0);
    }
  }
  const mk=(p,c,u,mat)=>{
    if(p.length===0)return null;
    const geo=new THREE.BufferGeometry();
    geo.setAttribute('position',new THREE.Float32BufferAttribute(p,3));
    geo.setAttribute('color',new THREE.Float32BufferAttribute(c,3));
    geo.setAttribute('uv',new THREE.Float32BufferAttribute(u,2));
    geo.setIndex([0,1,2,2,3,0, 4,5,6,6,7,4]); // 4頂点→2トライアングル: 0..3 each face? need groups
    // 各面4頂点: n faces。indexは face毎に [0,1,2,2,3,0] をオフセット
    const idxs=[]; const nf=p.length/4;
    for(let i=0;i<nf;i++){const o=i*4; idxs.push(o,o+1,o+2,o+2,o+3,o);}
    geo.setIndex(idxs);
    const mesh=new THREE.Mesh(geo,mat);
    mesh.frustumCulled=false;
    return mesh;
  };
  const old=chunks[ci];
  const newSolid=mk(pos,col,uv,matBlock);
  const newWater=mk(posW,colW,uvW,matWater);
  scene.remove(old);
  const grp=new THREE.Group();
  if(newSolid)grp.add(newSolid);
  if(newWater)grp.add(newWater);
  chunks[ci]=grp;
  scene.add(grp);
}

/* =========================================================
   プレイヤー
========================================================= */
const P={x:0,y:0,z:0,vy:0, yaw:0,pitch:0, fly:false, sneak:false, sprint:false,
  grounded:false, stepAcc:0, bob:0};
function collides(px,py,pz){
  const x0=Math.floor(px-0.3),x1=Math.floor(px+0.3),
        y0=Math.floor(py),y1=Math.floor(py+1.8-0.0001),
        z0=Math.floor(pz-0.3),z1=Math.floor(pz+0.3);
  for(let x=x0;x<=x1;x++)for(let y=y0;y<=y1;y++)for(let z=z0;z<=z1;z++){
    if(x<0||x>=W||z<0||z>=Z)continue; // 壁は外側でclampして後で処理
    const b=blocks[idx(x,y,z)];
    if(solid(b))return true;
    if(y<0)return true;
  }
  return false;
}
function inWaterEye(){
  const x=Math.floor(P.x),z=Math.floor(P.z),y=Math.floor(P.y+1.62);
  return getB(x,y,z)===WATER;
}
function inWaterFeet(){
  const x=Math.floor(P.x),z=Math.floor(P.z),y=Math.floor(P.y+0.9);
  return getB(x,y,z)===WATER;
}

function spawn(){
  const x=W/2, z=Z/2;
  for(let y=H-1;y>=0;y--){
    const b=blocks[idx(x,y,z)];
    if(b===GRASS||b===SNOW||b===SAND){P.x=x+0.5;P.y=y+1;P.z=z+0.5;return;}
  }
  P.x=W/2+0.5;P.y=SEA+1;P.z=Z/2+0.5;
}

/* レイキャスト */
function raycast(max=6){
  const dir=new THREE.Vector3(0,0,-1); camera.getWorldDirection(dir);
  let ox=P.x, oy=P.y+1.62, oz=P.z;
  const dx=dir.x,dy=dir.y,dz=dir.z;
  let x=Math.floor(ox),y=Math.floor(oy),z=Math.floor(oz);
  const sx=Math.sign(dx),sy=Math.sign(dy),sz=Math.sign(dz);
  const tdx=Math.abs(1/dx),tdy=Math.abs(1/dy),tdz=Math.abs(1/dz);
  let tx=dx===0?Infinity:((sx>0?x+1-ox:ox-x)*tdx);
  let ty=dy===0?Infinity:((sy>0?y+1-oy:oy-y)*tdy);
  let tz=dz===0?Infinity:((sz>0?z+1-oz:oz-z)*tdz);
  let last=null, t=0;
  for(let i=0;i<40;i++){
    const b=getB(x,y,z);
    if(b!==AIR&&b!==WATER) return {x,y,z,face:last};
    if(tx<ty&&tx<tz){x+=sx;t=tx;tx+=tdx;last=[-sx,0,0];}
    else if(ty<tz){y+=sy;t=ty;ty+=tdy;last=[0,-sy,0];}
    else{z+=sz;t=tz;tz+=tdz;last=[0,0,-sz];}
    if(t>max)return null;
    if(x<0||x>=W||y<0||y>=H||z<0||z>=Z)return null;
  }
  return null;
}

/* =========================================================
   音声 (WebAudio)
========================================================= */
let AC=null, master, noiseBuf, ambGain, musicGain, rainGain, muted=false, musicOn=true;
function initAudio(){
  if(AC)return;
  AC=new (window.AudioContext||window.webkitAudioContext)();
  master=AC.createGain(); master.gain.value=0.35; master.connect(AC.destination);
  noiseBuf=AC.createBuffer(1,AC.sampleRate*1.2,AC.sampleRate);
  const d=noiseBuf.getChannelData(0);
  for(let i=0;i<d.length;i++)d[i]=Math.random()*2-1;
  // ambient wind
  const src=AC.createBufferSource(); src.buffer=noiseBuf; src.loop=true;
  const lp=AC.createBiquadFilter(); lp.type='lowpass'; lp.frequency.value=380;
  ambGain=AC.createGain(); ambGain.gain.value=0.10;
  src.connect(lp); lp.connect(ambGain); ambGain.connect(master); src.start();
  const lfo=AC.createOscillator(); lfo.frequency.value=0.13; const lg=AC.createGain(); lg.gain.value=0.06;
  lfo.connect(lg); lg.connect(ambGain.gain); lfo.start();
  // music pad
  musicGain=AC.createGain(); musicGain.gain.value=0.12; musicGain.connect(master);
  const chord=[[220,277,330],[196,247,294],[174,220,262],[261,330,392]];
  let ci=0;
  chord[0].forEach(f=>{const o=AC.createOscillator();o.type='sine';o.frequency.value=f;
    const g=AC.createGain();g.gain.value=0.06;o.connect(g);g.connect(musicGain);o.start();});
  setInterval(()=>{
    if(!musicOn)return;
    ci=(ci+1)%chord.length;
    musicGain.gain.setTargetAtTime(0.001,AC.currentTime,0.25);
    chord[ci].forEach(f=>{const o=AC.createOscillator();o.type='triangle';o.frequency.value=f;
      const g=AC.createGain();g.gain.value=0.0;g.connect(musicGain);o.start();
      g.gain.setTargetAtTime(0.08,AC.currentTime+0.3,0.4);
      g.gain.setTargetAtTime(0,AC.currentTime+6,1.2);
      o.stop(AC.currentTime+7);});
  },8000);
  // rain
  const rsrc=AC.createBufferSource(); rsrc.buffer=noiseBuf; rsrc.loop=true;
  const rbp=AC.createBiquadFilter(); rbp.type='bandpass'; rbp.frequency.value=1400; rbp.Q.value=0.5;
  rainGain=AC.createGain(); rainGain.gain.value=0;
  rsrc.connect(rbp); rbp.connect(rainGain); rainGain.connect(master); rsrc.start();
}
function blip(freq,type,vol,dur,curve='decay'){
  if(!AC)return;
  const o=AC.createOscillator();o.type=type;o.frequency.value=freq;
  const g=AC.createGain();g.gain.value=vol;
  o.connect(g);g.connect(master);
  if(curve==='decay')g.gain.exponentialRampToValueAtTime(0.001,AC.currentTime+dur);
  o.start();o.stop(AC.currentTime+dur);
}
function noiseBurst(vol,dur,freq,q){
  if(!AC)return;
  const s=AC.createBufferSource();s.buffer=noiseBuf;s.playbackRate.value=1.3;
  const f=AC.createBiquadFilter();f.type='bandpass';f.frequency.value=freq;f.Q.value=q||1;
  const g=AC.createGain();g.gain.value=vol;
  g.gain.exponentialRampToValueAtTime(0.001,AC.currentTime+dur);
  s.connect(f);f.connect(g);g.connect(master);
  s.start();s.stop(AC.currentTime+dur);
}
const STEP_FREQ={1:320,2:260,3:190,4:400,5:220,6:240,7:300,8:420,9:300,10:420,12:240,13:200};
function stepSound(){
  const b=getB(Math.floor(P.x),Math.floor(P.y-0.2),Math.floor(P.z));
  noiseBurst(0.10,0.13,STEP_FREQ[b]||260,1.2);
}
function digSound(b){ noiseBurst(0.16,0.16,STEP_FREQ[b]||260,0.8); blip(90,'square',0.12,0.12);}
function placeSound(b){ blip(140,'square',0.14,0.09); noiseBurst(0.06,0.08,300,1);}

/* =========================================================
   UI: ホットバー・時計・ミニマップ
========================================================= */
const hotbar=document.getElementById('hotbar');
const slotCanvases=[];
let activeSlot=0;
function drawIcon(cv,id){
  const g=cv.getContext('2d');
  const T=atlas.canvas, tTop=tileFor(id,2), tSide=tileFor(id,1);
  g.clearRect(0,0,40,40); g.imageSmoothingEnabled=false;
  if(id===0){ // 消去ツール(つるはし風)
    g.strokeStyle='#cfd6e2'; g.lineWidth=3;
    g.beginPath();g.moveTo(8,32);g.lineTo(26,12);g.stroke();
    g.strokeStyle='#ffd23f';g.lineWidth=4;
    g.beginPath();g.arc(27,11,8,Math.PI*0.15,Math.PI*0.9);g.stroke();
    return;
  }
  // front face
  g.drawImage(T,(tSide%4)*16,((tSide/4)|0)*16,16,16, 6,20,28,28);
  // top face (平行四辺形 = 斜め描画を簡易に)
  g.save(); g.beginPath(); g.moveTo(6,20); g.lineTo(14,6); g.lineTo(42,6); g.lineTo(34,20); g.closePath(); g.clip();
  g.translate(6,20); g.transform(1,0, -0.6667, 0.5, 0,0); g.scale(1.33,1.33);
  g.drawImage(T,(tTop%4)*16,((tTop/4)|0)*16,16,16, 0,0,22,16);
  g.restore();
}
function buildHotbar(){
  hotbar.innerHTML='';
  SLOTS.forEach((id,i)=>{
    const d=document.createElement('div'); d.className='slot'+(i===activeSlot?' act':'');
    const num=document.createElement('div'); num.className='num'; num.textContent=((i+1)%10);
    const cv=document.createElement('canvas'); cv.width=34;cv.height=34;
    drawIcon(cv,id);
    d.appendChild(cv); d.appendChild(num);
    d.onclick=()=>{setSlot(i);};
    hotbar.appendChild(d); slotCanvases.push(cv);
  });
  document.getElementById('slotName').textContent=NAMES[SLOTS[activeSlot]];
  setHeld(SLOTS[activeSlot]||GRASS);
}
function setSlot(i){
  activeSlot=(i+10)%10;
  [...hotbar.children].forEach((d,k)=>d.classList.toggle('act',k===activeSlot));
  document.getElementById('slotName').textContent=NAMES[SLOTS[activeSlot]];
  setHeld(SLOTS[activeSlot]||GRASS);
  blip(700,'square',0.06,0.05);
}

/* 時計 */
const clockCv=document.getElementById('clockCv');
function drawClock(t){ // t 0..1 (0=0:00)
  const g=clockCv.getContext('2d'); g.clearRect(0,0,96,48);
  g.fillStyle='#0b1026'; g.fillRect(0,0,96,48);
  g.fillStyle='#1b212b'; g.fillRect(6,6,84,36);
  g.strokeStyle='#3a4453'; g.strokeRect(6,6,84,36);
  // 太陽/月の位置
  const ang=(t-0.25)*Math.PI*2; // 0.25=6時 sunrise
  const sx=48+Math.cos(ang)*36, sy=24-Math.sin(ang)*14;
  const dayF=Math.max(0,Math.sin((t-0.25)*Math.PI*2));
  g.fillStyle= dayF>0.05?'#ffd23f':'#dfe6ff';
  g.beginPath();g.arc(sx,Math.max(8,sy),4,0,7);g.fill();
  const mx=48-Math.cos(ang)*36, my=24+Math.sin(ang)*14;
  g.fillStyle='#aab4c6'; g.beginPath();g.arc(mx,Math.max(8,my),3,0,7);g.fill();
  g.fillStyle='#9fb0c8'; g.font='10px DotGothic16'; g.textAlign='center';
  const hh=Math.floor(t*24), mm=Math.floor((t*24-hh)*60);
  g.fillText(`${String(hh).padStart(2,'0')}:${String(mm).padStart(2,'0')}`,48,44);
}

/* ミニマップ */
const mapCv=document.getElementById('map'), mg=mapCv.getContext('2d');
function drawMap(){
  mg.fillStyle='#0b1026';mg.fillRect(0,0,96,96);
  for(let z=0;z<Z;z++)for(let x=0;x<W;x++){
    let y=H-1,b=AIR;
    while(y>=0){b=blocks[idx(x,y,z)]; if(b!==AIR&&b!==WATER)break; y--;}
    if(b===AIR)continue;
    mg.fillStyle=MINIMAP[b]||'#555';
    mg.fillRect(x*1.5,z*1.5,1.5,1.5);
  }
  // プレイヤー矢印
  mg.save(); mg.translate(P.x*1.5,P.z*1.5); mg.rotate(-P.yaw);
  mg.fillStyle='#fff'; mg.beginPath();
  mg.moveTo(0,-5);mg.lineTo(3,4);mg.lineTo(-3,4);mg.closePath();mg.fill();
  mg.restore();
}

/* トースト */
let toastTimer=null;
function toast(txt){
  const t=document.getElementById('toast');
  t.textContent=txt; t.style.opacity=1;
