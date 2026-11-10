// GYM BASECAMP ranking v2 — 100 points, objective, ties broken deterministically.
const RANK_V2 = (function(){
  const ITEMS=['슬리브리스/탱크','쇼츠','팬츠/조거','레깅스','스포츠브라','아우터','펌프커버/헤비웨이트','스트렝스/싱글렛','러닝/HYROX/크로스트레이닝'];
  const FITS=['머슬핏','오버핏','컴프레션'];
  const GYMF=['머슬핏','컴프레션','슬리브리스/탱크','펌프커버/헤비웨이트','스트렝스/싱글렛'];
  const TYPE_BASE={'짐웨어 전문':15,'스트렝스 스포츠':15,'짐 스트리트':14,'퍼포먼스 트레이닝':11,'애슬레저':8,'종합 스포츠':8};
  const BUY={'국내 공식몰':20,'국내 판매처':17,'해외 직배송':13,'해외 직구/확인 필요':7};
  const r1=x=>Math.round(x*10)/10;
  // 종목별 기준: kw=그 종목을 위한 브랜드인지(핵심 운동·성향·스타일), it=그 종목 필수 아이템 5개
  const CAT={
   '헬스·보디빌딩':{kw:/보디빌딩|웨이트|헬스|머슬/,it:['머슬핏','컴프레션','슬리브리스/탱크','펌프커버/헤비웨이트','스트렝스/싱글렛']},
   '스트렝스·파워리프팅':{kw:/파워|리프팅|스트렝스|역도/,it:['스트렝스/싱글렛','펌프커버/헤비웨이트','쇼츠','슬리브리스/탱크','오버핏']},
   '크로스핏':{kw:/크로스핏|펑셔널|WOD/i,it:['러닝/HYROX/크로스트레이닝','쇼츠','컴프레션','스포츠브라','슬리브리스/탱크']},
   'HYROX':{kw:/HYROX|하이록스|하이브리드/i,it:['러닝/HYROX/크로스트레이닝','쇼츠','컴프레션','스포츠브라','레깅스']},
   '요가·필라테스·레깅스':{kw:/요가|필라테스|레깅스|애슬레저/,it:['레깅스','스포츠브라','여성','팬츠/조거','아우터']},
   '러닝':{kw:/러닝|마라톤|트레일/,it:['러닝/HYROX/크로스트레이닝','쇼츠','레깅스','슬리브리스/탱크','아우터']},
   '격투기':{kw:/격투|복싱|MMA|주짓수|무에타이/i,it:['쇼츠','컴프레션','슬리브리스/탱크','팬츠/조거','아우터']},
   '컴프레션·기능성':{kw:/컴프레션|기능성/,it:['컴프레션','레깅스','쇼츠','스포츠브라','러닝/HYROX/크로스트레이닝']},
   '종합 스포츠':{kw:/종합|트레이닝/,it:['쇼츠','팬츠/조거','레깅스','스포츠브라','아우터']}};
  // 대표 종목이면 15, '겸'으로 들어온 종목이면 9 (+ 그 종목 전용 브랜드 5 + 필수 아이템 최대 5)
  function focusFor(b,c){ const m=CAT[c]||CAT['종합 스포츠']; const f=b.f||[]; const base=b.cat===c?15:9; const txt=[b.sport,b.vibe,b.style].join(' ');
    return base+(m.kw.test(txt)?5:0)+m.it.filter(k=>f.includes(k)).length; }
  function parts(b, react){
    const f=b.f||[];
    // 1. 종목 특화도 25 (2026-11-11 지훈 승인: 카테고리마다 그 종목 기준으로 채점) — 대표 카테고리 기준
    const focus=focusFor(b,b.cat);
    // 2. 제품 구성 20
    const items=ITEMS.filter(k=>f.includes(k)).length/ITEMS.length*11;
    const fits=FITS.filter(k=>f.includes(k)).length*2;
    const gender=(f.includes('남성')&&f.includes('여성'))?3:((f.includes('남성')||f.includes('여성'))?1.5:0);
    const range=items+fits+gender;
    // 3. 국내 구매 편의 20
    const access=BUY[b.buy]||7;
    // 4. 정보 신뢰도 10
    let info=0; if(b.url) info+=3;
    if(/\d/.test(b.price)&&!/상품별 상이|추가 확인/.test(b.price)) info+=3;
    if(b.items&&!/추가 확인/.test(b.items)) info+=2;
    if(b.ig&&b.ig!=='확인 필요') info+=2;
    // 5. 에디터 평가 5 (기존 20점 평가 반영)
    const editor=(b.score||0)/20*5;
    // 6. 사용자 반응 20 (데이터 부족 시 모두 10 = 중립)
    const user = react && react.ready && react.by ? react.by[b.id] ?? 0 : 10;
    const p={focus:r1(focus),range:r1(range),access:r1(access),info:r1(info),editor:r1(editor),user:r1(user)};
    p.total=r1(p.focus+p.range+p.access+p.info+p.editor+p.user);
    return p;
  }
  // react = {ready:bool, by:{id:0..20}, clicks:{id:n}} ; compute from raw counts with smoothing
  function reactFromCounts(counts){
    // counts: {id:{view:n, official:n, compare:n, quiz:n}}
    const ids=Object.keys(counts||{}); const tot=ids.reduce((s,i)=>s+(counts[i].view||0),0);
    if(tot<200) return {ready:false,by:{},clicks:{}};
    const raw={}; let max=0;
    ids.forEach(i=>{const c=counts[i]; const v=(c.official||0)*3+(c.view||0)+(c.compare||0)*2+(c.quiz||0)*2; raw[i]=v; if(v>max) max=v;});
    const by={}; ids.forEach(i=>by[i]=max? (Math.sqrt(raw[i])/Math.sqrt(max))*20 :0);
    const clicks={}; ids.forEach(i=>clicks[i]=counts[i].official||0);
    return {ready:true,by,clicks};
  }
  function rank(brands, react){
    const rows=brands.map(b=>({b,p:parts(b,react)}));
    rows.sort((x,y)=>y.p.total-x.p.total||y.p.user-x.p.user||y.p.focus-x.p.focus||y.p.info-x.p.info||((react&&react.clicks&&(react.clicks[y.b.id]||0))-(react&&react.clicks&&(react.clicks[x.b.id]||0)))||x.b.en.localeCompare(y.b.en));
    rows.forEach((r,i)=>{r.b.v2=r.p; r.b.rank2=i+1;});
    const tc={}; rows.forEach(r=>{const k=r.b.cat||r.b.type||''; tc[k]=(tc[k]||0)+1; r.b.rankT=tc[k];});
    // 종목별 점수: 같은 브랜드라도 종목마다 그 종목 기준의 특화도로 다시 계산 (겸 카테고리 포함)
    const byC={}; rows.forEach(r=>{r.b.rk={}; r.b.rs={}; r.b.fc={}; (r.b.cats||[r.b.cat]).forEach(c=>{const fo=focusFor(r.b,c); r.b.fc[c]=fo; const s=c===r.b.cat?r.p.total:r1(r.p.total-r.p.focus+fo); r.b.rs[c]=s; (byC[c]=byC[c]||[]).push(r);});});
    Object.keys(byC).forEach(c=>byC[c].sort((x,y)=>y.b.rs[c]-x.b.rs[c]||x.b.rank2-y.b.rank2).forEach((r,i)=>r.b.rk[c]=i+1));
    return rows;
  }
  return {parts,rank,reactFromCounts,focusFor};
})();
if(typeof module!=='undefined') module.exports=RANK_V2;
