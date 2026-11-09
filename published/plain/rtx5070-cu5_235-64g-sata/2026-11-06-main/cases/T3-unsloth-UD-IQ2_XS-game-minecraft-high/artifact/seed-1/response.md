以下は、ブラウザだけで動く「マイクラ風 3D 箱庭」の単一 HTML ファイルです。
`three.js` を CDN から読み込むだけで、地形生成・ブロック設置/破壊・視点操作・当たり判定・ホットバー・簡易な昼夜変化があります。

**使い方**
1. 下記コードを `minecraft.html` などのファイルに保存
2. ブラウザで開く
3. 画面をクリックしてマウスロック
4. 操作:
   - `W/A/S/D`: 移動
   - `Space`: ジャンプ
   - `Shift`: 走る
   - `マウス左`: 破壊
   - `マウス右`: 設置
   - `1〜7`: ブロック選択
   - `ホイール`: ブロック選択
   - `Esc`: 解放

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Voxel Sandbox</title>
  <style>
    html, body {
      margin: 0;
      height: 100%;
      overflow: hidden;
      background: #000;
      font-family: "Segoe UI", monospace;
    }

    canvas {
      display: block;
    }

    #ui {
      position: absolute;
      left: 12px;
      top: 12px;
      color: #fff;
      text-shadow: 1px 1px 2px #000;
      pointer-events: none;
      user-select: none;
      line-height: 1.55;
      font-size: 13px;
    }

    #title {
      font-weight: bold;
      margin-bottom: 8px;
      font-size: 16px;
    }

    #crosshair {
      position: absolute;
      left: 50%;
      top: 50%;
      transform: translate(-50%, -50%);
      width: 6px;
      height: 6px;
      background: rgba(255,255,255,.92);
      border: 1px solid #000;
      pointer-events: none;
    }

    #hotbar {
      position: absolute;
      left: 50%;
      bottom: 18px;
      transform: translateX(-50%);
      display: flex;
      gap: 6px;
      pointer-events: none;
    }

    .slot {
      width: 46px;
      height: 46px;
      border: 2px solid rgba(0,0,0,.6);
      background: rgba(0,0,0,.24);
      box-sizing: border-box;
      position: relative;
    }

    .slot.selected {
      border-color: #fff;
      box-shadow: 0 0 0 2px rgba(0,0,0,.45), 0 0 12px rgba(255,255,255,.22);
    }

    .slot span {
      display: block;
      width: 100%;
      height: 100%;
      image-rendering: pixelated;
      opacity: .96;
    }

    .slot::after {
      content: attr(data-key);
      position: absolute;
      top: 2px;
      left: 4px;
      color: #fff;
      text-shadow: 1px 1px 1px #000;
      font-size: 10px;
      opacity: .9;
    }
  </style>
</head>
<body>
  <div id="ui">
    <div id="title">Voxel Sandbox</div>
    クリックでマウスロック<br>
    WASD:移動 / Space:ジャンプ / Shift:走る<br>
    左クリック:破壊 / 右クリック:設置<br>
    1〜7 / ホイール:ブロック選択
  </div>

  <div id="crosshair"></div>
  <div id="hotbar"></div>

  <script src="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js"></script>
  <script>
    // ===================================================================
    // 基本定数
    // ===================================================================
    const CHUNK_SIZE = 16;
    const CHUNKS = 4;
    const WORLD_SIZE = CHUNK_SIZE * CHUNKS; // 64
    const HEIGHT = 32;
    const SEA_LEVEL = 11;

    const AIR = 0;
    const GRASS = 1;
    const DIRT = 2;
    const STONE = 3;
    const WOOD = 4;
    const LEAF = 5;
    const SAND = 6;
    const WATER = 7;

    const BLOCK_COLORS = [
      null,
      [0.34, 0.63, 0.27], // grass
      [0.47, 0.34, 0.22], // dirt
      [0.56, 0.57, 0.60], // stone
      [0.47, 0.33, 0.17], // wood
      [0.25, 0.50, 0.25], // leaf
      [0.81, 0.74, 0.53], // sand
      [0.19, 0.41, 0.78]  // water
    ];

    const BLOCK_CSS = [
      "#55a34a", // 1 grass
      "#78543c", // 2 dirt
      "#8f9092", // 3 stone
      "#7a5632", // 4 wood
      "#408040", // 5 leaf
      "#cfc08c", // 6 sand
      "#3b80a0"  // 7 water
    ];

    const BLOCK_NAMES = [
      "", "Grass", "Dirt", "Stone", "Wood", "Leaf", "Sand", "Water"
    ];

    // 面定義: [x軸, y軸, z軸] 方向 + 四隅
    const FACES = [
      { dir: [-1, 0, 0], corners: [[0,0,1],[0,0,0],[0,1,0],[0,1,1]] }, // -X
      { dir: [ 1, 0, 0], corners: [[1,0,0],[1,0,1],[1,1,1],[1,1,0]] }, // +X
      { dir: [ 0,-1, 0], corners: [[0,0,1],[1,0,1],[1,0,0],[0,0,0]] }, // -Y
      { dir: [ 0, 1, 0], corners: [[0,1,0],[1,1,0],[1,1,1],[0,1,1]] }, // +Y
      { dir: [ 0, 0,-1], corners: [[0,1,0],[0,0,0],[1,0,0],[1,1,0]] }, // -Z
      { dir: [ 0, 0, 1], corners: [[0,0,1],[0,1,1],[1,1,1],[1,0,1]] }  // +Z
    ];

    const FACE_LIGHT = [0.82, 0.86, 0.68, 1.0, 0.90, 0.92];

    // ===================================================================
    // シーン初期化
    // ===================================================================
    let scene, camera, renderer;
    let player;
    let world;
    let topY;
    let chunkMeshes;
    let opaqueMaterial, waterMaterial;

    let selected = GRASS;
    let time = 0;
    let locked = false;

    const keys = {};
    const EPS = 0.001;
    const EYE = 1.62;
    const PLAYER_WIDTH = 0.6;
    const PLAYER_HEIGHT = 1.8;
    const HALF_W = PLAYER_WIDTH / 2;

    const dayColor = new THREE.Color("#87ceeb");
    const nightColor = new THREE.Color("#0b1020");
    const skyColor = new THREE.Color();

    init();
    generateWorld();
    buildAllChunks();
    spawnPlayer();
    setupUI();
    setupInput();
    animate();

    function init() {
      scene = new THREE.Scene();
      camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 500);
      camera.rotation.order = "YXZ";

      renderer = new THREE.WebGLRenderer({ antialias: true });
      renderer.setSize(window.innerWidth, window.innerHeight);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      document.body.appendChild(renderer.domElement);

      scene.fog = new THREE.Fog(dayColor.getHex(), 25, 120);
      scene.background = dayColor.clone();

      opaqueMaterial = new THREE.MeshBasicMaterial({
        vertexColors: true,
        fog: true,
        side: THREE.DoubleSide
      });

      waterMaterial = new THREE.MeshBasicMaterial({
        vertexColors: true,
        fog: true,
        transparent: true,
        opacity: 0.72,
        depthWrite: false,
        side: THREE.DoubleSide
      });

      world = new Uint8Array(WORLD_SIZE * WORLD_SIZE * HEIGHT);
      topY = new Uint8Array(WORLD_SIZE * WORLD_SIZE);

      chunkMeshes = Array.from({ length: CHUNKS * CHUNKS }, () => ({
        opaque: null,
        water: null
      }));

      player = {
        pos: new THREE.Vector3(WORLD_SIZE / 2 + 0.5, 24, WORLD_SIZE / 2 + 0.5),
        vel: new THREE.Vector3(),
        yaw: 0,
        pitch: 0,
        onGround: false
      };

      window.addEventListener("resize", () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
      });
    }

    // ===================================================================
    // 雑音・世界生成
    // ===================================================================
    function hash2(x, z) {
      let h = (x * 374761393 + z * 668265263) | 0;
      h = Math.imul(h ^ (h >>> 13), 1274126177);
      h = (h ^ (h >>> 16)) | 0;
      return (h >>> 0) / 4294967295;
    }

    function hash3(x, y, z) {
      return hash2(x * 73856093 + y * 19349663, z * 83492791 + y * 265443576);
    }

    function noise2(x, z) {
      const ix = Math.floor(x);
      const iz = Math.floor(z);
      const fx = x - ix;
      const fz = z - iz;
      const sx = fx * fx * (3 - 2 * fx);
      const sz = fz * fz * (3 - 2 * fz);

      const v00 = hash2(ix, iz);
      const v10 = hash2(ix + 1, iz);
      const v01 = hash2(ix, iz + 1);
      const v11 = hash2(ix + 1, iz + 1);

      const a = v00 * (1 - sx) + v10 * sx;
      const b = v01 * (1 - sx) + v11 * sx;
      return a * (1 - sz) + b * sz;
    }

    function terrainHeight(x, z) {
      const base = 10;
      const hills = noise2(x * 0.045, z * 0.045) * 7;
      const detail = noise2(x * 0.12, z * 0.12) * 4;
      const mountain = Math.pow(noise2(x * 0.022, z * 0.022), 2) * 11;
      const h = Math.floor(base + hills + detail + mountain);
      return Math.max(2, Math.min(HEIGHT - 8, h));
    }

    function generateWorld() {
      // 地形・水
      for (let x = 0; x < WORLD_SIZE; x++) {
        for (let z = 0; z < WORLD_SIZE; z++) {
          const h = terrainHeight(x, z);
          topY[z * WORLD_SIZE + x] = h;

          for (let y = 0; y <= h; y++) {
            let b = STONE;
            if (y === h) {
              b = (h <= SEA_LEVEL + 1) ? SAND : GRASS;
            } else if (y > h - 4) {
              b = DIRT;
            }
            setBlockData(x, y, z, b);
          }

          for (let y = h + 1; y <= SEA_LEVEL; y++) {
            setBlockData(x, y, z, WATER);
          }
        }
      }

      // 木
      for (let x = 2; x < WORLD_SIZE - 2; x++) {
        for (let z = 2; z < WORLD_SIZE - 2; z++) {
          if (hash2(x * 127, z * 127) < 0.008) {
            placeTree(x, z);
          }
        }
      }
    }

    function placeTree(x, z) {
      const h = topY[z * WORLD_SIZE + x];
      if (h <= SEA_LEVEL + 1) return;
      if (getBlock(x, h, z) !== GRASS) return;

      const treeH = 4 + Math.floor(hash2(x * 5, z * 5) * 3);
      const trunkTop = h + treeH - 1;
      if (trunkTop + 1 >= HEIGHT) return;

      for (let y = h + 1; y <= trunkTop; y++) {
        setBlockData(x, y, z, WOOD);
      }

      for (let dx = -2; dx <= 2; dx++) {
        for (let dz = -2; dz <= 2; dz++) {
          for (let dy = -2; dy <= 1; dy++) {
            const yy = trunkTop + dy;
            const dist2 = dx * dx + dy * dy + dz * dz;
            if (dist2 <= 5 && !(dx === 0 && dz === 0 && dy <= 0)) {
              if (getBlock(x + dx, yy, z + dz) === AIR) {
                setBlockData(x + dx, yy, z + dz, LEAF);
              }
            }
          }
        }
      }
    }

    // ===================================================================
    // ブロックアクセス
    // ===================================================================
    function index3(x, y, z) {
      return (y * WORLD_SIZE + z) * WORLD_SIZE + x;
    }

    function inBounds(x, y, z) {
      return x >= 0 && x < WORLD_SIZE && y >= 0 && y < HEIGHT && z >= 0 && z < WORLD_SIZE;
    }

    function getBlock(x, y, z) {
      if (!inBounds(x, y, z)) return AIR;
      return world[index3(x, y, z)];
    }

    function setBlockData(x, y, z, block) {
      if (!inBounds(x, y, z)) return;
      world[index3(x, y, z)] = block;
    }

    function isSolid(x, y, z) {
      const b = getBlock(x, y, z);
      return b !== AIR && b !== WATER;
    }

    function isTargetable(x, y, z) {
      return getBlock(x, y, z) !== AIR;
    }

    // ===================================================================
    // メッシュ生成
    // ===================================================================
    function chunkIndex(cx, cz) {
      return cx * CHUNKS + cz;
    }

    function addQuad(positions, normals, colors, indices, faceIndex, x, y, z, type) {
      const f = FACES[faceIndex];
      const base = BLOCK_COLORS[type];
      const rnd = hash3(x, y, z);
      const shade = FACE_LIGHT[faceIndex] * (0.85 + rnd * 0.18);

      const r = Math.min(1, base[0] * shade);
      const g = Math.min(1, base[1] * shade);
      const b = Math.min(1, base[2] * shade);

      const start = positions.length / 3;

      for (const v of f.corners) {
        positions.push(x + v[0], y + v[1], z + v[2]);
        normals.push(f.dir[0], f.dir[1], f.dir[2]);
        colors.push(r, g, b);
      }

      indices.push(
        start, start + 1, start + 2,
        start, start + 2, start + 3
      );
    }

    function buildChunk(cx, cz) {
      const c = chunkMeshes[chunkIndex(cx, cz)];

      if (c.opaque) {
        scene.remove(c.opaque);
        c.opaque.geometry.dispose();
        c.opaque = null;
      }

      if (c.water) {
        scene.remove(c.water);
        c.water.geometry.dispose();
        c.water = null;
      }

      const ox = cx * CHUNK_SIZE;
      const oz = cz * CHUNK_SIZE;

      const pos = [];
      const nor = [];
      const col = [];
      const idx = [];

      const wpos = [];
      const wnor = [];
      const wcol = [];
      const widx = [];

      for (let dx = 0; dx < CHUNK_SIZE; dx++) {
        for (let dz = 0; dz < CHUNK_SIZE; dz++) {
          const x = ox + dx;
          const z = oz + dz;

          for (let y = 0; y < HEIGHT; y++) {
            const b = getBlock(x, y, z);
            if (b === AIR) continue;

            for (let fi = 0; fi < 6; fi++) {
              const dir = FACES[fi].dir;
              const nx = x + dir[0];
              const ny = y + dir[1];
              const nz = z + dir[2];
              const nb = getBlock(nx, ny, nz);

              if (b === WATER) {
                if (nb !== AIR) continue;
                addQuad(wpos, wnor, wcol, widx, fi, x, y, z, b);
              } else {
                if (!(nb === AIR || nb === WATER)) continue;
                addQuad(pos, nor, col, idx, fi, x, y, z, b);
              }
            }
          }
        }
      }

      if (pos.length) {
        const g = new THREE.BufferGeometry();
        g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(pos), 3));
        g.setAttribute("normal", new THREE.BufferAttribute(new Float32Array(nor), 3));
        g.setAttribute("color", new THREE.BufferAttribute(new Float32Array(col), 3));
        g.setIndex(new THREE.BufferAttribute(new Uint32Array(idx), 1));
        g.computeBoundingSphere();
        const mesh = new THREE.Mesh(g, opaqueMaterial);
        scene.add(mesh);
        c.opaque = mesh;
      }

      if (wpos.length) {
        const g = new THREE.BufferGeometry();
        g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(wpos), 3));
        g.setAttribute("normal", new THREE.BufferAttribute(new Float32Array(wnor), 3));
        g.setAttribute("color", new THREE.BufferAttribute(new Float32Array(wcol), 3));
        g.setIndex(new THREE.BufferAttribute(new Uint32Array(widx), 1));
        g.computeBoundingSphere();
        const mesh = new THREE.Mesh(g, waterMaterial);
        scene.add(mesh);
        c.water = mesh;
      }
    }

    function buildAllChunks() {
      for (let cx = 0; cx < CHUNKS; cx++) {
        for (let cz = 0; cz < CHUNKS; cz++) {
          buildChunk(cx, cz);
        }
      }
    }

    function rebuildAround(x, z) {
      const cx = Math.floor(x / CHUNK_SIZE);
      const cz = Math.floor(z / CHUNK_SIZE);
      const set = new Set();

      const add = (a, b) => {
        if (a >= 0 && a < CHUNKS && b >= 0 && b < CHUNKS) {
          set.add(`${a}|${b}`);
        }
      };

      const lx = x % CHUNK_SIZE;
      const lz = z % CHUNK_SIZE;

      add(cx, cz);

      if (lx === 0) {
        add(cx - 1, cz);
        add(cx - 1, cz - 1);
        add(cx - 1, cz + 1);
      } else if (lx === CHUNK_SIZE - 1) {
        add(cx + 1, cz);
        add(cx + 1, cz - 1);
        add(cx + 1, cz + 1);
      }

      if (lz === 0) {
        add(cx, cz - 1);
        add(cx - 1, cz - 1);
        add(cx + 1, cz - 1);
      } else if (lz === CHUNK_SIZE - 1) {
        add(cx, cz + 1);
        add(cx - 1, cz + 1);
        add(cx + 1, cz + 1);
      }

      for (const key of set) {
        const parts = key.split("|").map(Number);
        buildChunk(parts[0], parts[1]);
      }
    }

    function modifyBlock(x, y, z, block) {
      if (!inBounds(x, y, z)) return;
      if (getBlock(x, y, z) === block) return;

      setBlockData(x, y, z, block);
      rebuildAround(x, z);
    }

    // ===================================================================
    // プレイヤー
    // ===================================================================
    function findGround(x, z) {
      x = Math.floor(x);
      z = Math.floor(z);
      for (let y = HEIGHT - 1; y >= 0; y--) {
        if (isSolid(x, y, z)) return y;
      }
      return 0;
    }

    function spawnPlayer() {
      player.pos.set(
        WORLD_SIZE / 2 + 0.5,
        findGround(WORLD_SIZE / 2 + 0.5, WORLD_SIZE / 2 + 0.5) + 1,
        WORLD_SIZE / 2 + 0.5
      );
      player.vel.set(0, 0, 0);
      player.onGround = false;
    }

    function boxCollision() {
      const minX = Math.floor(player.pos.x - HALF_W);
      const maxX = Math.floor(player.pos.x + HALF_W);
      const minY = Math.floor(player.pos.y + EPS);
      const maxY = Math.floor(player.pos.y + PLAYER_HEIGHT - EPS);
      const minZ = Math.floor(player.pos.z - HALF_W);
      const maxZ = Math.floor(player.pos.z + HALF_W);

      for (let x = minX; x <= maxX; x++) {
        for (let y = minY; y <= maxY; y++) {
          for (let z = minZ; z <= maxZ; z++) {
            if (isSolid(x, y, z)) return true;
          }
        }
      }
      return false;
    }

    function collideX(delta) {
      if (delta === 0) return;
      player.pos.x += delta;

      if (!boxCollision()) return;

      if (delta > 0) {
        let best = Infinity;
        const x0 = Math.floor(player.pos.x + HALF_W);
        const y0 = Math.floor(player.pos.y + EPS);
        const y1 = Math.floor(player.pos.y + PLAYER_HEIGHT - EPS);
        const z0 = Math.floor(player.pos.z - HALF_W);
        const z1 = Math.floor(player.pos.z + HALF_W);

        for (let y = y0; y <= y1; y++) {
          for (let z = z0; z <= z1; z++) {
            if (isSolid(x0, y, z)) {
              best = Math.min(best, x0 - HALF_W - EPS - player.pos.x);
            }
          }
        }
        if (best !== Infinity) player.pos.x += best;
      } else {
        let best = Infinity;
        const x0 = Math.floor(player.pos.x - HALF_W);
        const y0 = Math.floor(player.pos.y + EPS);
        const y1 = Math.floor(player.pos.y + PLAYER_HEIGHT - EPS);
        const z0 = Math.floor(player.pos.z - HALF_W);
        const z1 = Math.floor(player.pos.z + HALF_W);

        for (let y = y0; y <= y1; y++) {
          for (let z = z0; z <= z1; z++) {
            if (isSolid(x0, y, z)) {
              best = Math.min(best, (x0 + 1) + HALF_W + EPS - player.pos.x);
            }
          }
        }
        if (best !== Infinity) player.pos.x += best;
      }

      if (player.vel.x > 0) player.vel.x = Math.min(0, player.vel.x);
      else if (player.vel.x < 0) player.vel.x = Math.max(0, player.vel.x);
    }

    function collideZ(delta) {
      if (delta === 0) return;
      player.pos.z += delta;

      if (!boxCollision()) return;

      if (delta > 0) {
        let best = Infinity;
        const z0 = Math.floor(player.pos.z + HALF_W);
        const x0 = Math.floor(player.pos.x - HALF_W);
        const x1 = Math.floor(player.pos.x + HALF_W);
        const y0 = Math.floor(player.pos.y + EPS);
        const y1 = Math.floor(player.pos.y + PLAYER_HEIGHT - EPS);

        for (let y = y0; y <= y1; y++) {
          for (let x = x0; x <= x1; x++) {
            if (isSolid(x, y, z0)) {
              best = Math.min(best, z0 - HALF_W - EPS - player.pos.z);
            }
          }
        }
        if (best !== Infinity) player.pos.z += best;
      } else {
        let best = Infinity;
        const z0 = Math.floor(player.pos.z - HALF_W);
        const x0 = Math.floor(player.pos.x - HALF_W);
        const x1 = Math.floor(player.pos.x + HALF_W);
        const y0 = Math.floor(player.pos.y + EPS);
        const y1 = Math.floor(player.pos.y + PLAYER_HEIGHT - EPS);

        for (let y = y0; y <= y1; y++) {
          for (let x = x0; x <= x1; x++) {
            if (isSolid(x, y, z0)) {
              best = Math.min(best, (z0 + 1) + HALF_W + EPS - player.pos.z);
            }
          }
        }
        if (best !== Infinity) player.pos.z += best;
      }

      if (player.vel.z > 0) player.vel.z = Math.min(0, player.vel.z);
      else if (player.vel.z < 0) player.vel.z = Math.max(0, player.vel.z);
    }

    function collideY(delta) {
      if (delta === 0) return;
      player.pos.y += delta;

      if (!boxCollision()) return;

      if (delta > 0) {
        let best = -Infinity;
        const y1 = Math.floor(player.pos.y + PLAYER_HEIGHT - EPS);
        const x0 = Math.floor(player.pos.x - HALF_W);
        const x1 = Math.floor(player.pos.x + HALF_W);
        const z0 = Math.floor(player.pos.z - HALF_W);
        const z1 = Math.floor(player.pos.z + HALF_W);

        for (let x = x0; x <= x1; x++) {
          for (let z = z0; z <= z1; z++) {
            if (isSolid(x, y1, z)) {
              best = Math.max(best, y1 - PLAYER_HEIGHT - EPS - player.pos.y);
            }
          }
        }
        if (best !== -Infinity) player.pos.y += best;
        player.vel.y = 0;
      } else {
        let best = Infinity;
        const y0 = Math.floor(player.pos.y + EPS);
        const x0 = Math.floor(player.pos.x - HALF_W);
        const x1 = Math.floor(player.pos.x + HALF_W);
        const z0 = Math.floor(player.pos.z - HALF_W);
        const z1 = Math.floor(player.pos.z + HALF_W);

        for (let x = x0; x <= x1; x++) {
          for (let z = z0; z <= z1; z++) {
            if (isSolid(x, y0, z)) {
              best = Math.min(best, (y0 + 1) + EPS - player.pos.y);
            }
          }
        }
        if (best !== Infinity) player.pos.y += best;
        player.vel.y = 0;
        player.onGround = true;
      }
    }

    function updatePlayer(dt) {
      // 視点
      camera.position.set(
        player.pos.x,
        player.pos.y + EYE,
        player.pos.z
      );
      camera.rotation.set(player.pitch, player.yaw, 0);

      // 入力
      const forward = new THREE.Vector3();
      camera.getWorldDirection(forward);
      forward.y = 0;
      forward.normalize();

      const right = new THREE.Vector3();
      right.crossVectors(forward, new THREE.Vector3(0, 1, 0)).normalize();

      let inputZ = 0;
      let inputX = 0;

      if (keys["KeyW"]) inputZ += 1;
      if (keys["KeyS"]) inputZ -= 1;
      if (keys["KeyD"]) inputX += 1;
      if (keys["KeyA"]) inputX -= 1;

      const speed = keys["ShiftLeft"] || keys["ShiftRight"] ? 7.5 : 4.6;
      const move = new THREE.Vector3();
      move.addScaledVector(forward, inputZ);
      move.addScaledVector(right, inputX);

      if (move.lengthSq() > 1) move.normalize();

      const targetVx = move.x * speed;
      const targetVz = move.z * speed;

      const accel = player.onGround ? 18 : 6;
      player.vel.x += (targetVx - player.vel.x) * Math.min(1, dt * accel);
      player.vel.z += (targetVz - player.vel.z) * Math.min(1, dt * accel);

      if (player.onGround && keys["Space"]) {
        player.vel.y = 8.6;
        player.onGround = false;
      }

      // 重力
      player.vel.y -= 22 * dt;
      player.vel.y = Math.max(player.vel.y, -30);

      player.onGround = false;

      // 移動
      collideX(player.vel.x * dt);
      collideZ(player.vel.z * dt);
      collideY(player.vel.y * dt);

      // ワールド外落下リセット
      if (player.pos.y < -10) {
        spawnPlayer();
      }
    }

    // ===================================================================
    // レイキャスト
    // ===================================================================
    function raycast(maxDist = 7) {
      const origin = camera.position.clone();
      const dir = camera.getWorldDirection(new THREE.Vector3()).normalize();

      let prevX, prevY, prevZ;
      let first = true;
      const step = 0.05;

      for (let d = 0; d < maxDist; d += step) {
        const x = origin.x + dir.x * d;
        const y = origin.y + dir.y * d;
        const z = origin.z + dir.z * d;

        const bx = Math.floor(x);
        const by = Math.floor(y);
        const bz = Math.floor(z);

        if (first) {
          prevX = bx;
          prevY = by;
          prevZ = bz;
          first = false;
          continue;
        }

        if (bx === prevX && by === prevY && bz === prevZ) continue;

        if (isTargetable(bx, by, bz)) {
          let nx = prevX - bx;
          let ny = prevY - by;
          let nz = prevZ - bz;

          const ax = Math.abs(nx);
          const ay = Math.abs(ny);
          const az = Math.abs(nz);

          if (ax >= ay && ax >= az) { nx = Math.sign(nx); ny = 0; nz = 0; }
          else if (ay >= az) { nx = 0; ny = Math.sign(ny); nz = 0; }
          else { nx = 0; ny = 0; nz = Math.sign(nz); }

          return { x: bx, y: by, z: bz, nx, ny, nz };
        }

        prevX = bx;
        prevY = by;
        prevZ = bz;
      }

      return null;
    }

    function blockOverlapsPlayer(bx, by, bz) {
      const minX = bx;
      const maxX = bx + 1;
      const minY = by;
      const maxY = by + 1;
      const minZ = bz;
      const maxZ = bz + 1;

      const px = player.pos.x;
      const py = player.pos.y;
      const pz = player.pos.z;

      return (
        px + HALF_W > minX &&
        px - HALF_W < maxX &&
        py + PLAYER_HEIGHT > minY &&
        py < maxY &&
        pz + HALF_W > minZ &&
        pz - HALF_W < maxZ
      );
    }

    // ===================================================================
    // ハイライト・マウス操作
    // ===================================================================
    let highlight;

    function initHighlight() {
      const box = new THREE.BoxGeometry(1.002, 1.002, 1.002);
      const edges = new THREE.EdgesGeometry(box);
      highlight = new THREE.LineSegments(
        edges,
        new THREE.LineBasicMaterial({
          color: 0x000000,
          transparent: true,
          opacity: 0.75
        })
      );
      highlight.visible = false;
      scene.add(highlight);
    }

    function updateHighlight() {
      if (!highlight) return;
      const hit = raycast();

      if (hit) {
        highlight.visible = true;
        highlight.position.set(hit.x + 0.5, hit.y + 0.5, hit.z + 0.5);
      } else {
        highlight.visible = false;
      }
    }

    function destroyBlock() {
      const hit = raycast();
      if (!hit) return;
      modifyBlock(hit.x, hit.y, hit.z, AIR);
    }

    function placeBlock() {
      const hit = raycast();
      if (!hit) return;

      const tx = hit.x + hit.nx;
      const ty = hit.y + hit.ny;
      const tz = hit.z + hit.nz;

      if (!inBounds(tx, ty, tz)) return;

      const target = getBlock(tx, ty, tz);
      if (!(target === AIR || target === WATER)) return;

      if (blockOverlapsPlayer(tx, ty, tz)) return;

      modifyBlock(tx, ty, tz, selected);
    }

    // ===================================================================
    // UI
    // ===================================================================
    function setupUI() {
      const hotbar = document.getElementById("hotbar");
      hotbar.innerHTML = "";

      for (let i = 1; i <= 7; i++) {
        const div = document.createElement("div");
        div.className = "slot";
        if (i === selected) div.classList.add("selected");
        div.dataset.key = String(i);
        div.dataset.block = String(i);

        const span = document.createElement("span");
        span.style.background = BLOCK_CSS[i - 1];
        div.appendChild(span);

        div.title = BLOCK_NAMES[i];
        hotbar.appendChild(div);
      }

      updateHotbar();
      initHighlight();
    }

    function updateHotbar() {
      const slots = document.querySelectorAll("#hotbar .slot");
      slots.forEach((slot, i) => {
        slot.classList.toggle("selected", (i + 1) === selected);
      });
    }

    function selectBlock(n) {
      if (n < 1 || n > 7) return;
      selected = n;
      updateHotbar();
    }

    // ===================================================================
    // 入力
    // ===================================================================
    function setupInput() {
      document.addEventListener("keydown", (e) => {
        keys[e.code] = true;

        if (e.code.startsWith("Digit")) {
          selectBlock(parseInt(e.code.slice(5), 10));
          e.preventDefault();
        }

        if (e.code === "Space") e.preventDefault();
      });

      document.addEventListener("keyup", (e) => {
        keys[e.code] = false;
      });

      const canvas = renderer.domElement;

      canvas.addEventListener("click", () => {
        if (!document.pointerLockElement) {
          canvas.requestPointerLock();
        }
      });

      document.addEventListener("pointerlockchange", () => {
        locked = !!document.pointerLockElement;
        document.body.style.cursor = locked ? "none" : "default";
      });

      document.addEventListener("mousemove", (e) => {
        if (!locked) return;

        const sens = 0.0022;
        player.yaw -= e.movementX * sens;
        player.pitch -= e.movementY * sens;

        const limit = Math.PI / 2 - 0.02;
        player.pitch = Math.max(-limit, Math.min(limit, player.pitch));
      });

      document.addEventListener("mousedown", (e) => {
        if (!locked) return;
        if (e.button === 0) destroyBlock();
        if (e.button === 2) placeBlock();
      });

      document.addEventListener("contextmenu", (e) => {
        e.preventDefault();
      });

      window.addEventListener("wheel", (e) => {
        if (!locked) return;
        const dir = e.deltaY > 0 ? 1 : -1;
        let next = selected + dir;
        if (next < 1) next = 7;
        if (next > 7) next = 1;
        selectBlock(next);
      });
    }

    // ===================================================================
    // 昼夜
    // ===================================================================
    function updateDayNight(dt) {
      time += dt;
      const dayLength = 240;
      const angle = (time / dayLength) * Math.PI * 2 - Math.PI / 2;
      const factor = (Math.sin(angle) + 1) * 0.5;

      skyColor.copy(nightColor).lerp(dayColor, factor);
      scene.background.copy(skyColor);
      scene.fog.color.copy(skyColor);
    }

    // ===================================================================
    // 表示ループ
    // ===================================================================
    let lastTime = performance.now();

    function animate() {
      requestAnimationFrame(animate);

      const now = performance.now();
      const dt = Math.min(0.05, (now - lastTime) / 1000);
      lastTime = now;

      updatePlayer(dt);
      updateHighlight();
      updateDayNight(dt);

      renderer.render(scene, camera);
    }
  </script>
</body>
</html>
```

このコードは「完全に動くことを確認するためにはブラウザで実行する必要はある」ものの、基本的な 3D ボクセルゲームとしてはかなり遊べる状態を狙っています。

追加したくなる機能があれば、次はこういう拡張がおすすめです。

1. **ブロックのテクスチャ化**  
   現在は無地の色ですが、`canvas` で 16x16 のピクセルテクスチャを作って貼ると、よりマイクラ感が出ます。

2. **チャンク分割の高度化**  
   64x64x32 なので今でも十分動きますが、さらに大きくするならチャンク読み込み/解放が必要です。

3. **木・葉・水の見え方の改善**  
   葉を「半透過」、水を「揺れる水」にすると見た目が一気に上がります。

4. **インベントリ / チェスト / 台帳風UI**  
   今風にするなら `div` のインベントリと、右クリックメニューを合わせると面白いです。

5. **マルチプレイ対応**  
   WebSocket + Node.js で同期できます。