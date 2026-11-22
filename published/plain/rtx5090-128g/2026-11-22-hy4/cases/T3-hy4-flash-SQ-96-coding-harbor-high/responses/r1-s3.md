Here is a complete, single HTML file containing the 3D voxel art scene. It uses Three.js and OrbitControls via CDN, so you don't need to install anything. 

Just copy the code below, save it as an `.html` file (e.g., `voxel-harbor.html`), and double-click to open it in Chrome. You can click and drag to rotate the camera and scroll to zoom.

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
            background-color: #87CEEB; 
            font-family: sans-serif;
        }
        #info { 
            position: absolute; 
            top: 15px; 
            left: 20px; 
            color: white; 
            pointer-events: none; 
            text-shadow: 1px 1px 3px rgba(0,0,0,0.8); 
        }
        #info h2 { margin: 0 0 5px 0; font-size: 24px; }
        #info p { margin: 0; font-size: 14px; opacity: 0.9; }
        canvas { display: block; }
    </style>
</head>
<body>
    <div id="info">
        <h2>Voxel Harbor</h2>
        <p>Drag to rotate • Scroll to zoom</p>
    </div>

    <!-- Three.js and OrbitControls from CDN -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    
    <script>
        // --- SCENE SETUP ---
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x87CEEB);
        scene.fog = new THREE.Fog(0x87CEEB, 50, 120);

        const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(35, 25, 40);

        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        document.body.appendChild(renderer.domElement);

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.target.set(5, 6, 0);
        controls.maxPolarAngle = Math.PI / 2 - 0.05; // Prevent going under the ground

        // --- LIGHTING ---
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        scene.add(ambientLight);

        const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
        dirLight.position.set(30, 50, 20);
        dirLight.castShadow = true;
        dirLight.shadow.mapSize.width = 2048;
        dirLight.shadow.mapSize.height = 2048;
        dirLight.shadow.camera.top = 40;
        dirLight.shadow.camera.bottom = -40;
        dirLight.shadow.camera.left = -40;
        dirLight.shadow.camera.right = 40;
        scene.add(dirLight);

        const fillLight = new THREE.DirectionalLight(0xaaccff, 0.3);
        fillLight.position.set(-20, 20, -20);
        scene.add(fillLight);

        // --- VOXEL ENGINE ---
        const voxelMap = new Map();

        function addVoxel(x, y, z, color) {
            const key = `${x},${y},${z}`;
            voxelMap.set(key, { x, y, z, color });
        }

        function addBox(x1, y1, z1, x2, y2, z2, color) {
            for (let x = x1; x <= x2; x++)
                for (let y = y1; y <= y2; y++)
                    for (let z = z1; z <= z2; z++)
                        addVoxel(x, y, z, color);
        }

        // --- COLORS ---
        const C_WATER = 0x2980b9;
        const C_WATER_LIGHT = 0x3498db;
        const C_WOOD = 0x8B5A2B;
        const C_WOOD_DARK = 0x5c2c00;
        const C_STONE = 0x95a5a6;
        const C_STONE_DARK = 0x7f8c8d;
        const C_SAIL = 0xecf0f1;
        const C_SAIL_SHADOW = 0xbdc3c7;
        const C_RED = 0xc0392b;
        const C_YELLOW = 0xf1c40f;
        const C_WHITE = 0xffffff;
        const C_SAND = 0xf1c40f;
        const C_GREEN = 0x27ae60;
        const C_PALM = 0x2ecc71;

        // --- GENERATE SCENE ---

        // 1. Ocean & Waves
        const isShipArea = (x, z) => x >= -7 && x <= 7 && z >= -10 && z <= 16;
        const isDockArea = (x, z) => x >= 10 && x <= 25 && z >= -16 && z <= 16;

        for (let x = -35; x <= 35; x++) {
            for (let z = -35; z <= 35; z++) {
                const noise = Math.sin(x * 0.4) + Math.cos(z * 0.4) + Math.sin((x+z)*0.2);
                let color = noise > 1 ? C_WATER_LIGHT : C_WATER;
                
                // Skip water under the dock
                if (!(x >= 10 && x <= 25 && z >= -15 && z <= 15)) {
                    addVoxel(x, 0, z, color);
                }

                // Random wave crests
                if (noise > 1.6 && Math.random() > 0.4 && !isShipArea(x, z) && !isDockArea(x, z)) {
                    addVoxel(x, 1, z, C_WATER_LIGHT);
                }
            }
        }

        // 2. Tropical Island (Background)
        for(let x=-32; x<=-17; x++) {
            for(let z=-32; z<=-17; z++) {
                let dx = x + 24;
                let dz = z + 24;
                let dist = Math.sqrt(dx*dx + dz*dz);
                if (dist < 8) {
                    let h = Math.floor((8 - dist) / 2);
                    for(let y=1; y<=h; y++) addVoxel(x, y, z, C_SAND);
                    
                    if (h > 0 && Math.random() > 0.8) addVoxel(x, h+1, z, C_GREEN);
                    
                    // Palm tree
                    if (dx===0 && dz===0) {
                        addBox(x, h+1, z, x, h+4, z, C_WOOD_DARK);
                        addVoxel(x-1, h+5, z, C_PALM); addVoxel(x+1, h+5, z, C_PALM);
                        addVoxel(x, h+5, z-1, C_PALM); addVoxel(x, h+5, z+1, C_PALM);
                        addVoxel(x-2, h+4, z, C_PALM); addVoxel(x+2, h+4, z, C_PALM);
                    }
                }
            }
        }

        // 3. Harbor Dock & Pillars
        addBox(10, 0, -15, 25, 0, 15, C_STONE); // Base
        addBox(10, 1, -15, 25, 1, 15, C_WOOD);  // Planks
        for (let x of [10, 15, 20, 25]) {
            for (let z of [-15, -5, 5, 15]) {
                addBox(x, -1, z, x, 0, z, 0x2c3e50); // Pillars under dock
            }
        }

        // 4. Lighthouse
        addBox(21, 2, -1, 23, 6, 1, C_WHITE);
        addBox(21, 4, -1, 23, 4, 1, C_RED); // Stripe
        addBox(20, 7, -2, 24, 7, 2, C_STONE_DARK); // Gallery
        addBox(21, 8, -1, 23, 9, 1, C_YELLOW); // Light room
        addBox(20, 10, -2, 24, 10, 2, C_RED); // Roof
        addBox(24, 10, 0, 24, 12, 0, 0x6e2c00); // Flag pole
        addBox(25, 12, 0, 27, 12, 0, C_RED); // Flag

        // 5. Dock Details (Crates, People, Bollards)
        addBox(12, 2, 8, 13, 3, 9, C_WOOD_DARK);
        addBox(14, 2, 9, 15, 2, 10, C_WOOD_DARK);
        addBox(10, 2, -8, 10, 2, -8, C_STONE_DARK); // Bollards
        addBox(10, 2, 8, 10, 2, 8, C_STONE_DARK);

        function addPerson(x, z, shirtColor) {
            addVoxel(x, 2, z, 0x000000);
            addBox(x, 3, z, x, 4, z, shirtColor);
            addVoxel(x, 5, z, 0xffdcb3);
        }
        addPerson(13, 12, C_RED);
        addPerson(18, -5, 0x2ecc71);
        addPerson(14, -8, 0x3498db);

        // Rowboat tied to dock
        for(let z=4; z<=6; z++) {
            for(let x=7; x<=9; x++) {
                if (z===4 || z===6 || x===7 || x===9) {
                    if (x===8 && z===4) continue;
                    addVoxel(x, 1, z, C_WOOD_DARK);
                } else {
                    addVoxel(x, 1, z, 0x000000);
                }
            }
        }

        // 6. The Sailing Ship
        // Hull
        for (let z = -8; z <= 8; z++) {
            let width = (z === -8 || z === 8) ? 0 : (Math.abs(z) === 7 ? 1 : (Math.abs(z) === 6 ? 2 : 3));
            for (let x = -width; x <= width; x++) {
                if (Math.abs(x) === width) {
                    addVoxel(x, 1, z, C_WOOD_DARK);
                    addVoxel(x, 2, z, C_WOOD);
                    if (width === 3) addVoxel(x, 3, z, C_WOOD);
                } else {
                    addVoxel(x, 1, z, C_WOOD_DARK); // Deck floor
                }
            }
        }
        
        // Cabin
        addBox(-1, 2, -6, 1, 4, -4, C_WOOD_DARK);
        addBox(-2, 5, -7, 2, 5, -3, C_RED); // Roof

        // Mast & Bowsprit
        addBox(0, 2, 0, 0, 18, 0, 0x6e2c00);
        addBox(0, 3, 8, 0, 3, 12, 0x6e2c00);

        // Crow's Nest
        for(let x=-1; x<=1; x++) {
            for(let z=-1; z<=1; z++) {
                if (Math.abs(x) === 1 || Math.abs(z) === 1) addVoxel(x, 15, z, C_WOOD_DARK);
            }
        }

        // Sails (with slight 3D curve)
        for (let y = 4; y <= 11; y++) {
            for (let x = -5; x <= 5; x++) {
                if (Math.abs(x) <= 5 - Math.floor((y - 4) / 3)) {
                    let color = (y === 7 || y === 8) ? C_RED : ((x+y)%2 === 0 ? C_SAIL_SHADOW : C_SAIL);
                    let z = (x === 0) ? 2 : 1;
                    addVoxel(x, y, z, color);
                }
            }
        }
        for (let y = 12; y <= 16; y++) {
            for (let x = -3; x <= 3; x++) {
                if (Math.abs(x) <= 3 - Math.floor((y - 12) / 2)) {
                    let color = (x+y)%2 === 0 ? C_SAIL_SHADOW : C_SAIL;
                    let z = (x === 0) ? 2 : 1;
                    addVoxel(x, y, z, color);
                }
            }
        }
        addBox(1, 18, 0, 3, 19, 0, C_RED); // Ship Flag
        addVoxel(0, 19, 0, C_YELLOW);

        // Ship Cannons
        for (let z of [-4, 0, 4]) {
            addBox(-3, 3, z, -4, 3, z, 0x2c3e50);
            addBox(3, 3, z, 4, 3, z, 0x2c3e50);
        }

        // Mooring Rope
        for (let x = 4; x <= 9; x++) {
            let y = (x === 4) ? 3 : 2; 
            addVoxel(x, y, 4, C_YELLOW); 
        }

        // 7. Ambient Details (Wake, Seagulls, Clouds)
        for(let z=9; z<=16; z++) {
            let w = Math.max(1, z - 8);
            for(let x=-w; x<=w; x++) {
                if ((x+z)%2 === 0) addVoxel(x, 1, z, C_WATER_LIGHT);
            }
        }

        function addSeagull(x, y, z) {
            addVoxel(x, y, z, C_WHITE);
            addVoxel(x-1, y+1, z, C_WHITE); addVoxel(x+1, y+1, z, C_WHITE);
            addVoxel(x-2, y+1, z, C_WHITE); addVoxel(x+2, y+1, z, C_WHITE);
        }
        addSeagull(5, 14, 15);
        addSeagull(-8, 16, 10);
        addSeagull(15, 15, -10);

        function addCloud(cx, cy, cz, size) {
            for(let x=-size; x<=size; x++) {
                for(let z=-size; z<=size; z++) {
                    for(let y=0; y<=1; y++) {
                        if (x*x + z*z + y*y*2 <= size*size + 1 && (Math.abs(x*z) + y) % 3 !== 0) {
                            addVoxel(cx+x, cy+y, cz+z, C_WHITE);
                        }
                    }
                }
            }
        }
        addCloud(-15, 22, -10, 4);
        addCloud(10, 26, 20, 5);
        addCloud(25, 20, -15, 3);
        addCloud(-20, 24, 15, 4);

        // --- BUILD OPTIMIZED INSTANCED MESHES ---
        const voxelsByColor = {};
        for (const voxel of voxelMap.values()) {
            if (!voxelsByColor[voxel.color]) voxelsByColor[voxel.color] = [];
            voxelsByColor[voxel.color].push(voxel);
        }

        const cubeGeo = new THREE.BoxGeometry(1, 1, 1);
        const dummy = new THREE.Object3D();

        for (const colorHex in voxelsByColor) {
            const voxels = voxelsByColor[colorHex];
            const material = new THREE.MeshLambertMaterial({ color: parseInt(colorHex) });
            const instancedMesh = new THREE.InstancedMesh(cubeGeo, material, voxels.length);
            
            for (let i = 0; i < voxels.length; i++) {
                const v = voxels[i];
                dummy.position.set(v.x, v.y, v.z);
                dummy.updateMatrix();
                instancedMesh.setMatrixAt(i, dummy.matrix);
            }
            instancedMesh.castShadow = true;
            instancedMesh.receiveShadow = true;
            scene.add(instancedMesh);
        }

        // --- RENDER LOOP ---
        function animate() {
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        }
        animate();

        // Handle window resize
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    </script>
</body>
</html>
```