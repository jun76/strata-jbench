以下は単一 HTML ファイルで playableのマイクラ風3D box庭ゲームを。  
開ファイル directly from your browser and play.

```html
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, height=device-height, initial-scale=1" />
<title>マイクラ風 3D 箱庭</title>
<style>
  html, body {
    margin: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
    background: #87ceeb;
  }
  #overlay {
    position: fixed;
    left: 12px;
    top: 12px;
    font: 14px monospace;
    color: #fff;
    text-shadow: 0 0 3 #000;
    line-height: 1.45;
    pointer-events: none;
    white-space: pre-wrap;
  }
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>
<div id="overlay"></div>

<script>
(function () {
  "use strict";

  if (!window.THREE) {
    document.getElementById("overlay").textContent =
      "Error: Three.js could not be loaded.";
    return;
  }

  const THREE = window.THREE;
  const overlay = document.getElementById("overlay");

  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ antialias: true });
  } catch (e) {
    overlay.textContent =
      "Error: WebGL is not supported in this browser.";
    return;
  }

  const canvas = renderer.domElement;
  document.body.appendChild(canvas);

  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(window.innerWidth, window.innerHeight);

  // ============================================================
  // Scene, camera, lights
  // ============================================================
  const scene = new THREE.Scene();
  scene.background = new THREE.Color("#87ceeb");
  scene.fog = new THREE.FogExp2("#87ceeb", 0.012);

  const camera = new THREE.PerspectiveCamera(72, window.innerWidth / window.innerHeight, 0.1, 300);
  camera.rotation.order = "YXZ";
  scene.add(camera);

  const ambient = new THREE.AmbientLight("#ffffff", 0.65);
  scene.add(ambient);

  const sun = new THREE.DirectionalLight("#ffffff", 0.85);
  sun.position.set(40, 90, 15);
  scene.add(sun);

  // ============================================================
  // Block types
  // ============================================================
  const TYPES = [
    { name: "Grass", color: "#68a939" },
    { name: "Dirt", color: "#8b5a37" },
    { name: "Stone", color: "#8d8e93" },
    { name: "Wood", color: "#7b5130" },
    { name: "Leaf", color: "#2f8b57" },
    { name: "Sand", color: "#d5b96d" }
  ];

  const MAX_PER_TYPE = 18000;
  const boxGeo = new THREE.BoxGeometry(1, 1, 1);

  const instancedMeshes = [];
  const instanceMaps = [];

  for (let i = 0; i < TYPES.length; i++) {
    const mat = new THREE.MeshLambertMaterial({ color: TYPES[i].color });
    const mesh = new THREE.InstancedMesh(boxGeo, mat, MAX_PER_TYPE);
    mesh.frustumCulled = false;
    mesh.count = 0;
    mesh.userData = { type: i };
    scene.add(mesh);
    instancedMeshes.push(mesh);
    instanceMaps.push([]);
  }

  // ============================================================
  // Voxel world data
  // ============================================================
  const blockType = new Map();   // key -> typeIndex
  const keyToInstance = new Map(); // key -> [typeIndex, instanceIndex]

  function key(x, y, z) {
    return x + "," + y + "," + z;
  }

  function parseKey(k) {
    const a = k.split(",");
    return { x: Number(a[0]), y: Number(a[1]), z: Number(a[2]) };
  }

  const dummy = new THREE.Object3D();

  function addBlock(x, y, z, type) {
    const k = key(x, y, z);
    if (blockType.has(k)) return false;
    if (instanceMaps[type].length >= MAX_PER_TYPE) return false;

    blockType.set(k, type);
    const idx = instanceMaps[type].length;
    instanceMaps[type].push(k);
    keyToInstance.set(k, [type, idx]);

    dummy.position.set(x + 0.5, y + 0.5, z + 0.5);
    dummy.updateMatrix();
    instancedMeshes[type].setMatrixAt(idx, dummy.matrix);
    instancedMeshes[type].instanceMatrix.needsUpdate = true;
    instancedMeshes[type].count = instanceMaps[type].length;
    return true;
  }

  function removeBlock(x, y, z) {
    const k = key(x, y, z);
    const info = keyToInstance.get(k);
    if (!info) return false;

    const type = info[0];
    const idx = info[1];
    const mesh = instancedMeshes[type];
    const arr = instanceMaps[type];

    blockType.delete(k);
    keyToInstance.delete(k);

    const last = arr.length - 1;
    if (idx !== last) {
      const movedKey = arr[last];
      arr[idx] = movedKey;
      const p = parseKey(movedKey);

      dummy.position.set(p.x + 0.5, p.y + 0.5, p.z + 0.5);
      dummy.updateMatrix();
      mesh.setMatrixAt(idx, dummy.matrix);
      keyToInstance.set(movedKey, [type, idx]);
    }

    arr.pop();
    mesh.count = arr.length;
    mesh.instanceMatrix.needsUpdate = true;
    return true;
  }

  // ============================================================
  // Noise / terrain
  // ============================================================
  function hash(n) {
    const x = Math.sin(n * 12.9898) * 43758.5453123;
    return x - Math.floor(x);
  }

  function value(x, z, scale) {
    const fx = x / scale;
    const fz = z / scale;
    const ix = Math.floor(fx);
    const iz = Math.floor(fz);
    const xf = fx - ix;
    const zf = fz - iz;

    const a = hash(ix * 13.1 + iz * 37.7);
    const b = hash((ix + 1) * 13.1 + iz * 37.7);
    const c = hash(ix * 13.1 + (iz + 1) * 37.7);
    const d = hash((ix + 1) * 13.1 + (iz + 1) * 37.7);

    const t1 = a * (1 - xf) + b * xf;
    const t2 = c * (1 - xf) + d * xf;
    return t1 * (1 - zf) + t2 * zf;
  }

  function terrainHeight(x, z) {
    const a = value(x, z, 3);
    const b = value(x, z, 7);
    const c = value(x, z, 17);
    return Math.floor(6 + a * 4 + b * 4 + c * 3);
  }

  const R = 24;
  const WORLD_MIN_X = -R;
  const WORLD_MAX_X = R - 1;
  const WORLD_MIN_Z = -R;
  const WORLD_MAX_Z = R - 1;
  const MAX_Y = 100;
  const BEDROCK_Y = 0;

  function generateTerrain() {
    for (let x = WORLD_MIN_X; x <= WORLD_MAX_X; x++) {
      for (let z = WORLD_MIN_Z; z <= WORLD_MAX_Z; z++) {
        const h = terrainHeight(x, z);

        for (let y = 0; y < h; y++) {
          let type;
          if (y === 0) type = 2;
          else if (y === h - 1) type = 0;
          else if (y >= h - 3) type = 1;
          else type = 2;
          addBlock(x, y, z, type);
        }
      }
    }

    // Trees
    let seed = 987654321;
    function rnd() {
      seed = (seed * 1103515245 + 12345) % 2147483647;
      return seed / 2147483647;
    }

    for (let x = -R + 2; x < R - 2; x += 5) {
      for (let z = -R + 2; z < R - 2; z += 5) {
        if (rnd() < 0.28) {
          const h = terrainHeight(x, z);
          if (h >= 4) {
            const trunkTop = h + 2;
            for (let y = h; y <= trunkTop; y++) {
              addBlock(x, y, z, 3);
            }

            const leafY0 = h + 2;
            for (let dy = 0; dy < 2; dy++) {
              for (let dx = -1; dx <= 1; dx++) {
                for (let dz = -1; dz <= 1; dz++) {
                  if (dy === 1 && dx === 0 && dz === 0) continue;
                  addBlock(x + dx, leafY0 + dy, z + dz, 4);
                }
              }
            }
          }
        }
      }
    }
  }

  generateTerrain();

  // ============================================================
  // Player
  // ============================================================
  const HALF_W = 0.4;
  const PLAYER_H = 1.8;
  const EYE = 1.6;
  const GRAVITY = -24;
  const JUMP = 8.2;
  const WALK = 4.6;
  const RUN = 7.2;
  const EPS = 0.0001;

  const spawnX = 0.5;
  const spawnZ = 0.5;
  const spawnY = terrainHeight(0, 0) + 0.05;

  const player = {
    x: spawnX,
    y: spawnY,
    z: spawnZ,
    vy: 0,
    grounded: false
  };

  let yaw = 0;
  let pitch = 0;

  const keys = {};

  function blockCollides(px, py, pz) {
    const minX = px - HALF_W;
    const maxX = px + HALF_W;
    const minY = py;
    const maxY = py + PLAYER_H;
    const minZ = pz - HALF_W;
    const maxZ = pz + HALF_W;

    const x0 = Math.floor(minX + EPS);
    const x1 = Math.floor(maxX - EPS);
    const y0 = Math.floor(minY + EPS);
    const y1 = Math.floor(maxY - EPS);
    const z0 = Math.floor(minZ + EPS);
    const z1 = Math.floor(maxZ - EPS);

    for (let x = x0; x <= x1; x++) {
      for (let y = y0; y <= y1; y++) {
        for (let z = z0; z <= z1; z++) {
          if (blockType.has(key(x, y, z))) return true;
        }
      }
    }
    return false;
  }

  function blockWouldOverlapPlayer(cx, cy, cz) {
    const minX = player.x - HALF_W;
    const maxX = player.x + HALF_W;
    const minY = player.y;
    const maxY = player.y + PLAYER_H;
    const minZ = player.z - HALF_W;
    const maxZ = player.z + HALF_W;

    return (
      maxX > cx - EPS &&
      minX < cx + 1 + EPS &&
      maxY > cy - EPS &&
      minY < cy + 1 + EPS &&
      maxZ > cz - EPS &&
      minZ < cz + 1 + EPS
    );
  }

  // ============================================================
  // Input
  // ============================================================
  let mouseHeld = false;
  let selectedType = 0;

  let lastTime = performance.now();

  document.addEventListener("contextmenu", function () {
    // right click is used for deleting blocks in pointer lock
  });

  document.addEventListener("keydown", function (e) {
    keys[e.key] = true;
    if (e.key >= "1" && e.key <= "6") {
      selectedType = Math.min(Number(e.key) - 1, TYPES.length - 1);
    }
  });

  document.addEventListener("keyup", function (e) {
    keys[e.key] = false;
  });

  canvas.addEventListener("mousedown", function (e) {
    mouseHeld = true;
    const locked = document.pointerLockElement === canvas;

    if (!locked && (e.button === 0 || e.button === 2)) {
      try {
        canvas.requestPointerLock();
      } catch (err) {
        // ignore
      }
      return;
    }

    if (locked) {
      if (e.button === 0) placeBlock();
      if (e.button === 2) deleteBlock();
    }
  });

  canvas.addEventListener("mouseup", function () {
    mouseHeld = false;
  });

  document.addEventListener("mousemove", function (e) {
    const locked = document.pointerLockElement === canvas;
    const dx = e.movementX || 0;
    const dy = e.movementY || 0;

    if (locked || mouseHeld) {
      const sens = locked ? 0.0022 : 0.0030;
      yaw -= dx * sens;
      pitch -= dy * sens;
      pitch = Math.max(-1.52, Math.min(1.52, pitch));
    }
  });

  function placeBlock() {
    const hit = centerRaycast();
    if (!hit) return;

    const n = getFaceNormal(hit);
    if (!n) return;

    const point = hit.point;
    const cx = point.x - n.x * 0.5;
    const cy = point.y - n.y * 0.5;
    const cz = point.z - n.z * 0.5;

    const bx = Math.floor(cx);
    const by = Math.floor(cy);
    const bz = Math.floor(cz);

    const tx = bx + Math.round(n.x);
    const ty = by + Math.round(n.y);
    const tz = bz + Math.round(n.z);

    if (ty < 1) return;
    if (ty > MAX_Y) return;
    if (tx < -200 || tx > 200) return;
    if (tz < -200 || tz > 200) return;

    if (blockWouldOverlapPlayer(tx, ty, tz)) return;

    addBlock(tx, ty, tz, selectedType);
  }

  function deleteBlock() {
    const hit = centerRaycast();
    if (!hit) return;

    const n = getFaceNormal(hit);
    if (!n) return;

    const point = hit.point;
    const cx = point.x - n.x * 0.5;
    const cy = point.y - n.y * 0.5;
    const cz = point.z - n.z * 0.5;

    const bx = Math.floor(cx);
    const by = Math.floor(cy);
    const bz = Math.floor(cz);

    if (by <= BEDROCK_Y) return;

    removeBlock(bx, by, bz);
  }

  const raycaster = new THREE.Raycaster();

  function centerRaycast() {
    const dir = camera.getWorldDirection(new THREE.Vector3());
    raycaster.set(camera.position, dir);
    raycaster.far = 120;

    const hits = raycaster.intersectObjects(instancedMeshes, true);
    if (hits.length === 0) return null;
    return hits[0];
  }

  function getFaceNormal(hit) {
    if (hit.face) {
      return hit.face.normal;
    }

    // Fallback if face normal is unavailable.
    const p = hit.point;
    const cx = Math.round(p.x - 0.5);
    const cy = Math.round(p.y - 0.5);
    const cz = Math.round(p.z - 0.5);

    const dx = p.x - cx;
    const dy = p.y - cy;
    const dz = p.z - cz;

    const ax = Math.abs(dx);
    const ay = Math.abs(dy);
    const az = Math.abs(dz);

    if (ax > ay && ax > az) {
      return new THREE.Vector3(Math.sign(dx), 0, 0);
    }
    if (ay > ax && ay > az) {
      return new THREE.Vector3(0, Math.sign(dy), 0);
    }
    if (az >= ax && az >= ay) {
      return new THREE.Vector3(0, 0, Math.sign(dz));
    }

    return null;
  }

  // ============================================================
  // UI overlay
  // ============================================================
  function updateOverlay() {
    overlay.textContent =
      "マイクラ風 3D 箱庭\n" +
      "左クリック: pointer lock\n" +
      "左クリック: block place\n" +
      "右クリック: block delete\n" +
      "Q: place, B: delete\n" +
      "1-6: select block\n\n" +
      "Move: Arrow keys / WASD-like\n" +
      "Space: jump\n" +
      "Shift: run\n" +
      "ESC: unlock mouse\n\n" +
      "Selected: " + TYPES[selectedType].name + "\n" +
      "Blocks: " + blockType.size;
  }

  updateOverlay();

  // ============================================================
  // Movement
  // ============================================================
  function updateMovement(dt) {
    const forward =
      (keys["ArrowUp"] ? 1 : 0) -
      (keys["ArrowDown"] ? 1 : 0);
    const right =
      (keys["ArrowRight"] ? 1 : 0) -
      (keys["ArrowLeft"] ? 1 : 0);

    const speed = (keys.ShiftLeft || keys.ShiftRight) ? RUN : WALK;

    const sin = Math.sin(yaw);
    const cos = Math.cos(yaw);

    // forward is -z when yaw=0
    const vx = (right * cos - forward * sin) * speed * dt;
    const vz = (-right * sin - forward * cos) * speed * dt;

    // X movement
    const oldX = player.x;
    player.x += vx;
    if (blockCollides(player.x, player.y, player.z)) {
      player.x = oldX;
    }

    // Z movement
    const oldZ = player.z;
    player.z += vz;
    if (blockCollides(player.x, player.y, player.z)) {
      player.z = oldZ;
    }

    // Jump
    if (keys[" "] && player.grounded) {
      player.vy = JUMP;
      player.grounded = false;
    }

    // Gravity
    player.vy += GRAVITY * dt;
    if (player.vy < -35) player.vy = -35;

    // Y movement
    const oldY = player.y;
    player.y += player.vy * dt;
    if (blockCollides(player.x, player.y, player.z)) {
      player.y = oldY;
      if (player.vy < 0) {
        player.grounded = true;
      }
      player.vy = 0;
    } else {
      if (player.vy <= 0) player.grounded = false;
    }

    // Fall protection
    if (player.y < -100) {
      player.x = spawnX;
      player.y = spawnY;
      player.z = spawnZ;
      player.vy = 0;
    }
  }

  // ============================================================
  // Main loop
  // ============================================================
  function animate() {
    const now = performance.now();
    let dt = (now - lastTime) / 1000;
    lastTime = now;
    if (dt > 0.1) dt = 0.1;

    updateMovement(dt);

    camera.position.set(player.x, player.y + EYE, player.z);
    camera.rotation.set(pitch, yaw, 0);

    renderer.render(scene, camera);

    updateOverlay();

    requestAnimationFrame(animate);
  }

  requestAnimationFrame(animate);

  window.addEventListener("resize", function () {
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  });
})();
</script>
</body>
</html>
```