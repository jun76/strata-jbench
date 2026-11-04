了解。ブラウザだけで遊べる「マイクラ風3D箱庭ゲーム」の単一HTMLを作ります。  
Three.jsを使い、ブロック破壊/設置、地形生成、木、一人称視点、重力、衝突判定などを入れてあります。

## 使い方

1. 下のコードを `voxel-game.html` として保存  
2. そのHTMLをブラウザで開く  
3. 画面をクリックしてマウスロック  
4. 遊ぶ

## 操作方法

- `W/A/S/D` : 移動
- `Space` : ジャンプ
- `Shift` : ダッシュ
- マウス : 視点移動
- 左クリック : ブロック破壊
- 右クリック : ブロック設置
- `1`〜`6` : 設置するブロック選択
- `Esc` : マウスロック解除

---

## コード

```html
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>ボクセル箱庭</title>
<style>
  html, body {
    margin: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
    background: #000;
    font-family: system-ui, sans-serif;
  }

  canvas {
    display: block;
  }

  #ui {
    position: fixed;
    inset: 0;
    pointer-events: none;
    color: #fff;
    text-shadow: 0 0 4px rgba(0, 0, 0, 0.9);
    user-select: none;
  }

  #info {
    position: absolute;
    top: 12px;
    left: 12px;
    padding: 10px 14px;
    border-radius: 12px;
    background: rgba(0, 0, 0, 0.45);
    font-size: 13px;
    line-height: 1.55;
    max-width: 340px;
  }

  #crosshair {
    position: absolute;
    left: 50%;
    top: 50%;
    width: 22px;
    height: 22px;
    transform: translate(-50%, -50%);
    opacity: 0.85;
  }

  #crosshair::before,
  #crosshair::after {
    content: "";
    position: absolute;
    background: #fff;
    box-shadow: 0 0 4px rgba(0, 0, 0, 0.8);
  }

  #crosshair::before {
    width: 18px;
    height: 2px;
    left: 2px;
    top: 10px;
  }

  #crosshair::after {
    width: 2px;
    height: 18px;
    left: 10px;
    top: 2px;
  }

  #hotbar {
    position: absolute;
    bottom: 18px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: 8px;
    pointer-events: auto;
  }

  .slot {
    width: 58px;
    height: 58px;
    box-sizing: border-box;
    border: 3px solid rgba(255, 255, 255, 0.45);
    border-radius: 10px;
    background: rgba(0, 0, 0, 0.38);
    color: #fff;
    cursor: pointer;
    position: relative;
    overflow: hidden;
  }

  .slot.selected {
    border-color: #fff;
    box-shadow: 0 0 16px rgba(255, 255, 255, 0.55);
    background: rgba(255, 255, 255, 0.18);
  }

  .slot .color {
    position: absolute;
    inset: 7px 7px 18px 7px;
    border-radius: 7px;
    border: 1px solid rgba(0, 0, 0, 0.35);
  }

  .slot .name {
    position: absolute;
    bottom: 3px;
    left: 0;
    right: 0;
    text-align: center;
    font-size: 10px;
    line-height: 1;
  }

  .slot .num {
    position: absolute;
    top: 2px;
    left: 5px;
    font-size: 11px;
    opacity: 0.95;
  }

  #overlay {
    position: fixed;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(0, 0, 0, 0.62);
    color: #fff;
    text-align: center;
    cursor: pointer;
  }

  #overlay .panel {
    padding: 24px 30px;
    border-radius: 18px;
    background: rgba(0, 0, 0, 0.45);
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
  }

  #overlay h1 {
    margin: 0 0 12px;
    font-size: 28px;
    font-weight: 700;
  }

  #overlay p {
    margin: 6px 0;
    font-size: 15px;
    opacity: 0.92;
  }

  .hidden {
    display: none !important;
  }
</style>
</head>
<body>
  <div id="ui">
    <div id="info">
      <strong>操作方法</strong><br />
      W/A/S/D : 移動<br />
      Space : ジャンプ<br />
      Shift : ダッシュ<br />
      左クリック : 破壊<br />
      右クリック : 設置<br />
      1〜6 : ブロック選択<br />
      Esc : 解放
    </div>

    <div id="crosshair"></div>
    <div id="hotbar"></div>
  </div>

  <div id="overlay">
    <div class="panel">
      <h1>ボクセル箱庭</h1>
      <p>クリックしてゲーム開始</p>
      <p>マイクラ風の一人称3Dブロックゲーム</p>
    </div>
  </div>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script>
    // ============================================================
    // 定数・設定
    // ============================================================
    const WORLD_X = 32;
    const WORLD_Y = 32;
    const WORLD_Z = 32;
    const REACH_DISTANCE = 6;

    const TYPES = [
      null,
      { name: "草", color: 0x67b55e, place: true },
      { name: "土", color: 0x8d5a2f, place: true },
      { name: "石", color: 0x8f8f8f, place: true },
      { name: "木", color: 0xa06f3c, place: true },
      { name: "葉", color: 0x3f8f46, place: true },
      { name: "砂", color: 0xd8c28a, place: true },
      { name: "岩盤", color: 0x444444, place: false }
    ];

    const PLACEABLE = [];
    for (let i = 1; i < TYPES.length; i++) {
      if (TYPES[i].place) PLACEABLE.push(i);
    }

    let selectedBlock = PLACEABLE[0];

    // ============================================================
    // Three.js 初期化
    // ============================================================
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x87ceeb);
    scene.fog = new THREE.Fog(0x87ceeb, 30, 90);

    const camera = new THREE.PerspectiveCamera(
      75,
      window.innerWidth / window.innerHeight,
      0.1,
      300
    );

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    document.body.appendChild(renderer.domElement);

    const ambient = new THREE.AmbientLight(0xffffff, 0.62);
    scene.add(ambient);

    const sun = new THREE.DirectionalLight(0xffffff, 0.85);
    sun.position.set(70, 110, 45);
    sun.castShadow = true;
    sun.shadow.mapSize.set(1024, 1024);
    sun.shadow.camera.left = -50;
    sun.shadow.camera.right = 50;
    sun.shadow.camera.top = 50;
    sun.shadow.camera.bottom = -50;
    sun.shadow.camera.near = 1;
    sun.shadow.camera.far = 220;
    scene.add(sun);
    scene.add(sun.target);

    const hemi = new THREE.HemisphereLight(0xbfd9ff, 0x8a7355, 0.25);
    scene.add(hemi);

    // ============================================================
    // ブロックワールド
    // ============================================================
    const blocks = new Map();

    function blockKey(x, y, z) {
      return x + y * WORLD_X + z * WORLD_X * WORLD_Y;
    }

    function inBounds(x, y, z) {
      return (
        x >= 0 && x < WORLD_X &&
        y >= 0 && y < WORLD_Y &&
        z >= 0 && z < WORLD_Z
      );
    }

    function getBlock(x, y, z) {
      if (!inBounds(x, y, z)) return 0;
      return blocks.get(blockKey(x, y, z)) || 0;
    }

    function setBlockDirect(x, y, z, type) {
      if (!inBounds(x, y, z)) return;
      const k = blockKey(x, y, z);
      if (type === 0) blocks.delete(k);
      else blocks.set(k, type);
    }

    // ============================================================
    // 地形生成
    // ============================================================
    function mulberry32(seed) {
      return function () {
        let t = (seed += 0x6d2b79f5);
        t = Math.imul(t ^ (t >>> 15), t | 1);
        t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
      };
    }

    const rand = mulberry32(1337);

    const heights = new Uint8Array(WORLD_X * WORLD_Z);

    function heightIndex(x, z) {
      return x + z * WORLD_X;
    }

    function terrainHeight(x, z) {
      const h =
        12 +
        3.5 * Math.sin(x * 0.17) +
        3.5 * Math.cos(z * 0.15) +
        2.5 * Math.sin((x + z) * 0.23) +
        1.5 * Math.cos((x - z) * 0.19);

      return Math.max(1, Math.min(WORLD_Y - 10, Math.floor(h)));
    }

    function generateTerrain() {
      for (let z = 0; z < WORLD_Z; z++) {
        for (let x = 0; x < WORLD_X; x++) {
          const h = terrainHeight(x, z);
          heights[heightIndex(x, z)] = h;

          for (let y = 0; y <= h; y++) {
            let type;

            if (y === 0) {
              type = 7; // 岩盤
            } else if (y === h) {
              type = h <= 4 ? 6 : 1; // 砂 or 草
            } else if (y >= h - 2) {
              type = 2; // 土
            } else {
              type = 3; // 石
            }

            blocks.set(blockKey(x, y, z), type);
          }
        }
      }
    }

    function canPlaceTree(x, z) {
      const h = heights[heightIndex(x, z)];
      if (getBlock(x, h, z) !== 1) return false; // 草の上だけ
      if (h <= 4) return false; // 砂地には植えない

      // 中央付近は spawn 用に残す
      const cx = Math.floor(WORLD_X / 2);
      const cz = Math.floor(WORLD_Z / 2);
      if (Math.abs(x - cx) <= 3 && Math.abs(z - cz) <= 3) return false;

      return true;
    }

    function placeTree(x, z) {
      const ground = heights[heightIndex(x, z)];
      if (getBlock(x, ground, z) !== 1) return;

      const trunkHeight = 3 + Math.floor(rand() * 2);
      const topY = ground + trunkHeight;

      // 幹
      for (let y = ground + 1; y <= topY; y++) {
        setBlockDirect(x, y, z, 4);
      }

      // 葉っぱ
      for (let dy = -1; dy <= 1; dy++) {
        const ly = topY + dy;
        if (!inBounds(x, ly, z)) continue;

        for (let dx = -2; dx <= 2; dx++) {
          for (let dz = -2; dz <= 2; dz++) {
            const lx = x + dx;
            const lz = z + dz;

            if (!inBounds(lx, ly, lz)) continue;

            // 幹の位置は消さない
            if (dx === 0 && dz === 0 && dy <= 0) continue;

            // 丸っぽい形にする
            let dist;
            if (dy === 1) {
              dist = Math.abs(dx) + Math.abs(dz);
            } else {
              dist = Math.abs(dx) + Math.abs(dz) + Math.abs(dy);
            }

            if (dist > 3) continue;
            if (Math.abs(dx) === 2 && Math.abs(dz) === 2) continue;

            if (getBlock(lx, ly, lz) === 0) {
              setBlockDirect(lx, ly, lz, 5);
            }
          }
        }
      }
    }

    function generateTrees() {
      for (let z = 2; z < WORLD_Z - 2; z++) {
        for (let x = 2; x < WORLD_X - 2; x++) {
          if (!canPlaceTree(x, z)) continue;
          if (rand() < 0.018) {
            placeTree(x, z);
          }
        }
      }
    }

    generateTerrain();
    generateTrees();

    // ============================================================
    // InstancedMesh でブロックを描画
    // ============================================================
    const boxGeometry = new THREE.BoxGeometry(1, 1, 1);
    const boxMaterial = new THREE.MeshLambertMaterial({ color: 0xffffff });

    const maxInstances = WORLD_X * WORLD_Y * WORLD_Z;
    const blockMesh = new THREE.InstancedMesh(boxGeometry, boxMaterial, maxInstances);
    blockMesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
    blockMesh.castShadow = true;
    blockMesh.receiveShadow = true;
    blockMesh.frustumCulled = false;
    scene.add(blockMesh);

    const dummy = new THREE.Object3D();
    const tempColor = new THREE.Color();
    let needsRebuild = true;

    function rebuildBlockMesh() {
      let i = 0;

      const XY = WORLD_X * WORLD_Y;

      for (const [k, type] of blocks.entries()) {
        if (i >= maxInstances) break;

        const z = Math.floor(k / XY);
        const rem = k - z * XY;
        const y = Math.floor(rem / WORLD_X);
        const x = rem - y * WORLD_X;

        dummy.position.set(x + 0.5, y + 0.5, z + 0.5);
        dummy.scale.set(1, 1, 1);
        dummy.rotation.set(0, 0, 0);
        dummy.updateMatrix();

        blockMesh.setMatrixAt(i, dummy.matrix);

        tempColor.setHex(TYPES[type].color);
        blockMesh.setColorAt(i, tempColor);

        i++;
      }

      blockMesh.count = i;
      blockMesh.instanceMatrix.needsUpdate = true;
      if (blockMesh.instanceColor) {
        blockMesh.instanceColor.needsUpdate = true;
      }
    }

    // ブロックハイライト
    const highlightGeometry = new THREE.BoxGeometry(1.005, 1.005, 1.005);
    const highlightMaterial = new THREE.LineBasicMaterial({ color: 0x000000 });
    const highlight = new THREE.LineSegments(
      new THREE.EdgesGeometry(highlightGeometry),
      highlightMaterial
    );
    highlight.visible = false;
    scene.add(highlight);

    // ============================================================
    // プレイヤー
    // ============================================================
    const player = {
      pos: new THREE.Vector3(),
      vel: new THREE.Vector3(),
      height: 1.8,
      radius: 0.3,
      eye: 1.62,
      onGround: false
    };

    function findSpawnHeight(x, z) {
      for (let y = WORLD_Y - 1; y >= 0; y--) {
        if (blocks.has(blockKey(x, y, z))) {
          return y;
        }
      }
      return 0;
    }

    const spawnX = Math.floor(WORLD_X / 2);
    const spawnZ = Math.floor(WORLD_Z / 2);
    const spawnTop = findSpawnHeight(spawnX, spawnZ);

    player.pos.set(spawnX + 0.5, spawnTop + 1.01, spawnZ + 0.5);
    player.vel.set(0, 0, 0);

    // 初期視点
    let yaw = 0;
    let pitch = -0.25;

    // ============================================================
    // 衝突判定
    // ============================================================
    function isSolidForPlayer(x, y, z) {
      // 世界の外は壁として扱う。下に落ちないための床にもなる。
      if (x < 0 || x >= WORLD_X || z < 0 || z >= WORLD_Z || y < 0) {
        return true;
      }

      if (y >= WORLD_Y) {
        return false;
      }

      return blocks.has(blockKey(x, y, z));
    }

    function collidesAt(pos) {
      const r = player.radius;
      const h = player.height;

      const minX = Math.floor(pos.x - r);
      const maxX = Math.floor(pos.x + r);
      const minY = Math.floor(pos.y + 0.001);
      const maxY = Math.floor(pos.y + h - 0.001);
      const minZ = Math.floor(pos.z - r);
      const maxZ = Math.floor(pos.z + r);

      for (let y = minY; y <= maxY; y++) {
        for (let x = minX; x <= maxX; x++) {
          for (let z = minZ; z <= maxZ; z++) {
            if (isSolidForPlayer(x, y, z)) {
              return true;
            }
          }
        }
      }

      return false;
    }

    function moveAxis(axis, amount) {
      if (Math.abs(amount) < 1e-7) return false;

      const old = player.pos.clone();
      const next = old.clone();
      next[axis] += amount;

      if (!collidesAt(next)) {
        player.pos.copy(next);
        return false;
      }

      const clamped = old.clone();
      const eps = 0.001;

      if (axis === "y") {
        if (amount < 0) {
          clamped.y = Math.ceil(next.y) + eps;
        } else {
          clamped.y = Math.floor(next.y + player.height) - player.height - eps;
        }
      } else {
        if (amount > 0) {
          if (axis === "x") {
            clamped.x = Math.floor(next.x + player.radius) - player.radius - eps;
          } else {
            clamped.z = Math.floor(next.z + player.radius) - player.radius - eps;
          }
        } else {
          if (axis === "x") {
            clamped.x = Math.floor(next.x - player.radius) + 1 + player.radius + eps;
          } else {
            clamped.z = Math.floor(next.z - player.radius) + 1 + player.radius + eps;
          }
        }
      }

      if (collidesAt(clamped)) {
        return true;
      }

      player.pos.copy(clamped);

      if (axis === "y") {
        if (amount < 0) {
          player.vel.y = 0;
          player.onGround = true;
        } else {
          player.vel.y = 0;
        }
      } else {
        player.vel[axis] = 0;
      }

      return true;
    }

    // ============================================================
    // ブロック操作用ボクセルレイキャスト
    // ============================================================
    function raycastBlock(maxDist = REACH_DISTANCE) {
      const origin = new THREE.Vector3(
        player.pos.x,
        player.pos.y + player.eye,
        player.pos.z
      );

      const dir = new THREE.Vector3();
      camera.getWorldDirection(dir);

      let x = Math.floor(origin.x);
      let y = Math.floor(origin.y);
      let z = Math.floor(origin.z);

      const stepX = dir.x > 0 ? 1 : dir.x < 0 ? -1 : 0;
      const stepY = dir.y > 0 ? 1 : dir.y < 0 ? -1 : 0;
      const stepZ = dir.z > 0 ? 1 : dir.z < 0 ? -1 : 0;

      const invX = stepX !== 0 ? Math.abs(1 / dir.x) : Infinity;
      const invY = stepY !== 0 ? Math.abs(1 / dir.y) : Infinity;
      const invZ = stepZ !== 0 ? Math.abs(1 / dir.z) : Infinity;

      let tMaxX = stepX !== 0
        ? ((stepX > 0 ? x + 1 - origin.x : origin.x - x) * invX)
        : Infinity;

      let tMaxY = stepY !== 0
        ? ((stepY > 0 ? y + 1 - origin.y : origin.y - y) * invY)
        : Infinity;

      let tMaxZ = stepZ !== 0
        ? ((stepZ > 0 ? z + 1 - origin.z : origin.z - z) * invZ)
        : Infinity;

      const face = new THREE.Vector3();

      for (let i = 0; i < 300; i++) {
        if (inBounds(x, y, z) && blocks.has(blockKey(x, y, z))) {
          return { x, y, z, face: face.clone() };
        }

        const minT = Math.min(tMaxX, tMaxY, tMaxZ);
        if (minT > maxDist) break;

        if (minT === tMaxX) {
          x += stepX;
          tMaxX += invX;
          face.set(-stepX, 0, 0);
        } else if (minT === tMaxY) {
          y += stepY;
          tMaxY += invY;
          face.set(0, -stepY, 0);
        } else {
          z += stepZ;
          tMaxZ += invZ;
          face.set(0, 0, -stepZ);
        }
      }

      return null;
    }

    function breakBlock() {
      const hit = raycastBlock();
      if (!hit) return;

      const type = getBlock(hit.x, hit.y, hit.z);
      if (type === 0) return;

      // 岩盤は破壊不可
      if (type === 7) return;

      setBlockDirect(hit.x, hit.y, hit.z, 0);
      needsRebuild = true;
    }

    function placeBlock() {
      const hit = raycastBlock();
      if (!hit) return;

      const nx = hit.x + hit.face.x;
      const ny = hit.y + hit.face.y;
      const nz = hit.z + hit.face.z;

      if (!inBounds(nx, ny, nz)) return;
      if (getBlock(nx, ny, nz) !== 0) return;

      // 自分の体にブロックを入れられない
      const playerMinX = player.pos.x - player.radius;
      const playerMaxX = player.pos.x + player.radius;
      const playerMinY = player.pos.y;
      const playerMaxY = player.pos.y + player.height;
      const playerMinZ = player.pos.z - player.radius;
      const playerMaxZ = player.pos.z + player.radius;

      const blockMinX = nx;
      const blockMaxX = nx + 1;
      const blockMinY = ny;
      const blockMaxY = ny + 1;
      const blockMinZ = nz;
      const blockMaxZ = nz + 1;

      const overlaps =
        playerMinX < blockMaxX &&
        playerMaxX > blockMinX &&
        playerMinY < blockMaxY &&
        playerMaxY > blockMinY &&
        playerMinZ < blockMaxZ &&
        playerMaxZ > blockMinZ;

      if (overlaps) return;

      setBlockDirect(nx, ny, nz, selectedBlock);
      needsRebuild = true;
    }

    // ============================================================
    // UI: ホットバー
    // ============================================================
    const hotbar = document.getElementById("hotbar");
    const overlay = document.getElementById("overlay");

    function updateHotbar() {
      hotbar.innerHTML = "";

      PLACEABLE.forEach((type, index) => {
        const t = TYPES[type];

        const slot = document.createElement("div");
        slot.className = "slot" + (selectedBlock === type ? " selected" : "");

        const num = document.createElement("div");
        num.className = "num";
        num.textContent = String(index + 1);

        const color = document.createElement("div");
        color.className = "color";
        color.style.background = "#" + t.color.toString(16).padStart(6, "0");

        const name = document.createElement("div");
        name.className = "name";
        name.textContent = t.name;

        slot.appendChild(num);
        slot.appendChild(color);
        slot.appendChild(name);

        slot.addEventListener("click", (e) => {
          e.stopPropagation();
          selectedBlock = type;
          updateHotbar();
        });

        hotbar.appendChild(slot);
      });
    }

    updateHotbar();

    // ============================================================
    // 入力
    // ============================================================
    const pressed = new Set();

    window.addEventListener("keydown", (e) => {
      pressed.add(e.code);

      if (e.code === "Space") {
        e.preventDefault();
      }

      if (e.code.startsWith("Digit")) {
        const n = Number(e.code.slice(5));
        if (n >= 1 && n <= PLACEABLE.length) {
          selectedBlock = PLACEABLE[n - 1];
          updateHotbar();
        }
      }
    });

    window.addEventListener("keyup", (e) => {
      pressed.delete(e.code);
    });

    window.addEventListener("contextmenu", (e) => {
      e.preventDefault();
    });

    // Pointer Lock
    function requestLock() {
      renderer.domElement.requestPointerLock();
    }

    renderer.domElement.addEventListener("click", () => {
      if (document.pointerLockElement !== renderer.domElement) {
        requestLock();
      }
    });

    overlay.addEventListener("click", () => {
      requestLock();
    });

    document.addEventListener("pointerlockchange", () => {
      const locked = document.pointerLockElement === renderer.domElement;
      overlay.classList.toggle("hidden", locked);

      if (!locked) {
        pressed.clear();
      }
    });

    document.addEventListener("mousemove", (e) => {
      if (document.pointerLockElement !== renderer.domElement) return;

      const sensitivity = 0.0022;
      yaw -= e.movementX * sensitivity;
      pitch -= e.movementY * sensitivity;

      pitch = Math.max(-1.52, Math.min(1.52, pitch));
    });

    document.addEventListener("mousedown", (e) => {
      if (document.pointerLockElement !== renderer.domElement) return;

      if (e.button === 0) {
        breakBlock();
      } else if (e.button === 2) {
        placeBlock();
      }
    });

    // ============================================================
    // プレイヤー更新
    // ============================================================
    function updatePlayer(dt) {
      const locked = document.pointerLockElement === renderer.domElement;

      const walkSpeed = 5.2;
      const sprintSpeed = 8.2;
      const speed = pressed.has("ShiftLeft") ? sprintSpeed : walkSpeed;

      // 入力方向をyawで変換
      const forward = new THREE.Vector3(
        -Math.sin(yaw),
        0,
        -Math.cos(yaw)
      );

      const right = new THREE.Vector3(
        Math.cos(yaw),
        0,
        -Math.sin(yaw)
      );

      let f = 0;
      let s = 0;

      if (locked) {
        if (pressed.has("KeyW")) f += 1;
        if (pressed.has("KeyS")) f -= 1;
        if (pressed.has("KeyD")) s += 1;
        if (pressed.has("KeyA")) s -= 1;
      }

      let wishX = right.x * s + forward.x * f;
      let wishZ = right.z * s + forward.z * f;

      const wishLen = Math.hypot(wishX, wishZ);
      if (wishLen > 0) {
        wishX /= wishLen;
        wishZ /= wishLen;
      }

      player.vel.x = wishX * speed;
      player.vel.z = wishZ * speed;

      // 重力
      player.vel.y -= 24 * dt;

      // ジャンプ
      if (locked && pressed.has("Space") && player.onGround) {
        player.vel.y = 9;
        player.onGround = false;
      }

      player.onGround = false;

      moveAxis("x", player.vel.x * dt);
      moveAxis("z", player.vel.z * dt);
      moveAxis("y", player.vel.y * dt);

      // 接地判定
      if (player.vel.y <= 0) {
        const probe = player.pos.clone();
        probe.y -= 0.04;
        if (collidesAt(probe)) {
          player.onGround = true;
        }
      }

      // 万一プレイヤーが世界外に出たらリセット
      if (
        player.pos.y < -10 ||
        player.pos.x < -10 ||
        player.pos.z < -10 ||
        player.pos.x > WORLD_X + 10 ||
        player.pos.z > WORLD_Z + 10
      ) {
        player.pos.set(spawnX + 0.5, spawnTop + 1.01, spawnZ + 0.5);
        player.vel.set(0, 0, 0);
      }
    }

    // ============================================================
    // レンダリングループ
    // ============================================================
    function updateCamera() {
      camera.position.set(
        player.pos.x,
        player.pos.y + player.eye,
        player.pos.z
      );

      camera.rotation.set(pitch, yaw, 0, "YXZ");
    }

    function updateHighlight() {
      const hit = raycastBlock();
      if (!hit) {
        highlight.visible = false;
        return;
      }

      highlight.position.set(hit.x + 0.5, hit.y + 0.5, hit.z + 0.5);
      highlight.visible = true;
    }

    const clock = new THREE.Clock();

    function animate() {
      requestAnimationFrame(animate);

      const dt = Math.min(clock.getDelta(), 0.05);

      updatePlayer(dt);
      updateCamera();

      if (needsRebuild) {
        rebuildBlockMesh();
        needsRebuild = false;
      }

      updateHighlight();

      renderer.render(scene, camera);
    }

    window.addEventListener("resize", () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    });

    // 初回描画
    rebuildBlockMesh();
    needsRebuild = false;
    updateCamera();
    animate();
  </script>
</body>
</html>
```

---

もし次に拡張するなら、これをベースに

- チャンク分割で巨大マップ化
- テクスチャ貼り
- 水・溶岩
- インベントリUI
- セーブ/ロード
- マルチプレイ

などを足せます。