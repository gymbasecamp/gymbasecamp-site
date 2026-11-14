const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1350}});
for(let i=1;i<=6;i++){await p.goto('file://'+__dirname+'/s'+i+'.html');await p.waitForTimeout(300);await p.screenshot({path:__dirname+'/s'+i+'.jpg',type:'jpeg',quality:92});}await b.close();})();
