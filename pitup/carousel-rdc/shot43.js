const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1440,height:1080},deviceScaleFactor:Number(process.env.DSF||1)});
await p.goto('file://'+process.argv[2]);await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(600);
const n=await p.$$eval('section.s',e=>e.length);
for(let i=0;i<n;i++){const el=await p.$('#s'+i);await el.screenshot({path:process.argv[3]+`/PitUp-carrousel-RDC-${String(i+1).padStart(2,'0')}.png`});}
await b.close();})();
