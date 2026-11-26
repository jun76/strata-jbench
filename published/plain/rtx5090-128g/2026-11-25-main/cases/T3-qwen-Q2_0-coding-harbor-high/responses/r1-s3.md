Save the following as `harbor-voxel.html` and open it in Chrome. Drag with the mouse to rotate, scroll to zoom.

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Harbor Voxel Scene: Sailing Ship Calling at Harbor</title>
<style>
  html, body {
    height: 100%;
    margin: 0;
    overflow: hidden;
    background: #071423;
  }

  canvas {
    display: block;
    width: 100%;
    height: 100%;
  }

  .ui {
    position: fixed;
    left: 14px;
    top: 12px;
    color: #e8f4ff;
    font: 14px system-ui, sans-serif;
    background: rgba(10, 22, 38, 0.62);
    padding: 8px 10px;
    border-radius: 8px;
  }

  .ui button {
    margin-top: 6px;
    padding: 6px 9px;
    border: 0;
    border-radius: 6px;
    background: #225d88;
    color: white;
    font: inherit;
    cursor: pointer;
  }
</style>
</head>
<body>
  <canvas id="scene"></canvas>

  <div class="ui">
    Drag to rotate · Scroll to zoom
    <button id="reset">Reset view</button>
  </div>

<script>
/*
  A small self-contained voxel renderer.

  Scene:
  - Harbor water
  - Dock beside a sailing ship
  - Lighthouse on the left shore
  - Harbor buildings on the right shore
*/

const canvas = document.getElementById("scene");
const ctx = canvas.getContext("2d");

let width = 800;
let height = 600;
let dpr = 1;

let yaw = 0.72;
let pitch = 0.58;
let zoom = 0;

function resize() {
  dpr = Math.max(1, window.devicePixelRatio || 1);
  width = window.innerWidth;
  height = window.innerHeight;

  canvas.width = Math.floor(width * dpr);
  canvas.height = Math.floor(height * dpr);

  canvas.style.width = width + "px";
  canvas.style.height = height + "px";

  if (zoom <= 0) {
    zoom = Math.max(16, Math.min(32, Math.min(width, height) / 32));
  }
}

resize();
window.addEventListener("resize", resize);

const colors = {
  water: "#2771a2",
  waterLight: "#3389b8",
  dock: "#8c5b43",
  dockDark: "#63392b",
  land: "#6f9058",
  landDark: "#56713f",
  stone: "#9c8f7d",
  building: "#efdfc1",
  buildingDark: "#d7c5a9",
  roof: "#b85355",
  roofDark: "#8b3436",
  mast: "#a26c48",
  sail: "#f7f0e4",
  flag: "#d74545",
  hull: "#6a3b2f",
  hullDark: "#4b271f",
  deck: "#b57956",
  light: "#ffe38f"
};

const voxels = [];
const occupied = new Set();

function key(x, y, z) {
  return x + "," + y + "," + z;
}

function addVoxel(x, y, z, color, ship = false, water = false) {
  const k = key(x, y, z);
  if (occupied.has(k)) return;

  occupied.add(k);
  voxels.push({ x, y, z, color, ship, water });
}

function addBox(x0, x1, y0, y1, z0, z1, color, ship = false) {
  for (let x = x0; x <= x1; x++) {
    for (let y = y0; y <= y1; y++) {
      for (let z = z0; z <= z1; z++) {
        addVoxel(x, y, z, color, ship, false);
      }
    }
  }
}

function hexToRgb(hex) {
  const n = parseInt(hex.slice(1), 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}

/* ---------- Harbor scene ---------- */

// Dock pilings at water level.
for (let x = 7; x <= 22; x += 3) {
  addVoxel(x, 0, 0, colors.dockDark);
}

// Harbor water.
for (let x = -24; x <= 22; x++) {
  for (let y = -14; y <= 10; y++) {
    const color = ((x + y) & 1) ? colors.water : colors.waterLight;
    addVoxel(x, y, 0, color, false, true);
  }
}

// Dock surface, flush with the shore.
for (let x = 7; x <= 22; x++) {
  for (let y = -2; y <= 1; y++) {
    addVoxel(x, y, 1, colors.dock);
  }
}

// Right shore.
for (let x = 23; x <= 31; x++) {
  for (let y = -18; y <= 12; y++) {
    addVoxel(x, y, 1, colors.land);
  }
}

// Left shore / lighthouse ground.
for (let x = -32; x <= -25; x++) {
  for (let y = -10; y <= 8; y++) {
    addVoxel(x, y, 1, colors.land);
  }
}

// Back shore behind the harbor.
for (let x = -30; x <= 31; x++) {
  for (let y = -19; y <= -15; y++) {
    addVoxel(x, y, 1, colors.land);
  }
}

function addBuilding(x0, x1, y0, y1, h, body, roof) {
  for (let z = 2; z <= h; z++) {
    for (let x = x0; x <= x1; x++) {
      for (let y = y0; y <= y1; y++) {
        addVoxel(x, y, z, body);
      }
    }
  }

  for (let z = h + 1; z <= h + 3; z++) {
    const inset = z - h - 1;
    if (x0 + inset > x1 - inset) continue;
    if (y0 + inset > y1 - inset) continue;

    for (let x = x0 + inset; x <= x1 - inset; x++) {
      for (let y = y0 + inset; y <= y1 - inset; y++) {
        addVoxel(x, y, z, roof);
      }
    }
  }
}

// Harbor buildings.
addBuilding(24, 29, -12, -8, 5, colors.building, colors.roof);
addBuilding(30, 31, -1, 5, 4, colors.buildingDark, colors.roofDark);
addBuilding(24, 31, 7, 11, 3, colors.building, colors.roof);

// Lighthouse on the left shore.
addBox(-30, -27, -4, 2, 1, 4, colors.stone);
addBox(-29, -28, -2, 0, 5, 13, colors.building);
addBox(-29, -28, -1, 0, 14, 15, colors.roof);
addVoxel(-28, 0, 16, colors.light);

/* ---------- Sailing ship ---------- */

function addShip() {
  // Hull.
  for (let x = -7; x <= 6; x++) {
    for (let y = -2; y <= 2; y++) {
      if ((x === -7 || x === 6) && Math.abs(y) > 1) continue;

      addVoxel(x, y, 1, colors.hullDark, true);
      addVoxel(x, y, 2, colors.hull, true);
    }
  }

  // Deck.
  for (let x = -6; x <= 5; x++) {
    for (let y = -1; y <= 1; y++) {
      addVoxel(x, y, 3, colors.deck, true);
    }
  }

  // Cabin.
  for (let x = 2; x <= 4; x++) {
    for (let y = -1; y <= 1; y++) {
      addVoxel(x, y, 4, colors.hullDark, true);
    }
  }

  // Masts and sails.
  const masts = [-4, 0, 4];

  for (const m of masts) {
    addVoxel(m, 0, 4, colors.mast, true);

    // Sail panel.
    for (let z = 5; z <= 8; z++) {
      for (let y = -3; y <= 3; y++) {
        addVoxel(m, y, z, colors.sail, true);
      }
    }

    // Yard / mast top.
    for (let z = 9; z <= 12; z++) {
      addVoxel(m, 0, z, colors.mast, true);
    }

    for (let y = -3; y <= 3; y++) {
      addVoxel(m, y, 9, colors.mast, true);
    }
  }

  // Small stern flag.
  addVoxel(-5, 0, 11, colors.flag, true);
  addVoxel(-5, 0, 10, colors.flag, true);
  addVoxel(-5, 1, 11, colors.flag, true);
}

addShip();

/* ---------- Build visible voxel faces ---------- */

const faces = [];

function addFace(x, y, z, nx, ny, nz, color, ship = false, water = false) {
  const h = 0.5;
  let pts;

  if (nx === 1) {
    pts = [
      [x + h, y - h, z - h],
      [x + h, y + h, z - h],
      [x + h, y + h, z + h],
      [x + h, y - h, z + h]
    ];
  } else if (nx === -1) {
    pts = [
      [x - h, y + h, z - h],
      [x - h, y - h, z - h],
      [x - h, y - h, z + h],
      [x - h, y + h, z + h]
    ];
  } else if (ny === 1) {
    pts = [
      [x - h, y + h, z - h],
      [x + h, y + h, z - h],
      [x + h, y + h, z + h],
      [x - h, y + h, z + h]
    ];
  } else if (ny === -1) {
    pts = [
      [x + h, y - h, z - h],
      [x - h, y - h, z - h],
      [x - h, y - h, z + h],
      [x + h, y - h, z + h]
    ];
  } else if (nz === 1) {
    pts = [
      [x - h, y - h, z + h],
      [x + h, y - h, z + h],
      [x + h, y + h, z + h],
      [x - h, y + h, z + h]
    ];
  } else {
    pts = [
      [x - h, y + h, z - h],
      [x + h, y + h, z - h],
      [x + h, y - h, z - h],
      [x - h, y - h, z - h]
    ];
  }

  faces.push({
    v: pts,
    n: [nx, ny, nz],
    rgb: hexToRgb(color),
    water,
    bob: ship,
    pts: [],
    avg: 0
  });
}

const dirs = [
  [1, 0, 0],
  [-1, 0, 0],
  [0, 1, 0],
  [0, -1, 0],
  [0, 0, 1],
  [0, 0, -1]
];

function buildFaces() {
  for (const v of voxels) {
    for (const d of dirs) {
      const nx = v.x + d[0];
      const ny = v.y + d[1];
      const nz = v.z + d[2];

      if (!occupied.has(key(nx, ny, nz))) {
        addFace(v.x, v.y, v.z, d[0], d[1], d[2], v.color, v.ship, v.water);
      }
    }
  }
}

buildFaces();

/* ---------- Drawing ---------- */

function clamp(v, a, b) {
  return Math.max(a, Math.min(b, v));
}

function draw() {
  const time = performance.now() / 1000;
  const shipBob = Math.sin(time * 1.15) * 0.18;

  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

  const sky = ctx.createLinearGradient(0, 0, 0, height);
  sky.addColorStop(0, "#1b3553");
  sky.addColorStop(1, "#071424");
  ctx.fillStyle = sky;
  ctx.fillRect(0, 0, width, height);

  // Soft sun.
  ctx.fillStyle = "rgba(255, 225, 190, 0.22)";
  ctx.beginPath();
  ctx.arc(width * 0.78, height * 0.18, Math.max(25, Math.min(70, width * 0.08)), 0, Math.PI * 2);
  ctx.fill();

  const cosA = Math.cos(yaw);
  const sinA = Math.sin(yaw);
  const cosP = Math.cos(pitch);
  const sinP = Math.sin(pitch);

  const cx = width / 2;
  const cy = height / 2;

  const visible = [];
  const eps = 0.0001;

  for (const f of faces) {
    const nx = f.n[0];
    const ny = f.n[1];
    const nz = f.n[2];

    const nY = nx * sinA + ny * cosA;
    const nZ = nY * sinP + nz * cosP;

    if (nZ <= eps) continue;

    const zOff = f.bob ? shipBob : 0;
    let zSum = 0;

    for (let i = 0; i < 4; i++) {
      const vx = f.v[i][0];
      const vy = f.v[i][1];
      const vz = f.v[i][2] + zOff;

      const x2 = vx * cosA - vy * sinA;
      const y2 = vx * sinA + vy * cosA;
      const y3 = y2 * cosP - vz * sinP;
      const z3 = y2 * sinP + vz * cosP;

      f.pts[i] = [x2 * zoom + cx, -y3 * zoom + cy];
      zSum += z3;
    }

    f.avg = zSum / 4;
    visible.push(f);
  }

  visible.sort((a, b) => a.avg - b.avg);

  ctx.lineJoin = "round";
  ctx.lineWidth = 0.7;

  for (const f of visible) {
    const nx = f.n[0];
    const ny = f.n[1];
    const nz = f.n[2];

    const light = nx * 0.62 + ny * 0.50 + nz * 0.80;
    let factor = 0.72 + 0.30 * light;

    if (f.water) {
      factor += 0.10 * Math.sin((f.v[0][0] + f.v[0][1]) * 0.28 + time * 1.6);
    }

    factor = clamp(factor, 0.42, 1.18);

    const r = Math.round(f.rgb[0] * factor);
    const g = Math.round(f.rgb[1] * factor);
    const b = Math.round(f.rgb[2] * factor);

    ctx.fillStyle = "rgb(" + r + "," + g + "," + b + ")";
    ctx.strokeStyle = "rgba(18, 25, 34, 0.28)";

    ctx.beginPath();
    ctx.moveTo(f.pts[0][0], f.pts[0][1]);
    ctx.lineTo(f.pts[1][0], f.pts[1][1]);
    ctx.lineTo(f.pts[2][0], f.pts[2][1]);
    ctx.lineTo(f.pts[3][0], f.pts[3][1]);
    ctx.closePath();

    ctx.fill();
    ctx.stroke();
  }
}

/* ---------- Mouse controls ---------- */

let dragging = false;

canvas.addEventListener("pointerdown", () => {
  dragging = true;
});

canvas.addEventListener("pointermove", (e) => {
  if (!dragging) return;

  yaw += e.movementX * 0.0075;
  pitch -= e.movementY * 0.0075;

  pitch = clamp(pitch, 0.12, 1.32);
});

canvas.addEventListener("pointerup", () => {
  dragging = false;
});

canvas.addEventListener("wheel", (e) => {
  zoom *= (1 - e.deltaY * 0.0014);
  zoom = clamp(zoom, 12, 45);
  e.preventDefault();
});

document.getElementById("reset").addEventListener("click", () => {
  yaw = 0.72;
  pitch = 0.58;
  zoom = Math.max(16, Math.min(32, Math.min(width, height) / 32));
});

/* Start immediately. */
draw();
requestAnimationFrame(draw);
</script>
</body>
</html>
```