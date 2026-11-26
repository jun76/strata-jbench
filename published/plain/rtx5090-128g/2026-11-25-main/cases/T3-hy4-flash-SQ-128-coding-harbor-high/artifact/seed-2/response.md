Here is the complete, single HTML file. You can copy the code below, save it as an `.html` file (for example, `voxel_harbor.html`), and double-click it to open it in Google Chrome. 

It uses Three.js and `OrbitControls` via CDN. The scene uses `InstancedMesh` to render thousands of individual voxels smoothly, features shadows, animated water waves, a bobbing sailing ship, and a pulsing lighthouse.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Voxel Harbor Scene</title>
  <style>
    body {
      margin: 0;
      overflow: hidden;
      background-color: #87CEEB; /* Sky blue background */
    }
    canvas {
      display: block;
    }
    #info {
      position: absolute;
      top: 10px;
      left: 10px;
      color: white;
      font-family: sans-serif;
      text-shadow: 1px 1px 2px black;
      pointer-events: none;
    }
  </style>
  <!-- Three.js and OrbitControls from CDN -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
  <div id="info">
    <h2>A Sailing Ship Calling at a Harbor</h2>
    <p>Left click + drag to rotate. Scroll to zoom.</p>
  </div>
  
  <script>
    // --- 1. Basic Setup ---
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x87CEEB);
    scene.fog = new THREE.Fog(0x87CEEB, 60, 150);

    const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(45, 35, 45);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    document.body.appendChild(renderer.domElement);

    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.target.set(10, 5, 0);
    controls.maxPolarAngle = Math.PI / 2 - 0.05; // Prevent camera from going under the water

    // --- 2. Lighting ---
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
    dirLight.position.set(50, 80, 30);
    dirLight.castShadow = true;
    dirLight.shadow.camera.left = -80;
    dirLight.shadow.camera.right = 80;
    dirLight.shadow.camera.top = 80;
    dirLight.shadow.camera.bottom = -80;
    dirLight.shadow.camera.near = 0.5;
    dirLight.shadow.camera.far = 250;
    dirLight.shadow.bias = -0.001;
    scene.add(dirLight);

    // Pulsing light for the lighthouse
    const lighthouseLight = new THREE.PointLight(0xffff00, 1.5, 60);
    lighthouseLight.position.set(45, 18, -20);
    scene.add(lighthouseLight);

    // --- 3. Water Base ---
    const waterGeo = new THREE.BoxGeometry(200, 2, 200);
    const waterMat = new THREE.MeshLambertMaterial({ color: 0x4682B4, transparent: true, opacity: 0.9 });
    const waterBase = new THREE.Mesh(waterGeo, waterMat);
    waterBase.position.set(0, -1, 0);
    waterBase.receiveShadow = true;
    scene.add(waterBase);

    // --- 4. Voxel Data Storage ---
    const sceneVoxels = {};
    const shipVoxels = {}; // Separated so the ship can bob independently
    let currentBucket = sceneVoxels;

    const colors = {
      wood: 0xCD853F,
      darkWood: 0x8B4513,
      white: 0xF5F5F5,
      water: 0x4682B4,
      green: 0x2E8B57,
      stone: 0x808080,
      red: 0xCD5C5C,
      yellow: 0xFFD700,
      gray: 0x696969
    };

    function addVoxel(type, x, y, z) {
      if (!currentBucket[type]) currentBucket[type] = [];
      currentBucket[type].push({ x, y, z });
    }

    function addBarrel(cx, cy, cz, color) {
      for(let y=0; y<2; y++) {
        for(let x=-1; x<=1; x++) {
          for(let z=-1; z<=1; z++) {
            addVoxel(color, cx+x, cy+y, cz+z);
          }
        }
      }
    }

    // --- 5. Build the Ship ---
    currentBucket = shipVoxels;

    // Ship Hull
    for (let y = 0; y <= 5; y++) {
      for (let z = -12; z <= 12; z++) {
        let maxX = 0;
        if (y === 0) maxX = Math.floor(1 * (1 - Math.abs(z)/13));
        if (y === 1) maxX = Math.floor(2 * (1 - Math.abs(z)/13));
        if (y === 2) maxX = Math.floor(3 * (1 - Math.abs(z)/13));
        if (y === 3) maxX = Math.floor(4 * (1 - Math.abs(z)/13));
        if (y === 4) maxX = Math.floor(5 * (1 - Math.abs(z)/13));
        if (y === 5) maxX = Math.floor(5 * (1 - Math.abs(z)/13));
        
        if (z > 8) maxX = 4; // Flatten the stern
        
        for (let x = -maxX; x <= maxX; x++) {
          // Hollow out the deck area
          if (y === 5 && Math.abs(x) < maxX && z > -11 && z < 8) continue;
          
          let type = (y === 5) ? 'wood' : 'darkWood';
          // Add cannon ports
          if ((y === 2 || y === 3) && Math.abs(x) === maxX && maxX >= 3 && z > -9 && z < 8 && z % 3 === 0) {
            type = 'stone'; 
          }
          addVoxel(type, x, y, z);
        }
      }
    }

    // Masts and Spars
    for (let y = 5; y <= 23; y++) addVoxel('wood', 0, y, 0);
    for (let x = -7; x <= 7; x++) {
      addVoxel('wood', x, 10, 0);
      addVoxel('wood', x, 16, 0);
      if (Math.abs(x) <= 5) addVoxel('wood', x, 21, 0);
    }

    // Sails
    for (let y = 5; y <= 9; y++) {
      for (let x = -7; x <= 7; x++) {
        let z = Math.floor(2 * Math.cos(Math.PI * x / 14));
        if (y === 7 && Math.abs(x) > 2) continue; // little detail gap
        addVoxel('white', x, y, z);
      }
    }
    for (let y = 11; y <= 15; y++) {
      for (let x = -7; x <= 7; x++) {
        let z = Math.floor(2 * Math.cos(Math.PI * x / 14));
        addVoxel('white', x, y, z);
      }
    }
    for (let y = 17; y <= 20; y++) {
      for (let x = -5; x <= 5; x++) {
        let z = Math.floor(1.5 * Math.cos(Math.PI * x / 10));
        addVoxel('white', x, y, z);
      }
    }

    // Flag
    for (let x = 1; x <= 5; x++) addVoxel('red', x, 23, 0);

    // Railings
    for (let z = -11; z <= 8; z++) {
      if (z % 2 === 0) {
        addVoxel('darkWood', 5, 6, z);
        addVoxel('darkWood', -5, 6, z);
      }
    }
    for (let x = -5; x <= 5; x++) {
      if (x % 2 === 0) {
        addVoxel('darkWood', x, 6, -11);
        addVoxel('darkWood', x, 6, 8);
      }
    }
    for (let z = -11; z <= 8; z++) {
      addVoxel('wood', 5, 7, z);
      addVoxel('wood', -5, 7, z);
    }
    for (let x = -5; x <= 5; x++) {
      addVoxel('wood', x, 7, -11);
      addVoxel('wood', x, 7, 8);
    }

    // Small stern flag & barrels on ship
    addVoxel('wood', 0, 11, 8);
    addVoxel('red', 0, 12, 8);
    addVoxel('red', 0, 12, 9);
    addBarrel(2, 5, 4, 'wood');
    addBarrel(-2, 5, 4, 'wood');
    addBarrel(0, 5, 6, 'wood');


    // --- 6. Build the Harbor & Environment ---
    currentBucket = sceneVoxels;

    // Wooden Pier
    for (let x = 8; x <= 36; x++) {
      for (let z = -10; z <= 10; z++) {
        addVoxel('wood', x, 2, z);
        // Wooden posts
        if (x % 4 === 0 && (z === -10 || z === 10)) {
          for (let y = 0; y <= 2; y++) addVoxel('darkWood', x, y, z);
        }
      }
    }

    // Warehouse
    for (let x = 25; x <= 35; x++) {
      for (let z = -5; z <= 5; z++) {
        if (x === 25 || x === 35 || z === -5 || z === 5) {
          for (let y = 3; y <= 8; y++) {
            if (x === 25 && Math.abs(z) <= 1 && y <= 5) continue; // door cutout
            addVoxel('red', x, y, z);
          }
        }
        // Roof
        for (let y = 9; y <= 11; y++) {
          if (y === 9) addVoxel('gray', x, y, z);
          if (y === 10 && Math.abs(z) <= 4) addVoxel('gray', x, y, z);
          if (y === 11 && Math.abs(z) <= 2) addVoxel('gray', x, y, z);
        }
      }
    }
    addBarrel(15, 3, 5, 'wood');
    addBarrel(17, 3, 5, 'wood');
    addBarrel(16, 3, 8, 'wood');

    // Landmass & Terrain
    const landHeights = {};
    for (let x = 36; x <= 60; x++) {
      for (let z = -40; z <= 40; z++) {
        let height = 2 + Math.floor(Math.random() * 3);
        landHeights[x + ',' + z] = height;
        for (let y = 0; y <= height; y++) {
           let type = y === height ? 'green' : 'stone';
           addVoxel(type, x, y, z);
        }
      }
    }

    // Lighthouse Tower
    for (let y = 3; y <= 16; y++) {
      for (let dx = -3; dx <= 3; dx++) {
        for (let dz = -3; dz <= 3; dz++) {
          if (Math.abs(dx) === 3 || Math.abs(dz) === 3) {
             if (y % 4 === 0 && y > 3) {
                addVoxel('gray', 45 + dx, y, -20 + dz);
             } else if ((y + dx + dz) % 2 === 0) {
                addVoxel('white', 45 + dx, y, -20 + dz);
             } else {
                addVoxel('red', 45 + dx, y, -20 + dz);
             }
          }
        }
      }
    }
    // Lighthouse Glass Room
    for (let y = 17; y <= 19; y++) {
      for (let dx = -2; dx <= 2; dx++) {
        for (let dz = -2; dz <= 2; dz++) {
          if (Math.abs(dx) === 2 || Math.abs(dz) === 2) {
             let type = 'yellow';
             if (dx === 0 || dz === 0) type = 'white'; // window frames
             addVoxel(type, 45 + dx, y, -20 + dz);
          }
        }
      }
    }
    // Lighthouse Roof
    for (let y = 20; y <= 22; y++) {
      for (let dx = -3; dx <= 3; dx++) {
        for (let dz = -3; dz <= 3; dz++) {
          let r = Math.max(Math.abs(dx), Math.abs(dz));
          if (r === 3 && y === 20) addVoxel('red', 45 + dx, y, -20 + dz);
          if (r === 2 && y === 21) addVoxel('red', 45 + dx, y, -20 + dz);
          if (r === 1 && y === 22) addVoxel('red', 45 + dx, y, -20 + dz);
        }
      }
    }

    // Trees
    function addTree(cx, cy, cz) {
      addVoxel('darkWood', cx, cy, cz);
      addVoxel('darkWood', cx, cy+1, cz);
      for(let x=-2; x<=2; x++) {
        for(let z=-2; z<=2; z++) {
          for(let y=2; y<=4; y++) {
            if (Math.abs(x) + Math.abs(z) + Math.abs(y-3) <= 4) {
              addVoxel('green', cx+x, cy+y, cz+z);
            }
          }
        }
      }
    }
    for (let i = 0; i < 20; i++) {
      let tx = 38 + Math.floor(Math.random() * 20);
      let tz = -35 + Math.floor(Math.random() * 70);
      let ty = landHeights[tx + ',' + tz];
      if (ty !== undefined) addTree(tx, ty + 1, tz);
    }

    // Small Rowboat
    for (let z = -17; z <= -13; z++) {
      for (let x = 8; x <= 12; x++) {
        if (z === -17 || z === -13 || x === 8 || x === 12) addVoxel('darkWood', x, 1, z);
        else addVoxel('wood', x, 1, z);
      }
    }
    addVoxel('wood', 7, 1, -15);
    addVoxel('wood', 6, 1, -15);
    addVoxel('wood', 13, 1, -15);
    addVoxel('wood', 14, 1, -15);

    // Voxel Water Waves
    for(let x = -50; x <= 50; x++) {
      for(let z = -50; z <= 50; z++) {
        // Keep water out of dock, land, and lighthouse area
        if (x >= 8 && x <= 60 && z >= -10 && z <= 10) continue; 
        if (x >= 36) continue; 
        
        if (Math.random() > 0.85) {
          addVoxel('water', x, 1, z);
          if (Math.random() > 0.7) addVoxel('water', x, 2, z);
        }
      }
    }

    // Blocky Clouds
    function addCloud(cx, cy, cz) {
      const cloudShape = [
        [0,0,0], [1,0,0], [2,0,0], [3,0,0],
        [1,1,0], [2,1,0], [3,1,0],
        [2,0,1], [3,0,1],
        [1,0,-1], [0,0,-1]
      ];
      cloudShape.forEach(p => addVoxel('white', cx + p[0], cy + p[1], cz + p[2]));
    }
    addCloud(-20, 30, -20);
    addCloud(10, 35, -40);
    addCloud(50, 25, 20);
    addCloud(-40, 40, 30);

    // --- 7. Generate Meshes ---
    // InstancedMesh allows rendering thousands of identical cubes in a single draw call
    function buildMeshes(bucket, parent) {
      const dummy = new THREE.Object3D();
      for (const type in bucket) {
        if (bucket[type].length === 0) continue;
        const geo = new THREE.BoxGeometry(1, 1, 1);
        const mat = new THREE.MeshLambertMaterial({ color: colors[type] });
        const instMesh = new THREE.InstancedMesh(geo, mat, bucket[type].length);
        instMesh.castShadow = true;
        instMesh.receiveShadow = true;
        
        bucket[type].forEach((v, i) => {
          dummy.position.set(v.x, v.y, v.z);
          dummy.updateMatrix();
          instMesh.setMatrixAt(i, dummy.matrix);
        });
        parent.add(instMesh);
      }
    }

    const shipGroup = new THREE.Group();
    scene.add(shipGroup);

    buildMeshes(sceneVoxels, scene);
    buildMeshes(shipVoxels, shipGroup);

    // --- 8. Animation Loop ---
    function animate() {
      requestAnimationFrame(animate);
      controls.update();
      
      const time = Date.now() * 0.001;
      
      // Bob the ship up and down smoothly
      shipGroup.position.y = Math.sin(time * 2) * 0.3;
      shipGroup.rotation.z = Math.sin(time * 1.5) * 0.02;
      shipGroup.rotation.x = Math.cos(time * 1.8) * 0.02;
      
      // Pulse the lighthouse beam
      lighthouseLight.intensity = 1.0 + Math.sin(time * 4) * 1.0;
      
      renderer.render(scene, camera);
    }
    animate();

    // Handle window resizing
    window.addEventListener('resize', () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    });
  </script>
</body>
</html>
```