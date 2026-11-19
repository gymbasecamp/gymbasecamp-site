"""인스타 게시물 성과 수집(읽기 전용, 2026-11-20~). 주간 리뷰·콘텐츠 실험 판정용.
기본 필드(좋아요·댓글 수)는 게시 권한 토큰으로도 읽히고, 조회·도달·저장·공유·평균 시청 시간은
instagram_manage_insights 권한이 있을 때만 읽힌다(없으면 오류를 그대로 기록).
결과: reels/insights/YYYY-MM-DD.json
"""
import os, json, datetime, requests
tok, uid = os.environ['IG_TOKEN'], os.environ['IG_USER_ID']
G = 'https://graph.facebook.com/v21.0' if not tok.startswith('IG') else 'https://graph.instagram.com/v21.0'
kst = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)
out = {'at_kst': kst.strftime('%Y-%m-%d %H:%M'), 'account': {}, 'media': [], 'errors': {}}
r = requests.get(f'{G}/{uid}', params={'fields': 'username,followers_count,media_count', 'access_token': tok}, timeout=30).json()
out['account'] = {k: r.get(k) for k in ('username', 'followers_count', 'media_count')}
if 'error' in r: out['errors']['account'] = r['error'].get('message')
r = requests.get(f'{G}/{uid}/media', params={'fields': 'id,caption,media_type,media_product_type,timestamp,permalink,like_count,comments_count', 'limit': 40, 'access_token': tok}, timeout=30).json()
if 'error' in r: out['errors']['media'] = r['error'].get('message')
REEL = 'reach,views,likes,comments,shares,saved,total_interactions,ig_reels_avg_watch_time,ig_reels_video_view_total_time'
FEED = 'reach,views,likes,comments,shares,saved,total_interactions'
for m in r.get('data', []):
    row = {k: m.get(k) for k in ('id', 'timestamp', 'media_type', 'media_product_type', 'permalink', 'like_count', 'comments_count')}
    row['title'] = (m.get('caption') or '').split('\n')[0][:80]
    met = REEL if m.get('media_product_type') == 'REELS' else FEED
    ir = requests.get(f"{G}/{m['id']}/insights", params={'metric': met, 'access_token': tok}, timeout=30).json()
    if 'error' in ir:
        row['insights_error'] = ir['error'].get('message')
    else:
        row['insights'] = {d['name']: (d.get('values') or [{}])[0].get('value') for d in ir.get('data', [])}
    out['media'].append(row)
# 계정 단위(팔로워 활동 시간·도달) — 권한 있으면
ar = requests.get(f'{G}/{uid}/insights', params={'metric': 'reach,profile_views,website_clicks,follower_count', 'period': 'day', 'access_token': tok}, timeout=30).json()
if 'error' in ar: out['errors']['account_insights'] = ar['error'].get('message')
else: out['account_insights'] = {d['name']: d.get('values') for d in ar.get('data', [])}
os.makedirs('reels/insights', exist_ok=True)
p = f"reels/insights/{kst.strftime('%Y-%m-%d')}.json"
json.dump(out, open(p, 'w'), ensure_ascii=False, indent=1)
print(p, json.dumps(out['errors'], ensure_ascii=False), len(out['media']), 'media')
