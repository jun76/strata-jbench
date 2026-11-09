マイクラ風ボクセルサンドボックスを作りました。単一 HTML の WebGL2 自作レンダラー（チャンク+グリディ・メッシュ、手続きテクスチャ、昼夜サイクル、雲・星空、日射光＋ヘミスフェリック、フォグ）で、挖掘/設置・物理・フライ・発光ブロック・パーティクル・音・セーブまで全部入りです。

```html
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<title>VOXEL GARDEN — 3D箱庭</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Zen+Kaku+Gothic+New:wght@500;700;900&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">
<style>
:root{
  --ink:#0b0f14; --panel:#121a22; --panel2:#0d141b; --edge:#2c3a46; --edge-hi:#3f5568;
  --lime:#a6e06b; --amber:#ffc45c; --cyan:#6fd3e8; --rose:#ff8a70;
  --paper:#e9eef3; --dim:#8ba0b3;
}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;background:#0b0f14;overflow:hidden;color:var(--paper);
  font-family:"Zen Kaku Gothic New","Hiragino Sans",system-ui,sans-serif}
.pixel{font-family:"Press Start 2P","IBM Plex Mono","DIN Alternate",monospace}
.mono{font-family:"IBM Plex Mono","DIN Alternate","Courier New",monospace;font-variant-numeric:tabular-nums}

#stage{position:fixed;inset:0}
canvas#cv{position:absolute;inset:0;width:100%;height:100%;display:block}
#vignette{position:absolute;inset:0;pointer-events:none;
  background:radial-gradient(120% 90% at 50% 45%, transparent 45%, rgba(6,10,14,.32) 100%);
  mix-blend-mode:multiply}
#grain{position:absolute;inset:0;pointer-events:none;opacity:.14;
  background:repeating-linear-gradient(0deg,rgba(255,255,255,.12) 0 1px,transparent 1px 3px)}

/* ---------- HUD ---------- */
#hud{position:absolute;inset:0;pointer-events:none;display:none}
#hud.on{display:block}
#cross{position:absolute;left:50%;top:50%;width:26px;height:26px;transform:translate(-50%,-50%);
  transition:transform .12s ease}
#cross::before,#cross::after{content:"";position:absolute;background:#eaf3f6;opacity:.85;
  box-shadow:0 0 6px rgba(233,243,246,.45)}
#cross::before{left:50%;top:0;width:2px;height:100%;transform:translateX(-50%)}
#cross::after{top:50%;left:0;height:2px;width:100%;transform:translateY(-50%)}
#cross.hit{transform:translate(-50%,-50%) scale(1.35) rotate(45deg)}
#cross.place{transform:translate(-50%,-50%) scale(1.5)}

#topbar{position:absolute;left:14px;top:12px;display:flex;gap:10px;align-items:flex-start;flex-wrap:wrap}
#topbar .cube{width:38px;height:38px;filter:drop-shadow(0 3px 6px rgba(0,0,0,.55))}
#brand{line-height:1}
#brand h1{font-size:12px;letter-spacing:.14em;color:var(--paper)}
#brand p{margin-top:6px;font-size:11px;color:var(--dim);letter-spacing:.05em}

#stats{position:absolute;left:14px;bottom:14px;background:linear-gradient(180deg,rgba(18,26,34,.88),rgba(13,20,27,.88));
  border:2px solid var(--edge);border-radius:8px;padding:10px 12px;box-shadow:0 8px 24px rgba(0,0,0,.45), inset 0 1px 0 rgba(255,255,255,.06)}
#stats .row{display:flex;gap:8px;align-items:baseline;font-size:11px;color:var(--dim)}
#stats .row+.row{margin-top:4px}
#stats b{color:var(--paper);font-weight:600;font-size:12px;letter-spacing:.03em}
#stats .lime{color:var(--lime)}
#stats .amber{color:var(--amber)}
#stats .cyan{color:var(--cyan)}
#modeChip{display:inline-block;margin-top:6px;font-size:10px;padding:3px 7px;border:1px solid var(--edge-hi);
  border-radius:999px;color:var(--cyan);background:rgba(111,211,232,.08)}

#clock{position:absolute;right:14px;top:12px;background:rgba(13,20,27,.82);border:2px solid var(--edge);
  border-radius:8px;padding:8px 10px;box-shadow:0 8px 24px rgba(0,0,0,.4)}
#clock .lab{font-size:10px;color:var(--dim);letter-spacing:.14em}
#clock .val{font-size:14px;margin-top:4px;letter-spacing:.06em}
#track{margin-top:8px;width:130px;height:8px;border:1px solid var(--edge-hi);border-radius:999px;
  background:linear-gradient(90deg,#1b2735,#334a5d 22%,#c98a3c 42%,#ffe3a8 50%,#c98a3c 58%,#334a5d 78%,#141d28);
  position:relative;overflow:hidden}
#track i{position:absolute;top:-3px;left:0;width:6px;height:14px;border-radius:3px;background:#fff;
  box-shadow:0 0 8px rgba(255,255,255,.75);transform:translateX(-50%)}

#barwrap{position:absolute;left:50%;bottom:16px;transform:translateX(-50%);display:flex;flex-direction:column;
  align-items:center;gap:8px}
#bar{display:flex;gap:6px;padding:6px;background:rgba(13,20,27,.72);border:2px solid var(--edge);
  border-radius:10px;box-shadow:0 10px 26px rgba(0,0,0,.5), inset 0 1px 0 rgba(255,255,255,.07)}
.slot{width:52px;height:52px;border:2px solid #26323d;border-radius:6px;background:#0e161e;position:relative;
  transition:transform .14s cubic-bezier(.2,.9,.3,1.4), border-color .14s;cursor:pointer;pointer-events:auto}
.slot canvas{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:34px;height:34px}
.slot .num{position:absolute;left:4px;top:2px;font-size:9px;color:var(--dim)}
.slot:hover{transform:translateY(-4px);border-color:var(--edge-hi)}
.slot.sel{border-color:var(--lime);transform:translateY(-7px) scale(1.06);
  box-shadow:0 0 0 2px rgba(166,224,107,.25),0 8px 18px rgba(0,0,0,.5)}
.slot.sel::after{content:"";position:absolute;left:50%;bottom:-6px;width:8px;height:2px;background:var(--lime);
  transform:translateX(-50%)}
#barhint{font-size:11px;color:var(--dim);letter-spacing:.06em}
#barhint b{color:var(--amber);font-weight:600}

#toast{position:absolute;left:50%;bottom:86px;transform:translateX(-50%);font-size:12px;color:var(--paper);
  background:rgba(13,20,27,.85);border:1px solid var(--edge-hi);padding:6px 12px;border-radius:6px;
  opacity:0;transition:opacity .3s, transform .3s;letter-spacing:.05em}
#toast.show{opacity:1;transform:translateX(-50%) translateY(-6px)}

/* ---------- overlay ---------- */
#overlay{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
  background:radial-gradient(90% 70% at 50% 40%, rgba(11,15,20,.7), rgba(11,15,20,.92));
  backdrop-filter:blur(2px);transition:opacity .25s}
#overlay.hide{opacity:0;pointer-events:none}
#panel{width:min(660px,92vw);background:linear-gradient(180deg,#16202a,#0f171f);
  border:3px solid var(--edge-hi);border-radius:12px;padding:26px 26px 22px;
  box-shadow:0 26px 60px rgba(0,0,0,.6), inset 0 1px 0 rgba(255,255,255,.08);position:relative}
#panel::before{content:"";position:absolute;left:0;right:0;top:0;height:3px;
  background:linear-gradient(90deg,var(--lime),var(--amber) 45%,var(--cyan))}
#head{display:flex;gap:16px;align-items:center}
#head svg{width:46px;height:46px;flex:none}
#head h2{font-size:16px;letter-spacing:.16em}
#head .sub{margin-top:8px;font-size:12px;color:var(--dim);letter-spacing:.08em}
.kbd{font-family:"IBM Plex Mono",monospace;font-size:11px;background:#0b1219;border:1px solid var(--edge-hi);
  border-radius:4px;padding:3px 7px;color:var(--paper);box-shadow:0 2px 0 rgba(0,0,0,.5)}
#keys{margin-top:18px;display:grid;grid-template-columns:repeat(2,1fr);gap:8px 18px}
#keys div{display:flex;gap:9px;align-items:center;font-size:12px;color:var(--dim)}
#keys div em{font-style:normal;color:var(--paper)}
.btns{margin-top:20px;display:flex;gap:8px;flex-wrap:wrap;align-items:center}
button{font-family:"IBM Plex Mono",monospace;font-size:12px;letter-spacing:.1em;color:var(--paper);
  background:#1b2732;border:2px solid var(--edge-hi);border-radius:7px;padding:9px 14px;cursor:pointer;
  box-shadow:0 3px 0 rgba(0,0,0,.55), inset 0 1px 0 rgba(255,255,255,.06);
  transition:transform .12s, background .12s, border-color .12s}
button:hover{transform:translateY(-2px);background:#233140;border-color:var(--lime)}
button:active{transform:translateY(1px);box-shadow:0 1px 0 rgba(0,0,0,.5)}
button.go{background:#243c22;border-color:var(--lime);color:var(--lime)}
button.go:hover{background:#2d4a29}
button.warn{background:#3a2420;border-color:var(--rose);color:var(--rose)}
input.seed{font-family:"IBM Plex Mono",monospace;font-size:12px;background:#0b1219;border:2px solid var(--edge-hi);
  border-radius:7px;padding:9px 12px;color:var(--paper);width:120px}
input.seed:focus{outline:none;border-color:var(--amber)}
#panel .tip{margin-top:14px;font-size:11px;color:var(--dim);letter-spacing:.05em}

#loading{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;flex-direction:column;
  gap:14px;background:#0b0f14;z-index:5}
#loading.done{opacity:0;pointer-events:none;transition:opacity .5s}
#loading .lb{font-size:12px;letter-spacing:.2em;color:var(--cyan)}
#genbar{width:260px;height:10px;border:2px solid var(--edge-hi);border-radius:6px;overflow:hidden;background:#0d141b}
#genbar i{display:block;height:100%;width:0%;background:linear-gradient(90deg,var(--lime),var(--cyan));transition:width .1s}
#genpct{font-size:11px;color:var(--dim);letter-spacing:.14em}

#err{position:absolute;inset:0;display:none;align-items:center;justify-content:center;text-align:center;
  font-size:13px;color:var(--rose);padding:24px;line-height:1.7}
@media (max-width:640px){ #keys{grid-template-columns:1fr} #topbar{display:none} }
</style>
</head>
<body>
<div id="stage">
  <canvas id="cv"></canvas>
  <div id="grain"></div>
  <div id="vignette"></div>

  <div id="hud">
    <div id="cross"></div>
    <div id="topbar">
      <svg class="cube" viewBox="0 0 32 32" aria-hidden="true">
        <path d="M16 2 30 9 30 23 16 30 2 23 2 9Z" fill="#74c250"/>
        <path d="M16 2 30 9 16 16 2 9Z" fill="#a6e06b"/>
        <path d="M16 16 30 9 30 23 16 30Z" fill="#7d5f42"/>
        <path d="M16 16 2 9 2 23 16 30Z" fill="#5f4830"/>
      </svg>
      <div id="brand"><h1 class="pixel">VOXEL GARDEN</h1><p>3Dボクセル箱庭 / WebGL2</p></div>
    </div>

    <div id="stats">
      <div class="row"><span class="mono">FPS</span><b id="fps" class="mono lime">60</b></div>
      <div class="row"><span class="mono">XYZ</span><b id="xyz" class="mono">0 0 0</b></div>
      <div class="row"><span class="mono">BIOME</span><b id="biome" class="mono cyan">草原</b></div>
      <div class="row"><span class="mono">CHUNK</span><b id="chunks" class="mono amber">0</b></div>
      <div id="modeChip" class="mono">歩行モード</div>
    </div>

    <div id="clock">
      <div class="lab pixel">TIME</div>
      <div class="val mono" id="clockval">12:00</div>
      <div id="track"><i id="sunmark"></i></div>
    </div>

    <div id="barwrap">
      <div id="bar"></div>
      <div id="barhint"><span id="selname">草ブロック</span> / <b>1〜9</b>・ホイールで切替</div>
    </div>

    <div id="toast"></div>
  </div>

  <div id="overlay">
    <div id="panel">
      <div id="head">
        <svg viewBox="0 0 32 32" aria-hidden="true">
          <path d="M16 2 30 9 30 23 16 30 2 23 2 9Z" fill="#74c250"/>
          <path d="M16 2 30 9 16 16 2 9Z" fill="#a6e06b"/>
          <path d="M16 16 30 9 30 23 16 30Z" fill="#7d5f42"/>
          <path d="M16 16 2 9 2 23 16 30Z" fill="#5f4830"/>
        </svg>
        <div>
          <h2 class="pixel">VOXEL GARDEN</h2>
          <div class="sub">ブロックを掘って、積んで、飛ぶ。昼夜が回って、水が揺れる。</div>
        </div>
      </div>
      <div id="keys">
        <div><span class="kbd">W A S D</span><em>移動</em></div>
        <div><span class="kbd">Space</span><em>ジャンプ / 上昇</em></div>
        <div><span class="kbd">Shift</span><em>走る / 下降</em></div>
        <div><span class="kbd">F</span><em>フライ切替</em></div>
        <div><span class="kbd">左クリック</span><em>ブロック破壊</em></div>
        <div><span class="kbd">右クリック</span><em>ブロック設置</em></div>
        <div><span class="kbd">中クリック</span><em>その場のブロックを採取</em></div>
        <div><span class="kbd">1〜9 / ホイール</span><em>スロット選択</em></div>
        <div><span class="kbd">T</span><em>時間早送り</em></div>
        <div><span class="kbd">M</span><em>音 ON / OFF</em></div>
        <div><span class="kbd">Esc</span><em>メニュー</em></div>
        <div><span class="kbd">Ctrl</span><em>ゆっくり移動</em></div>
      </div>
      <div class="btns">
        <button id="btnStart" class="go pixel">はじめる</button>
        <button id="btnGen">再生成</button>
        <input id="seed" class="seed" value="seed-2025" aria-label="シード">
        <button id="btnSave">保存</button>
        <button id="btnLoad">読込</button>
        <button id="btnSound">音: ON</button>
      </div>
      <div class="tip">床の岩盤は壊せません。海抜 20 以下は水没。洞窟と光石の脈あり。</div>
    </div>
  </div>

  <div id="loading">
    <div class="lb pixel">地形生成中</div>
    <div id="genbar"><i id="genfill"></i></div>
    <div id="genpct" class="mono">0%</div>
  </div>

  <div id="err"></div>
</div>

<script>
"use strict";
/* ================= 定数・ブロック ================= */
const SX=128, SZ=128, SY=64, CS=16, CX=SX/CS, CZ=SZ/CS, SEA=20;
const AIR=0,GRASS=1,DIRT=2,STONE=3,COBBLE=4,SAND=5,LOG=6,LEAF=7,WATER=8,GLASS=9,BRICK=10,GLOW=11,BEDROCK=12;
const NAMES={1:'草ブロック',2:'土',3:'石',4:'丸石',5:'砂',6:'原木',7:'葉',8:'水',9:'ガラス',10:'レンガ',11:'光石',12:'岩盤'};
const PAL={1:[.45,.73,.34,.48,.38,.28],2:[.46,.34,.25,.38,.28,.2],3:[.55,.58,.62,.42,.45,.48],
  4:[.62,.66,.7,.45,.48,.52],5:[.88,.82,.66,.72,.66,.5],6:[.72,.56,.36,.5,.38,.27],
  7:[.36,.62,.3,.24,.44,.22],8:[.34,.6,.82,.2,.42,.62],9:[.86,.95,.98,.62,.8,.86],
  10:[.7,.4,.33,.5,.26,.22],11:[1,.86,.55,.8,.6,.34],12:[.26,.28,.33,.16,.18,.22]};
const hotbar=[GRASS,DIRT,STONE,COBBLE,SAND,LOG,LEAF,GLASS,GLOW];
const isOpaque=t=>t!==AIR&&t!==WATER&&t!==GLASS;
const isSolid=t=>t!==AIR&&t!==WATER;
const isTrans=t=>t===WATER||t===GLASS;
const idx=(x,y,z)=>x+SX*(z+SZ*y);
let data=new Uint8Array(SX*SY*SZ);
const bAt=(x,y,z)=>(x<0||x>=SX||y<0||y>=SY||z<0||z>=SZ)?BEDROCK:data[idx(x,y,z)];

/* ================= JS ノイズ ================= */
function mulberry(a){return function(){a|=0;a=(a+0x6D2B79F5)|0;let t=Math.imul(a^(a>>>15),1|a);t=(t+Math.imul(t^(t>>>7),61|t))^t;return((t^(t>>>14))>>>0)/4294967296}}
function h3i(x,y,z,s){let n=Math.imul(x|0,374761393)^Math.imul(y|0,668265263)^Math.imul(z|0,2147483647)^Math.imul(s|0,1274126177);
  n=Math.imul(n^(n>>>13),1274126177);n^=n>>>16;return((n>>>0)&0xffff)/65536}
function vnoise(x,y,z,s){const ix=Math.floor(x),iy=Math.floor(y),iz=Math.floor(z);
  const fx=x-ix,fy=y-iy,fz=z-iz,sx=fx*fx*(3-2*fx),sy=fy*fy*(3-2*fy),sz=fz*fz*(3-2*fz);
  const a=h3i(ix,iy,iz,s),b=h3i(ix+1,iy,iz,s),c=h3i(ix,iy+1,iz,s),d=h3i(ix+1,iy+1,iz,s);
  const e=h3i(ix,iy,iz+1,s),f=h3i(ix+1,iy,iz+1,s),g=h3i(ix,iy+1,iz+1,s),h=h3i(ix+1,iy+1,iz+1,s);
  const X0=a+(b-a)*sx,X1=c+(d-c)*sx,X2=e+(f-e)*sx,X3=g+(h-g)*sx;
  const Y0=X0+(X1-X0)*sy,Y1=X2+(X3-X2)*sy;return Y0+(Y1-Y0)*sz}
function fbm(x,y,z,s,oct){let v=0,a=.5,f=1;for(let i=0;i<oct;i++){v+=a*vnoise(x*f,y*f,z*f,s+i*131);f*=2.03;a*=.5}return v}

/* ================= WebGL ================= */
const canvas=document.getElementById('cv');
let gl=canvas.getContext('webgl2',{antialias:true,alpha:false});
if(!gl){document.getElementById('err').style.display='flex';
  document.getElementById('err').innerHTML='このブラウザは WebGL2 に対応していません。<br>Chrome / Edge / Firefox の最新版で開いてください。';
  document.getElementById('loading').classList.add('done');document.getElementById('overlay').style.display='none';}
function sh(src,type){const s=gl.createShader(type);gl.shaderSource(s,src);gl.compileShader(s);
  if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))console.error(gl.getShaderInfoLog(s));return s}
function prog(vs,fs){const p=gl.createProgram();gl.attachShader(p,sh(vs,gl.VERTEX_SHADER));gl.attachShader(p,sh(fs,gl.FRAGMENT_SHADER));
  gl.linkProgram(p);if(!gl.getProgramParameter(p,gl.LINK_STATUS))console.error(gl.getShaderInfoLog(p));
  p.u={};[...fs.matchAll(/uniform\s+\w+\s+(\w+)/g)].forEach(m=>p.u[m[1]]=gl.getUniformLocation(p,m[1]));return p}
const commonVS=`#version 300 es
precision highp float;
in vec3 aPos; in vec3 aNor; in float aType;
out vec3 vPos; out vec3 vNor; out float vType;
uniform mat4 uVP;
void main(){ vPos=aPos; vNor=aNor; vType=aType; gl_Position=uVP*vec4(aPos,1.0); }`;
const noiseGL=`
float h21(vec2 p){ p=fract(p*vec2(123.34,456.21)); p+=dot(p,p+45.32); return fract(p.x*p.y); }
float h31(vec3 p){ p=fract(p*vec3(127.1,311.7,74.7)); p+=dot(p,p+34.34); return fract(p.x*p.y*p.z); }
float vn2(vec2 p){ vec2 i=floor(p),f=fract(p); f=f*f*(3.0-2.0*f);
  float a=h21(i),b=h21(i+vec2(1,0)),c=h21(i+vec2(0,1)),d=h21(i+vec2(1,1));
  return mix(mix(a,b,f.x),mix(c,d,f.x),f.y); }
float fbm2(vec2 p){ float s=0.0,a=0.5; for(int i=0;i<4;i++){ s+=a*vn2(p); p*=2.03; a*=0.5; } return s; }`;
const lightGL=`
uniform vec3 uSunDir,uSunCol,uSkyAmb,uAmbDown,uFog,uCam;
uniform float uTime,uFogNear,uFogFar;
vec3 shade(vec3 col,vec3 n,vec3 wp,float emissive){
  float ndl=max(dot(n,uSunDir),0.0);
  float hemi=0.5+0.5*n.y;
  vec3 amb=mix(uAmbDown,uSkyAmb,hemi);
  vec3 lit=col*(amb+uSunCol*ndl)+col*emissive;
  float d=distance(uCam,wp);
  lit=mix(lit,uFog,smoothstep(uFogNear,uFogFar,d));
  return lit;
}`;
const blockFS=`#version 300 es
precision highp float;
in vec3 vPos; in vec3 vNor; in float vType; out vec4 frag;
`+noiseGL+lightGL+`
vec3 tint(vec3 n){
  int t=int(vType); vec3 wp=vPos; vec3 an=abs(n); vec2 uv;
  if(an.y>0.5) uv=vec2(wp.x,wp.z); else if(an.x>0.5) uv=vec2(wp.z,wp.y); else uv=vec2(wp.x,wp.y);
  vec2 local=fract(uv)*16.0; vec2 cell=floor(local); float g=h21(cell);
  float pv=h31(floor(wp)); vec3 col;
  if(t==1){ if(n.y>0.5){ col=mix(vec3(.40,.68,.30),vec3(.52,.82,.38),g); }
    else{ float band=fract(wp.y)>0.72?1.0:0.0; col=mix(vec3(.44,.34,.25),vec3(.48,.72,.34),band*(0.55+0.45*g)); } }
  else if(t==2){ col=mix(vec3(.40,.29,.21),vec3(.52,.39,.29),g); }
  else if(t==3){ float m=h21(floor(local*0.5)); col=mix(vec3(.46,.48,.52),vec3(.62,.65,.70),g*0.6+m*0.4); }
  else if(t==4){ float m=h21(floor(local/4.0)); col=mix(vec3(.36,.38,.42),vec3(.66,.69,.74),m);
    float mo=(local.x<0.7||local.y<0.7||local.x>15.3||local.y>15.3)?1.0:0.0; col*=1.0-mo*0.42; }
  else if(t==5){ col=mix(vec3(.82,.75,.58),vec3(.93,.87,.72),g); }
  else if(t==6){ if(n.y>0.5){ float r=length(fract(uv)*2.0-1.0); col=mix(vec3(.58,.44,.28),vec3(.80,.64,.42),sin(r*15.0)*0.5+0.5); }
    else{ float s=h21(vec2(floor(local.x*0.4),0.7)); col=mix(vec3(.40,.30,.21),vec3(.58,.45,.32),s); } }
  else if(t==7){ col=mix(vec3(.20,.42,.19),vec3(.42,.66,.31),h21(cell)); }
  else if(t==8){ col=mix(vec3(.30,.58,.80),vec3(.20,.42,.62),g); }
  else if(t==9){ float edge=(local.x<1.0||local.y<1.0||local.x>15.0||local.y>15.0)?1.0:0.0;
    col=mix(vec3(.78,.90,.95),vec3(.96,.99,1.0),edge); }
  else if(t==10){ float row=floor(local.y/4.0); float off=mod(row,2.0)*2.0;
    float bc=h21(floor((local.x+off)/5.0)); col=mix(vec3(.56,.26,.21),vec3(.74,.42,.33),bc);
    float mo=(local.y<0.8||mod(local.x+off,5.0)<0.8)?1.0:0.0; col=mix(col,vec3(.80,.78,.73),mo*0.8); }
  else if(t==11){ col=mix(vec3(.95,.74,.36),vec3(1.15,.95,.55),g); }
  else col=mix(vec3(.17,.19,.23),vec3(.30,.33,.38),g);
  col*=0.92+0.12*pv; return col;
}
void main(){
  vec3 n=normalize(vNor); float em=(int(vType)==11)?(0.55+0.35*h21(floor(fract(vPos.xz)*16.0))):0.0;
  vec3 lit=shade(tint(n),n,vPos,em);
  frag=vec4(pow(max(lit,0.0),vec3(0.92)),1.0);
}`;
const waterFS=`#version 300 es
precision highp float;
in vec3 vPos; in vec3 vNor; in float vType; out vec4 frag;
`+noiseGL+lightGL+`
void main(){
  vec3 n=normalize(vNor); vec3 wp=vPos;
  float w=sin(wp.x*0.7+wp.z*0.55+uTime*1.7)*0.5+sin(wp.z*0.85-wp.y*0.5+uTime*1.1)*0.5;
  float g=h21(floor(fract(vec2(wp.x,wp.z))*16.0));
  vec3 col=mix(vec3(.16,.36,.56),vec3(.34,.62,.82),0.55+0.3*w+0.2*g);
  float alpha=int(vType)==9?0.5:0.66;
  float fres=pow(1.0-abs(n.y),2.0);
  col=mix(col,uSkyAmb,fres*0.35);
  vec3 lit=shade(col,n,wp,int(vType)==11?0.5:0.0);
  frag=vec4(pow(max(lit,0.0),vec3(0.92)),alpha);
}`;
const skyVS=`#version 300 es
precision highp float;
in vec2 aNdc; out vec2 vNdc;
void main(){ vNdc=aNdc; gl_Position=vec4(aNdc,0.999,1.0); }`;
const skyFS=`#version 300 es
precision highp float;
in vec2 vNdc; out vec4 frag;
uniform vec3 uF,uR,uU,uSunDir,uSunCol,uMoonDir,uMoonCol,uZenith,uHorizon,uGround,uFog;
uniform vec2 uTan; uniform float uNight,uTime;
`+noiseGL+`
void main(){
  vec3 d=normalize(uF+uR*vNdc.x*uTan.x+uU*vNdc.y*uTan.y);
  float t=clamp(d.y,0.0,1.0);
  vec3 col=mix(uHorizon,uZenith,pow(t,0.62));
  if(d.y<0.0) col=mix(uHorizon,uGround,clamp(-d.y*3.5,0.0,1.0));
  float sd=dot(d,uSunDir);
  col+=uSunCol*smoothstep(0.9975,0.9992,sd)*2.2+uSunCol*pow(max(sd,0.0),90.0)*0.45;
  float md=dot(d,uMoonDir);
  col+=uMoonCol*smoothstep(0.9980,0.9995,md)*1.6+uMoonCol*pow(max(md,0.0),60.0)*0.22;
  if(d.y>0.02){
    vec3 sp=floor(d*140.0); float s=h31(sp);
    float tw=0.55+0.45*sin(uTime*2.2+s*40.0);
    col+=vec3(0.85,0.92,1.0)*step(0.972,s)*uNight*tw*0.9;
    vec2 cp=d.xz/max(d.y,0.08)*7.0+vec2(uTime*0.035,uTime*0.02);
    float c=fbm2(cp);
    float cloud=smoothstep(0.55,0.72,c)*smoothstep(0.02,0.22,d.y);
    vec3 cc=mix(vec3(0.08,0.12,0.20),vec3(0.94,0.96,1.0),1.0-uNight*0.85);
    col=mix(col,cc,cloud*0.75);
  }
  float low=smoothstep(-0.15,0.12,d.y);
  col=mix(uFog,col,low*0.9+0.1);
  frag=vec4(pow(max(col,0.0),vec3(0.92)),1.0);
}`;
const lineVS=`#version 300 es
precision highp float;
in vec3 aPos; uniform mat4 uVP; uniform vec3 uOrigin; uniform float uSize;
void main(){ gl_Position=uVP*vec4((aPos-0.5)*uSize+uOrigin+0.5,1.0); }`;
const lineFS=`#version 300 es
precision highp float; out vec4 frag; uniform vec3 uColor; uniform float uAlpha;
void main(){ frag=vec4(uColor,uAlpha); }`;
const partVS=`#version 300 es
precision highp float;
in vec3 aPos; in vec3 aCol; in float aAlpha; in float aSize;
uniform mat4 uVP; uniform vec3 uCam; uniform float uDPR;
out vec3 vCol; out float vAlpha;
void main(){ vec4 clip=uVP*vec4(aPos,1.0); gl_Position=clip;
  float d=max(distance(uCam,aPos),1.0);
  gl_PointSize=clamp(260.0/d,2.0,30.0)*aSize*uDPR;
  vCol=aCol; vAlpha=aAlpha; }`;
const partFS=`#version 300 es
precision highp float; in vec3 vCol; in float vAlpha; out vec4 frag;
void vec4MainPlaceholder(){}
void main(){ vec2 p=gl_PointCoord-0.5; float m=smoothstep(0.5,0.22,length(p));
  frag=vec4(vCol,m*vAlpha); }`;

const pBlock=prog(commonVS,blockFS), pWater=prog(commonVS,waterFS), pSky=prog(skyVS,skyFS),
      pLine=prog(lineVS,lineFS), pPart=prog(partVS,partFS);
pPart.fs=null;

/* buffers */
const quadBuf=gl.createBuffer();
gl.bindBuffer(gl.ARRAY_BUFFER,quadBuf);
gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,3,-1,-1,3]),gl.STATIC_DRAW);
const wireBuf=gl.createBuffer();
{const e=[[0,0,0,1,0,0],[1,0,0,1,1,0],[1,1,0,0,1,0],[0,1,0,0,0,0],[0,0,1,1,0,1],[1,0,1,1,1,1],[1,1,1,0,1,1],[0,1,1,0,0,1],[0,0,0,0,0,1],[1,0,0,1,0,1],[1,1,0,1,1,1],[0,1,0,0,1,1]];
 const a=new Float32Array(e.length*6); e.forEach((s,i)=>{a.set(s,i*6)});
 gl.bindBuffer(gl.ARRAY_BUFFER,wireBuf); gl.bufferData(gl.ARRAY_BUFFER,a,gl.STATIC_DRAW);}
const partBuf=gl.createBuffer();
const emptyVBO=gl.createBuffer();
gl.bindBuffer(gl.ARRAY_BUFFER,emptyVBO); gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([0,0,0,0,0,0,0]),gl.STATIC_DRAW);
const emptyIBO=gl.createBuffer();
gl.bindBuffer(gl.ARRAY_BUFFER,emptyIBO); gl.bufferData(gl.ARRAY_BUFFER,new Uint8Array(4),gl.STATIC_DRAW);

function attribBlock(vao){gl.bindBuffer(gl.ARRAY_BUFFER,vao.vbo);gl.enableVertexAttribArray(0);gl.vertexAttribPointer(0,3,gl.FLOAT,false,28,0);
  gl.enableVertexAttribArray(1);gl.vertexAttribPointer(1,3,gl.FLOAT,false,28,12);
  gl.enableVertexAttribArray(2);gl.vertexAttribPointer(2,1,gl.FLOAT,false,28,24);}
function attribSky(vao){gl.bindBuffer(gl.ARRAY_BUFFER,quadBuf);gl.enableVertexAttribArray(0);gl.vertexAttribPointer(0,2,gl.FLOAT,false,0,0);}

const VAO=[];
function makeVAO(){const v=gl.createVertexArray();VAO.push(v);return v}
const vaoBlock=makeVAO(),vaoWater=makeVAO(),vaoSky=makeVAO(),vaoLine=makeVAO(),vaoPart=makeVAO();
gl.bindVertexArray(vaoSky);attribSky(vaoSky);
gl.bindVertexArray(vaoLine);gl.bindBuffer(gl.ARRAY_BUFFER,wireBuf);gl.enableVertexAttribArray(0);gl.vertexAttribPointer(0,3,gl.FLOAT,false,0,0);
gl.bindVertexArray(vaoPart);gl.bindBuffer(gl.ARRAY_BUFFER,partBuf);
gl.enableVertexAttribArray(0);gl.vertexAttribPointer(0,3,gl.FLOAT,false,24,0);
gl.enableVertexAttribArray(1);gl.vertexAttribPointer(1,3,gl.FLOAT,false,24,12);
gl.enableVertexAttribArray(2);gl.vertexAttribPointer(2,1,gl.FLOAT,false,24,20);
gl.enableVertexAttribArray(3);gl.vertexAttribPointer(3,1,gl.FLOAT,false,24,24);
gl.bindVertexArray(null);

/* ================= チャンクメッシュ ================= */
const AX=[[1,2],[2,0],[0,1]];
function faceVisible(cur,nb){
  if(nb===AIR)return true;
  if(isOpaque(nb))return false;
  if(isTrans(cur))return cur!==nb;
  return true;
}
const chunks=[];
function initChunks(){chunks.length=0;for(let cz=0;cz<CZ;cz++)for(let cx=0;cx<CX;cx++)chunks.push({cx,cz,vbo:null,ibo:null,count:0,ivbo:null,ibo2:null,icount:0,center:[cx*CS+CS/2,SY/2,cz*CS+CS/2],r:Math.sqrt(CS*CS/2+SY*SY/4)})}
function buildChunk(c){
  const bx=c.cx*CS,bz=c.cz*CS;
  const op={pos:[],nor:[],ty:[],idx:[]}, tr={pos:[],nor:[],ty:[],idx:[]};
  for(let axis=0;axis<3;axis++){
    const ua=AX[axis][0],va=AX[axis][1],nu=[CS,SY,CS][ua],nv=[CS,SY,CS][va],np=[CS,SY,CS][axis];
    const mask=new Int16Array(nu*nv);
    for(let p=0;p<np;p++){
      for(const sign of [1,-1]){
        mask.fill(0);
        for(let u=0;u<nu;u++)for(let v=0;v<nv;v++){
          const gx=bx+(axis===0?p:(ua===0?u:v)), gy=(axis===1?p:(ua===1?u:v)), gz=bz+(axis===2?p:(ua===2?u:v));
          const cur=data[idx(gx,gy,gz)];
          if(cur===AIR)continue;
          const nx=gx+(axis===0?sign:0), ny=gy+(axis===1?sign:0), nz=gz+(axis===2?sign:0);
          if(faceVisible(cur,bAt(nx,ny,nz)))mask[u*nv+v]=cur;
        }
        if(!mask.some(v=>v))continue;
        const plane=(axis===0?bx:p)+(sign>0?1:0), bu=(axis===0?bx:(ua===0?bx:0)), bv=(axis===2?bz:(va===2?bz:0));
        const tgt=isTrans(cur0(mask))?tr:op;
        for(let u=0;u<nu;u++){
          for(let v=0;v<nv;v++){
            const t=mask[u*nv+v]; if(!t)continue;
            let h=1; while(u+h<nu&&mask[(u+h)*nv+v]===t)h++;
            let w=1; while(v+w<nv&&mask[u*nv+v+w]===t)w++;
            const g=tgt; const base=g.pos.length/3;
            const corners=[[u,v],[u+h,v],[u+h,v+w],[u,v+w]];
            for(const [cu,cv] of corners){
              const q=[0,0,0]; q[axis]=plane; q[ua]=bu+cu; q[va]=bv+cv;
              g.pos.push(q[0],q[1],q[2]);
              g.nor.push(axis===0?sign:0,axis===1?sign:0,axis===2?sign:0);
              g.ty.push(t);
            }
            g.idx.push(base,base+1,base+2,base,base+2,base+3);
            for(let i=0;i<h;i++)for(let j=0;j<w;j++)mask[(u+i)*nv+v+j]=0;
            v+=w-1;
          }
        }
      }
    }
  }
  function cur0(m){return 0}
  upload(c,op,'op');upload(c,tr,'tr');
}
function upload(c,arr,kind){
  const n=arr.pos.length/3;
  if(n===0){ if(c.vbo)gl.deleteBuffer(c.vbo); if(c.ibo)gl.deleteBuffer(c.ibo); if(c.ivbo)gl.deleteBuffer(c.ivbo); if(c.ibo2)gl.deleteBuffer(c.ibo2);
    c.vbo=emptyVBO;c.ibo=emptyIBO;c.count=0;c.ivbo=emptyVBO;c.ibo2=emptyIBO;c.icount=0; }
  const inter=new Float32Array(n*7);
  for(let i=0;i<n;i++){inter[i*7]=arr.pos[i*3];inter[i*7+1]=arr.pos[i*3+1];inter[i*7+2]=arr.pos[i*3+2];
    inter[i*7+3]=arr.nor[i*3];inter[i*7+4]=arr.nor[i*3+1];inter[i*7+5]=arr.nor[i*3+2];inter[i*7+6]=arr.ty[i]}
  if(kind==='op'){
    c.vbo=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,c.vbo);gl.bufferData(gl.ARRAY_BUFFER,inter,gl.STATIC_DRAW);
    c.ibo=gl.createBuffer();gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,c.ibo);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,new Uint32Array(arr.idx),gl.STATIC_DRAW);
    c.count=arr.idx.length;
    if(arr.idx.length===0){c.vbo=emptyVBO;c.ibo=emptyIBO;c.count=0}
  }else{
    c.ivbo=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,c.ivbo);gl.bufferData(gl.ARRAY_BUFFER,inter,gl.STATIC_DRAW);
    c.ibo2=gl.createBuffer();gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,c.ibo2);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,new Uint32Array(arr.idx),gl.STATIC_DRAW);
    c.icount=arr.idx.length;
    if(arr.idx.length===0){c.ivbo=emptyVBO;c.ibo2=emptyIBO;c.icount=0}
  }
}
function dirty(x,y,z){
  const cx=Math.floor(x/CS),cz=Math.floor(z/CS);
  const set=new Set();set.add(cx+','+cz);
  if(x===cx*CS)set.add((cx-1)+','+cz); if(x===cx*CS+CS-1)set.add((cx+1)+','+cz);
  if(z===cz*CS)set.add(cx+','+(cz-1)); if(z===cz*CS+CS-1)set.add(cx+','+(cz+1));
  for(const k of set){const [a,b]=k.split(',').map(Number);const c=chunks.find(cc=>cc.cx===a&&cc.cz===b);if(c)buildChunk(c)}
}

/* ================= 地形 ================= */
function generate(seed){
  const s=(seed|0)||1;
  data.fill(AIR);
  const hm=new Float32Array(SX*SZ);
  for(let z=0;z<SZ;z++)for(let x=0;x<SX;x++){
    const n=fbm(x*0.016,z*0.02,0,s,4);
    const m=fbm(x*0.004,z*0.005,0,s+17,3);
    hm[idx(x,0,z)]=8+n*16+m*m*30;
  }
  for(let z=0;z<SZ;z++)for(let x=0;x<SX;x++){
    const h=Math.floor(hm[idx(x,0,z)]);
    for(let y=0;y<SY;y++){
      let b=AIR;
      if(y===0)b=BEDROCK;
      else if(y<h)b=(y>h-3)?DIRT:STONE;
      else if(y===h)b=(h<=SEA+1)?SAND:(h>44?COBBLE:GRASS);
      else if(y<=SEA)b=WATER;
      if(y>1&&y<=h-1&&fbm(x*0.06,y*0.07,z*0.06,s+53,2)>0.68)b=AIR;
      if(b===STONE&&fbm(x*0.09,y*0.11,z*0.09,s+209,2)>0.78)b=GLOW;
      data[idx(x,y,z)]=b;
    }
    // 浜辺の砂
    if(h>SEA&&h<SEA+2)data[idx(x,h,z)]=SAND;
  }
  const rnd=mulberry(s*7919);
  for(let n=0;n<240;n++){
    const x=2+Math.floor(rnd()*(SX-4)), z=2+Math.floor(rnd()*(SZ-4));
    const h=Math.floor(hm[idx(x,0,z)]);
    if(h<=SEA+1||h>42)continue;
    if(data[idx(x,h,z)]!==GRASS)continue;
    const th=4+Math.floor(rnd()*3);
    if(h+th+2>=SY)continue;
    for(let y=h+1;y<=h+th;y++)data[idx(x,y,z)]=LOG;
    const top=h+th;
    for(let dy=top-2;dy<=top+1;dy++){
      const r=(dy>=top)?1:2;
      for(let dx=-r;dx<=r;dx++)for(let dz=-r;dz<=r;dz++){
        if(dx===0&&dz===0&&dy<=top)continue;
        if(Math.abs(dx)===2&&Math.abs(dz)===2&&dy>=top)continue;
        const px=x+dx,pz=z+dz,py=dy;
        if(px<0||px>=SX||pz<0||pz>=SZ||py>=SY)continue;
        const i=idx(px,py,pz);
        if(data[i]===AIR)data[i]=LEAF;
      }
    }
  }
}

/* ================= カメラ / 行列 ================= */
function persp(fov,asp,n,f){const t=1/Math.tan(fov/2),nf=1/(n-f);
  return [t/asp,0,0,0, 0,t,0,0, 0,0,(f+n)*nf,-1, 0,0,2*f*n*nf,0]}
function mul(a,b){const o=new Array(16);
  for(let i=0;i<4;i++)for(let j=0;j<4;j++){let s=0;for(let k=0;k<4;k++)s+=a[k*4+i]*b[j*4+k];o[j*4+i]=s}return o}
function viewMat(e,dir,up){
  const z=[-dir[0],-dir[1],-dir[2]];
  let x=[up[1]*z[2]-up[2]*z[1], up[2]*z[0]-up[0]*z[2], up[0]*z[1]-up[1]*z[0]];
  const lx=Math.hypot(x[0],x[1],x[2]);x=[x[0]/lx,x[1]/lx,x[2]/lx];
  const y=[z[1]*x[2]-z[2]*x[1], z[2]*x[0]-z[0]*x[2], z[0]*x[1]-z[1]*x[0]];
  return [x[0],y[0],z[0],0, x[1],y[1],z[1],0, x[2],y[2],z[2],0,
    -(x[0]*e[0]+x[1]*e[1]+x[2]*e[2]), -(y[0]*e[0]+y[1]*e[1]+y[2]*e[2]), -(z[0]*e[0]+z[1]*e[1]+z[2]*e[2]),1]
}
let VP=new Array(16), cam=[0,0,0], fwd=[0,0,-1], right=[1,0,0], up=[0,1,0], aspect=1, tanFov=Math.tan(0.62);
let dpr=1,W=0,H=0;
function resize(){
  dpr=Math.min(window.devicePixelRatio||1,1.6);
  W=Math.floor(canvas.width=dpr*canvas.clientWidth);
  H=Math.floor(canvas.height=dpr*canvas.clientHeight);
  aspect=W/H; gl.viewport(0,0,W,H);
}

/* ================= プレイヤー ================= */
const P={pos:[SX/2,30,SZ/2],vel:[0,0,0],yaw:0.4,pitch:0.15,onGround:false,fly:false,sprint:false,sneak:false,inWater:false};
const HW=0.3,PH=1.8,EYE=1.62;
function keys={};
function move(dt){
  const spd=P.fly?14:(P.inWater?3.2:(P.sneak?1.5:(P.sprint?7.0:4.2)));
  const fx=Math.sin(P.yaw),fz=-Math.cos(P.yaw);
  let mx=(keys['w']?1:0)-(keys['s']?1:0), mz=(keys['a']?1:0)-(keys['d']?1:0);
  const dirx=fx*mx+Math.cos(P.yaw)*mz, dirz=fz*mx-Math.sin(P.yaw)*mz;
  const len=Math.hypot(dirx,dirz)||1;
  let vx=dirx/len*spd, vz=dirz/len*spd;
  if(keys[' ']&&P.fly)vyIn=spd;if(keys['shift']&&P.fly)vyIn=-spd;
  if(keys[' ']&&P.inWater&&!P.fly)vyIn=spd*0.7;
  if(keys['shift']&&P.inWater&&!P.fly)vyIn=-spd*0.7;
  let vy=vyIn||0;
  if(P.fly){P.vel=[vx,vy,vz]}
  else{
    if(P.inWater){P.vel=[vx,vy-(P.inWater?4:0),vz]}
    else{P.vel=[vx,vy,vz];P.vel[1]-=22*dt}
  }
  const prevY=P.pos[1];
  P.pos[0]=resolve(0,vx*dt);P.pos[2]=resolve(2,vz*dt);P.pos[1]=resolve(1,P.vel[1]*dt);
  if(P.pos[1]!==prevY){
    const vyv=P.vel[1];
    if(vyv<0&&P.pos[1]+PH-(prevY+PH)>=0){}
    if(P.vel[1]<=0&&prevY>P.pos[1]+0.001&&Math.abs(prevY-P.pos[1])>0.05){
      P.onGround=true;sfx.step(Math.min(1,Math.abs(prevY-P.pos[1])*1.2));
      spawnDust(P.pos[0],P.pos[1],P.pos[2]);
    }
  }
  if(!P.fly){
    const feet=Math.floor(P.pos[1]),mid=Math.floor(P.pos[1]+0.5);
    P.inWater=bAt(Math.floor(P.pos[0]),feet,Math.floor(P.pos[2]))===WATER||bAt(Math.floor(P.pos[0]),mid,Math.floor(P.pos[2]))===WATER;
    P.onGround=P.vel[1===0?1:1]!==undefined&&groundCheck();
    if(P.onGround&&keys[' ']&&P.vel[1]<=0){P.vel[1]=P.inWater?5.2:8.3;P.onGround=false;sfx.jump()}
  }else P.onGround=false;
}
let vyIn=0;
function groundCheck(){
  const y=Math.floor(P.pos[1]-0.05);
  for(let x=Math.floor(P.pos[0]-HW);x<=Math.floor(P.pos[0]+HW);x++)
    for(let z=Math.floor(P.pos[2]-HW);z<=Math.floor(P.pos[2]+HW);z++)
      if(isSolid(bAt(x,y,z)))return true;
  return false;
}
function resolve(axis,d){
  P.pos[axis]+=d;
  const minx=P.pos[0]-HW,maxx=P.pos[0]+HW,miny=P.pos[1],maxy=P.pos[1]+PH,minz=P.pos[2]-HW,maxz=P.pos[2]+HW;
  const x0=Math.floor(minx),x1=Math.floor(maxx),y0=Math.floor(miny),y1=Math.floor(maxy),z0=Math.floor(minz),z1=Math.floor(maxz);
  const vel=P.vel[axis];
  for(let x=x0;x<=x1;x++)for(let y=y0;y<=y1;y++)for(let z=z0;z<=z1;z++){
    if(!isSolid(bAt(x,y,z)))continue;
    if(axis===0){ if(vel>0)P.pos[0]=Math.min(P.pos[0],x-HW-1e-3); else if(vel<0)P.pos[0]=Math.max(P.pos[0],x+1+HW+1e-3); P.vel[0]=0; }
    if(axis===1){ if(vel>0){P.pos[1]=Math.min(P.pos[1],y-PH-1e-3);P.vel[1]=0} else if(vel<0){P.pos[1]=Math.max(P.pos[1],y+1+1e-3);P.vel[1]=0;P.onGround=true} }
    if(axis===2){ if(vel>0)P.pos[2]=Math.min(P.pos[2],z-HW-1e-3); else if(vel<0)P.pos[2]=Math.max(P.pos[2],z+1+HW+1e-3); P.vel[2]=0; }
    const nminx=P.pos[0]-HW,maxnx=P.pos[0]+HW,nminy=P.pos[1],maxny=P.pos[1]+PH,nminz=P.pos[2]-HW,maxnz=P.pos[2]+HW;
    if(maxnx<=x||nminx>=x+1||maxny<=y||nminy>=y+1||maxnz<=z||nminz>=z+1)continue;
  }
  if(axis===1&&!keys[' ']&&P.vel[1]<0){}
  return P.pos[axis];
}

/* ================= レイキャスト ================= */
function raycast(o,d,maxD){
  let x=Math.floor(o[0]),y=Math.floor(o[1]),z=Math.floor(o[2]);
  const step=[Math.sign(d[0]),Math.sign(d[1]),Math.sign(d[2])];
  const tDelta=[Math.abs(1/d[0]),Math.abs(1/d[1]),Math.abs(1/d[2])];
  let tMax=[step[0]>0?(x+1-o[0])*tDelta[0]:(o[0]-x)*tDelta[0],
            step[1]>0?(y+1-o[1])*tDelta[1]:(o[1]-y)*tDelta[1],
            step[2]>0?(z+1-o[2])*tDelta[2]:(o[2]-z)*tDelta[2]];
  let t=0,n=[0,0,0];
  for(let i=0;i<120&&t<maxD;i++){
    const b=bAt(x,y,z);
    if(b!==AIR&&b!==WATER)return{x,y,z,n};
    if(tMax[0]<tMax[1]&&tMax[0]<tMax[2]){x+=step[0];t=tMax[0];tMax[0]+=tDelta[0];n=[-step[0],0,0]}
    else if(tMax[1]<tMax[2]){y+=step[1];t=tMax[1];tMax[1]+=tDelta[1];n=[0,-step[1],0]}
    else{z+=step[2];t=tMax[2];tMax[2]+=tDelta[2];n=[0,0,-step[2]]}
  }
  return null;
}

/* ================= 編集 ================= */
let sel=0, target=null, ghost=null;
function breakBlock(){
  if(!target)return;
  const b=bAt(target.x,target.y,target.z);
  if(b===BEDROCK){toast('岩盤は壊せない');return}
  data[idx(target.x,target.y,target.z)]=AIR;
  dirty(target.x,target.y,target.z);
  spawnBreak(target.x,target.y,target.z,b);
  sfx.break();pulse('hit');toast(NAMES[b]+' を破壊');
  target=null;
}
function placeBlock(){
  if(!target)return;
  const px=target.x+target.n[0],py=target.y+target.n[1],pz=target.z+target.n[2];
  if(py<1||py>=SY)return;
  const cur=bAt(px,py,pz);
  if(cur!==AIR&&cur!==WATER)return;
  const b=hotbar[sel];
  if(isSolid(b)){
    const minx=P.pos[0]-HW,maxx=P.pos[0]+HW,miny=P.pos[1],maxy=P.pos[1]+PH,minz=P.pos[2]-HW,maxz=P.pos[2]+HW;
    if(maxx>px&&minx<px+1&&maxy>py&&miny<py+1&&maxz>pz&&minz<pz+1){toast('プレイヤーが重なっている');return}
  }
  data[idx(px,py,pz)]=b;dirty(px,py,pz);
  spawnPlace(px,py,pz,b);sfx.place();pulse('place');toast(NAMES[b]+' を設置');
}
function pickBlock(){
  if(!target)return;
  const b=bAt(target.x,target.y,target.z);
  const at=hotbar.indexOf(b);
  if(at>=0){sel=at;renderBar()}else toast(NAMES[b]+' はホットバーにない');
}

/* ================= パーティクル ================= */
const parts=[];
function spawn(x,y,z,col,n,spread,life,size){
  for(let i=0;i<n;i++){
    if(parts.length>420)break;
    parts.push({p:[x,y,z],v:[(Math.random()-.5)*spread,(Math.random()*0.6+0.25)*spread,(Math.random()-.5)*spread],
      c:col,a:1,l:life*(0.6+Math.random()*0.6),s:size});
  }
}
function spawnBreak(x,y,z,b){const c=PAL[b];spawn(x+.5,y+.5,z+.5,[c[0],c[1],c[2]],12,4.2,0.7,0.9)}
function spawnPlace(x,y,z,b){const c=PAL[b];spawn(x+.5,y+.5,z+.5,[c[0],c[1],c[2]],6,2.4,0.4,0.7)}
function spawnDust(x,y,z){spawn(x,y+.1,z,[.6,.62,.66],7,2.6,0.4,0.6)}
function updateParts(dt){
  for(let i=parts.length-1;i>=0;i--){
    const q=parts[i];
    q.v[1]-=16*dt;q.p[0]+=q.v[0]*dt;q.p[1]+=q.v[1]*dt;q.p[2]+=q.v[2]*dt;
    const bx=Math.floor(q.p[0]),by=Math.floor(q.p[1]),bz=Math.floor(q.p[2]);
    if(isSolid(bAt(bx,by,bz))&&q.v[1]<0){q.p[1]=by+1+0.02;q.v[1]*=-0.3;q.v[0]*=0.6;q.v[2]*=0.6}
    q.l-=dt;q.a=Math.max(0,Math.min(1,q.l*2));
    if(q.l<=0)parts.splice(i,1);
  }
}
function drawParts(){
  const n=parts.length;if(!n)return;
  const arr=new Float32Array(n*8);
  for(let i=0;i<n;i++){const q=parts[i];arr.set([q.p[0],q.p[1],q.p[2],q.c[0],q.c[1],q.c[2],q.a,q.s],i*8)}
  gl.bindBuffer(gl.ARRAY_BUFFER,partBuf);gl.bufferData(gl.ARRAY_BUFFER,arr,gl.DYNAMIC_DRAW);
  gl.bindVertexArray(vaoPart);
  gl.useProgram(pPart);
  gl.uniformMatrix4fv(pPart.u.uVP,false,VP);gl.uniform3fv(pPart.u.uCam,cam);gl.uniform1f(pPart.u.uDPR,dpr);
  gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);gl.depthMask(false);
  gl.drawArrays(gl.POINTS,0,n);
  gl.depthMask(true);gl.disable(gl.BLEND);
  gl.bindVertexArray(null);
}

/* ================= 音 ================= */
let actx=null,sound=true,nb=null;
function ensureAudio(){if(!actx){actx=new(window.AudioContext||window.webkitAudioContext)();
  nb=actx.createBuffer(1,actx.sampleRate*0.5,actx.sampleRate);
  const d=nb.getChannelData(0);for(let i=0;i<d.length;i++)d[i]=Math.random()*2-1;}}
function burst(vol,dur,f0,f1,q){
  if(!sound||!actx)return;ensureAudio();
  const src=actx.createBufferSource();src.buffer=nb;src.loop=true;
  const bp=actx.createBiquadFilter();bp.type='bandpass';bp.Q.value=q||1.2;
  bp.frequency.setValueAtTime(f0,actx.currentTime);bp.frequency.exponentialRampToValueAtTime(f1,