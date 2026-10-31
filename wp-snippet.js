/* GYM BASECAMP v2 - loads the latest site from GitHub (gymbasecamp/gymbasecamp-site) */
(function(){
var me=document.currentScript;
var m=document.createElement('div');m.id='gb-root';m.style.minHeight='100vh';m.style.background='#111111';
if(me){me.before(m);}else{document.body.prepend(m);}
var R='gymbasecamp/gymbasecamp-site';
function load(ref){
  var s=document.createElement('sc'+'ript');
  s.src='https://cdn.jsdelivr.net/gh/'+R+'@'+ref+'/dist/gb.js';
  s.async=true;
  if(ref!=='main'){s.addEventListener('error',function(){load('main');});}
  document.head.appendChild(s);
}
fetch('https://api.github.com/repos/'+R+'/commits/main',{headers:{Accept:'application/vnd.github.sha'}})
  .then(function(r){return r.ok?r.text():Promise.reject();})
  .then(function(t){t=t.trim();load(/^[0-9a-f]{40}$/.test(t)?t:'main');})
  .catch(function(){load('main');});
})();
