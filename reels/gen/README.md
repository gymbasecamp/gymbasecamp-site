# 대회형 릴스 생성기 (2026-11-12~)
브랜드를 선수처럼 표현해 종목별 대회로 5위→1위를 보여준다. 각 html 맨 위 `const D=` 를 그날 순위로 바꾸고, 같은 폴더의 music 스크립트로 매번 새 곡(시드·BPM·키 변경, music_log.json 기록)을 만든다.

렌더: `cd reels/gen && PAGE=hyrox/hyrox.html OUT=/tmp/f START=0 STOP=125 node rec.js` (6개 병렬) → ffmpeg로 음악 합치기.

## 승인된 포맷 (자동 예약 가능)
- 격투기 토너먼트 — fight/
- 러닝 레이스 — run/
- 파워리프팅 최고 기록전 (점수×4=kg) — powerlifting/
- HYROX 레이스 (기록=120분−점수) — hyrox/ (2026-11-12 첫 게시)

## 승인 대기 (지훈 OK 전 큐에 넣지 않음)
- 보디빌딩 포징 심사, 요가·필라테스, 크로스핏, 컴프레션, 종합 스포츠
