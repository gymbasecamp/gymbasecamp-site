// 시리즈 오버레이 — 모든 대회형 릴스에 '지난 화'와 '다음 화 예고'를 얹는다.
// rec.js가 STORY=<json> 환경변수가 있으면 페이지에 주입. json: {"season":"시즌 1 · 정상 쟁탈전","ep":15,"prev":"지난 화 한 줄","next":"다음 화 예고 한 줄","ask":"댓글 질문"}
window.__story=function(S){
  const base=window.frame, TOT=window.TOT, c=document.getElementById('c'), x=c.getContext('2d'), PT='#FF6A3D', IV='#F4EFE8';
  const cl=(v,a,b)=>Math.max(a,Math.min(b,v)), e=t=>1-Math.pow(1-cl(t,0,1),3);
  function wrap(t,f,maxW){ x.font=f; const out=[]; let line=''; for(const w of t.split(' ')){ const tr=line?line+' '+w:w; if(x.measureText(tr).width>maxW&&line){ out.push(line); line=w; } else line=tr; } if(line) out.push(line); return out; }
  window.frame=function(t){ base(t); x.save(); x.setTransform(1,0,0,1,0,0); x.filter='none'; x.letterSpacing='0px';
    // 시즌 표기(항상, 우상단)
    x.globalAlpha=.85; x.font="600 22px 'Inter Display','Noto Sans CJK KR'"; x.textAlign='right'; x.fillStyle='rgba(244,239,232,.7)'; x.fillText(S.season,W0-70,200); x.globalAlpha=1;
    // 지난 화 (0~1.9초)
    if(S.prev&&t<1.9){ const a=Math.min(e(t/.25),e((1.9-t)/.3)); x.globalAlpha=a; const f="600 30px 'Noto Sans CJK KR'"; const L=wrap(S.prev,f,W0-200);
      const h=58+L.length*42; x.fillStyle='rgba(10,10,12,.86)'; x.beginPath(); x.roundRect(60,1000,W0-120,h,8); x.fill(); x.fillStyle=PT; x.fillRect(60,1000,8,h);
      x.textAlign='left'; x.font="700 22px 'Inter Display'"; x.letterSpacing='6px'; x.fillStyle=PT; x.fillText("지난 화",96,1042); x.letterSpacing='0px'; x.font=f; x.fillStyle=IV; L.forEach((l,i)=>x.fillText(l,96,1086+i*42)); }
    // 다음 화 예고 (마지막 2.8초)
    const s0=TOT-2.8; if(S.next&&t>s0){ const a=e((t-s0)/.35); x.globalAlpha=a; const f="700 40px 'Noto Serif CJK KR'"; const L=wrap(S.next,f,W0-200); const h=96+L.length*56+(S.ask?56:0);
      const y=1240-h/2; x.fillStyle='rgba(10,10,12,.9)'; x.beginPath(); x.roundRect(60,y,W0-120,h,8); x.fill(); x.strokeStyle=PT; x.lineWidth=2; x.stroke();
      x.textAlign='center'; x.font="700 24px 'Inter Display'"; x.letterSpacing='8px'; x.fillStyle=PT; x.fillText('NEXT · EP.'+(S.ep+1),W0/2,y+48); x.letterSpacing='0px';
      x.font=f; x.fillStyle=IV; L.forEach((l,i)=>x.fillText(l,W0/2,y+104+i*56)); if(S.ask){ x.font="500 30px 'Noto Sans CJK KR'"; x.fillStyle='#ddd3c9'; x.fillText('💬 '+S.ask,W0/2,y+104+L.length*56+14); } }
    x.restore(); };
  const W0=c.width;
};
