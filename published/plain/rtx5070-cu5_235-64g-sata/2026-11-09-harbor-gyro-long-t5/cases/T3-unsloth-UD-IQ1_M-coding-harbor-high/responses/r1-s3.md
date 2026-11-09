Save the following as a `.html` file and open it in Chrome. It uses no external libraries, so it renders immediately as a self-contained WebGL voxel scene.

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Voxel Harbor — Sailing Ship Calling In</title>
<style>
  html, body {
    margin: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
    background: #0b0f12;
  }
  canvas {
    display: block;
    touch-action: none;
  }
  #info {
    position: fixed;
    top: 12px;
    left: 12px;
    color: #fff;
    font: 13px/1.35 system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
    background: rgba(0, 0, 0, 0.35);
    padding: 8px 10px;
    border-radius: 8px;
    pointer-events: none;
  }
</style>
</head>
<body>
<div id="info">Left-drag: orbit • Right-drag: pan • Wheel: zoom</div>

<script>
(function () {
  try {
    const info = document.getElementById("info");
    const canvas = document.createElement("canvas");
    document.body.appendChild(canvas);

    const gl = canvas.getContext("webgl2", { antialias: true });
    if (!gl) {
      info.textContent = "WebGL2 is required to view this scene.";
      return;
    }

    const vsSrc = `#version 300 es
      layout(location=0) in vec3 aPos;
      layout(location=1) in vec3 aNormal;
      layout(location=2) in mat4 aMat;
      layout(location=6) in vec3 aColor;

      uniform mat4 uVP;
      uniform mat4 uModel;

      out vec3 vColor;
      out vec3 vNormal;
      out vec3 vWorldPos;

      void main() {
        mat4 m = uModel * aMat;
        vec4 world = m * vec4(aPos, 1.0);
        vWorldPos = world.xyz;
        vNormal = normalize(mat3(m) * aNormal);
        vColor = aColor;
        gl_Position = uVP * world;
      }
    `;

    const fsSrc = `#version 300 es
      precision highp float;

      in vec3 vColor;
      in vec3 vNormal;
      in vec3 vWorldPos;

      uniform vec3 uCamera;
      uniform vec3 uFogColor;
      uniform vec3 uLanternPos;
      uniform vec3 uLanternColor;

      out vec4 fragColor;

      void main() {
        vec3 n = normalize(vNormal);
        vec3 lightDir = normalize(vec3(0.45, 0.9, 0.35));

        float ndl = max(dot(n, lightDir), 0.0);
        float shade = 0.45 + 0.62 * ndl + 0.18 * max(n.y, 0.0);
        vec3 col = vColor * shade;

        float d = distance(vWorldPos, uCamera);
        float fog = clamp((d - 100.0) / 280.0, 0.0, 1.0);
        col = mix(col, uFogColor, fog * 0.75);

        float lantern = max(0.0, 1.0 - distance(vWorldPos, uLanternPos) / 35.0);
        col += uLanternColor * lantern * lantern * 0.28;

        fragColor = vec4(col, 1.0);
      }
    `;

    function compileShader(type, src) {
      const s = gl.createShader(type);
      gl.shaderSource(s, src);
      gl.compileShader(s);
      if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {
        throw new Error(gl.getShaderInfoLog(s));
      }
      return s;
    }

    const program = gl.createProgram();
    gl.attachShader(program, compileShader(gl.VERTEX_SHADER, vsSrc));
    gl.attachShader(program, compileShader(gl.FRAGMENT_SHADER, fsSrc));
    gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
      throw new Error(gl.getProgramInfoLog(program));
    }
    gl.useProgram(program);

    const uVP = gl.getUniformLocation(program, "uVP");
    const uModel = gl.getUniformLocation(program, "uModel");
    const uCamera = gl.getUniformLocation(program, "uCamera");
    const uFogColor = gl.getUniformLocation(program, "uFogColor");
    const uLanternPos = gl.getUniformLocation(program, "uLanternPos");
    const uLanternColor = gl.getUniformLocation(program, "uLanternColor");

    // Unit cube geometry, centered at origin, extents [-0.5, 0.5].
    const pos = [];
    const norm = [];
    const idx = [];

    function addQuad(a, b, c, d, n) {
      const start = pos.length / 3;
      pos.push(a[0], a[1], a[2], b[0], b[1], b[2], c[0], c[1], c[2], d[0], d[1], d[2]);
      norm.push(n[0], n[1], n[2], n[0], n[1], n[2], n[0], n[1], n[2], n[0], n[1], n[2]);
      idx.push(start, start + 1, start + 2, start, start + 2, start + 3);
    }

    const A = [-0.5, -0.5, -0.5];
    const B = [0.5, -0.5, -0.5];
    const C = [0.5, 0.5, -0.5];
    const D = [-0.5, 0.5, -0.5];
    const E = [-0.5, -0.5, 0.5];
    const F = [0.5, -0.5, 0.5];
    const G = [0.5, 0.5, 0.5];
    const H = [-0.5, 0.5, 0.5];

    addQuad(F, G, H, E, [0, 0, 1]);   // +Z
    addQuad(A, C, G, F, [0, 0, -1]);  // -Z
    addQuad(F, B, C, G, [1, 0, 0]);   // +X
    addQuad(E, A, D, H, [-1, 0, 0]);  // -X
    addQuad(G, C, D, H, [0, 1, 0]);   // +Y
    addQuad(F, B, A, E, [0, -1, 0]);  // -Y

    const vertexBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, vertexBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(pos), gl.STATIC_DRAW);

    const normalBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, normalBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(norm), gl.STATIC_DRAW);

    const indexBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, indexBuffer);
    gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, new Uint16Array(idx), gl.STATIC_DRAW);

    const indexCount = idx.length;

    // Instance data buffers.
    const staticMatrices = [];
    const staticColors = [];
    const shipMatrices = [];
    const shipColors = [];

    function rotX(v, a) {
      const c = Math.cos(a), s = Math.sin(a);
      return [v[0], v[1] * c - v[2] * s, v[1] * s + v[2] * c];
    }
    function rotY(v, a) {
      const c = Math.cos(a), s = Math.sin(a);
      return [v[0] * c + v[2] * s, v[1], -v[0] * s + v[2] * c];
    }
    function rotZ(v, a) {
      const c = Math.cos(a), s = Math.sin(a);
      return [v[0] * c - v[1] * s, v[0] * s + v[1] * c, v[2]];
    }

    function composeMatrix(x, y, z, rx, ry, rz, sx, sy, sz) {
      if (rx === 0 && ry === 0 && rz === 0) {
        return [
          sx, 0, 0, 0,
          0, sy, 0, 0,
          0, 0, sz, 0,
          x, y, z, 1
        ];
      }

      let ax = [1, 0, 0];
      let ay = [0, 1, 0];
      let az = [0, 0, 1];

      ax = rotX(ax, rx); ay = rotX(ay, rx); az = rotX(az, rx);
      ax = rotY(ax, ry); ay = rotY(ay, ry); az = rotY(az, ry);
      ax = rotZ(ax, rz); ay = rotZ(ay, rz); az = rotZ(az, rz);

      return [
        ax[0] * sx, ax[1] * sx, ax[2] * sx, 0,
        ay[0] * sy, ay[1] * sy, ay[2] * sy, 0,
        az[0] * sz, az[1] * sz, az[2] * sz, 0,
        x, y, z, 1
      ];
    }

    function addInstance(matrices, colors, w, h, d, color, x, y, z, rx = 0, ry = 0, rz = 0) {
      if (w <= 0 || h <= 0 || d <= 0) return;
      const m = composeMatrix(x, y, z, rx, ry, rz, w, h, d);
      for (let i = 0; i < 16; i++) matrices.push(m[i]);

      const r = ((color >> 16) & 255) / 255;
      const g = ((color >> 8) & 255) / 255;
      const b = (color & 255) / 255;
      colors.push(r, g, b);
    }

    function addStatic(w, h, d, color, x, y, z, rx = 0, ry = 0, rz = 0) {
      addInstance(staticMatrices, staticColors, w, h, d, color, x, y, z, rx, ry, rz);
    }

    function addShip(w, h, d, color, x, y, z, rx = 0, ry = 0, rz = 0) {
      addInstance(shipMatrices, shipColors, w, h, d, color, x, y, z, rx, ry, rz);
    }

    function clamp(v, a, b) {
      return v < a ? a : v > b ? b : v;
    }

    function hash(x, z) {
      const n = Math.sin(x * 127.1 + z * 311.7) * 43758.5453;
      return n - Math.floor(n);
    }

    function lineBox(add, a, b, color, thickness) {
      const dx = b[0] - a[0];
      const dy = b[1] - a[1];
      const dz = b[2] - a[2];
      const len = Math.hypot(dx, dy, dz);
      if (len < 0.01) return;

      const mx = (a[0] + b[0]) * 0.5;
      const my = (a[1] + b[1]) * 0.5;
      const mz = (a[2] + b[2]) * 0.5;

      const ry = Math.atan2(dx, dz);
      const ratio = clamp(dy / len, -1, 1);
      const rx = -Math.asin(ratio);

      add(thickness, thickness, len, color, mx, my, mz, rx, ry, 0);
    }

    function lineScene(a, b, color, t = 0.1) {
      lineBox(addStatic, a, b, color, t);
    }

    function lineShip(a, b, color, t = 0.08) {
      lineBox(addShip, a, b, color, t);
    }

    // ---------------------------------------------------------------------
    // Scene palette
    // ---------------------------------------------------------------------
    const water1 = 0x25739d;
    const water2 = 0x1e6790;
    const ocean = 0x1e5e88;
    const woodLight = 0x8b5e34;
    const woodDark = 0x4b311d;
    const sand1 = 0x9d8a61;
    const sand2 = 0x8a7955;
    const stone1 = 0x8f8d86;
    const stone2 = 0x716f68;
    const red = 0xc0392b;
    const white = 0xf3f0e6;
    const roofRed = 0x7d3b31;
    const crate = 0xa2764c;
    const rigDark = 0x282624;
    const sailColor = 0xf4efe1;
    const sailShadow = 0xcfc7b6;
    const mastColor = 0x6b4225;

    // ---------------------------------------------------------------------
    // Harbor / land / buildings
    // ---------------------------------------------------------------------
    function makeBuilding(cx, cz, w, d, h, wall, roof) {
      addStatic(w, h, d, wall, cx, 1 + h / 2, cz);
      addStatic(w + 0.8, 1, d + 0.8, roof, cx, 1 + h + 0.5, cz);
      if (w > 4) addStatic(w - 2, 1, d - 2, roof, cx, 1 + h + 1.5, cz);
      if (w > 6) addStatic(w - 4, 1, d - 4, roof, cx, 1 + h + 2.5, cz);

      const doorX = cx - w / 2 - 0.12;
      addStatic(0.25, 3, 2, 0x2f241c, doorX, 2.5, cz);
      addStatic(0.25, 1.4, 1.4, 0xc5d9e6, doorX, 1 + h - 1.5, cz - 2);
      addStatic(0.25, 1.4, 1.4, 0xc5d9e6, doorX, 1 + h - 1.5, cz + 2);
    }

    function makeTree(x, z) {
      addStatic(1, 4, 1, 0x5a3d24, x, 3, z);
      addStatic(5, 2, 5, 0x43803f, x, 5, z);
      addStatic(3, 2, 3, 0x356b35, x, 6, z);
    }

    function buildHarbor() {
      // Large ocean plate.
      addStatic(700, 1, 700, ocean, 0, -0.6, 0);

      // Blocky water near the harbor.
      for (let x = -36; x <= 10; x += 3) {
        for (let z = -36; z <= 36; z += 3) {
          const r = hash(x, z);
          if (r < 0.03) continue;
          const col = r < 0.45 ? water1 : water2;
          const lift = Math.abs(Math.floor(r * 10) - 4) * 0.018;
          addStatic(3, 0.6, 3, col, x, -0.32 + lift, z);
        }
      }

      // Dock planking and piles.
      for (let z = -18; z <= 18; z += 2) {
        addStatic(2, 1, 2, woodLight, 9, 0.5, z);
      }
      for (let z = -18; z <= 18; z += 4) {
        addStatic(1.2, 2.5, 1.2, woodDark, 9, -1.25, z);
      }

      // Main harbor land block.
      for (let x = 11; x <= 23; x += 2) {
        for (let z = -18; z <= 18; z += 2) {
          const c = hash(x, z) > 0.5 ? sand1 : sand2;
          addStatic(2, 2, 2, c, x, 0, z);
        }
      }

      // Breakwaters.
      for (let x = 1; x <= 10; x += 2) {
        for (const bz of [19, -19]) {
          addStatic(2, 2, 2, hash(x, bz) > 0.5 ? stone1 : stone2, x, 0, bz);
          if (hash(x, bz) > 0.55) {
            addStatic(1.1, 1, 1.1, stone2, x + 0.5, 0.5, bz + 0.5);
          }
        }
      }
      addStatic(2, 2, 2, stone1, 11, 0, 19);
      addStatic(2, 2, 2, stone1, 11, 0, -19);

      // Lighthouse on the southern breakwater.
      addStatic(6, 2, 6, 0x7e8088, 1, 0, -19);
      addStatic(4, 2, 4, 0xe9e9e9, 1, 2, -19);
      const bands = [red, white, red, white, red];
      for (let i = 0; i < 4; i++) {
        addStatic(4, 2, 4, bands[i], 1, 4 + i * 2, -19);
      }
      addStatic(5.2, 0.6, 5.2, 0x333333, 1, 11.3, -19);
      addStatic(3.4, 2.2, 3.4, 0xffe9a6, 1, 12.6, -19);
      addStatic(4.4, 0.8, 4.4, 0x8f3a34, 1, 14.0, -19);

      // Warehouses / houses.
      makeBuilding(15, -12, 8, 8, 5, 0xb65a4f, roofRed);
      makeBuilding(15, 0, 10, 8, 6, 0x5a7d9d, 0x314658);
      makeBuilding(15, 12, 8, 8, 5, 0x9b8661, 0x6f4c36);
      makeBuilding(21, -15, 6, 6, 4, 0x7d654b, 0x54382b);
      makeBuilding(21, 15, 6, 6, 4, 0x8f6d52, 0x5b3f2e);

      // A little greenery.
      makeTree(22, -14);
      makeTree(22, 14);
      makeTree(22, 0);

      // Dock clutter: bollards, barrels, crates.
      for (let z = -16; z <= 16; z += 4) {
        addStatic(0.7, 1.2, 0.7, 0x3e3e3e, 8.15, 1.6, z);
      }

      for (let z = -15; z <= 15; z += 7) {
        addStatic(1.6, 2.4, 1.6, 0x704d38, 8.5, 2.2, z);
        addStatic(1.9, 0.2, 1.9, 0x303030, 8.5, 2.0, z);
        addStatic(1.9, 0.2, 1.9, 0x303030, 8.5, 2.4, z);
      }

      for (let z = -12; z <= 12; z += 6) {
        addStatic(2, 2, 2, crate, 8.5, 2, z);
        addStatic(1, 1, 1, 0xb98a5c, 8.5, 3.5, z + 1.5);
      }

      // Mooring buoy.
      addStatic(3, 1, 3, 0xc0392b, -14, 0.5, 12);
      addStatic(3, 1, 3, 0xf2f2f2, -14, 1.5, 12);
      addStatic(0.3, 3, 0.3, 0x333333, -14, 3, 12);
      addStatic(1.2, 0.8, 0.2, 0xc0392b, -13.4, 4.3, 12);

      // Clouds.
      function cloud(x, y, z, s) {
        addStatic(22 * s, 5 * s, 8 * s, 0xffffff, x, y, z);
        addStatic(14 * s, 6 * s, 10 * s, 0xffffff, x + 9 * s, y + 0.7 * s, z);
        addStatic(10 * s, 4 * s, 7 * s, 0xffffff, x - 13 * s, y - 0.5 * s, z);
      }
      cloud(-120, 90, 210, 1.2);
      cloud(170, 105, -170, 1.0);
      cloud(-20, 115, -60, 0.7);
    }

    // ---------------------------------------------------------------------
    // Sailing ship
    // ---------------------------------------------------------------------
    function buildShip() {
      const hullBottom = 0x2e1e12;
      const hullMid = 0x664326;
      const hullTop = 0x483120;
      const bulwark = 0x5b3a22;
      const deck = 0x9a7043;

      function halfWidth(z) {
        if (z <= -11) return 2;
        if (z <= -10) return 3;
        if (z <= -9) return 3;
        if (z <= -8) return 4;
        if (z >= 10) return 1;
        if (z >= 9) return 2;
        if (z >= 8) return 3;
        return 4;
      }

      // Hull shell.
      for (let z = -11; z <= 10; z++) {
        const hw = halfWidth(z);
        for (let x = -hw; x <= hw; x++) {
          const edge = Math.abs(x) === hw || z === -11 || z === 10;
          if (edge) {
            addShip(1, 1, 1, hullBottom, x, 0.5, z);
            addShip(1, 1, 1, hullMid, x, 1.5, z);
            addShip(1, 1, 1, hullTop, x, 2.5, z);
            addShip(1, 1, 1, bulwark, x, 3.5, z);
          } else if (z > -11 && z < 10) {
            addShip(1, 1, 1, deck, x, 2.5, z);
          }
        }
      }

      // Stern castle / poop deck.
      addShip(7, 1, 3, deck, 0, 3.5, -9.5);
      addShip(7.5, 2.5, 1, 0x3e2718, 0, 4.25, -10.5);
      addShip(0.6, 1.5, 3, 0x3e2718, -3.25, 4.25, -9.5);
      addShip(0.6, 1.5, 3, 0x3e2718, 3.25, 4.25, -9.5);

      for (let i = -1; i <= 1; i++) {
        addShip(0.3, 0.9, 0.8, 0xd7eaff, -2 * i, 4.6, -11.2);
      }
      addShip(7.5, 0.3, 0.3, 0xc8a66b, 0, 4.0, -11.2);
      addShip(7.5, 0.3, 0.3, 0xc8a66b, 0, 5.1, -11.2);

      // Forecastle.
      addShip(6.5, 1, 3, deck, 0, 3.5, 8.5);
      addShip(6.5, 2.5, 1, 0x3e2718, 0, 4.25, 10.5);
      addShip(0.6, 1.5, 2, 0x3e2718, -3, 4.25, 8.5);
      addShip(0.6, 1.5, 2, 0x3e2718, 3, 4.25, 8.5);

      // Figurehead.
      addShip(0.6, 2, 0.6, 0xbca07a, 0, 2.8, 11.2);

      // Bowsprit.
      addShip(0.6, 0.6, 8, mastColor, 0, 4.3, 13, -0.28, 0, 0);

      // Gun ports and cannons.
      for (let z = -5; z <= 5; z += 2) {
        addShip(0.45, 1, 1, 0x111111, 4.25, 2.5, z);
        addShip(0.45, 1, 1, 0x111111, -4.25, 2.5, z);
        addShip(0.9, 0.7, 0.7, 0x232323, 4.85, 2.5, z);
        addShip(0.9, 0.7, 0.7, 0x232323, -4.85, 2.5, z);
      }

      // Deck details.
      addShip(2.5, 0.25, 4, 0x664a31, 0, 3.1, -2);
      addShip(1, 1.2, 1, mastColor, 0, 3.6, 2);
      addShip(1.6, 0.2, 1.6, 0x50331f, 0, 3.0, 2);
      addShip(1, 1.6, 1, 0x704d38, 2, 3.8, -4);
      addShip(1, 1.6, 1, 0x704d38, -2, 3.8, 4);

      function mast(z, h, base = 3) {
        addShip(0.7, h, 0.7, mastColor, 0, base + h / 2, z);
      }

      function yard(z, y, w) {
        addShip(w, 0.4, 0.4, mastColor, 0, y, z);
      }

      function sail(y, w, h, z, color = sailColor) {
        const sy = y - h / 2 - 0.35;
        addShip(w, h, 0.25, color, 0, sy, z);
        for (let i = -1; i <= 1; i++) {
          addShip(0.12, h - 0.5, 0.26, sailShadow, i * w * 0.25, sy, z);
        }
      }

      // Foremast.
      mast(7, 14);
      yard(7, 8, 10);   sail(8, 10, 4.5, 7);
      yard(7, 12, 8);   sail(12, 8, 3.2, 7);
      yard(7, 15, 6);   sail(15, 6, 2.2, 7);

      // Mainmast.
      mast(0, 16);
      yard(0, 9, 12);   sail(9, 12, 5, 0);
      yard(0, 14, 10);  sail(14, 10, 3.8, 0);
      yard(0, 18, 8);   sail(18, 8, 2.5, 0);

      // Mizzenmast.
      mast(-7, 12);
      yard(-7, 8, 9);   sail(8, 9, 4, -7);
      yard(-7, 11.5, 7); sail(11.5, 7, 3, -7);

      // Flagpoles and flags.
      addShip(0.2, 2, 0.2, mastColor, 0, 20.0, 0);
      addShip(0.18, 1.6, 0.18, mastColor, 0, 17.3, 7);
      addShip(0.18, 1.4, 0.18, mastColor, 0, 15.2, -7);

      addShip(1.8, 1.2, 0.12, 0xd94f41, 1.1, 20.4, 0, 0, 0, -0.12);
      addShip(1.2, 0.8, 0.1, 0x16a3c7, 0.7, 17.6, 7, 0, 0, -0.15);

      // Rigging as thin voxel cylinders/boxes.
      const railY = 3.6;
      function shrouds(z, topY) {
        for (const sx of [-4.15, 4.15]) {
          for (const sz of [z - 3, z + 3]) {
            lineShip([0, topY, z], [sx, railY, sz], rigDark, 0.07);
          }
        }
      }
      shrouds(7, 17);
      shrouds(0, 19);
      shrouds(-7, 15);

      lineShip([0, 19, 0], [0, 4.8, 10], rigDark, 0.09);
      lineShip([0, 19, 0], [0, 4.8, -11], rigDark, 0.09);
      lineShip([0, 17, 7], [0, 4.8, 10], rigDark, 0.09);
      lineShip([0, 15, -7], [0, 4.8, -11], rigDark, 0.09);

      const tip = [0, 5.4, 16.85];
      lineShip(tip, [0, 19, 0], rigDark, 0.07);
      lineShip(tip, [0, 17, 7], rigDark, 0.07);
      lineShip(tip, [0, 4.8, 11], rigDark, 0.07);
      lineShip(tip, [0, 8, 7], rigDark, 0.07);
      lineShip([0, 4.3, 10], tip, rigDark, 0.06);
    }

    buildHarbor();
    buildShip();

    function makeBuffer(data) {
      const buf = gl.createBuffer();
      gl.bindBuffer(gl.ARRAY_BUFFER, buf);
      gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(data), gl.STATIC_DRAW);
      return buf;
    }

    const staticMatrixBuffer = makeBuffer(staticMatrices);
    const staticColorBuffer = makeBuffer(staticColors);
    const shipMatrixBuffer = makeBuffer(shipMatrices);
    const shipColorBuffer = makeBuffer(shipColors);

    const staticCount = staticColors.length / 3;
    const shipCount = shipColors.length / 3;

    function makeVAO(matrixBuffer, colorBuffer) {
      const vao = gl.createVertexArray();
      gl.bindVertexArray(vao);

      gl.bindBuffer(gl.ARRAY_BUFFER, vertexBuffer);
      gl.enableVertexAttribArray(0);
      gl.vertexAttribPointer(0, 3, gl.FLOAT, false, 0, 0);

      gl.bindBuffer(gl.ARRAY_BUFFER, normalBuffer);
      gl.enableVertexAttribArray(1);
      gl.vertexAttribPointer(1, 3, gl.FLOAT, false, 0, 0);

      gl.bindBuffer(gl.ARRAY_BUFFER, matrixBuffer);
      const stride = 16 * 4;
      for (let i = 0; i < 4; i++) {
        gl.enableVertexAttribArray(2 + i);
        gl.vertexAttribPointer(2 + i, 4, gl.FLOAT, false, stride, i * 16);
        gl.vertexAttribDivisor(2 + i, 1);
      }

      gl.bindBuffer(gl.ARRAY_BUFFER, colorBuffer);
      gl.enableVertexAttribArray(6);
      gl.vertexAttribPointer(6, 3, gl.FLOAT, false, 0, 0);
      gl.vertexAttribDivisor(6, 1);

      gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, indexBuffer);
      gl.bindVertexArray(null);
      return vao;
    }

    const staticVAO = makeVAO(staticMatrixBuffer, staticColorBuffer);
    const shipVAO = makeVAO(shipMatrixBuffer, shipColorBuffer);

    gl.enable(gl.DEPTH_TEST);
    gl.disable(gl.CULL_FACE);

    gl.uniform3f(uFogColor, 0.53, 0.71, 0.84);
    gl.uniform3f(uLanternPos, 1, 12.6, -19);
    gl.uniform3f(uLanternColor, 1.0, 0.82, 0.5);

    // ---------------------------------------------------------------------
    // Camera and orbit controls
    // ---------------------------------------------------------------------
    const target = [0, 5, 0];
    const eye = [0, 0, 0];
    let yaw = -2.4;
    let pitch = 0.32;
    let dist = 70;

    function normalize(v) {
      const l = Math.hypot(v[0], v[1], v[2]) || 1;
      return [v[0] / l, v[1] / l, v[2] / l];
    }
    function cross(a, b) {
      return [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0]
      ];
    }
    function dot(a, b) {
      return a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
    }

    function perspective(fovy, aspect, near, far) {
      const f = 1 / Math.tan(fovy / 2);
      const nf = 1 / (near - far);
      return [
        f / aspect, 0, 0, 0,
        0, f, 0, 0,
        0, 0, (far + near) * nf, -1,
        0, 0, 2 * far * near * nf, 0
      ];
    }

    function lookAt(e, t, up) {
      const z = normalize([e[0] - t[0], e[1] - t[1], e[2] - t[2]]);
      const x = normalize(cross(up, z));
      const y = cross(z, x);

      return [
        x[0], y[0], z[0], 0,
        x[1], y[1], z[1], 0,
        x[2], y[2], z[2], 0,
        -dot(x, e), -dot(y, e), -dot(z, e), 1
      ];
    }

    function matMul(a, b) {
      const out = new Array(16);
      for (let col = 0; col < 4; col++) {
        for (let row = 0; row < 4; row++) {
          let s = 0;
          for (let k = 0; k < 4; k++) {
            s += a[k * 4 + row] * b[col * 4 + k];
          }
          out[col * 4 + row] = s;
        }
      }
      return out;
    }

    function updateCamera() {
      const cp = Math.cos(pitch);
      const sp = Math.sin(pitch);
      eye[0] = target[0] + dist * Math.sin(yaw) * cp;
      eye[1] = target[1] + dist * sp;
      eye[2] = target[2] + dist * Math.cos(yaw) * cp;
    }

    let drag = null;

    canvas.addEventListener("contextmenu", e => e.preventDefault());

    canvas.addEventListener("pointerdown", e => {
      drag = {
        pointerId: e.pointerId,
        button: e.button,
        x: e.clientX,
        y: e.clientY
      };
      canvas.setPointerCapture(e.pointerId);
    });

    canvas.addEventListener("pointerup", e => {
      if (drag && drag.pointerId === e.pointerId) {
        drag = null;
        canvas.releasePointerCapture(e.pointerId);
      }
    });

    canvas.addEventListener("pointercancel", () => { drag = null; });

    canvas.addEventListener("pointermove", e => {
      if (!drag || drag.pointerId !== e.pointerId) return;

      const dx = e.clientX - drag.x;
      const dy = e.clientY - drag.y;
      drag.x = e.clientX;
      drag.y = e.clientY;

      if (drag.button === 0) {
        yaw -= dx * 0.005;
        pitch -= dy * 0.005;
        pitch = clamp(pitch, 0.05, 1.35);
      } else if (drag.button === 2) {
        updateCamera();
        const view = lookAt(eye, target, [0, 1, 0]);
        const right = [view[0], view[1], view[2]];
        const up = [view[4], view[5], view[6]];
        const scale = dist * 0.0018;

        target[0] -= right[0] * dx * scale;
        target[1] -= right[1] * dx * scale;
        target[2] -= right[2] * dx * scale;

        target[0] -= up[0] * dy * scale;
        target[1] -= up[1] * dy * scale;
        target[2] -= up[2] * dy * scale;

        target[0] = clamp(target[0], -35, 45);
        target[1] = clamp(target[1], 0, 25);
        target[2] = clamp(target[2], -55, 55);
      }
    });

    canvas.addEventListener("wheel", e => {
      e.preventDefault();
      dist *= Math.exp(e.deltaY * 0.001);
      dist = clamp(dist, 12, 220);
    }, { passive: false });

    function resize() {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      gl.viewport(0, 0, canvas.width, canvas.height);
    }
    window.addEventListener("resize", resize);
    resize();

    const vpArr = new Float32Array(16);
    const modelArr = new Float32Array(16);
    const identityArr = new Float32Array([
      1, 0, 0, 0,
      0, 1, 0, 0,
      0, 0, 1, 0,
      0, 0, 0, 1
    ]);

    function draw(time) {
      requestAnimationFrame(draw);
      const t = time * 0.001;

      updateCamera();
      const proj = perspective(55 * Math.PI / 180, canvas.width / canvas.height, 0.1, 1000);
      const view = lookAt(eye, target, [0, 1, 0]);
      const vp = matMul(proj, view);
      for (let i = 0; i < 16; i++) vpArr[i] = vp[i];

      gl.useProgram(program);
      gl.clearColor(0.53, 0.71, 0.84, 1);
      gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

      gl.uniformMatrix4fv(uVP, false, vpArr);
      gl.uniform3f(uCamera, eye[0], eye[1], eye[2]);

      // Static harbor.
      gl.uniformMatrix4fv(uModel, false, identityArr);
      gl.bindVertexArray(staticVAO);
      gl.drawElementsInstanced(gl.TRIANGLES, indexCount, gl.UNSIGNED_SHORT, 0, staticCount);

      // Bobbing ship.
      const bob = -0.15 + Math.sin(t * 1.1) * 0.12;
      const roll = Math.sin(t * 0.7) * 0.015;
      const pitchShip = Math.sin(t * 0.4) * 0.008;
      const shipM = composeMatrix(-6, bob, 0, pitchShip, 0, roll, 1, 1, 1);
      for (let i = 0; i < 16; i++) modelArr[i] = shipM[i];

      gl.uniformMatrix4fv(uModel, false, modelArr);
      gl.bindVertexArray(shipVAO);
      gl.drawElementsInstanced(gl.TRIANGLES, indexCount, gl.UNSIGNED_SHORT, 0, shipCount);
    }

    requestAnimationFrame(draw);
  } catch (err) {
    const info = document.getElementById("info");
    if (info) info.textContent = "Initialization failed: " + err.message;
  }
})();
</script>
</body>
</html>
```