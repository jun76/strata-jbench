了解しました。ブラウザだけで動く「マイクラ風 3D 箱庭ゲーム」を 1 ファイル HTML で作ります。  
下のコードを `minecraft-style.html` みたいな名前で保存して開くだけで遊べます。

特徴:

- 3D ボクセル地形生成
- 1人称視点
- WASD 移動 / Space ジャンプ
- マウス視点
- 左クリックでブロック破壊
- 右クリックでブロック設置
- 1〜7 / ホイールでブロック選択
- F で飛行モード切替
- 木生成あり
- Three.js 使用、外部アセットなし

---

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Microcraft - 3D箱庭</title>
  <style>
    html, body {
      margin: 0;
      height: 100%;
      overflow: hidden;
      background: #87ceeb;
      font-family: system-ui, -apple-system, sans-serif;
    }

    #app {
      position: fixed;
      inset: 0;
    }

    canvas {
      display: block;
    }

    #hud {
      position: fixed;
      inset: 0;
      pointer-events: none;
      color: #fff;
    }

    #info {
      position: absolute;
      top: 12px;
      left: 12px;
      background: rgba(0, 0, 0, 0.45);
      padding: 10px 12px;
      border-radius: 10px;
      font-size: 13px;
      line-height: 1.55;
      max-width: 320px;
    }

    #status {
      margin-top: 6px;
      font-weight: 700;
      color: #fff;
    }

    #crosshair {
      position: absolute;
      left: 50%;
      top: 50%;
      transform: translate(-50%, -50%);
      width: 22px;
      height: 22px;
      opacity: 0.8;
    }

    #crosshair::before,
    #crosshair::after {
      content: "";
      position: absolute;
      background: #fff;
      box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.55);
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
      bottom: 14px;
      left: 50%;
      transform: translateX(-50%);
      display: flex;
      gap: 5px;
    }

    .slot {
      position: relative;
      width: 46px;
      height: 46px;
      border: 2px solid rgba(255, 255, 255, 0.45);
      border-radius: 6px;
      background: rgba(0, 0, 0, 0.35);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-direction: column;
      gap: 2px;
      transition: transform 0.12s, box-shadow 0.12s;
    }

    .slot.active {
      border-color: #fff;
      box-shadow: 0 0 14px rgba(255, 255, 255, 0.35);
      transform: translateY(-3px);
    }

    .slot .swatch {
      width: 24px;
      height: 24px;
      border-radius: 3px;
      box-shadow:
        inset -4px -4px 0 rgba(0, 0, 0, 0.18),
        inset 4px 4px 0 rgba(255, 255, 255, 0.16);
    }

    .slot .num {
      font-size: 10px;
      opacity: 0.85;
    }

    #lockHint {
      position: absolute;
      left: 50%;
      top: 58%;
      transform: translate(-50%, 110px);
      font-size: 15px;
      background: rgba(0, 0, 0, 0.6);
      padding: 10px 16px;
      border-radius: 10px;
    }
  </style>
</head>
<body>
  <div id="app"></div>

  <div id="hud">
    <div id="info">
      <strong>マイクラ風 3D 箱庭</strong><br>
      WASD: 移動<br>
      Space: ジャンプ / 飛行時は上昇<br>
      Shift: 飛行時に下降<br>
      F: 飛行モード ON/OFF<br>
      左クリック: ブロック破壊<br>
      右クリック: ブロック設置<br>
      1〜7 / マウスホイール: ブロック選択<br>
      Esc: ポインタロック解除
      <div id="status"></div>
    </div>

    <div id="crosshair"></div>
    <div id="hotbar"></div>
    <div id="lockHint">クリックしてマウスをロック</div>
  </div>

  <script type="module">
    import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js";

    // --------------------------------------------------
    // 定数・ブロック定義
    // --------------------------------------------------

    const WORLD_X = 64;
    const WORLD_Y = 40;
    const WORLD_Z = 64;
    const CHUNK_SIZE = 16;
    const CHUNKS_X = WORLD_X / CHUNK_SIZE;
    const CHUNKS_Z = WORLD_Z / CHUNK_SIZE;

    const BLOCK_NAMES = [
      null,
      "草",
      "土",
      "石",
      "原木",
      "葉",
      "砂",
      "板"
    ];

    const BLOCK_COLORS = [
      null,
      // 1 草
      { top: 0x5fb34d, bottom: 0x754f2f, side: 0x85603a },
      // 2 土
      { top: 0x8b5a2b, bottom: 0x744a23, side: 0x8b5a2b },
      // 3 石
      { top: 0x9c9c9c, bottom: 0x727272, side: 0x888888 },
      // 4 原木
      { top: 0xa77c53, bottom: 0x7e5a3a, side: 0x8f6742 },
      // 5 葉
      { top: 0x55a54a, bottom: 0x3f7f39, side: 0x4d9443 },
      // 6 砂
      { top: 0xe2d29c, bottom: 0xc8b375, side: 0xd7c68f },
      // 7 板
      { top: 0xd6a85c, bottom: 0xa87a3b, side: 0xc18f4e }
    ];

    const BLOCK_COUNT = BLOCK_NAMES.length - 1;

    const FACES = [
      // +X
      {
        dir: [1, 0, 0],
        corners: [
          [1, 0, 0],
          [1, 0, 1],
          [1, 1, 1],
          [1, 1, 0]
        ]
      },
      // -X
      {
        dir: [-1, 0, 0],
        corners: [
          [0, 0, 1],
          [0, 0, 0],
          [0, 1, 0],
          [0, 1, 1]
        ]
      },
      // +Y top
      {
        dir: [0, 1, 0],
        corners: [
          [0, 1, 0],
          [1, 1, 0],
          [1, 1, 1],
          [0, 1, 1]
        ]
      },
      // -Y bottom
      {
        dir: [0, -1, 0],
        corners: [
          [0, 0, 1],
          [1, 0, 1],
          [1, 0, 0],
          [0, 0, 0]
        ]
      },
      // +Z
      {
        dir: [0, 0, 1],
        corners: [
          [0, 0, 1],
          [1, 0, 1],
          [1, 1, 1],
          [0, 1, 1]
        ]
      },
      // -Z
      {
        dir: [0, 0, -1],
        corners: [
          [1, 0, 0],
          [0, 0, 0],
          [0, 1, 0],
          [1, 1, 0]
        ]
      }
    ];

    // --------------------------------------------------
    // ワールドデータ
    // --------------------------------------------------

    const worldData = new Uint8Array(WORLD_X * WORLD_Y * WORLD_Z);

    function index(x, y, z) {
      return x + z * WORLD_X + y * WORLD_X * WORLD_Z;
    }

    function inWorld(x, y, z) {
      return x >= 0 && x < WORLD_X && y >= 0 && y < WORLD_Y && z >= 0 && z < WORLD_Z;
    }

    function getRaw(x, y, z) {
      if (!inWorld(x, y, z)) return 0;
      return worldData[index(x, y, z)];
    }

    function setRaw(x, y, z, id) {
      if (!inWorld(x, y, z)) return;
      worldData[index(x, y, z)] = id;
    }

    function getBlock(x, y, z) {
      if (y < 0) return 1;
      if (y >= WORLD_Y) return 0;
      if (x < 0 || x >= WORLD_X || z < 0 || z >= WORLD_Z) return 0;
      return worldData[index(x, y, z)];
    }

    const heightMap = new Uint8Array(WORLD_X * WORLD_Z);

    function terrainHeight(x, z) {
      const h =
        9 +
        3.2 * Math.sin(x * 0.17) +
        2.3 * Math.cos(z * 0.15) +
        1.8 * Math.sin((x + z) * 0.09) +
        2.1 * Math.sin((x - z) * 0.12) +
        1.2 * Math.cos(x * 0.31 + z * 0.27);

      return Math.round(Math.max(5, Math.min(WORLD_Y - 8, h)));
    }

    function generateWorld() {
      for (let z = 0; z < WORLD_Z; z++) {
        for (let x = 0; x < WORLD_X; x++) {
          const h = terrainHeight(x, z);
          heightMap[x + z * WORLD_X] = h;

          for (let y = 0; y <= h; y++) {
            let id = 3;

            if (y === h) {
              id = h < 7 ? 6 : 1;
            } else if (y > h - 3) {
              id = 2;
            }

            setRaw(x, y, z, id);
          }
        }
      }

      // 木を適当に生成
      for (let z = 2; z < WORLD_Z - 2; z++) {
        for (let x = 2; x < WORLD_X - 2; x++) {
          const h = heightMap[x + z * WORLD_X];

          if (getBlock(x, h, z) !== 1) continue;
          if (Math.random() > 0.035) continue;

          const trunkHeight = 4 + Math.floor(Math.random() * 3);
          if (h + trunkHeight + 2 >= WORLD_Y) continue;

          // 幹
          for (let y = h + 1; y <= h + trunkHeight; y++) {
            setRaw(x, y, z, 4);
          }

          const top = h + trunkHeight;

          // 葉
          for (let dy = -1; dy <= 1; dy++) {
            for (let dx = -2; dx <= 2; dx++) {
              for (let dz = -2; dz <= 2; dz++) {
                if (dx === 0 && dz === 0 && dy <= 0) continue;

                const radius = Math.abs(dx) + Math.abs(dz);

                if (dy === -1 && radius > 3) continue;
                if (dy === 1 && radius > 2) continue;

                const bx = x + dx;
                const by = top + dy;
                const bz = z + dz;

                if (getBlock(bx, by, bz) === 0) {
                  setRaw(bx, by, bz, 5);
                }
              }
            }
          }
        }
      }
    }

    generateWorld();

    // --------------------------------------------------
    // Three.js 基礎
    // --------------------------------------------------

    const app = document.getElementById("app");

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x87ceeb);
    scene.fog = new THREE.Fog(0x87ceeb, 35, 110);

    const camera = new THREE.PerspectiveCamera(
      75,
      window.innerWidth / window.innerHeight,
      0.1,
      400
    );

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(Math.min(2, window.devicePixelRatio));
    renderer.setSize(window.innerWidth, window.innerHeight);
    app.appendChild(renderer.domElement);

    const hemiLight = new THREE.HemisphereLight(0xbfdfff, 0x3f3a35, 1.1);
    scene.add(hemiLight);

    const sunLight = new THREE.DirectionalLight(0xffffff, 2.0);
    sunLight.position.set(60, 90, 25);
    scene.add(sunLight);

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.35);
    scene.add(ambientLight);

    const voxelMaterial = new THREE.MeshLambertMaterial({
      vertexColors: true,
      side: THREE.DoubleSide
    });

    const highlightGeometry = new THREE.EdgesGeometry(
      new THREE.BoxGeometry(1.002, 1.002, 1.002)
    );
    const highlightMaterial = new THREE.LineBasicMaterial({
      color: 0x000000,
      transparent: true,
      opacity: 0.55
    });
    const blockHighlight = new THREE.LineSegments(highlightGeometry, highlightMaterial);
    blockHighlight.visible = false;
    scene.add(blockHighlight);

    // --------------------------------------------------
    // チャンク描画
    // --------------------------------------------------

    const chunks = new Map();

    function chunkKey(cx, cz) {
      return cx + "," + cz;
    }

    for (let cx = 0; cx < CHUNKS_X; cx++) {
      for (let cz = 0; cz < CHUNKS_Z; cz++) {
        const group = new THREE.Group();
        scene.add(group);
        chunks.set(chunkKey(cx, cz), { group, mesh: null });
      }
    }

    const colorCache = new Map();

    function faceColor(id, normal) {
      const colors = BLOCK_COLORS[id];
      if (!colors) colors = { top: 0xffffff, bottom: 0xffffff, side: 0xffffff };

      let hex;

      if (normal[1] === 1) hex = colors.top;
      else if (normal[1] === -1) hex = colors.bottom;
      else hex = colors.side;

      let cached = colorCache.get(hex);

      if (!cached) {
        cached = [
          ((hex >> 16) & 255) / 255,
          ((hex >> 8) & 255) / 255,
          (hex & 255) / 255
        ];
        colorCache.set(hex, cached);
      }

      return cached;
    }

    function rebuildChunk(cx, cz) {
      const chunk = chunks.get(chunkKey(cx, cz));
      if (!chunk) return;

      if (chunk.mesh) {
        chunk.group.remove(chunk.mesh);
        chunk.mesh.geometry.dispose();
        chunk.mesh = null;
      }

      const positions = [];
      const normals = [];
      const colors = [];
      const indices = [];

      const sx = cx * CHUNK_SIZE;
      const sz = cz * CHUNK_SIZE;

      for (let z = sz; z < sz + CHUNK_SIZE; z++) {
        for (let x = sx; x < sx + CHUNK_SIZE; x++) {
          for (let y = 0; y < WORLD_Y; y++) {
            const id = getBlock(x, y, z);
            if (id === 0) continue;

            for (const face of FACES) {
              const n = face.dir;

              const neighbor = getBlock(
                x + n[0],
                y + n[1],
                z + n[2]
              );

              if (neighbor !== 0) continue;

              const base = positions.length / 3;
              const col = faceColor(id, n);

              for (const c of face.corners) {
                positions.push(
                  x + c[0],
                  y + c[1],
                  z + c[2]
                );

                normals.push(n[0], n[1], n[2]);
                colors.push(col[0], col[1], col[2]);
              }

              indices.push(
                base, base + 1, base + 2,
                base, base + 2, base + 3
              );
            }
          }
        }
      }

      if (indices.length > 0) {
        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
        geometry.setAttribute("normal", new THREE.Float32BufferAttribute(normals, 3));
        geometry.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));
        geometry.setIndex(indices);
        geometry.computeBoundingSphere();

        chunk.mesh = new THREE.Mesh(geometry, voxelMaterial);
        chunk.group.add(chunk.mesh);
      }
    }

    for (let cx = 0; cx < CHUNKS_X; cx++) {
      for (let cz = 0; cz < CHUNKS_Z; cz++) {
        rebuildChunk(cx, cz);
      }
    }

    function setBlock(x, y, z, id) {
      if (!inWorld(x, y, z)) return;

      worldData[index(x, y, z)] = id;

      const cx = Math.floor(x / CHUNK_SIZE);
      const cz = Math.floor(z / CHUNK_SIZE);

      rebuildChunk(cx, cz);

      if (x % CHUNK_SIZE === 0 && cx > 0) {
        rebuildChunk(cx - 1, cz);
      }

      if (x % CHUNK_SIZE === CHUNK_SIZE - 1 && cx < CHUNKS_X - 1) {
        rebuildChunk(cx + 1, cz);
      }

      if (z % CHUNK_SIZE === 0 && cz > 0) {
        rebuildChunk(cx, cz - 1);
      }

      if (z % CHUNK_SIZE === CHUNK_SIZE - 1 && cz < CHUNKS_Z - 1) {
        rebuildChunk(cx, cz + 1);
      }
    }

    // --------------------------------------------------
    // プレイヤー
    // --------------------------------------------------

    const PLAYER_RADIUS = 0.3;
    const PLAYER_HEIGHT = 1.8;
    const EYE_HEIGHT = 1.62;

    const GRAVITY = 26;
    const JUMP_SPEED = 8.6;
    const WALK_SPEED = 4.8;
    const FLY_SPEED = 10.0;

    const spawnX = Math.floor(WORLD_X / 2);
    const spawnZ = Math.floor(WORLD_Z / 2);
    const spawnY = heightMap[spawnX + spawnZ * WORLD_X] + 1;

    const player = {
      pos: new THREE.Vector3(spawnX + 0.5, spawnY, spawnZ + 0.5),
      vel: new THREE.Vector3(),
      yaw: 0,
      pitch: 0,
      onGround: false,
      fly: false,
      selected: 1
    };

    camera.position.set(player.pos.x, player.pos.y + EYE_HEIGHT, player.pos.z);
    camera.rotation.set(player.pitch, player.yaw, 0, "YXZ");

    function collides(pos) {
      const eps = 0.000001;

      const minX = pos.x - PLAYER_RADIUS + eps;
      const maxX = pos.x + PLAYER_RADIUS - eps;
      const minY = pos.y + eps;
      const maxY = pos.y + PLAYER_HEIGHT - eps;
      const minZ = pos.z - PLAYER_RADIUS + eps;
      const maxZ = pos.z + PLAYER_RADIUS - eps;

      const x0 = Math.floor(minX);
      const x1 = Math.floor(maxX);
      const y0 = Math.floor(minY);
      const y1 = Math.floor(maxY);
      const z0 = Math.floor(minZ);
      const z1 = Math.floor(maxZ);

      for (let y = y0; y <= y1; y++) {
        for (let z = z0; z <= z1; z++) {
          for (let x = x0; x <= x1; x++) {
            if (getBlock(x, y, z) !== 0) {
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

      if (collides(player.pos)) {
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

      if (axis === "y" && amount < 0) {
        player.onGround = false;
      }

      return false;
    }

    // --------------------------------------------------
    // 入力
    // --------------------------------------------------

    const keys = new Set();
    let pointerLocked = false;

    const lockHint = document.getElementById("lockHint");
    const statusEl = document.getElementById("status");

    renderer.domElement.addEventListener("click", () => {
      renderer.domElement.requestPointerLock();
    });

    document.addEventListener("pointerlockchange", () => {
      pointerLocked = document.pointerLockElement === renderer.domElement;

      if (pointerLocked) {
        lockHint.style.display = "none";
      } else {
        lockHint.style.display = "";
        keys.clear();
      }
    });

    document.addEventListener("mousemove", (e) => {
      if (!pointerLocked) return;

      const sensitivity = 0.0022;

      player.yaw -= e.movementX * sensitivity;
      player.pitch -= e.movementY * sensitivity;

      player.pitch = Math.max(-1.55, Math.min(1.55, player.pitch));
    });

    document.addEventListener("mousedown", (e) => {
      if (!pointerLocked) return;

      if (e.button === 0) {
        breakBlock();
      } else if (e.button === 2) {
        placeBlock();
      }
    });

    window.addEventListener("contextmenu", (e) => {
      e.preventDefault();
    });

    window.addEventListener("keydown", (e) => {
      keys.add(e.code);

      if (e.code === "Space") {
        e.preventDefault();
      }

      if (e.code === "KeyF") {
        player.fly = !player.fly;
        player.vel.set(0, 0, 0);
        player.onGround = false;
      }

      if (e.code.startsWith("Digit")) {
        const n = parseInt(e.code.slice(5), 10);

        if (n >= 1 && n <= BLOCK_COUNT) {
          player.selected = n;
          updateHotbar();
        }
      }
    });

    window.addEventListener("keyup", (e) => {
      keys.delete(e.code);
    });

    window.addEventListener("wheel", (e) => {
      if (!pointerLocked) return;

      const d = Math.sign(e.deltaY);

      player.selected =
        (((player.selected - 1 + d + BLOCK_COUNT) % BLOCK_COUNT) + 1);

      updateHotbar();
    });

    // --------------------------------------------------
    // レイキャスト
    // --------------------------------------------------

    function raycast(maxDistance = 6) {
      const origin = camera.position;
      const dir = new THREE.Vector3();
      camera.getWorldDirection(dir);

      let ix = Math.floor(origin.x);
      let iy = Math.floor(origin.y);
      let iz = Math.floor(origin.z);

      const dx = dir.x;
      const dy = dir.y;
      const dz = dir.z;

      const stepX = Math.sign(dx) || 1;
      const stepY = Math.sign(dy) || 1;
      const stepZ = Math.sign(dz) || 1;

      const tDeltaX = dx !== 0 ? Math.abs(1 / dx) : Infinity;
      const tDeltaY = dy !== 0 ? Math.abs(1 / dy) : Infinity;
      const tDeltaZ = dz !== 0 ? Math.abs(1 / dz) : Infinity;

      let tMaxX =
        dx !== 0
          ? (dx > 0 ? (ix + 1 - origin.x) / dx : (ix - origin.x) / dx)
          : Infinity;

      let tMaxY =
        dy !== 0
          ? (dy > 0 ? (iy + 1 - origin.y) / dy : (iy - origin.y) / dy)
          : Infinity;

      let tMaxZ =
        dz !== 0
          ? (dz > 0 ? (iz + 1 - origin.z) / dz : (iz - origin.z) / dz)
          : Infinity;

      let normal = [0, 0, 0];
      let distance = 0;

      if (getBlock(ix, iy, iz) !== 0) {
        return { x: ix, y: iy, z: iz, normal: [0, 0, 0] };
      }

      while (distance <= maxDistance) {
        if (tMaxX < tMaxY && tMaxX < tMaxZ) {
          ix += stepX;
          distance = tMaxX;
          tMaxX += tDeltaX;
          normal = [-stepX, 0, 0];
        } else if (tMaxY < tMaxZ) {
          iy += stepY;
          distance = tMaxY;
          tMaxY += tDeltaY;
          normal = [0, -stepY, 0];
        } else {
          iz += stepZ;
          distance = tMaxZ;
          tMaxZ += tDeltaZ;
          normal = [0, 0, -stepZ];
        }

        if (distance > maxDistance) break;

        if (getBlock(ix, iy, iz) !== 0) {
          return { x: ix, y: iy, z: iz, normal };
        }
      }

      return null;
    }

    function intersectsPlayer(x, y, z) {
      const px = player.pos.x;
      const py = player.pos.y;
      const pz = player.pos.z;

      return (
        x + 1 > px - PLAYER_RADIUS &&
        x < px + PLAYER_RADIUS &&
        y + 1 > py &&
        y < py + PLAYER_HEIGHT &&
        z + 1 > pz - PLAYER_RADIUS &&
        z < pz + PLAYER_RADIUS
      );
    }

    function breakBlock() {
      const hit = raycast(6);
      if (!hit) return;

      if (hit.y === 0) return;

      setBlock(hit.x, hit.y, hit.z, 0);
    }

    function placeBlock() {
      const hit = raycast(6);
      if (!hit) return;

      const nx = hit.x + hit.normal[0];
      const ny = hit.y + hit.normal[1];
      const nz = hit.z + hit.normal[2];

      if (!inWorld(nx, ny, nz)) return;
      if (getBlock(nx, ny, nz) !== 0) return;
      if (intersectsPlayer(nx, ny, nz)) return;

      setBlock(nx, ny, nz, player.selected);
    }

    // --------------------------------------------------
    // UI
    // --------------------------------------------------

    const hotbar = document.getElementById("hotbar");

    for (let id = 1; id <= BLOCK_COUNT; id++) {
      const slot = document.createElement("div");
      slot.className = "slot";
      slot.dataset.id = String(id);

      const swatch = document.createElement("div");
      swatch.className = "swatch";
      swatch.style.background =
        "#" + BLOCK_COLORS[id].top.toString(16).padStart(6, "0");

      const num = document.createElement("div");
      num.className = "num";
      num.textContent = String(id);

      slot.appendChild(swatch);
      slot.appendChild(num);
      hotbar.appendChild(slot);
    }

    function updateHotbar() {
      for (const slot of hotbar.querySelectorAll(".slot")) {
        slot.classList.toggle("active", Number(slot.dataset.id) === player.selected);
      }
    }

    updateHotbar();

    // --------------------------------------------------
    // 更新ループ
    // --------------------------------------------------

    function update(dt) {
      camera.position.set(player.pos.x, player.pos.y + EYE_HEIGHT, player.pos.z);
      camera.rotation.set(player.pitch, player.yaw, 0, "YXZ");

      const forward = new THREE.Vector3();
      camera.getWorldDirection(forward);
      forward.y = 0;

      if (forward.lengthSq() < 0.0001) {
        forward.set(0, 0, -1);
      }

      forward.normalize();

      const right = new THREE.Vector3();
      right.crossVectors(forward, new THREE.Vector3(0, 1, 0));
      right.normalize();

      const move = new THREE.Vector3();

      if (keys.has("KeyW")) move.add(forward);
      if (keys.has("KeyS")) move.sub(forward);
      if (keys.has("KeyD")) move.add(right);
      if (keys.has("KeyA")) move.sub(right);

      if (move.lengthSq() > 0) {
        move.normalize();
      }

      if (player.fly) {
        let up = 0;

        if (keys.has("Space")) up += 1;
        if (keys.has("ShiftLeft") || keys.has("ShiftRight")) up -= 1;

        player.vel.x = move.x * FLY_SPEED;
        player.vel.z = move.z * FLY_SPEED;
        player.vel.y = up * FLY_SPEED;

        player.onGround = false;
      } else {
        player.vel.x = move.x * WALK_SPEED;
        player.vel.z = move.z * WALK_SPEED;

        player.vel.y -= GRAVITY * dt;

        if (player.vel.y < -55) {
          player.vel.y = -55;
        }

        if (player.onGround && keys.has("Space")) {
          player.vel.y = JUMP_SPEED;
          player.onGround = false;
        }
      }

      moveAxis("x", player.vel.x * dt);
      moveAxis("z", player.vel.z * dt);
      moveAxis("y", player.vel.y * dt);

      camera.position.set(player.pos.x, player.pos.y + EYE_HEIGHT, player.pos.z);
      camera.rotation.set(player.pitch, player.yaw, 0, "YXZ");

      const hit = raycast(6);

      if (hit) {
        blockHighlight.visible = true;
        blockHighlight.position.set(hit.x + 0.5, hit.y + 0.5, hit.z + 0.5);
      } else {
        blockHighlight.visible = false;
      }

      statusEl.textContent =
        `選択: ${BLOCK_NAMES[player.selected]}` +
        (player.fly ? " | 飛行ON" : "");
    }

    let last = performance.now();

    function tick(now) {
      const dt = Math.min(0.05, (now - last) / 1000);
      last = now;

      update(dt);

      renderer.render(scene, camera);
      requestAnimationFrame(tick);
    }

    requestAnimationFrame(tick);

    // --------------------------------------------------
    // リサイズ
    // --------------------------------------------------

    window.addEventListener("resize", () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    });
  </script>
</body>
</html>
```

---

### 遊び方

1. コードを保存  
   例: `microcraft.html`

2. ファイルを開く  
   ブラウザで表示される。

3. 画面クリック  
   マウスロックが始まります。

4. 操作  
   - `W A S D` 移動
   - `Space` ジャンプ
   - 左クリック 破壊
   - 右クリック 設置
   - `1`〜`7` ブロック選択
   - `F` 飛行
   - `Esc` マウス解除

---

### 拡張しやすい部分

このゲームはわりと改造しやすい構造にしています。

追加しやすいもの:

- ブロックを増やす
- 水を描画する
- 時間経過で空の色を変える
- 音を出す
- 破壊アニメーション
- 複数人マルチ
- インベントリ
- 洞窟生成
- バイオーム
- モブ
- クラフト
- 無限地形

もし続けるなら、次は **インベントリ＋クラフト** か **地形をさらに綺麗にするノイズ生成** か **水中ブロック** あたりを追加すると一気に Minecraft っぽくなります。