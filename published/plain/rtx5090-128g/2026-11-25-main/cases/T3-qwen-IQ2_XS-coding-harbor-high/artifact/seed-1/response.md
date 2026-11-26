Save this as a single `.html` file and open it in Chrome. It uses only built-in HTML/JavaScript, no external libraries, and renders immediately. Drag to rotate, scroll to zoom.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Voxel Harbor</title>
<style>
  html, body {
    margin: 0;
    height: 100%;
    overflow: hidden;
    background: #76c2eb;
    font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
  }

  canvas {
    display: block;
    width: 100vw;
    height: 100vh;
    cursor: grab;
  }

  #hud {
    position: fixed;
    left: 12px;
    top: 12px;
    padding: 8px 11px;
    background: rgba(255, 255, 255, 0.78);
    border-radius: 10px;
    font-size: 13px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.14);
    pointer-events: none;
  }

  #hud b {
    color: #2d4a5b;
  }
</style>
</head>
<body>
  <div id="hud"><b>Sailing ship at harbor</b> — drag to orbit, scroll to zoom</div>
  <canvas id="c"></canvas>

  <script>
    const canvas = document.getElementById("c");
    const ctx = canvas.getContext("2d");
    const DPR = Math.min(window.devicePixelRatio || 1, 2);

    let W = 0;
    let H = 0;
    let needsDraw = true;

    function resize() {
      W = window.innerWidth;
      H = window.innerHeight;
      canvas.width = W * DPR;
      canvas.height = H * DPR;
      ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
      ctx.imageSmoothingEnabled = false;
    }

    resize();
    window.addEventListener("resize", () => {
      resize();
      needsDraw = true;
    });

    const blocks = new Map();

    function parseHex(hex) {
      const s = hex.replace("#", "");
      return [
        parseInt(s.slice(0, 2), 16),
        parseInt(s.slice(2, 4), 16),
        parseInt(s.slice(4, 6), 16)
      ];
    }

    function addBlock(x, y, z, hex) {
      const c = parseHex(hex);
      const key = `${x},${y},${z}`;
      const existing = blocks.get(key);

      if (existing) {
        existing.c = c;
      } else {
        blocks.set(key, { x, y, z, c });
      }
    }

    function clampColor(v) {
      return Math.max(0, Math.min(255, Math.round(v)));
    }

    function dot(a, b) {
      return a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
    }

    function normalize(v) {
      const len = Math.hypot(v[0], v[1], v[2]);
      return [v[0] / len, v[1] / len, v[2] / len];
    }

    const corners = [
      [-0.5, -0.5, -0.5],
      [ 0.5, -0.5, -0.5],
      [ 0.5, -0.5,  0.5],
      [-0.5, -0.5,  0.5],
      [-0.5,  0.5, -0.5],
      [ 0.5,  0.5, -0.5],
      [ 0.5,  0.5,  0.5],
      [-0.5,  0.5,  0.5]
    ];

    const faceDefs = [
      { v: [0, 3, 2, 1], n: [ 0, -1,  0] }, // bottom
      { v: [4, 5, 6, 7], n: [ 0,  1,  0] }, // top
      { v: [0, 1, 5, 4], n: [ 0,  0, -1] }, // front
      { v: [3, 7, 6, 2], n: [ 0,  0,  1] }, // back
      { v: [1, 2, 6, 5], n: [ 1,  0,  0] }, // right
      { v: [0, 4, 7, 3], n: [-1,  0,  0] }  // left
    ];

    const light = normalize([0.45, 0.62, 0.40]);
    const faceShade = faceDefs.map(def => {
      return 0.35 + Math.max(0, dot(def.n, light)) * 0.62;
    });

    const target = { x: 0, y: 3.5, z: 1 };

    let yaw = -0.65;
    let pitch = 0.55;
    let camDist = 42;

    let V = [0, 0, 1];
    let U = [0, 1, 0];
    let R = [1, 0, 0];
    let focal = 300;

    function updateAxes() {
      const sy = Math.sin(yaw);
      const cy = Math.cos(yaw);
      const sp = Math.sin(pitch);
      const cp = Math.cos(pitch);

      R = [cy, 0, sy];
      U = [-sp * sy, cp, sp * cy];
      V = [-cp * sy, -sp, cp * cy];

      focal = Math.min(W, H) * 0.68;
    }

    function projectRelative(x, y, z) {
      const d = camDist + x * V[0] + y * V[1] + z * V[2];

      if (d < 1) return null;

      const sx = W / 2 + (x * R[0] + y * R[1] + z * R[2]) * focal / d;
      const sy = H / 2 - (x * U[0] + y * U[1] + z * U[2]) * focal / d;

      return { x: sx, y: sy, d };
    }

    function draw() {
      ctx.clearRect(0, 0, W, H);

      const gradient = ctx.createLinearGradient(0, 0, 0, H);
      gradient.addColorStop(0, "#84c6f0");
      gradient.addColorStop(0.65, "#c3dfed");
      gradient.addColorStop(1, "#d2e0d4");
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, W, H);

      const sunRadius = Math.min(W, H) * 0.075;
      ctx.fillStyle = "rgba(255, 233, 166, 0.72)";
      ctx.beginPath();
      ctx.arc(W * 0.76, H * 0.24, sunRadius, 0, Math.PI * 2);
      ctx.fill();

      updateAxes();

      const faces = [];

      for (const block of blocks.values()) {
        const cx = block.x + 0.5 - target.x;
        const cy = block.y + 0.5 - target.y;
        const cz = block.z + 0.5 - target.z;

        for (let i = 0; i < faceDefs.length; i++) {
          const def = faceDefs[i];

          // Backface culling: only draw faces pointing toward the camera.
          if (dot(def.n, V) >= -0.001) continue;

          const pts = [];
          let depthSum = 0;
          let ok = true;

          for (const idx of def.v) {
            const c = corners[idx];
            const p = projectRelative(cx + c[0], cy + c[1], cz + c[2]);

            if (!p) {
              ok = false;
              break;
            }

            pts.push({ x: p.x, y: p.y });
            depthSum += p.d;
          }

          if (!ok) continue;

          const shade = faceShade[i];

          const cr = clampColor(block.c[0] * shade);
          const cg = clampColor(block.c[1] * shade);
          const cb = clampColor(block.c[2] * shade);

          faces.push({
            depth: depthSum / 4,
            points: pts,
            fill: `rgb(${cr}, ${cg}, ${cb})`
          });
        }
      }

      faces.sort((a, b) => b.depth - a.depth);

      ctx.lineWidth = 1;
      ctx.strokeStyle = "rgba(14, 26, 38, 0.25)";

      for (const f of faces) {
        ctx.beginPath();
        ctx.moveTo(f.points[0].x, f.points[0].y);

        for (let i = 1; i < f.points.length; i++) {
          ctx.lineTo(f.points[i].x, f.points[i].y);
        }

        ctx.closePath();
        ctx.fillStyle = f.fill;
        ctx.fill();
        ctx.stroke();
      }
    }

    function addBox(x0, z0, w, d, h, wall, roof) {
      for (let x = x0; x < x0 + w; x++) {
        for (let z = z0; z < z0 + d; z++) {
          for (let y = 1; y <= h; y++) {
            addBlock(x, y, z, y === h ? roof : wall);
          }
        }
      }
    }

    function tree(x, z) {
      addBlock(x, 1, z, "#5b4431");

      for (let y = 2; y <= 3; y++) {
        addBlock(x, y, z, "#4f7f48");
      }

      addBlock(x + 1, 2, z, "#416844");
      addBlock(x - 1, 2, z, "#598450");
      addBlock(x, 2, z + 1, "#3c643d");
      addBlock(x, 2, z - 1, "#4d7a47");
      addBlock(x, 3, z, "#5d8d55");
    }

    function smallBoat(x, z) {
      for (let zz = z; zz <= z + 1; zz++) {
        addBlock(x, 1, zz, "#6d4f35");
      }

      addBlock(x, 2, z, "#48372e");
      addBlock(x, 3, z, "#d2d2c3");
    }

    function lighthouse(x, z) {
      const white = "#efe7d0";
      const red = "#c4433d";
      const dark = "#2f353c";

      for (let y = 1; y <= 6; y++) {
        addBlock(x, y, z, y % 2 === 1 ? white : red);
      }

      addBlock(x, 7, z, dark);
      addBlock(x, 8, z, "#313943");
      addBlock(x, 9, z, "#f4c661");
      addBlock(x, 10, z, red);
    }

    function addShip(sx = -1, sz = -3) {
      const HULL = "#744f34";
      const DECK = "#9b7247";
      const SAIL = "#e6e3cf";
      const MAST = "#443d31";
      const FLAG = "#d24543";
      const GOLD = "#c29040";

      function halfAt(z) {
        if (z <= sz - 3) return 1;
        if (z >= sz + 4) return 1;
        return 2;
      }

      for (let z = sz - 3; z <= sz + 4; z++) {
        const w = halfAt(z);

        for (let x = sx - w; x <= sx + w; x++) {
          for (let y = 1; y <= 3; y++) {
            addBlock(x, y, z, HULL);
          }
        }
      }

      for (let z = sz - 2; z <= sz + 4; z++) {
        for (let x = sx - 1; x <= sx + 1; x++) {
          addBlock(x, 3, z, DECK);
        }
      }

      for (let z = sz - 2; z <= sz + 4; z++) {
        addBlock(sx, 2, z, GOLD);
      }

      // Bow and bowsprit.
      addBlock(sx, 3, sz - 3, DECK);
      addBlock(sx, 4, sz - 3, MAST);
      addBlock(sx, 3, sz - 4, MAST);

      // Stern cabin.
      for (let x = sx - 1; x <= sx + 1; x++) {
        addBlock(x, 4, sz + 4, "#8b5437");
      }

      addBlock(sx, 5, sz + 4, FLAG);
      addBlock(sx, 4, sz + 3, "#333c45");

      // Cargo and barrels.
      addBlock(sx + 1, 3, sz - 1, "#7c613c");
      addBlock(sx - 1, 3, sz, "#6b5437");
      addBlock(sx + 1, 3, sz - 2, "#8a6f42");

      for (let x = sx - 1; x <= sx + 1; x++) {
        addBlock(x, 3, sz + 1, "#6a4a31");
      }

      function mast(z, h) {
        for (let y = 4; y <= h; y++) {
          addBlock(sx, y, z, MAST);
        }

        for (let y = 5; y <= h - 2; y++) {
          for (let x = sx - 1; x <= sx + 1; x++) {
            addBlock(x, y, z, SAIL);
          }
        }

        for (let x = sx - 1; x <= sx + 1; x++) {
          addBlock(x, h - 1, z, MAST);
        }

        addBlock(sx, h + 1, z, FLAG);
      }

      mast(sz - 1, 8);
      mast(sz + 1, 9);
      mast(sz + 3, 7);

      // Simple rigging hints.
      for (let z = sz - 1; z <= sz + 3; z += 2) {
        addBlock(sx + 1, 4, z, MAST);
        addBlock(sx - 1, 4, z, MAST);
      }
    }

    function buildScene() {
      const water = "#1c6687";
      const waterDark = "#18546b";
      const waterLight = "#2a7b93";

      for (let x = -7; x <= 7; x++) {
        for (let z = -7; z <= 4; z++) {
          const h = ((x + z) % 7 + 7) % 7;
          const c = h === 0 ? waterDark : h === 3 ? waterLight : water;
          addBlock(x, 0, z, c);
        }

        for (let z = 5; z <= 10; z++) {
          addBlock(x, 0, z, z === 5 ? "#d2ba88" : "#437d58");
        }
      }

      // Quay wall.
      for (let x = -7; x <= 7; x++) {
        addBlock(x, 1, 5, "#727272");
      }

      // Dock.
      for (let z = 0; z <= 4; z++) {
        addBlock(3, 1, z, "#875731");
        addBlock(2, 0, z, "#563923");
        addBlock(4, 0, z, "#563923");
      }

      for (let z = 1; z <= 4; z++) {
        addBlock(3, 2, z, "#303030");
      }

      // Small rowboat.
      smallBoat(4, 1);

      // Path.
      for (let x = -4; x <= 4; x++) {
        addBlock(x, 0, 6, "#a79172");
      }

      for (let x = -2; x <= 2; x++) {
        addBlock(x, 0, 7, "#a08a6c");
      }

      // Buildings.
      addBox(-5, 6, 3, 3, 4, "#c05b54", "#534743");
      addBlock(-4, 2, 6, "#343f49");
      addBlock(-3, 2, 6, "#343f49");
      addBlock(-5, 2, 7, "#343f49");
      addBlock(-3, 1, 6, "#4f3b31");

      addBox(3, 7, 3, 3, 3, "#a3876a", "#57443b");
      addBlock(4, 2, 7, "#344350");
      addBlock(3, 2, 8, "#344350");
      addBlock(5, 2, 7, "#344350");

      addBox(-1, 9, 2, 2, 2, "#786555", "#3b433b");
      addBlock(-1, 1, 9, "#354149");

      addBox(1, 7, 1, 1, 1, "#657365", "#536358");

      // Trees.
      tree(-6, 7);
      tree(-3, 9);
      tree(2, 9);
      tree(1, 6);
      tree(6, 10);

      // Lighthouse.
      lighthouse(6, 9);

      // Quay lamps.
      for (let x = -6; x <= 6; x += 4) {
        addBlock(x, 2, 5, "#2f353b");
        addBlock(x, 3, 5, "#884141");
      }

      // Crates.
      addBlock(-4, 1, 4, "#98613d");
      addBlock(2, 1, 4, "#84754d");
      addBlock(-1, 1, 4, "#7e6c55");

      // Ship.
      addShip(-1, -3);
    }

    buildScene();

    function loop() {
      if (needsDraw) {
        draw();
        needsDraw = false;
      }

      requestAnimationFrame(loop);
    }

    let dragging = false;
    let lastX = 0;
    let lastY = 0;

    canvas.addEventListener("pointerdown", (e) => {
      dragging = true;
      lastX = e.clientX;
      lastY = e.clientY;
      canvas.style.cursor = "grabbing";

      try {
        canvas.setPointerCapture(e.pointerId);
      } catch {
        // Ignore pointer capture failures.
      }
    });

    canvas.addEventListener("pointermove", (e) => {
      if (!dragging) return;

      yaw += (e.clientX - lastX) * 0.006;
      pitch += (e.clientY - lastY) * 0.006;

      lastX = e.clientX;
      lastY = e.clientY;

      pitch = Math.max(-1.2, Math.min(1.2, pitch));
      needsDraw = true;
    });

    window.addEventListener("pointerup", () => {
      dragging = false;
      canvas.style.cursor = "grab";
    });

    canvas.addEventListener("wheel", (e) => {
      e.preventDefault();

      camDist *= Math.exp(-e.deltaY * 0.0015);
      camDist = Math.max(18, Math.min(70, camDist));

      needsDraw = true;
    }, { passive: false });

    loop();
  </script>
</body>
</html>
```