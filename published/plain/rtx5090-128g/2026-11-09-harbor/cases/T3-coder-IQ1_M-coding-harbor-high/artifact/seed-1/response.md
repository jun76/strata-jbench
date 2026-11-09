Below is a complete single-file HTML page. Paste it into a `.html` file and open it in Chrome. It uses no external libraries, renders immediately, and you can rotate with the mouse by dragging, zoom with the wheel/pinch, and reset with a double-click.

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Voxel harbor — sailing ship calling at harbor</title>
<style>
  html, body {
    width: 100%;
    height: 100%;
    margin: 0;
    overflow: hidden;
    background: #cfe7f3;
  }
  #scene {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    cursor: grab;
    background: linear-gradient(180deg, #88c9e8 0%, #c5e6f2 45%, #f2fafe 100%);
  }
  #hint {
    position: fixed;
    bottom: 14px;
    left: 14px;
    font-family: system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
    font-size: 13px;
    color: #223441;
    opacity: 0.82;
    pointer-events: none;
    white-space: pre;
  }
</style>
</head>
<body>
<canvas id="scene"></canvas>
<div id="hint">Drag: rotate • Wheel/pinch: zoom • Double-click: reset</div>
<script>
(() => {
  const canvas = document.getElementById('scene');
  function fail(msg) {
    document.getElementById('hint').textContent = msg;
  }

  const gl = canvas.getContext('webgl', {
    alpha: true,
    antialias: true,
    depth: true,
    stencil: false,
    premultipliedAlpha: true
  });

  if (!gl) {
    fail('WebGL is not available in this browser.');
    return;
  }

  const FACE_VERTS = [
    [
      0.5,-0.5,-0.5, 0.5,-0.5,0.5, 0.5,0.5,0.5,
      0.5,-0.5,-0.5, 0.5,0.5,0.5, 0.5,0.5,-0.5
    ],
    [
      -0.5,-0.5,0.5, -0.5,-0.5,-0.5, -0.5,0.5,-0.5,
      -0.5,-0.5,0.5, -0.5,0.5,-0.5, -0.5,0.5,0.5
    ],
    [
      -0.5,0.5,-0.5, 0.5,0.5,-0.5, 0.5,0.5,0.5,
      -0.5,0.5,-0.5, 0.5,0.5,0.5, -0.5,0.5,0.5
    ],
    [
      -0.5,-0.5,0.5, 0.5,-0.5,0.5, 0.5,-0.5,-0.5,
      -0.5,-0.5,0.5, 0.5,-0.5,-0.5, -0.5,-0.5,-0.5
    ],
    [
      -0.5,-0.5,0.5, 0.5,-0.5,0.5, 0.5,0.5,0.5,
      -0.5,-0.5,0.5, 0.5,0.5,0.5, -0.5,0.5,0.5
    ],
    [
      0.5,-0.5,-0.5, -0.5,-0.5,-0.5, -0.5,0.5,-0.5,
      0.5,-0.5,-0.5, -0.5,0.5,-0.5, 0.5,0.5,-0.5
    ]
  ];

  const FACE_NORMALS = [
    [1,0,0],
    [-1,0,0],
    [0,1,0],
    [0,-1,0],
    [0,0,1],
    [0,0,-1]
  ];

  const pos = [];
  const nrm = [];
  const col = [];
  const colorCache = {};

  function parseColor(hex) {
    const cached = colorCache[hex];
    if (cached) return cached;

    let h = hex.replace('#', '');
    if (h.length === 3) {
      h = h[0] + h[0] + h[1] + h[1] + h[2] + h[2];
    }

    const r = parseInt(h.slice(0, 2), 16) / 255;
    const g = parseInt(h.slice(2, 4), 16) / 255;
    const b = parseInt(h.slice(4, 6), 16) / 255;
    return colorCache[hex] = [r, g, b];
  }

  function addBox(cx, cy, cz, sx, sy, sz, hex) {
    if (sx <= 0 || sy <= 0 || sz <= 0) return;

    const c = parseColor(hex);

    for (let f = 0; f < 6; f++) {
      const n = FACE_NORMALS[f];
      const v = FACE_VERTS[f];

      for (let i = 0; i < 18; i += 3) {
        pos.push(
          cx + v[i] * sx,
          cy + v[i + 1] * sy,
          cz + v[i + 2] * sz
        );
        nrm.push(n[0], n[1], n[2]);
        col.push(c[0], c[1], c[2]);
      }
    }
  }

  function buildScene() {
    const SHIP_Z = 5;

    // Water
    addBox(0, -1, 0, 180, 1, 180, '#2f6f95');

    // Water texture / waves
    for (let x = -45; x <= 45; x += 3) {
      for (let z = -45; z <= 45; z += 3) {
        const inShip = (x >= -22 && x <= 1 && z >= 1 && z <= 10);
        const inPier = (x >= 4 && x <= 8 && z >= 0 && z <= 17);
        const inQuay = (x >= -27 && x <= 27 && z >= 11 && z <= 21);
        if (inShip || inPier || inQuay) continue;

        const s = Math.sin(x * 0.75) + Math.cos(z * 0.55);
        if (s > 0.25) {
          addBox(x, -0.44, z, 1.4, 0.10, 1.4, '#3f85a4');
        } else if (s > -0.05) {
          addBox(x, -0.46, z, 1.0, 0.06, 1.0, '#2b678c');
        }
      }
    }

    // Harbor quay
    addBox(0, 0, 16, 54, 1, 10, '#c6b294');
    addBox(0, -0.5, 11.7, 54, 2, 0.6, '#9d917a');
    addBox(0, -0.5, 21.7, 54, 2, 0.6, '#8d826c');
    addBox(0, 0.3, 12.2, 54, 0.2, 0.25, '#d5c5a6');

    function tree(x, z) {
      addBox(x, 2, z, 0.55, 3, 0.55, '#694b2e');
      addBox(x, 4.1, z, 2.8, 1, 2.8, '#5b8b39');
      addBox(x, 5, z, 2, 1.1, 2, '#699c42');
      addBox(x, 5.9, z, 1.2, 0.8, 1.2, '#74af4d');
    }

    function lamp(x, z) {
      addBox(x, 2, z, 0.14, 3, 0.14, '#353d47');
      addBox(x, 3.6, z, 0.45, 0.35, 0.45, '#ffe79a');
    }

    tree(-6, 19);
    tree(15, 19);
    lamp(-12, 18);
    lamp(3, 18);
    lamp(20, 18);

    // Pier
    addBox(6, 0, 9, 3, 1, 18, '#9d6a40');
    addBox(6, -0.5, 9, 3, 2, 18, '#7b5533');

    for (let z = 0; z <= 16; z += 4) {
      addBox(4, -1.5, z, 0.8, 3, 0.8, '#6c472d');
      addBox(8, -1.5, z, 0.8, 3, 0.8, '#6c472d');
    }

    for (let z = 1; z <= 17; z += 8) {
      addBox(5, 0.95, z, 0.8, 0.9, 0.8, '#5b6573');
      addBox(7, 0.95, z, 0.8, 0.9, 0.8, '#5b6573');
    }

    // Gangplank between ship and pier
    addBox(2.5, 1.05, SHIP_Z, 5.2, 0.18, 1.2, '#c29256');
    addBox(2.5, 0.97, SHIP_Z - 0.6, 5.2, 0.08, 0.12, '#8c6441');

    // Warehouse
    addBox(-13, 3, 23, 10, 5, 4, '#c84f3a');
    addBox(-13, 6, 23, 10.6, 1.2, 4.4, '#7a3f2d');
    addBox(-13, 1.8, 21, 1.8, 2.4, 0.22, '#744d2c');
    addBox(-16, 3.5, 21, 1.1, 1.1, 0.22, '#9dd7df');
    addBox(-10, 3.5, 21, 1.1, 1.1, 0.22, '#9dd7df');
    addBox(-16.5, 5.5, 22.5, 1.1, 2.4, 1.1, '#57545c');

    // Harbor office
    addBox(11, 2.5, 23.5, 8, 4, 4.5, '#719ea7');
    addBox(11, 4.8, 23.5, 8.6, 0.8, 4.9, '#45666f');
    addBox(11, 1.5, 21.2, 1.6, 2, 0.22, '#573c2b');
    addBox(8.5, 3, 21.2, 1, 1.2, 0.22, '#9dd7df');
    addBox(13.5, 3, 21.2, 1, 1.2, 0.22, '#9dd7df');

    // Lighthouse
    addBox(18, 1.5, 18, 3.2, 2, 3.2, '#d7d2c6');
    addBox(18, 4.5, 18, 2.4, 4, 2.4, '#eee9df');
    addBox(18, 3.5, 18, 2.6, 0.8, 2.6, '#d5423f');
    addBox(18, 5.5, 18, 2.6, 0.8, 2.6, '#d5423f');
    addBox(18, 7, 18, 2.8, 0.5, 2.8, '#222b36');
    addBox(18, 7.6, 18, 2.4, 1.1, 2.4, '#ffd96b');
    addBox(18, 8.6, 18, 3, 0.3, 3, '#253b45');
    addBox(18, 9, 18, 2.2, 0.6, 2.2, '#36515c');

    // Cargo on quay
    addBox(6, 1.1, 0, 1.2, 1.2, 1.2, '#c17c41');
    addBox(6, 1.75, 0, 1.4, 0.08, 1.4, '#8a5733');

    addBox(7.6, 1.1, 1.6, 1.2, 1.2, 1.2, '#b46f3c');
    addBox(7.6, 2.3, 1.6, 1.1, 1.1, 1.1, '#c78045');

    addBox(8, 1.25, 10, 1.2, 1.4, 1.2, '#a05d37');
    addBox(8, 1.95, 10, 1.45, 0.08, 1.45, '#7a4728');

    // ----------------------------------------------------------------------
    // Sailing ship
    // ----------------------------------------------------------------------

    const hullHalf = [];

    for (let x = -20; x <= 0; x++) {
      let hw = 3;
      if (x <= -19) hw = 1;
      else if (x === -18) hw = 2;
      else if (x >= 0) hw = 1;
      else if (x >= -1) hw = 2;

      hullHalf.push(hw);

      if (x > -19 && x < 0) {
        for (let zz = -hw; zz <= hw; zz++) {
          addBox(x, -1, SHIP_Z + zz, 1, 1, 1, '#3f434b');
        }
      }

      for (let zz = -hw; zz <= hw; zz++) {
        const side = (zz === -hw || zz === hw);
        addBox(
          x, 0, SHIP_Z + zz, 1, 1, 1,
          side ? '#7b4d2b' : '#a36036'
        );
      }

      if (x > -19 && x < -1) {
        for (let zz = -hw + 1; zz <= hw - 1; zz++) {
          addBox(x, 1, SHIP_Z + zz, 1, 1, 1, '#d5a765');
        }
      }
    }

    // White upper hull stripe
    for (let i = 0; i < hullHalf.length; i++) {
      const x = -20 + i;
      const hw = hullHalf[i];
      if (hw > 0) {
        addBox(x, 0.1, SHIP_Z + hw, 1, 0.3, 0.2, '#f1e6d0');
        addBox(x, 0.1, SHIP_Z - hw, 1, 0.3, 0.2, '#f1e6d0');
      }
    }

    // Red waterline stripe
    for (let i = 0; i < hullHalf.length; i++) {
      const x = -20 + i;
      const hw = hullHalf[i];
      if (hw > 0 && x >= -18 && x <= -1) {
        addBox(x, -0.25, SHIP_Z + hw, 1, 0.3, 0.18, '#c84243');
        addBox(x, -0.25, SHIP_Z - hw, 1, 0.3, 0.18, '#c84243');
      }
    }

    // Bowsprit
    addBox(2, 1.5, SHIP_Z, 4, 0.35, 0.4, '#c8975e');
    addBox(2, 2.2, SHIP_Z, 0.3, 1.2, 0.3, '#c8975e');

    // Jib
    addBox(-1, 4.5, SHIP_Z, 0.25, 3, 2.2, '#f0e9d4');

    // Masts
    function addMast(x, h) {
      for (let y = 2; y <= h; y++) {
        addBox(x, y, SHIP_Z, 0.6, 1, 0.6, '#c8995f');
      }
    }

    addMast(-4, 9);
    addMast(-10, 12);
    addMast(-17, 7);

    // Yards
    addBox(-4, 5, SHIP_Z, 0.4, 0.4, 7, '#b6824c');
    addBox(-10, 6, SHIP_Z, 0.4, 0.4, 9, '#b6824c');
    addBox(-17, 4, SHIP_Z, 0.4, 0.4, 5, '#b6824c');

    // Square sails
    function addSail(x, yLow, yHigh, halfWidth) {
      for (let y = yLow; y <= yHigh; y++) {
        const mid = (yLow + yHigh) / 2;
        const span = Math.max(1, (yHigh - yLow) / 2);
        let w = halfWidth * (1 - Math.abs(y - mid) / span);
        if (w < 0.7) w = 0.7;

        addBox(x, y, SHIP_Z, 0.4, 1, w * 2, '#f1e8d2');
      }
    }

    addSail(-4, 4, 9, 2.2);
    addSail(-10, 5, 11, 3.2);

    // Small mizzen sail
    addBox(-17, 5.5, SHIP_Z, 0.35, 3, 3, '#efe5cd');

    // Rigging shrouds
    function addShroud(x, z, h) {
      for (let y = 2; y <= h; y++) {
        addBox(x, y, z, 0.09, 0.09, 0.09, '#c8b37a');
      }
    }

    addShroud(-4, SHIP_Z + 4.2, 8);
    addShroud(-4, SHIP_Z - 4.2, 8);
    addShroud(-10, SHIP_Z + 4.6, 11);
    addShroud(-10, SHIP_Z - 4.6, 11);
    addShroud(-17, SHIP_Z + 3.4, 6);
    addShroud(-17, SHIP_Z - 3.4, 6);

    // Cabin
    addBox(-14, 2.5, SHIP_Z, 3, 2, 3, '#ebd9bd');
    addBox(-14, 3.65, SHIP_Z, 3.4, 0.25, 3.2, '#c6915a');
    addBox(-14, 2.5, SHIP_Z - 1.55, 0.2, 1, 0.2, '#6b4a2e');
    addBox(-14, 2.6, SHIP_Z - 1.6, 0.8, 0.7, 0.08, '#35404b');
    addBox(-14, 2.6, SHIP_Z + 1.6, 0.8, 0.7, 0.08, '#35404b');

    // Forecastle
    addBox(-1, 1.9, SHIP_Z, 2, 1, 2, '#e8d7b6');

    // Deck hatches
    for (const x of [-16, -12, -8, -4]) {
      addBox(x, 1.55, SHIP_Z, 1.1, 0.1, 1.1, '#b58a55');
    }

    // Cargo on deck
    addBox(-10, 2.1, SHIP_Z - 1, 1.1, 1.1, 1.1, '#b97041');
    addBox(-10, 2.1, SHIP_Z + 1, 1.1, 1.1, 1.1, '#b97041');
    addBox(-10, 3.2, SHIP_Z, 1, 1, 1, '#c67f46');

    // Steering area
    addBox(-2, 1.65, SHIP_Z, 1.2, 0.2, 1.2, '#8c5f37');
    addBox(-2, 1.95, SHIP_Z, 0.2, 1, 0.2, '#73523a');

    // Bow and stern flags
    for (let y = 2; y <= 4; y++) {
      addBox(2, y, SHIP_Z + 1.2, 0.1, 0.1, 0.1, '#c8995f');
    }
    addBox(3, 3.8, SHIP_Z + 1.8, 1.6, 0.5, 0.1, '#d9423f');
    addBox(3, 3.4, SHIP_Z + 1.8, 1.6, 0.4, 0.1, '#264c82');

    for (let y = 2; y <= 5; y++) {
      addBox(-20, y, SHIP_Z, 0.1, 0.1, 0.1, '#c8995f');
    }
    addBox(-21, 4.5, SHIP_Z, 1.6, 0.9, 0.1, '#1f4287');

    // Signal flags between masts
    const pennantColors = [
      '#d8443f', '#2c6e9f', '#f1e9d3',
      '#337a45', '#e4a64a', '#2d6e9f'
    ];

    for (let i = 0; i < 8; i++) {
      const x = -10 + i * 1.1;
      const y = 11.4 - Math.abs(i - 4) * 0.28;
      const z = SHIP_Z + 0.6 + Math.sin(i) * 0.7;
      addBox(x, y, z, 0.45, 0.38, 0.08, pennantColors[i % pennantColors.length]);
    }

    // Seagulls
    const seagulls = [
      [2, 10, -3],
      [6, 11, 0],
      [12, 9, -6],
      [-14, 12, 10]
    ];

    for (const g of seagulls) {
      const gx = g[0];
      const gy = g[1];
      const gz = g[2];
      addBox(gx, gy, gz, 0.7, 0.12, 1.1, '#f3f2ee');
      addBox(gx, gy + 0.15, gz, 0.25, 0.25, 0.2, '#f3f2ee');
    }
  }

  buildScene();
  const numVertices = pos.length / 3;
  if (numVertices === 0) {
    fail('No scene data was generated.');
    return;
  }

  const vertexShader = `
    precision high float;
    attribute vec3 a_pos;
    attribute vec3 a_nor;
    attribute vec3 a_col;
    uniform mat4 u_mvp;
    uniform vec3 u_camPos;
    uniform vec3 u_fogColor;
    uniform float u_fogDensity;
    varying vec3 v_color;
    varying float v_fog;

    void main() {
      vec4 wp = vec4(a_pos, 1.0);
      gl_Position = u_mvp * wp;

      float d = length(wp.xyz - u_camPos);
      v_fog = clamp(exp(-d * u_fogDensity), 0.0, 1.0);

      vec3 n = normalize(a_nor);
      vec3 lightDir = normalize(vec3(0.27, 0.77, 0.31));
      float diff = max(dot(n, lightDir), 0.0);

      vec3 amb = vec3(0.28, 0.32, 0.38);
      v_color = a_col * (amb + vec3(0.73, 0.73, 0.71) * diff);
    }
  `;

  const fragmentShader = `
    precision mediump float;
    varying vec3 v_color;
    varying float v_fog;
    uniform vec3 u_fogColor;

    void main() {
      vec3 c = clamp(v_color, 0.0, 1.0);
      vec3 f = mix(c, u_fogColor, 1.0 - v_fog);
      gl_FragColor = vec4(clamp(f, 0.0, 1.0), 1.0);
    }
  `;

  function compileShader(type, source) {
    const shader = gl.createShader(type);
    if (!shader) return null;

    gl.shaderSource(shader, source);
    gl.compileShader(shader);

    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
      const log = gl.getShaderInfoLog(shader);
      fail('Shader compile failed: ' + log);
      gl.deleteShader(shader);
      return null;
    }

    return shader;
  }

  const vs = compileShader(gl.VERTEX_SHADER, vertexShader);
  const fs = compileShader(gl.FRAGMENT_SHADER, fragmentShader);
  if (!vs || !fs) return;

  const program = gl.createProgram();
  gl.attachShader(program, vs);
  gl.attachShader(program, fs);
  gl.linkProgram(program);

  if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
    const log = gl.getProgramInfoLog(program);
    fail('Program link failed: ' + log);
    return;
  }

  const aPos = gl.getAttribLocation(program, 'a_pos');
  const aNor = gl.getAttribLocation(program, 'a_nor');
  const aCol = gl.getAttribLocation(program, 'a_col');

  if (aPos < 0 || aNor < 0 || aCol < 0) {
    fail('Attributes are not available.');
    return;
  }

  const uMVP = gl.getUniformLocation(program, 'u_mvp');
  const uCamPos = gl.getUniformLocation(program, 'u_camPos');
  const uFogColor = gl.getUniformLocation(program, 'u_fogColor');
  const uFogDensity = gl.getUniformLocation(program, 'u_fogDensity');

  if (!uMVP || !uCamPos || !uFogColor || !uFogDensity) {
    fail('Uniforms are not available.');
    return;
  }

  function makeBuffer(arr) {
    const buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(arr), gl.STATIC_DRAW);
    return buf;
  }

  const posBuf = makeBuffer(pos);
  const nrmBuf = makeBuffer(nrm);
  const colBuf = makeBuffer(col);

  gl.enable(gl.DEPTH_TEST);
  gl.depthFunc(gl.LEQUAL);

  function resize() {
    const dpr = Math.min(2, window.devicePixelRatio || 1);
    const w = Math.max(1, Math.floor(window.innerWidth * dpr));
    const h = Math.max(1, Math.floor(window.innerHeight * dpr));

    if (canvas.width !== w || canvas.height !== h) {
      canvas.width = w;
      canvas.height = h;
    }

    gl.viewport(0, 0, canvas.width, canvas.height);
  }

  const clamp = (v, min, max) => Math.max(min, Math.min(max, v));

  const DEF = {
    yaw: 2.22,
    pitch: 0.27,
    dist: 47
  };

  const TARGET = [-6, 3, 3];
  let yaw = DEF.yaw;
  let pitch = DEF.pitch;
  let dist = DEF.dist;

  function resetView() {
    yaw = DEF.yaw;
    pitch = DEF.pitch;
    dist = DEF.dist;
    lastInteract = performance.now();
    canvas.style.cursor = 'grab';
  }

  function matMul(a, b) {
    const out = new Float32Array(16);

    for (let c = 0; c < 4; c++) {
      for (let r = 0; r < 4; r++) {
        let sum = 0;
        for (let k = 0; k < 4; k++) {
          sum += a[k * 4 + r] * b[c * 4 + k];
        }
        out[c * 4 + r] = sum;
      }
    }

    return out;
  }

  function perspective(fov, aspect, near, far) {
    const t = near * Math.tan(fov * 0.5);
    const r = t * aspect;

    return new Float32Array([
      near / r, 0, 0, 0,
      0, near / t, 0, 0,
      0, 0, -(far + near) / (far - near), -1,
      0, 0, -(2 * far * near) / (far - near), 0
    ]);
  }

  function normalize(v) {
    const l = Math.hypot(v[0], v[1], v[2]);
    if (l < 1e-8) return [0, 0, 0];
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

  function lookAt(eye, target, up) {
    let f = normalize([
      target[0] - eye[0],
      target[1] - eye[1],
      target[2] - eye[2]
    ]);

    let s = normalize(cross(f, up));
    if (Math.hypot(s[0], s[1], s[2]) < 1e-6) {
      s = normalize(cross(f, [1, 0, 0]));
    }

    const u = cross(s, f);

    return new Float32Array([
      s[0], u[0], -f[0], 0,
      s[1], u[1], -f[1], 0,
      s[2], u[2], -f[2], 0,
      -dot(s, eye),
      -dot(u, eye),
       dot(f, eye),
      1
    ]);
  }

  const fogColor = [0.87, 0.93, 0.97];

  function render() {
    resize();

    gl.clearColor(0.0, 0.0, 0.0, 0.0);
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

    const aspect = canvas.width / Math.max(1, canvas.height);
    const cp = Math.cos(pitch);
    const sp = Math.sin(pitch);

    const eye = [
      TARGET[0] + dist * cp * Math.sin(yaw),
      TARGET[1] + dist * sp,
      TARGET[2] + dist * cp * Math.cos(yaw)
    ];

    const mvp = matMul(
      perspective(0.75, aspect, 0.1, 400),
      lookAt(eye, TARGET, [0, 1, 0])
    );

    gl.useProgram(program);

    gl.bindBuffer(gl.ARRAY_BUFFER, posBuf);
    gl.vertexAttribPointer(aPos, 3, gl.FLOAT, false, 0, 0);

    gl.bindBuffer(gl.ARRAY_BUFFER, nrmBuf);
    gl.vertexAttribPointer(aNor, 3, gl.FLOAT, false, 0, 0);

    gl.bindBuffer(gl.ARRAY_BUFFER, colBuf);
    gl.vertexAttribPointer(aCol, 3, gl.FLOAT, false, 0, 0);

    gl.uniformMatrix4fv(uMVP, false, mvp);
    gl.uniform3fv(uCamPos, false, eye);
    gl.uniform3fv(uFogColor, false, fogColor);
    gl.uniform1f(uFogDensity, 0.013);

    gl.drawArrays(gl.TRIANGLES, 0, numVertices);
  }

  let lastInteract = performance.now();

  function animate(now) {
    if (now - lastInteract > 12000) {
      yaw += 0.00055;
    }
    render();
    requestAnimationFrame(animate);
  }

  requestAnimationFrame(animate);

  // Mouse / touch controls
  const pointers = new Map();
  let pinchDist = 0;

  function pointDistance() {
    const pts = Array.from(pointers.values());
    if (pts.length < 2) return 0;
    const dx = pts[0].x - pts[1].x;
    const dy = pts[0].y - pts[1].y;
    return Math.hypot(dx, dy);
  }

  function onPointerDown(e) {
    pointers.set(e.pointerId, {
      x: e.clientX,
      y: e.clientY
    });

    if (pointers.size === 2) {
      pinchDist = pointDistance();
    }

    lastInteract = performance.now();
    canvas.style.cursor = pointers.size === 1 ? 'grabbing' : 'grab';
  }

  function onPointerMove(e) {
    const p = pointers.get(e.pointerId);
    if (!p) return;

    lastInteract = performance.now();

    if (pointers.size === 1) {
      const dx = e.clientX - p.x;
      const dy = e.clientY - p.y;

      yaw += dx * 0.005;
      pitch = clamp(pitch + dy * -0.005, -0.12, 1.25);
    } else if (pointers.size === 2) {
      p.x = e.clientX;
      p.y = e.clientY;

      const d = pointDistance();
      if (pinchDist > 0 && d > 0) {
        dist *= Math.pow(pinchDist / d, 0.6);
        dist = clamp(dist, 16, 110);
      }
      pinchDist = d;
    }

    p.x = e.clientX;
    p.y = e.clientY;
  }

  function onPointerUp(e) {
    pointers.delete(e.pointerId);

    if (pointers.size === 1) {
      canvas.style.cursor = 'grabbing';
    } else {
      canvas.style.cursor = 'grab';
    }

    if (pointers.size < 2) pinchDist = 0;
    lastInteract = performance.now();
  }

  canvas.addEventListener('pointerdown', onPointerDown);
  canvas.addEventListener('pointermove', onPointerMove);
  canvas.addEventListener('pointerup', onPointerUp);
  canvas.addEventListener('dblclick', resetView);

  canvas.addEventListener('wheel', (e) => {
    dist *= Math.pow(1.1, e.deltaY * 0.01);
    dist = clamp(dist, 16, 110);
    lastInteract = performance.now();
  });

  window.addEventListener('resize', resize);
})();
</script>
</body>
</html>
```