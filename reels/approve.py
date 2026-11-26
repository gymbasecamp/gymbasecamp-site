# -*- coding: utf-8 -*-
"""지훈 점검 OK → 게시 승인 (2026-11-27~). 사용: python3 reels/approve.py 2026-11-28 [card|reel]
큐 json의 "approved"를 true로 바꾼다. 종류를 안 주면 그날 메인 릴스·점심 게시물 둘 다."""
import json, os, sys
R = os.path.dirname(os.path.abspath(__file__))
day = sys.argv[1]; kind = sys.argv[2] if len(sys.argv) > 2 else 'all'
names = {'reel': [day], 'card': [day + '-card']}.get(kind, [day, day + '-card'])
for n in names:
    p = os.path.join(R, 'queue', n + '.json')
    if not os.path.exists(p): print('없음', n); continue
    q = json.load(open(p, encoding='utf-8')); q['approved'] = True
    json.dump(q, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1); print('승인', n)
