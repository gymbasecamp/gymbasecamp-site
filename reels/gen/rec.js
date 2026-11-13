const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const br=await chromium.launch();const p=await br.newPage({viewport:{width:1080,height:1920}});p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto('file://'+__dirname+'/'+(process.env.PAGE||'page.html'),{timeout:180000});await p.waitForTimeout(600);
if(process.env.STORY){await p.addScriptTag({path:__dirname+'/story.js'});await p.evaluate(S=>window.__story(S),JSON.parse(fs.readFileSync(process.env.STORY,'utf8')));}
const only=process.argv[2]; fs.mkdirSync((process.env.OUT||'f'),{recursive:true});const TOT=await p.evaluate(()=>TOT);
const ts=only?only.split(',').map(Number):[...Array(Math.round(TOT*30)).keys()].map(i=>i/30);
for(let i=+(process.env.START||0);i<Math.min(+(process.env.STOP||ts.length),ts.length);i++){const u=await p.evaluate(t=>{frame(t);return document.getElementById('c').toDataURL('image/jpeg',.9)},ts[i]);fs.writeFileSync(`${process.env.OUT||'f'}/${only?'k':'f'}${String(i).padStart(4,'0')}.jpg`,Buffer.from(u.split(',')[1],'base64'));}
console.log('TOT',TOT);await br.close();})();
