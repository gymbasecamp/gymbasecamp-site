"""Build GYM BASECAMP outputs from app.css + app.html + data/brands.json + en.py.

Outputs (in out/):
  gb-wordpress.html  paste into a WordPress Custom HTML block (or a WPCode HTML snippet)
  index.html         full standalone page (upload by FTP, or open locally)
  gym-basecamp.html  claude.ai artifact preview (same content, title first)
Every CSS selector is scoped under #gbapp so Astra's theme styles can't override it.
"""
import json, os, re
D = os.path.dirname(os.path.abspath(__file__))
P = lambda *a: os.path.join(D, *a)

ns = {}
exec(open(P('en.py'), encoding='utf-8').read(), ns)
B = json.load(open(P('data/brands.json'), encoding='utf-8'))
for b in B:
    b['descEn'] = ns['DESC'].get(b['id'], b['desc'])

def scope_selector(sel):
    sel = sel.strip()
    if sel in (':root', 'body', 'html'):
        return '#gbapp'
    if sel == '*':
        return '#gbapp,#gbapp *'
    return '#gbapp ' + sel

def split_top(s, ch=','):
    out, depth, cur = [], 0, ''
    for c in s:
        if c in '([': depth += 1
        if c in ')]': depth -= 1
        if c == ch and depth == 0:
            out.append(cur); cur = ''
        else:
            cur += c
    out.append(cur)
    return out

def scope_css(css):
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    out, i, n = [], 0, len(css)
    def parse_block(start):
        res, i = [], start
        while i < n:
            while i < n and css[i] in ' \n\t\r': i += 1
            if i >= n or css[i] == '}':
                return ''.join(res), i + 1
            j = css.index('{', i)
            prelude = css[i:j].strip()
            if prelude.startswith('@media') or prelude.startswith('@supports'):
                inner, i = parse_block(j + 1)
                res.append(prelude + '{' + inner + '}')
            else:
                k = css.index('}', j)
                body = css[j + 1:k].strip()
                sels = ','.join(scope_selector(s) for s in split_top(prelude))
                res.append(sels + '{' + body + '}')
                i = k + 1
        return ''.join(res), i
    result, _ = parse_block(0)
    return result

css = scope_css(open(P('app.css'), encoding='utf-8').read())
app = open(P('app.html'), encoding='utf-8').read()
safe = lambda o: json.dumps(o, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
rank_js = open(P('rank_v2.js'), encoding='utf-8').read().split('if(typeof module')[0]
react_path = P('data/react.json')
REACT = json.load(open(react_path, encoding='utf-8')) if os.path.exists(react_path) else {}
app = app.replace('/*__RANK_V2__*/', rank_js).replace('__REACT__', safe(REACT))
import datetime as _dt
_hp = P('data/rank_history.json')
_H = json.load(open(_hp, encoding='utf-8')) if os.path.exists(_hp) else {}
_t = (_dt.datetime.now(_dt.timezone.utc) + _dt.timedelta(hours=9)).strftime('%Y-%m-%d')
_ds = sorted(d for d in _H if d < _t)
PREV = {'d': _ds[-1], 'r': {k: v[1:3] for k, v in _H[_ds[-1]].items()}} if _ds else {'d': '', 'r': {}}
app = app.replace('__PREV__', safe(PREV))
app = app.replace('__DATA__', safe(B)).replace('__TOK__', safe(ns['TOK']))

FONTS = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@700;800;900&family=IBM+Plex+Sans+KR:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap">'
snippet = f'<!-- GYM BASECAMP landing (built {__import__("datetime").date.today()}) -->\n{FONTS}\n<style>{css}</style>\n{app}'

DESC = '국내외 짐웨어 브랜드 50+ 한곳에서. 머슬핏, 오버핏, 컴프레션, 애슬레저까지 나에게 맞는 운동복 브랜드를 발견하세요.'
page_css = '<style>html,body{margin:0;background:#F2F1EE}</style>'
standalone = f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>GYM BASECAMP · 국내외 짐웨어 브랜드 50+ 한곳에서</title>
<meta name="description" content="{DESC}">
<meta property="og:title" content="GYM BASECAMP">
<meta property="og:description" content="{DESC}">
<meta name="theme-color" content="#111111">
{page_css}
</head>
<body>
{snippet}
</body>
</html>
'''
artifact = f'''<title>GYM BASECAMP</title>
<meta name="claude:viewport-fit-sides" content="cover">
{page_css}
{snippet}
'''
os.makedirs(P('out'), exist_ok=True)
for name, txt in [('gb-wordpress.html', snippet), ('index.html', standalone), ('gym-basecamp.html', artifact)]:
    open(P('out', name), 'w', encoding='utf-8').write(txt)
script = re.findall(r'<script>(.*?)</script>', snippet, re.S)[0]
open(P('out', '_check.js'), 'w', encoding='utf-8').write(script)
print(len(B), 'brands;', {k: os.path.getsize(P('out', k)) for k in ('gb-wordpress.html', 'index.html', 'gym-basecamp.html')})
