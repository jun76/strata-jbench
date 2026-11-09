以下をファイル名 `minecraft-style-game.html` などで保存し、ブラウザで開くと動く、マイクラ風の 3D ブロックサンドボックスゲームです。  
WebGL 用に Three.js を CDN から読み込むので、インターネット接続が必要です。

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>マイクラ風 3D 箱庭ゲーム</title>
  <style>
    html, body {
      margin: 0;
      width: 100%;
      height: 100%;
      overflow: hidden;
      background: #87ceeb;
      font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
      user-select: none;
    }
    canvas {
      display: block;
    }
    #overlay {
      position: fixed;
      inset: 0;
      z-index: 20;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 14px;
      background: rgba(0, 0, 0, 0.62);
      color: white;
      text-align: center;
    }
    #overlay.hidden {
      display: none;
    }
    #startButton {
      padding: 12px 22px;
      font-size: 18px;
      font-weight: 700;
      border: 0;
      border-radius: 8px;
      cursor: pointer;
      background: #4caf50;
      color: white;
    }
    #startButton:hover {
      filter: brightness(1.08);
    }
    #controls {
      line-height: 1.7;
      font-size: 14px;
      max-width: 420px;
    }
    #crosshair {
      position: fixed;
      left: 50%;
      top: 50%;
      transform: translate(-50%, -50%);
      color: rgba(255, 255, 255, 0.9);
      font-size: 26px;
      z-index: 5;
      pointer-events: none;
      text-shadow: 0 0 4px black;
    }
    #hotbar {
      position: fixed;
      left: 50%;
      bottom: 18px;
      transform: translateX(-50%);
      display: flex;
      gap: 7px;
      z-index: 6;
      pointer-events: none;
    }
    .slot {
      width: 54px;
      height: 54px;
      border: 3px solid #111;
      background: rgba(255, 255, 255, 0.14);
      border-radius: 6px;
      box-sizing: border-box;
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .slot.selected {
      border-color: #ffe04d;
      background: rgba(255, 224, 77, 0.25);
    }
    .slot .num {
      position: absolute;
      left: 4px;
      top: 2px;
      color: white;
      font-size: 11px;
      opacity: 0.85;
    }
    .swatch {
      width: 34px;
      height: 34px;
      border: 1px solid rgba(0, 0, 0, 0.45);
      border-radius: 3px;
    }
    #info {
      position: fixed;
      top: 10px;
      left: 10px;
      z-index: 6;
      color: white;
      font-size: 12px;
      text-shadow: 0 0 4px black;
      pointer-events: none;
    }
  </style>
</head>
<body>
  <div id="info">左クリック: 破壊 / 右クリック: 設置</div>
  <div id="crosshair">+</div>
  <div id="hotbar"></div>

  <div id="overlay">
    <h1>マイクラ風 3D 箱庭</h1>
    <button id="startButton">クリックして開始</button>
    <div id="controls">
      WASD: 移動<br />
      スペース: ジャンプ<br />
      マウス: 視点<br />
      左クリック: ブロック破壊<br />
      右クリック: ブロック設置<br />
      1〜6: ブロック選択<br />
      Esc: ポインター解除
    </div>
  </div>

  <script type="module">
    import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';

    // ----------------------------------------------------------------------
    // 基本パラメータ
    // ----------------------------------------------------------------------
    const WORLD_SIZE = 48;
    const HALF_SIZE = WORLD_SIZE / 2;
    const MAX_BLOCKS = 60000;

    const GRAVITY = 28;
    const JUMP_SPEED = 8.2;
    const WALK_SPEED = 5.0;
    const SENSITIVITY = 0.0022;
    const REACH = 6.0;

    const BLOCK_TYPES = ['grass', 'dirt', 'stone', 'wood', 'leaves', 'sand'];

    const BLOCK_INFO = {
      grass:  { name: '草',   color: 0x4aa53f, dark: 0x2e7828, light: 0x74c769 },
      dirt:   { name: '土',   color: 0x7f5a37, dark: 0x5b4025, light: 0x9d774d },
      stone:  { name: '石',   color: 0x8c8c8c, dark: 0x626262, light: 0xa9a9a9 },
      wood:   { name: '木',   color: 0x8a5a2d, dark: 0x67411f, light: 0xa87947 },
      leaves: { name: '葉',   color: 0x2f7d34, dark: 0x1b5a20, light: 0x4bb455 },
      sand:   { name: '砂',   color: 0xe1d18c, dark: 0xbdb16a, light: 0xf2e8b7 }
    };

    function hex(n) {
      return '#' + n.toString(16).padStart(6, '0');
    }

    // ----------------------------------------------------------------------
    // Three.js セットアップ
    // ----------------------------------------------------------------------
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x87ceeb);
    scene.fog = new THREE.Fog(0x87ceeb, 28, 90);

    const camera = new THREE.PerspectiveCamera(
      75,
      window.innerWidth / window.innerHeight,
      0.05,
      500
    );
    camera.rotation.order = 'YXZ';

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    scene.add(new THREE.AmbientLight(0xffffff, 0.68));

    const sun = new THREE.DirectionalLight(0xffffff, 0.72);
    sun.position.set(30, 60, 18);
    scene.add(sun);

    // ----------------------------------------------------------------------
    // ブロック素材
    // ----------------------------------------------------------------------
    function makeBlockTexture(base, dark, light) {
      const c = document.createElement('canvas');
      c.width = 16;
      c.height = 16;
      const ctx = c.getContext('2d');

      ctx.fillStyle = hex(base);
      ctx.fillRect(0, 0, 16, 16);

      for (let y = 0; y < 16; y++) {
        for (let x = 0; x < 16; x++) {
          const r = Math.random();
          if (r < 0.12) {
            ctx.fillStyle = hex(dark);
            ctx.fillRect(x, y, 1, 1);
          } else if (r < 0.20) {
            ctx.fillStyle = hex(light);
            ctx.fillRect(x, y, 1, 1);
          }
        }
      }

      ctx.strokeStyle = 'rgba(0,0,0,0.28)';
      ctx.lineWidth = 1;
      ctx.strokeRect(0.5, 0.5, 15, 15);

      const tex = new THREE.CanvasTexture(c);
      tex.magFilter = THREE.NearestFilter;
      tex.minFilter = THREE.NearestFilter;
      return tex;
    }

    const boxGeometry = new THREE.BoxGeometry(1, 1, 1);

    const materials = BLOCK_TYPES.map(name => {
      const info = BLOCK_INFO[name];
      return new THREE.MeshLambertMaterial({
        map: makeBlockTexture(info.color, info.dark, info.light)
      });
    });

    const instancedMeshes = BLOCK_TYPES.map((_, i) => {
      const mesh = new THREE.InstancedMesh(boxGeometry, materials[i], MAX_BLOCKS);
      mesh.count = 0;
      mesh.frustumCulled = false;
      scene.add(mesh);
      return mesh;
    });

    // ----------------------------------------------------------------------
    // ワールドデータ
    // ----------------------------------------------------------------------
    // key: "x,y,z"
    // value: { x, y, z, typeIndex }
    const blocks = new Map();
    let dirty = true;

    function key(x, y, z) {
      return x + ',' + y + ',' + z;
    }

    function isSolid(x, y, z) {
      return blocks.has(key(x, y, z));
    }

    function setBlockRaw(x, y, z, typeIndex) {
      if (blocks.size >= MAX_BLOCKS) return false;
      blocks.set(key(x, y, z), { x, y, z, type: typeIndex });
      return true;
    }

    function setBlock(x, y, z, typeIndex) {
      const k = key(x, y, z);
      if (blocks.has(k)) return false;
      if (blocks.size >= MAX_BLOCKS) return false;
      blocks.set(k, { x, y, z, type: typeIndex });
      dirty = true;
      return true;
    }

    function removeBlock(x, y, z) {
      const k = key(x, y, z);
      if (!blocks.has(k)) return false;
      blocks.delete(k);
      dirty = true;
      return true;
    }

    const tmpMatrix = new THREE.Matrix4();

    function rebuildBlocks() {
      const counts = new Array(BLOCK_TYPES.length).fill(0);

      for (const block of blocks.values()) {
        const type = block.type;
        if (type < 0 || type >= BLOCK_TYPES.length) continue;

        const index = counts[type];
        if (index >= MAX_BLOCKS) continue;

        tmpMatrix.makeTranslation(block.x + 0.5, block.y + 0.5, block.z + 0.5);
        instancedMeshes[type].setMatrixAt(index, tmpMatrix);
        counts[type]++;
      }

      for (let i = 0; i < instancedMeshes.length; i++) {
        instancedMeshes[i].count = counts[i];
        instancedMeshes[i].instanceMatrix.needsUpdate = true;
      }
    }

    // ----------------------------------------------------------------------
    // 地形生成
    // ----------------------------------------------------------------------
    function terrainHeight(x, z) {
      let h =
        7 +
        2.0 * Math.sin(x * 0.19) +
        2.0 * Math.cos(z * 0.22) +
        1.5 * Math.sin((x + z) * 0.13) +
        0.8 * Math.cos((x - z) * 0.31);

      h = Math.round(h);
      if (h < 1) h = 1;
      if (h > 13) h = 13;
      return h;
    }

    function hash2(x, z) {
      const v = Math.sin(x * 127.1 + z * 311.7) * 43758.5453;
      return v - Math.floor(v);
    }

    function generateWorld() {
      // 地面
      for (let x = -HALF_SIZE; x < HALF_SIZE; x++) {
        for (let z = -HALF_SIZE; z < HALF_SIZE; z++) {
          const h = terrainHeight(x, z);

          for (let y = 0; y <= h; y++) {
            let type = 2; // stone

            if (y === h) {
              type = h <= 3 ? 5 : 0; // sand or grass
            } else if (y >= h - 2) {
              type = 1; // dirt
            }

            setBlockRaw(x, y, z, type);
          }
        }
      }

      // 木
      for (let x = -HALF_SIZE + 3; x < HALF_SIZE - 3; x++) {
        for (let z = -HALF_SIZE + 3; z < HALF_SIZE - 3; z++) {
          if (x * x + z * z < 16) continue; // スpawn付近は木を出さない
          if (hash2(x, z) <= 0.975) continue;

          const h = terrainHeight(x, z);
          if (h <= 3) continue;

          const base = h + 1;

          // 幹
          for (let i = 0; i < 3; i++) {
            setBlockRaw(x, base + i, z, 3); // wood
          }

          // 葉
          for (let dy = -1; dy <= 0; dy++) {
            const y = base + 2 + dy;
            for (let dx = -2; dx <= 2; dx++) {
              for (let dz = -2; dz <= 2; dz++) {
                if (dx === 0 && dz === 0) continue;
                if (Math.abs(dx) + Math.abs(dz) > 3) continue;
                if (Math.abs(dx) === 2 && Math.abs(dz) === 2) continue;

                setBlockRaw(x + dx, y, z + dz, 4); // leaves
              }
            }
          }
        }
      }

      dirty = true;
    }

    generateWorld();
    rebuildBlocks();

    // ----------------------------------------------------------------------
    // プレイヤー
    // ----------------------------------------------------------------------
    const player = {
      pos: new THREE.Vector3(0.5, 20, 0.5),
      vel: new THREE.Vector3(0, 0, 0),
      width: 0.62,
      height: 1.80,
      eye: 1.62,
      onGround: false
    };

    const halfWidth = player.width * 0.5;

    function respawn() {
      const h = terrainHeight(0, 0);
      player.pos.set(0.5, h + 1.15, 0.5);
      player.vel.set(0, 0, 0);
      yaw = 0;
      pitch = -0.15;
      camera.rotation.set(pitch, yaw, 0, 'YXZ');
    }

    respawn();

    const EPS = 0.0001;

    function collides(pos) {
      const minX = pos.x - halfWidth + EPS;
      const maxX = pos.x + halfWidth - EPS;
      const minY = pos.y + EPS;
      const maxY = pos.y + player.height - EPS;
      const minZ = pos.z - halfWidth + EPS;
      const maxZ = pos.z + halfWidth - EPS;

      const x0 = Math.floor(minX);
      const x1 = Math.floor(maxX);
      const y0 = Math.floor(minY);
      const y1 = Math.floor(maxY);
      const z0 = Math.floor(minZ);
      const z1 = Math.floor(maxZ);

      for (let x = x0; x <= x1; x++) {
        for (let y = y0; y <= y1; y++) {
          for (let z = z0; z <= z1; z++) {
            if (isSolid(x, y, z)) return true;
          }
        }
      }

      return false;
    }

    function blockIntersectsPlayer(x, y, z) {
      const minX = x;
      const maxX = x + 1;
      const minY = y;
      const maxY = y + 1;
      const minZ = z;
      const maxZ = z + 1;

      return (
        player.pos.x - halfWidth < maxX - EPS &&
        player.pos.x + halfWidth > minX + EPS &&
        player.pos.y < maxY - EPS &&
        player.pos.y + player.height > minY + EPS &&
        player.pos.z - halfWidth < maxZ - EPS &&
        player.pos.z + halfWidth > minZ + EPS
      );
    }

    function movePlayer(dt) {
      const input = new THREE.Vector3(0, 0, 0);

      if (keys['KeyW']) input.z -= 1;
      if (keys['KeyS']) input.z += 1;
      if (keys['KeyA']) input.x -= 1;
      if (keys['KeyD']) input.x += 1;

      if (input.lengthSq() > 0) input.normalize();

      const forward = new THREE.Vector3();
      camera.getWorldDirection(forward);
      forward.y = 0;
      forward.normalize();

      const right = new THREE.Vector3().crossVectors(
        forward,
        new THREE.Vector3(0, 1, 0)
      ).normalize();

      const desired = new THREE.Vector3()
        .addScaledVector(right, input.x)
        .addScaledVector(forward, -input.z)
        .normalize()
        .multiplyScalar(WALK_SPEED);

      player.vel.x = desired.x;
      player.vel.z = desired.z;

      if (keys['Space'] && player.onGround) {
        player.vel.y = JUMP_SPEED;
        player.onGround = false;
      }

      player.vel.y -= GRAVITY * dt;
      if (player.vel.y < -55) player.vel.y = -55;

      // X移動
      const dx = player.vel.x * dt;
      player.pos.x += dx;
      if (collides(player.pos)) {
        player.pos.x -= dx;
        player.vel.x = 0;
      }

      // Z移動
      const dz = player.vel.z * dt;
      player.pos.z += dz;
      if (collides(player.pos)) {
        player.pos.z -= dz;
        player.vel.z = 0;
      }

      // Y移動
      const dy = player.vel.y * dt;
      player.pos.y += dy;
      if (collides(player.pos)) {
        player.pos.y -= dy;
        if (player.vel.y < 0) {
          player.onGround = true;
        }
        player.vel.y = 0;
      } else {
        player.onGround = false;
      }

      // 落下しすぎたらリスポーン
      if (player.pos.y < -30) {
        respawn();
      }
    }

    // ----------------------------------------------------------------------
    // Voxel レイキャスト
    // ----------------------------------------------------------------------
    function raycastVoxel(ox, oy, oz, dx, dy, dz, maxDist) {
      let x = Math.floor(ox);
      let y = Math.floor(oy);
      let z = Math.floor(oz);

      let prevX = x;
      let prevY = y;
      let prevZ = z;

      const stepX = dx > 0 ? 1 : dx < 0 ? -1 : 0;
      const stepY = dy > 0 ? 1 : dy < 0 ? -1 : 0;
      const stepZ = dz > 0 ? 1 : dz < 0 ? -1 : 0;

      const absDx = Math.abs(dx);
      const absDy = Math.abs(dy);
      const absDz = Math.abs(dz);

      const tDeltaX = absDx > 0 ? 1 / absDx : Infinity;
      const tDeltaY = absDy > 0 ? 1 / absDy : Infinity;
      const tDeltaZ = absDz > 0 ? 1 / absDz : Infinity;

      let tMaxX = dx > 0 ? (x + 1 - ox) * tDeltaX :
                  dx < 0 ? (ox - x) * tDeltaX : Infinity;

      let tMaxY = dy > 0 ? (y + 1 - oy) * tDeltaY :
                  dy < 0 ? (oy - y) * tDeltaY : Infinity;

      let tMaxZ = dz > 0 ? (z + 1 - oz) * tDeltaZ :
                  dz < 0 ? (oz - z) * tDeltaZ : Infinity;

      for (let i = 0; i < 180; i++) {
        if (tMaxX <= tMaxY && tMaxX <= tMaxZ) {
          if (tMaxX > maxDist) break;

          const nx = x + stepX;
          if (isSolid(nx, y, z)) {
            return {
              block: { x: nx, y, z },
              place: { x: prevX, y: prevY, z: prevZ },
              normal: { x: -stepX, y: 0, z: 0 }
            };
          }

          prevX = x;
          prevY = y;
          prevZ = z;
          x = nx;
          tMaxX += tDeltaX;
        } else if (tMaxY <= tMaxZ) {
          if (tMaxY > maxDist) break;

          const ny = y + stepY;
          if (isSolid(x, ny, z)) {
            return {
              block: { x, y: ny, z },
              place: { x: prevX, y: prevY, z: prevZ },
              normal: { x: 0, y: -stepY, z: 0 }
            };
          }

          prevX = x;
          prevY = y;
          prevZ = z;
          y = ny;
          tMaxY += tDeltaY;
        } else {
          if (tMaxZ > maxDist) break;

          const nz = z + stepZ;
          if (isSolid(x, y, nz)) {
            return {
              block: { x, y, z: nz },
              place: { x: prevX, y: prevY, z: prevZ },
              normal: { x: 0, y: 0, z: -stepZ }
            };
          }

          prevX = x;
          prevY = y;
          prevZ = z;
          z = nz;
          tMaxZ += tDeltaZ;
        }
      }

      return null;
    }

    // ----------------------------------------------------------------------
    // 表示用の選択ボックス
    // ----------------------------------------------------------------------
    const targetOutline = new THREE.LineSegments(
      new THREE.EdgesGeometry(new THREE.BoxGeometry(1.002, 1.002, 1.002)),
      new THREE.LineBasicMaterial({ color: 0x000000 })
    );
    targetOutline.visible = false;
    scene.add(targetOutline);

    const placeBox = new THREE.Mesh(
      new THREE.BoxGeometry(0.92, 0.92, 0.92),
      new THREE.MeshBasicMaterial({
        color: 0x3dff60,
        transparent: true,
        opacity: 0.45
      })
    );
    placeBox.visible = false;
    scene.add(placeBox);

    let target = null;

    function updateTarget() {
      const dir = new THREE.Vector3();
      camera.getWorldDirection(dir);

      target = raycastVoxel(
        camera.position.x,
        camera.position.y,
        camera.position.z,
        dir.x,
        dir.y,
        dir.z,
        REACH
      );

      if (target) {
        targetOutline.visible = true;
        targetOutline.position.set(
          target.block.x + 0.5,
          target.block.y + 0.5,
          target.block.z + 0.5
        );

        const p = target.place;
        const validPlace =
          !isSolid(p.x, p.y, p.z) &&
          p.y >= 0 &&
          p.y <= 150 &&
          !blockIntersectsPlayer(p.x, p.y, p.z);

        if (validPlace) {
          placeBox.visible = true;
          placeBox.position.set(p.x + 0.5, p.y + 0.5, p.z + 0.5);
        } else {
          placeBox.visible = false;
        }
      } else {
        targetOutline.visible = false;
        placeBox.visible = false;
      }
    }

    function breakBlock() {
      if (!target) return;
      removeBlock(target.block.x, target.block.y, target.block.z);
    }

    function placeBlock() {
      if (!target) return;

      const p = target.place;
      if (isSolid(p.x, p.y, p.z)) return;
      if (p.y < 0 || p.y > 150) return;
      if (blocks.size >= MAX_BLOCKS) return;
      if (blockIntersectsPlayer(p.x, p.y, p.z)) return;

      setBlock(p.x, p.y, p.z, selectedBlock);
    }

    // ----------------------------------------------------------------------
    // ホットバー
    // ----------------------------------------------------------------------
    let selectedBlock = 0;
    const hotbar = document.getElementById('hotbar');
    const slots = [];

    BLOCK_TYPES.forEach((name, i) => {
      const info = BLOCK_INFO[name];

      const slot = document.createElement('div');
      slot.className = 'slot';

      const num = document.createElement('div');
      num.className = 'num';
      num.textContent = String(i + 1);

      const swatch = document.createElement('div');
      swatch.className = 'swatch';
      swatch.style.background = hex(info.color);

      slot.appendChild(num);
      slot.appendChild(swatch);
      hotbar.appendChild(slot);
      slots.push(slot);
    });

    function setSelectedBlock(index) {
      selectedBlock = index;
      slots.forEach((slot, i) => {
        slot.classList.toggle('selected', i === index);
      });
    }

    setSelectedBlock(0);

    // ----------------------------------------------------------------------
    // 入力
    // ----------------------------------------------------------------------
    const keys = {};

    document.addEventListener('keydown', e => {
      keys[e.code] = true;

      if (e.code.startsWith('Digit')) {
        const n = Number(e.code.slice(5));
        if (n >= 1 && n <= BLOCK_TYPES.length) {
          setSelectedBlock(n - 1);
        }
      }

      if (e.code === 'Space') {
        e.preventDefault();
      }
    });

    document.addEventListener('keyup', e => {
      keys[e.code] = false;
    });

    document.addEventListener('contextmenu', e => e.preventDefault());

    // ポインターロック
    let locked = false;
    let yaw = 0;
    let pitch = -0.15;

    const overlay = document.getElementById('overlay');
    const startButton = document.getElementById('startButton');

    function startPointerLock() {
      renderer.domElement.requestPointerLock();
    }

    startButton.addEventListener('click', startPointerLock);

    renderer.domElement.addEventListener('click', () => {
      if (!locked) startPointerLock();
    });

    document.addEventListener('pointerlockchange', () => {
      locked = document.pointerLockElement === renderer.domElement;
      overlay.classList.toggle('hidden', locked);
    });

    document.addEventListener('mousemove', e => {
      if (!locked) return;

      yaw -= e.movementX * SENSITIVITY;
      pitch -= e.movementY * SENSITIVITY;

      const limit = Math.PI / 2 - 0.01;
      pitch = Math.max(-limit, Math.min(limit, pitch));

      camera.rotation.set(pitch, yaw, 0, 'YXZ');
    });

    document.addEventListener('mousedown', e => {
      if (!locked) return;

      if (e.button === 0) {
        breakBlock();
      } else if (e.button === 2) {
        placeBlock();
      }
    });

    // ----------------------------------------------------------------------
    // リサイズ
    // ----------------------------------------------------------------------
    window.addEventListener('resize', () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    });

    // ----------------------------------------------------------------------
    // メインループ
    // ----------------------------------------------------------------------
    const clock = new THREE.Clock();

    function animate() {
      requestAnimationFrame(animate);

      const dt = Math.min(clock.getDelta(), 0.05);

      if (locked) {
        movePlayer(dt);
      }

      camera.position.set(
        player.pos.x,
        player.pos.y + player.eye,
        player.pos.z
      );

      updateTarget();

      if (dirty) {
        rebuildBlocks();
        dirty = false;
      }

      renderer.render(scene, camera);
    }

    animate();
  </script>
</body>
</html>
```