"""오늘(KST) 예약된 릴스를 인스타그램(+유튜브 쇼츠)에 자동 업로드.
큐 형식: reels/queue/YYYY-MM-DD.json
  {"video": "reels/queue/YYYY-MM-DD.mp4", "caption": "...", "title": "유튜브 제목(100자 이내)", "platforms": ["instagram","youtube"]}
비밀값(GitHub secrets): IG_TOKEN, IG_USER_ID / YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN
없는 플랫폼은 건너뛴다. 결과는 reels/posted/YYYY-MM-DD.json 에 기록하고 큐 파일을 옮긴다.
"""
import os, sys, json, time, datetime, requests
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
kst = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)
day = os.environ.get('PUBLISH_DATE') or kst.strftime('%Y-%m-%d')
# 카드뉴스: reels/queue/YYYY-MM-DD-card.json {"images":[...], "caption":...} — 낮 실행(KST 16시 전)이나 PUBLISH_KIND=card 일 때
kind = os.environ.get('PUBLISH_KIND') or ('card' if kst.hour < 16 and not os.environ.get('PUBLISH_DATE') else 'reel')
if kind == 'card': day = day + '-card'
q = os.path.join(ROOT, 'reels/queue', day + '.json')
if not os.path.exists(q):
    print('no queue for', day); sys.exit(0)
item = json.load(open(q, encoding='utf-8'))
video = item.get('video', ''); plats = item.get('platforms', ['instagram', 'youtube'])
sha = os.environ.get('GITHUB_SHA', 'main')
public_url = f'https://cdn.jsdelivr.net/gh/gymbasecamp/gymbasecamp-site@{sha}/{video}'
result = {'date': day, 'video_url': public_url}

def instagram():
    tok, uid = os.environ.get('IG_TOKEN'), os.environ.get('IG_USER_ID')
    if not (tok and uid): return 'skip: IG secrets not set'
    # IGAA = 인스타 로그인 토큰 / EAA = 페이스북(시스템 사용자) 토큰
    G = 'https://graph.facebook.com/v21.0' if not tok.startswith('IG') else 'https://graph.instagram.com/v21.0'
    # 11/13 릴스: 인스타가 jsDelivr 영상을 못 가져옴(2207052) → 캐시 예열·재시도 후 raw.githubusercontent 로 대체
    raw = f'https://raw.githubusercontent.com/gymbasecamp/gymbasecamp-site/{sha}/'
    cands = [(public_url, f"https://cdn.jsdelivr.net/gh/gymbasecamp/gymbasecamp-site@{sha}/"), (public_url, f"https://cdn.jsdelivr.net/gh/gymbasecamp/gymbasecamp-site@{sha}/"), (raw + video, raw)]
    errs, cid, vurl = [], None, None
    for i, (vu, base) in enumerate(cands):
        try: requests.get(vu, timeout=120, stream=True).close()  # CDN 캐시 예열
        except Exception: pass
        if i: time.sleep(20)
        r = requests.post(f'{G}/{uid}/media', data={'media_type': 'REELS', 'video_url': vu,
            'caption': item['caption'], 'share_to_feed': 'true', 'access_token': tok,
            **({'cover_url': base + item['cover']} if item.get('cover') else {})}, timeout=60).json()
        if 'id' not in r: errs.append(f'create {vu}: {r}'); continue
        st = None
        for _ in range(40):
            s = requests.get(f'{G}/{r["id"]}', params={'fields': 'status_code,status', 'access_token': tok}, timeout=30).json()
            st = s.get('status_code')
            if st in ('FINISHED', 'ERROR'): break
            time.sleep(15)
        if st == 'FINISHED': cid, vurl = r['id'], vu; break
        errs.append(f'processing {vu}: {s}')
    if not cid: return f'error: {errs}'
    result['video_url'] = vurl
    p = requests.post(f'{G}/{uid}/media_publish', data={'creation_id': cid, 'access_token': tok}, timeout=60).json()
    if 'id' not in p: return f'error publish: {p}'
    # 같은 영상을 스토리로도 알림 (실패해도 릴스 결과에는 영향 없음)
    try:
        r2 = requests.post(f'{G}/{uid}/media', data={'media_type': 'STORIES', 'video_url': vurl, 'access_token': tok}, timeout=60).json()
        if 'id' in r2:
            for _ in range(30):
                s2 = requests.get(f'{G}/{r2["id"]}', params={'fields': 'status_code', 'access_token': tok}, timeout=30).json()
                if s2.get('status_code') in ('FINISHED', 'ERROR'): break
                time.sleep(10)
            p2 = requests.post(f'{G}/{uid}/media_publish', data={'creation_id': r2['id'], 'access_token': tok}, timeout=60).json()
            result['story'] = f"ok {p2.get('id')}" if 'id' in p2 else f'error {p2}'
        else: result['story'] = f'error {r2}'
    except Exception as ex: result['story'] = f'error {ex}'
    return f"ok {p.get('id')}"

def carousel():
    tok, uid = os.environ.get('IG_TOKEN'), os.environ.get('IG_USER_ID')
    if not (tok and uid): return 'skip: IG secrets not set'
    G = 'https://graph.facebook.com/v21.0' if not tok.startswith('IG') else 'https://graph.instagram.com/v21.0'
    kids = []
    for im in item['images']:
        # 11/11 카드: 인스타가 jsDelivr 이미지를 못 가져옴(2207052) → 재시도 후 raw.githubusercontent 로 대체
        urls = [f'https://cdn.jsdelivr.net/gh/gymbasecamp/gymbasecamp-site@{sha}/{im}',
                f'https://cdn.jsdelivr.net/gh/gymbasecamp/gymbasecamp-site@{sha}/{im}',
                f'https://raw.githubusercontent.com/gymbasecamp/gymbasecamp-site/{sha}/{im}']
        errs = []
        for i, u in enumerate(urls):
            if i: time.sleep(20)
            r = requests.post(f'{G}/{uid}/media', data={'image_url': u, 'is_carousel_item': 'true', 'access_token': tok}, timeout=60).json()
            if 'id' in r: break
            errs.append(f'{u}: {r}')
        if 'id' not in r: return f'error item {im}: {errs}'
        kids.append(r['id'])
    r = requests.post(f'{G}/{uid}/media', data={'media_type': 'CAROUSEL', 'children': ','.join(kids), 'caption': item['caption'], 'access_token': tok}, timeout=60).json()
    if 'id' not in r: return f'error carousel: {r}'
    cid = r['id']
    for _ in range(20):
        st = requests.get(f'{G}/{cid}', params={'fields': 'status_code', 'access_token': tok}, timeout=30).json()
        if st.get('status_code') in ('FINISHED', None): break
        if st.get('status_code') == 'ERROR': return f'error processing: {st}'
        time.sleep(5)
    p = requests.post(f'{G}/{uid}/media_publish', data={'creation_id': cid, 'access_token': tok}, timeout=60).json()
    return f"ok {p.get('id')}" if 'id' in p else f'error publish: {p}'

def youtube():
    cid, sec, ref = (os.environ.get(k) for k in ('YT_CLIENT_ID', 'YT_CLIENT_SECRET', 'YT_REFRESH_TOKEN'))
    if not (cid and sec and ref): return 'skip: YT secrets not set'
    t = requests.post('https://oauth2.googleapis.com/token', data={'client_id': cid, 'client_secret': sec,
        'refresh_token': ref, 'grant_type': 'refresh_token'}, timeout=30).json()
    if 'access_token' not in t: return f'error token: {t}'
    meta = {'snippet': {'title': item.get('title', item['caption'].split('\n')[0])[:95] + ' #shorts',
                        'description': item['caption'], 'categoryId': '17', 'defaultLanguage': 'ko'},
            'status': {'privacyStatus': item.get('yt_privacy', 'public'), 'selfDeclaredMadeForKids': False}}
    body = open(os.path.join(ROOT, video), 'rb').read()
    b = 'gbboundary'
    data = (f'--{b}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n' + json.dumps(meta) +
            f'\r\n--{b}\r\nContent-Type: video/mp4\r\n\r\n').encode() + body + f'\r\n--{b}--'.encode()
    r = requests.post('https://www.googleapis.com/upload/youtube/v3/videos?uploadType=multipart&part=snippet,status',
                      headers={'Authorization': 'Bearer ' + t['access_token'], 'Content-Type': f'multipart/related; boundary={b}'},
                      data=data, timeout=300).json()
    return f"ok {r.get('id')} ({r.get('status', {}).get('privacyStatus')})" if 'id' in r else f'error upload: {r}'

if item.get('images'): result['instagram'] = carousel(); plats = []
if 'instagram' in plats: result['instagram'] = instagram()
if 'youtube' in plats: result['youtube'] = youtube()
print(json.dumps(result, ensure_ascii=False))
if any(str(v).startswith('ok') for k, v in result.items() if k in ('instagram', 'youtube')):
    json.dump(result, open(os.path.join(ROOT, 'reels/posted', day + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    os.replace(q, os.path.join(ROOT, 'reels/posted', day + '.queue.json'))
else:
    json.dump(result, open(os.path.join(ROOT, 'reels/posted', day + '.error.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
