const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1350},deviceScaleFactor:2});
await p.goto('file://'+process.argv[2]);await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(600);
for(let i=0;i<7;i++){const el=await p.$('#s'+i);await el.screenshot({path:process.argv[3]+`/PitUp-carrousel-${String(i).padStart(2,'0')}.png`});}
await b.close();})();
