できます。「マイクラ風」という方向で、**壊せる・置ける・自由に歩ける3Dボクセル箱庭**を作ります。  
以下のコードを **`index.html`** に保存してブラウザで開くだけで遊べます。PC推奨です。

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>ボクセル箱庭</title>
  <style>
    html, body {
      margin: 0;
      height: 100%;
      overflow: hidden;
      background: #87ceeb;
      font-family: system-ui, sans-serif;
      user-select: none;
    }
    canvas { display: block; }

    #hud {
      position: fixed;
      left: 50%;
      bottom: 18px;
      transform: translateX(-50%);
      display: flex;
      gap: 6px;
      z-index: 10;
    }

    .slot {
      width: 46px;
      height: 46px;
      border: 2px solid #222;
      border-radius: 10px;
      box-shadow: 0 4px 10px rgba(0,0,0,.25);
      position: relative;
      cursor: pointer;
    }

    .slot span {
      position: absolute;
      left: 5px;
      top: 4px;
      font-size: 11px;
      font-weight: 700;
      color: #fff;
      text-shadow: 0 1px 2px #000;
    }

    .slot.selected {
      border-color: #fff;
      transform: scale(1.12);
    }

    #info {
      position: fixed;
      left: 12px;
      top: 12px;
      z-index: 10;
      color: #fff;
      background: rgba(0,0,0,.45);
      padding: 10px 14px;
      border-radius: 12px;
      font-size: 12px;
      line-height: 1.6;
      pointer-events: none;
    }

    #crosshair {
      position: fixed;
      left: 50%;
      top: 50%;
      width: 5px;
      height: 5px;
      transform: translate(-50%, -50%);
      background: #fff;
      border-radius: 50%;
      opacity: .85;
      z-index: 10;
      pointer-events: none;
    }

    #overlay {
      position: fixed;
      inset: 0;
      z-index: 20;
      display: flex;
      align-items: center;
      justify-content: center;
      background: rgba(0,0,0,.58);
      color: #fff;
      text-align: center;
      cursor: pointer;
    }

    #overlay h1 {
      margin: 0 0 12px;
      font-size: 42px;
      letter-spacing: .04em;
    }

    #overlay p {
      margin: 6px 0;
      font-size: 14px;
      opacity: .95;
    }
  </style>
</head>
<body>
  <div id="overlay">
    <div>
      <h1>ボクセル箱庭</h1>
      <p>クリックして開始</p>
      <p>WASD 移動 / Space ジャンプ / 左クリック 壊す / 右クリック 置く</p>
      <p>1〜6 または マウスホイール でブロック選択</p>
    </div>
  </div>

  <div id="crosshair"></div>

  <div id="info">
    <div><b>ボクセル箱庭</b></div>
    <div>クリックでマウスロック</div>
    <div>WASD 移動 / Space ジャンプ</div>
    <div>左クリック 破壊 / 右クリック 設置</div>
    <div>1〜6 または ホイール でブロック選択</div>
    <div>Esc でロック解除</div>
  </div>

  <div id="hud"></div>

  <script type="importmap">
  {
    "imports": {
      "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js"
    }
  }
  </script>

  <script type="module">
    import * as THREE from "three";

    // -----------------------------------
    // 世界定義
    // -----------------------------------
    const WORLD_X = 64;
    const WORLD_Y = 32;
    const WORLD_Z = 64;
    const CHUNK = 16;

    const AIR = 0;
    const GRASS = 1;
    const DIRT = 2;
    const STONE = 3;
    const SAND = 4;
    const WOOD = 5;
    const LEAVES = 6;

    const PALETTE = [GRASS, DIRT, STONE, SAND, WOOD, LEAVES];
    const NAMES = ["", "草", "土", "石", "砂", "木", "葉"];

    const BLOCK_HEX = {
      [GRASS]: 0x59c13f,
      [DIRT]: 0x7d5a3a,
      [STONE]: 0x8f8f8f,
      [SAND]: 0xd8c07d,
      [WOOD]: 0x8b5e34,
      [LEAVES]: 0x3e7f36
    };

    const blocks = new Uint8Array(WORLD_X * WORLD_Y * WORLD_Z);

    function idx(x, y, z) {
      return (x * WORLD_Y + y) * WORLD_Z + z;
    }

    function inWorld(x, y, z) {
      return x >= 0 && y >= 0 && z >= 0 &&
             x < WORLD_X && y < WORLD_Y && z < WORLD_Z;
    }

    function getBlock(x, y, z) {
      if (!inWorld(x, y, z)) return AIR;
      return blocks[idx(x, y, z)];
    }

    function setBlockRaw(x, y, z, type) {
      if (!inWorld(x, y, z)) return false;
      blocks[idx(x, y, z)] = type;
      return true;
    }

    function safeSet(x, y, z, type) {
      if (inWorld(x, y, z) && getBlock(x, y, z) === AIR) {
        blocks[idx(x, y, z)] = type;
      }
    }

    // -----------------------------------
    // 雑な地形生成用ノイズ
    // -----------------------------------
    function hash2(x, z) {
      let h = (Math.imul(x, 374761393) + Math.imul(z, 668265263)) | 0;
      h ^= h >>> 13;
      h = Math.imul(h, 1274126177);
      h ^= h >>> 16;
      return (h >>> 0) / 4294967296;
    }

    function smooth(t) {
      return t * t * (3 - 2 * t);
    }

    function valueNoise(x, z) {
      const ix = Math.floor(x);
      const iz = Math.floor(z);
      const tx = x - ix;
      const tz = z - iz;

      const sx = smooth(tx);
      const sz = smooth(tz);

      const a = hash2(ix, iz);
      const b = hash2(ix + 1, iz);
      const c = hash2(ix, iz + 1);
      const d = hash2(ix + 1, iz + 1);

      const ab = a + (b - a) * sx;
      const cd = c + (d - c) * sx;
      return ab + (cd - ab) * sz;
    }

    function terrainHeight(x, z) {
      const n1 = valueNoise(x * 0.030 + 12.3, z * 0.030 + 7.7);
      const n2 = valueNoise(x * 0.090 + 50.1, z * 0.090 + 90.2);
      const h = Math.floor(4 + n1 * 16 + n2 * 5);
      return Math.max(1, Math.min(25, h));
    }

    function generateWorld() {
      // 地面
      for (let x = 0; x < WORLD_X; x++) {
        for (let z = 0; z < WORLD_Z; z++) {
          const h = terrainHeight(x, z);
          for (let y = 0; y <= h; y++) {
            let b = STONE;
            if (y > h - 3) b = DIRT;
            if (y === h) b = h < 8 ? SAND : GRASS;
            blocks[idx(x, y, z)] = b;
          }
        }
      }

      // 木を少し
      for (let x = 3; x < WORLD_X - 3; x++) {
        for (let z = 3; z < WORLD_Z - 3; z++) {
          const r = hash2(x + 91, z + 57);
          if (r <= 0.99) continue;

          const h = terrainHeight(x, z);
          if (getBlock(x, h, z) !== GRASS) continue;

          const treeH = 3 + Math.floor(hash2(x + 3, z + 7) * 2);

          for (let y = h + 1; y <= h + treeH; y++) {
            setBlockRaw(x, y, z, WOOD);
          }

          const top = h + treeH;

          // 葉：少し大きめの層
          for (let dx = -2; dx <= 2; dx++) {
            for (let dz = -2; dz <= 2; dz++) {
              if (Math.abs(dx) + Math.abs(dz) <= 2) {
                safeSet(x + dx, top - 1, z + dz, LEAVES);
              }
            }
          }

          // 葉：上層
          for (let dx = -1; dx <= 1; dx++) {
            for (let dz = -1; dz <= 1; dz++) {
              if (Math.abs(dx) + Math.abs(dz) <= 1) {
                safeSet(x + dx, top, z + dz, LEAVES);
                safeSet(x + dx, top + 1, z + dz, LEAVES);
              }
            }
          }
        }
      }
    }

    // -----------------------------------
    // 描画まわり
    // -----------------------------------
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x87ceeb);
    scene.fog = new THREE.Fog(0x87ceeb, 45, 160);

    const camera = new THREE.PerspectiveCamera(
      75,
      window.innerWidth / window.innerHeight,
      0.08,
      400
    );
    camera.rotation.order = "YXZ";

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    window.addEventListener("resize", () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    });

    // 面の向き： +X, -X, +Y, -Y, +Z, -Z
    const faceDefs = [
      { d: [ 1, 0, 0], v: [[1,0,1],[1,0,0],[1,1,0],[1,1,1]] },
      { d: [-1, 0, 0], v: [[0,0,0],[0,0,1],[0,1,1],[0,1,0]] },
      { d: [ 0, 1, 0], v: [[0,1,1],[1,1,1],[1,1,0],[0,1,0]] },
      { d: [ 0,-1, 0], v: [[0,0,0],[1,0,0],[1,0,1],[0,0,1]] },
      { d: [ 0, 0, 1], v: [[0,0,1],[1,0,1],[1,1,1],[0,1,1]] },
      { d: [ 0, 0,-1], v: [[1,0,0],[0,0,0],[0,1,0],[1,1,0]] }
    ];

    const faceShade = [0.82, 0.82, 1.0, 0.55, 0.92, 0.70];

    const BASE_COLORS = {
      [GRASS]: [0x7bb661, 0x7bb661, 0x59c13f, 0x7d5a3a, 0x7bb661, 0x7bb661],
      [DIRT]: [0x7d5a3a, 0x7d5a3a, 0x7d5a3a, 0x7d5a3a, 0x7d5a3a, 0x7d5a3a],
      [STONE]: [0x8f8f8f, 0x8f8f8f, 0x8f8f8f, 0x8f8f8f, 0x8f8f8f, 0x8f8f8f],
      [SAND]: [0xd8c07d, 0xd8c07d, 0xd8c07d, 0xd8c07d, 0xd8c07d, 0xd8c07d],
      [WOOD]: [0x6d4a2c, 0x6d4a2c, 0xa6743f, 0xa6743f, 0x6d4a2c, 0x6d4a2c],
      [LEAVES]: [0x3e7f36, 0x3e7f36, 0x3e7f36, 0x3e7f36, 0x3e7f36, 0x3e7f36]
    };

    const faceColor = Array(7).fill(null).map(() => new Array(6));
    for (let t = 1; t <= 6; t++) {
      for (let f = 0; f < 6; f++) {
        faceColor[t][f] =
          new THREE.Color(BASE_COLORS[t][f]).multiplyScalar(faceShade[f]);
      }
    }

    const TRI = [0, 1, 2, 0, 2, 3];

    function addFace(x, y, z, type, face, positions, colors) {
      const def = faceDefs[face];
      const c = faceColor[type][face];

      for (const i of TRI) {
        const v = def.v[i];
        positions.push(x + v[0], y + v[1], z + v[2]);
        colors.push(c.r, c.g, c.b);
      }
    }

    const chunks = new Map();

    function chunkKey(cx, cz) {
      return `${cx},${cz}`;
    }

    function buildChunk(cx, cz) {
      if (cx < 0 || cz < 0) return;
      if (cx * CHUNK >= WORLD_X || cz * CHUNK >= WORLD_Z) return;

      const key = chunkKey(cx, cz);
      let mesh = chunks.get(key);

      if (mesh) {
        mesh.geometry.dispose();
        mesh.geometry = new THREE.BufferGeometry();
      } else {
        mesh = new THREE.Mesh(
          new THREE.BufferGeometry(),
          new THREE.MeshBasicMaterial({
            vertexColors: true,
            side: THREE.DoubleSide,
            fog: true
          })
        );
        scene.add(mesh);
        chunks.set(key, mesh);
      }

      const positions = [];
      const colors = [];

      const x0 = cx * CHUNK;
      const x1 = Math.min(WORLD_X, x0 + CHUNK);
      const z0 = cz * CHUNK;
      const z1 = Math.min(WORLD_Z, z0 + CHUNK);

      for (let x = x0; x < x1; x++) {
        for (let z = z0; z < z1; z++) {
          for (let y = 0; y < WORLD_Y; y++) {
            const t = blocks[idx(x, y, z)];
            if (!t) continue;

            for (let f = 0; f < 6; f++) {
              const d = faceDefs[f].d;
              const n = getBlock(x + d[0], y + d[1], z + d[2]);

              // 隣が空気なら面を出す
              if (n === AIR) {
                addFace(x, y, z, t, f, positions, colors);
              }
            }
          }
        }
      }

      mesh.geometry.setAttribute(
        "position",
        new THREE.Float32BufferAttribute(positions, 3)
      );
      mesh.geometry.setAttribute(
        "color",
        new THREE.Float32BufferAttribute(colors, 3)
      );
      mesh.geometry.computeBoundingSphere();
    }

    function rebuildAround(x, z) {
      const targets = new Set();

      const cx = Math.floor(x / CHUNK);
      const cz = Math.floor(z / CHUNK);

      targets.add(chunkKey(cx, cz));

      if (x % CHUNK === 0) targets.add(chunkKey(cx - 1, cz));
      if (x % CHUNK === CHUNK - 1) targets.add(chunkKey(cx + 1, cz));
      if (z % CHUNK === 0) targets.add(chunkKey(cx, cz - 1));
      if (z % CHUNK === CHUNK - 1) targets.add(chunkKey(cx, cz + 1));

      for (const key of targets) {
        const [cx2, cz2] = key.split(",").map(Number);
        buildChunk(cx2, cz2);
      }
    }

    function buildAllChunks() {
      for (let cx = 0; cx < WORLD_X / CHUNK; cx++) {
        for (let cz = 0; cz < WORLD_Z / CHUNK; cz++) {
          buildChunk(cx, cz);
        }
      }
    }

    // -----------------------------------
    // 対象ブロック表示
    // -----------------------------------
    const highlight = new THREE.LineSegments(
      new THREE.EdgesGeometry(new THREE.BoxGeometry(1, 1, 1)),
      new THREE.LineBasicMaterial({ color: 0x111111, transparent: true, opacity: 0.7 })
    );
    highlight.visible = false;
    scene.add(highlight);

    // -----------------------------------
    // プレイヤー
    // -----------------------------------
    const player = {
      pos: new THREE.Vector3(),
      vel: new THREE.Vector3(),
      width: 0.6,
      height: 1.8,
      eye: 1.62,
      onGround: false
    };

    function findGround(x, z) {
      const bx = Math.floor(x);
      const bz = Math.floor(z);
      for (let y = WORLD_Y - 1; y >= 0; y--) {
        if (getBlock(bx, y, bz) !== AIR) return y + 1;
      }
      return WORLD_Y - 1;
    }

    const spawnX = Math.floor(WORLD_X / 2);
    const spawnZ = Math.floor(WORLD_Z / 2);
    player.pos.set(spawnX + 0.5, findGround(spawnX, spawnZ) + 0.01, spawnZ + 0.5);

    function isSolidAt(x, y, z) {
      if (y < 0) return true;
      if (x < 0 || z < 0 || x >= WORLD_X || z >= WORLD_Z) return true;
      if (y >= WORLD_Y) return false;
      return blocks[idx(x, y, z)] !== AIR;
    }

    function collides(x, y, z) {
      const half = player.width / 2;
      const eps = 0.001;

      const minX = Math.floor(x - half + eps);
      const maxX = Math.floor(x + half - eps);
      const minY = Math.floor(y + eps);
      const maxY = Math.floor(y + player.height - eps);
      const minZ = Math.floor(z - half + eps);
      const maxZ = Math.floor(z + half - eps);

      for (let bx = minX; bx <= maxX; bx++) {
        for (let by = minY; by <= maxY; by++) {
          for (let bz = minZ; bz <= maxZ; bz++) {
            if (isSolidAt(bx, by, bz)) return true;
          }
        }
      }
      return false;
    }

    function moveAxis(axis, delta) {
      if (delta === 0) return;

      player.pos[axis] += delta;

      if (!collides(player.pos.x, player.pos.y, player.pos.z)) {
        return;
      }

      const half = player.width / 2;
      const eps = 0.001;

      if (axis === "x") {
        if (delta > 0) {
          const right = player.pos.x + half;
          const block = Math.floor(right + eps);
          player.pos.x = block - half - eps;
        } else {
          const left = player.pos.x - half;
          const block = Math.floor(left - eps);
          player.pos.x = block + 1 + half + eps;
        }
        player.vel.x = 0;
      }

      if (axis === "z") {
        if (delta > 0) {
          const front = player.pos.z + half;
          const block = Math.floor(front + eps);
          player.pos.z = block - half - eps;
        } else {
          const back = player.pos.z - half;
          const block = Math.floor(back - eps);
          player.pos.z = block + 1 + half + eps;
        }
        player.vel.z = 0;
      }

      if (axis === "y") {
        if (delta > 0) {
          const top = player.pos.y + player.height;
          const block = Math.floor(top + eps);
          player.pos.y = block - player.height - eps;
          player.vel.y = 0;
        } else {
          const bottom = player.pos.y;
          const block = Math.floor(bottom - eps);
          player.pos.y = block + 1 + eps;
          player.vel.y = 0;
          player.onGround = true;
        }
      }
    }

    // -----------------------------------
    // 入力
    // -----------------------------------
    const keys = {};
    let yaw = 0;
    let pitch = -0.22;
    let locked = false;
    let currentBlock = GRASS;

    const overlay = document.getElementById("overlay");
    const hud = document.getElementById("hud");

    function updateHotbar() {
      hud.innerHTML = "";

      PALETTE.forEach((b, i) => {
        const div = document.createElement("div");
        div.className = "slot" + (currentBlock === b ? " selected" : "");
        div.style.background = "#" + BLOCK_HEX[b].toString(16).padStart(6, "0");

        const span = document.createElement("span");
        span.textContent = i + 1;
        div.appendChild(span);

        div.title = NAMES[b];

        div.addEventListener("click", () => {
          currentBlock = b;
          updateHotbar();
        });

        hud.appendChild(div);
      });
    }

    overlay.addEventListener("click", () => {
      renderer.domElement.requestPointerLock();
    });

    document.addEventListener("pointerlockchange", () => {
      locked = document.pointerLockElement === renderer.domElement;
      overlay.style.display = locked ? "none" : "flex";
    });

    document.addEventListener("mousemove", (e) => {
      if (!locked) return;

      const sensitivity = 0.0022;
      yaw -= e.movementX * sensitivity;
      pitch -= e.movementY * sensitivity;
      pitch = Math.max(-1.55, Math.min(1.55, pitch));
    });

    document.addEventListener("contextmenu", e => e.preventDefault());

    document.addEventListener("mousedown", (e) => {
      if (!locked) {
        renderer.domElement.requestPointerLock();
        return;
      }

      if (e.button === 0) {
        breakBlock();
      } else if (e.button === 2) {
        placeBlock();
      }
    });

    document.addEventListener("wheel", (e) => {
      if (!locked) return;

      const i = PALETTE.indexOf(currentBlock);
      const next =
        PALETTE[
          (i + (e.deltaY > 0 ? 1 : -1) + PALETTE.length) % PALETTE.length
        ];
      currentBlock = next;
      updateHotbar();
    }, { passive: false });

    window.addEventListener("keydown", (e) => {
      keys[e.key.toLowerCase()] = true;

      if (e.key === " ") {
        e.preventDefault();
      }

      const num = Number(e.key);
      if (num >= 1 && num <= PALETTE.length) {
        currentBlock = PALETTE[num - 1];
        updateHotbar();
      }
    });

    window.addEventListener("keyup", (e) => {
      keys[e.key.toLowerCase()] = false;
    });

    // -----------------------------------
    // ブロック選択
    // -----------------------------------
    function blockIntersectsPlayer(bx, by, bz) {
      const half = player.width / 2;

      return (
        bx < player.pos.x + half &&
        bx + 1 > player.pos.x - half &&
        by < player.pos.y + player.height &&
        by + 1 > player.pos.y &&
        bz < player.pos.z + half &&
        bz + 1 > player.pos.z - half
      );
    }

    function breakBlock() {
      const hit = raycastVoxel(8);
      if (!hit) return;

      if (hit.y <= 0) return; // 底面は壊さない
      if (getBlock(hit.x, hit.y, hit.z) === AIR) return;

      setBlockRaw(hit.x, hit.y, hit.z, AIR);
      rebuildAround(hit.x, hit.z);
    }

    function placeBlock() {
      const hit = raycastVoxel(8);
      if (!hit) return;

      const x = hit.x + hit.nx;
      const y = hit.y + hit.ny;
      const z = hit.z + hit.nz;

      if (!inWorld(x, y, z)) return;
      if (getBlock(x, y, z) !== AIR) return;
      if (blockIntersectsPlayer(x, y, z)) return;

      setBlockRaw(x, y, z, currentBlock);
      rebuildAround(x, z);
    }

    // -----------------------------------
    // ボクセルへレイキャスト
    // -----------------------------------
    const rayDir = new THREE.Vector3();

    function raycastVoxel(maxDist = 8) {
      camera.getWorldDirection(rayDir);
      rayDir.normalize();

      let x = Math.floor(camera.position.x);
      let y = Math.floor(camera.position.y);
      let z = Math.floor(camera.position.z);

      const dx = rayDir.x;
      const dy = rayDir.y;
      const dz = rayDir.z;

      const stepX = dx > 0 ? 1 : -1;
      const stepY = dy > 0 ? 1 : -1;
      const stepZ = dz > 0 ? 1 : -1;

      const tDeltaX = dx !== 0 ? Math.abs(1 / dx) : Infinity;
      const tDeltaY = dy !== 0 ? Math.abs(1 / dy) : Infinity;
      const tDeltaZ = dz !== 0 ? Math.abs(1 / dz) : Infinity;

      let tMaxX = dx !== 0 ? ((stepX > 0 ? x + 1 : x) - camera.position.x) / dx : Infinity;
      let tMaxY = dy !== 0 ? ((stepY > 0 ? y + 1 : y) - camera.position.y) / dy : Infinity;
      let tMaxZ = dz !== 0 ? ((stepZ > 0 ? z + 1 : z) - camera.position.z) / dz : Infinity;

      let nx = 0, ny = 0, nz = 0;

      for (let i = 0; i < 80; i++) {
        if (tMaxX < tMaxY && tMaxX < tMaxZ) {
          if (tMaxX > maxDist) break;
          x += stepX;
          tMaxX += tDeltaX;
          nx = -stepX; ny = 0; nz = 0;
        } else if (tMaxY < tMaxZ) {
          if (tMaxY > maxDist) break;
          y += stepY;
          tMaxY += tDeltaY;
          nx = 0; ny = -stepY; nz = 0;
        } else {
          if (tMaxZ > maxDist) break;
          z += stepZ;
          tMaxZ += tDeltaZ;
          nx = 0; ny = 0; nz = -stepZ;
        }

        const b = getBlock(x, y, z);
        if (b !== AIR) {
          return { x, y, z, nx, ny, nz, block: b };
        }
      }

      return null;
    }

    // -----------------------------------
    // 毎フレーム更新
    // -----------------------------------
    function updatePlayer(dt) {
      const moveSpeed = 5.0;
      const jumpPower = 8.5;

      const forward = new THREE.Vector3(
        -Math.sin(yaw),
        0,
        -Math.cos(yaw)
      ).normalize();

      const right = new THREE.Vector3(
        Math.cos(yaw),
        0,
        -Math.sin(yaw)
      ).normalize();

      const wish = new THREE.Vector3();

      if (keys["w"]) wish.add(forward);
      if (keys["s"]) wish.sub(forward);
      if (keys["d"]) wish.add(right);
      if (keys["a"]) wish.sub(right);

      if (wish.lengthSq() > 0) wish.normalize();

      player.vel.x = wish.x * moveSpeed;
      player.vel.z = wish.z * moveSpeed;

      player.vel.y -= 24 * dt;
      player.vel.y = Math.max(player.vel.y, -60);

      if (keys[" "] && player.onGround) {
        player.vel.y = jumpPower;
        player.onGround = false;
      }

      player.onGround = false;

      moveAxis("x", player.vel.x * dt);
      moveAxis("z", player.vel.z * dt);
      moveAxis("y", player.vel.y * dt);

      camera.position.set(
        player.pos.x,
        player.pos.y + player.eye,
        player.pos.z
      );

      camera.rotation.set(pitch, yaw, 0, "YXZ");

      const hit = raycastVoxel(8);
      if (hit) {
        highlight.position.set(hit.x + 0.5, hit.y + 0.5, hit.z + 0.5);
        highlight.visible = true;
      } else {
        highlight.visible = false;
      }
    }

    // -----------------------------------
    // 初期化 & ループ
    // -----------------------------------
    generateWorld();
    buildAllChunks();
    updateHotbar();

    let last = performance.now();

    function animate(now) {
      requestAnimationFrame(animate);

      const dt = Math.min((now - last) / 1000, 0.05);
      last = now;

      if (locked) {
        updatePlayer(dt);
      } else {
        // ロック中以外も視点は更新しておく
        camera.position.set(
          player.pos.x,
          player.pos.y + player.eye,
          player.pos.z
        );
        camera.rotation.set(pitch, yaw, 0, "YXZ");
      }

      renderer.render(scene, camera);
    }

    requestAnimationFrame(animate);
  </script>
</body>
</html>
```

## 遊び方
- クリックして開始  
- **WASD** 移動  
- **Space** ジャンプ  
- **左クリック** ブロック破壊  
- **右クリック** ブロック設置  
- **1〜6** または **マウスホイール** でブロック選択  
- **Esc** でマウスロック解除  

## いま入っているもの
- 3Dボクセル地形
- 木
- 草・土・石・砂・木・葉の6ブロック
- 簡易物理 / 衝突判定
- ブロックの置き壊し

次のステップで拡張するなら、  
- **水**  
- **洞窟**  
- **昼夜**  
- **アイテムインベントリ**  
- **セーブ/ロード**  
- **モバイル操作**  
が入れやすいです。