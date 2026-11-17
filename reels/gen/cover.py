# -*- coding: utf-8 -*-
"""릴스 표지(썸네일) 통일 템플릿 (2026-11-17 지훈: "썸네일이 중구난방 — 릴스 목적이 보이는 표지로").

모든 메인 릴스 표지를 같은 틀로: 시즌·EP / 종목 이름(크게) / '운동복 브랜드 TOP5' / 주황 훅 배지 / 아래쪽 선수 실루엣.
프로필 그리드(3:4로 잘림)에서도 글자가 보이도록 핵심 글자는 세로 y 300~1500 안에 둔다.

사용: python3 cover.py --bg frame.jpg --crop 1080,1100,1750 --ep 20 --sport "헬스·보디빌딩" --hook "왕좌 교체 · 1위는?" --out ../covers/2026-11-18-bb.jpg
  --kind short 이면 '오늘의 브랜드' 표지(--sport 자리에 브랜드명).
"""
import argparse
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
BG, IV, PT = (10, 10, 12), (244, 239, 232), (255, 106, 61)
SERIF = '/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc'
SANS = '/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'
SANS_B = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
INTER = '/usr/share/fonts/opentype/inter/InterDisplay-Medium.otf'
KR = 1  # ttc 안 한국어 글꼴 번호

def font(path, size, idx=KR):
    try: return ImageFont.truetype(path, size, index=idx)
    except Exception: return ImageFont.truetype(path, size)

def fit(d, text, path, size, maxw, idx=KR):
    while size > 40:
        f = font(path, size, idx)
        if d.textlength(text, font=f) <= maxw: return f
        size -= 4
    return font(path, size, idx)

def make(bg, crop, ep, sport, hook, out, kind='main', line2=None):
    im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im)
    # 위쪽 스포트라이트
    glow = Image.new('L', (W, H), 0); gd = ImageDraw.Draw(glow)
    gd.polygon([(W/2-80, 0), (W/2+80, 0), (W/2+520, 1500), (W/2-520, 1500)], fill=60)
    glow = glow.filter(ImageFilter.GaussianBlur(70))
    im = Image.composite(Image.new('RGB', (W, H), (90, 52, 30)), im, glow)
    # 아래쪽 선수 실루엣(영상 프레임에서 잘라 옴) — 위로 갈수록 어둡게 사라짐
    if bg:
        src = Image.open(bg).convert('RGB').resize((W, H))
        x0, y0, y1 = crop
        part = src.crop((0, y0, W, y1)); ph = part.size[1]
        mask = Image.linear_gradient('L').resize((W, ph))  # 위 0 → 아래 255
        mask = mask.point(lambda v: min(255, int(v * 1.6)))
        top = H - ph - 200
        im.paste(part, (0, top), mask)
    d = ImageDraw.Draw(im)
    # 시즌·EP
    tag = f"SEASON 1 · 정상 쟁탈전   EP.{ep}" if kind == 'main' else "SEASON 1 · 오늘의 브랜드"
    f = font(SANS_B, 34); d.text((W/2, 330), tag, font=f, fill=PT, anchor='mm')
    # 종목 이름(크게)
    f = fit(d, sport, SERIF, 168, W - 120)
    d.text((W/2, 520), sport, font=f, fill=IV, anchor='mm')
    # 두 번째 줄
    l2 = line2 or ('운동복 브랜드 TOP5' if kind == 'main' else '종목별 순위·사는 곳')
    f = fit(d, l2, SERIF, 92, W - 160); d.text((W/2, 690), l2, font=f, fill=IV, anchor='mm')
    # 훅 배지
    f = fit(d, hook, SANS, 64, W - 260)
    tw = d.textlength(hook, font=f); bw, bh = tw + 90, 112; bx, by = (W - bw) / 2, 800
    d.rounded_rectangle((bx, by, bx + bw, by + bh), radius=18, fill=PT)
    d.text((W/2, by + bh/2 + 2), hook, font=f, fill=BG, anchor='mm')
    # 아래 브랜드 표기
    f = font(INTER, 30, 0); d.text((W/2, 1800), 'GYM BASECAMP · gymbasecamp.kr', font=f, fill=(200, 192, 182), anchor='mm')
    im.save(out, quality=92)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--bg'); ap.add_argument('--crop', default='0,1050,1760')
    ap.add_argument('--ep', default=''); ap.add_argument('--sport', required=True); ap.add_argument('--hook', required=True)
    ap.add_argument('--line2'); ap.add_argument('--kind', default='main'); ap.add_argument('--out', required=True)
    a = ap.parse_args()
    make(a.bg, [int(v) for v in a.crop.split(',')], a.ep, a.sport, a.hook, a.out, a.kind, a.line2)
    print(a.out)
