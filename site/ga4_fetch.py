"""Pull GYM BASECAMP numbers from GA4 (read-only service account) into the repo.
Env: GA4_SA_JSON (service-account key JSON), GA4_PROPERTY_ID (digits).
Writes:
  site/data/ga_daily.json : {"YYYY-MM-DD": {users, sessions, sources:{src:sessions}, events:{name:n}, top_brands:[[brand,official,views]]}}
  site/data/react.json    : {"<id>": {view, official, compare, quiz}} last 28 days -> ranking "사용자 반응" (activates at 200+ brand views)
"""
import json, os, re, sys, datetime
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

D = os.path.dirname(os.path.abspath(__file__))
P = lambda *a: os.path.join(D, *a)
prop = os.environ['GA4_PROPERTY_ID'].strip()
creds = service_account.Credentials.from_service_account_info(
    json.loads(os.environ['GA4_SA_JSON']), scopes=['https://www.googleapis.com/auth/analytics.readonly'])
S = AuthorizedSession(creds)
URL = f'https://analyticsdata.googleapis.com/v1beta/properties/{prop}:runReport'

def report(dims, mets, start, end='yesterday', filt=None, limit=1000):
    body = {'dateRanges': [{'startDate': start, 'endDate': end}],
            'dimensions': [{'name': d} for d in dims], 'metrics': [{'name': m} for m in mets], 'limit': limit}
    if filt: body['dimensionFilter'] = filt
    r = S.post(URL, json=body, timeout=60); r.raise_for_status()
    out = []
    for row in r.json().get('rows', []):
        out.append([v['value'] for v in row.get('dimensionValues', [])] + [float(v['value']) for v in row['metricValues']])
    return out

kst = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)
day = (kst - datetime.timedelta(days=1)).strftime('%Y-%m-%d')

tot = report([], ['activeUsers', 'sessions'], 'yesterday')
users, sessions = (tot[0] if tot else [0, 0])
src = {s: int(n) for s, n in report(['sessionSource'], ['sessions'], 'yesterday')}
ev = {e: int(n) for e, n in report(['eventName'], ['eventCount'], 'yesterday')}

# brand-level events, 28 days (custom dimension 'brand' registered as customEvent:brand)
want = ['brand_view', 'official_click', 'compare_add', 'shop_click', 'search_result_click']
rows = report(['customEvent:brand', 'eventName'], ['eventCount'], '28daysAgo',
              filt={'filter': {'fieldName': 'eventName', 'inListFilter': {'values': want}}}, limit=10000)
B = json.load(open(P('data/brands.json'), encoding='utf-8'))
by_en = {b['en'].lower(): b['id'] for b in B}
react = {}
for brand, name, n in rows:
    bid = by_en.get((brand or '').lower())
    if not bid: continue
    c = react.setdefault(bid, {'view': 0, 'official': 0, 'compare': 0, 'quiz': 0})
    if name in ('brand_view', 'search_result_click'): c['view'] += int(n)
    elif name in ('official_click', 'shop_click'): c['official'] += int(n)
    elif name == 'compare_add': c['compare'] += int(n)
json.dump(react, open(P('data/react.json'), 'w', encoding='utf-8'), ensure_ascii=False, sort_keys=True, indent=0)

top = sorted(((k, v['official'], v['view']) for k, v in react.items()), key=lambda x: (-x[1], -x[2]))[:10]
hp = P('data/ga_daily.json')
H = json.load(open(hp, encoding='utf-8')) if os.path.exists(hp) else {}
H[day] = {'users': int(users), 'sessions': int(sessions), 'sources': src, 'events': ev, 'top_brands_28d': top}
for d in sorted(H)[:-180]: del H[d]
json.dump(H, open(hp, 'w', encoding='utf-8'), ensure_ascii=False, sort_keys=True, indent=1)
print(f'{day}: users {int(users)}, sessions {int(sessions)}, sources {src}, brand views 28d {sum(v["view"] for v in react.values())}')

# 오늘(KST) 진행 중 수치 — 몇 시간마다 갱신, 확정치는 다음 날 ga_daily.json
tt = report([], ['activeUsers', 'sessions'], 'today', 'today')
tu, ts = (tt[0] if tt else [0, 0])
tsrc = {s: int(n) for s, n in report(['sessionSource'], ['sessions'], 'today', 'today')}
tev = {e: int(n) for e, n in report(['eventName'], ['eventCount'], 'today', 'today')}
json.dump({'date': kst.strftime('%Y-%m-%d'), 'updated_kst': kst.strftime('%Y-%m-%d %H:%M'), 'users': int(tu), 'sessions': int(ts), 'sources': tsrc, 'events': tev},
          open(P('data/ga_today.json'), 'w', encoding='utf-8'), ensure_ascii=False, sort_keys=True, indent=1)
print(f'today so far: users {int(tu)}, sessions {int(ts)}, sources {tsrc}')
