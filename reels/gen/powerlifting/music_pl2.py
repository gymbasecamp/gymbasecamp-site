import numpy as np, wave, sys, os
SEED=int(os.environ.get('SEED',23)); TR=int(os.environ.get('TR',0)); X=2**(TR/12); _r=np.random.default_rng(SEED*5+3)
SR=44100; INTRO,SEG,LAST,END=3.0,3.6,4.6,3.2; T=INTRO+SEG*4+LAST+END; n=int(SR*T); t=np.arange(n)/SR; out=np.zeros(n)
rng=np.random.default_rng(SEED); BPM=float(os.environ.get('BPM',82)); b=60/BPM
def add(sig,at,g=1):
    i=int(at*SR); j=min(n,i+len(sig))
    if 0<=i<n: out[i:j]+=g*sig[:j-i]
def kick(): k=np.arange(int(.5*SR))/SR; f=44+140*np.exp(-k*45); return np.tanh(2.6*np.sin(2*np.pi*np.cumsum(f)/SR))*np.exp(-k*5)
def clap():
    k=int(.25*SR); x=rng.standard_normal(k); x=x-np.convolve(x,np.ones(5)/5,'same'); e=np.exp(-np.arange(k)/SR*18); return x*e*.6
def hat(d=.025): m=int(d*SR); x=np.diff(rng.standard_normal(m+1)); return x*np.exp(-np.arange(m)/SR/(d/5))
def sub(f,L): k=np.arange(int(L*SR))/SR; return np.sin(2*np.pi*f*k)*np.minimum(k/.01,1)*np.exp(-k*1.2)
def stab(fs,L,dark=40):
    k=np.arange(int(L*SR))/SR; s=sum(sum((2*((f*h*k)%1)-1)/h for h in (1,2,3)) for f in fs)/len(fs); s=np.convolve(s,np.ones(dark)/dark,'same'); return s*np.minimum(k/.01,1)*np.exp(-k*3)
def hit(v,pitch):
    k=np.arange(int(1.8*SR))/SR; f=36+80*np.exp(-k*10); body=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-k*2)
    ring=np.sin(2*np.pi*pitch*k)*np.exp(-k*3)*.25+np.sin(2*np.pi*pitch*1.5*k)*np.exp(-k*4)*.12
    return v*(body+rng.standard_normal(len(k))*np.exp(-k*20)*.4+ring)
# tension pad
for f,a in [(41.2*X,.22),(61.7*X,.08),(82.4*X,.05)]: out+=a*np.sin(2*np.pi*f*t)*np.minimum(t/1.5,1)
end=INTRO+SEG*4+LAST
CL=(1,3) if SEED==23 else tuple(sorted(_r.choice(4,2,replace=False)))
for i,bt in enumerate(np.arange(INTRO-4*b,end,b)):
    if bt<0: continue
    add(kick(),bt,.85 if i%2==0 else .5)
    if i%4 in CL: add(clap(),bt,.5)
    add(hat(),bt+b/2,.12); add(hat(.012),bt+b*.75,.06)
roots=[r*X for r in ([41.2,41.2,49,36.7] if SEED==23 else [41.2,[36.7,49,55][_r.integers(3)],41.2,[30.9,36.7,46.2][_r.integers(3)]])]
for i,bt in enumerate(np.arange(INTRO,end,2*b)): add(sub(roots[i%4]*2,2*b),bt,.35)
succ=[INTRO+i*SEG+2.4 for i in range(4)]+[INTRO+4*SEG+2.4]
notes=[x*X for x in [220,246.9,277.2,329.6,440]]
for i,sct in enumerate(succ):
    a0=sct-.9; i0,i1=int(a0*SR),int(sct*SR); k=np.arange(i1-i0)/SR; nz=rng.standard_normal(len(k)); nz=nz-np.convolve(nz,np.ones(25)/25,'same')
    out[i0:i1]+=((k/.9)**2)*(.12+.05*i)*nz
    add(hit(.9+.12*i,notes[i]),sct); add(stab([notes[i]/2,notes[i]*.75,notes[i]],1.2),sct,.25+.04*i)
add(stab([110*X,138.6*X,164.8*X,220*X],3.0,25),succ[4]+.15,.35)
add(hit(1.0,110*X),end)
ir=np.random.default_rng(SEED+77).standard_normal(int(1.2*SR))*np.exp(-np.arange(int(1.2*SR))/SR*5)*.02
m=len(out)+len(ir); wet=np.fft.irfft(np.fft.rfft(out,m)*np.fft.rfft(ir,m))[:n]
mix=out+.5*wet; mix*=np.minimum(1,(T-t)/1.2); mix=np.tanh(mix*1.25); mix/=np.max(np.abs(mix))*1.06
st=np.stack([mix,np.roll(mix,240)],1)
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st*32767).astype(np.int16).tobytes()); w.close()
