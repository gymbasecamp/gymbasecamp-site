# -*- coding: utf-8 -*-
"""GYM BASECAMP 음악 엔진 v2 (2026-11-17~)

지훈 지시: 영상마다 노래가 똑같다 → 매번 달라야 한다. 숏폼 리듬 연구를 바탕으로
리드 멜로디 + 베이스(부음) + 종목별 고유 파츠(키트)를 만들고, 같은 종목이 다시 나올 때
같은 '종목 테마'를 쓰되 편곡·키·템포·멜로디 변주는 매번 다르게.

사용:
  python3 engine.py <종목키> <out.wav> --dur 25.2 --cues 5.4,9.0,12.6,16.2,19.8 --seed 123 [--log music_log.json --note EP.21]
  종목키: gym run hyrox fight pl yoga crossfit compression allsport short
  cues: 영상의 '공개/임팩트' 시각(초). 엔진이 그 순간에 맞춰 드롭·임팩트·라이저를 배치한다.

설계 원칙(근거는 MUSIC.md):
  1) 0~0.5초 '오디오 스파이크'(임팩트 + 훅 모티프 첫 음) — 첫 1~3초에 이탈이 가장 많다.
  2) 첫 공개 전까지는 훅(종목 테마 모티프)만 짧게, 첫 공개에서 풀 드롭.
  3) 공개마다 라이저→임팩트, 마지막(1위)은 한 옥타브 위 리드 + 풀 편성 클라이맥스.
  4) 종목 테마(모티프 4~6음의 음정 모양)는 고정 = 종목 '시그니처'. 키·템포·리듬 변형·화성·음색은 시드로 매번 다름.
"""
import numpy as np, wave, sys, json, argparse, os, datetime
from scipy.signal import lfilter

SR = 44100

# ---------------- 종목별 키트 ----------------
# bpm: 범위(시드로 선택), half: 하프타임 느낌, scale: 음계, motif: 종목 테마(음계 도수, 박자 길이 1=8분)
# drums: 16스텝 패턴 후보들, bass: 베이스 스타일, lead: 리드 음색, extra: 종목 고유 파츠
KITS = {
 'gym': dict(name='헬스·보디빌딩 — 짐 퐁크', bpm=(128, 142), half=True, scale='phrygian',
   motif=[(0,1),(1,1),(0,1),(4,2),(3,1),(0,2)], lead='cowbell', bass='808', pad='dark',
   kick=['x.....x...x.....','x.....x.......x.','x..x..x...x.....'], snare=['....x.......x...'], hat=['x.x.x.x.x.x.x.x.','xxx.x.xxx.x.x.xx'],
   extra='vox_chop'),
 'run': dict(name='러닝 — 리퀴드 드럼앤베이스', bpm=(168, 176), half=False, scale='minor',
   motif=[(4,1),(2,1),(0,1),(2,1),(4,2),(6,2)], lead='pluck', bass='reese', pad='bright',
   kick=['x.........x.....','x.........x..x..'], snare=['....x.......x...','....x.......x..x'], hat=['..x...x...x...x.','x.xxx.x.x.xxx.x.'],
   extra='footstep'),
 'hyrox': dict(name='HYROX — 인더스트리얼 테크노', bpm=(126, 132), half=False, scale='minor',
   motif=[(0,2),(0,1),(3,1),(2,2),(0,2)], lead='acid', bass='rolling', pad='dark',
   kick=['x...x...x...x...'], snare=['....x.......x...'], hat=['..x...x...x...x.','..x.x.x...x.x.xx'],
   extra='metal'),
 'fight': dict(name='격투기 — 타이코 힙합', bpm=(88, 98), half=False, scale='hijaz',
   motif=[(0,1),(1,1),(4,2),(3,1),(1,1),(0,2)], lead='brass', bass='sub', pad='dark',
   kick=['x.....x...x.....','x..x......x..x..'], snare=['....x.......x...'], hat=['x.x.x.x.x.x.x.x.'],
   extra='taiko'),
 'pl': dict(name='파워리프팅 — 헤비 시네마틱', bpm=(78, 88), half=False, scale='minor',
   motif=[(0,2),(0,1),(1,1),(2,2),(4,2)], lead='saw_dist', bass='sub', pad='dark',
   kick=['x.......x.......','x.....x.x.......'], snare=['....x.......x...'], hat=['x...x...x...x...'],
   extra='chain'),
 'yoga': dict(name='요가·필라테스 — 로파이 앰비언트', bpm=(72, 84), half=False, scale='dorian',
   motif=[(4,2),(2,1),(1,1),(0,2),(2,2)], lead='bell', bass='soft', pad='warm',
   kick=['x.........x.....','x......x..x.....'], snare=['....x.......x...'], hat=['..x...x...x...x.'],
   extra='breath'),
 'crossfit': dict(name='크로스핏 — 브레이크비트 록', bpm=(138, 148), half=False, scale='minor',
   motif=[(0,1),(0,1),(3,1),(0,1),(5,2),(4,2)], lead='power', bass='rolling', pad='dark',
   kick=['x.....x..x......','x.x...x...x.....'], snare=['....x..x....x...','....x.......x.x.'], hat=['x.x.x.x.x.x.x.x.'],
   extra='clang'),
 'compression': dict(name='컴프레션·기능성 — 퓨처 베이스', bpm=(120, 128), half=True, scale='major',
   motif=[(4,1),(5,1),(4,1),(2,1),(0,2),(2,2)], lead='supersaw', bass='808', pad='bright',
   kick=['x.......x.......','x.....x...x.....'], snare=['....x.......x...'], hat=['..x...x...x...x.'],
   extra='zip'),
 'allsport': dict(name='종합 스포츠 — 팝 하우스', bpm=(122, 126), half=False, scale='major',
   motif=[(0,1),(2,1),(4,1),(5,1),(4,2),(2,2)], lead='piano', bass='offbeat', pad='bright',
   kick=['x...x...x...x...'], snare=['....x.......x...'], hat=['..x...x...x...x.','x.xxx.xxx.xxx.xx'],
   extra='crowd'),
}
KITS['short'] = dict(KITS['allsport'], name='오늘의 브랜드 — 숏 하우스', bpm=(118, 128))

SCALES = {'minor':[0,2,3,5,7,8,10],'phrygian':[0,1,3,5,7,8,10],'dorian':[0,2,3,5,7,9,10],
          'major':[0,2,4,5,7,9,11],'hijaz':[0,1,4,5,7,8,10]}
PROGS = {'minor':[[0,5,2,6],[0,3,4,0],[0,5,3,4],[0,6,5,6]],'phrygian':[[0,1,0,6],[0,5,1,0]],
         'dorian':[[0,3,0,3],[0,6,3,4]],'major':[[0,4,5,3],[0,5,3,4],[3,4,0,5]],'hijaz':[[0,1,0,6],[0,3,1,0]]}

# ---------------- 신스 기본 ----------------
def tt(L): return np.arange(int(L*SR))/SR
def env(n, a=.005, d=.1, s=.6, r=.08, L=None):
    t=np.arange(n)/SR; L=L or n/SR; e=np.where(t<a,t/max(a,1e-4),s+(1-s)*np.exp(-(t-a)/max(d,1e-4)))
    rel=np.clip((L-t)/max(r,1e-4),0,1); return e*rel
def lp(x, fc):
    if np.ndim(fc)==0:
        a=np.exp(-2*np.pi*min(fc,SR/2.2)/SR); return lfilter([1-a],[1,-a],x)
    y=np.empty_like(x); z=np.zeros(1); B=128   # 시간에 따라 바뀌는 컷오프: 128샘플 블록마다 계수 갱신
    for i in range(0,len(x),B):
        a=np.exp(-2*np.pi*min(float(fc[i]),SR/2.2)/SR); y[i:i+B],z=lfilter([1-a],[1,-a],x[i:i+B],zi=z)
    return y
def hp(x, fc): return x-lp(x,fc)
def saw(f,t,ph=0): return 2*((f*t+ph)%1)-1
def sq(f,t): return np.sign(np.sin(2*np.pi*f*t))
def tri(f,t): return 2*np.abs(saw(f,t))-1
def sin(f,t): return np.sin(2*np.pi*f*t)
def mtof(m): return 440*2**((m-69)/12)

class Mix:
    def __init__(s, dur): s.n=int(dur*SR); s.bus={k:np.zeros(s.n) for k in ('drum','bass','lead','pad','fx')}
    def add(s, bus, sig, at, g=1.0):
        i=int(at*SR)
        if i>=s.n or i+len(sig)<=0: return
        if i<0: sig=sig[-i:]; i=0
        j=min(s.n,i+len(sig)); s.bus[bus][i:j]+=g*sig[:j-i]

# ---------------- 드럼 ----------------
def kick(r, hard=1.0):
    t=tt(.45); f=42+(150*hard)*np.exp(-t*38); x=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*6)
    x+=r.standard_normal(len(t))*np.exp(-t*120)*.15; return np.tanh(x*(1.6+hard))
def snare(r, tone=190):
    t=tt(.25); n=hp(r.standard_normal(len(t)),1200)*np.exp(-t*16); b=sin(tone,t)*np.exp(-t*22); return .7*n+.5*b
def clap(r):
    t=tt(.22); n=hp(r.standard_normal(len(t)),900); e=np.exp(-t*20)
    for o in (.0,.011,.022): e+=np.exp(-np.clip(t-o,0,None)*120)*(t>=o)*.6
    return n*e*.5
def hat(r, L=.035, open_=False):
    t=tt(.22 if open_ else L); return hp(r.standard_normal(len(t)),7000)*np.exp(-t*(12 if open_ else 1/(L/6)))*.5
def cowbell(f, L=.28):
    t=tt(L); x=sq(f,t)*.5+sq(f*1.48,t)*.5; return lp(x,3500)*np.exp(-t*9)
def taiko(r, f=70):
    t=tt(.9); fr=f+60*np.exp(-t*25); return (np.sin(2*np.pi*np.cumsum(fr)/SR)*np.exp(-t*4)+lp(r.standard_normal(len(t)),900)*np.exp(-t*30)*.5)
def metal(r, f=520):
    t=tt(.4); x=sum(sq(f*k,t) for k in (1,1.34,1.79,2.41)); return hp(x,1500)*np.exp(-t*11)*.15
def impact(r, L=2.0, f=38):
    t=tt(L); fr=f+90*np.exp(-t*9); b=np.sin(2*np.pi*np.cumsum(fr)/SR)*np.exp(-t*2.2)
    n=lp(r.standard_normal(len(t)),2500)*np.exp(-t*7)*.6; return np.tanh(1.8*(b+n))
def riser(r, L=1.0):
    t=tt(L); n=r.standard_normal(len(t)); y=np.zeros_like(n); seg=int(SR*.02)
    for i in range(0,len(n),seg): y[i:i+seg]=lp(n[i:i+seg],300+9000*(i/len(n))**2)
    return y*(t/L)**2*.8
def whoosh(r, L=.35):
    t=tt(L); return lp(r.standard_normal(len(t)),2500)*np.sin(np.pi*t/L)**2*.5

# ---------------- 음색 ----------------
def voice(kind, f, L, r, vel=1.0):
    n=int(L*SR); t=np.arange(n)/SR
    if kind=='cowbell': return cowbell(f*2,min(L,.35))*vel
    if kind=='pluck':   x=saw(f,t)+.5*saw(f*1.005,t); return lp(x,1500+5000*np.exp(-t*18))*env(n,.002,.12,.0,.05)*.6*vel
    if kind=='acid':
        x=saw(f,t); y=np.zeros(n); seg=int(SR*.004)
        for i in range(0,n,seg): y[i:i+seg]=lp(x[i:i+seg],400+3000*np.exp(-(i/SR)*12))
        return np.tanh(2*y)*env(n,.003,.15,.3,.04)*.5*vel
    if kind=='brass':   x=saw(f,t)+saw(f*1.003,t)+.5*saw(f/2,t); return lp(x,900+1800*np.minimum(t/.06,1))*env(n,.03,.2,.7,.08)*.35*vel
    if kind=='saw_dist':x=np.tanh(3*(saw(f,t)+saw(f*.997,t))); return lp(x,2200)*env(n,.01,.3,.6,.1)*.35*vel
    if kind=='bell':    x=sin(f,t)+.4*sin(f*2.76,t)*np.exp(-t*5)+.2*sin(f*5.4,t)*np.exp(-t*9); return x*np.exp(-t*2.2)*env(n,.003,9,1,.15)*.45*vel
    if kind=='power':   x=np.tanh(4*(saw(f,t)+saw(f*1.5,t)*.8+saw(f*2,t)*.5)); return lp(x,3000)*env(n,.005,.2,.7,.06)*.3*vel
    if kind=='supersaw':x=sum(saw(f*(1+d),t,ph) for d,ph in ((-.012,.1),(-.005,.4),(0,0),(.005,.7),(.012,.3))); return lp(x,4500)*env(n,.01,.2,.7,.1)*.18*vel
    if kind=='piano':   x=sum(sin(f*k,t)*np.exp(-t*(2+k*1.5))/k for k in (1,2,3,4)); return x*env(n,.002,9,1,.1)*.5*vel
    return sin(f,t)*env(n)*vel

def bassvoice(kind, f, L, r, glide_from=None):
    n=int(L*SR); t=np.arange(n)/SR
    if kind=='808':
        fr=f*np.ones(n) if glide_from is None else f+(glide_from-f)*np.exp(-t*30)
        x=np.sin(2*np.pi*np.cumsum(fr)/SR); return np.tanh(2.2*x)*env(n,.003,.6,.6,.06)*.8
    if kind=='reese':  x=saw(f,t)+saw(f*1.008,t)+saw(f*.993,t); return lp(x,500)*env(n,.01,.3,.8,.05)*.4
    if kind=='rolling':x=saw(f,t); return lp(x,350+900*np.exp(-t*25))*env(n,.002,.08,.2,.03)*.7
    if kind=='offbeat':x=sq(f,t)*.5+sin(f,t); return lp(x,700)*env(n,.003,.1,.4,.04)*.6
    if kind=='soft':   return sin(f,t)*env(n,.03,.5,.7,.15)*.6
    return np.tanh(1.5*sin(f,t))*env(n,.005,.4,.7,.08)*.7

def padchord(kind, fs, L):
    n=int(L*SR); t=np.arange(n)/SR; x=np.zeros(n)
    for f in fs:
        if kind=='warm': x+=tri(f,t)+.5*sin(f*2,t)
        elif kind=='bright': x+=saw(f,t)+saw(f*1.004,t)
        else: x+=saw(f,t)+saw(f*.996,t)
    x=lp(x,{'warm':1200,'bright':2600,'dark':800}[kind]); return x*env(n,.25,1,1,.4)*.06

# ---------------- 작곡 ----------------
def build(kitkey, dur, cues, seed, transpose=None, bpm=None):
    K=KITS[kitkey]; r=np.random.default_rng(seed)
    B=float(bpm or r.integers(K['bpm'][0],K['bpm'][1]+1)); st=60/B/4  # 16분 스텝
    root=48+int(transpose if transpose is not None else r.integers(-5,7))  # C3 기준
    sc=SCALES[K['scale']]; prog=PROGS[K['scale']][r.integers(len(PROGS[K['scale']]))]
    deg=lambda d,o=0: root+12*o+sc[d%7]+12*(d//7)
    kp=K['kick'][r.integers(len(K['kick']))]; sp=K['snare'][r.integers(len(K['snare']))]; hp_=K['hat'][r.integers(len(K['hat']))]
    if K['half']: sp='........x.......'
    swing=r.uniform(0,.12) if kitkey in ('gym','fight','yoga') else r.uniform(0,.04)
    cues=sorted(cues); first=cues[0] if cues else min(3.0,dur*.2); last=cues[-1] if cues else dur*.8
    M=Mix(dur)
    # 0) 오디오 스파이크
    M.add('fx',impact(r,1.6,40),0,.9); M.add('fx',whoosh(r,.3),0,.4)
    # 리드 모티프 변주 규칙(시드): 리듬 늘이기/줄이기, 끝음 바꾸기, 옥타브 점프
    motif=list(K['motif']); var=r.integers(4)
    def phrase(bar_i, climax=False):
        m=[list(x) for x in motif]
        if var==1 and bar_i%2: m[-1][0]+=r.choice([-2,2,4])
        if var==2: m=[[d,(l if j%2==0 else max(1,l-1))] for j,(d,l) in enumerate(m)]
        if var==3 and bar_i%2: m=m[:3]+[[m[2][0]+2,1],[m[0][0]+7 if climax else m[0][0],2]]
        if bar_i%4==3: m=[[d+ (1 if j==len(m)-1 else 0),l] for j,(d,l) in enumerate(m)]
        return m
    bar=16*st; nb=int(np.ceil(dur/bar))+1
    # 마디 시작을 첫 큐에 맞춰 정렬(드롭이 박자 위에 오게)
    off=first-np.floor(first/bar)*bar
    for b in range(-1,nb):
        t0=off+b*bar
        if t0>dur: break
        if t0+bar<0: continue
        sec='hook' if t0<first-1e-3 else ('outro' if t0>last+bar*1.5 else 'full')
        climax=t0>=last-bar*.5 and sec!='outro'
        ch=prog[(b%4+4)%4]
        # 드럼
        for i in range(16):
            at=t0+i*st+(swing*st if i%2 else 0)
            if at<0 or at>dur: continue
            if sec=='hook':
                if kp[i]=='x': M.add('drum',kick(r,.7),at,.6)
                if hp_[i]=='x' and K['extra']!='breath': M.add('drum',hat(r),at,.08)
                continue
            if sec=='outro' and i>0: continue
            if kp[i]=='x': M.add('drum',kick(r),at,.9)
            if sp[i]=='x': M.add('drum',clap(r) if kitkey in ('gym','compression','allsport','short') else snare(r),at,.55)
            if hp_[i]=='x': M.add('drum',hat(r),at,(.05 if K['extra']=='breath' else .1) if i%4 else .07)
            if K['extra']=='taiko' and i in (0,6,10) : M.add('drum',taiko(r,60+ch*3),at,.5)
            if K['extra']=='metal' and i in (3,11): M.add('drum',metal(r,500+40*(b%3)),at,.5)
            if K['extra']=='clang' and i==14: M.add('drum',metal(r,700),at,.45)
            if K['extra']=='footstep' and i%4==2: M.add('drum',lp(r.standard_normal(int(.05*SR)),600)*np.exp(-tt(.05)*60),at,.35)
        if K['extra']=='vox_chop' and sec=='full' and b%2==1:
            for i in (10,11,14):
                f=mtof(deg(ch+4,1)); t=tt(.12); M.add('fx',(saw(f,t)*.3+saw(f*1.5,t)*.2)*np.sin(np.pi*t/.12)*lp(np.ones(len(t)),1),t0+i*st,.25)
        if sec=='outro': continue
        # 베이스(부음)
        bf=mtof(deg(ch)-12)
        if K['bass']=='808':
            for i in range(16):
                if kp[i]=='x': L=st*(4 if i in (0,8) else 2); M.add('bass',bassvoice('808',bf,L,r,glide_from=bf*1.5 if (i==6 and r.random()<.5) else None),t0+i*st,.75 if sec=='full' else .4)
        elif K['bass']=='rolling':
            for i in range(16):
                if i%4: M.add('bass',bassvoice('rolling',bf*(2 if i%4==3 else 1),st*.9,r),t0+i*st,.6)
        elif K['bass']=='offbeat':
            for i in (2,6,10,14): M.add('bass',bassvoice('offbeat',bf,st*1.8,r),t0+i*st,.6)
        else:
            M.add('bass',bassvoice(K['bass'],bf,bar*.98,r),t0,.6 if sec=='full' else .3)
        # 패드(화음)
        if sec=='full': M.add('pad',padchord(K['pad'],[mtof(deg(ch+k)) for k in (0,2,4)],bar),t0,1.0)
        # 리드(종목 테마)
        if sec=='hook' and b%2: continue
        cur=t0; o=1 if climax else 0
        for d,l in phrase(b,climax):
            L=l*2*st
            if cur>dur: break
            M.add('lead',voice(K['lead'],mtof(deg(d+ch,o)),L*.95,r,1.0 if sec=='full' else .7),cur,.55)
            if climax: M.add('lead',voice(K['lead'],mtof(deg(d+ch,o-1)),L*.95,r,.6),cur,.3)
            cur+=L
    # 큐마다 라이저 → 임팩트
    for i,c in enumerate(cues):
        g=.6+.4*(i/max(1,len(cues)-1))
        M.add('fx',lp(riser(r,min(1.0,c-0.05)),5000),c-min(1.0,c-0.05),.25*g); M.add('fx',impact(r,1.8,36+i*2),c,.8*g); M.add('fx',whoosh(r,.25),c-.12,.3)
    M.add('fx',impact(r,2.5,34),last,.5)
    # 믹스: 킥 사이드체인, 리버브 느낌, 마스터
    duck=np.ones(M.n)
    for i in range(16*nb*2):
        pass
    kenv=np.abs(lfilter([1],[1,-.9995],np.abs(M.bus['drum'])))
    kenv/=kenv.max()+1e-9; duck=1-.45*kenv
    nb_=lambda v:v/(np.max(np.abs(v))+1e-9)
    GAIN={'gym':(1,.75,.8,.5),'pl':(1,.8,.75,.5),'yoga':(.6,.45,1,.8)}.get(kitkey,(1,.65,.85,.55))  # 드럼·베이스·리드·패드 (피크 정규화 후)
    mix=GAIN[0]*nb_(M.bus['drum'])+(GAIN[1]*nb_(M.bus['bass'])+GAIN[3]*nb_(M.bus['pad']))*duck+GAIN[2]*nb_(M.bus['lead'])*(.85+.15*duck)+.8*nb_(M.bus['fx'])
    ir=r.standard_normal(int(1.4*SR))*np.exp(-tt(1.4)*4)*.018
    m=len(mix)+len(ir); wet=np.fft.irfft(np.fft.rfft(M.bus['lead']+M.bus['pad']+M.bus['fx']*.5,m)*np.fft.rfft(ir,m))[:len(mix)]
    mix=mix+.6*wet
    # 휴대폰 스피커 대응: 200Hz 아래는 잘 안 들리므로 베이스 배음(포화)과 2~6kHz 존재감을 더한다
    mix=mix+.35*hp(np.tanh(4*nb_(M.bus['bass'])),300)*duck+1.2*hp(lp(mix,6500),1800)
    t=np.arange(M.n)/SR; mix*=np.minimum(1,(dur-t)/1.0).clip(0,1)
    mix/=np.max(np.abs(mix))+1e-9; mix=np.tanh(mix*1.6); mix/=np.max(np.abs(mix))*1.05
    L=mix+.15*np.roll(M.bus['lead'],300)/(np.max(np.abs(M.bus['lead']))+1e-9)*.2; R=mix-.15*np.roll(M.bus['lead'],300)/(np.max(np.abs(M.bus['lead']))+1e-9)*.2
    stv=np.stack([L,R],1); stv/=np.max(np.abs(stv))*1.02
    info=dict(kit=kitkey,style=K['name'],bpm=B,root_midi=root,scale=K['scale'],prog=prog,motif_var=int(var),swing=round(float(swing),3),drums=[kp,sp,hp_],seed=seed)
    return stv, info

def write(path, st):
    w=wave.open(path,'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st*32767).astype(np.int16).tobytes()); w.close()

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('kit'); ap.add_argument('out'); ap.add_argument('--dur',type=float,required=True)
    ap.add_argument('--cues',default=''); ap.add_argument('--seed',type=int,default=None); ap.add_argument('--bpm',type=float,default=None)
    ap.add_argument('--transpose',type=int,default=None); ap.add_argument('--log'); ap.add_argument('--note',default=''); ap.add_argument('--date',default='')
    a=ap.parse_args(); seed=a.seed if a.seed is not None else int.from_bytes(os.urandom(2),'big')
    cues=[float(x) for x in a.cues.split(',') if x]
    st,info=build(a.kit,a.dur,cues,seed,a.transpose,a.bpm); write(a.out,st)
    info.update(date=a.date or datetime.date.today().isoformat(),script='music/engine.py',note=a.note,cues=cues)
    print(json.dumps(info,ensure_ascii=False))
    if a.log:
        L=json.load(open(a.log)) if os.path.exists(a.log) else []
        # 같은 종목 직전 곡과 키·BPM·진행·변주가 모두 같으면 실패 처리(재사용 금지)
        for p in L:
            if p.get('kit')==info['kit'] and p.get('bpm')==info['bpm'] and p.get('root_midi')==info['root_midi'] and p.get('prog')==info['prog'] and p.get('motif_var')==info['motif_var']:
                sys.exit('같은 조합의 곡이 이미 있음 — 다른 시드로 다시')
        L.append(info); json.dump(L,open(a.log,'w'),ensure_ascii=False,indent=1)
