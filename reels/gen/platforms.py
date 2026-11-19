# -*- coding: utf-8 -*-
"""업로드 패키지 만들기 (2026-11-17 지훈: "업로드할 걸 만들면 인스타 릴스/피드 버전, TikTok 캡션, YouTube 쇼츠 캡션 등 전부 같이 항상 준비").

사용: python3 platforms.py reels/queue/2026-11-19.json [--title "유튜브 제목"]
결과: reels/out/<큐 이름>/  ← 영상(mp4)·커버·captions.md(플랫폼별 복붙용)·captions.json
- 인스타: 큐 캡션 그대로(릴스는 피드에도 같이 노출). 카드뉴스 큐면 피드 캐러셀 이미지 목록.
- TikTok: 훅 1줄 + TOP5 압축 + 질문 + 해시태그 5개(2,200자 제한 안, 짧게)
- YouTube Shorts: 제목(100자 이하, #Shorts) + 설명(링크 https:// 가능) + 해시태그 3개
"""
import json, re, sys, os, shutil, argparse

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

def parse(cap):
    lines = [l.strip() for l in cap.split('\n')]
    hook = next((l for l in lines if l), '')
    ranks = [l for l in lines if re.match(r'^\d위\s', l)]
    tags = re.findall(r'#\S+', cap)
    ask = next((l.lstrip('💬 ').strip() for l in lines if l.startswith('💬')), '')
    nxt = next((l for l in lines if l.startswith('다음 화')), '')
    notes = [l for l in lines if l.startswith('📌')]
    date = re.search(r'\((\d{1,2}\.\d{1,2}) 집계\)', cap)
    return dict(hook=hook, ranks=ranks, tags=tags, ask=ask, next=nxt, notes=notes, date=date.group(1) if date else '')

def dedupe_tags(text):
    seen=set(); out=[]
    for line in text.split('\n'):
        if line.startswith('#'):
            tags=[t for t in line.split() if not (t in seen or seen.add(t))]
            line=' '.join(tags)
        out.append(line)
    return '\n'.join(out)

def strip_handles(s):  # 틱톡·유튜브에선 인스타 @태그가 다른 계정을 가리킬 수 있어 뺀다
    return re.sub(r'\s*@[\w.]+', '', s).strip()

def build(qpath, title=None):
    q = json.load(open(qpath)); cap = q.get('caption', ''); P = parse(cap)
    name = os.path.basename(qpath).replace('.json', '')
    out = os.path.join(ROOT, 'reels', 'out', name); os.makedirs(out, exist_ok=True)
    files = []
    for k in ('video', 'cover'):
        if q.get(k) and os.path.exists(os.path.join(ROOT, q[k])):
            dst = os.path.join(out, os.path.basename(q[k])); shutil.copy(os.path.join(ROOT, q[k]), dst); files.append(dst)
    imgs = [i for i in q.get('images', []) if os.path.exists(os.path.join(ROOT, i))]
    for i in imgs: dst = os.path.join(out, os.path.basename(i)); shutil.copy(os.path.join(ROOT, i), dst); files.append(dst)
    ranks_short = [strip_handles(r) for r in P['ranks']]
    hook = strip_handles(re.sub(r'^\[[^\]]+\]\s*', '', P['hook']))
    ep = re.search(r'EP\.(\d+)', P['hook']); ep = ep.group(1) if ep else ''
    base_tags = [t for t in P['tags'] if t != '#베이스캠프정상쟁탈전'][:3]
    # TikTok
    tk = [f"{'[EP.'+ep+'] ' if ep else ''}{hook}", '']
    if ranks_short: tk += ranks_short[::-1][:3] + ['…전체 순위는 프로필 링크', '']
    if P['ask']: tk += [P['ask'], '']
    tk += [' '.join(['#베이스캠프정상쟁탈전'] + base_tags + ['#운동복추천'][: 5 - 1 - len(base_tags)] )]
    tiktok = '\n'.join(tk).strip()
    tiktok = dedupe_tags(tiktok)
    if imgs:  # 카드뉴스: 본문(종목별 순위 줄 등)을 그대로 살리고 해시태그만 5개로
        body = [l for l in cap.split('\n') if not l.startswith('#')]
        tags = ['#베이스캠프정상쟁탈전'] + [t for t in P['tags'] if t != '#베이스캠프정상쟁탈전'][:4]
        tiktok = dedupe_tags(strip_handles('\n'.join(body)).strip() + '\n\n' + ' '.join(tags))
    # YouTube Shorts
    sport = ''
    try:
        log = json.load(open(os.path.join(ROOT, 'reels', 'gen', 'story_log.json')))
        sport = next((e['sport'] for e in log if str(e.get('ep')) == ep), '')
    except Exception: pass
    if title: yt_title = title
    elif ep and sport: yt_title = f"[EP.{ep}] {sport} 운동복 브랜드 TOP5 — 1위는?"
    else: yt_title = hook if len(hook) <= 80 else hook[:78] + '…'
    yt_title = (yt_title + ' #Shorts')[:100]
    yd = [hook, '']
    if ranks_short: yd += ranks_short + ['']
    yd += [n.lstrip('📌 ') for n in P['notes']]
    if P['notes']: yd.append('')
    yd += ['광고 아님 · 순위에 광고를 섞지 않습니다' + (f" ({P['date']} 집계)" if P['date'] else ''), '']
    if P['next']: yd += [P['next'], '']
    yd += ['전체 순위·공식몰 바로가기 👉 https://gymbasecamp.kr', '']
    if P['ask']: yd += [P['ask'] if '댓글' in P['ask'] else P['ask'] + ' 댓글로', '']
    yd += [' '.join(['#Shorts', '#운동복'] + base_tags[:1])]
    yt_desc = dedupe_tags('\n'.join(yd).strip())
    if imgs:
        yt_title = yt_title.replace(' #Shorts', '')
        yt_desc = yt_desc.replace('#Shorts ', '')
    kind = '카드뉴스(피드 캐러셀)' if imgs else ('짧은 릴스' if name.endswith('-card') else '릴스')
    data = dict(name=name, kind=kind, instagram=cap, tiktok=tiktok, youtube_title=yt_title, youtube_description=yt_desc, files=[os.path.relpath(f, ROOT) for f in files])
    json.dump(data, open(os.path.join(out, 'captions.json'), 'w'), ensure_ascii=False, indent=1)
    md = [f"# {name} 업로드 패키지 ({kind})", '',
          '## 인스타그램 ' + ('— 피드 캐러셀(이미지 순서대로)' if imgs else '— 릴스(피드에도 노출)'), '(자동 게시됨 · 수동으로 올릴 때만 사용)', '', cap, '',
          '## TikTok' + (' — 사진 모드(이미지 여러 장)' if imgs else ''), '', tiktok, '', '## YouTube ' + ('커뮤니티 탭(이미지 게시물 — 쇼츠는 영상만 가능)' if imgs else 'Shorts'), '', '**제목**', '', yt_title, '', '**설명**', '', yt_desc, '',
          '## 파일', ''] + [f'- {os.path.basename(f)}' for f in files]
    open(os.path.join(out, 'captions.md'), 'w').write('\n'.join(md))
    return out, data

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('queue', nargs='+'); ap.add_argument('--title')
    a = ap.parse_args()
    for qp in a.queue:
        o, d = build(qp, a.title); print(o); print(d['youtube_title'])
