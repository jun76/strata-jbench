Here is the complete, single HTML file containing the 3D voxel art scene. It uses **Three.js** via CDN, so you can simply save this code as an `.html` file (e.g., `voxel-harbor.html`) and open it directly in Google Chrome. 

You can click and drag to orbit the camera around the scene, and use the scroll wheel to zoom in and out.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Voxel Sailing Ship in Harbor</title>
  <style>
    body { 
      margin: 0; 
      overflow: hidden; 
      background: #87CEEB; 
      font-family: sans-serif;
    }
    #info {
      position: absolute;
      top: 10px;
      left: 10px;
      color: white;
      text-shadow: 1px 1px 2px black;
      pointer-events: none;
      z-index: 10;
    }
  </style>
</head>
<body>
  <div id="info">
    <h2>A Sailing Ship Calling at a Harbor</h2>
    <p>Drag to rotate • Scroll to zoom</p>
  </div>

  <!-- Import maps for Three.js -->
  <script type="importmap">
    {
      "imports": {
        "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
        "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
      }
    }
  </script>

  <script type="module">
    import * as THREE from 'three';
    import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

    // --- 1. SCENE SETUP ---
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x87CEEB);
    scene.fog = new THREE.Fog(0x87CEEB, 40, 90);

    const camera = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 1, 1000);
    camera.position.set(20, 15, 25);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    document.body.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.target.set(5, 2, 2);
    controls.enableDamping = true;
    controls.maxPolarAngle = Math.PI / 2 - 0.05; // Prevent camera from going underwater
    controls.minDistance = 10;
    controls.maxDistance = 70;

    // --- 2. LIGHTING ---
    scene.add(new THREE.AmbientLight(0xffffff, 0.6));

    const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
    dirLight.position.set(30, 40, 20);
    dirLight.castShadow = true;
    dirLight.shadow.camera.left = -30;
    dirLight.shadow.camera.right = 30;
    dirLight.shadow.camera.top = 30;
    dirLight.shadow.camera.bottom = -30;
    scene.add(dirLight);

    const lighthousePointLight = new THREE.PointLight(0xfeca57, 1.5, 20);
    lighthousePointLight.position.set(22, 12.5, 10);
    scene.add(lighthousePointLight);

    // --- 3. MATERIALS & HELPERS ---
    const materials = {
      water: new THREE.MeshLambertMaterial({ color: 0x2980b9 }),
      wave: new THREE.MeshLambertMaterial({ color: 0x3498db }),
      foam: new THREE.MeshLambertMaterial({ color: 0xffffff, transparent: true, opacity: 0.6 }),
      hull: new THREE.MeshLambertMaterial({ color: 0x4a2c11 }),
      hullStripe: new THREE.MeshLambertMaterial({ color: 0x8a4a1c }),
      deck: new THREE.MeshLambertMaterial({ color: 0x9e7027 }),
      mast: new THREE.MeshLambertMaterial({ color: 0x3d2510 }),
      sail: new THREE.MeshLambertMaterial({ color: 0xf0f0e6, side: THREE.DoubleSide }),
      cannon: new THREE.MeshLambertMaterial({ color: 0x2c3e50 }),
      dock: new THREE.MeshLambertMaterial({ color: 0x7b5e3c }),
      crate: new THREE.MeshLambertMaterial({ color: 0xc19a6b }),
      lighthouseWhite: new THREE.MeshLambertMaterial({ color: 0xf5f5f5 }),
      lighthouseRed: new THREE.MeshLambertMaterial({ color: 0xd63031 }),
      lighthouseLight: new THREE.MeshLambertMaterial({ color: 0xffeaa7, emissive: 0xfeca57, emissiveIntensity: 0.8 }),
      rock: new THREE.MeshLambertMaterial({ color: 0x636e72 }),
      grass: new THREE.MeshLambertMaterial({ color: 0x27ae60 }),
      sand: new THREE.MeshLambertMaterial({ color: 0xf1c40f }),
      treeTrunk: new THREE.MeshLambertMaterial({ color: 0x8b4513 }),
      treeLeaves: new THREE.MeshLambertMaterial({ color: 0x228b22 }),
      cloud: new THREE.MeshLambertMaterial({ color: 0xffffff, transparent: true, opacity: 0.9 })
    };

    const boxGeo = new THREE.BoxGeometry(1, 1, 1);

    // Global helper (adds to scene)
    function addVoxel(gx, gy, gz, material) {
      const mesh = new THREE.Mesh(boxGeo, material);
      mesh.position.set(gx, gy + 0.5, gz); // +0.5 to rest on grid lines
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      scene.add(mesh);
      return mesh;
    }

    // Group helper (adds to specific group)
    function addVoxelToGroup(group, gx, gy, gz, material) {
      const mesh = new THREE.Mesh(boxGeo, material);
      mesh.position.set(gx, gy + 0.5, gz);
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      group.add(mesh);
      return mesh;
    }

    // --- 4. ENVIRONMENT ---
    // Ocean Plane
    const ocean = new THREE.Mesh(new THREE.PlaneGeometry(150, 150), materials.water);
    ocean.rotation.x = -Math.PI / 2;
    ocean.receiveShadow = true;
    scene.add(ocean);

    // Voxel Ocean Waves & Foam
    const waves = [];
    for(let i = 0; i < 150; i++) {
      let x = (Math.random() - 0.5) * 120;
      let z = (Math.random() - 0.5) * 120;
      if (x > -15 && x < 30 && z > -15 && z < 20) continue; // Keep harbor clear
      let wave = new THREE.Mesh(boxGeo, materials.wave);
      wave.position.set(x, 0, z);
      wave.scale.set(1 + Math.random() * 3, 0.2, 0.5 + Math.random());
      scene.add(wave);
      waves.push({ mesh: wave, baseX: x, speed: 0.5 + Math.random() });
    }

    const foam = [];
    for(let i = 0; i < 40; i++) {
      let x = (Math.random() - 0.5) * 20;
      let z = (Math.random() - 0.5) * 8;
      let mesh = new THREE.Mesh(boxGeo, materials.foam.clone()); // Clone material for individual opacity
      mesh.position.set(x, 0.1, z);
      mesh.scale.set(0.5 + Math.random(), 0.1, 0.5 + Math.random());
      scene.add(mesh);
      foam.push({ mesh: mesh, baseX: x, speed: 1 + Math.random() });
    }

    // Clouds
    const cloudGroup = new THREE.Group();
    scene.add(cloudGroup);
    function createCloud(cx, cy, cz) {
      for(let i = 0; i < 5; i++) {
        let mesh = new THREE.Mesh(boxGeo, materials.cloud);
        mesh.position.set(cx + (Math.random()-0.5)*4, cy + (Math.random()-0.5)*2, cz + (Math.random()-0.5)*3);
        mesh.scale.set(2+Math.random()*2, 1, 2+Math.random()*2);
        cloudGroup.add(mesh);
      }
    }
    createCloud(-20, 18, -10);
    createCloud(10, 22, -20);
    createCloud(-5, 15, 25);

    // --- 5. BUILD THE SHIP ---
    const shipGroup = new THREE.Group();
    scene.add(shipGroup);

    // Hull & Deck
    for (let x = -6; x <= 6; x++) {
      let w = 3;
      if (x === 6) w = 0;        // Pointy Bow
      else if (x === 5) w = 1;
      else if (x === 4) w = 2;
      else if (x === -6) w = 1;  // Flat Stern
      else if (x === -5) w = 2;

      for (let z = -w; z <= w; z++) {
        addVoxelToGroup(shipGroup, x, 0, z, materials.hull);
        addVoxelToGroup(shipGroup, x, 1, z, materials.hullStripe);
        addVoxelToGroup(shipGroup, x, 2, z, materials.deck);
      }
      // Rails
      if (w > 0) {
        addVoxelToGroup(shipGroup, x, 3, w, materials.hullStripe);
        addVoxelToGroup(shipGroup, x, 3, -w, materials.hullStripe);
      }
    }

    // Cannons
    for (let x = -2; x <= 2; x += 2) {
      addVoxelToGroup(shipGroup, x, 1, 3, materials.cannon);
      addVoxelToGroup(shipGroup, x, 1, -3, materials.cannon);
    }

    // Rudder
    addVoxelToGroup(shipGroup, -7, 1, 0, materials.mast);
    addVoxelToGroup(shipGroup, -7, 0, 0, materials.mast);

    // Captain's Cabin
    for (let x = -5; x <= -4; x++) {
      for (let z = -1; z <= 1; z++) {
        addVoxelToGroup(shipGroup, x, 3, z, materials.deck);
        addVoxelToGroup(shipGroup, x, 4, z, materials.hullStripe);
      }
    }

    // Masts & Bowsprit
    for (let x = 7; x <= 10; x++) addVoxelToGroup(shipGroup, x, 2, 0, materials.mast); // Bowsprit
    for (let y = 3; y <= 11; y++) addVoxelToGroup(shipGroup, 2, y, 0, materials.mast);  // Front Mast
    for (let y = 3; y <= 9; y++)  addVoxelToGroup(shipGroup, -3, y, 0, materials.mast); // Back Mast

    // Front Mast Sails
    for (let y = 7; y <= 9; y++) {
      for (let z = -3; z <= 3; z++) {
        if (y === 9 && Math.abs(z) > 1) continue;
        if (y === 8 && Math.abs(z) === 3) continue;
        addVoxelToGroup(shipGroup, 2, y, z, materials.sail);
      }
    }
    for (let y = 4; y <= 6; y++) {
      for (let z = -2; z <= 2; z++) {
        addVoxelToGroup(shipGroup, 2, y, z, materials.sail);
      }
    }
    // Jib Sail
    for (let x = 7; x <= 10; x++) {
      let maxY = 10 - (x - 7); 
      for (let y = 3; y <= maxY; y++) {
        addVoxelToGroup(shipGroup, x, y, 0, materials.sail);
      }
    }

    // Back Mast Sails
    for (let y = 6; y <= 8; y++) {
      for (let z = -2; z <= 2; z++) {
        addVoxelToGroup(shipGroup, -3, y, z, materials.sail);
      }
    }
    for (let y = 4; y <= 5; y++) {
      for (let z = -3; z <= 3; z++) {
        addVoxelToGroup(shipGroup, -3, y, z, materials.sail);
      }
    }

    // Flags
    for(let i = 1; i <= 3; i++) addVoxelToGroup(shipGroup, 2+i, 11, 0, materials.lighthouseRed);
    for(let i = 1; i <= 2; i++) addVoxelToGroup(shipGroup, -3+i, 9, 0, materials.sail);

    // --- 6. BUILD THE HARBOR ---
    // Wooden Pier
    for (let x = -10; x <= 15; x++) {
      for (let z = 5; z <= 8; z++) addVoxel(x, 0, z, materials.dock);
    }
    // Pier Posts
    for (let x = -10; x <= 15; x += 3) {
      for (let z of [5, 8]) {
        addVoxel(x, -1, z, materials.mast);
        addVoxel(x, -2, z, materials.mast);
      }
    }

    // Gangplank (Stairs from ship to pier)
    for (let x = 0; x <= 1; x++) {
      addVoxel(x, 2, 3, materials.mast); // On ship
      addVoxel(x, 1, 4, materials.mast); // Middle step
      addVoxel(x, 0, 5, materials.mast); // On pier
    }

    // Landmass
    for (let x = 16; x <= 30; x++) {
      for (let z = -15; z <= 25; z++) {
        let distFromWater = x - 15;
        let mat = distFromWater <= 2 ? materials.sand : materials.grass;
        let h = distFromWater > 5 ? 1 : 0; // Raised plateau in the back
        for(let y = 0; y <= h; y++) {
           addVoxel(x, y, z, mat);
        }
      }
    }

    // Trees on Land
    const treePositions = [ {x: 25, z: -5}, {x: 28, z: 15}, {x: 24, z: 20}, {x: 26, z: 5} ];
    treePositions.forEach(pos => {
      addVoxel(pos.x, 2, pos.z, materials.treeTrunk);
      addVoxel(pos.x, 3, pos.z, materials.treeTrunk);
      for(let dx = -1; dx <= 1; dx++) {
        for(let dz = -1; dz <= 1; dz++) {
          if (Math.abs(dx) === 1 && Math.abs(dz) === 1) continue;
          addVoxel(pos.x+dx, 4, pos.z+dz, materials.treeLeaves);
          addVoxel(pos.x+dx, 5, pos.z+dz, materials.treeLeaves);
        }
      }
      addVoxel(pos.x, 6, pos.z, materials.treeLeaves);
    });

    // Lighthouse
    const lhX = 22, lhZ = 10;
    for (let y = 2; y <= 11; y++) {
      let radius = y < 6 ? 2 : 1;
      for (let x = -radius; x <= radius; x++) {
        for (let z = -radius; z <= radius; z++) {
          if (radius === 2 && Math.abs(x) === 2 && Math.abs(z) === 2) continue;
          let mat = (y % 2 === 0) ? materials.lighthouseRed : materials.lighthouseWhite;
          addVoxel(lhX + x, y, lhZ + z, mat);
        }
      }
    }
    addVoxel(lhX, 12, lhZ, materials.lighthouseLight);
    addVoxel(lhX, 13, lhZ, materials.lighthouseRed);

    // Rotating Lighthouse Beam
    const beamGroup = new THREE.Group();
    beamGroup.position.set(lhX, 12.5, lhZ);
    const beamGeo = new THREE.ConeGeometry(3, 25, 16, 1, true);
    const beamMat = new THREE.MeshBasicMaterial({ color: 0xffeaa7, transparent: true, opacity: 0.15, side: THREE.DoubleSide, depthWrite: false });
    const beam = new THREE.Mesh(beamGeo, beamMat);
    beam.rotation.z = Math.PI / 2;
    beam.position.set(12.5, 0, 0); // Shift so tip is at group origin
    beamGroup.add(beam);
    scene.add(beamGroup);

    // Cargo & Crates on Pier
    const items = [
      {x: -8, z: 6, mat: materials.crate}, {x: -7, z: 6, mat: materials.crate},
      {x: -8, z: 7, mat: materials.crate}, {x: 5, z: 6, mat: materials.mast},
      {x: 6, z: 6, mat: materials.mast},  {x: 5, z: 7, mat: materials.mast},
      {x: 12, z: 6, mat: materials.crate}, {x: 12, z: 6, mat: materials.crate, y: 2}
    ];
    items.forEach(item => addVoxel(item.x, item.y !== undefined ? item.y : 1, item.z, item.mat));

    // --- 7. ANIMATION LOOP ---
    let time = 0;
    function animate() {
      requestAnimationFrame(animate);
      time += 0.05;

      // Bobbing ship
      shipGroup.position.y = Math.sin(time) * 0.15;
      shipGroup.rotation.z = Math.sin(time * 0.8) * 0.015;
      shipGroup.rotation.x = Math.cos(time * 0.7) * 0.015;

      // Animate Waves & Foam
      waves.forEach(w => {
        w.mesh.position.x = w.baseX + Math.sin(time * w.speed) * 0.5;
        w.mesh.position.y = 0 + Math.sin(time * w.speed * 2) * 0.1;
      });
      foam.forEach(f => {
        f.mesh.position.x = f.baseX + Math.sin(time * f.speed) * 0.5;
        f.mesh.material.opacity = 0.5 + Math.sin(time * f.speed * 2) * 0.3;
      });

      // Rotate Lighthouse Beam
      beamGroup.rotation.y = time * 0.4;

      // Drift Clouds
      cloudGroup.children.forEach(c => {
        c.position.x += 0.01;
        if (c.position.x > 50) c.position.x = -50;
      });

      controls.update();
      renderer.render(scene, camera);
    }
    animate();

    // --- 8. RESIZE HANDLER ---
    window.addEventListener('resize', () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    });
  </script>
</body>
</html>
```