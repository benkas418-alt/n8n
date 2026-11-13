// Quick stills of a HyperFrames page at given times (seeks the GSAP timeline). usage: node frames.cjs page.html out_prefix t1 t2 ...
const {chromium}=require('playwright');(async()=>{const [page,pre,...ts]=process.argv.slice(2);const b=await chromium.launch();
const p=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:0.5});await p.goto('file://'+page);
await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(800);
for(const t of ts){await p.evaluate(x=>{const tl=window.__timelines.main;tl.seek(+x);},t);await p.waitForTimeout(150);await p.screenshot({path:`${pre}_${t}.png`});}
await b.close();})();
