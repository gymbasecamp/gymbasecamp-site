# BASECAMP RANK — 릴스·틱톡 시리즈

모든 영상에 같은 브랜드 장치를 넣어 "아, 그 계정" 하고 기억되게 만든다.

| 고정 요소 | 내용 |
|---|---|
| 시리즈 태그 | 좌상단 빨간 박스 `BASECAMP RANK EP.NN` (회차 번호가 쌓임) |
| 시그니처 문구 | 하단 고정 `운동복, 감 말고 점수로.` + 엔딩 첫 줄 |
| 왼쪽 빨간 세로 바 | 모든 프레임 왼쪽 18px 빨간 띠 — 피드에서 썸네일만 봐도 구분 |
| 순위 스탬프 | 순위/카테고리를 화면 가득 빨간 글자로 '쾅' 줌인 + 저음 '쿵' 사운드 |
| 엔딩 카드 | "운동복 사기 전, 들르는 곳" → 로고 → "운동복, 감 말고 점수로." → 핵심 4가지 체크(브랜드 수·점수·안 팔고 공식몰로·광고 안 섞음) → gymbasecamp.kr |
| 색 | 검정 #0E0E0E · 빨강 #E0392F · 흰 #F2F1EE |
| 안전영역 | 위 200px · 아래 520px · 오른쪽 150px 비움 (인스타·틱톡 UI) |

## 만드는 법
```
node reels/make_reel.js reels/episodes/ep02.json /tmp/ep02
sh reels/render.sh /tmp/ep02     # → /tmp/ep02/final.mp4 (1080×1920, 30fps, 시그니처 사운드 포함)
```
에피소드 JSON: `ep, date, hook(HTML, <span class="red">강조</span>), sub, items[{r 또는 big/bigSub, en, ko, ig, s, p, price, buy}], cta`.
숫자·가격은 site/data/brands.json 과 rank_history.json 값만 쓴다(지어내지 않음).
