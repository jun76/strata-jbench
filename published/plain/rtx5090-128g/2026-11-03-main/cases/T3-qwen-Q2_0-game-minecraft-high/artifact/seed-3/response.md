以下の単一 HTML ファイルを保存して、ブラウザで開くとマイクラ風 3D 箱庭ゲームが動作します。  
`index.html` として保存してください。

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8" />
  <title>マイクラ風 3D 箱庭ゲーム</title>
  <style>
    body {
      margin: 0;
      overflow: hidden;
      font-family: system-ui, sans-serif;
    }

    #ui {
      position: fixed;
      top: 10px;
      left: 10px;
      background: rgba(255, 255, 255, 0.88);
      padding: 12px 14px;
      border-radius: 10px;
      box-shadow: 0 8px 22px rgba(0, 0, 0, 0.25);
      pointer-events: none;
      font-size: 14px;
      line-height: 1.45;
      max-width: 360px;
    }

    #ui h2 {
      margin: 0 0 6px;
      font-size: 16px;
    }

    .key {
      font-weight: 700;
      color: #2b4c4a;
    }

    .small {
      color: #555;
      font-size: 13px;
    }
  </style>
</head>
<body>
  <div id="ui">
    <h2>マイクラ風 3D 箱庭</h2>
    <div><span class="key">Click</span>: mouse lock</div>
    <div><span class="key">W A S D</span>: move</div>
    <div><span class="key">Space</span>: jump</div>
    <div><span class="key">Q</span> / <span class="key">E</span>: fly down / up</div>
    <div><span class="key">Mouse</span>: look around</div>
    <div><span class="key">Left click</span>: remove block</div>
    <div><span class="key">Right click</span>: place block</div>
    <div><span class="key">1-4</span>: choose block type</div>
    <div><span class="key">N</span>: regenerate terrain</div>
    <div class="small">1 grass / 2 dirt / 3 stone / 4 sand</div>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js"></script>
  <script>
    const SIZE = 32;
    const MAX_Y = 24;
    const MAX_BLOCKS = 50000;

    const COLORS = [
      0x377f4a, // grass
      0x6f4b2f, // dirt
      0x9c9c9c, // stone
      0xd4b57d  // sand
    ];

    let currentType = 0;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x8fb3d6);

    const camera = new THREE.PerspectiveCamera(
      72,
      window.innerWidth / window.innerHeight,
      0.1,
      2000
    );
    camera.rotation.order = "YXZ";
    camera.position.set(SIZE / 2, 12, SIZE / 2);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    document.body.appendChild(renderer.domElement);

    const canvas = renderer.domElement;

    const sun = new THREE.DirectionalLight(0xffffff, 1.1);
    sun.position.set(30, 50, 20);
    scene.add(sun);

    scene.add(new THREE.AmbientLight(0xffffff, 0.55));

    const grid = [];

    function createEmptyGrid() {
      for (let x = 0; x < SIZE; x++) {
        grid[x] = new Array(MAX_Y);
        for (let y = 0; y < MAX_Y; y++) {
          grid[x][y] = new Array(SIZE).fill(false);
        }
      }
    }

    createEmptyGrid();

    const boxGeometry = new THREE.BoxGeometry(1, 1, 1);
    const material = new THREE.MeshStandardMaterial({
      roughness: 0.85,
      metalness: 0.0
    });

    const mesh = new THREE.InstancedMesh(boxGeometry, material, MAX_BLOCKS);
    mesh.count = 0;

    mesh.instanceMatrix.setUsage(THREE.DynamicUsage);
    mesh.instanceColor = new THREE.InstancedBufferAttribute(
      new Float32Array(MAX_BLOCKS * 3),
      3
    );
    mesh.instanceColor.setUsage(THREE.DynamicUsage);

    scene.add(mesh);

    const blockInfo = new Array(MAX_BLOCKS);
    const blockMap = new Map();

    const dummy = new THREE.Object3D();

    function encode(x, y, z) {
      return ((x * MAX_Y + y) * SIZE) + z;
    }

    function isSolid(x, y, z) {
      if (x < 0 || x >= SIZE || y < 0 || y >= MAX_Y || z < 0 || z >= SIZE) {
        return false;
      }
      return grid[x][y][z];
    }

    function setInstance(idx, x, y, z, type) {
      dummy.position.set(x + 0.5, y + 0.5, z + 0.5);
      dummy.updateMatrix();
      mesh.setMatrixAt(idx, dummy.matrix);
      mesh.setColor(idx, new THREE.Color(COLORS[type]));
    }

    function addBlock(x, y, z, type) {
      if (x < 0 || x >= SIZE || y < 0 || y >= MAX_Y || z < 0 || z >= SIZE) {
        return false;
      }

      if (grid[x][y][z]) return false;
      if (mesh.count >= MAX_BLOCKS) return false;

      const idx = mesh.count++;
      grid[x][y][z] = true;

      blockInfo[idx] = { x, y, z, type };
      blockMap.set(encode(x, y, z), idx);
      setInstance(idx, x, y, z, type);

      return true;
    }

    function removeBlockAtIdx(idx) {
      if (idx === undefined || idx < 0 || idx >= mesh.count) return;

      const info = blockInfo[idx];
      if (!info) return;

      const last = mesh.count - 1;

      grid[info.x][info.y][info.z] = false;
      blockMap.delete(encode(info.x, info.y, info.z));

      if (last !== idx) {
        const lastInfo = blockInfo[last];

        if (lastInfo) {
          blockInfo[idx] = lastInfo;
          setInstance(idx, lastInfo.x, lastInfo.y, lastInfo.z, lastInfo.type);
          blockMap.set(encode(lastInfo.x, lastInfo.y, lastInfo.z), idx);
        }
      }

      blockInfo[last] = null;
      mesh.count--;
    }

    function removeBlockAt(x, y, z) {
      const idx = blockMap.get(encode(x, y, z));
      if (idx !== undefined) {
        removeBlockAtIdx(idx);
      }
    }

    function terrainHeight(x, z) {
      const h =
        3 +
        2.2 * Math.sin(x * 0.25 + z * 0.11) +
        1.5 * Math.cos(x * 0.14 - z * 0.23) +
        0.8 * Math.sin((x + z) * 0.33 + 0.5);

      return Math.max(2, Math.min(9, Math.floor(h)));
    }

    function generateTerrain() {
      for (let x = 0; x < SIZE; x++) {
        for (let z = 0; z < SIZE; z++) {
          const h = terrainHeight(x, z);

          for (let y = 0; y < h; y++) {
            let type;

            if (y === h - 1) {
              type = 0;
            } else if (y >= h - 2) {
              type = 1;
            } else {
              type = 2;
            }

            addBlock(x, y, z, type);
          }
        }
      }
    }

    generateTerrain();

    const player = new THREE.Vector3(SIZE / 2, 12, SIZE / 2);
    const velocity = new THREE.Vector3();
    const keys = new Set();

    let yaw = 0;
    let pitch = 0.1;

    const BODY_RADIUS = 0.3;
    const BODY_HEIGHT = 1.8;
    const EPS = 1e-6;

    function collides(px, py, pz) {
      const minx = px - BODY_RADIUS;
      const maxx = px + BODY_RADIUS;
      const miny = py - BODY_HEIGHT / 2;
      const maxy = py + BODY_HEIGHT / 2;
      const minz = pz - BODY_RADIUS;
      const maxz = pz + BODY_RADIUS;

      const x0 = Math.floor(minx + EPS);
      const x1 = Math.floor(maxx - EPS);
      const y0 = Math.floor(miny + EPS);
      const y1 = Math.floor(maxy - EPS);
      const z0 = Math.floor(minz + EPS);
      const z1 = Math.floor(maxz - EPS);

      if (x0 > x1 || y0 > y1 || z0 > z1) return false;

      for (let x = x0; x <= x1; x++) {
        for (let y = y0; y <= y1; y++) {
          for (let z = z0; z <= z1; z++) {
            if (isSolid(x, y, z)) {
              return true;
            }
          }
        }
      }

      return false;
    }

    function grounded(px, py, pz) {
      const y = Math.floor(py - BODY_HEIGHT / 2 - 0.05);

      const x0 = Math.floor(px - BODY_RADIUS + EPS);
      const x1 = Math.floor(px + BODY_RADIUS - EPS);
      const z0 = Math.floor(pz - BODY_RADIUS + EPS);
      const z1 = Math.floor(pz + BODY_RADIUS - EPS);

      if (x0 > x1 || z0 > z1) return false;

      for (let x = x0; x <= x1; x++) {
        for (let z = z0; z <= z1; z++) {
          if (isSolid(x, y, z)) {
            return true;
          }
        }
      }

      return false;
    }

    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2(0, 0);

    function rayAction(place) {
      raycaster.setFromCamera(mouse, camera);

      const hits = raycaster.intersectObject(mesh);
      if (hits.length === 0) return;

      const hit = hits[0];
      const info = blockInfo[hit.instanceId];

      if (!info) return;

      if (place) {
        const n = hit.normal;

        const nx = info.x + Math.round(n.x);
        const ny = info.y + Math.round(n.y);
        const nz = info.z + Math.round(n.z);

        if (nx < 0 || nx >= SIZE || ny < 0 || ny >= MAX_Y || nz < 0 || nz >= SIZE) {
          return;
        }

        if (grid[nx][ny][nz]) return;

        const cx = nx + 0.5;
        const cy = ny + 0.5;
        const cz = nz + 0.5;

        if (
          Math.abs(cx - player.x) < 0.8 &&
          Math.abs(cy - player.y) < 1.4 &&
          Math.abs(cz - player.z) < 0.8
        ) {
          return;
        }

        addBlock(nx, ny, nz, currentType);
      } else {
        removeBlockAtIdx(hit.instanceId);
      }
    }

    document.addEventListener("pointerlockchange", () => {
      const locked = document.pointerLockElement === canvas;
      if (locked) {
        document.getElementById("ui").innerHTML = `
          <h2>マイクラ風 3D 箱庭</h2>
          <div><span class="key">W A S D</span>: move</div>
          <div><span class="key">Space</span>: jump</div>
          <div><span class="key">Q</span> / <span class="key">E</span>: fly down / up</div>
          <div><span class="key">Mouse</span>: look around</div>
          <div><span class="key">Left click</span>: remove block</div>
          <div><span class="key">Right click</span>: place block</div>
          <div><span class="key">1-4</span>: choose block type</div>
          <div><span class="key">N</span>: regenerate terrain</div>
          <div class="small">1 grass / 2 dirt / 3 stone / 4 sand</div>
        `;
      }
    });

    canvas.addEventListener("click", () => {
      if (document.pointerLockElement !== canvas) {
        canvas.requestPointerLock();
      }
    });

    canvas.addEventListener("contextmenu", (e) => {
      e.preventDefault();
    });

    document.addEventListener("mousemove", (e) => {
      if (document.pointerLockElement !== canvas) return;

      yaw += e.movementX * 0.002;
      pitch -= e.movementY * 0.002;

      pitch = Math.max(-1.2, Math.min(1.2, pitch));
      yaw = yaw % (2 * Math.PI);
    });

    canvas.addEventListener("mousedown", (e) => {
      if (document.pointerLockElement !== canvas) return;

      if (e.button === 0) {
        rayAction(false); // remove
      } else if (e.button === 2) {
        rayAction(true);  // place
      }
    });

    document.addEventListener("keydown", (e) => {
      const key = e.key.toLowerCase();
      keys.add(key);

      if (e.code === "Space") {
        keys.add("space");
      }

      if (key === "1") currentType = 0;
      if (key === "2") currentType = 1;
      if (key === "3") currentType = 2;
      if (key === "4") currentType = 3;

      if (key === "n") {
        mesh.count = 0;
        blockMap.clear();

        for (let x = 0; x < SIZE; x++) {
          for (let y = 0; y < MAX_Y; y++) {
            grid[x][y].fill(false);
            blockInfo[x * MAX_Y * SIZE + y * SIZE] = null;
          }
        }

        blockInfo.fill(null);

        generateTerrain();

        player.set(SIZE / 2, 12, SIZE / 2);
        velocity.set(0, 0, 0);
        yaw = 0;
        pitch = 0.1;
      }
    });

    document.addEventListener("keyup", (e) => {
      const key = e.key.toLowerCase();
      keys.delete(key);

      if (e.code === "Space") {
        keys.delete("space");
      }
    });

    window.addEventListener("resize", () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    });

    function update(dt) {
      const acceleration = 70;

      let ax = 0;
      let az = 0;

      if (keys.has("w")) {
        ax += Math.sin(yaw);
        az -= Math.cos(yaw);
      }

      if (keys.has("s")) {
        ax -= Math.sin(yaw);
        az += Math.cos(yaw);
      }

      if (keys.has("d")) {
        ax += Math.cos(yaw);
        az += Math.sin(yaw);
      }

      if (keys.has("a")) {
        ax -= Math.cos(yaw);
        az -= Math.sin(yaw);
      }

      velocity.x += ax * acceleration * dt;
      velocity.z += az * acceleration * dt;

      const damp = Math.exp(-3.5 * dt);
      velocity.x *= damp;
      velocity.z *= damp;

      // gravity
      velocity.y -= 16 * dt;

      if (keys.has("space") && grounded(player.x, player.y, player.z)) {
        velocity.y = 9;
      }

      if (keys.has("e")) {
        velocity.y += 16 * dt;
      }

      if (keys.has("q")) {
        velocity.y -= 16 * dt;
      }

      // horizontal collision
      const nx = player.x + velocity.x * dt;
      if (!collides(nx, player.y, player.z)) {
        player.x = nx;
      } else {
        velocity.x = 0;
      }

      const nz = player.z + velocity.z * dt;
      if (!collides(player.x, player.y, nz)) {
        player.z = nz;
      } else {
        velocity.z = 0;
      }

      const ny = player.y + velocity.y * dt;
      if (!collides(player.x, ny, player.z)) {
        player.y = ny;
      } else {
        if (velocity.y < 0) {
          velocity.y = 0;
        }
      }

      if (player.y < 0.5) {
        player.y = 0.5;
        velocity.y = 0;
      }

      camera.position.copy(player);
      camera.rotation.set(pitch, yaw, 0);
    }

    let last = performance.now();

    function animate() {
      const now = performance.now();
      const dt = Math.min(0.05, (now - last) / 1000);
      last = now;

      update(dt);
      renderer.render(scene, camera);

      requestAnimationFrame(animate);
    }

    animate();
  </script>
</body>
</html>
```

操作:

- 画面をクリック → mouse lock
- `W A S D`: 移動
- `Space`: 跳
- `Q` / `E`: 下 / 上
- mouse: 視点
- left click: block 破壊
- right click: block 放置
- `1`: grass
- `2`: dirt
- `3`: stone
- `4`: sand
- `N`: terrain 再生