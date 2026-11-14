import json
CSS="""*{margin:0;box-sizing:border-box}body{width:1080px;height:1350px;background:#0A0A0C;color:#F4EFE8;font-family:'Noto Sans CJK KR',sans-serif;position:relative;overflow:hidden}
.top{position:absolute;top:72px;left:84px;right:84px;display:flex;justify-content:space-between;font:700 24px 'Noto Sans CJK KR';letter-spacing:6px;color:#FF6A3D}
.top span:last-child{color:rgba(244,239,232,.55)}
.sub{position:absolute;top:128px;left:84px;font:500 24px 'Noto Sans CJK KR';letter-spacing:3px;color:rgba(244,239,232,.5)}
.wrap{position:absolute;left:84px;right:84px;top:230px}
h1{font:900 104px/1.18 'Noto Serif CJK KR';letter-spacing:-2px}
h2{font:900 66px/1.25 'Noto Serif CJK KR';letter-spacing:-1px;margin-bottom:46px}
em{font-style:normal;color:#FF6A3D}
p{font:400 34px/1.6 'Noto Sans CJK KR';color:rgba(244,239,232,.82)}
.row{border-top:1px solid rgba(244,239,232,.14);padding:30px 0 32px}
.ep{font:700 26px 'Noto Sans CJK KR';letter-spacing:4px;color:#FF6A3D;margin-bottom:10px}
.t{font:700 40px/1.4 'Noto Sans CJK KR'}
.s{font:400 30px/1.5 'Noto Sans CJK KR';color:rgba(244,239,232,.7);margin-top:6px}
.big{font:900 150px/1 'Noto Sans CJK KR';color:#FF6A3D;letter-spacing:-4px}
.foot{position:absolute;left:84px;right:84px;bottom:80px;font:500 30px 'Noto Sans CJK KR';color:rgba(244,239,232,.75);display:flex;justify-content:space-between}
.glow{position:absolute;width:900px;height:900px;border-radius:50%;background:radial-gradient(circle,rgba(255,106,61,.16),rgba(255,106,61,0) 65%);right:-320px;top:-300px}
.ridge{position:absolute;left:0;right:0;bottom:0;height:420px}
"""
RIDGE='<svg class=ridge viewBox="0 0 1080 420" preserveAspectRatio="none"><path d="M0 420 L0 300 L120 220 L210 270 L330 140 L420 210 L540 60 L640 190 L760 120 L860 230 L960 170 L1080 260 L1080 420Z" fill="rgba(244,239,232,.05)"/><path d="M0 420 L0 350 L160 290 L280 330 L420 250 L560 320 L700 260 L840 330 L1000 280 L1080 320 L1080 420Z" fill="rgba(244,239,232,.06)"/><circle cx="540" cy="60" r="7" fill="#FF6A3D"/></svg>'
def page(n,body,sub=""):
    return f"<!doctype html><meta charset=utf-8><style>{CSS}</style><body><div class=glow></div><div class=top><span>SEASON 1 · 정상 쟁탈전</span><span>{n} / 6</span></div><div class=sub>{sub}</div>{body}</body>"
P=[]
P.append(page(1,RIDGE+"""<div class=wrap style="top:300px"><div class=ep style="font-size:30px">WEEKLY CHRONICLE · WEEK 1</div><h1>주간<br><em>연대기</em></h1><p style="margin-top:44px">4화, 4개의 봉우리.<br>지난주 정상 쟁탈전을 한 장씩 정리했어요.</p></div>
<div class=foot><span>EP.14 – EP.17 · 11.12 – 11.15</span><span>넘겨보기 →</span></div>""","GYM BASECAMP 베이스캠프 통신"))
rows=[("EP.14 · HYROX","리복이 결승 테이프를 끊었다","71.6점 · 기록 48:24"),
("EP.15 · 격투기","베넘이 블랙컴뱃을 끌어내리고 왕좌에","1~3위가 단 1.2점 안"),
("EP.16 · 러닝","미즈노 정상, 인디 UVU는 거인들 사이 2위","76.4 · 75.4 · 75.1"),
("EP.17 · 파워리프팅","SBD 319.6kg로 수성","A7 307.6kg, 12kg 뒤에서 추격")]
P.append(page(2,'<div class=wrap style="top:210px"><h2>지난주 <em>줄거리</em></h2>'+"".join(f'<div class=row><div class=ep>{a}</div><div class=t>{b}</div><div class=s>{c}</div></div>' for a,b,c in rows)+'</div>',"회차별 한 줄"))
P.append(page(3,"""<div class=wrap style="top:210px"><h2>왕좌 <em>교체</em> 2곳</h2>
<div class=row><div class=ep>격투기 · 11.12</div><div class=t>BLACK COMBAT → <em>VENUM</em></div><div class=s>베넘 74.3 · 블랙컴뱃 73.2 · 요카오 73.1</div></div>
<div class=row><div class=ep>컴프레션·기능성 · 11.12</div><div class=t>VOLANTE → <em>CW-X</em></div><div class=s>CW-X 81.3 · 볼란테 81.1 — 단 0.2점 차</div></div>
<p style="margin-top:40px;font-size:30px">두 봉우리 모두 1·2위 차이가 1.1점 이하.<br>정상이 가장 흔들리는 곳이에요.</p></div>""","정상이 바뀐 봉우리"))
P.append(page(4,"""<div class=wrap style="top:210px"><h2>이번 주 <em>급상승</em></h2><div class=ep style="font-size:30px">러닝 · UVU</div>
<div class=big>+13.0</div><p style="margin-top:30px">11.11 62.4점 → 11.13 75.4점<br>사흘 만에 러닝 2위, 정상 미즈노와 <em>1.0점</em> 차.</p>
<p style="margin-top:28px;font-size:28px;color:rgba(244,239,232,.6)">2017년 런던 러닝 클럽에서 시작한 브랜드.<br>11.12 한국 공식 스토어·원화 가격이 확인돼<br>국내 구매·정보 점수가 올랐어요.</p></div>""","어디서 나타났나"))
pts=[("① 격투기 삼파전","베넘·블랙컴뱃·요카오, 1.2점 안. 베넘은 왕좌를 지킬까?"),
("② 러닝 1.0점","미즈노 76.4 vs UVU 75.4. 인디가 거인을 넘을까?"),
("③ 컴프레션 0.2점","CW-X 81.3 vs 볼란테 81.1. 다시 뒤집힐까?")]
P.append(page(5,'<div class=wrap style="top:210px"><h2>이번 주 <em>관전 포인트</em></h2>'+"".join(f'<div class=row><div class=t><em>{a}</em></div><div class=s style="font-size:32px;color:rgba(244,239,232,.85)">{b}</div></div>' for a,b in pts)+'<p style="margin-top:36px;font-size:28px;color:rgba(244,239,232,.6)">오늘 밤 EP.18 HYROX · 화요일 EP.19 격투기</p></div>',"11.14 집계 기준"))
P.append(page(6,RIDGE+"""<div class=wrap style="top:300px"><h1 style="font-size:96px">이번 주 예측,<br><em>댓글로</em></h1><p style="margin-top:44px">이번 주 왕좌가 바뀔 봉우리는?<br>격투기 · 러닝 · 컴프레션 중 하나 골라 주세요.</p>
<p style="margin-top:44px;font:700 44px 'Noto Sans CJK KR';color:#FF6A3D">gymbasecamp.kr</p><p style="font-size:26px;color:rgba(244,239,232,.55)">9개 종목 · 100점 순위 · 광고 아님 · 순위에 광고 안 섞음</p></div>""","다음 주 연대기에서 채점합니다"))
for i,h in enumerate(P,1): open(f's{i}.html','w').write(h)
