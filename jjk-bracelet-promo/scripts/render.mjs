// Render index.html frame by frame and encode it to MP4 with the music.
// Usage: node scripts/render.mjs [--fps 30] [--from 0] [--to <seconds>] [--out out/promo.mp4] [--music <file>] [--stills 1,6.5,...]
import { spawn } from 'node:child_process';
import { createReadStream, existsSync, mkdirSync, statSync, writeFileSync } from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright-core';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const args = Object.fromEntries(process.argv.slice(2).reduce((acc, a, i, all) => {
  if (a.startsWith('--')) acc.push([a.slice(2), all[i + 1]]);
  return acc;
}, []));
const fps = Number(args.fps ?? 30);
const out = path.resolve(root, args.out ?? 'out/promo.mp4');
const music = args.music ? path.resolve(args.music) : null;
const chrome = process.env.CHROME_PATH ?? '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';

const types = { '.html': 'text/html', '.js': 'text/javascript', '.png': 'image/png', '.jpg': 'image/jpeg',
  '.webp': 'image/webp', '.ttf': 'font/ttf' };
const server = http.createServer((req, res) => {
  const file = path.join(root, decodeURIComponent(new URL(req.url, 'http://x').pathname));
  if (!file.startsWith(root) || !existsSync(file) || statSync(file).isDirectory()) {
    res.writeHead(404).end();
    return;
  }
  res.writeHead(200, { 'content-type': types[path.extname(file)] ?? 'application/octet-stream' });
  createReadStream(file).pipe(res);
}).listen(0, '127.0.0.1');
await new Promise((r) => server.once('listening', r));
const url = `http://127.0.0.1:${server.address().port}/index.html`;

const browser = await chromium.launch({ executablePath: chrome });
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
page.on('pageerror', (e) => console.error('page error:', e.message));
await page.goto(url);
await page.evaluate(() => window.__ready);
const duration = await page.evaluate(() => window.DURATION);

mkdirSync(path.dirname(out), { recursive: true });

if (args.stills) {
  for (const t of args.stills.split(',').map(Number)) {
    await page.evaluate((s) => window.__seek(s), t);
    const file = path.join(path.dirname(out), `still_${t.toFixed(2)}.jpg`);
    writeFileSync(file, await page.screenshot({ type: 'jpeg', quality: 85 }));
    console.log(file);
  }
} else {
  const from = Number(args.from ?? 0);
  const to = Number(args.to ?? duration);
  const ffArgs = ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-'];
  if (music) {
    // Music starts at 0:00 and fades out over the last 2 s.
    ffArgs.push('-ss', String(from), '-t', String(to - from), '-i', music,
      '-af', `loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=out:st=${Math.max(0, to - from - 2)}:d=2`, '-c:a', 'aac', '-b:a', '192k', '-shortest');
  }
  ffArgs.push('-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out);
  const ff = spawn('ffmpeg', ffArgs, { stdio: ['pipe', 'inherit', 'inherit'] });
  const total = Math.round((to - from) * fps);
  for (let i = 0; i < total; i++) {
    await page.evaluate((s) => window.__seek(s), from + i / fps);
    const buf = await page.screenshot({ type: 'jpeg', quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
    if (i % 60 === 0) console.log(`frame ${i}/${total}`);
  }
  ff.stdin.end();
  await new Promise((r) => ff.on('close', r));
  console.log('wrote', out);
}

await browser.close();
server.close();
