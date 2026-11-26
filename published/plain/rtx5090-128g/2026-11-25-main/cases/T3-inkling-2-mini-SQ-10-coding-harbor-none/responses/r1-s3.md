I can help with the scene, but I can't generate a copy-pasteable HTML file as a file download. What I can do is write a single, self-contained HTML/JavaScript sketch you can save and open in Chrome. It uses the 3D voxel-style style with Three.js, and it renders immediately in the browser.

Key design decisions:
- A blocky voxel ship built from cubes (hull, masts, sails, and cabin), sitting in a harbor of cubic water tiles.
- A simple harbor edge: docks, a lighthouse-like voxel tower, and a few moored small boats.
- A mouse-driven camera (drag to look around, wheel to zoom).

Here is a ready-to-paste HTML sketch. It uses Three.js via a CDN script tag, so you'll need an internet connection when opening it in Chrome (or vendor the Three.js file if you want it offline).

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Sailing Ship in Harbor</title>
<style>
  body { margin: 0; overflow: hidden; background: #0b1c2a; }
  canvas { display: block; }
</style>
</head>
<body>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0b1c2a);
const camera = new THREE.PerspectiveCamera(60, window.innerWidth/window.innerHeight, 0.1, 200);
camera.position.set(10, 8, 10);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.domElement.style.position = 'fixed';
renderer.domElement.style.top = '0';
document.body.appendChild(renderer.domElement);
const light = new THREE.DirectionalLight(0xffffff, 1.2);
light.position.set(5, 10, 4);
scene.add(light);
scene.add(new THREE.AmbientLight(0xffffff, 0.45));
function cube(x,y,z,w,h,d,color){
  const m = new THREE.Mesh(new THREE.BoxGeometry(w,h,d), new THREE.MeshLambertMaterial({ color }));
  m.position.set(x,y,z);
  scene.add(m);
}
// Harbor water tiles
for (let x=-6; x<=6; x++) for (let z=-6; z<=6; z++) {
  cube(x*0.8, 0, z*0.8, 0.78, 0.4, 0.78, 0x1f6f8b);
}
// Dock
cube(-6, 0.3, -5.5, 2.2, 0.6, 1.4, 0x6b5b45);
cube(-5.2, 0.9, -5.3, 1.2, 0.6, 0.7, 0x7c6a50);
// Voxel ship
cube(0, 0.6, 0, 4.0, 1.2, 1.8, 0x2d4a5b);   // hull
cube(0, 1.6, 0, 2.4, 0.6, 1.2, 0x4c3f2f);     // deck
cube(-1.2, 2.0, 0, 0.35, 2.4, 0.35, 0x6d5a42); // mast
cube(1.2, 2.0, 0, 0.35, 2.4, 0.35, 0x6d5a42);  // mast
cube(-1.2, 3.1, 0, 0.9, 1.1, 0.05, 0xf5f0e3);  // sail
cube(1.2, 3.1, 0, 0.9, 1.1, 0.05, 0xf5f0e3);
cube(0, 2.4, 0, 0.9, 1.1, 0.9, 0x3c2f2a);      // cabin
// Small moored boats
cube(-4.2, 0.5, 4.2, 1.3, 0.5, 0.8, 0x6a7d6b);
cube(4.2, 0.5, 4.2, 1.3, 0.5, 0.8, 0x6a7d6b);
// Lighthouse-ish voxel tower
cube(5.5, 1.2, -5.2, 0.9, 2.4, 0.9, 0xe8e2d6);
cube(5.5, 2.6, -5.2, 0.5, 0.4, 0.5, 0x111111);
// Mouse camera controls
let theta = 0.7, phi = 0.9, radius = 12, target = new THREE.Vector3(0,1,0);
const dom = renderer.domElement;
dom.addEventListener('mousedown', () => dragging = true);
window.addEventListener('mouseup', () => dragging = false);
let dragging = false, prevX = 0, prevY = 0;
window.addEventListener('mousemove', e => {
  if (!dragging) return;
  const dx = e.clientX - prevX, dy = e.clientY - prevY;
  theta -= dx * 0.005;
  phi = Math.max(0.2, Math.min(1.4, phi + dy * 0.005));
  prevX = e.clientX; prevY = e.clientY;
});
window.addEventListener('mousedown', e => { prevX = e.clientX; prevY = e.clientY; });
window.addEventListener('wheel', e => { radius = Math.max(6, Math.min(24, radius + e.deltaY * 0.01)); });
function updateCamera(){
  camera.position.set(
    target.x + radius * Math.sin(phi) * Math.cos(theta),
    target.y + radius * Math.cos(phi),
    target.z + radius * Math.sin(phi) * Math.sin(theta)
  );
  camera.lookAt(target);
}
function loop(){
  updateCamera();
  renderer.render(scene, camera);
  requestAnimationFrame(loop);
}
loop();
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
</script>
</body>
</html>
```

Notes:
- Save as an `.html` file and open it directly in Chrome.
- It uses an external CDN for Three.js, so offline use requires vendoring the library.
- The scene is intentionally compact and readable rather than highly detailed; it should render instantly once loaded.
- Drag the mouse to orbit, and use the mouse wheel to zoom.