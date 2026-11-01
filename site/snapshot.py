"""Daily rank snapshot: compute scores/ranks exactly as the site does and store them per day.
Usage: python3 -I snapshot.py            -> writes today's (KST) snapshot to data/rank_history.json
       python3 -I snapshot.py --report   -> also prints a Korean change report vs the previous day
History keeps the last 120 days: {"YYYY-MM-DD": {"<id>": [total, rank, typeRank, type]}}"""
import json, os, subprocess, sys, datetime
D = os.path.dirname(os.path.abspath(__file__))
P = lambda *a: os.path.join(D, *a)
JS = r"""
const fs=require('fs');const vm=require('vm');
const ctx={};vm.createContext(ctx);vm.runInContext(fs.readFileSync(process.argv[1],'utf8')+';this.RANK_V2=RANK_V2;',ctx);
const B=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
let rc={};try{rc=JSON.parse(fs.readFileSync(process.argv[3],'utf8'))}catch(e){}
const rows=ctx.RANK_V2.rank(B,ctx.RANK_V2.reactFromCounts(rc));
const o={};rows.forEach(r=>{o[r.b.id]=[r.p.total,r.b.rank2,r.b.rankT,r.b.type,r.b.en];});
process.stdout.write(JSON.stringify(o));
"""
def compute():
    out = subprocess.run(['node', '-e', JS, P('rank_v2.js'), P('data/brands.json'), P('data/react.json')],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)
def today():
    return (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)).strftime('%Y-%m-%d')
def load():
    p = P('data/rank_history.json')
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}
def prev_of(H, day):
    ds = sorted(d for d in H if d < day)
    return H[ds[-1]] if ds else {}
def main():
    H = load(); t = today(); cur = compute()
    H[t] = {k: v[:4] for k, v in cur.items()}
    for d in sorted(H)[:-120]: del H[d]
    json.dump(H, open(P('data/rank_history.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'), sort_keys=True)
    if '--report' in sys.argv:
        pv = prev_of(H, t); lines = []
        if not pv:
            print(f'{t} 첫 기록: {len(cur)}개 브랜드'); return
        new = [cur[k][4] for k in cur if k not in pv]
        gone = [k for k in pv if k not in cur]
        mv = sorted(((pv[k][1]-v[1], v[4], pv[k][1], v[1], round(v[0]-pv[k][0],1)) for k, v in cur.items() if k in pv and pv[k][1]!=v[1]), key=lambda x:-abs(x[0]))
        tm = [(v[3], v[4], pv[k][2], v[2]) for k, v in cur.items() if k in pv and pv[k][2]!=v[2] and v[2]<=5]
        print(f'{t} 랭킹 변동 (전체 {len(cur)}개)')
        if new: print('신규: ' + ', '.join(new))
        if gone: print('제외: ' + ', '.join(gone))
        top = sorted(cur.values(), key=lambda v: v[1])[:5]
        print('전체 TOP5: ' + ' / '.join(f'{v[1]}위 {v[4]} {v[0]}' for v in top))
        for d, n, a, b, s in mv[:10]: print(f'{"▲" if d>0 else "▼"}{abs(d)} {n}: {a}위 → {b}위 ({"+" if s>=0 else ""}{s}점)')
        if not mv: print('전체 순위 변동 없음')
        for ty, n, a, b in tm: print(f'[{ty}] {n}: {a}위 → {b}위')
main()
