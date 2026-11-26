Save this as `harbor.html` and open it in Chrome. It is fully self-contained — no external libraries or files needed.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>Voxel Harbor: A Sailing Ship Calling at Harbor</title>
<style>
  html, body {
    height: 100%;
    margin: 0;
    background: #0b1728;
  }
  canvas {
    display: block;
    width: 100%;
    height: 100%;
    cursor: grab;
  }
  .ui {
    position: fixed;
    left: 12px;
    bottom: 12px;
    color: rgba(255,255,255,.85);
    background: rgba(0,0,0,.45);
    padding: 8px 10px;
    border-radius: 6px;
    font-family: Arial, sans-serif;
    font-size: 13px;
  }
</style>
</head>
<body>
<canvas id="scene"></canvas>
<div class="ui">Drag to rotate · Scroll to zoom</div>

<script>
const canvas = document.getElementById("scene");
const ctx = canvas.getContext("2d");

let yaw = 0.72;
let pitch = -0.70;
let dist = 86;
const target = { x: 2.0, y: 3.5, z: 0.0 };

const occ = new Set();
const voxels = [];

function key(x, y, z) {
  return x + "," + y + "," + z;
}

function add(x, y, z, r, g, b, tag = "static") {
  const k = key(x, y, z);
  if (occ.has(k)) return;
  occ.add(k);
  voxels.push({ x, y, z, r, g, b, tag });
}

function box(x0, x1, y0, y1, z0, z1, r, g, b, tag = "static") {
  for (let x = x0; x <= x1; x++) {
    for (let y = y0; y <= y1; y++) {
      for (let z = z0; z <= z1; z++) {
        add(x, y, z, r, g, b, tag);
      }
    }
  }
}

/* ---------------------------------------------------------------- */
/* Scene construction                                                */
/* ---------------------------------------------------------------- */

// Water surface
for (let x = -16; x <= 16; x++) {
  for (let z = -16; z <= 16; z++) {
    const p = (((x * 3 + z * 5) % 4) + 4) % 4;
    add(x, 0, z, 46 + p * 8, 105 + p * 12, 165 + p * 12, "water");
  }
}

// Dock
for (let z = -10; z <= 10; z++) {
  for (let x = 4; x <= 6; x++) {
    add(x, 1, z, 190, 140, 85, "dock");
  }
}

// Dock bollards
for (let z = -8; z <= 8; z += 4) {
  add(4, 2, z, 60, 60, 60, "dock");
}

// Crates on dock
box(4, 6, 2, 3, -1, 2, 220, 180, 115, "dock");

// Land behind dock
box(7, 17, 1, 1, -12, 12, 198, 160, 112, "land");

// Harbor buildings
box(8, 12, 2, 5, -8, -4, 215, 195, 175, "building");
box(8, 12, 6, 6, -8, -4, 125, 85, 65, "building");

box(8, 10, 2, 4, 1, 3, 220, 155, 120, "building");
box(8, 10, 5, 5, 1, 3, 110, 70, 50, "building");

box(13, 15, 2, 4, -9, -7, 175, 205, 185, "building");
box(13, 15, 5, 5, -9, -7, 85, 130, 105, "building");

// Lighthouse
for (let y = 2; y <= 8; y++) {
  const c = (y % 2 === 0) ? [245, 245, 245] : [215, 70, 55];
  for (let x = 15; x <= 16; x++) {
    for (let z = 7; z <= 8; z++) {
      add(x, y, z, c[0], c[1], c[2], "building");
    }
  }
}
add(15, 9, 7, 255, 220, 95, "light");
add(16, 9, 7, 255, 220, 95, "light");
add(15, 9, 8, 255, 220, 95, "light");
add(16, 9, 8, 255, 220, 95, "light");

// Trees
function tree(x, z) {
  for (let y = 2; y <= 4; y++) {
    add(x, y, z, 120, 80, 50, "tree");
  }
  for (let y = 4; y <= 6; y++) {
    for (let dx = -1; dx <= 1; dx++) {
      for (let dz = -1; dz <= 1; dz++) {
        add(x + dx, y, z + dz, 75, 170, 90, "tree");
      }
    }
  }
}
tree(12, 5);
tree(14, -10);
tree(16, -4);

// Birds
add(-7, 10, -6, 255, 255, 255, "bird");
add(-6, 10, -4, 255, 255, 255, "bird");
add(-5, 10, -2, 255, 255, 255, "bird");

// Mooring line between dock and ship
for (let z = -4; z <= 4; z++) {
  add(3, 2, z, 100, 100, 100, "dock");
}

// Dock lanterns
for (let z = -7; z <= 7; z += 4) {
  for (let y = 2; y <= 4; y++) {
    add(4, y, z, 70, 70, 70, "dock");
  }
  add(4, 4, z, 255, 190, 90, "light");
}

/* ---------------------------------------------------------------- */
/* Sailing ship                                                      */
/* ---------------------------------------------------------------- */

const hullRows = [
  [-8, -2, -1],
  [-7, -3,  1],
  [-6, -3,  2],
  [-5, -3,  2],
  [-4, -3,  2],
  [-3, -3,  2],
  [-2, -3,  2],
  [-1, -3,  2],
  [ 0, -3,  2],
  [ 1, -3,  2],
  [ 2, -3,  2],
  [ 3, -3,  2],
  [ 4, -3,  2],
  [ 5, -2,  1],
  [ 6, -1,  0],
  [ 7, -1, -1]
];

for (const [z, x0, x1] of hullRows) {
  // Hull
  for (let y = 1; y <= 2; y++) {
    const c = (y === 1) ? [150, 85, 45] : [220, 190, 170];
    for (let x = x0; x <= x1; x++) {
      add(x, y, z, c[0], c[1], c[2], "ship");
    }
  }

  // Deck
  for (let x = x0; x <= x1; x++) {
    add(x, 3, z, 235, 225, 210, "ship");
  }
}

// Cabin
for (let x = -2; x <= 0; x++) {
  for (let z = -6; z <= -4; z++) {
    add(x, 4, z, 240, 210, 200, "ship");
    add(x, 5, z, 190, 115, 85, "ship");
  }
}

// Masts
for (let mz of [-5, 0, 5]) {
  for (let y = 3; y <= 9; y++) {
    add(-1, y, mz, 135, 90, 60, "ship");
  }
}

// Sails
for (let mz of [-5, 0, 5]) {
  for (let y = 4; y <= 8; y++) {
    const dz = 4 - (y - 4);
    for (let z = mz - dz; z <= mz + dz; z++) {
      for (let x = -2; x <= 0; x++) {
        add(x, y, z, 246, 236, 220, "sail");
      }
    }
  }
}

// Flag
for (let y = 6; y <= 8; y++) {
  add(-1, y, -7, 90, 70, 50, "ship");
}
add(0, 8, -8, 230, 40, 40, "ship");

/* ---------------------------------------------------------------- */
/* Build visible voxel faces                                         */
/* ---------------------------------------------------------------- */

const faceDefs = [
  { n: [1,0,0], shade: 0.78, verts: [[0.5,-0.5,-0.5],[0.5,-0.5,0.5],[0.5,0.5,0.5],[0.5,0.5,-0.5]] },
  { n: [-1,0,0], shade: 0.58, verts: [[-0.5,-0.5,0.5],[-0.5,-0.5,-0.5],[-0.5,0.5,-0.5],[-0.5,0.5,0.5]] },
  { n: [0,1,0], shade: 1.05, verts: [[-0.5,0.5,-0.5],[0.5,0.5,-0.5],[0.5,0.5,0.5],[-0.5,0.5,0.5]] },
  { n: [0,-1,0], shade: 0.30, verts: [[-0.5,-0.5,0.5],[0.5,-0.5,0.5],[0.5,-0.5,-0.5],[-0.5,-0.5,-0.5]] },
  { n: [0,0,1], shade: 0.72, verts: [[-0.5,-0.5,0.5],[0.5,-0.5,0.5],[0.5,0.5,0.5],[-0.5,0.5,0.5]] },
  { n: [0,0,-1], shade: 0.60, verts: [[-0.5,-0.5,-0.5],[-0.5,0.5,-0.5],[0.5,0.5,-0.5],[0.5,-0.5,-0.5]] }
];

const faces = [];

for (const v of voxels) {
  for (let i = 0; i < faceDefs.length; i++) {
    // Skip the underside of open water so the ocean does not look hollow.
    if (i === 3 && v.tag === "water") continue;

    const nx = faceDefs[i].n[0];
    const ny = faceDefs[i].n[1];
    const nz = faceDefs[i].n[2];

    // Hide interior faces where an adjacent voxel exists.
    if (occ.has(key(v.x + nx, v.y + ny, v.z + nz))) continue;

    faces.push({
      center: [v.x + nx * 0.5, v.y + ny * 0.5, v.z + nz * 0.5],
      normal: faceDefs[i].n,
      shade: faceDefs[i].shade,
      verts: faceDefs[i].verts.map(p => [v.x + p[0], v.y + p[1], v.z + p[2]]),
      r: v.r,
      g: v.g,
      b: v.b,
      tag: v.tag,
      wx: v.x,
      wz: v.z
    });
  }
}

/* ---------------------------------------------------------------- */
/* Rendering and interaction                                         */
/* ---------------------------------------------------------------- */

function resize() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
}
resize();
window.addEventListener("resize", resize);

let dragging = false;
let lastX = 0;
let lastY = 0;

canvas.addEventListener("pointerdown", e => {
  dragging = true;
  lastX = e.clientX;
  lastY = e.clientY;
  canvas.style.cursor = "grabbing";
});

canvas.addEventListener("pointermove", e => {
  if (!dragging) return;

  yaw += (e.clientX - lastX) * 0.006;
  pitch -= (e.clientY - lastY) * 0.004;
  pitch = Math.max(-1.3, Math.min(1.0, pitch));

  lastX = e.clientX;
  lastY = e.clientY;
});

canvas.addEventListener("pointerup", () => {
  dragging = false;
  canvas.style.cursor = "grab";
});

canvas.addEventListener("wheel", e => {
  e.preventDefault();
  dist *= (e.deltaY > 0 ? 1.08 : 0.92);
  dist = Math.max(45, Math.min(210, dist));
}, { passive: false });

function render(time) {
  const W = canvas.width;
  const H = canvas.height;
  const focal = Math.max(380, Math.min(1700, H * 1.2));

  // Background gradient
  const grad = ctx.createLinearGradient(0, 0, 0, H);
  grad.addColorStop(0, "#224e78");
  grad.addColorStop(0.38, "#5f8997");
  grad.addColorStop(0.60, "#244157");
  grad.addColorStop(1, "#0a1220");
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, W, H);

  const t = time * 0.001;
  const shipMove = Math.sin(t * 1.4) * 0.08;
  const shipBob = Math.sin(t * 1.8) * 0.22;
  const lightPulse = 0.85 + 0.5 * Math.sin(t * 4.2);

  const cY = Math.cos(yaw);
  const sY = Math.sin(yaw);
  const cP = Math.cos(pitch);
  const sP = Math.sin(pitch);

  const draw = [];

  for (const f of faces) {
    let dx = 0;
    let dy = 0;

    if (f.tag === "ship" || f.tag === "sail") {
      dx = shipMove;
      dy = shipBob;
    }

    // Transform face center
    let x = f.center[0] - target.x + dx;
    let y = f.center[1] - target.y + dy;
    let z = f.center[2] - target.z;

    let x1 = x * cY - z * sY;
    let z1 = x * sY + z * cY;
    let y1 = y * cP - z1 * sP;
    let z2 = y * sP + z1 * cP;
    let pz = z2 + dist;

    if (pz <= 1) continue;

    // Transform normal
    const n = f.normal;
    let nx = n[0];
    let ny = n[1];
    let nz = n[2];

    let nx1 = nx * cY - nz * sY;
    let nz1 = nx * sY + nz * cY;
    let ny1 = ny * cP - nz1 * sP;
    let nz2 = ny * sP + nz1 * cP;

    // Backface culling
    if (nx1 * x1 + ny1 * y1 + nz2 * pz >= 0) continue;

    // Transform vertices
    const pts = [];
    let ok = true;

    for (const v of f.verts) {
      x = v[0] - target.x + dx;
      y = v[1] - target.y + dy;
      z = v[2] - target.z;

      x1 = x * cY - z * sY;
      z1 = x * sY + z * cY;
      y1 = y * cP - z1 * sP;
      z2 = y * sP + z1 * cP;
      pz = z2 + dist;

      if (pz <= 1) {
        ok = false;
        break;
      }

      const sx = W / 2 + x1 * focal / pz;
      const sy = H / 2 - y1 * focal / pz;
      pts.push([sx, sy]);
    }

    if (!ok) continue;

    // Shading
    let shade = f.shade;

    if (f.tag === "water") {
      shade += 0.14 * Math.sin(t * 2.1 + f.wx * 0.25 + f.wz * 0.22);
    }

    if (f.tag === "light") {
      shade *= lightPulse;
    }

    shade = Math.max(0, Math.min(1.3, shade));

    const r = Math.min(255, Math.round(f.r * shade));
    const g = Math.min(255, Math.round(f.g * shade));
    const b = Math.min(255, Math.round(f.b * shade));

    draw.push({
      z: pz,
      pts,
      color: "rgb(" + r + "," + g + "," + b + ")"
    });
  }

  // Painter's algorithm: far faces first
  draw.sort((a, b) => b.z - a.z);

  ctx.lineWidth = 1;
  ctx.lineJoin = "round";

  for (const d of draw) {
    ctx.fillStyle = d.color;
    ctx.strokeStyle = d.color;

    ctx.beginPath();
    ctx.moveTo(d.pts[0][0], d.pts[0][1]);

    for (let i = 1; i < d.pts.length; i++) {
      ctx.lineTo(d.pts[i][0], d.pts[i][1]);
    }

    ctx.closePath();
    ctx.fill();
    ctx.stroke();
  }
}

function animate() {
  render(Date.now());
  requestAnimationFrame(animate);
}

animate();
</script>
</body>
</html>
```