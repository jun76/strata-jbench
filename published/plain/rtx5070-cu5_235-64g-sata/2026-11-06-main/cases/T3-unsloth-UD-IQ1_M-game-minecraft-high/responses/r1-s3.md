以下を `index.html` として保存し、ブラウザで開くと遊べます。  
※ Three.js をCDNから読み込むので、最初はネット接続が必要です。PC推奨。

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>マイクラ風 3D 箱庭</title>
  <style>
    html, body {
      margin: 0;
      width: 100%;
      height: 100%;
      overflow: hidden;
      background: #87ceeb;
      font-family: "Meiryo", "Hiragino Kaku Gothic ProN", sans-serif;
    }
    canvas {
      display: block;
    }
    #ui {
      position: fixed;
      top: 12px;
      left: 12px;
      color: #fff;
      background: rgba(0, 0, 0, 0.40);
      padding: 10px 14px;
      border-radius: 8px;
      line-height: 1.5;
      pointer-events: none;
      font-size: 14px;
      z-index: 10;
    }
    #start {
      position: fixed;
      inset: 0;
      margin: auto;
      width: max-content;
      height: max-content;
      padding: 18px 28px;
      font-size: 18px;
      font-weight: 700;
      color: #fff;
      background: #3c8f3c;
      border: 0;
      border-radius: 10px;
      cursor: pointer;
      z-index: 20;
    }
    #start:hover {
      background: #43a343;
    }
  </style>
</head>
<body>
  <div id="ui"></div>
  <button id="start">クリックでゲーム開始</button>

  <script type="importmap">
    {
      "imports": {
        "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js"
      }
    }
  </script>

  <script type="module">
    import * as THREE from "three";

    // -------------------------
    // 定数
    // -------------------------
    const WORLD_HALF = 24; // x,z は -24〜23
    const MAX_BLOCKS = 120000;

    const PLAYER_HEIGHT = 1.8;
    const PLAYER_HALF_WIDTH = 0.3;
    const EYE_HEIGHT = 1.6;

    const GRAVITY = 26.0;
    const JUMP_POWER = 9.0;
    const WALK_SPEED = 5.2;
    const SPRINT_SPEED = 9.5;

    const SELECT_MAX = 6;

    const blockTypes = [
      null,
      { name: "草",  color: new THREE.Color(0x5db335) },
      { name: "土",  color: new THREE.Color(0x8b6038) },
      { name: "石",  color: new THREE.Color(0x8a8a8a) },
      { name: "木",  color: new THREE.Color(0x6d4528) },
      { name: "葉",  color: new THREE.Color(0x2e8b3f) },
      { name: "砂",  color: new THREE.Color(0xe8d985) }
    ];

    let currentBlockType = 1;

    // -------------------------
    // 状態
    // -------------------------
    const blocks = new Map();        // "x,y,z" -> blockType
    const blockToInstance = new Map(); // "x,y,z" -> instanceIndex
    const instanceKeys = [];
    const instanceTypes = [];

    const player = {
      x: 0,
      y: 15,
      z: 0,
      vx: 0,
      vy: 0,
      vz: 0,
      onGround: false
    };

    let yaw = 0;
    let pitch = 0;

    const keys = {};

    let hoveredBlock = null;

    // -------------------------
    // Three.js初期化
    // -------------------------
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x87ceeb);
    scene.fog = new THREE.Fog(0x87ceeb, 28, 75);

    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 300);
    scene.add(camera);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    const hemiLight = new THREE.HemisphereLight(0xbfefff, 0x775522, 1.0);
    scene.add(hemiLight);

    const sunLight = new THREE.DirectionalLight(0xffffff, 1.5);
    sunLight.position.set(50, 80, 20);
    scene.add(sunLight);

    // ブロック用メッシュ
    const blockGeometry = new THREE.BoxGeometry(1, 1, 1);
    blockGeometry.translate(0.5, 0.5, 0.5);

    const blockMaterial = new THREE.MeshStandardMaterial({
      vertexColors: true,
      roughness: 0.88,
      metalness: 0.0
    });

    const blockMesh = new THREE.InstancedMesh(blockGeometry, blockMaterial, MAX_BLOCKS);
    blockMesh.count = 0;
    blockMesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);

    blockMesh.instanceColor = new THREE.InstancedBufferAttribute(
      new Float32Array(MAX_BLOCKS * 3).fill(1),
      3
    );
    blockMesh.instanceColor.setUsage(THREE.DynamicDrawUsage);

    scene.add(blockMesh);

    // ハイライト枠
    const highlightGeo = new THREE.EdgesGeometry(new THREE.BoxGeometry(1.005, 1.005, 1.005));
    const highlightMat = new THREE.LineBasicMaterial({ color: 0x000000, opacity: 0.7, transparent: true });
    const highlight = new THREE.LineSegments(highlightGeo, highlightMat);
    highlight.visible = false;
    scene.add(highlight);

    const dummy = new THREE.Object3D();
    dummy.matrixAutoUpdate = false;

    // -------------------------
    // UI
    // -------------------------
    const ui = document.getElementById("ui");
    const startButton = document.getElementById("start");

    function updateUI() {
      ui.innerHTML = `
        <b>選択: ${blockTypes[currentBlockType].name}</b><br>
        WASD: 移動 / Shift: ダッシュ / Space: ジャンプ<br>
        左クリック: 破壊 / 右クリック: 設置<br>
        1:草 2:土 3:石 4:木 5:葉 6:砂<br>
        マウス: 視点 / Esc: 停止
      `;
    }
    updateUI();

    // -------------------------
    // 地形生成用ノイズ
    // -------------------------
    function hash2D(x, y) {
      const n = Math.sin(x * 127.1 + y * 311.7) * 43758.5453123;
      return n - Math.floor(n);
    }

    function lerp(a, b, t) {
      return a + (b - a) * t;
    }

    function smoothstep(t) {
      return t * t * (3.0 - 2.0 * t);
    }

    function noise2D(x, y) {
      const ix = Math.floor(x);
      const iy = Math.floor(y);
      const fx = x - ix;
      const fy = y - iy;

      const tx = smoothstep(fx);
      const ty = smoothstep(fy);

      const a = hash2D(ix, iy);
      const b = hash2D(ix + 1, iy);
      const c = hash2D(ix, iy + 1);
      const d = hash2D(ix + 1, iy + 1);

      return lerp(lerp(a, b, tx), lerp(c, d, tx), ty);
    }

    function heightAt(x, z) {
      let h =
        10 +
        6.0 * noise2D(x / 9.0, z / 9.0) +
        4.0 * noise2D(x / 3.0, z / 3.0) +
        1.5 * Math.sin(x * 0.15) * Math.cos(z * 0.18);

      h = Math.max(1, Math.min(24, Math.floor(h)));
      return h;
    }

    // -------------------------
    // ブロック管理
    // -------------------------
    function makeKey(x, y, z) {
      return `${x},${y},${z}`;
    }

    function setInstance(index, key, type) {
      const p = key.split(",");
      const x = Number(p[0]);
      const y = Number(p[1]);
      const z = Number(p[2]);

      dummy.position.set(x + 0.5, y + 0.5, z + 0.5);
      dummy.rotation.set(0, 0, 0);
      dummy.scale.set(1, 1, 1);
      dummy.updateMatrix();

      blockMesh.setMatrixAt(index, dummy.matrix);
      blockMesh.setColorAt(index, blockTypes[type].color);

      blockMesh.instanceMatrix.needsUpdate = true;
      if (blockMesh.instanceColor) blockMesh.instanceColor.needsUpdate = true;
    }

    function addBlock(x, y, z, type) {
      const key = makeKey(x, y, z);
      if (blocks.has(key)) return false;
      if (instanceKeys.length >= MAX_BLOCKS) return false;

      const index = instanceKeys.length;

      blocks.set(key, type);
      blockToInstance.set(key, index);
      instanceKeys.push(key);
      instanceTypes.push(type);

      setInstance(index, key, type);

      blockMesh.count = instanceKeys.length;
      blockMesh.instanceMatrix.needsUpdate = true;
      if (blockMesh.instanceColor) blockMesh.instanceColor.needsUpdate = true;

      return true;
    }

    function removeBlock(x, y, z) {
      const key = makeKey(x, y, z);
      if (!blocks.has(key)) return false;

      const index = blockToInstance.get(key);

      blocks.delete(key);
      blockToInstance.delete(key);

      const lastIndex = instanceKeys.length - 1;

      if (index !== lastIndex) {
        const lastKey = instanceKeys[lastIndex];
        const lastType = instanceTypes[lastIndex];

        instanceKeys[index] = lastKey;
        instanceTypes[index] = lastType;
        blockToInstance.set(lastKey, index);

        setInstance(index, lastKey, lastType);
      }

      instanceKeys.pop();
      instanceTypes.pop();

      blockMesh.count = instanceKeys.length;
      blockMesh.instanceMatrix.needsUpdate = true;
      if (blockMesh.instanceColor) blockMesh.instanceColor.needsUpdate = true;

      return true;
    }

    // -------------------------
    // 初期地形
    // -------------------------
    for (let z = -WORLD_HALF; z < WORLD_HALF; z++) {
      for (let x = -WORLD_HALF; x < WORLD_HALF; x++) {
        const h = heightAt(x, z);
        const topY = h - 1;

        for (let y = 0; y < h; y++) {
          let type = 3; // 石

          if (y === topY) type = 1; // 草
          else if (y >= topY - 2) type = 2; // 土

          addBlock(x, y, z, type);
        }

        // まれに木
        if (topY >= 3 && hash2D(x * 3.7, z * 2.3) < 0.022) {
          makeTree(x, topY, z);
        }
      }
    }

    function makeTree(x, groundY, z) {
      const trunkHeight = 4;

      for (let i = 1; i <= trunkHeight; i++) {
        addBlock(x, groundY + i, z, 4); // 木
      }

      // 葉
      for (let ly = 3; ly <= 4; ly++) {
        for (let dx = -2; dx <= 2; dx++) {
          for (let dz = -2; dz <= 2; dz++) {
            if (Math.abs(dx) === 2 && Math.abs(dz) === 2) continue;
            if (dx === 0 && dz === 0) continue;
            addBlock(x + dx, groundY + ly, z + dz, 5);
          }
        }
      }

      for (let dx = -1; dx <= 1; dx++) {
        for (let dz = -1; dz <= 1; dz++) {
          if (dx === 0 && dz === 0) continue;
          addBlock(x + dx, groundY + 5, z + dz, 5);
        }
      }
    }

    // -------------------------
    // プレイヤー初期位置
    // -------------------------
    function resetPlayer() {
      const h = heightAt(0, 0);
      player.x = 0;
      player.y = h + 0.2;
      player.z = 0;
      player.vx = 0;
      player.vy = 0;
      player.vz = 0;
      player.onGround = false;
    }
    resetPlayer();

    // -------------------------
    // 衝突判定
    // -------------------------
    function isSolidCell(cx, cy, cz) {
      return blocks.has(makeKey(cx, cy, cz));
    }

    function collides(px, py, pz) {
      const x0 = Math.floor(px - PLAYER_HALF_WIDTH);
      const x1 = Math.floor(px + PLAYER_HALF_WIDTH - 0.0001);

      const y0 = Math.floor(py);
      const y1 = Math.floor(py + PLAYER_HEIGHT - 0.0001);

      const z0 = Math.floor(pz - PLAYER_HALF_WIDTH);
      const z1 = Math.floor(pz + PLAYER_HALF_WIDTH - 0.0001);

      for (let x = x0; x <= x1; x++) {
        for (let y = y0; y <= y1; y++) {
          for (let z = z0; z <= z1; z++) {
            if (isSolidCell(x, y, z)) return true;
          }
        }
      }

      return false;
    }

    function blockOverlapsPlayer(cx, cy, cz) {
      const px0 = player.x - PLAYER_HALF_WIDTH;
      const px1 = player.x + PLAYER_HALF_WIDTH;
      const py0 = player.y;
      const py1 = player.y + PLAYER_HEIGHT;
      const pz0 = player.z - PLAYER_HALF_WIDTH;
      const pz1 = player.z + PLAYER_HALF_WIDTH;

      return (
        px0 < cx + 1 &&
        px1 > cx &&
        py0 < cy + 1 &&
        py1 > cy &&
        pz0 < cz + 1 &&
        pz1 > cz
      );
    }

    function moveX(dx) {
      if (dx === 0) return;

      player.x += dx;

      if (collides(player.x, player.y, player.z)) {
        if (dx > 0) {
          const solidX = Math.floor(player.x + PLAYER_HALF_WIDTH);
          player.x = solidX - PLAYER_HALF_WIDTH - 0.0005;
        } else {
          const solidX = Math.floor(player.x - PLAYER_HALF_WIDTH);
          player.x = solidX + 1 + PLAYER_HALF_WIDTH + 0.0005;
        }
        player.vx = 0;
      }
    }

    function moveZ(dz) {
      if (dz === 0) return;

      player.z += dz;

      if (collides(player.x, player.y, player.z)) {
        if (dz > 0) {
          const solidZ = Math.floor(player.z + PLAYER_HALF_WIDTH);
          player.z = solidZ - PLAYER_HALF_WIDTH - 0.0005;
        } else {
          const solidZ = Math.floor(player.z - PLAYER_HALF_WIDTH);
          player.z = solidZ + 1 + PLAYER_HALF_WIDTH + 0.0005;
        }
        player.vz = 0;
      }
    }

    function moveY(dy) {
      if (dy === 0) return;

      player.y += dy;

      if (collides(player.x, player.y, player.z)) {
        if (dy < 0) {
          const solidY = Math.floor(player.y);
          player.y = solidY + 1;
          player.vy = 0;
          player.onGround = true;
        } else {
          const solidY = Math.floor(player.y + PLAYER_HEIGHT);
          player.y = solidY - PLAYER_HEIGHT - 0.0005;
          player.vy = 0;
        }
      }
    }

    function updateGroundState() {
      player.onGround = false;

      if (!collides(player.x, player.y, player.z)) {
        if (player.vy <= 0.5 && collides(player.x, player.y - 0.15, player.z)) {
          player.onGround = true;
        }
      }
    }

    // -------------------------
    // レイで向いているブロックを取得
    // -------------------------
    const rayDir = new THREE.Vector3();

    function pickBlock(maxDistance = 7) {
      camera.getWorldDirection(rayDir);

      const ox = camera.position.x;
      const oy = camera.position.y;
      const oz = camera.position.z;

      const dx = rayDir.x;
      const dy = rayDir.y;
      const dz = rayDir.z;

      let x = Math.floor(ox);
      let y = Math.floor(oy);
      let z = Math.floor(oz);

      const stepX = dx > 0 ? 1 : -1;
      const stepY = dy > 0 ? 1 : -1;
      const stepZ = dz > 0 ? 1 : -1;

      const tDeltaX = dx !== 0 ? Math.abs(1 / dx) : Infinity;
      const tDeltaY = dy !== 0 ? Math.abs(1 / dy) : Infinity;
      const tDeltaZ = dz !== 0 ? Math.abs(1 / dz) : Infinity;

      let tMaxX = dx > 0 ? (Math.floor(ox + 1) - ox) / dx : (Math.floor(ox) - ox) / dx;
      let tMaxY = dy > 0 ? (Math.floor(oy + 1) - oy) / dy : (Math.floor(oy) - oy) / dy;
      let tMaxZ = dz > 0 ? (Math.floor(oz + 1) - oz) / dz : (Math.floor(oz) - oz) / dz;

      let t = 0;

      let nx = 0;
      let ny = 0;
      let nz = 0;

      while (t <= maxDistance) {
        if (blocks.has(makeKey(x, y, z))) {
          return { x, y, z, nx, ny, nz };
        }

        if (tMaxX < tMaxY && tMaxX < tMaxZ) {
          x += stepX;
          t = tMaxX;
          tMaxX += tDeltaX;
          nx = -stepX;
          ny = 0;
          nz = 0;
        } else if (tMaxY < tMaxZ) {
          y += stepY;
          t = tMaxY;
          tMaxY += tDeltaY;
          nx = 0;
          ny = -stepY;
          nz = 0;
        } else {
          z += stepZ;
          t = tMaxZ;
          tMaxZ += tDeltaZ;
          nx = 0;
          ny = 0;
          nz = -stepZ;
        }

        if (Number.isNaN(t)) return null;
      }

      return null;
    }

    function updateHover() {
      hoveredBlock = pickBlock(7);

      if (hoveredBlock) {
        highlight.visible = true;
        highlight.position.set(hoveredBlock.x + 0.5, hoveredBlock.y + 0.5, hoveredBlock.z + 0.5);
      } else {
        highlight.visible = false;
      }
    }

    // -------------------------
    // ブロック操作
    // -------------------------
    function breakBlock() {
      if (!hoveredBlock) return;

      const { x, y, z } = hoveredBlock;
      removeBlock(x, y, z);
    }

    function placeBlock() {
      if (!hoveredBlock) return;

      const bx = hoveredBlock.x + hoveredBlock.nx;
      const by = hoveredBlock.y + hoveredBlock.ny;
      const bz = hoveredBlock.z + hoveredBlock.nz;

      if (by < -1 || by > 64) return;
      if (bx < -WORLD_HALF - 8 || bx >= WORLD_HALF + 8) return;
      if (bz < -WORLD_HALF - 8 || bz >= WORLD_HALF + 8) return;

      if (blockOverlapsPlayer(bx, by, bz)) return;

      addBlock(bx, by, bz, currentBlockType);
    }

    // -------------------------
    // 入力
    // -------------------------
    document.addEventListener("keydown", (e) => {
      if (e.code === "Space") e.preventDefault();
      if (e.repeat) return;

      keys[e.code] = true;

      if (e.code === "Digit1") setCurrentBlockType(1);
      if (e.code === "Digit2") setCurrentBlockType(2);
      if (e.code === "Digit3") setCurrentBlockType(3);
      if (e.code === "Digit4") setCurrentBlockType(4);
      if (e.code === "Digit5") setCurrentBlockType(5);
      if (e.code === "Digit6") setCurrentBlockType(6);
    });

    document.addEventListener("keyup", (e) => {
      keys[e.code] = false;
    });

    function setCurrentBlockType(type) {
      currentBlockType = type;
      updateUI();
    }

    document.addEventListener("contextmenu", (e) => {
      e.preventDefault();
    });

    document.addEventListener("pointerlockchange", () => {
      const locked = document.pointerLockElement === renderer.domElement;
      startButton.style.display = locked ? "none" : "block";
    });

    startButton.addEventListener("click", () => {
      renderer.domElement.requestPointerLock();
    });

    document.addEventListener("mousemove", (e) => {
      if (document.pointerLockElement !== renderer.domElement) return;

      const sensitivity = 0.0022;
      yaw -= e.movementX * sensitivity;
      pitch -= e.movementY * sensitivity;

      const maxPitch = Math.PI / 2 - 0.05;
      pitch = Math.max(-maxPitch, Math.min(maxPitch, pitch));
    });

    renderer.domElement.addEventListener("mousedown", (e) => {
      if (document.pointerLockElement !== renderer.domElement) return;

      if (e.button === 0) breakBlock();
      else if (e.button === 2) placeBlock();

      e.preventDefault();
    });

    // -------------------------
    // 物理更新
    // -------------------------
    const forwardVec = new THREE.Vector3();
    const rightVec = new THREE.Vector3();

    function updatePlayer(dt) {
      forwardVec.set(-Math.sin(yaw), 0, -Math.cos(yaw));
      rightVec.set(Math.cos(yaw), 0, -Math.sin(yaw));

      let mx = 0;
      let mz = 0;

      if (keys["KeyW"]) {
        mx += forwardVec.x;
        mz += forwardVec.z;
      }
      if (keys["KeyS"]) {
        mx -= forwardVec.x;
        mz -= forwardVec.z;
      }
      if (keys["KeyD"]) {
        mx += rightVec.x;
        mz += rightVec.z;
      }
      if (keys["KeyA"]) {
        mx -= rightVec.x;
        mz -= rightVec.z;
      }

      const len = Math.hypot(mx, mz);
      if (len > 0) {
        mx /= len;
        mz /= len;
      }

      const moveSpeed = keys["ShiftLeft"] ? SPRINT_SPEED : WALK_SPEED;

      const targetVx = mx * moveSpeed;
      const targetVz = mz * moveSpeed;

      const acceleration = 22.0;
      player.vx += (targetVx - player.vx) * Math.min(1.0, dt * acceleration);
      player.vz += (targetVz - player.vz) * Math.min(1.0, dt * acceleration);

      if (keys["Space"] && player.onGround) {
        player.vy = JUMP_POWER;
        player.onGround = false;
      }

      const speed = Math.hypot(player.vx, player.vy, player.vz);
      const maxStep = 0.15;
      const steps = Math.max(1, Math.ceil((speed * dt) / maxStep));

      for (let i = 0; i < steps; i++) {
        const h = dt / steps;

        player.vy -= GRAVITY * h;

        if (player.vy < -55) player.vy = -55;

        moveX(player.vx * h);
        moveZ(player.vz * h);
        moveY(player.vy * h);
      }

      updateGroundState();

      // 落下しすぎたらリセット
      if (player.y < -25) resetPlayer();

      // 外に出すぎない範囲
      const minX = -WORLD_HALF + PLAYER_HALF_WIDTH;
      const maxX = WORLD_HALF - PLAYER_HALF_WIDTH;
      const minZ = -WORLD_HALF + PLAYER_HALF_WIDTH;
      const maxZ = WORLD_HALF - PLAYER_HALF_WIDTH;

      if (player.x < minX) {
        player.x = minX;
        player.vx = 0;
      }
      if (player.x > maxX) {
        player.x = maxX;
        player.vx = 0;
      }
      if (player.z < minZ) {
        player.z = minZ;
        player.vz = 0;
      }
      if (player.z > maxZ) {
        player.z = maxZ;
        player.vz = 0;
      }
    }

    function updateCamera() {
      camera.position.set(player.x, player.y + EYE_HEIGHT, player.z);
      camera.quaternion.setFromEuler(new THREE.Euler(pitch, yaw, 0, "YXZ"));
      camera.updateMatrixWorld(true);
    }

    // -------------------------
    // リサイズ
    // -------------------------
    window.addEventListener("resize", () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    });

    // -------------------------
    // メインループ
    // -------------------------
    let lastTime = performance.now();

    function animate() {
      requestAnimationFrame(animate);

      const now = performance.now();
      let dt = (now - lastTime) / 1000;
      lastTime = now;
      dt = Math.min(dt, 0.05);

      updatePlayer(dt);
      updateCamera();
      updateHover();

      renderer.render(scene, camera);
    }

    animate();
  </script>
</body>
</html>
```

**遊び方**

1. `index.html` をダブルクリックで開く  
2. 画面上の「クリックでゲーム開始」を押す  
3. マウスで視点操作  
4. `WASD` で移動、`Shift` でダッシュ、`Space` でジャンプ  
5. 左クリックでブロック破壊、右クリックで設置  
6. `1〜6` でブロック種類選択  
   - 1: 草  
   - 2: 土  
   - 3: 石  
   - 4: 木  
   - 5: 葉  
   - 6: 砂