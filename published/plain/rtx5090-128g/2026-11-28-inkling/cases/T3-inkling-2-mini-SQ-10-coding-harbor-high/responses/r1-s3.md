```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>A Sailing Ship Calling at a Harbor</title>
<style>
  html, body { margin: 0; padding: 0; height: 100%; overflow: hidden; background: #1a2b3a; }
  #c { display: block; width: 100vw; height: 100vh; cursor: grab; touch-action: none; }
  #c.dragging { cursor: grabbing; }
  .overlay { position: fixed; z-index: 10; pointer-events: none; font-family: system-ui, sans-serif; color: #fff; text-shadow: 0 1px 3px rgba(0,0,0,.55); }
  #title { top: 14px; left: 16px; font-size: 20px; font-weight: 600; letter-spacing: .3px; }
  #hint { bottom: 14px; left: 50%; transform: translateX(-50%); font-size: 13px; background: rgba(20,32,46,.55); padding: 8px 14px; border-radius: 12px; }
</style>
</head>
<body>
<canvas id="c"></canvas>
<div class="overlay" id="title">A Sailing Ship Calling at a Harbor</div>
<div class="overlay" id="hint">Drag to rotate &middot; Scroll to zoom</div>
<script>
(() => {
  const canvas = document.getElementById('c');
  const ctx = canvas.getContext('2d');
  let W = 0, H = 0, DPR = 1;

  function resize(){
    DPR = Math.min(window.devicePixelRatio || 1, 2);
    W = window.innerWidth; H = window.innerHeight;
    canvas.width = Math.round(W * DPR);
    canvas.height = Math.round(H * DPR);
    canvas.style.width = W + 'px';
    canvas.style.height = H + 'px';
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
  }
  window.addEventListener('resize', resize);
  resize();

  // ---------- voxel scene ----------
  const scene = [];
  function add(x, y, z, color, type, phase = 0){
    const v = { baseX: x, baseY: y, baseZ: z, color: color, type: type, phase: phase, x: x, y: y, z: z };
    scene.push(v);
    return v;
  }

  // water plane
  for (let x = -20; x <= 20; x++) for (let z = -11; z <= 20; z++) {
    if (x === -8 && (z === -6 || z === 6)) continue; // posts
    add(x, 0, z, [34, 78, 112], 'water');
  }

  // dock planks (with lighthouse footprint removed)
  for (let x = -17; x <= -8; x++) for (let z = -5; z <= 5; z++) {
    if (x >= -15 && x <= -14 && z >= 4 && z <= 5) continue;
    add(x, 1, z, [126, 90, 54], 'solid');
  }
  // dock posts
  add(-8, 0, -6, [84, 58, 36], 'solid'); add(-8, 1, -6, [84, 58, 36], 'solid');
  add(-8, 0, 6, [84, 58, 36], 'solid');  add(-8, 1, 6, [84, 58, 36], 'solid');
  // crates, barrels, lantern post
  add(-10, 2, -2, [150, 112, 60], 'solid');
  add(-12, 2, -3, [150, 112, 60], 'solid');
  add(-9, 2, 2, [96, 70, 44], 'solid');
  add(-11, 2, 3, [96, 70, 44], 'solid');
  add(-8, 2, 4, [70, 50, 30], 'solid');
  add(-8, 3, 4, [255, 210, 110], 'lantern', 0);
  // rowboat
  for (let x = -7; x <= -4; x++) for (let z = 3; z <= 4; z++) add(x, 1, z, [110, 80, 50], 'solid');

  // lighthouse
  const LH = {1:[232,226,214],2:[232,226,214],3:[198,58,48],4:[232,226,214],5:[232,226,214],6:[198,58,48],7:[232,226,214],8:[232,226,214]};
  for (let y = 1; y <= 8; y++) for (let x = -15; x <= -14; x++) for (let z = 4; z <= 5; z++) add(x, y, z, LH[y], 'solid');
  add(-15, 9, 4, [255, 220, 120], 'lantern', 0);
  add(-15, 9, 5, [42, 40, 36], 'solid');
  add(-14, 9, 4, [42, 40, 36], 'solid');
  add(-14, 9, 5, [42, 40, 36], 'solid');
  for (let x = -15; x <= -14; x++) for (let z = 4; z <= 5; z++) add(x, 10, z, [198, 58, 48], 'solid');
  add(-15, 11, 4, [210, 60, 50], 'flag', 0);

  // sailing ship
  const HULL = [96, 60, 34], DECK = [140, 100, 58], MAST = [74, 48, 28], SAIL = [232, 220, 190], FLAG = [210, 60, 50];
  for (let x = -6; x <= 10; x++) {
    if (x === -6 || x === 10) add(x, 1, 0, HULL, 'ship');
    else for (let z = -1; z <= 1; z++) add(x, 1, z, HULL, 'ship');
  }
  for (let x = -5; x <= 9; x++) for (let z = -1; z <= 1; z++) add(x, 2, z, DECK, 'ship');
  for (const mx of [-3, 1, 5]) for (let y = 3; y <= 8; y++) add(mx, y, 0, MAST, 'ship');
  for (const [a, b, m] of [[-5, -1, -3], [0, 2, 1], [3, 7, 5]]) {
    for (let x = a; x <= b; x++) {
      if (x === m) continue;
      for (let y = 3; y <= 6; y++) add(x, y, 0, SAIL, 'ship');
    }
  }
  add(1, 9, 0, FLAG, 'shipflag', 0);
  add(12, 3, 0, FLAG, 'shipflag', 1.5);
  add(-6, 4, 0, FLAG, 'shipflag', 3.0);
  add(11, 2, 0, MAST, 'ship'); add(12, 2, 0, MAST, 'ship'); add(13, 2, 0, MAST, 'ship');
  add(-6, 3, -1, [40, 38, 36], 'ship');
  add(8, 3, -1, [40, 38, 36], 'ship');
  add(9, 3, 0, [96, 70, 44], 'ship');

  // distant sailboat
  const DIST_HULL = [72, 60, 48], DIST_MAST = [56, 44, 32], DIST_SAIL = [200, 190, 168];
  for (let x = 12; x <= 15; x++) for (let z = -8; z <= -7; z++) add(x, 1, z, DIST_HULL, 'distant');
  for (let y = 2; y <= 5; y++) add(13, y, -8, DIST_MAST, 'distant');
  add(12, 2, -8, DIST_SAIL, 'distant'); add(12, 3, -8, DIST_SAIL, 'distant');
  add(13, 6, -8, [180, 60, 50], 'distant');

  // mountains
  const MT = [[-14,0,-12,4],[-13,0,-12,3],[-12,0,-12,3],[-10,0,-12,2],[12,0,-12,3],[13,0,-12,4],[14,0,-12,2]];
  for (const [mx, y0, z0, n] of MT) {
    for (let y = y0; y < y0 + n; y++) add(mx, y, z0, y % 2 ? [96, 108, 122] : [90, 102, 116], 'solid');
  }

  // buoy
  add(9, 1, -5, [210, 70, 50], 'buoy', 0);
  add(9, 2, -5, [230, 230, 225], 'buoy', 0);

  // clouds
  const cloudDefs = [
    { x: -12, y: 11.5, z: -6, phase: 0.0, offs: [[0,0,0],[1,0,0],[2,0,0],[0,1,0],[1,1,0],[-1,0,0]] },
    { x: 6, y: 12.5, z: -8, phase: 2.1, offs: [[0,0,0],[1,0,0],[2,0,0],[1,1,0],[0,-1,0]] },
    { x: 13, y: 10.5, z: 2, phase: 4.2, offs: [[0,0,0],[1,0,0],[1,1,0],[2,0,0]] }
  ];
  for (const c of cloudDefs) for (const o of c.offs) add(c.x + o[0], c.y + o[1], c.z + o[2], [240, 240, 246], 'cloud', c.phase);

  // birds
  const birdTrio = [];
  for (let i = 0; i < 3; i++) {
    const phase = i * 2.1;
    const body = add(0, 0, 0, [45, 48, 55], 'bird', phase);
    const wingL = add(0, 0, 0, [45, 48, 55], 'bird', phase);
    const wingR = add(0, 0, 0, [45, 48, 55], 'bird', phase);
    birdTrio.push({ body, wingL, wingR, idx: i });
  }

  // ---------- camera / interaction ----------
  let yaw = 0.55, pitch = 0.42, scale = 30;
  let dragging = false, lastPX = 0, lastPY = 0;

  canvas.addEventListener('pointerdown', e => {
    dragging = true; lastPX = e.clientX; lastPY = e.clientY;
    canvas.classList.add('dragging');
    canvas.setPointerCapture(e.pointerId);
  });
  window.addEventListener('pointermove', e => {
    if (!dragging) return;
    const dx = e.clientX - lastPX, dy = e.clientY - lastPY;
    lastPX = e.clientX; lastPY = e.clientY;
    yaw += dx * 0.006;
    pitch += dy * 0.0035;
    pitch = Math.max(0.14, Math.min(0.75, pitch));
  });
  window.addEventListener('pointerup', () => { dragging = false; canvas.classList.remove('dragging'); });
  window.addEventListener('pointercancel', () => { dragging = false; canvas.classList.remove('dragging'); });
  canvas.addEventListener('wheel', e => {
    e.preventDefault();
    scale = Math.max(8, Math.min(64, scale * (1 - e.deltaY * 0.0012)));
  }, { passive: false });

  // ---------- rendering ----------
  function drawBackground(){
    const g = ctx.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0.0, '#4e8fbe');
    g.addColorStop(0.42, '#9cc2d6');
    g.addColorStop(0.50, '#e3d9bc');
    g.addColorStop(0.56, '#3a6a84');
    g.addColorStop(1.0, '#23405a');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, W, H);
    const sunX = W * 0.24, sunY = H * 0.2;
    const r = H * 0.12;
    const sg = ctx.createRadialGradient(sunX, sunY, 0, sunX, sunY, r);
    sg.addColorStop(0, 'rgba(255,236,170,0.95)');
    sg.addColorStop(0.5, 'rgba(255,220,140,0.45)');
    sg.addColorStop(1, 'rgba(255,220,140,0)');
    ctx.fillStyle = sg;
    ctx.beginPath(); ctx.arc(sunX, sunY, r, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = '#ffe9a8';
    ctx.beginPath(); ctx.arc(sunX, sunY, H * 0.045, 0, Math.PI * 2); ctx.fill();
  }

  function corners(wx, wy, wz, cy, sy, cp, sp, s){
    const h = 0.5;
    const offs = {
      top:   [[h,h,-h],[h,h,h],[-h,h,h],[-h,h,-h]],
      front: [[h,h,h],[h,-h,h],[-h,-h,h],[-h,h,h]],
      left:  [[-h,h,h],[-h,-h,h],[-h,-h,-h],[-h,h,-h]],
      right: [[h,h,h],[h,-h,h],[h,-h,-h],[h,h,-h]]
    };
    const out = {};
    for (const key in offs) {
      out[key] = offs[key].map(([ox, oy, oz]) => {
        const x = wx + ox, y = wy + oy, z = wz + oz;
        const xr = x * cy + z * sy;
        const zr = -x * sy + z * cy;
        const yr = y * cp - zr * sp;
        return [W * 0.5 + xr * s, H * 0.52 - yr * s];
      });
    }
    return out;
  }

  function voxelColor(v, t){
    if (v.type === 'water') {
      const wave = 0.5 + 0.5 * Math.sin(t * 2.2 + v.x * 0.33 + v.z * 0.47);
      const glint = Math.sin(t * 3.1 + v.x * 0.53 + v.z * 0.71) > 0.72;
      let r = 34 + (88 - 34) * wave, g = 78 + (144 - 78) * wave, b = 112 + (184 - 112) * wave;
      if (glint) { r *= 1.3; g *= 1.3; b *= 1.3; }
      return [r, g, b];
    }
    if (v.type === 'lantern') return [255, 200 + 50 * Math.sin(t * 2.5), 110];
    if (v.type === 'cloud') return [240, 240, 246];
    if (v.type === 'bird') return [45, 48, 55];
    return v.color;
  }

  function drawVoxel(v, t, topVis, frontVis, leftVis, rightVis, cy, sy, cp, sp){
    const s = scale;
    const wx = v.x, wy = v.y, wz = v.z;
    const fz = corners(wx, wy, wz, cy, sy, cp, sp, s);
    const faces = [];
    if (topVis) faces.push({ nz: sp, corners: fz.top, mul: v.type === 'water' ? 1.0 : 1.35, alpha: v.type === 'cloud' ? 0.85 : 1.0 });
    if (frontVis) faces.push({ nz: cy * cp, corners: fz.front, mul: 1.0, alpha: v.type === 'cloud' ? 0.85 : 1.0 });
    if (leftVis) faces.push({ nz: sy * cp, corners: fz.left, mul: 0.8, alpha: v.type === 'cloud' ? 0.85 : 1.0 });
    if (rightVis) faces.push({ nz: -sy * cp, corners: fz.right, mul: 0.8, alpha: v.type === 'cloud' ? 0.85 : 1.0 });
    if (v.type === 'water') faces = [{ nz: sp, corners: fz.top, mul: 1.0, alpha: 1.0 }];
    faces.sort((a, b) => a.nz - b.nz);
    const base = voxelColor(v, t);
    for (const f of faces) {
      const r = Math.min(255, base[0] * f.mul) | 0, g = Math.min(255, base[1] * f.mul) | 0, b = Math.min(255, base[2] * f.mul) | 0;
      ctx.globalAlpha = f.alpha;
      ctx.fillStyle = `rgb(${r},${g},${b})`;
      ctx.beginPath();
      ctx.moveTo(f.corners[0][0], f.corners[0][1]);
      for (let i = 1; i < 4; i++) ctx.lineTo(f.corners[i][0], f.corners[i][1]);
      ctx.closePath();
      ctx.fill();
      ctx.globalAlpha = 1;
    }
  }

  function drawGlow(t){
    const cy = Math.cos(yaw), sy = Math.sin(yaw), cp = Math.cos(pitch), sp = Math.sin(pitch);
    const x = -15, y = 9.5, z = 4.5;
    const xr = x * cy + z * sy;
    const zr = -x * sy + z * cy;
    const yr = y * cp - zr * sp;
    const sx = W * 0.5 + xr * scale;
    const sy2 = H * 0.52 - yr * scale;
    const r = scale * 2.4;
    const a = 0.35 + 0.2 * Math.sin(t * 2.5);
    const g = ctx.createRadialGradient(sx, sy2, 0, sx, sy2, r);
    g.addColorStop(0, `rgba(255,214,110,${a})`);
    g.addColorStop(1, 'rgba(255,214,110,0)');
    ctx.globalCompositeOperation = 'lighter';
    ctx.fillStyle = g;
    ctx.beginPath(); ctx.arc(sx, sy2, r, 0, Math.PI * 2); ctx.fill();
    ctx.globalCompositeOperation = 'source-over';
  }

  function draw(t){
    // animated offsets
    const shipOffX = Math.sin(t * 0.5) * 0.5;
    const shipOffY = Math.sin(t * 1.3) * 0.3;
    const distOffX = Math.sin(t * 0.4 + 2.0) * 0.4;
    const distOffY = Math.sin(t * 1.1 + 2.0) * 0.25;
    // birds
    for (const b of birdTrio) {
      const phase = b.idx * 2.1;
      const bx = Math.sin(t * 0.35 + phase) * 10;
      const by = 9.5 + Math.sin(t * 0.8 + phase * 1.7) * 1.6;
      const bz = -5 + Math.cos(t * 0.3 + phase * 2.0) * 5;
      const flap = Math.sin(t * 7 + phase * 3) > 0 ? 0.4 : 0;
      b.body.x = bx; b.body.y = by; b.body.z = bz;
      b.wingL.x = bx - 1.1; b.wingL.y = by + flap; b.wingL.z = bz;
      b.wingR.x = bx + 1.1; b.wingR.y = by + flap; b.wingR.z = bz;
    }

    drawBackground();

    const cy = Math.cos(yaw), sy = Math.sin(yaw), cp = Math.cos(pitch), sp = Math.sin(pitch);
    const items = [];
    for (const v of scene) {
      if (v.type === 'water') { v.x = v.baseX; v.y = 0; v.z = v.baseZ; }
      else if (v.type === 'ship') { v.x = v.baseX + shipOffX; v.y = v.baseY + shipOffY; v.z = v.baseZ; }
      else if (v.type === 'shipflag') { v.x = v.baseX + shipOffX + Math.sin(t * 5 + v.phase) * 0.3; v.y = v.baseY + shipOffY; v.z = v.baseZ; }
      else if (v.type === 'distant') { v.x = v.baseX + distOffX; v.y = v.baseY + distOffY; v.z = v.baseZ; }
      else if (v.type === 'flag') { v.x = v.baseX + Math.sin(t * 5 + v.phase) * 0.3; v.y = v.baseY; v.z = v.baseZ; }
      else if (v.type === 'cloud') { v.x = v.baseX + Math.sin(t * 0.12 + v.phase) * 3; v.y = v.baseY; v.z = v.baseZ; }
      else if (v.type === 'buoy') { v.x = v.baseX; v.y = v.baseY + Math.sin(t * 1.5 + v.phase) * 0.25; v.z = v.baseZ; }
      else if (v.type !== 'bird') { v.x = v.baseX; v.y = v.baseY; v.z = v.baseZ; }
      // project center
      const xr = v.x * cy + v.z * sy;
      const zr = -v.x * sy + v.z * cy;
      const zr2 = v.y * sp + zr * cp;
      const yr = v.y * cp - zr * sp;
      const sx = W * 0.5 + xr * scale;
      const sy2 = H * 0.52 - yr * scale;
      if (sx < -3 * scale || sx > W + 3 * scale || sy2 < -3 * scale || sy2 > H + 3 * scale) continue;
      items.push({ v: v, zr2: zr2 });
    }
    items.sort((a, b) => a.zr2 - b.zr2);

    const topVis = sp > 0.15, frontVis = cy * cp > 0.15, leftVis = sy * cp > 0.15, rightVis = -sy * cp > 0.15;
    for (const it of items) drawVoxel(it.v, t, topVis, frontVis, leftVis, rightVis, cy, sy, cp, sp);
    drawGlow(t);
  }

  let lastTime = performance.now(), time = 0;
  function frame(now){
    const dt = Math.min((now - lastTime) / 1000, 0.05);
    lastTime = now;
    time += dt;
    draw(time);
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
})();
</script>
</body>
</html>
```

**How to use it:** Save everything above into a single `harbor.html` file and open it in Chrome. It renders immediately.

- **Drag** (left mouse button) to rotate the scene around the harbor.
- **Scroll wheel** to zoom in and out.
- The scene is fully self-contained — no libraries, no internet needed — so it works offline in Chrome.

**What's in the scene:** a 3-mast sailing ship (bobbing gently, with waving flags, sails, cannons, a barrel and a bowsprit) at a harbor with a wooden pier, crates, barrels, a lantern post, a lighthouse with a pulsing light and glow, a rowboat, a bobbing buoy, distant silhouette mountains, a far sailboat, drifting clouds, flapping seagulls, and a shimmering animated ocean with a sun. All motion (waves, bobbing, flags, light, birds) is animated in real time.