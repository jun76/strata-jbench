I can help with the 3D voxel art scene, but I can't verify it renders in your browser—I'm a text model and don't have a sandbox or a live preview of your HTML file. What I can do is give you a self-contained HTML file you can paste into one document and open in Chrome. If anything looks off, tell me what you see and I can adjust it.

The core idea: use a voxel approach (a grid of small cubes) to build a stylized sailing ship and harbor. A lightweight approach is Three.js via CDN, with OrbitControls so the scene rotates with the mouse. Here's a complete starter file:

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Voxel Harbor</title>
<style>body{margin:0;overflow:hidden}</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
<script>
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);

const camera = new THREE.PerspectiveCamera(60, window.innerWidth/window.innerHeight, 0.1, 1000);
camera.position.set(18, 14, 18);

const renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.target.set(0, 2, 0);

const light = new THREE.DirectionalLight(0xffffff, 0.9);
light.position.set(10, 20, 10);
scene.add(light);
scene.add(new THREE.AmbientLight(0x404040));

function box(x,y,z,sx,sy,sz,color){
  const g = new THREE.BoxGeometry(sx,sy,sz);
  const m = new THREE.MeshLambertMaterial({color:color});
  const mesh = new THREE.Mesh(g,m);
  mesh.position.set(x,y,z);
  scene.add(mesh);
  return mesh;
}

// Harbor ground
box(0, -0.5, 0, 30, 1, 30, 0x2e8b57);
// Water strip
box(0, 0.05, 8, 30, 0.3, 6, 0x1e90ff);
// Quay
box(-6, 0.5, 4, 10, 1, 6, 0x8b4513);

// Ship hull (voxels)
const hullColor = 0x654321;
for(let i=-4;i<=4;i++){
  for(let j=-2;j<=2;j++){
    if(Math.abs(i)+Math.abs(j) < 5) box(i*0.9, 1.2, j*0.9, 0.85, 1.4, 0.85, hullColor);
  }
}
// Deck
box(0, 2.0, 0, 8, 0.3, 5, 0xd2b48c);
// Mast
box(0, 4.5, 0, 0.5, 5, 0.5, 0x4b3621);
// Sail
box(0, 4.5, 0.6, 3.5, 3.5, 0.25, 0xf5f5f5);
// Small flag
box(0.4, 7.2, 0, 1.2, 0.6, 0.2, 0xff4444);

function animate(){
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}
animate();

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth/window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
</script>
</body>
</html>
```

A few practical notes: the file uses CDN-loaded Three.js, so it needs internet access when opened. The scene is a simple stylized ship at a quay, not a photoreal harbor—if you want, I can add waves, docked buoys, cranes, or a crew of voxels. If it renders blank or the CDN fails in your environment, I can switch it to a fully local approach or inline the geometry.