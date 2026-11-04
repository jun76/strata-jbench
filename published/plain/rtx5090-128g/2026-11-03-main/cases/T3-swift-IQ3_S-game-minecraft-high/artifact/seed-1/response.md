「1ファイルでそのまま動く Three.js 版マイクラ風 3D箱庭ゲーム」を作りました。

以下の HTML をそのまま `index.html` などに保存して、ブラウザ（Chrome / Edge / Safari など）で開いてください。

- WASD 移動
- スペース ジャンプ
- マウス視点
- 左クリック 破壊
- 右クリック 設置
- 1〜9 / ホイール ブロック選択
- R 新規生成
- セーブ / ロード

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>マイクラ風 3D 箱庭</title>
  <style>
    :root {
      --panel-bg: rgba(0, 0, 0, 0.35);
      --panel-border: rgba(255, 255, 255, 0.18);
      --text: #fff;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      overflow: hidden;
      background: #000;
      font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
      color: var(--text);
      user-select: none;
    }
    canvas {
      position: fixed;
      inset: 0;
      z-index: 0;
      display: block;
    }
    #ui {
      position: fixed;
      inset: 0;
      z-index: 10;
      pointer-events: none;
      text-shadow: 0 1px 3px rgba(0,0,0,.7);
    }
    #panel {
      position: absolute;
      top: 12px;
      left: 12px;
      padding: 10px 12px;
      border: 1px solid var(--panel-border);
      border-radius: 12px;
      background: var(--panel-bg);
      backdrop-filter: blur(6px);
      font-size: 12px;
      line-height: 1.5;
      max-width: 260px;
    }
    #panel h1 {
      margin: 0 0 6px;
      font-size: 15px;
    }
    #toolbar {
      position: absolute;
      top: 12px;
      right: 12px;
      display: flex;
      gap: 8px;
      pointer-events: auto;
      flex-wrap: wrap;
    }
    #toolbar button {
      border: 1px solid rgba(255,255,255,.22);
      border-radius: 10px;
      background: rgba(0,0,0,.45);
      color: #fff;
      padding: 9px 12px;
      cursor: pointer;
      font-size: 12px;
    }
    #toolbar button:hover { background: rgba(255,255,255,.14); }
    #status {
      position: absolute;
      top: 56px;
      left: 50%;
      transform: translateX(-50%);
      padding: 6px 10px;
      border-radius: 999px;
      background: rgba(0,0,0,.35);
      border: 1px solid rgba(255,255,255,.14);
      font-size: 12px;
      opacity: 0;
      transition: opacity .25s;
    }
    #status.show { opacity: 1; }
    #crosshair {
      position: absolute;
      left: 50%;
      top: 50%;
      transform: translate(-50%, -50%);
      font-size: 24px;
      font-weight: 700;
      opacity: .85;
    }
    #coords {
      position: absolute;
      left: 12px;
      bottom: 72px;
      font-size: 12px;
      padding: 6px 8px;
      border-radius: 8px;
      background: rgba(0,0,0,.3);
    }
    #hotbar {
      position: absolute;
      left: 50%;
      bottom: 14px;
      transform: translateX(-50%);
      display: flex;
      gap: 6px;
      pointer-events: auto;
    }
    .slot {
      position: relative;
      width: 52px;
      height: 52px;
      border: 2px solid rgba(255,255,255,.35);
      border-radius: 10px;
      background: rgba(255,255,255,.12);
      overflow: hidden;
      cursor: pointer;
    }
    .slot.active {
      border-color: #fff;
      box-shadow: 0 0 0 2px rgba(255,255,255,.8), 0 0 18px rgba(255,255,255,.35);
    }
    .slot .num {
      position: absolute;
      left: 4px;
      top: 2px;
      font-size: 10px;
      opacity: .8;
    }
    .slot .name {
      position: absolute;
      left: 4px;
      bottom: 2px;
      font-size: 10px;
    }
    #lockHint {
      position: absolute;
      inset: 0;
      display: grid;
      place-items: center;
      background: rgba(0,0,0,.42);
      pointer-events: auto;
      cursor: pointer;
      font-size: 16px;
    }
    #lockHint.hidden { display: none; }
    .kbd {
      display: inline-block;
      padding: 1px 5px;
      border: 1px solid rgba(255,255,255,.28);
      border-radius: 5px;
      background: rgba(255,255,255,.08);
      font-size: 11px;
    }
  </style>

  <script type="importmap">
  {
    "imports": {
      "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js"
    }
  }
  </script>
</head>
<body>
  <div id="ui">
    <div id="panel">
      <h1>Voxel Garden</h1>
      <div><span class="kbd">W</span><span class="kbd">A</span><span class="kbd">S</span><span class="kbd">D</span> 移動</div>
      <div><span class="kbd">Space</span> ジャンプ / <span class="kbd">Shift</span> 走る</div>
      <div><span class="kbd">左</span> 破壊 / <span class="kbd">右</span> 設置</div>
      <div><span class="kbd">1</span>〜<span class="kbd">9</span> / ホイールでブロック選択</div>
      <div><span class="kbd">R</span> 新規ワールド</div>
    </div>

    <div id="toolbar">
      <button id="btnNew">新規</button>
      <button id="btnSave">保存</button>
      <button id="btnLoad">読込</button>
    </div>

    <div id="status"></div>
    <div id="crosshair">+</div>
    <div id="coords">x: 0 y: 0 z: 0</div>

    <div id="hotbar"></div>

    <div id="lockHint">クリックして画面を操作（ポインターロック）</div>
  </div>

  <script type="module">
    import * as THREE from 'three';

    // -----------------------------
    // 定数
    // -----------------------------
    const W = 64;
    const D = 64;
    const H = 32;
    const WATER_LEVEL = 4;
    const STORAGE_KEY = 'voxel-garden-v1';

    const HOTBAR_TYPES = [1, 2, 3, 4, 5, 6, 7, 8, 9];
    const BLOCK_NAMES = ['', '草', '土', '石', '木', '葉', '砂', 'ガラス', 'レンガ', '水'];

    // ブロックID
    // 0 空気
    // 1 草
    // 2 土
    // 3 石
    // 4 木
    // 5 葉
    // 6 砂
    // 7 ガラス
    // 8 レンガ
    // 9 水

    // -----------------------------
    // 状態
    // -----------------------------
    let seed = Math.floor(Math.random() * 1_000_000_000);
    const world = new Uint8Array(W * D * H);
    let dirty = true;

    const player = {
      x: W / 2 + 0.5,
      y: H + 5,
      z: D / 2 + 0.5,
      vx: 0,
      vy: 0,
      vz: 0,
      yaw: 0,
      pitch: -0.1,
      onGround: false,
      inWater: false,
    };

    const keys = {};
    let selectedType = 1;

    // -----------------------------
    // ユーティリティ
    // -----------------------------
    function clamp(v, min, max) {
      return Math.max(min, Math.min(max, v));
    }

    function idx(x, y, z) {
      return (y * W + x) * D + z;
    }

    function getRaw(x, y, z) {
      if (y < 0) return 3;          // 下は岩盤扱い
      if (y >= H) return 0;
      if (x < 0 || x >= W || z < 0 || z >= D) return 3; // 外側は壁扱い
      return world[idx(x, y, z)];
    }

    function setRaw(x, y, z, t) {
      if (x < 0 || x >= W || y < 0 || y >= H || z < 0 || z >= D) return;
      world[idx(x, y, z)] = t;
      dirty = true;
    }

    function setDirect(x, y, z, t) {
      if (x < 0 || x >= W || y < 0 || y >= H || z < 0 || z >= D) return;
      world[idx(x, y, z)] = t;
    }

    function isTransparent(t) {
      return t === 0 || t === 7 || t === 9;
    }

    function isSolid(t) {
      return t !== 0 && t !== 9;
    }

    function isTargetable(t) {
      return t !== 0 && t !== 9;
    }

    // -----------------------------
    // 雑なノイズ
    // -----------------------------
    function hash2(x, z) {
      let n = (x | 0) * 374761393 + (z | 0) * 668265263 + (seed | 0) * 1274126177;
      n = (n ^ (n >>> 15)) * 1274126177;
      n ^= n >>> 16;
      return (n >>> 0) / 4294967295;
    }

    function lerp(a, b, t) {
      return a + (b - a) * t;
    }

    function smoothNoise(x, z) {
      const ix = Math.floor(x);
      const iz = Math.floor(z);
      const fx = x - ix;
      const fz = z - iz;

      const a = hash2(ix, iz);
      const b = hash2(ix + 1, iz);
      const c = hash2(ix, iz + 1);
      const d = hash2(ix + 1, iz + 1);

      const ux = fx * fx * (3 - 2 * fx);
      const uz = fz * fz * (3 - 2 * fz);

      return lerp(lerp(a, b, ux), lerp(c, d, ux), uz);
    }

    function fbm(x, z) {
      let sum = 0;
      let amp = 1;
      let freq = 1;
      let norm = 0;
      for (let i = 0; i < 4; i++) {
        sum += amp * smoothNoise(x * freq, z * freq);
        norm += amp;
        amp *= 0.5;
        freq *= 2;
      }
      return sum / norm;
    }

    // -----------------------------
    // ワールド生成
    // -----------------------------
    function generateWorld() {
      world.fill(0);

      for (let x = 0; x < W; x++) {
        for (let z = 0; z < D; z++) {
          const n1 = fbm(x * 0.025, z * 0.025);
          const n2 = fbm(x * 0.08, z * 0.08);
          let h = Math.floor(8 + 11 * n1 + 5 * n2);
          h = clamp(h, 1, H - 7);

          for (let y = 0; y <= h; y++) {
            let t = 0;
            if (y === 0) {
              t = 3; // 岩盤扱い
            } else if (y === h) {
              t = h <= WATER_LEVEL + 1 ? 6 : 1;
            } else if (y >= h - 3) {
              t = 2;
            } else {
              t = 3;
            }
            setDirect(x, y, z, t);
          }

          for (let y = h + 1; y <= WATER_LEVEL; y++) {
            setDirect(x, y, z, 9);
          }
        }
      }

      addTrees();
      spawnPlayer();
      dirty = true;
    }

    function findTopSolid(x, z) {
      for (let y = H - 2; y >= 1; y--) {
        const t = getRaw(x, y, z);
        if (t === 1) return y;
      }
      return -1;
    }

    function addTrees() {
      for (let x = 2; x < W - 2; x++) {
        for (let z = 2; z < D - 2; z++) {
          if (hash2(x + 13, z + 29) < 0.985) continue;

          const top = findTopSolid(x, z);
          if (top < WATER_LEVEL + 2) continue;
          if (getRaw(x, top, z) !== 1) continue;

          const trunkH = 3 + Math.floor(hash2(x, z) * 3); // 3〜5
          if (top + trunkH + 3 >= H) continue;

          for (let i = 1; i <= trunkH; i++) {
            setDirect(x, top + i, z, 4);
          }

          const leafCenterY = top + trunkH + 1;
          for (let dy = -1; dy <= 1; dy++) {
            for (let dx = -2; dx <= 2; dx++) {
              for (let dz = -2; dz <= 2; dz++) {
                const y = leafCenterY + dy;
                if (Math.abs(dx) + Math.abs(dz) + Math.abs(dy) > 3) continue;
                if (Math.abs(dx) === 2 && Math.abs(dz) === 2) continue;
                if (getRaw(x + dx, y, z + dz) === 0) {
                  setDirect(x + dx, y, z + dz, 5);
                }
              }
            }
          }
        }
      }
    }

    function spawnPlayer() {
      const x = Math.floor(W / 2);
      const z = Math.floor(D / 2);

      player.x = x + 0.5;
      player.z = z + 0.5;
      player.vx = 0;
      player.vy = 0;
      player.vz = 0;

      for (let y = H - 1; y >= 1; y--) {
        if (isSolid(getRaw(x, y, z))) {
          player.y = y + 1.05;
          return;
        }
      }

      player.y = WATER_LEVEL + 3;
    }

    // -----------------------------
    // Three.js
    // -----------------------------
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x87ceeb);
    scene.fog = new THREE.Fog(0x87ceeb, 32, 110);

    const camera = new THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 0.05, 500);
    camera.rotation.order = 'YXZ';

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    const hemiLight = new THREE.HemisphereLight(0xbfd8ff, 0x4b3a2a, 0.85);
    scene.add(hemiLight);

    const sun = new THREE.DirectionalLight(0xffffff, 1.0);
    sun.position.set(24, 48, 16);
    scene.add(sun);

    const opaqueMaterial = new THREE.MeshLambertMaterial({ vertexColors: true });
    const transparentMaterial = new THREE.MeshLambertMaterial({
      vertexColors: true,
      transparent: true,
      opacity: 0.72,
      depthWrite: false,
      side: THREE.DoubleSide,
    });

    const opaqueMesh = new THREE.Mesh(new THREE.BufferGeometry(), opaqueMaterial);
    const transparentMesh = new THREE.Mesh(new THREE.BufferGeometry(), transparentMaterial);
    transparentMesh.renderOrder = 1;
    scene.add(opaqueMesh, transparentMesh);

    const outlineGeom = new THREE.EdgesGeometry(new THREE.BoxGeometry(1, 1, 1));
    const outlineMat = new THREE.LineBasicMaterial({ color: 0x111111, transparent: true, opacity: 0.75 });
    const outline = new THREE.LineSegments(outlineGeom, outlineMat);
    outline.scale.set(1.012, 1.012, 1.012);
    outline.visible = false;
    scene.add(outline);

    // -----------------------------
    // メッシュ生成
    // -----------------------------
    const faceDirs = [
      [1, 0, 0],
      [-1, 0, 0],
      [0, 1, 0],
      [0, -1, 0],
      [0, 0, 1],
      [0, 0, -1],
    ];

    const faceCorners = [
      // +x
      [[1, 0, 0], [1, 1, 0], [1, 1, 1], [1, 0, 1]],
      // -x
      [[0, 0, 1], [0, 1, 1], [0, 1, 0], [0, 0, 0]],
      // +y
      [[0, 1, 1], [1, 1, 1], [1, 1, 0], [0, 1, 0]],
      // -y
      [[0, 0, 0], [1, 0, 0], [1, 0, 1], [0, 0, 1]],
      // +z
      [[1, 0, 1], [1, 1, 1], [0, 1, 1], [0, 0, 1]],
      // -z
      [[0, 0, 0], [0, 1, 0], [1, 1, 0], [1, 0, 0]],
    ];

    const tmpColor = new THREE.Color();

    function setBlockColor(type, dir, color) {
      switch (type) {
        case 1:
          color.setHex(dir === 2 ? 0x56a847 : 0x855d3a);
          break;
        case 2:
          color.setHex(dir === 2 ? 0x916340 : 0x855d3a);
          break;
        case 3:
          color.setHex(dir === 2 ? 0x979797 : 0x808080);
          break;
        case 4:
          color.setHex(dir === 2 ? 0x96734a : 0x6b4d2e);
          break;
        case 5:
          color.setHex(dir === 2 ? 0x3ca44b : dir === 3 ? 0x2b7a34 : 0x359041);
          break;
        case 6:
          color.setHex(dir === 2 ? 0xe7db9a : 0xd8c583);
          break;
        case 7:
          color.setHex(0x9cd7ef);
          break;
        case 8:
          color.setHex(0xb45247);
          break;
        case 9:
          color.setHex(0x3d7ad6);
          break;
        default:
          color.setHex(0xffffff);
          break;
      }
    }

    function pushFace(pos, norm, col, x, y, z, dir) {
      const n = faceDirs[dir];
      const c = faceCorners[dir];

      for (const tri of [[0, 1, 2], [2, 1, 3]]) {
        for (const vi of tri) {
          const p = c[vi];
          pos.push(x + p[0], y + p[1], z + p[2]);
          norm.push(n[0], n[1], n[2]);
          col.push(tmpColor.r, tmpColor.g, tmpColor.b);
        }
      }
    }

    function makeGeometry(pos, norm, col) {
      const g = new THREE.BufferGeometry();
      g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
      g.setAttribute('normal', new THREE.Float32BufferAttribute(norm, 3));
      g.setAttribute('color', new THREE.Float32BufferAttribute(col, 3));
      g.computeBoundingSphere();
      return g;
    }

    function buildWorldMesh() {
      const opPos = [], opNorm = [], opCol = [];
      const trPos = [], trNorm = [], trCol = [];

      for (let y = 0; y < H; y++) {
        for (let x = 0; x < W; x++) {
          for (let z = 0; z < D; z++) {
            const t = world[idx(x, y, z)];
            if (t === 0) continue;

            const isTransparentBlock = t === 7 || t === 9;

            for (let dir = 0; dir < 6; dir++) {
              const nx = x + faceDirs[dir][0];
              const ny = y + faceDirs[dir][1];
              const nz = z + faceDirs[dir][2];
              const nb = getRaw(nx, ny, nz);

              let visible = false;

              if (t === 9) {
                visible = nb === 0 || nb === 7;
              } else if (t === 7) {
                visible = isTransparent(nb) && nb !== 7;
              } else {
                visible = isTransparent(nb);
              }

              if (!visible) continue;

              setBlockColor(t, dir, tmpColor);

              if (isTransparentBlock) {
                pushFace(trPos, trNorm, trCol, x, y, z, dir);
              } else {
                pushFace(opPos, opNorm, opCol, x, y, z, dir);
              }
            }
          }
        }
      }

      const oldOpaque = opaqueMesh.geometry;
      const oldTransparent = transparentMesh.geometry;

      opaqueMesh.geometry = makeGeometry(opPos, opNorm, opCol);
      transparentMesh.geometry = makeGeometry(trPos, trNorm, trCol);

      oldOpaque.dispose();
      oldTransparent.dispose();
    }

    // -----------------------------
    // レイキャスト
    // -----------------------------
    function raycast(maxDist = 6) {
      const o = camera.position;
      const d = new THREE.Vector3();
      camera.getWorldDirection(d);
      d.normalize();

      let x = Math.floor(o.x);
      let y = Math.floor(o.y);
      let z = Math.floor(o.z);

      const stepX = d.x > 0 ? 1 : d.x < 0 ? -1 : 0;
      const stepY = d.y > 0 ? 1 : d.y < 0 ? -1 : 0;
      const stepZ = d.z > 0 ? 1 : d.z < 0 ? -1 : 0;

      const tDeltaX = stepX !== 0 ? Math.abs(1 / d.x) : Infinity;
      const tDeltaY = stepY !== 0 ? Math.abs(1 / d.y) : Infinity;
      const tDeltaZ = stepZ !== 0 ? Math.abs(1 / d.z) : Infinity;

      let tMaxX = stepX > 0
        ? (Math.floor(o.x) + 1 - o.x) / d.x
        : stepX < 0
          ? (Math.floor(o.x) - o.x) / d.x
          : Infinity;

      let tMaxY = stepY > 0
        ? (Math.floor(o.y) + 1 - o.y) / d.y
        : stepY < 0
          ? (Math.floor(o.y) - o.y) / d.y
          : Infinity;

      let tMaxZ = stepZ > 0
        ? (Math.floor(o.z) + 1 - o.z) / d.z
        : stepZ < 0
          ? (Math.floor(o.z) - o.z) / d.z
          : Infinity;

      let nx = 0, ny = 0, nz = 0;

      for (let i = 0; i < 120; i++) {
        const t = getRaw(x, y, z);
        if (isTargetable(t)) {
          return { x, y, z, nx, ny, nz };
        }

        if (tMaxX < tMaxY && tMaxX < tMaxZ) {
          if (tMaxX > maxDist) break;
          x += stepX;
          nx = -stepX;
          ny = 0;
          nz = 0;
          tMaxX += tDeltaX;
        } else if (tMaxY < tMaxZ) {
          if (tMaxY > maxDist) break;
          y += stepY;
          nx = 0;
          ny = -stepY;
          nz = 0;
          tMaxY += tDeltaY;
        } else {
          if (tMaxZ > maxDist) break;
          z += stepZ;
          nx = 0;
          ny = 0;
          nz = -stepZ;
          tMaxZ += tDeltaZ;
        }
      }

      return null;
    }

    function updateHighlight() {
      const hit = raycast(6);
      if (hit) {
        outline.visible = true;
        outline.position.set(hit.x + 0.5, hit.y + 0.5, hit.z + 0.5);
      } else {
        outline.visible = false;
      }
    }

    function breakBlock() {
      const hit = raycast(6);
      if (!hit) return;
      if (hit.y <= 0) return; // 岩盤は壊せない
      setRaw(hit.x, hit.y, hit.z, 0);
      dirty = true;
    }

    function placeBlock() {
      const hit = raycast(6);
      if (!hit) return;

      const x = hit.x + hit.nx;
      const y = hit.y + hit.ny;
      const z = hit.z + hit.nz;

      if (x < 0 || x >= W || y < 0 || y >= H || z < 0 || z >= D) return;

      const current = getRaw(x, y, z);
      if (!(current === 0 || current === 9)) return;

      // 中に設置してプレイヤーと衝突するなら阻止
      if (boxIntersectsPlayer(x, y, z)) return;

      setRaw(x, y, z, selectedType);
      dirty = true;
    }

    function boxIntersectsPlayer(bx, by, bz) {
      const playerMinX = player.x - 0.3;
      const playerMaxX = player.x + 0.3;
      const playerMinY = player.y;
      const playerMaxY = player.y + 1.8;
      const playerMinZ = player.z - 0.3;
      const playerMaxZ = player.z + 0.3;

      return bx < playerMaxX &&
             bx + 1 > playerMinX &&
             by < playerMaxY &&
             by + 1 > playerMinY &&
             bz < playerMaxZ &&
             bz + 1 > playerMinZ;
    }

    // -----------------------------
    // 物理・衝突
    // -----------------------------
    function collides(px, py, pz) {
      const minX = Math.floor(px - 0.3);
      const maxX = Math.floor(px + 0.3);
      const minY = Math.floor(py);
      const maxY = Math.floor(py + 1.799);
      const minZ = Math.floor(pz - 0.3);
      const maxZ = Math.floor(pz + 0.3);

      for (let ix = minX; ix <= maxX; ix++) {
        for (let iy = minY; iy <= maxY; iy++) {
          for (let iz = minZ; iz <= maxZ; iz++) {
            if (isSolid(getRaw(ix, iy, iz))) return true;
          }
        }
      }
      return false;
    }

    function moveAxis(axis, delta) {
      if (delta === 0) return;

      player[axis] += delta;

      if (collides(player.x, player.y, player.z)) {
        player[axis] -= delta;

        if (axis === 'y') {
          if (delta < 0) {
            player.onGround = true;
          }
          player.vy = 0;
        } else {
          const vKey = 'v' + axis;
          player[vKey] = 0;
        }
      }
    }

    function update(dt) {
      const sprint = !!keys['ShiftLeft'];
      const baseSpeed = sprint ? 9.0 : 5.5;
      const speed = player.inWater ? baseSpeed * 0.62 : baseSpeed;

      const forward = new THREE.Vector3(-Math.sin(player.yaw), 0, -Math.cos(player.yaw));
      const right = new THREE.Vector3(Math.cos(player.yaw), 0, -Math.sin(player.yaw));

      const move = new THREE.Vector3();

      if (keys['KeyW']) move.add(forward);
      if (keys['KeyS']) move.sub(forward);
      if (keys['KeyD']) move.add(right);
      if (keys['KeyA']) move.sub(right);

      if (move.lengthSq() > 0) move.normalize();

      player.vx = move.x * speed;
      player.vz = move.z * speed;

      const footBlock = getRaw(Math.floor(player.x), Math.floor(player.y + 0.2), Math.floor(player.z));
      player.inWater = footBlock === 9;

      if (player.inWater) {
        player.vy -= 10 * dt;
        player.vy = Math.max(player.vy, -4.5);
        if (keys['Space']) player.vy = 4.0;
      } else {
        player.vy -= 24 * dt;
        player.vy = Math.max(player.vy, -48);

        if (keys['Space'] && player.onGround) {
          player.vy = 9.0;
        }
      }

      player.onGround = false;

      moveAxis('x', player.vx * dt);
      moveAxis('z', player.vz * dt);
      moveAxis('y', player.vy * dt);

      // 落下死防止（床下へ消えない）
      if (player.y < -4) {
        spawnPlayer();
      }

      camera.position.set(player.x, player.y + 1.6, player.z);
      camera.rotation.y = player.yaw;
      camera.rotation.x = player.pitch;
    }

    // -----------------------------
    // 入力
    // -----------------------------
    const lockHint = document.getElementById('lockHint');
    const statusEl = document.getElementById('status');

    function setStatus(msg) {
      statusEl.textContent = msg;
      statusEl.classList.add('show');
      clearTimeout(setStatus._t);
      setStatus._t = setTimeout(() => statusEl.classList.remove('show'), 1400);
    }

    function isLocked() {
      return document.pointerLockElement === renderer.domElement;
    }

    function setLockHint() {
      lockHint.classList.toggle('hidden', isLocked());
    }

    renderer.domElement.addEventListener('click', () => {
      if (!isLocked()) {
        renderer.domElement.requestPointerLock();
      }
    });

    lockHint.addEventListener('click', () => {
      renderer.domElement.requestPointerLock();
    });

    document.addEventListener('pointerlockchange', setLockHint);

    document.addEventListener('mousemove', (e) => {
      if (!isLocked()) return;
      player.yaw -= e.movementX * 0.0022;
      player.pitch -= e.movementY * 0.0022;
      player.pitch = clamp(player.pitch, -1.5, 1.5);
    });

    document.addEventListener('mousedown', (e) => {
      if (!isLocked()) return;
      if (e.button === 0) breakBlock();
      if (e.button === 2) placeBlock();
    });

    renderer.domElement.addEventListener('contextmenu', (e) => e.preventDefault());

    window.addEventListener('keydown', (e) => {
      keys[e.code] = true;

      if (e.code === 'Space') e.preventDefault();

      if (/^Digit[1-9]$/.test(e.code)) {
        selectedType = parseInt(e.code.slice(5), 10);
        updateHotbar();
      }

      if (e.code === 'KeyR') {
        seed = Math.floor(Math.random() * 1_000_000_000);
        generateWorld();
        setStatus('新規ワールド');
      }

      if (e.code === 'KeyV') {
        saveWorld();
      }

      if (e.code === 'KeyB') {
        loadWorld();
      }
    });

    window.addEventListener('keyup', (e) => {
      keys[e.code] = false;
    });

    window.addEventListener('wheel', (e) => {
      if (!isLocked()) return;
      selectedType += e.deltaY > 0 ? 1 : -1;
      if (selectedType < 1) selectedType = 9;
      if (selectedType > 9) selectedType = 1;
      updateHotbar();
    }, { passive: true });

    window.addEventListener('resize', () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    });

    // -----------------------------
    // ホットバー
    // -----------------------------
    const hotbarEl = document.getElementById('hotbar');
    const slots = [];

    function topColorCss(t) {
      const hex = (() => {
        switch (t) {
          case 1: return 0x56a847;
          case 2: return 0x855d3a;
          case 3: return 0x979797;
          case 4: return 0x6b4d2e;
          case 5: return 0x359041;
          case 6: return 0xe7db9a;
          case 7: return 0x9cd7ef;
          case 8: return 0xb45247;
          case 9: return 0x3d7ad6;
          default: return 0xffffff;
        }
      })();
      return `#${hex.toString(16).padStart(6, '0')}`;
    }

    function createHotbar() {
      hotbarEl.innerHTML = '';
      slots.length = 0;

      HOTBAR_TYPES.forEach((type, i) => {
        const div = document.createElement('div');
        div.className = 'slot';
        div.style.background = topColorCss(type);
        div.innerHTML = `
          <div class="num">${i + 1}</div>
          <div class="name">${BLOCK_NAMES[type]}</div>
        `;
        div.addEventListener('click', (e) => {
          e.stopPropagation();
          selectedType = type;
          updateHotbar();
        });
        hotbarEl.appendChild(div);
        slots.push(div);
      });

      updateHotbar();
    }

    function updateHotbar() {
      slots.forEach((el, i) => {
        el.classList.toggle('active', HOTBAR_TYPES[i] === selectedType);
      });
    }

    // -----------------------------
    // セーブ / ロード
    // -----------------------------
    function bytesToBase64(arr) {
      let bin = '';
      const chunk = 0x8000;
      for (let i = 0; i < arr.length; i += chunk) {
        bin += String.fromCharCode.apply(null, arr.subarray(i, i + chunk));
      }
      return btoa(bin);
    }

    function base64ToBytes(b64) {
      const bin = atob(b64);
      const arr = new Uint8Array(bin.length);
      for (let i = 0; i < bin.length; i++) {
        arr[i] = bin.charCodeAt(i);
      }
      return arr;
    }

    function saveWorld() {
      const data = {
        version: 1,
        seed,
        base64: bytesToBase64(world),
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
      setStatus('保存しました');
    }

    function loadWorld() {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) {
        setStatus('保存データがありません');
        return;
      }

      try {
        const data = JSON.parse(raw);
        const bytes = base64ToBytes(data.base64);
        if (bytes.length !== world.length) {
          setStatus('データが壊れています');
          return;
        }

        world.set(bytes);
        seed = data.seed ?? seed;
        spawnPlayer();
        dirty = true;
        setStatus('読み込みました');
      } catch (e) {
        console.error(e);
        setStatus('読み込みに失敗しました');
      }
    }

    document.getElementById('btnNew').addEventListener('click', (e) => {
      e.stopPropagation();
      seed = Math.floor(Math.random() * 1_000_000_000);
      generateWorld();
      setStatus('新規ワールド');
    });

    document.getElementById('btnSave').addEventListener('click', (e) => {
      e.stopPropagation();
      saveWorld();
    });

    document.getElementById('btnLoad').addEventListener('click', (e) => {
      e.stopPropagation();
      loadWorld();
    });

    // -----------------------------
    // UI更新
    // -----------------------------
    const coordsEl = document.getElementById('coords');

    function updateUI() {
      coordsEl.textContent =
        `x: ${player.x.toFixed(1)}  y: ${player.y.toFixed(1)}  z: ${player.z.toFixed(1)}  /  ${BLOCK_NAMES[selectedType]}`;
    }

    // -----------------------------
    // メインループ
    // -----------------------------
    const clock = new THREE.Clock();

    function animate() {
      requestAnimationFrame(animate);

      const dt = Math.min(clock.getDelta(), 0.05);

      update(dt);

      if (dirty) {
        buildWorldMesh();
        dirty = false;
      }

      updateHighlight();
      updateUI();

      renderer.render(scene, camera);
    }

    // -----------------------------
    // 開始
    // -----------------------------
    createHotbar();
    generateWorld();
    buildWorldMesh();
    dirty = false;
    setLockHint();
    animate();
  </script>
</body>
</html>
```

追加しそうな要素：  
- テクスチャ化  
- 自動階段移動  
- 水中の泡、夜間  
- 作業台・クラフト  
- インベントリ  
- 保存スロット複数  

必要なら次に「テクスチャ付きマイクラ風」にアップグレードします。