はい。以下を「マイクラ風3D箱庭ゲーム」として、**1ファイルの HTML** にまとめます。  
そのまま `minecraft-style-voxel.html` などに保存してブラウザで開くと動きます。

- 3D 視点 / WASD 移動 / マウス視点
- ブロック破壊・設置
- 地形生成（草原・砂浜・海・木）
- 衝突判定
- 飛行モード
- ブロック選択（1〜7）
- R でワールド再生成

---

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>マイクラ風 3D 箱庭ゲーム</title>
  <style>
    html, body {
      margin: 0;
      padding: 0;
      width: 100%;
      height: 100%;
      overflow: hidden;
      background: #000;
      font-family: system-ui, -apple-system, sans-serif;
      color: #fff;
    }

    canvas {
      display: block;
    }

    #overlay {
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.65);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-direction: column;
      z-index: 20;
      user-select: none;
    }

    #overlay h1 {
      margin: 0 0 16px;
      font-size: 40px;
      text-shadow: 0 4px 12px rgba(0,0,0,0.8);
    }

    #overlay p {
      margin: 6px 0;
      font-size: 16px;
      opacity: 0.92;
    }

    #hud {
      position: fixed;
      left: 16px;
      top: 16px;
      z-index: 10;
      pointer-events: none;
      background: rgba(0,0,0,0.38);
      border: 1px solid rgba(255,255,255,0.14);
      border-radius: 12px;
      padding: 10px 14px;
      font-size: 14px;
      line-height: 1.5;
      backdrop-filter: blur(8px);
      white-space: pre;
    }

    #help {
      position: fixed;
      left: 16px;
      bottom: 16px;
      z-index: 10;
      pointer-events: none;
      background: rgba(0,0,0,0.35);
      border: 1px solid rgba(255,255,255,0.12);
      border-radius: 12px;
      padding: 10px 14px;
      font-size: 13px;
      line-height: 1.6;
      backdrop-filter: blur(8px);
      max-width: min(520px, calc(100vw - 32px));
    }

    #crosshair {
      position: fixed;
      left: 50%;
      top: 50%;
      width: 18px;
      height: 18px;
      transform: translate(-50%, -50%);
      z-index: 15;
      pointer-events: none;
      opacity: 0.9;
    }

    #crosshair::before,
    #crosshair::after {
      content: "";
      position: absolute;
      background: white;
      box-shadow: 0 0 6px rgba(0,0,0,0.8);
    }

    #crosshair::before {
      left: 8px;
      top: 0;
      width: 2px;
      height: 18px;
    }

    #crosshair::after {
      left: 0;
      top: 8px;
      width: 18px;
      height: 2px;
    }
  </style>
</head>
<body>
  <div id="overlay">
    <h1>Minecraft-style Voxel Sandbox</h1>
    <p>クリックして開始 / Click to start</p>
    <p>Esc でマウス解放</p>
    <p>マウス: 視点 / 左クリック: 破壊 / 右クリック: 設置</p>
  </div>

  <div id="hud">Loading...</div>
  <div id="help">
    WASD: 移動 / Space: ジャンプ・上昇 / Shift: 降下 / F: 飛行切替 / 1〜7: ブロック選択 / R: ワールド再生成 / H: ヘルプ切替
  </div>
  <div id="crosshair"></div>

  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js"></script>
  <script>
    /*
      Three.js を使ったマイクラ風ボクセル箱庭
      - 64x32x64 の小型ワールド
      - 地形生成 + 木 + 水
      - AABB 衝突
      - DDA によるボクセルレイキャスト
      - ブロック設置/破壊
    */

    const WORLD_X = 64;
    const WORLD_Y = 32;
    const WORLD_Z = 64;
    const SEA_LEVEL = 10;

    const AIR   = 0;
    const GRASS = 1;
    const DIRT  = 2;
    const STONE = 3;
    const WOOD  = 4;
    const LEAVES= 5;
    const SAND  = 6;
    const WATER = 7;

    const BLOCK_NAMES = [
      "Air",
      "Grass",
      "Dirt",
      "Stone",
      "Wood",
      "Leaves",
      "Sand",
      "Water"
    ];

    const SOLID = [
      false, // AIR
      true,  // GRASS
      true,  // DIRT
      true,  // STONE
      true,  // WOOD
      true,  // LEAVES
      true,  // SAND
      false  // WATER
    ];

    const world = new Uint8Array(WORLD_X * WORLD_Y * WORLD_Z);

    function idx(x, y, z) {
      return x + WORLD_X * (z + WORLD_Z * y);
    }

    function inWorld(x, y, z) {
      return x >= 0 && x < WORLD_X && y >= 0 && y < WORLD_Y && z >= 0 && z < WORLD_Z;
    }

    function getRaw(x, y, z) {
      if (!inWorld(x, y, z)) return AIR;
      return world[idx(x, y, z)];
    }

    function setRaw(x, y, z, type) {
      if (!inWorld(x, y, z)) return;
      world[idx(x, y, z)] = type;
    }

    function getBlockForCollision(x, y, z) {
      // 横・下は壁扱いにして外に出られないようにする
      if (x < 0 || x >= WORLD_X || z < 0 || z >= WORLD_Z || y < 0) return STONE;
      if (y >= WORLD_Y) return AIR;
      return world[idx(x, y, z)];
    }

    function getBlockForRay(x, y, z) {
      // レイは外へ抜ける。ただし地面の下は石扱いで当たりやすくする。
      if (x < 0 || x >= WORLD_X || z < 0 || z >= WORLD_Z) return AIR;
      if (y < 0) return STONE;
      if (y >= WORLD_Y) return AIR;
      return world[idx(x, y, z)];
    }

    function isSolid(type) {
      return !!SOLID[type];
    }

    // -------------------------------
    // 雑なノイズ生成
    // -------------------------------
    function hash2(x, z) {
      const n = Math.sin(x * 127.1 + z * 311.7) * 43758.5453123;
      return n - Math.floor(n);
    }

    function smooth(t) {
      return t * t * (3 - 2 * t);
    }

    function lerp(a, b, t) {
      return a + (b - a) * t;
    }

    function valueNoise2D(x, z) {
      const x0 = Math.floor(x);
      const z0 = Math.floor(z);
      const fx = x - x0;
      const fz = z - z0;
      const sx = smooth(fx);
      const sz = smooth(fz);

      const a = hash2(x0,     z0);
      const b = hash2(x0 + 1, z0);
      const c = hash2(x0,     z0 + 1);
      const d = hash2(x0 + 1, z0 + 1);

      return lerp(
        lerp(a, b, sx),
        lerp(c, d, sx),
        sz
      );
    }

    function fbm2D(x, z) {
      let sum = 0;
      let amp = 1;
      let freq = 1;
      let norm = 0;

      for (let i = 0; i < 4; i++) {
        sum += valueNoise2D(x * freq, z * freq) * amp;
        norm += amp;
        amp *= 0.5;
        freq *= 2.0;
      }

      return sum / norm;
    }

    // -------------------------------
    // テクスチャ生成
    // -------------------------------
    function makeCanvasTexture(draw) {
      const canvas = document.createElement("canvas");
      canvas.width = 16;
      canvas.height = 16;
      const ctx = canvas.getContext("2d");
      draw(ctx);

      const tex = new THREE.CanvasTexture(canvas);
      tex.magFilter = THREE.NearestFilter;
      tex.minFilter = THREE.NearestFilter;
      tex.wrapS = THREE.RepeatWrapping;
      tex.wrapT = THREE.RepeatWrapping;
      tex.generateMipmaps = false;
      return tex;
    }

    function makeBlockTexture(type) {
      return makeCanvasTexture((ctx) => {
        const size = 16;

        function randomFill(colors) {
          for (let y = 0; y < size; y++) {
            for (let x = 0; x < size; x++) {
              ctx.fillStyle = colors[Math.floor(Math.random() * colors.length)];
              ctx.fillRect(x, y, 1, 1);
            }
          }
        }

        if (type === GRASS) {
          randomFill([
            "#58a83b",
            "#4e9834",
            "#64b647",
            "#43862d",
            "#539f38"
          ]);
        } else if (type === DIRT) {
          randomFill([
            "#8b5a2b",
            "#7b4c24",
            "#986632",
            "#6e4423",
            "#835628"
          ]);
        } else if (type === STONE) {
          randomFill([
            "#8d8d8d",
            "#9b9b9b",
            "#7a7a7a",
            "#a7a7a7",
            "#6f6f6f"
          ]);
        } else if (type === WOOD) {
          for (let y = 0; y < size; y++) {
            for (let x = 0; x < size; x++) {
              let base;
              if (x % 5 === 0) base = "#57351e";
              else if (x % 5 === 2) base = "#6a4125";
              else base = "#75492b";

              if (Math.random() < 0.12) {
                ctx.fillStyle = "#4b2c18";
              } else if (Math.random() < 0.18) {
                ctx.fillStyle = "#845434";
              } else {
                ctx.fillStyle = base;
              }
              ctx.fillRect(x, y, 1, 1);
            }
          }
        } else if (type === LEAVES) {
          randomFill([
            "#2d7d32",
            "#246a2a",
            "#358d3c",
            "#1d5622",
            "#2e8235"
          ]);
        } else if (type === SAND) {
          randomFill([
            "#d9c98a",
            "#cdbb7c",
            "#e3d49c",
            "#c2ae6c",
            "#d1c083"
          ]);
        } else if (type === WATER) {
          for (let y = 0; y < size; y++) {
            for (let x = 0; x < size; x++) {
              let c;
              if ((x + y) % 7 === 0) c = "#4f97ea";
              else if ((x * 2 + y) % 11 === 0) c = "#2a5fb0";
              else c = "#3878d4";

              if (Math.random() < 0.08) c = "#62a7f2";
              ctx.fillStyle = c;
              ctx.fillRect(x, y, 1, 1);
            }
          }
        } else {
          ctx.fillStyle = "#f0f";
          ctx.fillRect(0, 0, size, size);
        }
      });
    }

    const materials = new Array(8);

    for (let t = 0; t < 8; t++) {
      const map = makeBlockTexture(t);

      if (t === WATER) {
        materials[t] = new THREE.MeshLambertMaterial({
          map,
          transparent: true,
          opacity: 0.68,
          depthWrite: true
        });
      } else {
        materials[t] = new THREE.MeshLambertMaterial({ map });
      }
    }

    // -------------------------------
    // シーン
    // -------------------------------
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x87ceeb);
    scene.fog = new THREE.Fog(0x87ceeb, 28, 90);

    const camera = new THREE.PerspectiveCamera(
      75,
      window.innerWidth / window.innerHeight,
      0.05,
      400
    );

    const renderer = new THREE.WebGLRenderer({ antialias: false });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    document.body.appendChild(renderer.domElement);

    const hemi = new THREE.HemisphereLight(0xffffff, 0x556b2f, 0.75);
    scene.add(hemi);

    const sun = new THREE.DirectionalLight(0xfff3c4, 0.95);
    sun.position.set(30, 60, 20);
    scene.add(sun);

    // -------------------------------
    // ボクセル表示（InstancedMesh）
    // -------------------------------
    const cubeGeometry = new THREE.BoxGeometry(1, 1, 1);
    const visualMeshes = new Map();
    const meshCaps = new Map();

    function ensureMesh(type, needed) {
      let mesh = visualMeshes.get(type);
      let cap = meshCaps.get(type) || 0;

      if (!mesh || cap < needed) {
        if (mesh) scene.remove(mesh);

        cap = Math.max(needed, cap ? cap * 2 : 4096);

        mesh = new THREE.InstancedMesh(cubeGeometry, materials[type], cap);
        mesh.frustumCulled = false;
        mesh.userData = { type };
        mesh.castShadow = false;
        mesh.receiveShadow = false;

        if (type === WATER) {
          mesh.renderOrder = 1;
        }

        scene.add(mesh);
        visualMeshes.set(type, mesh);
        meshCaps.set(type, cap);
      }

      return mesh;
    }

    function isExposedForRender(x, y, z, type) {
      // 外側が空気・水なら見える
      if (x < 0 || x >= WORLD_X || z < 0 || z >= WORLD_Z) return true;

      const neighbors = [
        [1, 0, 0],
        [-1, 0, 0],
        [0, 1, 0],
        [0, -1, 0],
        [0, 0, 1],
        [0, 0, -1]
      ];

      for (const [dx, dy, dz] of neighbors) {
        const nx = x + dx;
        const ny = y + dy;
        const nz = z + dz;

        if (nx < 0 || nx >= WORLD_X || nz < 0 || nz >= WORLD_Z) return true;
        if (ny < 0 || ny >= WORLD_Y) return true;

        const n = getRaw(nx, ny, nz);
        if (n === AIR || n === WATER) return true;
      }

      return false;
    }

    function rebuildWorld() {
      const positions = [];
      for (let i = 0; i < 8; i++) positions.push([]);

      for (let y = 0; y < WORLD_Y; y++) {
        for (let z = 0; z < WORLD_Z; z++) {
          for (let x = 0; x < WORLD_X; x++) {
            const t = getRaw(x, y, z);
            if (t === AIR) continue;

            if (t === WATER) {
              // 水面のブロックだけ表示
              if (getRaw(x, y + 1, z) === AIR) {
                positions[t].push([x, y, z]);
              }
            } else {
              if (isExposedForRender(x, y, z, t)) {
                positions[t].push([x, y, z]);
              }
            }
          }
        }
      }

      const mat4 = new THREE.Matrix4();

      for (let type = 1; type < 8; type++) {
        const arr = positions[type];
        const mesh = ensureMesh(type, arr.length);

        for (let i = 0; i < arr.length; i++) {
          const [x, y, z] = arr[i];
          mat4.makeTranslation(x + 0.5, y + 0.5, z + 0.5);
          mesh.setMatrixAt(i, mat4);
        }

        mesh.count = arr.length;
        mesh.instanceMatrix.needsUpdate = true;
      }
    }

    // -------------------------------
    // ワールド生成
    // -------------------------------
    function generateWorld() {
      world.fill(AIR);

      // 地形
      for (let x = 0; x < WORLD_X; x++) {
        for (let z = 0; z < WORLD_Z; z++) {
          let n = fbm2D(x / 26, z / 26);
          let h = Math.floor(5 + n * 17);

          // 山っぽいところを出す
          if (n > 0.74) {
            h += Math.floor((n - 0.74) * 55);
          }

          h = Math.max(1, Math.min(WORLD_Y - 10, h));

          for (let y = 0; y <= h; y++) {
            let b = STONE;

            if (y === h) {
              if (h <= SEA_LEVEL + 1) b = SAND;
              else b = GRASS;
            } else if (y >= h - 4) {
              b = DIRT;
            }

            setRaw(x, y, z, b);
          }

          // 水
          for (let y = h + 1; y <= SEA_LEVEL; y++) {
            setRaw(x, y, z, WATER);
          }
        }
      }

      // 木
      for (let x = 3; x < WORLD_X - 3; x++) {
        for (let z = 3; z < WORLD_Z - 3; z++) {
          let groundY = -1;
          for (let y = WORLD_Y - 1; y >= 0; y--) {
            const b = getRaw(x, y, z);
            if (b === GRASS) {
              groundY = y;
              break;
            }
          }

          if (groundY <= SEA_LEVEL + 1) continue;

          const r = hash2(x * 13.37 + 1.2, z * 17.13 + 5.7);
          if (r > 0.982) {
            const trunkH = 4 + Math.floor(hash2(x * 7.7, z * 9.1) * 3);
            const topY = groundY + trunkH;

            if (topY + 3 >= WORLD_Y) continue;

            for (let ty = 1; ty <= trunkH; ty++) {
              setRaw(x, groundY + ty, z, WOOD);
            }

            for (let dx = -2; dx <= 2; dx++) {
              for (let dz = -2; dz <= 2; dz++) {
                for (let dy = -2; dy <= 1; dy++) {
                  const lx = x + dx;
                  const lz = z + dz;
                  const ly = topY + dy;

                  if (!inWorld(lx, ly, lz)) continue;

                  if (Math.abs(dx) === 2 && Math.abs(dz) === 2) continue;
                  if (dx === 0 && dz === 0 && dy < 1) continue;

                  if (getRaw(lx, ly, lz) === AIR) {
                    setRaw(lx, ly, lz, LEAVES);
                  }
                }
              }
            }
          }
        }
      }

      rebuildWorld();
    }

    // -------------------------------
    // プレイヤー
    // -------------------------------
    const PLAYER_RADIUS = 0.3;
    const PLAYER_HEIGHT = 1.8;
    const EYE_HEIGHT = 1.62;

    const player = {
      pos: new THREE.Vector3(),
      vel: new THREE.Vector3(),
      yaw: 0,
      pitch: 0,
      onGround: false,
      fly: false
    };

    const keys = {};

    function collides(px = player.pos.x, py = player.pos.y, pz = player.pos.z) {
      const r = PLAYER_RADIUS;
      const h = PLAYER_HEIGHT - 0.001;

      const minX = Math.floor(px - r);
      const maxX = Math.floor(px + r);
      const minY = Math.floor(py);
      const maxY = Math.floor(py + h);
      const minZ = Math.floor(pz - r);
      const maxZ = Math.floor(pz + r);

      for (let y = minY; y <= maxY; y++) {
        for (let z = minZ; z <= maxZ; z++) {
          for (let x = minX; x <= maxX; x++) {
            const b = getBlockForCollision(x, y, z);
            if (isSolid(b)) return true;
          }
        }
      }

      return false;
    }

    function blockIntersectsPlayer(x, y, z, blockType) {
      if (!isSolid(blockType)) return false;

      const minX = player.pos.x - PLAYER_RADIUS;
      const maxX = player.pos.x + PLAYER_RADIUS;
      const minY = player.pos.y;
      const maxY = player.pos.y + PLAYER_HEIGHT;
      const minZ = player.pos.z - PLAYER_RADIUS;
      const maxZ = player.pos.z + PLAYER_RADIUS;

      return (
        x + 1 > minX &&
        x < maxX &&
        y + 1 > minY &&
        y < maxY &&
        z + 1 > minZ &&
        z < maxZ
      );
    }

    function spawnPlayer() {
      const cx = Math.floor(WORLD_X / 2);
      const cz = Math.floor(WORLD_Z / 2);

      let y = WORLD_Y - 1;
      for (; y >= 0; y--) {
        const b = getRaw(cx, y, cz);
        if (isSolid(b)) break;
      }

      if (y < 0) y = 0;

      player.pos.set(cx + 0.5, y + 1.2, cz + 0.5);
      player.vel.set(0, 0, 0);
      player.yaw = Math.PI * 0.25;
      player.pitch = -0.12;
      player.fly = false;

      let guard = 0;
      while (collides() && guard < 100) {
        player.pos.y += 0.5;
        guard++;
      }
    }

    // -------------------------------
    // ブロックレイキャスト
    // -------------------------------
    function raycastBlock(origin, dir, maxDist = 6) {
      let x = Math.floor(origin.x);
      let y = Math.floor(origin.y);
      let z = Math.floor(origin.z);

      const stepX = dir.x >= 0 ? 1 : -1;
      const stepY = dir.y >= 0 ? 1 : -1;
      const stepZ = dir.z >= 0 ? 1 : -1;

      const tDeltaX = dir.x !== 0 ? Math.abs(1 / dir.x) : Infinity;
      const tDeltaY = dir.y !== 0 ? Math.abs(1 / dir.y) : Infinity;
      const tDeltaZ = dir.z !== 0 ? Math.abs(1 / dir.z) : Infinity;

      let tMaxX = dir.x !== 0
        ? (dir.x > 0 ? (x + 1 - origin.x) * tDeltaX : (origin.x - x) * tDeltaX)
        : Infinity;

      let tMaxY = dir.y !== 0
        ? (dir.y > 0 ? (y + 1 - origin.y) * tDeltaY : (origin.y - y) * tDeltaY)
        : Infinity;

      let tMaxZ = dir.z !== 0
        ? (dir.z > 0 ? (z + 1 - origin.z) * tDeltaZ : (origin.z - z) * tDeltaZ)
        : Infinity;

      let nx = 0, ny = 0, nz = 0;

      for (let i = 0; i < 10000; i++) {
        let t;

        if (tMaxX < tMaxY && tMaxX < tMaxZ) {
          if (tMaxX > maxDist) break;
          x += stepX;
          t = tMaxX;
          tMaxX += tDeltaX;
          nx = -stepX;
          ny = 0;
          nz = 0;
        } else if (tMaxY < tMaxZ) {
          if (tMaxY > maxDist) break;
          y += stepY;
          t = tMaxY;
          tMaxY += tDeltaY;
          nx = 0;
          ny = -stepY;
          nz = 0;
        } else {
          if (tMaxZ > maxDist) break;
          z += stepZ;
          t = tMaxZ;
          tMaxZ += tDeltaZ;
          nx = 0;
          ny = 0;
          nz = -stepZ;
        }

        const b = getBlockForRay(x, y, z);

        // 水は素通り。空気は素通り。石・草・土・木・葉・砂に当たる。
        if (b !== AIR && b !== WATER) {
          return {
            x,
            y,
            z,
            nx,
            ny,
            nz,
            block: b,
            distance: t
          };
        }
      }

      return null;
    }

    // -------------------------------
    // 操作
    // -------------------------------
    const overlay = document.getElementById("overlay");
    const hud = document.getElementById("hud");
    const help = document.getElementById("help");

    let selectedBlock = GRASS;
    let helpVisible = true;

    function setOverlayVisible(visible) {
      overlay.style.display = visible ? "flex" : "none";
    }

    function toggleHelp() {
      helpVisible = !helpVisible;
      help.style.display = helpVisible ? "block" : "none";
    }

    renderer.domElement.addEventListener("click", () => {
      renderer.domElement.requestPointerLock();
    });

    document.addEventListener("pointerlockchange", () => {
      setOverlayVisible(document.pointerLockElement !== renderer.domElement);
    });

    document.addEventListener("mousemove", (e) => {
      if (document.pointerLockElement !== renderer.domElement) return;

      player.yaw -= e.movementX * 0.0022;
      player.pitch -= e.movementY * 0.0022;

      const limit = Math.PI / 2 - 0.01;
      player.pitch = Math.max(-limit, Math.min(limit, player.pitch));
    });

    document.addEventListener("contextmenu", (e) => {
      e.preventDefault();
    });

    document.addEventListener("mousedown", (e) => {
      if (document.pointerLockElement !== renderer.domElement) return;

      const dir = new THREE.Vector3();
      camera.getWorldDirection(dir);
      const target = raycastBlock(camera.position, dir, 6);

      if (!target) return;

      if (e.button === 0) {
        // 破壊
        if (target.y <= 0) return; // 床は壊せない
        setRaw(target.x, target.y, target.z, AIR);
        rebuildWorld();
      } else if (e.button === 2) {
        // 設置
        const px = target.x + target.nx;
        const py = target.y + target.ny;
        const pz = target.z + target.nz;

        const current = getRaw(px, py, pz);

        if (current !== AIR && !(current === WATER && selectedBlock !== WATER)) return;
        if (blockIntersectsPlayer(px, py, pz, selectedBlock)) return;

        setRaw(px, py, pz, selectedBlock);
        rebuildWorld();
      }
    });

    document.addEventListener("keydown", (e) => {
      const key = e.key.toLowerCase();

      keys[key] = true;

      if (key === "f") {
        player.fly = !player.fly;
        player.vel.y = 0;
      }

      if (key === "r") {
        generateWorld();
        spawnPlayer();
      }

      if (key === "h") {
        toggleHelp();
      }

      if (key >= "1" && key <= "7") {
        selectedBlock = parseInt(key, 10);
      }
    });

    document.addEventListener("keyup", (e) => {
      keys[e.key.toLowerCase()] = false;
    });

    // -------------------------------
    // ハイライト表示
    // -------------------------------
    const highlightGeo = new THREE.BoxGeometry(1.01, 1.01, 1.01);
    const highlightMat = new THREE.MeshBasicMaterial({
      color: 0x000000,
      wireframe: true,
      transparent: true,
      opacity: 0.75
    });
    const highlight = new THREE.Mesh(highlightGeo, highlightMat);
    highlight.visible = false;
    scene.add(highlight);

    const ghostMat = new THREE.MeshBasicMaterial({
      color: 0xffffff,
      transparent: true,
      opacity: 0.22
    });
    const ghost = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), ghostMat);
    ghost.visible = false;
    scene.add(ghost);

    // -------------------------------
    // 更新
    // -------------------------------
    const clock = new THREE.Clock();

    function updatePlayer(dt) {
      const walkSpeed = 5.4;
      const flySpeed = 10.5;
      const gravity = 24;
      const jumpSpeed = 8.0;

      const forward =
        (keys["w"] ? 1 : 0) -
        (keys["s"] ? 1 : 0);

      const strafe =
        (keys["d"] ? 1 : 0) -
        (keys["a"] ? 1 : 0);

      const up =
        (keys[" "] ? 1 : 0) -
        (keys["shift"] ? 1 : 0);

      const sinY = Math.sin(player.yaw);
      const cosY = Math.cos(player.yaw);

      let wishX = (-sinY * forward + cosY * strafe);
      let wishZ = (-cosY * forward - sinY * strafe);

      const len = Math.hypot(wishX, wishZ) || 1;
      if (Math.hypot(forward, strafe) > 0) {
        wishX /= len;
        wishZ /= len;
      }

      if (player.fly) {
        player.vel.x = wishX * flySpeed;
        player.vel.z = wishZ * flySpeed;
        player.vel.y = up * flySpeed;
      } else {
        const speed = walkSpeed;

        // 着地判定
        player.onGround = collides(
          player.pos.x,
          player.pos.y - 0.01,
          player.pos.z
        );

        if (player.onGround && keys[" "]) {
          player.vel.y = jumpSpeed;
        }

        player.vel.x += (wishX * speed - player.vel.x) * Math.min(1, dt * 10);
        player.vel.z += (wishZ * speed - player.vel.z) * Math.min(1, dt * 10);

        player.vel.y -= gravity * dt;
        player.vel.y = Math.max(player.vel.y, -40);
      }

      const dx = player.vel.x * dt;
      const dy = player.vel.y * dt;
      const dz = player.vel.z * dt;

      // X
      player.pos.x += dx;
      if (collides()) {
        player.pos.x -= dx;
        player.vel.x = 0;
      }

      // Z
      player.pos.z += dz;
      if (collides()) {
        player.pos.z -= dz;
        player.vel.z = 0;
      }

      // Y
      const oldY = player.pos.y;
      player.pos.y += dy;

      if (collides()) {
        player.pos.y = oldY;

        if (dy < 0) {
          player.onGround = true;
        }

        player.vel.y = 0;
      } else {
        if (dy < -0.0001) {
          player.onGround = false;
        }
      }
    }

    function updateCamera() {
      camera.position.set(
        player.pos.x,
        player.pos.y + EYE_HEIGHT,
        player.pos.z
      );

      const euler = new THREE.Euler(
        player.pitch,
        player.yaw,
        0,
        "YXZ"
      );

      camera.quaternion.setFromEuler(euler);
    }

    function updateHighlight() {
      const dir = new THREE.Vector3();
      camera.getWorldDirection(dir);

      const target = raycastBlock(camera.position, dir, 6);

      if (!target) {
        highlight.visible = false;
        ghost.visible = false;
        return;
      }

      highlight.visible = true;
      highlight.position.set(
        target.x + 0.5,
        target.y + 0.5,
        target.z + 0.5
      );

      const px = target.x + target.nx;
      const py = target.y + target.ny;
      const pz = target.z + target.nz;

      const current = getRaw(px, py, pz);

      if (
        (current === AIR || current === WATER) &&
        !blockIntersectsPlayer(px, py, pz, selectedBlock)
      ) {
        ghost.visible = true;
        ghost.position.set(px + 0.5, py + 0.5, pz + 0.5);
      } else {
        ghost.visible = false;
      }
    }

    function updateHUD(fps) {
      const p = player.pos;

      hud.textContent =
        `FPS: ${fps.toFixed(1)}\n` +
        `選択: ${BLOCK_NAMES[selectedBlock]}\n` +
        `位置: ${p.x.toFixed(2)}, ${p.y.toFixed(2)}, ${p.z.toFixed(2)}\n` +
        `飛行: ${player.fly ? "ON" : "OFF"}\n` +
        `着地: ${player.onGround ? "YES" : "NO"}`;
    }

    // -------------------------------
    // メインループ
    // -------------------------------
    let frameCount = 0;
    let fpsTime = 0;
    let fps = 0;

    generateWorld();
    spawnPlayer();
    setOverlayVisible(true);

    function animate() {
      requestAnimationFrame(animate);

      const dt = Math.min(clock.getDelta(), 0.05);

      if (document.pointerLockElement === renderer.domElement) {
        updatePlayer(dt);
      } else {
        // ロック解除時は重力だけ止めて静止（見た目の安定）
        player.vel.x = 0;
        player.vel.z = 0;
        if (!player.fly) player.vel.y = 0;
      }

      updateCamera();
      updateHighlight();

      frameCount++;
      fpsTime += dt;
      if (fpsTime >= 0.5) {
        fps = frameCount / fpsTime;
        frameCount = 0;
        fpsTime = 0;
      }

      updateHUD(fps);

      renderer.render(scene, camera);
    }

    animate();

    window.addEventListener("resize", () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    });
  </script>
</body>
</html>
```

---

### 遊び方

1. 上のコードを全文コピー  
2. `minecraft-style-voxel.html` などの名前で保存  
3. そのままブラウザで開く  
4. 画面をクリックしてマウスロック

### 操作

- `W A S D`: 移動  
- `Space`: ジャンプ / 飛行時は上昇  
- `Shift`: 飛行時に下降  
- `マウス`: 視点操作  
- `左クリック`: ブロックを壊す  
- `右クリック`: ブロックを設置する  
- `1〜7`: 使うブロック選択  
  - 1: 草  
  - 2: 土  
  - 3: 石  
  - 4: 木  
  - 5: 葉  
  - 6: 砂  
  - 7: 水  
- `F`: 飛行モード切替  
- `R`: ワールド再生成  
- `H`: ヘルプ表示切替  

---

### 補足

これは「ブラウザで動くマイクラ風プロトタイプ」です。  
もっと本格化させるなら、次に足すと良いのは以下です。

- 無限ワールド化（チャンク分割）
- グリーディメッシュ化
- 影 / アンビエントオクルージョン
- インベントリ UI
- mob 追加
- セーブ / ロード

もし次を作るなら、私はこのコードから  
「チャンク分割」  
「インベントリ」  
「敵 mob 追加」  
あたりまで拡張できます。