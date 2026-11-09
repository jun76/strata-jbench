以下、単一HTMLファイルで動く「**Minecraft風 3D 箱庭**」を作りました。WebGL（Three.js）でブロックを積み重ねて壊し、地形を生成し、昼夜・日没・水中・雲まで備えています。

```html
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
<title>Blockcraft — 立方体の世界</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root{
    --ink:#0a0c08; --panel:#12160f; --panel2:#171d12;
    --line:rgba(246,214,122,.14);
    --brass:#f6d67a; --brass2:#e0a94a;
    --grass:#7fbf4d; --grass2:#5f9c39;
    --amber:#f4a63b; --danger:#ff5a52;
    --text:#f4efe6; --muted:#9aa78f;
  }
  *{box-sizing:border-box}
  html,body{margin:0;height:100%;overflow:hidden;background:var(--ink);color:var(--text);
    font-family:'Space Grotesk',system-ui,sans-serif}
  #gl{position:fixed;inset:0;display:block;z-index:0;cursor:default}

  /* ---------- shared blocky panel ---------- */
  .panel{background:linear-gradient(180deg,#171d12,#0f130c);
    border:1px solid var(--line);
    box-shadow:0 10px 0 rgba(0,0,0,.35), 0 22px 44px rgba(0,0,0,.5),
      inset 0 1px 0 rgba(255,255,255,.06);
    clip-path:polygon(0 6px,6px 6px,6px 0,calc(100% - 6px) 0,calc(100% - 6px) 6px,
      100% 6px,100% calc(100% - 6px),calc(100% - 6px) calc(100% - 6px),
      calc(100% - 6px) 100%,6px 100%,6px calc(100% - 6px),0 calc(100% - 6px));}

  .disp{font-family:'Press Start 2P',monospace;letter-spacing:.5px;line-height:1.5}

  /* ---------- HUD ---------- */
  #hud{position:fixed;inset:0;z-index:5;pointer-events:none}
  #hud .panel{pointer-events:auto}

  .info{position:absolute;top:16px;left:16px;min-width:212px;padding:14px 16px}
  .info h1{font-size:15px;margin:0 0 12px;color:var(--brass);text-shadow:0 2px 0 #000}
  .stat{display:flex;align-items:center;gap:9px;margin:7px 0;font-size:12.5px}
  .stat .lbl{font-family:'Press Start 2P',monospace;font-size:8px;color:var(--muted);width:44px}
  .stat .val{font-weight:700;letter-spacing:.5px}
  .stat .val.pos{font-size:10px;color:#cfe6c0}
  .sw{width:14px;height:14px;background:var(--sw,#666);border:2px solid rgba(0,0,0,.4);
    box-shadow:inset -3px -3px 0 rgba(0,0,0,.28),inset 3px 3px 0 rgba(255,255,255,.28)}
  .daynight{margin-top:11px;font-size:11px;color:var(--amber);font-weight:600}

  .clock{position:absolute;top:16px;right:16px;width:104px;padding:12px;text-align:center}
  .sun{width:54px;height:54px;margin:2px auto 4px;border-radius:2px;
    background:radial-gradient(circle at 40% 35%,#fff2b0,#ffce54 45%,#f4a63b 72%,#c9792c);
    box-shadow:0 0 22px rgba(255,206,84,.55),inset -6px -6px 0 rgba(0,0,0,.22);
    transition:transform .8s ease, box-shadow .8s ease, background .8s ease}
  .clock.night .sun{background:radial-gradient(circle at 40% 35%,#e9f2ff,#c8d8ee 45%,#94a8c4 72%,#67788f);
    box-shadow:0 0 18px rgba(150,185,240,.45),inset -6px -6px 0 rgba(0,0,0,.3);transform:rotate(180deg)}
  .clock .t{font-family:'Press Start 2P',monospace;font-size:14px;color:var(--brass)}
  .clock .p{font-size:10px;color:var(--muted);margin-top:5px}
  .clock .bar{height:5px;background:rgba(0,0,0,.5);margin-top:8px;overflow:hidden}
  .clock .bar i{display:block;height:100%;background:linear-gradient(90deg,#5c7fb0,#ffce54);transition:width .3s}

  .hint{position:absolute;bottom:16px;left:16px;padding:10px 14px;font-size:11px;color:var(--muted);
    display:flex;gap:14px;flex-wrap:wrap;align-items:center}
  .hint b{color:var(--text)}
  .ctrls{position:absolute;bottom:16px;right:16px;padding:9px 12px;font-size:11px}
  .ctrls button{background:#0f130c;color:var(--text);border:1px solid var(--line);
    padding:6px 10px;margin-left:8px;cursor:pointer;font-family:inherit;font-size:11px;transition:.15s}
  .ctrls button:hover{background:#1a2114;color:var(--brass);transform:translateY(-1px)}

  /* crosshair */
  .cross{position:absolute;left:50%;top:50%;width:34px;height:34px;transform:translate(-50%,-50%);
    pointer-events:none;opacity:0;transition:opacity .3s}
  .cross::before,.cross::after{content:'';position:absolute;background:rgba(255,255,255,.82);
    box-shadow:0 0 0 1px rgba(0,0,0,.6),0 0 4px rgba(0,0,0,.5)}
  .cross::before{left:50%;top:0;bottom:0;width:2px;transform:translateX(-50%)}
  .cross::after{top:50%;left:0;right:0;height:2px;transform:translateY(-50%)}
  body.locked .cross{opacity:1}

  /* hotbar */
  .hotbar{position:absolute;left:50%;bottom:18px;transform:translateX(-50%) translateY(16px);
    display:flex;gap:6px;padding:9px;pointer-events:auto;opacity:0;transition:opacity .4s,transform .4s}
  body.locked .hotbar{opacity:1;transform:translateX(-50%) translateY(0)}
  .slot{width:52px;height:52px;display:grid;place-items:center;background:#0f130c;
    border:2px solid #262c1e;position:relative;cursor:pointer;transition:.12s}
  .slot:hover{border-color:#3a4430}
  .slot.active{border-color:var(--brass);box-shadow:0 0 0 2px rgba(246,214,122,.35),
    inset 0 0 14px rgba(246,214,122,.15);transform:translateY(-3px)}
  .slot .cube{width:30px;height:30px;background:var(--sw);position:relative;
    box-shadow:inset -6px -6px 0 rgba(0,0,0,.34),inset 6px 6px 0 rgba(255,255,255,.24)}
  .slot .cube i{position:absolute;left:0;right:0;top:0;height:34%;background:var(--sw2);
    box-shadow:inset 0 -3px 0 rgba(0,0,0,.3)}
  .slot .num{position:absolute;top:3px;left:5px;font-family:'Press Start 2P',monospace;
    font-size:8px;color:var(--muted)}
  .slot .nm{position:absolute;bottom:-19px;left:50%;transform:translateX(-50%);white-space:nowrap;
    font-size:10px;font-weight:600;opacity:0;transition:.15s;pointer-events:none}
  .slot:hover .nm,.slot.active .nm{opacity:1}

  /* start screen */
  #start{position:fixed;inset:0;z-index:20;display:flex;align-items:center;justify-content:center;
    padding:24px;background:radial-gradient(120% 90% at 50% 40%,rgba(10,12,8,.32),rgba(10,12,8,.78));
    transition:opacity .5s,visibility .5s}
  #start.gone{opacity:0;visibility:hidden}
  .start-card{max-width:720px;width:100%;display:grid;grid-template-columns:1fr auto;gap:26px;
    align-items:center;padding:34px 36px}
  .brand{font-family:'Press Start 2P',monospace;font-size:40px;line-height:1.1;color:#fff;
    text-shadow:0 3px 0 #000,0 0 26px rgba(246,214,122,.35)}
  .brand .g{color:var(--brass)}
  .brand .b{color:#4a86c4}
  .tag{margin:14px 0 22px;font-size:15px;color:#d8e3d0;max-width:44ch}
  .tag b{color:var(--grass)}
  .play{font-family:'Press Start 2P',monospace;font-size:15px;color:#12240a;
    background:linear-gradient(180deg,#8fd25a,#5f9c39);border:none;padding:16px 26px;cursor:pointer;
    box-shadow:0 6px 0 #3d6b24,0 12px 22px rgba(0,0,0,.5);transition:.12s;position:relative;overflow:hidden}
  .play:hover{transform:translateY(-2px);box-shadow:0 8px 0 #3d6b24,0 14px 26px rgba(0,0,0,.55)}
  .play:active{transform:translateY(3px);box-shadow:0 3px 0 #3d6b24}
  .keys{margin-top:22px;display:grid;grid-template-columns:repeat(2,auto);gap:9px 26px;
    font-size:12.5px;color:var(--muted)}
  .keys div{display:flex;gap:8px;align-items:center}
  kbd{font-family:'Press Start 2P',monospace;font-size:9px;background:#0f130c;border:1px solid var(--line);
    border-bottom-width:3px;padding:5px 7px;color:var(--brass);min-width:20px;text-align:center;display:inline-block}
  .seedrow{margin-top:18px;display:flex;align-items:center;gap:10px;font-size:12px;color:var(--muted)}
  .seedrow input{background:#0f130c;border:1px solid var(--line);color:var(--text);padding:6px 8px;
    width:120px;font-family:'Press Start 2P',monospace;font-size:9px}
  .seedrow button{background:#0f130c;border:1px solid var(--line);color:var(--muted);padding:6px 9px;
    cursor:pointer;font-size:11px}
  .seedrow button:hover{color:var(--brass);border-color:var(--line)}
  .deco{position:relative;width:150px;height:150px}
  .deco .blk{position:absolute;width:44px;height:44px;box-shadow:inset -6px -6px 0 rgba(0,0,0,.32),
    inset 6px 6px 0 rgba(255,255,255,.24);animation:bob 3s ease-in-out infinite}
  @keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}

  #err{position:fixed;inset:0;z-index:40;display:none;place-items:center;text-align:center;
    padding:30px;background:#0a0c08}
  #err.show{display:grid}
  #err p{font-size:14px;color:var(--muted);max-width:40ch}

  @media (max-width:760px){
    .start-card{grid-template-columns:1fr}.deco{display:none}
    .brand{font-size:26px}.hint{display:none}
  }
</style>
</head>
<body>
<canvas id="gl"></canvas>

<div id="hud">
  <div class="info panel">
    <h1 class="disp">BLOCKCRAFT</h1>
    <div class="stat"><span class="sw" id="sw"></span><span class="lbl">ブロック</span><span class="val" id="curName">草ブロック</span></div>
    <div class="stat"><span class="lbl">XYZ</span><span class="val pos" id="coords">0 0 0</span></div>
    <div class="stat"><span class="lbl">ブロック</span><span class="val" id="blocks">0</span></div>
    <div class="daynight" id="phase">☀ 昼</div>
  </div>

  <div class="clock panel" id="clock">
    <div class="sun" id="sun"></div>
    <div class="t" id="time">06:00</div>
    <div class="p" id="day">DAY 1</div>
    <div class="bar"><i id="daybar"></i></div>
  </div>

  <div class="cross"></div>
  <div class="hotbar" id="hotbar"></div>

  <div class="hint panel"><span>移動 <b>WASD</b></span><span>ジャンプ <b>Space</b></span><span>走る <b>Shift</b></span><span>壊す <b>左クリック</b></span><span>置く <b>右クリック</b></span><span>視点 <b>マウス</b></span><span>選択 <b>1-9</b></span></div>
  <div class="ctrls panel"><button id="regen">地形再生成</button><button id="help">操作</button></div>
</div>

<div id="start">
  <div class="start-card panel">
    <div>
      <div class="brand"><span class="g">BLOCK</span><span class="b">CRAFT</span></div>
      <p class="tag">無限に広がる<b>立方体の世界</b>を歩いて、掘って、積み上げて、自分だけの箱庭を編もう。</p>
      <button class="play" id="play">▶ 世界に入る</button>
      <div class="keys">
        <div><kbd>WASD</kbd> 移動</div><div><kbd>␣</kbd> ジャンプ</div>
        <div><kbd>⇧</kbd> 走る</div><div><kbd>1-9</kbd> ブロック</div>
        <div><kbd>左</kbd> 壊す</div><div><kbd>右</kbd> 置く</div>
        <div><kbd>Esc</kbd> 解除</div><div><kbd>マウス</kbd> 視点</div>
      </div>
      <div class="seedrow">シード <input id="seed" value="2048"><button id="dice">🎲 乱数</button></div>
    </div>
    <div class="deco">
      <div class="blk" style="left:0;top:40px;background:#7fbf4d;--x:0;animation-delay:0s"></div>
      <div class="blk" style="left:52px;top:0;background:#8b5a2b;animation-delay:.4s"></div>
      <div class="blk" style="left:104px;top:40px;background:#b9c1c9;animation-delay:.8s"></div>
      <div class="blk" style="left:52px;top:80px;background:#34b1c9;animation-delay:1.2s"></div>
    </div>
  </div>
</div>

<div id="err"><p>この端末は WebGL に対応していないようです。<br>PC のブラウザでお試しください。</p></div>

<script type="importmap">
{ "imports": {
  "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
  "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
}}
</script>

<script type="module">
import * as THREE from 'three';
import { Sky } from 'three/addons/objects/Sky.js';

/* ============ helpers ============ */
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const lerp=(a,b,t)=>a+(b-a)*t;
const smooth=(e0,e1,x)=>{const t=clamp((x-e0)/(e1-e0),0,1);return t*t*(3-2*t);};
function mulberry32(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
function hash3(x,y,z,s){let h=x*374761393+y*668265263+z*2147483647+s*40503;h=(h^(h>>>13))>>>0;h=Math.imul(h,1274126177);return((h^(h>>>16))>>>0)/4294967296;}
function vnoise(x,y,z,s){const xi=Math.floor(x),yi=Math.floor(y),zi=Math.floor(z),xf=x-xi,yf=y-yi,zf=z-zi;
  const u=xf*xf*(3-2*xf),v=yf*yf*(3-2*yf),w=zf*zf*(3-2*zf);
  const c000=hash3(xi,yi,zi,s),c100=hash3(xi+1,yi,zi,s),c010=hash3(xi,yi+1,zi,s),c110=hash3(xi+1,yi+1,zi,s),
        c001=hash3(xi,yi,zi+1,s),c101=hash3(xi+1,yi,zi+1,s),c011=hash3(xi,yi+1,zi+1,s),c111=hash3(xi+1,yi+1,zi+1,s);
  const x00=lerp(c000,c100,u),x10=lerp(c010,c110,u),x01=lerp(c001,c101,u),x11=lerp(c011,c111,u);
  return lerp(lerp(x00,x10,v),lerp(x01,x11,v),w);}
function fbm(x,y,z,oct,s){let a=0,f=1,amp=0.5,n=0;for(let i=0;i<oct;i++){a+=amp*vnoise(x*f,y*f,z*f,s+i*17);n+=amp;f*=2;amp*=0.5;}return a/n;}

/* ============ block defs ============ */
const AIR=0,GRASS=1,DIRT=2,STONE=3,COBBLE=4,LOG=5,PLANKS=6,SAND=7,WATER=8,LEAVES=9,COAL=10,IRON=11,SNOW=12,GOLD=13;
const BLOCKS={
  1:{name:'草ブロック',top:'#6f9e3c',side:'#8a5a2b',bottom:'#8a5a2b',kind:'grass',sw:'grass'},
  2:{name:'土',top:'#8a5a2b',side:'#8a5a2b',bottom:'#8a5a2b',kind:'solid'},
  3:{name:'石',top:'#7f838b',side:'#7f838b',bottom:'#7f838b',kind:'solid'},
  4:{name:'丸石',top:'#87898f',side:'#87898f',bottom:'#87898f',kind:'solid'},
  5:{name:'原木',top:'#a07a44',side:'#6b4a2a',bottom:'#a07a44',kind:'log'},
  6:{name:'板材',top:'#b3854a',side:'#b3854a',bottom:'#b3854a',kind:'solid'},
  7:{name:'砂',top:'#d6c48a',side:'#d6c48a',bottom:'#d6c48a',kind:'solid'},
  8:{name:'水',top:'#34b1c9',side:'#34b1c9',bottom:'#34b1c9',kind:'water'},
  9:{name:'葉',top:'#3f7d2a',side:'#3f7d2a',bottom:'#3f7d2a',kind:'leaves'},
  10:{name:'石炭鉱石',top:'#5b5f66',side:'#5b5f66',bottom:'#5b5f66',kind:'ore',dots:'#1e1e22'},
  11:{name:'鉄鉱石',top:'#5b5f66',side:'#5b5f66',bottom:'#5b5f66',kind:'ore',dots:'#d9a06a'},
  12:{name:'雪',top:'#eef1f5',side:'#eef1f5',bottom:'#eef1f5',kind:'solid'},
  13:{name:'金鉱石',top:'#5b5f66',side:'#5b5f66',bottom:'#5b5f66',kind:'ore',dots:'#e8c34a'},
};
const PLACEABLE=[GRASS,DIRT,STONE,COBBLE,LOG,PLANKS,SAND,LEAVES,SNOW,GOLD];
const HOTBAR=[GRASS,DIRT,STONE,COBBLE,LOG,PLANKS,SAND,LEAVES,SNOW];

const isOpaque=b=>b!==AIR&&b!==WATER;
const isSolid=b=>b!==AIR&&b!==WATER;

/* ============ texture atlas ============ */
function makeTex(){
  const T=16,S=64,TOP=0,SIDE=1,BOT=2;
  const cv=document.createElement('canvas');cv.width=cv.height=T*T;
  const g=cv.getContext('2d');
  const rnd=mulberry32(12345);const rng=()=>(rnd()-.5)*2;
  function base(id,c){g.fillStyle=c;g.fillRect(id*T,0,T,T);}
  function noise(id,a){for(let x=0;x<T;x++)for(let y=0;y<T;y++){const v=(rng()*a)|0;if(v){g.fillStyle=`rgba(${v>0?255:0},${v>0?255:0},${v>0?255:0},${Math.abs(v)/255})`;g.fillRect(id*T+x,y,1,1);}}}
  function speck(id,cols,a){for(let x=0;x<T;x++)for(let y=0;y<T;y++)if(rnd()<a){const c=cols[(rnd()*cols.length)|0];g.fillStyle=c;g.fillRect(id*T+x,y,1,1);}}
  function grassTop(id){base(id,'#6f9e3c');speck(id,['#5f8f33','#7fb04a','#638f30','#84b751'],.22);}
  function dirtSided(id){base(id,'#8a5a2b');noise(id,26);speck(id,['#6e4722','#a06e3d'],.14);
    for(let x=0;x<T;x++){for(let y=0;y<3;y++){const v=rng()*26|0;if(v)g.fillStyle=`rgba(${v>0?120:40},${v>0?160:70},${v>0?60:30},.5)`;g.fillRect(id*T+x,y,1,1);}}}
  function grassSide(id){dirtSided(id);for(let x=0;x<T;x++){for(let y=0;y<3+((rnd()*3)|0);y++){g.fillStyle=`rgba(${90+rng()*40|0},${140+rng()*40|0},${60+rng()*30|0},1)`;g.fillRect(id*T+x,y,1,1);}}}
  function grassBot(id){base(id,'#8a5a2b');noise(id,26);}
  function stone(id){base(id,'#7f838b');noise(id,16);speck(id,['#6a6e75','#91959c'],.1);}
  function cobble(id){base(id,'#75777d');for(let x=0;x<T;x+=4)for(let y=0;y<T;y+=4){const v=rng()*26|0;g.fillStyle=v>0?`rgba(${150+v},${150+v},${150+v},.5)`:`rgba(0,0,0,.3)`;g.fillRect(id*T+x,y,1,1);}noise(id,14);}
  function logTop(id){base(id,'#a07a44');g.strokeStyle='#7a5a30';for(let r=1;r<=3;r++){g.beginPath();g.arc(id*T+T/2,T/2,r*2.2,0,7);g.stroke();}noise(id,12);}
  function logSide(id){base(id,'#6b4a2a');for(let x=0;x<T;x+=3){const d=8+x*4;g.fillStyle=`rgb(${d},${(d*.7)|0},${(d*.4)|0})`;g.fillRect(id*T+x,0,1,T);}noise(id,10);}
  function planks(id){base(id,'#b3854a');g.fillStyle='#8a6433';for(let y=0;y<T;y+=4)g.fillRect(id*T,y,T,1);for(let x=0;x<T;x+=6){g.fillStyle='#8a6433';g.fillRect(id*T+x,0,1,T);}noise(id,12);}
  function sand(id){base(id,'#d6c48a');noise(id,16);}
  function water(id){base(id,'#34b1c9');for(let y=0;y<T;y+=4)for(let x=0;x<T;x+=2){if(rnd()<.35){g.fillStyle='rgba(120,225,255,.5)';g.fillRect(id*T+x,y,1,1);}}}
  function leaves(id){base(id,'#2f5f1e');speck(id,['#3f7d2a','#54a03a','#264d18','#66b84a'],.55);}
  function ore(id,dots){stone(id);for(let i=0;i<5;i++){const x=1+(rnd()*12|0),y=1+(rnd()*12|0);g.fillStyle=dots;g.fillRect(id*T+x,y,2,2);g.fillStyle='rgba(255,255,255,.15)';g.fillRect(id*T+x,y,1,1);}}

  grassTop(GRASS);grassSide(GRASS);grassBot(GRASS);
  base(DIRT+TOP,'#8a5a2b');base(DIRT+SIDE,'#8a5a2b');base(DIRT+BOT,'#8a5a2b');noise(DIRT,26);
  stone(STONE);cobble(COBBLE);logTop(LOG);logSide(LOG);logTop(LOG);
  planks(PLANKS);sand(SAND);water(WATER);leaves(LEAVES);
  ore(COAL,'#1e1e22');ore(IRON,'#d9a06a');
  base(SNOW+TOP,'#eef1f5');noise(SNOW+TOP,8);base(SNOW+SIDE,'#eef1f5');base(SNOW+BOT,'#eef1f5');
  ore(GOLD,'#e8c34a');

  const tex=new THREE.CanvasTexture(cv);tex.magFilter=THREE.NearestFilter;tex.minFilter=THREE.NearestFilter;
  tex.generateMipmaps=false;tex.colorSpace=THREE.SRGBColorSpace;
  const cell=id=>{const r=(id/S)|0,c=(id%S)/S;return{u0:c/S,v0:1-(r+1)/S,u1:(c+1)/S,v1:1-r/S};};
  return{tex,cell};
}

/* ============ setup ============ */
let renderer,scene,camera,sky,sunDir,atlas,solidMat,waterMat,waterGeo;
let blocks,waterBlocks,wl,seed,terrainGroup;
let dayDur=180,dayT=0.26,dayCount=1,skyBaseY=0;
let fog,fogDay,fogNight;
const UP=new THREE.Vector3(0,1,0);

const CHUNK=16,CHUNKS=8,W=CHUNK*CHUNKS,SEA=14,MAXH=36;

function initRenderer(){
  const canvas=document.getElementById('gl');
  try{
    renderer=new THREE.WebGLRenderer({canvas,antialias:true});
  }catch(e){document.getElementById('err').classList.add('show');throw e;}
  renderer.setPixelRatio(Math.min(devicePixelRatio,2));
  renderer.setSize(innerWidth,innerHeight);
  renderer.outputColorSpace=THREE.SRGBColorSpace;
  scene=new THREE.Scene();
  camera=new THREE.PerspectiveCamera(75,innerWidth/innerHeight,0.1,1000);
  scene.fog=fog=new THREE.Fog(0x9fd0e6,60,150);
  fogDay=new THREE.Color(0x9fd0e6);fogNight=new THREE.Color(0x0a1020);
}

function initSky(){
  sky=new Sky();sky.scale.setScalar(10000);scene.add(sky);
  const u=sky.material.uniforms;
  u.turbidity.value=6;u.rayleigh.value=2.4;u.mieCoefficient.value=0.005;u.mieDirectionalG.value=0.85;
  u.sunPosition.value.set(0,1,0);
}

function initLights(){
  const sun=new THREE.DirectionalLight(0xffffff,2.0);sun.position.set(100,120,60);scene.add(sun);
  const hemi=new THREE.HemisphereLight(0xbfe3ff,0x4a4033,0.55);scene.add(hemi);
  scene.add(new THREE.AmbientLight(0xffffff,0.12));
  return{sun,hemi};
}

function initClouds(){
  const cvs=document.createElement('canvas');cvs.width=cvs.height=128;const g=cvs.getContext('2d');
  const r=mulberry32(77);
  for(let i=0;i<46;i++){const x=r()*128,y=r()*128,w=10+r()*34,h=6+r()*16;
    const grd=g.createRadialGradient(x,y,0,x,y,w);grd.addColorStop(0,'rgba(255,255,255,.9)');grd.addColorStop(1,'rgba(255,255,255,0)');
    g.fillStyle=grd;g.fillRect(x-w,y-h,w*2,h*2);}
  const t=new THREE.CanvasTexture(cvs);t.colorSpace=THREE.SRGBColorSpace;
  const mat=new THREE.MeshBasicMaterial({map:t,transparent:true,opacity:.62,depthWrite:false,alphaTest:.05});
  const grp=new THREE.Group();
  for(let i=0;i<14;i++){const m=new THREE.Mesh(new THREE.PlaneGeometry(60,60),mat);
    m.position.set((Math.random()-.5)*300,MAXH+12+Math.random()*8,(Math.random()-.5)*300);
    m.rotation.x=-Math.PI/2;m.userData.sp=0.4+Math.random()*0.5;grp.add(m);}
  scene.add(grp);return{grp,mat};
}

/* ============ terrain ============ */
function heightAt(x,z){
  const cont=fbm(x*0.006,z*0.006,7.1,4,seed);
  const hills=fbm(x*0.03,z*0.03,3.3,3,seed+91);
  const ridge=Math.abs(fbm(x*0.012,z*0.012,1.7,3,seed+55)*2-1);
  let h=SEA+ (cont-0.5)*22 + (hills-0.5)*7 + ridge*9 + 3;
  return clamp(Math.round(h),1,MAXH);
}
function genWorld(){
  blocks=new Uint8Array(W*W*MAXH);waterBlocks=new Uint8Array(W*W*MAXH);wl=W*MAXH;
  const idx=(x,y,z)=>(y*W+z)*W+x;
  for(let x=0;x<W;x++)for(let z=0;z<W;z++){
    const h=heightAt(x,z);
    for(let y=1;y<=h;y++){
      let b=STONE;
      if(y>h-4) b=DIRT;
      if(y===h){
        if(h>=SEA+6) b=SNOW;
        else if(h<=SEA) b=SAND;
        else b=GRASS;
      }
      if(b===STONE){const n=fbm(x*0.08,y*0.08,z*0.08,2,seed+777);
        if(n>0.80) b=COAL; else if(n>0.76&&y<16) b=IRON; else if(n>0.74&&y<12) b=GOLD;}
      blocks[idx(x,y,z)]=b;
    }
    for(let y=h+1;y<=SEA;y++) waterBlocks[idx(x,y,z)]=WATER;
    if(h>SEA&&h<MAXH-2&&hash3(x,z,0,seed+3)<0.016) plantTree(x,h+1,z);
  }
}
function plantTree(x,y,z){
  const idx=(x,y,z)=>(y*W+z)*W+x;
  const th=4+((hash3(x,z,1,seed+31)*3)|0);
  for(let i=0;i<th;i++){const yy=y+i;if(yy<MAXH)blocks[idx(x,yy,z)]=LOG;}
  const top=y+th;
  for(let dy=-2;dy<=1;dy++)for(let dx=-2;dx<=2;dx++)for(let dz=-2;dz<=2;dz++){
    const d=Math.abs(dx)+Math.abs(dy)+Math.abs(dz);
    if(d>4|| (dx===0&&dz===0&&dy<1)) continue;
    if(Math.abs(dx)===2&&Math.abs(dz)===2&&hash3(x+dx,z+dz,dy,seed+9)<0.4) continue;
    const px=x+dx,py=top+dy,pz=z+dz;
    if(px<0||pz<0||px>=W||pz>=W||py<0||py>=MAXH) continue;
    const i=idx(px,py,pz);if(!blocks[i])blocks[i]=LEAVES;
  }
}

/* ============ meshing ============ */
let solidGeo=null,dirty=true;
function buildChunkMeshes(){
  const pos=[],norm=[],uv=[],col=[],tri=[];
  const waterPos=[],waterNorm=[],waterUV=[],waterCol=[],waterTri=[];
  const idx=(x,y,z)=>(y*W+z)*W+x;
  const get=(x,y,z)=>(x<0||y<0||z<0||x>=W||y>=MAXH||z>=W)?AIR:blocks[(y*W+z)*W+x];
  const wget=(x,y,z)=>(x<0||y<0||z<0||x>=W||y>=MAXH||z>=W)?AIR:waterBlocks[(y*W+z)*W+x];
  const FACES=[[1,[0,0,0],[1,0,0],[0,1,0]],[0,[0,1,0],[0,0,1],[1,0,0]],
    [-1,[1,0,1],[0,0,1],[0,1,0]],[1,[1,0,1],[1,0,0],[0,1,0]],
    [0,[0,0,1],[1,0,1],[0,1,0]],[1,[1,0,1],[0,0,0],[0,1,0]]];

  for(let y=0;y<MAXH;y++)for(let z=0;z<W;z++)for(let x=0;x<W;x++){
    const b=blocks[idx(x,y,z)];if(b===AIR)continue;
    const def=BLOCKS[b],ci=(b-1)*3;
    const isL=b===LEAVES;
    for(let fi=0;fi<6;fi++){
      const d=FACES[fi][0],axis=fi>>1;
      const nb=get(x+((axis===0)?d:0),y+((axis===1)?d:0),z+((axis===2)?d:0));
      if(isL){if(isOpaque(nb))continue;}
      else if(isOpaque(nb))continue;
      let face=fi;
      if(def.kind==='grass'){face=axis===1?(d>0?ci+TOP:ci+BOT):ci+SIDE;}
      else if(def.kind==='log'){face=axis===1?ci+TOP:ci+SIDE;}
      else face=ci+TOP;
      const u=atlas.cell(face);
      const o=pos.length/3;
      const [a,b2,c]=FACES[fi][1],e2,f,g2=FACES[fi][2];
      const cx=(d>0)?1:0;
      const corners=[[a,b2,c],[a,b2,c],a2,b2,c2].map(()=>0);
      const P=[[a,b2,c],[a,b2,c],[e2,f,g2],[e2,f,g2]];
      const CC=[[a,b2,c],[e2,f,g2],[a,b2,c],[e2,f,g2]];
      const C=[
        [a,b2,c],
        [e2,f,g2],
        [a,b2,c],
        [e2,f,g2]];
      // build 4 corners properly
      const A=[a,b2,c], B=[a,b2,c], Cc=[e2,f,g2], D=[e2,f,g2];
      // recompute corners explicitly
      const c0=[a,b2,c], c1=[a,b2,c], c2=[e2,f,g2], c3=[e2,f,g2];
      // The face corners from data: origin O, edge e, edge f
      const O=[a,b2,c], E=[e2,f,g2], Fv=[FACES[fi][1][0]*0+0,0,0];
      // simpler: use stored edges
      const EO=FACES[fi][1], EE=FACES[fi][2], EF=FACES[fi][3];
      const p0=[EO[0],EO[1],EO[2]];
      const p1=[EO[0]+EF[0],EO[1]+EF[1],EO[2]+EF[2]];
      const p2=[EO[0]+EF[0]+EE[0],EO[1]+EF[1]+EE[1],EO[2]+EF[2]+EE[2]];
      const p3=[EO[0]+EE[0],EO[1]+EE[1],EO[2]+EE[2]];
      const pts=[p0,p1,p2,p3];
      for(const p of pts){pos.push(x+p[0],y+p[1],z+p[2]);norm.push(d*(axis===0?1:0),d*(axis===1?1:0),d*(axis===2?1:0));}
      uv.push(u.u0,u.v0,u.u1,u.v0,u.u1,u.v1,u.u0,u.v1);
      const sh=[0.55,0.55,0.55,0.55];
      if(axis===1)sh[0]=sh[1]=sh[2]=sh[3]=(d>0)?1.0:0.5;
      else if(axis===0)sh[0]=sh[1]=sh[2]=sh[3]=0.72;
      else sh[0]=sh[1]=sh[2]=sh[3]=0.85;
      for(const s of sh)col.push(s,s,s);
      tri.push(o,o+1,o+2,o,o+2,o+3);
    }
    // water top
    if(b===WATER){
      if(get(x,y+1,z)!==WATER){
        const u=atlas.cell((WATER-1)*3+TOP);const o=waterPos.length/3;
        const yy=SEA+0.9;
        waterPos.push(x,yy,z, x+1,yy,z, x+1,yy,z+1, x,yy,z+1);
        waterNorm.push(0,1,0,0,1,0,0,1,0,0,1,0);
        waterUV.push(u.u0,u.v0,u.u1,u.v0,u.u1,u.v1,u.u0,u.v1);
        waterCol.push(1,1,1,1,1,1,1,1,1,1,1,1);
        waterTri.push(o,o+1,o+2,o,o+2,o+3);
      }
    }
  }
  solidGeo=new THREE.BufferGeometry();
  solidGeo.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));
  solidGeo.setAttribute('normal',new THREE.Float32BufferAttribute(norm,3));
  solidGeo.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));
  solidGeo.setAttribute('color',new THREE.Float32BufferAttribute(col,3));
  solidGeo.setIndex(tri);
  if(terrainGroup.children[0])terrainGroup.children[0].geometry.dispose();
  const m=new THREE.Mesh(solidGeo,solidMat);terrainGroup.add(m);
  if(waterGeo)waterGeo.dispose();
  waterGeo=new THREE.BufferGeometry();
  waterGeo.setAttribute('position',new THREE.Float32BufferAttribute(waterPos,3));
  waterGeo.setAttribute('normal',new THREE.Float32BufferAttribute(waterNorm,3));
  waterGeo.setAttribute('uv',new THREE.Float32BufferAttribute(waterUV,2));
  waterGeo.setAttribute('color',new THREE.Float32BufferAttribute(waterCol,3));
  waterGeo.setIndex(waterTri);
  if(terrainGroup.children[1])terrainGroup.children[1].geometry.dispose();
  const wm=new THREE.Mesh(waterGeo,waterMat);terrainGroup.add(wm);
  dirty=false;
}
function rebuild(){buildChunkMeshes();}

/* ============ controls / physics ============ */
let yaw=0,pitch=0;const keys=new Set();let sprint=false;
const vel=new THREE.Vector3();const P=new THREE.Vector3();const eyeH=1.62;
let spawnY=SEA+1;
function getBlock(x,y,z){if(x<0||y<0||z<0||x>=W||y>=MAXH||z>=W)return STONE;return blocks[(y*W+z)*W+x];}
function setBlock(x,y,z,v){if(x<0||y<0||z<0||x>=W||y>=MAXH||z>=W)return;blocks[(y*W+z)*W+x]=v;dirty=true;}
function collides(x,y,z){const i=(Math.floor(y)*W+Math.floor(z))*W+Math.floor(x);return blocks[i]===WATER?false:(blocks[i]!==AIR);}
function collidesAABB(p){const r=0.3,fe=0.001;
  const x0=Math.floor(p.x-r+fe),x1=Math.floor(p.x+r-fe);
  const y0=Math.floor(p.y+fe),y1=Math.floor(p.y+1.8-fe);
  const z0=Math.floor(p.z-r+fe),z1=Math.floor(p.z+r-fe);
  for(let y=y0;y<=y1;y++)for(let z=z0;z<=z1;z++)for(let x=x0;x<=x1;x++)if(x<0||y<0||z<0||x>=W||y>=MAXH||z>=W||collides(x,y,z))return true;
  return false;}
function spawn(){let x=W/2|0,z=W/2|0;for(let i=0;i<80;i++){const h=heightAt(x,z);if(h>SEA){P.set(x+0.5,h+1.2,z+0.5);spawnY=h+1;break;}x=W/2+i|0;z=W/2-i|0;}
  if(P.y<1)P.set(W/2+0.5,SEA+6,W/2+0.5);}

/* ============ picking ============ */
function pick(){
  const dir=new THREE.Vector3();camera.getWorldDirection(dir);
  const o=camera.position;let px=Math.floor(o.x),py=Math.floor(o.y),pz=Math.floor(o.z);
  const sx=Math.sign(dir.x),sy=Math.sign(dir.y),sz=Math.sign(dir.z);
  const ddx=Math.abs(1/dir.x),ddy=Math.abs(1/dir.y),ddz=Math.abs(1/dir.z);
  let tx=(sx>0?px+1-o.x:o.x-px)*ddx, ty=(sy>0?py+1-o.y:o.y-py)*ddy, tz=(sz>0?pz+1-o.z:o.z-pz)*ddz;
  let face=[0,0,0];
  for(let i=0;i<200;i++){
    if(tx<ty&&tx<tz){px+=sx;tx+=ddx;face=[-sx,0,0];}
    else if(ty<tz){py+=sy;ty+=ddy;face=[0,-sy,0];}
    else{pz+=sz;tz+=ddz;face=[0,0,-sz];}
    if(px<0||py<0||pz<0||px>=W||py>=MAXH||pz>=W)break;
    const b=blocks[(py*W+pz)*W+px];if(b!==AIR&&b!==WATER)return{block:[px,py,pz],prev:[px+face[0],py+face[1],pz+face[2]]};
  }
  return null;
}

/* ============ day / night ============ */
let lights,clouds;
function updateDay(dt){
  dayT+=dt/dayDur;
  while(dayT>=1){dayT-=1;dayCount++;document.getElementById('day').textContent='DAY '+dayCount;}
  const ang=dayT*2*Math.PI;const el=Math.sin(ang);
  sunDir.set(Math.cos(ang)*0.7,el,Math.sin(ang)*0.3).normalize();
  sky.material.uniforms.sunPosition.value.copy(sunDir).multiplyScalar(1000);
  const dl=clamp(el*3,-1,1);
  lights.sun.intensity=clamp(el,0,1)*2.4;
  lights.hemi.intensity=0.45+0.35*clamp(el,0,1);
  const day=smooth(0.05,0.2,el),tw=clamp(Math.exp(-Math.abs(el)/0.06),0,1);
  const hz=new THREE.Color().copy(fogNight).lerp(fogDay,day).lerp(new THREE.Color(0xff9a5a),tw*0.55);
  fog.color.copy(hz);
  const ph=phaseName(dayT);
  document.getElementById('phase').textContent=ph;
  document.getElementById('clock').classList.toggle('night',el<0);
  const hh=Math.floor(((dayT*24+6)%24)),mm=Math.floor((dayT*24*60)%60);
  document.getElementById('time').textContent=String(hh).padStart(2,'0')+':'+String(mm).padStart(2,'0');
  document.getElementById('daybar').style.width=(dayT*100)+'%';
  const under=camera.position.y<SEA-0.5;
  fog.near=under?2:60;fog.far=under?46:150;
  const cc=under?new THREE.Color(0x2b6f7e):hz;fog.color.copy(cc);
  renderer.setClearColor(cc);
}
function phaseName(t){if(t<0.22)return'☀ 昼';if(t<0.32)return'🌅 日没';if(t<0.68)return'🌙 夜';if(t<0.78)return'🌄 夜明け';return'☀ 昼';}

/* ============ interaction ============ */
let highlight,selId=1,locked=false;
function initHighlight(){
  const box=new THREE.BoxGeometry(1.002,1.002,1.002);
  const edges=new THREE.EdgesGeometry(box);
  highlight=new THREE.LineSegments(edges,new THREE.LineBasicMaterial({color:0xf6d67a,transparent:true,opacity:.9}));
  highlight.visible=false;scene.add(highlight);
}
function breakBlock(){const h=pick();if(h){const[x,y,z]=h.block;if(y<=0)return;setBlock(x,y,z,AIR);rebuild();}}
function placeBlock(){const h=pick();if(h){const[x,y,z]=h.prev;if(x<0||y<0||z<0||x>=W||y>=MAXH||z>=W)return;
  if(blocks[(y*W+z)*W+x]!==AIR&&blocks[(y*W+z)*W+x]!==WATER)return;
  if(Math.floor(P.x)===x&&Math.floor(P.z)===z&&(Math.floor(P.y)===y||Math.floor(P.y+1)===y))return;
  setBlock(x,y,z,selId);rebuild();}}
function select(i){selId=HOTBAR[i];document.querySelectorAll('.slot').forEach((s,j)=>s.classList.toggle('active',j===i));
  const d=BLOCKS[selId];document.getElementById('curName').textContent=d.name;
  document.getElementById('sw').style.setProperty('--sw',d.sw==='grass'?'#7fbf4d':d.top);}

/* ============ UI ============ */
function buildHotbar(){
  const hb=document.getElementById('hotbar');hb.innerHTML='';
  HOTBAR.forEach((id,i)=>{const d=BLOCKS[id];const s=document.createElement('div');s.className='slot'+(i===0?' active':'');
    s.style.setProperty('--sw',d.sw==='grass'?'#7fbf4d':d.top);s.style.setProperty('--sw2','#5f9c39');
    s.innerHTML=`<span class="num">${i+1}</span><div class="cube">${d.sw==='grass'?'<i></i>':''}</div><span class="nm">${d.name}</span>`;
    s.onclick=()=>{if(locked)select(i);};hb.appendChild(s);});
  select(0);
}
function bindControls(){
  addEventListener('keydown',e=>{
    if(e.code==='Space')e.preventDefault();
    keys.add(e.code);
    if(e.code==='ShiftLeft'||e.code==='ShiftRight')sprint=true;
    if(e.code.startsWith('Digit')){const n=+e.code.slice(5);if(n>=1&&n<=HOTBAR.length)select(n-1);}
  });
  addEventListener('keyup',e=>{keys.delete(e.code);if(e.code.startsWith('Shift'))sprint=false;});
  addEventListener('wheel',e=>{if(!locked)return;const i=HOTBAR.indexOf(selId);let n=(i+(e.deltaY>0?1:-1)+HOTBAR.length)%HOTBAR.length;select(n);});
  addEventListener('click',()=>{if(!locked){document.getElementById('gl').requestPointerLock();}},{capture:true});
  addEventListener('contextmenu',e=>e.preventDefault());
  addEventListener('mousedown',e=>{if(!locked)return;if(e.button===0)breakBlock();else if(e.button===2)placeBlock();});
  addEventListener('mousemove',e=>{if(!locked)return;const s=0.0022;yaw-=e.movementX*s;pitch=clamp(pitch-e.movementY*s,-1.56,1.56);});
  document.addEventListener('pointerlockchange',()=>{locked=document.pointerLockElement===document.getElementById('gl');document.body.classList.toggle('locked',locked);});
  document.getElementById('regen').onclick=()=>{seed=Math.floor(Math.random()*1e6);document.getElementById('seed').value=seed;genWorld();rebuild();spawn();};
  document.getElementById('help').onclick=()=>document.getElementById('start').classList.remove('gone');
  document.getElementById('dice').onclick=()=>{seed=Math.floor(Math.random()*1e6);document.getElementById('seed').value=seed;};
  document.getElementById('play').onclick=()=>{seed=+document.getElementById('seed').value||Math.floor(Math.random()*1e6);genWorld();rebuild();spawn();document.getElementById('start').classList.add('gone');document.getElementById('gl').requestPointerLock();};
}

/* ============ loop ============ */
let last=performance.now();
function loop(now){
  const dt=Math.min((now-last)/1000,0.05);last=now;
  updateDay(dt);
  clouds.grp.children.forEach(m=>{m.position.x+=m.userData.sp*dt;if(m.position.x>160)m.position.x=-160;});
  waterMat.uniforms.uTime.value=now*0.001;

  // movement
  const fwd=new THREE.Vector3(-Math.sin(yaw),0,-Math.cos(yaw));
  const right=new THREE.Vector3(Math.cos(yaw),0,-Math.sin(yaw));
  const mv=new THREE.Vector3();
  if(keys.has('KeyW'))mv.add(fwd);if(keys.has('KeyS'))mv.sub(fwd);
  if(keys.has('KeyD'))mv.add(right);if(keys.has('KeyA'))mv.sub(right);
  if(mv.lengthSq())mv.normalize();
  const under=camera.position.y<SEA-0.5;
  const speed=(sprint?7.2:4.6)*(under?0.55:1);
  vel.x=mv.x*speed;vel.z=mv.z*speed;
  const grounded=collidesAABB(new THREE.Vector3(P.x,P.y-0.02,P.z));
  if(under){
    vel.y=keys.has('Space')?3.2:(keys.has('KeyC')?-3:0.3);
  }else{
    vel.y-=24*dt;if(grounded&&vel.y<0)vel.y=-0.5;
    if(keys.has('Space')&&grounded)vel.y=8.4;
  }
  P.x+=vel.x*dt;
  if(collidesAABB(P)){P.x-=vel.x*dt;vel.x=0;}
  P.z+=vel.z*dt;
  if(collidesAABB(P)){P.z-=vel.z*dt;vel.z=0;}
  P.y+=vel.y*dt;
  if(collidesAABB(P)){if(vel.y<0){P.y=Math.floor(P.y)+1;}else if(vel.y>0){P.y=Math.ceil(P.y)-1.8;}vel.y=0;}
  if(P.y<-10){P.set(W/2+0.5,spawnY,W/2+0.5);vel.set(0,0,0);}

  camera.position.set(P.x,P.y+eyeH,P.z);
  camera.rotation.order='YXZ';camera.rotation.y=yaw;camera.rotation.x=pitch;
  camera.rotation.z=under?0.02*Math.sin(now*0.002):0;

  const h=pick();
  if(h&&h.prev[0]>=0&&h.prev[1]>=0&&h.prev[2]>=0){highlight.position.set(h.prev[0]+0.5,h.prev[1]+0.5,h.prev[2]+0.5);highlight.visible=true;}
  else highlight.visible=false;

  if(dirty)rebuild();

  document.getElementById('coords').textContent=`${Math.floor(P.x)} ${Math.floor(P.y)} ${Math.floor(P.z)}`;
  let cnt=0;for(let i=0;i<blocks.length;i++)if(blocks[i]!==AIR)cnt++;
  document.getElementById('blocks').textContent=cnt.toLocaleString();

  renderer.render(scene,camera);
  requestAnimationFrame(loop);
}
addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);});

/* ============ boot ============ */
initRenderer();
atlas=makeTex();
solidMat=new THREE.MeshLambertMaterial({map:atlas.tex,vertexColors:true});
waterMat=new THREE.MeshStandardMaterial({map:atlas.tex,transparent:true,opacity:0.72,roughness:0.15,metalness:0.05,side:THREE.DoubleSide});
waterMat.onBeforeCompile=sh=>{sh.uniforms.uTime={value:0};
  sh.vertexShader='uniform float uTime;\n'+sh.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\n transformed.y += sin(position.x*2.0+uTime*2.0)*0.025 + cos(position.z*2.5+uTime*1.7)*0.025;');
};
skyBaseY=0;initSky();lights=initLights();clouds=initClouds();initHighlight();
terrainGroup=new THREE.Group();scene.add(terrainGroup);
buildHotbar();bindControls();
seed=2048;genWorld();rebuild();spawn();
document.getElementById('seed').value=seed;
requestAnimationFrame(loop);
</script>
</body>
</html>
```

## 遊び方のポイント

- **世界に入る**を押すとマウスがロックされ、視点操作が有効になります（**Esc**で解除）。
- **WASD**で移動、**Space**でジャンプ、**Shift**で走る。水中では浮上・沈降が切り替わり、水面でゆっくり泳げます。
- **左クリック**でブロック破壊、**右クリック**で設置。十字の中心をねらってください。
- **1〜9キー / ホイール / クリック**でホットバーのブロックを選択。
- 地形は**シード値**で生成され、丘・砂浜・浅瀬の海・木・鉱脈（石炭・鉄・金）が自動配置されます。右上の**地形再生成**で毎回新しい世界に。
- **昼夜サイクル**が動き、日没・夜明けで空と霧の色が変化します。

## 中身の技術メモ

- ブロックは3D配列で管理し、16³チャンクを1メッシュに集約して描画（壊す/置くたびに再メッシュ）。
- 16×16の**ピクセルアートなテクスチャアトラス**をCanvasで生成し、Nearest補間でブロックの質感を出しています。面ごとに色を軽く変えて「光の方向感」を演出。
- Three.js の `Sky` で実際の太陽高度に基づく空を再現、雲は半透明のシートで流しています。

`<canvas id="gl">` の WebGL 起動失敗時はエラー画面が出ます（PCブラウザ推奨）。