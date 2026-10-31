# gymbasecamp-site

GYM BASECAMP (gymbasecamp.kr) 사이트 데이터·코드 자동 배포 저장소.

- 브랜드 마스터 DB: `site/data/brands.csv` (매일 리서치가 여기를 수정)
- 빌드: `site/build_all.sh` → `dist/gb.js`
- 워드프레스(WPCode 스니펫 14, JavaScript)에는 `wp-snippet.js` 한 번만 넣어 둔다.
  이 코드가 GitHub 최신 커밋을 조회해 jsDelivr로 `dist/gb.js`를 불러오므로,
  이 저장소 main에 push하면 실제 사이트가 바로 바뀐다.
