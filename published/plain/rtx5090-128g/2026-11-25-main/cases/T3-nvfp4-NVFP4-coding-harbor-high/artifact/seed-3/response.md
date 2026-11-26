```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Voxel Scene — A Sailing Ship Calling at a Harbor</title>
  <style>
    html, body {
      margin: 0;
      height: 100%;
      overflow: hidden;
      background: #8fcfff;
    }
    canvas { display: block; }
    #ui {
      position: fixed;
      left: 14px;
      top: 12px;
      color: #fff;
      font: 13px/1.45 system-ui, -apple-system, Segoe UI, sans-serif;
      background: rgba(0, 0, 0, 0.35);
      padding: 9px 11px;
      border-radius: 10px;
      backdrop-filter: blur(4px);
      pointer-events: none;
      max-width: 330px;
    }
    #ui strong { font-size: 14px; }
  </style>

  <script type="importmap">
    {
      "imports": {
        "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
        "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
      }
    }
  </script>
</head>
<body>
  <div id="ui">
    <strong>A sailing ship calling at a harbor</strong><br />
    Drag: orbit &nbsp;•&nbsp; Scroll: zoom &nbsp;•&nbsp; Right-drag: pan
  </div>

  <script type="module">
    import * as THREE from 'three';
    import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

    /* ---------------- Scene, camera, renderer ---------------- */

    const scene = new THREE.Scene();
    scene.fog = new THREE.Fog(0xb7dcf7, 190, 430);

    const camera = new THREE.PerspectiveCamera(
      50,
      window.innerWidth / window.innerHeight,
      1,
      1000
    );
    camera.position.set(76, 56, 96);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.06;
    document.body.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.target.set(-8, 14, 4);
    controls.enableDamping = true;
    controls.dampingFactor = 0.055;
    controls.minDistance = 35;
    controls.maxDistance = 330;
    controls.maxPolarAngle = Math.PI * 0.49;
    controls.autoRotate = true;
    controls.autoRotateSpeed = 0.38;

    const stopAutoRotate = () => { controls.autoRotate = false; };
    renderer.domElement.addEventListener('pointerdown', stopAutoRotate, { once: true });
    renderer.domElement.addEventListener('wheel', stopAutoRotate, { once: true });

    window.addEventListener('resize', () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    });

    /* ---------------- Sky ---------------- */

    scene.background = new THREE.Color(0xcfeeff);

    const skyMesh = new THREE.Mesh(
      new THREE.SphereGeometry(500, 24, 16),
      new THREE.ShaderMaterial({
        side: THREE.BackSide,
        fog: false,
        depthWrite: false,
        uniforms: {
          top: { value: new THREE.Color(0x174f9b) },
          bottom: { value: new THREE.Color(0xdff3ff) }
        },
        vertexShader: `
          varying vec3 vPos;
          void main() {
            vPos = position;
            gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
          }
        `,
        fragmentShader: `
          varying vec3 vPos;
          uniform vec3 top;
          uniform vec3 bottom;
          void main() {
            float h = normalize(vPos).y * 0.5 + 0.5;
            float t = smoothstep(0.45, 0.85, h);
            gl_FragColor = vec4(mix(bottom, top, t), 1.0);
          }
        `
      })
    );
    skyMesh.renderOrder = -1000;
    scene.add(skyMesh);

    const sun = new THREE.Mesh(
      new THREE.SphereGeometry(26, 16, 8),
      new THREE.MeshBasicMaterial({ color: 0xfff4c8, fog: false })
    );
    sun.position.set(180, 160, -200);
    scene.add(sun);

    /* ---------------- Lights ---------------- */

    const hemi = new THREE.HemisphereLight(0xcfefff, 0x455a3b, 0.55);
    scene.add(hemi);

    const ambient = new THREE.AmbientLight(0xffffff, 0.16);
    scene.add(ambient);

    const dir = new THREE.DirectionalLight(0xfff2cf, 1.9);
    dir.position.set(180, 170, -210);
    scene.add(dir);

    /* ---------------- Voxel helpers ---------------- */

    const staticMap = new Map();

    function makeVoxelGeometry(sizeX = 1, sizeY = 1, sizeZ = 1) {
      const g = new THREE.BoxGeometry(sizeX, sizeY, sizeZ);
      const count = g.attributes.position.count;
      const colors = new Float32Array(count * 3);
      colors.fill(1);
      g.setAttribute('color', new THREE.BufferAttribute(colors, 3));
      return g;
    }

    function shade(hex, deltaL) {
      return new THREE.Color(hex).offsetHSL(0, 0, deltaL);
    }

    function voxel(x, y, z, color) {
      const ix = Math.round(x);
      const iy = Math.round(y);
      const iz = Math.round(z);
      const key = ix + ',' + iy + ',' + iz;
      staticMap.set(key, color instanceof THREE.Color ? color : new THREE.Color(color));
    }

    function box(x1, y1, z1, x2, y2, z2, color) {
      const minx = Math.min(Math.round(x1), Math.round(x2));
      const maxx = Math.max(Math.round(x1), Math.round(x2));
      const miny = Math.min(Math.round(y1), Math.round(y2));
      const maxy = Math.max(Math.round(y1), Math.round(y2));
      const minz = Math.min(Math.round(z1), Math.round(z2));
      const maxz = Math.max(Math.round(z1), Math.round(z2));

      for (let x = minx; x <= maxx; x++) {
        for (let y = miny; y <= maxy; y++) {
          for (let z = minz; z <= maxz; z++) {
            voxel(x, y, z, color);
          }
        }
      }
    }

    /* ---------------- Land & harbor ---------------- */

    function buildLand() {
      for (let x = -120; x <= -52; x++) {
        for (let z = -60; z <= 90; z++) {
          let c = 0x5c8847;

          if (x > -57) c = 0xc9bb90;

          const n =
            Math.sin(x * 0.23 + z * 0.17) +
            Math.sin(x * 0.71 - z * 0.53) * 0.5;

          if (n > 0.9) c = shade(c, 0.05);
          else if (n < -1.0) c = shade(c, -0.05);

          voxel(x, 1, z, c);
        }
      }
    }

    function addCrate(x, z, s) {
      const base = 2;
      for (let y = 0; y < s; y++) {
        for (let xi = 0; xi < s; xi++) {
          for (let zi = 0; zi < s; zi++) {
            const outer =
              y === 0 || y === s - 1 ||
              xi === 0 || xi === s - 1 ||
              zi === 0 || zi === s - 1;

            let c = outer
              ? ((xi + zi + y) % 2 === 0 ? 0x9c6f41 : 0x7a5634)
              : 0x64462c;

            if (outer && (xi + y + zi) % 5 === 0) c = shade(c, -0.04);

            voxel(x + xi, base + y, z + zi, c);
          }
        }
      }
    }

    function addBarrel(x, z) {
      for (let y = 2; y <= 3; y++) {
        for (let xi = 0; xi <= 1; xi++) {
          for (let zi = 0; zi <= 1; zi++) {
            const c = (xi === 0 || zi === 0) ? 0x6b4527 : 0x865931;
            voxel(x + xi, y, z + zi, c);
          }
        }
      }
    }

    function addPier(z1, z2) {
      for (let x = -41; x <= -28; x++) {
        for (let z = z1; z <= z2; z++) {
          let c = (z % 2 === 0) ? 0x8f6d47 : 0x785838;
          if ((x + z) % 9 === 0) c = 0x5b422b;

          voxel(x, 1, z, c);

          if (z === z1 || z === z2) {
            voxel(x, 0, z, 0x4b3524);
          }
        }
      }

      for (let z = z1; z <= z2; z += 2) {
        voxel(-28, 0, z, 0x3e2a1c);
        voxel(-28, 1, z, 0x3e2a1c);
      }
    }

    function addWarehouse(x, z, w, d, h, wall = 0xa85a47) {
      const roof = 0x484e57;

      for (let xi = 0; xi < w; xi++) {
        for (let zi = 0; zi < d; zi++) {
          for (let yi = 0; yi < h; yi++) {
            let c = wall;

            if (xi === w - 1) {
              if ((yi === 3 || yi === 4) && (zi === 3 || zi === 7 || zi === d - 4)) {
                c = shade(0x385c75, -0.02);
              }

              if (yi < 3 && zi >= Math.floor(d / 2) - 2 && zi <= Math.floor(d / 2) + 1) {
                c = shade(0x4d2f20, 0);
              }
            }

            if (xi === 0 && yi === 4 && zi === Math.floor(d / 2)) {
              c = shade(0x35566d, 0);
            }

            voxel(x + xi, 2 + yi, z + zi, c);
          }
        }
      }

      const roofBase = 2 + h;
      const roofH = Math.floor(d / 2);

      for (let r = 0; r <= roofH; r++) {
        const y = roofBase + r;

        for (let xi = -1; xi <= w; xi++) {
          const c = (r % 2 === 0) ? roof : shade(roof, -0.04);

          voxel(x + xi, y, z + r, c);
          voxel(x + xi, y, z + d - 1 - r, c);
        }
      }
    }

    function addHouse(x, z, w, d, h, wall, roof) {
      for (let xi = 0; xi < w; xi++) {
        for (let zi = 0; zi < d; zi++) {
          for (let yi = 0; yi < h; yi++) {
            let c = wall;

            if (xi === w - 1) {
              if (yi === 3 && (zi === 2 || zi === 5 || zi === d - 3)) {
                c = shade(0x355970, -0.02);
              }

              if (yi < 3 && zi >= Math.floor(d / 2) - 1 && zi <= Math.floor(d / 2) + 1) {
                c = shade(0x4a2c1f, 0);
              }
            }

            if (xi === 0 && yi === 3 && zi === Math.floor(d / 2)) {
              c = shade(0x355970, -0.02);
            }

            voxel(x + xi, 2 + yi, z + zi, c);
          }
        }
      }

      const roofBase = 2 + h;
      const roofH = Math.floor(d / 2);

      for (let r = 0; r <= roofH; r++) {
        const y = roofBase + r;

        for (let xi = -1; xi <= w; xi++) {
          const c = (r % 2 === 0) ? roof : shade(roof, -0.04);

          voxel(x + xi, y, z + r, c);
          voxel(x + xi, y, z + d - 1 - r, c);
        }
      }

      voxel(x + w - 2, roofBase + roofH + 1, z + 1, 0x4d3b36);
    }

    function addCrane(x, z) {
      for (let y = 2; y <= 7; y++) {
        voxel(x, y, z, 0x825e3b);
        voxel(x + 1, y, z, 0x825e3b);
        voxel(x, y, z + 1, 0x825e3b);
        voxel(x + 1, y, z + 1, 0x825e3b);
      }

      box(x - 1, 7, z - 1, x + 2, 7, z + 2, 0x9a784e);

      for (let i = 0; i <= 10; i++) {
        voxel(x + i, 8, z + 1, 0x8e6b42);
      }

      box(x + 9, 7, z + 1, x + 9, 8, z + 1, 0x5c432b);

      for (let y = 4; y <= 7; y++) {
        voxel(x + 7, y, z + 1, 0x3b3b3b);
      }

      addCrate(x + 6, z, 2);
    }

    function buildLighthouse() {
      for (let x = -96; x <= -56; x++) {
        for (let z = 38; z <= 58; z++) {
          const dx = (x + 76) / 20;
          const dz = (z - 48) / 10;

          if (dx * dx + dz * dz < 1) {
            voxel(x, 0, z, 0x555b64);
            if (Math.sin(x * 0.7 + z * 0.6) > -0.25) {
              voxel(x, 1, z, 0x737881);
            }
          }
        }
      }

      box(-88, 2, 45, -82, 4, 51, 0x89919a);

      const cx = -85;
      const cz = 48;

      for (let y = 5; y <= 19; y++) {
        const r = 2.15 + (19 - y) * 0.02;

        for (let dx = -3; dx <= 3; dx++) {
          for (let dz = -3; dz <= 3; dz++) {
            if (dx * dx + dz * dz <= r * r + 0.3) {
              const c = (y % 4 < 2) ? 0xd63d3d : 0xf5f0e6;
              voxel(cx + dx, y, cz + dz, c);
            }
          }
        }
      }

      box(cx - 2, 20, cz - 2, cx + 2, 21, cz + 2, 0x2e3440);
      voxel(cx, 20, cz, 0xffe69b);
      voxel(cx, 21, cz, 0xfff3c4);

      for (let z = -3; z < 0; z++) {
        voxel(cx + 3, 22, z, 0xd23c3c);
      }
    }

    function buildHarbor() {
      buildLand();

      // Cobblestone quay
      for (let z = -62; z <= 92; z++) {
        for (let x = -51; x <= -42; x++) {
          let c = ((x + z) & 1) ? 0x9aa0a8 : 0x7f838a;

          if (((x * 3 + z * 5) % 23) === 0) c = 0x656b75;

          voxel(x, 1, z, c);
        }
      }

      // Quay sea wall
      for (let z = -62; z <= 92; z++) {
        voxel(-42, 0, z, 0x555a63);
        voxel(-42, 1, z, 0x4e535c);
      }

      // Wooden piers
      addPier(10, 13);
      addPier(-11, -8);

      // Bollards
      for (let z = -18; z <= 72; z += 12) {
        voxel(-44, 2, z, 0x2f333a);
        voxel(-44, 3, z, 0xb03434);
      }

      // Lamp posts
      for (let z = -15; z <= 70; z += 18) {
        for (let y = 2; y <= 6; y++) {
          voxel(-48, y, z, 0x2f2c2c);
        }
        voxel(-48, 7, z, 0x595050);
        voxel(-47, 7, z, 0xf7d57d);
      }

      // Cargo and barrels
      addCrate(-48, -18, 3);
      addCrate(-46, -12, 2);
      addCrate(-49, 18, 3);
      addCrate(-45, 24, 2);
      addCrate(-50, 54, 4);
      addCrate(-47, 60, 2);

      addBarrel(-45, 30);
      addBarrel(-48, 34);
      addBarrel(-44, 66);
      addBarrel(-49, 70);

      // Buildings
      addWarehouse(-66, -6, 12, 10, 5);
      addWarehouse(-66, 30, 10, 8, 4, 0xb75f4d);

      addHouse(-105, -30, 8, 8, 4, 0xd9bd92, 0x8a4c3f);
      addHouse(-96, -35, 7, 7, 4, 0xa7c7c6, 0x4b5e56);
      addHouse(-103, 12, 9, 8, 5, 0xd8c3a7, 0x743e33);
      addHouse(-112, 48, 8, 8, 4, 0xb8cbd2, 0x385f4b);
      addHouse(-96, 58, 7, 7, 4, 0xe2d3b7, 0x6f3f3f);

      // Harbor crane
      addCrane(-46, -35);

      // Lighthouse / breakwater
      buildLighthouse();
    }

    /* ---------------- Ship ---------------- */

    function shipHalfWidth(x) {
      const minX = -25;
      const maxX = 25;
      const t = (x - minX) / (maxX - minX);
      const s = Math.sin(Math.PI * t);

      if (s <= 0) return 0;

      return Math.max(0, Math.round(7 * Math.pow(s, 0.82)));
    }

    function addSail(x, yardY, len, drop) {
      for (let z = -len; z <= len; z++) {
        voxel(x, yardY, z, 0x4a3524);
      }

      const startY = yardY - drop;

      for (let y = startY; y < yardY; y++) {
        const rowT = (y - startY) / Math.max(1, drop - 1);
        const l = Math.max(1, Math.round(len * (0.82 + Math.sin(rowT * Math.PI) * 0.18)));

        for (let z = -l; z <= l; z++) {
          let c = (y & 1) ? 0xf3ecdb : 0xe5dcc7;

          if (Math.abs(z) === l) c = 0xc8bfae;
          if (y === startY) c = 0xb5aa96;
          if ((z - x + y) % 11 === 0) c = shade(c, -0.03);

          voxel(x, y, z, c);
        }
      }
    }

    function addMast(x, top, yards, flagColor = 0xc73636) {
      for (let y = 6; y <= top; y++) {
        voxel(x, y, 0, (y & 1) ? 0x5b4a34 : 0x725b41);
      }

      for (let z = -2; z <= 2; z++) {
        voxel(x, top - 3, z, 0x4b3a29);
      }

      for (const [yardY, len, drop] of yards) {
        addSail(x, yardY, len, drop);
      }

      for (let z = -3; z < 0; z++) {
        voxel(x, top + 1, z, flagColor);
        voxel(x, top + 2, z, 0xffffff);
      }
    }

    function addShipCabin(x1, z1, x2, z2, y1, y2, base) {
      for (let x = Math.round(x1); x <= Math.round(x2); x++) {
        for (let z = Math.round(z1); z <= Math.round(z2); z++) {
          for (let y = Math.round(y1); y <= Math.round(y2); y++) {
            let c = base;
            const edge = (x === Math.round(x1) || x === Math.round(x2) || z === Math.round(z1) || z === Math.round(z2));

            if (edge && ((x + z + y) % 5 === 0)) {
              c = shade(0x335b78, 0);
            }

            if (edge && ((x + y) % 7 === 0)) {
              c = shade(0x24313c, 0);
            }

            voxel(x, y, z, c);
          }
        }
      }
    }

    function addBowsprit() {
      for (let i = 0; i <= 20; i++) {
        const x = -25 - i;
        const y = Math.round(7 + i * 0.05);
        voxel(x, y, 0, 0x5b4631);
      }

      box(-36, 5, -3, -25, 7, 3, 0xece3d0);
    }

    function addShip() {
      const minX = -25;
      const maxX = 25;

      const hullColors = [
        0x2c1a12,
        0x4b2f1d,
        0x5d3c25,
        0x7b5836
      ];

      const shrinks = [2.5, 1.6, 0.7, 0];

      for (let x = minX; x <= maxX; x++) {
        const half = shipHalfWidth(x);

        for (let y = 2; y <= 5; y++) {
          const hw = Math.max(0, Math.round(half - shrinks[y - 2]));

          let c = hullColors[y - 2];

          if (y === 5 && ((x + z) & 3) === 0) {
            c = shade(c, 0.05);
          } else if (y < 5 && Math.abs(z) === hw) {
            c = shade(c, -0.04);
          }

          for (let z = -hw; z <= hw; z++) {
            let cc = c;

            if (y === 5 && ((x + z) & 3) === 0) cc = shade(c, 0.05);
            else if (y < 5 && Math.abs(z) === hw) cc = shade(c, -0.04);

            voxel(x, y, z, cc);
          }
        }

        if (half > 5 && x % 5 === 0) {
          const hw = Math.max(0, Math.round(half - shrinks[1]));
          voxel(x, 3, hw, 0x160e08);
          voxel(x, 3, -hw, 0x160e08);
        }

        if (x <= minX + 1 || x >= maxX - 1) {
          for (let y = 2; y <= 6; y++) {
            voxel(x, y, 0, 0x25160f);
          }
        }
      }

      // Bulwarks
      for (let x = -23; x <= 23; x++) {
        const half = shipHalfWidth(x);
        if (half <= 0) continue;

        for (let z = -half; z <= half; z++) {
          if (Math.abs(z) === half || x === -23 || x === 23) {
            voxel(x, 6, z, 0x4b3120);
          }
        }
      }

      // Cabins
      addShipCabin(10, -4, 22, 4, 6, 8, 0x6d4e2e);
      addShipCabin(-19, -2, -13, 2, 6, 7, 0x6d4e2e);

      // Masts and square sails
      addMast(-14, 27, [
        [11, 10, 4],
        [17, 8, 4],
        [23, 6, 3],
        [28, 4, 2]
      ]);

      addMast(-2, 33, [
        [12, 14, 5],
        [20, 12, 4],
        [26, 9, 4],
        [31, 6, 3]
      ]);

      addMast(12, 27, [
        [11, 9, 4],
        [18, 7, 4],
        [24, 5, 3]
      ]);

      addBowsprit();
    }

    function addWake() {
      for (let x = -30; x <= 30; x++) {
        const half = shipHalfWidth(x);
        const edge = half === 0 ? 2 : half + 2;

        voxel(x, 0, edge, 0xf3f9ff);
        voxel(x, 0, -edge, 0xf3f9ff);
      }

      for (let z = -7; z <= 7; z++) {
        voxel(-31, 0, z, 0xf3f9ff);
        voxel(31, 0, z, 0xf3f9ff);
      }
    }

    /* ---------------- Clouds ---------------- */

    function addClouds() {
      const clouds = [
        [-80, 42, -70, 10, 5],
        [30, 46, -100, 14, 6],
        [100, 40, 50, 12, 5],
        [-40, 50, 80, 16, 5],
        [70, 52, -50, 13, 6],
        [-110, 48, 20, 10, 4]
      ];

      for (const cloud of clouds) {
        const [cx, cy, cz, w, d] = cloud;

        for (let xi = 0; xi < w; xi++) {
          for (let zi = 0; zi < d; zi++) {
            for (let yi = 0; yi < 3; yi++) {
              const nx = (xi - (w - 1) / 2) / (w / 2);
              const nz = (zi - (d - 1) / 2) / (d / 2);

              const dist =
                nx * nx +
                nz * nz +
                yi * yi * 0.18 +
                Math.sin(xi * 0.7 + zi * 1.2) * 0.12;

              if (dist < 1.05) {
                const c =
                  yi === 2
                    ? 0xffffff
                    : (Math.sin(xi * 0.7 + zi * 0.9) > 0 ? 0xf3f8ff : 0xdfe9f6);

                voxel(cx + xi, cy + yi, cz + zi, c);
              }
            }
          }
        }
      }
    }

    /* ---------------- Build static voxel mesh ---------------- */

    buildHarbor();
    addShip();
    addWake();
    addClouds();

    const staticGeo = makeVoxelGeometry(1, 1, 1);
    const staticMat = new THREE.MeshStandardMaterial({
      roughness: 0.9,
      metalness: 0,
      vertexColors: true,
      flatShading: true
    });

    const staticMesh = new THREE.InstancedMesh(staticGeo, staticMat, staticMap.size);
    staticMesh.frustumCulled = false;

    const matrix = new THREE.Matrix4();
    let staticIndex = 0;

    for (const entry of staticMap) {
      const parts = entry[0].split(',');

      matrix.makeTranslation(
        Number(parts[0]),
        Number(parts[1]),
        Number(parts[2])
      );

      staticMesh.setMatrixAt(staticIndex, matrix);
      staticMesh.setColorAt(staticIndex, entry[1]);
      staticIndex++;
    }

    staticMesh.instanceColor.needsUpdate = true;
    scene.add(staticMesh);

    /* ---------------- Animated water ---------------- */

    const waterGeo = makeVoxelGeometry(3, 1, 3);
    const waterMat = new THREE.MeshStandardMaterial({
      roughness: 0.25,
      metalness: 0.05,
      vertexColors: true,
      flatShading: true
    });

    const waterData = [];
    const waterCount = 84;

    for (let ix = 0; ix < waterCount; ix++) {
      for (let iz = 0; iz < waterCount; iz++) {
        const x = -126.5 + ix * 3;
        const z = -126.5 + iz * 3;

        waterData.push({ x, z });
      }
    }

    const waterMesh = new THREE.InstancedMesh(waterGeo, waterMat, waterData.length);
    waterMesh.frustumCulled = false;

    const waterMatrix = new THREE.Matrix4();

    for (let i = 0; i < waterData.length; i++) {
      const { x, z } = waterData[i];

      waterMatrix.makeTranslation(x, -0.2, z);
      waterMesh.setMatrixAt(i, waterMatrix);

      const c = new THREE.Color().setHSL(
        0.55 + Math.sin(x * 0.07 + z * 0.04) * 0.012,
        0.5,
        0.33 + Math.sin(x * 0.13 - z * 0.09) * 0.025
      );

      waterMesh.setColorAt(i, c);
    }

    waterMesh.instanceMatrix.needsUpdate = true;
    waterMesh.instanceColor.needsUpdate = true;
    scene.add(waterMesh);

    function updateWater(time) {
      for (let i = 0; i < waterData.length; i++) {
        const { x, z } = waterData[i];

        const y =
          -0.20 +
          Math.sin(x * 0.07 + z * 0.05 + time * 0.7) * 0.12 +
          Math.sin(x * 0.18 - z * 0.13 + time * 1.1) * 0.06;

        waterMatrix.makeTranslation(x, y, z);
        waterMesh.setMatrixAt(i, waterMatrix);
      }

      waterMesh.instanceMatrix.needsUpdate = true;
    }

    /* ---------------- Render loop ---------------- */

    function animate(timestamp) {
      const t = timestamp * 0.001;

      controls.update();
      updateWater(t);
      renderer.render(scene, camera);
    }

    renderer.setAnimationLoop(animate);
  </script>
</body>
</html>
```