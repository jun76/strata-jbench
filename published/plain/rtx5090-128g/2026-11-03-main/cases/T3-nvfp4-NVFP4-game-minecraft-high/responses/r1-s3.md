# マイクラ風3D箱庭ゲーム

下のHTMLをそのまま `index.html` として保存してブラウザで開くと動きます。  
WebGLのみの自己完結型で、外部ライブラリ不要です。

```html
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<title>マイクラ風3D箱庭</title>
<style>
  html, body {
    margin: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
    background: #000;
    font-family: system-ui, -apple-system, "Segoe UI", "Noto Sans JP", sans-serif;
  }

  #game {
    position: fixed;
    inset: 0;
    display: block;
    width: 100%;
    height: 100%;
    cursor: crosshair;
  }

  #ui {
    position: fixed;
    inset: 0;
    pointer-events: none;
    color: #fff;
    text-shadow: 0 2px 6px rgba(0,0,0,.65);
    user-select: none;
  }

  #cross {
    position: absolute;
    left: 50%;
    top: 50%;
    width: 18px;
    height: 18px;
    transform: translate(-50%, -50%);
    opacity: .85;
  }

  #cross::before,
  #cross::after {
    content: "";
    position: absolute;
    left: 50%;
    top: 50%;
    background: #fff;
    transform: translate(-50%, -50%);
  }

  #cross::before {
    width: 18px;
    height: 2px;
  }

  #cross::after {
    width: 2px;
    height: 18px;
  }

  #hotbar {
    position: absolute;
    left: 50%;
    bottom: 20px;
    transform: translateX(-50%);
    display: flex;
    gap: 6px;
    padding: 6px;
    background: rgba(0,0,0,.35);
    border-radius: 10px;
  }

  .slot {
    width: 42px;
    height: 42px;
    border-radius: 6px;
    border: 2px solid rgba(255,255,255,.45);
    position: relative;
    overflow: hidden;
  }

  .slot.active {
    border-color: #fff;
    box-shadow: 0 0 0 2px rgba(0,0,0,.45);
  }

  .slot span {
    position: absolute;
    left: 3px;
    top: 1px;
    font-size: 11px;
    color: rgba(255,255,255,.9);
  }

  #help {
    position: absolute;
    left: 14px;
    top: 14px;
    font-size: 13px;
    line-height: 1.6;
    background: rgba(0,0,0,.35);
    padding: 10px 12px;
    border-radius: 10px;
  }

  #msg {
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    font-size: 20px;
    background: rgba(0,0,0,.55);
    padding: 16px 24px;
    border-radius: 12px;
  }

  #msg.hidden {
    display: none;
  }

  #status {
    position: absolute;
    right: 14px;
    top: 14px;
    font-size: 12px;
    background: rgba(0,0,0,.35);
    padding: 8px 10px;
    border-radius: 8px;
    text-align: right;
  }
</style>
</head>
<body>
<canvas id="game"></canvas>

<div id="ui">
  <div id="cross"></div>
  <div id="hotbar"></div>

  <div id="help">
    <strong>操作</strong><br>
    WASD: 移動 / マウス: 視点<br>
    左クリック: 破壊<br>
    右クリック: 設置<br>
    スペース: ジャンプ<br>
    Shift: 下降<br>
    1〜7: ブロック選択<br>
    ホイール: 選択変更<br>
    F: 飛行切替<br>
    R: 初期スポーン<br>
    P: 世界再生成<br>
  </div>

  <div id="status"></div>

  <div id="msg">クリックしてスタート</div>
</div>

<script>
"use strict";

const canvas = document.getElementById("game");
const msg = document.getElementById("msg");
const hotbar = document.getElementById("hotbar");
const statusEl = document.getElementById("status");

const gl =
  canvas.getContext("webgl", { antialias: false, alpha: false }) ||
  canvas.getContext("experimental-webgl", { antialias: false, alpha: false });

if (!gl) {
  msg.textContent = "WebGLが利用できません。";
  throw new Error("No WebGL");
}

/*
  =========================================
  基本設定
  =========================================
*/

const W = 48;
const H = 32;
const D = 48;

const AIR = 0;

const world = new Uint8Array(W * H * D);
const heights = new Int16Array(W * D);

const BLOCKS = {
  1: {
    name: "草",
    colors: [
      [0.31, 0.62, 0.24], // top
      [0.48, 0.55, 0.24], // side
      [0.48, 0.36, 0.24], // bottom
    ],
  },
  2: {
    name: "土",
    colors: [
      [0.50, 0.35, 0.22],
      [0.47, 0.33, 0.21],
      [0.42, 0.30, 0.20],
    ],
  },
  3: {
    name: "石",
    colors: [
      [0.52, 0.52, 0.54],
      [0.47, 0.47, 0.50],
      [0.42, 0.42, 0.45],
    ],
  },
  4: {
    name: "木",
    colors: [
      [0.42, 0.30, 0.17],
      [0.36, 0.25, 0.15],
      [0.30, 0.20, 0.13],
    ],
  },
  5: {
    name: "葉",
    colors: [
      [0.25, 0.48, 0.21],
      [0.22, 0.42, 0.19],
      [0.18, 0.34, 0.16],
    ],
  },
  6: {
    name: "砂",
    colors: [
      [0.84, 0.79, 0.54],
      [0.79, 0.74, 0.51],
      [0.72, 0.67, 0.46],
    ],
  },
  7: {
    name: "レンガ",
    colors: [
      [0.62, 0.27, 0.23],
      [0.55, 0.24, 0.21],
      [0.45, 0.20, 0.18],
    ],
  },
};

const HOTBAR = [1, 2, 3, 4, 5, 6, 7];
let selected = 1;

const player = {
  pos: [W / 2 + 0.5, 16, D / 2 + 0.5],
  height: 1.8,
  width: 0.62,
  eye: 1.62,
  vy: 0,
  onGround: false,
  fly: false,
};

let yaw = 0;
let pitch = -0.22;
let keys = new Set();

/*
  =========================================
  シェーダー
  =========================================
*/

const vertexShaderSource = `
attribute vec3 aPos;
attribute vec3 aColor;
attribute float aShade;

uniform mat4 uProj;
uniform mat4 uView;

varying vec3 vColor;
varying float vShade;
varying float vDepth;

void main() {
  gl_Position = uProj * uView * vec4(aPos, 1.0);
  vColor = aColor;
  vShade = aShade;
  vDepth = gl_Position.w;
}
`;

const fragmentShaderSource = `
precision mediump float;

varying vec3 vColor;
varying float vShade;
varying float vDepth;

uniform vec3 uFogColor;

void main() {
  vec3 col = vColor * vShade;
  float fog = clamp((vDepth - 32.0) / 78.0, 0.0, 1.0);
  col = mix(col, uFogColor, fog * 0.88);
  gl_FragColor = vec4(col, 1.0);
}
`;

function compileShader(type, source) {
  const shader = gl.createShader(type);
  gl.shaderSource(shader, source);
  gl.compileShader(shader);
  if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
    console.error(gl.getShaderInfoLog(shader));
    gl.deleteShader(shader);
    throw new Error("shader compile error");
  }
  return shader;
}

function createProgram(vsSource, fsSource) {
  const vs = compileShader(gl.VERTEX_SHADER, vsSource);
  const fs = compileShader(gl.FRAGMENT_SHADER, fsSource);
  const prog = gl.createProgram();
  gl.attachShader(prog, vs);
  gl.attachShader(prog, fs);
  gl.linkProgram(prog);

  if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) {
    console.error(gl.getProgramInfoLog(prog));
    throw new Error("program link error");
  }
  return prog;
}

const program = createProgram(vertexShaderSource, fragmentShaderSource);

const aPos = gl.getAttribLocation(program, "aPos");
const aColor = gl.getAttribLocation(program, "aColor");
const aShade = gl.getAttribLocation(program, "aShade");

const uProj = gl.getUniformLocation(program, "uProj");
const uView = gl.getUniformLocation(program, "uView");
const uFogColor = gl.getUniformLocation(program, "uFogColor");

const meshBuffer = gl.createBuffer();
let vertexCount = 0;

/*
  =========================================
  行列
  =========================================
*/

function perspective(fovY, aspect, near, far) {
  const f = 1.0 / Math.tan(fovY / 2.0);
  const nf = 1.0 / (near - far);

  return new Float32Array([
    f / aspect, 0, 0, 0,
    0, f, 0, 0,
    0, 0, (far + near) * nf, -1,
    0, 0, 2 * far * near * nf, 0,
  ]);
}

function computeView(px, py, pz, yaw, pitch) {
  const cp = Math.cos(pitch);
  const sp = Math.sin(pitch);

  // カメラ前方ベクトル: yaw=0,pitch=0 で -Z を向く
  const fx = -Math.sin(yaw) * cp;
  const fy = sp;
  const fz = -Math.cos(yaw) * cp;

  // right = cross(forward, up)
  const rlen = Math.hypot(fx, fz) || 1;
  const rx = -fz / rlen;
  const ry = 0;
  const rz = fx /rlen;

  // up = cross(right, forward)
  const ux = ry * fz - rz * fy;
  const uy = rz * fx - rx * fz;
  const uz = rx * fy - ry * fx;

  // backward = -forward
  const bx = -fx;
  const by = -fy;
  const bz = -fz;

  return new Float32Array([
    rx, ry, rz, 0,
    ux, uy, uz, 0,
    bx, by, bz, 0,
    -(rx * px + ry * py + rz * pz),
    -(ux * px + uy * py + uz * pz),
    -(bx * px + by * py + bz * pz),
    1,
  ]);
}

/*
  =========================================
  ワールド操作
  =========================================
*/

function idx(x, y, z) {
  return (x * H + y) * D + z;
}

function getBlock(x, y, z) {
  if (x < 0 || y < 0 || z < 0 || x >= W || y >= H || z >= D) return 0;
  return world[idx(x, y, z)];
}

function setBlock(x, y, z, v) {
  if (x < 0 || y < 0 || z < 0 || x >= W || y >= H || z >= D) return false;
  world[idx(x, y, z)] = v;
  return true;
}

function isSolidForMesh(x, y, z) {
  if (y < 0 || x < 0 || z < 0 || x >= W || z >= D) return true;
  if (y >= H) return false;
  return world[idx(x, y, z)] !== AIR;
}

function isSolidForCollision(x, y, z) {
  if (y < 0 || x < 0 || z < 0 || x >= W || z >= D) return true;
  if (y >= H) return false;
  return world[idx(x, y, z)] !== AIR;
}

function isSolidForRaycast(x, y, z) {
  if (x < 0 || y < 0 || z < 0 || x >= W || y >= H || z >= D) return false;
  return world[idx(x, y, z)] !== AIR;
}

function hash2(x, z) {
  let n = Math.imul(x | 0, 374761393) ^ Math.imul(z | 0, 668265263);
  n = (n ^ (n >>> 13)) >>> 0;
  n = Math.imul(n, 1274126177);
  n = (n ^ (n >>> 16)) >>> 0;
  return n / 4294967296;
}

function hash3(x, y, z) {
  let n =
    Math.imul(x | 0, 374761393) ^
    Math.imul(y | 0, 668265263) ^
    Math.imul(z | 0, 1440662683);

  n = (n ^ (n >>> 13)) >>> 0;
  n = Math.imul(n, 1274126177);
  n = (n ^ (n >>> 16)) >>> 0;
  return n / 4294967296;
}

/*
  =========================================
  地形生成
  =========================================
*/

function generateWorld() {
  world.fill(0);
  heights.fill(0);

  for (let z = 0; z < D; z++) {
    for (let x = 0; x < W; x++) {
      let h =
        12 +
        6 * Math.sin(x * 0.18) +
        5 * Math.cos(z * 0.15) +
        4 * Math.sin((x + z) * 0.11) +
        3 * Math.sin((x - z) * 0.07);

      h += hash2(x, z) * 2.5;
      h = Math.floor(h);

      if (h < 3) h = 3;
      if (h > H - 10) h = H - 10;

      heights[x * D + z] = h;

      const topBlock = h < 11 ? 6 : 1;

      for (let y = 0; y <= h; y++) {
        let block;

        if (y === h) {
          block = topBlock;
        } else if (y >= h - 2) {
          block = 2; // dirt
        } else {
          block = 3; // stone
        }

        world[idx(x, y, z)] = block;
      }
    }
  }

  // 木
  for (let z = 3; z < D - 3; z++) {
    for (let x = 3; x < W - 3; x++) {
      const h = heights[x * D + z];
      if (getBlock(x, h, z) !== 1) continue;
      if (hash2(x * 17, z * 31) < 0.978) continue;

      const treeHeight = 4 + Math.floor(hash2(x, z + 123) * 3);

      for (let y = h + 1; y <= h + treeHeight; y++) {
        setBlock(x, y, z, 4);
      }

      const top = h + treeHeight;

      for (let ly = top - 1; ly <= top + 1; ly++) {
        const radius = ly === top + 1 ? 1 : 2;

        for (let dx = -radius; dx <= radius; dx++) {
          for (let dz = -radius; dz <= radius; dz++) {
            if (dx === 0 && dz === 0) continue;

            const d2 = dx * dx + dz * dz;
            if (d2 > radius * radius + 1) continue;

            if (getBlock(x + dx, ly, z + dz) === 0) {
              setBlock(x + dx, ly, z + dz, 5);
            }
          }
        }
      }

      if (getBlock(x, top + 1, z) === 0) {
        setBlock(x, top + 1, z, 5);
      }
    }
  }
}

/*
  =========================================
  メッシュ生成
  =========================================
*/

// colorIndex: 0=top, 1=side, 2=bottom
const FACES = [
  {
    n: [0, 1, 0],
    c: 0,
    s: 1.0,
    v: [
      0, 1, 1,
      1, 1, 1,
      1, 1, 0,
      0, 1, 0,
    ],
  },
  {
    n: [0, -1, 0],
    c: 2,
    s: 0.45,
    v: [
      0, 0, 0,
      1, 0, 0,
      1, 0, 1,
      0, 0, 1,
    ],
  },
  {
    n: [1, 0, 0],
    c: 1,
    s: 0.80,
    v: [
      1, 0, 0,
      1, 0, 1,
      1, 1, 1,
      1, 1, 0,
    ],
  },
  {
    n: [-1, 0, 0],
    c: 1,
    s: 0.80,
    v: [
      0, 0, 1,
      0, 0, 0,
      0, 1, 0,
      0, 1, 1,
    ],
  },
  {
    n: [0, 0, 1],
    c: 1,
    s: 0.65,
    v: [
      0, 0, 1,
      1, 0, 1,
      1, 1, 1,
      0, 1, 1,
    ],
  },
  {
    n: [0, 0, -1],
    c: 1,
    s: 0.65,
    v: [
      1, 0, 0,
      0, 0, 0,
      0, 1, 0,
      1, 1, 0,
    ],
  },
];

const TRI = [0, 1, 2, 0, 2, 3];

function buildMesh() {
  const verts = [];

  function addFace(face, x, y, z, color, shade) {
    const v = face.v;

    for (let i = 0; i < 6; i++) {
      const p = TRI[i] * 3;
      verts.push(
        x + v[p],
        y + v[p + 1],
        z + v[p + 2],

        color[0],
        color[1],
        color[2],

        shade
      );
    }
  }

  for (let y = 0; y < H; y++) {
    for (let z = 0; z < D; z++) {
      for (let x = 0; x < W; x++) {
        const b = world[idx(x, y, z)];
        if (!b) continue;

        const info = BLOCKS[b];
        if (!info) continue;

        const color = info.colors;

        for (const face of FACES) {
          const nx = x + face.n[0];
          const ny = y + face.n[1];
          const nz = z + face.n[2];

          if (!isSolidForMesh(nx, ny, nz)) {
            const variation = 0.94 + hash3(x, y, z) * 0.12;
            const shade = face.s * variation;

            addFace(
              face,
              x,
              y,
              z,
              color[face.c],
              shade
            );
          }
        }
      }
    }
  }

  gl.bindBuffer(gl.ARRAY_BUFFER, meshBuffer);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(verts), gl.DYNAMIC_DRAW);

  vertexCount = verts.length / 7;
}

/*
  =========================================
  レイキャスト
  =========================================
*/

function raycast(px, py, pz, fx, fy, fz, maxDist) {
  let x = Math.floor(px);
  let y = Math.floor(py);
  let z = Math.floor(pz);

  if (isSolidForRaycast(x, y, z)) {
    return {
      x, y, z,
      nx: 0, ny: 1, nz: 0,
      lx: x, ly: y + 1, lz: z,
    };
  }

  const stepX = fx > 0 ? 1 : -1;
  const stepY = fy > 0 ? 1 : -1;
  const stepZ = fz > 0 ? 1 : -1;

  const invX = Math.abs(fx) < 1e-10 ? Infinity : 1 / Math.abs(fx);
  const invY = Math.abs(fy) < 1e-10 ? Infinity : 1 / Math.abs(fy);
  const invZ = Math.abs(fz) < 1e-10 ? Infinity : 1 / Math.abs(fz);

  let tMaxX =
    invX === Infinity
      ? Infinity
      : (fx > 0 ? x + 1 - px : px - x) * invX;

  let tMaxY =
    invY === Infinity
      ? Infinity
      : (fy > 0 ? y + 1 - py : py - y) * invY;

  let tMaxZ =
    invZ === Infinity
      ? Infinity
      : (fz > 0 ? z + 1 - pz : pz - z) * invZ;

  for (let i = 0; i < 256; i++) {
    let axis;
    let t;

    if (tMaxX < tMaxY && tMaxX < tMaxZ) {
      axis = 0;
      t = tMaxX;
    } else if (tMaxY < tMaxZ) {
      axis = 1;
      t = tMaxY;
    } else {
      axis = 2;
      t = tMaxZ;
    }

    if (t > maxDist) break;

    let lx = x;
    let ly = y;
    let lz = z;

    let nx = 0;
    let ny = 0;
    let nz = 0;

    if (axis === 0) {
      x += stepX;
      tMaxX += invX;
      nx = -stepX;
    } else if (axis === 1) {
      y += stepY;
      tMaxY += invY;
      ny = -stepY;
    } else {
      z += stepZ;
      tMaxZ += invZ;
      nz = -stepZ;
    }

    if (isSolidForRaycast(x, y, z)) {
      return {
        x, y, z,
        nx, ny, nz,
        lx: x + nx,
        ly: y + ny,
        lz: z + nz,
      };
    }
  }

  return null;
}

/*
  =========================================
  当たり判定
  =========================================
*/

function collides() {
  const half = player.width / 2;
  const eps = 0.0001;

  const minX = Math.floor(player.pos[0] - half + eps);
  const maxX = Math.floor(player.pos[0] + half - eps);

  const minY = Math.floor(player.pos[1] + eps);
  const maxY = Math.floor(player.pos[1] + player.height - eps);

  const minZ = Math.floor(player.pos[2] - half + eps);
  const maxZ = Math.floor(player.pos[2] + half - eps);

  for (let x = minX; x <= maxX; x++) {
    for (let y = minY; y <= maxY; y++) {
      for (let z = minZ; z <= maxZ; z++) {
        if (isSolidForCollision(x, y, z)) return true;
      }
    }
  }

  return false;
}

function blockIntersectsPlayer(x, y, z) {
  const half = player.width / 2;
  const eps = 0.0001;

  const minX = x;
  const maxX = x + 1;

  const minY = y;
  const maxY = y + 1;

  const minZ = z;
  const maxZ = z + 1;

  const pxMin = player.pos[0] - half + eps;
  const pxMax = player.pos[0] + half - eps;

  const pyMin = player.pos[1] + eps;
  const pyMax = player.pos[1] + player.height - eps;

  const pzMin = player.pos[2] - half + eps;
  const pzMax = player.pos[2] + half - eps;

  return (
    maxX > pxMin &&
    minX < pxMax &&
    maxY > pyMin &&
    minY < pyMax &&
    maxZ > pzMin &&
    minZ < pzMax
  );
}

function applyMove(axis, amount) {
  const old = player.pos[axis];
  player.pos[axis] += amount;

  if (collides()) {
    player.pos[axis] = old;

    if (axis === 1) {
      if (amount < 0) {
        player.onGround = true;
      }
      player.vy = 0;
    }
  }
}

/*
  =========================================
  更新
  =========================================
*/

function getForward() {
  const cp = Math.cos(pitch);
  return [
    -Math.sin(yaw) * cp,
    Math.sin(pitch),
    -Math.cos(yaw) * cp,
  ];
}

function respawn() {
  const cx = W >> 1;
  const cz = D >> 1;

  let y = heights[cx * D + cz] + 2;

  while (y > 0 && getBlock(cx, y - 1, cz) === 0) y--;

  player.pos = [cx + 0.5, y + 0.01, cz + 0.5];
  player.vy = 0;
  player.onGround = false;
  player.fly = false;

  yaw = 0;
  pitch = -0.22;
}

function update(dt) {
  if (Number.isNaN(player.pos[1]) || player.pos[1] < -20) {
    respawn();
  }

  const speed = player.fly ? 9 : 5;

  const forwardX = -Math.sin(yaw);
  const forwardZ = -Math.cos(yaw);

  const rightX = Math.cos(yaw);
  const rightZ = -Math.sin(yaw);

  let mx = 0;
  let mz = 0;

  if (keys.has("KeyW")) {
    mx += forwardX;
    mz += forwardZ;
  }

  if (keys.has("KeyS")) {
    mx -= forwardX;
    mz -= forwardZ;
  }

  if (keys.has("KeyD")) {
    mx += rightX;
    mz += rightZ;
  }

  if (keys.has("KeyA")) {
    mx -= rightX;
    mz -= rightZ;
  }

  const len = Math.hypot(mx, mz);
  if (len > 0) {
    mx /= len;
    mz /= len;
  }

  const moveX = mx * speed * dt;
  const moveZ = mz * speed * dt;

  if (player.fly) {
    let vy = 0;

    if (keys.has("Space")) vy += speed * dt;
    if (keys.has("ShiftLeft") || keys.has("ShiftRight")) vy -= speed * dt;

    applyMove(0, moveX);
    applyMove(2, moveZ);
    applyMove(1, vy);
  } else {
    player.vy -= 28 * dt;
    if (player.vy < -32) player.vy = -32;

    if (keys.has("Space") && player.onGround) {
      player.vy = 8.6;
      player.onGround = false;
    }

    applyMove(0, moveX);
    applyMove(2, moveZ);

    player.onGround = false;
    applyMove(1, player.vy * dt);
  }
}

/*
  =========================================
  UI
  =========================================
*/

function rgb(c) {
  return `rgb(${Math.floor(c[0] * 255)},${Math.floor(c[1] * 255)},${Math.floor(c[2] * 255)})`;
}

function buildHotbar() {
  hotbar.innerHTML = "";

  HOTBAR.forEach((id, i) => {
    const div = document.createElement("div");
    div.className = "slot";
    div.style.background = rgb(BLOCKS[id].colors[0]);
    div.title = BLOCKS[id].name;

    const s = document.createElement("span");
    s.textContent = String(i + 1);
    div.appendChild(s);

    hotbar.appendChild(div);
  });

  updateSelected();
}

function updateSelected() {
  const slots = hotbar.querySelectorAll(".slot");
  slots.forEach((el, i) => {
    el.classList.toggle("active", HOTBAR[i] === selected);
  });
}

function updateStatus() {
  const f = getForward();
  const hit = raycast(
    player.pos[0],
    player.pos[1] + player.eye,
    player.pos[2],
    f[0],
    f[1],
    f[2],
    6
  );

  let target = "空中";
  if (hit) {
    const b = BLOCKS[getBlock(hit.x, hit.y, hit.z)];
    target = b ? b.name : "空気";
  }

  statusEl.innerHTML =
    `選択: ${BLOCKS[selected].name}<br>` +
    `見ているもの: ${target}<br>` +
    `mode: ${player.fly ? "飛行" : "通常"}<br>` +
    `X:${player.pos[0].toFixed(1)} Y:${player.pos[1].toFixed(1)} Z:${player.pos[2].toFixed(1)}`;
}

/*
  =========================================
  入力
  =========================================
*/

canvas.addEventListener("click", () => {
  if (document.pointerLockElement !== canvas) {
    canvas.requestPointerLock();
  }
});

document.addEventListener("pointerlockchange", () => {
  const locked = document.pointerLockElement === canvas;
  msg.classList.toggle("hidden", locked);
});

window.addEventListener("mousemove", (e) => {
  if (document.pointerLockElement !== canvas) return;

  const sens = 0.0024;
  yaw -= e.movementX * sens;
  pitch -= e.movementY * sens;

  pitch = Math.max(-1.55, Math.min(1.55, pitch));
});

canvas.addEventListener("contextmenu", (e) => {
  e.preventDefault();
});

canvas.addEventListener("mousedown", (e) => {
  if (document.pointerLockElement !== canvas) return;

  const f = getForward();
  const ex = player.pos[0];
  const ey = player.pos[1] + player.eye;
  const ez = player.pos[2];

  const hit = raycast(ex, ey, ez, f[0], f[1], f[2], 6);
  if (!hit) return;

  if (e.button === 0) {
    if (hit.y > 0) {
      setBlock(hit.x, hit.y, hit.z, 0);
      buildMesh();
    }
  } else if (e.button === 2) {
    const bx = hit.x + hit.nx;
    const by = hit.y + hit.ny;
    const bz = hit.z + hit.nz;

    if (
      bx >= 0 && by >= 0 && bz >= 0 &&
      bx < W && by < H && bz < D &&
      getBlock(bx, by, bz) === 0 &&
      BLOCKS[selected] &&
      !blockIntersectsPlayer(bx, by, bz)
    ) {
      setBlock(bx, by, bz, selected);
      buildMesh();
    }
  }
});

window.addEventListener("keydown", (e) => {
  if (e.code === "Space") e.preventDefault();

  keys.add(e.code);

  if (e.code >= "Digit1" && e.code <= "Digit7") {
    const i = Number(e.code.slice(-1)) - 1;
    if (HOTBAR[i] !== undefined) {
      selected = HOTBAR[i];
      updateSelected();
    }
  }

  if (e.code === "KeyF") {
    player.fly = !player.fly;
    player.vy = 0;
  }

  if (e.code === "KeyR") {
    respawn();
  }

  if (e.code === "KeyP") {
    generateWorld();
    respawn();
    buildMesh();
  }
});

window.addEventListener("keyup", (e) => {
  keys.delete(e.code);
});

window.addEventListener("wheel", (e) => {
  const dir = e.deltaY > 0 ? 1 : -1;
  const i = HOTBAR.indexOf(selected);
  selected = HOTBAR[(i + dir + HOTBAR.length) % HOTBAR.length];
  updateSelected();
});

/*
  =========================================
  描画
  =========================================
*/

let proj = perspective(Math.PI / 3, 1, 0.08, 220);

function resize() {
  const dpr = Math.min(window.devicePixelRatio || 1, 1.25);

  canvas.width = Math.floor(window.innerWidth * dpr);
  canvas.height = Math.floor(window.innerHeight * dpr);

  canvas.style.width = window.innerWidth + "px";
  canvas.style.height = window.innerHeight + "px";

  gl.viewport(0, 0, canvas.width, canvas.height);

  proj = perspective(
    Math.PI / 3,
    canvas.width / Math.max(1, canvas.height),
    0.08,
    220
  );
}

window.addEventListener("resize", resize);

function render() {
  gl.viewport(0, 0, canvas.width, canvas.height);

  gl.clearColor(0.55, 0.78, 0.95, 1);
  gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

  gl.enable(gl.DEPTH_TEST);

  if (vertexCount === 0) return;

  gl.useProgram(program);

  const ex = player.pos[0];
  const ey = player.pos[1] + player.eye;
  const ez = player.pos[2];

  const view = computeView(ex, ey, ez, yaw, pitch);

  gl.uniformMatrix4fv(uProj, false, proj);
  gl.uniformMatrix4fv(uView, false, view);
  gl.uniform3f(uFogColor, 0.55, 0.78, 0.95);

  gl.bindBuffer(gl.ARRAY_BUFFER, meshBuffer);

  const stride = 7 * 4;

  gl.enableVertexAttribArray(aPos);
  gl.vertexAttribPointer(aPos, 3, gl.FLOAT, false, stride, 0);

  gl.enableVertexAttribArray(aColor);
  gl.vertexAttribPointer(aColor, 3, gl.FLOAT, false, stride, 3 * 4);

  gl.enableVertexAttribArray(aShade);
  gl.vertexAttribPointer(aShade, 1, gl.FLOAT, false, stride, 6 * 4);

  gl.drawArrays(gl.TRIANGLES, 0, vertexCount);
}

/*
  =========================================
  初期化・ループ
  =========================================
*/

function start() {
  resize();
  generateWorld();
  respawn();
  buildHotbar();
  buildMesh();

  let last = performance.now();

  function frame(now) {
    const dt = Math.min(0.045, (now - last) / 1000);
    last = now;

    update(dt);
    render();
    updateStatus();

    requestAnimationFrame(frame);
  }

  requestAnimationFrame(frame);
}

start();
</script>
</body>
</html>
```

## できること

- 3Dブロック視点での一人称操作
- WASD移動、マウス視点操作
- 左クリックでブロック破壊
- 右クリックでブロック設置
- 草 / 土 / 石 / 木 / 葉 / 砂 / レンガを選択可能
- 自動地形生成と木生成
- Fキーで飛行モード
- Pキーで世界再生成

まずはこちらのバージョンで遊べる状態にしています。  
次は「チャンク分割」「洞窟」「水」「クラフト」「Mob」などへ拡張できます。