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
q = os.path.join(ROOT, 'reels/queue', day + '.json')
if not os.path.exists(q):
    print('no queue for', day); sys.exit(0)
item = json.load(open(q, encoding='utf-8'))
video = item['video']; plats = item.get('platforms', ['instagram', 'youtube'])
sha = os.environ.get('GITHUB_SHA', 'main')
public_url = f'https://cdn.jsdelivr.net/gh/gymbasecamp/gymbasecamp-site@{sha}/{video}'
result = {'date': day, 'video_url': public_url}

def instagram():
    tok, uid = os.environ.get('IG_TOKEN'), os.environ.get('IG_USER_ID')
    if not (tok and uid): return 'skip: IG secrets not set'
    G = 'https://graph.instagram.com/v21.0'
    r = requests.post(f'{G}/{uid}/media', data={'media_type': 'REELS', 'video_url': public_url,
        'caption': item['caption'], 'share_to_feed': 'true', 'access_token': tok}, timeout=60).json()
    if 'id' not in r: return f'error create: {r}'
    cid = r['id']
    for _ in range(40):
        s = requests.get(f'{G}/{cid}', params={'fields': 'status_code,status', 'access_token': tok}, timeout=30).json()
        if s.get('status_code') == 'FINISHED': break
        if s.get('status_code') == 'ERROR': return f'error processing: {s}'
        time.sleep(15)
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

if 'instagram' in plats: result['instagram'] = instagram()
if 'youtube' in plats: result['youtube'] = youtube()
print(json.dumps(result, ensure_ascii=False))
if any(str(v).startswith('ok') for k, v in result.items() if k in ('instagram', 'youtube')):
    json.dump(result, open(os.path.join(ROOT, 'reels/posted', day + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    os.replace(q, os.path.join(ROOT, 'reels/posted', day + '.queue.json'))
