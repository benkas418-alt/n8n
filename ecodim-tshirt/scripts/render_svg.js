// usage: node render_svg.js in.svg out.png widthPx   (transparent background, Chromium)
const { chromium } = require('playwright'); const fs = require('fs');
(async () => {
  const [,, inp, out, w] = process.argv; const svg = fs.readFileSync(inp, 'utf8');
  const vb = svg.match(/viewBox="([\d.\s-]+)"/)[1].trim().split(/\s+/).map(Number);
  const W = +w, H = Math.round(W * vb[3] / vb[2]);
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: W, height: H } });
  const s = svg.replace(/<svg([^>]*?)\swidth="[^"]*"/, '<svg$1').replace(/<svg([^>]*?)\sheight="[^"]*"/, '<svg$1')
               .replace('<svg ', `<svg width="${W}" height="${H}" `);
  await p.setContent(`<html><body style="margin:0;background:transparent">${s}</body></html>`);
  await p.screenshot({ path: out, omitBackground: true, clip: { x: 0, y: 0, width: W, height: H } });
  await b.close();
})();
