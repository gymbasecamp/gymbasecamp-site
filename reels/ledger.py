# -*- coding: utf-8 -*-
"""게시물 장부 (2026-11-20~, 인스타 개선 방향 H1).
게시물마다 꼬리표(형식·종목·EP·훅·길이·음악·게시 시각·표지)와 성과(게시 후 48시간 조회·좋아요·댓글·공유·저장)를 한 줄로 합친다.
- 꼬리표: reels/posted/<이름>.queue.json (큐에 "meta"가 있으면 우선) + story_log.json + music_log.json
- 성과: reels/insights/YYYY-MM-DD.json (매일 아침 수집) 중 게시 후 48시간에 가장 가까운 스냅샷
결과: reels/insights/ledger.csv, reels/insights/ledger.md (묶음별 중앙값)
"""
import os, json, glob, csv, re, statistics, datetime

R = os.path.dirname(os.path.abspath(__file__))
P = lambda *a: os.path.join(R, *a)
story = {e['date']: e for e in json.load(open(P('gen/story_log.json')))}
music = {}
for e in json.load(open(P('gen/music_log.json'))):
    if e.get('date'): music.setdefault(e['date'], []).append(e)

# 성과 스냅샷: media_id -> [(수집시각, metrics)]
snaps = {}
for f in sorted(glob.glob(P('insights/2*.json'))):
    d = json.load(open(f)); at = d.get('at_kst', os.path.basename(f)[:10])
    for m in d.get('media', []):
        met = dict(m.get('insights') or {})
        met.setdefault('likes', m.get('like_count')); met.setdefault('comments', m.get('comments_count'))
        snaps.setdefault(m['id'], []).append((at, met, m.get('timestamp'), m.get('media_product_type'), m.get('title')))

SPORTS = ['헬스·보디빌딩', '헬스', '보디빌딩', '파워리프팅', '스트렝스', '크로스핏', 'HYROX', '하이록스', '요가', '필라테스', '러닝', '격투기', '컴프레션', '종합 스포츠']
def sport_of(text):
    for s in SPORTS:
        if s in text: return {'헬스': '헬스·보디빌딩', '보디빌딩': '헬스·보디빌딩', '스트렝스': '파워리프팅', '하이록스': 'HYROX', '필라테스': '요가'}.get(s, s)
    return '여러 종목'

rows = []
for qf in sorted(glob.glob(P('posted/*.queue.json'))):
    name = os.path.basename(qf).replace('.queue.json', '')
    rf = P('posted', name + '.json')
    if not os.path.exists(rf): continue
    res = json.load(open(rf)); ig = str(res.get('instagram', ''))
    mid = ig.split()[-1] if ig.startswith('ok') else None
    if not mid or mid not in snaps: continue  # 삭제됐거나 아직 수집 안 된 게시물 제외
    q = json.load(open(qf)); meta = q.get('meta', {}); cap = q.get('caption', '')
    date = name[:10]; slot = 'card' if name.endswith('-card') else 'reel'
    kind = meta.get('format') or ('card' if q.get('images') else ('short' if slot == 'card' else 'contest'))
    st = story.get(date) if slot == 'reel' else None
    mu = (music.get(date) or [{}])[-1] if slot == 'reel' else {}
    sn = snaps.get(mid, [])
    pick = None
    if sn:
        ts = sn[0][2]
        try:
            t0 = datetime.datetime.strptime(ts[:19], '%Y-%m-%dT%H:%M:%S') + datetime.timedelta(hours=9)
            target = t0 + datetime.timedelta(hours=48)
            pick = min(sn, key=lambda s: abs((datetime.datetime.strptime(s[0][:16], '%Y-%m-%d %H:%M') - target).total_seconds()) if len(s[0]) >= 16 else 9e9)
            age_h = round((datetime.datetime.strptime(pick[0][:16], '%Y-%m-%d %H:%M') - t0).total_seconds() / 3600)
        except Exception:
            pick, age_h = sn[-1], None
    met = pick[1] if pick else {}
    views = met.get('views') or 0
    react = sum((met.get(k) or 0) for k in ('likes', 'comments', 'shares', 'saved'))
    rows.append({
        'date': date, 'slot': slot, 'format': kind,
        'sport': meta.get('sport') or (st or {}).get('sport') or sport_of(cap[:200]),
        'ep': meta.get('ep') or (st or {}).get('ep', ''),
        'hook': meta.get('hook') or cap.split('\n')[0][:60],
        'caption_first': 'EP형' if cap.startswith('[SEASON') else '훅형',
        'length_s': meta.get('length_s', ''), 'bpm': meta.get('bpm') or mu.get('bpm', ''),
        'music_kit': mu.get('kit', mu.get('script', '')), 'post_time': (sn[0][2][11:16] + ' UTC') if sn else '',
        'cover': meta.get('cover_style') or ('통일 템플릿' if date >= '2026-11-18' else '영상 프레임'),
        'media_id': mid, 'measured_at_h': age_h if pick else '',
        'views': views, 'likes': met.get('likes') or 0, 'comments': met.get('comments') or 0,
        'shares': met.get('shares') or 0, 'saved': met.get('saved') or 0,
        'react_per_1k': round(react / views * 1000, 1) if views else '',
    })

os.makedirs(P('insights'), exist_ok=True)
with open(P('insights/ledger.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ['date']); w.writeheader(); w.writerows(rows)

def med(v): v = [x for x in v if isinstance(x, (int, float))]; return round(statistics.median(v), 1) if v else '-'
md = ['# 게시물 장부 요약 (자동 생성)', '', f'게시물 {len(rows)}개 · 비교는 게시 후 48시간 값의 **중앙값** · 같은 묶음 3편 이상만 판정', '']
for key, title in (('format', '형식별'), ('sport', '종목별'), ('caption_first', '캡션 첫 줄'), ('cover', '표지')):
    md += [f'## {title}', '', '| 묶음 | 편수 | 조회 중앙값 | 반응/1천회 중앙값 | 저장 합 | 공유 합 |', '|---|---|---|---|---|---|']
    groups = {}
    for r in rows: groups.setdefault(r[key], []).append(r)
    for g, rs in sorted(groups.items(), key=lambda x: -len(x[1])):
        md.append(f"| {g} | {len(rs)}{'' if len(rs) >= 3 else ' (판정 보류)'} | {med([r['views'] for r in rs])} | {med([r['react_per_1k'] for r in rs])} | {sum(r['saved'] for r in rs)} | {sum(r['shares'] for r in rs)} |")
    md.append('')
md += ['## 조회 상위 5', '', '| 날짜 | 형식 | 종목 | 조회 | 첫 줄 |', '|---|---|---|---|---|']
for r in sorted(rows, key=lambda r: -r['views'])[:5]:
    md.append(f"| {r['date']} | {r['format']} | {r['sport']} | {r['views']} | {r['hook'][:30]} |")
open(P('insights/ledger.md'), 'w').write('\n'.join(md) + '\n')
print(len(rows), 'rows')
