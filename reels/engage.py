"""매일 '오늘의 소통 리스트' 후보 수집 (읽기 전용 — 좋아요·댓글을 자동으로 달지 않는다).
1) 사이트 브랜드 공식 계정(brands.csv '인스타그램' 칸의 확인된 @계정)의 최근 게시물 — business_discovery
2) 운동 해시태그 인기 게시물 — ig_hashtag_search + top_media (주 30개 해시태그 한도 안에서 요일별로 돌림)
결과: reels/engage/YYYY-MM-DD.json
"""
import os, csv, json, re, datetime, requests
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tok, uid = os.environ.get('IG_TOKEN'), os.environ.get('IG_USER_ID')
G = 'https://graph.facebook.com/v21.0' if not (tok or '').startswith('IG') else 'https://graph.instagram.com/v21.0'
kst = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)
day = kst.strftime('%Y-%m-%d'); wd = kst.weekday()
out = {'date': day, 'brands': [], 'hashtags': [], 'errors': []}
since = (kst - datetime.timedelta(days=4)).isoformat()

# 1) 브랜드 계정 — 매일 18개씩 돌아가며
rows = list(csv.DictReader(open(os.path.join(ROOT, 'site/data/brands.csv'), encoding='utf-8')))
handles = []
for r in rows:
    if r.get('사이트 공개') != '공개': continue
    m = re.match(r'@([A-Za-z0-9._]+)', (r.get('인스타그램') or '').strip())
    if m: handles.append((m.group(1), r['브랜드 명'], r.get('대표 카테고리', '')))
k = 18; start = (kst.toordinal() * k) % max(1, len(handles))
pick = (handles[start:] + handles[:start])[:k]
F = 'media.limit(4){permalink,caption,like_count,comments_count,timestamp,media_type}'
for h, name, cat in pick:
    try:
        r = requests.get(f'{G}/{uid}', params={'fields': f'business_discovery.username({h}){{username,followers_count,{F}}}', 'access_token': tok}, timeout=30).json()
        bd = r.get('business_discovery')
        if not bd: out['errors'].append(f'@{h}: {str(r)[:160]}'); continue
        for m in bd.get('media', {}).get('data', []):
            if m.get('timestamp', '') < since[:10]: continue
            out['brands'].append({'brand': name, 'cat': cat, 'account': '@' + h, 'followers': bd.get('followers_count'),
                                  'url': m.get('permalink'), 'likes': m.get('like_count'), 'comments': m.get('comments_count'),
                                  'time': m.get('timestamp'), 'type': m.get('media_type'), 'caption': (m.get('caption') or '')[:400]})
    except Exception as ex: out['errors'].append(f'@{h}: {ex}')

# 2) 해시태그 — 요일별 4개(총 28개 고정 목록, 주 30개 한도 이하)
TAGS = [['헬스타그램', 'gymwear', 'hyrox', '오운완'], ['러닝크루', 'runningcommunity', '운동복', 'fitnessmotivation'],
        ['크로스핏', 'powerlifting', '운동동기부여', 'gymshark'], ['필라테스', 'yogawear', '하이록스', 'legday'],
        ['마라톤', 'bodybuilding', '운동하는여자', 'gymmotivation'], ['주짓수', 'muaythai', '바디프로필', 'athleisure'],
        ['홈트', 'hybridathlete', '3대운동', 'activewear']]
for tag in TAGS[wd]:
    try:
        s = requests.get(f'{G}/ig_hashtag_search', params={'user_id': uid, 'q': tag, 'access_token': tok}, timeout=30).json()
        if not s.get('data'): out['errors'].append(f'#{tag}: {str(s)[:160]}'); continue
        hid = s['data'][0]['id']
        t = requests.get(f'{G}/{hid}/top_media', params={'user_id': uid, 'fields': 'permalink,caption,like_count,comments_count,timestamp,media_type', 'limit': 12, 'access_token': tok}, timeout=30).json()
        for m in t.get('data', []):
            out['hashtags'].append({'tag': '#' + tag, 'url': m.get('permalink'), 'likes': m.get('like_count'), 'comments': m.get('comments_count'),
                                    'time': m.get('timestamp'), 'type': m.get('media_type'), 'caption': (m.get('caption') or '')[:400]})
        if 'error' in t: out['errors'].append(f'#{tag} top: {str(t)[:160]}')
    except Exception as ex: out['errors'].append(f'#{tag}: {ex}')

json.dump(out, open(os.path.join(ROOT, 'reels/engage', day + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f"brands {len(out['brands'])} posts / hashtags {len(out['hashtags'])} posts / errors {len(out['errors'])}")
for e in out['errors'][:8]: print(' -', e)
