const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const br=await chromium.launch();const p=await br.newPage({viewport:{width:1080,height:1920}});p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto('file://'+process.env.GEN+'/'+process.env.PAGE);await p.waitForTimeout(600);
if(process.env.STORY){await p.addScriptTag({path:process.env.GEN+'/story.js'});await p.evaluate(S=>window.__story(S),JSON.parse(fs.readFileSync(process.env.STORY,'utf8')));}
await p.evaluate(()=>window.SAFE=true);
console.log('TOT',await p.evaluate(()=>TOT),'CUES',await p.evaluate(()=>window.CUES));
const ts=process.argv[2].split(',').map(Number);let t0=Date.now();
for(const t of ts){const u=await p.evaluate(t=>{frame(t);return document.getElementById('c').toDataURL('image/jpeg',.85)},t);fs.writeFileSync(`${process.env.OUT}/k${t.toFixed(2)}.jpg`,Buffer.from(u.split(',')[1],'base64'));}
console.log('ms/frame',(Date.now()-t0)/ts.length);await br.close();})();
