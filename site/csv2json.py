"""Convert the '브랜드 마스터' CSV (columns below) into data/brands.json used by build.py.
Usage: python3 -I csv2json.py data/brands.csv
Only rows with 사이트 공개 == '공개' are published."""
import csv, json, re, sys, os
D = os.path.dirname(os.path.abspath(__file__))
F = ['남성','여성','머슬핏','오버핏','컴프레션','슬리브리스/탱크','쇼츠','팬츠/조거','레깅스','스포츠브라','아우터','펌프커버/헤비웨이트','스트렝스/싱글렛','러닝/HYROX/크로스트레이닝']
LV = {'주력':'M','많음':'H','일부':'L','없음':'X'}
def cov(r):
    # 커버리지 column: '남성=주력;오버핏=많음;레깅스=없음' (공식몰 카테고리별 상품 수 기준). Missing -> {}
    out = {}
    for part in (r.get('커버리지') or '').split(';'):
        if '=' in part:
            k, v = [x.strip() for x in part.split('=', 1)]
            if k in F and v in LV:
                out[k] = LV[v]
    return out
def shops(r):
    # 국내 구매처: '코오롱몰(공식 판매처)|https://...;KREAM(리셀)|https://...'
    out = []
    for part in (r.get('국내 구매처') or '').split(';'):
        if '|' in part:
            n, u = [x.strip() for x in part.split('|', 1)]
            if n and u.startswith('https://'):
                out.append([n, u])
    return out
rows = list(csv.DictReader(open(sys.argv[1], encoding='utf-8')))
out = []
for r in rows:
    if not r.get('브랜드 명') or r.get('사이트 공개', '공개') != '공개':
        continue
    parts = [s.strip() for s in r['브랜드 명'].split(' / ', 1)]
    en, ko = (parts + [parts[0]])[:2]
    slug = re.sub(r'[^a-z0-9]+', '-', en.lower()).strip('-') or 'b'
    out.append(dict(id=slug, en=en, ko=ko, origin=r['국내/해외'], url=r['공식몰'], gender=r['남성/여성'],
        style=r['주요 스타일'], price=r['가격대'], items=r['대표 상품'], ig=r['인스타그램'], desc=r['특징'],
        cat=r.get('대표 카테고리') or '헬스·보디빌딩', score=int(float(r['현재 점수 (20)'] or 0)), rank=int(float(r['현재 순위'] or 99)), type=r['브랜드 유형'],
        sport=r['핵심 운동'], vibe=r['스타일 성향'], group=r['사이트 그룹'], buy=r['구매 방식'], shops=shops(r),
        f=[k for k in F if r.get(k) == 'Y'], cov=cov(r)))
json.dump(out, open(os.path.join(D, 'data/brands.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print(len(out), 'brands written')
