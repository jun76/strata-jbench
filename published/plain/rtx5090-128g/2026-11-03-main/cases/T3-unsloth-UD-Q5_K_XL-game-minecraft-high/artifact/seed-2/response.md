「マイクラ風」というより、完全に自作の Web 用 3D ボクセル箱庭ゲームを作りました。  
以下は **単一の HTML ファイル** です。ファイル名を `voxel-sandbox.html` などにして、ブラウザで開けば動きます。

- Three.js（CDN）使用
- 自動生成の地形
- ブロックを置いて/壊す
- 一人称視点
- 衝突判定 / ジャンプ / 飛行モード
- 6種類のブロック選択

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>ボクセル箱庭</title>
  <style>
    html, body {
      margin: 0;
      width: 100%;
      height: 100%;
      overflow: hidden;
      background: #87ceeb;
      font-family: system-ui, -apple-system, sans-serif;
      color: white;
      user-select: none;
    }

    canvas {
      display: block;
    }

    #overlay {
      position: fixed;
      inset: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      background: rgba(8, 18, 28, 0.62);
      cursor: pointer;
      z-index: 20;
    }

    #overlay.hidden {
      display: none;
    }

    #overlay .box {
      padding: 24px 28px;
      border-radius: 14px;
      background: rgba(0, 0, 0, 0.28);
      box-shadow: 0 12px 40px rgba(0, 0, 0, 0.25);
      max-width: 560px;
    }

    #overlay h1 {
      margin: 0 0 10px;
      font-size: 28px;
    }

    #overlay p {
      margin: 6px 0;
      line-height: 1.6;
      color: #e8f4ff;
    }

    #coords {
      position: fixed;
      left: 10px;
      top: 10px;
      padding: 8px 10px;
      border-radius: 8px;
      background: rgba(0, 0, 0, 0.30);
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 13px;
      line-height: 1.45;
      z-index: 10;
    }

    #help {
      position: fixed;
      left: 10px;
      bottom: 86px;
      padding: 9px 11px;
      border-radius: 8px;
      background: rgba(0, 0, 0, 0.30);
      font-size: 12.5px;
      line-height: 1.55;
      z-index: 10;
    }

    #hotbar {
      position: fixed;
      left: 50%;
      bottom: 14px;
      transform: translateX(-50%);
      display: flex;
      gap: 7px;
      z-index: 10;
      pointer-events: none;
    }

    .slot {
      position: relative;
      width: 54px;
      height: 54px;
      border: 3px solid rgba(0, 0, 0, 0.32);
      border-radius: 7px;
      overflow: hidden;
      background: rgba(255,255,255,0.14);
      box-shadow: inset 0 0 0 1px rgba(255,255,255,0.12);
    }

    .slot.selected {
      border-color: #fff;
      transform: scale(1.08);
      box-shadow: 0 0 0 2px rgba(255,255,255,0.18);
    }

    .slot .num {
      position: absolute;
      left: 4px;
      top: 2px;
      font-size: 12px;
      font-weight: 700;
      color: #fff;
      text-shadow: 0 1px 2px #000;
      z-index: 2;
    }

    .slot .swatch {
      width: 100%;
      height: 100%;
    }

    #crosshair {
      position: fixed;
      left: 50%;
      top: 50%;
      width: 2px;
      height: 18px;
      background: #fff;
      transform: translate(-50%, -50%);
      mix-blend-mode: difference;
      pointer-events: none;
      z-index: 9;
    }

    #crosshair::after {
      content: "";
      position: absolute;
      left: 50%;
      top: 50%;
      width: 18px;
      height: 2px;
      background: #fff;
      transform: translate(-50%, -50%);
    }
  </style>
</head>
<body>
  <div id="overlay">
    <div class="box">
      <h1>ボクセル箱庭</h1>
      <p><b>クリック</b>して画面をクリックすると開始します。</p>
      <p>WASD: 移動 / Space: ジャンプ / マウス: 視点</p>
      <p>左クリック: 破壊 / 右クリック: 設置 / 1〜6: ブロック選択</p>
      <p>F: 飛行モード切り替え</p>
    </div>
  </div>

  <div id="coords">
    読み込み中…
  </div>

  <div id="help">
    左クリック: 破壊<br>
    右クリック: 設置<br>
    1〜6: ブロック<br>
    WASD: 移動 / Space: ジャンプ<br>
    F: 飛行モード / Shift: 下降
  </div>

  <div id="hotbar"></div>
  <div id="crosshair"></div>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script>
    (() => {
      // --------------------------------------------------
      // 基本定数
      // --------------------------------------------------
      const W = 64;
      const D = 64;
      const H = 32;
      const CHUNK = 16;
      const CHUNK_X = W / CHUNK;
      const CHUNK_Z = D / CHUNK;

      const PLAYER_R = 0.30;
      const PLAYER_H = 1.80;
      const EYE_H = 1.62;

      const GRAVITY = 24;
      const JUMP_V = 8.2;
      const WALK_SPEED = 4.35;
      const FLY_SPEED = 12.0;

      // --------------------------------------------------
      // ブロック定義
      // --------------------------------------------------
      const BLOCKS = [
        null,
        { name: '草', color: 0x65b449, opaque: true },
        { name: '土', color: 0x8b5e3c, opaque: true },
        { name: '石', color: 0x8c8c8c, opaque: true },
        { name: '木', color: 0x724d2e, opaque: true },
        { name: '葉', color: 0x3f8f38, opaque: true },
        { name: '砂', color: 0xe1d09b, opaque: true },
      ];

      const HOTBAR = [1, 2, 3, 4, 5, 6];
      let selected = 0;

      // --------------------------------------------------
      // ワールド配列
      // --------------------------------------------------
      const world = new Uint8Array(W * H * D);

      function idx(x, y, z) {
        return x + W * (y + H * z);
      }

      function getBlock(x, y, z) {
        if (x < 0 || x >= W || y < 0 || y >= H || z < 0 || z >= D) return 0;
        return world[idx(x, y, z)];
      }

      function setBlock(x, y, z, id) {
        if (x < 0 || x >= W || y < 0 || y >= H || z < 0 || z >= D) return;
        world[idx(x, y, z)] = id;
      }

      // --------------------------------------------------
      // Three.js
      // --------------------------------------------------
      const scene = new THREE.Scene();
      scene.background = new THREE.Color(0x9ad7ff);
      scene.fog = new THREE.Fog(0x9ad7ff, 34, 92);

      const camera = new THREE.PerspectiveCamera(
        72,
        window.innerWidth / window.innerHeight,
        0.08,
        220
      );
      camera.rotation.order = 'YXZ';

      const renderer = new THREE.WebGLRenderer({ antialias: true });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
      renderer.setSize(window.innerWidth, window.innerHeight);
      document.body.appendChild(renderer.domElement);

      const sceneRoot = scene;

      const ambient = new THREE.HemisphereLight(0xffffff, 0x556055, 0.88);
      scene.add(ambient);

      const sun = new THREE.DirectionalLight(0xffffff, 0.45);
      sun.position.set(1.0, 2.4, 0.8);
      scene.add(sun);

      const chunkMaterial = new THREE.MeshLambertMaterial({
        vertexColors: true,
        side: THREE.DoubleSide,
      });

      const chunks = new Map();

      // --------------------------------------------------
      // ブロック面の形状
      // --------------------------------------------------
      // 0:+X, 1:-X, 2:+Y, 3:-Y, 4:+Z, 5:-Z
      const FACES = [
        {
          dir: [1, 0, 0],
          verts: [
            [1, 0, 0],
            [1, 0, 1],
            [1, 1, 1],
            [1, 1, 0],
          ],
        },
        {
          dir: [-1, 0, 0],
          verts: [
            [0, 0, 1],
            [0, 0, 0],
            [0, 1, 0],
            [0, 1, 1],
          ],
        },
        {
          dir: [0, 1, 0],
          verts: [
            [0, 1, 1],
            [1, 1, 1],
            [1, 1, 0],
            [0, 1, 0],
          ],
        },
        {
          dir: [0, -1, 0],
          verts: [
            [0, 0, 0],
            [1, 0, 0],
            [1, 0, 1],
            [0, 0, 1],
          ],
        },
        {
          dir: [0, 0, 1],
          verts: [
            [0, 0, 1],
            [1, 0, 1],
            [1, 1, 1],
            [0, 1, 1],
          ],
        },
        {
          dir: [0, 0, -1],
          verts: [
            [1, 0, 0],
            [0, 0, 0],
            [0, 1, 0],
            [1, 1, 0],
          ],
        },
      ];

      const FACE_BRIGHT = [0.84, 0.80, 1.0, 0.60, 0.92, 0.86];
      const tmpColor = new THREE.Color();

      function faceColor(id, faceIndex) {
        if (id === 1) {
          if (faceIndex === 2) return 0x73c64f; // 草の上面
          if (faceIndex === 3) return 0x8b6b41; // 草の下面
          return 0x9bb35b;                      // 草の横面
        }
        return BLOCKS[id].color;
      }

      // --------------------------------------------------
      // チャンク生成
      // --------------------------------------------------
      function chunkKey(cx, cz) {
        return cx + ',' + cz;
      }

      function removeChunk(key) {
        const mesh = chunks.get(key);
        if (!mesh) return;
        scene.remove(mesh);
        if (mesh.geometry) mesh.geometry.dispose();
        chunks.delete(key);
      }

      function buildChunk(cx, cz) {
        const key = chunkKey(cx, cz);
        removeChunk(key);

        const x0 = cx * CHUNK;
        const x1 = Math.min(x0 + CHUNK, W);
        const z0 = cz * CHUNK;
        const z1 = Math.min(z0 + CHUNK, D);

        const positions = [];
        const normals = [];
        const colors = [];
        const indices = [];

        for (let z = z0; z < z1; z++) {
          for (let x = x0; x < x1; x++) {
            for (let y = 0; y < H; y++) {
              const id = world[idx(x, y, z)];
              if (id === 0) continue;

              for (let fi = 0; fi < FACES.length; fi++) {
                const face = FACES[fi];
                const dx = face.dir[0];
                const dy = face.dir[1];
                const dz = face.dir[2];

                // 最下層の下面は描かない
                if (dy < 0 && y === 0) continue;

                const nx = x + dx;
                const ny = y + dy;
                const nz = z + dz;

                let opaqueNeighbor = false;
                if (
                  nx >= 0 && nx < W &&
                  ny >= 0 && ny < H &&
                  nz >= 0 && nz < D
                ) {
                  const nid = world[idx(nx, ny, nz)];
                  if (nid !== 0) opaqueNeighbor = BLOCKS[nid].opaque;
                }

                if (opaqueNeighbor) continue;

                const start = positions.length / 3;

                for (let v = 0; v < 4; v++) {
                  const vv = face.verts[v];
                  positions.push(x + vv[0], y + vv[1], z + vv[2]);
                }

                for (let v = 0; v < 4; v++) {
                  normals.push(dx, dy, dz);
                }

                tmpColor
                  .setHex(faceColor(id, fi))
                  .multiplyScalar(FACE_BRIGHT[fi]);

                for (let v = 0; v < 4; v++) {
                  colors.push(tmpColor.r, tmpColor.g, tmpColor.b);
                }

                indices.push(
                  start, start + 1, start + 2,
                  start, start + 2, start + 3
                );
              }
            }
          }
        }

        if (positions.length === 0) return;

        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        geometry.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
        geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
        geometry.setIndex(indices);
        geometry.computeBoundingSphere();

        const mesh = new THREE.Mesh(geometry, chunkMaterial);
        mesh.frustumCulled = true;
        scene.add(mesh);
        chunks.set(key, mesh);
      }

      function buildAllChunks() {
        for (let cz = 0; cz < CHUNK_Z; cz++) {
          for (let cx = 0; cx < CHUNK_X; cx++) {
            buildChunk(cx, cz);
          }
        }
      }

      function rebuildAround(x, z) {
        const cx = Math.floor(x / CHUNK);
        const cz = Math.floor(z / CHUNK);

        for (let dz = -1; dz <= 1; dz++) {
          for (let dx = -1; dx <= 1; dx++) {
            const nx = cx + dx;
            const nz = cz + dz;
            if (nx >= 0 && nx < CHUNK_X && nz >= 0 && nz < CHUNK_Z) {
              buildChunk(nx, nz);
            }
          }
        }
      }

      // --------------------------------------------------
      // 簡易 PRNG（地形・木を再現性のある乱数で生成）
      // --------------------------------------------------
      function mulberry32(seed) {
        let a = seed >>> 0;
        return function () {
          a += 0x6D2B79F5;
          let t = a;
          t = Math.imul(t ^ (t >>> 15), t | 1);
          t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
          return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
        };
      }

      const rand = mulberry32(20260513);

      // --------------------------------------------------
      // 地形生成
      // --------------------------------------------------
      function surfaceHeight(x, z) {
        const h =
          10 +
          Math.sin(x * 0.13) * 2.3 +
          Math.cos(z * 0.11) * 2.0 +
          Math.sin((x + z) * 0.07) * 1.8 +
          Math.sin((x - z) * 0.05) * 1.2;

        return Math.max(2, Math.min(20, Math.floor(h)));
      }

      function generateWorld() {
        for (let z = 0; z < D; z++) {
          for (let x = 0; x < W; x++) {
            const h = surfaceHeight(x, z);

            for (let y = 0; y <= h; y++) {
              let id;

              if (h <= 7) {
                if (y === h) id = 6; // 砂浜
                else if (y >= h - 2) id = 6;
                else id = 3;
              } else {
                if (y === h) id = 1; // 草
                else if (y >= h - 3) id = 2; // 土
                else id = 3; // 石
              }

              setBlock(x, y, z, id);
            }
          }
        }

        // 木生成
        const spawnX = 32;
        const spawnZ = 32;

        for (let z = 2; z < D - 2; z++) {
          for (let x = 2; x < W - 2; x++) {
            const h = surfaceHeight(x, z);
            const top = getBlock(x, h, z);

            if (top !== 1) continue;
            if (Math.abs(x - spawnX) + Math.abs(z - spawnZ) < 8) continue;
            if (rand() > 0.010) continue;
            if (h + 7 >= H) continue;

            const trunkBase = h + 1;
            const trunkH = 4;
            const trunkTop = trunkBase + trunkH - 1;

            // 幹
            for (let y = trunkBase; y <= trunkTop; y++) {
              setBlock(x, y, z, 4);
            }

            // 葉
            for (let ly = trunkTop - 1; ly <= trunkTop + 1; ly++) {
              const radius = ly === trunkTop + 1 ? 1 : 2;

              for (let lx = -radius; lx <= radius; lx++) {
                for (let lz = -radius; lz <= radius; lz++) {
                  if (lx === 0 && lz === 0 && ly <= trunkTop) continue;

                  if (lx === 0 && lz === 0 && ly === trunkTop) continue;

                  if (Math.abs(lx) + Math.abs(lz) <= radius + 1) {
                    if (getBlock(x + lx, ly, z + lz) === 0) {
                      setBlock(x + lx, ly, z + lz, 5);
                    }
                  }
                }
              }
            }
          }
        }

        buildAllChunks();
      }

      function topY(x, z) {
        for (let y = H - 1; y >= 0; y--) {
          if (world[idx(x, y, z)] !== 0) return y;
        }
        return 0;
      }

      // --------------------------------------------------
      // 衝突判定
      // --------------------------------------------------
      function isSolidCollision(x, y, z) {
        if (x < 0 || x >= W || z < 0 || z >= D) return true;
        if (y < 0) return true;
        if (y >= H) return false;
        return world[idx(x, y, z)] !== 0;
      }

      function collide(px, py, pz) {
        const eps = 1e-4;

        const minX = Math.floor(px - PLAYER_R + eps);
        const maxX = Math.floor(px + PLAYER_R - eps);

        const minY = Math.floor(py + eps);
        const maxY = Math.floor(py + PLAYER_H - eps);

        const minZ = Math.floor(pz - PLAYER_R + eps);
        const maxZ = Math.floor(pz + PLAYER_R - eps);

        for (let y = minY; y <= maxY; y++) {
          for (let z = minZ; z <= maxZ; z++) {
            for (let x = minX; x <= maxX; x++) {
              if (isSolidCollision(x, y, z)) return true;
            }
          }
        }

        return false;
      }

      function blockIntersectsPlayer(bx, by, bz) {
        return (
          player.x + PLAYER_R > bx &&
          player.x - PLAYER_R < bx + 1 &&
          player.y + PLAYER_H > by &&
          player.y < by + 1 &&
          player.z + PLAYER_R > bz &&
          player.z - PLAYER_R < bz + 1
        );
      }

      // --------------------------------------------------
      // ボクセルレイキャスト
      // --------------------------------------------------
      function raycastBlock(origin, dir, maxDist) {
        let x = Math.floor(origin.x);
        let y = Math.floor(origin.y);
        let z = Math.floor(origin.z);

        if (
          x >= 0 && x < W &&
          y >= 0 && y < H &&
          z >= 0 && z < D &&
          world[idx(x, y, z)] !== 0
        ) {
          return { x, y, z, normal: [0, 1, 0], dist: 0 };
        }

        const stepX = dir.x > 0 ? 1 : dir.x < 0 ? -1 : 0;
        const stepY = dir.y > 0 ? 1 : dir.y < 0 ? -1 : 0;
        const stepZ = dir.z > 0 ? 1 : dir.z < 0 ? -1 : 0;

        const absDirX = Math.abs(dir.x);
        const absDirY = Math.abs(dir.y);
        const absDirZ = Math.abs(dir.z);

        const tDeltaX = absDirX > 1e-8 ? Math.abs(1 / dir.x) : Infinity;
        const tDeltaY = absDirY > 1e-8 ? Math.abs(1 / dir.y) : Infinity;
        const tDeltaZ = absDirZ > 1e-8 ? Math.abs(1 / dir.z) : Infinity;

        const distX = dir.x > 0 ? (x + 1 - origin.x) : (origin.x - x);
        const distY = dir.y > 0 ? (y + 1 - origin.y) : (origin.y - y);
        const distZ = dir.z > 0 ? (z + 1 - origin.z) : (origin.z - z);

        let tMaxX = absDirX > 1e-8 ? distX / absDirX : Infinity;
        let tMaxY = absDirY > 1e-8 ? distY / absDirY : Infinity;
        let tMaxZ = absDirZ > 1e-8 ? distZ / absDirZ : Infinity;

        let t = 0;
        let lastAxis = -1;

        while (t < maxDist) {
          if (tMaxX < tMaxY && tMaxX < tMaxZ) {
            x += stepX;
            t = tMaxX;
            tMaxX += tDeltaX;
            lastAxis = 0;
          } else if (tMaxY < tMaxZ) {
            y += stepY;
            t = tMaxY;
            tMaxY += tDeltaY;
            lastAxis = 1;
          } else {
            z += stepZ;
            t = tMaxZ;
            tMaxZ += tDeltaZ;
            lastAxis = 2;
          }

          if (t >= maxDist) break;

          if (x < 0 || x >= W || y < 0 || y >= H || z < 0 || z >= D) {
            break;
          }

          if (world[idx(x, y, z)] !== 0) {
            const normal = [0, 0, 0];
            if (lastAxis === 0) normal[0] = -stepX;
            else if (lastAxis === 1) normal[1] = -stepY;
            else normal[2] = -stepZ;

            return { x, y, z, normal, dist: t };
          }
        }

        return null;
      }

      // --------------------------------------------------
      // プレイヤー状態
      // --------------------------------------------------
      const player = {
        x: 32.5,
        y: 20.2,
        z: 32.5,
        vx: 0,
        vy: 0,
        vz: 0,
      };

      let yaw = 0.65;
      let pitch = -0.28;
      let fly = false;
      let grounded = false;

      const keys = Object.create(null);

      // --------------------------------------------------
      // 入力
      // --------------------------------------------------
      const overlay = document.getElementById('overlay');
      const coordsEl = document.getElementById('coords');
      const hotbarEl = document.getElementById('hotbar');

      function setPointerLockedUI() {
        if (document.pointerLockElement === renderer.domElement) {
          overlay.classList.add('hidden');
        } else {
          overlay.classList.remove('hidden');
        }
      }

      overlay.addEventListener('click', () => {
        if (document.pointerLockElement !== renderer.domElement) {
          renderer.domElement.requestPointerLock();
        }
      });

      document.addEventListener('pointerlockchange', setPointerLockedUI);

      document.addEventListener('contextmenu', (e) => {
        e.preventDefault();
      });

      document.addEventListener('mousemove', (e) => {
        if (document.pointerLockElement !== renderer.domElement) return;

        yaw -= e.movementX * 0.0022;
        pitch -= e.movementY * 0.0022;

        pitch = Math.max(-Math.PI / 2 + 0.02, Math.min(Math.PI / 2 - 0.02, pitch));
      });

      document.addEventListener('mousedown', (e) => {
        if (document.pointerLockElement !== renderer.domElement) return;

        if (e.button === 0) destroyBlock();
        else if (e.button === 2) placeBlock();
      });

      document.addEventListener('keydown', (e) => {
        keys[e.code] = true;

        if (e.code === 'Space') e.preventDefault();

        if (e.code === 'KeyF') {
          fly = !fly;
          player.vy = 0;
        }

        const digit = e.code.match(/^Digit([1-6])$/);
        if (digit) {
          selected = Math.max(0, Math.min(HOTBAR.length - 1, parseInt(digit[1], 10) - 1));
          refreshHotbar();
        }
      });

      document.addEventListener('keyup', (e) => {
        keys[e.code] = false;
      });

      // --------------------------------------------------
      // ブロック操作
      // --------------------------------------------------
      const rayDir = new THREE.Vector3();

      function destroyBlock() {
        camera.getWorldDirection(rayDir);
        const hit = raycastBlock(camera.position, rayDir, 8.0);
        if (!hit) return;

        // 最下層だけは壊さない（落下しすぎる事故防止）
        if (hit.y <= 0) return;

        setBlock(hit.x, hit.y, hit.z, 0);
        rebuildAround(hit.x, hit.z);
      }

      function placeBlock() {
        camera.getWorldDirection(rayDir);
        const hit = raycastBlock(camera.position, rayDir, 8.0);
        if (!hit) return;

        const bx = hit.x + hit.normal[0];
        const by = hit.y + hit.normal[1];
        const bz = hit.z + hit.normal[2];

        if (bx < 0 || bx >= W || by < 0 || by >= H || bz < 0 || bz >= D) return;
        if (world[idx(bx, by, bz)] !== 0) return;
        if (blockIntersectsPlayer(bx, by, bz)) return;

        setBlock(bx, by, bz, HOTBAR[selected]);
        rebuildAround(bx, bz);
      }

      // --------------------------------------------------
      // 当たり判定枠
      // --------------------------------------------------
      const highlight = new THREE.LineSegments(
        new THREE.EdgesGeometry(new THREE.BoxGeometry(1.002, 1.002, 1.002)),
        new THREE.LineBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.72 })
      );
      highlight.visible = false;
      scene.add(highlight);

      // --------------------------------------------------
      // Hotbar UI
      // --------------------------------------------------
      function hexString(id) {
        const colorId = id === 1 ? 0x73c64f : BLOCKS[id].color;
        return '#' + new THREE.Color(colorId).getHexString();
      }

      function refreshHotbar() {
        hotbarEl.innerHTML = '';

        HOTBAR.forEach((id, i) => {
          const slot = document.createElement('div');
          slot.className = 'slot' + (i === selected ? ' selected' : '');

          const num = document.createElement('div');
          num.className = 'num';
          num.textContent = String(i + 1);

          const swatch = document.createElement('div');
          swatch.className = 'swatch';
          swatch.style.background = hexString(id);

          slot.appendChild(num);
          slot.appendChild(swatch);
          hotbarEl.appendChild(slot);
        });
      }

      refreshHotbar();

      // --------------------------------------------------
      // 更新
      // --------------------------------------------------
      function updatePlayer(dt) {
        const forward = (keys.KeyW ? 1 : 0) - (keys.KeyS ? 1 : 0);
        const right = (keys.KeyD ? 1 : 0) - (keys.KeyA ? 1 : 0);

        const fx = -Math.sin(yaw);
        const fz = -Math.cos(yaw);

        const rx = Math.cos(yaw);
        const rz = -Math.sin(yaw);

        let wx = fx * forward + rx * right;
        let wz = fz * forward + rz * right;

        const len = Math.hypot(wx, wz);
        if (len > 0) {
          wx /= len;
          wz /= len;
        }

        const speed = fly ? FLY_SPEED : WALK_SPEED;
        const targetVX = wx * speed;
        const targetVZ = wz * speed;

        const horizontalAccel = fly ? 10.0 : (grounded ? 15.0 : 5.0);
        const tH = Math.min(1.0, horizontalAccel * dt);

        player.vx += (targetVX - player.vx) * tH;
        player.vz += (targetVZ - player.vz) * tH;

        if (!fly) {
          if (keys.Space && grounded) {
            player.vy = JUMP_V;
            grounded = false;
          }

          player.vy -= GRAVITY * dt;
          player.vy = Math.max(player.vy, -45.0);
        } else {
          let up = (keys.Space ? 1 : 0) - (keys.ShiftLeft ? 1 : 0) - (keys.ShiftRight ? 1 : 0);
          const targetVY = up * FLY_SPEED;
          const tV = Math.min(1.0, 10.0 * dt);
          player.vy += (targetVY - player.vy) * tV;
        }

        // X 軸
        let nx = player.x + player.vx * dt;
        if (!collide(nx, player.y, player.z)) {
          player.x = nx;
        } else {
          player.vx = 0;
        }

        // Z 軸
        let nz = player.z + player.vz * dt;
        if (!collide(player.x, player.y, nz)) {
          player.z = nz;
        } else {
          player.vz = 0;
        }

        // Y 軸
        const ny = player.y + player.vy * dt;
        if (!collide(player.x, ny, player.z)) {
          player.y = ny;
        } else {
          if (player.vy < 0) grounded = true;
          player.vy = 0;
        }

        // 接地判定
        if (!fly) {
          grounded = collide(player.x, player.y - 0.02, player.z);
        } else {
          grounded = false;
        }
      }

      function updateCamera() {
        camera.position.set(player.x, player.y + EYE_H, player.z);
        camera.rotation.set(pitch, yaw, 0, 'YXZ');
      }

      function updateHighlight() {
        camera.getWorldDirection(rayDir);
        const hit = raycastBlock(camera.position, rayDir, 8.0);

        if (hit) {
          highlight.position.set(hit.x + 0.5, hit.y + 0.5, hit.z + 0.5);
          highlight.visible = true;
        } else {
          highlight.visible = false;
        }
      }

      function updateHUD() {
        const mode = fly ? '飛行' : '通常';
        coordsEl.innerHTML =
          `X ${player.x.toFixed(1)} / Y ${player.y.toFixed(1)} / Z ${player.z.toFixed(1)}<br>` +
          `ブロック: ${BLOCKS[HOTBAR[selected]].name} (${selected + 1}) / ${mode}`;
      }

      // --------------------------------------------------
      // リサイズ
      // --------------------------------------------------
      window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
      });

      // --------------------------------------------------
      // 初期化
      // --------------------------------------------------
      generateWorld();

      const spawnX = Math.floor(W / 2);
      const spawnZ = Math.floor(D / 2);
      player.x = spawnX + 0.5;
      player.z = spawnZ + 0.5;
      player.y = topY(spawnX, spawnZ) + 1.05;

      const clock = new THREE.Clock();

      function animate() {
        requestAnimationFrame(animate);

        const dt = Math.min(0.05, clock.getDelta());

        updatePlayer(dt);
        updateCamera();
        updateHighlight();
        updateHUD();

        renderer.render(scene, camera);
      }

      animate();
    })();
  </script>
</body>
</html>
```