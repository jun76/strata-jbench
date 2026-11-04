マイクラ風の 3D 箱庭を、**1 ファイルで動く HTML/JS** で作りました。  
ブラウザだけで動きます（Three.js を CDN から読み込むのでインターネット接続が必要です）。

### 使い方
- **クリック**：マウスロック（操作開始）
- **WASD**：移動
- **Space**：ジャンプ
- **Shift**：走る
- **マウス**：視点移動
- **左クリック**：ブロック破壊
- **右クリック**：ブロック設置
- **1〜7**：.hotbar のブロック切替
- **Esc**：マウスロック解除

ファイル名は `index.html` にして保存し、ブラウザで開けば遊べます。

```html
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Web Voxel Sandbox - マイクラ風箱庭</title>
<style>
  html, body {
    margin: 0;
    height: 100%;
    overflow: hidden;
    background: #000;
    font-family: system-ui, -apple-system, sans-serif;
    user-select: none;
  }
  canvas { display: block; }
  #ui {
    position: absolute;
    inset: 0;
    pointer-events: none;
    color: white;
    text-shadow: 0 2px 6px rgba(0,0,0,.8);
  }
  #crosshair {
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    font-size: 28px;
    font-weight: 700;
    color: rgba(255,255,255,.85);
    mix-blend-mode: difference;
  }
  #hotbar {
    position: absolute;
    left: 50%;
    bottom: 18px;
    transform: translateX(-50%);
    display: flex;
    gap: 8px;
    padding: 10px;
    background: rgba(0,0,0,.35);
    border-radius: 12px;
    pointer-events: none;
  }
  .slot {
    width: 46px;
    height: 46px;
    border: 2px solid rgba(255,255,255,.25);
    border-radius: 8px;
    position: relative;
    background: rgba(255,255,255,.08);
  }
  .slot.selected {
    border-color: #fff;
    transform: scale(1.08);
    background: rgba(255,255,255,.18);
  }
  .slot span {
    position: absolute;
    left: 4px;
    top: 2px;
    font-size: 11px;
    color: rgba(255,255,255,.85);
  }
  .slot em {
    position: absolute;
    left: 0;
    right: 0;
    bottom: 2px;
    text-align: center;
    font-size: 11px;
    font-style: normal;
  }
  #overlay {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 18px;
    background: rgba(0,0,0,.45);
    pointer-events: auto;
    text-align: center;
  }
  #overlay.hidden { display: none; }
  #overlay h1 {
    margin: 0;
    font-size: clamp(32px, 6vw, 72px);
    letter-spacing: .06em;
  }
  #overlay p {
    margin: 0;
    line-height: 1.8;
    color: rgba(255,255,255,.88);
  }
  #start {
    border: 0;
    padding: 14px 28px;
    border-radius: 999px;
    font-size: 18px;
    font-weight: 700;
    cursor: pointer;
    color: #122;
    background: linear-gradient(180deg, #fff, #cfe9ff);
    box-shadow: 0 8px 30px rgba(0,0,0,.35);
  }
  #info {
    position: absolute;
    right: 12px;
    top: 12px;
    background: rgba(0,0,0,.35);
    padding: 8px 12px;
    border-radius: 10px;
    font-size: 12px;
    line-height: 1.6;
  }
</style>
</head>
<body>
<div id="ui">
  <div id="crosshair">+</div>
  <div id="hotbar"></div>
  <div id="info">
    WASD:移動 / Space:ジャンプ / Shift:走る<br />
    左クリック:破壊 / 右クリック:設置 / 1-7:ブロック選択<br />
    Esc:マウスロック解除
  </div>
</div>

<div id="overlay">
  <h1>Web Voxel Sandbox</h1>
  <p>
    クリックで開始します。<br />
    マウスを動かして視点、WASD で移動、Space でジャンプ。<br />
    左クリックでブロックを壊し、右クリックで設置できます。
  </p>
  <button id="start">開始</button>
</div>

<script src="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js"></script>
<script>
(() => {
  const SX = 64;
  const SY = 64;
  const SZ = 64;
  const CS = 16;
  const CHUNKS_X = SX / CS;
  const CHUNKS_Z = SZ / CS;

  const BLOCK = {
    AIR: 0,
    GRASS: 1,
    DIRT: 2,
    STONE: 3,
    WOOD: 4,
    LEAVES: 5,
    SAND: 6,
    PLANKS: 7
  };

  const BLOCK_NAMES = {
    [BLOCK.GRASS]: "草",
    [BLOCK.DIRT]: "土",
    [BLOCK.STONE]: "石",
    [BLOCK.WOOD]: "木",
    [BLOCK.LEAVES]: "葉",
    [BLOCK.SAND]: "砂",
    [BLOCK.PLANKS]: "板"
  };

  const BLOCK_COLORS = {
    [BLOCK.GRASS]: "#69b945",
    [BLOCK.DIRT]: "#89613f",
    [BLOCK.STONE]: "#8c8c92",
    [BLOCK.WOOD]: "#6f4f30",
    [BLOCK.LEAVES]: "#398d33",
    [BLOCK.SAND]: "#ddd193",
    [BLOCK.PLANKS]: "#b8885a"
  };

  const hotbarBlocks = [
    BLOCK.GRASS,
    BLOCK.DIRT,
    BLOCK.STONE,
    BLOCK.WOOD,
    BLOCK.LEAVES,
    BLOCK.SAND,
    BLOCK.PLANKS
  ];

  let selectedSlot = 0;

  const data = new Uint8Array(SX * SY * SZ);
  const heightmap = new Uint8Array(SX * SZ);

  function idx(x, y, z) {
    return x + z * SX + y * SX * SZ;
  }

  function inBounds(x, y, z) {
    return x >= 0 && y >= 0 && z >= 0 && x < SX && y < SY && z < SZ;
  }

  function getBlockRaw(x, y, z) {
    if (!inBounds(x, y, z)) return 0;
    return data[idx(x, y, z)];
  }

  function setBlockRaw(x, y, z, v) {
    if (!inBounds(x, y, z)) return;
    data[idx(x, y, z)] = v;
  }

  function isSolid(x, y, z) {
    if (y < 0) return true;
    if (x < 0 || z < 0 || y >= SY || x >= SX || z >= SZ) return false;
    return data[idx(x, y, z)] !== BLOCK.AIR;
  }

  function getBlockForMesh(x, y, z) {
    if (y < 0) return BLOCK.STONE;
    if (!inBounds(x, y, z)) return BLOCK.AIR;
    return data[idx(x, y, z)];
  }

  // ---------------- noise ----------------
  function fract(x) {
    return x - Math.floor(x);
  }

  function hash2(x, z) {
    return fract(Math.sin(x * 127.1 + z * 311.7) * 43758.5453123);
  }

  function smooth(t) {
    return t * t * (3 - 2 * t);
  }

  function noise2(x, z) {
    const ix = Math.floor(x);
    const iz = Math.floor(z);
    const fx = x - ix;
    const fz = z - iz;

    const sx = smooth(fx);
    const sz = smooth(fz);

    const a = hash2(ix, iz);
    const b = hash2(ix + 1, iz);
    const c = hash2(ix, iz + 1);
    const d = hash2(ix + 1, iz + 1);

    return a * (1 - sx) * (1 - sz) +
           b * sx * (1 - sz) +
           c * (1 - sx) * sz +
           d * sx * sz;
  }

  function fbm(x, z) {
    return (
      noise2(x, z) * 0.5 +
      noise2(x * 2.03, z * 2.03) * 0.3 +
      noise2(x * 4.11, z * 4.11) * 0.2
    );
  }

  // ---------------- world generation ----------------
  function generateWorld() {
    const sea = 15;

    for (let z = 0; z < SZ; z++) {
      for (let x = 0; x < SX; x++) {
        const n = fbm(x * 0.045, z * 0.045);
        const m = Math.pow(noise2(x * 0.018, z * 0.018), 1.6);

        let h = Math.floor(20 + n * 16 + m * 14);
        h = Math.max(3, Math.min(SY - 10, h));

        heightmap[x + z * SX] = h;

        for (let y = 0; y <= h; y++) {
          let id = BLOCK.STONE;

          if (y === h) {
            id = (h <= sea + 2) ? BLOCK.SAND : BLOCK.GRASS;
          } else if (y >= h - 3) {
            id = BLOCK.DIRT;
          }

          data[idx(x, y, z)] = id;
        }
      }
    }

    // trees
    for (let z = 2; z < SZ - 2; z++) {
      for (let x = 2; x < SX - 2; x++) {
        const h = heightmap[x + z * SX];
        if (getBlockRaw(x, h, z) !== BLOCK.GRASS) continue;
        if (h <= 15 || h >= SY - 8) continue;

        const r = hash2(x * 2.17, z * 3.91);
        if (r > 0.012) continue;

        const trunkH = 4 + (hash2(x, z) > 0.5 ? 1 : 0);
        const top = h + trunkH;
        if (top >= SY - 3) continue;

        for (let y = h + 1; y <= top; y++) {
          setBlockRaw(x, y, z, BLOCK.WOOD);
        }

        for (let y = top - 1; y <= top + 1; y++) {
          const rad = (y <= top - 1) ? 2 : 2;
          for (let dx = -rad; dx <= rad; dx++) {
            for (let dz = -rad; dz <= rad; dz++) {
              if (dx === 0 && dz === 0 && y <= top) continue;
              if (Math.abs(dx) === rad && Math.abs(dz) === rad) continue;
              const bx = x + dx;
              const bz = z + dz;
              if (getBlockRaw(bx, y, bz) === BLOCK.AIR) {
                setBlockRaw(bx, y, bz, BLOCK.LEAVES);
              }
            }
          }
        }

        const cy = top + 2;
        for (let dx = -1; dx <= 1; dx++) {
          for (let dz = -1; dz <= 1; dz++) {
            if (Math.abs(dx) === 1 && Math.abs(dz) === 1) continue;
            const bx = x + dx;
            const bz = z + dz;
            if (getBlockRaw(bx, cy, bz) === BLOCK.AIR) {
              setBlockRaw(bx, cy, bz, BLOCK.LEAVES);
            }
          }
        }
      }
    }
  }

  // ---------------- texture atlas ----------------
  function clampByte(v) {
    return Math.max(0, Math.min(255, Math.round(v)));
  }

  function rgb(r, g, b, a = 1) {
    return `rgba(${clampByte(r)}, ${clampByte(g)}, ${clampByte(b)}, ${a})`;
  }

  function createAtlas() {
    const size = 64;
    const tile = 16;
    const canvas = document.createElement("canvas");
    canvas.width = size;
    canvas.height = size;
    const ctx = canvas.getContext("2d");

    function drawTile(i, fn) {
      const tx = (i % 4) * tile;
      const ty = Math.floor(i / 4) * tile;

      ctx.save();
      ctx.beginPath();
      ctx.rect(tx, ty, tile, tile);
      ctx.clip();
      ctx.translate(tx, ty);
      fn(ctx);
      ctx.restore();
    }

    function fillNoise(ctx, r, g, b, variance) {
      for (let y = 0; y < 16; y++) {
        for (let x = 0; x < 16; x++) {
          const d = (Math.random() - 0.5) * variance;
          ctx.fillStyle = rgb(r + d, g + d * 0.8, b + d * 0.55);
          ctx.fillRect(x, y, 1, 1);
        }
      }
    }

    // 0: grass top
    drawTile(0, (c) => fillNoise(c, 95, 175, 75, 38));

    // 1: grass side
    drawTile(1, (c) => {
      fillNoise(c, 130, 96, 66, 26);
      for (let y = 0; y < 16; y++) {
        for (let x = 0; x < 16; x++) {
          if (y < 4) {
            const d = (Math.random() - 0.5) * 40;
            c.fillStyle = rgb(88 + d, 168 + d, 70 + d, 1);
            c.fillRect(x, y, 1, 1);
          }
        }
      }
      // jagged grass edge
      for (let x = 0; x < 16; x++) {
        const h = 4 + (Math.random() > 0.65 ? 1 : 0);
        for (let y = 4; y < h; y++) {
          c.fillStyle = rgb(78, 154, 60, 1);
          c.fillRect(x, y, 1, 1);
        }
      }
    });

    // 2: dirt
    drawTile(2, (c) => fillNoise(c, 132, 96, 65, 30));

    // 3: stone
    drawTile(3, (c) => {
      fillNoise(c, 128, 128, 134, 28);
      for (let i = 0; i < 10; i++) {
        c.fillStyle = rgb(105, 105, 112, 0.65);
        c.fillRect(Math.floor(Math.random() * 13), Math.floor(Math.random() * 14), 3, 2);
      }
    });

    // 4: wood side
    drawTile(4, (c) => {
      fillNoise(c, 110, 80, 48, 22);
      for (let x = 0; x < 16; x++) {
        if (x % 3 === 0) {
          c.fillStyle = rgb(70, 48, 28, 0.55);
          c.fillRect(x, 0, 1, 16);
        }
      }
    });

    // 5: leaves
    drawTile(5, (c) => {
      fillNoise(c, 52, 128, 48, 52);
      for (let i = 0; i < 60; i++) {
        const x = Math.floor(Math.random() * 16);
        const y = Math.floor(Math.random() * 16);
        c.fillStyle = rgb(30, 92, 30, 0.8);
        c.fillRect(x, y, 1, 1);
      }
      for (let i = 0; i < 22; i++) {
        const x = Math.floor(Math.random() * 16);
        const y = Math.floor(Math.random() * 16);
        c.fillStyle = rgb(96, 185, 82, 0.7);
        c.fillRect(x, y, 1, 1);
      }
    });

    // 6: sand
    drawTile(6, (c) => fillNoise(c, 222, 207, 151, 22));

    // 7: planks
    drawTile(7, (c) => {
      fillNoise(c, 176, 138, 92, 22);

      c.fillStyle = rgb(90, 62, 34, 0.85);
      [3, 7, 11, 15].forEach(y => c.fillRect(0, y, 16, 1));

      c.fillStyle = rgb(110, 78, 46, 0.65);
      c.fillRect(8, 0, 1, 4);
      c.fillRect(3, 4, 1, 4);
      c.fillRect(12, 8, 1, 4);
      c.fillRect(6, 12, 1, 4);
    });

    // 8: wood top / rings
    drawTile(8, (c) => {
      for (let y = 0; y < 16; y++) {
        for (let x = 0; x < 16; x++) {
          const dx = x - 7.5;
          const dy = y - 7.5;
          const d = Math.sqrt(dx * dx + dy * dy);

          let r = 178, g = 138, b = 88;

          if (d > 6.7) {
            r = 118; g = 82; b = 48;
          } else {
            const ring = Math.floor(d * 1.8) % 3;
            if (ring === 0) { r -= 34; g -= 28; b -= 24; }
            if (ring === 1) { r += 6; g += 4; b += 2; }
          }

          const n = (Math.random() - 0.5) * 18;
          c.fillStyle = rgb(r + n, g + n * 0.8, b + n * 0.5);
          c.fillRect(x, y, 1, 1);
        }
      }
    });

    const tex = new THREE.CanvasTexture(canvas);
    tex.magFilter = THREE.NearestFilter;
    tex.minFilter = THREE.NearestFilter;
    tex.generateMipmaps = false;
    tex.colorSpace = THREE.SRGBColorSpace;
    return tex;
  }

  // ---------------- three scene ----------------
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setClearColor(0x88bbee);
  document.body.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x88bbee);
  scene.fog = new THREE.Fog(0x88bbee, 45, 170);

  const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 500);
  camera.rotation.order = "YXZ";

  const hemi = new THREE.HemisphereLight(0xbfe7ff, 0x6f6255, 0.65);
  scene.add(hemi);

  const sun = new THREE.DirectionalLight(0xfff2d5, 1.0);
  sun.position.set(25, 80, 15);
  scene.add(sun);

  const atlas = createAtlas();
  const blockMaterial = new THREE.MeshLambertMaterial({
    map: atlas,
    side: THREE.DoubleSide
  });

  // ---------------- meshing ----------------
  const FACES = [
    {
      dir: [1, 0, 0],
      corners: [
        [1, 0, 0],
        [1, 1, 0],
        [1, 1, 1],
        [1, 0, 1]
      ],
      uv: [
        [0, 0],
        [0, 1],
        [1, 1],
        [1, 0]
      ]
    },
    {
      dir: [-1, 0, 0],
      corners: [
        [0, 0, 1],
        [0, 1, 1],
        [0, 1, 0],
        [0, 0, 0]
      ],
      uv: [
        [0, 0],
        [0, 1],
        [1, 1],
        [1, 0]
      ]
    },
    {
      dir: [0, 1, 0],
      corners: [
        [0, 1, 1],
        [1, 1, 1],
        [1, 1, 0],
        [0, 1, 0]
      ],
      uv: [
        [0, 0],
        [1, 0],
        [1, 1],
        [0, 1]
      ]
    },
    {
      dir: [0, -1, 0],
      corners: [
        [0, 0, 0],
        [1, 0, 0],
        [1, 0, 1],
        [0, 0, 1]
      ],
      uv: [
        [0, 0],
        [1, 0],
        [1, 1],
        [0, 1]
      ]
    },
    {
      dir: [0, 0, 1],
      corners: [
        [1, 0, 1],
        [1, 1, 1],
        [0, 1, 1],
        [0, 0, 1]
      ],
      uv: [
        [0, 0],
        [0, 1],
        [1, 1],
        [1, 0]
      ]
    },
    {
      dir: [0, 0, -1],
      corners: [
        [0, 0, 0],
        [0, 1, 0],
        [1, 1, 0],
        [1, 0, 0]
      ],
      uv: [
        [0, 0],
        [0, 1],
        [1, 1],
        [1, 0]
      ]
    }
  ];

  function blockTexture(id, face) {
    switch (id) {
      case BLOCK.GRASS:
        if (face === 2) return 0;
        if (face === 3) return 2;
        return 1;
      case BLOCK.DIRT: return 2;
      case BLOCK.STONE: return 3;
      case BLOCK.WOOD:
        if (face === 2 || face === 3) return 8;
        return 4;
      case BLOCK.LEAVES: return 5;
      case BLOCK.SAND: return 6;
      case BLOCK.PLANKS: return 7;
      default: return 3;
    }
  }

  const chunkMeshes = new Map();
  const dirtyChunks = new Set();

  function chunkKey(cx, cz) {
    return cx + "," + cz;
  }

  function markDirty(cx, cz) {
    if (cx >= 0 && cz >= 0 && cx < CHUNKS_X && cz < CHUNKS_Z) {
      dirtyChunks.add(chunkKey(cx, cz));
    }
  }

  function markBlockDirty(x, z) {
    const cx = Math.floor(x / CS);
    const cz = Math.floor(z / CS);

    markDirty(cx, cz);

    if (x % CS === 0) markDirty(cx - 1, cz);
    if (x % CS === CS - 1) markDirty(cx + 1, cz);
    if (z % CS === 0) markDirty(cx, cz - 1);
    if (z % CS === CS - 1) markDirty(cx, cz + 1);
  }

  function addFace(id, faceIndex, x, y, z, positions, normals, uvs) {
    const face = FACES[faceIndex];
    const tile = blockTexture(id, faceIndex);

    const pad = 0.025;
    const col = tile % 4;
    const row = Math.floor(tile / 4);

    const u0 = (col + pad) / 4;
    const u1 = (col + 1 - pad) / 4;

    // Three.js CanvasTexture has flipY=true by default.
    // Row 0 is top of canvas, so it should map to higher V.
    const v0 = (3 - row + pad) / 4;
    const v1 = (4 - row - pad) / 4;

    function pushVertex(cornerIndex) {
      const c = face.corners[cornerIndex];
      positions.push(x + c[0], y + c[1], z + c[2]);
      normals.push(face.dir[0], face.dir[1], face.dir[2]);

      const uv = face.uv[cornerIndex];
      uvs.push(
        u0 + uv[0] * (u1 - u0),
        v0 + uv[1] * (v1 - v0)
      );
    }

    pushVertex(0);
    pushVertex(1);
    pushVertex(2);

    pushVertex(0);
    pushVertex(2);
    pushVertex(3);
  }

  function buildChunk(cx, cz) {
    const key = chunkKey(cx, cz);
    const positions = [];
    const normals = [];
    const uvs = [];

    const x0 = cx * CS;
    const z0 = cz * CS;
    const x1 = Math.min(SX, x0 + CS);
    const z1 = Math.min(SZ, z0 + CS);

    for (let x = x0; x < x1; x++) {
      for (let z = z0; z < z1; z++) {
        for (let y = 0; y < SY; y++) {
          const id = getBlockRaw(x, y, z);
          if (id === BLOCK.AIR) continue;

          for (let f = 0; f < FACES.length; f++) {
            const dir = FACES[f].dir;
            const nx = x + dir[0];
            const ny = y + dir[1];
            const nz = z + dir[2];

            const neighbor = getBlockForMesh(nx, ny, nz);
            if (neighbor !== BLOCK.AIR) continue;

            addFace(id, f, x, y, z, positions, normals, uvs);
          }
        }
      }
    }

    let mesh = chunkMeshes.get(key);

    if (!mesh) {
      mesh = new THREE.Mesh(new THREE.BufferGeometry(), blockMaterial);
      mesh.matrixAutoUpdate = false;
      chunkMeshes.set(key, mesh);
      scene.add(mesh);
    }

    if (mesh.geometry) {
      mesh.geometry.dispose();
    }

    if (positions.length === 0) {
      mesh.geometry = new THREE.BufferGeometry();
      mesh.visible = false;
    } else {
      const geo = new THREE.BufferGeometry();
      geo.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
      geo.setAttribute("normal", new THREE.Float32BufferAttribute(normals, 3));
      geo.setAttribute("uv", new THREE.Float32BufferAttribute(uvs, 2));
      geo.computeBoundingSphere();
      mesh.geometry = geo;
      mesh.visible = true;
    }
  }

  function processDirtyChunks() {
    if (dirtyChunks.size === 0) return;

    const keys = Array.from(dirtyChunks);
    dirtyChunks.clear();

    for (const key of keys) {
      const [cx, cz] = key.split(",").map(Number);
      buildChunk(cx, cz);
    }
  }

  // ---------------- target highlight ----------------
  const highlightBox = new THREE.LineSegments(
    new THREE.EdgesGeometry(new THREE.BoxGeometry(1.002, 1.002, 1.002)),
    new THREE.LineBasicMaterial({ color: 0x111111, opacity: 0.55, transparent: true })
  );
  highlightBox.visible = false;
  scene.add(highlightBox);

  // ---------------- player ----------------
  const PLAYER_HALF = 0.3;
  const PLAYER_HEIGHT = 1.8;
  const EYE = 1.62;

  const player = {
    pos: new THREE.Vector3(SX / 2 + 0.5, 40, SZ / 2 + 0.5),
    vel: new THREE.Vector3(),
    onGround: false,
    yaw: 0,
    pitch: -0.08
  };

  function surfaceHeightAt(x, z) {
    x = Math.floor(x);
    z = Math.floor(z);
    if (x < 0 || z < 0 || x >= SX || z >= SZ) return 30;

    for (let y = SY - 1; y >= 0; y--) {
      if (isSolid(x, y, z)) return y + 1;
    }
    return 10;
  }

  function resetPlayer() {
    const x = SX / 2 + 0.5;
    const z = SZ / 2 + 0.5;
    player.pos.set(x, surfaceHeightAt(x, z) + 0.2, z);
    player.vel.set(0, 0, 0);
    player.onGround = true;
  }

  // ---------------- collision ----------------
  function aabbCollides(pos) {
    const minX = Math.floor(pos.x - PLAYER_HALF + 1e-5);
    const maxX = Math.floor(pos.x + PLAYER_HALF - 1e-5);

    const minY = Math.floor(pos.y + 1e-5);
    const maxY = Math.floor(pos.y + PLAYER_HEIGHT - 1e-5);

    const minZ = Math.floor(pos.z - PLAYER_HALF + 1e-5);
    const maxZ = Math.floor(pos.z + PLAYER_HALF - 1e-5);

    for (let x = minX; x <= maxX; x++) {
      for (let y = minY; y <= maxY; y++) {
        for (let z = minZ; z <= maxZ; z++) {
          if (isSolid(x, y, z)) return true;
        }
      }
    }

    return false;
  }

  function moveAxis(axis, delta) {
    if (delta === 0) return;

    const old = player.pos[axis];
    player.pos[axis] += delta;

    if (!aabbCollides(player.pos)) return;

    if (axis === "x") {
      if (delta > 0) {
        player.pos.x = Math.floor(player.pos.x + PLAYER_HALF + 1e-5) - PLAYER_HALF - 1e-3;
      } else {
        player.pos.x = Math.floor(player.pos.x - PLAYER_HALF - 1e-5) + 1 + PLAYER_HALF + 1e-3;
      }
      player.vel.x = 0;
    } else if (axis === "z") {
      if (delta > 0) {
        player.pos.z = Math.floor(player.pos.z + PLAYER_HALF + 1e-5) - PLAYER_HALF - 1e-3;
      } else {
        player.pos.z = Math.floor(player.pos.z - PLAYER_HALF - 1e-5) + 1 + PLAYER_HALF + 1e-3;
      }
      player.vel.z = 0;
    } else if (axis === "y") {
      if (delta < 0) {
        player.pos.y = Math.floor(player.pos.y + 1e-5) + 1 + 1e-3;
        player.onGround = true;
      } else {
        player.pos.y = Math.floor(player.pos.y + PLAYER_HEIGHT - 1e-5) - PLAYER_HEIGHT - 1e-3;
      }
      player.vel.y = 0;
    }
  }

  function playerIntersectsBlock(x, y, z) {
    const minX = player.pos.x - PLAYER_HALF;
    const maxX = player.pos.x + PLAYER_HALF;
    const minY = player.pos.y;
    const maxY = player.pos.y + PLAYER_HEIGHT;
    const minZ = player.pos.z - PLAYER_HALF;
    const maxZ = player.pos.z + PLAYER_HALF;

    return x < maxX &&
           x + 1 > minX &&
           y < maxY &&
           y + 1 > minY &&
           z < maxZ &&
           z + 1 > minZ;
  }

  // ---------------- input ----------------
  const keys = {};

  const overlay = document.getElementById("overlay");
  const hotbarEl = document.getElementById("hotbar");
  const slotEls = [];

  function buildHotbar() {
    hotbarEl.innerHTML = "";
    slotEls.length = 0;

    hotbarBlocks.forEach((block, i) => {
      const slot = document.createElement("div");
      slot.className = "slot" + (i === selectedSlot ? " selected" : "");
      slot.style.background = `linear-gradient(180deg, rgba(255,255,255,.28), rgba(255,255,255,.04)), ${BLOCK_COLORS[block]}`;

      const num = document.createElement("span");
      num.textContent = (i + 1).toString();

      const name = document.createElement("em");
      name.textContent = BLOCK_NAMES[block];

      slot.appendChild(num);
      slot.appendChild(name);
      hotbarEl.appendChild(slot);
      slotEls.push(slot);
    });
  }

  function setSelected(i) {
    selectedSlot = Math.max(0, Math.min(hotbarBlocks.length - 1, i));
    slotEls.forEach((el, idx) => {
      el.classList.toggle("selected", idx === selectedSlot);
    });
  }

  window.addEventListener("keydown", (e) => {
    keys[e.code] = true;

    if (e.code.startsWith("Digit")) {
      const n = Number(e.code.slice(5));
      if (n >= 1 && n <= hotbarBlocks.length) {
        setSelected(n - 1);
      }
    }

    if (e.code === "Space") e.preventDefault();
  });

  window.addEventListener("keyup", (e) => {
    keys[e.code] = false;
  });

  document.addEventListener("pointerlockchange", () => {
    const locked = document.pointerLockElement === renderer.domElement;
    overlay.classList.toggle("hidden", locked);
  });

  renderer.domElement.addEventListener("mousemove", (e) => {
    if (document.pointerLockElement !== renderer.domElement) return;

    player.yaw -= e.movementX * 0.0023;
    player.pitch -= e.movementY * 0.0023;

    const maxPitch = Math.PI / 2 - 0.01;
    player.pitch = Math.max(-maxPitch, Math.min(maxPitch, player.pitch));
  });

  document.addEventListener("contextmenu", (e) => e.preventDefault());

  renderer.domElement.addEventListener("mousedown", (e) => {
    if (document.pointerLockElement !== renderer.domElement) {
      renderer.domElement.requestPointerLock();
      return;
    }

    if (e.button === 0) {
      breakBlock();
    } else if (e.button === 2) {
      placeBlock();
    }
  });

  document.getElementById("start").addEventListener("click", () => {
    renderer.domElement.requestPointerLock();
  });

  // ---------------- voxel raycast ----------------
  function raycastVoxel(origin, dir, maxDistance = 6.5) {
    let x = Math.floor(origin.x);
    let y = Math.floor(origin.y);
    let z = Math.floor(origin.z);

    const stepX = dir.x > 0 ? 1 : -1;
    const stepY = dir.y > 0 ? 1 : -1;
    const stepZ = dir.z > 0 ? 1 : -1;

    const tDeltaX = dir.x !== 0 ? Math.abs(1 / dir.x) : Infinity;
    const tDeltaY = dir.y !== 0 ? Math.abs(1 / dir.y) : Infinity;
    const tDeltaZ = dir.z !== 0 ? Math.abs(1 / dir.z) : Infinity;

    let tMaxX = dir.x > 0
      ? (Math.floor(origin.x) + 1 - origin.x) / dir.x
      : dir.x < 0
        ? (Math.floor(origin.x) - origin.x) / dir.x
        : Infinity;

    let tMaxY = dir.y > 0
      ? (Math.floor(origin.y) + 1 - origin.y) / dir.y
      : dir.y < 0
        ? (Math.floor(origin.y) - origin.y) / dir.y
        : Infinity;

    let tMaxZ = dir.z > 0
      ? (Math.floor(origin.z) + 1 - origin.z) / dir.z
      : dir.z < 0
        ? (Math.floor(origin.z) - origin.z) / dir.z
        : Infinity;

    let nx = 0, ny = 0, nz = 0;

    for (let i = 0; i < 160; i++) {
      if (isSolid(x, y, z)) {
        return { hit: true, x, y, z, nx, ny, nz };
      }

      if (tMaxX < tMaxY && tMaxX < tMaxZ) {
        if (tMaxX > maxDistance) break;
        x += stepX;
        tMaxX += tDeltaX;
        nx = -stepX;
        ny = 0;
        nz = 0;
      } else if (tMaxY < tMaxZ) {
        if (tMaxY > maxDistance) break;
        y += stepY;
        tMaxY += tDeltaY;
        nx = 0;
        ny = -stepY;
        nz = 0;
      } else {
        if (tMaxZ > maxDistance) break;
        z += stepZ;
        tMaxZ += tDeltaZ;
        nx = 0;
        ny = 0;
        nz = -stepZ;
      }
    }

    return { hit: false };
  }

  let lastTarget = null;

  function updateTarget() {
    const origin = camera.position;
    const dir = new THREE.Vector3();
    camera.getWorldDirection(dir);

    const target = raycastVoxel(origin, dir, 6.0);
    lastTarget = target;

    if (target.hit) {
      highlightBox.visible = true;
      highlightBox.position.set(target.x + 0.5, target.y + 0.5, target.z + 0.5);
    } else {
      highlightBox.visible = false;
    }
  }

  function breakBlock() {
    if (!lastTarget || !lastTarget.hit) return;

    const { x, y, z } = lastTarget;
    if (!inBounds(x, y, z)) return;

    setBlockRaw(x, y, z, BLOCK.AIR);
    markBlockDirty(x, z);
  }

  function placeBlock() {
    if (!lastTarget || !lastTarget.hit) return;

    const x = lastTarget.x + lastTarget.nx;
    const y = lastTarget.y + lastTarget.ny;
    const z = lastTarget.z + lastTarget.nz;

    if (!inBounds(x, y, z)) return;
    if (getBlockRaw(x, y, z) !== BLOCK.AIR) return;
    if (playerIntersectsBlock(x, y, z)) return;

    setBlockRaw(x, y, z, hotbarBlocks[selectedSlot]);
    markBlockDirty(x, z);
  }

  // ---------------- update loop ----------------
  let prevTime = performance.now();

  function updatePlayer(dt) {
    const sprint = keys["ShiftLeft"] || keys["ShiftRight"];
    const speed = sprint ? 8.0 : 4.7;

    const forward = new THREE.Vector3(-Math.sin(player.yaw), 0, -Math.cos(player.yaw));
    const right = new THREE.Vector3(Math.cos(player.yaw), 0, -Math.sin(player.yaw));

    const wish = new THREE.Vector3();

    if (keys["KeyW"]) wish.add(forward);
    if (keys["KeyS"]) wish.sub(forward);
    if (keys["KeyD"]) wish.add(right);
    if (keys["KeyA"]) wish.sub(right);

    if (wish.lengthSq() > 0) {
      wish.normalize().multiplyScalar(speed);
    }

    const accel = player.onGround ? 36 : 11;
    const blend = Math.min(1, accel * dt);

    player.vel.x += (wish.x - player.vel.x) * blend;
    player.vel.z += (wish.z - player.vel.z) * blend;

    player.vel.y -= 28.0 * dt;
    if (player.vel.y < -55) player.vel.y = -55;

    if (player.onGround && keys["Space"]) {
      player.vel.y = 9.2;
      player.onGround = false;
    }

    moveAxis("x", player.vel.x * dt);
    player.onGround = false;
    moveAxis("y", player.vel.y * dt);
    moveAxis("z", player.vel.z * dt);

    // keep player inside world bounds
    player.pos.x = Math.max(PLAYER_HALF + 0.01, Math.min(SX - PLAYER_HALF - 0.01, player.pos.x));
    player.pos.z = Math.max(PLAYER_HALF + 0.01, Math.min(SZ - PLAYER_HALF - 0.01, player.pos.z));

    if (player.pos.y < -8) {
      resetPlayer();
    }

    camera.position.set(
      player.pos.x,
      player.pos.y + EYE,
      player.pos.z
    );

    camera.rotation.set(player.pitch, player.yaw, 0, "YXZ");
  }

  function animate() {
    requestAnimationFrame(animate);

    const now = performance.now();
    let dt = (now - prevTime) / 1000;
    prevTime = now;

    dt = Math.min(dt, 0.05);

    updatePlayer(dt);
    updateTarget();
    processDirtyChunks();

    renderer.render(scene, camera);
  }

  function resize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  }

  window.addEventListener("resize", resize);

  // ---------------- boot ----------------
  generateWorld();
  buildHotbar();
  setSelected(0);

  for (let cz = 0; cz < CHUNKS_Z; cz++) {
    for (let cx = 0; cx < CHUNKS_X; cx++) {
      buildChunk(cx, cz);
    }
  }

  resetPlayer();
  animate();
})();
</script>
</body>
</html>
```

必要なら次は  
**地形を無限生成、洞窟、水、スニーク、ブロック保存、クラフト風メニュー、音、モバイル対応**  
なども追加できます。