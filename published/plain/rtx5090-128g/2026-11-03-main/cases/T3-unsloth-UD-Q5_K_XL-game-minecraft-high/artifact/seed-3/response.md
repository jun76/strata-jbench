以下、単一 HTML で動く「マイクラ風 3D 箱庭ゲーム」です。  
`index.html` として保存し、ブラウザで開けばすぐ遊べます。

- Three.js を CDN から読み込みます。
- マウスクリックでマウスロック（ゲーム開始）
- WASD / Space / Shift / F / 数字キー / 左クリック破壊 / 右クリック設置
- 地形自動生成、木、水、昼夜、ホットバー付き

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>マイクラ風3D箱庭</title>
  <style>
    html, body {
      margin: 0;
      padding: 0;
      overflow: hidden;
      background: #000;
      font-family: "Yu Gothic UI", "Hiragino Kaku Gothic ProN", "Meiryo", sans-serif;
      color: #fff;
      user-select: none;
      -webkit-user-select: none;
    }

    #ui {
      position: fixed;
      inset: 0;
      pointer-events: none;
      z-index: 10;
    }

    #crosshair {
      position: absolute;
      left: 50%;
      top: 50%;
      width: 18px;
      height: 18px;
      transform: translate(-50%, -50%);
      opacity: 0.85;
    }

    #crosshair::before,
    #crosshair::after {
      content: "";
      position: absolute;
      background: #fff;
      mix-blend-mode: difference;
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

    #info {
      position: absolute;
      left: 14px;
      bottom: 86px;
      background: rgba(0, 0, 0, 0.55);
      border: 2px solid rgba(255, 255, 255, 0.18);
      padding: 12px 14px;
      border-radius: 8px;
      font-size: 13px;
      line-height: 1.55;
      max-width: 360px;
      white-space: pre-line;
      text-shadow: 0 1px 2px #000;
    }

    #message {
      position: absolute;
      left: 50%;
      top: 50%;
      transform: translate(-50%, -50%);
      background: rgba(0, 0, 0, 0.72);
      border: 3px solid #fff;
      padding: 22px 34px;
      font-size: 24px;
      font-weight: 700;
      letter-spacing: 1px;
      box-shadow: 0 0 30px rgba(0,0,0,0.7);
      text-align: center;
    }

    #hotbar {
      position: absolute;
      left: 50%;
      bottom: 14px;
      transform: translateX(-50%);
      display: flex;
      gap: 6px;
      padding: 6px;
      background: rgba(0, 0, 0, 0.45);
      border: 2px solid rgba(255, 255, 255, 0.2);
      border-radius: 8px;
    }

    .slot {
      width: 52px;
      height: 52px;
      border: 2px solid #555;
      background: #111;
      display: flex;
      align-items: flex-end;
      justify-content: center;
      position: relative;
      box-shadow: inset 0 0 12px rgba(0,0,0,0.7);
    }

    .slot.active {
      border-color: #fff;
      box-shadow: 0 0 0 2px #fff inset, 0 0 18px rgba(255,255,255,0.45);
    }

    .slot .num {
      position: absolute;
      top: 2px;
      left: 4px;
      font-size: 12px;
      color: #fff;
      text-shadow: 1px 1px 2px #000;
    }

    .slot .name {
      font-size: 11px;
      color: #fff;
      text-shadow: 1px 1px 2px #000;
      margin-bottom: 2px;
      font-weight: 700;
    }

    .slot .preview {
      position: absolute;
      inset: 12px 12px 24px 12px;
      border: 1px solid rgba(255,255,255,0.35);
      image-rendering: pixelated;
    }

    #fps {
      position: absolute;
      right: 14px;
      top: 14px;
      background: rgba(0,0,0,0.5);
      padding: 8px 10px;
      border-radius: 6px;
      font-size: 13px;
      text-shadow: 1px 1px 2px #000;
    }
  </style>
</head>
<body>
  <div id="ui">
    <div id="crosshair"></div>

    <div id="info">
左クリック: 破壊
右クリック: 設置
WASD: 移動
Space: ジャンプ / 飛行時に上
Shift: 走る / 飛行時に下
F: 飛行切替
R: リスポーン
1〜8: ブロック選択
Esc: カーソル解放

座標: X,Y,Z
      </div>

    <div id="hotbar"></div>

    <div id="fps">FPS: --</div>

    <div id="message">
      画面をクリックして開始
    </div>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js"></script>
  <script>
    /*
      Minecraft-like 3D sandbox
      Single file prototype
    */

    // ------------------------------------------------------------
    // Constants
    // ------------------------------------------------------------
    const WORLD_W = 64;
    const WORLD_D = 64;
    const WORLD_H = 36;
    const SEA_LEVEL = 12;

    const AIR = 0;
    const GRASS = 1;
    const DIRT = 2;
    const STONE = 3;
    const SAND = 4;
    const WOOD = 5;
    const PLANK = 6;
    const LEAVES = 7;
    const COBBLE = 8;
    const WATER = 9;

    const TILE_COLS = 4;
    const TILE_ROWS = 4;
    const TILE_SIZE = 16;

    const GRAVITY = 24.0;
    const JUMP_POWER = 8.2;
    const WALK_SPEED = 4.3;
    const SPRINT_SPEED = 7.2;
    const FLY_SPEED = 9.0;

    const PLAYER_RADIUS = 0.3;
    const PLAYER_HEIGHT = 1.8;
    const PLAYER_EYE = 1.62;
    const REACH = 6.0;

    const SEED = 123456789;

    const BLOCKS = [
      null,
      { name: "草",   top: 0,  bottom: 1,  side: 2,  color: "#5d9c3a" },
      { name: "土",   top: 1,  bottom: 1,  side: 1,  color: "#7a5230" },
      { name: "石",   top: 3,  bottom: 3,  side: 3,  color: "#808080" },
      { name: "砂",   top: 7,  bottom: 7,  side: 7,  color: "#e0cf8f" },
      { name: "木",   top: 5,  bottom: 5,  side: 4,  color: "#6b4b2b" },
      { name: "板",   top: 8,  bottom: 8,  side: 8,  color: "#9c6b3c" },
      { name: "葉",   top: 6,  bottom: 6,  side: 6,  color: "#3b6e2e" },
      { name: "石レンガ", top: 9, bottom: 9, side: 9, color: "#737373" },
      { name: "水",   top: 10, bottom: 10, side: 10, color: "#3c6ec6", liquid: true },
    ];

    const HOTBAR = [
      GRASS,
      DIRT,
      STONE,
      SAND,
      WOOD,
      PLANK,
      LEAVES,
      COBBLE,
    ];

    // ------------------------------------------------------------
    // DOM
    // ------------------------------------------------------------
    const messageEl = document.getElementById("message");
    const hotbarEl = document.getElementById("hotbar");
    const fpsEl = document.getElementById("fps");
    const infoEl = document.getElementById("info");

    let selected = 0;

    function buildHotbar() {
      hotbarEl.innerHTML = "";
      HOTBAR.forEach((blockType, i) => {
        const slot = document.createElement("div");
        slot.className = "slot" + (i === selected ? " active" : "");

        const num = document.createElement("div");
        num.className = "num";
        num.textContent = String(i + 1);

        const preview = document.createElement("div");
        preview.className = "preview";
        preview.style.background = BLOCKS[blockType].color;

        const name = document.createElement("div");
        name.className = "name";
        name.textContent = BLOCKS[blockType].name;

        slot.appendChild(num);
        slot.appendChild(preview);
        slot.appendChild(name);
        hotbarEl.appendChild(slot);
      });
    }

    function updateHotbar() {
      [...hotbarEl.children].forEach((slot, i) => {
        slot.classList.toggle("active", i === selected);
      });
    }

    buildHotbar();

    // ------------------------------------------------------------
    // Renderer / Scene / Camera
    // ------------------------------------------------------------
    const renderer = new THREE.WebGLRenderer({ antialias: false, powerPreference: "high-performance" });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(window.innerWidth, window.innerHeight);
    if (THREE.SRGBColorSpace) {
      renderer.outputColorSpace = THREE.SRGBColorSpace;
    }
    document.body.appendChild(renderer.domElement);

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x87ceeb);
    scene.fog = new THREE.Fog(0x87ceeb, 34, 110);

    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.08, 400);
    camera.rotation.order = "YXZ";

    // Lights
    const ambient = new THREE.AmbientLight(0xffffff, 0.55);
    scene.add(ambient);

    const hemi = new THREE.HemisphereLight(0xffffff, 0x556644, 0.45);
    scene.add(hemi);

    const sun = new THREE.DirectionalLight(0xffffff, 1.0);
    sun.position.set(50, 80, 30);
    scene.add(sun);

    const skyNight = new THREE.Color(0x081028);
    const skyDay = new THREE.Color(0x87ceeb);
    const fogNight = new THREE.Color(0x101828);
    const fogDay = new THREE.Color(0xbfd9ee);

    // ------------------------------------------------------------
    // World storage
    // ------------------------------------------------------------
    const world = new Uint8Array(WORLD_W * WORLD_D * WORLD_H);

    function idx(x, y, z) {
      return x + WORLD_W * (z + WORLD_D * y);
    }

    function inWorld(x, y, z) {
      return x >= 0 && x < WORLD_W && y >= 0 && y < WORLD_H && z >= 0 && z < WORLD_D;
    }

    function getBlock(x, y, z) {
      if (!inWorld(x, y, z)) return AIR;
      return world[idx(x, y, z)];
    }

    function setBlockRaw(x, y, z, v) {
      if (!inWorld(x, y, z)) return;
      world[idx(x, y, z)] = v;
    }

    function isSolidBlock(type) {
      return type !== AIR && type !== WATER;
    }

    // ------------------------------------------------------------
    // Procedural textures
    // ------------------------------------------------------------
    function makeTextureAtlas() {
      const canvas = document.createElement("canvas");
      canvas.width = TILE_COLS * TILE_SIZE;
      canvas.height = TILE_ROWS * TILE_SIZE;
      const ctx = canvas.getContext("2d");

      ctx.clearRect(0, 0, canvas.width, canvas.height);

      function clamp255(v) {
        return Math.max(0, Math.min(255, Math.round(v)));
      }

      function rgb(r, g, b) {
        return `rgb(${clamp255(r)},${clamp255(g)},${clamp255(b)})`;
      }

      function tilePos(i) {
        return {
          x: (i % TILE_COLS) * TILE_SIZE,
          y: Math.floor(i / TILE_COLS) * TILE_SIZE,
        };
      }

      function fillTile(i, color) {
        const p = tilePos(i);
        ctx.fillStyle = color;
        ctx.fillRect(p.x, p.y, TILE_SIZE, TILE_SIZE);
      }

      function noiseTile(i, base, amount, alpha = 1) {
        const p = tilePos(i);
        for (let y = 0; y < TILE_SIZE; y++) {
          for (let x = 0; x < TILE_SIZE; x++) {
            const r = base[0] + (Math.random() * 2 - 1) * amount;
            const g = base[1] + (Math.random() * 2 - 1) * amount;
            const b = base[2] + (Math.random() * 2 - 1) * amount;
            ctx.fillStyle = rgb(r, g, b);
            ctx.fillRect(p.x + x, p.y + y, 1, 1);
          }
        }
      }

      // 0 grass top
      noiseTile(0, [92, 154, 64], 24);

      // 1 dirt
      noiseTile(1, [122, 82, 52], 24);

      // 2 grass side
      fillTile(2, rgb(122, 82, 52));
      noiseTile(1, [122, 82, 52], 24); // redraw dirt for tile1
      const grassSide = tilePos(2);
      for (let y = 0; y < 5; y++) {
        for (let x = 0; x < TILE_SIZE; x++) {
          const r = 84 + Math.random() * 36;
          const g = 142 + Math.random() * 38;
          const b = 58 + Math.random() * 24;
          ctx.fillStyle = rgb(r, g, b);
          ctx.fillRect(grassSide.x + x, grassSide.y + y, 1, 1);
        }
      }
      // ragged edge
      for (let x = 0; x < TILE_SIZE; x++) {
        if (Math.random() > 0.45) {
          ctx.fillStyle = rgb(84 + Math.random() * 36, 142 + Math.random() * 38, 58 + Math.random() * 24);
          ctx.fillRect(grassSide.x + x, grassSide.y + 5, 1, 1);
        }
        if (Math.random() > 0.75) {
          ctx.fillStyle = rgb(84 + Math.random() * 36, 142 + Math.random() * 38, 58 + Math.random() * 24);
          ctx.fillRect(grassSide.x + x, grassSide.y + 6, 1, 1);
        }
      }

      // 3 stone
      noiseTile(3, [130, 130, 132], 22);
      const stone = tilePos(3);
      for (let i = 0; i < 16; i++) {
        const x = Math.floor(Math.random() * TILE_SIZE);
        const y = Math.floor(Math.random() * TILE_SIZE);
        const s = Math.random() > 0.5 ? 1 : 2;
        ctx.fillStyle = Math.random() > 0.5 ? rgb(95, 95, 98) : rgb(160, 160, 164);
        ctx.fillRect(stone.x + x, stone.y + y, s, s);
      }

      // 4 wood side
      noiseTile(4, [109, 75, 44], 14);
      const woodSide = tilePos(4);
      for (let x = 0; x < TILE_SIZE; x++) {
        if (x === 0 || x === 4 || x === 8 || x === 12) {
          ctx.fillStyle = rgb(78, 52, 30);
          ctx.fillRect(woodSide.x + x, woodSide.y, 1, TILE_SIZE);
        }
        if (x === 1 || x === 9) {
          ctx.fillStyle = rgb(135, 95, 56);
          ctx.fillRect(woodSide.x + x, woodSide.y, 1, TILE_SIZE);
        }
      }

      // 5 wood top
      noiseTile(5, [166, 126, 80], 14);
      const woodTop = tilePos(5);
      const cx = woodTop.x + 8;
      const cy = woodTop.y + 8;
      for (let y = 0; y < TILE_SIZE; y++) {
        for (let x = 0; x < TILE_SIZE; x++) {
          const d = Math.floor(Math.hypot(x + 0.5 - 7.5, y + 0.5 - 7.5));
          if (d === 2 || d === 4 || d === 6 || d === 7) {
            ctx.fillStyle = rgb(124, 88, 52);
            ctx.fillRect(woodTop.x + x, woodTop.y + y, 1, 1);
          }
        }
      }

      // 6 leaves
      noiseTile(6, [54, 112, 43], 34);
      const leaf = tilePos(6);
      for (let i = 0; i < 36; i++) {
        const x = Math.floor(Math.random() * TILE_SIZE);
        const y = Math.floor(Math.random() * TILE_SIZE);
        ctx.fillStyle = Math.random() > 0.48 ? rgb(92, 164, 70) : rgb(32, 78, 26);
        ctx.fillRect(leaf.x + x, leaf.y + y, 1, 1);
      }

      // 7 sand
      noiseTile(7, [226, 208, 142], 18);

      // 8 plank
      noiseTile(8, [156, 108, 62], 12);
      const plank = tilePos(8);
      ctx.fillStyle = rgb(106, 70, 39);
      for (let y = 3; y < TILE_SIZE; y += 4) {
        ctx.fillRect(plank.x, plank.y + y, TILE_SIZE, 1);
      }
      for (let i = 0; i < 5; i++) {
        const x = Math.floor(Math.random() * TILE_SIZE);
        ctx.fillRect(plank.x + x, plank.y, 1, TILE_SIZE);
      }

      // 9 cobble
      noiseTile(9, [126, 126, 128], 28);
      const cobble = tilePos(9);
      for (let i = 0; i < 16; i++) {
        const x = Math.floor(Math.random() * TILE_SIZE);
        const y = Math.floor(Math.random() * TILE_SIZE);
        const w = 2 + Math.floor(Math.random() * 3);
        const h = 2 + Math.floor(Math.random() * 3);
        ctx.fillStyle = Math.random() > 0.5 ? rgb(94, 94, 96) : rgb(168, 168, 172);
        ctx.fillRect(cobble.x + x, cobble.y + y, w, h);
      }

      // 10 water
      noiseTile(10, [64, 122, 212], 22);
      const water = tilePos(10);
      ctx.fillStyle = "rgba(255,255,255,0.22)";
      for (let y = 0; y < TILE_SIZE; y++) {
        for (let x = 0; x < TILE_SIZE; x++) {
          if ((x + y) % 7 === 0) {
            ctx.fillRect(water.x + x, water.y + y, 1, 1);
          }
        }
      }

      // Fill remaining unused tiles with dark gray to avoid sampling noise.
      for (let i = 11; i < TILE_COLS * TILE_ROWS; i++) {
        fillTile(i, "#202020");
      }

      const tex = new THREE.CanvasTexture(canvas);
      tex.magFilter = THREE.NearestFilter;
      tex.minFilter = THREE.NearestMipmapNearestFilter;
      tex.generateMipmaps = true;
      tex.anisotropy = renderer.capabilities.getMaxAnisotropy ? Math.min(4, renderer.capabilities.getMaxAnisotropy()) : 1;
      return tex;
    }

    const textureAtlas = makeTextureAtlas();

    const solidMaterial = new THREE.MeshLambertMaterial({
      map: textureAtlas,
      side: THREE.FrontSide,
    });

    const waterMaterial = new THREE.MeshLambertMaterial({
      map: textureAtlas,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.74,
      depthWrite: false,
    });

    // ------------------------------------------------------------
    // Meshes
    // ------------------------------------------------------------
    const solidGeometry = new THREE.BufferGeometry();
    const waterGeometry = new THREE.BufferGeometry();

    const solidMesh = new THREE.Mesh(solidGeometry, solidMaterial);
    solidMesh.frustumCulled = false;
    scene.add(solidMesh);

    const waterMesh = new THREE.Mesh(waterGeometry, waterMaterial);
    waterMesh.frustumCulled = false;
    scene.add(waterMesh);

    // Highlight
    const highlightGeometry = new THREE.BoxGeometry(1.002, 1.002, 1.002);
    const highlightEdges = new THREE.EdgesGeometry(highlightGeometry);
    const highlight = new THREE.LineSegments(
      highlightEdges,
      new THREE.LineBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.72 })
    );
    highlight.visible = false;
    scene.add(highlight);

    // ------------------------------------------------------------
    // Faces
    // ------------------------------------------------------------
    // Face order: +x, -x, +y, -y, +z, -z
    const FACES = [
      {
        dir: [1, 0, 0],
        corners: [
          [1, 0, 0],
          [1, 1, 0],
          [1, 1, 1],
          [1, 0, 1],
        ],
      },
      {
        dir: [-1, 0, 0],
        corners: [
          [0, 0, 1],
          [0, 1, 1],
          [0, 1, 0],
          [0, 0, 0],
        ],
      },
      {
        dir: [0, 1, 0],
        corners: [
          [0, 1, 1],
          [1, 1, 1],
          [1, 1, 0],
          [0, 1, 0],
        ],
      },
      {
        dir: [0, -1, 0],
        corners: [
          [0, 0, 0],
          [1, 0, 0],
          [1, 0, 1],
          [0, 0, 1],
        ],
      },
      {
        dir: [0, 0, 1],
        corners: [
          [0, 0, 1],
          [1, 0, 1],
          [1, 1, 1],
          [0, 1, 1],
        ],
      },
      {
        dir: [0, 0, -1],
        corners: [
          [1, 0, 0],
          [0, 0, 0],
          [0, 1, 0],
          [1, 1, 0],
        ],
      },
    ];

    function tileUV(tileIndex) {
      const col = tileIndex % TILE_COLS;
      const row = Math.floor(tileIndex / TILE_COLS);
      return {
        u0: col / TILE_COLS,
        u1: (col + 1) / TILE_COLS,
        v0: row / TILE_ROWS,
        v1: (row + 1) / TILE_ROWS,
      };
    }

    function addFace(arr, faceIndex, x, y, z, tileIndex) {
      const face = FACES[faceIndex];
      const base = arr.positions.length / 3;

      for (let i = 0; i < 4; i++) {
        const c = face.corners[i];
        arr.positions.push(x + c[0], y + c[1], z + c[2]);
        arr.normals.push(face.dir[0], face.dir[1], face.dir[2]);
      }

      const uv = tileUV(tileIndex);
      // v0 is lower in this custom atlas mapping; assign cyclically.
      arr.uvs.push(
        uv.u0, uv.v0,
        uv.u1, uv.v0,
        uv.u1, uv.v1,
        uv.u0, uv.v1
      );

      arr.indices.push(
        base, base + 1, base + 2,
        base, base + 2, base + 3
      );
    }

    function getTileForFace(blockType, faceIndex) {
      const b = BLOCKS[blockType];
      if (!b) return 3;

      // faceIndex: 0 +x, 1 -x, 2 +y, 3 -y, 4 +z, 5 -z
      if (faceIndex === 2) return b.top;
      if (faceIndex === 3) return b.bottom;
      return b.side;
    }

    // ------------------------------------------------------------
    // Geometry rebuild
    // ------------------------------------------------------------
    let dirty = true;

    function rebuildGeometries() {
      const solid = { positions: [], normals: [], uvs: [], indices: [] };
      const water = { positions: [], normals: [], uvs: [], indices: [] };

      for (let y = 0; y < WORLD_H; y++) {
        for (let z = 0; z < WORLD_D; z++) {
          for (let x = 0; x < WORLD_W; x++) {
            const type = getBlock(x, y, z);
            if (type === AIR) continue;

            if (type === WATER) {
              // Water only render faces touching air.
              for (let f = 0; f < 6; f++) {
                const nx = x + FACES[f].dir[0];
                const ny = y + FACES[f].dir[1];
                const nz = z + FACES[f].dir[2];
                const n = getBlock(nx, ny, nz);
                if (n === AIR) {
                  addFace(water, f, x, y, z, BLOCKS[WATER].top);
                }
              }
            } else if (isSolidBlock(type)) {
              for (let f = 0; f < 6; f++) {
                const nx = x + FACES[f].dir[0];
                const ny = y + FACES[f].dir[1];
                const nz = z + FACES[f].dir[2];
                const n = getBlock(nx, ny, nz);

                // Render solid face if neighbor is air or water.
                if (!isSolidBlock(n)) {
                  addFace(solid, f, x, y, z, getTileForFace(type, f));
                }
              }
            }
          }
        }
      }

      solidGeometry.setIndex(solid.indices);
      solidGeometry.setAttribute("position", new THREE.Float32BufferAttribute(solid.positions, 3));
      solidGeometry.setAttribute("normal", new THREE.Float32BufferAttribute(solid.normals, 3));
      solidGeometry.setAttribute("uv", new THREE.Float32BufferAttribute(solid.uvs, 2));
      solidGeometry.computeBoundingSphere();

      waterGeometry.setIndex(water.indices);
      waterGeometry.setAttribute("position", new THREE.Float32BufferAttribute(water.positions, 3));
      waterGeometry.setAttribute("normal", new THREE.Float32BufferAttribute(water.normals, 3));
      waterGeometry.setAttribute("uv", new THREE.Float32BufferAttribute(water.uvs, 2));
      waterGeometry.computeBoundingSphere();

      dirty = false;
    }

    // ------------------------------------------------------------
    // Terrain generation
    // ------------------------------------------------------------
    function hash2(x, z) {
      let h = Math.imul(x | 0, 374761393) ^ Math.imul(z | 0, 668265263) ^ Math.imul(SEED, 0x9e3779b9);
      h = Math.imul(h ^ (h >>> 13), 1274126177);
      h ^= h >>> 16;
      return (h >>> 0) / 4294967295;
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
      const xf = x - x0;
      const zf = z - z0;

      const v00 = hash2(x0, z0);
      const v10 = hash2(x0 + 1, z0);
      const v01 = hash2(x0, z0 + 1);
      const v11 = hash2(x0 + 1, z0 + 1);

      const u = smooth(xf);
      const v = smooth(zf);

      return lerp(
        lerp(v00, v10, u),
        lerp(v01, v11, u),
        v
      );
    }

    function fbm(x, z) {
      let sum = 0;
      let amp = 0.5;
      let freq = 1;
      for (let i = 0; i < 4; i++) {
        sum += valueNoise2D(x * freq, z * freq) * amp;
        freq *= 2.0;
        amp *= 0.5;
      }
      return sum;
    }

    function generateTerrain() {
      world.fill(AIR);

      const heights = new Uint8Array(WORLD_W * WORLD_D);

      for (let z = 0; z < WORLD_D; z++) {
        for (let x = 0; x < WORLD_W; x++) {
          const base = fbm(x / 30, z / 30);
          const detail = fbm(x / 7 + 500, z / 7 + 500);
          let h = Math.floor(9 + base * 17 + detail * 4);
          h = Math.max(1, Math.min(WORLD_H - 8, h));
          heights[z * WORLD_W + x] = h;
        }
      }

      // Fill blocks
      for (let z = 0; z < WORLD_D; z++) {
        for (let x = 0; x < WORLD_W; x++) {
          const h = heights[z * WORLD_W + x];

          // bedrock layer (cannot be removed because removeBlock rejects y === 0)
          setBlockRaw(x, 0, z, STONE);

          for (let y = 1; y <= h; y++) {
            let block = STONE;

            if (y === h) {
              if (h <= SEA_LEVEL + 1) block = SAND;
              else block = GRASS;
            } else if (y >= h - 3) {
              block = (h <= SEA_LEVEL + 1) ? SAND : DIRT;
            }

            setBlockRaw(x, y, z, block);
          }

          // water
          if (h < SEA_LEVEL) {
            for (let y = h + 1; y <= SEA_LEVEL; y++) {
              setBlockRaw(x, y, z, WATER);
            }
          }
        }
      }

      // Trees
      for (let z = 4; z < WORLD_D - 4; z++) {
        for (let x = 4; x < WORLD_W - 4; x++) {
          const h = heights[z * WORLD_W + x];
          if (getBlock(x, h, z) !== GRASS) continue;
          if (h <= SEA_LEVEL + 1) continue;

          const r = hash2(x * 31 + 17, z * 73 + 91);
          if (r > 0.986) {
            const trunkH = 4 + Math.floor(hash2(x * 101, z * 97) * 3);
            const top = h + trunkH;

            if (top + 3 >= WORLD_H) continue;

            // trunk
            for (let y = h + 1; y <= top; y++) {
              if (getBlock(x, y, z) === AIR) {
                setBlockRaw(x, y, z, WOOD);
              }
            }

            // leaves
            for (let dx = -2; dx <= 2; dx++) {
              for (let dz = -2; dz <= 2; dz++) {
                for (let dy = -1; dy <= 1; dy++) {
                  const bx = x + dx;
                  const by = top + dy;
                  const bz = z + dz;

                  if (!inWorld(bx, by, bz)) continue;
                  if (getBlock(bx, by, bz) !== AIR) continue;

                  const dist = Math.abs(dx) + Math.abs(dy) + Math.abs(dz);
                  if (dist > 4) continue;
                  if (dx === 0 && dz === 0 && dy <= 0) continue;

                  const leafChance = 0.88 - Math.abs(dy) * 0.12 - Math.max(Math.abs(dx), Math.abs(dz)) * 0.08;
                  if (hash2(bx * 57 + by * 13, bz * 89 + by * 31) < leafChance) {
                    setBlockRaw(bx, by, bz, LEAVES);
                  }
                }
              }
            }

            // small top cap
            for (let dx = -1; dx <= 1; dx++) {
              for (let dz = -1; dz <= 1; dz++) {
                const bx = x + dx;
                const by = top + 1;
                const bz = z + dz;
                if (!inWorld(bx, by, bz)) continue;
                if (getBlock(bx, by, bz) !== AIR) continue;
                if (Math.abs(dx) + Math.abs(dz) <= 2 && hash2(bx * 19 + by * 5, bz * 23) > 0.22) {
                  setBlockRaw(bx, by, bz, LEAVES);
                }
              }
            }
          }
        }
      }

      dirty = true;
    }

    generateTerrain();
    rebuildGeometries();

    // ------------------------------------------------------------
    // Player
    // ------------------------------------------------------------
    function surfaceHeightAt(x, z) {
      x = Math.max(0, Math.min(WORLD_W - 1, x));
      z = Math.max(0, Math.min(WORLD_D - 1, z));
      for (let y = WORLD_H - 1; y >= 0; y--) {
        if (isSolidBlock(getBlock(x, y, z))) return y;
      }
      return SEA_LEVEL;
    }

    const player = {
      pos: new THREE.Vector3(),
      vel: new THREE.Vector3(),
      yaw: Math.PI * 0.25,
      pitch: -0.18,
      onGround: false,
      fly: false,
    };

    function respawn() {
      const sx = Math.floor(WORLD_W / 2);
      const sz = Math.floor(WORLD_D / 2);
      const h = surfaceHeightAt(sx, sz);
      player.pos.set(sx + 0.5, h + 1.05, sz + 0.5);
      player.vel.set(0, 0, 0);
      player.onGround = false;
    }

    respawn();

    function collides(px, py, pz) {
      const EPS = 0.0001;

      const minX = Math.floor(px - PLAYER_RADIUS + EPS);
      const maxX = Math.floor(px + PLAYER_RADIUS - EPS);
      const minY = Math.floor(py + EPS);
      const maxY = Math.floor(py + PLAYER_HEIGHT - EPS);
      const minZ = Math.floor(pz - PLAYER_RADIUS + EPS);
      const maxZ = Math.floor(pz + PLAYER_RADIUS - EPS);

      // World bounds as solid walls.
      if (minX < 0 || maxX >= WORLD_W) return true;
      if (minZ < 0 || maxZ >= WORLD_D) return true;
      if (minY < 0) return true;
      if (maxY >= WORLD_H) return false;

      for (let x = minX; x <= maxX; x++) {
        for (let z = minZ; z <= maxZ; z++) {
          for (let y = minY; y <= maxY; y++) {
            if (isSolidBlock(getBlock(x, y, z))) return true;
          }
        }
      }
      return false;
    }

    function moveAxis(axis, amount) {
      if (amount === 0) return;
      const old = player.pos[axis];
      player.pos[axis] += amount;

      if (collides(player.pos.x, player.pos.y, player.pos.z)) {
        player.pos[axis] = old;

        if (axis === "y") {
          if (amount < 0) player.onGround = true;
          player.vel.y = 0;
        } else {
          player.vel[axis] = 0;
        }
      }
    }

    function blockIntersectsPlayer(bx, by, bz) {
      const EPS = 0.0001;
      return (
        bx + 1 > player.pos.x - PLAYER_RADIUS + EPS &&
        bx < player.pos.x + PLAYER_RADIUS - EPS &&
        by + 1 > player.pos.y + EPS &&
        by < player.pos.y + PLAYER_HEIGHT - EPS &&
        bz + 1 > player.pos.z - PLAYER_RADIUS + EPS &&
        bz < player.pos.z + PLAYER_RADIUS - EPS
      );
    }

    // ------------------------------------------------------------
    // Input / Pointer lock
    // ------------------------------------------------------------
    const keys = new Set();
    let pointerLocked = false;

    function requestLock() {
      renderer.domElement.requestPointerLock();
    }

    document.addEventListener("click", () => {
      if (!pointerLocked) requestLock();
    });

    document.addEventListener("pointerlockchange", () => {
      pointerLocked = document.pointerLockElement === renderer.domElement;
      messageEl.style.display = pointerLocked ? "none" : "block";
    });

    document.addEventListener("mousemove", (e) => {
      if (!pointerLocked) return;

      const sens = 0.0022;
      player.yaw -= e.movementX * sens;
      player.pitch -= e.movementY * sens;
      player.pitch = Math.max(-Math.PI / 2 + 0.01, Math.min(Math.PI / 2 - 0.01, player.pitch));
    });

    window.addEventListener("keydown", (e) => {
      keys.add(e.code);

      if (e.code === "Space") {
        e.preventDefault();
      }

      if (!pointerLocked) return;

      if (e.code.startsWith("Digit")) {
        const n = Number(e.code.replace("Digit", "")) - 1;
        if (n >= 0 && n < HOTBAR.length) {
          selected = n;
          updateHotbar();
        }
      }

      if (e.code === "KeyF") {
        player.fly = !player.fly;
        player.vel.y = 0;
      }

      if (e.code === "KeyR") {
        respawn();
      }
    });

    window.addEventListener("keyup", (e) => {
      keys.delete(e.code);
    });

    document.addEventListener("contextmenu", (e) => e.preventDefault());

    document.addEventListener("mousedown", (e) => {
      if (!pointerLocked) return;

      if (e.button === 0) {
        breakTargetBlock();
      } else if (e.button === 2) {
        placeTargetBlock();
      }
    });

    window.addEventListener("resize", () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    });

    // ------------------------------------------------------------
    // Raycast / interaction
    // ------------------------------------------------------------
    const raycaster = new THREE.Raycaster();
    raycaster.far = REACH;
    const screenCenter = new THREE.Vector2(0, 0);

    function getHitNormal(intersect) {
      if (intersect.face && intersect.face.normal) {
        const n = intersect.face.normal.clone();

        // Mesh has no rotation/scale, so local == world here.
        n.x = Math.round(n.x);
        n.y = Math.round(n.y);
        n.z = Math.round(n.z);

        if (n.lengthSq() > 0) {
          n.normalize();
          return n;
        }
      }

      // Fallback: infer face normal from ray direction.
      const d = raycaster.ray.direction.clone();
      const ax = Math.abs(d.x);
      const ay = Math.abs(d.y);
      const az = Math.abs(d.z);
      const n = new THREE.Vector3(0, 0, 0);

      if (ax >= ay && ax >= az) n.x = -Math.sign(d.x);
      else if (ay >= az) n.y = -Math.sign(d.y);
      else n.z = -Math.sign(d.z);

      if (n.lengthSq() === 0) n.y = 1;
      return n;
    }

    function getTargetInfo() {
      raycaster.setFromCamera(screenCenter, camera);
      const hits = raycaster.intersectObject(solidMesh, false);

      if (hits.length === 0) return null;

      const hit = hits[0];
      const normal = getHitNormal(hit);

      // Block that was hit.
      const blockX = Math.floor(hit.point.x - normal.x * 0.5);
      const blockY = Math.floor(hit.point.y - normal.y * 0.5);
      const blockZ = Math.floor(hit.point.z - normal.z * 0.5);

      // Air block adjacent to hit face.
      const placeX = blockX + Math.round(normal.x);
      const placeY = blockY + Math.round(normal.y);
      const placeZ = blockZ + Math.round(normal.z);

      if (!inWorld(blockX, blockY, blockZ)) return null;
      if (!inWorld(placeX, placeY, placeZ)) return null;

      const targetType = getBlock(blockX, blockY, blockZ);
      if (!isSolidBlock(targetType)) return null;

      return {
        block: { x: blockX, y: blockY, z: blockZ },
        place: { x: placeX, y: placeY, z: placeZ },
        hit,
      };
    }

    function breakTargetBlock() {
      const t = getTargetInfo();
      if (!t) return;

      const b = t.block;
      if (b.y === 0) return; // bedrock-like bottom layer

      const type = getBlock(b.x, b.y, b.z);
      if (!isSolidBlock(type)) return;

      setBlockRaw(b.x, b.y, b.z, AIR);

      // If breaking leaves and there is water above? keep simple.
      dirty = true;
    }

    function placeTargetBlock() {
      const t = getTargetInfo();
      if (!t) return;

      const p = t.place;
      if (!inWorld(p.x, p.y, p.z)) return;
      if (getBlock(p.x, p.y, p.z) !== AIR) return;

      const blockType = HOTBAR[selected];
      if (!blockType) return;

      if (blockIntersectsPlayer(p.x, p.y, p.z)) return;

      setBlockRaw(p.x, p.y, p.z, blockType);
      dirty = true;
    }

    // ------------------------------------------------------------
    // Sky / day-night
    // ------------------------------------------------------------
    let dayTime = 0.22; // 0..1
    const tmpColor = new THREE.Color();

    function updateSky(dt) {
      dayTime = (dayTime + dt / 95) % 1;

      const angle = dayTime * Math.PI * 2;
      const sunY = Math.sin(angle);
      const sunX = Math.cos(angle);

      sun.position.set(sunX * 90, sunY * 90, 35);
      sun.intensity = THREE.MathUtils.clamp(sunY, 0, 1) * 1.45;

      const dayFactor = THREE.MathUtils.clamp(sunY + 0.28, 0, 1);

      tmpColor.copy(skyNight).lerp(skyDay, dayFactor);
      scene.background.copy(tmpColor);

      tmpColor.copy(fogNight).lerp(fogDay, dayFactor);
      scene.fog.color.copy(tmpColor);

      ambient.intensity = 0.22 + dayFactor * 0.62;
      hemi.intensity = 0.18 + dayFactor * 0.55;
    }

    // ------------------------------------------------------------
    // Update
    // ------------------------------------------------------------
    function updateMovement(dt) {
      player.onGround = false;

      const sprint = keys.has("ShiftLeft") || keys.has("ShiftRight");

      const f =
        (keys.has("KeyW") ? 1 : 0) -
        (keys.has("KeyS") ? 1 : 0);

      const r =
        (keys.has("KeyD") ? 1 : 0) -
        (keys.has("KeyA") ? 1 : 0);

      const move = new THREE.Vector3();

      if (f !== 0 || r !== 0) {
        // yaw=0: forward = -z, right = +x
        const forward = new THREE.Vector3(-Math.sin(player.yaw), 0, -Math.cos(player.yaw));
        const right = new THREE.Vector3(Math.cos(player.yaw), 0, -Math.sin(player.yaw));
        move.addScaledVector(forward, f);
        move.addScaledVector(right, r);
        move.normalize();
      }

      const speed = player.fly
        ? FLY_SPEED
        : (sprint ? SPRINT_SPEED : WALK_SPEED);

      player.vel.x = move.x * speed;
      player.vel.z = move.z * speed;

      if (player.fly) {
        let up = 0;
        if (keys.has("Space")) up += 1;
        if (keys.has("ShiftLeft") || keys.has("ShiftRight")) up -= 1;
        player.vel.y = up * FLY_SPEED;
      } else {
        if (keys.has("Space") && player.onGround) {
          player.vel.y = JUMP_POWER;
        }

        player.vel.y -= GRAVITY * dt;
        player.vel.y = Math.max(player.vel.y, -38);
      }

      // Move axis by axis for simple voxel collision.
      moveAxis("x", player.vel.x * dt);
      moveAxis("z", player.vel.z * dt);
      moveAxis("y", player.vel.y * dt);

      // Safety respawn if stuck/fell.
      if (player.pos.y < -8) {
        respawn();
      }
    }

    function updateCamera() {
      camera.position.copy(player.pos);
      camera.position.y += PLAYER_EYE;
      camera.rotation.set(player.pitch, player.yaw, 0);
    }

    function updateHighlight() {
      if (!pointerLocked) {
        highlight.visible = false;
        return;
      }

      const t = getTargetInfo();
      if (!t) {
        highlight.visible = false;
        return;
      }

      highlight.visible = true;
      highlight.position.set(
        t.block.x + 0.5,
        t.block.y + 0.5,
        t.block.z + 0.5
      );
    }

    function updateInfo() {
      const p = player.pos;
      const text = `
左クリック: 破壊
右クリック: 設置
WASD: 移動
Space: ジャンプ${player.fly ? " / 上" : ""}
Shift: 走る${player.fly ? " / 下" : ""}
F: 飛行${player.fly ? " ON" : " OFF"}
R: リスポーン
1〜8: ブロック選択
Esc: カーソル解放

座標: ${p.x.toFixed(1)}, ${p.y.toFixed(1)}, ${p.z.toFixed(1)}
選択: ${BLOCKS[HOTBAR[selected]].name}
      `.trim();

      infoEl.textContent = text;
    }

    // ------------------------------------------------------------
    // Main loop
    // ------------------------------------------------------------
    const clock = new THREE.Clock();
    let fpsTimer = 0;
    let fpsFrames = 0;

    function animate() {
      requestAnimationFrame(animate);

      const dt = Math.min(clock.getDelta(), 0.1);

      if (dt > 0) {
        updateMovement(dt);
        updateCamera();
        updateHighlight();
        updateSky(dt);

        if (dirty) {
          rebuildGeometries();
        }

        updateInfo();

        fpsTimer += dt;
        fpsFrames++;
        if (fpsTimer >= 0.5) {
          const fps = fpsFrames / fpsTimer;
          fpsEl.textContent = "FPS: " + fps.toFixed(0);
          fpsTimer = 0;
          fpsFrames = 0;
        }
      }

      renderer.render(scene, camera);
    }

    animate();
  </script>
</body>
</html>
```

遊び方のポイント：

1. 画面をクリックしてマウスロック  
2. 左クリックでブロック破壊、右クリックでブロック設置  
3. `F` で飛行モード、`R` でリスポーン  

必要なら次に、  
- インベントリ  
- クラフト  
- 音  
- 敵・モブ  
- チャンク分割で巨大ワールド  
- セーブ機能  
なども拡張できます。