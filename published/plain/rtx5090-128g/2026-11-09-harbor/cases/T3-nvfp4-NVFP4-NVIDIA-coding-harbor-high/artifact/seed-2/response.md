Save this as `harbor.html` and open it in Chrome.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Voxel Scene — A Sailing Ship Calling at a Harbor</title>
  <style>
    html, body {
      height: 100%;
      margin: 0;
      overflow: hidden;
      background: #9bd7ff;
      font-family: system-ui, sans-serif;
    }
    canvas {
      display: block;
    }
    #overlay {
      position: fixed;
      left: 12px;
      bottom: 12px;
      color: white;
      background: rgba(0, 0, 0, 0.35);
      padding: 10px 12px;
      border-radius: 10px;
      font-size: 13px;
      line-height: 1.4;
      pointer-events: none;
      backdrop-filter: blur(4px);
      user-select: none;
    }
    #overlay strong {
      display: block;
      margin-bottom: 3px;
      font-size: 15px;
    }
  </style>
</head>
<body>
  <div id="overlay">
    <strong>A Sailing Ship Calling at a Harbor</strong>
    drag: orbit &nbsp;•&nbsp; scroll: zoom &nbsp;•&nbsp; right-drag / shift-drag: pan
  </div>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>

  <script>
    (function () {
      'use strict';

      function fract(x) {
        return x - Math.floor(x);
      }

      function rand(seed) {
        return fract(Math.sin(seed * 127.1 + 0.1234) * 43758.5453123);
      }

      function rand3(x, y, z) {
        return fract(Math.sin(x * 127.1 + y * 311.7 + z * 74.7) * 43758.5453);
      }

      function pick(arr, x, y, z) {
        return arr[Math.floor(rand3(x, y, z) * arr.length) % arr.length];
      }

      const voxelGeometry = new THREE.BoxGeometry(1, 1, 1);
      voxelGeometry.translate(0, 0.5, 0);

      class VoxelBuilder {
        constructor() {
          this.groups = new Map();
          this.seen = new Set();
        }

        add(x, y, z, color) {
          const key = `${x},${y},${z}`;
          if (this.seen.has(key)) return;
          this.seen.add(key);

          let arr = this.groups.get(color);
          if (!arr) {
            arr = [];
            this.groups.set(color, arr);
          }
          arr.push(x, y, z);
        }

        box(x1, x2, y1, y2, z1, z2, color) {
          if (x1 > x2) { let t = x1; x1 = x2; x2 = t; }
          if (y1 > y2) { let t = y1; y1 = y2; y2 = t; }
          if (z1 > z2) { let t = z1; z1 = z2; z2 = t; }

          for (let x = x1; x <= x2; x++) {
            for (let y = y1; y <= y2; y++) {
              for (let z = z1; z <= z2; z++) {
                const c = Array.isArray(color) ? pick(color, x, y, z) : color;
                this.add(x, y, z, c);
              }
            }
          }
        }

        walls(x1, x2, y1, y2, z1, z2, color) {
          if (x1 > x2) { let t = x1; x1 = x2; x2 = t; }
          if (y1 > y2) { let t = y1; y1 = y2; y2 = t; }
          if (z1 > z2) { let t = z1; z1 = z2; z2 = t; }

          for (let y = y1; y <= y2; y++) {
            for (let x = x1; x <= x2; x++) {
              const c = Array.isArray(color) ? pick(color, x, y, z1) : color;
              this.add(x, y, z1, c);
              const c2 = Array.isArray(color) ? pick(color, x, y, z2) : color;
              this.add(x, y, z2, c2);
            }
          }

          for (let y = y1; y <= y2; y++) {
            for (let z = z1; z <= z2; z++) {
              const c = Array.isArray(color) ? pick(color, x1, y, z) : color;
              this.add(x1, y, z, c);
              const c2 = Array.isArray(color) ? pick(color, x2, y, z) : color;
              this.add(x2, y, z, c2);
            }
          }
        }

        build(parent) {
          const matrix = new THREE.Matrix4();

          for (const [color, arr] of this.groups) {
            const count = arr.length / 3;
            if (!count) continue;

            const material = new THREE.MeshLambertMaterial({ color });
            const mesh = new THREE.InstancedMesh(voxelGeometry, material, count);

            for (let i = 0, p = 0; i < count; i++, p += 3) {
              matrix.makeTranslation(arr[p], arr[p + 1], arr[p + 2]);
              mesh.setMatrixAt(i, matrix);
            }

            mesh.instanceMatrix.needsUpdate = true;
            mesh.frustumCulled = false;
            parent.add(mesh);
          }
        }
      }

      class SimpleControls {
        constructor(camera, dom, target) {
          this.camera = camera;
          this.dom = dom;
          this.target = target.clone();

          this.spherical = new THREE.Spherical();
          this.sphericalDelta = new THREE.Spherical(0, 0, 0);

          const offset = new THREE.Vector3().subVectors(camera.position, this.target);
          this.spherical.setFromVector3(offset);

          this.down = false;
          this.button = 0;
          this.lastX = 0;
          this.lastY = 0;
          this.rotateSpeed = 0.005;
          this.minDistance = 14;
          this.maxDistance = 160;

          const onDown = (e) => {
            this.down = true;
            this.button = e.button || 0;
            this.lastX = e.clientX;
            this.lastY = e.clientY;
          };

          const onMove = (e) => {
            if (!this.down) return;

            const dx = e.clientX - this.lastX;
            const dy = e.clientY - this.lastY;
            this.lastX = e.clientX;
            this.lastY = e.clientY;

            if (this.button === 2 || e.shiftKey) {
              const panScale = this.spherical.radius * 0.0018;
              const panX = new THREE.Vector3().setFromMatrixColumn(this.camera.matrix, 0);
              const panY = new THREE.Vector3().setFromMatrixColumn(this.camera.matrix, 1);

              this.target.addScaledVector(panX, -dx * panScale);
              this.target.addScaledVector(panY, dy * panScale);
            } else {
              this.sphericalDelta.theta -= dx * this.rotateSpeed;
              this.sphericalDelta.phi -= dy * this.rotateSpeed;
            }
          };

          const onUp = () => {
            this.down = false;
          };

          dom.addEventListener('pointerdown', onDown);
          window.addEventListener('pointermove', onMove);
          window.addEventListener('pointerup', onUp);

          dom.addEventListener('wheel', (e) => {
            e.preventDefault();
            this.spherical.radius *= e.deltaY > 0 ? 1.08 : 0.92;
          }, { passive: false });

          dom.addEventListener('contextmenu', (e) => e.preventDefault());
        }

        update() {
          this.spherical.theta += this.sphericalDelta.theta;
          this.spherical.phi += this.sphericalDelta.phi;
          this.spherical.phi = Math.max(0.1, Math.min(Math.PI * 0.49, this.spherical.phi));
          this.spherical.radius = Math.max(this.minDistance, Math.min(this.maxDistance, this.spherical.radius));

          this.camera.position.setFromSpherical(this.spherical).add(this.target);
          this.camera.lookAt(this.target);

          this.sphericalDelta.theta *= 0.85;
          this.sphericalDelta.phi *= 0.85;
        }
      }

      // Scene
      const scene = new THREE.Scene();
      scene.background = new THREE.Color(0x9bd7ff);
      scene.fog = new THREE.Fog(0x9bd7ff, 95, 330);

      const camera = new THREE.PerspectiveCamera(
        52,
        window.innerWidth / window.innerHeight,
        0.1,
        1600
      );
      camera.position.set(44, 27, 46);

      const renderer = new THREE.WebGLRenderer({ antialias: true });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
      renderer.setSize(window.innerWidth, window.innerHeight);
      if (THREE.sRGBEncoding && renderer.outputEncoding !== undefined) {
        renderer.outputEncoding = THREE.sRGBEncoding;
      }
      document.body.appendChild(renderer.domElement);

      const cameraTarget = new THREE.Vector3(2, 10, 0);
      let controls;

      if (THREE.OrbitControls) {
        controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.target.copy(cameraTarget);
        controls.enableDamping = true;
        controls.dampingFactor = 0.06;
        controls.minDistance = 14;
        controls.maxDistance = 160;
        controls.maxPolarAngle = Math.PI * 0.49;
        controls.minPolarAngle = Math.PI * 0.07;
        controls.update();
      } else {
        controls = new SimpleControls(camera, renderer.domElement, cameraTarget);
        controls.update();
      }

      // Lights
      const hemi = new THREE.HemisphereLight(0xd8f4ff, 0x294122, 0.95);
      scene.add(hemi);

      const sun = new THREE.DirectionalLight(0xfff3cf, 1.25);
      sun.position.set(70, 95, 45);
      scene.add(sun);

      const fill = new THREE.DirectionalLight(0xc9e8ff, 0.35);
      fill.position.set(-60, 40, -35);
      scene.add(fill);

      // Water
      const waterGeometry = new THREE.PlaneGeometry(460, 460, 64, 64);
      const waterMaterial = new THREE.MeshStandardMaterial({
        color: 0x3285bb,
        roughness: 0.35,
        metalness: 0.02,
        flatShading: true,
        side: THREE.DoubleSide
      });
      const water = new THREE.Mesh(waterGeometry, waterMaterial);
      water.rotation.x = -Math.PI / 2;
      water.position.y = -0.05;
      scene.add(water);

      // Harbor
      const harbor = new THREE.Group();
      const hb = new VoxelBuilder();

      const grassPal = [0x4f8f3a, 0x5aa042, 0x457b2d, 0x66b24b];
      const sandPal = [0xdcc79c, 0xe7d4a8, 0xc9b37e];
      const dirtPal = [0x7d5738, 0x8a6242, 0x6b472d];
      const rockPal = [0x8f8f88, 0xa0a098, 0x767670];
      const stonePal = [0x9e9e9e, 0x8a8a8a, 0xb0b0b0];
      const woodPal = [0x8d5f37, 0x9f6b3e, 0x784e2d];
      const darkWoodPal = [0x4d3122, 0x5a3828, 0x3d2718];
      const cratePal = [0xb17f4d, 0x9a683b, 0xc28a55];
      const barrelPal = [0x7a4b2a, 0x915c33, 0x5f391f];
      const glassPal = [0x9fd6f5, 0xc4eaff, 0x86c8e8];
      const leafPal = [0x2f7030, 0x3f8f36, 0x276028, 0x4c9a3c];

      function addDock(b) {
        b.box(-20, 0, 3, 3, -6, 6, woodPal);

        for (let x = -18; x <= -4; x += 4) {
          for (let i = 0; i < 3; i++) {
            const z = [-6, 0, 6][i];
            b.box(x, x + 1, -1, 2, z, z, darkWoodPal);
          }
        }

        for (let x = -18; x <= 0; x += 4) {
          b.box(x, x, 4, 5, 6, 6, stonePal);
          b.box(x, x, 4, 5, -6, -6, stonePal);
        }
      }

      function addLand(b) {
        const cx = -22;
        const cz = 0;

        for (let x = -40; x <= -4; x++) {
          for (let z = -22; z <= 22; z++) {
            const dx = (x - cx) / 17;
            const dz = z / 21;
            const d = dx * dx + dz * dz;

            if (d > 1.07) continue;

            let h = 1;
            if (d < 0.45) h = 4;
            else if (d < 0.68) h = 3;
            else if (d < 0.88) h = 2;

            const beach = d > 0.72;

            for (let y = 0; y < h; y++) {
              let color;
              if (y === h - 1) {
                color = pick(beach ? sandPal : grassPal, x, y, z);
              } else if (y === 0) {
                color = pick(beach ? sandPal : rockPal, x, y, z);
              } else {
                color = pick(beach ? sandPal : dirtPal, x, y, z);
              }
              b.add(x, y, z, color);
            }
          }
        }
      }

      function addTree(b, x, z, height) {
        b.box(x, x, 4, 4 + height - 1, z, z, darkWoodPal);
        b.box(x - 2, x + 2, 4 + height, 4 + height + 1, z - 2, z + 2, leafPal);
        b.box(x - 1, x + 1, 4 + height + 2, 4 + height + 2, z - 1, z + 1, leafPal);
      }

      function addHouse(b, x, z, w, d, h, wall, roof) {
        b.walls(x, x + w - 1, 4, 4 + h - 1, z, z + d - 1, wall);
        b.box(x, x + w - 1, 4 + h, 4 + h, z, z + d - 1, wall);
        b.box(x - 1, x + w, 4 + h + 1, 4 + h + 1, z - 1, z + d, roof);

        const midZ = z + Math.floor(d / 2);

        // Door and windows facing the harbor (+x side)
        b.box(x + w, x + w, 4, 5, midZ, midZ, darkWoodPal);
        b.box(x + w, x + w, 5, 6, z, z, glassPal);
        b.box(x + w, x + w, 5, 6, z + d - 1, z + d - 1, glassPal);

        // Chimney
        b.box(x + w - 2, x + w - 2, 4 + h + 2, 4 + h + 4, z + 1, z + 1, darkWoodPal);
      }

      function addLighthouse(b, x, z) {
        b.box(x - 2, x + 2, 4, 4, z - 2, z + 2, stonePal);

        for (let y = 5; y <= 17; y++) {
          const red = Math.floor((y - 5) / 3) % 2 === 1;
          b.walls(x - 1, x + 1, y, y, z - 1, z + 1, red ? 0xd6514f : 0xf8f8f8);
        }

        b.box(x - 2, x + 2, 18, 18, z - 2, z + 2, darkWoodPal);
        b.box(x - 1, x + 1, 19, 20, z - 1, z + 1, [0xfff3b0, 0xffe47a]);
        b.box(x - 3, x + 3, 21, 21, z - 1, z + 1, darkWoodPal);
      }

      function addCrane(b) {
        const x = -13;
        const z = 4;

        b.box(x, x + 1, 4, 13, z, z, darkWoodPal);
        b.box(x - 2, x + 16, 14, 14, z, z, woodPal);
        b.box(x - 4, x - 4, 12, 14, z, z, woodPal);
        b.box(x + 16, x + 16, 12, 13, z, z, woodPal);

        // Cable and crate
        b.box(x + 14, x + 14, 10, 14, z, z, 0x3f2a1b);
        b.box(x + 12, x + 14, 8, 10, z, z, cratePal);
      }

      function addProps(b) {
        // Crates
        b.box(-19, -17, 4, 6, -5, -3, cratePal);
        b.box(-19, -17, 4, 5, 2, 4, cratePal);
        b.box(-9, -8, 4, 5, -5, -4, cratePal);
        b.box(-6, -5, 4, 4, 4, 5, cratePal);

        // Barrels
        b.box(-8, -7, 4, 5, 3, 4, barrelPal);
        b.box(-5, -4, 4, 5, -5, -4, barrelPal);
        b.box(-14, -13, 4, 5, -1, 0, barrelPal);

        // Tarps / market boxes
        b.box(-12, -11, 4, 4, 5, 6, [0x2b6c9a, 0x3a82b2]);

        // Flag near the dock
        b.box(-2, -2, 4, 9, 4, 4, darkWoodPal);
        b.box(-1, 1, 8, 9, 4, 4, [0xc83b3b, 0xe64f4f]);
      }

      // Harbor construction order matters: dock first so wood is not overbuilt by grass.
      addDock(hb);
      addLand(hb);
      addTree(hb, -28, -1, 2);
      addTree(hb, -23, 7, 3);
      addTree(hb, -22, -11, 2);
      addTree(hb, -26, -12, 3);

      addHouse(
        hb,
        -31, -5, 5, 4, 3,
        [0xd9bc98, 0xc9a87f, 0xe3c9a8],
        [0x94453d, 0x7d3b35]
      );
      addHouse(
        hb,
        -28, 5, 6, 5, 4,
        [0xc7a982, 0xb8966f, 0xd9c1a3],
        [0x566a71, 0x4a5b61]
      );
      addHouse(
        hb,
        -21, -3, 5, 4, 3,
        [0xe4d2b0, 0xd4c19a, 0xefdfc0],
        [0x7a453c, 0x8a5446]
      );

      addLighthouse(hb, -24, -10);
      addCrane(hb);
      addProps(hb);
      hb.build(harbor);
      scene.add(harbor);

      // Lighthouse lamp + light
      const lampGeo = new THREE.BoxGeometry(1.35, 1.35, 1.35);
      const lampMat = new THREE.MeshBasicMaterial({ color: 0xfff4b0 });
      const lamp = new THREE.Mesh(lampGeo, lampMat);
      lamp.position.set(-24, 20.6, -10);
      scene.add(lamp);

      const lampLight = new THREE.PointLight(0xffeaa0, 1.6, 120, 1);
      lampLight.position.copy(lamp.position);
      scene.add(lampLight);

      // Ship
      const shipGroup = new THREE.Group();
      const sb = new VoxelBuilder();

      const hullBottomPal = [0x2c1d14, 0x37251a];
      const hullDarkPal = [0x4b2f1d, 0x5a3721];
      const hullMidPal = [0x734728, 0x855331];
      const hullLightPal = [0x8c5a34, 0x9e673a];
      const deckPal = [0x9d6e42, 0xb07a47, 0x8b5a34];
      const mastPal = [0x6d4a2a, 0x7e5732];
      const sailPal = [0xf5ecd6, 0xe8d9b3, 0xfaf4e3];
      const goldPal = [0xd9b15a, 0xc9a048, 0xe6c276];
      const flagPal = [0xc83b3b, 0xe64f4f];
      const castlePal = [0x6d4a2a, 0x7d5532, 0x5c3a20];

      function addShip(b) {
        // Hull bottom / keel
        b.box(-7, 7, -2, -1, -1, 1, hullBottomPal);
        b.box(-11, 11, -1, -1, -2, 2, hullBottomPal);
        b.box(-13, 13, 0, 0, -3, 3, hullBottomPal);

        // Lower hull and trim line
        b.box(-13, 13, 1, 2, -4, 4, hullDarkPal);
        b.box(-14, 14, 3, 3, -5, 5, goldPal);

        // Upper hull
        b.walls(-14, 14, 4, 5, -5, 5, hullLightPal);

        // Main deck
        b.box(-13, 13, 6, 6, -4, 4, deckPal);

        // Bulwark around deck
        b.walls(-14, 14, 6, 7, -5, 5, hullDarkPal);

        // Forecastle
        b.walls(-14, -10, 8, 9, -4, 4, castlePal);
        b.box(-14, -10, 10, 10, -4, 4, castlePal);

        // Sterncastle
        b.walls(8, 14, 8, 11, -4, 4, castlePal);
        b.box(8, 14, 12, 12, -4, 4, castlePal);
        b.box(11, 14, 9, 11, -3, 3, castlePal);

        // Stern / bow decorations
        b.box(15, 15, 6, 9, 0, 0, goldPal);
        b.box(-15, -15, 6, 8, 0, 0, goldPal);

        // Bowsprit
        b.box(-17, -14, 7, 8, 0, 0, mastPal);
        b.box(-14, -13, 6, 6, -1, 1, mastPal);

        // Masts
        b.box(0, 0, 6, 30, 0, 0, mastPal);   // main
        b.box(-8, -8, 6, 22, 0, 0, mastPal); // fore
        b.box(8, 8, 6, 20, 0, 0, mastPal);   // mizzen

        function yardSail(x, yardY, bottomY, topY, halfWidth) {
          b.box(x - 1, x + 1, yardY, yardY, -halfWidth, halfWidth, mastPal);
          b.box(x, x, bottomY, topY, -halfWidth + 1, halfWidth - 1, sailPal);

          // Billow toward one side
          for (let y = bottomY; y <= topY; y++) {
            for (let z = -halfWidth + 2; z <= halfWidth - 2; z += 2) {
              b.box(x + 1, x + 1, y, y, z, z + 1, sailPal);
            }
          }
        }

        // Main sails
        yardSail(0, 12, 8, 11, 8);
        yardSail(0, 17, 13, 16, 6);
        yardSail(0, 22, 18, 21, 5);
        yardSail(0, 26, 23, 25, 4);
        yardSail(0, 30, 27, 29, 3);

        // Fore sails
        yardSail(-8, 12, 8, 11, 6);
        yardSail(-8, 16, 13, 15, 5);
        yardSail(-8, 20, 17, 19, 4);

        // Mizzen sails
        yardSail(8, 12, 9, 11, 5);
        yardSail(8, 16, 13, 15, 4);

        // Crow's nests
        b.box(-2, 2, 21, 22, -2, 2, deckPal);
        b.box(-9, -7, 17, 18, -1, 1, deckPal);
        b.box(7, 9, 14, 15, -1, 1, deckPal);

        // Flags
        b.box(-1, 0, 31, 32, -2, -1, flagPal);
        b.box(-9, -8, 23, 24, -2, -1, flagPal);
        b.box(8, 9, 21, 22, -2, -1, flagPal);
      }

      addShip(sb);
      sb.build(shipGroup);
      shipGroup.position.set(8, 0, 0);
      shipGroup.rotation.set(0, Math.PI / 2, 0);
      scene.add(shipGroup);

      // Clouds
      const clouds = [];

      function makeCloud(seed) {
        const b = new VoxelBuilder();
        const g = new THREE.Group();
        const cloudPal = [0xffffff, 0xf7fcff, 0xeaf6ff];

        for (let i = 0; i < 16; i++) {
          const ox = Math.floor(rand(seed + i * 3) * 14) - 7;
          const oy = Math.floor(rand(seed + i * 5) * 5) - 2;
          const oz = Math.floor(rand(seed + i * 7) * 10) - 5;
          const w = Math.floor(rand(seed + i * 11) * 4) + 2;
          const h = Math.floor(rand(seed + i * 13) * 2) + 1;
          const d = Math.floor(rand(seed + i * 17) * 4) + 2;

          b.box(ox, ox + w - 1, oy, oy + h - 1, oz, oz + d - 1, cloudPal);
        }

        b.build(g);
        return g;
      }

      const cloudPositions = [
        [-65, 38, -40],
        [-25, 44, 50],
        [25, 39, -55],
        [70, 46, 25],
        [-95, 42, 15],
        [10, 50, 75],
        [95, 37, -25],
        [-50, 54, 70]
      ];

      cloudPositions.forEach((p, i) => {
        const cloud = makeCloud(i * 17.3 + 1);
        cloud.position.set(p[0], p[1], p[2]);
        cloud.userData.speed = 0.5 + rand(i * 9.1) * 0.8;
        clouds.push(cloud);
        scene.add(cloud);
      });

      // Animation
      const clock = new THREE.Clock();
      let elapsed = 0;

      function animate() {
        requestAnimationFrame(animate);

        const dt = Math.min(clock.getDelta(), 0.05);
        elapsed += dt;

        // Animate water vertices
        const pos = waterGeometry.attributes.position;
        for (let i = 0; i < pos.count; i++) {
          const x = pos.getX(i);
          const y = pos.getY(i);
          const z =
            Math.sin(x * 0.07 + elapsed * 0.9) * 0.35 +
            Math.sin(y * 0.09 + elapsed * 0.7) * 0.28 +
            Math.cos((x * 0.04 + y * 0.05) + elapsed * 0.5) * 0.22;
          pos.setZ(i, z);
        }
        pos.needsUpdate = true;

        // Ship bobbing and gentle sway
        shipGroup.position.y =
          Math.sin(elapsed * 0.55) * 0.18 +
          Math.sin(elapsed * 1.3) * 0.04;

        shipGroup.rotation.set(
          Math.sin(elapsed * 0.38) * 0.010,
          Math.PI / 2 + Math.sin(elapsed * 0.18) * 0.008,
          Math.sin(elapsed * 0.52) * 0.014
        );

        // Cloud drift
        for (const cloud of clouds) {
          cloud.position.x += dt * cloud.userData.speed;
          if (cloud.position.x > 170) cloud.position.x = -170;
        }

        // Lamp flicker
        lampLight.intensity = 1.35 + Math.sin(elapsed * 3.0) * 0.18;
        lamp.material.color.setHSL(0.13, 0.55, 0.82 + Math.sin(elapsed * 2.2) * 0.02);

        controls.update();
        renderer.render(scene, camera);
      }

      animate();

      window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
      });
    })();
  </script>
</body>
</html>
```