マイクラ風 3D 箱庭を、単一 HTML で自作 WebGL2 ボクセルレンダラーとして組みました。Three.js は使わず、チャンクメッシュ・AO・日-cycle・天空シェーダー・粒子まで全部自前です。

```html
<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>VOXEL GARDEN — 箱庭ヴォクセル</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DotGothic16&family=Zen+Kaku+Gothic+New:wght@400;500;700&display=swap" rel="stylesheet">
<style>
:root{
  --ink:#f4ece0; --dim:#a2937f; --panel:#2b241e; --panel2:#171310;
  --line:#3e342b; --amber:#f5b758; --grass:#79c76f; --rose:#e2735c; --steel:#8fb4c9;
  --disp:'DotGothic16',monospace; --body:'Zen Kaku Gothic New','Hiragino Sans',sans-serif;
}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;background:#120f10;color:var(--ink);font-family:var(--body);overflow:hidden}
#gl{position:fixed;inset:0;display:block}
#grain{position:fixed;inset:0;pointer-events:none;z-index:2;
  background:
    radial-gradient(ellipse at 50% 45%,transparent 42%,rgba(8,6,5,.55) 100%),
    repeating-linear-gradient(0deg,rgba(255,255,255,.022) 0 1px,transparent 1px 3px);
  mix-blend-mode:soft-light}
#under{position:fixed;inset:0;pointer-events:none;z-index:2;opacity:0;transition:opacity .35s;
  background:linear-gradient(rgba(38,96,120,.45),rgba(22,64,88,.6));mix-blend-mode:screen}
#vig{position:fixed;inset:0;pointer-events:none;z-index:3;opacity:0;transition:opacity .2s;
  background:radial-gradient(circle at 50% 50%,transparent 55%,rgba(241,182,90,.22))}

/* ---- HUD ---- */
#hud{position:fixed;inset:0;z-index:4;pointer-events:none;opacity:0;transition:opacity .5s}
#hud.on{opacity:1}
.panel{background:linear-gradient(#2e2720,#191512);border:2px solid var(--line);
  box-shadow:inset 0 1px 0 #4d423a,inset 0 -2px 0 #0d0b09,0 10px 26px rgba(0,0,0,.5);
  padding:10px 12px;pointer-events:auto}
.tag{font-family:var(--disp);font-size:11px;letter-spacing:.16em;color:var(--amber);
  display:flex;align-items:center;gap:6px;margin-bottom:6px}
.tag i{width:9px;height:9px;background:var(--amber);box-shadow:0 0 8px rgba(245,183,88,.6)}
.row{font-family:var(--disp);font-size:12px;display:flex;justify-content:space-between;gap:14px;
  color:var(--ink);padding:2px 0;border-bottom:1px dashed #352b22}
.row:last-child{border-bottom:0}
.row b{font-weight:400;color:var(--dim)}
#dbg{position:fixed;top:14px;left:14px;width:236px}
#clock{position:fixed;top:14px;right:14px;display:flex;gap:12px;align-items:center}
#clock svg{display:block}
#mode{position:fixed;top:96px;right:14px;font-family:var(--disp);font-size:11px;letter-spacing:.12em;
  color:var(--grass);border:2px solid #3a4b39;background:rgba(24,34,24,.72);padding:6px 10px;pointer-events:auto}
#mode.fly{color:var(--amber);border-color:#4c3d26}
#mode.hide{display:none}

#legend{position:fixed;left:14px;bottom:14px;display:flex;flex-wrap:wrap;gap:6px;max-width:340px}
.chip{font-family:var(--disp);font-size:11px;letter-spacing:.08em;color:var(--ink);
  border:2px solid #3b3229;background:rgba(23,19,16,.7);padding:5px 8px;pointer-events:auto}
.chip k{color:var(--amber)}

#bar{position:fixed;left:50%;bottom:16px;transform:translateX(-50%);display:flex;gap:8px;
  padding:8px;background:rgba(18,15,12,.7);border:2px solid var(--line);pointer-events:auto}
.slot{position:relative;width:50px;height:50px;border:2px solid #463a30;background:#201b16;
  transition:transform .16s cubic-bezier(.2,.9,.2,1),border-color .16s,box-shadow .16s}
.slot canvas{position:absolute;inset:3px;width:44px;height:44px}
.slot .num{position:absolute;top:-1px;left:2px;font-family:var(--disp);font-size:10px;color:#7f6f5d}
.slot:hover{transform:translateY(-5px);border-color:#6a594b}
.slot.sel{border-color:var(--amber);box-shadow:0 0 0 2px rgba(245,183,88,.25),0 8px 18px rgba(0,0,0,.5);transform:translateY(-6px)}
.slot.sel::after{content:'';position:absolute;left:0;right:0;bottom:-3px;height:3px;background:var(--amber)}
.slot.pop{animation:pop .22s ease-out}
@keyframes pop{0%{transform:translateY(-6px) scale(1.12)}100%{transform:translateY(-6px) scale(1)}}

#cross{position:fixed;left:50%;top:50%;width:22px;height:22px;transform:translate(-50%,-50%);z-index:5;pointer-events:none}
#cross::before,#cross::after{content:'';position:absolute;background:rgba(244,236,224,.82);
  box-shadow:0 0 6px rgba(0,0,0,.6)}
#cross::before{left:10px;top:2px;width:2px;height:18px}
#cross::after{left:2px;top:10px;width:18px;height:2px}
#cross.hit{filter:drop-shadow(0 0 6px var(--amber))}
#cross.pulse{animation:pulse .22s ease-out}
@keyframes pulse{0%{transform:translate(-50%,-50%) scale(1)}40%{transform:translate(-50%,-50%) scale(1.55)}100%{transform:translate(-50%,-50%) scale(1)}}

#toast{position:fixed;left:50%;top:calc(50% + 34px);transform:translateX(-50%);z-index:5;
  font-family:var(--disp);font-size:13px;letter-spacing:.1em;opacity:0;pointer-events:none}
#toast.show{animation:rise .95s ease-out}
@keyframes rise{0%{opacity:0;transform:translateX(-50%) translateY(6px)}20%{opacity:1;transform:translateX(-50%) translateY(0)}100%{opacity:0;transform:translateX(-50%) translateY(-14px)}}

#sndBtn{position:fixed;right:14px;bottom:14px;font-family:var(--disp);font-size:11px;letter-spacing:.1em;
  border:2px solid #3b3229;background:rgba(23,19,16,.75);padding:7px 10px;color:var(--ink);
  cursor:pointer;pointer-events:auto;transition:.15s}
#sndBtn:hover{border-color:var(--amber);color:var(--amber)}

/* ---- overlays ---- */
.ov{position:fixed;inset:0;z-index:8;display:none}
.ov.on{display:block}
#title{background:linear-gradient(180deg,rgba(14,11,10,.86),rgba(14,11,10,.92));overflow:auto}
#title .wrap{min-height:100%;display:grid;grid-template-columns:1.05fr .9fr;gap:34px;padding:clamp(20px,4vw,46px);align-content:center}
.logo{font-family:var(--disp);line-height:.92;letter-spacing:.02em}
.logo .l1{font-size:clamp(34px,6vw,78px);color:var(--ink);text-shadow:4px 4px 0 #241d16,8px 8px 0 #0f0b09}
.logo .l2{font-size:clamp(12px,1.4vw,17px);color:var(--amber);letter-spacing:.3em;margin-top:12px}
.logo .l3{font-size:13px;color:var(--dim);margin-top:14px;line-height:1.75;max-width:46ch}
.blockart{display:flex;gap:6px;margin-top:20px;flex-wrap:wrap}
.blockart span{font-family:var(--disp);font-size:11px;letter-spacing:.1em;color:var(--ink);
  border:2px solid #463a30;background:#201b16;padding:6px 9px}
#gen{margin-top:22px;display:flex;flex-direction:column;gap:12px}
#gen .field{display:flex;gap:8px;align-items:center}
#seed{font-family:var(--disp);font-size:13px;background:#181411;border:2px solid #463a30;color:var(--ink);
  padding:9px 12px;width:180px}
#seed:focus{border-color:var(--amber);outline:none}
.btn{font-family:var(--disp);font-size:14px;letter-spacing:.14em;border:2px solid var(--amber);
  background:#3a2a18;color:var(--amber);padding:11px 18px;cursor:pointer;transition:.15s}
.btn:hover{background:var(--amber);color:#1b1410}
.btn:disabled{opacity:.5;cursor:not-allowed}
.btn.ghost{border-color:#4a3f36;background:#231d18;color:var(--ink)}
.btn.ghost:hover{border-color:var(--grass);color:var(--grass)}
#prog{height:10px;border:2px solid #463a30;background:#16120f;position:relative}
#prog i{position:absolute;left:0;top:0;bottom:0;width:0;background:var(--amber);transition:width .2s}
#prog span{font-family:var(--disp);font-size:11px;color:var(--dim);display:block;margin-top:6px}
.keys{border-left:2px solid #3a312a;padding-left:14px}
.keys h4{font-family:var(--disp);font-size:12px;letter-spacing:.16em;color:var(--amber);margin-bottom:12px}
.keys dl{display:grid;grid-template-columns:auto 1fr;gap:6px 10px;font-size:12.5px;line-height:1.6}
.keys dt{font-family:var(--disp);font-size:11px;color:var(--amber);letter-spacing:.08em}
.keys dd{color:var(--ink)}

#pause,#inv{background:rgba(12,10,9,.82);display:grid;place-items:center}
.card{width:min(560px,92vw);background:linear-gradient(#2d2620,#1a1613);border:2px solid var(--line);
  box-shadow:inset 0 1px 0 #4d423a,0 18px 40px rgba(0,0,0,.6);padding:22px}
.card h3{font-family:var(--disp);font-size:22px;letter-spacing:.1em;margin-bottom:14px}
.card .acts{display:flex;gap:10px;flex-wrap:wrap;margin-top:16px}
.settings{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:14px}
.set{font-family:var(--disp);font-size:11px;letter-spacing:.1em;color:var(--dim)}
.set input{width:100%;accent-color:var(--amber)}
.set .v{color:var(--ink)}
#inv .grid{display:grid;grid-template-columns:repeat(6,1fr);gap:10px;margin-top:14px}
#inv .cell{border:2px solid #463a30;background:#201b16;padding:8px;cursor:pointer;transition:.14s;text-align:center}
#inv .cell:hover{border-color:var(--amber);transform:translateY(-4px)}
#inv .cell canvas{width:44px;height:44px}
#inv .cell em{font-style:normal;font-family:var(--disp);font-size:11px;color:var(--ink);display:block;margin-top:4px}
#inv .hint{font-size:12px;color:var(--dim);margin-top:12px}
@media(max-width:900px){#title .wrap{grid-template-columns:1fr}.keys{border-left:0;border-top:2px solid #3a312a;padding:14px 0 0}#dbg{width:196px}}
</style>
</head>
<body>
<canvas id="gl"></canvas>
<div id="grain"></div><div id="under"></div><div id="vig"></div>
<div id="cross"></div>
<div id="toast"></div>

<div id="hud">
  <div id="dbg" class="panel">
    <div class="tag"><i></i>DEBUG</div>
    <div class="row"><span>XYZ</span><span id="dxyz">0 / 0 / 0</span></div>
    <div class="row"><span>足元</span><span id="dblock">-</span></div>
    <div class="row"><span>チャンク</span><span id="dchunk">0 / 25</span></div>
    <div class="row"><span>面数</span><span id="dface">0</span></div>
    <div class="row"><span>FPS</span><span id="dfps">0</span></div>
    <div class="row"><span>SEED</span><span id="dseed">-</span></div>
  </div>
  <div id="clock" class="panel">
    <svg width="66" height="66" viewBox="0 0 66 66">
      <circle cx="33" cy="33" r="24" fill="none" stroke="#3e342b" stroke-width="2"/>
      <path id="arcD" d="" stroke="#f5b758" stroke-width="3" fill="none"/>
      <path id="arcN" d="" stroke="#4c6b86" stroke-width="3" fill="none"/>
      <circle id="sunM" cx="33" cy="9" r="5" fill="#f7c877"/>
      <circle id="moonM" cx="33" cy="57" r="4" fill="#cbd6e2"/>
      <circle cx="33" cy="33" r="1.6" fill="#8a7a66"/>
    </svg>
    <div>
      <div class="tag"><i></i>TIME</div>
      <div class="row"><span id="dtime">06:00</span><span id="dday">DAY 1</span></div>
    </div>
  </div>
  <div id="mode" class="hide">地上</div>
  <div id="legend">
    <div class="chip"><k>WASD</k> 移動</div>
    <div class="chip"><k>Space</k> ジャンプ</div>
    <div class="chip"><k>Shift</k> 走る</div>
    <div class="chip"><k>Ctrl</k> スニーク</div>
    <div class="chip"><k>F</k> 飛行</div>
    <div class="chip"><k>1-9</k> / <k>ホイール</k> ブロック</div>
    <div class="chip"><k>左クリック</k> 破壊</div>
    <div class="chip"><k>右クリック</k> 設置</div>
    <div class="chip"><k>中クリック</k> 採取</div>
    <div class="chip"><k>E</k> インベントリ</div>
    <div class="chip"><k>T</k> 時刻送り</div>
    <div class="chip"><k>Esc</k> メニュー</div>
  </div>
  <div id="bar"></div>
  <button id="sndBtn">音: ON</button>
</div>

<div id="title" class="ov on">
  <div class="wrap">
    <div>
      <div class="logo">
        <div class="l1">VOXEL<br>GARDEN</div>
        <div class="l2">箱庭ヴォクセル / 自作 WebGL2 レンダラー</div>
        <div class="l3">チャンク単位でメッシュを生成し、周辺ブロックから環境閉塞(AO)を計算。日-cycle・雲・星・水面の揺れ・破壊粒子・ホタルまで、すべてシェーダーと JS で自前生成しています。</div>
        <div class="blockart"><span>25 CHUNKS</span><span>AO LIGHTING</span><span>DAY / NIGHT</span><span>CREATIVE</span></div>
      </div>
      <div id="gen">
        <div class="field">
          <label style="font-family:var(--disp);font-size:11px;letter-spacing:.14em;color:var(--dim)">SEED</label>
          <input id="seed" value="7714202755">
          <button class="btn ghost" id="reroll">再抽選</button>
          <button class="btn" id="go">世界を生成</button>
        </div>
        <div id="prog"><i></i></div>
        <span id="progTxt">待機中 …</span>
      </div>
    </div>
    <div class="keys">
      <h4>CONTROLS</h4>
      <dl>
        <dt>WASD</dt><dd>移動（マウスで視点）</dd>
        <dt>Space</dt><dd>ジャンプ / 水中で上昇 / 飛行で上昇</dd>
        <dt>Shift</dt><dd>走る / 飛行で加速</dd>
        <dt>Ctrl</dt><dd>スニーク（低姿勢）</dd>
        <dt>F</dt><dd>飛行モード切替</dd>
        <dt>1–9</dt><dd>ホットバー選択、ホイールでも切替</dd>
        <dt>左クリック</dt><dd>ブロック破壊（粒子が散ります）</dd>
        <dt>右クリック</dt><dd>ブロック設置</dd>
        <dt>中クリック</dt><dd>対象ブロックをスロットに採取</dd>
        <dt>E</dt><dd>全ブロックインベントリ</dd>
        <dt>T</dt><dd>時刻を早送り</dd>
        <dt>Esc</dt><dd>メニュー・感度/霧/日長/音の調整</dd>
      </dl>
      <p class="hint" style="margin-top:14px">デスクトップ向け（マウス + キーボード）です。</p>
    </div>
  </div>
</div>

<div id="pause" class="ov">
  <div class="card">
    <h3>メニュー</h3>
    <div class="settings">
      <div class="set">マウス感度 <span class="v" id="s1v">1.0</span><input id="s1" type="range" min="0.2" max="2.6" step="0.1" value="1"></div>
      <div class="set">霧の距離 <span class="v" id="s2v">70</span><input id="s2" type="range" min="30" max="120" step="5" value="70"></div>
      <div class="set">1日の長さ <span class="v" id="s3v">120s</span><input id="s3" type="range" min="20" max="420" step="10" value="120"></div>
      <div class="set">FOV <span class="v" id="s4v">70</span><input id="s4" type="range" min="55" max="100" step="1" value="70"></div>
    </div>
    <div class="acts">
      <button class="btn" id="resume">世界に戻る</button>
      <button class="btn ghost" id="newworld">別の世界</button>
      <button class="btn ghost" id="flybtn">飛行 ON</button>
    </div>
  </div>
</div>

<div id="inv" class="ov">
  <div class="card">
    <h3>インベントリ</h3>
    <p class="hint">クリックで、選択中のホットバー Slot に割り当てます。</p>
    <div class="grid" id="invGrid"></div>
    <div class="acts"><button class="btn ghost" id="closeInv">閉じる (E)</button></div>
  </div>
</div>

<script>
"use strict";
/* ============================================================
   0. ユーティリティ
============================================================ */
const clamp=(v,a,b)=>v<a?a:v>b?b:v;
function mulberry32(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)&0x255)/256}}
function hash3(x,y,z){let n=(x*1973+ y*2641 + z*5717)&0xffffffff; n=(n^(n>>15))*0x45d9f5b|0; n=(n^(n>>13))*0x45d9f5b|0; return ((n^(n>>15))&0xfffff)/0xfffff;}
function hash2(x,y){let n=(x*374761393+y*668265263)&0xffffffff;n=(n^(n>>13))*0x45d9f5b|0;return ((n^(n>>15))&0xffffff)/0xffffff;}

/* ============================================================
   1. ブロック定義 + テクスチャアトラス生成
============================================================ */
const TS=16, ACOLS=8, AROWS=4;
const AIR=0,BEDROCK=1,GRASS=2,DIRT=3,STONE=4,COBBLE=5,SAND=6,SNOW=7,LOG=8,LEAF=9,PLANK=10,BRICK=11,GLASS=12,GLOW=13,WATER=14;
const TILE={grass_top:0,grass_side:1,dirt:2,stone:3,cobble:4,sand:5,snow:6,log_top:7,log_side:8,leaf:9,plank:10,brick:11,glass:12,glow:13,water:14,bedrock:15};
const DEFS={};
function def(id,jp,en,tiles,opt={}){DEFS[id]={id,jp,en,tiles,...opt};}
def(BEDROCK,'基盤岩','Bedrock',[TILE.bedrock,TILE.bedrock,TILE.bedrock],{unbreak:true});
def(GRASS,'草ブロック','Grass',[TILE.grass_top,TILE.grass_side,TILE.dirt]);
def(DIRT,'土','Dirt',[TILE.dirt,TILE.dirt,TILE.dirt]);
def(STONE,'石','Stone',[TILE.stone,TILE.stone,TILE.stone]);
def(COBBLE,'丸石','Cobblestone',[TILE.cobble,TILE.cobble,TILE.cobble]);
def(SAND,'砂','Sand',[TILE.sand,TILE.sand,TILE.sand]);
def(SNOW,'雪ブロック','Snow',[TILE.snow,TILE.snow,TILE.snow]);
def(LOG,'オークの原木','Oak Log',[TILE.log_top,TILE.log_side,TILE.log_side]);
def(LEAF,'オークの葉','Oak Leaves',[TILE.leaf,TILE.leaf,TILE.leaf]);
def(PLANK,'オークの木材','Planks',[TILE.plank,TILE.plank,TILE.plank]);
def(BRICK,'レンガ','Bricks',[TILE.brick,TILE.brick,TILE.brick]);
def(GLASS,'ガラス','Glass',[TILE.glass,TILE.glass,TILE.glass],{alphaTest:true});
def(GLOW,'グロウストーン','Glowstone',[TILE.glow,TILE.glow,TILE.glow],{glow:true});
def(WATER,'水','Water',[TILE.water,TILE.water,TILE.water],{blend:true,noSolid:true});
const LIST=[GRASS,DIRT,STONE,COBBLE,SAND,SNOW,LOG,LEAF,PLANK,BRICK,GLASS,GLOW,WATER];

function genAtlas(){
  const cv=document.createElement('canvas');cv.width=ACOLS*TS;cv.height=AROWS*TS;
  const c=cv.getContext('2d');c.imageSmoothingEnabled=false;
  const R=mulberry32(91762);
  const px=(ox,x,y,col)=>{c.fillStyle=col;c.fillRect(ox+x,oy0+y,1,1)};
  let oy0=0;
  function tile(t,fn){const col=t%ACOLS,row=(t/ACOLS)|0;const ox=col*TS;oy0=row*TS;fn(ox,oy0);}
  const speck=(ox,oy,palette,n)=>{for(let i=0;i<n;i++){const x=(R()*TS)|0,y=(R()*TS)|0;c.fillStyle=palette[(R()*palette.length)|0];c.fillRect(ox+x,oy+y,1,1)}};
  const fill=(ox,oy,col)=>{c.fillStyle=col;c.fillRect(ox,oy,TS,TS)};

  tile(TILE.grass_top,(ox,oy)=>{fill(ox,oy,'#6b9d52');speck(ox,oy,['#7fae63','#5c884a','#84b96c','#628f4d'],140)});
  tile(TILE.grass_side,(ox,oy)=>{fill(ox,oy,'#8a6242');speck(ox,oy,['#96715a','#7b563a','#8f6b4c'],90);
    for(let x=0;x<TS;x++){const h=3+((R()*3)|0);for(let y=0;y<h;y++){c.fillStyle=y===h-1?'#557a3f':'#6b9d52';c.fillRect(ox+x,oy+y,1,1)}}});
  tile(TILE.dirt,(ox,oy)=>{fill(ox,oy,'#8a6242');speck(ox,oy,['#96715a','#7b563a','#6f4b33','#9a7a60'],130)});
  tile(TILE.stone,(ox,oy)=>{fill(ox,oy,'#87878d');speck(ox,oy,['#94949b','#77777e','#6d6d74','#9d9da3'],140);
    for(let i=0;i<5;i++){c.fillStyle='#63636a';const x=(R()*12)|0,y=(R()*12)|0;c.fillRect(ox+x,oy+y,3,2)}});
  tile(TILE.cobble,(ox,oy)=>{fill(ox,oy,'#7d7d84');
    for(let i=0;i<12;i++){const x=(R()*13)|0,y=(R()*13)|0,s=2+((R()*3)|0);
      c.fillStyle=['#99999f','#6a6a71','#86868d'][(R()*3)|0];c.fillRect(ox+x,oy+y,s,s);
      c.fillStyle='#4f4f56';c.fillRect(ox+x,oy+y+s,1,1)}});
  tile(TILE.sand,(ox,oy)=>{fill(ox,oy,'#ded0a3');speck(ox,oy,['#e9dcb4','#cbbb90','#e4d5a8'],120)});
  tile(TILE.snow,(ox,oy)=>{fill(ox,oy,'#eef3f5');speck(ox,oy,['#ffffff','#dfe6ea','#e6eef1'],70)});
  tile(TILE.log_top,(ox,oy)=>{fill(ox,oy,'#a98356');
    for(let x=0;x<TS;x++)for(let y=0;y<TS;y++){const d=Math.hypot(x-8,y-8);
      c.fillStyle=(Math.floor(d)%2)?'#8d6a42':'#b89263';c.fillRect(ox+x,oy+y,1,1)}
    c.fillStyle='#6f5233';c.fillRect(ox+7,oy+7,2,2)});
  tile(TILE.log_side,(ox,oy)=>{fill(ox,oy,'#8d6a42');
    for(let x=0;x<TS;x++){c.fillStyle=(x%3===0)?'#6f5233':'#9b7549';for(let y=0;y<TS;y++)if(R()>.18)c.fillRect(ox+x,oy+y,1,1)}
    c.fillStyle='#5e452b';c.fillRect(ox+2,oy,1,TS);c.fillRect(ox+11,oy,1,TS)});
  tile(TILE.leaf,(ox,oy)=>{for(let x=0;x<TS;x++)for(let y=0;y<TS;y++){
    if(R()<.22){c.clearRect(ox+x,oy+y,1,1);continue}
    c.fillStyle=['#3f7b38','#4c8f42','#356b2f','#57a04a'][(R()*4)|0];c.fillRect(ox+x,oy+y,1,1)}});
  tile(TILE.plank,(ox,oy)=>{fill(ox,oy,'#b89164');
    for(let y=0;y<TS;y++){for(let x=0;x<TS;x++)if(R()>.6){c.fillStyle=R()>.5?'#c79e71':'#9f7a53';c.fillRect(ox+x,oy+y,1,1)}}
    c.fillStyle='#8a6b47';c.fillRect(ox,oy+4,TS,1);c.fillRect(ox,oy+11,TS,1);c.fillRect(ox+7,oy,1,4);c.fillRect(ox+3,oy+5,1,6)});
  tile(TILE.brick,(ox,oy)=>{fill(ox,oy,'#a4593f');
    for(let y=0;y<TS;y++){for(let x=0;x<TS;x++)if(R()>.55){c.fillStyle=R()>.5?'#b4664a':'#8f4c36';c.fillRect(ox+x,oy+y,1,1)}}
    c.fillStyle='#c8c0b4';for(let y=2;y<TS;y+=5)c.fillRect(ox,oy+y,TS,1);
    for(let r=0;r<3;r++)for(let k=0;k<4;k++)c.fillRect(ox+((k*4+r*2)%TS),oy+r*5+1,1,4)});
  tile(TILE.glass,(ox,oy)=>{c.clearRect(ox,oy,TS,TS);
    c.fillStyle='rgba(214,232,242,.85)';for(let i=0;i<TS;i++){c.fillRect(ox+i,oy,1,1);c.fillRect(ox+i,oy+TS-1,1,1);c.fillRect(ox,oy+i,1,1);c.fillRect(ox+TS-1,oy+i,1,1)}
    c.fillStyle='rgba(240,250,255,.5)';c.fillRect(ox+3,oy+9,4,1);c.fillRect(ox+4,oy+8,4,1);c.fillRect(ox+5,oy+7,4,1);
    c.fillStyle='rgba(150,190,210,.45)';c.fillRect(ox+2,oy+2,12,12)});
  tile(TILE.glow,(ox,oy)=>{fill(ox,oy,'#d99a3f');speck(ox,oy,['#f5c76a','#c27f31','#ffe0a0'],90);
    for(let i=0;i<5;i++){c.fillStyle='#fff0c0';c.fillRect(ox+((R()*12)|0),oy+((R()*12)|0),2,2)}});
  tile(TILE.water,(ox,oy)=>{fill(ox,oy,'#3d6fa3');
    for(let y=0;y<TS;y++){const w=Math.sin(y*0.7)*2;for(let x=0;x<TS;x++){
      c.fillStyle=(x+Math.round(w))%5===0?'#4f82b8':(y%4===0?'#345f90':'#3d6fa3');c.fillRect(ox+x,oy+y,1,1)}}});
  tile(TILE.bedrock,(ox,oy)=>{fill(ox,oy,'#43424a');
    for(let x=0;x<TS;x++)for(let y=0;y<TS;y++){c.fillStyle=['#2b2b31','#565561','#37363d'][(R()*3)|0];c.fillRect(ox+x,oy+y,1,1)}});
  return cv;
}
const atlasCanvas=genAtlas();

/* アイコン描画（2.5D キューブ風） */
function drawIcon(cv,id){
  const c=cv.getContext('2d');c.imageSmoothingEnabled=false;
  const d=DEFS[id],W=cv.width,H=cv.height;
  const tileRect=(t,dx,dy,dw,dh)=>{const col=t%ACOLS,row=(t/ACOLS)|0;c.drawImage(atlasCanvas,col*TS,row*TS,TS,TS,dx,dy,dw,dh)};
  const s=W/48;
  c.clearRect(0,0,W,H);
  // 側面
  tileRect(d.tiles[1],3*s,20*s,34*s,24*s);
  c.fillStyle='rgba(0,0,0,.22)';c.fillRect(3*s,20*s,34*s,24*s);
  // 上面（平行四辺形）
  c.save();c.setTransform(s,0,-0.42*s,0.44*s,6*s,14*s);
  tileRect(d.tiles[0],0,0,30*s/s,30*s/s);
  c.restore();
  // 上面の縁
  c.fillStyle='rgba(255,255,255,.16)';
  c.beginPath();c.moveTo(6*s,14*s);c.lineTo(36*s,14*s);c.lineTo(30*s,20*s);c.lineTo(0*s+6*s-6*s+0,20*s);c.closePath();c.fill();
}
function makeIconCanvas(id,size=44){const cv=document.createElement('canvas');cv.width=cv.height=48;drawIcon(cv,id);cv.style.width=size+'px';cv.style.height=size+'px';return cv}

/* ============================================================
   2. 世界データ
============================================================ */
const WX=80,WY=48,WZ=80,CS=16,CX=WX/CS,CZ=WZ/CS,WATER_LEVEL=13;
let world=new Uint8Array(WX*WY*WZ),seed=7714202755;
const wIdx=(x,y,z)=>(y*WZ+z)*WX+x;
function get(x,y,z){if(x<0||y<0||z<0||x>=WX||y>=WY||z>=WZ)return y<0?BEDROCK:AIR;return world[wIdx(x,y,z)]}
function set(x,y,z,v){if(x<0||y<0||z<0||x>=WX||y>=WY||z>=WZ)return false;world[wIdx(x,y,z)]=v;return true}
const isBlend=id=>DEFS[id]&&DEFS[id].blend;
const isOpaque=id=>id!==AIR&&!isBlend(id)&&!(DEFS[id]&&DEFS[id].alphaTest);
const isSolid=id=>id!==AIR&&!(DEFS[id]&&DEFS[id].noSolid);

function fbm2(x,y,oct,s){let v=0,a=1,tot=0;for(let i=0;i<oct;i++){v+=a*value2(x*(1+i*0.9),y*(1+i*0.9),s+i*131);tot+=a;a*=.5}return v/tot}
function value2(x,y,s){const xi=Math.floor(x),yi=Math.floor(y),fx=x-xi,fy=y-yi;
  const a=hash2(xi,yi+s),b=hash2(xi+1,yi+s),cc=hash2(xi,yi+1+s),d=hash2(xi+1,yi+1+s);
  const sx=fx*fx*(3-2*fx),sy=fy*fy*(3-2*fy);
  return (a*(1-sx)+b*sx)*(1-sy)+(cc*(1-sx)+d*sx)*sy}
function noise3(x,y,z,s){const xi=Math.floor(x),yi=Math.floor(y),zi=Math.floor(z);
  const fx=x-xi,fy=y-yi,fz=z-zi,sx=fx*fx*(3-2*fx),sy=fy*fy*(3-2*fy),sz=fz*fz*(3-2*fz);
  const h=(a,b,c)=>hash3(a,b,c+s);
  const c00=h(xi,yi,zi)*(1-sx)+h(xi+1,yi,zi)*sx;
  const c10=h(xi,yi+1,zi)*(1-sx)+h(xi+1,yi+1,zi)*sx;
  const c01=h(xi,yi,zi+1)*(1-sx)+h(xi+1,yi,zi+1)*sx;
  const c11=h(xi,yi+1,zi+1)*(1-sx)+h(xi+1,yi+1,zi+1)*sx;
  const c0=c00*(1-sy)+c10*sy,c1=c01*(1-sy)+c11*sy;
  return c0*(1-sz)+c1*sz}
function fbm3(x,y,z,oct,s){let v=0,a=1,tot=0;for(let i=0;i<oct;i++){v+=a*noise3(x*(1+i*.8),y*(1+i*.6),z*(1+i*.8),s+i*77);tot+=a;a*=.5}return v/tot}
function heightAt(x,z){
  const n1=fbm2(x*0.024,z*0.024,4,seed), n2=fbm2(x*0.0075,z*0.0085,3,seed+911);
  return Math.floor(4+n2*26+n1*8);
}
function genTerrain(){
  world.fill(AIR);
  const hs=new Int16Array(WX*WZ);
  for(let x=0;x<WX;x++)for(let z=0;z<WZ;z++){
    const h=heightAt(x,z);hs[x*WZ+z]=h;
    for(let y=0;y<=Math.max(h,WATER_LEVEL);y++){
      if(y===0){set(x,y,z,BEDROCK);continue}
      if(y>h){ if(y<=WATER_LEVEL){set(x,y,z,WATER)} continue }
      let top=GRASS;
      if(h<=WATER_LEVEL+1)top=SAND;
      else if(h>27)top=SNOW;
      if(y===h)set(x,y,z,top);
      else if(y>h-4)set(x,y,z, top===SAND?SAND:DIRT);
      else set(x,y,z,STONE);
    }
  }
  // 洞窟
  for(let x=1;x<WX-1;x++)for(let z=1;z<WZ-1;z++){
    const h=hs[x*WZ+z];
    for(let y=2;y<h-1;y++){
      if(fbm3(x*0.055,y*0.09,z*0.055,3,seed+400)>0.63){
        if(get(x,y,z)!==BEDROCK)set(x,y,z,AIR);
      }
    }
  }
  // 水再充填（洞窟で抜けた陸下）
  for(let x=0;x<WX;x++)for(let z=0;z<WZ;z++){
    const h=hs[x*WZ+z];
    for(let y=h+1;y<=WATER_LEVEL;y++)if(get(x,y,z)===AIR)set(x,y,z,WATER);
  }
  // 木
  for(let x=2;x<WX-2;x++)for(let z=2;z<WZ-2;z++){
    const h=hs[x*WZ+z];
    if(get(x,h,z)!==GRASS)continue;
    if(hash2(x*7+3,z*11+5,seed+31)>0.94){
      const th=4+((hash2(x,z,seed+7)*3)|0);
      for(let y=h+1;y<=h+th;y++)set(x,y,z,LOG);
      const ly=h+th-1;
      for(let dy=-1;dy<=2;dy++)for(let dx=-2;dx<=2;dx++)for(let dz=-2;dz<=2;dz++){
        const r=Math.abs(dx)+Math.abs(dz)+Math.abs(dy)*1.2;
        if(r>3.2)continue;
        const px2=x+dx,py=ly+dy,pz=z+dz;
        if(get(px2,py,pz)===AIR)set(px2,py,pz,LEAF);
      }
      set(x,ly+3,z,LEAF);
    }
  }
}

/* ============================================================
   3. WebGL2 レンダラ
============================================================ */
const canvas=document.getElementById('gl');
const gl=canvas.getContext('webgl2',{antialias:true});
if(!gl){document.getElementById('title').innerHTML='<div class="wrap"><div class="logo"><div class="l1">WebGL2</div><div class="l3">このブラウザでは WebGL2 が使えません。</div></div></div>';throw new Error('no webgl2')}

const VS=`#version 300 es
precision highp float;
in vec3 aPos; in vec2 aUV; in float aTile; in float aAO; in vec3 aN;
uniform mat4 uProj,uView; uniform vec3 uSunDir,uSunCol,uAmbient,uFogCol;
uniform float uFogNear,uFogFar,uTime,uUnder,uOpacity,uAlphaTest,uCols,uRows;
out vec2 vUV; out float vTile; out float vAO; out vec3 vN; out float vDist;
void main(){
  vec4 cp=uView*vec4(aPos,1.0);
  gl_Position=uProj*cp;
  vDist=length(cp.xyz);
  vUV=aUV; vTile=aTile; vAO=aAO; vN=aN;
}`;
const FS=`#version 300 es
precision highp float;
in vec2 vUV; in float vTile; in float vAO; in vec3 vN; in float vDist;
uniform vec3 uSunDir,uSunCol,uAmbient,uFogCol;
uniform float uFogNear,uFogFar,uTime,uUnder,uOpacity,uAlphaTest,uCols,uRows;
uniform sampler2D uAtlas;
out vec4 frag;
void main(){
  vec2 uv=(vec2(mod(vTile,uCols),floor(vTile/uCols))+vUV)/vec2(uCols,uRows);
  if(vTile==14.0){uv+=vec2(sin(uTime*1.1+vUV.y*6.0)*0.02,cos(uTime*0.8+vUV.x*5.0)*0.02);}
  vec4 t=texture(uAtlas,uv);
  if(uAlphaTest>0.5&&t.a<0.5) discard;
  float ao=mix(0.30,1.0,vAO);
  float ndl=max(dot(vN,uSunDir),0.0);
  float shade=ao*(uAmbient+uSunCol*ndl);
  vec3 col=t.rgb*shade;
  if(vTile==13.0) col+=t.rgb*0.55;
  float f=smoothstep(uFogNear,uFogFar,vDist);
  col=mix(col,uFogCol,f*0.85);
  if(uUnder>0.5){col=mix(col,vec3(0.20,0.42,0.55),0.45);col*=0.85;}
  frag=vec4(col,t.a*uOpacity);
}`;
const SVS=`#version 300 es
in vec2 aP; out vec2 vUv;
void main(){vUv=aP;gl_Position=vec4(aP,0.0,1.0);}`;
const SFS=`#version 300 es
precision highp float;
in vec2 vUv;
uniform vec3 uRight,uUp,uFwd,uSunDir;
uniform float uTan,uAspect,uDay,uTime;
out vec4 frag;
float h21(vec2 p){p=fract(p*vec2(123.34,456.21));p+=dot(p,p+45.32);return fract(p.x*p.y);}
float n2(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.0-2.0*f);
  return mix(mix(h21(i),h21(i+vec2(1,0)),f.x),mix(h21(i+vec2(0,1)),h21(i+vec2(1,1)),f.x),f.y);}
float fbm(vec2 p){float v=0.0,a=0.5;for(int i=0;i<5;i++){v+=a*n2(p);p*=2.03;a*=0.5;}return v;}
void main(){
  vec2 p=vUv*uTan;
  vec3 dir=normalize(uFwd+uRight*p.x*uAspect+uUp*p.y);
  float up=dir.y;
  float d=uDay;
  float dusk=smoothstep(0.0,0.32,d)*(1.0-smoothstep(0.30,0.8,d));
  vec3 zen=mix(vec3(0.03,0.05,0.11),vec3(0.40,0.62,0.86),d);
  zen=mix(zen,vec3(0.20,0.26,0.42),dusk*0.7);
  vec3 hor=mix(vec3(0.09,0.13,0.21),vec3(0.72,0.83,0.93),d);
  hor=mix(hor,vec3(0.94,0.52,0.28),dusk*0.85);
  float t=pow(max(up,0.0),0.6);
  vec3 col=mix(hor,zen,t);
  float sd=dot(dir,uSunDir);
  float disc=smoothstep(0.9972,0.9995,sd);
  col+=disc*mix(vec3(1.0,0.55,0.26),vec3(1.0,0.96,0.82),d)*2.2;
  col+=pow(max(sd,0.0),9.0)*mix(vec3(0.85,0.42,0.22),vec3(0.42,0.52,0.66),d)*0.4;
  float md=dot(dir,-uSunDir);
  col+=smoothstep(0.9978,0.9997,md)*vec3(0.86,0.90,0.96)*(1.0-d)*1.8;
  float st=fract(sin(dot(floor(dir*230.0),vec3(12.9898,78.233,45.164)))*43758.5453);
  col+=step(0.984,st)*(st-0.984)*26.0*(1.0-d)*vec3(0.85,0.9,1.0)*(0.7+0.3*sin(uTime*3.0+st*20.0));
  if(up>0.0){
    vec2 cp=dir.xz/max(up,0.06)*0.021+vec2(uTime*0.012,uTime*0.006);
    float c=fbm(cp); c=smoothstep(0.52,0.70,c);
    float a=c*smoothstep(0.02,0.25,up)*0.85;
    vec3 cl=mix(vec3(0.96,0.95,0.93),vec3(0.30,0.36,0.48),1.0-d);
    col=mix(col,cl,a);
  }
  frag=vec4(col,1.0);
}`;
const LVS=`#version 300 es
in vec3 aPos; uniform mat4 uProj,uView,uModel; uniform float uFlash;
out float vF;
void main(){vF=uFlash;gl_Position=uProj*uView*uModel*vec4(aPos,1.0);}`;
const LFS=`#version 300 es
precision highp float; in float vF; uniform float uAlpha; out vec4 frag;
void main(){frag=vec4(mix(vec3(1.0),vec3(0.96,0.72,0.36),vF),uAlpha*(0.55+0.45*vF));}`;

function prog(v,f){const p=gl.createProgram();const a=gl.createShader(gl.VERTEX_SHADER);gl.shaderSource(a,v);gl.compileShader(a);
  const b=gl.createShader(gl.FRAGMENT_SHADER);gl.shaderSource(b,f);gl.compileShader(b);
  gl.attachShader(p,a);gl.attachShader(p,b);gl.linkProgram(p);
  if(!gl.getProgramParameter(p,gl.LINK_STATUS))console.error(gl.getProgramInfoLog(p));
  return p}
const P=prog(VS,FS),SP=prog(SVS,SFS),LP=prog(LVS,LFS);
const U={};for(const name of ['uProj','uView','uSunDir','uSunCol','uAmbient','uFogCol','uFogNear','uFogFar','uTime','uUnder','uOpacity','uAlphaTest','uCols','uRows','uAtlas'])U[name]=gl.getUniformLocation(P,name);
const SU={};for(const n of ['uRight','uUp','uFwd','uSunDir','uTan','uAspect','uDay','uTime'])SU[n]=gl.getUniformLocation(SP,n);
const LU={};for(const n of ['uProj','uView','uModel','uFlash','uAlpha'])LU[n]=gl.getUniformLocation(LP,n);

const tex=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,tex);
gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,atlasCanvas);
gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.NEAREST);
gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.NEAREST);
gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);
gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
gl.uniform1i(U.uAtlas,0);gl.uniform1f(U.uCols,ACOLS);gl.uniform1f(U.uRows,AROWS);

/* チャンクメッシュ構築 */
const DIRS=[
 {n:[0,1,0],c:[[0,1,1],[1,1,1],[1,1,0],[0,1,0]],uv:c=>[c[0],c[2]]},
 {n:[0,-1,0],c:[[0,0,0],[1,0,0],[1,0,1],[0,0,1]],uv:c=>[c[0],c[2]]},
 {n:[1,0,0],c:[[1,0,1],[1,0,0],[1,1,0],[1,1,1]],uv:c=>[c[2],c[1]]},
 {n:[-1,0,0],c:[[0,0,0],[0,0,1],[0,1,1],[0,1,0]],uv:c=>[c[2],c[1]]},
 {n:[0,0,1],c:[[0,0,1],[1,0,1],[1,1,1],[0,1,1]],uv:c=>[c[0],c[1]]},
 {n:[0,0,-1],c:[[1,0,0],[0,0,0],[0,1,0],[1,1,0]],uv:c=>[c[0],c[1]]},
];
const PERP=[[0,2],[0,1],[1,2],[1,2],[0,1],[0,1]];
function aoAt(x,y,z,f){
  const d=DIRS[f],n=d.n,axis=(n[0]!==0?0:(n[1]!==0?1:2));
  const u=PERP[f][0],v=PERP[f][1];
  const p=[x+n[0],y+n[1],z+n[2]];
  const s1=(u===axis)?0:(p[u]<x?1:(p[u]>x?2:0));
  const su=u===axis?0:((d.c[0][u]===0)?-1:1);
  const sv=v===axis?0:((d.c[0][v]===0)?-1:1);
  const a=isOpaque(get(p[0]+ (u===axis?0:su), p[1]+(v===axis?0:0), p[2]+(v===axis?0:sv)));
  // 正確な AO: side1(u軸方向), side2(v軸方向), corner
  const b1=isOpaque(get(p[0]+su,p[1],p[2]));
  const b2=isOpaque(get(p[0],p[1]+sv,p[2]));
  if(u===2&&v===1){/* 軸対応は下の汎用で処理 */}
  const sA=(u===0)?su:(u===1?sv:sv);
  const sB=(v===0)?su:(v===1?sv:sv);
  const side1=isOpaque(get(p[0]+(u===0?su:0)+(v===0?0:0),p[1]+(u===1||v===1?sv:0),p[2]+(u===2?su:v===2?sv:0)));
  const side2=isOpaque(get(p[0]+(u===0?su:0),p[1]+(v===1?sv:0),p[2]+(v===2?sv:0)));
  const corner=isOpaque(get(p[0]+su,p[1]+sv,p[2]));
  const s=(side1?1:0)+(side2?1:0)+(corner?1:0);
  return s>=3?0:3-s;
}
function buildChunk(cx,cz){
  const op=[],oi=[],al=[],ai=[];
  let faces=0;
  for(let y=0;y<WY;y++)for(let z=cz*CS;z<cz*CS+CS;z++)for(let x=cx*CS;x<cx*CS+CS;x++){
    const id=world[wIdx(x,y,z)];
    if(id===AIR)continue;
    const blend=isBlend(id);
    const surf=(id===WATER&&get(x,y+1,z)===AIR)?y+0.9:y+1;
    const d=DEFS[id];
    for(let f=0;f<6;f++){
      const dd=DIRS[f],n=dd.n;
      const nb=get(x+n[0],y+n[1],z+n[2]);
      if(nb===id&&id!==AIR&&!(DEFS[nb]&&DEFS[nb].alphaTest))continue;
      if(isOpaque(nb))continue;
      const tile=(dd.n[1]>0)?d.tiles[0]:(dd.n[1]<0?d.tiles[2]:d.tiles[1]);
      const base=blend?al:op, bi=blend?ai:oi;
      const v0=base.length;
      const useAO=!blend;
      for(let k=0;k<4;k++){
        const c=dd.c[k];
        base.push(x+c[0],Math.min(y+c[1],surf),z+c[2]);
        base.push(dd.uv(c)[0],dd.uv(c)[1]);
        base.push(tile);
        base.push(useAO?aoAt(x,y,z,f)/3:1);
        base.push(n[0],n[1],n[2]);
      }
      bi.push(v0/9,v0/9+1,v0/9+2,v0/9,v0/9+2,v0/9+3);
      faces++;
    }
  }
  return {op:new Float32Array(op),oi:new Uint32Array(oi),al:new Float32Array(al),ai:new Uint32Array(ai),faces};
}
function makeMesh(data){
  if(!data.op.length&&!data.al.length)return {nulls:true,faces:0};
  const m={faces:data.faces,nulls:false};
  if(data.op.length){m.vaoO=gl.createVertexArray();gl.bindVertexArray(m.vaoO);
    const vb=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,vb);gl.bufferData(gl.ARRAY_BUFFER,data.op,gl.STATIC_DRAW);
    gl.enableVertexAttribArray(0);gl.vertexAttribPointer(0,3,gl.FLOAT,false,36,0);
    gl.enableVertexAttribArray(1);gl.vertexAttribPointer(1,2,gl.FLOAT,false,36,12);
    gl.enableVertexAttribArray(2);gl.vertexAttribPointer(2,1,gl.FLOAT,false,36,20);
    gl.enableVertexAttribArray(3);gl.vertexAttribPointer(3,1,gl.FLOAT,false,36,24);
    gl.enableVertexAttribArray(4);gl.vertexAttribPointer(4,3,gl.FLOAT,false,36,28);
    const ib=gl.createBuffer();gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,ib);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,data.oi,gl.STATIC_DRAW);
    m.countO=data.oi.length;m.vb=vb;m.ib=ib;}
  if(data.al.length){m.vaoA=gl.createVertexArray();gl.bindVertexArray(m.vaoA);
    const vb=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,vb);gl.bufferData(gl.ARRAY_BUFFER,data.al,gl.STATIC_DRAW);
    gl.enableVertexAttribArray(0);gl.vertexAttribPointer(0,3,gl.FLOAT,false,36,0);
    gl.enableVertexAttribArray(1);gl.vertexAttribPointer(1,2,gl.FLOAT,false,36,12);
    gl.enableVertexAttribArray(2);gl.vertexAttribPointer(2,1,gl.FLOAT,false,36,20);
    gl.enableVertexAttribArray(3);gl.vertexAttribPointer(3,1,gl.FLOAT,false,36,24);
    gl.enableVertexAttribArray(4);gl.vertexAttribPointer(4,3,gl.FLOAT,false,36,28);
    const ib=gl.createBuffer();gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,ib);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,data.ai,gl.STATIC_DRAW);
    m.countA=data.ai.length;m.vbA=vb;m.ibA=ib;}
  return m;
}
const chunks=[];
let totalFaces=0;
function rebuild(cx,cz){
  const c=chunks[cx*CZ+cz];
  if(c.mesh&&!c.mesh.nulls){
    if(c.mesh.vb){gl.deleteBuffer(c.mesh.vb);gl.deleteBuffer(c.mesh.ib)}
    if(c.mesh.vbA){gl.deleteBuffer(c.mesh.vbA);gl.deleteBuffer(c.mesh.ibA)}
    if(c.mesh.vaoO)gl.deleteVertexArray(c.mesh.vaoO);
    if(c.mesh.vaoA)gl.deleteVertexArray(c.mesh.vaoA);
  }
  const data=buildChunk(cx,cz);
  c.mesh=makeMesh(data);
  totalFaces+=c.mesh.faces-(c.faces||0);
  c.faces=c.mesh.faces;
}

/* 輪郭線 */
const cubeLines=new Float32Array([
 0,0,0, 1,0,0, 1,0,0, 1,0,1, 1,0,1, 0,0,1, 0,0,1, 0,0,0,
 0,1,0, 1,1,0, 1,1,0, 1,1,1, 1,1,1, 0,1,1, 0,1,1, 0,1,0,
 0,0,0, 0,1,0, 1,0,0, 1,1,0, 1,0,1, 1,1,1, 0,0,1, 0,1,1
]);
const lvao=gl.createVertexArray();gl.bindVertexArray(lvao);
const lvb=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,lvb);gl.bufferData(gl.ARRAY_BUFFER,cubeLines,gl.STATIC_DRAW);
gl.enableVertexAttribArray(0);gl.vertexAttribPointer(0,3,gl.FLOAT,false,12,0);
const skyVAO=gl.createVertexArray();gl.bindVertexArray(skyVAO);
const skb=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,skb);
gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,3,-1,-1,3]),gl.STATIC_DRAW);
gl.enableVertexAttribArray(0);gl.vertexAttribPointer(0,2,gl.FLOAT,false,8,0);

/* 粒子 */
const MAXP=420;
const pbuf=new Float32Array(MAXP*24*9);
const pidx=new Uint32Array(MAXP*36);
for(let i=0;i<MAXP;i++){const b=i*24;for(let f=0;f<6;f++){const o=b+f*4;pidx[i*36+f*6+0]=o;pidx[i*36+f*6+1]=o+1;pidx[i*36+f*6+2]=o+2;pidx[i*36+f*6+3]=o;pidx[i*36+f*6+4]=o+2;pidx[i*36+f*6+5]=o+3}}
const pvao=gl.createVertexArray();gl.bindVertexArray(pvao);
const pvb=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,pvb);gl.bufferData(gl.ARRAY_BUFFER,pbuf.byteLength,gl.DYNAMIC_DRAW);
gl.enableVertexAttribArray(0);gl.vertexAttribPointer(0,3,gl.FLOAT,false,36,0);
gl.enableVertexAttribArray(1);gl.vertexAttribPointer(1,2,gl.FLOAT,false,36,12);
gl.enableVertexAttribArray(2);gl.vertexAttribPointer(2,1,gl.FLOAT,false,36,20);
gl.enableVertexAttribArray(3);gl.vertexAttribPointer(3,1,gl.FLOAT,false,36,24);
gl.enableVertexAttribArray(4);gl.vertexAttribPointer(4,3,gl.FLOAT,false,36,28);
const pib=gl.createBuffer();gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,pib);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,pidx,gl.STATIC_DRAW);

/* ============================================================
   4. 行列
============================================================ */
function persp(fovY,a,n,f){const t=1/Math.tan(fovY/2);return new Float32Array([t/a,0,0,0, 0,t,0,0, 0,0,(f+n)/(n-f),-1, 0,0,2*f*n/(n-f),0])}
function mul(a,b){const o=new Float32Array(16);for(let i=0;i<4;i++)for(let j=0;j<4;j++){let s=0;for(let k=0;k<4;k++)s+=a[k*4+i]*b[k*4+j];o[j*4+i]=s}return o}
function viewMat(yaw,pitch,eye){
  const cp=Math.cos(-pitch),sp=Math.sin(-pitch),cy=Math.cos(-yaw),sy=Math.sin(-yaw);
  const rx=new Float32Array([1,0,0,0, 0,cp,sp,0, 0,-sp,cp,0, 0,0,0,1]);
  const ry=new Float32Array([cy,0,-sy,0, 0,1,0,0, sy,0,cy,0, 0,0,0,1]);
  const tr=new Float32Array([1,0,0,0, 0,1,0,0, 0,0,1,0, -eye[0],-eye[1],-eye[2],1]);
  return mul(mul(rx,ry),tr);
}

/* ============================================================
   5. プレイヤー / 入力
============================================================ */
const player={pos:{x:0,y:0,z:0},vel:{x:0,y:0,z:0},yaw:0,pitch:0,onGround:false,fly:false,sneak:false,inWater:false};
let hotbar=[GRASS,DIRT,STONE,COBBLE,SAND,LOG,LEAF,PLANK,BRICK];
let sel=0, slotTarget=null;
const keys={};
let sens=1, fogFar=70, dayLen=120, fovBase=70, fovCur=70;
let dayT=0.22, dayCount=1, elapsed=0;
let state='title';
let flash=