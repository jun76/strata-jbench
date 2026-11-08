以下を `minecraft-like.html` などとして保存し、ブラウザで開くと動く **マイクラ風3D箱庭ゲーム** になります。  
Three.js を使った1ファイル完結のWeb版で、**視点操作・WASD移動・重力・ブロック配置/破壊・自動地形生成**が主な機能です。

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>マイクラ風3D箱庭ゲーム</title>
  <style>
    html, body {
      margin: 0;
      width: 100%;
      height: 100%;
      overflow: hidden;
      background: #000;
      font-family: monospace;
      color: #fff;
      -webkit-user-select: none;
      user-select: none;
    }
    canvas {
      display: block;
    }
    #ui {
      position: fixed;
      inset: 0;
      pointer-events: none;
    }
    #crosshair {
      position: fixed;
      left: 50%;
      top: 50%;
      width: 14px;
      height: 14px;
      margin-left: -7px;
      margin-top: -7px;
      text-align: center;
      line-height: 14px;
      color: rgba(255,255,255,.8);
      font-size: 16px;
      text-shadow: 0 0 4px #000;
    }
    #help {
      position: fixed;
      top: 10px;
      right: 10px;
      background: rgba(0,0,0,.55);
      border: 1px solid rgba(255,255,255,.18);
      padding: 8px 10px;
      border-radius: 8px;
      font-size: 12px;
      line-height: 1.4;
      max-width: 280px;
    }
    #info {
      position: fixed;
      left: 10px;
      top: 10px;
      background: rgba(0,0,0,.55);
      border: 1px solid rgba(255,255,255,.18);
      padding: 8px 10px;
      border-radius: 8px;
      font-size: 12px;
      line-height: 1.45;
    }
    #hotbar {
      position: fixed;
      bottom: 18px;
      left: 50%;
      transform: translateX(-50%);
      display: flex;
      gap: 6px;
      pointer-events: none;
    }
    .slot {
      width: 48px;
      height: 48px;
      background: rgba(0,0,0,.45);
      border: 2px solid rgba(255,255,255,.25);
      box-sizing: border-box;
      position: relative;
    }
    .slot canvas {
      width: 100%;
      height: 100%;
      image-rendering: pixelated;
    }
    .slot .num {
      position: absolute;
      left: 2px;
      top: 1px;
      font-size: 10px;
      color: #fff;
      text-shadow: 1px 1px #000;
    }
    .slot.selected {
      border-color: #fff;
      box-shadow: 0 0 0 2px rgba(255,255,255,.25) inset;
    }
    #lockPrompt {
      position: fixed;
      inset: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      background: rgba(0,0,0,.72);
      pointer-events: none;
      transition: opacity .25s ease;
    }
    #lockPrompt .panel {
      background: rgba(0,0,0,.82);
      border: 1px solid rgba(255,255,255,.3);
      padding: 18px 22px;
      border-radius: 12px;
      text-align: center;
    }
    #lockPrompt .panel b {
      font-size: 18px;
      color: #8ef6c4;
    }
    #lockPrompt.hide {
      opacity: 0;
      pointer-events: none;
    }
  </style>
</head>
<body>
  <div id="ui">
    <div id="info"></div>
    <div id="help">
      <b>操作</b><br>
      クリック: 視点ロック<br>
      WASD: 移動 / Shift: スプリント / Space: ジャンプ<br>
      マウス左: ブロック破壊 / 右: ブロック配置<br>
      ホイール / 1〜8: ブロック選択<br>
      Esc: ロック解除
    </div>
    <div id="crosshair">＋</div>
    <div id="hotbar"></div>
    <div id="lockPrompt">
      <div class="panel">
        <b>ここをクリックして開始</b><br><br>
        マイクラ風3D箱庭ゲーム<br>
        Three.js 版
      </div>
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
  import * as THREE from 'three';

  // ============================================================
  // 基本設定
  // ============================================================
  const CHUNK_SIZE = 16;
  const WORLD_HEIGHT = 64;
  const RENDER_RADIUS = 4; // 半径4チャンク程度
  const MAX_VIEW_DIST = 7;
  const GRAVITY = 24;
  const MOVE_SPEED = 5.4;
  const SPRINT_SPEED = 8.2;
  const JUMP_SPEED = 8.3;
  const PLAYER_HALF_WIDTH = 0.3;
  const PLAYER_HEIGHT = 1.8;

  // ブロックID
  const AIR = 0;
  const GRASS = 1;
  const DIRT = 2;
  const STONE = 3;
  const COBBLE = 4;
  const WOOD = 5;
  const LEAVES = 6;
  const SAND = 7;
  const PLANKS = 8;

  const BLOCK_NAMES = [
    "空",
    "草",
    "土",
    "石",
    "石レンガ",
    "木材",
    "葉",
    "砂",
    "板材"
  ];

  const SOLID = [
    false, // AIR
    true,  // GRASS
    true,  // DIRT
    true,  // STONE
    true,  // COBBLE
    true,  // WOOD
    true,  // LEAVES
    true,  // SAND
    true   // PLANKS
  ];

  const HOTBAR = [GRASS, DIRT, STONE, COBBLE, WOOD, LEAVES, SAND, PLANKS];
  let selected = 0;

  // ============================================================
  // テクスチャアトラス
  // ============================================================
  const TILE = 16;
  const TILE_COUNT = 10;
  const atlasCanvas = document.createElement("canvas");
  atlasCanvas.width = TILE_COUNT * TILE;
  atlasCanvas.height = TILE;
  const atlasCtx = atlasCanvas.getContext("2d");
  atlasCtx.imageSmoothingEnabled = false;

  function hash2(x, y) {
    let n = Math.imul(x, 374761393) + Math.imul(y, 668265263);
    n = n ^ (n >> 13);
    n = Math.imul(n, 1274126177);
    n = n ^ (n >> 16);
    return (n >>> 0) / 4294967295;
  }

  function px(x, y, r, g, b) {
    atlasCtx.fillStyle = `rgb(${r|0},${g|0},${b|0})`;
    atlasCtx.fillRect(x, y, 1, 1);
  }

  function drawTile(tile, kind) {
    const ox = tile * TILE;
    for (let y = 0; y < TILE; y++) {
      for (let x = 0; x < TILE; x++) {
        const r = hash2(x + tile * 1000, y + tile * 2000);
        let rr, gg, bb;

        if (kind === "grass_top") {
          rr = 70 + r * 25;
          gg = 150 + r * 35;
          bb = 40 + r * 12;
          if (r < 0.18) { rr -= 18; gg -= 22; bb -= 8; }
        } else if (kind === "grass_side") {
          if (y < 4) {
            rr = 70 + r * 25;
            gg = 150 + r * 35;
            bb = 40 + r * 12;
          } else {
            rr = 122 + r * 22;
            gg = 91 + r * 18;
            bb = 55 + r * 12;
          }
          if (y >= 3 && y < 5 && r > 0.55) {
            rr = 70 + r * 25;
            gg = 150 + r * 35;
            bb = 40 + r * 12;
          }
        } else if (kind === "dirt") {
          rr = 122 + r * 22;
          gg = 91 + r * 18;
          bb = 55 + r * 12;
          if (r > 0.86) { rr -= 28; gg -= 18; bb -= 10; }
        } else if (kind === "stone") {
          rr = 126 + r * 30;
          gg = 126 + r * 30;
          bb = 126 + r * 30;
          if (r < 0.14) { rr -= 18; gg -= 18; bb -= 18; }
        } else if (kind === "cobble") {
          rr = 110 + r * 30;
          gg = 110 + r * 30;
          bb = 110 + r * 30;
          if (((x + y * 3) % 4) === 0) { rr -= 24; gg -= 24; bb -= 24; }
        } else if (kind === "log_side") {
          rr = 123 + r * 18;
          gg = 91 + r * 12;
          bb = 43 + r * 10;
          const stripe = Math.sin(x * 0.9 + r) * 0.5 + 0.5;
          if (stripe > 0.65) { rr -= 24; gg -= 16; bb -= 8; }
        } else if (kind === "log_top") {
          rr = 193 + r * 18;
          gg = 154 + r * 14;
          bb = 96 + r * 12;
          const cx = x - 8;
          const cy = y - 8;
          const d = Math.sqrt(cx*cx + cy*cy);
          if (d > 3 && d < 5 || d > 6 && d < 8) { rr -= 30; gg -= 22; bb -= 14; }
        } else if (kind === "leaves") {
          rr = 46 + r * 25;
          gg = 139 + r * 30;
          bb = 50 + r * 12;
          if (r > 0.72) { rr -= 18; gg -= 24; bb -= 12; }
          if (r < 0.22) { rr += 16; gg += 22; bb += 10; }
        } else if (kind === "sand") {
          rr = 201 + r * 18;
          gg = 194 + r * 16;
          bb = 119 + r * 14;
          if (r > 0.8) { rr -= 18; gg -= 16; bb -= 12; }
        } else if (kind === "planks") {
          rr = 165 + r * 14;
          gg = 121 + r * 12;
          bb = 57 + r * 10;
          if (y === 0 || y === 7 || y === 15) { rr -= 30; gg -= 22; bb -= 12; }
          if (x === 0 || x === 8) { rr -= 20; gg -= 14; bb -= 8; }
        } else {
          rr = 255; gg = 0; bb = 255;
        }

        px(ox + x, y, rr, gg, bb);
      }
    }
  }

  // tile index
  const GRASS_TOP = 0;
  const GRASS_SIDE = 1;
  const DIRT_TILE = 2;
  const STONE_TILE = 3;
  const COBBLE_TILE = 4;
  const LOG_SIDE = 5;
  const LOG_TOP = 6;
  const LEAVES_TILE = 7;
  const SAND_TILE = 8;
  const PLANKS_TILE = 9;

  drawTile(GRASS_TOP, "grass_top");
  drawTile(GRASS_SIDE, "grass_side");
  drawTile(DIRT_TILE, "dirt");
  drawTile(STONE_TILE, "stone");
  drawTile(COBBLE_TILE, "cobble");
  drawTile(LOG_SIDE, "log_side");
  drawTile(LOG_TOP, "log_top");
  drawTile(LEAVES_TILE, "leaves");
  drawTile(SAND_TILE, "sand");
  drawTile(PLANKS_TILE, "planks");

  const blockTexture = new THREE.CanvasTexture(atlasCanvas);
  blockTexture.magFilter = THREE.NearestFilter;
  blockTexture.minFilter = THREE.NearestFilter;
  blockTexture.wrapS = THREE.ClampToEdgeWrapping;
  blockTexture.wrapT = THREE.ClampToEdgeWrapping;
  blockTexture.colorSpace = THREE.SRGBColorSpace;

  function tileForBlock(block, faceIndex) {
    // faceIndex: 0:+X 1:-X 2:+Y 3:-Y 4:+Z 5:-Z
    if (block === GRASS) {
      if (faceIndex === 2) return GRASS_TOP;
      if (faceIndex === 3) return DIRT_TILE;
      return GRASS_SIDE;
    }
    if (block === DIRT) return DIRT_TILE;
    if (block === STONE) return STONE_TILE;
    if (block === COBBLE) return COBBLE_TILE;
    if (block === WOOD) {
      if (faceIndex === 2 || faceIndex === 3) return LOG_TOP;
      return LOG_SIDE;
    }
    if (block === LEAVES) return LEAVES_TILE;
    if (block === SAND) return SAND_TILE;
    if (block === PLANKS) return PLANKS_TILE;
    return STONE_TILE;
  }

  // ============================================================
  // 地形ノイズ
  // ============================================================
  function smoothstep(t) {
    return t * t * (3 - 2 * t);
  }

  function valueNoise2(x, z) {
    const ix = Math.floor(x);
    const iz = Math.floor(z);
    const fx = x - ix;
    const fz = z - iz;

    const a = hash2(ix, iz);
    const b = hash2(ix + 1, iz);
    const c = hash2(ix, iz + 1);
    const d = hash2(ix + 1, iz + 1);

    const sx = smoothstep(fx);
    const sz = smoothstep(fz);

    const ab = a * (1 - sx) + b * sx;
    const cd = c * (1 - sx) + d * sx;
    return ab * (1 - sz) + cd * sz;
  }

  function terrainHeight(wx, wz) {
    let h = 24;
    h += 10 * valueNoise2(wx / 48, wz / 48);
    h += 5 * valueNoise2(wx / 16, wz / 16);
    h += 2 * valueNoise2(wx / 7, wz / 7);
    h = Math.floor(h);
    if (h < 4) h = 4;
    if (h > WORLD_HEIGHT - 12) h = WORLD_HEIGHT - 12;
    return h;
  }

  // ============================================================
  // ワールド
  // ============================================================
  const chunks = new Map();

  function chunkKey(cx, cz) {
    return `${cx},${cz}`;
  }

  function blockIndex(x, y, z) {
    return (x * CHUNK_SIZE + z) * WORLD_HEIGHT + y;
  }

  function makeChunk(cx, cz) {
    const data = new Uint8Array(CHUNK_SIZE * CHUNK_SIZE * WORLD_HEIGHT);
    const chunk = {
      cx, cz,
      key: chunkKey(cx, cz),
      data,
      mesh: null,
      dirty: true
    };

    for (let x = 0; x < CHUNK_SIZE; x++) {
      for (let z = 0; z < CHUNK_SIZE; z++) {
        const wx = cx * CHUNK_SIZE + x;
        const wz = cz * CHUNK_SIZE + z;
        const h = terrainHeight(wx, wz);

        for (let y = 0; y < WORLD_HEIGHT; y++) {
          let block = AIR;

          if (y <= h) {
            if (y === h) {
              if (h <= 17) block = SAND;
              else block = GRASS;
            } else if (y > h - 4) {
              block = DIRT;
            } else {
              block = STONE;
            }
          }

          data[blockIndex(x, y, z)] = block;
        }
      }
    }

    // 木をチャンク内安全領域に生成
    for (let x = 2; x < CHUNK_SIZE - 2; x++) {
      for (let z = 2; z < CHUNK_SIZE - 2; z++) {
        const wx = cx * CHUNK_SIZE + x;
        const wz = cz * CHUNK_SIZE + z;
        const h = terrainHeight(wx, wz);

        if (h <= 18 || h > WORLD_HEIGHT - 10) continue;

        const r = hash2(wx * 37 + 11, wz * 57 + 13);
        if (r <= 0.985) continue;

        const trunkH = 3 + Math.floor(r * 3);
        const topY = h + trunkH;
        if (topY + 3 >= WORLD_HEIGHT) continue;

        for (let y = h + 1; y <= topY; y++) {
          data[blockIndex(x, y, z)] = WOOD;
        }

        for (let dy = 0; dy <= 2; dy++) {
          const yy = topY + dy;
          if (yy >= WORLD_HEIGHT) break;

          let radius;
          if (dy === 0) radius = 2;
          else if (dy === 1) radius = 2;
          else radius = 1;

          for (let dx = -radius; dx <= radius; dx++) {
            for (let dz = -radius; dz <= radius; dz++) {
              if (Math.abs(dx) + Math.abs(dz) > radius + 1) continue;
              if (dx === 0 && dz === 0 && dy === 0) continue;

              const lx = x + dx;
              const lz = z + dz;
              if (lx < 0 || lx >= CHUNK_SIZE || lz < 0 || lz >= CHUNK_SIZE) continue;

              const idx = blockIndex(lx, yy, lz);
              if (data[idx] === AIR) {
                data[idx] = LEAVES;
              }
            }
          }
        }
      }
    }

    return chunk;
  }

  function ensureChunk(cx, cz) {
    const key = chunkKey(cx, cz);
    let chunk = chunks.get(key);
    if (!chunk) {
      chunk = makeChunk(cx, cz);
      chunks.set(key, chunk);
    }
    return chunk;
  }

  function getBlockGlobal(wx, wy, wz) {
    if (wy < 0) return STONE;
    if (wy >= WORLD_HEIGHT) return AIR;

    const cx = Math.floor(wx / CHUNK_SIZE);
    const cz = Math.floor(wz / CHUNK_SIZE);
    const chunk = chunks.get(chunkKey(cx, cz));
    if (!chunk) return AIR;

    const lx = wx - cx * CHUNK_SIZE;
    const lz = wz - cz * CHUNK_SIZE;
    return chunk.data[blockIndex(lx, wy, lz)];
  }

  function isSolidBlock(block) {
    if (block <= 0 || block >= SOLID.length) return false;
    return SOLID[block];
  }

  function setBlockGlobal(wx, wy, wz, block) {
    if (wy < 0 || wy >= WORLD_HEIGHT) return false;

    const cx = Math.floor(wx / CHUNK_SIZE);
    const cz = Math.floor(wz / CHUNK_SIZE);
    const chunk = chunks.get(chunkKey(cx, cz));
    if (!chunk) return false;

    const lx = wx - cx * CHUNK_SIZE;
    const lz = wz - cz * CHUNK_SIZE;
    chunk.data[blockIndex(lx, wy, lz)] = block;

    rebuildChunk(chunk);

    if (lx === 0) {
      const n = chunks.get(chunkKey(cx - 1, cz));
      if (n) rebuildChunk(n);
    }
    if (lx === CHUNK_SIZE - 1) {
      const n = chunks.get(chunkKey(cx + 1, cz));
      if (n) rebuildChunk(n);
    }
    if (lz === 0) {
      const n = chunks.get(chunkKey(cx, cz - 1));
      if (n) rebuildChunk(n);
    }
    if (lz === CHUNK_SIZE - 1) {
      const n = chunks.get(chunkKey(cx, cz + 1));
      if (n) rebuildChunk(n);
    }

    return true;
  }

  // ============================================================
  // チャンクメッシュ生成
  // ============================================================
  const FACES = [
    { dir: [ 1, 0, 0], corners: [[1,0,1],[1,0,0],[1,1,0],[1,1,1]] },
    { dir: [-1, 0, 0], corners: [[0,0,0],[0,0,1],[0,1,1],[0,1,0]] },
    { dir: [ 0, 1, 0], corners: [[0,1,1],[1,1,1],[1,1,0],[0,1,0]] },
    { dir: [ 0,-1, 0], corners: [[0,0,0],[1,0,0],[1,0,1],[0,0,1]] },
    { dir: [ 0, 0, 1], corners: [[1,0,1],[0,0,1],[0,1,1],[1,1,1]] },
    { dir: [ 0, 0,-1], corners: [[0,0,0],[1,0,0],[1,1,0],[0,1,0]] }
  ];

  const material = new THREE.MeshLambertMaterial({
    map: blockTexture,
    side: THREE.DoubleSide,
    transparent: false
  });

  function uvForCorner(faceIndex, corner) {
    let uvx;
    if (faceIndex === 0 || faceIndex === 1) uvx = corner[2];
    else if (faceIndex === 2 || faceIndex === 3) uvx = corner[0];
    else uvx = corner[0];

    const uvy = 1 - corner[1];
    return [uvx, uvy];
  }

  function tileUV(tile, uvx, uvy) {
    const tileU = tile / TILE_COUNT;
    const tileSize = 1 / TILE_COUNT;
    const u = tileU + uvx * tileSize;
    const v = 1 - uvy;
    return [u, v];
  }

  function buildChunkGeometry(chunk) {
    const positions = [];
    const normals = [];
    const uvs = [];
    const indices = [];

    const data = chunk.data;

    for (let x = 0; x < CHUNK_SIZE; x++) {
      for (let y = 0; y < WORLD_HEIGHT; y++) {
        for (let z = 0; z < CHUNK_SIZE; z++) {
          const block = data[blockIndex(x, y, z)];
          if (block === AIR) continue;

          for (let faceIndex = 0; faceIndex < FACES.length; faceIndex++) {
            const face = FACES[faceIndex];
            const nx = chunk.cx * CHUNK_SIZE + x + face.dir[0];
            const ny = y + face.dir[1];
            const nz = chunk.cz * CHUNK_SIZE + z + face.dir[2];

            const neighbor = getBlockGlobal(nx, ny, nz);
            if (neighbor !== AIR) continue;

            const tile = tileForBlock(block, faceIndex);
            const baseIndex = positions.length / 3;

            for (let i = 0; i < 4; i++) {
              const c = face.corners[i];
              positions.push(chunk.cx * CHUNK_SIZE + x + c[0], y + c[1], chunk.cz * CHUNK_SIZE + z + c[2]);
              normals.push(face.dir[0], face.dir[1], face.dir[2]);

              const uv = uvForCorner(faceIndex, c);
              const [tu, tv] = tileUV(tile, uv[0], uv[1]);
              uvs.push(tu, tv);
            }

            indices.push(baseIndex, baseIndex + 1, baseIndex + 2);
            indices.push(baseIndex, baseIndex + 2, baseIndex + 3);
          }
        }
      }
    }

    const geometry = new THREE.BufferGeometry();
    if (positions.length > 0) {
      geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
      geometry.setAttribute("normal", new THREE.Float32BufferAttribute(normals, 3));
      geometry.setAttribute("uv", new THREE.Float32BufferAttribute(uvs, 2));
      geometry.setIndex(indices);
      geometry.computeBoundingSphere();
    }

    return geometry;
  }

  function rebuildChunk(chunk) {
    const geometry = buildChunkGeometry(chunk);

    if (!chunk.mesh) {
      chunk.mesh = new THREE.Mesh(geometry, material);
      chunk.mesh.frustumCulled = true;
      scene.add(chunk.mesh);
    } else {
      chunk.mesh.geometry.dispose();
      chunk.mesh.geometry = geometry;
    }

    chunk.dirty = false;
  }

  function unloadFarChunks(pc) {
    const removeList = [];
    for (const chunk of chunks.values()) {
      const dx = chunk.cx - pc.x;
      const dz = chunk.cz - pc.z;
      const d = Math.max(Math.abs(dx), Math.abs(dz));
      if (d > RENDER_RADIUS + 2) {
        removeList.push(chunk);
      }
    }
    for (const chunk of removeList) {
      if (chunk.mesh) {
        scene.remove(chunk.mesh);
        chunk.mesh.geometry.dispose();
      }
      chunks.delete(chunk.key);
    }
  }

  // ============================================================
  // Three.js
  // ============================================================
  const renderer = new THREE.WebGLRenderer({ antialias: false });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  document.body.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x87c6ff);
  scene.fog = new THREE.Fog(0x87c6ff, 30, 120);

  const camera = new THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 0.1, 300);
  camera.rotation.order = "YXZ";

  const hemi = new THREE.HemisphereLight(0xcfefff, 0x52633a, 1.0);
  scene.add(hemi);

  const sun = new THREE.DirectionalLight(0xfff4d5, 0.8);
  sun.position.set(80, 130, 40);
  scene.add(sun);

  // 選択枠
  const selectionGeometry = new THREE.BoxGeometry(1.002, 1.002, 1.002);
  const selectionEdges = new THREE.EdgesGeometry(selectionGeometry);
  const selection = new THREE.LineSegments(
    selectionEdges,
    new THREE.LineBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.7 })
  );
  selection.visible = false;
  scene.add(selection);

  // 配置プレビュー
  const ghost = new THREE.Mesh(
    new THREE.BoxGeometry(0.98, 0.98, 0.98),
    new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.22 })
  );
  ghost.visible = false;
  scene.add(ghost);

  // ============================================================
  // プレイヤー
  // ============================================================
  const player = {
    pos: new THREE.Vector3(0.5, 50, 0.5),
    vel: new THREE.Vector3(0, 0, 0),
    yaw: 0,
    pitch: 0,
    onGround: false
  };

  const keys = new Set();

  function collidesAt(p) {
    const eps = 0.001;
    const minX = Math.floor(p.x - PLAYER_HALF_WIDTH + eps);
    const maxX = Math.floor(p.x + PLAYER_HALF_WIDTH - eps);
    const minZ = Math.floor(p.z - PLAYER_HALF_WIDTH + eps);
    const maxZ = Math.floor(p.z + PLAYER_HALF_WIDTH - eps);
    const minY = Math.floor(p.y + eps);
    const maxY = Math.floor(p.y + PLAYER_HEIGHT - eps);

    for (let x = minX; x <= maxX; x++) {
      for (let y = minY; y <= maxY; y++) {
        for (let z = minZ; z <= maxZ; z++) {
          if (isSolidBlock(getBlockGlobal(x, y, z))) {
            return true;
          }
        }
      }
    }
    return false;
  }

  function moveAxis(axis, amount) {
    const old = player.pos[axis];
    player.pos[axis] += amount;

    if (collidesAt(player.pos)) {
      player.pos[axis] = old;
      if (axis === "y") {
        if (amount < 0) {
          player.onGround = true;
        }
        player.vel.y = 0;
      } else {
        player.vel[axis] = 0;
      }
      return true;
    }

    return false;
  }

  function updatePlayer(dt) {
    const sprint = keys.has("ShiftLeft") || keys.has("ShiftRight");
    const speed = sprint ? SPRINT_SPEED : MOVE_SPEED;

    const fx = Math.sin(player.yaw);
    const fz = Math.cos(player.yaw);

    let inputX = 0;
    let inputZ = 0;

    if (keys.has("KeyW")) { inputX += fx; inputZ += fz; }
    if (keys.has("KeyS")) { inputX -= fx; inputZ -= fz; }
    if (keys.has("KeyA")) { inputX += fz; inputZ -= fx; }
    if (keys.has("KeyD")) { inputX -= fz; inputZ += fx; }

    const len = Math.hypot(inputX, inputZ);
    if (len > 0.0001) {
      inputX /= len;
      inputZ /= len;
    }

    player.vel.x = inputX * speed;
    player.vel.z = inputZ * speed;

    if (player.onGround && keys.has("Space")) {
      player.vel.y = JUMP_SPEED;
      player.onGround = false;
    }

    player.vel.y -= GRAVITY * dt;
    player.vel.y = Math.max(player.vel.y, -35);

    player.onGround = false;

    const moveX = player.vel.x * dt;
    const moveZ = player.vel.z * dt;
    const moveY = player.vel.y * dt;

    moveAxis("x", moveX);
    moveAxis("z", moveZ);
    moveAxis("y", moveY);

    // 安全のため、地面判定
    const below = getBlockGlobal(Math.floor(player.pos.x), Math.floor(player.pos.y - 0.05), Math.floor(player.pos.z));
    if (isSolidBlock(below) && player.vel.y <= 0.1) {
      player.onGround = true;
    }

    camera.position.set(player.pos.x, player.pos.y + 1.62, player.pos.z);
    camera.rotation.y = player.yaw;
    camera.rotation.x = player.pitch;
  }

  // ============================================================
  // ボクセルレイキャスト
  // ============================================================
  function raycast(origin, dir, maxDist) {
    let x = Math.floor(origin.x);
    let y = Math.floor(origin.y);
    let z = Math.floor(origin.z);

    const stepX = dir.x > 0 ? 1 : dir.x < 0 ? -1 : 0;
    const stepY = dir.y > 0 ? 1 : dir.y < 0 ? -1 : 0;
    const stepZ = dir.z > 0 ? 1 : dir.z < 0 ? -1 : 0;

    const dxAbs = Math.abs(dir.x);
    const dyAbs = Math.abs(dir.y);
    const dzAbs = Math.abs(dir.z);

    let tMaxX = stepX === 0 ? Infinity : ((stepX > 0 ? x + 1 - origin.x : origin.x - x) / dxAbs);
    let tMaxY = stepY === 0 ? Infinity : ((stepY > 0 ? y + 1 - origin.y : origin.y - y) / dyAbs);
    let tMaxZ = stepZ === 0 ? Infinity : ((stepZ > 0 ? z + 1 - origin.z : origin.z - z) / dzAbs);

    let tDistX = stepX === 0 ? Infinity : 1 / dxAbs;
    let tDistY = stepY === 0 ? Infinity : 1 / dyAbs;
    let tDistZ = stepZ === 0 ? Infinity : 1 / dzAbs;

    let dist = 0;
    let normal = [0, -1, 0];

    while (dist <= maxDist) {
      const block = getBlockGlobal(x, y, z);
      if (isSolidBlock(block)) {
        return {
          block: [x, y, z],
          normal: [
            stepX === 0 ? 0 : -stepX,
            stepY === 0 ? 0 : -stepY,
            stepZ === 0 ? 0 : -stepZ
          ],
          dist
        };
      }

      if (tMaxX < tMaxY && tMaxX < tMaxZ) {
        if (tMaxX > maxDist) break;
        dist = tMaxX;
        x += stepX;
        tMaxX += tDistX;
        normal = [-stepX, 0, 0];
      } else if (tMaxY < tMaxZ) {
        if (tMaxY > maxDist) break;
        dist = tMaxY;
        y += stepY;
        tMaxY += tDistY;
        normal = [0, -stepY, 0];
      } else {
        if (tMaxZ > maxDist) break;
        dist = tMaxZ;
        z += stepZ;
        tMaxZ += tDistZ;
        normal = [0, 0, -stepZ];
      }
    }

    return null;
  }

  // ============================================================
  // 入力
  // ============================================================
  const lockPrompt = document.getElementById("lockPrompt");
  let pointerLocked = false;

  window.addEventListener("keydown", e => {
    keys.add(e.code);
    if (e.code.startsWith("Digit")) {
      const n = parseInt(e.code.slice(5), 10);
      if (n >= 1 && n <= HOTBAR.length) {
        selected = n - 1;
        updateHotbar();
      }
    }
  });

  window.addEventListener("keyup", e => {
    keys.delete(e.code);
  });

  document.addEventListener("pointerlockchange", () => {
    pointerLocked = document.pointerLockElement === renderer.domElement;
    lockPrompt.classList.toggle("hide", pointerLocked);
  });

  lockPrompt.addEventListener("click", () => {
    renderer.domElement.requestPointerLock();
  });

  renderer.domElement.addEventListener("click", () => {
    if (!pointerLocked) {
      renderer.domElement.requestPointerLock();
    }
  });

  document.addEventListener("mousemove", e => {
    if (!pointerLocked) return;
    const sens = 0.0022;
    player.yaw -= e.movementX * sens;
    player.pitch -= e.movementY * sens;
    player.pitch = Math.max(-1.55, Math.min(1.55, player.pitch));
  });

  document.addEventListener("mousedown", e => {
    if (!pointerLocked) return;
    if (e.button === 0) breakBlock();
    if (e.button === 2) placeBlock();
  });

  document.addEventListener("wheel", e => {
    if (!pointerLocked) return;
    selected += (e.deltaY > 0 ? 1 : -1);
    if (selected < 0) selected += HOTBAR.length;
    if (selected >= HOTBAR.length) selected -= HOTBAR.length;
    updateHotbar();
  }, { passive: true });

  document.addEventListener("contextmenu", e => e.preventDefault());

  function breakBlock() {
    const hit = getCurrentRayHit();
    if (!hit) return;
    setBlockGlobal(hit.block[0], hit.block[1], hit.block[2], AIR);
  }

  function placeBlock() {
    const hit = getCurrentRayHit();
    if (!hit) return;

    const px = hit.block[0] + hit.normal[0];
    const py = hit.block[1] + hit.normal[1];
    const pz = hit.block[2] + hit.normal[2];

    if (py < 0 || py >= WORLD_HEIGHT) return;
    if (getBlockGlobal(px, py, pz) !== AIR) return;

    // プレイヤーが占領する場合は置かない
    const eps = 0.001;
    const minX = Math.floor(player.pos.x - PLAYER_HALF_WIDTH + eps);
    const maxX = Math.floor(player.pos.x + PLAYER_HALF_WIDTH - eps);
    const minZ = Math.floor(player.pos.z - PLAYER_HALF_WIDTH + eps);
    const maxZ = Math.floor(player.pos.z + PLAYER_HALF_WIDTH - eps);
    const minY = Math.floor(player.pos.y + eps);
    const maxY = Math.floor(player.pos.y + PLAYER_HEIGHT - eps);

    if (px >= minX && px <= maxX && pz >= minZ && pz <= maxZ && py >= minY && py <= maxY) return;

    const cx = Math.floor(px / CHUNK_SIZE);
    const cz = Math.floor(pz / CHUNK_SIZE);
    ensureChunk(cx, cz);
    setBlockGlobal(px, py, pz, HOTBAR[selected]);
  }

  function getCurrentRayHit() {
    const dir = camera.getWorldDirection(new THREE.Vector3());
    return raycast(camera.position, dir, MAX_VIEW_DIST);
  }

  function updateSelection() {
    const hit = getCurrentRayHit();
    if (!hit) {
      selection.visible = false;
      ghost.visible = false;
      return;
    }

    selection.visible = true;
    selection.position.set(hit.block[0] + 0.5, hit.block[1] + 0.5, hit.block[2] + 0.5);

    const gx = hit.block[0] + hit.normal[0];
    const gy = hit.block[1] + hit.normal[1];
    const gz = hit.block[2] + hit.normal[2];

    ghost.visible = gy >= 0 && gy < WORLD_HEIGHT && getBlockGlobal(gx, gy, gz) === AIR;
    ghost.position.set(gx + 0.5, gy + 0.5, gz + 0.5);
  }

  // ============================================================
  // ホットバーUI
  // ============================================================
  const hotbar = document.getElementById("hotbar");
  const slots = [];

  function createHotbar() {
    for (let i = 0; i < HOTBAR.length; i++) {
      const slot = document.createElement("div");
      slot.className = "slot";
      const num = document.createElement("div");
      num.className = "num";
      num.textContent = String(i + 1);
      slot.appendChild(num);

      const c = document.createElement("canvas");
      c.width = 48;
      c.height = 48;
      c.style.imageRendering = "pixelated";
      slot.appendChild(c);

      const ctx = c.getContext("2d");
      ctx.imageSmoothingEnabled = false;
      const tile = tileForBlock(HOTBAR[i], 2);
      ctx.drawImage(atlasCanvas, tile * TILE, 0, TILE, TILE, 0, 0, 48, 48);

      hotbar.appendChild(slot);
      slots.push(slot);
    }
    updateHotbar();
  }

  function updateHotbar() {
    slots.forEach((slot, i) => {
      slot.classList.toggle("selected", i === selected);
    });
  }

  createHotbar();

  // ============================================================
  // 情報表示
  // ============================================================
  const infoEl = document.getElementById("info");
  let lastInfoUpdate = 0;

  function updateInfo(now) {
    if (now - lastInfoUpdate < 0.18) return;
    lastInfoUpdate = now;

    const pcx = Math.floor(player.pos.x / CHUNK_SIZE);
    const pcz = Math.floor(player.pos.z / CHUNK_SIZE);
    infoEl.innerHTML = `
      FPS: ${fps.toFixed(1)}<br>
      座標: ${player.pos.x.toFixed(1)}, ${player.pos.y.toFixed(1)}, ${player.pos.z.toFixed(1)}<br>
      チャンク: ${pcx}, ${pcz}<br>
      選択: ${BLOCK_NAMES[HOTBAR[selected]]}
    `;
  }

  // ============================================================
  // メインループ
  // ============================================================
  const clock = new THREE.Clock();
  let buildQueue = [];
  let lastTime = performance.now();
  let fps = 0;

  function requestChunksAroundPlayer() {
    const pcx = Math.floor(player.pos.x / CHUNK_SIZE);
    const pcz = Math.floor(player.pos.z / CHUNK_SIZE);

    for (let dx = -RENDER_RADIUS; dx <= RENDER_RADIUS; dx++) {
      for (let dz = -RENDER_RADIUS; dz <= RENDER_RADIUS; dz++) {
        const cx = pcx + dx;
        const cz = pcz + dz;
        const chunk = ensureChunk(cx, cz);
        if (chunk.dirty && !buildQueue.some(k => k === chunk.key)) {
          buildQueue.push(chunk.key);
        }
      }
    }

    unloadFarChunks({ x: pcx, z: pcz });
  }

  function processBuildQueue() {
    // 1フレームで多く作りすぎない
    const maxPerFrame = 2;
    for (let i = 0; i < maxPerFrame && buildQueue.length > 0; i++) {
      const key = buildQueue.shift();
      const chunk = chunks.get(key);
      if (chunk && chunk.dirty) rebuildChunk(chunk);
    }
  }

  function animate() {
    const dt = Math.min(clock.getDelta(), 0.05);

    updatePlayer(dt);
    requestChunksAroundPlayer();
    processBuildQueue();
    updateSelection();

    const now = performance.now();
    const delta = (now - lastTime) / 1000;
    lastTime = now;
    fps = fps * 0.8 + (1 / Math.max(delta, 0.0001)) * 0.2;
    updateInfo(now);

    renderer.render(scene, camera);
    requestAnimationFrame(animate);
  }

  window.addEventListener("resize", () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

  animate();
  </script>
</body>
</html>
```