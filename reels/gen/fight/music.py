import numpy as np, wave, sys, os
SEED=int(os.environ.get('SEED',3)); BPM=float(os.environ.get('BPM',100)); R=float(os.environ.get('ROOT',55))
_r=np.random.default_rng(SEED*7+1); PAT=_r.random(16)<.72; GH=int(_r.integers(0,4))
SR=44100; T=19.6; n=int(SR*T); t=np.arange(n)/SR; out=np.zeros(n)
HOOK,SEG=3.0,2.6; hits=[HOOK+i*SEG for i in range(5)]; END=HOOK+5*SEG
def env(a,d,length):
    k=np.arange(int(length*SR))/SR; e=np.minimum(k/a if a>0 else 1,1)*np.exp(-k/d); return e
def add(sig,at):
    i=int(at*SR); j=min(n,i+len(sig)); 
    if i<n: out[i:j]+=sig[:j-i]
# drone A1 + E2 with slow swell
for f,amp in [(R,.22),(R*1.4983,.12),(R*2,.07),(R*2.9966,.03),(R*2.3784,.025*(SEED%2))]:
    out+=amp*np.sin(2*np.pi*f*t+0.3*np.sin(2*np.pi*.13*t))*(0.6+0.4*np.sin(2*np.pi*.07*t+1))
out*=np.minimum(t/1.5,1)
# heartbeat kick 100bpm
bt=60/BPM
def kick(v=1):
    k=np.arange(int(.45*SR))/SR; f=45+80*np.exp(-k*28); ph=2*np.pi*np.cumsum(f)/SR; return v*np.sin(ph)*np.exp(-k*7)
for b in np.arange(0,END,bt):
    add(kick(.55 if b<HOOK else .8),b)
    if b>=HOOK: add(kick(.35),b+bt*.5) if int(b/bt)%4==GH else None
# hats
rng=np.random.default_rng(SEED)
def hat(v):
    k=int(.06*SR); nz=rng.standard_normal(k); nz=np.diff(nz,prepend=0); return v*nz*np.exp(-np.arange(k)/SR*70)
for j,b in enumerate(np.arange(HOOK,END,bt/2)):
    if PAT[j%16]: add(hat(.08 if j%2 else .05),b)
# impact hits on reveals
def impact(v=1,low=1):
    k=np.arange(int(2.2*SR))/SR; f=38+60*np.exp(-k*10); body=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-k*2.2)
    nz=rng.standard_normal(len(k))*np.exp(-k*14)*.5
    metal=sum(np.sin(2*np.pi*fr*k)*np.exp(-k*dk) for fr,dk in [(R*9.5,5),(R*14.25,6),(R*19,8)])*.12
    return v*(low*body+nz+metal)
for i,h in enumerate(hits): add(impact(1.0 if i<4 else 1.35,1.2 if i==4 else 1),h)
for i in range(3): add(impact(.9),.05+i*.32) if i==0 else add(impact(.45),.05+i*.32)
# riser before #1
a,b=hits[4]-2.0,hits[4]; i0,i1=int(a*SR),int(b*SR); k=np.arange(i1-i0)/SR; dur=b-a
nz=rng.standard_normal(len(k)); 
for _ in range(3): nz=(nz+np.roll(nz,1))/2
sw=np.sin(2*np.pi*np.cumsum(200+900*(k/dur)**2)/SR)
out[i0:i1]+=((k/dur)**2)*(.25*nz+.12*sw)
# end double hit + tail
add(impact(1.2,1.3),END); add(impact(.8),END+.2)
# simple reverb
ir=np.random.default_rng(SEED+101).standard_normal(int(1.4*SR))*np.exp(-np.arange(int(1.4*SR))/SR*4)*.025
wet=np.fft.irfft(np.fft.rfft(out,len(out)+len(ir))*np.fft.rfft(ir,len(out)+len(ir)))[:n]
mix=out+.6*wet
mix*=np.minimum(1,(T-t)/1.0)
mix=np.tanh(mix*1.2); mix/=np.max(np.abs(mix))*1.08
st=np.stack([mix,np.roll(mix,180)],1)
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st*32767).astype(np.int16).tobytes()); w.close()
