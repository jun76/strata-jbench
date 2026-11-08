下のコードをそのまま `.html` として保存し、ブラウザで開くと遊べる「マイクラ風 3D 箱庭」です。

- WASD: 移動
- Space: ジャンプ
- Shift: ダッシュ
- マウス: 視点
- 左クリック: 破壊
- 右クリック: 設置
- 1〜9 / ホイール: ブロック選択
- 中クリック: 対象ブロックをコピー
- クリック画面でポインターロック開始

```html
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>マイクラ風 3D 箱庭</title>
<style>
  html, body {
    margin: 0;
    padding: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
    background: #79c7e8;
    font-family: sans-serif;
    user-select: none;
  }
  #game {
    position: fixed;
    inset: 0;
  }
  #crosshair {
    position: fixed;
    left: 50%;
    top: 50%;
    width: 24px;
    height: 24px;
    transform: translate(-50%, -50%);
    pointer-events: none;
    opacity: 0.85;
    z-index: 10;
  }
  #crosshair::before,
  #crosshair::after {
    content: "";
    position: absolute;
    background: white;
    box-shadow: 0 0 2px rgba(0,0,0,0.7);
  }
  #crosshair::before {
    left: 11px;
    top: 0;
    width: 2px;
    height: 24px;
  }
  #crosshair::after {
    top: 11px;
    left: 0;
    width: 24px;
    height: 2px;
  }
  #hotbar {
    position: fixed;
    bottom: 18px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: 6px;
    z-index: 11;
    padding: 6px;
    background: rgba(0,0,0,0.25);
    border-radius: 8px;
  }
  .slot {
    width: 44px;
    height: 44px;
    border: 2px solid rgba(255,255,255,0.35);
    background: rgba(30,30,30,0.55);
    border-radius: 5px;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: bold;
  }
  .slot.selected {
    border-color: #fff;
    box-shadow: 0 0 10px #fff;
  }
  .slot .key {
    position: absolute;
    top: 2px;
    left: 3px;
    font-size: 10px;
    opacity: 0.8;
  }
  .slot .icon {
    width: 28px;
    height: 28px;
    border-radius: 4px;
    border: 1px solid rgba(0,0,0,0.4);
  }
  #ui {
    position: fixed;
    top: 12px;
    left: 12px;
    color: white;
    text-shadow: 0 1px 3px #000;
    font-size: 13px;
    line-height: 1.35;
    z-index: 12;
    pointer-events: none;
  }
  #overlay {
    position: fixed;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(10,15,25,0.55);
    color: white;
    z-index: 30;
  }
  #overlay.hidden { display: none; }
  #panel {
    background: rgba(10,15,25,0.78);
    padding: 26px 34px;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.25);
    text-align: center;
    max-width: 520px;
  }
  #panel h1 {
    margin: 0 0 14px;
    font-size: 30px;
  }
  #panel p {
    margin: 7px 0;
    line-height: 1.5;
  }
  #startBtn {
    margin-top: 18px;
    padding: 10px 28px;
    font-size: 18px;
    border: 0;
    border-radius: 7px;
    cursor: pointer;
    background: #46a24c;
    color: white;
  }
</style>
</head>
<body>
<div id="game"></div>
<div id="crosshair"></div>
<div id="ui">
  <div>座標: <span id="coords">0, 0, 0</span></div>
  <div>選択: <span id="blockName">草</span></div>
  <div>FPS: <span id="fps">0</span></div>
</div>
<div id="hotbar"></div>
<div id="overlay">
  <div id="panel">
    <h1>マイクラ風 3D 箱庭</h1>
    <p><b>WASD</b> 移動 / <b>Space</b> ジャンプ / <b>Shift</b> ダッシュ</p>
    <p><b>左クリック</b> 破壊 / <b>右クリック</b> 設置</p>
    <p><b>1〜9</b> / <b>ホイール</b> ブロック選択 / <b>中クリック</b> 対象をコピー</p>
    <p>ESC でマウス解放</p>
    <button id="startBtn">ゲーム開始</button>
  </div>
</div>

<script type="importmap">
{
  "imports": {
    "three": "https://unpkg.com/three@0.160.0/build/three.module.js"
  }
}
</script>

<script type="module">
import * as THREE from "three";

/* =========================================================
 * 定数・ワールド設定
 * ========================================================= */
const WX = 64;
const WZ = 64;
const WY = 64;
const CHUNK = 16;
const CX = Math.floor(WX / CHUNK);
const CZ = Math.floor(WZ / CHUNK);
const SEA = 12;

const AIR = 0;
const GRASS = 1;
const DIRT = 2;
const STONE = 3;
const WOOD = 4;
const LEAVES = 5;
const SAND = 6;
const PLANKS = 7;
const WATER = 8;
const GLASS = 9;

const HOTBAR = [GRASS, DIRT, STONE, WOOD, LEAVES, SAND, PLANKS, WATER, GLASS];

const BLOCK_INFO = {
  [GRASS]:  { name: "草",   color: "#6ab150" },
  [DIRT]:   { name: "土",   color: "#7a4c2b" },
  [STONE]:  { name: "石",   color: "#8b8b8b" },
  [WOOD]:   { name: "木",   color: "#78562f" },
  [LEAVES]: { name: "葉",   color: "#3c7a34" },
  [SAND]:   { name: "砂",   color: "#dbcb8d" },
  [PLANKS]: { name: "板",   color: "#a6723a" },
  [WATER]:  { name: "水",   color: "#3f86ff" },
  [GLASS]:  { name: "ガラス", color: "#cfefff" }
};

const PLAYER_HEIGHT = 1.8;
const PLAYER_RADIUS = 0.32;
const EYE = 1.62;
const GRAVITY = 28;
const JUMP = 8.8;
const SPEED = 5.2;
const SPRINT_SPEED = 8.8;
const MOUSE_SENS = 0.0022;
const REACH = 6.2;

/* =========================================================
 * ユーティリティ
 * ========================================================= */
function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }

function hash2(x, y) {
  let h = x * 374761393 + y * 668265263;
  h = (h ^ (h >>> 13)) * 1274126177;
  return (h ^ (h >>> 16)) >>> 0;
}

function rand2(x, y) {
  return hash2(x, y) / 4294967295;
}

function smooth(t) {
  return t * t * (3.0 - 2.0 * t);
}

function noise2D(x, y) {
  const xi = Math.floor(x);
  const yi = Math.floor(y);
  const xf = x - xi;
  const yf = y - yi;

  const a = rand2(xi, yi);
  const b = rand2(xi + 1, yi);
  const c = rand2(xi, yi + 1);
  const d = rand2(xi + 1, yi + 1);

  const u = smooth(xf);
  const v = smooth(yf);

  return (a * (1 - u) + b * u) * (1 - v) + (c * (1 - u) + d * u) * v;
}

function fbm(x, y) {
  return (
    0.55 * noise2D(x, y) +
    0.28 * noise2D(x * 2.0, y * 2.0) +
    0.17 * noise2D(x * 4.0, y * 4.0)
  );
}

/* =========================================================
 * 世界データ
 * ========================================================= */
const world = new Uint8Array(WX * WZ * WY);

function idx(x, y, z) {
  return (y * WZ + z) * WX + x;
}

function getBlock(x, y, z) {
  if (x < 0 || x >= WX || y < 0 || y >= WY || z < 0 || z >= WZ) return AIR;
  return world[idx(x, y, z)];
}

function setBlock(x, y, z, id) {
  if (x < 0 || x >= WX || y < 0 || y >= WY || z < 0 || z >= WZ) return false;
  world[idx(x, y, z)] = id;
  return true;
}

function isCollisionSolid(x, y, z) {
  if (x < 0 || x >= WX || z < 0 || z >= WZ || y < 0) return true;
  if (y >= WY) return false;
  const id = getBlock(x, y, z);
  return id !== AIR && id !== WATER;
}

function occludesFor(id, nb) {
  if (nb === AIR) return false;

  if (id === WATER) {
    // 水は空気・ガラス以外で覆われていれば見えない
    return nb !== GLASS;
  }

  if (id === GLASS) {
    // ガラスはガラスや不透明ブロックで覆われていれば見えない
    return nb === GLASS || (nb !== AIR && nb !== WATER);
  }

  // 通常ブロックは不透明ブロックで覆われていれば見えない
  return nb !== AIR && nb !== WATER && nb !== GLASS;
}

function isBlockVisible(x, y, z, id) {
  if (id === AIR) return false;

  const neighbors = [
    getBlock(x + 1, y, z),
    getBlock(x - 1, y, z),
    getBlock(x, y + 1, z),
    getBlock(x, y - 1, z),
    getBlock(x, y, z + 1),
    getBlock(x, y, z - 1)
  ];

  for (const nb of neighbors) {
    if (!occludesFor(id, nb)) return true;
  }
  return false;
}

/* =========================================================
 * テクスチャ生成
 * ========================================================= */
function makeTexture(draw) {
  const size = 16;
  const canvas = document.createElement("canvas");
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext("2d");
  draw(ctx, size);

  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.magFilter = THREE.NearestFilter;
  tex.minFilter = THREE.LinearMipmapLinearFilter;
  tex.anisotropy = 4;
  tex.needsUpdate = true;
  return tex;
}

function hexToRgb(hex) {
  const n = parseInt(hex.replace("#", ""), 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}

function rgbToHex(r, g, b) {
  return "#" + [r, g, b].map(v => clamp(Math.round(v), 0, 255).toString(16).padStart(2, "0")).join("");
}

function shade(hex, amount) {
  const [r, g, b] = hexToRgb(hex);
  return rgbToHex(
    r + amount + (Math.random() * 20 - 10),
    g + amount + (Math.random() * 20 - 10),
    b + amount + (Math.random() * 20 - 10)
  );
}

function fillNoise(ctx, base, variance = 18, density = 0.55) {
  ctx.fillStyle = base;
  ctx.fillRect(0, 0, 16, 16);
  for (let y = 0; y < 16; y++) {
    for (let x = 0; x < 16; x++) {
      if (Math.random() < density) {
        ctx.fillStyle = shade(base, Math.random() * variance * 2 - variance);
        ctx.fillRect(x, y, 1, 1);
      }
    }
  }
}

const grassTopTex = makeTexture((ctx) => {
  fillNoise(ctx, "#6ab150", 22, 0.75);
  for (let i = 0; i < 10; i++) {
    ctx.fillStyle = "#52923b";
    ctx.fillRect(Math.floor(Math.random() * 16), Math.floor(Math.random() * 16), 1, 1);
  }
});

const grassSideTex = makeTexture((ctx) => {
  fillNoise(ctx, "#7a4c2b", 14, 0.65);
  ctx.fillStyle = "#6ab150";
  for (let x = 0; x < 16; x++) {
    const h = 3 + (Math.random() < 0.35 ? 1 : 0) + (Math.random() < 0.12 ? 1 : 0);
    ctx.fillRect(x, 0, 1, h);
    ctx.fillStyle = shade("#6ab150", Math.random() * 14 - 7);
  }
});

const dirtTex = makeTexture((ctx) => {
  fillNoise(ctx, "#7a4c2b", 18, 0.7);
});

const stoneTex = makeTexture((ctx) => {
  fillNoise(ctx, "#8b8b8b", 16, 0.7);
  ctx.fillStyle = "#757575";
  for (let i = 0; i < 8; i++) {
    ctx.fillRect(Math.floor(Math.random() * 16), Math.floor(Math.random() * 16), 2, 1);
  }
});

const woodSideTex = makeTexture((ctx) => {
  ctx.fillStyle = "#78562f";
  ctx.fillRect(0, 0, 16, 16);
  for (let x = 0; x < 16; x += 3) {
    ctx.fillStyle = "#654624";
    ctx.fillRect(x, 0, 1, 16);
  }
  for (let i = 0; i < 40; i++) {
    ctx.fillStyle = shade("#78562f", Math.random() * 20 - 10);
    ctx.fillRect(Math.floor(Math.random() * 16), Math.floor(Math.random() * 16), 1, 1);
  }
});

const woodTopTex = makeTexture((ctx) => {
  ctx.fillStyle = "#9a703e";
  ctx.fillRect(0, 0, 16, 16);
  ctx.strokeStyle = "#6f4e24";
  for (let r = 2; r < 8; r += 2) {
    ctx.beginPath();
    ctx.arc(8, 8, r, 0, Math.PI * 2);
    ctx.stroke();
  }
});

const leavesTex = makeTexture((ctx) => {
  fillNoise(ctx, "#3c7a34", 18, 0.85);
  for (let i = 0; i < 18; i++) {
    ctx.fillStyle = "#2f6228";
    ctx.fillRect(Math.floor(Math.random() * 16), Math.floor(Math.random() * 16), 1, 1);
  }
});

const sandTex = makeTexture((ctx) => {
  fillNoise(ctx, "#dbcb8d", 12, 0.6);
});

const plankTex = makeTexture((ctx) => {
  fillNoise(ctx, "#a6723a", 12, 0.55);
  ctx.fillStyle = "#77522a";
  ctx.fillRect(0, 4, 16, 1);
  ctx.fillRect(0, 8, 16, 1);
  ctx.fillRect(0, 12, 16, 1);
});

const waterTex = makeTexture((ctx) => {
  fillNoise(ctx, "#3f86ff", 12, 0.6);
  ctx.strokeStyle = "rgba(255,255,255,0.18)";
  for (let i = 0; i < 4; i++) {
    ctx.beginPath();
    const y = 2 + i * 4;
    for (let x = 0; x < 16; x++) {
      ctx.lineTo(x, y + Math.sin((x + i) * 0.7) * 0.5);
    }
    ctx.stroke();
  }
});

const glassTex = makeTexture((ctx) => {
  ctx.clearRect(0, 0, 16, 16);
  ctx.fillStyle = "rgba(200,240,255,0.35)";
  ctx.fillRect(1, 1, 14, 14);
  ctx.strokeStyle = "rgba(255,255,255,0.75)";
  ctx.lineWidth = 1;
  ctx.strokeRect(1.5, 1.5, 13, 13);
});

/* =========================================================
 * マテリアル
 * ========================================================= */
function lambert(tex, options = {}) {
  return new THREE.MeshLambertMaterial({
    map: tex,
    transparent: false,
    ...options
  });
}

const grassSideMat = lambert(grassSideTex);
const grassTopMat = lambert(grassTopTex);
const dirtMat = lambert(dirtTex);
const stoneMat = lambert(stoneTex);
const woodSideMat = lambert(woodSideTex);
const woodTopMat = lambert(woodTopTex);
const leavesMat = lambert(leavesTex);
const sandMat = lambert(sandTex);
const plankMat = lambert(plankTex);

const waterMat = lambert(waterTex, {
  transparent: true,
  opacity: 0.62,
  depthWrite: false
});

const glassMat = lambert(glassTex, {
  transparent: true,
  opacity: 0.45,
  depthWrite: true
});

const materials = new Array(10).fill(null);
materials[GRASS] = [grassSideMat, grassSideMat, grassTopMat, dirtMat, grassSideMat, grassSideMat];
materials[DIRT] = dirtMat;
materials[STONE] = stoneMat;
materials[WOOD] = [woodSideMat, woodSideMat, woodTopMat, woodTopMat, woodSideMat, woodSideMat];
materials[LEAVES] = leavesMat;
materials[SAND] = sandMat;
materials[PLANKS] = plankMat;
materials[WATER] = waterMat;
materials[GLASS] = glassMat;

/* =========================================================
 * Three.js 初期化
 * ========================================================= */
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x79c7e8);
scene.fog = new THREE.Fog(0x79c7e8, 34, 92);

const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.08, 260);
camera.rotation.order = "YXZ";

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
document.getElementById("game").appendChild(renderer.domElement);

const hemiLight = new THREE.HemisphereLight(0xbfd7ff, 0x556b3a, 0.85);
scene.add(hemiLight);

const dirLight = new THREE.DirectionalLight(0xffffff, 1.15);
dirLight.position.set(28, 64, 16);
scene.add(dirLight);

const ambientLight = new THREE.AmbientLight(0xffffff, 0.22);
scene.add(ambientLight);

const chunkRoot = new THREE.Group();
scene.add(chunkRoot);

const chunkGroups = new Array(CX * CZ).fill(null);
const cubeGeo = new THREE.BoxGeometry(1, 1, 1);
const dummyMatrix = new THREE.Matrix4();

/* =========================================================
 * 地形生成
 * ========================================================= */
function generateWorld() {
  for (let z = 0; z < WZ; z++) {
    for (let x = 0; x < WX; x++) {
      const n1 = fbm(x / 22.0, z / 22.0);
      const n2 = fbm(x / 75.0 + 31.7, z / 75.0 + 17.3);
      let h = Math.floor(9 + n1 * 20 + n2 * 8);
      h = clamp(h, 2, 40);

      const waterTop = Math.max(SEA, h);

      for (let y = 0; y <= h; y++) {
        let id = STONE;
        if (y === h) {
          if (h <= SEA + 1) id = SAND;
          else id = GRASS;
        } else if (h - y <= 3) {
          id = DIRT;
        } else {
          id = STONE;
        }
        setBlock(x, y, z, id);
      }

      for (let y = h + 1; y <= SEA; y++) {
        setBlock(x, y, z, WATER);
      }
    }
  }

  // 木
  for (let z = 3; z < WZ - 3; z++) {
    for (let x = 3; x < WX - 3; x++) {
      if (getBlock(x, SEA, z) === GRASS && rand2(x * 17 + 9, z * 23 + 5) < 0.018) {
        let groundY = -1;
        for (let y = SEA + 6; y >= SEA; y--) {
          if (getBlock(x, y, z) === GRASS) {
            groundY = y;
            break;
          }
        }
        if (groundY < 0) continue;
        if (getBlock(x, groundY + 1, z) !== AIR) continue;

        const treeHeight = 4 + Math.floor(rand2(x, z) * 3);
        const topY = groundY + treeHeight;

        for (let y = groundY + 1; y <= topY; y++) {
          setBlock(x, y, z, WOOD);
        }

        const leafStartY = topY - 2;
        const leafEndY = topY + 1;
        for (let dy = leafStartY; dy <= leafEndY; dy++) {
          const r = dy === leafEndY ? 1 : 2;
          for (let dx = -r; dx <= r; dx++) {
            for (let dz = -r; dz <= r; dz++) {
              if (Math.abs(dx) + Math.abs(dz) === 2 && r === 2) continue;
              const wx = x + dx;
              const wz = z + dz;
              if (getBlock(wx, dy, wz) === AIR) {
                setBlock(wx, dy, wz, LEAVES);
              }
            }
          }
        }
      }
    }
  }
}

/* =========================================================
 * チャンク再構築
 * ========================================================= */
function chunkKey(cx, cz) {
  return cx + cz * CX;
}

function disposeChunkGroup(group) {
  if (!group) return;
  chunkRoot.remove(group);
  group.traverse((obj) => {
    if (obj.isInstancedMesh) {
      // 共有マテリアル/ジオメトリは破棄しない
      obj.userData.blockList = null;
    }
  });
}

function rebuildChunk(cx, cz) {
  if (cx < 0 || cx >= CX || cz < 0 || cz >= CZ) return;

  const key = chunkKey(cx, cz);
  disposeChunkGroup(chunkGroups[key]);

  const group = new THREE.Group();
  group.position.set(cx * CHUNK, 0, cz * CHUNK);

  const dataByType = new Map();

  const baseX = cx * CHUNK;
  const baseZ = cz * CHUNK;

  for (let z = 0; z < CHUNK; z++) {
    const wz = baseZ + z;
    for (let y = 0; y < WY; y++) {
      for (let x = 0; x < CHUNK; x++) {
        const wx = baseX + x;
        const id = getBlock(wx, y, wz);
        if (id === AIR) continue;
        if (!isBlockVisible(wx, y, wz, id)) continue;

        let entry = dataByType.get(id);
        if (!entry) {
          entry = {
            matrices: [],
            blockList: []
          };
          dataByType.set(id, entry);
        }

        dummyMatrix.makeTranslation(x + 0.5, y + 0.5, z + 0.5);
        entry.matrices.push(dummyMatrix.clone());
        entry.blockList.push([wx, y, wz]);
      }
    }
  }

  for (const [id, entry] of dataByType.entries()) {
    const count = entry.matrices.length;
    if (count === 0) continue;

    const mat = materials[id];
    if (!mat) continue;

    const mesh = new THREE.InstancedMesh(cubeGeo, mat, count);
    mesh.userData.id = id;
    mesh.userData.blockList = entry.blockList;

    for (let i = 0; i < count; i++) {
      mesh.setMatrixAt(i, entry.matrices[i]);
    }
    mesh.instanceMatrix.needsUpdate = true;

    // 水にはレイキャストさせない
    if (id === WATER) {
      mesh.raycast = () => {};
    }

    group.add(mesh);
  }

  chunkRoot.add(group);
  chunkGroups[key] = group;
}

function rebuildAround(wx, wz) {
  const cx = Math.floor(wx / CHUNK);
  const cz = Math.floor(wz / CHUNK);

  const targets = [
    [cx, cz],
    [cx + 1, cz],
    [cx - 1, cz],
    [cx, cz + 1],
    [cx, cz - 1]
  ];

  const seen = new Set();
  for (const [tx, tz] of targets) {
    if (tx < 0 || tx >= CX || tz < 0 || tz >= CZ) continue;
    const key = chunkKey(tx, tz);
    if (seen.has(key)) continue;
    seen.add(key);
    rebuildChunk(tx, tz);
  }
}

function rebuildAllChunks() {
  for (let cz = 0; cz < CZ; cz++) {
    for (let cx = 0; cx < CX; cx++) {
      rebuildChunk(cx, cz);
    }
  }
}

/* =========================================================
 * プレイヤー状態
 * ========================================================= */
const player = {
  pos: new THREE.Vector3(),
  vel: new THREE.Vector3(),
  yaw: 0,
  pitch: 0,
  onGround: false
};

function findSpawn() {
  const sx = Math.floor(WX / 2);
  const sz = Math.floor(WZ / 2);
  for (let y = WY - 2; y >= 0; y--) {
    const id = getBlock(sx, y, sz);
    if (id !== AIR && id !== WATER) {
      return { x: sx + 0.5, y: y + 1.01, z: sz + 0.5 };
    }
  }
  return { x: sx + 0.5, y: SEA + 2, z: sz + 0.5 };
}

function spawnPlayer() {
  const p = findSpawn();
  player.pos.set(p.x, p.y, p.z);
  player.vel.set(0, 0, 0);
  player.yaw = Math.PI * 0.25;
  player.pitch = -0.15;
  camera.position.set(player.pos.x, player.pos.y + EYE, player.pos.z);
}

/* =========================================================
 * 衝突判定
 * ========================================================= */
function playerCollides() {
  const r = PLAYER_RADIUS;
  const px = player.pos.x;
  const py = player.pos.y;
  const pz = player.pos.z;

  const minX = Math.floor(px - r);
  const maxX = Math.floor(px + r - 1e-7);
  const minY = Math.floor(py);
  const maxY = Math.floor(py + PLAYER_HEIGHT - 1e-7);
  const minZ = Math.floor(pz - r);
  const maxZ = Math.floor(pz + r - 1e-7);

  for (let x = minX; x <= maxX; x++) {
    for (let y = minY; y <= maxY; y++) {
      for (let z = minZ; z <= maxZ; z++) {
        if (isCollisionSolid(x, y, z)) return true;
      }
    }
  }
  return false;
}

function moveAxis(axis, amount) {
  if (Math.abs(amount) < 1e-10) return false;

  player.pos[axis] += amount;

  if (!playerCollides()) return false;

  const eps = 1e-6;

  if (axis === "x") {
    if (amount > 0) {
      const maxX = Math.floor(player.pos.x + PLAYER_RADIUS - 1e-7);
      player.pos.x = maxX - PLAYER_RADIUS - eps;
    } else {
      const minX = Math.floor(player.pos.x - PLAYER_RADIUS);
      player.pos.x = minX + 1 + PLAYER_RADIUS + eps;
    }
    player.vel.x = 0;
  } else if (axis === "z") {
    if (amount > 0) {
      const maxZ = Math.floor(player.pos.z + PLAYER_RADIUS - 1e-7);
      player.pos.z = maxZ - PLAYER_RADIUS - eps;
    } else {
      const minZ = Math.floor(player.pos.z - PLAYER_RADIUS);
      player.pos.z = minZ + 1 + PLAYER_RADIUS + eps;
    }
    player.vel.z = 0;
  } else if (axis === "y") {
    if (amount > 0) {
      const maxY = Math.floor(player.pos.y + PLAYER_HEIGHT - 1e-7);
      player.pos.y = maxY - PLAYER_HEIGHT - eps;
      player.vel.y = 0;
    } else {
      player.pos.y = Math.floor(player.pos.y) + 1 + eps;
      player.vel.y = 0;
      player.onGround = true;
    }
  }

  return true;
}

function blockOverlapsPlayer(bx, by, bz) {
  const id = getBlock(bx, by, bz);
  if (id === AIR || id === WATER) return false;

  const px = player.pos.x;
  const py = player.pos.y;
  const pz = player.pos.z;
  const r = PLAYER_RADIUS;

  return (
    px - r < bx + 1 &&
    px + r > bx &&
    py < by + 1 &&
    py + PLAYER_HEIGHT > by &&
    pz - r < bz + 1 &&
    pz + r > bz
  );
}

/* =========================================================
 * 入力
 * ========================================================= */
const keys = {};
let selected = GRASS;
let pointerLocked = false;

const overlay = document.getElementById("overlay");
const startBtn = document.getElementById("startBtn");

function updateHotbar() {
  const hotbar = document.getElementById("hotbar");
  hotbar.innerHTML = "";

  HOTBAR.forEach((id, i) => {
    const info = BLOCK_INFO[id];
    const slot = document.createElement("div");
    slot.className = "slot" + (id === selected ? " selected" : "");

    const key = document.createElement("div");
    key.className = "key";
    key.textContent = String(i + 1);

    const icon = document.createElement("div");
    icon.className = "icon";
    icon.style.background = info.color;

    slot.appendChild(key);
    slot.appendChild(icon);
    hotbar.appendChild(slot);
  });

  document.getElementById("blockName").textContent = BLOCK_INFO[selected]?.name || "";
}

function selectBlock(blockId) {
  if (HOTBAR.includes(blockId)) {
    selected = blockId;
    updateHotbar();
  }
}

function requestPointerLock() {
  renderer.domElement.requestPointerLock();
}

startBtn.addEventListener("click", requestPointerLock);

document.addEventListener("pointerlockchange", () => {
  pointerLocked = document.pointerLockElement === renderer.domElement;
  overlay.classList.toggle("hidden", pointerLocked);
});

document.addEventListener("mousemove", (e) => {
  if (!pointerLocked) return;

  player.yaw -= e.movementX * MOUSE_SENS;
  player.pitch -= e.movementY * MOUSE_SENS;
  player.pitch = clamp(player.pitch, -Math.PI / 2 + 0.01, Math.PI / 2 - 0.01);
});

document.addEventListener("keydown", (e) => {
  keys[e.code] = true;

  if (e.code === "Space") e.preventDefault();

  if (e.code.startsWith("Digit")) {
    const n = parseInt(e.code.slice(5), 10);
    if (n >= 1 && n <= 9) selectBlock(HOTBAR[n - 1]);
  }
});

document.addEventListener("keyup", (e) => {
  keys[e.code] = false;
});

document.addEventListener("contextmenu", (e) => {
  e.preventDefault();
});

document.addEventListener("wheel", (e) => {
  if (!pointerLocked) return;
  e.preventDefault();

  let idx = HOTBAR.indexOf(selected);
  idx = (idx + (e.deltaY > 0 ? 1 : -1) + HOTBAR.length) % HOTBAR.length;
  selectBlock(HOTBAR[idx]);
}, { passive: false });

const raycaster = new THREE.Raycaster();
const rayCenter = new THREE.Vector2(0, 0);

function getTarget() {
  raycaster.setFromCamera(rayCenter, camera);
  raycaster.far = REACH;

  const intersects = raycaster.intersectObjects(chunkRoot.children, true);
  if (intersects.length === 0) return null;

  const hit = intersects[0];
  const list = hit.object.userData.blockList;
  if (!list || hit.instanceId === undefined) return null;

  const block = list[hit.instanceId];
  return {
    block,
    faceNormal: hit.face ? hit.face.normal.clone() : new THREE.Vector3(0, 1, 0)
  };
}

function breakTarget(target) {
  if (!target) return;

  const [bx, by, bz] = target.block;
  const id = getBlock(bx, by, bz);
  if (id === AIR || id === WATER) return;
  if (by === 0) return; // 床岩っぽいものを守る

  setBlock(bx, by, bz, AIR);
  rebuildAround(bx, bz);
}

function placeTarget(target) {
  if (!target) return;

  const [bx, by, bz] = target.block;
  const n = target.faceNormal;

  const nx = bx + Math.round(n.x);
  const ny = by + Math.round(n.y);
  const nz = bz + Math.round(n.z);

  if (nx < 0 || nx >= WX || ny < 1 || ny >= WY || nz < 0 || nz >= WZ) return;

  const existing = getBlock(nx, ny, nz);
  if (existing !== AIR && existing !== WATER) return;

  if (selected !== WATER && blockOverlapsPlayer(nx, ny, nz)) return;

  setBlock(nx, ny, nz, selected);
  rebuildAround(nx, nz);
}

function pickTarget(target) {
  if (!target) return;
  const [bx, by, bz] = target.block;
  const id = getBlock(bx, by, bz);
  if (HOTBAR.includes(id)) selectBlock(id);
}

renderer.domElement.addEventListener("mousedown", (e) => {
  if (!pointerLocked) return;

  const target = getTarget();

  if (e.button === 0) {
    breakTarget(target);
  } else if (e.button === 2) {
    placeTarget(target);
  } else if (e.button === 1) {
    pickTarget(target);
  }
});

/* =========================================================
 * 画面リサイズ
 * ========================================================= */
window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

/* =========================================================
 * 起動処理
 * ========================================================= */
generateWorld();
rebuildAllChunks();
spawnPlayer();
updateHotbar();

/* =========================================================
 * ゲームループ
 * ========================================================= */
let last = performance.now();
let fpsTimer = 0;
let fpsCount = 0;
const fpsEl = document.getElementById("fps");
const coordsEl = document.getElementById("coords");

function update(dt) {
  // 視点
  camera.position.set(player.pos.x, player.pos.y + EYE, player.pos.z);
  camera.rotation.set(player.pitch, player.yaw, 0);

  // 入力方向
  const forward = new THREE.Vector3();
  camera.getWorldDirection(forward);
  forward.y = 0;
  forward.normalize();

  const right = new THREE.Vector3().crossVectors(forward, new THREE.Vector3(0, 1, 0)).normalize();

  const move = new THREE.Vector3();
  if (keys["KeyW"]) move.add(forward);
  if (keys["KeyS"]) move.sub(forward);
  if (keys["KeyD"]) move.add(right);
  if (keys["KeyA"]) move.sub(right);

  if (move.lengthSq() > 0) move.normalize();

  const speed = keys["ShiftLeft"] || keys["ShiftRight"] ? SPRINT_SPEED : SPEED;

  player.vel.x = move.x * speed;
  player.vel.z = move.z * speed;

  // ジャンプ
  if ((keys["Space"]) && player.onGround) {
    player.vel.y = JUMP;
    player.onGround = false;
  }

  // 重力
  player.vel.y -= GRAVITY * dt;
  player.vel.y = clamp(player.vel.y, -70, 50);

  player.onGround = false;

  // 軸ごとに衝突解決
  moveAxis("x", player.vel.x * dt);
  moveAxis("z", player.vel.z * dt);

  const beforeY = player.vel.y;
  moveAxis("y", player.vel.y * dt);

  // 落下中に接地判定を補強
  if (!player.onGround && beforeY < 0) {
    const checkY = player.pos.y - 0.03;
    const minY = Math.floor(checkY);
    const px = Math.floor(player.pos.x);
    const pz = Math.floor(player.pos.z);
    if (isCollisionSolid(px, minY, pz)) {
      player.onGround = true;
    }
  }

  // 画面外の非常用リセット
  if (player.pos.y < -20) spawnPlayer();
}

function animate() {
  requestAnimationFrame(animate);

  const now = performance.now();
  let dt = Math.min((now - last) / 1000, 0.05);
  last = now;

  if (pointerLocked) {
    update(dt);
  }

  fpsCount++;
  fpsTimer += dt;
  if (fpsTimer >= 0.5) {
    fpsEl.textContent = Math.round(fpsCount / fpsTimer);
    fpsCount = 0;
    fpsTimer = 0;
  }

  coordsEl.textContent =
    `${Math.floor(player.pos.x)}, ${Math.floor(player.pos.y)}, ${Math.floor(player.pos.z)}`;

  renderer.render(scene, camera);
}

animate();
</script>
</body>
</html>
```