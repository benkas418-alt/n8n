// Photoreal silicone bracelet (202 x 12 x 2 mm) rendered with three.js.
// Units are millimetres. The scene is driven by a plain "shot" object that
// the GSAP timeline tweens, so every frame can be rendered on demand.
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { BokehPass } from 'three/addons/postprocessing/BokehPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { RectAreaLightUniformsLib } from 'three/addons/lights/RectAreaLightUniformsLib.js';

const R_IN = 202 / (2 * Math.PI) - 1; // inner radius, so the mid-line is 202 mm long
const THICK = 2;
const WIDTH = 12;
const CORNER = 0.75;

/* ---------- Geometry: a rounded-rectangle profile revolved around Y ---------- */
function profile() {
  const ro = R_IN + THICK;
  const h = WIDTH / 2;
  const faces = { outer: [], top: [], inner: [], bottom: [] };
  const arc = (cx, cy, a0, a1, n, out) => {
    for (let i = 0; i <= n; i++) {
      const a = a0 + (a1 - a0) * (i / n);
      out.push({ r: cx + CORNER * Math.cos(a), y: cy + CORNER * Math.sin(a), nr: Math.cos(a), ny: Math.sin(a) });
    }
  };
  // About 0.1 mm between rows, so the displaced engraving keeps sharp walls.
  const ROWS = 104;
  for (let i = 0; i <= ROWS; i++) {
    faces.outer.push({ r: ro, y: -h + CORNER + (WIDTH - 2 * CORNER) * (i / ROWS), nr: 1, ny: 0 });
  }
  arc(ro - CORNER, h - CORNER, 0, Math.PI / 2, 8, faces.top);
  arc(R_IN + CORNER, h - CORNER, Math.PI / 2, Math.PI, 8, faces.top);
  for (let i = 0; i <= ROWS; i++) {
    faces.inner.push({ r: R_IN, y: h - CORNER - (WIDTH - 2 * CORNER) * (i / ROWS), nr: -1, ny: 0 });
  }
  arc(R_IN + CORNER, -h + CORNER, Math.PI, 1.5 * Math.PI, 8, faces.bottom);
  arc(ro - CORNER, -h + CORNER, 1.5 * Math.PI, 2 * Math.PI, 8, faces.bottom);
  return faces;
}

// u runs around the band; v follows the height on the band (0 = bottom, 1 = top),
// so a texture row maps to the same height on every face.
function revolve(points, segments, flipU) {
  const pos = [];
  const nor = [];
  const uv = [];
  const idx = [];
  for (let s = 0; s <= segments; s++) {
    const u = s / segments;
    const phi = u * Math.PI * 2;
    const c = Math.cos(phi);
    const sn = Math.sin(phi);
    for (const p of points) {
      pos.push(p.r * sn, p.y, p.r * c);
      nor.push(p.nr * sn, p.ny, p.nr * c);
      uv.push(flipU ? 1 - u : u, (p.y + WIDTH / 2) / WIDTH);
    }
  }
  const n = points.length;
  for (let s = 0; s < segments; s++) {
    for (let i = 0; i < n - 1; i++) {
      const a = s * n + i;
      const b = (s + 1) * n + i;
      idx.push(a, b, a + 1, b, b + 1, a + 1);
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute('normal', new THREE.Float32BufferAttribute(nor, 3));
  g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
  g.setIndex(idx);
  return g;
}

/* ---------- Materials from the maps made by scripts/make_bracelet_maps.py ---------- */
const DESIGNS = {
  gojo: { sheen: 0.4, sheenColor: '#b48cff', clearcoat: 0.15, neon: true },
  toji: { sheen: 0.08, sheenColor: '#ffffff', clearcoat: 0.08, neon: false },
};
const DEPTH = 0.45; // engraving depth in mm, same as the maps

const loader = new THREE.TextureLoader();
const load = (src, srgb) => new Promise((res, rej) => loader.load(src, (t) => {
  t.colorSpace = srgb ? THREE.SRGBColorSpace : THREE.NoColorSpace;
  t.anisotropy = 8;
  t.wrapS = THREE.RepeatWrapping;
  res(t);
}, undefined, () => rej(new Error(`cannot load ${src}`))));

async function faceMaterial(kind, face, displaced) {
  const d = DESIGNS[kind];
  const pre = `assets/tex/${kind}_${face}`;
  const [map, height, normal, rough, glow] = await Promise.all([
    load(`${pre}_color.jpg`, true), load(`${pre}_height.png`), load(`${pre}_normal.png`), load(`${pre}_rough.png`),
    d.neon && face === 'outer' ? load(`${pre}_glow.jpg`, true) : null,
  ]);
  const m = new THREE.MeshPhysicalMaterial({
    map,
    normalMap: normal,
    roughnessMap: rough,
    roughness: 1,
    sheen: d.sheen,
    sheenRoughness: 0.7,
    sheenColor: new THREE.Color(d.sheenColor),
    clearcoat: d.clearcoat,
    clearcoatRoughness: 0.45,
  });
  if (displaced) {
    // The groove is cut into the geometry, so the letters have real walls.
    m.displacementMap = height;
    m.displacementScale = -DEPTH;
  }
  if (glow) {
    m.emissiveMap = glow;
    m.emissive = new THREE.Color('#ffffff');
    m.emissiveIntensity = 1;
  }
  return m;
}

export async function createBracelet(kind) {
  const faces = profile();
  const group = new THREE.Group();
  const [outerMat, innerMat, rimMat] = await Promise.all([
    faceMaterial(kind, 'outer', true), faceMaterial(kind, 'inner', true), faceMaterial(kind, 'outer', false),
  ]);
  const outer = new THREE.Mesh(revolve(faces.outer, 3072, false), outerMat);
  const inner = new THREE.Mesh(revolve(faces.inner, 3072, true), innerMat);
  const top = new THREE.Mesh(revolve(faces.top, 1024, false), rimMat);
  const bottom = new THREE.Mesh(revolve(faces.bottom, 1024, false), rimMat);
  group.add(outer, inner, top, bottom);
  group.traverse((o) => { o.castShadow = true; o.receiveShadow = true; });
  group.userData.neon = outerMat;
  return group;
}

function canvas(w, h) {
  const c = document.createElement('canvas');
  c.width = w;
  c.height = h;
  return c;
}

/* ---------- Studio ---------- */
export async function createStudio(canvasEl, { width, height }) {
  const renderer = new THREE.WebGLRenderer({ canvas: canvasEl, antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1);
  renderer.setSize(width, height, false);
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 0.9;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  const scene = new THREE.Scene();
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  scene.environmentIntensity = 0.35;
  scene.background = new THREE.Color('#050506');

  // Backdrop: a card fixed to the camera, with a soft coloured glow.
  const glowCanvas = canvas(540, 960);
  const backdrop = new THREE.Mesh(
    new THREE.PlaneGeometry(1, 1),
    new THREE.MeshBasicMaterial({ map: new THREE.CanvasTexture(glowCanvas), toneMapped: false, depthWrite: false }),
  );
  backdrop.material.map.colorSpace = THREE.SRGBColorSpace;
  backdrop.renderOrder = -1;
  const paintBackdrop = (color) => {
    const x = glowCanvas.getContext('2d');
    x.fillStyle = '#050506';
    x.fillRect(0, 0, 540, 960);
    const g = x.createRadialGradient(270, 430, 0, 270, 430, 420);
    g.addColorStop(0, color);
    g.addColorStop(1, 'rgba(5,5,6,0)');
    x.fillStyle = g;
    x.fillRect(0, 0, 540, 960);
    backdrop.material.map.needsUpdate = true;
  };

  // Floor that only catches the soft shadow.
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(600, 600), new THREE.ShadowMaterial({ opacity: 0.45 }));
  floor.rotation.x = -Math.PI / 2;
  floor.position.y = -6.2;
  floor.receiveShadow = true;
  scene.add(floor);

  const key = new THREE.SpotLight('#ffffff', 14000, 0, 0.45, 0.6, 2);
  key.castShadow = true;
  scene.add(key.target);
  key.shadow.mapSize.set(2048, 2048);
  key.shadow.radius = 6;
  key.shadow.bias = -0.0004;
  scene.add(key);
  const rimA = new THREE.PointLight('#8a4dff', 5000, 0, 2);
  rimA.position.set(-80, 30, -60);
  const rimB = new THREE.PointLight('#ff3040', 0, 0, 2);
  rimB.position.set(80, 20, -70);
  const fill = new THREE.PointLight('#ffffff', 600, 0, 2);
  fill.position.set(-60, 10, 90);
  scene.add(rimA, rimB, fill);

  // A long softbox that sweeps across the band: the moving highlight shows the relief.
  RectAreaLightUniformsLib.init();
  const sweep = new THREE.RectAreaLight('#ffffff', 0, 14, 160);
  scene.add(sweep);

  const camera = new THREE.PerspectiveCamera(30, width / height, 1, 3000);
  camera.add(backdrop);
  scene.add(camera);

  const composer = new EffectComposer(renderer);
  composer.setSize(width, height);
  composer.addPass(new RenderPass(scene, camera));
  const bokeh = new BokehPass(scene, camera, { focus: 100, aperture: 0.0002, maxblur: 0.01 });
  composer.addPass(bokeh);
  composer.addPass(new OutputPass());

  const rings = {};
  for (const kind of ['gojo', 'toji']) {
    rings[kind] = await createBracelet(kind);
    rings[kind].visible = false;
    scene.add(rings[kind]);
  }

  const target = new THREE.Vector3();
  // shot: { gojo, toji: {visible, x, y, z, rx, ry, rz, s}, cam: {theta, phi, dist, tx, ty, tz, fov, roll},
  //         focus, aperture, glow, rim }
  function render(shot) {
    for (const kind of ['gojo', 'toji']) {
      const r = rings[kind];
      const p = shot[kind];
      r.visible = p.visible > 0.5;
      r.position.set(p.x, p.y, p.z);
      r.rotation.set(p.rx, p.ry, p.rz, 'YXZ');
      r.scale.setScalar(p.s ?? 1);
    }
    const c = shot.cam;
    target.set(c.tx, c.ty, c.tz);
    camera.fov = c.fov;
    camera.position.set(
      target.x + c.dist * Math.cos(c.phi) * Math.sin(c.theta),
      target.y + c.dist * Math.sin(c.phi),
      target.z + c.dist * Math.cos(c.phi) * Math.cos(c.theta),
    );
    camera.up.set(Math.sin(c.roll), Math.cos(c.roll), 0);
    camera.lookAt(target);
    camera.updateProjectionMatrix();
    const far = 2000;
    const bh = 2 * far * Math.tan(THREE.MathUtils.degToRad(c.fov / 2));
    backdrop.position.set(0, 0, -far);
    backdrop.scale.set(bh * camera.aspect, bh, 1);
    floor.visible = shot.floor > 0.5;
    key.castShadow = floor.visible;
    rimA.color.set(shot.rimA);
    rimB.intensity = shot.rimB;
    // Key light on a sphere around the target: azimuth, elevation, intensity.
    const L = shot.light;
    key.position.set(
      target.x + 220 * Math.cos(L.el) * Math.sin(L.az),
      target.y + 220 * Math.sin(L.el),
      target.z + 220 * Math.cos(L.el) * Math.cos(L.az),
    );
    key.target.position.copy(target);
    key.intensity = L.int;
    // The softbox slides sideways in front of the target, facing it.
    sweep.intensity = shot.sweep.int;
    sweep.position.set(target.x + shot.sweep.x, target.y + 40, target.z + 70);
    sweep.lookAt(target);
    for (const kind of ['gojo', 'toji']) rings[kind].userData.neon.emissiveIntensity = shot.neon;
    if (shot.backdrop !== render.lastBackdrop) {
      paintBackdrop(shot.backdrop);
      render.lastBackdrop = shot.backdrop;
    }
    bokeh.uniforms.focus.value = shot.focus || c.dist;
    bokeh.uniforms.aperture.value = shot.aperture;
    bokeh.uniforms.maxblur.value = 0.012;
    composer.render();
  }

  return { render, rings, renderer };
}
