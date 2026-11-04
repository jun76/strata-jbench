import React, { useEffect, useRef, useState, useCallback } from "react";

/* =========================================================================
   TYPES & CONFIG
   ========================================================================= */
type BlockId = number;

interface BlockDef {
  id: number;
  name: string;
  color: [number, number, number]; // base RGB
  top?: [number, number, number];
  side?: [number, number, number];
  bottom?: [number, number, number];
  opaque?: boolean;
  liquid?: boolean;
  solid?: boolean; // collides with player
  transparent?: boolean; // skip fog/fill
}

const AIR = 0, GRASS = 1, DIRT = 2, STONE = 3, SAND = 4, WATER = 5,
  WOOD = 6, LEAVES = 7, SNOW = 8, PLANK = 9, GLASS = 10, FLOWER = 11,
  TORCH = 12, BEDROCK = 13;

const BLOCKS: Record<number, BlockDef> = {
  [AIR]: { id: 0, name: "Air", color: [0, 0, 0], opaque: false },
  [GRASS]: { id: 1, name: "Grass Block", color: [106, 170, 84], top: [106, 170, 84], side: [150, 116, 82], bottom: [134, 100, 72] },
  [DIRT]: { id: 2, name: "Dirt", color: [134, 100, 72] },
  [STONE]: { id: 3, name: "Stone", color: [130, 130, 134] },
  [SAND]: { id: 4, name: "Sand", color: [232, 214, 160] },
  [WATER]: { id: 5, name: "Water", color: [54, 120, 190], liquid: true, transparent: true },
  [WOOD]: { id: 6, name: "Wood Log", color: [92, 62, 38], top: [180, 140, 92], side: [92, 62, 38] },
  [LEAVES]: { id: 7, name: "Leaves", color: [58, 128, 58] },
  [SNOW]: { id: 8, name: "Snow", color: [240, 244, 250] },
  [PLANK]: { id: 9, name: "Oak Planks", color: [176, 140, 86] },
  [GLASS]: { id: 10, name: "Glass", color: [190, 225, 240], transparent: true },
  [FLOWER]: { id: 11, name: "Flower", color: [230, 80, 90] },
  [TORCH]: { id: 12, name: "Torch", color: [255, 190, 90] },
  [BEDROCK]: { id: 13, name: "Bedrock", color: [70, 70, 72] },
};

const isOpaque = (id: BlockId) => id !== AIR && id !== WATER && id !== GLASS && id !== FLOWER && id !== TORCH;
const isSolid = (id: BlockId) => id !== AIR && id !== WATER && id !== FLOWER && id !== TORCH;

const HOTBAR: number[] = [GRASS, DIRT, STONE, SAND, WOOD, PLANK, LEAVES, GLASS, TORCH];
const CRAFT = 24;

/* =========================================================================
   NOISE / WORLD
   ========================================================================= */
function hash2(x: number, z: number, seed: number) {
  let h = Math.imul(x, 374761393) ^ Math.imul(z, 668265263) ^ Math.imul(seed, 1442695041);
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  h = (h ^ (h >>> 16)) >>> 0;
  return h / 4294967295;
}
function smooth(t: number) { return t * t * (3 - 2 * t); }
function n2(x: number, z: number, seed: number) {
  const xi = Math.floor(x), zi = Math.floor(z);
  const xf = x - xi, zf = z - zi;
  const a = hash2(xi, zi, seed), b = hash2(xi + 1, zi, seed);
  const c = hash2(xi, zi + 1, seed), d = hash2(xi + 1, zi + 1, seed);
  const u = smooth(xf), v = smooth(zf);
  return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v;
}
function fbm(x: number, z: number, seed: number) {
  let s = 0, amp = 1, f = 1, norm = 0;
  for (let i = 0; i < 4; i++) { s += n2(x * f, z * f, seed + i * 97) * amp; norm += amp; amp *= 0.5; f *= 2; }
  return s / norm;
}

const SEA = 22;
const WORLD_SIZE = 84;
const MAXY = 48;
const REACH = 6;
const EYE = 1.62, PH = 1.8, RAD = 0.3;

/* =========================================================================
   SHADERS
   ========================================================================= */
const BLOCK_VS = `
uniform float fogNear; uniform float fogFar; uniform vec3 fogColor;
varying float vFog; varying vec3 vCol; varying vec3 vLight; varying vec3 vWorld; varying vec3 vN;
void main(){
  vCol = color; vLight = aLight; vN = normal;
  vec4 wp = modelMatrix * vec4(position,1.0); vWorld = wp.xyz;
  vec4 mv = modelViewMatrix * vec4(position,1.0);
  float d = max(length(mv.xyz),0.0);
  vFog = clamp((d - fogNear)/(fogFar - fogNear),0.0,1.0);
  gl_Position = projectionMatrix * mv;
}`;
const BLOCK_FS = `
precision highp float;
uniform float fogNear; uniform float fogFar; uniform vec3 fogColor;
uniform float time; uniform float dayLight;
varying float vFog; varying vec3 vCol; varying vec3 vLight; varying vec3 vWorld; varying vec3 vN;
float h3(vec3 p){ return fract(sin(dot(p, vec3(12.9898,78.233,37.719)))*43758.5453); }
void main(){
  vec3 col = vCol * vLight;
  float n = (h3(floor(vWorld*2.0)) - 0.5) * 0.13;
  col += n;
  col *= (0.42 + dayLight*0.58);
  col = mix(col, fogColor, vFog);
  gl_FragColor = vec4(col, 1.0);
}`;
const LIQ_VS = `
uniform float time; uniform float fogNear; uniform float fogFar;
varying float vFog; varying vec3 vCol; varying vec3 vLight; varying vec3 vWorld;
void main(){
  vec3 p = position;
  p.y += sin(time*1.6 + (modelMatrix*vec4(position,1.0)).x*0.7 + (modelMatrix*vec4(position,1.0)).z*0.7)*0.04;
  vCol = color; vLight = aLight;
  vec4 wp = modelMatrix*vec4(p,1.0); vWorld = wp.xyz;
  vec4 mv = modelViewMatrix*vec4(p,1.0);
  float d = max(length(mv.xyz),0.0);
  vFog = clamp((d - fogNear)/(fogFar - fogNear),0.0,1.0);
  gl_Position = projectionMatrix*mv;
}`;
const LIQ_FS = `
precision highp float;
uniform float fogNear; uniform float fogFar; uniform vec3 fogColor; uniform float dayLight;
varying float vFog; varying vec3 vCol; varying vec3 vLight; varying vec3 vWorld;
void main(){
  vec3 col = vCol*vLight*(0.5 + dayLight*0.5);
  float band = step(0.5, fract(vWorld.x*2.0)) * step(0.5, fract(vWorld.z*2.0));
  col += 0.06*band;
  col = mix(col, fogColor, vFog*0.85);
  gl_FragColor = vec4(col, 0.62);
}`;

/* =========================================================================
   GAME ENGINE (imperative)
   ========================================================================= */
class MCGame {
  canvas: HTMLCanvasElement;
  three: any;
  scene: any; camera: any; renderer: any;
  matOpaque: any; matLiquid: any;
  opaqueGeo: any; liquidGeo: any; opaqueMesh: any; liquidMesh: any;
  highlight: any;
  skyGroup: any; sun: any; moon: any; starMesh: any; sunLight: any;
  ambLight: any; hemiLight: any; torchLights: any[] = [];
  fog: any; skyMat: any; starMat: any;
  dayLight = 1; timeOfDay = 0.28; daySpeed = 0.011;
  seed = Math.floor(Math.random() * 1e6);
  grid: Int8Array;
  dirty = new Set<number>();
  cx = 0; cz = 0;
  pos = { x: 0, y: 40, z: 0 }; vel = { x: 0, y: 0, z: 0 };
  onGround = false; yaw = 0; pitch = 0;
  keys: Record<string, boolean> = {};
  hotbar = HOTBAR; slot = 0;
  inv: Record<number, number> = {};
  torchGrid = new Set<number>();
  locked = false; running = true; raf = 0; last = 0;
  sel = { x: 0, y: 0, z: 0, nx: 0, ny: 0, nz: 0, hit: false };
  // audio
  actx: any = null; master: any = null; ambGain: any = null;
  muted = false;
  // callbacks
  onStats: (s: { fps: number; x: number; y: number; z: number; time: string }) => void;
  onInv: (inv: Record<number, number>, slot: number) => void;
  onLock: (locked: boolean) => void;

  constructor(canvas: HTMLCanvasElement, cb: any) {
    this.canvas = canvas;
    this.onStats = cb.onStats; this.onInv = cb.onInv; this.onLock = cb.onLock;
    this.grid = new Int8Array(WORLD_SIZE * MAXY * WORLD_SIZE);
    this.three = window.THREE;
    this.initThree();
    this.generateWorld();
    this.rebuild();
    this.spawn();
    this.bind();
    this.last = performance.now();
    this.loop();
  }

  /* ---------- THREE setup ---------- */
  initThree() {
    const THREE = this.three;
    this.renderer = new THREE.WebGLRenderer({ canvas: this.canvas, antialias: true, powerPreference: "high-performance" });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.setSize(this.canvas.clientWidth, this.canvas.clientHeight);
    this.scene = new THREE.Scene();
    this.fog = new THREE.Fog(0x9cc4ff, 24, 68);
    this.scene.fog = this.fog;
    this.camera = new THREE.PerspectiveCamera(72, this.canvas.clientWidth / this.canvas.clientHeight, 0.05, 400);
    this.camera.rotation.order = "YXZ";

    this.skyMat = new THREE.ShaderMaterial({
      uniforms: { top: { value: new THREE.Color(0x2f6bb0) }, horizon: { value: new THREE.Color(0xbfe0ff) }, sunDir: { value: new THREE.Vector3(0, 1, 0) }, sunCol: { value: new THREE.Color(0xffffff) }, star: { value: 0 } },
      vertexShader: `varying vec3 vP; void main(){ vP = position; gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.0); }`,
      fragmentShader: `uniform vec3 top; uniform vec3 horizon; uniform vec3 sunDir; uniform vec3 sunCol; uniform float star; varying vec3 vP;
        void main(){ vec3 d = normalize(vP); float up = clamp(d.y,0.0,1.0);
        vec3 col = mix(horizon, top, pow(up,0.55));
        float sd = max(dot(d, normalize(sunDir)),0.0);
        col += sunCol * pow(sd, 4.0) * 0.35;
        col += sunCol * pow(sd, 220.0) * 1.2;
        col *= (1.0 - star*0.55);
        gl_FragColor = vec4(col,1.0); }`,
      side: THREE.BackSide, depthWrite: false,
    });
    const sky = new THREE.Mesh(new THREE.SphereGeometry(300, 32, 16), this.skyMat);
    this.scene.add(sky);

    this.sun = new THREE.Mesh(new THREE.SphereGeometry(7, 16, 16), new THREE.MeshBasicMaterial({ color: 0xfff2c0, fog: false }));
    this.moon = new THREE.Mesh(new THREE.SphereGeometry(5, 16, 16), new THREE.MeshBasicMaterial({ color: 0xdfe6ff, fog: false }));
    this.scene.add(this.sun); this.scene.add(this.moon);

    const sg = new THREE.BufferGeometry();
    const sp = []; for (let i = 0; i < 500; i++) { const u = Math.random() * 2 - 1, t = Math.random() * Math.PI * 2, r = Math.sqrt(1 - u * u); sp.push(Math.cos(t) * r * 280, Math.abs(u) * 280 + 20, Math.sin(t) * r * 280); }
    sg.setAttribute("position", new THREE.Float32BufferAttribute(sp, 3));
    this.starMat = new THREE.PointsMaterial({ color: 0xffffff, size: 1.6, fog: false, transparent: true, opacity: 0 });
    this.starMesh = new THREE.Points(sg, this.starMat);
    this.scene.add(this.starMesh);

    this.sunLight = new THREE.DirectionalLight(0xffffff, 1);
    this.ambLight = new THREE.AmbientLight(0xffffff, 0.5);
    this.hemiLight = new THREE.HemisphereLight(0xbfe0ff, 0x4a5a3a, 0.35);
    this.scene.add(this.sunLight, this.ambLight, this.hemiLight);

    const sh = (a: number, b: number, c: number) => new THREE.BufferAttribute(new Float32Array([a, b, c]), 3);
    this.matOpaque = new THREE.ShaderMaterial({
      uniforms: { fogNear: { value: 24 }, fogFar: { value: 68 }, fogColor: { value: new THREE.Color(0x9cc4ff) }, time: { value: 0 }, dayLight: { value: 1 } },
      vertexShader: BLOCK_VS, fragmentShader: BLOCK_FS,
    });
    this.matLiquid = new THREE.ShaderMaterial({
      uniforms: { fogNear: { value: 24 }, fogFar: { value: 68 }, fogColor: { value: new THREE.Color(0x9cc4ff) }, time: { value: 0 }, dayLight: { value: 1 } },
      vertexShader: LIQ_VS, fragmentShader: LIQ_FS, transparent: true, depthWrite: false, side: THREE.DoubleSide,
    });
    const mk = () => { const g = new THREE.BufferGeometry(); g.setAttribute("position", sh(0, 0, 0)); g.setAttribute("normal", sh(0, 0, 0)); g.setAttribute("color", sh(0, 0, 0)); g.setAttribute("aLight", sh(0, 0, 0)); return g; };
    this.opaqueGeo = mk(); this.liquidGeo = mk();
    this.opaqueMesh = new THREE.Mesh(this.opaqueGeo, this.matOpaque); this.opaqueMesh.frustumCulled = false;
    this.liquidMesh = new THREE.Mesh(this.liquidGeo, this.matLiquid); this.liquidMesh.frustumCulled = false; this.liquidMesh.renderOrder = 1;
    this.scene.add(this.opaqueMesh, this.liquidMesh);

    this.highlight = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(1.003, 1.003, 1.003)), new THREE.LineBasicMaterial({ color: 0x111111, transparent: true, opacity: 0.7 }));
    this.highlight.visible = false; this.scene.add(this.highlight);
  }

  /* ---------- WORLD GEN ---------- */
  gi(x: number, y: number, z: number) {
    if (x < 0 || z < 0 || y < 0 || x >= WORLD_SIZE || z >= WORLD_SIZE || y >= MAXY) return AIR;
    return this.grid[x + z * WORLD_SIZE + y * WORLD_SIZE * WORLD_SIZE];
  }
  si(x: number, y: number, z: number, id: number) {
    if (x < 0 || z < 0 || y < 0 || x >= WORLD_SIZE || z >= WORLD_SIZE || y >= MAXY) return;
    this.grid[x + z * WORLD_SIZE + y * WORLD_SIZE * WORLD_SIZE] = id;
  }
  generateWorld() {
    const s = this.seed;
    for (let x = 0; x < WORLD_SIZE; x++) for (let z = 0; z < WORLD_SIZE; z++) {
      const h = Math.round(SEA + fbm(x * 0.045, z * 0.045, s) * 16 - 6);
      const clamped = Math.max(1, Math.min(MAXY - 6, h));
      for (let y = 0; y < MAXY; y++) {
        let id = AIR;
        if (y === 0) id = BEDROCK;
        else if (y <= clamped) {
          if (y === clamped) id = clamped < SEA + 2 ? SAND : (clamped > 30 ? SNOW : GRASS);
          else if (y > clamped - 4) id = SAND;
          else id = STONE;
        } else if (y <= SEA) id = WATER;
        this.si(x, y, z, id);
      }
    }
    // trees
    for (let x = 3; x < WORLD_SIZE - 3; x++) for (let z = 3; z < WORLD_SIZE - 3; z++) {
      if (hash2(x, z, s + 55) < 0.014) {
        let top = -1; for (let y = 1; y < MAXY; y++) if (this.gi(x, y, z) === GRASS) top = y;
        if (top < 0) continue;
        const th = 4 + Math.floor(hash2(x, z, s + 9) * 3);
        for (let i = 1; i <= th; i++) this.si(x, top + i, z, WOOD);
        const cy = top + th;
        for (let dx = -2; dx <= 2; dx++) for (let dz = -2; dz <= 2; dz++) for (let dy = -1; dy <= 2; dy++) {
          if (Math.abs(dx) + Math.abs(dz) + Math.abs(dy) > 3) continue;
          if (this.gi(x + dx, cy + dy, z + dz) === AIR) this.si(x + dx, cy + dy, z + dz, LEAVES);
        }
      }
    }
    // flowers
    for (let x = 1; x < WORLD_SIZE - 1; x++) for (let z = 1; z < WORLD_SIZE - 1; z++) {
      for (let y = MAXY - 1; y >= 1; y--) if (this.gi(x, y, z) === GRASS) { if (hash2(x, z, s + 77) < 0.03 && this.gi(x, y + 1, z) === AIR) this.si(x, y + 1, z, FLOWER); break; }
    }
    this.setSpawn();
  }
  setSpawn() {
    let best = -1, by = 0;
    for (let x = 30; x < 54; x++) for (let z = 30; z < 54; z++) {
      let top = -1; for (let y = MAXY - 1; y >= 1; y--) { const b = this.gi(x, y, z); if (isSolid(b)) { top = y; break; } }
      if (top > best && top >= SEA) { best = top; by = y; }
    }
    this.pos = { x: 42.5, y: 0, z: 42.5 };
    let gy = 1; for (let y = MAXY - 1; y >= 1; y--) if (isSolid(this.gi(42, y, 42))) { gy = y + 1; break; }
    this.pos.y = gy + 0.02;
    this.vel = { x: 0, y: 0, z: 0 };
  }
  spawn() {
    this.inv = { [GRASS]: 24, [DIRT]: 16, [STONE]: 16, [SAND]: 12, [WOOD]: 8, [PLANK]: 12, [GLASS]: 8, [TORCH]: 6, [FLOWER]: 4 };
    this.onInv(this.inv, this.slot);
  }

  /* ---------- MESH REBUILD ---------- */
  markDirty(x: number, y: number, z: number) {
    for (let dx = -1; dx <= 1; dx++) for (let dz = -1; dz <= 1; dz++) this.dirty.add((x + dx) + (z + dz) * WORLD_SIZE);
  }
  rebuild() {
    const THREE = this.three;
    const op = { p: [] as number[], n: [] as number[], c: [] as number[], l: [] as number[] };
    const li = { p: [] as number[], n: [] as number[], c: [] as number[], l: [] as number[] };
    const dirs: [number, number, number][] = [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]];
    const shade = [0.86, 0.86, 1.0, 0.5, 0.74, 0.74];
    const quad = (T: any, x: number, y: number, z: number, dir: number, col: number[], sh: number) => {
      const [nx, ny, nz] = dirs[dir];
      const a = [x, y, z], b = [x, y, z], c = [x, y, z], d = [x, y, z];
      const A = (a as any), B = (b as any), C = (c as any), D = (d as any);
      if (dir === 0) { A[0]++; B[1]++; C[1]++; D[0]++; C[2]++; D[2]++; }
      else if (dir === 1) { B[0]++; D[1]++; C[1]++; A[0]++; C[2]++; D[2]++; }
      else if (dir === 2) { A[1]++; B[0]++; C[0]++; D[1]++; B[2]++; C[2]++; }
      else if (dir === 3) { C[1]++; D[0]++; A[0]++; B[1]++; B[2]++; C[2]++; }
      else if (dir === 4) { A[2]++; B[0]++; C[0]++; D[2]++; B[1]++; C[1]++; }
      else { C[2]++; D[0]++; A[0]++; B[2]++; B[1]++; C[1]++; }
      const push = (v: any) => { T.p.push(v[0], v[1], v[2]); T.n.push(nx, ny, nz); T.c.push(col[0], col[1], col[2]); T.l.push(sh, sh, sh); };
      push(a); push(b); push(c); push(a); push(c); push(d);
    };
    const colFor = (def: BlockDef, dir: number) => {
      if (dir === 2) return def.top || def.color;
      if (dir === 3) return def.bottom || def.color;
      return def.side || def.color;
    };
    for (let y = 0; y < MAXY; y++) for (let z = 0; z < WORLD_SIZE; z++) for (let x = 0; x < WORLD_SIZE; x++) {
      const id = this.gi(x, y, z); if (id === AIR) continue;
      const def = BLOCKS[id];
      const liquid = id === WATER, thin = id === FLOWER, torch = id === TORCH;
      const T = liquid ? li : op;
      if (thin) {
        const cx = x + 0.5, cz = z + 0.5;
        const c = def.color;
        const q = [
          [cx - .16, y, cz, cx + .16, y, cz, cx + .16, y + 1, cz, cx - .16, y + 1, cz],
          [cx, y, cz - .16, cx, y, cz + .16, cx, y + 1, cz + .16, cx, y + 1, cz - .16],
        ];
        for (const v of q) for (const idx of [0, 1, 2, 0, 2, 3]) { T.p.push(v[idx * 3], v[idx * 3 + 1], v[idx * 3 + 2]); T.n.push(0, 0, 0); T.c.push(c[0], c[1], c[2]); T.l.push(1, 1, 1); }
        continue;
      }
      if (torch) {
        const cx = x + 0.5, cz = z + 0.5;
        const c = def.color;
        const box = (x0: number, y0: number, z0: number, x1: number, y1: number, z1: number, s: number) => {
          const v = [[x0, y0, z0], [x1, y0, z0], [x1, y0, z1], [x0, y0, z1], [x0, y1, z0], [x1, y1, z0], [x1, y1, z1], [x0, y1, z1]];
          const f = [[0, 1, 2, 3], [7, 6, 5, 4], [0, 4, 5, 1], [2, 6, 7, 3], [1, 5, 6, 2], [0, 3, 7, 4]];
          for (const qf of f) for (const idx of [0, 1, 2, 0, 2, 3]) { T.p.push(...v[qf[idx]]); T.n.push(0, 1, 0); T.c.push(c[0], c[1], c[2]); T.l.push(s, s, s); }
        };
        box(cx - .12, y, cz - .12, cx + .12, y + .7, cz + .12, 0.8);
        box(cx - .16, y + .7, cz - .16, cx + .16, y + .95, cz + .16, 1.2);
        continue;
      }
      for (let d = 0; d < 6; d++) {
        const [nx, ny, nz] = dirs[d];
        const nb = this.gi(x + nx, y + ny, z + nz);
        if (liquid) { if (isOpaque(nb) || nb === WATER) continue; }
        else { if (nb === id) continue; if (isOpaque(nb)) continue; }
        const sh = liquid ? 0.8 : shade[d];
        quad(T, x, y, z, d, colFor(def, d), sh);
      }
    }
    const apply = (geo: any, T: any) => {
      geo.setAttribute("position", new THREE.Float32BufferAttribute(T.p, 3));
      geo.setAttribute("normal", new THREE.Float32BufferAttribute(T.n, 3));
      geo.setAttribute("color", new THREE.Float32BufferAttribute(T.c, 3));
      geo.setAttribute("aLight", new THREE.Float32BufferAttribute(T.l, 3));
      geo.computeBoundingSphere();
    };
    apply(this.opaqueGeo, op); apply(this.liquidGeo, li);
  }
  edit(x: number, y: number, z: number, id: number) {
    if (this.gi(x, y, z) === id) return;
    this.si(x, y, z, id);
    if (id === TORCH) this.torchGrid.add(x + z * WORLD_SIZE + y * WORLD_SIZE * WORLD_SIZE);
    else this.torchGrid.delete(x + z * WORLD_SIZE + y * WORLD_SIZE * WORLD_SIZE);
    this.markDirty(x, y, z);
    this.rebuild();
    this.updateTorchLights();
  }

  /* ---------- PLAYER PHYSICS ---------- */
  aabb(cx: number, cy: number, cz: number) {
    const minX = Math.floor(cx - RAD), maxX = Math.floor(cx + RAD);
    const minY = Math.floor(cy), maxY = Math.floor(cy + PH);
    const minZ = Math.floor(cz - RAD), maxZ = Math.floor(cz + RAD);
    for (let x = minX; x <= maxX; x++) for (let y = minY; y <= maxY; y++) for (let z = minZ; z <= maxZ; z++)
      if (isSolid(this.gi(x, y, z))) return true;
    return false;
  }
  updatePlayer(dt: number) {
    const sinY = Math.sin(this.yaw), cosY = Math.cos(this.yaw);
    let fx = 0, fz = 0;
    if (this.keys["KeyW"]) { fx += -sinY; fz += -cosY; }
    if (this.keys["KeyS"]) { fx += sinY; fz += cosY; }
    if (this.keys["KeyA"]) { fx += -cosY; fz += sinY; }
    if (this.keys["KeyD"]) { fx += cosY; fz += -sinY; }
    const len = Math.hypot(fx, fz) || 1; fx /= len; fz /= len;
    const sprint = this.keys["ShiftLeft"] ? 8.2 : 5.2;
    this.vel.x = fx * sprint; this.vel.z = fz * sprint;
    this.vel.y -= 26 * dt; if (this.vel.y < -45) this.vel.y = -45;
    if (this.keys["Space"] && this.onGround) { this.vel.y = 8.4; this.onGround = false; }
    // swim
    const feet = this.gi(Math.floor(this.pos.x), Math.floor(this.pos.y), Math.floor(this.pos.z));
    const head = this.gi(Math.floor(this.pos.x), Math.floor(this.pos.y + EYE), Math.floor(this.pos.z));
    const inWater = feet === WATER || head === WATER;
    if (inWater) { this.vel.y *= 0.55; if (this.keys["Space"]) this.vel.y = 3.6; }

    this.pos.x += this.vel.x * dt; if (this.aabb(this.pos.x, this.pos.y, this.pos.z)) { this.pos.x -= this.vel.x * dt; this.vel.x = 0; }
    this.pos.z += this.vel.z * dt; if (this.aabb(this.pos.x, this.pos.y, this.pos.z)) { this.pos.z -= this.vel.z * dt; this.vel.z = 0; }
    this.pos.y += this.vel.y * dt;
    this.onGround = false;
    if (this.aabb(this.pos.x, this.pos.y, this.pos.z)) {
      this.pos.y -= this.vel.y * dt;
      if (this.vel.y < 0) { this.onGround = true; this.vel.y = 0; } else this.vel.y = 0;
    }
    if (this.pos.y < -6) this.setSpawn();
  }

  /* ---------- CAMERA / SKY ---------- */
  updateCamera() {
    this.camera.position.set(this.pos.x, this.pos.y + EYE, this.pos.z);
    this.camera.rotation.set(this.pitch, this.yaw, 0);
  }
  updateSky(dt: number) {
    this.timeOfDay = (this.timeOfDay + dt * this.daySpeed) % 1;
    const ang = this.timeOfDay * Math.PI * 2 - Math.PI / 2;
    const sunDir = { x: Math.cos(ang), y: Math.sin(ang), z: 0.35 };
    const L = Math.hypot(sunDir.x, sunDir.y, sunDir.z); sunDir.x /= L; sunDir.y /= L; sunDir.z /= L;
    const elev = Math.max(0, sunDir.y);
    this.dayLight = 0.24 + elev * 0.76;
    const dawn = Math.pow(Math.max(0, 1 - Math.abs(sunDir.y) * 4), 2);
    const top = new this.three.Color(0x2f6bb0).lerp(new this.three.Color(0x0a1230), 1 - this.dayLight);
    const horizon = new this.three.Color(0xbfe0ff).lerp(new this.three.Color(0xff9a5a), dawn * 0.9).lerp(new this.three.Color(0x1a2440), 1 - this.dayLight);
    const sunCol = new this.three.Color(0xffffff).lerp(new this.three.Color(0xff7a3a), dawn * 0.7);
    this.skyMat.uniforms.top.value = top; this.skyMat.uniforms.horizon.value = horizon;
    this.skyMat.uniforms.sunDir.value = new this.three.Vector3(sunDir.x, sunDir.y, sunDir.z);
    this.skyMat.uniforms.sunCol.value = sunCol;
    const star = Math.max(0, 1 - this.dayLight * 2.4);
    this.skyMat.uniforms.star.value = star; this.starMat.opacity = star;
    const fogCol = top.clone().lerp(horizon, 0.35);
    this.fog.color = fogCol; this.matOpaque.uniforms.fogColor.value = fogCol; this.matLiquid.uniforms.fogColor.value = fogCol;
    this.sunLight.position.set(this.pos.x + sunDir.x * 60, this.pos.y + Math.max(0, sunDir.y) * 60 + 6, this.pos.z + sunDir.z * 60);
    this.sunLight.intensity = 0.4 + elev * 1.1;
    this.sunLight.color = new this.three.Color(0xffffff).lerp(new this.three.Color(0xffb066), dawn * 0.6);
    this.ambLight.intensity = 0.34 + this.dayLight * 0.42;
    this.hemiLight.color = top; this.hemiLight.intensity = 0.25 + this.dayLight * 0.2;
    this.sun.position.set(this.pos.x + sunDir.x * 200, this.pos.y + sunDir.y * 200, this.pos.z + sunDir.z * 200);
    this.moon.position.set(this.pos.x - sunDir.x * 200, this.pos.y - sunDir.y * 200, this.pos.z - sunDir.z * 200);
    this.sun.visible = sunDir.y > -0.2; this.moon.visible = sunDir.y < 0.2;
  }
  updateTorchLights() {
    const THREE = this.three;
    for (const t of this.torchLights) this.scene.remove(t);
    this.torchLights = [];
    let count = 0;
    for (const key of this.torchGrid) {
      if (count >= 8) break;
      const y = Math.floor(key / (WORLD_SIZE * WORLD_SIZE));
      const r = key % (WORLD_SIZE * WORLD_SIZE);
      const z = Math.floor(r / WORLD_SIZE), x = r % WORLD_SIZE;
      const d = Math.hypot(x - this.pos.x, z - this.pos.z);
      if (d > 34) continue;
      const lt = new THREE.PointLight(0xffa64d, 1.4, 9, 2);
      lt.position.set(x + 0.5, y + 0.85, z + 0.5);
      this.scene.add(lt); this.torchLights.push(lt); count++;
    }
  }
  raycast() {
    const cam = this.camera, org = cam.position;
    const dir = new this.three.Vector3(0, 0, -1).applyQuaternion(cam.quaternion).normalize();
    let x = Math.floor(org.x), y = Math.floor(org.y), z = Math.floor(org.z);
    const sx = dir.x > 0 ? 1 : -1, sy = dir.y > 0 ? 1 : -1, sz = dir.z > 0 ? 1 : -1;
    const dx = dir.x !== 0 ? Math.abs(1 / dir.x) : Infinity;
    const dy = dir.y !== 0 ? Math.abs(1 / dir.y) : Infinity;
    const dz = dir.z !== 0 ? Math.abs(1 / dir.z) : Infinity;
    let tmx = dir.x !== 0 ? ((sx > 0 ? x + 1 - org.x : org.x - x) * dx) : Infinity;
    let tmy = dir.y !== 0 ? ((sy > 0 ? y + 1 - org.y : org.y - y) * dy) : Infinity;
    let tmz = dir.z !== 0 ? ((sz > 0 ? z + 1 - org.z : org.z - z) * dz) : Infinity;
    let nx = 0, ny = 0, nz = 0, dist = 0;
    for (let i = 0; i < 64; i++) {
      if (tmx < tmy && tmx < tmz) { x += sx; dist = tmx; tmx += dx; nx = -sx; ny = 0; nz = 0; }
      else if (tmy < tmz) { y += sy; dist = tmy; tmy += dy; nx = 0; ny = -sy; nz = 0; }
      else { z += sz; dist = tmz; tmz += dz; nx = 0; ny = 0; nz = -sz; }
      if (dist > REACH) break;
      if (isSolid(this.gi(x, y, z))) { this.sel = { x, y, z, nx, ny, nz, hit: true }; return; }
    }
    this.sel = { x, y, z, nx, ny, nz, hit: false };
  }

  /* ---------- INPUT ---------- */
  bind() {
    window.addEventListener("keydown", this.kd);
    window.addEventListener("keyup", this.ku);
    window.addEventListener("resize", this.resize);
    document.addEventListener("pointerlockchange", this.plock);
    document.addEventListener("mousemove", this.mm);
    document.addEventListener("wheel", this.wheel, { passive: true });
    this.canvas.addEventListener("mousedown", this.md);
    this.canvas.addEventListener("contextmenu", (e) => e.preventDefault());
  }
  kd = (e: KeyboardEvent) => {
    this.keys[e.code] = true;
    if (e.code === "KeyE") { this.toggleCraft(); }
    if (e.code >= "Digit1" && e.code <= "Digit9") { this.slot = +e.code.slice(5) - 1; this.onInv(this.inv, this.slot); }
  };
  ku = (e: KeyboardEvent) => { this.keys[e.code] = false; };
  mm = (e: MouseEvent) => {
    if (!this.locked) return;
    this.yaw -= e.movementX * 0.0022;
    this.pitch -= e.movementY * 0.0022;
    this.pitch = Math.max(-1.5, Math.min(1.5, this.pitch));
  };
  wheel = (e: WheelEvent) => {
    if (!this.locked) return;
    this.slot = (this.slot + (e.deltaY > 0 ? 1 : -1) + 9) % 9;
    this.onInv(this.inv, this.slot);
  };
  plock = () => {
    this.locked = document.pointerLockElement === this.canvas;
    this.onLock(this.locked);
  };
  md = (e: MouseEvent) => {
    if (!this.locked) return;
    if (e.button === 0) this.breakBlock();
    else if (e.button === 2) this.placeBlock();
  };
  breakBlock() {
    if (!this.sel.hit) return;
    const { x, y, z } = this.sel;
    const id = this.gi(x, y, z);
    if (id === BEDROCK) return;
    this.edit(x, y, z, AIR);
    const drop = id === GRASS ? DIRT : id === LEAVES ? (hash2(x, z, this.seed) < 0.5 ? WOOD : LEAVES) : id;
    this.inv[drop] = (this.inv[drop] || 0) + 1;
    this.playSound("break"); this.onInv(this.inv, this.slot);
  }
  placeBlock() {
    if (!this.sel.hit) return;
    const item = this.hotbar[this.slot];
    if ((this.inv[item] || 0) <= 0) return;
    const tx = this.sel.x + this.sel.nx, ty = this.sel.y + this.sel.ny, tz = this.sel.z + this.sel.nz;
    if (ty < 1 || ty >= MAXY) return;
    if (isSolid(this.gi(tx, ty, tz))) return;
    // don't place inside player
    if (item !== TORCH && item !== FLOWER) {
      const pminx = this.pos.x - RAD, pmaxx = this.pos.x + RAD, pzmin = this.pos.z - RAD, pzmax = this.pos.z + RAD, pymin = this.pos.y, pymax = this.pos.y + PH;
      if (tx + 1 > pminx && tx < pmaxx && tz + 1 > pzmin && tz < pzmax && ty + 1 > pymin && ty < pymax) return;
    }
    this.edit(tx, ty, tz, item);
    this.inv[item]--;
    this.playSound("place"); this.onInv(this.inv, this.slot);
  }
  toggleCraft() {
    if (this.locked) { document.exitPointerLock(); this.craftOpen = true; this.onInv(this.inv, this.slot); }
    else if (this.craftOpen) { this.craftOpen = false; this.canvas.requestPointerLock(); }
  }
  craftOpen = false;
  craft(recipe: number[]) {
    for (const [out, need] of Object.entries({ [PLANK]: 4 })) {
      const id = +out; if (this.inv[id] >= need) { this.inv[id] -= need; this.inv[recipe] = (this.inv[recipe] || 0) + 1; }
    }
    this.playSound("craft"); this.onInv(this.inv, this.slot);
  }
  craftFrom(ing: number, out: number, ratio: number) {
    const have = this.inv[ing] || 0; if (have < ratio) return;
    this.inv[ing] -= ratio; this.inv[out] = (this.inv[out] || 0) + 1;
    this.playSound("craft"); this.onInv(this.inv, this.slot);
  }
  pick(id: number) {
    this.slot = this.hotbar.indexOf(id);
    if (this.slot < 0) { this.hotbar[8] = id; this.slot = 8; }
    this.onInv(this.inv, this.slot);
  }
  setBlock(i: number, id: number) { this.hotbar[i] = id; this.slot = i; this.onInv(this.inv, this.slot); }

  /* ---------- AUDIO ---------- */
  ensureAudio() {
    if (this.actx) { if (this.actx.state === "suspended") this.actx.resume(); return; }
    try {
      this.actx = new (window.AudioContext || (window as any).webkitAudioContext)();
      this.master = this.actx.createGain(); this.master.gain.value = this.muted ? 0 : 0.5; this.master.connect(this.actx.destination);
      const amb = this.actx.createGain(); amb.gain.value = 0.12; amb.connect(this.master);
      const buf = this.actx.createBuffer(1, this.actx.sampleRate * 3, this.actx.sampleRate);
      const d = buf.getChannelData(0);
      for (let i = 0; i < d.length; i++) d[i] = (Math.random() * 2 - 1) * 0.5;
      const src = this.actx.createBufferSource(); src.buffer = buf; src.loop = true;
      const lp = this.actx.createBiquadFilter(); lp.type = "lowpass"; lp.frequency.value = 420;
      src.connect(lp); lp.connect(amb); src.start();
      this.ambGain = amb;
    } catch (e) { }
  }
  playSound(kind: string) {
    if (!this.actx) return;
    const t = this.actx.currentTime;
    const o = this.actx.createOscillator(), g = this.actx.createGain();
    o.connect(g); g.connect(this.master);
    if (kind === "break") { o.type = "square"; o.frequency.setValueAtTime(180, t); o.frequency.exponentialRampToValueAtTime(90, t + 0.12); g.gain.setValueAtTime(0.3, t); g.gain.exponentialRampToValueAtTime(0.001, t + 0.14); o.start(t); o.stop(t + 0.15); }
    else if (kind === "place") { o.type = "sine"; o.frequency.setValueAtTime(320, t); o.frequency.exponentialRampToValueAtTime(500, t + 0.08); g.gain.setValueAtTime(0.25, t); g.gain.exponentialRampToValueAtTime(0.001, t + 0.12); o.start(t); o.stop(t + 0.13); }
    else if (kind === "craft") { o.type = "triangle"; o.frequency.setValueAtTime(600, t); o.frequency.exponentialRampToValueAtTime(900, t + 0.12); g.gain.setValueAtTime(0.2, t); g.gain.exponentialRampToValueAtTime(0.001, t + 0.18); o.start(t); o.stop(t + 0.2); }
  }
  toggleMute() { this.muted = !this.muted; if (this.master) this.master.gain.value = this.muted ? 0 : 0.5; }

  resize = () => {
    const w = this.canvas.clientWidth, h = this.canvas.clientHeight;
    this.renderer.setSize(w, h); this.camera.aspect = w / h; this.camera.updateProjectionMatrix();
  };

  /* ---------- LOOP ---------- */
  loop = () => {
    if (!this.running) return;
    this.raf = requestAnimationFrame(this.loop);
    const now = performance.now();
    let dt = (now - this.last) / 1000; this.last = now;
    dt = Math.min(dt, 0.05);
    if (this.locked) this.updatePlayer(dt);
    this.updateCamera();
    this.updateSky(dt);
    this.raycast();
    if (this.sel.hit) { this.highlight.visible = true; this.highlight.position.set(this.sel.x + 0.5, this.sel.y + 0.5, this.sel.z + 0.5); }
    else this.highlight.visible = false;
    this.matOpaque.uniforms.time.value = now / 1000; this.matOpaque.uniforms.dayLight.value = this.dayLight;
    this.matLiquid.uniforms.time.value = now / 1000; this.matLiquid.uniforms.dayLight.value = this.dayLight;
    this.updateTorchLights();
    this.renderer.render(this.scene, this.camera);
    const t = ((this.timeOfDay * 24 + 6) % 24);
    const hh = Math.floor(t), mm = Math.floor((t - hh) * 60);
    this.onStats({ fps: Math.round(1 / Math.max(dt, 0.0001)), x: Math.floor(this.pos.x), y: Math.floor(this.pos.y), z: Math.floor(this.pos.z), time: `${String(hh).padStart(2, "0")}:${String(mm).padStart(2, "0")}` });
  };

  start() { this.ensureAudio(); this.canvas.requestPointerLock(); }
  destroy() {
    this.running = false; cancelAnimationFrame(this.raf);
    window.removeEventListener("keydown", this.kd); window.removeEventListener("keyup", this.ku);
    window.removeEventListener("resize", this.resize); document.removeEventListener("pointerlockchange", this.plock);
    document.removeEventListener("mousemove", this.mm); document.removeEventListener("wheel", this.wheel);
    this.renderer.dispose();
  }
}

/* =========================================================================
   UI HELPERS
   ========================================================================= */
const rgb = (c: number[]) => `rgb(${c[0]},${c[1]},${c[2]})`;
const shadeCol = (c: number[], f: number) => `rgb(${Math.min(255, c[0] * f) | 0},${Math.min(255, c[1] * f) | 0},${Math.min(255, c[2] * f) | 0})`;

function CubeIcon({ def, size = 46 }: { def: BlockDef; size?: number }) {
  const top = def.top || def.color, side = def.side || def.color, bot = def.bottom || def.color;
  const s = size;
  return (
    <svg width={s} height={s} viewBox="0 0 32 32" style={{ imageRendering: "pixelated" }}>
      <polygon points="16,3 29,10 16,17 3,10" fill={rgb(top)} />
      <polygon points="3,10 16,17 16,29 3,22" fill={shadeCol(side, 0.78)} />
      <polygon points="16,17 29,10 29,22 16,29" fill={shadeCol(side, 1)} />
    </svg>
  );
}

/* =========================================================================
   MAIN COMPONENT
   ========================================================================= */
export default function MinecraftSandbox() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const gameRef = useRef<MCGame | null>(null);
  const [ready, setReady] = useState(false);
  const [locked, setLocked] = useState(false);
  const [stats, setStats] = useState({ fps: 0, x: 0, y: 0, z: 0, time: "08:00" });
  const [inv, setInv] = useState<Record<number, number>>({});
  const [slot, setSlot] = useState(0);
  const [hotbar, setHotbar] = useState<number[]>(HOTBAR);
  const [craftOpen, setCraftOpen] = useState(false);
  const [muted, setMuted] = useState(false);
  const [pick, setPick] = useState<number | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current!;
    const game = new MCGame(canvas, {
      onStats: setStats,
      onInv: (i: Record<number, number>, s: number) => { setInv({ ...i }); setSlot(s); },
      onLock: (l: boolean) => { setLocked(l); if (!l) setPick(null); },
    });
    gameRef.current = game;
    setReady(true);
    return () => game.destroy();
  }, []);

  // keep hotbar in sync
  useEffect(() => { if (gameRef.current) setHotbar([...gameRef.current.hotbar]); }, [slot]);

  const start = () => { gameRef.current?.start(); };
  const toggleMute = () => { gameRef.current?.toggleMute(); setMuted((m) => !m); };
  const openCraft = () => { gameRef.current?.toggleCraft(); };

  const isDay = stats.time >= "06:00" && stats.time < "18:00";

  return (
    <div className="fixed inset-0 overflow-hidden bg-[#0a1230] font-mono text-white select-none">
      <canvas ref={canvasRef} className="absolute inset-0 h-full w-full" style={{ cursor: locked ? "none" : "crosshair" }} />

      {/* ===== START SCREEN ===== */}
      {!ready && (
        <div className="absolute inset-0 z-40 flex items-center justify-center bg-[#0a1230]">
          <div className="text-center">
            <div className="mb-4 text-3xl font-bold tracking-widest">VoxelCraft</div>
            <div className="text-sm text-slate-300 animate-pulse">Generating world…</div>
          </div>
        </div>
      )}

      {ready && !locked && !craftOpen && (
        <div className="absolute inset-0 z-30 flex items-center justify-center bg-black/55 backdrop-blur-sm">
          <div className="mx-4 max-w-md w-full rounded-2xl border border-emerald-400/40 bg-[#111b2e]/90 p-8 shadow-2xl">
            <div className="mb-1 text-center text-4xl font-black tracking-tight text-emerald-300">VoxelCraft</div>
            <div className="mb-6 text-center text-xs uppercase tracking-[0.3em] text-slate-400">Minecraft-style 3D Sandbox</div>
            <button onClick={start} className="mb-6 w-full rounded-xl bg-emerald-500 py-3 text-lg font-bold text-[#062018] shadow-lg shadow-emerald-500/30 transition hover:bg-emerald-400 active:scale-[0.98]">
              ▶ Start Exploring
            </button>
            <div className="grid grid-cols-2 gap-x-6 gap-y-2 text-sm text-slate-300">
              <Ctrl k="WASD" v="Move" /><Ctrl k="Mouse" v="Look around" />
              <Ctrl k="Space" v="Jump / Swim" /><Ctrl k="Shift" v="Sprint" />
              <Ctrl k="Left Click" v="Break block" /><Ctrl k="Right Click" v="Place block" />
              <Ctrl k="1–9 / Scroll" v="Select block" /><Ctrl k="E" v="Crafting" />
            </div>
            <div className="mt-6 text-center text-xs text-slate-500">Click to capture the mouse · Press <span className="text-slate-300">Esc</span> to release</div>
          </div>
        </div>
      )}

      {/* ===== HUD (crosshair + info) ===== */}
      {ready && (
        <>
          <div className="pointer-events-none absolute left-4 top-4 z-20 rounded-lg bg-black/40 px-3 py-2 text-[11px] leading-relaxed text-slate-200">
            <div className="mb-1 font-bold text-emerald-300">VoxelCraft</div>
            <div>{stats.fps} fps · {isDay ? "☀ Day" : "🌙 Night"}</div>
            <div>XYZ {stats.x}, {stats.y}, {stats.z}</div>
            <div>Time {stats.time}</div>
          </div>

          <div className="pointer-events-none absolute right-4 top-4 z-20 flex gap-2">
            <button onClick={toggleMute} className="rounded-lg bg-black/40 px-3 py-2 text-sm hover:bg-black/60">{muted ? "🔇" : "🔊"}</button>
            <button onClick={openCraft} className="rounded-lg bg-black/40 px-3 py-2 text-sm hover:bg-black/60">🔨 Craft</button>
          </div>

          {locked && (
            <div className="pointer-events-none absolute left-1/2 top-1/2 z-20 -translate-x-1/2 -translate-y-1/2">
              <div className="h-5 w-5 relative">
                <div className="absolute left-1/2 top-0 h-5 w-0.5 -translate-x-1/2 bg-white/80 mix-blend-difference" />
                <div className="absolute top-1/2 left-0 h-0.5 w-5 -translate-y-1/2 bg-white/80 mix-blend-difference" />
              </div>
            </div>
          )}
        </>
      )}

      {/* ===== HOTBAR ===== */}
      {ready && (
        <div className="absolute bottom-5 left-1/2 z-20 flex -translate-x-1/2 gap-1.5 rounded-xl border border-white/15 bg-black/45 p-1.5 backdrop-blur-sm">
          {hotbar.map((id, i) => {
            const def = BLOCKS[id];
            const count = inv[id] || 0;
            return (
              <div key={i} className={`relative h-14 w-14 rounded-lg border-2 transition ${i === slot ? "border-emerald-300 bg-white/10 scale-105" : "border-white/15 bg-white/5"}`}>
                <div className="absolute inset-0 flex items-center justify-center"><CubeIcon def={def} size={40} /></div>
                <span className="absolute left-1 top-0.5 text-[10px] text-white/50">{i + 1}</span>
                {count > 0 && <span className="absolute bottom-0.5 right-1 text-xs font-bold text-white drop-shadow">{count}</span>}
              </div>
            );
          })}
        </div>
      )}

      {/* ===== CRAFTING ===== */}
      {craftOpen && gameRef.current && (
        <div className="absolute inset-0 z-40 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={openCraft}>
          <div className="mx-4 w-full max-w-lg rounded-2xl border border-amber-400/40 bg-[#141d2e]/95 p-6 shadow-2xl" onClick={(e) => e.stopPropagation()}>
            <div className="mb-1 text-2xl font-black text-amber-300">🔨 Crafting</div>
            <div className="mb-5 text-xs text-slate-400">Combine resources. Click a result to craft. Press <span className="text-slate-200">E</span> to resume.</div>

            <div className="mb-4">
              <div className="mb-2 text-xs uppercase tracking-widest text-slate-400">Recipes</div>
              <div className="grid grid-cols-2 gap-3">
                <Recipe out={PLANK} from={WOOD} ratio={1} inv={inv} onCraft={() => gameRef.current!.craftFrom(WOOD, PLANK, 1)} />
                <Recipe out={GLASS} from={SAND} ratio={2} inv={inv} onCraft={() => gameRef.current!.craftFrom(SAND, GLASS, 1)} />
                <Recipe out={TORCH} from={WOOD} ratio={1} inv={inv} onCraft={() => gameRef.current!.craftFrom(WOOD, TORCH, 1)} />
                <Recipe out={FLOWER} from={GRASS} ratio={1} inv={inv} onCraft={() => gameRef.current!.craftFrom(GRASS, FLOWER, 1)} />
              </div>
            </div>

            <div className="mb-2 text-xs uppercase tracking-widest text-slate-400">Inventory</div>
            <div className="grid grid-cols-6 gap-2">
              {Object.entries(BLOCKS).filter(([id]) => +id !== 0).map(([id]) => {
                const def = BLOCKS[+id]; const count = inv[+id] || 0;
                return (
                  <button key={id} onClick={() => { gameRef.current!.pick(+id); setHotbar([...gameRef.current!.hotbar]); }}
                    className={`relative h-14 rounded-lg border transition ${count > 0 ? "border-white/20 bg-white/5 hover:bg-white/10" : "border-white/5 bg-white/5 opacity-40"}`}>
                    <div className="flex h-full items-center justify-center"><CubeIcon def={def} size={34} /></div>
                    {count > 0 && <span className="absolute bottom-0.5 right-1 text-[11px] font-bold">{count}</span>}
                  </button>
                );
              })}
            </div>
            <div className="mt-5 text-center text-xs text-slate-500">Tip: click an item to assign it to your selected hotbar slot.</div>
          </div>
        </div>
      )}
    </div>
  );
}

function Ctrl({ k, v }: { k: string; v: string }) {
  return <div className="flex items-center gap-2"><kbd className="rounded bg-white/10 px-2 py-0.5 text-[11px] font-bold text-white">{k}</kbd><span className="text-slate-400">{v}</span></div>;
}
function Recipe({ out, from, ratio, inv, onCraft }: { out: number; from: number; ratio: number; inv: Record<number, number>; onCraft: () => void }) {
  const can = (inv[from] || 0) >= ratio;
  return (
    <button onClick={onCraft} disabled={!can} className={`flex items-center justify-between gap-2 rounded-xl border p-3 transition ${can ? "border-amber-400/50 bg-amber-400/10 hover:bg-amber-400/20" : "border-white/10 bg-white/5 opacity-50"}`}>
      <div className="flex items-center gap-1 text-xs">
        <div className="flex items-center"><CubeIcon def={BLOCKS[from]} size={26} /><span className="ml-1 text-slate-300">×{ratio}</span></div>
        <span className="mx-1 text-slate-400">→</span>
        <CubeIcon def={BLOCKS[out]} size={26} />
      </div>
      <span className="text-[11px] font-bold text-amber-200">{can ? "Craft" : "Need " + ratio}</span>
    </button>
  );
}
