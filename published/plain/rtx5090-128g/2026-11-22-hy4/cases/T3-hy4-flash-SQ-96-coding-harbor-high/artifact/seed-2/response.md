Here is the complete HTML file. It uses Three.js (via CDN) and `InstancedMesh` to efficiently render thousands of voxels. 

It features a main ship calling at the dock, a second ship sailing in the background, a harbor with a lighthouse and a warehouse, an island, and gently drifting clouds. The ships bob gently in the water. You can use your mouse (left click to rotate, scroll to zoom, right click to pan) to explore the scene.

Save this code into an `index.html` file and open it in Chrome:

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
    <!-- Three.js r128 -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <!-- OrbitControls -->
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
    <div id="info">
        <strong>Voxel Harbor</strong><br>
        Left Click: Rotate | Scroll: Zoom | Right Click: Pan
    </div>

<script>
// --------------------------------------------------------
// 1. Scene Setup, Camera, Renderer, Controls
// --------------------------------------------------------
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87CEEB);
scene.fog = new THREE.Fog(0x87CEEB, 60, 150);

const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 1, 1000);
camera.position.set(25, 30, 50);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.target.set(0, 5, 0);
controls.maxDistance = 150;
controls.minDistance = 15;

// --------------------------------------------------------
// 2. Lighting
// --------------------------------------------------------
const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
scene.add(ambientLight);

const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
dirLight.position.set(30, 50, -20);
dirLight.castShadow = true;
dirLight.shadow.mapSize.width = 2048;
dirLight.shadow.mapSize.height = 2048;
dirLight.shadow.camera.near = 0.5;
dirLight.shadow.camera.far = 150;
const d = 60;
dirLight.shadow.camera.left = -d;
dirLight.shadow.camera.right = d;
dirLight.shadow.camera.top = d;
dirLight.shadow.camera.bottom = -d;
dirLight.shadow.bias = -0.0005;
scene.add(dirLight);

// Lighthouse glow
const pointLight = new THREE.PointLight(0xffff00, 1.2, 25);
pointLight.position.set(15, 9.5, -15);
scene.add(pointLight);

// --------------------------------------------------------
// 3. Voxel Engine Helper
// --------------------------------------------------------
function createVoxelMesh(voxels) {
    const geometry = new THREE.BoxGeometry(1, 1, 1);
    const material = new THREE.MeshLambertMaterial({ color: 0xffffff });
    const mesh = new THREE.InstancedMesh(geometry, material, voxels.length);
    
    const dummy = new THREE.Object3D();
    const color = new THREE.Color();
    
    for(let i = 0; i < voxels.length; i++) {
        const v = voxels[i];
        dummy.position.set(v.x, v.y, v.z);
        dummy.updateMatrix();
        mesh.setMatrixAt(i, dummy.matrix);
        mesh.setColorAt(i, color.setHex(v.c));
    }
    mesh.instanceMatrix.needsUpdate = true;
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    return mesh;
}

const waterVoxels = [];
const staticVoxels = [];
const ship1Voxels = [];
const ship2Voxels = [];
const cloudVoxels = [];

function addVoxel(arr, x, y, z, c) {
    arr.push({x, y, z, c});
}

// --------------------------------------------------------
// 4. Generate Scene Geometry
// --------------------------------------------------------

// --- Water ---
for(let x = -40; x <= 40; x++) {
    for(let z = -40; z <= 40; z++) {
        if (x >= 17) continue; // Leave room for land
        
        let distIsland = Math.sqrt((x + 30)**2 + (z - 20)**2);
        if(distIsland < 6) continue; // Leave room for island
        
        let c = 0x2874b5;
        let r = Math.random();
        if(r < 0.05) c = 0x1e5f9e;
        else if(r > 0.95) c = 0x3487c9;
        
        addVoxel(waterVoxels, x, -1, z, c);
    }
}

// --- Shore / Land ---
for(let x = 17; x <= 40; x++) {
    for(let z = -30; z <= 30; z++) {
        if (x >= 18 && x <= 25 && z >= 5 && z <= 15) continue; // Skip warehouse area
        
        let h = 1 + Math.floor(Math.random() * 2); // height 1 or 2
        for(let y = 0; y <= h; y++) {
            let c = (y === h) ? 0x55aa55 : 0x777777; // Grass top, dirt bottom
            addVoxel(staticVoxels, x, y, z, c);
        }
    }
}

// --- Island ---
for(let x = -35; x <= -25; x++) {
    for(let z = 15; z <= 25; z++) {
        let dist = Math.sqrt((x + 30)**2 + (z - 20)**2);
        if(dist < 6) {
            for(let y = 0; y <= 1; y++) addVoxel(staticVoxels, x, y, z, 0xeebb55); // Sand
        }
        if(dist < 3.5) {
            for(let y = 2; y <= 3; y++) addVoxel(staticVoxels, x, y, z, 0x228b22); // Grass
        }
    }
}
// Island Tree
for(let y = 4; y <= 7; y++) addVoxel(staticVoxels, -30, y, 20, 0x8b5a2b);
for(let x = -33; x <= -27; x++) {
    for(let z = 17; z <= 23; z++) {
        let dist = Math.abs(x + 30) + Math.abs(z - 20);
        if(dist < 5 && dist > 0) {
            addVoxel(staticVoxels, x, 7, z, 0x228b22);
            if(dist < 3) addVoxel(staticVoxels, x, 8, z, 0x228b22);
        }
    }
}

// --- Trees on Shore ---
for(let i = 0; i < 25; i++) {
    let tx = 20 + Math.floor(Math.random() * 18);
    let tz = -25 + Math.floor(Math.random() * 50);
    if (tx >= 18 && tx <= 25 && tz >= 5 && tz <= 15) continue; // avoid warehouse
    
    let th = 1 + Math.floor(Math.random() * 2);
    for(let y = 1; y <= 3 + th; y++) addVoxel(staticVoxels, tx, y, tz, 0x8b5a2b); // Trunk
    for(let dx = -2; dx <= 2; dx++) {
        for(let dz = -2; dz <= 2; dz++) {
            if(Math.abs(dx) + Math.abs(dz) <= 2) {
                addVoxel(staticVoxels, tx + dx, 4 + th, tz + dz, 0x228b22); // Leaves
            }
        }
    }
}

// --- Pier ---
for (let z = -20; z <= 20; z++) {
    for (let y = 0; y <= 1; y++) {
        for (let x = 13; x <= 17; x++) {
            addVoxel(staticVoxels, x, y, z, 0x8b5a2b);
        }
    }
}

// --- Lighthouse ---
for(let y = 2; y <= 8; y++) {
    let color = (y % 2 === 0) ? 0xff3333 : 0xffffff; // Red and white stripes
    for(let x = 14; x <= 16; x++) {
        for(let z = -16; z <= -14; z++) {
            addVoxel(staticVoxels, x, y, z, color);
        }
    }
}
// Light room
for(let x = 14; x <= 16; x++) {
    for(let z = -16; z <= -14; z++) {
        addVoxel(staticVoxels, x, 9, z, 0xffff00); 
    }
}

// --- Harbor Warehouse ---
for(let x = 18; x <= 25; x++) {
    for(let z = 5; z <= 15; z++) {
        for(let y = 1; y <= 4; y++) {
            if (x === 18 || x === 25 || z === 5 || z === 15 || y === 4) {
                let c = (y === 4) ? 0xaa4444 : 0xdddddd; // Red roof, gray walls
                addVoxel(staticVoxels, x, y, z, c);
            }
        }
    }
}

// --- Crane & Crates ---
for(let y = 2; y <= 8; y++) addVoxel(staticVoxels, 15, y, 5, 0xddaa00); // Crane pillar
for(let x = 12; x <= 18; x++) addVoxel(staticVoxels, x, 8, 5, 0xddaa00); // Crane arm
for(let y = 6; y <= 7; y++) addVoxel(staticVoxels, 12, y, 5, 0x333333); // Rope
addVoxel(staticVoxels, 12, 5, 5, 0xcd853f); // Hanging crate

for(let i = 0; i < 15; i++) {
    let cx = 13 + Math.floor(Math.random() * 4);
    let cz = -5 + Math.floor(Math.random() * 20);
    addVoxel(staticVoxels, cx, 2, cz, 0xcd853f);
    if(Math.random() > 0.6) addVoxel(staticVoxels, cx, 3, cz, 0xcd853f);
}

// --- Clouds ---
for(let i = 0; i < 8; i++) {
    let cx = -60 + Math.random() * 120;
    let cy = 30 + Math.random() * 15;
    let cz = -60 + Math.random() * 120;
    for(let dx = -4; dx <= 4; dx++) {
        for(let dz = -2; dz <= 2; dz++) {
            if(Math.random() > 0.4) {
                addVoxel(cloudVoxels, cx + dx, cy + (Math.abs(dx) < 2 ? 1 : 0), cz + dz, 0xffffff);
            }
        }
    }
}

// --- Ships ---
function generateShip(arr, offsetX, offsetZ, rotY) {
    function add(x, y, z, c) {
        if(rotY === 0) {
            addVoxel(arr, x + offsetX, y, z + offsetZ, c);
        } else {
            // Rotate 90 degrees for the background ship
            addVoxel(arr, z + offsetX, y, -x + offsetZ, c);
        }
    }
    // Hull
    for(let x = -10; x <= 10; x++) {
        let width = 3;
        if(Math.abs(x) > 8) width = 0;
        else if(Math.abs(x) > 6) width = 1;
        else if(Math.abs(x) > 4) width = 2;
        
        for(let y = 0; y <= 2; y++) {
            for(let z = -width; z <= width; z++) {
                let c = 0x8b5a2b; // Wood brown
                if(y === 1) c = 0xdddddd; // White stripe
                if(y === 2) c = 0xa0522d; // Deck surface
                add(x, y, z, c);
            }
        }
    }
    // Mast
    for(let y = 3; y <= 18; y++) add(0, y, 0, 0x5c4033);
    
    // Yardarms
    for(let z = -8; z <= 8; z++) add(0, 11, z, 0x5c4033);
    for(let z = -5; z <= 5; z++) add(0, 15, z, 0x5c4033);
    
    // Lower Sail (shaped like a trapezoid)
    for(let y = 4; y <= 10; y++) {
        for(let z = -7; z <= 7; z++) {
            let maxZ = 7;
            if (y < 6) maxZ = 5;
            else if (y < 8) maxZ = 6;
            if (Math.abs(z) <= maxZ) add(-1, y, z, 0xffffff);
        }
    }
    
    // Upper Sail
    for(let y = 12; y <= 14; y++) {
        for(let z = -4; z <= 4; z++) {
            let maxZ = 4;
            if (y < 13) maxZ = 2;
            if (Math.abs(z) <= maxZ) add(-1, y, z, 0xf5f5f5);
        }
    }
    
    // Flag
    for(let z = 0; z <= 3; z++) {
        if(z === 3 && Math.random() > 0.5) continue; // Ragged edge
        add(0, 18, z, 0xff0000);
    }
}

// Ship 1 (Docked at pier), Ship 2 (Sailing in background)
generateShip(ship1Voxels, 0, 0, 0);
generateShip(ship2Voxels, -20, -15, 1);

// --------------------------------------------------------
// 5. Instantiate Meshes & Add to Scene
// --------------------------------------------------------
const waterMesh = createVoxelMesh(waterVoxels);
const staticMesh = createVoxelMesh(staticVoxels);
const ship1Mesh = createVoxelMesh(ship1Voxels);
const ship2Mesh = createVoxelMesh(ship2Voxels);
const cloudMesh = createVoxelMesh(cloudVoxels);

scene.add(waterMesh);
scene.add(staticMesh);
scene.add(ship1Mesh);
scene.add(ship2Mesh);
scene.add(cloudMesh);

// --------------------------------------------------------
// 6. Animation & Render Loop
// --------------------------------------------------------
const clock = new THREE.Clock();

function animate() {
    requestAnimationFrame(animate);
    
    const t = clock.getElapsedTime();
    
    // Bobbing ships
    ship1Mesh.position.y = Math.sin(t * 2) * 0.15;
    ship1Mesh.rotation.z = Math.sin(t * 1.5) * 0.01;
    
    ship2Mesh.position.y = Math.cos(t * 1.8) * 0.15;
    ship2Mesh.rotation.x = Math.cos(t * 1.2) * 0.01;
    
    // Subtle water waves
    waterMesh.position.y = Math.sin(t) * 0.05;
    
    // Drifting clouds
    cloudMesh.position.x = (t * 1.5) % 160 - 80;

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