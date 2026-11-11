// usage: node sr.js in.raw W H out.raw   (raw = uint8 RGB)
const fs = require('fs'), path = require('path');
const tf = require('@tensorflow/tfjs');
require('@tensorflow/tfjs-backend-wasm');
const [,, inp, W, H, out] = process.argv; const w = +W, h = +H, S = 4, T = 128, O = 12;
(async () => {
  await tf.setBackend('wasm'); await tf.ready();
  const dir = path.join(process.env.SR_MODULES || path.join(__dirname, 'node_modules'), '@upscalerjs/esrgan-medium/models/x4');
  const mj = JSON.parse(fs.readFileSync(path.join(dir, 'model.json')));
  const wb = fs.readFileSync(path.join(dir, mj.weightsManifest[0].paths[0]));
  const model = await tf.loadLayersModel(tf.io.fromMemory({ modelTopology: mj.modelTopology,
    weightSpecs: mj.weightsManifest[0].weights, weightData: wb.buffer.slice(wb.byteOffset, wb.byteOffset + wb.length) }));
  const src = new Uint8Array(fs.readFileSync(inp)); const dst = new Uint8Array(w * S * h * S * 3);
  const img = tf.tensor3d(src, [h, w, 3], 'int32').toFloat();
  const t0 = Date.now(); let n = 0;
  for (let y = 0; y < h; y += T) for (let x = 0; x < w; x += T) {
    const x0 = Math.max(0, x - O), y0 = Math.max(0, y - O);
    const x1 = Math.min(w, x + T + O), y1 = Math.min(h, y + T + O);
    const r = tf.tidy(() => model.predict(img.slice([y0, x0, 0], [y1 - y0, x1 - x0, 3]).expandDims(0)).squeeze().clipByValue(0, 255).round().toInt());
    const d = r.dataSync(); r.dispose(); const rw = (x1 - x0) * S;
    const cx0 = (x - x0) * S, cy0 = (y - y0) * S, cw = (Math.min(w, x + T) - x) * S, ch = (Math.min(h, y + T) - y) * S;
    for (let j = 0; j < ch; j++) for (let i = 0; i < cw; i++) {
      const s = ((cy0 + j) * rw + cx0 + i) * 3, t = ((y * S + j) * w * S + x * S + i) * 3;
      dst[t] = d[s]; dst[t + 1] = d[s + 1]; dst[t + 2] = d[s + 2];
    }
    n++;
  }
  fs.writeFileSync(out, dst); console.log('tiles', n, 'sec', (Date.now() - t0) / 1000);
})();
