Here is a complete single-file HTML voxel scene. Save it as something like `harbor-ship.html` and open it in Chrome.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Voxel Harbor Ship</title>
<style>
  html, body {
    margin: 0;
    height: 100%;
    overflow: hidden;
    background: #8bc9ef;
  }
  #ui {
    position: fixed;
    left: 14px;
    top: 14px;
    color: #fff;
    font: 13px/1.4 system-ui, sans-serif;
    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.75);
    pointer-events: none;
    user-select: none;
  }
  #ui b {
    font-size: 18px;
    letter-spacing: 0.03em;
  }
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
  <b>A sailing ship calling at a harbor</b><br />
  Drag to orbit • Scroll to zoom • Right-drag to pan
</div>

<script type="module">
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

const COL = {
  grass: 0x5fa95c,
  grassDark: 0x447f47,
  sand: 0xe3c98d,
  dockWood: 0x8c5b37,
  pierPlank: 0xb88457,
  dockDark: 0x624025,
  hullDark: 0x40261a,
  hullSide: 0x7a4628,
  deck: 0xd7a869,
  sail: 0xf4eedd,
  mast: 0x6b452b,
  yard: 0x4f311f,
  stone: 0x9aa2aa,
  stoneDark: 0x6b747c,
  wallCream: 0xd9c59b,
  wallRed: 0xb34a3f,
  roofBlue: 0x2d5f8a,
  roofBrown: 0x6d4327,
  crate: 0xc0884f,
  lampYellow: 0xffe384,
  flagRed: 0xd8433c,
  white: 0xf6f7f4,
  black: 0x1d1b1a,
  gold: 0xcfaa52,
  lighthouseWhite: 0xf3f1e5,
  lighthouseRed: 0xc94a46,
  galleryDark: 0x43332c
};

function hash2(x, z) {
  const s = Math.sin(x * 127.1 + z * 311.7) * 43758.5453123;
  return s - Math.floor(s);
}

class Builder {
  constructor() {
    this.blocks = [];
  }

  add(x, y, z, color, sx = 1, sy = 1, sz = 1) {
    this.blocks.push({ x, y, z, sx, sy, sz, color });
  }

  build(material) {
    if (this.blocks.length === 0) return new THREE.Group();

    const geometry = new THREE.BoxGeometry(1, 1, 1);
    const mesh = new THREE.InstancedMesh(geometry, material, this.blocks.length);
    const dummy = new THREE.Object3D();
    const color = new THREE.Color();

    for (let i = 0; i < this.blocks.length; i++) {
      const b = this.blocks[i];

      dummy.position.set(b.x, b.y, b.z);
      dummy.scale.set(b.sx, b.sy, b.sz);
      dummy.rotation.set(0, 0, 0);
      dummy.updateMatrix();

      mesh.setMatrixAt(i, dummy.matrix);
      color.set(b.color);
      mesh.setColorAt(i, color);
    }

    mesh.instanceMatrix.needsUpdate = true;
    if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
    mesh.castShadow = true;
    mesh.receiveShadow = true;

    return mesh;
  }
}

/* Renderer, scene, camera, lights */
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x8cc9ef);
scene.fog = new THREE.Fog(0x8cc9ef, 55, 165);

const camera = new THREE.PerspectiveCamera(
  45,
  window.innerWidth / window.innerHeight,
  0.1,
  600
);
camera.position.set(22, 16, 28);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 4, 4);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.minDistance = 6;
controls.maxDistance = 90;
controls.maxPolarAngle = Math.PI / 2 - 0.03;
controls.update();

const hemi = new THREE.HemisphereLight(0xbde6ff, 0x2d5b43, 0.9);
scene.add(hemi);

const sun = new THREE.DirectionalLight(0xfff3c8, 2.0);
sun.position.set(42, 55, -28);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -70;
sun.shadow.camera.right = 70;
sun.shadow.camera.top = 70;
sun.shadow.camera.bottom = -70;
sun.shadow.camera.near = 1;
sun.shadow.camera.far = 220;
sun.shadow.bias = -0.0005;
sun.shadow.normalBias = 0.03;
scene.add(sun);

const fill = new THREE.DirectionalLight(0x8ab4ff, 0.45);
fill.position.set(-30, 20, 20);
scene.add(fill);

/* Deep ocean base plane */
const ocean = new THREE.Mesh(
  new THREE.PlaneGeometry(420, 420),
  new THREE.MeshStandardMaterial({
    color: 0x1e5e90,
    roughness: 0.35,
    metalness: 0.05
  })
);
ocean.rotation.x = -Math.PI / 2;
ocean.position.y = -1.0;
ocean.receiveShadow = true;
scene.add(ocean);

/* Harbor voxels */
const harbor = new Builder();

function buildLand() {
  for (let x = -16; x <= -8; x++) {
    for (let z = -14; z <= 14; z++) {
      const lowerColor = x >= -10 ? COL.sand : COL.grassDark;
      harbor.add(x, 0, z, lowerColor);

      if (x === -8) {
        if (Math.abs(z) <= 6 && Math.abs(z) > 1) {
          harbor.add(x, 1, z, COL.stone);
        } else if (Math.abs(z) <= 10 && Math.abs(z) > 1) {
          harbor.add(x, 1, z, COL.sand);
        } else if (Math.abs(z) > 10) {
          harbor.add(
            x,
            1,
            z,
            hash2(x, z) > 0.62 ? COL.grassDark : COL.grass
          );
        }
      } else if (x >= -10) {
        harbor.add(x, 1, z, Math.abs(z) <= 6 ? COL.stone : COL.sand);
      } else {
        harbor.add(
          x,
          1,
          z,
          hash2(x, z) > 0.62 ? COL.grassDark : COL.grass
        );
      }
    }
  }
}

function buildPier() {
  for (let x = -8; x <= 6; x++) {
    for (let z = -1; z <= 1; z++) {
      harbor.add(x, 1, z, (x + z) & 1 ? COL.dockWood : COL.pierPlank);
    }
  }

  for (let x = -7; x <= 6; x++) {
    harbor.add(x, 1, -2, COL.dockDark);
  }

  for (let x = -7; x <= 6; x += 2) {
    harbor.add(x, 0, -1, COL.dockDark);
    harbor.add(x, 0, 1, COL.dockDark);
  }
}

function addBuilding(x0, z0, w, d, h, wallColor, roofColor) {
  for (let y = 2; y <= h; y++) {
    for (let x = x0; x < x0 + w; x++) {
      for (let z = z0; z < z0 + d; z++) {
        harbor.add(x, y, z, wallColor);
      }
    }
  }

  for (let x = x0; x < x0 + w; x++) {
    for (let z = z0; z < z0 + d; z++) {
      harbor.add(x, h + 1, z, roofColor);
    }
  }
}

function addDoor(x, z) {
  harbor.add(x, 2, z, COL.black);
  harbor.add(x, 3, z, COL.black);
}

function addWindow(x, z, y = 3) {
  harbor.add(x, y, z, COL.white);
}

function addCrate(x, z, size = 1) {
  for (let y = 2; y < 2 + size; y++) {
    for (let dx = 0; dx < size; dx++) {
      for (let dz = 0; dz < size; dz++) {
        harbor.add(
          x + dx,
          y,
          z + dz,
          (dx + dz + y) & 1 ? COL.dockDark : COL.crate
        );
      }
    }
  }
}

function addLighthouse(cx, cz) {
  for (let y = 2; y <= 3; y++) {
    for (let dx = -2; dx <= 2; dx++) {
      for (let dz = -2; dz <= 2; dz++) {
        harbor.add(cx + dx, y, cz + dz, COL.stone);
      }
    }
  }

  for (let y = 4; y <= 9; y++) {
    const c = y % 2 === 0 ? COL.lighthouseWhite : COL.lighthouseRed;
    for (let dx = -1; dx <= 1; dx++) {
      for (let dz = -1; dz <= 1; dz++) {
        harbor.add(cx + dx, y, cz + dz, c);
      }
    }
  }

  for (let dx = -1; dx <= 1; dx++) {
    for (let dz = -1; dz <= 1; dz++) {
      harbor.add(cx + dx, 10, cz + dz, COL.galleryDark);
    }
  }

  harbor.add(cx, 11, cz, COL.lampYellow);
  harbor.add(cx, 12, cz, COL.black);
}

function addTree(x, z) {
  for (let y = 2; y <= 4; y++) {
    harbor.add(x, y, z, COL.mast);
  }

  for (let y = 5; y <= 6; y++) {
    for (let dx = -1; dx <= 1; dx++) {
      for (let dz = -1; dz <= 1; dz++) {
        harbor.add(
          x + dx,
          y,
          z + dz,
          hash2(x + dx, z + dz) > 0.5 ? COL.grass : COL.grassDark
        );
      }
    }
  }

  harbor.add(x, 7, z, COL.grassDark);
}

function addDockLamp(x, z) {
  for (let y = 2; y <= 4; y++) {
    harbor.add(x, y, z, COL.dockDark);
  }
  harbor.add(x, 5, z, COL.lampYellow);
}

function buildHarbor() {
  buildLand();
  buildPier();

  addBuilding(-13, -7, 6, 4, 5, COL.wallCream, COL.roofBlue);
  addBuilding(-13, 3, 5, 4, 4, COL.wallRed, COL.roofBrown);

  addDoor(-8 + 0.1, -5);
  addWindow(-8 + 0.1, -7);
  addWindow(-8 + 0.1, -4);

  addDoor(-9 + 0.1, 4);
  addWindow(-9 + 0.1, 3);
  addWindow(-9 + 0.1, 6);

  addCrate(-11, -2, 1);
  addCrate(-12, -3, 2);
  addCrate(-10, 1, 1);
  addCrate(-4, 0, 1);
  addCrate(2, 0, 1);
  addCrate(4, 0, 1);

  addLighthouse(-12, -11);

  addTree(-15, -6);
  addTree(-14, 8);
  addTree(-15, 12);
  addTree(-16, 2);

  addDockLamp(-5, -1);
  addDockLamp(1, -1);
  addDockLamp(5, -1);
}

buildHarbor();

const harborMesh = harbor.build(
  new THREE.MeshStandardMaterial({
    roughness: 0.9,
    metalness: 0.0
  })
);
scene.add(harborMesh);

/* Animated voxel water */
const waterCells = [];
const waterStep = 2;

for (let x = -30; x <= 70; x += waterStep) {
  for (let z = -40; z <= 40; z += waterStep) {
    if (x < -8.5) continue;

    waterCells.push({
      x,
      z,
      size: waterStep,
      phase: hash2(x, z) * Math.PI * 2
    });
  }
}

const waterMaterial = new THREE.MeshStandardMaterial({
  roughness: 0.25,
  metalness: 0.05
});

const water = new THREE.InstancedMesh(
  new THREE.BoxGeometry(1, 1, 1),
  waterMaterial,
  waterCells.length
);
water.castShadow = false;
water.receiveShadow = true;

const dummy = new THREE.Object3D();
const tempColor = new THREE.Color();

for (let i = 0; i < waterCells.length; i++) {
  const c = waterCells[i];

  dummy.position.set(c.x, -0.45, c.z);
  dummy.scale.set(c.size, 1, c.size);
  dummy.rotation.set(0, 0, 0);
  dummy.updateMatrix();

  water.setMatrixAt(i, dummy.matrix);

  const h = hash2(c.x, c.z);
  tempColor.setHSL(0.53 + 0.045 * h, 0.58, 0.38 + 0.08 * h);
  water.setColorAt(i, tempColor);
}

water.instanceMatrix.needsUpdate = true;
if (water.instanceColor) water.instanceColor.needsUpdate = true;
scene.add(water);

/* Main sailing ship */
const shipBuilder = new Builder();

function addShipBlock(x, y, z, color, sx = 1, sy = 1, sz = 1) {
  shipBuilder.add(x, y, z, color, sx, sy, sz);
}

function addShipCrate(x, z, size = 1) {
  for (let y = 2; y < 2 + size; y++) {
    for (let dx = 0; dx < size; dx++) {
      for (let dz = 0; dz < size; dz++) {
        addShipBlock(
          x + dx,
          y,
          z + dz,
          (dx + dz + y) & 1 ? COL.dockDark : COL.crate
        );
      }
    }
  }
}

function buildShip() {
  // Hull footprint
  for (let x = -8; x <= 8; x++) {
    let zmin = -2;
    let zmax = 2;

    if (x === -8 || x === 8) {
      zmin = -1;
      zmax = 1;
    }

    for (let z = zmin; z <= zmax; z++) {
      const edge = z === zmin || z === zmax || x === -8 || x === 8;

      addShipBlock(x, 0, z, COL.hullDark);
      addShipBlock(x, 1, z, edge ? COL.hullSide : COL.deck);

      if (edge) {
        addShipBlock(x, 2, z, COL.gold);
      }
    }
  }

  // Cabin / stern quarters
  for (let x = -6; x <= -4; x++) {
    for (let z = -1; z <= 1; z++) {
      for (let y = 2; y <= 3; y++) {
        let c = COL.wallCream;

        if (y === 3 && (x === -4 || x === -6) && (z === -1 || z === 1)) {
          c = COL.white;
        }

        if (y === 2 && x === -4 && z === 0) {
          c = COL.black;
        }

        addShipBlock(x, y, z, c);
      }
    }
  }

  for (let x = -6; x <= -4; x++) {
    for (let z = -1; z <= 1; z++) {
      addShipBlock(x, 4, z, COL.roofBlue);
    }
  }

  // Cargo and barrels
  addShipCrate(3, -1, 2);
  addShipCrate(6, -1, 1);
  addShipCrate(-2, 1, 1);
  addShipBlock(1, 2, 0, COL.dockDark, 0.7, 1, 0.7);

  // Masts
  function addMast(x, height) {
    for (let y = 2; y <= height; y++) {
      addShipBlock(x, y, 0, COL.mast);
    }
  }

  addMast(5, 11);   // foremast
  addMast(0, 13);   // mainmast
  addMast(-5, 10);  // mizzenmast

  function addYard(x, y, span) {
    addShipBlock(x, y, 0.05, COL.yard, span * 2 + 1, 1, 1);
  }

  function addSail(x, yLow, yHigh, span) {
    for (let y = yLow; y <= yHigh; y++) {
      for (let dx = -span; dx <= span; dx++) {
        if (dx === 0) continue;
        addShipBlock(x + dx, y, 0, COL.sail);
      }
    }
  }

  // Foremast sails
  addYard(5, 8, 3);
  addSail(5, 3, 7, 3);

  addYard(5, 10, 2);
  addSail(5, 8, 9, 2);

  // Mainmast sails
  addYard(0, 9, 4);
  addSail(0, 4, 8, 4);

  addYard(0, 12, 3);
  addSail(0, 10, 11, 3);

  // Mizzenmast sail
  addYard(-5, 7, 2);
  addSail(-5, 3, 6, 2);

  // Bowsprit
  for (let x = 9; x <= 11; x++) {
    addShipBlock(x, 2, 0, COL.mast);
  }
  for (let x = 12; x <= 14; x++) {
    addShipBlock(x, 3, 0, COL.mast);
  }

  // Flags
  addShipBlock(1, 14, 0.05, COL.flagRed);
  addShipBlock(2, 14, 0.05, COL.white);

  addShipBlock(-4, 11, 0.05, COL.flagRed);
  addShipBlock(-3, 11, 0.05, COL.flagRed);
}

buildShip();

const shipGroup = new THREE.Group();
shipGroup.position.set(0, 0, 4);
shipGroup.add(
  shipBuilder.build(
    new THREE.MeshStandardMaterial({
      roughness: 0.7,
      metalness: 0.05
    })
  )
);
scene.add(shipGroup);

/* Small boat in the harbor */
const boatBuilder = new Builder();

function buildSmallBoat() {
  for (let x = -3; x <= 3; x++) {
    let zmin = -1;
    let zmax = 1;

    if (x === -3 || x === 3) {
      zmin = 0;
      zmax = 0;
    }

    for (let z = zmin; z <= zmax; z++) {
      const edge = z === zmin || z === zmax || x === -3 || x === 3;

      boatBuilder.add(x, 0, z, COL.hullDark);
      boatBuilder.add(x, 1, z, edge ? COL.hullSide : COL.deck);
    }
  }

  boatBuilder.add(0, 2, 0, COL.mast);
  boatBuilder.add(0, 3, 0, COL.mast);
  boatBuilder.add(0, 4, 0, COL.mast);

  for (let y = 2; y <= 4; y++) {
    boatBuilder.add(-1, y, 0.05, COL.sail);
    boatBuilder.add(1, y, 0.05, COL.sail);
  }

  boatBuilder.add(2, 5, 0.05, COL.flagRed);
}

buildSmallBoat();

const boatGroup = new THREE.Group();
boatGroup.position.set(21, 0, -12);
boatGroup.add(
  boatBuilder.build(
    new THREE.MeshStandardMaterial({
      roughness: 0.72,
      metalness: 0.04
    })
  )
);
scene.add(boatGroup);

/* Animation */
const clock = new THREE.Clock();

function updateWater(t) {
  for (let i = 0; i < waterCells.length; i++) {
    const c = waterCells[i];

    const y =
      -0.45 +
      Math.sin(t * 1.2 + c.x * 0.12 + c.phase) * 0.07 +
      Math.sin(t * 0.8 + c.z * 0.13 + c.phase * 0.4) * 0.04;

    dummy.position.set(c.x, y, c.z);
    dummy.scale.set(c.size, 1, c.size);
    dummy.rotation.set(0, 0, 0);
    dummy.updateMatrix();

    water.setMatrixAt(i, dummy.matrix);
  }

  water.instanceMatrix.needsUpdate = true;
}

function animate() {
  const t = clock.getElapsedTime();

  updateWater(t);

  shipGroup.position.y = Math.sin(t * 0.85) * 0.07;
  shipGroup.rotation.z = Math.sin(t * 0.55) * 0.03;
  shipGroup.rotation.y = Math.sin(t * 0.25) * 0.02;

  boatGroup.position.y = Math.sin(t * 1.1 + 1.7) * 0.08;
  boatGroup.rotation.z = Math.sin(t * 0.75 + 0.9) * 0.05;
  boatGroup.rotation.y = Math.sin(t * 0.4 + 2.0) * 0.03;

  controls.update();
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

animate();
</script>
</body>
</html>
```