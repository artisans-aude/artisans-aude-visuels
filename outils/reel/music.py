import numpy as np, wave
SR=44100; BPM=120; beat=60/BPM; D=42.0
N=int(SR*D); L=np.zeros(N); R=np.zeros(N)
rng=np.random.default_rng(7)
def add(sig,t,pan=0.0,g=1.0):
    i=int(t*SR); j=min(N,i+len(sig))
    if i>=N: return
    s=sig[:j-i]*g; L[i:j]+=s*(1-pan)*0.5*2**0.5; R[i:j]+=s*(1+pan)*0.5*2**0.5
def hp(x,a=0.9):  # simple one-pole high-pass
    y=np.zeros_like(x); p=0; px=0
    for k in range(len(x)): p=a*(p+x[k]-px); px=x[k]; y[k]=p
    return y
def lp(x,a=0.15):
    y=np.zeros_like(x); p=0
    for k in range(len(x)): p+=a*(x[k]-p); y[k]=p
    return y
# samples
t=np.arange(int(.35*SR))/SR
kick=np.sin(2*np.pi*np.cumsum(45+90*np.exp(-t*30))/SR)*np.exp(-t*11)
t=np.arange(int(.25*SR))/SR
clap=lp(hp(rng.standard_normal(len(t)),0.85),0.3)*np.exp(-t*35)*0.35
t=np.arange(int(.06*SR))/SR
hat=hp(rng.standard_normal(len(t)),0.6)*np.exp(-t*70)*0.25
t=np.arange(int(.12*SR))/SR
ohat=hp(rng.standard_normal(int(.18*SR)),0.6)*np.exp(-np.arange(int(.18*SR))/SR*25)*0.18
def note(f,dur,harm=(1,.5,.33,.25),dec=6):
    t=np.arange(int(dur*SR))/SR
    s=sum(a*np.sin(2*np.pi*f*(h+1)*t) for h,a in enumerate(harm))
    env=np.minimum(1,t/0.005)*np.exp(-t*dec)
    return s*env
def m(n): return 440*2**((n-69)/12)
# progression Am F C G (one bar each = 4 beats)
prog=[(57,[69,72,76]),(53,[65,69,72]),(48,[67,72,76]),(55,[67,71,74])]
bars=int(D/(4*beat))
sc=np.ones(N)  # sidechain envelope
for b in range(bars):
    t0=b*4*beat; root,ch=prog[b%4]
    drums = b>=2 and b<bars-1
    for q in range(4):
        tb=t0+q*beat
        if drums or b==bars-1 and q==0:
            add(kick,tb,0,0.6)
            i=int(tb*SR); k=np.arange(min(int(.3*SR),N-i))
            sc[i:i+len(k)]=np.minimum(sc[i:i+len(k)],0.45+0.55*(k/len(k)))
        if drums and q in (1,3): add(clap,tb,0.05,0.5)
        if b>=1 and b<bars-1:
            add(hat,tb+beat/2,0.3,0.45)
            if drums: add(hat,tb+beat/4,-0.3,0.2); add(hat,tb+3*beat/4,-0.3,0.2)
        if drums and q==3 and b%2==1: add(ohat,tb+beat/2,0.2,0.35)
    # bass 8ths (octave bounce)
    if b>=2 and b<bars-1:
        for e in range(8):
            f=m(root-12+(12 if e%2 else 0))
            add(note(f,beat/2*0.9,(1,.3,.08),7),t0+e*beat/2,0,0.45)
    # arpeggio 16ths
    if b<bars-1 or True:
        for s16 in range(16):
            if b==bars-1 and s16>3: break
            nn=ch[[0,1,2,1][s16%4]]+(12 if s16%8>=4 else 0)
            add(note(m(nn),beat/4*1.6,(1,.08),10),t0+s16*beat/4,0.4*(1 if s16%2 else -1),0.09)
    # soft pad
    padd=4*beat; tt=np.arange(int(padd*SR))/SR
    pad=sum(np.sin(2*np.pi*m(n)*tt)+0.3*np.sin(2*np.pi*m(n)*2.003*tt) for n in ch)
    pad*=np.minimum(1,tt/0.3)*np.minimum(1,(padd-tt)/0.3)
    add(pad,t0,0,0.075)
# apply sidechain to everything except we accept full mix pump lightly
mix=np.stack([L,R])
mix*= (0.8+0.2*sc)
mix=np.stack([lp(mix[0],0.22),lp(mix[1],0.22)])
fade=np.ones(N); fi=int(0.5*SR); fo=int(2.5*SR)
fade[:fi]=np.linspace(0,1,fi); fade[-fo:]=np.linspace(1,0,fo)
mix*=fade; mix/=np.abs(mix).max()/0.5
pcm=(mix.T*32767).astype(np.int16)
with wave.open('musique.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('ok')
