以下は、ブラウザだけでできる「マイクラ風 3D 箱庭ゲーム」の単一 HTML 版です。  
Copy して `index.html` として保存し、ブラウザで開くと起動します。

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>マイクラ風 3D 箱庭ゲーム</title>
  <style>
    body {
      margin: 0;
      overflow: hidden;
      font-family: sans-serif;
      background: #111;
    }
    canvas {
      display: block;
    }
    #hud {
      position: fixed;
      top: 12px;
      left: 12px;
      color: #fff;
      pointer-events: none;
      font-size: 14px;
    }
    #hotbar {
      position: fixed;
      bottom: 12px;
      left: 12px;
      display: flex;
      gap: 8px;
      pointer-events: none;
    }
    #hotbar button {
      pointer-events: auto;
      background: #222;
      color: #fff;
      border: 1px solid #555;
      padding: 8px 10px;
    }
    #hotbar button.active {
      background: #0a7;
    }
    #info {
      position: fixed;
      bottom: 48px;
      left: 12px;
      color: #fff;
      pointer-events: none;
      font-size: 14px;
    }
  </style>
</head>
<body>
  <div id="hud">
    WASD: 移動 / Space: ジャンプ / 鼠: 視点<br>
    左クリック: 破壊 / 右クリック: 設置<br>
    1~5: 設置ブロック選択<br>
    床・岩・木・葉・草・基盤など
  </div>

  <div id="hotbar">
    <button data-id="1" class="active">1: 草</button>
    <button data-id="2">2: 土</button>
    <button data-id="3">3: 石</button>
    <button data-id="4">4: 木</button>
    <button data-id="5">5: 葉</button>
  </div>

  <div id="info">Ready</div>

  <script src="https://cdn.jsdelivr.net/npm/three@0.158.0/build/three.min.js"></script>
  <script>
    const AIR = 0;
    const GRASS = 1;
    const DIRT = 2;
    const STONE = 3;
    const WOOD = 4;
    const LEAVES = 5;
    const BEDROCK = 6;

    const W = 64;
    const H = 40;
    const D = 64;

    const blocks = new Uint8Array(W * H * D);

    const PLAYER_HALF = 0.3;
    const PLAYER_HEIGHT = 1.8;

  function idx(x, y, z) {
    return x * H * D + y * D + z;
  }

  function inBounds(x, y, z) {
    return x >= 0 && x < W && y >= 0 && y < H && z >= 0 && z < D;
  }

  function getBlock(x, y, z) {
    if (!inBounds(x, y, z)) return AIR;
    return blocks[idx(x, y, z)];
  }

  function setBlock(x, y, z, type) {
    if (!inBounds(x, y, z)) return;
    blocks[idx(x, y, z)] = type;
  }

  function isSolid(x, y, z) {
    return getBlock(x, y, z) !== AIR;
  }

  function hash(x, z) {
    let h = (x * 2654435761 + z * 929124133) ^ 0x9e3779b9;
    h ^= h >>> 13;
    h = (h * 1274126177) >>> 0;
    return (h % 1000) / 1000;
  }

  function getTerrainHeight(x, z) {
    let h = 8;
    h += 3.5 * Math.sin(x * 0.14) * Math.cos(z * 0.13);
    h += 2.5 * Math.sin(x * 0.07 + z * 0.11);
    h += 2.0 * Math.sin((x + z) * 0.06);
    h += hash(x, z) * 6 - 3;
    return Math.max(2, Math.min(28, Math.floor(h)));
  }

  function placeTree(x, z) {
    const h = getTerrainHeight(x, z);
    if (h < 3 || h + 4 >= H) return;

    for (let y = h; y < h + 4; y++) {
      setBlock(x, y, z, WOOD);
    }

    for (let dy = -2; dy <= 1; dy++) {
      const y = h + 3 + dy;
      for (let dx = -2; dx <= 2; dx++) {
        for (let dz = -2; dz <= 2; dz++) {
          if (dx === 0 && dz === 0) continue;
          if (dx * dx + dz * dz + dy * dy <= 6) {
            if (getBlock(x + dx, y, z + dz) === AIR) {
              setBlock(x + dx, y, z + dz, LEAVES);
            }
          }
        }
      }
    }
  }

  function generateWorld() {
    for (let x = 0; x < W; x++) {
      for (let z = 0; z < D; z++) {
        const top = getTerrainHeight(x, z);
        for (let y = 0; y < top; y++) {
          if (y === 0) {
            setBlock(x, y, z, BEDROCK);
          } else if (y === top - 1) {
            setBlock(x, y, z, GRASS);
          } else if (y >= top - 4) {
            setBlock(x, y, z, DIRT);
          } else {
            setBlock(x, y, z, STONE);
          }
        }
      }
    }

    for (let x = 1; x < W - 1; x++) {
      for (let z = 1; z < D - 1; z++) {
        if (Math.random() < 0.02) {
          placeTree(x, z);
        }
      }
    }
  }

  generateWorld();

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x79a4e0);
  scene.fog = new THREE.FogExp2(0x79a4e0, 0.018);

  const camera = new THREE.PerspectiveCamera(
    70,
    window.innerWidth / window.innerHeight,
    0.1,
    160
  );
  camera.rotation.order = "YXZ";

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  document.body.appendChild(renderer.domElement);

  const material = new THREE.MeshBasicMaterial({ vertexColors: true });
  const worldMesh = new THREE.Mesh(new THREE.BufferGeometry(), material);
  scene.add(worldMesh);

  const targetBox = new THREE.Mesh(
    new THREE.BoxGeometry(1.04, 1.04, 1.04),
    new THREE.MeshBasicMaterial({
      color: 0x00ff00,
      wireframe: true
    })
  );
  scene.add(targetBox);
  targetBox.visible = false;

  function faceColor(block, nx, ny, nz) {
    if (block === GRASS) {
      if (ny > 0) return [0.44, 0.74, 0.38];
      if (ny < 0) return [0.42, 0.24, 0.13];
      return [0.52, 0.57, 0.38];
    }
    if (block === DIRT) return [0.36, 0.23, 0.15];
    if (block === STONE) return [0.51, 0.55, 0.58];
    if (block === WOOD) return [0.52, 0.40, 0.27];
    if (block === LEAVES) return [0.24, 0.52, 0.28];
    if (block === BEDROCK) return [0.12, 0.12, 0.13];
    return [1, 1, 1];
  }

  function addFace(positions, normals, colors, x, y, z, nx, ny, nz, block) {
    const c = faceColor(block, nx, ny, nz);
    const pts = [];

    if (nx === 1) {
      pts = [
        x + 1, y, z,
        x + 1, y + 1, z,
        x + 1, y + 1, z + 1,
        x + 1, y, z + 1
      ];
    } else if (nx === -1) {
      pts = [
        x, y, z + 1,
        x, y + 1, z + 1,
        x, y + 1, z,
        x, y, z
      ];
    } else if (ny === 1) {
      pts = [
        x, y + 1, z,
        x, y + 1, z + 1,
        x + 1, y + 1, z + 1,
        x + 1, y + 1, z
      ];
    } else if (ny === -1) {
      pts = [
        x, y, z,
        x + 1, y, z,
        x + 1, y, z + 1,
        x, y, z + 1
      ];
    } else if (nz === 1) {
      pts = [
        x, y, z + 1,
        x + 1, y, z + 1,
        x + 1, y + 1, z + 1,
        x, y + 1, z + 1
      ];
    } else {
      pts = [
        x, y, z,
        x, y + 1, z,
        x + 1, y + 1, z,
        x + 1, y, z
      ];
    }

    positions.push(
      pts[0], pts[1], pts[2],
      pts[3], pts[4], pts[5],
      pts[6], pts[7], pts[8]
    );
    positions.push(
      pts[0], pts[1], pts[2],
      pts[6], pts[7], pts[8],
      pts[9], pts[10], pts[11]
    );

    for (let i = 0; i < 6; i++) {
      normals.push(nx, ny, nz);
      colors.push(c[0], c[1], c[2]);
    }
  }

  function buildMesh() {
    const positions = [];
    const normals = [];
    const colors = [];

    for (let x = 0; x < W; x++) {
      for (let z = 0; z < D; z++) {
        for (let y = 0; y < H; y++) {
          const block = getBlock(x, y, z);
          if (!block) continue;

          if (!isSolid(x + 1, y, z)) addFace(positions, normals, colors, x, y, z, 1, 0, 0, block);
          if (!isSolid(x - 1, y, z)) addFace(positions, normals, colors, x, y, z, -1, 0, 0, block);
          if (!isSolid(x, y + 1, z)) addFace(positions, normals, colors, x, y, z, 0, 1, 0, block);
          if (y > 0 && !isSolid(x, y - 1, z)) addFace(positions, normals, colors, x, y, z, 0, -1, 0, block);
          if (!isSolid(x, y, z + 1)) addFace(positions, normals, colors, x, y, z, 0, 0, 1, block);
          if (!isSolid(x, y, z - 1)) addFace(positions, normals, colors, x, y, z, 0, 0, -1, block);
        }
      }
    }

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
    geometry.setAttribute("normal", new THREE.Float32BufferAttribute(normals, 3));
    geometry.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));

    if (worldMesh.geometry) worldMesh.geometry.dispose();
    worldMesh.geometry = geometry;
  }

  const player = {
    x: W / 2 + 0.5,
    y: 0,
    z: D / 2 + 0.5,
    vy: 0
  };

  player.y = getTerrainHeight(Math.floor(player.x), Math.floor(player.z));

  const yaw = 0.0;
  const pitch = -0.25;

  const keys = {};

  window.addEventListener("keydown", (e) => {
    if (e.key === "w") keys.w = true;
    if (e.key === "a") keys.a = true;
    if (e.key === "s") keys.s = true;
    if (e.key === "d") keys.d = true;
    if (e.key === " ") keys.space = true;

    if (e.key === "1") selectedBlock = GRASS;
    if (e.key === "2") selectedBlock = DIRT;
    if (e.key === "3") selectedBlock = STONE;
    if (e.key === "4") selectedBlock = WOOD;
    if (e.key === "5") selectedBlock = LEAVES;

    if (e.key === "l") breakBlock();
    if (e.key === "r") placeBlock();
  });

  window.addEventListener("keyup", (e) => {
    if (e.key === "w") keys.w = false;
    if (e.key === "a") keys.a = false;
    if (e.key === "s") keys.s = false;
    if (e.key === "d") keys.d = false;
    if (e.key === " ") keys.space = false;
  });

  window.addEventListener("contextmenu", (e) => {
    e.preventDefault();
  });

  let selectedBlock = GRASS;

  const hotbarButtons = document.querySelectorAll("#hotbar button");
  hotbarButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      selectedBlock = Number(btn.dataset.id);
      hotbarButtons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      info.textContent = "Selected: " + btn.textContent;
    });
  });

  const raycaster = new THREE.Raycaster();
  raycaster.far = 6;

  function getTarget() {
    const dir = new THREE.Vector3();
    camera.getWorldDirection(dir);
    raycaster.set(camera.position, dir);

    const hits = raycaster.intersectObject(worldMesh);
    if (!hits.length) return null;

    const hit = hits[0];
    if (hit.distance > 6) return null;

    const n = hit.face.normal;

    const x = Math.floor(hit.point.x - n.x * 0.1);
    const y = Math.floor(hit.point.y - n.y * 0.1);
    const z = Math.floor(hit.point.z - n.z * 0.1);

    if (!inBounds(x, y, z)) return null;

    const id = getBlock(x, y, z);
    if (id === AIR) return null;

    return { x, y, z, nx: n.x, ny: n.y, nz: n.z, id };
  }

  function voxelOverlapsPlayer(x, y, z) {
    return (
      x < player.x + PLAYER_HALF &&
      x + 1 > player.x - PLAYER_HALF &&
      y < player.y + PLAYER_HEIGHT &&
      y + 1 > player.y &&
      z < player.z + PLAYER_HALF &&
      z + 1 > player.z - PLAYER_HALF
    );
  }

  function breakBlock() {
    const t = getTarget();
    if (!t) return;
    if (t.id === BEDROCK) {
      info.textContent = "Bedrock cannot be broken.";
      return;
    }

    setBlock(t.x, t.y, t.z, AIR);
    buildMesh();
    info.textContent = "Block removed.";
  }

  function placeBlock() {
    const t = getTarget();
    if (!t) return;

    const nx = t.x + t.nx;
    const ny = t.y + t.ny;
    const nz = t.z + t.nz;

    if (!inBounds(nx, ny, nz)) return;
    if (getBlock(nx, ny, nz) !== AIR) return;
    if (voxelOverlapsPlayer(nx, ny, nz)) return;

    setBlock(nx, ny, nz, selectedBlock);
    buildMesh();
    info.textContent = "Block placed.";
  }

  renderer.domElement.addEventListener("mousedown", (e) => {
    if (e.button === 0) breakBlock();
    if (e.button === 2) placeBlock();
  });

  renderer.domElement.addEventListener("click", () => {
    try {
      renderer.domElement.requestPointerLock();
    } catch (err) {
      // ignore
    }
  });

  document.addEventListener("mousemove", (e) => {
    const dx = e.movementX ?? (e.clientX - lastMouseX);
    const dy = e.movementY ?? (e.clientY - lastMouseY);

    yaw -= dx * 0.003;
    pitch -= dy * 0.003;

    pitch = Math.max(-Math.PI / 2 + 0.05, Math.min(Math.PI / 2 - 0.05, pitch));

    lastMouseX = e.clientX;
    lastMouseY = e.clientY;
  });

  let lastMouseX = 0;
  let lastMouseY = 0;

  function collides(px, py, pz) {
    const xMin = Math.floor(px - PLAYER_HALF);
    const xMax = Math.floor(px + PLAYER_HALF);
    const yMin = Math.floor(py);
    const yMax = Math.floor(py + PLAYER_HEIGHT - 1e-6);
    const zMin = Math.floor(pz - PLAYER_HALF);
    const zMax = Math.floor(pz + PLAYER_HALF);

    for (let x = xMin; x <= xMax; x++) {
      for (let y = yMin; y <= yMax; y++) {
        for (let z = zMin; z <= zMax; z++) {
          if (isSolid(x, y, z)) {
            const overlap =
              x + 1 > px - PLAYER_HALF + 1e-6 &&
              x < px + PLAYER_HALF - 1e-6 &&
              y + 1 > py + 1e-6 &&
              y < py + PLAYER_HEIGHT - 1e-6 &&
              z + 1 > pz - PLAYER_HALF + 1e-6 &&
              z < pz + PLAYER_HALF - 1e-6;

            if (overlap) return true;
          }
        }
      }
    }

    return false;
  }

  function isOnGround(px, py, pz) {
    const xMin = Math.floor(px - PLAYER_HALF);
    const xMax = Math.floor(px + PLAYER_HALF);
    const yMin = Math.floor(py - 0.05);
    const yMax = Math.floor(py);
    const zMin = Math.floor(pz - PLAYER_HALF);
    const zMax = Math.floor(pz + PLAYER_HALF);

    for (let x = xMin; x <= xMax; x++) {
      for (let y = yMin; y <= yMax; y++) {
        for (let z = zMin; z <= zMax; z++) {
          if (isSolid(x, y, z)) return true;
        }
      }
    }
    return false;
  }

  function tryMove(dx, dy, dz) {
    if (!collides(player.x + dx, player.y, player.z)) {
      player.x += dx;
    }

    if (!collides(player.x, player.y + dy, player.z)) {
      player.y += dy;
    }

    if (!collides(player.x, player.y, player.z + dz)) {
      player.z += dz;
    }
  }

  let lastTime = performance.now();

  function loop() {
    const now = performance.now();
    const dt = Math.min(0.05, (now - lastTime) / 1000);
    lastTime = now;

    const moveSpeed = 6;
    const forward = new THREE.Vector3(Math.sin(yaw), 0, -Math.cos(yaw));
    const right = new THREE.Vector3(Math.cos(yaw), 0, Math.sin(yaw));

    let dx = 0;
    let dz = 0;

    if (keys.w) {
      dx += forward.x;
      dz += forward.z;
    }
    if (keys.s) {
      dx -= forward.x;
      dz -= forward.z;
    }
    if (keys.d) {
      dx += right.x;
      dz += right.z;
    }
    if (keys.a) {
      dx -= right.x;
      dz -= right.z;
    }

    const moveLen = Math.sqrt(dx * dx + dz * dz);
    if (moveLen > 0) {
      dx /= moveLen;
      dz /= moveLen;
      tryMove(dx * moveSpeed * dt, 0, dz * moveSpeed * dt);
    }

    player.vy -= 22 * dt;

    const ground = isOnGround(player.x, player.y, player.z);

    if (keys.space && ground && player.vy <= 0.1) {
      player.vy = 7.5;
    }

    const dy = player.vy * dt;
    const py = player.y + dy;

    if (!collides(player.x, py, player.z)) {
      player.y = py;
    } else {
      if (dy < 0) {
        // Snap to nearest ground.
        const xMin = Math.floor(player.x - PLAYER_HALF);
        const xMax = Math.floor(player.x + PLAYER_HALF);
        const zMin = Math.floor(player.z - PLAYER_HALF);
        const zMax = Math.floor(player.z + PLAYER_HALF);
        const yMin = Math.floor(py);
        const yMax = Math.floor(py + PLAYER_HEIGHT);

        let bestY = player.y;
        for (let x = xMin; x <= xMax; x++) {
          for (let y = yMin; y <= yMax; y++) {
            for (let z = zMin; z <= zMax; z++) {
              if (isSolid(x, y, z)) {
                const topY = y + 1;
                if (topY > bestY) bestY = topY;
              }
            }
          }
        }

        if (bestY !== player.y) {
          if (!collides(player.x, bestY, player.z)) {
            player.y = bestY;
            player.vy = 0;
          }
        } else {
          player.vy = 0;
        }
      }
    }

    camera.position.set(player.x, player.y + 1.6, player.z);
    camera.rotation.y = yaw;
    camera.rotation.x = pitch;

    const target = getTarget();
    if (target) {
      targetBox.visible = true;
      targetBox.position.set(target.x + 0.5, target.y + 0.5, target.z + 0.5);
    } else {
      targetBox.visible = false;
    }

    renderer.render(scene, camera);
  }

  function updateSize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  }

  window.addEventListener("resize", updateSize);

  buildMesh();
  info.textContent = "Ready. Click canvas, then move mouse and WASD.";

  loop();
  setInterval(loop, 1000 / 60);
</script>
</body>
</html>
```

## 操作

- **W / A / S / D**: 移動
- **Space**: ジャンプ
- **鼠**: 視点操作
- **左クリック**: 破壊
- **右クリック**: 設置
- **1~5**: 設置ブロック選択
  - 1: 草
  - 2: 土
  - 3: 石
  - 4: 木
  - 5: 葉
- **L**: 破壊
- **R**: 設置

## 特徴

- 3D 体素地形
- 木・葉の樹生成
- 床・土・草・石・基盤
- 第一人称視点
- 重力・ジャンプ・碰撞判定
- ブロック破壊・設置
- 対象ブロックの绿色枠表示

このままブラウザで開くと playable になります。  
もし Want, I can next add inventory, crafting, water, caves, saving world, or mobile controls.