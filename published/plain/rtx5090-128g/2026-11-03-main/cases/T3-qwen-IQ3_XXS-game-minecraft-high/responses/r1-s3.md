そのまま保存して開けば動く、Three.js を使った「マイクラ風 3D 箱庭ゲーム」を作ります。

## 使い方
1. 下のコードを `index.html` として保存  
2. ブラウザで開く  
3. 画面をクリックするとマウス視点操作が開始されます  

操作：
- `WASD` : 移動  
- `Space` : ジャンプ  
- 左クリック : ブロックを壊す  
- 右クリック : ブロックを置く  
- `1〜6` : ブロック切り替え  
- `Shift` : 走る  
- `Esc` : マウス視点解除  

---

```html
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>マイクラ風3D箱庭ゲーム</title>
<style>
  * {
    box-sizing: border-box;
  }

  html, body {
    margin: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
    background: #111;
    font-family: sans-serif;
    color: #fff;
  }

  canvas {
    display: block;
  }

  #overlay {
    position: fixed;
    inset: 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background: rgba(0, 0, 0, 0.65);
    z-index: 20;
    text-align: center;
    cursor: pointer;
  }

  #overlay h1 {
    margin-bottom: 12px;
    font-size: 2rem;
  }

  #overlay p {
    margin: 6px 0;
    font-size: 1rem;
    color: #ddd;
  }

  #crosshair {
    position: fixed;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    pointer-events: none;
    z-index: 10;
    font-size: 28px;
    color: white;
    text-shadow: 0 0 4px black;
  }

  #hud {
    position: fixed;
    left: 50%;
    bottom: 16px;
    transform: translateX(-50%);
    display: flex;
    gap: 6px;
    z-index: 10;
  }

  .slot {
    width: 52px;
    height: 52px;
    border: 2px solid rgba(255,255,255,0.55);
    background: rgba(0,0,0,0.35);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    text-align: center;
    padding: 2px;
  }

  .slot.selected {
    border-color: #fff;
    background: rgba(255,255,255,0.18);
  }

  #status {
    position: fixed;
    top: 12px;
    left: 12px;
    z-index: 10;
    background: rgba(0,0,0,0.45);
    padding: 8px 10px;
    font-size: 0.85rem;
  }
</style>
</head>
<body>
  <div id="overlay">
    <h1>マイクラ風3D箱庭</h1>
    <p>クリックして開始</p>
    <p>WASD:移動 / Space:ジャンプ / Shift:走る</p>
    <p>左クリック:破壊 / 右クリック:設置 / 1〜6:ブロック変更</p>
  </div>

  <div id="crosshair">+</div>

  <div id="hud"></div>

  <div id="status">
    Select: 草 / FPS: --
  </div>

  <script type="importmap">
  {
    "imports": {
      "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js"
    }
  }
  </script>

  <script type="module">
    import * as THREE from 'three';

    // ===== 基本 =====
    const SIZE = 64;
    const MAX_Y = 48;
    const CHUNK = 16;

    const HW = 0.30;       // 幅の半分
    const PH = 1.80;       // 高さ

    const GRAVITY = -28.0;
    const JUMP = 8.0;
    const SPEED = 5.2;
    const RUN_SPEED = 8.0;
    const REACH = 7.0;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x87ceeb);
    scene.fog = new THREE.Fog(0x87ceeb, 30, 110);

    const camera = new THREE.PerspectiveCamera(
      75,
      innerWidth / innerHeight,
      0.1,
      1000
    );
    camera.rotation.order = 'YXZ';

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(innerWidth, innerHeight);
    renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
    document.body.appendChild(renderer.domElement);

    // ===== ライト =====
    const hemiLight = new THREE.HemisphereLight(0xffffff, 0x445566, 1.1);
    scene.add(hemiLight);

    const sunLight = new THREE.DirectionalLight(0xffffff, 0.9);
    sunLight.position.set(25, 60, 15);
    scene.add(sunLight);

    // ===== ブロック定義 =====
    const BLOCKS = {
      1: { name: '草', top: 0x67a43a, side: 0x7c5b38, bottom: 0x69492b },
      2: { name: '土', top: 0x825f3c, side: 0x7a5537, bottom: 0x664631 },
      3: { name: '石', top: 0x9d9d9d, side: 0x8c8c8c, bottom: 0x787878 },
      4: { name: '砂', top: 0xe1d29a, side: 0xdac98f, bottom: 0xc6b47f },
      5: { name: '木', top: 0xa47648, side: 0x805737, bottom: 0xa47648 },
      6: { name: '葉', top: 0x2f8434, side: 0x286d2c, bottom: 0x1f5222 },
      7: { name: '岩盤', top: 0x2f2f2f, side: 0x252525, bottom: 0x252525 }
    };

    const HOTBAR = [1, 2, 3, 4, 5, 6];
    let selected = 0;

    // ===== ブロックマップ =====
    const blocks = new Map();

    function pack(x, y, z) {
      return (x << 16) | (z << 8) | y;
    }

    function inWorld(x, y, z) {
      return (
        x >= 0 && x < SIZE &&
        z >= 0 && z < SIZE &&
        y >= 0 && y < MAX_Y
      );
    }

    function getBlock(x, y, z) {
      if (!inWorld(x, y, z)) return null;
      return blocks.get(pack(x, y, z)) || null;
    }

    function hasBlock(x, y, z) {
      if (!inWorld(x, y, z)) return false;
      return blocks.has(pack(x, y, z));
    }

    // ===== チャンク再構築管理 =====
    const dirtyChunks = new Set();
    const chunkMeshes = new Map();
    const NUM_CHUNKS = SIZE / CHUNK;

    function chunkKey(cx, cz) {
      return `${cx},${cz}`;
    }

    function markDirtyChunks(x, z) {
      const cx = Math.floor(x / CHUNK);
      const cz = Math.floor(z / CHUNK);

      for (let dx = -1; dx <= 1; dx++) {
        for (let dz = -1; dz <= 1; dz++) {
          const cx2 = cx + dx;
          const cz2 = cz + dz;

          if (
            cx2 >= 0 && cx2 < NUM_CHUNKS &&
            cz2 >= 0 && cz2 < NUM_CHUNKS
          ) {
            dirtyChunks.add(chunkKey(cx2, cz2));
          }
        }
      }
    }

    function setBlock(x, y, z, type) {
      if (!inWorld(x, y, z)) return false;

      const k = pack(x, y, z);

      if (type === null) {
        if (!blocks.has(k)) return false;
        blocks.delete(k);
        markDirtyChunks(x, z);
        return true;
      }

      if (blocks.get(k) === type) return false;

      blocks.set(k, type);
      markDirtyChunks(x, z);
      return true;
    }

    // ===== 地形生成 =====
    function heightAt(x, z) {
      let h =
        24 +
        Math.sin(x * 0.12) * 4 +
        Math.cos(z * 0.14) * 4 +
        Math.sin((x + z) * 0.11) * 3 +
        Math.cos((x - z) * 0.09) * 2;

      return Math.max(4, Math.min(32, Math.floor(h)));
    }

    function addBlock(x, y, z, type) {
      if (!inWorld(x, y, z)) return;
      blocks.set(pack(x, y, z), type);
    }

    function makeTree(x, z, h) {
      if (h + 5 >= MAX_Y) return;

      const trunkHeight = 3 + Math.floor(Math.random() * 2);

      // 幹
      for (let i = 1; i <= trunkHeight; i++) {
        addBlock(x, h + i, z, 5);
      }

      const topY = h + trunkHeight;

      // 葉
      for (let dy = -2; dy <= 1; dy++) {
        const ly = topY + dy;

        for (let dx = -2; dx <= 2; dx++) {
          for (let dz = -2; dz <= 2; dz++) {
            if (dx === 0 && dz === 0 && dy < 0) continue;

            if (ly > topY && (Math.abs(dx) > 1 || Math.abs(dz) > 1)) continue;

            const bx = x + dx;
            const bz = z + dz;

            if (!hasBlock(bx, ly, bz)) {
              addBlock(bx, ly, bz, 6);
            }
          }
        }
      }
    }

    function generateWorld() {
      for (let z = 0; z < SIZE; z++) {
        for (let x = 0; x < SIZE; x++) {
          const h = heightAt(x, z);

          for (let y = 0; y <= h; y++) {
            let type;

            if (y === 0) {
              type = 7; // 岩盤
            } else if (y === h) {
              type = 1; // 草
            } else if (y > h - 4) {
              type = 2; // 土
            } else {
              type = 3; // 石
            }

            addBlock(x, y, z, type);
          }
        }
      }

      // 木を配置
      for (let i = 0; i < 12; i++) {
        const x = Math.floor(Math.random() * (SIZE - 8)) + 4;
        const z = Math.floor(Math.random() * (SIZE - 8)) + 4;
        const h = heightAt(x, z);

        if (getBlock(x, h, z) === 1) {
          makeTree(x, z, h);
        }
      }
    }

    // ===== チャンクメッシュ生成 =====
    const FACE_NORMALS = [
      [1, 0, 0],
      [-1, 0, 0],
      [0, 1, 0],
      [0, -1, 0],
      [0, 0, 1],
      [0, 0, -1]
    ];

    const FACE_VERTICES = [
      // +X
      [
        [1, 0, 0],
        [1, 1, 0],
        [1, 1, 1],
        [1, 0, 1]
      ],
      // -X
      [
        [0, 0, 1],
        [0, 1, 1],
        [0, 1, 0],
        [0, 0, 0]
      ],
      // +Y
      [
        [0, 1, 1],
        [1, 1, 1],
        [1, 1, 0],
        [0, 1, 0]
      ],
      // -Y
      [
        [0, 0, 0],
        [1, 0, 0],
        [1, 0, 1],
        [0, 0, 1]
      ],
      // +Z
      [
        [0, 0, 1],
        [1, 0, 1],
        [1, 1, 1],
        [0, 1, 1]
      ],
      // -Z
      [
        [1, 0, 0],
        [0, 0, 0],
        [0, 1, 0],
        [1, 1, 0]
      ]
    ];

    function hexRGB(hex) {
      return [
        ((hex >> 16) & 255) / 255,
        ((hex >> 8) & 255) / 255,
        (hex & 255) / 255
      ];
    }

    function faceColor(type, ny, x, y, z) {
      const b = BLOCKS[type];
      if (!b) return [1, 1, 1];

      let hex = b.side;
      if (ny === 1) hex = b.top;
      else if (ny === -1) hex = b.bottom;

      let rgb = hexRGB(hex);

      // 少しだけムラを出してブロックっぽさを出す
      const h = ((x * 73856093) ^ (y * 19349663) ^ (z * 83492791)) & 1023;
      const shade = 0.93 + (h / 1023) * 0.12;

      if (ny !== 1) {
        rgb = [rgb[0] * shade * 0.92, rgb[1] * shade * 0.92, rgb[2] * shade * 0.92];
      } else {
        rgb = [rgb[0] * shade, rgb[1] * shade, rgb[2] * shade];
      }

      return rgb;
    }

    function buildChunk(cx, cz) {
      const key = chunkKey(cx, cz);

      const old = chunkMeshes.get(key);
      if (old) {
        scene.remove(old);
        old.geometry.dispose();
        old.material.dispose();
      }

      const positions = [];
      const normals = [];
      const colors = [];

      const xStart = cx * CHUNK;
      const zStart = cz * CHUNK;

      for (let x = xStart; x < xStart + CHUNK; x++) {
        for (let z = zStart; z < zStart + CHUNK; z++) {
          for (let y = 0; y < MAX_Y; y++) {
            const type = getBlock(x, y, z);
            if (!type) continue;

            for (let f = 0; f < 6; f++) {
              const n = FACE_NORMALS[f];
              const nx = n[0];
              const ny = n[1];
              const nz = n[2];

              if (hasBlock(x + nx, y + ny, z + nz)) continue;

              const c = faceColor(type, ny, x, y, z);
              const verts = FACE_VERTICES[f];

              const p0 = verts[0];
              const p1 = verts[1];
              const p2 = verts[2];
              const p3 = verts[3];

              // triangle 1: p0, p1, p2
              positions.push(x + p0[0], y + p0[1], z + p0[2]);
              normals.push(nx, ny, nz);
              colors.push(c[0], c[1], c[2]);

              positions.push(x + p1[0], y + p1[1], z + p1[2]);
              normals.push(nx, ny, nz);
              colors.push(c[0], c[1], c[2]);

              positions.push(x + p2[0], y + p2[1], z + p2[2]);
              normals.push(nx, ny, nz);
              colors.push(c[0], c[1], c[2]);

              // triangle 2: p0, p2, p3
              positions.push(x + p0[0], y + p0[1], z + p0[2]);
              normals.push(nx, ny, nz);
              colors.push(c[0], c[1], c[2]);

              positions.push(x + p2[0], y + p2[1], z + p2[2]);
              normals.push(nx, ny, nz);
              colors.push(c[0], c[1], c[2]);

              positions.push(x + p3[0], y + p3[1], z + p3[2]);
              normals.push(nx, ny, nz);
              colors.push(c[0], c[1], c[2]);
            }
          }
        }
      }

      if (positions.length === 0) return;

      const geometry = new THREE.BufferGeometry();
      geometry.setAttribute(
        'position',
        new THREE.BufferAttribute(new Float32Array(positions), 3)
      );
      geometry.setAttribute(
        'normal',
        new THREE.BufferAttribute(new Float32Array(normals), 3)
      );
      geometry.setAttribute(
        'color',
        new THREE.BufferAttribute(new Float32Array(colors), 3)
      );

      const material = new THREE.MeshLambertMaterial({
        vertexColors: true,
        side: THREE.FrontSide
      });

      const mesh = new THREE.Mesh(geometry, material);
      scene.add(mesh);

      chunkMeshes.set(key, mesh);
    }

    function rebuildDirtyChunks() {
      for (const key of dirtyChunks) {
        const parts = key.split(',');
        const cx = parseInt(parts[0], 10);
        const cz = parseInt(parts[1], 10);
        buildChunk(cx, cz);
      }

      dirtyChunks.clear();
    }

    generateWorld();

    for (let cx = 0; cx < NUM_CHUNKS; cx++) {
      for (let cz = 0; cz < NUM_CHUNKS; cz++) {
        buildChunk(cx, cz);
      }
    }

    // ===== プレイヤー =====
    const spawnX = SIZE / 2;
    const spawnZ = SIZE / 2;
    const spawnY = heightAt(spawnX, spawnZ) + 1;

    const player = {
      x: spawnX,
      y: spawnY,
      z: spawnZ
    };

    let vx = 0;
    let vy = 0;
    let vz = 0;

    let yaw = 0;
    let pitch = 0;

    let grounded = false;

    const keys = {
      w: false,
      a: false,
      s: false,
      d: false,
      space: false,
      shift: false
    };

    function collides(px, py, pz) {
      const minX = px - HW;
      const maxX = px + HW;
      const minZ = pz - HW;
      const maxZ = pz + HW;

      // 世界の端は壁にする
      if (minX < -1e-6 || maxX > SIZE + 1e-6) return true;
      if (minZ < -1e-6 || maxZ > SIZE + 1e-6) return true;

      const minY = py;
      const maxY = py + PH;

      const x0 = Math.floor(minX);
      const x1 = Math.ceil(maxX);
      const y0 = Math.floor(minY);
      const y1 = Math.ceil(maxY);
      const z0 = Math.floor(minZ);
      const z1 = Math.ceil(maxZ);

      for (let x = x0; x < x1; x++) {
        for (let y = y0; y < y1; y++) {
          for (let z = z0; z < z1; z++) {
            if (hasBlock(x, y, z)) {
              return true;
            }
          }
        }
      }

      return false;
    }

    function isGrounded() {
      return collides(player.x, player.y - 0.01, player.z);
    }

    function blocksCollideWithPlayer(x, y, z) {
      const minX = x;
      const maxX = x + 1;
      const minY = y;
      const maxY = y + 1;
      const minZ = z;
      const maxZ = z + 1;

      return (
        player.x + HW > minX &&
        player.x - HW < maxX &&
        player.z + HW > minZ &&
        player.z - HW < maxZ &&
        player.y + PH > minY &&
        player.y < maxY
      );
    }

    // ===== レイキャスト（ブロック選択） =====
    function raycast(origin, direction, maxDist) {
      let x = Math.floor(origin.x);
      let y = Math.floor(origin.y);
      let z = Math.floor(origin.z);

      const stepX = direction.x > 0 ? 1 : -1;
      const stepY = direction.y > 0 ? 1 : -1;
      const stepZ = direction.z > 0 ? 1 : -1;

      const tDeltaX = direction.x !== 0 ? Math.abs(1 / direction.x) : Infinity;
      const tDeltaY = direction.y !== 0 ? Math.abs(1 / direction.y) : Infinity;
      const tDeltaZ = direction.z !== 0 ? Math.abs(1 / direction.z) : Infinity;

      let tMaxX = Infinity;
      let tMaxY = Infinity;
      let tMaxZ = Infinity;

      if (direction.x > 0) {
        tMaxX = ((x + 1 - origin.x) / direction.x);
      } else if (direction.x < 0) {
        tMaxX = ((origin.x - x) / -direction.x);
      }

      if (direction.y > 0) {
        tMaxY = ((y + 1 - origin.y) / direction.y);
      } else if (direction.y < 0) {
        tMaxY = ((origin.y - y) / -direction.y);
      }

      if (direction.z > 0) {
        tMaxZ = ((z + 1 - origin.z) / direction.z);
      } else if (direction.z < 0) {
        tMaxZ = ((origin.z - z) / -direction.z);
      }

      let currentNormal = null;

      // レイの始点から maxDist まで
      for (let i = 0; i < 1200; i++) {
        if (hasBlock(x, y, z)) {
          const normal = currentNormal || [0, 0, 0];
          return {
            x,
            y,
            z,
            nx: normal[0],
            ny: normal[1],
            nz: normal[2]
          };
        }

        const nextT = Math.min(tMaxX, tMaxY, tMaxZ);
        if (nextT > maxDist) return null;

        if (tMaxX < tMaxY && tMaxX < tMaxZ) {
          x += stepX;
          tMaxX += tDeltaX;
          currentNormal = [-stepX, 0, 0];
        } else if (tMaxY < tMaxX && tMaxY < tMaxZ) {
          y += stepY;
          tMaxY += tDeltaY;
          currentNormal = [0, -stepY, 0];
        } else {
          z += stepZ;
          tMaxZ += tDeltaZ;
          currentNormal = [0, 0, -stepZ];
        }
      }

      return null;
    }

    // ===== 選択ブロックのハイライト =====
    const highlightGeometry = new THREE.BoxGeometry(1.003, 1.003, 1.003);
    const highlightMaterial = new THREE.LineBasicMaterial({
      color: 0x000000
    });

    const highlightEdges = new THREE.EdgesGeometry(highlightGeometry);
    const highlightBox = new THREE.LineSegments(highlightEdges, highlightMaterial);
    highlightBox.visible = false;
    scene.add(highlightBox);

    // ===== 入力 =====
    document.addEventListener('keydown', (e) => {
      const k = e.key.toLowerCase();

      if (k === 'w') keys.w = true;
      if (k === 'a') keys.a = true;
      if (k === 's') keys.s = true;
      if (k === 'd') keys.d = true;
      if (k === ' ') keys.space = true;
      if (k === 'shift') keys.shift = true;

      const n = parseInt(k, 10);
      if (n >= 1 && n <= HOTBAR.length) {
        selected = n - 1;
        updateHUD();
      }
    });

    document.addEventListener('keyup', (e) => {
      const k = e.key.toLowerCase();

      if (k === 'w') keys.w = false;
      if (k === 'a') keys.a = false;
      if (k === 's') keys.s = false;
      if (k === 'd') keys.d = false;
      if (k === ' ') keys.space = false;
      if (k === 'shift') keys.shift = false;
    });

    document.addEventListener('contextmenu', (e) => {
      e.preventDefault();
    });

    document.addEventListener('mousedown', (e) => {
      if (!document.pointerLockElement) return;

      if (e.button === 0) {
        breakBlock();
      } else if (e.button === 2) {
        placeBlock();
      }
    });

    // ===== 視点 =====
    let pointerLocked = false;

    const overlay = document.getElementById('overlay');

    overlay.addEventListener('click', () => {
      renderer.domElement.requestPointerLock();
    });

    document.addEventListener('pointerlockchange', () => {
      pointerLocked = document.pointerLockElement === renderer.domElement;

      if (pointerLocked) {
        overlay.style.display = 'none';
      } else {
        overlay.style.display = 'flex';
      }
    });

    document.addEventListener('mousemove', (e) => {
      if (!pointerLocked) return;

      const sensitivity = 0.0022;

      yaw -= e.movementX * sensitivity;
      pitch -= e.movementY * sensitivity;

      pitch = Math.max(-Math.PI / 2 + 0.01, Math.min(Math.PI / 2 - 0.01, pitch));
    });

    // ===== ブロックを壊す／置く =====
    function getCurrentTarget() {
      const dir = new THREE.Vector3();
      camera.getWorldDirection(dir);

      return raycast(camera.position, dir, REACH);
    }

    function breakBlock() {
      const hit = getCurrentTarget();
      if (!hit) return;

      const type = getBlock(hit.x, hit.y, hit.z);
      if (!type) return;

      // 岩盤は壊せない
      if (type === 7) return;

      setBlock(hit.x, hit.y, hit.z, null);
    }

    function placeBlock() {
      const hit = getCurrentTarget();
      if (!hit) return;

      const type = HOTBAR[selected];
      if (!type) return;

      const x = hit.x + hit.nx;
      const y = hit.y + hit.ny;
      const z = hit.z + hit.nz;

      if (!inWorld(x, y, z)) return;
      if (hasBlock(x, y, z)) return;

      // 自分の体と重なる位置には置けない
      if (blocksCollideWithPlayer(x, y, z)) return;

      setBlock(x, y, z, type);
    }

    // ===== HUD =====
    const hud = document.getElementById('hud');
    const status = document.getElementById('status');

    function makeColorCSS(hex) {
      const r = (hex >> 16) & 255;
      const g = (hex >> 8) & 255;
      const b = hex & 255;
      return `rgb(${r},${g},${b})`;
    }

    function buildHUD() {
      hud.innerHTML = '';

      HOTBAR.forEach((id, i) => {
        const b = BLOCKS[id];

        const slot = document.createElement('div');
        slot.className = 'slot';
        slot.style.background = `linear-gradient(135deg, ${makeColorCSS(b.top)} 0%, ${makeColorCSS(b.side)} 55%, #222 100%)`;
        slot.textContent = `${i + 1}\n${b.name}`;

        hud.appendChild(slot);
      });

      updateHUD();
    }

    function updateHUD() {
      const slots = hud.querySelectorAll('.slot');
      slots.forEach((slot, i) => {
        slot.classList.toggle('selected', i === selected);
      });
    }

    buildHUD();

    // ===== 更新 =====
    const clock = new THREE.Clock();

    function updateCamera() {
      camera.rotation.set(pitch, yaw, 0);
      camera.position.set(player.x, player.y + 1.62, player.z);
    }

    function updateMovement(dt) {
      grounded = isGrounded();

      const forwardX = -Math.sin(yaw);
      const forwardZ = -Math.cos(yaw);

      const rightX = Math.cos(yaw);
      const rightZ = -Math.sin(yaw);

      let moveX = 0;
      let moveZ = 0;

      if (keys.w) {
        moveX += forwardX;
        moveZ += forwardZ;
      }

      if (keys.s) {
        moveX -= forwardX;
        moveZ -= forwardZ;
      }

      if (keys.a) {
        moveX -= rightX;
        moveZ -= rightZ;
      }

      if (keys.d) {
        moveX += rightX;
        moveZ += rightZ;
      }

      const len = Math.hypot(moveX, moveZ);
      if (len > 0) {
        moveX /= len;
        moveZ /= len;
      }

      const speed = keys.shift ? RUN_SPEED : SPEED;

      vx = moveX * speed;
      vz = moveZ * speed;

      if (keys.space && grounded) {
        vy = JUMP;
        grounded = false;
      }

      // 水平方向
      const oldX = player.x;
      const oldZ = player.z;

      player.x += vx * dt;
      if (collides(player.x, player.y, player.z)) {
        player.x = oldX;
        vx = 0;
      }

      player.z += vz * dt;
      if (collides(player.x, player.y, player.z)) {
        player.z = oldZ;
        vz = 0;
      }

      // 垂直方向
      if (grounded) {
        if (vy < 0) vy = 0;
      } else {
        vy += GRAVITY * dt;
        vy = Math.max(vy, -45);
      }

      const oldY = player.y;

      player.y += vy * dt;

      if (collides(player.x, player.y, player.z)) {
        player.y = oldY;

        if (vy < 0) {
          grounded = true;
        }

        vy = 0;
      }

      // 落下死防止：底面を貫通したらスポーンへ戻す
      if (player.y < -30) {
        player.x = spawnX;
        player.y = spawnY;
        player.z = spawnZ;
        vx = vy = vz = 0;
      }

      // 世界端から出ないよう強制補正
      player.x = Math.max(HW, Math.min(SIZE - HW, player.x));
      player.z = Math.max(HW, Math.min(SIZE - HW, player.z));
    }

    function updateHighlight() {
      const hit = getCurrentTarget();

      if (!hit) {
        highlightBox.visible = false;
        return;
      }

      highlightBox.visible = true;
      highlightBox.position.set(hit.x + 0.5, hit.y + 0.5, hit.z + 0.5);
    }

    let lastFrame = performance.now();

    function animate() {
      requestAnimationFrame(animate);

      const now = performance.now();
      let dt = (now - lastFrame) / 1000;
      lastFrame = now;

      dt = Math.min(dt, 0.05);

      if (pointerLocked) {
        updateMovement(dt);
      }

      updateCamera();
      updateHighlight();
      rebuildDirtyChunks();

      const fps = Math.round(1000 / Math.max(1, now - clock.getElapsedTime() * 1000));
      const name = BLOCKS[HOTBAR[selected]].name;
      status.textContent = `Select: ${name} / FPS: ${Math.round(1 / Math.max(dt, 0.001))}`;

      renderer.render(scene, camera);
    }

    animate();

    // ===== リサイズ =====
    window.addEventListener('resize', () => {
      camera.aspect = innerWidth / innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(innerWidth, innerHeight);
    });
  </script>
</body>
</html>
```

---

このコードは、かなり「マイクラらしさ」を狙った自作エンジン風になっています。

### このコードでできていること
- 3D 体素ブロック世界
- 自動地形生成
- 木生成
- WASD 移動
- ジャンプ / 重力 / 衝突判定
- ブロック破壊 / 設置
- 視点ポインターロック
- 選択ブロックのハイライト
- ホットバー UI
- 岩盤で底抜け防止

---

必要なら、次はさらに拡張して、

- クラフト風 UI
- 水 / 溶岩
- スカイブロック
- 洞窟生成
- 音
- セーブ/ロード
- スマホ操作
- パーティクル破壊演出

なども追加できます。