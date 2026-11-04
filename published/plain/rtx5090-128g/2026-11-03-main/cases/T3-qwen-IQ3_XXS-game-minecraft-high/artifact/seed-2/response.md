以下は**マイクラ風の3D箱庭ゲーム**を単一HTMLで遊べる形にしたものです。PCブラウザ向けで、マウスポインターロックで操作します。

- WASD移動
- Spaceジャンプ
- Shift走る
- 左クリック：ブロック破壊
- 右クリック：ブロック設置
- 1〜7：ホットバー選択
- Esc：カーソル解放

そのまま `.html` として保存して開けば動きます。

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>マイクラ風 3D 箱庭ゲーム</title>
  <style>
    html, body {
      margin: 0;
      height: 100%;
      overflow: hidden;
      background: #000;
      font-family: "Segoe UI", "Hiragino Kaku Gothic ProN", "Noto Sans JP", sans-serif;
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
      background: rgba(0, 0, 0, 0.72);
      color: white;
      z-index: 30;
      text-align: center;
      cursor: pointer;
    }
    #overlay h1 {
      margin: 0 0 10px;
      font-size: 30px;
      text-shadow: 0 2px 8px rgba(0,0,0,.8);
    }
    #overlay p {
      margin: 4px 0;
      font-size: 15px;
      color: #ddd;
    }
    #info {
      position: fixed;
      top: 12px;
      left: 12px;
      z-index: 10;
      color: white;
      background: rgba(0, 0, 0, 0.45);
      padding: 10px 12px;
      border-radius: 10px;
      font-size: 13px;
      line-height: 1.5;
      pointer-events: none;
    }
    #blockName {
      position: fixed;
      bottom: 82px;
      left: 50%;
      transform: translateX(-50%);
      z-index: 10;
      color: white;
      background: rgba(0, 0, 0, 0.45);
      padding: 6px 12px;
      border-radius: 8px;
      font-size: 14px;
      pointer-events: none;
    }
    #hotbar {
      position: fixed;
      bottom: 12px;
      left: 50%;
      transform: translateX(-50%);
      z-index: 10;
      display: flex;
      gap: 4px;
      background: rgba(0, 0, 0, 0.45);
      padding: 5px;
      border-radius: 10px;
    }
    .slot {
      width: 58px;
      height: 58px;
      border: 2px solid #666;
      border-radius: 8px;
      color: white;
      font-size: 11px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: transform .1s, border-color .1s, box-shadow .1s;
      text-align: center;
    }
    .slot:hover {
      transform: translateY(-2px);
    }
    .slot.selected {
      border-color: white;
      box-shadow: 0 0 14px rgba(255,255,255,.55);
    }
    .num {
      font-weight: 700;
      opacity: .85;
      margin-bottom: 4px;
    }
    #crosshair {
      position: fixed;
      left: 50%;
      top: 50%;
      width: 24px;
      height: 24px;
      transform: translate(-50%, -50%);
      z-index: 20;
      pointer-events: none;
      mix-blend-mode: difference;
    }
    #crosshair::before,
    #crosshair::after {
      content: "";
      position: absolute;
      background: white;
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
  <div id="overlay">
    <div>
      <h1>マイクラ風 3D 箱庭ゲーム</h1>
      <p>クリックで開始</p>
      <p>WASD：移動 / Space：ジャンプ / Shift：走る</p>
      <p>左クリック：破壊 / 右クリック：設置</p>
      <p>1〜7：ブロック選択 / Esc：カーソル解放</p>
    </div>
  </div>

  <div id="crosshair"></div>
  <div id="info"></div>
  <div id="blockName"></div>
  <div id="hotbar"></div>

  <script type="module">
    import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js";

    // -----------------------------
    // 基本設定
    // -----------------------------
    const SIZE = 32;
    const MAX_Y = 64;
    const EYE_HEIGHT = 1.62;
    const PLAYER_HEIGHT = 1.80;
    const PLAYER_RADIUS = 0.30;

    const AIR = 0;
    const BEDROCK = 1;
    const STONE = 2;
    const DIRT = 3;
    const GRASS = 4;
    const SAND = 5;
    const WOOD = 6;
    const LEAVES = 7;
    const PLANKS = 8;

    const BLOCK_NAMES = {
      [BEDROCK]: "岩床",
      [STONE]: "石",
      [DIRT]: "地面",
      [GRASS]: "草地",
      [SAND]: "砂",
      [WOOD]: "木材",
      [LEAVES]: "葉",
      [PLANKS]: "木板"
    };

    const HOTBAR = [DIRT, GRASS, STONE, SAND, WOOD, PLANKS, LEAVES];
    let selectedHotbarIndex = 0;

    function selectedBlockType() {
      return HOTBAR[selectedHotbarIndex];
    }

    // -----------------------------
    // Three.js シーン
    // -----------------------------
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x87ceeb);
    scene.fog = new THREE.Fog(0x87ceeb, 45, 105);

    const camera = new THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 0.1, 300);
    camera.rotation.order = "YXZ";

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    const hemi = new THREE.HemisphereLight(0xffffff, 0x4d7a2a, 1.0);
    scene.add(hemi);

    const sun = new THREE.DirectionalLight(0xffffff, 1.1);
    sun.position.set(70, 130, 45);
    scene.add(sun);

    // -----------------------------
    // 簡易テクスチャ生成
    // -----------------------------
    function fract(x) {
      return x - Math.floor(x);
    }

    function hash(x, z) {
      return fract(Math.sin(x * 12.9898 + z * 78.233) * 43758.5453);
    }

    function noise(ctx, colors) {
      for (let y = 0; y < 16; y++) {
        for (let x = 0; x < 16; x++) {
          ctx.fillStyle = colors[Math.floor(Math.random() * colors.length)];
          ctx.fillRect(x, y, 1, 1);
        }
      }
    }

    function drawTexture(name) {
      const canvas = document.createElement("canvas");
      canvas.width = 16;
      canvas.height = 16;
      const ctx = canvas.getContext("2d");

      if (name === "bedrock") {
        ctx.fillStyle = "#262626";
        ctx.fillRect(0, 0, 16, 16);
        noise(ctx, ["#101010", "#353535", "#1f1f1f", "#424242", "#161616"]);
      }

      if (name === "stone") {
        ctx.fillStyle = "#8c8c8c";
        ctx.fillRect(0, 0, 16, 16);
        noise(ctx, ["#828282", "#999999", "#737373", "#a7a7a7", "#6b6b6b"]);
      }

      if (name === "dirt") {
        ctx.fillStyle = "#775a38";
        ctx.fillRect(0, 0, 16, 16);
        noise(ctx, ["#6b5132", "#816340", "#5e4529", "#8b6d4a", "#705235"]);
      }

      if (name === "grassTop") {
        ctx.fillStyle = "#549f3d";
        ctx.fillRect(0, 0, 16, 16);
        noise(ctx, ["#4f9437", "#58a840", "#63bd4b", "#468431", "#5f9c3d"]);
      }

      if (name === "grassSide") {
        ctx.fillStyle = "#775a38";
        ctx.fillRect(0, 0, 16, 16);
        for (let y = 0; y < 16; y++) {
          for (let x = 0; x < 16; x++) {
            if (y < 4) {
              ctx.fillStyle = ["#4f9437", "#58a840", "#63bd4b", "#468431"][Math.floor(Math.random() * 4)];
            } else {
              ctx.fillStyle = ["#6b5132", "#816340", "#5e4529", "#8b6d4a"][Math.floor(Math.random() * 4)];
            }
            ctx.fillRect(x, y, 1, 1);
          }
        }
      }

      if (name === "sand") {
        ctx.fillStyle = "#e0cf97";
        ctx.fillRect(0, 0, 16, 16);
        noise(ctx, ["#d4c288", "#ecdaa3", "#c7b57d", "#f1e2ae", "#d8c68e"]);
      }

      if (name === "woodSide") {
        ctx.fillStyle = "#7b5231";
        ctx.fillRect(0, 0, 16, 16);
        for (let x = 0; x < 16; x++) {
          ctx.fillStyle = ["#7f5636", "#6d4428", "#8c613f", "#633920"][Math.floor(Math.random() * 4)];
          ctx.fillRect(x, 0, 1, 16);
        }
        for (let i = 0; i < 24; i++) {
          const x = Math.floor(Math.random() * 16);
          const y = Math.floor(Math.random() * 16);
          ctx.fillStyle = "#4f2f17";
          ctx.fillRect(x, y, 1, 1);
        }
      }

      if (name === "woodEnd") {
        ctx.fillStyle = "#a07343";
        ctx.fillRect(0, 0, 16, 16);
        for (let y = 0; y < 16; y++) {
          for (let x = 0; x < 16; x++) {
            const dx = Math.abs(x - 7.5);
            const dy = Math.abs(y - 7.5);
            const d = Math.max(dx, dy);
            if (d < 2) ctx.fillStyle = "#724d29";
            else if (d < 4) ctx.fillStyle = "#95693d";
            else if (d < 6) ctx.fillStyle = "#ad7f4f";
            else ctx.fillStyle = "#c0925d";
            ctx.fillRect(x, y, 1, 1);
          }
        }
      }

      if (name === "leaves") {
        ctx.fillStyle = "#2f8730";
        ctx.fillRect(0, 0, 16, 16);
        noise(ctx, ["#1f7024", "#3aa03f", "#2a7f2c", "#18651d", "#41b046", "#247726"]);
      }

      if (name === "planks") {
        ctx.fillStyle = "#9d6f42";
        ctx.fillRect(0, 0, 16, 16);
        noise(ctx, ["#8f6036", "#ad7c4d", "#815430", "#b58756"]);
        ctx.fillStyle = "#5f3f22";
        for (let y = 3; y < 16; y += 4) {
          ctx.fillRect(0, y, 16, 1);
        }
        ctx.fillRect(4, 0, 1, 3);
        ctx.fillRect(11, 4, 1, 3);
        ctx.fillRect(2, 8, 1, 3);
        ctx.fillRect(9, 12, 1, 3);
      }

      const texture = new THREE.CanvasTexture(canvas);
      texture.magFilter = THREE.NearestFilter;
      texture.minFilter = THREE.NearestFilter;
      if (THREE.SRGBColorSpace) texture.colorSpace = THREE.SRGBColorSpace;
      texture.needsUpdate = true;
      return texture;
    }

    const texBedrock = drawTexture("bedrock");
    const texStone = drawTexture("stone");
    const texDirt = drawTexture("dirt");
    const texGrassTop = drawTexture("grassTop");
    const texGrassSide = drawTexture("grassSide");
    const texSand = drawTexture("sand");
    const texWoodSide = drawTexture("woodSide");
    const texWoodEnd = drawTexture("woodEnd");
    const texLeaves = drawTexture("leaves");
    const texPlanks = drawTexture("planks");

    function lambert(texture) {
      return new THREE.MeshLambertMaterial({ map: texture });
    }

    const blockGeometry = new THREE.BoxGeometry(1, 1, 1);

    const MATS = [];
    MATS[BEDROCK] = lambert(texBedrock);
    MATS[STONE] = lambert(texStone);
    MATS[DIRT] = lambert(texDirt);
    MATS[GRASS] = [
      lambert(texGrassSide),
      lambert(texGrassSide),
      lambert(texGrassTop),
      lambert(texDirt),
      lambert(texGrassSide),
      lambert(texGrassSide)
    ];
    MATS[SAND] = lambert(texSand);
    MATS[WOOD] = [
      lambert(texWoodSide),
      lambert(texWoodSide),
      lambert(texWoodEnd),
      lambert(texWoodEnd),
      lambert(texWoodSide),
      lambert(texWoodSide)
    ];
    MATS[LEAVES] = lambert(texLeaves);
    MATS[PLANKS] = lambert(texPlanks);

    // -----------------------------
    // voxel world
    // -----------------------------
    const blocks = new Map();
    const blockMeshes = new THREE.Group();
    scene.add(blockMeshes);

    function key(x, y, z) {
      return x + y * SIZE + z * SIZE * MAX_Y;
    }

    function inBounds(x, y, z) {
      return x >= 0 && x < SIZE && z >= 0 && z < SIZE && y >= 0 && y < MAX_Y;
    }

    function addBlock(x, y, z, type) {
      if (!inBounds(x, y, z)) return false;
      const k = key(x, y, z);
      if (blocks.has(k)) return false;

      const mesh = new THREE.Mesh(blockGeometry, MATS[type]);
      mesh.position.set(x + 0.5, y + 0.5, z + 0.5);
      mesh.userData = { x, y, z, type, block: true };

      blocks.set(k, mesh);
      blockMeshes.add(mesh);
      return true;
    }

    function removeBlock(x, y, z) {
      const k = key(x, y, z);
      const mesh = blocks.get(k);
      if (!mesh) return false;
      if (mesh.userData.type === BEDROCK) return false;

      blocks.delete(k);
      blockMeshes.remove(mesh);
      return true;
    }

    // -----------------------------
    // 地形生成
    // -----------------------------
    function heightAt(x, z) {
      const h = 5 + Math.sin(x / 8) + Math.cos(z / 8) + Math.sin((x + z) / 12) + hash(x, z) * 2;
      return Math.max(2, Math.min(11, Math.floor(h)));
    }

    for (let x = 0; x < SIZE; x++) {
      for (let z = 0; z < SIZE; z++) {
        const h = heightAt(x, z);

        for (let y = 0; y <= h; y++) {
          let type = DIRT;

          if (y === 0) {
            type = BEDROCK;
          } else if (y === h) {
            type = h <= 4 ? SAND : GRASS;
          } else if (h - y >= 4) {
            type = STONE;
          } else {
            type = DIRT;
          }

          addBlock(x, y, z, type);
        }
      }
    }

    function addTree(x, z) {
      const h = heightAt(x, z);
      if (h < 5) return;

      const trunkH = 3 + Math.floor(hash(x * 7.3, z * 4.1) * 2);
      for (let i = 1; i <= trunkH; i++) {
        addBlock(x, h + i, z, WOOD);
      }

      const top = h + trunkH;

      // 葉
      for (let dx = -2; dx <= 2; dx++) {
        for (let dz = -2; dz <= 2; dz++) {
          addBlock(x + dx, top - 1, z + dz, LEAVES);
          addBlock(x + dx, top, z + dz, LEAVES);
        }
      }

      for (let dx = -1; dx <= 1; dx++) {
        for (let dz = -1; dz <= 1; dz++) {
          addBlock(x + dx, top + 1, z + dz, LEAVES);
        }
      }
    }

    for (let x = 2; x < SIZE - 2; x++) {
      for (let z = 2; z < SIZE - 2; z++) {
        if (hash(x * 2.1, z * 3.7) > 0.955) {
          addTree(x, z);
        }
      }
    }

    // -----------------------------
    // プレイヤー
    // -----------------------------
    const player = {
      pos: new THREE.Vector3(16.5, heightAt(16, 16) + 1, 16.5),
      vel: new THREE.Vector3(0, 0, 0),
      onGround: false
    };

    let yaw = 0;
    let pitch = 0;
    let locked = false;

    const keys = {};
    const raycaster = new THREE.Raycaster();
    raycaster.far = 6;
    const center = new THREE.Vector2(0, 0);

    const highlight = new THREE.Mesh(
      new THREE.BoxGeometry(1.01, 1.01, 1.01),
      new THREE.MeshBasicMaterial({ color: 0xffffff, wireframe: true, transparent: true, opacity: 0.45 })
    );
    highlight.visible = false;
    scene.add(highlight);

    // -----------------------------
    // 衝突判定
    // -----------------------------
    function intersectsPlayer(px, py, pz) {
      const minX = px - PLAYER_RADIUS;
      const maxX = px + PLAYER_RADIUS;
      const minY = py;
      const maxY = py + PLAYER_HEIGHT;
      const minZ = pz - PLAYER_RADIUS;
      const maxZ = pz + PLAYER_RADIUS;

      const x0 = Math.floor(minX);
      const x1 = Math.floor(maxX);
      const y0 = Math.floor(minY);
      const y1 = Math.floor(maxY);
      const z0 = Math.floor(minZ);
      const z1 = Math.floor(maxZ);

      for (let x = x0; x <= x1; x++) {
        for (let y = y0; y <= y1; y++) {
          for (let z = z0; z <= z1; z++) {
            if (x < 0 || x >= SIZE || z < 0 || z >= SIZE || y < 0 || y >= MAX_Y) continue;

            const mesh = blocks.get(key(x, y, z));
            if (!mesh) continue;

            if (x < maxX && x + 1 > minX &&
                y < maxY && y + 1 > minY &&
                z < maxZ && z + 1 > minZ) {
              return true;
            }
          }
        }
      }
      return false;
    }

    function blockOverlapsPlayer(x, y, z) {
      const minX = player.pos.x - PLAYER_RADIUS;
      const maxX = player.pos.x + PLAYER_RADIUS;
      const minY = player.pos.y;
      const maxY = player.pos.y + PLAYER_HEIGHT;
      const minZ = player.pos.z - PLAYER_RADIUS;
      const maxZ = player.pos.z + PLAYER_RADIUS;

      return x < maxX && x + 1 > minX &&
             y < maxY && y + 1 > minY &&
             z < maxZ && z + 1 > minZ;
    }

    function moveAxis(axis, amount) {
      if (Math.abs(amount) < 1e-7) return;

      const step = 0.05;
      const dir = amount > 0 ? 1 : -1;
      let moved = 0;

      while (true) {
        const remain = amount - moved;
        let d = dir * step;
        if (Math.abs(remain) <= step) d = remain;
        if (d === 0) break;

        player.pos[axis] += d;

        if (intersectsPlayer(player.pos.x, player.pos.y, player.pos.z)) {
          player.pos[axis] -= d;

          if (axis === "y") {
            if (dir < 0) player.onGround = true;
            player.vel.y = 0;
          } else {
            player.vel[axis] = 0;
          }
          break;
        }

        moved += d;

        if (dir > 0 && moved >= amount - 1e-9) break;
        if (dir < 0 && moved <= amount + 1e-9) break;
      }
    }

    // -----------------------------
    // レイキャスト
    // -----------------------------
    function raycast() {
      raycaster.setFromCamera(center, camera);
      const hits = raycaster.intersectObjects(blockMeshes.children, false);
      return hits[0] || null;
    }

    function breakBlock() {
      const hit = raycast();
      if (!hit || !hit.object.userData.block) return;

      const ud = hit.object.userData;
      if (ud.type === BEDROCK) return;

      removeBlock(ud.x, ud.y, ud.z);
    }

    function placeBlock() {
      const hit = raycast();
      if (!hit || !hit.object.userData.block) return;

      const ud = hit.object.userData;

      let normal = new THREE.Vector3(0, 1, 0);
      if (hit.face && hit.face.normal) {
        normal = hit.face.normal.clone();
        normal.transformDirection(hit.object.matrixWorld);
      }

      const nx = ud.x + Math.round(normal.x);
      const ny = ud.y + Math.round(normal.y);
      const nz = ud.z + Math.round(normal.z);

      if (!inBounds(nx, ny, nz)) return;
      if (blocks.has(key(nx, ny, nz))) return;
      if (blockOverlapsPlayer(nx, ny, nz)) return;

      addBlock(nx, ny, nz, selectedBlockType());
    }

    function updateHighlight() {
      if (!locked) {
        highlight.visible = false;
        return;
      }

      const hit = raycast();
      if (hit && hit.object.userData.block) {
        highlight.visible = true;
        highlight.position.copy(hit.object.position);
      } else {
        highlight.visible = false;
      }
    }

    // -----------------------------
    // UI / Input
    // -----------------------------
    const overlay = document.getElementById("overlay");
    const info = document.getElementById("info");
    const blockName = document.getElementById("blockName");
    const hotbar = document.getElementById("hotbar");

    function createHotbar() {
      hotbar.innerHTML = "";

      HOTBAR.forEach((type, i) => {
        const slot = document.createElement("div");
        slot.className = "slot" + (i === selectedHotbarIndex ? " selected" : "");
        slot.innerHTML = `<div class="num">${i + 1}</div><div>${BLOCK_NAMES[type]}</div>`;

        const color = {
          [DIRT]: "#7b5b39",
          [GRASS]: "#4f9437",
          [STONE]: "#8c8c8c",
          [SAND]: "#e0cf97",
          [WOOD]: "#7b5231",
          [PLANKS]: "#9d6f42",
          [LEAVES]: "#2f8730"
        }[type] || "#888";

        slot.style.background = color;
        slot.addEventListener("mousedown", (e) => {
          e.stopPropagation();
          selectHotbar(i);
        });

        hotbar.appendChild(slot);
      });
    }

    function selectHotbar(i) {
      selectedHotbarIndex = Math.max(0, Math.min(HOTBAR.length - 1, i));
      createHotbar();
      blockName.textContent = `選択: ${BLOCK_NAMES[selectedBlockType()]}`;
    }

    createHotbar();
    blockName.textContent = `選択: ${BLOCK_NAMES[selectedBlockType()]}`;

    function lockPointer() {
      if (document.pointerLockElement !== renderer.domElement) {
        renderer.domElement.requestPointerLock();
      }
    }

    overlay.addEventListener("click", lockPointer);

    document.addEventListener("pointerlockchange", () => {
      locked = document.pointerLockElement === renderer.domElement;
      overlay.style.display = locked ? "none" : "flex";
    });

    document.addEventListener("contextmenu", e => e.preventDefault());

    document.addEventListener("mousedown", (e) => {
      if (!locked) {
        lockPointer();
        return;
      }

      if (e.button === 0) {
        breakBlock();
      } else if (e.button === 2) {
        placeBlock();
      }
    });

    document.addEventListener("mousemove", (e) => {
      if (!locked) return;

      const sensitivity = 0.0023;
      yaw -= e.movementX * sensitivity;
      pitch -= e.movementY * sensitivity;

      pitch = Math.max(-Math.PI / 2 + 0.05, Math.min(Math.PI / 2 - 0.05, pitch));
    });

    document.addEventListener("keydown", (e) => {
      keys[e.code] = true;

      if (e.code >= "Digit1" && e.code <= "Digit7") {
        const i = Number(e.code.replace("Digit", "")) - 1;
        selectHotbar(i);
      }

      if (e.code === "Space") e.preventDefault();
    });

    document.addEventListener("keyup", (e) => {
      keys[e.code] = false;
    });

    window.addEventListener("resize", () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    });

    // -----------------------------
    // ゲームループ
    // -----------------------------
    const clock = new THREE.Clock();

    function update(dt) {
      if (locked) {
        const sprint = keys["ShiftLeft"] || keys["ShiftRight"];
        const speed = sprint ? 8 : 5;

        const forward = new THREE.Vector3(-Math.sin(yaw), 0, -Math.cos(yaw));
        const right = new THREE.Vector3(Math.cos(yaw), 0, -Math.sin(yaw));

        let mx = 0;
        let mz = 0;

        if (keys["KeyW"]) { mx += forward.x; mz += forward.z; }
        if (keys["KeyS"]) { mx -= forward.x; mz -= forward.z; }
        if (keys["KeyD"]) { mx += right.x; mz += right.z; }
        if (keys["KeyA"]) { mx -= right.x; mz -= right.z; }

        const len = Math.hypot(mx, mz);
        if (len > 1e-6) {
          mx /= len;
          mz /= len;
        }

        player.vel.x = mx * speed;
        player.vel.z = mz * speed;
        player.vel.y -= 22 * dt;
        if (player.vel.y < -32) player.vel.y = -32;

        if (keys["Space"] && player.onGround) {
          player.vel.y = 9.2;
        }

        player.onGround = false;

        moveAxis("x", player.vel.x * dt);
        moveAxis("z", player.vel.z * dt);
        moveAxis("y", player.vel.y * dt);

        camera.rotation.x = pitch;
        camera.rotation.y = yaw;
        camera.rotation.z = 0;
        camera.position.copy(player.pos);
        camera.position.y += EYE_HEIGHT;
      }

      updateHighlight();

      info.innerHTML = `
        <div>座標: ${player.pos.x.toFixed(1)}, ${player.pos.y.toFixed(1)}, ${player.pos.z.toFixed(1)}</div>
        <div>地面: ${player.onGround ? "はい" : "いいえ"}</div>
        <div>クリック: 破壊 / 右クリック: 設置</div>
      `;
    }

    function animate() {
      const dt = Math.min(clock.getDelta(), 0.1);
      update(dt);
      renderer.render(scene, camera);
      requestAnimationFrame(animate);
    }

    animate();
  </script>
</body>
</html>
```

補足：

- このままだと**32x32の小さな箱庭**です。
- 岩床は破壊できません。
- 木、草、地面、石、砂などがあります。
- 葉や木はランダム生成で出現します。
- 拡張方向は「チャンク分割」「インスタンシング」「チャンク再生成」「ブロック編集データ保存」などです。