// GYM BASECAMP 릴스·틱톡 생성기 — 시리즈 "BASECAMP RANK"
// 사용: node reels/make_reel.js reels/episodes/ep01.json <출력폴더>
// 브랜드 고정 요소(모든 영상 동일): 
//  ① 좌상단 빨간 태그 "BASECAMP RANK EP.NN"  ② 상단 로고 워터마크
//  ③ 시그니처 문구 "운동복, 감 말고 점수로."  ④ 순위 공개 때 빨간 스탬프 + '쿵' 사운드
//  ⑤ 같은 엔딩 카드(로고 스탬프 + gymbasecamp.kr)
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const ep=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));const OUT=process.argv[3];fs.mkdirSync(OUT+'/png',{recursive:true});
const logo='data:image/png;base64,'+fs.readFileSync(path.join(__dirname,'logo.png')).toString('base64');
const RED='#E0392F';
// 틱톡/인스타 안전영역: 위 200px, 아래 520px, 오른쪽 150px는 UI에 가려짐 → 글자는 x 80~930, y 200~1400
const css=`*{margin:0;box-sizing:border-box}body{width:1080px;height:1920px;background:#0E0E0E;color:#F2F1EE;font-family:'Inter Display','Noto Sans CJK KR',sans-serif;overflow:hidden;position:relative}
.ko{font-family:'Noto Sans CJK KR'}.red{color:${RED}}
.bar{position:absolute;left:0;top:0;bottom:0;width:18px;background:${RED}}
.top{position:absolute;top:210px;left:80px;right:150px;display:flex;justify-content:space-between;align-items:center}
.tag{background:${RED};color:#fff;font:800 30px 'Inter Display';letter-spacing:.06em;padding:10px 18px}
.top img{height:28px;opacity:.9}
.sig{position:absolute;bottom:520px;left:80px;right:150px;border-top:2px solid #2c2c2a;padding-top:22px;display:flex;justify-content:space-between;font:600 28px 'Noto Sans CJK KR';color:#8a8984}
.sig b{color:#F2F1EE;font-weight:800}`;
const page=b=>`<html><head><style>${css}</style></head><body><div class="bar"></div>${b}</body></html>`;
const tag=`BASECAMP RANK EP.${String(ep.ep).padStart(2,'0')}`;
const head=`<div class="top"><span class="tag">${tag}</span><img src="${logo}"></div>`;
const sig=`<div class="sig"><span><b>운동복, 감 말고 점수로.</b></span><span>${ep.date} · 광고 아님</span></div>`;
const S={};
S.hook=page(`${head}<div style="position:absolute;top:400px;left:80px;right:150px">
<div class="ko" style="font-weight:900;font-size:${ep.hookSize||104}px;line-height:1.14;letter-spacing:-.03em">${ep.hook}</div>
<div class="ko" style="margin-top:50px;font-weight:500;font-size:40px;color:#A2A19C;line-height:1.5">${ep.sub}</div></div>${sig}`);
ep.items.forEach((b,i)=>{
 const big=b.big??String(b.r);
 if(b.type==='point'){
  S['n'+i]=page(`${head}<div style="position:absolute;top:200px;bottom:520px;left:80px;right:150px;display:flex;flex-direction:column;align-items:center;justify-content:center"><div class="red" style="font-weight:900;font-size:380px;line-height:1;letter-spacing:-.04em">${big}</div></div>${sig}`);
  S['b'+i]=page(`${head}<div style="position:absolute;top:360px;left:80px;right:150px">
  <div class="red" style="font-weight:900;font-size:120px;line-height:1">${big}</div>
  <div class="ko" style="margin-top:40px;font-weight:900;font-size:${b.size||92}px;line-height:1.15;letter-spacing:-.03em">${b.title}</div>
  <div class="ko" style="margin-top:44px;font-weight:500;font-size:42px;line-height:1.6;color:#C9C8C3">${b.body}</div></div>${sig}`);
  return;
 }
 S['n'+i]=page(`${head}<div style="position:absolute;top:200px;bottom:520px;left:80px;right:150px;display:flex;flex-direction:column;align-items:center;justify-content:center">
  <div class="red" style="font-weight:900;font-size:${big.length>2?(big.length>5?120:170):460}px;line-height:1;letter-spacing:-.04em;text-align:center" class="ko">${big}</div>
  <div class="ko" style="font-weight:800;font-size:64px;color:#A2A19C;margin-top:14px">${b.bigSub||'위'}</div></div>${sig}`);
 const w=Math.max(4,Math.round((b.s-40)/50*100));
 const nm=b.en.length>12?96:b.en.length>9?118:146;
 S['b'+i]=page(`${head}<div style="position:absolute;top:330px;left:80px;right:150px">
 <div style="display:flex;align-items:baseline;gap:18px"><span class="red ko" style="font-weight:900;font-size:${big.length>2?72:170}px;line-height:.95;letter-spacing:-.03em">${big}</span><span class="ko" style="font-weight:800;font-size:42px;color:#A2A19C">${b.bigSub||'위'}</span></div>
 <div style="margin-top:40px;font-weight:900;font-size:${nm}px;line-height:.95;letter-spacing:-.03em">${b.en}</div>
 <div class="ko" style="margin-top:20px;font-weight:700;font-size:48px;color:#D6D5D0">${b.ko}${b.ig?` <span style="font-weight:500;font-size:32px;color:#7a7975;margin-left:8px">${b.ig}</span>`:''}</div>
 <div style="margin-top:46px;display:flex;align-items:baseline;gap:12px"><span style="font-weight:900;font-size:100px">${b.s}</span><span style="font-weight:600;font-size:36px;color:#A2A19C">/ 100</span></div>
 <div style="margin-top:14px;height:12px;background:#2c2c2a"><div style="height:12px;width:${w}%;background:${RED}"></div></div>
 <div class="ko" style="margin-top:40px;font-size:38px;line-height:1.7;color:#D6D5D0">
 <div><span style="color:#7a7975;display:inline-block;width:130px">대표</span>${b.p}</div>
 <div><span style="color:#7a7975;display:inline-block;width:130px">가격</span>${b.price}</div>
 <div><span style="color:#7a7975;display:inline-block;width:130px">구매</span>${b.buy}</div></div></div>${sig}`);
});
S.end=page(`<div style="position:absolute;top:330px;left:80px;right:150px">
<div class="ko" style="font-weight:800;font-size:44px;color:#A2A19C">운동복 사기 전, 들르는 곳</div>
<img src="${logo}" style="width:850px;margin-top:34px">
<div class="ko" style="margin-top:56px;font-weight:900;font-size:64px;line-height:1.25;letter-spacing:-.03em">${ep.cta}</div>
<div class="ko" style="margin-top:46px;font-size:40px;line-height:1.85;color:#D6D5D0">
<div><span class="red" style="font-weight:900">✓</span> 국내·해외 운동복 <b style="color:#fff">${ep.total||96}개 브랜드</b> 한곳에</div>
<div><span class="red" style="font-weight:900">✓</span> 감 말고 <b style="color:#fff">100점 점수</b>로 종목별 순위</div>
<div><span class="red" style="font-weight:900">✓</span> 우리는 안 팔아요 → <b style="color:#fff">공식몰로 바로</b></div>
<div><span class="red" style="font-weight:900">✓</span> 광고는 <b style="color:#fff">순위에 절대 안 섞음</b></div></div>
<div style="margin-top:56px;display:inline-block;background:${RED};color:#fff;padding:22px 44px;font-weight:800;font-size:48px">gymbasecamp.kr</div>
<div class="ko" style="margin-top:22px;font-weight:600;font-size:34px;color:#A2A19C">프로필 링크 · 다음 편은 팔로우하고 보기</div></div>`);
(async()=>{const br=await chromium.launch();const pg=await br.newPage({viewport:{width:1080,height:1920}});
for(const [k,h] of Object.entries(S)){await pg.setContent(h);await pg.waitForTimeout(120);await pg.screenshot({path:`${OUT}/png/${k}.png`});}
await br.close();fs.writeFileSync(OUT+'/n.txt',String(ep.items.length));console.log('frames',Object.keys(S).length)})();
