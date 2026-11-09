Paste this into a single `.html` file and open it in Chrome. Drag with the mouse to rotate the scene, and scroll to zoom. No external libraries are required.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>3D Voxel Harbor Scene</title>
  <style>
    body {
      margin: 0;
      overflow: hidden;
      background: #0d1520;
    }

    canvas {
      display: block;
      width: 100vw;
      height: 100vh;
    }

    #ui {
      position: absolute;
      top: 12px;
      left: 12px;
      color: rgba(255, 255, 255, 0.85);
      font-family: Arial, sans-serif;
      font-size: 14px;
      pointer-events: none;
    }
  </style>
</head>
<body>
  <div id="ui">Drag to rotate · Scroll to zoom</div>
  <canvas id="scene"></canvas>

  <script>
    const canvas = document.getElementById("scene");
    const ctx = canvas.getContext("2d");

    let yaw = 0.62;
    let pitch = 0.32;
    let zoom = 3000;
    let dist = 380;

    let dragging = false;
    let lastX = 0;
    let lastY = 0;
    let dirty = true;

    function resize() {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      dirty = true;
    }

    resize();
    window.addEventListener("resize", resize);

    const voxels = [];
    const seen = new Set();

    function addCube(x, y, z, color, edge = true) {
      const key = (x + 1000) * 1000000 + (y + 1000) * 1000 + z;
      if (seen.has(key)) return;

      seen.add(key);

      const r = Math.max(0, Math.min(255, color[0] | 0));
      const g = Math.max(0, Math.min(255, color[1] | 0));
      const b = Math.max(0, Math.min(255, color[2] | 0));

      voxels.push({ x, y, z, r, g, b, edge });
    }

    function addShell(x1, x2, y1, y2, z1, z2, color) {
      for (let x = x1; x <= x2; x++) {
        for (let y = y1; y <= y2; y++) {
          for (let z = z1; z <= z2; z++) {
            if (x === x1 || x === x2 || y === y1 || y === y2 || z === z1 || z === z2) {
              addCube(x, y, z, color);
            }
          }
        }
      }
    }

    const faceNormals = [
      [1, 0, 0],
      [-1, 0, 0],
      [0, 1, 0],
      [0, -1, 0],
      [0, 0, 1],
      [0, 0, -1]
    ];

    const faceCorners = [
      [[0.5, -0.5, -0.5], [0.5, 0.5, -0.5], [0.5, 0.5, 0.5], [0.5, -0.5, 0.5]],
      [[-0.5, -0.5, 0.5], [-0.5, 0.5, 0.5], [-0.5, 0.5, -0.5], [-0.5, -0.5, -0.5]],
      [[-0.5, 0.5, 0.5], [0.5, 0.5, 0.5], [0.5, 0.5, -0.5], [-0.5, 0.5, -0.5]],
      [[-0.5, -0.5, -0.5], [0.5, -0.5, -0.5], [0.5, -0.5, 0.5], [-0.5, -0.5, 0.5]],
      [[-0.5, -0.5, 0.5], [0.5, -0.5, 0.5], [0.5, 0.5, 0.5], [-0.5, 0.5, 0.5]],
      [[-0.5, 0.5, -0.5], [0.5, 0.5, -0.5], [0.5, -0.5, -0.5], [-0.5, -0.5, -0.5]]
    ];

    function shadeValue(normal) {
      const dot = normal[0] * 0.35 + normal[1] * 0.55 + normal[2] * 0.85;
      const s = 0.55 + 0.38 * dot;
      return Math.max(0.45, Math.min(1.0, s));
    }

    const shades = faceNormals.map(shadeValue);

    function buildScene() {
      /*
        Scene layout:
        - Open water: x/y roughly -38 to 38
        - Harbor/dock on the right
        - Sailing ship in the water to the left
        - Breakwater and lighthouse
        - Buoys and mooring rope
      */

      // Open water surface.
      for (let x = -38; x <= 38; x++) {
        for (let y = -38; y <= 38; y++) {
          const wave = Math.sin(x * 0.17 + y * 0.12) * 0.18 +
                       Math.sin((x + y) * 0.22) * 0.10;

          const r = Math.max(22, Math.min(110, 38 + Math.round(38 * wave)));
          const g = Math.max(68, Math.min(175, 104 + Math.round(55 * wave)));
          const b = Math.max(95, Math.min(215, 155 + Math.round(70 * wave)));

          addCube(x, y, 0, [r, g, b], false);
        }
      }

      // Harbor dock deck.
      const dock = [168, 113, 68];
      const dockDark = [110, 77, 52];

      for (let x = 14; x <= 31; x++) {
        for (let y = -9; y <= 9; y++) {
          addCube(x, y, 3, dock);
        }
      }

      for (let x = 14; x <= 31; x++) {
        addCube(x, -9, 2, dock);
        addCube(x, 9, 2, dock);
      }

      for (let y = -9; y <= 9; y++) {
        addCube(14, y, 2, dock);
        addCube(31, y, 2, dock);
      }

      // Dock pilings.
      for (let x of [14, 22, 31]) {
        for (let y of [-9, 9]) {
          addCube(x, y, 1, dockDark);
          addCube(x, y, 2, dock);
        }
      }

      // Harbor lamps.
      for (let x = 16; x <= 28; x += 4) {
        addCube(x, -9, 4, [240, 190, 120]);
        addCube(x, -9, 5, [78, 55, 35]);
      }

      // Shore land behind the dock.
      const land = [174, 134, 92];
      const landDark = [132, 106, 74];

      addShell(31, 44, -24, 24, 1, 3, land);

      for (let x = 31; x <= 44; x++) {
        addCube(x, -24, 1, landDark);
        addCube(x, 24, 1, landDark);
      }

      // Small harbor buildings.
      const house = [238, 224, 188];
      const roof = [147, 85, 60];

      for (let x = 33; x <= 40; x++) {
        for (let y = -7; y <= -3; y++) {
          for (let z = 4; z <= 6; z++) {
            addCube(x, y, z, house);
          }
          addCube(x, y, 7, roof);
        }
      }

      // Breakwater.
      const rock = [128, 133, 139];

      for (let x = 18; x <= 32; x++) {
        for (let y = 18; y <= 32; y++) {
          for (let z = 2; z <= 4; z++) {
            const t = Math.sin(x * 0.29 + y * 0.23 + z * 0.5);
            addCube(x, y, z, [
              rock[0] + Math.round(18 * t),
              rock[1] + Math.round(14 * t),
              rock[2] + Math.round(22 * t)
            ]);
          }
        }
      }

      // Lighthouse.
      const white = [245, 240, 235];
      const red = [240, 68, 54];
      const dark = [62, 58, 58];

      for (let z = 4; z <= 10; z++) {
        const c = (z % 3 === 1) ? red : white;
        for (let x = 28; x <= 29; x++) {
          for (let y = 24; y <= 25; y++) {
            addCube(x, y, z, c);
          }
        }
      }

      for (let x = 28; x <= 29; x++) {
        for (let y = 24; y <= 25; y++) {
          addCube(x, y, 11, dark);
        }
      }

      addCube(29, 25, 12, [255, 255, 255]);

      // Buoys.
      function buoy(x, y, c) {
        addCube(x, y, 1, c);
        addCube(x, y, 2, c);
        addCube(x, y, 3, [84, 64, 43]);
      }

      buoy(-24, 10, [225, 64, 49]);
      buoy(-22, -12, [255, 202, 86]);
      buoy(-12, 14, [225, 64, 49]);
      buoy(10, -18, [255, 202, 86]);

      // Sailing ship.
      const hull = [89, 57, 37];
      const hullBottom = [56, 39, 25];
      const deck = [125, 88, 57];
      const mast = [84, 64, 45];
      const sail = [242, 237, 219];
      const rope = [208, 188, 146];

      // Hull: bow toward the harbor, to the right.
      for (let x = -17; x <= 6; x++) {
        let maxAbsY = 5;

        if (x >= 4) {
          maxAbsY = Math.max(1, 7 - x);
        }

        if (x <= -15) {
          maxAbsY = Math.max(2, 15 + x);
        }

        for (let y = -maxAbsY; y <= maxAbsY; y++) {
          for (let z = 1; z <= 3; z++) {
            const col = (z === 1) ? hullBottom : (z === 3 ? deck : hull);
            addCube(x, y, z, col);
          }
        }
      }

      // Main mast and foremast.
      for (let z = 4; z <= 16; z++) {
        addCube(-8, 0, z, mast);
      }

      for (let z = 4; z <= 12; z++) {
        addCube(4, 0, z, mast);
      }

      // Yard arms for sails.
      function yard(cx, cz, x1, x2) {
        for (let x = x1; x <= x2; x++) {
          addCube(x, 0, cz, mast);
        }
      }

      yard(-8, 16, -16, 0);
      yard(-8, 14, -14, 0);
      yard(-8, 12, -12, 0);

      yard(4, 12, 0, 8);
      yard(4, 10, 0, 8);
      yard(4, 8, 0, 8);

      // Sails.
      function sail(cx, zBottom, zTop, halfWidth) {
        for (let z = zBottom; z <= zTop; z++) {
          const hw = Math.max(1, Math.round(halfWidth * (zTop - z) / Math.max(1, zTop - zBottom)));

          for (let x = cx - hw; x <= cx + hw; x++) {
            addCube(x, 0, z, sail);
            addCube(x, -1, z, sail);
          }
        }
      }

      sail(-8, 6, 15, 8);
      sail(4, 6, 12, 5);

      // Stern flag.
      addCube(-16, 0, 4, mast);
      addCube(-15, 0, 5, [244, 64, 60]);
      addCube(-14, 0, 5, [244, 64, 60]);

      // Bow mooring rope to dock.
      for (let x = 6; x <= 14; x++) {
        const t = (x - 6) / 8;
        const z = 3 - Math.round(Math.sin(t * Math.PI) * 1);
        addCube(x, 0, z, rope);
      }

      // Small wave crests, added after solid objects so they do not erase them.
      for (let x = -36; x <= 36; x++) {
        for (let y = -36; y <= 36; y++) {
          if (Math.sin(x * 0.28 + y * 0.19) > 0.85) {
            addCube(x, y, 1, [68, 138, 198], false);
          }
        }
      }
    }

    buildScene();

    function render() {
      dirty = false;

      const w = canvas.width;
      const h = canvas.height;

      // Background sky/sea gradient.
      const bg = ctx.createLinearGradient(0, 0, w, h);
      bg.addColorStop(0, "#22344d");
      bg.addColorStop(0.45, "#152231");
      bg.addColorStop(1, "#0b1420");

      ctx.fillStyle = bg;
      ctx.fillRect(0, 0, w, h);

      // Soft sun/cloud highlight.
      ctx.fillStyle = "rgba(255, 215, 130, 0.16)";
      ctx.beginPath();
      ctx.arc(w * 0.73, h * 0.13, Math.min(w, h) * 0.16, 0, Math.PI * 2);
      ctx.fill();

      const centerX = w * 0.5;
      const centerY = h * 0.5;
      const scale = zoom * Math.min(w, h) / 800;

      const sy = Math.sin(yaw);
      const cy = Math.cos(yaw);
      const sp = Math.sin(pitch);
      const cp = Math.cos(pitch);

      // Rotated basis vectors in camera space.
      const rotXx = cy;
      const rotXy = sy * cp;
      const rotXz = sy * sp;

      const rotYx = -sy;
      const rotYy = cy * cp;
      const rotYz = cy * sp;

      const rotZx = 0;
      const rotZy = -sp;
      const rotZz = cp;

      const faces = [];

      for (let i = 0; i < voxels.length; i++) {
        const v = voxels[i];

        const rotatedY = v.x * sy + v.y * cy;

        const cX = v.x * cy - v.y * sy;
        const cY = rotatedY * cp - v.z * sp;
        const cZ = rotatedY * sp + v.z * cp;

        for (let f = 0; f < 6; f++) {
          const n = faceNormals[f];

          const nX = n[0] * rotXx + n[1] * rotYx + n[2] * rotZx;
          const nY = n[0] * rotXy + n[1] * rotYy + n[2] * rotZy;
          const nZ = n[0] * rotXz + n[1] * rotYz + n[2] * rotZz;

          const fX = cX + nX * 0.5;
          const fY = cY + nY * 0.5;
          const fZ = cZ + nZ * 0.5;

          const depth = dist - fZ;
          if (depth <= 1) continue;

          // Face visibility from the camera:
          // normal dot (camera position - face center) > 0
          const visible = nX * (-fX) + nY * (-fY) + nZ * depth;
          if (visible <= 0.001) continue;

          const inv = scale / depth;
          const corners = faceCorners[f];

          const ax = centerX + (cX + corners[0][0] * rotXx + corners[0][1] * rotYx + corners[0][2] * rotZx) * inv;
          const ay = centerY - (cY + corners[0][0] * rotXy + corners[0][1] * rotYy + corners[0][2] * rotZy) * inv;

          const bx = centerX + (cX + corners[1][0] * rotXx + corners[1][1] * rotYx + corners[1][2] * rotZx) * inv;
          const by = centerY - (cY + corners[1][0] * rotXy + corners[1][1] * rotYy + corners[1][2] * rotZy) * inv;

          const dx = centerX + (cX + corners[2][0] * rotXx + corners[2][1] * rotYx + corners[2][2] * rotZx) * inv;
          const dy = centerY - (cY + corners[2][0] * rotXy + corners[2][1] * rotYy + corners[2][2] * rotZy) * inv;

          const ex = centerX + (cX + corners[3][0] * rotXx + corners[3][1] * rotYx + corners[3][2] * rotZx) * inv;
          const ey = centerY - (cY + corners[3][0] * rotXy + corners[3][1] * rotYy + corners[3][2] * rotZy) * inv;

          const s = shades[f];

          faces.push({
            depth,
            ax, ay,
            bx, by,
            dx, dy,
            ex, ey,
            r: Math.round(v.r * s),
            g: Math.round(v.g * s),
            b: Math.round(v.b * s),
            edge: v.edge
          });
        }
      }

      // Painter's algorithm: draw far faces first.
      faces.sort((a, b) => b.depth - a.depth);

      ctx.lineWidth = 1;

      for (let i = 0; i < faces.length; i++) {
        const face = faces[i];

        ctx.beginPath();
        ctx.moveTo(face.ax, face.ay);
        ctx.lineTo(face.bx, face.by);
        ctx.lineTo(face.dx, face.dy);
        ctx.lineTo(face.ex, face.ey);
        ctx.closePath();

        ctx.fillStyle = "rgb(" + face.r + "," + face.g + "," + face.b + ")";
        ctx.fill();

        if (face.edge) {
          ctx.strokeStyle = "rgba(12, 12, 12, 0.22)";
        } else {
          ctx.strokeStyle = "rgba(18, 28, 40, 0.12)";
        }

        ctx.stroke();
      }
    }

    canvas.addEventListener("mousedown", e => {
      dragging = true;
      lastX = e.clientX;
      lastY = e.clientY;
    });

    window.addEventListener("mouseup", () => {
      dragging = false;
    });

    window.addEventListener("mousemove", e => {
      if (!dragging) return;

      yaw += (e.clientX - lastX) * 0.004;
      pitch += (e.clientY - lastY) * 0.004;

      pitch = Math.max(-1.2, Math.min(1.2, pitch));

      lastX = e.clientX;
      lastY = e.clientY;

      dirty = true;
    });

    canvas.addEventListener("wheel", e => {
      e.preventDefault();

      zoom *= 1 - e.deltaY * 0.0004;
      zoom = Math.max(800, Math.min(12000, zoom));

      dirty = true;
    });

    function loop() {
      if (dirty) render();
      requestAnimationFrame(loop);
    }

    loop();
  </script>
</body>
</html>
```