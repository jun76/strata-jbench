Save this as a single `.html` file and open it directly in Chrome.

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>A sailing ship calling at a harbor</title>
  <style>
    html, body {
      height: 100%;
      margin: 0;
      overflow: hidden;
      background: #0f1721;
    }
    canvas {
      display: block;
      touch-action: none;
    }
    #hint {
      position: fixed;
      left: 14px;
      bottom: 14px;
      font: 14px system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
      color: #e9f1f8;
      background: rgba(10, 16, 26, 0.38);
      padding: 6px 8px;
      border-radius: 8px;
      pointer-events: none;
      opacity: 0.95;
    }
  </style>
</head>
<body>
  <canvas id="scene"></canvas>
  <div id="hint">drag = orbit · wheel = zoom · right/middle drag = pan</div>

  <script>
    (function () {
      const canvas = document.getElementById("scene");
      const ctx = canvas.getContext("2d");
      canvas.oncontextmenu = () => false;

      let width = 0, height = 0, dpr = 1;
      let dirty = true;

      let yaw = 0.58;
      let pitch = -0.34;
      let dist = 118;
      let panX = 0, panY = 0;

      let dragging = false;
      let mode = "rotate";
      let lastX = 0, lastY = 0;

      function clamp(v, a, b) {
        return v < a ? a : v > b ? b : v;
      }

      function resize() {
        width = window.innerWidth;
        height = window.innerHeight;
        dpr = Math.min(2, window.devicePixelRatio || 1);

        canvas.width = Math.round(width * dpr);
        canvas.height = Math.round(height * dpr);
        canvas.style.width = width + "px";
        canvas.style.height = height + "px";

        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        dirty = true;
      }

      window.addEventListener("resize", resize);
      resize();

      // Voxel storage: map key -> color array, list of occupied voxels.
      const voxMap = new Map();
      const voxList = [];

      function key(x, y, z) {
        // Safe for this scene size.
        return ((x + 100) * 1000000) + ((y + 100) * 1000) + (z + 100);
      }

      function setVoxel(x, y, z, r, g, b) {
        const k = key(x, y, z);
        const old = voxMap.get(k);

        if (old) {
          old[0] = r;
          old[1] = g;
          old[2] = b;
          return;
        }

        const c = [r, g, b];
        voxMap.set(k, c);
        voxList.push({ x, y, z, c });
      }

      function addBox(x0, y0, z0, x1, y1, z1, col) {
        if (x0 > x1) { const t = x0; x0 = x1; x1 = t; }
        if (y0 > y1) { const t = y0; y0 = y1; y1 = t; }
        if (z0 > z1) { const t = z0; z0 = z1; z1 = t; }

        for (let x = x0; x <= x1; x++) {
          for (let y = y0; y <= y1; y++) {
            for (let z = z0; z <= z1; z++) {
              setVoxel(x, y, z, col[0], col[1], col[2]);
            }
          }
        }
      }

      // Palette.
      const WATER_D = [23, 88, 150];
      const WATER_M = [32, 109, 176];
      const WATER_L = [42, 128, 194];

      const SAND    = [214, 184, 118];
      const GRASS   = [74, 140, 72];
      const GRASS2  = [58, 118, 62];

      const WOOD    = [119, 78, 52];
      const WOOD2   = [91, 58, 36];
      const WOOD3   = [150, 102, 66];
      const DECK    = [220, 180, 118];

      const SAIL    = [245, 243, 238];
      const WHITE   = [238, 240, 245];
      const RED     = [224, 60, 55];
      const BLUE    = [45, 85, 205];
      const YELLOW  = [245, 198, 55];
      const DARK    = [48, 54, 64];
      const METAL   = [96, 104, 118];
      const LAMP    = [255, 230, 120];

      // ------------------------------------------------------------
      // Build the voxel scene.
      // ------------------------------------------------------------

      // Water.
      for (let x = -18; x <= 10; x++) {
        for (let z = -14; z <= 13; z++) {
          const t = (x * 5 + z * 11) & 3;
          const col = (t === 0 ? WATER_D : (t === 1 ? WATER_M : WATER_L));
          setVoxel(x, 0, z, col[0], col[1], col[2]);
        }
      }

      // Shore land.
      for (let x = 11; x <= 27; x++) {
        for (let z = -15; z <= 14; z++) {
          setVoxel(x, 0, z, SAND[0], SAND[1], SAND[2]);

          const g = ((x + z * 3) & 1) ? GRASS : GRASS2;
          setVoxel(x, 1, z, g[0], g[1], g[2]);
        }
      }

      // Harbor dock.
      addBox(10, 2, -9, 21, 3, 9, WOOD);
      addBox(10, 3, -9, 21, 3, 9, WOOD2); // darker top planks

      for (const z of [-8, -4, 0, 4, 8]) {
        addBox(9, 1, z, 9, 3, z, WOOD);
      }

      // Mooring line from ship to dock.
      addBox(7, 4, 0, 9, 4, 0, DARK);

      // Bollards.
      for (const z of [-8, -4, 0, 4, 8]) {
        addBox(10, 4, z, 10, 5, z, DARK);
      }

      // Harbor sign.
      setVoxel(14, 4, -9, WOOD2[0], WOOD2[1], WOOD2[2]);
      setVoxel(15, 4, -9, WOOD2[0], WOOD2[1], WOOD2[2]);
      addBox(14, 5, -9, 15, 6, -9, YELLOW);

      // Crates.
      addBox(12, 4, -8, 13, 5, -7, WOOD3);
      addBox(13, 4, -6, 14, 6, -5, WOOD2);
      addBox(12, 4, -7, 12, 6, -7, WOOD);

      // Barrels.
      addBox(12, 4, 2, 13, 5, 3, WOOD2);
      addBox(12, 4, 1, 13, 4, 1, WOOD);

      // Warehouse.
      addBox(23, 4, -7, 26, 6, -3, RED);
      addBox(22, 7, -8, 27, 7, -2, METAL);

      // Lighthouse.
      for (let y = 4; y <= 10; y++) {
        const col = (y % 2 === 0 ? WHITE : RED);
        addBox(23, y, 8, 24, y, 9, col[0], col[1], col[2]);
      }
      addBox(22, 11, 7, 25, 11, 10, DARK);
      addBox(23, 12, 8, 24, 13, 9, LAMP);
      addBox(23, 14, 8, 24, 14, 9, DARK);

      // Harbor buoy.
      addBox(7, 1, -12, 8, 2, -11, RED);
      addBox(7, 3, -12, 8, 3, -11, WHITE);
      setVoxel(7, 4, -12, RED[0], RED[1], RED[2]);

      // ------------------------------------------------------------
      // Sailing ship hull, decks, masts, sails, flags.
      // ------------------------------------------------------------
      addBox(-8, 1, -1, 6, 1, 1, WOOD2);       // keel
      addBox(-9, 2, -3, 7, 2, 3, WOOD);       // lower hull
      addBox(-10, 3, -4, 7, 3, 4, WOOD);      // upper hull

      // Bow and stern tapers/overhang.
      addBox(8, 2, 0, 8, 2, 0, WOOD);
      addBox(8, 3, -1, 8, 3, 1, WOOD);
      addBox(9, 3, 0, 9, 3, 0, WOOD);
      addBox(-10, 2, -1, -10, 2, 1, WOOD);
      addBox(-11, 3, 0, -11, 3, 0, WOOD2);

      // Main deck.
      addBox(-9, 4, -4, 6, 4, 4, DECK);

      // Forecastle, quarterdeck, cabin.
      addBox(-10, 5, -3, -8, 6, 3, WOOD2);
      addBox(4, 5, -3, 6, 6, 3, WOOD2);
      addBox(-6, 5, -2, -3, 6, 2, WOOD3);

      // Masts.
      for (let y = 5; y <= 13; y++) setVoxel(-6, y, 0, WOOD[0], WOOD[1], WOOD[2]);
      for (let y = 5; y <= 15; y++) setVoxel(0, y, 0, WOOD[0], WOOD[1], WOOD[2]);
      for (let y = 5; y <= 12; y++) setVoxel(4, y, 0, WOOD[0], WOOD[1], WOOD[2]);

      // Yards.
      addBox(-6, 10, -3, -6, 10, 3, WOOD2);
      addBox(0, 12, -3, 0, 12, 3, WOOD2);
      addBox(4, 9, -3, 4, 9, 2, WOOD2);

      // Sails.
      addBox(-8, 6, -2, -4, 9, -1, SAIL);
      addBox(-2, 7, -2, 2, 11, -1, SAIL);
      addBox(3, 6, -2, 5, 8, -1, SAIL);

      // Mast flags.
      setVoxel(-6, 14, 0, RED[0], RED[1], RED[2]);
      setVoxel(-5, 13, 0, RED[0], RED[1], RED[2]);

      setVoxel(0, 16, 0, BLUE[0], BLUE[1], BLUE[2]);
      setVoxel(1, 15, 0, BLUE[0], BLUE[1], BLUE[2]);

      setVoxel(4, 13, 0, YELLOW[0], YELLOW[1], YELLOW[2]);
      setVoxel(3, 12, 0, YELLOW[0], YELLOW[1], YELLOW[2]);

      // Small signal pennants near the mainmast.
      setVoxel(-1, 13, 1, RED[0], RED[1], RED[2]);
      setVoxel(0, 14, 1, WHITE[0], WHITE[1], WHITE[2]);
      setVoxel(1, 15, 1, BLUE[0], BLUE[1], BLUE[2]);

      // ------------------------------------------------------------
      // Generate surface faces from occupied voxels.
      // Interior voxel-to-voxel faces are omitted.
      // ------------------------------------------------------------
      const faces = [];

      function addFaceFromSide(x, y, z, nx, ny, nz, col) {
        let c;

        if (nx === 1) {
          c = [
            x + 1, y, z,
            x + 1, y + 1, z,
            x + 1, y + 1, z + 1,
            x + 1, y, z + 1
          ];
        } else if (nx === -1) {
          c = [
            x, y, z + 1,
            x, y + 1, z + 1,
            x, y + 1, z,
            x, y, z
          ];
        } else if (ny === 1) {
          c = [
            x, y + 1, z,
            x + 1, y + 1, z,
            x + 1, y + 1, z + 1,
            x, y + 1, z + 1
          ];
        } else if (ny === -1) {
          c = [
            x + 1, y, z,
            x + 1, y, z + 1,
            x, y, z + 1,
            x, y, z
          ];
        } else if (nz === 1) {
          c = [
            x, y, z + 1,
            x + 1, y, z + 1,
            x + 1, y + 1, z + 1,
            x, y + 1, z + 1
          ];
        } else {
          c = [
            x + 1, y, z,
            x, y, z,
            x, y + 1, z,
            x + 1, y + 1, z
          ];
        }

        const dot = nx * 0.37 + ny * 0.90 + nz * 0.57;
        const shade = 0.52 + 0.42 * Math.max(0, dot);

        faces.push({
          c,
          pts: new Array(8),
          nx, ny, nz,
          col,
          shade
        });
      }

      for (const v of voxList) {
        const x = v.x, y = v.y, z = v.z;
        const col = v.c;

        if (!voxMap.has(key(x + 1, y, z))) addFaceFromSide(x, y, z, 1, 0, 0, col);
        if (!voxMap.has(key(x - 1, y, z))) addFaceFromSide(x, y, z, -1, 0, 0, col);
        if (!voxMap.has(key(x, y + 1, z))) addFaceFromSide(x, y, z, 0, 1, 0, col);
        if (!voxMap.has(key(x, y - 1, z))) addFaceFromSide(x, y, z, 0, -1, 0, col);
        if (!voxMap.has(key(x, y, z + 1))) addFaceFromSide(x, y, z, 0, 0, 1, col);
        if (!voxMap.has(key(x, y, z - 1))) addFaceFromSide(x, y, z, 0, 0, -1, col);
      }

      // ------------------------------------------------------------
      // Renderer.
      // ------------------------------------------------------------
      let fov = 1050;

      function render() {
        const sky = ctx.createLinearGradient(0, 0, 0, height);
        sky.addColorStop(0.0, "#77b7d8");
        sky.addColorStop(0.58, "#d7e9f1");
        sky.addColorStop(1.0, "#a5c8d8");

        ctx.fillStyle = sky;
        ctx.fillRect(0, 0, width, height);

        const centerX = 2;
        const centerY = 4;
        const centerZ = 0;

        const cyaw = Math.cos(yaw), syaw = Math.sin(yaw);
        const cp = Math.cos(pitch), sp = Math.sin(pitch);

        const camX = width / 2 + panX;
        const camY = height / 2 + panY;

        const near = 18;
        const visible = [];

        for (const f of faces) {
          const nx = f.nx, ny = f.ny, nz = f.nz;

          const ny0 = ny * cp - nz * sp;
          const nz0 = ny * sp + nz * cp;
          const nxc = nx * cyaw + nz0 * syaw;
          const nzc = -nx * syaw + nz0 * cyaw;
          const nyc = ny0;

          const c = f.c;
          const p = f.pts;

          let xs = 0, ys = 0, zs = 0;
          let ok = true;

          for (let i = 0; i < 4; i++) {
            const j = i * 3;

            const px = c[j] - centerX;
            const py = c[j + 1] - centerY;
            const pz = c[j + 2] - centerZ;

            const y0 = py * cp - pz * sp;
            const z0 = py * sp + pz * cp;

            const x2 = px * cyaw + z0 * syaw;
            const z2 = -px * syaw + z0 * cyaw;

            const zcam = z2 + dist;

            if (zcam < near) {
              ok = false;
              break;
            }

            const scale = fov / zcam;

            p[i * 2] = camX + x2 * scale;
            p[i * 2 + 1] = camY - y0 * scale;

            xs += x2;
            ys += y0;
            zs += z2;
          }

          if (!ok) continue;

          const cxc = xs * 0.25;
          const cyc = ys * 0.25;
          const czc = zs * 0.25 + dist;

          if (czc < near) continue;

          // Back-face culling.
          if (nxc * cxc + nyc * cyc + nzc * czc >= 0) continue;

          visible.push({
            depth: czc,
            pts: p,
            col: f.col,
            shade: f.shade
          });
        }

        visible.sort((a, b) => b.depth - a.depth);

        ctx.lineJoin = "round";
        ctx.lineCap = "round";

        for (const f of visible) {
          const p = f.pts;
          const c = f.col;
          const sh = f.shade;

          let r = Math.round(c[0] * sh);
          let g = Math.round(c[1] * sh);
          let b = Math.round(c[2] * sh);

          r = r > 255 ? 255 : r;
          g = g > 255 ? 255 : g;
          b = b > 255 ? 255 : b;

          let sr = Math.round(r * 0.72);
          let sg = Math.round(g * 0.72);
          let sb = Math.round(b * 0.72);

          if (sr < 0) sr = 0;
          if (sg < 0) sg = 0;
          if (sb < 0) sb = 0;

          ctx.beginPath();
          ctx.moveTo(p[0], p[1]);
          ctx.lineTo(p[2], p[3]);
          ctx.lineTo(p[4], p[5]);
          ctx.lineTo(p[6], p[7]);
          ctx.closePath();

          ctx.fillStyle = "rgb(" + r + "," + g + "," + b + ")";
          ctx.strokeStyle = "rgb(" + sr + "," + sg + "," + sb + ")";
          ctx.lineWidth = 0.55;

          ctx.fill();
          ctx.stroke();
        }
      }

      // Initial render.
      render();
      dirty = false;

      // Input handlers.
      canvas.addEventListener("pointerdown", function (e) {
        dragging = true;
        mode = (e.button === 2) ? "pan" : "rotate";
        lastX = e.clientX;
        lastY = e.clientY;
        dirty = true;
      });

      canvas.addEventListener("pointermove", function (e) {
        if (!dragging) return;

        const x = e.clientX;
        const y = e.clientY;

        const dx = x - lastX;
        const dy = y - lastY;

        if (mode === "pan") {
          panX += dx;
          panY += dy;
        } else {
          yaw += dx * 0.0055;
          pitch = clamp(pitch - dy * 0.0055, -1.20, 1.20);
        }

        lastX = x;
        lastY = y;
        dirty = true;
      });

      canvas.addEventListener("pointerup", function () {
        dragging = false;
        dirty = false;
      });

      canvas.addEventListener("wheel", function (e) {
        dist *= Math.exp(e.deltaY * 0.0016);
        dist = clamp(dist, 55, 260);
        dirty = true;
      });

      // Animation/redraw loop.
      (function loop() {
        if (dirty) {
          render();
          dirty = false;
        }
        requestAnimationFrame(loop);
      })();
    })();
  </script>
</body>
</html>
```