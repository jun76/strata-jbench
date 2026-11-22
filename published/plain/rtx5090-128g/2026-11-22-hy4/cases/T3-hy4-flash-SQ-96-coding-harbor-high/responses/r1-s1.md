Here is the complete, single HTML file containing the 3D voxel art scene. It uses Three.js and OrbitControls via CDN, so you just need to save it as an `.html` file (e.g., `voxel-harbor.html`) and open it in Google Chrome.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Voxel Art: Sailing Ship at Harbor</title>
    <style>
        body {
            margin: 0;
            overflow: hidden;
            background-color: #87CEEB;
        }
        canvas {
            display: block;
        }
        #ui {
            position: absolute;
            top: 20px;
            left: 20px;
            color: white;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            pointer-events: none;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
        }
        #ui h1 {
            margin: 0 0 8px 0;
            font-size: 32px;
            letter-spacing: 1px;
        }
        #ui p {
            margin: 0;
            font-size: 16px;
            opacity: 0.9;
        }
    </style>
    <!-- Three.js Library -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <!-- OrbitControls for Mouse Interaction -->
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
    <div id="ui">
        <h1>Voxel Harbor</h1>
        <p>Drag to rotate | Scroll to zoom</p>
    </div>

    <script>
        // --- Scene Setup ---
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x87CEEB);
        scene.fog = new THREE.Fog(0x87CEEB, 60, 150);

        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(35, 25, 45);

        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        document.body.appendChild(renderer.domElement);

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.target.set(0, 5, 0);
        controls.maxPolarAngle = Math.PI / 2 - 0.05; // Prevent camera from going under the water

        // --- Lighting ---
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        scene.add(ambientLight);

        const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
        dirLight.position.set(20, 50, 30);
        dirLight.castShadow = true;
        dirLight.shadow.mapSize.width = 2048;
        dirLight.shadow.mapSize.height = 2048;
        dirLight.shadow.camera.left = -50;
        dirLight.shadow.camera.right = 50;
        dirLight.shadow.camera.top = 50;
        dirLight.shadow.camera.bottom = -50;
        dirLight.shadow.bias = -0.001;
        scene.add(dirLight);

        // --- Materials ---
        const materials = {
            water: new THREE.MeshLambertMaterial({ color: 0x2277cc }),
            wave: new THREE.MeshLambertMaterial({ color: 0x44aadd }),
            hullDark: new THREE.MeshLambertMaterial({ color: 0x4a2e15 }),
            hullDeck: new THREE.MeshLambertMaterial({ color: 0x8b5a2b }),
            mast: new THREE.MeshLambertMaterial({ color: 0x3b2412 }),
            sail: new THREE.MeshLambertMaterial({ color: 0xfff8e7 }),
            flag: new THREE.MeshLambertMaterial({ color: 0xdd2222 }),
            dock: new THREE.MeshLambertMaterial({ color: 0x6b4423 }),
            crate: new THREE.MeshLambertMaterial({ color: 0xa0522d }),
            lighthouseWhite: new THREE.MeshLambertMaterial({ color: 0xeeeeee }),
            lighthouseRed: new THREE.MeshLambertMaterial({ color: 0xcc2222 }),
            lighthouseLight: new THREE.MeshBasicMaterial({ color: 0xffffaa }),
            rock: new THREE.MeshLambertMaterial({ color: 0x666666 }),
            cloud: new THREE.MeshLambertMaterial({ color: 0xffffff })
        };

        // --- Helper Function to create Voxels ---
        const geometry = new THREE.BoxGeometry(1, 1, 1);
        function addVoxel(x, y, z, sx, sy, sz, material, parent = scene) {
            const mesh = new THREE.Mesh(geometry, material);
            mesh.position.set(x, y, z);
            mesh.scale.set(sx, sy, sz);
            mesh.castShadow = true;
            mesh.receiveShadow = true;
            parent.add(mesh);
            return mesh;
        }

        // --- Build Ocean ---
        addVoxel(0, -1, 0, 200, 2, 200, materials.water).castShadow = false;
        
        const waves = [];
        for(let i = 0; i < 80; i++) {
            const x = (Math.random() - 0.5) * 120;
            const z = (Math.random() - 0.5) * 120;
            const wave = addVoxel(x, 0.05, z, 2 + Math.random()*2, 0.1, 0.5, materials.wave);
            wave.castShadow = false;
            waves.push(wave);
        }

        // --- Build Ship ---
        const ship = new THREE.Group();
        scene.add(ship);

        // Ship Hull
        for (let x = -10; x <= 10; x++) {
            let width = 4;
            if (x > 5) width = Math.max(0, 4 - (x - 5));       // Pointy bow
            if (x < -7) width = Math.max(2, 4 - (-7 - x));     // Squared stern
            
            for (let z = -width; z <= width; z++) {
                addVoxel(x, 0.5, z, 1, 1, 1, materials.hullDark, ship);
                addVoxel(x, 1.5, z, 1, 0.5, 1, materials.hullDeck, ship);
                if (z === width || z === -width) {
                    addVoxel(x, 1.0, z, 1, 0.2, 1, materials.lighthouseWhite, ship); // White stripe
                }
            }
        }

        // Masts
        addVoxel(0, 8.5, 0, 0.8, 14, 0.8, materials.mast, ship);  // Main mast
        addVoxel(6, 6.5, 0, 0.6, 10, 0.6, materials.mast, ship);  // Fore mast
        addVoxel(-6, 6.5, 0, 0.6, 10, 0.6, materials.mast, ship); // Mizzen mast
        addVoxel(0, 13, 0, 1.5, 0.5, 1.5, materials.hullDark, ship); // Crow's nest

        // Sails (built voxel by voxel for a curved billow effect)
        function buildSail(mastX, yBase, height, width, direction = 1) {
            for(let y = 0; y < height; y++) {
                for(let z = -Math.floor(width/2); z <= Math.floor(width/2); z++) {
                    let xOffset = direction * (0.8 + 0.4 * Math.cos(z * 0.8));
                    addVoxel(mastX + xOffset, yBase + y + 0.5, z, 0.2, 1, 1, materials.sail, ship);
                }
            }
        }
        buildSail(0, 6, 5, 5, 1);  
        buildSail(0, 12, 4, 4, 1); 
        buildSail(6, 5, 4, 4, 1);  
        buildSail(6, 10, 3, 3, 1); 
        buildSail(-6, 5, 4, 4, -1); 

        // Flag
        addVoxel(0, 16, 0, 0.4, 1, 0.4, materials.hullDark, ship);
        for(let z = 0; z <= 4; z++) {
            let yOffset = Math.sin(z * 0.8) * 0.4;
            addVoxel(0, 16 + yOffset, z, 0.2, 0.8, 1, materials.flag, ship);
        }

        // Gangplank connecting ship to dock
        addVoxel(11.5, 1.6, 0, 3, 0.3, 1, materials.dock, scene);

        // --- Build Harbor ---
        const harbor = new THREE.Group();
        harbor.position.set(13, 0, 0); // Moved close to the ship
        scene.add(harbor);

        // Wooden Dock
        for (let x = 0; x <= 10; x++) {
            for (let z = -8; z <= 8; z++) {
                addVoxel(x, 1.5, z, 1, 0.5, 1, materials.dock, harbor);
            }
        }

        // Dock Pillars
        for (let x = 0; x <= 10; x += 3) {
            for (let z = -6; z <= 6; z += 4) {
                addVoxel(x, -0.5, z, 0.8, 3, 0.8, materials.hullDark, harbor);
            }
        }

        // Cargo Crates
        addVoxel(3, 2.25, 3, 1, 1, 1, materials.crate, harbor);
        addVoxel(4, 2.25, 3.5, 1, 1, 1, materials.crate, harbor);
        addVoxel(3.5, 3.25, 3.25, 1, 1, 1, materials.crate, harbor);
        addVoxel(8, 2.25, -4, 1, 1, 1, materials.crate, harbor);

        // Harbor Crane
        addVoxel(8, 6.5, 0, 1, 11, 1, materials.mast, harbor);
        addVoxel(4, 11.5, 0, 9, 1, 1, materials.mast, harbor);
        addVoxel(2, 8, 0, 0.1, 6, 0.1, materials.hullDark, harbor); // Rope
        addVoxel(2, 4.5, 0, 1.5, 1.5, 1.5, materials.crate, harbor); // Hanging crate

        // --- Build Rowboat ---
        const rowboat = new THREE.Group();
        rowboat.position.set(18, 0, 12);
        scene.add(rowboat);

        for (let x = -3; x <= 3; x++) {
            let width = Math.max(0, 2 - Math.abs(x)/2);
            for (let z = -width; z <= width; z++) {
                addVoxel(x, 0.25, z, 1, 0.5, 1, materials.hullDeck, rowboat);
            }
        }
        addVoxel(0, 0.6, 3, 0.2, 0.2, 4, materials.mast, rowboat); // Oar
        addVoxel(0, 0.6, -3, 0.2, 0.2, 4, materials.mast, rowboat); // Oar

        // --- Build Lighthouse ---
        const lighthouse = new THREE.Group();
        lighthouse.position.set(-25, 0, -20);
        scene.add(lighthouse);

        // Rocky Base
        for(let i = 0; i < 20; i++) {
            let rx = (Math.random() - 0.5) * 12;
            let rz = (Math.random() - 0.5) * 12;
            let ry = Math.random() * 1.5 - 0.5;
            addVoxel(rx, ry, rz, 2 + Math.random()*2, 2 + Math.random()*2, 2 + Math.random()*2, materials.rock, lighthouse);
        }

        // Tower with Stripes
        for (let y = 0; y < 12; y++) {
            let mat = (Math.floor(y/3) % 2 === 0) ? materials.lighthouseWhite : materials.lighthouseRed;
            addVoxel(0, y + 1.5, 0, 4, 1, 4, mat, lighthouse);
        }
        
        // Light Room & Roof
        addVoxel(0, 13.5, 0, 3, 2, 3, materials.lighthouseLight, lighthouse);
        addVoxel(0, 15, 0, 4, 1, 4, materials.lighthouseRed, lighthouse); 
        addVoxel(0, 16, 0, 1, 1, 1, materials.mast, lighthouse); 

        // Rotating Light Beam (using a low-poly cone to match voxel aesthetic)
        const beamGeom = new THREE.ConeGeometry(3, 18, 4);
        beamGeom.rotateX(-Math.PI / 2); 
        beamGeom.translate(0, 0, 9); 
        const beamMat = new THREE.MeshBasicMaterial({ 
            color: 0xffffaa, transparent: true, opacity: 0.25, 
            side: THREE.DoubleSide, depthWrite: false, blending: THREE.AdditiveBlending 
        });
        const beam = new THREE.Mesh(beamGeom, beamMat);
        beam.position.set(0, 13.5, 0);
        lighthouse.add(beam);

        // --- Build Voxel Clouds ---
        function createCloud(x, y, z) {
            const cloud = new THREE.Group();
            cloud.position.set(x, y, z);
            addVoxel(0, 0, 0, 4, 1, 2, materials.cloud, cloud);
            addVoxel(2, 0.5, 0, 3, 1, 2, materials.cloud, cloud);
            addVoxel(-2, -0.5, 1, 2, 1, 2, materials.cloud, cloud);
            addVoxel(1, 1, 0, 2, 1, 2, materials.cloud, cloud);
            scene.add(cloud);
            return cloud;
        }
        const clouds = [
            createCloud(-30, 25, -40),
            createCloud(20, 30, -50),
            createCloud(40, 20, 10),
            createCloud(-10, 35, -60)
        ];

        // --- Animation Loop ---
        const clock = new THREE.Clock();
        function animate() {
            requestAnimationFrame(animate);
            const time = clock.getElapsedTime();

            // Bobbing ship
            ship.position.y = Math.sin(time * 1.5) * 0.15;
            ship.rotation.z = Math.sin(time * 1.2) * 0.02;
            ship.rotation.x = Math.cos(time * 1.3) * 0.02;

            // Bobbing rowboat
            rowboat.position.y = Math.sin(time * 1.5 + 2) * 0.1;
            rowboat.rotation.z = Math.sin(time * 1.4) * 0.05;

            // Rotating lighthouse beam
            beam.rotation.y = -time * 0.5;

            // Shimmering waves
            for(let i = 0; i < waves.length; i++) {
                waves[i].position.y = 0.05 + Math.sin(time * 2 + i) * 0.05;
            }

            // Drifting clouds
            clouds.forEach((c, i) => {
                c.position.x += 0.01 + (i * 0.002);
                if(c.position.x > 100) c.position.x = -100; // Loop back around
            });

            controls.update();
            renderer.render(scene, camera);
        }
        animate();

        // --- Handle Window Resize ---
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    </script>
</body>
</html>
```