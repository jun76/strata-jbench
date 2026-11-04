マイクラ風 3D 箱庭ゲームを、単一の HTML ファイルでブラウザ上に作ります。  
保存してブラウザで開くと動作します。Three.js を CDN 経由で読み込むので、ネット接続が必要です。

## `index.html`

```html
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>Minecraft-like 3D Sandbox</title>
<style>
  html, body {
    margin: 0;
    height: 100%;
    overflow: hidden;
    background: #87ceeb;
    font-family: sans-serif;
    color: #222;
  }

  #canvas {
    width: 100%;
    height: 100%;
    display: block;
    cursor: pointer;
  }

  #ui {
    position: fixed;
    top: 16px;
    left: 16px;
    background: rgba(255, 255, 255, 0.72);
    padding: 12px 16px;
    border-radius: 12px;
    box-shadow: 0 6px 18px rgba(0,0,0,.16);
    font-size: 14px;
    line-height: 1.45;
    user-select: none;
    z-index: 10;
  }

  #hotbar {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: 8px;
    z-index: 10;
  }

  .slot {
    width: 44px;
    height: 44px;
    border-radius: 10px;
    background: rgba(255,255,255,.78);
    border: 2px solid rgba(0,0,0,.16);
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    cursor: pointer;
  }

  .slot.selected {
    border-color: #222;
    box-shadow: 0 0 0 3px rgba(0,0,0,.18);
  }

  .slot .num {
    position: absolute;
    top: 2px;
    left: 4px;
    font-size: 11px;
    color: #333;
  }

  .slot .color {
    width: 28px;
    height: 28px;
    border-radius: 6px;
  }

  .slot .label {
    font-size: 11px;
    margin-left: 3px;
  }

  #overlay {
    position: fixed;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(0,0,0,.35);
    color: #fff;
    z-index: 20;
    cursor: pointer;
  }

  .overlay-card {
    background: rgba(255,255,255,.9);
    color: #222;
    padding: 24px 28px;
    border-radius: 16px;
    box-shadow: 0 10px 30px rgba(0,0,0,.2);
  }
</style>
</head>
<body>
  <div id="ui">
    <div><b>Minecraft-like 3D Sandbox</b></div>
    <div>Click canvas: ポインターロック</div>
    <div>WASD: 移動</div>
    <div>Space: ジャンプ / Fly mode で上昇</div>
    <div>Shift: サニーク / Fly mode で下降</div>
    <div>Left click: 破壊</div>
    <div>Right click: 設置</div>
    <div>1-8: ブロック選択</div>
    <div>F: Fly mode ON/OFF</div>
    <div id="status"></div>
  </div>

  <div id="hotbar"></div>
  <div id="overlay">
    <div class="overlay-card">
      Click to start<br>
      マウスで視点操作になります。
    </div>
  </div>

  <canvas id="canvas"></canvas>

  <script type="importmap">
  {
    "imports": {
      "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js"
    }
  }
  </script>

  <script type="module">
    import * as THREE from "three";

    const canvas = document.getElementById("canvas");
    const overlay = document.getElementById("overlay");
    const statusEl = document.getElementById("status");
    const hotbar = document.getElementById("hotbar");

    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(window.innerWidth, window.innerHeight);

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x87ceeb);
    scene.fog = new THREE.Fog(0x87ceeb, 40, 120);

    const camera = new THREE.PerspectiveCamera(
      70,
      window.innerWidth / window.innerHeight,
      0.1,
      500
    );
    camera.rotation.order = "YXZ";

    const hemisphereLight = new THREE.HemisphereLight(0xffffff, 0x556633, 1.0);
    scene.add(hemisphereLight);

    const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
    dirLight.position.set(20, 30, 10);
    scene.add(dirLight);

    const MAX_BLOCKS = 200000;
    const WORLD_RADIUS = 32;
    const MAX_Y = 64;

    const blockGeometry = new THREE.BoxGeometry(1, 1, 1);
    const blockMaterial = new THREE.MeshLambertMaterial();

    const instMesh = new THREE.InstancedMesh(
      blockGeometry,
      blockMaterial,
      MAX_BLOCKS
    );
    instMesh.instanceColor = new THREE.InstancedBufferAttribute(
      new Float32Array(MAX_BLOCKS * 3),
      3
    );
    instMesh.count = 0;
    scene.add(instMesh);

    const highlightGeometry = new THREE.BoxGeometry(1.02, 1.02, 1.02);
    const highlight = new THREE.LineSegments(
      new THREE.EdgesGeometry(highlightGeometry),
      new THREE.LineBasicMaterial({ color: 0x000000, linewidth: 2 })
    );
    highlight.visible = false;
    scene.add(highlight);

    const TYPES = {
      grass: { name: "Grass", color: 0x70b660, solid: true },
      dirt: { name: "Dirt", color: 0x8b5a2b, solid: true },
      stone: { name: "Stone", color: 0x9a9a9a, solid: true },
      wood: { name: "Wood", color: 0x654a2b, solid: true },
      leaves: { name: "Leaves", color: 0x317c31, solid: true },
      sand: { name: "Sand", color: 0xd8c87a, solid: true },
      brick: { name: "Brick", color: 0x754c46, solid: true },
      glass: { name: "Glass", color: 0x78a5b4, solid: true }
    };

    const hotbarTypes = [
      "grass",
      "dirt",
      "stone",
      "wood",
      "leaves",
      "sand",
      "brick",
      "glass"
    ];

    let selected = "grass";

    function key(x, y, z) {
      return `${x},${y},${z}`;
    }

    function inside(x, y, z) {
      return x >= -WORLD_RADIUS && x <= WORLD_RADIUS &&
             z >= -WORLD_RADIUS && z <= WORLD_RADIUS &&
             y >= 0 && y <= MAX_Y;
    }

    const blockMap = new Map();
    const instanceInfo = new Array(MAX_BLOCKS).fill(null);
    const heightMap = new Map();

    const matrix = new THREE.Matrix4();
    const tmpMatrix = new THREE.Matrix4();
    const tmpColor = new THREE.Color();
    const tmpVector = new THREE.Vector3();

    function setColorAt(idx, type) {
      const c = TYPES[type].color;
      tmpColor.setHex(c);
      instMesh.instanceColor.setXYZ(idx, tmpColor.r, tmpColor.g, tmpColor.b);
    }

    function addBlock(x, y, z, type) {
      if (!inside(x, y, z)) return false;

      const k = key(x, y, z);
      if (blockMap.has(k)) return false;

      if (instMesh.count >= MAX_BLOCKS) return false;

      const idx = instMesh.count;
      const info = { x, y, z, type, idx, key: k };

      matrix.identity();
      matrix.setPosition(x + 0.5, y + 0.5, z + 0.5);

      instMesh.setMatrixAt(idx, matrix);
      setColorAt(idx, type);

      blockMap.set(k, info);
      instanceInfo[idx] = info;

      instMesh.count++;
      instMesh.instanceMatrix.needsUpdate = true;
      instMesh.instanceColor.needsUpdate = true;

      return true;
    }

    function removeBlock(k) {
      const info = blockMap.get(k);
      if (!info) return false;

      const idx = info.idx;
      const lastIdx = instMesh.count - 1;

      blockMap.delete(k);

      if (idx !== lastIdx) {
        const lastInfo = instanceInfo[lastIdx];

        instMesh.getMatrixAt(lastIdx, tmpMatrix);
        instMesh.setMatrixAt(idx, tmpMatrix);

        const colorArray = instMesh.instanceColor.array;
        const src = lastIdx * 3;
        const dst = idx * 3;
        colorArray[dst] = colorArray[src];
        colorArray[dst + 1] = colorArray[src + 1];
        colorArray[dst + 2] = colorArray[src + 2];

        if (lastInfo) {
          instanceInfo[idx] = lastInfo;
          blockMap.set(lastInfo.key, lastInfo);
        }

        instanceInfo[lastIdx] = null;
      } else {
        instanceInfo[idx] = null;
      }

      instMesh.count--;
      instMesh.instanceMatrix.needsUpdate = true;
      instMesh.instanceColor.needsUpdate = true;

      return true;
    }

    function noise(x, z) {
      return Math.sin(x * 0.12) * Math.cos(z * 0.10) * 8
           + Math.sin((x + z) * 0.07) * 5
           + Math.cos((x - z) * 0.13) * 4;
    }

    function generateWorld() {
      for (let x = -WORLD_RADIUS; x <= WORLD_RADIUS; x++) {
        for (let z = -WORLD_RADIUS; z <= WORLD_RADIUS; z++) {
          const h = Math.max(0, Math.round(9 + noise(x, z)));
          heightMap.set(key(x, z), h);

          for (let y = 0; y <= h; y++) {
            let type;

            if (y === h) {
              type = "grass";
            } else if (y >= h - 2) {
              type = "dirt";
            } else {
              type = "stone";
            }

            addBlock(x, y, z, type);
          }
        }
      }

      for (let i = 0; i < 180; i++) {
        const x = Math.floor(Math.random() * (WORLD_RADIUS * 2 + 1)) - WORLD_RADIUS;
        const z = Math.floor(Math.random() * (WORLD_RADIUS * 2 + 1)) - WORLD_RADIUS;

        const h = heightMap.get(key(x, z));
        if (h === undefined) continue;

        const top = blockMap.get(key(x, h, z));
        if (!top || top.type !== "grass") continue;

        for (let dy = 1; dy <= 4; dy++) {
          addBlock(x, h + dy, z, "wood");
        }

        for (let dy = 3; dy <= 5; dy++) {
          for (let dx = -2; dx <= 2; dx++) {
            for (let dz = -2; dz <= 2; dz++) {
              const dist = Math.abs(dx) + Math.abs(dz);
              if (dist > 4) continue;

              const y = h + dy;

              if (dx === 0 && dz === 0 && dy <= 4) continue;

              const k = key(x + dx, y, z + dz);
              if (!blockMap.has(k)) {
                addBlock(x + dx, y, z + dz, "leaves");
              }
            }
          }
        }
      }
    }

    generateWorld();

    const player = {
      pos: new THREE.Vector3(0, 12, 0),
      vel: new THREE.Vector3(0, 0, 0),
      halfWidth: 0.3,
      height: 1.8,
      eye: 1.62,
      onGround: false
    };

    function setSpawn() {
      const h = heightMap.get(key(0, 0)) ?? 0;
      player.pos.set(0, h + 1, 0);
      player.vel.set(0, 0, 0);
    }

    setSpawn();

    function isSolidAt(x, y, z) {
      if (y < 0) return true;
      if (!inside(x, y, z)) return false;

      const info = blockMap.get(key(x, y, z));
      if (!info) return false;

      return TYPES[info.type].solid;
    }

    function getBox(pos) {
      const hw = player.halfWidth;
      return {
        minX: pos.x - hw,
        maxX: pos.x + hw,
        minY: pos.y,
        maxY: pos.y + player.height,
        minZ: pos.z - hw,
        maxZ: pos.z + hw
      };
    }

    function collides(pos) {
      const box = getBox(pos);
      const EPS = 0.001;

      for (let x = Math.floor(box.minX); x <= Math.floor(box.maxX - EPS); x++) {
        for (let y = Math.floor(box.minY); y <= Math.floor(box.maxY - EPS); y++) {
          for (let z = Math.floor(box.minZ); z <= Math.floor(box.maxZ - EPS); z++) {
            if (isSolidAt(x, y, z)) return true;
          }
        }
      }

      return false;
    }

    function isGrounded() {
      const box = getBox(player.pos);
      const EPS = 0.001;

      for (let x = Math.floor(box.minX); x <= Math.floor(box.maxX - EPS); x++) {
        for (let z = Math.floor(box.minZ); z <= Math.floor(box.maxZ - EPS); z++) {
          const y = Math.floor(player.pos.y - EPS);
          if (isSolidAt(x, y, z)) return true;
        }
      }

      return false;
    }

    function tryMoveAxis(axis, delta, allowStep) {
      const prev = player.pos[axis];
      player.pos[axis] = prev + delta;

      if (collides(player.pos)) {
        if (allowStep && (axis === "x" || axis === "z")) {
          const prevY = player.pos.y;

          player.pos[axis] = prev;
          player.pos.y += 1.0;

          if (!collides(player.pos)) {
            player.pos[axis] = prev + delta;

            if (!collides(player.pos)) {
              return true;
            }

            player.pos.y = prevY;
            player.pos[axis] = prev;
            player.vel[axis] = 0;
            return false;
          }

          player.pos.y = prevY;
          player.pos[axis] = prev;
        } else {
          player.pos[axis] = prev;
        }

        player.vel[axis] = 0;
        return false;
      }

      return true;
    }

    const keys = new Set();

    let yaw = 0;
    let pitch = 0;
    let pointerLocked = false;
    let flyMode = false;

    const raycaster = new THREE.Raycaster();
    raycaster.far = 6;

    function getTargetInfo() {
      const dir = new THREE.Vector3();
      camera.getWorldDirection(dir);

      raycaster.set(camera.position, dir);
      const hits = raycaster.intersectObject(instMesh, false);

      if (hits.length === 0) return null;

      const hit = hits[0];
      const idx = hit.instanceId;

      if (idx === undefined || idx >= instMesh.count) return null;

      const info = instanceInfo[idx];
      if (!info) return null;

      return {
        info,
        normal: hit.face ? hit.face.normal.clone() : new THREE.Vector3(0, 1, 0)
      };
    }

    function updateHighlight() {
      const target = getTargetInfo();

      if (!target) {
        highlight.visible = false;
        return null;
      }

      highlight.visible = true;
      highlight.position.set(
        target.info.x + 0.5,
        target.info.y + 0.5,
        target.info.z + 0.5
      );

      return target;
    }

    function breakBlock() {
      const target = getTargetInfo();
      if (!target) return;

      removeBlock(target.info.key);
    }

    function placeBlock() {
      const target = getTargetInfo();
      if (!target) return;

      const info = target.info;
      const normal = target.normal;

      const nx = info.x + Math.round(normal.x);
      const ny = info.y + Math.round(normal.y);
      const nz = info.z + Math.round(normal.z);

      if (!inside(nx, ny, nz)) return;

      const testPos = new THREE.Vector3(nx + 0.5, ny + 0.5, nz + 0.5);

      // プレイヤー本体と重ならない位置だけ設置
      const temp = {
        x: testPos.x - 0.5,
        y: testPos.y - 0.5,
        z: testPos.z - 0.5
      };

      const saved = new THREE.Vector3();
      saved.copy(player.pos);

      player.pos.set(temp.x, temp.y, temp.z);
      const blocked = collides(player.pos);
      player.pos.copy(saved);

      if (blocked) return;

      addBlock(nx, ny, nz, selected);
    }

    function updatePlayer(dt) {
      const speed = flyMode
        ? 7.0
        : (keys.has("ShiftLeft") ? 2.5 : (keys.has("ControlLeft") ? 6.5 : 4.3));

      const dir = new THREE.Vector3();
      camera.getWorldDirection(dir);
      dir.y = 0;
      if (dir.lengthSq() > 0) dir.normalize();

      const right = new THREE.Vector3(-dir.z, 0, dir.x);

      const input = new THREE.Vector3(0, 0, 0);

      if (keys.has("KeyW")) input.add(dir);
      if (keys.has("KeyS")) input.sub(dir);
      if (keys.has("KeyD")) input.add(right);
      if (keys.has("KeyA")) input.sub(right);

      if (input.lengthSq() > 0) input.normalize();

      player.vel.x = input.x * speed;
      player.vel.z = input.z * speed;

      if (flyMode) {
        let vertical = 0;

        if (keys.has("Space")) vertical += 1;
        if (keys.has("ShiftLeft")) vertical -= 1;

        player.vel.y = vertical * speed;
        player.onGround = false;
      } else {
        player.vel.y -= 18.0 * dt;

        if (keys.has("Space") && player.onGround) {
          player.vel.y = 7.5;
        }
      }

      tryMoveAxis("x", player.vel.x * dt, !flyMode);
      tryMoveAxis("z", player.vel.z * dt, !flyMode);
      tryMoveAxis("y", player.vel.y * dt, false);

      if (!flyMode) {
        player.onGround = isGrounded();
      }
    }

    function updateCamera() {
      camera.position.copy(player.pos);
      camera.position.y += player.eye;

      camera.rotation.y = yaw;
      camera.rotation.x = pitch;
    }

    function hexToCss(hex) {
      return "#" + hex.toString(16).padStart(6, "0");
    }

    function renderHotbar() {
      hotbar.innerHTML = "";

      hotbarTypes.forEach((type, i) => {
        const slot = document.createElement("div");
        slot.className = "slot" + (selected === type ? " selected" : "");
        slot.addEventListener("click", () => {
          selected = type;
          renderHotbar();
        });

        const num = document.createElement("span");
        num.className = "num";
        num.textContent = String(i + 1);

        const color = document.createElement("span");
        color.className = "color";
        color.style.background = hexToCss(TYPES[type].color);

        const label = document.createElement("span");
        label.className = "label";
        label.textContent = TYPES[type].name;

        slot.appendChild(num);
        slot.appendChild(color);
        slot.appendChild(label);

        hotbar.appendChild(slot);
      });
    }

    renderHotbar();

    window.addEventListener("keydown", (e) => {
      keys.add(e.code);

      if (e.code === "KeyF") {
        flyMode = !flyMode;
        player.vel.y = 0;
      }

      const digitMatch = e.code.match(/^Digit([1-8])$/);
      if (digitMatch) {
        const n = Number(digitMatch[1]);
        if (hotbarTypes[n - 1]) {
          selected = hotbarTypes[n - 1];
          renderHotbar();
        }
      }
    });

    window.addEventListener("keyup", (e) => {
      keys.delete(e.code);
    });

    window.addEventListener("mousemove", (e) => {
      if (!pointerLocked) return;

      const sensitivity = 0.0022;

      yaw += e.movementX * sensitivity;
      pitch += e.movementY * sensitivity;

      const minPitch = -Math.PI / 2 + 0.05;
      const maxPitch = Math.PI / 2 - 0.05;

      pitch = Math.max(minPitch, Math.min(maxPitch, pitch));
    });

    function startPointerLock() {
      canvas.requestPointerLock();
      overlay.style.display = "none";
    }

    overlay.addEventListener("click", startPointerLock);
    canvas.addEventListener("click", () => {
      if (!pointerLocked) startPointerLock();
    });

    document.addEventListener("pointerlockchange", () => {
      pointerLocked = document.pointerLockElement === canvas;
      if (pointerLocked) overlay.style.display = "none";
    });

    window.addEventListener("contextmenu", (e) => {
      e.preventDefault();
    });

    window.addEventListener("mousedown", (e) => {
      if (!pointerLocked) return;

      if (e.button === 0) {
        breakBlock();
      } else if (e.button === 2) {
        placeBlock();
      }
    });

    window.addEventListener("resize", () => {
      renderer.setSize(window.innerWidth, window.innerHeight);
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
    });

    let last = performance.now();
    let frameCount = 0;
    let lastStatus = performance.now();

    function updateStatus() {
      const fps = Math.round(1000 / ((performance.now() - lastStatus) / Math.max(frameCount, 1)));
      statusEl.textContent =
        `Selected: ${TYPES[selected].name} | FPS: ${fps} | Fly: ${flyMode ? "ON" : "OFF"}`;

      frameCount = 0;
      lastStatus = performance.now();
    }

    function animate() {
      requestAnimationFrame(animate);

      const now = performance.now();
      const dt = Math.min((now - last) / 1000, 0.05);
      last = now;

      frameCount++;

      updatePlayer(dt);
      updateCamera();
      updateHighlight();

      renderer.render(scene, camera);

      if (now - lastStatus > 1000) {
        updateStatus();
      }
    }

    animate();
  </script>
</body>
</html>
```

## 使い方

1. ファイル名を `index.html` で保存する。
2. ブラウザで開く。
3. 画面をクリックしてポインターロック。
4. `WASD` で移動。
5. `Space` でジャンプ。
6. 左クリックでブロック破壊。
7. 右クリックでブロック設置。
8. `1` から `8` でホットバー選択。
9. `F` で Fly mode ON/OFF。

このまま改造して、ブロック textures、日替わり、水、クラフト、マルチプレイなどに拡張しやすい構造です。