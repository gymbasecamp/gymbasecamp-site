# 대회형 릴스 생성기 (2026-11-12~)
브랜드를 선수처럼 표현해 종목별 대회로 5위→1위를 보여준다. 각 html 맨 위 `const D=` 를 그날 순위로 바꾸고, 같은 폴더의 music 스크립트로 매번 새 곡(시드·BPM·키 변경, music_log.json 기록)을 만든다.

렌더: `cd reels/gen && PAGE=hyrox/hyrox.html OUT=/tmp/f START=0 STOP=125 node rec.js` (6개 병렬) → ffmpeg로 음악 합치기.

## 승인된 포맷 (자동 예약 가능)
- 격투기 토너먼트 — fight/
- 러닝 레이스 — run/
- 파워리프팅 최고 기록전 (점수×4=kg) — powerlifting/
- HYROX 레이스 (기록=120분−점수) — hyrox/ (2026-11-12 첫 게시)
- 짧은 릴스 '오늘의 브랜드' (9.6초) — short/short.html + music_short.py (2026-11-13 지훈 OK · 점심 12:37 화·목·토·일, 큐 파일명 YYYY-MM-DD-card.json 에 "video" 넣으면 됨)

## 승인 대기 (지훈 OK 전 큐에 넣지 않음)
- 보디빌딩 포징 심사, 요가·필라테스, 크로스핏, 컴프레션, 종합 스포츠

## 시리즈 스토리 (2026-11-13~)
모든 메인 릴스는 STORY.md 규칙대로 '지난 화/다음 화 예고' 오버레이를 넣는다: `STORY=ep.json PAGE=... node rec.js`. 회차 기록은 story_log.json.
