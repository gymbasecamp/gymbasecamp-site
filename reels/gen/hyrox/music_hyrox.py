# HYROX 레이스 전용 트랙 — 128BPM 드라이빙 테크노, 출발 휘슬 + 결승 통과마다 상승 히트 (다른 릴스와 겹치지 않는 새 곡)
import numpy as np, wave, sys
SR=44100; INTRO,SEG,LAST,END=3.4,3.4,4.6,3.2; T=INTRO+SEG*4+LAST+END; n=int(SR*T); t=np.arange(n)/SR; out=np.zeros(n)
rng=np.random.default_rng(91); BPM=128; b=60/BPM; GO=2.9
def add(sig,at,g=1):
    i=int(at*SR); j=min(n,i+len(sig))
    if 0<=i<n: out[i:j]+=g*sig[:j-i]
def env(L,a=.005,d=8): k=np.arange(int(L*SR))/SR; return k,np.minimum(k/a,1)*np.exp(-k*d)
def kick(): k=np.arange(int(.35*SR))/SR; f=50+170*np.exp(-k*55); return np.tanh(3*np.sin(2*np.pi*np.cumsum(f)/SR))*np.exp(-k*9)
def hat(d=.04,o=False):
    m=int((.12 if o else d)*SR); x=np.diff(rng.standard_normal(m+1)); return x*np.exp(-np.arange(m)/SR*(18 if o else 90))
def rim():
    k,e=env(.08,.001,60); return (np.sin(2*np.pi*1700*k)+.6*rng.standard_normal(len(k)))*e*.5
def bass(f,L):
    k,e=env(L,.003,6); s=2*((f*k)%1)-1; s=np.convolve(s,np.ones(18)/18,'same'); return np.tanh(2.2*s)*e
def pluck(f,L=.22):
    k,e=env(L,.002,14); return (np.sin(2*np.pi*f*k)+.4*np.sin(2*np.pi*2*f*k+.3)+.2*np.sign(np.sin(2*np.pi*f*k)))*e
def whistle(L=.5):
    k=np.arange(int(L*SR))/SR; f=2900+120*np.sin(2*np.pi*34*k); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.minimum(k/.01,1)*np.minimum((L-k)/.05,1)*.35
def boom(p):
    k=np.arange(int(2*SR))/SR; f=40+120*np.exp(-k*14); body=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-k*2.2)
    ch=sum(np.sin(2*np.pi*p*m*k)*np.exp(-k*(2.5+m)) for m in (1,1.5,2))*.18
    return body+ch+rng.standard_normal(len(k))*np.exp(-k*25)*.35
# 인트로: 카운트다운 비프 + 낮은 드론
for i in range(3): k,e=env(.18,.003,10); add(np.sin(2*np.pi*660*k)*e*.35,1.4+i*.5)
add(whistle(.55),GO); out+=.10*np.sin(2*np.pi*55*t)*np.clip((t-.2)/1.5,0,1)*(t<GO)
end=INTRO+SEG*4+LAST
# 그루브 (GO 이후) — 구간마다 레이어 추가
root=[55,55,65.4,49]; scale=[0,3,7,10,12,15]
beats=np.arange(GO,end,b)
for i,bt in enumerate(beats):
    lv=min(4,int(max(0,bt-INTRO)//SEG))
    add(kick(),bt,.9)
    add(hat(),bt+b/2,.16+.03*lv)
    if lv>=1: add(hat(.02),bt+b/4,.06); add(hat(.02),bt+3*b/4,.06)
    if i%4 in (1,3): add(rim(),bt,.45)
    if lv>=2 and i%2==1: add(hat(o=True),bt+b/2,.08)
    r=root[(i//8)%4]
    add(bass(r,b*.45),bt+b/2,.42)
    if lv>=1:
        for q in range(2):
            add(pluck(r*4*2**(scale[(i*3+q*2+lv)%len(scale)]/12),.18),bt+q*b/2,.08+.02*lv)
# 결승 통과 히트 (구간마다 반음씩 상승)
fins=[INTRO+i*SEG+2.3 for i in range(4)]+[INTRO+4*SEG+2.2]
for i,ft in enumerate(fins):
    a0=ft-1.0; i0,i1=int(a0*SR),int(ft*SR); k=np.arange(i1-i0)/SR; nz=rng.standard_normal(len(k)); nz=nz-np.convolve(nz,np.ones(30)/30,'same')
    out[i0:i1]+=((k/1.0)**2.2)*(.10+.04*i)*nz
    add(boom(110*2**(i*2/12)),ft,.8+.1*i)
# 마지막: 메이저 코드 + 엔딩
for f in (220,277.2,329.6,440): k,e=env(3.2,.01,1.1); add((np.sin(2*np.pi*f*k)+.3*np.sin(2*np.pi*2*f*k))*e*.12,fins[4]+.1)
add(boom(82.4),end,1.0)
ir=np.random.default_rng(5).standard_normal(int(1.0*SR))*np.exp(-np.arange(int(1.0*SR))/SR*6)*.02
m=len(out)+len(ir); wet=np.fft.irfft(np.fft.rfft(out,m)*np.fft.rfft(ir,m))[:n]
mix=out+.45*wet; mix*=np.minimum(1,(T-t)/1.0); mix=np.tanh(mix*1.3); mix/=np.max(np.abs(mix))*1.06
st=np.stack([mix,np.roll(mix,180)],1)
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st*32767).astype(np.int16).tobytes()); w.close()
print('T',T)
