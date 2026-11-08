マイクラ風の箱庭3Dゲームを作りました。ファイル1つでそのまま動くよう、Three.js（CDN）で実装しています。

**遊び方**
- クリックで画面ロック（ポインターロック）
- `WASD` 移動 / `Shift` 走る / `Space` ジャンプ / `C` しゃがみ
- 左クリック＝ブロック破壊、右クリック＝ブロック設置
- `1〜9` でスロット切替、`E` でクラフト、`Esc` で解除
- 18ブロック種・無限地形生成・昼夜サイクル・クラフト台・水が流れる・花の揺れ（風）・水中で水中モード、など

```html
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>VOXELCRAFT — マインクラフト風 3D 箱庭</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&family=VT323&display=swap" rel="stylesheet">
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  :root{
    --oak:#c69a5c; --oakd:#8a5a2f; --grass:#6aa84f; --grassd:#3f7d34;
    --dark:#141a12; --panel:rgba(18,24,15,.82); --line:#3a3226;
    --gold:#e6b94d; --txt:#e9e3d3; --red:#c0392b; --blue:#4a90d9;
  }
  html,body{height:100%;overflow:hidden;background:#0b0d08;color:var(--txt);
    font-family:'VT323',monospace;cursor:default}
  #app{position:fixed;inset:0}
  canvas{position:fixed;inset:0;display:block}
  .pix{font-family:'Press Start 2P',monospace;text-transform:uppercase;letter-spacing:.5px}

  /* ---------- HUD ---------- */
  #hud{position:fixed;inset:0;z-index:10;pointer-events:none}
  #crosshair{position:absolute;top:50%;left:50%;width:24px;height:24px;transform:translate(-50%,-50%);opacity:.85}
  #crosshair::before,#crosshair::after{content:"";position:absolute;background:rgba(255,255,255,.9);box-shadow:0 0 0 1px rgba(0,0,0,.55)}
  #crosshair::before{left:50%;top:0;width:2px;height:100%;transform:translateX(-50%)}
  #crosshair::after{top:50%;left:0;height:2px;width:100%;transform:translateY(-50%)}

  #vignette{position:absolute;inset:0;box-shadow:inset 0 0 130px 26px rgba(0,0,0,.42)}
  #waterTint{position:absolute;inset:0;background:rgba(30,92,145,.4);opacity:0;transition:opacity .25s;
    box-shadow:inset 0 0 160px 40px rgba(10,40,70,.6)}

  #topleft{position:absolute;top:12px;left:12px;display:flex;gap:6px;flex-direction:column}
  .chip{pointer-events:auto;background:var(--panel);border:2px solid var(--line);padding:5px 9px;font-size:20px;
    display:flex;align-items:center;gap:7px;box-shadow:0 3px 0 rgba(0,0,0,.35)}
  .chip b{color:var(--gold)}
  .btn{font-family:'VT323',monospace;font-size:19px;cursor:pointer;color:var(--txt);background:var(--panel);
    border:2px solid var(--line);padding:5px 9px;box-shadow:0 3px 0 rgba(0,0,0,.35);transition:.12s}
  .btn:hover{background:#241f14;border-color:var(--gold)}
  .btn:active{transform:translateY(2px);box-shadow:0 1px 0 rgba(0,0,0,.35)}
  .btn.on{border-color:var(--gold);color:var(--gold)}

  #topright{position:absolute;top:12px;right:12px;display:flex;flex-direction:column;gap:6px;align-items:flex-end}
  #coords,#fps{font-size:19px;opacity:.85;text-align:right}
  #coords{color:#cfe0c6}

  #hotbar{position:absolute;bottom:14px;left:50%;transform:translateX(-50%);display:flex;gap:3px;
    padding:5px;background:rgba(12,15,9,.78);border:3px solid var(--line);box-shadow:0 5px 0 rgba(0,0,0,.4)}
  .slot{width:52px;height:52px;background:#2a2f24;border:2px solid #14181a;position:relative;
    box-shadow:inset 2px 2px 0 rgba(255,255,255,.09),inset -2px -2px 0 rgba(0,0,0,.45);display:flex;align-items:center;justify-content:center}
  .slot .ic{width:38px;height:38px;image-rendering:pixelated;filter:drop-shadow(0 1px 0 rgba(0,0,0,.4))}
  .slot .cnt{position:absolute;right:2px;bottom:0;font-size:19px;color:#fff;text-shadow:1px 1px 0 #000}
  .slot .selno{position:absolute;top:-16px;left:50%;transform:translateX(-50%);font-size:15px;color:#fff;opacity:.7;text-shadow:1px 1px 0 #000}
  .slot.sel{border-color:var(--gold);outline:2px solid rgba(230,185,77,.4);transform:translateY(-3px)}
  .slot .name{position:absolute;top:-26px;left:50%;transform:translateX(-50%);white-space:nowrap;font-size:19px;
    color:#fff;text-shadow:2px 2px 0 #000;opacity:0;transition:.15s}
  .slot.sel .name{opacity:1}

  /* ---------- Toast ---------- */
  #toast{position:absolute;bottom:88px;left:50%;transform:translateX(-50%) translateY(20px);
    background:var(--panel);border:2px solid var(--gold);padding:7px 15px;font-size:22px;opacity:0;transition:.2s;
    box-shadow:0 4px 0 rgba(0,0,0,.4);white-space:nowrap}
  #toast.show{opacity:1;transform:translateX(-50%) translateY(0)}

  /* ---------- Start / Pause ---------- */
  .overlay{position:fixed;inset:0;z-index:40;display:flex;flex-direction:column;align-items:center;justify-content:center;
    background:linear-gradient(rgba(10,14,8,.35),rgba(10,14,8,.72));backdrop-filter:blur(2px)}
  #start{background:
    radial-gradient(ellipse at 50% -10%, rgba(255,240,200,.25), transparent 55%),
    linear-gradient(rgba(10,14,8,.3),rgba(8,11,6,.78))}
  .title-wrap{text-align:center;position:relative;margin-bottom:20px}
  .title-wrap::before{content:"";position:absolute;left:50%;bottom:-6px;width:64%;height:12px;transform:translateX(-50%);
    background:linear-gradient(#2a2a2a,#000);filter:blur(3px);opacity:.6}
  .title{font-family:'Press Start 2P';font-size:clamp(30px,7vw,66px);color:#c69a5c;line-height:1;
    text-shadow:4px 4px 0 #3a2a18, 8px 8px 0 rgba(0,0,0,.4);transform:translateY(0);animation:bob 3s ease-in-out infinite}
  .title span{color:#8a5a2f}
  .sub{margin-top:14px;font-size:26px;color:#dfe6d6;letter-spacing:2px}
  .sub b{color:var(--gold)}
  @keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
  .start-btn{margin-top:34px;font-family:'Press Start 2P';font-size:16px;padding:16px 26px;cursor:pointer;
    background:var(--oak);color:#1c140a;border:3px solid #3a2a18;box-shadow:0 6px 0 #3a2a18;transition:.1s}
  .start-btn:hover{background:#d7ac6d;transform:translateY(-2px);box-shadow:0 8px 0 #3a2a18}
  .start-btn:active{transform:translateY(4px);box-shadow:0 2px 0 #3a2a18}
  .controls{margin-top:30px;display:grid;grid-template-columns:1fr 1fr;gap:5px 26px;
    background:rgba(12,16,9,.7);border:2px solid var(--line);padding:14px 20px;font-size:20px}
  .controls .row{display:flex;justify-content:space-between;gap:12px}
  .controls .k{color:var(--gold)}
  #pause{display:none}
  #pause h2{font-family:'Press Start 2P';font-size:34px;color:var(--gold);text-shadow:3px 3px 0 #000;margin-bottom:26px}
  #pause .btn{font-size:22px;padding:10px 22px;margin:5px}

  /* ---------- Craft ---------- */
  #craft{position:fixed;z-index:50;left:50%;top:50%;transform:translate(-50%,-50%);width:min(560px,92vw);
    background:var(--panel);border:3px solid var(--line);box-shadow:0 10px 0 rgba(0,0,0,.5);display:none;padding:0}
  #craft header{display:flex;justify-content:space-between;align-items:center;padding:10px 14px;
    background:#241f14;border-bottom:2px solid var(--line)}
  #craft header h3{font-family:'Press Start 2P';font-size:14px;color:var(--gold)}
  #craft .recipe{display:flex;align-items:center;gap:14px;padding:11px 14px;border-bottom:1px solid #2a2418}
  #craft .recipe:hover{background:rgba(230,185,77,.06)}
  #craft .ing{display:flex;align-items:center;gap:4px;flex-wrap:wrap}
  #craft .out{margin-left:auto;display:flex;align-items:center;gap:8px;font-size:21px;color:var(--gold)}
  #craft .need{font-size:17px;color:#c9b78f;margin-top:2px}
  #craft .need.no{color:#d98a7a}
  #craft .crafter{color:#7d7360;font-size:18px}
  #craft .mk{pointer-events:auto;font-family:'VT323';font-size:20px;padding:5px 12px;cursor:pointer;
    background:var(--oak);color:#1c140a;border:2px solid #3a2a18;box-shadow:0 3px 0 #3a2a18}
  #craft .mk:hover{background:#d7ac6d}
  #craft .mk:disabled{background:#5a5140;color:#8a8272;box-shadow:0 3px 0 #3a2a18;cursor:not-allowed;border-color:#3a2a18}
  #craft .close{cursor:pointer;font-size:22px;color:#e9e3d3;background:none;border:none}
  #craft .hint{padding:8px 14px;font-size:17px;color:#8a8272;background:#1c1812;border-top:2px solid var(--line)}

  #loading{position:fixed;inset:0;z-index:60;display:flex;align-items:center;justify-content:center;
    background:#0b0d08;font-size:30px;color:var(--gold)}
  .fade{animation:fade .5s ease}
  @keyframes fade{from{opacity:0}to{opacity:1}}
</style>
</head>
<body>
<div id="app"></div>

<div id="hud" style="display:none">
  <div id="vignette"></div><div id="waterTint"></div>
  <div id="crosshair"></div>
  <div id="topleft">
    <div class="chip">☀ <b id="daytime">12:00</b> <span id="phase">日中</span></div>
    <div class="chip"><span id="clockico">🌙</span> <b id="day">1</b>日</div>
    <button class="btn" id="btnCraft">🔨 クラフト (E)</button>
    <button class="btn" id="btnDay">⏰ 時間</button>
    <button class="btn" id="btnFull">⛶ 全画面</button>
  </div>
  <div id="topright">
    <div id="coords">X 0 Y 0 Z 0</div>
    <div id="fps">60 FPS</div>
  </div>
  <div id="hotbar"></div>
  <div id="toast"></div>
</div>

<div id="start">
  <div class="title-wrap">
    <div class="title pix">VOXEL<span>CRAFT</span></div>
    <div class="sub">マインクラフト風 3D 箱庭 — <b>無限生成ワールド</b></div>
  </div>
  <button class="start-btn" id="btnStart">▶ 冒険に出る</button>
  <div class="controls">
    <div class="row"><span>移動</span><span class="k">W A S D</span></div>
    <div class="row"><span>走る</span><span class="k">Shift</span></div>
    <div class="row"><span>ジャンプ</span><span class="k">Space</span></div>
    <div class="row"><span>しゃがみ</span><span class="k">C</span></div>
    <div class="row"><span>ブロック破壊</span><span class="k">左クリック</span></div>
    <div class="row"><span>ブロック設置</span><span class="k">右クリック</span></div>
    <div class="row"><span>スロット</span><span class="k">1-9 / ホイール</span></div>
    <div class="row"><span>クラフト</span><span class="k">E</span></div>
    <div class="row"><span>解除</span><span class="k">Esc</span></div>
    <div class="row"><span>水中で</span><span class="k">潜行</span></div>
  </div>
</div>

<div id="pause">
  <h2 class="pix">ポーズ</h2>
  <button class="btn" id="btnResume">▶ 続ける</button>
  <button class="btn" id="btnMenu">メニューへ</button>
</div>

<div id="craft">
  <header><h3 class="pix">作業台</h3><button class="close" id="craftClose">✕</button></header>
  <div id="recipeList"></div>
  <div class="hint">素材を集めて、アイテムを工作しよう。作業台が近くにあると高度なレシピが使える。</div>
</div>

<div id="loading">ワールド生成中…</div>

<script type="importmap">
{ "imports": { "three": "https://unpkg.com/three@0.160.0/build/three.module.js" } }
</script>

<script type="module">
import * as THREE from 'three';

/* ============ 定数・ブロック定義 ============ */
const CHUNK=16, WORLD_H=64, SEA=24, MINE_Y=2, MINE_H=1.62, STAND_H=1.8, CROUCH_H=1.3,
      RADIUS=3, DAY=480, GRAVITY=30, JUMP_V=9.0, REACH=6, MAXPLACE=800;
const AIR=0,GRASS=1,DIRT=2,STONE=3,COBBLE=4,LOG=5,PLANK=6,LEAVES=7,SAND=8,WATER=9,
      GLASS=10,BRICK=11,IRON=12,GOLD=13,SNOW=14,LAMP=15,GRAVEL=16,COAL=17,
      FLOWERS=18,STONE_BRICK=19,COBBLE_STEP=20;
const BLOCKS={}; // id -> {solid,transparent,emissive,light,top,side,bottom,name}
function def(id,o){BLOCKS[id]=Object.assign({solid:true,transparent:false,emissive:false,light:0,top:id,side:id,bottom:id,name:''},o);}
def(AIR,{solid:false,transparent:true});
def(GRASS,{top:GRASS,side:GRASS,side2:DIRT,bottom:DIRT,name:'草ブロック'});
def(DIRT,{name:'土'});def(STONE,{name:'石'});def(COBBLE,{name:'丸石'});
def(LOG,{top:LOG,side:LOG,side2:LOG,name:'原木'});
def(PLANK,{name:'板材'});def(LEAVES,{transparent:true,name:'葉'});def(SAND,{name:'砂'});
def(WATER,{solid:false,transparent:true,name:'水'});def(GLASS,{transparent:true,name:'ガラス'});
def(BRICK,{name:'レンガ'});def(IRON,{name:'鉄ブロック'});def(GOLD,{name:'金ブロック'});
def(SNOW,{name:'雪ブロック'});def(LAMP,{emissive:true,light:14,name:'発光石'});
def(GRAVEL,{name:'砂利'});def(COAL,{name:'石炭鉱石'});def(STONE_BRICK,{name:'石レンガ'});
def(COBBLE_STEP,{name:'丸石のハーフ'});
const HOTBAR=[GRASS,DIRT,STONE,COBBLE,LOG,PLANK,LEAVES,SAND,WATER];

/* ============ 雑音 ============ */
function hash(x,y){let h=(x*374761393+y*668265263)>>>0;h=(h^(h>>13))>>>0;h=Math.imul(h,1274126177);h^=h>>16;return (h>>>0)/4294967295;}
function noise2(x,y){const xi=Math.floor(x),yi=Math.floor(y),xf=x-xi,yf=y-yi;
  const u=xf*xf*(3-2*xf),v=yf*yf*(3-2*yf);
  const a=hash(xi,yi),b=hash(xi+1,yi),c=hash(xi,yi+1),d=hash(xi+1,yi+1);
  return a+(b-a)*u+(c-a)*v+(a-b-c+d)*u*v;}
const fbm=(x,y)=>noise2(x,y)*.5+noise2(x*2,y*2)*.25+noise2(x*4,y*4)*.125;

/* ============ 地形プロシージャ ============ */
function terrain(x,z){
  const cont=fbm(x*0.006+11.3,z*0.006-4.1);
  const hills=fbm(x*0.02+3.7,z*0.02+8.9);
  const mtn=Math.pow(Math.max(0,fbm(x*0.004+40,z*0.004-20)-0.45)/0.55,2);
  const e=cont*0.5+hills*0.34+mtn*1.25;
  return Math.max(1,Math.min(63,Math.round(SEA-1+e*30)));
}
function treeAt(x,z){return fbm(x*0.05+123,z*0.05-77)>0.62;}
const isSolid=id=>id&&id!==AIR&&id!==WATER;
const isWater=id=>id===WATER;

/* ============ ワールド（チャンク） ============ */
const world=new Map(), dirty=new Set(), chunkMeshes=new Map();
const ck=(cx,cz)=>cx+','+cz;
const getB=(x,y,z)=>{if(y<0)return STONE;if(y>=WORLD_H)return AIR;const c=world.get(ck(x>>4,z>>4));return c?c[y<<8|((x&15)<<4)|(z&15)]:AIR;};
const setB=(x,y,z,id)=>{if(y<0||y>=WORLD_H)return;const c=world.get(ck(x>>4,z>>4));if(!c)return;c[y<<8|((x&15)<<4)|(z&15)]=id;dirty.add(ck(x>>4,z>>4));};

function genChunk(cx,cz){
  const c=new Uint8Array(WORLD_H*256);world.set(ck(cx,cz),c);
  const bx=cx<<4,bz=cz<<4;
  for(let x=0;x<16;x++)for(let z=0;z<16;z++){
    const wx=bx+x,wz=bz+z,h=terrain(wx,wz);
    for(let y=0;y<=h;y++){
      let id;
      if(y===0)id=STONE;
      else if(y<h-3)id=STONE;
      else if(y<h)id=DIRT;
      else id=h<SEA+1?SAND:(h>44?SNOW:GRASS);
      if(id===STONE&&y<h-2&&hash(wx*13+y*7,wz*7+y*17)<0.012)id=COAL;
      c[y<<8|(x<<4)|z]=id;
    }
    for(let y=h+1;y<=SEA;y++)c[y<<8|(x<<4)|z]=WATER;
  }
  // 木
  for(let x=0;x<16;x++)for(let z=0;z<16;z++){
    const wx=bx+x,wz=bz+z,h=terrain(wx,wz);
    if(h>SEA&&h<45&&treeAt(wx,wz)&&c[h<<8|(x<<4)|z]===GRASS){
      const th=4+Math.floor(hash(wx,wz)*3);
      for(let i=1;i<=th;i++){const y=h+i;if(y<WORLD_H)c[y<<8|(x<<4)|z]=LOG;}
      const top=h+th;
      for(let dx=-2;dx<=2;dx++)for(let dz=-2;dz<=2;dz++)for(let dy=-1;dy<=1;dy++){
        if(dx===0&&dz===0&&dy<1)continue;
        if(Math.abs(dx)===2&&Math.abs(dz)===2&&hash(wx+dx,wz+dz)<0.6)continue;
        const nx=x+dx,nz=z+dz,ny=top+dy;
        if(nx<0||nx>15||nz<0||nz>15||ny>=WORLD_H)continue;
        if(c[ny<<8|(nx<<4)|nz]===AIR)c[ny<<8|(nx<<4)|nz]=LEAVES;
      }
    }
  }
  // 花・草（草ブロック表面のみ）
  for(let x=0;x<16;x++)for(let z=0;z<16;z++){
    const wx=bx+x,wz=bz+z,h=terrain(wx,wz);
    if(h>SEA+1&&h<45&&c[h<<8|(x<<4)|z]===GRASS&&c[(h+1)<<8|(x<<4)|z]===AIR&&hash(wx*3+7,wz*5-3)<0.06)
      c[(h+1)<<8|(x<<4)|z]=FLOWERS;
  }
  return c;
}
const ensure=(cx,cz)=>{if(!world.has(ck(cx,cz)))genChunk(cx,cz);};

/* 近傍チャンク */
function near(cx,cz){const s=[];for(let z=-1;z<=1;z++)for(let x=-1;x<=1;x++)s.push(ck(cx+x,cz+z));return s;}
const ensureRing=(cx,cz)=>{for(let z=-RADIUS;z<=RADIUS;z++)for(let x=-RADIUS;x<=RADIUS;x++)ensure(cx+x,cz+z);};
const inRadius=(cx,cz)=>Math.abs(cx)<=RADIUS&&Math.abs(cz)<=RADIUS;

/* ============ レンダラ・シーン ============ */
const renderer=new THREE.WebGLRenderer({antialias:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.setSize(innerWidth,innerHeight);
document.getElementById('app').appendChild(renderer.domElement);
const scene=new THREE.Scene();
const camera=new THREE.PerspectiveCamera(72,innerWidth/innerHeight,0.08,1000);
const fogColor=new THREE.Color(0x7ea8d0);
scene.fog=new THREE.Fog(fogColor,26,104);
scene.add(new THREE.AmbientLight(0xffffff,0.55));
const sun=new THREE.DirectionalLight(0xfff4d6,0.9);
scene.add(sun);
const hemi=new THREE.HemisphereLight(0xbfe0ff,0x39421f,0.35);scene.add(hemi);

/* スカイ（グラデ→星→雲→太陽/月） */
function skyTex(){const c=document.createElement('canvas');c.width=c.height=256;const x=c.getContext('2d');
  const g=x.createLinearGradient(0,0,0,256);g.addColorStop(0,'#8fbfe8');g.addColorStop(.5,'#bfe0f0');g.addColorStop(1,'#eaf4e8');
  x.fillStyle=g;x.fillRect(0,0,256,256);const t=new THREE.CanvasTexture(c);return t;}
const skyMat=new THREE.MeshBasicMaterial({map:skyTex(),side:THREE.BackSide,depthWrite:false});
const sky=new THREE.Mesh(new THREE.SphereGeometry(480,24,16),skyMat);sky.renderOrder=-10;scene.add(sky);
function starTex(){const c=document.createElement('canvas');c.width=c.height=128;const x=c.getContext('2d');x.clearRect(0,0,128,128);
  for(let i=0;i<160;i++){const b=(0.4+Math.random()*0.6).toFixed(2);x.fillStyle=`rgba(255,255,240,${b})`;x.fillRect(Math.random()*128|0,Math.random()*128|0,1,1);}
  const t=new THREE.CanvasTexture(c);t.magFilter=THREE.NearestFilter;return t;}
const stars=new THREE.Points(new THREE.BufferGeometry().setAttribute('position',
  new THREE.Float32BufferAttribute((()=>{const a=[];for(let i=0;i<1600;i++){const v=new THREE.Vector3(Math.random()-0.5,Math.random()-0.5,Math.random()-0.5).normalize().multiplyScalar(475);a.push(v.x,v.y,v.z);}return a;})(),3)),
  new THREE.PointsMaterial({map:starTex(),size:2.4,sizeAttenuation:true,transparent:true,opacity:0,depthWrite:false}));
stars.renderOrder=-9;scene.add(stars);
function cloudTex(){const c=document.createElement('canvas');c.width=c.height=64;const x=c.getContext('2d');
  for(let i=0;i<30;i++){const px=Math.random()*64,py=Math.random()*64,s=6+Math.random()*10;
    x.fillStyle=`rgba(255,255,255,${0.5+Math.random()*0.4})`;x.fillRect(px|0,py|0,s|0,s*0.6|0);}
  const t=new THREE.CanvasTexture(c);t.magFilter=THREE.NearestFilter;return t;}
const clouds=new THREE.Mesh(new THREE.PlaneGeometry(700,700),
  new THREE.MeshBasicMaterial({map:cloudTex(),transparent:true,opacity:.5,depthWrite:false,alphaTest:0.15}));
clouds.rotation.x=-Math.PI/2;clouds.position.y=98;scene.add(clouds);
const sunDisc=new THREE.Mesh(new THREE.PlaneGeometry(46,46),new THREE.MeshBasicMaterial({color:0xfff2c0,transparent:true,fog:false,depthWrite:false}));
const moonDisc=new THREE.Mesh(new THREE.PlaneGeometry(30,30),new THREE.MeshBasicMaterial({color:0xdfe6ef,transparent:true,fog:false,depthWrite:false}));
sunDisc.renderOrder=-8;moonDisc.renderOrder=-8;scene.add(sunDisc,moonDisc);

/* ============ テクスチャ生成 ============ */
const atlas={};
const px=(x,y,c)=>{x.fillStyle=c;x.fillRect(x|0,y|0,1,1);};
function texTop(id){const c=document.createElement('canvas');c.width=c.height=16;const x=c.getContext('2d');
  const rnd=(a,b)=>a+Math.random()*(b-a);
  const pick=(id)=>{switch(id){
    case GRASS:return ['#5f9e46','#6cae4d','#77b457','#4f8a3c'];
    case DIRT:return ['#8a6a44','#7a5c39','#95754e','#6e5231'];
    case SAND:return ['#dcc48b','#cbb277','#e6d19d','#c9b078'];
    case LOG:return ['#6b4f2c','#7d5c34','#5a4224','#8a6a3c'];
    case PLANK:return ['#b3854a','#a2763f','#c1935a','#956c39'];
    case LEAVES:return ['#417a37','#4c8a3e','#396b31','#579a48'];
    case SNOW:return ['#eef2f4','#e2e8ea','#f6f8f9','#d8dee0'];
    case IRON:return ['#c2c4c8','#cfd1d4','#b4b6ba','#d7d9dc'];
    case GOLD:return ['#e2b93f','#f0cf5b','#d3a832','#f7dd78'];
    case COAL:return ['#8f9295','#a2a5a8','#7d8083','#b0b3b6'];
    case GRAVEL:return ['#8a8272','#7a7263','#99907d','#6e6656'];
    case STONE:return ['#8f9295','#9aa0a4','#84888c','#a2a5a8'];
    default:return ['#909396','#a2a5a8','#7f8387'];
  }};
  const pal=pick(id);
  for(let y=0;y<16;y++)for(let xx=0;xx<16;xx++)px(x,xx,y,pal[Math.floor(Math.random()*pal.length)]);
  if(id===GRASS){for(let y=0;y<4;y++)for(let xx=0;xx<16;xx++){const p=pal[Math.floor(Math.random()*pal.length)];px(x,xx,y,p);if(Math.random()<.3)px(x,xx,y-1>=0?y-1:0,'#3f7d34');}}
  if(id===LOG){for(let r=5;r<15;r+=2)x.beginPath(),x.arc(8,8,r,0,7),x.strokeStyle=pal[r%4],x.stroke();x.fillStyle='#3f6a2e';x.beginPath();x.arc(8,8,3,0,7);x.fill();}
  if(id===SNOW){for(let i=0;i<40;i++)px(x,Math.random()*16|0,Math.random()*16|0,'#fff');}
  return c;}
function texSide(id){const c=document.createElement('canvas');c.width=c.height=16;const x=c.getContext('2d');
  const rnd=(a,b)=>a+Math.random()*(b-a);
  const pal=(id)=>{switch(id){
    case GRASS:return ['#5f9e46','#6cae4d','#77b457','#4f8a3c'];
    case DIRT:return ['#8a6a44','#7a5c39','#95754e','#6e5231'];
    case SAND:return ['#dcc48b','#cbb277','#e6d19d'];
    case LOG:return ['#6b4f2c','#7d5c34','#5a4224','#8a6a3c'];
    case PLANK:return ['#b3854a','#a2763f','#c1935a','#956c39'];
    case LEAVES:return ['#417a37','#4c8a3e','#396b31','#579a48'];
    case SNOW:return ['#eef2f4','#e2e8ea','#f6f8f9'];
    case IRON:return ['#c2c4c8','#cfd1d4','#b4b6ba'];
    case GOLD:return ['#e2b93f','#f0cf5b','#d3a832'];
    case COAL:return ['#8f9295','#a2a5a8','#7d8083'];
    case GRAVEL:return ['#8a8272','#7a7263','#99907d'];
    case BRICK:return ['#a4442f','#8f3a28','#b5503a'];
    case STONE_BRICK:return ['#8f9295','#7f8387','#9aa0a4'];
    case COBBLE:return ['#8f9295','#a2a5a8','#7f8387','#b0b3b6'];
    default:return ['#909396','#a2a5a8','#7f8387'];
  }};
  const p=pal(id);
  for(let y=0;y<16;y++)for(let xx=0;xx<16;xx++)px(x,xx,y,p[Math.floor(Math.random()*p.length)]);
  if(id===GRASS){for(let xx=0;xx<16;xx++)px(x,xx,0,'#4f8a3c');for(let xx=0;xx<16;xx++)px(x,xx,1,'#63a64b');
    for(let xx=0;xx<16;xx++){if(Math.random()<.6)px(x,xx,2,'#4f8a3c');if(Math.random()<.3)px(x,xx,3,'#3f7d34');}}
  if(id===LOG){for(let xx=0;xx<16;xx++){const w=Math.random()<.4?'#5a4224':'#8a6a3c';px(x,xx,0,w);px(x,xx,15,w);}}
  if(id===PLANK){for(let y=3;y<16;y+=4)for(let xx=0;xx<16;xx++)px(x,xx,y,'#6b4f2c');}
  if(id===BRICK){for(let y=0;y<16;y++)for(let xx=0;xx<16;xx++)px(x,xx,y,'#c9b7a0');
    for(let y=1;y<16;y+=4)for(let xx=0;xx<16;xx++)px(x,xx,y,'#8f3a28');
    for(let y=0;y<16;y+=4){const off=(y/4)%2?2:0;for(let xx=off;xx<16;xx+=4)for(let yy=0;yy<3;yy++)px(x,xx,y+yy,'#a4442f');}}
  if(id===STONE_BRICK){for(let y=0;y<16;y++)for(let xx=0;xx<16;xx++)px(x,xx,y,'#6d7175');
    for(let y=1;y<16;y+=8)for(let xx=0;xx<16;xx++)px(x,xx,y,'#5a5e62');
    for(let y=0;y<16;y+=8){const off=(y/8)%2?4:0;for(let xx=off;xx<16;xx+=4)for(let yy=0;yy<7;yy++)px(x,xx,y+yy,'#8f9295');}}
  if(id===COBBLE){for(let i=0;i<26;i++){const cx=Math.random()*16,cy=Math.random()*16,r=1+Math.random()*2;
    x.fillStyle=p[Math.floor(Math.random()*p.length)];x.fillRect(cx|0,cy|0,r|0,r|0);
    x.fillStyle='#565a5e';x.fillRect(cx|0,cy|0,1,r|0);}}
  if(id===COAL){for(let i=0;i<7;i++){const cx=2+Math.floor(Math.random()*11),cy=2+Math.floor(Math.random()*11);
    x.fillStyle='#20232a';x.fillRect(cx,cy,2,2);x.fillStyle='#3a3d44';x.fillRect(cx+1,cy,1,1);}}
  if(id===IRON){for(let i=0;i<6;i++){const cx=2+Math.floor(Math.random()*11),cy=2+Math.floor(Math.random()*11);
    x.fillStyle='#e6e8ea';x.fillRect(cx,cy,2,2);}}
  if(id===GOLD){for(let i=0;i<6;i++){const cx=2+Math.floor(Math.random()*11),cy=2+Math.random()*11|0;
    x.fillStyle='#fff0b0';x.fillRect(cx,cy,2,2);}}
  if(id===GRAVEL){for(let i=0;i<40;i++)px(x,Math.random()*16|0,Math.random()*16|0,['#5a5245','#a89e88','#4a443a'][Math.floor(Math.random()*3)]);}
  if(id===SNOW){for(let i=0;i<30;i++)px(x,Math.random()*16|0,Math.random()*16|0,'#fff');}
  return c;}
function texWater(){const c=document.createElement('canvas');c.width=c.height=16;const x=c.getContext('2d');
  x.fillStyle='#3f7fc0';x.fillRect(0,0,16,16);
  for(let i=0;i<20;i++){x.fillStyle=`rgba(120,180,230,${0.3+Math.random()*0.4})`;x.fillRect(Math.random()*16|0,Math.random()*16|0,2+Math.random()*3|0,1);}
  const t=new THREE.CanvasTexture(c);t.wrapS=t.wrapT=THREE.RepeatWrapping;return t;}
function texGlass(){const c=document.createElement('canvas');c.width=c.height=16;const x=c.getContext('2d');
  x.fillStyle='rgba(150,200,230,0.14)';x.fillRect(0,0,16,16);
  x.fillStyle='rgba(205,235,250,0.85)';x.fillRect(0,0,16,1);x.fillRect(0,15,16,1);x.fillRect(0,0,1,16);x.fillRect(15,0,1,16);
  x.fillStyle='rgba(255,255,255,0.5)';x.fillRect(2,2,4,1);x.fillRect(2,2,1,4);
  const t=new THREE.CanvasTexture(c);return t;}
function texLamp(){const c=document.createElement('canvas');c.width=c.height=16;const x=c.getContext('2d');
  x.fillStyle='#6a4a1e';x.fillRect(0,0,16,16);
  x.fillStyle='#f0b03a';x.fillRect(1,1,14,14);
  x.fillStyle='#ffe08a';x.fillRect(3,3,10,10);x.fillStyle='#fff2c0';x.fillRect(5,5,6,6);
  for(let i=0;i<20;i++)px(x,Math.random()*16|0,Math.random()*16|0,'#f7c968');
  return c;}
function texFlower(){const c=document.createElement('canvas');c.width=c.height=16;const x=c.getContext('2d');
  x.fillStyle='#4f8a3c';x.fillRect(7,8,2,7);x.fillRect(5,10,2,1);x.fillRect(9,11,2,1);
  const pal=['#e05a4a','#e6b94d','#c86bd0','#e0e0e0'];const col=pal[(Math.random()*pal.length)|0];
  for(const[dx,dy]of[[7,4],[8,4],[6,5],[9,5],[7,6],[8,6],[7,3],[6,4],[9,4]])x.fillStyle=col,x.fillRect(dx,dy,1,1);
  x.fillStyle='#f2e28a';x.fillRect(7,5,2,1);
  return c;}

let atlasCanvas,atlasUV={},atlasTex;
function buildAtlas(){atlasCanvas=document.createElement('canvas');atlasCanvas.width=atlasCanvas.height=1024;
  const ctx=atlasCanvas.getContext('2d');let col=0,row=0;
  for(const id of Object.keys(BLOCKS).map(Number)){
    if(id===AIR)continue;const B=BLOCKS[id];
    const top=id===GRASS?texTop(GRASS):id===FLOWERS?null:texTop(id);
    const side=id===FLOWERS?null:(B.side2?texSide(id):texSide(id));
    const bot=id===GRASS?texTop(DIRT):id===FLOWERS?null:texTop(id);
    const put=(cv,slot)=>{if(!cv)return;const sx=col*16,sy=row*16;ctx.drawImage(cv,sx,sy);atlasUV[id+'_'+slot]=[sx/1024,sy/1024];};
    put(top,'top');put(side,'side');put(bot,'bottom');
    if(id===GRASS){const s2=texSide(DIRT);const sx=col*16,sy=row*16;ctx.drawImage(s2,sx,sy);atlasUV['GRASS_side2']=[sx/1024,sy/1024];}
    col++;if(col>=64){col=0;row++;}
  }
  atlasTex=new THREE.CanvasTexture(atlasCanvas);atlasTex.magFilter=THREE.NearestFilter;atlasTex.minFilter=THREE.NearestMipmapNearestFilter;
  atlasTex.colorSpace=THREE.SRGBColorSpace;
}

/* ============ メッシュマテリアル ============ */
const matOpaque=new THREE.MeshLambertMaterial({map:atlasTex});
const matLeaf=new THREE.MeshLambertMaterial({map:atlasTex,transparent:true,alphaTest:0.4,side:THREE.DoubleSide});
const matGlass=new THREE.MeshLambertMaterial({map:atlasTex,transparent:true,opacity:0.6,depthWrite:false});
const matLamp=new THREE.MeshBasicMaterial({map:atlasTex});
const matWater=new THREE.MeshLambertMaterial({map:texWater(),transparent:true,opacity:0.68,depthWrite:false,side:THREE.DoubleSide});
const matFlower=new THREE.MeshLambertMaterial({map:atlasTex,transparent:true,alphaTest:0.5,side:THREE.DoubleSide});

/* ============ チャンク メッシュビルド ============ */
const U=1/64;
function uvFor(id,slot){const k=BLOCKS[id].side2&&slot==='side'?id+'_'+(slot):id+'_'+slot;return atlasUV[k]||atlasUV[id+'_top'];}
function buildChunkMesh(cx,cz){
  const o={pos:[],uv:[],nrm:[]};
  const tr={pos:[],uv:[],nrm:[]},wl={pos:[],uv:[],nrm:[]};
  const fl={pos:[],uv:[]};
  const bx=cx<<4,bz=cz<<4;
  const addFace=(t,f,wx,wy,wz,id)=>{const p=f.pos,n=f.nrm;
    for(let i=0;i<4;i++){t.pos.push(wx+p[i*3],wy+p[i*3+1],wz+p[i*3+2]);t.nrm.push(n[0],n[1],n[2]);}
    const[u,v]=uvFor(id,f.uv);t.uv.push(u,v,u+U,v,u+U,v+U,u,v+U);
    t.pos.push(wx+p[9],wy+p[10],wz+p[11]);t.nrm.push(n[0],n[1],n[2]);
    t.pos.push(wx+p[3],wy+p[4],wz+p[5]);t.nrm.push(n[0],n[1],n[2]);
  };
  for(let x=0;x<16;x++)for(let z=0;z<16;z++)for(let y=0;y<WORLD_H;y++){
    const id=getB(bx+x,y,bz+z);if(!id||id===AIR)continue;
    const wx=bx+x,wz=bz+z;
    if(id===FLOWERS){
      const[u,v]=uvFor(FLOWERS,'side');
      // 交差十字（billboard-ish）2枚
      const quads=[[[0,0,0.5],[1,0,0.5],[1,1,0.5],[0,1,0.5]],[[0.5,0,0],[0.5,0,1],[0.5,1,1],[0.5,1,0]]];
      for(const q of quads){for(const p of q){fl.pos.push(wx+p[0],y+p[1],wz+p[2]);fl.uv.push(u+(p[0]===1?U:0),v+(p[1]===1?U:0));}}
      continue;
    }
    const isW=id===WATER;
    for(const f of FACES){
      const nb=getB(wx+f.nx,y+f.ny,wz+f.nz);
      if(isW){
        if(nb!==AIR)continue;
        const t=(f.ny>0?wl:wl);
        const yy=(f.ny>0&&getB(wx,y+1,wz)!==WATER)?y+0.86:(f.ny<0?y+0.98:y);
        const p=f.pos.map((v,i)=>i%3===1?yy:y+v); // 簡易: 面をyyに寄せる
        // top/bottom は y を yy に、側面は y..y+1
        const q=f.pos.map((v,i)=>i%3===1?((f.ny!==0)?yy:v):v);
        for(let i=0;i<4;i++){const vi=f.pos[i*3],vj=f.pos[i*3+1],vk=f.pos[i*3+2];
          const vy=f.ny!==0?yy:vj;t.pos.push(wx+vi,vy,wz+vk);t.nrm.push(f.nx,f.ny,f.nz);}
        const[pu,pv]=uvFor(WATER,'top');t.uv.push(pu,pv,pu+U,pv,pu+U,pv+U,pu,pv+U);
        t.pos.push(wx+f.pos[9],(f.ny!==0?yy:f.pos[10]),wz+f.pos[11]);t.nrm.push(f.nx,f.ny,f.nz);
        t.pos.push(wx+f.pos[3],(f.ny!==0?yy:f.pos[4]),wz+f.pos[5]);t.nrm.push(f.nx,f.ny,f.nz);
        continue;
      }
      if(isSolid(nb)&&!BLOCKS[nb].transparent)continue;
      if(isWater(nb))continue;
      const t=(id===LEAVES?tr:id===GLASS?tr:id===LAMP?tr:o);
      if(id===COBBLE_STEP){ // 半ブロック
        if(f.ny<0||getB(wx,y-1,wz)!==AIR){if(f.ny!==0&&getB(wx+f.nx,y+f.ny,wz+f.nz)===AIR)addFace(t,f,wx,y,wz,id);continue;}
        if(f.ny>0){addFace(t,f,wx,y,wz,id);}else{ // 側面は高さ0.5
          const q=f.pos.map((v,i)=>i%3===1?v*0.5:v);
          const p=f.pos;for(let i=0;i<4;i++){const vi=p[i*3],vj=p[i*3+1],vk=p[i*3+2];t.pos.push(wx+vi,y+vj*0.5,wz+vk);t.nrm.push(f.nx,f.ny,f.nz);}
          const[pu,pv]=uvFor(id,'side');t.uv.push(pu,pv,pu+U,pv+U,pu+U,pv,pu,pv);
          t.pos.push(wx+p[9],y+p[10]*0.5,wz+p[11]);t.nrm.push(f.nx,f.ny,f.nz);
          t.pos.push(wx+p[3],y+p[4]*0.5,wz+p[5]);t.nrm.push(f.nx,f.ny,f.nz);
        }
        continue;
      }
      addFace(t,f,wx,y,wz,id);
    }
  }
  return {o,tr,wl,fl};
}
/* メッシュ化 */
function toMesh(g,mat){if(!g.pos.length)return null;const geo=new THREE.BufferGeometry();
  geo.setAttribute('position',new THREE.Float32BufferAttribute(g.pos,3));
  geo.setAttribute('uv',new THREE.Float32BufferAttribute(g.uv,2));
  geo.setAttribute('normal',new THREE.Float32BufferAttribute(g.nrm,3));
  const m=new THREE.Mesh(geo,mat);m.frustumCulled=false;return m;}
function rebuild(cx,cz){
  const key=ck(cx,cz);const old=chunkMeshes.get(key);
  if(old){for(const m of old){scene.remove(m);m.geometry&&m.geometry.dispose();}chunkMeshes.delete(key);}
  const g=buildChunkMesh(cx,cz);const arr=[];
  const mo=toMesh(g.o,matOpaque);if(mo)arr.push(mo);
  const mt=toMesh(g.tr,matLeaf);if(mt)arr.push(mt);
  const mw=toMesh(g.wl,matWater);if(mw)arr.push(mw);
  const mf=toMesh(g.fl,matFlower);if(mf)arr.push(mf);
  for(const m of arr)scene.add(m);chunkMeshes.set(key,arr);
}
const FACES=[
 {nx:1,ny:0,nz:0,uv:'side',pos:[1,0,0,1,1,0,1,1,1,1,0,1],nrm:[1,0,0]},
 {nx:-1,ny:0,nz:0,uv:'side',pos:[0,0,1,0,1,1,0,1,0,0,0,0],nrm:[-1,0,0]},
 {nx:0,ny:1,nz:0,uv:'top',pos:[0,1,1,1,1,1,1,1,0,0,1,0],nrm:[0,1,0]},
 {nx:0,ny:-1,nz:0,uv:'bottom',pos:[0,0,0,1,0,0,1,0,1,0,0,1],nrm:[0,-1,0]},
 {nx:0,ny:0,nz:1,uv:'side',pos:[1,0,1,1,1,1,0,1,1,0,0,1],nrm:[0,0,1]},
 {nx:0,ny:0,nz:-1,uv:'side',pos:[0,0,0,0,1,0,1,1,0,1,0,0],nrm:[0,0,-1]},
];
function buildAll(){for(let z=-RADIUS;z<=RADIUS;z++)for(let x=-RADIUS;x<=RADIUS;x++)rebuild(cx(x),cz(x));}
const cx=v=>Math.floor(v.x/CHUNK),cz=v=>Math.floor(v.z/CHUNK);

/* 隣接更新 */
function markNeigh(cx,cz){for(let z=-1;z<=1;z++)for(let x=-1;x<=1;x++){const k=ck(cx+x,cz+z);if(inRadius(cx+x,cz+z))dirty.add(k);}}

/* ============ 破砕アニメ + 粒子 ============ */
const crackTex=(()=>{const arr=[];for(let s=0;s<8;s++){const c=document.createElement('canvas');c.width=c.height=16;const x=c.getContext('2d');
  x.strokeStyle='rgba(0,0,0,0.8)';x.lineWidth=1.5;
  const seg=Math.ceil((s+1)/8*10);
  for(let i=0;i<seg;i++){x.beginPath();x.moveTo(2+Math.random()*12,2);x.lineTo(2+Math.random()*12,14);x.stroke();x.beginPath();x.moveTo(2,2+Math.random()*12);x.lineTo(14,2+Math.random()*12);x.stroke();}
  const t=new THREE.CanvasTexture(c);t.magFilter=THREE.NearestFilter;arr.push(t);}return arr;})();
const crackMesh=new THREE.Mesh(new THREE.BoxGeometry(1.001,1.001,1.001),
  new THREE.MeshBasicMaterial({map:crackTex[0],transparent:true,depthWrite:false}));
crackMesh.visible=false;scene.add(crackMesh);
const breakParts=[];
function spawnBreak(id,bx,by,bz){const col=BLOCKS[id]?BLOCKS[id].name:'';
  const base=id===GRASS?'#6cae4d':id===DIRT?'#8a6a44':id===STONE||id===COBBLE||id===COBBLE_STEP||id===COAL?'#8f9295':id===LOG?'#6b4f2c':id===LEAVES?'#4c8a3e':id===SAND?'#dcc48b':'#8f9295';
  for(let i=0;i<14;i++){const m=new THREE.Mesh(new THREE.BoxGeometry(.12,.12,.12),new THREE.MeshLambertMaterial({color:base}));
    m.position.set(bx+.5+(Math.random()-.5)*.7,by+.5+(Math.random()-.5)*.7,bz+.5+(Math.random()-.5)*.7);
    m.userData.v=new THREE.Vector3((Math.random()-.5)*4,2+Math.random()*4,(Math.random()-.5)*4);
    m.userData.t=0.6;scene.add(m);breakParts.push(m);}
}
function updBreakParts(dt){for(let i=breakParts.length-1;i>=0;i--){const m=breakParts[i];m.userData.v.y-=GRAVITY*dt;
  m.position.addScaledVector(m.userData.v,dt);m.userData.t-=dt;m.scale.setScalar(Math.max(0,m.userData.t/0.6));
  if(m.userData.t<=0||m.position.y<-5){scene.remove(m);m.geometry.dispose();m.material.dispose();breakParts.splice(i,1);}}}

/* ============ 水中泡 ============ */
const bubbleTex=(()=>{const c=document.createElement('canvas');c.width=c.height=32;const x=c.getContext('2d');
  x.strokeStyle='rgba(255,255,255,0.8)';x.lineWidth=3;x.beginPath();x.arc(16,16,11,0,7);x.stroke();
  x.fillStyle='rgba(255,255,255,0.15)';x.beginPath();x.arc(16,16,11,0,7);x.fill();
  const t=new THREE.CanvasTexture(c);return t;})();
const bubbles=[];const bubblePool=[];
function spawnBubbles(){const p=new THREE.Mesh(new THREE.PlaneGeometry(.4,.4),new THREE.MeshBasicMaterial({map:bubbleTex,transparent:true,depthWrite:false}));
  p.userData.v=new THREE.Vector3((Math.random()-.5)*1.2,1.5+Math.random()*1.5,(Math.random()-.5)*1.2);p.userData.t=1.2;
  p.position.set(player.x,player.y+0.2,player.z);scene.add(p);bubbles.push(p);}
function updBubbles(dt){for(let i=bubbles.length-1;i>=0;i--){const b=bubbles[i];b.userData.v.y-=1.5*dt;
  b.position.addScaledVector(b.userData.v,dt);b.userData.t-=dt;if(b.userData.t<=0||b.position.y>SEA){scene.remove(b);bubbles.splice(i,1);}}}

/* 花の揺れ */
let flowerMesh=null;
function updateFlowerWind(t){if(!flowerMesh)return;const arr=flowerMesh.geometry.attributes.position.array;
  const base=flowerMesh.userData.base;for(let i=0;i<arr.length;i+=3){const x0=base[i],z0=base[i+2];
    arr[i]=x0+Math.sin(t*3+z0*0.6)*0.05;arr[i+2]=z0+Math.cos(t*2.3+x0*0.6)*0.04;}
  flowerMesh.geometry.attributes.position.needsUpdate=true;}

/* ============ 作業台（デコ） ============ */
let workbench=null;
function makeWorkbench(){const g=new THREE.Group();
  const legM=new THREE.MeshLambertMaterial({color:0x6b4f2c});const bodyM=new THREE.MeshLambertMaterial({color:0x8a5a2f});
  const leg=new THREE.BoxGeometry(0.2,0.7,0.2);
  for(const[dx,dz]of[[-0.35,-0.35],[0.35,-0.35],[-0.35,0.35],[0.35,0.35]]){const l=new THREE.Mesh(leg,legM);l.position.set(dx,0.35,dz);g.add(l);}
  const top=new THREE.Mesh(new THREE.BoxGeometry(1,0.25,1),bodyM);top.position.y=0.82;g.add(top);
  const grid=new THREE.Mesh(new THREE.BoxGeometry(0.9,0.05,0.9),new THREE.MeshLambertMaterial({color:0x5a4224}));grid.position.y=0.96;g.add(grid);
  const saw=new THREE.Mesh(new THREE.BoxGeometry(0.5,0.08,0.12),new THREE.MeshLambertMaterial({color:0x8f9295}));saw.position.set(0.1,1.02,0.2);g.add(saw);
  return g;}

/* ============ 壊れブロックの破砕状態 ============ */
let mine=null; // {x,y,z,progress}

/* ============ プレイヤー ============ */
const player={x:0,y:0,z:0,vx:0,vy:0,vz:0,onGround:false,crouching:false,fly:false};
let yaw=0,pitch=0;
function spawnPlayer(){let x=0,z=0;for(let r=0;r<40;r++){if(terrain(x,z)>SEA+1)break;x+=Math.floor(Math.random()*20-10);z+=Math.floor(Math.random()*20-10);}
  player.x=x+0.5;player.z=z+0.5;player.y=terrain(x,z)+1.2;player.vx=player.vy=player.vz=0;}

/* 衝突 */
function collide(x,y,z,feet){const h=feet?STAND_H:CROUCH_H;
  const x0=Math.floor(x-0.3),x1=Math.floor(x+0.3),z0=Math.floor(z-0.3),z1=Math.floor(z+0.3);
  for(let bx=x0;bx<=x1;bx++)for(let bz=z0;bz<=z1;bz++)for(let by=Math.floor(y);by<=Math.floor(y+h);by++){
    const id=getB(bx,by,bz);if(id===COBBLE_STEP){if(by+0.5>y&&by<y+h)return true;}else if(isSolid(id))return true;}
  return false;}
function moveAxis(axis,d){if(d===0)return;
  if(axis==='x')player.x+=d;else if(axis==='y')player.y+=d;else player.z+=d;
  if(collide(player.x,player.y,player.z,player.crouching)){
    if(axis==='y'){if(d<0)player.onGround=true;player.vy=0;}
    if(axis==='x')player.x-=d;if(axis==='z')player.z-=d;
  }
}

/* レイキャスト */
let target=null;
function raycast(){const dir=new THREE.Vector3();camera.getWorldDirection(dir);
  let px=Math.floor(player.x),py=Math.floor(player.y),pz=Math.floor(player.z);
  const sx=dir.x>0?1:-1,sy=dir.y>0?1:-1,sz=dir.z>0?1:-1;
  const tdx=Math.abs(1/dir.x),tdy=Math.abs(1/dir.y),tdz=Math.abs(1/dir.z);
  let tmx=dir.x!==0?((sx>0?(px+1-player.x):(player.x-px))*tdx):Infinity;
  let tmy=dir.y!==0?((sy>0?(py+1-player.y):(player.y-py))*tdy):Infinity;
  let tmz=dir.z!==0?((sz>0?(pz+1-player.z):(player.z-pz))*tdz):Infinity;
  let nx=0,ny=0,nz=0,dist=0;
  while(dist<REACH){
    if(tmx<tmy&&tmx<tmz){px+=sx;dist=tmx;tmx+=tdx;nx=-sx;ny=0;nz=0;}
    else if(tmy<tmz){py+=sy;dist=tmy;tmy+=tdy;nx=0;ny=-sy;nz=0;}
    else{pz+=sz;dist=tmz;tmz+=tdz;nx=0;ny=0;nz=-sz;}
    const id=getB(px,py,pz);
    if(id&&id!==AIR&&id!==WATER){target={x:px,y:py,z:pz,id,px:px+nx,py:py+ny,pz:pz+nz};return;}
  }
  target=null;
}
/* ハイトラバー */
const highlight=new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(1.002,1.002,1.002)),
  new THREE.LineBasicMaterial({color:0x000000,transparent:true,opacity:0.5}));
highlight.visible=false;scene.add(highlight);

/* ============ インタラクション ============ */
let hotbarIdx=0;
const placeCounts={};
function placeBlock(){if(!target)return;const id=HOTBAR[hotbarIdx];
  const{x,y,z}=target;
  // 衝突判定
  const feetH=player.crouching?CROUCH_H:STAND_H;
  const x0=Math.floor(x+0.0),x1=Math.floor(x+1-0.001);
  const px0=player.x-0.3,px1=player.x+0.3,pz0=player.z-0.3,pz1=player.z+0.3;
  const overlap=!(x+1<px0||x>px1||z+1<pz0||z>pz1||y+1<player.y||y>player.y+feetH);
  if(overlap&&isSolid(id))return;
  if(getB(x,y,z)!==AIR&&getB(x,y,z)!==WATER)return;
  setB(x,y,z,id);markNeigh(cx({x}),cz({x}));
  if(id===COBBLE_STEP){/* 隣更新 */}
  placeCounts[id]=(placeCounts[id]||0)+1;if(placeCounts[id]>MAXPLACE){toast('設置上限に達しました');}
}
function breakBlock(){if(!target)return;const{x,y,z,id}=target;
  if(id===WATER)return;
  if(id===COBBLE_STEP){/* ok */}
  const b=BLOCKS[id];
  spawnBreak(id,x,y,z);
  setB(x,y,z,AIR);
  // 隣接の水を流す
  for(const f of FACES){const nx=x+f.nx,ny=y+f.ny,nz=z+f.nz;if(getB(nx,ny,nz)===WATER)dirty.add(ck(nx>>4,nz>>4));}
  markNeigh(cx({x}),cz({x}));
}
/* 長押し破砕 */
let holdingBreak=false, breakTargetPos=null, breakProgress=0;
function updateBreak(dt){
  if(holdingBreak&&target){
    const t=target;const same=breakTargetPos&&breakTargetPos.x===t.x&&breakTargetPos.y===t.y&&breakTargetPos.z===t.z;
    if(!same){breakTargetPos={x:t.x,y:t.y,z:t.z};breakProgress=0;}
    breakProgress+=dt;
    const s=Math.min(7,Math.floor(breakProgress*6));
    crackMesh.visible=true;crackMesh.position.set(t.x+0.5,t.y+0.5,t.z+0.5);crackMesh.material.map=crackTex[s];
    if(breakProgress>=1.0){breakBlock();breakProgress=0;breakTargetPos=null;crackMesh.visible=false;}
  }else{crackMesh.visible=false;breakProgress=0;breakTargetPos=null;}
}

/* ============ ホットバー UI ============ */
const hotbarEl=document.getElementById('hotbar');
function buildHotbar(){hotbarEl.innerHTML='';
  HOTBAR.forEach((id,i)=>{const s=document.createElement('div');s.className='slot';
    const c=document.createElement('canvas');c.className='ic';c.width=c.height=32;const x=c.getContext('2d');
    const top=atlasCanvas?atlasCanvas:(0);
    // atlasからスライス
    const uv=atlasUV[id+'_top']||atlasUV[id+'_side'];if(uv){const sx=uv[0]*1024,sy=uv[1]*1024;
      x.imageSmoothingEnabled=false;x.drawImage(atlasCanvas,sx,sy,16,16,0,0,32