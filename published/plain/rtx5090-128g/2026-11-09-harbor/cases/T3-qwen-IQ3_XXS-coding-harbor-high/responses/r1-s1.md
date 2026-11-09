```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Voxel Scene: Sailing Ship Calling at a Harbor</title>
<style>
  html, body {
    margin: 0;
    height: 100%;
    overflow: hidden;
    background: #87a9c6;
  }
  canvas {
    display: block;
    width: 100vw;
    height: 100vh;
    cursor: grab;
  }
  canvas:active {
    cursor: grabbing;
  }
  #ui {
    position: fixed;
    top: 12px;
    left: 12px;
    font-family: monospace;
    font-size: 14px;
    color: #fff;
    text-shadow: 0 1px 4px #000;
    pointer-events: none;
    background: rgba(0,0,0,0.22);
    padding: 8px 10px;
    border-radius: 6px;
  }
  #err {
    position: fixed;
    top: 12px;
    left: 12px;
    font-family: monospace;
    font-size: 16px;
    color: #fff;
    background: #701010;
    padding: 12px;
  }
</style>
</head>
<body>
<canvas id="c"></canvas>
<div id="ui">Drag: rotate &nbsp; Wheel/pinch: zoom &nbsp; Double-click: reset</div>

<script>
'use strict';

const canvas = document.getElementById('c');
const gl = canvas.getContext('webgl', { antialias: true, alpha: false }) ||
           canvas.getContext('experimental-webgl', { antialias: true, alpha: false });

if (!gl) {
  const err = document.createElement('div');
  err.id = 'err';
  err.textContent = 'WebGL is not available in this browser.';
  document.body.appendChild(err);
  throw new Error('WebGL unavailable');
}

/* ----------------------------------------------------------------------
   Tiny voxel engine / scene builder / renderer
   No external libraries are used.
----------------------------------------------------------------------- */

function rgb(r, g, b) {
  return [r / 255, g / 255, b / 255];
}

function clamp01(v) {
  return v < 0 ? 0 : v > 1 ? 1 : v;
}

function hashVal(x, y, z) {
  const s = Math.sin(x * 127.1 + y * 311.7 + z * 74.7) * 43758.5453;
  return s - Math.floor(s);
}

function vary(color, x, y, z, amt) {
  const shift = (hashVal(x, y, z) - 0.5) * amt;
  return [
    clamp01(color[0] + shift),
    clamp01(color[1] + shift),
    clamp01(color[2] + shift)
  ];
}

/* Palette */
const SEA1     = rgb( 42, 115, 170);
const SEA2     = rgb( 33,  94, 146);
const SEA3     = rgb( 24,  70, 112);
const FOAM     = rgb(222, 238, 244);
const STONE    = rgb(126, 122, 112);
const COBBLE   = rgb(153, 146, 128);
const GRASS    = rgb( 94, 142,  76);
const PIER     = rgb(160, 119,  74);
const PIER_DARK= rgb(108,  77,  48);
const HULL     = rgb(104,  70,  46);
const DECK     = rgb(165, 128,  81);
const SAIL     = rgb(240, 230, 208);
const MAST     = rgb( 78,  58,  44);
const FLAG     = rgb(222,  58,  48);
const WALL     = rgb(228, 212, 186);
const ROOF_RED = rgb(166,  71,  58);
const ROOF_BLUE= rgb( 70, 104, 154);
const TRUNK    = rgb( 86,  62,  43);
const LEAF1    = rgb( 63, 131,  77);
const LEAF2    = rgb( 93, 157,  88);
const LAMP     = rgb(255, 246, 188);
const CRATE    = rgb(195, 157, 102);
const BLACK    = rgb( 34,  34,  38);
const WINDOW   = rgb(128, 170, 218);
const CHIMNEY  = rgb( 90,  70,  60);
const WHITE    = rgb(242, 242, 246);
const FOG      = rgb(174, 203, 234);

/* Voxel storage */
const KEY_OFF = 300;
const KEY_S1 = 1048576;
const KEY_S2 = 4096;

function key(x, y, z) {
  return (x + KEY_OFF) * KEY_S1 + (y + KEY_OFF) * KEY_S2 + (z + KEY_OFF);
}

const voxMap = new Map();     // key -> index in voxels array
const voxels = [];

function setV(x, y, z, color) {
  const id = key(x, y, z);
  let idx = voxMap.get(id);
  if (idx === undefined) {
    idx = voxels.length;
    voxMap.set(id, idx);
    voxels.push({ x, y, z, c: color });
  } else {
    voxels[idx].c = color;
  }
}

function fillRect(x1, x2, y, z1, z2, color, jitter = 0) {
  for (let x = x1; x <= x2; x++) {
    for (let z = z1; z <= z2; z++) {
      setV(x, y, z, jitter ? vary(color, x, y, z, jitter) : color);
    }
  }
}

function fillBox(x1, x2, y1, y2, z1, z2, color, jitter = 0) {
  for (let y = y1; y <= y2; y++) {
    fillRect(x1, x2, y, z1, z2, color, jitter);
  }
}

/* ----------------------------------------------------------------------
   Build the harbor scene
----------------------------------------------------------------------- */

function buildSea() {
  const min = -38, max = 38;
  for (let x = min; x <= max; x++) {
    for (let z = min; z <= max; z++) {
      const h = hashVal(x, 0, z);
      let base = SEA1;
      if (h > 0.72) base = SEA2;
      if (h < 0.16) base = SEA1;
      if (Math.max(Math.abs(x), Math.abs(z)) > 34) base = SEA2;

      setV(x, 0, z, vary(base, x, 0, z, 0.13));
    }
  }
}

function buildFoam() {
  // Shore foam
  for (let z = -22; z <= 22; z++) {
    if (hashVal(17, 0, z) > 0.38) {
      setV(17, 0, z, vary(FOAM, 17, 0, z, 0.18));
    }
  }

  // Pier front foam
  for (let z = -14; z <= 14; z++) {
    if (hashVal(7, 0, z) > 0.52) {
      setV(7, 0, z, vary(FOAM, 7, 0, z, 0.18));
    }
  }

  // Pier end foam
  for (let x = 8; x <= 18; x++) {
    if (hashVal(x, 0, -15) > 0.55) setV(x, 0, -15, vary(FOAM, x, 0, -15, 0.18));
    if (hashVal(x, 0, 15)  > 0.55) setV(x, 0, 15,  vary(FOAM, x, 0, 15, 0.18));
  }

  // Gentle foam around the ship
  for (let z = -7; z <= 7; z++) {
    if (hashVal(1, 0, z) > 0.70) setV(1, 0, z, vary(FOAM, 1, 0, z, 0.18));
    if (hashVal(7, 0, z) > 0.70) setV(7, 0, z, vary(FOAM, 7, 0, z, 0.18));
  }
}

function buildLand() {
  for (let x = 19; x <= 36; x++) {
    for (let z = -22; z <= 22; z++) {
      setV(x, 1, z, vary(STONE, x, 1, z, 0.12));

      const surface = (x < 26 || Math.abs(z) < 16) ? COBBLE : GRASS;
      setV(x, 2, z, vary(surface, x, 2, z, 0.12));
    }
  }
}

function buildPier() {
  // Main pier
  for (let x = 8; x <= 18; x++) {
    for (let z = -14; z <= 14; z++) {
      setV(x, 1, z, vary(PIER_DARK, x, 1, z, 0.07));
      setV(x, 2, z, vary(PIER, x, 2, z, 0.12));
    }
  }

  // Darker trim
  for (let x = 8; x <= 18; x++) {
    setV(x, 2, -14, vary(PIER_DARK, x, 2, -14, 0.05));
    setV(x, 2,  14, vary(PIER_DARK, x, 2,  14, 0.05));
  }
  for (let z = -14; z <= 14; z++) {
    setV(8, 2, z, vary(PIER_DARK, 8, 2, z, 0.05));
  }

  // Gangplank to the ship
  for (let z = 4; z <= 6; z++) {
    setV(7, 1, z, vary(PIER_DARK, 7, 1, z, 0.05));
    setV(7, 2, z, vary(PIER, 7, 2, z, 0.08));
  }

  // Bollards
  for (const bz of [-12, -8, -4, 4, 8, 12]) {
    setV(8, 3, bz, BLACK);
  }

  // Small lamp posts
  for (const lz of [-13, 13]) {
    setV(10, 3, lz, MAST);
    setV(10, 4, lz, LAMP);
  }
}

function buildShip() {
  // Hull: stern at -7, bow at +7
  for (let z = -7; z <= 7; z++) {
    let x1 = 2, x2 = 6;

    if (z === 7) {
      x1 = 4; x2 = 5;       // pointed bow
    } else if (z === 6) {
      x1 = 3; x2 = 6;
    } else if (z === -7) {
      x1 = 3; x2 = 5;       // rounded stern
    } else if (z === -6) {
      x1 = 2; x2 = 6;
    }

    for (let x = x1; x <= x2; x++) {
      setV(x, 1, z, vary(HULL, x, 1, z, 0.10));
      setV(x, 2, z, vary(DECK, x, 2, z, 0.10));
    }
  }

  // Small stern cabin
  fillRect(3, 4, 3, -7, -5, WALL, 0.08);

  // Cargo crates on deck
  fillRect(3, 4, 3, 2, 4, CRATE, 0.08);
  fillRect(5, 5, 3, 2, 4, CRATE, 0.08);

  // Masts
  const masts = [-4, 0, 4];

  for (const mz of masts) {
    for (let y = 3; y <= 10; y++) {
      setV(4, y, mz, vary(MAST, 4, y, mz, 0.04));
    }
  }

  // Yards
  for (const mz of masts) {
    fillRect(2, 6, 7, mz, mz, MAST, 0.03);
  }

  // Square sails
  for (const mz of masts) {
    const z1 = mz - 2;
    const z2 = mz + 2;

    for (let x = 3; x <= 5; x++) {
      for (let z = z1; z <= z2; z++) {
        for (let y = 4; y <= 6; y++) {
          setV(x, y, z, vary(SAIL, x, y, z, 0.09));
        }
      }
    }
  }

  // Flag at foremast
  setV(4, 11, 4, MAST);
  setV(5, 11, 4, FLAG);
}

function addHouse(x1, x2, z1, z2, wall, roof) {
  // Walls
  fillRect(x1, x2, 3, z1, z2, wall, 0.08);
  fillRect(x1, x2, 4, z1, z2, wall, 0.06);

  // Roofs
  fillRect(x1, x2, 5, z1, z2, roof, 0.08);
  if (x1 + 1 <= x2 - 1 && z1 + 1 <= z2 - 1) {
    fillRect(x1 + 1, x2 - 1, 6, z1 + 1, z2 - 1, roof, 0.04);
  }

  // Chimney
  setV(x1 + 1, 5, z1, CHIMNEY);
  setV(x1 + 1, 6, z1, CHIMNEY);

  // Windows
  for (let x = x1 + 1; x <= x2 - 1; x += 2) {
    setV(x, 3, z1, WINDOW);
  }
  for (let z = z1 + 1; z <= z2 - 1; z += 2) {
    setV(x1, 3, z, WINDOW);
  }
}

function addTree(x, z) {
  for (let y = 3; y <= 5; y++) {
    setV(x, y, z, TRUNK);
  }
  fillRect(x - 1, x + 1, 6, z - 1, z + 1, LEAF1, 0.18);
  fillRect(x - 1, x + 1, 7, z - 1, z + 1, LEAF2, 0.18);
}

function buildLighthouse(x, z) {
  for (let y = 3; y <= 10; y++) {
    let color;
    if (y === 3) {
      color = STONE;
    } else if (y === 4 || y === 8) {
      color = ROOF_RED;
    } else {
      color = WHITE;
    }
    fillRect(x - 1, x + 1, y, z - 1, z + 1, color, 0.04);
  }

  // Lamp
  fillRect(x - 1, x + 1, 11, z - 1, z + 1, LAMP, 0.04);

  // Cap
  fillRect(x - 1, x + 1, 12, z - 1, z + 1, ROOF_RED, 0.04);
}

function buildTown() {
  // Warehouse near the pier
  fillRect(19, 22, 3, -8, -4, WALL, 0.08);
  fillRect(19, 22, 4, -8, -4, WALL, 0.06);
  fillRect(19, 22, 5, -8, -4, ROOF_BLUE, 0.06);

  // Houses
  addHouse(23, 26, -18, -14, WALL, ROOF_RED);
  addHouse(28, 31, -17, -13, WALL, ROOF_BLUE);
  addHouse(23, 26,  12,  16, WALL, ROOF_RED);
  addHouse(28, 31,  11,  15, WALL, ROOF_BLUE);
  addHouse(33, 36,  -2,   2, WALL, ROOF_RED);

  // Trees
  addTree(20, 18);
  addTree(20, -20);
  addTree(33, -18);

  // Lighthouse
  buildLighthouse(35, 16);
}

function buildDockCargo() {
  fillRect(10, 12, 3, -12, -10, CRATE, 0.09);
  fillRect(10, 11, 3,   8,  10, CRATE, 0.09);
  fillRect(14, 15, 3,  -6,  -5, CRATE, 0.09);
}

/* Build scene */
buildSea();
buildFoam();
buildLand();
buildPier();
buildShip();
buildTown();
buildDockCargo();

/* ----------------------------------------------------------------------
   Convert voxel map into WebGL triangles (only exposed faces)
----------------------------------------------------------------------- */

let vertexData = new Float32Array(2_000_000);
let vertexLen = 0;

function ensureCapacity(needed) {
  if (vertexLen + needed > vertexData.length) {
    let cap = vertexData.length || 1024;
    while (cap < vertexLen + needed) cap *= 2;
    const next = new Float32Array(cap);
    next.set(vertexData.subarray(0, vertexLen));
    vertexData = next;
  }
}

function pushV(x, y, z, r, g, b, nx, ny, nz) {
  vertexData[vertexLen++] = x;
  vertexData[vertexLen++] = y;
  vertexData[vertexLen++] = z;
  vertexData[vertexLen++] = r;
  vertexData[vertexLen++] = g;
  vertexData[vertexLen++] = b;
  vertexData[vertexLen++] = nx;
  vertexData[vertexLen++] = ny;
  vertexData[vertexLen++] = nz;
}

function addQuad(
  p1x, p1y, p1z,
  p2x, p2y, p2z,
  p3x, p3y, p3z,
  p4x, p4y, p4z,
  nx, ny, nz,
  r, g, b
) {
  ensureCapacity(54);

  pushV(p1x, p1y, p1z, r, g, b, nx, ny, nz);
  pushV(p2x, p2y, p2z, r, g, b, nx, ny, nz);
  pushV(p3x, p3y, p3z, r, g, b, nx, ny, nz);

  pushV(p1x, p1y, p1z, r, g, b, nx, ny, nz);
  pushV(p3x, p3y, p3z, r, g, b, nx, ny, nz);
  pushV(p4x, p4y, p4z, r, g, b, nx, ny, nz);
}

function addFace(name, x, y, z, col) {
  const r = col[0];
  const g = col[1];
  const b = col[2];
  const H = 0.5;

  if (name === '+X') {
    addQuad(
      x + H, y - H, z - H,
      x + H, y - H, z + H,
      x + H, y + H, z + H,
      x + H, y + H, z - H,
      1, 0, 0, r, g, b
    );
  } else if (name === '-X') {
    addQuad(
      x - H, y + H, z + H,
      x - H, y - H, z + H,
      x - H, y - H, z - H,
      x - H, y + H, z - H,
      -1, 0, 0, r, g, b
    );
  } else if (name === '+Y') {
    addQuad(
      x - H, y + H, z - H,
      x - H, y + H, z + H,
      x + H, y + H, z + H,
      x + H, y + H, z - H,
      0, 1, 0, r, g, b
    );
  } else if (name === '-Y') {
    addQuad(
      x - H, y - H, z + H,
      x + H, y - H, z + H,
      x + H, y - H, z - H,
      x - H, y - H, z - H,
      0, -1, 0, r, g, b
    );
  } else if (name === '+Z') {
    addQuad(
      x + H, y - H, z + H,
      x - H, y - H, z + H,
      x - H, y + H, z + H,
      x + H, y + H, z + H,
      0, 0, 1, r, g, b
    );
  } else if (name === '-Z') {
    addQuad(
      x - H, y - H, z - H,
      x + H, y - H, z - H,
      x + H, y + H, z - H,
      x - H, y + H, z - H,
      0, 0, -1, r, g, b
    );
  }
}

const DIRS = [
  [ 1,  0,  0, '+X'],
  [-1,  0,  0, '-X'],
  [ 0,  1,  0, '+Y'],
  [ 0, -1,  0, '-Y'],
  [ 0,  0,  1, '+Z'],
  [ 0,  0, -1, '-Z']
];

function buildFaces() {
  for (const v of voxels) {
    for (const [dx, dy, dz, name] of DIRS) {
      // Bottom faces are not needed because the camera never goes underwater.
      if (dy === -1) continue;

      if (voxMap.has(key(v.x + dx, v.y + dy, v.z + dz))) {
        continue;
      }

      addFace(name, v.x, v.y, v.z, v.c);
    }
  }

  // Free scene generation memory
  voxMap.clear();
  voxels.length = 0;
}

buildFaces();

/* Upload geometry */
const totalFloats = vertexLen;
const finalData = new Float32Array(totalFloats);
finalData.set(vertexData.subarray(0, totalFloats));
vertexData = null;

const vertexBuffer = gl.createBuffer();
gl.bindBuffer(gl.ARRAY_BUFFER, vertexBuffer);
gl.bufferData(gl.ARRAY_BUFFER, finalData, gl.STATIC_DRAW);
finalData = null;

const vertexCount = Math.floor(totalFloats / 9);

/* ----------------------------------------------------------------------
   Shaders / program
----------------------------------------------------------------------- */

function makeShader(type, source) {
  const shader = gl.createShader(type);
  gl.shaderSource(shader, source);
  gl.compileShader(shader);

  if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
    const log = gl.getShaderInfoLog(shader);
    gl.deleteShader(shader);
    throw new Error('Shader compile error: ' + log);
  }

  return shader;
}

function makeProgram(vsSource, fsSource) {
  const vs = makeShader(gl.VERTEX_SHADER, vsSource);
  const fs = makeShader(gl.FRAGMENT_SHADER, fsSource);

  const program = gl.createProgram();
  gl.attachShader(program, vs);
  gl.attachShader(program, fs);
  gl.linkProgram(program);

  if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
    throw new Error('Program link error: ' + gl.getProgramInfoLog(program));
  }

  return program;
}

const vsSource = `
attribute vec3 aPos;
attribute vec3 aColor;
attribute vec3 aNormal;

uniform mat4 uProj;
uniform mat4 uView;
uniform vec3 uLight;

varying vec3 vColor;
varying float vLight;
varying float vFog;

void main() {
  vec4 viewPos = uView * vec4(aPos, 1.0);
  gl_Position = uProj * viewPos;

  vec3 n = normalize(aNormal);
  float diff = max(0.0, dot(n, normalize(uLight)));

  vColor = aColor;
  vLight = 0.45 + 0.60 * diff;

  float d = length(viewPos.xyz);
  vFog = clamp((d - 120.0) / 140.0, 0.0, 1.0) * 0.42;
}
`;

const fsSource = `
precision mediump float;

varying vec3 vColor;
varying float vLight;
varying float vFog;

uniform vec3 uFogColor;

void main() {
  vec3 c = vColor * vLight;
  c = mix(c, uFogColor, vFog);
  gl_FragColor = vec4(c, 1.0);
}
`;

const program = makeProgram(vsSource, fsSource);
gl.useProgram(program);

const aPos    = gl.getAttribLocation(program, 'aPos');
const aColor  = gl.getAttribLocation(program, 'aColor');
const aNormal = gl.getAttribLocation(program, 'aNormal');

const uProj      = gl.getUniformLocation(program, 'uProj');
const uView      = gl.getUniformLocation(program, 'uView');
const uLight     = gl.getUniformLocation(program, 'uLight');
const uFogColor  = gl.getUniformLocation(program, 'uFogColor');

gl.enableVertexAttribArray(aPos);
gl.enableVertexAttribArray(aColor);
gl.enableVertexAttribArray(aNormal);

const stride = 9 * 4;
gl.vertexAttribPointer(aPos,    3, gl.FLOAT, false, stride, 0);
gl.vertexAttribPointer(aColor,  3, gl.FLOAT, false, stride, 12);
gl.vertexAttribPointer(aNormal, 3, gl.FLOAT, false, stride, 24);

gl.enable(gl.DEPTH_TEST);
gl.disable(gl.CULL_FACE);

/* ----------------------------------------------------------------------
   Camera controls
----------------------------------------------------------------------- */

const target = [14, 5, 0];

let azimuth = 3.06;
let elevation = 0.56;
let distance = 95;

let dragging = false;
let lastX = 0;
let lastY = 0;
let autoOrbit = true;

let lastTouch = null;
let lastPinch = 0;

function clampElevation() {
  if (elevation < 0.12) elevation = 0.12;
  if (elevation > 1.32) elevation = 1.32;
}

function clampDistance() {
  if (distance < 42) distance = 42;
  if (distance > 250) distance = 250;
}

function resetView() {
  azimuth = 3.06;
  elevation = 0.56;
  distance = 95;
  autoOrbit = false;
}

canvas.addEventListener('mousedown', e => {
  dragging = true;
  autoOrbit = false;
  lastX = e.clientX;
  lastY = e.clientY;
});

window.addEventListener('mouseup', () => {
  dragging = false;
});

window.addEventListener('mousemove', e => {
  if (!dragging) return;

  const dx = e.clientX - lastX;
  const dy = e.clientY - lastY;
  lastX = e.clientX;
  lastY = e.clientY;

  azimuth += dx * 0.0055;
  elevation -= dy * 0.0048;
  clampElevation();
});

canvas.addEventListener('wheel', e => {
  e.preventDefault();
  autoOrbit = false;
  distance *= Math.exp(e.deltaY * 0.0012);
  clampDistance();
}, { passive: false });

canvas.addEventListener('dblclick', () => {
  resetView();
});

canvas.addEventListener('contextmenu', e => e.preventDefault());

function touchDistance(e) {
  return Math.hypot(
    e.touches[0].clientX - e.touches[1].clientX,
    e.touches[0].clientY - e.touches[1].clientY
  );
}

canvas.addEventListener('touchstart', e => {
  e.preventDefault();
  dragging = true;
  autoOrbit = false;

  if (e.touches.length === 1) {
    lastTouch = {
      x: e.touches[0].clientX,
      y: e.touches[0].clientY
    };
    lastPinch = 0;
  } else if (e.touches.length >= 2) {
    lastTouch = null;
    lastPinch = touchDistance(e);
  }
}, { passive: false });

canvas.addEventListener('touchmove', e => {
  e.preventDefault();
  if (!dragging) return;

  if (e.touches.length === 1 && lastTouch) {
    const dx = e.touches[0].clientX - lastTouch.x;
    const dy = e.touches[0].clientY - lastTouch.y;
    lastTouch = {
      x: e.touches[0].clientX,
      y: e.touches[0].clientY
    };

    azimuth += dx * 0.0065;
    elevation -= dy * 0.0055;
    clampElevation();
  } else if (e.touches.length >= 2) {
    const d = touchDistance(e);
    if (lastPinch > 1 && d > 1) {
      distance *= lastPinch / d;
      clampDistance();
    }
    lastPinch = d;
  }
}, { passive: false });

canvas.addEventListener('touchend', e => {
  if (e.touches.length === 0) {
    dragging = false;
    lastTouch = null;
    lastPinch = 0;
  } else if (e.touches.length === 1) {
    lastTouch = {
      x: e.touches[0].clientX,
      y: e.touches[0].clientY
    };
    lastPinch = 0;
  }
});

canvas.addEventListener('touchcancel', () => {
  dragging = false;
  lastTouch = null;
  lastPinch = 0;
});

/* ----------------------------------------------------------------------
   Matrices
----------------------------------------------------------------------- */

function dot(a, b) {
  return a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
}

function cross(a, b) {
  return [
    a[1] * b[2] - a[2] * b[1],
    a[2] * b[0] - a[0] * b[2],
    a[0] * b[1] - a[1] * b[0]
  ];
}

function normalize(v) {
  const len = Math.hypot(v[0], v[1], v[2]);
  if (len < 1e-8) return [0, 1, 0];
  return [v[0] / len, v[1] / len, v[2] / len];
}

function createPerspective(fovy, aspect, near, far) {
  const f = 1.0 / Math.tan(fovy * 0.5);
  const nf = near - far;

  return [
    f / aspect, 0, 0, 0,
    0, f, 0, 0,
    0, 0, (far + near) / nf, -1,
    0, 0, (2 * far * near) / nf, 0
  ];
}

function createView(eye, target, up) {
  const z = normalize([
    eye[0] - target[0],
    eye[1] - target[1],
    eye[2] - target[2]
  ]);

  let x = cross(up, z);
  if (Math.hypot(x[0], x[1], x[2]) < 1e-6) {
    x = [1, 0, 0];
  } else {
    x = normalize(x);
  }

  const y = normalize(cross(z, x));

  const tx = -dot(x, eye);
  const ty = -dot(y, eye);
  const tz = -dot(z, eye);

  return [
    x[0], y[0], z[0], 0,
    x[1], y[1], z[1], 0,
    x[2], y[2], z[2], 0,
    tx, ty, tz, 1
  ];
}

/* ----------------------------------------------------------------------
   Resize / render loop
----------------------------------------------------------------------- */

let proj = null;

function resize() {
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  canvas.width = Math.floor(window.innerWidth * dpr);
  canvas.height = Math.floor(window.innerHeight * dpr);
  canvas.style.width = window.innerWidth + 'px';
  canvas.style.height = window.innerHeight + 'px';
  gl.viewport(0, 0, canvas.width, canvas.height);

  const aspect = canvas.width / Math.max(1, canvas.height);
  proj = createPerspective(Math.PI / 4.0, aspect, 1, 1000);
}

window.addEventListener('resize', resize);
resize();

gl.clearColor(FOG[0], FOG[1], FOG[2], 1);

function render() {
  if (autoOrbit) {
    azimuth += 0.0017;
  }

  const cosE = Math.cos(elevation);
  const sinE = Math.sin(elevation);

  const eye = [
    target[0] + distance * cosE * Math.cos(azimuth),
    target[1] + distance * sinE,
    target[2] + distance * cosE * Math.sin(azimuth)
  ];

  const view = createView(eye, target, [0, 1, 0]);

  // Camera-relative key light so the visible side of the voxel scene stays readable.
  const light = normalize([
    Math.cos(azimuth) * 0.58,
    0.82,
    Math.sin(azimuth) * 0.58
  ]);

  gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

  gl.uniformMatrix4fv(uProj, false, proj);
  gl.uniformMatrix4fv(uView, false, view);
  gl.uniform3fv(uLight, light);
  gl.uniform3fv(uFogColor, FOG);

  gl.drawArrays(gl.TRIANGLES, 0, vertexCount);

  requestAnimationFrame(render);
}

render();
</script>
</body>
</html>
```