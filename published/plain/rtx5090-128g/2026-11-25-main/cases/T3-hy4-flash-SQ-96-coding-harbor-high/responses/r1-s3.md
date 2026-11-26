Here is the complete, single HTML file containing the 3D voxel art scene. It uses the Three.js library and OrbitControls to provide an interactive, mouse-viewable experience. 

Just copy the code below, save it as an `.html` file (for example, `voxel_harbor.html`), and open it in Google Chrome.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Voxel Sailing Ship at Harbor</title>
    <style>
        body {
            margin: 0;
            overflow: hidden;
            background-color: #87CEEB; /* Sky blue fallback */
            font-family: sans-serif;
            user-select: none;
        }
        canvas {
            display: block;
        }
        #info {
            position: absolute;
            top: 15px;
            left: 15px;
            color: white;
            background: rgba(0, 0, 0, 0.6);
            padding: 12px 18px;
            border-radius: 8px;
            pointer-events: none;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        #info h1 {
            margin: 0 0 5px 0;
            font-size: 18px;
        }
        #info p {
            margin: 0;
            font-size: 13px;
            color: #cccccc;
        }
    </style>
    <!-- Load Three.js and OrbitControls from CDN -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
    <div id="info">
        <h1>Voxel Harbor</h1>
        <p>Drag to rotate • Scroll to zoom</p>
    </div>

    <script>
        // --- Scene Setup ---
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x87CEEB); // Sky blue
        scene.fog = new THREE.Fog(0x87CEEB, 60, 150);

        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(25, 18, 25);

        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        document.body.appendChild(renderer.domElement);

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.target.set(10, 4, 0); // Focus on the dock and ship
        controls.maxPolarAngle = Math.PI / 2 - 0.05; // Don't go below ground

        // --- Lighting ---
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        scene.add(ambientLight);

        const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
        dirLight.position.set(20, 30, 10);
        dirLight.castShadow = true;
        dirLight.shadow.mapSize.width = 2048;
        dirLight.shadow.mapSize.height = 2048;
        dirLight.shadow.camera.left = -50;
        dirLight.shadow.camera.right = 50;
        dirLight.shadow.camera.top = 50;
        dirLight.shadow.camera.bottom = -50;
        dirLight.shadow.bias = -0.001;
        scene.add(dirLight);

        // --- Caching Geometries & Materials for Performance ---
        const materials = {};
        const geometries = {};

        function getMaterial(color) {
            if (!materials[color]) {
                materials[color] = new THREE.MeshLambertMaterial({ color: color });
            }
            return materials[color];
        }

        function createVoxel(x, y, z, color, w = 1, h = 1, d = 1) {
            const geoKey = `${w}_${h}_${d}`;
            if (!geometries[geoKey]) {
                geometries[geoKey] = new THREE.BoxGeometry(w, h, d);
            }
            const mesh = new THREE.Mesh(geometries[geoKey], getMaterial(color));
            mesh.position.set(x, y, z);
            mesh.castShadow = true;
            mesh.receiveShadow = true;
            return mesh;
        }

        // --- Water ---
        const waterGroup = new THREE.Group();
        const waterGeo = new THREE.PlaneGeometry(200, 200);
        const waterMat = new THREE.MeshLambertMaterial({ color: 0x1e6b9e });
        const waterMesh = new THREE.Mesh(waterGeo, waterMat);
        waterMesh.rotation.x = -Math.PI / 2;
        waterMesh.position.y = 0;
        waterMesh.receiveShadow = true;
        waterGroup.add(waterMesh);

        // Animated Wave Voxels
        const waveColors = [0x0077A6, 0x0080B3, 0x005C80];
        const waves = [];
        for (let i = 0; i < 300; i++) {
            let x = (Math.random() - 0.5) * 100;
            let z = (Math.random() - 0.5) * 100;
            
            // Clear area for dock, ship, and lighthouse
            if (x > 0 && x < 20 && Math.abs(z) < 10) continue;
            if (x > 20 && x < 28 && z > -16 && z < -8) continue;

            let c = waveColors[Math.floor(Math.random() * waveColors.length)];
            let w = Math.random() > 0.6 ? 2 : 1;
            let d = Math.random() > 0.6 ? 2 : 1;
            
            let voxel = createVoxel(x, 0.1, z, c, w, 0.2, d);
            voxel.castShadow = false;
            voxel.receiveShadow = false;
            waterGroup.add(voxel);
            waves.push(voxel);
        }
        scene.add(waterGroup);

        // --- The Sailing Ship ---
        const shipGroup = new THREE.Group();
        const hullColor = 0x6b3a20;
        const deckColor = 0xc19a6b;
        const sailColor = 0xfdfdfd;
        const mastColor = 0x4a2511;
        const redStripe = 0xd63031;

        // Hull generation
        for (let z = -8; z <= 8; z++) {
            let maxX = z === 8 ? 0 : (Math.abs(z) === 7 || z === -8 ? 1 : 2);
            let minY = Math.abs(z) > 5 ? 0 : -1;
            
            for (let y = minY; y <= 1; y++) {
                for (let x = -maxX; x <= maxX; x++) {
                    shipGroup.add(createVoxel(x, y, z, hullColor));
                }
            }
            // Deck
            for (let x = -maxX; x <= maxX; x++) {
                shipGroup.add(createVoxel(x, 2, z, deckColor));
            }
        }

        // Gunwales (side rails)
        for (let z = -8; z <= 8; z++) {
            let maxX = z === 8 ? 0 : (Math.abs(z) === 7 || z === -8 ? 1 : 2);
            if (maxX > 0) {
                shipGroup.add(createVoxel(-maxX, 3, z, mastColor));
                shipGroup.add(createVoxel(maxX, 3, z, mastColor));
            }
        }

        // Masts, Yardarms, and Curved Sails
        function addMast(zPos, mastHeight, sailBottom, sailTop, sailWidth) {
            for (let y = 3; y <= mastHeight; y++) {
                shipGroup.add(createVoxel(0, y, zPos, mastColor));
            }
            for (let x = -sailWidth; x <= sailWidth; x++) {
                shipGroup.add(createVoxel(x, sailTop, zPos, mastColor));
            }
            for (let y = sailBottom; y <= sailTop - 1; y++) {
                for (let x = -sailWidth + 1; x <= sailWidth - 1; x++) {
                    // Creates a billowing curve for the sail
                    let zOffset = Math.round(Math.sin(Math.PI * (x + sailWidth) / (2 * sailWidth)) * 1.5);
                    let color = (y === sailBottom + 1) ? redStripe : sailColor;
                    shipGroup.add(createVoxel(x, y, zPos + zOffset, color));
                }
            }
        }

        addMast(4, 13, 6, 11, 4);  // Foremast
        addMast(-1, 16, 7, 13, 5); // Mainmast
        addMast(-6, 11, 5, 9, 3);  // Mizzenmast

        // Crows nest & Flags
        for (let x = -1; x <= 1; x++) {
            for (let z = -2; z <= 0; z++) {
                shipGroup.add(createVoxel(x, 14, z, hullColor));
            }
        }
        function addFlag(zPos, mastHeight) {
            for (let z = zPos + 1; z <= zPos + 3; z++) {
                shipGroup.add(createVoxel(0, mastHeight - 1, z, redStripe));
            }
        }
        addFlag(4, 13); addFlag(-1, 16); addFlag(-6, 11);

        // Bowsprit
        for (let z = 9; z <= 11; z++) {
            shipGroup.add(createVoxel(0, 3, z, mastColor));
        }

        shipGroup.position.set(4, 0, 0);
        scene.add(shipGroup);

        // --- The Harbor Dock & Buildings ---
        const dockGroup = new THREE.Group();
        const dockColor = 0x8a5a33;

        // Pier planks
        for (let x = 5; x <= 15; x++) {
            for (let z = -4; z <= 4; z++) {
                dockGroup.add(createVoxel(x, 1, z, dockColor));
            }
        }

        // Dock support posts
        for (let x = 6; x <= 15; x += 3) {
            for (let z of [-4, 4]) {
                dockGroup.add(createVoxel(x, 0, z, mastColor));
                dockGroup.add(createVoxel(x, -1, z, mastColor));
            }
        }

        // Gangplank bridging to ship
        for (let x = 5; x <= 7; x++) {
            for (let z = -1; z <= 1; z++) {
                dockGroup.add(createVoxel(x, 2, z, 0x5c3a21)); 
            }
        }

        // Crates and Barrels
        dockGroup.add(createVoxel(12, 2, -2, 0xA0522D));
        dockGroup.add(createVoxel(12, 2, -1, 0xA0522D));
        dockGroup.add(createVoxel(10, 2, 2, 0xD2B48C));
        dockGroup.add(createVoxel(11, 2, 3, 0xD2B48C));
        dockGroup.add(createVoxel(10, 3, 2, 0xD2B48C)); // Stacked crate

        // Dockside flag pole
        for (let y = 2; y <= 8; y++) dockGroup.add(createVoxel(6, y, 4, mastColor));
        dockGroup.add(createVoxel(6, 7, 5, 0xFFFF00));
        dockGroup.add(createVoxel(6, 7, 6, 0xFFFF00));

        // Dock Warehouse
        const wallColor = 0xdddddd;
        const roofColor = 0xa93226;
        for (let x = 14; x <= 18; x++) {
            for (let y = 2; y <= 5; y++) {
                for (let z = -4; z <= 4; z++) {
                    if (x === 14 && Math.abs(z) <= 1 && y <= 3) continue; // Doorway
                    if (x === 14 && Math.abs(z) === 3 && y === 4) continue; // Window
                    if (x > 14 && x < 18 && z > -4 && z < 4 && y < 5) continue; // Interior hollow
                    dockGroup.add(createVoxel(x, y, z, wallColor));
                }
            }
        }
        for (let x = 13; x <= 19; x++) {
            for (let z = -5; z <= 5; z++) {
                dockGroup.add(createVoxel(x, 6, z, roofColor));
            }
        }
        for (let z = -5; z <= 5; z++) dockGroup.add(createVoxel(16, 7, z, roofColor)); // Roof peak

        scene.add(dockGroup);

        // --- Lighthouse ---
        const lighthouseGroup = new THREE.Group();
        const lhRed = 0xFF0000;
        
        // Rocky Island Base
        for (let y = -2; y <= 0; y++) {
            for (let x = -3; x <= 3; x++) {
                for (let z = -3; z <= 3; z++) {
                    if (x*x + z*z + y*y < 10) {
                        lighthouseGroup.add(createVoxel(x, y, z, 0x555555));
                    }
                }
            }
        }
        
        // Tower (Red & White stripes)
        for (let y = 0; y <= 8; y++) {
            let color = (Math.floor(y/2) % 2 === 0) ? 0xFFFFFF : lhRed;
            for (let x = -1; x <= 1; x++) {
                for (let z = -1; z <= 1; z++) {
                    if (Math.abs(x) === 1 && Math.abs(z) === 1) continue; // Chamfer corners
                    if (x === 0 && z === 0) continue; // Hollow center
                    lighthouseGroup.add(createVoxel(x, y, z, color));
                }
            }
        }
        
        // Top deck, Light room, and Roof
        for (let x = -2; x <= 2; x++) {
            for (let z = -2; z <= 2; z++) {
                if (Math.abs(x) === 2 && Math.abs(z) === 2) continue;
                lighthouseGroup.add(createVoxel(x, 9, z, 0x555555));
            }
        }
        for (let y = 10; y <= 12; y++) {
            for (let x = -1; x <= 1; x++) {
                for (let z = -1; z <= 1; z++) {
                    if (Math.abs(x) === 1 && Math.abs(z) === 1) continue;
                    if (x === 0 && z === 0) continue;
                    lighthouseGroup.add(createVoxel(x, y, z, 0xFFFF00));
                }
            }
        }
        const lightCore = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.8, 0.8), new THREE.MeshBasicMaterial({ color: 0xFFFFFF }));
        lightCore.position.set(0, 11, 0);
        lighthouseGroup.add(lightCore);

        for (let x = -2; x <= 2; x++) {
            for (let z = -2; z <= 2; z++) {
                if (Math.abs(x) === 2 && Math.abs(z) === 2) continue;
                lighthouseGroup.add(createVoxel(x, 13, z, lhRed));
            }
        }
        lighthouseGroup.add(createVoxel(0, 14, 0, lhRed));

        // Rotating Light Beam
        const beamGeo = new THREE.ConeGeometry(3.5, 25, 8);
        beamGeo.rotateZ(-Math.PI / 2);
        beamGeo.translate(12.5, 0, 0); 
        const beamMat = new THREE.MeshBasicMaterial({ color: 0xFFFF00, transparent: true, opacity: 0.25, depthWrite: false });
        const beam = new THREE.Mesh(beamGeo, beamMat);
        beam.position.set(0, 11, 0);
        lighthouseGroup.add(beam);

        lighthouseGroup.position.set(24, 0, -12);
        scene.add(lighthouseGroup);

        // --- Rowboat ---
        const rowboatGroup = new THREE.Group();
        for (let z = -2; z <= 2; z++) {
            let maxX = Math.abs(z) === 2 ? 0 : 1;
            for (let x = -maxX; x <= maxX; x++) {
                rowboatGroup.add(createVoxel(x, 0, z, hullColor));
            }
        }
        rowboatGroup.add(createVoxel(-2, 0, 0, deckColor));
        rowboatGroup.add(createVoxel(2, 0, 0, deckColor));
        rowboatGroup.position.set(10, -0.2, 7);
        scene.add(rowboatGroup);

        // --- Clouds ---
        const cloudGroup = new THREE.Group();
        const cloudMat = new THREE.MeshLambertMaterial({ color: 0xFFFFFF });
        function addCloud(x, y, z, scale) {
            const cloud = new THREE.Group();
            for (let i = -2; i <= 2; i++) {
                for (let j = -1; j <= 1; j++) {
                    if (Math.random() > 0.3) {
                        let mesh = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), cloudMat);
                        mesh.position.set(i, j, (Math.random() - 0.5));
                        cloud.add(mesh);
                    }
                }
            }
            cloud.position.set(x, y, z);
            cloud.scale.set(scale, scale, scale);
            cloudGroup.add(cloud);
        }
        addCloud(-20, 25, -30, 3);
        addCloud(30, 30, -40, 4);
        addCloud(-40, 20, 10, 2);
        addCloud(10, 35, -20, 2);
        scene.add(cloudGroup);

        // --- Seagulls ---
        const birds = [];
        const birdMat = new THREE.MeshLambertMaterial({ color: 0xFFFFFF });
        for (let i = 0; i < 10; i++) {
            let bird = new THREE.Group();
            let leftWing = new THREE.Mesh(new THREE.BoxGeometry(1, 0.2, 0.2), birdMat);
            leftWing.position.x = -0.5;
            let rightWing = new THREE.Mesh(new THREE.BoxGeometry(1, 0.2, 0.2), birdMat);
            rightWing.position.x = 0.5;
            bird.add(leftWing);
            bird.add(rightWing);
            
            bird.position.set((Math.random() - 0.5) * 40 + 10, Math.random() * 10 + 10, (Math.random() - 0.5) * 40);
            scene.add(bird);
            birds.push({ group: bird, leftWing: leftWing, rightWing: rightWing, offset: Math.random() * Math.PI * 2 });
        }

        // --- Window Resize Handling ---
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });

        // --- Animation Loop ---
        function animate() {
            requestAnimationFrame(animate);
            const time = Date.now() * 0.001;
            
            // Ship bobbing on the waves
            shipGroup.position.y = Math.sin(time * 1.5) * 0.3;
            shipGroup.rotation.z = Math.sin(time) * 0.015;
            shipGroup.rotation.x = Math.cos(time * 1.2) * 0.015;
            
            // Rowboat bobbing
            rowboatGroup.position.y = -0.2 + Math.sin(time * 2 + 5) * 0.15;
            
            // Animate ocean wave blocks
            waves.forEach(wave => {
                wave.position.y = 0.1 + Math.sin(time * 2 + wave.position.x * 0.5 + wave.position.z * 0.5) * 0.1;
            });
            
            // Drift clouds
            cloudGroup.children.forEach((cloud, idx) => {
                cloud.position.x += 0.005 * (idx % 2 === 0 ? 1 : -1);
                if (cloud.position.x > 60) cloud.position.x = -60;
                if (cloud.position.x < -60) cloud.position.x = 60;
            });

            // Flap bird wings & drift
            birds.forEach(bird => {
                let flap = Math.sin(time * 10 + bird.offset) * 0.5;
                bird.leftWing.rotation.z = flap;
                bird.rightWing.rotation.z = -flap;
                bird.group.position.x += 0.02;
                if (bird.group.position.x > 30) bird.group.position.x = -10;
            });

            // Rotate lighthouse beam
            beam.rotation.y = time * 2;

            controls.update();
            renderer.render(scene, camera);
        }
        
        animate();
    </script>
</body>
</html>
```