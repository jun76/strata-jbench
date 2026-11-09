```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Voxel Harbor — Sailing Ship Calling At Harbor</title>
  <style>
    html, body {
      margin: 0;
      width: 100%;
      height: 100%;
      overflow: hidden;
      background: #9ed5ea;
    }
    canvas {
      display: block;
    }
    #info {
      position: absolute;
      left: 14px;
      top: 14px;
      color: white;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 13px;
      line-height: 1.35;
      text-shadow: 0 2px 6px rgba(0, 0, 0, 0.45);
      pointer-events: none;
      user-select: none;
    }
    #info strong {
      font-size: 15px;
    }
  </style>
</head>
<body>
  <div id="info">
    <strong>Voxel Harbor — Sailing Ship</strong><br />
    Drag: orbit<br />
    Scroll: zoom<br />
    Double-click: reset view
  </div>

  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js"></script>
  <script>
    if (!window.THREE) {
      document.getElementById("info").innerHTML =
        "<strong>Three.js failed to load.</strong><br />Check your internet connection.";
    } else {
      main();
    }

    function main() {
      const scene = new THREE.Scene();
      scene.background = new THREE.Color(0x9ed5ea);
      scene.fog = new THREE.Fog(0x9ed5ea, 65, 135);

      const camera = new THREE.PerspectiveCamera(
        52,
        window.innerWidth / window.innerHeight,
        0.1,
        220
      );

      const renderer = new THREE.WebGLRenderer({ antialias: true });
      renderer.setSize(window.innerWidth, window.innerHeight);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      renderer.domElement.style.touchAction = "none";
      document.body.appendChild(renderer.domElement);

      const hemi = new THREE.HemisphereLight(0xcfe8ff, 0x3b4b3d, 0.82);
      scene.add(hemi);

      const sun = new THREE.DirectionalLight(0xfff5d6, 0.88);
      sun.position.set(18, 28, 16);
      scene.add(sun);

      scene.add(new THREE.AmbientLight(0x2a4560, 0.28));

      const cubeGeo = new THREE.BoxGeometry(1, 1, 1);

      class VoxelBuilder {
        constructor() {
          this.byColor = new Map();
        }

        add(x, y, z, color) {
          let arr = this.byColor.get(color);
          if (!arr) {
            arr = [];
            this.byColor.set(color, arr);
          }
          arr.push({ x, y, z });
        }

        addBox(x0, y0, z0, sx, sy, sz, color) {
          for (let y = y0; y < y0 + sy; y++) {
            for (let z = z0; z < z0 + sz; z++) {
              for (let x = x0; x < x0 + sx; x++) {
                this.add(x, y, z, color);
              }
            }
          }
        }

        build(parent) {
          const matrix = new THREE.Matrix4();

          for (const [color, positions] of this.byColor) {
            const material = new THREE.MeshLambertMaterial({ color });
            const mesh = new THREE.InstancedMesh(cubeGeo, material, positions.length);

            for (let i = 0; i < positions.length; i++) {
              const p = positions[i];
              matrix.setPosition(p.x, p.y, p.z);
              mesh.setMatrixAt(i, matrix);
            }

            mesh.instanceMatrix.needsUpdate = true;
            mesh.frustumCulled = false;
            parent.add(mesh);
          }
        }
      }

      const staticBuilder = new VoxelBuilder();
      const shipBuilder = new VoxelBuilder();
      const cloudBuilder = new VoxelBuilder();

      const C = {
        waterDeep: 0x1c5e86,
        waterMid: 0x2b7ba7,
        waterLight: 0x4f9bc1,
        waterShallow: 0x76bfd2,
        foam: 0xeaf8f7,

        pierLight: 0xb9926a,
        pierMid: 0x8d6946,
        pierDark: 0x5d442f,
        pilings: 0x4a3528,

        hullDark: 0x314861,
        hullTrim: 0x8d332c,
        deck: 0xd5aa71,
        deckDark: 0xa67c4d,
        mast: 0x887150,
        rigging: 0x403024,
        sail: 0xf3efe0,
        sailShade: 0xc6bfaa,
        flag: 0xd34a3d,

        sand: 0xdcc99f,
        grass: 0x74a052,
        stone: 0x8b888f,
        stoneDark: 0x6b6870,

        wallWhite: 0xe9e2d6,
        roofRed: 0xa9413a,
        roofBlue: 0x2d5a82,

        crate1: 0xa87d51,
        crate2: 0x7b5c39,
        crate3: 0x366e8b,
        barrel: 0x8c6940,

        treeTrunk: 0x65492e,
        leaf: 0x567f44,

        lamp: 0xf5cf57,
        crane: 0xb94d4d,
        metal: 0x667182
      };

      function hash(x, y, z) {
        const n =
          Math.sin(x * 12.9898 + y * 78.233 + z * 37.719) * 43758.5453123;
        return n - Math.floor(n);
      }

      function pick(a, r) {
        return a[Math.floor(r * a.length) % a.length];
      }

      function addLine(b, ax, ay, az, bx, by, bz, color) {
        const dist = Math.max(
          Math.abs(ax - bx),
          Math.abs(ay - by),
          Math.abs(az - bz)
        );
        const steps = Math.max(1, Math.ceil(dist * 1.2));

        for (let i = 0; i <= steps; i++) {
          const t = i / steps;
          b.add(
            Math.round(ax + (bx - ax) * t),
            Math.round(ay + (by - ay) * t),
            Math.round(az + (bz - az) * t),
            color
          );
        }
      }

      // Ship geometry helper. Coordinates are centered cube cells.
      function hullHalfAtX(x) {
        if (x >= 6) {
          return x >= 8 ? 1 : x >= 7 ? 2 : 3;
        }
        if (x <= -6) {
          return x <= -8 ? 1 : x <= -7 ? 2 : 3;
        }
        return 3;
      }

      function shipLowerContains(x, z) {
        if (x < -8 || x > 8) return false;
        const lh = Math.max(0, hullHalfAtX(x) - 1);
        return z >= -lh && z <= lh;
      }

      function isWater(x, z) {
        if (x < -24 || x > 24 || z < -10 || z > 16) return false;
        if (shipLowerContains(x, z)) return false;
        if (x >= -6 && x <= 6 && z >= -10 && z <= -4) return false;
        return true;
      }

      // ------------------------------------------------------------------
      // Water
      // ------------------------------------------------------------------
      const waterColors = [
        C.waterDeep,
        C.waterMid,
        C.waterLight,
        C.waterShallow
      ];

      for (let x = -24; x <= 24; x++) {
        for (let z = -10; z <= 16; z++) {
          if (!isWater(x, z)) continue;

          const r = hash(x, z, 0);
          let col;
          if (r < 0.14) col = C.waterDeep;
          else if (r < 0.42) col = C.waterMid;
          else if (r < 0.75) col = C.waterLight;
          else col = C.waterShallow;

          staticBuilder.add(x, 0, z, col);
        }
      }

      // Foam near ship, pier, and shoreline.
      for (let x = -10; x <= 10; x++) {
        for (let z = -5; z <= 5; z++) {
          if (!isWater(x, z)) continue;
          if (x <= -8 || x >= 8 || z <= -4 || z >= 4) {
            staticBuilder.add(x, 1, z, C.foam);
          }
        }
      }

      for (let x = -22; x <= 22; x++) {
        if (isWater(x, -10)) {
          staticBuilder.add(x, 1, -10, C.foam);
        }
      }

      for (let z = -5; z <= 4; z++) {
        if (isWater(-7, z)) staticBuilder.add(-7, 1, z, C.foam);
        if (isWater(7, z)) staticBuilder.add(7, 1, z, C.foam);
      }

      // ------------------------------------------------------------------
      // Shore / land
      // ------------------------------------------------------------------
      for (let x = -22; x <= 22; x++) {
        for (let z = -20; z <= -12; z++) {
          staticBuilder.add(x, 0, z, C.stoneDark);
          const r = hash(x, z, 2);
          staticBuilder.add(
            x,
            1,
            z,
            r < 0.42 ? C.sand : r < 0.72 ? C.grass : C.stone
          );
        }
      }

      // Quay wall between land and pier/water.
      staticBuilder.addBox(-20, 1, -11, 41, 1, 1, C.stone);

      // ------------------------------------------------------------------
      // Pier
      // ------------------------------------------------------------------
      for (let x = -6; x <= 6; x++) {
        for (let z = -10; z <= -4; z++) {
          const edge = x === -6 || x === 6 || z === -4 || z === -10;
          const col = edge
            ? C.pierDark
            : ((x + z) & 1) ? C.pierLight : C.pierMid;
          staticBuilder.add(x, 1, z, col);
        }
      }

      // Supports / pilings.
      for (const x of [-5, -2, 1, 4]) {
        for (const z of [-9, -6]) {
          staticBuilder.add(x, 0, z, C.pilings);
        }
      }

      for (let x = -6; x <= 6; x += 2) {
        staticBuilder.add(x, 0, -4, C.pilings);
      }

      for (const x of [-6, 6]) {
        for (const z of [-9, -7, -5]) {
          staticBuilder.add(x, 0, z, C.pilings);
        }
      }

      // Bollards.
      for (const x of [-3, 0, 3]) {
        staticBuilder.add(x, 2, -4, C.pilings);
      }

      // Pier cargo.
      staticBuilder.addBox(-5, 2, -9, 1, 1, 1, C.crate1);
      staticBuilder.addBox(-5, 3, -9, 1, 1, 1, C.crate2);
      staticBuilder.addBox(-4, 2, -8, 1, 1, 1, C.crate2);
      staticBuilder.addBox(-3, 2, -9, 1, 1, 1, C.crate3);
      staticBuilder.addBox(4, 2, -8, 1, 2, 1, C.barrel);
      staticBuilder.addBox(5, 2, -7, 1, 1, 1, C.barrel);

      // Small crane on pier.
      staticBuilder.addBox(5, 2, -9, 2, 2, 2, C.pierDark);
      staticBuilder.addBox(5, 4, -9, 1, 3, 1, C.metal);
      staticBuilder.addBox(6, 6, -9, 3, 1, 1, C.crane);
      staticBuilder.addBox(6, 3, -8, 1, 1, 1, C.crate1);
      addLine(staticBuilder, 8, 5, -9, 7, 3, -7, C.rigging);

      // Simple mooring lines from ship side to pier front edge.
      for (const x of [-3, 0, 3]) {
        staticBuilder.add(x, 4, -2, C.rigging);
        staticBuilder.add(x, 4, -3, C.rigging);
        staticBuilder.add(x, 3, -4, C.rigging);
      }

      // ------------------------------------------------------------------
      // Shore buildings / lighthouse / trees
      // ------------------------------------------------------------------
      // Warehouse.
      staticBuilder.addBox(-18, 2, -18, 9, 3, 5, C.wallWhite);
      staticBuilder.addBox(-18, 5, -18, 9, 1, 5, C.roofRed);
      staticBuilder.addBox(-17, 6, -17, 7, 1, 3, C.roofRed);
      staticBuilder.addBox(-15, 2, -13, 2, 2, 1, C.pierDark);
      for (const x of [-17, -12, -10]) {
        staticBuilder.add(x, 3, -13, C.roofBlue);
      }

      // Harbor office.
      staticBuilder.addBox(10, 2, -17, 7, 3, 4, C.wallWhite);
      staticBuilder.addBox(10, 5, -17, 7, 1, 4, C.roofBlue);
      staticBuilder.addBox(11, 6, -16, 5, 1, 2, C.roofBlue);
      staticBuilder.addBox(12, 2, -13, 2, 2, 1, C.pierDark);
      for (const x of [10, 13, 15]) {
        staticBuilder.add(x, 3, -13, C.crate3);
      }

      // Lighthouse.
      for (let y = 2; y <= 7; y++) {
        const col = y === 3 || y === 5 || y === 7 ? C.flag : C.wallWhite;
        staticBuilder.addBox(-21, y, -17, 2, 1, 2, col);
      }
      staticBuilder.addBox(-21, 8, -17, 2, 1, 2, C.stoneDark);
      staticBuilder.addBox(-20, 9, -16, 1, 1, 1, C.lamp);
      staticBuilder.addBox(-21, 10, -17, 2, 1, 2, C.roofRed);

      function addTree(x, z) {
        staticBuilder.addBox(x, 2, z, 1, 3, 1, C.treeTrunk);
        staticBuilder.addBox(x - 1, 5, z - 1, 3, 2, 3, C.leaf);
      }
      addTree(-1, -16);
      addTree(5, -17);
      addTree(18, -19);

      // Rocks / breakwater.
      function rockCluster(cx, cz, count) {
        for (let i = 0; i < count; i++) {
          const x = cx + Math.floor(hash(i, 0, 0) * 7) - 3;
          const z = cz + Math.floor(hash(i, 1, 0) * 5) - 2;
          const h = Math.floor(hash(i, 2, 0) * 3) + 1;
          const col = h === 1 ? C.stone : C.stoneDark;
          staticBuilder.addBox(x, 1, z, 1, h, 1, col);
        }
      }
      rockCluster(19, 7, 12);
      rockCluster(-19, 4, 10);
      rockCluster(22, -3, 8);
      rockCluster(-22, -3, 8);

      // ------------------------------------------------------------------
      // Sailing ship
      // ------------------------------------------------------------------
      for (let x = -8; x <= 8; x++) {
        const hw = hullHalfAtX(x);
        const lh = Math.max(0, hw - 1);

        // Lower hull.
        for (let z = -lh; z <= lh; z++) {
          shipBuilder.add(x, 0, z, C.hullDark);
        }

        // Hull sides / trim.
        for (let z = -hw; z <= hw; z++) {
          shipBuilder.add(x, 1, z, C.hullDark);
          shipBuilder.add(
            x,
            2,
            z,
            Math.abs(z) === hw ? C.hullTrim : C.hullDark
          );
        }

        // Deck and rails.
        if (x >= -7 && x <= 7) {
          const dh = Math.max(0, hw - 1);
          for (let z = -dh; z <= dh; z++) {
            shipBuilder.add(
              x,
              3,
              z,
              ((x + z) & 1) ? C.deck : C.deckDark
            );
          }
          shipBuilder.add(x, 3, -hw, C.hullDark);
          shipBuilder.add(x, 3, hw, C.hullDark);
        } else {
          shipBuilder.add(x, 3, 0, C.hullDark);
        }
      }

      // Stern cabin.
      for (let x = -7; x <= -5; x++) {
        for (let z = -2; z <= 2; z++) {
          shipBuilder.add(x, 4, z, C.wallWhite);
          shipBuilder.add(x, 5, z, C.roofRed);
        }
      }
      for (let x = -6; x <= -5; x++) {
        for (let z = -1; z <= 1; z++) {
          shipBuilder.add(x, 6, z, C.roofRed);
        }
      }
      for (const x of [-6, -5]) {
        shipBuilder.add(x, 4, -3, C.pierDark);
      }

      // Cargo on deck.
      shipBuilder.addBox(1, 4, 0, 1, 1, 1, C.crate1);
      shipBuilder.addBox(2, 4, 1, 1, 1, 1, C.crate2);
      shipBuilder.addBox(-1, 4, 1, 1, 1, 1, C.crate3);
      shipBuilder.addBox(3, 4, 2, 1, 1, 1, C.crate1);
      shipBuilder.addBox(-2, 4, -1, 1, 2, 1, C.barrel);

      // Bowsprit.
      for (let x = 9; x <= 12; x++) {
        shipBuilder.add(x, 4, 0, C.mast);
      }
      shipBuilder.add(12, 5, 0, C.mast);

      function addYard(sailX, y, half, col) {
        for (let z = -half; z <= half; z++) {
          shipBuilder.add(sailX, y, z, col);
        }
      }

      function addSail(sailX, y0, y1, topHalf, bottomHalf, col, edgeCol) {
        const range = y1 - y0;

        for (let y = y0; y <= y1; y++) {
          const frac = range ? (y - y0) / range : 1;
          const half = Math.max(
            1,
            Math.round(bottomHalf + frac * (topHalf - bottomHalf))
          );

          for (let z = -half; z <= half; z++) {
            const c = y === y1 || Math.abs(z) === half ? edgeCol : col;
            shipBuilder.add(sailX, y, z, c);
          }
        }
      }

      function addFlag(mastX, y) {
        shipBuilder.add(mastX + 2, y, 0, C.flag);
        shipBuilder.add(mastX + 2, y - 1, 1, C.flag);
      }

      // Main mast.
      for (let y = 3; y <= 15; y++) shipBuilder.add(0, y, 0, C.mast);
      addYard(1, 10, 3, C.mast);
      addSail(1, 5, 9, 3, 1, C.sail, C.sailShade);
      addYard(1, 13, 2, C.mast);
      addSail(1, 11, 12, 2, 1, C.sail, C.sailShade);
      addFlag(0, 15);

      // Foremast.
      for (let y = 3; y <= 14; y++) shipBuilder.add(4, y, 0, C.mast);
      addYard(5, 10, 3, C.mast);
      addSail(5, 6, 9, 3, 2, C.sail, C.sailShade);
      addYard(5, 12, 2, C.mast);
      addSail(5, 11, 11, 1, 1, C.sail, C.sailShade);
      addFlag(4, 14);

      // Mizzen mast.
      for (let y = 3; y <= 13; y++) shipBuilder.add(-3, y, 0, C.mast);
      addYard(-2, 9, 2, C.mast);
      addSail(-2, 6, 8, 2, 1, C.sail, C.sailShade);
      addYard(-2, 11, 1, C.mast);
      addSail(-2, 10, 10, 1, 1, C.sail, C.sailShade);
      addFlag(-3, 13);

      // Rigging lines.
      addLine(shipBuilder, 3, 14, 0, 12, 3, 0, C.rigging);   // forestay
      addLine(shipBuilder, -1, 15, 0, 8, 4, 0, C.rigging);   // mainstay
      addLine(shipBuilder, -1, 15, 0, -8, 4, 0, C.rigging);  // backstay
      addLine(shipBuilder, -4, 13, 0, -8, 4, 0, C.rigging);  // mizzen backstay

      addLine(shipBuilder, -1, 15, 0, 0, 4, 3, C.rigging);   // main shroud
      addLine(shipBuilder, 3, 14, 0, 4, 4, 3, C.rigging);    // fore shroud
      addLine(shipBuilder, -4, 13, 0, -3, 4, 3, C.rigging);  // mizzen shroud

      const shipGroup = new THREE.Group();
      shipBuilder.build(shipGroup);
      scene.add(shipGroup);

      staticBuilder.build(scene);

      // ------------------------------------------------------------------
      // Clouds
      // ------------------------------------------------------------------
      function addCloud(cx, cz, size) {
        for (let x = -size; x <= size; x++) {
          for (let z = -Math.floor(size / 2); z <= Math.floor(size / 2); z++) {
            const r = hash(x + cx, z + cz, cx);
            if (r > 0.35) {
              const y = 14 + Math.floor(hash(x, z, 3) * 2);
              const col = hash(x, z, 4) > 0.75 ? C.stone : C.wallWhite;
              cloudBuilder.add(cx + x, y, cz + z, col);
            }
          }
        }
      }

      addCloud(-22, -30, 8);
      addCloud(12, -28, 10);
      addCloud(26, -36, 7);
      addCloud(-12, -38, 6);

      const cloudGroup = new THREE.Group();
      cloudBuilder.build(cloudGroup);
      scene.add(cloudGroup);

      // ------------------------------------------------------------------
      // Mouse / touch view controls
      // ------------------------------------------------------------------
      const target = new THREE.Vector3(0, 3.2, 0);
      const controls = {
        target,
        theta: 0.80,
        phi: 1.18,
        radius: 46,
        desiredTheta: 0.80,
        desiredPhi: 1.18,
        desiredRadius: 46,
        curTheta: 0.80,
        curPhi: 1.18,
        curRadius: 46,
        dragging: false,
        lastX: 0,
        lastY: 0
      };

      function clamp(v, min, max) {
        return Math.min(max, Math.max(min, v));
      }

      const dom = renderer.domElement;
      dom.style.cursor = "grab";

      dom.addEventListener("mousedown", (e) => {
        controls.dragging = true;
        controls.lastX = e.clientX;
        controls.lastY = e.clientY;
        dom.style.cursor = "grabbing";
        e.preventDefault();
      });

      window.addEventListener("mouseup", () => {
        controls.dragging = false;
        dom.style.cursor = "grab";
      });

      window.addEventListener("mousemove", (e) => {
        if (!controls.dragging) return;

        const dx = e.clientX - controls.lastX;
        const dy = e.clientY - controls.lastY;
        controls.lastX = e.clientX;
        controls.lastY = e.clientY;

        controls.desiredTheta -= dx * 0.005;
        controls.desiredPhi += dy * 0.005;
        controls.desiredPhi = clamp(controls.desiredPhi, 0.22, 1.52);
      });

      dom.addEventListener(
        "wheel",
        (e) => {
          e.preventDefault();
          controls.desiredRadius *= 1 + e.deltaY * 0.0012;
          controls.desiredRadius = clamp(controls.desiredRadius, 18, 95);
        },
        { passive: false }
      );

      dom.addEventListener("dblclick", () => {
        controls.desiredTheta = 0.80;
        controls.desiredPhi = 1.18;
        controls.desiredRadius = 46;
      });

      function touchDist(touches) {
        const dx = touches[0].clientX - touches[1].clientX;
        const dy = touches[0].clientY - touches[1].clientY;
        return Math.sqrt(dx * dx + dy * dy);
      }

      let touchStart = null;
      let pinchStart = 0;

      dom.addEventListener(
        "touchstart",
        (e) => {
          if (e.touches.length === 1) {
            touchStart = {
              x: e.touches[0].clientX,
              y: e.touches[0].clientY
            };
          } else if (e.touches.length === 2) {
            pinchStart = touchDist(e.touches);
          }
          e.preventDefault();
        },
        { passive: false }
      );

      dom.addEventListener(
        "touchmove",
        (e) => {
          if (e.touches.length === 1 && touchStart) {
            const dx = e.touches[0].clientX - touchStart.x;
            const dy = e.touches[0].clientY - touchStart.y;
            touchStart = {
              x: e.touches[0].clientX,
              y: e.touches[0].clientY
            };

            controls.desiredTheta -= dx * 0.006;
            controls.desiredPhi += dy * 0.006;
            controls.desiredPhi = clamp(controls.desiredPhi, 0.22, 1.52);
          } else if (e.touches.length === 2) {
            const d = touchDist(e.touches);
            if (pinchStart > 0) {
              controls.desiredRadius *= pinchStart / d;
              controls.desiredRadius = clamp(controls.desiredRadius, 18, 95);
            }
            pinchStart = d;
          }
          e.preventDefault();
        },
        { passive: false }
      );

      function updateCamera() {
        controls.curTheta += (controls.desiredTheta - controls.curTheta) * 0.15;
        controls.curPhi += (controls.desiredPhi - controls.curPhi) * 0.15;
        controls.curRadius +=
          (controls.desiredRadius - controls.curRadius) * 0.15;

        const r = controls.curRadius;
        const phi = controls.curPhi;
        const theta = controls.curTheta;

        camera.position.set(
          controls.target.x + r * Math.sin(phi) * Math.sin(theta),
          controls.target.y + r * Math.cos(phi),
          controls.target.z + r * Math.sin(phi) * Math.cos(theta)
        );
        camera.lookAt(controls.target);
      }

      window.addEventListener("resize", () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
      });

      const clock = new THREE.Clock();

      function animate() {
        requestAnimationFrame(animate);

        const t = clock.getElapsedTime();
        updateCamera();

        cloudGroup.position.x = Math.sin(t * 0.10) * 6;
        cloudGroup.position.y = 1.0 + Math.sin(t * 0.23) * 0.35;

        renderer.render(scene, camera);
      }

      animate();
    }
  </script>
</body>
</html>
```