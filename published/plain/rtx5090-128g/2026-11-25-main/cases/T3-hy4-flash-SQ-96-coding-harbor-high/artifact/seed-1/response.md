Here is the complete HTML file. It uses Three.js to render a low-poly, voxel-style scene with a sailing ship docked at a harbor. It includes orbit controls so you can view it from any angle using your mouse.

Save the code below into a single file (e.g., `harbor.html`) and open it in Google Chrome.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Voxel Harbor - A Sailing Ship</title>
    <style>
        body { 
            margin: 0; 
            overflow: hidden; 
            background-color: #87CEEB; 
            font-family: sans-serif;
        }
        canvas { 
            display: block; 
        }
        #ui {
            position: absolute;
            top: 15px;
            width: 100%;
            text-align: center;
            color: white;
            font-size: 20px;
            font-weight: bold;
            pointer-events: none;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
        }
        #instructions {
            font-size: 14px;
            font-weight: normal;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div id="ui">
        A Sailing Ship Calling at a Harbor
        <div id="instructions">Click and drag to orbit • Scroll to zoom</div>
    </div>

    <!-- Three.js and OrbitControls from CDN -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>

    <script>
        // 1. Basic Setup
        const scene = new THREE.Scene();
        scene.fog = new THREE.Fog(0x87CEEB, 40, 90);
        scene.background = new THREE.Color(0x87CEEB);

        const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(25, 22, 28);

        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        document.body.appendChild(renderer.domElement);

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.target.set(-2, 2, 0);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.maxPolarAngle = Math.PI / 2 - 0.05; // Prevent camera from going below ground

        // 2. Lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        scene.add(ambientLight);

        const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
        dirLight.position.set(20, 40, 20);
        dirLight.castShadow = true;
        dirLight.shadow.camera.top = 50;
        dirLight.shadow.camera.bottom = -50;
        dirLight.shadow.camera.left = -50;
        dirLight.shadow.camera.right = 50;
        dirLight.shadow.mapSize.width = 2048;
        dirLight.shadow.mapSize.height = 2048;
        scene.add(dirLight);

        // 3. Voxel Helper Functions
        const materials = {};
        const geometryCache = {};

        function getMaterial(color) {
            if (!materials[color]) {
                materials[color] = new THREE.MeshStandardMaterial({ color: color, roughness: 0.8 });
            }
            return materials[color];
        }

        function getGeometry(w, h, d) {
            const key = `${w},${h},${d}`;
            if (!geometryCache[key]) {
                geometryCache[key] = new THREE.BoxGeometry(w, h, d);
            }
            return geometryCache[key];
        }

        function createVoxel(x, y, z, color, w = 1, h = 1, d = 1) {
            const mesh = new THREE.Mesh(getGeometry(w, h, d), getMaterial(color));
            mesh.position.set(x, y, z);
            mesh.castShadow = true;
            mesh.receiveShadow = true;
            return mesh;
        }

        // 4. Build the Scene

        // -- Water (Instanced Mesh for performance) --
        const waterColors = [0x1E90FF, 0x00BFFF, 0x4682B4, 0x1e90ff];
        const waterGeometry = new THREE.BoxGeometry(1, 0.8, 1);
        const waterMaterial = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.6, metalness: 0.1 });
        const waterMesh = new THREE.InstancedMesh(waterGeometry, waterMaterial, 44 * 51);
        const dummy = new THREE.Object3D();
        let wIndex = 0;
        for (let x = -13; x <= 30; x++) {
            for (let z = -25; z <= 25; z++) {
                dummy.position.set(x, -0.4, z);
                dummy.updateMatrix();
                waterMesh.setMatrixAt(wIndex, dummy.matrix);
                waterMesh.setColorAt(wIndex, new THREE.Color(waterColors[Math.floor(Math.random() * waterColors.length)]));
                wIndex++;
            }
        }
        waterMesh.receiveShadow = true;
        scene.add(waterMesh);

        // -- Foam around the ship --
        for (let i = 0; i < 40; i++) {
            let x = (Math.random() - 0.5) * 16;
            let z = -1 + (Math.random() - 0.5) * 16;
            if (Math.abs(x) < 5 && Math.abs(z + 1) < 6) {
                x = Math.sign(x || 1) * (5 + Math.random() * 2);
            }
            scene.add(createVoxel(x, 0, z, 0xE0FFFF, 0.8, 0.2, 0.8));
        }

        // -- Land / Coastline --
        const landColors = [0x228B22, 0x32CD32, 0x006400];
        for (let x = -30; x <= -14; x++) {
            for (let z = -25; z <= 25; z++) {
                let isStructure = (x === -18 && z >= -1 && z <= 1) || (x >= -23 && x <= -19 && (z === 8 || z === 5 || z === -6));
                let h = isStructure || Math.random() > 0.7 ? 2 : 1;
                for (let y = 0; y < h; y++) {
                    let color = y === 0 ? 0xF4A460 : landColors[Math.floor(Math.random() * landColors.length)];
                    scene.add(createVoxel(x, y, z, color));
                }
            }
        }

        // -- Wooden Harbor Dock --
        for (let x = -14; x <= -4; x++) {
            for (let z = -2; z <= 6; z++) {
                let color = Math.random() > 0.3 ? 0xA0522D : 0x8B4513;
                scene.add(createVoxel(x, 1, z, color));
            }
        }
        for (let x = -12; x <= -4; x += 3) {
            for (let z = -1; z <= 5; z += 3) {
                scene.add(createVoxel(x, 0, z, 0x5C4033));
            }
        }

        // -- Gangplank connecting dock to ship --
        scene.add(createVoxel(-4, 1.75, 0, 0xDEB887, 2.5, 0.25, 1));

        // -- Cargo Crates --
        function addCrate(x, z) {
            scene.add(createVoxel(x, 2, z, 0xCD853F));
            scene.add(createVoxel(x, 3, z, 0xCD853F));
        }
        addCrate(-6, 1);
        addCrate(-6, 2);
        addCrate(-5, 1);
        addCrate(-8, 4);
        addCrate(-9, 4);

        // -- Lighthouse --
        const lhGroup = new THREE.Group();
        lhGroup.position.set(-18, 2, 0);
        for (let y = 0; y < 8; y++) {
            let color = (y % 2 === 0) ? 0xFF0000 : 0xFFFFFF;
            let w = y > 5 ? 1 : 2; 
            for (let x = -w; x <= w; x++) {
                for (let z = -w; z <= w; z++) {
                    lhGroup.add(createVoxel(x, y, z, color));
                }
            }
        }
        lhGroup.add(createVoxel(0, 8, 0, 0xFFFF00)); // Beacon
        scene.add(lhGroup);

        const lhLight = new THREE.PointLight(0xFFFF00, 1.5, 30);
        lhLight.position.set(-18, 10, 0);
        scene.add(lhLight);

        // -- Houses on the coast --
        function addHouse(x, z, color) {
            const house = new THREE.Group();
            house.position.set(x, 2, z); 
            for (let dx = -1; dx <= 1; dx++) {
                for (let dz = -1; dz <= 1; dz++) {
                    house.add(createVoxel(dx, 0, dz, color));
                }
            }
            // Pyramid roof
            house.add(createVoxel(0, 1, 0, 0x8B0000));
            for (let dx = -1; dx <= 1; dx++) {
                for (let dz = -1; dz <= 1; dz++) {
                    if (Math.abs(dx) === 1 || Math.abs(dz) === 1) {
                        house.add(createVoxel(dx, 1, dz, 0xA52A2A));
                    }
                }
            }
            scene.add(house);
        }
        addHouse(-21, 8, 0xEEE8AA);
        addHouse(-21, 5, 0xF0FFFF);
        addHouse(-21, -6, 0xFFE4C4);

        // -- The Sailing Ship --
        const shipGroup = new THREE.Group();
        shipGroup.position.set(0, 0, -1);

        // Hull shape definition
        const widths = {
            '-5': 1, '-4': 2, '-3': 3, '-2': 4, '-1': 4,
            '0': 4, '1': 4, '2': 4, '3': 3, '4': 2, '5': 1
        };

        for (let z = -5; z <= 5; z++) {
            let w = widths[z];
            for (let x = -w; x <= w; x++) {
                shipGroup.add(createVoxel(x, 1, z, 0x8B4513)); // Hull body
                if (x === -w || x === w || z === -5 || z === 5) {
                    shipGroup.add(createVoxel(x, 2, z, 0xA0522D)); // Rim
                } else {
                    shipGroup.add(createVoxel(x, 2, z, 0xDEB887)); // Deck
                }
            }
        }

        // Mast
        for (let y = 3; y <= 12; y++) {
            shipGroup.add(createVoxel(0, y, 0, 0x5C4033));
        }
        // Crow's nest
        shipGroup.add(createVoxel(0, 9, 0, 0x8B4513, 2, 0.5, 2));

        // Lower Sail
        for (let x = -3; x <= 3; x++) {
            let height = 4 - Math.floor(Math.abs(x) / 2); 
            for (let y = 4; y < 4 + height; y++) {
                let zOffset = Math.abs(x) * 0.15; 
                shipGroup.add(createVoxel(x, y, zOffset, 0xF5F5DC));
            }
        }
        // Upper Sail
        for (let x = -2; x <= 2; x++) {
            let height = 3 - Math.floor(Math.abs(x) / 2);
            for (let y = 10; y < 10 + height; y++) {
                let zOffset = Math.abs(x) * 0.15;
                shipGroup.add(createVoxel(x, y, zOffset, 0xFFFAF0));
            }
        }
        // Red Flag
        shipGroup.add(createVoxel(1, 13, 0, 0xFF0000));
        shipGroup.add(createVoxel(2, 13, 0, 0xFF0000));
        shipGroup.add(createVoxel(3, 13, 0, 0xFF0000));

        // Cannon
        shipGroup.add(createVoxel(2, 3, -3, 0x222222, 1, 0.5, 2));
        shipGroup.add(createVoxel(2, 2.8, -3, 0x8B4513, 1.2, 0.5, 1));

        // Bowsprit
        shipGroup.add(createVoxel(0, 2.5, -6, 0x5C4033, 0.5, 0.5, 3));

        scene.add(shipGroup);

        // -- Seagulls --
        const birds = [];
        for (let i = 0; i < 6; i++) {
            const bird = new THREE.Group();
            const wing1 = createVoxel(-0.5, 0, 0, 0xFFFFFF, 1, 0.1, 0.3);
            const wing2 = createVoxel(0.5, 0, 0, 0xFFFFFF, 1, 0.1, 0.3);
            bird.add(wing1);
            bird.add(wing2);
            scene.add(bird);
            birds.push({ 
                mesh: bird, 
                speed: 0.01 + Math.random() * 0.015, 
                angle: Math.random() * Math.PI * 2,
                radius: 10 + Math.random() * 10,
                height: 8 + Math.random() * 6
            });
        }

        // 5. Animation Loop
        const clock = new THREE.Clock();

        function animate() {
            requestAnimationFrame(animate);
            const t = clock.getElapsedTime();

            // Animate birds
            birds.forEach(b => {
                b.angle += b.speed;
                b.mesh.position.x = Math.cos(b.angle) * b.radius - 2;
                b.mesh.position.z = Math.sin(b.angle) * b.radius;
                b.mesh.position.y = b.height + Math.sin(t * 2 + b.angle) * 0.5;
                
                // Face direction of travel
                b.mesh.lookAt(
                    b.mesh.position.x + Math.cos(b.angle + Math.PI / 2) * 10, 
                    b.mesh.position.y, 
                    b.mesh.position.z + Math.sin(b.angle + Math.PI / 2) * 10
                );
                
                // Flap wings
                const flap = Math.sin(t * 15 + b.angle) * 0.5;
                b.mesh.children[0].rotation.z = flap;
                b.mesh.children[1].rotation.z = -flap;
            });

            // Bob the ship in the water
            shipGroup.position.y = Math.sin(t * 2) * 0.1;
            shipGroup.rotation.z = Math.sin(t * 1.5) * 0.02;

            controls.update();
            renderer.render(scene, camera);
        }
        animate();

        // 6. Handle Window Resizing
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    </script>
</body>
</html>
```