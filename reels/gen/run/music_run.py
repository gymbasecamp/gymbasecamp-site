import numpy as np, wave, sys
SR=44100; T=19.6; n=int(SR*T); t=np.arange(n)/SR; out=np.zeros(n)
BPM=140; b=60/BPM; HOOK,SEG=3.0,2.6; hits=[HOOK+i*SEG for i in range(5)]; END=HOOK+5*SEG
rng=np.random.default_rng(7)
def add(sig,at,g=1):
    i=int(at*SR); j=min(n,i+len(sig))
    if 0<=i<n: out[i:j]+=g*sig[:j-i]
def env(L,a,d): k=np.arange(int(L*SR))/SR; return np.minimum(k/a,1)*np.exp(-k/d)
def kick():
    k=np.arange(int(.3*SR))/SR; f=50+110*np.exp(-k*35); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-k*9)
def hat(d=.04):
    k=int(d*SR); x=np.diff(rng.standard_normal(k+1)); return x*np.exp(-np.arange(k)/SR/(d/4))
def clap():
    k=int(.18*SR); x=rng.standard_normal(k); x=x-np.convolve(x,np.ones(8)/8,'same'); return x*np.exp(-np.arange(k)/SR*22)*.6
def note(f,L,wave='saw',cut=1.0):
    k=np.arange(int(L*SR))/SR; ph=f*k
    s=2*(ph%1)-1 if wave=='saw' else np.sign(np.sin(2*np.pi*ph))*.6 if wave=='sq' else np.sin(2*np.pi*ph)
    a=int(len(s)*0+1); w=max(1,int(SR/(f*6*cut))); s=np.convolve(s,np.ones(w)/w,'same')
    return s*env(L,.005,L/3)
# key A minor: bass roots per bar  Am F C G
roots=[55,43.65,65.41,49]
lv=lambda tt: 0 if tt<HOOK else min(4,int((tt-HOOK)/SEG))
# pad intro
for f in [220,261.6,329.6]: out+= .05*np.sin(2*np.pi*f*t)*np.minimum(t/2,1)*np.exp(-np.maximum(t-HOOK,0)*.4)
beats=np.arange(0,END,b)
for i,bt in enumerate(beats):
    L=lv(bt); bar=int(bt/(4*b))%4; r=roots[bar]
    add(kick(),bt,.9 if bt>=HOOK-2*b else .5)
    add(hat(),bt+b/2,.10+.03*L)
    if bt>=HOOK: add(hat(.02),bt+b/4,.04*L); add(hat(.02),bt+3*b/4,.04*L)
    if bt>=HOOK and L>=1:  # driving 8th bass
        for h in (0,.5): add(note(r*2,b*.45,'saw',.5),bt+h*b,.22)
    if bt>=HOOK and L>=3 and i%2==1: add(clap(),bt,.5)
# arp from rank 3 (L>=2): 16th notes
arp=[1,1.5,2,2.4]
for i,bt in enumerate(np.arange(HOOK+2*SEG,END,b/4)):
    bar=int(bt/(4*b))%4; f=roots[bar]*8*arp[i%4]
    add(note(f,b/4*.9,'sq',1.5),bt,.05+.02*lv(bt))
# lead from #1
mel=[659,587,523,587,659,784,659,523]
for i,bt in enumerate(np.arange(hits[4],END,b)):
    add(note(mel[i%len(mel)],b*.9,'saw',2),bt,.10)
# riser into #1 and impacts
a0,a1=hits[4]-2.2,hits[4]; i0,i1=int(a0*SR),int(a1*SR); k=np.arange(i1-i0)/SR; d=a1-a0
nz=rng.standard_normal(len(k)); nz=nz-np.convolve(nz,np.ones(30)/30,'same')
out[i0:i1]+=((k/d)**2.5)*(.35*nz+.15*np.sin(2*np.pi*np.cumsum(300+1500*(k/d)**2)/SR))
def boom(v):
    k=np.arange(int(1.6*SR))/SR; f=40+70*np.exp(-k*12); return v*(np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-k*3)+rng.standard_normal(len(k))*np.exp(-k*18)*.4)
for i,h in enumerate(hits): add(boom(.55+.15*i),h)
add(boom(1.0),END)
# reverb
ir=np.random.default_rng(1).standard_normal(int(1.0*SR))*np.exp(-np.arange(int(1.0*SR))/SR*6)*.02
m=len(out)+len(ir); wet=np.fft.irfft(np.fft.rfft(out,m)*np.fft.rfft(ir,m))[:n]
mix=out+.5*wet; mix*=np.minimum(1,(T-t)/1.2)*np.minimum(1,t/.05)
mix=np.tanh(mix*1.3); mix/=np.max(np.abs(mix))*1.06
st=np.stack([mix,np.roll(mix,220)],1)
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st*32767).astype(np.int16).tobytes()); w.close()
