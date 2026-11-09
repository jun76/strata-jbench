以下は **単一 HTML で動く「マイクラ風 3D 箱庭ゲーム」** です。  
コピーして `.html` として保存し、ブラウザで開けば遊べます。

- 移動: WASD / Space / Shift
- 視点: マウス（クリックで操作開始）
- ブロック破壊: 左クリック
- ブロック設置: 右クリック
- ブロック選択: 1〜8 / ホイール / ホットバークリック
- 飛行: F
- 自動で地形・木を生成します

```html
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>マイクラ風 3D 箱庭</title>
<style>
  html, body {
    margin: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
    background: #87ceeb;
    font-family: system-ui, sans-serif;
  }
  canvas {
    display: block;
    width: 100%;
    height: 100%;
  }
  #hud {
    position: absolute;
    inset: 0;
    pointer-events: none;
    color: white;
    text-shadow: 0 1px 2px rgba(0,0,0,.8);
    user-select: none;
  }
  #crosshair {
    position: absolute;
    left: 50%;
    top: 50%;
    width: 22px;
    height: 22px;
    transform: translate(-50%, -50%);
  }
  #crosshair::before,
  #crosshair::after {
    content: "";
    position: absolute;
    background: rgba(255,255,255,.9);
  }
  #crosshair::before {
    left: 10px;
    top: 0;
    width: 2px;
    height: 22px;
  }
  #crosshair::after {
    left: 0;
    top: 10px;
    width: 22px;
    height: 2px;
  }
  #hotbar {
    position: absolute;
    left: 50%;
    bottom: 18px;
    transform: translateX(-50%);
    display: flex;
    gap: 6px;
    pointer-events: auto;
  }
  .slot {
    width: 48px;
    height: 48px;
    border: 2px solid #666;
    background: rgba(0,0,0,.45);
    display: flex;
    align-items: flex-end;
    justify-content: flex-start;
    color: white;
    font-size: 11px;
    cursor: pointer;
    position: relative;
    border-radius: 6px;
    overflow: hidden;
  }
  .slot.selected {
    border-color: white;
    box-shadow: 0 0 0 2px rgba(255,255,255,.35);
  }
  .slot .num {
    position: absolute;
    left: 4px;
    top: 3px;
    font-size: 10px;
    opacity: .9;
  }
  .slot .swatch {
    position: absolute;
    inset: 4px 4px 12px 4px;
    border-radius: 4px;
    box-shadow: inset 0 -6px 0 rgba(0,0,0,.18);
  }
  .slot .name {
    position: absolute;
    left: 0;
    right: 0;
    bottom: 1px;
    text-align: center;
    font-size: 9px;
    background: rgba(0,0,0,.35);
  }
  #info {
    position: absolute;
    top: 10px;
    left: 10px;
    background: rgba(0,0,0,.45);
    padding: 10px 12px;
    border-radius: 10px;
    font-size: 12px;
    line-height: 1.55;
    max-width: 380px;
  }
  #stats {
    position: absolute;
    top: 10px;
    right: 10px;
    background: rgba(0,0,0,.40);
    padding: 8px 10px;
    border-radius: 10px;
    font-size: 12px;
    min-width: 170px;
  }
  #hint {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: rgba(0,0,0,.55);
    padding: 16px 24px;
    border-radius: 12px;
    font-size: 16px;
    text-align: center;
  }
</style>
</head>
<body>
<canvas id="c"></canvas>

<div id="hud">
  <div id="info">
    <b>マイクラ風 3D 箱庭</b><br>
    クリックで視点操作 / WASD 移動 / Space ジャンプ<br>
    左クリック: 破壊 / 右クリック: 設置 / 1〜8: ブロック選択<br>
    Shift: ダッシュ / F: 飛行モード<br>
    <span id="selName"></span>
  </div>
  <div id="stats">
    FPS: <span id="fps">--</span><br>
    X: <span id="px">--</span><br>
    Y: <span id="py">--</span><br>
    Z: <span id="pz">--</span><br>
    Mode: <span id="mode">Walking</span>
  </div>
  <div id="crosshair"></div>
  <div id="hotbar"></div>
  <div id="hint">クリックして開始</div>
</div>

<script>
(() => {
  const canvas = document.getElementById('c');
  const gl = canvas.getContext('webgl', { antialias: false });
  if (!gl) {
    alert('WebGL が使えないブラウザです。');
    return;
  }

  // --- Basic WebGL state ---
  gl.enable(gl.DEPTH_TEST);
  gl.disable(gl.CULL_FACE);
  gl.clearColor(0.47, 0.74, 0.88, 1);

  // --- World constants ---
  const W = 48;
  const H = 26;
  const D = 48;
  const BLOCK_SIZE = 1;

  const AIR = 0;
  const GRASS = 1;
  const DIRT = 2;
  const STONE = 3;
  const SAND = 4;
  const WOOD = 5;
  const LEAVES = 6;
  const PLANKS = 7;
  const COBBLE = 8;

  const HOTBAR = [GRASS, DIRT, STONE, SAND, WOOD, LEAVES, PLANKS, COBBLE];
  const BLOCK_NAMES = [
    '', 'Grass', 'Dirt', 'Stone', 'Sand',
    'Wood', 'Leaves', 'Planks', 'Cobble'
  ];
  const BLOCK_COLORS = [
    '', '#6aa83a', '#8b5a2b', '#8b8b8b', '#d7c478',
    '#8b6b43', '#338f2b', '#b2894e', '#787878'
  ];

  const TILE = {
    GRASS_TOP: 0,
    GRASS_SIDE: 1,
    DIRT: 2,
    STONE: 3,
    SAND: 4,
    LOG_TOP: 5,
    LOG_SIDE: 6,
    LEAVES: 7,
    PLANKS: 8,
    COBBLE: 9
  };

  const BLOCK_TILE = [
    null,
    { top: TILE.GRASS_TOP, side: TILE.GRASS_SIDE, bottom: TILE.DIRT },
    { top: TILE.DIRT, side: TILE.DIRT, bottom: TILE.DIRT },
    { top: TILE.STONE, side: TILE.STONE, bottom: TILE.STONE },
    { top: TILE.SAND, side: TILE.SAND, bottom: TILE.SAND },
    { top: TILE.LOG_TOP, side: TILE.LOG_SIDE, bottom: TILE.LOG_TOP },
    { top: TILE.LEAVES, side: TILE.LEAVES, bottom: TILE.LEAVES },
    { top: TILE.PLANKS, side: TILE.PLANKS, bottom: TILE.PLANKS },
    { top: TILE.COBBLE, side: TILE.COBBLE, bottom: TILE.COBBLE }
  ];

  // --- Shader ---
  const vs = `
    attribute vec3 aPos;
    attribute vec3 aNormal;
    attribute vec2 aUV;
    attribute float aTile;

    uniform mat4 uProj;
    uniform mat4 uView;

    varying vec2 vUV;
    varying vec3 vNormal;
    varying float vTile;
    varying float vDist;

    void main() {
      vec4 viewPos = uView * vec4(aPos, 1.0);
      vDist = length(viewPos.xyz);
      gl_Position = uProj * viewPos;
      vUV = aUV;
      vNormal = aNormal;
      vTile = aTile;
    }
  `;

  const fs = `
    precision mediump float;

    uniform sampler2D uAtlas;
    uniform vec3 uSky;
    uniform float uFogNear;
    uniform float uFogFar;

    varying vec2 vUV;
    varying vec3 vNormal;
    varying float vTile;
    varying float vDist;

    void main() {
      vec2 tile = vec2(mod(vTile, 4.0), floor(vTile / 4.0)) * 0.25 + vUV * 0.25;
      vec4 tex = texture2D(uAtlas, tile);

      vec3 n = normalize(vNormal);
      vec3 lightDir = normalize(vec3(0.25, 1.0, 0.35));
      float light = 0.66 + 0.42 * max(dot(n, lightDir), 0.0);

      vec3 lit = tex.rgb * light;
      float fog = clamp((vDist - uFogNear) / (uFogFar - uFogNear), 0.0, 1.0);
      gl_FragColor = vec4(mix(lit, uSky, fog), 1.0);
    }
  `;

  function compileShader(type, src) {
    const s = gl.createShader(type);
    gl.shaderSource(s, src);
    gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {
      throw new Error(gl.getShaderInfoLog(s));
    }
    return s;
  }

  const program = gl.createProgram();
  gl.attachShader(program, compileShader(gl.VERTEX_SHADER, vs));
  gl.attachShader(program, compileShader(gl.FRAGMENT_SHADER, fs));
  gl.linkProgram(program);
  if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
    throw new Error(gl.getProgramInfoLog(program));
  }
  gl.useProgram(program);

  const aPos = gl.getAttribLocation(program, 'aPos');
  const aNormal = gl.getAttribLocation(program, 'aNormal');
  const aUV = gl.getAttribLocation(program, 'aUV');
  const aTile = gl.getAttribLocation(program, 'aTile');

  const uProj = gl.getUniformLocation(program, 'uProj');
  const uView = gl.getUniformLocation(program, 'uView');
  const uAtlas = gl.getUniformLocation(program, 'uAtlas');
  const uSky = gl.getUniformLocation(program, 'uSky');
  const uFogNear = gl.getUniformLocation(program, 'uFogNear');
  const uFogFar = gl.getUniformLocation(program, 'uFogFar');

  const posBuf = gl.createBuffer();
  const normBuf = gl.createBuffer();
  const uvBuf = gl.createBuffer();
  const tileBuf = gl.createBuffer();

  gl.enableVertexAttribArray(aPos);
  gl.enableVertexAttribArray(aNormal);
  gl.enableVertexAttribArray(aUV);
  gl.enableVertexAttribArray(aTile);

  function bindBuffers() {
    gl.bindBuffer(gl.ARRAY_BUFFER, posBuf);
    gl.vertexAttribPointer(aPos, 3, gl.FLOAT, false, 0, 0);

    gl.bindBuffer(gl.ARRAY_BUFFER, normBuf);
    gl.vertexAttribPointer(aNormal, 3, gl.FLOAT, false, 0, 0);

    gl.bindBuffer(gl.ARRAY_BUFFER, uvBuf);
    gl.vertexAttribPointer(aUV, 2, gl.FLOAT, false, 0, 0);

    gl.bindBuffer(gl.ARRAY_BUFFER, tileBuf);
    gl.vertexAttribPointer(aTile, 1, gl.FLOAT, false, 0, 0);
  }

  // --- Procedural texture atlas 4x4, each tile 16px, atlas 64x64 ---
  function makeAtlasTexture() {
    const cv = document.createElement('canvas');
    cv.width = 64;
    cv.height = 64;
    const ctx = cv.getContext('2d');

    function rnd(a, b, c) {
      let h = (a * 73856093 ^ b * 19349663 ^ c * 83492791) >>> 0;
      h = (h ^ (h >> 13)) * 1274126177 >>> 0;
      h ^= h >> 16;
      return h / 4294967295;
    }

    function tileStart(i) {
      return { x: (i % 4) * 16, y: Math.floor(i / 4) * 16 };
    }

    function drawTile(i, fn) {
      const s = tileStart(i);
      for (let y = 0; y < 16; y++) {
        for (let x = 0; x < 16; x++) {
          const c = fn(x, y, rnd(i + 17, x, y));
          ctx.fillStyle = `rgb(${Math.max(0, Math.min(255, c[0] | 0))},${Math.max(0, Math.min(255, c[1] | 0))},${Math.max(0, Math.min(255, c[2] | 0))})`;
          ctx.fillRect(s.x + x, s.y + y, 1, 1);
        }
      }
    }

    // Grass top
    drawTile(TILE.GRASS_TOP, (x, y, r) => {
      const g = 122 + Math.floor(r * 48);
      return [86 + Math.floor(r * 30), g, 68 + Math.floor(r * 22)];
    });

    // Grass side
    drawTile(TILE.GRASS_SIDE, (x, y, r) => {
      if (y < 5) {
        const g = 126 + Math.floor(r * 40);
        return [88 + Math.floor(r * 26), g, 70 + Math.floor(r * 22)];
      }
      if (y === 5 && r < 0.55) {
        const g = 112 + Math.floor(r * 32);
        return [92 + Math.floor(r * 22), g, 64 + Math.floor(r * 18)];
      }
      const d = 108 + Math.floor(r * 38);
      return [d, Math.floor(d * 0.70), Math.floor(d * 0.45)];
    });

    // Dirt
    drawTile(TILE.DIRT, (x, y, r) => {
      const d = 112 + Math.floor(r * 38);
      return [d, Math.floor(d * 0.70), Math.floor(d * 0.45)];
    });

    // Stone
    drawTile(TILE.STONE, (x, y, r) => {
      let v = 124 + Math.floor(r * 26);
      if (r < 0.13) v -= 28;
      if (r > 0.82) v += 18;
      return [v, v, Math.min(255, v + 6)];
    });

    // Sand
    drawTile(TILE.SAND, (x, y, r) => {
      const v = 218 + Math.floor(r * 20);
      return [v, Math.floor(v * 0.92), Math.floor(v * 0.66)];
    });

    // Log top
    drawTile(TILE.LOG_TOP, (x, y, r) => {
      const dx = x - 7.5;
      const dy = y - 7.5;
      const dist = Math.sqrt(dx * dx + dy * dy);
      const ring = Math.floor(dist * 1.3) % 3;
      let c = ring === 0 ? [172, 136, 82] : [138, 104, 66];
      if (dist < 2) c = [186, 150, 96];
      c[0] += Math.floor(r * 18 - 9);
      c[1] += Math.floor(r * 18 - 9);
      c[2] += Math.floor(r * 18 - 9);
      return c;
    });

    // Log side
    drawTile(TILE.LOG_SIDE, (x, y, r) => {
      let base = [132, 100, 64];
      if ((x + Math.floor(y * 0.35)) % 4 === 0) base = [104, 78, 50];
      if (r < 0.12) base = [154, 118, 80];
      base[0] += Math.floor(r * 18 - 9);
      base[1] += Math.floor(r * 18 - 9);
      base[2] += Math.floor(r * 18 - 9);
      return base;
    });

    // Leaves
    drawTile(TILE.LEAVES, (x, y, r) => {
      let c = [70 + Math.floor(r * 40), 132 + Math.floor(r * 40), 52 + Math.floor(r * 26)];
      if (r < 0.18) {
        c[0] -= 28;
        c[1] -= 32;
        c[2] -= 20;
      }
      return c;
    });

    // Planks
    drawTile(TILE.PLANKS, (x, y, r) => {
      let c = [174 + Math.floor(r * 22), 136 + Math.floor(r * 18), 82 + Math.floor(r * 18)];
      if (y % 4 === 0) {
        c[0] -= 38;
        c[1] -= 34;
        c[2] -= 26;
      }
      if (x === 0 || x === 15) {
        c[0] -= 22;
        c[1] -= 18;
        c[2] -= 12;
      }
      return c;
    });

    // Cobble
    drawTile(TILE.COBBLE, (x, y, r) => {
      let v = 134 + Math.floor(r * 34);
      if (r < 0.22) v -= 38;
      if (r > 0.78) v += 22;
      return [v, Math.max(0, v - 4), Math.max(0, v - 2)];
    });

    const tex = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, tex);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, cv);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.uniform1i(uAtlas, 0);
    return tex;
  }

  const sky = [0.47, 0.74, 0.88];
  gl.uniform3fv(uSky, sky);
  gl.uniform1f(uFogNear, 26);
  gl.uniform1f(uFogFar, 58);
  makeAtlasTexture();

  // --- World data ---
  const voxels = new Uint8Array(W * D * H);
  const heightMap = new Uint8Array(W * D);

  function idx(x, y, z) {
    return (z * W + x) * H + y;
  }

  function getBlock(x, y, z) {
    if (x < 0 || x >= W || y < 0 || y >= H || z < 0 || z >= D) return AIR;
    return voxels[idx(x, y, z)];
  }

  function setBlock(x, y, z, id) {
    if (x < 0 || x >= W || y < 0 || y >= H || z < 0 || z >= D) return;
    voxels[idx(x, y, z)] = id;
    dirtyMesh = true;
  }

  function isSolid(x, y, z) {
    return getBlock(x, y, z) !== AIR;
  }

  // --- Terrain generation ---
  const SEED = 1337;
  function hash2(x, y) {
    let n = (x * 374761393 + y * 668265263 + SEED) | 0;
    n = ((n ^ (n >> 13)) * 1274126177) | 0;
    n = (n ^ (n >> 16)) >>> 0;
    return n / 4294967295;
  }

  function smooth(t) {
    return t * t * (3 - 2 * t);
  }

  function lerp(a, b, t) {
    return a + (b - a) * t;
  }

  function noise2(x, y) {
    const x0 = Math.floor(x);
    const y0 = Math.floor(y);
    const fx = x - x0;
    const fy = y - y0;

    const a = hash2(x0, y0);
    const b = hash2(x0 + 1, y0);
    const c = hash2(x0, y0 + 1);
    const d = hash2(x0 + 1, y0 + 1);

    const u = smooth(fx);
    const v = smooth(fy);
    return lerp(lerp(a, b, u), lerp(c, d, u), v);
  }

  function fbm(x, y) {
    let v = 0;
    let amp = 1;
    let scale = 1;
    let norm = 0;
    for (let i = 0; i < 4; i++) {
      v += amp * noise2(x * scale, y * scale);
      norm += amp;
      amp *= 0.5;
      scale *= 2;
    }
    return v / norm;
  }

  function generateWorld() {
    for (let z = 0; z < D; z++) {
      for (let x = 0; x < W; x++) {
        const n = fbm(x * 0.04 + 0.5, z * 0.04 + 0.5);
        let h = Math.floor(6 + 9 * n);
        h = Math.max(1, Math.min(H - 8, h));

        const topId = h < 4 ? SAND : GRASS;
        heightMap[z * W + x] = h;

        for (let y = 0; y <= h; y++) {
          let id;
          if (y === h) {
            id = topId;
          } else if (y >= h - 2) {
            id = topId === SAND ? SAND : DIRT;
          } else {
            id = STONE;
          }
          voxels[idx(x, y, z)] = id;
        }
      }
    }

    // Trees
    for (let z = 2; z < D - 2; z++) {
      for (let x = 2; x < W - 2; x++) {
        const h = heightMap[z * W + x];
        const top = getBlock(x, h, z);
        if (top !== GRASS) continue;
        const treeRand = hash2(x * 91 + 17, z * 61 + 7);
        if (treeRand > 0.945 && h + 5 < H - 4) {
          const trunkH = 3 + Math.floor(treeRand * 100) % 2;
          const trunkTop = h + trunkH;

          for (let y = h + 1; y <= trunkTop; y++) {
            setBlock(x, y, z, WOOD);
          }

          const leafY = trunkTop;
          for (let dy = -1; dy <= 1; dy++) {
            const y = leafY + dy;
            if (y < 0 || y >= H) continue;
            const radius = dy === 1 ? 1 : 2;

            for (let dx = -radius; dx <= radius; dx++) {
              for (let dz = -radius; dz <= radius; dz++) {
                if (dx === 0 && dz === 0 && dy <= 0 && y <= leafY) continue;
                if (Math.abs(dx) === radius && Math.abs(dz) === radius && dy !== 1) continue;
                const bx = x + dx;
                const bz = z + dz;
                if (getBlock(bx, y, bz) === AIR) {
                  setBlock(bx, y, bz, LEAVES);
                }
              }
            }
          }
        }
      }
    }
  }

  generateWorld();

  // --- Mesh generation ---
  let dirtyMesh = true;
  let vertexCount = 0;

  const FACE_VERTS = [
    // +X
    [[1,0,0],[1,1,0],[1,1,1],[1,0,1], [1,0,0], [0,0],[0,1],[1,1],[1,0]],
    // -X
    [[0,1,0],[0,0,0],[0,0,1],[0,1,1], [-1,0,0], [0,0],[0,1],[1,1],[1,0]],
    // +Y
    [[0,1,1],[1,1,1],[1,1,0],[0,1,0], [0,1,0], [0,0],[1,0],[1,1],[0,1]],
    // -Y
    [[0,0,0],[1,0,0],[1,0,1],[0,0,1], [0,-1,0], [0,0],[1,0],[1,1],[0,1]],
    // +Z
    [[1,0,1],[1,1,1],[0,1,1],[0,0,1], [0,0,1], [0,0],[0,1],[1,1],[1,0]],
    // -Z
    [[0,0,0],[0,1,0],[1,1,0],[1,0,0], [0,0,-1], [0,0],[0,1],[1,1],[1,0]]
  ];

  function pushQuad(posArr, normArr, uvArr, tileArr, x, y, z, faceIndex, tileId) {
    const f = FACE_VERTS[faceIndex];
    const nv = f[0], nn = f[4], uv = f[5];
    const tri = [0, 1, 2, 0, 2, 3];

    for (let t = 0; t < 6; t++) {
      const k = tri[t];
      const vx = x + nv[k][0];
      const vy = y + nv[k][1];
      const vz = z + nv[k][2];

      posArr.push(vx, vy, vz);
      normArr.push(nn[0], nn[1], nn[2]);
      uvArr.push(uv[k][0], uv[k][1]);
      tileArr.push(tileId);
    }
  }

  function tileForFace(id, normal) {
    const t = BLOCK_TILE[id];
    if (!t) return 0;
    if (normal[1] === 1) return t.top;
    if (normal[1] === -1) return t.bottom;
    return t.side;
  }

  function rebuildMesh() {
    const posArr = [];
    const normArr = [];
    const uvArr = [];
    const tileArr = [];

    for (let y = 0; y < H; y++) {
      for (let z = 0; z < D; z++) {
        for (let x = 0; x < W; x++) {
          const id = getBlock(x, y, z);
          if (id === AIR) continue;

          for (let f = 0; f < 6; f++) {
            const n = FACE_VERTS[f][4];
            const nx = x + n[0];
            const ny = y + n[1];
            const nz = z + n[2];

            if (getBlock(nx, ny, nz) !== AIR) continue;

            pushQuad(
              posArr,
              normArr,
              uvArr,
              tileArr,
              x, y, z, f, tileForFace(id, n)
            );
          }
        }
      }
    }

    vertexCount = posArr.length / 3;

    gl.bindBuffer(gl.ARRAY_BUFFER, posBuf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(posArr), gl.DYNAMIC_DRAW);

    gl.bindBuffer(gl.ARRAY_BUFFER, normBuf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(normArr), gl.DYNAMIC_DRAW);

    gl.bindBuffer(gl.ARRAY_BUFFER, uvBuf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(uvArr), gl.DYNAMIC_DRAW);

    gl.bindBuffer(gl.ARRAY_BUFFER, tileBuf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(tileArr), gl.DYNAMIC_DRAW);

    dirtyMesh = false;
  }

  // --- Camera / player ---
  const player = {
    x: W / 2 + 0.5,
    y: heightMap[Math.floor(D / 2) * W + Math.floor(W / 2)] + 1.01,
    z: D / 2 + 0.5,
    yaw: 0,
    pitch: -0.35,
    vy: 0,
    fly: false,
    onGround: false
  };

  const WIDTH = 0.6;
  const HEIGHT = 1.8;
  const EYE = 1.62;
  const EPS = 0.001;
  const GRAVITY = 22;
  const JUMP_V = 8.2;

  function collides(px, py, pz) {
    const minX = Math.floor(px - WIDTH / 2 + EPS);
    const maxX = Math.floor(px + WIDTH / 2 - EPS);
    const minY = Math.floor(py + EPS);
    const maxY = Math.floor(py + HEIGHT - EPS);
    const minZ = Math.floor(pz - WIDTH / 2 + EPS);
    const maxZ = Math.floor(pz + WIDTH / 2 - EPS);

    for (let y = minY; y <= maxY; y++) {
      for (let z = minZ; z <= maxZ; z++) {
        for (let x = minX; x <= maxX; x++) {
          if (isSolid(x, y, z)) return true;
        }
      }
    }
    return false;
  }

  function tryMove(dx, dy, dz) {
    // X
    player.x += dx;
    if (collides(player.x, player.y, player.z)) {
      if (dx > 0) {
        const edge = Math.floor(player.x + WIDTH / 2 - EPS);
        player.x = edge - WIDTH / 2 - EPS;
      } else if (dx < 0) {
        const edge = Math.floor(player.x - WIDTH / 2 + EPS);
        player.x = edge + 1 + WIDTH / 2 + EPS;
      }
      if (collides(player.x, player.y, player.z)) player.x -= dx;
    }

    // Y
    player.y += dy;
    if (collides(player.x, player.y, player.z)) {
      if (dy > 0) {
        const top = Math.floor(player.y + HEIGHT - EPS);
        player.y = top - HEIGHT - EPS;
        player.vy = 0;
      } else if (dy < 0) {
        const bottom = Math.floor(player.y + EPS);
        player.y = bottom + 1 + EPS;
        player.vy = 0;
        player.onGround = true;
      } else {
        player.y -= dy;
      }
      if (collides(player.x, player.y, player.z)) player.y -= dy;
    }

    // Z
    player.z += dz;
    if (collides(player.x, player.y, player.z)) {
      if (dz > 0) {
        const edge = Math.floor(player.z + WIDTH / 2 - EPS);
        player.z = edge - WIDTH / 2 - EPS;
      } else if (dz < 0) {
        const edge = Math.floor(player.z - WIDTH / 2 + EPS);
        player.z = edge + 1 + WIDTH / 2 + EPS;
      }
      if (collides(player.x, player.y, player.z)) player.z -= dz;
    }
  }

  function getForward() {
    const cp = Math.cos(player.pitch);
    return [
      Math.sin(player.yaw) * cp,
      Math.sin(player.pitch),
      -Math.cos(player.yaw) * cp
    ];
  }

  function normalize3(v) {
    const len = Math.hypot(v[0], v[1], v[2]);
    if (len === 0) return [0, 0, 0];
    return [v[0] / len, v[1] / len, v[2] / len];
  }

  // --- Matrices ---
  function perspective(fovy, aspect, near, far) {
    const f = 1 / Math.tan(fovy / 2);
    const nf = 1 / (near - far);
    return new Float32Array([
      f / aspect, 0, 0, 0,
      0, f, 0, 0,
      0, 0, (far + near) * nf, -1,
      0, 0, 2 * far * near * nf, 0
    ]);
  }

  function lookAt(eye, target, up) {
    const z = normalize3([
      eye[0] - target[0],
      eye[1] - target[1],
      eye[2] - target[2]
    ]);
    let x = normalize3([
      up[1] * z[2] - up[2] * z[1],
      up[2] * z[0] - up[0] * z[2],
      up[0] * z[1] - up[1] * z[0]
    ]);
    const y = [
      z[1] * x[2] - z[2] * x[1],
      z[2] * x[0] - z[0] * x[2],
      z[0] * x[1] - z[1] * x[0]
    ];

    return new Float32Array([
      x[0], y[0], z[0], 0,
      x[1], y[1], z[1], 0,
      x[2], y[2], z[2], 0,
      -(x[0] * eye[0] + x[1] * eye[1] + x[2] * eye[2]),
      -(y[0] * eye[0] + y[1] * eye[1] + y[2] * eye[2]),
      -(z[0] * eye[0] + z[1] * eye[1] + z[2] * eye[2]),
      1
    ]);
  }

  // --- Raycast block picking ---
  function raycast(maxDist = 6) {
    const dir = normalize3(getForward());
    const ox = player.x;
    const oy = player.y + EYE;
    const oz = player.z;

    let x = Math.floor(ox);
    let y = Math.floor(oy);
    let z = Math.floor(oz);

    if (isSolid(x, y, z)) {
      return { x, y, z, face: [0, 0, -1] };
    }

    const stepX = dir.x > 0 ? 1 : -1;
    const stepY = dir.y > 0 ? 1 : -1;
    const stepZ = dir.z > 0 ? 1 : -1;

    const tDeltaX = dir.x !== 0 ? Math.abs(1 / dir.x) : Infinity;
    const tDeltaY = dir.y !== 0 ? Math.abs(1 / dir.y) : Infinity;
    const tDeltaZ = dir.z !== 0 ? Math.abs(1 / dir.z) : Infinity;

    let tMaxX = dir.x !== 0 ? ((stepX > 0 ? (x + 1 - ox) : (ox - x)) * tDeltaX) : Infinity;
    let tMaxY = dir.y !== 0 ? ((stepY > 0 ? (y + 1 - oy) : (oy - y)) * tDeltaY) : Infinity;
    let tMaxZ = dir.z !== 0 ? ((stepZ > 0 ? (z + 1 - oz) : (oz - z)) * tDeltaZ) : Infinity;

    for (let i = 0; i < 80; i++) {
      if (tMaxX < tMaxY && tMaxX < tMaxZ) {
        if (tMaxX > maxDist) break;
        x += stepX;
        tMaxX += tDeltaX;
        if (x < 0 || x >= W || y < 0 || y >= H || z < 0 || z >= D) return null;
        if (isSolid(x, y, z)) return { x, y, z, face: [-stepX, 0, 0] };
      } else if (tMaxY < tMaxZ) {
        if (tMaxY > maxDist) break;
        y += stepY;
        tMaxY += tDeltaY;
        if (x < 0 || x >= W || y < 0 || y >= H || z < 0 || z >= D) return null;
        if (isSolid(x, y, z)) return { x, y, z, face: [0, -stepY, 0] };
      } else {
        if (tMaxZ > maxDist) break;
        z += stepZ;
        tMaxZ += tDeltaZ;
        if (x < 0 || x >= W || y < 0 || y >= H || z < 0 || z >= D) return null;
        if (isSolid(x, y, z)) return { x, y, z, face: [0, 0, -stepZ] };
      }
    }

    return null;
  }

  function overlapsPlayer(tx, ty, tz) {
    return tx < player.x + WIDTH / 2 &&
           tx + 1 > player.x - WIDTH / 2 &&
           tz < player.z + WIDTH / 2 &&
           tz + 1 > player.z - WIDTH / 2 &&
           ty < player.y + HEIGHT &&
           ty + 1 > player.y + EPS;
  }

  function breakBlock() {
    const hit = raycast();
    if (!hit) return;
    setBlock(hit.x, hit.y, hit.z, AIR);
    rebuildMesh();
  }

  function placeBlock() {
    const hit = raycast();
    if (!hit || !hit.face) return;

    const tx = hit.x + hit.face[0];
    const ty = hit.y + hit.face[1];
    const tz = hit.z + hit.face[2];

    if (getBlock(tx, ty, tz) !== AIR) return;
    if (overlapsPlayer(tx, ty, tz)) return;

    setBlock(tx, ty, tz, selectedBlock);
    rebuildMesh();
  }

  // --- Input ---
  let locked = false;
  let selectedBlock = GRASS;
  let selectedSlot = 0;
  const keys = {};

  function updateHotbar() {
    const slots = document.querySelectorAll('.slot');
    slots.forEach((el, i) => {
      el.classList.toggle('selected', i === selectedSlot);
    });
    document.getElementById('selName').textContent =
      'Selected: ' + BLOCK_NAMES[selectedBlock];
  }

  function selectSlot(i) {
    if (i < 0 || i >= HOTBAR.length) return;
    selectedSlot = i;
    selectedBlock = HOTBAR[i];
    updateHotbar();
  }

  // Hotbar UI
  const hotbar = document.getElementById('hotbar');
  HOTBAR.forEach((id, i) => {
    const el = document.createElement('div');
    el.className = 'slot';
    el.innerHTML = `
      <div class="num">${i + 1}</div>
      <div class="swatch" style="background:${BLOCK_COLORS[id]}"></div>
      <div class="name">${BLOCK_NAMES[id]}</div>
    `;
    el.addEventListener('click', () => selectSlot(i));
    hotbar.appendChild(el);
  });
  updateHotbar();

  canvas.addEventListener('contextmenu', e => e.preventDefault());

  canvas.addEventListener('click', () => {
    if (!locked) {
      canvas.requestPointerLock();
    }
  });

  canvas.addEventListener('mousedown', e => {
    if (!locked) return;
    if (e.button === 0) breakBlock();
    else if (e.button === 2) placeBlock();
  });

  canvas.addEventListener('wheel', e => {
    if (!locked) return;
    e.preventDefault();
    const dir = e.deltaY > 0 ? 1 : -1;
    selectedSlot = (selectedSlot + dir + HOTBAR.length) % HOTBAR.length;
    selectSlot(selectedSlot);
  }, { passive: false });

  document.addEventListener('pointerlockchange', () => {
    locked = document.pointerLockElement === canvas;
    document.getElementById('hint').style.display = locked ? 'none' : 'block';
  });

  document.addEventListener('mousemove', e => {
    if (!locked) return;
    player.yaw += e.movementX * 0.002;
    player.pitch -= e.movementY * 0.002;
    player.pitch = Math.max(-1.52, Math.min(1.52, player.pitch));
  });

  function keyName(e) {
    if (e.key === ' ') return 'space';
    return e.key.toLowerCase();
  }

  document.addEventListener('keydown', e => {
    const k = keyName(e);
    keys[k] = true;

    if (k >= '1' && k <= '8') {
      selectSlot(parseInt(k, 10) - 1);
    }
    if (k === 'f') {
      player.fly = !player.fly;
      player.vy = 0;
      document.getElementById('mode').textContent = player.fly ? 'Fly' : 'Walking';
    }
  });

  document.addEventListener('keyup', e => {
    keys[keyName(e)] = false;
  });

  // --- Resize ---
  function resize() {
    const scale = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.floor(window.innerWidth * scale);
    canvas.height = Math.floor(window.innerHeight * scale);
    canvas.style.width = window.innerWidth + 'px';
    canvas.style.height = window.innerHeight + 'px';
    gl.viewport(0, 0, canvas.width, canvas.height);
  }
  window.addEventListener('resize', resize);
  resize();

  // --- Main loop ---
  let last = performance.now();
  let fps = 60;
  let frames = 0;
  let fpsTimer = 0;

  function update(dt) {
    if (dt > 0.1) dt = 0.1;

    const forwardInput = (keys['w'] ? 1 : 0) - (keys['s'] ? 1 : 0);
    const rightInput = (keys['d'] ? 1 : 0) - (keys['a'] ? 1 : 0);

    const fx = Math.sin(player.yaw);
    const fz = -Math.cos(player.yaw);
    const rx = Math.cos(player.yaw);
    const rz = Math.sin(player.yaw);

    let mx = fx * forwardInput + rx * rightInput;
    let mz = fz * forwardInput + rz * rightInput;

    const len = Math.hypot(mx, mz);
    if (len > 0) {
      mx /= len;
      mz /= len;
    }

    const sprint = keys['shift'] ? 1.55 : 1;
    const speed = player.fly ? 15 * sprint : 5.5 * sprint;

    const vx = mx * speed;
    const vz = mz * speed;

    if (player.fly) {
      player.vy = ((keys['space'] ? 1 : 0) - (keys['shift'] ? 1 : 0)) * 8 * sprint;
    } else {
      player.vy -= GRAVITY * dt;
      if (keys['space'] && player.onGround) {
        player.vy = JUMP_V;
        player.onGround = false;
      }
    }

    player.onGround = false;
    tryMove(vx * dt, player.vy * dt, vz * dt);

    if (player.y < -30) {
      player.x = W / 2 + 0.5;
      player.y = heightMap[Math.floor(D / 2) * W + Math.floor(W / 2)] + 3;
      player.z = D / 2 + 0.5;
      player.vy = 0;
    }
  }

  function render() {
    if (dirtyMesh) rebuildMesh();

    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

    const aspect = canvas.width / canvas.height;
    const proj = perspective(Math.PI / 3, aspect, 0.1, 120);

    const eye = [player.x, player.y + EYE, player.z];
    const fwd = normalize3(getForward());
    const target = [
      eye[0] + fwd[0],
      eye[1] + fwd[1],
      eye[2] + fwd[2]
    ];
    const view = lookAt(eye, target, [0, 1, 0]);

    gl.uniformMatrix4fv(uProj, false, proj);
    gl.uniformMatrix4fv(uView, false, view);

    bindBuffers();
    if (vertexCount > 0) {
      gl.drawArrays(gl.TRIANGLES, 0, vertexCount);
    }
  }

  function loop(now) {
    const dt = Math.min(0.05, (now - last) / 1000);
    last = now;

    update(dt);
    render();

    frames++;
    fpsTimer += dt;
    if (fpsTimer >= 0.5) {
      fps = Math.round(frames / fpsTimer);
      frames = 0;
      fpsTimer = 0;

      document.getElementById('fps').textContent = fps;
      document.getElementById('px').textContent = player.x.toFixed(2);
      document.getElementById('py').textContent = player.y.toFixed(2);
      document.getElementById('pz').textContent = player.z.toFixed(2);
      document.getElementById('mode').textContent = player.fly ? 'Fly' : 'Walking';
    }

    requestAnimationFrame(loop);
  }

  rebuildMesh();
  requestAnimationFrame(loop);
})();
</script>
</body>
</html>
```

### ポイント
- **チャンクなしでも動く**よう、まず「小さな世界をメッシュ化して描画」する簡易実装にしています。
- ブロックを置くとメッシュを再構築して反映します。
- テクスチャは全部 **Canvas で生成**しているので、外部画像不要です。
- 3D 描画は **WebGL** を直接使っています。
- 物理は簡易 AABB 衝突判定で、壁にめり込みにくくしています。