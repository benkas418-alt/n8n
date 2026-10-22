// Photoreal silicone bracelet (202 x 12 x 2 mm) rendered with three.js.
// Units are millimetres. The scene is driven by a plain "shot" object that
// the GSAP timeline tweens, so every frame can be rendered on demand.
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { BokehPass } from 'three/addons/postprocessing/BokehPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

const R_IN = 202 / (2 * Math.PI) - 1; // inner radius, so the mid-line is 202 mm long
const THICK = 2;
const WIDTH = 12;
const CORNER = 0.75;
const TEX_W = 8192;
const TEX_H = 512;

const loadImage = (src) => new Promise((res, rej) => {
  const img = new Image();
  img.onload = () => res(img);
  img.onerror = () => rej(new Error(`cannot load ${src}`));
  img.src = src;
});

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
  for (let i = 0; i <= 24; i++) {
    faces.outer.push({ r: ro, y: -h + CORNER + (WIDTH - 2 * CORNER) * (i / 24), nr: 1, ny: 0 });
  }
  arc(ro - CORNER, h - CORNER, 0, Math.PI / 2, 8, faces.top);
  arc(R_IN + CORNER, h - CORNER, Math.PI / 2, Math.PI, 8, faces.top);
  for (let i = 0; i <= 24; i++) {
    faces.inner.push({ r: R_IN, y: h - CORNER - (WIDTH - 2 * CORNER) * (i / 24), nr: -1, ny: 0 });
  }
  arc(R_IN + CORNER, -h + CORNER, Math.PI, 1.5 * Math.PI, 8, faces.bottom);
  arc(ro - CORNER, -h + CORNER, 1.5 * Math.PI, 2 * Math.PI, 8, faces.bottom);
  return faces;
}

function revolve(points, segments, flipU, flipV = false) {
  const pos = [];
  const nor = [];
  const uv = [];
  const idx = [];
  for (let s = 0; s <= segments; s++) {
    const u = s / segments;
    const phi = u * Math.PI * 2;
    const c = Math.cos(phi);
    const sn = Math.sin(phi);
    points.forEach((p, i) => {
      pos.push(p.r * sn, p.y, p.r * c);
      nor.push(p.nr * sn, p.ny, p.nr * c);
      const v = i / (points.length - 1);
      uv.push(flipU ? 1 - u : u, flipV ? v : 1 - v);
    });
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

/* ---------- Artwork: colour, engraving depth and glow per face ---------- */
const MM = TEX_W / 202; // texels per millimetre around the band

function canvas(w = TEX_W, h = TEX_H) {
  const c = document.createElement('canvas');
  c.width = w;
  c.height = h;
  return c;
}

// Each design element is drawn three times: colour, bump (engraving), glow.
function drawText(ctx, text, xMm, heightMm, font, squeeze = 1, weight = 400) {
  ctx.save();
  ctx.font = `${weight} ${heightMm * MM}px ${font}`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.translate(xMm * MM, TEX_H / 2 + heightMm * MM * 0.04);
  ctx.scale(squeeze, 1);
  ctx.fillText(text, 0, 0);
  ctx.restore();
}

function tintedMask(mask, color) {
  const c = canvas(mask.width, mask.height);
  const x = c.getContext('2d');
  x.fillStyle = color;
  x.fillRect(0, 0, c.width, c.height);
  x.globalCompositeOperation = 'destination-in';
  // Masks are white on black: turn luminance into alpha.
  const m = canvas(mask.width, mask.height);
  const mx = m.getContext('2d');
  mx.drawImage(mask, 0, 0);
  const d = mx.getImageData(0, 0, m.width, m.height);
  for (let i = 0; i < d.data.length; i += 4) {
    d.data[i + 3] = d.data[i];
  }
  mx.putImageData(d, 0, 0);
  x.drawImage(m, 0, 0);
  return c;
}

function drawMask(ctx, mask, color, xMm, heightMm) {
  const h = heightMm * MM;
  const w = (mask.width / mask.height) * h;
  ctx.drawImage(tintedMask(mask, color), xMm * MM - w / 2, TEX_H / 2 - h / 2, w, h);
}

const DESIGNS = {
  gojo: {
    base: 'assets/tex/gojo_base.jpg',
    name: 'SATORU GOJO', nameColor: '#f4f2f6', nameGlow: null,
    icon: 'assets/tex/icon_gojo.png', iconColor: '#58d8ff', iconGlow: '#2fb8ff', iconAt: 36, iconH: 9.5,
    logoColor: '#58d8ff', logoGlow: '#2fb8ff', logoRed: null,
    quote: 'Throughout heaven and earth, I alone am honored', quoteColor: '#f1eff4', quoteH: 4.6,
    roughness: 0.55, sheen: 0.6, sheenColor: '#b48cff',
  },
  toji: {
    base: 'assets/tex/toji_base.jpg',
    name: "TOJI ZEN'IN", nameColor: '#121212', nameGlow: null,
    icon: 'assets/tex/icon_toji.png', iconColor: '#141414', iconGlow: null, iconAt: 34, iconH: 9.5,
    logoColor: '#141414', logoGlow: null, logoRed: '#a3101a',
    quote: 'A monkey like me, incapable of using occult energy, has just surpassed all the chosen ones',
    quoteColor: '#151515', quoteH: 4.2,
    roughness: 0.62, sheen: 0.35, sheenColor: '#ffffff',
  },
};

async function makeMaps(kind) {
  const d = DESIGNS[kind];
  const [base, icon, logo, logoRed, micro] = await Promise.all([
    loadImage(d.base), loadImage(d.icon), loadImage('assets/tex/logo_line.png'),
    loadImage('assets/tex/logo_red.png'), loadImage('assets/tex/micro.png'),
  ]);

  const outer = { color: canvas(), bump: canvas(), glow: canvas() };
  const inner = { color: canvas(), bump: canvas() };
  const nameFont = "'JJK'";

  for (const face of [outer, inner]) {
    const cx = face.color.getContext('2d');
    cx.drawImage(base, 0, 0, TEX_W, TEX_H);
    const bx = face.bump.getContext('2d');
    bx.fillStyle = '#bdbdbd';
    bx.fillRect(0, 0, TEX_W, TEX_H);
    // Fine matte grain of moulded silicone.
    bx.globalAlpha = 0.18;
    for (let x = 0; x < TEX_W; x += 1024) bx.drawImage(micro, x, 0, 1024, TEX_H);
    bx.globalAlpha = 1;
  }

  // Outer face.
  const oc = outer.color.getContext('2d');
  const ob = outer.bump.getContext('2d');
  const og = outer.glow.getContext('2d');
  og.fillStyle = '#000';
  og.fillRect(0, 0, TEX_W, TEX_H);
  const engrave = (drawFn) => {
    ob.save();
    // A soft shoulder, then a flat floor: reads as a debossed groove.
    ob.filter = 'blur(5px)';
    drawFn(ob, '#555555');
    ob.filter = 'blur(1.5px)';
    drawFn(ob, '#1e1e1e');
    ob.restore();
  };

  const name = (x, c) => {
    x.fillStyle = c;
    x.strokeStyle = c;
    x.lineWidth = 0.45 * MM;
    x.lineJoin = 'miter';
    drawText(x, d.name, 84, 7.4, nameFont);
    x.save();
    x.font = `400 ${7.4 * MM}px ${nameFont}`;
    x.textAlign = 'center';
    x.textBaseline = 'middle';
    x.strokeText(d.name, 84 * MM, TEX_H / 2 + 7.4 * MM * 0.04);
    x.restore();
  };
  name(oc, d.nameColor);
  engrave((x, c) => name(x, c));

  drawMask(oc, icon, d.iconColor, d.iconAt, d.iconH);
  engrave((x, c) => drawMask(x, icon, c, d.iconAt, d.iconH));
  if (d.iconGlow) {
    og.filter = 'blur(6px)';
    drawMask(og, icon, d.iconGlow, d.iconAt, d.iconH);
    og.filter = 'none';
    drawMask(og, icon, d.iconGlow, d.iconAt, d.iconH);
  }

  drawMask(oc, logo, d.logoColor, 140, 8.4);
  if (d.logoRed) drawMask(oc, logoRed, d.logoRed, 140, 8.4);
  engrave((x, c) => drawMask(x, logo, c, 140, 8.4));
  if (d.logoGlow) {
    og.filter = 'blur(6px)';
    drawMask(og, logo, d.logoGlow, 140, 8.4);
    og.filter = 'none';
    drawMask(og, logo, d.logoGlow, 140, 8.4);
  }

  // Inner face: the quote runs around the inside.
  const ic = inner.color.getContext('2d');
  const ib = inner.bump.getContext('2d');
  // Squeeze long quotes so they fit in 175 mm of the inside.
  ic.font = `500 ${d.quoteH * MM}px 'Poppins'`;
  const squeeze = Math.min(0.88, (175 * MM) / ic.measureText(d.quote).width);
  ic.fillStyle = d.quoteColor;
  drawText(ic, d.quote, 92, d.quoteH, "'Poppins'", squeeze, 500);
  ib.save();
  ib.filter = 'blur(4px)';
  ib.fillStyle = '#555555';
  drawText(ib, d.quote, 92, d.quoteH, "'Poppins'", squeeze, 500);
  ib.filter = 'blur(1.2px)';
  ib.fillStyle = '#1e1e1e';
  drawText(ib, d.quote, 92, d.quoteH, "'Poppins'", squeeze, 500);
  ib.restore();

  const tex = (c, srgb) => {
    const t = new THREE.CanvasTexture(c);
    t.colorSpace = srgb ? THREE.SRGBColorSpace : THREE.NoColorSpace;
    t.anisotropy = 8;
    t.wrapS = THREE.RepeatWrapping;
    return t;
  };
  return {
    outer: { map: tex(outer.color, true), bump: tex(outer.bump), glow: tex(outer.glow, true) },
    inner: { map: tex(inner.color, true), bump: tex(inner.bump) },
    rim: tex(outer.color, true),
    design: d,
  };
}

function material(d, maps) {
  const m = new THREE.MeshPhysicalMaterial({
    map: maps.map,
    bumpMap: maps.bump,
    bumpScale: 7,
    roughness: d.roughness,
    sheen: d.sheen,
    sheenRoughness: 0.75,
    sheenColor: new THREE.Color(d.sheenColor),
    clearcoat: 0.12,
    clearcoatRoughness: 0.55,
  });
  if (maps.glow) {
    m.emissiveMap = maps.glow;
    m.emissive = new THREE.Color('#ffffff');
    m.emissiveIntensity = 0.9;
  }
  return m;
}

export async function createBracelet(kind) {
  const maps = await makeMaps(kind);
  const faces = profile();
  const group = new THREE.Group();
  const SEG = 720;
  // The outer profile runs bottom to top, so V is flipped to keep the text upright.
  const outer = new THREE.Mesh(revolve(faces.outer, SEG, false, true), material(maps.design, maps.outer));
  const inner = new THREE.Mesh(revolve(faces.inner, SEG, true), material(maps.design, maps.inner));
  const rimMat = material(maps.design, { map: maps.rim, bump: maps.outer.bump });
  rimMat.bumpScale = 0.3;
  const top = new THREE.Mesh(revolve(faces.top, SEG, false), rimMat);
  const bottom = new THREE.Mesh(revolve(faces.bottom, SEG, false), rimMat);
  group.add(outer, inner, top, bottom);
  group.traverse((o) => { o.castShadow = true; o.receiveShadow = true; });
  return group;
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
  key.position.set(60, 120, 90);
  key.castShadow = true;
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
    rimA.color.set(shot.rimA);
    rimB.intensity = shot.rimB;
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
