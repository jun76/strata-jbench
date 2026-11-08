以下は、ブラウザでそのまま遊べる **Minecraft風の3Dボクセル箱庭ゲーム** です。  
ファイル1本で動くようにして、地形生成・ブロック破壊/設置・物理・視点移動・ホットバー・飛行切替まで入れています。

## 使い方
1. コードを `game.html` などとして保存
2. そのままブラウザで開く
3. クリックでマウスロック
4. `WASD` で移動、マウスで視点、左クリック破壊、右クリック設置

---

## 全ソース

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1.0" />
  <title>Voxel Sandbox</title>
  <style>
    * {
      box-sizing: border-box;
    }
    html, body {
      margin: 0;
      padding: 0;
      width: 100%;
      height: 100%;
      overflow: hidden;
      background: #000;
      font-family: "Segoe UI", Roboto, "Hiragino Kaku Gothic ProN", Meiryo, sans-serif;
      color: #fff;
      user-select: none;
    }
    canvas {
      display: block;
    }
    #loading {
      position: fixed;
      inset: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      background: rgba(0,0,0,0.85);
      font-size: 28px;
      z-index: 100;
    }
    #ui {
      position: fixed;
      left: 12px;
      top: 12px;
      background: rgba(0,0,0,0.45);
      padding: 10px 12px;
      border-radius: 10px;
      font-size: 13px;
      line-height: 1.55;
      pointer-events: none;
      z-index: 20;
      max-width: 320px;
    }
    #ui h2 {
      margin: 0 0 6px 0;
      font-size: 16px;
      color: #8fd6ff;
    }
    #ui .small {
      opacity: 0.8;
      font-size: 12px;
    }
    #status {
      position: fixed;
      right: 12px;
      top: 12px;
      background: rgba(0,0,0,0.45);
      padding: 8px 10px;
      border-radius: 8px;
      font-size: 12px;
      z-index: 20;
      pointer-events: none;
    }
    #hotbar {
      position: fixed;
      left: 50%;
      bottom: 16px;
      transform: translateX(-50%);
      display: flex;
      gap: 6px;
      z-index: 20;
      pointer-events: none;
    }
    .slot {
      width: 56px;
      height: 56px;
      border: 3px solid #333;
      border-radius: 10px;
      position: relative;
      overflow: hidden;
      opacity: 0.85;
    }
    .slot.active {
      border-color: #fff;
      opacity: 1;
      box-shadow: 0 0 0 2px rgba(255,255,255,0.25);
    }
    .slot .num {
      position: absolute;
      left: 4px;
      top: 2px;
      font-size: 11px;
      background: rgba(0,0,0,0.45);
      padding: 1px 3px;
      border-radius: 3px;
    }
    .slot .name {
      position: absolute;
      left: 4px;
      bottom: 2px;
      font-size: 10px;
      background: rgba(0,0,0,0.45);
      padding: 1px 3px;
      border-radius: 3px;
    }
    #crosshair {
      position: fixed;
      left: 50%;
      top: 50%;
      width: 24px;
      height: 24px;
      transform: translate(-50%, -50%);
      pointer-events: none;
      z-index: 15;
    }
    #crosshair::before,
    #crosshair::after {
      content: "";
      position: absolute;
      background: rgba(255,255,255,0.9);
    }
    #crosshair::before {
      left: 11px;
      top: 0;
      width: 2px;
      height: 24px;
    }
    #crosshair::after {
      left: 0;
      top: 11px;
      width: 24px;
      height: 2px;
    }
  </style>
</head>
<body>
  <div id="loading">読み込み中...</div>

  <div id="ui">
    <h2>Voxel Sandbox</h2>
    クリック: ポインターロック<br />
    WASD: 移動 / Space: ジャンプ / Shift: スニーク<br />
    左クリック: 破壊 / 右クリック: 設置<br />
    1〜8: ブロック選択 / ホイール: 選択変更<br />
    F: 飛行切替 / 飛行中はSpace上, Shift下<br />
    <div class="small">※有限世界(96×96)。端では移動が止まることがあります。</div>
  </div>

  <div id="status">FPS: --</div>

  <div id="hotbar"></div>
  <div id="crosshair"></div>

  <script src="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js"></script>
  <script>
    if (!window.THREE) {
      document.getElementById("loading").textContent = "Three.js を読み込めませんでした。ネット接続を確認してください。";
    } else {
      startGame();
    }

    function startGame() {
      const loadingEl = document.getElementById("loading");
      loadingEl.style.display = "none";

      // -----------------------------
      // World constants
      // -----------------------------
      const WORLD_X = 96;
      const WORLD_Z = 96;
      const WORLD_Y = 28;
      const CHUNK = 16;
      const CHUNKS_X = WORLD_X / CHUNK;
      const CHUNKS_Z = WORLD_Z / CHUNK;

      const idx = (x, y, z) => x + z * WORLD_X + y * WORLD_X * WORLD_Z;
      const blocks = new Uint8Array(WORLD_X * WORLD_Y * WORLD_Z);

      const BLOCK = {
        AIR: 0,
        GRASS: 1,
        DIRT: 2,
        STONE: 3,
        OAK: 4,
        LEAF: 5,
        SAND: 6,
        BRICK: 7,
        GLASS: 8,
      };

      const BLOCK_INFO = {
        [BLOCK.GRASS]: {
          name: "草",
          top: 0x5f9b3d,
          side: 0x7d5b3b,
          bottom: 0x6d4f31,
          all: 0x5f9b3d,
          ui: 0x5f9b3d,
        },
        [BLOCK.DIRT]: {
          name: "土",
          all: 0x865727,
          ui: 0x865727,
        },
        [BLOCK.STONE]: {
          name: "石",
          all: 0x8f8f8f,
          ui: 0x8f8f8f,
        },
        [BLOCK.OAK]: {
          name: "木",
          all: 0x9a6a42,
          ui: 0x9a6a42,
        },
        [BLOCK.LEAF]: {
          name: "葉",
          all: 0x3d7e2b,
          ui: 0x3d7e2b,
        },
        [BLOCK.SAND]: {
          name: "砂",
          all: 0xe8d69a,
          ui: 0xe8d69a,
        },
        [BLOCK.BRICK]: {
          name: "レンガ",
          all: 0xb24d3c,
          ui: 0xb24d3c,
        },
        [BLOCK.GLASS]: {
          name: "ガラス",
          all: 0x9fd5ff,
          ui: 0x9fd5ff,
        },
      };

      const BLOCK_ORDER = [
        BLOCK.GRASS,
        BLOCK.DIRT,
        BLOCK.STONE,
        BLOCK.OAK,
        BLOCK.LEAF,
        BLOCK.SAND,
        BLOCK.BRICK,
        BLOCK.GLASS,
      ];

      // -----------------------------
      // Basic helpers
      // -----------------------------
      function getBlock(x, y, z) {
        if (x < 0 || x >= WORLD_X || y < 0 || y >= WORLD_Y || z < 0 || z >= WORLD_Z) return 0;
        return blocks[idx(x, y, z)];
      }

      function inBounds(x, y, z) {
        return x >= 0 && x < WORLD_X && y >= 0 && y < WORLD_Y && z >= 0 && z < WORLD_Z;
      }

      function isSolidRender(x, y, z) {
        if (y < 0) return true;
        if (x < 0 || x >= WORLD_X || z < 0 || z >= WORLD_Z || y >= WORLD_Y) return false;
        return blocks[idx(x, y, z)] !== 0;
      }

      function isSolidCollision(x, y, z) {
        if (x < 0 || x >= WORLD_X || z < 0 || z >= WORLD_Z || y < 0) return true;
        if (y >= WORLD_Y) return false;
        return blocks[idx(x, y, z)] !== 0;
      }

      function isSolidRay(x, y, z) {
        return getBlock(x, y, z) !== 0;
      }

      function setBlockInitial(x, y, z, id) {
        if (!inBounds(x, y, z)) return;
        blocks[idx(x, y, z)] = id;
      }

      // -----------------------------
      // Noise / generation
      // -----------------------------
      let seed = 1337;
      function rnd() {
        seed = (seed * 1664525 + 1013904223) >>> 0;
        return seed / 4294967296;
      }

      function hash2(x, z) {
        let n = Math.sin(x * 12.9898 + z * 78.233) * 43758.5453;
        n -= Math.floor(n);
        return n;
      }

      function smoothstep(t) {
        return t * t * (3 - 2 * t);
      }

      function lerp(a, b, t) {
        return a + (b - a) * t;
      }

      function valueNoise(x, z) {
        const x0 = Math.floor(x);
        const z0 = Math.floor(z);
        const tx = smoothstep(x - x0);
        const tz = smoothstep(z - z0);

        const v00 = hash2(x0, z0);
        const v10 = hash2(x0 + 1, z0);
        const v01 = hash2(x0, z0 + 1);
        const v11 = hash2(x0 + 1, z0 + 1);

        const a = lerp(v00, v10, tx);
        const b = lerp(v01, v11, tx);
        return lerp(a, b, tz);
      }

      function fbm(x, z) {
        let v = 0;
        let amp = 0.55;
        let freq = 1.0;
        for (let i = 0; i < 4; i++) {
          v += valueNoise(x * freq, z * freq) * amp;
          amp *= 0.5;
          freq *= 2.0;
        }
        return v;
      }

      function heightAt(x, z) {
        const base = 6 + valueNoise(x * 0.05, z * 0.05) * 10;
        const detail = fbm(x * 0.08, z * 0.08) * 5;
        const flatten = Math.max(0, 1.2 - Math.sqrt(((x - WORLD_X / 2) ** 2 + (z - WORLD_Z / 2) ** 2)) / 40);
        let h = Math.floor(base + detail - flatten * 3);
        return Math.max(1, Math.min(WORLD_Y - 7, h));
      }

      function generateWorld() {
        for (let x = 0; x < WORLD_X; x++) {
          for (let z = 0; z < WORLD_Z; z++) {
            const h = heightAt(x, z);
            for (let y = 0; y <= h; y++) {
              let id = BLOCK.STONE;
              if (y === h) {
                id = h <= 4 ? BLOCK.SAND : BLOCK.GRASS;
              } else if (y >= h - 2) {
                id = BLOCK.DIRT;
              }
              setBlockInitial(x, y, z, id);
            }

            // Sparse trees
            if (x > 3 && z > 3 && x < WORLD_X - 4 && z < WORLD_Z - 4) {
              const surface = h;
              if (getBlock(x, surface, z) === BLOCK.GRASS && valueNoise(x * 0.13, z * 0.13) > 0.75 && rnd() < 0.22) {
                const trunkH = 4 + Math.floor(rnd() * 3);
                for (let y = surface + 1; y <= surface + trunkH; y++) {
                  setBlockInitial(x, y, z, BLOCK.OAK);
                }

                const topY = surface + trunkH;
                for (let dy = -2; dy <= 2; dy++) {
                  const r = (dy <= 0 ? 2 : 1);
                  for (let dx = -r; dx <= r; dx++) {
                    for (let dz = -r; dz <= r; dz++) {
                      if (dx === 0 && dz === 0 && dy <= 0) continue;
                      if (dx * dx + dz * dz > r * r + 1) continue;
                      setBlockInitial(x + dx, topY + dy, z + dz, BLOCK.LEAF);
                    }
                  }
                }
              }
            }
          }
        }
      }

      generateWorld();

      // -----------------------------
      // Face definitions
      // -----------------------------
      const FACES = [
        { dir: [0, 1, 0], verts: [[0,1,0],[1,1,0],[1,1,1],[0,1,1]], shade: 1.0 },
        { dir: [0,-1, 0], verts: [[0,0,0],[1,0,0],[1,0,1],[0,0,1]], shade: 0.62 },
        { dir: [1, 0, 0], verts: [[1,0,0],[1,1,0],[1,1,1],[1,0,1]], shade: 0.80 },
        { dir: [-1,0, 0], verts: [[0,0,0],[0,1,0],[0,1,1],[0,0,1]], shade: 0.80 },
        { dir: [0, 0, 1], verts: [[0,0,1],[1,0,1],[1,1,1],[0,1,1]], shade: 0.72 },
        { dir: [0, 0,-1], verts: [[0,0,0],[1,0,0],[1,1,0],[0,1,0]], shade: 0.72 },
      ];

      function faceColorInfo(block, faceIndex) {
        const info = BLOCK_INFO[block];
        const face = FACES[faceIndex];
        let hex = info.all || 0xffffff;

        if (face.dir[1] === 1) hex = info.top || info.all || 0xffffff;
        else if (face.dir[1] === -1) hex = info.bottom || info.all || 0xffffff;
        else hex = info.side || info.all || 0xffffff;

        const c = new THREE.Color(hex);
        c.multiplyScalar(face.shade);
        return [c.r, c.g, c.b];
      }

      // Precompute face colors
      const FACE_COLORS = {};
      for (const id of BLOCK_ORDER) {
        FACE_COLORS[id] = FACES.map((_, i) => faceColorInfo(id, i));
      }

      // -----------------------------
      // Three.js setup
      // -----------------------------
      const renderer = new THREE.WebGLRenderer({ antialias: true });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      renderer.setSize(window.innerWidth, window.innerHeight);
      renderer.outputColorSpace = THREE.SRGBColorSpace;
      document.body.appendChild(renderer.domElement);

      const scene = new THREE.Scene();
      scene.background = new THREE.Color(0x87ceeb);
      scene.fog = new THREE.Fog(0x87ceeb, 40, 140);

      const camera = new THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 0.1, 500);
      camera.rotation.order = "YXZ";

      const hemiLight = new THREE.HemisphereLight(0xddeeff, 0x505050, 0.95);
      scene.add(hemiLight);

      const sunLight = new THREE.DirectionalLight(0xffffff, 1.0);
      sunLight.position.set(120, 220, 80);
      scene.add(sunLight);

      const blockMaterial = new THREE.MeshLambertMaterial({
        vertexColors: true,
        side: THREE.DoubleSide,
      });

      const chunks = new Map();
      const dirtyChunks = new Set();

      function addFace(positions, normals, colors, baseX, baseY, baseZ, blockId, faceIndex) {
        const face = FACES[faceIndex];
        const col = FACE_COLORS[blockId][faceIndex];
        const tri = [0, 1, 2, 0, 2, 3];

        for (const vi of tri) {
          const v = face.verts[vi];
          positions.push(baseX + v[0], baseY + v[1], baseZ + v[2]);
          normals.push(face.dir[0], face.dir[1], face.dir[2]);
          colors.push(col[0], col[1], col[2]);
        }
      }

      function buildChunkGeometry(cx, cz) {
        const positions = [];
        const normals = [];
        const colors = [];

        const x0 = cx * CHUNK;
        const x1 = Math.min(x0 + CHUNK, WORLD_X);
        const z0 = cz * CHUNK;
        const z1 = Math.min(z0 + CHUNK, WORLD_Z);

        for (let x = x0; x < x1; x++) {
          for (let z = z0; z < z1; z++) {
            for (let y = 0; y < WORLD_Y; y++) {
              const id = blocks[idx(x, y, z)];
              if (id === 0) continue;

              for (let fi = 0; fi < FACES.length; fi++) {
                const f = FACES[fi];
                const nx = x + f.dir[0];
                const ny = y + f.dir[1];
                const nz = z + f.dir[2];

                if (isSolidRender(nx, ny, nz)) continue;
                addFace(positions, normals, colors, x, y, z, id, fi);
              }
            }
          }
        }

        const geo = new THREE.BufferGeometry();
        geo.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
        geo.setAttribute("normal", new THREE.Float32BufferAttribute(normals, 3));
        geo.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));
        geo.computeBoundingSphere();
        return geo;
      }

      function chunkKey(cx, cz) {
        return cx + "," + cz;
      }

      function rebuildChunk(cx, cz) {
        if (cx < 0 || cz < 0 || cx >= CHUNKS_X || cz >= CHUNKS_Z) return;

        const key = chunkKey(cx, cz);
        const old = chunks.get(key);
        if (old) {
          scene.remove(old.mesh);
          old.mesh.geometry.dispose();
        }

        const geo = buildChunkGeometry(cx, cz);
        const mesh = new THREE.Mesh(geo, blockMaterial);
        scene.add(mesh);
        chunks.set(key, { mesh });
      }

      function buildAllChunks() {
        for (let cx = 0; cx < CHUNKS_X; cx++) {
          for (let cz = 0; cz < CHUNKS_Z; cz++) {
            rebuildChunk(cx, cz);
          }
        }
      }

      function markDirtyForBlock(x, z) {
        const cx = Math.floor(x / CHUNK);
        const cz = Math.floor(z / CHUNK);

        for (let dx = -1; dx <= 1; dx++) {
          for (let dz = -1; dz <= 1; dz++) {
            const nx = cx + dx;
            const nz = cz + dz;
            if (nx >= 0 && nx < CHUNKS_X && nz >= 0 && nz < CHUNKS_Z) {
              dirtyChunks.add(chunkKey(nx, nz));
            }
          }
        }
      }

      function rebuildDirtyChunks() {
        if (dirtyChunks.size === 0) return;
        for (const key of dirtyChunks) {
          const parts = key.split(",");
          rebuildChunk(parseInt(parts[0], 10), parseInt(parts[1], 10));
        }
        dirtyChunks.clear();
      }

      buildAllChunks();

      // Highlight wireframe box
      const highlight = new THREE.LineSegments(
        new THREE.EdgesGeometry(new THREE.BoxGeometry(1.002, 1.002, 1.002)),
        new THREE.LineBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.45 })
      );
      highlight.visible = false;
      scene.add(highlight);

      // -----------------------------
      // Player setup
      // -----------------------------
      const PLAYER_H = 1.8;
      const PLAYER_W = 0.7;
      const GRAVITY = 28;
      const JUMP_SPEED = 8.8;
      const WALK_SPEED = 5.5;
      const SNEAK_SPEED = 2.2;
      const FLY_SPEED = 13.0;

      const player = {
        pos: new THREE.Vector3(),
        vel: new THREE.Vector3(),
        onGround: false,
      };

      let yaw = Math.PI;
      let pitch = -0.18;
      let fly = false;
      let currentBlock = BLOCK.GRASS;
      let locked = false;

      const keys = new Set();

      function surfaceYAt(x, z) {
        for (let y = WORLD_Y - 1; y >= 0; y--) {
          if (blocks[idx(x, y, z)] !== 0) return y + 1;
        }
        return 8;
      }

      const spawnX = WORLD_X / 2 + 0.5;
      const spawnZ = WORLD_Z / 2 + 0.5;
      const spawnY = surfaceYAt(Math.floor(spawnX), Math.floor(spawnZ));
      player.pos.set(spawnX, spawnY + 0.5, spawnZ);

      // -----------------------------
      // UI hotbar
      // -----------------------------
      const hotbarEl = document.getElementById("hotbar");

      function buildHotbar() {
        hotbarEl.innerHTML = "";
        for (let i = 0; i < BLOCK_ORDER.length; i++) {
          const id = BLOCK_ORDER[i];
          const info = BLOCK_INFO[id];
          const slot = document.createElement("div");
          slot.className = "slot";
          slot.style.background = "#" + (info.ui || info.all || 0xffffff).toString(16).padStart(6, "0");
          slot.innerHTML = `
            <div class="num">${i + 1}</div>
            <div class="name">${info.name}</div>
          `;
          hotbarEl.appendChild(slot);
        }
        updateHotbar();
      }

      function updateHotbar() {
        const children = hotbarEl.children;
        for (let i = 0; i < children.length; i++) {
          children[i].classList.toggle("active", BLOCK_ORDER[i] === currentBlock);
        }
      }

      buildHotbar();

      // -----------------------------
      // Input
      // -----------------------------
      const canvas = renderer.domElement;

      canvas.addEventListener("contextmenu", (e) => e.preventDefault());
      document.addEventListener("contextmenu", (e) => e.preventDefault());

      canvas.addEventListener("click", () => {
        if (document.pointerLockElement !== canvas) {
          canvas.requestPointerLock();
        }
      });

      document.addEventListener("pointerlockchange", () => {
        locked = document.pointerLockElement === canvas;
      });

      document.addEventListener("mousemove", (e) => {
        if (!locked) return;
        yaw -= e.movementX * 0.0022;
        pitch -= e.movementY * 0.0022;
        pitch = Math.max(-1.4, Math.min(1.4, pitch));
      });

      document.addEventListener("mousedown", (e) => {
        if (!locked) return;
        if (e.button === 0) breakBlock();
        if (e.button === 2) placeBlock();
      });

      window.addEventListener("keydown", (e) => {
        if (e.code === "Space") e.preventDefault();
        keys.add(e.code);

        if (e.code.startsWith("Digit")) {
          const n = parseInt(e.code.slice(5), 10);
          if (n >= 1 && n <= BLOCK_ORDER.length) {
            currentBlock = BLOCK_ORDER[n - 1];
            updateHotbar();
          }
        }

        if (e.code === "KeyF") {
          fly = !fly;
          player.vel.y = 0;
        }
      });

      window.addEventListener("keyup", (e) => {
        keys.delete(e.code);
      });

      window.addEventListener("wheel", (e) => {
        if (!locked) return;
        const idx = BLOCK_ORDER.indexOf(currentBlock);
        const dir = e.deltaY > 0 ? 1 : -1;
        const next = (idx + dir + BLOCK_ORDER.length) % BLOCK_ORDER.length;
        currentBlock = BLOCK_ORDER[next];
        updateHotbar();
      }, { passive: true });

      // -----------------------------
      // Collision / movement
      // -----------------------------
      function collides() {
        const minX = Math.floor(player.pos.x - PLAYER_W / 2);
        const maxX = Math.floor(player.pos.x + PLAYER_W / 2);
        const minY = Math.floor(player.pos.y);
        const maxY = Math.floor(player.pos.y + PLAYER_H);
        const minZ = Math.floor(player.pos.z - PLAYER_W / 2);
        const maxZ = Math.floor(player.pos.z + PLAYER_W / 2);

        for (let x = minX; x <= maxX; x++) {
          for (let y = minY; y <= maxY; y++) {
            for (let z = minZ; z <= maxZ; z++) {
              if (isSolidCollision(x, y, z)) return true;
            }
          }
        }
        return false;
      }

      function moveAxis(axis, amount) {
        if (amount === 0) return false;
        const old = player.pos[axis];
        player.pos[axis] += amount;
        if (collides()) {
          player.pos[axis] = old;
          return true;
        }
        return false;
      }

      function moveHorizontal(axis, amount) {
        if (amount === 0) return;

        const old = player.pos[axis];
        player.pos[axis] += amount;

        if (!collides()) return;

        if (!fly && player.onGround) {
          const oldY = player.pos.y;
          player.pos.y += 0.35;
          if (!collides()) return;
          player.pos.y = oldY;
        }

        player.pos[axis] = old;
      }

      function blockIntersectsPlayer(x, y, z) {
        const px = player.pos.x;
        const py = player.pos.y;
        const pz = player.pos.z;
        const hw = PLAYER_W / 2;
        const h = PLAYER_H;

        return (
          x < px + hw && x + 1 > px - hw &&
          y < py + h && y + 1 > py &&
          z < pz + hw && z + 1 > pz - hw
        );
      }

      function updatePlayer(dt) {
        const sneak = keys.has("ShiftLeft") && !fly;
        const speed = fly ? FLY_SPEED : sneak ? SNEAK_SPEED : WALK_SPEED;

        let mx = 0;
        let mz = 0;
        if (keys.has("KeyW")) mz -= 1;
        if (keys.has("KeyS")) mz += 1;
        if (keys.has("KeyA")) mx -= 1;
        if (keys.has("KeyD")) mx += 1;

        const len = Math.hypot(mx, mz);
        if (len > 0) {
          mx /= len;
          mz /= len;
        }

        const sinY = Math.sin(yaw);
        const cosY = Math.cos(yaw);
        const worldX = mx * cosY + mz * sinY;
        const worldZ = -mx * sinY + mz * cosY;

        player.vel.x = worldX * speed;
        player.vel.z = worldZ * speed;

        if (fly) {
          player.onGround = false;
          let vy = 0;
          if (keys.has("Space")) vy += FLY_SPEED;
          if (keys.has("ShiftLeft")) vy -= FLY_SPEED;
          player.vel.y = vy;
        } else {
          if (player.onGround && player.vel.y < 0) player.vel.y = 0;
          player.vel.y -= GRAVITY * dt;
          if (player.vel.y < -40) player.vel.y = -40;

          if (keys.has("Space") && player.onGround) {
            player.vel.y = JUMP_SPEED;
            player.onGround = false;
          }
        }

        // Horizontal move first (after gravity/jump decision)
        moveHorizontal("x", player.vel.x * dt);
        moveHorizontal("z", player.vel.z * dt);

        // Vertical move
        const hitY = moveAxis("y", player.vel.y * dt);
        if (hitY) {
          if (player.vel.y < 0) {
            player.onGround = true;
          }
          player.vel.y = 0;
        } else if (!fly) {
          player.onGround = false;
        }
      }

      // -----------------------------
      // Raycast
      // -----------------------------
      function raycastBlock(ox, oy, oz, dx, dy, dz, maxDist = 8) {
        let x = Math.floor(ox);
        let y = Math.floor(oy);
        let z = Math.floor(oz);

        const sx = dx > 0 ? 1 : dx < 0 ? -1 : 0;
        const sy = dy > 0 ? 1 : dy < 0 ? -1 : 0;
        const sz = dz > 0 ? 1 : dz < 0 ? -1 : 0;

        const tx = dx !== 0 ? Math.abs(1 / dx) : Infinity;
        const ty = dy !== 0 ? Math.abs(1 / dy) : Infinity;
        const tz = dz !== 0 ? Math.abs(1 / dz) : Infinity;

        let tmx = dx !== 0 ? (sx > 0 ? (x + 1 - ox) * tx : (x - ox) * tx) : Infinity;
        let tmy = dy !== 0 ? (sy > 0 ? (y + 1 - oy) * ty : (y - oy) * ty) : Infinity;
        let tmz = dz !== 0 ? (sz > 0 ? (z + 1 - oz) * tz : (z - oz) * tz) : Infinity;

        let nx = 0, ny = 0, nz = 0;
        let t = 0;

        while (t <= maxDist) {
          if (isSolidRay(x, y, z)) {
            return { x, y, z, nx, ny, nz, dist: t };
          }

          if (tmx < tmy && tmx < tmz) {
            x += sx;
            t = tmx;
            tmx += tx;
            nx = -sx; ny = 0; nz = 0;
          } else if (tmy < tmz) {
            y += sy;
            t = tmy;
            tmy += ty;
            nx = 0; ny = -sy; nz = 0;
          } else {
            z += sz;
            t = tmz;
            tmz += tz;
            nx = 0; ny = 0; nz = -sz;
          }
        }

        return null;
      }

      let hit = null;
      const dirVec = new THREE.Vector3();

      function updateHighlight() {
        camera.getWorldDirection(dirVec);
        hit = raycastBlock(
          camera.position.x,
          camera.position.y,
          camera.position.z,
          dirVec.x,
          dirVec.y,
          dirVec.z,
          8
        );

        if (hit) {
          highlight.visible = true;
          highlight.position.set(hit.x + 0.5, hit.y + 0.5, hit.z + 0.5);
        } else {
          highlight.visible = false;
        }
      }

      function breakBlock() {
        if (!hit) return;
        if (!inBounds(hit.x, hit.y, hit.z)) return;
        setBlockInitial(hit.x, hit.y, hit.z, BLOCK.AIR);
        markDirtyForBlock(hit.x, hit.z);
        rebuildDirtyChunks();
      }

      function placeBlock() {
        if (!hit) return;
        if (hit.nx === 0 && hit.ny === 0 && hit.nz === 0) return;

        const x = hit.x + hit.nx;
        const y = hit.y + hit.ny;
        const z = hit.z + hit.nz;

        if (!inBounds(x, y, z)) return;
        if (getBlock(x, y, z) !== 0) return;
        if (blockIntersectsPlayer(x, y, z)) return;

        setBlockInitial(x, y, z, currentBlock);
        markDirtyForBlock(x, z);
        rebuildDirtyChunks();
      }

      // -----------------------------
      // Resize
      // -----------------------------
      window.addEventListener("resize", () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
      });

      // -----------------------------
      // Main loop
      // -----------------------------
      const clock = new THREE.Clock();
      const statusEl = document.getElementById("status");

      let fpsTime = 0;
      let frames = 0;

      function animate() {
        requestAnimationFrame(animate);

        const dt = Math.min(clock.getDelta(), 0.05);
        updatePlayer(dt);

        const eyeHeight = fly ? 1.62 : (keys.has("ShiftLeft") ? 1.45 : 1.62);
        camera.position.set(player.pos.x, player.pos.y + eyeHeight, player.pos.z);
        camera.rotation.set(pitch, yaw, 0);

        updateHighlight();

        renderer.render(scene, camera);

        frames++;
        fpsTime += dt;
        if (fpsTime >= 0.5) {
          const fps = Math.round(frames / fpsTime);
          statusEl.textContent = `FPS: ${fps} / ${fly ? "FLY" : "WALK"} / ${BLOCK_INFO[currentBlock].name}`;
          frames = 0;
          fpsTime = 0;
        }
      }

      animate();
    }
  </script>
</body>
</html>
```

---

## 追加できる要素

もう少し「Minecraft感」を強めるなら、次も追加しやすいです。

- **水ブロック**
- **作業台やインベントリ**
- **セーブ/ロード**
- **テクスチャ**
- **影**
- **日中/夜間サイクル**
- **無限世界のチャンクストリーミング**
- **敵・動物NPC**
- **破壊音・設置音**

必要なら次は、

1. テクスチャ付き版
2. インベントリ付き版
3. 自動セーブ版
4. 無限世界版
5. スマホ対応版

のどれかに拡張して書き直せます。