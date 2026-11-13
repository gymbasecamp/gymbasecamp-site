# '오늘의 브랜드' 짧은 릴스 전용 곡 — 140BPM 트랩 스타일, F# 마이너. 매 편 시드·키를 바꿔 재사용 금지(music_log.json 기록)
import numpy as np, wave, sys
SEED=int(sys.argv[2]) if len(sys.argv)>2 else 140; ROOT=float(sys.argv[3]) if len(sys.argv)>3 else 46.25
SR=44100; T=9.6; n=int(SR*T); t=np.arange(n)/SR; out=np.zeros(n); rng=np.random.default_rng(SEED); b=60/140
def add(sig,at,g=1):
    i=int(at*SR); j=min(n,i+len(sig))
    if 0<=i<n: out[i:j]+=g*sig[:j-i]
def env(L,a=.004,d=8): k=np.arange(int(L*SR))/SR; return k,np.minimum(k/a,1)*np.exp(-k*d)
def k808(f,L):
    k=np.arange(int(L*SR))/SR; fr=f*(1+2.5*np.exp(-k*30)); return np.tanh(2.5*np.sin(2*np.pi*np.cumsum(fr)/SR))*np.exp(-k*1.6)
def snare():
    k,e=env(.22,.001,22); return (rng.standard_normal(len(k))*.8+np.sin(2*np.pi*190*k)*.6)*e
def hat(): m=int(.03*SR); x=np.diff(rng.standard_normal(m+1)); return x*np.exp(-np.arange(m)/SR*120)
def bell(f):
    k,e=env(.5,.002,5); return (np.sin(2*np.pi*f*k)+.5*np.sin(2*np.pi*f*2.76*k)*np.exp(-k*8))*e
def hit():
    k=np.arange(int(1.2*SR))/SR; f=45+150*np.exp(-k*16); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-k*3)+rng.standard_normal(len(k))*np.exp(-k*30)*.4
add(hit(),0,1.0)
for i,bt in enumerate(np.arange(0,7.3,b)):
    if i%8 in (0,3): add(k808(ROOT*(1 if (i//8)%2==0 else 1.19),b*2.6),bt,.7)
    if i%4==2: add(snare(),bt,.45)
    for q in range(2 if i%8<6 else 4): add(hat(),bt+q*b/(2 if i%8<6 else 4),.13)
mel=[0,3,7,10,7,3,12,10]
for i,bt in enumerate(np.arange(0,7.3,b)):
    if i%2==0: add(bell(ROOT*8*2**(mel[(i//2)%8]/12)),bt,.10)
for at in (1.4,1.75,2.2,4.1,7.3): add(hit(),at,.55)
for f in (ROOT*4,ROOT*4*1.19,ROOT*4*1.5,ROOT*8): k,e=env(2.3,.01,1.4); add(np.sin(2*np.pi*f*k)*e*.12,7.3)
mix=out*np.minimum(1,(T-t)/.6); mix=np.tanh(mix*1.3); mix/=np.max(np.abs(mix))*1.06
st=np.stack([mix,np.roll(mix,150)],1)
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st*32767).astype(np.int16).tobytes()); w.close()
