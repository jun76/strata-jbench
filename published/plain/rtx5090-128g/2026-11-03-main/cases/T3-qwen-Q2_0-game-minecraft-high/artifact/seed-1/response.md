これは Three.js による「マイクラ風 3D 箱庭」の単一 HTML 版です。保存してブラウザで開けば、移動・視点・ブロック放置・壊す・ジャンプ などができます。

## 保存するファイル名

```text
minecraft_sandbox.html
```

## 単一 HTML 版

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>マイクラ風 3D 箱庭</title>
  <style>
    body {
      margin: 0;
      overflow: hidden;
      background: #0f172a;
      font-family: sans-serif;
    }

    #ui {
      position: fixed;
      top: 10px;
      left: 10px;
      background: rgba(0, 0, 0, 0.35);
      padding: 10px;
      border-radius: 8px;
      color: white;
    }

    button {
      margin: 4px;
      padding: 6px 10px;
      border-radius: 6px;
      border: 1px solid rgba(255,255,255,0.3);
      background: rgba(255,255,255,0.1);
      color: white;
      cursor: pointer;
    }

    button.active {
      background: rgba(255,255,255,0.35);
    }

    #help {
      position: fixed;
      bottom: 10px;
      left: 10px;
      background: rgba(0,0,0,0.35);
      padding: 10px;
      border-radius: 8px;
      color: white;
      font-size: 12px;
      max-width: 640px;
    }
  </style>
</head>
<body>
  <div id="ui">
    <strong>ブロック種類</strong><br>
    <button data-type="1" class="active">草</button>
    <button data-type="2">石</button>
    <button data-type="3">木</button>
    <button data-type="4">ガラス</button>
    <button data-type="5">タイル</button>
    <button data-type="6">砂</button>
  </div>

  <div id="help">
    WASD: 移動  
    左クリック: 放置  
    右クリック: 壊す  
    Space: ジャンプ  
    E: 放置  
    Q: 壊す  
    左ボタン押し + 鼠の鼠の動: 視点  
  </div>

  <script src="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js"></script>
  <script>
    const W = 32;
    const D = 32;
    const H = 20;

    const blockDefs = [
      null,
      { name: "草", color: 0x4ea469 },
      { name: "石", color: 0x7f7f7f },
      { name: "木", color: 0x8b5a2b },
      { name: "ガラス", color: 0x89b7d8, transparent: true },
      { name: "タイル", color: 0xd25f5f },
      { name: "砂", color: 0xd8b77b }
    ];

    const blocks = new Uint8Array(W * D * H);

    function index(x, y, z) {
      return y * W * D + z * W + x;
    }

    function getBlock(x, y, z) {
      if (x < 0 || x >= W || y < 0 || y >= H || z < 0 || z >= D) return 0;
      return blocks[index(x, y, z)];
    }

    function setBlock(x, y, z, type) {
      if (x < 0 || x >= W || y < 0 || y >= H || z < 0 || z >= D) return;
      blocks[index(x, y, z)] = type;
      rebuild();
    }

    function generateWorld() {
      for (let x = 0; x < W; x++) {
        for (let z = 0; z < D; z++) {
          const h = Math.max(1, Math.min(H - 2, 6 + Math.floor(3 * Math.sin(x * 0.21) * Math.cos(z * 0.19))));

          for (let y = 0; y < H; y++) {
            if (y < h) {
              let t = 2;
              if (y === h - 1) t = 1;

              if (y < h - 1 && Math.random() < 0.02) t = 5;

              blocks[index(x, y, z)] = t;
            }
          }

          if (h < H - 3 && Math.random() < 0.035) {
            const treeHeight = 1 + Math.floor(Math.random() * 2);
            for (let dy = 1; dy <= treeHeight; dy++) {
              if (h + dy < H) {
                blocks[index(x, h + dy, z)] = 3;
              }
            }
          }
        }
      }
    }

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0f172a);
    scene.fog = new THREE.Fog(0x0f172a, 35, 90);

    const camera = new THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 0.1, 200);
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setClearColor(0x0f172a);
    document.body.appendChild(renderer.domElement);

    const geometry = new THREE.BoxGeometry(1, 1, 1);
    const meshes = [];

    for (let t = 1; t < blockDefs.length; t++) {
      const def = blockDefs[t];
      const material = new THREE.MeshStandardMaterial({
        color: def.color,
        roughness: def.transparent ? 0.2 : 0.85,
        transparent: def.transparent,
        opacity: def.transparent ? 0.7 : 1.0
      });

      const mesh = new THREE.InstancedMesh(geometry, material, W * D * H);
      mesh.count = 0;
      scene.add(mesh);
      meshes[t] = mesh;
    }

    function rebuild() {
      const counts = new Array(blockDefs.length).fill(0);
      const matrix = new THREE.Matrix4();

      for (let y = 0; y < H; y++) {
        for (let z = 0; z < D; z++) {
          for (let x = 0; x < W; x++) {
            const type = blocks[index(x, y, z)];
            if (!type) continue;

            matrix.setTranslation(x + 0.5, y + 0.5, z + 0.5);
            meshes[type].setMatrixAt(counts[type], matrix);
            counts[type]++;
          }
        }
      }

      for (let t = 1; t < blockDefs.length; t++) {
        meshes[t].count = counts[t];
        meshes[t].instanceMatrix.needsUpdate = true;
      }
    }

    const light = new THREE.DirectionalLight(0xffffff, 1.2);
    light.position.set(20, 40, 10);
    scene.add(light);

    scene.add(new THREE.AmbientLight(0xffffff, 0.35));

    generateWorld();
    rebuild();

    const player = {
      x: 16.5,
      y: 10,
      z: 16.5,
      vx: 0,
      vy: 0,
      vz: 0,
      yaw: 0,
      pitch: -0.2,
      grounded: false
    };

    let currentType = 1;
    const keys = {};

    function forwardHorizontal() {
      return new THREE.Vector3(
        Math.sin(player.yaw),
        0,
        Math.cos(player.yaw)
      );
    }

    function rightHorizontal() {
      return new THREE.Vector3(
        Math.cos(player.yaw),
        0,
        -Math.sin(player.yaw)
      );
    }

    function forwardVector() {
      const cp = Math.cos(player.pitch);
      return new THREE.Vector3(
        Math.sin(player.yaw) * cp,
        Math.sin(player.pitch),
        Math.cos(player.yaw) * cp
      );
    }

    function playerCollides(x, y, z) {
      const minX = Math.max(0, Math.floor(x - 0.3));
      const maxX = Math.min(W - 1, Math.floor(x + 0.3 - 1e-6));

      const minY = Math.max(0, Math.floor(y));
      const maxY = Math.min(H - 1, Math.floor(y + 1.8 - 1e-6));

      const minZ = Math.max(0, Math.floor(z - 0.3));
      const maxZ = Math.min(D - 1, Math.floor(z + 0.3 - 1e-6));

      for (let ix = minX; ix <= maxX; ix++) {
        for (let iy = minY; iy <= maxY; iy++) {
          for (let iz = minZ; iz <= maxZ; iz++) {
            if (getBlock(ix, iy, iz)) return true;
          }
        }
      }

      return false;
    }

    function isGrounded() {
      const checkY = Math.floor(player.y - 0.01);
      if (checkY < 0 || checkY >= H) return false;

      const ix0 = Math.floor(player.x - 0.3);
      const ix1 = Math.floor(player.x + 0.3 - 1e-6);
      const iz0 = Math.floor(player.z - 0.3);
      const iz1 = Math.floor(player.z + 0.3 - 1e-6);

      for (let ix = ix0; ix <= ix1; ix++) {
        for (let iz = iz0; iz <= iz1; iz++) {
          if (getBlock(ix, checkY, iz)) return true;
        }
      }

      return false;
    }

    function updatePhysics(dt) {
      const fh = forwardHorizontal();
      const rh = rightHorizontal();

      let mx = 0;
      let mz = 0;

      if (keys["w"]) {
        mx += fh.x;
        mz += fh.z;
      }
      if (keys["s"]) {
        mx -= fh.x;
        mz -= fh.z;
      }
      if (keys["d"]) {
        mx += rh.x;
        mz += rh.z;
      }
      if (keys["a"]) {
        mx -= rh.x;
        mz -= rh.z;
      }

      const len = Math.sqrt(mx * mx + mz * mz);
      if (len > 1) {
        mx /= len;
        mz /= len;
      }

      player.vx = mx * 5;
      player.vz = mz * 5;

      if (keys[" "] && isGrounded()) {
        player.vy = 8;
        player.grounded = false;
      }

      player.vy -= 20 * dt;
      if (player.vy < -25) player.vy = -25;

      const nx = player.x + player.vx * dt;
      if (!playerCollides(nx, player.y, player.z)) {
        player.x = nx;
      }

      const ny = player.y + player.vy * dt;
      if (!playerCollides(player.x, ny, player.z)) {
        player.y = ny;
        player.grounded = isGrounded();
      } else {
        if (player.vy < 0) {
          player.grounded = true;
        } else {
          player.grounded = false;
        }
        player.vy = 0;
      }

      const nz = player.z + player.vz * dt;
      if (!playerCollides(player.x, player.y, nz)) {
        player.z = nz;
      }

      if (player.y < 0) {
        player.y = 1;
        player.vy = 0;
      }

      if (player.y > H) {
        player.y = H;
        player.vy = 0;
      }

      player.x = Math.max(0.4, Math.min(W - 0.4, player.x));
      player.z = Math.max(0.4, Math.min(D - 0.4, player.z));
    }

    function raycast(origin, dir, maxDist = 50) {
      let x = origin.x;
      let y = origin.y;
      let z = origin.z;

      let ix = Math.floor(x);
      let iy = Math.floor(y);
      let iz = Math.floor(z);

      const dx = dir.x;
      const dy = dir.y;
      const dz = dir.z;

      const stepX = dx > 0 ? 1 : dx < 0 ? -1 : 0;
      const stepY = dy > 0 ? 1 : dy < 0 ? -1 : 0;
      const stepZ = dz > 0 ? 1 : dz < 0 ? -1 : 0;

      let tMaxX = Infinity;
      let tMaxY = Infinity;
      let tMaxZ = Infinity;

      if (dx !== 0) {
        tMaxX = stepX > 0 ? ((ix + 1 - x) / dx) : ((ix - x) / dx);
      }
      if (dy !== 0) {
        tMaxY = stepY > 0 ? ((iy + 1 - y) / dy) : ((iy - y) / dy);
      }
      if (dz !== 0) {
        tMaxZ = stepZ > 0 ? ((iz + 1 - z) / dz) : ((iz - z) / dz);
      }

      if (getBlock(ix, iy, iz)) {
        return { x: ix, y: iy, z: iz, nx: 0, ny: 0, nz: 0, t: 0 };
      }

      for (let i = 0; i < 1000; i++) {
        if (tMaxX <= tMaxY && tMaxX <= tMaxZ) {
          const t = tMaxX;
          if (t > maxDist) break;

          ix += stepX;
          const nx = -stepX;

          if (getBlock(ix, iy, iz)) {
            return { x: ix, y: iy, z: iz, nx: nx, ny: 0, nz: 0, t: t };
          }

          tMaxX += 1 / Math.abs(dx);
        } else if (tMaxY <= tMaxX && tMaxY <= tMaxZ) {
          const t = tMaxY;
          if (t > maxDist) break;

          iy += stepY;
          const ny = -stepY;

          if (getBlock(ix, iy, iz)) {
            return { x: ix, y: iy, z: iz, nx: 0, ny: ny, nz: 0, t: t };
          }

          tMaxY += 1 / Math.abs(dy);
        } else {
          const t = tMaxZ;
          if (t > maxDist) break;

          iz += stepZ;
          const nz = -stepZ;

          if (getBlock(ix, iy, iz)) {
            return { x: ix, y: iy, z: iz, nx: 0, ny: 0, nz: nz, t: t };
          }

          tMaxZ += 1 / Math.abs(dz);
        }
      }

      return null;
    }

    function getEyePosition() {
      return new THREE.Vector3(player.x, player.y + 1.5, player.z);
    }

    function placeBlock() {
      const eye = getEyePosition();
      const dir = forwardVector();
      const hit = raycast(eye, dir, 30);

      if (!hit) return;
      if (hit.nx === 0 && hit.ny === 0 && hit.nz === 0) return;

      const tx = hit.x + hit.nx;
      const ty = hit.y + hit.ny;
      const tz = hit.z + hit.nz;

      if (tx < 0 || tx >= W || ty < 0 || ty >= H || tz < 0 || tz >= D) return;
      if (getBlock(tx, ty, tz) !== 0) return;

      const minX = player.x - 0.3;
      const maxX = player.x + 0.3;
      const minY = player.y;
      const maxY = player.y + 1.8;
      const minZ = player.z - 0.3;
      const maxZ = player.z + 0.3;

      const overlapsPlayer =
        tx + 1 > minX &&
        tx < maxX &&
        ty + 1 > minY &&
        ty < maxY &&
        tz + 1 > minZ &&
        tz < maxZ;

      if (overlapsPlayer) return;

      setBlock(tx, ty, tz, currentType);
    }

    function removeBlock() {
      const eye = getEyePosition();
      const dir = forwardVector();
      const hit = raycast(eye, dir, 30);

      if (!hit) return;

      setBlock(hit.x, hit.y, hit.z, 0);
    }

    let dragging = false;
    let moved = false;
    let lastX = 0;
    let lastY = 0;

    renderer.domElement.addEventListener("mousedown", (e) => {
      if (e.button === 0) {
        dragging = true;
        moved = false;
        lastX = e.clientX;
        lastY = e.clientY;
      }
    });

    renderer.domElement.addEventListener("mouseup", (e) => {
      if (e.button === 0) {
        dragging = false;
      }
    });

    renderer.domElement.addEventListener("mousemove", (e) => {
      if (!dragging) return;

      const dx = e.clientX - lastX;
      const dy = e.clientY - lastY;

      lastX = e.clientX;
      lastY = e.clientY;

      if (Math.abs(dx) + Math.abs(dy) > 3) {
        moved = true;
      }

      player.yaw += dx * 0.005;
      player.pitch -= dy * 0.005;

      player.pitch = Math.max(-1.2, Math.min(1.2, player.pitch));
    });

    renderer.domElement.addEventListener("click", (e) => {
      if (e.button === 0 && !moved) {
        placeBlock();
      }
    });

    renderer.domElement.addEventListener("contextmenu", (e) => {
      e.preventDefault();
      removeBlock();
    });

    window.addEventListener("keydown", (e) => {
      if (e.key === " ") {
        e.preventDefault();
        keys[" "] = true;
      } else {
        keys[e.key.toLowerCase()] = true;
      }

      if (e.key.toLowerCase() === "e") placeBlock();
      if (e.key.toLowerCase() === "q") removeBlock();
    });

    window.addEventListener("keyup", (e) => {
      if (e.key === " ") {
        keys[" "] = false;
      } else {
        keys[e.key.toLowerCase()] = false;
      }
    });

    const typeButtons = document.querySelectorAll("button");
    typeButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        currentType = parseInt(btn.dataset.type, 10);

        typeButtons.forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
      });
    });

    window.addEventListener("resize", () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    });

    let lastTime = performance.now();

    function render() {
      const eye = getEyePosition();
      const f = forwardVector();

      camera.position.set(eye.x, eye.y, eye.z);
      camera.lookAt(eye.x + f.x, eye.y + f.y, eye.z + f.z);

      renderer.render(scene, camera);
    }

    function animate() {
      requestAnimationFrame(animate);

      const now = performance.now();
      const dt = Math.min(0.05, (now - lastTime) / 1000);
      lastTime = now;

      updatePhysics(dt);
      render();
    }

    animate();
  </script>
</body>
</html>
```

## 操作方法

- `W A S D`：移動
- 鼠の鼠の動: 視点
- 左クリック: ブロック放置
- 右クリック: ブロック壊す
- `Space`: ジャンプ
- `E`: 放置
- `Q`: 壊す
- UI のボタンで放置ブロック種類選択

## 特徴

- 3D voxel 世界
- 地形自動生成
- 木もちょっと生成
- 草・石・木・ガラス・タイル・砂
- 第一人称視点
- 重力・ジャンプ・碰撞
- InstancedMesh による比較的軽い渲染